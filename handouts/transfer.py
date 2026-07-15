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

# Settings that must never leave this machine. A bundle is carried on a USB
# stick or emailed, so it is treated as public: the passphrase hash would be
# offered up for offline cracking, and the session signing key is worse still
# -- anyone holding it can forge an `is_master` cookie without ever knowing the
# passphrase. The theme is genuinely portable and stays.
PRIVATE_SETTINGS = ('master_passphrase_hash', 'secret_key')


def _public_db(db):
    """A copy of the DB safe to write into an export bundle.

    Only `settings` is filtered; handouts, folders and wiki pages travel whole.
    The copy is shallow apart from `settings`, which is the only thing rebuilt,
    so nothing here mutates the caller's DB.
    """
    out = dict(db)
    out['settings'] = {k: v for k, v in db.get('settings', {}).items()
                       if k not in PRIVATE_SETTINGS}
    return out


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

    Includes the normalized database (minus this machine's credentials, see
    PRIVATE_SETTINGS) and every upload it references. Files that are referenced
    but missing on disk are simply skipped (best-effort).
    """
    db = storage.load_db()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_NAME,
                    json.dumps(_public_db(db), indent=2, ensure_ascii=False))
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
        'new_wiki':  [incoming wiki page, ...], # wiki pages not present locally
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

    # Wiki pages are reported but not conflict-resolved: they are small, plain
    # text and cheap to re-edit, so the flow stays simple -- brand-new pages
    # are added and anything already present is left alone. The Master keeps
    # their own version rather than being asked page by page.
    local_wiki_ids = {p['id'] for p in local.get('wiki', [])}
    new_wiki = [p for p in incoming.get('wiki', [])
                if p['id'] not in local_wiki_ids]

    return {
        'new': new,
        'identical': identical,
        'conflicts': conflicts,
        'incoming_folders': incoming.get('folders', []),
        'new_wiki': new_wiki,
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
    - Wiki: incoming pages whose id is not present locally are added, scope
      and all. Existing ids are left alone (see analyze).
    - Settings are NOT merged: the theme is a local choice, and the bundle
      deliberately carries no credentials (see PRIVATE_SETTINGS).
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

    # Wiki pages: add the ones we don't have. Their scope rides along with the
    # record, so a master page stays a master page across the transfer.
    local_wiki_ids = {p['id'] for p in db.get('wiki', [])}
    wiki_added = 0
    for p in incoming.get('wiki', []):
        if p['id'] not in local_wiki_ids:
            db.setdefault('wiki', []).append(p)
            local_wiki_ids.add(p['id'])
            wiki_added += 1

    storage.save_db(db)
    return {'added': added, 'replaced': replaced, 'kept_local': kept,
            'wiki_added': wiki_added}
