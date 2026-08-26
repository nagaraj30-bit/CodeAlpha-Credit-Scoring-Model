"""
Credit Intelligence & Risk Engine — Production Streamlit Application
====================================================================
A human-centered, explainable, multilingual machine learning application
for credit risk assessment, Financial Health scoring (FHI-5), and
real-time What-If scenario simulation.

Phases 6–8 Integration:
- Phase 6: Full Multilingual Support (English, தமிழ், हिन्दी) + Accessible UI
- Phase 7: Complete Streamlit Integration with production ML pipeline
- Phase 8: Premium Fintech UI/UX Design System, Risk Visualizations, and Flagship Simulator
"""

import os
import sys
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import streamlit as st

# Add src to python path for clean modular imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from data_loader import load_credit_data
from financial_health import (
    COMPONENT_WEIGHTS,
    FINANCIAL_HEALTH_DISCLAIMER,
    calculate_financial_health,
    determine_health_label,
)
from i18n import (
    SUPPORTED_LANGUAGES,
    get_current_language,
    get_supported_languages,
    set_current_language,
    t,
)
from predict import (
    LEGAL_DISCLAIMER,
    PRIVACY_STATEMENT,
    PROBABILITY_CALIBRATION_NOTICE,
    REQUIRED_CREDIT_COLUMNS,
    predict_credit_risk,
)
from risk_reasons import FEATURE_TERMINOLOGY_MAP, explain_prediction
from fairness import (
    DEMOGRAPHIC_CONFIGS,
    bin_age_groups,
    generate_full_fairness_report,
)
from scenario_simulator import (
    SIMULATOR_DISCLAIMER,
    SUPPORTED_SCENARIO_VARIABLES,
    simulate_balance_paydown,
    simulate_credit_limit_increase,
    simulate_repayment_remediation,
    simulate_scenario,
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & FINTECH STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Credit Intelligence & Risk Engine",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* Modern Fintech Typography & Color Variables */
:root {
    --primary: #0284C7;
    --primary-dark: #0369A1;
    --bg-main: #F8FAFC;
    --card-bg: #FFFFFF;
    --text-main: #0F172A;
    --text-muted: #64748B;
    --border-color: #E2E8F0;
    --risk-low: #10B981;
    --risk-med: #F59E0B;
    --risk-high: #EF4444;
}

/* Base App Framing */
.stApp {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Card Containers */
.fintech-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
}

.fintech-card-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 8px;
}

/* Metric Display Cards */
.metric-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.metric-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.1;
    color: #0F172A;
}

.metric-sub {
    font-size: 0.85rem;
    color: #64748B;
    margin-top: 6px;
}

/* Risk Badges */
.badge-risk-low {
    display: inline-block;
    background-color: #ECFDF5;
    color: #065F46;
    border: 1px solid #A7F3D0;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.95rem;
}

.badge-risk-med {
    display: inline-block;
    background-color: #FFFBEB;
    color: #92400E;
    border: 1px solid #FDE68A;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.95rem;
}

.badge-risk-high {
    display: inline-block;
    background-color: #FEF2F2;
    color: #991B1B;
    border: 1px solid #FECACA;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.95rem;
}

/* Pillar Progress Item */
.pillar-row {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

/* Disclaimer Banner */
.disclaimer-banner {
    background-color: #F1F5F9;
    border-left: 4px solid #64748B;
    padding: 12px 16px;
    border-radius: 4px;
    font-size: 0.85rem;
    color: #475569;
    margin-top: 24px;
    line-height: 1.45;
}

/* Form Section Title */
.form-section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1E293B;
    margin-top: 16px;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 2px solid #E2E8F0;
}

