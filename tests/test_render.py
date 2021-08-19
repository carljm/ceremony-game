import math
from typing import Sequence

import pytest

from ceremony.geometry import Hex, Shape as HexShape, OR, UP
from ceremony.render import Point, Shape, layout_shapes


class TestLayoutShapes:
    @pytest.mark.parametrize(
        "shapes,translated,width,height",
        [
            ([], [], 0, 0),
            ([HexShape.of(OR)], [Shape([Point(3.0, 3.0)])], 60, 60),
            (
                [HexShape.of(OR, UP)],
                [Shape([Point(3.0, 3.0), Point(3.0, 3.0 + math.sqrt(3.0))])],
                60,
                77,
            ),
            (
                [HexShape.of(OR, UP), HexShape.of(OR)],
                [
                    Shape([Point(3.0, 3.0), Point(3.0, 3.0 + math.sqrt(3.0))]),
                    Shape([Point(6.0, 3.0)]),
                ],
                90,
                77,
            ),
            (
                [HexShape.of(OR)] * 21,
                [Shape([Point(3.0 * (x + 1), 3.0)]) for x in range(20)]
                + [Shape([Point(3.0, 6.0)])],
                630,
                90,
            ),
        ],
    )
    def test_layout_shapes(
        self,
        shapes: Sequence[HexShape],
        translated: Sequence[Shape],
        width: int,
        height: int,
    ) -> None:
        assert layout_shapes(shapes) == (translated, width, height)


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
