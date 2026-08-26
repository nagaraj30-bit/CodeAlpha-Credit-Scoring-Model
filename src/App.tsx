import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { OverviewView } from "./components/OverviewView";
import { LoginPage } from "./components/LoginPage";
import { AssessmentForm } from "./components/AssessmentForm";
import { ResultView } from "./components/ResultView";
import { ExplainView } from "./components/ExplainView";
import { FinancialHealthView } from "./components/FinancialHealthView";
import { SimulatorView } from "./components/SimulatorView";
import { FairnessView } from "./components/FairnessView";
import { InsightsView } from "./components/InsightsView";
import { Language, ApplicantData, PredictionResult, ExplainabilityResult, FinancialHealthResult, ScenarioResult } from "./types";
import { getT } from "./i18n";

// Verified Benchmark Baseline Defaults (UCI Index 0 - Delinquent Sample)
const DEFAULT_APPLICANT: ApplicantData = {
  LIMIT_BAL: 20000.0,
  SEX: 2,
  EDUCATION: 2,
  MARRIAGE: 1,
  AGE: 24,
  PAY_0: 2,
  PAY_2: 2,
  PAY_3: -1,
  PAY_4: -1,
  PAY_5: -2,
  PAY_6: -2,
  BILL_AMT1: 3913.0,
  BILL_AMT2: 3102.0,
  BILL_AMT3: 689.0,
  BILL_AMT4: 0.0,
  BILL_AMT5: 0.0,
  BILL_AMT6: 0.0,
  PAY_AMT1: 0.0,
  PAY_AMT2: 689.0,
  PAY_AMT3: 0.0,
  PAY_AMT4: 0.0,
  PAY_AMT5: 0.0,
  PAY_AMT6: 0.0,
};

export default function App() {
  const [currentLang, setCurrentLang] = useState<Language>("en");
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [applicant, setApplicant] = useState<ApplicantData>(DEFAULT_APPLICANT);

  // Authenticated user state
  const [currentUser, setCurrentUser] = useState<{ name: string; role: string; email: string } | null>(null);

  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [explanation, setExplanation] = useState<ExplainabilityResult | null>(null);
  const [financialHealth, setFinancialHealth] = useState<FinancialHealthResult | null>(null);
  const [scenarioResult, setScenarioResult] = useState<ScenarioResult | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Initial Assessment on mount (pre-warms the cache & state)
  useEffect(() => {
    runFullAssessment(DEFAULT_APPLICANT, false);
  }, []);

  const runFullAssessment = async (data: ApplicantData, shouldNavigate = true) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/assess-full", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ applicant: data }),
      });
      const json = await res.json();
      if (json.success) {
        setApplicant(data);
        setPrediction(json.prediction);
        setExplanation(json.explanation);
        setFinancialHealth(json.financial_health);
        setScenarioResult(null); // reset scenario on new baseline assessment
        if (shouldNavigate) {
          setActiveTab("result");
        }
      } else {
        setErrorMsg(json.error || "Failed to evaluate credit profile");
      }
    } catch (err: any) {
      console.error("API error:", err);
      setErrorMsg("Network error connecting to machine learning engine");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSimulateCustom = async (modifications: Partial<ApplicantData>) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          applicant,
          modifications,
        }),
      });
      const json = await res.json();
      if (json.success) {
        setScenarioResult(json.data);
      } else {
        setErrorMsg(json.error || "Failed to simulate scenario");
      }
    } catch (err: any) {
      console.error("Simulation error:", err);
      setErrorMsg("Error executing What-If simulation");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSimulatePreset = async (preset: "remediate" | "paydown_50" | "paydown_80" | "limit_increase") => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/simulate-preset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          applicant,
          preset,
        }),
      });
      const json = await res.json();
      if (json.success) {
        setScenarioResult(json.data);
      } else {
        setErrorMsg(json.error || "Failed to simulate preset");
      }
    } catch (err: any) {
      console.error("Preset simulation error:", err);
      setErrorMsg("Error executing preset simulation");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadSample = async (sampleType: "prime" | "revolving" | "delinquent") => {
    try {
      const res = await fetch("/api/samples");
      const samples = await res.json();
      const sample = samples[sampleType];
      if (sample) {
        await runFullAssessment(sample, true);
      }
    } catch (err) {
      console.error("Failed to load sample:", err);
    }
  };

  const handleLoginSuccess = (user: { name: string; role: string; email: string }) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setActiveTab("overview");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans w-full max-w-full overflow-x-hidden">
      <Header
        currentLang={currentLang}
        onLanguageChange={(lang) => setCurrentLang(lang)}
        activeTab={activeTab}
        onTabChange={(tab) => setActiveTab(tab)}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {errorMsg && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4 w-full max-w-full">
          <div className="bg-rose-50 border border-rose-200 text-rose-800 text-xs p-3 rounded-lg flex items-center justify-between w-full max-w-full">
            <span>⚠️ {errorMsg}</span>
            <button onClick={() => setErrorMsg(null)} className="text-rose-600 font-bold hover:text-rose-900">
              ✕
            </button>
          </div>
        </div>
      )}

      <main className="flex-1 max-w-7xl w-full max-w-full mx-auto px-3 sm:px-6 lg:px-8 py-5 sm:py-8 overflow-x-hidden">
        {activeTab === "overview" && (
          <OverviewView
            currentLang={currentLang}
            onNavigate={(tab) => setActiveTab(tab)}
            onLoadSample={handleLoadSample}
          />
        )}

        {activeTab === "login" && (
          <LoginPage
            currentLang={currentLang}
            onLoginSuccess={handleLoginSuccess}
            onNavigate={(tab) => setActiveTab(tab)}
          />
        )}

        {activeTab === "assess" && (
          <AssessmentForm
            currentLang={currentLang}
            applicant={applicant}
            isLoading={isLoading}
            onSubmit={(data) => runFullAssessment(data, true)}
            onReset={() => setApplicant(DEFAULT_APPLICANT)}
          />
        )}

        {activeTab === "result" && prediction && explanation && financialHealth && (
          <ResultView
            currentLang={currentLang}
            prediction={prediction}
            explanation={explanation}
            financialHealth={financialHealth}
            onNavigate={(tab) => setActiveTab(tab)}
          />
        )}

        {activeTab === "explain" && explanation && (
          <ExplainView
            currentLang={currentLang}
            explanation={explanation}
          />
        )}

        {activeTab === "financial_health" && financialHealth && (
          <FinancialHealthView
            currentLang={currentLang}
            financialHealth={financialHealth}
          />
        )}

        {activeTab === "simulator" && (
          <SimulatorView
            currentLang={currentLang}
            applicant={applicant}
            scenarioResult={scenarioResult}
            isLoading={isLoading}
            onSimulateCustom={handleSimulateCustom}
            onSimulatePreset={handleSimulatePreset}
            onReset={() => setScenarioResult(null)}
          />
        )}

        {activeTab === "fairness" && (
          <FairnessView currentLang={currentLang} />
        )}

        {activeTab === "insights" && (
          <InsightsView currentLang={currentLang} />
        )}
      </main>

      <footer className="bg-white border-t border-slate-200 py-4 sm:py-6 text-center text-xs text-slate-500 w-full max-w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-1 break-words w-full max-w-full">
          <p className="font-semibold text-slate-700">Credit Intelligence & Risk Engine — Production ML Platform</p>
          <p>Scored via Audited Random Forest Pipeline (ROC-AUC 0.7744) · UCI Default of Credit Card Clients Dataset</p>
        </div>
      </footer>
    </div>
  );
}
