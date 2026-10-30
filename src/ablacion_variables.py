"""Sprint 08 — Etapa 2: ablación individual de los 26 atributos de E2 con validación temporal.

Solo se usan filas de entrenamiento (anio_objetivo <= 2021). Los pliegues reproducen la regla
de Sprint 06 (notebooks/08_mejoras_baseline.ipynb, celda 16): ventanas expansivas por año
objetivo y bloques de validación de dos años desde el noveno año. Cada variante y pliegue usa
un Pipeline nuevo con la preparación E2 del notebook 07, ajustado solo con su entrenamiento.
La regla de clasificación se fijó en este módulo antes de ejecutar el análisis.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import src.auditoria_calidad as ac

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/sprint_08/ablacion'
NB07 = ROOT / 'notebooks/07_baseline_variantes.ipynb'
NB08 = ROOT / 'notebooks/08_mejoras_baseline.ipynb'
PROPIOS = {'src/ablacion_variables.py', 'scripts/reproduce_ablacion_variables.py', 'tests/test_ablacion_variables.py',
           'notebooks/sprint_08/12_ablacion_variables.ipynb'}
IGNORADOS = {'.git', '.cache', '__pycache__', '.ipynb_checkpoints'}

ANIO_OBJETIVO_MAX_TRAIN = 2021
ALPHA = 1.0
# Regla de pliegues de Sprint 06: 8 años de calentamiento si hay >= 12 años; bloques de 2 años.
CALENTAMIENTO, BLOQUE = 8, 2
REFERENCIA = 'referencia_26'

# Protocolo de clasificación (fijado antes de examinar resultados; umbrales exploratorios).
TOLERANCIA_EMPATE_REL = 1e-6      # |delta| <= 1e-6 x error de referencia se considera empate numérico
UMBRAL_PRACTICO_PCT = 1.0         # cambio mínimo del RMSE anual medio para considerarlo relevante (exploratorio)
FRACCION_ANIOS_CONSISTENCIA = 0.75  # proporción mínima de años evaluables en la misma dirección


def separar_entrenamiento(panel):
    """Primera operación tras cargar el panel: solo filas elegibles de entrenamiento."""
    t = panel.loc[panel.utilizable_supervisado & panel.particion.eq('entrenamiento')].copy()
    t['id_fila'] = t.index
    assert t.anio_objetivo.le(ANIO_OBJETIVO_MAX_TRAIN).all() and t.objetivo_fcl_t1.notna().all()
    assert t.Moneda.eq(t.moneda_objetivo).all() and t.anio_objetivo.eq(t.Ejercicio + 1).all()
    return t


def cargar_entrenamiento():
    """Panel verificado por Sprint 08 Etapa 1 (reconstrucción exacta); se descarta todo salvo entrenamiento."""
    panel, cols, _ = ac.load_inputs()
    entrenamiento = separar_entrenamiento(panel)
    del panel
    assert len(entrenamiento) == 2869
    return entrenamiento, cols


def verificar_modelo_original():
    """Contrasta la especificación con el código literal del notebook 07 (sin ejecutarlo)."""
    spec = ac.especificacion_e2()
    nb = json.loads(NB07.read_text(encoding='utf-8'))
    fuente = re.sub(r'\s', '', ''.join(nb['cells'][int(spec['evidencia']['preparacion'].split('celda ')[1].split()[0])]['source']))
    for patron in ['SimpleImputer(strategy="median",keep_empty_features=True)', 'StandardScaler()ifescala=="standard"', 'Ridge(alpha=ALPHA,solver="svd",fit_intercept=True)',
                   'remainder="drop"', 'modelo.fit(tr[cols],tr.objetivo_fcl_t1)']:
        assert patron in fuente, patron
    assert spec['alpha'] == ALPHA
    texto = ''.join(json.loads(NB08.read_text(encoding='utf-8'))['cells'][16]['source'])
    for patron in ['warmup=8 if len(years)>=12', 'range(warmup,len(years),2)', 'valyears=years[inicio:inicio+2];trainyears=years[:inicio]']:
        assert patron in texto, patron
    return spec


def crear_modelo(columnas, alpha=ALPHA):
    """Réplica de crear_modelo(columnas, 'standard') del notebook 07; alpha solo cambia en la validación anidada."""
    numerico = Pipeline([('imputer', SimpleImputer(strategy='median', keep_empty_features=True)), ('scaler', StandardScaler())])
    preparador = ColumnTransformer([('numericas', numerico, columnas)], remainder='drop', verbose_feature_names_out=False)
    return Pipeline([('preparacion', preparador), ('ridge', Ridge(alpha=alpha, solver='svd', fit_intercept=True))])


def pliegues(entrenamiento):
    """Pliegues por moneda con la regla de Sprint 06 (cohorte 'todas')."""
    out = {}
    for moneda, t in entrenamiento.groupby('Moneda', sort=True):
        anios = sorted(t.anio_objetivo.unique())
        calentamiento = CALENTAMIENTO if len(anios) >= 12 else max(4, len(anios) - 4)
        lista = []
        for inicio in range(calentamiento, len(anios), BLOQUE):
            val, ent = anios[inicio:inicio + BLOQUE], anios[:inicio]
            idx_tr = t.index[t.anio_objetivo.isin(ent)].tolist()
            idx_va = t.index[t.anio_objetivo.isin(val)].tolist()
            assert idx_tr and idx_va and max(ent) < min(val) and not set(idx_tr) & set(idx_va)
            lista.append(dict(fold=len(lista) + 1, anios_train=[int(a) for a in ent], anios_validacion=[int(a) for a in val],
                              idx_train=idx_tr, idx_validacion=idx_va))
        out[moneda] = lista
    return out


def tabla_pliegues(entrenamiento, folds):
    filas, anuales = [], []
    for moneda, lista in folds.items():
        for f in lista:
            tr, va = entrenamiento.loc[f['idx_train']], entrenamiento.loc[f['idx_validacion']]
            filas.append(dict(moneda=moneda, fold=f['fold'], anios_objetivo_train=f'{min(f["anios_train"])}-{max(f["anios_train"])}',
                              anios_objetivo_validacion=';'.join(map(str, f['anios_validacion'])),
                              n_train=len(tr), empresas_train=tr.RPJ.nunique(), n_validacion=len(va), empresas_validacion=va.RPJ.nunique(),
                              evaluable=True, motivo=''))
            for anio, g in va.groupby('anio_objetivo'):
                anuales.append(dict(moneda=moneda, fold=f['fold'], anio_validacion=int(anio), n=len(g), empresas=g.RPJ.nunique()))
        anios_tr = sorted(entrenamiento.loc[entrenamiento.Moneda.eq(moneda), 'anio_objetivo'].unique())
        primeros = [a for a in anios_tr if a < min(lista[0]['anios_validacion'])]
        filas.append(dict(moneda=moneda, fold=0, anios_objetivo_train='', anios_objetivo_validacion=f'{min(primeros)}-{max(primeros)}',
                          n_train=0, empresas_train=0, n_validacion=int(entrenamiento.Moneda.eq(moneda).sum() - sum(len(f['idx_validacion']) for f in lista)),
                          empresas_validacion=0, evaluable=False,
                          motivo='Años de calentamiento: solo entrenan; no tienen historia previa suficiente para validarse (regla Sprint 06)'))
    return pd.DataFrame(filas).sort_values(['moneda', 'fold']).reset_index(drop=True), pd.DataFrame(anuales)


def variantes(cols):
    v = {REFERENCIA: (None, list(cols))}
    for c in cols:
        v[f'sin_{c}'] = (c, [x for x in cols if x != c])
    return v


def ajustar_y_predecir(tr, va, columnas):
    """Pipeline nuevo por variante y pliegue; verifica que imputación y escalado provienen solo de tr."""
    modelo = crear_modelo(columnas).fit(tr[columnas], tr.objetivo_fcl_t1)
    num = modelo.named_steps['preparacion'].named_transformers_['numericas']
    imp, esc = num.named_steps['imputer'], num.named_steps['scaler']
    np.testing.assert_allclose(imp.statistics_, tr[columnas].median().fillna(0).to_numpy(), rtol=1e-12)
    z = imp.transform(tr[columnas])
    np.testing.assert_allclose(esc.mean_, z.mean(axis=0), rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(esc.var_, z.var(axis=0), rtol=1e-12, atol=1e-12)
    assert int(esc.n_samples_seen_) == len(tr) and list(modelo.named_steps['preparacion'].feature_names_in_) == columnas
    p = modelo.predict(va[columnas])
    assert np.isfinite(p).all()
    return modelo, p


def metricas(y, p):
    e = np.asarray(p, float) - np.asarray(y, float)
    return dict(n=len(e), RMSE=float(np.sqrt(np.mean(e ** 2))), MAE=float(np.mean(np.abs(e))))


def ejecutar(entrenamiento, cols, extras=None):
    """Referencia + 26 ablaciones (+ variantes extra) por moneda y pliegue. Recibe solo entrenamiento."""
    assert entrenamiento.particion.eq('entrenamiento').all() and entrenamiento.utilizable_supervisado.all()
    assert entrenamiento.anio_objetivo.le(ANIO_OBJETIVO_MAX_TRAIN).all()
    folds = pliegues(entrenamiento)
    todas = variantes(cols)
    todas.update(extras or {})
    preds, ajustes = [], []
    ident = ['id_fila', 'RPJ', 'Ejercicio', 'anio_objetivo', 'Moneda']
    for moneda, lista in folds.items():
        for f in lista:
            tr, va = entrenamiento.loc[f['idx_train']], entrenamiento.loc[f['idx_validacion']]
            assert tr.anio_objetivo.max() < va.anio_objetivo.min() and tr.Moneda.eq(moneda).all() and va.Moneda.eq(moneda).all()
            for nombre, (retirado, columnas) in todas.items():
                _, p = ajustar_y_predecir(tr, va, columnas)
                g = va[ident].copy()
                g.insert(0, 'variante', nombre)
                g.insert(1, 'atributo_retirado', retirado if isinstance(retirado, str) else ('' if retirado is None else ';'.join(retirado)))
                g['fold'] = f['fold']
                g['y_real'] = va.objetivo_fcl_t1.to_numpy()
                g['y_predicho'] = p
                preds.append(g)
                ajustes.append(dict(variante=nombre, moneda=moneda, fold=f['fold'], n_predictores=len(columnas), n_train=len(tr), n_validacion=len(va),
                                    anio_train_max=int(tr.anio_objetivo.max()), anio_validacion_min=int(va.anio_objetivo.min()),
                                    hash_ids_train=hashlib.sha256(np.asarray(f['idx_train']).tobytes()).hexdigest()[:16],
                                    hash_ids_validacion=hashlib.sha256(np.asarray(f['idx_validacion']).tobytes()).hexdigest()[:16],
                                    imputacion_y_escalado_verificados_train=True))
    pred = pd.concat(preds, ignore_index=True).rename(columns={'Moneda': 'moneda'})
    return pred, pd.DataFrame(ajustes), folds


def metricas_por_anio(pred):
    filas = [dict(variante=k[0], atributo_retirado=k[1], moneda=k[2], fold=k[3], anio_validacion=int(k[4]), **metricas(g.y_real, g.y_predicho))
             for k, g in pred.groupby(['variante', 'atributo_retirado', 'moneda', 'fold', 'anio_objetivo'], sort=True)]
    return pd.DataFrame(filas)


def _pct(delta, ref):
    """Cambio porcentual; indefinido (NaN) si el error de referencia es cero."""
    ref = np.asarray(ref, float)
    return np.where(ref != 0, 100 * np.asarray(delta, float) / np.where(ref != 0, ref, 1), np.nan)


def _direccion(delta, ref):
    tol = TOLERANCIA_EMPATE_REL * np.abs(ref)
    return np.where(delta < -tol, 'mejora', np.where(delta > tol, 'empeora', 'empate'))


def comparaciones(m):
    ref = m.loc[m.variante.eq(REFERENCIA), ['moneda', 'anio_validacion', 'n', 'RMSE', 'MAE']].rename(
        columns={'n': 'n_ref', 'RMSE': 'RMSE_referencia', 'MAE': 'MAE_referencia'})
    c = m.loc[m.variante.ne(REFERENCIA)].merge(ref, on=['moneda', 'anio_validacion'], validate='many_to_one')
    assert c.n.eq(c.n_ref).all()
    c = c.drop(columns='n_ref').rename(columns={'RMSE': 'RMSE_sin_variable', 'MAE': 'MAE_sin_variable'})
    for x in ['RMSE', 'MAE']:
        c[f'delta_{x}'] = c[f'{x}_sin_variable'] - c[f'{x}_referencia']
        c[f'delta_{x}_pct'] = _pct(c[f'delta_{x}'], c[f'{x}_referencia'])
        c[f'direccion_{x}'] = _direccion(c[f'delta_{x}'], c[f'{x}_referencia'])
    return c


def clasificar(r):
    """Regla declarada: ver configuracion.json. Devuelve (clase, motivo)."""
    minimo = math.ceil(FRACCION_ANIOS_CONSISTENCIA * r['anios_evaluables'])
    rmse_mejora = r['delta_RMSE_medio_pct'] <= -UMBRAL_PRACTICO_PCT and r['anios_mejora_RMSE'] >= minimo and r['mediana_delta_RMSE_anual'] < 0
    rmse_empeora = r['delta_RMSE_medio_pct'] >= UMBRAL_PRACTICO_PCT and r['anios_empeora_RMSE'] >= minimo and r['mediana_delta_RMSE_anual'] > 0
    mae_tol = TOLERANCIA_EMPATE_REL * 100
    if rmse_mejora and r['delta_MAE_medio_pct'] <= mae_tol:
        return 'Candidata a retirar', f'RMSE anual medio {r["delta_RMSE_medio_pct"]:.2f}% y mejora en {r["anios_mejora_RMSE"]}/{r["anios_evaluables"]} años; MAE no empeora'
    if rmse_empeora and r['delta_MAE_medio_pct'] >= -mae_tol:
        return 'Conservar', f'RMSE anual medio +{r["delta_RMSE_medio_pct"]:.2f}% y empeora en {r["anios_empeora_RMSE"]}/{r["anios_evaluables"]} años; MAE no mejora'
    motivos = []
    if rmse_mejora or rmse_empeora:
        motivos.append(f'conflicto: RMSE {"mejora" if rmse_mejora else "empeora"} de forma consistente pero MAE anual medio cambia {r["delta_MAE_medio_pct"]:+.2f}%')
    if abs(r['delta_RMSE_medio_pct']) < UMBRAL_PRACTICO_PCT:
        motivos.append(f'cambio del RMSE anual medio {r["delta_RMSE_medio_pct"]:+.2f}% menor que el umbral exploratorio de {UMBRAL_PRACTICO_PCT:g}%')
    elif not (rmse_mejora or rmse_empeora):
        motivos.append(f'dirección inestable: mejora {r["anios_mejora_RMSE"]}, empeora {r["anios_empeora_RMSE"]}, empate {r["anios_empate_RMSE"]} de {r["anios_evaluables"]} años (mínimo {minimo})')
    return 'Resultado incierto', '; '.join(motivos)


def resumen(c, pred):
    filas = []
    ref_pred = pred.loc[pred.variante.eq(REFERENCIA)].set_index(['moneda', 'id_fila'])
    for (variante, retirado, moneda), g in c.groupby(['variante', 'atributo_retirado', 'moneda'], sort=False):
        r = dict(variante=variante, atributo_retirado=retirado, moneda=moneda, anios_evaluables=len(g), n_validacion=int(g.n.sum()))
        for x in ['RMSE', 'MAE']:
            ref_m, var_m = g[f'{x}_referencia'].mean(), g[f'{x}_sin_variable'].mean()
            r.update({f'{x}_anual_medio_referencia': ref_m, f'{x}_anual_medio_sin_variable': var_m, f'delta_{x}_medio': var_m - ref_m,
                      f'delta_{x}_medio_pct': float(_pct(var_m - ref_m, ref_m)), f'mediana_delta_{x}_anual': g[f'delta_{x}'].median(),
                      f'mediana_delta_{x}_anual_pct': g[f'delta_{x}_pct'].median(),
                      f'anios_mejora_{x}': int(g[f'direccion_{x}'].eq('mejora').sum()), f'anios_empeora_{x}': int(g[f'direccion_{x}'].eq('empeora').sum()),
                      f'anios_empate_{x}': int(g[f'direccion_{x}'].eq('empate').sum())})
            r[f'proporcion_anios_mejora_{x}'] = r[f'anios_mejora_{x}'] / len(g)
        # Diagnóstico descriptivo (no interviene en la regla): concentración del cambio en un año.
        absd = g.delta_RMSE.abs()
        r['anio_dominante_RMSE'] = int(g.loc[absd.idxmax(), 'anio_validacion'])
        r['concentracion_anio_dominante'] = float(absd.max() / absd.sum()) if absd.sum() > 0 else np.nan
        r['mediana_anual_supera_umbral'] = bool(abs(r['mediana_delta_RMSE_anual_pct']) >= UMBRAL_PRACTICO_PCT)
        r['anios_que_mejora_RMSE'] = ';'.join(map(str, g.loc[g.direccion_RMSE.eq('mejora'), 'anio_validacion']))
        r['anios_que_empeora_RMSE'] = ';'.join(map(str, g.loc[g.direccion_RMSE.eq('empeora'), 'anio_validacion']))
        v = pred.loc[pred.variante.eq(variante) & pred.moneda.eq(moneda)]
        ref = ref_pred.loc[[(moneda, i) for i in v.id_fila]]
        assert np.array_equal(ref.y_real.to_numpy(), v.y_real.to_numpy())
        for nombre, serie in [('referencia', ref.y_predicho), ('sin_variable', v.y_predicho)]:
            mm = metricas(v.y_real, serie)
            r[f'RMSE_concatenado_{nombre}'], r[f'MAE_concatenado_{nombre}'] = mm['RMSE'], mm['MAE']
        for x in ['RMSE', 'MAE']:
            d = r[f'{x}_concatenado_sin_variable'] - r[f'{x}_concatenado_referencia']
            r[f'delta_{x}_concatenado'], r[f'delta_{x}_concatenado_pct'] = d, float(_pct(d, r[f'{x}_concatenado_referencia']))
        r['clasificacion'], r['motivo'] = clasificar(r)
        filas.append(r)
    return pd.DataFrame(filas)


def sensibilidad_caso_dominante(pred):
    """Post hoc (no altera la clasificación). Solo cambia la evaluación, no reajusta modelos: excluye de todas las
    variantes (a) la observación con mayor error absoluto de la referencia en cada moneda y (b) todas las
    observaciones de validación de esa empresa; luego reaplica la misma regla."""
    ref = pred.loc[pred.variante.eq(REFERENCIA)].assign(error_abs=lambda x: (x.y_predicho - x.y_real).abs())
    casos = ref.loc[ref.groupby('moneda').error_abs.idxmax(), ['moneda', 'id_fila', 'RPJ', 'Ejercicio', 'anio_objetivo', 'fold', 'y_real', 'y_predicho', 'error_abs']]
    obs, emp = set(zip(casos.moneda, casos.id_fila)), set(zip(casos.moneda, casos.RPJ))
    salidas = []
    for nombre, mascara in [('sin_observacion_dominante', [k not in obs for k in zip(pred.moneda, pred.id_fila)]),
                            ('sin_empresa_dominante', [k not in emp for k in zip(pred.moneda, pred.RPJ)])]:
        p = pred.loc[mascara]
        salidas.append(resumen(comparaciones(metricas_por_anio(p)), p).assign(sensibilidad=nombre))
    return pd.concat(salidas, ignore_index=True), casos.reset_index(drop=True)


def concentracion_error_referencia(pred):
    """Descriptivo: observación con mayor error de la referencia en cada año y su peso en el error cuadrático del año."""
    ref = pred.loc[pred.variante.eq(REFERENCIA)].assign(sq=lambda x: (x.y_predicho - x.y_real) ** 2)
    filas = []
    for (moneda, anio), g in ref.groupby(['moneda', 'anio_objetivo']):
        r = g.loc[g.sq.idxmax()]
        filas.append(dict(moneda=moneda, anio_validacion=int(anio), n=len(g), RPJ=r.RPJ, Ejercicio=int(r.Ejercicio), y_real=r.y_real,
                          y_predicho=r.y_predicho, proporcion_error_cuadratico_del_anio=float(r.sq / g.sq.sum())))
    return pd.DataFrame(filas)


def configuracion(cols, spec):
    return {
        'pregunta': '¿Retirar una variable reduce el error de predicción de forma consistente en validación temporal dentro de entrenamiento?',
        'alcance': 'Conclusiones limitadas a Ridge(alpha=1.0) con mediana + StandardScaler, por moneda, objetivo FCL_preliminar(t+1) y años objetivo de validación 2014–2021.',
        'atributos_E2': cols, 'grupos': {g: spec[k] for g, k in [('financieros', 'financieros'), ('macroeconomicos', 'macroeconomicos'), ('bursatiles', 'bursatiles')]},
        'objetivo': spec['objetivo'],
        'modelo': {'pipeline': "Pipeline([('preparacion', ColumnTransformer([('numericas', Pipeline([('imputer', SimpleImputer(strategy='median', "
                               "keep_empty_features=True)), ('scaler', StandardScaler())]), columnas)], remainder='drop')), ('ridge', Ridge(alpha=1.0, solver='svd', fit_intercept=True))])",
                   'por_moneda': True, 'nuevo_pipeline_por_variante_y_pliegue': True, 'hiperparametros_fijos': True,
                   'evidencia': spec['evidencia']['preparacion'] + '; ' + spec['evidencia']['listas_E0_E1_E2']},
        'datos': 'panel_financiero_macro_bursatil.csv verificado por src/auditoria_calidad.load_inputs; se retienen solo filas utilizable_supervisado y particion == entrenamiento (anio_objetivo <= 2021).',
        'pliegues': {'origen': 'notebooks/08_mejoras_baseline.ipynb celda 16 (cohorte todas); tamaños contrastados con reports/sprint_06/mejoras/cv_folds.csv',
                     'regla': f'Años objetivo ordenados; calentamiento {CALENTAMIENTO} años (si hay >= 12); bloques de validación de {BLOQUE} años; entrenamiento expansivo con todos los años anteriores al bloque.',
                     'unidad_de_validacion': 'año objetivo', 'aleatorio': False},
        'metricas': {'delta_RMSE': 'RMSE_sin_variable - RMSE_referencia', 'delta_MAE': 'MAE_sin_variable - MAE_referencia',
                     'delta_porcentual': '100 x (error_sin_variable - error_referencia) / error_referencia; indefinido si error_referencia = 0',
                     'signo': 'negativo = retirar la variable reduce el error',
                     'criterio_principal': 'promedio simple del RMSE anual (cada año evaluable pesa igual)', 'complementaria': 'promedio simple del MAE anual',
                     'concatenadas': 'RMSE y MAE sobre todas las predicciones de validación juntas (pondera años por n); no son el criterio de clasificación'},
        'clasificacion': {
            'tolerancia_empate_relativa': TOLERANCIA_EMPATE_REL,
            'umbral_practico_pct_exploratorio': UMBRAL_PRACTICO_PCT,
            'fraccion_anios_consistencia': FRACCION_ANIOS_CONSISTENCIA,
            'candidata_a_retirar': 'delta_RMSE_medio_pct <= -1 Y años con mejora de RMSE >= ceil(0.75 x años evaluables) Y mediana anual de delta_RMSE < 0 Y delta_MAE_medio_pct <= tolerancia',
            'conservar': 'delta_RMSE_medio_pct >= +1 Y años con empeoramiento de RMSE >= ceil(0.75 x años) Y mediana anual de delta_RMSE > 0 Y delta_MAE_medio_pct >= -tolerancia',
            'resultado_incierto': 'cualquier otro caso: cambio menor que el umbral, dirección inestable entre años o conflicto entre RMSE y MAE',
            'nota': 'El umbral de 1% y la fracción 0.75 son decisiones exploratorias, no reglas universales. Fijadas antes de ejecutar el análisis.'},
        'retirada_conjunta': 'Por moneda, retirar juntas todas las candidatas de esa moneda; mismos pliegues, filas, modelo e hiperparámetros. Exploratoria: las candidatas se eligieron con la misma validación.',
        'supuestos': ['Se reutiliza la cohorte "todas" de Sprint 06; no se usan cohortes sectoriales.',
                      'Las métricas monetarias están en la unidad reportada de cada moneda; nunca se agregan entre monedas.',
                      'Un año de validación pertenece a un único pliegue; los años del mismo bloque comparten modelo.'],
    }


def _archivos(excluir=('reports/sprint_08/ablacion/',)):
    out = {}
    for p in ROOT.rglob('*'):
        rel = p.relative_to(ROOT)
        if p.is_file() and not IGNORADOS.intersection(rel.parts) and not rel.as_posix().startswith(excluir) and rel.as_posix() not in PROPIOS:
            out[rel.as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def verificar_replica_sprint06(entrenamiento, cols):
    """Ajuste con todo el entrenamiento: debe reproducir las predicciones E2 de entrenamiento del notebook 07."""
    p07 = pd.read_csv(ROOT / 'reports/sprint_06/predicciones_baseline.csv', dtype={'RPJ': 'string', 'RUC': 'string'}, float_precision='round_trip')
    p07 = p07.loc[p07.particion.eq('entrenamiento') & p07.escenario.eq('principal') & p07.experimento.eq('E2_bursatil')]
    out = {}
    for moneda, t in entrenamiento.groupby('Moneda'):
        _, p = ajustar_y_predecir(t, t, cols)
        ref = p07.set_index('id_fila').loc[t.id_fila, 'y_predicho'].to_numpy()
        out[moneda] = float(np.max(np.abs(p - ref) / np.maximum(np.abs(ref), 1)))
        np.testing.assert_allclose(p, ref, rtol=1e-9, atol=1e-6)
    return out


def graficos(resumen_df, comp, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    tinta, tinta2, fondo = '#0b0b0b', '#52514e', '#fcfcfb'
    azul, naranja = '#2a78d6', '#eb6834'
    divergente = LinearSegmentedColormap.from_list('div', ['#1c5cab', '#86b6ef', '#f0efec', '#f09b9a', '#b8302f'])
    plt.rcParams.update({'font.size': 9, 'axes.edgecolor': tinta2, 'axes.labelcolor': tinta, 'xtick.color': tinta2, 'ytick.color': tinta2,
                         'figure.facecolor': fondo, 'axes.facecolor': fondo, 'savefig.facecolor': fondo})
    (out / 'graficos').mkdir(exist_ok=True)
    rutas = []
    for moneda, g in resumen_df.groupby('moneda'):
        g = g.sort_values('delta_RMSE_medio_pct')
        fig, ax = plt.subplots(figsize=(8, 7.5))
        y = np.arange(len(g))
        ax.axvline(0, color=tinta2, lw=1)
        for u in (-UMBRAL_PRACTICO_PCT, UMBRAL_PRACTICO_PCT):
            ax.axvline(u, color=tinta2, lw=.8, ls=':')
        ax.scatter(g.delta_RMSE_medio_pct, y, s=36, color=azul, label='RMSE anual medio (criterio principal)', zorder=3, edgecolor=fondo, linewidth=1.5)
        ax.scatter(g.delta_MAE_medio_pct, y, s=36, color=naranja, marker='D', label='MAE anual medio (complementaria)', zorder=3, edgecolor=fondo, linewidth=1.5)
        ax.set_yticks(y, [f'{a}  [{ETIQUETAS[c]}]' for a, c in zip(g.atributo_retirado, g.clasificacion)])
        ax.set_xlabel('Cambio % del error al retirar la variable (negativo = mejora)')
        ax.set_title(f'{_nombre(moneda)}: efecto de retirar cada atributo (validación 2014–2021)', color=tinta, loc='left')
        ax.grid(axis='x', color='#e4e3df', lw=.6)
        ax.legend(loc='upper left', frameon=False)
        fig.text(0.01, 0.01, 'Líneas punteadas: umbral exploratorio ±1 %. [cand.] candidata a retirar, [cons.] conservar, [inc.] incierto.',
                 color=tinta2, fontsize=8)
        for s in ['top', 'right']:
            ax.spines[s].set_visible(False)
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        ruta = out / 'graficos' / f'delta_error_{_slug(moneda)}.png'
        fig.savefig(ruta, dpi=150)
        plt.close(fig)
        rutas.append(ruta)
        h = comp.loc[comp.moneda.eq(moneda) & comp.variante.str.startswith('sin_')].pivot(index='atributo_retirado', columns='anio_validacion', values='delta_RMSE_pct')
        h = h.loc[g.atributo_retirado]
        lim = max(float(np.nanpercentile(np.abs(h.to_numpy()), 98)), 1.0)
        fig, ax = plt.subplots(figsize=(8, 7.5))
        im = ax.imshow(h.to_numpy(), cmap=divergente, norm=TwoSlopeNorm(0, -lim, lim), aspect='auto')
        ax.set_xticks(range(h.shape[1]), h.columns)
        ax.set_yticks(range(h.shape[0]), h.index)
        for i in range(h.shape[0]):
            for j in range(h.shape[1]):
                val = h.iat[i, j]
                ax.text(j, i, f'{val:+.1f}', ha='center', va='center', fontsize=6.5, color=tinta if abs(val) < .6 * lim else fondo)
        ax.set_xlabel('Año objetivo de validación')
        ax.set_title(f'{_nombre(moneda)}: cambio % del RMSE por año al retirar cada atributo', color=tinta, loc='left')
        cb = fig.colorbar(im, ax=ax, shrink=.8)
        cb.set_label('% (azul = mejora, rojo = empeora; escala recortada al p98)')
        fig.tight_layout()
        ruta = out / 'graficos' / f'estabilidad_anual_{_slug(moneda)}.png'
        fig.savefig(ruta, dpi=150)
        plt.close(fig)
        rutas.append(ruta)
    return rutas


ETIQUETAS = {'Candidata a retirar': 'cand.', 'Conservar': 'cons.', 'Resultado incierto': 'inc.'}


def _nombre(moneda):
    return 'Soles' if moneda == 'Soles' else 'Dólares'


def _slug(moneda):
    return 'soles' if moneda == 'Soles' else 'dolares'


def _md_tabla(df):
    cols = list(df.columns)
    lineas = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    for r in df.itertuples(index=False):
        lineas.append('| ' + ' | '.join(f'{x:.2f}' if isinstance(x, float) else str(x) for x in r) + ' |')
    return '\n'.join(lineas)


def informe(cfg, tpl, res, conj, comp, replica, integridad, sens, casos_dom, conc):
    L = ['# Sprint 08 — Etapa 2: ablación individual de los 26 atributos de E2', '',
         f'**Pregunta.** {cfg["pregunta"]} **Alcance.** {cfg["alcance"]} No se afirma que una variable sea inútil para otros modelos, configuraciones o periodos.', '',
         '## 1. Método', '',
         '- **Datos:** solo entrenamiento (2.869 filas, años objetivo 2006–2021); el panel se carga, se verifica y se separa de inmediato. Prueba 2022–2025 no participa en filas, objetivos, predicciones ni métricas.',
         f'- **Modelo:** {cfg["modelo"]["pipeline"]}, uno por moneda, nuevo para cada variante y pliegue. Réplica verificada: con todo el entrenamiento reproduce las predicciones E2 de entrenamiento del notebook 07 (diferencia relativa máxima: '
         + ', '.join(f'{m} {v:.1e}' for m, v in replica.items()) + ').',
         f'- **Pliegues:** {cfg["pliegues"]["regla"]} Origen: {cfg["pliegues"]["origen"]}. Los ocho primeros años objetivo (2006–2013) solo entrenan.',
         '- **Métricas:** delta = error sin la variable − error de referencia (negativo = mejora); cambio % = 100·delta/referencia. Criterio principal: promedio simple del RMSE anual de los 8 años 2014–2021; MAE anual medio complementario; métricas concatenadas como contraste (ponderan por n).',
         f'- **Regla de clasificación (fijada antes de ejecutar):** candidata si el RMSE anual medio baja ≥ {UMBRAL_PRACTICO_PCT:g} %, mejora en ≥ 6 de 8 años, la mediana anual es negativa y el MAE anual medio no empeora; conservar con la condición simétrica; incierto en otro caso. Empate: |delta| ≤ {TOLERANCIA_EMPATE_REL:g} × error de referencia. El 1 % y el 75 % son umbrales exploratorios.', '',
         '## Síntesis', '',
         *[f'- **{m}:** candidatas bajo la regla principal: ' + (', '.join(f'`{a}`' for a in g.loc[g.clasificacion.eq('Candidata a retirar'), 'atributo_retirado']) or 'ninguna')
           + '; también candidatas al excluir la observación y la empresa dominantes: ' + (', '.join(f'`{a}`' for a in g.loc[g.candidata_robusta_a_casos_dominantes, 'atributo_retirado']) or 'ninguna') + '.'
           for m, g in res.groupby('moneda', sort=False)],
         '- Ninguna conclusión justifica retirar variables todavía: el RMSE anual depende de pocas empresas ('
         + '; '.join(f'{m}: ' + ', '.join(f'{rpj} en {n} año(s)' for rpj, n in g.loc[g.proporcion_error_cuadratico_del_anio.ge(.5)].RPJ.value_counts().items())
                     for m, g in conc.groupby('moneda'))
         + ' concentran ≥ 50 % del error cuadrático del año) y las candidatas se eligieron con la misma validación. Son hipótesis para confirmar con datos independientes.',
         '- Problemas de calidad del dato (Etapa 1) y perjuicio predictivo son cosas distintas: aquí solo se mide el efecto marginal sobre el error de este Ridge.', '',
         '## 2. Pliegues y tamaños', '', _md_tabla(tpl[['moneda', 'fold', 'anios_objetivo_train', 'anios_objetivo_validacion', 'n_train', 'empresas_train', 'n_validacion', 'empresas_validacion', 'evaluable']]), '']
    for moneda, g in res.groupby('moneda', sort=False):
        g = g.sort_values('delta_RMSE_medio_pct')
        cand, cons, inc = (g.loc[g.clasificacion.eq(x)] for x in ['Candidata a retirar', 'Conservar', 'Resultado incierto'])
        L += [f'## 3. Resultados — {moneda}', '',
              f'Referencia (26 atributos): RMSE anual medio {g.RMSE_anual_medio_referencia.iloc[0]:,.0f}; MAE anual medio {g.MAE_anual_medio_referencia.iloc[0]:,.0f}; '
              f'RMSE concatenado {g.RMSE_concatenado_referencia.iloc[0]:,.0f}; MAE concatenado {g.MAE_concatenado_referencia.iloc[0]:,.0f} (unidad monetaria reportada).', '',
              f'1. **Candidatas a retirar:** ' + (', '.join(
                  f'`{r.atributo_retirado}`' + ('' if r.mediana_anual_supera_umbral else
                                                f' (mejora concentrada: mediana anual {r.mediana_delta_RMSE_anual_pct:+.2f} %, {r.concentracion_anio_dominante:.0%} del cambio absoluto en {r.anio_dominante_RMSE})')
                  for r in cand.itertuples()) if len(cand) else 'ninguna. No hay evidencia consistente, bajo la regla declarada, para retirar variables en esta moneda.'),
              f'2. **Cambio de RMSE y MAE al retirar cada variable:** tabla siguiente (y `resumen_ablacion.csv`).',
              f'3. **Años con mejora/empeoramiento:** columnas "mejora/empeora" y años listados; detalle anual en `comparaciones_pareadas.csv` y en `graficos/estabilidad_anual_{_slug(moneda)}.png`.',
              f'4. **Resultados inciertos ({len(inc)}):** ' + ', '.join(f'`{a}`' for a in inc.atributo_retirado) + '.',
              f'   **Conservar ({len(cons)}):** ' + (', '.join(f'`{a}`' for a in cons.atributo_retirado) or 'ninguna') + '.']
        cj = conj.loc[conj.moneda.eq(moneda)]
        if len(cj):
            r = cj.iloc[0]
            L.append(f'5. **Retirada conjunta** ({r.atributo_retirado.replace(";", ", ")}): RMSE anual medio {r.delta_RMSE_medio_pct:+.2f} %, MAE {r.delta_MAE_medio_pct:+.2f} %, '
                     f'mejora en {r.anios_mejora_RMSE}/{r.anios_evaluables} años; concatenado RMSE {r.delta_RMSE_concatenado_pct:+.2f} %. {r.conclusion_conjunta} Exploratorio: mismas validaciones que eligieron las candidatas.')
        else:
            L.append('5. **Retirada conjunta:** no aplica; no hay candidatas en esta moneda.')
        t = g[['atributo_retirado', 'delta_RMSE_medio_pct', 'delta_MAE_medio_pct', 'mediana_delta_RMSE_anual_pct', 'anios_mejora_RMSE', 'anios_empeora_RMSE',
               'anios_empate_RMSE', 'anios_mejora_MAE', 'delta_RMSE_concatenado_pct', 'delta_MAE_concatenado_pct', 'anios_que_mejora_RMSE', 'clasificacion']].copy()
        t.columns = ['atributo', 'ΔRMSE anual medio %', 'ΔMAE anual medio %', 'mediana ΔRMSE anual %', 'años mejora RMSE', 'años empeora RMSE', 'empates RMSE',
                     'años mejora MAE', 'ΔRMSE concat. %', 'ΔMAE concat. %', 'años que mejora (RMSE)', 'clasificación']
        L += ['', _md_tabla(t), '', f'![Cambio de error]({"graficos/delta_error_" + _slug(moneda) + ".png"})', '',
              f'![Estabilidad anual]({"graficos/estabilidad_anual_" + _slug(moneda) + ".png"})', '']
        conflictos = g.loc[g.motivo.str.contains('conflicto')]
        if len(conflictos):
            L += ['Conflictos RMSE/MAE: ' + '; '.join(f'`{r.atributo_retirado}` ({r.motivo})' for r in conflictos.itertuples()) + '.', '']
    L += ['## 4. Concentración y sensibilidad a un caso (post hoc; no altera la clasificación)', '',
          'Estos diagnósticos se añadieron tras observar los resultados y por eso no modifican la regla declarada. Indican cuánto depende cada conclusión de un año o una observación.', '']
    for r in casos_dom.itertuples():
        L.append(f'- **{r.moneda}:** la observación con mayor error absoluto de la referencia es {r.RPJ} ejercicio {r.Ejercicio} (año objetivo {r.anio_objetivo}): '
                 f'real {r.y_real:,.0f}, predicho {r.y_predicho:,.0f}.')
    dom = conc.loc[conc.proporcion_error_cuadratico_del_anio.ge(.5)]
    L.append('- Años en que una sola observación concentra ≥ 50 % del error cuadrático de la referencia: '
             + ('; '.join(f'{r.moneda} {r.anio_validacion}: {r.RPJ} ej. {r.Ejercicio} ({r.proporcion_error_cuadratico_del_anio:.0%})' for r in dom.itertuples()) or 'ninguno')
             + '. Con RMSE, el cambio de un año así refleja sobre todo esa predicción.')
    L.append('')
    textos = {'sin_observacion_dominante': 'excluir esa observación', 'sin_empresa_dominante': 'excluir todas las validaciones de esa empresa'}
    for moneda, g in res.groupby('moneda', sort=False):
        for sens_nombre, texto in textos.items():
            s = sens.loc[sens.moneda.eq(moneda) & sens.sensibilidad.eq(sens_nombre)].set_index('atributo_retirado')
            cambios = [(r.atributo_retirado, r.clasificacion, s.loc[r.atributo_retirado, 'clasificacion'], s.loc[r.atributo_retirado, 'delta_RMSE_medio_pct'])
                       for r in g.itertuples() if r.clasificacion != s.loc[r.atributo_retirado, 'clasificacion']]
            L.append(f'- **{moneda}, {texto}:** cambian {len(cambios)} clasificaciones'
                     + (': ' + '; '.join(f'`{a}` {c1} → {c2} (ΔRMSE anual medio {d:+.2f} %)' for a, c1, c2, d in cambios) if cambios else '') + '. '
                     f'Candidatas en esta sensibilidad: ' + (', '.join(f'`{a}`' for a in s.index[s.clasificacion.eq('Candidata a retirar')]) or 'ninguna') + '.')
    L += ['', '## 5. Calidad del dato frente a perjuicio predictivo', '',
          '- La Etapa 1 documentó problemas de calidad (casos de denominador pequeño, saltos de magnitud, VIF altos, faltantes estructurales, riesgo temporal). Esos hallazgos no se usan aquí para retirar variables: una variable con extremos o VIF alto puede no perjudicar el error, y una sin problemas de calidad puede perjudicarlo.',
          '- La ablación mide solo el efecto marginal de retirar una variable de este Ridge con las otras 25 presentes. Variables redundantes entre sí (p. ej. rezagos FCO/FCL) pueden mostrar efectos individuales pequeños aunque el bloque sea informativo.', '',
          '## 6. Limitaciones', '',
          '- Ocho años de validación por moneda, en cuatro bloques; los años del mismo bloque comparten modelo y las observaciones de una empresa no son independientes: no se afirma significancia estadística.',
          '- RMSE en unidades monetarias reportadas está dominado por pocas empresas grandes o casos extremos; un cambio del RMSE puede reflejar pocas predicciones. Dólares tiene 47–54 filas de validación por bloque.',
          '- La regla y los umbrales son exploratorios; con otros umbrales la clasificación puede cambiar (todos los valores se publican).',
          '- La retirada conjunta reutiliza la misma validación que eligió las candidatas: es optimista y no estima el rendimiento final; requiere confirmación independiente (p. ej., periodos futuros) antes de cualquier decisión.',
          '- No hay fechas de publicación ni vintages: la separación por ejercicio no acredita disponibilidad real de la información (ver auditoría temporal de la Etapa 1); 12 atributos están clasificados como posible fuga temporal.',
          '- Escala monetaria no acreditada; FCL preliminar no es FCFF validado; alpha fijo en 1.0, sin búsqueda de hiperparámetros ni otros modelos.', '',
          '## 7. Integridad y reproducción', '',
          f'- Archivos fuera de `reports/sprint_08/ablacion/` y de los archivos nuevos de esta etapa: sin cambios durante la ejecución ({integridad["archivos_verificados"]} verificados). '
          f'Cambios previos del usuario presentes en archivos rastreados (no modificados por esta etapa): {", ".join(integridad["git_modificados_previos"]) or "ninguno"}.',
          '- Reproducción: ver `REPRODUCIR.md`.']
    return '\n'.join(L) + '\n'


# ---------------------------------------------------------------------------
# Validación temporal anidada (alternativa principal). Protocolo fijado antes de ejecutar.
# ---------------------------------------------------------------------------
ALPHAS = (0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)   # rejilla predefinida de Sprint 06 (notebooks/08_mejoras_baseline.ipynb, celda 1)
ANIOS_EXTERNOS = (2017, 2018, 2019, 2020, 2021)       # un modelo por año externo; entrenamiento con todos los años anteriores
N_ANIOS_INTERNOS = 3                                   # años internos inmediatamente anteriores al año externo
MIN_ANIOS_HISTORIA_INTERNA = 8                         # mismo calentamiento que Sprint 06
UMBRAL_SELECCION_PCT = 1.0                             # mejora mínima del RMSE interno medio para aceptar una retirada
MIN_ANIOS_INTERNOS_MEJORA = 2                          # de 3 años internos
MAX_RETIRADAS = 5
MIN_ANIOS_EXTERNOS_MEJORA = 4                          # de 5 años externos, para recomendar el procedimiento reducido
PEOR_EMPEORAMIENTO_MAX_PCT = 5.0
PROCEDIMIENTOS = ('completo_alpha_interno', 'reducido', 'E2_alpha_1')
# Revisión (exploratoria): rejilla ampliada una sola vez, igual para completo y reducido.
ALPHAS_REVISION = (0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0)
REFERENCIAS_SIMPLES = ('media_historica', 'persistencia')


def protocolo_anidado():
    return {
        'proposito': 'Estimar el desempeño de un procedimiento de selección (atributos y alpha) frente al modelo completo con alpha seleccionado, '
                     'separando selección (validación interna, solo pasado) y evaluación (año externo no usado en decisiones).',
        'anios_externos': list(ANIOS_EXTERNOS), 'entrenamiento_externo': 'todas las filas con anio_objetivo < año externo, misma moneda',
        'validacion_interna': f'los {N_ANIOS_INTERNOS} años objetivo inmediatamente anteriores al año externo; cada uno con ventana expansiva '
                              f'(entrena con años anteriores) y al menos {MIN_ANIOS_HISTORIA_INTERNA} años de historia; por eso el primer año externo es 2017',
        'compatibilidad_sprint06': 'Se conserva la unidad año objetivo, las ventanas expansivas y el calentamiento de 8 años de Sprint 06. Sus bloques de 2 años '
                                   'no se reutilizan como pliegues externos porque los primeros (2014–2015) no dejan historia para una validación interna.',
        'rejilla_alpha': list(ALPHAS), 'seleccion_alpha': 'mínimo RMSE anual medio interno; empate (diferencia relativa <= 1e-9): mayor alpha',
        'eliminacion_hacia_atras': {
            'inicio': '26 atributos de E2', 'paso': 'evaluar retirar cada atributo restante (alpha reajustado para cada subconjunto con la misma rejilla y pliegues internos)',
            'eleccion': 'retirada con menor RMSE anual medio interno; empate: primer atributo en el orden E2',
            'aceptacion': f'mejora relativa >= {UMBRAL_SELECCION_PCT:g} % del RMSE interno medio Y RMSE menor en >= {MIN_ANIOS_INTERNOS_MEJORA} de {N_ANIOS_INTERNOS} años internos',
            'maximo_retiradas': MAX_RETIRADAS, 'sin_busqueda_exhaustiva': True},
        'procedimientos': {'completo_alpha_interno': '26 atributos, alpha interno', 'reducido': 'atributos y alpha internos',
                           'E2_alpha_1': 'contexto: E2 original con alpha=1.0 fijo (no participa en la decisión)'},
        'regla_recomendacion': {
            'reducir_provisional': f'RMSE anual medio externo del reducido <= -{UMBRAL_SELECCION_PCT:g} % frente al completo, mejora en >= {MIN_ANIOS_EXTERNOS_MEJORA} '
                                   f'de {len(ANIOS_EXTERNOS)} años, MAE anual medio no peor y peor empeoramiento anual <= {PEOR_EMPEORAMIENTO_MAX_PCT:g} %',
            'conservar_completo': 'RMSE anual medio externo del reducido >= completo o reducido peor en la mayoría de años',
            'evidencia_insuficiente': 'cualquier otro caso'},
        'nota': 'Umbrales exploratorios fijados antes de ejecutar; la evaluación externa mide el procedimiento, no la optimalidad de una lista fija.',
    }


def _ridge_multi(ztr, ytr, zva, alphas):
    """Ridge con intercepto (solver SVD) para varias alphas a la vez; equivale a sklearn Ridge(solver='svd')."""
    xm, ym = ztr.mean(axis=0), ytr.mean()
    u, s, vt = np.linalg.svd(ztr - xm, full_matrices=False)
    uty = u.T @ (ytr - ym)
    out = []
    for a in alphas:
        coef = vt.T @ (s / (s ** 2 + a) * uty)
        out.append((zva - xm) @ coef + ym)
    return out


class PliegueInterno:
    """Preparación ajustada solo con el entrenamiento interno; mediana y escala son por columna,
    así que un subconjunto de columnas equivale a ajustar la preparación con ese subconjunto."""

    def __init__(self, tr, va, cols, anio):
        imp = SimpleImputer(strategy='median', keep_empty_features=True).fit(tr[cols])
        esc = StandardScaler().fit(imp.transform(tr[cols]))
        self.ztr, self.zva = esc.transform(imp.transform(tr[cols])), esc.transform(imp.transform(va[cols]))
        self.ytr, self.yva = tr.objetivo_fcl_t1.to_numpy(float), va.objetivo_fcl_t1.to_numpy(float)
        self.anio, self.n_train, self.n_val = anio, len(tr), len(va)
        self.anio_train_max = int(tr.anio_objetivo.max())
        self.pos = {c: i for i, c in enumerate(cols)}

    def rmse(self, columnas, alphas=ALPHAS):
        j = [self.pos[c] for c in columnas]
        return np.array([np.sqrt(np.mean((p - self.yva) ** 2)) for p in _ridge_multi(self.ztr[:, j], self.ytr, self.zva[:, j], alphas)])


def pliegues_internos(hist, cols):
    anios = sorted(hist.anio_objetivo.unique())
    internos = anios[-N_ANIOS_INTERNOS:]
    out = []
    for a in internos:
        previos = [y for y in anios if y < a]
        if len(previos) < MIN_ANIOS_HISTORIA_INTERNA:
            raise ValueError(f'Historia insuficiente para validar internamente {a}: {len(previos)} años')
        tr, va = hist.loc[hist.anio_objetivo.lt(a)], hist.loc[hist.anio_objetivo.eq(a)]
        out.append(PliegueInterno(tr, va, cols, int(a)))
    return out


def evaluar_subconjunto(internos, columnas, alphas=ALPHAS):
    """RMSE interno por año y alpha; devuelve el alpha elegido, su media y sus RMSE anuales."""
    m = np.vstack([f.rmse(columnas, alphas) for f in internos])  # años x alphas
    medias = m.mean(axis=0)
    mejor = medias.min()
    k = max(i for i, v in enumerate(medias) if v <= mejor * (1 + 1e-9))  # empate: mayor alpha
    return dict(alpha=alphas[k], rmse_medio=float(medias[k]), rmse_anual=m[:, k], medias_por_alpha=medias)


def seleccionar_original(hist, cols, etiqueta):
    """Versión de la primera ejecución (se conserva sin cambios para reproducir reports/sprint_08/ablacion/).
    Defecto auditado: se detiene si la retirada de menor RMSE no es admisible, aunque otra sí lo sea."""
    internos = pliegues_internos(hist, cols)
    actual = list(cols)
    ev = evaluar_subconjunto(internos, actual)
    alpha_completo = ev['alpha']
    historial = [dict(**etiqueta, paso=0, atributo_evaluado='', n_atributos=len(actual), alpha=ev['alpha'], rmse_interno_medio=ev['rmse_medio'],
                      **{f'rmse_interno_{f.anio}': v for f, v in zip(internos, ev['rmse_anual'])}, mejora_pct=np.nan, anios_internos_mejora=np.nan,
                      elegido=True, aceptado=True, motivo='punto de partida: 26 atributos')]
    for paso in range(1, MAX_RETIRADAS + 1):
        candidatos = [(c, evaluar_subconjunto(internos, [x for x in actual if x != c])) for c in actual]
        orden = sorted(range(len(candidatos)), key=lambda i: (candidatos[i][1]['rmse_medio'], cols.index(candidatos[i][0])))
        elegido = orden[0]
        for i, (c, e) in enumerate(candidatos):
            mejora = 100 * (ev['rmse_medio'] - e['rmse_medio']) / ev['rmse_medio']
            anios = int(np.sum(e['rmse_anual'] < ev['rmse_anual'] * (1 - TOLERANCIA_EMPATE_REL)))
            acepta = i == elegido and mejora >= UMBRAL_SELECCION_PCT and anios >= MIN_ANIOS_INTERNOS_MEJORA
            motivo = '' if i != elegido else ('retirada aceptada' if acepta else
                                              f'no aceptada: mejora {mejora:.2f} % (mínimo {UMBRAL_SELECCION_PCT:g} %), años internos con mejora {anios} (mínimo {MIN_ANIOS_INTERNOS_MEJORA})')
            historial.append(dict(**etiqueta, paso=paso, atributo_evaluado=c, n_atributos=len(actual) - 1, alpha=e['alpha'], rmse_interno_medio=e['rmse_medio'],
                                  **{f'rmse_interno_{f.anio}': v for f, v in zip(internos, e['rmse_anual'])}, mejora_pct=mejora, anios_internos_mejora=anios,
                                  elegido=i == elegido, aceptado=acepta, motivo=motivo))
        c, e = candidatos[elegido]
        if not historial[-len(candidatos) + elegido]['aceptado']:
            break
        actual = [x for x in actual if x != c]
        ev = e
    info_internos = [dict(**etiqueta, anio_interno=f.anio, anios_train=f'{int(hist.anio_objetivo.min())}-{f.anio_train_max}', n_train=f.n_train, n_validacion=f.n_val)
                     for f in internos]
    return dict(atributos=actual, alpha=ev['alpha'], alpha_completo=alpha_completo, retirados=[c for c in cols if c not in actual],
                historial=historial, internos=info_internos)


def elegir_retirada(ev, candidatos, cols, eleccion='mejor_admisible'):
    """Regla de elección de un paso. Devuelve (índice elegido o None, filas descriptivas, motivo de parada).
    'mejor_admisible' (revisión): entre las retiradas que cumplen umbral y estabilidad, la de menor RMSE.
    'mejor_rmse' (ejecución original): la de menor RMSE; si no es admisible se detiene, aunque otra lo sea."""
    filas = []
    for c, e in candidatos:
        mejora = 100 * (ev['rmse_medio'] - e['rmse_medio']) / ev['rmse_medio']
        anios = int(np.sum(e['rmse_anual'] < ev['rmse_anual'] * (1 - TOLERANCIA_EMPATE_REL)))
        filas.append(dict(atributo_evaluado=c, mejora_pct=mejora, anios_internos_mejora=anios,
                          admisible=bool(mejora >= UMBRAL_SELECCION_PCT and anios >= MIN_ANIOS_INTERNOS_MEJORA)))
    orden = sorted(range(len(candidatos)), key=lambda i: (candidatos[i][1]['rmse_medio'], cols.index(candidatos[i][0])))
    if eleccion == 'mejor_rmse':
        k = orden[0]
        if filas[k]['admisible']:
            return k, filas, ''
        return None, filas, (f'la retirada de menor RMSE ({filas[k]["atributo_evaluado"]}) no es admisible: mejora {filas[k]["mejora_pct"]:.2f} % '
                             f'(mínimo {UMBRAL_SELECCION_PCT:g} %), años internos con mejora {filas[k]["anios_internos_mejora"]} (mínimo {MIN_ANIOS_INTERNOS_MEJORA})')
    admisibles = [i for i in orden if filas[i]['admisible']]
    if admisibles:
        return admisibles[0], filas, ''
    return None, filas, (f'ninguna de {len(candidatos)} retiradas es admisible; la de menor RMSE ({filas[orden[0]]["atributo_evaluado"]}) mejora '
                         f'{filas[orden[0]]["mejora_pct"]:.2f} % en {filas[orden[0]]["anios_internos_mejora"]} años internos')


def seleccionar(hist, cols, etiqueta, alphas=ALPHAS, eleccion='mejor_admisible'):
    """Eliminación hacia atrás acotada usando solo `hist` (pasado del año externo)."""
    internos = pliegues_internos(hist, cols)
    actual = list(cols)
    ev = evaluar_subconjunto(internos, actual, alphas)
    alpha_completo = ev['alpha']
    historial = [dict(**etiqueta, paso=0, atributo_evaluado='', n_atributos=len(actual), alpha=ev['alpha'], rmse_interno_medio=ev['rmse_medio'],
                      **{f'rmse_interno_{f.anio}': v for f, v in zip(internos, ev['rmse_anual'])}, mejora_pct=np.nan, anios_internos_mejora=np.nan,
                      admisible=True, elegido=True, aceptado=True, motivo='punto de partida: 26 atributos')]
    parada = f'máximo de {MAX_RETIRADAS} retiradas alcanzado'
    for paso in range(1, MAX_RETIRADAS + 1):
        candidatos = [(c, evaluar_subconjunto(internos, [x for x in actual if x != c], alphas)) for c in actual]
        k, filas, motivo_parada = elegir_retirada(ev, candidatos, cols, eleccion)
        n_adm = sum(f['admisible'] for f in filas)
        for i, ((c, e), f) in enumerate(zip(candidatos, filas)):
            historial.append(dict(**etiqueta, paso=paso, n_atributos=len(actual) - 1, alpha=e['alpha'], rmse_interno_medio=e['rmse_medio'],
                                  **{f'rmse_interno_{x.anio}': v for x, v in zip(internos, e['rmse_anual'])}, **f,
                                  elegido=i == k, aceptado=i == k,
                                  motivo=(f'retirada aceptada ({n_adm} admisibles en el paso)' if i == k else '')))
        if k is None:
            parada = f'paso {paso}: {motivo_parada}'
            historial[-1]['motivo'] = 'parada: ' + motivo_parada  # registro explícito en la última fila del paso
            break
        actual = [x for x in actual if x != candidatos[k][0]]
        ev = candidatos[k][1]
    info_internos = [dict(**etiqueta, anio_interno=f.anio, anios_train=f'{int(hist.anio_objetivo.min())}-{f.anio_train_max}', n_train=f.n_train, n_validacion=f.n_val)
                     for f in internos]
    return dict(atributos=actual, alpha=ev['alpha'], alpha_completo=alpha_completo, retirados=[c for c in cols if c not in actual],
                historial=historial, internos=info_internos, motivo_parada=parada)


def ejecutar_anidada(entrenamiento, cols, anios_externos=ANIOS_EXTERNOS, revision=False):
    """Validación externa: para cada moneda y año externo, toda la selección usa solo años anteriores.
    revision=False reproduce la primera ejecución; revision=True usa la elección entre admisibles, la rejilla ampliada
    y añade las referencias simples sobre las mismas filas."""
    assert entrenamiento.particion.eq('entrenamiento').all() and entrenamiento.anio_objetivo.le(ANIO_OBJETIVO_MAX_TRAIN).all()
    preds, hist, internos, selecciones = [], [], [], []
    ident = ['id_fila', 'RPJ', 'Ejercicio', 'anio_objetivo']
    for moneda, t in entrenamiento.groupby('Moneda', sort=True):
        for y in anios_externos:
            pasado, externo = t.loc[t.anio_objetivo.lt(y)], t.loc[t.anio_objetivo.eq(y)]
            assert len(externo) and pasado.anio_objetivo.max() < y
            etiqueta = dict(moneda=moneda, anio_externo=y)
            sel = seleccionar(pasado, cols, etiqueta, ALPHAS_REVISION) if revision else seleccionar_original(pasado, cols, etiqueta)
            hist += sel['historial']
            internos += sel['internos']
            selecciones.append(dict(moneda=moneda, anio_externo=y, n_train=len(pasado), empresas_train=pasado.RPJ.nunique(), n_externo=len(externo),
                                    empresas_externo=externo.RPJ.nunique(), alpha_completo=sel['alpha_completo'], alpha_reducido=sel['alpha'],
                                    n_atributos_reducido=len(sel['atributos']), retirados=';'.join(sel['retirados']),
                                    **({'motivo_parada': sel['motivo_parada']} if revision else {})))
            for proc, columnas, alpha in [('completo_alpha_interno', list(cols), sel['alpha_completo']), ('reducido', sel['atributos'], sel['alpha']),
                                          ('E2_alpha_1', list(cols), ALPHA)]:
                modelo = crear_modelo(columnas, alpha).fit(pasado[columnas], pasado.objetivo_fcl_t1)
                num = modelo.named_steps['preparacion'].named_transformers_['numericas']
                np.testing.assert_allclose(num.named_steps['imputer'].statistics_, pasado[columnas].median().fillna(0).to_numpy(), rtol=1e-12)
                assert int(num.named_steps['scaler'].n_samples_seen_) == len(pasado)
                g = externo[ident].copy()
                g.insert(0, 'procedimiento', proc)
                g.insert(1, 'moneda', moneda)
                g['alpha'], g['n_atributos'] = alpha, len(columnas)
                g['y_real'], g['y_predicho'] = externo.objetivo_fcl_t1.to_numpy(), modelo.predict(externo[columnas])
                preds.append(g)
            if revision:
                preds += referencias_simples(pasado, externo, moneda, ident)
    return (pd.concat(preds, ignore_index=True), pd.DataFrame(hist), pd.DataFrame(internos), pd.DataFrame(selecciones))


def fcl_t(tabla):
    """FCL preliminar del ejercicio t con la regla del proyecto: inválido si CAPEX_reportado(t) > 0.
    Es el mismo valor que el objetivo de la fila t-1 (verificado en pruebas); FCL_preliminar_lag1 es FCL(t-1)."""
    return tabla.FCL_preliminar.where(~tabla.CAPEX_reportado.gt(0))


def referencias_simples(pasado, externo, moneda, ident):
    """Media histórica del objetivo en el entrenamiento externo y persistencia FCL(t) con respaldo en esa media."""
    media = float(pasado.objetivo_fcl_t1.mean())
    persist = fcl_t(externo)
    out = []
    for proc, pred, respaldo in [('media_historica', pd.Series(media, index=externo.index), pd.Series(False, index=externo.index)),
                                 ('persistencia', persist.fillna(media), persist.isna())]:
        g = externo[ident].copy()
        g.insert(0, 'procedimiento', proc)
        g.insert(1, 'moneda', moneda)
        g['alpha'], g['n_atributos'] = np.nan, 0
        g['y_real'], g['y_predicho'] = externo.objetivo_fcl_t1.to_numpy(), pred.to_numpy()
        g['usa_respaldo_media'] = respaldo.to_numpy()
        out.append(g)
    return out


def resumen_anidada(pred):
    anual = pd.DataFrame([dict(procedimiento=p, moneda=m, anio_externo=int(y), **metricas(g.y_real, g.y_predicho))
                          for (p, m, y), g in pred.groupby(['procedimiento', 'moneda', 'anio_objetivo'])])
    ref = anual.loc[anual.procedimiento.eq('completo_alpha_interno')].set_index(['moneda', 'anio_externo'])
    pares = anual.loc[anual.procedimiento.ne('completo_alpha_interno')].copy()
    for x in ['RMSE', 'MAE']:
        base = ref.loc[list(zip(pares.moneda, pares.anio_externo)), x].to_numpy()
        pares[f'{x}_completo'] = base
        pares[f'delta_{x}'] = pares[x] - base
        pares[f'delta_{x}_pct'] = _pct(pares[f'delta_{x}'], base)
        pares[f'direccion_{x}'] = _direccion(pares[f'delta_{x}'], base)
    filas = []
    for (p, m), g in anual.groupby(['procedimiento', 'moneda']):
        cat = pred.loc[pred.procedimiento.eq(p) & pred.moneda.eq(m)]
        r = dict(procedimiento=p, moneda=m, anios_externos=len(g), n_externo=int(g.n.sum()), RMSE_anual_medio=g.RMSE.mean(), MAE_anual_medio=g.MAE.mean(),
                 **{f'{k}_concatenado': v for k, v in metricas(cat.y_real, cat.y_predicho).items() if k != 'n'})
        if p != 'completo_alpha_interno':
            c = pares.loc[pares.procedimiento.eq(p) & pares.moneda.eq(m)]
            rc = anual.loc[anual.procedimiento.eq('completo_alpha_interno') & anual.moneda.eq(m)]
            catc = pred.loc[pred.procedimiento.eq('completo_alpha_interno') & pred.moneda.eq(m)]
            mc = metricas(catc.y_real, catc.y_predicho)
            r.update(delta_RMSE_anual_medio_pct=float(_pct(r['RMSE_anual_medio'] - rc.RMSE.mean(), rc.RMSE.mean())),
                     delta_MAE_anual_medio_pct=float(_pct(r['MAE_anual_medio'] - rc.MAE.mean(), rc.MAE.mean())),
                     delta_RMSE_concatenado_pct=float(_pct(r['RMSE_concatenado'] - mc['RMSE'], mc['RMSE'])),
                     delta_MAE_concatenado_pct=float(_pct(r['MAE_concatenado'] - mc['MAE'], mc['MAE'])),
                     mediana_delta_RMSE_anual_pct=c.delta_RMSE_pct.median(), anios_mejora_RMSE=int(c.direccion_RMSE.eq('mejora').sum()),
                     anios_empeora_RMSE=int(c.direccion_RMSE.eq('empeora').sum()), anios_empate_RMSE=int(c.direccion_RMSE.eq('empate').sum()),
                     anios_mejora_MAE=int(c.direccion_MAE.eq('mejora').sum()),
                     peor_empeoramiento_anual_RMSE_pct=float(c.delta_RMSE_pct.max()), anio_peor_empeoramiento=int(c.loc[c.delta_RMSE_pct.idxmax(), 'anio_externo']))
        filas.append(r)
    res = pd.DataFrame(filas)
    res['recomendacion'] = [recomendar(r) if r['procedimiento'] == 'reducido' else '' for r in res.to_dict('records')]
    return anual, pares, res


def recomendar(r):
    reducir = (r['delta_RMSE_anual_medio_pct'] <= -UMBRAL_SELECCION_PCT and r['anios_mejora_RMSE'] >= MIN_ANIOS_EXTERNOS_MEJORA
               and r['delta_MAE_anual_medio_pct'] <= 0 and r['peor_empeoramiento_anual_RMSE_pct'] <= PEOR_EMPEORAMIENTO_MAX_PCT)
    if reducir:
        return 'Reducir (provisional; requiere evaluación posterior)'
    if r['delta_RMSE_anual_medio_pct'] >= 0 or r['anios_empeora_RMSE'] > r['anios_externos'] / 2:
        return 'Conservar modelo completo'
    return 'Evidencia insuficiente'


def frecuencias(sel, cols):
    filas = []
    for m, g in sel.groupby('moneda'):
        retirados = [x.split(';') if x else [] for x in g.retirados]
        for c in cols:
            anios = [int(y) for y, r in zip(g.anio_externo, retirados) if c in r]
            filas.append(dict(moneda=m, atributo=c, veces_retirado=len(anios), pliegues=len(g), anios_externos_retirado=';'.join(map(str, anios))))
    alphas = pd.concat([sel[['moneda', 'anio_externo']].assign(procedimiento=p, alpha=sel[c]) for p, c in
                        [('completo_alpha_interno', 'alpha_completo'), ('reducido', 'alpha_reducido')]])
    return pd.DataFrame(filas), alphas.groupby(['moneda', 'procedimiento', 'alpha']).size().rename('pliegues').reset_index()


def graficos_anidada(anual, sel, cols, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tinta, tinta2, fondo = '#0b0b0b', '#52514e', '#fcfcfb'
    colores = {'completo_alpha_interno': '#2a78d6', 'reducido': '#eb6834', 'E2_alpha_1': '#8a8984'}
    nombres = {'completo_alpha_interno': 'Completo (26, alpha interno)', 'reducido': 'Reducido (selección interna)', 'E2_alpha_1': 'E2 original (alpha = 1)'}
    rutas = []
    for moneda in sorted(anual.moneda.unique()):
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={'width_ratios': [1.1, 1]})
        for p in PROCEDIMIENTOS:
            g = anual.loc[anual.procedimiento.eq(p) & anual.moneda.eq(moneda)].sort_values('anio_externo')
            ax.plot(g.anio_externo, g.RMSE, color=colores[p], lw=2, marker='o', ms=7, mec=fondo, mew=1.5, label=nombres[p], ls='--' if p == 'E2_alpha_1' else '-')
        ax.set_title(f'{_nombre(moneda)}: RMSE por año externo', color=tinta, loc='left')
        ax.set_xlabel('Año objetivo externo')
        ax.set_ylabel('RMSE (unidad monetaria reportada)')
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:,.0f}'))
        ax.set_xticks(list(ANIOS_EXTERNOS))
        ax.grid(axis='y', color='#e4e3df', lw=.6)
        ax.legend(frameon=False, fontsize=8)
        for s_ in ['top', 'right']:
            ax.spines[s_].set_visible(False)
        g = sel.loc[sel.moneda.eq(moneda)].sort_values('anio_externo')
        retirados = sorted({c for x in g.retirados for c in (x.split(';') if x else [])}, key=cols.index)
        if retirados:
            mat = np.array([[c in (x.split(';') if x else []) for x in g.retirados] for c in retirados], float)
            ax2.imshow(mat, cmap=matplotlib.colors.ListedColormap(['#f0efec', '#eb6834']), vmin=0, vmax=1, aspect='auto')
            ax2.set_yticks(range(len(retirados)), retirados)
            ax2.set_xticks(range(len(g)), [f'{y}\nα={a:g}\n{n} atr.' for y, a, n in zip(g.anio_externo, g.alpha_reducido, g.n_atributos_reducido)])
            ax2.set_xticks(np.arange(-.5, len(g)), minor=True)
            ax2.set_yticks(np.arange(-.5, len(retirados)), minor=True)
            ax2.grid(which='minor', color=fondo, lw=2)
            ax2.tick_params(which='minor', length=0)
            ax2.set_title('Atributos retirados por año externo (naranja)', color=tinta, loc='left')
        else:
            ax2.axis('off')
            ax2.text(0.5, 0.5, 'El procedimiento no retiró ningún atributo', ha='center', color=tinta2)
        fig.tight_layout()
        ruta = out / 'graficos' / f'anidada_{_slug(moneda)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
    return rutas


def cabecera(res_a, final_a, res_ind, replica, sel_a):
    r = res_a.loc[res_a.procedimiento.eq('reducido')].set_index('moneda')
    L = ['# Sprint 08 — Etapa 2: ¿qué variables perjudican la predicción del FCL preliminar?', '',
         'Solo entrenamiento (2.869 filas, años objetivo 2006–2021), por moneda; prueba 2022–2025 no interviene. Parte A (principal): validación temporal anidada '
         'que separa selección y evaluación. Parte B: diagnóstico de ablación individual con Ridge(alpha = 1).', '',
         '## Respuesta breve', '']
    for m, x in r.iterrows():
        fm = final_a.loc[final_a.moneda.eq(m)].iloc[0]
        L.append(f'- **{m}: {x.recomendacion}.** El procedimiento reducido cambia el RMSE anual medio externo {x.delta_RMSE_anual_medio_pct:+.2f} % y el MAE '
                 f'{x.delta_MAE_anual_medio_pct:+.2f} % frente al completo con alpha interno; mejora en {int(x.anios_mejora_RMSE)} de {int(x.anios_externos)} años; peor año '
                 f'{x.peor_empeoramiento_anual_RMSE_pct:+.2f} %. Lista propuesta con todo el entrenamiento: retirar '
                 f'{fm.retirados.replace(";", ", ") or "nada"} (pendiente de evaluación posterior).')
    e2 = res_a.loc[res_a.procedimiento.eq('E2_alpha_1')].set_index('moneda')
    tope = sel_a.assign(t=lambda x: (x.alpha_completo == max(ALPHAS)).astype(int) + (x.alpha_reducido == max(ALPHAS)).astype(int)).groupby('moneda').t.sum()
    L += ['- **El efecto dominante es la regularización, no la retirada de variables:** E2 con alpha = 1 tiene un RMSE anual medio externo '
          + '; '.join(f'{m} {x.delta_RMSE_anual_medio_pct:+.1f} %' for m, x in e2.iterrows())
          + ' respecto al completo con alpha interno. Las mejoras de la ablación individual (Parte B, alpha = 1) son compatibles con compensar una regularización insuficiente: '
          'con alpha elegido internamente, retirar variables ya no mejora de forma consistente.',
          '- Alpha elegido en el máximo de la rejilla (10000) en ' + '; '.join(f'{m} {int(n)} de {2 * len(ANIOS_EXTERNOS)} selecciones' for m, n in tope.items())
          + ': la rejilla predefinida puede quedar corta por arriba. No se amplía a posteriori; debe revisarse en una etapa posterior con un protocolo nuevo.',
          '- Los problemas de calidad de la Etapa 1 (extremos, VIF, faltantes) no se usan como criterio de retirada; solo cuenta el efecto sobre el error fuera de muestra.', '',
          '## Auditoría previa e inconsistencias documentadas', '',
          '- Verificado contra el código: 26 atributos y orden (notebook 07 celda 10, `validacion_baseline.json`, `especificacion_e2.json`); objetivo FCO+CAPEX de t+1 por unión '
          'Ejercicio+1 exacta; elegibilidad objetivo no faltante y misma moneda; particiones 2.869/691; Pipeline mediana (`keep_empty_features=True`) + StandardScaler + '
          'Ridge(alpha=1, solver="svd") por moneda. La réplica reproduce las predicciones E2 de entrenamiento del notebook 07 con diferencia '
          + ', '.join(f'{k} {v:.0e}' for k, v in replica.items()) + '.',
          '- `src/feature_engineering.make_preprocessor` usa RobustScaler: no es la configuración E2 (sensibilidad en Sprint 06); se usa StandardScaler.',
          '- La validación de Sprint 06 (notebook 08) eligió alpha por MSE anual medio con recorte p1/p99 y niveles t: no es E2. Se reutilizan solo su regla de pliegues '
          '(calentamiento 8 años, ventanas expansivas por año objetivo) y su rejilla de alpha; el criterio interno aquí es el RMSE anual medio.',
          '- Los bloques de 2 años de Sprint 06 sirven para el diagnóstico individual (Parte B) pero no como pliegues externos anidados: 2014–2015 no dejan historia para una validación interna.',
          '- La etiqueta de dólares es `D lares` en la fuente; se conserva.',
          '- `notebooks/03_extraccion_macroeconomica.ipynb` y `reports/auditoria_extraccion_macroeconomica.md` tienen cambios del usuario sin commit; hacen fallar las pruebas de '
          'integridad de Sprint 07 y de la Etapa 1 (detección correcta, ajena a esta etapa). No se modificaron.', '']
    return L


def informe_anidada(proto, internos, sel, res, pares, freq, alphas, final, cols):
    L = ['## Parte A — Validación temporal anidada (alternativa principal)', '',
         f'**Propósito.** {proto["proposito"]} La evaluación externa estima el desempeño del procedimiento, no demuestra que una lista fija sea óptima.', '',
         '### A.1 Protocolo (fijado antes de ejecutar)', '',
         f'- Años externos: {", ".join(map(str, ANIOS_EXTERNOS))}; {proto["entrenamiento_externo"]}.',
         f'- Validación interna: {proto["validacion_interna"]}. {proto["compatibilidad_sprint06"]}',
         f'- Rejilla de alpha (de Sprint 06): {", ".join(f"{a:g}" for a in ALPHAS)}; {proto["seleccion_alpha"]}.',
         f'- Eliminación hacia atrás: {proto["eliminacion_hacia_atras"]["paso"]}; {proto["eliminacion_hacia_atras"]["eleccion"]}; aceptación: {proto["eliminacion_hacia_atras"]["aceptacion"]}; máximo {MAX_RETIRADAS} retiradas.',
         f'- Regla de recomendación: reducir solo si {proto["regla_recomendacion"]["reducir_provisional"]}; conservar el completo si {proto["regla_recomendacion"]["conservar_completo"]}; si no, evidencia insuficiente.',
         '- Las métricas usan solo años objetivo ≤ 2021. Ambas monedas tienen 16 años (2006–2021), suficientes para la regla de 8 años de historia; en dólares cada año externo tiene solo 21–28 filas.', '',
         '### A.2 Pliegues externos e internos', '',
         _md_tabla(sel[['moneda', 'anio_externo', 'n_train', 'empresas_train', 'n_externo', 'empresas_externo']]), '',
         'Pliegues internos (años de validación y tamaños): `anidada_pliegues_internos.csv`.', '']
    for moneda, r in res.loc[res.procedimiento.eq('reducido')].set_index('moneda').iterrows():
        c = res.loc[res.moneda.eq(moneda)].set_index('procedimiento')
        p = pares.loc[pares.moneda.eq(moneda)].pivot(index='anio_externo', columns='procedimiento', values='delta_RMSE_pct')
        s = sel.loc[sel.moneda.eq(moneda)]
        f = freq.loc[freq.moneda.eq(moneda) & freq.veces_retirado.gt(0)].sort_values('veces_retirado', ascending=False)
        L += [f'### A.3 Resultados — {moneda}', '',
              f'**Recomendación (regla declarada): {r.recomendacion}.**', '',
              f'- RMSE anual medio externo: completo {c.loc["completo_alpha_interno", "RMSE_anual_medio"]:,.0f}; reducido {r.RMSE_anual_medio:,.0f} '
              f'({r.delta_RMSE_anual_medio_pct:+.2f} %); E2 con alpha = 1: {c.loc["E2_alpha_1", "RMSE_anual_medio"]:,.0f} ({c.loc["E2_alpha_1", "delta_RMSE_anual_medio_pct"]:+.2f} %).',
              f'- MAE anual medio: completo {c.loc["completo_alpha_interno", "MAE_anual_medio"]:,.0f}; reducido {r.MAE_anual_medio:,.0f} ({r.delta_MAE_anual_medio_pct:+.2f} %).',
              f'- Métricas concatenadas (ponderan años por n; no son el criterio): RMSE reducido {r.delta_RMSE_concatenado_pct:+.2f} %, MAE {r.delta_MAE_concatenado_pct:+.2f} % frente al completo.',
              f'- Reducido frente a completo por año: mejora en {int(r.anios_mejora_RMSE)}, empeora en {int(r.anios_empeora_RMSE)}, empata en {int(r.anios_empate_RMSE)} de {int(r.anios_externos)}; '
              f'mediana {r.mediana_delta_RMSE_anual_pct:+.2f} %; peor empeoramiento anual {r.peor_empeoramiento_anual_RMSE_pct:+.2f} % ({int(r.anio_peor_empeoramiento)}).',
              '- Atributos retirados por pliegue: ' + '; '.join(f'{x.anio_externo}: {x.retirados.replace(";", ", ") or "ninguno"} (α completo {x.alpha_completo:g}, α reducido {x.alpha_reducido:g})' for x in s.itertuples()) + '.',
              '- Frecuencia de retirada: ' + (', '.join(f'`{x.atributo}` {x.veces_retirado}/{x.pliegues}' for x in f.itertuples()) or 'ningún atributo retirado') + '. Una frecuencia alta indica selección repetida por este procedimiento, no irrelevancia universal.',
              '', '| año externo | ΔRMSE reducido % | ΔRMSE E2 α=1 % |', '|---|---|---|']
        L += [f'| {y} | {row["reducido"]:+.2f} | {row["E2_alpha_1"]:+.2f} |' for y, row in p.iterrows()]
        fm = final.loc[final.moneda.eq(moneda)].iloc[0]
        L += ['', f'- **Lista candidata final (propuesta pendiente de evaluación posterior):** el procedimiento ajustado con todo el entrenamiento hasta 2021 '
                  f'(años internos {fm.anios_internos}) retira {fm.retirados.replace(";", ", ") or "ningún atributo"} con alpha {fm.alpha_reducido:g} '
                  f'(alpha del completo {fm.alpha_completo:g}). Las métricas externas anteriores no corresponden a esta lista.', '',
              f'![Validación anidada]({"graficos/anidada_" + _slug(moneda) + ".png"})', '']
    return L


def ejecutar_final(entrenamiento, cols, revision=False):
    filas, hist = [], []
    for moneda, t in entrenamiento.groupby('Moneda', sort=True):
        etiqueta = dict(moneda=moneda, anio_externo='final_2021')
        sel = seleccionar(t, cols, etiqueta, ALPHAS_REVISION) if revision else seleccionar_original(t, cols, etiqueta)
        hist += sel['historial']
        filas.append(dict(moneda=moneda, anios_internos=';'.join(str(x['anio_interno']) for x in sel['internos']), n_train=len(t),
                          alpha_completo=sel['alpha_completo'], alpha_reducido=sel['alpha'], n_atributos=len(sel['atributos']),
                          retirados=';'.join(sel['retirados']), estado='Propuesta pendiente de evaluación posterior; sin métricas externas propias'))
    return pd.DataFrame(filas), pd.DataFrame(hist)


REPRODUCIR = """# Reproducir la ablación de variables (Sprint 08 — Etapa 2)

