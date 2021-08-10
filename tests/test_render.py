import math

import pytest

from ceremony.geometry import Hex, Shape as HexShape
from ceremony.render import Point, Shape


class TestPoint:
    def test_add(self) -> None:
        assert Point(1.0, 2.0) + Point(3.1, 1.2) == Point(4.1, 3.2)


class TestShape:
    def test_from_hex_shape(self) -> None:
        s = Shape.from_hex_shape(HexShape([Hex(1, 0, -1)]))
        assert s == Shape([Point(1.5, math.sqrt(3.0) / 2.0)])

    @pytest.mark.parametrize(
        "shape,box",
        [
            (Shape([]), (Point(0.0, 0.0), Point(0.0, 0.0))),
            (Shape([Point(1.0, 2.0)]), (Point(1.0, 2.0), Point(1.0, 2.0))),
            (
                Shape([Point(0.0, 3.0), Point(1.0, 2.0)]),
                (Point(0.0, 2.0), Point(1.0, 3.0)),
            ),
        ],
    )
    def test_bounding_box(self, shape, box) -> None:
        assert shape.bounding_box() == box

    def test_translate(self) -> None:
        s1 = Shape([Point(0.0, 1.0), Point(1.0, 3.0)])
        s2 = s1.translate(Point(1.0, -1.0))
        assert s2 == Shape([Point(1.0, 0.0), Point(2.0, 2.0)])
