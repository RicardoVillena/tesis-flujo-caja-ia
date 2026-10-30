"""Sprint 09 — Importancia post hoc del procedimiento final `persistencia|boosting_abs:E1`.

Retirada con reajuste, sin nueva búsqueda: por moneda y año externo se usa la configuración E1 ya seleccionada en
reports/sprint_09/experimento_final/configuraciones_seleccionadas.csv, con hiperparámetros congelados, el mismo
respaldo de FCL(t) (media del objetivo en el entrenamiento) y la misma reconstrucción base(t) + cambio predicho.
Se retira cada uno de los 23 atributos y los bloques financiero y macroeconómico; se reajusta y se evalúa en las
mismas filas externas. La retirada no afecta a base(t): FCL(t) sigue siendo la base de la formulación.
Es explicativa y exploratoria: los años 2017–2021 ya fueron examinados y no hay interpretación causal.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import src.ablacion_variables as ab
import src.alineacion_investigacion as ai
import src.auditoria_calidad as ac
import src.experimento_final as ef
import src.variantes_importancia as vi

FORMULACION, MODELO, VARIANTE = 'persistencia', 'boosting_abs', 'E1'
PROCEDIMIENTO = ef.procedimiento(FORMULACION, MODELO, VARIANTE)
OUT = ef.OUT / 'importancia_procedimiento_final'


def configuraciones():
    sel = pd.read_csv(ef.OUT / 'configuraciones_seleccionadas.csv')
    sel = sel.loc[sel.formulacion.eq(FORMULACION) & sel.modelo.eq(MODELO) & sel.variante.eq(VARIANTE)]
    assert not sel.duplicated(['moneda', 'anio_externo']).any()
    return {(r.moneda, int(r.anio_externo)): json.loads(r.configuracion) for r in sel.itertuples()}


def retiros():
    b = vi.bloques()
    cols = vi.variantes()[VARIANTE]
    assert cols == b['financiero'] + b['macroeconomico'] and len(cols) == 23
    return cols, [('individual', c, [c]) for c in cols] + [('bloque', k, b[k]) for k in ('financiero', 'macroeconomico')]


def _errores(p, y):
    e = p - y
    return float(np.sqrt(np.mean(e ** 2))), float(np.mean(np.abs(e)))


def ejecutar(entrenamiento, clas, anios_externos=vi.ANIOS_EXTERNOS):
    cfgs = configuraciones()
    cols, lista = retiros()
    datos = entrenamiento.loc[clas.loc[entrenamiento.index, ef.POBLACION].astype(bool)]
    completas, filas = [], []
    for moneda in sorted(datos.Moneda.unique()):
        t = datos.loc[datos.Moneda.eq(moneda)]
        for y in anios_externos:
            pasado, externo = t.loc[t.anio_objetivo.lt(y)], t.loc[t.anio_objetivo.eq(y)]
            assert len(externo) and pasado.anio_objetivo.max() < y
            cfg, real = cfgs[(moneda, int(y))], externo.objetivo_fcl_t1.to_numpy()
            p, _, _ = ef.ajustar_predecir(FORMULACION, MODELO, cols, cfg, pasado, externo)
            completas.append(externo[vi.IDENT].assign(moneda=moneda, y_predicho=p))
            rmse_c, mae_c = _errores(p, real)
            for tipo, nombre, quitar in lista:
                resto = [c for c in cols if c not in quitar]
                q, _, _ = ef.ajustar_predecir(FORMULACION, MODELO, resto, cfg, pasado, externo)
                rmse_s, mae_s = _errores(q, real)
                filas.append(dict(procedimiento=PROCEDIMIENTO, moneda=moneda, anio_externo=int(y), modelo=MODELO, tipo=tipo, retirado=nombre,
                                  n_retirados=len(quitar), n=len(externo), configuracion=json.dumps(cfg), RMSE_completo=rmse_c, RMSE_sin=rmse_s,
                                  delta_RMSE=rmse_s - rmse_c, delta_RMSE_pct=100 * (rmse_s - rmse_c) / rmse_c,
                                  MAE_completo=mae_c, MAE_sin=mae_s, delta_MAE_pct=100 * (mae_s - mae_c) / mae_c))
    return pd.concat(completas, ignore_index=True), pd.DataFrame(filas)


def verificar(completas, anual):
    """El modelo completo debe reproducir las predicciones auditadas del procedimiento final."""
    pred = pd.read_csv(ef.OUT / 'predicciones.csv', dtype={'RPJ': 'string'}, float_precision='round_trip')
    a = pred.loc[pred.procedimiento.eq(PROCEDIMIENTO)].set_index(['moneda', 'id_fila']).sort_index()
    b = completas.set_index(['moneda', 'id_fila']).sort_index()
    assert a.index.equals(b.index)
    dif = float(np.max(np.abs(a.y_predicho - b.y_predicho) / np.maximum(np.abs(a.y_predicho), 1)))
    assert dif <= 1e-9, dif
    met = pd.read_csv(ef.OUT / 'metricas_por_anio.csv')
    met = met.loc[met.procedimiento.eq(PROCEDIMIENTO)].set_index(['moneda', 'anio_externo'])
    comp = anual.drop_duplicates(['moneda', 'anio_externo']).set_index(['moneda', 'anio_externo']).loc[met.index]
    np.testing.assert_allclose(comp.RMSE_completo, met.RMSE, rtol=1e-9)
    np.testing.assert_allclose(comp.MAE_completo, met.MAE, rtol=1e-9)
    anios = anual.groupby(['moneda', 'retirado']).anio_externo.nunique()
    assert anios.eq(len(vi.ANIOS_EXTERNOS)).all()
    return {'procedimiento': PROCEDIMIENTO, 'filas_por_moneda': completas.groupby('moneda').size().to_dict(),
            'max_diferencia_relativa_prediccion_completa': dif, 'metricas_anuales_reproducidas': int(len(met)),
            'retiros_por_moneda_y_anio': int(anual.groupby(['moneda', 'anio_externo']).size().iloc[0])}


def run(out=None, sobrescribir=False):
    out = Path(out or OUT)
    for previo in ('importancia_por_anio.csv', 'importancia_resumen.csv'):
        assert sobrescribir or not (out / previo).exists(), f'{previo} ya existe; no se sobrescribe'
    out.mkdir(parents=True, exist_ok=True)
    panel, _, _ = ac.load_inputs()
    clas = ai.clasificar_poblacion(panel)
    entrenamiento = ab.separar_entrenamiento(panel)
    del panel
    completas, anual = ejecutar(entrenamiento, clas)
    verif = verificar(completas, anual)
    resumen = vi.resumen_importancia(anual, 'retirado').merge(anual[['moneda', 'retirado', 'tipo']].drop_duplicates(), on=['moneda', 'retirado'])
    resumen.insert(0, 'procedimiento', PROCEDIMIENTO)
    anual.to_csv(out / 'importancia_por_anio.csv', index=False, float_format='%.15g')
    resumen.to_csv(out / 'importancia_resumen.csv', index=False, float_format='%.15g')
    (out / 'verificacion.json').write_text(json.dumps(verif, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return anual, resumen, verif
