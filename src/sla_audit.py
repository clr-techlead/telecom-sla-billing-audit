"""
sla_audit.py

Caso de negocio (portafolio):
-----------------------------
Un reporte de cumplimiento de SLA calculaba el tiempo de resolución con
horas corridas (24/7) en lugar de horas hábiles (L-V, 8am-6pm). Como el
reloj corrido nunca se detiene (incluye noches y fines de semana), un
caso abierto un viernes en la tarde acumulaba horas rápidamente y
aparecía como "incumplido", aunque en horas hábiles reales el equipo lo
había resuelto dentro del plazo.

Esto generaba incumplimientos de SLA que no eran reales, con dos
consecuencias de negocio: (1) exposición a penalidades o créditos de
servicio que no correspondían, y (2) una imagen de desempeño peor a la
real ante el cliente.

Este script:
  1. Calcula el cumplimiento con la lógica DEFECTUOSA (horas corridas).
  2. Calcula el cumplimiento con la lógica CORRECTA (horas hábiles).
  3. Cuantifica cuántos casos estaban mal marcados como incumplidos y
     qué monto de facturación quedaba expuesto a penalidad indebida.
"""

import pandas as pd
from generate_synthetic_data import business_hours_between


def audit_sla(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["opened_at"] = pd.to_datetime(df["opened_at"])
    df["closed_at"] = pd.to_datetime(df["closed_at"])

    # --- Lógica DEFECTUOSA: horas corridas ---
    df["resolution_hours_naive"] = (
        df["closed_at"] - df["opened_at"]
    ).dt.total_seconds() / 3600
    df["sla_met_naive"] = df["resolution_hours_naive"] <= df["sla_target_hours"]

    # --- Lógica CORRECTA: horas hábiles ---
    df["resolution_hours_business"] = df.apply(
        lambda r: business_hours_between(r["opened_at"], r["closed_at"]), axis=1
    )
    df["sla_met_correct"] = df["resolution_hours_business"] <= df["sla_target_hours"]

    # --- Casos donde el defecto marca como INCUMPLIDO algo que sí cumplía ---
    # (la lógica de horas corridas penaliza de más frente a la de horas hábiles)
    df["defect_flips_result"] = df["sla_met_correct"] & ~df["sla_met_naive"]

    return df


def summarize_impact(df: pd.DataFrame) -> dict:
    total_cases = len(df)
    flipped = df[df["defect_flips_result"]]
    n_flipped = len(flipped)
    pct_flipped = round(100 * n_flipped / total_cases, 2)
    exposed_billing = round(flipped["billing_amount_usd"].sum(), 2)

    compliance_naive = round(100 * df["sla_met_naive"].mean(), 2)
    compliance_correct = round(100 * df["sla_met_correct"].mean(), 2)

    by_country = (
        flipped.groupby("country")
        .agg(cases_afectados=("case_id", "count"), monto_expuesto_usd=("billing_amount_usd", "sum"))
        .sort_values("cases_afectados", ascending=False)
    )

    return {
        "total_cases": total_cases,
        "cases_flipped_by_defect": n_flipped,
        "pct_cases_flipped": pct_flipped,
        "billing_exposed_usd": exposed_billing,
        "sla_compliance_naive_pct": compliance_naive,
        "sla_compliance_correct_pct": compliance_correct,
        "compliance_gap_points": round(compliance_naive - compliance_correct, 2),
        "breakdown_by_country": by_country,
    }


if __name__ == "__main__":
    raw = pd.read_csv("data/synthetic_cases.csv")
    audited = audit_sla(raw)
    audited.to_csv("outputs/audited_cases.csv", index=False)

    impact = summarize_impact(audited)

    print("=" * 60)
    print("AUDITORÍA DE LÓGICA DE CÁLCULO DE SLA — RESULTADOS")
    print("=" * 60)
    print(f"Casos totales analizados:            {impact['total_cases']:,}")
    print(f"Casos marcados como incumplidos      {impact['cases_flipped_by_defect']:,} "
          f"({impact['pct_cases_flipped']}%)")
    print(f"  sin serlo realmente (falso breach):")
    print(f"Monto expuesto a penalidad indebida: USD {impact['billing_exposed_usd']:,.2f}")
    print(f"Cumplimiento reportado (con defecto):{impact['sla_compliance_naive_pct']}%")
    print(f"Cumplimiento real (corregido):        {impact['sla_compliance_correct_pct']}%")
    print(f"Brecha de cumplimiento subestimada:   {abs(impact['compliance_gap_points'])} puntos")
    print()
    print("Desglose por país (top casos afectados):")
    print(impact["breakdown_by_country"])
