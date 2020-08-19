import pytest
import redis
import os
from backend import settings

from caching.scripts import RedisScriptsPool


@pytest.fixture
def scripts_pool():
    return RedisScriptsPool()


@pytest.fixture
def r():
    return redis.Redis(host=settings.REDIS_HOSTNAME)


def test_redis_scripts_folder_address_exists():
    assert os.path.exists(RedisScriptsPool.redis_scripts_folder_address)


def test_register_from_volume(scripts_pool, r):
    script_name = 'test.lua'
    script_address = scripts_pool.redis_scripts_folder_address + script_name

    with open(script_address, 'w+') as script_file:
        script_file.write('return "It works!"')

    script = scripts_pool.register_from_volume(script_name)
    assert script().decode() == 'It works!'

    os.remove(script_address)
