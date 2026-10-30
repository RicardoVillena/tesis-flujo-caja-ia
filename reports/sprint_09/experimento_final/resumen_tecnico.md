# Experimento final — resumen técnico (para revisión; no es el informe académico)

**Alcance:**
- Predicción del FCL preliminar t+1 (FCO + CAPEX reportado); **no** es un FCFF validado ni una valoración DCF.
- Población no financiera (regla SMV), con soles y dólares por separado.
- Validación anidada en los años externos 2017–2021, que **ya se habían examinado**: los resultados son exploratorios y no constituyen confirmación independiente. La prueba 2022–2025 no se usó.

**Protocolo:** [protocolo.json](protocolo.json), SHA-256 `c2430bd4…`, escrito el 30 de octubre de 2026 a las 17:04:28, antes de la ejecución completa. Se ejecutó una sola vez; no hubo repeticiones por correcciones de implementación. La única modificación posterior fue visual: los gráficos se regeneraron desde los CSV, truncando el eje y anotando el valor real de las barras extremas.

**Diseño:**
- 3 formulaciones del objetivo: directa, corrección de persistencia y relativa al activo.
- 3 modelos: Ridge, boosting con pérdida cuadrática y boosting con pérdida absoluta.
- 4 variantes de atributos: E0 a E3.
- Rejillas de 8 configuraciones.
- Selección interna por RMSE monetario de las predicciones reconstruidas.
- Mismas filas para los 38 procedimientos de cada moneda: 119 en dólares y 547 en soles.
- Criterio: al menos 1 % menos de RMSE anual medio, mejora en al menos 4 de 5 años y MAE no mayor. No es significancia estadística.
- Se hicieron 156 comparaciones por moneda (312 en total), de modo que algunos cumplimientos pueden ser casuales.

**Verificaciones:**
- La formulación directa con Ridge y boosting cuadrático reproduce la etapa de alineación (diferencia relativa ≤ 5e-15).
- Pruebas de esta etapa: 9 de 9 aprobadas. Suite completa: 124 pruebas, 121 aprobadas y 3 fallos históricos de integridad, sin fallos nuevos ([registro_pruebas.txt](registro_pruebas.txt)).

## Preguntas

### ¿Mejoró la predicción frente a la referencia directa?

Se distinguen tres niveles: reducción observada, consistencia temporal según el criterio, y confirmación independiente (que no existe en ningún caso).

| Contraste | Dólares | Soles |
|---|---|---|
| **Corrección de persistencia frente a directa** | Cumple en 8 de 12 (−11,9 % a −19,1 %): Ridge y boosting absoluto en todas las variantes | Cumple en 8 de 12: boosting cuadrático (≈ −5 %) y absoluto (−7,3 % a −8,7 %). **Ridge empeora mucho** (hasta +52 %). |
| **Relativa frente a directa** (no validada económicamente) | Cumple en 7 de 12 (hasta −26,5 %) | Cumple en 2 de 12. Con pérdida cuadrática **explota** (Ridge 5,4–5,6 millones; boosting 2,0–6,0 millones, frente a 0,26–0,29 millones de la directa): se predicen ratios extremos, aprendidos de casos como FOSSAL (ratio 385), que se multiplican por activos grandes o sospechosos (CD0009 2016). |
| **Pérdida absoluta frente a cuadrática** | 0 de 12: reducciones de −1,7 % a −7,8 %, pero solo en 2 o 3 de 5 años | Cumple en 11 de 12: directa −2,6 % a −3,5 %, persistencia −5,6 % a −6,3 % (5 de 5 años). En la relativa, −88 % a −96 % frente a una base que explotó (no es una mejora sustantiva). |
| **Boosting frente a Ridge** | 4 de 12 (formulación relativa) | 4 de 12 (formulación directa, ≈ −9,7 %) |

### ¿Superó a la persistencia y a la media histórica?

- **Media histórica:** la superan de forma consistente 35 de 36 procedimientos en dólares y 24 de 36 en soles, entre ellos todos los de formulación directa.
- **Persistencia:** solo la superan de forma consistente:
  - `persistencia|boosting_abs:E1` en **ambas monedas**: dólares −1,75 % de RMSE, MAE −4,17 %, 5 de 5 años; soles −1,06 %, MAE −3,26 %, 4 de 5 años (peor año +7,5 %);
  - `persistencia|boosting_abs:E3` en dólares: −1,06 %, 4 de 5 años.

  Son márgenes pequeños, apenas por encima del umbral, elegidos entre 36 procedimientos por moneda.
