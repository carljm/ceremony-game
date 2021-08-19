import sys

from ceremony.generate import extensions, max_length, longest_line
from ceremony.geometry import Shape, OR, UR
from ceremony.render import render_shapes


def main(nodes: int) -> None:
    shapes = set()
    shapes.add(Shape.of(OR, UR))
    last = shapes

    for i in range(nodes - 2):
        new = set()
        for shape in last:
            for ext in extensions(shape):
                if max_length(ext) <= 8 and 3 <= longest_line(ext) < 5:
                    new.add(ext)
        shapes.update(new)
        last = new

    print(f"Rendering {len(last)} unique {i+3}-node constellations.")
    render_shapes(last, "example.png")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        nodes = int(sys.argv[1])
    else:
        nodes = 3
    main(nodes)
