"""Master-facing routes: dashboard, upload, edit, publish toggle, delete.

Every route here is behind auth.master_required. The one exception is the
unlock pair below, which by definition must be reachable while locked.
"""

import os
import uuid

from flask import (Blueprint, render_template, request, redirect,
                   url_for, abort, Response, jsonify)

from . import auth
from . import storage
from . import organize
from . import transfer
from . import pdfs
from . import theming

bp = Blueprint('master', __name__)

# Where uploaded import bundles are staged between the review + apply steps.
IMPORT_TMP_DIR = os.path.join(storage.BASE_DIR, 'data', 'import_tmp')

# Grouping modes the master can pick for its two lists.
MASTER_MODES = ('recent', 'folder', 'tag', 'session', 'format')


# --------------------------------------------------------------------------
# Unlocking. These two are deliberately NOT guarded: the unlock page is how a
# locked Master gets in, and locking is safe to call in any state.
# --------------------------------------------------------------------------

@bp.route('/unlock', methods=['GET', 'POST'])
def unlock():
    """Ask for the master passphrase and unlock this browser's session.

    `next` is carried through the form so the Master returns to whatever they
    were aiming at. It is validated as a relative path before use: an
    attacker-supplied absolute URL here would turn the login into an open
    redirect.
    """
    db = storage.load_db()
    target = request.values.get('next', '')
    # Only same-site, root-relative paths. '//host' is protocol-relative and
    # would leave the site, so it is rejected along with anything absolute.
    if not target.startswith('/') or target.startswith('//'):
        target = url_for('master.dm_panel')

    if request.method == 'GET':
        return render_template('master/unlock.html',
                               configured=auth.is_configured(db),
                               next=target)

    if auth.check_passphrase(db, request.form.get('passphrase')):
        auth.unlock()
        return redirect(target)

    return render_template('master/unlock.html',
                           configured=auth.is_configured(db),
                           next=target,
                           error=True), 403


@bp.route('/lock', methods=['POST'])
def lock():
    """Drop master rights (e.g. before handing the laptop round the table)."""
    auth.lock()
    return redirect(url_for('player.home'))


@bp.route('/settings/passphrase', methods=['POST'])
@auth.master_required
def set_passphrase():
    """Set or change the master passphrase.

    Changing it requires knowing the current one; setting it for the first
    time does not, since there is nothing to know yet and the first-run state
    is already open by design (see auth.is_master).
    """
    db = storage.load_db()
    if auth.is_configured(db):
        if not auth.check_passphrase(db, request.form.get('current')):
            abort(403, 'The current passphrase is wrong.')

    if not auth.set_passphrase(db, request.form.get('passphrase')):
        abort(400, 'A passphrase is required.')
    storage.save_db(db)
    # The session that just set the passphrase is, definitionally, the Master.
    auth.unlock()
    return redirect(url_for('master.dm_panel'))


# --------------------------------------------------------------------------
# Dashboard + library management. All guarded.
# --------------------------------------------------------------------------

@bp.route('/dm-panel', strict_slashes=False)
@auth.master_required
def dm_panel():
    db = storage.load_db()
    folders = storage.all_folders(db)

    mode = request.args.get('by', 'recent')
    if mode not in MASTER_MODES:
        mode = 'recent'

    # The hidden/public split is always kept; grouping happens *within* each.
    hidden = [h for h in db['handouts'] if not h.get('visible')]
    public = [h for h in db['handouts'] if h.get('visible')]

    return render_template('master/dashboard.html',
                           hidden_groups=organize.group_by_mode(
                               hidden, mode, folders),
                           public_groups=organize.group_by_mode(
                               public, mode, folders),
                           hidden_count=len(hidden),
                           public_count=len(public),
                           mode=mode,
                           categories=storage.all_categories(db),
                           tags=storage.all_tags(db),
                           folders=folders,
                           view_types=storage.VIEW_TYPES,
                           default_view_type=storage.DEFAULT_VIEW_TYPE,
                           # The theme picker moved to master.appearance, so
                           # the dashboard no longer needs the theme table.
                           passphrase_set=auth.is_configured(db))


