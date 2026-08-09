"""Upload/file operations: saving handout files and back covers, deleting them
(and their generated thumbnails), and the map-image save/remove pair. The only
storage module besides db that touches the uploads/maps folders on disk.
"""

import os

from werkzeug.utils import secure_filename

from .paths import UPLOAD_DIR, MAP_DIR, MAP_EXTENSIONS
from .util import reader_for, now_stamp


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


def allowed_map_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in MAP_EXTENSIONS


def save_map_image(file_storage):
    """Save an uploaded map background into MAP_DIR and return its filename.

    Returns None if no usable file was given. The name is timestamped so a new
    upload never collides with (or silently overwrites) a cached older one on
    the players' browsers. Only the bare filename is returned; the caller
    stores it in map_state['map_image'] and the templates build the URL.
    """
    if not file_storage or not file_storage.filename:
        return None
    safe = secure_filename(file_storage.filename)
    if '.' not in safe:
        return None
    ext = safe.rsplit('.', 1)[1].lower()
    os.makedirs(MAP_DIR, exist_ok=True)
    name = f'map_{now_stamp()}.{ext}'
    file_storage.save(os.path.join(MAP_DIR, name))
    return name


def remove_map_image(filename):
    """Delete a saved map background, best-effort. Silent if already gone."""
    if not filename:
        return
    # Defend against a stored value that somehow carries a path: only ever
    # touch a bare name inside MAP_DIR.
    if '/' in filename or '\\' in filename:
        return
    try:
        os.remove(os.path.join(MAP_DIR, filename))
    except OSError:
        pass
