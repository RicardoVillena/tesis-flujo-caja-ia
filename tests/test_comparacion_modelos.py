import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import numpy as np
import pandas as pd
import src.ablacion_variables as ab
import src.auditoria_calidad as ac
import src.comparacion_modelos as cm

NOTEBOOK = cm.ROOT / 'notebooks/sprint_08/13_comparacion_modelos.ipynb'
panel = cols = train = salida = None


def setUpModule():
    global panel, cols, train, salida
    panel, cols, _ = ac.load_inputs()
    train = ab.separar_entrenamiento(panel)
    salida = tempfile.TemporaryDirectory()
    cm.run(salida.name)


def tearDownModule():
    salida.cleanup()


def leer(nombre, **kw):
    return pd.read_csv(Path(salida.name) / nombre, **kw)


class ComparisonTests(unittest.TestCase):
    def test_test_partition_isolation(self):
        alterado = panel.copy()
        m = alterado.particion.eq('prueba')
        alterado.loc[m, cols + ['FCL_preliminar', 'CAPEX_reportado']] = 1e9
        alterado.loc[m, 'objetivo_fcl_t1'] = -1e12
        dl = lambda t: t.loc[t.Moneda.eq('D lares')]
        a = cm.ejecutar(dl(train), cols, (2017,))
        b = cm.ejecutar(dl(ab.separar_entrenamiento(alterado)), cols, (2017,))
        for x, y, nombre in zip(a, b, ['pred', 'busq', 'eleg', 'tiempos', 'internos']):
            if nombre != 'tiempos':
                pd.testing.assert_frame_equal(x, y, check_exact=True)
        pred = leer('predicciones_externas.csv')
        self.assertFalse(set(pred.id_fila) & set(panel.index[panel.particion.eq('prueba')]))
        self.assertTrue(pred.anio_objetivo.between(2017, 2021).all())

    def test_internal_and_external_separation(self):
        internos = leer('pliegues_internos.csv')
        for (m, y), g in internos.groupby(['moneda', 'anio_externo']):
            self.assertEqual(sorted(g.anio_interno), [y - 3, y - 2, y - 1])
            self.assertTrue((g.anio_train_max < g.anio_interno).all())
            self.assertTrue((g.anio_train_max - 2006 + 1 >= ab.MIN_ANIOS_HISTORIA_INTERNA).all())
        t = train.loc[train.Moneda.eq('Soles') & train.anio_objetivo.lt(2019)]
        self.assertEqual([a for a, _, _ in cm.cortes_internos(t)], [f.anio for f in ab.pliegues_internos(t, cols)])

    def test_preprocessing_and_target_transform_fit_only_on_training(self):
        t = train.loc[train.Moneda.eq('D lares')]
        tr, va = t.loc[t.anio_objetivo.lt(2017)], t.loc[t.anio_objetivo.eq(2017)]
        est, conv, _, _ = cm.ajustar('elastic_net', cols, dict(alpha=0.01, l1_ratio=0.5), tr)
        self.assertTrue(conv)
        pre = est.regressor_.named_steps['preparacion'].named_transformers_['numericas']
        np.testing.assert_allclose(pre.named_steps['imputer'].statistics_, tr[cols].median().fillna(0))
        self.assertEqual(int(pre.named_steps['scaler'].n_samples_seen_), len(tr))
        y = tr.objetivo_fcl_t1.to_numpy()
        np.testing.assert_allclose(est.transformer_.mean_, [y.mean()])
        np.testing.assert_allclose(est.transformer_.scale_, [y.std()])
        p = est.predict(va[cols])
        interna = est.regressor_.predict(va[cols])
        np.testing.assert_allclose(p, interna * y.std() + y.mean(), rtol=1e-10)  # unidades originales
        va2 = va.copy()
        va2[cols] = va2[cols] * 9 + 1
        est.predict(va2[cols])
        np.testing.assert_allclose(est.transformer_.mean_, [y.mean()])

    def test_same_rows_for_all_procedures(self):
        pred = leer('predicciones_externas.csv')
        for (m, y), g in pred.groupby(['moneda', 'anio_objetivo']):
            ids = g.groupby('procedimiento').id_fila.apply(lambda s: tuple(sorted(s)))
            self.assertEqual(set(ids.index), set(cm.PROCEDIMIENTOS))
            self.assertEqual(ids.nunique(), 1)
            self.assertEqual(len(ids.iloc[0]), int((train.Moneda.eq(m) & train.anio_objetivo.eq(y)).sum()))

    def test_future_years_do_not_affect_earlier_fits(self):
        t = train.loc[train.Moneda.eq('D lares')]
        a = cm.ejecutar(t, cols, (2017, 2018))
        alt = t.copy()
        alt.loc[alt.anio_objetivo.eq(2017), 'objetivo_fcl_t1'] *= 25
        b = cm.ejecutar(alt, cols, (2017, 2018))
        p17 = lambda x: x.loc[x.anio_objetivo.eq(2017) & x.procedimiento.isin(cm.MODELOS + ('media_historica',)), 'y_predicho'].to_numpy()
        np.testing.assert_array_equal(p17(a[0]), p17(b[0]))
        pd.testing.assert_frame_equal(a[1].loc[a[1].anio_externo.eq(2017)].reset_index(drop=True), b[1].loc[b[1].anio_externo.eq(2017)].reset_index(drop=True))
        # Control positivo: 2018 entrena con 2017 perturbado.
        p18 = lambda x: x.loc[x.anio_objetivo.eq(2018) & x.procedimiento.eq('ridge'), 'y_predicho'].to_numpy()
        self.assertFalse(np.allclose(p18(a[0]), p18(b[0])))

    def test_finite_predictions_and_metrics(self):
        pred = leer('predicciones_externas.csv')
        self.assertTrue(np.isfinite(pred.y_predicho).all())
        anual = leer('metricas_por_anio.csv')
        for r in anual.sample(8, random_state=0).itertuples():
            g = pred.loc[pred.procedimiento.eq(r.procedimiento) & pred.moneda.eq(r.moneda) & pred.anio_objetivo.eq(r.anio_externo)]
            e = g.y_predicho - g.y_real
            np.testing.assert_allclose([r.RMSE, r.MAE, r.n], [np.sqrt((e ** 2).mean()), e.abs().mean(), len(g)], rtol=1e-12)
        comp = leer('comparaciones_pareadas.csv')
        np.testing.assert_allclose(comp.delta_RMSE, comp.RMSE_candidato - comp.RMSE_comparador)
        np.testing.assert_allclose(comp.delta_MAE_pct, 100 * comp.delta_MAE / comp.MAE_comparador)
        res = leer('resumen_comparaciones.csv')
        for r in res.itertuples():
            g = comp.loc[comp.moneda.eq(r.moneda) & comp.candidato.eq(r.candidato) & comp.comparador.eq(r.comparador)]
            np.testing.assert_allclose(r.delta_RMSE_anual_medio_pct, 100 * (g.RMSE_candidato.mean() - g.RMSE_comparador.mean()) / g.RMSE_comparador.mean())
            self.assertEqual(r.anios_mejora_RMSE, int(g.direccion_RMSE.eq('mejora').sum()))

    def test_references_and_ridge_reproduce_revision(self):
        verif = cm.verificar_contra_revision(leer('predicciones_externas.csv', dtype={'RPJ': 'string'}))
        self.assertEqual(set(verif), {'media_historica', 'persistencia', 'ridge'})
        self.assertTrue(all(v < 1e-9 for v in verif.values()))

    def test_convergence_and_no_random_validation(self):
        busq = leer('busquedas_internas.csv')
        eleg = leer('hiperparametros_elegidos.csv')
        self.assertTrue(busq.valida.all() and eleg.evaluado.all() and eleg.convergio_externo.all())
        self.assertLessEqual(busq.groupby(['moneda', 'anio_externo', 'modelo']).size().max(), 12)
        hgb = cm.crear('boosting', cols, cm.rejillas()['boosting'][0])
        self.assertFalse(hgb.early_stopping)
        self.assertEqual(hgb.random_state, cm.SEMILLA)
        # Control positivo: con muy pocas iteraciones se detecta la falta de convergencia.
        t = train.loc[train.Moneda.eq('D lares') & train.anio_objetivo.lt(2017)]
        with mock.patch.object(cm, 'EN_MAX_ITER', 1):
            _, conv, _, _ = cm.ajustar('elastic_net', cols, dict(alpha=0.001, l1_ratio=0.1), t)
        self.assertFalse(conv)

    def test_tie_break_prefers_simpler_configuration(self):
        grid = cm.rejillas()
        self.assertEqual(grid['ridge'][0]['alpha'], max(cm.ALPHAS_RIDGE))
        self.assertEqual(grid['elastic_net'][0], dict(alpha=max(cm.EN_ALPHAS), l1_ratio=max(cm.EN_L1)))
        self.assertEqual(grid['boosting'][0], dict(max_depth=min(cm.HGB_PROFUNDIDAD), max_iter=min(cm.HGB_ITERACIONES), l2_regularization=max(cm.HGB_L2)))
        busq = leer('busquedas_internas.csv')
        for _, g in busq.groupby(['moneda', 'anio_externo', 'modelo']):
            e = g.loc[g.elegida.astype(bool)]
            self.assertEqual(len(e), 1)
            self.assertLessEqual(float(e.rmse_interno_medio.iloc[0]), g.rmse_interno_medio.min() * (1 + cm.EMPATE_REL))

    def test_rule_and_decision(self):
        ok = dict(delta_RMSE_anual_medio_pct=-1.5, anios_mejora_RMSE=4, delta_MAE_anual_medio_pct=-0.1)
        self.assertTrue(cm.cumple_regla(ok))
        self.assertFalse(cm.cumple_regla({**ok, 'delta_RMSE_anual_medio_pct': -0.96}))
        self.assertFalse(cm.cumple_regla({**ok, 'anios_mejora_RMSE': 3}))
        self.assertFalse(cm.cumple_regla({**ok, 'delta_MAE_anual_medio_pct': 0.2}))
        dec = leer('decision.csv')
        res = leer('resumen_comparaciones.csv')
        for d in dec.itertuples():
            x = res.loc[res.moneda.eq(d.moneda) & res.candidato.eq('boosting') & res.comparador.isin(['media_historica', 'persistencia', 'ridge'])]
            self.assertEqual(d.boosting_recomendado, bool(x.cumple_regla.all()))

    def test_lowest_rmse_is_not_labeled_consistent_superiority(self):
        filas = []
        for c, k in __import__('itertools').permutations(cm.PROCEDIMIENTOS, 2):
            # boosting tiene el menor RMSE pero no cumple la regla frente a ridge; nadie cumple frente a todos.
            cumple = c == 'boosting' and k != 'ridge'
            filas.append(dict(moneda='X', candidato=c, comparador=k, anios=5, delta_RMSE_anual_medio_pct=-0.9 if (c, k) == ('boosting', 'ridge') else (-5. if cumple else 5.),
                              delta_MAE_anual_medio_pct=-1., anios_mejora_RMSE=4, cumple_regla=cumple))
        res = pd.DataFrame(filas)
        proc = pd.DataFrame(dict(moneda='X', procedimiento=list(cm.PROCEDIMIENTOS), RMSE_anual_medio=[5., 4., 3., 2.5, 1.]))
        d = cm.decision(res, proc).iloc[0]
        self.assertEqual(d.menor_RMSE_anual_medio, 'boosting')
        self.assertEqual(d.alternativa_con_superioridad_consistente, '')
        self.assertEqual(d.modelo_vigente, 'ridge')
        self.assertTrue(d.cambio_recomendado.startswith('Conservar ridge'))
        self.assertIn('no alcanza', d.motivo_decision)
        self.assertNotIn('alternativa_respaldada', cm.decision(res, proc).columns)

    def test_soles_keeps_ridge_although_boosting_has_lower_rmse(self):
        dec = leer('decision.csv', keep_default_na=False).set_index('moneda')
        s, d = dec.loc['Soles'], dec.loc['D lares']
        self.assertEqual((s.menor_RMSE_anual_medio, s.alternativa_con_superioridad_consistente, s.modelo_vigente), ('boosting', '', 'ridge'))
        self.assertTrue(s.cambio_recomendado.startswith('Conservar ridge'))
        self.assertEqual((d.menor_RMSE_anual_medio, d.alternativa_con_superioridad_consistente, d.modelo_vigente), ('persistencia', 'persistencia', 'persistencia'))
        x = leer('resumen_comparaciones.csv').query("moneda == 'Soles' and candidato == 'boosting' and comparador == 'ridge'").iloc[0]
        self.assertAlmostEqual(round(x.delta_RMSE_anual_medio_pct, 3), -0.956)
        self.assertAlmostEqual(round(x.delta_MAE_anual_medio_pct, 2), -9.80)
        self.assertEqual(x.anios_mejora_RMSE, 4)
        self.assertFalse(x.cumple_regla)
        self.assertIn('-0.956 %', s.motivo_decision)

    def test_csv_and_report_express_the_same_decision(self):
        texto = (Path(salida.name) / 'informe_comparacion.md').read_text(encoding='utf-8')
        nombres = {'ridge': 'Ridge', 'persistencia': 'persistencia', 'boosting': 'boosting'}
        for archivo in ['decision.csv', 'decision_sin_empresa_dominante.csv']:
            df = leer(archivo, keep_default_na=False)
            self.assertNotIn('alternativa_respaldada', df.columns)
            for c in ['menor_RMSE_anual_medio', 'alternativa_con_superioridad_consistente', 'modelo_vigente', 'cambio_recomendado', 'motivo_decision']:
                self.assertIn(c, df.columns)
        for r in leer('decision.csv', keep_default_na=False).itertuples():
            bloque = texto.split(f'### {r.moneda}\n')[1].split('###')[0]
            self.assertIn(f'**Modelo vigente:** {nombres[r.modelo_vigente]}', bloque)
            self.assertIn(f'**Cambio recomendado:** {r.cambio_recomendado}', bloque)
            self.assertIn(r.motivo_decision, bloque)
            self.assertIn('**Superioridad consistente frente a todos:** ' + (nombres[r.alternativa_con_superioridad_consistente] if r.alternativa_con_superioridad_consistente else 'ninguna'), bloque)
        self.assertNotIn('alternativa_respaldada', texto)
        self.assertNotIn('alternativa respaldada', texto.lower())

    def test_reproducible_outputs(self):
        with tempfile.TemporaryDirectory() as b:
            cm.run(b)
            for p in Path(salida.name).rglob('*'):
                if p.is_file() and p.name != 'tiempos_ajuste.csv':
                    self.assertEqual(p.read_bytes(), (Path(b) / p.relative_to(salida.name)).read_bytes(), p.name)
        cfg = json.loads((Path(salida.name) / 'configuracion.json').read_text())
        self.assertIn('versiones', cfg)
        self.assertEqual(cfg['maximo_configuraciones'], {'ridge': 8, 'elastic_net': 12, 'boosting': 8})

    def test_notebook_structure_and_execution(self):
        nb = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        codigo = [c for c in nb['cells'] if c['cell_type'] == 'code']
        self.assertGreater(len(codigo), 4)
        for i, c in enumerate(nb['cells']):
            if c['cell_type'] == 'code':
                previa = [x for x in ''.join(nb['cells'][i - 1]['source']).splitlines() if x.strip()]
                self.assertTrue(nb['cells'][i - 1]['cell_type'] == 'markdown' and previa[0].startswith('**'))
                self.assertFalse(any(o.get('output_type') == 'error' for o in c.get('outputs', [])))
        self.assertEqual([c['execution_count'] for c in codigo], list(range(1, len(codigo) + 1)))


if __name__ == '__main__':
    unittest.main()
