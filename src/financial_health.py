"""
Credit Scoring Model — Financial Health Indicator Engine
=========================================================
Human-Centered Machine Learning for Credit Risk Analysis.
Provides a transparent, deterministic, and explainable Financial Health Indicator
derived strictly from empirical credit bureau variables available in the UCI dataset.

Important Boundaries:
1. This is NOT an official credit score (FICO, VantageScore, Experian, TransUnion, Equifax).
2. This is NOT a bank underwriting score or a loan approval determination.
3. Named strictly: "Financial Health Indicator".
4. Calculations are 100% deterministic, rule-based, and zero-division safe.
5. Strictly avoids Generative AI, LLMs, or fabricated scores.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from feature_engineering import CreditFeatureEngineer
from predict import LEGAL_DISCLAIMER, PRIVACY_STATEMENT, validate_applicant_input

# -----------------------------------------------------------------------------
# METHODOLOGY & FACTOR WEIGHT SPECIFICATION
# -----------------------------------------------------------------------------
# Total Indicator Score ranges from 0 to 100.
# Weighted across 5 fundamental domain pillars present in the credit dataset:
# 1. Payment Timeliness & Delinquency History  (35% weight)
# 2. Revolving Credit Utilization             (25% weight)
# 3. Repayment Adequacy (Payment-to-Bill)     (20% weight)
# 4. Debt & Net Deficit Burden                (15% weight)
# 5. Account Trajectory & Trend Momentum      ( 5% weight)
# Sum of weights = 100% (1.00)
# -----------------------------------------------------------------------------

COMPONENT_WEIGHTS = {
    "payment_timeliness": 0.35,
    "credit_utilization": 0.25,
    "repayment_adequacy": 0.20,
    "debt_burden": 0.15,
    "account_trajectory": 0.05,
}

FINANCIAL_HEALTH_DISCLAIMER = (
    "The Financial Health Indicator is an educational heuristic score (0–100) calculated "
    "deterministically from credit utilization, payment history, repayment adequacy, and debt burden. "
    "It is NOT a FICO score, VantageScore, credit bureau score, or loan approval decision."
)


def _compute_utilization_component(recent_util: float, avg_util: float, max_util: float) -> Dict[str, Any]:
    """
    Evaluate revolving credit utilization (Weight: 25%).

    Optimal utilization is below 30%. Ratios above 80% indicate severe liquidity strain.
    Safe with zero limits and negative bills.
    """
    # Utilization metrics are bounded in [0.0, 5.0] by feature engineer
    u_rec = float(np.clip(recent_util, 0.0, 5.0))
    u_avg = float(np.clip(avg_util, 0.0, 5.0))

    # Continuous piece-wise scoring based on financial benchmarks
    # Effective composite utilization (60% recent, 40% 6-month average)
    composite_u = 0.60 * u_rec + 0.40 * u_avg

    if composite_u <= 0.10:
        score = 100.0
        status = "Optimal"
        explanation = f"Minimal credit utilization ({composite_u * 100:.1f}%), leaving substantial borrowing capacity."
    elif composite_u <= 0.30:
        # 10% to 30% utilization: 100 down to 85
        score = 100.0 - ((composite_u - 0.10) / 0.20) * 15.0
        status = "Good"
        explanation = f"Disciplined credit utilization ({composite_u * 100:.1f}%), well within healthy thresholds (<30%)."
    elif composite_u <= 0.60:
        # 30% to 60% utilization: 85 down to 55
        score = 85.0 - ((composite_u - 0.30) / 0.30) * 30.0
        status = "Moderate"
        explanation = f"Moderate revolving balance ({composite_u * 100:.1f}%). Reducing balances below 30% would strengthen your profile."
    elif composite_u <= 0.90:
        # 60% to 90% utilization: 55 down to 20
        score = 55.0 - ((composite_u - 0.60) / 0.30) * 35.0
        status = "High"
        explanation = f"High credit utilization ({composite_u * 100:.1f}%), indicating heavy reliance on revolving credit."
    else:
        # > 90% utilization: 20 down to 0
        score = max(0.0, 20.0 - ((composite_u - 0.90) / 0.50) * 20.0)
        status = "Critical"
        explanation = f"Near-maximum or over-limit credit utilization ({composite_u * 100:.1f}%), signaling acute balance stress."

    return {
        "name": "Revolving Credit Utilization",
        "score": round(score, 1),
        "weight": COMPONENT_WEIGHTS["credit_utilization"],
        "status": status,
        "actual_value_display": f"{composite_u * 100:.1f}%",
        "recent_utilization_pct": round(u_rec * 100, 1),
        "avg_utilization_pct": round(u_avg * 100, 1),
        "explanation": explanation,
    }


def _compute_timeliness_component(
    pay_0: float,
    max_delinq: float,
    num_delinq: float,
    avg_delay: float
) -> Dict[str, Any]:
    """
    Evaluate payment timeliness and delinquency history (Weight: 35%).

    On-time payments (<= 0) receive maximum points. Delays reduce points by delay duration.
    """
    p0 = float(pay_0) if not np.isnan(pay_0) else 0.0
    max_d = float(max_delinq) if not np.isnan(max_delinq) else 0.0
    num_d = int(num_delinq) if not np.isnan(num_delinq) else 0
    avg_d = float(avg_delay) if not np.isnan(avg_delay) else 0.0

    # Clean profile: All on-time (status <= 0)
    if max_d <= 0 and p0 <= 0:
        score = 100.0
        status = "Pristine"
        explanation = "Flawless payment history with zero delinquent cycles across all 6 observed months."
    elif max_d <= 1 and num_d <= 1 and p0 <= 0:
        # Isolated 1-month delay in the past, currently recovered on-time
        score = 75.0
        status = "Good (Recovered)"
        explanation = "Past 1-month payment delay is fully resolved, with recent billing cycles paid on time."
    elif p0 == 1 and num_d <= 1:
        # Recent 1-month delay
        score = 60.0
        status = "Minor Delay"
        explanation = "Recent 1-month payment delay observed. Bringing the account current will immediately improve this score."
    elif p0 <= 0 and max_d >= 2:
        # Past multi-month delinquency, but currently on time
        score = max(35.0, 65.0 - (max_d * 8.0) - (num_d * 5.0))
        status = "Recovered Delinquency"
        explanation = f"History of {int(max_d)}-month peak payment delay, though the most recent cycle is current."
    else:
        # Active multi-month delinquency (p0 >= 2 or active multi-cycle delay)
        penalty = (p0 * 20.0) + (max_d * 10.0) + (num_d * 8.0)
        score = max(0.0, 100.0 - penalty)
        status = "Delinquent"
        explanation = f"Active payment delinquency ({int(p0)} month(s) overdue recently; peak {int(max_d)} months delay across {num_d} billing cycles)."

    return {
        "name": "Payment Timeliness & History",
        "score": round(score, 1),
        "weight": COMPONENT_WEIGHTS["payment_timeliness"],
        "status": status,
        "actual_value_display": "On-Time" if max_d <= 0 else f"{int(max_d)} Mo. Max Delay",
        "recent_status_code": int(p0),
        "delinquent_months_count": num_d,
        "explanation": explanation,
    }


def _compute_adequacy_component(pay_to_bill_1: float, pay_to_bill_avg: float) -> Dict[str, Any]:
    """
    Evaluate repayment adequacy (payment-to-bill ratio) (Weight: 20%).

    Ratios >= 1.0 indicate full statement payoff. Ratios < 0.1 indicate minimums only.
    """
    pb1 = float(np.clip(pay_to_bill_1, 0.0, 2.0))
    pb_avg = float(np.clip(pay_to_bill_avg, 0.0, 2.0))

    # Blend 60% recent payment adequacy, 40% average adequacy
    composite_pb = 0.60 * pb1 + 0.40 * pb_avg

    if composite_pb >= 1.0:
        score = 100.0
        status = "Full Payoff"
        explanation = "Full balance repayment demonstrated, avoiding accumulating revolving interest charges."
    elif composite_pb >= 0.50:
        score = 80.0 + ((composite_pb - 0.50) / 0.50) * 19.0
        status = "Substantial Payment"
        explanation = f"Substantial repayment coverage ({composite_pb * 100:.1f}% of billed balances), paying down principal."
    elif composite_pb >= 0.20:
        score = 45.0 + ((composite_pb - 0.20) / 0.30) * 35.0
        status = "Moderate Payment"
        explanation = f"Moderate payment coverage ({composite_pb * 100:.1f}%). Paying more than minimums helps avoid debt escalation."
    elif composite_pb > 0.0:
        score = 15.0 + (composite_pb / 0.20) * 30.0
        status = "Minimum / Low Payment"
        explanation = f"Low payment-to-bill coverage ({composite_pb * 100:.1f}%), indicating reliance on minimum allowable payments."
    else:
        score = 0.0
        status = "Zero Repayment"
        explanation = "Zero cash repayment recorded against previous billed balance."

    return {
        "name": "Repayment Adequacy (Payment-to-Bill)",
        "score": round(score, 1),
        "weight": COMPONENT_WEIGHTS["repayment_adequacy"],
        "status": status,
        "actual_value_display": f"{composite_pb * 100:.1f}%",
        "recent_payment_ratio": round(pb1, 3),
        "avg_payment_ratio": round(pb_avg, 3),
        "explanation": explanation,
    }


def _compute_debt_burden_component(deficit_to_limit: float, net_deficit: float, limit_bal: float) -> Dict[str, Any]:
    """
    Evaluate accumulated net unpaid debt burden relative to credit limit (Weight: 15%).

    Negative deficit (payments >= bills) receives top score. Expanding debt reduces score.
    """
    dl = float(np.clip(deficit_to_limit, -5.0, 10.0))
    limit = max(float(limit_bal), 1.0)
    deficit = float(net_deficit)

    if dl <= 0.0:
        score = 100.0
        status = "Surplus / Balanced"
        explanation = f"Net debt position is fully managed (Total repayments match or exceed statements by NT${abs(deficit):,.0f})."
    elif dl <= 0.30:
        score = 100.0 - (dl / 0.30) * 20.0
        status = "Low Deficit"
        explanation = f"Manageable accumulated deficit (NT${deficit:,.0f}, {dl * 100:.1f}% of credit line)."
    elif dl <= 0.70:
        score = 80.0 - ((dl - 0.30) / 0.40) * 35.0
        status = "Moderate Deficit"
        explanation = f"Moderate cumulative unpaid debt (NT${deficit:,.0f}, {dl * 100:.1f}% of credit line)."
    elif dl <= 1.20:
        score = 45.0 - ((dl - 0.70) / 0.50) * 30.0
        status = "High Deficit"
        explanation = f"Substantial accumulated unpaid balance (NT${deficit:,.0f}, {dl * 100:.1f}% of total credit line)."
    else:
        score = max(0.0, 15.0 - ((dl - 1.20) / 1.0) * 15.0)
        status = "Critical Burden"
        explanation = f"Cumulative unpaid deficit (NT${deficit:,.0f}) exceeds total approved credit limit ({dl * 100:.1f}% of limit)."

    return {
        "name": "Debt & Deficit Burden",
        "score": round(score, 1),
        "weight": COMPONENT_WEIGHTS["debt_burden"],
        "status": status,
        "actual_value_display": f"{dl * 100:.1f}% of limit",
        "net_deficit_amount": round(deficit, 2),
        "deficit_to_limit_ratio": round(dl, 3),
        "explanation": explanation,
    }


def _compute_trajectory_component(delinq_trend: float, bill_growth: float) -> Dict[str, Any]:
    """
    Evaluate 6-month account trajectory & momentum (Weight: 5%).

    Improving timeliness and shrinking balances score highest; deteriorating trends score lower.
    """
    dt = float(delinq_trend) if not np.isnan(delinq_trend) else 0.0
    bg = float(bill_growth) if not np.isnan(bill_growth) else 0.0

    score = 70.0  # Neutral baseline

    # Delinquency trend: Recent status minus Month 6 status
    if dt < 0:
        # Negative means recent delay is smaller than historical (recovering)
        score += 20.0
        trend_desc = "Repayment timeliness is improving compared to earlier months."
    elif dt > 0:
        # Positive means recent delay is worse than historical
        score -= min(40.0, dt * 15.0)
        trend_desc = "Repayment timeliness has recently deteriorated."
    else:
        trend_desc = "Repayment timeliness has remained steady over 6 months."

    # Bill growth trend
    if bg < -0.10:
        score += 10.0
    elif bg > 0.30:
        score -= 15.0

    score = float(np.clip(score, 0.0, 100.0))

    if score >= 80.0:
        status = "Improving"
    elif score >= 55.0:
        status = "Stable"
    else:
        status = "Deteriorating"

    return {
        "name": "Account Trajectory & Momentum",
        "score": round(score, 1),
        "weight": COMPONENT_WEIGHTS["account_trajectory"],
        "status": status,
        "actual_value_display": status,
        "delinquency_trend_code": int(dt),
        "explanation": trend_desc,
    }


def determine_health_label(score: float) -> str:
    """
    Map continuous 0-100 Financial Health score to descriptive tier label.

    Bands:
    - 80 to 100: EXCELLENT
    - 65 to 79 : GOOD
    - 50 to 64 : FAIR
    - 0  to 49 : POOR / AT RISK
    """
    if score >= 80.0:
        return "EXCELLENT"
    elif score >= 65.0:
        return "GOOD"
    elif score >= 50.0:
        return "FAIR"
    else:
        return "POOR / AT RISK"


def calculate_financial_health(
    input_data: Union[Dict[str, Any], pd.Series, pd.DataFrame]
) -> Dict[str, Any]:
    """
    Calculate the transparent Financial Health Indicator for an applicant.

    Args:
        input_data: Raw applicant data (dict, Series, or DataFrame).

    Returns:
        Dict[str, Any]: Structured Financial Health output including score, tier label,
                        component breakdowns, narrative summary, and disclaimers.
    """
    # 1. Standardize and validate input
    validated_df = validate_applicant_input(input_data)

    # 2. Extract engineered domain indicators using single source of truth
    engineer = CreditFeatureEngineer()
    feat_df = engineer.transform(validated_df)
    row = feat_df.iloc[0]

    # 3. Calculate individual domain components safely
    util_comp = _compute_utilization_component(
        recent_util=row.get("UTILIZATION_RECENT", 0.0),
        avg_util=row.get("UTILIZATION_AVG", 0.0),
        max_util=row.get("UTILIZATION_MAX", 0.0),
    )

    time_comp = _compute_timeliness_component(
        pay_0=row.get("PAY_0", 0.0),
        max_delinq=row.get("MAX_DELINQUENCY", 0.0),
        num_delinq=row.get("NUM_DELINQUENT_MONTHS", 0.0),
        avg_delay=row.get("AVG_DELAY_MONTHS", 0.0),
    )

    adeq_comp = _compute_adequacy_component(
        pay_to_bill_1=row.get("PAY_TO_BILL_1", 1.0),
        pay_to_bill_avg=row.get("PAY_TO_BILL_AVG", 1.0),
    )

    debt_comp = _compute_debt_burden_component(
        deficit_to_limit=row.get("DEFICIT_TO_LIMIT", 0.0),
        net_deficit=row.get("NET_DEFICIT", 0.0),
        limit_bal=row.get("LIMIT_BAL", 1.0),
    )

    traj_comp = _compute_trajectory_component(
        delinq_trend=row.get("DELINQUENCY_TREND", 0.0),
        bill_growth=row.get("BILL_GROWTH_TREND", 0.0),
    )

    # 4. Compute weighted final score: sum(score_i * weight_i)
    raw_score = (
        util_comp["score"] * util_comp["weight"]
        + time_comp["score"] * time_comp["weight"]
        + adeq_comp["score"] * adeq_comp["weight"]
        + debt_comp["score"] * debt_comp["weight"]
        + traj_comp["score"] * traj_comp["weight"]
    )

    # Strictly bound between 0 and 100, ensure float/int safety
    final_score = int(round(np.clip(raw_score, 0.0, 100.0)))
    health_label = determine_health_label(final_score)

    # 5. Build structured narrative summary
    components = {
        "credit_utilization": util_comp,
        "payment_timeliness": time_comp,
        "repayment_adequacy": adeq_comp,
        "debt_burden": debt_comp,
        "account_trajectory": traj_comp,
    }

    # Find highest and lowest component
    sorted_comps = sorted(components.values(), key=lambda c: c["score"])
    weakest = sorted_comps[0]
    strongest = sorted_comps[-1]

    if final_score >= 80:
        summary = (
            f"Your Financial Health Indicator is {final_score}/100 ({health_label}). "
            f"Your strongest pillar is {strongest['name'].lower()} ({strongest['score']:.0f}/100). "
            f"Maintaining current repayment habits will keep your profile robust."
        )
    elif final_score >= 65:
        summary = (
            f"Your Financial Health Indicator is {final_score}/100 ({health_label}). "
            f"While {strongest['name'].lower()} is solid ({strongest['score']:.0f}/100), "
            f"improving {weakest['name'].lower()} ({weakest['score']:.0f}/100) will yield the biggest score gain."
        )
    elif final_score >= 50:
        summary = (
            f"Your Financial Health Indicator is {final_score}/100 ({health_label}). "
            f"Primary drag on your indicator is {weakest['name'].lower()} ({weakest['score']:.0f}/100). "
            f"Focusing on {weakest['explanation'].lower()} is recommended."
        )
    else:
        summary = (
            f"Your Financial Health Indicator is {final_score}/100 ({health_label}). "
            f"Significant pressure detected across {weakest['name'].lower()} ({weakest['score']:.0f}/100) "
            f"and payment timeliness. Bringing overdue balances current is essential."
        )

    return {
        "score": final_score,
        "label": health_label,
        "components": components,
        "summary": summary,
        "methodology": {
            "name": "Financial Health Indicator (FHI-5)",
            "score_scale": "0 to 100",
            "weights": COMPONENT_WEIGHTS,
            "tiers": {
                "EXCELLENT": "80–100",
                "GOOD": "65–79",
                "FAIR": "50–64",
                "POOR / AT RISK": "0–49",
            },
            "factors_used": [
                "Revolving Credit Utilization (BILL_AMT1, 6-mo avg vs LIMIT_BAL)",
                "Payment Timeliness & Delinquency (PAY_0..PAY_6, MAX_DELINQUENCY)",
                "Repayment Adequacy (PAY_AMT1..3 vs previous statement balances)",
                "Net Unpaid Cash Deficit & Debt Burden (Cumulative bills vs repayments)",
                "6-Month Trajectory & Trend Momentum (Recent vs historical repayment direction)",
            ],
            "notice": FINANCIAL_HEALTH_DISCLAIMER,
        },
        "disclaimer": LEGAL_DISCLAIMER,
        "privacy_statement": PRIVACY_STATEMENT,
    }


if __name__ == "__main__":
    from data_loader import load_credit_data
    df, _ = load_credit_data("data/credit_data.csv")

    print("=== SAMPLE 1: Clean Applicant (Index 2) ===")
    sample_clean = df.iloc[2].to_dict()
    fhi_clean = calculate_financial_health(sample_clean)
    print(f"Score: {fhi_clean['score']} ({fhi_clean['label']})")
    print(f"Summary: {fhi_clean['summary']}")
    for k, v in fhi_clean["components"].items():
        print(f"  - {v['name']}: {v['score']}/100 (Weight {int(v['weight']*100)}%) [{v['status']}] -> {v['explanation']}")

    print("\n=== SAMPLE 2: Delinquent Applicant (Index 0) ===")
    sample_delinq = df.iloc[0].to_dict()
    fhi_delinq = calculate_financial_health(sample_delinq)
    print(f"Score: {fhi_delinq['score']} ({fhi_delinq['label']})")
    print(f"Summary: {fhi_delinq['summary']}")
    for k, v in fhi_delinq["components"].items():
        print(f"  - {v['name']}: {v['score']}/100 (Weight {int(v['weight']*100)}%) [{v['status']}] -> {v['explanation']}")
