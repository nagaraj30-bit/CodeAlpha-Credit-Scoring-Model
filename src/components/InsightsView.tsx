import React from "react";
import { Language } from "../types";
import { getT } from "../i18n";
import { Cpu, Award, BarChart3, Scale, ShieldCheck } from "lucide-react";

interface InsightsViewProps {
  currentLang: Language;
}

export const InsightsView: React.FC<InsightsViewProps> = ({ currentLang }) => {
  const t = getT(currentLang);

  const featureImportances = [
    { name: "PAY_0 (Recent Payment Status)", value: 18.5 },
    { name: "UTILIZATION_AVG (6-Month Utilization)", value: 8.2 },
    { name: "PAY_2 (1-Month Prior Status)", value: 7.5 },
    { name: "BILL_AMT1 (Recent Statement Bill)", value: 6.8 },
    { name: "LIMIT_BAL (Approved Credit Line)", value: 5.9 },
    { name: "PAY_AMT1 (Recent Paid Amount)", value: 5.4 },
    { name: "PAY_TO_BILL_1 (Payment-to-Bill Ratio)", value: 4.8 },
    { name: "AGE (Borrower Age)", value: 4.2 },
  ];

  return (
    <div className="max-w-5xl w-full max-w-full mx-auto space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs w-full max-w-full">
        <h2 className="text-lg sm:text-xl font-bold text-slate-900 break-words">{t("insights_header")}</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mt-6 w-full max-w-full">
          {/* Architecture Card */}
          <div className="p-4 sm:p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-3 min-w-0 w-full max-w-full">
            <div className="flex items-center space-x-2 text-sm font-bold text-slate-900 border-b border-slate-200 pb-2 w-full max-w-full">
              <Cpu className="w-4 h-4 text-sky-600 shrink-0" />
              <span className="break-words">{t("insights_champion_title")}</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed break-words">
              {t("insights_champion_desc")}
            </p>
            <ul className="text-xs text-slate-700 space-y-1.5 list-disc list-inside">
              <li className="break-words"><strong>Dataset:</strong> UCI Credit Card Default (30,000 borrowers).</li>
              <li className="break-words"><strong>Zero Data Leakage:</strong> Strict pre-split transformation pipeline.</li>
              <li className="break-words"><strong>16 Engineered Signals:</strong> Delinquency trends, payment ratios, and utilization averages.</li>
            </ul>
          </div>

          {/* Audited Metrics */}
          <div className="p-4 sm:p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-3 min-w-0 w-full max-w-full">
            <div className="flex items-center space-x-2 text-sm font-bold text-slate-900 border-b border-slate-200 pb-2 w-full max-w-full">
              <Award className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="break-words">{t("insights_metrics_title")}</span>
            </div>
            <ul className="text-xs text-slate-700 space-y-2 w-full max-w-full">
              <li className="flex items-center justify-between gap-2">
                <span className="break-words">{t("insights_metric_auc")}</span>
                <span className="font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded shrink-0">0.7744</span>
              </li>
              <li className="flex items-center justify-between gap-2">
                <span className="break-words">{t("insights_metric_acc")}</span>
                <span className="font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded shrink-0">82.02%</span>
              </li>
              <li className="flex items-center justify-between gap-2">
                <span className="break-words">{t("insights_metric_brier")}</span>
                <span className="font-mono font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded shrink-0">0.1299</span>
              </li>
              <li className="flex items-center justify-between gap-2">
                <span className="break-words">{t("insights_metric_f1")}</span>
                <span className="font-mono font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded shrink-0">0.4812</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Global Feature Importance Chart */}
        <div className="mt-6 pt-6 border-t border-slate-100 space-y-4 w-full max-w-full">
          <div className="flex items-center space-x-2 text-sm font-bold text-slate-900 w-full max-w-full">
            <BarChart3 className="w-4 h-4 text-sky-600 shrink-0" />
            <span className="break-words">{t("insights_feature_imp_title")}</span>
          </div>

          <div className="space-y-3 w-full max-w-full">
            {featureImportances.map((item, idx) => (
              <div key={idx} className="space-y-1 w-full max-w-full">
                <div className="flex justify-between text-xs font-semibold text-slate-700 gap-2 w-full max-w-full">
                  <span className="break-words">{item.name}</span>
                  <span className="font-mono text-slate-900 font-bold shrink-0">{item.value}%</span>
                </div>
                <div className="w-full max-w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-sky-600 h-2 rounded-full"
                    style={{ width: `${(item.value / 20) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Disclaimers & Fair Lending */}
      <div className="bg-slate-100 border-l-4 border-slate-500 rounded p-3.5 sm:p-4 text-xs text-slate-600 space-y-1.5 break-words w-full max-w-full">
        <p><strong>⚖️ Governance & Compliance Notice:</strong> {t("disclaimer_legal")}</p>
        <p><strong>🔒 Privacy Statement:</strong> {t("disclaimer_privacy")}</p>
      </div>
    </div>
  );
};
