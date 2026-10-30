"""Sprint 09 — Variantes de atributos (E0–E4), sensibilidad temporal e importancia de variables.

Evalúa si los bloques macroeconómico y bursátil mejoran la predicción del FCL preliminar t+1
frente a los atributos financieros, con Ridge y HistGradientBoosting en la validación temporal
anidada del Sprint 08 (años externos 2017–2021). Solo usa entrenamiento (anio_objetivo <= 2021),
por moneda. El protocolo se escribe y versiona antes de ejecutar; es una evaluación exploratoria.
"""
from pathlib import Path
import json
import platform
import subprocess
import time
import numpy as np
import pandas as pd
import sklearn
import src.ablacion_variables as ab
import src.auditoria_calidad as ac
import src.comparacion_modelos as cm

ROOT = ab.ROOT
OUT = ROOT / 'reports/sprint_09'
ANTECEDENTE = OUT / 'antecedente_6eeac16'
SPRINT08 = ROOT / 'reports/sprint_08/comparacion_modelos'
IDENT = ['id_fila', 'RPJ', 'Ejercicio', 'anio_objetivo']

MODELOS = ('ridge', 'boosting')
ANIOS_EXTERNOS = ab.ANIOS_EXTERNOS
REFERENCIAS = ('media_historica', 'persistencia')
# Selección E4 (fijada antes de ejecutar): mismas constantes que la revisión del Sprint 08.
E4_UMBRAL_PCT = ab.UMBRAL_SELECCION_PCT
E4_MIN_ANIOS = ab.MIN_ANIOS_INTERNOS_MEJORA
E4_MAX_RETIRADAS = ab.MAX_RETIRADAS


def bloques():
    spec = ac.especificacion_e2()
    archivo = json.loads((ROOT / 'reports/sprint_08/especificacion_e2.json').read_text(encoding='utf-8'))
    assert archivo['E2'] == spec['E2']
    return {'financiero': spec['financieros'], 'macroeconomico': spec['macroeconomicos'], 'bursatil': spec['bursatiles']}


def variantes():
    b = bloques()
    return {'E0': b['financiero'], 'E1': b['financiero'] + b['macroeconomico'],
            'E2': b['financiero'] + b['macroeconomico'] + b['bursatil'], 'E3': b['financiero'] + b['bursatil']}


SENSIBILIDAD = {'E1_rezago': 'E1', 'E2_rezago': 'E2', 'E3_rezago': 'E3'}


def comparaciones_previstas():
    """(candidato, comparador, pregunta). Procedimiento = 'modelo:variante' o referencia."""
    pares = []
    for m in MODELOS:
        pares += [(f'{m}:E1', f'{m}:E0', 'aporte macroeconómico'), (f'{m}:E3', f'{m}:E0', 'aporte bursátil sobre financieros'),
                  (f'{m}:E2', f'{m}:E1', 'aporte bursátil sobre financieros + macro'), (f'{m}:E2', f'{m}:E0', 'aporte externo conjunto'),
                  (f'{m}:E2', f'{m}:E3', 'aporte macroeconómico sobre financieros + bursátil'),
                  (f'{m}:E4', f'{m}:E2', 'selección de atributos frente a todos'), (f'{m}:E4', f'{m}:E0', 'selección frente a financieros'),
                  (f'{m}:E1_rezago', f'{m}:E0', 'sensibilidad t-1: aporte macroeconómico'),
                  (f'{m}:E3_rezago', f'{m}:E0', 'sensibilidad t-1: aporte bursátil'),
                  (f'{m}:E2_rezago', f'{m}:E0', 'sensibilidad t-1: aporte externo conjunto'),
                  (f'{m}:E2_rezago', f'{m}:E1_rezago', 'sensibilidad t-1: aporte bursátil sobre macro')]
        for v in ['E0', 'E1', 'E2', 'E3', 'E4']:
            pares += [(f'{m}:{v}', r, f'frente a referencia simple') for r in REFERENCIAS]
    for v in ['E0', 'E1', 'E2', 'E3', 'E4']:
        pares.append((f'boosting:{v}', f'ridge:{v}', 'algoritmo (misma variante)'))
    return pares


