"""Controles y priorización de la Fase 3; no ajusta modelos ni valores financieros."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

OUT='reports/sprint_07/fase_3'
BASE='data/raw/sectorial_fase3'


def select_evidence(evidence, reference_year):
    """Primero vigencia, luego calidad y jerarquía; el ID no aporta calidad."""
    if evidence.empty:
        return None
    e=evidence.copy()
    e['_vigente']=e.anios_respaldados.map(lambda s:int(reference_year) in {int(y) for y in str(s).split('|')})
    e['_anio']=pd.to_numeric(e.anio_referencia,errors='raise')
    quality={'Alta':3,'Media':2,'Baja':1,'Pendiente':0}
    e['_calidad']=e.certeza_actividad.map(quality).fillna(0)
    # Campo explícito; alternativas sin este campo usan el tipo, sin analizar el ID.
    hierarchy={'EEFF individual auditado':5,'Memoria anual del emisor':4,
        'Nota individual no auditada':3,'Descripción de entidad en consolidado':2,
        'Estadística oficial sectorial':1,'Documento empresarial primario (tipo no normalizado)':4}
    if 'clase_documental' in e:
        e['_jerarquia']=e.clase_documental.map(hierarchy).fillna(0)
    else:
        e['_jerarquia']=e.tipo_fuente.map({'PDF':4,'XLSX':1}).fillna(0)
    # Evita privilegiar una memoria antigua frente a una actividad posterior distinta.
    if e._vigente.any():
        candidates=e.loc[e._vigente]
    else:
        candidates=e.loc[e._anio.eq(e._anio.max())]
    candidates=candidates.sort_values(['_calidad','_jerarquia','_anio','fuente_url','actividad_principal'],
        ascending=[False,False,False,True,True],kind='stable')
    winner=candidates.iloc[0]
    peers=candidates.loc[candidates._calidad.eq(winner._calidad)&candidates._jerarquia.eq(winner._jerarquia)&candidates._anio.eq(winner._anio)]
    if peers.industria_propuesta.replace('',pd.NA).dropna().nunique()>1:
        raise ValueError('Evidencias de igual calidad y vigencia discrepan; revisar antes de resumir')
    return evidence.loc[winner.name]


def temporal_status(observations, evidence):
    """Evalúa años y etiquetas, no igualdad de redacciones del texto de actividad."""
    backed=sorted(set(int(y) for s in evidence.anios_respaldados for y in str(s).split('|')))
    if not backed:
        return 'Historia sin evidencia específica'
    assigned=observations.loc[observations.industria_damodaran.notna()]
    industries=set(assigned.industria_damodaran.dropna())
    if not industries:
        return 'Actividad documentada; industria o coincidencia temporal pendiente'
    inner_missing=sorted(set(range(backed[0],backed[-1]+1))-set(backed))
    if len(industries)>1:
        return 'Múltiples industrias en ejercicios documentados; revisar cambio o perímetro'
    return ('Industria compatible; intervalo documentado sin huecos internos' if not inner_missing else
            'Industria compatible; huecos internos documentales pendientes')


def canonical_minem(mapping, root):
    """Una entidad por RPJ; cada localizador histórico se conserva como procedencia."""
    import openpyxl
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',message='Unable to read chart.*',category=UserWarning)
        w=openpyxl.load_workbook(Path(root)/'data/raw/sectorial_documental/minem24_cap10.xlsx',data_only=True)
    rows=[]
    for rpj,g in mapping.groupby('RPJ',sort=True):
        if g.RUC_panel.nunique()!=1 or g.nombre_panel.nunique()!=1:
            raise ValueError('Identidad MINEM contradictoria')
        locators=[]
        for m in g.itertuples(index=False):
            s=w[m.hoja];r=int(m.fila_empresa)
            years=[int(s.cell(int(m.fila_encabezado_anio),c).value) for c in range(3,33)
                if isinstance(s.cell(int(m.fila_encabezado_anio),c).value,int)
                and isinstance(s.cell(r,c).value,(int,float)) and s.cell(r,c).value>0]
            locators.append({'hoja':m.hoja,'fila':r,'nombre_fuente':m.nombre_minem,
                'anios_con_inversion_positiva':years,'uso':'Histórico anterior a 2005' if years and max(years)<2005 else 'Incluye años del panel'})
        rows.append({'RPJ':rpj,'RUC_panel':g.RUC_panel.iloc[0],'nombre_panel':g.nombre_panel.iloc[0],
            'localizadores':json.dumps(sorted(locators,key=lambda x:(x['hoja'],x['fila'])),ensure_ascii=False),
            'cantidad_localizadores':len(locators),'duplicado_empresarial':False})
    return pd.DataFrame(rows)


def priority_table(panel, catalog):
    d=panel.merge(catalog[['RPJ','Ejercicio','industria_damodaran']],on=['RPJ','Ejercicio'],validate='one_to_one')
    d['pendiente']=d.industria_damodaran.isna()
    rows=[]
    financial={'BANCOS','SEGUROS','FINANCIERAS','A.F.P.','AFP','ADMINISTRADORAS DE FONDOS DE PENSIONES'}
    for rpj,g in d.groupby('RPJ',sort=True):
        p=g.loc[g.pendiente]
        if p.empty:continue
        eligible=p.loc[p.utilizable_supervisado]
        train=eligible.loc[eligible.particion.eq('entrenamiento')]
        test=eligible.loc[eligible.particion.eq('prueba')]
        rows.append({'RPJ':rpj,'NombreEmpresa':g.NombreEmpresa.iloc[0],'RUC':g.RUC.iloc[0],
            'TipoSector':g.TipoSector.iloc[0],'grupo_priorizacion':'Financiero' if g.TipoSector.iloc[0] in financial else 'No financiero',
            'observaciones_pendientes':len(p),'entrenamiento_elegible_pendiente':len(train),
            'prueba_elegible_pendiente':len(test),'total_elegible_pendiente':len(eligible),
            'ambas_particiones':bool(len(train) and len(test)),
            'anios_entrenamiento_pendientes':'|'.join(map(str,sorted(train.Ejercicio.unique()))),
            'anios_prueba_pendientes':'|'.join(map(str,sorted(test.Ejercicio.unique()))),
            'motivo':'Recuperar evidencia primaria de la entidad y los ejercicios con mayor muestra elegible; no usar métricas predictivas'})
    result=pd.DataFrame(rows).sort_values(['total_elegible_pendiente','ambas_particiones',
        'entrenamiento_elegible_pendiente','prueba_elegible_pendiente','RPJ'],ascending=[False,False,False,False,True]).reset_index(drop=True)
    result.insert(0,'prioridad',np.arange(1,len(result)+1))
    return result


def sufficiency(panel):
    """Conteos separados por moneda y RPJ independientes; no estima independencia estadística."""
    rows=[]
    for (industry,currency),g in panel.loc[panel.industria_damodaran.notna()].groupby(['industria_damodaran','Moneda']):
        e=g.loc[g.utilizable_supervisado];tr=e.loc[e.particion.eq('entrenamiento')];te=e.loc[e.particion.eq('prueba')]
        original_threshold=g.RPJ.nunique()>=5 and len(tr)>=30 and len(te)>=10
        independent_threshold=tr.RPJ.nunique()>=5 and te.RPJ.nunique()>=5
        rows.append({'industria_damodaran':industry,'Moneda':currency,'empresas_panel':g.RPJ.nunique(),
            'observaciones_panel':len(g),'empresas_entrenamiento':tr.RPJ.nunique(),'empresas_prueba':te.RPJ.nunique(),
            'observaciones_entrenamiento':len(tr),'observaciones_prueba':len(te),
            'anios_entrenamiento':tr.anio_objetivo.nunique(),'anios_prueba':te.anio_objetivo.nunique(),
            'supera_umbral_original':original_threshold,'diversidad_empresarial_minima':independent_threshold,
            'muestra_suficiente_orientativa':original_threshold and independent_threshold,
            'muestra_insuficiente':not original_threshold,
            'nota':'Umbral original: >=5 RPJ en panel, >=30 filas train y >=10 test; condición adicional >=5 RPJ en cada partición. No prueba independencia, potencia estadística ni validez del FCL financiero.'})
    return pd.DataFrame(rows)
