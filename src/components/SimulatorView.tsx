import React, { useState } from "react";
import { Language, ApplicantData, ScenarioResult } from "../types";
import { getT } from "../i18n";
import {
  Sliders,
  TrendingDown,
  TrendingUp,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";

interface SimulatorViewProps {
  currentLang: Language;
  applicant: ApplicantData;
  scenarioResult: ScenarioResult | null;
  isLoading: boolean;
  onSimulateCustom: (modifications: Partial<ApplicantData>) => void;
  onSimulatePreset: (preset: "remediate" | "paydown_50" | "paydown_80" | "limit_increase") => void;
  onReset: () => void;
}

export const SimulatorView: React.FC<SimulatorViewProps> = ({
  currentLang,
  applicant,
  scenarioResult,
  isLoading,
  onSimulateCustom,
  onSimulatePreset,
  onReset,
}) => {
  const t = getT(currentLang);

  const [simLimit, setSimLimit] = useState<number>(applicant.LIMIT_BAL || 50000);
  const [simPay0, setSimPay0] = useState<number>(applicant.PAY_0 || 0);
  const [simPay2, setSimPay2] = useState<number>(applicant.PAY_2 || 0);
  const [simBill1, setSimBill1] = useState<number>(applicant.BILL_AMT1 || 10000);
  const [simPayAmt1, setSimPayAmt1] = useState<number>(applicant.PAY_AMT1 || 2000);

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSimulateCustom({
      LIMIT_BAL: simLimit,
      PAY_0: simPay0,
      PAY_2: simPay2,
      BILL_AMT1: simBill1,
      PAY_AMT1: simPayAmt1,
    });
  };

  const comp = scenarioResult?.comparison;
  const currProb = (scenarioResult?.current?.default_probability != null ? scenarioResult.current.default_probability * 100 : (scenarioResult as any)?.current_state?.prediction?.default_probability != null ? (scenarioResult as any).current_state.prediction.default_probability * 100 : 0);
  const scenProb = (scenarioResult?.scenario?.default_probability != null ? scenarioResult.scenario.default_probability * 100 : (scenarioResult as any)?.simulated_state?.prediction?.default_probability != null ? (scenarioResult as any).simulated_state.prediction.default_probability * 100 : 0);
  const probDelta = (comp?.default_probability_delta != null ? comp.default_probability_delta * 100 : (scenarioResult as any)?.default_probability_delta != null ? (scenarioResult as any).default_probability_delta * 100 : (scenProb - currProb));

  const currFhi = scenarioResult?.current?.financial_health?.score ?? (scenarioResult as any)?.current_state?.financial_health?.score ?? 0;
  const scenFhi = scenarioResult?.scenario?.financial_health?.score ?? (scenarioResult as any)?.simulated_state?.financial_health?.score ?? 0;
  const fhiDelta = comp?.financial_health_delta ?? (scenarioResult as any)?.fhi_score_delta ?? (scenFhi - currFhi);

  return (
    <div className="max-w-6xl w-full max-w-full mx-auto space-y-6">
      {/* Title & Presets */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs space-y-4 w-full max-w-full">
        <div className="w-full max-w-full">
          <h2 className="text-lg sm:text-xl font-bold text-slate-900 break-words">{t("sim_header")}</h2>
          <p className="text-xs text-slate-500 mt-1 break-words">{t("sim_subtitle")}</p>
        </div>

        {/* 1-Click Presets */}
        <div className="w-full max-w-full">
          <div className="text-xs font-bold text-slate-700 mb-2 flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-sky-600 shrink-0" />
            <span className="break-words">{t("sim_presets_title")}</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-3 w-full max-w-full">
            <button
              id="preset-remediate"
              type="button"
              disabled={isLoading}
              onClick={() => onSimulatePreset("remediate")}
              className="p-3 text-left rounded-lg border border-slate-200 hover:border-sky-500 bg-slate-50 hover:bg-sky-50/50 transition flex flex-col justify-between min-h-[56px] min-w-0 w-full max-w-full"
            >
              <div className="text-xs font-bold text-slate-900 break-words">{t("sim_preset_remediate")}</div>
              <div className="text-[11px] text-slate-500 mt-1 break-words">Sets recent overdue delays to on-time (0)</div>
            </button>

            <button
              id="preset-paydown-50"
              type="button"
              disabled={isLoading}
              onClick={() => onSimulatePreset("paydown_50")}
              className="p-3 text-left rounded-lg border border-slate-200 hover:border-emerald-500 bg-slate-50 hover:bg-emerald-50/50 transition flex flex-col justify-between min-h-[56px] min-w-0 w-full max-w-full"
            >
              <div className="text-xs font-bold text-slate-900 break-words">{t("sim_preset_paydown_50")}</div>
              <div className="text-[11px] text-slate-500 mt-1 break-words">Reduces statement bill by 50%</div>
            </button>

            <button
              id="preset-paydown-80"
              type="button"
              disabled={isLoading}
              onClick={() => onSimulatePreset("paydown_80")}
              className="p-3 text-left rounded-lg border border-slate-200 hover:border-emerald-500 bg-slate-50 hover:bg-emerald-50/50 transition flex flex-col justify-between min-h-[56px] min-w-0 w-full max-w-full"
            >
              <div className="text-xs font-bold text-slate-900 break-words">{t("sim_preset_paydown_80")}</div>
              <div className="text-[11px] text-slate-500 mt-1 break-words">Substantial 80% balance reduction</div>
            </button>

            <button
              id="preset-limit-inc"
              type="button"
              disabled={isLoading}
              onClick={() => onSimulatePreset("limit_increase")}
              className="p-3 text-left rounded-lg border border-slate-200 hover:border-purple-500 bg-slate-50 hover:bg-purple-50/50 transition flex flex-col justify-between min-h-[56px] min-w-0 w-full max-w-full"
            >
              <div className="text-xs font-bold text-slate-900 break-words">{t("sim_preset_limit_inc")}</div>
              <div className="text-[11px] text-slate-500 mt-1 break-words">Simulates +50% limit expansion</div>
            </button>
          </div>
        </div>
      </div>

      {/* 3-Panel Main Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 sm:gap-6 w-full max-w-full">
        {/* Left: Scenario Controls */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-xs space-y-4 min-w-0 w-full max-w-full">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 gap-2 w-full max-w-full">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-sky-600 shrink-0" />
              <span className="break-words">{t("sim_panel_controls")}</span>
            </h3>
            <button
              type="button"
              onClick={onReset}
              className="text-xs text-slate-500 hover:text-slate-800 flex items-center space-x-1 py-1 px-2 rounded hover:bg-slate-100 transition shrink-0 min-h-[32px]"
            >
              <RotateCcw className="w-3 h-3" />
              <span>{t("btn_reset_scenario")}</span>
            </button>
          </div>

          <form onSubmit={handleCustomSubmit} className="space-y-4 w-full max-w-full">
            {/* Credit Limit */}
            <div className="w-full max-w-full">
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {t("lbl_limit_bal")} (NT$)
              </label>
              <input
                id="sim-input-limit"
                type="number"
                min="10000"
                max="1000000"
                step="5000"
                value={simLimit}
                onChange={(e) => setSimLimit(Number(e.target.value))}
                className="w-full max-w-full min-w-0 py-2 sm:py-1.5 px-3 text-xs sm:text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 min-h-[40px] sm:min-h-[36px] box-border"
              />
            </div>

            {/* Repayment Sliders */}
            <div className="space-y-3 pt-2 w-full max-w-full">
              <div className="w-full max-w-full">
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1 gap-2">
                  <span className="break-words">September Repayment Status (PAY_0)</span>
                  <span className="font-mono text-sky-600 font-bold shrink-0">{simPay0}</span>
                </div>
                <input
                  id="sim-slider-pay0"
                  type="range"
                  min="-2"
                  max="8"
                  value={simPay0}
                  onChange={(e) => setSimPay0(Number(e.target.value))}
                  className="w-full max-w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                  <span>On-time (-2..0)</span>
                  <span>1 Mo Delay</span>
                  <span>2+ Mo Delay</span>
                </div>
              </div>

              <div className="w-full max-w-full">
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1 gap-2">
                  <span className="break-words">August Repayment Status (PAY_2)</span>
                  <span className="font-mono text-sky-600 font-bold shrink-0">{simPay2}</span>
                </div>
                <input
                  id="sim-slider-pay2"
                  type="range"
                  min="-2"
                  max="8"
                  value={simPay2}
                  onChange={(e) => setSimPay2(Number(e.target.value))}
                  className="w-full max-w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>

            {/* Bill & Pay Amount */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 w-full max-w-full">
              <div className="min-w-0 w-full max-w-full">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Sept Bill (BILL_AMT1)
                </label>
                <input
                  id="sim-input-bill1"
                  type="number"
                  step="1000"
                  value={simBill1}
                  onChange={(e) => setSimBill1(Number(e.target.value))}
                  className="w-full max-w-full min-w-0 py-2 sm:py-1.5 px-3 text-xs sm:text-sm border border-slate-300 rounded-lg font-mono min-h-[40px] sm:min-h-[36px] box-border"
                />
              </div>
              <div className="min-w-0 w-full max-w-full">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Sept Paid (PAY_AMT1)
                </label>
                <input
                  id="sim-input-payamt1"
                  type="number"
                  step="500"
                  value={simPayAmt1}
                  onChange={(e) => setSimPayAmt1(Number(e.target.value))}
                  className="w-full max-w-full min-w-0 py-2 sm:py-1.5 px-3 text-xs sm:text-sm border border-slate-300 rounded-lg font-mono min-h-[40px] sm:min-h-[36px] box-border"
                />
              </div>
            </div>

            <button
              id="btn-run-sim-custom"
              type="submit"
              disabled={isLoading}
              className="w-full max-w-full mt-4 bg-sky-600 hover:bg-sky-700 disabled:bg-sky-400 text-white font-bold text-xs sm:text-sm py-3 sm:py-2.5 rounded-lg shadow-xs transition min-h-[44px]"
            >
              {isLoading ? t("msg_simulating") : t("btn_simulate_scenario")}
            </button>
          </form>
        </div>

        {/* Right: Simulation Delta & Factor Comparison */}
        <div className="lg:col-span-7 space-y-4 min-w-0 w-full max-w-full">
          {!scenarioResult ? (
            <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-xs text-center w-full max-w-full">
              <Sliders className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h4 className="text-sm font-bold text-slate-700 break-words">No Scenario Simulated Yet</h4>
              <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto break-words leading-relaxed">
                Click one of the 1-click presets above or adjust controls on the left to observe how the production Random Forest model responds to hypothetical changes.
              </p>
            </div>
          ) : (
            <div className="space-y-4 w-full max-w-full min-w-0">
              {/* Metric Comparison Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 w-full max-w-full">
                {/* Default Probability Delta */}
                <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-xs text-center min-w-0 w-full max-w-full">
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                    {t("sim_lbl_prob_delta")}
                  </div>
                  <div className={`text-2xl sm:text-3xl font-extrabold my-1 ${
                    probDelta < 0 ? "text-emerald-600" : probDelta > 0 ? "text-rose-600" : "text-slate-600"
                  }`}>
                    {(probDelta ?? 0) > 0 ? `+${(probDelta ?? 0).toFixed(2)}%` : `${(probDelta ?? 0).toFixed(2)}%`}
                  </div>
                  <div className="text-xs text-slate-500 mt-1 break-words">
                    {(currProb ?? 0).toFixed(1)}% → <strong className="text-slate-800">{(scenProb ?? 0).toFixed(1)}%</strong> ({comp?.risk_direction || (scenarioResult as any)?.risk_direction || "EVALUATED"})
                  </div>
                </div>

                {/* Financial Health Delta */}
                <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-xs text-center min-w-0 w-full max-w-full">
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                    {t("sim_lbl_fhi_delta")}
                  </div>
                  <div className={`text-2xl sm:text-3xl font-extrabold my-1 ${
                    fhiDelta > 0 ? "text-emerald-600" : fhiDelta < 0 ? "text-rose-600" : "text-slate-600"
                  }`}>
                    {fhiDelta > 0 ? `+${fhiDelta}` : `${fhiDelta}`} pts
                  </div>
                  <div className="text-xs text-slate-500 mt-1 break-words">
                    {currFhi} → <strong className="text-slate-800">{scenFhi} / 100</strong> ({comp?.financial_health_direction})
                  </div>
                </div>
              </div>

              {/* Narrative Summary */}
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-xs space-y-2 w-full max-w-full">
                <div className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Simulation Outcome Narrative
                </div>
                <p className="text-xs text-slate-700 leading-relaxed break-words">
                  {comp?.summary}
                </p>
              </div>

              {/* Resolved Factors & Gained Strengths */}
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-xs space-y-4 w-full max-w-full">
                {comp?.risk_factors_resolved && comp.risk_factors_resolved.length > 0 && (
                  <div className="w-full max-w-full">
                    <div className="text-xs font-bold text-emerald-800 mb-2 flex items-center space-x-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span className="break-words">{t("sim_resolved_factors_title")}</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {comp.risk_factors_resolved.map((f, idx) => (
                        <span key={idx} className="bg-emerald-50 text-emerald-800 border border-emerald-300 text-xs px-2.5 py-1 rounded-md font-semibold break-words">
                          ✓ {f.human_label}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {comp?.positive_factors_gained && comp.positive_factors_gained.length > 0 && (
                  <div className="w-full max-w-full">
                    <div className="text-xs font-bold text-emerald-800 mb-2 flex items-center space-x-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span className="break-words">{t("sim_gained_strengths_title")}</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {comp.positive_factors_gained.map((f, idx) => (
                        <span key={idx} className="bg-sky-50 text-sky-800 border border-sky-300 text-xs px-2.5 py-1 rounded-md font-semibold break-words">
                          + {f.human_label}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Disclaimers */}
      <div className="bg-slate-100 border-l-4 border-slate-500 rounded p-4 text-xs text-slate-600 space-y-1 break-words leading-relaxed w-full max-w-full">
        <p><strong>⚖️ Simulation Disclaimer:</strong> {t("disclaimer_simulation")}</p>
      </div>
    </div>
  );
};
