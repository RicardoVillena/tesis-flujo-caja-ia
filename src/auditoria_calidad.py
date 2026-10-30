"""Sprint 08 — Etapa 1: auditoría descriptiva de los 26 atributos de E2, sin ajustar modelos.

Toda estadística utilizable para seleccionar atributos usa solo filas de entrenamiento
(objetivos 2006–2021), separadas por moneda. La historia auxiliar (denominadores de t−1,
medianas por empresa, saltos de magnitud) se limita a ejercicios <= último ejercicio de
entrenamiento: ninguna fila de prueba la alimenta. Nada aquí modifica datos ni reportes previos.
"""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import numpy as np
import pandas as pd
from src.feature_engineering import build_features, RATIOS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/sprint_08'
NB07 = ROOT / 'notebooks/07_baseline_variantes.ipynb'
CATALOGO = 'reports/diccionario_integracion_bursatil.csv'
REFERENCIA_INTEGRIDAD = OUT / 'referencia_integridad_previa.csv'
PROPIOS = {'src/auditoria_calidad.py', 'scripts/reproduce_auditoria_calidad.py', 'tests/test_auditoria_calidad.py',
            'src/ablacion_variables.py', 'scripts/reproduce_ablacion_variables.py', 'tests/test_ablacion_variables.py',
            'src/comparacion_modelos.py', 'scripts/reproduce_comparacion_modelos.py', 'tests/test_comparacion_modelos.py'}
PROPIOS_DIRS = ('reports/sprint_08/', 'notebooks/sprint_08/')
IGNORADOS = {'.git', '.cache', '__pycache__', '.ipynb_checkpoints'}
PANEL_INICIO = 2005

# Umbrales exploratorios: señalan casos para revisión, no reglas financieras ni de selección.
UMBRAL_CORRELACION = 0.8
CAMBIO_LOO_RELEVANTE = 0.2
FRACCIONES_DENOMINADOR = (0.001, 0.01, 0.05)
FRACCION_DENOMINADOR = 0.01
MIN_OBS_EMPRESA = 3
FACTOR_SALTO = 100
INDICE_CONDICION = 30
PROPORCION_VARIANZA = 0.5
VIF_REFERENCIA = 10
CATEGORIAS_TEMPORALES = ('DISPONIBILIDAD VERIFICADA', 'DISPONIBILIDAD NO VERIFICADA', 'POSIBLE FUGA TEMPORAL')


def _linea(rel, patron):
    """Primera línea (1-indexada) que contiene el patrón: evidencia localizable."""
    for i, texto in enumerate((ROOT / rel).read_text(encoding='utf-8').splitlines(), 1):
        if patron in texto:
            return f'{rel}:{i}'
    raise AssertionError(f'{patron!r} no aparece en {rel}')


def _fila_csv(rel, clave):
    for i, texto in enumerate((ROOT / rel).read_text(encoding='utf-8-sig').splitlines(), 1):
        if texto.startswith(f'{clave},'):
            return f'{rel}:{i}'
    raise AssertionError(f'{clave} no aparece en {rel}')


def especificacion_e2():
    """Recupera E2 del código literal del notebook 07 y del manifiesto; nunca ejecuta el notebook."""
    literales, celdas, modelo = {}, {}, None
    nb = json.loads(NB07.read_text(encoding='utf-8'))
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue
        fuente = ''.join(cell['source'])
        for node in ast.walk(ast.parse(fuente)):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {'MACRO', 'BOLSA', 'redundantes', 'ALPHA'}:
                        literales[target.id] = ast.literal_eval(node.value)
                        celdas[target.id] = i
            if isinstance(node, ast.FunctionDef) and node.name == 'crear_modelo':
                modelo, celdas['crear_modelo'] = ast.get_source_segment(fuente, node), i
        for clave, patron in [('objetivo', 'fuente_futura['), ('rezago_externo', 'rezagada[v]=esperado'),
                              ('ejecucion', 'ejecutar("sensibilidad_robust"')]:
            if patron in fuente:
                celdas[clave] = i
    compacto = re.sub(r'\s', '', modelo)
    for patron in ['SimpleImputer(strategy="median",keep_empty_features=True)', 'StandardScaler()',
                   'RobustScaler(quantile_range=(25,75))', 'ColumnTransformer(']:
        assert patron in compacto, patron
    catalogo = pd.read_csv(ROOT / CATALOGO, keep_default_na=False)
    fin22 = catalogo.loc[catalogo.origen.eq('SMV/Feature Engineering') & catalogo.predictor_candidato.eq(True), 'variable'].tolist()
    fin = [v for v in fin22 if v not in literales['redundantes']]
    validacion = json.loads((ROOT / 'reports/sprint_06/validacion_baseline.json').read_text())
    exp = validacion['experimentos']
    assert len(fin22) == 22 and exp['E0_financiero'] == fin
    assert exp['E1_macroeconomico'] == fin + literales['MACRO']
    cols = fin + literales['MACRO'] + literales['BOLSA']
    assert exp['E2_bursatil'] == cols and len(cols) == 26
    assert validacion['escenarios'] == ['principal', 'rezago_externo_t_1', 'sensibilidad_robust']
    nb07 = 'notebooks/07_baseline_variantes.ipynb'
    return {
        'financieros': fin, 'macroeconomicos': literales['MACRO'], 'bursatiles': literales['BOLSA'], 'E2': cols,
        'redundantes_excluidas_por_definicion': sorted(literales['redundantes']),
        'objetivo': {
            'nombre': 'objetivo_fcl_t1',
            'definicion': 'FCL_preliminar(t+1) = FCO(t+1) + CAPEX_reportado(t+1) de la misma RPJ, unido por Ejercicio+1 exacto '
                          '(nunca la fila siguiente); faltante si CAPEX_reportado(t+1) > 0. FCL preliminar, no FCFF validado.',
            'horizonte': 'un ejercicio anual adelante (anio_objetivo = Ejercicio + 1)',
            'elegibilidad': 'utilizable_supervisado = objetivo no faltante Y Moneda(t) == Moneda(t+1); sin imputación del objetivo',
            'particion': 'entrenamiento: anio_objetivo <= 2021 (Ejercicio 2005–2020); prueba: anio_objetivo 2022–2025 (Ejercicio 2021–2024)',
        },
        'preparacion_principal': 'Por moneda y ajustado solo en entrenamiento: ColumnTransformer -> SimpleImputer(strategy="median", '
                                 'keep_empty_features=True) -> StandardScaler() (ddof=0) -> Ridge(alpha=1.0, solver="svd")',
        'sensibilidades': ['rezago_externo_t_1: los 7 externos se reemplazan por su valor del año Ejercicio−1 (2005 queda faltante e imputado)',
                           'sensibilidad_robust: RobustScaler(quantile_range=(25,75)) en lugar de StandardScaler'],
        'alpha': literales['ALPHA'],
        'evidencia': {
            'listas_E0_E1_E2': f'{nb07} celda {celdas["MACRO"]}; reports/sprint_06/validacion_baseline.json (experimentos)',
            'objetivo_y_elegibilidad': f'{nb07} celda {celdas["objetivo"]}; {_linea("src/feature_engineering.py", "Objetivo por unión exacta")}',
            'preparacion': f'{nb07} celda {celdas["crear_modelo"]} (crear_modelo)',
            'sensibilidad_rezago_externo': f'{nb07} celda {celdas["rezago_externo"]}',
            'sensibilidad_robust': f'{nb07} celda {celdas["ejecucion"]}',
        },
    }


def load_inputs():
    """Panel original verificado; reconstruye exactamente los atributos financieros desde la fuente."""
    spec = especificacion_e2()
    cols = spec['E2']
    d = pd.read_csv(ROOT / 'data/processed/panel_financiero_macro_bursatil.csv', float_precision='round_trip',
                    dtype={'RPJ': 'string', 'RUC': 'string'})
    assert len(d) == 4221 and d.utilizable_supervisado.sum() == 3560
    assert d.loc[d.utilizable_supervisado, 'particion'].value_counts().to_dict() == {'entrenamiento': 2869, 'prueba': 691}
    assert d.anio_objetivo.eq(d.Ejercicio + 1).all() and not d.duplicated(['RPJ', 'Ejercicio']).any()
    raw = pd.read_csv(ROOT / 'data/processed/panel_fcl_preliminar.csv', float_precision='round_trip', dtype={'RPJ': 'string', 'RUC': 'string'})
    rebuilt, _, _ = build_features(raw)
    pd.testing.assert_frame_equal(rebuilt, d[rebuilt.columns], check_dtype=False, check_exact=True)
    # Externos: valor anual idéntico por Ejercicio (año t), nunca por anio_objetivo.
    anual = pd.read_csv(ROOT / 'data/processed/macroeconomia_peru_2005_2025.csv', float_precision='round_trip').set_index('anio').join(
        pd.read_csv(ROOT / 'data/processed/bursatil_mercado_anual.csv', float_precision='round_trip').set_index('anio'), how='outer')
    for v in spec['macroeconomicos'] + spec['bursatiles']:
        np.testing.assert_array_equal(d[v].to_numpy(), d.Ejercicio.map(anual[v]).to_numpy())
    catalogo = pd.read_csv(ROOT / CATALOGO, keep_default_na=False)
    return d, cols, catalogo.set_index('variable').loc[cols].reset_index()


def training(d):
    return d.loc[d.utilizable_supervisado & d.particion.eq('entrenamiento')].copy()


