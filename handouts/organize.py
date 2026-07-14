"""Grouping, ordering and searching of handouts for display.

Pure functions over lists of handout dicts — no Flask, no I/O — so they're
easy to reason about and test. Covers session/folder/tag grouping, a plain
chronological ordering, and free-text search.

A "group" is uniformly {'label': str, 'key': str|None, 'handouts': [...]}
with the exception of group_by_session, which keeps its richer session shape
(number + title) that the existing template already relies on.
"""

# Reserved id for the virtual folder holding handouts that belong to none.
ORPHANS_ID = 'orphans'
ORPHANS_NAME = 'Orphans'


def sort_chronological(handouts, newest_first=True):
    """Return handouts ordered by creation time (newest first by default)."""
    return sorted(handouts,
                  key=lambda h: h.get('created_at', ''),
                  reverse=newest_first)


def _in_folder(handouts, folder_id, known_ids):
    """Handouts belonging to `folder_id`, newest-first.

    `orphans` resolves to handouts that sit in no *existing* folder (ids that
    point at deleted folders don't count as membership). `known_ids` is the
    set of real folder ids, used to decide orphanhood.
    """
    if folder_id == ORPHANS_ID:
        picked = [h for h in handouts
                  if not any(fid in known_ids for fid in h.get('folders', []))]
    else:
        picked = [h for h in handouts if folder_id in h.get('folders', [])]
    return sort_chronological(picked)


def folder_cards(handouts, folders):
    """Build the "collections" view: one card per folder for the player.

    Each card is:
      {'id', 'name', 'count', 'covers': [file, ...],  # up to 4, for a 2x2 mosaic
       'is_orphans': bool}
    Real folders come first (alphabetical), then a virtual "Orphans" card if
    any handout is orphans. Empty real folders are still shown (count 0) so the
    master can see them; the Orphans card only appears when it has contents.
    """
    known_ids = {fo['id'] for fo in folders}
    cards = []
    for fo in sorted(folders, key=lambda f: f.get('name', '').lower()):
        items = _in_folder(handouts, fo['id'], known_ids)
        cards.append({
            'id': fo['id'],
            'name': fo['name'],
            'count': len(items),
            'covers': [h['files'][0] for h in items[:4] if h.get('files')],
            'is_orphans': False,
        })

    orphans = _in_folder(handouts, ORPHANS_ID, known_ids)
    if orphans:
        cards.append({
            'id': ORPHANS_ID,
            'name': ORPHANS_NAME,
            'count': len(orphans),
            'covers': [h['files'][0] for h in orphans[:4] if h.get('files')],
            'is_orphans': True,
        })
    return cards


def resolve_folder(folders, folder_id):
    """Return {'id', 'name'} for a folder id, handling the virtual Orphans.

    Returns None if the id matches no real folder and isn't `orphans`.
    """
    if folder_id == ORPHANS_ID:
        return {'id': ORPHANS_ID, 'name': ORPHANS_NAME}
    return next(({'id': fo['id'], 'name': fo['name']}
                 for fo in folders if fo['id'] == folder_id), None)


def handouts_in_folder(handouts, folders, folder_id):
    """Handouts inside a given folder id (or the virtual Orphans), newest-first."""
    known_ids = {fo['id'] for fo in folders}
    return _in_folder(handouts, folder_id, known_ids)


def group_by_folder(handouts, folders):
    """Group handouts by folder for the player view.

    `folders` is the master's folder list ([{id, name}, ...]); it drives the
    order and lets us show empty folders too. A handout in several folders
    appears under each. Handouts in no folder fall into a trailing
    "Orphans" group. Items within a group are newest-first.
    """
    by_id = {fo['id']: fo for fo in folders}
    buckets = {fo['id']: [] for fo in folders}
    orphans = []
    for h in handouts:
        member_ids = [fid for fid in h.get('folders', []) if fid in by_id]
        if member_ids:
            for fid in member_ids:
                buckets[fid].append(h)
        else:
            orphans.append(h)

    groups = []
    for fo in sorted(folders, key=lambda f: f.get('name', '').lower()):
        groups.append({'label': fo['name'], 'key': fo['id'],
                       'handouts': sort_chronological(buckets[fo['id']])})
    if orphans:
        groups.append({'label': 'Orphans', 'key': None,
                       'handouts': sort_chronological(orphans)})
    return groups


