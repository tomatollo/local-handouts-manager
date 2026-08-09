"""Handout record helpers: lookup, the player-facing payload, secret reveals,
and the small parse/aggregate helpers over the handout list (categories, tags,
passwords, session number).
"""

from .paths import DEFAULT_VIEW_TYPE


def find(db, handout_id):
    return next((h for h in db['handouts'] if h['id'] == handout_id), None)


def player_payload(handout):
    """The player-facing view of a handout: exactly what the lightbox opens.

    One shared shape for every path that hands a handout to the client (the POP
    poll and the secret-reveal endpoint), so the browser never needs a second
    way to build a viewer. Deliberately omits master-only fields -- notably the
    secret password itself, which must never travel to a player.
    """
    return {
        'id': handout['id'],
        'title': handout.get('title', ''),
        'description': handout.get('description', ''),
        'found_location': handout.get('found_location', ''),
        'found_date': handout.get('found_date', ''),
        'view_type': handout.get('view_type', DEFAULT_VIEW_TYPE),
        'hard_covers': handout.get('hard_covers', True),
        'files': handout.get('files', []),
        'back_cover': handout.get('back_cover'),
        # True when THIS handout itself carries a further secret reveal, so the
        # viewer knows to keep showing the password box after a reveal chains
        # into another handout. The password values are never included.
        'has_secret': bool(handout.get('secret_passwords')
                           and handout.get('secret_handout_id')),
    }


def reveal_secret(db, handout_id, password):
    """Resolve a password typed on `handout_id` to the hidden handout it unlocks.

    Returns the target handout's player_payload when `password` matches ANY of
    the source handout's accepted passwords AND the linked target still exists;
    otherwise None. Each side is whitespace-trimmed to match how the Master
    typed the words into the form. When the source has secret_ignore_case set,
    the comparison is case-insensitive, so "Xanathar" accepts "xanathar" too.

    No timing-safe compare and no hashing: this is a table gimmick guarding a
    story beat, not a credential (see the module + auth notes). The target is
    returned even if it is not `visible` -- typing the password IS the reveal,
    so requiring a separate publish would defeat the feature.
    """
    source = find(db, handout_id)
    if source is None:
        return None
    accepted = [p for p in (source.get('secret_passwords') or []) if p.strip()]
    target_id = source.get('secret_handout_id')
    if not accepted or not target_id:
        return None
    typed = (password or '').strip()
    if not typed:
        return None
    if source.get('secret_ignore_case'):
        typed_cmp = typed.casefold()
        matched = any(typed_cmp == p.strip().casefold() for p in accepted)
    else:
        matched = any(typed == p.strip() for p in accepted)
    if not matched:
        return None
    target = find(db, target_id)
    if target is None:
        return None
    return player_payload(target)


def all_categories(db):
    return sorted({h.get('category', '').strip()
                   for h in db['handouts'] if h.get('category', '').strip()})


def all_tags(db, only_visible=False):
    """Every distinct tag across handouts, sorted case-insensitively.

    With `only_visible=True`, tags are gathered ONLY from handouts the players
    can see (visible=True). This is what the player side must use: a tag that
    exists solely on a hidden handout would otherwise leak the existence of
    unrevealed material through the browse drawer / tag grouping. The master
    side calls it without the flag so it can still organise by every tag,
    including those on handouts not yet published.
    """
    tags = set()
    for h in db['handouts']:
        if only_visible and not h.get('visible'):
            continue
        for t in h.get('tags', []):
            t = t.strip()
            if t:
                tags.add(t)
    return sorted(tags, key=str.lower)


def parse_tags(raw):
    """Split a comma-separated tag string into a clean, de-duplicated list.

    Order is preserved (first occurrence wins); comparison is case-insensitive
    so 'Map' and 'map' don't both survive.
    """
    seen = set()
    out = []
    for part in (raw or '').split(','):
        t = part.strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def parse_passwords(raw):
    """Split the secret-reveal textarea into a clean list of accepted words.

    One password per line: passwords may well contain spaces or commas ("open
    sesame", "3,000 gold"), so a newline is the only safe separator. Blank
    lines are dropped and exact duplicates removed while keeping first-seen
    order. Case is preserved here; whether case matters at match time is the
    separate secret_ignore_case flag's job (see reveal_secret).
    """
    seen = set()
    out = []
    for line in (raw or '').replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        p = line.strip()
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def parse_session_number(raw):
    raw = (raw or '').strip()
    try:
        return int(raw) if raw else None
    except ValueError:
        return None
