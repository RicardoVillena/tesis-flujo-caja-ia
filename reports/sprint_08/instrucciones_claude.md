# Instrucciones para Claude — Sprint 08, Etapa 1

Fecha: 24 de octubre de 2026.

## Acuerdo de trabajo

Claude programa y Codex realiza posteriormente la auditoría independiente. La implementación inicial de Codex queda disponible como punto de partida; sus resultados deben verificarse, no aceptarse como autoridad. No se ha invocado a Claude desde esta sesión: estas instrucciones permiten continuar el trabajo con él.

## Encargo

Actúa como científico de datos senior, especialista en econometría financiera, Machine Learning y metodología de investigación, y como programador responsable del Sprint 08 — Etapa 1: auditoría de calidad de los 26 atributos de E2 en `tesis-flujo-caja-ia`, tesis de Maestría en Inteligencia Artificial de la UNI.

Objetivo de la tesis: predecir el Flujo de Caja Libre de empresas peruanas mediante información financiera SMV, indicadores macroeconómicos BCRP y variables bursátiles.

Ya existe una implementación inicial. Revísala, corrígela y completa lo que falte, verificando cada afirmación contra el código y los datos originales. Codex auditará después tus cambios. Esta etapa no incluye selección definitiva ni evaluación experimental de nuevos modelos.

## Antes de editar

1. Lee las instrucciones AGENTS.md que correspondan.
2. Revisa `git status` y confirma la rama local `sprint-08-auditoria-calidad`.
3. Identifica y preserva todos los cambios existentes, incluidos los archivos no rastreados de Sprint 07. No uses reset, clean ni restauraciones que descarten trabajo ajeno.
4. Inspecciona:
   - `src/auditoria_calidad.py`
   - `scripts/reproduce_auditoria_calidad.py`
   - `tests/test_auditoria_calidad.py`
   - `notebooks/sprint_08/11_auditoria_calidad_atributos.ipynb`
   - `reports/sprint_08/`
5. Registra el estado inicial y hashes de los archivos previos que deban preservarse antes de cualquier edición.

## Verificación de la especificación original

Recupera directamente de los notebooks, catálogos y código de Sprint 06:

- Scripts, notebooks y reportes utilizados por E0, E1 y E2.
- Nombres y orden exactos de los 26 predictores de E2; no asumirlos.
- Clasificación en financieros, macroeconómicos y bursátiles.
- Definición de `objetivo_fcl_t1`, horizonte y reglas de elegibilidad.
- Imputación y escalamiento de la configuración principal y sus sensibilidades.

Referencias iniciales: notebooks 07, 08 y 09; `reports/sprint_06/`; `src/feature_engineering.py`; diccionarios de integración financiera, macroeconómica y bursátil. No ejecutes notebooks anteriores si ello vuelve a entrenar modelos o sobrescribe sus reportes.

## Trabajo requerido

Revisa y completa la implementación para producir:

- Diccionario por atributo: nombre exacto, definición financiera o estadística, unidad, escala, fuente original y evidencia localizable.
- Calidad por atributo y moneda: tipo, faltantes (cantidad y porcentaje), mínimo, máximo, media, mediana, desviación estándar, asimetría, percentiles 1/5/25/50/75/95/99, límites y extremos RIQ, constantes, infinitos e indefinidos. Define claramente cada conteo.
- Cobertura temporal: diferencia ausencia estructural por rezagos de otros faltantes cuando la evidencia lo permita.
- Denominadores positivos pequeños: criterio explícito y casos identificables por empresa y ejercicio; revisar consistencia económica de ratios y variaciones.
- Matrices Pearson y Spearman, tamaños efectivos de muestra y pares altamente correlacionados.
- VIF cuando sea apropiado; constantes, duplicados y dependencias lineales, documentando imputación, tolerancias y limitaciones.
- Auditoría temporal por atributo con una categoría exacta:
  - DISPONIBILIDAD VERIFICADA
  - DISPONIBILIDAD NO VERIFICADA
  - POSIBLE FUGA TEMPORAL