def protocolo():
    vs = variantes()
    return {
        'version': 'Sprint 09 — protocolo fijado antes de ejecutar E3, E4, sensibilidad t-1 e importancia por bloques',
        'caracter': 'EXPLORATORIO. Los años externos 2017–2021 ya se examinaron en el Sprint 08; los resultados E0–E2 de Ridge y boosting ya se observaron en '
                    'la versión inicial del Sprint 09 (commit 6eeac16). No se cambian rejillas, criterios ni años tras observarlos. La prueba 2022–2025 no se usa.',
        'datos': 'Filas elegibles de entrenamiento (anio_objetivo <= 2021), por moneda; mismas filas externas para todas las variantes y referencias.',
        'validacion': {'anios_externos': list(ANIOS_EXTERNOS), 'interna': '3 años previos, ventana expansiva, >= 8 años de historia (Sprint 08)',
                       'criterio_interno': 'promedio simple del RMSE de los años internos'},
        'variantes': {**vs, 'E4': 'subconjunto de los 26 atributos de E2 seleccionado dentro de cada entrenamiento externo (ver seleccion_E4)'},
        'modelos': list(MODELOS), 'rejillas': {m: cm.rejillas()[m] for m in MODELOS},
        'presupuesto': 'Misma rejilla (8 configuraciones) y mismos pliegues internos para cada variante y modelo; desempate hacia la configuración más simple (Sprint 08).',
        'referencias': {'media_historica': 'media del objetivo en el entrenamiento externo', 'persistencia': 'FCL(t) válido; respaldo: media del entrenamiento externo'},
        'seleccion_E4': {
            'candidatos': '26 atributos de E2', 'por_modelo': True,
            'paso_1': 'hiperparámetros h0 = configuración de E2 elegida con los pliegues internos',
            'paso_2': f'eliminación hacia atrás con h0 fijo: en cada paso se evalúa retirar cada atributo restante; admisible si mejora el RMSE interno medio >= {E4_UMBRAL_PCT:g} % '
                      f'y en >= {E4_MIN_ANIOS} de 3 años internos; se elige la admisible de menor RMSE (empate: orden E2); parada si ninguna es admisible o tras {E4_MAX_RETIRADAS} retiradas',
            'paso_3': 'reajuste de hiperparámetros del subconjunto final con la rejilla completa y los mismos pliegues internos; ajuste en el entrenamiento externo; una sola predicción del año externo',
            'justificacion': 'h0 fijo durante la eliminación mantiene acotado el coste de boosting; el mismo procedimiento se aplica a Ridge para comparar selección con selección.',
            'restriccion': 'no usa resultados externos ni el ranking de importancia del Sprint 09'},
        'disponibilidad_temporal': {
            'supuesto_principal': 'los atributos de t (financieros y externos del año calendario t) están disponibles al pronosticar t+1; no está acreditado '
                                  '(Sprint 08: 0 atributos verificados, 12 con posible fuga temporal)',
            'sensibilidad_t_1': {'variantes': SENSIBILIDAD, 'definicion': 'los 7 externos se reemplazan por su valor del año Ejercicio-1 (fuente anual); 2005 queda faltante y '
                                 'se imputa dentro del pipeline (Ridge) o como NaN nativo (boosting); E0 no cambia',
                                 'advertencia': 'el rezago reduce la simultaneidad pero no acredita publicación ni elimina revisiones de las series'}},
        'importancia': {
            'individual': 'retirar cada uno de los 26 atributos de E2, reajustar con la configuración E2 de ese pliegue (congelada) y predecir el año externo',
            'bloques': 'retirar cada bloque (financiero, macroeconómico, bursátil) de E2 con la configuración E2 congelada',
            'signo': 'delta_RMSE = RMSE_sin_atributo - RMSE_completo; positivo = retirarlo aumenta el error (aporte predictivo); negativo = retirarlo reduce el error',
            'estabilidad': 'años con delta > 0 (tolerancia relativa 1e-6), mediana y media del delta porcentual; aporte estable = delta > 0 en >= 4 de 5 años y media >= 1 %',
            'no_permutacion': 'no se permutan externos entre empresas del mismo año: son constantes dentro del año; se usa retirada con reajuste',
            'interpretacion': 'importancia predictiva condicional al modelo y a los demás atributos; no implica causalidad; la redundancia puede repartir u ocultar aportes'},
        'comparaciones': [dict(candidato=a, comparador=b, pregunta=q) for a, b, q in comparaciones_previstas()],
        'regla': f'mejora consistente si RMSE anual medio <= -{cm.UMBRAL_PCT:g} %, menor RMSE en >= {cm.MIN_ANIOS_MEJORA} de 5 años y MAE anual medio no mayor (Sprint 08; no es significancia)',
        'objetivo': 'FCL preliminar t+1 = FCO(t+1) + CAPEX_reportado(t+1), no FCFF validado; sin imputar',
    }


