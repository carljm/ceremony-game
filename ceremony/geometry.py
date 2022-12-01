from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import reduce, total_ordering
from typing import Dict, FrozenSet, List, Set, Tuple


class InvalidHexError(Exception):
    pass


@total_ordering
@dataclass(frozen=True)
class Hex:
    """A hex position in cube coordinates.

    q, r, and s must always total to zero.

    See https://www.redblobgames.com/grids/hexagons/ for details.

    """

    q: int
    r: int
    s: int

    def __post_init__(self) -> None:
        if self.q + self.r + self.s != 0:
            raise InvalidHexError(f"{self.q} + {self.r} + {self.s} != 0")

    def __add__(self, h: Hex) -> Hex:
        return Hex(self.q + h.q, self.r + h.r, self.s + h.s)

    def __sub__(self, h: Hex) -> Hex:
        return self + (-h)

    def __neg__(self) -> Hex:
        return Hex(-self.q, -self.r, -self.s)

    def __mul__(self, mult: int) -> Hex:
        return Hex(self.q * mult, self.r * mult, self.s * mult)

    def __floordiv__(self, div: int) -> Hex:
        return Hex(self.q // div, self.r // div, self.s // div)

    def __lt__(self, h: Hex) -> bool:
        return (self.q, self.r, self.s) < (h.q, h.r, h.s)

    def is_origin(self) -> bool:
        return self.q == self.r == self.s == 0

    def reflect(self, axis: Axis) -> Hex:
        """Return reflection of this hex across an axis."""
        if axis == Axis.Q:
            return Hex(self.q, self.s, self.r)
        if axis == Axis.R:
            return Hex(self.s, self.r, self.q)
        else:
            assert axis == Axis.S
            return Hex(self.r, self.q, self.s)

    def rotate(self, steps: int = 1) -> Hex:
        """Return clockwise rotation of this hex around origin.

        If `steps` is one, rotate a single hex side; six steps is the identity.

        """
        while steps > 5:
            steps -= 6
        while steps < 0:
            steps += 6
        if steps == 0:
            return self
        q, r, s = self.q, self.r, self.s
        if steps % 2:
            q, r, s = -q, -r, -s
        if steps == 1 or steps == 4:
            q, r, s = s, q, r
        elif steps == 2 or steps == 5:
            q, r, s = r, s, q
        return Hex(q, r, s)

    def ring(self) -> int:
        """Return distance in hexes from origin, or "ring" of this hex."""
        return max(abs(self.q), abs(self.r), abs(self.s))

    def ring_index(self) -> int:
        """
        Return index of this hex around its ring (clockwise, straight up is 0).

        """
        if self.is_origin():
            return 0
        ring = self.ring()
        a_q, a_r, a_s = abs(self.q), abs(self.r), abs(self.s)
        if a_s > a_q and a_s >= a_r:
            sector = 0
            startd = UP
            key = self.s
        elif a_q > a_r and a_q >= a_s:
            sector = 1
            startd = UR
            key = -self.q
        elif a_r > a_s and a_r >= a_q:
            sector = 2
            startd = DR
            key = self.r
        else:  # pragma: no cover
            raise ValueError(f"{self} is not in any sector.")
        if key > 0:
            sector += 3
            startd = startd.rotate(3)
        start = startd * ring
        dist_from_start = (self - start).ring()
        return (sector * ring) + dist_from_start


def distance(h1: Hex, h2: Hex) -> int:
    return (h1 - h2).ring()


OR = Hex(0, 0, 0)
UP = Hex(0, 1, -1)
UR = UP.rotate()
DR = UR.rotate()
DN = DR.rotate()
DL = DN.rotate()
UL = DL.rotate()

DIRS = [UP, UR, DR, DN, DL, UL]


class Axis(Enum):
    Q = 0
    R = 1
    S = 2


@dataclass(frozen=True)
class Shape:
    """
    A hex-grid shape represented as an ordered sequence of Hex.

    In practice a tuple of Hex is used for hashability.

    """

    hexes: FrozenSet[Hex]

    @classmethod
    def of(cls, *hs: Hex) -> Shape:
        """Shortcut to create a normalized shape of given hexes."""
        return cls(frozenset(hs)).normalize()

    def translate(self, h: Hex) -> Shape:
        """Return a new Shape with all hexes translated by h."""
        return Shape(frozenset(n + h for n in self.hexes))

    def rotate(self, steps: int = 1) -> Shape:
        """Return clockwise rotation of this shape (not normalized.)"""
        return Shape(frozenset(h.rotate(steps) for h in self.hexes))

    def reflect(self, axis: Axis) -> Shape:
        """Return reflection of this shape (not normalized.)"""
        return Shape(frozenset(h.reflect(axis) for h in self.hexes))

    def scale_up(self, factor: int) -> Shape:
        """Return this shape scaled up by given integer factor."""
        return Shape(frozenset(n * factor for n in self.hexes))

    def scale_down(self, factor: int) -> Shape:
        """Return this shape scaled down by given integer factor."""
        return Shape(frozenset(n // factor for n in self.hexes))

    def sum(self) -> Hex:
        """Return the vector sum of all hexes in this shape."""
        return reduce(lambda a, b: a + b, self.hexes, Hex(0, 0, 0))

    def mean(self) -> Hex:
        """Return the vector mean of all hexes in this shape."""
        n = len(self.hexes)
        return self.sum() // n

    def normalize(self) -> Shape:
        """
        Return same shape in translationally and rotationally normal form.

        """
        if not self.hexes:
            return self
        # Scale up to N so that vector mean must be a precise integer hex, then
        # translate to make vector mean the origin. This will be stable in rotation.
        scale = len(self.hexes)
        s = self.scale_up(scale)
        s = s.translate(-s.mean())
        rotations = [s.rotate(i) for i in range(6)]
        ring = 1
        outer_ring = max(h.ring() for h in s.hexes)
        while ring <= outer_ring:
            sums = [(r, r.ring_sum(ring)) for r in rotations]
            min_sum = min(s[1] for s in sums)
            rotations = [s[0] for s in sums if s[1] == min_sum]
            if len(rotations) == 1:
                break
            ring += 1
        else:
            # If we still have >1 rotations, we have rotational symmetry
            for r in rotations[1:]:
                assert r == rotations[0]
        s = rotations[0]
        # Now that we've normalized the rotation, translate back to where lowest hex
        # -- in (q, r, s) tuple ordering -- is origin, and scale back down.
        h = sorted(s.hexes)[0]
        return s.translate(-h).scale_down(scale)

    def ring_sum(self, ring: int) -> int:
        """Return binary sum of a ring."""
        return sum(2 ** h.ring_index() for h in self.hexes if h.ring() == ring)


def shape_distance(s1: Shape, s2: Shape) -> int:
    """
    Return "distance" between two shapes

    Distance is defined as sum of squares of distance between nearest-paired hexes.

    """
    # map (hex1-idx, hex2-idx) to distance between them
    distances: Dict[Tuple[int, int], int] = {}
    # map a distance to a list of (hex1-idx, hex2-idx) at that distance
    rev: Dict[int, List[Tuple[int, int]]] = {}
    size: int = len(s1.hexes)
    assert size == len(s2.hexes)
    for i, h1 in enumerate(s1.hexes):
        for j, h2 in enumerate(s2.hexes):
            t = (i, j)
            d = distance(h1, h2)
            distances[t] = d
            rev.setdefault(d, []).append(t)
    seen1: Set[int] = set()
    seen2: Set[int] = set()
    ret: int = 0
    pairs: int = 0
    for dist in sorted(rev.keys()):
        for i, j in rev[dist]:
            if i in seen1 or j in seen2:
                continue
            ret += dist**2
            seen1.add(i)
            seen2.add(j)
            pairs += 1
    assert pairs == size
    return ret
