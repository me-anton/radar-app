from collections import namedtuple
from itertools import repeat
from operator import attrgetter
from random import randint, randrange
from copy import deepcopy
from typing import Iterable, List, Optional

from radar.engine.moving_objects import MovingObject
from radar.engine.body_objects import Position, BodyObjectsPool
from share.metaclasses import Singleton


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

        self._check_zone_volume(moving_objects)
        self.__moving_objects = moving_objects

        # if position vacancy matrix isn't provided, provided moving objects'
        # positions are ignored and overridden
        if position_vacancy is None:
            self._position_vacancy = [
                [True for _ in range(width)] for _ in range(height)]
            self._place_moving_objects()
        else:
            self._position_vacancy = position_vacancy

    def update_image(self) -> str:
        """Update, move and draw all objects in the zone"""
        self.move_objects()
        return self.draw()

    @property
    def moving_objects(self):
        """Objects moving across zone with each move_objects method call"""
        return deepcopy(self.__moving_objects)

    def fits_profile(self, profile: 'ZoneProfile') -> bool:
        """
        Check if the zone has the same parameters as provided profile
        """
        return self.width == profile.width and self.height == profile.height

    def __str__(self):
        return self.draw()

    def move_objects(self, max_attempts=7):
        """
        Move all moving objects in the zone in the direction they were
        moving or in a new direction in the case of collision;
        or don't move them at all in the case they are trapped
        """
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

    def draw(self, positive_noise=3, negative_noise=5):
        """Represent the zone and objects in it as string"""
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

    def draw_position_vacancy(self):
        """
        Draw all objects in the zone as the place they occupy,
        ignoring their body strings and only accounting for their profile.
        Useful for debugging.
        """
        lines = (''.join((self.void if vacant else self.matter
                          for vacant in line))
                 for line in self._position_vacancy)
        return '\n'.join(lines)

    def _check_zone_volume(self, moving_objects):
        """
        Check if the zone provides enough space to fit all the moving objects
        with enough space for them to actually move.

        The rule is that the zone has to be at least as tall as all the
        moving objects with twice their width neatly squeezed in the zone's
        width
        """
        max_obj_width = max(obj.width for obj in moving_objects) * 2
        max_obj_height = max(obj.height for obj in moving_objects)
        if self.width < max_obj_width or self.height < max_obj_height:
            raise ValueError('The moving objects are too big')

        min_profile_width = 0
        min_profile_height = 0
        line_width = 0
        max_height_on_line = 0
        for obj in moving_objects:
            new_line_width = line_width + obj.width * 2
            if new_line_width > self.width:
                if min_profile_width < line_width:
                    min_profile_width = line_width
                min_profile_height += max_height_on_line
                line_width, max_height_on_line = \
                    self._update_line(obj.width * 2, 0, obj)
            else:
                line_width, max_height_on_line = \
                    self._update_line(new_line_width, max_height_on_line, obj)
        min_profile_height += max_height_on_line

        if self.width < min_profile_width or self.height < min_profile_height:
            raise TooManyMovingObjectsError('The zone size is too small')

    @staticmethod
    def _update_line(new_line_width, max_height_on_line, obj):
        line_width = new_line_width
        if max_height_on_line < obj.height:
            max_height_on_line = obj.height
        return line_width, max_height_on_line

    def _place_moving_objects(self):
        for obj in self.__moving_objects:
            while obj.position is None:
                x = randint(0, self.width - obj.width)
                y = randint(0, self.height - obj.height)
                if self._region_is_vacant(x, y, obj.width, obj.height):
                    obj.position = Position(x, y)
                    self._occupy_region(x, y, obj.width, obj.height)

    def _region_is_vacant(self, x, y, width, height):
        region_vacancy = ((self._position_vacancy[i][j] for j in
                           range(x, x + width) for i in range(y, y + height)))
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

    def _are_available(self, positions):
        try:
            positions_vacancy = (
                p.x >= 0 and p.y >= 0 and self._position_vacancy[p.y][p.x]
                for p in positions
            )
            return all(positions_vacancy)
        except IndexError:
            return False

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


class TooManyMovingObjectsError(ValueError):
    """
    Thrown if there is an attempt to build a zone with more moving objects
    then it can fit
    """
    pass


