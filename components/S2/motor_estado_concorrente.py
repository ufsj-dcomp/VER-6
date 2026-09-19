"""
Módulo: Motor de Gerenciamento de Estado Concorrente
Sprint: 2

Responsabilidades atendidas nesta Sprint:
- S2: Consolidação inicial: criar a estrutura do dicionário em memória que apenas recebe o ID e repassa para frente, sem fusão complexa ainda.
- S2: Fusão de identidade e Deduplicação: codificar a correlação para unificar IDs de múltiplas fontes apontando para a mesma coordenada no mesmo instante.
"""

import math

from typing import Dict, Any, List

class MotorGerenciamentoEstadoConcorrente:
    def __init__(self, merge_distance_threshold: float = 2.0, time_sync_threshold_ms: int = 100):
        self.merge_distance_threshold = merge_distance_threshold
        self.time_sync_threshold_ms = time_sync_threshold_ms
        
        # Consolidação inicial: criar a estrutura do dicionário em memória[cite: 2]
        self.estado_em_memoria = {}
        self.global_id_counter = 1

    def atualizar_estado_memoria(self, evento: Dict[str, Any]):
        """
        Recebe o ID e repassa para frente, registrando na memória[cite: 2].
        """
        entity_id = evento.get("entity_id")
        self.estado_em_memoria[entity_id] = evento

    def fusao_e_deduplicacao(self, eventos_validos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Codifica a correlação para unificar IDs de múltiplas fontes apontando para a mesma coordenada no mesmo instante[cite: 2].
        """
        eventos_canonicos = []
        indices_processados = set()
        
        for i, ev_base in enumerate(eventos_validos):
            self.atualizar_estado_memoria(ev_base)
            
            if i in indices_processados:
                continue
                
            # Estrutura de um Evento Canônico com identificador global[cite: 2]
            evento_fundido = {
                "global_entity_id": f"GLOBAL_{self.global_id_counter}",
                "fontes_origem": [ev_base.get("source", "desconhecida")],
                "x": ev_base.get("x"),
                "y": ev_base.get("y"),
                "timestamp": ev_base.get("timestamp"),
                "zone_id": ev_base.get("zone_id"),
                "status": "CONSOLIDADO"
            }
            
            self.global_id_counter += 1
            indices_processados.add(i)
            
            for j, ev_comparacao in enumerate(eventos_validos):
                if j in indices_processados:
                    continue
                    
                diff_tempo = abs(ev_base.get("timestamp") - ev_comparacao.get("timestamp"))
                
                x_base = ev_base.get("x") or 0.0
                y_base = ev_base.get("y") or 0.0
                x_comp = ev_comparacao.get("x") or 0.0
                y_comp = ev_comparacao.get("y") or 0.0
                
                distancia = math.hypot(x_base - x_comp, y_base - y_comp)
                
                if diff_tempo <= self.time_sync_threshold_ms and distancia <= self.merge_distance_threshold:
                    evento_fundido["fontes_origem"].append(ev_comparacao.get("source", "desconhecida"))
                    indices_processados.add(j)
                    self.atualizar_estado_memoria(ev_comparacao)
                    
            eventos_canonicos.append(evento_fundido)
            
        return eventos_canonicos