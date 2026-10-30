"""Sprint 09 — Experimento final acotado: formulaciones del objetivo, pérdida robusta y variables externas.

Población principal: regla sectorial SMV no financiera (src/alineacion_investigacion.py). Validación anidada
de los Sprints 08–09 (años externos 2017–2021 ya examinados: exploratorio; prueba 2022–2025 no se usa).
Formulaciones (todas evaluadas en unidades monetarias originales tras reconstruir la predicción):
  directa      objetivo y = FCL(t+1)                       predicción ŷ
  persistencia objetivo y − base(t)                        base(t) + cambio predicho
  relativa     objetivo y / ActivoTotal(t)                 ratio predicho × ActivoTotal(t)
base(t) = FCL(t) válido (src/ablacion_variables.fcl_t); si falta, media de y en el entrenamiento correspondiente
(la misma regla de respaldo que la referencia de persistencia). Nunca se usa información de t+1 como predictor.
El protocolo se escribe antes de ejecutar; no es FCFF ni valoración DCF.
"""
from pathlib import Path
import json
import platform
import subprocess
import numpy as np
import pandas as pd
import sklearn
from joblib import Parallel, delayed
from sklearn.ensemble import HistGradientBoostingRegressor
import src.ablacion_variables as ab
import src.alineacion_investigacion as ai
import src.auditoria_calidad as ac
import src.comparacion_modelos as cm
import src.variantes_importancia as vi

ROOT = ab.ROOT
OUT = ROOT / 'reports/sprint_09/experimento_final'
FORMULACIONES = ('directa', 'persistencia', 'relativa')
MODELOS = ('ridge', 'boosting', 'boosting_abs')
VARIANTES = ('E0', 'E1', 'E2', 'E3')
POBLACION = 'no_financiera'


def rejillas():
    g = cm.rejillas()
    return {'ridge': g['ridge'], 'boosting': g['boosting'], 'boosting_abs': g['boosting']}


def crear(modelo, cols, cfg):
    if modelo == 'ridge':
        return ab.crear_modelo(cols, cfg['alpha'])
    fijos = {**cm.HGB_FIJOS, 'loss': 'squared_error' if modelo == 'boosting' else 'absolute_error'}
    return HistGradientBoostingRegressor(**cfg, **fijos)


def respaldo(entrenamiento):
    """Respaldo de FCL(t) faltante: media del objetivo en ese entrenamiento (igual que la referencia de persistencia)."""
    return float(entrenamiento.objetivo_fcl_t1.mean())


def base_t(tabla, b):
    return ab.fcl_t(tabla).fillna(b)


def objetivo(formulacion, tabla, b):
    y = tabla.objetivo_fcl_t1
    if formulacion == 'directa':
        return y
    if formulacion == 'persistencia':
        return y - base_t(tabla, b)
    assert (tabla.ActivoTotal > 0).all(), 'formulación relativa exige ActivoTotal(t) > 0'
    return y / tabla.ActivoTotal


def reconstruir(formulacion, pred, tabla, b):
    pred = np.asarray(pred, float)
    if formulacion == 'directa':
        return pred
    if formulacion == 'persistencia':
        return base_t(tabla, b).to_numpy() + pred
    assert (tabla.ActivoTotal > 0).all()
    return pred * tabla.ActivoTotal.to_numpy()


def ajustar_predecir(formulacion, modelo, cols, cfg, tr, va):
    """Toda la preparación, el respaldo y el objetivo transformado se aprenden solo con `tr`."""
    b = respaldo(tr)
    est = crear(modelo, cols, cfg).fit(tr[cols], objetivo(formulacion, tr, b))
    z = est.predict(va[cols])
    p = reconstruir(formulacion, z, va, b)
    assert np.isfinite(p).all()
    return p, z, b


def buscar(formulacion, modelo, pasado, cols, etiqueta):
    """Selección interna por RMSE monetario de las predicciones reconstruidas; desempate: configuración más simple."""
    cortes = cm.cortes_internos(pasado)
    filas = []
    for cfg in rejillas()[modelo]:
        rm = {}
        for anio, tr, va in cortes:
            p, _, _ = ajustar_predecir(formulacion, modelo, cols, cfg, tr, va)
            rm[f'rmse_{anio}'] = float(np.sqrt(np.mean((p - va.objetivo_fcl_t1.to_numpy()) ** 2)))
        filas.append(dict(**etiqueta, formulacion=formulacion, modelo=modelo, configuracion=json.dumps(cfg), **rm, rmse_interno_medio=float(np.mean(list(rm.values())))))
    medias = [f['rmse_interno_medio'] for f in filas]
    k = next(i for i, v in enumerate(medias) if v <= min(medias) * (1 + cm.EMPATE_REL))
    for i, f in enumerate(filas):
        f['elegida'] = i == k
    return rejillas()[modelo][k], filas


