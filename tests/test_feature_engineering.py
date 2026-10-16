import unittest
import numpy as np
import pandas as pd
from src.feature_engineering import build_features, divide, make_preprocessor
from sklearn.base import clone


def sample():
    rows = []
    for company, base in [('A', 10), ('B', 1000)]:
        for year in range(2016, 2026):
            v = base + year - 2016
            rows.append(dict(RPJ=company, Ejercicio=year, Moneda='Soles',
                ActivoTotal=100, PasivoTotal=40, PatrimonioTotal=60,
                TotalIngreso=50, UtilidadNeta=5, FCO=float(v),
                CAPEX_reportado=-2., FCL_preliminar=float(v-2)))
    return pd.DataFrame(rows)


class FeaturesTest(unittest.TestCase):
    def test_ratios_and_zero(self):
        d = sample(); d.loc[0, 'TotalIngreso'] = 0
        out, cols, _ = build_features(d)
        self.assertAlmostEqual(out.iloc[1].pasivo_activo, .4)
        self.assertTrue(pd.isna(out.iloc[0].margen_neto))
        self.assertEqual(divide(pd.Series([0.]), pd.Series([1.])).iloc[0], 0)
        self.assertTrue(pd.isna(divide(pd.Series([1.]),pd.Series([-1.])).iloc[0]))
        self.assertFalse(np.isinf(out[cols].to_numpy()).any())

    def test_lags_rolling_and_company(self):
        out, _, _ = build_features(sample())
        a = out[out.RPJ.eq('A')].reset_index(drop=True)
        b = out[out.RPJ.eq('B')].reset_index(drop=True)
        self.assertTrue(pd.isna(b.iloc[0].FCO_lag1))
        self.assertEqual(a.iloc[3].FCO_lag3, 10)
        self.assertEqual(a.iloc[3].FCO_mean3_previa, 11)
        self.assertEqual(a.iloc[3].FCO_std3_previa, 1)
        self.assertEqual(b.iloc[1].FCO_lag1, 1000)
        self.assertAlmostEqual(a.iloc[1].cambio_FCO_activo_previo, .01)
        self.assertAlmostEqual(a.iloc[1].crecimiento_TotalIngreso, 0)

    def test_gap_and_currency_return(self):
        d = sample(); d = d[~(d.RPJ.eq('A') & d.Ejercicio.eq(2018))]
        d.loc[d.RPJ.eq('B') & d.Ejercicio.eq(2018), 'Moneda'] = 'USD'
        out, _, _ = build_features(d)
        for company in ['A', 'B']:
            row = out[out.RPJ.eq(company) & out.Ejercicio.eq(2019)].iloc[0]
            self.assertTrue(pd.isna(row.FCO_lag1))
            self.assertTrue(pd.isna(row.FCO_lag3))
        row = out[out.RPJ.eq('A') & out.Ejercicio.eq(2017)].iloc[0]
        self.assertTrue(pd.isna(row.objetivo_fcl_t1))
        row = out[out.RPJ.eq('B') & out.Ejercicio.eq(2017)].iloc[0]
        self.assertFalse(row.utilizable_supervisado)

    def test_future_invariance(self):
        d = sample(); before, cols, _ = build_features(d)
        changed = d.copy()
        changed.loc[changed.Ejercicio.gt(2020), ['FCO','FCL_preliminar','ActivoTotal','TotalIngreso']] = 999999.
        after, _, _ = build_features(changed)
        pd.testing.assert_frame_equal(before.loc[before.Ejercicio.le(2020), cols],
                                      after.loc[after.Ejercicio.le(2020), cols])
        self.assertNotIn('objetivo_fcl_t1', cols)

    def test_target_split_missing_and_capex(self):
        d = sample(); d.loc[1, 'FCL_preliminar'] = np.nan; d.loc[0,'CAPEX_reportado'] = 2
        out, _, _ = build_features(d)
        self.assertTrue(pd.isna(out.iloc[0].objetivo_fcl_t1))
        self.assertTrue(pd.isna(out.iloc[0].inversion_capex_activo))
        train = out[out.particion.eq('entrenamiento')]
        test = out[out.particion.eq('prueba')]
        self.assertLess(train.anio_objetivo.max(), test.anio_objetivo.min())
        self.assertTrue(test.objetivo_fcl_t1.notna().all())
        self.assertEqual(test.iloc[0].anio_objetivo, 2022)
        d = sample(); d.loc[0,'FCL_preliminar'] = 0
        out, _, _ = build_features(d)
        self.assertEqual(out.iloc[1].FCL_preliminar_lag1, 0)

    def test_duplicates_rejected(self):
        d = sample()
        with self.assertRaises(ValueError): build_features(pd.concat([d, d.iloc[:1]]))

    def test_missing_window_and_input_order(self):
        d = sample()
        d.loc[d.RPJ.eq('A') & d.Ejercicio.eq(2017), 'FCO'] = np.nan
        ordered, cols, _ = build_features(d)
        shuffled, _, _ = build_features(d.sample(frac=1, random_state=42))
        pd.testing.assert_frame_equal(ordered[cols], shuffled[cols])
        row = ordered[ordered.RPJ.eq('A') & ordered.Ejercicio.eq(2019)].iloc[0]
        self.assertTrue(pd.isna(row.FCO_mean3_previa))
        self.assertTrue(pd.isna(row.FCO_std3_previa))
        self.assertEqual(row.FCO_lag1, 12)

    def test_current_value_excluded_from_rolling(self):
        d = sample()
        before, _, _ = build_features(d)
        d.loc[d.RPJ.eq('A') & d.Ejercicio.eq(2019), 'FCO'] = 999999
        after, _, _ = build_features(d)
        row = before.RPJ.eq('A') & before.Ejercicio.eq(2019)
        for c in ['FCO_lag1', 'FCO_lag2', 'FCO_lag3', 'FCO_mean3_previa', 'FCO_std3_previa']:
            self.assertEqual(before.loc[row, c].iloc[0], after.loc[row, c].iloc[0])

    def test_positive_capex_invalidates_all_fcl_derivatives(self):
        d = sample()
        d.loc[d.RPJ.eq('A') & d.Ejercicio.eq(2018), 'CAPEX_reportado'] = 2
        original = d.copy(deep=True)
        out, _, _ = build_features(d)
        a = out[out.RPJ.eq('A')].set_index('Ejercicio')
        # Fuente preservada, incluso si contenía FCL inválido no pre-anulado.
        self.assertEqual(a.loc[2018, 'FCL_preliminar'], 10)
        pd.testing.assert_frame_equal(d, original)
        self.assertTrue(pd.isna(a.loc[2018, 'fcl_activo']))
        self.assertTrue(pd.isna(a.loc[2017, 'objetivo_fcl_t1']))
        self.assertFalse(a.loc[2017, 'utilizable_supervisado'])
        for lag in [1, 2, 3]:
            self.assertTrue(pd.isna(a.loc[2018 + lag, f'FCL_preliminar_lag{lag}']))
        for year in [2019, 2020, 2021]:
            for stat in ['mean', 'std']:
                self.assertTrue(pd.isna(a.loc[year, f'FCL_preliminar_{stat}3_previa']))
        self.assertTrue(pd.isna(a.loc[2019, 'cambio_FCL_preliminar_activo_previo']))

    def test_nonpositive_income_domain(self):
        for value in [0, -1]:
            with self.subTest(value=value):
                d = sample()
                d.loc[d.RPJ.eq('A') & d.Ejercicio.eq(2018), 'TotalIngreso'] = value
                out, _, _ = build_features(d)
                a = out[out.RPJ.eq('A')].set_index('Ejercicio')
                self.assertTrue(pd.isna(a.loc[2018, 'rotacion_activo_cierre']))
                self.assertTrue(pd.isna(a.loc[2018, 'crecimiento_TotalIngreso']))
                self.assertTrue(pd.isna(a.loc[2019, 'crecimiento_TotalIngreso']))
                self.assertEqual(a.loc[2018, 'TotalIngreso'], value)

    def test_robust_pipeline_training_only_and_fold_clone(self):
        tr = pd.DataFrame({'x': [1., 2., 3., 4., 1e9], 'z': [1., np.nan, 3., 4., 5.]})
        te = pd.DataFrame({'x': [-1e12, 1e12], 'z': [np.nan, -1e12]})
        pipeline = make_preprocessor()
        transformed = pipeline.fit_transform(tr)
        before_center = pipeline.named_steps['scaler'].center_.copy()
        before_median = pipeline.named_steps['imputer'].statistics_.copy()
        pipeline.transform(te)
        np.testing.assert_array_equal(before_center, pipeline.named_steps['scaler'].center_)
        np.testing.assert_array_equal(before_median, pipeline.named_steps['imputer'].statistics_)
        self.assertAlmostEqual(np.subtract(*np.percentile(transformed[:, 0], [75, 25])), 1.)
        fold = clone(pipeline)
        self.assertFalse(hasattr(fold.named_steps['imputer'], 'statistics_'))
        fold.fit(tr.iloc[:2])
        self.assertEqual(fold.named_steps['imputer'].statistics_[0], 1.5)
        self.assertEqual(pipeline.named_steps['imputer'].statistics_[0], 3.)

if __name__ == '__main__':
    unittest.main()
