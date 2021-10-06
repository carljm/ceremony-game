from ceremony.generate import generate
from ceremony.render import render_shapes


def main() -> None:
    shapes = generate()
    print(f"Rendering {len(shapes)} constellations.")
    render_shapes(shapes, "example.png")


if __name__ == "__main__":
    main()
