"""
Credit Scoring Model — Prediction and Explainability Test Suite
================================================================
Unit and integration tests for Phase 4:
1. Production pipeline loading and validation.
2. Binary prediction class and probability bounds [0.0, 1.0].
3. Probability sum-to-one constraint and class consistency.
4. Risk-level presentation category mapping.
5. Explainability output structure and human-readable factor generation.
6. Differentiation of explanations across different applicant profiles.
7. Handling of unknown categorical levels (OneHotEncoder handle_unknown='ignore').
8. Handling of missing optional values (Imputer resilience).
9. Edge case arithmetic safety (zero credit limit, negative bills).
10. Privacy compliance (no sensitive identity fields required).
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from data_loader import load_credit_data
from predict import (
    LEGAL_DISCLAIMER,
    PRIVACY_STATEMENT,
    PROBABILITY_CALIBRATION_NOTICE,
    determine_risk_level,
    load_prediction_pipeline,
    predict_credit_risk,
    validate_applicant_input,
)
from risk_reasons import (
    FEATURE_TERMINOLOGY_MAP,
    GLOBAL_VS_INDIVIDUAL_CAUSALITY_NOTICE,
    explain_prediction,
    identify_positive_factors,
    identify_risk_factors,
)


class TestCreditPredictionAndExplainability(unittest.TestCase):
    """Test suite for prediction inference and human-readable explainability modules."""

    @classmethod
    def setUpClass(cls):
        cls.data_path = "data/credit_data.csv"
        cls.pipeline_path = "models/credit_pipeline.pkl"
        cls.df_raw, _ = load_credit_data(cls.data_path)

        # Real test samples
        # Find a clean non-default applicant (all payments on time)
        clean_mask = (cls.df_raw["PAY_0"] <= 0) & (cls.df_raw["PAY_2"] <= 0) & (cls.df_raw["PAY_3"] <= 0)
        cls.applicant_clean = cls.df_raw[clean_mask].iloc[0].to_dict()

        # Find a severely delinquent applicant (PAY_0 >= 2)
        delinq_mask = (cls.df_raw["PAY_0"] >= 2) & (cls.df_raw["PAY_2"] >= 2)
        cls.applicant_delinq = cls.df_raw[delinq_mask].iloc[0].to_dict()

    def test_01_pipeline_loading_and_type(self):
        """Test that saved credit pipeline loads successfully and has prediction methods."""
        pipeline = load_prediction_pipeline(self.pipeline_path)
        self.assertIsNotNone(pipeline)
        self.assertTrue(hasattr(pipeline, "predict"))
        self.assertTrue(hasattr(pipeline, "predict_proba"))
        self.assertEqual(len(pipeline.classes_), 2)
        self.assertListEqual(list(pipeline.classes_), [0, 1])

    def test_02_predict_clean_applicant(self):
        """Test scoring of a creditworthy applicant with on-time payment track record."""
        result = predict_credit_risk(self.applicant_clean, pipeline_path=self.pipeline_path)

        self.assertIn("predicted_class", result)
        self.assertIn("predicted_label", result)
        self.assertIn("default_probability", result)
        self.assertIn("non_default_probability", result)
        self.assertIn("risk_level", result)
        self.assertIn("disclaimer", result)
        self.assertIn("probability_notice", result)

        self.assertEqual(result["predicted_class"], 0)
        self.assertEqual(result["predicted_label"], "Non-Default")
        self.assertGreaterEqual(result["default_probability"], 0.0)
        self.assertLessEqual(result["default_probability"], 1.0)
        self.assertAlmostEqual(result["default_probability"] + result["non_default_probability"], 1.0, places=3)
        self.assertIn(result["risk_level"], ["LOW RISK", "MEDIUM RISK"])

    def test_03_predict_delinquent_applicant(self):
        """Test scoring of a high-risk applicant with multi-month delinquency history."""
        result = predict_credit_risk(self.applicant_delinq, pipeline_path=self.pipeline_path)

        self.assertEqual(result["predicted_class"], 1)
        self.assertEqual(result["predicted_label"], "Default")
        self.assertGreater(result["default_probability"], 0.50)
        self.assertEqual(result["risk_level"], "HIGH RISK")
        self.assertGreaterEqual(result["default_probability"], 0.0)
        self.assertLessEqual(result["default_probability"], 1.0)

    def test_04_different_applicants_produce_different_outputs(self):
        """Verify that distinct applicants produce distinct probabilities and explanations."""
        pred_clean = predict_credit_risk(self.applicant_clean)
        pred_delinq = predict_credit_risk(self.applicant_delinq)

        # Probabilities must clearly diverge
        self.assertNotEqual(pred_clean["default_probability"], pred_delinq["default_probability"])
        self.assertLess(pred_clean["default_probability"], pred_delinq["default_probability"])

        # Explanations must differ
        exp_clean = explain_prediction(self.applicant_clean, pred_clean)
        exp_delinq = explain_prediction(self.applicant_delinq, pred_delinq)

        self.assertNotEqual(exp_clean["summary"], exp_delinq["summary"])
        self.assertGreater(len(exp_clean["positive_factors"]), 0)
        self.assertGreater(len(exp_delinq["top_risk_factors"]), 0)

        # Check clean has on-time as top positive factor
        clean_pos_features = [f["feature_name"] for f in exp_clean["positive_factors"]]
        self.assertIn("PAY_0", clean_pos_features)

        # Check delinq has delinquency as top risk factor
        delinq_risk_features = [f["feature_name"] for f in exp_delinq["top_risk_factors"]]
        self.assertIn("PAY_0", delinq_risk_features)

    def test_05_unknown_categorical_handling(self):
        """Test that unknown categorical levels (e.g., EDUCATION=99, SEX=9) are safely handled."""
        applicant_novel = self.applicant_clean.copy()
        applicant_novel["EDUCATION"] = 99
        applicant_novel["SEX"] = 9
        applicant_novel["MARRIAGE"] = 0

        # Should execute without throwing categorical encoder error
        result = predict_credit_risk(applicant_novel)
        self.assertIn(result["predicted_class"], [0, 1])
        self.assertGreaterEqual(result["default_probability"], 0.0)
        self.assertLessEqual(result["default_probability"], 1.0)

    def test_06_missing_optional_value_imputation(self):
        """Test that missing values are imputed gracefully by the pipeline."""
        applicant_missing = self.applicant_clean.copy()
        applicant_missing["BILL_AMT1"] = np.nan
        applicant_missing["PAY_AMT1"] = np.nan
        applicant_missing["LIMIT_BAL"] = np.nan

        result = predict_credit_risk(applicant_missing)
        self.assertIn(result["predicted_class"], [0, 1])
        self.assertFalse(np.isnan(result["default_probability"]))

    def test_07_edge_case_zero_limit_and_negative_bills(self):
        """Test arithmetic stability when LIMIT_BAL is zero and bills are negative (refunds)."""
        edge_applicant = {
            "LIMIT_BAL": 0,
            "SEX": 1,
            "EDUCATION": 1,
            "MARRIAGE": 2,
            "AGE": 25,
            "PAY_0": 0,
            "PAY_2": 0,
            "PAY_3": 0,
            "PAY_4": 0,
            "PAY_5": 0,
            "PAY_6": 0,
            "BILL_AMT1": -500,
            "BILL_AMT2": -500,
            "BILL_AMT3": 0,
            "BILL_AMT4": 0,
            "BILL_AMT5": 0,
            "BILL_AMT6": 0,
            "PAY_AMT1": 0,
            "PAY_AMT2": 0,
            "PAY_AMT3": 0,
            "PAY_AMT4": 0,
            "PAY_AMT5": 0,
            "PAY_AMT6": 0,
        }
        result = predict_credit_risk(edge_applicant)
        self.assertIn(result["predicted_class"], [0, 1])
        self.assertFalse(np.isnan(result["default_probability"]))
        self.assertFalse(np.isinf(result["default_probability"]))

        explanation = explain_prediction(edge_applicant, result)
        self.assertIsInstance(explanation["summary"], str)
        self.assertGreater(len(explanation["summary"]), 10)

    def test_08_explainability_structure_and_terminology(self):
        """Test that explanation output contains all required fields, factors, and terminology."""
        explanation = explain_prediction(self.applicant_delinq)

        self.assertIn("summary", explanation)
        self.assertIn("predicted_label", explanation)
        self.assertIn("model_estimated_likelihood_pct", explanation)
        self.assertIn("top_risk_factors", explanation)
        self.assertIn("positive_factors", explanation)
        self.assertIn("technical_factors", explanation)
        self.assertIn("global_vs_individual_notice", explanation)
        self.assertIn("limitations", explanation)
        self.assertIn("disclaimer", explanation)
        self.assertIn("privacy_statement", explanation)

        # Check factor schema
        if explanation["top_risk_factors"]:
            factor = explanation["top_risk_factors"][0]
            self.assertIn("feature_name", factor)
            self.assertIn("human_label", factor)
            self.assertIn("direction", factor)
            self.assertIn("severity", factor)
            self.assertIn("importance", factor)
            self.assertIn("explanation", factor)
            self.assertEqual(factor["direction"], "negative")

    def test_09_risk_level_threshold_logic(self):
        """Test deterministic presentation risk tier thresholds."""
        self.assertEqual(determine_risk_level(0.05), "LOW RISK")
        self.assertEqual(determine_risk_level(0.199), "LOW RISK")
        self.assertEqual(determine_risk_level(0.20), "MEDIUM RISK")
        self.assertEqual(determine_risk_level(0.499), "MEDIUM RISK")
        self.assertEqual(determine_risk_level(0.50), "HIGH RISK")
        self.assertEqual(determine_risk_level(0.85), "HIGH RISK")

    def test_10_privacy_and_disclaimer_compliance(self):
        """Test that privacy fields are not required and disclaimers are populated."""
        input_data = self.applicant_clean.copy()
        # Add extraneous private fields to verify they are safely stripped
        input_data["name"] = "John Doe"
        input_data["email"] = "johndoe@example.com"
        input_data["phone"] = "555-1234"
        input_data["ssn"] = "000-00-0000"

        validated_df = validate_applicant_input(input_data)
        self.assertNotIn("name", validated_df.columns)
        self.assertNotIn("email", validated_df.columns)
        self.assertNotIn("phone", validated_df.columns)
        self.assertNotIn("ssn", validated_df.columns)

        result = predict_credit_risk(input_data)
        self.assertIn("educational machine-learning risk assessment", result["disclaimer"])
        self.assertIn("Personal identity details", result["privacy_statement"])

    def test_11_extreme_supported_values_and_type_coercion(self):
        """Test extreme financial values and string-encoded numerical types."""
        extreme_input = {
            "LIMIT_BAL": "2000000.0",  # String encoded
            "SEX": "1",
            "EDUCATION": "1",
            "MARRIAGE": "2",
            "AGE": "75",
            "PAY_0": "-2",
            "PAY_2": "-2",
            "PAY_3": "-2",
            "PAY_4": "-2",
            "PAY_5": "-2",
            "PAY_6": "-2",
            "BILL_AMT1": "-50000.0",  # Account credit balance
            "BILL_AMT2": "0",
            "BILL_AMT3": "0",
            "BILL_AMT4": "0",
            "BILL_AMT5": "0",
            "BILL_AMT6": "0",
            "PAY_AMT1": "100000.0",
            "PAY_AMT2": "0",
            "PAY_AMT3": "0",
            "PAY_AMT4": "0",
            "PAY_AMT5": "0",
            "PAY_AMT6": "0",
        }
        result = predict_credit_risk(extreme_input)
        self.assertIn(result["prediction"], [0, 1])
        self.assertGreaterEqual(result["default_probability"], 0.0)
        self.assertLessEqual(result["default_probability"], 1.0)
        self.assertIn(result["risk_level"], ["LOW RISK", "MEDIUM RISK", "HIGH RISK"])

    def test_12_empty_dict_fallback_graceful_handling(self):
        """Test that an empty or missing input dictionary uses defaults gracefully."""
        result = predict_credit_risk({})
        self.assertIn(result["prediction"], [0, 1])
        self.assertGreaterEqual(result["default_probability"], 0.0)
        self.assertLessEqual(result["default_probability"], 1.0)
        self.assertIn(result["risk_level"], ["LOW RISK", "MEDIUM RISK", "HIGH RISK"])


if __name__ == "__main__":
    unittest.main()
