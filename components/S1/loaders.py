from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Union

from .models import Point, TrajectoryPoint, Zone

PathLike = Union[str, Path]


def load_zones(path: PathLike) -> List[Zone]:

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    zones = []
    for raw in data["zonas"]:
        polygon = [Point(vertex["x"], vertex["y"]) for vertex in raw["poligono"]]
        zones.append(
            Zone(
                zone_id=raw["zone_id"],
                nome_amigavel=raw["nome_amigavel"],
                polygon=polygon,
                risco=raw["risco"],
                cor_dashboard=raw["cor_dashboard"],
            )
        )
    return zones


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_trajectory(path: PathLike) -> List[TrajectoryPoint]:
    """Carrega leituras de trajetória contínua (vindas de I2/I3)."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    points = [
        TrajectoryPoint(
            timestamp=_parse_timestamp(raw["timestamp"]),
            source_id=raw["source_id"],
            entity_id=raw["entity_id"],
            position=Point(
                raw["world_coordinates"]["x"], raw["world_coordinates"]["y"]
            ),
        )
        for raw in data
    ]
    points.sort(key=lambda p: p.timestamp)
    return points
