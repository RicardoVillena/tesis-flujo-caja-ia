"""Sprint 07: auditoría descriptiva, sin entrenamiento ni edición de fuentes."""
from pathlib import Path
import hashlib
from html.parser import HTMLParser
import json
import re
import numpy as np
import pandas as pd

PANEL = 'data/processed/panel_financiero_macro_bursatil.csv'
MACRO = {
    'BANCOS': 'Financiero', 'SEGUROS': 'Financiero', 'FINANCIERAS': 'Financiero',
    'A.F.P.': 'Financiero', 'AGRICOLAS': 'Agroindustrial',
    'MINERAS': 'Extractivo', 'INDUSTRIALES': 'Industrial',
    'SERVICIOS PUBLICOS': 'Servicios públicos',
    'DIVERSOS': 'Pendiente', 'INDUSTRIALES DEL TRABAJO': 'Pendiente',
}
PENDIENTE = 'Pendiente de revisión'



def extract_official_names(html):
    """Extrae nombres del HTML congelado sin dependencias de scraping."""
    class TableParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.rows, self.row, self.cell = [], None, None

        def handle_starttag(self, tag, attrs):
            if tag == 'tr':
                self.row = []
            if tag in ('td', 'th'):
                self.cell = ''

        def handle_data(self, data):
            if self.cell is not None:
                self.cell += data

        def handle_endtag(self, tag):
            if tag in ('td', 'th') and self.cell is not None:
                if self.row is not None:
                    self.row.append(' '.join(self.cell.split()))
                self.cell = None
            if tag == 'tr' and self.row:
                self.rows.append(self.row)
                self.row = None
    parser = TableParser()
    parser.feed(html)
    return [row[0] for row in parser.rows if len(row) == 11 and row[0]
            and row[0] != 'Industry Name' and not row[0].startswith('Total Market')]


def read_panel(root):
    return pd.read_csv(Path(root) / PANEL, dtype={'RPJ': 'string', 'RUC': 'string',
                       'CIIU': 'string'}, float_precision='round_trip')


def normalize_ciiu(value):
    """Normalización auxiliar sin alterar el CIIU original ni adivinar revisión."""
    if pd.isna(value) or not str(value).strip():
        return pd.NA
    value = str(value).strip()
    if not re.fullmatch(r'\d{1,4}(?:\.0+)?', value):
        return pd.NA
    return value.split('.')[0].zfill(4)


