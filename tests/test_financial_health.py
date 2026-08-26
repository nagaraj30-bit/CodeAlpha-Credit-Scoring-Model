"""
Credit Scoring Model — Financial Health Indicator Test Suite
============================================================
Unit and integration tests for Phase 5 Financial Health Indicator:
1. Deterministic calculation and reproducibility.
2. Score range boundedness [0, 100].
3. Component weight sum equals 1.00 (100%).
4. Presentation health label mappings (EXCELLENT, GOOD, FAIR, POOR).
5. Mathematical resilience to division-by-zero (LIMIT_BAL=0).
6. Handling of negative bill amounts (refunds / credit balances).
7. Handling of missing optional values via pipeline imputation.
8. Score monotonicity (on-time applicant scores strictly higher than delinquent applicant).
9. Component schema completeness (name, score, weight, status, explanation).
10. Disclaimer and terminology verification.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from data_loader import load_credit_data
from financial_health import (
    COMPONENT_WEIGHTS,
    FINANCIAL_HEALTH_DISCLAIMER,
    calculate_financial_health,
    determine_health_label,
)


class TestFinancialHealthIndicator(unittest.TestCase):
    """Test suite for the deterministic Financial Health Indicator engine."""

    @classmethod
    def setUpClass(cls):
        cls.data_path = "data/credit_data.csv"
        cls.df_raw, _ = load_credit_data(cls.data_path)

        # Clean profile: All payments on-time (status <= 0)
        clean_mask = (cls.df_raw["PAY_0"] <= 0) & (cls.df_raw["PAY_2"] <= 0) & (cls.df_raw["PAY_3"] <= 0)
        cls.applicant_clean = cls.df_raw[clean_mask].iloc[0].to_dict()

        # Delinquent profile: Multiple months overdue
        delinq_mask = (cls.df_raw["PAY_0"] >= 2) & (cls.df_raw["PAY_2"] >= 2)
        cls.applicant_delinq = cls.df_raw[delinq_mask].iloc[0].to_dict()

    def test_01_component_weights_sum_to_one(self):
        """Verify that all 5 component weights sum precisely to 1.0 (100%)."""
        total_weight = sum(COMPONENT_WEIGHTS.values())
        self.assertAlmostEqual(total_weight, 1.0, places=5)
        self.assertEqual(len(COMPONENT_WEIGHTS), 5)
        self.assertIn("payment_timeliness", COMPONENT_WEIGHTS)
        self.assertIn("credit_utilization", COMPONENT_WEIGHTS)
        self.assertIn("repayment_adequacy", COMPONENT_WEIGHTS)
        self.assertIn("debt_burden", COMPONENT_WEIGHTS)
        self.assertIn("account_trajectory", COMPONENT_WEIGHTS)

    def test_02_score_range_and_output_structure(self):
        """Verify score bounds [0, 100] and schema completeness."""
        result = calculate_financial_health(self.applicant_clean)

        self.assertIn("score", result)
        self.assertIn("label", result)
        self.assertIn("components", result)
        self.assertIn("summary", result)
        self.assertIn("methodology", result)
        self.assertIn("disclaimer", result)
        self.assertIn("privacy_statement", result)

        self.assertIsInstance(result["score"], int)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)
        self.assertIn(result["label"], ["EXCELLENT", "GOOD", "FAIR", "POOR / AT RISK"])

    def test_03_deterministic_reproducibility(self):
        """Verify that identical inputs produce identical scores and explanations."""
        res1 = calculate_financial_health(self.applicant_clean)
        res2 = calculate_financial_health(self.applicant_clean)

        self.assertEqual(res1["score"], res2["score"])
        self.assertEqual(res1["label"], res2["label"])
        self.assertEqual(res1["summary"], res2["summary"])
        for k in res1["components"]:
            self.assertEqual(res1["components"][k]["score"], res2["components"][k]["score"])

    def test_04_profile_monotonicity(self):
        """Verify that a clean on-time applicant receives a higher score than a delinquent applicant."""
        res_clean = calculate_financial_health(self.applicant_clean)
        res_delinq = calculate_financial_health(self.applicant_delinq)

        self.assertGreater(res_clean["score"], res_delinq["score"])
        self.assertGreater(
            res_clean["components"]["payment_timeliness"]["score"],
            res_delinq["components"]["payment_timeliness"]["score"]
        )

    def test_05_division_by_zero_safety(self):
        """Verify safe execution when LIMIT_BAL is 0 (division-by-zero protection)."""
        edge_data = self.applicant_clean.copy()
        edge_data["LIMIT_BAL"] = 0
        edge_data["BILL_AMT1"] = 0
        edge_data["PAY_AMT1"] = 0

        result = calculate_financial_health(edge_data)
        self.assertIsInstance(result["score"], int)
        self.assertFalse(np.isnan(result["score"]))
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)

    def test_06_negative_bill_amounts_safety(self):
        """Verify safe execution when bills are negative (refunds or overpayments)."""
        edge_data = self.applicant_clean.copy()
        edge_data["BILL_AMT1"] = -5000
        edge_data["BILL_AMT2"] = -3000
        edge_data["BILL_AMT3"] = -1000

        result = calculate_financial_health(edge_data)
        self.assertIsInstance(result["score"], int)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)
        self.assertFalse(np.isnan(result["components"]["credit_utilization"]["score"]))

    def test_07_missing_values_imputation_safety(self):
        """Verify that NaN values are handled gracefully without raising exceptions."""
        edge_data = self.applicant_clean.copy()
        edge_data["BILL_AMT1"] = np.nan
        edge_data["PAY_AMT1"] = np.nan
        edge_data["PAY_0"] = np.nan

        result = calculate_financial_health(edge_data)
        self.assertIsInstance(result["score"], int)
        self.assertFalse(np.isnan(result["score"]))

    def test_08_label_threshold_logic(self):
        """Verify deterministic tier mapping boundaries."""
        self.assertEqual(determine_health_label(100), "EXCELLENT")
        self.assertEqual(determine_health_label(80.0), "EXCELLENT")
        self.assertEqual(determine_health_label(79.9), "GOOD")
        self.assertEqual(determine_health_label(65.0), "GOOD")
        self.assertEqual(determine_health_label(64.9), "FAIR")
        self.assertEqual(determine_health_label(50.0), "FAIR")
        self.assertEqual(determine_health_label(49.9), "POOR / AT RISK")
        self.assertEqual(determine_health_label(0.0), "POOR / AT RISK")

    def test_09_component_schema_completeness(self):
        """Verify all 5 components contain name, score, weight, status, and explanation."""
        result = calculate_financial_health(self.applicant_delinq)
        components = result["components"]

        for comp_key, comp in components.items():
            self.assertIn("name", comp)
            self.assertIn("score", comp)
            self.assertIn("weight", comp)
            self.assertIn("status", comp)
            self.assertIn("explanation", comp)
            self.assertGreaterEqual(comp["score"], 0.0)
            self.assertLessEqual(comp["score"], 100.0)

    def test_10_disclaimer_notice_compliance(self):
        """Verify that required disclaimer notices are present in output."""
        result = calculate_financial_health(self.applicant_clean)
        self.assertIn("NOT a FICO score", result["methodology"]["notice"])
        self.assertIn("educational machine-learning risk assessment", result["disclaimer"])


if __name__ == "__main__":
    unittest.main()
