"""Player-facing routes: the public hub of revealed handouts."""

from flask import Blueprint, render_template, request, redirect, url_for

from . import storage
from . import organize
from . import pdfs

bp = Blueprint('player', __name__)

# Organization modes offered in the player drawer.
MODES = ('folder', 'session', 'tag', 'recent')


@bp.route('/')
def home():
    db = storage.load_db()
    
    # Older PDFs predate thumbnails; render any that are missing so cards show
    # a real preview instead of the grey placeholder.
    if pdfs.backfill_thumbs(db):
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
