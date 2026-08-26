"""
Credit Scoring Model — Production Prediction Layer
===================================================
Human-Centered Machine Learning for Credit Risk Analysis.
Provides a clean, robust, and validated inference API for raw applicant scoring.

Key Principles:
1. Passes raw applicant data through the saved production Pipeline (models/credit_pipeline.pkl)
   without duplicating preprocessing or feature engineering logic.
2. Validates inputs safely (handles missing optional fields and unseen categoricals).
3. Produces structured output: class prediction, continuous default likelihood, and risk tier.
4. Strictly preserves applicant privacy: never requests or accepts personal identification data.
5. Strictly avoids LLMs, external APIs, or artificial score fabrication.
"""

import os
import pickle
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

# Standard expected raw input features for applicant scoring
REQUIRED_CREDIT_COLUMNS = [
    "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE",
    "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
    "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
    "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"
]

# Educational and safety disclaimers
LEGAL_DISCLAIMER = (
    "This is an educational machine-learning risk assessment demonstration. "
    "It is not an official credit score, credit bureau report, loan approval system, "
    "or binding financial decision. Do not enter real sensitive financial or identity information."
)

PRIVACY_STATEMENT = (
    "This system only processes model-required credit parameters. Personal identity details "
    "(such as names, phone numbers, email addresses, Aadhaar, PAN, SSN, bank accounts, or passwords) "
    "are strictly not collected or required."
)

PROBABILITY_CALIBRATION_NOTICE = (
    "Model-estimated default likelihood is the model's output score from predict_proba(). "
    "This value has not been independently calibrated as a real-world empirical probability."
)

# -----------------------------------------------------------------------------
# PRESENTATION RISK TIERS & THRESHOLD RATIONALE
# -----------------------------------------------------------------------------
# The underlying Random Forest model is a binary classifier (0 = Non-Default, 1 = Default)
# evaluated at the standard decision boundary threshold of 0.50.
#
# For human-facing presentation and exploratory usability, continuous default likelihoods
# are mapped into three descriptive risk bands:
# - LOW RISK    : P(Default) < 0.20  (Low estimated likelihood; strong on-time payment track record)
# - MEDIUM RISK : 0.20 <= P(Default) < 0.50 (Moderate estimated likelihood; elevated balance/occasional delay; below binary default cutoff)
# - HIGH RISK   : P(Default) >= 0.50 (High estimated likelihood; predicted positive for default at standard threshold)
#
# Note: These thresholds represent a presentation layer designed for user clarity
# and do not represent statutory or official banking credit rating bands.
PRESENTATION_RISK_THRESHOLDS = {
    "LOW_RISK_UPPER": 0.20,
    "MEDIUM_RISK_UPPER": 0.50,
}

_CACHED_PIPELINE: Optional[Pipeline] = None
_CACHED_PIPELINE_PATH: Optional[str] = None


def load_prediction_pipeline(pipeline_path: str = "models/credit_pipeline.pkl") -> Pipeline:
    """
    Load and cache the trained end-to-end credit scoring pipeline.

    Args:
        pipeline_path: Path to the serialized .pkl pipeline artifact.

    Returns:
        Pipeline: Fitted Scikit-Learn Pipeline object.
    """
    global _CACHED_PIPELINE, _CACHED_PIPELINE_PATH

    if _CACHED_PIPELINE is not None and _CACHED_PIPELINE_PATH == pipeline_path:
        return _CACHED_PIPELINE

    if not os.path.exists(pipeline_path):
        raise FileNotFoundError(
            f"Production pipeline artifact not found at '{pipeline_path}'. "
            f"Please run 'python src/train_model.py' to generate the required model artifacts."
        )

    with open(pipeline_path, "rb") as f:
        pipeline = pickle.load(f)

    if not hasattr(pipeline, "predict") or not hasattr(pipeline, "predict_proba"):
        raise ValueError(f"Loaded object from '{pipeline_path}' is not a valid predictor pipeline.")

    _CACHED_PIPELINE = pipeline
    _CACHED_PIPELINE_PATH = pipeline_path
    return _CACHED_PIPELINE


