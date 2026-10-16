"""Características retrospectivas; ninguna transformación aprende del conjunto de prueba."""
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

REDUNDANT_PREDICTORS = {'fcl_activo', 'FCO_mean3_previa', 'FCL_preliminar_mean3_previa'}

def make_preprocessor():
    """Clonar/crear y ajustar de nuevo en cada moneda y pliegue temporal futuro."""
    return Pipeline([('imputer', SimpleImputer(strategy='median', keep_empty_features=True)),
                     ('scaler', RobustScaler(quantile_range=(25., 75.)))])

RATIOS = {
    'pasivo_activo': ('PasivoTotal', 'ActivoTotal', 1),
    'margen_neto': ('UtilidadNeta', 'TotalIngreso', 1),
    'rentabilidad_activo_cierre': ('UtilidadNeta', 'ActivoTotal', 1),
    'rotacion_activo_cierre': ('TotalIngreso', 'ActivoTotal', 1),
    'fco_activo': ('FCO', 'ActivoTotal', 1),
    'fco_ingresos': ('FCO', 'TotalIngreso', 1),
    'inversion_capex_activo': ('CAPEX_reportado', 'ActivoTotal', -1),
    'fcl_activo': ('FCL_preliminar', 'ActivoTotal', 1),
}
RATIO_REASONS = {
    'pasivo_activo': 'Proporción de activos financiados con pasivos; no equivale a deuda financiera',
    'margen_neto': 'Resultado neto por unidad de ingreso total; no equivale a margen operativo',
    'rentabilidad_activo_cierre': 'Rentabilidad contable respecto al activo al cierre, no activo promedio',
    'rotacion_activo_cierre': 'Ingreso total generado por unidad de activo al cierre',
    'fco_activo': 'Generación operativa de efectivo relativa al tamaño',
    'fco_ingresos': 'Conversión de ingresos en flujo operativo',
    'inversion_capex_activo': 'Esfuerzo inversor reportado relativo al activo; excluye CAPEX positivo',
    'fcl_activo': 'Flujo libre preliminar relativo al tamaño; no FCFF validado',
}

def divide(a, b):
    """Solo denominadores estrictamente positivos; preserva ceros del numerador."""
    return (a / b.where(b > 0)).replace([np.inf, -np.inf], np.nan)

