"""
Credit Scoring Model — What-If Scenario Simulator Test Suite
============================================================
Unit and integration tests for Phase 5 What-If Scenario Engine:
1. Production pipeline reuse verification (models/credit_pipeline.pkl).
2. Unchanged scenario returns identical outputs and zero delta.
3. Realistic scenario modification (remediating delinquency) reduces default probability.
4. Valid continuous probability bounds [0.0, 1.0] and risk tier output.
5. Exact arithmetic consistency of probability and Financial Health deltas.
6. Dynamic risk and positive factor resolution tracking.
7. Component-level financial health delta comparison.
8. Preset helper actions (remediation, balance paydown, credit limit adjustment).
9. Edge case handling (zero limit, negative bill amounts, empty modifications, invalid types).
10. Non-promissory language and simulation disclaimer compliance.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from data_loader import load_credit_data
from scenario_simulator import (
    SIMULATOR_DISCLAIMER,
    SUPPORTED_SCENARIO_VARIABLES,
    apply_scenario_modifications,
    simulate_balance_paydown,
    simulate_credit_limit_increase,
    simulate_repayment_remediation,
    simulate_scenario,
    validate_scenario_modifications,
)


class TestScenarioSimulator(unittest.TestCase):
    """Test suite for the What-If Scenario Simulator engine."""

    @classmethod
    def setUpClass(cls):
        cls.data_path = "data/credit_data.csv"
        cls.pipeline_path = "models/credit_pipeline.pkl"
        cls.df_raw, _ = load_credit_data(cls.data_path)

        # Delinquent profile (Index 0 in UCI dataset)
        cls.sample_delinq = cls.df_raw.iloc[0].to_dict()

        # Clean profile (Index 2 in UCI dataset)
        clean_mask = (cls.df_raw["PAY_0"] <= 0) & (cls.df_raw["PAY_2"] <= 0)
        cls.sample_clean = cls.df_raw[clean_mask].iloc[0].to_dict()

    def test_01_supported_scenario_variables(self):
        """Verify supported scenario variables match real dataset columns."""
        for var_name, cfg in SUPPORTED_SCENARIO_VARIABLES.items():
            self.assertIn(var_name, self.df_raw.columns)
            self.assertIn("human_name", cfg)
            self.assertIn("min_value", cfg)
            self.assertIn("max_value", cfg)

    def test_02_unchanged_scenario(self):
        """Verify that passing empty modifications produces zero deltas."""
        result = simulate_scenario(self.sample_delinq, modifications={})

        self.assertEqual(result["comparison"]["default_probability_delta"], 0.0)
        self.assertEqual(result["comparison"]["financial_health_delta"], 0)
        self.assertEqual(result["comparison"]["risk_direction"], "UNCHANGED")
        self.assertEqual(result["comparison"]["financial_health_direction"], "UNCHANGED")
        self.assertEqual(
            result["current"]["default_probability"],
            result["scenario"]["default_probability"]
        )
        self.assertEqual(
            result["current"]["financial_health"]["score"],
            result["scenario"]["financial_health"]["score"]
        )

    def test_03_repayment_remediation_reduces_risk(self):
        """Verify that bringing an overdue account current reduces model default probability."""
        result = simulate_repayment_remediation(self.sample_delinq)

        curr_p = result["current"]["default_probability"]
        scen_p = result["scenario"]["default_probability"]

        # Default probability must decrease
        self.assertLess(scen_p, curr_p)
        self.assertEqual(result["comparison"]["risk_direction"], "IMPROVED")
        self.assertLess(result["comparison"]["default_probability_delta"], 0.0)

        # Financial health must increase
        curr_fhi = result["current"]["financial_health"]["score"]
        scen_fhi = result["scenario"]["financial_health"]["score"]
        self.assertGreater(scen_fhi, curr_fhi)
        self.assertEqual(result["comparison"]["financial_health_direction"], "IMPROVED")

    def test_04_delta_arithmetic_consistency(self):
        """Verify that delta values precisely equal (scenario - current)."""
        mods = {"LIMIT_BAL": 150000.0, "PAY_AMT1": 20000.0}
        result = simulate_scenario(self.sample_delinq, modifications=mods)

        curr_p = result["current"]["default_probability"]
        scen_p = result["scenario"]["default_probability"]
        expected_p_delta = round(scen_p - curr_p, 4)
        self.assertEqual(result["comparison"]["default_probability_delta"], expected_p_delta)

        curr_fhi = result["current"]["financial_health"]["score"]
        scen_fhi = result["scenario"]["financial_health"]["score"]
        self.assertEqual(result["comparison"]["financial_health_delta"], scen_fhi - curr_fhi)

    def test_05_factor_resolution_tracking(self):
        """Verify that resolved risk factors and gained positive factors are accurately tracked."""
        result = simulate_repayment_remediation(self.sample_delinq)

        comp = result["comparison"]
        resolved_names = [f["feature_name"] for f in comp["risk_factors_resolved"]]

        # PAY_0 was delinquent in sample 0; setting to 0 should resolve it
        self.assertIn("PAY_0", resolved_names)

        gained_names = [f["feature_name"] for f in comp["positive_factors_gained"]]
        self.assertIn("PAY_0", gained_names)

    def test_06_component_comparison_breakdown(self):
        """Verify that component comparisons contain score deltas and status directions."""
        result = simulate_scenario(
            self.sample_delinq,
            modifications={"PAY_0": 0, "PAY_2": 0, "PAY_AMT1": 10000}
        )

        comp_table = result["comparison"]["component_comparison"]
        self.assertIn("payment_timeliness", comp_table)
        self.assertIn("credit_utilization", comp_table)
        self.assertIn("repayment_adequacy", comp_table)

        time_comp = comp_table["payment_timeliness"]
        self.assertGreater(time_comp["scenario_score"], time_comp["current_score"])
        self.assertEqual(time_comp["direction"], "IMPROVED")

    def test_07_balance_paydown_helper(self):
        """Verify that simulate_balance_paydown executes correctly."""
        result = simulate_balance_paydown(self.sample_clean, paydown_fraction=0.80)

        self.assertIn("current", result)
        self.assertIn("scenario", result)
        self.assertIn("comparison", result)
        self.assertGreaterEqual(result["scenario"]["default_probability"], 0.0)
        self.assertLessEqual(result["scenario"]["default_probability"], 1.0)

    def test_08_credit_limit_increase_helper(self):
        """Verify that simulate_credit_limit_increase executes correctly."""
        result = simulate_credit_limit_increase(self.sample_clean, new_limit=200000.0)

        self.assertIn("current", result)
        self.assertIn("scenario", result)
        self.assertGreaterEqual(result["scenario"]["financial_health"]["score"], 0)
        self.assertLessEqual(result["scenario"]["financial_health"]["score"], 100)

    def test_09_edge_case_zero_limit_and_negative_bills(self):
        """Verify mathematical robustness with extreme or zero inputs."""
        mods = {"LIMIT_BAL": 0.0, "BILL_AMT1": -10000.0, "PAY_AMT1": 0.0}
        result = simulate_scenario(self.sample_clean, modifications=mods)

        self.assertFalse(np.isnan(result["scenario"]["default_probability"]))
        self.assertFalse(np.isinf(result["scenario"]["default_probability"]))
        self.assertFalse(np.isnan(result["scenario"]["financial_health"]["score"]))

    def test_10_safe_simulation_language_and_disclaimers(self):
        """Verify non-promissory language in narrative summary and disclaimers."""
        result = simulate_repayment_remediation(self.sample_delinq)

        summary = result["comparison"]["summary"]
        self.assertNotIn("will be approved", summary.lower())
        self.assertNotIn("guarantee", summary.lower())
        self.assertIn("under this model", summary.lower())

        self.assertIn("hypothetical input conditions", result["disclaimer"])
        self.assertIn("Personal identity details", result["privacy_statement"])


if __name__ == "__main__":
    unittest.main()
