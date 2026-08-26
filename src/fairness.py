"""
Credit Scoring Model — Fairness & Bias Analysis Module
======================================================
Comprehensive, statistically rigorous group-wise fairness auditing.

Audited Attributes Present in Dataset:
- SEX (1 = Male, 2 = Female)
- EDUCATION (1 = Graduate School, 2 = University, 3 = High School, 4 = Others, 5/6 = Undocumented)
- MARRIAGE (1 = Married, 2 = Single, 3 = Others/Divorced, 0 = Undocumented)
- AGE_GROUP (21-29, 30-39, 40-49, 50-59, 60+)

Unavailable Attributes in UCI Credit Card Dataset:
- Race / Ethnicity
- Geographic Location / Zip Code / Nationality
- Income Level (Only credit limit proxy available)
- Religion / Disability / Marital Dependents

Important Fairness Principles:
- We do NOT claim the model is "unbiased" or "fair".
- Removing demographic features does NOT prove fairness due to proxy variables.
- We measure empirical group-wise metrics and disclose all dataset and sample size limitations.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


MIN_SAMPLE_SIZE_THRESHOLD = 300
MIN_SAMPLE_SIZE_CRITICAL = 100

DEMOGRAPHIC_CONFIGS = {
    "SEX": {
        "display_name": "Gender / Sex",
        "description": "Biological sex recorded at credit card account opening.",
        "type": "categorical",
        "groups": {
            1: {"label": "Male", "is_reference_candidate": True},
            2: {"label": "Female", "is_reference_candidate": True},
        },
        "default_reference": 2,  # Largest group in dataset (~60.4%)
    },
    "EDUCATION": {
        "display_name": "Education Level",
        "description": "Highest completed education level recorded.",
        "type": "categorical",
        "groups": {
            1: {"label": "Graduate School", "is_reference_candidate": True},
            2: {"label": "University", "is_reference_candidate": True},
            3: {"label": "High School", "is_reference_candidate": True},
            4: {"label": "Others", "is_reference_candidate": False},
            5: {"label": "Unknown / Undocumented", "is_reference_candidate": False},
            6: {"label": "Undocumented (Category 6)", "is_reference_candidate": False},
            0: {"label": "Undocumented (Category 0)", "is_reference_candidate": False},
        },
        "default_reference": 2,  # University is largest group (~46.8%)
    },
    "MARRIAGE": {
        "display_name": "Marital Status",
        "description": "Civil marital status of applicant.",
        "type": "categorical",
        "groups": {
            1: {"label": "Married", "is_reference_candidate": True},
            2: {"label": "Single", "is_reference_candidate": True},
            3: {"label": "Divorced / Others", "is_reference_candidate": False},
            0: {"label": "Undocumented", "is_reference_candidate": False},
        },
        "default_reference": 2,  # Single is largest group (~53.2%)
    },
    "AGE_GROUP": {
        "display_name": "Age Bracket",
        "description": "Discretized applicant age cohorts.",
        "type": "binned",
        "groups": {
            "21-29": {"label": "21–29 (Young Adult)", "is_reference_candidate": True},
            "30-39": {"label": "30–39 (Early Career)", "is_reference_candidate": True},
            "40-49": {"label": "40–49 (Mid Career)", "is_reference_candidate": True},
            "50-59": {"label": "50–59 (Pre-Retirement)", "is_reference_candidate": True},
            "60+": {"label": "60+ (Senior)", "is_reference_candidate": False},
        },
        "default_reference": "30-39",  # Largest working cohort
    },
}


def bin_age_groups(ages: Union[pd.Series, np.ndarray, List[int]]) -> List[str]:
    """
    Categorize continuous AGE values into standard demographic cohorts.
    """
    cohorts = []
    for a in ages:
        try:
            val = float(a)
            if val < 30:
                cohorts.append("21-29")
            elif val < 40:
                cohorts.append("30-39")
            elif val < 50:
                cohorts.append("40-49")
            elif val < 60:
                cohorts.append("50-59")
            else:
                cohorts.append("60+")
        except (ValueError, TypeError):
            cohorts.append("Unknown")
    return cohorts


def calculate_confusion_matrix_counts(
    y_true: Union[pd.Series, np.ndarray, List[int]],
    y_pred: Union[pd.Series, np.ndarray, List[int]]
) -> Dict[str, int]:
    """
    Calculate TP, FP, TN, FN safely from binary sequences.
    1 = Positive (Default predicted/actual), 0 = Negative (Non-default).
    """
    y_t = np.asarray(y_true, dtype=int)
    y_p = np.asarray(y_pred, dtype=int)

    tp = int(np.sum((y_t == 1) & (y_p == 1)))
    fp = int(np.sum((y_t == 0) & (y_p == 1)))
    tn = int(np.sum((y_t == 0) & (y_p == 0)))
    fn = int(np.sum((y_t == 1) & (y_p == 0)))

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "total": len(y_t),
        "actual_positives": tp + fn,
        "actual_negatives": tn + fp,
        "predicted_positives": tp + fp,
        "predicted_negatives": tn + fn,
    }


def calculate_group_metrics(
    y_true: Union[pd.Series, np.ndarray, List[int]],
    y_pred: Union[pd.Series, np.ndarray, List[int]],
    y_prob: Optional[Union[pd.Series, np.ndarray, List[float]]] = None,
    min_sample_threshold: int = MIN_SAMPLE_SIZE_THRESHOLD
) -> Dict[str, Any]:
    """
    Compute mathematically sound group-level fairness & classification metrics.
    Handles zero denominators gracefully.
    """
    counts = calculate_confusion_matrix_counts(y_true, y_pred)
    tp, fp, tn, fn, total = counts["tp"], counts["fp"], counts["tn"], counts["fn"], counts["total"]

    # 1. Base Rate (Actual default prevalence in this group)
    base_rate = (tp + fn) / total if total > 0 else 0.0

    # 2. Positive Prediction Rate (Selection Rate / Rate of Default Prediction)
    selection_rate = (tp + fp) / total if total > 0 else 0.0

    # 3. Recall / True Positive Rate = TP / (TP + FN)
    actual_pos = tp + fn
    recall = (tp / actual_pos) if actual_pos > 0 else None

    # 4. False Positive Rate = FP / (FP + TN)
    actual_neg = tn + fp
    fpr = (fp / actual_neg) if actual_neg > 0 else None

    # 5. False Negative Rate = FN / (FN + TP) = 1 - Recall
    fnr = (fn / actual_pos) if actual_pos > 0 else None

    # 6. Precision / Positive Predictive Value = TP / (TP + FP)
    predicted_pos = tp + fp
    precision = (tp / predicted_pos) if predicted_pos > 0 else None

    # 7. Accuracy = (TP + TN) / total
    accuracy = ((tp + tn) / total) if total > 0 else None

    # 8. Mean Predicted Probability
    mean_prob = None
    if y_prob is not None and len(y_prob) > 0:
        mean_prob = float(np.mean(y_prob))

    # 9. Sample Size Check
    is_small_sample = total < min_sample_threshold
    is_critical_sample = total < MIN_SAMPLE_SIZE_CRITICAL

    warning_msg = None
    if is_critical_sample:
        warning_msg = f"Critical sample size warning: Only {total} observations. Group-level metrics have high statistical variance."
    elif is_small_sample:
        warning_msg = f"Limited sample size ({total} observations); group-level metrics may be statistically unstable."

    return {
        "sample_count": total,
        "counts": counts,
        "base_rate": round(base_rate, 4),
        "positive_prediction_rate": round(selection_rate, 4),
        "recall": round(recall, 4) if recall is not None else None,
        "false_positive_rate": round(fpr, 4) if fpr is not None else None,
        "false_negative_rate": round(fnr, 4) if fnr is not None else None,
        "precision": round(precision, 4) if precision is not None else None,
        "accuracy": round(accuracy, 4) if accuracy is not None else None,
        "mean_predicted_probability": round(mean_prob, 4) if mean_prob is not None else None,
        "is_small_sample": is_small_sample,
        "is_critical_sample": is_critical_sample,
        "sample_warning": warning_msg,
    }


def calculate_group_disparities(
    group_metrics: Dict[str, Any],
    baseline_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate absolute differences and relative ratios against a baseline reference group.
    Handles zero baselines and missing values without crashing.
    """
    disparities = {}

    metric_keys = [
        "positive_prediction_rate",
        "recall",
        "false_positive_rate",
        "false_negative_rate",
        "precision",
        "accuracy",
        "base_rate",
    ]

    for key in metric_keys:
        g_val = group_metrics.get(key)
        b_val = baseline_metrics.get(key)

        diff = None
        ratio = None

        if g_val is not None and b_val is not None:
            diff = round(g_val - b_val, 4)
            if b_val > 1e-6:
                ratio = round(g_val / b_val, 4)
            elif g_val == 0.0 and b_val == 0.0:
                ratio = 1.0

        disparities[f"{key}_diff"] = diff
        disparities[f"{key}_ratio"] = ratio

    return disparities


