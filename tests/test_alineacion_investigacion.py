import json
import unittest
import numpy as np
import pandas as pd
import src.ablacion_variables as ab
import src.auditoria_calidad as ac
import src.alineacion_investigacion as ai
import src.comparacion_modelos as cm

OUT = ai.OUT
panel = clas = train = None


def setUpModule():
    global panel, clas, train
    panel, _, _ = ac.load_inputs()
    clas = ai.clasificar_poblacion(panel)
    train = ab.separar_entrenamiento(panel)


def leer(nombre, **kw):
    return pd.read_csv(OUT / nombre, **kw)


class AlineacionTests(unittest.TestCase):
    def test_protocol_versioned(self):
        self.assertEqual(json.loads((OUT / 'protocolo.json').read_text(encoding='utf-8')), json.loads(json.dumps(ai.protocolo(), ensure_ascii=False)))

    def test_sector_filter_rule_and_traceability(self):
        self.assertEqual(len(clas), 4221)
        fin = clas.TipoSector.isin(ai.SECTORES_FINANCIEROS)
        self.assertTrue((~clas.no_financiera == fin).all())
        self.assertTrue(set(clas.loc[fin, 'TipoSector']) == set(ai.SECTORES_FINANCIEROS))  # no solo BANCOS
        self.assertTrue((clas.conservadora <= clas.no_financiera).all())
        self.assertTrue(panel.groupby('RPJ').TipoSector.nunique().le(1).all())
        self.assertTrue(clas.loc[clas.motivo.str.startswith('dudosa'), 'no_financiera'].all())  # dudosas se conservan
        tabla = leer('poblacion_por_anio_sector_moneda.csv')
        self.assertEqual(int(tabla.observaciones.sum()), 4221)
        for motivo, g in clas.groupby('motivo'):
            self.assertEqual(int(tabla.loc[tabla.motivo.eq(motivo), 'observaciones'].sum()), len(g))
        dud = leer('clasificaciones_dudosas.csv', dtype={'RPJ': 'string'})
        self.assertEqual(set(dud.RPJ), set(clas.loc[clas.motivo.str.startswith('dudosa'), 'RPJ']))

    def test_same_samples_between_variants(self):
        p = leer('predicciones.csv')
        ids_fin = set(clas.index[~clas.no_financiera])
        ids_dud = set(clas.index[~clas.conservadora])
        for (proc_pob, m, y), g in p.assign(pob=p.procedimiento.str.split('|').str[0]).groupby(['pob', 'moneda', 'anio_objetivo']):
            filas = g.groupby('procedimiento').apply(lambda x: tuple(x.sort_values('id_fila')[['id_fila', 'y_real']].itertuples(index=False)))
            self.assertEqual(filas.nunique(), 1, (proc_pob, m, y))
            ids = {r[0] for r in filas.iloc[0]}
            self.assertFalse(ids & (ids_fin if proc_pob == 'no_financiera' else ids_dud))
            esperado = train.loc[train.Moneda.eq(m) & train.anio_objetivo.eq(y) & clas.loc[train.index, proc_pob]]
            self.assertEqual(ids, set(esperado.index))
        self.assertTrue(p.anio_objetivo.between(2017, 2021).all())
        self.assertFalse(set(p.id_fila) & set(panel.index[panel.particion.eq('prueba')]))

    def test_temporal_separation(self):
        b = leer('busquedas_internas.csv')
        for c in [c for c in b.columns if c.startswith('rmse_') and c[5:].isdigit()]:
            self.assertTrue((b.loc[b[c].notna(), 'anio_externo'] > int(c[5:])).all())
        self.assertTrue(b.groupby(['poblacion', 'moneda', 'anio_externo', 'modelo', 'variante']).elegida.sum().eq(1).all())

    def test_no_learning_from_test_or_future(self):
        alterado = panel.copy()
        m = alterado.particion.eq('prueba')
        alterado.loc[m, ['ActivoTotal', 'FCL_preliminar', 'CAPEX_reportado'] + ai.variantes()['E2']] = 1e9
        alterado.loc[m, 'objetivo_fcl_t1'] = -1e12
        dl = lambda x: x.loc[x.Moneda.eq('D lares')]
        a = ai.ejecutar(dl(train), clas, (2017, 2018), ('ridge',), con_importancia=False)
        b = ai.ejecutar(dl(ab.separar_entrenamiento(alterado)), ai.clasificar_poblacion(alterado), (2017, 2018), ('ridge',), con_importancia=False)
        for k in ('pred', 'busq'):
            pd.testing.assert_frame_equal(a[k], b[k], check_exact=True)
        fut = dl(train).copy()
        fut.loc[fut.anio_objetivo.eq(2017), 'objetivo_fcl_t1'] *= 25
        c = ai.ejecutar(fut, clas, (2017, 2018), ('ridge',), con_importancia=False)
        a17, c17 = (x['pred'].loc[x['pred'].anio_objetivo.eq(2017)] for x in (a, c))
        np.testing.assert_array_equal(a17.y_predicho.to_numpy(), c17.y_predicho.to_numpy())
        a18, c18 = (x['pred'].loc[x['pred'].anio_objetivo.eq(2018) & x['pred'].modelo.eq('ridge')] for x in (a, c))
        self.assertFalse(np.allclose(a18.y_predicho, c18.y_predicho))  # control positivo

    def test_metrics_reconstruct_from_predictions(self):
        p = leer('predicciones.csv')
        a = leer('metricas_por_anio.csv')
        for r in a.sample(30, random_state=1).itertuples():
            g = p.loc[p.procedimiento.eq(r.procedimiento) & p.moneda.eq(r.moneda) & p.anio_objetivo.eq(r.anio_externo)]
            e = g.y_predicho - g.y_real
            np.testing.assert_allclose([r.RMSE, r.MAE], [np.sqrt((e ** 2).mean()), e.abs().mean()], rtol=1e-12)
        c = leer('resumen_comparaciones.csv')
        self.assertEqual(len(c), sum(1 for m in ('D lares', 'Soles') for _ in ai.comparaciones_previstas()))
        for r in c.itertuples():
            self.assertEqual(r.cumple_regla, cm.cumple_regla(r._asdict()))

    def test_attributes_and_transformations(self):
        t = ai.anadir_tamano(train)
        np.testing.assert_allclose(t[ai.TAMANO], np.log(train.ActivoTotal))
        v = ai.variantes()
        self.assertEqual(v['E0T'], v['E0'] + [ai.TAMANO])
        self.assertEqual(v['E2T'], v['E2'] + [ai.TAMANO])
        self.assertIn('pasivo_activo', v['E0'])
        self.assertFalse(any('efectivo' in c.lower() or 'cash' in c.lower() for x in v.values() for c in x))
        av = leer('auditoria_variables.csv')
        self.assertTrue(av.loc[av.atributo.eq('efectivo_activo'), 'estado'].str.startswith('NO construible').all())
        self.assertEqual(int(av.loc[av.atributo.eq(ai.TAMANO), 'faltantes'].sum()), 0)

    def test_reproduces_sprint09_for_dollars(self):
        v = json.loads((OUT / 'verificacion_reproduccion.json').read_text())
        self.assertEqual(len(v), 10)
        self.assertTrue(all(x < 1e-9 for x in v.values()))

    def test_importance_coverage_and_sign(self):
        imp, b = leer('importancia_individual_por_anio.csv'), leer('importancia_bloques_por_anio.csv')
        self.assertEqual(len(imp), 2 * 2 * 5 * 27)
        self.assertEqual(len(b), 2 * 2 * 5 * 4)
        for d in (imp, b):
            np.testing.assert_allclose(d.delta_RMSE, d.RMSE_sin - d.RMSE_completo, atol=1e-6)
        m = leer('metricas_por_anio.csv')
        m = m.loc[m.procedimiento.str.contains(r'no_financiera\|.*:E2T$', regex=True)].assign(modelo=lambda x: x.procedimiento.str.split('|').str[1].str.split(':').str[0])
        j = imp.merge(m, on=['moneda', 'modelo', 'anio_externo'])
        np.testing.assert_allclose(j.RMSE_completo, j.RMSE, rtol=1e-12)


if __name__ == '__main__':
    unittest.main()
