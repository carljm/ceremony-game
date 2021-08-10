from typing import Sequence, Tuple

import pytest

from ceremony.collection import ShapeSet
from ceremony.geometry import Shape, OR, UP, UL, DL, DN, DR, UR


class TestShapeSet:
    @pytest.mark.parametrize(
        "shapes",
        [
            [(Shape([]), True)],
            [(Shape([OR]), False)],
            [(Shape([UP, UP + UR]), False), (Shape([UP, UP + UR]), True)],
            [(Shape([DR, DR + DN]), False), (Shape([DL, DL + UL]), True)],
            [
                (Shape([DR, DR + DN, DR + DN + DN]), False),
                (Shape([DR, DR + DN]), False),
                (Shape([DR, DR + DN]), True),
            ],
        ],
    )
    def test_add(self, shapes: Sequence[Tuple[Shape, bool]]) -> None:
        ss = ShapeSet()
        for shape, dupe in shapes:
            added = ss.add(shape)
            assert added == (not dupe)
