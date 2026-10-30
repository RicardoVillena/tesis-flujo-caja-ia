"""Sprint 09 — Alineación con el plan de investigación: población no financiera y tamaño empresarial.

Experimento acotado y exploratorio (años externos 2017–2021 ya examinados; prueba 2022–2025 no se usa):
  línea 1: E0–E3 sobre empresas no financieras (regla SMV explícita); sensibilidad con población conservadora;
  línea 2: tamaño (ln activo total) añadido a E0 y E2; apalancamiento ya está en E0 (pasivo_activo);
           reservas de efectivo no existen en los datos (pendiente, no se sustituyen por FCO);
  línea 3: interacciones tamaño × externos NO se implementan (justificación insuficiente; ver protocolo).
Reutiliza la validación anidada, rejillas y criterio del Sprint 08/09. El protocolo se escribe antes de ejecutar.
"""
from pathlib import Path
import json
import platform
import subprocess
import numpy as np
import pandas as pd
import sklearn
import src.ablacion_variables as ab
import src.auditoria_calidad as ac
import src.comparacion_modelos as cm
import src.variantes_importancia as vi

ROOT = ab.ROOT
OUT = ROOT / 'reports/sprint_09/alineacion_investigacion'
CATALOGO_S07 = ROOT / 'reports/sprint_07/fase_3/catalogo_empresa_anio.csv'
SECTORES_FINANCIEROS = ('BANCOS', 'SEGUROS', 'FINANCIERAS', 'A.F.P.')
DIVISIONES_CIIU_DUDOSAS = ('64', '65', '66', '67')
TAMANO = 'log_activo_total'
MODELOS = vi.MODELOS
POBLACIONES = ('no_financiera', 'conservadora')


def clasificar_poblacion(panel):
    """Clasificación por fila; no elimina filas del panel. Devuelve columnas de población y motivo."""
    c = pd.read_csv(CATALOGO_S07, dtype=str)[['RPJ', 'Ejercicio', 'ciiu_normalizado', 'industria_damodaran']]
    c['Ejercicio'] = c.Ejercicio.astype(int)
    t = panel[['RPJ', 'NombreEmpresa', 'Ejercicio', 'Moneda', 'TipoSector', 'particion']].merge(c, on=['RPJ', 'Ejercicio'], how='left', validate='one_to_one')
    t.index = panel.index
    ciiu_emp = t.dropna(subset=['ciiu_normalizado']).groupby('RPJ').ciiu_normalizado.agg(lambda s: ';'.join(sorted(set(s))))
    t['ciiu_empresa'] = t.RPJ.map(ciiu_emp)
    financiera_smv = t.TipoSector.isin(SECTORES_FINANCIEROS)
    dudosa_ciiu = t.TipoSector.eq('DIVERSOS') & t.ciiu_empresa.fillna('').str.split(';').apply(lambda xs: any(x[:2] in DIVISIONES_CIIU_DUDOSAS for x in xs if x))
    sin_actividad = t.TipoSector.eq('DIVERSOS') & t.ciiu_empresa.isna() & t.industria_damodaran.isna()
    t['motivo'] = np.select([financiera_smv, dudosa_ciiu, sin_actividad],
                            ['excluida: TipoSector SMV financiero', 'dudosa: DIVERSOS con CIIU 64–67 (financiero u holding; CIIU no acredita actividad principal)',
                             'dudosa: DIVERSOS sin CIIU ni actividad documentada'], 'incluida: sector SMV no financiero')
    t['no_financiera'] = ~financiera_smv
    t['conservadora'] = ~financiera_smv & ~dudosa_ciiu
    return t


def tablas_poblacion(clas):
    filas = clas.groupby(['Moneda', 'Ejercicio', 'TipoSector', 'motivo', 'particion'], dropna=False).agg(
        observaciones=('RPJ', 'size'), empresas=('RPJ', 'nunique')).reset_index()
    resumen = clas.groupby(['Moneda', 'motivo']).agg(observaciones=('RPJ', 'size'), empresas=('RPJ', 'nunique')).reset_index()
    dud = clas.loc[clas.motivo.str.startswith('dudosa')].groupby(['RPJ', 'motivo']).agg(
        NombreEmpresa=('NombreEmpresa', 'last'), TipoSector=('TipoSector', 'first'), ciiu_empresa=('ciiu_empresa', 'first'),
        monedas=('Moneda', lambda s: ';'.join(sorted(set(s)))), ejercicios=('Ejercicio', lambda s: f'{s.min()}-{s.max()}'),
        observaciones=('Ejercicio', 'size'), observaciones_entrenamiento=('particion', lambda s: int(s.eq('entrenamiento').sum()))).reset_index()
    return filas, resumen, dud


