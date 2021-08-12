from __future__ import annotations

import cairo
import math
from dataclasses import dataclass
from typing import Sequence, Tuple


from .geometry import Hex, Shape as HexShape


def render_shapes(hex_shapes: Sequence[HexShape], filename: str) -> None:
    shapes = [Shape.from_hex_shape(hs) for hs in hex_shapes]
    # stack shapes one below the other
    translated_shapes = []
    offset = ORIGIN
    minx = maxx = miny = maxy = None
    for shape in shapes:
        box = shape.bounding_box()
        if miny is not None:
            offset = offset + Point(0.0, maxy - box[0].y + 4.0)
        shape = shape.translate(offset)
        translated_shapes.append(shape)
        box = shape.bounding_box()
        minx = min(minx if minx is not None else box[0].x, box[0].x)
        maxx = max(maxx if maxx is not None else box[1].x, box[1].x)
        miny = min(miny if miny is not None else box[0].y, box[0].y)
        maxy = max(maxy if maxy is not None else box[1].y, box[1].y)
    # translate everything again so that (3.0, 3.0) is upper left of overall box
    if miny is None or maxy is None or minx is None or maxx is None:
        # No shapes to render!
        return
    offset = Point(3.0 - minx, 3.0 - miny)
    translated_shapes = [s.translate(offset) for s in translated_shapes]
    width = round((maxx + offset.x + 3.0) * 20)
    height = round((maxy + offset.y + 3.0) * 20)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.scale(20, 20)
    ctx.rectangle(0, 0, width, height)
    ctx.set_source_rgb(0.0, 0.0, 0.0)
    ctx.fill()
    for shape in translated_shapes:
        draw_shape(shape, ctx)
    surface.write_to_png(filename)


@dataclass(frozen=True)
class Orientation:
    """
    An "orientation" of hexes to render on screen.

    There are really only two relevant ones, "flat-top" and "pointy-top", and we only
    use flat-top.

    This currently has only the forward matrix, not inverse or start_angle, since we
    only go from hex to pixel, not the reverse.

    """

    forward: Tuple[float, float, float, float]


FLAT = Orientation((3.0 / 2.0, 0.0, math.sqrt(3.0) / 2.0, math.sqrt(3.0)))


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __add__(self, p: Point) -> Point:
        return Point(self.x + p.x, self.y + p.y)

    def __mul__(self, factor: float) -> Point:
        return Point(self.x * factor, self.y * factor)


ORIGIN = Point(0.0, 0.0)
UNIT = Point(1.0, 1.0)


@dataclass(frozen=True)
class Shape:
    """A shape made up of a series of cartesian Points."""

    points: Sequence[Point]

    @classmethod
    def from_hex_shape(cls, hs: HexShape) -> Shape:
        return Shape([LAYOUT.hex_to_point(h) for h in sorted(hs.hexes)]).scale(
            1 / hs._scale
        )

    def bounding_box(self) -> Tuple[Point, Point]:
        if not self.points:
            return ORIGIN, ORIGIN
        xs = sorted(p.x for p in self.points)
        ys = sorted(p.y for p in self.points)
        return (Point(xs[0], ys[0]), Point(xs[-1], ys[-1]))

    def translate(self, vec: Point) -> Shape:
        return Shape([p + vec for p in self.points])

    def scale(self, factor: float) -> Shape:
        return Shape([p * factor for p in self.points])


@dataclass(frozen=True)
class Layout:
    """A layout of cube-coordinate hexes on a 2d x/y screen."""

    orientation: Orientation
    size: Point
    origin: Point

    def hex_to_point(self, h: Hex) -> Point:
        f = self.orientation.forward
        x = (f[0] * h.q + f[1] * h.r) * self.size.x
        y = (f[2] * h.q + f[3] * h.r) * self.size.y
        return Point(x + self.origin.x, y + self.origin.y)


LAYOUT = Layout(FLAT, UNIT, ORIGIN)


def draw_shape(shape: Shape, ctx: cairo.Context) -> None:
    for point in shape.points:
        ctx.arc(point.x, point.y, 0.5, 0.0, 2 * math.pi)
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.fill()
