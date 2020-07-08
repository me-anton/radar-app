import pytest
from radar.engine.body_objects import Position
from radar.engine.directions import DirectionPool
from radar.tests.engine.share import make_positions


start_pos = Position(5, 5)
width = 4
height = 6
occupy_when_moving_left = make_positions((4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10))
occupy_when_moving_right = make_positions((9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (9, 10))
occupy_when_moving_up = make_positions((5, 4), (6, 4), (7, 4), (8, 4))
occupy_when_moving_down = make_positions((5, 11), (6, 11), (7, 11), (8, 11))
occupy_when_moving_top_left = occupy_when_moving_left + occupy_when_moving_up + [Position(4, 4)]
occupy_when_moving_top_right = occupy_when_moving_right + occupy_when_moving_up + [Position(9, 4)]
occupy_when_moving_bottom_left = occupy_when_moving_left + occupy_when_moving_down + [Position(4, 11)]
occupy_when_moving_bottom_right = occupy_when_moving_right + occupy_when_moving_down + [Position(9, 11)]


@pytest.mark.parametrize("direction, expected_output", [
    [DirectionPool.left, occupy_when_moving_left],
    [DirectionPool.right, occupy_when_moving_right],
    [DirectionPool.up, occupy_when_moving_up],
    [DirectionPool.down, occupy_when_moving_down],
    [DirectionPool.top_left, occupy_when_moving_top_left],
    [DirectionPool.top_right, occupy_when_moving_top_right],
    [DirectionPool.bottom_left, occupy_when_moving_bottom_left],
    [DirectionPool.bottom_right, occupy_when_moving_bottom_right]
])
def test_positions_to_occupy_by_movement(direction, expected_output):
    assert direction.positions_to_occupy_by_movement(start_pos, width, height) \
           == set(expected_output), \
           'Incorrect prediction for positions occupied by moving ' \
           f'{direction.name} from {start_pos}'


free_when_moving_left = occupy_when_moving_right
free_when_moving_right = occupy_when_moving_left
free_when_moving_up = occupy_when_moving_down
free_when_moving_down = occupy_when_moving_up
free_when_moving_top_left = occupy_when_moving_bottom_right
free_when_moving_top_right = occupy_when_moving_bottom_left
free_when_moving_bottom_left = occupy_when_moving_top_right
free_when_moving_bottom_right = occupy_when_moving_top_left


@pytest.mark.parametrize('direction, expected_output', [
    [DirectionPool.left, free_when_moving_left],
    [DirectionPool.right, free_when_moving_right],
    [DirectionPool.up, free_when_moving_up],
    [DirectionPool.down, free_when_moving_down],
    [DirectionPool.top_left, free_when_moving_top_left],
    [DirectionPool.top_right, free_when_moving_top_right],
    [DirectionPool.bottom_left, free_when_moving_bottom_left],
    [DirectionPool.bottom_right, free_when_moving_bottom_right]
])
def test_positions_freed_by_movement(direction, expected_output):
    assert direction.positions_freed_by_movement(start_pos, width, height) \
           == set(expected_output), \
           'Incorrect prediction for positions freed by moving ' \
           f'{direction.name} from {start_pos}'
