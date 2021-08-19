import pytest
from typing import Sequence

from ceremony.geometry import Shape, OR, UP, UR, DR, DN
from ceremony.generate import extensions, max_length


class TestExtensions:
    @pytest.mark.parametrize(
        "ins,exts",
        [
            (
                Shape.of(OR),
                [
                    Shape.of(OR, UR),
                ],
            ),
            (
                Shape.of(OR, UP),
                [
                    Shape.of(OR, UP, UR),
                    Shape.of(OR, UP, DR),
                    Shape.of(OR, UP, DN),
                ],
            ),
        ],
    )
    def test_extensions(self, ins: Shape, exts: Sequence[Shape]) -> None:
        assert list(extensions(ins)) == exts


class TestRules:
    @pytest.mark.parametrize(
        "shape,maxlen",
        [
            (Shape.of(OR), 0),
            (Shape.of(OR, UP), 2),
            (Shape.of(OR, UP, DN), 4),
            (Shape.of(OR, UP, DN, DN + DR), 5),
        ],
    )
    def test_max_length(self, shape: Shape, maxlen: int) -> None:
        assert max_length(shape) == maxlen
