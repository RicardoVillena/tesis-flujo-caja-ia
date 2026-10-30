"""Reproduce la comparación acotada de modelos del Sprint 08 sin red ni datos de prueba."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.comparacion_modelos import run
if __name__ == '__main__':
    salidas = run()
    print('Comparación reproducida en reports/sprint_08/comparacion_modelos/')
    print(salidas['decision.csv'].to_string(index=False))
