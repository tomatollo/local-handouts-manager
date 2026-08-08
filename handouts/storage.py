"""Data + file storage for handouts.

Everything that touches the JSON database or the uploads folder lives here,
so the route modules stay thin and free of persistence details.
"""

import json
import os
import re
import threading
import uuid
from datetime import datetime, timezone

from werkzeug.utils import secure_filename

from . import theming

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.json')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
# The interactive map's background image lives in its own folder, kept apart
# from the handout library so a large campaign map never mixes in with the
# handouts and can be managed (and cleared) independently.
MAP_DIR = os.path.join(BASE_DIR, 'static', 'maps')

# Extension whitelist (images + PDF). Kept lowercase, no leading dot.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

# Map backgrounds are images only -- no PDF (the map viewer draws an <img>).
MAP_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# How a handout's files are presented to players. This is a handout-level
# property (distinct from each file's `reader`, which is image/pdf).
VIEW_TYPES = ('carousel', 'book')
DEFAULT_VIEW_TYPE = 'carousel'

# Key under `settings` holding the current POP broadcast (see pop_state).
POP_KEY = 'pop'

# Top-level DB key holding the interactive map's shared state (see
# get_map_state / update_map_state). Kept at the root, alongside `handouts`
# and `folders`, because the map is table-wide state rather than a per-handout
# or display setting.
MAP_KEY = 'map_state'

# How long a POP stays live, in seconds.
#
# A POP is a moment at the table ("look at this, now"), not a piece of state.
# Without an expiry the stored pointer stays true forever, so every player who
# joined, reloaded or woke their phone hours later got the modal again -- the
# handout is still popped, as far as the DB is concerned. Two minutes is long
# enough to cover a latecomer or a phone that was asleep during the reveal, and
# short enough that the POP is over before the scene is.
POP_TTL_SECONDS = 120


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


def clean_view_type(raw):
    """Return a valid view_type, falling back to the default for junk input.

    Note: 'gallery' was removed; any legacy value that isn't recognised (incl.
    old 'gallery' records) collapses to the default carousel.
    """
    raw = (raw or '').strip().lower()
    return raw if raw in VIEW_TYPES else DEFAULT_VIEW_TYPE


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def reader_for(ext):
    return 'pdf' if ext.lower() == 'pdf' else 'image'


# --------------------------------------------------------------------------
# File format (for the master's "Group by Format" view)
#
# `source_format` records the ORIGINAL kind of a handout -- 'pdf', 'png',
# 'jpg', ... -- chosen from the first file the Master uploaded, BEFORE any
# conversion. It matters because a PDF is now rendered to PNG pages at upload:
# grouping by what sits on disk would file every PDF under "PNG", so we keep
# the original format as its own field instead. It is a label for sorting only;
# nothing about how the handout is viewed depends on it.
# --------------------------------------------------------------------------

# jpg/jpeg are the same format to a human sorting a shelf, so they fold together
# under the shorter, more familiar 'jpg'.
_FORMAT_ALIASES = {'jpeg': 'jpg'}
# Shown for a handout whose format can't be determined (no files, hand-edited
# record). Kept distinct from a real extension so it sorts into its own group.
FORMAT_UNKNOWN = ''
# Substring that pdfs.explode_to_pages bakes into every page it renders from a
# PDF ('<id>_pdf<stamp>_<n>.png'). It is the one durable trace that a now-PNG
# page began life as a PDF, so a handout converted BEFORE source_format was
# recorded can still be grouped under 'pdf' instead of 'png'. Must stay in sync
# with pdfs.PDF_PAGE_MARKER (kept as a literal here to avoid importing pdfs,
# which imports this module).
_PDF_PAGE_MARKER = '_pdf'


def ext_of(filename):
    """Lowercase extension of a filename without the dot, or '' if none."""
    name = filename or ''
    return name.rsplit('.', 1)[1].lower() if '.' in name else ''


def normalize_format(ext):
    """Fold an extension into its canonical format label (jpeg -> jpg, ...)."""
    ext = (ext or '').strip().lower().lstrip('.')
    return _FORMAT_ALIASES.get(ext, ext)


def _looks_like_converted_pdf(h):
    """True if this handout's pages look like they were rendered from a PDF.

    A PDF is exploded into PNG pages whose names carry the '_pdf' marker (see
    _PDF_PAGE_MARKER). A handout saved before source_format existed therefore
    still betrays its PDF origin through those filenames. We require the COVER
    (files[0]) to carry the marker: that is the page the format label is meant
    to describe, and it avoids mislabelling an image handout that happens to
    include one converted page.
    """
    files = h.get('files') or []
    if not files:
        return False
    cover_name = files[0].get('filename', '') or ''
    return _PDF_PAGE_MARKER in cover_name


