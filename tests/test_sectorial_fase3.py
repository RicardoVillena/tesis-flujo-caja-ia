"""Regresiones de las cinco observaciones de auditoría y alcance histórico."""
from pathlib import Path
import json,unittest
import pandas as pd
from src.sectorial_fase3 import select_evidence,temporal_status,canonical_minem,priority_table,sufficiency
from src.clasificacion_sectorial import read_panel
from src.enriquecimiento_sectorial import regulatory_evidence,BASE,OUT
ROOT=Path(__file__).resolve().parents[1]
class Phase3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=read_panel(ROOT)
        cls.c=pd.read_csv(ROOT/OUT/'catalogo_empresa_anio.csv',dtype={'RPJ':str},keep_default_na=True)
        cls.e=pd.read_csv(ROOT/OUT/'evidencias_actividad.csv',dtype=str,keep_default_na=False)
    def test_d04_cero_y_vacio_no_son_inactividad(self):
        _,detail,_=regulatory_evidence(ROOT,self.p,include_unassigned=True)
        holes=detail.loc[(detail.RPJ.eq('SP0008')&detail.Ejercicio.eq(2022))|
            (detail.RPJ.eq('B40002')&detail.Ejercicio.eq(2015))|
            (detail.RPJ.eq('003058')&detail.Ejercicio.isin([2021,2022]))]
        self.assertEqual(len(holes.drop_duplicates(['RPJ','Ejercicio'])),4)
        # Cinco localizadores fuente representan cuatro pares empresa-año; Hidrandina tiene dos series históricas.
        self.assertFalse(holes.asignable_por_inversion.any())
        self.assertTrue(holes.estado_actividad.str.contains('No determinada').all())
        merged=holes.merge(self.c,on=['RPJ','Ejercicio'],validate='many_to_one')
        self.assertTrue(merged.industria_damodaran.eq('Power').all())
        self.assertTrue(merged.regla_industria.str.startswith('D03').all())
        for row in merged.itertuples():
            support=self.e.loc[self.e.evidencia_id.isin(row.evidencias_documentales.split('|'))]
            self.assertTrue(support.tipo_fuente.eq('PDF').any())
    def test_master_jerarquia_no_depende_id_ni_orden(self):
        e=self.e.loc[self.e.RPJ.eq('SP0008')&self.e.anio_referencia.eq('2024')].copy()
        self.assertIn('XLSX',set(e.tipo_fuente));self.assertIn('PDF',set(e.tipo_fuente))
        for reverse in [False,True]:
            q=e.iloc[::-1].copy() if reverse else e.copy()
            q['evidencia_id']=['ZZZ' if t=='XLSX' else 'AAA' for t in q.tipo_fuente]
            self.assertEqual(select_evidence(q,2024).tipo_fuente,'PDF')
    def test_master_vigencia_precede_documento_antiguo(self):
        q=self.e.iloc[:2].copy();q['anios_respaldados']=['2020','2025'];q['anio_referencia']=['2020','2025']
        q['clase_documental']=['EEFF individual auditado','Nota individual no auditada']
        self.assertEqual(select_evidence(q,2025).anio_referencia,'2025')
    def test_hidrandina_entidad_unica_historia_preservada(self):
        raw=pd.read_csv(ROOT/BASE/'correspondencias_minem.csv',dtype=str,keep_default_na=False)
        canonical=canonical_minem(raw,ROOT)
        self.assertEqual((len(raw),len(canonical)),(25,24));self.assertFalse(canonical.RPJ.duplicated().any())
        h=canonical.loc[canonical.RPJ.eq('B40002')].iloc[0]
        loc=json.loads(h.localizadores)
        self.assertEqual(len(loc),2);self.assertIn('Histórico anterior a 2005',{x['uso'] for x in loc})
        self.assertEqual({x['fila'] for x in loc},{35,161})
    def test_notebook_canonico_alias_compatible_y_unico(self):
        old=ROOT/'notebooks/08_clasificacion_sectorial.ipynb';canonical=ROOT/'notebooks/sprint_07/10_clasificacion_sectorial.ipynb'
        self.assertTrue(old.is_symlink());self.assertEqual(old.resolve(),canonical)
        self.assertEqual(old.read_bytes(),canonical.read_bytes())
        physical=[p for p in (ROOT/'notebooks').glob('08_*.ipynb') if not p.is_symlink()]
        self.assertEqual([p.name for p in physical],['08_mejoras_baseline.ipynb'])
    def test_muestra_no_confunde_filas_y_empresas(self):
        g=pd.DataFrame({'industria_damodaran':['Power']*80,'Moneda':['Soles']*80,'RPJ':['A']*80,
            'utilizable_supervisado':[True]*80,'particion':['entrenamiento']*60+['prueba']*20,'anio_objetivo':[2020]*60+[2024]*20})
        s=sufficiency(g).iloc[0]
        self.assertEqual(s.empresas_entrenamiento,1);self.assertEqual(s.observaciones_entrenamiento,60)
        self.assertFalse(s.muestra_suficiente_orientativa);self.assertTrue(s.muestra_insuficiente)
    def test_prioridad_solo_pendientes_elegibles_sin_metricas(self):
        t=priority_table(self.p,self.c);self.assertTrue(t.total_elegible_pendiente.is_monotonic_decreasing)
        for r in t.head(15).itertuples():
            g=self.p.loc[self.p.RPJ.eq(r.RPJ)&self.p.utilizable_supervisado]
            c=self.c.loc[self.c.RPJ.eq(r.RPJ)&self.c.industria_damodaran.isna()]
            self.assertEqual(r.total_elegible_pendiente,len(g.loc[g.Ejercicio.isin(c.Ejercicio)]))
    def test_temporal_no_usa_redaccion_de_actividad(self):
        e=pd.DataFrame({'anios_respaldados':['2020','2021'],'actividad_principal':['redacción A','redacción B']})
        c=pd.DataFrame({'industria_damodaran':['Power','Power']})
        self.assertIn('sin huecos internos',temporal_status(c,e))
    def test_ampliacion_ningun_anio_sin_respaldo(self):
        old=pd.read_csv(ROOT/'reports/sprint_07/enriquecimiento/catalogo_empresa_anio.csv',dtype={'RPJ':str})
        m=self.c.merge(old[['RPJ','Ejercicio','industria_damodaran']],on=['RPJ','Ejercicio'],suffixes=('','_f2'),validate='one_to_one')
        self.assertTrue(m.loc[m.industria_damodaran_f2.notna(),'industria_damodaran'].eq(m.loc[m.industria_damodaran_f2.notna(),'industria_damodaran_f2']).all())
        added=m.loc[m.industria_damodaran_f2.isna()&m.industria_damodaran.notna()]
        self.assertGreater(len(added),0)
        for r in added.itertuples():
            e=self.e.loc[self.e.evidencia_id.isin(r.evidencias_documentales.split('|'))]
            self.assertTrue(any(str(r.Ejercicio) in s.split('|') for s in e.anios_respaldados))
if __name__=='__main__':unittest.main()
