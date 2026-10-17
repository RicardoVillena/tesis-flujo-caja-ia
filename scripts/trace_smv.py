"""Inventario y contraste verificable; no reconstruye FCO/CAPEX ausentes.
Uso: python scripts/trace_smv.py [--extract ruta.csv]
La extracción opcional es local y no sustituye panel_fcl_preliminar.csv.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def extract(path):
    root = ET.fromstring(path.read_bytes())
    nodes = [n for n in root.iter() if n.tag.split('}')[-1] == 'obtener_InfoFinancieraResult']
    if len(nodes) != 1 or not nodes[0].text:
        raise ValueError(f'Respuesta no válida: {path.name}')
    rows = json.loads(nodes[0].text)
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        raise ValueError('Se esperaba una lista JSON de objetos')
    return rows


def equal(a, b):
    if a is None or a == '':
        return b in (None, '')
    return str(a) == str(b)


def trace(raw_dir, panel_path):
    with panel_path.open(encoding='utf-8-sig', newline='') as f:
        panel = list(csv.DictReader(f))
    index = {(r['RPJ'], r['Ejercicio']): r for r in panel}
    inventory, extracted, seen = [], [], {}
    for path in sorted(raw_dir.glob('*.xml')):
        if not path.is_file():
            continue
        rows = extract(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        matches = [r for r in rows if (str(r['RPJ']), str(r['Ejercicio'])) in index]
        mismatches = {}
        for r in matches:
            target = index[(str(r['RPJ']), str(r['Ejercicio']))]
            for k, v in r.items():
                if k in target and not equal(v, target[k]):
                    mismatches[k] = mismatches.get(k, 0) + 1
        inventory.append(dict(archivo=path.name, bytes=path.stat().st_size, sha256=digest,
            formato='XML SOAP 1.1 con lista JSON', ejercicios=sorted({str(r['Ejercicio']) for r in rows}),
            registros=len(rows), campos=sorted({k for r in rows for k in r}),
            claves_en_panel=len(matches), discrepancias_por_campo=mismatches,
            duplicado_de=seen.get(digest), uso_historico='No acreditado por logs o script de consolidación'))
        if digest not in seen:
            extracted.extend(rows)
        seen.setdefault(digest, path.name)
    result = dict(archivos=len(inventory), bytes=sum(r['bytes'] for r in inventory),
        panel_sha256=hashlib.sha256(panel_path.read_bytes()).hexdigest(), filas_panel=len(panel),
        registros_extraidos_sin_archivos_duplicados=len(extracted), inventario=inventory,
        advertencia='Coincidencia de claves/valores no demuestra uso histórico. No hay FCO/CAPEX en estos XML.')
    return result, extracted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=ROOT / 'data/raw/smv')
    parser.add_argument('--panel', type=Path, default=ROOT / 'data/processed/panel_fcl_preliminar.csv')
    parser.add_argument('--report', type=Path, default=ROOT / 'reports/trazabilidad_smv.json')
    parser.add_argument('--extract', type=Path)
    args = parser.parse_args()
    result, rows = trace(args.raw_dir, args.panel)
    if not result['archivos']:
        parser.error('No hay originales locales; descargarlos no garantiza recuperar la misma versión histórica.')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if args.extract:
        args.extract.parent.mkdir(parents=True, exist_ok=True)
        with args.extract.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r}))
            writer.writeheader()
            writer.writerows(rows)
    print(f"{result['archivos']} archivos; {result['bytes']} bytes; {len(rows)} registros únicos por contenido de archivo")


if __name__ == '__main__':
    main()
