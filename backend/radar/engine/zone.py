from collections import namedtuple
from itertools import repeat
from operator import attrgetter
from random import randint, randrange
from copy import deepcopy
from typing import Iterable, List, Optional

from radar.engine.moving_objects import MovingObject
from radar.engine.alien_bodies import Position


class Zone:
    void = '-'
    matter = 'o'

    def __init__(self, moving_objects: List[MovingObject],
                 width: int = 300, height: int = 100,
                 position_vacancy: Optional[List[List[bool]]] = None):
        # No big reason for that one, just making sure nobody abuses
        # the computational costs that come with this class
        if width >= 1000 or height >= 1000:
            raise ValueError(
                f'Zone size {width}x{height} is too big. It has to be '
                f'at most 1000x1000')

        self.width = width
        self.height = height

        self._check_moving_objects_dimensions(moving_objects)
        self.__moving_objects = moving_objects

        # if position vacancy matrix isn't provided, provided moving objects'
        # positions are ignored and overridden
        if position_vacancy is None:
            self._position_vacancy = [
                [True for _ in range(width)] for _ in range(height)]
            self._place_moving_objects()
        else:
            self._position_vacancy = position_vacancy

    def _check_moving_objects_dimensions(self, moving_objects):
        max_obj_width = max(obj.width for obj in moving_objects)
        max_obj_height = max(obj.height for obj in moving_objects)
        if self.width < max_obj_width or self.height < max_obj_height:
            raise ValueError(
                f'Zone size {self.width}x{self.height} is too small')

    def _place_moving_objects(self):
        for obj in self.__moving_objects:
            while obj.position is None:
                x = randint(0, self.width - obj.width)
                y = randint(0, self.height - obj.height)
                if self._region_is_vacant(x, y, obj.width, obj.height):
                    obj.position = Position(x, y)
                    self._occupy_region(x, y, obj.width, obj.height)

    def _region_is_vacant(self, x, y, width, height):
        region_vacancy = ((self._position_vacancy[i][j] for j in range(
            x, x + width) for i in range(y, y + height)))
        return all(region_vacancy)

    def _occupy_region(self, x, y, width, height):
        self._change_region_vacancy(x, y, width, height, False)

    def _change_region_vacancy(self, x, y, width, height, vacancy):
        for i in range(y, y + height):
            for j in range(x, x + width):
                self._position_vacancy[i][j] = vacancy

    def _free_positions(self, positions):
        self._change_positions_vacancy(positions, True)

    def _occupy_positions(self, positions):
        self._change_positions_vacancy(positions, False)

    def _change_positions_vacancy(self, positions, vacancy):
        for p in positions:
            self._position_vacancy[p.y][p.x] = vacancy

    def move_objects(self, max_attempts=7):
        for obj in self.__moving_objects:
            attempts = 0
            while attempts < max_attempts:
                goto_positions = obj.estimate_movement()
                if self._are_available(goto_positions):
                    self._occupy_positions(goto_positions)
                    freed_positions = obj.move()
                    self._free_positions(freed_positions)
                    break
                else:
                    obj.evade_collision()
                    attempts += 1

    def _are_available(self, positions):
        try:
            positions_vacancy = (
                p.x >= 0 and p.y >= 0 and self._position_vacancy[p.y][p.x]
                for p in positions
            )
            return all(positions_vacancy)
        except IndexError:
            return False

    def draw_position_vacancy(self):
        lines = (''.join((self.void if vacant else self.matter
                          for vacant in line))
                 for line in self._position_vacancy)
        return '\n'.join(lines)

    def draw(self, positive_noise=3, negative_noise=5):
        self.__moving_objects.sort(key=attrgetter('position.y'))
        printable_objects = [_PrintableObject(obj.position.x,
                                              obj.width,
                                              obj.position.y,
                                              obj.get_line_iterator())
                             for obj in self.__moving_objects]
        zone_lines = []
        objects_drawn = 0
        for y in range(self.height):
            obj_lines = []
            for obj in printable_objects[objects_drawn:]:
                if y < obj.y:
                    break
                else:
                    try:
                        obj_line_str = next(obj.lines)
                    except StopIteration:
                        objects_drawn += 1
                    else:
                        obj_lines.append(_ObjectLine(
                            obj.x, obj.width, obj_line_str))
            obj_lines.sort(key=attrgetter('x'))
            line = []
            x = 0
            for obj_line in obj_lines:
                line += self._fill_void(obj_line.x - x)
                line += obj_line.line
                x = obj_line.x + obj_line.width
            line += self._fill_void(self.width - x)
            self._apply_noise(line, positive_noise, negative_noise)
            zone_lines.append(''.join(line))
        return '\n'.join(zone_lines)

    def _apply_noise(self, zone_line, positive_noise, negative_noise):
        self._add_distortion(zone_line, positive_noise, self.matter)
        self._add_distortion(zone_line, negative_noise, self.void)

    def _add_distortion(self, zone_line, percent, symbol):
        distorted_positions = int(self.width * percent / 100)
        for _ in range(distorted_positions):
            x = randrange(0, self.width)
            zone_line[x] = symbol

    def _fill_void(self, num):
        return list(repeat(self.void, num))

    def __str__(self):
        return self.draw()

    @property
    def moving_objects(self):
        return deepcopy(self.__moving_objects)


_PrintableObject = namedtuple('_PrintableObject', ('x', 'width', 'y', 'lines'))
_ObjectLine = namedtuple('_ObjectLine', ('x', 'width', 'line'))
ObjectRequest = namedtuple('ObjectRequest', ('body_idx', 'num'))


def create_zone(width: int = 300, height: int = 100,
                *moving_objects_by_index: Iterable[ObjectRequest]) -> Zone:
    moving_objects = _create_moving_objects(
        moving_objects_by_index or (ObjectRequest(0, 10),
                                    ObjectRequest(1, 10),
                                    ObjectRequest(2, 10)))
    return Zone(moving_objects, width, height)


def _create_moving_objects(objs):
    moving_objects = []
    for body_idx, num in objs:
        moving_objects += [MovingObject(body_idx) for _ in range(num)]
    return moving_objects
