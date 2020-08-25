from collections import namedtuple


Position = namedtuple('Position', ('x', 'y'))


def _risk_zone_provider(tangent, constant_provider, position_provider):
    def get_positions(pos, **dimensions):
        risk_zone = set()
        constant = constant_provider(pos, **dimensions)
        for i in range(dimensions[tangent]):
            risk_zone.add(position_provider(pos, i, constant))
        return risk_zone

    return get_positions


def _vertical_risk_zone_provider(constant_provider):
    return _risk_zone_provider('width', constant_provider,
                               lambda pos, i, new_y: Position(pos.x + i, new_y))


def _horizontal_risk_zone_provider(constant_provider):
    return _risk_zone_provider('height', constant_provider,
                               lambda pos, i, new_x: Position(new_x, pos.y + i))


def _diagonal_risk_zone_provider(vertical_provider, horizontal_provider,
                                 diagonal_provider):
    def get_positions(pos, **dimensions):
        horizontal_risk_zone = horizontal_provider(pos, **dimensions)
        horizontal_risk_zone.add(diagonal_provider(pos=pos, **dimensions))
        return horizontal_risk_zone | vertical_provider(pos, **dimensions)

    return get_positions


def _leftmost_x_neighbor(pos, width, height):
    return pos.x - 1


def _rightmost_x_neighbor(pos, width, height):
    return pos.x + width


def _topmost_y_neighbor(pos, width, height):
    return pos.y - 1


def _lowest_y_neighbor(pos, width, height):
    return pos.y + height


left_risk_zone = _horizontal_risk_zone_provider(_leftmost_x_neighbor)
right_risk_zone = _horizontal_risk_zone_provider(_rightmost_x_neighbor)
upper_risk_zone = _vertical_risk_zone_provider(_topmost_y_neighbor)
bottom_risk_zone = _vertical_risk_zone_provider(_lowest_y_neighbor)
top_left_risk_zone = \
    _diagonal_risk_zone_provider(upper_risk_zone, left_risk_zone,
                                 lambda **kwargs: Position(_leftmost_x_neighbor(**kwargs),
                                                           _topmost_y_neighbor(**kwargs)))
top_right_risk_zone = \
    _diagonal_risk_zone_provider(upper_risk_zone, right_risk_zone,
                                 lambda **kwargs: Position(_rightmost_x_neighbor(**kwargs),
                                                           _topmost_y_neighbor(**kwargs)))
bottom_left_risk_zone = \
    _diagonal_risk_zone_provider(bottom_risk_zone, left_risk_zone,
                                 lambda **kwargs: Position(_leftmost_x_neighbor(**kwargs),
                                                           _lowest_y_neighbor(**kwargs)))
bottom_right_risk_zone = \
    _diagonal_risk_zone_provider(bottom_risk_zone, right_risk_zone,
                                 lambda **kwargs: Position(_rightmost_x_neighbor(**kwargs),
                                                           _lowest_y_neighbor(**kwargs)))