def tabla_rezagada(entrenamiento, externos):
    anual = pd.read_csv(ROOT / 'data/processed/macroeconomia_peru_2005_2025.csv', float_precision='round_trip').set_index('anio').join(
        pd.read_csv(ROOT / 'data/processed/bursatil_mercado_anual.csv', float_precision='round_trip').set_index('anio'), how='outer')
    t = entrenamiento.copy()
    for v in externos:
        np.testing.assert_array_equal(t[v].to_numpy(), t.Ejercicio.map(anual[v]).to_numpy())  # el panel usa el año t
        t[v] = t.Ejercicio.sub(1).map(anual[v])
    return t


def rmse_interno_fijo(modelo, cache, cols, cfg):
    """RMSE por año interno con hiperparámetros fijos (preparación siempre ajustada en el entrenamiento interno)."""
    if modelo == 'ridge':
        return np.array([f.rmse(cols, (cfg['alpha'],))[0] for f in cache['ridge']])
    out = []
    for _, tr, va in cache['cortes']:
        est, conv, _, err = cm.ajustar(modelo, cols, cfg, tr)
        assert est is not None and conv, err
        out.append(float(np.sqrt(np.mean((est.predict(va[cols]) - va.objetivo_fcl_t1.to_numpy()) ** 2))))
    return np.array(out)


def seleccionar_e4(modelo, pasado, candidatos, etiqueta):
    """Eliminación hacia atrás acotada usando solo `pasado` (entrenamiento externo)."""
    cache = {'ridge': ab.pliegues_internos(pasado, candidatos) if modelo == 'ridge' else None, 'cortes': cm.cortes_internos(pasado)}
    h0, _ = cm.buscar(modelo, pasado, candidatos, {**etiqueta, 'variante': 'E4_h0'})
    actual = list(candidatos)
    anual = rmse_interno_fijo(modelo, cache, actual, h0)
    ev = dict(rmse_medio=float(anual.mean()), rmse_anual=anual)
    hist = [dict(**etiqueta, modelo=modelo, paso=0, atributo_evaluado='', n_atributos=len(actual), rmse_interno_medio=ev['rmse_medio'],
                 mejora_pct=np.nan, anios_internos_mejora=np.nan, admisible=True, elegido=True, configuracion_h0=json.dumps(h0), motivo='26 atributos con h0')]
    parada = f'máximo de {E4_MAX_RETIRADAS} retiradas'
    for paso in range(1, E4_MAX_RETIRADAS + 1):
        cand = []
        for c in actual:
            r = rmse_interno_fijo(modelo, cache, [x for x in actual if x != c], h0)
            cand.append((c, dict(rmse_medio=float(r.mean()), rmse_anual=r)))
        k, filas, motivo = ab.elegir_retirada(ev, cand, candidatos, 'mejor_admisible')
        for i, ((c, e), f) in enumerate(zip(cand, filas)):
            hist.append(dict(**etiqueta, modelo=modelo, paso=paso, n_atributos=len(actual) - 1, rmse_interno_medio=e['rmse_medio'], **f,
                             elegido=i == k, configuracion_h0=json.dumps(h0), motivo='retirada aceptada' if i == k else ''))
        if k is None:
            parada = f'paso {paso}: {motivo}'
            break
        actual = [x for x in actual if x != cand[k][0]]
        ev = cand[k][1]
    cfg, filas = cm.buscar(modelo, pasado, actual, {**etiqueta, 'variante': 'E4'})
    return actual, cfg, h0, hist, filas, parada


def ajustar_predecir(modelo, cols, cfg, pasado, externo):
    est, conv, seg, err = cm.ajustar(modelo, cols, cfg, pasado)
    assert est is not None and conv, err
    p = est.predict(externo[cols])
    assert np.isfinite(p).all()
    return p, seg


