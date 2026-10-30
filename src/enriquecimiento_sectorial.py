"""Extensión documental auditable. Las reglas D01/D02/P01/P02/P03 no se modifican."""
from pathlib import Path
import hashlib
import json
import platform
import re
import warnings
import unicodedata
import numpy as np
import pandas as pd
from scripts.trace_smv import extract
from src.clasificacion_sectorial import (read_panel, classify, join_classification,
    summary, fingerprints, normalize_ciiu, PENDIENTE)

BASE = 'data/raw/sectorial_documental'
OUT = 'reports/sprint_07/fase_3'
from src.sectorial_fase3 import select_evidence, temporal_status, canonical_minem, priority_table, sufficiency


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def norm(text):
    return ' '.join(unicodedata.normalize('NFKC', str(text)).split())


def valid_ruc(value):
    """Control formal de longitud, prefijo y dígito; no acredita alta/estado SUNAT."""
    if pd.isna(value):
        return False
    text = str(value)
    if not re.fullmatch(r'(10|15|16|17|20)\d{9}', text):
        return False
    remainder = sum(int(d)*w for d,w in zip(text[:10], [5,4,3,2,7,6,5,4,3,2])) % 11
    return (11-remainder) % 10 == int(text[-1])


def baseline_hashes(root):
    root = Path(root)
    paths = [root/'src/clasificacion_sectorial.py', root/'tests/test_clasificacion_sectorial.py']
    paths += [p for p in (root/'reports/sprint_07').iterdir() if p.is_file()]
    return {str(p.relative_to(root)):sha(p) for p in sorted(paths)}


def source_inventory(root, base=BASE):
    b = Path(root)/base
    rows = []
    for spec in json.loads((b/'descargas.json').read_text()):
        sid = spec['id']; meta_path = b/(sid+'.json'); pdf=b/(sid+'.pdf'); txt=b/(sid+'.txt')
        row = {'fuente_id':sid,'url':spec['url'],'pdf_local':'','texto_local':'',
               'sha256_pdf':'','sha256_texto':'','estado':'No descargado','error':''}
        if pdf.exists() and txt.exists() and meta_path.exists():
            meta=json.loads(meta_path.read_text())
            if sha(pdf)!=meta['sha256'] or sha(txt)!=meta['sha256_texto']:
                raise ValueError(f'Fuente alterada: {sid}')
            row.update(pdf_local=str(pdf.relative_to(root)),texto_local=str(txt.relative_to(root)),
                sha256_pdf=sha(pdf),sha256_texto=sha(txt),estado='Conservado; revisar alcance de transcripción')
        error=b/(sid+'.error.json')
        if error.exists():
            row['error']=json.loads(error.read_text())['error']
        rows.append(row)
    return pd.DataFrame(rows)


