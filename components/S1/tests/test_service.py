from datetime import datetime, timedelta

from s1.geometry import ZoneResolver
from s1.models import Point, TrajectoryPoint, Zone
from s1.service import S1Service


def _zones():
    return [
        Zone(
            "zona_segura_01",
            "Recepção",
            [Point(0, 0), Point(50, 0), Point(50, 50), Point(0, 50)],
            "Segura",
            "Verde",
        ),
        Zone(
            "zona_proibida_01",
            "Portão Sul",
            [Point(51, 0), Point(100, 0), Point(100, 50), Point(51, 50)],
            "Critico",
            "Vermelho",
        ),
    ]


def _point(t_ms, x, y, entity="obj_01"):
    return TrajectoryPoint(
        datetime(2026, 1, 1) + timedelta(milliseconds=t_ms), "cam_frontal", entity, Point(x, y)
    )


def test_object_dancing_on_border_never_triggers_zone_event():
    """Réplica do cenário de demonstração da Sprint 2: um objeto
    "dançando" na linha da zona proibida não deve gerar eventos de
    entrada/saída."""

    service = S1Service(ZoneResolver(_zones()), min_streak=2)
    samples = [(0, 50.9), (100, 51.1), (200, 50.8)]

    events = [service.process(_point(t, x, 25.0)) for t, x in samples]

    assert all(event.event_type == "none" for event in events)
    assert all(event.zone_id is None for event in events)
    assert service.occupancy_snapshot() == {"zona_segura_01": 0, "zona_proibida_01": 0}


def test_sustained_entry_triggers_enter_and_updates_occupancy():
    service = S1Service(ZoneResolver(_zones()), min_streak=2)
    samples = [(0, 60.0), (100, 61.0), (200, 62.0)]

    events = [service.process(_point(t, x, 25.0)) for t, x in samples]

    assert events[0].event_type == "none"
    assert events[1].event_type == "enter"
    assert events[1].zone_id == "zona_proibida_01"
    assert events[1].risco == "Critico"
    assert events[2].event_type == "update"
    assert events[2].occupancy == 1
    assert events[2].dwell_seconds == 0.1


def test_exit_after_entry_frees_occupancy():
    service = S1Service(ZoneResolver(_zones()), min_streak=2)
    for t, x in [(0, 60.0), (100, 61.0)]:
        service.process(_point(t, x, 25.0))

    events = [service.process(_point(t, x, 25.0)) for t, x in [(200, 200.0), (300, 200.0)]]

    assert events[-1].event_type == "exit"
    assert events[-1].zone_id is None
    assert events[-1].previous_zone_id == "zona_proibida_01"
    assert service.occupancy_snapshot()["zona_proibida_01"] == 0


def test_two_sources_pointing_to_same_zone_are_counted_as_two_entities():
    service = S1Service(ZoneResolver(_zones()), min_streak=1)
    service.process(_point(0, 25.0, 25.0, entity="obj_01"))
    service.process(_point(0, 25.0, 25.0, entity="obj_02"))

    assert service.occupancy_snapshot()["zona_segura_01"] == 2
