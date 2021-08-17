from ceremony import geometry


def shape(*h: geometry.Hex) -> geometry.Shape:
    return geometry.Shape(frozenset(h))
