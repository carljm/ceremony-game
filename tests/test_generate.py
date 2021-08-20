import pytest
from typing import Sequence

from ceremony.geometry import Shape, OR, UP, UR, DR, DN, DL, UL
from ceremony.generate import (
    extensions,
    generate_all,
    generate_diff_by_2,
    max_length,
    longest_line,
)


class TestGenerate:
    def test_generate_all(self) -> None:
        shapes = generate_all(3)
        assert shapes == {
            Shape.of(DN, OR, UP),
            Shape.of(OR, UP, UR),
            Shape.of(DN, OR, UR),
        }

    def test_too_long(self) -> None:
        shapes = generate_all(6)
        assert Shape.of(DN + DN, DN, OR, UP, UP + UR, UP + UR + UP) not in shapes

    def test_line_too_long(self) -> None:
        shapes = generate_all(5)
        assert Shape.of(DN + DN, DN, OR, UP, UP + UP) not in shapes

    def test_generate_diff_by_2(self) -> None:
        shapes = generate_diff_by_2(generate_all(4))

        assert shapes == {
            Shape.of(UR, OR, UR + DR, UR + DR + DR, UR + DR + DR + DR),
            Shape.of(UR, OR, UR + UR, UR + UR + DR, UR + UR + DR + UR),
            Shape.of(UR, DR, OR, UR + DR, UR + UP),
        }

    @pytest.mark.parametrize(
        "ins,exts",
        [
            (Shape.of(), []),
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

    @pytest.mark.parametrize(
        "shape,longest",
        [
            (Shape.of(OR), 1),
            (Shape.of(OR, UP), 2),
            (Shape.of(OR, UP, DN), 3),
            (Shape.of(OR, UP, DN, DN + DR), 3),
            (Shape.of(OR, UP, DN, DN + DR, DL, DL + UL), 4),
            (Shape.of(OR, UP, DN, DN + DR, UL, DL + UL), 3),
        ],
    )
    def test_longest_line(self, shape: Shape, longest: int) -> None:
        assert longest_line(shape) == longest
