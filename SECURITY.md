Nessun problema! In realtà, usare la prima persona singolare ("I") per un progetto personale non solo è corretto, ma è anche la scelta più onesta e trasparente per un paper a firma singola. È una pratica comunemente accettata nell'ingegneria del software.

Ho corretto i pronomi ("we" in "I", "our" in "my"), lasciando il plurale solamente all'interno della citazione delle quattro domande di Shostack (nella sezione 2), poiché si tratta di un costrutto standard del settore.

Ecco il tuo paper aggiornato:

---

# Security Design of the Local Handouts Manager

*A study of the access-control, request-integrity, and availability decisions
made in this application, the reasoning behind each, and the alternatives that
were weighed and rejected.*

---

## 1. Purpose and scope

This document is not a user guide. It is a record of *why* the application's security mechanisms are built the way they are, written so that a future maintainer (or a reader studying the codebase) can reconstruct the reasoning rather than merely observe the result. Where a decision trades one property for another, the trade is stated explicitly.

The application is a self-hosted tool for tabletop role-playing games. One person (the *Master*) runs it on a computer on a home network; the other people at the table (the *players*) reach it from their phones and laptops
over that same local network (LAN). The Master manages a library of "handouts"
(images, maps, PDFs) and reveals them to the players at chosen moments. Some
material is secret: revealing it early spoils the game.

Everything below follows from that setting.

---

## 2. Threat model

