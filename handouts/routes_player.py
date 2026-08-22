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

    # One-time legacy backfills, gated on schema. On a library already migrated
    # and saved (stamped current), neither of these ever finds anything to do,
    # yet each still walks every handout and stats every PDF thumb on disk --
    # on the busiest page in the app, every load. So we run them ONLY until the
    # DB is stamped current, after which they are skipped entirely. New PDF
    # uploads are converted on the master upload/edit path, not here, so
    # skipping these on a current DB cannot leave a freshly uploaded PDF
    # unconverted -- these only ever recovered handouts saved before the
    # image-only viewers and thumbnails existed.
    if not storage.is_current_schema(db):
        # Older carousel handouts stored PDFs as PDFs (shown in an iframe).
        # Both viewers now render images only, so expand any lingering PDF
        # pages into page images once, here, and persist if anything changed.
        # Non-destructive: the source PDFs stay on disk (see
        # pdfs.backfill_carousel_pdfs).
        changed = pdfs.backfill_carousel_pdfs(db)
        # Older PDFs predate thumbnails; render any that are missing so cards
        # show a real preview instead of the grey placeholder.
        if pdfs.backfill_thumbs(db):
            changed = True
        # Persist regardless of `changed`: save_db stamps the schema current,
        # which is what lets every later hub load skip the two walks above.
        # (Even a no-op pass should record "nothing left to migrate" so it is
        # not repeated forever.)
        storage.save_db(db)

    visible = [h for h in db['handouts'] if h.get('visible')]
    # The full folder list drives grouping/orphan resolution (it needs every
    # real folder id to tell a true orphan from a member of a folder that
    # happens to hold nothing visible). The drawer, however, should only list
    # folders that actually contain something a player can open -- see
    # `drawer_folders` below.
    folders = storage.all_folders(db)
    drawer_folders = storage.non_empty_folders(db, only_visible=True)

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
                           folders=drawer_folders,
                           tags=storage.all_tags(db, only_visible=True),
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

    payload['handout'] = storage.player_payload(handout)
    return jsonify(payload)


@bp.route('/api/reveal-secret', methods=['POST'])
def reveal_secret():
    """Open a handout hidden behind a password typed into the viewer.

    The player types a password into any open handout's info panel; this checks
    it against that handout's secret_password and, on a match, returns the
    linked handout as a ready-to-open payload (the same shape as /api/pop, so
    the lightbox opens it through exactly one code path).

    Public by necessity -- players are never authenticated -- so the guards
    live here, server-side:

      * The password is checked against the SOURCE handout only. A wrong or
        empty password yields the same {handout: null} as a source with no
        secret at all, so the endpoint never tells a guesser whether a given
        handout even has a secret to find.
      * The source handout must itself be visible: a password box is only ever
        shown on a revealed handout, and honouring it on a hidden one would
        turn this into a way to probe unpublished handouts.
      * The TARGET is returned even if hidden -- typing the password IS its
        reveal (see storage.reveal_secret) -- but only ever reachable through a
        correct password on a visible source, never enumerable on its own.
    """
    db = storage.load_db()
    payload = request.get_json(silent=True) or {}
    source_id = payload.get('handout_id')
    password = payload.get('password')

    source = storage.find(db, source_id)
    # Fail closed and identically for "no such handout", "hidden handout" and
    # "wrong password": the response must not distinguish these cases.
    if source is None or not source.get('visible'):
        return jsonify({'handout': None})

    revealed = storage.reveal_secret(db, source_id, password)
    return jsonify({'handout': revealed})


@bp.route('/maps', strict_slashes=False)
def map_index():
    """The players' list of maps to choose from.

    Every map is offered, including ones with no background image yet: those
    simply show the fog placeholder until the Master uploads a map. If exactly
    one map exists we skip the list and go straight to it, so the common
    single-map table never sees an extra click. If none exist at all, there is
    nothing to show -- the nav button that points here is itself hidden in that
    case (see the drawer/menu), so this is a defensive redirect back to the
    hub.
    """
    db = storage.load_db()
    maps = storage.all_maps(db)
    if not maps:
        return redirect(url_for('player.home'))
    if len(maps) == 1:
        return redirect(url_for('player.map_view', map_id=maps[0]['id']))
    return render_template('player/maps.html', maps=maps)


@bp.route('/map/<map_id>')
def map_view(map_id):
    """The players' read-only interactive map for one map.

    The page paints the current state once server-side, then polls
    /api/map/<id>/state (below) to stay in sync as the Master reveals hexes and
    moves the marker. There is no write path here: players observe, they do
    not edit. An unknown/deleted id sends them back to the map list.
    """
    db = storage.load_db()
    m = storage.get_map(db, map_id)
    if m is None:
        return redirect(url_for('player.map_index'))
    return render_template('player/map.html', map_state=m, map_id=map_id)


@bp.route('/api/map/<map_id>/state')
def map_state(map_id):
    """Public, read-only mirror of one map's shared state.

    GET only -- players poll this to follow the Master. The matching write
    endpoint lives in routes_master.py behind master_required; keeping the two
    in separate blueprints is what makes "players can read but never write"
    true by construction rather than by an if-branch that could be forgotten.
    An unknown id is a 404 (a deleted map, a stale tab).
    """
    db = storage.load_db()
    m = storage.get_map(db, map_id)
    if m is None:
        abort(404)
    return jsonify(m)


@bp.route('/api/map/<map_id>/reveal.png')
def map_reveal(map_id):
    """One map's revealed-only composite: the anti-spoiler payload.

    This is the ONLY map imagery a player ever receives. mapmask composites a
    PNG the size of the map in which only CONFIRMED-revealed hexes carry the
    real pixels and everything else is transparent, so un-revealed terrain is
    never sent -- not hidden client-side, simply absent from the bytes. The raw
    background in static/maps is never linked from the player page.

    Served with a confirm_seq-based ETag and no-cache-revalidate so a browser
    reuses the composite between polls but always re-fetches after the Master
    reveals more (which bumps confirm_seq). A map that doesn't exist, has no
    image, or whose file is missing yields 404 -- the template then shows its
    fog placeholder.
    """
    db = storage.load_db()
    state = storage.get_map(db, map_id)
    if state is None or not state.get('map_image'):
        abort(404)

    # ETag ties the cached image to this map's reveal generation. If the
    # client's If-None-Match already matches, skip the (potentially large)
    # transfer. Namespaced by map id so two maps never share an ETag.
    etag = f'reveal-{map_id}-{state.get("confirm_seq", 0)}'
    if request.headers.get('If-None-Match') == etag:
        resp = Response(status=304)
        resp.headers['ETag'] = etag
        resp.headers['Cache-Control'] = 'no-cache'
        return resp

    path = mapmask.build_composite(db, map_id)
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
    # Full list for resolving/looking up this folder; filtered list for the
    # browse drawer so it never advertises an empty folder.
    folders = storage.all_folders(db)
    drawer_folders = storage.non_empty_folders(db, only_visible=True)

    folder = organize.resolve_folder(folders, folder_id)
    if folder is None:
        # Unknown/deleted folder: send the player back to the collections view.
        return redirect(url_for('player.home', by='folder'))

    items = organize.handouts_in_folder(visible, folders, folder_id)
    return render_template('player/folder.html',
                           folder=folder,
                           handouts=items,
                           folders=drawer_folders,
                           tags=storage.all_tags(db, only_visible=True))