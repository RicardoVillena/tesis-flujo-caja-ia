import json
import unittest
import numpy as np
import pandas as pd
import src.ablacion_variables as ab
import src.alineacion_investigacion as ai
import src.auditoria_calidad as ac
import src.comparacion_modelos as cm
import src.experimento_final as ef

OUT = ef.OUT
panel = clas = train = None


def setUpModule():
    global panel, clas, train
    panel, _, _ = ac.load_inputs()
    clas = ai.clasificar_poblacion(panel)
    train = ab.separar_entrenamiento(panel)


def leer(nombre, **kw):
    return pd.read_csv(OUT / nombre, **kw)


class ExperimentoFinalTests(unittest.TestCase):
    def test_protocol_versioned(self):
        self.assertEqual(json.loads((OUT / 'protocolo.json').read_text(encoding='utf-8')), json.loads(json.dumps(ef.protocolo(), ensure_ascii=False)))

    def test_target_reconstruction_roundtrip(self):
        t = train.loc[train.Moneda.eq('Soles')].head(300)
        b = ef.respaldo(t)
        for f in ef.FORMULACIONES:
            z = ef.objetivo(f, t, b)
            np.testing.assert_allclose(ef.reconstruir(f, z, t, b), t.objetivo_fcl_t1.to_numpy(), rtol=1e-12, atol=1e-6)
        # base(t) = FCL(t) válido (CAPEX > 0 lo invalida) y nunca FCL(t+1)
        fcl = ab.fcl_t(t)
        self.assertTrue(fcl.loc[t.CAPEX_reportado.gt(0)].isna().all())
        self.assertFalse(np.allclose(ef.base_t(t, b), t.objetivo_fcl_t1))
        np.testing.assert_allclose(ef.objetivo('relativa', t, b), t.objetivo_fcl_t1 / t.ActivoTotal)

    def test_fallback_and_denominator_coherence(self):
        p = leer('predicciones.csv')
        per = p.loc[p.formulacion.eq('persistencia')]
        for (m, y), g in per.groupby(['moneda', 'anio_objetivo']):
            pasado = train.loc[train.Moneda.eq(m) & train.anio_objetivo.lt(y) & clas.loc[train.index, ef.POBLACION]]
            np.testing.assert_allclose(g.respaldo_media_entrenamiento, pasado.objetivo_fcl_t1.mean(), rtol=1e-12)
            base = ab.fcl_t(train.loc[g.id_fila]).fillna(pasado.objetivo_fcl_t1.mean()).to_numpy()
            np.testing.assert_allclose(g.base_t, base, rtol=1e-12)
            np.testing.assert_allclose(g.y_predicho, g.base_t + g.prediccion_objetivo_transformado, rtol=1e-9, atol=1e-6)
        rel = p.loc[p.formulacion.eq('relativa')]
        self.assertTrue((rel.activo_t > 0).all())
        np.testing.assert_allclose(rel.activo_t, train.loc[rel.id_fila, 'ActivoTotal'].to_numpy())  # activo de t, no de t+1
        np.testing.assert_allclose(rel.y_predicho, rel.prediccion_objetivo_transformado * rel.activo_t, rtol=1e-9)
        # Con cambio predicho 0, la corrección de persistencia coincide con la referencia de persistencia.
        ref = p.loc[p.procedimiento.eq('persistencia')].set_index(['moneda', 'id_fila']).y_predicho
        uno = per.loc[per.procedimiento.eq('persistencia|ridge:E0')].set_index(['moneda', 'id_fila']).base_t
        np.testing.assert_allclose(uno.sort_index(), ref.loc[uno.sort_index().index], rtol=1e-12)

    def test_same_samples_between_comparators(self):
        p = leer('predicciones.csv')
        n_proc = len(ef.FORMULACIONES) * len(ef.MODELOS) * len(ef.VARIANTES) + 2
        for (m, y), g in p.groupby(['moneda', 'anio_objetivo']):
            self.assertEqual(g.procedimiento.nunique(), n_proc)
            filas = g.groupby('procedimiento').apply(lambda x: tuple(x.sort_values('id_fila')[['id_fila', 'y_real']].itertuples(index=False)))
            self.assertEqual(filas.nunique(), 1)
            esperado = train.loc[train.Moneda.eq(m) & train.anio_objetivo.eq(y) & clas.loc[train.index, ef.POBLACION]]
            self.assertEqual({r[0] for r in filas.iloc[0]}, set(esperado.index))
        self.assertFalse(set(p.id_fila) & (set(panel.index[panel.particion.eq('prueba')]) | set(panel.index[~clas.no_financiera])))

    def test_no_future_information(self):
        dl = train.loc[train.Moneda.eq('D lares')]
        kw = dict(n_jobs=1, modelos=('ridge',), variantes=('E0',))
        a = ef.ejecutar(dl, clas, (2017, 2018), **kw)
        alt = dl.copy()
        alt.loc[alt.anio_objetivo.ge(2018), ['objetivo_fcl_t1', 'FCL_preliminar', 'ActivoTotal']] *= 7
        b = ef.ejecutar(alt, clas, (2017, 2018), **kw)
        sel = lambda x, y: x[0].loc[x[0].anio_objetivo.eq(y)].reset_index(drop=True)
        pd.testing.assert_frame_equal(sel(a, 2017), sel(b, 2017), check_exact=True)
        pd.testing.assert_frame_equal(a[1].loc[a[1].anio_externo.eq(2017)].reset_index(drop=True), b[1].loc[b[1].anio_externo.eq(2017)].reset_index(drop=True))
        c_ = dl.copy()
        c_.loc[c_.anio_objetivo.eq(2017), 'objetivo_fcl_t1'] *= 7
        c = ef.ejecutar(c_, clas, (2017, 2018), **kw)
        self.assertFalse(np.allclose(sel(a, 2018).loc[lambda x: x.procedimiento.eq('directa|ridge:E0'), 'y_predicho'],
                                     sel(c, 2018).loc[lambda x: x.procedimiento.eq('directa|ridge:E0'), 'y_predicho']))  # control positivo
        prueba = panel.copy()
        m = prueba.particion.eq('prueba')
        prueba.loc[m, ['objetivo_fcl_t1', 'FCL_preliminar', 'ActivoTotal']] = 1e12
        d = ef.ejecutar(ab.separar_entrenamiento(prueba).query("Moneda == 'D lares'"), ai.clasificar_poblacion(prueba), (2017, 2018), **kw)
        pd.testing.assert_frame_equal(a[0], d[0], check_exact=True)

    def test_internal_selection_uses_reconstructed_monetary_errors(self):
        t = train.loc[train.Moneda.eq('D lares') & clas.loc[train.index, ef.POBLACION] & train.anio_objetivo.lt(2018)]
        cols = ef.vi.variantes()['E0']
        cfg, filas = ef.buscar('relativa', 'ridge', t, cols, dict(moneda='D lares', anio_externo=2018, variante='E0'))
        anio, tr, va = cm.cortes_internos(t)[0]
        b = ef.respaldo(tr)
        est = ef.crear('ridge', cols, filas[0] and json.loads(filas[0]['configuracion'])).fit(tr[cols], tr.objetivo_fcl_t1 / tr.ActivoTotal)
        p = est.predict(va[cols]) * va.ActivoTotal.to_numpy()
        self.assertAlmostEqual(filas[0][f'rmse_{anio}'], float(np.sqrt(np.mean((p - va.objetivo_fcl_t1.to_numpy()) ** 2))), places=4)
        b_ = leer('busquedas_internas.csv')
        self.assertTrue(b_.groupby(['moneda', 'anio_externo', 'formulacion', 'modelo', 'variante']).elegida.sum().eq(1).all())
        anios = [c for c in b_.columns if c.startswith('rmse_') and c[5:].isdigit()]
        for c in anios:
            self.assertTrue((b_.loc[b_[c].notna(), 'anio_externo'] > int(c[5:])).all())

    def test_metrics_from_predictions_and_rule(self):
        p = leer('predicciones.csv')
        a = leer('metricas_por_anio.csv')
        for r in a.sample(30, random_state=2).itertuples():
            g = p.loc[p.procedimiento.eq(r.procedimiento) & p.moneda.eq(r.moneda) & p.anio_objetivo.eq(r.anio_externo)]
            e = g.y_predicho - g.y_real
            np.testing.assert_allclose([r.RMSE, r.MAE], [np.sqrt((e ** 2).mean()), e.abs().mean()], rtol=1e-12)
        c = leer('resumen_comparaciones.csv')
        self.assertEqual(len(c), 2 * len(ef.comparaciones_previstas()))
        for r in c.itertuples():
            self.assertEqual(r.cumple_regla, cm.cumple_regla(r._asdict()))

    def test_direct_formulation_reproduces_previous_stage(self):
        v = json.loads((OUT / 'verificacion_reproduccion.json').read_text())
        self.assertEqual(len(v), 10)
        self.assertTrue(all(x < 1e-9 for x in v.values()), v)

    def test_units_audit_no_silent_corrections(self):
        r = json.loads((OUT / 'auditoria_unidades_resumen.json').read_text())
        self.assertEqual(r['violaciones_identidad_activo_pasivo_patrimonio'], 0)
        self.assertFalse(r['version_derivada'])
        casos = leer('auditoria_unidades_casos.csv')
        self.assertTrue(casos.decision.str.startswith('sin corrección').all())
        self.assertGreater(len(casos), 0)


if __name__ == '__main__':
    unittest.main()
