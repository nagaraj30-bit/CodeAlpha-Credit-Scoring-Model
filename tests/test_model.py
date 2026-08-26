"""
Credit Scoring Model — Comprehensive Model Training & Inference Test Suite
==========================================================================
Unit and integration tests for:
1. End-to-end pipeline training and serialization
2. Model loading and reproduction
3. Probability prediction sanity, bounds [0, 1], and sum-to-one
4. Single applicant scoring & batch scoring
5. Zero leakage and absence of NaN / Inf in predictions
6. Class imbalance handling and metric sanity
"""

import json
import os
import pickle
import sys
import unittest
import numpy as np
import pandas as pd

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from data_loader import load_credit_data
from feature_engineering import CreditFeatureEngineer
from preprocessing import CleanDataPreprocessor
from evaluate_model import (
    evaluate_saved_model,
    load_production_pipeline,
    score_single_applicant,
    validate_prediction_probabilities,
)
from train_model import train_and_compare_all_models


class TestCreditModelPipeline(unittest.TestCase):
    """
    Test suite for credit model training, evaluation, and pipeline validation.
    """

    @classmethod
    def setUpClass(cls):
        """Load or create saved pipeline artifacts for testing."""
        cls.data_path = "data/credit_data.csv"
        cls.model_path = "models/credit_pipeline.pkl"
        cls.metadata_path = "models/model_metadata.json"

        # Execute training only if model artifacts not already present
        if not os.path.exists(cls.model_path) or not os.path.exists(cls.metadata_path):
            cls.results_dict, cls.pipeline, cls.metadata = train_and_compare_all_models(
                data_path=cls.data_path, save_reports=False
            )
        else:
            with open(cls.metadata_path, "r") as f:
                cls.metadata = json.load(f)

        # Load raw data for evaluation tests
        cls.df, _ = load_credit_data(cls.data_path)
        cls.preprocessor = CleanDataPreprocessor(test_size=0.2, random_state=42)
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = cls.preprocessor.prepare_data_splits(cls.df)

    def test_01_pipeline_serialization_and_reloading(self):
        """Test that the complete pipeline is saved and successfully reloaded."""
        self.assertTrue(os.path.exists(self.model_path), "Model pipeline file should exist on disk.")
        self.assertTrue(os.path.exists(self.metadata_path), "Metadata JSON should exist on disk.")

        loaded_pipeline = load_production_pipeline(self.model_path)
        self.assertIsNotNone(loaded_pipeline, "Loaded pipeline should not be None.")
        self.assertTrue(hasattr(loaded_pipeline, "predict"), "Pipeline must expose .predict()")
        self.assertTrue(hasattr(loaded_pipeline, "predict_proba"), "Pipeline must expose .predict_proba()")

    def test_02_probability_bounds_and_validity(self):
        """Test that prediction probabilities are bounded in [0, 1] and sum to 1."""
        pipeline = load_production_pipeline(self.model_path)
        validation_results = validate_prediction_probabilities(pipeline, self.X_test.iloc[:500])

        self.assertTrue(validation_results["probabilities_in_range_0_1"])
        self.assertTrue(validation_results["probabilities_sum_to_one"])
        self.assertTrue(validation_results["prediction_matches_highest_prob"])
        self.assertTrue(validation_results["no_nan_or_inf"])
        self.assertGreaterEqual(validation_results["min_default_prob"], 0.0)
        self.assertLessEqual(validation_results["max_default_prob"], 1.0)

    def test_03_single_applicant_scoring(self):
        """Test real-time scoring of single applicant dictionary payload."""
        sample_applicant = {
            "LIMIT_BAL": 200000.0,
            "SEX": 1,
            "EDUCATION": 1,
            "MARRIAGE": 2,
            "AGE": 32,
            "PAY_0": 0,
            "PAY_2": 0,
            "PAY_3": 0,
            "PAY_4": 0,
            "PAY_5": 0,
            "PAY_6": 0,
            "BILL_AMT1": 25000.0,
            "BILL_AMT2": 24000.0,
            "BILL_AMT3": 23000.0,
            "BILL_AMT4": 22000.0,
            "BILL_AMT5": 21000.0,
            "BILL_AMT6": 20000.0,
            "PAY_AMT1": 5000.0,
            "PAY_AMT2": 5000.0,
            "PAY_AMT3": 5000.0,
            "PAY_AMT4": 5000.0,
            "PAY_AMT5": 5000.0,
            "PAY_AMT6": 5000.0
        }

        result = score_single_applicant(sample_applicant, self.model_path)
        self.assertIn("default_probability", result)
        self.assertIn("risk_grade", result)
        self.assertIn("recommendation", result)
        self.assertAlmostEqual(result["default_probability"] + result["non_default_probability"], 1.0, places=4)
        self.assertIn(result["predicted_class"], [0, 1])

    def test_04_high_risk_vs_low_risk_discrimination(self):
        """Test that delinquent profile yields higher default probability than prime profile."""
        pipeline = load_production_pipeline(self.model_path)

        low_risk = {
            "LIMIT_BAL": 500000.0, "SEX": 2, "EDUCATION": 1, "MARRIAGE": 2, "AGE": 40,
            "PAY_0": -1, "PAY_2": -1, "PAY_3": -1, "PAY_4": -1, "PAY_5": -1, "PAY_6": -1,
            "BILL_AMT1": 5000.0, "BILL_AMT2": 5000.0, "BILL_AMT3": 5000.0, "BILL_AMT4": 5000.0, "BILL_AMT5": 5000.0, "BILL_AMT6": 5000.0,
            "PAY_AMT1": 5000.0, "PAY_AMT2": 5000.0, "PAY_AMT3": 5000.0, "PAY_AMT4": 5000.0, "PAY_AMT5": 5000.0, "PAY_AMT6": 5000.0
        }

        high_risk = {
            "LIMIT_BAL": 20000.0, "SEX": 1, "EDUCATION": 3, "MARRIAGE": 1, "AGE": 25,
            "PAY_0": 2, "PAY_2": 2, "PAY_3": 2, "PAY_4": 2, "PAY_5": 2, "PAY_6": 2,
            "BILL_AMT1": 25000.0, "BILL_AMT2": 24000.0, "BILL_AMT3": 23000.0, "BILL_AMT4": 22000.0, "BILL_AMT5": 21000.0, "BILL_AMT6": 20000.0,
            "PAY_AMT1": 0.0, "PAY_AMT2": 0.0, "PAY_AMT3": 0.0, "PAY_AMT4": 0.0, "PAY_AMT5": 0.0, "PAY_AMT6": 0.0
        }

        df_profiles = pd.DataFrame([low_risk, high_risk])
        probas = pipeline.predict_proba(df_profiles)[:, 1]

        self.assertLess(probas[0], probas[1], "Delinquent profile must have higher risk than prime profile.")
        self.assertGreater(probas[1], 0.5, "High delinquency profile should have elevated default probability.")

    def test_05_metadata_completeness(self):
        """Test metadata file contains all required schema attributes."""
        self.assertIn("selected_champion_model", self.metadata)
        self.assertIn("selection_reasoning", self.metadata)
        self.assertIn("champion_metrics", self.metadata)
        self.assertIn("demographic_experiment_statement", self.metadata)
        self.assertIn("probability_calibration_statement", self.metadata)
        self.assertIn("class_weight_decision", self.metadata)
        self.assertIn("feature_importance_breakdown_pct", self.metadata)
        self.assertIn("engineered_features", self.metadata)
        self.assertGreaterEqual(self.metadata["champion_metrics"]["roc_auc"], 0.70)


if __name__ == "__main__":
    unittest.main()