def build_features(raw):
    d = raw.copy().sort_values(['RPJ', 'Ejercicio']).reset_index(drop=True)
    if d[['RPJ', 'Ejercicio', 'Moneda']].isna().any().any():
        raise ValueError('Claves o moneda ausentes')
    if d.duplicated(['RPJ', 'Ejercicio']).any():
        raise ValueError('Duplicados empresa-año')
    if not pd.api.types.is_integer_dtype(d.Ejercicio):
        raise ValueError('Ejercicio debe ser entero')
    original = list(d.columns)
    # Conservar la fuente exportada; usar una versión validada en TODAS las derivaciones.
    original_fcl = d.FCL_preliminar.copy()
    d['FCL_preliminar'] = d.FCL_preliminar.where(~d.CAPEX_reportado.gt(0))
    dictionary = []
    predictors = []
    def add(name, values, formula, unit, why):
        d[name] = values
        predictors.append(name)
        dictionary.append(dict(nombre=name, formula=formula, unidad=unit,
                               disponibilidad='Al publicar estados de t; fuentes <= t',
                               justificacion=why, rol='predictor'))
    # Un cambio de moneda o hueco rompe el segmento, incluso si luego vuelve la moneda.
    g = d.groupby('RPJ', sort=False)
    previous = g[['Ejercicio', 'Moneda']].shift()
    broken = (d.Ejercicio.ne(previous.Ejercicio + 1) | d.Moneda.ne(previous.Moneda))
    d['segmento_temporal'] = broken.cumsum()
    groups = d.groupby(['RPJ', 'segmento_temporal'], sort=False)
    d['historial_previo_contiguo'] = groups.cumcount()
    for name, (num, den, sign) in RATIOS.items():
        values = d[num] * sign
        if num == 'CAPEX_reportado':
            values = values.where(d[num] <= 0)
        if num == 'TotalIngreso':
            values = values.where(d[num] > 0)
        formula = f'{sign} × {num}(t) / {den}(t), denominador > 0'
        if num == 'CAPEX_reportado':
            formula += '; solo CAPEX_reportado <= 0'
        if num == 'TotalIngreso':
            formula += '; ingreso actual > 0'
        add(name, divide(values, d[den]), formula, 'adimensional', RATIO_REASONS[name])
    for col in ['ActivoTotal', 'TotalIngreso']:
        prev = groups[col].shift(1)
        current = d[col].where(d[col] > 0) if col == 'TotalIngreso' else d[col]
        add(f'crecimiento_{col}', divide(current - prev, prev),
            f'({col}(t) - {col}(t-1)) / {col}(t-1), base > 0' + ('; ingreso actual > 0' if col == 'TotalIngreso' else ''),
            'adimensional', 'Expansión anual con continuidad y moneda constante')
    for col in ['FCO', 'FCL_preliminar']:
        add(f'cambio_{col}_activo_previo', divide(d[col] - groups[col].shift(1), groups.ActivoTotal.shift(1)),
            f'({col}(t)-{col}(t-1))/ActivoTotal(t-1)', 'adimensional',
            'Cambio de efectivo relativo al tamaño anterior; admite flujos negativos')
        for lag in [1, 2, 3]:
            add(f'{col}_lag{lag}', groups[col].shift(lag), f'{col}(t-{lag})',
                'unidad monetaria reportada, escala no acreditada', 'Persistencia histórica por empresa y segmento')
        for stat in ['mean', 'std']:
            values = groups[col].transform(lambda s: getattr(s.shift(1).rolling(3, min_periods=3), stat)())
            add(f'{col}_{stat}3_previa', values,
                f'{stat} de {col}(t-3), {col}(t-2), {col}(t-1)' + ('; ddof=1' if stat == 'std' else ''),
                'unidad monetaria reportada, escala no acreditada', 'Nivel o volatilidad de tres años estrictamente anteriores')
    # Objetivo por unión exacta al año siguiente, nunca por siguiente fila.
    future = d[['RPJ', 'Ejercicio', 'Moneda', 'FCL_preliminar']].copy()
    future['Ejercicio'] -= 1
    future = future.rename(columns={'Moneda': 'moneda_objetivo', 'FCL_preliminar': 'objetivo_fcl_t1'})
    d = d.merge(future, on=['RPJ', 'Ejercicio'], how='left', validate='one_to_one')
    d['anio_objetivo'] = d.Ejercicio + 1
    d['objetivo_moneda_consistente'] = d.Moneda.eq(d.moneda_objetivo).fillna(False)
    d['utilizable_supervisado'] = d.objetivo_fcl_t1.notna() & d.objetivo_moneda_consistente
    d['particion'] = np.select([
        d.utilizable_supervisado & (d.anio_objetivo <= 2021),
        d.utilizable_supervisado & d.anio_objetivo.between(2022, 2025)],
        ['entrenamiento', 'prueba'], default='sin_etiqueta_elegible')
    d['n_features_disponibles'] = d[predictors].notna().sum(axis=1)
    d['ingresos_no_positivos'] = d.TotalIngreso.le(0)
    d['capex_signo_revisar'] = d.CAPEX_reportado.gt(0)
    d['patrimonio_no_positivo'] = d.PatrimonioTotal.le(0)
    d['FCL_preliminar'] = original_fcl.to_numpy()
    controls = {
        'segmento_temporal': ('Identificador acumulado al cambiar empresa, moneda o faltar año consecutivo', 'identificador', 'Hasta t'),
        'historial_previo_contiguo': ('Número de filas previas del segmento anual continuo', 'años', 'Hasta t'),
        'moneda_objetivo': ('Moneda reportada para la misma empresa en año t+1 exacto', 'categoría', 'Futuro; NO predictor'),
        'objetivo_fcl_t1': ('FCL_preliminar de la misma empresa en año t+1 exacto; sin imputación', 'moneda reportada; escala no acreditada', 'Futuro; solo etiqueta'),
        'anio_objetivo': ('Ejercicio + 1', 'año', 'Conocido en t'),
        'objetivo_moneda_consistente': ('Moneda(t) == moneda_objetivo; falso si no existe', 'booleano', 'Ex post; NO predictor'),
        'utilizable_supervisado': ('objetivo_fcl_t1 no faltante Y objetivo_moneda_consistente', 'booleano', 'Ex post; NO predictor'),
        'particion': ('Elegible y año objetivo <=2021: entrenamiento; 2022–2025: prueba; resto sin etiqueta elegible', 'categoría', 'Diseño ex post; NO predictor'),
        'n_features_disponibles': ('Conteo de predictores no faltantes en la fila', 'conteo', 'Hasta t'),
        'ingresos_no_positivos': ('TotalIngreso <= 0', 'booleano', 'Hasta t'),
        'capex_signo_revisar': ('CAPEX_reportado > 0; falso si falta', 'booleano', 'Hasta t'),
        'patrimonio_no_positivo': ('PatrimonioTotal <= 0', 'booleano', 'Hasta t'),
    }
    monetary = {'ActivoTotal', 'PasivoTotal', 'PatrimonioTotal', 'TotalIngreso',
                'UtilidadNeta', 'FCO', 'CAPEX_reportado', 'FCL_preliminar'}
    # Diccionario de todas las columnas exportadas; originales no se usan automáticamente como X.
    for c in d.columns:
        if c in predictors:
            continue
        role = 'fuente/contexto' if c in original else 'control'
        if c == 'objetivo_fcl_t1':
            role = 'objetivo; EXCLUIR de X'
        formula, unit, availability = controls.get(c, ('Dato original sin modificación',
            'moneda reportada; escala no acreditada' if c in monetary else
            'año' if c == 'Ejercicio' else 'booleano' if c == 'revision_interanual' else 'categoría / identificador',
            'Al publicar estados de t; sin fecha/vintage verificado'))
        if c == 'FCL_preliminar':
            formula = 'FCO + CAPEX_reportado; aproximación original no FCFF validado'
        dictionary.append(dict(nombre=c, formula=formula,
                               unidad=unit, disponibilidad=availability,
                               justificacion='Trazabilidad; excluir de la matriz predictiva salvo decisión explícita', rol=role))
    assert not np.isinf(d[predictors].to_numpy(dtype=float)).any()
    for item in dictionary:
        if item['nombre'].startswith('FCL_preliminar_') or item['nombre'] in {'fcl_activo', 'cambio_FCL_preliminar_activo_previo', 'objetivo_fcl_t1'}:
            item['formula'] += '; FCL fuente invalidado si CAPEX de su año > 0'
        if item['nombre'] in REDUNDANT_PREDICTORS:
            item['justificacion'] += '; redundante exacta: excluir del subconjunto lineal de 19'
    return d, predictors, pd.DataFrame(dictionary)