def group_by_tag(handouts):
    """Group handouts by tag. A handout with several tags appears under each.

    Tags are ordered alphabetically (case-insensitive). Handouts with no tag
    fall into a trailing "Untagged" group. Items within a group are
    newest-first.
    """
    buckets = {}
    untagged = []
    for h in handouts:
        tags = [t.strip() for t in h.get('tags', []) if t.strip()]
        if tags:
            for t in tags:
                buckets.setdefault(t, []).append(h)
        else:
            untagged.append(h)

    groups = [{'label': t, 'key': t, 'handouts': sort_chronological(items)}
              for t, items in sorted(buckets.items(),
                                     key=lambda kv: kv[0].lower())]
    if untagged:
        groups.append({'label': 'Untagged', 'key': None,
                       'handouts': sort_chronological(untagged)})
    return groups


def search(handouts, query):
    """Filter handouts by a free-text query (case-insensitive).

    Matches against title, description, category, tags, session number/title
    and per-file descriptions — i.e. everything a player might recall. An
    empty query returns the list unchanged.
    """
    q = (query or '').strip().lower()
    if not q:
        return handouts

    def haystack(h):
        parts = [
            h.get('title', ''),
            h.get('description', ''),
            h.get('category', ''),
            h.get('session_title', ''),
            str(h.get('session_number') or ''),
        ]
        parts.extend(h.get('tags', []))
        parts.extend(f.get('description', '') for f in h.get('files', []))
        return ' '.join(parts).lower()

    return [h for h in handouts if q in haystack(h)]


def group_by_session(handouts):
    """Group handouts by session number for the player view.

    Returns a list of dicts ordered by session number (unsorted last), each:
      {'number': int|None, 'title': str, 'handouts': [handout, ...]}
    Items within a session are ordered chronologically. The session title is
    taken from the earliest handout in that session that defines one.
    """
    buckets = {}
    for h in handouts:
        num = h.get('session_number')
        buckets.setdefault(num, []).append(h)

    groups = []
    for num, items in buckets.items():
        items.sort(key=lambda h: h.get('created_at', ''))
        title = next((h.get('session_title', '').strip()
                      for h in items if h.get('session_title', '').strip()), '')
        # `label`/`key` mirror the other groupers so the player template can
        # iterate any mode uniformly; `number`/`title` stay for the richer
        # session heading the template already renders.
        label = f'Session {num}' if num else 'Unsorted'
        groups.append({'number': num, 'title': title,
                       'label': label, 'key': num, 'handouts': items})

    # Numbered sessions ascending; unsorted (None) goes last.
    groups.sort(key=lambda g: (g['number'] is None, g['number'] or 0))
    return groups


def group_by_mode(handouts, mode, folders):
    """Dispatch a handout list into display groups by mode, uniform shape.

    Used by the master dashboard (and reusable elsewhere). Modes:
      'folder'  -> section per folder (+ Orphans), NOT collection cards
      'tag'     -> section per tag (+ Untagged)
      'session' -> section per session
      'recent'  -> a single unlabelled group, newest-first
    Any unknown mode collapses to 'recent'. Every group has label/key/handouts.
    """
    if mode == 'folder':
        return group_by_folder(handouts, folders)
    if mode == 'tag':
        return group_by_tag(handouts)
    if mode == 'session':
        return group_by_session(handouts)
    # recent / default: one flat, newest-first group
    return [{'label': '', 'key': None,
             'handouts': sort_chronological(handouts)}]