def historia(d, anio_max=None):
    """Filas fuente hasta el último ejercicio de entrenamiento (incluye no elegibles históricas)."""
    anio_max = training(d).Ejercicio.max() if anio_max is None else anio_max
    return d.loc[d.Ejercicio.le(anio_max)].sort_values(['RPJ', 'Ejercicio'])


def grupo_atributo(v, spec):
    return 'financiero' if v in spec['financieros'] else 'macroeconomico' if v in spec['macroeconomicos'] else 'bursatil'


def tipo_atributo(v):
    """Estructura temporal y denominador de cada atributo según src/feature_engineering.py."""
    if v in RATIOS:
        num, den, _ = RATIOS[v]
        return dict(tipo='ratio', num=num, den=den, desfase_den=0, k=0)
    if v.startswith('crecimiento_') and v.endswith(('ActivoTotal', 'TotalIngreso')):
        col = v.removeprefix('crecimiento_')
        return dict(tipo='crecimiento', col=col, den=col, desfase_den=1, k=1)
    m = re.fullmatch(r'cambio_(FCO|FCL_preliminar)_activo_previo', v)
    if m:
        return dict(tipo='cambio', col=m.group(1), den='ActivoTotal', desfase_den=1, k=1)
    m = re.fullmatch(r'(FCO|FCL_preliminar)_lag(\d)', v)
    if m:
        return dict(tipo='rezago', col=m.group(1), k=int(m.group(2)))
    m = re.fullmatch(r'(FCO|FCL_preliminar)_std3_previa', v)
    if m:
        return dict(tipo='volatilidad', col=m.group(1), k=3)
    return dict(tipo='externo', k=0)


def causas_faltantes(d, cols, anio_max=None):
    """Clasifica cada faltante de entrenamiento: estructural (rezago), regla de cálculo o fuente ausente."""
    tr, h = training(d), historia(d, anio_max)
    seg = h.segmento_temporal

    def previo(s, k=1):
        return s.groupby(seg, sort=False).shift(k).loc[tr.index]

    capex_pos = h.CAPEX_reportado.gt(0)
    hist = tr.historial_previo_contiguo
    primer_anio = h.groupby('RPJ').Ejercicio.transform('min').loc[tr.index]
    inicio_segmento = tr.Ejercicio - hist
    filas = []
    for v in cols:
        info, falta = tipo_atributo(v), tr[v].isna()
        if not falta.any():
            continue
        causa = pd.Series(None, index=tr.index, dtype='object')

        def asignar(mascara, texto):
            causa[falta & causa.isna() & mascara.fillna(False).astype(bool)] = texto

        k = info['k']
        if k:
            corto = hist.lt(k)
            asignar(corto & inicio_segmento.gt(primer_anio), 'estructural: ruptura de segmento (hueco anual o cambio de moneda)')
            asignar(corto & primer_anio.eq(PANEL_INICIO), 'estructural: historia anterior a 2005 fuera del panel')
            asignar(corto, 'estructural: entrada de la empresa al panel después de 2005')
        if info['tipo'] == 'ratio':
            num, den = info['num'], info['den']
            asignar(tr[num].isna() | tr[den].isna(), 'fuente: numerador o denominador ausente en t')
            asignar(tr[den].le(0), 'regla: denominador no positivo en t')
            if num == 'TotalIngreso':
                asignar(tr[num].le(0), 'regla: ingreso no positivo en t')
            if num == 'CAPEX_reportado':
                asignar(tr[num].gt(0), 'regla: CAPEX positivo excluido')
        elif info['tipo'] == 'crecimiento':
            col = info['col']
            asignar(tr[col].isna() | previo(h[col]).isna(), 'fuente: valor ausente en t o t-1')
            asignar(previo(h[col]).le(0), 'regla: base t-1 no positiva')
            if col == 'TotalIngreso':
                asignar(tr[col].le(0), 'regla: ingreso actual no positivo')
        elif info['tipo'] == 'cambio':
            col = info['col']
            asignar(previo(h.ActivoTotal).isna(), 'fuente: ActivoTotal ausente en t-1')
            asignar(previo(h.ActivoTotal).le(0), 'regla: ActivoTotal t-1 no positivo')
            asignar(tr[col].isna() | previo(h[col]).isna(), 'fuente: flujo ausente en t o t-1')
            if col == 'FCL_preliminar':
                asignar(tr.CAPEX_reportado.gt(0) | previo(capex_pos).fillna(False).astype(bool), 'regla: CAPEX positivo invalida FCL en t o t-1')
        elif info['tipo'] == 'rezago':
            col = info['col']
            asignar(previo(h[col], k).isna(), f'fuente: flujo ausente en t-{k}')
            if col == 'FCL_preliminar':
                asignar(previo(capex_pos, k).fillna(False).astype(bool), f'regla: CAPEX positivo invalida FCL en t-{k}')
        elif info['tipo'] == 'volatilidad':
            col = info['col']
            ausente = sum(previo(h[col], j).isna().astype(int) for j in (1, 2, 3)).gt(0)
            asignar(ausente, 'fuente: flujo ausente en la ventana t-3..t-1')
            if col == 'FCL_preliminar':
                invalida = sum(previo(capex_pos, j).fillna(False).astype(int) for j in (1, 2, 3)).gt(0)
                asignar(invalida, 'regla: CAPEX positivo invalida FCL en la ventana')
        else:
            asignar(falta, 'fuente: serie externa sin dato para el año')
        causa[falta & causa.isna()] = 'no explicado'
        m = falta[falta].index
        filas.append(pd.DataFrame({'moneda': tr.loc[m, 'Moneda'], 'RPJ': tr.loc[m, 'RPJ'], 'Ejercicio': tr.loc[m, 'Ejercicio'],
                                   'variable': v, 'causa': causa.loc[m]}))
    out = pd.concat(filas) if filas else pd.DataFrame(columns=['moneda', 'RPJ', 'Ejercicio', 'variable', 'causa'])
    out['grupo_causa'] = out.causa.str.split(':').str[0]
    return out


def calidad(tr, cols, causas):
    filas, cobertura = [], []
    grupos = causas.groupby(['moneda', 'variable', 'grupo_causa']).size()
    anual = causas.groupby(['moneda', 'variable', 'Ejercicio', 'grupo_causa']).size()
    for moneda, t in tr.groupby('Moneda', sort=True):
        for v in cols:
            bruto = t[v]
            s = bruto.replace([np.inf, -np.inf], np.nan)
            z = s.dropna()
            q = s.quantile([.01, .05, .25, .5, .75, .95, .99])
            iqr = q.loc[.75] - q.loc[.25]
            lo, hi = q.loc[.25] - 1.5 * iqr, q.loc[.75] + 1.5 * iqr
            g = {c: int(grupos.get((moneda, v, c), 0)) for c in ['estructural', 'regla', 'fuente', 'no explicado']}
            por_anio = t.loc[s.notna()].groupby('Ejercicio')[v].nunique()
            externo = tipo_atributo(v)['tipo'] == 'externo'
            filas.append(dict(
                moneda=moneda, variable=v, tipo=str(bruto.dtype), n=len(s), n_empresas=t.RPJ.nunique(),
                faltantes_n=int(s.isna().sum()), faltantes_pct=100 * s.isna().mean(),
                faltantes_estructurales=g['estructural'], faltantes_regla=g['regla'], faltantes_fuente=g['fuente'],
                faltantes_no_explicados=g['no explicado'],
                minimo=s.min(), maximo=s.max(), media=s.mean(), mediana=s.median(), desviacion_estandar=s.std(ddof=1),
                asimetria=s.skew(), **{f'p{int(round(k * 100)):02d}': a for k, a in q.items()},
                limite_RIQ_inferior=lo, limite_RIQ_superior=hi, extremos_RIQ=int((s.lt(lo) | s.gt(hi)).sum()),
                extremos_RIQ_pct=100 * (s.lt(lo) | s.gt(hi)).sum() / max(len(z), 1),
                n_unicos=z.nunique(), es_constante=z.nunique() == 1, constante_dentro_de_anio=bool(por_anio.le(1).all()),
                ceros=int(s.eq(0).sum()), repeticiones=int(len(z) - z.nunique()),
                infinitos=int(np.isinf(bruto.to_numpy(dtype=float)).sum()), indefinidos_por_regla=g['regla'],
                nan_total=int(bruto.isna().sum()),
                primer_anio=int(t.loc[s.notna(), 'Ejercicio'].min()) if len(z) else None,
                ultimo_anio=int(t.loc[s.notna(), 'Ejercicio'].max()) if len(z) else None,
                anios_observados=int(t.loc[s.notna(), 'Ejercicio'].nunique()),
                unidad_estadistica='año calendario repetido entre empresas' if externo else 'empresa-ejercicio'))
            for anio, ga in t.groupby('Ejercicio'):
                c = {k: int(anual.get((moneda, v, anio, k), 0)) for k in ['estructural', 'regla', 'fuente', 'no explicado']}
                cobertura.append(dict(moneda=moneda, variable=v, anio=int(anio), n=len(ga), observados=int(ga[v].notna().sum()),
                                      faltantes=int(ga[v].isna().sum()), faltantes_pct=100 * ga[v].isna().mean(),
                                      faltantes_estructurales=c['estructural'], faltantes_regla=c['regla'],
                                      faltantes_fuente=c['fuente'], faltantes_no_explicados=c['no explicado'],
                                      valores_distintos=int(ga[v].nunique())))
    resumen = causas.groupby(['moneda', 'variable', 'grupo_causa', 'causa']).size().rename('n').reset_index()
    return pd.DataFrame(filas), pd.DataFrame(cobertura), resumen


