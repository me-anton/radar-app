import pytest
from radar.engine.moving_objects import MovingObject, Position
from radar.tests.engine.share import assert_pos_moved


@pytest.fixture()
def moving_obj():
    return MovingObject(body_idx=0, position=Position(1, 1))


def test_estimate_movement(moving_obj):
    estimate = moving_obj.estimate_movement()
    estimate_of_direction = moving_obj.direction.\
        positions_to_occupy_by_movement(moving_obj.position,
                                        moving_obj.width,
                                        moving_obj.height)
    assert estimate == estimate_of_direction


def test_move(moving_obj):
    position_before = moving_obj.position
    freed_positions_estimate = moving_obj.move()
    position_after = moving_obj.position
    estimate_of_direction = moving_obj.direction.\
        positions_freed_by_movement(moving_obj.position,
                                    moving_obj.width,
                                    moving_obj.height)

    assert_pos_moved(position_before, position_after,
                     moving_obj.direction.name, fail_on_unmoved=True)
    assert freed_positions_estimate == estimate_of_direction


def test_evade_collision(moving_obj):
    estimate_before = moving_obj.estimate_movement()
    moving_obj.evade_collision()
    estimate_after = moving_obj.estimate_movement()
    assert estimate_before != estimate_after


def test_get_line_iterator(moving_obj):
    str_body = moving_obj.body.str_lines
    iter_body = list(moving_obj.get_line_iterator())
    assert str_body == iter_body

