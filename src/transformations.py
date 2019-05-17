import numpy as np
from math import cos, sin, radians

def rotation_matrix(angle: float) -> np.ndarray:
    angle = radians(angle)
    return np.array(
        [
            cos(angle), -sin(angle),    0.0,
            sin(angle), cos(angle),     0.0,
            0.0,               0.0,     1.0
        ],
        dtype=float
    ).reshape(3, 3)

def translate_matrix(dx: float, dy: float) -> np.ndarray:
    return np.array(
        [
            1.0,  0.0,  0.0,
            0.0,  1.0,  0.0,
            dx,   dy,   1.0
        ],
        dtype=float
    ).reshape(3, 3)

def scale_matrix(sx: float, sy: float) -> np.ndarray:
    return np.array(
        [
            sx, 0, 0,
            0, sy, 0,
            0, 0, 1,
        ],
        dtype=float
    ).reshape(3, 3)

def viewport_matrix(viewport: 'Rectangle') -> np.ndarray:
    return (
        scale_matrix(viewport.width / 2, -viewport.height / 2)
        @ translate_matrix(viewport.centroid.x, viewport.centroid.y)
    )

def normalized_matrix(window: 'Window') -> np.ndarray:
    return (
        translate_matrix(-window.centroid.x, -window.centroid.y)
        @ rotation_matrix(-window.angle)
        @ scale_matrix(2 / window.width, 2 / window.height)
    )
