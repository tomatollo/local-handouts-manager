"""Export / import of the whole handout library as a single .zip.

An export bundle contains the database JSON plus every referenced upload, so
it can be carried to another computer. Import merges the incoming library into
the current one: brand-new handouts (by id) are added outright, while handouts
whose id already exists but whose content differs are reported as conflicts
for the Master to resolve one by one (keep Local vs Replace with imported).

All functions here are pure-ish helpers over paths + dicts; the routes stay
thin and own the HTTP/session flow.
"""

import io
import json
import os
import zipfile

from . import storage

# Name of the JSON entry inside the bundle.
MANIFEST_NAME = 'database.json'
# Folder inside the bundle that holds the graphics.
BUNDLE_UPLOADS = 'uploads/'


def _handout_filenames(h):
    """Every stored filename a handout references (pages + back cover).

    Includes generated PDF thumbnails so an imported library still shows its
    previews without having to re-render anything.
    """
    names = []
    entries = list(h.get('files', []))
    bc = h.get('back_cover')
    if bc:
        entries.append(bc)
    for entry in entries:
        if entry.get('filename'):
            names.append(entry['filename'])
        if entry.get('thumb'):
            names.append(entry['thumb'])
    return names


def export_bytes():
    """Build the export .zip in memory and return its raw bytes.

    Includes the normalized database and every upload it references. Files that
    are referenced but missing on disk are simply skipped (best-effort).
    """
    db = storage.load_db()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_NAME,
                    json.dumps(db, indent=2, ensure_ascii=False))
        seen = set()
        for h in db['handouts']:
            for name in _handout_filenames(h):
                if name in seen:
                    continue
                seen.add(name)
                src = os.path.join(storage.UPLOAD_DIR, name)
                if os.path.exists(src):
                    zf.write(src, BUNDLE_UPLOADS + name)
    buf.seek(0)
    return buf.getvalue()


def _read_bundle(zip_bytes):
    """Parse an uploaded bundle into (incoming_db, zipfile). Raises ValueError
    if the bundle is not a valid export."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        raise ValueError('That file is not a valid .zip archive.')
    if MANIFEST_NAME not in zf.namelist():
        raise ValueError('The archive has no database.json; '
                         'it is not a handout export.')
    try:
        incoming = json.loads(zf.read(MANIFEST_NAME).decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError('The database.json in the archive is unreadable.')
    storage._normalize(incoming)
    return incoming, zf


def _content_signature(h):
    """A comparable view of a handout's content, ignoring nothing meaningful.

    Two handouts with the same id are 'the same file' only if this matches;
    otherwise it's a conflict the Master must resolve.
    """
    return json.dumps({
        'title': h.get('title', ''),
        'description': h.get('description', ''),
        'category': h.get('category', ''),
        'tags': sorted(h.get('tags', [])),
        'folders': sorted(h.get('folders', [])),
        'view_type': h.get('view_type', ''),
        'session_number': h.get('session_number'),
        'session_title': h.get('session_title', ''),
        'found_location': h.get('found_location', ''),
        'found_date': h.get('found_date', ''),
        'visible': h.get('visible', False),
        'files': h.get('files', []),
        'back_cover': h.get('back_cover'),
    }, sort_keys=True, ensure_ascii=False)


def analyze(zip_bytes):
    """Compare an incoming bundle against the current library.

    Returns a dict:
      {
        'new':       [incoming handout, ...],   # ids not present locally
        'identical': [id, ...],                 # same id, same content (skip)
        'conflicts': [{'id', 'local', 'incoming'}, ...],  # same id, differ
        'incoming_folders': [...],              # folders from the bundle
      }
    Nothing is written; this only inspects.
    """
    incoming, _zf = _read_bundle(zip_bytes)
    local = storage.load_db()
    local_by_id = {h['id']: h for h in local['handouts']}

    new, identical, conflicts = [], [], []
    for h in incoming['handouts']:
        cur = local_by_id.get(h['id'])
        if cur is None:
            new.append(h)
        elif _content_signature(cur) == _content_signature(h):
            identical.append(h['id'])
        else:
            conflicts.append({'id': h['id'], 'local': cur, 'incoming': h})

    return {
        'new': new,
        'identical': identical,
        'conflicts': conflicts,
        'incoming_folders': incoming.get('folders', []),
    }


def _extract_files_for(handout, zf):
    """Copy a handout's referenced uploads out of the bundle onto disk.

    Overwrites existing files of the same name (they are id-scoped, so this is
    the intended behaviour when replacing). Missing bundle members are skipped.
    """
    os.makedirs(storage.UPLOAD_DIR, exist_ok=True)
    members = set(zf.namelist())
    for name in _handout_filenames(handout):
        member = BUNDLE_UPLOADS + name
        if member in members:
            with zf.open(member) as src:
                dest = os.path.join(storage.UPLOAD_DIR, name)
                with open(dest, 'wb') as out:
                    out.write(src.read())


def apply_import(zip_bytes, resolutions):
    """Apply a merge. `resolutions` maps conflict id -> 'local' | 'imported'.

    - New handouts: added, with their files extracted.
    - Conflicts resolved 'imported': local replaced (old files removed, new
      files extracted). 'local' (or missing/unknown): left untouched.
    - Folders: any incoming folder whose id is not present locally is added,
      so folder memberships carried on imported handouts still resolve.
    Returns a summary dict of counts.
    """
    incoming, zf = _read_bundle(zip_bytes)
    db = storage.load_db()
    local_by_id = {h['id']: h for h in db['handouts']}

    added = replaced = kept = 0

    # Merge folders first (by id) so membership references stay valid.
    local_folder_ids = {fo['id'] for fo in db.get('folders', [])}
    for fo in incoming.get('folders', []):
        if fo['id'] not in local_folder_ids:
            db.setdefault('folders', []).append(fo)
            local_folder_ids.add(fo['id'])

    incoming_by_id = {h['id']: h for h in incoming['handouts']}
    for hid, h in incoming_by_id.items():
        cur = local_by_id.get(hid)
        if cur is None:
            _extract_files_for(h, zf)
            db['handouts'].append(h)
            added += 1
        elif _content_signature(cur) == _content_signature(h):
            # identical - nothing to do
            continue
        else:
            choice = resolutions.get(hid, 'local')
            if choice == 'imported':
                # Remove the local files that are being superseded, then bring
                # in the imported record + its files.
                storage.remove_files(cur.get('files', []))
                if cur.get('back_cover'):
                    storage.remove_files([cur['back_cover']])
                _extract_files_for(h, zf)
                idx = db['handouts'].index(cur)
                db['handouts'][idx] = h
                replaced += 1
            else:
                kept += 1

    storage.save_db(db)
    return {'added': added, 'replaced': replaced, 'kept_local': kept}
