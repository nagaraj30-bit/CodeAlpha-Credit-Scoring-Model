"""
Credit Scoring Model — Unit & Pipeline Integration Tests
=========================================================
Human-Centered Machine Learning for Credit Risk Analysis.
Validates data loading, domain feature engineering, preprocessing pipelines,
leakage prevention, and numerical edge-case safety.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from data_loader import DataLoader, load_credit_data, DatasetValidationError
from feature_engineering import CreditFeatureEngineer, engineer_credit_features
from preprocessing import CleanDataPreprocessor, ALL_NUMERICAL_FEATURES, CATEGORICAL_FEATURES


class TestDataPreparation(unittest.TestCase):
    """Test suite for Phase 2 Data Preparation & Preprocessing Layer."""

    @classmethod
    def setUpClass(cls):
        """Load real dataset once for tests."""
        cls.df, cls.report = load_credit_data("data/credit_data.csv")

    def test_01_data_loader_integrity(self):
        """Test dataset dimensions, absence of nulls, and target column extraction."""
        self.assertGreaterEqual(len(self.df), 20000)
        self.assertEqual(len(self.df.columns), 25)
        self.assertIn("default_payment_next_month", self.df.columns)
        self.assertEqual(sum(self.report["null_counts"].values()), 0)
        self.assertEqual(self.report["duplicate_count"], 0)

    def test_02_data_loader_error_handling(self):
        """Test that non-existent dataset raises FileNotFoundError."""
        loader = DataLoader("data/non_existent_dataset.csv")
        with self.assertRaises(FileNotFoundError):
            loader.load_raw_data()

    def test_03_feature_engineering_safety(self):
        """Test feature engineering calculations, edge-case division by zero, and no inf/NaN."""
        df_feat = engineer_credit_features(self.df)
        
        # Check all expected engineered features exist
        expected_engineered = [
            "UTILIZATION_RECENT", "UTILIZATION_AVG", "UTILIZATION_MAX",
            "PAY_TO_BILL_1", "PAY_TO_BILL_2", "PAY_TO_BILL_3", "PAY_TO_BILL_AVG",
            "MAX_DELINQUENCY", "NUM_DELINQUENT_MONTHS", "AVG_DELAY_MONTHS",
            "DELINQUENCY_TREND", "TOTAL_BILL_AMT", "TOTAL_PAY_AMT",
            "NET_DEFICIT", "DEFICIT_TO_LIMIT", "BILL_GROWTH_TREND"
        ]
        for col in expected_engineered:
            self.assertIn(col, df_feat.columns, f"Missing engineered feature: {col}")
            self.assertFalse(df_feat[col].isna().any(), f"Engineered feature {col} contains NaN")
            self.assertFalse(np.isinf(df_feat[col]).any(), f"Engineered feature {col} contains Inf")

    def test_04_feature_engineering_synthetic_edge_cases(self):
        """Test synthetic edge cases: negative bills, zero limits, zero previous bills."""
        edge_data = pd.DataFrame({
            "LIMIT_BAL": [0, 100000, 50000],
            "SEX": [1, 2, 1],
            "EDUCATION": [1, 2, 3],
            "MARRIAGE": [1, 2, 1],
            "AGE": [25, 40, 60],
            "PAY_0": [-2, 2, 0],
            "PAY_2": [-1, 2, 0],
            "PAY_3": [-1, 2, 0],
            "PAY_4": [-1, 1, 0],
            "PAY_5": [-1, 0, 0],
            "PAY_6": [-1, 0, 0],
            "BILL_AMT1": [-5000, 80000, 0],
            "BILL_AMT2": [0, 75000, 1000],
            "BILL_AMT3": [0, 70000, 1000],
            "BILL_AMT4": [0, 65000, 1000],
            "BILL_AMT5": [0, 60000, 1000],
            "BILL_AMT6": [0, 55000, 1000],
            "PAY_AMT1": [0, 5000, 1000],
            "PAY_AMT2": [0, 5000, 1000],
            "PAY_AMT3": [0, 5000, 1000],
            "PAY_AMT4": [0, 5000, 1000],
            "PAY_AMT5": [0, 5000, 1000],
            "PAY_AMT6": [0, 5000, 1000],
        })
        
        engineer = CreditFeatureEngineer()
        transformed = engineer.transform(edge_data)
        
        # Verify no NaN or Inf even with zero limit and negative bills
        self.assertFalse(transformed.isna().any().any())
        self.assertFalse(np.isinf(transformed.select_dtypes(include=np.number)).any().any())
        # First row has negative BILL_AMT1 (-5000) -> UTILIZATION_RECENT floored to 0.0
        self.assertEqual(transformed["UTILIZATION_RECENT"].iloc[0], 0.0)

    def test_05_preprocessing_pipeline_train_test_split(self):
        """Test that Stratified Split preserves class distribution and prevents leakage."""
        preprocessor = CleanDataPreprocessor(test_size=0.2, random_state=42)
        X_train, X_test, y_train, y_test = preprocessor.prepare_data_splits(self.df)

        expected_train_len = int(len(self.df) * 0.8)
        expected_test_len = len(self.df) - expected_train_len
        self.assertEqual(len(X_train), expected_train_len)
        self.assertEqual(len(X_test), expected_test_len)
        
        # Check target is NOT in X
        self.assertNotIn("default_payment_next_month", X_train.columns)
        self.assertNotIn("default_payment_next_month", X_test.columns)
        # Check ID is NOT in X
        self.assertNotIn("ID", X_train.columns)
        self.assertNotIn("ID", X_test.columns)

        # Check stratification
        train_default_rate = y_train.mean()
        test_default_rate = y_test.mean()
        self.assertAlmostEqual(train_default_rate, self.df["default_payment_next_month"].mean(), delta=0.01)
        self.assertAlmostEqual(test_default_rate, self.df["default_payment_next_month"].mean(), delta=0.01)

    def test_06_preprocessing_fit_transform_lifecycle(self):
        """Test full preprocessing pipeline transformation and feature names."""
        preprocessor = CleanDataPreprocessor(test_size=0.2, random_state=42)
        X_tr_trans, X_te_trans, y_tr, y_te, pipe = preprocessor.fit_transform_train_test(self.df)

        expected_train_len = int(len(self.df) * 0.8)
        expected_test_len = len(self.df) - expected_train_len
        self.assertEqual(X_tr_trans.shape[0], expected_train_len)
        self.assertEqual(X_te_trans.shape[0], expected_test_len)
        self.assertEqual(X_tr_trans.shape[1], X_te_trans.shape[1])
        self.assertEqual(X_tr_trans.shape[1], len(preprocessor.feature_names_))

        # Check for NaN in transformed outputs
        self.assertFalse(np.isnan(X_tr_trans).any())
        self.assertFalse(np.isnan(X_te_trans).any())

    def test_07_unseen_categorical_inference_handling(self):
        """Test that OneHotEncoder with handle_unknown='ignore' safely handles novel categories."""
        preprocessor = CleanDataPreprocessor(test_size=0.2, random_state=42)
        preprocessor.fit_transform_train_test(self.df)

        # Create single applicant with unseen/extreme categorical values (e.g. EDUCATION=99, MARRIAGE=99)
        unseen_applicant = self.df.drop(columns=["ID", "default_payment_next_month"]).iloc[0].to_dict()
        unseen_applicant["EDUCATION"] = 99
        unseen_applicant["MARRIAGE"] = 99
        
        # Should transform without throwing errors
        trans_applicant = preprocessor.transform_single_applicant(unseen_applicant)
        self.assertEqual(trans_applicant.shape[0], 1)
        self.assertEqual(trans_applicant.shape[1], len(preprocessor.feature_names_))
        self.assertFalse(np.isnan(trans_applicant).any())


if __name__ == "__main__":
    unittest.main(verbosity=2)
