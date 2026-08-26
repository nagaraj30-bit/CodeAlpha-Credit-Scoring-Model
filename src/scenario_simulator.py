"""
Credit Scoring Model — What-If Scenario Simulator Engine
=========================================================
Human-Centered Machine Learning for Credit Risk Analysis.
Enables transparent, interactive simulation of hypothetical financial adjustments
by re-running the exact same production prediction pipeline, explainability engine,
and financial health indicator.

Design Principles:
1. Reuses the EXACT production pipeline (models/credit_pipeline.pkl) — No second model or simplified formulas.
2. 100% deterministic and reproducible.
3. Strictly avoids Generative AI, LLMs, or hardcoded mock predictions.
4. Uses strictly non-promissory, educational language:
   - "Under this model, the simulated scenario produces a different estimated risk."
   - "This scenario is associated with a lower estimated model risk."
   - Never promises loan approval, credit rating guarantees, or binding lending outcomes.
5. Bidirectional delta comparisons for default likelihood, risk tier, financial health, and explainability factors.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from financial_health import calculate_financial_health
from predict import (
    LEGAL_DISCLAIMER,
    PRIVACY_STATEMENT,
    PROBABILITY_CALIBRATION_NOTICE,
    load_prediction_pipeline,
    predict_credit_risk,
    validate_applicant_input,
)
from risk_reasons import FEATURE_TERMINOLOGY_MAP, explain_prediction

# -----------------------------------------------------------------------------
# SUPPORTED SCENARIO VARIABLES & SAFE BOUNDS
# -----------------------------------------------------------------------------
# Exposes only empirical features that exist in the UCI dataset and can be
# meaningfully modified in realistic consumer credit scenarios.
SUPPORTED_SCENARIO_VARIABLES = {
    "LIMIT_BAL": {
        "human_name": "Approved Credit Limit",
        "category": "Credit Facility",
        "min_value": 10000.0,
        "max_value": 1000000.0,
        "description": "Total revolving credit line granted by the financial institution.",
    },
    "PAY_0": {
        "human_name": "Recent Repayment Status (September)",
        "category": "Repayment Timeliness",
        "min_value": -2,
        "max_value": 8,
        "description": "Repayment timeliness in the most recent billing cycle (-1=Paid in full, 0=Revolving on-time, 1..8=Months overdue).",
    },
    "PAY_2": {
        "human_name": "Repayment Status (August)",
        "category": "Repayment Timeliness",
        "min_value": -2,
        "max_value": 8,
        "description": "Repayment timeliness 1 month prior.",
    },
    "PAY_3": {
        "human_name": "Repayment Status (July)",
        "category": "Repayment Timeliness",
        "min_value": -2,
        "max_value": 8,
        "description": "Repayment timeliness 2 months prior.",
    },
    "PAY_4": {
        "human_name": "Repayment Status (June)",
        "category": "Repayment Timeliness",
        "min_value": -2,
        "max_value": 8,
        "description": "Repayment timeliness 3 months prior.",
    },
    "PAY_5": {
        "human_name": "Repayment Status (May)",
        "category": "Repayment Timeliness",
        "min_value": -2,
        "max_value": 8,
        "description": "Repayment timeliness 4 months prior.",
    },
    "PAY_6": {
        "human_name": "Repayment Status (April)",
        "category": "Repayment Timeliness",
        "min_value": -2,
        "max_value": 8,
        "description": "Repayment timeliness 5 months prior.",
    },
    "BILL_AMT1": {
        "human_name": "Recent Statement Bill Amount",
        "category": "Billed Balance",
        "min_value": -50000.0,
        "max_value": 1000000.0,
        "description": "Most recent statement balance (September).",
    },
    "BILL_AMT2": {
        "human_name": "Bill Amount (August)",
        "category": "Billed Balance",
        "min_value": -50000.0,
        "max_value": 1000000.0,
        "description": "Statement balance 1 month prior.",
    },
    "PAY_AMT1": {
        "human_name": "Recent Payment Amount",
        "category": "Repayment Amount",
        "min_value": 0.0,
        "max_value": 1000000.0,
        "description": "Amount paid in recent cycle (September) towards previous bill.",
    },
    "PAY_AMT2": {
        "human_name": "Payment Amount (August)",
        "category": "Repayment Amount",
        "min_value": 0.0,
        "max_value": 1000000.0,
        "description": "Amount paid in August towards July bill.",
    },
}

SIMULATOR_DISCLAIMER = (
    "The What-If Simulator demonstrates how the model's estimated default likelihood "
    "and financial health indicators change under hypothetical input conditions. "
    "Under this model, the simulated scenario produces a different estimated risk. "
    "This does NOT predict guaranteed future outcomes, bank approvals, or loan decisions."
)


def validate_scenario_modifications(modifications: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize scenario modifications against supported variables and safe bounds.

    Args:
        modifications: Dictionary of feature modifications (e.g. {'PAY_0': 0, 'PAY_AMT1': 15000}).

    Returns:
        Dict[str, Any]: Sanitized dictionary containing only valid numeric modifications.
    """
    if not isinstance(modifications, dict):
        raise TypeError(f"Expected modifications as a dict; received {type(modifications).__name__}.")

    sanitized: Dict[str, Any] = {}
    for key, value in modifications.items():
        if value is None:
            continue

        key_upper = key.strip().upper()
        # Handle PAY_1 alias
        if key_upper == "PAY_1":
            key_upper = "PAY_0"

        # Check if key is a valid credit column
        try:
            val_num = float(value)
        except (ValueError, TypeError):
            continue  # Ignore non-numeric inputs

        # Apply domain-safe clipping if in supported variable list
        if key_upper in SUPPORTED_SCENARIO_VARIABLES:
            cfg = SUPPORTED_SCENARIO_VARIABLES[key_upper]
            val_clipped = np.clip(val_num, cfg["min_value"], cfg["max_value"])
            # Keep integer type for status codes
            if key_upper.startswith("PAY_") and not key_upper.startswith("PAY_AMT"):
                sanitized[key_upper] = int(round(val_clipped))
            else:
                sanitized[key_upper] = float(val_clipped)
        elif key_upper.startswith("BILL_AMT") or key_upper.startswith("PAY_AMT") or key_upper in ["AGE", "SEX", "EDUCATION", "MARRIAGE"]:
            # Other credit features can also be modified safely
            if key_upper.startswith("PAY_AMT"):
                sanitized[key_upper] = max(0.0, float(val_num))
            elif key_upper.startswith("BILL_AMT"):
                sanitized[key_upper] = float(val_num)
            elif key_upper in ["SEX", "EDUCATION", "MARRIAGE", "AGE"]:
                sanitized[key_upper] = int(round(val_num))
            else:
                sanitized[key_upper] = float(val_num)

    return sanitized