_PrintableObject = namedtuple('_PrintableObject', ('x', 'width', 'y', 'lines'))
_ObjectLine = namedtuple('_ObjectLine', ('x', 'width', 'line'))
ObjectRequest = namedtuple('ObjectRequest', ('body_obj', 'num'))
ZoneProfile = namedtuple('ZoneProfile', ('width', 'height'))


class ZoneBuilder(metaclass=Singleton):
    """
    Class for creating Zone class instances and MovingObject instances for them
    """
    small_zone_profile = ZoneProfile(75, 25)
    medium_zone_profile = ZoneProfile(150, 50)
    large_zone_profile = ZoneProfile(300, 100)

    def __init__(self):
        self.body_pool = BodyObjectsPool()

    def request_small_zone(self, *obj_requests: Iterable[ObjectRequest]) -> Zone:
        """
        Returns a Zone instance with small profile and moving objects created
        according to obj_requests (or with default objects)
        """
        obj_requests = obj_requests or (ObjectRequest(self.body_pool.first, 2),
                                        ObjectRequest(self.body_pool.second, 2),
                                        ObjectRequest(self.body_pool.third, 2))
        return self.request_custom_zone(*self.small_zone_profile, *obj_requests)

    def request_medium_zone(self, *obj_requests: Iterable[ObjectRequest]) -> Zone:
        """
        Creates a Zone instance with medium profile and moving objects created
        according to obj_requests (or with default objects)
        """
        obj_requests = obj_requests or (ObjectRequest(self.body_pool.first, 5),
                                        ObjectRequest(self.body_pool.second, 5),
                                        ObjectRequest(self.body_pool.third, 5))
        return self.request_custom_zone(*self.medium_zone_profile,
                                        *obj_requests)

    def request_large_zone(self, *obj_requests: Iterable[ObjectRequest]) -> Zone:
        """
        Creates a Zone instance with large profile and moving objects created
        according to obj_requests (or with default objects)
        """
        return self.request_custom_zone(*self.large_zone_profile, *obj_requests)

    def request_custom_zone(self, width: int = 300, height: int = 100,
                            *obj_requests: ObjectRequest) -> Zone:
        """
        Creates a Zone instance with set profile and moving objects created
        according to obj_requests (or with default objects)
        """
        obj_requests = obj_requests or (ObjectRequest(self.body_pool.first, 10),
                                        ObjectRequest(self.body_pool.second, 10),
                                        ObjectRequest(self.body_pool.third, 10))
        moving_objects = self._create_moving_objects(obj_requests)
        return Zone(moving_objects, width, height)

    @classmethod
    def create_small_zone(cls, moving_objects: List[MovingObject],
                          position_vacancy: Optional[List[List[bool]]] = None) -> Zone:
        """
        Creates a Zone instance with small profile
        """
        return cls.create_custom_zone(moving_objects, *cls.small_zone_profile,
                                      position_vacancy=position_vacancy)

    @classmethod
    def create_medium_zone(cls, moving_objects: List[MovingObject],
                           position_vacancy: Optional[
                           List[List[bool]]] = None) -> Zone:
        """
        Creates a Zone instance with medium profile
        """
        return cls.create_custom_zone(moving_objects, *cls.medium_zone_profile,
                                      position_vacancy=position_vacancy)

    @classmethod
    def create_large_zone(cls, moving_objects: List[MovingObject],
                          position_vacancy: Optional[
                          List[List[bool]]] = None) -> Zone:
        """
        Creates a Zone instance with large profile
        """
        return cls.create_custom_zone(moving_objects, *cls.large_zone_profile,
                                      position_vacancy=position_vacancy)

    @staticmethod
    def create_custom_zone(moving_objects: List[MovingObject],
                           width: int, height: int,
                           position_vacancy: Optional[List[List[bool]]] = None) -> Zone:
        """
        Creates a Zone instance with set profile
        """
        return Zone(moving_objects, width, height, position_vacancy)

    @staticmethod
    def _create_moving_objects(obj_requests: Iterable[ObjectRequest]):
        moving_objects = []
        for body, num in obj_requests:
            moving_objects += [MovingObject(body) for _ in range(num)]
        return moving_objects
