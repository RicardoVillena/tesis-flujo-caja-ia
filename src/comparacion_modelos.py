"""Sprint 08 — Comparación acotada de modelos (exploratoria) con los 26 atributos de E2.

Compara media histórica, persistencia, Ridge, Elastic Net y HistGradientBoosting en la validación
temporal anidada de la revisión de ablación (años externos 2017–2021). Solo entrenamiento
(anio_objetivo <= 2021), por moneda. Hiperparámetros elegidos solo con validación interna.
El protocolo se fijó en este módulo antes de ejecutar; los años externos ya se habían examinado.
"""
from pathlib import Path
import itertools
import json
import platform
import subprocess
import time
import warnings
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import src.ablacion_variables as ab

ROOT = ab.ROOT
OUT = ROOT / 'reports/sprint_08/comparacion_modelos'
REVISION = ROOT / 'reports/sprint_08/ablacion_revision'
PROPIOS = {'src/comparacion_modelos.py', 'scripts/reproduce_comparacion_modelos.py', 'tests/test_comparacion_modelos.py',
           'notebooks/sprint_08/13_comparacion_modelos.ipynb'}

# Protocolo fijado antes de ejecutar.
SEMILLA = 0
ANIOS_EXTERNOS = ab.ANIOS_EXTERNOS
ALPHAS_RIDGE = ab.ALPHAS_REVISION
EN_ALPHAS = (0.001, 0.01, 0.1, 1.0)
EN_L1 = (0.1, 0.5, 0.9)
EN_MAX_ITER, EN_TOL = 10000, 1e-4
HGB_PROFUNDIDAD = (2, 3)
HGB_ITERACIONES = (100, 300)
HGB_L2 = (0.0, 10.0)
HGB_FIJOS = dict(loss='squared_error', learning_rate=0.05, min_samples_leaf=20, early_stopping=False, random_state=SEMILLA)
EMPATE_REL = 1e-9
UMBRAL_PCT = 1.0
MIN_ANIOS_MEJORA = 4
REFERENCIAS = ('media_historica', 'persistencia')
MODELOS = ('ridge', 'elastic_net', 'boosting')
PROCEDIMIENTOS = REFERENCIAS + MODELOS


def rejillas():
    """Configuraciones en orden de simplicidad (la primera es la más simple); el desempate elige la más simple."""
    ridge = [dict(alpha=a) for a in sorted(ALPHAS_RIDGE, reverse=True)]
    en = [dict(alpha=a, l1_ratio=l) for a in sorted(EN_ALPHAS, reverse=True) for l in sorted(EN_L1, reverse=True)]
    hgb = [dict(max_depth=d, max_iter=i, l2_regularization=l) for d in HGB_PROFUNDIDAD for i in HGB_ITERACIONES for l in sorted(HGB_L2, reverse=True)]
    return {'ridge': ridge, 'elastic_net': en, 'boosting': hgb}


def protocolo():
    r = rejillas()
    return {
        'caracter': 'EXPLORATORIA: años externos 2017–2021 ya examinados en la ablación y su revisión; la elección del ganador no es una estimación independiente.',
        'ajuste_de_alcance': 'reports/sprint_08/instrucciones_claude.md (Etapa 1) excluía entrenar modelos nuevos; este encargo autoriza una comparación acotada como continuación del Sprint 08.',
        'datos': 'Solo filas elegibles de entrenamiento (anio_objetivo <= 2021); 26 atributos de E2 sin selección; soles y dólares por separado.',
        'validacion': {'anios_externos': list(ANIOS_EXTERNOS), 'entrenamiento_externo': 'anio_objetivo < año externo, misma moneda',
                       'interna': f'{ab.N_ANIOS_INTERNOS} últimos años antes del externo, ventana expansiva, >= {ab.MIN_ANIOS_HISTORIA_INTERNA} años de historia (mismo código que la revisión)',
                       'criterio': 'promedio simple del RMSE de los años internos', 'aleatoria': False},
        'referencias': {'media_historica': 'media de objetivo_fcl_t1 en el entrenamiento externo', 'persistencia': 'FCL(t) válido (src/ablacion_variables.fcl_t); respaldo: media del entrenamiento externo'},
        'ridge': {'pipeline': 'src/ablacion_variables.crear_modelo (mediana keep_empty_features + StandardScaler + Ridge svd)', 'rejilla_alpha': list(ALPHAS_RIDGE), 'configuraciones': len(r['ridge'])},
        'elastic_net': {'pipeline': 'TransformedTargetRegressor(Pipeline(ColumnTransformer(mediana keep_empty_features + StandardScaler), ElasticNet), transformer=StandardScaler()): '
                                    'el objetivo se estandariza con la media y desviación del entrenamiento; predicciones en unidades originales',
                        'alpha': list(EN_ALPHAS), 'l1_ratio': list(EN_L1), 'max_iter': EN_MAX_ITER, 'tol': EN_TOL, 'configuraciones': len(r['elastic_net'])},
        'boosting': {'algoritmo': 'HistGradientBoostingRegressor', 'max_depth': list(HGB_PROFUNDIDAD), 'max_iter': list(HGB_ITERACIONES), 'l2_regularization': list(HGB_L2),
                     'fijos': HGB_FIJOS, 'faltantes': 'tratamiento nativo de NaN (sin imputación ni eliminación de filas); sin escalado (árboles)',
                     'configuraciones': len(r['boosting'])},
        'maximo_configuraciones': {k: len(v) for k, v in r.items()},
        'desempate': f'diferencia relativa <= {EMPATE_REL:g} en el RMSE interno medio: configuración más simple (Ridge/Elastic Net: mayor alpha, luego mayor l1_ratio; '
                     'boosting: menor profundidad, menos iteraciones, mayor l2)',
        'fallos': 'una configuración con excepción, predicción no finita o ConvergenceWarning en cualquier pliegue interno queda excluida de la selección de ese año externo; '
                  'si el ajuste externo de la configuración elegida emite ConvergenceWarning se registra y se marca; si ninguna configuración es válida, el modelo no se evalúa en ese año',
        'regla_recomendacion': f'un modelo se recomienda frente a un comparador si su RMSE anual medio es <= -{UMBRAL_PCT:g} %, su RMSE es menor en >= {MIN_ANIOS_MEJORA} de '
                               f'{len(ANIOS_EXTERNOS)} años y su MAE anual medio no es mayor. Un modelo nuevo (Elastic Net o boosting) se recomienda solo si cumple frente a '
                               'media histórica, persistencia y Ridge. Decisión: el modelo vigente (Ridge) solo se sustituye por un procedimiento que cumpla la regla frente '
                               'a todos los demás (superioridad consistente); el menor RMSE observado se reporta por separado y no implica superioridad consistente. '
                               '(Aclaración de etiquetas tras la auditoría; la regla y los umbrales no cambian.)',
        'no_es': 'significancia estadística ni estimación independiente del rendimiento futuro',
        'versiones': {'python': platform.python_version(), 'scikit-learn': sklearn.__version__, 'numpy': np.__version__, 'pandas': pd.__version__},
    }