def denominadores(d, cols, anio_max=None):
    """Denominadores positivos pequeños según dos criterios exploratorios explícitos, por moneda."""
    tr, h = training(d), historia(d, anio_max)
    q = {}
    resumen, casos = [], []
    for v in cols:
        info = tipo_atributo(v)
        if 'den' not in info:
            continue
        col = info['den']
        den = (h[col].groupby(h.segmento_temporal, sort=False).shift(1) if info['desfase_den'] else h[col]).loc[tr.index]
        positivo = h[col].where(h[col].gt(0))
        llaves = [h.RPJ, h.Moneda]
        mediana_empresa = positivo.groupby(llaves).transform('median').where(positivo.groupby(llaves).transform('count').ge(MIN_OBS_EMPRESA)).loc[tr.index]
        etiqueta = f'{col}(t-1)' if info['desfase_den'] else f'{col}(t)'
        for moneda, idx in tr.groupby('Moneda', sort=True).groups.items():
            dm, me, s = den.loc[idx], mediana_empresa.loc[idx], tr.loc[idx, v]
            mediana = dm[dm.gt(0)].median()
            if (moneda, v) not in q:
                a, b = s.quantile([.25, .75])
                q[(moneda, v)] = (a - 1.5 * (b - a), b + 1.5 * (b - a))
            lo, hi = q[(moneda, v)]
            for f in FRACCIONES_DENOMINADOR:
                transversal = dm.gt(0) & dm.le(f * mediana)
                intra = dm.gt(0) & dm.le(f * me)
                union = transversal | intra
                resumen.append(dict(moneda=moneda, variable=v, denominador=etiqueta, fraccion=f, principal=f == FRACCION_DENOMINADOR,
                                    n_filas=len(idx), denominador_ausente=int(dm.isna().sum()), denominador_no_positivo=int(dm.le(0).sum()),
                                    mediana_positiva_moneda=mediana, umbral_transversal=f * mediana,
                                    casos_transversal=int(transversal.sum()), casos_intraempresa=int(intra.sum()),
                                    casos_union=int(union.sum()), empresas_union=int(tr.loc[union[union].index, 'RPJ'].nunique()),
                                    casos_union_con_atributo_extremo_RIQ=int((union & (s.lt(lo) | s.gt(hi))).sum()),
                                    criterio=f'denominador > 0 y <= {f:g} x mediana positiva de la moneda (transversal) '
                                             f'o <= {f:g} x mediana positiva de la propia empresa con >= {MIN_OBS_EMPRESA} años <= último ejercicio train (intraempresa)'))
                if f != FRACCION_DENOMINADOR:
                    continue
                for i in union[union].index:
                    r = tr.loc[i]
                    casos.append(dict(moneda=moneda, variable=v, RPJ=r.RPJ, NombreEmpresa=r.NombreEmpresa, Ejercicio=int(r.Ejercicio),
                                      denominador=etiqueta, valor_denominador=dm.loc[i], mediana_positiva_moneda=mediana,
                                      mediana_positiva_empresa=me.loc[i], relativo_moneda=dm.loc[i] / mediana,
                                      relativo_empresa=dm.loc[i] / me.loc[i] if pd.notna(me.loc[i]) else np.nan,
                                      criterio_transversal=bool(transversal.loc[i]), criterio_intraempresa=bool(intra.loc[i]),
                                      valor_atributo=s.loc[i], atributo_extremo_RIQ=bool(s.loc[i] < lo or s.loc[i] > hi),
                                      revision_interanual=bool(r.revision_interanual)))
    columnas = ['moneda', 'variable', 'RPJ', 'NombreEmpresa', 'Ejercicio', 'denominador', 'valor_denominador', 'mediana_positiva_moneda',
                'mediana_positiva_empresa', 'relativo_moneda', 'relativo_empresa', 'criterio_transversal', 'criterio_intraempresa',
                'valor_atributo', 'atributo_extremo_RIQ', 'revision_interanual']
    return pd.DataFrame(resumen), pd.DataFrame(casos, columns=columnas)


def saltos_escala(d, cols, anio_max=None):
    """Cambios intraempresa >= FACTOR_SALTO veces en montos positivos; 'pico' si revierten al año siguiente."""
    tr, h = training(d), historia(d, anio_max)
    seg = h.segmento_temporal
    filas = []
    for col in ['ActivoTotal', 'PasivoTotal', 'TotalIngreso']:
        x = h[col].where(h[col].gt(0))
        previo, siguiente = x.groupby(seg, sort=False).shift(1), x.groupby(seg, sort=False).shift(-1)
        lf, lf_sig = np.log10(x / previo), np.log10(siguiente / x)
        umbral = np.log10(FACTOR_SALTO)
        salto = lf.abs().ge(umbral)
        pico = salto & lf_sig.abs().ge(umbral) & np.sign(lf_sig).eq(-np.sign(lf))
        for i in salto[salto].index:
            r = h.loc[i]
            # Filas train del mismo segmento cuyos atributos usan el valor de t (t..t+3).
            afectadas = tr.loc[tr.segmento_temporal.eq(r.segmento_temporal) & tr.Ejercicio.between(r.Ejercicio, r.Ejercicio + 3), 'Ejercicio']
            if afectadas.empty:
                continue
            filas.append(dict(moneda=r.Moneda, RPJ=r.RPJ, NombreEmpresa=r.NombreEmpresa, Ejercicio=int(r.Ejercicio), columna=col,
                              valor_t_1=previo.loc[i], valor_t=x.loc[i], valor_t_mas_1=siguiente.loc[i], factor=10 ** lf.loc[i],
                              patron_pico=bool(pico.loc[i]), fila_t_en_entrenamiento=bool(i in tr.index),
                              ejercicios_train_afectados=';'.join(map(str, sorted(afectadas))),
                              revision_interanual=bool(r.revision_interanual)))
    return pd.DataFrame(filas, columns=['moneda', 'RPJ', 'NombreEmpresa', 'Ejercicio', 'columna', 'valor_t_1', 'valor_t', 'valor_t_mas_1',
                                        'factor', 'patron_pico', 'fila_t_en_entrenamiento', 'ejercicios_train_afectados', 'revision_interanual'])


def pearson_loo(x, y):
    """Pearson al excluir cada observación (forma cerrada sobre datos estandarizados para estabilidad)."""
    x = (x - x.mean()) / x.std()
    y = (y - y.mean()) / y.std()
    n = len(x) - 1
    sx, sy = x.sum() - x, y.sum() - y
    sxx, syy, sxy = (x * x).sum() - x * x, (y * y).sum() - y * y, (x * y).sum() - x * y
    return (sxy - sx * sy / n) / np.sqrt((sxx - sx * sx / n) * (syy - sy * sy / n))


def correlaciones(tr, cols, spec):
    externos = spec['macroeconomicos'] + spec['bursatiles']
    matrices, tamanos, pares, anuales = {'pearson': [], 'spearman': []}, [], [], []
    for moneda, t in tr.groupby('Moneda', sort=True):
        x = t[cols].replace([np.inf, -np.inf], np.nan)
        c = {m: x.corr(method=m, min_periods=3) for m in matrices}
        for m in matrices:
            matrices[m].append(pd.concat({moneda: c[m]}, names=['moneda', 'variable']))
        mask = x.notna().astype(int)
        tamanos.append(pd.concat({moneda: mask.T @ mask}, names=['moneda', 'variable']))
        serie = t.groupby('Ejercicio')[externos].first()
        ca = {m: serie.corr(method=m) for m in matrices}
        for i, a in enumerate(externos):
            for b in externos[i + 1:]:
                anuales.append(dict(moneda=moneda, variable_1=a, variable_2=b, pearson_anual=ca['pearson'].loc[a, b],
                                    spearman_anual=ca['spearman'].loc[a, b], n_anios=len(serie),
                                    pearson_filas=c['pearson'].loc[a, b], spearman_filas=c['spearman'].loc[a, b]))
        for i, a in enumerate(cols):
            for b in cols[i + 1:]:
                p, s = c['pearson'].loc[a, b], c['spearman'].loc[a, b]
                if not max(abs(p), abs(s)) >= UMBRAL_CORRELACION:
                    continue
                completo = x[[a, b]].dropna()
                loo = pearson_loo(completo[a].to_numpy(float), completo[b].to_numpy(float))
                j = int(np.nanargmax(np.abs(loo - p)))
                fila = t.loc[completo.index[j]]
                tipo = 'externo-externo' if a in externos and b in externos else 'financiero-externo' if a in externos or b in externos else 'financiero-financiero'
                pares.append(dict(moneda=moneda, variable_1=a, variable_2=b, tipo_par=tipo, pearson=p, spearman=s,
                                  supera_pearson=abs(p) >= UMBRAL_CORRELACION, supera_spearman=abs(s) >= UMBRAL_CORRELACION,
                                  n_pares=len(completo), n_empresas=t.loc[completo.index, 'RPJ'].nunique(),
                                  n_anios=t.loc[completo.index, 'Ejercicio'].nunique(),
                                  pearson_loo_min=np.nanmin(loo), pearson_loo_max=np.nanmax(loo), cambio_max_loo=float(np.abs(loo[j] - p)),
                                  pearson_sin_caso_influyente=loo[j], caso_influyente=f'{fila.RPJ} {int(fila.Ejercicio)} ({fila.NombreEmpresa})',
                                  RPJ_influyente=fila.RPJ, Ejercicio_influyente=int(fila.Ejercicio),
                                  depende_de_un_caso=bool(np.abs(loo[j] - p) >= CAMBIO_LOO_RELEVANTE), umbral=UMBRAL_CORRELACION))
    columnas = ['moneda', 'variable_1', 'variable_2', 'tipo_par', 'pearson', 'spearman', 'supera_pearson', 'supera_spearman', 'n_pares',
                'n_empresas', 'n_anios', 'pearson_loo_min', 'pearson_loo_max', 'cambio_max_loo', 'pearson_sin_caso_influyente',
                'caso_influyente', 'RPJ_influyente', 'Ejercicio_influyente', 'depende_de_un_caso', 'umbral']
    return (pd.concat(matrices['pearson']), pd.concat(matrices['spearman']), pd.concat(tamanos),
            pd.DataFrame(pares, columns=columnas), pd.DataFrame(anuales))


