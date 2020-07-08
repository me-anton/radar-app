import logging
from collections import namedtuple
from typing import Iterable, Tuple, Iterator
from share.metaclasses import Singleton
from radar.models import AlienBody


logger = logging.getLogger(__name__)
BodyObject = namedtuple('BodyObject', 'id, matrix, width, height')
Position = namedtuple('Position', ('x', 'y'))


class BodyObjectsPool(metaclass=Singleton):
    """
    An object for getting BodyObject instances from database or cache
    """
    def __init__(self, num_of_default_bodies=3):
        self.num_of_default_bodies = num_of_default_bodies
        self.__default_bodies: Tuple[BodyObject, ...] = \
            self._generate_defaults(num_of_default_bodies)

    def __getitem__(self, __id):
        raise NotImplemented    # TODO try to return custom body from cache

    @property
    def first(self):
        return self._get_default(0)

    @property
    def second(self):
        return self._get_default(1)

    @property
    def third(self):
        return self._get_default(2)

    def _get_default(self, index):
        return self.__default_bodies[index]

    def _generate_defaults(self, num_of_defaults):
        logger.info('Generating default bodies')
        query = AlienBody.objects.filter(id__lte=num_of_defaults)
        return tuple(self._create_body_objects(query))

    @staticmethod
    def _create_body_objects(bodies: Iterable[AlienBody])\
            -> Iterator[BodyObject]:
        body_line_lists = (_BodyLineList(id=body.id,
                                         line_list=body.body_str.splitlines())
                           for body in bodies)

        body_matrices = [_BodyMatrix(id=body.id,
                                     matrix=[list(line) for line in body.line_list])
                         for body in body_line_lists]

        body_objects = (BodyObject(id=body.id,
                                   matrix=body.matrix,
                                   width=len(body.matrix[0]),
                                   height=len(body.matrix))
                        for body in body_matrices)

        return body_objects


_BodyLineList = namedtuple('_BodyLineLists', 'id, line_list')
_BodyMatrix = namedtuple('_BodyMatrix', 'id, matrix')
