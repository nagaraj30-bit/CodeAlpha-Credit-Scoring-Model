import React from "react";
import { Language } from "../types";
import { getT } from "../i18n";
import { ShieldCheck, Globe, User, LogOut, Lock } from "lucide-react";

interface HeaderProps {
  currentLang: Language;
  onLanguageChange: (lang: Language) => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
  currentUser?: { name: string; role: string; email: string } | null;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentLang,
  onLanguageChange,
  activeTab,
  onTabChange,
  currentUser,
  onLogout,
}) => {
  const t = getT(currentLang);

  const tabs = [
    { id: "overview", label: t("nav_overview") },
    { id: "assess", label: t("nav_assess") },
    { id: "result", label: t("nav_result") },
    { id: "explain", label: t("nav_explain") },
    { id: "financial_health", label: t("nav_financial_health") },
    { id: "simulator", label: t("nav_simulator") },
    { id: "fairness", label: t("nav_fairness") },
    { id: "insights", label: t("nav_insights") },
  ];

  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50 w-full max-w-full">
      {/* Top Banner */}
      <div className="max-w-7xl w-full max-w-full mx-auto px-3 sm:px-6 lg:px-8 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
        {/* Brand & Version */}
        <div className="flex items-center space-x-3 min-w-0 max-w-full">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-sky-600 flex items-center justify-center text-white shadow-sm shrink-0">
            <ShieldCheck className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center space-x-2 flex-wrap">
              <h1 className="text-base sm:text-lg font-bold tracking-tight text-white truncate">
                {t("app_title")}
              </h1>
              <span className="bg-sky-950 text-sky-300 text-[10px] sm:text-xs px-2 py-0.5 rounded border border-sky-800 font-mono shrink-0">
                v1.0 RF Production
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-400 truncate">{t("app_subtitle")}</p>
          </div>
        </div>

        {/* Right Section: Language Switcher & Officer Auth */}
        <div className="flex items-center justify-between sm:justify-end space-x-2 sm:space-x-3 flex-wrap gap-y-2 max-w-full">
          {/* Language Selector */}
          <div className="flex items-center space-x-1.5 sm:space-x-2">
            <Globe className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-400 shrink-0" />
            <span className="text-[11px] sm:text-xs text-slate-400 font-medium hidden md:inline">
              {t("btn_switch_language")}:
            </span>
            <div className="inline-flex rounded-md shadow-sm border border-slate-700 bg-slate-800 p-0.5">
              <button
                id="lang-btn-en"
                type="button"
                onClick={() => onLanguageChange("en")}
                className={`px-2.5 sm:px-3 py-1 text-xs font-semibold rounded min-h-[32px] sm:min-h-[28px] transition ${
                  currentLang === "en"
                    ? "bg-sky-600 text-white shadow-xs"
                    : "text-slate-300 hover:text-white"
                }`}
              >
                English
              </button>
              <button
                id="lang-btn-ta"
                type="button"
                onClick={() => onLanguageChange("ta")}
                className={`px-2.5 sm:px-3 py-1 text-xs font-semibold rounded min-h-[32px] sm:min-h-[28px] transition ${
                  currentLang === "ta"
                    ? "bg-sky-600 text-white shadow-xs"
                    : "text-slate-300 hover:text-white"
                }`}
              >
                தமிழ்
              </button>
              <button
                id="lang-btn-hi"
                type="button"
                onClick={() => onLanguageChange("hi")}
                className={`px-2.5 sm:px-3 py-1 text-xs font-semibold rounded min-h-[32px] sm:min-h-[28px] transition ${
                  currentLang === "hi"
                    ? "bg-sky-600 text-white shadow-xs"
                    : "text-slate-300 hover:text-white"
                }`}
              >
                हिन्दी
              </button>
            </div>
          </div>

          {/* User Status / Officer Login Portal Button */}
          {currentUser ? (
            <div className="flex items-center space-x-2 bg-slate-800 border border-slate-700 px-2.5 py-1 rounded-md">
              <User className="w-3.5 h-3.5 text-sky-400 shrink-0" />
              <div className="text-left">
                <div className="text-xs font-bold text-white truncate max-w-[100px] sm:max-w-[120px]">{currentUser.name}</div>
                <div className="text-[10px] text-sky-300">{currentUser.role}</div>
              </div>
              {onLogout && (
                <button
                  id="btn-logout"
                  type="button"
                  onClick={onLogout}
                  title="Sign Out"
                  className="text-slate-400 hover:text-rose-400 p-1 transition"
                >
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          ) : (
            <button
              id="nav-login-btn"
              type="button"
              onClick={() => onTabChange("login")}
              className={`inline-flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold rounded-md border min-h-[32px] sm:min-h-[28px] transition ${
                activeTab === "login"
                  ? "bg-sky-600 border-sky-500 text-white"
                  : "bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700 hover:text-white"
              }`}
            >
              <Lock className="w-3 h-3 text-sky-400" />
              <span>Officer Portal</span>
            </button>
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-slate-950 border-t border-slate-800 w-full max-w-full">
        <div className="max-w-7xl w-full max-w-full mx-auto px-2 sm:px-6 lg:px-8">
          <nav className="flex space-x-1 overflow-x-auto no-scrollbar py-2 touch-pan-x w-full max-w-full">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                id={`nav-${tab.id}`}
                onClick={() => onTabChange(tab.id)}
                className={`whitespace-nowrap px-3 sm:px-3.5 py-2 sm:py-1.5 text-xs font-medium rounded-md transition-colors min-h-[36px] sm:min-h-[32px] shrink-0 ${
                  activeTab === tab.id
                    ? "bg-sky-600 text-white shadow-xs"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
};