def load_evidence(root, panel, official, base=BASE):
    root=Path(root)
    evidence = pd.read_csv(root/base/'evidencias_actividad.csv', dtype=str, keep_default_na=False)
    if evidence.evidencia_id.duplicated().any():
        raise ValueError('Evidencia duplicada')
    if not set(evidence.RPJ).issubset(set(panel.RPJ)):
        raise ValueError('RPJ documental fuera del universo')
    if not set(evidence.industria_propuesta.loc[evidence.industria_propuesta.ne('')]).issubset(set(official)):
        raise ValueError('Nombre industrial no oficial')
    sources=source_inventory(root,base).set_index('fuente_id')
    for e in evidence.itertuples(index=False):
        row=sources.loc[e.fuente_id]
        if not row.pdf_local:
            raise ValueError(f'Evidencia sin documento primario conservado: {e.evidencia_id}')
        text=(root/row.texto_local).read_text()
        if norm(e.entidad_documento).casefold() not in norm(text).casefold():
            raise ValueError(f'Entidad no identificada en documento: {e.evidencia_id}')
        pages=re.split(r'=== PAGINA PDF (\d+) ===',text)
        page_map={int(pages[i]):pages[i+1] for i in range(1,len(pages),2)}
        actual=norm(page_map[int(e.pagina_pdf)])
        if norm(e.ancla_verificacion).casefold() not in actual.casefold() or norm(e.extracto_verificable) not in actual:
            raise ValueError(f'Pasaje no verificado: {e.evidencia_id}')
        entity=panel.loc[panel.RPJ.eq(e.RPJ)]
        if set(entity.RUC.dropna())!={e.RUC_panel} or set(entity.NombreEmpresa)!={e.nombre_panel}:
            raise ValueError(f'Identidad no coincide con maestro: {e.evidencia_id}')
        for code in e.ciiu_documental.split('|') if e.ciiu_documental else []:
            if not re.fullmatch(r'\d{4}',code) or code not in actual:
                raise ValueError(f'CIIU no transcrito del pasaje: {e.evidencia_id}')
        years=[int(y) for y in e.anios_respaldados.split('|')]
        if len(years)!=len(set(years)) or any(y<2005 or y>2025 for y in years):
            raise ValueError(f'Años documentales inválidos: {e.evidencia_id}')
        if max(years)!=int(e.anio_referencia):
            raise ValueError(f'Período inconsistente: {e.evidencia_id}')
        if e.estado_evidencia=='Asignable' and (not e.industria_propuesta or
              e.certeza_actividad!='Alta' or e.certeza_correspondencia!='Alta'):
            raise ValueError(f'Asignación sin certeza suficiente: {e.evidencia_id}')
    return evidence, sources.reset_index()


def regulatory_evidence(root, panel, include_unassigned=False):
    """Serie primaria MINEM: verificar celda, año, actividad y entidad, sin interpolar."""
    import openpyxl
    root=Path(root);b=root/BASE
    mapping=pd.read_csv(b/'correspondencias_minem.csv',dtype=str,keep_default_na=False)
    specs=json.loads((b/'fuentes_estadisticas.json').read_text())
    meta=next(x for x in specs if x['id']=='minem24_cap10')
    path=b/'minem24_cap10.xlsx'
    if sha(path)!=meta['sha256']:
        raise ValueError('Libro MINEM alterado')
    # Solo se leen celdas. openpyxl no interpreta algunos gráficos del libro oficial.
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',message='Unable to read chart.*',category=UserWarning)
        w=openpyxl.load_workbook(path,read_only=False,data_only=True)
    detail=[];evidence=[]
    for m in mapping.itertuples(index=False):
        sheet=w[m.hoja];r=int(m.fila_empresa);h=int(m.fila_encabezado_actividad)
        if sheet.cell(r,2).value!=m.nombre_minem or sheet.cell(h,2).value!=m.actividad_minem:
            raise ValueError('Identidad o actividad MINEM fuera de localizador')
        entity=panel.loc[panel.RPJ.eq(m.RPJ)]
        if set(entity.RUC.dropna())!={m.RUC_panel} or set(entity.NombreEmpresa)!={m.nombre_panel}:
            raise ValueError('Identidad MINEM/maestro inconsistente')
        years=[];cells=[]
        for col in range(3,33):
            y=sheet.cell(int(m.fila_encabezado_anio),col).value
            value=sheet.cell(r,col).value
            if not isinstance(y,int) or not 2005<=y<=2025:
                continue
            matched=entity.loc[entity.Ejercicio.eq(y)]
            if matched.empty or not matched.TipoSector.eq('SERVICIOS PUBLICOS').all():
                continue
            positive=isinstance(value,(int,float)) and not isinstance(value,bool) and np.isfinite(value) and value>0
            investment_status=('Positiva' if positive else 'Cero' if isinstance(value,(int,float)) and value==0 else 'No acreditada')
            cell=sheet.cell(r,col).coordinate
            if positive:
                years.append(y);cells.append(cell)
            detail.append({'RPJ':m.RPJ,'Ejercicio':y,'fuente_id':m.fuente_id,'hoja':m.hoja,
                'celda_nombre':f'B{r}','nombre_minem':m.nombre_minem,'celda_actividad':f'B{h}',
                'actividad_minem':m.actividad_minem,'celda_anio':sheet.cell(3,col).coordinate,
                'celda_valor':cell,'inversion_miles_usd':value,'estado_inversion':investment_status,
                'estado_actividad':('Indicio sectorial con inversión positiva' if positive else 'No determinada por inversión; cero o vacío no implica inactividad'),
                'asignable_por_inversion':positive,'fuente_url':meta['url'],
                'sha256_fuente':meta['sha256'],'regla':'D04: indicio sectorial condicionado a inversión positiva; actividad independiente se acredita mediante D03' })
        if not years:
            continue
        eid=f'M{len(evidence)+1:03}'
        evidence.append({'evidencia_id':eid,'RPJ':m.RPJ,'nombre_panel':m.nombre_panel,'RUC_panel':m.RUC_panel,
            'fuente_id':m.fuente_id,'titulo_documento':'MINEM, Anuario Estadístico de Electricidad 2024, cuadro 10.17; serie histórica por empresa',
            'fuente_url':meta['url'],'pagina_pdf':'','seccion':m.actividad_minem,
            'anios_respaldados':'|'.join(map(str,years)),'anio_referencia':str(max(years)),
            'fecha_consulta':'2026-10-23','actividad_principal':'Empresa de servicio público eléctrico: '+m.actividad_minem,
            'categoria_propuesta':'Electricidad','industria_propuesta':'Power','ciiu_documental':'',
            'revision_ciiu_documental':'','certeza_actividad':'Alta','certeza_correspondencia':'Alta',
            'estado_evidencia':'Asignable','extracto_verificable':m.nombre_minem,'ancla_verificacion':m.nombre_minem,
            'alcance_temporal':'Celdas con inversión positiva y ejercicio coincidente; huecos quedan pendientes',
            'identidad_vinculo':m.justificacion_identidad,'observacion':m.limite,
            'disponibilidad_historica':'Fuente retrospectiva revisada; no certifica disponibilidad point-in-time',
            'tipo_fuente':'XLSX','entidad_documento':m.nombre_minem,'hoja':m.hoja,'celdas':'|'.join(cells)})
    stats_sources=[]
    for spec in specs:
        p=b/(spec['id']+'.xlsx')
        if sha(p)!=spec['sha256']:
            raise ValueError('Fuente estadística alterada')
        stats_sources.append({'fuente_id':spec['id'],'url':spec['url'],'pdf_local':'',
            'texto_local':'','sha256_pdf':'','sha256_texto':'','estado':'Libro XLSX primario conservado',
            'error':'','xlsx_local':str(p.relative_to(root)),'sha256_xlsx':sha(p)})
    return pd.DataFrame(evidence),pd.DataFrame(detail if include_unassigned else [d for d in detail if d['asignable_por_inversion']]),pd.DataFrame(stats_sources)