def anadir_tamano(t):
    """ln(ActivoTotal) del ejercicio t: transformación determinista por fila (no aprende de los datos)."""
    t = t.copy()
    t[TAMANO] = np.log(t.ActivoTotal.where(t.ActivoTotal > 0))
    return t


def variantes():
    v = vi.variantes()
    return {**v, 'E0T': v['E0'] + [TAMANO], 'E2T': v['E2'] + [TAMANO]}


EXPERIMENTOS = {'no_financiera': ('E0', 'E1', 'E2', 'E3', 'E0T', 'E2T'), 'conservadora': ('E0', 'E1', 'E2', 'E3')}


def comparaciones_previstas():
    pares = []
    for pob, vs in EXPERIMENTOS.items():
        p = lambda x: f'{pob}|{x}'
        for m in MODELOS:
            pares += [(p(f'{m}:E1'), p(f'{m}:E0'), f'{pob}: aporte macroeconómico'), (p(f'{m}:E3'), p(f'{m}:E0'), f'{pob}: aporte bursátil'),
                      (p(f'{m}:E2'), p(f'{m}:E1'), f'{pob}: aporte bursátil sobre macro'), (p(f'{m}:E2'), p(f'{m}:E0'), f'{pob}: aporte externo conjunto')]
            if 'E0T' in vs:
                pares += [(p(f'{m}:E0T'), p(f'{m}:E0'), f'{pob}: aporte del tamaño sobre financieros'),
                          (p(f'{m}:E2T'), p(f'{m}:E2'), f'{pob}: aporte del tamaño sobre E2'),
                          (p(f'{m}:E2T'), p(f'{m}:E0T'), f'{pob}: aporte externo con tamaño')]
            for v in vs:
                pares += [(p(f'{m}:{v}'), p(r), f'{pob}: frente a referencia simple') for r in vi.REFERENCIAS]
        for v in vs:
            pares.append((p(f'boosting:{v}'), p(f'ridge:{v}'), f'{pob}: algoritmo (misma variante)'))
    return pares


