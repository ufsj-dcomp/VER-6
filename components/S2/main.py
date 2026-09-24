import json
import os

from datetime import datetime
from filtro_ruido_temporal import FiltroRuidoTemporal
from motor_estado_concorrente import MotorGerenciamentoEstadoConcorrente

class CamadaS2:
    def __init__(self):
        self.filtro_temporal = FiltroRuidoTemporal()
        self.motor_estado = MotorGerenciamentoEstadoConcorrente()

    def processar_eventos(self, fluxo_bruto: list) -> list:
        # 1. Filtro de Ruído Temporal[cite: 2]
        eventos_sem_ruido = self.filtro_temporal.processar(fluxo_bruto)
        
        # 2. Gerenciamento de Estado Concorrente[cite: 2]
        eventos_canonicos_finais = self.motor_estado.fusao_e_deduplicacao(eventos_sem_ruido)
        
        # Eventos lógicos finais, estáveis e confiáveis prontos para A3[cite: 2]
        return eventos_canonicos_finais

if __name__ == "__main__":
    # Inicializa o motor S2
    #s2 = CamadaS2()

    # Caminhos para os ficheiros baseados na árvore do repositório Git
    caminho_eventos_s1 = "data/output_s1/eventos_s2_demo.json"
    caminho_eventos_fusao = "data/fusao_deduplicacao.json"

    def executar_teste_com_ficheiro(caminho_ficheiro):
        # Inicializa o motor S2
        s2 = CamadaS2() 

        if os.path.exists(caminho_ficheiro):
            print(f"\n=== A iniciar leitura do ficheiro: {caminho_ficheiro} ===")
            
            with open(caminho_ficheiro, 'r', encoding='utf-8') as ficheiro:
                fluxo_bruto = json.load(ficheiro)
            
            # 1. Garante que o fluxo é sempre uma lista (resolve o AttributeError)
            if isinstance(fluxo_bruto, dict):
                fluxo_bruto = [fluxo_bruto]
                
            # 2. Normaliza as chaves e converte datas para milissegundos
            eventos_normalizados = []
            for ev in fluxo_bruto:
                # Pega o timestamp direto ou de dentro de 'transition' (Mock S1)
                ts_str = ev.get("timestamp")
                if not ts_str and "transition" in ev:
                    ts_str = ev["transition"].get("timestamp")
                    
                ts_ms = 0
                if ts_str:
                    if isinstance(ts_str, int):
                        # Se já for um número inteiro (milissegundos), usa diretamente
                        ts_ms = ts_str
                    elif isinstance(ts_str, str):
                        # Se for texto (ISO-8601), converte para milissegundos
                        dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                        ts_ms = int(dt.timestamp() * 1000)
                    
                # Pega coordenadas diretas ou de dentro de 'world_coordinates' (Mock Fusão)
                coords = ev.get("world_coordinates", {})
                x = ev.get("x", coords.get("x"))
                y = ev.get("y", coords.get("y"))
                
                eventos_normalizados.append({
                    "entity_id": ev.get("entity_id"),
                    "source": ev.get("source_id", "desconhecida"),
                    "timestamp": ts_ms,
                    "x": x,
                    "y": y,
                    "zone_id": ev.get("zone_id")
                })
            
            # 3. Passa os dados normalizados pelo pipeline S2
            eventos_consolidados = s2.processar_eventos(eventos_normalizados)
            
            print("\nResultado Canônico (Saída de S2):")
            print(json.dumps(eventos_consolidados, indent=4, ensure_ascii=False))
        else:
            print(f"\n[AVISO] O ficheiro '{caminho_ficheiro}' não foi encontrado.")

    executar_teste_com_ficheiro(caminho_eventos_s1)
    executar_teste_com_ficheiro(caminho_eventos_fusao)