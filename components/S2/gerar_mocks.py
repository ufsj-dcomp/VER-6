import os
import json

def construir_jsons_de_teste(caminho_gt, saida_s1, saida_fusao, limite_frames=30):
    """
    Lê o Ground Truth do MOT20 e gera os payloads para a Sprint 2.
    """
    eventos_s1 = []
    eventos_fusao = []
    
    # O seqinfo.ini do MOT20 indica 25 FPS (40ms por frame)
    ms_por_frame = 40
    ts_base = 1789552800000 
    
    if not os.path.exists(caminho_gt):
        print(f"Erro: Não foi possível encontrar o ficheiro em {caminho_gt}")
        return

    with open(caminho_gt, 'r') as ficheiro:
        for linha in ficheiro:
            colunas = linha.strip().split(',')
            frame = int(colunas[0])
            
            # Limitamos os frames para não criar ficheiros gigantescos
            if frame > limite_frames:
                break
                
            entity_id = int(colunas[1])
            
            # Ignorar entradas inválidas caso existam
            if entity_id == -1:
                continue
                
            # Extrair coordenadas e calcular o centro do objeto
            x_esq, y_topo = float(colunas[2]), float(colunas[3])
            largura, altura = float(colunas[4]), float(colunas[5])
            x_centro = round(x_esq + (largura / 2), 2)
            y_centro = round(y_topo + (altura / 2), 2)
            
            ts_atual = ts_base + (frame * ms_por_frame)
            
            # 1. Cria o evento da Câmara Principal
            evento_principal = {
                "timestamp": ts_atual,
                "source_id": "cam_frontal",
                "entity_id": f"pedestre_{entity_id}",
                "world_coordinates": {"x": x_centro, "y": y_centro}
            }
            
            # Guarda no Mock S1 (fluxo limpo)
            eventos_s1.append(evento_principal)
            
            # 2. Cria o evento da Câmara Secundária (simulando sobreposição)
            # Adiciona ruído espacial (+0.2m) e temporal (+15ms)
            evento_secundario = {
                "timestamp": ts_atual + 15,
                "source_id": "cam_lateral",
                "entity_id": f"pedestre_{entity_id}",
                "world_coordinates": {
                    "x": round(x_centro + 0.2, 2), 
                    "y": round(y_centro + 0.1, 2)
                }
            }
            
            # Guarda ambos no Mock de Fusão
            eventos_fusao.append(evento_principal)
            eventos_fusao.append(evento_secundario)

    # Escreve os ficheiros nas pastas corretas
    with open(saida_s1, 'w') as f1:
        json.dump(eventos_s1, f1, indent=2)
        
    with open(saida_fusao, 'w') as f2:
        json.dump(eventos_fusao, f2, indent=2)
        
    print(f"Sucesso!")
    print(f"-> {len(eventos_s1)} eventos guardados em {saida_s1}")
    print(f"-> {len(eventos_fusao)} eventos guardados em {saida_fusao}")

# Ajusta o caminho inicial para onde descompactaste a pasta MOT20
construir_jsons_de_teste(
    caminho_gt="MOT20/train/MOT20-01/gt/gt.txt",
    saida_s1="data/mock_s1_evento_espacial.json",
    saida_fusao="data/fusao_deduplicacao.json"
)