# Auditoría de unidades y casos extremos (previa al entrenamiento)

El detalle caso por caso está en [auditoria_unidades_casos.csv](auditoria_unidades_casos.csv) y el resumen en [auditoria_unidades_resumen.json](auditoria_unidades_resumen.json). Esta auditoría **no corrigió ningún valor** y **no generó una versión derivada** de los datos.

## Evidencia disponible sobre unidades, miles y moneda

- **XML de SMV (InfoFinanciera):** incluyen moneda (`Soles` o `D lares`) pero **ningún campo de unidad ni de escala**. Los valores del panel coinciden con esos XML (`reports/procedimiento_smv.md`); por tanto, los casos extremos no son errores de nuestra extracción.
- **Documentación del repositorio:** declara la escala "no acreditada" (`data/README.md`, `reports/trazabilidad_variables.md`). La única rotulación explícita encontrada es "S/ miles", en un Excel de análisis de Aceros Arequipa (`reports/procedimiento_smv.md`) que no forma parte del panel.
- **FCO y CAPEX:** provienen de otra operación SMV (FlujoEfectivo) cuya extracción histórica no es reproducible. La compatibilidad de escala entre el activo y el flujo de una misma fila no está acreditada.
- **Identidad contable:** activo = pasivo + patrimonio se cumple en las 4.221 filas, sin ninguna violación. Una inconsistencia de escala que afecte por igual a todo un balance no se detecta con esta comprobación.
- **Ratio FCL(t+1) / Activo(t)** en entrenamiento no financiero: mediana 0,033 y percentiles 1 % y 99 % de −0,48 y 0,52. La mayoría es coherente con una misma escala. Hay 13 filas con |ratio| > 1 y 5 con |FCO/activo| > 1.

## Clasificación de los casos

| Tipo | Casos | Clasificación | Decisión |
|---|---|---|---|
| Errores comprobados | 0 | Ninguno: no hay evidencia documental de error | — |
| CD0009 (Transacciones Financieras), 2016 | ActivoTotal ×1111 y PasivoTotal ×1478 respecto a 2015, con reversión en 2017; identidad contable consistente | **Sospecha de escala** (compatible con un cambio de unidades), no acreditada | Sin corrección |
| FOSSAL 2016 y NISA Malls 2012–2013 | Activo de 1, 9 y 28 unidades; identidad consistente | **Sospecha:** activo casi nulo (empresa sin operaciones o problema de escala) | Sin corrección |
| Ratios extremos (\|FCL(t+1)/activo\| > 1 o \|FCO/activo\| > 1) | 17 filas en total (incluye CD0009, FOSSAL y NISA; ver CSV) | El resto son **no resueltos**. Edyficar Perú 2014 (en DIVERSOS, incluida en la población) tiene un activo que cae de 5,2 millones a 21.430 en 2015: evento o escala, no resuelto. | Sin corrección |
| Saltos de magnitud del Sprint 08 en empresas no financieras | 22 (2 con reversión) | Picos con reversión: sospecha de escala. Sin reversión: evento o escala, no resuelto. | Sin corrección |
| Empresas con mayor error (persistencia, población no financiera) | Dólares: Cerro Verde (60 %), Southern (22 %) y Buenaventura (8 %) del error cuadrático. Soles: Shougang (44 %), Backus (38 %) y Aceros Arequipa (5 %). | Series de activo sin saltos de ×100 o más: **volatilidad económica plausible** (minería e industria), no verificada documentalmente | Sin corrección; **no se excluyen por su error predictivo** |

## Consecuencias para el experimento

- **Fórmula directa y corrección de persistencia:** usan los valores tal como fueron reportados.
- **Formulación relativa:** depende de que activo y flujo estén en la misma escala, y eso no está acreditado. Sus resultados **no se presentan como validados económicamente**. Los casos con activo casi nulo generan ratios de entrenamiento extremos (FOSSAL: 385), y CD0009 2016 multiplica un ratio predicho por un activo sospechoso (67,6 millones). Ambos efectos aparecen en los errores de esa formulación.
- **Casos no resueltos:** se conservan para revisión documental (estados financieros originales) antes de cualquier corrección futura.