def crear_elastic_net(cols, alpha, l1_ratio):
    numerico = Pipeline([('imputer', SimpleImputer(strategy='median', keep_empty_features=True)), ('scaler', StandardScaler())])
    pre = ColumnTransformer([('numericas', numerico, cols)], remainder='drop', verbose_feature_names_out=False)
    pipe = Pipeline([('preparacion', pre), ('modelo', ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=EN_MAX_ITER, tol=EN_TOL))])
    return TransformedTargetRegressor(regressor=pipe, transformer=StandardScaler())


def crear_boosting(cols, max_depth, max_iter, l2_regularization):
    return HistGradientBoostingRegressor(max_depth=max_depth, max_iter=max_iter, l2_regularization=l2_regularization, **HGB_FIJOS)


def crear(modelo, cols, cfg):
    if modelo == 'ridge':
        return ab.crear_modelo(cols, cfg['alpha'])
    if modelo == 'elastic_net':
        return crear_elastic_net(cols, **cfg)
    return crear_boosting(cols, **cfg)


def ajustar(modelo, cols, cfg, tr):
    """Ajusta un modelo nuevo; devuelve (estimador, convergio, segundos, error)."""
    est = crear(modelo, cols, cfg)
    t0 = time.perf_counter()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        try:
            est.fit(tr[cols], tr.objetivo_fcl_t1)
        except Exception as e:  # registrado como fallo de la configuración
            return None, False, time.perf_counter() - t0, repr(e)
    no_conv = any(issubclass(x.category, ConvergenceWarning) for x in w)
    return est, not no_conv, time.perf_counter() - t0, ''


def cortes_internos(pasado):
    anios = sorted(pasado.anio_objetivo.unique())
    out = []
    for a in anios[-ab.N_ANIOS_INTERNOS:]:
        if sum(y < a for y in anios) < ab.MIN_ANIOS_HISTORIA_INTERNA:
            raise ValueError(f'Historia insuficiente para el año interno {a}')
        out.append((int(a), pasado.loc[pasado.anio_objetivo.lt(a)], pasado.loc[pasado.anio_objetivo.eq(a)]))
    return out


def buscar(modelo, pasado, cols, etiqueta):
    """Búsqueda interna; devuelve (configuración elegida o None, filas de la búsqueda)."""
    grid = rejillas()[modelo]
    filas = []
    if modelo == 'ridge':  # mismo cálculo que la revisión (src/ablacion_variables.evaluar_subconjunto)
        internos = ab.pliegues_internos(pasado, cols)
        m = np.vstack([f.rmse(cols, ALPHAS_RIDGE) for f in internos])
        for cfg in grid:
            k = ALPHAS_RIDGE.index(cfg['alpha'])
            filas.append(dict(**etiqueta, modelo=modelo, configuracion=json.dumps(cfg), valida=True, motivo='',
                              **{f'rmse_{f.anio}': m[j, k] for j, f in enumerate(internos)}, rmse_interno_medio=float(m[:, k].mean())))
    else:
        cortes = cortes_internos(pasado)
        for cfg in grid:
            rmses, valida, motivo = {}, True, ''
            for anio, tr, va in cortes:
                est, conv, _, err = ajustar(modelo, cols, cfg, tr)
                if est is None or not conv:
                    valida, motivo = False, err or f'ConvergenceWarning en año interno {anio}'
                    break
                p = est.predict(va[cols])
                if not np.isfinite(p).all():
                    valida, motivo = False, f'predicción no finita en año interno {anio}'
                    break
                rmses[f'rmse_{anio}'] = float(np.sqrt(np.mean((p - va.objetivo_fcl_t1.to_numpy()) ** 2)))
            filas.append(dict(**etiqueta, modelo=modelo, configuracion=json.dumps(cfg), valida=valida, motivo=motivo, **rmses,
                              rmse_interno_medio=float(np.mean(list(rmses.values()))) if valida else np.nan))
    validas = [(i, f['rmse_interno_medio']) for i, f in enumerate(filas) if f['valida']]
    if not validas:
        return None, filas
    mejor = min(v for _, v in validas)
    elegido = next(i for i, v in validas if v <= mejor * (1 + EMPATE_REL))  # grid en orden de simplicidad
    for i, f in enumerate(filas):
        f['elegida'] = i == elegido
    return grid[elegido], filas