def ejecutar(entrenamiento, anios_externos=ANIOS_EXTERNOS, modelos=MODELOS, con_importancia=True):
    assert entrenamiento.particion.eq('entrenamiento').all() and entrenamiento.anio_objetivo.le(ab.ANIO_OBJETIVO_MAX_TRAIN).all()
    vs, b = variantes(), bloques()
    rezagada = tabla_rezagada(entrenamiento, b['macroeconomico'] + b['bursatil'])
    preds, busq, sel_hist, sel, imp, impb, tiempos, internos = [], [], [], [], [], [], [], []
    for moneda in sorted(entrenamiento.Moneda.unique()):
        t, tl = entrenamiento.loc[entrenamiento.Moneda.eq(moneda)], rezagada.loc[rezagada.Moneda.eq(moneda)]
        for y in anios_externos:
            pasado, externo = t.loc[t.anio_objetivo.lt(y)], t.loc[t.anio_objetivo.eq(y)]
            pasado_l, externo_l = tl.loc[tl.anio_objetivo.lt(y)], tl.loc[tl.anio_objetivo.eq(y)]
            assert len(externo) and pasado.anio_objetivo.max() < y and pasado.index.equals(pasado_l.index) and externo.index.equals(externo_l.index)
            for anio, tr, va in cm.cortes_internos(pasado):
                internos.append(dict(moneda=moneda, anio_externo=int(y), anio_interno=anio, anio_train_max=int(tr.anio_objetivo.max()), n_train=len(tr), n_validacion=len(va)))
            for g in ab.referencias_simples(pasado, externo, moneda, IDENT):
                preds.append(g.drop(columns=['alpha', 'n_atributos']).assign(modelo='referencia', variante=g.procedimiento.iloc[0], configuracion=''))
            for modelo in modelos:
                cfgs = {}
                trabajos = [(v, vs[v], pasado, externo) for v in vs] + [(s, vs[base], pasado_l, externo_l) for s, base in SENSIBILIDAD.items()]
                for v, cols, pa, ex in trabajos:
                    tag = dict(moneda=moneda, anio_externo=int(y), variante=v)
                    t0 = time.perf_counter()
                    cfg, filas = cm.buscar(modelo, pa, cols, tag)
                    busq += filas
                    assert cfg is not None, (tag, modelo)
                    p, seg = ajustar_predecir(modelo, cols, cfg, pa, ex)
                    cfgs[v] = cfg
                    if v == 'E2':
                        p_e2 = p
                    preds.append(ex[IDENT].assign(procedimiento=f'{modelo}:{v}', moneda=moneda, y_real=ex.objetivo_fcl_t1.to_numpy(), y_predicho=p,
                                                  usa_respaldo_media=False, modelo=modelo, variante=v, configuracion=json.dumps(cfg)))
                    tiempos.append(dict(moneda=moneda, anio_externo=int(y), modelo=modelo, variante=v, segundos=time.perf_counter() - t0))
                t0 = time.perf_counter()
                tag = dict(moneda=moneda, anio_externo=int(y))
                cols4, cfg4, h0, hist, filas, parada = seleccionar_e4(modelo, pasado, vs['E2'], tag)
                sel_hist += hist
                busq += filas
                p, _ = ajustar_predecir(modelo, cols4, cfg4, pasado, externo)
                preds.append(externo[IDENT].assign(procedimiento=f'{modelo}:E4', moneda=moneda, y_real=externo.objetivo_fcl_t1.to_numpy(), y_predicho=p,
                                                   usa_respaldo_media=False, modelo=modelo, variante='E4', configuracion=json.dumps(cfg4)))
                sel.append(dict(moneda=moneda, anio_externo=int(y), modelo=modelo, configuracion_h0=json.dumps(h0), configuracion_final=json.dumps(cfg4),
                                n_atributos=len(cols4), retirados=';'.join(c for c in vs['E2'] if c not in cols4), seleccionados=';'.join(cols4), motivo_parada=parada))
                tiempos.append(dict(moneda=moneda, anio_externo=int(y), modelo=modelo, variante='E4', segundos=time.perf_counter() - t0))
                if not con_importancia:
                    continue
                y_real = externo.objetivo_fcl_t1.to_numpy()
                base = float(np.sqrt(np.mean((p_e2 - y_real) ** 2)))
                base_mae = float(np.mean(np.abs(p_e2 - y_real)))
                for nombre, retirar, destino in [(c, [c], imp) for c in vs['E2']] + [(k, v, impb) for k, v in b.items()]:
                    cols_r = [c for c in vs['E2'] if c not in retirar]
                    p, _ = ajustar_predecir(modelo, cols_r, cfgs['E2'], pasado, externo)
                    rmse, mae = float(np.sqrt(np.mean((p - y_real) ** 2))), float(np.mean(np.abs(p - y_real)))
                    destino.append(dict(moneda=moneda, anio_externo=int(y), modelo=modelo, retirado=nombre, n_retirados=len(retirar),
                                        configuracion_E2=json.dumps(cfgs['E2']), RMSE_completo=base, RMSE_sin=rmse, delta_RMSE=rmse - base,
                                        delta_RMSE_pct=100 * (rmse - base) / base, MAE_completo=base_mae, MAE_sin=mae, delta_MAE_pct=100 * (mae - base_mae) / base_mae))
            print(f'{moneda} {y} completado', flush=True)
    pred = pd.concat(preds, ignore_index=True)
    pred['usa_respaldo_media'] = pred.usa_respaldo_media.astype(bool)
    return dict(pred=pred, busq=pd.DataFrame(busq), sel=pd.DataFrame(sel), sel_hist=pd.DataFrame(sel_hist), imp=pd.DataFrame(imp),
                impb=pd.DataFrame(impb), tiempos=pd.DataFrame(tiempos), internos=pd.DataFrame(internos))


