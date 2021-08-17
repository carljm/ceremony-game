import math

import pytest

from ceremony.geometry import Hex, Shape as HexShape
from ceremony.render import Point, Shape


class TestPoint:
    def test_add(self) -> None:
        assert Point(1.0, 2.0) + Point(3.1, 1.2) == Point(4.1, 3.2)

    def test_mul(self) -> None:
        assert Point(1.0, 2.0) * 2 == Point(2.0, 4.0)


class TestShape:
    @pytest.mark.parametrize(
        "hexshape,shape",
        [
            (HexShape.of(Hex(0, 0, 0)), Shape([Point(0.0, 0.0)])),
            (
                HexShape.of(Hex(0, 1, -1), Hex(1, 0, -1)),
                Shape([Point(0.0, 0.0), Point(0.0, math.sqrt(3.0))]),
            ),
        ],
    )
    def test_from_hex_shape(self, hexshape: HexShape, shape: Shape) -> None:
        assert Shape.from_hex_shape(hexshape) == shape

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

    def test_scale(self) -> None:
        s1 = Shape([Point(0.0, 1.0), Point(1.0, 3.0)])
        s2 = s1.scale(0.5)
        assert s2 == Shape([Point(0.0, 0.5), Point(0.5, 1.5)])
