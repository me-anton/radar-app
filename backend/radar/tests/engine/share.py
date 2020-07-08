from typing import Tuple
from radar.engine.body_objects import Position

from radar.tests.engine._moving import assert_pos_moved


def make_positions(*coordinates: Tuple[int, int]):
    positions = []
    for x, y in coordinates:
        positions.append(Position(x, y))
    return positions
