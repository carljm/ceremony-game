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

    X, Y, and Z must always total to zero.

    See https://www.redblobgames.com/grids/hexagons/ for details.

    """

    x: int
    y: int
    z: int

    def __post_init__(self) -> None:
        if self.x + self.y + self.z != 0:
            raise InvalidHexError(f"{self.x} + {self.y} + {self.z} != 0")

    def __add__(self, h: Hex) -> Hex:
        return Hex(self.x + h.x, self.y + h.y, self.z + h.z)

    def __sub__(self, h: Hex) -> Hex:
        return self + (-h)

    def __neg__(self) -> Hex:
        return Hex(-self.x, -self.y, -self.z)

    def __lt__(self, h: Hex) -> bool:
        return (self.x, self.y, self.z) < (h.x, h.y, h.z)

    def is_origin(self) -> bool:
        return self.x == self.y == self.z == 0

    def rotate(self) -> Hex:
        """Return next clockwise rotation of this hex around origin."""
        return Hex(-self.z, -self.x, -self.y)


@dataclass(frozen=True)
class Shape:
    """A set of hexes represented as an ordered sequence of Hex."""

    nodes: Sequence[Hex]

    def translate(self, h: Hex) -> Shape:
        """Return a new Shape with all nodes translated by h."""
        return Shape([n + h for n in self.nodes])

    def rotate(self) -> Shape:
        """Return next clockwise rotation of this shape (not normalized.)"""
        return Shape([h.rotate() for h in self.nodes])

    def normalize_translation(self) -> Shape:
        """Return the same Shape in translationally normal form.

        In translationally normal form, hexes are ordered by (x, y, z) tuple and shape
        is translated such that first hex is (0, 0, 0).

        """
        nodes = sorted(self.nodes)
        if not nodes:
            return self
        n = nodes[0]
        s = Shape(nodes)
        if n.is_origin():
            return s
        return s.translate(-n)

    def sum(self) -> Hex:
        """Return the vector sum of all hexes in this shape."""
        return reduce(lambda a, b: a + b, self.nodes, Hex(0, 0, 0))

    def normalize_rotation(self) -> Shape:
        """Return the same Shape in rotationally normal form.

        This is the rotated form which maximizes the sum of the x components of all
        hexes in the shape (if tied, maximize y components next.)

        """
        cur = self
        best_rotation = cur
        best_sum = cur.sum()
        for i in range(5):
            cur_sum = cur.sum()
            if cur_sum > best_sum:
                best_sum = cur_sum
                best_rotation = cur
            cur = cur.rotate()
        return best_rotation

    def normalize(self) -> Shape:
        """Return same shape in translationally and rotationally normal form."""
        return self.normalize_rotation().normalize_translation()