Desde la raíz del repositorio, con el entorno existente `tesis-fcl` (sin instalar dependencias):

```bash
conda activate tesis-fcl
python scripts/reproduce_ablacion_variables.py      # regenera reports/sprint_08/ablacion/
python -m unittest tests.test_ablacion_variables -v  # pruebas de aislamiento, pliegues y métricas
```

El notebook `notebooks/sprint_08/12_ablacion_variables.ipynb` explica el método y muestra los resultados;
toda la lógica está en `src/ablacion_variables.py`. La ejecución es determinista (Ridge con solver SVD):
dos corridas producen archivos idénticos. No usa red ni datos de prueba 2022–2025.
"""


def run(out=None):
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    antes = _archivos()
    spec = verificar_modelo_original()
    entrenamiento, cols = cargar_entrenamiento()
    assert cols == spec['E2']
    cfg = configuracion(cols, spec)
    cfg['validacion_anidada'] = protocolo_anidado()
    # Ambos protocolos se escriben antes de calcular cualquier métrica.
    (out / 'configuracion.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    replica = verificar_replica_sprint06(entrenamiento, cols)
    pred, ajustes, folds = ejecutar(entrenamiento, cols)
    tpl, anual = tabla_pliegues(entrenamiento, folds)
    s06 = pd.read_csv(ROOT / 'reports/sprint_06/mejoras/cv_folds.csv').query('grupo == "todas"')[['moneda', 'fold', 'n_train', 'n_validacion']].drop_duplicates()
    pd.testing.assert_frame_equal(tpl.loc[tpl.evaluable, ['moneda', 'fold', 'n_train', 'n_validacion']].reset_index(drop=True),
                                  s06.sort_values(['moneda', 'fold']).reset_index(drop=True), check_dtype=False)
    m = metricas_por_anio(pred)
    comp = comparaciones(m)
    res = resumen(comp, pred)
    conj = []
    extras = {}
    for moneda, g in res.groupby('moneda'):
        cand = g.loc[g.clasificacion.eq('Candidata a retirar'), 'atributo_retirado'].tolist()
        if cand:
            extras[moneda] = (cand, [c for c in cols if c not in cand])
    pred_conj = []
    for moneda, (cand, columnas) in extras.items():
        p, aj, _ = ejecutar(entrenamiento.loc[entrenamiento.Moneda.eq(moneda)], cols, {f'conjunta_sin_{len(cand)}_candidatas': (cand, columnas)})
        p = p.loc[p.variante.str.startswith('conjunta')]
        pred_conj.append(p)
        ajustes = pd.concat([ajustes, aj.loc[aj.variante.str.startswith('conjunta')]], ignore_index=True)
        mm = metricas_por_anio(pd.concat([pred.loc[pred.variante.eq(REFERENCIA) & pred.moneda.eq(moneda)], p]))
        rc = resumen(comparaciones(mm), pd.concat([pred.loc[pred.variante.eq(REFERENCIA) & pred.moneda.eq(moneda)], p])).iloc[0].to_dict()
        mejor = res.loc[res.moneda.eq(moneda) & res.atributo_retirado.isin(cand), 'delta_RMSE_medio_pct'].min()
        mantiene = rc['delta_RMSE_medio_pct'] <= -UMBRAL_PRACTICO_PCT and rc['anios_mejora_RMSE'] >= math.ceil(FRACCION_ANIOS_CONSISTENCIA * rc['anios_evaluables'])
        rc['mejor_delta_individual_pct'] = mejor
        rc['conclusion_conjunta'] = ('La mejora se mantiene bajo la misma regla.' if mantiene else 'La mejora no se mantiene bajo la misma regla.') + \
            f' Mejor cambio individual: {mejor:+.2f} %.'
        conj.append(rc)
        comp = pd.concat([comp, comparaciones(mm)], ignore_index=True)
    conj = pd.DataFrame(conj, columns=list(res.columns) + ['mejor_delta_individual_pct', 'conclusion_conjunta'])
    todas_pred = pd.concat([pred, *pred_conj], ignore_index=True)
    sens, casos_dom = sensibilidad_caso_dominante(pred)
    for nombre in ['sin_observacion_dominante', 'sin_empresa_dominante']:
        c = sens.loc[sens.sensibilidad.eq(nombre)].set_index(['moneda', 'atributo_retirado']).clasificacion
        res[f'clasificacion_{nombre}'] = [c[(m, a)] for m, a in zip(res.moneda, res.atributo_retirado)]
    # Síntesis descriptiva: candidata bajo la regla principal y bajo ambas sensibilidades post hoc.
    res['candidata_robusta_a_casos_dominantes'] = (res.clasificacion.eq('Candidata a retirar')
                                                   & res.clasificacion_sin_observacion_dominante.eq('Candidata a retirar')
                                                   & res.clasificacion_sin_empresa_dominante.eq('Candidata a retirar'))
    conc = concentracion_error_referencia(pred)
    m_all = metricas_por_anio(todas_pred)
    rutas = graficos(res, comp, out)
    # Parte A: validación temporal anidada.
    pred_a, hist_a, int_a, sel_a = ejecutar_anidada(entrenamiento, cols)
    anual_a, pares_a, res_a = resumen_anidada(pred_a)
    freq_a, alphas_a = frecuencias(sel_a, cols)
    final_a, hist_final = ejecutar_final(entrenamiento, cols)
    rutas += graficos_anidada(anual_a, sel_a, cols, out)
    despues = _archivos()
    assert antes == despues, 'La ablación modificó archivos previos'
    try:
        git_mod = [x[3:] for x in subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain', '--untracked-files=no'],
                                                 capture_output=True, text=True, check=True).stdout.splitlines()]
    except (OSError, subprocess.CalledProcessError):
        git_mod = []
    integridad = dict(archivos_verificados=len(antes), sin_cambios_durante_ejecucion=True, git_modificados_previos=git_mod,
                      filas_entrenamiento=len(entrenamiento), filas_prueba_usadas=0, replica_sprint06_dif_rel_max=replica)
    salidas = {'pliegues.csv': tpl, 'tamanos_por_anio.csv': anual, 'metricas_por_variante_anio.csv': m_all, 'comparaciones_pareadas.csv': comp,
               'resumen_ablacion.csv': res, 'retirada_conjunta.csv': conj, 'predicciones_validacion.csv': todas_pred, 'ajustes.csv': ajustes,
               'sensibilidad_caso_dominante.csv': sens, 'casos_dominantes.csv': casos_dom, 'concentracion_error_referencia.csv': conc,
               'anidada_pliegues_externos.csv': sel_a, 'anidada_pliegues_internos.csv': int_a, 'anidada_historial_seleccion.csv': hist_a,
               'anidada_predicciones_externas.csv': pred_a, 'anidada_metricas_por_anio.csv': anual_a, 'anidada_comparaciones_pareadas.csv': pares_a,
               'anidada_resumen.csv': res_a, 'anidada_frecuencia_retirada.csv': freq_a, 'anidada_frecuencia_alpha.csv': alphas_a,
               'anidada_lista_final_propuesta.csv': final_a, 'anidada_historial_lista_final.csv': hist_final}
    for nombre, t in salidas.items():
        t.to_csv(out / nombre, index=False, float_format='%.15g')
    (out / 'integridad.json').write_text(json.dumps(integridad, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    individual = informe(cfg, tpl, res, conj, comp, replica, integridad, sens, casos_dom, conc)
    individual = '\n'.join('## Parte B — Diagnóstico de ablación individual (condicionado a Ridge con alpha = 1; no es selección definitiva)' if l.startswith('# ')
                           else ('#' + l if l.startswith('##') else l) for l in individual.splitlines())
    texto = cabecera(res_a, final_a, res, replica, sel_a) + informe_anidada(cfg['validacion_anidada'], int_a, sel_a, res_a, pares_a, freq_a, alphas_a, final_a, cols)
    (out / 'informe_ablacion.md').write_text('\n'.join(texto) + '\n' + individual + '\n', encoding='utf-8')
    (out / 'REPRODUCIR.md').write_text(REPRODUCIR, encoding='utf-8')
    return dict(salidas, graficos=rutas, configuracion=cfg)


# ---------------------------------------------------------------------------
# Revisión exploratoria (cierre de la etapa): elección entre retiradas admisibles,
# rejilla de alpha ampliada una sola vez y referencias simples. Los años externos ya se examinaron.
# ---------------------------------------------------------------------------
OUT_REVISION = ROOT / 'reports/sprint_08/ablacion_revision'


def protocolo_revision():
    base = protocolo_anidado()
    base['eliminacion_hacia_atras']['eleccion'] = ('se evalúan todas las retiradas del paso; son admisibles las que cumplen umbral y estabilidad; '
                                                   'se elige la de menor RMSE interno entre las admisibles (empate: orden E2); se detiene solo si ninguna es admisible')
    base.update({
        'caracter': 'EXPLORATORIA: los años externos 2017–2021 ya se examinaron en la ejecución anterior; no es confirmación independiente ni prueba final.',
        'cambios_frente_a_ejecucion_anterior': [
            'seleccionar(): la versión anterior se detenía si la retirada de menor RMSE no era admisible, aunque otra sí lo fuera (corregido).',
            f'rejilla de alpha ampliada una sola vez a {list(ALPHAS_REVISION)}, idéntica para completo y reducido; alpha se elige solo en pliegues internos.',
            'referencias simples en las mismas filas y años externos.'],
        'rejilla_alpha': list(ALPHAS_REVISION),
        'regla_limite_rejilla': 'si alguna selección vuelve a elegir el máximo (1e6), se documenta la limitación y no se amplía de nuevo',
        'referencias_simples': {
            'media_historica': 'promedio de objetivo_fcl_t1 en el entrenamiento externo (años objetivo < año externo), por moneda',
            'persistencia': 'FCL(t) = FCL_preliminar(t) invalidado si CAPEX_reportado(t) > 0 (misma regla que el objetivo; igual al objetivo de la fila t-1); '
                            'si falta, respaldo con la media histórica del entrenamiento externo. FCL_preliminar_lag1 es FCL(t-1) y no se usa.'},
        'regla_modelo_frente_a_referencias': f'mejora consistente si el RMSE anual medio es <= -{UMBRAL_SELECCION_PCT:g} % frente a la referencia y menor en >= '
                                             f'{MIN_ANIOS_EXTERNOS_MEJORA} de {len(ANIOS_EXTERNOS)} años externos; sin mejora si el RMSE anual medio no es menor; si no, mejora no consistente',
        'procedimientos': {'completo_alpha_interno': '26 atributos, alpha interno (rejilla ampliada)', 'reducido': 'atributos y alpha internos (rejilla ampliada)',
                           'E2_alpha_1': 'contexto: E2 original con alpha=1.0', 'media_historica': 'referencia simple', 'persistencia': 'referencia simple'}})
    return base


def frente_a_referencias(anual):
    filas = []
    for m in sorted(anual.moneda.unique()):
        a = anual.loc[anual.moneda.eq(m)].set_index(['procedimiento', 'anio_externo'])
        for modelo in ['completo_alpha_interno', 'reducido']:
            for ref in REFERENCIAS_SIMPLES:
                d = {x: a.loc[modelo, x] - a.loc[ref, x] for x in ['RMSE', 'MAE']}
                rm, rr = a.loc[modelo, 'RMSE'].mean(), a.loc[ref, 'RMSE'].mean()
                mm, mr = a.loc[modelo, 'MAE'].mean(), a.loc[ref, 'MAE'].mean()
                mejora_anios = int((d['RMSE'] < -TOLERANCIA_EMPATE_REL * a.loc[ref, 'RMSE']).sum())
                pct = 100 * (rm - rr) / rr
                veredicto = ('mejora consistente' if pct <= -UMBRAL_SELECCION_PCT and mejora_anios >= MIN_ANIOS_EXTERNOS_MEJORA
                             else 'sin mejora' if pct >= 0 else 'mejora no consistente')
                filas.append(dict(moneda=m, modelo=modelo, referencia=ref, RMSE_anual_medio_modelo=rm, RMSE_anual_medio_referencia=rr, delta_RMSE_anual_medio_pct=pct,
                                  MAE_anual_medio_modelo=mm, MAE_anual_medio_referencia=mr, delta_MAE_anual_medio_pct=100 * (mm - mr) / mr,
                                  anios_modelo_mejor_RMSE=mejora_anios, anios_modelo_mejor_MAE=int((d['MAE'] < 0).sum()),
                                  peor_anio_delta_RMSE_pct=float((100 * d['RMSE'] / a.loc[ref, 'RMSE']).max()), veredicto=veredicto))
    return pd.DataFrame(filas)


def comparar_con_anterior(sel_nueva, res_nueva, final_nueva):
    previo = OUT / 'anidada_pliegues_externos.csv'
    if not previo.exists():
        return pd.DataFrame(), pd.DataFrame()
    sel_v = pd.read_csv(previo, keep_default_na=False)
    res_v = pd.read_csv(OUT / 'anidada_resumen.csv')
    fin_v = pd.read_csv(OUT / 'anidada_lista_final_propuesta.csv', keep_default_na=False)
    a = sel_v[['moneda', 'anio_externo', 'alpha_completo', 'alpha_reducido', 'retirados']].merge(
        sel_nueva[['moneda', 'anio_externo', 'alpha_completo', 'alpha_reducido', 'retirados', 'motivo_parada']], on=['moneda', 'anio_externo'],
        suffixes=('_anterior', '_revision'), validate='one_to_one')
    fin = fin_v[['moneda', 'alpha_completo', 'alpha_reducido', 'retirados']].assign(anio_externo='final_2021').merge(
        final_nueva[['moneda', 'alpha_completo', 'alpha_reducido', 'retirados']].assign(anio_externo='final_2021'), on=['moneda', 'anio_externo'],
        suffixes=('_anterior', '_revision'))
    a = pd.concat([a.astype({'anio_externo': str}), fin], ignore_index=True)
    a['seleccion_cambia'] = a.retirados_anterior.ne(a.retirados_revision.fillna(''))
    m = res_v[['procedimiento', 'moneda', 'RMSE_anual_medio', 'MAE_anual_medio', 'RMSE_concatenado']].merge(
        res_nueva[['procedimiento', 'moneda', 'RMSE_anual_medio', 'MAE_anual_medio', 'RMSE_concatenado']], on=['procedimiento', 'moneda'],
        suffixes=('_anterior', '_revision'), how='outer')
    m['cambio_RMSE_anual_medio_pct'] = 100 * (m.RMSE_anual_medio_revision - m.RMSE_anual_medio_anterior) / m.RMSE_anual_medio_anterior
    return a, m


def decision_final(res, refs, sel, final):
    filas = []
    tope = max(ALPHAS_REVISION)
    for m, r in res.loc[res.procedimiento.eq('reducido')].set_index('moneda').iterrows():
        regla = r.recomendacion
        decision = ('Proponer subconjunto reducido (limitaciones: selección y evaluación sobre años ya examinados)' if regla.startswith('Reducir')
                    else 'Conservar los 26 atributos' if regla == 'Conservar modelo completo'
                    else 'Evidencia insuficiente para reducir; se mantienen los 26 atributos como configuración vigente')
        s = sel.loc[sel.moneda.eq(m)]
        f = final.loc[final.moneda.eq(m)].iloc[0]
        en_tope = int((s.alpha_completo == tope).sum() + (s.alpha_reducido == tope).sum() + (f.alpha_completo == tope) + (f.alpha_reducido == tope))
        rf = refs.loc[refs.moneda.eq(m) & refs.modelo.eq('completo_alpha_interno')].set_index('referencia')
        aporta = all(rf.veredicto.eq('mejora consistente'))
        filas.append(dict(moneda=m, regla_reducido_vs_completo=regla, decision=decision, delta_RMSE_reducido_pct=r.delta_RMSE_anual_medio_pct,
                          anios_mejora_reducido=int(r.anios_mejora_RMSE), anios_empeora_reducido=int(r.anios_empeora_RMSE), selecciones_alpha_en_maximo=en_tope,
                          delta_RMSE_modelo_vs_media_pct=rf.loc['media_historica', 'delta_RMSE_anual_medio_pct'],
                          delta_RMSE_modelo_vs_persistencia_pct=rf.loc['persistencia', 'delta_RMSE_anual_medio_pct'],
                          modelo_vs_media=rf.loc['media_historica', 'veredicto'], modelo_vs_persistencia=rf.loc['persistencia', 'veredicto'],
                          modelo_aporta_mejora_consistente_frente_a_referencias=aporta, lista_final_propuesta=f.retirados or ''))
    return pd.DataFrame(filas)


def informe_revision(proto, sel, res, anual, refs, respaldo, comp_sel, comp_met, dec, final, git_mod):
    tope = max(ALPHAS_REVISION)
    L = ['# Sprint 08 — Revisión de la evaluación de variables (exploratoria) y cierre de la etapa', '',
         f'**Carácter:** {proto["caracter"]} Solo entrenamiento (años objetivo ≤ 2021), por moneda; prueba 2022–2025 no interviene. '
         'Resultados anteriores preservados en `reports/sprint_08/ablacion/`.', '',
         '## Cambios de esta revisión', ''] + [f'- {x}' for x in proto['cambios_frente_a_ejecucion_anterior']] + [
         f'- Umbrales, años externos e internos, máximo de {MAX_RETIRADAS} retiradas y reglas de decisión: sin cambios.', '',
         '## Decisión final por moneda', '']
    for d in dec.itertuples():
        L.append(f'- **{d.moneda}: {d.decision}.** Reducido frente a completo: RMSE anual medio {d.delta_RMSE_reducido_pct:+.2f} %, mejora en '
                 f'{d.anios_mejora_reducido} y empeora en {d.anios_empeora_reducido} de {len(ANIOS_EXTERNOS)} años (regla: {d.regla_reducido_vs_completo}). Frente a referencias simples, el modelo completo '
                 f'{"aporta" if d.modelo_aporta_mejora_consistente_frente_a_referencias else "NO aporta"} una mejora consistente '
                 f'(media histórica: {d.modelo_vs_media}, RMSE {d.delta_RMSE_modelo_vs_media_pct:+.2f} %; persistencia: {d.modelo_vs_persistencia}, RMSE {d.delta_RMSE_modelo_vs_persistencia_pct:+.2f} %). '
                 f'Lista final propuesta por el procedimiento: '
                 f'{d.lista_final_propuesta.replace(";", ", ") or "sin retiradas"} (pendiente de evaluación posterior).')
    L += ['', '## Regularización', '']
    for m, g in sel.groupby('moneda'):
        f = final.loc[final.moneda.eq(m)].iloc[0]
        n = int((g.alpha_completo == tope).sum() + (g.alpha_reducido == tope).sum())
        L.append(f'- {m}: alpha completo por año externo {", ".join(f"{a:g}" for a in g.alpha_completo)}; reducido {", ".join(f"{a:g}" for a in g.alpha_reducido)}; '
                 f'final {f.alpha_completo:g}/{f.alpha_reducido:g}. Selecciones en el máximo (1e6): {n} de {2 * len(g)} externas'
                 + (f' y {int(f.alpha_completo == tope) + int(f.alpha_reducido == tope)} de 2 finales.' if True else '.'))
    if (dec.selecciones_alpha_en_maximo > 0).any():
        L.append('- **Limitación:** la selección vuelve a alcanzar el máximo de la rejilla ampliada en al menos una moneda; la regularización óptima puede ser mayor. '
                 'Conforme al protocolo, no se amplía de nuevo y la etapa se cierra con esta limitación documentada.')
    else:
        L.append('- Ninguna selección alcanza el máximo de la rejilla ampliada.')
    L += ['', '## Métricas externas por moneda (promedio de años; RMSE y MAE en unidad monetaria reportada)', '',
          '| moneda | procedimiento | RMSE anual medio | MAE anual medio | RMSE concatenado | MAE concatenado |', '|---|---|---|---|---|---|']
    orden = ['media_historica', 'persistencia', 'completo_alpha_interno', 'reducido', 'E2_alpha_1']
    for r in res.assign(o=res.procedimiento.map(orden.index)).sort_values(['moneda', 'o']).itertuples():
        L.append(f'| {r.moneda} | {r.procedimiento} | {r.RMSE_anual_medio:,.0f} | {r.MAE_anual_medio:,.0f} | {r.RMSE_concatenado:,.0f} | {r.MAE_concatenado:,.0f} |')
    L += ['', 'Las concatenadas ponderan años por número de filas; el criterio es el promedio anual. Detalle por año: `metricas_por_anio.csv`.', '',
          '## Modelo frente a referencias simples', '',
          '| moneda | modelo | referencia | ΔRMSE anual medio % | ΔMAE anual medio % | años mejor (RMSE) | años mejor (MAE) | peor año ΔRMSE % | veredicto |', '|---|---|---|---|---|---|---|---|---|']
    for r in refs.itertuples():
        L.append(f'| {r.moneda} | {r.modelo} | {r.referencia} | {r.delta_RMSE_anual_medio_pct:+.2f} | {r.delta_MAE_anual_medio_pct:+.2f} | {r.anios_modelo_mejor_RMSE} | '
                 f'{r.anios_modelo_mejor_MAE} | {r.peor_anio_delta_RMSE_pct:+.2f} | {r.veredicto} |')
    L += ['', 'Filas de persistencia con respaldo en la media histórica (FCL(t) no válido o ausente): '
          + '; '.join(f'{m} {int(g.usa_respaldo_media.sum())} de {len(g)}' for m, g in respaldo.groupby('moneda')) + '. No se elimina ninguna fila.', '',
          '## Selección por pliegue y comparación con la ejecución anterior', '',
          '| moneda | año externo | retirados (anterior) | retirados (revisión) | alpha completo ant./rev. | alpha reducido ant./rev. | motivo de parada (revisión) |', '|---|---|---|---|---|---|---|']
    for r in comp_sel.itertuples():
        L.append(f'| {r.moneda} | {r.anio_externo} | {r.retirados_anterior.replace(";", ", ") or "—"} | {(r.retirados_revision or "").replace(";", ", ") or "—"} | '
                 f'{r.alpha_completo_anterior:g}/{r.alpha_completo_revision:g} | {r.alpha_reducido_anterior:g}/{r.alpha_reducido_revision:g} | '
                 f'{r.motivo_parada if isinstance(r.motivo_parada, str) else "—"} |')
    L += ['', 'Cambio del RMSE anual medio externo respecto a la ejecución anterior: '
          + '; '.join(f'{r.moneda} {r.procedimiento} {r.cambio_RMSE_anual_medio_pct:+.2f} %' for r in comp_met.dropna(subset=['cambio_RMSE_anual_medio_pct']).itertuples()) + '.', '',
          '## Limitaciones', '',
          '- Revisión exploratoria sobre años externos ya examinados: cualquier mejora observada aquí no es una estimación independiente.',
          '- Cinco años externos por moneda; dólares con 21–26 filas por año y errores dominados por pocas empresas (ver ejecución anterior).',
          '- Sin fechas de publicación ni vintages: la separación por ejercicio no acredita disponibilidad real de la información.',
          '- La persistencia usa FCL(t), que exige conocer los estados de t al pronosticar, con la misma condición de disponibilidad que los atributos.',
          f'- Cambios del usuario en archivos rastreados presentes y no modificados: {", ".join(git_mod) or "ninguno"}.', '',
          '## Archivos', '',
          '`configuracion.json`, `pliegues_externos.csv`, `pliegues_internos.csv`, `historial_seleccion.csv`, `historial_lista_final.csv`, `predicciones_externas.csv`, '
          '`metricas_por_anio.csv`, `comparaciones_pareadas.csv`, `resumen.csv`, `frente_a_referencias.csv`, `respaldo_persistencia.csv`, `comparacion_seleccion_anterior.csv`, '
          '`comparacion_metricas_anterior.csv`, `decision_final.csv`, `lista_final_propuesta.csv`, `integridad.json`. Reproducción: `python scripts/reproduce_ablacion_variables.py --revision`.']
    return '\n'.join(L) + '\n'


def run_revision(out=None):
    out = Path(out or OUT_REVISION)
    out.mkdir(parents=True, exist_ok=True)
    # Verifica todo lo previo, incluida la ejecución anterior en reports/sprint_08/ablacion/; excluye solo esta salida.
    propia = out.resolve().relative_to(ROOT).as_posix() + '/' if out.resolve().is_relative_to(ROOT) else '\0'
    archivos = lambda: _archivos(excluir=(propia,))
    antes = archivos()
    verificar_modelo_original()
    entrenamiento, cols = cargar_entrenamiento()
    proto = protocolo_revision()
    (out / 'configuracion.json').write_text(json.dumps(proto, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')  # antes de calcular
    pred, hist, internos, sel = ejecutar_anidada(entrenamiento, cols, revision=True)
    anual, pares, res = resumen_anidada(pred)
    refs = frente_a_referencias(anual)
    respaldo = pred.loc[pred.procedimiento.eq('persistencia'), ['moneda', 'anio_objetivo', 'id_fila', 'usa_respaldo_media']]
    resp_tab = respaldo.groupby(['moneda', 'anio_objetivo']).usa_respaldo_media.agg(['sum', 'size']).rename(columns={'sum': 'filas_con_respaldo', 'size': 'filas'}).reset_index()
    final, hist_final = ejecutar_final(entrenamiento, cols, revision=True)
    comp_sel, comp_met = comparar_con_anterior(sel, res, final)
    dec = decision_final(res, refs, sel, final)
    assert antes == archivos(), 'La revisión modificó archivos previos'
    try:
        git_mod = [x[3:] for x in subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain', '--untracked-files=no'],
                                                 capture_output=True, text=True, check=True).stdout.splitlines()]
    except (OSError, subprocess.CalledProcessError):
        git_mod = []
    salidas = {'pliegues_externos.csv': sel, 'pliegues_internos.csv': internos, 'historial_seleccion.csv': hist, 'historial_lista_final.csv': hist_final,
               'predicciones_externas.csv': pred, 'metricas_por_anio.csv': anual, 'comparaciones_pareadas.csv': pares, 'resumen.csv': res,
               'frente_a_referencias.csv': refs, 'respaldo_persistencia.csv': resp_tab, 'comparacion_seleccion_anterior.csv': comp_sel,
               'comparacion_metricas_anterior.csv': comp_met, 'decision_final.csv': dec, 'lista_final_propuesta.csv': final}
    for nombre, t in salidas.items():
        t.to_csv(out / nombre, index=False, float_format='%.15g')
    (out / 'integridad.json').write_text(json.dumps(dict(archivos_verificados=len(antes), sin_cambios_durante_ejecucion=True, git_modificados_previos=git_mod,
                                                         filas_entrenamiento=len(entrenamiento), filas_prueba_usadas=0,
                                                         resultados_anteriores_preservados='reports/sprint_08/ablacion/ (solo lectura)'),
                                                    ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (out / 'informe_revision.md').write_text(informe_revision(proto, sel, res, anual, refs, respaldo, comp_sel, comp_met, dec, final, git_mod), encoding='utf-8')
    return salidas
