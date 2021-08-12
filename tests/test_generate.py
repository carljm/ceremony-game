import pytest
from typing import Sequence

from ceremony.geometry import Shape, OR, UP, UR, DR, DN
from ceremony.generate import extensions


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
