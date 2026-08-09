"""Assemble the per-language catalogues into the CATALOG table.

Each language is its own module here (it.py, and future es.py, fr.py, ...),
exposing a module-level TRANSLATIONS dict of English-source -> translated. This
package gathers them into:

    CATALOG : dict[lang_code, dict[str, str]]  -- what resolver.translate reads.

English is the source language: its strings ARE the keys, so there is no en.py
and 'en' never appears here (translate() short-circuits for the default lang).

To add a language: drop `<code>.py` with a TRANSLATIONS dict, add its code to
LANGUAGES in i18n/config.py, and add one line to _LANGUAGE_MODULES below.
"""

from importlib import import_module

# code -> module name under this package. Keep in sync with config.LANGUAGES
# (minus the default 'en', which has no catalogue).
_LANGUAGE_MODULES = {
    'it': 'it',
}

CATALOG = {
    code: import_module(f'.{mod}', __name__).TRANSLATIONS
    for code, mod in _LANGUAGE_MODULES.items()
}
