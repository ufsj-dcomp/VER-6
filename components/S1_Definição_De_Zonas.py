import json
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# 1. Carregar os dados do arquivo
with open('data/definicao_zonas.json', 'r', encoding='utf-8') as arquivo:
    dados = json.load(arquivo)

# 2. Configurar a figura do gráfico
fig, ax = plt.subplots(figsize=(10, 6))

# Dicionário simples para traduzir as cores em português para o Matplotlib
mapa_cores = {
    "Verde": "#8bc34a",     
    "Vermelho": "#e53935"   
}

# 3. Iterar sobre as zonas e desenhá-las
for zona in dados['zonas']:
    pontos = [[pt['x'], pt['y']] for pt in zona['poligono']]
    
    cor_face = mapa_cores.get(zona['cor_dashboard'], 'gray')
    
    poligono_shape = Polygon(pontos, closed=True, facecolor=cor_face, 
                             alpha=0.6, edgecolor='black', linewidth=2)
    ax.add_patch(poligono_shape)
    
    centro_x = sum([p[0] for p in pontos]) / len(pontos)
    centro_y = sum([p[1] for p in pontos]) / len(pontos)
    
    texto_label = f"{zona['nome_amigavel']}\n({zona['risco']})"
    ax.text(centro_x, centro_y, texto_label, ha='center', va='center', 
            fontsize=11, weight='bold', color='black')

# 4. Ajustar os limites da tela (margem para visualização)
ax.set_xlim(-10, 110)
ax.set_ylim(-10, 60)
ax.set_aspect('equal')

# Adicionar detalhes finais
ax.set_title("Mapeamento das Zonas de Risco", fontsize=14, weight='bold')
ax.set_xlabel("Coordenada X")
ax.set_ylabel("Coordenada Y")
ax.grid(True, linestyle='--', alpha=0.5)

# 5. Salvar o gráfico como imagem (PNG)
plt.savefig("imgs/mapa_zonas.png", dpi=300, bbox_inches='tight')

# Opcional: Se você também quiser que a janela abra na tela, descomente a linha abaixo.
# plt.show()

# Fechar a figura para liberar memória
plt.close()

print("Imagem 'mapa_zonas.png' gerada com sucesso!")