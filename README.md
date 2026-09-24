# VER-6

## Como rodar componente S1

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Demonstração (equivalente ao "script simulador" da Sprint 2)
python3 -m components.S1.simulate

# Testes
pytest
```