def vif(z):
    """VIF_j = 1/(1-R²_j) por OLS auxiliar sobre columnas centradas (intercepto implícito)."""
    arr, out = z.to_numpy(float), {}
    for j, v in enumerate(z.columns):
        y, X = arr[:, j], np.delete(arr, j, axis=1)
        resid = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
        ratio = (resid @ resid) / (y @ y)
        out[v] = np.inf if ratio < 1e-12 else 1 / ratio
    return pd.Series(out)


def _estandarizar(x):
    sd = x.std(ddof=0)
    activos = sd.gt(0)
    return (x.loc[:, activos] - x.loc[:, activos].mean()) / sd[activos], activos


def colinealidad(tr, cols, spec, influyentes=None):
    """VIF y dependencias; `influyentes` (moneda, RPJ, Ejercicio) define una sensibilidad que los excluye, sin limpiar datos."""
    externos = spec['macroeconomicos'] + spec['bursatiles']
    influyentes = set() if influyentes is None else set(influyentes)
    vifs, deps = [], []

    def condicion(z, moneda, especificacion):
        arr = z.to_numpy(float) / np.sqrt(len(z))
        _, s, vh = np.linalg.svd(arr, full_matrices=False)
        tol = s.max() * max(arr.shape) * np.finfo(float).eps
        rango = int((s > tol).sum())
        for k in np.where(s <= tol)[0]:
            deps.append(dict(moneda=moneda, especificacion=especificacion, tipo='dependencia lineal exacta (tolerancia numérica)',
                             indice_condicion=np.inf, variables=';'.join(z.columns), detalle=json.dumps(dict(zip(z.columns, vh[k].round(6).tolist()))), tolerancia=tol))
        phi = (vh.T ** 2) / np.where(s > tol, s, np.nan) ** 2
        prop = phi / np.nansum(phi, axis=1, keepdims=True)
        for k in np.where((s > tol) & (s.max() / s >= INDICE_CONDICION))[0]:
            sel = [(v, prop[j, k]) for j, v in enumerate(z.columns) if prop[j, k] >= PROPORCION_VARIANZA]
            if len(sel) >= 2:
                deps.append(dict(moneda=moneda, especificacion=especificacion, tipo='casi dependencia (índice de condición, exploratorio)',
                                 indice_condicion=s.max() / s[k], variables=';'.join(v for v, _ in sel),
                                 detalle=json.dumps({v: round(p, 4) for v, p in sel}), tolerancia=INDICE_CONDICION))
        return rango, s.max() / s[s > tol].min()

    for moneda, t in tr.groupby('Moneda', sort=True):
        x = t[cols].replace([np.inf, -np.inf], np.nan)
        # Réplica de la preparación E2: mediana train (0 si la columna está vacía) + StandardScaler ddof=0.
        zi, activos = _estandarizar(x.fillna(x.median().fillna(0)))
        cc = x.dropna()
        zc, activos_c = _estandarizar(cc)
        especificaciones = [('imputada_mediana_E2', zi, activos, x.index), ('casos_completos', zc, activos_c, cc.index)]
        excluir = [i for i in t.index if (moneda, t.at[i, 'RPJ'], int(t.at[i, 'Ejercicio'])) in influyentes]
        if excluir:
            xs = x.drop(index=excluir)
            zs, activos_s = _estandarizar(xs.fillna(xs.median().fillna(0)))
            especificaciones.append(('imputada_sin_casos_influyentes', zs, activos_s, xs.index))
        for nombre, z, act, filas in especificaciones:
            n = len(filas)
            rango, ncond = condicion(z, moneda, nombre) if n > z.shape[1] else (None, np.nan)
            valores = vif(z) if n > z.shape[1] else pd.Series(dtype=float)
            for v in cols:
                vifs.append(dict(moneda=moneda, especificacion=nombre, variable=v, VIF=valores.get(v, np.nan), n=n,
                                 n_anios=t.loc[filas, 'Ejercicio'].nunique(),
                                 imputados_pct=0.0 if nombre == 'casos_completos' else 100 * x.loc[filas, v].isna().mean(),
                                 constante=not bool(act.get(v, False)), rango=rango, columnas=int(act.sum()), numero_condicion=ncond))
        serie = t.groupby('Ejercicio')[externos].first()
        za, act_a = _estandarizar(serie)
        rango, ncond = condicion(za, moneda, 'externos_anual')
        for v, val in vif(za).items():
            vifs.append(dict(moneda=moneda, especificacion='externos_anual', variable=v, VIF=val, n=len(serie), n_anios=len(serie),
                             imputados_pct=0.0, constante=False, rango=rango, columnas=int(act_a.sum()), numero_condicion=ncond))
        for i, a in enumerate(cols):
            for b in cols[i + 1:]:
                if x[a].equals(x[b]):
                    deps.append(dict(moneda=moneda, especificacion='sin imputar', tipo='columna duplicada exacta', indice_condicion=np.nan,
                                     variables=f'{a};{b}', detalle='mismos valores y misma máscara de faltantes', tolerancia=0))
                par = x[[a, b]].dropna()
                if len(par) >= 3 and par[a].nunique() > 1 and par[b].nunique() > 1 and abs(par[a].corr(par[b])) >= 1 - 1e-12:
                    deps.append(dict(moneda=moneda, especificacion='sin imputar', tipo='relación afín exacta en pares observados', indice_condicion=np.nan,
                                     variables=f'{a};{b}', detalle=f'n={len(par)}', tolerancia=1e-12))
        for nombre, sub in [('26 atributos', cols), ('19 financieros', spec['financieros'])]:
            dup = x[sub].duplicated(keep=False)
            if dup.any():
                deps.append(dict(moneda=moneda, especificacion='sin imputar', tipo=f'filas duplicadas en {nombre}', indice_condicion=np.nan,
                                 variables='', detalle=';'.join(f'{r.RPJ} {r.Ejercicio}' for r in t.loc[dup[dup].index].itertuples()), tolerancia=0))
    columnas = ['moneda', 'especificacion', 'tipo', 'indice_condicion', 'variables', 'detalle', 'tolerancia']
    return pd.DataFrame(vifs), pd.DataFrame(deps, columns=columnas)


def diagnostics(d, cols, anio_max_historia=None):
    """Diagnósticos de selección: dependen solo de entrenamiento y de historia <= último ejercicio train."""
    spec = especificacion_e2()
    tr = training(d)
    causas = causas_faltantes(d, cols, anio_max_historia)
    q, cobertura, resumen_causas = calidad(tr, cols, causas)
    den_resumen, den_casos = denominadores(d, cols, anio_max_historia)
    pearson, spearman, tamanos, pares, anuales = correlaciones(tr, cols, spec)
    influyentes = pares.loc[pares.depende_de_un_caso, ['moneda', 'RPJ_influyente', 'Ejercicio_influyente']].itertuples(index=False, name=None)
    vifs, deps = colinealidad(tr, cols, spec, influyentes)
    return {'calidad_atributos': q, 'cobertura_temporal_train': cobertura, 'faltantes_causas_train': resumen_causas,
            'denominadores_train': den_resumen, 'denominadores_casos_train': den_casos,
            'saltos_escala_train': saltos_escala(d, cols, anio_max_historia),
            'correlaciones_pearson': pearson, 'correlaciones_spearman': spearman, 'n_pares_correlacion': tamanos,
            'pares_correlacionados': pares, 'correlaciones_externas_anuales': anuales,
            'diagnostico_vif': vifs, 'dependencias_lineales': deps}