def ejecutar(entrenamiento, cols, anios_externos=ANIOS_EXTERNOS):
    assert entrenamiento.particion.eq('entrenamiento').all() and entrenamiento.anio_objetivo.le(ab.ANIO_OBJETIVO_MAX_TRAIN).all()
    ident = ['id_fila', 'RPJ', 'Ejercicio', 'anio_objetivo']
    preds, busquedas, elegidos, tiempos, internos = [], [], [], [], []
    for moneda, t in entrenamiento.groupby('Moneda', sort=True):
        for y in anios_externos:
            pasado, externo = t.loc[t.anio_objetivo.lt(y)], t.loc[t.anio_objetivo.eq(y)]
            assert len(externo) and pasado.anio_objetivo.max() < y
            etiqueta = dict(moneda=moneda, anio_externo=int(y))
            for anio, tr, va in cortes_internos(pasado):
                internos.append(dict(**etiqueta, anio_interno=anio, anio_train_max=int(tr.anio_objetivo.max()), n_train=len(tr), n_validacion=len(va)))
            for g in ab.referencias_simples(pasado, externo, moneda, ident):
                preds.append(g.drop(columns=['alpha', 'n_atributos']))
            for modelo in MODELOS:
                t0 = time.perf_counter()
                cfg, filas = buscar(modelo, pasado, cols, etiqueta)
                t_busqueda = time.perf_counter() - t0
                busquedas += filas
                if cfg is None:
                    elegidos.append(dict(**etiqueta, modelo=modelo, configuracion='', convergio_externo=False, evaluado=False))
                    continue
                est, conv, seg, err = ajustar(modelo, cols, cfg, pasado)
                assert est is not None, err
                p = est.predict(externo[cols])
                assert np.isfinite(p).all()
                g = externo[ident].copy()
                g.insert(0, 'procedimiento', modelo)
                g.insert(1, 'moneda', moneda)
                g['y_real'], g['y_predicho'], g['usa_respaldo_media'] = externo.objetivo_fcl_t1.to_numpy(), p, False
                preds.append(g)
                elegidos.append(dict(**etiqueta, modelo=modelo, configuracion=json.dumps(cfg), convergio_externo=conv, evaluado=True))
                tiempos.append(dict(**etiqueta, modelo=modelo, segundos_busqueda_interna=t_busqueda, segundos_ajuste_externo=seg))
    pred = pd.concat(preds, ignore_index=True)
    pred['usa_respaldo_media'] = pred.usa_respaldo_media.astype(bool)
    return pred, pd.DataFrame(busquedas), pd.DataFrame(elegidos), pd.DataFrame(tiempos), pd.DataFrame(internos)


def metricas_anuales(pred):
    filas = []
    for (p, m, y), g in pred.groupby(['procedimiento', 'moneda', 'anio_objetivo']):
        filas.append(dict(procedimiento=p, moneda=m, anio_externo=int(y), empresas=g.RPJ.nunique(), **ab.metricas(g.y_real, g.y_predicho)))
    return pd.DataFrame(filas)


def comparaciones(anual):
    filas = []
    for m, g in anual.groupby('moneda'):
        a = g.set_index(['procedimiento', 'anio_externo'])
        procs = [p for p in PROCEDIMIENTOS if p in a.index.get_level_values(0)]
        for cand, comp in itertools.permutations(procs, 2):
            x, c = a.loc[cand], a.loc[comp]
            for y in x.index:
                fila = dict(moneda=m, candidato=cand, comparador=comp, anio_externo=int(y), n=int(x.loc[y, 'n']))
                for k in ['RMSE', 'MAE']:
                    d = x.loc[y, k] - c.loc[y, k]
                    fila.update({f'{k}_candidato': x.loc[y, k], f'{k}_comparador': c.loc[y, k], f'delta_{k}': d,
                                 f'delta_{k}_pct': float(ab._pct(d, c.loc[y, k])), f'direccion_{k}': str(ab._direccion(np.array([d]), np.array([c.loc[y, k]]))[0])})
                filas.append(fila)
    return pd.DataFrame(filas)


def cumple_regla(r):
    return bool(r['delta_RMSE_anual_medio_pct'] <= -UMBRAL_PCT and r['anios_mejora_RMSE'] >= MIN_ANIOS_MEJORA and r['delta_MAE_anual_medio_pct'] <= 0)