def format_of_handout(h):
    """The handout's original format label for grouping.

    Resolution order:
      1. An explicit `source_format` recorded at upload -- always authoritative.
      2. The '_pdf' filename marker on the cover: recovers handouts that were
         converted from PDF to PNG BEFORE source_format was recorded, so those
         still group under 'pdf' rather than 'png'.
      3. The cover file's extension -- correct for plain image handouts.
    Returns FORMAT_UNKNOWN when nothing can be determined.
    """
    fmt = normalize_format(h.get('source_format'))
    if fmt:
        return fmt
    if _looks_like_converted_pdf(h):
        return 'pdf'
    files = h.get('files') or []
    if files:
        return normalize_format(ext_of(files[0].get('filename', '')))
    return FORMAT_UNKNOWN


def source_format_from_uploads(file_storages):
    """Pick the original format label from a list of just-uploaded files.

    Uses the FIRST file (the cover), mirroring how the rest of the app treats
    files[0] as the handout's face. Called at upload time, before any PDF is
    rendered to images, so a PDF handout is recorded as 'pdf' even though its
    stored pages end up as PNG.
    """
    for f in file_storages:
        if f and getattr(f, 'filename', ''):
            return normalize_format(ext_of(f.filename))
    return FORMAT_UNKNOWN


def all_formats(db):
    """Every distinct source format across handouts, sorted alphabetically."""
    formats = set()
    for h in db.get('handouts', []):
        fmt = format_of_handout(h)
        if fmt:
            formats.add(fmt)
    return sorted(formats)


# --------------------------------------------------------------------------
# Database load / save / normalize
# --------------------------------------------------------------------------

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

    # DB-level: interactive map state, shared by the Master (who reveals hexes
    # and moves the marker) and every player screen (which polls it). Created
    # on the fly with per-key setdefault so a DB written before this feature
    # existed gains it without touching the rest of the record, and so a
    # partially hand-edited node keeps whatever keys it already has.
    map_state = data.setdefault(MAP_KEY, {})
    map_state.setdefault('revealed_hexes', [])
    map_state.setdefault('marker_x', 0)
    map_state.setdefault('marker_y', 0)
    map_state.setdefault('marker_visible', False)
    # How big the party marker is drawn, as a multiplier on its base size.
    map_state.setdefault('marker_scale', 1.0)
    # The party marker is customisable like a POI: an optional custom glyph
    # and a colour. Empty icon = the default diamond marker.
    map_state.setdefault('marker_icon', '')
    map_state.setdefault('marker_color', '#c0533b')
    # Grid the Master can size to match a printed map (e.g. Chult is 23x24).
    map_state.setdefault('grid_cols', 20)
    map_state.setdefault('grid_rows', 15)
    # Colour of un-revealed (fogged) hexes, as a CSS hex string.
    map_state.setdefault('fog_color', '#0d0b0a')
    # Uploaded map image filename (in static/maps), or None for placeholder.
    map_state.setdefault('map_image', None)
    # Grid calibration, all as PERCENT of the map image so they survive a
    # resolution change. offset_x/offset_y move the whole grid so its first hex
    # lands on the map's first printed hex; hex_size is one hex's width as a
    # percent of the image width (height follows from hex geometry). These let
    # the Master align the overlay to a map that already has hexes drawn on it,
    # instead of stretching the grid to the image edges.
    map_state.setdefault('offset_x', 0.0)
    map_state.setdefault('offset_y', 0.0)
    map_state.setdefault('hex_size', 5.0)
    # Points of interest: labels the Master pins to the map (city names, etc.).
    # Each is {id, label, x, y, always_visible} with x/y as PERCENT of the
    # image so they survive a resolution change, exactly like the calibration
    # fields. They live ON TOP of everything (fog, grid, marker) and carry only
    # text -- never map pixels -- so an always_visible POI is safe to show even
    # over an un-revealed hex. always_visible False means the POI only appears
    # once the hex it sits in has been revealed (resolved client-side).
    map_state.setdefault('pois', [])
    # Older POIs (saved before icon/colour/scale existed) are re-run through the
    # cleaner so every stored pin carries the full field set with sane defaults,
    # rather than leaking null icon/colour/scale to the player JSON.
    map_state['pois'] = _clean_pois(map_state['pois'], map_state['pois'])
    # Camera focus broadcast: "everyone look here, now". Like the POP, this is
    # NOT staged -- it is a live directive, not a draft edit. {seq, x, y, scale}
    # where x/y are the focus point as PERCENT of the image and scale is the
    # zoom level the Master was using. Players compare seq to tell a fresh
    # focus from an unchanged poll and animate their view to match. seq 0 means
    # "never focused"; players ignore it.
    map_state.setdefault('focus', {})
    focus = map_state['focus']
    focus.setdefault('seq', 0)
    focus.setdefault('x', 50.0)
    focus.setdefault('y', 50.0)
    focus.setdefault('scale', 1.0)

    # --- Staging (draft) layer ---------------------------------------------
    # Everything above is the CONFIRMED state -- the only thing players read.
    # The Master edits a draft first and explicitly confirms it, so a mistaken
    # click never flashes onto the table. `pending` mirrors the same keys; a
    # confirm copies pending -> confirmed, a discard copies confirmed -> pending.
    # Seeded from confirmed values so a fresh DB starts with draft == live.
    pending = map_state.setdefault('pending', {})
    pending.setdefault('revealed_hexes', list(map_state['revealed_hexes']))
    pending.setdefault('marker_x', map_state['marker_x'])
    pending.setdefault('marker_y', map_state['marker_y'])
    pending.setdefault('marker_visible', map_state['marker_visible'])
    pending.setdefault('marker_scale', map_state['marker_scale'])
    pending.setdefault('marker_icon', map_state['marker_icon'])
    pending.setdefault('marker_color', map_state['marker_color'])
    pending.setdefault('grid_cols', map_state['grid_cols'])
    pending.setdefault('grid_rows', map_state['grid_rows'])
    pending.setdefault('fog_color', map_state['fog_color'])
    pending.setdefault('map_image', map_state['map_image'])
    pending.setdefault('offset_x', map_state['offset_x'])
    pending.setdefault('offset_y', map_state['offset_y'])
    pending.setdefault('hex_size', map_state['hex_size'])
    # POIs are staged like everything else: the draft carries its own list and
    # a confirm promotes it. Deep-copied from the confirmed list so the two
    # layers never alias (each POI is its own dict).
    pending.setdefault('pois', [dict(poi) for poi in map_state['pois']])
    pending['pois'] = _clean_pois(pending['pois'], pending['pois'])
    # Bumped on every confirm; players compare it to tell a fresh confirmation
    # from an unchanged poll (and so the marker only animates on real changes).
    map_state.setdefault('confirm_seq', 0)

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


