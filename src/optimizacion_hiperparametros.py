"""Sesión IA07 — Optimización de hiperparámetros de Ridge: Random Search frente a Optuna TPE.

Conserva los datos, la partición temporal y el baseline Ridge de los notebooks 07 y 08. Las ventanas y el criterio
son los del notebook 08: ventanas expansivas de dos años objetivo y media del MSE por año de validación.
Ambos métodos usan el mismo objetivo, las mismas ventanas y el mismo número de trials; solo cambia el muestreador.
Etapas: protocolo -> búsqueda (solo entrenamiento) -> congelación con hash -> evaluación única en prueba.
Sin pruning ni early stopping: Ridge se resuelve en forma cerrada; las limitaciones están en reports/ia07/informe_resultados.md.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import subprocess
import time
import numpy as np
import pandas as pd
import scipy
import sklearn
from joblib import Parallel, delayed
from scipy.stats import mannwhitneyu, spearmanr, wilcoxon
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
import optuna

optuna.logging.set_verbosity(optuna.logging.WARNING)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/ia07'
PANEL = ROOT / 'data/processed/panel_financiero_macro_bursatil.csv'

MACRO = ['inflacion_lima_dic_dic_pct', 'tipo_cambio_promedio_soles_usd', 'tasa_referencia_promedio_pct', 'crecimiento_pbi_real_pct']
BOLSA = ['rentabilidad_indice_anual_pct', 'volatilidad_diaria_anualizada_pct', 'monto_renta_variable_anual_millones_pen']
EXTERNAS = MACRO + BOLSA
NIVELES = ['FCL_t_verificado', 'FCO_t']
REDUNDANTES = {'fcl_activo', 'FCO_mean3_previa', 'FCL_preliminar_mean3_previa'}

COHORTES = (('D lares', 'todas'), ('Soles', 'todas'), ('Soles', 'no_bancario'), ('Soles', 'bancario'))
# Selección de características ya congelada por CV en el notebook 08 (seleccion_congelada_cv.csv); aquí no se vuelve a buscar.
SELECCION_08 = {('D lares', 'todas'): ('niveles_t_externos_t_1', 'E1_macroeconomico'), ('Soles', 'todas'): ('niveles_t_externos_t', 'E1_macroeconomico'),
                ('Soles', 'no_bancario'): ('sin_niveles_t_externos_t_1', 'E2_bursatil'), ('Soles', 'bancario'): ('niveles_t_externos_t_1', 'E1_macroeconomico')}
CARACTERISTICAS = ('E0_07', 'E1_07', 'E2_07', 'seleccion_08')

ALPHA_MIN, ALPHA_MAX = 1e-2, 1e7
ESCALADORES = ('standard', 'robust')
RECORTES = {'sin_recorte': None, 'p01_p99': (.01, .99), 'p05_p95': (.05, .95)}
METODOS = ('random_search', 'tpe')
PRESUPUESTO = 60
TPE_INICIALES = 10
SEMILLAS = tuple(20261103 + i for i in range(20))
SEMILLA_PRINCIPAL = SEMILLAS[0]
HITOS = (6, 10, 20, 30, 60)
ALPHAS_08 = (.1, 1., 10., 100., 1000., 10000.)
N_ALPHAS_DENSA = 181
ID_ESTUDIO = ['moneda', 'grupo', 'caracteristicas']


def cargar_muestra():
    """Devuelve (muestra, muestra con externos t-1, financieros, ratios) con los mismos 3.560 casos de los notebooks 07 y 08."""
    datos = pd.read_csv(PANEL, dtype={'RPJ': 'string', 'RUC': 'string'}, float_precision='round_trip')
    assert datos.shape == (4221, 68)
    m = datos.loc[datos.utilizable_supervisado].copy()
    m['id_fila'] = m.index
    assert len(m) == 3560 and m.particion.value_counts().to_dict() == {'entrenamiento': 2869, 'prueba': 691}
    assert m.loc[m.particion.eq('entrenamiento'), 'anio_objetivo'].max() == 2021 and m.loc[m.particion.eq('prueba'), 'anio_objetivo'].min() == 2022
    m['grupo_bancario'] = np.where(m.TipoSector.eq('BANCOS'), 'bancario', 'no_bancario')
    m['FCL_t_verificado'] = (m.FCO + m.CAPEX_reportado).where(~m.CAPEX_reportado.gt(0))
    m['FCO_t'] = m.FCO
    cat = pd.read_csv(ROOT / 'reports/diccionario_integracion_bursatil.csv', keep_default_na=False)
    fin22 = cat.loc[cat.origen.eq('SMV/Feature Engineering') & cat.predictor_candidato.astype(str).eq('True'), 'variable'].tolist()
    fin = [v for v in fin22 if v not in REDUNDANTES]
    ratios = [c for c in fin if '_lag' not in c and '_std3_' not in c]
    assert len(fin) == 19 and len(ratios) == 11
    ma = pd.read_csv(ROOT / 'data/processed/macroeconomia_peru_2005_2025.csv', float_precision='round_trip')
    ba = pd.read_csv(ROOT / 'data/processed/bursatil_mercado_anual.csv', float_precision='round_trip')
    anual = ma[['anio', *MACRO]].merge(ba[['anio', *BOLSA]], on='anio', validate='one_to_one').set_index('anio')
    lag = m.copy()
    for v in EXTERNAS:
        lag[v] = lag.Ejercicio.sub(1).map(anual[v])
    return m, lag, fin, ratios


def especificacion_08(spec, exp, fin):
    base = fin + NIVELES if not spec.startswith('sin_niveles') else list(fin)
    return base + {'E0_financiero': [], 'E1_macroeconomico': MACRO, 'E2_bursatil': EXTERNAS}[exp]


def caracteristicas(nombre, cohorte, m, lag, fin):
    """(tabla, columnas) de un conjunto de características fijo; nunca se elige dentro de la búsqueda."""
    if nombre != 'seleccion_08':
        return m, fin + {'E0_07': [], 'E1_07': MACRO, 'E2_07': EXTERNAS}[nombre]
    spec, exp = SELECCION_08[cohorte]
    return (m if spec == 'niveles_t_externos_t' else lag), especificacion_08(spec, exp, fin)


def subconjunto(tabla, moneda, grupo):
    mascara = tabla.Moneda.eq(moneda)
    if grupo != 'todas':
        mascara &= tabla.grupo_bancario.eq(grupo)
    return tabla.loc[mascara]


def solo_entrenamiento(tabla):
    return tabla.loc[tabla.particion.eq('entrenamiento')]


def pliegues(entrenamiento):
    """Ventanas del notebook 08: ocho años iniciales (cinco en banca) y bloques de validación de dos años objetivo."""
    assert entrenamiento.particion.eq('entrenamiento').all()
    anios = sorted(entrenamiento.anio_objetivo.unique())
    assert len(anios) >= 6
    inicial = 8 if len(anios) >= 12 else max(4, len(anios) - 4)
    salida = []
    for i in range(inicial, len(anios), 2):
        previos, validacion = anios[:i], anios[i:i + 2]
        a = entrenamiento.index[entrenamiento.anio_objetivo.isin(previos)]
        b = entrenamiento.index[entrenamiento.anio_objetivo.isin(validacion)]
        assert max(previos) < min(validacion)
        salida.append((a, b))
    return salida


class ClipRatios(BaseEstimator, TransformerMixin):
    """Recorte de ratios del notebook 08: cuantiles aprendidos en entrenamiento, después de imputar."""

    def __init__(self, feature_names, ratio_names, q_low=.01, q_high=.99):
        self.feature_names = feature_names
        self.ratio_names = ratio_names
        self.q_low = q_low
        self.q_high = q_high

    def fit(self, X, y=None):
        z = np.asarray(X, dtype=float)
        self.indices_ = np.array([i for i, c in enumerate(self.feature_names) if c in self.ratio_names], dtype=int)
        self.lower_ = np.quantile(z[:, self.indices_], self.q_low, axis=0)
        self.upper_ = np.quantile(z[:, self.indices_], self.q_high, axis=0)
        return self

    def transform(self, X):
        z = np.array(X, dtype=float, copy=True)
        z[:, self.indices_] = np.clip(z[:, self.indices_], self.lower_, self.upper_)
        return z


def crear_preparador(cols, ratios, escalador='standard', recorte='sin_recorte'):
    pasos = [('imputer', SimpleImputer(strategy='median', keep_empty_features=True))]
    if RECORTES[recorte] is not None:
        pasos.append(('clip', ClipRatios(cols, ratios, *RECORTES[recorte])))
    pasos.append(('scaler', StandardScaler() if escalador == 'standard' else RobustScaler(quantile_range=(25, 75))))
    return ColumnTransformer([('numericas', Pipeline(pasos), cols)], remainder='drop', verbose_feature_names_out=False)


def crear_pipeline(cols, ratios, alpha, escalador='standard', recorte='sin_recorte'):
    return Pipeline([('preparacion', crear_preparador(cols, ratios, escalador, recorte)), ('ridge', Ridge(alpha=alpha, solver='svd', fit_intercept=True))])


class EvaluadorCV:
    """Puntúa una configuración en las ventanas temporales. Rechaza filas de prueba; el preprocesador se guarda por ventana."""

    def __init__(self, entrenamiento, cols, ratios):
        assert entrenamiento.particion.eq('entrenamiento').all(), 'la búsqueda no puede recibir filas de prueba'
        self.t, self.cols, self.ratios = entrenamiento, cols, ratios
        self.folds = pliegues(entrenamiento)
        self._cache = {}

    def _preparar(self, escalador, recorte):
        clave = (escalador, recorte)
        if clave not in self._cache:
            salida = []
            for a, b in self.folds:
                tr, va = self.t.loc[a], self.t.loc[b]
                pre = crear_preparador(self.cols, self.ratios, escalador, recorte)
                salida.append((pre.fit_transform(tr[self.cols]), tr.objetivo_fcl_t1.to_numpy(), pre.transform(va[self.cols]), va.objetivo_fcl_t1.to_numpy(), va.anio_objetivo.to_numpy()))
            self._cache[clave] = salida
        return self._cache[clave]

    def evaluar(self, alpha, escalador='standard', recorte='sin_recorte'):
        anuales, por_fold = [], []
        for ztr, ytr, zva, yva, anios in self._preparar(escalador, recorte):
            p = Ridge(alpha=alpha, solver='svd', fit_intercept=True).fit(ztr, ytr).predict(zva)
            assert np.isfinite(p).all()
            mse = [float(np.mean((p[anios == y] - yva[anios == y]) ** 2)) for y in np.unique(anios)]
            anuales += mse
            por_fold.append(float(np.mean(mse)))
        return float(np.mean(anuales)), por_fold


def muestreador(metodo, semilla):
    """Sin pruner: el estudio se crea siempre con NopPruner, de modo que todo trial consume el presupuesto completo."""
    if metodo == 'random_search':
        return optuna.samplers.RandomSampler(seed=semilla)
    return optuna.samplers.TPESampler(seed=semilla, n_startup_trials=TPE_INICIALES)


def buscar(evaluador, metodo, semilla, presupuesto=PRESUPUESTO):
    filas = []

    def objetivo(trial):
        inicio = time.perf_counter()
        alpha = trial.suggest_float('alpha', ALPHA_MIN, ALPHA_MAX, log=True)
        escalador = trial.suggest_categorical('escalador', list(ESCALADORES))
        recorte = trial.suggest_categorical('recorte', list(RECORTES))
        mse, por_fold = evaluador.evaluar(alpha, escalador, recorte)
        filas.append(dict(trial=trial.number, alpha=alpha, escalador=escalador, recorte=recorte, mse_cv=mse, rmse_cv=float(np.sqrt(mse)),
                          **{f'mse_fold_{i}': v for i, v in enumerate(por_fold, 1)}, duracion_s=time.perf_counter() - inicio))
        return mse

    estudio = optuna.create_study(direction='minimize', sampler=muestreador(metodo, semilla), pruner=optuna.pruners.NopPruner())
    estudio.optimize(objetivo, n_trials=presupuesto, n_jobs=1, gc_after_trial=False)
    estados = {t.state.name for t in estudio.trials}
    assert estados == {'COMPLETE'} and len(filas) == presupuesto, estados
    return pd.DataFrame(filas).assign(metodo=metodo, semilla=semilla, estado='COMPLETE')


def elegir(trials):
    """Menor MSE de validación; desempate hacia mayor regularización, como en el notebook 08."""
    return trials.sort_values(['mse_cv', 'alpha', 'trial'], ascending=[True, False, True], kind='stable').iloc[0]


def protocolo():
    return {'sesion': 'IA07', 'modelo': 'Ridge(solver=svd, fit_intercept=True)', 'datos': 'data/processed/panel_financiero_macro_bursatil.csv, utilizable_supervisado; 3.560 filas sin alterar',
            'particion': 'la original: entrenamiento con año objetivo hasta 2021 (2.869 filas), prueba 2022 a 2025 (691 filas)',
            'cohortes': [list(c) for c in COHORTES], 'nota_cohortes': 'D lares/no_bancario coincide fila a fila con D lares/todas y no se repite',
            'caracteristicas': {'E0_07': 'E0 del notebook 07 (19)', 'E1_07': 'E1 del notebook 07 (23)', 'E2_07': 'E2 del notebook 07 (26)',
                                'seleccion_08': {f'{m}/{g}': list(v) for (m, g), v in SELECCION_08.items()}, 'regla': 'fijas por estudio; no forman parte del espacio de búsqueda'},
            'espacio': {'alpha': {'tipo': 'log-uniforme', 'min': ALPHA_MIN, 'max': ALPHA_MAX}, 'escalador': list(ESCALADORES), 'recorte_ratios': list(RECORTES)},
            'validacion': 'ventanas expansivas del notebook 08: bloques de dos años objetivo, cuatro ventanas (dos en banca)', 'criterio': 'media del MSE por año de validación; desempate hacia mayor alpha',
            'metodos': {'random_search': 'optuna.samplers.RandomSampler', 'tpe': f'optuna.samplers.TPESampler(n_startup_trials={TPE_INICIALES}), demás parámetros por defecto'},
            'presupuesto': {'trials_por_corrida': PRESUPUESTO, 'semillas': list(SEMILLAS), 'semilla_principal': SEMILLA_PRINCIPAL, 'hitos': list(HITOS), 'equivalencia': 'mismo objetivo, ventanas, trials y semillas; solo cambia el muestreador'},
            'pruning_early_stopping': 'no se implementan: NopPruner en todos los estudios', 'comparadores': {'ridge_alpha1': 'baseline del notebook 07: alpha=1, StandardScaler, sin recorte', 'rejilla_08': f'rejilla del notebook 08: alphas {list(ALPHAS_08)}, StandardScaler, recorte p01_p99'},
            'referencia_densa': f'{N_ALPHAS_DENSA} alphas por combinación de escalador y recorte; solo mide la distancia al óptimo y nunca selecciona',
            'seleccion': 'por estudio, método y semilla principal; por cohorte, menor MSE de validación entre sus estudios', 'prueba': 'evaluación única de configuraciones congeladas con hash; no selecciona nada; ya inspeccionada en los notebooks 07 y 08, por lo que no es confirmatoria'}


def escribir_protocolo(out=None):
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'protocolo.json').write_text(json.dumps(protocolo(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def estudios(m, lag, fin):
    return [(c, n, *caracteristicas(n, c, m, lag, fin)) for c in COHORTES for n in CARACTERISTICAS]


def _corrida(tabla, cols, ratios, cohorte, nombre, metodo, semilla, presupuesto):
    ev = EvaluadorCV(solo_entrenamiento(subconjunto(tabla, *cohorte)), cols, ratios)
    return buscar(ev, metodo, semilla, presupuesto).assign(moneda=cohorte[0], grupo=cohorte[1], caracteristicas=nombre)


def _comparadores_y_densa(tabla, cols, ratios, cohorte, nombre):
    ev = EvaluadorCV(solo_entrenamiento(subconjunto(tabla, *cohorte)), cols, ratios)
    id_ = dict(moneda=cohorte[0], grupo=cohorte[1], caracteristicas=nombre)
    mse1 = ev.evaluar(1., 'standard', 'sin_recorte')[0]
    comparadores = [dict(id_, procedimiento='ridge_alpha1', alpha=1., escalador='standard', recorte='sin_recorte', mse_cv=mse1)]
    rejilla = pd.DataFrame([dict(alpha=a, mse_cv=ev.evaluar(a, 'standard', 'p01_p99')[0], trial=i) for i, a in enumerate(ALPHAS_08)])
    g = elegir(rejilla)
    comparadores.append(dict(id_, procedimiento='rejilla_08', alpha=float(g.alpha), escalador='standard', recorte='p01_p99', mse_cv=float(g.mse_cv)))
    densa = [dict(id_, alpha=float(a), escalador=e, recorte=r, mse_cv=ev.evaluar(float(a), e, r)[0])
             for e in ESCALADORES for r in RECORTES for a in np.geomspace(ALPHA_MIN, ALPHA_MAX, N_ALPHAS_DENSA)]
    return comparadores, densa


def plan_pliegues(m):
    filas = []
    for cohorte in COHORTES:
        t = solo_entrenamiento(subconjunto(m, *cohorte))
        for i, (a, b) in enumerate(pliegues(t), 1):
            filas.append(dict(moneda=cohorte[0], grupo=cohorte[1], fold=i, anio_entrenamiento_min=int(t.loc[a].anio_objetivo.min()), anio_entrenamiento_max=int(t.loc[a].anio_objetivo.max()),
                              anio_validacion_min=int(t.loc[b].anio_objetivo.min()), anio_validacion_max=int(t.loc[b].anio_objetivo.max()), n_entrenamiento=len(a), n_validacion=len(b)))
    return pd.DataFrame(filas)


def congelar(trials, comparadores, out):
    """Fija las configuraciones ganadoras antes de calcular cualquier métrica de prueba."""
    filas = list(comparadores.to_dict('records'))
    principal = trials.loc[trials.semilla.eq(SEMILLA_PRINCIPAL)]
    for (mo, gr, ca, me), g in principal.groupby([*ID_ESTUDIO, 'metodo'], sort=True):
        r = elegir(g)
        filas.append(dict(moneda=mo, grupo=gr, caracteristicas=ca, procedimiento=me, alpha=float(r.alpha), escalador=r.escalador, recorte=r.recorte, mse_cv=float(r.mse_cv)))
    t = pd.DataFrame(filas).sort_values([*ID_ESTUDIO, 'procedimiento'], kind='stable').reset_index(drop=True)
    t['rmse_cv'] = np.sqrt(t.mse_cv)
    t['ganador_cohorte'] = False
    for _, g in t.groupby(['moneda', 'grupo', 'procedimiento']):
        t.loc[g.sort_values(['mse_cv', 'alpha'], ascending=[True, False], kind='stable').index[0], 'ganador_cohorte'] = True
    texto = t.to_csv(index=False, float_format='%.15g')
    (out / 'seleccion_congelada.csv').write_text(texto, encoding='utf-8')
    (out / 'seleccion_congelada.json').write_text(json.dumps({'sha256': hashlib.sha256(texto.encode()).hexdigest(), 'congelada_utc': datetime.now(timezone.utc).isoformat(), 'filas': len(t)}, indent=2) + '\n', encoding='utf-8')
    return t


def ejecutar_busqueda(out=None, n_jobs=-1, semillas=SEMILLAS, presupuesto=PRESUPUESTO):
    """Etapa de búsqueda: el panel se recorta a entrenamiento en cada tarea, antes de construir el evaluador."""
    out = Path(out or OUT)
    (out / 'graficos').mkdir(parents=True, exist_ok=True)
    assert (out / 'protocolo.json').read_text(encoding='utf-8') == json.dumps(protocolo(), ensure_ascii=False, indent=2) + '\n', 'protocolo ausente o distinto del código'
    assert not (out / 'metricas_prueba.csv').exists(), 'ya hay métricas de prueba: la búsqueda no se repite sobre esa carpeta'
    m, lag, fin, ratios = cargar_muestra()
    es = estudios(m, lag, fin)
    res = Parallel(n_jobs=n_jobs)(delayed(_corrida)(solo_entrenamiento(t), cols, ratios, c, n, me, s, presupuesto) for c, n, t, cols in es for me in METODOS for s in semillas)
    trials = pd.concat(res, ignore_index=True)
    columnas = [*ID_ESTUDIO, 'metodo', 'semilla', 'trial', 'alpha', 'escalador', 'recorte', 'mse_cv', 'rmse_cv', *[c for c in trials if c.startswith('mse_fold_')], 'estado', 'duracion_s']
    trials = trials[columnas]
    res2 = Parallel(n_jobs=n_jobs)(delayed(_comparadores_y_densa)(solo_entrenamiento(t), cols, ratios, c, n) for c, n, t, cols in es)
    comparadores = pd.DataFrame([f for r in res2 for f in r[0]])
    densa = pd.DataFrame([f for r in res2 for f in r[1]])
    trials.to_csv(out / 'trials.csv', index=False, float_format='%.15g')
    densa.to_csv(out / 'referencia_densa.csv', index=False, float_format='%.15g')
    plan_pliegues(m).to_csv(out / 'pliegues.csv', index=False)
    t = congelar(trials, comparadores, out)
    return trials, densa, t


def mejor_acumulado(trials):
    t = trials.sort_values([*ID_ESTUDIO, 'metodo', 'semilla', 'trial'], kind='stable').copy()
    t['mejor_mse'] = t.groupby([*ID_ESTUDIO, 'metodo', 'semilla']).mse_cv.cummin()
    return t


def holm(p):
    """Ajuste de Holm para los estudios de un mismo hito (añadido al análisis después de ver los valores sin ajustar)."""
    p = np.asarray(p, float)
    orden = np.argsort(p, kind='stable')
    ajustado = np.maximum.accumulate(p[orden] * (len(p) - np.arange(len(p))))
    salida = np.empty(len(p))
    salida[orden] = np.minimum(ajustado, 1.)
    return salida


def _wilcoxon_pareada(diferencias):
    """p de Wilcoxon de rangos con signo sobre diferencias pareadas por semilla. Devuelve 1.0 si todas son nulas."""
    d = np.asarray(diferencias, float)
    if not np.any(d):
        return 1.
    return float(wilcoxon(d, alternative='two-sided').pvalue)


def analizar_convergencia(trials, densa):
    """Distancia al mejor valor conocido de cada estudio, en % de RMSE de validación. No usa prueba.

    Inferencia RS frente a TPE: la unidad experimental es la corrida con una semilla (20 por estudio) y ambos métodos
    comparten semillas y sus 10 primeros trials (arranque de TPE), así que las observaciones están pareadas por semilla
    y la prueba adecuada es Wilcoxon de rangos con signo sobre las diferencias TPE − RS por semilla. Mann-Whitney
    supone muestras independientes; se conserva solo como referencia histórica de la primera versión del análisis.
    Familia de hipótesis: las 16 comparaciones de estudios dentro de cada hito n_trials; el ajuste de Holm se aplica
    de forma independiente por hito (16 pruebas por familia).
    """
    t = mejor_acumulado(trials)
    mejor = pd.concat([t[[*ID_ESTUDIO, 'mse_cv']], densa[[*ID_ESTUDIO, 'mse_cv']]]).groupby(ID_ESTUDIO).mse_cv.min().rename('mse_ref').reset_index()
    t = t.merge(mejor, on=ID_ESTUDIO)
    t['brecha_pct'] = 100 * (np.sqrt(t.mejor_mse) / np.sqrt(t.mse_ref) - 1)
    t['n_trials'] = t.trial + 1
    curvas = t.groupby([*ID_ESTUDIO, 'metodo', 'n_trials']).brecha_pct.agg(mediana='median', q1=lambda s: s.quantile(.25), q3=lambda s: s.quantile(.75), maximo='max').reset_index()
    filas = []
    for k in HITOS:
        for id_, g in t.loc[t.n_trials.eq(k)].groupby(ID_ESTUDIO):
            pares = g.pivot(index='semilla', columns='metodo', values='brecha_pct')
            assert pares.notna().all().all() and set(pares.columns) == set(METODOS), 'cada semilla debe tener ambos métodos para el pareo'
            a, b = pares[METODOS[0]].to_numpy(), pares[METODOS[1]].to_numpy()
            d = b - a
            filas.append(dict(zip(ID_ESTUDIO, id_), n_trials=k, semillas=len(a), brecha_mediana_random_search=np.median(a), brecha_mediana_tpe=np.median(b),
                              brecha_maxima_random_search=a.max(), brecha_maxima_tpe=b.max(), diferencia_mediana_tpe_menos_rs=np.median(b) - np.median(a),
                              p_mann_whitney=float(mannwhitneyu(a, b, alternative='two-sided').pvalue) if not np.array_equal(a, b) else 1.,
                              p_wilcoxon=_wilcoxon_pareada(d)))
    comparacion = pd.DataFrame(filas)
    comparacion['p_holm'] = comparacion.groupby('n_trials').p_mann_whitney.transform(holm)
    comparacion['p_wilcoxon_holm'] = comparacion.groupby('n_trials').p_wilcoxon.transform(holm)
    agregado = comparacion.groupby('n_trials').agg(estudios=('moneda', 'size'), brecha_mediana_random_search=('brecha_mediana_random_search', 'median'), brecha_mediana_tpe=('brecha_mediana_tpe', 'median'),
                                                   peor_mediana_random_search=('brecha_mediana_random_search', 'max'), peor_mediana_tpe=('brecha_mediana_tpe', 'max'),
                                                   estudios_tpe_menor=('diferencia_mediana_tpe_menos_rs', lambda s: int((s < 0).sum())), estudios_rs_menor=('diferencia_mediana_tpe_menos_rs', lambda s: int((s > 0).sum())),
                                                   estudios_p_menor_005=('p_mann_whitney', lambda s: int((s < .05).sum())), estudios_p_holm_menor_005=('p_holm', lambda s: int((s < .05).sum())),
                                                   estudios_p_wilcoxon_menor_005=('p_wilcoxon', lambda s: int((s < .05).sum())), estudios_p_wilcoxon_holm_menor_005=('p_wilcoxon_holm', lambda s: int((s < .05).sum()))).reset_index()
    return curvas, comparacion, agregado


def diagnostico_pruning(trials):
    """Qué arriesgaría un pruning entre ventanas, medido con los trials de Random Search; no implementa ningún pruner."""
    filas = []
    folds = [c for c in trials if c.startswith('mse_fold_')]
    rs = trials.loc[trials.metodo.eq('random_search')]
    for id_, g in rs.groupby(ID_ESTUDIO):
        g = g.dropna(axis=1, how='all')
        fs = [c for c in folds if c in g]
        for k in range(1, len(fs)):
            parcial = g[fs[:k]].mean(axis=1)
            perdidas = []
            for _, s in g.assign(parcial=parcial).groupby('semilla'):
                perdidas.append(float(s.sort_values(['mse_cv', 'alpha'], ascending=[True, False]).iloc[0].parcial > s.parcial.median()))
            filas.append(dict(zip(ID_ESTUDIO, id_), ventanas_observadas=k, ventanas_totales=len(fs), spearman_parcial_final=float(spearmanr(parcial, g.mse_cv).statistic), semillas_donde_mediana_descartaria_ganador_pct=100 * float(np.mean(perdidas))))
    return pd.DataFrame(filas)


def importancia_descriptiva(trials):
    """Peso descriptivo de cada hiperparámetro: mejor MSE por nivel categórico, en % de RMSE sobre el mejor del estudio (no es fANOVA)."""
    filas = []
    for id_, g in trials.groupby(ID_ESTUDIO):
        mejor = np.sqrt(g.mse_cv.min())
        for h in ('escalador', 'recorte'):
            for nivel, s in g.groupby(h):
                filas.append(dict(zip(ID_ESTUDIO, id_), hiperparametro=h, nivel=nivel, trials=len(s), mejor_rmse_cv=np.sqrt(s.mse_cv.min()), brecha_con_mejor_pct=100 * (np.sqrt(s.mse_cv.min()) / mejor - 1)))
    return pd.DataFrame(filas)


def verificar_congelacion(out):
    texto = (out / 'seleccion_congelada.csv').read_text(encoding='utf-8')
    registro = json.loads((out / 'seleccion_congelada.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(texto.encode()).hexdigest() == registro['sha256'], 'seleccion_congelada.csv cambió después de congelarse'
    return registro


def medir(y, p, media, persistencia):
    y, p = np.asarray(y, float), np.asarray(p, float)
    sse = float(np.sum((p - y) ** 2))
    dm, dp = float(np.sum((y - media) ** 2)), float(np.sum((y - persistencia) ** 2))
    return dict(n=len(y), MAE=float(mean_absolute_error(y, p)), RMSE=float(root_mean_squared_error(y, p)), R2=float(r2_score(y, p, force_finite=False)), error_medio=float(np.mean(p - y)),
                R2_OOS_media=1 - sse / dm if dm > 0 else np.nan, R2_OOS_persistencia=1 - sse / dp if dp > 0 else np.nan)


def evaluar_prueba(out=None):
    """Evaluación única: requiere la selección congelada con hash y no devuelve nada a la búsqueda."""
    out = Path(out or OUT)
    registro = verificar_congelacion(out)
    assert not (out / 'metricas_prueba.csv').exists(), 'la prueba ya fue evaluada en esta carpeta'
    sel = pd.read_csv(out / 'seleccion_congelada.csv')
    m, lag, fin, ratios = cargar_muestra()
    filas, anuales, predicciones = [], [], []
    for cohorte in COHORTES:
        t0 = subconjunto(m, *cohorte)
        tr0 = solo_entrenamiento(t0)
        media, mediana = float(tr0.objetivo_fcl_t1.mean()), float(tr0.FCL_t_verificado.median())
        te0 = t0.loc[t0.particion.eq('prueba')]
        ref_media, ref_pers = np.full(len(te0), media), te0.FCL_t_verificado.fillna(mediana).to_numpy()
        id_ref = dict(moneda=cohorte[0], grupo=cohorte[1], caracteristicas='ninguna')
        for nombre, p in (('media_entrenamiento', ref_media), ('persistencia', ref_pers)):
            filas.append(dict(id_ref, procedimiento=nombre, alpha=np.nan, **medir(te0.objetivo_fcl_t1, p, ref_media, ref_pers)))
            predicciones.append(te0[['id_fila', 'anio_objetivo']].assign(**id_ref, procedimiento=nombre, y_real=te0.objetivo_fcl_t1.to_numpy(), y_predicho=p))
        for r in sel.loc[sel.moneda.eq(cohorte[0]) & sel.grupo.eq(cohorte[1])].itertuples():
            tabla, cols = caracteristicas(r.caracteristicas, cohorte, m, lag, fin)
            t = subconjunto(tabla, *cohorte)
            tr, te = solo_entrenamiento(t), t.loc[t.particion.eq('prueba')]
            assert te.id_fila.equals(te0.id_fila)
            p = crear_pipeline(cols, ratios, r.alpha, r.escalador, r.recorte).fit(tr[cols], tr.objetivo_fcl_t1).predict(te[cols])
            assert np.isfinite(p).all()
            id_ = dict(moneda=r.moneda, grupo=r.grupo, caracteristicas=r.caracteristicas)
            filas.append(dict(id_, procedimiento=r.procedimiento, alpha=r.alpha, escalador=r.escalador, recorte=r.recorte, rmse_cv=r.rmse_cv, ganador_cohorte=r.ganador_cohorte,
                              **medir(te.objetivo_fcl_t1, p, ref_media, ref_pers)))
            predicciones.append(te[['id_fila', 'anio_objetivo']].assign(**id_, procedimiento=r.procedimiento, y_real=te.objetivo_fcl_t1.to_numpy(), y_predicho=p))
    pred = pd.concat(predicciones, ignore_index=True)
    for id_, g in pred.groupby([*ID_ESTUDIO, 'procedimiento', 'anio_objetivo']):
        e = g.y_predicho - g.y_real
        anuales.append(dict(zip([*ID_ESTUDIO, 'procedimiento', 'anio_objetivo'], id_), n=len(g), RMSE=float(np.sqrt(np.mean(e ** 2))), MAE=float(np.mean(np.abs(e)))))
    anual = pd.DataFrame(anuales)
    met = pd.DataFrame(filas).merge(anual.groupby([*ID_ESTUDIO, 'procedimiento'], as_index=False).RMSE.mean().rename(columns={'RMSE': 'RMSE_anual_medio'}), on=[*ID_ESTUDIO, 'procedimiento'])
    pred.to_csv(out / 'predicciones_prueba.csv', index=False, float_format='%.15g')
    anual.to_csv(out / 'metricas_prueba_por_anio.csv', index=False, float_format='%.15g')
    met.to_csv(out / 'metricas_prueba.csv', index=False, float_format='%.15g')
    (out / 'evaluacion_prueba.json').write_text(json.dumps({'sha256_seleccion': registro['sha256'], 'evaluada_utc': datetime.now(timezone.utc).isoformat()}, indent=2) + '\n', encoding='utf-8')
    return met, anual, pred


def graficos(trials, curvas, met, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tinta, azul, naranja, aqua, gris = '#52514e', '#2a78d6', '#eb6834', '#1baf7a', '#a3a29c'
    plt.rcParams.update({'figure.dpi': 130, 'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 9, 'axes.edgecolor': gris, 'axes.labelcolor': tinta,
                         'xtick.color': tinta, 'ytick.color': tinta, 'text.color': tinta, 'axes.grid': True, 'axes.axisbelow': True, 'grid.color': '#e6e5e0', 'grid.linewidth': .6})
    colores = {'random_search': azul, 'tpe': naranja}
    etiquetas = {'random_search': 'Random Search', 'tpe': 'Optuna TPE'}
    rotulo = lambda mo, gr: f"{'Dólares' if mo == 'D lares' else 'Soles'} / {gr}"
    rutas = {}
    fig, axs = plt.subplots(len(COHORTES), len(CARACTERISTICAS), figsize=(12.5, 9), sharex=True)
    for i, (mo, gr) in enumerate(COHORTES):
        for j, ca in enumerate(CARACTERISTICAS):
            ax = axs[i, j]
            g = curvas.loc[curvas.moneda.eq(mo) & curvas.grupo.eq(gr) & curvas.caracteristicas.eq(ca)]
            for me in METODOS:
                s = g.loc[g.metodo.eq(me)]
                ax.fill_between(s.n_trials, s.q1, s.q3, color=colores[me], alpha=.18, lw=0)
                ax.plot(s.n_trials, s.mediana, color=colores[me], lw=2, label=etiquetas[me])
            ax.set_yscale('symlog', linthresh=.01)
            if i == 0:
                ax.set_title(ca)
            if j == 0:
                ax.set_ylabel(f'{rotulo(mo, gr)}\nbrecha RMSE CV (%)', fontsize=8)
            if i == len(COHORTES) - 1:
                ax.set_xlabel('Trials')
    axs[0, 0].legend(frameon=False, fontsize=8)
    fig.suptitle('Convergencia: mediana y rango intercuartílico en 20 semillas', x=.01, ha='left')
    fig.tight_layout()
    rutas['convergencia'] = out / 'graficos/convergencia.png'
    fig.savefig(rutas['convergencia'])
    plt.close(fig)

    fig, axs = plt.subplots(1, len(COHORTES), figsize=(12.5, 3.2))
    for ax, (mo, gr) in zip(axs, COHORTES):
        g = trials.loc[trials.moneda.eq(mo) & trials.grupo.eq(gr) & trials.caracteristicas.eq('seleccion_08') & trials.semilla.eq(SEMILLA_PRINCIPAL)]
        for me in METODOS:
            s = g.loc[g.metodo.eq(me)]
            ax.scatter(s.alpha, s.rmse_cv / 1e3, s=12, color=colores[me], alpha=.7, label=etiquetas[me], linewidths=0)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set(title=rotulo(mo, gr), xlabel='alpha', ylabel='RMSE CV (miles)')
    axs[0].legend(frameon=False, fontsize=8, markerscale=2)
    fig.tight_layout()
    rutas['respuesta_alpha'] = out / 'graficos/respuesta_alpha.png'
    fig.savefig(rutas['respuesta_alpha'])
    plt.close(fig)

    orden = ['ridge_alpha1', 'rejilla_08', 'random_search', 'tpe']
    nombres = {'ridge_alpha1': 'Ridge α=1', 'rejilla_08': 'Rejilla 08', 'random_search': 'Random Search', 'tpe': 'Optuna TPE'}
    tonos = dict(zip(orden, [gris, aqua, azul, naranja]))
    fig, axs = plt.subplots(1, len(COHORTES), figsize=(12.5, 3.4))
    for ax, (mo, gr) in zip(axs, COHORTES):
        g = met.loc[met.moneda.eq(mo) & met.grupo.eq(gr) & met.caracteristicas.eq('seleccion_08')].set_index('procedimiento')
        for x, p in enumerate(orden):
            ax.bar(x, g.loc[p, 'RMSE'] / 1e3, color=tonos[p], width=.7)
        refs = met.loc[met.moneda.eq(mo) & met.grupo.eq(gr) & met.caracteristicas.eq('ninguna')].set_index('procedimiento')
        ax.axhline(refs.loc['persistencia', 'RMSE'] / 1e3, color=tinta, lw=1, ls='--', label='Persistencia')
        ax.axhline(refs.loc['media_entrenamiento', 'RMSE'] / 1e3, color=tinta, lw=1, ls=':', label='Media de entrenamiento')
        ax.set_xticks(range(4), [nombres[p] for p in orden], rotation=30, ha='right')
        ax.set(title=rotulo(mo, gr), ylabel='RMSE de prueba (miles)')
        ax.grid(axis='x', visible=False)
    axs[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    rutas['prueba'] = out / 'graficos/prueba_por_cohorte.png'
    fig.savefig(rutas['prueba'])
    plt.close(fig)
    return rutas


def estado_archivos_previos():
    rutas = ['data', 'reports/sprint_06', 'notebooks/07_baseline_variantes.ipynb', 'notebooks/08_mejoras_baseline.ipynb']
    salida = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain', '--', *rutas], capture_output=True, text=True, check=True).stdout
    return {'rutas': rutas, 'cambios_git': salida.splitlines(), 'sha256_panel': hashlib.sha256(PANEL.read_bytes()).hexdigest()}


def entorno():
    return {'python': platform.python_version(), 'optuna': optuna.__version__, 'scikit-learn': sklearn.__version__, 'numpy': np.__version__, 'pandas': pd.__version__, 'scipy': scipy.__version__,
            'git_head': subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()}


def analizar(out=None):
    """Tablas de la búsqueda; solo leen entrenamiento (trials y referencia densa)."""
    out = Path(out or OUT)
    trials = pd.read_csv(out / 'trials.csv')
    densa = pd.read_csv(out / 'referencia_densa.csv')
    curvas, comparacion, agregado = analizar_convergencia(trials, densa)
    diag = diagnostico_pruning(trials)
    curvas.to_csv(out / 'curvas_convergencia.csv', index=False, float_format='%.15g')
    comparacion.to_csv(out / 'comparacion_metodos.csv', index=False, float_format='%.15g')
    agregado.to_csv(out / 'comparacion_metodos_agregada.csv', index=False, float_format='%.15g')
    diag.to_csv(out / 'diagnostico_pruning.csv', index=False, float_format='%.15g')
    importancia_descriptiva(trials).to_csv(out / 'efecto_categoricos.csv', index=False, float_format='%.15g')
    (out / 'entorno.json').write_text(json.dumps(entorno(), indent=2) + '\n', encoding='utf-8')
    return trials, curvas, comparacion, agregado, diag
