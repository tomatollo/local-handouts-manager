"""Data + file storage for handouts.

Everything that touches the JSON database or the uploads folder lives here,
so the route modules stay thin and free of persistence details.
"""

import json
import os
import uuid
from datetime import datetime, timezone

from werkzeug.utils import secure_filename

from . import theming

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.json')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')

# Extension whitelist (images + PDF). Kept lowercase, no leading dot.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

# How a handout's files are presented to players. This is a handout-level
# property (distinct from each file's `reader`, which is image/pdf).
VIEW_TYPES = ('carousel', 'book')
DEFAULT_VIEW_TYPE = 'carousel'

# Key under `settings` holding the current POP broadcast (see pop_state).
POP_KEY = 'pop'

# How long a POP stays live, in seconds.
#
# A POP is a moment at the table ("look at this, now"), not a piece of state.
# Without an expiry the stored pointer stays true forever, so every player who
# joined, reloaded or woke their phone hours later got the modal again -- the
# handout is still popped, as far as the DB is concerned. Two minutes is long
# enough to cover a latecomer or a phone that was asleep during the reveal, and
# short enough that the POP is over before the scene is.
POP_TTL_SECONDS = 120


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
# Database load / save / normalize
# --------------------------------------------------------------------------

def load_db():
    """Load the DB, creating an empty one if missing (robust for clones)."""
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump({'handouts': [], 'folders': []}, f)
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    _normalize(data)
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
        # Optional back cover (a single file entry or None). Shown as the very
        # last page in the Book viewer. Ignored by the carousel.
        h.setdefault('back_cover', None)
        if h.get('back_cover'):
            h['back_cover'].setdefault('description', '')
            h['back_cover'].setdefault('thumb', None)


def save_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# Record helpers
# --------------------------------------------------------------------------

def find(db, handout_id):
    return next((h for h in db['handouts'] if h['id'] == handout_id), None)


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


def new_handout_id():
    return uuid.uuid4().hex


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_stamp():
    return int(datetime.now(timezone.utc).timestamp())