# --------------------------------------------------------------------------
# Record helpers
# --------------------------------------------------------------------------

def find(db, handout_id):
    return next((h for h in db['handouts'] if h['id'] == handout_id), None)


def player_payload(handout):
    """The player-facing view of a handout: exactly what the lightbox opens.

    One shared shape for every path that hands a handout to the client (the POP
    poll and the secret-reveal endpoint), so the browser never needs a second
    way to build a viewer. Deliberately omits master-only fields -- notably the
    secret password itself, which must never travel to a player.
    """
    return {
        'id': handout['id'],
        'title': handout.get('title', ''),
        'description': handout.get('description', ''),
        'found_location': handout.get('found_location', ''),
        'found_date': handout.get('found_date', ''),
        'view_type': handout.get('view_type', DEFAULT_VIEW_TYPE),
        'hard_covers': handout.get('hard_covers', True),
        'files': handout.get('files', []),
        'back_cover': handout.get('back_cover'),
        # True when THIS handout itself carries a further secret reveal, so the
        # viewer knows to keep showing the password box after a reveal chains
        # into another handout. The password values are never included.
        'has_secret': bool(handout.get('secret_passwords')
                           and handout.get('secret_handout_id')),
    }


def reveal_secret(db, handout_id, password):
    """Resolve a password typed on `handout_id` to the hidden handout it unlocks.

    Returns the target handout's player_payload when `password` matches ANY of
    the source handout's accepted passwords AND the linked target still exists;
    otherwise None. Each side is whitespace-trimmed to match how the Master
    typed the words into the form. When the source has secret_ignore_case set,
    the comparison is case-insensitive, so "Xanathar" accepts "xanathar" too.

    No timing-safe compare and no hashing: this is a table gimmick guarding a
    story beat, not a credential (see the module + auth notes). The target is
    returned even if it is not `visible` -- typing the password IS the reveal,
    so requiring a separate publish would defeat the feature.
    """
    source = find(db, handout_id)
    if source is None:
        return None
    accepted = [p for p in (source.get('secret_passwords') or []) if p.strip()]
    target_id = source.get('secret_handout_id')
    if not accepted or not target_id:
        return None
    typed = (password or '').strip()
    if not typed:
        return None
    if source.get('secret_ignore_case'):
        typed_cmp = typed.casefold()
        matched = any(typed_cmp == p.strip().casefold() for p in accepted)
    else:
        matched = any(typed == p.strip() for p in accepted)
    if not matched:
        return None
    target = find(db, target_id)
    if target is None:
        return None
    return player_payload(target)


