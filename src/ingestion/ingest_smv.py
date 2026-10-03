from pathlib import Path
from datetime import datetime
import requests

URL = "https://mvnet.smv.gob.pe/ws_od_eeff/WebServiceInfoFinanciera.asmx"

EJERCICIO = "2025"
PERIODO = "A"
TIPO = "I"

soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <obtener_InfoFinanciera xmlns="http://tempuri.org/">
            <Ejercicio>{EJERCICIO}</Ejercicio>
            <Periodo>{PERIODO}</Periodo>
            <Tipo>{TIPO}</Tipo>
        </obtener_InfoFinanciera>
    </soap:Body>
</soap:Envelope>
"""

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "http://tempuri.org/obtener_InfoFinanciera"
}

print("=" * 60)
print("INGESTA DE DATOS FINANCIEROS - SMV")
print("=" * 60)

try:
    response = requests.post(
        URL,
        data=soap_body.encode("utf-8"),
        headers=headers,
        timeout=60
    )

    print("Código HTTP:", response.status_code)
    response.raise_for_status()

    output_dir = Path("data/raw/smv")
    output_dir.mkdir(parents=True, exist_ok=True)

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    archivo = output_dir / (
        f"smv_infofinanciera_{EJERCICIO}_{PERIODO}_{TIPO}_{fecha}.xml"
    )

    archivo.write_bytes(response.content)

    print("INGESTA COMPLETADA")
    print("Archivo:", archivo)
    print("Tamaño:", len(response.content), "bytes")

except requests.exceptions.RequestException as error:
    print("ERROR EN LA INGESTA")
    print(error)
