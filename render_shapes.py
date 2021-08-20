import sys

from ceremony.generate import generate
from ceremony.render import render_shapes


def main(nodes: int) -> None:
    shapes = generate(nodes)
    print(f"Rendering {len(shapes)} unique {nodes}-node constellations.")
    render_shapes(shapes, "example.png")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        nodes = int(sys.argv[1])
    else:
        nodes = 3
    main(nodes)