def metricas_anuales(pred):
    return pd.DataFrame([dict(procedimiento=p, moneda=m, anio_externo=int(y), n=len(g), empresas=g.RPJ.nunique(), **{k: v for k, v in ab.metricas(g.y_real, g.y_predicho).items() if k != 'n'})
                         for (p, m, y), g in pred.groupby(['procedimiento', 'moneda', 'anio_objetivo'])])


def comparar(anual, pred, pares):
    por_anio, filas = [], []
    for m in sorted(anual.moneda.unique()):
        a = anual.loc[anual.moneda.eq(m)].set_index(['procedimiento', 'anio_externo'])
        for cand, comp, pregunta in pares:
            x, c = a.loc[cand], a.loc[comp]
            assert x.index.equals(c.index) and (x.n == c.n).all()
            for yy in x.index:
                fila = dict(moneda=m, candidato=cand, comparador=comp, pregunta=pregunta, anio_externo=int(yy), n=int(x.loc[yy, 'n']))
                for k in ['RMSE', 'MAE']:
                    d = x.loc[yy, k] - c.loc[yy, k]
                    fila.update({f'{k}_candidato': x.loc[yy, k], f'{k}_comparador': c.loc[yy, k], f'delta_{k}': d, f'delta_{k}_pct': 100 * d / c.loc[yy, k],
                                 f'direccion_{k}': str(ab._direccion(np.array([d]), np.array([c.loc[yy, k]]))[0])})
                por_anio.append(fila)
            g = pd.DataFrame(por_anio[-len(x):])
            pc = pred.loc[pred.moneda.eq(m) & pred.procedimiento.eq(cand)].sort_values('id_fila')
            pk = pred.loc[pred.moneda.eq(m) & pred.procedimiento.eq(comp)].sort_values('id_fila')
            assert pc.id_fila.tolist() == pk.id_fila.tolist()
            mc, mk = ab.metricas(pc.y_real, pc.y_predicho), ab.metricas(pk.y_real, pk.y_predicho)
            r = dict(moneda=m, candidato=cand, comparador=comp, pregunta=pregunta, anios=len(g),
                     RMSE_anual_medio_candidato=g.RMSE_candidato.mean(), RMSE_anual_medio_comparador=g.RMSE_comparador.mean(),
                     delta_RMSE_anual_medio_pct=100 * (g.RMSE_candidato.mean() - g.RMSE_comparador.mean()) / g.RMSE_comparador.mean(),
                     MAE_anual_medio_candidato=g.MAE_candidato.mean(), MAE_anual_medio_comparador=g.MAE_comparador.mean(),
                     delta_MAE_anual_medio_pct=100 * (g.MAE_candidato.mean() - g.MAE_comparador.mean()) / g.MAE_comparador.mean(),
                     delta_RMSE_concatenado_pct=100 * (mc['RMSE'] - mk['RMSE']) / mk['RMSE'], delta_MAE_concatenado_pct=100 * (mc['MAE'] - mk['MAE']) / mk['MAE'],
                     anios_mejora_RMSE=int(g.direccion_RMSE.eq('mejora').sum()), anios_empeora_RMSE=int(g.direccion_RMSE.eq('empeora').sum()),
                     anios_empate_RMSE=int(g.direccion_RMSE.eq('empate').sum()), peor_anio_delta_RMSE_pct=float(g.delta_RMSE_pct.max()))
            r['cumple_regla'] = cm.cumple_regla(r)
            filas.append(r)
    return pd.DataFrame(por_anio), pd.DataFrame(filas)


