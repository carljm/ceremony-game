from __future__ import annotations

from typing import Dict, Iterator, List, Tuple

from ceremony.geometry import Hex, Shape, OR


class ShapeSet:
    """
    A collection of unique normalized shapes.

    Uses a tree internally to more efficiently detect duplicates.

    """

    shapes: List[Shape]
    tree: Node

    def __init__(self) -> None:
        self.shapes = []
        # All normalized shapes' first hex is origin so we can root the tree there
        self.tree = Node(OR)

    def add(self, shape: Shape) -> bool:
        """Add `shape` to the set or return False if it's already there."""
        if not shape.hexes:
            return False
        s = shape.normalize()
        node = self.tree
        dupe = True
        assert s.hexes[0] == node.value
        for h in s.hexes[1:]:
            node, added = node.add_child(h)
            dupe = dupe and not added
        dupe = dupe and node.terminal
        node.terminal = True
        if not dupe:
            self.shapes.append(s)
            return True
        return False

    def __iter__(self) -> Iterator[Shape]:
        return iter(self.shapes)


class Node:
    value: Hex
    children: Dict[Hex, Node]
    # a member shape ends with this hex (there may be others that pass through it)
    terminal: bool = False

    def __init__(self, value: Hex) -> None:
        self.value = value
        self.children = {}
        self.terminal = False

    def add_child(self, h: Hex) -> Tuple[Node, bool]:
        """Add h as a child if not present; return its node and whether added."""
        node = self.children.get(h, None)
        added = False
        if node is None:
            node = self.children[h] = Node(h)
            added = True
        return node, added
