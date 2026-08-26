import React, { useState } from "react";
import { Language } from "../types";
import { getT } from "../i18n";
import { ShieldCheck, UserCheck, KeyRound, Sparkles, ArrowRight, Lock, Building2, Eye, EyeOff, User, CheckCircle2 } from "lucide-react";

interface LoginPageProps {
  currentLang: Language;
  onLoginSuccess: (user: { name: string; role: string; email: string }) => void;
  onNavigate: (tab: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  currentLang,
  onLoginSuccess,
  onNavigate,
}) => {
  const t = getT(currentLang);
  const [email, setEmail] = useState("officer.vance@credit-intelligence.ai");
  const [password, setPassword] = useState("••••••••••••");
  const [selectedRole, setSelectedRole] = useState<"officer" | "analyst" | "auditor" | "guest">("officer");
  const [showPassword, setShowPassword] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authStep, setAuthStep] = useState<string>("");

  const handleLogin = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsAuthenticating(true);
    setAuthStep("Authenticating Security Credentials...");

    setTimeout(() => {
      setAuthStep("Establishing Secure Session Token...");
      setTimeout(() => {
        setAuthStep("Connecting to Random Forest Risk Engine...");
        setTimeout(() => {
          const roleLabels = {
            officer: "Senior Credit Underwriter",
            analyst: "Quantitative Risk Analyst",
            auditor: "Model Governance Auditor",
            guest: "Applicant Self-Assessment Mode",
          };
          const names = {
            officer: "Alex Vance",
            analyst: "Dr. Elena Rostova",
            auditor: "Marcus Chen",
            guest: "Guest Applicant",
          };

          setIsAuthenticating(false);
          onLoginSuccess({
            name: names[selectedRole],
            role: roleLabels[selectedRole],
            email: selectedRole === "guest" ? "guest@session.local" : email,
          });
          // Immediately navigate to the credit assessment page
          onNavigate("assess");
        }, 350);
      }, 350);
    }, 350);
  };

  const handleQuickDemo = (role: "officer" | "guest") => {
    setSelectedRole(role);
    if (role === "guest") {
      setEmail("guest.applicant@credit-intelligence.ai");
    } else {
      setEmail("officer.vance@credit-intelligence.ai");
    }
    handleLogin();
  };

  return (
    <div className="max-w-4xl w-full max-w-full mx-auto py-4 sm:py-6 px-3 sm:px-6">
      {/* Back button */}
      <div className="mb-4 sm:mb-6 w-full max-w-full">
        <button
          onClick={() => onNavigate("overview")}
          className="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center space-x-1.5 transition min-h-[36px]"
        >
          <span>← Back to Overview</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-8 items-stretch w-full max-w-full">
        {/* Left Side: Cinematic Branding & Portal Info */}
        <div className="lg:col-span-5 bg-gradient-to-br from-slate-900 via-slate-850 to-slate-950 text-white rounded-2xl p-5 sm:p-8 border border-slate-800 flex flex-col justify-between shadow-lg relative overflow-hidden min-w-0 w-full max-w-full">
          <div className="absolute top-0 right-0 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
          
          <div className="relative z-10 w-full max-w-full">
            <div className="inline-flex items-center space-x-2 bg-sky-950/80 border border-sky-700/60 text-sky-300 text-xs px-3 py-1 rounded-full font-mono mb-4 sm:mb-6 max-w-full">
              <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
              <span className="break-words">Officer & Underwriter Gateway</span>
            </div>

            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white leading-snug break-words">
              Secure Credit Intelligence Access
            </h2>
            <p className="mt-2.5 sm:mt-3 text-xs text-slate-300 leading-relaxed break-words">
              Sign in to initiate deterministic credit risk assessments, evaluate local Shapley feature attributions, and simulate counterfactual credit outcomes.
            </p>

            <div className="mt-6 sm:mt-8 space-y-2.5 sm:space-y-3 w-full max-w-full">
              <div className="flex items-start space-x-3 text-xs text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span className="break-words">Production Random Forest ML Pipeline (ROC-AUC 0.7744)</span>
              </div>
              <div className="flex items-start space-x-3 text-xs text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span className="break-words">Deterministic 5-Pillar Financial Health Engine (FHI-5)</span>
              </div>
              <div className="flex items-start space-x-3 text-xs text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span className="break-words">Zero PII Storage & Complete Demographic Fairness Audit</span>
              </div>
            </div>
          </div>

          <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-slate-800 text-[11px] text-slate-400 flex flex-wrap items-center justify-between gap-2 relative z-10 w-full max-w-full">
            <span>Security: TLS 1.3 · Local AES</span>
            <span className="text-emerald-400 font-medium">● System Online</span>
          </div>
        </div>

        {/* Right Side: Authentication Form */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 p-5 sm:p-8 shadow-xs flex flex-col justify-between min-w-0 w-full max-w-full">
          <div className="w-full max-w-full">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-5 sm:mb-6 w-full max-w-full">
              <div className="min-w-0">
                <h3 className="text-base sm:text-lg font-bold text-slate-900 break-words">Portal Authentication</h3>
                <p className="text-xs text-slate-500 mt-0.5 break-words">Select your role or click instant demo access</p>
              </div>
              <div className="w-9 h-9 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center font-bold shrink-0">
                <Lock className="w-4 h-4" />
              </div>
            </div>

            {/* Quick Demo Access Bar */}
            <div className="mb-5 sm:mb-6 bg-slate-50 border border-slate-200 rounded-xl p-3 sm:p-3.5 w-full max-w-full">
              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2">
                ⚡ Instant Single-Click Demo Access
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-full">
                <button
                  type="button"
                  id="btn-demo-officer"
                  disabled={isAuthenticating}
                  onClick={() => handleQuickDemo("officer")}
                  className="inline-flex items-center justify-center space-x-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold py-2.5 sm:py-2 px-3 rounded-lg transition shadow-xs disabled:opacity-50 min-h-[44px] sm:min-h-[38px] min-w-0 w-full max-w-full"
                >
                  <Building2 className="w-3.5 h-3.5 shrink-0" />
                  <span>Credit Officer Demo</span>
                </button>
                <button
                  type="button"
                  id="btn-demo-guest"
                  disabled={isAuthenticating}
                  onClick={() => handleQuickDemo("guest")}
                  className="inline-flex items-center justify-center space-x-2 bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-semibold py-2.5 sm:py-2 px-3 rounded-lg transition disabled:opacity-50 min-h-[44px] sm:min-h-[38px] min-w-0 w-full max-w-full"
                >
                  <User className="w-3.5 h-3.5 shrink-0" />
                  <span>Guest Applicant</span>
                </button>
              </div>
            </div>

            {/* Main Form */}
            <form onSubmit={handleLogin} className="space-y-4 w-full max-w-full">
              {/* Role Selection */}
              <div className="w-full max-w-full">
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Operating Persona / Role
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 w-full max-w-full">
                  {[
                    { id: "officer", label: "Risk Officer", icon: Building2 },
                    { id: "analyst", label: "Quant Analyst", icon: Sparkles },
                    { id: "auditor", label: "Bias Auditor", icon: ShieldCheck },
                    { id: "guest", label: "Applicant", icon: User },
                  ].map((r) => {
                    const Icon = r.icon;
                    const isSelected = selectedRole === r.id;
                    return (
                      <button
                        key={r.id}
                        type="button"
                        onClick={() => setSelectedRole(r.id as any)}
                        className={`p-2.5 rounded-lg border text-center transition flex flex-col items-center justify-center space-y-1 min-h-[54px] min-w-0 w-full max-w-full ${
                          isSelected
                            ? "bg-sky-50 border-sky-600 text-sky-900 font-bold"
                            : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                        }`}
                      >
                        <Icon className={`w-4 h-4 ${isSelected ? "text-sky-600" : "text-slate-400"} shrink-0`} />
                        <span className="text-[11px] whitespace-nowrap">{r.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Email/Username */}
              <div className="w-full max-w-full">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Officer ID / Work Email
                </label>
                <div className="relative w-full max-w-full">
                  <UserCheck className="w-4 h-4 text-slate-400 absolute left-3 top-3 sm:top-2.5 pointer-events-none" />
                  <input
                    type="text"
                    id="input-login-email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full max-w-full min-w-0 pl-9 pr-3 py-2.5 sm:py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white min-h-[44px] sm:min-h-[38px] box-border"
                    placeholder="officer@credit-intelligence.ai"
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div className="w-full max-w-full">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Security Passcode / Token
                </label>
                <div className="relative w-full max-w-full">
                  <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-3 sm:top-2.5 pointer-events-none" />
                  <input
                    type={showPassword ? "text" : "password"}
                    id="input-login-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full max-w-full min-w-0 pl-9 pr-9 py-2.5 sm:py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white min-h-[44px] sm:min-h-[38px] box-border"
                    placeholder="••••••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 sm:top-2.5 text-slate-400 hover:text-slate-600 p-0.5"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-2 text-xs pt-1 w-full max-w-full">
                <label className="flex items-center space-x-2 text-slate-600 cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded border-slate-300 text-sky-600 focus:ring-sky-500" />
                  <span>Remember session token</span>
                </label>
                <span className="text-sky-600 hover:underline cursor-pointer">Demo Sandbox Mode</span>
              </div>

              {/* Submit CTA */}
              <div className="pt-2 w-full max-w-full">
                <button
                  type="submit"
                  id="btn-login-submit"
                  disabled={isAuthenticating}
                  className="w-full max-w-full bg-slate-900 hover:bg-slate-850 text-white text-xs sm:text-sm font-bold py-3.5 sm:py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition shadow-md disabled:opacity-75 min-h-[48px] sm:min-h-[44px]"
                >
                  {isAuthenticating ? (
                    <div className="flex items-center space-x-2 text-sky-300">
                      <div className="w-4 h-4 border-2 border-sky-400 border-t-transparent rounded-full animate-spin"></div>
                      <span className="break-words">{authStep}</span>
                    </div>
                  ) : (
                    <>
                      <span className="break-words">Enter Credit Assessment Engine</span>
                      <ArrowRight className="w-4 h-4 shrink-0" />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400 w-full max-w-full">
            <span>Encrypted Session · Zero Third-Party Tracking</span>
            <button
              type="button"
              onClick={() => onNavigate("assess")}
              className="text-sky-600 font-semibold hover:underline"
            >
              Skip Directly to Assessment →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
