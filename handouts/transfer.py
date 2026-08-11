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
    """Every stored filename a handout references (pages + back cover +
    3D back texture).

    Includes generated PDF thumbnails so an imported library still shows its
    previews without having to re-render anything. The object3d viewer's
    reverse-side texture (`back_texture`) is included too, or a 3D sheet would
    lose its back face on transfer.
    """
    names = []
    entries = list(h.get('files', []))
    bc = h.get('back_cover')
    if bc:
        entries.append(bc)
    bt = h.get('back_texture')
    if bt:
        entries.append(bt)
    for entry in entries:
        if entry.get('filename'):
            names.append(entry['filename'])
        if entry.get('thumb'):
            names.append(entry['thumb'])
    return names


def _map_image_names(db):
    """Every map-background filename the DB references, deduplicated.

    Walks ALL maps (the table can have several) and, for each, both its
    confirmed state and the Master's unconfirmed draft (`pending`) -- the
    Master may have uploaded a new background but not yet confirmed it, so both
    are collected or the draft's image would be lost on transfer. Bare
    filenames only (no path); they live in static/maps.
    """
    names = []
    for m in db.get('maps', []):
        for source in (m, m.get('pending', {})):
            name = source.get('map_image')
            if name and name not in names:
                names.append(name)
    return names


def _map_image_names_one(m):
    """Map-background filename(s) for a SINGLE map dict (confirmed + draft)."""
    names = []
    for source in (m, m.get('pending', {})):
        name = source.get('map_image')
        if name and name not in names:
            names.append(name)
    return names


# Name of the JSON entry listing files the export could NOT include because
# they were referenced by the database but absent on disk. Its presence in a
# bundle is a breadcrumb for the import side and for a human opening the zip.
MISSING_MANIFEST_NAME = 'missing_files.json'


def _build_bundle(db):
    """Zip a (possibly filtered) DB into an export bundle in memory.

    Shared core of every export: the full-library backup and the single-item
    exports all funnel through here. `db` is whatever set of handouts/maps the
    caller wants in the bundle -- already trimmed to one item for the single
    exports -- and this writes the manifest plus every upload and map image the
    given records reference. Returns (raw_bytes, missing), where `missing`
    lists files referenced but absent on disk (also written into the bundle as
    a breadcrumb). The caller owns any DB mutation (e.g. thumbnail backfill)
    and PDF concerns; this function only reads and zips.
    """
    missing = []
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_NAME,
                    json.dumps(_public_db(db), indent=2, ensure_ascii=False))
        # Handout graphics (pages, back covers, PDF thumbnails).
        seen = set()
        for h in db.get('handouts', []):
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
        # the imported map would point at a file that never travelled, leaving
        # the map blank on the destination machine.
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


def _backfill_thumbs_quietly(db):
    """Re-render any missing PDF thumbnails so an export carries its previews.

    Mutates `db` in memory and persists if anything changed, so the names it
    fills in match what we are about to zip. Never raises: a thumb that can't
    be produced simply shows up in the export's `missing` list.
    """
    try:
        from . import pdfs
        if pdfs.backfill_thumbs(db):
            storage.save_db(db)
    except Exception:
        pass


