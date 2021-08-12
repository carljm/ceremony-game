from __future__ import annotations

from dataclasses import dataclass
from functools import reduce, total_ordering
from typing import FrozenSet


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
        else:
            raise ValueError(f"{self} is not in any sector.")
        if key > 0:
            sector += 3
            startd = startd.rotate(3)
        start = startd * ring
        dist_from_start = (self - start).ring()
        return (sector * ring) + dist_from_start


OR = Hex(0, 0, 0)
UP = Hex(0, 1, -1)
UR = UP.rotate()
DR = UR.rotate()
DN = DR.rotate()
DL = DN.rotate()
UL = DL.rotate()

DIRS = [UP, UR, DR, DN, DL, UL]


@dataclass(frozen=True)
class Shape:
    """
    A hex-grid shape represented as an ordered sequence of Hex.

    In practice a tuple of Hex is used for hashability.

    A scaling factor is also included, so that we can always have an integer-coordinates
    center of mass / vector mean. In normalized form the scale should always equal the
    number of hexes in the shape, but we explicitly track the scale to allow
    construction of denormalized shapes.

    Hexes always use integer coordinates, so if a shape is constructed with a scale that
    is not a factor of all coordinates of all hexes in the shape, normalization could
    result in floor division and an InvalidHexError. In general manual Shape
    construction should always use scale=1 and only normalization should re-scale.

    """

    hexes: FrozenSet[Hex]
    _scale: int = 1

    @classmethod
    def of(cls, *hs: Hex) -> Shape:
        """Shortcut to create a normalized shape of given hexes."""
        return cls(frozenset(hs)).normalize()

    def translate(self, h: Hex) -> Shape:
        """Return a new Shape with all hexes translated by h."""
        return Shape(frozenset(n + h for n in self.hexes), self._scale)

    def rotate(self, steps: int = 1) -> Shape:
        """Return clockwise rotation of this shape (not normalized.)"""
        return Shape(frozenset(h.rotate(steps) for h in self.hexes), self._scale)

    def scale_up(self, factor: int) -> Shape:
        """Return this shape scaled up by given integer factor."""
        return Shape(frozenset(n * factor for n in self.hexes), self._scale * factor)

    def scale_down(self, factor: int) -> Shape:
        """Return this shape scaled down by given integer factor."""
        assert self._scale % factor == 0
        return Shape(frozenset(n // factor for n in self.hexes), self._scale // factor)

    def scale_to_one(self) -> Shape:
        """Translate shape onto unit grid and scale down to scale == 1."""
        if not self.hexes:
            return self
        sample_hex = sorted(self.hexes)[0]
        return self.translate(-sample_hex).scale_down(self._scale)

    def sum(self) -> Hex:
        """Return the vector sum of all hexes in this shape."""
        return reduce(lambda a, b: a + b, self.hexes, Hex(0, 0, 0))

    def mean(self) -> Hex:
        """
        Return the vector mean of all hexes in this shape.

        Requires that shape is scaled to a multiple of N, where N is number of hexes in
        shape.

        """
        n = len(self.hexes)
        assert self._scale % n == 0
        return self.sum() // n

    def normalize_translation(self) -> Shape:
        """Return the same Shape in translationally normal form.

        This means that the origin is also the center of mass (or vector mean) of the
        shape. We scale the shape to N (where N is number of nodes) to ensure the vector
        mean is an integer-coordinates hex.

        Requires that shape must initially have scale == 1.

        """
        if not self.hexes:
            return self
        assert self._scale == 1
        s = self.scale_up(len(self.hexes))
        return s.translate(-s.mean())

    def normalize(self) -> Shape:
        """
        Return same shape in translationally and rotationally normal form.

        """
        if not self.hexes:
            return self
        s = self.normalize_translation()
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
        return rotations[0]

    def ring_sum(self, ring: int) -> int:
        """Return binary sum of a ring."""
        return sum(2 ** h.ring_index() for h in self.hexes if h.ring() == ring)