def audit_attribute_fairness(
    df: pd.DataFrame,
    attribute_col: str,
    y_true_col: str = "default_payment_next_month",
    y_pred_col: str = "prediction",
    y_prob_col: Optional[str] = "default_probability",
    reference_group: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Perform a complete fairness audit for a given grouping attribute across all sub-cohorts.
    """
    if attribute_col not in df.columns:
        if attribute_col == "AGE_GROUP" and "AGE" in df.columns:
            df = df.copy()
            df["AGE_GROUP"] = bin_age_groups(df["AGE"])
        else:
            raise KeyError(f"Attribute column '{attribute_col}' not found in dataset.")

    config = DEMOGRAPHIC_CONFIGS.get(attribute_col, {
        "display_name": attribute_col,
        "description": f"Group attribute: {attribute_col}",
        "groups": {},
        "default_reference": None,
    })

    unique_vals = sorted(df[attribute_col].unique(), key=lambda x: (str(type(x)), str(x)))

    # Determine reference group
    if reference_group is None or reference_group not in unique_vals:
        reference_group = config.get("default_reference")
        if reference_group not in unique_vals and len(unique_vals) > 0:
            # Fallback to largest group
            group_counts = df[attribute_col].value_counts()
            reference_group = group_counts.index[0]

    groups_data = {}
    for val in unique_vals:
        sub_df = df[df[attribute_col] == val]
        y_true = sub_df[y_true_col]
        y_pred = sub_df[y_pred_col]
        y_prob = sub_df[y_prob_col] if (y_prob_col and y_prob_col in sub_df.columns) else None

        metrics = calculate_group_metrics(y_true, y_pred, y_prob)
        group_meta = config.get("groups", {}).get(val, {})
        metrics["label"] = group_meta.get("label", str(val))
        metrics["group_value"] = val
        metrics["is_reference"] = bool(val == reference_group)
        groups_data[str(val)] = metrics

    # Calculate disparities vs reference group
    ref_key = str(reference_group)
    baseline_metrics = groups_data.get(ref_key, {})

    for val_str, g_data in groups_data.items():
        if val_str != ref_key and baseline_metrics:
            g_data["disparities_vs_baseline"] = calculate_group_disparities(g_data, baseline_metrics)
        else:
            g_data["disparities_vs_baseline"] = {
                "positive_prediction_rate_diff": 0.0,
                "recall_diff": 0.0,
                "false_positive_rate_diff": 0.0,
                "false_negative_rate_diff": 0.0,
                "precision_diff": 0.0,
                "accuracy_diff": 0.0,
            }

    # Summary analysis
    max_ppr_diff = 0.0
    max_recall_diff = 0.0
    max_fpr_diff = 0.0

    for val_str, g_data in groups_data.items():
        if not g_data.get("is_small_sample"):
            disp = g_data.get("disparities_vs_baseline", {})
            p_diff = abs(disp.get("positive_prediction_rate_diff") or 0.0)
            r_diff = abs(disp.get("recall_diff") or 0.0)
            f_diff = abs(disp.get("false_positive_rate_diff") or 0.0)

            max_ppr_diff = max(max_ppr_diff, p_diff)
            max_recall_diff = max(max_recall_diff, r_diff)
            max_fpr_diff = max(max_fpr_diff, f_diff)

    return {
        "attribute": attribute_col,
        "display_name": config.get("display_name", attribute_col),
        "description": config.get("description", ""),
        "reference_group": reference_group,
        "reference_group_label": config.get("groups", {}).get(reference_group, {}).get("label", str(reference_group)),
        "total_records_evaluated": len(df),
        "groups": groups_data,
        "summary": {
            "max_selection_rate_gap": round(max_ppr_diff, 4),
            "max_recall_gap": round(max_recall_diff, 4),
            "max_fpr_gap": round(max_fpr_diff, 4),
        },
        "limitations": [
            "Group-level metrics describe model behavior on this historical dataset and must NOT be taken as proof of fairness or unfairness.",
            "Features not explicitly present (e.g., race, location, disability) could not be evaluated.",
            "Removing demographic variables from inputs does not guarantee zero disparity due to correlation with financial history (proxies).",
            "Groups with small sample sizes exhibit higher estimation uncertainty.",
        ]
    }


def generate_full_fairness_report(
    eval_df: pd.DataFrame,
    y_true_col: str = "default_payment_next_month",
    y_pred_col: str = "prediction",
    y_prob_col: str = "default_probability"
) -> Dict[str, Any]:
    """
    Generate comprehensive multi-attribute fairness assessment across all valid dataset features.
    """
    # Ensure AGE_GROUP is populated
    df = eval_df.copy()
    if "AGE" in df.columns and "AGE_GROUP" not in df.columns:
        df["AGE_GROUP"] = bin_age_groups(df["AGE"])

    supported_attributes = ["SEX", "EDUCATION", "MARRIAGE", "AGE_GROUP"]
    attributes_report = {}

    for attr in supported_attributes:
        if attr in df.columns:
            attributes_report[attr] = audit_attribute_fairness(
                df,
                attribute_col=attr,
                y_true_col=y_true_col,
                y_pred_col=y_pred_col,
                y_prob_col=y_prob_col
            )

    return {
        "dataset_audit": {
            "total_evaluated_samples": len(df),
            "available_demographics": [
                {"name": "SEX", "label": "Gender / Sex", "categories": ["Male", "Female"]},
                {"name": "EDUCATION", "label": "Education Level", "categories": ["Graduate School", "University", "High School", "Others", "Unknown"]},
                {"name": "MARRIAGE", "label": "Marital Status", "categories": ["Married", "Single", "Divorced / Others"]},
                {"name": "AGE", "label": "Age Cohort", "categories": ["21–29", "30–39", "40–49", "50–59", "60+"]},
            ],
            "unavailable_demographics": [
                "Race / Ethnicity (Completely absent from dataset)",
                "Geographic Region / Zip Code / Nationality (Absent)",
                "Annual Household Income / Wealth (Direct income absent; credit limit serves as proxy)",
                "Religion, Disability Status, Sexual Orientation (Absent)",
                "Family Size & Number of Dependents (Absent)",
            ],
            "removed_variables": ["ID (Pure identifier)"],
            "retained_pipeline_variables": "23 raw financial/demographic variables + 16 engineered domain features",
        },
        "attributes": attributes_report,
        "fairness_principles": {
            "no_unbiased_claim": "We do NOT claim the model is unbiased or fair. Fairness is multi-dimensional and context-dependent.",
            "no_blindness_proof": "Removing sensitive features from model training does not eliminate group disparities due to correlated financial proxies.",
            "sample_size_discipline": "Small demographic cohorts (<300 samples) are flagged with statistical instability warnings.",
        },
        "global_disclaimer": "This fairness audit is an empirical model assessment tool for transparency. It does not provide legal compliance certification or guarantees of non-discrimination."
    }
