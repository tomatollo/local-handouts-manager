"""POP broadcasts (global, master-controlled).

A POP is "the Master wants this handout on every screen, now". It is stored
rather than pushed: there is no socket to push down, and storing it makes the
feature independent of who happened to be connected at the moment it fired.

Only the newest POP is kept. The Master popping a second handout supersedes
the first -- there is no queue, because a queue would mean players silently
working through a backlog of dramatic reveals in the wrong order.
"""

from datetime import datetime, timezone

from .paths import POP_KEY, POP_TTL_SECONDS
from .util import now_iso


def pop_state(db):
    """The current POP as {seq, handout_id, at}. Never None (see _normalize)."""
    return db.get('settings', {}).get(POP_KEY, {
        'seq': 0, 'handout_id': None, 'at': None})


def pop_age_seconds(pop, now=None):
    """Seconds since `pop` was fired, or None if that can't be determined.

    Returns None -- not 0 -- when `at` is missing or unparseable, so callers
    must decide explicitly what an unknown age means rather than inheriting a
    "fresh" answer by accident (see pop_is_live, which treats it as expired).

    `now` is injectable so the TTL can be tested without sleeping.
    """
    at = (pop or {}).get('at')
    if not at:
        return None
    try:
        fired = datetime.fromisoformat(at)
    except (TypeError, ValueError):
        # A hand-edited or truncated timestamp. Unknown age, not zero.
        return None
    # Records written before the TTL existed may be naive; assume UTC, which is
    # what now_iso() has always produced.
    if fired.tzinfo is None:
        fired = fired.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    return (now - fired).total_seconds()


def pop_is_live(pop, now=None):
    """True if `pop` still points at something and hasn't aged out.

    Fails closed on every uncertainty: no handout, no timestamp, an unreadable
    timestamp, or a clock that has jumped backwards all count as "not live".
    The cost of a false negative is a POP the Master re-fires; the cost of a
    false positive is a stale modal ambushing a player mid-session, which is
    the bug this exists to kill.
    """
    pop = pop or {}
    if not pop.get('handout_id'):
        return False
    age = pop_age_seconds(pop, now)
    if age is None:
        return False
    # A negative age means the POP is stamped in the future -- a clock change,
    # or a DB copied from another machine. Don't trust it.
    if age < 0:
        return False
    return age < POP_TTL_SECONDS


def set_pop(db, handout_id):
    """Record a POP for `handout_id` and return the new state.

    Bumping `seq` is what actually notifies players: they poll for it and act
    on any value above the last one they showed. The counter is bumped even
    when the same handout is popped twice in a row, so a Master re-popping to
    catch a distracted table still reaches screens that already dismissed it.
    """
    settings = db.setdefault('settings', {})
    current = settings.setdefault(POP_KEY, {'seq': 0})
    settings[POP_KEY] = {
        'seq': current.get('seq', 0) + 1,
        'handout_id': handout_id,
        'at': now_iso(),
    }
    return settings[POP_KEY]


def clear_pop(db):
    """Retire the current POP without rewinding `seq`.

    Called when the popped handout is deleted or unpublished. `seq` keeps
    climbing so clients that already showed this POP never see it again, while
    clients still polling simply find nothing to open.
    """
    settings = db.setdefault('settings', {})
    current = settings.setdefault(POP_KEY, {'seq': 0})
    settings[POP_KEY] = {
        'seq': current.get('seq', 0) + 1,
        'handout_id': None,
        'at': None,
    }
    return settings[POP_KEY]
