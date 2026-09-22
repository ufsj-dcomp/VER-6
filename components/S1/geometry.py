"""Motor de Geometria Estática.

Resolve se um ponto está dentro de um polígono (zona) e desempata
sobreposições entre zonas escolhendo a de centróide mais próximo.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon as ShapelyPolygon

from .models import Point, Zone


class ZoneResolver:
    def __init__(self, zones: List[Zone]):
        self._zones = list(zones)
        self._polygons: Dict[str, ShapelyPolygon] = {
            zone.zone_id: ShapelyPolygon([(p.x, p.y) for p in zone.polygon])
            for zone in self._zones
        }

    def zones(self) -> List[Zone]:
        return list(self._zones)

    def zone_by_id(self, zone_id: str) -> Optional[Zone]:
        for zone in self._zones:
            if zone.zone_id == zone_id:
                return zone
        return None

    def resolve(self, point: Point) -> Optional[Zone]:
        """Retorna a zona que contém o ponto, ou None se estiver fora
        de todas as zonas conhecidas."""

        shapely_point = ShapelyPoint(point.x, point.y)
        candidates = [
            zone
            for zone in self._zones
            if self._polygons[zone.zone_id].contains(shapely_point)
        ]

        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]

        # Sobreposição: desempata pela zona de centróide mais próximo.
        return min(
            candidates,
            key=lambda zone: self._polygons[zone.zone_id].centroid.distance(
                shapely_point
            ),
        )
