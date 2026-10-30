"""Reproduce el experimento final del Sprint 09 sin red ni datos de prueba 2022–2025.

Uso desde la raíz: python scripts/reproduce_experimento_final.py [--protocolo]
  --protocolo  solo escribe reports/sprint_09/experimento_final/protocolo.json (paso previo).
"""
import os
for clave in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(clave, '1')
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import experimento_final as ef

if __name__ == '__main__':
    if '--protocolo' in sys.argv[1:]:
        ef.escribir_protocolo()
        print('Protocolo escrito en', ef.OUT / 'protocolo.json')
    else:
        s = ef.run()
        print(s['resumen_comparaciones.csv'].query('cumple_regla')[['moneda', 'candidato', 'comparador', 'delta_RMSE_anual_medio_pct']].to_string(index=False))
