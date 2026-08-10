"""Database load / save / normalize -- the heart of the storage package.

Everything that reads or writes data/database.json lives here: the write lock,
the opt-in per-request cache, atomic saves, and _normalize (which brings legacy
records up to the current shape). _normalize reaches into the domain modules for
their per-node cleaners (welcome, map POIs, view-type, format) so the migration
logic for each concern stays next to that concern; this is the one module that
imports several siblings, and it is imported by none of them, so the package
dependency graph stays acyclic.

This module keeps NO Flask import: the request cache is injected from the web
layer via set_request_cache_hooks, so storage stays usable from the CLI (where
the hooks are simply never installed and every load_db reads from disk).
"""

import json
import os
import threading

from .. import theming
from .paths import DB_PATH, POP_KEY, MAP_KEY, MAPS_KEY
from .util import clean_view_type
from .formats import format_of_handout
from .welcome import _normalize_welcome
from .map_state import _normalize_map

# --------------------------------------------------------------------------
# Concurrency + request-scoped caching
#
# waitress serves the app with a thread pool, so two requests can be inside a
# load -> mutate -> save cycle at the same time. A bare open('w') + json.dump
# can then interleave (or a reader can catch a half-written file), corrupting
# database.json. `_DB_LOCK` serialises every write, and save_db writes to a
# temp file then os.replace()s it into place, so a reader ALWAYS sees either
# the old file or the new one whole, never a truncated middle.
#
# Separately, a single request calls load_db() many times (the language, CSRF
# and rate-limit hooks, the UI context processor, and the view itself each
# ask for it), and every call used to re-read and re-parse the whole file and
# re-run _normalize. A per-request cache collapses those into one read. The
# cache is OPT-IN and injected by the web layer: `set_request_cache_hooks`
# hands storage two callables backed by flask.g, so this module keeps no Flask
# import and stays usable from the CLI (where the hooks are simply never set,
# and every load_db hits disk as before).
# --------------------------------------------------------------------------

_DB_LOCK = threading.RLock()

# Filled in by set_request_cache_hooks(). `_cache_get()` returns the cached DB
# for the current request or None; `_cache_set(db)` stores it. Left as no-ops
# so a caller that never installs them (the CLI, tests) behaves exactly as it
# did before this cache existed.
_cache_get = lambda: None          # noqa: E731 - deliberately tiny
_cache_set = lambda _db: None      # noqa: E731


def set_request_cache_hooks(getter, setter):
    """Install per-request DB cache callables (see the module comment above).

    `getter()` returns the DB cached for the current request, or None if none
    is cached yet (or there is no request context). `setter(db)` records one.
    The web layer wires these to flask.g; other entry points leave them unset.
    """
    global _cache_get, _cache_set
    _cache_get = getter
    _cache_set = setter


def load_db():
    """Load the DB, creating an empty one if missing (robust for clones).

    Within a single web request the parsed DB is cached (see the module
    comment), so the many hooks and the view that each call load_db share one
    read + normalize instead of re-parsing the file every time. The FIRST call
    of a request populates the cache; later calls return that same object, so a
    mutation made after an earlier load in the same request is visible to a
    later load -- which is what the routes already assume when they load, edit,
    then load again indirectly through a helper.

    Outside a request context (CLI, tests) the hooks are unset and every call
    reads from disk exactly as before.
    """
    cached = _cache_get()
    if cached is not None:
        return cached

    # Reading under the same lock that guards writes means a concurrent save
    # (temp-file + os.replace) is atomic with respect to us: we open either the
    # old file or the new one, never a partial write.
    with _DB_LOCK:
        if not os.path.exists(DB_PATH):
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            _atomic_write({'handouts': [], 'folders': []})
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    _normalize(data)
    _cache_set(data)
    return data


