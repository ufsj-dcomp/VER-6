from s1.hysteresis import HysteresisController


def test_confirms_transition_only_after_min_streak():
    hysteresis = HysteresisController(min_streak=2)

    zone, transitioned = hysteresis.update("obj_01", None)
    assert zone is None and not transitioned

    zone, transitioned = hysteresis.update("obj_01", "zona_a")
    assert zone is None and not transitioned  # ainda não atingiu o streak mínimo

    zone, transitioned = hysteresis.update("obj_01", "zona_a")
    assert zone == "zona_a" and transitioned


def test_ignores_single_sample_flicker_at_border():
    hysteresis = HysteresisController(min_streak=2)
    sequence = [None, "zona_b", None, "zona_b", None]
    result = [hysteresis.update("obj_01", z)[0] for z in sequence]
    assert all(z is None for z in result)  # oscilação nunca é confirmada


def test_transition_streak_resets_when_raw_zone_changes():
    hysteresis = HysteresisController(min_streak=2)
    hysteresis.update("obj_01", "zona_a")
    hysteresis.update("obj_01", "zona_b")  # muda de candidata antes de confirmar
    zone, transitioned = hysteresis.update("obj_01", "zona_b")
    assert zone == "zona_b" and transitioned


def test_entities_are_tracked_independently():
    hysteresis = HysteresisController(min_streak=1)
    hysteresis.update("obj_01", "zona_a")
    zone, _ = hysteresis.update("obj_02", "zona_b")
    assert hysteresis.current_zone("obj_01") == "zona_a"
    assert zone == "zona_b"


def test_invalid_min_streak_raises():
    try:
        HysteresisController(min_streak=0)
    except ValueError:
        return
    raise AssertionError("esperava ValueError para min_streak < 1")