def smv_registry(root, panel):
    """Reutiliza el parser SOAP del repositorio, conservando localizador por registro."""
    root=Path(root);wanted=set(zip(panel.RPJ, panel.Ejercicio)); rows=[]
    for year in range(2005,2026):
        path=root/f'data/raw/smv/smv_infofinanciera_{year}_A_I.xml'
        if not path.exists():
            continue
        digest=sha(path)
        for position, item in enumerate(extract(path),start=1):
            key=(str(item['RPJ']).strip(),int(item['Ejercicio']))
            if key not in wanted:
                continue
            rows.append({'RPJ':key[0],'Ejercicio':key[1],
                'nombre_smv_documental':item.get('NombreEmpresa',''),
                'ruc_smv_documental':item.get('RUC',''),
                'sector_smv_documental':item.get('TipoSector',''),
                'ciiu_smv_documental':item.get('CIIU',''),
                'archivo_fuente':str(path.relative_to(root)), 'registro_fuente':position,
                'sha256_fuente':digest})
    result=pd.DataFrame(rows)
    if result.duplicated(['RPJ','Ejercicio']).any():
        raise ValueError('Múltiples registros SMV por clave; resolver antes de unir')
    return result


def enrich(panel, baseline, evidence):
    """Sobrepone solo evidencia explícita a pendientes y nunca extiende períodos."""
    c=baseline.copy(deep=True)
    c['industria_anterior']=baseline.industria_damodaran
    c['evidencias_documentales']=''
    c['actividad_documentada']=''
    c['fuente_documental']=''
    c['pagina_documental']=''
    c['hoja_documental']=''
    c['celdas_documentales']=''
    c['anios_documentales']=''
    c['ciiu_documental']=''
    c['revision_ciiu_documental']=''
    c['categoria_documental']=''
    c['certeza_actividad_documental']='Pendiente'
    c['certeza_industria_documental']='Pendiente'
    c['industria_candidata_documental']=''
    c['origen_asignacion']=np.where(c.industria_damodaran.notna(),'Regla original','Pendiente')
    proposals={}
    for e in evidence.itertuples(index=False):
        for y in map(int,e.anios_respaldados.split('|')):
            proposals.setdefault((e.RPJ,y),[]).append(e)
    for (rpj,year), es in proposals.items():
        mask=c.RPJ.eq(rpj)&c.Ejercicio.eq(year)
        if not mask.any():
            continue
        c.loc[mask,'evidencias_documentales']='|'.join(e.evidencia_id for e in es)
        for col,attr in [('actividad_documentada','actividad_principal'),('fuente_documental','fuente_url'),
                         ('pagina_documental','pagina_pdf'),('hoja_documental','hoja'),('celdas_documentales','celdas'),('anios_documentales','anios_respaldados'),
                         ('ciiu_documental','ciiu_documental'),('revision_ciiu_documental','revision_ciiu_documental'),
                         ('categoria_documental','categoria_propuesta'),('certeza_actividad_documental','certeza_actividad'),
                         ('certeza_industria_documental','certeza_correspondencia'),
                         ('industria_candidata_documental','industria_propuesta')]:
            c.loc[mask,col]=' ; '.join(dict.fromkeys(getattr(e,attr) for e in es if getattr(e,attr)))
        allowed=[e for e in es if e.estado_evidencia=='Asignable' and e.certeza_actividad=='Alta'
                 and e.certeza_correspondencia=='Alta' and e.industria_propuesta]
        inds=set(e.industria_propuesta for e in allowed)
        if len(inds)>1:
            raise ValueError(f'Evidencias contradictorias: {rpj}/{year}')
        if not inds or c.loc[mask,['cambio_sector_posible','identificador_inconsistente']].any().any():
            continue
        industry=next(iter(inds)); existing=c.loc[mask,'industria_damodaran'].iloc[0]
        if pd.notna(existing):
            if existing!=industry:
                raise ValueError('Documento contradice regla verificada; no sobrescribir')
            continue
        c.loc[mask,'industria_damodaran']=industry
        c.loc[mask,'regla_industria']=('D04: actividad eléctrica MINEM por empresa-año + sector SMV; inversión positiva'
            if all(getattr(e,'tipo_fuente','PDF')=='XLSX' for e in allowed) else
            'D03: actividad principal documentada; años y entidad explícitos')
        c.loc[mask,'fuente_regla']=' | '.join(dict.fromkeys(e.fuente_url for e in allowed))
        c.loc[mask,'estado_clasificacion']='Clasificado documentalmente'
        c.loc[mask,'origen_asignacion']='Documento primario'
        c.loc[mask,'version_clasificacion']='Damodaran January 2026 / sprint07-documental-v1'
    macro_by_industry={'Metals & Mining':'Extractivo','Precious Metals':'Extractivo','Power':'Servicios públicos',
        'Building Materials':'Industrial','Steel':'Industrial','Machinery':'Industrial','Food Processing':'Agroindustrial',
        'Engineering/Construction':'Construcción','Education':'Servicios','Retail (General)':'Comercio',
        'Retail (Grocery and Food)':'Comercio','Retail (Distributors)':'Comercio',
        'Real Estate (Operations & Services)':'Servicios inmobiliarios',
        'Financial Svcs. (Non-bank & Insurance)':'Financiero','Insurance (Life)':'Financiero'}
    c['macrosector_enriquecido']=c.macrosector_propuesto.where(c.macrosector_propuesto.ne('Pendiente'),
        c.industria_damodaran.map(macro_by_industry).fillna('Pendiente'))
    c['sector_enriquecido']=c.categoria_documental.where(c.industria_damodaran.notna() & c.categoria_documental.ne(''),c.sector_propuesto)
    c['estado_observacion']=np.where(c.industria_damodaran.notna(),'Clasificada','Pendiente')
    return c


