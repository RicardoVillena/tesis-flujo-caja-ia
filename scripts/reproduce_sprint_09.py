"""Reproduce el Sprint 09 (variantes E0–E4, sensibilidad t-1 e importancia) sin red ni datos de prueba 2022–2025.

Uso desde la raíz: python scripts/reproduce_sprint_09.py [--protocolo]
  --protocolo  solo escribe reports/sprint_09/protocolo.json (paso previo a ejecutar).
La versión inicial de este script está en el commit 6eeac16 (resultados en reports/sprint_09/antecedente_6eeac16/).
"""
import os
for clave in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(clave, '1')  # determinismo y misma configuración que la versión inicial
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import variantes_importancia as vi

if __name__ == '__main__':
    if '--protocolo' in sys.argv[1:]:
        vi.escribir_protocolo()
        print('Protocolo escrito en reports/sprint_09/protocolo.json')
    else:
        salidas = vi.run()
        print(salidas['resumen_comparaciones.csv'].query('cumple_regla')[['moneda', 'candidato', 'comparador', 'delta_RMSE_anual_medio_pct']].to_string(index=False))
