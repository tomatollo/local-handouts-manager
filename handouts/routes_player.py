"""Player-facing routes: the public hub of revealed handouts."""

import os

from flask import (Blueprint, render_template, request, redirect, url_for,
                   jsonify, send_file, abort, Response)

from . import storage
from . import organize
from . import pdfs
from . import mapmask

bp = Blueprint('player', __name__)

# Organization modes offered in the player drawer.
MODES = ('folder', 'session', 'tag', 'recent')


@bp.route('/')
def home():
    db = storage.load_db()

    # Older carousel handouts stored PDFs as PDFs (shown in an iframe). Both
    # viewers now render images only, so expand any lingering PDF pages into
    # page images once, here, and persist if anything changed. Non-destructive:
    # the source PDFs stay on disk (see pdfs.backfill_carousel_pdfs).
    changed = pdfs.backfill_carousel_pdfs(db)
    # Older PDFs predate thumbnails; render any that are missing so cards show
    # a real preview instead of the grey placeholder.
    if pdfs.backfill_thumbs(db):
        changed = True
    if changed:
        storage.save_db(db)

    visible = [h for h in db['handouts'] if h.get('visible')]
    folders = storage.all_folders(db)

    # State lives in the querystring so views are shareable + reloadable.
    query = request.args.get('q', '').strip()
    mode = request.args.get('by', 'folder')
    if mode not in MODES:
        mode = 'folder'

    # Search first, then group/sort what survived.
    matched = organize.search(visible, query)

    # Folder mode shows "collection" cards (a 2x2 cover mosaic per folder) so
    # folders read as objects, not sections. But an active search cuts across
    # folders, so we fall back to a flat result grid while searching.
    folder_cards = None
    if mode == 'folder' and not query:
        folder_cards = organize.folder_cards(matched, folders)
        groups = []
    elif mode == 'session':
        groups = organize.group_by_session(matched)
    elif mode == 'tag':
        groups = organize.group_by_tag(matched)
    elif mode == 'recent' or (mode == 'folder' and query):
        # A single flat group, newest first.
        groups = [{'label': '', 'key': None,
                   'handouts': organize.sort_chronological(matched)}]
    else:  # folder, no query handled above; safety fallback
        groups = [{'label': '', 'key': None,
                   'handouts': organize.sort_chronological(matched)}]

    return render_template('player/hub.html',
                           groups=groups,
                           folder_cards=folder_cards,
                           mode=mode,
                           query=query,
                           folders=folders,
                           tags=storage.all_tags(db),
                           total=len(visible),
                           shown=len(matched))


@bp.route('/api/pop')
def pop_status():
    """What the players' browsers poll to learn about a POP.

    Deliberately the smallest useful payload. It answers two questions -- "is
    there a POP newer than the one I last showed?" and "what should I render?"
    -- in a single response, so a client that is behind needs one request, not
    a poll followed by a fetch.

    The handout is inlined rather than referenced by id because the payload is
    exactly what the lightbox already knows how to open (the same shape the
    hub's data-* attributes carry), which keeps the client free of a second
    code path for building a view.

    Three guards matter here, and all are server-side because this endpoint is
    public by definition -- players are never authenticated:

      * A POP older than storage.POP_TTL_SECONDS is not served at all. A POP is
        a moment, not a state: without this, every player joining or reloading
        later would be ambushed by a reveal the table finished with long ago.
        Expiry is computed per request rather than written back to the DB, so
        it needs no cleanup job and a GET stays a GET.
      * `visible` is re-checked at read time. A POP is a pointer, and the
        handout it points at may have been unpublished since. Trusting the
        stored pop alone would turn this route into a way to read hidden
        handouts by polling.
      * A missing handout (deleted) collapses to the same empty answer rather
        than a 404, because to a poller "nothing to show" is not an error.
    """
    db = storage.load_db()
    pop = storage.pop_state(db)

    payload = {'seq': pop.get('seq', 0), 'handout': None, 'expires_in': 0}

    # Expired, never fired, or a timestamp we can't trust: nothing to show.
    # `seq` still rides along so a client that missed the live window records
    # it as seen and doesn't re-ask about it.
    if not storage.pop_is_live(pop):
        return jsonify(payload)

    handout = storage.find(db, pop.get('handout_id'))
    # Re-checking `visible` is what stops a stale POP from leaking a handout
    # the Master has since pulled back.
    if handout is None or not handout.get('visible'):
        return jsonify(payload)

    # Seconds of life left. The client uses this to refuse a POP that would
    # expire between this response and the moment it renders -- on a slow phone
    # those are not the same instant.
    age = storage.pop_age_seconds(pop) or 0
    payload['expires_in'] = max(0, int(storage.POP_TTL_SECONDS - age))

    payload['handout'] = {
        'id': handout['id'],
        'title': handout.get('title', ''),
        'description': handout.get('description', ''),
        'found_location': handout.get('found_location', ''),
        'found_date': handout.get('found_date', ''),
        'view_type': handout.get('view_type', storage.DEFAULT_VIEW_TYPE),
        'files': handout.get('files', []),
        'back_cover': handout.get('back_cover'),
    }
    return jsonify(payload)


