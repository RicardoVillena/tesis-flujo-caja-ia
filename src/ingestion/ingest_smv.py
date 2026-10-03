from pathlib import Path
from datetime import datetime
import requests
import time

URL = "https://mvnet.smv.gob.pe/ws_od_eeff/WebServiceInfoFinanciera.asmx"

ANIO_INICIAL = 2005
ANIO_FINAL = 2025

PERIODO = "A"
TIPO = "I"

output_dir = Path("data/raw/smv")
output_dir.mkdir(parents=True, exist_ok=True)

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "http://tempuri.org/obtener_InfoFinanciera"
}

print("=" * 65)
print("INGESTA HISTÓRICA DE INFORMACIÓN FINANCIERA - SMV")
print("=" * 65)
print(f"Periodo de análisis: {ANIO_INICIAL} - {ANIO_FINAL}")
print("Frecuencia: Anual")
print("Tipo: Individual")
print("=" * 65)

exitosas = 0
errores = 0

for ejercicio in range(ANIO_INICIAL, ANIO_FINAL + 1):

    ejercicio = str(ejercicio)

    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <obtener_InfoFinanciera xmlns="http://tempuri.org/">
            <Ejercicio>{ejercicio}</Ejercicio>
            <Periodo>{PERIODO}</Periodo>
            <Tipo>{TIPO}</Tipo>
        </obtener_InfoFinanciera>
    </soap:Body>
</soap:Envelope>
"""

    print(f"\nConsultando SMV: {ejercicio}...")

    try:
        response = requests.post(
            URL,
            data=soap_body.encode("utf-8"),
            headers=headers,
            timeout=60
        )

        print("Código HTTP:", response.status_code)

        response.raise_for_status()

        nombre_archivo = (
            f"smv_infofinanciera_{ejercicio}_{PERIODO}_{TIPO}.xml"
        )

        archivo = output_dir / nombre_archivo

        archivo.write_bytes(response.content)

        print(
            f"OK -> {archivo} "
            f"({len(response.content):,} bytes)"
        )

        exitosas += 1

    except requests.exceptions.RequestException as error:

        print(f"ERROR {ejercicio}: {error}")

        errores += 1

    # Pausa para no saturar el servicio de la SMV
    time.sleep(1)


print("\n" + "=" * 65)
print("RESUMEN DE INGESTA")
print("=" * 65)

print("Consultas esperadas:", ANIO_FINAL - ANIO_INICIAL + 1)
print("Consultas exitosas:", exitosas)
print("Consultas con error:", errores)

print("\nArchivos almacenados en:")
print(output_dir)

print("=" * 65)
