"""
Credit Scoring Model — Human-Readable Explainability Layer
===========================================================
Human-Centered Machine Learning for Credit Risk Analysis.
Translates complex ML predictions, Gini feature importances, and engineered financial indicators
into clear, actionable, and deterministic explanations.

Design Principles:
1. No LLMs, Generative AI, or synthetic text hallucinations.
2. Deterministic evaluation grounded in actual applicant financial records.
3. Feature engineering powered by the single source of truth (CreditFeatureEngineer).
4. Explicit separation between global statistical association (Gini importance) and individual causality.
5. Bidirectional reasoning: Identifies both risk drivers (negative factors) and credit strengths (positive factors).
"""

import json
import os
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from feature_engineering import CreditFeatureEngineer
from predict import (
    LEGAL_DISCLAIMER,
    PRIVACY_STATEMENT,
    PROBABILITY_CALIBRATION_NOTICE,
    predict_credit_risk,
    validate_applicant_input,
)

# -----------------------------------------------------------------------------
# FINANCIAL TERMINOLOGY MAPPINGS (Reused for Multilingual UI in future phases)
# -----------------------------------------------------------------------------
FEATURE_TERMINOLOGY_MAP: Dict[str, Dict[str, str]] = {
    "PAY_0": {
        "label": "Recent Repayment Status",
        "category": "Repayment Timeliness",
        "description": "Payment timeliness in the most recent billing cycle (September)."
    },
    "PAY_2": {
        "label": "Repayment Status (1 Month Prior)",
        "category": "Repayment Timeliness",
        "description": "Payment timeliness in August."
    },
    "PAY_3": {
        "label": "Repayment Status (2 Months Prior)",
        "category": "Repayment Timeliness",
        "description": "Payment timeliness in July."
    },
    "PAY_4": {
        "label": "Repayment Status (3 Months Prior)",
        "category": "Repayment Timeliness",
        "description": "Payment timeliness in June."
    },
    "PAY_5": {
        "label": "Repayment Status (4 Months Prior)",
        "category": "Repayment Timeliness",
        "description": "Payment timeliness in May."
    },
    "PAY_6": {
        "label": "Repayment Status (5 Months Prior)",
        "category": "Repayment Timeliness",
        "description": "Payment timeliness in April."
    },
    "MAX_DELINQUENCY": {
        "label": "Peak Delinquency Delay",
        "category": "Delinquency Summary",
        "description": "Highest payment delay observed across the 6-month observation window."
    },
    "NUM_DELINQUENT_MONTHS": {
        "label": "Past-Due Months Count",
        "category": "Delinquency Summary",
        "description": "Number of billing cycles with delayed payments (out of 6)."
    },
    "AVG_DELAY_MONTHS": {
        "label": "Average Repayment Delay",
        "category": "Delinquency Summary",
        "description": "Mean delay duration across all 6 billing cycles."
    },
    "DELINQUENCY_TREND": {
        "label": "Delinquency Momentum",
        "category": "Delinquency Summary",
        "description": "Direction of repayment timeliness (recent status minus historical status)."
    },
    "UTILIZATION_RECENT": {
        "label": "Recent Credit Utilization",
        "category": "Credit Utilization",
        "description": "Proportion of available credit limit used in the most recent billing cycle."
    },
    "UTILIZATION_AVG": {
        "label": "6-Month Average Credit Utilization",
        "category": "Credit Utilization",
        "description": "Average revolving credit balance relative to credit limit over 6 months."
    },
    "UTILIZATION_MAX": {
        "label": "Peak Credit Utilization",
        "category": "Credit Utilization",
        "description": "Highest single-month credit utilization over the observation period."
    },
    "PAY_TO_BILL_1": {
        "label": "Recent Payment-to-Bill Ratio",
        "category": "Payment Adequacy",
        "description": "Fraction of previous statement balance repaid in the most recent cycle."
    },
    "PAY_TO_BILL_AVG": {
        "label": "Average Payment-to-Bill Ratio",
        "category": "Payment Adequacy",
        "description": "Mean payment adequacy across the 3 most recent statement cycles."
    },
    "TOTAL_BILL_AMT": {
        "label": "Aggregate Statement Balance",
        "category": "Debt Burden",
        "description": "Sum of all statement balances across the 6-month observation period."
    },
    "TOTAL_PAY_AMT": {
        "label": "Aggregate Repayments",
        "category": "Debt Burden",
        "description": "Sum of all cash payments made across the 6-month observation period."
    },
    "NET_DEFICIT": {
        "label": "Net Unpaid Cash Deficit",
        "category": "Debt Burden",
        "description": "Total billed amount minus total repaid amount over 6 months."
    },
    "DEFICIT_TO_LIMIT": {
        "label": "Unpaid Deficit-to-Limit Ratio",
        "category": "Debt Burden",
        "description": "Accumulated unpaid debt burden relative to approved credit limit."
    },
    "BILL_GROWTH_TREND": {
        "label": "Debt Expansion Trajectory",
        "category": "Debt Burden",
        "description": "Change in statement balance from Month 6 to Month 1 relative to credit limit."
    },
    "LIMIT_BAL": {
        "label": "Approved Credit Limit",
        "category": "Account Terms",
        "description": "Total revolving credit limit granted to the applicant."
    },
    "AGE": {
        "label": "Applicant Age",
        "category": "Demographics",
        "description": "Age of the applicant in years."
    }
}