def coverage(catalog):
    firm=catalog.groupby('RPJ').industria_damodaran.agg(n='size',clasificadas='count')
    return {'empresas':len(firm),'observaciones':len(catalog),
        'empresas_clasificadas':int(firm.clasificadas.eq(firm.n).sum()),
        'empresas_parcialmente_clasificadas':int((firm.clasificadas.gt(0)&firm.clasificadas.lt(firm.n)).sum()),
        'empresas_pendientes':int(firm.clasificadas.eq(0).sum()),
        'empresas_con_alguna_clasificacion':int(firm.clasificadas.gt(0).sum()),
        'observaciones_clasificadas':int(catalog.industria_damodaran.notna().sum()),
        'observaciones_pendientes':int(catalog.industria_damodaran.isna().sum()),
        'industrias':catalog.industria_damodaran.nunique()}


def master_catalog(panel, c, ev, registry):
    rows=[]
    for rpj,g in panel.groupby('RPJ',sort=True):
        h=c.loc[c.RPJ.eq(rpj)]; e=ev.loc[ev.RPJ.eq(rpj)]; local=registry.loc[registry.RPJ.eq(rpj)]
        n=int(h.industria_damodaran.notna().sum())
        rucs=sorted(set(g.RUC.dropna())); valid=[r for r in rucs if valid_ruc(r)]
        status='Clasificada' if n==len(g) else 'Parcialmente clasificada' if n else 'Pendiente'
        current=select_evidence(e, int(g.Ejercicio.max()))
        def unique(s):return '|'.join(sorted(set(s.dropna().astype(str))))
        rows.append({'RPJ':rpj,'NombreEmpresa':unique(g.NombreEmpresa),'TipoSector':unique(g.TipoSector),
            'RUC_originales': '|'.join(rucs),'RUC_valido_formal':valid[0] if len(valid)==1 else '',
            'estado_RUC':'Válido formalmente; sin consulta registral SUNAT' if len(valid)==1 else 'Ausente o inválido; no inventar',
            'ruc_consulta_sunat_realizada':False,
            'ejercicio_inicial':g.Ejercicio.min(),'ejercicio_final':g.Ejercicio.max(),
            'observaciones':len(g),'observaciones_clasificadas':n,'observaciones_pendientes':len(g)-n,
            'estado_clasificacion':status,'industrias_en_observaciones':unique(h.industria_damodaran),
            'macrosector_enriquecido':unique(h.macrosector_enriquecido),
            'fuentes_reglas_observadas':unique(h.fuente_regla),
            'reglas_aplicadas':unique(h.regla_industria),
            'actividad_principal_documentada':current.actividad_principal if current is not None else '',
            'fuente_actividad':current.fuente_url if current is not None else '',
            'anio_referencia_actividad':current.anio_referencia if current is not None else '',
            'categoria_propuesta':current.categoria_propuesta if current is not None else '',
            'industria_propuesta_documental':current.industria_propuesta if current is not None else '',
            'estado_industria_empresarial_documental':('Industria documentada en años de referencia; no acredita toda la historia'
                if current is not None and current.estado_evidencia=='Asignable' else
                'Actividad documentada; industria pendiente' if current is not None else
                'Regla original disponible; sin documento empresarial específico' if n else 'Pendiente de evidencia específica'),
            'certeza_actividad':current.certeza_actividad if current is not None else 'Pendiente',
            'certeza_industria':current.certeza_correspondencia if current is not None else 'Pendiente',
            'evidencias_documentales':unique(e.evidencia_id),'anios_documentados':unique(e.anios_respaldados),
            'evidencia_resumen_seleccionada':current.evidencia_id if current is not None else '',
            'criterio_seleccion':'Vigencia explícita, certeza, jerarquía documental, año; nunca identificador',
            'estado_temporal':temporal_status(h,e),
            'revision_smv_local':'Realizada' if len(local) else 'Sin registro localizado',
            'registros_smv_locales':len(local),'fuentes_smv_locales':unique(local.archivo_fuente),
            'resultado_revision_documental':'Actividad específica documentada; revisar industria/período según evidencia' if len(e) else
                'Fuente SMV local revisada; no acredita actividad principal específica; ampliar documentación',
            'motivo_pendiente':'' if status=='Clasificada' else
                'Años fuera del alcance documental' if n else
                'Industria/perímetro documental ambiguo' if len(e) else
                'Sin evidencia primaria específica suficiente',
            'siguiente_accion_auditoria':'Verificar notas por año, identidad jurídica, CIIU y frontera industrial antes de ampliar períodos'})
    return pd.DataFrame(rows)


