from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
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


@dataclass(frozen=True)
class Shape:
    """A set of hexes represented as an ordered sequence of Hex."""

    nodes: Sequence[Hex]

    def translate(self, h: Hex) -> Shape:
        """Return a new Shape with all nodes translated by h."""
        return Shape([n + h for n in self.nodes])

    def normalize(self) -> Shape:
        """Return the same Shape in normal form.

        In normal form, hexes are ordered by (x, y, z) tuple and shape is translated
        such that first hex is (0, 0, 0).

        This means that translationally-equivalent shapes will always be identical in
        normal form.

        """
        nodes = sorted(self.nodes)
        if not nodes:
            return self
        n = nodes[0]
        s = Shape(nodes)
        if n.is_origin():
            return s
        return s.translate(-n)
