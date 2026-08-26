"""
Credit Scoring Model — Translation Helpers
==========================================
Helper functions for deterministic multilingual string lookups, key fallbacks,
formatting, and language switching.
"""

from typing import Any, Dict, List, Optional

from .translations import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, TRANSLATIONS

_CURRENT_LANGUAGE = DEFAULT_LANGUAGE


def get_current_language() -> str:
    """Return currently active language code ('en', 'ta', 'hi')."""
    global _CURRENT_LANGUAGE
    return _CURRENT_LANGUAGE


def set_current_language(lang_code: str) -> str:
    """
    Set currently active language code. Falls back to 'en' if invalid.

    Args:
        lang_code: 'en', 'ta', or 'hi'

    Returns:
        str: Activated valid language code.
    """
    global _CURRENT_LANGUAGE
    if lang_code in SUPPORTED_LANGUAGES:
        _CURRENT_LANGUAGE = lang_code
    else:
        _CURRENT_LANGUAGE = DEFAULT_LANGUAGE
    return _CURRENT_LANGUAGE


def get_supported_languages() -> Dict[str, Dict[str, str]]:
    """Return dictionary of supported languages with native names."""
    return SUPPORTED_LANGUAGES


def t(key: str, lang: Optional[str] = None, **kwargs: Any) -> str:
    """
    Look up translated string for given key in requested or current language.

    Fallback behavior:
    1. Check TRANSLATIONS[lang][key]
    2. Fallback to TRANSLATIONS['en'][key]
    3. Fallback to key itself if not found anywhere

    Args:
        key: String key name in translations dictionary.
        lang: Optional explicit language code ('en', 'ta', 'hi').
        **kwargs: Dynamic interpolation variables if string contains {param}.

    Returns:
        str: Translated string or key fallback.
    """
    target_lang = lang if (lang and lang in SUPPORTED_LANGUAGES) else _CURRENT_LANGUAGE

    lang_dict = TRANSLATIONS.get(target_lang, {})
    val = lang_dict.get(key)

    # Fallback to English if missing in target language
    if val is None:
        val = TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key, key)

    if kwargs and isinstance(val, str):
        try:
            return val.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return val

    return str(val)