def resumen_importancia(df, clave):
    filas = []
    for (m, mo, a), g in df.groupby(['moneda', 'modelo', clave]):
        pos = int((g.delta_RMSE > ab.TOLERANCIA_EMPATE_REL * g.RMSE_completo).sum())
        neg = int((g.delta_RMSE < -ab.TOLERANCIA_EMPATE_REL * g.RMSE_completo).sum())
        media = g.delta_RMSE_pct.mean()
        filas.append(dict(moneda=m, modelo=mo, **{clave: a}, anios=len(g), delta_RMSE_pct_medio=media, delta_RMSE_pct_mediana=g.delta_RMSE_pct.median(),
                          delta_RMSE_pct_min=g.delta_RMSE_pct.min(), delta_RMSE_pct_max=g.delta_RMSE_pct.max(), delta_MAE_pct_medio=g.delta_MAE_pct.mean(),
                          anios_aporta=pos, anios_perjudica=neg, anios_empate=len(g) - pos - neg,
                          aporte_estable=bool(pos >= cm.MIN_ANIOS_MEJORA and media >= cm.UMBRAL_PCT),
                          perjuicio_estable=bool(neg >= cm.MIN_ANIOS_MEJORA and media <= -cm.UMBRAL_PCT)))
    return pd.DataFrame(filas)


def verificar_reproduccion(pred, imp):
    """Mismo protocolo que el Sprint 08 (E2 y referencias) y que la versión inicial del Sprint 09 (E0–E2, importancia)."""
    out = {}
    s08 = pd.read_csv(SPRINT08 / 'predicciones_externas.csv', dtype={'RPJ': 'string'}, float_precision='round_trip')
    for nuevo, viejo in [('media_historica', 'media_historica'), ('persistencia', 'persistencia'), ('ridge:E2', 'ridge'), ('boosting:E2', 'boosting')]:
        a = pred.loc[pred.procedimiento.eq(nuevo)].set_index(['moneda', 'id_fila']).sort_index()
        b_ = s08.loc[s08.procedimiento.eq(viejo)].set_index(['moneda', 'id_fila']).sort_index()
        assert a.index.equals(b_.index)
        np.testing.assert_allclose(a.y_predicho, b_.y_predicho, rtol=1e-9, atol=1e-6)
        out[f'sprint08:{nuevo}'] = float(np.max(np.abs(a.y_predicho.to_numpy() - b_.y_predicho.to_numpy()) / np.maximum(np.abs(b_.y_predicho.to_numpy()), 1)))
    v1 = ANTECEDENTE / 'predicciones.csv'
    if v1.exists():
        p1 = pd.read_csv(v1, dtype={'RPJ': 'string'}, float_precision='round_trip')
        for mo in MODELOS:
            for v in ['E0', 'E1', 'E2']:
                a = pred.loc[pred.procedimiento.eq(f'{mo}:{v}')].set_index(['moneda', 'id_fila']).sort_index()
                b_ = p1.loc[p1.modelo.eq(mo) & p1.variante.eq(v)].set_index(['moneda', 'id_fila']).sort_index()
                assert a.index.equals(b_.index)
                np.testing.assert_allclose(a.y_predicho, b_.y_predicho, rtol=1e-9, atol=1e-6)
                out[f'v1:{mo}:{v}'] = float(np.max(np.abs(a.y_predicho.to_numpy() - b_.y_predicho.to_numpy()) / np.maximum(np.abs(b_.y_predicho.to_numpy()), 1)))
        i1 = pd.read_csv(ANTECEDENTE / 'importancia_por_anio.csv')
        j = imp.merge(i1, left_on=['moneda', 'anio_externo', 'modelo', 'retirado'], right_on=['moneda', 'anio_externo', 'modelo', 'atributo'], validate='one_to_one')
        assert len(j) == len(imp) == len(i1)
        np.testing.assert_allclose(j.RMSE_sin, j.RMSE_sin_atributo, rtol=1e-9)
        out['v1:importancia_individual'] = float(np.max(np.abs(j.RMSE_sin - j.RMSE_sin_atributo) / j.RMSE_sin_atributo))
    return out