# --------------------------------------------------------------------------
# Settings (global, master-controlled)
# --------------------------------------------------------------------------

def get_theme(db):
    return theming.clean_theme(db.get('settings', {}).get('theme'))


def set_theme(db, raw):
    """Set the table-wide theme. Unknown ids collapse to the default."""
    db.setdefault('settings', {})['theme'] = theming.clean_theme(raw)
    return db['settings']['theme']


# --------------------------------------------------------------------------
# POP broadcasts (global, master-controlled)
#
# A POP is "the Master wants this handout on every screen, now". It is stored
# rather than pushed: there is no socket to push down, and storing it makes the
# feature independent of who happened to be connected at the moment it fired.
#
# Only the newest POP is kept. The Master popping a second handout supersedes
# the first -- there is no queue, because a queue would mean players silently
# working through a backlog of dramatic reveals in the wrong order.
# --------------------------------------------------------------------------

def pop_state(db):
    """The current POP as {seq, handout_id, at}. Never None (see _normalize)."""
    return db.get('settings', {}).get(POP_KEY, {
        'seq': 0, 'handout_id': None, 'at': None})


def pop_age_seconds(pop, now=None):
    """Seconds since `pop` was fired, or None if that can't be determined.

    Returns None -- not 0 -- when `at` is missing or unparseable, so callers
    must decide explicitly what an unknown age means rather than inheriting a
    "fresh" answer by accident (see pop_is_live, which treats it as expired).

    `now` is injectable so the TTL can be tested without sleeping.
    """
    at = (pop or {}).get('at')
    if not at:
        return None
    try:
        fired = datetime.fromisoformat(at)
    except (TypeError, ValueError):
        # A hand-edited or truncated timestamp. Unknown age, not zero.
        return None
    # Records written before the TTL existed may be naive; assume UTC, which is
    # what now_iso() has always produced.
    if fired.tzinfo is None:
        fired = fired.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    return (now - fired).total_seconds()


def pop_is_live(pop, now=None):
    """True if `pop` still points at something and hasn't aged out.

    Fails closed on every uncertainty: no handout, no timestamp, an unreadable
    timestamp, or a clock that has jumped backwards all count as "not live".
    The cost of a false negative is a POP the Master re-fires; the cost of a
    false positive is a stale modal ambushing a player mid-session, which is
    the bug this exists to kill.
    """
    pop = pop or {}
    if not pop.get('handout_id'):
        return False
    age = pop_age_seconds(pop, now)
    if age is None:
        return False
    # A negative age means the POP is stamped in the future -- a clock change,
    # or a DB copied from another machine. Don't trust it.
    if age < 0:
        return False
    return age < POP_TTL_SECONDS


def set_pop(db, handout_id):
    """Record a POP for `handout_id` and return the new state.

    Bumping `seq` is what actually notifies players: they poll for it and act
    on any value above the last one they showed. The counter is bumped even
    when the same handout is popped twice in a row, so a Master re-popping to
    catch a distracted table still reaches screens that already dismissed it.
    """
    settings = db.setdefault('settings', {})
    current = settings.setdefault(POP_KEY, {'seq': 0})
    settings[POP_KEY] = {
        'seq': current.get('seq', 0) + 1,
        'handout_id': handout_id,
        'at': now_iso(),
    }
    return settings[POP_KEY]


def clear_pop(db):
    """Retire the current POP without rewinding `seq`.

    Called when the popped handout is deleted or unpublished. `seq` keeps
    climbing so clients that already showed this POP never see it again, while
    clients still polling simply find nothing to open.
    """
    settings = db.setdefault('settings', {})
    current = settings.setdefault(POP_KEY, {'seq': 0})
    settings[POP_KEY] = {
        'seq': current.get('seq', 0) + 1,
        'handout_id': None,
        'at': None,
    }
    return settings[POP_KEY]


# --------------------------------------------------------------------------
# Interactive map (global, master-controlled)
#
# One shared map per table: the Master reveals hexes and moves a marker, and
# every player screen polls this state. Stored at the DB root (see MAP_KEY),
# not under `settings`, because it is live scene state rather than a display
# preference.
# --------------------------------------------------------------------------