@bp.route('/dm-panel/create')
@auth.master_required
def create_page():
    """The 'Create' page: the upload form + folder management on their own page.

    These used to live in the dashboard's right column, where they crowded out
    the handout lists and, as the Master noted, don't belong beside the lists
    they're used far less often than. Same data the dashboard passed to the
    form, just rendered on a dedicated page reached from the menu / a Create
    button. The form still POSTs to upload_handout as before.
    """
    db = storage.load_db()
    folders = storage.all_folders(db)
    return render_template('master/create.html',
                           categories=storage.all_categories(db),
                           tags=storage.all_tags(db),
                           folders=folders,
                           view_types=storage.VIEW_TYPES,
                           default_view_type=storage.DEFAULT_VIEW_TYPE,
                           passphrase_set=auth.is_configured(db))


@bp.route('/upload', methods=['POST'])
@auth.master_required
def upload_handout():
    title = request.form.get('title', '').strip()
    if not title:
        abort(400, 'A title is required.')

    files = [f for f in request.files.getlist('files') if f and f.filename]
    if not files:
        abort(400, 'No file selected.')
    for f in files:
        if not storage.allowed_file(f.filename):
            abort(400, f'File type not allowed: {f.filename}')

    handout_id = storage.new_handout_id()
    # Record the ORIGINAL format now, from the uploaded files, BEFORE the PDF
    # expansion below turns a .pdf into .png pages. This is what the master's
    # "Group by Format" view sorts on, so a PDF handout stays 'pdf' even though
    # its stored pages become images.
    source_format = storage.source_format_from_uploads(files)
    # Per-file descriptions arrive as new_desc, one input per file in order.
    descriptions = request.form.getlist('new_desc')
    stored_files = storage.save_files(files, handout_id,
                                      descriptions=descriptions)

    view_type = storage.clean_view_type(request.form.get('view_type'))
    # Book viewer: an unticked "hard covers" box makes the cover and back cover
    # flip like ordinary pages instead of stiff boards. A checkbox that is off
    # sends no field at all, so absence means False here. Default-on lives in
    # the create form's `checked` attribute and in _normalize for old records.
    hard_covers = bool(request.form.get('hard_covers'))

    # Optional back cover (only meaningful for the Book viewer).
    back_cover = None
    back_file = request.files.get('back_cover')
    if back_file and back_file.filename:
        if not storage.allowed_file(back_file.filename):
            abort(400, f'File type not allowed: {back_file.filename}')
        back_cover = storage.save_back_cover(back_file, handout_id)

    # Both viewers show images, never a live PDF. Expand every PDF into one
    # image per page now, for Book AND Carousel alike -- the only difference
    # left between the two is how the player steps through those images
    # (page-curl vs arrows). A back cover is expanded the same way and, being a
    # single page, keeps its first rendered page.
    stored_files, dropped = pdfs.expand_pdfs(stored_files, handout_id)
    storage.remove_files(dropped)
    if back_cover and pdfs.is_pdf(back_cover):
        pages, dropped = pdfs.expand_pdfs([back_cover], handout_id)
        # A back cover is a single page: keep the first rendered page.
        back_cover = pages[0]
        storage.remove_files(dropped)

    # Every remaining PDF gets a first-page thumbnail for its card preview.
    pdfs.attach_thumbs(stored_files)
    if back_cover:
        pdfs.attach_thumbs([back_cover])

    db = storage.load_db()
    if pdfs.backfill_thumbs(db):
        storage.save_db(db)
    # Only keep folder ids that actually exist (guards against stale form data).
    folder_ids = storage.valid_folder_ids(
        db, request.form.getlist('folders'))

    # "Forge & POP" both publishes and pops in one click. Uploads are hidden by
    # default, so this is the one place where a new handout can arrive already
    # visible -- and it only does so on an explicit, separately-labelled button.
    pop_now = bool(request.form.get('pop'))

    db['handouts'].append({
        'id': handout_id,
        'title': title,
        'description': request.form.get('description', '').strip(),
        'files': stored_files,
        'visible': pop_now,
        'category': request.form.get('category', '').strip(),
        'tags': storage.parse_tags(request.form.get('tags')),
        'folders': folder_ids,
        'view_type': view_type,
        'hard_covers': hard_covers,
        'source_format': source_format,
        'back_cover': back_cover,
        'session_number': storage.parse_session_number(
            request.form.get('session_number')),
        'session_title': request.form.get('session_title', '').strip(),
        'found_location': request.form.get('found_location', '').strip(),
        'found_date': request.form.get('found_date', '').strip(),
        'created_at': storage.now_iso(),
    })

    if pop_now:
        storage.set_pop(db, handout_id)

    storage.save_db(db)
    return redirect(url_for('master.dm_panel'))


