import pytest
from typing import Sequence

from ceremony.geometry import Shape, OR, UP, UR, DR
from ceremony.generate import extensions


class TestExtensions:
    @pytest.mark.parametrize(
        "ins,exts",
        [
            (
                Shape((OR,)),
                [
                    Shape((OR, UR)),
                ],
            ),
            (
                Shape((OR, UP)),
                [
                    Shape((OR, DR, UR)),
                    Shape((OR, UP, DR)),
                    Shape((OR, UP, UP + UP)),
                    Shape((OR, UR, UR + DR)),
                    Shape((OR, DR, DR + UR)),
                ],
            ),
        ],
    )
    def test_extensions(self, ins: Shape, exts: Sequence[Shape]) -> None:
        assert list(extensions(ins)) == exts