def export_bytes():
    """Build the full-library export .zip in memory; return (raw_bytes, missing).

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
    _backfill_thumbs_quietly(db)
    return _build_bundle(db)


def _single_item_db(db, handouts=None, maps=None, folders=None):
    """A shallow copy of `db` carrying only the given handouts/maps/folders.

    Used by the single-item exports so the shared bundle builder and the import
    side see a normal DB shape -- just a smaller one. Wiki pages and settings
    are dropped (a single handout/map export shouldn't drag the whole wiki or
    any theme along); `_public_db` still strips credentials when the bundle is
    written. Folders are included so an exported handout's folder membership
    can be re-created on import.
    """
    return {
        'handouts': handouts or [],
        'maps': maps or [],
        'folders': folders or [],
        'wiki': [],
        'settings': db.get('settings', {}),
    }


def export_handout_bytes(handout_id):
    """Export ONE handout as a bundle; return (raw_bytes, missing).

    The bundle has the same shape as a full export, carrying just this handout
    plus the folders it belongs to (so its folder membership survives the
    round-trip). Because the format is identical, the ordinary import flow
    handles it with no special case: it simply reports one new/identical/
    conflicting handout. Returns (None, None) if the id doesn't exist.
    """
    db = storage.load_db()
    handout = storage.find(db, handout_id)
    if handout is None:
        return None, None
    _backfill_thumbs_quietly(db)
    # Re-fetch after the possible save+reload so we hand the builder the
    # thumbnail names it just filled in.
    handout = storage.find(db, handout_id) or handout
    # Carry only the folders this handout actually belongs to.
    member_ids = set(handout.get('folders', []))
    folders = [fo for fo in db.get('folders', []) if fo.get('id') in member_ids]
    sub = _single_item_db(db, handouts=[handout], folders=folders)
    return _build_bundle(sub)


def export_map_bytes(map_id):
    """Export ONE map as a bundle; return (raw_bytes, missing).

    Same shape as a full export, carrying just this map (and its background
    image). The ordinary import flow treats it as one new/identical/conflicting
    map. Returns (None, None) if the id doesn't exist.
    """
    db = storage.load_db()
    m = storage.find_map(db, map_id)
    if m is None:
        return None, None
    sub = _single_item_db(db, maps=[m])
    return _build_bundle(sub)


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
        'back_texture': h.get('back_texture'),
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


def _map_counts(m):
    """The small tallies the review page shows for a map (hexes/pois/image)."""
    return {
        'name': m.get('name', ''),
        'hexes': len(m.get('revealed_hexes', [])),
        'pois': len(m.get('pois', [])),
        'has_image': bool(m.get('map_image')),
    }


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

    # Interactive maps. The table can hold several, so -- like handouts --
    # they merge by id into new / identical / conflict, rather than the single
    # either-or the old single-map bundle used:
    #   * incoming id not present locally -> NEW: added outright on apply.
    #   * same id, same content           -> identical: skipped.
    #   * same id, content differs        -> conflict: the Master chooses keep
    #                                        local vs take imported, per map.
    # An incoming map with no content at all is ignored (nothing to carry).
    local_maps_by_id = {m['id']: m for m in local.get('maps', [])}
    new_maps, identical_maps, map_conflicts = [], [], []
    for m in incoming.get('maps', []):
        if not _map_has_content(m):
            continue
        cur = local_maps_by_id.get(m['id'])
        if cur is None:
            new_maps.append(_map_counts(m))
        elif _map_signature(cur) == _map_signature(m):
            identical_maps.append(m['id'])
        else:
            map_conflicts.append({
                'id': m['id'],
                'local': _map_counts(cur),
                'incoming': _map_counts(m),
            })

    return {
        'new': new,
        'identical': identical,
        'conflicts': conflicts,
        'incoming_folders': incoming.get('folders', []),
        'new_wiki': new_wiki,
        'new_maps': new_maps,
        'identical_maps': identical_maps,
        'map_conflicts': map_conflicts,
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


def _extract_map_images(names, zf):
    """Copy the named map background image(s) out of the bundle into
    static/maps. Missing members are skipped. `names` is a list of bare
    filenames (see _map_image_names / _map_image_names_one).

    Only bare filenames are honoured; a member whose stored name somehow
    carries a path separator is ignored, so a crafted bundle can't write
    outside static/maps.
    """
    os.makedirs(storage.MAP_DIR, exist_ok=True)
    members = set(zf.namelist())
    for name in names:
        if '/' in name or '\\' in name:
            continue
        member = BUNDLE_MAPS + name
        if member in members:
            with zf.open(member) as src:
                dest = os.path.join(storage.MAP_DIR, name)
                with open(dest, 'wb') as out:
                    out.write(src.read())


def apply_import(zip_bytes, resolutions, map_resolutions=None):
    """Apply a merge. `resolutions` maps conflict id -> 'local' | 'imported'.

    - New handouts: added, with their files extracted.
    - Conflicts resolved 'imported': local replaced (old files removed, new
      files extracted). 'local' (or missing/unknown): left untouched.
    - Folders: any incoming folder whose id is not present locally is added,
      so folder memberships carried on imported handouts still resolve.
    - Wiki: incoming pages whose id is not present locally are added, scope
      and all. Existing ids are left alone (see analyze).
    - Maps: the table can hold several, so they merge by id exactly like
      handouts. A map whose id is new locally is ADDED (its background image
      extracted). A map whose id already exists but differs is a conflict,
      resolved via `map_resolutions` (id -> 'local' | 'imported'); 'imported'
      replaces the local map wholesale (its image extracted, the superseded
      local background removed if no longer referenced, its draft reset to the
      imported confirmed state), 'local' (or absent) leaves it untouched.
      Identical maps are skipped. `map_resolutions` defaults to empty (keep
      local on every conflict).
    - Settings are NOT merged: the theme is a local choice, and the bundle
      deliberately carries no credentials (see PRIVATE_SETTINGS).
    Returns a summary dict of counts.
    """
    map_resolutions = map_resolutions or {}
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
                if cur.get('back_texture'):
                    storage.remove_files([cur['back_texture']])
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

    # Interactive maps: merge by id, like handouts.
    #   * new id            -> add the map + extract its background image;
    #   * same id, differs  -> conflict, resolved via map_resolutions;
    #   * same id, identical-> skipped.
    # Importing a map REPLACES that id's local map wholesale (a map is a single
    # scene, not a field-by-field merge). confirm_seq is bumped past the local
    # one so player pages polling that map pick up the change, and the draft
    # (`pending`) is reset to the imported confirmed state so a stale local
    # draft can't shadow it.
    local_maps_by_id = {m['id']: m for m in db.get('maps', [])}
    maps_added = maps_replaced = maps_kept = 0
    for m in incoming.get('maps', []):
        if not _map_has_content(m):
            continue
        cur = local_maps_by_id.get(m['id'])
        if cur is None:
            # New map: extract its image(s) and append.
            _extract_map_images(_map_image_names_one(m), zf)
            db.setdefault('maps', []).append(m)
            local_maps_by_id[m['id']] = m
            maps_added += 1
        elif _map_signature(cur) == _map_signature(m):
            # Identical map: still make sure its image is on disk (fresh device
            # or a DB copied without static/maps), then leave it.
            for name in _map_image_names_one(cur):
                dest = os.path.join(storage.MAP_DIR, name)
                if not os.path.exists(dest):
                    _extract_map_images([name], zf)
            continue
        else:
            choice = map_resolutions.get(m['id'], 'local')
            if choice == 'imported':
                old_image = cur.get('map_image')
                _extract_map_images(_map_image_names_one(m), zf)
                m['confirm_seq'] = cur.get('confirm_seq', 0) + 1
                idx = db['maps'].index(cur)
                db['maps'][idx] = m
                local_maps_by_id[m['id']] = m
                # Reset this map's draft to its freshly-imported confirmed
                # state so a stale local draft doesn't shadow it.
                storage.discard_map_state(db, m['id'])
                # Drop the superseded background if nothing else references it.
                new_image = m.get('map_image')
                if old_image and old_image != new_image \
                        and old_image not in _map_image_names(db):
                    storage.remove_map_image(old_image)
                maps_replaced += 1
            else:
                maps_kept += 1

    storage.save_db(db)
    return {'added': added, 'replaced': replaced, 'kept_local': kept,
            'wiki_added': wiki_added, 'restored_files': restored_files,
            'maps_added': maps_added, 'maps_replaced': maps_replaced,
            'maps_kept_local': maps_kept}
