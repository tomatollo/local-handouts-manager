"""PDF rendering helpers: page images for the Book viewer, plus thumbnails.

The Book viewer flips through images, so a PDF destined for it is converted
into one image per page at upload (or when the Master switches a handout to
Book). Carousel keeps the original PDF and just gets a first-page thumbnail
so the card shows a real preview instead of a grey placeholder.

Rendering is done with PyMuPDF (fitz). Everything here works on filenames
inside storage.UPLOAD_DIR and returns file entries in the same shape the rest
of the app uses: {'filename', 'reader', 'description'}.
"""

import os

import fitz  # PyMuPDF

from . import storage

# Render resolution. 110 DPI keeps handouts readable when zoomed on a tablet
# without producing huge files for a table-side app.
PAGE_DPI = 110
# Thumbnails only need to look right in a card, so they can be much smaller.
THUMB_DPI = 40


def is_pdf(entry):
    """True if a file entry points at a PDF."""
    return entry.get('reader') == 'pdf'


def _render(doc_path, page_index, dpi):
    """Render one page of a PDF to PNG bytes."""
    with fitz.open(doc_path) as doc:
        page = doc.load_page(page_index)
        pix = page.get_pixmap(dpi=dpi)
        return pix.tobytes('png')


def page_count(filename):
    """How many pages a stored PDF has (0 if it can't be read)."""
    path = os.path.join(storage.UPLOAD_DIR, filename)
    try:
        with fitz.open(path) as doc:
            return doc.page_count
    except Exception:
        return 0


def make_thumb(entry):
    """Render a PDF's first page to a small PNG and return its filename.

    The thumb sits next to the PDF as '<pdfname>.thumb.png'. Returns None if
    the PDF can't be rendered (corrupt file, password-protected, etc.) so the
    caller can fall back to the plain PDF placeholder.
    """
    src = os.path.join(storage.UPLOAD_DIR, entry['filename'])
    thumb_name = entry['filename'] + '.thumb.png'
    try:
        png = _render(src, 0, THUMB_DPI)
    except Exception:
        return None
    with open(os.path.join(storage.UPLOAD_DIR, thumb_name), 'wb') as f:
        f.write(png)
    return thumb_name


def explode_to_pages(entry, handout_id):
    """Turn a PDF file entry into one image entry per page.

    Writes '<handout_id>_pdf<stamp>_<n>.png' files and returns the new list of
    entries (reader='image'). The original PDF and any thumb are left on disk
    for the caller to remove once it has committed the new list. Returns the
    original entry unchanged (as a single-item list) if rendering fails, so a
    bad PDF never loses the Master's upload.
    """
    src = os.path.join(storage.UPLOAD_DIR, entry['filename'])
    try:
        with fitz.open(src) as doc:
            count = doc.page_count
            if count == 0:
                return [entry]
            stamp = storage.now_stamp()
            pages = []
            for i in range(count):
                page = doc.load_page(i)
                png = page.get_pixmap(dpi=PAGE_DPI).tobytes('png')
                name = f'{handout_id}_pdf{stamp}_{i}.png'
                with open(os.path.join(storage.UPLOAD_DIR, name), 'wb') as f:
                    f.write(png)
                pages.append({
                    'filename': name,
                    'reader': 'image',
                    # The first page inherits the PDF's description; the rest
                    # start blank for the Master to fill in.
                    'description': entry.get('description', '') if i == 0 else '',
                })
            return pages
    except Exception:
        return [entry]


def expand_pdfs_for_book(files, handout_id):
    """Replace every PDF in `files` with its rendered pages.

    Returns (new_files, discarded) where `discarded` lists the file entries
    (PDFs + their thumbs) the caller should delete from disk once saved.
    Non-PDF entries pass through untouched and keep their order.
    """
    out = []
    discarded = []
    for entry in files:
        if not is_pdf(entry):
            out.append(entry)
            continue
        pages = explode_to_pages(entry, handout_id)
        if pages == [entry]:
            # Rendering failed: keep the PDF as-is rather than losing it.
            out.append(entry)
            continue
        out.extend(pages)
        discarded.append({'filename': entry['filename']})
        if entry.get('thumb'):
            discarded.append({'filename': entry['thumb']})
    return out, discarded


def attach_thumbs(files):
    """Give every PDF entry in `files` a 'thumb' filename, in place.

    Safe to call repeatedly: entries that already have a usable thumb are left
    alone. Non-PDF entries are ignored.
    """
    for entry in files:
        if not is_pdf(entry):
            continue
        existing = entry.get('thumb')
        if existing and os.path.exists(
                os.path.join(storage.UPLOAD_DIR, existing)):
            continue
        thumb = make_thumb(entry)
        if thumb:
            entry['thumb'] = thumb
    return files

def backfill_thumbs(db):
    """Generate missing PDF thumbnails across the whole library.

    attach_thumbs only runs on upload/edit, so PDFs stored before thumbnails
    existed (or whose thumb file was lost) never get a preview. This walks the
    DB, renders what's missing and reports whether anything changed, so the
    caller can persist the new filenames.

    Idempotent and cheap once warm: entries with a thumb already on disk are
    skipped without opening the PDF.
    """
    changed = False
    for h in db.get('handouts', []):
        entries = list(h.get('files', []))
        if h.get('back_cover'):
            entries.append(h['back_cover'])
        for entry in entries:
            if not is_pdf(entry):
                continue
            existing = entry.get('thumb')
            if existing and os.path.exists(
                    os.path.join(storage.UPLOAD_DIR, existing)):
                continue
            thumb = make_thumb(entry)
            if thumb and thumb != existing:
                entry['thumb'] = thumb
                changed = True
    return changed