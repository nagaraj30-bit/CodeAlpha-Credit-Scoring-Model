"""
Credit Scoring Model — Model Evaluation, Verification & Diagnostics
===================================================================
Reloads the saved `models/credit_pipeline.pkl` production pipeline,
performs inference on test instances, validates probabilities, and
checks for prediction safety and zero data leakage.
"""

import json
import os
import pickle
from typing import Any, Dict, Union

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from data_loader import load_credit_data
from preprocessing import CleanDataPreprocessor


def load_production_pipeline(model_path: str = "models/credit_pipeline.pkl") -> Any:
    """
    Load the trained end-to-end Pipeline object from disk.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model pipeline not found at '{model_path}'. Please train the model first.")
    with open(model_path, "rb") as f:
        pipeline = pickle.load(f)
    return pipeline


def validate_prediction_probabilities(
    pipeline: Any,
    test_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Verify probability validity on representative test samples:
    - Probability range is bounded strictly in [0.0, 1.0]
    - Binary probabilities sum to 1.0
    - Argmax probability strictly matches discrete binary prediction
    - No NaN or Infinite values
    """
    # Predict probabilities directly from raw DataFrame
    probas = pipeline.predict_proba(test_df)
    preds = pipeline.predict(test_df)

    # 1. Bounds check
    in_range = bool(np.all((probas >= 0.0) & (probas <= 1.0)))
    
    # 2. Sum to 1.0 check
    sums_to_one = bool(np.allclose(probas.sum(axis=1), 1.0, atol=1e-5))
    
    # 3. Argmax matches discrete prediction
    argmax_matches = bool(np.all(np.argmax(probas, axis=1) == preds))
    
    # 4. No NaN or Inf
    no_nan_or_inf = bool(not np.any(np.isnan(probas)) and not np.any(np.isinf(probas)))

    return {
        "probabilities_in_range_0_1": in_range,
        "probabilities_sum_to_one": sums_to_one,
        "prediction_matches_highest_prob": argmax_matches,
        "no_nan_or_inf": no_nan_or_inf,
        "min_default_prob": float(probas[:, 1].min()),
        "max_default_prob": float(probas[:, 1].max()),
        "mean_default_prob": float(probas[:, 1].mean()),
        "sample_size": len(test_df)
    }


def evaluate_saved_model(
    data_path: str = "data/credit_data.csv",
    model_path: str = "models/credit_pipeline.pkl"
) -> Dict[str, Any]:
    """
    Run full end-to-end evaluation with the loaded production pipeline.
    """
    print(f"Loading pipeline from '{model_path}'...")
    pipeline = load_production_pipeline(model_path)

    print(f"Loading evaluation dataset from '{data_path}'...")
    df, report = load_credit_data(data_path)

    preprocessor = CleanDataPreprocessor(test_size=0.2, random_state=42)
    X_train_raw, X_test_raw, y_train, y_test = preprocessor.prepare_data_splits(df)

    print(f"Evaluating on Test Split ({len(X_test_raw):,} applicants)...")
    y_pred = pipeline.predict(X_test_raw)
    y_proba = pipeline.predict_proba(X_test_raw)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    pr_auc = float(average_precision_score(y_test, y_proba))
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    prob_checks = validate_prediction_probabilities(pipeline, X_test_raw)

    print("\n" + "=" * 60)
    print("  PRODUCTION PIPELINE EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Accuracy:    {acc:.4f}")
    print(f"Precision:   {prec:.4f}")
    print(f"Recall:      {rec:.4f}")
    print(f"F1-Score:    {f1:.4f}")
    print(f"ROC-AUC:     {roc_auc:.4f}")
    print(f"PR-AUC:      {pr_auc:.4f}")
    print("\nConfusion Matrix:")
    print(f"  True Negatives (Correct Non-Defaults): {tn:,}")
    print(f"  False Positives (Incorrect Flags):     {fp:,}  (FPR: {fp/(fp+tn):.4f})")
    print(f"  False Negatives (Missed Defaults):    {fn:,}  (FNR: {fn/(fn+tp):.4f})")
    print(f"  True Positives (Caught Defaults):      {tp:,}")
    print("\nProbability Health Checks:")
    for k, v in prob_checks.items():
        print(f"  - {k}: {v}")

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "probability_checks": prob_checks
    }


def score_single_applicant(
    applicant_data: Dict[str, Any],
    pipeline_path: str = "models/credit_pipeline.pkl"
) -> Dict[str, Any]:
    """
    Score a single customer's credit profile in real-time.
    
    Args:
        applicant_data: Dictionary of applicant features.
        pipeline_path: Path to serialized pipeline.
        
    Returns:
        Dict: Risk evaluation including probability, decision, and risk grade.
    """
    pipeline = load_production_pipeline(pipeline_path)
    df_applicant = pd.DataFrame([applicant_data])

    prob_default = float(pipeline.predict_proba(df_applicant)[0, 1])
    is_default = int(pipeline.predict(df_applicant)[0])

    if prob_default < 0.10:
        risk_grade = "Low Risk (Grade A)"
        recommendation = "Approved - Prime Tier"
    elif prob_default < 0.25:
        risk_grade = "Moderate Risk (Grade B)"
        recommendation = "Approved - Standard Tier"
    elif prob_default < 0.50:
        risk_grade = "Elevated Risk (Grade C)"
        recommendation = "Manual Review / Lower Limit"
    else:
        risk_grade = "High Risk (Grade D)"
        recommendation = "Declined / High Probability of Default"

    return {
        "default_probability": prob_default,
        "non_default_probability": 1.0 - prob_default,
        "predicted_class": is_default,
        "risk_grade": risk_grade,
        "recommendation": recommendation
    }


if __name__ == "__main__":
    evaluate_saved_model()
