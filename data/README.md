# Datos de la entrega de Semana 5

Fuente: Superintendencia del Mercado de Valores del Perú (SMV).
Consulta de las fichas de licencia: 16 de octubre de 2026.

- [Principales cuentas / obtener_InfoFinanciera](https://mvnet.smv.gob.pe/SMV.OpenData.Web/Views/Datasets/CtasPrinc.aspx).
- [Estado de Flujo de Efectivo / obtener_FlujoEfectivo](https://mvnet.smv.gob.pe/SMV.OpenData.Web/Views/Datasets/FluEfe.aspx).

Ambas fichas enlazan Open Data Commons Open Database License. Los XML de
`raw/smv/` son respuestas del primer dataset. Se conservan sin modificaciones,
incluida la copia idéntica de 2025 para preservar el inventario local.

Esta base de datos se ofrece bajo [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Se conservan los derechos y avisos de la SMV sobre su base de origen. Atribuir a
la SMV y a Ricardo Villena por la preparación del panel y los cálculos derivados.
Las bases adaptadas deben conservar los avisos y cumplir las condiciones de
compartir bajo la misma licencia. Este aviso se aplica a la base de datos, no
asigna una licencia general al código ni a derechos independientes de terceros.

Transformaciones de esta entrega: desde `processed/panel_fcl_preliminar.csv`,
cálculo de 22 características y controles, orden por RPJ/ejercicio y exportación
completa a `processed/features_financieras.csv`, sin imputar ni excluir filas.
Las celdas vacías del CSV representan NaN; `pd.read_csv` las recupera como faltantes.
RPJ y RUC deben leerse como texto. Los originales del panel no cambian.
La unidad monetaria y su escala no están acreditadas; no se convierten monedas.

La fuente declarada del panel es SMV; los resúmenes coinciden en todos los
campos compartidos, pero las respuestas históricas de detalle de FCO/CAPEX y el
script original de consolidación no están disponibles. La licencia del dataset
oficial permite la reutilización; no prueba el linaje histórico de esos valores.
Los cálculos derivados se entregan con esta limitación explícita para revisión
académica, sin atribuir a la SMV su validación ni un aval a las conclusiones.

El Excel `raw/base_de_datos.xlsx` no participa en Feature Engineering y se excluye
por carecer de fuente y permisos verificados. No es necesario para reproducir
los cálculos desde el panel incluido.