def graficos(resumen_proc, imp_res, impb, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tinta, tinta2, fondo = '#0b0b0b', '#52514e', '#fcfcfb'
    col = {'ridge': '#2a78d6', 'boosting': '#1baf7a'}
    cb = {'financiero': '#2a78d6', 'macroeconomico': '#eb6834', 'bursatil': '#1baf7a'}
    (out / 'graficos').mkdir(parents=True, exist_ok=True)
    rutas = []
    fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:,.0f}')
    for m in sorted(resumen_proc.moneda.unique()):
        r = resumen_proc.loc[resumen_proc.moneda.eq(m)].set_index('procedimiento')
        fig, ax = plt.subplots(figsize=(10, 4.6))
        vv = ['E0', 'E1', 'E3', 'E2', 'E4', 'E1_rezago', 'E3_rezago', 'E2_rezago']
        x = np.arange(len(vv))
        for k, mo in enumerate(MODELOS):
            vals = [r.loc[f'{mo}:{v}', 'RMSE_anual_medio'] for v in vv]
            ax.bar(x + (k - .5) * .38, vals, width=.36, color=col[mo], label='Ridge' if mo == 'ridge' else 'HistGradientBoosting', edgecolor=fondo, linewidth=2)
        for ref, ls in [('media_historica', ':'), ('persistencia', '--')]:
            ax.axhline(r.loc[ref, 'RMSE_anual_medio'], color=tinta2, ls=ls, lw=1.2)
            ax.text(len(vv) - .45, r.loc[ref, 'RMSE_anual_medio'], ' ' + ('media histórica' if ref == 'media_historica' else 'persistencia'), va='center', fontsize=8, color=tinta2)
        ax.set_xticks(x, vv)
        lo = min(r.RMSE_anual_medio) * .85
        ax.set_ylim(lo, max(r.RMSE_anual_medio) * 1.05)
        ax.yaxis.set_major_formatter(fmt)
        ax.set_ylabel('RMSE anual medio (unidad reportada)')
        ax.set_title(f'{ab._nombre(m)}: RMSE anual medio por variante (eje no parte de cero)', color=tinta, loc='left')
        ax.legend(frameon=False, fontsize=8, loc='upper left')
        for s in ['top', 'right']:
            ax.spines[s].set_visible(False)
        fig.tight_layout(rect=(0, 0, .93, 1))
        ruta = out / 'graficos' / f'variantes_{ab._slug(m)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        for ax, mo in zip(axs, MODELOS):
            g = imp_res.loc[imp_res.moneda.eq(m) & imp_res.modelo.eq(mo)].sort_values('delta_RMSE_pct_medio', ascending=False)
            g = pd.concat([g.head(8), g.tail(4)]).drop_duplicates('retirado').iloc[::-1]
            colores = ['#2a78d6' if v > 0 else '#e34948' for v in g.delta_RMSE_pct_medio]
            ax.barh(range(len(g)), g.delta_RMSE_pct_medio, color=colores, height=.6, edgecolor=fondo, linewidth=2)
            ax.set_yticks(range(len(g)), [f'{a}  ({p}/5)' for a, p in zip(g.retirado, g.anios_aporta)], fontsize=8)
            ax.axvline(0, color=tinta2, lw=1)
            ax.set_title(f'{"Ridge" if mo == "ridge" else "Boosting"}: Δ RMSE % al retirar', color=tinta, loc='left', fontsize=10)
            ax.set_xlabel('positivo = retirarlo empeora (aporta); (k/5) = años con aporte')
            for s in ['top', 'right']:
                ax.spines[s].set_visible(False)
        fig.suptitle(f'{ab._nombre(m)}: importancia individual (8 mayores y 4 menores, media de 5 años)', x=.02, ha='left', color=tinta)
        fig.tight_layout()
        ruta = out / 'graficos' / f'importancia_individual_{ab._slug(m)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
        fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), sharey=False)
        for ax, mo in zip(axs, MODELOS):
            g = impb.loc[impb.moneda.eq(m) & impb.modelo.eq(mo)]
            for bl, gg in g.groupby('retirado'):
                gg = gg.sort_values('anio_externo')
                ax.plot(gg.anio_externo, gg.delta_RMSE_pct, marker='o', ms=7, lw=2, color=cb[bl], mec=fondo, mew=1.5, label=bl)
            ax.axhline(0, color=tinta2, lw=1)
            ax.set_xticks(list(ANIOS_EXTERNOS))
            ax.set_title(f'{"Ridge" if mo == "ridge" else "Boosting"}: Δ RMSE % al retirar el bloque', color=tinta, loc='left', fontsize=10)
            ax.legend(frameon=False, fontsize=8)
            for s in ['top', 'right']:
                ax.spines[s].set_visible(False)
        fig.suptitle(f'{ab._nombre(m)}: importancia por bloques por año externo (positivo = el bloque aporta)', x=.02, ha='left', color=tinta)
        fig.tight_layout()
        ruta = out / 'graficos' / f'importancia_bloques_{ab._slug(m)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
    return rutas


