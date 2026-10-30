# Matriz de operacionalización — alineación con el plan de tesis

**Estado:** propuesta. Complementa la matriz de operacionalización del Sprint 09 ([../matriz_operacionalizacion.md](../matriz_operacionalizacion.md)), sin reemplazarla.
- Agrega la población, el tamaño, el apalancamiento y el efectivo.
- Separa las variables del plan de tesis que no tienen datos disponibles.

**Convenciones:**
- Unidad de análisis: empresa (RPJ) y ejercicio.
- Horizonte: un ejercicio.
- Soles y dólares se miden y evalúan por separado.

## Variables implementadas

| Variable y papel | Definición conceptual | Dimensión | Definición operacional | Medición y unidad | Fuente |
|---|---|---|---|---|---|
| Población de estudio (criterio de inclusión) | Empresas no financieras emisoras (plan de tesis, Ali 2026) | Sector | Se incluye la fila si `TipoSector` SMV ∉ {BANCOS, SEGUROS, FINANCIERAS, A.F.P.}. Las dudosas se conservan y se listan: DIVERSOS con CIIU 64–67, o sin CIIU ni actividad documentada. Sensibilidad conservadora: excluye también DIVERSOS con CIIU 64–67 | Categórica (incluida / excluida / dudosa) | Panel SMV (`TipoSector`); CIIU y actividad: catálogo del Sprint 07 |
| Tamaño empresarial — independiente | Escala de la empresa | Tamaño | `log_activo_total` = ln(ActivoTotal(t)), ActivoTotal > 0 | Logaritmo de la unidad monetaria reportada. La escala no está acreditada: un cambio entre unidades y miles desplaza el valor en ≈ 6,9 | SMV: ActivoTotal |
| Apalancamiento — independiente | Estructura de capital contable | Endeudamiento | `pasivo_activo` = PasivoTotal(t) / ActivoTotal(t), con denominador > 0 (igual al LEV de Ali, 2026) | Fracción; puede superar 1 | SMV |
| Generación histórica de caja — independiente | Persistencia y variabilidad del flujo | Memoria temporal | Rezagos 1–3 de FCO y FCL preliminar, desviación estándar de los 3 años previos y cambio sobre el activo previo (ingeniería de atributos existente) | Unidad monetaria reportada, o fracción del activo | SMV |
| Bloques macroeconómico y bursátil — independientes | Entorno económico y de mercado agregado | Actividad, precios, política monetaria y mercado | Los mismos 7 atributos del Sprint 09, del año t | Porcentajes, S/ por US$ y millones de PEN | BCRP y agregados bursátiles |
| FCL preliminar(t+1) — dependiente | Aproximación al flujo después de la inversión reportada | Flujo futuro | FCO(t+1) + CAPEX_reportado(t+1). Misma empresa, ejercicio consecutivo exacto y misma moneda. Inválido si el CAPEX es positivo y no se imputa | Unidad monetaria reportada; **no es FCFF validado** | SMV |

## Variables del plan sin datos disponibles

| Variable del plan | Estado |
|---|---|
| Reservas de efectivo (efectivo y equivalentes / activo) | **No construible.** El panel y los XML de SMV InfoFinanciera solo tienen activo, pasivo, patrimonio, ingresos y utilidad, más FCO y CAPEX. Requiere estados detallados. **No se sustituye por FCO.** |
| Valor intrínseco / valor de la empresa / precio de la acción | No hay precios por emisor ni capitalización individual. El FCL preliminar no es un valor. |
| Índices de incertidumbre global (WUI, GPR, ESGUI, sentimiento mediático) | No incorporados. Requieren una fuente nueva y la verificación de su disponibilidad temporal. |
| WACC, beta, tasa libre de riesgo, riesgo país, valor terminal | No incorporados (ver [viabilidad_pendientes.md](viabilidad_pendientes.md)). |
| Eficiencia operativa impulsada por IA, gobernanza Human-in-the-Loop | Sin operacionalización posible con los datos actuales. |

## Indicadores de evaluación

Son los mismos del Sprint 09:
- RMSE y MAE por año y moneda, con promedio simple de años.
- Δ % = 100·(candidato/comparador − 1), donde negativo significa mejora.
- Años con mejora.
- Importancia por retirada: Δ RMSE = sin − completo, donde positivo significa que el atributo aporta.

**Regla exploratoria:** al menos 1 % menos de RMSE, mejora en al menos 4 de 5 años y MAE no mayor. No es significancia estadística.
