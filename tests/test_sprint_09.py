import json
import unittest
import numpy as np
import pandas as pd
import src.ablacion_variables as ab
import src.auditoria_calidad as ac
import src.comparacion_modelos as cm
import src.variantes_importancia as vi

OUT = vi.OUT
panel = train = None


def setUpModule():
    global panel, train
    panel, _, _ = ac.load_inputs()
    train = ab.separar_entrenamiento(panel)


def leer(nombre, **kw):
    return pd.read_csv(OUT / nombre, **kw)


class Sprint09Tests(unittest.TestCase):
    def test_protocol_is_the_versioned_one(self):
        self.assertEqual(json.loads((OUT / 'protocolo.json').read_text(encoding='utf-8')), json.loads(json.dumps(vi.protocolo(), ensure_ascii=False)))
        v = vi.variantes()
        b = vi.bloques()
        self.assertEqual((len(v['E0']), len(v['E1']), len(v['E2']), len(v['E3'])), (19, 23, 26, 22))
        self.assertEqual(v['E3'], b['financiero'] + b['bursatil'])

    def test_same_rows_for_all_procedures_and_years(self):
        p = leer('predicciones.csv')
        self.assertTrue(p.anio_objetivo.between(2017, 2021).all())
        self.assertFalse(set(p.id_fila) & set(panel.index[panel.particion.eq('prueba')]))
        procs = {f'{m}:{v}' for m in vi.MODELOS for v in ['E0', 'E1', 'E2', 'E3', 'E4', *vi.SENSIBILIDAD]} | set(vi.REFERENCIAS)
        for (m, y), g in p.groupby(['moneda', 'anio_objetivo']):
            self.assertEqual(set(g.procedimiento), procs)
            filas = g.groupby('procedimiento').apply(lambda x: tuple(x.sort_values('id_fila')[['id_fila', 'y_real']].itertuples(index=False)))
            self.assertEqual(filas.nunique(), 1)
            self.assertEqual(len(filas.iloc[0]), int((train.Moneda.eq(m) & train.anio_objetivo.eq(y)).sum()))
        self.assertTrue(np.isfinite(p.y_predicho).all())

    def test_temporal_separation_of_folds_and_searches(self):
        i = leer('pliegues_internos.csv')
        self.assertTrue((i.anio_train_max < i.anio_interno).all() and (i.anio_interno < i.anio_externo).all())
        b = leer('busquedas_internas.csv')
        anios = [c for c in b.columns if c.startswith('rmse_') and c[5:].isdigit()]
        for c in anios:
            self.assertTrue((b.loc[b[c].notna(), 'anio_externo'] > int(c[5:])).all(), c)
        for (m, y, mo, v), g in b.groupby(['moneda', 'anio_externo', 'modelo', 'variante']):
            self.assertLessEqual(len(g), 8)
            self.assertEqual(int(g.elegida.astype(bool).sum()), 1)

    def test_e4_selection_ignores_future_and_test_data(self):
        t = train.loc[train.Moneda.eq('D lares')]
        cols = vi.variantes()['E2']
        pasado = t.loc[t.anio_objetivo.lt(2018)]
        a = vi.seleccionar_e4('ridge', pasado, cols, dict(moneda='D lares', anio_externo=2018))
        alterado = t.copy()
        fut = alterado.anio_objetivo.ge(2018)
        alterado.loc[fut, cols] = alterado.loc[fut, cols] * -40 + 3
        alterado.loc[fut, 'objetivo_fcl_t1'] *= 50
        b = vi.seleccionar_e4('ridge', alterado.loc[alterado.anio_objetivo.lt(2018)], cols, dict(moneda='D lares', anio_externo=2018))
        self.assertEqual(a[0], b[0])
        self.assertEqual(a[1], b[1])
        pd.testing.assert_frame_equal(pd.DataFrame(a[3]), pd.DataFrame(b[3]))
        # Control positivo: perturbar un año interno (2016) sí cambia la búsqueda.
        interno = alterado.copy()
        interno.loc[interno.anio_objetivo.eq(2016), 'objetivo_fcl_t1'] *= 50
        c = vi.seleccionar_e4('ridge', interno.loc[interno.anio_objetivo.lt(2018)], cols, dict(moneda='D lares', anio_externo=2018))
        self.assertFalse(pd.DataFrame(a[3]).rmse_interno_medio.equals(pd.DataFrame(c[3]).rmse_interno_medio))

    def test_test_partition_perturbation_does_not_change_results(self):
        alterado = panel.copy()
        m = alterado.particion.eq('prueba')
        alterado.loc[m, vi.variantes()['E2'] + ['FCL_preliminar', 'CAPEX_reportado']] = 1e9
        alterado.loc[m, 'objetivo_fcl_t1'] = -1e12
        dl = lambda x: x.loc[x.Moneda.eq('D lares')]
        a = vi.ejecutar(dl(train), (2017,), ('ridge',))
        b = vi.ejecutar(dl(ab.separar_entrenamiento(alterado)), (2017,), ('ridge',))
        for k in a:
            if k != 'tiempos':
                pd.testing.assert_frame_equal(a[k], b[k], check_exact=True, obj=k)
        # Lo guardado coincide con la ejecución reducida (mismas predicciones de 2017 en dólares).
        p = leer('predicciones.csv', dtype={'RPJ': 'string'}, float_precision='round_trip')
        g = p.loc[p.moneda.eq('D lares') & p.anio_objetivo.eq(2017) & p.procedimiento.str.startswith('ridge')].sort_values(['procedimiento', 'id_fila'])
        h = a['pred'].loc[a['pred'].procedimiento.str.startswith('ridge')].sort_values(['procedimiento', 'id_fila'])
        np.testing.assert_allclose(g.y_predicho.to_numpy(), h.y_predicho.to_numpy(), rtol=1e-9)

    def test_lagged_sensitivity_table(self):
        b = vi.bloques()
        ext = b['macroeconomico'] + b['bursatil']
        tl = vi.tabla_rezagada(train, ext)
        self.assertTrue(tl.index.equals(train.index))
        pd.testing.assert_frame_equal(tl[b['financiero']], train[b['financiero']])
        self.assertTrue(tl.loc[tl.Ejercicio.eq(2005), ext].isna().all().all())
        u = train.loc[train.Ejercicio.eq(2010), ext].iloc[0]
        np.testing.assert_allclose(tl.loc[tl.Ejercicio.eq(2011), ext].iloc[0].to_numpy(), u.to_numpy())

    def test_metrics_and_comparisons_reconstruct_from_predictions(self):
        p = leer('predicciones.csv')
        a = leer('metricas_por_anio.csv')
        for r in a.sample(25, random_state=0).itertuples():
            g = p.loc[p.procedimiento.eq(r.procedimiento) & p.moneda.eq(r.moneda) & p.anio_objetivo.eq(r.anio_externo)]
            e = g.y_predicho - g.y_real
            np.testing.assert_allclose([r.RMSE, r.MAE, r.n], [np.sqrt((e ** 2).mean()), e.abs().mean(), len(g)], rtol=1e-12)
        c = leer('resumen_comparaciones.csv')
        ca = leer('comparaciones_por_anio.csv')
        self.assertEqual(len(c), 2 * len(vi.comparaciones_previstas()))
        for r in c.itertuples():
            g = ca.loc[ca.moneda.eq(r.moneda) & ca.candidato.eq(r.candidato) & ca.comparador.eq(r.comparador)]
            np.testing.assert_allclose(r.delta_RMSE_anual_medio_pct, 100 * (g.RMSE_candidato.mean() / g.RMSE_comparador.mean() - 1))
            self.assertEqual(r.anios_mejora_RMSE, int(g.direccion_RMSE.eq('mejora').sum()))
            self.assertEqual(r.cumple_regla, cm.cumple_regla(r._asdict()))

    def test_reproduces_sprint08_and_initial_version(self):
        v = json.loads((OUT / 'verificacion_reproduccion.json').read_text())
        esperadas = {f'sprint08:{x}' for x in ['media_historica', 'persistencia', 'ridge:E2', 'boosting:E2']} | \
                    {f'v1:{m}:{e}' for m in vi.MODELOS for e in ['E0', 'E1', 'E2']} | {'v1:importancia_individual'}
        self.assertEqual(set(v), esperadas)
        self.assertTrue(all(x < 1e-9 for x in v.values()))
        p = leer('predicciones.csv', dtype={'RPJ': 'string'}, float_precision='round_trip')
        self.assertEqual(vi.verificar_reproduccion(p, leer('importancia_individual_por_anio.csv')).keys(), v.keys())

    def test_importance_coverage_and_sign(self):
        imp, b = leer('importancia_individual_por_anio.csv'), leer('importancia_bloques_por_anio.csv')
        self.assertEqual(len(imp), 2 * 2 * 5 * 26)
        self.assertEqual(len(b), 2 * 2 * 5 * 3)
        for d in (imp, b):
            np.testing.assert_allclose(d.delta_RMSE, d.RMSE_sin - d.RMSE_completo, atol=1e-6)
            np.testing.assert_allclose(d.delta_RMSE_pct, 100 * d.delta_RMSE / d.RMSE_completo)
        e2 = leer('metricas_por_anio.csv')
        e2 = e2.loc[e2.procedimiento.str.endswith(':E2')].assign(modelo=lambda x: x.procedimiento.str.split(':').str[0])
        j = imp.merge(e2, left_on=['moneda', 'modelo', 'anio_externo'], right_on=['moneda', 'modelo', 'anio_externo'])
        np.testing.assert_allclose(j.RMSE_completo, j.RMSE, rtol=1e-12)
        res = leer('importancia_individual.csv')
        self.assertTrue((res.anios_aporta + res.anios_perjudica + res.anios_empate == 5).all())

    def test_e4_history_consistent(self):
        sel = leer('seleccion_e4.csv', keep_default_na=False)
        h = leer('seleccion_e4_historial.csv', keep_default_na=False)
        for r in sel.itertuples():
            g = h.loc[h.moneda.eq(r.moneda) & h.anio_externo.eq(r.anio_externo) & h.modelo.eq(r.modelo) & h.paso.gt(0)]
            aceptados = g.loc[g.elegido.astype(str).eq('True'), 'atributo_evaluado'].tolist()
            self.assertEqual(sorted(aceptados), sorted(x for x in r.retirados.split(';') if x))
            self.assertLessEqual(len(aceptados), vi.E4_MAX_RETIRADAS)
            self.assertEqual(r.n_atributos, 26 - len(aceptados))
            for _, s in g.groupby('paso'):
                adm = s.loc[s.admisible.astype(str).eq('True')]
                el = s.loc[s.elegido.astype(str).eq('True')]
                if len(adm):
                    self.assertAlmostEqual(float(el.rmse_interno_medio.iloc[0]), adm.rmse_interno_medio.astype(float).min())
                else:
                    self.assertEqual(len(el), 0)


if __name__ == '__main__':
    unittest.main()