def escribir_protocolo(out=None):
    """Escribe el protocolo antes de ejecutar (se versiona en un commit previo a los resultados)."""
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'protocolo.json').write_text(json.dumps(protocolo(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(out=None):
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    proto = protocolo()
    ruta_proto = out / 'protocolo.json'
    texto = json.dumps(proto, ensure_ascii=False, indent=2) + '\n'
    if out.resolve() == OUT.resolve():
        # En la carpeta oficial se exige el protocolo versionado: no se ejecuta con uno distinto.
        assert ruta_proto.exists() and ruta_proto.read_text(encoding='utf-8') == texto, 'protocolo.json ausente o distinto del código'
    ruta_proto.write_text(texto, encoding='utf-8')
    entorno = {'python': platform.python_version(), 'scikit-learn': sklearn.__version__, 'numpy': np.__version__, 'pandas': pd.__version__}
    try:
        entorno['git_head'] = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        entorno['git_head'] = None
    ab.verificar_modelo_original()
    entrenamiento, _ = ab.cargar_entrenamiento()
    r = ejecutar(entrenamiento)
    pred = r['pred']
    anual = metricas_anuales(pred)
    proc = anual.groupby(['moneda', 'procedimiento'], as_index=False).agg(anios=('anio_externo', 'size'), n=('n', 'sum'), RMSE_anual_medio=('RMSE', 'mean'), MAE_anual_medio=('MAE', 'mean'))
    conc = cm.concentracion(pred)
    comp_anio, comp = comparar(anual, pred, comparaciones_previstas())
    imp_res, impb_res = resumen_importancia(r['imp'], 'retirado'), resumen_importancia(r['impb'], 'retirado')
    verif = verificar_reproduccion(pred, r['imp'])
    rutas = graficos(proc, imp_res, r['impb'], out)
    salidas = {'pliegues_internos.csv': r['internos'], 'busquedas_internas.csv': r['busq'], 'seleccion_e4.csv': r['sel'], 'seleccion_e4_historial.csv': r['sel_hist'],
               'predicciones.csv': pred, 'metricas_por_anio.csv': anual, 'resumen_procedimientos.csv': proc, 'comparaciones_por_anio.csv': comp_anio,
               'resumen_comparaciones.csv': comp, 'importancia_individual_por_anio.csv': r['imp'], 'importancia_individual.csv': imp_res,
               'importancia_bloques_por_anio.csv': r['impb'], 'importancia_bloques.csv': impb_res, 'concentracion_error.csv': conc}
    for nombre, t in salidas.items():
        t.to_csv(out / nombre, index=False, float_format='%.15g')
    r['tiempos'].to_csv(out / 'tiempos_ajuste.csv', index=False, float_format='%.4f')
    (out / 'entorno.json').write_text(json.dumps(entorno, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (out / 'verificacion_reproduccion.json').write_text(json.dumps(verif, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return dict(salidas, tiempos=r['tiempos'], verificacion=verif, graficos=rutas, protocolo=proto)
