"""UI translations.

This package replaces the former single i18n.py. Its public surface is
unchanged, so the app keeps calling `i18n.translate(...)`, `i18n.resolve(...)`,
`i18n.LANGUAGES`, `i18n.COOKIE_NAME`, etc. exactly as before -- only the
internals are split up:

    config.py       LANGUAGES, DEFAULT_LANG, COOKIE_NAME, COOKIE_MAX_AGE
    catalogs/       one module per language (it.py, ...), each a flat
                    TRANSLATIONS dict, gathered into CATALOG by catalogs/__init__
    resolver.py     the logic: clean_lang, translate, resolve

No external dependency and no build step: a key is the English source string
itself, so an untranslated string still renders sensibly in English.

Language is per-user, not global: each player picks their own, the Master picks
their own. The choice rides in a cookie, and `?lang=` sets it. Resolution
happens once per request in resolve().

To add a language, see the note in catalogs/__init__.py: drop a `<code>.py`
catalogue, list it there, and add its code to LANGUAGES in config.py. Nothing
here needs editing.
"""

from .config import LANGUAGES, DEFAULT_LANG, COOKIE_NAME, COOKIE_MAX_AGE
from .catalogs import CATALOG
from .resolver import clean_lang, translate, resolve

__all__ = [
    'LANGUAGES', 'DEFAULT_LANG', 'COOKIE_NAME', 'COOKIE_MAX_AGE',
    'CATALOG', 'clean_lang', 'translate', 'resolve',
]
