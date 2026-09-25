from datetime import datetime, timezone

from s1.models import ZoneEvent
from s1.s2_adapter import to_s2_transitions


def _event(event_type, zone_id=None, previous_zone_id=None):
    return ZoneEvent(
        entity_id="pessoa_01",
        timestamp=datetime(2026, 9, 16, 10, 0, 0, 100_000, tzinfo=timezone.utc),
        zone_id=zone_id,
        zone_name=None,
        event_type=event_type,
        previous_zone_id=previous_zone_id,
    )


def test_enter_produces_single_entrada_transition():
    event = _event("enter", zone_id="zona_segura_01")
    transitions = to_s2_transitions(event)
    assert transitions == [
        {
            "entity_id": "pessoa_01",
            "zone_id": "zona_segura_01",
            "transition": {"type": "entrada", "timestamp": "2026-09-16T10:00:00.100Z"},
        }
    ]


def test_exit_produces_single_saida_transition():
    event = _event("exit", zone_id=None, previous_zone_id="zona_segura_01")
    transitions = to_s2_transitions(event)
    assert transitions == [
        {
            "entity_id": "pessoa_01",
            "zone_id": "zona_segura_01",
            "transition": {"type": "saida", "timestamp": "2026-09-16T10:00:00.100Z"},
        }
    ]


def test_transfer_produces_saida_then_entrada():
    event = _event("transfer", zone_id="zona_proibida_01", previous_zone_id="zona_segura_01")
    transitions = to_s2_transitions(event)
    assert [t["transition"]["type"] for t in transitions] == ["saida", "entrada"]
    assert transitions[0]["zone_id"] == "zona_segura_01"
    assert transitions[1]["zone_id"] == "zona_proibida_01"


def test_update_and_none_produce_no_transitions():
    assert to_s2_transitions(_event("update", zone_id="zona_segura_01")) == []
    assert to_s2_transitions(_event("none")) == []