def classify(panel, official):
    """Asignaciones contemporáneas; no propaga información 2024 hacia 2005."""
    if panel[['RPJ', 'Ejercicio']].isna().any().any():
        raise ValueError('Claves ausentes')
    if panel.duplicated(['RPJ', 'Ejercicio']).any():
        raise ValueError('Duplicados empresa-año en origen')
    c = panel[['RPJ', 'RUC', 'NombreEmpresa', 'Ejercicio', 'CIIU', 'TipoSector']].copy()
    c['ciiu_normalizado'] = c.CIIU.map(normalize_ciiu).astype('string')
    c['revision_ciiu'] = 'No declarada en el panel'
    c['macrosector_propuesto'] = c.TipoSector.map(MACRO).fillna('Pendiente')
    c['sector_propuesto'] = c.TipoSector.fillna('Pendiente')
    c['regla_macrosector'] = 'M01: agrupación analítica del TipoSector observado'
    c['industria_damodaran'] = pd.Series(pd.NA, index=c.index, dtype='string')
    c['regla_industria'] = 'P01: CIIU ausente; sector insuficiente'
    c.loc[c.CIIU.notna(), 'regla_industria'] = 'P02: revisión CIIU no declarada o correspondencia no unívoca'
    c['candidatas_revision'] = ''
    c.loc[c.TipoSector.eq('BANCOS'), 'candidatas_revision'] = 'Bank (Money Center) | Banks (Regional)'
    c.loc[c.TipoSector.eq('SEGUROS'), 'candidatas_revision'] = 'Insurance (General) | Insurance (Life) | Insurance (Prop/Cas.) | Reinsurance'
    c.loc[c.TipoSector.eq('MINERAS'), 'candidatas_revision'] = 'Metals & Mining | Precious Metals | Coal & Related Energy'
    c['fuente_regla'] = PANEL + ':TipoSector/CIIU de la misma observación'
    afp = c.TipoSector.eq('A.F.P.')
    c.loc[afp, ['industria_damodaran', 'regla_industria', 'fuente_regla']] = [
        'Investments & Asset Management', 'D01: AFP; administración de fondos previsionales',
        'https://www.sbs.gob.pe/sistema-privado-de-pensiones/temas-de-interes-del-spp/fondo-de-pensiones']
    hotel = c.ciiu_normalizado.eq('5510').fillna(False) & c.TipoSector.eq('DIVERSOS')
    c.loc[hotel, ['industria_damodaran', 'regla_industria', 'fuente_regla']] = [
        'Hotel/Gaming', 'D02: CIIU 5510; alojamiento compatible en revisiones 3.1 y 4',
        'https://unstats.un.org/unsd/classifications/Econ/Structure/Detail/EN/17/5510 | https://unstats.un.org/unsd/classifications/Econ/Structure/Detail/EN/27/5510']
    c.loc[hotel, ['macrosector_propuesto', 'sector_propuesto', 'regla_macrosector']] = [
        'Servicios de consumo', 'Alojamiento', 'M02: actividad CIIU 5510 verificada en revisiones 3.1 y 4']
    # Contradicciones empresariales se conservan, pero no reciben industria automática.
    conflicts = panel.groupby('RPJ').TipoSector.nunique().gt(1)
    c['cambio_sector_posible'] = c.RPJ.map(conflicts)
    ruc_conflicts = panel.groupby('RPJ').RUC.nunique().gt(1)
    c['identificador_inconsistente'] = c.RPJ.map(ruc_conflicts)
    conflict = c.cambio_sector_posible | c.identificador_inconsistente
    c.loc[conflict, 'industria_damodaran'] = pd.NA
    c.loc[conflict, 'regla_industria'] = 'P03: cambio sectorial o RPJ con múltiples RUC; revisar historial'
    c['estado_clasificacion'] = np.where(c.industria_damodaran.notna(), 'Clasificado por regla', 'Pendiente')
    c['version_clasificacion'] = 'Damodaran January 2026 / sprint07-v1'
    c['fecha_consulta'] = '2026-10-23'
    if not set(c.industria_damodaran.dropna()).issubset(set(official)):
        raise ValueError('Industria fuera del vocabulario oficial')
    return c


def join_classification(panel, catalog):
    extra = [x for x in catalog if x not in panel.columns or x in ['RPJ', 'Ejercicio']]
    out = panel.merge(catalog[extra], on=['RPJ', 'Ejercicio'], how='left',
                      validate='one_to_one', sort=False)
    pd.testing.assert_frame_equal(out[panel.columns], panel.reset_index(drop=True), check_exact=True)
    assert len(out) == len(panel) and out.RPJ.nunique() == panel.RPJ.nunique()
    return out


