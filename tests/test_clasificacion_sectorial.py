"""Controles del Sprint 07: evidencia, integridad y reproducción sin modelos."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import pandas as pd
from src.clasificacion_sectorial import (read_panel, classify, join_classification,
    normalize_ciiu, run, fingerprints)

ROOT = Path(__file__).resolve().parents[1]


class SectorialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = read_panel(ROOT)
        cls.official = pd.read_csv(ROOT/'data/raw/damodaran/industrias_2026.csv').industria_damodaran
        cls.catalog = classify(cls.panel, cls.official)

    def test_union_preserva_todas_columnas_y_particiones(self):
        d = join_classification(self.panel, self.catalog)
        pd.testing.assert_frame_equal(d[self.panel.columns], self.panel, check_exact=True)
        self.assertEqual((len(d), d.RPJ.nunique()), (4221, 336))
        self.assertFalse(d.duplicated(['RPJ','Ejercicio']).any())

    def test_duplicado_rechazado(self):
        with self.assertRaises(ValueError):
            classify(pd.concat([self.panel, self.panel.iloc[:1]]), self.official)
        with self.assertRaises(pd.errors.MergeError):
            join_classification(self.panel, pd.concat([self.catalog, self.catalog.iloc[:1]]))

    def test_no_clasifica_por_nombre_ni_propaga_ciiu(self):
        altered = self.panel.copy()
        altered['NombreEmpresa'] = 'BANCO HOTEL MINERA AFP'
        a = classify(altered, self.official)
        pd.testing.assert_series_equal(a.industria_damodaran, self.catalog.industria_damodaran)
        hotel_ids = self.catalog.loc[self.catalog.industria_damodaran.eq('Hotel/Gaming').fillna(False),'RPJ']
        old = self.catalog.loc[self.catalog.RPJ.isin(hotel_ids) & self.catalog.CIIU.isna()]
        self.assertGreater(len(old), 0)
        self.assertTrue(old.industria_damodaran.isna().all())

    def test_ambiguos_pendientes_y_vocabulario_oficial(self):
        c = self.catalog
        self.assertTrue(c.loc[c.TipoSector.isin(['BANCOS','SEGUROS','MINERAS']), 'industria_damodaran'].isna().all())
        a = c.loc[c.industria_damodaran.notna()]
        self.assertTrue(set(a.industria_damodaran).issubset(set(self.official)))
        self.assertTrue(a.regla_industria.str.startswith(('D01:', 'D02:')).all())
        self.assertTrue(a.fuente_regla.str.startswith('https://').all())
        self.assertEqual(len(self.official), 94)

    def test_conflicto_sector_o_ruc_queda_pendiente(self):
        d = self.panel.copy()
        idx = d.index[d.TipoSector.eq('A.F.P.')][0]
        d.loc[idx, 'TipoSector'] = 'BANCOS'
        a = classify(d, self.official)
        self.assertTrue(a.loc[a.RPJ.eq(d.loc[idx,'RPJ']), 'industria_damodaran'].isna().all())
        d = self.panel.copy(); d.loc[idx, 'RUC'] = '00000000000'
        a = classify(d, self.official)
        self.assertTrue(a.loc[a.RPJ.eq(d.loc[idx,'RPJ']), 'industria_damodaran'].isna().all())

    def test_normalizacion_no_inventa_revision(self):
        self.assertEqual(normalize_ciiu('729.0'), '0729')
        self.assertEqual(normalize_ciiu('0729'), '0729')
        self.assertTrue(pd.isna(normalize_ciiu('foo')))
        self.assertTrue(pd.isna(normalize_ciiu('12345')))

    def test_reproducibilidad_fuentes_y_salida_exacta(self):
        before = fingerprints(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            _, tables, audit = run(ROOT, Path(tmp), make_plots=False)
            self.assertEqual(audit['elegibles'], 3560)
            self.assertEqual(audit['particiones_elegibles'], {'entrenamiento':2869,'prueba':691})
            for name in tables:
                self.assertEqual((Path(tmp)/name).read_bytes(), (ROOT/'reports/sprint_07'/name).read_bytes(), name)
            reference = json.loads((ROOT/'reports/sprint_07/auditoria_sectorial.json').read_text())
            self.assertEqual(audit, reference)
        self.assertEqual(before, fingerprints(ROOT))

    def test_notebook_formato_y_sin_entrenamiento(self):
        n = json.loads((ROOT/'notebooks/08_clasificacion_sectorial.ipynb').read_text())
        for i,c in enumerate(n['cells']):
            if c['cell_type'] != 'code':
                continue
            self.assertEqual(n['cells'][i-1]['cell_type'], 'markdown')
            text = ''.join(n['cells'][i-1]['source'])
            self.assertTrue(text.startswith('**'))
            self.assertFalse(any(line.startswith('#') for line in text.splitlines()))
            self.assertNotIn('.fit(', ''.join(c['source']))
            self.assertIsNotNone(c['execution_count'])
            self.assertFalse(any(o['output_type']=='error' for o in c.get('outputs',[])))