def get_map_state(db):
    """Return the current map state dict.

    Never None: _normalize() guarantees the node and its keys exist, but we
    still fall back defensively so a caller that hand-built a db without
    normalizing gets a sane shape rather than a KeyError.
    """
    return db.setdefault(MAP_KEY, {
        'revealed_hexes': [],
        'marker_x': 0,
        'marker_y': 0,
        'marker_visible': False,
        'marker_scale': 1.0,
        'marker_icon': '',
        'marker_color': '#c0533b',
        'grid_cols': 20,
        'grid_rows': 15,
        'fog_color': '#0d0b0a',
        'map_image': None,
        'offset_x': 0.0,
        'offset_y': 0.0,
        'hex_size': 5.0,
        'pois': [],
        'focus': {'seq': 0, 'x': 50.0, 'y': 50.0, 'scale': 1.0},
    })


# Bounds for the grid dimensions the Master can set. A hard ceiling stops a
# typo (2300 instead of 23) from asking the browser to draw millions of hexes.
GRID_MIN = 1
GRID_MAX = 400


def _clean_hex_color(raw, fallback):
    """Return a #rrggbb / #rgb string, or `fallback` for anything else.

    Guards the fog colour: it is written straight into CSS on both the master
    and player pages, so only a real hex colour is allowed through -- never an
    arbitrary string that could carry other CSS.
    """
    raw = (raw or '').strip()
    if len(raw) in (4, 7) and raw[0] == '#' and \
            all(c in '0123456789abcdefABCDEF' for c in raw[1:]):
        return raw
    return fallback

