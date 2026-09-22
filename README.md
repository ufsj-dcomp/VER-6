# VER-6

## Como rodar componente S1

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Demonstração (equivalente ao "script simulador" da Sprint 2)
python3 -m components.S1.simulate

# Mesma coisa, mas com uma trajetória que de fato gera transições
python3 -m components.S1.simulate --trajetorias data/trajetoria_demo_transicoes.json \
    --saida-s2 data/output/eventos_s2_demo.json

# Testes
pytest
```