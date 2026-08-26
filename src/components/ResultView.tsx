import React from "react";
import { Language, PredictionResult, ExplainabilityResult, FinancialHealthResult } from "../types";
import { getT } from "../i18n";
import { ShieldCheck, AlertTriangle, AlertOctagon, ArrowRight, Sliders, Info, HeartPulse } from "lucide-react";

interface ResultViewProps {
  currentLang: Language;
  prediction: PredictionResult;
  explanation: ExplainabilityResult;
  financialHealth: FinancialHealthResult;
  onNavigate: (tab: string) => void;
}

export const ResultView: React.FC<ResultViewProps> = ({
  currentLang,
  prediction,
  explanation,
  financialHealth,
  onNavigate,
}) => {
  const t = getT(currentLang);

  const isLow = prediction.risk_level === "LOW RISK";
  const isMed = prediction.risk_level === "MEDIUM RISK";

  return (
    <div className="max-w-5xl w-full max-w-full mx-auto space-y-6">
      {/* 3 Metric Summary Header */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 w-full max-w-full">
        {/* Risk Level Badge */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs text-center flex flex-col justify-between min-w-0 w-full max-w-full">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
            {t("result_risk_level")}
          </div>
          <div className="my-2">
            {isLow ? (
              <span className="inline-flex items-center space-x-1.5 bg-emerald-50 text-emerald-800 border border-emerald-300 px-3.5 py-1.5 rounded-full font-bold text-xs sm:text-sm">
                <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                <span className="break-words">{t("risk_tier_low")}</span>
              </span>
            ) : isMed ? (
              <span className="inline-flex items-center space-x-1.5 bg-amber-50 text-amber-800 border border-amber-300 px-3.5 py-1.5 rounded-full font-bold text-xs sm:text-sm">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                <span className="break-words">{t("risk_tier_medium")}</span>
              </span>
            ) : (
              <span className="inline-flex items-center space-x-1.5 bg-rose-50 text-rose-800 border border-rose-300 px-3.5 py-1.5 rounded-full font-bold text-xs sm:text-sm">
                <AlertOctagon className="w-4 h-4 text-rose-600 shrink-0" />
                <span className="break-words">{t("risk_tier_high")}</span>
              </span>
            )}
          </div>
          <div className="text-xs text-slate-500 mt-2 break-words">
            {t("result_binary_decision")}:{" "}
            <strong className="text-slate-800">
              {prediction.predicted_class === 1 ? t("pred_class_1") : t("pred_class_0")}
            </strong>
          </div>
        </div>

        {/* Model Estimated Default Likelihood */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs text-center flex flex-col justify-between min-w-0 w-full max-w-full">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
            {t("result_likelihood")}
          </div>
          <div className={`text-3xl sm:text-4xl font-extrabold my-1 ${
            isLow ? "text-emerald-600" : isMed ? "text-amber-600" : "text-rose-600"
          }`}>
            {(prediction?.model_estimated_likelihood_pct ?? ((prediction?.default_probability ?? 0) * 100)).toFixed(2)}%
          </div>
          <div className="text-xs text-slate-500 mt-2 break-words">
            {t("result_non_default_likelihood")}:{" "}
            <strong className="text-slate-800">
              {(prediction?.model_estimated_non_default_pct ?? (100 - (prediction?.model_estimated_likelihood_pct ?? ((prediction?.default_probability ?? 0) * 100)))).toFixed(2)}%
            </strong>
          </div>
        </div>

        {/* Financial Health Score FHI-5 */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs text-center flex flex-col justify-between sm:col-span-2 md:col-span-1 min-w-0 w-full max-w-full">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
            {t("fhi_score_title")}
          </div>
          <div className="text-3xl sm:text-4xl font-extrabold text-sky-600 my-1">
            {financialHealth?.score ?? 0} <span className="text-sm font-normal text-slate-400">/ 100</span>
          </div>
          <div className="text-xs text-slate-500 mt-2 break-words">
            Health Rating: <strong className="text-slate-800">{financialHealth?.label ?? "N/A"}</strong>
          </div>
        </div>
      </div>

      {/* Executive Narrative Summary */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs space-y-3 w-full max-w-full">
        <h3 className="text-sm sm:text-base font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3 w-full max-w-full">
          <Info className="w-4 h-4 text-sky-600 shrink-0" />
          <span className="break-words">{t("result_summary")}</span>
        </h3>
        <p className="text-slate-700 text-xs sm:text-sm leading-relaxed break-words">
          {explanation.summary}
        </p>

        <div className="pt-4 flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-2.5 sm:gap-3 w-full max-w-full">
          <button
            id="result-btn-explain"
            onClick={() => onNavigate("explain")}
            className="inline-flex items-center justify-center space-x-2 bg-sky-50 hover:bg-sky-100 text-sky-700 border border-sky-200 font-semibold text-xs px-4 py-2.5 sm:py-2 rounded-lg transition min-h-[42px] sm:min-h-[36px]"
          >
            <span>{t("nav_explain")}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
          <button
            id="result-btn-fhi"
            onClick={() => onNavigate("financial_health")}
            className="inline-flex items-center justify-center space-x-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 font-semibold text-xs px-4 py-2.5 sm:py-2 rounded-lg transition min-h-[42px] sm:min-h-[36px]"
          >
            <HeartPulse className="w-3.5 h-3.5" />
            <span>{t("nav_financial_health")}</span>
          </button>
          <button
            id="result-btn-simulator"
            onClick={() => onNavigate("simulator")}
            className="inline-flex items-center justify-center space-x-2 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 font-semibold text-xs px-4 py-2.5 sm:py-2 rounded-lg transition min-h-[42px] sm:min-h-[36px]"
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>{t("nav_simulator")}</span>
          </button>
        </div>
      </div>

      {/* Disclaimers */}
      <div className="bg-slate-100 border-l-4 border-slate-500 rounded p-4 text-xs text-slate-600 space-y-1 break-words leading-relaxed w-full max-w-full">
        <p><strong>⚖️ Educational Notice:</strong> {t("disclaimer_legal")}</p>
        <p><strong>📈 Probability Notice:</strong> {t("disclaimer_calibration")}</p>
      </div>
    </div>
  );
};
