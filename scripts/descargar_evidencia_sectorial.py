"""Descarga fuentes primarias del manifiesto; no sobrescribe respuestas conservadas.
Extracción PDF opcional requiere pypdf, que no es dependencia de reproducción.
"""
from pathlib import Path
import hashlib
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'data/raw/sectorial_documental'

def fetch(row):
    path = BASE/(row['id']+'.pdf')
    meta = BASE/(row['id']+'.json')
    if path.exists() and meta.exists():
        return row['id']+': conservado'
    try:
        req=urllib.request.Request(row['url'], headers={'User-Agent':'Mozilla/5.0 (academic research)'})
        with urllib.request.urlopen(req, timeout=40) as r:
            data=r.read(); final=r.url; content_type=r.headers.get('Content-Type')
        if not data.startswith(b'%PDF'):
            raise ValueError('La respuesta no es un PDF')
        path.write_bytes(data)
        meta.write_text(json.dumps(row | {'url_final':final,'content_type':content_type,
            'fecha_consulta':'2026-10-23','sha256':hashlib.sha256(data).hexdigest()},indent=2)+'\n')
        return row['id']+': descargado'
    except Exception as e:
        (BASE/(row['id']+'.error.json')).write_text(json.dumps(row | {'fecha_consulta':'2026-10-23','error':str(e)},indent=2)+'\n')
        return row['id']+': ERROR '+str(e)

if __name__=='__main__':
    rows=json.loads((BASE/'descargas.json').read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(fetch,rows):print(result,flush=True)
    if '--extract' in sys.argv:
        from pypdf import PdfReader
        for row in rows:
            pdf=BASE/(row['id']+'.pdf'); out=BASE/(row['id']+'.txt')
            if pdf.exists() and not out.exists():
                reader=PdfReader(pdf)
                text='\n'.join(f'\n=== PAGINA PDF {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages[:35]))
                out.write_text(text,encoding='utf-8')
                print(row['id']+': texto extraído',flush=True)
