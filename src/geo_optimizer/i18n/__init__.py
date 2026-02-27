"""
Internazionalizzazione (i18n) per GEO Optimizer.

Usa gettext della libreria standard Python. Italiano come lingua
primaria (built-in), inglese come secondaria.

Configurazione lingua:
    - Flag CLI: ``geo audit --lang en``
    - Variabile ambiente: ``GEO_LANG=en``
    - Default: ``it`` (italiano)
"""

import gettext
import os
from pathlib import Path

# Directory contenente i file .mo di traduzione
LOCALES_DIR = Path(__file__).parent / "locales"

# Lingua di default
DEFAULT_LANG = "it"

# Lingue supportate
SUPPORTED_LANGS = {"it", "en"}

# Istanza globale di traduzione
_current_translation = None


def get_lang() -> str:
    """Determina la lingua corrente da GEO_LANG o default."""
    lang = os.environ.get("GEO_LANG", DEFAULT_LANG).lower()
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    return lang


def setup_i18n(lang: str = None) -> gettext.GNUTranslations:
    """Inizializza il sistema i18n per la lingua specificata.

    Args:
        lang: Codice lingua (it, en). Se None, usa get_lang().

    Returns:
        Oggetto GNUTranslations (o NullTranslations se file .mo mancante).
    """
    global _current_translation

    if lang is None:
        lang = get_lang()

    try:
        translation = gettext.translation(
            "geo_optimizer",
            localedir=str(LOCALES_DIR),
            languages=[lang],
        )
    except FileNotFoundError:
        # Fallback: nessuna traduzione (stringhe passthrough)
        translation = gettext.NullTranslations()

    _current_translation = translation
    return translation


def _(message: str) -> str:
    """Traduce un messaggio nella lingua corrente.

    Funzione di traduzione principale. Uso::

        from geo_optimizer.i18n import _
        print(_("Score GEO"))
    """
    global _current_translation

    if _current_translation is None:
        setup_i18n()

    return _current_translation.gettext(message)


def set_lang(lang: str) -> None:
    """Cambia la lingua corrente a runtime."""
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    setup_i18n(lang)