def diccionario(cat, spec):
    nb07 = 'notebooks/07_baseline_variantes.ipynb'
    celda = spec['evidencia']['listas_E0_E1_E2'].split(';')[0]
    patrones = {'crecimiento': "f'crecimiento_{col}'", 'cambio': "f'cambio_{col}_activo_previo'", 'rezago': "f'{col}_lag{lag}'",
                'volatilidad': "f'{col}_{stat}3_previa'"}
    escalas = {'ratio': 'fracción decimal (0.05 = 5 %)', 'crecimiento': 'fracción decimal (0.10 = 10 %)',
               'cambio': 'fracción decimal del activo t-1', 'rezago': 'unidades monetarias reportadas en la moneda de la fila; escala (unidades o miles) no acreditada',
               'volatilidad': 'unidades monetarias reportadas en la moneda de la fila; escala no acreditada'}
    referencia = {'ratio': 't', 'crecimiento': 't y t-1', 'cambio': 't y t-1', 'volatilidad': 't-3, t-2 y t-1'}
    filas = []
    for orden, r in enumerate(cat.itertuples(), 1):
        v, info, grupo = r.variable, tipo_atributo(r.variable), grupo_atributo(r.variable, spec)
        evid = [_fila_csv(CATALOGO, v), celda]
        if grupo == 'financiero':
            fuente = ('SMV: estados financieros individuales anuales (data/processed/panel_fcl_preliminar.csv); '
                      'extracción histórica de FCO/CAPEX no reproducible (reports/procedimiento_smv.md)')
            evid.insert(0, _linea('src/feature_engineering.py', f"'{v}': (" if info['tipo'] == 'ratio' else patrones[info['tipo']]))
            escala, codigo = escalas[info['tipo']], ''
            anio = referencia.get(info['tipo'], f"t-{info['k']}")
        elif grupo == 'macroeconomico':
            fuente = r.fuente_original if r.fuente_original == 'BCRP' else f'{r.fuente_original} vía BCRP'
            fuente, codigo = f'{fuente} ({r.url_ficha})', r.codigo
            evid += ['data/processed/macroeconomia_peru_2005_2025.csv', _fila_csv('reports/diccionario_macroeconomia_bcrp.csv', r.codigo)]
            escala = 'S/ por US$ (nivel)' if 'tipo_cambio' in v else 'puntos porcentuales (5.0 = 5 %)'
            anio = 'año calendario t (agregado anual)'
        else:
            fuente, codigo = f'BCRP, serie {r.codigo} (mercado bursátil agregado)', r.codigo
            evid += ['data/processed/bursatil_mercado_anual.csv', _fila_csv('reports/bursatil_diccionario_indicadores.csv', v)]
            escala = 'millones de PEN nominales' if 'monto' in v else 'puntos porcentuales anuales' if 'rentabilidad' in v else 'puntos porcentuales anualizados'
            anio = 'año calendario t (agregado anual)'
        filas.append(dict(orden=orden, nombre=v, grupo=grupo, definicion=r.metodo,
                          interpretacion=r.justificacion or r.descripcion, unidad=r.unidad_final, escala=escala, anio_referencia=anio,
                          fuente_original=fuente, codigo_serie=codigo, disponibilidad_documentada=r.disponibilidad,
                          preparacion_E2=spec['preparacion_principal'].split(' -> Ridge')[0],
                          evidencia='; '.join(evid)))
    return pd.DataFrame(filas)


def auditoria_temporal(d, cols, spec):
    tr, h = training(d), historia(d)
    rev = h.revision_interanual.astype(bool)
    publicacion_fin = 'No registrada por fila; los EEFF anuales de t solo pueden publicarse tras el cierre de t'
    vintage_fin = ('Desconocido: un valor por empresa-ejercicio, sin indicar el reporte del que proviene; '
                   'revision_interanual sin algoritmo documentado (reports/revision_entrega_semana5.md)')
    pronostico = 'No definida en Sprint 06; hipótesis documentada: tras publicar los EEFF de t ("Al publicar estados de t")'
    filas = []
    for v in cols:
        info, grupo = tipo_atributo(v), grupo_atributo(v, spec)
        observado = tr[v].notna()
        if info['tipo'] in {'ratio', 'crecimiento', 'cambio'}:
            expuesto = tr.revision_interanual.astype(bool)
            clase = 'POSIBLE FUGA TEMPORAL'
            fundamento = ('Usa montos de t. En filas con revision_interanual=True el valor de t podría provenir de la columna comparativa '
                          'del reporte de t+1 (reexpresión), publicada después de la fecha de pronóstico; la fórmula no usa t+1, '
                          'pero la fuente no permite descartarlo. No es fuga probada.')
            anio = 't' if info['tipo'] == 'ratio' else 't y t-1'
            sens = 'POSIBLE FUGA TEMPORAL (EEFF de t no publicados al 31/12/t)'
        elif info['tipo'] in {'rezago', 'volatilidad'}:
            js = [info['k']] if info['tipo'] == 'rezago' else [1, 2, 3]
            expuesto = sum(rev.groupby(h.segmento_temporal, sort=False).shift(j).fillna(False).astype(int) for j in js).loc[tr.index].gt(0)
            clase = 'DISPONIBILIDAD NO VERIFICADA'
            fundamento = ('Solo usa años <= t-1, cuyos reportes (incluida una eventual reexpresión comparativa publicada con los EEFF de t) '
                          'son anteriores o simultáneos a la fecha de pronóstico. Sin fechas por fila ni vintages no se certifica; '
                          'revisiones posteriores a t no pueden descartarse.')
            anio = f"t-{info['k']}" if info['tipo'] == 'rezago' else 't-3, t-2 y t-1'
            sens = 'DISPONIBILIDAD NO VERIFICADA'
        else:
            expuesto = pd.Series(np.nan, index=tr.index)
            anio = 'año calendario t'
            sens = 'POSIBLE FUGA TEMPORAL (agregado anual completo solo después del 31/12/t)'
            if v == 'crecimiento_pbi_real_pct':
                clase = 'POSIBLE FUGA TEMPORAL'
                fundamento = ('Variación anual del PBI: cifra preliminar publicada después del año y revisada en años siguientes; '
                              'el panel usa la consulta revisada de 2026-10-21, no el valor disponible al pronosticar.')
            elif grupo == 'macroeconomico':
                clase = 'DISPONIBILIDAD NO VERIFICADA'
                fundamento = ('Agregado de datos mensuales de t, conocidos al cierre de t; serie consultada en 2026 sin vintage ni '
                              'fecha de publicación histórica. Revisión o rebase posible pero no documentado.')
            else:
                clase = 'DISPONIBILIDAD NO VERIFICADA'
                fundamento = ('Agregado de mercado de t observado al cierre de t; consulta BCRP verificada el 2026-10-22, sin vintage; '
                              'transición metodológica de mayo 2015 sin empalme propio.')
        filas.append(dict(
            variable=v, grupo=grupo, anio_referencia=anio,
            fecha_publicacion=publicacion_fin if grupo == 'financiero' else 'No registrada; publicada por BCRP después del periodo de referencia',
            vintage=vintage_fin if grupo == 'financiero' else ('Consulta revisada BCRP 2026-10-21 (reports/validacion_macroeconomia_bcrp.json)'
                                                              if grupo == 'macroeconomico' else 'Consulta BCRP verificada 2026-10-22 (reports/validacion_extraccion_bursatil.json)'),
            fecha_pronostico=pronostico, clasificacion=clase, fundamento=fundamento,
            # Filas train con dato cuya fila fuente (t, o t-k en rezagos/ventanas) tiene revision_interanual=True.
            pct_filas_train_con_revision_interanual=100 * expuesto[observado].astype(float).mean(),
            clasificacion_si_pronostico_31dic_t=sens,
            sensibilidad_sprint06='Externos t-1: reduce simultaneidad, no elimina revisiones ni acredita publicación' if grupo != 'financiero' else 'Sin sensibilidad temporal en Sprint 06',
            accion=('Recuperar reportes originales y su fecha de presentación SMV; documentar el algoritmo de revision_interanual'
                    if grupo == 'financiero' else 'Obtener vintages o fechas de publicación BCRP/INEI; fijar fecha operativa de pronóstico')))
    t = pd.DataFrame(filas)
    assert t.clasificacion.isin(CATEGORIAS_TEMPORALES).all()
    return t


def _fmt(x, nd=2):
    return 'NA' if pd.isna(x) else 'inf' if np.isinf(x) else f'{x:.{nd}f}'


