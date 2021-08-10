from ceremony.geometry import Shape, OR, UP, UR, DR, DN, DL, UL
from ceremony.render import render_shapes

s1 = Shape(
    [
        OR,
        UP,
        UP + UR,
        UP + UR + DR,
        UP + UR + DR + DN,
        UP + UR + DR + DN + DL,
        UP + UL,
        UP + UL + DL,
        UP + UL + DL + DL,
    ]
).normalize()
s2 = Shape(
    [
        OR,
        UP,
        UR,
        UR + UR,
        UR + UR + UP,
        UR + UR + UP + UL,
        UR + UR + DN,
        UR + UR + DN + DN,
        DN,
    ]
)
render_shapes([s1, s2], "example.png")
