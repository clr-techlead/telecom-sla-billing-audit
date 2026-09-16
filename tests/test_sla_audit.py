import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sla_audit import audit_sla, summarize_impact
class TestSlaAudit(unittest.TestCase):
    def setUp(self):
        self.cases = pd.DataFrame([
            {"case_id": "C001", "country": "Chile", "opened_at": "2026-01-09 16:00", "closed_at": "2026-01-12 10:00", "sla_target_hours": 4, "billing_amount_usd": 1000.0},
            {"case_id": "C002", "country": "Peru", "opened_at": "2026-01-12 08:00", "closed_at": "2026-01-12 09:00", "sla_target_hours": 4, "billing_amount_usd": 500.0},
        ])
    def test_audit_flags_calendar_hours_false_breach(self):
        audited = audit_sla(self.cases)
        self.assertTrue(audited.loc[0, "defect_flips_result"])
        self.assertFalse(audited.loc[1, "defect_flips_result"])
    def test_summary_quantifies_impact(self):
        impact = summarize_impact(audit_sla(self.cases))
        self.assertEqual(impact["total_cases"], 2)
        self.assertEqual(impact["cases_flipped_by_defect"], 1)
        self.assertEqual(impact["billing_exposed_usd"], 1000.0)
        self.assertEqual(impact["pct_cases_flipped"], 50.0)
if __name__ == "__main__":
    unittest.main()
