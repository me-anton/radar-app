from collections import namedtuple
from typing import Iterable, Tuple, List


AlienBody = namedtuple('AlienBody', ('str_lines', 'width', 'height'))
Position = namedtuple('Position', ('x', 'y'))

alien_bodies_str = (
    '''\
--o-----o--
---o---o---
--ooooooo--
-oo-ooo-oo-
ooooooooooo
o-ooooooo-o
o-o-----o-o
---oo-oo---''',
    '''\
---oo---
--oooo--
-oooooo-
oo-oo-oo
oooooooo
--o--o--
-o-oo-o-
o-o--o-o''',
    '''\
-------o-------
-----ooooo-----
---oo--o--oo---
ooooooooooooooo
---oo-----oo---
--o--ooooo--o--
-oo---------oo-'''
)


def create_alien_bodies(bodies_str: Iterable[str]) \
        -> Tuple[List[AlienBody], int, int]:
    _alien_bodies_line_lists = (body.splitlines() for body in bodies_str)
    _alien_bodies_matrices = [[list(line) for line in body]
                              for body in _alien_bodies_line_lists]

    alien_max_width = max(len(body[0]) for body in _alien_bodies_matrices)
    alien_max_height = max(len(body) for body in _alien_bodies_matrices)

    alien_bodies = [AlienBody(body, len(body[0]), len(body))
                    for body in _alien_bodies_matrices]

    return alien_bodies, alien_max_width, alien_max_height


alien_bodies, alien_max_width, alien_max_height = create_alien_bodies(alien_bodies_str)


