"""Conserva documentos primarios de Fase 3; no sustituye corpus anteriores."""
from pathlib import Path
import json, hashlib, concurrent.futures, requests
BASE=Path(__file__).resolve().parents[1]/'data/raw/sectorial_fase3'
def fetch(row):
    p=BASE/(row['id']+'.pdf');m=BASE/(row['id']+'.json');t=BASE/(row['id']+'.txt')
    if p.exists() and m.exists() and t.exists():return row['id']+': conservado'
    try:
        r=requests.get(row['url'],headers={'User-Agent':'Mozilla/5.0'},timeout=45);r.raise_for_status()
        if not r.content.startswith(b'%PDF'):raise ValueError('Respuesta no PDF')
        p.write_bytes(r.content)
        from pypdf import PdfReader
        reader=PdfReader(p)
        text='\n'.join(f'\n=== PAGINA PDF {i+1} ===\n'+(x.extract_text() or '') for i,x in enumerate(reader.pages[:60]))
        t.write_text(text)
        m.write_text(json.dumps(row|{'url_final':r.url,'fecha_consulta':'2026-10-23','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256_texto':hashlib.sha256(t.read_bytes()).hexdigest(),'paginas_transcritas':min(len(reader.pages),60)},ensure_ascii=False,indent=2)+'\n')
        return row['id']+': descargado'
    except Exception as e:
        (BASE/(row['id']+'.error.json')).write_text(json.dumps(row|{'error':str(e)},ensure_ascii=False,indent=2));return row['id']+': '+str(e)
if __name__=='__main__':
    rows=json.loads((BASE/'descargas.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        for result in pool.map(fetch,rows):print(result,flush=True)