# Global Gini feature importance weights from fitted Random Forest model
GLOBAL_FEATURE_IMPORTANCES: Dict[str, float] = {
    "PAY_0": 0.1625,
    "AVG_DELAY_MONTHS": 0.0989,
    "MAX_DELINQUENCY": 0.0793,
    "NUM_DELINQUENT_MONTHS": 0.0786,
    "PAY_2": 0.0507,
    "PAY_3": 0.0287,
    "DELINQUENCY_TREND": 0.0273,
    "PAY_4": 0.0268,
    "TOTAL_PAY_AMT": 0.0232,
    "PAY_TO_BILL_1": 0.0216,
    "UTILIZATION_MAX": 0.0211,
    "UTILIZATION_AVG": 0.0199,
    "UTILIZATION_RECENT": 0.0195,
    "PAY_TO_BILL_AVG": 0.0192,
    "TOTAL_BILL_AMT": 0.0190,
    "BILL_GROWTH_TREND": 0.0189,
    "DEFICIT_TO_LIMIT": 0.0183,
    "PAY_6": 0.0179,
    "PAY_AMT1": 0.0160,
    "LIMIT_BAL": 0.0152,
}

GLOBAL_VS_INDIVIDUAL_CAUSALITY_NOTICE = (
    "Model feature importance (Gini importance) indicates global statistical association across the "
    "training dataset. It reflects the model's reliance on each factor and does not prove that a specific "
    "variable caused an individual applicant's prediction."
)


def _format_currency(value: float) -> str:
    """Format numeric currency value with commas."""
    return f"${value:,.0f}" if abs(value) >= 1000 else f"${value:.2f}"


def _format_percentage(value: float) -> str:
    """Format ratio as percentage string."""
    return f"{value * 100.0:.1f}%"