@bp.route('/edit/<handout_id>', methods=['GET', 'POST'])
@auth.master_required
def edit_handout(handout_id):
    db = storage.load_db()
    handout = storage.find(db, handout_id)
    if handout is None:
        abort(404, 'Handout not found.')

    if request.method == 'GET':
        return render_template('master/edit.html',
                               handout=handout,
                               categories=storage.all_categories(db),
                               tags=storage.all_tags(db),
                               folders=storage.all_folders(db),
                               view_types=storage.VIEW_TYPES)

    # --- POST: metadata ---
    handout['title'] = request.form.get('title', '').strip() or handout['title']
    handout['description'] = request.form.get('description', '').strip()
    handout['category'] = request.form.get('category', '').strip()
    handout['tags'] = storage.parse_tags(request.form.get('tags'))
    handout['view_type'] = storage.clean_view_type(
        request.form.get('view_type'))
    # Book viewer: hard vs soft covers (see upload_handout). Off = no field, so
    # absence means the Master unticked it. `source_format` is deliberately NOT
    # touched here: it records what the handout ORIGINALLY was, so adding or
    # swapping files in an edit doesn't relabel a PDF handout as PNG.
    handout['hard_covers'] = bool(request.form.get('hard_covers'))
    handout['folders'] = storage.valid_folder_ids(
        db, request.form.getlist('folders'))
    handout['session_title'] = request.form.get('session_title', '').strip()
    handout['found_location'] = request.form.get('found_location', '').strip()
    handout['found_date'] = request.form.get('found_date', '').strip()
    handout['session_number'] = storage.parse_session_number(
        request.form.get('session_number'))

    # --- Files: removals, per-file descriptions, reordering, additions ---
    remove = set(request.form.getlist('remove'))
    kept = [f for f in handout.get('files', []) if f['filename'] not in remove]

    # Update descriptions of kept files from desc_<filename> inputs.
    for f in kept:
        field = f'desc_{f["filename"]}'
        if field in request.form:
            f['description'] = request.form.get(field, '').strip()

    # Reorder kept files to match the `order` list (list of filenames from the
    # drag-and-drop widget). Unknown/removed names are ignored; any kept file
    # missing from the order (defensive) is appended in its original spot.
    order = request.form.getlist('order')
    if order:
        pos = {name: i for i, name in enumerate(order)}
        kept.sort(key=lambda f: pos.get(f['filename'], len(pos)))

    new_files = [f for f in request.files.getlist('files') if f and f.filename]
    for f in new_files:
        if not storage.allowed_file(f.filename):
            abort(400, f'File type not allowed: {f.filename}')

    if not kept and not new_files:
        abort(400, 'A handout must have at least one file.')

    storage.remove_files(f for f in handout.get('files', [])
                         if f['filename'] in remove)

    if new_files:
        stamp = f'{storage.now_stamp()}_'
        new_descs = request.form.getlist('new_desc')
        # New files are appended after the (reordered) kept ones.
        kept.extend(storage.save_files(new_files, handout_id, prefix=stamp,
                                       descriptions=new_descs))

    handout['files'] = kept

    # --- Back cover: optional single file, remove/replace ---
    if request.form.get('remove_back_cover') and handout.get('back_cover'):
        storage.remove_files([handout['back_cover']])
        handout['back_cover'] = None
    back_file = request.files.get('back_cover')
    if back_file and back_file.filename:
        if not storage.allowed_file(back_file.filename):
            abort(400, f'File type not allowed: {back_file.filename}')
        # Replace any existing back cover.
        if handout.get('back_cover'):
            storage.remove_files([handout['back_cover']])
        handout['back_cover'] = storage.save_back_cover(back_file, handout_id)

    # --- PDFs: both viewers show images, so convert any PDF now. This also
    # covers a handout that still had PDF pages from before the carousel
    # rendered images, and the Master switching an existing handout's viewer. ---
    handout['files'], dropped = pdfs.expand_pdfs(
        handout['files'], handout_id)
    storage.remove_files(dropped)
    if handout.get('back_cover') and pdfs.is_pdf(handout['back_cover']):
        pages, dropped = pdfs.expand_pdfs(
            [handout['back_cover']], handout_id)
        handout['back_cover'] = pages[0]
        storage.remove_files(dropped)

    # Any PDF still around (Carousel) gets a first-page thumbnail.
    pdfs.attach_thumbs(handout['files'])
    if handout.get('back_cover'):
        pdfs.attach_thumbs([handout['back_cover']])

    # Drop legacy single-file keys now that files: [...] is authoritative.
    handout.pop('filename', None)
    handout.pop('reader', None)
    storage.save_db(db)
    return redirect(url_for('master.dm_panel'))


