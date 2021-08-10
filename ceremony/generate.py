from typing import Iterator

from ceremony.collection import ShapeSet
from ceremony.geometry import Shape, DIRS


def extensions(base: Shape) -> Iterator[Shape]:
    """
    Yield all valid shapes derived from adding one hex to base shape.

    Shapes must be contiguous. (TODO more validity restrictions.)

    """
    hexes = set(base.hexes)
    seen = ShapeSet()
    for h in hexes:
        for d in DIRS:
            cand = h + d
            if cand in hexes:
                continue
            new = Shape(list(base.hexes) + [cand]).normalize()
            added = seen.add(new)
            if added:
                yield new