def summary(panel, groups):
    """FCL contemporáneo en unidades reportadas, siempre separado por moneda."""
    rows = []
    for keys, g in panel.groupby(groups, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        f = g.FCL_preliminar.dropna()
        q1, q3 = f.quantile([.25, .75]) if len(f) else (np.nan, np.nan)
        iqr = q3 - q1
        eligible = g.loc[g.utilizable_supervisado]
        rows.append(dict(zip(groups, keys)) | {
            'empresas': g.RPJ.nunique(), 'observaciones': len(g),
            'anio_min': g.Ejercicio.min(), 'anio_max': g.Ejercicio.max(),
            'anios_cubiertos': g.Ejercicio.nunique(),
            'anios': '|'.join(map(str, sorted(g.Ejercicio.unique()))),
            'entrenamiento_elegible': eligible.particion.eq('entrenamiento').sum(),
            'prueba_elegible': eligible.particion.eq('prueba').sum(),
            'empresas_entrenamiento': eligible.loc[eligible.particion.eq('entrenamiento'), 'RPJ'].nunique(),
            'empresas_prueba': eligible.loc[eligible.particion.eq('prueba'), 'RPJ'].nunique(),
            'fcl_disponible': len(f), 'fcl_faltante_pct': g.FCL_preliminar.isna().mean()*100,
            'ciiu_faltante': g.CIIU.isna().sum(), 'fcl_mediana': f.median(),
            'fcl_desviacion': f.std(), 'fcl_riq': iqr, 'fcl_asimetria': f.skew(),
            'fcl_extremos_riq': ((f < q1-1.5*iqr) | (f > q3+1.5*iqr)).sum(),
            'participacion_panel_pct': len(g)/len(panel)*100,
            'muestra_insuficiente': (g.RPJ.nunique() < 5 or
                eligible.particion.eq('entrenamiento').sum() < 30 or
                eligible.particion.eq('prueba').sum() < 10),
        })
    return pd.DataFrame(rows)


def fingerprints(root):
    """Protege originales y todos los entregables preexistentes de experimentos."""
    root = Path(root)
    paths = list((root/'data/processed').glob('*.csv')) + list((root/'data/raw').glob('*.xlsx'))
    paths += list((root/'reports/sprint_06').rglob('*'))
    paths += [p for p in (root/'notebooks').glob('*.ipynb') if p.name != '08_clasificacion_sectorial.ipynb']
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file()}


def plots(d, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'figure.dpi': 140})
    def save(fig, name):
        fig.tight_layout(); fig.savefig(out/name, bbox_inches='tight'); plt.close(fig)
    for col, name, title in [('macrosector_propuesto', 'empresas_macrosector.png', 'Empresas por macrosector'),
                              ('industria_analisis', 'empresas_industria.png', 'Empresas por industria; cobertura parcial')]:
        s = d.groupby(col).RPJ.nunique().sort_values()
        fig, ax = plt.subplots(figsize=(10, 5)); s.plot.barh(ax=ax)
        ax.set(xlabel='RPJ únicos por grupo (una empresa puede figurar en varios)', title=title)
        save(fig, name)
    for value, name, title in [('RPJ', 'cobertura_temporal.png', 'Empresas por industria y año'),
                                ('FCL_preliminar', 'disponibilidad_sector_anio.png', 'FCL disponible por sector SMV y año')]:
        group = 'industria_analisis' if value == 'RPJ' else 'TipoSector'
        grid = pd.MultiIndex.from_product([sorted(d[group].unique()), range(2005, 2026)])
        g = d.groupby([group, 'Ejercicio'])[value]
        s = g.nunique() if value == 'RPJ' else g.count()
        matrix = s.reindex(grid, fill_value=0).unstack()
        fig, ax = plt.subplots(figsize=(13, 4)); im=ax.imshow(matrix, aspect='auto', cmap='Blues')
        ax.set_yticks(range(len(matrix)), matrix.index); ax.set_xticks(range(21), range(2005, 2026), rotation=90)
        ax.set(title=title, xlabel='Ejercicio'); fig.colorbar(im, ax=ax, label='Conteo'); save(fig, name)
    fig, ax = plt.subplots(figsize=(11, 5))
    pd.crosstab(d.TipoSector, d.Moneda).plot.barh(stacked=True, ax=ax)
    ax.set(title='Observaciones por sector SMV y moneda', xlabel='Observaciones'); save(fig, 'sector_moneda.png')
    currencies = sorted(d.Moneda.unique())
    fig, axs = plt.subplots(1, len(currencies), figsize=(14, 5), squeeze=False)
    for ax, currency in zip(axs[0], currencies):
        g = d.loc[d.Moneda.eq(currency)]
        labels = sorted(g.industria_analisis.unique())
        vals = [g.loc[g.industria_analisis.eq(x), 'FCL_preliminar'].dropna().to_numpy() for x in labels]
        ax.boxplot(vals, tick_labels=labels, vert=False); ax.set_xscale('symlog')
        ax.set(title=currency, xlabel='FCL reportado; eje symlog, escala monetaria no acreditada')
    fig.suptitle('Distribución de FCL por industria y moneda; sin recorte'); save(fig, 'fcl_industria.png')


