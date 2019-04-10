import cairo
import numpy as np

from abc import ABC, abstractmethod
#from dataclasses import dataclass
#from math import cos, sin, radians


class Vetor2D(np.ndarray):
    def __new__(cls, x: float = 0, y: float = 0):
        objeto = np.asarray([x, y, 1], dtype=float).view(cls)
        return objeto

    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

class GraphicObject(ABC):
    def __init__(self, name=''):
        super().__init__()
        self.name = name

    @abstractmethod
    def draw(self, cr: cairo.Context, transform):
        pass

    @abstractmethod
    def transform(self, matrix: np.ndarray):
        pass


class Point(GraphicObject):
    def __init__(self, position: Vetor2D, name=''):
        super().__init__(name)
        self.position = position

    @property
    def x(self) -> float:
        return self.position[0]

    @property
    def y(self) -> float:
        return self.position[1]

    def draw(self, cr: cairo.Context, transform=lambda v: v):
        coord_viewport = transform(Vetor2D(self.x, self.y))
        cr.move_to(coord_viewport.x, coord_viewport.y)
        cr.arc(coord_viewport.x, coord_viewport.y, 1, 0, 2 * np.pi)
        cr.fill()

    def transform(self, matrix: np.ndarray):
        self.position = matrix @ self.position

class Line(GraphicObject):
    def __init__(self, inicio: Vetor2D, fim: Vetor2D, name=''):
        super().__init__(name)
        self.pontos =  np.array([inicio, fim], dtype=float)

    @property
    def x1(self):
        return self.pontos[0, 0]

    @property
    def y1(self):
        return self.pontos[0, 1]

    @property
    def x2(self):
        return self.pontos[1, 0]

    @property
    def y2(self):
        return self.pontos[1, 1]

    def draw(self, cr: cairo.Context, transform=lambda v: v):
        coord_viewport1 = transform(Vetor2D(self.x1, self.y1))
        coord_viewport2 = transform(Vetor2D(self.x2, self.y2))
        cr.move_to(coord_viewport1.x, coord_viewport1.y)
        cr.line_to(coord_viewport2.x, coord_viewport2.y)
        cr.stroke()

    def transform(self, matrix: np.ndarray):
        self.pontos[0] = matrix @ self.pontos[0]
        self.pontos[1] = matrix @ self.pontos[1]

