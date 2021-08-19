from __future__ import annotations

import cairo
import math
from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple


from .geometry import Hex, Shape as HexShape


# Scaling factor between user coordinates (Shape Point x,y) and pixel coordinates.
# Larger number will result in larger rendered shapes.
SCALE = 10

# Padding around rendered shapes, in user coordinates
PAD = 3.0

# Number of shapes rendered in each row of grid
GRID_WIDTH = 20


def render_shapes(hex_shapes: Iterable[HexShape], filename: str) -> None:
    """Render given hex shapes to given PNG filename."""
    shapes, width, height = layout_shapes(hex_shapes)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.scale(SCALE, SCALE)
    ctx.rectangle(0, 0, width, height)
    ctx.set_source_rgb(0.0, 0.0, 0.0)
    ctx.fill()
    for shape in shapes:
        draw_shape(shape, ctx)
    surface.write_to_png(filename)


def layout_shapes(hex_shapes: Iterable[HexShape]) -> Tuple[Sequence[Shape], int, int]:
    """Layout hex shapes as non-overlapping cartesian shapes for rendering.

    Will be laid out entirely in +x, +y quadrant, with some empty padding.

    Return (shapes, width, height), where width and height are the width and height of
    overall needed canvas, scaled to pixel coordinates.

    """
    if not hex_shapes:
        return [], 0, 0
    shapes = [Shape.from_hex_shape(hs) for hs in hex_shapes]
    boxes = [s.bounding_box() for s in shapes]
    max_width = max(b[1].x - b[0].x for b in boxes)
    max_height = max(b[1].y - b[0].y for b in boxes)
    padded_w = max_width + PAD
    padded_h = max_height + PAD
    # lay out shapes in a grid
    translated_shapes = []
    grid_x = 0
    grid_y = 0
    for s, b in zip(shapes, boxes):
        width = b[1].x - b[0].x
        x_offset = (PAD + (padded_w * grid_x)) - b[0].x + ((max_width - width) / 2.0)
        y_offset = (PAD + (padded_h * grid_y)) - b[0].y
        translated_shapes.append(s.translate(Point(x_offset, y_offset)))
        grid_x += 1
        if grid_x >= GRID_WIDTH:
            grid_x = 0
            grid_y += 1
    max_grid_y = grid_y + (1 if grid_x else 0)
    max_grid_x = GRID_WIDTH if grid_y else grid_x
    width = round((PAD + (max_grid_x * padded_w)) * SCALE)
    height = round((PAD + (max_grid_y * padded_h)) * SCALE)
    return translated_shapes, width, height


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
        return Shape([LAYOUT.hex_to_point(h) for h in sorted(hs.hexes)])

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
    """A layout of cube-coordinate hexes on a cartesian plane."""

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
