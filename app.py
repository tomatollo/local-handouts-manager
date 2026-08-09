"""Local Handouts Manager - application entry point.

Thin by design: it builds the Flask app, wires up the cross-cutting concerns
every template needs (language, theme, who is looking, and the CSRF token), and
registers the player and master blueprints. All data logic lives in the
`handouts` package; the security primitives (CSRF + rate limiting) live in
`handouts/security.py`.
"""

from datetime import timedelta

from flask import Flask, g, has_app_context, render_template, request
from jinja2 import pass_context

from handouts import auth, i18n, storage, theming, security
from handouts.routes_player import bp as player_bp
from handouts.routes_master import bp as master_bp


def create_app():
    app = Flask(__name__)

    # Give storage a per-request DB cache backed by flask.g, so the several
    # before_request hooks + the context processor + the view share ONE read
    # and parse of database.json instead of re-reading it on every call. The
    # hooks live here (not in storage) so storage keeps no Flask dependency and
    # still works from the CLI, where the cache is simply never installed.
    # g is request-scoped, so nothing leaks between requests.
    #
    # Both hooks tolerate being called with no application context: load_db is
    # invoked once during create_app() itself (auth.secret_key below), before
    # any request exists, and touching g there would raise. `has_app_context`
    # makes those calls fall through to a normal disk read instead.
    def _db_cache_get():
        if not has_app_context():
            return None
        return getattr(g, '_db_cache', None)

    def _db_cache_set(db):
        if has_app_context():
            g._db_cache = db

    storage.set_request_cache_hooks(_db_cache_get, _db_cache_set)

    # Signs the session cookie that carries the Master's unlocked state. It is
    # read once at boot from the env or the DB (auth.secret_key persists a
    # generated one), because a key that changed per boot would log the Master
    # out on every restart.
    app.config['SECRET_KEY'] = auth.secret_key(storage.load_db())
    # The Master unlocks once and expects to stay unlocked across a campaign's
    # worth of sessions, not to be asked again mid-game.
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    @app.before_request
    def _pick_language():
        # Per-user, cookie-backed. `?lang=` is an explicit click and wins;
        # remember it so the next request doesn't need the querystring.
        g.lang, g.lang_changed = i18n.resolve(request)

    @app.before_request
    def _rate_limit():
        # Guard against request-loop DoS. The player pollers hit the DB on
        # every call, so they get the tighter 'poll' policy; everything else
        # gets a loose ceiling. Static files are exempt: they don't touch the
        # DB and the dev server/waitress serve them cheaply. See security.py.
        if request.endpoint == 'static':
            return
        poll_paths = ('/api/pop', '/api/map/state', '/api/map/reveal.png')
        policy = 'poll' if request.path in poll_paths else 'default'
        security.enforce(policy)

    @app.before_request
    def _csrf_protect():
        # Reject state-changing requests that lack a valid per-session token.
        # Safe methods (GET/HEAD/OPTIONS) pass straight through. See security.py.
        security.validate_request()

    @app.after_request
    def _security_headers(response):
        if getattr(g, 'lang_changed', False):
            response.set_cookie(i18n.COOKIE_NAME, g.lang,
                                max_age=i18n.COOKIE_MAX_AGE, samesite='Lax')
        # Baseline hardening headers. These are cheap, static, and defend the
        # whole app at once:
        #   * nosniff stops a browser from MIME-guessing an uploaded file into
        #     something executable (OWASP Secure Headers Project).
        #   * DENY framing blocks clickjacking of the master controls.
        #   * A conservative referrer policy keeps the LAN URL out of any
        #     external request's Referer.
        # A full Content-Security-Policy is intentionally NOT set here: the app
        # loads its fonts from Google Fonts and uses inline <style>/<script> in
        # several templates, so a strict CSP would need nonces threaded through
        # every page -- a larger change tracked in SECURITY.md rather than
        # bolted on half-done (a permissive CSP would be security theatre).
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy',
                                    'strict-origin-when-cross-origin')
        retry_after = getattr(g, 'rate_limited_retry_after', None)
        if retry_after:
            response.headers['Retry-After'] = str(retry_after)
        return response

    # `|t` is the only translation entry point templates use.
    #
    # @pass_context is load-bearing, not decoration. Every call site passes a
    # string literal ({{ 'Browse' | t }}), and Jinja constant-folds filters it
    # believes are pure: it would run `t` once at compile time and bake that
    # one language into the cached template, serving it to every later request
    # regardless of their cookie. Taking the context marks the filter as
    # context-dependent, so it is evaluated per render instead.
    @pass_context
    def translate_filter(_ctx, text):
        return i18n.translate(text, g.lang)

    app.add_template_filter(translate_filter, 't')

    # Last-modified date of a template file, formatted for the footer. Templates
    # call {{ page_modified('master/dashboard.html') }} to show when that page's
    # file was last edited/maintained. Reads the mtime lazily and tolerates a
    # missing file (returns None) so a footer include never breaks a page.
    import os
    from datetime import datetime, timezone

    def _page_modified(template_name, fmt='%Y-%m-%d'):
        try:
            path = os.path.join(app.root_path, app.template_folder, template_name)
            ts = os.path.getmtime(path)
            return datetime.fromtimestamp(ts, timezone.utc).strftime(fmt)
        except OSError:
            return None

    app.jinja_env.globals['page_modified'] = _page_modified

    @app.context_processor
    def _ui_context():
        # The theme is global (master-chosen), so it's read from the DB rather
        # than the request. Both are needed by every page's <head>.
        db = storage.load_db()
        theme = storage.get_theme(db)
        # The player-hub welcome header, resolved to one title + subtitle for
        # this render (a random line when the Master enabled random and gave a
        # list, else the first / their single text; None where they left it
        # default, which the hub template turns into the translatable default).
        welcome = storage.pick_welcome(db)
        # `is_master` drives which nav entries a page offers. It is a UI hint
        # ONLY: every master route enforces the same check server-side via
        # auth.master_required, so a template that forgot the condition would
        # expose a link, never the data behind it.
        return {
            'lang': g.lang,
            'languages': i18n.LANGUAGES,
            # The active theme id, exposed so templates can special-case a
            # specific look (e.g. the footer's Curse of Strahd easter egg).
            'theme': theme,
            'theme_css': theming.css_vars(theme),
            'theme_fonts_url': theming.fonts_url(theme),
            # Resolved welcome header (see above). A dict {title, subtitle};
            # either may be None, meaning "use the template's default".
            'welcome': welcome,
            'is_master': auth.is_master(),
            # Stricter than is_master: true only after a real passphrase
            # unlock, never during first-run fall-open. Used by pages that
            # render master-only *content* (e.g. the public guide) so they
            # don't advertise the master side to an un-unlocked visitor.
            'master_unlocked': auth.is_master_unlocked(),
            # True until a passphrase exists: the master side is open, and the
            # dashboard says so rather than pretending to be secure.
            'first_run': not auth.is_configured(db),
            # Per-session CSRF token for every POST form + the fetch() header.
            'csrf_token': security.get_token(),
            # Folders + tags are provided globally so the shared player
            # navigation drawer (templates/player/_drawer.html) renders its
            # Folders/Tags shortcuts on EVERY page, including ones whose route
            # doesn't build them (map, guide, qr). A route that passes its own
            # `folders`/`tags` to render_template still overrides these, since
            # explicit template args win over context-processor values -- so
            # the hub and folder pages keep passing their already-filtered
            # lists and nothing changes for them.
            'folders': storage.all_folders(db),
            # Tags for the shared browse drawer. Players must only ever see
            # tags that belong to a VISIBLE handout -- a tag living solely on a
            # hidden handout would leak that unrevealed material exists. The
            # master sees every tag so they can still organise drafts. A route
            # that passes its own already-filtered `tags` still overrides this.
            'tags': storage.all_tags(db, only_visible=not auth.is_master()),
        }

    app.register_blueprint(player_bp)
    app.register_blueprint(master_bp)

    @app.route('/guide')
    def app_guide():
        return render_template('guide.html')

    @app.route('/qr')
    def qr_page():
        # A page that shows a QR code pointing at the player home, so people at
        # the table can join by scanning instead of typing an IP. The URL is
        # built client-side from window.location, so it carries whatever LAN
        # address the Master opened this page with (not localhost). Reachable
        # from both sides; it only ever reveals the already-public player URL.
        return render_template('qr.html')

    # Tiny liveness endpoint the footer polls to show Online/Offline. Returns
    # 204 No Content: cheapest possible "yes, the server is up" answer.
    @app.route('/ping')
    def ping():
        return ('', 204)

    from flask import render_template

    def _render_error(code):
        # Pick the wording for the ACTIVE theme (master-chosen, global). Falls
        # back to the default theme's set inside theming.theme_errors() when a
        # theme hasn't defined its own copy, so this never blows up.
        theme = storage.get_theme(storage.load_db())
        icon, title, msg, type_en = theming.theme_errors(theme, code)
        return render_template('error.html',
            error_code=code,
            error_type_en=type_en,
            error_icon=icon,
            error_title=title,
            error_msg=msg,
            # The theme's in-character "back home" button label (falls back to
            # the default theme's when a theme leaves it blank).
            error_home_label=theming.theme_home_label(theme),
        ), code

    @app.errorhandler(400)
    def bad_request(e):
        return _render_error(400)

    @app.errorhandler(401)
    def unauthorized(e):
        return _render_error(401)

    @app.errorhandler(403)
    def forbidden(e):
        return _render_error(403)

    @app.errorhandler(404)
    def page_not_found(e):
        return _render_error(404)

    @app.errorhandler(500)
    def internal_server_error(e):
        return _render_error(500)

    @app.errorhandler(429)
    def too_many_requests(e):
        return _render_error(429)

    return app

app = create_app()

if __name__ == '__main__':
    import os
    # debug is OFF by default: the Werkzeug debugger exposes an interactive
    # console that runs arbitrary code on any request that errors, which is a
    # remote-code-execution hole if the port is reachable. Opt in explicitly
    # with HANDOUTS_DEBUG=1 only on a machine you trust, never for the LAN
    # server the players reach. (Werkzeug docs, "Debugging Applications".)
    debug = os.environ.get('HANDOUTS_DEBUG', '').strip() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=8000, debug=debug)