def protocolo():
    vs = variantes()
    return {
        'version': 'Sprint 09 — alineación con el plan de investigación; protocolo fijado antes de ejecutar',
        'caracter': 'EXPLORATORIO: años externos 2017–2021 ya examinados (Sprints 08 y 09); prueba 2022–2025 no se usa; el cambio de población no se presenta como mejora confirmada.',
        'poblacion': {
            'fuente_plan': 'El plan de tesis excluye empresas del sector financiero y bancario.',
            'regla_principal': f'no_financiera: excluir filas con TipoSector SMV en {list(SECTORES_FINANCIEROS)}; ninguna empresa cambia de TipoSector en el panel',
            'por_que_no_solo_bancos': 'BANCOS es una de cuatro categorías financieras SMV; SEGUROS, FINANCIERAS y A.F.P. también se excluyen',
            'dudosas': f'DIVERSOS con CIIU (2023–2025) en divisiones {list(DIVISIONES_CIIU_DUDOSAS)} o sin CIIU ni actividad documentada: se listan y se conservan en la población principal; '
                       'el CIIU mezcla revisiones y asigna 6719/6599/6420 a holdings no financieros (p. ej. AENZA, InRetail, UNACEM Corp), por lo que no acredita actividad principal',
            'sensibilidad': 'conservadora: además excluye las empresas DIVERSOS con CIIU 64–67 (solo línea 1)',
            'filas_originales': 'se conservan las 4.221 filas; los filtros se aplican solo al experimento'},
        'lineas': {
            'linea_1': 'E0, E1, E2 y E3 de Sprint 09 sobre la población no financiera (y conservadora como sensibilidad)',
            'linea_2': f'tamaño = ln(ActivoTotal(t)); E0T = E0 + tamaño, E2T = E2 + tamaño; apalancamiento ya incluido en E0 como pasivo_activo (= LEV de Ali, 2026); '
                       'reservas de efectivo: no hay efectivo y equivalentes en el panel ni en los XML SMV disponibles → no evaluable; no se sustituye por FCO',
            'linea_3': 'NO implementada: Pham (2026) estudia ln(precio) mensual con índices de incertidumbre global (WUI, GPR, ESGUI, WSI) no disponibles en el panel; '
                       'el objetivo (FCL anual) y las variables externas disponibles no reproducen ese diseño; una interacción tamaño × externos sería una búsqueda sin fundamento suficiente'},
        'variantes': vs, 'experimentos': {k: list(v) for k, v in EXPERIMENTOS.items()},
        'modelos': list(MODELOS), 'rejillas': {m: cm.rejillas()[m] for m in MODELOS},
        'validacion': 'anidada del Sprint 08/09: años externos 2017–2021; 3 años internos expansivos con >= 8 años de historia; mismo presupuesto (8 configuraciones) por variante',
        'preparacion': 'Ridge: mediana + StandardScaler dentro del pipeline; boosting: NaN nativos; el tamaño es una transformación determinista por fila; objetivo sin transformar',
        'referencias': 'media histórica y persistencia (definiciones verificadas en Sprint 08), por población',
        'importancia': 'población no financiera, E2T con configuración congelada por pliegue: retirada individual (27 atributos) y por bloques (financiero, tamaño, macroeconómico, bursátil); '
                       'signo: delta_RMSE = RMSE_sin − RMSE_completo (positivo = aporta); externos no se permutan',
        'comparaciones': [dict(candidato=a, comparador=b, pregunta=q) for a, b, q in comparaciones_previstas()],
        'regla': vi.protocolo()['regla'],
        'objetivo': 'FCL preliminar t+1 (FCO + CAPEX reportado), no FCFF validado ni valor intrínseco',
    }


