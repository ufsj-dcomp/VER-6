"""Controlador de Estado Espacial.

Aplica uma janela de histerese à transição de zona de cada entidade,
evitando que oscilações na borda de uma zona (ex: uma entidade
"balançando" na porta) gerem múltiplos eventos de entrada/saída.

Uma transição de zona só é confirmada depois que a nova leitura bruta
se repete por `min_streak` amostras consecutivas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class _EntityState:
    confirmed_zone_id: Optional[str] = None
    pending_zone_id: Optional[str] = None
    pending_streak: int = 0


class HysteresisController:
    def __init__(self, min_streak: int = 2):
        if min_streak < 1:
            raise ValueError("min_streak deve ser >= 1")
        self._min_streak = min_streak
        self._states: Dict[str, _EntityState] = {}

    def update(
        self, entity_id: str, raw_zone_id: Optional[str]
    ) -> Tuple[Optional[str], bool]:
        """Processa a leitura bruta de zona para a entidade.

        Retorna uma tupla (zona_confirmada, houve_transicao).
        """

        state = self._states.setdefault(entity_id, _EntityState())

        if raw_zone_id == state.confirmed_zone_id:
            # Confirma a permanência: descarta qualquer transição pendente.
            state.pending_zone_id = None
            state.pending_streak = 0
            return state.confirmed_zone_id, False

        if raw_zone_id == state.pending_zone_id:
            state.pending_streak += 1
        else:
            state.pending_zone_id = raw_zone_id
            state.pending_streak = 1

        if state.pending_streak >= self._min_streak:
            state.confirmed_zone_id = raw_zone_id
            state.pending_zone_id = None
            state.pending_streak = 0
            return state.confirmed_zone_id, True

        return state.confirmed_zone_id, False

    def current_zone(self, entity_id: str) -> Optional[str]:
        state = self._states.get(entity_id)
        return state.confirmed_zone_id if state else None

    def reset(self, entity_id: str) -> None:
        self._states.pop(entity_id, None)
