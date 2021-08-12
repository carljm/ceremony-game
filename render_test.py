from ceremony.generate import extensions
from ceremony.geometry import Shape, OR, UR
from ceremony.render import render_shapes


def main() -> None:
    shapes = set()
    shapes.add(Shape.of(OR, UR))
    last = shapes

    for i in range(3):
        new = set()
        for shape in last:
            for ext in extensions(shape):
                new.add(ext)
        shapes.update(new)
        last = new

    render_shapes(last, "example.png")


if __name__ == "__main__":
    main()
