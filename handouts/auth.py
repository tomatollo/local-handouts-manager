"""Master authentication.

The app is a LAN tool: everyone at the table reaches the same host, so "who is
the Master" cannot be inferred from the network. Until now nothing separated
the two roles at all -- /dm-panel was simply an URL players were trusted not to
type. That was tolerable while the Master side only held *management* controls
(a curious player could publish a handout, which is annoying but not a spoiler).

The Master Wiki changes the stakes: it holds secrets that ruin the campaign if
read. Hiding it in a menu players don't open is not protection, so the split is
enforced here, server-side, on every request.

The model is deliberately small:

  * One shared passphrase, set by the Master. There are no user accounts,
    because there is only ever one Master per table.
  * Unlocking stores a flag in Flask's signed session cookie. The cookie is
    signed with SECRET_KEY, so a player cannot forge `is_master` by editing it.
  * The passphrase is stored as a salted PBKDF2 hash in the DB, never in clear.

The threat model is honest about its limits: this stops a curious player at the
table from reading the Master's notes. It is not hardened against an attacker
on the network (the app is plain HTTP), and it is not meant to be -- the app is
built to be served on a trusted home Wi-Fi.
"""

import functools
import os

from flask import session, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import storage

# Key under `settings` in the DB holding the PBKDF2 hash of the passphrase.
PASSPHRASE_KEY = 'master_passphrase_hash'

# Session key marking this browser as the Master's.
SESSION_KEY = 'is_master'

# Where the signing key is read from, with a persisted fallback (see
# `secret_key`). Environment wins so the deployment can rotate it.
SECRET_ENV = 'HANDOUTS_SECRET_KEY'
SECRET_KEY_SETTING = 'secret_key'


def secret_key(db):
    """The Flask SECRET_KEY used to sign the session cookie.

    Order: environment first (lets the Master rotate it without touching the
    DB), then a value persisted in the DB, then a freshly generated one which
    is saved. Persisting matters: a key regenerated on every boot would sign
    cookies that the next boot cannot verify, silently logging the Master out
    on every restart.
    """
    from_env = os.environ.get(SECRET_ENV, '').strip()
    if from_env:
        return from_env

    settings = db.setdefault('settings', {})
    existing = settings.get(SECRET_KEY_SETTING)
    if existing:
        return existing

    generated = os.urandom(32).hex()
    settings[SECRET_KEY_SETTING] = generated
    storage.save_db(db)
    return generated


def is_configured(db):
    """True once the Master has chosen a passphrase."""
    return bool(db.get('settings', {}).get(PASSPHRASE_KEY))


def set_passphrase(db, raw):
    """Store a new passphrase as a salted hash. Empty input is rejected."""
    raw = (raw or '').strip()
    if not raw:
        return False
    db.setdefault('settings', {})[PASSPHRASE_KEY] = generate_password_hash(raw)
    return True


def check_passphrase(db, raw):
    """Verify a candidate passphrase against the stored hash."""
    stored = db.get('settings', {}).get(PASSPHRASE_KEY)
    if not stored:
        return False
    return check_password_hash(stored, (raw or '').strip())


def unlock():
    """Mark this session as the Master's."""
    session[SESSION_KEY] = True
    session.permanent = True


def lock():
    """Drop Master rights from this session."""
    session.pop(SESSION_KEY, None)


def is_master():
    """True if the current request carries an unlocked Master session.

    Falls open only in the one case where it must: before a passphrase has
    ever been set, there is nothing to check against and the Master needs to
    reach the dashboard to set one. `first_run` in the UI context makes this
    state visible rather than silent, and the dashboard nags until it is fixed.
    """
    if session.get(SESSION_KEY):
        return True
    return not is_configured(storage.load_db())


def master_required(view):
    """Guard a view so only an unlocked Master session may reach it.

    Applied to every master route, including the Wiki. Browsers get a redirect
    to the unlock page carrying `next`, so the Master lands back where they
    were aiming.
    """
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not is_master():
            return redirect(url_for('master.unlock', next=request.full_path))
        return view(*args, **kwargs)
    return wrapped
