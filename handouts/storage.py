"""Data + file storage for handouts.

Everything that touches the JSON database or the uploads folder lives here,
so the route modules stay thin and free of persistence details.
"""

import json
import os
import uuid
from datetime import datetime, timezone

from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.json')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')

# Extension whitelist (images + PDF). Kept lowercase, no leading dot.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

# How a handout's files are presented to players. This is a handout-level
# property (distinct from each file's `reader`, which is image/pdf).
VIEW_TYPES = ('carousel', 'book')
DEFAULT_VIEW_TYPE = 'carousel'


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


def save_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# Record helpers
# --------------------------------------------------------------------------

def find(db, handout_id):
    return next((h for h in db['handouts'] if h['id'] == handout_id), None)


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
    """Delete stored files from disk, best-effort."""
    for entry in file_entries:
        try:
            os.remove(os.path.join(UPLOAD_DIR, entry['filename']))
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
