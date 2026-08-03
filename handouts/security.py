"""Security primitives: CSRF protection and rate limiting.

Both are written against the Python standard library only -- no Flask-WTF, no
Flask-Limiter -- so the whole mechanism is readable in one file and has no
version-coupled dependency to maintain. The goal is not to reimplement a
security framework, but to close two concrete holes in this app's stated threat
model (a curious or careless client on a trusted LAN) with code a maintainer
can audit end to end.

References
---------
* OWASP, "Cross-Site Request Forgery Prevention Cheat Sheet" (2024): the
  synchronizer-token and signed double-submit patterns used below.
  https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
* OWASP, "Denial of Service Cheat Sheet": application-level rate limiting as a
  first-line control against resource-exhaustion loops.
* D. Hardt (ed.), RFC 6749 sec. 10.12 (OAuth 2.0), on CSRF and the role of an
  unguessable, session-bound token. https://www.rfc-editor.org/rfc/rfc6749
* A. Tanenbaum, *Computer Networks*, 5th ed., sec. 5.4 (leaky/token bucket) --
  the traffic-shaping algorithm the limiter implements.
* Python docs: `hmac.compare_digest` for constant-time comparison
  (https://docs.python.org/3/library/hmac.html), and `secrets` for
  cryptographically strong tokens (https://docs.python.org/3/library/secrets.html).
"""

import hmac
import time
import threading
from collections import defaultdict
from hashlib import sha256

from flask import session, request, abort, g


# ===========================================================================
# CSRF PROTECTION
# ===========================================================================
#
# Why this exists
# ---------------
# Every state-changing action in the app is a POST behind master_required. The
# session cookie is already set SameSite=Lax, which the browser will NOT attach
# to a cross-site POST -- so a form on evil.example that auto-submits to our
# /delete/<id> simply arrives without the master session and is rejected. That
# covers the classic cross-origin CSRF case.
#
# Lax does NOT cover the *same-site* case, though, and this app has one that
# matters: the Master enters free text (handout descriptions, wiki bodies, POI
# labels) that is rendered back into master pages. A payload that reaches the
# DOM on our own origin can issue same-origin POSTs that DO carry the cookie. A
# per-session CSRF token defeats that, because a script running on a page it is
# not allowed to read cannot obtain the token, and the server rejects any POST
# that lacks it.
#
# Design: synchronizer token, session-bound
# -----------------------------------------
# We keep ONE random secret per session (`csrf_secret`) and derive the token as
# HMAC-SHA256(secret, "csrf"). The same opaque token is handed to every form;
# validation is a constant-time compare. This is the "synchronizer token
# pattern" (OWASP). We deliberately do not tie the token to each form's action
# -- per-action tokens buy little here and would complicate the many small POST
# forms in the templates.
#
# The token is exposed to templates via a context processor (see app.py) and
# dropped into each form as a hidden field, plus a <meta> tag so `fetch()`
# callers (the map page) can echo it in an X-CSRF-Token header.

CSRF_SESSION_KEY = 'csrf_secret'
CSRF_FORM_FIELD = 'csrf_token'
CSRF_HEADER = 'X-CSRF-Token'

# Methods that change state must carry a valid token. Safe methods (GET, HEAD,
# OPTIONS) are exempt by definition -- they must not mutate anything, per
# RFC 7231 sec. 4.2.1 "safe methods".
PROTECTED_METHODS = frozenset({'POST', 'PUT', 'PATCH', 'DELETE'})


def _get_or_create_secret():
    """Return this session's CSRF secret, creating one on first use.

    The secret lives in the signed session cookie, so a client cannot forge it
    without SECRET_KEY. `secrets.token_hex` gives a cryptographically strong
    value (Python docs, `secrets`).
    """
    secret = session.get(CSRF_SESSION_KEY)
    if not secret:
        import secrets
        secret = secrets.token_hex(32)
        session[CSRF_SESSION_KEY] = secret
    return secret


def get_token():
    """The token to embed in forms / expose via <meta>.

    Derived as HMAC(secret, "csrf") so the value handed out is not the raw
    session secret itself. Any constant message works; the security comes from
    the secret, which never leaves the signed cookie.
    """
    secret = _get_or_create_secret()
    return hmac.new(secret.encode(), b'csrf', sha256).hexdigest()


def _submitted_token():
    """Pull the token from the form field first, then the header (for fetch)."""
    return (request.form.get(CSRF_FORM_FIELD)
            or request.headers.get(CSRF_HEADER)
            or '')


def validate_request():
    """Abort 400 if a state-changing request lacks a valid CSRF token.

    Wired as a before_request in app.py. Constant-time comparison via
    hmac.compare_digest avoids leaking, through timing, how much of the token
    matched (Python docs, hmac).
    """
    if request.method not in PROTECTED_METHODS:
        return
    # A session with no secret yet cannot have issued a token, so any token
    # presented is by definition invalid -- fail closed.
    expected = get_token()
    submitted = _submitted_token()
    if not submitted or not hmac.compare_digest(expected, submitted):
        abort(400, 'Missing or invalid CSRF token. Reload the page and retry.')


