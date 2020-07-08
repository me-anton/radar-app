import logging
import os
from radar.engine.body_objects import Position

logger = logging.getLogger('.'.join(os.path.splitext(__file__)[:-1]))


def _pos_moving_assertion(x_transform, y_transform):
    def check_moved_pos(old_pos: Position, new_pos: Position,
                        fail_on_unmoved: bool = False):
        pos_after_movement = Position(x_transform(old_pos.x),
                                      y_transform(old_pos.y))
        try:
            assert new_pos == pos_after_movement, \
                f'Incorrect movement: from {old_pos} to {new_pos} ' \
                f'(should have moved to {pos_after_movement})'
        except AssertionError as err:
            if old_pos == new_pos and not fail_on_unmoved:
                logger.debug("Object's position didn't change")
            else:
                raise err

    return check_moved_pos


_x_right = lambda x: x + 1
_x_left = lambda x: x - 1
_x_stay = lambda x: x
_y_up = lambda y: y - 1
_y_down = lambda y: y + 1
_y_stay = lambda y: y

_directed_assertions = {
    'Left': _pos_moving_assertion(_x_left, _y_stay),
    'Right': _pos_moving_assertion(_x_right, _y_stay),
    'Up': _pos_moving_assertion(_x_stay, _y_up),
    'Down': _pos_moving_assertion(_x_stay, _y_down),
    'Top Left': _pos_moving_assertion(_x_left, _y_up),
    'Top Right': _pos_moving_assertion(_x_right, _y_up),
    'Bottom Left': _pos_moving_assertion(_x_left, _y_down),
    'Bottom Right': _pos_moving_assertion(_x_right, _y_down)
}


def assert_pos_moved(old_pos: Position, new_pos: Position, direction: str,
                     fail_on_unmoved: bool = False):
    _directed_assertions[direction.title()](old_pos, new_pos,
                                            fail_on_unmoved)
