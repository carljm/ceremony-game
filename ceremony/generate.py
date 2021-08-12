from typing import Iterator

from ceremony.geometry import Shape, DIRS


def extensions(base: Shape) -> Iterator[Shape]:
    """
    Yield all valid shapes derived from adding one hex to base shape.

    Shapes must be contiguous. Base shape will be translated onto grid and scaled down
    to scale == 1.

    (TODO more validity restrictions.)

    """
    seen = set()
    base = base.scale_to_one()
    for h in base.hexes:
        for d in DIRS:
            cand = h + d
            if cand in base.hexes:
                continue
            new = Shape.of(*base.hexes, cand)
            if new not in seen:
                seen.add(new)
                yield new
