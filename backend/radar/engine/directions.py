import random
from typing import Dict, Callable, Sequence, ClassVar
from radar.engine.body_objects import Position
from radar.engine import directions_meta


class Direction:
    def __init__(self,
                 name: str,
                 handler: Callable[[Position], Position],
                 risk_zone_provider: Callable[[Position, int, int],
                                              Sequence[Position]],
                 opposite_key: str):
        """
        :param name: direction name
        :param handler: function for moving from current position in this
        direction
        :param risk_zone_provider: points of the moving object
        (assuming it's located in top left corner of an area)
        that should be tested for collision
        :param opposite_key: key for the opposite direction in DirectionsPool
        """
        self.name = name
        self.move_from_pos = handler
        self._risk_zone_provider = risk_zone_provider
        self._opposite_key = opposite_key
        self._opposite = None

    @property
    def opposite(self):
        if self._opposite is None:
            self._opposite = DirectionPool[self._opposite_key]
            del self._opposite_key
            return self._opposite
        else:
            return self._opposite

    def positions_to_occupy_by_movement(self, cur_pos, width, height):
        return self._movement_affected_points(cur_pos, width, height,
                                              self._risk_zone_provider)

    def positions_freed_by_movement(self, new_pos, width, height):
        return self._movement_affected_points(new_pos, width, height,
                                              self.opposite._risk_zone_provider)

    @staticmethod
    def _movement_affected_points(pos, width, height, provider):
        return provider(pos, width=width, height=height)


class __DirectionPoolMeta(type):
    __directions: ClassVar[Dict[str, Direction]] = {
        'left':
            Direction('Left',
                      lambda cur_pos: Position(cur_pos.x - 1, cur_pos.y),
                      directions_meta.left_risk_zone, 'right'),
        'right':
            Direction('Right',
                      lambda cur_pos: Position(cur_pos.x + 1, cur_pos.y),
                      directions_meta.right_risk_zone, 'left'),
        'up':
            Direction('UP',
                      lambda cur_pos: Position(cur_pos.x, cur_pos.y - 1),
                      directions_meta.upper_risk_zone, 'down'),
        'down':
            Direction('Down',
                      lambda cur_pos: Position(cur_pos.x, cur_pos.y + 1),
                      directions_meta.bottom_risk_zone, 'up'),
        'top_left':
            Direction('Top Left',
                      lambda cur_pos: Position(cur_pos.x - 1, cur_pos.y - 1),
                      directions_meta.top_left_risk_zone, 'bottom_right'),
        'top_right':
            Direction('Top Right',
                      lambda cur_pos: Position(cur_pos.x + 1, cur_pos.y - 1),
                      directions_meta.top_right_risk_zone, 'bottom_left'),
        'bottom_left':
            Direction('Bottom Left',
                      lambda cur_pos: Position(cur_pos.x - 1, cur_pos.y + 1),
                      directions_meta.bottom_left_risk_zone, 'top_right'),
        'bottom_right':
            Direction('Bottom Right',
                      lambda cur_pos: Position(cur_pos.x + 1, cur_pos.y + 1),
                      directions_meta.bottom_right_risk_zone, 'top_left')
    }
    values = tuple(__directions.values())

    def __getattr__(cls, item):
        return cls.__directions[item]

    def __getitem__(cls, item: str) -> Direction:
        return cls.__directions[item]


class DirectionPool(metaclass=__DirectionPoolMeta):
    @classmethod
    def random_direction(cls) -> Direction:
        return random.choice(cls.values)

