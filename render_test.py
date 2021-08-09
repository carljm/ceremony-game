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
    ]
).normalize()
render_shapes([s1], "example.png")
