"""Language resolution + translation lookup.

The request-facing logic, kept apart from the pure data (catalogs/) and the pure
constants (config.py). resolve() is the only function that touches a Flask
request object; translate() and clean_lang() are plain and testable.

Language is per-user, not global: each player picks their own, the Master picks
their own. The choice rides in a cookie, and `?lang=` sets it (so a link can
carry a language). Resolution happens once per request in resolve().
"""

from .config import LANGUAGES, DEFAULT_LANG, COOKIE_NAME
from .catalogs import CATALOG


def clean_lang(raw):
    """Return a supported language code, falling back to the default."""
    raw = (raw or '').strip().lower()
    return raw if raw in LANGUAGES else DEFAULT_LANG


def translate(text, lang):
    """Look the string up in the catalogue; unknown keys pass through as-is."""
    if lang == DEFAULT_LANG:
        return text
    return CATALOG.get(lang, {}).get(text, text)


def resolve(request):
    """Work out the language for this request.

    `?lang=` wins (it's an explicit click) and is then persisted to a cookie by
    the after_request hook; otherwise the existing cookie decides.
    """
    if 'lang' in request.args:
        return clean_lang(request.args.get('lang')), True
    return clean_lang(request.cookies.get(COOKIE_NAME)), False
