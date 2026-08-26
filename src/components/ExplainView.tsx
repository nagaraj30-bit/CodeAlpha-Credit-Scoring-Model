import React from "react";
import { Language, ExplainabilityResult } from "../types";
import { getT } from "../i18n";
import { AlertCircle, ShieldCheck, HelpCircle } from "lucide-react";

interface ExplainViewProps {
  currentLang: Language;
  explanation: ExplainabilityResult;
}

export const ExplainView: React.FC<ExplainViewProps> = ({
  currentLang,
  explanation,
}) => {
  const t = getT(currentLang);

  const riskFactors = explanation.top_risk_factors || [];
  const positiveFactors = explanation.positive_factors || [];

  return (
    <div className="max-w-5xl w-full max-w-full mx-auto space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs w-full max-w-full">
        <div className="w-full max-w-full">
          <h2 className="text-lg sm:text-xl font-bold text-slate-900 break-words">{t("explain_header")}</h2>
          <p className="text-xs text-slate-500 mt-1 break-words">{t("explain_subtitle")}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 sm:gap-6 mt-6 w-full max-w-full">
          {/* Risk Factors */}
          <div className="space-y-4 min-w-0 w-full max-w-full">
            <div className="flex items-center space-x-2 text-sm font-bold text-rose-900 border-b border-rose-100 pb-2 w-full max-w-full">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              <span className="break-words">{t("explain_risk_factors_title")}</span>
              <span className="ml-auto text-xs bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full font-mono shrink-0">
                {riskFactors.length}
              </span>
            </div>

            {riskFactors.length === 0 ? (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 break-words w-full max-w-full">
                {t("explain_no_risk_factors")}
              </div>
            ) : (
              <div className="space-y-3 w-full max-w-full">
                {riskFactors.map((factor, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 bg-rose-50/70 border border-rose-200 rounded-lg space-y-1.5 min-w-0 w-full max-w-full"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-1.5 text-xs font-bold text-rose-900 w-full max-w-full">
                      <span className="break-words">{factor.human_label}</span>
                      <span className="font-mono bg-rose-100 px-2 py-0.5 rounded text-rose-800 shrink-0">
                        {factor.display_value}
                      </span>
                    </div>
                    <p className="text-xs text-rose-800 leading-relaxed break-words">
                      {factor.explanation}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Positive Strengths */}
          <div className="space-y-4 min-w-0 w-full max-w-full">
            <div className="flex items-center space-x-2 text-sm font-bold text-emerald-900 border-b border-emerald-100 pb-2 w-full max-w-full">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="break-words">{t("explain_positive_factors_title")}</span>
              <span className="ml-auto text-xs bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-mono shrink-0">
                {positiveFactors.length}
              </span>
            </div>

            {positiveFactors.length === 0 ? (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 break-words w-full max-w-full">
                {t("explain_no_positive_factors")}
              </div>
            ) : (
              <div className="space-y-3 w-full max-w-full">
                {positiveFactors.map((factor, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-lg space-y-1.5 min-w-0 w-full max-w-full"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-1.5 text-xs font-bold text-emerald-900 w-full max-w-full">
                      <span className="break-words">{factor.human_label}</span>
                      <span className="font-mono bg-emerald-100 px-2 py-0.5 rounded text-emerald-800 shrink-0">
                        {factor.display_value}
                      </span>
                    </div>
                    <p className="text-xs text-emerald-800 leading-relaxed break-words">
                      {factor.explanation}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Statistical Notice */}
      <div className="bg-slate-100 border-l-4 border-slate-500 rounded p-4 text-xs text-slate-600 space-y-1 break-words leading-relaxed w-full max-w-full">
        <p><strong>📌 Association vs Causality:</strong> {t("disclaimer_association")}</p>
      </div>
    </div>
  );
};
