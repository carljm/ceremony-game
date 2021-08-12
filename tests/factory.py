from ceremony import geometry


def shape(*h: geometry.Hex, _scale: int = 1) -> geometry.Shape:
    return geometry.Shape(frozenset(h), _scale)
