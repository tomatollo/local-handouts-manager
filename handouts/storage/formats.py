"""File-format labelling for the master's "Group by Format" view.

`source_format` records the ORIGINAL kind of a handout -- 'pdf', 'png',
'jpg', ... -- chosen from the first file the Master uploaded, BEFORE any
conversion. It matters because a PDF is now rendered to PNG pages at upload:
grouping by what sits on disk would file every PDF under "PNG", so we keep
the original format as its own field instead. It is a label for sorting only;
nothing about how the handout is viewed depends on it.
"""

# jpg/jpeg are the same format to a human sorting a shelf, so they fold together
# under the shorter, more familiar 'jpg'.
_FORMAT_ALIASES = {'jpeg': 'jpg'}
# Shown for a handout whose format can't be determined (no files, hand-edited
# record). Kept distinct from a real extension so it sorts into its own group.
FORMAT_UNKNOWN = ''
# Substring that pdfs.explode_to_pages bakes into every page it renders from a
# PDF ('<id>_pdf<stamp>_<n>.png'). It is the one durable trace that a now-PNG
# page began life as a PDF, so a handout converted BEFORE source_format was
# recorded can still be grouped under 'pdf' instead of 'png'. Must stay in sync
# with pdfs.PDF_PAGE_MARKER (kept as a literal here to avoid importing pdfs,
# which imports this module).
_PDF_PAGE_MARKER = '_pdf'


def ext_of(filename):
    """Lowercase extension of a filename without the dot, or '' if none."""
    name = filename or ''
    return name.rsplit('.', 1)[1].lower() if '.' in name else ''


def normalize_format(ext):
    """Fold an extension into its canonical format label (jpeg -> jpg, ...)."""
    ext = (ext or '').strip().lower().lstrip('.')
    return _FORMAT_ALIASES.get(ext, ext)


def _looks_like_converted_pdf(h):
    """True if this handout's pages look like they were rendered from a PDF.

    A PDF is exploded into PNG pages whose names carry the '_pdf' marker (see
    _PDF_PAGE_MARKER). A handout saved before source_format existed therefore
    still betrays its PDF origin through those filenames. We require the COVER
    (files[0]) to carry the marker: that is the page the format label is meant
    to describe, and it avoids mislabelling an image handout that happens to
    include one converted page.
    """
    files = h.get('files') or []
    if not files:
        return False
    cover_name = files[0].get('filename', '') or ''
    return _PDF_PAGE_MARKER in cover_name


def format_of_handout(h):
    """The handout's original format label for grouping.

    Resolution order:
      1. An explicit `source_format` recorded at upload -- always authoritative.
      2. The '_pdf' filename marker on the cover: recovers handouts that were
         converted from PDF to PNG BEFORE source_format was recorded, so those
         still group under 'pdf' rather than 'png'.
      3. The cover file's extension -- correct for plain image handouts.
    Returns FORMAT_UNKNOWN when nothing can be determined.
    """
    fmt = normalize_format(h.get('source_format'))
    if fmt:
        return fmt
    if _looks_like_converted_pdf(h):
        return 'pdf'
    files = h.get('files') or []
    if files:
        return normalize_format(ext_of(files[0].get('filename', '')))
    return FORMAT_UNKNOWN


def source_format_from_uploads(file_storages):
    """Pick the original format label from a list of just-uploaded files.

    Uses the FIRST file (the cover), mirroring how the rest of the app treats
    files[0] as the handout's face. Called at upload time, before any PDF is
    rendered to images, so a PDF handout is recorded as 'pdf' even though its
    stored pages end up as PNG.
    """
    for f in file_storages:
        if f and getattr(f, 'filename', ''):
            return normalize_format(ext_of(f.filename))
    return FORMAT_UNKNOWN


def all_formats(db):
    """Every distinct source format across handouts, sorted alphabetically."""
    formats = set()
    for h in db.get('handouts', []):
        fmt = format_of_handout(h)
        if fmt:
            formats.add(fmt)
    return sorted(formats)