def resumen(anual, comp, pred):
    filas = []
    for (m, cand, compa), g in comp.groupby(['moneda', 'candidato', 'comparador']):
        rc, rk = g.RMSE_candidato.mean(), g.RMSE_comparador.mean()
        mc, mk = g.MAE_candidato.mean(), g.MAE_comparador.mean()
        pc = pred.loc[pred.moneda.eq(m) & pred.procedimiento.eq(cand)]
        pk = pred.loc[pred.moneda.eq(m) & pred.procedimiento.eq(compa)].set_index('id_fila').loc[pc.id_fila]
        cc, ck = ab.metricas(pc.y_real, pc.y_predicho), ab.metricas(pk.y_real, pk.y_predicho)
        r = dict(moneda=m, candidato=cand, comparador=compa, anios=len(g), RMSE_anual_medio_candidato=rc, RMSE_anual_medio_comparador=rk,
                 delta_RMSE_anual_medio_pct=100 * (rc - rk) / rk, MAE_anual_medio_candidato=mc, MAE_anual_medio_comparador=mk,
                 delta_MAE_anual_medio_pct=100 * (mc - mk) / mk, delta_RMSE_concatenado_pct=100 * (cc['RMSE'] - ck['RMSE']) / ck['RMSE'],
                 delta_MAE_concatenado_pct=100 * (cc['MAE'] - ck['MAE']) / ck['MAE'],
                 anios_mejora_RMSE=int(g.direccion_RMSE.eq('mejora').sum()), anios_empeora_RMSE=int(g.direccion_RMSE.eq('empeora').sum()),
                 anios_empate_RMSE=int(g.direccion_RMSE.eq('empate').sum()), anios_mejora_MAE=int(g.direccion_MAE.eq('mejora').sum()),
                 peor_empeoramiento_anual_RMSE_pct=float(g.delta_RMSE_pct.max()), anio_peor=int(g.loc[g.delta_RMSE_pct.idxmax(), 'anio_externo']))
        r['cumple_regla'] = cumple_regla(r)
        filas.append(r)
    return pd.DataFrame(filas)


def resumen_procedimientos(anual, pred):
    filas = []
    for (m, p), g in anual.groupby(['moneda', 'procedimiento']):
        pc = pred.loc[pred.moneda.eq(m) & pred.procedimiento.eq(p)]
        cc = ab.metricas(pc.y_real, pc.y_predicho)
        filas.append(dict(moneda=m, procedimiento=p, anios=len(g), n=int(g.n.sum()), RMSE_anual_medio=g.RMSE.mean(), MAE_anual_medio=g.MAE.mean(),
                          RMSE_concatenado=cc['RMSE'], MAE_concatenado=cc['MAE']))
    return pd.DataFrame(filas)


def concentracion(pred):
    """Proporción del error cuadrático externo concentrada en la empresa (y las 3 empresas) con mayor aporte."""
    filas = []
    for (m, p), g in pred.groupby(['moneda', 'procedimiento']):
        sse = ((g.y_predicho - g.y_real) ** 2).groupby(g.RPJ).sum().sort_values(ascending=False)
        filas.append(dict(moneda=m, procedimiento=p, empresas=len(sse), empresa_dominante=sse.index[0], proporcion_empresa_dominante=float(sse.iloc[0] / sse.sum()),
                          proporcion_top3=float(sse.iloc[:3].sum() / sse.sum()), top3=';'.join(sse.index[:3])))
    return pd.DataFrame(filas)


MODELO_VIGENTE_INICIAL = 'ridge'  # modelo vigente al empezar la comparación (validación anidada de la revisión)


def _criterios_fallidos(r):
    fallos = []
    if not r['delta_RMSE_anual_medio_pct'] <= -UMBRAL_PCT:
        fallos.append(f'RMSE {r["delta_RMSE_anual_medio_pct"]:+.3f} % no alcanza -{UMBRAL_PCT:g} %')
    if not r['anios_mejora_RMSE'] >= MIN_ANIOS_MEJORA:
        fallos.append(f'mejor en {r["anios_mejora_RMSE"]} de {r["anios"]} años (mínimo {MIN_ANIOS_MEJORA})')
    if not r['delta_MAE_anual_medio_pct'] <= 0:
        fallos.append(f'MAE {r["delta_MAE_anual_medio_pct"]:+.2f} % peor')
    return fallos