def procedimiento(formulacion, modelo, variante):
    return f'{formulacion}|{modelo}:{variante}'


def comparaciones_previstas():
    pares = []
    for m in MODELOS:
        for v in VARIANTES:
            for f in ('persistencia', 'relativa'):
                pares.append((procedimiento(f, m, v), procedimiento('directa', m, v), f'formulación: {f} frente a directa'))
    for f in FORMULACIONES:
        for v in VARIANTES:
            pares.append((procedimiento(f, 'boosting_abs', v), procedimiento(f, 'boosting', v), 'pérdida: absoluta frente a cuadrática'))
            pares.append((procedimiento(f, 'boosting', v), procedimiento(f, 'ridge', v), 'algoritmo: boosting frente a Ridge'))
        for m in MODELOS:
            p = lambda v: procedimiento(f, m, v)
            pares += [(p('E1'), p('E0'), 'externos: aporte macroeconómico'), (p('E3'), p('E0'), 'externos: aporte bursátil'),
                      (p('E2'), p('E1'), 'externos: bursátil sobre macro'), (p('E2'), p('E0'), 'externos: aporte conjunto')]
            for v in VARIANTES:
                pares += [(p(v), r, 'frente a referencia simple') for r in vi.REFERENCIAS]
    return pares


def protocolo():
    return {
        'version': 'Sprint 09 — experimento final acotado; protocolo fijado antes de ejecutar',
        'caracter': 'EXPLORATORIO: años externos 2017–2021 ya examinados en Sprints 08–09; prueba 2022–2025 no se usa; sin confirmación independiente.',
        'alcance': 'Predicción del FCL preliminar t+1 (FCO + CAPEX reportado); no es FCFF validado ni valoración DCF.',
        'poblacion': {'principal': 'no_financiera: TipoSector SMV ∉ {BANCOS, SEGUROS, FINANCIERAS, A.F.P.} (regla de src/alineacion_investigacion.py)',
                      'limite_historico': 'TipoSector se toma del registro SMV de cada ejercicio; no está acreditado que la categoría reflejara la actividad vigente en cada año; '
                                          'ninguna empresa cambia de TipoSector en el panel',
                      'conservadora': 'NO se usa: emplea CIIU de 2023–2025 para clasificar ejercicios anteriores (sensibilidad retrospectiva, no disponible históricamente)'},
        'datos': 'Sin correcciones: la auditoría de unidades no acreditó errores (ver auditoria_unidades.md); no hay versión derivada.',
        'formulaciones': {
            'directa': {'objetivo': 'FCL(t+1)', 'prediccion': 'ŷ'},
            'persistencia': {'objetivo': 'FCL(t+1) − base(t)', 'prediccion': 'base(t) + cambio predicho'},
            'relativa': {'objetivo': 'FCL(t+1) / ActivoTotal(t)', 'prediccion': 'ratio predicho × ActivoTotal(t)', 'requisito': 'ActivoTotal(t) > 0 en todas las filas (verificado; sin restricción de filas)',
                         'advertencia': 'compatibilidad de unidades entre ActivoTotal (SMV InfoFinanciera) y FCO/CAPEX (FlujoEfectivo, extracción no reproducible) no acreditada: '
                                        'resultado no validado económicamente'}},
        'base_t': 'FCL(t) válido = FCL_preliminar(t) si CAPEX_reportado(t) <= 0 (src/ablacion_variables.fcl_t); si falta, media de FCL(t+1) en el entrenamiento correspondiente '
                  '(externo o interno), aplicada igual al construir el objetivo y al reconstruir; con cambio predicho 0 coincide con la referencia de persistencia',
        'prohibido': 'FCL(t+1) como predictor; ActivoTotal(t+1) para reconstruir',
        'variantes': {v: vi.variantes()[v] for v in VARIANTES},
        'modelos': {'ridge': 'Pipeline mediana + StandardScaler + Ridge', 'boosting': 'HistGradientBoosting pérdida cuadrática', 'boosting_abs': 'HistGradientBoosting pérdida absoluta (contraste robusto)'},
        'rejillas': rejillas(), 'fijos_boosting': cm.HGB_FIJOS,
        'presupuesto': '8 configuraciones por modelo, mismos pliegues para todas las formulaciones y variantes',
        'validacion': 'anidada: años externos 2017–2021; 3 años internos expansivos, >= 8 años de historia',
        'seleccion_interna': 'promedio simple del RMSE monetario de las predicciones reconstruidas en los años internos (también para pérdida absoluta); empate: configuración más simple',
        'referencias': 'media histórica y persistencia de FCL(t) con respaldo de media (Sprint 08)',
        'comparaciones': [dict(candidato=a, comparador=b, pregunta=q) for a, b, q in comparaciones_previstas()],
        'sensibilidad_concentracion': 'descriptiva, predefinida: repetir las comparaciones excluyendo de la evaluación (sin reajustar) la empresa con mayor error cuadrático de la persistencia en cada moneda',
        'regla': vi.protocolo()['regla'],
        'evaluacion': 'valores reales sin recortar; mismas filas para todos los procedimientos de una moneda',
    }


