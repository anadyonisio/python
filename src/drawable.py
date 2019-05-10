import cairo
import numpy as np

from abc import ABC, abstractmethod
from math import cos, sin, radians
from dataclasses import dataclass
from cairo import Context
from typing import List, Optional
from transformations import rotation_matrix, translate_matrix, scale_matrix



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

@dataclass
class Rectangle:
    min: Vetor2D
    max: Vetor2D

    @property
    def width(self) -> float:
        return self.max.x - self.min.x

    @property
    def height(self) -> float:
        return self.max.y - self.min.y

    def with_margin(self, margin: float) -> 'Rectangle':
        return Rectangle(
            self.min + Vetor2D(margin, margin),
            self.max - Vetor2D(margin, margin),
        )
    def offset(self, offset: Vetor2D):
        self.min += offset
        self.max += offset

    def rotate(self, angle: float):
        self.min = self.min @ rotation_matrix(angle)
        self.max = self.max @ rotation_matrix(angle)

    def zoom(self, amount: float):
        self.max *= amount
        self.min *= amount

    def center(self) -> Vetor2D:
        return (self.max + self.min) / 2


@dataclass
class Window(Rectangle):
    angle: float = 0.0


@dataclass
class Viewport:
    region: Rectangle
    window: Window

    @property
    def min(self) -> float:
        return self.region.min

    @property
    def max(self) -> float:
        return self.region.max

    @property
    def width(self) -> float:
        return self.region.width

    @property
    def height(self) -> float:
        return self.region.height

    def transform(self, p: Vetor2D) -> Vetor2D:
        if not isinstance(p, Vetor2D):
            p = Vetor2D(p[0], p[1])

        view_size = Vetor2D(self.max.x - self.min.x, self.max.y - self.min.y)

        win_size = Vetor2D(self.window.max.x - self.window.min.x,
                           self.window.max.y - self.window.min.y
                           )
        return Vetor2D((p.x - self.min.x) * view_size.x / win_size.x,
                       (p.y - self.min.y) * view_size.y / win_size.y
                       )

    def draw(self, cr: Context):
        _min = self.min
        _max = self.max

        cr.set_source_rgb(0.4, 0.4, 0.4)
        cr.move_to(_min.x, _min.y)
        for x, y in [
                (_max.x, _min.y),
                (_max.x, _max.y),
                (_min.x, _max.y),
                (_min.x, _min.y),
        ]:
            cr.line_to(x, y)
            cr.move_to(x, y)
        cr.stroke()

class GraphicObject(ABC):
    def __init__(self, name=''):
        super().__init__()
        self.name = name

    @abstractmethod
    def draw(self, cr: cairo.Context, viewport: Viewport, transform=lambda v: v):
        pass

    def transform(self, matrix: np.ndarray):
        pass

    @abstractmethod
    def normalize(self, window: Window):
        pass

    @abstractmethod
    def centroid(self):
        pass

    def translate(self, offset: Vetor2D):
        self.transform(translate_matrix(offset.x, offset.y))

    def scale(self, factor: Vetor2D):
        cx = self.centroid.x
        cy = self.centroid.y
        t_matrix = (
            translate_matrix(-cx, -cy) @
            scale_matrix(factor.x, factor.y) @
            translate_matrix(cx, cy)
        )
        self.transform(t_matrix)

    def rotate(self, angle: float, reference: Vetor2D):
        ref_x = reference.x
        ref_y = reference.y
        t_matrix = (
                translate_matrix(-ref_x, -ref_y) @
                rotation_matrix(angle) @
                translate_matrix(ref_x, ref_y)
        )
        self.transform(t_matrix)

    def clipped(self, window: Window, method=None) -> Optional['GraphicObject']:
        return self

class Point(GraphicObject):
    def __init__(self, posicao: Vetor2D, name=''):
        super().__init__(name)
        self.posicao = posicao
        self.normalize(Window(min=Vetor2D(), max=Vetor2D()))

    @property
    def x(self) -> float:
        return self.posicao[0]

    @property
    def y(self) -> float:
        return self.posicao[1]

    def draw(self, cr: cairo.Context, viewport: Viewport, transform=lambda v: v):
        viewport_coord = transform(self.normalized)
        cr.move_to(viewport_coord.x, viewport_coord.y)
        cr.arc(viewport_coord.x, viewport_coord.y, 1, 0, 2 * np.pi)
        cr.fill()

    @property
    def centroid(self):
        return self.posicao

    def transform(self, matrix: np.ndarray):
        print(f'posição: {self.posicao}')
        print(f'matrix: {matrix}')
        self.posicao = self.posicao @ matrix

    def normalize(self, window: Window):
        self.normalized = self.posicao

class Line(GraphicObject):
    def __init__(self, inicio: Vetor2D, fim: Vetor2D, name=''):
        super().__init__(name)
        self.inicio = inicio
        self.fim = fim
        self.normalize(Window(min=Vetor2D(), max=Vetor2D()))

    @property
    def x1(self):
        return self.inicio[0]

    @property
    def y1(self):
        return self.inicio[1]

    @property
    def x2(self):
        return self.fim[0]

    @property
    def y2(self):
        return self.fim[1]

    def draw(self, cr: cairo.Context,viewport: Viewport, transform=lambda v: v):
        viewport_coord1 = transform(self.normalized[0])
        viewport_coord2 = transform(self.normalized[1])
        cr.move_to(viewport_coord1.x, viewport_coord1.y)
        cr.line_to(viewport_coord2.x, viewport_coord2.y)
        cr.stroke()

    @property
    def centroid(self):
        return (self.inicio + self.fim) / 2

    def transform(self, matrix: np.ndarray):
        print(f'inicio: {self.inicio}')
        print(f'fim: {self.fim}')
        print(f'matriz: {matrix}')
        self.inicio = self.inicio @ matrix
        self.fim =  self.fim @ matrix

    def normalize(self, window: Window):
        self.normalized = [self.inicio, self.fim]


class Polygon(GraphicObject):
    def __init__(self, vertices, name=''):
        super().__init__(name)
        self.vertices = vertices
        self.normalized = self.vertices

    def draw(self, cr: cairo.Context,viewport: Viewport, transform=lambda v: v):
        if not self.normalized:
            return

        for i in range(0, len(self.vertices)):
            proximo = self.normalized[i]
            print(f'proximo: {proximo}')
            proximo_vp = transform(Vetor2D(proximo[0], proximo[1]))
            print(f'proximo_vp: {proximo_vp}')
            cr.line_to(proximo_vp.x, proximo_vp.y)
        cr.close_path()
        cr.stroke()

    @property
    def centroid(self):
        center = np.sum(self.vertices, 0) / len(self.vertices)
        return Vetor2D(center[0], center[1])

    def transform(self, matrix: np.ndarray):
        for i, vertex in enumerate(self.vertices):
            self.vertices[i] = vertex @ matrix

    def normalize(self, window: Window):
        self.normalized = self.vertices