/* Responsive Media Queries */
@media (max-width: 768px) {
    .fintech-card {
        padding: 16px;
        margin-bottom: 16px;
    }
    .metric-container {
        padding: 14px;
    }
    .metric-value {
        font-size: 1.6rem;
    }
    .fintech-card-header {
        font-size: 1.05rem;
    }
    .badge-risk-low, .badge-risk-med, .badge-risk-high {
        font-size: 0.85rem;
        padding: 4px 10px;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_cached_dataset():
    """Load benchmark dataset for sample applicant inspection."""
    df, _ = load_credit_data("data/credit_data.csv")
    return df


df_benchmark = get_cached_dataset()

# Default Prime / Clean Sample Profile (Index 2 in UCI dataset)
SAMPLE_PRIME = {
    "LIMIT_BAL": 90000.0, "SEX": 2, "EDUCATION": 2, "MARRIAGE": 2, "AGE": 34,
    "PAY_0": 0, "PAY_2": 0, "PAY_3": 0, "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
    "BILL_AMT1": 29239.0, "BILL_AMT2": 14027.0, "BILL_AMT3": 13559.0,
    "BILL_AMT4": 14331.0, "BILL_AMT5": 14948.0, "BILL_AMT6": 15549.0,
    "PAY_AMT1": 1518.0, "PAY_AMT2": 1500.0, "PAY_AMT3": 1000.0,
    "PAY_AMT4": 1000.0, "PAY_AMT5": 1000.0, "PAY_AMT6": 5000.0
}

# Delinquent Sample Profile (Index 0 in UCI dataset)
SAMPLE_DELINQUENT = {
    "LIMIT_BAL": 20000.0, "SEX": 2, "EDUCATION": 2, "MARRIAGE": 1, "AGE": 24,
    "PAY_0": 2, "PAY_2": 2, "PAY_3": -1, "PAY_4": -1, "PAY_5": -2, "PAY_6": -2,
    "BILL_AMT1": 3913.0, "BILL_AMT2": 3102.0, "BILL_AMT3": 689.0,
    "BILL_AMT4": 0.0, "BILL_AMT5": 0.0, "BILL_AMT6": 0.0,
    "PAY_AMT1": 0.0, "PAY_AMT2": 689.0, "PAY_AMT3": 0.0,
    "PAY_AMT4": 0.0, "PAY_AMT5": 0.0, "PAY_AMT6": 0.0
}

# High Revolving Utilization Sample Profile
SAMPLE_REVOLVING = {
    "LIMIT_BAL": 50000.0, "SEX": 1, "EDUCATION": 1, "MARRIAGE": 2, "AGE": 30,
    "PAY_0": 0, "PAY_2": 0, "PAY_3": 0, "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
    "BILL_AMT1": 48500.0, "BILL_AMT2": 49000.0, "BILL_AMT3": 47800.0,
    "BILL_AMT4": 46000.0, "BILL_AMT5": 45000.0, "BILL_AMT6": 44000.0,
    "PAY_AMT1": 2000.0, "PAY_AMT2": 2000.0, "PAY_AMT3": 2000.0,
    "PAY_AMT4": 2000.0, "PAY_AMT5": 2000.0, "PAY_AMT6": 2000.0
}

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

if "current_applicant" not in st.session_state:
    st.session_state["current_applicant"] = SAMPLE_DELINQUENT.copy()

if "prediction_result" not in st.session_state:
    st.session_state["prediction_result"] = predict_credit_risk(st.session_state["current_applicant"])

if "explanation_result" not in st.session_state:
    st.session_state["explanation_result"] = explain_prediction(
        st.session_state["current_applicant"],
        st.session_state["prediction_result"]
    )

if "financial_health_result" not in st.session_state:
    st.session_state["financial_health_result"] = calculate_financial_health(st.session_state["current_applicant"])

if "scenario_result" not in st.session_state:
    st.session_state["scenario_result"] = None

# Synchronize i18n package language
set_current_language(st.session_state["lang"])
curr_lang = st.session_state["lang"]


# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & LANGUAGE SELECTOR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### 💳 **{t('app_title')}**")
    st.caption(f"🛡️ *{t('app_badge')}*")

    st.markdown("---")

    # Language Selector
    st.markdown(f"🌐 **{t('btn_switch_language')}**")
    lang_options = {"en": "🇬🇧 English", "ta": "🇮🇳 தமிழ்", "hi": "🇮🇳 हिन्दी"}
    selected_lang = st.selectbox(
        label="Language Selector",
        options=list(lang_options.keys()),
        format_func=lambda x: lang_options[x],
        index=list(lang_options.keys()).index(curr_lang),
        label_visibility="collapsed",
    )

    if selected_lang != curr_lang:
        st.session_state["lang"] = selected_lang
        set_current_language(selected_lang)
        st.rerun()

    st.markdown("---")

    # Navigation Menu
    if "nav_view" not in st.session_state:
        st.session_state["nav_view"] = "nav_overview"

    nav_options = [
        "nav_overview",
        "nav_login",
        "nav_assess",
        "nav_result",
        "nav_explain",
        "nav_financial_health",
        "nav_simulator",
        "nav_fairness",
        "nav_insights",
    ]
    
    if st.session_state["nav_view"] not in nav_options:
        st.session_state["nav_view"] = "nav_overview"

    nav_selection = st.radio(
        label="Navigation",
        options=nav_options,
        index=nav_options.index(st.session_state["nav_view"]),
        format_func=lambda key: f"{'🏠' if key=='nav_overview' else '🔐' if key=='nav_login' else '📝' if key=='nav_assess' else '📊' if key=='nav_result' else '🔍' if key=='nav_explain' else '💚' if key=='nav_financial_health' else '⚡' if key=='nav_simulator' else '⚖️' if key=='nav_fairness' else '📈'} {'Officer Portal / Sign In' if key=='nav_login' else t(key)}",
        label_visibility="collapsed",
    )
    if nav_selection != st.session_state["nav_view"]:
        st.session_state["nav_view"] = nav_selection
        st.rerun()

    st.markdown("---")
    st.caption("🔒 **Zero Personal Data**: Names, emails, phone numbers, SSN, PAN, Aadhaar are never collected.")


# -----------------------------------------------------------------------------
# VIEW 1: OVERVIEW & CINEMATIC LANDING
# -----------------------------------------------------------------------------
if nav_selection == "nav_overview":
    # Cinematic Hero Section
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #020617 0%, #0F172A 50%, #082F49 100%); color: #FFFFFF; padding: 36px 32px; border-radius: 20px; border: 1px solid #1E293B; margin-bottom: 24px; box-shadow: 0 12px 32px rgba(0,0,0,0.25);">
        <div style="display: inline-block; background: rgba(14, 165, 233, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: #7DD3FC; padding: 4px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; margin-bottom: 16px;">
            ● {t('app_badge')} · ROC-AUC 0.7744 · 30,000 UCI Benchmark Records
        </div>
        <h1 style="font-size: 2.3rem; font-weight: 800; color: #FFFFFF; line-height: 1.2; margin: 0 0 12px 0;">
            {t('overview_hero_title')}
        </h1>
        <p style="font-size: 1.05rem; color: #CBD5E1; line-height: 1.6; max-width: 850px; margin: 0 0 20px 0;">
            {t('overview_hero_desc')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Primary Action CTA Bar
    cta_c1, cta_c2, cta_c3 = st.columns([1.5, 1.2, 1.2])
    with cta_c1:
        if st.button("🚀 **GET STARTED (Sign In & Assess)**", type="primary", use_container_width=True):
            st.session_state["nav_view"] = "nav_login"
            st.rerun()
    with cta_c2:
        if st.button(f"📝 {t('btn_assess_risk')}", use_container_width=True):
            st.session_state["nav_view"] = "nav_assess"
            st.rerun()
    with cta_c3:
        if st.button(f"⚡ {t('btn_explore_what_if')}", use_container_width=True):
            st.session_state["nav_view"] = "nav_simulator"
            st.rerun()

    st.markdown("---")

    # 4-Stage Decision Architecture Journey
    st.markdown("""
    <div style="text-align: center; margin: 16px 0 24px 0;">
        <span style="background: #E0F2FE; color: #0369A1; font-weight: 700; font-size: 0.75rem; padding: 4px 12px; border-radius: 9999px; text-transform: uppercase;">
            Decision Architecture
        </span>
        <h3 style="margin-top: 8px; color: #0F172A; font-weight: 800;">End-to-End Credit Assessment Lifecycle</h3>
    </div>
    """, unsafe_allow_html=True)

    arch1, arch2, arch3, arch4 = st.columns(4)
    with arch1:
        st.markdown("""
        <div class="fintech-card" style="padding: 16px; min-height: 140px;">
            <div style="font-size: 0.8rem; font-weight: 800; color: #0284C7; margin-bottom: 4px;">01 · Ingestion</div>
            <strong style="font-size: 0.9rem; color: #0F172A;">Behavioral Profiling</strong>
            <p style="font-size: 0.8rem; color: #64748B; margin-top: 4px; line-height: 1.4;">Parses 6-mo repayment statuses, bill amounts & paydown velocity.</p>
        </div>
        """, unsafe_allow_html=True)
    with arch2:
        st.markdown("""
        <div class="fintech-card" style="padding: 16px; min-height: 140px;">
            <div style="font-size: 0.8rem; font-weight: 800; color: #10B981; margin-bottom: 4px;">02 · Scoring</div>
            <strong style="font-size: 0.9rem; color: #0F172A;">Random Forest Pipeline</strong>
            <p style="font-size: 0.8rem; color: #64748B; margin-top: 4px; line-height: 1.4;">100-tree ensemble outputs calibrated probability of default.</p>
        </div>
        """, unsafe_allow_html=True)
    with arch3:
        st.markdown("""
        <div class="fintech-card" style="padding: 16px; min-height: 140px;">
            <div style="font-size: 0.8rem; font-weight: 800; color: #F59E0B; margin-bottom: 4px;">03 · Attribution</div>
            <strong style="font-size: 0.9rem; color: #0F172A;">Factor Explainability</strong>
            <p style="font-size: 0.8rem; color: #64748B; margin-top: 4px; line-height: 1.4;">Extracts top risk amplifiers and positive mitigating factors.</p>
        </div>
        """, unsafe_allow_html=True)
    with arch4:
        st.markdown("""
        <div class="fintech-card" style="padding: 16px; min-height: 140px;">
            <div style="font-size: 0.8rem; font-weight: 800; color: #8B5CF6; margin-bottom: 4px;">04 · Counterfactual</div>
            <strong style="font-size: 0.9rem; color: #0F172A;">What-If Simulator</strong>
            <p style="font-size: 0.8rem; color: #64748B; margin-top: 4px; line-height: 1.4;">Tests paydowns & limits through the live production model.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Feature Grid
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header">🤖 {t('overview_card1_title')}</div>
            <p style="color: #475569; font-size: 0.95rem; margin: 0;">{t('overview_card1_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header">💚 {t('overview_card3_title')}</div>
            <p style="color: #475569; font-size: 0.95rem; margin: 0;">{t('overview_card3_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header">🔍 {t('overview_card2_title')}</div>
            <p style="color: #475569; font-size: 0.95rem; margin: 0;">{t('overview_card2_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header">⚡ {t('overview_card4_title')}</div>
            <p style="color: #475569; font-size: 0.95rem; margin: 0;">{t('overview_card4_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick Start Profile Loaders
    st.subheader(f"🚀 {t('overview_quick_start')}")
    q_col1, q_col2, q_col3 = st.columns(3)

    with q_col1:
        if st.button(f"🟢 {t('overview_sample_prime')}", use_container_width=True):
            st.session_state["current_applicant"] = SAMPLE_PRIME.copy()
            st.session_state["prediction_result"] = predict_credit_risk(SAMPLE_PRIME)
            st.session_state["explanation_result"] = explain_prediction(SAMPLE_PRIME, st.session_state["prediction_result"])
            st.session_state["financial_health_result"] = calculate_financial_health(SAMPLE_PRIME)
            st.session_state["scenario_result"] = None
            st.success(f"{t('overview_sample_prime')} loaded!")

    with q_col2:
        if st.button(f"🟡 {t('overview_sample_revolving')}", use_container_width=True):
            st.session_state["current_applicant"] = SAMPLE_REVOLVING.copy()
            st.session_state["prediction_result"] = predict_credit_risk(SAMPLE_REVOLVING)
            st.session_state["explanation_result"] = explain_prediction(SAMPLE_REVOLVING, st.session_state["prediction_result"])
            st.session_state["financial_health_result"] = calculate_financial_health(SAMPLE_REVOLVING)
            st.session_state["scenario_result"] = None
            st.success(f"{t('overview_sample_revolving')} loaded!")

    with q_col3:
        if st.button(f"🔴 {t('overview_sample_delinquent')}", use_container_width=True):
            st.session_state["current_applicant"] = SAMPLE_DELINQUENT.copy()
            st.session_state["prediction_result"] = predict_credit_risk(SAMPLE_DELINQUENT)
            st.session_state["explanation_result"] = explain_prediction(SAMPLE_DELINQUENT, st.session_state["prediction_result"])
            st.session_state["financial_health_result"] = calculate_financial_health(SAMPLE_DELINQUENT)
            st.session_state["scenario_result"] = None
            st.success(f"{t('overview_sample_delinquent')} loaded!")

    st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>⚖️ Educational Disclaimer:</strong> {t('disclaimer_legal')}<br>
        <strong>🔒 Privacy Notice:</strong> {t('disclaimer_privacy')}
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 1.5: OFFICER LOGIN PORTAL
# -----------------------------------------------------------------------------
elif nav_selection == "nav_login":
    st.title("🔐 Credit Intelligence Gateway")
    st.caption("Sign in to initialize secure credit assessment sessions.")

    l_col1, l_col2 = st.columns([1.2, 1.8])

    with l_col1:
        st.markdown("""
        <div style="background: #0F172A; color: white; padding: 24px; border-radius: 12px; border: 1px solid #1E293B;">
            <div style="color: #38BDF8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Security Gateway</div>
            <h3 style="color: white; margin-top: 6px;">Underwriter Portal</h3>
            <p style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">
                Deterministic credit risk evaluation with audited Random Forest ML model, 5-pillar financial health scoring, and counterfactual scenario simulations.
            </p>
            <ul style="font-size: 0.8rem; color: #CBD5E1; padding-left: 16px; margin-top: 12px; line-height: 1.6;">
                <li>Production Machine Learning Engine</li>
                <li>Zero PII Storage Architecture</li>
                <li>Comprehensive Demographic Bias Audit</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with l_col2:
        with st.form("login_form"):
            st.markdown("##### 👤 Enter Security Credentials")
            role_choice = st.selectbox(
                "Operating Persona / Role",
                ["Senior Credit Underwriter (Alex Vance)", "Quantitative Risk Analyst (Dr. Elena Rostova)", "Model Governance Auditor (Marcus Chen)", "Applicant Self-Assessment Mode (Guest)"]
            )
            email_val = st.text_input("Officer ID / Email", "officer.vance@credit-intelligence.ai")
            pass_val = st.text_input("Security Passcode / Token", "••••••••••••", type="password")
            
            c_sub1, c_sub2 = st.columns(2)
            with c_sub1:
                login_btn = st.form_submit_button("🚀 Enter Credit Assessment Engine", type="primary", use_container_width=True)
            with c_sub2:
                guest_btn = st.form_submit_button("⚡ Single-Click Demo Access", use_container_width=True)

            if login_btn or guest_btn:
                st.session_state["nav_view"] = "nav_assess"
                st.success("Session authenticated! Redirecting to Risk Assessment...")
                st.rerun()



# -----------------------------------------------------------------------------
# VIEW 2: RISK ASSESSMENT INPUT FORM
# -----------------------------------------------------------------------------
elif nav_selection == "nav_assess":
    st.title(f"📝 {t('form_title')}")
    st.markdown(f"<p style='color: #64748B;'>{t('form_desc')}</p>", unsafe_allow_html=True)

    applicant = st.session_state["current_applicant"].copy()

    with st.form("risk_assessment_form"):
        # Section 1: Credit Profile & Demographics
        st.markdown(f"<div class='form-section-title'>1. {t('form_sec_credit_profile')}</div>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            limit_bal = st.number_input(
                t("lbl_limit_bal"),
                min_value=10000.0,
                max_value=1000000.0,
                value=float(applicant.get("LIMIT_BAL", 50000.0)),
                step=10000.0,
                help=t("help_limit_bal")
            )
        with col2:
            sex_val = st.selectbox(
                t("lbl_sex"),
                options=[1, 2],
                format_func=lambda x: f"👨 {t('lbl_sex_male')}" if x == 1 else f"👩 {t('lbl_sex_female')}",
                index=0 if applicant.get("SEX", 1) == 1 else 1
            )
        with col3:
            edu_options = {1: t("lbl_edu_grad"), 2: t("lbl_edu_uni"), 3: t("lbl_edu_high"), 4: t("lbl_edu_other")}
            edu_val = st.selectbox(
                t("lbl_education"),
                options=list(edu_options.keys()),
                format_func=lambda x: edu_options.get(x, t("lbl_edu_other")),
                index=list(edu_options.keys()).index(applicant.get("EDUCATION", 2)) if applicant.get("EDUCATION", 2) in edu_options else 1
            )
        with col4:
            marr_options = {1: t("lbl_marr_married"), 2: t("lbl_marr_single"), 3: t("lbl_marr_other")}
            marr_val = st.selectbox(
                t("lbl_marriage"),
                options=list(marr_options.keys()),
                format_func=lambda x: marr_options.get(x, t("lbl_marr_other")),
                index=list(marr_options.keys()).index(applicant.get("MARRIAGE", 2)) if applicant.get("MARRIAGE", 2) in marr_options else 1
            )
        with col5:
            age_val = st.number_input(
                t("lbl_age"),
                min_value=21,
                max_value=79,
                value=int(applicant.get("AGE", 30)),
                step=1,
                help=t("help_age")
            )

        # Section 2: Repayment History (Past 6 Months)
        st.markdown(f"<div class='form-section-title'>2. {t('form_sec_repayment')}</div>", unsafe_allow_html=True)
        pay_cols = st.columns(6)
        pay_labels = [
            ("PAY_0", t("lbl_pay_0")),
            ("PAY_2", t("lbl_pay_2")),
            ("PAY_3", t("lbl_pay_3")),
            ("PAY_4", t("lbl_pay_4")),
            ("PAY_5", t("lbl_pay_5")),
            ("PAY_6", t("lbl_pay_6")),
        ]
        pay_values = {}
        pay_option_map = {
            -2: t("opt_pay_neg2"),
            -1: t("opt_pay_neg1"),
            0: t("opt_pay_0"),
            1: t("opt_pay_1"),
            2: t("opt_pay_2"),
            3: t("opt_pay_3"),
            4: t("opt_pay_4"),
            5: t("opt_pay_5"),
            6: t("opt_pay_6"),
            7: t("opt_pay_7"),
            8: t("opt_pay_8"),
        }

        for i, (k, lbl) in enumerate(pay_labels):
            with pay_cols[i]:
                curr_val = int(applicant.get(k, 0))
                idx = list(pay_option_map.keys()).index(curr_val) if curr_val in pay_option_map else 2
                pay_values[k] = st.selectbox(
                    lbl,
                    options=list(pay_option_map.keys()),
                    format_func=lambda x: pay_option_map[x],
                    index=idx,
                    key=f"input_{k}"
                )

        # Section 3: Billed Statement Amounts
        st.markdown(f"<div class='form-section-title'>3. {t('form_sec_bills')}</div>", unsafe_allow_html=True)
        bill_cols = st.columns(6)
        bill_labels = [
            ("BILL_AMT1", t("lbl_bill_amt1")),
            ("BILL_AMT2", t("lbl_bill_amt2")),
            ("BILL_AMT3", t("lbl_bill_amt3")),
            ("BILL_AMT4", t("lbl_bill_amt4")),
            ("BILL_AMT5", t("lbl_bill_amt5")),
            ("BILL_AMT6", t("lbl_bill_amt6")),
        ]
        bill_values = {}
        for i, (k, lbl) in enumerate(bill_labels):
            with bill_cols[i]:
                bill_values[k] = st.number_input(
                    lbl,
                    min_value=-50000.0,
                    max_value=1000000.0,
                    value=float(applicant.get(k, 10000.0)),
                    step=1000.0,
                    key=f"input_{k}"
                )

        # Section 4: Paid Amounts
        st.markdown(f"<div class='form-section-title'>4. {t('form_sec_payments')}</div>", unsafe_allow_html=True)
        pay_amt_cols = st.columns(6)
        pay_amt_labels = [
            ("PAY_AMT1", t("lbl_pay_amt1")),
            ("PAY_AMT2", t("lbl_pay_amt2")),
            ("PAY_AMT3", t("lbl_pay_amt3")),
            ("PAY_AMT4", t("lbl_pay_amt4")),
            ("PAY_AMT5", t("lbl_pay_amt5")),
            ("PAY_AMT6", t("lbl_pay_amt6")),
        ]
        pay_amt_values = {}
        for i, (k, lbl) in enumerate(pay_amt_labels):
            with pay_amt_cols[i]:
                pay_amt_values[k] = st.number_input(
                    lbl,
                    min_value=0.0,
                    max_value=1000000.0,
                    value=float(applicant.get(k, 2000.0)),
                    step=500.0,
                    key=f"input_{k}"
                )

        submit_btn = st.form_submit_button(f"🚀 {t('btn_run_assessment')}", use_container_width=True)

    if submit_btn:
        new_applicant = {
            "LIMIT_BAL": limit_bal, "SEX": sex_val, "EDUCATION": edu_val, "MARRIAGE": marr_val, "AGE": age_val,
            **pay_values,
            **bill_values,
            **pay_amt_values,
        }
        with st.spinner(t("msg_calculating")):
            pred = predict_credit_risk(new_applicant)
            expl = explain_prediction(new_applicant, pred)
            fhi = calculate_financial_health(new_applicant)

            st.session_state["current_applicant"] = new_applicant
            st.session_state["prediction_result"] = pred
            st.session_state["explanation_result"] = expl
            st.session_state["financial_health_result"] = fhi
            st.session_state["scenario_result"] = None

        st.success(t("msg_success_calculated"))


# -----------------------------------------------------------------------------
# VIEW 3: ASSESSMENT RESULT SCREEN
# -----------------------------------------------------------------------------
elif nav_selection == "nav_result":
    st.title(f"📊 {t('result_header')}")

    pred = st.session_state["prediction_result"]
    fhi = st.session_state["financial_health_result"]

    prob_default_pct = pred["model_estimated_likelihood_pct"]
    prob_non_default_pct = pred["model_estimated_non_default_pct"]
    risk_level = pred["risk_level"]

    if risk_level == "LOW RISK":
        badge_html = f"<span class='badge-risk-low'>🟢 {t('risk_tier_low')}</span>"
        color_code = "#10B981"
    elif risk_level == "MEDIUM RISK":
        badge_html = f"<span class='badge-risk-med'>🟡 {t('risk_tier_medium')}</span>"
        color_code = "#F59E0B"
    else:
        badge_html = f"<span class='badge-risk-high'>🔴 {t('risk_tier_high')}</span>"
        color_code = "#EF4444"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{t('result_risk_level')}</div>
            <div style="margin: 12px 0;">{badge_html}</div>
            <div class="metric-sub">{t('result_binary_decision')}: <strong>{t('pred_class_1') if pred['predicted_class']==1 else t('pred_class_0')}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{t('result_likelihood')}</div>
            <div class="metric-value" style="color: {color_code};">{prob_default_pct:.2f}%</div>
            <div class="metric-sub">{t('result_non_default_likelihood')}: {prob_non_default_pct:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{t('fhi_score_title')}</div>
            <div class="metric-value">{fhi['score']} <span style="font-size: 1.1rem; color: #64748B;">/ 100</span></div>
            <div class="metric-sub">Rating: <strong>{fhi['label']}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    # Narrative Summary
    st.markdown(f"""
    <div class="fintech-card" style="margin-top: 16px;">
        <div class="fintech-card-header">📋 {t('result_summary')}</div>
        <p style="font-size: 1.05rem; color: #1E293B; line-height: 1.6; margin: 0;">{st.session_state['explanation_result']['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Disclaimers
    st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>⚖️ {t('insights_disclaimer_title')}:</strong> {t('disclaimer_legal')}<br>
        <strong>📈 Calibration Notice:</strong> {t('disclaimer_calibration')}
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 4: WHY THIS RESULT? (EXPLAINABILITY)
# -----------------------------------------------------------------------------
elif nav_selection == "nav_explain":
    st.title(f"🔍 {t('explain_header')}")
    st.caption(t("explain_subtitle"))

    expl = st.session_state["explanation_result"]
    risk_factors = expl.get("top_risk_factors", [])
    positive_factors = expl.get("positive_factors", [])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header" style="color: #991B1B;">⚠️ {t('explain_risk_factors_title')}</div>
        """, unsafe_allow_html=True)

        if not risk_factors:
            st.info(t("explain_no_risk_factors"))
        else:
            for factor in risk_factors:
                st.markdown(f"""
                <div style="background: #FEF2F2; border-left: 4px solid #EF4444; padding: 10px 14px; border-radius: 6px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; font-weight: 700; color: #991B1B;">
                        <span>{factor['human_label']}</span>
                        <span>{factor['display_value']}</span>
                    </div>
                    <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #7F1D1D;">{factor['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header" style="color: #065F46;">🛡️ {t('explain_positive_factors_title')}</div>
        """, unsafe_allow_html=True)

        if not positive_factors:
            st.info(t("explain_no_positive_factors"))
        else:
            for factor in positive_factors:
                st.markdown(f"""
                <div style="background: #ECFDF5; border-left: 4px solid #10B981; padding: 10px 14px; border-radius: 6px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; font-weight: 700; color: #065F46;">
                        <span>{factor['human_label']}</span>
                        <span>{factor['display_value']}</span>
                    </div>
                    <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #064E3B;">{factor['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>📌 Association Notice:</strong> {t('disclaimer_association')}
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 5: FINANCIAL HEALTH INDICATOR (FHI-5)
# -----------------------------------------------------------------------------
elif nav_selection == "nav_financial_health":
    st.title(f"💚 {t('fhi_header')}")
    st.caption(t("fhi_subtitle"))

    fhi = st.session_state["financial_health_result"]
    score = fhi["score"]
    label = fhi["label"]
    components = fhi["components"]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"""
        <div class="metric-container" style="padding: 36px 20px;">
            <div class="metric-label">{t('fhi_score_title')}</div>
            <div class="metric-value" style="font-size: 3.2rem; color: #0284C7;">{score}</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #1E293B; margin-top: 8px;">{label}</div>
            <div style="margin-top: 14px; font-size: 0.85rem; color: #64748B;">{fhi['summary']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='fintech-card'><div class='fintech-card-header'>📊 5 Core Financial Health Pillars</div>", unsafe_allow_html=True)

        for pillar_key, comp in components.items():
            pillar_name = comp["name"]
            pillar_score = comp["score"]
            pillar_status = comp["status"]
            pillar_weight = comp["weight"] * 100

            st.markdown(f"""
            <div class="pillar-row">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-weight: 700; color: #0F172A;">{pillar_name} ({pillar_weight:.0f}% weight)</span>
                    <span style="font-weight: 800; color: #0284C7;">{pillar_score:.0f} / 100 — <span style="font-size: 0.85rem; color: #475569;">{pillar_status}</span></span>
                </div>
                <div style="font-size: 0.85rem; color: #64748B; margin-top: 4px;">{comp['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>⚖️ Educational Heuristic Notice:</strong> {t('disclaimer_legal')} The Financial Health Indicator is NOT a FICO score or credit bureau score.
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 6: WHAT-IF SCENARIO SIMULATOR (FLAGSHIP WOW EXPERIENCE)
# -----------------------------------------------------------------------------
elif nav_selection == "nav_simulator":
    st.title(f"⚡ {t('sim_header')}")
    st.caption(t("sim_subtitle"))

    applicant = st.session_state["current_applicant"].copy()
    current_pred = st.session_state["prediction_result"]
    current_fhi = st.session_state["financial_health_result"]

    # 1-Click Preset Actions
    st.markdown(f"##### 🎯 {t('sim_presets_title')}")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    with p_col1:
        if st.button(f"🛠️ {t('sim_preset_remediate')}", use_container_width=True):
            st.session_state["scenario_result"] = simulate_repayment_remediation(applicant)
            st.success("Remediation preset simulated!")

    with p_col2:
        if st.button(f"📉 {t('sim_preset_paydown_50')}", use_container_width=True):
            st.session_state["scenario_result"] = simulate_balance_paydown(applicant, paydown_fraction=0.50)
            st.success("50% Balance Paydown simulated!")

    with p_col3:
        if st.button(f"📉 {t('sim_preset_paydown_80')}", use_container_width=True):
            st.session_state["scenario_result"] = simulate_balance_paydown(applicant, paydown_fraction=0.80)
            st.success("80% Balance Paydown simulated!")

    with p_col4:
        if st.button(f"📈 {t('sim_preset_limit_inc')}", use_container_width=True):
            new_limit = applicant.get("LIMIT_BAL", 50000.0) * 1.5
            st.session_state["scenario_result"] = simulate_credit_limit_increase(applicant, new_limit=new_limit)
            st.success("Credit Limit increase simulated!")

    st.markdown("---")

    # 3-Panel Workspace
    panel_col1, panel_col2 = st.columns([1, 1.4])

    with panel_col1:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header">🎛️ {t('sim_panel_controls')}</div>
        """, unsafe_allow_html=True)

        with st.form("custom_scenario_form"):
            sim_limit = st.number_input(
                t("lbl_limit_bal"),
                min_value=10000.0,
                max_value=1000000.0,
                value=float(applicant.get("LIMIT_BAL", 50000.0)),
                step=10000.0,
            )

            st.caption("Recent Repayment Status:")
            sim_pay0 = st.slider("September Status (PAY_0)", min_value=-2, max_value=8, value=int(applicant.get("PAY_0", 0)))
            sim_pay2 = st.slider("August Status (PAY_2)", min_value=-2, max_value=8, value=int(applicant.get("PAY_2", 0)))

            st.caption("Latest Statement & Payment (NT$):")
            sim_bill1 = st.number_input("September Bill (BILL_AMT1)", value=float(applicant.get("BILL_AMT1", 10000.0)), step=1000.0)
            sim_payamt1 = st.number_input("September Paid Amount (PAY_AMT1)", value=float(applicant.get("PAY_AMT1", 2000.0)), step=500.0)

            run_sim_btn = st.form_submit_button(f"⚡ {t('btn_simulate_scenario')}", use_container_width=True)

        if run_sim_btn:
            mods = {
                "LIMIT_BAL": sim_limit,
                "PAY_0": sim_pay0,
                "PAY_2": sim_pay2,
                "BILL_AMT1": sim_bill1,
                "PAY_AMT1": sim_payamt1,
            }
            with st.spinner(t("msg_simulating")):
                st.session_state["scenario_result"] = simulate_scenario(applicant, modifications=mods)
            st.success(t("msg_success_simulated"))

        st.markdown("</div>", unsafe_allow_html=True)

    with panel_col2:
        sim_res = st.session_state["scenario_result"]

        if sim_res is None:
            st.info("👈 Select a preset above or adjust scenario controls and click 'Run Simulation' to observe model responses.")
        else:
            comp = sim_res["comparison"]
            curr_prob = sim_res["current"]["default_probability"] * 100
            scen_prob = sim_res["scenario"]["default_probability"] * 100
            p_delta = comp["default_probability_delta"] * 100

            curr_fhi = sim_res["current"]["financial_health"]["score"]
            scen_fhi = sim_res["scenario"]["financial_health"]["score"]
            fhi_delta = comp["financial_health_delta"]

            st.markdown(f"""
            <div class="fintech-card">
                <div class="fintech-card-header">📊 {t('sim_panel_comparison')}</div>
            """, unsafe_allow_html=True)

            c_box1, c_box2 = st.columns(2)

            with c_box1:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">{t('sim_lbl_prob_delta')}</div>
                    <div class="metric-value" style="color: {'#10B981' if p_delta < 0 else '#EF4444' if p_delta > 0 else '#64748B'}; font-size: 1.9rem;">
                        {'+' if p_delta > 0 else ''}{p_delta:.2f}% pts
                    </div>
                    <div class="metric-sub">{curr_prob:.1f}% → <strong>{scen_prob:.1f}%</strong> ({comp['risk_direction']})</div>
                </div>
                """, unsafe_allow_html=True)

            with c_box2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">{t('sim_lbl_fhi_delta')}</div>
                    <div class="metric-value" style="color: {'#10B981' if fhi_delta > 0 else '#EF4444' if fhi_delta < 0 else '#64748B'}; font-size: 1.9rem;">
                        {'+' if fhi_delta > 0 else ''}{fhi_delta} pts
                    </div>
                    <div class="metric-sub">{curr_fhi} → <strong>{scen_fhi} / 100</strong> ({comp['financial_health_direction']})</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px; margin: 16px 0; font-size: 0.95rem; line-height: 1.5; color: #1E293B;">
                <strong>📋 Model Simulation Narrative:</strong><br>{comp['summary']}
            </div>
            """, unsafe_allow_html=True)

            # Resolved Factors
            res_factors = comp.get("risk_factors_resolved", [])
            gained_factors = comp.get("positive_factors_gained", [])

            if res_factors:
                st.markdown(f"**🎉 {t('sim_resolved_factors_title')}:**")
                tags = " ".join([f"<span class='badge-risk-low' style='margin-right: 6px;'>✓ {f['human_label']}</span>" for f in res_factors])
                st.markdown(f"<div style='margin-bottom: 12px;'>{tags}</div>", unsafe_allow_html=True)

            if gained_factors:
                st.markdown(f"**🛡️ {t('sim_gained_strengths_title')}:**")
                tags = " ".join([f"<span class='badge-risk-low' style='margin-right: 6px;'>+ {f['human_label']}</span>" for f in gained_factors])
                st.markdown(f"<div style='margin-bottom: 12px;'>{tags}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>⚖️ Hypothetical Simulation Disclaimer:</strong> {t('disclaimer_simulation')}
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 7: FAIRNESS & DEMOGRAPHIC BIAS AUDIT
# -----------------------------------------------------------------------------
elif nav_selection == "nav_fairness":
    st.title(f"⚖️ {t('fairness_title')}")
    st.caption(t("fairness_subtitle"))

    @st.cache_data(show_spinner=False)
    def get_cached_fairness_report():
        df_bench = get_cached_dataset()
        df_eval = df_bench.sample(n=min(len(df_bench), 5000), random_state=42).copy()
        preds = []
        probs = []
        for _, row in df_eval.iterrows():
            r = predict_credit_risk(row.to_dict())
            preds.append(r["prediction"])
            probs.append(r["default_probability"])
        df_eval["prediction"] = preds
        df_eval["default_probability"] = probs
        return generate_full_fairness_report(df_eval)

    with st.spinner("Auditing demographic fairness across benchmark cohorts..."):
        report = get_cached_fairness_report()

    fairness_tabs = st.tabs([
        f"📊 {t('fairness_tab_metrics')}",
        f"📁 {t('fairness_tab_overview')}",
        f"⚖️ {t('fairness_tab_limitations')}"
    ])

    with fairness_tabs[0]:
        st.markdown(f"#### {t('fairness_select_attribute')}")
        attr_opts = {
            "SEX": "Gender / Biological Sex (SEX)",
            "EDUCATION": "Education Level (EDUCATION)",
            "MARRIAGE": "Marital Status (MARRIAGE)",
            "AGE_GROUP": "Age Cohort (AGE_GROUP)",
        }
        selected_attr = st.selectbox(
            "Demographic Variable",
            options=list(attr_opts.keys()),
            format_func=lambda x: attr_opts[x],
            label_visibility="collapsed",
        )

        attr_data = report["attributes"].get(selected_attr, {})
        ref_label = attr_data.get("reference_group_label", "Baseline")

        st.info(f"**{t('fairness_reference_group')}** `{ref_label}` — {attr_data.get('description', '')}")

        groups_dict = attr_data.get("groups", {})
        table_rows = []
        for g_key, g_val in groups_dict.items():
            disp = g_val.get("disparities_vs_baseline", {})
            table_rows.append({
                "Cohort": g_val.get("group_label", str(g_key)),
                "Sample Size (n)": g_val.get("sample_count", 0),
                "Base Default Rate": f"{g_val.get('base_rate', 0.0) * 100:.1f}%",
                "Selection Rate (PPR)": f"{g_val.get('positive_prediction_rate', 0.0) * 100:.1f}%",
                "Recall (TPR)": f"{g_val.get('recall', 0.0) * 100:.1f}%" if g_val.get("recall") is not None else "N/A",
                "FPR": f"{g_val.get('false_positive_rate', 0.0) * 100:.1f}%" if g_val.get("false_positive_rate") is not None else "N/A",
                "Accuracy": f"{g_val.get('accuracy', 0.0) * 100:.1f}%" if g_val.get("accuracy") is not None else "N/A",
                "PPR Gap vs Ref": f"{disp.get('positive_prediction_rate_diff', 0.0) * 100:+.1f}% pts" if disp else "Reference",
            })

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        summary = attr_data.get("summary", {})
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Max Selection Rate Gap", f"{summary.get('max_selection_rate_gap', 0.0)*100:.1f}% pts")
        with c2:
            st.metric("Max Recall (TPR) Gap", f"{summary.get('max_recall_gap', 0.0)*100:.1f}% pts")
        with c3:
            st.metric("Max FPR Gap", f"{summary.get('max_fpr_gap', 0.0)*100:.1f}% pts")

    with fairness_tabs[1]:
        ds_audit = report.get("dataset_audit", {})
        st.markdown(f"#### 🔍 {t('fairness_tab_overview')}")
        st.markdown(f"**{t('fairness_dataset_total')}:** `{ds_audit.get('total_evaluated_samples', 0):,} records evaluated`")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="fintech-card">
                <div class="fintech-card-header">✅ {t('fairness_available_demographics')}</div>
                <ul style="color: #334155; font-size: 0.9rem; line-height: 1.8;">
                    <li><strong>SEX:</strong> Male, Female</li>
                    <li><strong>EDUCATION:</strong> Graduate School, University, High School, Others</li>
                    <li><strong>MARRIAGE:</strong> Married, Single, Divorced/Other</li>
                    <li><strong>AGE:</strong> Discretized 21–29, 30–39, 40–49, 50–59, 60+</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="fintech-card">
                <div class="fintech-card-header">⚠️ {t('fairness_unavailable_demographics')}</div>
                <ul style="color: #991B1B; font-size: 0.9rem; line-height: 1.8;">
                    <li><strong>Race & Ethnicity:</strong> Completely absent from dataset.</li>
                    <li><strong>Geographic Location:</strong> Postal codes / region absent.</li>
                    <li><strong>Annual Income:</strong> Direct income absent (credit limit is proxy).</li>
                    <li><strong>Family Dependents & Religion:</strong> Absent.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with fairness_tabs[2]:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header">🏛️ Core Ethical Principles & Caveats</div>
            <ul style="color: #334155; font-size: 0.95rem; line-height: 1.8;">
                <li><strong>{t('fairness_principle_1')}</strong></li>
                <li><strong>{t('fairness_principle_2')}</strong></li>
                <li><strong>{t('fairness_principle_3')}</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>⚖️ Fairness Audit Disclaimer:</strong> {report.get('global_disclaimer', '')}
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 8: MODEL INSIGHTS, METHODOLOGY & GOVERNANCE
# -----------------------------------------------------------------------------
elif nav_selection == "nav_insights":
    st.title(f"📈 {t('insights_header')}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header">🏛️ {t('insights_champion_title')}</div>
            <p style="color: #475569; font-size: 0.95rem;">{t('insights_champion_desc')}</p>
            <ul style="color: #334155; font-size: 0.9rem; line-height: 1.8;">
                <li><strong>Dataset:</strong> UCI Credit Card Default (30,000 empirical borrower profiles).</li>
                <li><strong>Preprocessing:</strong> Zero-leakage median imputation, standard scaling, and one-hot encoding.</li>
                <li><strong>Feature Engineering:</strong> 16 custom credit metrics (delinquency trends, payment-to-bill ratios, revolving utilization).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-card-header">🎯 {t('insights_metrics_title')}</div>
            <ul style="color: #334155; font-size: 0.95rem; line-height: 1.9; list-style-type: square;">
                <li>{t('insights_metric_auc')}</li>
                <li>{t('insights_metric_acc')}</li>
                <li>{t('insights_metric_brier')}</li>
                <li>{t('insights_metric_f1')}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Global Feature Importance Chart
    st.markdown(f"""
    <div class="fintech-card">
        <div class="fintech-card-header">📊 {t('insights_feature_imp_title')}</div>
    """, unsafe_allow_html=True)

    feature_imp_data = pd.DataFrame({
        "Feature": [
            "PAY_0 (Recent Payment Status)",
            "UTILIZATION_AVG (6-Mo Avg Utilization)",
            "PAY_2 (1-Mo Prior Status)",
            "BILL_AMT1 (Recent Statement Bill)",
            "LIMIT_BAL (Credit Limit)",
            "PAY_AMT1 (Recent Paid Amount)",
            "PAY_TO_BILL_1 (Payment-to-Bill Ratio)",
            "AGE (Borrower Age)",
        ],
        "Gini Importance": [0.185, 0.082, 0.075, 0.068, 0.059, 0.054, 0.048, 0.042]
    }).sort_values("Gini Importance", ascending=True)

    st.bar_chart(feature_imp_data.set_index("Feature"), horizontal=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>⚖️ Governance & Limitations Notice:</strong> {t('disclaimer_legal')}<br>
        <strong>🔒 Privacy Commitment:</strong> {t('disclaimer_privacy')}
    </div>
    """, unsafe_allow_html=True)