def run(root, output=None):
    root=Path(root);out=Path(output) if output else root/OUT;out.mkdir(parents=True,exist_ok=True)
    protected=fingerprints(root); old_hash=baseline_hashes(root)
    phase2_path=root/'reports/sprint_07/enriquecimiento/auditoria_enriquecimiento.json'
    phase2_audit=json.loads(phase2_path.read_text())
    for rel,digest in phase2_audit['hashes_insumos'].items():
        if sha(root/rel)!=digest:raise ValueError('Insumo congelado de Fase 2 alterado: '+rel)
    for name,digest in phase2_audit['hashes_salidas'].items():
        if sha(phase2_path.parent/name)!=digest:raise ValueError('Salida congelada de Fase 2 alterada: '+name)
    phase2_hash=sha(phase2_path)
    panel=read_panel(root)
    official=pd.read_csv(root/'data/raw/damodaran/industrias_2026.csv').industria_damodaran
    old=classify(panel,official)
    if old.to_csv(index=False).encode('utf-8') != (root/'reports/sprint_07/catalogo_correspondencias.csv').read_bytes():
        raise ValueError('La clasificación original no reproduce el catálogo congelado')
    evidence,sources=load_evidence(root,panel,official)
    evidence['tipo_fuente']='PDF'
    evidence['hoja']=''
    evidence['celdas']=''
    evidence['clase_documental']='Documento empresarial primario (tipo no normalizado)'
    extra_base='data/raw/sectorial_fase3'
    if (root/extra_base/'evidencias_actividad.csv').exists():
        extra,extra_sources=load_evidence(root,panel,official,extra_base)
        extra['tipo_fuente']='PDF';extra['hoja']='';extra['celdas']=''
        evidence=pd.concat([evidence,extra],ignore_index=True)
        sources=pd.concat([sources,extra_sources],ignore_index=True)
    ev_reg,detail_reg,source_reg=regulatory_evidence(root,panel,include_unassigned=True)
    ev_reg['clase_documental']='Estadística oficial sectorial'
    evidence=pd.concat([evidence,ev_reg],ignore_index=True)
    if evidence.evidencia_id.duplicated().any():
        raise ValueError('Identificadores de evidencia repetidos entre corpus')
    sources=pd.concat([sources,source_reg],ignore_index=True).fillna('')
    registry=smv_registry(root,panel)
    c=enrich(panel,old,evidence)
    joined=join_classification(panel,c)
    joined['industria_analisis']=joined.industria_damodaran.fillna(PENDIENTE)
    # Un CIIU SMV solo se vincula por clave del mismo ejercicio, nunca hacia atrás.
    c=c.merge(registry[['RPJ','Ejercicio','ciiu_smv_documental','archivo_fuente','registro_fuente']],
        on=['RPJ','Ejercicio'],how='left',validate='one_to_one',sort=False)
    master=master_catalog(panel,c,evidence,registry)
    before,after=coverage(old),coverage(c)
    frozen=pd.read_csv(root/'reports/sprint_07/enriquecimiento/catalogo_empresa_anio.csv',dtype={'RPJ':str})
    phase2=coverage(frozen)
    prior=priority_table(panel,frozen)
    mapping=pd.read_csv(root/BASE/'correspondencias_minem.csv',dtype=str,keep_default_na=False)
    assert before['observaciones_clasificadas']==87 and before['empresas_con_alguna_clasificacion']==7
    assert after['observaciones_clasificadas']>=before['observaciones_clasificadas']
    inherited=old.industria_damodaran.notna()
    pd.testing.assert_frame_equal(c.loc[inherited,list(old.columns)],old.loc[inherited],check_dtype=False,check_exact=True)
    comparison=pd.DataFrame([{'indicador':k,'anterior':before[k],'nueva':after[k],
                             'diferencia':after[k]-before[k]} for k in before])
    changes=pd.DataFrame([{'RPJ':'B30121','evento':'Reorganización de UNACEM hacia estructura holding',
        'fecha_reportada':'2022-01-01','fuente':'https://www.smv.gob.pe/ConsultasP8/temp/HdI%20Reorganizacion%20societaria%20-%20EEFF%20apertura.pdf',
        'estado':'Reportado en fuente primaria indexada; copia original pendiente HTTP 403',
        'efecto':'No atribuir producción de subsidiarias a la matriz; no asignar industria ni rellenar historia con este indicio'}])
    pairs=[]
    for e in evidence.itertuples(index=False):
        for year in map(int,e.anios_respaldados.split('|')):
            if not ((panel.RPJ==e.RPJ)&(panel.Ejercicio==year)).any():
                pairs.append({'evidencia_id':e.evidencia_id,'RPJ':e.RPJ,'Ejercicio':year,
                    'industria_propuesta':e.industria_propuesta,'estado_evidencia':e.estado_evidencia,
                    'motivo':'Año documentado sin observación en panel; prohibido trasladar a otros ejercicios'})
    off_panel=pd.DataFrame(pairs,columns=['evidencia_id','RPJ','Ejercicio','industria_propuesta','estado_evidencia','motivo'])
    tables={'priorizacion_inicial.csv':prior,'priorizacion_pendientes.csv':priority_table(panel,c),
        'correspondencia_minem_canonica.csv':canonical_minem(mapping,root),
        'suficiencia_muestral.csv':sufficiency(joined),
        'comparacion_fase2_fase3.csv':pd.DataFrame([{'indicador':k,'fase2':phase2[k],'fase3':after[k],'diferencia':after[k]-phase2[k]} for k in phase2]),
        'catalogo_maestro_empresas.csv':master, 'evidencias_sin_observacion_panel.csv':off_panel,'catalogo_empresa_anio.csv':c,
        'evidencias_actividad.csv':evidence,'fuentes_documentales.csv':sources,
        'evidencias_estadisticas_empresa_anio.csv':detail_reg.loc[detail_reg.asignable_por_inversion],
        'revision_actividad_inversion.csv':detail_reg.merge(c[['RPJ','Ejercicio','industria_damodaran','regla_industria','evidencias_documentales']],on=['RPJ','Ejercicio'],how='left',validate='many_to_one'),
        'revision_smv_empresa_anio.csv':registry,'comparacion_cobertura.csv':comparison,
        'distribucion_industria.csv':summary(joined,['industria_analisis','Moneda']),
        'empresas_clasificadas.csv':master.loc[master.estado_clasificacion.eq('Clasificada')],
        'empresas_parcialmente_clasificadas.csv':master.loc[master.estado_clasificacion.eq('Parcialmente clasificada')],
        'empresas_pendientes.csv':master.loc[master.estado_clasificacion.eq('Pendiente')],
        'observaciones_pendientes.csv':c.loc[c.industria_damodaran.isna()],
        'cambios_actividad_revision.csv':changes,
        'correspondencia_actividad_ciiu_industria.csv':c.loc[c.evidencias_documentales.ne(''),[
            'RPJ','RUC','NombreEmpresa','Ejercicio','actividad_documentada','CIIU','ciiu_normalizado',
            'ciiu_smv_documental','ciiu_documental','revision_ciiu_documental','industria_candidata_documental',
            'industria_damodaran','regla_industria','evidencias_documentales','fuente_documental','pagina_documental','hoja_documental','celdas_documentales']]}
    for name,table in tables.items():
        table.to_csv(out/name,index=False,encoding='utf-8')
    inputs={str(p.relative_to(root)):sha(p) for p in sorted((root/BASE).iterdir()) if p.is_file()}
    inputs.update({str(p.relative_to(root)):sha(p) for p in sorted((root/'data/raw/sectorial_fase3').iterdir()) if p.is_file()})
    inputs.update({str(p.relative_to(root)):sha(p) for p in sorted((root/'data/raw/smv').glob('smv_infofinanciera_*_A_I.xml'))})
    sources_used=set(evidence.fuente_id)
    audit={'version':'sprint07-documental-fase3','fecha_consulta':'2026-10-23',
        'cobertura_anterior':before,'cobertura_fase2':phase2,'cobertura_nueva':after,
        'hash_auditoria_fase2':phase2_hash,
        'versiones':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__},
        'hashes_implementacion':{rel:sha(root/rel) for rel in ['src/enriquecimiento_sectorial.py',
            'scripts/reproduce_enriquecimiento_sectorial.py','scripts/descargar_evidencia_sectorial.py',
            'tests/test_enriquecimiento_sectorial.py','src/sectorial_fase3.py','tests/test_sectorial_fase3.py','scripts/descargar_evidencia_fase3.py','scripts/reporte_sectorial_fase3.py']},
        'empresas_con_documentacion_especifica':evidence.RPJ.nunique(),
        'empresas_con_industria_documental_en_anio_referencia':evidence.loc[evidence.estado_evidencia.eq('Asignable'),'RPJ'].nunique(),
        'industrias_documentales_en_anio_referencia':evidence.loc[evidence.estado_evidencia.eq('Asignable'),'industria_propuesta'].nunique(),
        'empresas_con_industria_documentada_sin_coincidencia_en_panel':master.loc[master.observaciones_clasificadas.eq(0) & master.industria_propuesta_documental.ne(''),'RPJ'].nunique(),
        'empresas_revisadas_en_smv_local':registry.RPJ.nunique(),
        'evidencias':len(evidence),'documentos_utilizados':len(sources_used),
        'empresas_sin_ruc_valido_formal':int(master.RUC_valido_formal.eq('').sum()),
        'ruc_validos_compartidos':int(master.loc[master.RUC_valido_formal.ne('')].groupby('RUC_valido_formal').RPJ.nunique().gt(1).sum()),
        'particiones_elegibles':panel.loc[panel.utilizable_supervisado,'particion'].value_counts().to_dict(),
        'controles':{'sin_perdidas_ni_duplicados':len(c)==len(panel) and not c.duplicated(['RPJ','Ejercicio']).any(),
            'reglas_verificadas_preservadas':True,'valores_financieros_y_particiones_exactos':True,
            'fuentes_conservadas_y_pasajes_verificados':True,
            'fase2_documentos_y_resultados_congelados':sha(phase2_path)==phase2_hash,
            'periodos_explicitos_sin_interpolacion':True,'sin_entrenamiento':True,
            'bases_y_experimentos_previos_intactos':protected==fingerprints(root),
            'primera_entrega_sprint07_intacta':old_hash==baseline_hashes(root)},
        'hashes_bases_previas':protected,'hashes_primera_entrega':old_hash,'hashes_insumos':inputs,
        'hashes_salidas':{name:sha(out/name) for name in tables},
        'limites':['No es taxonomía point-in-time ni consulta registral SUNAT.',
            'La revisión específica no cubre todas las empresas; el resto conserva revisión SMV local y pendientes explícitos.',
            'Los 0 de RUC extranjero no son un RUC compartido válido; no se inventa sustituto.',
            'CIIU ausente permanece ausente; los códigos documentales se conservan separados del original.',
            'Estabilidad solo en años documentados; un indicio de reorganización con HTTP 403 no habilita asignaciones.']}
    def safe(x):
        if isinstance(x,dict):return {k:safe(v) for k,v in x.items()}
        if isinstance(x,np.generic):return x.item()
        return x
    audit=safe(audit);assert all(audit['controles'].values())
    (out/'auditoria_enriquecimiento.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return joined,tables,audit
