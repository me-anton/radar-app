import pytest
import random
from radar.engine.zone import (
    Zone, create_custom_zone, ObjectRequest, TooManyMovingObjectsError,
    SmallZone, MediumZone, LargeZone
)
from radar.engine.moving_objects import MovingObject
from radar.tests.engine.share import assert_pos_moved


@pytest.fixture
def def_zone():
    return create_custom_zone()


@pytest.fixture
def alien1():
    return MovingObject(0)


@pytest.fixture
def alien2():
    return MovingObject(1)


@pytest.fixture
def alien3():
    return MovingObject(2)


def test_zone_too_small(alien1):
    with pytest.raises(ValueError):
        Zone([alien1], alien1.width, alien1.height)


def test_too_many_moving_objects(alien1):
    with pytest.raises(TooManyMovingObjectsError):
        Zone([alien1] * 2, alien1.width * 2, alien1.height)


def test_zone_too_big(alien1):
    with pytest.raises(ValueError):
        Zone([alien1], 1000, 1000)


@pytest.mark.parametrize('zone_cls', [SmallZone, MediumZone, LargeZone])
def test_max_out_zone(alien1, alien2, alien3, zone_cls):
    aliens = (alien1, alien2, alien3)
    moving_objects = []
    while True:
        moving_objects.append(random.choice(aliens))
        try:
            zone_cls(moving_objects)
        except TooManyMovingObjectsError:
            break
        except Exception as err:
            raise AssertionError(err)


@pytest.mark.parametrize("width, height, moving_objects_by_index", [
    (30, 30, [ObjectRequest(0, 1)]),
    (30, 100, [ObjectRequest(1, 3)]),
    (150, 30, [ObjectRequest(0, 1), ObjectRequest(1, 1), ObjectRequest(2, 2)])
])
def test_create_zone(width, height, moving_objects_by_index):
    zone = create_custom_zone(width, height, *moving_objects_by_index)
    assert zone.width == width
    assert zone.height == height
    _check_initialized_moving_objects(moving_objects_by_index,
                                      zone.moving_objects)


def _check_initialized_moving_objects(request, moving_objects):
    moving_objects_by_index = request.copy()
    for obj in moving_objects:
        for i, obj_req in enumerate(moving_objects_by_index):
            if obj_req.body_idx == obj.body_idx:
                _fail_on_excess_objects(request, moving_objects, obj_req, i)
                moving_objects_by_index[i] = ObjectRequest(obj_req.body_idx,
                                                           obj_req.num - 1)
                break


def _fail_on_excess_objects(request, moving_objects, obj_req, i):
    if obj_req.num == 0:
        num_of_requested_objs = len(
            [req_obj for req_obj in moving_objects
             if req_obj.body_idx == obj_req.body_idx])
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
