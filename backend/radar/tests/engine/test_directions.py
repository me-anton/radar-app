import pytest
from radar.engine.alien_bodies import Position
from radar.engine.directions import directions_pool
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
    [directions_pool.left, occupy_when_moving_left],
    [directions_pool.right, occupy_when_moving_right],
    [directions_pool.up, occupy_when_moving_up],
    [directions_pool.down, occupy_when_moving_down],
    [directions_pool.top_left, occupy_when_moving_top_left],
    [directions_pool.top_right, occupy_when_moving_top_right],
    [directions_pool.bottom_left, occupy_when_moving_bottom_left],
    [directions_pool.bottom_right, occupy_when_moving_bottom_right]
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
    [directions_pool.left, free_when_moving_left],
    [directions_pool.right, free_when_moving_right],
    [directions_pool.up, free_when_moving_up],
    [directions_pool.down, free_when_moving_down],
    [directions_pool.top_left, free_when_moving_top_left],
    [directions_pool.top_right, free_when_moving_top_right],
    [directions_pool.bottom_left, free_when_moving_bottom_left],
    [directions_pool.bottom_right, free_when_moving_bottom_right]
])
def test_positions_freed_by_movement(direction, expected_output):
    assert direction.positions_freed_by_movement(start_pos, width, height) \
           == set(expected_output), \
           'Incorrect prediction for positions freed by moving ' \
           f'{direction.name} from {start_pos}'
