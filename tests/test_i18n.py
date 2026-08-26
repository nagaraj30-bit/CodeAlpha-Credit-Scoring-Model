"""
Credit Scoring Model — Internationalization (i18n) & Language Invariance Test Suite
==================================================================================
Unit and integration tests for Phase 6 Multilingual Architecture:
1. Translation helper functions (get/set active language, supported languages).
2. Dictionary completeness across English (en), Tamil (ta), and Hindi (hi).
3. Key lookup and fallback to English for missing entries.
4. Resilience to invalid language codes without exceptions.
5. Unicode encoding verification for Tamil script and Hindi Devanagari.
6. Absolute Language Invariance: Proving ML prediction, probabilities, FHI scores,
   and What-If scenario deltas are 100% numerically identical regardless of language.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from data_loader import load_credit_data
from financial_health import calculate_financial_health
from i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    TRANSLATIONS,
    get_current_language,
    get_supported_languages,
    set_current_language,
    t,
)
from predict import predict_credit_risk
from risk_reasons import explain_prediction
from scenario_simulator import simulate_scenario


class TestInternationalization(unittest.TestCase):
    """Test suite for multilingual translation and language invariance."""

    @classmethod
    def setUpClass(cls):
        cls.data_path = "data/credit_data.csv"
        cls.df_raw, _ = load_credit_data(cls.data_path)
        cls.sample_delinq = cls.df_raw.iloc[0].to_dict()
        cls.sample_clean = cls.df_raw.iloc[2].to_dict()

    def setUp(self):
        set_current_language("en")

    def tearDown(self):
        set_current_language("en")

    def test_01_supported_languages(self):
        """Verify supported languages dictionary structure."""
        langs = get_supported_languages()
        self.assertIn("en", langs)
        self.assertIn("ta", langs)
        self.assertIn("hi", langs)
        self.assertEqual(len(langs), 3)

    def test_02_set_and_get_language(self):
        """Verify setting and getting current language."""
        self.assertEqual(get_current_language(), "en")
        set_current_language("ta")
        self.assertEqual(get_current_language(), "ta")
        set_current_language("hi")
        self.assertEqual(get_current_language(), "hi")
        # Invalid language falls back to default 'en'
        set_current_language("invalid_lang_code")
        self.assertEqual(get_current_language(), "en")

    def test_03_translations_presence_and_types(self):
        """Verify that core UI keys exist in all three languages."""
        core_keys = [
            "app_title",
            "btn_assess_risk",
            "btn_simulate_scenario",
            "risk_tier_low",
            "risk_tier_medium",
            "risk_tier_high",
            "fhi_header",
            "fhi_score_title",
            "sim_header",
            "disclaimer_legal",
            "disclaimer_privacy",
        ]

        for lang in ["en", "ta", "hi"]:
            self.assertIn(lang, TRANSLATIONS)
            for key in core_keys:
                self.assertIn(key, TRANSLATIONS[lang], f"Missing key '{key}' in language '{lang}'")
                val = TRANSLATIONS[lang][key]
                self.assertIsInstance(val, str)
                self.assertGreater(len(val.strip()), 0)

    def test_04_fallback_behavior(self):
        """Verify fallback to English when key is missing in target language."""
        # Non-existent key returns key itself
        self.assertEqual(t("non_existent_key_12345", lang="en"), "non_existent_key_12345")
        self.assertEqual(t("non_existent_key_12345", lang="ta"), "non_existent_key_12345")

    def test_05_tamil_and_hindi_unicode_safety(self):
        """Verify Tamil script and Hindi Devanagari strings load properly without encoding errors."""
        tamil_title = t("app_title", lang="ta")
        hindi_title = t("app_title", lang="hi")

        self.assertIsInstance(tamil_title, str)
        self.assertIn("கடன்", tamil_title)

        self.assertIsInstance(hindi_title, str)
        self.assertIn("क्रेडिट", hindi_title)

    def test_06_model_prediction_language_invariance(self):
        """Verify that ML model predictions are 100% identical regardless of active UI language."""
        # Run in English
        set_current_language("en")
        pred_en = predict_credit_risk(self.sample_delinq)

        # Run in Tamil
        set_current_language("ta")
        pred_ta = predict_credit_risk(self.sample_delinq)

        # Run in Hindi
        set_current_language("hi")
        pred_hi = predict_credit_risk(self.sample_delinq)

        # Invariance assertions
        self.assertEqual(pred_en["predicted_class"], pred_ta["predicted_class"])
        self.assertEqual(pred_en["predicted_class"], pred_hi["predicted_class"])
        self.assertAlmostEqual(pred_en["default_probability"], pred_ta["default_probability"], places=6)
        self.assertAlmostEqual(pred_en["default_probability"], pred_hi["default_probability"], places=6)
        self.assertEqual(pred_en["risk_level"], pred_ta["risk_level"])
        self.assertEqual(pred_en["risk_level"], pred_hi["risk_level"])

    def test_07_financial_health_language_invariance(self):
        """Verify that Financial Health Indicator is 100% identical regardless of language."""
        set_current_language("en")
        fhi_en = calculate_financial_health(self.sample_delinq)

        set_current_language("ta")
        fhi_ta = calculate_financial_health(self.sample_delinq)

        set_current_language("hi")
        fhi_hi = calculate_financial_health(self.sample_delinq)

        self.assertEqual(fhi_en["score"], fhi_ta["score"])
        self.assertEqual(fhi_en["score"], fhi_hi["score"])
        self.assertEqual(fhi_en["label"], fhi_ta["label"])
        self.assertEqual(fhi_en["label"], fhi_hi["label"])

        for pillar in fhi_en["components"]:
            self.assertEqual(fhi_en["components"][pillar]["score"], fhi_ta["components"][pillar]["score"])
            self.assertEqual(fhi_en["components"][pillar]["score"], fhi_hi["components"][pillar]["score"])

    def test_08_what_if_simulator_language_invariance(self):
        """Verify that What-If Scenario simulation outputs are 100% identical across languages."""
        mods = {"PAY_0": 0, "PAY_2": 0, "PAY_AMT1": 5000.0}

        set_current_language("en")
        sim_en = simulate_scenario(self.sample_delinq, modifications=mods)

        set_current_language("ta")
        sim_ta = simulate_scenario(self.sample_delinq, modifications=mods)

        set_current_language("hi")
        sim_hi = simulate_scenario(self.sample_delinq, modifications=mods)

        # Delta invariance
        self.assertEqual(
            sim_en["comparison"]["default_probability_delta"],
            sim_ta["comparison"]["default_probability_delta"]
        )
        self.assertEqual(
            sim_en["comparison"]["default_probability_delta"],
            sim_hi["comparison"]["default_probability_delta"]
        )
        self.assertEqual(
            sim_en["comparison"]["financial_health_delta"],
            sim_ta["comparison"]["financial_health_delta"]
        )
        self.assertEqual(
            sim_en["comparison"]["financial_health_delta"],
            sim_hi["comparison"]["financial_health_delta"]
        )

    def test_09_fairness_keys_completeness(self):
        """Verify all fairness keys are present across en, ta, and hi."""
        fairness_keys = [
            "nav_fairness",
            "fairness_title",
            "fairness_subtitle",
            "fairness_tab_overview",
            "fairness_tab_metrics",
            "fairness_tab_limitations",
            "fairness_dataset_total",
            "fairness_available_demographics",
            "fairness_unavailable_demographics",
            "fairness_removed_variables",
            "fairness_retained_variables",
            "fairness_select_attribute",
            "fairness_reference_group",
            "fairness_metric_base_rate",
            "fairness_metric_ppr",
            "fairness_metric_recall",
            "fairness_metric_fpr",
            "fairness_metric_fnr",
            "fairness_metric_precision",
            "fairness_metric_accuracy",
            "fairness_small_sample_warning",
            "fairness_disparity_diff",
            "fairness_disparity_ratio",
            "fairness_principle_1",
            "fairness_principle_2",
            "fairness_principle_3",
        ]
        for lang in ["en", "ta", "hi"]:
            set_current_language(lang)
            for k in fairness_keys:
                translated = t(k)
                self.assertIsInstance(translated, str, f"Missing or non-string translation for key '{k}' in language '{lang}'")
                self.assertNotEqual(translated, k, f"Key '{k}' fell back to untranslated key name in language '{lang}'")


if __name__ == "__main__":
    unittest.main()
