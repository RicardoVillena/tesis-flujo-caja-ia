"""Sesión IA07: Random Search frente a Optuna TPE para Ridge.

Uso desde la raíz, con el orden de etapas obligatorio:
  python scripts/reproduce_optimizacion_hiperparametros.py --protocolo   escribe reports/ia07/protocolo.json
  python scripts/reproduce_optimizacion_hiperparametros.py --buscar      trials, referencia densa y selección congelada (solo entrenamiento)
  python scripts/reproduce_optimizacion_hiperparametros.py --analizar    convergencia y diagnóstico de pruning
  python scripts/reproduce_optimizacion_hiperparametros.py --evaluar     evaluación única en prueba y gráficos
  python scripts/reproduce_optimizacion_hiperparametros.py --graficos    regenera los gráficos desde los CSV (no evalúa ni busca)
"""
import os
for clave in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(clave, '1')
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import optimizacion_hiperparametros as oh

if __name__ == '__main__':
    etapa = sys.argv[1] if len(sys.argv) > 1 else ''
    if etapa == '--protocolo':
        oh.escribir_protocolo()
        print('Protocolo escrito en', oh.OUT / 'protocolo.json')
    elif etapa == '--buscar':
        trials, densa, sel = oh.ejecutar_busqueda()
        print('Trials:', len(trials), '| referencia densa:', len(densa), '| configuraciones congeladas:', len(sel))
    elif etapa == '--analizar':
        _, _, _, agregado, _ = oh.analizar()
        print(agregado.to_string(index=False))
    elif etapa == '--evaluar':
        met, _, _ = oh.evaluar_prueba()
        trials = oh.pd.read_csv(oh.OUT / 'trials.csv')
        curvas = oh.pd.read_csv(oh.OUT / 'curvas_convergencia.csv')
        oh.graficos(trials, curvas, met, oh.OUT)
        (oh.OUT / 'integridad_previa.json').write_text(json.dumps(oh.estado_archivos_previos(), indent=2) + '\n', encoding='utf-8')
        print('Prueba evaluada:', len(met), 'filas de métricas')
    elif etapa == '--graficos':
        print(oh.graficos(oh.pd.read_csv(oh.OUT / 'trials.csv'), oh.pd.read_csv(oh.OUT / 'curvas_convergencia.csv'), oh.pd.read_csv(oh.OUT / 'metricas_prueba.csv'), oh.OUT))
    else:
        sys.exit(__doc__)
