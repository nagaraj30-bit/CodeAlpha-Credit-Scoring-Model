"""
Credit Scoring Model — Data Ingestion & Validation Module
=========================================================
Human-Centered Machine Learning for Credit Risk Analysis.
Responsible for loading, validating, and verifying the financial credit risk dataset.
Strictly adheres to traditional ML, zero data leakage, and rigorous statistical validation.
"""

import os
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


# Default expected columns for standard Credit Risk and Credit Card Default Datasets
DEFAULT_CREDIT_COLUMNS = [
    "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE",
    "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
    "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
    "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"
]

TARGET_CANDIDATES = [
    "default payment next month",
    "default_payment_next_month",
    "default",
    "loan_status",
    "target"
]


class DatasetValidationError(Exception):
    """Raised when the dataset fails schema, integrity, or quality validation."""
    pass


class DataLoader:
    """
    Robust Data Loader and Schema Validator for Credit Scoring Datasets.
    
    Provides automated column standardization, missing value detection,
    type inference, and target extraction without data leakage.
    """

    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize DataLoader with a file path or use standard workspace location.
        """
        self.default_paths = [
            "data/credit_data.csv",
            "data/credit_risk_dataset.csv",
            "data/default of credit card clients.xls",
            "data/credit_card_default.csv"
        ]
        self.data_path = data_path or self._resolve_default_path()

    def _resolve_default_path(self) -> str:
        """Find the first available dataset in default storage locations."""
        for path in self.default_paths:
            if os.path.exists(path):
                return path
        return "data/credit_risk_dataset.csv"

    def validate_file_existence(self) -> None:
        """Ensure the target dataset file exists on disk."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(
                f"[DataLoader Error] Dataset not found at: '{self.data_path}'. "
                f"Please ensure the authentic credit dataset is placed in the 'data/' directory. "
                f"Expected one of: {self.default_paths}"
            )

    def load_raw_data(self) -> pd.DataFrame:
        """
        Load raw dataset with automatic format detection (CSV or Excel).
        
        Returns:
            pd.DataFrame: Raw dataset.
        """
        self.validate_file_existence()
        
        try:
            if self.data_path.endswith(".csv"):
                df = pd.read_csv(self.data_path)
            elif self.data_path.endswith((".xls", ".xlsx")):
                df = pd.read_excel(self.data_path, header=1)
            else:
                raise DatasetValidationError(
                    f"Unsupported file format for: {self.data_path}. Expected .csv or .xls/.xlsx"
                )
        except Exception as e:
            if isinstance(e, (DatasetValidationError, FileNotFoundError)):
                raise
            raise DatasetValidationError(f"Failed to read file '{self.data_path}': {str(e)}") from e

        return df

    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize column headers (strip whitespace, unify casing for target).
        """
        df = df.copy()
        df.columns = [str(col).strip() for col in df.columns]
        
        # Standardize PAY_1 to PAY_0 if present for consistency across credit card datasets
        if "PAY_1" in df.columns and "PAY_0" not in df.columns:
            df = df.rename(columns={"PAY_1": "PAY_0"})
            
        # Standardize target column name
        for candidate in TARGET_CANDIDATES:
            matching = [col for col in df.columns if col.lower() == candidate.lower()]
            if matching:
                df = df.rename(columns={matching[0]: "default_payment_next_month"})
                break
                
        return df

    def validate_schema(self, df: pd.DataFrame) -> Dict[str, Union[int, List[str], Dict[str, int]]]:
        """
        Execute comprehensive validation checks on dataset integrity.
        
        Returns:
            Dict containing validation summary metrics.
        """
        if df.empty:
            raise DatasetValidationError("Dataset is empty (0 rows).")

        if len(df) < 50:
            raise DatasetValidationError(
                f"Dataset contains only {len(df)} rows. Insufficient for statistical credit modeling."
            )

        # Check target column existence
        if "default_payment_next_month" not in df.columns:
            found_targets = [c for c in df.columns if any(tc in c.lower() for tc in ["default", "target", "risk"])]
            if not found_targets:
                raise DatasetValidationError(
                    f"Target column not detected. Expected 'default_payment_next_month' or similar. "
                    f"Available columns: {list(df.columns)}"
                )

        target_col = "default_payment_next_month"
        target_unique = df[target_col].dropna().unique()
        
        if not set(target_unique).issubset({0, 1}):
            raise DatasetValidationError(
                f"Target column '{target_col}' must be binary (0 and 1). Found unique values: {target_unique}"
            )

        # Check for non-predictive ID column
        id_cols = [c for c in df.columns if c.upper() in ["ID", "INDEX", "UNNAMED: 0"]]

        # Calculate nulls and duplicates
        null_counts = df.isnull().sum().to_dict()
        duplicate_count = int(df.duplicated().sum())

        return {
            "num_rows": len(df),
            "num_cols": len(df.columns),
            "target_col": target_col,
            "id_cols": id_cols,
            "null_counts": {k: v for k, v in null_counts.items() if v > 0},
            "duplicate_count": duplicate_count,
            "class_distribution": df[target_col].value_counts(normalize=True).to_dict()
        }

    def load_and_validate(self) -> Tuple[pd.DataFrame, Dict]:
        """
        High-level pipeline method: Loads, standardizes, validates, and returns clean data.
        
        Returns:
            Tuple[pd.DataFrame, Dict]: (Clean DataFrame, Validation Metadata Dictionary)
        """
        raw_df = self.load_raw_data()
        clean_df = self.standardize_column_names(raw_df)
        validation_report = self.validate_schema(clean_df)
        
        return clean_df, validation_report


def load_credit_data(filepath: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to load and validate the credit dataset.
    
    Args:
        filepath: Optional path to the credit risk dataset.
        
    Returns:
        Tuple[pd.DataFrame, Dict]: Cleaned DataFrame and validation report.
    """
    loader = DataLoader(filepath)
    return loader.load_and_validate()


if __name__ == "__main__":
    print("Testing data_loader.py on real dataset...")
    df, report = load_credit_data()
    print("Successfully loaded dataset:")
    print(f"  Rows: {report['num_rows']}, Columns: {report['num_cols']}")
    print(f"  Target: {report['target_col']}")
    print(f"  Class Distribution: {report['class_distribution']}")
    print(f"  Missing values count: {len(report['null_counts'])}")
    print(f"  Duplicate rows: {report['duplicate_count']}")