def decision(res, proc):
    """Separa el menor RMSE observado, la superioridad consistente (regla frente a todos los demás) y la decisión:
    el modelo vigente solo cambia si otro procedimiento cumple la regla frente a todos."""
    filas = []
    for m, g in res.groupby('moneda'):
        nuevos = {}
        for c in ['elastic_net', 'boosting']:
            x = g.loc[g.candidato.eq(c) & g.comparador.isin(['media_historica', 'persistencia', 'ridge'])]
            nuevos[c] = bool(len(x) == 3 and x.cumple_regla.all())
        superiores = [c for c in PROCEDIMIENTOS if len(g.loc[g.candidato.eq(c)]) and g.loc[g.candidato.eq(c)].cumple_regla.all()]
        superior = superiores[0] if superiores else ''
        pr = proc.loc[proc.moneda.eq(m)].sort_values('RMSE_anual_medio')
        mejor = pr.iloc[0].procedimiento
        vig = MODELO_VIGENTE_INICIAL
        if superior:
            vigente = superior
            cambio = (f'Conservar {vig}' if superior == vig else
                      f'Sustituir {vig} por {superior} (exploratorio; requiere confirmación en datos no examinados)')
            motivo = f'{superior} cumple la regla frente a los otros {len(PROCEDIMIENTOS) - 1} procedimientos.'
        else:
            vigente = vig
            cambio = f'Conservar {vig}; no se recomienda sustituirlo'
            if mejor == vig:
                motivo = f'{vig} tiene el menor RMSE observado, pero ningún procedimiento cumple la regla frente a todos los demás.'
            else:
                x = g.loc[g.candidato.eq(mejor) & g.comparador.eq(vig)].iloc[0]
                motivo = (f'Ningún procedimiento cumple la regla frente a todos. {mejor} tiene el menor RMSE observado; frente a {vig}: RMSE '
                          f'{x.delta_RMSE_anual_medio_pct:+.3f} %, MAE {x.delta_MAE_anual_medio_pct:+.2f} %, menor RMSE en {x.anios_mejora_RMSE} de {x.anios} años; '
                          f'no cumple el criterio predefinido para sustituirlo ({"; ".join(_criterios_fallidos(x))}). Mantener {vig} no demuestra que supere a '
                          f'{mejor}, ni equivalencia entre ambos, ni inutilidad de {mejor}: la evidencia no alcanza el criterio de cambio.')
        filas.append(dict(moneda=m, menor_RMSE_anual_medio=mejor, alternativa_con_superioridad_consistente=superior, modelo_vigente=vigente,
                          cambio_recomendado=cambio, motivo_decision=motivo, elastic_net_recomendado=nuevos['elastic_net'],
                          boosting_recomendado=nuevos['boosting'], orden_RMSE_anual_medio=' < '.join(pr.procedimiento)))
    return pd.DataFrame(filas)


def sensibilidad_empresa(pred, conc):
    """Post hoc descriptivo: excluye de la evaluación (no del ajuste) la empresa con mayor error cuadrático
    acumulado entre todos los procedimientos de cada moneda y recalcula el resumen y la decisión."""
    sse = pred.assign(sq=(pred.y_predicho - pred.y_real) ** 2).groupby(['moneda', 'RPJ']).sq.sum()
    excl = {m: sse.loc[m].idxmax() for m in pred.moneda.unique()}
    p = pred.loc[[r != excl[m] for m, r in zip(pred.moneda, pred.RPJ)]]
    anual = metricas_anuales(p)
    res = resumen(anual, comparaciones(anual), p)
    return excl, res, decision(res, resumen_procedimientos(anual, p))


def verificar_contra_revision(pred):
    """Referencias y Ridge deben reproducir las predicciones de la revisión anterior."""
    ruta = REVISION / 'predicciones_externas.csv'
    if not ruta.exists():
        return {}
    rev = pd.read_csv(ruta, dtype={'RPJ': 'string'}, float_precision='round_trip')
    mapa = {'media_historica': 'media_historica', 'persistencia': 'persistencia', 'ridge': 'completo_alpha_interno'}
    out = {}
    for nuevo, viejo in mapa.items():
        a = pred.loc[pred.procedimiento.eq(nuevo)].set_index(['moneda', 'id_fila']).sort_index()
        b = rev.loc[rev.procedimiento.eq(viejo)].set_index(['moneda', 'id_fila']).sort_index()
        assert a.index.equals(b.index)
        np.testing.assert_allclose(a.y_predicho, b.y_predicho, rtol=1e-9, atol=1e-6)
        out[nuevo] = float(np.max(np.abs(a.y_predicho.to_numpy() - b.y_predicho.to_numpy()) / np.maximum(np.abs(b.y_predicho.to_numpy()), 1)))
    return out


def graficos(anual, proc, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tinta, tinta2, fondo = '#0b0b0b', '#52514e', '#fcfcfb'
    estilo = {'ridge': ('#2a78d6', '-', 'o'), 'elastic_net': ('#eb6834', '-', 's'), 'boosting': ('#1baf7a', '-', 'D'),
              'persistencia': ('#6250d6', '--', '^'), 'media_historica': ('#8a8984', ':', 'v')}
    nombres = {'ridge': 'Ridge (alpha interno)', 'elastic_net': 'Elastic Net', 'boosting': 'HistGradientBoosting',
               'persistencia': 'Persistencia FCL(t)', 'media_historica': 'Media histórica'}
    (out / 'graficos').mkdir(parents=True, exist_ok=True)
    rutas = []
    for m in sorted(anual.moneda.unique()):
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12.5, 5), gridspec_kw={'width_ratios': [1.25, 1]})
        for p in PROCEDIMIENTOS:
            g = anual.loc[anual.moneda.eq(m) & anual.procedimiento.eq(p)].sort_values('anio_externo')
            if len(g):
                c, ls, mk = estilo[p]
                ax.plot(g.anio_externo, g.RMSE, color=c, ls=ls, lw=2, marker=mk, ms=7, mec=fondo, mew=1.5, label=nombres[p])
        ax.set_title(f'{ab._nombre(m)}: RMSE por año externo', color=tinta, loc='left')
        ax.set_xticks(list(ANIOS_EXTERNOS))
        ax.set_xlabel('Año objetivo externo')
        ax.set_ylabel('RMSE (unidad monetaria reportada)')
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:,.0f}'))
        ax.grid(axis='y', color='#e4e3df', lw=.6)
        ax.legend(frameon=False, fontsize=8)
        pr = proc.loc[proc.moneda.eq(m)].sort_values('RMSE_anual_medio', ascending=False)
        ax2.barh(range(len(pr)), pr.RMSE_anual_medio, color=[estilo[p][0] for p in pr.procedimiento], height=.6, edgecolor=fondo, linewidth=2)
        ax2.set_yticks(range(len(pr)), [nombres[p] for p in pr.procedimiento])
        for i, v in enumerate(pr.RMSE_anual_medio):
            ax2.text(v, i, f' {v:,.0f}', va='center', fontsize=8, color=tinta)
        ax2.set_title('RMSE anual medio (menor es mejor)', color=tinta, loc='left')
        ax2.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
        ax2.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v / 1e6:.1f} M'))
        ax2.set_xlim(0, pr.RMSE_anual_medio.max() * 1.3)
        for a_ in (ax, ax2):
            for s in ['top', 'right']:
                a_.spines[s].set_visible(False)
        fig.tight_layout()
        ruta = out / 'graficos' / f'comparacion_{ab._slug(m)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
    return rutas