def hallazgos(tablas, spec, temporal):
    q, pares, casos, saltos = tablas['calidad_atributos'], tablas['pares_correlacionados'], tablas['denominadores_casos_train'], tablas['saltos_escala_train']
    vifs, deps, anuales, causas = tablas['diagnostico_vif'], tablas['dependencias_lineales'], tablas['correlaciones_externas_anuales'], tablas['faltantes_causas_train']
    out = []

    def add(estado, categoria, moneda, variables, evidencia, interpretacion, accion):
        out.append(dict(estado=estado, categoria=categoria, moneda=moneda, variables=variables,
                        evidencia=evidencia.rstrip('.'), interpretacion=interpretacion, accion=accion))

    for r in pares.loc[pares.depende_de_un_caso].itertuples():
        add('COMPROBADO', 'correlación dominada por un caso', r.moneda, f'{r.variable_1};{r.variable_2}',
            f'Pearson={r.pearson:.6f} (n={r.n_pares}); sin {r.caso_influyente}: {r.pearson_sin_caso_influyente:.4f}; Spearman={r.spearman:.4f}',
            'La correlación alta de Pearson no describe la muestra: la determina una observación. No implica redundancia ni irrelevancia.',
            'Conciliar el caso con la fuente documental antes de cualquier decisión de redundancia.')
    for moneda, g in casos.groupby('moneda'):
        top = g.sort_values('relativo_moneda').drop_duplicates(['RPJ', 'Ejercicio', 'denominador']).head(6)
        add('COMPROBADO', 'denominador positivo pequeño', moneda, ';'.join(sorted(g.variable.unique())),
            f'{len(g)} celdas ({g[["RPJ", "Ejercicio"]].drop_duplicates().shape[0]} empresa-ejercicio) con fracción {FRACCION_DENOMINADOR:g}: '
            f'transversal {int(g.criterio_transversal.sum())}, intraempresa {int(g.criterio_intraempresa.sum())}, con atributo extremo RIQ '
            f'{int(g.atributo_extremo_RIQ.sum())}; menores: ' + '; '.join(f'{r.RPJ} {r.Ejercicio} {r.denominador}={r.valor_denominador:g}' for r in top.itertuples()),
            'El criterio transversal señala sobre todo empresas pequeñas (o de escala distinta), cuyo ratio puede ser normal; el intraempresa '
            'señala caídas respecto de la propia historia. Denominadores pequeños amplifican el ratio; el umbral es exploratorio y no prueba error contable.',
            'Revisar casos en denominadores_casos_train.csv contra estados financieros originales.')
    picos = saltos.loc[saltos.patron_pico]
    if len(saltos):
        add('COMPROBADO', 'salto intraempresa de magnitud', ';'.join(sorted(saltos.moneda.unique())), ';'.join(sorted(saltos.columna.unique())),
            f'{len(saltos)} cambios >= {FACTOR_SALTO}x entre años consecutivos ({len(picos)} con reversión al año siguiente): '
            + '; '.join(f'{r.RPJ} {r.Ejercicio} {r.columna} x{r.factor:.3g}' for r in saltos.sort_values('factor', key=np.abs, ascending=False).head(6).itertuples()),
            'Hecho numérico verificable en la fuente; su causa no está determinada.',
            'Ver saltos_escala_train.csv; conciliar con reportes SMV.')
    if len(picos):
        add('SOSPECHA PENDIENTE', 'posible inconsistencia de escala', ';'.join(sorted(picos.moneda.unique())), ';'.join(sorted(picos.columna.unique())),
            '; '.join(f'{r.RPJ} {r.Ejercicio} {r.columna}: {r.valor_t_1:g} -> {r.valor_t:g} -> {r.valor_t_mas_1:g}' for r in picos.itertuples()),
            'Un salto de ~1000x que revierte al año siguiente es compatible con unidades vs miles, pero también con eventos reales; no se declara error.',
            'Conciliación documental; no corregir ni excluir sin evidencia.')
    est = q.assign(pct=lambda x: 100 * x.faltantes_estructurales / x.faltantes_n.where(x.faltantes_n > 0)).loc[lambda x: x.faltantes_estructurales > 0]
    add('COMPROBADO', 'faltantes estructurales por rezago', 'ambas', ';'.join(est.variable.unique()),
        '; '.join(f'{r.moneda} {r.variable}: {r.faltantes_estructurales}/{r.faltantes_n}' for r in est.loc[est.variable.str.contains('lag3|std3')].itertuples()),
        'La mayor parte de los faltantes de rezagos/ventanas se explica por historia contigua insuficiente (inicio 2005, entrada o ruptura), no por errores.',
        'Tratar como ausencia estructural en la etapa de modelado; la mediana E2 los imputa sin indicador.')
    reg = causas.loc[causas.grupo_causa.eq('regla')].groupby(['moneda', 'causa']).n.sum()
    if len(reg):
        add('COMPROBADO', 'indefinidos por regla de cálculo', 'ambas', ';'.join(sorted(causas.loc[causas.grupo_causa.eq('regla'), 'variable'].unique())),
            'celdas: ' + '; '.join(f'{m} {c}: {n}' for (m, c), n in reg.items()),
            'NaN deliberados de Sprint 06 (denominador/ingreso no positivo, CAPEX positivo); no son faltantes de fuente.', 'Documentar en la etapa de modelado.')
    noexp = int(q.faltantes_no_explicados.sum())
    add('COMPROBADO', 'control de causas de faltantes', 'ambas', 'todas',
        f'{int(q.faltantes_n.sum())} celdas faltantes en train; no explicadas por las reglas de Sprint 06: {noexp}', 'Las causas reconstruidas cubren todos los faltantes.' if noexp == 0 else 'Hay faltantes sin causa identificada.',
        'Ninguna' if noexp == 0 else 'Investigar faltantes no explicados.')
    altos = anuales.loc[anuales.pearson_anual.abs().ge(UMBRAL_CORRELACION) | anuales.spearman_anual.abs().ge(UMBRAL_CORRELACION)]
    add('COMPROBADO', 'series externas repetidas', 'ambas', ';'.join(spec['macroeconomicos'] + spec['bursatiles']),
        f'{anuales.n_anios.max()} valores anuales distintos en train, repetidos entre empresas; pares anuales |r|>={UMBRAL_CORRELACION}: '
        + ('; '.join(f'{r.variable_1}~{r.variable_2} {r.pearson_anual:.3f}' for r in altos.drop_duplicates(['variable_1', 'variable_2']).itertuples()) or 'ninguno'),
        'El tamaño efectivo para relaciones entre externos es de 16 años, no de miles de filas; su correlación por filas pondera años por número de empresas.',
        'No usar n por filas para inferencia sobre externos.')
    for moneda, g in vifs.loc[vifs.especificacion.eq('imputada_mediana_E2') & vifs.VIF.ge(VIF_REFERENCIA)].groupby('moneda'):
        otras = {e: vifs.loc[vifs.especificacion.eq(e) & vifs.moneda.eq(moneda)].set_index('variable').VIF
                 for e in ['casos_completos', 'imputada_sin_casos_influyentes']}
        add('COMPROBADO', f'VIF >= {VIF_REFERENCIA} (referencia convencional)', moneda, ';'.join(g.variable),
            '; '.join(f'{r.variable}: {_fmt(r.VIF, 1)} (casos completos {_fmt(otras["casos_completos"].get(r.variable), 1)}'
                      + (f', sin casos influyentes {_fmt(otras["imputada_sin_casos_influyentes"].get(r.variable), 1)}' if len(otras['imputada_sin_casos_influyentes']) else '')
                      + ')' for r in g.itertuples()),
            'Redundancia lineal condicionada a la imputación por mediana y a pocos casos extremos; no indica irrelevancia predictiva ni justifica eliminar.',
            'Considerar en la selección junto con la evidencia temporal y de denominadores.')
    cond = vifs.groupby(['moneda', 'especificacion']).numero_condicion.first()
    for moneda in sorted(vifs.loc[vifs.especificacion.eq('imputada_sin_casos_influyentes'), 'moneda'].unique()):
        quitados = pares.loc[pares.depende_de_un_caso & pares.moneda.eq(moneda)].drop_duplicates(['RPJ_influyente', 'Ejercicio_influyente'])
        add('COMPROBADO', 'condicionamiento dominado por pocos casos', moneda, 'todas',
            f'Número de condición imputado {cond[(moneda, "imputada_mediana_E2")]:.2f}; sin {len(quitados)} casos '
            f'({", ".join(quitados.caso_influyente)}): {cond[(moneda, "imputada_sin_casos_influyentes")]:.2f}',
            'La sensibilidad numérica alta de la matriz E2 en esta moneda proviene de pocas filas extremas, no de una colinealidad general.',
            'Conciliar esos casos; cualquier tratamiento debe decidirse con datos de entrenamiento y documentarse.')
    exactas = deps.loc[deps.tipo.str.contains('exacta|duplicada')]
    constantes = q.loc[q.es_constante]
    add('COMPROBADO', 'control: constantes, duplicados y dependencias exactas', 'ambas', 'todas',
        f'constantes={len(constantes)}; duplicados/afines/dependencias exactas={len(exactas)}; filas duplicadas={int(deps.tipo.str.startswith("filas duplicadas").sum())}; '
        f'rango imputado: ' + '; '.join(f'{m} {int(g.rango.iloc[0])}/26' for m, g in vifs.loc[vifs.especificacion.eq("imputada_mediana_E2")].groupby('moneda')),
        'Sin dependencia exacta con tolerancia numérica; la colinealidad es aproximada.', 'Ninguna')
    pct_rev = temporal.set_index('variable').pct_filas_train_con_revision_interanual
    contemp = temporal.loc[temporal.clasificacion.eq('POSIBLE FUGA TEMPORAL') & temporal.grupo.eq('financiero'), 'variable']
    add('COMPROBADO', 'ausencia de fechas de publicación y pronóstico', 'ambas', 'todas',
        'El repositorio no registra fecha de presentación por empresa-ejercicio, vintage financiero ni fecha operativa de pronóstico; '
        f'revision_interanual=True en {pct_rev[contemp].min():.1f}–{pct_rev[contemp].max():.1f} % de las filas train con dato.',
        'Ningún atributo puede clasificarse como DISPONIBILIDAD VERIFICADA con la evidencia local.', 'Definir fecha de pronóstico y recuperar fechas SMV.')
    add('SOSPECHA PENDIENTE', 'posible fuga por reexpresión', 'ambas', ';'.join(contemp),
        'revision_interanual sin algoritmo documentado; posible uso de cifras comparativas publicadas en t+1.',
        'Si el valor de t proviene del reporte de t+1, el atributo contiene información posterior al pronóstico. No probado.',
        'Recuperar ambos reportes y comparar; sensibilidad que excluya o marque filas revisadas, solo en entrenamiento.')
    add('SOSPECHA PENDIENTE', 'revisiones del PBI', 'ambas', 'crecimiento_pbi_real_pct',
        'Serie revisada consultada el 2026-10-21; sin vintages.', 'El valor usado puede diferir del preliminar disponible al pronosticar.',
        'Construir vintages en tiempo real o usar sensibilidad t-1 (que tampoco elimina revisiones).')
    add('SOSPECHA PENDIENTE', 'escala monetaria no acreditada', 'ambas',
        ';'.join(v for v in spec['financieros'] if tipo_atributo(v)['tipo'] in {'rezago', 'volatilidad'}),
        'Rezagos y volatilidades en unidades reportadas; data/README.md declara escala no acreditada.',
        'Diferencias de escala entre emisores (unidades o miles) dominarían magnitudes, colas y VIF de atributos en niveles.',
        'Acreditar la unidad por emisor-ejercicio antes de comparar niveles.')
    add('SOSPECHA PENDIENTE', 'comparabilidad bursátil 2015', 'ambas', ';'.join(spec['bursatiles']),
        'Transición metodológica documentada en mayo de 2015; sin empalme.', 'Posible quiebre de nivel en rentabilidad y volatilidad.',
        'Revisar documentación BVL/S&P; no corregir sin evidencia.')
    out = pd.DataFrame(out).sort_values('estado', kind='stable').reset_index(drop=True)
    out.insert(0, 'id', [f'H{i + 1:02d}' for i in range(len(out))])
    return out


