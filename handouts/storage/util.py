"""Small, dependency-light helpers shared across the storage package.

Pure functions with no knowledge of the DB shape: view-type cleaning, the
upload extension check, the image/pdf reader label, id/timestamp minting. Kept
here so both the domain modules and the web layer can reach them without pulling
in the heavier db module.
"""

import uuid
from datetime import datetime, timezone

from .paths import ALLOWED_EXTENSIONS, VIEW_TYPES, DEFAULT_VIEW_TYPE


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
    """Label a stored file by how the client should open it.

    'pdf'   -> rendered to images at upload, then read as pages.
    'model' -> a .glb 3D model, shown only by the object3d viewer. Kept as its
               own reader so the PDF-expansion and thumbnail passes skip it (a
               model is not a paged image) and the templates never try to draw
               an <img> for it.
    'image' -> everything else (png/jpg/gif/webp), the default.
    """
    ext = ext.lower()
    if ext == 'pdf':
        return 'pdf'
    if ext == 'glb':
        return 'model'
    return 'image'


def new_handout_id():
    return uuid.uuid4().hex


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_stamp():
    return int(datetime.now(timezone.utc).timestamp())
