import pytest
from typing import Sequence

from ceremony.geometry import Hex, InvalidHexError, Shape


OR = Hex(0, 0, 0)
UP = Hex(0, 1, -1)
UR = UP.rotate()
DR = UR.rotate()
DN = DR.rotate()
DL = DN.rotate()
UL = DL.rotate()


class TestHex:
    @pytest.mark.parametrize(
        "x,y,z",
        [
            (0, 0, 0),
            (1, 0, -1),
        ],
    )
    def test_valid(self, x: int, y: int, z: int) -> None:
        h = Hex(x, y, z)
        assert h.x == x
        assert h.y == y
        assert h.z == z

    @pytest.mark.parametrize(
        "x,y,z",
        [
            (1, 0, 0),
        ],
    )
    def test_invalid(self, x: int, y: int, z: int) -> None:
        with pytest.raises(InvalidHexError):
            Hex(x, y, z)

    @pytest.mark.parametrize(
        "ins,outs",
        [
            ([], []),
            (
                [Hex(1, 0, -1), Hex(1, -1, 0), Hex(-1, 0, 1)],
                [Hex(-1, 0, 1), Hex(1, -1, 0), Hex(1, 0, -1)],
            ),
        ],
    )
    def test_sort(self, ins: Sequence[Hex], outs: Sequence[Hex]) -> None:
        assert sorted(ins) == outs

    @pytest.mark.parametrize(
        "inh,addh,outh",
        [
            (Hex(0, 0, 0), Hex(0, 0, 0), Hex(0, 0, 0)),
            (Hex(1, 0, -1), Hex(0, 2, -2), Hex(1, 2, -3)),
            (Hex(1, 0, -1), Hex(-1, 0, 1), Hex(0, 0, 0)),
        ],
    )
    def test_add(self, inh: Hex, addh: Hex, outh: Hex) -> None:
        assert inh + addh == outh

    @pytest.mark.parametrize(
        "inh,subh,outh",
        [
            (Hex(0, 0, 0), Hex(0, 0, 0), Hex(0, 0, 0)),
            (Hex(1, 0, -1), Hex(0, 2, -2), Hex(1, -2, 1)),
            (Hex(1, 0, -1), Hex(-1, 0, 1), Hex(2, 0, -2)),
        ],
    )
    def test_sub(self, inh: Hex, subh: Hex, outh: Hex) -> None:
        assert inh - subh == outh

    @pytest.mark.parametrize(
        "inh,outh",
        [(Hex(0, 0, 0), Hex(0, 0, 0)), (Hex(1, 0, -1), Hex(-1, 0, 1))],
    )
    def test_neg(self, inh: Hex, outh: Hex) -> None:
        assert -inh == outh

    @pytest.mark.parametrize(
        "inh,times,outh",
        [
            (Hex(0, 0, 0), 1, Hex(0, 0, 0)),
            (Hex(1, 0, -1), 1, Hex(1, -1, 0)),
            (Hex(1, -1, 0), 1, Hex(0, -1, 1)),
            (Hex(1, 2, -3), 1, Hex(3, -1, -2)),
            (UP, 1, UR),
            (UR, 1, DR),
            (DR, 1, DN),
            (DN, 1, DL),
            (DL, 1, UL),
            (UL, 1, UP),
            (UP, 2, DR),
            (DR, 3, UL),
            (DN, 6, DN),
        ],
    )
    def test_rotate(self, inh: Hex, times: int, outh: Hex) -> None:
        assert inh.rotate(times) == outh

    def test_conveniences(self) -> None:
        assert OR == Hex(0, 0, 0)
        assert UP == Hex(0, 1, -1)
        assert UR == Hex(1, 0, -1)
        assert DR == Hex(1, -1, 0)
        assert DN == Hex(0, -1, 1)
        assert DL == Hex(-1, 0, 1)
        assert UL == Hex(-1, 1, 0)


class TestShape:
    @pytest.mark.parametrize(
        "ins,diff,outs",
        [
            (Shape([]), Hex(0, 0, 0), Shape([])),
            (Shape([Hex(1, 0, -1)]), Hex(0, 1, -1), Shape([Hex(1, 1, -2)])),
        ],
    )
    def test_translate(self, ins: Shape, diff: Hex, outs: Shape) -> None:
        assert ins.translate(diff) == outs

    @pytest.mark.parametrize(
        "ins,outs",
        [
            (Shape([]), Shape([])),
            (Shape([Hex(1, 1, -2)]), Shape([Hex(0, 0, 0)])),
            (
                Shape([Hex(1, 2, -3), Hex(-3, 2, 1)]),
                Shape([Hex(0, 0, 0), Hex(4, 0, -4)]),
            ),
        ],
    )
    def test_normalize_translation(self, ins: Shape, outs: Shape) -> None:
        assert ins.normalize_translation() == outs

    @pytest.mark.parametrize(
        "ins,outs",
        [
            (Shape([]), Shape([])),
            (
                Shape([Hex(0, 0, 0), Hex(0, -1, 1)]),
                Shape([Hex(0, 0, 0), Hex(1, 0, -1)]),
            ),
        ],
    )
    def test_normalize_rotation(self, ins: Shape, outs: Shape) -> None:
        assert ins.normalize_rotation() == outs

    @pytest.mark.parametrize(
        "ins,outs",
        [
            (Shape([]), Shape([])),
            (
                Shape([Hex(0, -1, 1), Hex(0, -2, 2), Hex(-1, -2, 3)]),
                Shape([Hex(0, 0, 0), Hex(1, 0, -1), Hex(2, -1, -1)]),
            ),
            (
                Shape([OR, DR, DR + UR, DR + UR + UR]),
                Shape([OR, DR, DR + UR, DR + UR + UR]),
            ),
            (
                Shape([OR, UP, UP + UR, UP + UR + UR]),
                Shape([OR, UR, UR + DR, UR + DR + DR]),
            ),
        ],
    )
    def test_normalize(self, ins: Shape, outs: Shape) -> None:
        assert ins.normalize() == outs
