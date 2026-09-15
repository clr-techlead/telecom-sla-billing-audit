"""
report_generator.py

Automatiza la generación de un reporte ejecutivo en Excel a partir de
los resultados de la auditoría, reemplazando lo que en un flujo manual
sería copiar y pegar tablas en Word/Excel caso por caso.

Salida: outputs/reporte_ejecutivo_sla.xlsx con dos hojas:
  - Resumen: KPIs de la auditoría.
  - Detalle_por_pais: desglose de casos e impacto económico.
"""

import pandas as pd
from sla_audit import audit_sla, summarize_impact


def build_report(input_csv: str, output_xlsx: str):
    raw = pd.read_csv(input_csv)
    audited = audit_sla(raw)
    impact = summarize_impact(audited)

    resumen = pd.DataFrame([
        {"Métrica": "Casos totales analizados", "Valor": impact["total_cases"]},
        {"Métrica": "Casos marcados como incumplidos sin serlo (falso breach)", "Valor": impact["cases_flipped_by_defect"]},
        {"Métrica": "% de casos con falso breach", "Valor": f"{impact['pct_cases_flipped']}%"},
        {"Métrica": "Monto expuesto a penalidad indebida (USD)", "Valor": impact["billing_exposed_usd"]},
        {"Métrica": "Cumplimiento SLA reportado (con defecto)", "Valor": f"{impact['sla_compliance_naive_pct']}%"},
        {"Métrica": "Cumplimiento SLA real (lógica corregida)", "Valor": f"{impact['sla_compliance_correct_pct']}%"},
        {"Métrica": "Brecha de cumplimiento subestimada", "Valor": f"{abs(impact['compliance_gap_points'])} pts"},
    ])

    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        resumen.to_excel(writer, sheet_name="Resumen", index=False)
        impact["breakdown_by_country"].to_excel(writer, sheet_name="Detalle_por_pais")

    print(f"Reporte ejecutivo generado en: {output_xlsx}")


if __name__ == "__main__":
    build_report("data/synthetic_cases.csv", "outputs/reporte_ejecutivo_sla.xlsx")