Security design is meaningless without a stated adversary. Following the
structured approach recommended in Shostack's *Threat Modeling: Designing for
Security* (Wiley, 2014) (asking "what are we building, what can go wrong, what
do we do about it, and did we do a good job") I name the actors and the
threats explicitly.

### 2.1 Assets

1. **Secret handouts and Master notes.** The primary asset. Their value is
*timing*: a map is not secret forever, only until the party reaches it.
2. **Table availability.** The app must stay responsive during a session; an
outage mid-game is a real harm even if no data leaks.
3. **Integrity of the library.** Handouts must not be deleted, republished, or
altered except by the Master.

### 2.2 Actors

* **The Master.** Trusted. Holds one passphrase.
* **A player.** Semi-trusted. Invited to the network and to the player view,
but must not reach the Master side. The realistic player threat is
*curiosity*: typing `/dm-panel` to peek, not mounting a network attack.
* **A network attacker.** *Explicitly out of scope.* The app is served over
plain HTTP on a trusted LAN. An attacker who can already read LAN traffic or
run code on the Master's machine defeats any control this app could add, and
defending against them (TLS, network isolation) is the deployment's job, not
the application's. This boundary is stated so the reader knows which
guarantees are *not* claimed. This mirrors the standard advice that a threat
model must document assumptions and trust boundaries rather than pretend to
universal protection.

### 2.3 Threats addressed in the application

Using the STRIDE taxonomy (Microsoft; see Shostack, 2014) as a
checklist, the threats this application's code is responsible for are:

| STRIDE category | Concrete threat here | Control (section) |
| --- | --- | --- |
| **S**poofing | A player claims to be the Master | Passphrase + signed session (3) |
| **T**ampering | A forged request mutates the library | CSRF token (4) |
| **R**epudiation | *Out of scope* single trusted Master, no audit requirement | - |
| **I**nformation disclosure | Secret handouts leak early | Server-side authorization + staged reveals (3, 6) |
| **D**enial of service | A request loop exhausts the server | Rate limiting (5) |
| **E**levation of privilege | Player reaches Master routes (3) | `master_required` on every route |

The rows marked out of scope are deliberate: naming them and declining them is
itself a design decision, not an omission.

---

## 3. Authentication and authorization

### 3.1 The core decision: one passphrase, not user accounts

There is exactly one privileged role and, at any table, exactly one person who
holds it. Building user accounts (registration, per-user credentials, password
reset flows) would add a large attack surface (account enumeration, credential
storage, reset-token handling) to protect a distinction the deployment already
makes physically: whoever is running the laptop is the Master.

I therefore chose a **single shared passphrase**. This is the smallest
mechanism that expresses the one distinction that matters. The cost is that the
passphrase cannot identify *which* Master unlocked (there is only one) and
cannot be revoked per-person (there are no persons, only the role). Both costs
are acceptable given the actor model in 2.2.

### 3.2 How the passphrase is stored

The passphrase is never stored in clear text. It is stored as a salted hash
produced by Werkzeug's `generate_password_hash`, which defaults to PBKDF2 with
a per-hash random salt, and verified with `check_password_hash`. This follows
the long-standing guidance to store passwords using a salted, iterated
key-derivation function rather than a bare hash (OWASP, *Password Storage Cheat
Sheet*; NIST SP 800-63B, 5.1.1.2, which recommends salting and using an
approved key-derivation function). PBKDF2 is explicitly listed as an acceptable
choice in NIST SP 800-63B. I rely on the library default rather than
hand-rolling parameters, on the principle that cryptographic primitives should
come from a reviewed implementation.

### 3.3 How a session is recognized

On a correct passphrase, the server records `is_master` in Flask's session,
which is a cookie **signed** with a server-side `SECRET_KEY` (Flask signs
session cookies with an HMAC via `itsdangerous`; see the Flask documentation,
"Sessions"). Because the cookie is signed, a player cannot edit their cookie to
grant themselves `is_master` without forging the signature, which requires the
secret. The cookie is set `HttpOnly` (so page scripts cannot read it) and
`SameSite=Lax` (see 4).

**A subtle but load-bearing decision:** the `SECRET_KEY` is *persisted*. It is
read from an environment variable if present, otherwise from the database,
otherwise generated once and saved. An earlier naive approach (generating a
fresh key on every boot) would sign cookies that the next boot could not
verify, silently logging the Master out on every restart. Persisting the key is
what makes "unlock once, stay unlocked for the campaign" true across restarts.
This is documented in `auth.py:secret_key`.

### 3.4 Where authorization is enforced

Every Master route is decorated with `master_required`, which redirects an
un-unlocked request to the unlock page. Authorization is enforced **server-side per request**, never in the template. The templates *do* branch on an
`is_master` flag, but that flag only decides which links to *draw*; a template
that forgot the check would expose a link, never the data behind it, because the
route itself re-checks. This is the principle of **complete mediation**: every access to a protected object is checked, and the check is not bypassable by reaching the object through another path.

The read/write split for the interactive map is enforced *structurally*, which
is stronger than a runtime check. The player blueprint physically contains only
GET handlers; the write endpoints live in a separate master blueprint behind
`master_required`. "Players can read but never write" is therefore true *by
construction*, there is no write handler in the player code path to forget to
guard, rather than true *by an `if` branch* that a later edit might drop. This
is an application of **economy of mechanism** and **fail-safe defaults**: the safe outcome is the structural default, not a condition that must be actively maintained.

### 3.5 The first-run problem and a deliberate "fail-open"

Before any passphrase exists, there is nothing to check a login against, yet the
Master must reach the dashboard to *set* the first passphrase. The code resolves
this by having `is_master()` fall open in exactly one state: when no passphrase
is configured. This is a conscious, bounded exception to fail-safe defaults, and
it is made *visible* rather than silent, a persistent banner warns that the
Master side is open, and the UI nags until a passphrase is set.

This exception created a real, subtler leak, which is worth recording because
finding it illustrates why fail-open states must be audited wherever they
propagate. The public application guide rendered a whole "Master section"
gated on the same `is_master()` flag. During first-run fall-open, that flag is
true for *everyone*, so every player saw the Master instructions and a "Back to
the Dashboard" link, the application advertising its own privileged side.

The fix distinguishes two questions that had been conflated behind one function:

* *"Is the Master side currently reachable?"* - `is_master()`, which may
fall open during first-run so the dashboard stays reachable.
* *"Has this browser actually proven it is the Master?"* - a new,
stricter `is_master_unlocked()`, true **only** after a real passphrase
unlock, never during fall-open.

Content that would *leak information* by its mere presence (the guide's Master
section) is now gated on the stricter predicate, while the dashboard's
first-run openness - which is necessary and intended - is preserved. The general lesson, and the reason this is documented rather than quietly patched: a fail-open state is not local. Every consumer of the flag that opens must be
re-examined, because "temporarily true for everyone" means something different
to a *route guard* (acceptable: the Master must get in) than to a *content
switch* (a leak: players see the privileged side exists).

---

## 4. Request integrity: Cross-Site Request Forgery (CSRF)

### 4.1 The residual risk after `SameSite=Lax`

All state-changing actions are `POST` requests, and the session cookie is
`SameSite=Lax`. A `Lax` cookie is **not** sent on cross-site `POST`
sub-requests, so the classic cross-origin CSRF - a form on `evil.example`
auto-submitting to my `/delete/<id>` - arrives without the Master session and
is rejected outright. `SameSite` is a strong first layer and is recommended as
defense-in-depth by the OWASP *Cross-Site Request Forgery Prevention Cheat
Sheet* (2024).

However, OWASP is explicit that `SameSite` is **not sufficient on its own**. It
does not cover the *same-site* case, and this application has a same-site vector
that matters: the Master enters free-form text (handout descriptions, POI
labels, wiki bodies) that is rendered back into Master pages. Any script that
reaches the DOM on my own origin can issue *same-origin* POSTs that the browser
*will* accompany with the cookie. `SameSite` does nothing against that.

### 4.2 The chosen mechanism: a session-bound synchronizer token

I add a **synchronizer token** (OWASP's recommended primary defense). A random
secret is generated per session and stored in the signed cookie; a token is
derived from it as `HMAC-SHA256(secret, "csrf")` and must accompany every
state-changing request. The server recomputes the expected token and compares it in **constant time** using `hmac.compare_digest`, which the Python documentation recommends precisely to avoid leaking, through response timing, how many leading bytes of a guess were correct (Python `hmac` documentation).

Why this shape:

* **Session-bound, not per-form.** OWASP describes both per-session and
per-request tokens. I've chosen per-session because per-request tokens buy little in this app (there is one trusted Master, not a large multi-user surface) and would complicate the many small POST forms in the templates. The token is unpredictable and unreadable to an attacker who cannot read the Master pages, which is the property that defeats 4.1's vector.
* **Derived via HMAC, not the raw secret.** The value handed to the page is a
keyed hash of the secret, so the secret itself never leaves the signed cookie.
* **Standard library only.** The mechanism uses `hmac`, `hashlib`, and
`secrets`, no Flask-WTF. The motivation is auditability: the entire check is
a dozen lines a maintainer can read, with no framework version to track. The
cost is that I forgo features I do not need (per-field form protection,
automatic template integration). For an application this size, a mechanism you
can fully read is worth more than one you must trust blindly. (`secrets` is the
standard library's interface for cryptographically strong randomness (Python
`secrets` documentation) and is the correct source for a token that must be
unguessable.)

### 4.3 Delivery without touching every form

Threading a hidden field through every template by hand is error-prone: miss one
form and either it breaks (if the field is required) or, worse, a maintainer
later "fixes" it by weakening the check. Instead the token is emitted **once**,
in the shared `<head>` include, and delivered two ways:

1. A small script auto-injects a hidden `csrf_token` field into every `POST`
form at submit time. No individual form has to remember it, and a *new* form
cannot ship unprotected.
2. `window.fetch` is wrapped once to attach an `X-CSRF-Token` header to
same-origin, state-changing calls (the interactive map posts JSON via
`fetch`, not a form). Cross-origin requests are never given the token, and
safe methods (GET/HEAD/OPTIONS) are left untouched.

Centralizing delivery is itself a security decision: it makes "every mutation
carries the token" a property of one file, not a discipline that must be
re-applied on every future edit.

### 4.4 Safe methods are exempt by definition

Only `POST`, `PUT`, `PATCH`, and `DELETE` are checked. `GET`, `HEAD`, and
`OPTIONS` are *safe methods*, by the HTTP specification they must not carry
side effects, so they neither need nor receive CSRF validation. This is why the app's mutations were made POST routes in the first place: a GET that changed state would be both a CSRF hole and a spec violation (a link-prefetcher or crawler could trigger it).

---

## 5. Availability: rate limiting

### 5.1 The concrete vulnerability

The two player-facing polling endpoints (`/api/pop`, `/api/map/state`) call
`load_db()` on every hit, which reads and parses the whole JSON database from
disk. Nothing in the original code bounded request rate, so a client stuck in a
tight loop, a runaway script, a wedged browser tab, or someone deliberately
hammering the box, can turn that per-request disk-and-parse cost into sustained
load and starve the table's real traffic. Application-level rate limiting is the
standard first-line control for exactly this resource-exhaustion class (OWASP,
*Denial of Service Cheat Sheet*).

### 5.2 Algorithm choice: token bucket over fixed window

I implement a **token bucket**. Each client owns a bucket that refills at a steady rate up to a capacity; each request spends one token; an empty bucket yields HTTP 429.

The token bucket was chosen over the simpler **fixed-window counter** for a
specific reason. A fixed window ("N requests per 60 s") suffers the
*window-boundary burst* problem: a client can send N requests at 0:59 and N more
at 1:01, i.e. 2N in two seconds, and still be "within limit". It also punishes
honest bursts: a page that legitimately fires a few quick polls on load can trip
a tight window. The token bucket instead bounds the *average* rate (the refill
rate) while permitting a controlled burst (the capacity), which is exactly the
shape of legitimate polling occasional small bursts over a low sustained rate.
The **sliding-window log** algorithm would also avoid the boundary problem but
requires storing a timestamp per request; the token bucket needs only two
numbers per client (token count and last-update time), which matters for a
mechanism kept in memory.

### 5.3 Scope: in-memory and per-process, on purpose

The limiter is a dict of buckets guarded by a lock, held in the single server
process. It is deliberately **not** backed by a shared store (Redis, a database)
as production rate limiters often are. The justification is the deployment: the
app is one `waitress` process on one machine (see the launcher), so there is no
second process for a shared store to coordinate. Adding one would be
dependency and operational weight with no benefit here. This is a case of
matching the mechanism to the actual deployment rather than to a generic
"best practice" built for horizontally-scaled services. Memory is bounded by
pruning buckets that have been idle beyond a threshold, so the dict cannot grow
without limit.

### 5.4 The identity key and its honest limitation

Buckets are keyed by client IP (`request.remote_addr`). Two limitations are
acknowledged in the code rather than hidden:

* **Shared NAT.** Several players behind one home router may share a public IP
and thus one bucket. The limits are therefore set generously (a sustained
~5 requests/second with a 15-request burst for pollers) high enough that
several honest pollers on one IP stay comfortable, low enough that a genuine
loop is still caught. The limiter is a *resource guard, not an authentication
mechanism*, and is tuned accordingly.
* **`X-Forwarded-For` is deliberately not trusted.** On this LAN deployment
there is no reverse proxy setting that header, so honoring it would let any
client spoof its identity and dodge the limit by forging the header. The code
reads the peer address directly. The one place to revisit if the app is ever
put behind a real proxy is noted inline: only a *trusted* proxy's forwarded
header should ever be believed (this is the well-known `X-Forwarded-For`
spoofing caveat).

### 5.5 Policy tiers

Two policies are defined declaratively: a tight one for the DB-touching pollers
and a loose ceiling for everything else (page loads, Master actions), which
exists only to cap absurd floods without interfering with human navigation.
Static files are exempt entirely, they do not touch the database and the server
serves them cheaply. On exceeding a limit the server returns **429 Too Many
Requests** with a `Retry-After` header, both as specified by RFC 6585 (which
defines 429) and RFC 7231 7.1.3 (which defines `Retry-After`), so a
well-behaved client knows to back off and for how long.

---

## 6. Defense in depth: secondary controls

### 6.1 Baseline response headers

Every response carries three static headers, each closing a distinct
browser-side vector (all from the OWASP *Secure Headers Project*):

* `X-Content-Type-Options: nosniff` stops a browser from MIME-sniffing an
uploaded file into something executable, relevant because the app serves
user-uploaded images and PDFs.
* `X-Frame-Options: DENY` prevents the Master controls from being framed by
another page, defeating clickjacking.
* `Referrer-Policy: strict-origin-when-cross-origin` keeps the LAN URL out of
the `Referer` header on any outbound request.

### 6.2 Why there is no Content-Security-Policy (yet)

A Content-Security-Policy is the strongest browser-side control against
injected script, and its absence is a *known, documented gap* rather than an
oversight. The app currently loads fonts from Google Fonts and uses inline
`<style>`/`<script>` in several templates. A CSP strict enough to be worth
having (one that forbids inline script) would require threading a per-response
nonce through every inline block on every page, a substantial change. A
*permissive* CSP that allowed `unsafe-inline` would pass a scanner while
providing almost no real protection, i.e. security theater. The honest choice is
to ship the cheap, effective headers now and track the CSP as future work here,
rather than bolt on a policy that looks like protection without being it.

### 6.3 The debugger: an availability-for-safety default flip

The development entry point previously ran with Flask's interactive debugger
enabled. That debugger executes **arbitrary code** on any request that raises an
exception (Werkzeug documentation, "Debugging Applications", which warns it must
never be used in production because it "allows execution of arbitrary code").
On a LAN-reachable port that is a remote-code-execution hole. The default is now
*off*; the debugger is opt-in via an explicit environment variable, to be set
only on a trusted machine during development. The production launcher runs the
app under `waitress`, not this entry point, so the safe default aligns with the
intended deployment.

### 6.4 Input validation already present

The pre-existing code already validated untrusted input well, and that work is
part of the security posture:

* Uploaded filenames pass through Werkzeug's `secure_filename`, and stored
names are rebuilt from a server-generated handout ID plus an extension from a
whitelist so a crafted filename cannot escape the uploads directory (a
path-traversal defense; cf. OWASP, *Path Traversal*).
* The map's fog colour is validated against a strict hex pattern before being
written into CSS, so a value cannot smuggle arbitrary style or markup.
* Map dimensions, point-of-interest counts, label lengths, and scale factors
are all clamped to sane bounds, so a malformed or padded client payload cannot
ask the browser to render millions of elements a client-side
resource-exhaustion guard that complements 5.

These are noted so the reader sees the CSRF and rate-limiting work as *additions
to* an already-careful codebase, not as the whole of its security.

---

## 7. Residual risks and honest limitations

A security document that claims no gaps is not credible. The following are known
and accepted, each with its justification:

1. **Plain HTTP.** Traffic is unencrypted. Anyone who can already sniff the LAN
can read handouts and capture the session cookie. This is accepted per the
2.2 trust boundary: the app targets a trusted home network, and transport
security is the deployment's responsibility (a reverse proxy terminating TLS,
or network isolation).
2. **No CSP.** See 6.2. Tracked as future work.
3. **Shared-passphrase model.** No per-person revocation or audit trail. Correct
for a single-Master table (3.1); would be wrong for a multi-admin tool.
4. **IP-based rate-limit identity.** Coarse under shared NAT (5.4). Acceptable
because the limiter guards resources, not identity.
5. **Same-origin XSS would defeat CSRF.** The synchronizer token stops a script
that *cannot* read the Master pages. A stored-XSS bug that let an attacker run
script *on* a Master page could read the token. The mitigation is to prevent
that XSS in the first place: Jinja auto-escaping is on by default, and the
few `|safe` uses are audited to carry only server-built CSS/URLs, never user
input (documented at each call site). CSP (6.2) would add a second layer.

