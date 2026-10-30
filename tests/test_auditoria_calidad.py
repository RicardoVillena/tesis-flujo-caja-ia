import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import numpy as np
import pandas as pd
import src.auditoria_calidad as ac
from src.auditoria_calidad import ROOT, load_inputs, diagnostics, especificacion_e2, run, training

NOTEBOOK = ROOT / 'notebooks/sprint_08/11_auditoria_calidad_atributos.ipynb'


class AuditQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d, cls.cols, cls.cat = load_inputs()
        cls.spec = especificacion_e2()
        cls.tables = diagnostics(cls.d, cls.cols)

    def test_e2_specification_and_target_integrity(self):
        self.assertEqual(len(self.cols), 26)
        self.assertEqual((len(self.spec['financieros']), len(self.spec['macroeconomicos']), len(self.spec['bursatiles'])), (19, 4, 3))
        self.assertEqual(self.cols[:3], ['pasivo_activo', 'margen_neto', 'rentabilidad_activo_cierre'])
        self.assertEqual(self.cols[-1], 'monto_renta_variable_anual_millones_pen')
        self.assertEqual(len(self.d), 4221)
        self.assertEqual(int(self.d.utilizable_supervisado.sum()), 3560)
        self.assertNotIn('objetivo_fcl_t1', self.cols)
        t = self.d.loc[self.d.utilizable_supervisado]
        self.assertEqual(t.loc[t.particion.eq('entrenamiento'), 'anio_objetivo'].agg(['min', 'max']).tolist(), [2006, 2021])
        self.assertEqual(t.loc[t.particion.eq('prueba'), 'anio_objetivo'].agg(['min', 'max']).tolist(), [2022, 2025])
        self.assertTrue(t.Moneda.eq(t.moneda_objetivo).all())

    def _perturbado(self):
        changed = self.d.copy()
        no_train = ~(changed.utilizable_supervisado & changed.particion.eq('entrenamiento'))
        changed.loc[no_train, self.cols] = 1e99
        changed.loc[no_train, 'objetivo_fcl_t1'] = -1e99
        # Montos fuente de ejercicios posteriores al último de entrenamiento (prueba y no elegibles futuras).
        futuro = changed.Ejercicio.gt(training(self.d).Ejercicio.max())
        fuente = ['ActivoTotal', 'PasivoTotal', 'TotalIngreso', 'UtilidadNeta', 'FCO', 'CAPEX_reportado', 'FCL_preliminar']
        changed.loc[futuro, fuente] = 1e9
        changed.loc[futuro, 'revision_interanual'] = ~changed.loc[futuro, 'revision_interanual'].astype(bool)
        return changed, no_train, futuro, fuente

    def test_perturbation_really_changes_test_data(self):
        changed, no_train, futuro, fuente = self._perturbado()
        prueba = self.d.particion.eq('prueba')
        self.assertTrue(prueba.sum() == 691 and no_train[prueba].all())
        for c in self.cols:
            self.assertTrue((changed.loc[prueba, c] != self.d.loc[prueba, c]).all(), c)
        self.assertTrue((changed.loc[futuro, fuente] != self.d.loc[futuro, fuente]).all().all())
        pd.testing.assert_frame_equal(training(changed), training(self.d), check_exact=True)

    def test_test_and_future_perturbation_cannot_change_diagnostics(self):
        changed, *_ = self._perturbado()
        other = diagnostics(changed, self.cols)
        for key in self.tables:
            pd.testing.assert_frame_equal(self.tables[key], other[key], check_exact=True, obj=key)

    def test_positive_control_contaminated_training_is_detected(self):
        changed, *_ = self._perturbado()
        contaminado = lambda d: d.loc[d.utilizable_supervisado].copy()
        with mock.patch.object(ac, 'training', contaminado):
            a, b = diagnostics(self.d, self.cols), diagnostics(changed, self.cols)
        self.assertFalse(a['calidad_atributos'].equals(b['calidad_atributos']))
        self.assertFalse(a['correlaciones_pearson'].equals(b['correlaciones_pearson']))

    def test_positive_control_unrestricted_history_is_detected(self):
        changed, *_ = self._perturbado()
        a, b = diagnostics(self.d, self.cols, anio_max_historia=2025), diagnostics(changed, self.cols, anio_max_historia=2025)
        self.assertFalse(a['saltos_escala_train'].equals(b['saltos_escala_train']) and a['denominadores_casos_train'].equals(b['denominadores_casos_train']))

    def test_statistics_independently(self):
        q = self.tables['calidad_atributos']
        self.assertEqual(len(q), 52)
        tr = training(self.d)
        for r in q.itertuples():
            s = tr.loc[tr.Moneda.eq(r.moneda), r.variable]
            self.assertAlmostEqual(r.faltantes_pct, 100 * s.isna().mean())
            np.testing.assert_allclose([r.media, r.mediana, r.desviacion_estandar, r.p05, r.p95],
                                       [s.mean(), s.median(), s.std(), s.quantile(.05), s.quantile(.95)], equal_nan=True)
        for method in ['pearson', 'spearman']:
            for currency, t in tr.groupby('Moneda'):
                pd.testing.assert_frame_equal(self.tables[f'correlaciones_{method}'].loc[currency],
                                              t[self.cols].corr(method=method, min_periods=3).rename_axis('variable'))

    def test_missing_causes_cover_every_missing_cell(self):
        q = self.tables['calidad_atributos']
        partes = q.faltantes_estructurales + q.faltantes_regla + q.faltantes_fuente + q.faltantes_no_explicados
        self.assertTrue(partes.eq(q.faltantes_n).all())
        self.assertEqual(int(q.faltantes_no_explicados.sum()), 0)
        cov = self.tables['cobertura_temporal_train']
        self.assertEqual((cov.anio.min(), cov.anio.max()), (2005, 2020))
        # Un rezago k no puede tener dato si la historia contigua es menor que k.
        tr = training(self.d)
        for k in (1, 2, 3):
            self.assertTrue(tr.loc[tr.historial_previo_contiguo.lt(k), f'FCO_lag{k}'].isna().all())

    def test_small_denominator_cases_are_identifiable_and_train_only(self):
        casos = self.tables['denominadores_casos_train']
        tr = training(self.d)
        claves = set(zip(tr.RPJ, tr.Ejercicio))
        self.assertTrue(len(casos) > 0 and casos[['RPJ', 'Ejercicio']].notna().all().all())
        self.assertTrue(all((r.RPJ, r.Ejercicio) in claves for r in casos.itertuples()))
        self.assertTrue((casos.valor_denominador > 0).all())
        self.assertTrue((casos.criterio_transversal | casos.criterio_intraempresa).all())
        tr_ = casos.loc[casos.criterio_transversal]
        self.assertTrue((tr_.valor_denominador <= ac.FRACCION_DENOMINADOR * tr_.mediana_positiva_moneda).all())
        fossal = casos.loc[casos.RPJ.eq('OE6928') & casos.Ejercicio.eq(2017) & casos.variable.eq('crecimiento_ActivoTotal')]
        self.assertEqual(fossal.valor_denominador.tolist(), [1])
        self.assertTrue(self.tables['saltos_escala_train'].Ejercicio.le(2020).all())

    def test_pairs_leave_one_out_and_sample_sizes(self):
        pares = self.tables['pares_correlacionados']
        tr = training(self.d)
        r = pares.loc[pares.moneda.eq('Soles') & pares.variable_1.eq('crecimiento_ActivoTotal') & pares.variable_2.eq('cambio_FCO_activo_previo')].iloc[0]
        t = tr.loc[tr.Moneda.eq('Soles'), [r.variable_1, r.variable_2, 'RPJ', 'Ejercicio']].dropna()
        self.assertEqual(r.n_pares, len(t))
        sin = t.loc[~(t.RPJ.eq(r.RPJ_influyente) & t.Ejercicio.eq(r.Ejercicio_influyente))]
        self.assertAlmostEqual(r.pearson_sin_caso_influyente, sin[r.variable_1].corr(sin[r.variable_2]), places=8)
        self.assertTrue(r.depende_de_un_caso and r.pearson > .99 and r.pearson_sin_caso_influyente < 0)
        n = self.tables['n_pares_correlacion'].loc['Soles']
        self.assertEqual(n.loc[r.variable_1, r.variable_2], len(t))
        self.assertTrue(self.tables['correlaciones_externas_anuales'].n_anios.eq(16).all())

    def test_vif_and_condition_number_match_independent_computation(self):
        v = self.tables['diagnostico_vif']
        s06 = pd.read_csv(ROOT / 'reports/sprint_06/diagnostico_colinealidad.csv').query('experimento == "E2_bursatil"').set_index('moneda')
        tr = training(self.d)
        for moneda, t in tr.groupby('Moneda'):
            x = t[self.cols]
            z = x.fillna(x.median().fillna(0))
            inv = np.diag(np.linalg.inv(np.corrcoef(z.to_numpy(float), rowvar=False)))
            g = v.loc[v.moneda.eq(moneda) & v.especificacion.eq('imputada_mediana_E2')].set_index('variable').loc[self.cols]
            np.testing.assert_allclose(g.VIF, inv, rtol=1e-6)
            self.assertEqual(int(g.rango.iloc[0]), int(s06.loc[moneda, 'rango']))
            np.testing.assert_allclose(g.numero_condicion.iloc[0], s06.loc[moneda, 'numero_condicion'], rtol=1e-8)
        deps = self.tables['dependencias_lineales']
        self.assertFalse(deps.tipo.str.contains('exacta|duplicad').any())

    def test_temporal_classification_rules(self):
        t = run_tables['auditoria_temporal'].set_index('variable')
        self.assertTrue(t.clasificacion.isin(ac.CATEGORIAS_TEMPORALES).all())
        # Sin fechas de publicación ni vintages en el repositorio, nada puede certificarse.
        self.assertFalse(t.clasificacion.eq('DISPONIBILIDAD VERIFICADA').any())
        for v in self.cols:
            tipo = ac.tipo_atributo(v)['tipo']
            esperado = ('POSIBLE FUGA TEMPORAL' if tipo in {'ratio', 'crecimiento', 'cambio'} or v == 'crecimiento_pbi_real_pct'
                        else 'DISPONIBILIDAD NO VERIFICADA')
            self.assertEqual(t.loc[v, 'clasificacion'], esperado, v)
        for c in ['anio_referencia', 'fecha_publicacion', 'vintage', 'fecha_pronostico']:
            self.assertTrue(t[c].astype(str).str.len().gt(0).all())

    def test_dictionary_evidence_is_locatable(self):
        dic = run_tables['diccionario_atributos']
        self.assertEqual(dic.nombre.tolist(), self.cols)
        for r in dic.itertuples():
            for ref in r.evidencia.split('; '):
                ruta = ref.split(':')[0].split(' celda')[0]
                self.assertTrue((ROOT / ruta).exists(), ref)
                if ':' in ref:
                    linea = int(ref.split(':')[1])
                    texto = (ROOT / ruta).read_text(encoding='utf-8-sig').splitlines()[linea - 1]
                    self.assertTrue(r.nombre in texto or bool(r.codigo_serie) and r.codigo_serie in texto or "f'" in texto, ref)

    def test_findings_and_summary_separate_proven_from_suspected(self):
        h = run_tables['hallazgos_calidad']
        self.assertTrue(set(h.estado) == {'COMPROBADO', 'SOSPECHA PENDIENTE'})
        texto = (Path(run_dir.name) / 'resumen_auditoria.md').read_text(encoding='utf-8')
        comp, sosp = texto.index('## 4. Problemas comprobados'), texto.index('## 5. Sospechas pendientes')
        for r in h.itertuples():
            pos = texto.index(f'**{r.id} ')
            self.assertTrue(comp < pos < sosp if r.estado == 'COMPROBADO' else pos > sosp, r.id)
        rec = run_tables['tabla_26_atributos'].recomendacion
        self.assertEqual(len(rec), 26)
        self.assertFalse(rec.str.contains('Eliminar|eliminar').any())

    def test_reproducible_outputs(self):
        with tempfile.TemporaryDirectory() as b:
            run(b)
            for p in Path(run_dir.name).iterdir():
                self.assertEqual(p.read_bytes(), (Path(b) / p.name).read_bytes(), p.name)

    def test_prior_files_intact_against_head_and_pre_edit_reference(self):
        r = ac.verificar_integridad()
        self.assertEqual(r['modificados'], [])
        self.assertEqual(r['ausentes'], [])
        self.assertEqual(r['nuevos_fuera_de_sprint08'], [])
        if r['git_head'] is not None:
            self.assertEqual(r['git_rastreados_modificados'], [])
        manifest = json.loads((Path(run_dir.name) / 'integridad.json').read_text())
        self.assertTrue(manifest['sin_cambios_durante_ejecucion'])

    def test_notebook_structure_and_execution(self):
        nb = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        codigo = [c for c in nb['cells'] if c['cell_type'] == 'code']
        self.assertGreater(len(codigo), 5)
        for i, c in enumerate(nb['cells']):
            if c['cell_type'] == 'code':
                previous = nb['cells'][i - 1]
                self.assertEqual(previous['cell_type'], 'markdown')
                lineas = [x for x in ''.join(previous['source']).splitlines() if x.strip()]
                self.assertTrue(lineas[0].startswith('**') and lineas[0].endswith('**'))
                self.assertLessEqual(len(lineas), 3)
                self.assertFalse(any(o.get('output_type') == 'error' for o in c.get('outputs', [])))
        self.assertEqual([c['execution_count'] for c in codigo], list(range(1, len(codigo) + 1)))


run_dir, run_tables = None, None


def setUpModule():
    global run_dir, run_tables
    run_dir = tempfile.TemporaryDirectory()
    run_tables = run(run_dir.name)


def tearDownModule():
    run_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
