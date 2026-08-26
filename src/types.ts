export type Language = "en" | "ta" | "hi";

export interface ApplicantData {
  LIMIT_BAL: number;
  SEX: number;
  EDUCATION: number;
  MARRIAGE: number;
  AGE: number;
  PAY_0: number;
  PAY_2: number;
  PAY_3: number;
  PAY_4: number;
  PAY_5: number;
  PAY_6: number;
  BILL_AMT1: number;
  BILL_AMT2: number;
  BILL_AMT3: number;
  BILL_AMT4: number;
  BILL_AMT5: number;
  BILL_AMT6: number;
  PAY_AMT1: number;
  PAY_AMT2: number;
  PAY_AMT3: number;
  PAY_AMT4: number;
  PAY_AMT5: number;
  PAY_AMT6: number;
}

export interface PredictionResult {
  predicted_class: number;
  predicted_label: string;
  default_probability: number;
  non_default_probability: number;
  model_estimated_likelihood_pct: number;
  model_estimated_non_default_pct: number;
  risk_level: "LOW RISK" | "MEDIUM RISK" | "HIGH RISK";
  decision_threshold: number;
  disclaimer: string;
  probability_notice: string;
  privacy_statement: string;
}

export interface FactorItem {
  feature_name: string;
  human_label: string;
  direction: "risk" | "positive";
  significance: string;
  importance: number;
  actual_value: number;
  display_value: string;
  explanation: string;
  impact_score: number;
}

export interface ExplainabilityResult {
  risk_level: string;
  predicted_label: string;
  top_risk_factors: FactorItem[];
  positive_factors: FactorItem[];
  summary: string;
  factor_count: {
    total_risk_factors: number;
    total_positive_factors: number;
  };
  global_feature_importances: Record<string, number>;
}

export interface FinancialHealthPillar {
  name: string;
  score: number;
  weight: number;
  status: string;
  explanation: string;
}

export interface FinancialHealthResult {
  score: number;
  label: "EXCELLENT" | "GOOD" | "FAIR" | "POOR / AT RISK";
  components: Record<string, FinancialHealthPillar>;
  summary: string;
  methodology: {
    name: string;
    version: string;
    total_weight: number;
    notice: string;
  };
  disclaimer: string;
  privacy_statement: string;
}

export interface ScenarioComparison {
  default_probability_delta: number;
  financial_health_delta: number;
  risk_direction: "IMPROVED" | "WORSENED" | "UNCHANGED";
  financial_health_direction: "IMPROVED" | "WORSENED" | "UNCHANGED";
  summary: string;
  risk_factors_resolved: FactorItem[];
  positive_factors_gained: FactorItem[];
  component_comparison: Record<string, {
    current_score: number;
    scenario_score: number;
    delta: number;
    direction: string;
  }>;
}

export interface ScenarioResult {
  current: {
    default_probability: number;
    risk_level: string;
    financial_health: FinancialHealthResult;
  };
  scenario: {
    default_probability: number;
    risk_level: string;
    financial_health: FinancialHealthResult;
  };
  comparison: ScenarioComparison;
  disclaimer: string;
  privacy_statement: string;
}

export interface FullAssessmentResponse {
  success: boolean;
  prediction: PredictionResult;
  explanation: ExplainabilityResult;
  financial_health: FinancialHealthResult;
}

export type {
  GroupFairnessMetrics,
  AttributeFairnessAudit,
  FullFairnessReport,
  ConfusionMatrixCounts,
} from "./engine/fairnessEngine";

