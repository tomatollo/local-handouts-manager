"""Language configuration: the supported set and the cookie parameters.

Pure constants, no logic and no Flask. Split out from the resolver so a caller
that only needs LANGUAGES (e.g. the template context) doesn't pull in the
request-handling code, and so adding a language is an edit in one obvious place.
"""

# Supported languages: code -> the name shown in the switcher (in that language).
# Add a language by adding its code here AND a catalogue module under
# i18n/catalogs/ (see i18n/catalogs/__init__.py).
LANGUAGES = {
    'en': 'English',
    'it': 'Italiano',
}

# English is the source language: its strings are the catalogue KEYS, so there
# is no 'en' catalogue and translate() short-circuits for it.
DEFAULT_LANG = 'en'

# The cookie that remembers a user's choice.
COOKIE_NAME = 'lang'
# Roughly a year; the choice is a preference, not a session detail.
COOKIE_MAX_AGE = 60 * 60 * 24 * 365
