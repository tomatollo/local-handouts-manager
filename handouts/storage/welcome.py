"""Player-hub welcome header (global, master-controlled).

The player hub shows a big title + subtitle. By default these are the
hardcoded, translatable "Welcome, Adventurers!" / "Handouts revealed by..."
strings. The Master can replace either with their own text, or with a LIST
of alternatives: with `random` on, each page load shows a random line from
the list; with it off, the first line is used (so a list doubles as a simple
way to keep spares around without showing them). An empty list falls back to
the app default, which is applied in the template so it stays translatable.
"""

import random

# Caps: a title/subtitle is a header, not an essay, and the list is a handful
# of alternatives, not a database. Bounded so a paste can't bloat the DB.
WELCOME_TITLE_MAX = 200
WELCOME_SUBTITLE_MAX = 300
WELCOME_MAX_LINES = 30


def _clean_welcome_lines(raw, cap):
    """Normalise welcome text into a clean list of lines.

    Accepts either a textarea string (split on newlines) or an already-split
    list. Each line is stripped, capped to `cap` chars, blanks dropped, exact
    duplicates removed keeping first-seen order, and the whole list capped to
    WELCOME_MAX_LINES so a runaway paste can't bloat the DB.
    """
    if isinstance(raw, str):
        raw = raw.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    if not isinstance(raw, (list, tuple)):
        return []
    out, seen = [], set()
    for line in raw:
        s = (str(line) if line is not None else '').strip()[:cap]
        if s and s not in seen:
            seen.add(s)
            out.append(s)
        if len(out) >= WELCOME_MAX_LINES:
            break
    return out


def _normalize_welcome(settings):
    """Bring the welcome node to its canonical shape, in place. Idempotent."""
    w = settings.setdefault('welcome', {})
    w['titles'] = _clean_welcome_lines(w.get('titles', []), WELCOME_TITLE_MAX)
    w['subtitles'] = _clean_welcome_lines(
        w.get('subtitles', []), WELCOME_SUBTITLE_MAX)
    w['random'] = bool(w.get('random', False))
    return w


def get_welcome_config(db):
    """The raw welcome config {titles: [...], subtitles: [...], random: bool}.

    This is what the settings FORM edits (it shows the full lists). The player
    hub uses pick_welcome() instead, which resolves the lists to one line each.
    """
    return _normalize_welcome(db.setdefault('settings', {}))


def set_welcome(db, titles_raw, subtitles_raw, random_flag):
    """Store the Master's welcome title(s) + subtitle(s) and random flag.

    `titles_raw` / `subtitles_raw` may be textarea strings (one line each) or
    lists; both are cleaned by _clean_welcome_lines. Returns the stored node.
    """
    w = db.setdefault('settings', {}).setdefault('welcome', {})
    w['titles'] = _clean_welcome_lines(titles_raw, WELCOME_TITLE_MAX)
    w['subtitles'] = _clean_welcome_lines(subtitles_raw, WELCOME_SUBTITLE_MAX)
    w['random'] = bool(random_flag)
    return w


def pick_welcome(db, rng=random):
    """Resolve the welcome config to one {title, subtitle} for this render.

    Each field independently: with `random` on and more than one line, a random
    line is chosen; otherwise the first line. An empty list yields None for
    that field, and the template falls back to the translatable app default so
    the header is never blank. `rng` is injectable for deterministic tests.
    """
    w = get_welcome_config(db)

    def choose(lines):
        if not lines:
            return None
        if w['random'] and len(lines) > 1:
            return rng.choice(lines)
        return lines[0]

    return {'title': choose(w['titles']), 'subtitle': choose(w['subtitles'])}
