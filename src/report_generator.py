"""
report_generator.py

Automates the generation of an executive Excel report from the audit
results, replacing what in a manual workflow would be copying and
pasting tables into Word/Excel case by case.

Output: outputs/sla_executive_report.xlsx with two sheets:
  - Summary: audit KPIs.
  - Breakdown_by_country: case count and economic impact by country.
"""

import pandas as pd
from sla_audit import audit_sla, summarize_impact


def build_report(input_csv: str, output_xlsx: str):
    raw = pd.read_csv(input_csv)
    audited = audit_sla(raw)
    impact = summarize_impact(audited)

    summary = pd.DataFrame([
        {"Metric": "Total cases analyzed", "Value": impact["total_cases"]},
        {"Metric": "Cases wrongly flagged as breached (false breach)", "Value": impact["cases_flipped_by_defect"]},
        {"Metric": "% of cases with false breach", "Value": f"{impact['pct_cases_flipped']}%"},
        {"Metric": "Amount exposed to undue penalty (USD)", "Value": impact["billing_exposed_usd"]},
        {"Metric": "Reported SLA compliance (with defect)", "Value": f"{impact['sla_compliance_naive_pct']}%"},
        {"Metric": "Real SLA compliance (corrected logic)", "Value": f"{impact['sla_compliance_correct_pct']}%"},
        {"Metric": "Underestimated compliance gap", "Value": f"{abs(impact['compliance_gap_points'])} pts"},
    ])

    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        impact["breakdown_by_country"].to_excel(writer, sheet_name="Breakdown_by_country")

    print(f"Executive report generated at: {output_xlsx}")


if __name__ == "__main__":
    build_report("data/synthetic_cases.csv", "outputs/sla_executive_report.xlsx")
