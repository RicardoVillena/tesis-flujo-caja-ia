# Viabilidad de LSTM, DCF y valoración probabilística (sin implementar)

Este documento evalúa la viabilidad; **no implementa** LSTM, Monte Carlo ni DCF. Ninguna simulación se presenta aquí como mejora de precisión.

## 1. Historia temporal disponible para LSTM

- **Alcance de la serie:** el panel es anual, de 2005 a 2025, con un máximo de 21 ejercicios por empresa. Entrenamiento: 2.869 filas elegibles. En la población no financiera quedan 1.913 filas y 200 empresas en soles, y 353 filas y 49 empresas en dólares.
- **Historia por empresa:** la historia contigua depende de cada empresa. Muchas tienen menos de 4 años previos: en entrenamiento, la mayoría de los faltantes de los rezagos de 3 años son estructurales (Sprint 08).
- **Implicación:** una LSTM por empresa tendría secuencias de 5 a 15 pasos anuales, y ventanas de 3 a 4 años eliminarían una parte relevante de las observaciones. Una LSTM global, que apila empresas, tendría pocas secuencias por moneda en dólares (unas 50 empresas) y heterogeneidad de escala no acreditada.
- **Prerrequisitos:** antes de comparar con Ridge o boosting haría falta un protocolo temporal anidado equivalente, con las mismas filas, un tratamiento explícito de los huecos y la ruptura de segmentos, y una referencia que use las mismas ventanas.
- **Viabilidad:** limitada; requiere una justificación previa de que hay datos suficientes.

## 2. Validación económica del flujo para un DCF

- **Diferencia de objetivo:** el objetivo actual es un FCL preliminar = FCO + CAPEX reportado. Un DCF de firma requiere FCFF = EBIT·(1 − t) + depreciación − CAPEX − ΔCT, o una conciliación explícita desde el FCO, que ajuste intereses pagados según el formato, impuestos y partidas no operativas.
- **Datos faltantes:** el panel no tiene EBIT, depreciación, impuestos, intereses, capital de trabajo ni deuda financiera separada del pasivo total.
- **Linaje:** la extracción histórica de FCO y CAPEX no es reproducible (`reports/procedimiento_smv.md`), y la escala monetaria por emisor no está acreditada.
- **Pendiente:** obtener los estados detallados de SMV (balance, resultados y flujo), mapear cuentas por formato y sector, y validar la conciliación en una muestra documental.

## 3. Datos para tasa de descuento y valor terminal

| Componente | Qué requiere | Situación en el repositorio |
|---|---|---|
| Costo de capital propio | Tasa libre de riesgo (bonos soberanos en soles y dólares), prima de mercado, riesgo país y beta | `data/raw/damodaran/` contiene la página de betas sectoriales de EE. UU. (enero de 2026), sin uso validado. No hay series locales de tasas ni de riesgo país incorporadas. La clasificación por industria del Sprint 07 solo cubre unas 463 de 4.221 filas. |
| Costo de deuda y estructura | Deuda financiera, gasto financiero y tasa impositiva | No disponibles. El pasivo total incluye pasivos no financieros. |
| Valor de mercado (para WACC con ponderación de mercado y para comparar con el precio) | Precio y acciones en circulación por emisor | El repositorio solo tiene agregados bursátiles del mercado. No hay precios individuales; la API histórica de BVL figura como no verificada en `reports/bursatil_fuentes.csv`. |
| Valor terminal | Crecimiento de largo plazo y supuestos de reinversión por moneda | Requiere supuestos documentados y un análisis de sensibilidad. |

## 4. Cómo evaluar intervalos probabilísticos y riesgos de cola

Una simulación solo podría presentarse como aporte si sus **pronósticos** se evalúan fuera de muestra con la misma validación temporal:
- **Calibración:** cobertura empírica de los intervalos del 80 % y el 95 % (proporción de observaciones reales dentro del intervalo), por moneda y año.
- **Puntuaciones propias:** CRPS y puntuación de pinball (cuantílica) para los cuantiles 5, 50 y 95, comparadas con referencias probabilísticas simples, como la distribución empírica de residuos de persistencia o de la media histórica.
- **Colas:** frecuencia de excedencias de los cuantiles extremos (prueba de cobertura tipo Kupiec) y error en el cuantil 5 %.
- **Valoración:** si se quiere ir más allá del flujo, comparar la distribución de valor con precios de mercado observados, lo que exige precios por emisor. Esa comparación evalúa coherencia con el mercado, no precisión del flujo.
- **Condiciones:** filas y años idénticos, sin usar 2022–2025 para decidir, con un protocolo versionado antes de ejecutar.

## Resumen de pendientes

**Ya documentados como limitación:**
- disponibilidad temporal de los datos al pronosticar;
- vintages (versiones históricas de las series);
- escala monetaria;
- FCL preliminar ≠ FCFF;
- uso previo de 2022–2025.

**Comprobaciones todavía no realizadas:**
- estados financieros detallados para FCFF y para el efectivo;
- precios por emisor;
- tasas y riesgo país locales;
- protocolo y evaluación de LSTM;
- calibración probabilística.