- **Menor error observado sin consistencia:** en dólares, el menor RMSE observado es de `relativa|boosting:E1` (171.286, −10,8 % frente a la persistencia), pero mejora solo en 2 de 5 años, con un peor año de +22 %: **no es consistente**.

### ¿Las variables externas aportaron una mejora consistente?

**No de forma general.** Cumplen 5 de 36 comparaciones en dólares y 1 de 36 en soles:
- 5 de esos 6 cumplimientos están en la formulación relativa, que no está validada: en dólares, Ridge E3 frente a E0 y E2 frente a E1, y boosting E1 y E2 frente a E0 (−14,6 % y −13,8 %, sobre un modelo con alta varianza); en soles, `relativa|boosting_abs:E1` frente a E0 (−3,73 %, 4 de 5).
- El único cumplimiento fuera de la formulación relativa es el aporte macroeconómico de `persistencia|boosting_abs:E1` frente a E0 en dólares (−1,37 %, 4 de 5).

No se repiten de forma coherente entre formulaciones, modelos y monedas, y con 72 comparaciones de este tipo algunos cumplimientos aislados son esperables por azar. No respaldan un aporte consistente de las variables externas.

### ¿Qué resultados dependen de pocas empresas?

- **Concentración:** según el procedimiento, 3 empresas concentran entre el 77 % y el 92 % del error cuadrático en dólares, y entre el 71 % y el 100 % en soles ([concentracion_error.csv](concentracion_error.csv)).
- **Empresas dominantes de la persistencia:** Cerro Verde (60 %) en dólares, y Shougang (44 %) y Backus (38 %) en soles. Ver [auditoria_unidades.md](auditoria_unidades.md).
- **Sensibilidad predefinida:** se excluyó de la evaluación, sin reajustar, a la empresa dominante (CM0006 en dólares, CM0004 en soles) ([resumen_comparaciones_sin_empresa_dominante.csv](resumen_comparaciones_sin_empresa_dominante.csv)):
  - La ventaja de `persistencia|boosting_abs` frente a la persistencia **se mantiene y aumenta**: E1 −2,78 % en dólares y −2,07 % en soles. E2 y E3 pasan a cumplir en ambas monedas.
  - Varios aportes de las variables externas cambian de estado: aparecen o desaparecen según la empresa excluida. Es otra señal de inestabilidad.
- **Formulación relativa:** sus errores dependen de unos pocos casos de activo casi nulo o con escala sospechosa.

### ¿Qué limitaciones siguen pendientes?

- **Confirmación:** 2017–2021 ya se habían examinado, y hacen falta datos no examinados con este protocolo congelado.
- **Datos:**
  - Unidades y escala no acreditadas: casos sospechosos sin conciliar y compatibilidad activo-flujo sin verificar, lo que impide validar la formulación relativa.
  - Disponibilidad temporal de los datos al pronosticar y versiones históricas no acreditadas; la persistencia y la corrección de persistencia usan FCL(t), que requiere conocer los estados de t.
  - La población por `TipoSector` no está acreditada como históricamente vigente, y hay 78 empresas dudosas.
- **Modelo:**
  - La pérdida absoluta se seleccionó por RMSE, por decisión del protocolo, para comparar en la misma métrica.
  - El efectivo y equivalentes no está disponible en los datos.
  - FCL preliminar ≠ FCFF; no hay valoración DCF.

## Archivos

| Contenido | Archivos |
|---|---|
| Protocolo y entorno | `protocolo.json`, `entorno.json` |
| Auditoría | `auditoria_unidades.md`, `auditoria_unidades_casos.csv`, `auditoria_unidades_resumen.json` |
| Búsquedas y selección | `busquedas_internas.csv`, `configuraciones_seleccionadas.csv` |
| Predicciones con identificadores y valores reconstruidos | `predicciones.csv`: objetivo transformado predicho, `base_t`, `activo_t` y respaldo |
| Métricas | `metricas_por_anio.csv`, `resumen_procedimientos.csv` |
| Comparaciones | `comparaciones_por_anio.csv`, `resumen_comparaciones.csv`, `resumen_comparaciones_sin_empresa_dominante.csv` |
| Concentración y verificación | `concentracion_error.csv`, `verificacion_reproduccion.json`, `registro_pruebas.txt` |
| Gráficos | `graficos/` |