@bp.route('/toggle/<handout_id>', methods=['POST'])
@auth.master_required
def toggle_visibility(handout_id):
    db = storage.load_db()
    handout = storage.find(db, handout_id)
    if handout is None:
        abort(404, 'Handout not found.')
    handout['visible'] = not handout.get('visible', False)

    # Unpublishing the handout that is currently popped must also retire the
    # POP. The player endpoint re-checks `visible` and would refuse to serve
    # it anyway, but leaving a pointer to a hidden handout lying around in the
    # DB invites the next reader of this code to trust it.
    if not handout['visible'] and \
            storage.pop_state(db).get('handout_id') == handout_id:
        storage.clear_pop(db)

    storage.save_db(db)
    return redirect(url_for('master.dm_panel'))


@bp.route('/pop/<handout_id>', methods=['POST'])
@auth.master_required
def pop_handout(handout_id):
    """Force an already-public handout onto every player's screen.

    Publishing and popping are kept as separate routes even though the
    dashboard can fire both at once (see `publish` below): popping is not a
    property of publishing, it is a thing the Master does repeatedly to a
    handout that is already public -- when the party finally reaches the room
    the map belongs to, and again ten minutes later when nobody looked.

    A hidden handout cannot be popped. Popping is a reveal, and revealing via
    a route whose name says 'pop' would be a surprising way to publish.
    """
    db = storage.load_db()
    handout = storage.find(db, handout_id)
    if handout is None:
        abort(404, 'Handout not found.')
    if not handout.get('visible'):
        abort(400, 'Publish this handout before popping it to the players.')

    storage.set_pop(db, handout_id)
    storage.save_db(db)
    return redirect(url_for('master.dm_panel'))


@bp.route('/publish/<handout_id>', methods=['POST'])
@auth.master_required
def publish_handout(handout_id):
    """Publish a hidden handout, optionally popping it in the same click.

    Distinct from `toggle_visibility`, which flips whichever way the handout
    is currently facing. This one only ever publishes, because "publish and
    pop" must not silently mean "unpublish and pop" if the Master double-
    clicks or the page was stale.
    """
    db = storage.load_db()
    handout = storage.find(db, handout_id)
    if handout is None:
        abort(404, 'Handout not found.')

    handout['visible'] = True
    # The POP is recorded only after `visible` is set, so the state the player
    # endpoint reads is never "popped but still hidden".
    if request.form.get('pop'):
        storage.set_pop(db, handout_id)

    storage.save_db(db)
    return redirect(url_for('master.dm_panel'))


