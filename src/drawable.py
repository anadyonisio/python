import cairo
import numpy as np

from abc import ABC, abstractmethod
from math import cos, sin, radians
from dataclasses import dataclass
from cairo import Context
from typing import List, Optional

from transformations import (
    rotation_matrix,
    translate_matrix,
    scale_matrix,
    normalized_matrix
)


class Vetor2D(np.ndarray):
    def __new__(cls, x: float = 0, y: float = 0):
        objeto = np.asarray([x, y, 1], dtype=float).view(cls)
        return objeto

    @property
    def x(self) -> float:
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self) -> float:
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value


class GraphicObject(ABC):
    def __init__(self, vertices=[], name=''):
        super().__init__()
        self.name = name
        self.vertices: List[Vetor2D] = vertices
        self.normalized_vertices: List[Vetor2D] = vertices

    @abstractmethod
    def draw(self, cr: cairo.Context, vp_matrix: np.ndarray):
        pass

    def transform(self, matrix: np.ndarray):
        self.vertices = [v @ matrix for v in self.vertices]

    # @abstractmethod
    # def normalize(self, window: Window):
    #     pass

    def update_norm_coord(self, window: 'Window'):
        t_matrix = normalized_matrix(window)
        self.normalized_vertices = [v @ t_matrix for v in self.vertices]

    @property
    def centroid(self):
        return sum(self.vertices) / len(self.vertices)

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

    def clipped(self, method=None) -> Optional['GraphicObject']:
        return self

class Rectangle(GraphicObject):
    def __init__(self, min: Vetor2D, max: Vetor2D, name=''):
        super().__init__(vertices=[min, max], name=name)

    @property
    def min(self):
        return self.vertices[0]

    @property
    def max(self):
        return self.vertices[1]

    @min.setter
    def min(self, value: Vetor2D):
        self.vertices[0] = value

    @max.setter
    def max(self, value: Vetor2D):
        self.vertices[1] = value

    @property
    def width(self) -> float:
        return self.max.x - self.min.x

    @property
    def height(self) -> float:
        return self.max.y - self.min.y

    def draw(self, cr: Context,  vp_matrix: np.ndarray):
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

    def with_margin(self, margin: float) -> 'Rectangle':
        return Rectangle(
            self.min + Vetor2D(margin, margin),
            self.max - Vetor2D(margin, margin),
        )
    # def offset(self, offset: Vetor2D):
    #     self.min += offset
    #     self.max += offset
    #
    # def rotate(self, angle: float):
    #     self.min = self.min @ rotation_matrix(angle)
    #     self.max = self.max @ rotation_matrix(angle)
    #
    # def zoom(self, amount: float):
    #     self.max *= amount
    #     self.min *= amount
    #
    # def center(self) -> Vetor2D:
    #     return (self.max + self.min) / 2

class Window(Rectangle):
    def __init__(self, min: Vetor2D, max: Vetor2D, angle: float = 0.0):
        super().__init__(min, max)
        self.angle = angle

class View:
    def __init__(self, obj_list : List[GraphicObject] = [], window: Window = None):
        self.obj_list = obj_list
        self.window = window

    def add_object(self, object: GraphicObject):
        object.update_norm_coord(self.window)
        self.obj_list.append(object)

    # def remove_objects(self, indexes: Iterable[int]):
    #     for i in reversed(indexes):
    #         self.objs.pop(i)
    #
    # def translate_window(self, offset: Vec2):
    #     self.window.translate(offset)
    #     self.update_ndc()
    #
    # def zoom_window(self, factor: float):
    #     self.window.scale(Vec2(factor, factor))
    #     self.update_ndc()
    #
    # def rotate_window(self):
    #     pass
    #     self.update_ndc()

    def update_norm_coord(self):
        for obj in self.obj_list:
            obj.update_ndc(self.window)

    # @classmethod
    # def load(self, path: str):
    #     with open(path) as file:
    #         contents = file.read()
    #         return ObjCodec.decode(contents)
    #
    # def save(self, path: str):
    #     with open(path, 'w+') as file:
    #         contents = ObjCodec.encode(self)
    #         file.write(contents)
    #
    # def clip_objects(self):
    #     pass

