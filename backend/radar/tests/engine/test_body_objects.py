import pytest
import redis
import uuid
from unittest.mock import Mock
from backend import settings
from radar.engine.body_objects import BodyObjectsPool


@pytest.fixture(scope='session')
def r():
    return redis.Redis(host=settings.REDIS_HOSTNAME)


@pytest.fixture
@pytest.mark.django_db
def pool() -> BodyObjectsPool:
    return BodyObjectsPool()


@pytest.fixture
def new_body():
    return 'o--o\n' \
           '-oo-\n' \
           'o--o'


@pytest.mark.django_db
def test_add_body(pool, new_body, r):
    body_id = str(uuid.uuid4())
    body_key = pool.make_body_key(body_id)

    pool.add_body(new_body, body_id)
    assert r.exists(body_key), "Can't find added bodies"
    assert r.get(body_key).decode() == new_body, \
        "The bodies added to Redis aren't the same as original bodies"


@pytest.mark.django_db
def test_ping_body(pool, r):
    body_id = str(uuid.uuid4())
    body_key = pool.make_body_key(body_id)

    r.set(body_key, '~', pool.body_expiration - 1)
    pool.ping_body(body_id)
    assert r.ttl(body_key) == pool.body_expiration


@pytest.mark.django_db
def test_update_bodies(pool, r):
    dropped_keys = ['a', 'b']
    new_records = {'c': '1', 'd': '2'}
    pool._scripts.update_records = Mock(
        return_value='{"dropped_keys":' + str(dropped_keys).replace("'", '"') +
                     ',"new_records":' + str(new_records).replace("'",
                                                                  '"') + '}'
    )
    update = pool.update_bodies(['dummy', 'data'], 10)
    assert update['dropped_keys'] == dropped_keys and \
           update['new_records'] == new_records, \
           'Incorrect json handling'
