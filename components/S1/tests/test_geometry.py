from s1.geometry import ZoneResolver
from s1.models import Point, Zone


def _square(zone_id, x0, y0, x1, y1, risco="Segura", cor="Verde"):
    return Zone(
        zone_id=zone_id,
        nome_amigavel=zone_id,
        polygon=[Point(x0, y0), Point(x1, y0), Point(x1, y1), Point(x0, y1)],
        risco=risco,
        cor_dashboard=cor,
    )


def test_resolve_point_inside_single_zone():
    resolver = ZoneResolver([_square("a", 0, 0, 10, 10)])
    zone = resolver.resolve(Point(5, 5))
    assert zone is not None
    assert zone.zone_id == "a"


def test_resolve_point_outside_all_zones():
    resolver = ZoneResolver([_square("a", 0, 0, 10, 10)])
    assert resolver.resolve(Point(50, 50)) is None


def test_resolve_point_in_gap_between_zones():
    # Réplica do cenário real: zona_segura_01 termina em x=50 e
    # zona_proibida_01 começa em x=51, deixando uma faixa sem zona.
    zone_a = _square("zona_segura_01", 0, 0, 50, 50)
    zone_b = _square("zona_proibida_01", 51, 0, 100, 50, risco="Critico", cor="Vermelho")
    resolver = ZoneResolver([zone_a, zone_b])
    assert resolver.resolve(Point(50.9, 25)) is None
    zone = resolver.resolve(Point(51.1, 25))
    assert zone.zone_id == "zona_proibida_01"


def test_resolve_overlap_breaks_tie_by_nearest_centroid():
    zone_a = _square("a", 0, 0, 10, 10)
    zone_b = _square("b", 5, 0, 20, 10)
    resolver = ZoneResolver([zone_a, zone_b])

    # Ponto dentro da sobreposição [5,10]x[0,10], mais próximo do
    # centróide de b (12.5, 5).
    zone = resolver.resolve(Point(9, 5))
    assert zone.zone_id == "b"

    # Mais próximo do centróide de a (5, 5).
    zone = resolver.resolve(Point(6, 5))
    assert zone.zone_id == "a"