@bp.route('/delete/<handout_id>', methods=['POST'])
@auth.master_required
def delete_handout(handout_id):
    db = storage.load_db()
    handout = storage.find(db, handout_id)
    if handout is None:
        abort(404, 'Handout not found.')
    storage.remove_files(handout.get('files', []))
    if handout.get('back_cover'):
        storage.remove_files([handout['back_cover']])
    db['handouts'].remove(handout)

    # Never leave the POP pointing at a handout that no longer exists.
    if storage.pop_state(db).get('handout_id') == handout_id:
        storage.clear_pop(db)

    storage.save_db(db)
    return redirect(url_for('master.dm_panel'))


# --------------------------------------------------------------------------
# Folder management (create / rename / delete). Deleting a folder detaches
# it from handouts but never removes the handouts themselves.
# --------------------------------------------------------------------------

@bp.route('/folders/create', methods=['POST'])
@auth.master_required
def create_folder():
    db = storage.load_db()
    storage.create_folder(db, request.form.get('name', ''))
    storage.save_db(db)
    return redirect(url_for('master.dm_panel'))


@bp.route('/folders/rename/<folder_id>', methods=['POST'])
@auth.master_required
def rename_folder(folder_id):
    db = storage.load_db()
    storage.rename_folder(db, folder_id, request.form.get('name', ''))
    storage.save_db(db)
    return redirect(url_for('master.dm_panel'))


@bp.route('/folders/delete/<folder_id>', methods=['POST'])
@auth.master_required
def delete_folder(folder_id):
    db = storage.load_db()
    storage.delete_folder(db, folder_id)
    storage.save_db(db)
    return redirect(url_for('master.dm_panel'))


# --------------------------------------------------------------------------
# Interactive map (master side).
#
# The Master's page is the control surface: it reveals hexes and drags the
# marker. The write endpoint that backs it is the ONLY way map state changes,
# and it is guarded by master_required exactly like every other mutation here.
# Players get a read-only view + a read-only polling endpoint, both defined in
# routes_player.py; they can never POST here.
# --------------------------------------------------------------------------

@bp.route('/dm-panel/map')
@auth.master_required
def map_control():
    """The Master's interactive-map control page.

    Kept under /dm-panel/ so it sits with the other master pages and inherits
    the same guard. The current state is handed to the template for the first
    paint so the page isn't blank until the first poll returns.
    """
    db = storage.load_db()
    return render_template('master/map.html',
                           map_state=storage.get_map_state(db))


@bp.route('/master/api/map/state', methods=['GET', 'POST'])
@auth.master_required
def map_state_api():
    """Read or write the shared map state (Master only).

    GET returns the current state; POST merges a partial JSON body and saves.
    Both live behind master_required because this is the write path -- the
    marker moves and hexes are revealed from here. Players read the same state
    through the public, GET-only mirror in routes_player.py, which never
    accepts a write.

    Note the URL: /master/api/map/state, NOT /api/map/state. The player
    blueprint owns the bare /api/map/state for its read-only poll, and both
    blueprints are mounted at the root, so a shared path would collide at
    registration. The /master/ prefix keeps the two rules distinct and makes
    the write path self-documenting.

    POST accepts any subset of the state's keys (a marker nudge need not resend
    the revealed hexes); storage.update_map_state does the type-coercion and
    key-whitelisting, so a malformed or padded body can't corrupt the DB.
    """
    db = storage.load_db()

    if request.method == 'GET':
        return jsonify(storage.get_map_state(db))

    # POST. silent=True so a missing/!json body yields None (-> {}), which
    # update_map_state treats as "change nothing" rather than raising.
    payload = request.get_json(silent=True)
    state = storage.update_map_state(db, payload)
    storage.save_db(db)
    return jsonify(state)

