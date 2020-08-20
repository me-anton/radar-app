import pytest
import redis
import json
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
    assert script() == b'It works!', \
        f"Can't read files from {scripts_pool.redis_scripts_folder_address}" \
        " correctly"

    os.remove(script_address)


def test_get_by_pattern(scripts_pool, r):
    keys = ['test:a', 'test:b', 'test:c']
    values = {b'1', b'2', b'3'}
    records = dict(zip(keys, values))
    r.mset(records)

    assert set(scripts_pool.get_by_pattern(args=[10, 'test:*'])) == values, \
        "Script get_by_pattern.lua doesn't work as intended"

    r.delete(*keys)


def test_update_records(scripts_pool, r):
    keys_pattern = 'test:*'
    known_expired_keys = {'test:a', 'test:b'}
    known_live_records = {'test:c': '1', 'test:d': '2'}
    unknown_live_records = {'test:e': '3', 'test:f': '4', 'test:g': '5'}
    live_records = known_live_records.copy()
    live_records.update(unknown_live_records)
    known_keys = known_expired_keys | set(known_live_records.keys())

    r.mset(live_records)

    max_relevant_keys_1 = len(known_keys)
    result1 = json.loads(scripts_pool.update_records(keys=known_keys,
                                                     args=[max_relevant_keys_1,
                                                           keys_pattern]))
    assert set(result1['dropped_keys']) == known_expired_keys, \
        'Invalid handling of expired keys'
    assert len(result1['new_records']) == len(known_expired_keys), \
        'Wrong number of new records retrieved ' \
        '(should just compensate for expired keys in this case)'
    assert result1['new_records'].items() <= unknown_live_records.items(), \
        'new_records is not a subset of unknown_live_records'

    max_relevant_keys_2 = len(live_records) + 1
    result2 = json.loads(scripts_pool.update_records(keys=known_keys,
                                                     args=[max_relevant_keys_2,
                                                           keys_pattern]))
    assert result2['new_records'] == unknown_live_records, \
        'Wrong new records retrieved ' \
        '(should just retrieve all unknown_live_records in this case)'

    r.delete(*live_records.keys())

