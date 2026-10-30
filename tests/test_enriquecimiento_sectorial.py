"""Auditoría independiente de la capa documental; conserva los 23 tests anteriores."""
from pathlib import Path
import json
import shutil
import tempfile
import unittest
import pandas as pd
import openpyxl
from src.clasificacion_sectorial import read_panel, classify, join_classification
from src.enriquecimiento_sectorial import (run, valid_ruc, load_evidence, enrich,
    regulatory_evidence, baseline_hashes, sha, BASE, OUT)

ROOT=Path(__file__).resolve().parents[1]


class DocumentaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel=read_panel(ROOT)
        cls.official=pd.read_csv(ROOT/'data/raw/damodaran/industrias_2026.csv').industria_damodaran
        cls.old=classify(cls.panel,cls.official)
        cls.temp=tempfile.TemporaryDirectory()
        cls.joined,cls.tables,cls.audit=run(ROOT,Path(cls.temp.name))
        cls.c=cls.tables['catalogo_empresa_anio.csv']
        cls.ev=cls.tables['evidencias_actividad.csv']

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_maestro_universo_ruc_y_estados_disjuntos(self):
        m=self.tables['catalogo_maestro_empresas.csv']
        self.assertEqual(len(m),336)
        self.assertFalse(m.RPJ.duplicated().any())
        self.assertEqual(set(m.RPJ),set(self.panel.RPJ))
        self.assertEqual(m.observaciones.sum(),4221)
        self.assertEqual(sum(len(self.tables[f'empresas_{s}.csv']) for s in
            ['clasificadas','parcialmente_clasificadas','pendientes']),336)
        self.assertEqual(m.RUC_valido_formal.ne('').sum(),330)
        self.assertFalse(m.ruc_consulta_sunat_realizada.any())
        self.assertEqual(self.audit['ruc_validos_compartidos'],0)

    def test_ruc_no_inventa_extranjeros_y_rechaza_digito_alterado(self):
        self.assertTrue(valid_ruc('20100128056'))
        self.assertFalse(valid_ruc('20100128057'))
        for value in ['0','','2010012805',None]:
            self.assertFalse(valid_ruc(value))
        m=self.tables['catalogo_maestro_empresas.csv']
        self.assertTrue(m.loc[m.RUC_originales.eq('0'),'RUC_valido_formal'].eq('').all())

    def test_union_finanzas_elegibilidad_y_particiones_exactas(self):
        pd.testing.assert_frame_equal(self.joined[self.panel.columns],self.panel,check_exact=True)
        self.assertFalse(self.c.duplicated(['RPJ','Ejercicio']).any())
        self.assertEqual(self.audit['particiones_elegibles'],{'entrenamiento':2869,'prueba':691})
        self.assertEqual(set(self.c.RPJ),set(self.panel.RPJ))

    def test_reglas_previas_preservadas_sin_reescritura(self):
        mask=self.old.industria_damodaran.notna()
        pd.testing.assert_frame_equal(self.c.loc[mask,self.old.columns],self.old.loc[mask],check_dtype=False,check_exact=True)
        self.assertEqual(self.audit['hashes_primera_entrega'],baseline_hashes(ROOT))
        self.assertEqual(self.audit['cobertura_anterior']['observaciones_pendientes'],4134)

    def test_toda_nueva_asignacion_tiene_evidencia_del_mismo_rpj_y_anio(self):
        ids=self.ev.set_index('evidencia_id')
        added=self.c.loc[self.c.industria_anterior.isna() & self.c.industria_damodaran.notna()]
        self.assertGreater(len(added),300)
        for row in added.itertuples(index=False):
            evidence=ids.loc[row.evidencias_documentales.split('|')]
            ok=evidence.loc[evidence.estado_evidencia.eq('Asignable') &
                 evidence.industria_propuesta.eq(row.industria_damodaran)]
            self.assertGreater(len(ok),0)
            for e in ok.itertuples():
                self.assertEqual(e.RPJ,row.RPJ)
                self.assertIn(str(row.Ejercicio),e.anios_respaldados.split('|'))
                self.assertEqual((e.certeza_actividad,e.certeza_correspondencia),('Alta','Alta'))

    def test_huecos_sin_evidencia_no_se_interpolan(self):
        c=self.c
        self.assertTrue(c.loc[c.RPJ.eq('000355')&~c.Ejercicio.isin([2020,2024]),'industria_damodaran'].isna().all())
        # Aseguradora de vida: un informe 2025 respalda el comparativo 2024, nunca 2005–2023.
        self.assertTrue(c.loc[c.RPJ.eq('OE2069')&c.Ejercicio.lt(2024),'industria_damodaran'].isna().all())
        no_evidence=c.evidencias_documentales.eq('') & c.industria_anterior.isna()
        self.assertTrue(c.loc[no_evidence,'industria_damodaran'].isna().all())

    def test_no_fuerza_holdings_bancos_ni_perimetro_consolidado(self):
        for rpj in ['B80004','B80020','B30121','023106','B60001','OE5087','B20010']:
            self.assertTrue(self.c.loc[self.c.RPJ.eq(rpj),'industria_damodaran'].isna().all(),rpj)
        self.assertGreater(self.tables['cambios_actividad_revision.csv'].shape[0],0)

    def test_conflictos_documentales_se_rechazan(self):
        ev=self.ev.copy()
        first=ev.loc[ev.estado_evidencia.eq('Asignable')].iloc[[0]].copy()
        first['evidencia_id']='CONTRADICCION'
        first['industria_propuesta']='Education'
        ev=pd.concat([ev,first],ignore_index=True)
        with self.assertRaisesRegex(ValueError,'contradictorias'):
            enrich(self.panel,self.old,ev)

    def test_ciiu_no_se_imputa_desde_actividad_ni_otro_anio(self):
        pd.testing.assert_series_equal(self.c.CIIU,self.panel.CIIU,check_exact=True)
        reg=self.tables['revision_smv_empresa_anio.csv']
        merged=self.c[['RPJ','Ejercicio','ciiu_smv_documental']].merge(reg[['RPJ','Ejercicio','ciiu_smv_documental']],
            on=['RPJ','Ejercicio'],validate='one_to_one',suffixes=('_out','_raw'))
        self.assertTrue(merged.ciiu_smv_documental_out.fillna('').eq(merged.ciiu_smv_documental_raw.fillna('')).all())
        self.assertTrue(set(self.c.industria_damodaran.dropna()).issubset(set(self.official)))

    def test_tampering_pdf_texto_y_ciiu_no_documentado(self):
        ev=self.ev.loc[self.ev.evidencia_id.eq('E001')].drop(columns=['tipo_fuente','hoja','celdas'])
        sid=ev.fuente_id.iloc[0]
        with tempfile.TemporaryDirectory() as tmp:
            b=Path(tmp)/BASE;b.mkdir(parents=True)
            for ext in ['pdf','txt','json']:
                shutil.copyfile(ROOT/BASE/f'{sid}.{ext}',b/f'{sid}.{ext}')
            specs=json.loads((ROOT/BASE/'descargas.json').read_text())
            (b/'descargas.json').write_text(json.dumps([s for s in specs if s['id']==sid]))
            ev.to_csv(b/'evidencias_actividad.csv',index=False)
            load_evidence(Path(tmp),self.panel,self.official)
            original_name=ev.entidad_documento.iloc[0]
            ev.loc[:,'entidad_documento']='ENTIDAD SIN RELACION CON EL DOCUMENTO'
            ev.to_csv(b/'evidencias_actividad.csv',index=False)
            with self.assertRaisesRegex(ValueError,'Entidad no identificada'):
                load_evidence(Path(tmp),self.panel,self.official)
            ev.loc[:,'entidad_documento']=original_name
            ev.loc[:,'ciiu_documental']='9999';ev.to_csv(b/'evidencias_actividad.csv',index=False)
            with self.assertRaisesRegex(ValueError,'CIIU no transcrito'):
                load_evidence(Path(tmp),self.panel,self.official)
            ev.loc[:,'ciiu_documental']='';ev.to_csv(b/'evidencias_actividad.csv',index=False)
            with (b/f'{sid}.txt').open('a') as f:f.write('ALTERACION')
            with self.assertRaisesRegex(ValueError,'Fuente alterada'):
                load_evidence(Path(tmp),self.panel,self.official)

    def test_minem_rechaza_celdas_sin_inversion_positiva_y_autoconsumo(self):
        # Libro mínimo independiente: años con cero, hueco y valor positivo; otro año industrial.
        with tempfile.TemporaryDirectory() as tmp:
            b=Path(tmp)/BASE;b.mkdir(parents=True)
            w=openpyxl.Workbook();s=w.active;s.title='Serie';s['B3']='Actividad de generación';s['B4']='EMPRESA A'
            for col,year,value in [('M',2005,0),('N',2006,None),('O',2007,2),('P',2008,3)]:
                s[f'{col}3']=year;s[f'{col}4']=value
            p=b/'minem24_cap10.xlsx';w.save(p)
            (b/'fuentes_estadisticas.json').write_text(json.dumps([{'id':'minem24_cap10','url':'https://www.gob.pe/ejemplo','sha256':sha(p)}]))
            pd.DataFrame([dict(RPJ='A',RUC_panel='20100128056',nombre_panel='EMPRESA A',fuente_id='minem24_cap10',hoja='Serie',
                fila_empresa=4,nombre_minem='EMPRESA A',fila_encabezado_actividad=3,actividad_minem='Actividad de generación',
                fila_encabezado_anio=3,justificacion_identidad='Referencia manual de prueba',limite='No interpolar')]).to_csv(b/'correspondencias_minem.csv',index=False)
            panel=pd.DataFrame({'RPJ':['A']*4,'RUC':['20100128056']*4,'NombreEmpresa':['EMPRESA A']*4,
                'Ejercicio':[2005,2006,2007,2008],'TipoSector':['SERVICIOS PUBLICOS']*3+['INDUSTRIALES']})
            ev,detail,_=regulatory_evidence(Path(tmp),panel)
            self.assertEqual(detail.Ejercicio.tolist(),[2007])
            self.assertEqual(ev.anios_respaldados.tolist(),['2007'])

    def test_reproduccion_exacta_catalogos_y_json_sin_red(self):
        for name in self.tables:
            self.assertEqual((Path(self.temp.name)/name).read_bytes(),(ROOT/OUT/name).read_bytes(),name)
        self.assertEqual(self.audit,json.loads((ROOT/OUT/'auditoria_enriquecimiento.json').read_text()))
        self.assertTrue(all(self.audit['controles'].values()))
