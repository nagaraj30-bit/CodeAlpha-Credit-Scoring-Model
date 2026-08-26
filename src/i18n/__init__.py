"""
Credit Scoring Model — Internationalization Package
"""

from .helpers import (
    get_current_language,
    get_supported_languages,
    set_current_language,
    t,
)
from .translations import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, TRANSLATIONS

__all__ = [
    "DEFAULT_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "TRANSLATIONS",
    "get_current_language",
    "get_supported_languages",
    "set_current_language",
    "t",
]
