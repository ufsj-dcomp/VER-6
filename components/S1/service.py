"""Orquestração do componente S1 - Zonas, ocupação e eventos."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, Set, Tuple

from .geometry import ZoneResolver
from .hysteresis import HysteresisController
from .models import TrajectoryPoint, ZoneEvent


class S1Service:
    """Componente S1.

    Recebe trajetórias contínuas (I2, opcionalmente enriquecidas com as
    coordenadas de mundo de I3) e emite eventos espacialmente
    qualificados: associação (carimbo) entre a entidade e a região, com
    a transição de bordas protegida por uma janela de histerese.
    """

    def __init__(self, resolver: ZoneResolver, min_streak: int = 2):
        self._resolver = resolver
        self._hysteresis = HysteresisController(min_streak=min_streak)
        self._occupancy: Dict[str, Set[str]] = {
            zone.zone_id: set() for zone in resolver.zones()
        }
        self._entered_at: Dict[Tuple[str, str], datetime] = {}

    def process(self, point: TrajectoryPoint) -> ZoneEvent:
        raw_zone = self._resolver.resolve(point.position)
        raw_zone_id = raw_zone.zone_id if raw_zone else None

        previous_zone_id = self._hysteresis.current_zone(point.entity_id)
        confirmed_zone_id, transitioned = self._hysteresis.update(
            point.entity_id, raw_zone_id
        )

        event_type = "none"
        if transitioned:
            if previous_zone_id is not None:
                self._occupancy[previous_zone_id].discard(point.entity_id)
                self._entered_at.pop((point.entity_id, previous_zone_id), None)
                event_type = "exit" if confirmed_zone_id is None else "transfer"
            if confirmed_zone_id is not None:
                self._occupancy[confirmed_zone_id].add(point.entity_id)
                self._entered_at[(point.entity_id, confirmed_zone_id)] = point.timestamp
                if previous_zone_id is None:
                    event_type = "enter"
        elif confirmed_zone_id is not None:
            event_type = "update"

        zone = self._resolver.zone_by_id(confirmed_zone_id) if confirmed_zone_id else None
        entered_at = (
            self._entered_at.get((point.entity_id, confirmed_zone_id))
            if confirmed_zone_id
            else None
        )
        dwell_seconds = (
            (point.timestamp - entered_at).total_seconds()
            if entered_at is not None
            else None
        )
        occupancy = (
            len(self._occupancy[confirmed_zone_id]) if confirmed_zone_id else 0
        )

        return ZoneEvent(
            entity_id=point.entity_id,
            timestamp=point.timestamp,
            zone_id=confirmed_zone_id,
            zone_name=zone.nome_amigavel if zone else None,
            event_type=event_type,
            entered_at=entered_at,
            dwell_seconds=dwell_seconds,
            occupancy=occupancy,
            risco=zone.risco if zone else None,
            cor_dashboard=zone.cor_dashboard if zone else None,
            previous_zone_id=previous_zone_id,
        )

    def occupancy_snapshot(self) -> Dict[str, int]:
        """Contagem instantânea de entidades confirmadas por zona."""

        return {zone_id: len(entities) for zone_id, entities in self._occupancy.items()}