def escribir_protocolo(out=None):
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'protocolo.json').write_text(json.dumps(protocolo(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def ejecutar(entrenamiento, clas, anios_externos=vi.ANIOS_EXTERNOS, modelos=MODELOS, con_importancia=True):
    assert entrenamiento.particion.eq('entrenamiento').all() and entrenamiento.anio_objetivo.le(ab.ANIO_OBJETIVO_MAX_TRAIN).all()
    vs = variantes()
    base = anadir_tamano(entrenamiento)
    preds, busq, imp, impb = [], [], [], []
    bloques = {**vi.bloques(), 'tamano': [TAMANO]}
    for pob, lista in EXPERIMENTOS.items():
        datos = base.loc[clas.loc[base.index, pob].astype(bool)]
        for moneda in sorted(datos.Moneda.unique()):
            t = datos.loc[datos.Moneda.eq(moneda)]
            for y in anios_externos:
                pasado, externo = t.loc[t.anio_objetivo.lt(y)], t.loc[t.anio_objetivo.eq(y)]
                assert len(externo) and pasado.anio_objetivo.max() < y
                for g in ab.referencias_simples(pasado, externo, moneda, vi.IDENT):
                    preds.append(g.drop(columns=['alpha', 'n_atributos']).assign(procedimiento=f'{pob}|{g.procedimiento.iloc[0]}', poblacion=pob, modelo='referencia',
                                                                               variante=g.procedimiento.iloc[0], configuracion=''))
                for modelo in modelos:
                    cfgs, p_e2t = {}, None
                    for v in lista:
                        cols = vs[v]
                        cfg, filas = cm.buscar(modelo, pasado, cols, dict(poblacion=pob, moneda=moneda, anio_externo=int(y), variante=v))
                        busq += filas
                        assert cfg is not None
                        p, _ = vi.ajustar_predecir(modelo, cols, cfg, pasado, externo)
                        cfgs[v] = cfg
                        if v == 'E2T':
                            p_e2t = p
                        preds.append(externo[vi.IDENT].assign(procedimiento=f'{pob}|{modelo}:{v}', moneda=moneda, y_real=externo.objetivo_fcl_t1.to_numpy(), y_predicho=p,
                                                              usa_respaldo_media=False, poblacion=pob, modelo=modelo, variante=v, configuracion=json.dumps(cfg)))
                    if not con_importancia or p_e2t is None:
                        continue
                    y_real = externo.objetivo_fcl_t1.to_numpy()
                    rb, mb = float(np.sqrt(np.mean((p_e2t - y_real) ** 2))), float(np.mean(np.abs(p_e2t - y_real)))
                    for nombre, retirar, destino in [(c, [c], imp) for c in vs['E2T']] + [(k, b, impb) for k, b in bloques.items()]:
                        cols_r = [c for c in vs['E2T'] if c not in retirar]
                        p, _ = vi.ajustar_predecir(modelo, cols_r, cfgs['E2T'], pasado, externo)
                        r, m_ = float(np.sqrt(np.mean((p - y_real) ** 2))), float(np.mean(np.abs(p - y_real)))
                        destino.append(dict(poblacion=pob, moneda=moneda, anio_externo=int(y), modelo=modelo, retirado=nombre, n_retirados=len(retirar),
                                            configuracion_E2T=json.dumps(cfgs['E2T']), RMSE_completo=rb, RMSE_sin=r, delta_RMSE=r - rb,
                                            delta_RMSE_pct=100 * (r - rb) / rb, MAE_completo=mb, MAE_sin=m_, delta_MAE_pct=100 * (m_ - mb) / mb))
                print(f'{pob} {moneda} {y} completado', flush=True)
    pred = pd.concat(preds, ignore_index=True)
    pred['usa_respaldo_media'] = pred.usa_respaldo_media.astype(bool)
    return dict(pred=pred, busq=pd.DataFrame(busq), imp=pd.DataFrame(imp), impb=pd.DataFrame(impb))


def auditoria_variables(entrenamiento):
    t = anadir_tamano(entrenamiento)
    filas = []
    for nombre, formula, fuente, unidad, disp, estado in [
        (TAMANO, 'ln(ActivoTotal(t)); ActivoTotal > 0', 'panel_fcl_preliminar.csv (SMV, ActivoTotal)', 'log de la unidad monetaria reportada; escala no acreditada (un cambio unidades↔miles desplaza ~6,9)',
         'misma condición que los financieros de t: posible fuga por reexpresiones (Sprint 08)', 'construible'),
        ('pasivo_activo', 'PasivoTotal(t)/ActivoTotal(t)', 'panel SMV', 'fracción', 'igual que financieros de t', 'ya incluido en E0 (= LEV de Ali, 2026)'),
        ('efectivo_activo', 'Efectivo y equivalentes(t)/ActivoTotal(t)', 'no existe: el panel y los XML SMV InfoFinanciera solo tienen 5 agregados (activo, pasivo, patrimonio, ingresos, utilidad) más FCO y CAPEX',
         '—', '—', 'NO construible; pendiente de nueva fuente (balance detallado SMV); no se sustituye por FCO'),
        ('FCO/FCL históricos', 'rezagos 1–3, std 3 años previos, cambio sobre activo previo', 'panel SMV', 'unidad monetaria reportada / fracción', 'años <= t-1: no verificada (Sprint 08)', 'ya incluidos en E0')]:
        if nombre in t.columns:
            for m, g in t.groupby('Moneda'):
                s = g[nombre]
                filas.append(dict(atributo=nombre, moneda=m, formula=formula, fuente=fuente, unidad=unidad, disponibilidad_temporal=disp, estado=estado,
                                  n=len(s), faltantes=int(s.isna().sum()), minimo=s.min(), mediana=s.median(), maximo=s.max()))
        else:
            filas.append(dict(atributo=nombre, moneda='ambas', formula=formula, fuente=fuente, unidad=unidad, disponibilidad_temporal=disp, estado=estado,
                              n=len(t), faltantes=np.nan, minimo=np.nan, mediana=np.nan, maximo=np.nan))
    return pd.DataFrame(filas)


def verificar_reproduccion(pred):
    """Dólares: la población no financiera coincide con la completa → debe reproducir exactamente el Sprint 09."""
    s9 = pd.read_csv(vi.OUT / 'predicciones.csv', dtype={'RPJ': 'string'}, float_precision='round_trip')
    out = {}
    for proc in ['media_historica', 'persistencia'] + [f'{m}:{v}' for m in MODELOS for v in ['E0', 'E1', 'E2', 'E3']]:
        a = pred.loc[pred.procedimiento.eq(f'no_financiera|{proc}') & pred.moneda.eq('D lares')].set_index('id_fila').sort_index()
        b = s9.loc[s9.procedimiento.eq(proc) & s9.moneda.eq('D lares')].set_index('id_fila').sort_index()
        assert a.index.equals(b.index)
        np.testing.assert_allclose(a.y_predicho, b.y_predicho, rtol=1e-9, atol=1e-6)
        out[f'D lares|{proc}'] = float(np.max(np.abs(a.y_predicho.to_numpy() - b.y_predicho.to_numpy()) / np.maximum(np.abs(b.y_predicho.to_numpy()), 1)))
    return out


def graficos(proc, imp_res, impb, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tinta, tinta2, fondo = '#0b0b0b', '#52514e', '#fcfcfb'
    col = {'ridge': '#2a78d6', 'boosting': '#1baf7a'}
    cb = {'financiero': '#2a78d6', 'macroeconomico': '#eb6834', 'bursatil': '#1baf7a', 'tamano': '#6250d6'}
    (out / 'graficos').mkdir(parents=True, exist_ok=True)
    fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:,.0f}')
    rutas = []
    for m in sorted(proc.moneda.unique()):
        r = proc.loc[proc.moneda.eq(m) & proc.procedimiento.str.startswith('no_financiera|')].assign(p=lambda x: x.procedimiento.str.split('|').str[1]).set_index('p')
        vv = list(EXPERIMENTOS['no_financiera'])
        fig, ax = plt.subplots(figsize=(10, 4.6))
        x = np.arange(len(vv))
        for k, mo in enumerate(MODELOS):
            ax.bar(x + (k - .5) * .38, [r.loc[f'{mo}:{v}', 'RMSE_anual_medio'] for v in vv], width=.36, color=col[mo], edgecolor=fondo, linewidth=2,
                   label='Ridge' if mo == 'ridge' else 'HistGradientBoosting')
        for ref, ls in [('media_historica', ':'), ('persistencia', '--')]:
            ax.axhline(r.loc[ref, 'RMSE_anual_medio'], color=tinta2, ls=ls, lw=1.2)
            ax.text(-.55, r.loc[ref, 'RMSE_anual_medio'], 'media histórica' if ref == 'media_historica' else 'persistencia', va='bottom', fontsize=8, color=tinta2)
        ax.set_xticks(x, vv)
        ax.set_ylim(min(r.RMSE_anual_medio) * .85, max(r.RMSE_anual_medio) * 1.05)
        ax.yaxis.set_major_formatter(fmt)
        ax.set_ylabel('RMSE anual medio (unidad reportada)')
        ax.set_title(f'{ab._nombre(m)}, población no financiera: RMSE anual medio (eje no parte de cero)', color=tinta, loc='left')
        ax.legend(frameon=False, fontsize=8, loc='upper right')
        for s in ['top', 'right']:
            ax.spines[s].set_visible(False)
        fig.tight_layout()
        ruta = out / 'graficos' / f'variantes_no_financiera_{ab._slug(m)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
        fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
        for ax, mo in zip(axs, MODELOS):
            g = impb.loc[impb.moneda.eq(m) & impb.modelo.eq(mo)]
            for bl, gg in g.groupby('retirado'):
                gg = gg.sort_values('anio_externo')
                ax.plot(gg.anio_externo, gg.delta_RMSE_pct, marker='o', ms=7, lw=2, color=cb[bl], mec=fondo, mew=1.5, label=bl)
            ax.axhline(0, color=tinta2, lw=1)
            ax.set_xticks(list(vi.ANIOS_EXTERNOS))
            ax.set_title(f'{"Ridge" if mo == "ridge" else "Boosting"}: Δ RMSE % al retirar el bloque de E2T', color=tinta, loc='left', fontsize=10)
            ax.legend(frameon=False, fontsize=8)
            for s in ['top', 'right']:
                ax.spines[s].set_visible(False)
        fig.suptitle(f'{ab._nombre(m)}, no financiera: importancia por bloques (positivo = el bloque aporta)', x=.02, ha='left', color=tinta)
        fig.tight_layout()
        ruta = out / 'graficos' / f'importancia_bloques_{ab._slug(m)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        for ax, mo in zip(axs, MODELOS):
            g = imp_res.loc[imp_res.moneda.eq(m) & imp_res.modelo.eq(mo)].sort_values('delta_RMSE_pct_medio', ascending=False)
            g = pd.concat([g.head(8), g.tail(4)]).drop_duplicates('retirado').iloc[::-1]
            ax.barh(range(len(g)), g.delta_RMSE_pct_medio, color=['#2a78d6' if v > 0 else '#e34948' for v in g.delta_RMSE_pct_medio], height=.6, edgecolor=fondo, linewidth=2)
            ax.set_yticks(range(len(g)), [f'{a}  ({p}/5)' for a, p in zip(g.retirado, g.anios_aporta)], fontsize=8)
            ax.axvline(0, color=tinta2, lw=1)
            ax.set_xlabel('Δ RMSE % (positivo = aporta); (k/5) años con aporte', fontsize=8)
            ax.set_title(f'{"Ridge" if mo == "ridge" else "Boosting"}: retirada individual en E2T', color=tinta, loc='left', fontsize=10)
            for s in ['top', 'right']:
                ax.spines[s].set_visible(False)
        fig.suptitle(f'{ab._nombre(m)}, no financiera: importancia individual (8 mayores y 4 menores)', x=.02, ha='left', color=tinta)
        fig.tight_layout()
        ruta = out / 'graficos' / f'importancia_individual_{ab._slug(m)}.png'
        fig.savefig(ruta, dpi=150, facecolor=fondo)
        plt.close(fig)
        rutas.append(ruta)
    return rutas


def run(out=None):
    out = Path(out or OUT)
    out.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(protocolo(), ensure_ascii=False, indent=2) + '\n'
    if out.resolve() == OUT.resolve():
        assert (out / 'protocolo.json').exists() and (out / 'protocolo.json').read_text(encoding='utf-8') == texto, 'protocolo.json ausente o distinto del código'
    (out / 'protocolo.json').write_text(texto, encoding='utf-8')
    panel, _, _ = ac.load_inputs()
    clas = clasificar_poblacion(panel)
    assert len(clas) == 4221
    pob_filas, pob_res, dudosas = tablas_poblacion(clas)
    entrenamiento = ab.separar_entrenamiento(panel)
    del panel
    r = ejecutar(entrenamiento, clas)
    pred = r['pred']
    anual = vi.metricas_anuales(pred)
    proc = anual.groupby(['moneda', 'procedimiento'], as_index=False).agg(anios=('anio_externo', 'size'), n=('n', 'sum'), RMSE_anual_medio=('RMSE', 'mean'), MAE_anual_medio=('MAE', 'mean'))
    comp_anio, comp = vi.comparar(anual, pred, comparaciones_previstas())
    imp_res, impb_res = vi.resumen_importancia(r['imp'], 'retirado'), vi.resumen_importancia(r['impb'], 'retirado')
    verif = verificar_reproduccion(pred)
    rutas = graficos(proc, imp_res, r['impb'], out)
    entorno = {'python': platform.python_version(), 'scikit-learn': sklearn.__version__, 'numpy': np.__version__, 'pandas': pd.__version__}
    try:
        entorno['git_head'] = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        entorno['git_head'] = None
    salidas = {'poblacion_por_anio_sector_moneda.csv': pob_filas, 'poblacion_resumen.csv': pob_res, 'clasificaciones_dudosas.csv': dudosas,
               'clasificacion_filas.csv': clas.reset_index().rename(columns={'index': 'id_fila'}),
               'auditoria_variables.csv': auditoria_variables(entrenamiento), 'busquedas_internas.csv': r['busq'], 'predicciones.csv': pred,
               'metricas_por_anio.csv': anual, 'resumen_procedimientos.csv': proc, 'comparaciones_por_anio.csv': comp_anio, 'resumen_comparaciones.csv': comp,
               'importancia_individual_por_anio.csv': r['imp'], 'importancia_individual.csv': imp_res, 'importancia_bloques_por_anio.csv': r['impb'],
               'importancia_bloques.csv': impb_res, 'concentracion_error.csv': cm.concentracion(pred)}
    for nombre, t in salidas.items():
        t.to_csv(out / nombre, index=False, float_format='%.15g')
    (out / 'entorno.json').write_text(json.dumps(entorno, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (out / 'verificacion_reproduccion.json').write_text(json.dumps(verif, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return dict(salidas, verificacion=verif, graficos=rutas)
