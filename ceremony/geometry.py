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
        x, y, z = self.x, self.y, self.z
        if steps % 2:
            x, y, z = -x, -y, -z
        if steps == 1 or steps == 4:
            x, y, z = z, x, y
        elif steps == 2 or steps == 5:
            x, y, z = y, z, x
        return Hex(x, y, z)


@dataclass(frozen=True)
class Shape:
    """A set of hexes represented as an ordered sequence of Hex."""

    nodes: Sequence[Hex]

    def translate(self, h: Hex) -> Shape:
        """Return a new Shape with all nodes translated by h."""
        return Shape([n + h for n in self.nodes])

    def rotate(self, steps: int = 1) -> Shape:
        """Return clockwise rotation of this shape (not normalized.)"""
        return Shape([h.rotate(steps) for h in self.nodes])

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
