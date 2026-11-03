# Memoria de decisiones y propuestas de investigación

## 30 de octubre de 2026 — Objetivos orientados al accionista

El usuario comunica que el profesor considera los objetivos demasiado académicos y pide orientarlos al beneficio del accionista o a la reducción de incertidumbre.

Estado: propuesta pendiente de evaluación. No reemplazar todavía el objetivo general, los objetivos específicos, las hipótesis ni las matrices oficiales. El usuario solicita conservar esta observación para evaluarla; no autoriza nuevos experimentos mediante este registro.

Propuesta de objetivo general para evaluar: desarrollar una herramienta de apoyo al accionista para estimar la generación futura de caja y cuantificar su incertidumbre, facilitando la evaluación del riesgo de inversión.

Posibles objetivos específicos: mejorar la precisión frente a referencias simples; proporcionar intervalos de predicción para escenarios favorables y adversos; identificar las variables que permitan interpretar las estimaciones.

El modelo actual predice FCL preliminar y presenta mejoras exploratorias de error, además de importancia por retirada de atributos. Todavía no genera intervalos validados ni demuestra mayor rentabilidad para el accionista. El FCL preliminar no equivale a flujo disponible al accionista ni a FCFF validado.

Cuantificar incertidumbre requiere implementar intervalos de predicción y evaluar cobertura y amplitud fuera de muestra. Una menor incertidumbre estimada solo es favorable si mantiene calibración adecuada; intervalos estrechos por sí solos no demuestran mejora.

Maximizar el beneficio del accionista requiere definir una decisión o estrategia, medir rentabilidad y riesgo, e incorporar precios, dividendos y costos según corresponda. No atribuir esa capacidad al modelo actual ni confundir menor error predictivo con mayor beneficio económico o menor incertidumbre del negocio.

Próxima revisión: definir el usuario y decisión concreta a apoyar; distinguir incertidumbre del pronóstico de riesgo económico; evaluar disponibilidad de datos y alcance viable; después proponer objetivos, hipótesis e indicadores consistentes para revisión con el asesor.

Preferencia vigente del usuario: no hacer commits ni publicaciones sin autorización explícita para la acción correspondiente.

## 30 de octubre de 2026 — Mejoras e hiperparámetros solicitados por el profesor

El usuario añade que el profesor solicita las mejoras y los hiperparámetros. Registrar como pendiente de la próxima revisión y entrega; este registro no autoriza nuevos experimentos ni publicación.

Preparar una explicación breve de los cambios respecto al modelo anterior: población no financiera, corrección de persistencia, pérdida absoluta y variantes de atributos. Separar el efecto de la formulación, el algoritmo y las variables externas. Mostrar cambios de RMSE y MAE, años con mejora y limitaciones; no confundir mejoras del procedimiento con aporte incremental de variables.

Documentar los hiperparámetros buscados, sus valores candidatos, los parámetros fijos y las configuraciones efectivamente seleccionadas por moneda y año externo. Explicar el criterio de selección interna temporal y el presupuesto de búsqueda. No presentar una configuración única como si hubiera sido usada en todos los pliegues ni atribuir a un hiperparámetro una mejora aislada sin un contraste que lo demuestre.

Fuentes existentes: reports/sprint_09/experimento_final/protocolo.json, configuraciones_seleccionadas.csv, busquedas_internas.csv y resumen_comparaciones.csv; código en src/experimento_final.py y módulos reutilizados. Verificar contra estas fuentes antes de incorporar cifras al informe o notebook.