@bp.route('/map')
def map_view():
    """The players' read-only interactive map.

    The page paints the current state once server-side, then polls
    /api/map/state (below) to stay in sync as the Master reveals hexes and
    moves the marker. There is no write path here: players observe, they do
    not edit.
    """
    db = storage.load_db()
    return render_template('player/map.html',
                           map_state=storage.get_map_state(db))


@bp.route('/api/map/state')
def map_state():
    """Public, read-only mirror of the shared map state.

    GET only -- players poll this to follow the Master. The matching write
    endpoint lives in routes_master.py behind master_required; keeping the two
    in separate blueprints is what makes "players can read but never write"
    true by construction rather than by an if-branch that could be forgotten.
    """
    db = storage.load_db()
    return jsonify(storage.get_map_state(db))


@bp.route('/api/map/reveal.png')
def map_reveal():
    """The revealed-only map composite: the anti-spoiler payload.

    This is the ONLY map imagery a player ever receives. mapmask composites a
    PNG the size of the map in which only CONFIRMED-revealed hexes carry the
    real pixels and everything else is transparent, so un-revealed terrain is
    never sent -- not hidden client-side, simply absent from the bytes. The raw
    background in static/maps is never linked from the player page.

    Served with a confirm_seq-based ETag and no-cache-revalidate so a browser
    reuses the composite between polls but always re-fetches after the Master
    reveals more (which bumps confirm_seq). A map with no image, or one whose
    file is missing, yields 404 -- the template then shows its fog placeholder.
    """
    db = storage.load_db()
    state = storage.get_map_state(db)
    if not state.get('map_image'):
        abort(404)

    # ETag ties the cached image to the reveal generation. If the client's
    # If-None-Match already matches, skip the (potentially large) transfer.
    etag = f'reveal-{state.get("confirm_seq", 0)}'
    if request.headers.get('If-None-Match') == etag:
        resp = Response(status=304)
        resp.headers['ETag'] = etag
        resp.headers['Cache-Control'] = 'no-cache'
        return resp

    path = mapmask.build_composite(db)
    if not path or not os.path.exists(path):
        abort(404)

    resp = send_file(path, mimetype='image/png', conditional=False)
    resp.headers['ETag'] = etag
    # no-cache (not no-store): the browser may keep it, but must revalidate,
    # so a new reveal is picked up immediately via the ETag check above.
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@bp.route('/folder/<folder_id>')
def folder(folder_id):
    """A single folder's page: the handouts it contains, as a grid."""
    db = storage.load_db()
    visible = [h for h in db['handouts'] if h.get('visible')]
    folders = storage.all_folders(db)

    folder = organize.resolve_folder(folders, folder_id)
    if folder is None:
        # Unknown/deleted folder: send the player back to the collections view.
        return redirect(url_for('player.home', by='folder'))

    items = organize.handouts_in_folder(visible, folders, folder_id)
    return render_template('player/folder.html',
                           folder=folder,
                           handouts=items,
                           folders=folders,
                           tags=storage.all_tags(db))