# Caps for POIs. A generous ceiling on count stops a runaway client from
# stuffing the draft, and a label cap keeps one pin from carrying an essay
# (the label is rendered as plain text, so length is the only concern).
POI_MAX = 200
POI_LABEL_MAX = 80
# The icon is a single glyph the Master picks (a letter, an emoji, a symbol).
# We cap it short so it stays a marker, not a text field. Emoji can be multiple
# code points (e.g. flags, ZWJ sequences), so the cap is generous but bounded.
POI_ICON_MAX = 8
# POI/marker scale multipliers, clamped so a bad value can't make a pin fill
# the screen or vanish.
SCALE_MIN = 0.3
SCALE_MAX = 4.0
# A hex colour like #rrggbb or #rgb; anything else falls back to the default.
_HEX_COLOR_RE = re.compile(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')
POI_DEFAULT_COLOR = '#e8a83a'


def _clean_scale(value, default=1.0):
    """Clamp a scale multiplier to SCALE_MIN..SCALE_MAX, or return default."""
    try:
        return max(SCALE_MIN, min(SCALE_MAX, float(value)))
    except (TypeError, ValueError):
        return default


def _clean_color(value, default=POI_DEFAULT_COLOR):
    """Return value if it is a #rgb/#rrggbb hex colour, else the default."""
    if isinstance(value, str) and _HEX_COLOR_RE.match(value.strip()):
        return value.strip().lower()
    return default


def _clean_pois(raw, previous):
    """Return a validated list of POI dicts, or `previous` if `raw` is junk.

    Each POI is normalised to
    {id, label, x, y, always_visible, icon, color, scale}. x/y are clamped to
    0..100 (percent of the image). A POI with no usable id gets a fresh one; a
    blank label is allowed (the Master may pin first, name later). Anything that
    isn't a list leaves the previous value untouched, so a partial patch that
    omits `pois` never wipes them.
    """
    if not isinstance(raw, (list, tuple)):
        return previous
    cleaned = []
    seen_ids = set()
    for item in raw[:POI_MAX]:
        if not isinstance(item, dict):
            continue
        pid = str(item.get('id') or '').strip()
        if not pid or pid in seen_ids:
            pid = uuid.uuid4().hex
        seen_ids.add(pid)
        label = str(item.get('label') or '').strip()[:POI_LABEL_MAX]
        try:
            x = max(0.0, min(100.0, float(item.get('x', 0))))
        except (TypeError, ValueError):
            x = 0.0
        try:
            y = max(0.0, min(100.0, float(item.get('y', 0))))
        except (TypeError, ValueError):
            y = 0.0
        # icon: a short custom glyph. Empty string means "use the default pin".
        icon = str(item.get('icon') or '').strip()[:POI_ICON_MAX]
        # category: a free-text group the Master assigns (e.g. "Cities",
        # "Ruins"). Empty = uncategorised. Capped so it stays a tag, not prose.
        category = str(item.get('category') or '').strip()[:POI_LABEL_MAX]
        cleaned.append({
            'id': pid,
            'label': label,
            'x': x,
            'y': y,
            'always_visible': bool(item.get('always_visible', True)),
            'icon': icon,
            'color': _clean_color(item.get('color')),
            'scale': _clean_scale(item.get('scale')),
            'category': category,
            # Optional filled background behind the icon/pin, with its own
            # colour independent of the icon colour. icon_bg False = no plate.
            'icon_bg': bool(item.get('icon_bg', False)),
            'icon_bg_color': _clean_color(item.get('icon_bg_color'), '#241d18'),
        })
    return cleaned


def _coerce_map_fields(target, data):
    """Write the known map fields from `data` into `target` dict, in place.

    Shared by the draft writer and the map-upload route so validation lives in
    one spot. Unknown keys are ignored; bad types leave the previous value.
    `target` is either the confirmed state or its `pending` sub-dict.
    """
    if 'revealed_hexes' in data:
        hexes = data['revealed_hexes']
        if isinstance(hexes, (list, tuple)):
            seen = set()
            cleaned = []
            for hx in hexes:
                key = str(hx)
                if key not in seen:
                    seen.add(key)
                    cleaned.append(key)
            target['revealed_hexes'] = cleaned

    for axis in ('marker_x', 'marker_y'):
        if axis in data:
            try:
                target[axis] = float(data[axis])
            except (TypeError, ValueError):
                pass

    if 'marker_visible' in data:
        target['marker_visible'] = bool(data['marker_visible'])

    if 'marker_scale' in data:
        target['marker_scale'] = _clean_scale(data['marker_scale'])

    if 'marker_icon' in data:
        target['marker_icon'] = str(data['marker_icon'] or '').strip()[:POI_ICON_MAX]

    if 'marker_color' in data:
        target['marker_color'] = _clean_color(data['marker_color'], '#c0533b')

    for key in ('grid_cols', 'grid_rows'):
        if key in data:
            try:
                n = int(data[key])
                target[key] = max(GRID_MIN, min(GRID_MAX, n))
            except (TypeError, ValueError):
                pass

    # Calibration floats (percent). offset can be slightly negative so the grid
    # can start just off the top-left corner; hex_size has a sane floor so a
    # zero never collapses every hex to a point.
    for key in ('offset_x', 'offset_y'):
        if key in data:
            try:
                target[key] = max(-50.0, min(150.0, float(data[key])))
            except (TypeError, ValueError):
                pass
    if 'hex_size' in data:
        try:
            target['hex_size'] = max(0.5, min(100.0, float(data['hex_size'])))
        except (TypeError, ValueError):
            pass

    if 'fog_color' in data:
        target['fog_color'] = _clean_hex_color(
            data['fog_color'], target.get('fog_color', '#0d0b0a'))

    if 'map_image' in data:
        val = data['map_image']
        if val is None:
            target['map_image'] = None
        elif isinstance(val, str) and '/' not in val and '\\' not in val:
            target['map_image'] = val

    if 'pois' in data:
        target['pois'] = _clean_pois(data['pois'], target.get('pois', []))


def update_map_state(db, data):
    """Write `data` into the DRAFT (pending) layer and return the full state.

    This is what the Master's live edits hit: revealing a hex, dragging the
    marker, changing the grid or fog colour all land in `pending` and are NOT
    visible to players until confirm_map_state() promotes them. `data` may
    carry any subset of the known keys.

    NB: the map-upload route writes map_image straight to BOTH layers via
    set_map_image() -- see there for why an uploaded image is not staged.
    """
    state = get_map_state(db)
    pending = state.setdefault('pending', {})
    _coerce_map_fields(pending, data or {})
    return state


def set_map_image(db, filename):
    """Set (or clear) the map background on BOTH the confirmed and draft layers.

    The background image is deliberately NOT staged: an uploaded map is a setup
    action, not a reveal, and a half-set-up map where the Master sees the new
    image but players still see the old one (until a confirm) would be more
    confusing than useful. Upload = immediately live for everyone.
    """
    state = get_map_state(db)
    _coerce_map_fields(state, {'map_image': filename})
    _coerce_map_fields(state.setdefault('pending', {}), {'map_image': filename})
    return state


def confirm_map_state(db):
    """Promote the draft to confirmed: players now see what the Master staged.

    Copies every pending field onto the confirmed state and bumps confirm_seq
    so player pages can tell this is a fresh confirmation. This is the ONLY
    function that changes what players read (aside from set_map_image).
    """
    state = get_map_state(db)
    pending = state.get('pending', {})
    for key in ('revealed_hexes', 'marker_x', 'marker_y', 'marker_visible',
                'marker_scale', 'marker_icon', 'marker_color',
                'grid_cols', 'grid_rows', 'fog_color',
                'map_image', 'offset_x', 'offset_y', 'hex_size', 'pois'):
        if key in pending:
            # Copy lists by value so the two layers don't alias. POIs need a
            # deep copy: each is a dict, and a shallow list() would still let
            # a later draft edit mutate the confirmed pin in place.
            if key == 'revealed_hexes':
                state[key] = list(pending[key])
            elif key == 'pois':
                state[key] = [dict(poi) for poi in pending[key]]
            else:
                state[key] = pending[key]
    state['confirm_seq'] = state.get('confirm_seq', 0) + 1
    return state


def discard_map_state(db):
    """Throw the draft away: reset pending back to the confirmed state.

    Used by the Master's 'Discard changes' button so a session of experimental
    reveals can be abandoned wholesale without touching what players see.
    """
    state = get_map_state(db)
    state['pending'] = {
        'revealed_hexes': list(state['revealed_hexes']),
        'marker_x': state['marker_x'],
        'marker_y': state['marker_y'],
        'marker_visible': state['marker_visible'],
        'marker_scale': state['marker_scale'],
        'marker_icon': state['marker_icon'],
        'marker_color': state['marker_color'],
        'grid_cols': state['grid_cols'],
        'grid_rows': state['grid_rows'],
        'fog_color': state['fog_color'],
        'map_image': state['map_image'],
        'offset_x': state['offset_x'],
        'offset_y': state['offset_y'],
        'hex_size': state['hex_size'],
        'pois': [dict(poi) for poi in state['pois']],
    }
    return state


def set_map_focus(db, x, y, scale):
    """Record a camera-focus broadcast and return the new focus dict.

    Not staged: a focus is a live "look here, now" directive, so it takes
    effect immediately rather than waiting for a confirm -- the same design as
    a POP. Bumping seq is what notifies players: they poll for it and animate
    to the new centre/zoom on any value above the last one they acted on, so a
    Master re-focusing the same spot still nudges a table that drifted away.

    x/y are the focus point as PERCENT of the image (clamped 0..100); scale is
    the zoom level, clamped to a sane range so a bad client value can't ask the
    player view for an absurd magnification.
    """
    state = get_map_state(db)
    focus = state.setdefault('focus', {'seq': 0})
    try:
        fx = max(0.0, min(100.0, float(x)))
    except (TypeError, ValueError):
        fx = 50.0
    try:
        fy = max(0.0, min(100.0, float(y)))
    except (TypeError, ValueError):
        fy = 50.0
    try:
        fs = max(0.1, min(8.0, float(scale)))
    except (TypeError, ValueError):
        fs = 1.0
    state['focus'] = {
        'seq': focus.get('seq', 0) + 1,
        'x': fx, 'y': fy, 'scale': fs,
    }
    return state['focus']


def all_categories(db):
    return sorted({h.get('category', '').strip()
                   for h in db['handouts'] if h.get('category', '').strip()})


def all_tags(db):
    """Every distinct tag across handouts, sorted case-insensitively."""
    tags = set()
    for h in db['handouts']:
        for t in h.get('tags', []):
            t = t.strip()
            if t:
                tags.add(t)
    return sorted(tags, key=str.lower)


def parse_tags(raw):
    """Split a comma-separated tag string into a clean, de-duplicated list.

    Order is preserved (first occurrence wins); comparison is case-insensitive
    so 'Map' and 'map' don't both survive.
    """
    seen = set()
    out = []
    for part in (raw or '').split(','):
        t = part.strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def parse_passwords(raw):
    """Split the secret-reveal textarea into a clean list of accepted words.

    One password per line: passwords may well contain spaces or commas ("open
    sesame", "3,000 gold"), so a newline is the only safe separator. Blank
    lines are dropped and exact duplicates removed while keeping first-seen
    order. Case is preserved here; whether case matters at match time is the
    separate secret_ignore_case flag's job (see reveal_secret).
    """
    seen = set()
    out = []
    for line in (raw or '').replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        p = line.strip()
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def parse_session_number(raw):
    raw = (raw or '').strip()
    try:
        return int(raw) if raw else None
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Folders (master-defined, id + name, multi-membership on handouts)
# --------------------------------------------------------------------------

def all_folders(db):
    """Folders sorted by name (case-insensitive). Each is {id, name}."""
    return sorted(db.get('folders', []),
                  key=lambda fo: fo.get('name', '').lower())


def find_folder(db, folder_id):
    return next((fo for fo in db.get('folders', [])
                 if fo['id'] == folder_id), None)


def create_folder(db, name):
    """Create a folder if the name is non-empty and not a duplicate.

    Returns the folder dict (existing or new); returns None for empty names.
    Name matching is case-insensitive to avoid near-duplicate folders.
    """
    name = (name or '').strip()
    if not name:
        return None
    existing = next((fo for fo in db.get('folders', [])
                     if fo.get('name', '').lower() == name.lower()), None)
    if existing:
        return existing
    folder = {'id': uuid.uuid4().hex, 'name': name}
    db.setdefault('folders', []).append(folder)
    return folder


def rename_folder(db, folder_id, name):
    """Rename a folder in place. No-op if the folder is gone or name empty."""
    name = (name or '').strip()
    folder = find_folder(db, folder_id)
    if folder and name:
        folder['name'] = name
    return folder


def delete_folder(db, folder_id):
    """Remove a folder and detach it from every handout (handouts are kept)."""
    db['folders'] = [fo for fo in db.get('folders', [])
                     if fo['id'] != folder_id]
    for h in db['handouts']:
        if folder_id in h.get('folders', []):
            h['folders'] = [fid for fid in h['folders'] if fid != folder_id]


def valid_folder_ids(db, folder_ids):
    """Keep only ids that correspond to folders that actually exist."""
    known = {fo['id'] for fo in db.get('folders', [])}
    return [fid for fid in folder_ids if fid in known]


# --------------------------------------------------------------------------
# File operations
# --------------------------------------------------------------------------

def save_files(file_storages, handout_id, prefix='', descriptions=None):
    """Save a list of Werkzeug FileStorage objects to the uploads folder.

    Returns a list of {'filename', 'reader', 'description'} entries. `prefix`
    keeps names unique when adding files to an existing handout (e.g. a
    timestamp). `descriptions` is an optional list aligned by index with
    `file_storages`; missing/short entries default to ''.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    descriptions = descriptions or []
    stored = []
    for idx, f in enumerate(file_storages):
        safe_name = secure_filename(f.filename)
        ext = safe_name.rsplit('.', 1)[1].lower()
        name = f'{handout_id}_{prefix}{idx}.{ext}' if prefix \
            else f'{handout_id}_{idx}.{ext}'
        f.save(os.path.join(UPLOAD_DIR, name))
        desc = descriptions[idx].strip() if idx < len(descriptions) else ''
        stored.append({'filename': name,
                       'reader': reader_for(ext),
                       'description': desc})
    return stored


def remove_files(file_entries):
    """Delete stored files from disk, best-effort.

    Also removes a PDF's generated thumbnail, if the entry carries one, so
    rendered artefacts never outlive the file they belong to.
    """
    for entry in file_entries:
        names = [entry['filename']]
        if entry.get('thumb'):
            names.append(entry['thumb'])
        for name in names:
            try:
                os.remove(os.path.join(UPLOAD_DIR, name))
            except OSError:
                pass


def save_back_cover(file_storage, handout_id):
    """Save a single back-cover file and return its {filename, reader,
    description} entry, or None if no file was given.

    Named with a 'back' marker so it never collides with page files.
    """
    if not file_storage or not file_storage.filename:
        return None
    stored = save_files([file_storage], handout_id, prefix='back_')
    return stored[0] if stored else None


def allowed_map_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in MAP_EXTENSIONS


def save_map_image(file_storage):
    """Save an uploaded map background into MAP_DIR and return its filename.

    Returns None if no usable file was given. The name is timestamped so a new
    upload never collides with (or silently overwrites) a cached older one on
    the players' browsers. Only the bare filename is returned; the caller
    stores it in map_state['map_image'] and the templates build the URL.
    """
    if not file_storage or not file_storage.filename:
        return None
    safe = secure_filename(file_storage.filename)
    if '.' not in safe:
        return None
    ext = safe.rsplit('.', 1)[1].lower()
    os.makedirs(MAP_DIR, exist_ok=True)
    name = f'map_{now_stamp()}.{ext}'
    file_storage.save(os.path.join(MAP_DIR, name))
    return name


def remove_map_image(filename):
    """Delete a saved map background, best-effort. Silent if already gone."""
    if not filename:
        return
    # Defend against a stored value that somehow carries a path: only ever
    # touch a bare name inside MAP_DIR.
    if '/' in filename or '\\' in filename:
        return
    try:
        os.remove(os.path.join(MAP_DIR, filename))
    except OSError:
        pass


def new_handout_id():
    return uuid.uuid4().hex


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_stamp():
    return int(datetime.now(timezone.utc).timestamp())