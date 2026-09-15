# Auditoría de lógica de SLA y exposición de facturación en telecomunicaciones

Pipeline en Python que detecta y cuantifica un defecto de lógica de negocio en el cálculo de cumplimiento de SLA, y automatiza el reporte ejecutivo del hallazgo.

> **Nota sobre los datos:** este repositorio usa datos 100% sintéticos generados con una semilla fija, sin ninguna relación con clientes, empleadores o información real. El objetivo es mostrar la metodología de auditoría de datos aplicada a un problema real de la industria de telecomunicaciones (facturación ligada a cumplimiento de SLA), no exponer información confidencial de ningún tercero.

## El problema de negocio

En operaciones de telecomunicaciones, el cumplimiento de SLA suele estar directamente ligado a la facturación: un caso que incumple el SLA puede generar penalidad contractual o crédito de servicio al cliente.

Un patrón de error común: la lógica de cálculo mide el tiempo de resolución en **horas corridas (24/7)** en lugar de **horas hábiles (lunes a viernes, horario laboral)**. Como el reloj corrido nunca se detiene, un caso abierto un viernes por la tarde acumula horas rápidamente durante el fin de semana y aparece como "incumplido" — aunque el equipo lo resolvió dentro del tiempo hábil real.

El resultado: casos marcados como incumplimiento que en realidad sí cumplieron, con dos consecuencias:

1. **Económica** — exposición a penalidades o créditos de servicio que no correspondían.
2. **Reputacional** — una imagen de desempeño peor que la real frente al cliente.

## Qué hace este proyecto

| Script | Función |
|---|---|
| `src/generate_synthetic_data.py` | Genera 12,000 casos sintéticos de soporte/facturación con fecha de apertura, cierre, tipo de caso y SLA objetivo. |
| `src/sla_audit.py` | Calcula el cumplimiento con la lógica defectuosa (horas corridas) y con la lógica correcta (horas hábiles), y cuantifica la diferencia. |
| `src/report_generator.py` | Automatiza la generación de un reporte ejecutivo en Excel a partir de la auditoría — reemplaza el armado manual de tablas caso por caso. |

## Resultado de la auditoría (sobre datos sintéticos)

```
Casos totales analizados:              12,000
Casos marcados como incumplidos
  sin serlo realmente (falso breach):  4,149  (34.58%)
Monto expuesto a penalidad indebida:   USD 494,290.74
Cumplimiento reportado (con defecto):  64.22%
Cumplimiento real (corregido):         98.79%
Brecha de cumplimiento subestimada:    34.57 puntos
```

Es decir: con la lógica correcta, el cumplimiento real de esta operación sintética es 98.79%, no 64.22% como reportaba el cálculo defectuoso — una brecha de más de 34 puntos porcentuales, con casi medio millón de dólares en facturación potencialmente afectada por una penalidad que no debía aplicarse.

## Cómo correrlo

```bash
pip install -r requirements.txt
python src/generate_synthetic_data.py   # genera data/synthetic_cases.csv
python src/sla_audit.py                  # corre la auditoría, imprime resumen
python src/report_generator.py           # genera outputs/reporte_ejecutivo_sla.xlsx
```

## Stack técnico

- **Python** — pandas, numpy para el pipeline de datos
- **openpyxl** — generación automatizada de reportes Excel
- Lógica de negocio modularizada: generación de datos, motor de auditoría y capa de reporting están separados, replicando cómo se estructura un pipeline de producción real

## Contexto

Este proyecto está inspirado en el tipo de trabajo que hago como analista de datos en telecomunicaciones: gestión de reporting de SLA y facturación para operaciones multipaís, y detección de inconsistencias en la lógica de cálculo con impacto económico directo. Los datos y cifras de este repositorio son ilustrativos; no corresponden a ningún empleador ni cliente real.

---

**Camilo Andrés León Rubriche** — Data & BI Analyst
[LinkedIn](https://linkedin.com/in/tu-usuario) · [correo](mailto:camiloleonrubriche@outlook.com)
