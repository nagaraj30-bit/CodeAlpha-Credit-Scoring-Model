# Credit Scoring Model — Credit Risk Assessment, Financial Health & Scenario Engine

An educational machine learning credit risk assessment and human-readable explainability system trained on the UCI Default of Credit Card Clients dataset (30,000 records).

---

## 1. System Architecture

```
Raw Applicant Input (23 bureau features)
      ↓
CreditFeatureEngineer (16 domain features)
      ↓
ColumnTransformer (Median Imputer + Scaler + OHE)
      ↓
Random Forest Classifier (Production Champion)
      ↓
Prediction Output & Probabilities (predict.py)
      ↓
Deterministic Explainability Layer (risk_reasons.py)
      ↓
Financial Health Indicator Engine (financial_health.py)
      ↓
What-If Scenario Simulator (scenario_simulator.py)
```

---

## 2. Prediction Layer (`src/predict.py`)

- **Inference API**: `predict_credit_risk(input_data, pipeline_path="models/credit_pipeline.pkl")`
- **Input Validation**: Accepts dictionary, pandas Series, or DataFrame; safely imputes missing optional inputs and ignores unseen categorical levels (`handle_unknown="ignore"`).
- **Single Source of Truth**: Passes raw applicant data through the saved production pipeline artifact (`models/credit_pipeline.pkl`) without duplicating preprocessing logic.
- **Output Schema**:
  - `predicted_class`: Binary decision (`0` = Non-Default, `1` = Default)
  - `predicted_label`: Text label (`"Non-Default"` or `"Default"`)
  - `default_probability`: Model output score in `[0.0, 1.0]`
  - `non_default_probability`: Complementary score `1.0 - default_probability`
  - `risk_level`: Deterministic presentation tier (`"LOW RISK"`, `"MEDIUM RISK"`, or `"HIGH RISK"`)

### Presentation Risk Tiers
- **Low Risk**: $P(\text{Default}) < 0.20$
- **Medium Risk**: $0.20 \le P(\text{Default}) < 0.50$
- **High Risk**: $P(\text{Default}) \ge 0.50$ (predicted positive for default at binary threshold 0.50)

*Note: These tiers are a presentation layer for educational clarity and do not represent statutory credit bureau or banking ratings.*

---

## 3. Explainability Layer (`src/risk_reasons.py`)

- **Explainability API**: `explain_prediction(input_data, prediction_result=None)`
- **Deterministic Evaluation**: Derives explanations from actual applicant features, domain rules, and global Random Forest Gini feature importances.
- **No Generative AI / LLMs**: Fully deterministic, reproducible, and transparent.
- **Bidirectional Analysis**:
  - **Risk Drivers**: Identifies repayment delays (`PAY_0`..`PAY_6`), elevated credit utilization, low payment-to-bill coverage, and accumulating unpaid balances.
  - **Credit Strengths**: Identifies on-time repayment history, zero delinquent billing cycles, low revolving credit utilization, and high repayment adequacy.
- **Financial Terminology**: Maps technical variable names (e.g., `PAY_0`, `UTILIZATION_AVG`, `DEFICIT_TO_LIMIT`) to human-friendly financial concepts.

---

## 4. Financial Health Indicator (`src/financial_health.py`)

### Methodology & Calculation
The **Financial Health Indicator (FHI-5)** is a transparent, deterministic heuristic score ($0–100$) derived strictly from empirical credit bureau variables present in the UCI dataset. It assesses 5 fundamental financial health pillars:

1. **Payment Timeliness & Delinquency History (35% weight)**:
   - Evaluates `PAY_0`, `MAX_DELINQUENCY`, `NUM_DELINQUENT_MONTHS`, and `AVG_DELAY_MONTHS`.
   - On-time track records receive maximum points; active multi-month delays apply proportional penalties.
2. **Revolving Credit Utilization (25% weight)**:
   - Evaluates composite utilization: $60\% \times \text{UTILIZATION\_RECENT} + 40\% \times \text{UTILIZATION\_AVG}$.
   - Optimal range ($<30\%$) receives 85–100 points; ratios $>90\%$ scale down to 0 points.
3. **Repayment Adequacy (20% weight)**:
   - Evaluates payment-to-bill coverage: $60\% \times \text{PAY\_TO\_BILL\_1} + 40\% \times \text{PAY\_TO\_BILL\_AVG}$.
   - Full statement balance payoffs receive 100 points; minimum-only payments ($<20\%$) receive 15–45 points.
4. **Debt & Net Deficit Burden (15% weight)**:
   - Evaluates accumulated unpaid deficit (`NET_DEFICIT`) relative to credit limit (`DEFICIT_TO_LIMIT`).
   - Managed/negative deficits receive 100 points; deficits exceeding total credit line scale down to 0–15 points.
5. **Account Trajectory & Momentum (5% weight)**:
   - Evaluates delinquency trend direction (`DELINQUENCY_TREND`) and balance expansion trajectory (`BILL_GROWTH_TREND`).

### Presentation Tiers:
- **80 – 100**: **EXCELLENT** (Disciplined credit habits, low revolving debt, zero delinquencies)
- **65 – 79**: **GOOD** (Controlled balances, generally timely repayments, manageable debt)
- **50 – 64**: **FAIR** (Elevated utilization, occasional payment friction, or high revolving balance)
- **0 – 49**: **POOR / AT RISK** (Active payment delays, heavy debt burden, or low payment adequacy)

*Note: The Financial Health Indicator is an educational heuristic. It is NOT an official credit score (FICO/VantageScore), a bank score, or a loan approval decision.*

---

## 5. What-If Scenario Simulator (`src/scenario_simulator.py`)

