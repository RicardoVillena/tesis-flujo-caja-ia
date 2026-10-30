# Antecedente: versión inicial del Sprint 09 (commit 6eeac16)

Archivos movidos sin cambios desde `reports/sprint_09/` (historia conservada con `git mv`). Los generó la versión inicial de
`scripts/reproduce_sprint_09.py` (código disponible en el commit `6eeac16`): variantes E0–E2, Ridge y boosting, e importancia
individual por retirada con configuración E2 congelada.

Se conservan como antecedente trazable porque sus resultados E0–E2 ya se observaron antes de fijar el protocolo final del
Sprint 09. El protocolo final mantiene sus rejillas y criterios, y verifica que reproduce exactamente sus predicciones E0–E2 y su
importancia individual (`../verificacion_reproduccion.json`). Limitaciones de la versión inicial, corregidas en la final:
sin E3 ni E4, sin importancia por bloques ni sensibilidad t-1, sin comparaciones frente a referencias, protocolo escrito en la misma
ejecución, y pruebas en formato pytest (no instalado) que `unittest` no ejecutaba.
