import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('trace', Path(__file__).resolve().parents[1] / 'scripts/trace_smv.py')
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


class TraceTest(unittest.TestCase):
    def test_duplicate_files_and_value_discrepancy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = '<x><obtener_InfoFinancieraResult>' + json.dumps([
                dict(RPJ='001', Ejercicio='2025', ActivoTotal=9)]) + '</obtener_InfoFinancieraResult></x>'
            for name in ('a.xml', 'b.xml'):
                (root / name).write_text(body)
            panel = root / 'panel.csv'
            panel.write_text('RPJ,Ejercicio,ActivoTotal\n001,2025,8\n')
            raw = root / 'raw'
            raw.mkdir()
            for p in root.glob('*.xml'):
                p.rename(raw / p.name)
            result, rows = trace.trace(raw, panel)
            self.assertEqual(len(rows), 1)
            self.assertEqual(result['inventario'][1]['duplicado_de'], 'a.xml')
            self.assertEqual(result['inventario'][0]['discrepancias_por_campo'], {'ActivoTotal': 1})

    def test_fault_is_not_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fault.xml'
            path.write_text('<Envelope><Fault>error</Fault></Envelope>')
            with self.assertRaises(ValueError):
                trace.extract(path)