### Overview
The What-If Simulator reruns the **exact same production ML pipeline** (`models/credit_pipeline.pkl`) on modified inputs to demonstrate how model risk estimates and financial health scores respond to hypothetical financial changes.

### Supported Scenario Variables
Only empirical variables present in the UCI dataset can be modified:
- `LIMIT_BAL`: Approved credit line
- `PAY_0` .. `PAY_6`: Repayment timeliness statuses
- `BILL_AMT1` .. `BILL_AMT6`: Statement bill amounts
- `PAY_AMT1` .. `PAY_AMT6`: Cash payment amounts

### Comparison Outputs
- **Continuous Deltas**: $\Delta P(\text{Default})$ and $\Delta \text{Financial Health Score}$.
- **Risk Tier Transition**: e.g., `HIGH RISK → MEDIUM RISK`.
- **Dynamic Factor Resolution**: Tracks resolved risk factors, newly introduced risk drivers, and gained positive strengths.
- **Component-Level Comparison**: Side-by-side breakdown of all 5 financial health pillars.

---

## 6. Fairness & Demographic Bias Audit (`src/fairness.py`)

- **Empirical Group-Level Metrics**: Evaluates Selection Rate (PPR), Base Default Rate, Recall (TPR), False Positive Rate (FPR), False Negative Rate (FNR), Precision (PPV), and Accuracy across demographic cohorts.
- **Available Demographic Variables**:
  - `SEX`: Gender (Male / Female)
  - `EDUCATION`: Graduate School, University, High School, Others
  - `MARRIAGE`: Married, Single, Divorced/Other
  - `AGE_GROUP`: Discretized cohorts (21–29, 30–39, 40–49, 50–59, 60+)
- **Disparity & Ratio Analysis**: Calculates group difference ($\Delta$) and selection ratio against established baseline reference groups.
- **Small Cohort Reliability Guards**: Highlights statistical instability flags when evaluating small subgroup sample sizes ($n < 300$).
- **Data Gap & Demographic Absence Transparency**: Explicitly documents missing attributes in the UCI dataset (Race, Ethnicity, Geography, Income, Dependents, Religion).
- **Core Ethical Principles**:
  - *No Claim of Absolute Fairness*: Explicitly recognizes the inherent mathematical trade-offs among fairness definitions.
  - *Fairness Through Blindness Fallacy*: Explains why removing demographic fields from training does not guarantee equitable outcomes due to strong correlated financial proxies.

---

## 7. Multilingual Infrastructure (`src/i18n/`)

- **Supported Languages**: English (`en`), தமிழ் / Tamil (`ta`), हिन्दी / Hindi (`hi`).
- **Mathematical Language Invariance**: Ensures that ML model predictions, probabilities, Financial Health scores, scenario deltas, and fairness metrics are 100% identical regardless of the active UI language.
- **Pure Unicode Safety**: Complete static phrase dictionaries with no runtime LLM dependencies or translation hallucination.

---

## 8. Dataset & Currency Context

- **Source Dataset**: UCI Default of Credit Card Clients Dataset (30,000 empirical cardholder records from Taiwan).
- **Currency Context**: All monetary values (`LIMIT_BAL`, `BILL_AMT1`..`BILL_AMT6`, `PAY_AMT1`..`PAY_AMT6`) are denominated in **New Taiwan Dollars (NT$ / NTD / TWD)**.
- **Conversion Context**: 1 USD $\approx$ 30–32 NTD (for scale context: NT$ 100,000 $\approx$ USD 3,100).

---

## 9. Important Limitations & Disclaimers

1. **Hypothetical Simulation Notice**:
   > *"The simulator demonstrates how the model's estimated risk changes under hypothetical input conditions. It does not predict guaranteed future outcomes or loan approval."*
2. **Probability Calibration**:
   > *"Model-estimated default likelihood is the model's output score from `predict_proba()`. This value has not been independently calibrated as a real-world empirical probability."*
3. **Global Association vs. Individual Causality**:
   > *"Model feature importance (Gini importance) indicates global statistical association across the training dataset. It reflects the model's reliance on each factor and does not prove that a specific variable caused an individual applicant's prediction."*
4. **Privacy Protection**:
   - The system strictly requires only model credit attributes.
   - Sensitive personal information (Name, Phone, Email, SSN, PAN, Aadhaar, Bank Account, Passwords) is never collected or stored.
5. **Educational Disclaimer**:
   - This application is an educational machine-learning demonstration and is **not an official credit score, loan underwriting decision, or financial advice**.

---

## 10. Running Tests & Quality Verification

Execute the comprehensive automated test suite:
```bash
python3 -m unittest discover tests
# or using pytest
pytest -v
```
- `tests/test_data_preparation.py`: Data loader, schema integrity, and zero leakage validation (7 tests).
- `tests/test_model.py`: Model training, serialization, and metric benchmarks (5 tests).
- `tests/test_prediction.py`: Prediction API, probability bounds, edge cases, explainability, extreme values, empty dicts, and privacy validation (12 tests).
- `tests/test_financial_health.py`: Financial Health Indicator calculations, weights, edge cases, and schema validation (10 tests).
- `tests/test_scenario_simulator.py`: What-If Simulator pipeline reuse, continuous deltas, factor tracking, and safety language (10 tests).
- `tests/test_fairness.py`: Group statistics, zero-denominator safety, sample thresholds, disparity calculations, and demographic audits (7 tests).
- `tests/test_i18n.py`: Internationalization, language switching, unicode safety, prediction invariance, and translation completeness (9 tests).
- **Total**: 60 unit & integration tests passing (100% green).

