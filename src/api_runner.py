"""
Credit Scoring Model — CLI & JSON API Bridge
============================================
Provides command-line and JSON interface to production ML, explainability,
Financial Health, and Scenario Simulation modules.
"""

import json
import os
import sys
from typing import Any, Dict

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from data_loader import load_credit_data
from financial_health import calculate_financial_health
from i18n import TRANSLATIONS, get_supported_languages, t
from predict import predict_credit_risk
from risk_reasons import explain_prediction
from scenario_simulator import (
    simulate_balance_paydown,
    simulate_credit_limit_increase,
    simulate_repayment_remediation,
    simulate_scenario,
)
from fairness import generate_full_fairness_report, audit_attribute_fairness


def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Route and dispatch JSON API requests."""
    action = request.get("action", "predict")
    payload = request.get("payload", {})

    if action == "predict":
        applicant = payload.get("applicant", {})
        return predict_credit_risk(applicant)

    elif action == "assess_full":
        applicant = payload.get("applicant", {})
        pred = predict_credit_risk(applicant)
        fhi = calculate_financial_health(applicant)
        expl = explain_prediction(applicant, prediction_result=pred)
        return {
            "prediction": pred,
            "explanation": expl,
            "financial_health": fhi,
        }

    elif action == "explain":
        applicant = payload.get("applicant", {})
        pred = payload.get("prediction")
        return explain_prediction(applicant, prediction_result=pred)

    elif action == "financial_health":
        applicant = payload.get("applicant", {})
        return calculate_financial_health(applicant)

    elif action == "simulate":
        applicant = payload.get("applicant", {})
        mods = payload.get("modifications", {})
        return simulate_scenario(applicant, modifications=mods)

    elif action == "simulate_remediation":
        applicant = payload.get("applicant", {})
        return simulate_repayment_remediation(applicant)

    elif action == "simulate_paydown":
        applicant = payload.get("applicant", {})
        fraction = float(payload.get("fraction", 0.50))
        return simulate_balance_paydown(applicant, paydown_fraction=fraction)

    elif action == "simulate_limit_increase":
        applicant = payload.get("applicant", {})
        new_limit = float(payload.get("new_limit", applicant.get("LIMIT_BAL", 50000.0) * 1.5))
        return simulate_credit_limit_increase(applicant, new_limit=new_limit)

    elif action == "get_fairness_report":
        attribute = payload.get("attribute") if isinstance(payload, dict) else None
        from fairness import audit_attribute_fairness, generate_full_fairness_report
        from data_loader import load_credit_data
        from evaluate_model import load_production_pipeline
        
        df, _ = load_credit_data("data/credit_data.csv")
        try:
            pipeline = load_production_pipeline("models/credit_pipeline.pkl")
            df_eval = df.copy()
            df_eval["prediction"] = pipeline.predict(df)
            df_eval["default_probability"] = pipeline.predict_proba(df)[:, 1]
        except Exception as e:
            df_eval = df.copy()
            df_eval["prediction"] = df_eval["default_payment_next_month"]
            df_eval["default_probability"] = df_eval["default_payment_next_month"].astype(float)
        
        if attribute:
            return audit_attribute_fairness(df_eval, attribute_col=attribute)
        return generate_full_fairness_report(df_eval)

    elif action == "get_translations":
        return {
            "translations": TRANSLATIONS,
            "supported_languages": get_supported_languages(),
        }

    else:
        raise ValueError(f"Unknown API action: '{action}'")


def sanitize_for_json(obj: Any) -> Any:
    """Recursively convert numpy types and non-serializable objects to pure Python primitives."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    elif hasattr(obj, "item") and callable(getattr(obj, "item")):
        return obj.item()
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    return str(obj)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI execution with JSON string argument
        try:
            req_data = json.loads(sys.argv[1])
            res_data = handle_request(req_data)
            clean_res = sanitize_for_json(res_data)
            print(json.dumps({"status": "success", "data": clean_res}))
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}))
    else:
        # Read from stdin
        try:
            input_text = sys.stdin.read()
            if input_text:
                req_data = json.loads(input_text)
                res_data = handle_request(req_data)
                clean_res = sanitize_for_json(res_data)
                print(json.dumps({"status": "success", "data": clean_res}))
            else:
                print(json.dumps({"status": "error", "message": "No input provided"}))
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}))
