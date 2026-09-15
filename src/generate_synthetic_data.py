"""
generate_synthetic_data.py

Generates a SYNTHETIC dataset of support/billing cases for a fictional
telecom operation, with a business-logic defect injected on purpose
(same spirit as the one audited in sla_audit.py). All names, countries
and volumes are made up for portfolio purposes; they do not represent
any real operation.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_CASES = 12000
COUNTRIES = ["Country A", "Country B", "Country C", "Country D"]
CASE_TYPES = ["Billing complaint", "Service outage", "Technical request", "Plan change"]

# Target SLA per case type, in business hours
SLA_TARGET_HOURS = {
    "Billing complaint": 48,
    "Service outage": 24,
    "Technical request": 72,
    "Plan change": 24,
}

def business_hours_between(start: datetime, end: datetime) -> float:
    """Computes business hours (Mon-Fri, 8am-6pm) between two timestamps."""
    if end <= start:
        return 0.0
    total_hours = 0.0
    current = start
    while current < end:
        if current.weekday() < 5 and 8 <= current.hour < 18:
            total_hours += 1
        current += timedelta(hours=1)
    return total_hours

def generate_dataset():
    rows = []
    base_date = datetime(2025, 1, 1)

    for i in range(N_CASES):
        country = np.random.choice(COUNTRIES, p=[0.35, 0.30, 0.20, 0.15])
        case_type = np.random.choice(CASE_TYPES)
        target = SLA_TARGET_HOURS[case_type]

        opened_at = base_date + timedelta(
            days=np.random.randint(0, 365),
            hours=np.random.randint(0, 24),
        )

        # Real resolution time: most cases meet the target, some overrun
        resolution_hours_real = np.random.gamma(shape=2.0, scale=target / 2.2)
        closed_at = opened_at + timedelta(hours=float(resolution_hours_real))

        billing_amount = round(np.random.uniform(15, 220), 2)

        rows.append({
            "case_id": f"C-{100000 + i}",
            "country": country,
            "case_type": case_type,
            "opened_at": opened_at,
            "closed_at": closed_at,
            "sla_target_hours": target,
            "billing_amount_usd": billing_amount,
        })

    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("data/synthetic_cases.csv", index=False)
    print(f"Synthetic dataset generated: {len(df)} cases -> data/synthetic_cases.csv")
