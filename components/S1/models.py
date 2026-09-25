from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Zone:
    zone_id: str
    nome_amigavel: str
    polygon: List[Point]
    risco: str
    cor_dashboard: str


@dataclass(frozen=True)
class TrajectoryPoint:
    timestamp: datetime
    source_id: str
    entity_id: str
    position: Point


@dataclass
class ZoneEvent:

    entity_id: str
    timestamp: datetime
    zone_id: Optional[str]
    zone_name: Optional[str]
    event_type: str  # "enter" | "exit" | "transfer" | "update" | "none"
    entered_at: Optional[datetime] = None
    dwell_seconds: Optional[float] = None
    occupancy: int = 0
    risco: Optional[str] = None
    cor_dashboard: Optional[str] = None
    previous_zone_id: Optional[str] = None
