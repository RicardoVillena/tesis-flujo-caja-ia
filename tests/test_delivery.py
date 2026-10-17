"""Controles de entrega y referencia manual para los 22 predictores."""
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from src.feature_engineering import build_features
from test_feature_engineering import sample


class DeliveryTest(unittest.TestCase):
    def test_all_22_against_hand_calculation(self):
        out, predictors, _ = build_features(sample())
        row = out.loc[out.RPJ.eq('A') & out.Ejercicio.eq(2019)].iloc[0]
        expected = dict(pasivo_activo=.4, margen_neto=.1, rentabilidad_activo_cierre=.05,
            rotacion_activo_cierre=.5, fco_activo=.13, fco_ingresos=.26,
            inversion_capex_activo=.02, fcl_activo=.11, crecimiento_ActivoTotal=0.,
            crecimiento_TotalIngreso=0., cambio_FCO_activo_previo=.01,
            cambio_FCL_preliminar_activo_previo=.01, FCO_lag1=12., FCO_lag2=11.,
            FCO_lag3=10., FCO_mean3_previa=11., FCO_std3_previa=1.,
            FCL_preliminar_lag1=10., FCL_preliminar_lag2=9., FCL_preliminar_lag3=8.,
            FCL_preliminar_mean3_previa=9., FCL_preliminar_std3_previa=1.)
        self.assertEqual(set(expected), set(predictors))
        for name, value in expected.items():
            with self.subTest(variable=name):
                self.assertAlmostEqual(row[name], value)
        self.assertEqual(row.objetivo_fcl_t1, 12.)

    def test_delivery_csv_preserves_every_row_source_and_nan(self):
        root = Path(__file__).resolve().parents[1]
        read = lambda name: pd.read_csv(root / 'data/processed' / name,
            dtype={'RPJ': str, 'RUC': str}, encoding='utf-8-sig')
        raw = read('panel_fcl_preliminar.csv')
        saved = read('features_financieras.csv')
        calculated, predictors, _ = build_features(raw)
        self.assertEqual(calculated.shape, (4221, 57))
        self.assertEqual(len(predictors), 22)
        pd.testing.assert_frame_equal(calculated, saved, check_dtype=False, rtol=1e-12, atol=1e-12)
        self.assertTrue(calculated.isna().equals(saved.isna()))
        self.assertGreater(int(saved[predictors].isna().sum().sum()), 0)
        pd.testing.assert_frame_equal(calculated[raw.columns],
            raw.sort_values(['RPJ', 'Ejercicio']).reset_index(drop=True))
        self.assertFalse(np.isinf(saved[predictors].to_numpy(dtype=float)).any())