def validate_applicant_input(input_data: Union[Dict[str, Any], pd.Series, pd.DataFrame]) -> pd.DataFrame:
    """
    Validate and format raw applicant inputs into a standardized DataFrame.

    Ensures:
    1. Input contains required financial and credit columns (or applies defaults for missing fields).
    2. Discards any sensitive or non-model columns (e.g., 'ID', 'name', 'email').
    3. Converts data types to appropriate numeric representations.

    Args:
        input_data: Applicant data as a dictionary, Series, or DataFrame.

    Returns:
        pd.DataFrame: Formatted DataFrame ready for the production pipeline.
    """
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    elif isinstance(input_data, pd.Series):
        df = pd.DataFrame([input_data.to_dict()])
    elif isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
    else:
        raise TypeError(f"Expected dict, pd.Series, or pd.DataFrame; received {type(input_data).__name__}.")

    # Remove non-predictive or target columns if accidentally passed
    columns_to_drop = [col for col in ["ID", "id", "default_payment_next_month", "target"] if col in df.columns]
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)

    # Check for missing required features and populate with NaN for imputer to handle if necessary
    for col in REQUIRED_CREDIT_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    # Order columns consistently
    df = df[REQUIRED_CREDIT_COLUMNS]

    # Convert all columns to numeric type
    for col in REQUIRED_CREDIT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def determine_risk_level(default_probability: float) -> str:
    """
    Map continuous default probability to human-facing presentation risk category.

    Args:
        default_probability: Float value in range [0.0, 1.0].

    Returns:
        str: 'LOW RISK', 'MEDIUM RISK', or 'HIGH RISK'.
    """
    if default_probability < PRESENTATION_RISK_THRESHOLDS["LOW_RISK_UPPER"]:
        return "LOW RISK"
    elif default_probability < PRESENTATION_RISK_THRESHOLDS["MEDIUM_RISK_UPPER"]:
        return "MEDIUM RISK"
    else:
        return "HIGH RISK"


def predict_credit_risk(
    input_data: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    pipeline_path: str = "models/credit_pipeline.pkl"
) -> Dict[str, Any]:
    """
    Generate credit risk prediction and class likelihoods for a single applicant or batch.

    Args:
        input_data: Raw applicant data (dict, pd.Series, or 1-row pd.DataFrame).
        pipeline_path: Path to the saved production pipeline.

    Returns:
        Dict[str, Any]: Structured prediction output with probabilities, labels, and safety notices.
    """
    pipeline = load_prediction_pipeline(pipeline_path)
    df_clean = validate_applicant_input(input_data)

    if len(df_clean) == 0:
        raise ValueError("Input data contains 0 applicant records.")

    # Execute inference directly through the single source of truth pipeline
    raw_preds = pipeline.predict(df_clean)
    raw_probs = pipeline.predict_proba(df_clean)

    # Verify class ordering from the fitted estimator
    classes = list(pipeline.classes_)
    default_class_idx = classes.index(1) if 1 in classes else 1
    non_default_class_idx = classes.index(0) if 0 in classes else 0

    results: List[Dict[str, Any]] = []
    for i in range(len(df_clean)):
        pred_class = int(raw_preds[i])
        prob_default = float(raw_probs[i][default_class_idx])
        prob_non_default = float(raw_probs[i][non_default_class_idx])
        pred_label = "Default" if pred_class == 1 else "Non-Default"
        risk_level = determine_risk_level(prob_default)

        applicant_raw = df_clean.iloc[i].to_dict()

        result = {
            "prediction": pred_class,
            "predicted_class": pred_class,
            "predicted_label": pred_label,
            "default_probability": round(prob_default, 4),
            "non_default_probability": round(prob_non_default, 4),
            "model_estimated_likelihood_pct": round(prob_default * 100.0, 2),
            "risk_level": risk_level,
            "decision_threshold": 0.50,
            "raw_input": applicant_raw,
            "probability_notice": PROBABILITY_CALIBRATION_NOTICE,
            "disclaimer": LEGAL_DISCLAIMER,
            "privacy_statement": PRIVACY_STATEMENT
        }
        results.append(result)

    # Return single record dictionary if single input, otherwise return batch list
    if len(results) == 1:
        return results[0]

    return {
        "batch_size": len(results),
        "predictions": results,
        "disclaimer": LEGAL_DISCLAIMER,
        "probability_notice": PROBABILITY_CALIBRATION_NOTICE
    }


if __name__ == "__main__":
    # Self-test using a sample applicant
    sample_applicant = {
        "LIMIT_BAL": 100000,
        "SEX": 2,
        "EDUCATION": 2,
        "MARRIAGE": 1,
        "AGE": 32,
        "PAY_0": 0,
        "PAY_2": 0,
        "PAY_3": 0,
        "PAY_4": 0,
        "PAY_5": 0,
        "PAY_6": 0,
        "BILL_AMT1": 25000,
        "BILL_AMT2": 24000,
        "BILL_AMT3": 23000,
        "BILL_AMT4": 20000,
        "BILL_AMT5": 18000,
        "BILL_AMT6": 15000,
        "PAY_AMT1": 5000,
        "PAY_AMT2": 4000,
        "PAY_AMT3": 3000,
        "PAY_AMT4": 3000,
        "PAY_AMT5": 3000,
        "PAY_AMT6": 3000,
    }

    prediction = predict_credit_risk(sample_applicant)
    print("--- Single Applicant Prediction Output ---")
    print(f"Predicted Class: {prediction['predicted_class']} ({prediction['predicted_label']})")
    print(f"Default Probability: {prediction['default_probability']:.4f}")
    print(f"Non-Default Probability: {prediction['non_default_probability']:.4f}")
    print(f"Risk Level: {prediction['risk_level']}")
    print(f"Probability Notice: {prediction['probability_notice']}")
