# Adding a Language

The app translates its interface using a simple catalog: no external dependencies, no build steps. The key for each entry is **the English string itself**, so an untranslated string simply falls back to English without breaking anything.

Language selection is **per-user**, not global: each player chooses their own, and the Game Master chooses theirs. The choice is stored in a cookie, and the `?lang=` query parameter sets it (so a link can carry a language preference).

The code lives in the `handouts/i18n/` package:

```
handouts/i18n/
├── __init__.py       # re-exports the public API (translate, resolve, LANGUAGES...)
├── config.py         # LANGUAGES, DEFAULT_LANG, COOKIE_NAME, COOKIE_MAX_AGE
├── resolver.py       # the logic: clean_lang, translate, resolve
└── catalogs/
    ├── __init__.py   # assembles CATALOG from all languages
    └── it.py         # one file per language: TRANSLATIONS = { 'English': 'Italiano', ... }

```

English is the **source language**: its strings act as keys, which means there is no `en.py` file, and calling `translate()` with `lang='en'` simply returns the text as is.

---

## Steps to add a language (e.g., Spanish, `es`)

### 1. Create the catalog file — `handouts/i18n/catalogs/es.py`

The easiest way is to copy `it.py` and translate the **values** (the keys remain in English, unchanged):

```python
"""Spanish (es) UI translations."""

TRANSLATIONS = {
    # ---- Player: hub + folder ----
    'Player Hub': 'Zona de Jugadores',
    'Welcome, Adventurers!': '¡Bienvenidos, Aventureros!',
    'Browse': 'Explorar',
    # ... all other keys ...
}

```

Rules:

* **Do not translate the keys.** The key is the exact English string appearing in the templates (via the `|t` filter). If you change it, the translation will no longer be found.
* **You don't need to translate everything at once.** Any omitted key will just display in English. You can start with the most visible sections and fill in the rest over time.
* The file is **data only**: no imports, no logic.

### 2. Register the module — `handouts/i18n/catalogs/__init__.py`

Add a line to `_LANGUAGE_MODULES`:

```python
_LANGUAGE_MODULES = {
    'it': 'it',
    'es': 'es',   # <-- here
}

```

### 3. Add the language to the list — `handouts/i18n/config.py`

Add the language code to `LANGUAGES`, with the name shown in the language switcher **written in that language**:

```python
LANGUAGES = {
    'en': 'English',
    'it': 'Italiano',
    'es': 'Español',   # <-- here
}

```

You're done. The language switcher will now display the new option on every page, and `?lang=es` will activate it. No other files need to be touched: `translate()`, the cookie logic, and the template context will pick it up automatically.

---

## How lookup works (for reference)

`translate(text, lang)`:

1. if `lang` is English (`DEFAULT_LANG`), it returns `text` as is;
2. otherwise, it looks up `text` in that language's catalog;
3. if it cannot find it (missing key or unknown language), it returns `text` unchanged — which means English.

This is what makes an incomplete catalog safe: a missing key isn't an error, it's just a string that remains in English.

`clean_lang(raw)` normalizes any input (querystring or cookie) to a supported code, falling back to English for unknown values. `resolve(request)` determines a request's language: the `?lang=` parameter takes priority (and is then saved in the cookie), otherwise, it uses the existing cookie.

---

## Notes on keys

* Keys can contain quotes: use the appropriate Python syntax (e.g., `"Master's Screen"` with double quotes, or `'The Area\\'s'` with escapes).
* The order of the entries is purely **cosmetic** — the lookup is strictly by key — so you can group new strings into thematic sections using comments, just like `it.py` already does (player hub, dashboard, error pages, guide, etc.).
* A duplicate key in the same file isn't an error in Python (the last one wins), but it's best avoided: if two sections share the exact same English string, a single entry is enough.