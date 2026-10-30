"""Comparación incremental y ablación de atributos, sin usar prueba 2022–2025."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hashlib
import json
import numpy as np
import pandas as pd
from src import ablacion_variables as ab
from src import comparacion_modelos as cm

OUT = ab.ROOT / 'reports/sprint_09'


def run():
    OUT.mkdir(exist_ok=True)
    spec = json.loads((ab.ROOT / 'reports/sprint_08/especificacion_e2.json').read_text())
    blocks = {k: spec[k] for k in ('financieros', 'macroeconomicos', 'bursatiles')}
    variants = {'E0': blocks['financieros'], 'E1': blocks['financieros'] + blocks['macroeconomicos'], 'E2': spec['E2']}
    protocol = dict(anios_externos=list(ab.ANIOS_EXTERNOS), variantes=variants,
                    modelos=['ridge', 'boosting'], rejillas=cm.rejillas(),
                    ajuste='Tres años internos expansivos; mismo protocolo Sprint 08; preparación solo en entrenamiento.',
                    criterio='RMSE anual medio -1% o menor, mejora en >=4/5 años, MAE no mayor.',
                    importancia='Retirada individual E2 con reajuste y configuración E2 congelada por pliegue; delta RMSE sin atributo menos completo. No selección ni causalidad.',
                    alcance='Exploratorio: 2017–2021 ya examinados; no usa prueba 2022–2025. Monedas separadas; FCL preliminar, no FCFF validado.')
    (OUT / 'protocolo.json').write_text(json.dumps(protocol, ensure_ascii=False, indent=2))
    data, _ = ab.cargar_entrenamiento()
    preds, searches, importance = [], [], []
    for currency, group in data.groupby('Moneda'):
        for year in ab.ANIOS_EXTERNOS:
            train, val = group[group.anio_objetivo < year], group[group.anio_objetivo == year]
            assert train.anio_objetivo.max() < val.anio_objetivo.min() <= 2021
            for ref in ab.referencias_simples(train, val, currency, ['id_fila', 'RPJ', 'Ejercicio', 'anio_objetivo']):
                preds.append(ref.assign(modelo=ref.procedimiento, variante='referencia'))
            for model in ('ridge', 'boosting'):
                for variant, cols in variants.items():
                    tag = dict(moneda=currency, anio_externo=int(year), variante=variant)
                    cfg, rows = cm.buscar(model, train, cols, tag)
                    searches.extend(rows)
                    if cfg is None:
                        raise RuntimeError(f'Sin configuración válida: {tag} {model}')
                    est, converged, _, error = cm.ajustar(model, cols, cfg, train)
                    if est is None or not converged:
                        raise RuntimeError(error or 'No convergió')
                    prediction = est.predict(val[cols])
                    assert np.isfinite(prediction).all()
                    result = val[['id_fila', 'RPJ', 'Ejercicio', 'anio_objetivo']].copy()
                    result = result.assign(moneda=currency, modelo=model, variante=variant,
                                           y_real=val.objetivo_fcl_t1.to_numpy(), y_predicho=prediction,
                                           configuracion=json.dumps(cfg))
                    preds.append(result)
                    if variant == 'E2':
                        base = float(np.sqrt(np.mean((prediction - val.objetivo_fcl_t1.to_numpy()) ** 2)))
                        for col in cols:
                            reduced = [c for c in cols if c != col]
                            reduced_est, conv, _, err = cm.ajustar(model, reduced, cfg, train)
                            if reduced_est is None or not conv:
                                raise RuntimeError(err or 'No convergió ablación')
                            p = reduced_est.predict(val[reduced])
                            rmse = float(np.sqrt(np.mean((p - val.objetivo_fcl_t1.to_numpy()) ** 2)))
                            importance.append(dict(**tag, modelo=model, atributo=col, RMSE_completo=base,
                                                   RMSE_sin_atributo=rmse, delta_RMSE=rmse-base,
                                                   delta_RMSE_pct=100*(rmse/base-1)))
            print(f'Finalizado {currency} {year}', flush=True)
    pred = pd.concat(preds, ignore_index=True)
    annual = pd.DataFrame([dict(moneda=m, modelo=mo, variante=v, anio_externo=int(y), **ab.metricas(g.y_real, g.y_predicho))
                           for (m, mo, v, y), g in pred.groupby(['moneda','modelo','variante','anio_objetivo'])])
    summary = annual.groupby(['moneda','modelo','variante'], as_index=False).agg(RMSE_anual_medio=('RMSE','mean'), MAE_anual_medio=('MAE','mean'))
    comparisons = []
    for (currency, model), g in annual[annual.variante.ne('referencia')].groupby(['moneda','modelo']):
        for candidate, baseline in [('E1','E0'), ('E2','E0'), ('E2','E1')]:
            a = g[g.variante.eq(candidate)].set_index('anio_externo')
            b = g[g.variante.eq(baseline)].set_index('anio_externo')
            change = 100*(a.RMSE.mean()/b.RMSE.mean()-1)
            wins = int((a.RMSE < b.RMSE).sum())
            mae = 100*(a.MAE.mean()/b.MAE.mean()-1)
            comparisons.append(dict(moneda=currency, modelo=model, variante=candidate, referencia=baseline,
                                     delta_RMSE_pct=change, delta_MAE_pct=mae, anios_mejora=wins,
                                     mejora_consistente=bool(change <= -1 and wins >= 4 and mae <= 0)))
    imp = pd.DataFrame(importance)
    ranking = imp.groupby(['moneda','modelo','atributo'], as_index=False).agg(delta_RMSE_medio=('delta_RMSE','mean'), delta_RMSE_pct_medio=('delta_RMSE_pct','mean'), anios_aporta=('delta_RMSE',lambda x: int((x>0).sum())))
    outputs = {'predicciones.csv':pred,'busquedas.csv':pd.DataFrame(searches),'metricas_por_anio.csv':annual,
               'resumen.csv':summary,'comparacion_incremental.csv':pd.DataFrame(comparisons),
               'importancia_por_anio.csv':imp,'importancia_variables.csv':ranking}
    for name, table in outputs.items():
        table.to_csv(OUT/name, index=False)
    hashes = {name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in [*outputs, 'protocolo.json']}
    (OUT/'integridad.json').write_text(json.dumps(hashes, indent=2))
    lines = ['# Sprint 09 — Resultados exploratorios', '', 'Comparación en años objetivo 2017–2021, con ajuste interno temporal. Prueba 2022–2025 excluida. Menor error es mejor.', '',
             '| Moneda | Modelo | Comparación | ΔRMSE % | ΔMAE % | Años mejora | Cumple criterio |', '|---|---|---|---:|---:|---:|---|']
    for r in comparisons:
        lines.append(f"| {r['moneda']} | {r['modelo']} | {r['variante']} vs {r['referencia']} | {r['delta_RMSE_pct']:.2f} | {r['delta_MAE_pct']:.2f} | {r['anios_mejora']}/5 | {'Sí' if r['mejora_consistente'] else 'No'} |")
    lines += ['', 'La comparación E1–E0 mide aporte macro; E2–E1, aporte bursátil; E2–E0, aporte externo conjunto. Las variantes ajustan sus hiperparámetros con el mismo presupuesto interno.', '',
              'La importancia individual se calcula retirando cada atributo y reajustando con los hiperparámetros E2 de ese pliegue. Un delta positivo indica que retirarlo aumenta el error. Es importancia predictiva condicional; correlación entre atributos puede repartir u ocultar importancia. Las variables externas son constantes entre empresas de un año: por eso no se permutan filas dentro del año.', '',
              'Cinco años reutilizados, concentración del error en pocas empresas, disponibilidad temporal y escala monetaria pendientes. No confirma desempeño futuro ni causalidad. La clasificación de mejora sigue el criterio exploratorio del Sprint 08; no es significancia estadística. No se ajustaron rejillas después de observar estos resultados.']
    (OUT/'resultados.md').write_text('\n'.join(lines)+'\n')
    print(pd.DataFrame(comparisons).to_string(index=False))


if __name__ == '__main__':
    run()