def escribir_protocolo(out=None):
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'protocolo.json').write_text(json.dumps(protocolo(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _tarea(t, moneda, y, formulaciones=FORMULACIONES, modelos=MODELOS, variantes=VARIANTES):
    pasado, externo = t.loc[t.anio_objetivo.lt(y)], t.loc[t.anio_objetivo.eq(y)]
    assert len(externo) and pasado.anio_objetivo.max() < y
    preds, busq = [], []
    for g in ab.referencias_simples(pasado, externo, moneda, vi.IDENT):
        preds.append(g.drop(columns=['alpha', 'n_atributos']).assign(formulacion='referencia', modelo='referencia', variante=g.procedimiento.iloc[0], configuracion=''))
    vs = vi.variantes()
    for f in formulaciones:
        for m in modelos:
            for v in variantes:
                cfg, filas = buscar(f, m, pasado, vs[v], dict(moneda=moneda, anio_externo=int(y), variante=v))
                busq += filas
                p, z, b = ajustar_predecir(f, m, vs[v], cfg, pasado, externo)
                preds.append(externo[vi.IDENT].assign(procedimiento=procedimiento(f, m, v), moneda=moneda, y_real=externo.objetivo_fcl_t1.to_numpy(), y_predicho=p,
                                                      usa_respaldo_media=ab.fcl_t(externo).isna().to_numpy() & (f == 'persistencia'), formulacion=f, modelo=m, variante=v,
                                                      configuracion=json.dumps(cfg), prediccion_objetivo_transformado=z, base_t=base_t(externo, b).to_numpy(),
                                                      activo_t=externo.ActivoTotal.to_numpy(), respaldo_media_entrenamiento=b))
    return preds, busq


def ejecutar(entrenamiento, clas, anios_externos=vi.ANIOS_EXTERNOS, n_jobs=-1, **kw):
    assert entrenamiento.particion.eq('entrenamiento').all() and entrenamiento.anio_objetivo.le(ab.ANIO_OBJETIVO_MAX_TRAIN).all()
    datos = entrenamiento.loc[clas.loc[entrenamiento.index, POBLACION].astype(bool)]
    tareas = [(datos.loc[datos.Moneda.eq(m)], m, y) for m in sorted(datos.Moneda.unique()) for y in anios_externos]
    res = Parallel(n_jobs=n_jobs)(delayed(_tarea)(t, m, y, **kw) for t, m, y in tareas)
    pred = pd.concat([p for r in res for p in r[0]], ignore_index=True)
    pred['usa_respaldo_media'] = pred.usa_respaldo_media.astype(bool)
    return pred, pd.DataFrame([b for r in res for b in r[1]])


def auditoria_unidades(panel, clas):
    """Casos extremos y evidencia de unidades; solo describe: no corrige valores."""
    filas = []
    ident = (panel.ActivoTotal - panel.PasivoTotal - panel.PatrimonioTotal).abs()
    t = ab.separar_entrenamiento(panel)
    t = t.loc[clas.loc[t.index, POBLACION]]
    r, fa = t.objetivo_fcl_t1 / t.ActivoTotal, t.FCO / t.ActivoTotal
    saltos = pd.read_csv(ROOT / 'reports/sprint_08/saltos_escala_train.csv', dtype={'RPJ': 'string'})
    saltos = saltos.loc[saltos.RPJ.isin(set(t.RPJ))]
    for i in t.index[(r.abs() > 1) | (fa.abs() > 1)]:
        x = t.loc[i]
        nombre = str(x.NombreEmpresa).upper()
        pico = saltos.loc[saltos.RPJ.eq(x.RPJ) & saltos.patron_pico.astype(bool)]
        if len(pico) and x.RPJ == 'CD0009':
            estado = 'sospecha de escala: ActivoTotal 2016 ×1111 con reversión en 2017; identidad contable consistente; no acreditado'
        elif x.ActivoTotal < 100:
            estado = 'sospecha: activo casi nulo (identidad contable consistente); posible empresa sin operaciones o escala; no acreditado'
        elif any(k in nombre for k in ('ABSORBIDA', 'LIQUIDACION', 'LIQUIDACIÓN', 'FUSION', 'FUSIÓN')):
            estado = 'posible evento corporativo indicado en la razón social; no verificado documentalmente'
        else:
            estado = 'no resuelto: ratio extremo sin evidencia de error ni de evento'
        filas.append(dict(tipo='ratio extremo', RPJ=x.RPJ, NombreEmpresa=x.NombreEmpresa, Ejercicio=int(x.Ejercicio), Moneda=x.Moneda, ActivoTotal_t=x.ActivoTotal,
                          FCO_t=x.FCO, objetivo_t1=x.objetivo_fcl_t1, ratio_objetivo_activo=r.loc[i], ratio_fco_activo=fa.loc[i], estado=estado, decision='sin corrección'))
    for x in saltos.itertuples():
        filas.append(dict(tipo='salto de magnitud (Sprint 08)', RPJ=x.RPJ, NombreEmpresa=x.NombreEmpresa, Ejercicio=int(x.Ejercicio), Moneda=x.moneda,
                          ActivoTotal_t=np.nan, FCO_t=np.nan, objetivo_t1=np.nan, ratio_objetivo_activo=np.nan, ratio_fco_activo=np.nan,
                          estado=('sospecha de escala (pico con reversión)' if x.patron_pico else 'salto sin reversión: evento o escala, no resuelto') + f' en {x.columna} ×{x.factor:.3g}',
                          decision='sin corrección'))
    previo = pd.read_csv(ROOT / 'reports/sprint_09/alineacion_investigacion/predicciones.csv', dtype={'RPJ': 'string'})
    previo = previo.loc[previo.procedimiento.eq(f'{POBLACION}|persistencia')]
    sse = ((previo.y_predicho - previo.y_real) ** 2).groupby([previo.moneda, previo.RPJ]).sum()
    for m in sse.index.get_level_values(0).unique():
        s = sse.loc[m].sort_values(ascending=False)
        for rpj in s.index[:3]:
            serie = panel.loc[panel.RPJ.eq(rpj)].sort_values('Ejercicio')
            salto = saltos.RPJ.eq(rpj).any()
            filas.append(dict(tipo='empresa con mayor error (persistencia, alineación)', RPJ=rpj, NombreEmpresa=serie.NombreEmpresa.iloc[-1], Ejercicio=np.nan, Moneda=m,
                              ActivoTotal_t=serie.ActivoTotal.median(), FCO_t=serie.FCO.median(), objetivo_t1=np.nan, ratio_objetivo_activo=np.nan, ratio_fco_activo=np.nan,
                              estado=(f'proporción del error cuadrático: {s.loc[rpj] / s.sum():.1%}; ' + ('con saltos de magnitud registrados' if salto else
                                      'serie de activo sin saltos ≥100×: volatilidad económica plausible (sector ' + str(serie.TipoSector.iloc[0]) + '); no verificado documentalmente')),
                              decision='sin corrección; no se excluye por su error predictivo'))
    resumen = dict(filas_panel=len(panel), violaciones_identidad_activo_pasivo_patrimonio=int((ident > 1).sum()),
                   ratio_objetivo_activo_cuantiles=t.objetivo_fcl_t1.div(t.ActivoTotal).quantile([.01, .05, .5, .95, .99]).round(4).to_dict(),
                   filas_ratio_mayor_1=int((r.abs() > 1).sum()), filas_fco_activo_mayor_1=int((fa.abs() > 1).sum()),
                   campo_unidad_en_xml_smv=False, errores_acreditados=0, version_derivada=False)
    return pd.DataFrame(filas), resumen


def verificar_reproduccion(pred):
    """La formulación directa con Ridge y boosting cuadrático reproduce la alineación (mismos datos y protocolo)."""
    prev = pd.read_csv(ROOT / 'reports/sprint_09/alineacion_investigacion/predicciones.csv', dtype={'RPJ': 'string'}, float_precision='round_trip')
    out = {}
    pares = [(r, f'{POBLACION}|{r}') for r in vi.REFERENCIAS] + [(procedimiento('directa', m, v), f'{POBLACION}|{m}:{v}') for m in ('ridge', 'boosting') for v in VARIANTES]
    for nuevo, viejo in pares:
        a = pred.loc[pred.procedimiento.eq(nuevo)].set_index(['moneda', 'id_fila']).sort_index()
        b = prev.loc[prev.procedimiento.eq(viejo)].set_index(['moneda', 'id_fila']).sort_index()
        assert a.index.equals(b.index), nuevo
        out[nuevo] = float(np.max(np.abs(a.y_predicho.to_numpy() - b.y_predicho.to_numpy()) / np.maximum(np.abs(b.y_predicho.to_numpy()), 1)))
    return out


def sin_empresa_dominante(pred, anual_fn=vi.metricas_anuales):
    p = pred.loc[pred.procedimiento.eq('persistencia')]
    sse = ((p.y_predicho - p.y_real) ** 2).groupby([p.moneda, p.RPJ]).sum()
    excl = {m: sse.loc[m].idxmax() for m in sse.index.get_level_values(0).unique()}
    q = pred.loc[[r != excl[m] for m, r in zip(pred.moneda, pred.RPJ)]]
    anual = anual_fn(q)
    _, comp = vi.comparar(anual, q, comparaciones_previstas())
    return excl, comp


def graficos(proc, anual, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tinta, tinta2, fondo = '#0b0b0b', '#52514e', '#fcfcfb'
    col = {'directa': '#2a78d6', 'persistencia': '#eb6834', 'relativa': '#1baf7a'}
    (out / 'graficos').mkdir(parents=True, exist_ok=True)
    fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:,.0f}')
    rutas = []
    for mo in sorted(proc.moneda.unique()):
        r = proc.loc[proc.moneda.eq(mo)].set_index('procedimiento')
        fig, axs = plt.subplots(1, 3, figsize=(14, 4.6), sharey=True)
        for ax, m in zip(axs, MODELOS):
            x = np.arange(len(VARIANTES))
            tope = 1.5 * r.loc['media_historica', 'RMSE_anual_medio']  # solo visual: las barras mayores se anotan con su valor real
            for k, f in enumerate(FORMULACIONES):
                vals = np.array([r.loc[procedimiento(f, m, v), 'RMSE_anual_medio'] for v in VARIANTES])
                ax.bar(x + (k - 1) * .27, np.minimum(vals, tope), width=.25, color=col[f], label=f, edgecolor=fondo, linewidth=1.5)
                for xi, val in zip(x + (k - 1) * .27, vals):
                    if val > tope:
                        ax.text(xi, tope, f'{val / 1e6:.1f} M', ha='center', va='bottom', fontsize=7, color=tinta, rotation=90)
            for ref, ls in [('media_historica', ':'), ('persistencia', '--')]:
                ax.axhline(r.loc[ref, 'RMSE_anual_medio'], color=tinta2, ls=ls, lw=1.2)
            ax.text(-.6, r.loc['persistencia', 'RMSE_anual_medio'], 'persistencia', va='bottom', fontsize=7, color=tinta2)
            ax.text(-.6, r.loc['media_historica', 'RMSE_anual_medio'], 'media histórica', va='bottom', fontsize=7, color=tinta2)
            ax.set_xticks(x, VARIANTES)
            ax.set_title({'ridge': 'Ridge', 'boosting': 'Boosting (cuadrática)', 'boosting_abs': 'Boosting (absoluta)'}[m], color=tinta, loc='left', fontsize=10)
            ax.yaxis.set_major_formatter(fmt)
            for s in ['top', 'right']:
                ax.spines[s].set_visible(False)
        axs[0].set_ylabel('RMSE anual medio (unidad reportada)')
        axs[0].legend(title='formulación', frameon=False, fontsize=8, title_fontsize=8)
        lo = r.RMSE_anual_medio.min() * .8
        axs[0].set_ylim(lo, min(r.RMSE_anual_medio.max(), 1.5 * r.loc['media_historica', 'RMSE_anual_medio']) * 1.12)
        fig.suptitle(f'{ab._nombre(mo)}, no financiera: RMSE anual medio por formulación, modelo y variante (eje no parte de cero; barras truncadas anotadas)', x=.02, ha='left', color=tinta)
        fig.tight_layout()
        ruta = out / 'graficos' / f'formulaciones_{ab._slug(mo)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
        fig, ax = plt.subplots(figsize=(9, 4.4))
        for f in FORMULACIONES:
            g = anual.loc[anual.moneda.eq(mo) & anual.procedimiento.eq(procedimiento(f, 'boosting', 'E0'))].sort_values('anio_externo')
            ax.plot(g.anio_externo, g.RMSE, marker='o', lw=2, ms=7, color=col[f], mec=fondo, mew=1.5, label=f'boosting E0, {f}')
        for ref, ls, c in [('persistencia', '--', '#6250d6'), ('media_historica', ':', '#8a8984')]:
            g = anual.loc[anual.moneda.eq(mo) & anual.procedimiento.eq(ref)].sort_values('anio_externo')
            ax.plot(g.anio_externo, g.RMSE, ls=ls, lw=2, color=c, marker='^', ms=6, label=ref.replace('_', ' '))
        ax.set_xticks(list(vi.ANIOS_EXTERNOS))
        ax.yaxis.set_major_formatter(fmt)
        ax.set_ylabel('RMSE (unidad reportada)')
        ax.set_title(f'{ab._nombre(mo)}: RMSE por año externo', color=tinta, loc='left')
        ax.legend(frameon=False, fontsize=8)
        for s in ['top', 'right']:
            ax.spines[s].set_visible(False)
        fig.tight_layout()
        ruta = out / 'graficos' / f'rmse_por_anio_{ab._slug(mo)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
    return rutas


def run(out=None, n_jobs=-1):
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(protocolo(), ensure_ascii=False, indent=2) + '\n'
    if out.resolve() == OUT.resolve():
        assert (out / 'protocolo.json').exists() and (out / 'protocolo.json').read_text(encoding='utf-8') == texto, 'protocolo.json ausente o distinto del código'
    (out / 'protocolo.json').write_text(texto, encoding='utf-8')
    panel, _, _ = ac.load_inputs()
    clas = ai.clasificar_poblacion(panel)
    casos, res_unid = auditoria_unidades(panel, clas)
    entrenamiento = ab.separar_entrenamiento(panel)
    del panel
    pred, busq = ejecutar(entrenamiento, clas, n_jobs=n_jobs)
    anual = vi.metricas_anuales(pred)
    proc = anual.groupby(['moneda', 'procedimiento'], as_index=False).agg(anios=('anio_externo', 'size'), n=('n', 'sum'), RMSE_anual_medio=('RMSE', 'mean'), MAE_anual_medio=('MAE', 'mean'))
    comp_anio, comp = vi.comparar(anual, pred, comparaciones_previstas())
    excl, comp_sin = sin_empresa_dominante(pred)
    verif = verificar_reproduccion(pred)
    rutas = graficos(proc, anual, out)
    entorno = {'python': platform.python_version(), 'scikit-learn': sklearn.__version__, 'numpy': np.__version__, 'pandas': pd.__version__}
    try:
        entorno['git_head'] = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        entorno['git_head'] = None
    seleccion = busq.loc[busq.elegida, ['moneda', 'anio_externo', 'formulacion', 'modelo', 'variante', 'configuracion', 'rmse_interno_medio']]
    salidas = {'auditoria_unidades_casos.csv': casos, 'busquedas_internas.csv': busq, 'configuraciones_seleccionadas.csv': seleccion, 'predicciones.csv': pred,
               'metricas_por_anio.csv': anual, 'resumen_procedimientos.csv': proc, 'comparaciones_por_anio.csv': comp_anio, 'resumen_comparaciones.csv': comp,
               'resumen_comparaciones_sin_empresa_dominante.csv': comp_sin.assign(empresa_excluida=comp_sin.moneda.map(excl)), 'concentracion_error.csv': cm.concentracion(pred)}
    for nombre, t in salidas.items():
        t.to_csv(out / nombre, index=False, float_format='%.15g')
    for nombre, obj in [('entorno.json', entorno), ('verificacion_reproduccion.json', verif), ('auditoria_unidades_resumen.json', res_unid)]:
        (out / nombre).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=float) + '\n', encoding='utf-8')
    return dict(salidas, verificacion=verif, graficos=rutas)