---

## 8. Summary of decisions

| Decision | Chosen | Rejected alternative | Primary reason |
| --- | --- | --- | --- |
| Identity | One shared passphrase | Per-user accounts | Smallest mechanism for one real role (3.1) |
| Passphrase storage | Salted PBKDF2 hash | Plain / bare hash | NIST SP 800-63B, OWASP (3.2) |
| Session | Signed `HttpOnly` `Lax` cookie | Unsigned / readable | Unforgeable without secret (3.3) |
| Authorization | Per-route server check + structural read/write split | Template-only gating | Complete mediation (3.4) |
| First-run | Visible, bounded fail-open + stricter predicate for content | Silent fail-open everywhere | Fail-open must not leak (3.5) |
| CSRF | Stdlib HMAC synchronizer token | Flask-WTF / SameSite alone | Auditable; `Lax` insufficient same-site (4) |
| Rate limiting | In-memory token bucket per IP | Fixed window / Redis-backed | Bounds average, allows burst; matches single-process deploy (5) |
| Debugger | Off by default, opt-in | On in dev entry point | Debugger = RCE if reachable (6.3) |
| CSP | Deferred, documented | Permissive `unsafe-inline` CSP | Avoid security theater (6.2) |

---

## References

* J. H. Saltzer and M. D. Schroeder, "The Protection of Information in Computer
Systems," *Proceedings of the IEEE*, vol. 63, no. 9, 1975. (Complete
mediation; economy of mechanism; fail-safe defaults.)
* OWASP Foundation, *Cross-Site Request Forgery Prevention Cheat Sheet*, 2024.
[https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
* OWASP Foundation, *Denial of Service Cheat Sheet*.
[https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html)
* OWASP Foundation, *Password Storage Cheat Sheet*.
* OWASP Foundation, *Secure Headers Project*. [https://owasp.org/www-project-secure-headers/](https://owasp.org/www-project-secure-headers/)
* OWASP Foundation, *Path Traversal*.
* NIST, *Special Publication 800-63B: Digital Identity Guidelines
Authentication and Lifecycle Management*. [https://pages.nist.gov/800-63-3/sp800-63b.html](https://pages.nist.gov/800-63-3/sp800-63b.html)
* R. Fielding and J. Reschke (eds.), *RFC 7231: HTTP/1.1 Semantics and Content*. [https://www.rfc-editor.org/rfc/rfc7231](https://www.rfc-editor.org/rfc/rfc7231)
* M. Nottingham and R. Fielding, *RFC 6585: Additional HTTP Status Codes*. [https://www.rfc-editor.org/rfc/rfc6585](https://www.rfc-editor.org/rfc/rfc6585)
* D. Hardt (ed.), *RFC 6749: The OAuth 2.0 Authorization Framework*. [https://www.rfc-editor.org/rfc/rfc6749](https://www.rfc-editor.org/rfc/rfc6749)
* Pallets Projects, *Flask Documentation* "Sessions" and security
considerations. [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
* Pallets Projects, *Werkzeug Documentation* - "Debugging Applications"
(debugger warning) and `security` helpers. [https://werkzeug.palletsprojects.com/](https://werkzeug.palletsprojects.com/)
* Python Software Foundation, *Python Documentation* - `hmac` (constant-time
compare) and `secrets` (cryptographic tokens).
[https://docs.python.org/3/library/hmac.html](https://docs.python.org/3/library/hmac.html) · [https://docs.python.org/3/library/secrets.html](https://docs.python.org/3/library/secrets.html)

*This document describes the state of the application's security design as of
the changes that introduced `handouts/security.py`. Sections 6.2 (CSP) and the
items in 7 are the maintained list of known future work.*