from ceremony.generate import extensions
from ceremony.geometry import Shape, OR, UR
from ceremony.render import render_shapes


def main():
    shapes = set()
    shapes.add(Shape.of((OR, UR)))

    for i in range(2, 4):
        for shape in shapes:
            if len(shape.hexes) != i:
                continue
            for ext in extensions(shape):
                shapes.add(ext)

    render_shapes([s for s in shapes if len(s.hexes) == 3], "example.png")


if __name__ == "__main__":
    main()