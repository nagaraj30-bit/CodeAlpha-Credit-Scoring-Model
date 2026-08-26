"""
Credit Scoring Model — Fairness & Bias Evaluation Tests
======================================================
Tests for Phase 9 Fairness Analysis:
- Group statistics & confusion matrix calculations
- Metric formulas (Prediction Rate, Recall, FPR, FNR, Precision)
- Zero-denominator edge-case safety
- Disparity & ratio calculations
- Sample size threshold flags and instability warnings
- Deterministic behavior across runs
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from fairness import (
    calculate_confusion_matrix_counts,
    calculate_group_metrics,
    calculate_group_disparities,
    audit_attribute_fairness,
    bin_age_groups,
    generate_full_fairness_report,
    MIN_SAMPLE_SIZE_THRESHOLD,
    MIN_SAMPLE_SIZE_CRITICAL,
)


class TestFairnessAnalysis(unittest.TestCase):
    """Unit test suite for Fairness & Bias Evaluation Module."""

    def setUp(self):
        """Create a synthetic controlled evaluation dataset with known group parameters."""
        # Group A (Baseline): 1000 samples, 200 actual defaults (20%)
        # 160 TP, 40 FN, 80 FP, 720 TN
        y_true_A = [1] * 200 + [0] * 800
        y_pred_A = [1] * 160 + [0] * 40 + [1] * 80 + [0] * 720

        # Group B (Comparator): 500 samples, 100 actual defaults (20%)
        # 75 TP, 25 FN, 50 FP, 350 TN
        y_true_B = [1] * 100 + [0] * 400
        y_pred_B = [1] * 75 + [0] * 25 + [1] * 50 + [0] * 350

        # Group C (Small Sample): 50 samples (< 100 critical threshold)
        # 10 actual defaults: 8 TP, 2 FN, 4 FP, 36 TN
        y_true_C = [1] * 10 + [0] * 40
        y_pred_C = [1] * 8 + [0] * 2 + [1] * 4 + [0] * 36

        self.df_test = pd.DataFrame({
            "SEX": [1] * 1000 + [2] * 500 + [1] * 50,
            "EDUCATION": [1] * 1000 + [2] * 500 + [4] * 50,
            "AGE": [25] * 500 + [35] * 500 + [45] * 500 + [65] * 50,
            "default_payment_next_month": y_true_A + y_true_B + y_true_C,
            "prediction": y_pred_A + y_pred_B + y_pred_C,
            "default_probability": [0.8] * 160 + [0.2] * 40 + [0.7] * 80 + [0.1] * 720 +
                                  [0.8] * 75 + [0.2] * 25 + [0.7] * 50 + [0.1] * 350 +
                                  [0.8] * 8 + [0.2] * 2 + [0.7] * 4 + [0.1] * 36,
        })

    def test_01_confusion_matrix_counts(self):
        """Test exact TP, FP, TN, FN extraction."""
        y_true = [1, 1, 0, 0, 1, 0]
        y_pred = [1, 0, 1, 0, 1, 0]
        counts = calculate_confusion_matrix_counts(y_true, y_pred)

        self.assertEqual(counts["tp"], 2)
        self.assertEqual(counts["fn"], 1)
        self.assertEqual(counts["fp"], 1)
        self.assertEqual(counts["tn"], 2)
        self.assertEqual(counts["total"], 6)

    def test_02_group_metrics_mathematical_precision(self):
        """Test accuracy of group-level metric formulas: Recall, FPR, FNR, Precision, PPR."""
        # 160 TP, 40 FN, 80 FP, 720 TN (Total = 1000)
        y_true = [1] * 200 + [0] * 800
        y_pred = [1] * 160 + [0] * 40 + [1] * 80 + [0] * 720
        y_prob = [0.8] * 240 + [0.1] * 760

        metrics = calculate_group_metrics(y_true, y_pred, y_prob)

        # Expected:
        # Base rate = 200 / 1000 = 0.2000
        # Positive prediction rate = (160 + 80) / 1000 = 0.2400
        # Recall (TPR) = 160 / 200 = 0.8000
        # FPR = 80 / 800 = 0.1000
        # FNR = 40 / 200 = 0.2000
        # Precision = 160 / (160 + 80) = 160 / 240 = 0.6667
        # Accuracy = (160 + 720) / 1000 = 0.8800

        self.assertEqual(metrics["sample_count"], 1000)
        self.assertAlmostEqual(metrics["base_rate"], 0.2000, places=3)
        self.assertAlmostEqual(metrics["positive_prediction_rate"], 0.2400, places=3)
        self.assertAlmostEqual(metrics["recall"], 0.8000, places=3)
        self.assertAlmostEqual(metrics["false_positive_rate"], 0.1000, places=3)
        self.assertAlmostEqual(metrics["false_negative_rate"], 0.2000, places=3)
        self.assertAlmostEqual(metrics["precision"], 0.6667, places=3)
        self.assertAlmostEqual(metrics["accuracy"], 0.8800, places=3)
        self.assertFalse(metrics["is_small_sample"])

    def test_03_zero_denominator_safety(self):
        """Test that metric calculations never crash on 0 positives or 0 negatives."""
        # Case A: No positive actuals (TP + FN = 0)
        y_true_zero_pos = [0, 0, 0, 0]
        y_pred_zero_pos = [0, 0, 0, 0]
        metrics_a = calculate_group_metrics(y_true_zero_pos, y_pred_zero_pos)
        self.assertIsNone(metrics_a["recall"])
        self.assertIsNone(metrics_a["false_negative_rate"])
        self.assertEqual(metrics_a["false_positive_rate"], 0.0)

        # Case B: No positive predictions (TP + FP = 0)
        y_true_zero_pred = [1, 0, 1, 0]
        y_pred_zero_pred = [0, 0, 0, 0]
        metrics_b = calculate_group_metrics(y_true_zero_pred, y_pred_zero_pred)
        self.assertIsNone(metrics_b["precision"])
        self.assertEqual(metrics_b["positive_prediction_rate"], 0.0)
        self.assertEqual(metrics_b["recall"], 0.0)

        # Case C: Empty inputs
        metrics_empty = calculate_group_metrics([], [])
        self.assertEqual(metrics_empty["sample_count"], 0)
        self.assertEqual(metrics_empty["positive_prediction_rate"], 0.0)

    def test_04_sample_size_warnings(self):
        """Verify that small groups are flagged with explicit instability notices."""
        # Group with 50 samples (< 100 critical threshold)
        metrics_crit = calculate_group_metrics([1] * 10 + [0] * 40, [1] * 8 + [0] * 42)
        self.assertTrue(metrics_crit["is_small_sample"])
        self.assertTrue(metrics_crit["is_critical_sample"])
        self.assertIn("Critical sample size warning", metrics_crit["sample_warning"])

        # Group with 200 samples (< 300 small sample threshold)
        metrics_small = calculate_group_metrics([1] * 40 + [0] * 160, [1] * 35 + [0] * 165)
        self.assertTrue(metrics_small["is_small_sample"])
        self.assertFalse(metrics_small["is_critical_sample"])
        self.assertIn("Limited sample size", metrics_small["sample_warning"])

        # Group with 500 samples (>= 300 threshold)
        metrics_ok = calculate_group_metrics([1] * 100 + [0] * 400, [1] * 80 + [0] * 420)
        self.assertFalse(metrics_ok["is_small_sample"])
        self.assertIsNone(metrics_ok["sample_warning"])

    def test_05_group_disparities(self):
        """Test disparity differences and ratio calculations against baseline."""
        baseline = {
            "positive_prediction_rate": 0.20,
            "recall": 0.80,
            "false_positive_rate": 0.10,
            "precision": 0.60,
            "accuracy": 0.85,
            "base_rate": 0.20,
        }
        comparator = {
            "positive_prediction_rate": 0.25,
            "recall": 0.75,
            "false_positive_rate": 0.12,
            "precision": 0.58,
            "accuracy": 0.82,
            "base_rate": 0.22,
        }

        disp = calculate_group_disparities(comparator, baseline)
        self.assertAlmostEqual(disp["positive_prediction_rate_diff"], 0.05, places=4)
        self.assertAlmostEqual(disp["positive_prediction_rate_ratio"], 1.25, places=4)
        self.assertAlmostEqual(disp["recall_diff"], -0.05, places=4)
        self.assertAlmostEqual(disp["recall_ratio"], 0.9375, places=4)
        self.assertAlmostEqual(disp["false_positive_rate_diff"], 0.02, places=4)

    def test_06_age_group_binning(self):
        """Test continuous age categorization into standard cohorts."""
        ages = [22, 29, 30, 39, 40, 49, 50, 59, 60, 75, "invalid"]
        bins = bin_age_groups(ages)
        expected = [
            "21-29", "21-29", "30-39", "30-39", "40-49", "40-49",
            "50-59", "50-59", "60+", "60+", "Unknown"
        ]
        self.assertEqual(bins, expected)

    def test_07_full_fairness_audit_execution(self):
        """Test full fairness auditing pipeline over all supported attributes."""
        report = generate_full_fairness_report(self.df_test)

        self.assertIn("dataset_audit", report)
        self.assertIn("attributes", report)
        self.assertIn("fairness_principles", report)

        # Check supported attributes
        attrs = report["attributes"]
        self.assertIn("SEX", attrs)
        self.assertIn("EDUCATION", attrs)
        self.assertIn("AGE_GROUP", attrs)

        # Verify SEX audit structure
        sex_audit = attrs["SEX"]
        self.assertIn("groups", sex_audit)
        self.assertIn("summary", sex_audit)
        self.assertIn("limitations", sex_audit)


if __name__ == "__main__":
    unittest.main()
