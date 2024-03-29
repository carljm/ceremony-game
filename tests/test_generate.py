import pytest
import random
from typing import Collection

from ceremony.geometry import Shape, OR, UP, UR, DR, DN, DL, UL
from ceremony.generate import (
    extensions,
    generate,
    generate_all,
    max_length,
    longest_line,
    num_triangles,
)


class TestGenerate:
    def test_generate(self) -> None:
        random.seed(1)
        shapes = generate()
        assert len(shapes) == 94

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

    @pytest.mark.parametrize(
        "ins,exts",
        [
            (Shape.of(), set()),
            (
                Shape.of(OR),
                {
                    Shape.of(OR, UR),
                },
            ),
            (
                Shape.of(OR, UP),
                {
                    Shape.of(OR, UP, UR),
                    Shape.of(OR, UP, DR),
                    Shape.of(OR, UP, DN),
                },
            ),
        ],
    )
    def test_extensions(self, ins: Shape, exts: Collection[Shape]) -> None:
        assert set(extensions(ins)) == exts


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

    @pytest.mark.parametrize(
        "shape,num_tri",
        [
            (Shape.of(OR), 0),
            (Shape.of(OR, UP), 0),
            (Shape.of(OR, UP, DN), 0),
            (Shape.of(OR, UP, UR), 1),
            (Shape.of(OR, UP, UL), 1),
            (Shape.of(OR, UP, DN, DL), 1),
            (Shape.of(OR, UP, UL, UR), 2),
            (Shape.of(OR, UP, UL, UR, UP + UR), 3),
            (Shape.of(OR, UP, UR, DR, DN, DL, UL), 6),
        ],
    )
    def test_num_triangles(self, shape: Shape, num_tri: int) -> None:
        assert num_triangles(shape) == num_tri