# ===========================================================================
# RATE LIMITING
# ===========================================================================
#
# Why this exists
# --------------
# The player-facing pollers -- /api/pop and /api/map/state -- each call
# storage.load_db(), which reads and JSON-parses the whole database file on
# every hit. A client stuck in a tight loop (a runaway script, a wedged tab, or
# someone deliberately hammering the box) can turn that into sustained disk +
# CPU load and starve the table's real traffic. Nothing in the app currently
# bounds request rate, so this is the one DoS vector that is cheap to trigger
# and worth closing (OWASP DoS Cheat Sheet).
#
# Algorithm: token bucket
# -----------------------
# Each client (keyed by IP) owns a bucket that refills at a steady rate up to a
# capacity. Each request costs one token; an empty bucket means "too many
# requests" -> HTTP 429. The token bucket is the standard traffic-shaping
# primitive (Tanenbaum, *Computer Networks*, sec. 5.4): unlike a fixed window,
# it permits short bursts (up to `capacity`) while still bounding the *average*
# rate to `refill_per_sec`, which fits a page that legitimately polls a few
# times per second but should never sustain hundreds.
#
# Scope + limits
# --------------
# This is an in-process, in-memory limiter. It is intentionally NOT distributed:
# the app is a single-process waitress server on one machine, so a shared store
# (Redis, etc.) would be dead weight. State is a dict of buckets guarded by a
# lock; abandoned buckets are pruned so memory cannot grow without bound.
#
# The IP key is honest about its limit: on a LAN, several players may share one
# NAT and thus one bucket. The limits below are set high enough that normal
# polling by a shared IP stays comfortable, and low enough that a genuine loop
# is still caught. This is a resource guard, not an authentication mechanism.

class TokenBucket:
    """A single client's bucket. Not thread-safe on its own; the limiter locks."""

    __slots__ = ('capacity', 'tokens', 'refill_per_sec', 'last')

    def __init__(self, capacity, refill_per_sec, now):
        self.capacity = float(capacity)
        self.tokens = float(capacity)      # start full: first hits never wait
        self.refill_per_sec = float(refill_per_sec)
        self.last = now

    def take(self, now):
        """Refill by elapsed time, then try to spend one token.

        Returns (allowed, retry_after_seconds). retry_after is 0 when allowed,
        else the whole seconds until one token is available -- handed back to
        the client in a Retry-After header (RFC 7231 sec. 7.1.3).
        """
        elapsed = now - self.last
        self.last = now
        # Refill, capped at capacity.
        self.tokens = min(self.capacity,
                          self.tokens + elapsed * self.refill_per_sec)
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True, 0
        # Time until the bucket regains a full token.
        needed = 1.0 - self.tokens
        retry_after = needed / self.refill_per_sec if self.refill_per_sec else 1
        return False, max(1, int(retry_after + 0.999))


class RateLimiter:
    """In-memory token-bucket limiter keyed by an arbitrary string (here, IP).

    One instance can serve several route groups by exposing named policies; a
    single lock protects all buckets, which is ample for a single-process
    server handling table-sized traffic.
    """

    def __init__(self):
        self._buckets = defaultdict(dict)   # policy -> {key -> TokenBucket}
        self._lock = threading.Lock()
        # Track last-seen per (policy,key) so idle buckets can be pruned.
        self._seen = defaultdict(dict)
        self._last_prune = time.monotonic()

    def _prune(self, now, max_idle=3600):
        """Drop buckets untouched for `max_idle` seconds. Called opportunistically."""
        if now - self._last_prune < 300:      # at most every 5 min
            return
        self._last_prune = now
        for policy, seen in list(self._seen.items()):
            for key, ts in list(seen.items()):
                if now - ts > max_idle:
                    seen.pop(key, None)
                    self._buckets[policy].pop(key, None)

    def check(self, policy, key, capacity, refill_per_sec):
        """Spend a token for (policy,key). Returns (allowed, retry_after)."""
        now = time.monotonic()
        with self._lock:
            self._prune(now)
            buckets = self._buckets[policy]
            bucket = buckets.get(key)
            if bucket is None:
                bucket = TokenBucket(capacity, refill_per_sec, now)
                buckets[key] = bucket
            self._seen[policy][key] = now
            return bucket.take(now)


# One shared limiter for the process.
limiter = RateLimiter()


def client_key():
    """Best-effort client identity for limiting: the peer IP.

    We read request.remote_addr directly and do NOT trust X-Forwarded-For:
    on the trusted-LAN deployment there is no reverse proxy setting it, so
    honouring that header would let any client spoof its identity and dodge the
    limit. If this app is ever put behind a real proxy, that is the one place
    to revisit (and then only a trusted proxy's header should be believed).
    """
    return request.remote_addr or 'unknown'


# Policies. Kept as data so app.py reads them declaratively. Numbers are chosen
# for the poller case: the player pages poll a few times a second at most, so a
# steady 5/sec with a 15-burst capacity is invisible to honest use but caps a
# runaway loop at 5 req/sec/IP instead of thousands.
POLICIES = {
    # Player pollers: /api/pop, /api/map/state, /api/map/reveal.png
    'poll': {'capacity': 15, 'refill_per_sec': 5},
    # Everything else (page loads, master actions): far looser, just a ceiling
    # on absurd floods.
    'default': {'capacity': 60, 'refill_per_sec': 20},
}


def enforce(policy_name):
    """Apply a named policy to the current request; abort 429 if over.

    Returns the retry_after (0 when allowed) so the caller/after_request can set
    a Retry-After header. Wired in app.py's before_request.
    """
    policy = POLICIES.get(policy_name, POLICIES['default'])
    allowed, retry_after = limiter.check(
        policy_name, client_key(),
        policy['capacity'], policy['refill_per_sec'])
    if not allowed:
        # Stash for the error handler / after_request to surface Retry-After.
        g.rate_limited_retry_after = retry_after
        abort(429, 'Too many requests. Slow down and try again shortly.')
    return retry_after
