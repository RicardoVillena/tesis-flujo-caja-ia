# Fuentes bursátiles 2005–2025

Reproducción: ejecutar notebooks/05_extraccion_bursatil.ipynb con el kernel tesis-fcl.
Las versiones de paquetes se registran en reports/validacion_extraccion_bursatil.json.
Con ACTUALIZAR=False se reutilizan los originales verificando sus hashes.
Con True se consultan nuevamente las fuentes y se conservan versiones anteriores.

Los .bin contienen exactamente las respuestas JSON, XML o HTML recibidas.
Cada .meta.json conserva URL, método, solicitud pública, fecha UTC y SHA-256.
manifest_bursatil.json consolida esa trazabilidad; no contiene credenciales.

BCRP: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api
Condiciones: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/condiciones-de-uso
Atribución: BCRPData; fuentes originales BVL, CAVALI y BCRP según cada serie.

SMV: https://mvnet.smv.gob.pe/SMV.OpenData.Web/Views/Datasets/Valores_Inscritos.aspx
La ficha declara Open Database License (ODbL) 1.0:
https://opendatacommons.org/licenses/odbl/1-0/
Las respuestas y tablas registrales derivadas de SMV se ofrecen bajo esa licencia;
se conserva la atribución a SMV y a Ricardo Villena por la preparación.
La licencia de SMV no se extiende automáticamente a las demás fuentes ni al código.
El SOAP usa la dirección HTTP pública publicada por el WSDL; no envía credenciales.

BVL: https://www.bvl.com.pe/mercado/movimientos-diarios
Se conservaron respuestas públicas de documentación y de su cliente web.
No se verificó una API pública de históricos ni se descargaron series individuales.
No se atribuyen las cotizaciones actuales de SMV a años históricos ni se completan ISIN.

Datasets de mercado y registro están separados en data/processed/.
Diccionarios, controles, cobertura y restricciones se guardan en reports/.
Ningún archivo financiero o macroeconómico anterior participa como salida.
