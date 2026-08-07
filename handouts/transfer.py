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
# Folder inside the bundle that holds the handout graphics.
BUNDLE_UPLOADS = 'uploads/'
# Folder inside the bundle that holds the interactive-map background image.
# Kept separate from uploads/ because on disk the two live in different places
# (static/uploads vs static/maps) and must be restored to the right one.
BUNDLE_MAPS = 'maps/'

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


def _map_image_names(db):
    """Every map-background filename the DB references, deduplicated.

    The confirmed state and the Master's unconfirmed draft (`pending`) can name
    different images -- the Master may have uploaded a new map but not yet
    confirmed it -- so both are collected, or the draft's image would be lost
    on transfer. Bare filenames only (no path); they live in static/maps.
    """
    names = []
    map_state = db.get('map_state', {})
    for source in (map_state, map_state.get('pending', {})):
        name = source.get('map_image')
        if name and name not in names:
            names.append(name)
    return names


# Name of the JSON entry listing files the export could NOT include because
# they were referenced by the database but absent on disk. Its presence in a
# bundle is a breadcrumb for the import side and for a human opening the zip.
MISSING_MANIFEST_NAME = 'missing_files.json'


def export_bytes():
    """Build the export .zip in memory and return (raw_bytes, missing).

    Includes the normalized database (minus this machine's credentials, see
    PRIVATE_SETTINGS), every upload it references, and the interactive-map
    background image(s).

    A file that is referenced by the database but not present on disk cannot be
    put in the bundle. Rather than dropping it *silently* -- which is how an
    imported library ends up with a handful of broken images "at random" -- such
    files are collected and returned in `missing`, and also written into the
    bundle as MISSING_MANIFEST_NAME so the fact travels with the zip. The caller
    (the Master UI / the CLI) is expected to surface `missing` to the user.

    Before scanning, any absent PDF thumbnails are re-rendered on the fly
    (they are generated lazily elsewhere, so an export taken right after an
    upload could otherwise miss them); a thumb that still can't be produced is
    reported like any other missing file rather than aborting the export.
    """
    db = storage.load_db()

    # Re-render any missing PDF thumbnails so a freshly-uploaded PDF doesn't
    # export without its preview. backfill_thumbs mutates the db in memory and
    # returns True if it changed anything; persist so the names it filled in
    # match what we are about to zip and what the DB now claims.
    try:
        from . import pdfs
        if pdfs.backfill_thumbs(db):
            storage.save_db(db)
    except Exception:
        # Thumbnail rendering must never block a backup. A thumb that couldn't
        # be produced simply shows up in `missing` below.
        pass

    missing = []
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_NAME,
                    json.dumps(_public_db(db), indent=2, ensure_ascii=False))
        # Handout graphics (pages, back covers, PDF thumbnails).
        seen = set()
        for h in db['handouts']:
            for name in _handout_filenames(h):
                if name in seen:
                    continue
                seen.add(name)
                src = os.path.join(storage.UPLOAD_DIR, name)
                if os.path.exists(src):
                    zf.write(src, BUNDLE_UPLOADS + name)
                else:
                    # Referenced but gone: record which handout it belonged to
                    # so the Master can find and re-upload it.
                    missing.append({'file': name, 'handout_id': h.get('id'),
                                    'title': h.get('title', ''),
                                    'kind': 'upload'})
        # Interactive-map background image(s), from static/maps. Without this
        # the imported map_state would point at a file that never travelled,
        # leaving the map blank on the destination machine.
        for name in _map_image_names(db):
            src = os.path.join(storage.MAP_DIR, name)
            if os.path.exists(src):
                zf.write(src, BUNDLE_MAPS + name)
            else:
                missing.append({'file': name, 'handout_id': None,
                                'title': 'Interactive map background',
                                'kind': 'map'})
        # Leave a breadcrumb inside the bundle itself.
        if missing:
            zf.writestr(MISSING_MANIFEST_NAME,
                        json.dumps(missing, indent=2, ensure_ascii=False))
    buf.seek(0)
    return buf.getvalue(), missing


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
        'hard_covers': h.get('hard_covers', True),
        'source_format': h.get('source_format', ''),
        'session_number': h.get('session_number'),
        'session_title': h.get('session_title', ''),
        'found_location': h.get('found_location', ''),
        'found_date': h.get('found_date', ''),
        'visible': h.get('visible', False),
        'files': h.get('files', []),
        'back_cover': h.get('back_cover'),
    }, sort_keys=True, ensure_ascii=False)