def tabla_final(tablas, dic, temporal, spec):
    q, pares, vifs = tablas['calidad_atributos'], tablas['pares_correlacionados'], tablas['diagnostico_vif']
    casos, saltos = tablas['denominadores_casos_train'], tablas['saltos_escala_train']
    tem = temporal.set_index('variable')
    filas = []
    for r in dic.itertuples():
        v = r.nombre
        qv = q.loc[q.variable.eq(v)]
        calidad_txt = ' | '.join(f'{x.moneda}: faltan {x.faltantes_pct:.1f}% (estr. {x.faltantes_estructurales}, regla {x.faltantes_regla}, '
                                 f'fuente {x.faltantes_fuente}); extremos RIQ {x.extremos_RIQ}; asim. {x.asimetria:.1f}' for x in qv.itertuples())
        cv = casos.loc[casos.variable.eq(v)]
        if len(cv):
            calidad_txt += (f' | denominador pequeño: {len(cv)} casos (transversal {int(cv.criterio_transversal.sum())}, '
                            f'intraempresa {int(cv.criterio_intraempresa.sum())}, atributo extremo {int(cv.atributo_extremo_RIQ.sum())})')
        rel = pares.loc[pares.variable_1.eq(v) | pares.variable_2.eq(v)]
        partes = []
        for x in rel.sort_values('pearson', key=np.abs, ascending=False).itertuples():
            otro = x.variable_2 if x.variable_1 == v else x.variable_1
            partes.append(f'{x.moneda} {otro} P={x.pearson:.2f}/S={x.spearman:.2f}' + (' (un caso)' if x.depende_de_un_caso else ''))
        vi = vifs.loc[vifs.variable.eq(v) & vifs.especificacion.eq('imputada_mediana_E2')]
        vc = vifs.loc[vifs.variable.eq(v) & vifs.especificacion.eq('casos_completos')].set_index('moneda').VIF
        redund = ('pares |r|>=0.8: ' + ('; '.join(partes[:4]) if partes else 'ninguno') + ' | VIF imputado/casos completos: '
                  + '; '.join(f'{x.moneda} {_fmt(x.VIF, 1)}/{_fmt(vc.get(x.moneda), 1)}' for x in vi.itertuples()))
        info, grupo = tipo_atributo(v), r.grupo
        obs = []
        if grupo == 'financiero':
            obs.append('No mezclar monedas.')
            if info['tipo'] in {'rezago', 'volatilidad'}:
                obs.append('Nivel monetario con escala no acreditada; faltantes mayormente estructurales.')
            else:
                obs.append('Fracción decimal; extremos RIQ no prueban error.')
            sv = saltos.loc[saltos.columna.isin([info.get('den'), info.get('num'), info.get('col')])]
            if 'den' in info and len(sv):
                obs.append('Afectado por saltos de magnitud en su denominador.')
        else:
            obs.append('16 valores anuales repetidos entre empresas: n efectivo = años, no filas.')
            if grupo == 'bursatil':
                obs.append('Transición metodológica 2015.')
        clase = tem.loc[v, 'clasificacion']
        condiciones = []
        if clase == 'POSIBLE FUGA TEMPORAL':
            condiciones.append('verificar reexpresiones (revision_interanual) antes del modelo final' if grupo == 'financiero'
                               else 'verificar vintage y revisiones antes del modelo final')
        else:
            condiciones.append('documentar fecha de publicación')
        if rel.depende_de_un_caso.any() or cv.criterio_intraempresa.any() or cv.atributo_extremo_RIQ.any():
            condiciones.append('conciliar casos influyentes o de denominador pequeño')
        if (vi.VIF >= VIF_REFERENCIA).any() or (rel.supera_spearman.any() and not rel.depende_de_un_caso.all()):
            condiciones.append('evaluar redundancia en la selección con validación temporal dentro de train')
        rec = 'Conservar provisionalmente; ' + '; '.join(condiciones)
        filas.append(dict(nombre=v, origen=f'{grupo}: {r.fuente_original.split(" (")[0]}', definicion=r.definicion, calidad=calidad_txt,
                          redundancia=redund, riesgo_temporal=clase, observaciones=' '.join(obs), recomendacion=rec))
    return pd.DataFrame(filas)


