import sys

from ceremony.generate import generate_all, generate_diff_by_2
from ceremony.render import render_shapes


def main(nodes: int) -> None:
    base_shapes = list(generate_all(nodes - 1))
    print(f"Generated {len(base_shapes)} unique {nodes-1}-node constellations.")
    shapes = generate_diff_by_2(base_shapes)
    print(f"Rendering {len(shapes)} unique {nodes}-node constellations.")
    render_shapes(shapes, "example.png")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        nodes = int(sys.argv[1])
    else:
        nodes = 3
    main(nodes)
