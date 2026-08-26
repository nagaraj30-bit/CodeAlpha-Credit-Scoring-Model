import React from "react";
import { Language, FinancialHealthResult, FinancialHealthPillar } from "../types";
import { getT } from "../i18n";
import { HeartPulse, CheckCircle2, AlertCircle, Info } from "lucide-react";

interface FinancialHealthViewProps {
  currentLang: Language;
  financialHealth: FinancialHealthResult;
}

export const FinancialHealthView: React.FC<FinancialHealthViewProps> = ({
  currentLang,
  financialHealth,
}) => {
  const t = getT(currentLang);
  const { score, label, components, summary } = financialHealth;

  const getScoreColor = (s: number) => {
    if (s >= 80) return "text-emerald-600";
    if (s >= 65) return "text-sky-600";
    if (s >= 50) return "text-amber-600";
    return "text-rose-600";
  };

  const getBarColor = (s: number) => {
    if (s >= 80) return "bg-emerald-500";
    if (s >= 65) return "bg-sky-500";
    if (s >= 50) return "bg-amber-500";
    return "bg-rose-500";
  };

  return (
    <div className="max-w-5xl w-full max-w-full mx-auto space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full max-w-full">
        {/* Score & Rating Column */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs flex flex-col justify-between text-center min-w-0 w-full max-w-full">
          <div className="w-full max-w-full">
            <div className="inline-flex items-center space-x-1.5 text-xs font-bold text-sky-700 bg-sky-50 px-3 py-1 rounded-full border border-sky-200 mb-4">
              <HeartPulse className="w-4 h-4 text-sky-600 shrink-0" />
              <span>{t("fhi_header")}</span>
            </div>
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              {t("fhi_score_title")}
            </div>
            <div className={`text-4xl sm:text-5xl font-black my-3 ${getScoreColor(score)}`}>
              {score}
              <span className="text-base font-normal text-slate-400"> / 100</span>
            </div>
            <div className="inline-block px-3 py-1 bg-slate-100 text-slate-800 rounded-md font-bold text-sm">
              {label}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 text-xs text-slate-600 leading-relaxed text-left break-words w-full max-w-full">
            <Info className="w-4 h-4 text-sky-600 inline mr-1 shrink-0" />
            {summary}
          </div>
        </div>

        {/* 5 Core Pillars Breakdown */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs space-y-4 min-w-0 w-full max-w-full">
          <h3 className="text-sm sm:text-base font-bold text-slate-900 border-b border-slate-100 pb-3 break-words w-full max-w-full">
            5 Core Financial Health Pillars
          </h3>

          <div className="space-y-3 sm:space-y-4 w-full max-w-full">
            {Object.entries(components).map(([key, pillarVal]) => {
              const pillar = pillarVal as FinancialHealthPillar;
              return (
                <div key={key} className="p-3 sm:p-3.5 bg-slate-50 border border-slate-200 rounded-lg space-y-2 min-w-0 w-full max-w-full">
                  <div className="flex flex-wrap items-center justify-between gap-1 text-xs w-full max-w-full">
                    <span className="font-bold text-slate-900 break-words">
                      {pillar?.name || key} <span className="text-slate-400 font-normal">({((pillar?.weight ?? 0.2) * 100).toFixed(0)}% weight)</span>
                    </span>
                    <span className="font-mono font-bold text-slate-800 shrink-0">
                      {(pillar?.score ?? 0).toFixed(0)} / 100 · <span className="text-slate-600 font-normal">{pillar?.status || "N/A"}</span>
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full max-w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full transition-all ${getBarColor(pillar?.score ?? 0)}`}
                      style={{ width: `${Math.min(100, Math.max(0, pillar?.score ?? 0))}%` }}
                    />
                  </div>

                  <p className="text-[11px] sm:text-xs text-slate-600 break-words leading-relaxed">
                    {pillar.explanation}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Disclaimers Banner */}
      <div className="bg-slate-100 border-l-4 border-slate-500 rounded p-4 text-xs text-slate-600 space-y-1 break-words leading-relaxed w-full max-w-full">
        <p><strong>⚖️ Educational Heuristic:</strong> The Financial Health Indicator (FHI-5) is a transparent mathematical index calculated strictly from payment timeliness, utilization, and debt burden ratios. It is NOT an official credit bureau score or FICO score.</p>
      </div>
    </div>
  );
};
