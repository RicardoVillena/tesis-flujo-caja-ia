"""Reproduce la evaluación de variables del Sprint 08 sin red ni datos de prueba.

Sin argumentos: ejecución original (reports/sprint_08/ablacion/).
--revision: revisión exploratoria de cierre (reports/sprint_08/ablacion_revision/).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ablacion_variables import run, run_revision
if __name__ == '__main__':
    if '--revision' in sys.argv[1:]:
        salidas = run_revision()
        print('Revisión reproducida en reports/sprint_08/ablacion_revision/')
        print(salidas['decision_final.csv'].to_string(index=False))
    else:
        salidas = run()
        print('Ablación reproducida en reports/sprint_08/ablacion/')
        print(salidas['resumen_ablacion.csv'].groupby(['moneda', 'clasificacion']).size().to_string())
