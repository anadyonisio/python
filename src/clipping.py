from enum import auto, Enum
from typing import List, Optional
import copy

from drawable import Line, Vetor2D

class LineClippingMethod(Enum):
    COHEN_SUTHERLAND = auto()

class CohenRegion:
    INSIDE = 0b0000
    LEFT = 0b0001
    RIGHT = 0b0010
    BOTTOM = 0b0100
    TOP = 0b1000

    @classmethod
    def region(cls, v: Vetor2D) -> 'CohenRegion':
        region = CohenRegion.INSIDE
        if v.x < -1:
            region |= CohenRegion.LEFT
        elif v.x > 1:
            region |= CohenRegion.RIGHT

        if v.y > 1:
            region |= CohenRegion.TOP
        elif v.y < -1:
            region |= CohenRegion.BOTTOM

        return region


def cohen_sutherland_line_clip(line: Line) -> Line:
    new_line = copy.deepcopy(line)
    inicio, fim = new_line.normalized_vertices
    regions = [
        CohenRegion.region(v)
        for v in (inicio, fim)
    ]

    while True:
        # dois pontos dentro
        if all([r == CohenRegion.INSIDE for r in regions]):
            return new_line
        # dois pontos fora
        elif regions[0] & regions[1] != 0:
            return

        clip_index = 0 if regions[0] != CohenRegion.INSIDE else 1

        dx, dy, _ = fim - inicio
        m = dx / dy

        if regions[clip_index] & CohenRegion.TOP != 0:
            x = inicio.x + m * (1 - inicio.y)
            y = 1
        elif regions[clip_index] & CohenRegion.BOTTOM != 0:
            x = inicio.x + m * (-1 - inicio.y)
            y = -1
        elif regions[clip_index] & CohenRegion.RIGHT != 0:
            x = 1
            y = inicio.y + (1 - inicio.x) / m
        elif regions[clip_index] & CohenRegion.LEFT != 0:
            x = -1
            y = inicio.y + (-1 - inicio.x) / m

        if clip_index == 0:
            inicio = Vetor2D(x, y)
            new_line.normalized_vertices[0] = inicio
            regions[0] = CohenRegion.region(inicio)
        else:
            fim = Vetor2D(x, y)
            new_line.normalized_vertices[1] = fim
            regions[1] = CohenRegion.region(fim)

#
# def liang_barsky_line_clip(line: Line) -> Optional[Line]:
#     inicio, fim = line.vertices_ndc
#
#     p1 = inicio.x - fim.x
#     p2 = -p1
#     p3 = inicio.y - fim.y
#     p4 = -p3
#
#     q1 = inicio.x - (-1)
#     q2 = 1 - inicio.x
#     q3 = inicio.y - (-1)
#     q4 = 1 - inicio.y
#
#     posarr = [1 for _ in range(5)]
#     negarr = [0 for _ in range(5)]
#
#     if (p1 == 0 and q1 < 0
#        or p3 == 0 and q3 < 0):
#         return
#
#     if p1 != 0:
#         r1 = q1 / p1
#         r2 = q2 / p2
#
#         if p1 < 0:
#             negarr.append(r1)
#             posarr.append(r2)
#         else:
#             negarr.append(r2)
#             posarr.append(r1)
#
#     if p3 != 0:
#         r3 = q3 / p3
#         r4 = q4 / p4
#
#         if p3 < 0:
#             negarr.append(r3)
#             posarr.append(r4)
#         else:
#             negarr.append(r4)
#             posarr.append(r3)
#
#     rn1 = max(negarr)
#     rn2 = min(posarr)
#
#     if rn1 > rn2:
#         return
#
#     xn1 = inicio.x + p2 * rn1
#     yn1 = inicio.y + p4 * rn1
#
#     xn2 = inicio.x + p2 * rn2
#     yn2 = inicio.y + p4 * rn2
#
#     new_line = copy.deepcopy(line)
#     new_line.vertices_ndc = [Vetor2D(xn1, yn1), Vetor2D(xn2, yn2)]
#     return new_line
#

def line_clip(line: Line, method=LineClippingMethod.COHEN_SUTHERLAND) -> Optional[Line]:
    METHODS = {
        LineClippingMethod.COHEN_SUTHERLAND: cohen_sutherland_line_clip
    }
    return METHODS[method](line)