- Tabla final de los 26 atributos con: nombre, origen, definición, calidad, redundancia, riesgo temporal, observaciones metodológicas y recomendación provisional de revisión.

Todos los diagnósticos utilizables para selección deben calcularse exclusivamente sobre entrenamiento. Respeta la separación por moneda. No uses resultados de prueba para recomendar atributos.

## Puntos de revisión especial

- Correlación alta no demuestra dependencia lineal exacta ni irrelevancia predictiva.
- Las series macroeconómicas repetidas entre empresas no son observaciones temporales independientes.
- Justifica el cálculo e interpretación del VIF con imputación y estructura de panel.
- Distingue año de referencia, fecha de publicación, vintage y fecha de pronóstico.
- No certifiques disponibilidad histórica por la sola alineación t → t+1. Un dato del año t no necesariamente estaba publicado al cierre de t.
- No declares erróneo un extremo sin evidencia documental.
- Un umbral exploratorio para denominadores pequeños no es una regla financiera universal.
- Comprueba que las pruebas de aislamiento temporal perturben efectivamente prueba y puedan detectar contaminación.
- Los hashes calculados después de una modificación no prueban conservación respecto del estado anterior.
- No declares que un atributo genera ruido predictivo: requiere la siguiente etapa experimental.
- Separa problemas comprobados de sospechas que requieren investigación adicional.

## Entregables

Conservar en `reports/sprint_08/`:

```text
diccionario_atributos.csv
calidad_atributos.csv
correlaciones_pearson.csv
correlaciones_spearman.csv
diagnostico_vif.csv
auditoria_temporal.csv
hallazgos_calidad.csv
resumen_auditoria.md
```

Añade anexos cuando aporten trazabilidad, incluida la tabla completa de 26 atributos. Mantén el notebook canónico `notebooks/sprint_08/11_auditoria_calidad_atributos.ipynb` reproducible. Cada celda de código debe estar precedida por una celda Markdown con título breve en negrita, sin encabezados grandes, y una o dos líneas de explicación técnica. Incluye interpretaciones breves de resultados principales y ejecuta el notebook completo.

## Restricciones obligatorias

- Preservar las 4,221 observaciones originales y las 3,560 elegibles.
- No modificar FCL ni las particiones: objetivos de entrenamiento 2006–2021 y prueba 2022–2025.
- No eliminar atributos ni entrenar modelos nuevos.
- No modificar E0/E1/E2, Sprint 06, Sprint 07 ni datos originales.
- No sobrescribir fuentes originales.
- No hacer commit, push ni Pull Request; no modificar main.
- Trabajar exclusivamente en la rama local `sprint-08-auditoria-calidad`.
- No descartar, limpiar ni sobrescribir cambios ajenos.

## Validación y entrega a Codex

Ejecuta pruebas automatizadas pertinentes y verifica conservación de los archivos previos. Comandos iniciales, usando el entorno existente `tesis-fcl`:

```bash
/home/ricardo/miniconda3/envs/tesis-fcl/bin/python scripts/reproduce_auditoria_calidad.py
/home/ricardo/miniconda3/envs/tesis-fcl/bin/python -m unittest discover -s tests -v
```

Ejecuta también el notebook con ese entorno. Informa cualquier restricción del entorno sin simular ejecuciones ni resultados.

Entrega un informe breve con archivos modificados, correcciones, comandos ejecutados, resultados reales de pruebas y limitaciones pendientes. Deja los cambios locales disponibles para la auditoría independiente de Codex.

## Estado comunicado antes de este traspaso

La ejecución inicial comunicó: E2 con 19 atributos financieros, 4 macroeconómicos y 3 bursátiles; 49 pruebas aprobadas; notebook ejecutado; 1,499 archivos previos con hashes preservados. Detectó correlaciones superiores a 0.999 y VIF máximo cercano a 7,942.55 en soles, sin constantes, infinitos ni dependencias lineales exactas detectadas. No acreditó disponibilidad histórica real. Estos resultados son antecedentes que Claude debe verificar de nuevo; no sustituyen su revisión ni la auditoría posterior de Codex.