def run(root, output=None, make_plots=True):
    root = Path(root); out = Path(output) if output else root/'reports/sprint_07'
    out.mkdir(parents=True, exist_ok=True)
    before = fingerprints(root)
    p = read_panel(root)
    financial = pd.read_csv(root/'data/processed/panel_fcl_preliminar.csv',
        dtype={'RPJ':'string','RUC':'string','CIIU':'string'}, float_precision='round_trip')
    financial = financial.sort_values(['RPJ','Ejercicio']).reset_index(drop=True)
    comparable = p[financial.columns].copy()
    comparable['CIIU'] = comparable.CIIU.map(normalize_ciiu).astype('string')
    financial['CIIU'] = financial.CIIU.map(normalize_ciiu).astype('string')
    pd.testing.assert_frame_equal(comparable, financial, check_exact=True)
    eligible = p.objetivo_fcl_t1.notna() & p.Moneda.eq(p.moneda_objetivo)
    assert eligible.equals(p.utilizable_supervisado)
    # Contraste independiente con las predicciones ya existentes; no se ejecutan modelos.
    previous = pd.read_csv(root/'reports/sprint_06/predicciones_baseline.csv', dtype={'RPJ':'string'})
    previous = previous.loc[previous.escenario.eq('principal') & previous.experimento.eq('E0_financiero')]
    prior = previous[['RPJ','Ejercicio','particion']].sort_values(['RPJ','Ejercicio']).reset_index(drop=True)
    current = p.loc[eligible, ['RPJ','Ejercicio','particion']].sort_values(['RPJ','Ejercicio']).reset_index(drop=True)
    pd.testing.assert_frame_equal(prior, current, check_dtype=False, check_exact=True)
    source = json.loads((root/'data/raw/damodaran/fuente_2026.json').read_text())
    assert hashlib.sha256((root/'data/raw/damodaran/betas_2026.html').read_bytes()).hexdigest() == source['sha256_html']
    official = pd.read_csv(root/'data/raw/damodaran/industrias_2026.csv').industria_damodaran
    assert official.tolist() == extract_official_names((root/'data/raw/damodaran/betas_2026.html').read_text())
    catalog = classify(p, official)
    d = join_classification(p, catalog)
    d['industria_analisis'] = d.industria_damodaran.fillna(PENDIENTE)
    tables = {'catalogo_correspondencias.csv': catalog,
              'casos_pendientes.csv': catalog.loc[catalog.estado_clasificacion.eq('Pendiente')],
              'distribucion_industria.csv': summary(d, ['industria_analisis','Moneda']),
              'auditoria_sector_moneda.csv': summary(d, ['TipoSector','Moneda']),
              'distribucion_macrosector.csv': summary(d, ['macrosector_propuesto','Moneda'])}
    tables['cobertura_sector_anio.csv'] = d.groupby(['TipoSector','Ejercicio','Moneda']).agg(
        empresas=('RPJ','nunique'), observaciones=('RPJ','size'), fcl_disponible=('FCL_preliminar','count')).reset_index()
    # Una fila por RPJ con listas de valores observados; no se elige un nombre o CIIU arbitrario.
    firms = catalog.groupby('RPJ').agg(
        nombres=('NombreEmpresa', lambda s:' | '.join(sorted(s.dropna().unique()))),
        rucs=('RUC', lambda s:' | '.join(sorted(s.dropna().unique()))),
        sectores=('TipoSector', lambda s:' | '.join(sorted(s.dropna().unique()))),
        ciius=('CIIU', lambda s:' | '.join(sorted(s.dropna().unique()))),
        industrias=('industria_damodaran', lambda s:' | '.join(sorted(s.dropna().unique()))),
        registros=('RPJ','size'), registros_clasificados=('industria_damodaran','count'),
        cambio_sector_posible=('cambio_sector_posible','max'), identificador_inconsistente=('identificador_inconsistente','max')).reset_index()
    firms['clasificacion_completa'] = firms.registros.eq(firms.registros_clasificados)
    tables['empresas_clasificacion.csv'] = firms
    tables['identificadores_ruc_compartidos.csv'] = catalog.loc[catalog.RUC.isin(
        catalog.groupby('RUC').RPJ.nunique().loc[lambda s:s.gt(1)].index), ['RPJ','RUC','NombreEmpresa']].drop_duplicates()
    tables['casos_cambio_sector.csv'] = catalog.loc[catalog.cambio_sector_posible]
    for name, table in tables.items():
        table.to_csv(out/name, index=False, encoding='utf-8')
    if make_plots:
        plots(d, out)
    assigned = catalog.industria_damodaran.notna()
    audit = {'estado':'EJECUTADO_CON_CLASIFICACION_PARCIAL', 'fuente':source,
        'observaciones':len(p), 'empresas':p.RPJ.nunique(),
        'empresas_con_alguna_clasificacion':catalog.loc[assigned,'RPJ'].nunique(),
        'empresas_completamente_clasificadas':int(firms.clasificacion_completa.sum()),
        'empresas_con_registros_pendientes':catalog.loc[~assigned,'RPJ'].nunique(),
        'registros_clasificados':int(assigned.sum()), 'registros_pendientes':int((~assigned).sum()),
        'industrias_identificadas':catalog.industria_damodaran.nunique(),
        'elegibles':int(eligible.sum()), 'empresas_elegibles':p.loc[eligible,'RPJ'].nunique(),
        'particiones_elegibles':p.loc[eligible,'particion'].value_counts().to_dict(),
        'ciiu_faltantes_registros':int(p.CIIU.isna().sum()),
        'empresas_sin_ciiu_en_todo_historial':int(p.groupby('RPJ').CIIU.count().eq(0).sum()),
        'registros_ciiu_revision_no_declarada':int(p.CIIU.notna().sum()),
        'ciiu_sintaxis_invalida':int((p.CIIU.notna() & catalog.ciiu_normalizado.isna()).sum()),
        'empresas_cambio_sector':int(firms.cambio_sector_posible.sum()),
        'empresas_multiples_ciiu':int(p.groupby('RPJ').CIIU.nunique().gt(1).sum()),
        'empresas_multiples_ruc':int(firms.identificador_inconsistente.sum()),
        'ruc_compartido_entre_rpj':int(catalog.groupby('RUC').RPJ.nunique().gt(1).sum()),
        'empresas_multiples_nombres':int(p.groupby('RPJ').NombreEmpresa.nunique().gt(1).sum()),
        'rpj_faltante':int(p.RPJ.isna().sum()), 'ruc_faltante':int(p.RUC.isna().sum()),
        'periodo':[int(p.Ejercicio.min()),int(p.Ejercicio.max())],
        'umbral_orientativo':{'empresas_min':5,'train_min':30,'test_min':10},
        'controles':{'union_sin_perdidas':True,'sin_duplicados_empresa_anio':True,
          'valores_originales_exactos':True,'particiones_iguales_sprint06':True,
          'archivos_previos_preservados':before == fingerprints(root)},
        'archivos_previos_sha256':before,
        'salidas_sha256':{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in tables}}
    assert all(audit['controles'].values())
    def safe(x):
        if isinstance(x,dict):return {str(k):safe(v) for k,v in x.items()}
        if isinstance(x,list):return [safe(v) for v in x]
        if isinstance(x,np.generic):return x.item()
        return x
    audit = safe(audit)
    (out/'auditoria_sectorial.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return d, tables, audit
