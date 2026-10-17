"""Descarga prospectiva del resumen SMV; no descarga el detalle de flujos.
No sobrescribe originales. Los logs nuevos no acreditan la ingesta histórica.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.request
import xml.etree.ElementTree as ET

URL = 'https://mvnet.smv.gob.pe/ws_od_eeff/WebServiceInfoFinanciera.asmx'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start', type=int, default=2005)
    p.add_argument('--end', type=int, default=2025)
    p.add_argument('--output', type=Path, default=Path('data/raw/smv'))
    args = p.parse_args()
    if not 1900 <= args.start <= args.end <= 2100:
        p.error('Rango de años inválido')
    args.output.mkdir(parents=True, exist_ok=True)
    failures = 0
    for year in range(args.start, args.end + 1):
        dest = args.output / f'smv_infofinanciera_{year}_A_I.xml'
        if dest.exists():
            print(f'Conservado: {dest}')
            continue
        body = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body><obtener_InfoFinanciera xmlns="http://tempuri.org/">
<Ejercicio>{year}</Ejercicio><Periodo>A</Periodo><Tipo>I</Tipo>
</obtener_InfoFinanciera></soap:Body></soap:Envelope>'''.encode()
        event = dict(fecha_utc=datetime.now(timezone.utc).isoformat(), url=URL,
                     operacion='obtener_InfoFinanciera', ejercicio=year, periodo='A', tipo='I')
        try:
            req = urllib.request.Request(URL, data=body, headers={
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': 'http://tempuri.org/obtener_InfoFinanciera'})
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
                event['http_status'] = response.status
            root = ET.fromstring(data)
            results = [n for n in root.iter() if n.tag.split('}')[-1] == 'obtener_InfoFinancieraResult']
            if len(results) != 1 or not isinstance(json.loads(results[0].text or ''), list):
                raise ValueError('Respuesta inesperada o SOAP Fault')
            rows = json.loads(results[0].text)
            with dest.open('xb') as f:
                f.write(data)
            event.update(estado='ok', registros=len(rows), archivo=dest.name,
                         sha256=hashlib.sha256(data).hexdigest())
        except Exception as exc:
            failures += 1
            event.update(estado='error', error=str(exc))
        with (args.output / 'descargas.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
        print(year, event['estado'])
        time.sleep(1)
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
