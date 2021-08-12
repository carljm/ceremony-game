import pytest
from typing import Sequence, Tuple

from ceremony.geometry import Hex, InvalidHexError, Shape, OR, UP, UR, DR, DN, DL, UL
from .factory import shape


class TestHex:
    @pytest.mark.parametrize(
        "q,r,s",
        [
            (0, 0, 0),
            (1, 0, -1),
        ],
    )
    def test_valid(self, q: int, r: int, s: int) -> None:
        h = Hex(q, r, s)
        assert h.q == q
        assert h.r == r
        assert h.s == s

    @pytest.mark.parametrize(
        "q,r,s",
        [
            (1, 0, 0),
        ],
    )
    def test_invalid(self, q: int, r: int, s: int) -> None:
        with pytest.raises(InvalidHexError):
            Hex(q, r, s)

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
        "inh,mul,outh",
        [
            (Hex(0, 0, 0), 2, Hex(0, 0, 0)),
            (Hex(1, 0, -1), 0, Hex(0, 0, 0)),
            (Hex(1, 0, -1), 1, Hex(1, 0, -1)),
            (Hex(1, 1, -2), 2, Hex(2, 2, -4)),
        ],
    )
    def test_mul(self, inh: Hex, mul: int, outh: Hex) -> None:
        assert inh * mul == outh

    @pytest.mark.parametrize(
        "inh,div,outh",
        [
            (Hex(0, 0, 0), 2, Hex(0, 0, 0)),
            (Hex(1, 0, -1), 1, Hex(1, 0, -1)),
            (Hex(2, 2, -4), 2, Hex(1, 1, -2)),
        ],
    )
    def test_floordiv(self, inh: Hex, div: int, outh: Hex) -> None:
        assert inh // div == outh

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

    @pytest.mark.parametrize("h,ring", [(OR, 0), (UP, 1), (DN + DL, 2)])
    def test_ring(self, h: Hex, ring: int) -> None:
        assert h.ring() == ring

    @pytest.mark.parametrize(
        "h,ring_index",
        [
            (OR, 0),
            (UP, 0),
            (UR, 1),
            (DR, 2),
            (DN, 3),
            (DL, 4),
            (UL, 5),
            (UP + UP, 0),
            (UP + UR, 1),
            (UR + UR, 2),
            (UR + DR, 3),
            (DR + DR, 4),
            (DN + DR, 5),
            (DN + DN, 6),
            (DN + DL, 7),
            (DL + DL, 8),
            (DL + UL, 9),
            (UL + UL, 10),
            (UL + UP, 11),
        ],
    )
    def test_ring_index(self, h: Hex, ring_index: int) -> None:
        assert h.ring_index() == ring_index


class TestShape:
    @pytest.mark.parametrize(
        "ins,diff,outs",
        [
            (shape(), Hex(0, 0, 0), shape()),
            (shape(Hex(1, 0, -1)), Hex(0, 1, -1), shape(Hex(1, 1, -2))),
        ],
    )
    def test_translate(self, ins: Shape, diff: Hex, outs: Shape) -> None:
        assert ins.translate(diff) == outs

    @pytest.mark.parametrize(
        "ins,outs",
        [
            (shape(), shape()),
            (shape(Hex(1, 1, -2)), shape(Hex(0, 0, 0))),
            (
                shape(Hex(1, 2, -3), Hex(-3, 2, 1)),
                shape(Hex(4, 0, -4), Hex(-4, 0, 4), _scale=2),
            ),
        ],
    )
    def test_normalize_translation(self, ins: Shape, outs: Shape) -> None:
        assert ins.normalize_translation() == outs

    @pytest.mark.parametrize(
        "ins,outs",
        [
            (shape(), shape()),
            (
                shape(Hex(0, -1, 1), Hex(0, -2, 2), Hex(-1, -2, 3)),
                shape(Hex(-3, 1, 2), Hex(0, 1, -1), Hex(3, -2, -1), _scale=3),
            ),
            (
                shape(OR, DR, DR + UR, DR + UR + UR),
                shape(
                    Hex(q=1, r=1, s=-2),
                    Hex(q=-3, r=-3, s=6),
                    Hex(q=1, r=-3, s=2),
                    Hex(q=1, r=5, s=-6),
                    _scale=4,
                ),
            ),
            (
                shape(OR, UP, UP + UR, UP + UR + UR),
                shape(
                    Hex(q=1, r=1, s=-2),
                    Hex(q=-3, r=-3, s=6),
                    Hex(q=-3, r=1, s=2),
                    Hex(q=5, r=1, s=-6),
                    _scale=4,
                ),
            ),
        ],
    )
    def test_normalize(self, ins: Shape, outs: Shape) -> None:
        assert ins.normalize() == outs

    @pytest.mark.parametrize(
        "s,sums",
        [
            (shape(), (0, 0, 0)),
            (shape(OR), (1, 0, 0)),
            (shape(OR, UP), (1, 1, 0)),
            (shape(OR, DN), (1, 8, 0)),
            (shape(DN, UP), (0, 9, 0)),
            (shape(DN + DN, DR, DL, UP + UR), (0, 20, 66)),
        ],
    )
    def test_ring_sum(self, s: Shape, sums: Tuple[int, ...]) -> None:
        assert (s.ring_sum(0), s.ring_sum(1), s.ring_sum(2)) == sums