@bp.route('/dm-panel/map/upload', methods=['POST'])
@auth.master_required
def map_upload():
    """Upload (or clear) the map background image.

    Kept as its own form-POST route rather than folded into the JSON write
    endpoint because it carries a file, not JSON. On success it saves the image
    to static/maps, points map_state at it, deletes the previous map so old
    backgrounds don't pile up, and returns to the map page.

    A submit with no file but the `clear` flag set removes the current map and
    falls back to the placeholder.
    """
    db = storage.load_db()
    state = storage.get_map_state(db)
    old = state.get('map_image')

    if request.form.get('clear'):
        storage.remove_map_image(old)
        storage.set_map_image(db, None)
        storage.save_db(db)
        return redirect(url_for('master.map_control'))

    upload = request.files.get('map_image')
    if not upload or not upload.filename:
        abort(400, 'No file selected.')
    if not storage.allowed_map_file(upload.filename):
        abort(400, f'File type not allowed: {upload.filename}')

    name = storage.save_map_image(upload)
    if not name:
        abort(400, 'Could not save the map image.')

    storage.set_map_image(db, name)
    storage.save_db(db)
    # Remove the previous background only after the new one is safely stored.
    if old and old != name:
        storage.remove_map_image(old)
    return redirect(url_for('master.map_control'))

@bp.route('/master/api/map/confirm', methods=['POST'])
@auth.master_required
def map_confirm():
    """Promote the Master's draft to the live state players read.

    The map page POSTs its latest draft to /master/api/map/state (which lands
    in `pending`), then calls this to publish it. Splitting write-draft from
    confirm is the whole point: nothing reaches the table until the Master says
    so. Returns the full state so the page can refresh its 'pending vs live'
    indicator from the server's own view.
    """
    db = storage.load_db()
    state = storage.confirm_map_state(db)
    storage.save_db(db)
    return jsonify(state)


@bp.route('/master/api/map/discard', methods=['POST'])
@auth.master_required
def map_discard():
    """Throw the Master's draft away, resetting it to the live state."""
    db = storage.load_db()
    state = storage.discard_map_state(db)
    storage.save_db(db)
    return jsonify(state)


@bp.route('/master/api/map/focus', methods=['POST'])
@auth.master_required
def map_focus():
    """Broadcast the Master's current camera to every player screen.

    The Master frames a spot on their own map (a centre point + a zoom level)
    and fires this; players poll the shared state, see focus.seq change, and
    animate their view to match. Deliberately NOT staged: a focus is a live
    "everyone look here" directive, like a POP, not a draft edit that waits for
    a confirm.

    Body is JSON: {x, y, scale} where x/y are the focus point as percent of the
    image and scale is the zoom. storage.set_map_focus clamps and bumps the seq;
    a malformed body falls back to sane centre/zoom rather than raising.
    """
    db = storage.load_db()
    payload = request.get_json(silent=True) or {}
    focus = storage.set_map_focus(
        db, payload.get('x'), payload.get('y'), payload.get('scale'))
    storage.save_db(db)
    return jsonify(focus)

# --------------------------------------------------------------------------
# Settings pages. These used to be panels crowding the dashboard; each is now
# its own page reached from the menu, so the dashboard can be just the lists
# and the upload form.
# --------------------------------------------------------------------------

@bp.route('/dm-panel/appearance')
@auth.master_required
def appearance():
    """Theme + interface language, moved off the dashboard."""
    db = storage.load_db()
    return render_template('master/appearance.html',
                           themes=theming.theme_list(),
                           theme_vars=theming.THEMES,
                           current_theme=storage.get_theme(db))


@bp.route('/dm-panel/transfer')
@auth.master_required
def transfer_page():
    """Export / import entry point, moved off the dashboard.

    Named `transfer_page` rather than `transfer` so it cannot shadow the
    `transfer` module imported at the top of this file.
    """
    return render_template('master/transfer.html')


