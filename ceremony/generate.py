from __future__ import annotations

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
    for h in base.hexes:
        for d in DIRS:
            cand = h + d
            if cand in base.hexes:
                continue
            new = Shape.of(*base.hexes, cand)
            if new not in seen:
                seen.add(new)
                yield new


def max_length(shape: Shape) -> int:
    """Return max length in any dimension.

    So as to stick to integers, lengths are "doubled" -- single hex is 2, "half" hex
    is 1.

    """
    q = sorted(h.q for h in shape.hexes)
    r = sorted(h.r for h in shape.hexes)
    s = sorted(h.s for h in shape.hexes)
    qr_dist = (q[-1] - q[0]) + (r[-1] - r[0])
    qs_dist = (q[-1] - q[0]) + (s[-1] - s[0])
    rs_dist = (r[-1] - r[0]) + (s[-1] - s[0])
    return max(qr_dist, qs_dist, rs_dist)