def _archivos():
    actuales = {}
    for p in ROOT.rglob('*'):
        rel = p.relative_to(ROOT).as_posix()
        if p.is_file() and not IGNORADOS.intersection(p.relative_to(ROOT).parts) and rel not in PROPIOS and not rel.startswith(PROPIOS_DIRS):
            actuales[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return dict(sorted(actuales.items()))


def verificar_integridad(actuales=None):
    """Compara contra HEAD (archivos rastreados) y contra la referencia previa a esta revisión (todos)."""
    actuales = _archivos() if actuales is None else actuales
    ref = pd.read_csv(REFERENCIA_INTEGRIDAD, dtype=str, keep_default_na=False)
    refd = dict(zip(ref.ruta, ref.sha256))
    try:
        git = lambda *a: subprocess.run(['git', '-C', str(ROOT), *a], capture_output=True, text=True, check=True).stdout
        head = git('rev-parse', 'HEAD').strip()
        rastreados_modificados = [x[3:] for x in git('status', '--porcelain', '--untracked-files=no').splitlines()]
    except (OSError, subprocess.CalledProcessError):
        head, rastreados_modificados = None, None
    return dict(
        referencia='reports/sprint_08/referencia_integridad_previa.csv',
        referencia_descripcion=('SHA-256 de todos los archivos fuera de Sprint 08, tomados el 2026-10-24 al inicio de esta revisión y antes '
                                'de editar; posterior a la implementación inicial de Sprint 08.'),
        archivos_referencia=len(refd), modificados=sorted(k for k in refd if k in actuales and actuales[k] != refd[k]),
        ausentes=sorted(k for k in refd if k not in actuales), nuevos_fuera_de_sprint08=sorted(set(actuales) - set(refd)),
        git_head=head, git_rastreados_modificados=rastreados_modificados,
        alcance=('Para archivos rastreados, git status contra HEAD acredita que no cambiaron desde el último commit. Para no rastreados '
                 '(Sprint 07 y evidencia sectorial), la referencia solo acredita ausencia de cambios desde el inicio de esta revisión.'))


def resumen(tablas, spec, dic, temporal, final, hall, integridad):
    q, vifs, pares, casos = tablas['calidad_atributos'], tablas['diagnostico_vif'], tablas['pares_correlacionados'], tablas['denominadores_casos_train']
    den = tablas['denominadores_train']
    conteo = temporal.clasificacion.value_counts()
    L = ['# Sprint 08 — Etapa 1: auditoría de calidad de los 26 atributos de E2', '',
         'Auditoría descriptiva: no se entrenan modelos, no se eliminan atributos y no se modifican datos, particiones, FCL ni '
         'E0/E1/E2. Todo diagnóstico utilizable para selección usa solo entrenamiento (2.869 filas, objetivos 2006–2021), por moneda; '
         'no se consultan filas ni métricas de prueba.', '',
         '## 1. Especificación recuperada de Sprint 06', '',
         f'- **Financieros (19):** {", ".join(spec["financieros"])}. Excluidas por identidad exacta, no por desempeño: {", ".join(spec["redundantes_excluidas_por_definicion"])}.',
         f'- **Macroeconómicos (4):** {", ".join(spec["macroeconomicos"])}.',
         f'- **Bursátiles (3):** {", ".join(spec["bursatiles"])}.',
         f'- **Objetivo:** {spec["objetivo"]["definicion"]} Horizonte: {spec["objetivo"]["horizonte"]}. Elegibilidad: {spec["objetivo"]["elegibilidad"]}.',
         f'- **Particiones:** {spec["objetivo"]["particion"]}. Panel 4.221; elegibles 3.560 (2.869/691).',
         f'- **Preparación principal:** {spec["preparacion_principal"]}.',
         f'- **Sensibilidades:** {"; ".join(spec["sensibilidades"])}. El RobustScaler de `src/feature_engineering.py` (make_preprocessor) no es la configuración E2.',
         '- **Evidencia:** ' + '; '.join(f'{k}: `{v}`' for k, v in spec['evidencia'].items()) + '.', '',
         '## 2. Método y criterios', '',
         '- Descriptivos sin imputar; desviación con ddof=1; asimetría ajustada de pandas; percentiles con interpolación lineal; extremos fuera de Q1−1,5·RIQ y Q3+1,5·RIQ. Un extremo es una señal de revisión, no un error.',
         '- Faltantes clasificados por causa reconstruida de las reglas de Sprint 06: **estructural** (historia contigua insuficiente para el rezago: inicio del panel en 2005, entrada de la empresa o ruptura de segmento), **regla** (denominador/ingreso no positivo, CAPEX positivo) y **fuente** (monto ausente).',
         f'- Denominadores positivos pequeños: criterio transversal (≤ {FRACCION_DENOMINADOR:g} × mediana positiva de la moneda) o intraempresa (≤ {FRACCION_DENOMINADOR:g} × mediana positiva de la propia empresa, ≥ {MIN_OBS_EMPRESA} años hasta 2020). Sensibilidad con {", ".join(f"{f:g}" for f in FRACCIONES_DENOMINADOR)}. Es un umbral exploratorio, no una regla financiera universal.',
         f'- Saltos de magnitud: cambio ≥ {FACTOR_SALTO}× entre años consecutivos del mismo segmento en ActivoTotal, PasivoTotal o TotalIngreso; "pico" si revierte ≥ {FACTOR_SALTO}× al año siguiente (solo años ≤ 2020).',
         f'- Pearson y Spearman por pares observados (mínimo 3); umbral exploratorio |r| ≥ {UMBRAL_CORRELACION}. Para cada par alto se recalcula Pearson excluyendo cada observación (leave-one-out); un cambio ≥ {CAMBIO_LOO_RELEVANTE} indica dependencia de un caso. Los externos se correlacionan además sobre sus 16 valores anuales. Correlación alta ≠ dependencia lineal exacta ≠ irrelevancia predictiva.',
         f'- VIF por OLS auxiliar sobre columnas centradas y estandarizadas (intercepto implícito) en cuatro especificaciones: (a) imputada con la mediana de entrenamiento y StandardScaler, réplica de la matriz E2; (b) casos completos sin imputar; (c) imputada sin los casos que dominan un par correlacionado (sensibilidad, no limpieza); (d) bloque externo anual (16 años). La imputación por mediana crea masas en la mediana que atenúan correlaciones (VIF subestimado) o, con faltantes compartidos (rezago 3 y ventana), pueden crear asociación artificial. El VIF es algebraico: con panel dependiente y externos repetidos no admite inferencia iid. VIF ≥ {VIF_REFERENCIA} es solo una referencia convencional.',
         f'- Dependencias exactas: valores singulares ≤ máx(s)·máx(n,p)·eps; casi dependencias: índice de condición ≥ {INDICE_CONDICION} con ≥ 2 proporciones de varianza ≥ {PROPORCION_VARIANZA} (Belsley, sobre datos centrados; exploratorio). Duplicados: columnas idénticas, relaciones afines exactas y filas repetidas.', '',
         '## 3. Controles verificados', '',
         '- Las 26 columnas y su orden coinciden con el código literal del notebook 07, el catálogo y `validacion_baseline.json`; las variables financieras y la etiqueta se reconstruyen con igualdad exacta desde `panel_fcl_preliminar.csv`; los externos coinciden con las series anuales por Ejercicio.',
         '- Se preservan 4.221 filas, 3.560 elegibles y particiones 2.869/691.',
         '- Pruebas de aislamiento: perturbar filas de prueba/no elegibles y montos fuente de ejercicios ≥ 2021 no cambia ningún diagnóstico; dos controles positivos (incluir prueba en `training` o extender la historia a 2025) sí los cambian, lo que demuestra que la perturbación es detectable.',
         '- Número de condición de la matriz imputada y estandarizada: ' + '; '.join(f'{m} {g.numero_condicion.iloc[0]:.4f}' for m, g in vifs.loc[vifs.especificacion.eq('imputada_mediana_E2')].groupby('moneda')) + ', igual al de `reports/sprint_06/diagnostico_colinealidad.csv` (verificado en pruebas).',
         f'- Integridad: archivos rastreados modificados respecto de HEAD ({integridad["git_head"][:7] if integridad["git_head"] else "git no disponible"}): {len(integridad["git_rastreados_modificados"] or [])}; '
         f'archivos de la referencia previa modificados: {len(integridad["modificados"])}, ausentes: {len(integridad["ausentes"])}. {integridad["alcance"]}', '',
         '## 4. Problemas comprobados', '']
    for r in hall.loc[hall.estado.eq('COMPROBADO')].itertuples():
        L.append(f'- **{r.id} — {r.categoria} ({r.moneda}).** {r.evidencia}. {r.interpretacion}')
    L += ['', '## 5. Sospechas pendientes de investigación', '']
    for r in hall.loc[hall.estado.eq('SOSPECHA PENDIENTE')].itertuples():
        L.append(f'- **{r.id} — {r.categoria}.** {r.evidencia}. {r.interpretacion} Acción: {r.accion}')
    L += ['', '## 6. Auditoría temporal', '',
          '- **Año de referencia:** periodo económico que mide el atributo (t, t−k o año calendario t). **Fecha de publicación:** cuándo la fuente lo hizo público (no registrada por fila). **Vintage:** versión del dato usada (financieros: desconocida; externos: consultas de octubre de 2026). **Fecha de pronóstico:** momento en que se emitiría la predicción de FCL(t+1); Sprint 06 no la define y solo documenta "Al publicar estados de t".',
          '- La alineación t → t+1 garantiza que la fórmula no use t+1, pero no certifica que el dato estuviera publicado ni que fuera la versión disponible; por eso ningún atributo se clasifica como verificado.',
          f'- Resultado: ' + '; '.join(f'{k}: {conteo.get(k, 0)}' for k in CATEGORIAS_TEMPORALES) + '. Con pronóstico al 31/12/t, todos los atributos de t pasarían a posible fuga (columna de sensibilidad).', '',
          '## 7. Tabla de los 26 atributos', '',
          '| Atributo | Origen | Calidad (train) | Redundancia | Riesgo temporal | Recomendación provisional |', '|---|---|---|---|---|---|']
    for r in final.itertuples():
        L.append('| ' + ' | '.join(str(a).replace('|', '/') for a in [r.nombre, r.origen, r.calidad, r.redundancia, r.riesgo_temporal, r.recomendacion]) + ' |')
    L += ['', 'Definiciones y observaciones metodológicas completas: `tabla_26_atributos.csv` y `diccionario_atributos.csv`.', '',
          '## 8. Limitaciones', '',
          '- No se consultaron fuentes externas nuevas ni reportes SMV originales: los hallazgos de escala y denominadores quedan como casos a conciliar.',
          '- Las causas de faltantes reproducen las reglas de Sprint 06; no explican por qué falta un monto en la fuente.',
          '- La muestra elegible depende de eventos de t+1 (empresa que sigue reportando con la misma moneda): sesgo de supervivencia heredado, documentado en Sprint 06.',
          '- Los umbrales (|r| ≥ 0,8, VIF ≥ 10, fracción 0,01, factor 100, índice 30) son exploratorios y se reportan con sensibilidad o valores completos.',
          '- Las recomendaciones son provisionales y no usan resultados de prueba; la selección queda para una etapa posterior con validación temporal dentro de entrenamiento.', '',
          '## 9. Reproducción y archivos', '',
          '`python scripts/reproduce_auditoria_calidad.py` o el notebook `notebooks/sprint_08/11_auditoria_calidad_atributos.ipynb`; pruebas: `python -m unittest tests.test_auditoria_calidad -v`. '
          'Entregables: diccionario_atributos, calidad_atributos, correlaciones_pearson, correlaciones_spearman, diagnostico_vif, auditoria_temporal, hallazgos_calidad (CSV) y este resumen. '
          'Anexos: cobertura_temporal_train, faltantes_causas_train, denominadores_train, denominadores_casos_train, saltos_escala_train, pares_correlacionados, n_pares_correlacion, '
          'correlaciones_externas_anuales, dependencias_lineales, tabla_26_atributos, especificacion_e2.json, integridad.json y referencia_integridad_previa.csv.']
    return '\n'.join(L) + '\n'


def run(out=None):
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    antes = _archivos()
    d, cols, cat = load_inputs()
    spec = especificacion_e2()
    tablas = diagnostics(d, cols)
    dic = diccionario(cat, spec)
    temporal = auditoria_temporal(d, cols, spec)
    hall = hallazgos(tablas, spec, temporal)
    final = tabla_final(tablas, dic, temporal, spec)
    tablas.update({'diccionario_atributos': dic, 'auditoria_temporal': temporal, 'hallazgos_calidad': hall, 'tabla_26_atributos': final})
    for name, t in tablas.items():
        t.to_csv(out / f'{name}.csv', index=name.startswith(('correlaciones_pearson', 'correlaciones_spearman', 'n_pares')), float_format='%.15g')
    (out / 'especificacion_e2.json').write_text(json.dumps(spec, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    integridad = verificar_integridad(antes)
    (out / 'resumen_auditoria.md').write_text(resumen(tablas, spec, dic, temporal, final, hall, integridad), encoding='utf-8')
    despues = _archivos()
    assert antes == despues, 'La auditoría modificó archivos fuera de Sprint 08'
    integridad.update(sin_cambios_durante_ejecucion=antes == despues, panel=len(d), elegibles=int(d.utilizable_supervisado.sum()),
                      entrenamiento=int(d.particion.eq('entrenamiento').sum()), prueba=int(d.particion.eq('prueba').sum()), predictores=cols)
    (out / 'integridad.json').write_text(json.dumps(integridad, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return tablas
