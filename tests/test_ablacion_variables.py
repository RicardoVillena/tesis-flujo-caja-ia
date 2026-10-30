import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import src.ablacion_variables as ab
import src.auditoria_calidad as ac

NOTEBOOK = ab.ROOT / 'notebooks/sprint_08/12_ablacion_variables.ipynb'
panel = cols = train = base = salida = revision = None


def _hashes(carpeta):
    import hashlib
    return {p.relative_to(carpeta).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(carpeta.rglob('*')) if p.is_file()}


def setUpModule():
    global panel, cols, train, base, salida, revision
    panel, cols, _ = ac.load_inputs()
    train = ab.separar_entrenamiento(panel)
    base = ab.ejecutar(train, cols)
    salida = tempfile.TemporaryDirectory()
    ab.run(salida.name)
    revision = tempfile.TemporaryDirectory()
    antes = _hashes(ab.OUT)
    ab.run_revision(revision.name)
    assert _hashes(ab.OUT) == antes, 'la revisión alteró los resultados anteriores'


def tearDownModule():
    salida.cleanup()
    revision.cleanup()


class AblationTests(unittest.TestCase):
    def test_only_training_rows_enter_training_or_validation(self):
        pred, ajustes, folds = base
        prueba = set(panel.index[panel.particion.eq('prueba')])
        self.assertTrue(train.particion.eq('entrenamiento').all() and train.anio_objetivo.max() == 2021 and len(train) == 2869)
        self.assertFalse(prueba & set(pred.id_fila))
        for lista in folds.values():
            for f in lista:
                self.assertFalse(prueba & set(f['idx_train']) | prueba & set(f['idx_validacion']))
        self.assertTrue(pred.anio_objetivo.between(2014, 2021).all())

    def test_test_perturbation_does_not_change_results_and_contamination_is_rejected(self):
        alterado = panel.copy()
        m = alterado.particion.eq('prueba')
        alterado.loc[m, cols] = alterado.loc[m, cols] * 100 + 1e6
        alterado.loc[m, 'objetivo_fcl_t1'] = -1e12
        self.assertTrue((alterado.loc[m, 'objetivo_fcl_t1'] != panel.loc[m, 'objetivo_fcl_t1']).all())
        pred2, _, _ = ab.ejecutar(ab.separar_entrenamiento(alterado), cols)
        pd.testing.assert_frame_equal(pred2, base[0], check_exact=True)
        # Control positivo: un conjunto que incluya prueba es rechazado antes de ajustar.
        contaminado = alterado.loc[alterado.utilizable_supervisado].copy()
        contaminado['id_fila'] = contaminado.index
        with self.assertRaises(AssertionError):
            ab.ejecutar(contaminado, cols)
        # Si las filas de prueba perturbadas se colaran en el entrenamiento (como años antiguos), las mismas
        # filas de validación recibirían otras predicciones: la perturbación es detectable.
        extra = contaminado.loc[contaminado.particion.eq('prueba')].assign(particion='entrenamiento', anio_objetivo=2010)
        pred3, _, _ = ab.ejecutar(pd.concat([ab.separar_entrenamiento(panel), extra]), cols)
        pd.testing.assert_frame_equal(pred3[['variante', 'moneda', 'id_fila']], base[0][['variante', 'moneda', 'id_fila']])
        self.assertFalse(np.allclose(pred3.y_predicho, base[0].y_predicho))

    def test_training_precedes_validation_and_folds_match_sprint06(self):
        pred, ajustes, folds = base
        self.assertTrue((ajustes.anio_train_max < ajustes.anio_validacion_min).all())
        for lista in folds.values():
            self.assertEqual([f['anios_validacion'] for f in lista], [[2014, 2015], [2016, 2017], [2018, 2019], [2020, 2021]])
            for f in lista:
                self.assertEqual(f['anios_train'], list(range(2006, f['anios_validacion'][0])))
        tpl = pd.read_csv(Path(salida.name) / 'pliegues.csv')
        s06 = pd.read_csv(ab.ROOT / 'reports/sprint_06/mejoras/cv_folds.csv').query('grupo == "todas"')[['moneda', 'fold', 'n_train', 'n_validacion']].drop_duplicates()
        pd.testing.assert_frame_equal(tpl.loc[tpl.evaluable, ['moneda', 'fold', 'n_train', 'n_validacion']].reset_index(drop=True),
                                      s06.sort_values(['moneda', 'fold']).reset_index(drop=True), check_dtype=False)

    def test_imputation_and_scaling_fit_only_on_fold_training(self):
        f = ab.pliegues(train)['Soles'][0]
        tr, va = train.loc[f['idx_train']], train.loc[f['idx_validacion']]
        modelo, p = ab.ajustar_y_predecir(tr, va, cols)
        num = modelo.named_steps['preparacion'].named_transformers_['numericas']
        np.testing.assert_allclose(num.named_steps['imputer'].statistics_, tr[cols].median().fillna(0))
        juntas = pd.concat([tr, va])[cols].median().fillna(0).to_numpy()
        self.assertFalse(np.allclose(num.named_steps['imputer'].statistics_, juntas))
        self.assertEqual(int(num.named_steps['scaler'].n_samples_seen_), len(tr))
        va2 = va.copy()
        va2[cols] = va2[cols] * 7 + 3
        modelo2, _ = ab.ajustar_y_predecir(tr, va2, cols)
        n2 = modelo2.named_steps['preparacion'].named_transformers_['numericas']
        np.testing.assert_array_equal(num.named_steps['scaler'].mean_, n2.named_steps['scaler'].mean_)
        np.testing.assert_array_equal(modelo.named_steps['ridge'].coef_, modelo2.named_steps['ridge'].coef_)

    def test_same_validation_rows_for_every_variant(self):
        pred = pd.read_csv(Path(salida.name) / 'predicciones_validacion.csv')
        for moneda, g in pred.groupby('moneda'):
            conjuntos = g.groupby('variante').id_fila.apply(lambda s: tuple(sorted(s)))
            self.assertEqual(conjuntos.nunique(), 1, moneda)
            ys = g.groupby('variante').apply(lambda x: tuple(x.sort_values('id_fila').y_real))
            self.assertEqual(ys.nunique(), 1)

    def test_each_ablation_removes_exactly_its_attribute(self):
        v = ab.variantes(cols)
        self.assertEqual(len(v), 27)
        self.assertEqual(v[ab.REFERENCIA][1], cols)
        for c in cols:
            retirado, columnas = v[f'sin_{c}']
            self.assertEqual(retirado, c)
            self.assertEqual(set(cols) - set(columnas), {c})
            self.assertEqual(columnas, [x for x in cols if x != c])
        aj = base[1]
        self.assertTrue(aj.loc[aj.variante.ne(ab.REFERENCIA), 'n_predictores'].eq(25).all())
        f = ab.pliegues(train)['D lares'][0]
        modelo, _ = ab.ajustar_y_predecir(train.loc[f['idx_train']], train.loc[f['idx_validacion']], v['sin_FCO_lag1'][1])
        self.assertNotIn('FCO_lag1', modelo.named_steps['preparacion'].feature_names_in_)

    def test_metrics_and_sign_of_differences(self):
        m = pd.read_csv(Path(salida.name) / 'metricas_por_variante_anio.csv')
        pred = pd.read_csv(Path(salida.name) / 'predicciones_validacion.csv')
        r = m.iloc[17]
        g = pred.loc[pred.variante.eq(r.variante) & pred.moneda.eq(r.moneda) & pred.anio_objetivo.eq(r.anio_validacion)]
        e = g.y_predicho - g.y_real
        self.assertEqual(r.n, len(g))
        np.testing.assert_allclose([r.RMSE, r.MAE], [np.sqrt((e ** 2).mean()), e.abs().mean()], rtol=1e-12)
        sint = pd.DataFrame({'variante': [ab.REFERENCIA, 'sin_x', ab.REFERENCIA, 'sin_x'], 'atributo_retirado': ['', 'x', '', 'x'],
                             'moneda': ['S'] * 4, 'fold': [1] * 4, 'anio_validacion': [2014, 2014, 2015, 2015], 'n': [3] * 4,
                             'RMSE': [10., 8., 0., 1.], 'MAE': [5., 6., 0., 0.]})
        c = ab.comparaciones(sint).set_index('anio_validacion')
        self.assertEqual(c.loc[2014, 'delta_RMSE'], -2.)
        self.assertEqual(c.loc[2014, 'delta_RMSE_pct'], -20.)
        self.assertEqual(c.loc[2014, 'direccion_RMSE'], 'mejora')
        self.assertEqual(c.loc[2014, 'direccion_MAE'], 'empeora')
        self.assertTrue(np.isnan(c.loc[2015, 'delta_RMSE_pct']))
        self.assertEqual(c.loc[2015, 'direccion_MAE'], 'empate')
        comp = pd.read_csv(Path(salida.name) / 'comparaciones_pareadas.csv')
        np.testing.assert_allclose(comp.delta_RMSE, comp.RMSE_sin_variable - comp.RMSE_referencia)
        np.testing.assert_allclose(comp.delta_MAE_pct, 100 * (comp.MAE_sin_variable - comp.MAE_referencia) / comp.MAE_referencia)

    def test_classification_rule(self):
        base_r = dict(anios_evaluables=8, delta_RMSE_medio_pct=-5., anios_mejora_RMSE=6, anios_empeora_RMSE=2, anios_empate_RMSE=0,
                      mediana_delta_RMSE_anual=-1., delta_MAE_medio_pct=-1.)
        self.assertEqual(ab.clasificar(base_r)[0], 'Candidata a retirar')
        self.assertEqual(ab.clasificar({**base_r, 'anios_mejora_RMSE': 5})[0], 'Resultado incierto')
        self.assertEqual(ab.clasificar({**base_r, 'delta_RMSE_medio_pct': -0.5})[0], 'Resultado incierto')
        clase, motivo = ab.clasificar({**base_r, 'delta_MAE_medio_pct': 2.})
        self.assertEqual(clase, 'Resultado incierto')
        self.assertIn('conflicto', motivo)
        malo = {**base_r, 'delta_RMSE_medio_pct': 4., 'anios_mejora_RMSE': 1, 'anios_empeora_RMSE': 7, 'mediana_delta_RMSE_anual': 2., 'delta_MAE_medio_pct': .5}
        self.assertEqual(ab.clasificar(malo)[0], 'Conservar')
        res = pd.read_csv(Path(salida.name) / 'resumen_ablacion.csv')
        self.assertEqual(len(res), 52)
        self.assertTrue(res.clasificacion.isin(['Candidata a retirar', 'Conservar', 'Resultado incierto']).all())

    def test_joint_removal_uses_same_rows_and_reference(self):
        conj = pd.read_csv(Path(salida.name) / 'retirada_conjunta.csv')
        res = pd.read_csv(Path(salida.name) / 'resumen_ablacion.csv')
        pred = pd.read_csv(Path(salida.name) / 'predicciones_validacion.csv')
        for r in conj.itertuples():
            cand = sorted(res.loc[res.moneda.eq(r.moneda) & res.clasificacion.eq('Candidata a retirar'), 'atributo_retirado'])
            self.assertEqual(sorted(r.atributo_retirado.split(';')), cand)
            g = pred.loc[pred.moneda.eq(r.moneda)]
            self.assertEqual(set(g.loc[g.variante.eq(r.variante), 'id_fila']), set(g.loc[g.variante.eq(ab.REFERENCIA), 'id_fila']))

    def test_reference_replicates_sprint06_and_outputs_reproducible(self):
        rep = ab.verificar_replica_sprint06(train, cols)
        self.assertTrue(all(v < 1e-9 for v in rep.values()))
        with tempfile.TemporaryDirectory() as b:
            ab.run(b)
            for p in Path(salida.name).rglob('*'):
                if p.is_file():
                    self.assertEqual(p.read_bytes(), (Path(b) / p.relative_to(salida.name)).read_bytes(), p.name)
        cfg = json.loads((Path(salida.name) / 'configuracion.json').read_text())
        self.assertEqual(cfg['atributos_E2'], cols)
        self.assertEqual(cfg['clasificacion']['umbral_practico_pct_exploratorio'], 1.0)

    def test_fast_inner_ridge_equals_fresh_pipeline(self):
        t = train.loc[train.Moneda.eq('Soles')]
        tr, va = t.loc[t.anio_objetivo.lt(2016)], t.loc[t.anio_objetivo.eq(2016)]
        f = ab.PliegueInterno(tr, va, cols, 2016)
        rng = np.random.default_rng(0)
        for _ in range(3):
            sub = [c for c in cols if rng.random() < .7]
            rapidos = f.rmse(sub)
            for k, a in enumerate(ab.ALPHAS):
                p = ab.crear_modelo(sub, a).fit(tr[sub], tr.objetivo_fcl_t1).predict(va[sub])
                np.testing.assert_allclose(rapidos[k], np.sqrt(np.mean((p - va.objetivo_fcl_t1.to_numpy()) ** 2)), rtol=1e-8)

    def test_nested_internal_and_external_separation(self):
        internos = pd.read_csv(Path(salida.name) / 'anidada_pliegues_internos.csv')
        externos = pd.read_csv(Path(salida.name) / 'anidada_pliegues_externos.csv')
        for (m, y), g in internos.groupby(['moneda', 'anio_externo']):
            self.assertEqual(sorted(g.anio_interno), [y - 3, y - 2, y - 1])
            self.assertTrue((g.anios_train.str.split('-').str[1].astype(int) < g.anio_interno).all())
            self.assertTrue((g.anios_train.str.split('-').str[1].astype(int) - 2006 + 1 >= ab.MIN_ANIOS_HISTORIA_INTERNA).all())
        self.assertEqual(sorted(externos.anio_externo.unique()), list(ab.ANIOS_EXTERNOS))
        pred = pd.read_csv(Path(salida.name) / 'anidada_predicciones_externas.csv')
        self.assertTrue(pred.anio_objetivo.between(2017, 2021).all())
        for (m, y), g in pred.groupby(['moneda', 'anio_objetivo']):
            ids = g.groupby('procedimiento').id_fila.apply(lambda s: tuple(sorted(s)))
            self.assertEqual(ids.nunique(), 1)
            self.assertEqual(len(ids.iloc[0]), int(train.loc[train.Moneda.eq(m) & train.anio_objetivo.eq(y)].shape[0]))

    def test_future_years_do_not_change_past_selections(self):
        t = train.loc[train.Moneda.eq('D lares')]
        a = ab.ejecutar_anidada(t, cols, (2017, 2018, 2019))
        alterado = t.copy()
        futuro = alterado.anio_objetivo.ge(2019)
        alterado.loc[futuro, cols] = alterado.loc[futuro, cols] * -50 + 7
        alterado.loc[futuro, 'objetivo_fcl_t1'] = alterado.loc[futuro, 'objetivo_fcl_t1'] * 30
        b = ab.ejecutar_anidada(alterado, cols, (2017, 2018, 2019))
        pasado = lambda df, col: df.loc[df[col].lt(2019)].reset_index(drop=True)
        pd.testing.assert_frame_equal(pasado(a[0], 'anio_objetivo'), pasado(b[0], 'anio_objetivo'), check_exact=True)
        pd.testing.assert_frame_equal(pasado(a[1], 'anio_externo'), pasado(b[1], 'anio_externo'), check_exact=True)
        pd.testing.assert_frame_equal(pasado(a[3], 'anio_externo'), pasado(b[3], 'anio_externo'), check_exact=True)
        # Control positivo: el año externo 2019 sí usa los datos perturbados.
        self.assertFalse(np.allclose(a[0].loc[a[0].anio_objetivo.eq(2019), 'y_predicho'], b[0].loc[b[0].anio_objetivo.eq(2019), 'y_predicho']))

    def test_nested_ignores_test_partition(self):
        alterado = panel.copy()
        m = alterado.particion.eq('prueba')
        alterado.loc[m, cols] = 1e9
        alterado.loc[m, 'objetivo_fcl_t1'] = -1e12
        t1 = ab.separar_entrenamiento(alterado)
        a = ab.ejecutar_anidada(train.loc[train.Moneda.eq('D lares')], cols, (2017,))
        b = ab.ejecutar_anidada(t1.loc[t1.Moneda.eq('D lares')], cols, (2017,))
        for x, y in zip(a, b):
            pd.testing.assert_frame_equal(x, y, check_exact=True)

    def test_backward_elimination_consistent_with_history(self):
        hist = pd.read_csv(Path(salida.name) / 'anidada_historial_seleccion.csv', keep_default_na=False)
        sel = pd.read_csv(Path(salida.name) / 'anidada_pliegues_externos.csv', keep_default_na=False)
        for r in sel.itertuples():
            h = hist.loc[hist.moneda.eq(r.moneda) & hist.anio_externo.astype(str).eq(str(r.anio_externo))]
            aceptados = h.loc[h.paso.astype(int).gt(0) & h.aceptado.astype(str).eq('True'), 'atributo_evaluado'].tolist()
            self.assertEqual(sorted(aceptados), sorted([x for x in r.retirados.split(';') if x]))
            self.assertEqual(r.n_atributos_reducido, 26 - len(aceptados))
            self.assertLessEqual(len(aceptados), ab.MAX_RETIRADAS)
            for paso, g in h.loc[h.paso.astype(int).gt(0)].groupby('paso'):
                self.assertEqual(int(g.elegido.astype(str).eq('True').sum()), 1)
                elegido = g.loc[g.elegido.astype(str).eq('True')].iloc[0]
                self.assertAlmostEqual(float(elegido.rmse_interno_medio), g.rmse_interno_medio.astype(float).min())
                if elegido.aceptado == 'True':
                    self.assertGreaterEqual(float(elegido.mejora_pct), ab.UMBRAL_SELECCION_PCT)
                    self.assertGreaterEqual(int(float(elegido.anios_internos_mejora)), ab.MIN_ANIOS_INTERNOS_MEJORA)

    def test_nested_metrics_and_paired_differences(self):
        pred = pd.read_csv(Path(salida.name) / 'anidada_predicciones_externas.csv')
        pares = pd.read_csv(Path(salida.name) / 'anidada_comparaciones_pareadas.csv')
        res = pd.read_csv(Path(salida.name) / 'anidada_resumen.csv')
        for r in pares.itertuples():
            g = pred.loc[pred.procedimiento.eq(r.procedimiento) & pred.moneda.eq(r.moneda) & pred.anio_objetivo.eq(r.anio_externo)]
            c = pred.loc[pred.procedimiento.eq('completo_alpha_interno') & pred.moneda.eq(r.moneda) & pred.anio_objetivo.eq(r.anio_externo)]
            rm = lambda x: np.sqrt(np.mean((x.y_predicho - x.y_real) ** 2))
            np.testing.assert_allclose([r.RMSE, r.RMSE_completo, r.delta_RMSE], [rm(g), rm(c), rm(g) - rm(c)], rtol=1e-10)
        for r in res.loc[res.procedimiento.eq('reducido')].itertuples():
            p = pares.loc[pares.procedimiento.eq('reducido') & pares.moneda.eq(r.moneda)]
            completo = res.loc[res.procedimiento.eq('completo_alpha_interno') & res.moneda.eq(r.moneda)].iloc[0]
            np.testing.assert_allclose(r.delta_RMSE_anual_medio_pct, 100 * (r.RMSE_anual_medio - completo.RMSE_anual_medio) / completo.RMSE_anual_medio)
            self.assertAlmostEqual(r.peor_empeoramiento_anual_RMSE_pct, p.delta_RMSE_pct.max())
            self.assertIn(r.recomendacion, ['Reducir (provisional; requiere evaluación posterior)', 'Conservar modelo completo', 'Evidencia insuficiente'])
        self.assertEqual(ab.recomendar(dict(delta_RMSE_anual_medio_pct=-3., anios_mejora_RMSE=4, delta_MAE_anual_medio_pct=-1., peor_empeoramiento_anual_RMSE_pct=2.,
                                            anios_empeora_RMSE=1, anios_externos=5))[:7], 'Reducir')
        self.assertEqual(ab.recomendar(dict(delta_RMSE_anual_medio_pct=.5, anios_mejora_RMSE=1, delta_MAE_anual_medio_pct=0., peor_empeoramiento_anual_RMSE_pct=6.,
                                            anios_empeora_RMSE=1, anios_externos=5)), 'Conservar modelo completo')

    def test_admissible_choice_skips_unstable_best_candidate(self):
        ev = dict(rmse_medio=100., rmse_anual=np.array([100., 100., 100.]))
        candidatos = [('a', dict(rmse_medio=95., rmse_anual=np.array([40., 140., 105.]))),   # mejor RMSE, mejora solo 1 de 3 años
                      ('b', dict(rmse_medio=97., rmse_anual=np.array([97., 97., 97.]))),     # mejora 3 %, 3 de 3 años: admisible
                      ('c', dict(rmse_medio=99.5, rmse_anual=np.array([99.5, 99.5, 99.5])))]  # estable pero mejora 0,5 %
        orden = ['a', 'b', 'c']
        k, filas, motivo = ab.elegir_retirada(ev, candidatos, orden, 'mejor_admisible')
        self.assertEqual(candidatos[k][0], 'b')
        self.assertEqual([f['admisible'] for f in filas], [False, True, False])
        self.assertEqual(motivo, '')
        k1, _, motivo1 = ab.elegir_retirada(ev, candidatos, orden, 'mejor_rmse')
        self.assertIsNone(k1)  # defecto de la versión original: se detiene aunque 'b' sea admisible
        self.assertIn('no es admisible', motivo1)
        k2, _, motivo2 = ab.elegir_retirada(ev, candidatos[:1] + candidatos[2:], orden, 'mejor_admisible')
        self.assertIsNone(k2)
        self.assertIn('ninguna', motivo2)

    def test_revision_selection_history_and_grid(self):
        d = Path(revision.name)
        cfg = json.loads((d / 'configuracion.json').read_text())
        self.assertEqual(cfg['rejilla_alpha'], list(ab.ALPHAS_REVISION))
        self.assertIn('EXPLORATORIA', cfg['caracter'])
        sel = pd.read_csv(d / 'pliegues_externos.csv', keep_default_na=False)
        self.assertTrue(sel.alpha_completo.isin(ab.ALPHAS_REVISION).all() and sel.alpha_reducido.isin(ab.ALPHAS_REVISION).all())
        hist = pd.read_csv(d / 'historial_seleccion.csv', keep_default_na=False)
        for r in sel.itertuples():
            h = hist.loc[hist.moneda.eq(r.moneda) & hist.anio_externo.astype(str).eq(str(r.anio_externo)) & hist.paso.astype(int).gt(0)]
            for paso, g in h.groupby('paso'):
                adm = g.loc[g.admisible.astype(str).eq('True')]
                eleg = g.loc[g.elegido.astype(str).eq('True')]
                if len(adm):
                    self.assertEqual(len(eleg), 1)
                    self.assertAlmostEqual(float(eleg.rmse_interno_medio.iloc[0]), adm.rmse_interno_medio.astype(float).min())
                else:
                    self.assertEqual(len(eleg), 0)
                    self.assertTrue(g.motivo.str.startswith('parada').any())
            aceptados = h.loc[h.aceptado.astype(str).eq('True'), 'atributo_evaluado'].tolist()
            self.assertEqual(sorted(aceptados), sorted(x for x in r.retirados.split(';') if x))
            self.assertTrue(r.motivo_parada)
        dec = pd.read_csv(d / 'decision_final.csv')
        tope = max(ab.ALPHAS_REVISION)
        for r in dec.itertuples():
            g = sel.loc[sel.moneda.eq(r.moneda)]
            f = pd.read_csv(d / 'lista_final_propuesta.csv').query('moneda == @r.moneda').iloc[0]
            esperado = int((g.alpha_completo == tope).sum() + (g.alpha_reducido == tope).sum() + (f.alpha_completo == tope) + (f.alpha_reducido == tope))
            self.assertEqual(r.selecciones_alpha_en_maximo, esperado)

    def test_simple_references_and_fcl_t_definition(self):
        fcl = ab.fcl_t(panel)
        prev = panel[['RPJ', 'Ejercicio', 'objetivo_fcl_t1']].assign(Ejercicio=lambda x: x.Ejercicio + 1)
        m = panel[['RPJ', 'Ejercicio']].assign(fcl=fcl.to_numpy()).merge(prev, on=['RPJ', 'Ejercicio'])
        np.testing.assert_array_equal(m.fcl.to_numpy(), m.objetivo_fcl_t1.to_numpy())
        self.assertFalse(np.allclose(panel.FCL_preliminar_lag1, fcl, equal_nan=True))
        pred = pd.read_csv(Path(revision.name) / 'predicciones_externas.csv', dtype={'RPJ': 'string'})
        t = train.set_index('id_fila')
        for (mo, y), g in pred.groupby(['moneda', 'anio_objetivo']):
            ids = g.groupby('procedimiento').id_fila.apply(lambda s: tuple(sorted(s)))
            self.assertEqual(ids.nunique(), 1)
            self.assertEqual(set(g.procedimiento), set(ab.PROCEDIMIENTOS) | set(ab.REFERENCIAS_SIMPLES))
            media = train.loc[train.Moneda.eq(mo) & train.anio_objetivo.lt(y), 'objetivo_fcl_t1'].mean()
            np.testing.assert_allclose(g.loc[g.procedimiento.eq('media_historica'), 'y_predicho'], media, rtol=1e-12)
            p = g.loc[g.procedimiento.eq('persistencia')].set_index('id_fila')
            valor = ab.fcl_t(t.loc[p.index])
            np.testing.assert_allclose(p.y_predicho, valor.fillna(media), rtol=1e-12)
            self.assertTrue((p.usa_respaldo_media.astype(bool) == valor.isna()).all())
        resp = pd.read_csv(Path(revision.name) / 'respaldo_persistencia.csv')
        self.assertEqual(int(resp.filas.sum()), len(pred.loc[pred.procedimiento.eq('persistencia')]))

    def test_revision_ignores_test_partition_and_future(self):
        alterado = panel.copy()
        m = alterado.particion.eq('prueba')
        alterado.loc[m, cols + ['FCL_preliminar', 'CAPEX_reportado']] = 1e9
        alterado.loc[m, 'objetivo_fcl_t1'] = -1e12
        a = ab.ejecutar_anidada(train.loc[train.Moneda.eq('D lares')], cols, (2017, 2018), revision=True)
        b = ab.ejecutar_anidada(ab.separar_entrenamiento(alterado).query("Moneda == 'D lares'"), cols, (2017, 2018), revision=True)
        for x, y in zip(a, b):
            pd.testing.assert_frame_equal(x, y, check_exact=True)
        fut = train.loc[train.Moneda.eq('D lares')].copy()
        # Perturbar los objetivos de 2017 no puede cambiar las predicciones ni la selección de 2017 (entrenan con < 2017),
        # pero sí las de 2018, que entrenan con 2017 (control positivo).
        f = fut.anio_objetivo.eq(2017)
        fut.loc[f, 'objetivo_fcl_t1'] *= 25
        c = ab.ejecutar_anidada(fut, cols, (2017, 2018), revision=True)
        np.testing.assert_array_equal(a[0].loc[a[0].anio_objetivo.eq(2017), 'y_predicho'], c[0].loc[c[0].anio_objetivo.eq(2017), 'y_predicho'])
        pd.testing.assert_frame_equal(a[3].loc[a[3].anio_externo.eq(2017)].reset_index(drop=True), c[3].loc[c[3].anio_externo.eq(2017)].reset_index(drop=True))
        self.assertFalse(np.allclose(a[0].loc[a[0].anio_objetivo.eq(2018), 'y_predicho'], c[0].loc[c[0].anio_objetivo.eq(2018), 'y_predicho']))

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
