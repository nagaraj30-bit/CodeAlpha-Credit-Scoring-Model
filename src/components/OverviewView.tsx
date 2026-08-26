import React from "react";
import { Language, ApplicantData } from "../types";
import { getT } from "../i18n";
import { Cpu, Eye, HeartPulse, Sliders, ArrowRight, ShieldAlert, Sparkles, CheckCircle, Scale } from "lucide-react";

interface OverviewViewProps {
  currentLang: Language;
  onNavigate: (tab: string) => void;
  onLoadSample: (sampleType: "prime" | "revolving" | "delinquent") => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  currentLang,
  onNavigate,
  onLoadSample,
}) => {
  const t = getT(currentLang);

  return (
    <div className="space-y-8 max-w-6xl w-full max-w-full mx-auto">
      {/* Hero Section */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 sm:p-8 shadow-xs w-full max-w-full">
        <div className="max-w-3xl w-full max-w-full">
          <div className="inline-flex items-center space-x-2 bg-sky-50 text-sky-700 text-xs font-semibold px-3 py-1 rounded-full border border-sky-200 mb-4 max-w-full">
            <Sparkles className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">{t("app_badge")}</span>
          </div>
          <h2 className="text-xl sm:text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight leading-tight break-words">
            {t("overview_hero_title")}
          </h2>
          <p className="mt-3 sm:mt-4 text-slate-600 text-sm sm:text-base leading-relaxed break-words">
            {t("overview_hero_desc")}
          </p>

          <div className="mt-6 flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-3 w-full max-w-full">
            <button
              id="hero-btn-assess"
              onClick={() => onNavigate("assess")}
              className="inline-flex items-center justify-center space-x-2 bg-sky-600 hover:bg-sky-700 text-white font-semibold text-sm px-5 py-3 sm:py-2.5 rounded-lg shadow-xs transition min-h-[44px]"
            >
              <span>{t("btn_assess_risk")}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              id="hero-btn-simulator"
              onClick={() => onNavigate("simulator")}
              className="inline-flex items-center justify-center space-x-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-sm px-5 py-3 sm:py-2.5 rounded-lg transition min-h-[44px]"
            >
              <Sliders className="w-4 h-4 text-sky-600" />
              <span>{t("btn_explore_what_if")}</span>
            </button>
            <button
              id="hero-btn-fairness"
              onClick={() => onNavigate("fairness")}
              className="inline-flex items-center justify-center space-x-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-sm px-5 py-3 sm:py-2.5 rounded-lg transition min-h-[44px]"
            >
              <Scale className="w-4 h-4 text-sky-600" />
              <span>{t("nav_fairness")}</span>
            </button>
          </div>
        </div>
      </div>

      {/* 4 Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 w-full max-w-full">
        <div className="bg-white rounded-xl border border-slate-200 p-5 sm:p-6 shadow-xs flex flex-col justify-between min-w-0 w-full max-w-full">
          <div>
            <div className="w-10 h-10 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center mb-4">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-2 break-words">{t("overview_card1_title")}</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed break-words">{t("overview_card1_desc")}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 sm:p-6 shadow-xs flex flex-col justify-between min-w-0 w-full max-w-full">
          <div>
            <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
              <Eye className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-2 break-words">{t("overview_card2_title")}</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed break-words">{t("overview_card2_desc")}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 sm:p-6 shadow-xs flex flex-col justify-between min-w-0 w-full max-w-full">
          <div>
            <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
              <HeartPulse className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-2 break-words">{t("overview_card3_title")}</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed break-words">{t("overview_card3_desc")}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 sm:p-6 shadow-xs flex flex-col justify-between min-w-0 w-full max-w-full">
          <div>
            <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center mb-4">
              <Sliders className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-2 break-words">{t("overview_card4_title")}</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed break-words">{t("overview_card4_desc")}</p>
          </div>
        </div>
      </div>

      {/* Quick Start Loaders */}
      <div className="bg-slate-900 text-white rounded-xl p-5 sm:p-6 border border-slate-800 w-full max-w-full">
        <div className="flex items-center space-x-2 mb-3 sm:mb-4">
          <CheckCircle className="w-5 h-5 text-sky-400 shrink-0" />
          <h3 className="text-base font-bold text-white">{t("overview_quick_start")}</h3>
        </div>
        <p className="text-xs text-slate-400 mb-4 break-words leading-relaxed">
          Load verified benchmark credit profiles from the UCI dataset to immediately test risk evaluation, explainability breakdowns, and What-If simulations.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full max-w-full">
          <button
            id="btn-sample-prime"
            onClick={() => onLoadSample("prime")}
            className="flex items-center justify-between p-3.5 rounded-lg bg-slate-800 hover:bg-slate-750 border border-slate-700 hover:border-emerald-500 transition text-left min-h-[44px] min-w-0 w-full max-w-full"
          >
            <div className="min-w-0">
              <div className="text-xs font-bold text-emerald-400 break-words">{t("overview_sample_prime")}</div>
              <div className="text-[11px] text-slate-400 mt-0.5 break-words">NT$90K Limit · On-Time Payments</div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate-400 shrink-0 ml-2" />
          </button>

          <button
            id="btn-sample-revolving"
            onClick={() => onLoadSample("revolving")}
            className="flex items-center justify-between p-3.5 rounded-lg bg-slate-800 hover:bg-slate-750 border border-slate-700 hover:border-amber-500 transition text-left min-h-[44px] min-w-0 w-full max-w-full"
          >
            <div className="min-w-0">
              <div className="text-xs font-bold text-amber-400 break-words">{t("overview_sample_revolving")}</div>
              <div className="text-[11px] text-slate-400 mt-0.5 break-words">NT$50K Limit · 95% High Utilization</div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate-400 shrink-0 ml-2" />
          </button>

          <button
            id="btn-sample-delinquent"
            onClick={() => onLoadSample("delinquent")}
            className="flex items-center justify-between p-3.5 rounded-lg bg-slate-800 hover:bg-slate-750 border border-slate-700 hover:border-rose-500 transition text-left min-h-[44px] min-w-0 w-full max-w-full"
          >
            <div className="min-w-0">
              <div className="text-xs font-bold text-rose-400 break-words">{t("overview_sample_delinquent")}</div>
              <div className="text-[11px] text-slate-400 mt-0.5 break-words">NT$20K Limit · 2 Mo Past Due</div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate-400 shrink-0 ml-2" />
          </button>
        </div>
      </div>

      {/* Disclaimers Banner */}
      <div className="bg-slate-100 border-l-4 border-slate-500 rounded p-4 text-xs text-slate-600 space-y-1 leading-relaxed w-full max-w-full break-words">
        <p><strong>⚖️ Educational Notice:</strong> {t("disclaimer_legal")}</p>
        <p><strong>🔒 Privacy By Design:</strong> {t("disclaimer_privacy")}</p>
      </div>
    </div>
  );
};
