from enum import auto, Enum
from typing import List, Optional
import copy

from drawable import Line, Vetor2D, Polygon

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
    nova_linha = copy.deepcopy(line)
    inicio, fim = nova_linha.normalized_vertices
    regions = [
        CohenRegion.region(v)
        for v in (inicio, fim)
    ]

    while True:
        # dois pontos dentro
        if all([r == CohenRegion.INSIDE for r in regions]):
            return nova_linha
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
            nova_linha.normalized_vertices[0] = inicio
            regions[0] = CohenRegion.region(inicio)
        else:
            fim = Vetor2D(x, y)
            nova_linha.normalized_vertices[1] = fim
            regions[1] = CohenRegion.region(fim)

def line_clip(line: Line, method=LineClippingMethod.COHEN_SUTHERLAND) -> Optional[Line]:
    METHODS = {
        LineClippingMethod.COHEN_SUTHERLAND: cohen_sutherland_line_clip
    }
    return METHODS[method](line)

def poly_iter(vertices: List[Vetor2D]):
    if not vertices:
        return
    v1 = vertices[0]
    for v2 in vertices[1:]:
        yield v1, v2
        v1 = v2
    yield v1, vertices[0]

def poly_clipping(poly: Polygon) -> Optional[Polygon]:
    novo_poligono = copy.deepcopy(poly)

    def clip_region(vertices, clipping_region):
        clipped = []
        for v1, v2 in poly_iter(vertices):
            regions = [ CohenRegion.region(v) & clipping_region for v in [v1, v2]]

            if all([region != clipping_region for region in regions]):
                clipped.extend([v1, v2])
            elif all([region == clipping_region for region in regions]):
                continue
            elif any([region == clipping_region for region in regions]):
                clip_index = 0 if regions[0] == clipping_region else 1

                dx, dy, _ = v2 - v1
                m = dx / dy

                if clipping_region == CohenRegion.TOP:
                    x = v1.x + m * (1 - v1.y)
                    y = 1
                elif clipping_region == CohenRegion.BOTTOM:
                    x = v1.x + m * (-1 - v1.y)
                    y = -1
                elif clipping_region == CohenRegion.RIGHT:
                    x = 1
                    y = v1.y + (1 - v1.x) / m
                elif clipping_region == CohenRegion.LEFT:
                    x = -1
                    y = v1.y + (-1 - v1.x) / m

                if clip_index == 0:
                    v1 = Vetor2D(x, y)
                else:
                    v2 = Vetor2D(x, y)
                clipped.extend([v1, v2])
        return clipped

    regions = [
        CohenRegion.LEFT,
        CohenRegion.TOP,
        CohenRegion.RIGHT,
        CohenRegion.BOTTOM
    ]
    for region in regions:
        novo_poligono.normalized_vertices = clip_region(
            novo_poligono.normalized_vertices,
            region
        )
    return novo_poligono

def curve_clipping(curve):
    nova_curva = copy.deepcopy(curve)

    def clip_region(vertices, clipping_region):
        clipped = []
        for i in range(len(vertices) - 1):
            v1 = vertices[i]
            v2 = vertices[i + 1]

            regions = [
                CohenRegion.region(v) & clipping_region for v in [v1, v2]
            ]

            if all([region != clipping_region for region in regions]):
                clipped.extend([v1, v2])
            elif all([region == clipping_region for region in regions]):
                continue
            elif any([region == clipping_region for region in regions]):
                clip_index = 0 if regions[0] == clipping_region else 1

                dx, dy, _ = v2 - v1
                m = dx / dy

                if clipping_region == CohenRegion.TOP:
                    x = v1.x + m * (1 - v1.y)
                    y = 1
                elif clipping_region == CohenRegion.BOTTOM:
                    x = v1.x + m * (-1 - v1.y)
                    y = -1
                elif clipping_region == CohenRegion.RIGHT:
                    x = 1
                    y = v1.y + (1 - v1.x) / m
                elif clipping_region == CohenRegion.LEFT:
                    x = -1
                    y = v1.y + (-1 - v1.x) / m

                if clip_index == 0:
                    v1 = Vetor2D(x, y)
                else:
                    v2 = Vetor2D(x, y)
                clipped.extend([v1, v2])
        return clipped

    regions = [
        CohenRegion.LEFT,
        CohenRegion.TOP,
        CohenRegion.RIGHT,
        CohenRegion.BOTTOM
    ]
    for region in regions:
        nova_curva.normalized_vertices = clip_region(
            nova_curva.normalized_vertices,
            region
        )

    return nova_curva