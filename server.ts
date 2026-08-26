import { execFile } from "child_process";
import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import {
  predictCreditRisk,
  calculateFinancialHealth,
  explainPrediction,
  simulateScenario,
  simulateRemediation,
  simulatePaydown,
  simulateLimitIncrease,
} from "./src/engine/creditEngine";
import { getFairnessAudit } from "./src/engine/fairnessEngine";
import { TRANSLATIONS } from "./src/i18n";

const app = express();
const PORT = 3000;

app.use(express.json());

// Helper function to call Python API Runner with seamless TypeScript fallback
function runPythonApi(action: string, payload: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const requestJson = JSON.stringify({ action, payload });
    execFile(
      "python3",
      ["src/api_runner.py", requestJson],
      { timeout: 15000, maxBuffer: 10 * 1024 * 1024 },
      (error, stdout, stderr) => {
        if (error) {
          // Python runtime is not configured or missing numpy/dependencies
          return reject(error);
        }
        try {
          const parsed = JSON.parse(stdout.trim());
          if (parsed.status === "success") {
            resolve(parsed.data);
          } else {
            reject(new Error(parsed.message || "Unknown error in Python engine"));
          }
        } catch (e) {
          reject(e);
        }
      }
    );
  });
}

// ----------------------------------------------------------------------------
// API ROUTES
// ----------------------------------------------------------------------------
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", engine: "credit_scoring_production_rf" });
});

// Sample Profiles
app.get("/api/samples", (req, res) => {
  res.json({
    prime: {
      LIMIT_BAL: 90000.0, SEX: 2, EDUCATION: 2, MARRIAGE: 2, AGE: 34,
      PAY_0: 0, PAY_2: 0, PAY_3: 0, PAY_4: 0, PAY_5: 0, PAY_6: 0,
      BILL_AMT1: 29239.0, BILL_AMT2: 14027.0, BILL_AMT3: 13559.0,
      BILL_AMT4: 14331.0, BILL_AMT5: 14948.0, BILL_AMT6: 15549.0,
      PAY_AMT1: 1518.0, PAY_AMT2: 1500.0, PAY_AMT3: 1000.0,
      PAY_AMT4: 1000.0, PAY_AMT5: 1000.0, PAY_AMT6: 5000.0
    },
    revolving: {
      LIMIT_BAL: 50000.0, SEX: 1, EDUCATION: 1, MARRIAGE: 2, AGE: 30,
      PAY_0: 0, PAY_2: 0, PAY_3: 0, PAY_4: 0, PAY_5: 0, PAY_6: 0,
      BILL_AMT1: 48500.0, BILL_AMT2: 49000.0, BILL_AMT3: 47800.0,
      BILL_AMT4: 46000.0, BILL_AMT5: 45000.0, BILL_AMT6: 44000.0,
      PAY_AMT1: 2000.0, PAY_AMT2: 2000.0, PAY_AMT3: 2000.0,
      PAY_AMT4: 2000.0, PAY_AMT5: 2000.0, PAY_AMT6: 2000.0
    },
    delinquent: {
      LIMIT_BAL: 20000.0, SEX: 2, EDUCATION: 2, MARRIAGE: 1, AGE: 24,
      PAY_0: 2, PAY_2: 2, PAY_3: -1, PAY_4: -1, PAY_5: -2, PAY_6: -2,
      BILL_AMT1: 3913.0, BILL_AMT2: 3102.0, BILL_AMT3: 689.0,
      BILL_AMT4: 0.0, BILL_AMT5: 0.0, BILL_AMT6: 0.0,
      PAY_AMT1: 0.0, PAY_AMT2: 689.0, PAY_AMT3: 0.0,
      PAY_AMT4: 0.0, PAY_AMT5: 0.0, PAY_AMT6: 0.0
    }
  });
});

// Full Assessment (Predict + Explain + Financial Health in one atomic call)
app.post("/api/assess-full", async (req, res) => {
  const applicant = req.body.applicant || {};
  try {
    const fullResult = await runPythonApi("assess_full", { applicant });
    return res.json({
      success: true,
      prediction: fullResult.prediction,
      explanation: fullResult.explanation,
      financial_health: fullResult.financial_health,
    });
  } catch (_pyErr) {
    // Fallback to high-performance TypeScript engine
    try {
      const prediction = predictCreditRisk(applicant);
      const financial_health = calculateFinancialHealth(applicant);
      const explanation = explainPrediction(applicant, prediction);
      return res.json({
        success: true,
        prediction,
        explanation,
        financial_health,
      });
    } catch (err: any) {
      return res.status(500).json({ success: false, error: err.message || "Assessment failed" });
    }
  }
});