def informe(cfg, internos, elegidos, busq, proc, res, dec, conc, excl, res_s, dec_s, respaldo, verif, tiempos, git_mod):
    nombres = {'ridge': 'Ridge', 'elastic_net': 'Elastic Net', 'boosting': 'boosting', 'persistencia': 'persistencia', 'media_historica': 'media histórica'}
    L = ['# Sprint 08 — Comparación acotada de modelos (exploratoria)', '',
         f'**Carácter.** {cfg["caracter"]} {cfg["ajuste_de_alcance"]} Solo entrenamiento (años objetivo ≤ 2021), por moneda; prueba 2022–2025 no interviene; '
         'los 26 atributos de E2 se conservan sin selección.', '', '## Respuestas', '']
    for d in dec.itertuples():
        g = res.loc[res.moneda.eq(d.moneda)]
        def linea(c, k):
            x = g.loc[g.candidato.eq(c) & g.comparador.eq(k)].iloc[0]
            return (f'{nombres[c]} frente a {nombres[k]}: RMSE {x.delta_RMSE_anual_medio_pct:+.2f} %, MAE {x.delta_MAE_anual_medio_pct:+.2f} %, '
                    f'mejor en {x.anios_mejora_RMSE}/{x.anios} años ({"cumple" if x.cumple_regla else "no cumple"} la regla)')
        sup = d.alternativa_con_superioridad_consistente if isinstance(d.alternativa_con_superioridad_consistente, str) else ''
        L += [f'### {d.moneda}', '',
              f'1. **Menor RMSE observado:** {nombres[d.menor_RMSE_anual_medio]} (orden por RMSE anual medio: {d.orden_RMSE_anual_medio}). '
              f'**Superioridad consistente frente a todos:** {nombres[sup] if sup else "ninguna"}. **Modelo vigente:** {nombres[d.modelo_vigente]}. '
              f'**Cambio recomendado:** {d.cambio_recomendado}.',
              '2. **Frente a las referencias y Ridge:** ' + '; '.join(linea(c, k) for c in ['elastic_net', 'boosting'] for k in ['media_historica', 'persistencia', 'ridge'])
              + f'. Elastic Net recomendado: {"sí" if d.elastic_net_recomendado else "no"}; boosting recomendado: {"sí" if d.boosting_recomendado else "no"}.',
              '   Ridge: ' + '; '.join(linea('ridge', k) for k in ['media_historica', 'persistencia']) + '.']
        cs = conc.loc[conc.moneda.eq(d.moneda)].set_index('procedimiento')
        ds = dec_s.loc[dec_s.moneda.eq(d.moneda)].iloc[0]
        sup_s = ds.alternativa_con_superioridad_consistente if isinstance(ds.alternativa_con_superioridad_consistente, str) else ''
        L += [f'3. **Consistencia:** la empresa con mayor error cuadrático acumula ' + ', '.join(f'{nombres[p]} {cs.loc[p, "proporcion_empresa_dominante"]:.0%}' for p in cs.index)
              + f' del error cuadrático externo (empresa más frecuente: {cs.empresa_dominante.mode().iloc[0]}). Sensibilidad descriptiva y posterior al análisis '
              f'(excluye de la evaluación a {excl[d.moneda]}, sin reajustar; no modifica la decisión): menor RMSE observado {nombres[ds.menor_RMSE_anual_medio]}, '
              f'superioridad consistente {nombres[sup_s] if sup_s else "ninguna"} (orden: {ds.orden_RMSE_anual_medio}).',
              f'4. **Conclusión:** {d.cambio_recomendado}. {d.motivo_decision}'
              + (' La conclusión se mantiene en la sensibilidad sin la empresa dominante.' if sup and sup_s == sup else
                 ' En la sensibilidad sin la empresa dominante el orden cambia; la decisión no se basa en ella.' if ds.menor_RMSE_anual_medio != d.menor_RMSE_anual_medio else '')
              + ' Exploratorio: los años externos ya se examinaron.', '']
    L += ['### Listo para cerrar el Sprint 08', '', 'Auditoría de calidad (Etapa 1), ablación individual, validación anidada y su revisión, y esta comparación, con código, '
          'pruebas, notebooks y reportes reproducibles. Pendiente fuera de este sprint: evaluar cualquier cambio de modelo en datos no examinados.', '',
          '## Protocolo (fijado antes de ejecutar)', '',
          f'- Validación: {cfg["validacion"]["interna"]}; años externos {", ".join(map(str, ANIOS_EXTERNOS))}; criterio {cfg["validacion"]["criterio"]}; sin validación aleatoria.',
          f'- Ridge: alpha {", ".join(f"{a:g}" for a in ALPHAS_RIDGE)}. Elastic Net: alpha {", ".join(map(str, EN_ALPHAS))} × l1_ratio {", ".join(map(str, EN_L1))}, '
          f'max_iter {EN_MAX_ITER}, objetivo estandarizado en cada entrenamiento. Boosting (HistGradientBoostingRegressor): max_depth {HGB_PROFUNDIDAD}, max_iter {HGB_ITERACIONES}, '
          f'l2 {HGB_L2}, learning_rate 0.05, min_samples_leaf 20, early_stopping=False, random_state={SEMILLA}, NaN nativos.',
          f'- Máximo de configuraciones: {cfg["maximo_configuraciones"]}. Desempate: {cfg["desempate"]}. Fallos: {cfg["fallos"]}.',
          f'- Regla: {cfg["regla_recomendacion"]} No es significancia estadística.',
          f'- Versiones: {cfg["versiones"]}.', '',
          '## Métricas externas por procedimiento', '',
          '| moneda | procedimiento | RMSE anual medio | MAE anual medio | RMSE concatenado | MAE concatenado |', '|---|---|---|---|---|---|']
    for r in proc.sort_values(['moneda', 'RMSE_anual_medio']).itertuples():
        L.append(f'| {r.moneda} | {r.procedimiento} | {r.RMSE_anual_medio:,.0f} | {r.MAE_anual_medio:,.0f} | {r.RMSE_concatenado:,.0f} | {r.MAE_concatenado:,.0f} |')
    L += ['', 'Promedio anual = criterio (cada año pesa igual); concatenadas = todas las predicciones externas juntas (pesan por n). Detalle por año: `metricas_por_anio.csv`; '
          'comparaciones anuales: `comparaciones_pareadas.csv`; resumen pareado completo: `resumen_comparaciones.csv`.', '',
          '## Hiperparámetros elegidos (búsqueda interna)', '', '| moneda | año externo | Ridge | Elastic Net | boosting |', '|---|---|---|---|---|']
    piv = elegidos.pivot_table(index=['moneda', 'anio_externo'], columns='modelo', values='configuracion', aggfunc='first')
    for (m, y), r in piv.iterrows():
        L.append(f'| {m} | {y} | {r.get("ridge", "")} | {r.get("elastic_net", "")} | {r.get("boosting", "")} |')
    noconv = busq.loc[~busq.valida.astype(bool)]
    en = elegidos.loc[elegidos.modelo.eq('elastic_net') & elegidos.evaluado.astype(bool)]
    en_tope = int(sum(json.loads(c)['alpha'] == max(EN_ALPHAS) for c in en.configuracion))
    hg = elegidos.loc[elegidos.modelo.eq('boosting') & elegidos.evaluado.astype(bool)]
    hg_borde = int(sum(json.loads(c)['max_iter'] == min(HGB_ITERACIONES) for c in hg.configuracion))
    L += ['', f'- Configuraciones internas descartadas por fallo o falta de convergencia: {len(noconv)} de {len(busq)}'
          + (': ' + '; '.join(f'{r.moneda} {r.anio_externo} {r.modelo} {r.configuracion} ({r.motivo})' for r in noconv.head(10).itertuples()) if len(noconv) else '')
          + f'. Ajustes externos sin convergencia: {int((~elegidos.convergio_externo.astype(bool) & elegidos.evaluado.astype(bool)).sum())}.',
          f'- Elastic Net elige el alpha máximo de su rejilla ({max(EN_ALPHAS):g}) en {en_tope} de {len(en)} años externos: su regularización óptima podría ser mayor, '
          'lo que lo acercaría a la media histórica. Boosting elige el menor número de iteraciones en '
          f'{hg_borde} de {len(hg)}. Conforme al protocolo, las rejillas no se amplían tras ver resultados; es una limitación documentada.',
          f'- Persistencia con respaldo en la media: ' + '; '.join(f'{m} {int(g.usa_respaldo_media.sum())} de {len(g)} filas' for m, g in respaldo.groupby('moneda')) + '.',
          '- Referencias y Ridge reproducen la revisión anterior (diferencia relativa máxima: ' + ', '.join(f'{k} {v:.1e}' for k, v in verif.items()) + ').',
          '- Tiempos de ajuste: `tiempos_ajuste.csv` (no deterministas; se excluyen de la comparación byte a byte).', '',
          '## Concentración del error por empresa', '', '| moneda | procedimiento | empresa dominante | proporción | top-3 |', '|---|---|---|---|---|']
    for r in conc.itertuples():
        L.append(f'| {r.moneda} | {r.procedimiento} | {r.empresa_dominante} | {r.proporcion_empresa_dominante:.1%} | {r.proporcion_top3:.1%} |')
    L += ['', '## Gráficos', ''] + [f'![{m}](graficos/comparacion_{ab._slug(m)}.png)' for m in sorted(proc.moneda.unique())] + ['',
          '## Limitaciones', '',
          '- Exploratoria: los años 2017–2021 ya se examinaron; elegir el ganador con ellos sesga a favor del ganador. No es una estimación independiente.',
          '- Cinco años externos por moneda; dólares con 21–26 filas por año. La regla no es una prueba de significancia; las empresas no son independientes entre años.',
          '- El RMSE en unidades monetarias está dominado por pocas empresas (tabla anterior); la escala monetaria no está acreditada.',
          '- Sin fechas de publicación ni vintages: persistencia y atributos suponen conocidos los estados de t al pronosticar.',
          '- Rejillas pequeñas y fijas; en soles, Ridge ya alcanzaba el máximo de su rejilla en la revisión (limitación heredada, no se amplía).',
          f'- Cambios del usuario en archivos rastreados presentes y no modificados: {", ".join(git_mod) or "ninguno"}.', '',
          '## Reproducción', '', '`python scripts/reproduce_comparacion_modelos.py`; pruebas: `python -m unittest tests.test_comparacion_modelos -v`; notebook: '
          '`notebooks/sprint_08/13_comparacion_modelos.ipynb`.']
    return '\n'.join(L) + '\n'


