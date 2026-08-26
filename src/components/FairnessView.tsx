import React, { useState, useEffect } from "react";
import { Language } from "../types";
import { getT } from "../i18n";
import {
  ShieldAlert,
  Scale,
  Database,
  Users,
  AlertTriangle,
  Info,
  CheckCircle2,
  HelpCircle,
  TrendingDown,
  TrendingUp,
  BarChart2,
  Sliders,
  Layers,
  FileText,
} from "lucide-react";
import {
  AUDITED_DATASET_FAIRNESS,
  FullFairnessReport,
  AttributeFairnessAudit,
  GroupFairnessMetrics,
} from "../engine/fairnessEngine";

interface FairnessViewProps {
  currentLang: Language;
}

export const FairnessView: React.FC<FairnessViewProps> = ({ currentLang }) => {
  const t = getT(currentLang);

  const [fairnessReport, setFairnessReport] = useState<FullFairnessReport>(AUDITED_DATASET_FAIRNESS);
  const [selectedAttribute, setSelectedAttribute] = useState<string>("SEX");
  const [activeSubTab, setActiveSubTab] = useState<"metrics" | "dataset" | "principles">("metrics");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    async function loadFairnessData() {
      try {
        setIsLoading(true);
        const res = await fetch("/api/fairness");
        const json = await res.json();
        if (json.success && json.data) {
          setFairnessReport(json.data);
        }
      } catch (_err) {
        // Use static audited data from fairnessEngine
        setFairnessReport(AUDITED_DATASET_FAIRNESS);
      } finally {
        setIsLoading(false);
      }
    }
    loadFairnessData();
  }, []);

  const currentAudit: AttributeFairnessAudit | undefined =
    fairnessReport.attributes[selectedAttribute] || AUDITED_DATASET_FAIRNESS.attributes[selectedAttribute];

  const formatPct = (val?: number | null) => {
    if (val === undefined || val === null || isNaN(val)) return "N/A";
    return `${(val * 100).toFixed(1)}%`;
  };

  const formatRatio = (val?: number | null) => {
    if (val === undefined || val === null || isNaN(val)) return "N/A";
    return `${val.toFixed(2)}x`;
  };

  const formatDiff = (val?: number | null) => {
    if (val === undefined || val === null || isNaN(val)) return "0.0%";
    const sign = val > 0 ? "+" : "";
    return `${sign}${(val * 100).toFixed(1)}%`;
  };

  return (
    <div id="fairness-view-container" className="max-w-6xl w-full max-w-full mx-auto space-y-6">
      {/* Top Banner Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs w-full max-w-full">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5 w-full max-w-full">
          <div className="min-w-0 max-w-full">
            <div className="flex flex-wrap items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center shrink-0">
                <Scale className="w-5 h-5" />
              </div>
              <h2 className="text-lg sm:text-xl font-bold text-slate-900 break-words">{t("fairness_title")}</h2>
              <span className="bg-slate-100 text-slate-700 text-[11px] sm:text-xs px-2.5 py-0.5 rounded-full border border-slate-200 font-medium shrink-0">
                Phase 9 Rigorous Audit
              </span>
            </div>
            <p className="text-xs text-slate-600 mt-2 max-w-3xl leading-relaxed break-words">
              {t("fairness_subtitle")}
            </p>
          </div>

          <div className="flex items-center space-x-2 self-start md:self-auto shrink-0">
            <div className="bg-amber-50 border border-amber-200 text-amber-800 text-xs px-3 py-1.5 rounded-lg flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
              <span className="break-words">Statistical & Proxy Assessment</span>
            </div>
          </div>
        </div>

        {/* Sub-Navigation Tabs */}
        <div className="flex space-x-2 pt-4 border-b border-slate-100 overflow-x-auto no-scrollbar touch-pan-x w-full max-w-full">
          <button
            id="subtab-metrics"
            type="button"
            onClick={() => setActiveSubTab("metrics")}
            className={`flex items-center space-x-2 pb-3 px-3 text-xs font-semibold border-b-2 transition-colors whitespace-nowrap min-h-[40px] shrink-0 ${
              activeSubTab === "metrics"
                ? "border-sky-600 text-sky-700"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <BarChart2 className="w-4 h-4 shrink-0" />
            <span>{t("fairness_tab_metrics")}</span>
          </button>

          <button
            id="subtab-dataset"
            type="button"
            onClick={() => setActiveSubTab("dataset")}
            className={`flex items-center space-x-2 pb-3 px-3 text-xs font-semibold border-b-2 transition-colors whitespace-nowrap min-h-[40px] shrink-0 ${
              activeSubTab === "dataset"
                ? "border-sky-600 text-sky-700"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Database className="w-4 h-4 shrink-0" />
            <span>{t("fairness_tab_overview")}</span>
          </button>

          <button
            id="subtab-principles"
            type="button"
            onClick={() => setActiveSubTab("principles")}
            className={`flex items-center space-x-2 pb-3 px-3 text-xs font-semibold border-b-2 transition-colors whitespace-nowrap min-h-[40px] shrink-0 ${
              activeSubTab === "principles"
                ? "border-sky-600 text-sky-700"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{t("fairness_tab_limitations")}</span>
          </button>
        </div>

        {/* TAB 1: GROUP METRICS & DISPARITIES */}
        {activeSubTab === "metrics" && currentAudit && (
          <div className="space-y-6 pt-4 w-full max-w-full min-w-0">
            {/* Attribute Selector */}
            <div className="bg-slate-50 p-3.5 sm:p-4 rounded-xl border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-3 sm:gap-4 w-full max-w-full">
              <div className="space-y-1 min-w-0">
                <label htmlFor="attr-select" className="text-xs font-bold text-slate-900 flex items-center space-x-1.5">
                  <Users className="w-4 h-4 text-sky-600 shrink-0" />
                  <span className="break-words">{t("fairness_select_attribute")}</span>
                </label>
                <p className="text-xs text-slate-500 break-words">
                  Select a demographic dimension to inspect group-level confusion rates, selection disparity, and error rates.
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                {Object.keys(fairnessReport.attributes || {}).map((attrKey) => {
                  const item = fairnessReport.attributes[attrKey];
                  const isSelected = selectedAttribute === attrKey;
                  return (
                    <button
                      key={attrKey}
                      id={`btn-select-attr-${attrKey}`}
                      type="button"
                      onClick={() => setSelectedAttribute(attrKey)}
                      className={`px-3.5 py-2 sm:py-1.5 text-xs font-semibold rounded-lg border transition-all min-h-[36px] sm:min-h-[32px] ${
                        isSelected
                          ? "bg-sky-600 border-sky-700 text-white shadow-xs"
                          : "bg-white border-slate-200 text-slate-700 hover:bg-slate-100"
                      }`}
                    >
                      {item.display_name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Attribute Information Card */}
            <div className="p-3.5 sm:p-4 bg-sky-50/60 border border-sky-100 rounded-xl flex items-start space-x-3 text-xs text-sky-900 w-full max-w-full">
              <Info className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
              <div className="space-y-1 min-w-0 max-w-full">
                <span className="font-bold">{currentAudit.display_name} Dimension Audit:</span>
                <p className="text-sky-800 leading-relaxed break-words">{currentAudit.description}</p>
                <div className="pt-1 flex flex-wrap items-center gap-1.5 text-slate-600">
                  <span className="font-semibold text-slate-700">{t("fairness_reference_group")}</span>
                  <span className="font-mono bg-white px-2 py-0.5 rounded border border-sky-200 text-sky-900 font-bold">
                    {currentAudit.reference_group_label}
                  </span>
                  <span className="break-words">· Total Cohort Records: <strong>{currentAudit.total_records_evaluated.toLocaleString()}</strong></span>
                </div>
              </div>
            </div>

            {/* Group Performance Matrix Table */}
            <div className="space-y-3 w-full max-w-full min-w-0">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 w-full max-w-full">
                <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                  <BarChart2 className="w-4 h-4 text-sky-600 shrink-0" />
                  <span className="break-words">Cohort Confusion Metrics & Calibration Rates</span>
                </h3>
                <span className="text-xs text-slate-500">
                  Fixed Decision Threshold: <code className="font-mono font-bold bg-slate-100 px-1.5 py-0.5 rounded">p = 0.50</code>
                </span>
              </div>

              <div className="w-full max-w-full overflow-x-auto no-scrollbar border border-slate-200 rounded-xl bg-white touch-pan-x table-responsive-container">
                <table className="w-full text-xs text-left border-collapse min-w-[620px]" aria-label="Group Fairness Metrics Table">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-slate-700">
                      <th scope="col" className="py-3 px-4 font-bold whitespace-nowrap">Cohort Group</th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap">Sample (n)</th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap" title="Actual ground-truth default rate">
                        {t("fairness_metric_base_rate")}
                      </th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap" title="Selection Rate / Predicted Default Rate">
                        {t("fairness_metric_ppr")}
                      </th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap" title="True Positive Rate / Recall">
                        {t("fairness_metric_recall")}
                      </th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap" title="False Positive Rate / False Alarm">
                        {t("fairness_metric_fpr")}
                      </th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap" title="Precision / Positive Predictive Value">
                        {t("fairness_metric_precision")}
                      </th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap">
                        {t("fairness_metric_accuracy")}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {Object.entries(currentAudit.groups).map(([groupKey, group]) => {
                      const isRef = group.is_reference;
                      const hasWarning = group.is_small_sample || group.is_critical_sample;

                      return (
                        <tr
                          key={groupKey}
                          className={`hover:bg-slate-50/80 transition-colors ${
                            isRef ? "bg-sky-50/30 font-medium" : ""
                          }`}
                        >
                          <td className="py-3 px-4">
                            <div className="flex items-center space-x-2">
                              <span className="font-bold text-slate-900 whitespace-nowrap">{group.label}</span>
                              {isRef && (
                                <span className="bg-sky-100 text-sky-800 text-[10px] px-1.5 py-0.5 rounded font-mono font-bold shrink-0">
                                  BASELINE
                                </span>
                              )}
                              {hasWarning && (
                                <span
                                  className="bg-amber-100 text-amber-900 text-[10px] px-1.5 py-0.5 rounded font-bold shrink-0"
                                  title={group.sample_warning || "Small sample size"}
                                >
                                  n &lt; 300
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="py-3 px-3 text-right font-mono text-slate-700 whitespace-nowrap">
                            {group.sample_count.toLocaleString()}
                          </td>
                          <td className="py-3 px-3 text-right font-mono text-slate-900 whitespace-nowrap">
                            {formatPct(group.base_rate)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono font-bold text-sky-800 bg-sky-50/50 whitespace-nowrap">
                            {formatPct(group.positive_prediction_rate)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono text-slate-800 whitespace-nowrap">
                            {formatPct(group.recall)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono text-slate-800 whitespace-nowrap">
                            {formatPct(group.false_positive_rate)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono text-slate-800 whitespace-nowrap">
                            {formatPct(group.precision)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono font-semibold text-emerald-800 whitespace-nowrap">
                            {formatPct(group.accuracy)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Disparity Analysis Table vs Baseline */}
            <div className="space-y-3 w-full max-w-full min-w-0">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 w-full max-w-full">
                <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                  <Sliders className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="break-words">Disparity vs Baseline Group ({currentAudit.reference_group_label})</span>
                </h3>
                <span className="text-xs text-slate-500">
                  Differences (Δ = Group - Ref) & Ratios (Group / Ref)
                </span>
              </div>

              <div className="w-full max-w-full overflow-x-auto no-scrollbar border border-slate-200 rounded-xl bg-white touch-pan-x table-responsive-container">
                <table className="w-full text-xs text-left border-collapse min-w-[620px]" aria-label="Disparity vs Baseline Table">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-slate-700">
                      <th scope="col" className="py-3 px-4 font-bold whitespace-nowrap">Cohort Group</th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap">Selection Rate Δ</th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap">Selection Ratio</th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap">Recall (TPR) Δ</th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap">Recall Ratio</th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap">FPR Δ</th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap">Precision Δ</th>
                      <th scope="col" className="py-3 px-3 font-bold text-right whitespace-nowrap">Accuracy Δ</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {Object.entries(currentAudit.groups).map(([groupKey, group]) => {
                      const disp = group.disparities_vs_baseline;
                      const isRef = group.is_reference;

                      return (
                        <tr
                          key={groupKey}
                          className={`hover:bg-slate-50/80 transition-colors ${
                            isRef ? "bg-sky-50/20 font-medium" : ""
                          }`}
                        >
                          <td className="py-3 px-4 font-bold text-slate-900 whitespace-nowrap">
                            {group.label} {isRef && "(Baseline)"}
                          </td>
                          <td className="py-3 px-3 text-right font-mono whitespace-nowrap">
                            {isRef ? "—" : formatDiff(disp?.positive_prediction_rate_diff)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono font-bold whitespace-nowrap">
                            {isRef ? "1.00x" : formatRatio(disp?.positive_prediction_rate_ratio)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono whitespace-nowrap">
                            {isRef ? "—" : formatDiff(disp?.recall_diff)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono whitespace-nowrap">
                            {isRef ? "1.00x" : formatRatio(disp?.recall_ratio)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono whitespace-nowrap">
                            {isRef ? "—" : formatDiff(disp?.false_positive_rate_diff)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono whitespace-nowrap">
                            {isRef ? "—" : formatDiff(disp?.precision_diff)}
                          </td>
                          <td className="py-3 px-3 text-right font-mono whitespace-nowrap">
                            {isRef ? "—" : formatDiff(disp?.accuracy_diff)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Contextual Limitations & Caveats */}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2 w-full max-w-full">
              <div className="flex items-center space-x-2 text-xs font-bold text-slate-900">
                <FileText className="w-4 h-4 text-slate-700 shrink-0" />
                <span className="break-words">Audited Empirical Findings for {currentAudit.display_name}:</span>
              </div>
              <ul className="text-xs text-slate-700 space-y-1.5 list-disc list-inside">
                {currentAudit.limitations.map((item, idx) => (
                  <li key={idx} className="leading-relaxed break-words">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* TAB 2: DATASET & FEATURE AUDIT */}
        {activeSubTab === "dataset" && (
          <div className="space-y-6 pt-4 w-full max-w-full min-w-0">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6 w-full max-w-full">
              {/* Available Demographics */}
              <div className="p-4 sm:p-5 bg-emerald-50/50 border border-emerald-200 rounded-xl space-y-3 w-full max-w-full min-w-0">
                <div className="flex items-center space-x-2 text-sm font-bold text-emerald-950 border-b border-emerald-200 pb-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="break-words">{t("fairness_available_demographics")}</span>
                </div>
                <p className="text-xs text-emerald-900 leading-relaxed break-words">
                  Only 4 demographic / proxy fields exist in the benchmark dataset:
                </p>
                <div className="space-y-2 w-full max-w-full">
                  {fairnessReport.dataset_audit.available_demographics.map((demo) => (
                    <div key={demo.name} className="p-2.5 bg-white rounded-lg border border-emerald-100 text-xs w-full max-w-full">
                      <div className="font-bold text-slate-900 break-words">{demo.label} ({demo.name})</div>
                      <div className="text-[11px] text-slate-600 mt-1 break-words">
                        {demo.categories.join(" · ")}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Unavailable Demographic Attributes (Data Gaps) */}
              <div className="p-4 sm:p-5 bg-amber-50/50 border border-amber-200 rounded-xl space-y-3 w-full max-w-full min-w-0">
                <div className="flex items-center space-x-2 text-sm font-bold text-amber-950 border-b border-amber-200 pb-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span className="break-words">{t("fairness_unavailable_demographics")}</span>
                </div>
                <p className="text-xs text-amber-900 leading-relaxed break-words">
                  Critical socio-economic and demographic parameters are entirely absent from the raw dataset:
                </p>
                <ul className="text-xs text-amber-900 space-y-2 list-disc list-inside w-full max-w-full">
                  {fairnessReport.dataset_audit.unavailable_demographics.map((gap, idx) => (
                    <li key={idx} className="leading-relaxed bg-white/70 p-2 rounded border border-amber-100 break-words">
                      {gap}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Feature Pipeline Audit */}
            <div className="p-4 sm:p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-3 w-full max-w-full">
              <div className="flex items-center space-x-2 text-sm font-bold text-slate-900 border-b border-slate-200 pb-2">
                <Layers className="w-4 h-4 text-sky-600 shrink-0" />
                <span className="break-words">Feature Pipeline & Variable Exclusion Audit</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-700 w-full max-w-full">
                <div className="space-y-1 bg-white p-3 rounded-lg border border-slate-200 min-w-0 w-full max-w-full">
                  <span className="font-bold text-rose-700 break-words">Excluded Non-Predictive Features:</span>
                  <p className="text-slate-600 leading-relaxed break-words">
                    <code>ID</code> (Unique arbitrary borrower identifier) was dropped to prevent memorization artifacts and spurious indexing correlation.
                  </p>
                </div>
                <div className="space-y-1 bg-white p-3 rounded-lg border border-slate-200 min-w-0 w-full max-w-full">
                  <span className="font-bold text-sky-700 break-words">Retained Model Pipeline:</span>
                  <p className="text-slate-600 leading-relaxed break-words">
                    23 original credit/financial fields + 16 strictly pre-split engineered interaction features (utilization trajectory, delinquency counts, payment coverage ratios).
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: PRINCIPLES & LIMITATIONS */}
        {activeSubTab === "principles" && (
          <div className="space-y-6 pt-4 w-full max-w-full min-w-0">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 w-full max-w-full">
              {/* Principle 1 */}
              <div className="p-4 sm:p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-2.5 w-full max-w-full min-w-0">
                <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 border-b border-slate-200 pb-2">
                  <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />
                  <span className="break-words">No "Unbiased" Claim</span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed break-words">
                  {t("fairness_principle_1")}
                </p>
                <p className="text-xs text-slate-500 italic break-words leading-relaxed">
                  Fairness criteria like Demographic Parity, Equal Opportunity, and Predictive Parity are mathematically incompatible when base default rates differ across groups.
                </p>
              </div>

              {/* Principle 2 */}
              <div className="p-4 sm:p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-2.5 w-full max-w-full min-w-0">
                <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 border-b border-slate-200 pb-2">
                  <HelpCircle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span className="break-words">Fairness Through Blindness</span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed break-words">
                  {t("fairness_principle_2")}
                </p>
                <p className="text-xs text-slate-500 italic break-words leading-relaxed">
                  Credit limits, bill sizes, and repayment histories inherently reflect systemic economic realities and historical lending disparities.
                </p>
              </div>

              {/* Principle 3 */}
              <div className="p-4 sm:p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-2.5 w-full max-w-full min-w-0">
                <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 border-b border-slate-200 pb-2">
                  <AlertTriangle className="w-4 h-4 text-sky-600 shrink-0" />
                  <span className="break-words">Sample Size Discipline</span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed break-words">
                  {t("fairness_principle_3")}
                </p>
                <p className="text-xs text-slate-500 italic break-words leading-relaxed">
                  Groups with small sample sizes (e.g., EDUCATION 4 'Others' with n=123, or MARRIAGE 0 with n=54) exhibit wide confidence intervals and noisy point estimates.
                </p>
              </div>
            </div>

            {/* Global Disclaimer Box */}
            <div className="p-4 bg-amber-50/60 border border-amber-200 rounded-xl text-xs text-amber-900 space-y-1 break-words leading-relaxed w-full max-w-full">
              <span className="font-bold flex items-center space-x-1.5">
                <Info className="w-4 h-4 text-amber-700 shrink-0" />
                <span>Regulatory & Operational Notice:</span>
              </span>
              <p className="text-amber-800 leading-relaxed">
                {fairnessReport.global_disclaimer}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