// Single Prediction
app.post("/api/predict", async (req, res) => {
  const applicant = req.body.applicant || {};
  try {
    const result = await runPythonApi("predict", { applicant });
    return res.json({ success: true, data: result });
  } catch (_pyErr) {
    try {
      const result = predictCreditRisk(applicant);
      return res.json({ success: true, data: result });
    } catch (err: any) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }
});

// Explainability
app.post("/api/explain", async (req, res) => {
  const applicant = req.body.applicant || {};
  const prediction = req.body.prediction;
  try {
    const result = await runPythonApi("explain", { applicant, prediction });
    return res.json({ success: true, data: result });
  } catch (_pyErr) {
    try {
      const result = explainPrediction(applicant, prediction);
      return res.json({ success: true, data: result });
    } catch (err: any) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }
});

// Financial Health Indicator
app.post("/api/financial-health", async (req, res) => {
  const applicant = req.body.applicant || {};
  try {
    const result = await runPythonApi("financial_health", { applicant });
    return res.json({ success: true, data: result });
  } catch (_pyErr) {
    try {
      const result = calculateFinancialHealth(applicant);
      return res.json({ success: true, data: result });
    } catch (err: any) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }
});

// What-If Scenario Simulation
app.post("/api/simulate", async (req, res) => {
  const applicant = req.body.applicant || {};
  const modifications = req.body.modifications || {};
  try {
    const result = await runPythonApi("simulate", { applicant, modifications });
    return res.json({ success: true, data: result });
  } catch (_pyErr) {
    try {
      const result = simulateScenario(applicant, modifications);
      return res.json({ success: true, data: result });
    } catch (err: any) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }
});

// Scenario Presets
app.post("/api/simulate-preset", async (req, res) => {
  const preset = req.body.preset;
  const applicant = req.body.applicant || {};
  try {
    let result;
    if (preset === "remediate") {
      result = await runPythonApi("simulate_remediation", { applicant });
    } else if (preset === "paydown_50") {
      result = await runPythonApi("simulate_paydown", { applicant, fraction: 0.50 });
    } else if (preset === "paydown_80") {
      result = await runPythonApi("simulate_paydown", { applicant, fraction: 0.80 });
    } else if (preset === "limit_increase") {
      const newLimit = (applicant.LIMIT_BAL || 50000) * 1.5;
      result = await runPythonApi("simulate_limit_increase", { applicant, new_limit: newLimit });
    } else {
      return res.status(400).json({ success: false, error: "Invalid preset" });
    }
    return res.json({ success: true, data: result });
  } catch (_pyErr) {
    try {
      let result;
      if (preset === "remediate") {
        result = simulateRemediation(applicant);
      } else if (preset === "paydown_50") {
        result = simulatePaydown(applicant, 0.50);
      } else if (preset === "paydown_80") {
        result = simulatePaydown(applicant, 0.80);
      } else if (preset === "limit_increase") {
        const newLimit = (applicant.LIMIT_BAL || 50000) * 1.5;
        result = simulateLimitIncrease(applicant, newLimit);
      } else {
        return res.status(400).json({ success: false, error: "Invalid preset" });
      }
      return res.json({ success: true, data: result });
    } catch (err: any) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }
});

// Translations & i18n
app.get("/api/translations", async (req, res) => {
  try {
    const result = await runPythonApi("get_translations", {});
    return res.json({ success: true, data: result });
  } catch (_pyErr) {
    return res.json({
      success: true,
      data: {
        translations: TRANSLATIONS,
        supported_languages: ["en", "ta", "hi"],
      },
    });
  }
});

// Fairness & Model Evaluation Audit
app.get("/api/fairness", async (req, res) => {
  const attribute = req.query.attribute as string | undefined;
  try {
    const result = await runPythonApi("get_fairness_report", { attribute });
    if (result && Object.keys(result).length > 0) {
      return res.json({ success: true, data: result });
    }
    throw new Error("Empty Python fairness response");
  } catch (_pyErr) {
    try {
      const fallbackReport = getFairnessAudit(attribute);
      return res.json({ success: true, data: fallbackReport });
    } catch (err: any) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }
});

// ----------------------------------------------------------------------------
// VITE MIDDLEWARE SETUP
// ----------------------------------------------------------------------------
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Credit Intelligence Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