def identify_risk_factors(row: pd.Series) -> List[Dict[str, Any]]:
    """
    Evaluate deterministic financial risk indicators for an applicant.

    Args:
        row: Series containing both raw and engineered financial features.

    Returns:
        List[Dict[str, Any]]: Identified risk drivers sorted by impact score.
    """
    risk_factors: List[Dict[str, Any]] = []

    # 1. Recent Repayment Status (PAY_0)
    pay_0 = row.get("PAY_0", 0)
    if pay_0 >= 2:
        risk_factors.append({
            "feature_name": "PAY_0",
            "human_label": FEATURE_TERMINOLOGY_MAP["PAY_0"]["label"],
            "direction": "negative",
            "severity": "high",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("PAY_0", 0.16),
            "actual_value": int(pay_0),
            "display_value": f"{int(pay_0)} months delayed",
            "explanation": (
                f"Your most recent repayment history shows a {int(pay_0)}-month payment delay, "
                "which is strongly associated with higher estimated default risk in this model."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("PAY_0", 0.16) * 3.0
        })
    elif pay_0 == 1:
        risk_factors.append({
            "feature_name": "PAY_0",
            "human_label": FEATURE_TERMINOLOGY_MAP["PAY_0"]["label"],
            "direction": "negative",
            "severity": "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("PAY_0", 0.16),
            "actual_value": int(pay_0),
            "display_value": "1 month delayed",
            "explanation": (
                "Your most recent billing cycle shows a 1-month payment delay, "
                "which elevates the estimated risk score under this model."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("PAY_0", 0.16) * 1.5
        })

    # 2. Historical Maximum Delinquency
    max_delinq = row.get("MAX_DELINQUENCY", 0)
    if max_delinq >= 2:
        risk_factors.append({
            "feature_name": "MAX_DELINQUENCY",
            "human_label": FEATURE_TERMINOLOGY_MAP["MAX_DELINQUENCY"]["label"],
            "direction": "negative",
            "severity": "high" if max_delinq >= 3 else "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("MAX_DELINQUENCY", 0.08),
            "actual_value": int(max_delinq),
            "display_value": f"{int(max_delinq)} months past due",
            "explanation": (
                f"Your credit history records a peak payment delay of {int(max_delinq)} months within the past 6 months, "
                "indicating past repayment stress."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("MAX_DELINQUENCY", 0.08) * (2.0 if max_delinq >= 3 else 1.2)
        })

    # 3. Number of Delinquent Months
    num_delinq = row.get("NUM_DELINQUENT_MONTHS", 0)
    if num_delinq >= 2:
        risk_factors.append({
            "feature_name": "NUM_DELINQUENT_MONTHS",
            "human_label": FEATURE_TERMINOLOGY_MAP["NUM_DELINQUENT_MONTHS"]["label"],
            "direction": "negative",
            "severity": "high" if num_delinq >= 4 else "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("NUM_DELINQUENT_MONTHS", 0.08),
            "actual_value": int(num_delinq),
            "display_value": f"{int(num_delinq)} of 6 months delayed",
            "explanation": (
                f"You experienced delayed payments across {int(num_delinq)} of the 6 observed billing cycles, "
                "suggesting recurring payment difficulties."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("NUM_DELINQUENT_MONTHS", 0.08) * (num_delinq / 2.0)
        })

    # 4. Recent Credit Utilization
    util_recent = row.get("UTILIZATION_RECENT", 0.0)
    if util_recent > 0.80:
        risk_factors.append({
            "feature_name": "UTILIZATION_RECENT",
            "human_label": FEATURE_TERMINOLOGY_MAP["UTILIZATION_RECENT"]["label"],
            "direction": "negative",
            "severity": "high" if util_recent > 1.0 else "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("UTILIZATION_RECENT", 0.02),
            "actual_value": round(float(util_recent), 4),
            "display_value": _format_percentage(util_recent),
            "explanation": (
                f"Your recent credit utilization ({_format_percentage(util_recent)}) is high relative to your credit limit, "
                "which is associated with elevated balance burden in this model."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("UTILIZATION_RECENT", 0.02) * (2.5 if util_recent > 1.0 else 1.5)
        })
    elif util_recent > 0.60:
        risk_factors.append({
            "feature_name": "UTILIZATION_RECENT",
            "human_label": FEATURE_TERMINOLOGY_MAP["UTILIZATION_RECENT"]["label"],
            "direction": "negative",
            "severity": "low",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("UTILIZATION_RECENT", 0.02),
            "actual_value": round(float(util_recent), 4),
            "display_value": _format_percentage(util_recent),
            "explanation": (
                f"Your recent credit utilization ({_format_percentage(util_recent)}) is above moderate guidelines (>60%), "
                "which moderately increases revolving balance exposure."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("UTILIZATION_RECENT", 0.02) * 1.0
        })

    # 5. Low Payment Adequacy (Payment-to-Bill Ratio)
    pay_to_bill = row.get("PAY_TO_BILL_1", 1.0)
    bill_prev = row.get("BILL_AMT2", 0.0)
    if pay_to_bill < 0.20 and bill_prev > 1000:
        risk_factors.append({
            "feature_name": "PAY_TO_BILL_1",
            "human_label": FEATURE_TERMINOLOGY_MAP["PAY_TO_BILL_1"]["label"],
            "direction": "negative",
            "severity": "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("PAY_TO_BILL_1", 0.02),
            "actual_value": round(float(pay_to_bill), 4),
            "display_value": _format_percentage(pay_to_bill),
            "explanation": (
                f"Your recent payment covered only {_format_percentage(pay_to_bill)} of your previous statement balance, "
                "indicating reliance on minimum payments or carrying unpaid revolving debt."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("PAY_TO_BILL_1", 0.02) * 1.8
        })

    # 6. Unpaid Net Deficit relative to Limit
    deficit_to_limit = row.get("DEFICIT_TO_LIMIT", 0.0)
    net_deficit = row.get("NET_DEFICIT", 0.0)
    if deficit_to_limit > 0.50 and net_deficit > 0:
        risk_factors.append({
            "feature_name": "DEFICIT_TO_LIMIT",
            "human_label": FEATURE_TERMINOLOGY_MAP["DEFICIT_TO_LIMIT"]["label"],
            "direction": "negative",
            "severity": "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("DEFICIT_TO_LIMIT", 0.02),
            "actual_value": round(float(deficit_to_limit), 4),
            "display_value": _format_percentage(deficit_to_limit),
            "explanation": (
                f"Your accumulated unpaid deficit ({_format_currency(net_deficit)}) equals {_format_percentage(deficit_to_limit)} "
                "of your total credit line, reflecting expanding debt burden over the 6-month period."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("DEFICIT_TO_LIMIT", 0.02) * 1.6
        })

    # 7. Worsening Delinquency Trend
    delinq_trend = row.get("DELINQUENCY_TREND", 0)
    if delinq_trend >= 2:
        risk_factors.append({
            "feature_name": "DELINQUENCY_TREND",
            "human_label": FEATURE_TERMINOLOGY_MAP["DELINQUENCY_TREND"]["label"],
            "direction": "negative",
            "severity": "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("DELINQUENCY_TREND", 0.03),
            "actual_value": int(delinq_trend),
            "display_value": f"+{int(delinq_trend)} delay increase",
            "explanation": (
                "Your repayment timeliness worsened in recent cycles compared to earlier months, "
                "indicating negative payment momentum."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("DELINQUENCY_TREND", 0.03) * 1.5
        })

    # Sort risk factors by impact score descending
    risk_factors.sort(key=lambda x: x["impact_score"], reverse=True)
    return risk_factors


def identify_positive_factors(row: pd.Series) -> List[Dict[str, Any]]:
    """
    Evaluate deterministic credit-strengthening and positive risk-mitigating indicators.

    Args:
        row: Series containing both raw and engineered financial features.

    Returns:
        List[Dict[str, Any]]: Identified positive factors sorted by impact score.
    """
    positive_factors: List[Dict[str, Any]] = []

    # 1. On-Time Recent Payment (PAY_0 <= 0)
    pay_0 = row.get("PAY_0", 0)
    if pay_0 <= 0:
        status_text = "paid in full" if pay_0 == -1 else ("no consumption" if pay_0 == -2 else "revolving on-time")
        positive_factors.append({
            "feature_name": "PAY_0",
            "human_label": FEATURE_TERMINOLOGY_MAP["PAY_0"]["label"],
            "direction": "positive",
            "significance": "high",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("PAY_0", 0.16),
            "actual_value": int(pay_0),
            "display_value": f"On-time ({status_text})",
            "explanation": (
                "Your most recent billing cycle shows no overdue delays, "
                "which is the strongest positive factor associated with lower risk in this model."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("PAY_0", 0.16) * 3.0
        })

    # 2. Perfect 6-Month On-Time Record
    num_delinq = row.get("NUM_DELINQUENT_MONTHS", 0)
    if num_delinq == 0:
        positive_factors.append({
            "feature_name": "NUM_DELINQUENT_MONTHS",
            "human_label": FEATURE_TERMINOLOGY_MAP["NUM_DELINQUENT_MONTHS"]["label"],
            "direction": "positive",
            "significance": "high",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("NUM_DELINQUENT_MONTHS", 0.08),
            "actual_value": 0,
            "display_value": "0 past-due cycles",
            "explanation": (
                "You maintained zero past-due cycles across all 6 observed months, "
                "demonstrating consistent payment discipline."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("NUM_DELINQUENT_MONTHS", 0.08) * 2.5
        })

    # 3. Disciplined Credit Utilization
    util_avg = row.get("UTILIZATION_AVG", 0.0)
    util_recent = row.get("UTILIZATION_RECENT", 0.0)
    if util_recent < 0.30:
        positive_factors.append({
            "feature_name": "UTILIZATION_RECENT",
            "human_label": FEATURE_TERMINOLOGY_MAP["UTILIZATION_RECENT"]["label"],
            "direction": "positive",
            "significance": "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("UTILIZATION_RECENT", 0.02),
            "actual_value": round(float(util_recent), 4),
            "display_value": _format_percentage(util_recent),
            "explanation": (
                f"Your recent credit utilization ({_format_percentage(util_recent)}) is low (<30%), "
                "indicating substantial available credit cushion."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("UTILIZATION_RECENT", 0.02) * 2.0
        })

    if util_avg < 0.30 and util_recent >= 0.30:
        positive_factors.append({
            "feature_name": "UTILIZATION_AVG",
            "human_label": FEATURE_TERMINOLOGY_MAP["UTILIZATION_AVG"]["label"],
            "direction": "positive",
            "significance": "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("UTILIZATION_AVG", 0.02),
            "actual_value": round(float(util_avg), 4),
            "display_value": _format_percentage(util_avg),
            "explanation": (
                f"Your 6-month average credit utilization ({_format_percentage(util_avg)}) reflects controlled balance management."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("UTILIZATION_AVG", 0.02) * 1.5
        })

    # 4. Strong Payment Adequacy (Payment-to-Bill Ratio)
    pay_to_bill_avg = row.get("PAY_TO_BILL_AVG", 1.0)
    if pay_to_bill_avg >= 0.80:
        positive_factors.append({
            "feature_name": "PAY_TO_BILL_AVG",
            "human_label": FEATURE_TERMINOLOGY_MAP["PAY_TO_BILL_AVG"]["label"],
            "direction": "positive",
            "significance": "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("PAY_TO_BILL_AVG", 0.02),
            "actual_value": round(float(pay_to_bill_avg), 4),
            "display_value": _format_percentage(pay_to_bill_avg),
            "explanation": (
                f"Your average payment-to-bill ratio is high ({_format_percentage(pay_to_bill_avg)}), "
                "indicating consistent settlement of billed balances rather than rolling debt."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("PAY_TO_BILL_AVG", 0.02) * 1.8
        })

    # 5. Non-Accumulating Net Deficit
    net_deficit = row.get("NET_DEFICIT", 0.0)
    if net_deficit <= 0:
        positive_factors.append({
            "feature_name": "NET_DEFICIT",
            "human_label": FEATURE_TERMINOLOGY_MAP["NET_DEFICIT"]["label"],
            "direction": "positive",
            "significance": "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("NET_DEFICIT", 0.01),
            "actual_value": round(float(net_deficit), 2),
            "display_value": _format_currency(net_deficit),
            "explanation": (
                "Your total repayments over 6 months equaled or exceeded your total billed amounts, "
                "demonstrating balanced cash flow."
            ),
            "impact_score": 0.03
        })

    # 6. Improving Repayment Recovery (Negative Delinquency Trend)
    delinq_trend = row.get("DELINQUENCY_TREND", 0)
    if delinq_trend < 0:
        positive_factors.append({
            "feature_name": "DELINQUENCY_TREND",
            "human_label": FEATURE_TERMINOLOGY_MAP["DELINQUENCY_TREND"]["label"],
            "direction": "positive",
            "significance": "medium",
            "importance": GLOBAL_FEATURE_IMPORTANCES.get("DELINQUENCY_TREND", 0.03),
            "actual_value": int(delinq_trend),
            "display_value": f"{int(delinq_trend)} delay reduction",
            "explanation": (
                "Your repayment timeliness improved in recent cycles compared to past delayed months, "
                "showing positive repayment recovery."
            ),
            "impact_score": GLOBAL_FEATURE_IMPORTANCES.get("DELINQUENCY_TREND", 0.03) * 1.5
        })

    # Sort positive factors by impact score descending
    positive_factors.sort(key=lambda x: x["impact_score"], reverse=True)
    return positive_factors


def explain_prediction(
    input_data: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    prediction_result: Optional[Dict[str, Any]] = None,
    pipeline_path: str = "models/credit_pipeline.pkl"
) -> Dict[str, Any]:
    """
    Generate complete human-readable explainability report for an applicant.

    Args:
        input_data: Raw applicant data (dict, pd.Series, or single-row pd.DataFrame).
        prediction_result: Optional pre-calculated result from predict_credit_risk().
        pipeline_path: Path to saved production pipeline.

    Returns:
        Dict[str, Any]: Comprehensive explainability package with top risk factors,
                        positive factors, contextual summary, and technical metrics.
    """
    # 1. Validate raw applicant input
    df_raw = validate_applicant_input(input_data)
    if len(df_raw) > 1:
        df_raw = df_raw.iloc[[0]]

    # 2. Obtain prediction if not already supplied
    if prediction_result is None:
        prediction_result = predict_credit_risk(df_raw, pipeline_path=pipeline_path)

    # 3. Execute feature engineering using single source of truth
    engineer = CreditFeatureEngineer()
    df_enriched = engineer.transform(df_raw)
    applicant_row = df_enriched.iloc[0]

    # 4. Extract risk drivers and positive mitigators
    risk_factors = identify_risk_factors(applicant_row)
    positive_factors = identify_positive_factors(applicant_row)

    # 5. Formulate contextual narrative summary
    risk_level = prediction_result.get("risk_level", "MEDIUM RISK")
    likelihood_pct = prediction_result.get("model_estimated_likelihood_pct", 50.0)
    pred_label = prediction_result.get("predicted_label", "Non-Default")

    if risk_level == "LOW RISK":
        if positive_factors:
            primary_strength = positive_factors[0]["human_label"].lower()
            summary = (
                f"The model estimates a low likelihood of default ({likelihood_pct:.1f}%), "
                f"supported primarily by strong {primary_strength} and disciplined balance management."
            )
        else:
            summary = (
                f"The model estimates a low likelihood of default ({likelihood_pct:.1f}%) "
                "based on the available repayment history."
            )
    elif risk_level == "MEDIUM RISK":
        if risk_factors and positive_factors:
            summary = (
                f"The model estimates a moderate default risk score of {likelihood_pct:.1f}% (classified as {pred_label}). "
                f"While positive factors like {positive_factors[0]['human_label'].lower()} provide stability, "
                f"factors such as {risk_factors[0]['human_label'].lower()} moderately increase estimated risk."
            )
        elif risk_factors:
            summary = (
                f"The model estimates a moderate default risk score of {likelihood_pct:.1f}%, "
                f"influenced by elevated {risk_factors[0]['human_label'].lower()}."
            )
        else:
            summary = (
                f"The model estimates a moderate default risk score of {likelihood_pct:.1f}% "
                "based on the available financial indicators."
            )
    else:  # HIGH RISK
        if risk_factors:
            primary_driver = risk_factors[0]["human_label"].lower()
            secondary = f" and {risk_factors[1]['human_label'].lower()}" if len(risk_factors) > 1 else ""
            summary = (
                f"The model estimates an elevated default likelihood of {likelihood_pct:.1f}% (classified as {pred_label}). "
                f"This assessment is primarily associated with {primary_driver}{secondary}."
            )
        else:
            summary = (
                f"The model estimates an elevated default likelihood of {likelihood_pct:.1f}% "
                "based on overall payment history and balance metrics."
            )

    # 6. Technical indicators dictionary (useful for audit/debug views)
    technical_factors = {
        col: round(float(applicant_row[col]), 4) if isinstance(applicant_row[col], (int, float, np.number)) else str(applicant_row[col])
        for col in df_enriched.columns
    }

    # 7. Model limitations
    limitations = [
        PROBABILITY_CALIBRATION_NOTICE,
        GLOBAL_VS_INDIVIDUAL_CAUSALITY_NOTICE,
        "The model is trained on historical 6-month consumer credit card data (April-September) and does not capture macroeconomic shifts or external non-bureau financial events.",
        "Assessments are purely algorithmic approximations and must not be used as an automated sole decider for credit underwriting."
    ]

    return {
        "summary": summary,
        "predicted_label": pred_label,
        "predicted_class": prediction_result.get("predicted_class", 0),
        "model_estimated_likelihood_pct": likelihood_pct,
        "default_probability": prediction_result.get("default_probability", 0.0),
        "risk_level": risk_level,
        "top_risk_factors": risk_factors[:5],  # Top 5 most prominent risk drivers
        "positive_factors": positive_factors[:5],  # Top 5 most prominent positive mitigators
        "technical_factors": technical_factors,
        "global_vs_individual_notice": GLOBAL_VS_INDIVIDUAL_CAUSALITY_NOTICE,
        "limitations": limitations,
        "disclaimer": LEGAL_DISCLAIMER,
        "privacy_statement": PRIVACY_STATEMENT
    }


if __name__ == "__main__":
    from data_loader import load_credit_data
    df, _ = load_credit_data("data/credit_data.csv")

    # Sample Applicant A: On-time borrower (Index 2)
    sample_a = df.iloc[2].to_dict()
    pred_a = predict_credit_risk(sample_a)
    exp_a = explain_prediction(sample_a, pred_a)

    print("==================================================")
    print(" SAMPLE APPLICANT A (Low Risk Profile)")
    print("==================================================")
    print(f"Prediction: {exp_a['predicted_label']} (Risk: {exp_a['risk_level']})")
    print(f"Estimated Likelihood: {exp_a['model_estimated_likelihood_pct']}%")
    print(f"Summary: {exp_a['summary']}\n")
    print("Top Positive Factors:")
    for f in exp_a["positive_factors"]:
        print(f"  + [{f['human_label']}]: {f['explanation']}")
    print("Top Risk Factors:")
    for f in exp_a["top_risk_factors"]:
        print(f"  - [{f['human_label']}]: {f['explanation']}")

    # Sample Applicant B: Delinquent borrower (Index 0)
    sample_b = df.iloc[0].to_dict()
    pred_b = predict_credit_risk(sample_b)
    exp_b = explain_prediction(sample_b, pred_b)

    print("\n==================================================")
    print(" SAMPLE APPLICANT B (High Risk Profile)")
    print("==================================================")
    print(f"Prediction: {exp_b['predicted_label']} (Risk: {exp_b['risk_level']})")
    print(f"Estimated Likelihood: {exp_b['model_estimated_likelihood_pct']}%")
    print(f"Summary: {exp_b['summary']}\n")
    print("Top Risk Factors:")
    for f in exp_b["top_risk_factors"]:
        print(f"  - [{f['human_label']}]: {f['explanation']}")
    print("Top Positive Factors:")
    for f in exp_b["positive_factors"]:
        print(f"  + [{f['human_label']}]: {f['explanation']}")
