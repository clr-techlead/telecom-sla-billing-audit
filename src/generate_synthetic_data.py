"""
generate_synthetic_data.py

Genera un dataset SINTÉTICO de casos de soporte/facturación para una
operación de telecomunicaciones ficticia, con un defecto de lógica de
negocio inyectado a propósito (igual en espíritu al que se audita en
sla_audit.py). Todos los nombres, países y volúmenes son inventados
para fines de portafolio; no representan ninguna operación real.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_CASES = 12000
COUNTRIES = ["País A", "País B", "País C", "País D"]
CASE_TYPES = ["Reclamo de facturación", "Falla de servicio", "Solicitud técnica", "Ajuste de plan"]

# SLA objetivo por tipo de caso, en horas hábiles
SLA_TARGET_HOURS = {
    "Reclamo de facturación": 48,
    "Falla de servicio": 24,
    "Solicitud técnica": 72,
    "Ajuste de plan": 24,
}

def business_hours_between(start: datetime, end: datetime) -> float:
    """Calcula horas hábiles (L-V, 8am-6pm) entre dos timestamps."""
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

        # Tiempo de resolución real: la mayoría cumple, algunos se pasan
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
    print(f"Dataset sintético generado: {len(df)} casos -> data/synthetic_cases.csv")