def _normalize(data):
    """Bring legacy records up to the current shape, in memory.

    Kept idempotent and defensive: every access uses .get()/defaults so a
    half-migrated or clone-fresh DB never raises. Safe to run repeatedly.
    """
    # DB-level: master-defined folders live at the root as {id, name}.
    data.setdefault('folders', [])

    # DB-level: table-wide settings. Only the theme is global; language is a
    # per-user cookie and deliberately never stored here. The settings dict
    # also holds the master passphrase hash + session secret (see auth.py),
    # which are left untouched here: they are opaque to display code.
    settings = data.setdefault('settings', {})
    settings['theme'] = theming.clean_theme(settings.get('theme'))

    # DB-level: the player-hub welcome header. The Master can override the
    # hardcoded "Welcome, Adventurers!" title and its subtitle with their own
    # text, or with a LIST of lines one of which is picked (at random when
    # `random` is on, else the first). Empty lists mean "use the app default",
    # resolved in the template so the default stays translatable. See
    # get_welcome_config / set_welcome / pick_welcome.
    _normalize_welcome(settings)

    # DB-level: the current POP broadcast. `seq` is a monotonic counter that
    # only ever grows; clients compare it against the last one they showed to
    # tell a fresh POP from one they have already handled. Persisting it (as
    # opposed to keeping it in memory) means a player who loads the hub late,
    # or whose phone was asleep, still receives the POP the Master fired, and
    # that a server restart does not replay an old one.
    pop = settings.setdefault(POP_KEY, {})
    pop.setdefault('seq', 0)
    pop.setdefault('handout_id', None)
    pop.setdefault('at', None)

    # DB-level: interactive maps. The table can have several (a world map, a
    # city, a dungeon level), stored as a LIST under MAPS_KEY. Each is an
    # independent scene the Master reveals and players poll.
    #
    # Migration: databases written before multi-map support stored ONE map
    # under the legacy MAP_KEY. Convert it into maps[0] once, then drop the old
    # key so nothing keeps reading it. This is a clean, one-way migration --
    # after it runs the DB has only MAPS_KEY. (Backups are the safety net: the
    # library can always be re-imported from an export made on an older build.)
    legacy = data.pop(MAP_KEY, None)
    maps = data.get(MAPS_KEY)
    if not isinstance(maps, list):
        maps = []
    if legacy and not maps:
        # Give the migrated map a friendly default name and a STABLE id. The
        # legacy single map carried no id, and _normalize_map would otherwise
        # mint a fresh random one on every load_db -- and because the migration
        # isn't persisted until the next save_db, each request would see a
        # different id, breaking every /map/<id> link (an endless redirect
        # between the map list and a map that no longer matches its id). A
        # fixed id keeps the migrated map addressable across requests until it
        # is first saved.
        legacy.setdefault('id', 'legacy-map')
        legacy.setdefault('name', 'Map 1')
        maps = [legacy]
    data[MAPS_KEY] = maps
    # Normalize every map in place: ensures id + name, fills any missing scene
    # fields, re-cleans POIs, and seeds each map's pending/confirm_seq. Drops
    # entries that aren't dicts (hand-edited junk) rather than crashing on them.
    data[MAPS_KEY] = [_normalize_map(m) for m in maps if isinstance(m, dict)]

    for h in data.get('handouts', []):
        # Legacy single-file -> files: [...]
        if 'files' not in h:
            h['files'] = [{
                'filename': h.get('filename', ''),
                'reader': h.get('reader', 'image'),
            }]

        # Per-file description. The old handout-wide `alt_text` becomes the
        # description of the FIRST file (it was effectively the cover text).
        legacy_alt = h.get('alt_text', '').strip() if h.get('alt_text') else ''
        for i, f in enumerate(h['files']):
            if 'description' not in f:
                f['description'] = legacy_alt if i == 0 else ''
            # PDFs may carry a rendered first-page thumbnail; images never do.
            # Absent means "not generated yet", which callers handle.
            f.setdefault('thumb', None)
        # alt_text is superseded by per-file descriptions; drop it once
        # migrated so it can't drift out of sync.
        h.pop('alt_text', None)

        # Multi-value tags (searchable/groupable), separate from `category`
        # and from folders.
        h.setdefault('tags', [])
        # Folder membership: a list of folder ids (multi-membership).
        h.setdefault('folders', [])
        # How players view this handout's files (carousel/book).
        h['view_type'] = clean_view_type(h.get('view_type'))
        # Book viewer only: whether the first page (cover) and the back cover
        # are drawn as RIGID "hard" pages -- the stiff card of a real binding --
        # or flip like any inner leaf. Default True keeps every existing book
        # exactly as it was; a Master can clear it to make the covers turn soft.
        h.setdefault('hard_covers', True)
        h['hard_covers'] = bool(h.get('hard_covers'))
        # Original upload format ('pdf', 'png', ...), used only by the master's
        # "Group by Format" view. Legacy records saved before this field gain a
        # best-guess value from their cover file's extension, so they still
        # group sensibly without a migration pass. (A converted PDF can't be
        # recovered this way -- its cover is a PNG now -- but new PDF uploads
        # record 'pdf' explicitly at upload time.)
        if not h.get('source_format'):
            h['source_format'] = format_of_handout(h)
        # Optional secret reveal: one or more passwords the Master can set on a
        # handout so that a player who types any of them into the viewer's info
        # panel opens ANOTHER handout (a hidden twist, a decoded message, ...).
        # These are plain strings by design -- this is table theatre, not
        # security, and the Master needs to see the words back when editing.
        #
        # secret_passwords is the source of truth: a list of accepted words
        # (any one unlocks the target). secret_ignore_case, when true, matches
        # them without regard to letter case, so "Xanathar" also accepts
        # "xanathar" / "XANATHAR". Legacy records carried a single
        # secret_password string; migrate it into the list once, and keep
        # secret_password mirrored to the first entry so any old reader (and the
        # export/import round-trip) still sees a sensible value. An empty list
        # means "no secret to reveal here".
        legacy_pw = (h.get('secret_password') or '').strip()
        if 'secret_passwords' not in h:
            h['secret_passwords'] = [legacy_pw] if legacy_pw else []
        else:
            # Clean whatever is stored: strip, drop blanks, de-duplicate while
            # keeping order (case-sensitively here; the match step applies the
            # ignore-case flag, so we don't silently merge distinct entries).
            seen = set()
            cleaned = []
            for p in h['secret_passwords']:
                p = (p or '').strip()
                if p and p not in seen:
                    seen.add(p)
                    cleaned.append(p)
            h['secret_passwords'] = cleaned
        h.setdefault('secret_ignore_case', False)
        h['secret_ignore_case'] = bool(h.get('secret_ignore_case'))
        # Mirror the first password back into the legacy scalar so nothing that
        # still reads secret_password breaks.
        h['secret_password'] = h['secret_passwords'][0] if h['secret_passwords'] else ''
        h.setdefault('secret_handout_id', None)

        # Optional back cover (a single file entry or None). Shown as the very
        # last page in the Book viewer. Ignored by the carousel.
        h.setdefault('back_cover', None)
        if h.get('back_cover'):
            h['back_cover'].setdefault('description', '')
            h['back_cover'].setdefault('thumb', None)


def _atomic_write(data):
    """Serialise `data` to DB_PATH atomically: temp file, fsync, os.replace.

    os.replace is atomic on both POSIX and Windows when source and destination
    are on the same filesystem (here they share the data/ directory), so a
    reader never observes a half-written file -- it sees the previous complete
    file until the instant the new one takes its place. Caller must hold
    _DB_LOCK. Kept separate from save_db so load_db can reuse it to seed a
    missing database without recursing through the public entry point.
    """
    directory = os.path.dirname(DB_PATH)
    os.makedirs(directory, exist_ok=True)
    tmp = DB_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, DB_PATH)


def save_db(data):
    """Persist `data`, atomically and under the write lock.

    The lock serialises the whole read-modify-write cycle across threads: two
    master POSTs that each load, mutate and save can no longer interleave into
    a corrupt or clobbered file. The write itself is atomic (see _atomic_write),
    so even a reader that is NOT holding the lock only ever sees a complete DB.

    The request cache (if installed) is refreshed to the just-saved object, so
    a later load_db in the same request returns exactly what was written rather
    than a stale earlier copy.
    """
    with _DB_LOCK:
        _atomic_write(data)
    _cache_set(data)
