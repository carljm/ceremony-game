from __future__ import annotations

from dataclasses import dataclass
from functools import reduce, total_ordering
from typing import Sequence


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
    """A set of hexes represented as an ordered sequence of Hex."""

    hexes: Sequence[Hex]

    def translate(self, h: Hex) -> Shape:
        """Return a new Shape with all hexes translated by h."""
        return Shape([n + h for n in self.hexes])

    def rotate(self, steps: int = 1) -> Shape:
        """Return clockwise rotation of this shape (not normalized.)"""
        return Shape([h.rotate(steps) for h in self.hexes])

    def normalize_translation(self) -> Shape:
        """Return the same Shape in translationally normal form.

        In translationally normal form, hexes are ordered by (q, r, s) tuple and shape
        is translated such that first hex is (0, 0, 0).

        """
        hexes = sorted(self.hexes)
        if not hexes:
            return self
        n = hexes[0]
        s = Shape(hexes)
        if n.is_origin():
            return s
        return s.translate(-n)

    def sum(self) -> Hex:
        """Return the vector sum of all hexes in this shape."""
        return reduce(lambda a, b: a + b, self.hexes, Hex(0, 0, 0))

    def normalize_rotation(self) -> Shape:
        """Return the same Shape in rotationally normal form.

        This is the rotated form which maximizes the sum of the q components of all
        hexes in the shape (if tied, maximize r components next.)

        """
        # Rather than rotating the entire shape all the way around and re-summing each
        # version of it, we rely on the fact that the sum of a rotated shape is the same
        # as the rotated sum, so we can just find the best orientation for the single
        # sum vector, and then rotate the entire shape the right amount.
        cur_sum = self.sum()
        best_sum = cur_sum
        rotations = 0
        for i in range(5):
            cur_sum = cur_sum.rotate()
            if cur_sum > best_sum:
                best_sum = cur_sum
                rotations = i + 1
        if rotations:
            return self.rotate(rotations)
        return self

    def normalize(self) -> Shape:
        """Return same shape in translationally and rotationally normal form."""
        return self.normalize_rotation().normalize_translation()
