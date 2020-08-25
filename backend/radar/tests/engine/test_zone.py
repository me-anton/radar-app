import pytest
import random
from unittest import mock
from collections import namedtuple
from radar.engine.body_objects import BodyObjectsPool, BodyObject
from radar.engine.zone import (
    Zone, ZoneBuilder, ObjectRequest, TooManyMovingObjectsError
)
from radar.engine.moving_objects import MovingObject
from radar.tests.engine.share import assert_pos_moved


pytestmark = pytest.mark.usefixtures('session_db_fix')


@pytest.fixture
def body_pool():
    return BodyObjectsPool()


@pytest.fixture
def zone_builder():
    return ZoneBuilder()


@pytest.fixture
def def_zone(zone_builder):
    return zone_builder.request_custom_zone()


@pytest.fixture
def alien1(body_pool):
    return MovingObject(body_pool.first)


@pytest.fixture
def alien2(body_pool):
    return MovingObject(body_pool.second)


@pytest.fixture
def alien3(body_pool):
    return MovingObject(body_pool.third)


@pytest.fixture
def new_body():
    return 'o--o\n' \
           '-oo-\n' \
           'o--o'


def test_zone_too_small(alien1):
    with pytest.raises(ValueError):
        Zone([alien1], alien1.width, alien1.height)


def test_too_many_moving_objects(alien1):
    with pytest.raises(TooManyMovingObjectsError):
        Zone([alien1] * 2, alien1.width * 2, alien1.height)


def test_zone_too_big(alien1):
    with pytest.raises(ValueError):
        Zone([alien1], 1000, 1000)


@pytest.mark.parametrize('zone_creating_method', [
    ZoneBuilder.create_small_zone,
    ZoneBuilder.create_medium_zone,
    ZoneBuilder.create_large_zone
])
def test_max_out_zone(alien1, alien2, alien3, zone_creating_method):
    aliens = (alien1, alien2, alien3)
    moving_objects = []
    while True:
        moving_objects.append(random.choice(aliens))
        try:
            zone_creating_method(moving_objects)
        except TooManyMovingObjectsError:
            break
        except Exception as err:
            raise AssertionError(err)


# pytest wouldn't allow to create db-dependent objects in "parametrize"
# this namedtuple is a request to create ObjectRequest in the test itself
ObjectRequestRequest = namedtuple('ObjectRequestRequest', 'attr_str, num')


@pytest.mark.parametrize("width, height, requests", [
    (30, 30, [ObjectRequestRequest('first', 1)]),
    (30, 100, [ObjectRequestRequest('second', 3)]),
    (150, 30, [ObjectRequestRequest('first', 1),
               ObjectRequestRequest('second', 1),
               ObjectRequestRequest('third', 2)])
])
def test_create_zone(width, height, requests, body_pool, zone_builder):
    moving_objects_by_index = []
    for request in requests:
        body_obj = getattr(body_pool, request.attr_str)
        moving_objects_by_index.append(ObjectRequest(body_obj, request.num))

    zone = zone_builder.request_custom_zone(width, height,
                                            *moving_objects_by_index)
    assert zone.width == width
    assert zone.height == height
    _check_initialized_moving_objects(moving_objects_by_index,
                                      zone.moving_objects)


def _check_initialized_moving_objects(request, moving_objects):
    moving_objects_by_index = request.copy()
    for obj in moving_objects:
        for i, obj_req in enumerate(moving_objects_by_index):
            if obj_req.body_obj == obj.body:
                _fail_on_excess_objects(request, moving_objects, obj_req, i)
                moving_objects_by_index[i] = ObjectRequest(obj_req.body_obj,
                                                           obj_req.num - 1)
                break


def _fail_on_excess_objects(request, moving_objects, obj_req, i):
    if obj_req.num == 0:
        num_of_requested_objs = len(
            [req_obj for req_obj in moving_objects
             if req_obj.body_obj == obj_req.body_obj])
        requested_num = request[i].num
        pytest.fail(
            'Zone has more objects then the number requested.\n'
            f'Number of requested objects of index {obj_req.body_idx}: '
            f'{requested_num}, actual number in the zone: {num_of_requested_objs}')


def test_draw_zone(def_zone):
    _drawing_test(def_zone, str)


def test_draw_position_vacancy(def_zone):
    _drawing_test(def_zone, lambda zone: zone.draw_position_vacancy())


def _drawing_test(def_zone, draw_func):
    str1 = draw_func(def_zone)

    list_of_lines = str1.splitlines()
    assert len(list_of_lines[0]) == def_zone.width
    assert len(list_of_lines) == def_zone.height

    def_zone.move_objects()
    str2 = draw_func(def_zone)
    assert str1 != str2


def test_move_objects(def_zone):
    objects_before_move = def_zone.moving_objects
    def_zone.move_objects()
    for i, obj in enumerate(def_zone.moving_objects):
        old_pos = objects_before_move[i].position
        new_pos = obj.position
        direction = obj.direction.name
        assert_pos_moved(old_pos, new_pos, direction, fail_on_unmoved=False)


@pytest.mark.parametrize('zone_provider, profile', [
    ['request_small_zone', ZoneBuilder.small_zone_profile],
    ['request_medium_zone', ZoneBuilder.medium_zone_profile],
    ['request_large_zone', ZoneBuilder.large_zone_profile]
])
def test_fits_profile(zone_provider, profile, zone_builder):
    zone = getattr(zone_builder, zone_provider).__call__()
    assert zone.fits_profile(profile)


def test_update_objects(body_pool, new_body):
    known_expired_keys = ['a', 'b']
    known_live_keys = ['c', 'd']
    known_keys = known_live_keys + known_expired_keys
    unknown_live_keys = ['e', 'f', 'g']
    live_keys = {*known_live_keys, *unknown_live_keys}

    body_pool.update_bodies = mock.Mock(
        return_value={'dropped_keys': known_expired_keys,
                      'new_records': {key: new_body for key
                                      in unknown_live_keys}}
    )
    zone = Zone([MovingObject(BodyObject.generate(key, new_body))
                 for key in known_keys], 50, 50)
    zone.update_objects()
    assert set(obj.body.key for obj in zone.moving_objects) == live_keys
