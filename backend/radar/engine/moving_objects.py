import random
from typing import Set, Iterator
from radar.engine.moving_objects_meta import Position, alien_bodies
from radar.engine import directions_meta


class _Direction:
    def __init__(self, name, handler, risk_zone_provider, opposite_idx):
        """
        :param name: direction name
        :param handler: function for moving from current position in this direction
        :param risk_zone_provider: points of the moving object
        (assuming it's located in top left corner of an area)
        that should be tested for collision
        :param opposite_idx: opposite direction index in _directions_list
        """
        self.name = name
        self.move_from_pos = handler
        self._risk_zone_provider = risk_zone_provider
        self._opposite_idx = opposite_idx

    def collision_risk_points(self, cur_pos, width, height):
        return self._movement_affected_points(cur_pos, width, height,
                                              self._risk_zone_provider)

    def freed_after_movement_points(self, new_pos, width, height):
        opposite_direction = _directions_list[self._opposite_idx]
        return self._movement_affected_points(new_pos, width, height,
                                              opposite_direction._risk_zone_provider)

    @staticmethod
    def _movement_affected_points(pos, width, height, provider):
        return provider(pos, width=width, height=height)


_directions_list = (
    _Direction('Left', lambda cur_pos: Position(cur_pos.x - 1, cur_pos.y),
               directions_meta.left_risk_zone, 1),
    _Direction('Right', lambda cur_pos: Position(cur_pos.x + 1, cur_pos.y),
               directions_meta.right_risk_zone, 0),
    _Direction('UP', lambda cur_pos: Position(cur_pos.x, cur_pos.y - 1),
               directions_meta.upper_risk_zone, 3),
    _Direction('Down', lambda cur_pos: Position(cur_pos.x, cur_pos.y + 1),
               directions_meta.bottom_risk_zone, 2),
    _Direction('Top Left', lambda cur_pos: Position(cur_pos.x - 1, cur_pos.y - 1),
               directions_meta.top_left_risk_zone, 7),
    _Direction('Top Right', lambda cur_pos: Position(cur_pos.x + 1, cur_pos.y - 1),
               directions_meta.top_right_risk_zone, 6),
    _Direction('Bottom Left', lambda cur_pos: Position(
        cur_pos.x - 1, cur_pos.y + 1), directions_meta.bottom_left_risk_zone, 5),
    _Direction('Bottom Right', lambda cur_pos: Position(
        cur_pos.x + 1, cur_pos.y + 1), directions_meta.bottom_right_risk_zone, 4)
)


class MovingObject:
    def __init__(self, body_idx: int, position: Position = None):
        self.direction: _Direction = random.choice(_directions_list)
        self.body_idx = body_idx
        self.body = alien_bodies[body_idx]
        self.height = self.body.height
        self.width = self.body.width
        self.position: Position = position

    def estimate_movement(self) -> Set[Position]:
        return self.direction.collision_risk_points(self.position,
                                                    self.width,
                                                    self.height)

    def move(self) -> Set[Position]:
        self.position = self.direction.move_from_pos(self.position)
        return self.direction.freed_after_movement_points(self.position,
                                                          self.width,
                                                          self.height)

    def evade_collision(self):
        self._get_new_direction()

    def _get_new_direction(self):
        old_direction = self.direction
        while self.direction == old_direction:
            self.direction = random.choice(_directions_list)

    def get_line_iterator(self):
        return iter(self.body.str_lines)