@bp.route('/dm-panel/security')
@auth.master_required
def security():
    """Where the Master sets or changes the passphrase."""
    db = storage.load_db()
    return render_template('master/security.html',
                           passphrase_set=auth.is_configured(db))


# --------------------------------------------------------------------------
# Appearance. The theme is table-wide (players see it too), so it lives in
# the DB rather than in a cookie like the per-user language.
# --------------------------------------------------------------------------

@bp.route('/settings/theme', methods=['POST'])
@auth.master_required
def set_theme():
    db = storage.load_db()
    storage.set_theme(db, request.form.get('theme'))
    storage.save_db(db)
    # Back to the appearance page, which is where the form now lives, so the
    # Master can see the new theme applied without navigating.
    return redirect(url_for('master.appearance'))


# --------------------------------------------------------------------------
# Export / import (move the whole library between computers).
# Export is a plain download. Import is a two-step flow: upload -> review
# conflicts -> apply, so nothing is overwritten without the Master's say-so.
# --------------------------------------------------------------------------

@bp.route('/export')
@auth.master_required
def export_library():
    """Download the whole library as a .zip.

    export_bytes() returns the bundle AND a list of files it could not include
    because they were referenced by the database but missing on disk. If that
    list is non-empty we do NOT just stream the (incomplete) zip: a silently
    partial backup is exactly the bug that leaves 'random' broken images after
    an import. Instead we show a warning page listing what is missing, with a
    'download anyway' button (?force=1) for when the Master knowingly accepts a
    partial backup.
    """
    data, missing = transfer.export_bytes()

    if missing and not request.args.get('force'):
        return render_template('master/export_warning.html', missing=missing)

    return Response(
        data,
        mimetype='application/zip',
        headers={'Content-Disposition':
                 'attachment; filename=handouts-export.zip'})


@bp.route('/import', methods=['GET', 'POST'])
@auth.master_required
def import_library():
    if request.method == 'GET':
        return render_template('master/import.html')

    upload = request.files.get('bundle')
    if not upload or not upload.filename:
        abort(400, 'No file selected.')
    zip_bytes = upload.read()

    try:
        report = transfer.analyze(zip_bytes)
    except ValueError as exc:
        return render_template('master/import.html', error=str(exc)), 400

    # Stage the bundle so the apply step can read it back by token.
    os.makedirs(IMPORT_TMP_DIR, exist_ok=True)
    token = uuid.uuid4().hex
    with open(os.path.join(IMPORT_TMP_DIR, token + '.zip'), 'wb') as f:
        f.write(zip_bytes)

    return render_template('master/import_review.html',
                           token=token,
                           new=report['new'],
                           identical=report['identical'],
                           conflicts=report['conflicts'],
                           new_wiki=report['new_wiki'],
                           map_report=report['map'])


@bp.route('/import/apply', methods=['POST'])
@auth.master_required
def import_apply():
    token = request.form.get('token', '')
    # Guard the token so it can only name a file inside the staging dir.
    if not token or not token.isalnum():
        abort(400, 'Invalid import token.')
    staged = os.path.join(IMPORT_TMP_DIR, token + '.zip')
    if not os.path.exists(staged):
        abort(400, 'This import session has expired. Please upload again.')

    with open(staged, 'rb') as f:
        zip_bytes = f.read()

    # Collect per-conflict choices: resolve_<id> = 'local' | 'imported'.
    resolutions = {}
    for key, value in request.form.items():
        if key.startswith('resolve_'):
            resolutions[key[len('resolve_'):]] = value

    # The map is a single global object, resolved by one radio: map_action =
    # 'imported' means replace the local map with the bundle's; anything else
    # (incl. absent) keeps the local map.
    import_map = request.form.get('map_action') == 'imported'

    try:
        summary = transfer.apply_import(zip_bytes, resolutions,
                                        import_map=import_map)
    except ValueError as exc:
        abort(400, str(exc))
    finally:
        try:
            os.remove(staged)
        except OSError:
            pass

    return render_template('master/import_done.html', summary=summary)