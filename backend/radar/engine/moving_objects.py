from typing import Set, Optional
from radar.engine.alien_bodies import Position, alien_bodies
from radar.engine.directions import Direction, DirectionPool


class MovingObject:
    def __init__(self, body_idx: int, position: Optional[Position] = None):
        self.direction: Direction = DirectionPool.random_direction()
        self.body_idx = body_idx
        self.body = alien_bodies[body_idx]
        self.height = self.body.height
        self.width = self.body.width
        self.position: Position = position

    def estimate_movement(self) -> Set[Position]:
        return self.direction.positions_to_occupy_by_movement(self.position,
                                                              self.width,
                                                              self.height)

    def move(self) -> Set[Position]:
        self.position = self.direction.move_from_pos(self.position)
        return self.direction.positions_freed_by_movement(self.position,
                                                          self.width,
                                                          self.height)

    def evade_collision(self):
        self._get_new_direction()

    def _get_new_direction(self):
        old_direction = self.direction
        while self.direction == old_direction:
            self.direction = DirectionPool.random_direction()

    def get_line_iterator(self):
        return iter(self.body.str_lines)

    def __repr__(self):
        return f'Obj: body id {self.body_idx}; profile ' \
               f'{self.width}x{self.height}'
