"""Simulador do componente S1 - Zonas, ocupação e eventos.

Lê um artefato de zonas e um fluxo de trajetórias (as mesmas entradas
que I2/I3 forneceriam) e imprime, na ordem temporal, os eventos
espacialmente qualificados emitidos pelo S1. Serve como o "cliente"
mínimo para a demonstração da Sprint 2: mostra que a histerese evita
múltiplos eventos de entrada/saída quando uma entidade oscila na borda
de uma zona.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from components.S1.geometry import ZoneResolver
from components.S1.loaders import load_trajectory, load_zones
from components.S1.service import S1Service

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--zonas",
        default=str(DATA_DIR / "definicao_zonas.json"),
        help="Caminho do artefato JSON de definição de zonas.",
    )
    parser.add_argument(
        "--trajetorias",
        default=str(DATA_DIR / "timestamp.json"),
        help="Caminho do JSON com as leituras de trajetória.",
    )
    parser.add_argument(
        "--min-streak",
        type=int,
        default=2,
        help="Nº de leituras consecutivas para confirmar uma transição de zona (janela de histerese).",
    )
    args = parser.parse_args()

    zones = load_zones(args.zonas)
    trajectory = load_trajectory(args.trajetorias)
    service = S1Service(ZoneResolver(zones), min_streak=args.min_streak)

    print(f"Carregadas {len(zones)} zona(s) e {len(trajectory)} leitura(s) de trajetória.")
    print(f"Janela de histerese: {args.min_streak} leitura(s) consecutiva(s).\n")

    for point in trajectory:
        event = service.process(point)
        zone_label = event.zone_name or "fora de qualquer zona"
        print(
            f"[{point.timestamp.isoformat()}] {point.entity_id} "
            f"@ ({point.position.x:.2f}, {point.position.y:.2f}) -> {zone_label} "
            f"| evento={event.event_type} | ocupação={event.occupancy}"
        )

    print("\nOcupação final por zona:")
    for zone in zones:
        count = service.occupancy_snapshot()[zone.zone_id]
        print(f"  {zone.nome_amigavel} ({zone.zone_id}, {zone.risco}): {count} entidade(s)")


if __name__ == "__main__":
    main()
