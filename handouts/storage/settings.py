"""Global, master-controlled table settings. Only the theme is stored here;
language is a per-user cookie and deliberately never persisted. The welcome
header and POP also live under `settings` in the DB, but their logic has its
own modules (welcome.py, pop.py).
"""

from .. import theming


def get_theme(db):
    return theming.clean_theme(db.get('settings', {}).get('theme'))


def set_theme(db, raw):
    """Set the table-wide theme. Unknown ids collapse to the default."""
    db.setdefault('settings', {})['theme'] = theming.clean_theme(raw)
    return db['settings']['theme']
