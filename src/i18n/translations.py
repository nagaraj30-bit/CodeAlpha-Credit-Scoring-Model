"""
Credit Scoring Model — Internationalization (i18n) Package
===========================================================
Centralized deterministic translation dictionaries for English (en), Tamil (ta), and Hindi (hi).
Provides zero-external-API, offline-capable localizations across all user-facing features,
disclaimers, form fields, risk tiers, financial health pillars, and scenario simulators.
"""

from typing import Any, Dict

# Supported language codes and their native display names
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳"},
}

DEFAULT_LANGUAGE = "en"

# Comprehensive translations dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App Meta & Header
        "app_title": "Credit Intelligence & Risk Engine",
        "app_subtitle": "Human-Centered Machine Learning for Credit Assessment & Financial Health",
        "app_badge": "Production ML Pipeline",
        "nav_overview": "Overview",
        "nav_assess": "Assess Credit Risk",
        "nav_result": "Assessment Result",
        "nav_explain": "Why This Result?",
        "nav_financial_health": "Financial Health (FHI-5)",
        "nav_simulator": "What-If Simulator",
        "nav_fairness": "Fairness & Bias Audit",
        "nav_insights": "Model Insights & Methodology",

        # Common Actions & Buttons
        "btn_assess_risk": "Assess Credit Risk",
        "btn_run_assessment": "Calculate Credit Risk",
        "btn_explore_what_if": "Explore What-If Scenarios",
        "btn_simulate_scenario": "Run Simulation",
        "btn_reset_scenario": "Reset to Baseline",
        "btn_load_sample": "Load Sample Profile",
        "btn_clear": "Clear Form",
        "btn_view_details": "View Full Details",
        "btn_copy_summary": "Copy Summary",
        "btn_switch_language": "Change Language",

        # Overview / Landing Page
        "overview_hero_title": "Explainable Credit Risk & Financial Health Intelligence",
        "overview_hero_desc": "Evaluate credit card default risk using a transparent, machine-learning production pipeline trained on 30,000 empirical credit bureau records. Explore deterministic root causes, calculate your 5-pillar Financial Health Indicator, and test hypothetical behavioral improvements with our What-If Simulator.",
        "overview_card1_title": "Deterministic Machine Learning",
        "overview_card1_desc": "Scored via an audited Random Forest classifier (ROC-AUC 0.7744) evaluating 39 behavioral and financial features without generative AI hallucinations.",
        "overview_card2_title": "Transparent Explainability",
        "overview_card2_desc": "Bidirectional factor attribution highlighting specific risk drivers alongside positive financial mitigators grounded in your actual payment history.",
        "overview_card3_title": "Financial Health Indicator (FHI-5)",
        "overview_card3_desc": "A 0–100 deterministic scoring engine assessing Payment Timeliness, Credit Utilization, Repayment Adequacy, Debt Burden, and Trajectory.",
        "overview_card4_title": "What-If Scenario Simulation",
        "overview_card4_desc": "Simulate real-world behavioral changes (paying down balances, remediating overdue months) through the exact production pipeline with instant delta tracking.",
        "overview_quick_start": "Quick Start Options",
        "overview_sample_prime": "Sample Profile: Prime / Low Risk",
        "overview_sample_revolving": "Sample Profile: High Revolving / Medium Risk",
        "overview_sample_delinquent": "Sample Profile: Delinquent / High Risk",

        # Risk Assessment Form
        "form_title": "Applicant Credit Profile Input",
        "form_desc": "Enter credit bureau attributes to evaluate credit risk. All data is processed locally without collecting any personal identification information.",
        "form_sec_credit_profile": "Credit Facility & Demographics",
        "form_sec_repayment": "Repayment Timeliness History (Past 6 Months)",
        "form_sec_bills": "Statement Billed Amounts (NT$)",
        "form_sec_payments": "Actual Paid Amounts (NT$)",

        # Feature Labels & Helpers
        "lbl_limit_bal": "Approved Credit Limit (NT$)",
        "help_limit_bal": "Total credit limit granted on the credit card (e.g. 50,000 to 500,000 NT$).",
        "lbl_sex": "Gender Category",
        "lbl_sex_male": "Male",
        "lbl_sex_female": "Female",
        "lbl_education": "Education Level",
        "lbl_edu_grad": "Graduate School",
        "lbl_edu_uni": "University",
        "lbl_edu_high": "High School",
        "lbl_edu_other": "Other",
        "lbl_marriage": "Marital Status",
        "lbl_marr_married": "Married",
        "lbl_marr_single": "Single",
        "lbl_marr_other": "Other",
        "lbl_age": "Age (Years)",
        "help_age": "Applicant age in years (21–79).",

        "lbl_pay_0": "September Repayment Status (Most Recent)",
        "lbl_pay_2": "August Repayment Status (1 Month Prior)",
        "lbl_pay_3": "July Repayment Status (2 Months Prior)",
        "lbl_pay_4": "June Repayment Status (3 Months Prior)",
        "lbl_pay_5": "May Repayment Status (4 Months Prior)",
        "lbl_pay_6": "April Repayment Status (5 Months Prior)",
        "opt_pay_neg2": "No consumption / inactive balance (-2)",
        "opt_pay_neg1": "Paid in full on-time (-1)",
        "opt_pay_0": "Revolving credit used on-time (0)",
        "opt_pay_1": "Payment delay: 1 month (1)",
        "opt_pay_2": "Payment delay: 2 months (2)",
        "opt_pay_3": "Payment delay: 3 months (3)",
        "opt_pay_4": "Payment delay: 4 months (4)",
        "opt_pay_5": "Payment delay: 5 months (5)",
        "opt_pay_6": "Payment delay: 6 months (6)",
        "opt_pay_7": "Payment delay: 7 months (7)",
        "opt_pay_8": "Payment delay: 8+ months (8)",

        "lbl_bill_amt1": "Sept Statement Bill (NT$)",
        "lbl_bill_amt2": "Aug Statement Bill (NT$)",
        "lbl_bill_amt3": "July Statement Bill (NT$)",
        "lbl_bill_amt4": "June Statement Bill (NT$)",
        "lbl_bill_amt5": "May Statement Bill (NT$)",
        "lbl_bill_amt6": "April Statement Bill (NT$)",

        "lbl_pay_amt1": "Sept Paid Amount (NT$)",
        "lbl_pay_amt2": "Aug Paid Amount (NT$)",
        "lbl_pay_amt3": "July Paid Amount (NT$)",
        "lbl_pay_amt4": "June Paid Amount (NT$)",
        "lbl_pay_amt5": "May Paid Amount (NT$)",
        "lbl_pay_amt6": "April Paid Amount (NT$)",

        # Result Screen
        "result_header": "Credit Risk Assessment Result",
        "result_risk_level": "Assessed Risk Tier",
        "result_likelihood": "Estimated Default Likelihood",
        "result_non_default_likelihood": "Non-Default Likelihood",
        "result_binary_decision": "Model Binary Classification",
        "result_summary": "Assessment Executive Summary",
        "risk_tier_low": "LOW RISK",
        "risk_tier_medium": "MEDIUM RISK",
        "risk_tier_high": "HIGH RISK",
        "pred_class_0": "Non-Default (Favorable)",
        "pred_class_1": "Default (Elevated Risk)",

        # Explainability Screen
        "explain_header": "Deterministic Risk Factors & Strengths",
        "explain_subtitle": "Derived from Random Forest feature importances, repayment timeliness history, and balance utilization.",
        "explain_risk_factors_title": "Primary Risk Drivers (Areas of Concern)",
        "explain_positive_factors_title": "Credit Strengths & Positive Mitigators",
        "explain_no_risk_factors": "No significant negative risk factors identified. The account exhibits disciplined credit behavior.",
        "explain_no_positive_factors": "No major positive factors identified. Consider improving repayment timeliness and lowering revolving balances.",
        "explain_col_factor": "Financial Factor",
        "explain_col_value": "Current Value",
        "explain_col_impact": "Model Impact",
        "explain_col_explanation": "Contextual Explanation",

        # Financial Health Indicator (FHI-5)
        "fhi_header": "Financial Health Indicator (FHI-5)",
        "fhi_subtitle": "Deterministic 0–100 heuristic index assessing 5 foundational credit management pillars.",
        "fhi_score_title": "Overall Financial Health Score",
        "fhi_tier_excellent": "EXCELLENT",
        "fhi_tier_good": "GOOD",
        "fhi_tier_fair": "FAIR",
        "fhi_tier_poor": "POOR / AT RISK",
        "fhi_pillar_1": "Payment Timeliness & History",
        "fhi_pillar_1_weight": "35% Weight",
        "fhi_pillar_2": "Revolving Credit Utilization",
        "fhi_pillar_2_weight": "25% Weight",
        "fhi_pillar_3": "Repayment Adequacy",
        "fhi_pillar_3_weight": "20% Weight",
        "fhi_pillar_4": "Debt & Net Deficit Burden",
        "fhi_pillar_4_weight": "15% Weight",
        "fhi_pillar_5": "Account Trajectory & Momentum",
        "fhi_pillar_5_weight": "5% Weight",

        # What-If Simulator
        "sim_header": "What-If Scenario Simulator",
        "sim_subtitle": "Simulate behavioral changes and evaluate the exact production model's response in real time.",
        "sim_panel_controls": "1. Scenario Adjustment Controls",
        "sim_panel_result": "2. Simulated Model Response",
        "sim_panel_comparison": "3. Before vs After Comparison",
        "sim_presets_title": "One-Click Scenario Presets",
        "sim_preset_remediate": "Remediate Recent Overdue Delinquencies",
        "sim_preset_paydown_50": "Pay Down Statement Balances by 50%",
        "sim_preset_paydown_80": "Substantial Balance Paydown (80%)",
        "sim_preset_limit_inc": "Increase Approved Credit Line (+50%)",
        "sim_lbl_current_baseline": "Current Baseline",
        "sim_lbl_simulated_scenario": "Simulated Scenario",
        "sim_lbl_prob_delta": "Default Likelihood Delta",
        "sim_lbl_fhi_delta": "Financial Health Delta",
        "sim_direction_improved": "IMPROVED",
        "sim_direction_worsened": "WORSENED",
        "sim_direction_unchanged": "UNCHANGED",
        "sim_resolved_factors_title": "Resolved Risk Factors",
        "sim_gained_strengths_title": "Gained Positive Strengths",
        "sim_table_col_factor": "Financial Metric",
        "sim_table_col_current": "Current Value",
        "sim_table_col_scenario": "Scenario Value",
        "sim_table_col_change": "Net Change",

        # Model Insights & Methodology
        "insights_header": "Model Insights, Governance & Fair Lending",
        "insights_champion_title": "Production Champion Architecture",
        "insights_champion_desc": "Trained Random Forest Classifier (150 trees, max_depth=12) with zero-leakage scikit-learn Pipeline.",
        "insights_metrics_title": "Audited Test Set Benchmarks",
        "insights_metric_auc": "ROC-AUC Score: 0.7744 (Benchmark > 0.75 met)",
        "insights_metric_acc": "Accuracy: 82.02% (Benchmark > 80% met)",
        "insights_metric_brier": "Brier Score: 0.1299 (Well-calibrated probability distributions)",
        "insights_metric_f1": "Default F1-Score: 0.4812",
        "insights_feature_imp_title": "Global Feature Importances (Gini Index)",
        "insights_disclaimer_title": "Model Disclaimers & Governance Notice",

        # Fairness & Bias Audit
        "fairness_title": "Fairness & Demographic Bias Audit",
        "fairness_subtitle": "Empirical group-level performance metrics, disparity evaluation, and transparent documentation of dataset constraints.",
        "fairness_tab_overview": "Dataset & Feature Audit",
        "fairness_tab_metrics": "Group Metrics & Disparities",
        "fairness_tab_limitations": "Principles & Limitations",
        "fairness_dataset_total": "Total Evaluated Records",
        "fairness_available_demographics": "Available Demographic Variables in Dataset",
        "fairness_unavailable_demographics": "Unavailable Sensitive Attributes (Data Gaps)",
        "fairness_removed_variables": "Excluded Non-Predictive Features",
        "fairness_retained_variables": "Retained Feature Pipeline",
        "fairness_select_attribute": "Select Demographic Attribute to Audit:",
        "fairness_reference_group": "Baseline / Reference Group:",
        "fairness_metric_base_rate": "Base Default Rate (Actual)",
        "fairness_metric_ppr": "Selection Rate / Predicted Default (PPR)",
        "fairness_metric_recall": "True Positive Rate / Recall (TPR)",
        "fairness_metric_fpr": "False Positive Rate (FPR)",
        "fairness_metric_fnr": "False Negative Rate (FNR)",
        "fairness_metric_precision": "Precision (PPV)",
        "fairness_metric_accuracy": "Accuracy",
        "fairness_small_sample_warning": "Warning: Small cohort sample size (<300). Metrics subject to higher statistical variance.",
        "fairness_disparity_diff": "Difference vs Baseline (Δ)",
        "fairness_disparity_ratio": "Ratio vs Baseline (Group / Ref)",
        "fairness_principle_1": "No Claim of Absolute Fairness: We explicitly do NOT claim this model is 'unbiased' or 'fair'. Algorithmic fairness involves inherent statistical trade-offs.",
        "fairness_principle_2": "Fairness Through Blindness Fallacy: Removing demographic fields from training does not guarantee equitable outcomes due to strong correlated financial proxies.",
        "fairness_principle_3": "Sample Size Discipline: Small sub-cohorts are highlighted with statistical uncertainty flags rather than assumed to have stable disparities.",

        # Disclaimers & Trust Statements
        "disclaimer_legal": (
            "This application is an educational machine-learning risk assessment demonstration. "
            "It is NOT an official credit score (FICO/VantageScore), a bank credit rating, "
            "or a binding loan underwriting decision. Do not input sensitive personal information."
        ),
        "disclaimer_privacy": (
            "Privacy by Design: This system strictly processes model-required numerical credit parameters. "
            "Personal identification details (Name, Phone, Email, SSN, PAN, Aadhaar, Bank Accounts) "
            "are never requested, stored, or processed."
        ),
        "disclaimer_simulation": (
            "Hypothetical Simulation Notice: The simulator demonstrates how the model's estimated risk changes "
            "under hypothetical input conditions. It does not predict guaranteed future outcomes, lending approvals, "
            "or financial guarantees."
        ),
        "disclaimer_calibration": (
            "Model-estimated default likelihood is the model's direct output score from predict_proba(). "
            "This value has not been independently calibrated as a real-world empirical probability."
        ),
        "disclaimer_association": (
            "Model feature importance (Gini importance) indicates global statistical association across the training dataset. "
            "It reflects the model's reliance on each factor and does not prove individual causality."
        ),

        # Feedback & Notifications
        "msg_calculating": "Evaluating applicant credit profile through production pipeline...",
        "msg_simulating": "Executing What-If scenario simulation on production model...",
        "msg_success_calculated": "Assessment successfully calculated!",
        "msg_success_simulated": "Scenario simulation completed successfully!",
        "msg_invalid_input": "Invalid input detected. Please verify all numeric values.",
        "msg_limit_positive": "Approved credit limit must be greater than zero.",
    },

    "ta": {
        # App Meta & Header
        "app_title": "கடன் இடர் மதிப்பீடு மற்றும் நிதி ஆரோக்கிய தளம்",
        "app_subtitle": "கடன் இடர் மற்றும் நிதி ஆரோக்கியத்திற்கான வெளிப்படையான இயந்திர கற்றல் அமைப்பு",
        "app_badge": "இயந்திர கற்றல் மாதிரி",
        "nav_overview": "கண்ணோட்டம்",
        "nav_assess": "கடன் இடர் மதிப்பீடு",
        "nav_result": "மதிப்பீட்டு முடிவு",
        "nav_explain": "ஏன் இந்த முடிவு?",
        "nav_financial_health": "நிதி ஆரோக்கியம் (FHI-5)",
        "nav_simulator": "சாத்தியக்கூறு மாதிரி (What-If)",
        "nav_fairness": "நியாயத்தன்மை & சார்பு தணிக்கை",
        "nav_insights": "மாதிரி நுண்ணறிவுகள் & முறைமை",

        # Common Actions & Buttons
        "btn_assess_risk": "கடன் இடரை மதிப்பிடுக",
        "btn_run_assessment": "கடன் இடரை கணக்கிடுக",
        "btn_explore_what_if": "சாத்தியக்கூறுகளை ஆராய்க",
        "btn_simulate_scenario": "மாதிரியை இயக்குக",
        "btn_reset_scenario": "மீட்டமைக்க",
        "btn_load_sample": "மாதிரி விவரங்களை ஏற்றுக",
        "btn_clear": "படிவத்தை அழிக்க",
        "btn_view_details": "முழு விவரங்களையும் பார்க்க",
        "btn_copy_summary": "சுருக்கத்தை நகலெடு",
        "btn_switch_language": "மொழியை மாற்றுக",

        # Overview / Landing Page
        "overview_hero_title": "விளக்கக்கூடிய கடன் இடர் மற்றும் நிதி ஆரோக்கிய நுண்ணறிவு",
        "overview_hero_desc": "30,000 வங்கி பதிவுகளில் பயிற்றுவிக்கப்பட்ட வெளிப்படையான இயந்திர கற்றல் மாதிரியைப் பயன்படுத்தி கடன் தவறும் அபாயத்தை மதிப்பிடுங்கள். காரணங்களை ஆராய்ந்து, 5-அம்ச நிதி ஆரோக்கிய குறியீட்டைப் பெற்று, சாத்தியக்கூறு மாற்றங்களை சோதிக்கவும்.",
        "overview_card1_title": "துல்லியமான இயந்திர கற்றல்",
        "overview_card1_desc": "39 நிதி மற்றும் நடத்தை அம்சங்களை ஆராயும் ரேண்டம் பாரஸ்ட் மாடல் (ROC-AUC 0.7744) மூலம் மதிப்பீடு செய்யப்படுகிறது.",
        "overview_card2_title": "வெளிப்படையான விளக்கம்",
        "overview_card2_desc": "உங்கள் உண்மையான கட்டண வரலாற்றின் அடிப்படையில் இடர் காரணிகளையும் சாதகமான நிதி பலங்களையும் தெளிவாகக் காட்டுகிறது.",
        "overview_card3_title": "நிதி ஆரோக்கிய குறியீடு (FHI-5)",
        "overview_card3_desc": "கட்டண நேரம், கடன் பயன்பாடு, திருப்பிச் செலுத்தும் திறன், கடன் சுமை ஆகிய 5 அம்சங்களில் 0–100 மதிப்பெண் வழங்குகிறது.",
        "overview_card4_title": "சாத்தியக்கூறு உருவகப்படுத்துதல்",
        "overview_card4_desc": "நிலுவைத் தொகையை குறைத்தல் போன்ற நிதி மாற்றங்களை உருவகப்படுத்தி இடர் மாற்றங்களை உடனடியாகக் காணுங்கள்.",
        "overview_quick_start": "விரைவு தொடக்க விருப்பங்கள்",
        "overview_sample_prime": "மாதிரி விவரம்: சிறந்த / குறைந்த அபாயம்",
        "overview_sample_revolving": "மாதிரி விவரம்: மிதமான அபாயம்",
        "overview_sample_delinquent": "மாதிரி விவரம்: தாமதமான / அதிக அபாயம்",

        # Risk Assessment Form
        "form_title": "விண்ணப்பதாரர் கடன் விவர உள்ளீடு",
        "form_desc": "கடன் இடரை மதிப்பிட கடன் விவரங்களை உள்ளிடவும். தனிநபர் அடையாளத் தகவல்கள் எதுவும் சேகரிக்கப்படாமல் பாதுகாப்பாகச் செயல்படுத்தப்படுகிறது.",
        "form_sec_credit_profile": "கடன் வரம்பு & விவரங்கள்",
        "form_sec_repayment": "திருப்பிச் செலுத்தும் வரலாறு (கடந்த 6 மாதங்கள்)",
        "form_sec_bills": "மாதாந்திர பில் தொகைகள் (NT$)",
        "form_sec_payments": "செலுத்தப்பட்ட உண்மையான தொகைகள் (NT$)",

        # Feature Labels & Helpers
        "lbl_limit_bal": "அங்கீகரிக்கப்பட்ட கடன் வரம்பு (NT$)",
        "help_limit_bal": "கிரெடிட் கார்டில் வழங்கப்பட்ட மொத்த கடன் வரம்பு.",
        "lbl_sex": "பாலினம்",
        "lbl_sex_male": "ஆண்",
        "lbl_sex_female": "பெண்",
        "lbl_education": "கல்வி தகுதி",
        "lbl_edu_grad": "பட்டதாரி",
        "lbl_edu_uni": "பல்கலைக்கழகம்",
        "lbl_edu_high": "மேல்நிலைப் பள்ளி",
        "lbl_edu_other": "பிற",
        "lbl_marriage": "திருமண நிலை",
        "lbl_marr_married": "திருமணமானவர்",
        "lbl_marr_single": "திருமணமாகாதவர்",
        "lbl_marr_other": "பிற",
        "lbl_age": "வயது (ஆண்டுகள்)",
        "help_age": "விண்ணப்பதாரரின் வயது (21–79).",

        "lbl_pay_0": "செப்டம்பர் கட்டண நிலை (சமீபத்தியது)",
        "lbl_pay_2": "ஆகஸ்ட் கட்டண நிலை (1 மாதம் முன்)",
        "lbl_pay_3": "ஜூலை கட்டண நிலை (2 மாதங்கள் முன்)",
        "lbl_pay_4": "ஜூன் கட்டண நிலை (3 மாதங்கள் முன்)",
        "lbl_pay_5": "மே கட்டண நிலை (4 மாதங்கள் முன்)",
        "lbl_pay_6": "ஏப்ரல் கட்டண நிலை (5 மாதங்கள் முன்)",
        "opt_pay_neg2": "பயன்பாடு இல்லை / கட்டணம் இல்லை (-2)",
        "opt_pay_neg1": "முழுமையாக உரிய நேரத்தில் செலுத்தப்பட்டது (-1)",
        "opt_pay_0": "முறையாக உரிய நேரத்தில் பயன்படுத்தப்படுகிறது (0)",
        "opt_pay_1": "1 மாதம் தாமதம் (1)",
        "opt_pay_2": "2 மாதங்கள் தாமதம் (2)",
        "opt_pay_3": "3 மாதங்கள் தாமதம் (3)",
        "opt_pay_4": "4 மாதங்கள் தாமதம் (4)",
        "opt_pay_5": "5 மாதங்கள் தாமதம் (5)",
        "opt_pay_6": "6 மாதங்கள் தாமதம் (6)",
        "opt_pay_7": "7 மாதங்கள் தாமதம் (7)",
        "opt_pay_8": "8+ மாதங்கள் தாமதம் (8)",

        "lbl_bill_amt1": "செப்டம்பர் பில் தொகை (NT$)",
        "lbl_bill_amt2": "ஆகஸ்ட் பில் தொகை (NT$)",
        "lbl_bill_amt3": "ஜூலை பில் தொகை (NT$)",
        "lbl_bill_amt4": "ஜூன் பில் தொகை (NT$)",
        "lbl_bill_amt5": "மே பில் தொகை (NT$)",
        "lbl_bill_amt6": "ஏப்ரல் பில் தொகை (NT$)",

        "lbl_pay_amt1": "செப்டம்பர் செலுத்திய தொகை (NT$)",
        "lbl_pay_amt2": "ஆகஸ்ட் செலுத்திய தொகை (NT$)",
        "lbl_pay_amt3": "ஜூலை செலுத்திய தொகை (NT$)",
        "lbl_pay_amt4": "ஜூன் செலுத்திய தொகை (NT$)",
        "lbl_pay_amt5": "மே செலுத்திய தொகை (NT$)",
        "lbl_pay_amt6": "ஏப்ரல் செலுத்திய தொகை (NT$)",

        # Result Screen
        "result_header": "கடன் இடர் மதிப்பீட்டு முடிவு",
        "result_risk_level": "இடர் நிலை",
        "result_likelihood": "மதிப்பிடப்பட்ட கடன் தவறும் சாத்தியக்கூறு",
        "result_non_default_likelihood": "சரியாக செலுத்தும் சாத்தியக்கூறு",
        "result_binary_decision": "மாதிரி முடிவு",
        "result_summary": "மதிப்பீட்டு சுருக்கம்",
        "risk_tier_low": "குறைந்த அபாயம் (LOW RISK)",
        "risk_tier_medium": "மிதமான அபாயம் (MEDIUM RISK)",
        "risk_tier_high": "அதிக அபாயம் (HIGH RISK)",
        "pred_class_0": "தவறாதவர் (சாதகமானது)",
        "pred_class_1": "தவறும் வாய்ப்பு (அதிக அபாயம்)",

        # Explainability Screen
        "explain_header": "இடர் காரணிகள் மற்றும் நிதி பலங்கள்",
        "explain_subtitle": "கட்டண வரலாறு, கடன் பயன்பாடு மற்றும் நிதி நடத்தை ஆகியவற்றின் அடிப்படையில் தீர்மானிக்கப்படுகிறது.",
        "explain_risk_factors_title": "முக்கிய இடர் காரணிகள் (கவனிக்க வேண்டியவை)",
        "explain_positive_factors_title": "நிதி பலங்கள் மற்றும் சாதகமான அம்சங்கள்",
        "explain_no_risk_factors": "குறிப்பிடத்தக்க இடர் காரணிகள் எதுவும் இல்லை. கணக்கு சிறந்த முறையில் பராமரிக்கப்படுகிறது.",
        "explain_no_positive_factors": "முக்கிய சாதகமான அம்சங்கள் எதுவும் இல்லை. கட்டணங்களை சரியான நேரத்தில் செலுத்துவது சிறந்தது.",
        "explain_col_factor": "நிதி காரணி",
        "explain_col_value": "தற்போதைய மதிப்பு",
        "explain_col_impact": "மாதிரி தாக்கம்",
        "explain_col_explanation": "விளக்கம்",

        # Financial Health Indicator (FHI-5)
        "fhi_header": "நிதி ஆரோக்கிய குறியீடு (FHI-5)",
        "fhi_subtitle": "5 அடிப்படை கடன் மேலாண்மை தூண்களை மதிப்பிடும் 0–100 குறியீடு.",
        "fhi_score_title": "ஒட்டுமொத்த நிதி ஆரோக்கிய மதிப்பெண்",
        "fhi_tier_excellent": "மிகச் சிறந்தது (EXCELLENT)",
        "fhi_tier_good": "நல்லது (GOOD)",
        "fhi_tier_fair": "மிதமானது (FAIR)",
        "fhi_tier_poor": "மோசமானது / இடர் (POOR)",
        "fhi_pillar_1": "கட்டண நேரம் மற்றும் வரலாறு",
        "fhi_pillar_1_weight": "35% பங்கு",
        "fhi_pillar_2": "கடன் பயன்பாட்டு விகிதம்",
        "fhi_pillar_2_weight": "25% பங்கு",
        "fhi_pillar_3": "திருப்பிச் செலுத்தும் போதுமான தன்மை",
        "fhi_pillar_3_weight": "20% பங்கு",
        "fhi_pillar_4": "கடன் சுமை மற்றும் பற்றாக்குறை",
        "fhi_pillar_4_weight": "15% பங்கு",
        "fhi_pillar_5": "கணக்கு போக்கு மற்றும் முன்னேற்றம்",
        "fhi_pillar_5_weight": "5% பங்கு",

        # What-If Simulator
        "sim_header": "சாத்தியக்கூறு மாதிரி (What-If Simulator)",
        "sim_subtitle": "நிதி மாற்றங்களை உருவகப்படுத்தி மாதிரி எவ்வாறு செயல்படுகிறது என்பதை உடனுக்குடன் பாருங்கள்.",
        "sim_panel_controls": "1. மாற்றங்களை அமைத்தல்",
        "sim_panel_result": "2. மாதிரி மதிப்பீட்டு முடிவு",
        "sim_panel_comparison": "3. தற்போதைய vs உருவகப்படுத்தப்பட்ட ஒப்பீடு",
        "sim_presets_title": "எளிதான மாற்ற விருப்பங்கள்",
        "sim_preset_remediate": "சமீபத்திய தாமதங்களை சரிசெய்க",
        "sim_preset_paydown_50": "பில் நிலுவைத் தொகையை 50% செலுத்துக",
        "sim_preset_paydown_80": "அதிக நிலுவைத் தொகையை (80%) செலுத்துக",
        "sim_preset_limit_inc": "கடன் வரம்பை 50% உயர்த்துக",
        "sim_lbl_current_baseline": "தற்போதைய நிலை",
        "sim_lbl_simulated_scenario": "உருவகப்படுத்தப்பட்ட நிலை",
        "sim_lbl_prob_delta": "இடர் சாத்தியக்கூறு மாற்றம்",
        "sim_lbl_fhi_delta": "நிதி ஆரோக்கிய மதிப்பெண் மாற்றம்",
        "sim_direction_improved": "முன்னேற்றம் (IMPROVED)",
        "sim_direction_worsened": "பின்னடைவு (WORSENED)",
        "sim_direction_unchanged": "மாற்றமில்லை (UNCHANGED)",
        "sim_resolved_factors_title": "சரிசெய்யப்பட்ட இடர் காரணிகள்",
        "sim_gained_strengths_title": "புதிதாக பெற்ற சாதக பலங்கள்",
        "sim_table_col_factor": "காரணி",
        "sim_table_col_current": "தற்போதைய மதிப்பு",
        "sim_table_col_scenario": "உருவகப்படுத்தப்பட்ட மதிப்பு",
        "sim_table_col_change": "நிகர மாற்றம்",

        # Model Insights & Methodology
        "insights_header": "மாதிரி நுண்ணறிவுகள் மற்றும் முறைமை",
        "insights_champion_title": "முக்கிய மாதிரி கட்டமைப்பு",
        "insights_champion_desc": "பயிற்றுவிக்கப்பட்ட ரேண்டம் பாரஸ்ட் கிளாசிஃபையர் (150 மரங்கள், ஆழம் 12).",
        "insights_metrics_title": "மாதிரி செயல்திறன் அளவீடுகள்",
        "insights_metric_auc": "ROC-AUC மதிப்பெண்: 0.7744 (இலக்கு > 0.75 நிறைவுற்றது)",
        "insights_metric_acc": "துல்லியம் (Accuracy): 82.02% (இலக்கு > 80% நிறைவுற்றது)",
        "insights_metric_brier": "Brier மதிப்பெண்: 0.1299 (நன்கு அளவீடு செய்யப்பட்ட நிகழ்தகவு)",
        "insights_metric_f1": "Default F1-Score: 0.4812",
        "insights_feature_imp_title": "முக்கிய அம்சங்களின் முக்கியத்துவம் (Gini Index)",
        "insights_disclaimer_title": "பொறுப்புத் துறப்பு மற்றும் வழிகாட்டுதல்",

        # Fairness & Bias Audit
        "fairness_title": "நியாயத்தன்மை மற்றும் மக்கள்தொகை சார்பு தணிக்கை",
        "fairness_subtitle": "குழு அளவிலான செயல்திறன் அளவீடுகள், ஏற்றத்தாழ்வு மதிப்பீடு மற்றும் தரவுத்தொகுப்பு கட்டுப்பாடுகள்.",
        "fairness_tab_overview": "தரவுத்தொகுப்பு மற்றும் அம்ச தணிக்கை",
        "fairness_tab_metrics": "குழு அளவீடுகள் & ஒப்பீடுகள்",
        "fairness_tab_limitations": "கோட்பாடுகள் & வரம்புகள்",
        "fairness_dataset_total": "மதிப்பீடு செய்யப்பட்ட மொத்த பதிவுகள்",
        "fairness_available_demographics": "தரவுத்தொகுப்பில் உள்ள மக்கள்தொகை மாறிகள்",
        "fairness_unavailable_demographics": "தரவுத்தொகுப்பில் இல்லாத முக்கியமான தகவல்கள்",
        "fairness_removed_variables": "விலக்கப்பட்ட மாறிகள்",
        "fairness_retained_variables": "மாதிரியில் உள்ள மாறிகள்",
        "fairness_select_attribute": "தணிக்கை செய்ய வேண்டிய பண்பைத் தேர்ந்தெடுக்கவும்:",
        "fairness_reference_group": "அடிப்படை / ஒப்பீட்டுக் குழு:",
        "fairness_metric_base_rate": "உண்மையான தவறும் விகிதம் (Base Rate)",
        "fairness_metric_ppr": "கணிக்கப்பட்ட தவறும் விகிதம் (PPR)",
        "fairness_metric_recall": "உண்மையான நேர்மறை விகிதம் (Recall / TPR)",
        "fairness_metric_fpr": "தவறான நேர்மறை விகிதம் (FPR)",
        "fairness_metric_fnr": "தவறான எதிர்மறை விகிதம் (FNR)",
        "fairness_metric_precision": "துல்லிய விகிதம் (Precision)",
        "fairness_metric_accuracy": "ஒட்டுமொத்த துல்லியம் (Accuracy)",
        "fairness_small_sample_warning": "எச்சரிக்கை: சிறிய மாதிரி அளவு (<300). அளவீடுகளில் மாறுபாடு இருக்கலாம்.",
        "fairness_disparity_diff": "அடிப்படையுடன் உள்ள வேறுபாடு (Δ)",
        "fairness_disparity_ratio": "அடிப்படையுடன் உள்ள விகிதம் (Group / Ref)",
        "fairness_principle_1": "முழுமையான நியாயத்தன்மை கோரப்படவில்லை: மாதிரி முற்றிலும் சார்பற்றது என்று நாங்கள் கூறவில்லை.",
        "fairness_principle_2": "வெளிப்படைத்தன்மை இல்லாமை தவறானது: மக்கள்தொகை மாறிகளை நீக்குவது நிதி தொடர்புகளால் சமத்துவத்தை உறுதிப்படுத்தாது.",
        "fairness_principle_3": "மாதிரி அளவு கட்டுப்பாடு: சிறிய குழுக்கள் புள்ளியியல் நிச்சயமற்ற தன்மையைக் கொண்டுள்ளன.",

        # Disclaimers & Trust Statements
        "disclaimer_legal": (
            "இது ஒரு கல்வி நோக்கிலான இயந்திர கற்றல் இடர் மதிப்பீட்டு விளக்கம் மட்டுமே. "
            "இது அதிகாரப்பூர்வ கிரெடிட் ஸ்கோர் (FICO/VantageScore), வங்கி ஒப்புதல் அல்லது கடன் முடிவு அல்ல. "
            "உண்மையான முக்கிய தனிநபர் தகவல்களை உள்ளிட வேண்டாம்."
        ),
        "disclaimer_privacy": (
            "தனியுரிமை பாதுகாப்பு: இந்த அமைப்பு மாடலுக்குத் தேவையான எண் மதிப்புகளை மட்டுமே கையாளுகிறது. "
            "பெயர், தொலைபேசி எண், மின்னஞ்சல், ஆதார், பான், வங்கி கணக்கு எண் போன்ற தனிப்பட்ட விவரங்கள் சேகரிக்கப்படுவதில்லை."
        ),
        "disclaimer_simulation": (
            "உருவகப்படுத்துதல் அறிவிப்பு: இந்த மாதிரி கற்பனையான மாற்றங்களின் கீழ் கணக்கிடப்படும் இடர் மாற்றத்தை மட்டுமே காட்டுகிறது. "
            "இது கடன் ஒப்புதலுக்கான உத்தரவாதம் அல்ல."
        ),
        "disclaimer_calibration": (
            "மதிப்பிடப்பட்ட தவறும் சாத்தியக்கூறு என்பது மாதிரியின் கணிப்பு மட்டுமே. இது நிஜ உலக நிகழ்தகவாக உறுதிப்படுத்தப்படவில்லை."
        ),
        "disclaimer_association": (
            "மாதிரி முக்கியத்துவம் என்பது பொதுவான புள்ளியியல் தொடர்பைக் குறிக்கிறது; தனிநபரின் நேரடி காரணத்தை நிரூபிக்காது."
        ),

        # Feedback & Notifications
        "msg_calculating": "கடன் விவரங்கள் மதிப்பீடு செய்யப்படுகின்றன...",
        "msg_simulating": "சாத்தியக்கூறு மாதிரி கணக்கிடப்படுகிறது...",
        "msg_success_calculated": "மதிப்பீடு வெற்றிகரமாக முடிக்கப்பட்டது!",
        "msg_success_simulated": "உருவகப்படுத்துதல் வெற்றிகரமாக முடிந்தது!",
        "msg_invalid_input": "தவறான உள்ளீடு. எண்களைச் சரிபார்க்கவும்.",
        "msg_limit_positive": "கடன் வரம்பு பூஜ்ஜியத்தை விட அதிகமாக இருக்க வேண்டும்.",
    },

    "hi": {
        # App Meta & Header
        "app_title": "क्रेडिट जोखिम मूल्यांकन एवं वित्तीय स्वास्थ्य मंच",
        "app_subtitle": "क्रेडिट जोखिम और वित्तीय स्वास्थ्य के लिए पारदर्शी मशीन लर्निंग प्रणाली",
        "app_badge": "प्रोडक्शन एमएल मॉडल",
        "nav_overview": "अवलोकन",
        "nav_assess": "क्रेडिट जोखिम का आकलन",
        "nav_result": "मूल्यांकन परिणाम",
        "nav_explain": "यह परिणाम क्यों?",
        "nav_financial_health": "वित्तीय स्वास्थ्य (FHI-5)",
        "nav_simulator": "व्हाट-इफ सिम्युलेटर (परिदृश्य)",
        "nav_fairness": "निष्पक्षता एवं जनसांख्यिकीय ऑडिट",
        "nav_insights": "मॉडल अंतर्दृष्टि एवं कार्यप्रणाली",

        # Common Actions & Buttons
        "btn_assess_risk": "क्रेडिट जोखिम जांचें",
        "btn_run_assessment": "जोखिम की गणना करें",
        "btn_explore_what_if": "परिदृश्यों का अन्वेषण करें",
        "btn_simulate_scenario": "सिमुलेशन चलाएं",
        "btn_reset_scenario": "रीसेट करें",
        "btn_load_sample": "नमूना प्रोफ़ाइल लोड करें",
        "btn_clear": "फॉर्म साफ़ करें",
        "btn_view_details": "पूरा विवरण देखें",
        "btn_copy_summary": "सारांश कॉपी करें",
        "btn_switch_language": "भाषा बदलें",

        # Overview / Landing Page
        "overview_hero_title": "व्याख्यात्मक क्रेडिट जोखिम और वित्तीय स्वास्थ्य बुद्धिमत्ता",
        "overview_hero_desc": "30,000 क्रेडिट ब्यूरो रिकॉर्ड पर प्रशिक्षित पारदर्शी मशीन लर्निंग मॉडल के साथ क्रेडिट कार्ड डिफॉल्ट जोखिम का मूल्यांकन करें। इसके मूल कारणों को समझें, अपना 5-स्तंभ वित्तीय स्वास्थ्य स्कोर जानें और वित्तीय सुधारों का सिमुलेशन करें।",
        "overview_card1_title": "सटीक मशीन लर्निंग",
        "overview_card1_desc": "39 वित्तीय एवं व्यवहारिक विशेषताओं का विश्लेषण करने वाले ऑडिट किए गए रैंडम फ़ॉरेस्ट मॉडल (ROC-AUC 0.7744) द्वारा संचालित।",
        "overview_card2_title": "पारदर्शी व्याख्या",
        "overview_card2_desc": "आपके वास्तविक भुगतान इतिहास के आधार पर प्रमुख जोखिम कारकों और सकारात्मक वित्तीय शक्तियों की स्पष्ट पहचान।",
        "overview_card3_title": "वित्तीय स्वास्थ्य सूचकांक (FHI-5)",
        "overview_card3_desc": "समय पर भुगतान, क्रेडिट उपयोग, भुगतान पर्याप्तता, और ऋण भार के 5 प्रमुख आधारों पर 0–100 स्कोर प्रदान करता है।",
        "overview_card4_title": "व्हाट-इफ परिदृश्य सिमुलेशन",
        "overview_card4_desc": "बकाया राशि का भुगतान करने जैसे वित्तीय परिवर्तनों का सिमुलेशन करें और मॉडल के परिणाम में आए बदलाव को तुरंत देखें।",
        "overview_quick_start": "त्वरित आरंभ विकल्प",
        "overview_sample_prime": "नमूना प्रोफ़ाइल: उत्कृष्ट / कम जोखिम",
        "overview_sample_revolving": "नमूना प्रोफ़ाइल: मध्यम जोखिम",
        "overview_sample_delinquent": "नमूना प्रोफ़ाइल: विलंबित / उच्च जोखिम",

        # Risk Assessment Form
        "form_title": "आवेदक क्रेडिट प्रोफ़ाइल इनपुट",
        "form_desc": "क्रेडिट जोखिम का मूल्यांकन करने के लिए विवरण दर्ज करें। कोई भी व्यक्तिगत पहचान डेटा एकत्र किए बिना सभी डेटा सुरक्षित रूप से संसाधित होता है।",
        "form_sec_credit_profile": "क्रेडिट सीमा एवं विवरण",
        "form_sec_repayment": "भुगतान समयबद्धता इतिहास (पिछले 6 महीने)",
        "form_sec_bills": "मासिक बिल राशि (NT$)",
        "form_sec_payments": "वास्तविक भुगतान की गई राशि (NT$)",

        # Feature Labels & Helpers
        "lbl_limit_bal": "स्वीकृत क्रेडिट सीमा (NT$)",
        "help_limit_bal": "क्रेडिट कार्ड पर दी गई कुल क्रेडिट सीमा।",
        "lbl_sex": "लिंग",
        "lbl_sex_male": "पुरुष",
        "lbl_sex_female": "महिला",
        "lbl_education": "शिक्षा का स्तर",
        "lbl_edu_grad": "स्नातकोत्तर (Graduate)",
        "lbl_edu_uni": "विश्वविद्यालय (University)",
        "lbl_edu_high": "हाई स्कूल",
        "lbl_edu_other": "अन्य",
        "lbl_marriage": "वैवाहिक स्थिति",
        "lbl_marr_married": "विवाहित",
        "lbl_marr_single": "अविवाहित",
        "lbl_marr_other": "अन्य",
        "lbl_age": "आयु (वर्ष)",
        "help_age": "आवेदक की आयु (21–79 वर्ष)।",

        "lbl_pay_0": "सितंबर भुगतान स्थिति (नवीनतम)",
        "lbl_pay_2": "अगस्त भुगतान स्थिति (1 माह पूर्व)",
        "lbl_pay_3": "जुलाई भुगतान स्थिति (2 माह पूर्व)",
        "lbl_pay_4": "जून भुगतान स्थिति (3 माह पूर्व)",
        "lbl_pay_5": "मई भुगतान स्थिति (4 माह पूर्व)",
        "lbl_pay_6": "अप्रैल भुगतान स्थिति (5 माह पूर्व)",
        "opt_pay_neg2": "कोई उपयोग नहीं / शून्य शेष (-2)",
        "opt_pay_neg1": "पूर्ण भुगतान समय पर किया गया (-1)",
        "opt_pay_0": "क्रेडिट का उपयोग समय पर जारी (0)",
        "opt_pay_1": "1 माह की देरी (1)",
        "opt_pay_2": "2 माह की देरी (2)",
        "opt_pay_3": "3 माह की देरी (3)",
        "opt_pay_4": "4 माह की देरी (4)",
        "opt_pay_5": "5 माह की देरी (5)",
        "opt_pay_6": "6 माह की देरी (6)",
        "opt_pay_7": "7 माह की देरी (7)",
        "opt_pay_8": "8+ माह की देरी (8)",

        "lbl_bill_amt1": "सितंबर बिल राशि (NT$)",
        "lbl_bill_amt2": "अगस्त बिल राशि (NT$)",
        "lbl_bill_amt3": "जुलाई बिल राशि (NT$)",
        "lbl_bill_amt4": "जून बिल राशि (NT$)",
        "lbl_bill_amt5": "मई बिल राशि (NT$)",
        "lbl_bill_amt6": "अप्रैल बिल राशि (NT$)",

        "lbl_pay_amt1": "सितंबर भुगतान राशि (NT$)",
        "lbl_pay_amt2": "अगस्त भुगतान राशि (NT$)",
        "lbl_pay_amt3": "जुलाई भुगतान राशि (NT$)",
        "lbl_pay_amt4": "जून भुगतान राशि (NT$)",
        "lbl_pay_amt5": "मई भुगतान राशि (NT$)",
        "lbl_pay_amt6": "अप्रैल भुगतान राशि (NT$)",

        # Result Screen
        "result_header": "क्रेडिट जोखिम मूल्यांकन परिणाम",
        "result_risk_level": "जोखिम श्रेणी",
        "result_likelihood": "डिफ़ॉल्ट की अनुमानित संभावना",
        "result_non_default_likelihood": "समय पर भुगतान की संभावना",
        "result_binary_decision": "मॉडल वर्गीकरण",
        "result_summary": "मूल्यांकन सारांश",
        "risk_tier_low": "कम जोखिम (LOW RISK)",
        "risk_tier_medium": "मध्यम जोखिम (MEDIUM RISK)",
        "risk_tier_high": "उच्च जोखिम (HIGH RISK)",
        "pred_class_0": "डिफ़ॉल्ट नहीं (अनुकूल)",
        "pred_class_1": "डिफ़ॉल्ट का जोखिम (उच्च जोखिम)",

        # Explainability Screen
        "explain_header": "जोखिम कारक एवं वित्तीय शक्तियां",
        "explain_subtitle": "रैंडम फ़ॉरेस्ट फीचर महत्व और आपके भुगतान इतिहास के आधार पर निर्धारित।",
        "explain_risk_factors_title": "प्रमुख जोखिम कारक (चिंता के बिंदु)",
        "explain_positive_factors_title": "सकारात्मक वित्तीय शक्तियां",
        "explain_no_risk_factors": "कोई महत्वपूर्ण नकारात्मक जोखिम कारक नहीं पाया गया। आपका क्रेडिट व्यवहार अनुशासित है।",
        "explain_no_positive_factors": "कोई प्रमुख सकारात्मक कारक नहीं मिला। समय पर भुगतान सुधारने की सलाह दी जाती है।",
        "explain_col_factor": "वित्तीय कारक",
        "explain_col_value": "वर्तमान मान",
        "explain_col_impact": "मॉडल प्रभाव",
        "explain_col_explanation": "स्पष्टीकरण",

        # Financial Health Indicator (FHI-5)
        "fhi_header": "वित्तीय स्वास्थ्य सूचकांक (FHI-5)",
        "fhi_subtitle": "5 मूलभूत क्रेडिट प्रबंधन स्तंभों का मूल्यांकन करने वाला 0–100 सूचकांक।",
        "fhi_score_title": "कुल वित्तीय स्वास्थ्य स्कोर",
        "fhi_tier_excellent": "उत्कृष्ट (EXCELLENT)",
        "fhi_tier_good": "अच्छा (GOOD)",
        "fhi_tier_fair": "संतोषजनक (FAIR)",
        "fhi_tier_poor": "कमज़ोर / जोखिमपूर्ण (POOR)",
        "fhi_pillar_1": "भुगतान समयबद्धता एवं इतिहास",
        "fhi_pillar_1_weight": "35% भार",
        "fhi_pillar_2": "क्रेडिट उपयोग अनुपात",
        "fhi_pillar_2_weight": "25% भार",
        "fhi_pillar_3": "भुगतान पर्याप्तता",
        "fhi_pillar_3_weight": "20% भार",
        "fhi_pillar_4": "ऋण भार एवं घाटा",
        "fhi_pillar_4_weight": "15% भार",
        "fhi_pillar_5": "खाता रुझान एवं गति",
        "fhi_pillar_5_weight": "5% भार",

        # What-If Simulator
        "sim_header": "व्हाट-इफ परिदृश्य सिम्युलेटर",
        "sim_subtitle": "वित्तीय परिवर्तनों का सिमुलेशन करें और देखें कि मॉडल वास्तविक समय में कैसे प्रतिक्रिया देता है।",
        "sim_panel_controls": "1. परिदृश्य नियंत्रण",
        "sim_panel_result": "2. सिमुलेशन परिणाम",
        "sim_panel_comparison": "3. वर्तमान बनाम परिदृश्य तुलना",
        "sim_presets_title": "त्वरित परिदृश्य प्रीसेट",
        "sim_preset_remediate": "हाल की देरी का समाधान करें",
        "sim_preset_paydown_50": "बिल बकाया राशि को 50% चुकाएं",
        "sim_preset_paydown_80": "महत्वपूर्ण बकाया राशि (80%) चुकाएं",
        "sim_preset_limit_inc": "क्रेडिट सीमा में 50% वृद्धि करें",
        "sim_lbl_current_baseline": "वर्तमान स्थिति",
        "sim_lbl_simulated_scenario": "सिम्युलेटेड स्थिति",
        "sim_lbl_prob_delta": "डिफ़ॉल्ट संभावना में अंतर",
        "sim_lbl_fhi_delta": "वित्तीय स्वास्थ्य स्कोर में अंतर",
        "sim_direction_improved": "सुधार (IMPROVED)",
        "sim_direction_worsened": "गिरावट (WORSENED)",
        "sim_direction_unchanged": "कोई बदलाव नहीं (UNCHANGED)",
        "sim_resolved_factors_title": "समाधान किए गए जोखिम कारक",
        "sim_gained_strengths_title": "नई प्राप्त वित्तीय शक्तियां",
        "sim_table_col_factor": "वित्तीय कारक",
        "sim_table_col_current": "वर्तमान मान",
        "sim_table_col_scenario": "परिदृश्य मान",
        "sim_table_col_change": "शुद्ध परिवर्तन",

        # Model Insights & Methodology
        "insights_header": "मॉडल अंतर्दृष्टि एवं निष्पक्षता",
        "insights_champion_title": "प्रोडक्शन मॉडल आर्किटेक्चर",
        "insights_champion_desc": "प्रशिक्षित रैंडम फ़ॉरेस्ट क्लासिफ़ायर (150 पेड़, अधिकतम गहराई 12)।",
        "insights_metrics_title": "ऑडिट किए गए मॉडल मेट्रिक्स",
        "insights_metric_auc": "ROC-AUC स्कोर: 0.7744 (मानक > 0.75 सफल)",
        "insights_metric_acc": "सटीकता (Accuracy): 82.02% (मानक > 80% सफल)",
        "insights_metric_brier": "Brier स्कोर: 0.1299 (सटीक संभाव्यता वितरण)",
        "insights_metric_f1": "Default F1-Score: 0.4812",
        "insights_feature_imp_title": "वैश्विक फीचर महत्व (Gini Index)",
        "insights_disclaimer_title": "मॉडल अस्वीकरण एवं दिशानिर्देश",

        # Fairness & Bias Audit
        "fairness_title": "निष्पक्षता एवं जनसांख्यिकीय पूर्वाग्रह ऑडिट",
        "fairness_subtitle": "समूह-स्तरीय प्रदर्शन मेट्रिक्स, असमानता मूल्यांकन और डेटासेट सीमाओं का पारदर्शी दस्तावेजीकरण।",
        "fairness_tab_overview": "डेटासेट एवं फीचर ऑडिट",
        "fairness_tab_metrics": "समूह मेट्रिक्स एवं असमानताएं",
        "fairness_tab_limitations": "सिद्धांत एवं सीमाएं",
        "fairness_dataset_total": "कुल मूल्यांकित रिकॉर्ड",
        "fairness_available_demographics": "डेटासेट में उपलब्ध जनसांख्यिकीय चर",
        "fairness_unavailable_demographics": "अनुपलब्ध संवेदनशील चर (डेटा अंतर)",
        "fairness_removed_variables": "हटाए गए चर (ID आदि)",
        "fairness_retained_variables": "मॉडल पाइपलाइन में रखे गए चर",
        "fairness_select_attribute": "ऑडिट के लिए जनसांख्यिकीय विशेषता चुनें:",
        "fairness_reference_group": "आधार रेखा / संदर्भ समूह:",
        "fairness_metric_base_rate": "वास्तविक डिफ़ॉल्ट दर (Base Rate)",
        "fairness_metric_ppr": "अनुमानित डिफ़ॉल्ट दर (PPR)",
        "fairness_metric_recall": "वास्तविक सकारात्मक दर (Recall / TPR)",
        "fairness_metric_fpr": "गलत सकारात्मक दर (FPR)",
        "fairness_metric_fnr": "गलत नकारात्मक दर (FNR)",
        "fairness_metric_precision": "सटीकता दर (Precision / PPV)",
        "fairness_metric_accuracy": "समग्र सटीकता (Accuracy)",
        "fairness_small_sample_warning": "चेतावनी: छोटा नमूना आकार (<300)। मेट्रिक्स में सांख्यिकीय भिन्नता अधिक हो सकती है।",
        "fairness_disparity_diff": "आधार रेखा से अंतर (Δ)",
        "fairness_disparity_ratio": "आधार रेखा से अनुपात (Group / Ref)",
        "fairness_principle_1": "पूर्ण निष्पक्षता का कोई दावा नहीं: हम स्पष्ट रूप से यह दावा नहीं करते कि मॉडल निष्पक्ष या पूर्वाग्रह मुक्त है।",
        "fairness_principle_2": "अंधता द्वारा निष्पक्षता का भ्रम: जनसांख्यिकीय चर हटाने से सह-संबंधित वित्तीय कारकों के कारण असमानता समाप्त नहीं होती।",
        "fairness_principle_3": "नमूना आकार अनुशासन: छोटे समूहों को सांख्यिकीय अनिश्चितता चेतावनी के साथ चिह्नित किया गया है।",

        # Disclaimers & Trust Statements
        "disclaimer_legal": (
            "यह एप्लिकेशन केवल एक शैक्षिक मशीन लर्निंग जोखिम मूल्यांकन प्रदर्शन है। "
            "यह कोई आधिकारिक क्रेडिट स्कोर (FICO/VantageScore), बैंक रेटिंग या ऋण स्वीकृति निर्णय नहीं है। "
            "वास्तविक संवेदनशील व्यक्तिगत जानकारी दर्ज न करें।"
        ),
        "disclaimer_privacy": (
            "गोपनीयता सुरक्षा: यह प्रणाली केवल मॉडल-आवश्यक संख्यात्मक क्रेडिट मापदंडों को संसाधित करती है। "
            "व्यक्तिगत पहचान विवरण (नाम, फोन, ईमेल, आधार, पैन, बैंक खाता) कभी एकत्र नहीं किए जाते हैं।"
        ),
        "disclaimer_simulation": (
            "सिमुलेशन सूचना: सिम्युलेटर दर्शाता है कि काल्पनिक इनपुट के तहत मॉडल का अनुमान कैसे बदलता है। "
            "यह भविष्य के परिणामों या ऋण स्वीकृति की कोई गारंटी नहीं देता है।"
        ),
        "disclaimer_calibration": (
            "अनुमानित डिफ़ॉल्ट संभावना मॉडल का आउटपुट स्कोर है। इसे वास्तविक दुनिया की संभावना के रूप में स्वतंत्र रूप से कैलिब्रेट नहीं किया गया है।"
        ),
        "disclaimer_association": (
            "मॉडल फीचर महत्व सामान्य सांख्यिकीय संबंध को दर्शाता है; यह व्यक्तिगत कारण-प्रभाव साबित नहीं करता है।"
        ),

        # Feedback & Notifications
        "msg_calculating": "क्रेडिट प्रोफ़ाइल का मूल्यांकन किया जा रहा है...",
        "msg_simulating": "व्हाट-इफ सिमुलेशन चलाया जा रहा है...",
        "msg_success_calculated": "मूल्यांकन सफलतापूर्वक पूरा हुआ!",
        "msg_success_simulated": "सिमुलेशन सफलतापूर्वक पूरा हुआ!",
        "msg_invalid_input": "अमान्य इनपुट। कृपया संख्याओं की जांच करें।",
        "msg_limit_positive": "स्वीकृत क्रेडिट सीमा शून्य से अधिक होनी चाहिए।",
    }
}
