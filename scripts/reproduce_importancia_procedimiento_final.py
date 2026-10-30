"""Importancia post hoc de persistencia|boosting_abs:E1 (configuraciones ya seleccionadas; sin nueva búsqueda).

Uso desde la raíz: python scripts/reproduce_importancia_procedimiento_final.py [--sobrescribir]
Escribe reports/sprint_09/experimento_final/importancia_procedimiento_final/; no modifica las salidas auditadas.
"""
import os
for clave in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(clave, '1')
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import importancia_procedimiento_final as ipf

if __name__ == '__main__':
    _, resumen, verif = ipf.run(sobrescribir='--sobrescribir' in sys.argv[1:])
    print(verif)
    print(resumen.sort_values(['moneda', 'delta_RMSE_pct_medio'], ascending=[True, False])
          [['moneda', 'tipo', 'retirado', 'delta_RMSE_pct_medio', 'anios_aporta', 'anios_perjudica']].to_string(index=False))
