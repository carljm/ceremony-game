from __future__ import annotations

from itertools import groupby
from random import shuffle
from typing import Collection, Dict, Iterator, Set

from ceremony.geometry import Shape, DIRS, OR, UR, UP, UL


QUOTAS = [
    (4, 28),
    (3, 24),
    (2, 18),
    (1, 14),
    (0, 10),
]


def generate() -> Collection[Shape]:
    """
    Yield a set of nine-node shapes meeting criteria.
    """
    eight_node_shapes = generate_all(8)
    to_sources: Dict[int, Dict[Shape, Set[Shape]]] = {}
    for shape in eight_node_shapes:
        for ext in extensions(shape):
            if max_length(ext) <= 8 and 3 <= longest_line(ext) < 5:
                numtri = num_triangles(ext)
                to_sources.setdefault(numtri, {}).setdefault(ext, set()).add(shape)

    sources_seen: Set[Shape] = set()
    shapes = []
    for numtri, quota in QUOTAS:
        shapes_sources = list(to_sources.get(numtri, {}).items())
        shuffle(shapes_sources)
        shapes_sources.sort(key=lambda t: t[0].asymmetry())
        count = 0
        for shape, sources in shapes_sources:
            if not sources.intersection(sources_seen):
                shapes.append(shape)
                sources_seen.update(sources)
                count += 1
            if count >= quota:
                print(f"Found {count} shapes with {numtri} triangles.")
                break
        else:  # pragma: no cover
            print(f"Unable to find {quota} shapes with {numtri} triangles.")

    return shapes


def generate_all(size: int) -> Collection[Shape]:
    """Yield all valid size-node shapes."""
    assert size >= 2
    shapes = set([Shape.of(OR, UR)])

    for i in range(size - 2):
        new = set()
        for shape in shapes:
            for ext in extensions(shape):
                if max_length(ext) <= 8 and longest_line(ext) < 5:
                    new.add(ext)
        shapes = new

    return shapes


def extensions(base: Shape) -> Iterator[Shape]:
    """Yield all contiguous shapes derived from adding one hex to base shape."""
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


def num_triangles(shape: Shape) -> int:
    """Return number of triangles in shape."""
    ret = 0
    for h in shape.hexes:
        if (h + UP) in shape.hexes:
            if (h + UR) in shape.hexes:
                ret += 1
            if (h + UL) in shape.hexes:
                ret += 1
    return ret


def max_length(shape: Shape) -> int:
    """Return max length of shape in any dimension.

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


def longest_line(shape: Shape) -> int:
    """Return length of longest straight line in shape."""
    max_line = 1
    for dim1, dim2 in [("q", "r"), ("r", "s"), ("s", "q")]:
        hexes = sorted(shape.hexes, key=lambda h: (getattr(h, dim1), getattr(h, dim2)))
        for _d1val, row in groupby(hexes, lambda h: getattr(h, dim1)):
            curlen = 0
            lastv = None
            for h in row:
                v = getattr(h, dim2)
                if lastv is None or v - lastv == 1:
                    curlen += 1
                else:
                    curlen = 1
                lastv = v
            if curlen > max_line:
                max_line = curlen
    return max_line