REPRODUCIR = """# Reproducir la comparación de modelos (Sprint 08)

```bash
conda activate tesis-fcl          # entorno existente; no requiere instalar paquetes
python scripts/reproduce_comparacion_modelos.py
python -m unittest tests.test_comparacion_modelos -v
```

Escribe `reports/sprint_08/comparacion_modelos/`. Deterministas: todo salvo `tiempos_ajuste.csv`.
Usa solo entrenamiento (años objetivo <= 2021); no lee datos de prueba ni red.
"""


def run(out=None):
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    propia = out.resolve().relative_to(ROOT).as_posix() + '/' if out.resolve().is_relative_to(ROOT) else '\0'
    archivos = lambda: {k: v for k, v in ab._archivos(excluir=(propia,)).items() if k not in PROPIOS}
    antes = archivos()
    ab.verificar_modelo_original()
    entrenamiento, cols = ab.cargar_entrenamiento()
    cfg = protocolo()
    cfg['configuraciones'] = rejillas()
    (out / 'configuracion.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')  # antes de calcular
    pred, busq, elegidos, tiempos, internos = ejecutar(entrenamiento, cols)
    verif = verificar_contra_revision(pred)
    anual = metricas_anuales(pred)
    comp = comparaciones(anual)
    res = resumen(anual, comp, pred)
    proc = resumen_procedimientos(anual, pred)
    dec = decision(res, proc)
    conc = concentracion(pred)
    excl, res_s, dec_s = sensibilidad_empresa(pred, conc)
    externos = (pred.loc[pred.procedimiento.eq('media_historica')].groupby(['moneda', 'anio_objetivo'])
                .agg(n_externo=('id_fila', 'size'), empresas_externo=('RPJ', 'nunique')).reset_index().rename(columns={'anio_objetivo': 'anio_externo'}))
    respaldo = pred.loc[pred.procedimiento.eq('persistencia')]
    rutas = graficos(anual, proc, out)
    assert antes == archivos(), 'La comparación modificó archivos previos'
    try:
        git_mod = [x[3:] for x in subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain', '--untracked-files=no'],
                                                 capture_output=True, text=True, check=True).stdout.splitlines()]
    except (OSError, subprocess.CalledProcessError):
        git_mod = []
    salidas = {'pliegues_externos.csv': externos, 'pliegues_internos.csv': internos, 'busquedas_internas.csv': busq, 'hiperparametros_elegidos.csv': elegidos,
               'predicciones_externas.csv': pred, 'metricas_por_anio.csv': anual, 'comparaciones_pareadas.csv': comp, 'resumen_comparaciones.csv': res,
               'resumen_procedimientos.csv': proc, 'decision.csv': dec, 'concentracion_error.csv': conc, 'sensibilidad_empresa_dominante.csv': res_s,
               'decision_sin_empresa_dominante.csv': dec_s.assign(empresa_excluida=dec_s.moneda.map(excl))}
    for nombre, t in salidas.items():
        t.to_csv(out / nombre, index=False, float_format='%.15g')
    tiempos.to_csv(out / 'tiempos_ajuste.csv', index=False, float_format='%.4f')
    (out / 'integridad.json').write_text(json.dumps(dict(archivos_verificados=len(antes), sin_cambios_durante_ejecucion=True, git_modificados_previos=git_mod,
                                                         filas_entrenamiento=len(entrenamiento), filas_prueba_usadas=0, reproduccion_revision=verif),
                                                    ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (out / 'informe_comparacion.md').write_text(informe(cfg, internos, elegidos, busq, proc, res, dec, conc, excl, res_s, dec_s, respaldo, verif, tiempos, git_mod),
                                                encoding='utf-8')
    (out / 'REPRODUCIR.md').write_text(REPRODUCIR, encoding='utf-8')
    return dict(salidas, tiempos=tiempos, graficos=rutas, configuracion=cfg)
