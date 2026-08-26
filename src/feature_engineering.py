"""
Credit Scoring Model — Feature Engineering Layer
=================================================
Human-Centered Machine Learning for Credit Risk Analysis.
Creates financially meaningful, domain-grounded engineered features from historical credit records.
All calculations are strictly deterministic, rule-based, and handle numerical edge cases safely.
"""

from typing import List, Optional
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CreditFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Scikit-Learn compatible Transformer for domain-specific Credit Risk Feature Engineering.
    
    Transforms raw credit bureau and statement columns into financially interpretable indicators:
    1. Credit Utilization Ratios (Recent & 6-month average)
    2. Payment-to-Bill Ratios (Repayment adequacy)
    3. Delinquency Aggregations (Max delay, Delinquent month count, Repayment trend)
    4. Debt Burden & Net Deficit (Cumulative debt growth relative to limit)
    """

    def __init__(self, include_raw_features: bool = True):
        self.include_raw_features = include_raw_features
        self.engineered_feature_names_: List[str] = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Fit method (stateless feature transformer)."""
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Execute feature engineering on the input DataFrame.
        
        Args:
            X: Input DataFrame containing standardized credit features.
            
        Returns:
            pd.DataFrame: Transformed DataFrame with newly engineered features.
        """
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
            
        df = X.copy()
        
        # -------------------------------------------------------------
        # 1. CREDIT UTILIZATION RATIOS
        # -------------------------------------------------------------
        # Formula: Utilization_i = max(BILL_AMT_i, 0) / max(LIMIT_BAL, 1.0)
        # Financial Meaning: Fraction of available credit revolving balance.
        # High utilization (>80%) signals liquidity strain.
        # Edge Case: Negative bill amounts (refunds/overpayments) are floored at 0.
        # Zero limit is guarded by floor of 1.0.
        limit = np.maximum(df["LIMIT_BAL"].values, 1.0)
        
        bill_cols = [f"BILL_AMT{i}" for i in range(1, 7)]
        pay_cols = [f"PAY_AMT{i}" for i in range(1, 7)]
        status_cols = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
        
        # Recent utilization (Month 1 - September)
        df["UTILIZATION_RECENT"] = np.clip(np.maximum(df["BILL_AMT1"].values, 0.0) / limit, 0.0, 5.0)
        
        # 6-Month Average Utilization
        total_positive_bills = np.sum([np.maximum(df[col].values, 0.0) for col in bill_cols], axis=0)
        df["UTILIZATION_AVG"] = np.clip((total_positive_bills / 6.0) / limit, 0.0, 5.0)
        
        # Max Utilization across all 6 months
        max_bills = np.maximum.reduce([np.maximum(df[col].values, 0.0) for col in bill_cols])
        df["UTILIZATION_MAX"] = np.clip(max_bills / limit, 0.0, 5.0)

        # -------------------------------------------------------------
        # 2. PAYMENT-TO-BILL RATIOS (Repayment Adequacy)
        # -------------------------------------------------------------
        # Formula: Pay_Ratio_i = PAY_AMT_i / max(BILL_AMT_{i+1}, 1.0)
        # Financial Meaning: Measures whether the client pays off statement balances or pays minimums.
        # Ratio >= 1.0 implies full payoff; < 0.1 implies minimum/partial payments.
        # Edge Case: If previous bill is <= 0 (no balance due), ratio is set to 1.0 (satisfactory).
        # Ratios are capped at 2.0 to prevent outlier distortion.
        def _calc_pay_ratio(pay_amt: np.ndarray, prev_bill_amt: np.ndarray) -> np.ndarray:
            no_balance_mask = prev_bill_amt <= 0
            ratio = np.where(
                no_balance_mask,
                1.0,  # No debt was due, payment adequacy is 100%
                np.clip(pay_amt / np.maximum(prev_bill_amt, 1.0), 0.0, 2.0)
            )
            return ratio

        df["PAY_TO_BILL_1"] = _calc_pay_ratio(df["PAY_AMT1"].values, df["BILL_AMT2"].values)
        df["PAY_TO_BILL_2"] = _calc_pay_ratio(df["PAY_AMT2"].values, df["BILL_AMT3"].values)
        df["PAY_TO_BILL_3"] = _calc_pay_ratio(df["PAY_AMT3"].values, df["BILL_AMT4"].values)
        
        # Average Payment-to-Bill Ratio across top 3 recent cycles
        df["PAY_TO_BILL_AVG"] = (df["PAY_TO_BILL_1"] + df["PAY_TO_BILL_2"] + df["PAY_TO_BILL_3"]) / 3.0

        # -------------------------------------------------------------
        # 3. DELINQUENCY AGGREGATIONS & BEHAVIORAL TRENDS
        # -------------------------------------------------------------
        # Raw Status Codes: -2=No consumption, -1=Paid in full, 0=Revolving, 1-8=Months delayed
        # Max Delinquency: Highest past-due status observed over the 6 months
        df["MAX_DELINQUENCY"] = np.maximum.reduce([df[col].values for col in status_cols])
        
        # Total Delinquent Months: Count of months where status > 0 (past due)
        delinquent_counts = np.sum([np.where(df[col].values > 0, 1, 0) for col in status_cols], axis=0)
        df["NUM_DELINQUENT_MONTHS"] = delinquent_counts
        
        # Average Delay Severity (considering only positive delay months)
        positive_delays = np.sum([np.maximum(df[col].values, 0) for col in status_cols], axis=0)
        df["AVG_DELAY_MONTHS"] = positive_delays / 6.0

        # Delinquency Trend (Recent vs Historical): PAY_0 - PAY_6
        # Financial Meaning: Positive value indicates worsening credit behavior; negative indicates recovery.
        df["DELINQUENCY_TREND"] = df["PAY_0"].values - df["PAY_6"].values

        # -------------------------------------------------------------
        # 4. DEBT ACCUMULATION & CASH FLOW BURDEN
        # -------------------------------------------------------------
        # Total Bill Amount across 6 months
        df["TOTAL_BILL_AMT"] = np.sum([df[col].values for col in bill_cols], axis=0)
        
        # Total Cash Repaid across 6 months
        df["TOTAL_PAY_AMT"] = np.sum([df[col].values for col in pay_cols], axis=0)
        
        # Net Cash Deficit = Total Billed - Total Repaid
        # Financial Meaning: Cumulative unpaid balance additions over the observation period
        df["NET_DEFICIT"] = df["TOTAL_BILL_AMT"].values - df["TOTAL_PAY_AMT"].values
        
        # Net Deficit relative to Credit Limit
        df["DEFICIT_TO_LIMIT"] = np.clip(df["NET_DEFICIT"].values / limit, -5.0, 10.0)

        # Bill Balance Growth Trend: (BILL_AMT1 - BILL_AMT6) / LIMIT_BAL
        # Financial Meaning: Normalized expansion of credit balance from April to September
        df["BILL_GROWTH_TREND"] = np.clip((df["BILL_AMT1"].values - df["BILL_AMT6"].values) / limit, -5.0, 5.0)

        self.engineered_feature_names_ = [
            "UTILIZATION_RECENT", "UTILIZATION_AVG", "UTILIZATION_MAX",
            "PAY_TO_BILL_1", "PAY_TO_BILL_2", "PAY_TO_BILL_3", "PAY_TO_BILL_AVG",
            "MAX_DELINQUENCY", "NUM_DELINQUENT_MONTHS", "AVG_DELAY_MONTHS",
            "DELINQUENCY_TREND", "TOTAL_BILL_AMT", "TOTAL_PAY_AMT",
            "NET_DEFICIT", "DEFICIT_TO_LIMIT", "BILL_GROWTH_TREND"
        ]

        return df


def engineer_credit_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function for applying domain feature engineering.
    
    Args:
        df: Clean credit DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with all engineered indicators added.
    """
    engineer = CreditFeatureEngineer()
    return engineer.transform(df)


if __name__ == "__main__":
    from data_loader import load_credit_data
    df, report = load_credit_data()
    df_feat = engineer_credit_features(df)
    print(f"Original features count: {len(df.columns)}")
    print(f"Enriched features count: {len(df_feat.columns)}")
    print("\nNewly created engineered features:")
    new_cols = [c for c in df_feat.columns if c not in df.columns]
    for c in new_cols:
        print(f"  - {c}: (min={df_feat[c].min():.3f}, mean={df_feat[c].mean():.3f}, max={df_feat[c].max():.3f})")