# @dataclass
# class Viewport:
#     region: Rectangle
#     window: Window
#
#     @property
#     def min(self) -> float:
#         return self.region.min
#
#     @property
#     def max(self) -> float:
#         return self.region.max
#
#     @property
#     def width(self) -> float:
#         return self.region.width
#
#     @property
#     def height(self) -> float:
#         return self.region.height
#
#     def transform(self, p: Vetor2D) -> Vetor2D:
#         if not isinstance(p, Vetor2D):
#             p = Vetor2D(p[0], p[1])
#
#         view_size = Vetor2D(self.max.x - self.min.x, self.max.y - self.min.y)
#
#         win_size = Vetor2D(self.window.max.x - self.window.min.x,
#                            self.window.max.y - self.window.min.y
#                            )
#         return Vetor2D((p.x - self.min.x) * view_size.x / win_size.x,
#                        (p.y - self.min.y) * view_size.y / win_size.y
#                        )
#
#     def draw(self, cr: Context):
#         _min = self.min
#         _max = self.max
#
#         cr.set_source_rgb(0.4, 0.4, 0.4)
#         cr.move_to(_min.x, _min.y)
#         for x, y in [
#                 (_max.x, _min.y),
#                 (_max.x, _max.y),
#                 (_min.x, _max.y),
#                 (_min.x, _min.y),
#         ]:
#             cr.line_to(x, y)
#             cr.move_to(x, y)
#         cr.stroke()


class Point(GraphicObject):
    def __init__(self, posicao: Vetor2D, name=''):
        super().__init__(vertices=[posicao], name=name)

    @property
    def posicao(self) -> float:
        return self.vertices[0]

    @posicao.setter
    def posicao(self, value: Vetor2D):
        self.vertices[0] = value

    def draw(self, cr: cairo.Context, vp_matrix: np.ndarray):
        posicao_vp = self.normalized_vertices[0] @ vp_matrix
        cr.move_to(posicao_vp.x, posicao_vp.y)
        cr.arc(posicao_vp.x, posicao_vp.y, 1, 0, 2 * np.pi)
        cr.fill()

    # @property
    # def centroid(self):
    #     return self.posicao
    #
    # def transform(self, matrix: np.ndarray):
    #     print(f'posição: {self.posicao}')
    #     print(f'matrix: {matrix}')
    #     self.posicao = self.posicao @ matrix

    # def normalize(self, window: Window):
    #     self.normalized = self.posicao

    def clipped(self, *args, **kwargs) -> Optional['Point']:
        posicao = self.normalized_vertices[0]

        return (
            self if (posicao.x >= -1
                     and posicao.x <= 1
                     and posicao.y >= -1
                     and posicao.y <= 1
                     )
            else None
        )

class Line(GraphicObject):
    def __init__(self, inicio: Vetor2D, fim: Vetor2D, name=''):
        super().__init__(vertices=[inicio, fim], name=name)
        #self.normalize(Window(min=Vetor2D(), max=Vetor2D()))

    @property
    def inicio(self):
        return self.vertices[0]

    @inicio.setter
    def inicio(self, value: Vetor2D):
        self.vertices[0] = value

    @property
    def fim(self):
        return self.vertices[1]

    @fim.setter
    def fim(self, value: Vetor2D):
        self.vertices[1] = value

    def draw(self, cr: cairo.Context,vp_matrix: np.ndarray):
        inicio_vp, fim_vp = [v @ vp_matrix for v in self.normalized_vertices]
        cr.move_to(inicio_vp.x, inicio_vp.y)
        cr.line_to(fim_vp.x, fim_vp.y)
        cr.stroke()
    #
    # @property
    # def centroid(self):
    #     return (self.inicio + self.fim) / 2
    #
    # def transform(self, matrix: np.ndarray):
    #     print(f'inicio: {self.inicio}')
    #     print(f'fim: {self.fim}')
    #     print(f'matriz: {matrix}')
    #     self.inicio = self.inicio @ matrix
    #     self.fim =  self.fim @ matrix
    #
    # def normalize(self, window: Window):
    #     self.normalized = [self.inicio, self.fim]

    def clipped(self, method: 'LineClippingMethod') -> Optional[GraphicObject]:

        from clipping import line_clip
        return line_clip(self, method)


class Polygon(GraphicObject):
    def __init__(self, vertices, name=''):
        super().__init__(vertices=vertices, name=name)
        # self.normalized = self.vertices

    def draw(self, cr: cairo.Context,vp_matrix: np.ndarray):
        # if not self.normalized:
        #     return

        for i in range(len(self.normalized_vertices)):
            proximo_vp = self.normalized_vertices[i] @ vp_matrix
            cr.line_to(proximo_vp.x, proximo_vp.y)
        cr.close_path()
        cr.stroke()

    def clipped(self, method=None) -> Optional['GraphicObject']:
        return self


    # @property
    # def centroid(self):
    #     center = np.sum(self.vertices, 0) / len(self.vertices)
    #     return Vetor2D(center[0], center[1])
    #
    # def transform(self, matrix: np.ndarray):
    #     for i, vertex in enumerate(self.vertices):
    #         self.vertices[i] = vertex @ matrix
    #
    # def normalize(self, window: Window):
    #     self.normalized = self.vertices


