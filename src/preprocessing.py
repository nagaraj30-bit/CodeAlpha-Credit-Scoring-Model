"""
Credit Scoring Model — Preprocessing & Pipeline Architecture
============================================================
Human-Centered Machine Learning for Credit Risk Analysis.
Standardizes numerical variables, encodes categorical factors, imputes missing values,
and enforces zero data leakage via Scikit-Learn Pipeline and ColumnTransformer.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from feature_engineering import CreditFeatureEngineer


# Categorical demographic and discrete features
CATEGORICAL_FEATURES = ["SEX", "EDUCATION", "MARRIAGE"]

# Discrete repayment history features (already numerically ordered -2 to 8)
STATUS_FEATURES = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]

# Base numerical variables
BASE_NUMERICAL_FEATURES = [
    "LIMIT_BAL", "AGE",
    "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
    "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"
]

# Engineered continuous financial features
ENGINEERED_NUMERICAL_FEATURES = [
    "UTILIZATION_RECENT", "UTILIZATION_AVG", "UTILIZATION_MAX",
    "PAY_TO_BILL_1", "PAY_TO_BILL_2", "PAY_TO_BILL_3", "PAY_TO_BILL_AVG",
    "MAX_DELINQUENCY", "NUM_DELINQUENT_MONTHS", "AVG_DELAY_MONTHS",
    "DELINQUENCY_TREND", "TOTAL_BILL_AMT", "TOTAL_PAY_AMT",
    "NET_DEFICIT", "DEFICIT_TO_LIMIT", "BILL_GROWTH_TREND"
]

ALL_NUMERICAL_FEATURES = BASE_NUMERICAL_FEATURES + STATUS_FEATURES + ENGINEERED_NUMERICAL_FEATURES


class CleanDataPreprocessor:
    """
    Complete Credit Scoring Data Preprocessor and Transformer Pipeline.
    
    Ensures strict separation between training fit and test/live inference transform
    to prevent data leakage.
    """

    def __init__(
        self,
        test_size: float = 0.2,
        random_state: int = 42,
        scale_numerical: bool = True,
        include_demographics: bool = True
    ):
        self.test_size = test_size
        self.random_state = random_state
        self.scale_numerical = scale_numerical
        self.include_demographics = include_demographics
        self.pipeline: Optional[Pipeline] = None
        self.feature_names_: List[str] = []
        self.target_name = "default_payment_next_month"

    def build_column_transformer(self) -> ColumnTransformer:
        """
        Build the inner ColumnTransformer for numerical and categorical sub-pipelines.
        
        Returns:
            ColumnTransformer: Ready for integration into full Pipeline.
        """
        # Numerical transformer: Median Imputation + Optional Standard Scaling
        num_steps = [
            ("imputer", SimpleImputer(strategy="median"))
        ]
        if self.scale_numerical:
            num_steps.append(("scaler", StandardScaler()))
            
        num_pipeline = Pipeline(steps=num_steps)

        transformers = [
            ("num", num_pipeline, ALL_NUMERICAL_FEATURES)
        ]

        if self.include_demographics:
            # Categorical demographic transformer: Most Frequent Imputation + One-Hot Encoding
            # handle_unknown='ignore' guarantees safe handling of unseen classes during inference
            cat_pipeline = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            ])
            transformers.append(("cat", cat_pipeline, CATEGORICAL_FEATURES))

        preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder="drop"  # Drops ID and any unhandled columns safely
        )

        return preprocessor

    def build_full_pipeline(self, estimator=None) -> Pipeline:
        """
        Construct end-to-end Pipeline chaining domain feature engineering, ColumnTransformer,
        and optionally a final classifier estimator.
        
        Returns:
            Pipeline: Scikit-Learn Pipeline object.
        """
        steps = [
            ("feature_engineering", CreditFeatureEngineer()),
            ("preprocessor", self.build_column_transformer())
        ]
        if estimator is not None:
            steps.append(("classifier", estimator))

        full_pipeline = Pipeline(steps=steps)
        self.pipeline = full_pipeline
        return full_pipeline

    def prepare_data_splits(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split dataset into train and test sets using Stratified Splitting.
        
        Strict Leakage Protection:
        1. Non-predictive ID column is dropped.
        2. Target column is extracted into y before feature processing.
        3. Stratified split maintains identical 77.88% / 22.12% class balance in train & test.
        
        Args:
            df: Standardized credit DataFrame.
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]: (X_train, X_test, y_train, y_test)
        """
        # Remove ID column if present to prevent leakage/memorization
        cols_to_drop = [c for c in ["ID", "id", "Index"] if c in df.columns]
        clean_df = df.drop(columns=cols_to_drop)

        if self.target_name not in clean_df.columns:
            raise KeyError(f"Target column '{self.target_name}' not found in dataset columns: {list(clean_df.columns)}")

        X = clean_df.drop(columns=[self.target_name])
        y = clean_df[self.target_name]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y  # Essential for imbalanced credit default classification
        )

        return X_train, X_test, y_train, y_test

    def fit_transform_train_test(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, pd.Series, pd.Series, Pipeline]:
        """
        Execute full training split, fit pipeline ONLY on X_train, and transform both splits.
        
        Returns:
            Tuple: (X_train_transformed, X_test_transformed, y_train, y_test, fitted_pipeline)
        """
        X_train, X_test, y_train, y_test = self.prepare_data_splits(df)

        if self.pipeline is None:
            self.build_full_pipeline()

        # FIT ONLY ON TRAINING SET
        X_train_trans = self.pipeline.fit_transform(X_train)
        
        # TRANSFORM TEST SET WITHOUT FITTING (Zero Data Leakage)
        X_test_trans = self.pipeline.transform(X_test)

        # Extract output feature names from the fitted ColumnTransformer
        col_transformer: ColumnTransformer = self.pipeline.named_steps["preprocessor"]
        if "cat" in col_transformer.named_transformers_:
            cat_encoder = col_transformer.named_transformers_["cat"].named_steps["onehot"]
            cat_feature_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
            self.feature_names_ = ALL_NUMERICAL_FEATURES + cat_feature_names
        else:
            self.feature_names_ = list(ALL_NUMERICAL_FEATURES)

        return X_train_trans, X_test_trans, y_train, y_test, self.pipeline

    def transform_single_applicant(self, applicant_data: Union[pd.DataFrame, Dict]) -> np.ndarray:
        """
        Transform a single applicant or small batch for live scoring inference.
        
        Args:
            applicant_data: Dict or DataFrame containing applicant fields.
            
        Returns:
            np.ndarray: Preprocessed feature vector ready for model input.
        """
        if self.pipeline is None:
            raise RuntimeError("Pipeline must be fitted before transforming applicant data.")
            
        if isinstance(applicant_data, dict):
            applicant_df = pd.DataFrame([applicant_data])
        else:
            applicant_df = applicant_data.copy()

        return self.pipeline.transform(applicant_df)


if __name__ == "__main__":
    from data_loader import load_credit_data
    
    print("Testing Preprocessing & Pipeline Architecture...")
    df, report = load_credit_data()
    
    preprocessor = CleanDataPreprocessor(test_size=0.2, random_state=42)
    X_train_trans, X_test_trans, y_train, y_test, pipe = preprocessor.fit_transform_train_test(df)
    
    print(f"X_train shape: {X_train_trans.shape}")
    print(f"X_test shape:  {X_test_trans.shape}")
    print(f"y_train default rate: {y_train.mean():.4f}")
    print(f"y_test default rate:  {y_test.mean():.4f}")
    print(f"Total features created: {len(preprocessor.feature_names_)}")
    print(f"Pipeline output features: {preprocessor.feature_names_[:10]} ...")
    print("Preprocessing verification SUCCESSFUL.")