def apply_scenario_modifications(
    baseline_data: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    modifications: Dict[str, Any]
) -> pd.DataFrame:
    """
    Apply validated modifications to baseline applicant data.

    Args:
        baseline_data: Current applicant input.
        modifications: Dictionary of feature overrides.

    Returns:
        pd.DataFrame: Modified applicant DataFrame.
    """
    base_df = validate_applicant_input(baseline_data)
    mod_df = base_df.copy()
    sanitized_mods = validate_scenario_modifications(modifications)

    for col, new_val in sanitized_mods.items():
        if col in mod_df.columns:
            mod_df[col] = mod_df[col].astype(float)
            mod_df.loc[0, col] = float(new_val)

    return mod_df


def _compare_factor_lists(
    current_factors: List[Dict[str, Any]],
    scenario_factors: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare explainability factors between baseline and scenario to identify changes.
    """
    curr_dict = {f["feature_name"]: f for f in current_factors}
    scen_dict = {f["feature_name"]: f for f in scenario_factors}

    resolved = []
    for feat, factor in curr_dict.items():
        if feat not in scen_dict:
            resolved.append({
                "feature_name": feat,
                "human_label": factor["human_label"],
                "previous_status": factor["explanation"],
                "status": "Resolved / Cleared",
            })

    newly_added = []
    for feat, factor in scen_dict.items():
        if feat not in curr_dict:
            newly_added.append({
                "feature_name": feat,
                "human_label": factor["human_label"],
                "new_status": factor["explanation"],
                "status": "Newly Introduced",
            })

    retained = []
    for feat in curr_dict.keys() & scen_dict.keys():
        f_curr = curr_dict[feat]
        f_scen = scen_dict[feat]
        retained.append({
            "feature_name": feat,
            "human_label": f_curr["human_label"],
            "previous_explanation": f_curr["explanation"],
            "scenario_explanation": f_scen["explanation"],
            "severity_change": f"{f_curr.get('severity', 'N/A')} -> {f_scen.get('severity', 'N/A')}",
        })

    return {
        "resolved": resolved,
        "newly_added": newly_added,
        "retained": retained,
    }


def _compare_financial_health_components(
    curr_fhi: Dict[str, Any],
    scen_fhi: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare component-level Financial Health breakdown between baseline and scenario.
    """
    comp_comparison: Dict[str, Any] = {}
    curr_comps = curr_fhi.get("components", {})
    scen_comps = scen_fhi.get("components", {})

    for comp_key, curr_c in curr_comps.items():
        scen_c = scen_comps.get(comp_key, {})
        c_score = curr_c.get("score", 0.0)
        s_score = scen_c.get("score", 0.0)
        delta = round(s_score - c_score, 1)

        comp_comparison[comp_key] = {
            "name": curr_c.get("name", comp_key),
            "current_score": c_score,
            "scenario_score": s_score,
            "score_delta": delta,
            "current_status": curr_c.get("status", ""),
            "scenario_status": scen_c.get("status", ""),
            "current_display": curr_c.get("actual_value_display", ""),
            "scenario_display": scen_c.get("actual_value_display", ""),
            "direction": "IMPROVED" if delta > 0.5 else ("DETERIORATED" if delta < -0.5 else "UNCHANGED"),
        }

    return comp_comparison


def simulate_scenario(
    current_input: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    modifications: Dict[str, Any],
    pipeline_path: str = "models/credit_pipeline.pkl"
) -> Dict[str, Any]:
    """
    Simulate a What-If credit scenario by re-running the exact production pipeline.

    Flow:
    1. Current User Input -> Production Pipeline -> Current Prediction & Explainability & FHI
    2. Modified User Input -> Production Pipeline -> Scenario Prediction & Explainability & FHI
    3. Calculate continuous deltas and factor transitions.

    Args:
        current_input: Baseline applicant financial record.
        modifications: Dictionary of parameter modifications (e.g. {'PAY_0': 0, 'PAY_AMT1': 50000}).
        pipeline_path: Path to the production credit pipeline artifact.

    Returns:
        Dict[str, Any]: Complete comparative evaluation package.
    """
    # 1. Standardize baseline inputs and apply scenario modifications
    base_df = validate_applicant_input(current_input)
    sanitized_mods = validate_scenario_modifications(modifications)
    scen_df = apply_scenario_modifications(base_df, sanitized_mods)

    # 2. Run CURRENT input through production prediction, explainability, and FHI
    current_pred = predict_credit_risk(base_df, pipeline_path=pipeline_path)
    current_exp = explain_prediction(base_df, current_pred, pipeline_path=pipeline_path)
    current_fhi = calculate_financial_health(base_df)

    # 3. Run SCENARIO input through the EXACT SAME production pipeline, explainability, and FHI
    scenario_pred = predict_credit_risk(scen_df, pipeline_path=pipeline_path)
    scenario_exp = explain_prediction(scen_df, scenario_pred, pipeline_path=pipeline_path)
    scenario_fhi = calculate_financial_health(scen_df)

    # 4. Compute continuous probabilities and risk deltas
    p_curr = current_pred["default_probability"]
    p_scen = scenario_pred["default_probability"]
    prob_delta = round(p_scen - p_curr, 4)
    prob_delta_pct = round(prob_delta * 100.0, 2)

    # Risk level transition
    risk_curr = current_pred["risk_level"]
    risk_scen = scenario_pred["risk_level"]
    if prob_delta < -0.01:
        risk_direction = "IMPROVED"
    elif prob_delta > 0.01:
        risk_direction = "WORSENED"
    else:
        risk_direction = "UNCHANGED"

    # Financial health delta
    fhi_curr_score = current_fhi["score"]
    fhi_scen_score = scenario_fhi["score"]
    fhi_delta = fhi_scen_score - fhi_curr_score
    if fhi_delta > 0:
        fhi_direction = "IMPROVED"
    elif fhi_delta < 0:
        fhi_direction = "WORSENED"
    else:
        fhi_direction = "UNCHANGED"

    # 5. Compare risk and positive factors
    risk_factor_comp = _compare_factor_lists(
        current_factors=current_exp.get("top_risk_factors", []),
        scenario_factors=scenario_exp.get("top_risk_factors", [])
    )

    positive_factor_comp = _compare_factor_lists(
        current_factors=current_exp.get("positive_factors", []),
        scenario_factors=scenario_exp.get("positive_factors", [])
    )

    # 6. Compare Financial Health components
    component_comparison = _compare_financial_health_components(current_fhi, scenario_fhi)

    # 7. Document applied modifications with human readable names
    applied_mods_summary = []
    for k, v_new in sanitized_mods.items():
        v_old = base_df.iloc[0].get(k, np.nan)
        meta = SUPPORTED_SCENARIO_VARIABLES.get(k, {"human_name": k})
        human_name = meta["human_name"]
        applied_mods_summary.append({
            "feature": k,
            "human_name": human_name,
            "previous_value": v_old if not np.isnan(v_old) else "N/A",
            "scenario_value": v_new,
        })

    # 8. Generate safe, non-promissory comparative summary
    is_unchanged = (len(sanitized_mods) == 0) or (prob_delta == 0.0 and fhi_delta == 0)

    if is_unchanged:
        narrative_summary = (
            "No scenario modifications were applied. Baseline estimated risk and Financial Health "
            "remain unchanged under the model."
        )
    elif risk_direction == "IMPROVED":
        tier_change = f" ({risk_curr} → {risk_scen})" if risk_curr != risk_scen else f" ({risk_curr})"
        narrative_summary = (
            f"Under this model, the simulated scenario is associated with a lower estimated default likelihood "
            f"({current_pred['model_estimated_likelihood_pct']}% → {scenario_pred['model_estimated_likelihood_pct']}%, "
            f"a reduction of {abs(prob_delta_pct):.1f}% points{tier_change}). "
            f"Financial Health Indicator changes by {fhi_delta:+d} points ({fhi_curr_score} → {fhi_scen_score}/100, "
            f"{current_fhi['label']} → {scenario_fhi['label']})."
        )
    elif risk_direction == "WORSENED":
        tier_change = f" ({risk_curr} → {risk_scen})" if risk_curr != risk_scen else f" ({risk_curr})"
        narrative_summary = (
            f"Under this model, the simulated scenario is associated with an elevated estimated default likelihood "
            f"({current_pred['model_estimated_likelihood_pct']}% → {scenario_pred['model_estimated_likelihood_pct']}%, "
            f"an increase of {abs(prob_delta_pct):.1f}% points{tier_change}). "
            f"Financial Health Indicator changes by {fhi_delta:+d} points ({fhi_curr_score} → {fhi_scen_score}/100, "
            f"{current_fhi['label']} → {scenario_fhi['label']})."
        )
    else:
        narrative_summary = (
            f"Under this model, the simulated scenario produces minimal change in estimated default likelihood "
            f"({current_pred['model_estimated_likelihood_pct']}% vs {scenario_pred['model_estimated_likelihood_pct']}%). "
            f"Financial Health Indicator is {fhi_scen_score}/100 ({fhi_delta:+d} points)."
        )

    return {
        "current": {
            "predicted_class": current_pred["predicted_class"],
            "predicted_label": current_pred["predicted_label"],
            "default_probability": current_pred["default_probability"],
            "model_estimated_likelihood_pct": current_pred["model_estimated_likelihood_pct"],
            "risk_level": current_pred["risk_level"],
            "financial_health": {
                "score": current_fhi["score"],
                "label": current_fhi["label"],
                "components": current_fhi["components"],
                "summary": current_fhi["summary"],
            },
            "explainability": {
                "summary": current_exp["summary"],
                "top_risk_factors": current_exp["top_risk_factors"],
                "positive_factors": current_exp["positive_factors"],
            },
        },
        "scenario": {
            "predicted_class": scenario_pred["predicted_class"],
            "predicted_label": scenario_pred["predicted_label"],
            "default_probability": scenario_pred["default_probability"],
            "model_estimated_likelihood_pct": scenario_pred["model_estimated_likelihood_pct"],
            "risk_level": scenario_pred["risk_level"],
            "financial_health": {
                "score": scenario_fhi["score"],
                "label": scenario_fhi["label"],
                "components": scenario_fhi["components"],
                "summary": scenario_fhi["summary"],
            },
            "explainability": {
                "summary": scenario_exp["summary"],
                "top_risk_factors": scenario_exp["top_risk_factors"],
                "positive_factors": scenario_exp["positive_factors"],
            },
        },
        "comparison": {
            "default_probability_delta": prob_delta,
            "probability_change_pct_points": prob_delta_pct,
            "risk_direction": risk_direction,
            "risk_level_transition": f"{risk_curr} → {risk_scen}" if risk_curr != risk_scen else risk_curr,
            "financial_health_delta": fhi_delta,
            "financial_health_direction": fhi_direction,
            "financial_health_transition": f"{current_fhi['label']} ({fhi_curr_score}) → {scenario_fhi['label']} ({fhi_scen_score})",
            "component_comparison": component_comparison,
            "risk_factors_resolved": risk_factor_comp["resolved"],
            "risk_factors_newly_added": risk_factor_comp["newly_added"],
            "positive_factors_gained": positive_factor_comp["newly_added"],
            "positive_factors_lost": positive_factor_comp["resolved"],
            "modifications_applied": applied_mods_summary,
            "summary": narrative_summary,
        },
        "disclaimer": SIMULATOR_DISCLAIMER,
        "probability_notice": PROBABILITY_CALIBRATION_NOTICE,
        "privacy_statement": PRIVACY_STATEMENT,
    }


# -----------------------------------------------------------------------------
# HIGH-LEVEL ACTIONABLE PRESET SCENARIO HELPERS
# -----------------------------------------------------------------------------
def simulate_repayment_remediation(
    applicant: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    pipeline_path: str = "models/credit_pipeline.pkl"
) -> Dict[str, Any]:
    """
    Preset Scenario: Resolve recent payment delays to on-time status (PAY_0=0, PAY_2=0).
    """
    return simulate_scenario(
        applicant,
        modifications={"PAY_0": 0, "PAY_2": 0},
        pipeline_path=pipeline_path
    )


def simulate_balance_paydown(
    applicant: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    paydown_fraction: float = 0.50,
    pipeline_path: str = "models/credit_pipeline.pkl"
) -> Dict[str, Any]:
    """
    Preset Scenario: Pay down recent statement balance by a given fraction (e.g. 50%).
    """
    base_df = validate_applicant_input(applicant)
    recent_bill = max(0.0, float(base_df.iloc[0].get("BILL_AMT1", 0.0)))
    paydown_amt = recent_bill * float(np.clip(paydown_fraction, 0.0, 1.0))
    new_bill = max(0.0, recent_bill - paydown_amt)
    new_pay = max(0.0, float(base_df.iloc[0].get("PAY_AMT1", 0.0)) + paydown_amt)

    return simulate_scenario(
        applicant,
        modifications={"BILL_AMT1": new_bill, "PAY_AMT1": new_pay},
        pipeline_path=pipeline_path
    )


def simulate_credit_limit_increase(
    applicant: Union[Dict[str, Any], pd.Series, pd.DataFrame],
    new_limit: float,
    pipeline_path: str = "models/credit_pipeline.pkl"
) -> Dict[str, Any]:
    """
    Preset Scenario: Adjust revolving credit limit line.
    """
    return simulate_scenario(
        applicant,
        modifications={"LIMIT_BAL": new_limit},
        pipeline_path=pipeline_path
    )


if __name__ == "__main__":
    from data_loader import load_credit_data
    df, _ = load_credit_data("data/credit_data.csv")

    print("==================================================")
    print("WHAT-IF SCENARIO: Remediate Delinquency on Sample 0")
    print("==================================================")
    sample_delinq = df.iloc[0].to_dict()

    sim_res = simulate_repayment_remediation(sample_delinq)
    print(f"Current Probability: {sim_res['current']['default_probability']:.4f} ({sim_res['current']['risk_level']}) | FHI: {sim_res['current']['financial_health']['score']}")
    print(f"Scenario Probability: {sim_res['scenario']['default_probability']:.4f} ({sim_res['scenario']['risk_level']}) | FHI: {sim_res['scenario']['financial_health']['score']}")
    print(f"Delta Probability: {sim_res['comparison']['probability_change_pct_points']:+.2f}% points")
    print(f"Delta FHI: {sim_res['comparison']['financial_health_delta']:+d} points")
    print(f"Summary: {sim_res['comparison']['summary']}")
    print(f"Resolved Risk Factors: {[f['human_label'] for f in sim_res['comparison']['risk_factors_resolved']]}")
    print(f"Gained Positive Factors: {[f['human_label'] for f in sim_res['comparison']['positive_factors_gained']]}")
