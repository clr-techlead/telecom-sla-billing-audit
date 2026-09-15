"""
sla_audit.py

Business case (portfolio):
---------------------------
An SLA compliance report calculated resolution time using calendar
hours (24/7) instead of business hours (Mon-Fri, 8am-6pm). Since the
calendar clock never stops (it includes nights and weekends), a case
opened on a Friday afternoon would accumulate hours quickly and show
up as "breached" — even though, measured in real business hours, the
team had resolved it within the target window.

This produced SLA breaches that were not real, with two business
consequences: (1) exposure to penalties or service credits that did
not actually apply, and (2) a worse-than-real performance picture in
front of the client.

This script:
  1. Calculates compliance using the DEFECTIVE logic (calendar hours).
  2. Calculates compliance using the CORRECT logic (business hours).
  3. Quantifies how many cases were wrongly flagged as breaches and how
     much billing amount was exposed to an undue penalty.
"""

import pandas as pd
from generate_synthetic_data import business_hours_between


def audit_sla(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["opened_at"] = pd.to_datetime(df["opened_at"])
    df["closed_at"] = pd.to_datetime(df["closed_at"])

    # --- DEFECTIVE logic: calendar hours ---
    df["resolution_hours_naive"] = (
        df["closed_at"] - df["opened_at"]
    ).dt.total_seconds() / 3600
    df["sla_met_naive"] = df["resolution_hours_naive"] <= df["sla_target_hours"]

    # --- CORRECT logic: business hours ---
    df["resolution_hours_business"] = df.apply(
        lambda r: business_hours_between(r["opened_at"], r["closed_at"]), axis=1
    )
    df["sla_met_correct"] = df["resolution_hours_business"] <= df["sla_target_hours"]

    # --- Cases wrongly flagged as BREACHED when they actually met SLA ---
    # (the calendar-hours logic over-penalizes relative to business hours)
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
        .agg(affected_cases=("case_id", "count"), amount_exposed_usd=("billing_amount_usd", "sum"))
        .sort_values("affected_cases", ascending=False)
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
    print("SLA CALCULATION LOGIC AUDIT — RESULTS")
    print("=" * 60)
    print(f"Total cases analyzed:               {impact['total_cases']:,}")
    print(f"Cases wrongly flagged as breached    {impact['cases_flipped_by_defect']:,} "
          f"({impact['pct_cases_flipped']}%)")
    print(f"  (false breach):")
    print(f"Amount exposed to undue penalty:    USD {impact['billing_exposed_usd']:,.2f}")
    print(f"Reported compliance (with defect):  {impact['sla_compliance_naive_pct']}%")
    print(f"Real compliance (corrected):         {impact['sla_compliance_correct_pct']}%")
    print(f"Underestimated compliance gap:       {abs(impact['compliance_gap_points'])} points")
    print()
    print("Breakdown by country (top affected):")
    print(impact["breakdown_by_country"])
