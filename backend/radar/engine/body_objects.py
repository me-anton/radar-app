import logging
import json
from dataclasses import dataclass
from redis import Redis
from typing import Iterable, Tuple, List, Iterator, Union, Dict
from typing_extensions import TypedDict

from backend import settings
from caching.scripts import RedisScriptsPool
from share.metaclasses import Singleton
from radar.models import AlienBody
from radar.validation import validate_body_str_profile


logger = logging.getLogger(__name__)
BodiesUpdate = TypedDict('BodiesUpdate', {'dropped_keys': List[str],
                                          'new_records': Dict[str, str]})


@dataclass(frozen=True)
class BodyObject:
    key: str
    matrix: List[List[str]]
    width: int
    height: int

    @staticmethod
    def generate(key: str, body: str) -> 'BodyObject':
        line_list = body.splitlines()
        matrix = [list(line) for line in line_list]

        return BodyObject(key=key, matrix=matrix,
                          width=len(matrix[0]), height=len(matrix))


class BodyObjectsPool(metaclass=Singleton):
    """
    An object for getting BodyObject instances from database or cache
    """
    body_key_prefix = 'body:'
    body_lookup_pattern = body_key_prefix + '*'
    body_expiration = 10    # in seconds

    def __init__(self, num_of_default_bodies=3):
        self.num_of_default_bodies = num_of_default_bodies
        self.__default_bodies: Tuple[BodyObject, ...] = \
            self._generate_defaults(num_of_default_bodies)
        self._redis = Redis(host=settings.REDIS_HOSTNAME)
        self._scripts = RedisScriptsPool()

    def add_body(self, body: Union[str, bytes], body_id: str) -> None:
        """Cache the requested body string in Redis db"""
        validate_body_str_profile(body)
        key = self.make_body_key(body_id)
        self._redis.set(key, body, self.body_expiration)

    def ping_body(self, body_id: str):
        """Reset expiration time of a body"""
        key = self.make_body_key(body_id)
        self._redis.expire(key, self.body_expiration)

    def update_bodies(self, known_bodies_keys: Iterable[str],
                      max_capacity: int) -> BodiesUpdate:
        """
        Give update on state of body objects' records in Redis db
        :param known_bodies_keys: redis keys of already known bodies
        :param max_capacity: maximum relevant for requester number of bodies
        including already known ones
        """
        return json.loads(
            self._scripts.update_records(keys=known_bodies_keys,
                                         args=[max_capacity,
                                               self.body_lookup_pattern])
        )

    def make_body_key(self, body_id: str):
        return self.body_key_prefix + body_id

    @property
    def first(self):
        return self._get_default(0)

    @property
    def second(self):
        return self._get_default(1)

    @property
    def third(self):
        return self._get_default(2)

    def _get_default(self, index) -> BodyObject:
        return self.__default_bodies[index]

    @staticmethod
    def _generate_defaults(num_of_defaults):
        logger.info('Generating default bodies')
        query = AlienBody.objects.filter(id__lte=num_of_defaults)
        return tuple(BodyObject.generate(str(body.id), body.body_str)
                     for body in query)
