"""PDF rendering helpers: page images for the Book AND Carousel viewers, plus
thumbnails.

Neither player viewer flips a live PDF: both show images. A PDF destined for
either is therefore converted into one image per page at upload (or when the
Master edits the handout). The Book viewer flips those pages with a page-curl;
the Carousel steps through them with arrows/dots. In both cases the viewer only
ever sees `reader: 'image'` entries, so there is a single rendering path and no
<iframe> anywhere.

Rendering is done with PyMuPDF (fitz). Everything here works on filenames
inside storage.UPLOAD_DIR and returns file entries in the same shape the rest
of the app uses: {'filename', 'reader', 'description'}.
"""

import os

import fitz  # PyMuPDF

from . import storage

# Render resolution. A scanned text page needs more detail than a pixel-art
# map: 150 DPI keeps body text crisp when a page is flipped or zoomed on a
# tablet, while still producing files light enough for a table-side LAN app.
# (It was 110, which left PDF text soft and hard to read in the Book viewer.)
PAGE_DPI = 150
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


# The two viewers now expand PDFs identically -- both show images, neither
# flips a live PDF -- so carousel expansion is just an alias with a name that
# reads correctly at its call sites. Kept as a separate name (rather than
# renaming expand_pdfs_for_book everywhere) so each caller still says which
# viewer it is building for.
expand_pdfs_for_carousel = expand_pdfs_for_book


def expand_pdfs(files, handout_id):
    """View-agnostic PDF -> page-images expansion for a file list.

    Both viewers want the same thing now, so this is the plain entry point when
    the caller doesn't care to name a viewer. Same contract as
    expand_pdfs_for_book: returns (new_files, discarded).
    """
    return expand_pdfs_for_book(files, handout_id)


def backfill_carousel_pdfs(db):
    """Expand any still-PDF carousel pages across the library into images.

    Older carousel handouts (saved when the carousel showed PDFs in an iframe)
    still carry `reader: 'pdf'` page entries. The carousel now renders images
    only, so those would otherwise have nothing to show. This walks the DB and
    converts them in place, exactly like the upload path does for new files.

    Non-destructive by design: unlike the upload/edit path, the original PDF
    (and its thumb) are LEFT on disk rather than deleted, so this migration is
    reversible -- a Master who preferred the iframe can restore the old
    behaviour without having lost the source file. The cost is a little dead
    disk space, which the Master can reclaim by re-saving the handout.

    Book handouts are untouched here: their PDFs were already expanded at
    upload, so they carry no `reader: 'pdf'` pages to find. Returns True if it
    changed anything, so the caller can persist.
    """
    changed = False
    for h in db.get('handouts', []):
        files = h.get('files', [])
        if not any(is_pdf(f) for f in files):
            continue
        new_files, _discarded = expand_pdfs(files, h['id'])
        # _discarded intentionally ignored: we keep the source PDFs on disk
        # (see the docstring). Only the DB record is updated to point at the
        # freshly rendered images.
        if new_files != files:
            h['files'] = new_files
            changed = True
        # A PDF back cover, if any, is a single flip page in the Book viewer
        # and is handled by that path; the carousel ignores back covers, so we
        # leave back_cover alone here.
    return changed


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