# Fields of map_state that represent real Master work. Used to decide whether an
# incoming (or local) map is worth offering as an import choice, and to compare
# two maps for equality. The staging/bookkeeping keys (`pending`, `confirm_seq`,
# `focus`) are deliberately excluded: they are transient and not "content".
_MAP_CONTENT_KEYS = (
    'revealed_hexes', 'pois', 'map_image',
    'marker_x', 'marker_y', 'marker_visible', 'marker_scale',
    'marker_icon', 'marker_color',
    'grid_cols', 'grid_rows', 'fog_color',
    'offset_x', 'offset_y', 'hex_size',
)


def _map_signature(map_state):
    """A comparable view of a map's meaningful content (ignores staging keys)."""
    view = {}
    for k in _MAP_CONTENT_KEYS:
        v = map_state.get(k)
        # Order-independent for the hex/POI lists so a reshuffle isn't a diff.
        if k == 'revealed_hexes' and isinstance(v, list):
            v = sorted(str(x) for x in v)
        elif k == 'pois' and isinstance(v, list):
            v = sorted(json.dumps(p, sort_keys=True, ensure_ascii=False)
                       for p in v)
        view[k] = v
    return json.dumps(view, sort_keys=True, ensure_ascii=False)


def _map_has_content(map_state):
    """True if a map carries anything a Master would care to keep.

    A freshly-initialised map (no image, no revealed hexes, no POIs, marker
    hidden at the origin) is 'empty' and never worth offering as an import
    choice. Anything beyond that -- an uploaded background, revealed terrain,
    pinned POIs -- counts as content.
    """
    if not map_state:
        return False
    if map_state.get('map_image'):
        return True
    if map_state.get('revealed_hexes'):
        return True
    if map_state.get('pois'):
        return True
    if map_state.get('marker_visible'):
        return True
    return False


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

    # Interactive map. Unlike handouts, the map is a single global object, not a
    # collection to merge by id, so it can't be split into new/identical/
    # conflict. Instead we report enough for the review page to offer ONE
    # explicit choice -- keep the local map or take the incoming one -- and only
    # when it's a real decision:
    #   * incoming has no content  -> nothing to offer (map_action omitted).
    #   * local has no content     -> offer it, but there's nothing to lose.
    #   * both have content + differ -> a genuine either/or the Master resolves.
    #   * both identical           -> no choice needed.
    incoming_map = incoming.get('map_state', {})
    local_map = local.get('map_state', {})
    map_report = None
    if _map_has_content(incoming_map):
        differs = _map_signature(incoming_map) != _map_signature(local_map)
        if differs:
            map_report = {
                'incoming_has_content': True,
                'local_has_content': _map_has_content(local_map),
                'incoming_hexes': len(incoming_map.get('revealed_hexes', [])),
                'incoming_pois': len(incoming_map.get('pois', [])),
                'incoming_has_image': bool(incoming_map.get('map_image')),
                'local_hexes': len(local_map.get('revealed_hexes', [])),
                'local_pois': len(local_map.get('pois', [])),
                'local_has_image': bool(local_map.get('map_image')),
            }

    return {
        'new': new,
        'identical': identical,
        'conflicts': conflicts,
        'incoming_folders': incoming.get('folders', []),
        'new_wiki': new_wiki,
        'map': map_report,
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


def _ensure_files_on_disk(handout, zf):
    """Extract only the handout's files that are MISSING on disk.

    Used for handouts the merge does not otherwise touch (identical records, or
    conflicts the Master kept local). Their DB record already exists, but on a
    fresh machine -- or one where the JSON was copied over without its uploads,
    or the two were ever separated -- the referenced images are absent, so the
    player screens show broken pictures. This restores them from the bundle
    without overwriting anything that is already present (a kept-local record's
    own files stay as they are). Returns the number of files restored.
    """
    os.makedirs(storage.UPLOAD_DIR, exist_ok=True)
    members = set(zf.namelist())
    restored = 0
    for name in _handout_filenames(handout):
        dest = os.path.join(storage.UPLOAD_DIR, name)
        if os.path.exists(dest):
            continue
        member = BUNDLE_UPLOADS + name
        if member in members:
            with zf.open(member) as src:
                with open(dest, 'wb') as out:
                    out.write(src.read())
            restored += 1
    return restored


def _extract_map_images(incoming, zf):
    """Copy the incoming map background image(s) out of the bundle into
    static/maps. Missing members are skipped. Safe to call even if the map has
    no image (it simply copies nothing).

    Only bare filenames are honoured; a member whose stored name somehow
    carries a path separator is ignored, so a crafted bundle can't write
    outside static/maps.
    """
    os.makedirs(storage.MAP_DIR, exist_ok=True)
    members = set(zf.namelist())
    for name in _map_image_names(incoming):
        if '/' in name or '\\' in name:
            continue
        member = BUNDLE_MAPS + name
        if member in members:
            with zf.open(member) as src:
                dest = os.path.join(storage.MAP_DIR, name)
                with open(dest, 'wb') as out:
                    out.write(src.read())


def apply_import(zip_bytes, resolutions, import_map=False):
    """Apply a merge. `resolutions` maps conflict id -> 'local' | 'imported'.

    - New handouts: added, with their files extracted.
    - Conflicts resolved 'imported': local replaced (old files removed, new
      files extracted). 'local' (or missing/unknown): left untouched.
    - Folders: any incoming folder whose id is not present locally is added,
      so folder memberships carried on imported handouts still resolve.
    - Wiki: incoming pages whose id is not present locally are added, scope
      and all. Existing ids are left alone (see analyze).
    - Map: applied ONLY if `import_map` is True (the Master chose the incoming
      map on the review page). The map is a single global object, so importing
      it REPLACES the local one wholesale -- its image is extracted, the local
      background it supersedes is removed, and the draft (`pending`) is reset to
      match so the freshly-imported map isn't shadowed by a stale draft. When
      False, the local map is left exactly as it was.
    - Settings are NOT merged: the theme is a local choice, and the bundle
      deliberately carries no credentials (see PRIVATE_SETTINGS).
    Returns a summary dict of counts.
    """
    incoming, zf = _read_bundle(zip_bytes)
    db = storage.load_db()
    local_by_id = {h['id']: h for h in db['handouts']}

    added = replaced = kept = 0
    # Files pulled back from the bundle for records the merge didn't rewrite
    # (identical / kept-local) but whose images were missing on disk.
    restored_files = 0

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
            # Identical record: nothing to merge, but the files it points at may
            # be missing on this machine (fresh device, or a DB copied without
            # its uploads). Restore any that aren't already on disk so the
            # images actually load, then move on.
            restored_files += _ensure_files_on_disk(h, zf)
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
                # Kept local: the Master's own record wins, but its images may
                # still be absent here. Restore only the files that are missing
                # (the two sides share id-scoped filenames, so the bundle is a
                # valid source), never overwriting what is already on disk, so a
                # kept-local handout still shows its pictures.
                restored_files += _ensure_files_on_disk(cur, zf)
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

    # Interactive map: replace wholesale, only on explicit request.
    map_imported = False
    incoming_map = incoming.get('map_state', {})
    if import_map and _map_has_content(incoming_map):
        old_image = db.get('map_state', {}).get('map_image')
        _extract_map_images(incoming, zf)
        # Replace the whole map_state with the incoming one (already normalized
        # by _read_bundle). Bump confirm_seq so player pages pick up the change
        # on their next poll, then reset the draft (`pending`) to the imported
        # confirmed values via storage.discard_map_state, so the freshly-
        # imported map isn't shadowed by a stale local draft.
        new_map = incoming_map
        new_map['confirm_seq'] = db.get('map_state', {}).get('confirm_seq', 0) + 1
        db['map_state'] = new_map
        storage.discard_map_state(db)  # seeds pending from the confirmed state
        # Remove the previous background if the import replaced it with a
        # different file (or cleared it), so old maps don't pile up.
        new_image = new_map.get('map_image')
        if old_image and old_image != new_image:
            storage.remove_map_image(old_image)
        map_imported = True

    storage.save_db(db)
    return {'added': added, 'replaced': replaced, 'kept_local': kept,
            'wiki_added': wiki_added, 'map_imported': map_imported,
            'restored_files': restored_files}
