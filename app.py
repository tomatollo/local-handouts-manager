"""Local Handouts Manager — application entry point.

Thin by design: it builds the Flask app, wires up the cross-cutting concerns
every template needs (language, theme, and who is looking), and registers the
player, master and wiki blueprints. All data logic lives in the `handouts`
package.
"""

from ast import Not
from datetime import timedelta

from flask import Flask, app, g, render_template, request
from jinja2 import pass_context

from handouts import auth, i18n, storage, theming
from handouts.routes_player import bp as player_bp
from handouts.routes_master import bp as master_bp


def create_app():
    app = Flask(__name__)

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

    @app.after_request
    def _persist_language(response):
        if getattr(g, 'lang_changed', False):
            response.set_cookie(i18n.COOKIE_NAME, g.lang,
                                max_age=i18n.COOKIE_MAX_AGE, samesite='Lax')
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

    @app.context_processor
    def _ui_context():
        # The theme is global (master-chosen), so it's read from the DB rather
        # than the request. Both are needed by every page's <head>.
        db = storage.load_db()
        theme = storage.get_theme(db)
        # `is_master` drives which nav entries a page offers. It is a UI hint
        # ONLY: every master route enforces the same check server-side via
        # auth.master_required, so a template that forgot the condition would
        # expose a link, never the data behind it.
        return {
            'lang': g.lang,
            'languages': i18n.LANGUAGES,
            'theme_css': theming.css_vars(theme),
            'theme_fonts_url': theming.fonts_url(theme),
            'is_master': auth.is_master(),
            # True until a passphrase exists: the master side is open, and the
            # dashboard says so rather than pretending to be secure.
            'first_run': not auth.is_configured(db),
        }

    app.register_blueprint(player_bp)
    app.register_blueprint(master_bp)

    @app.route('/guide')
    def app_guide():
        return render_template('guide.html')

    from flask import render_template

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', 
            error_code=400,
            error_type_en="Bad Request",
            error_icon="💥",
            error_title="Wild Magic Surge",
            error_msg="You mixed up the spell components. Your request fizzled out in a shower of harmless sparks."
        ), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('error.html', 
            error_code=401,
            error_type_en="Unauthorized",
            error_icon="🛑",
            error_title="Failed Stealth Check",
            error_msg="'Halt! Who goes there?' The guards caught you trying to sneak in without the proper passphrase."
        ), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', 
            error_code=403,
            error_type_en="Forbidden",
            error_icon="🛡️",
            error_title="Magic Circle",
            error_msg="A powerful barrier blocks your path. You lack the required alignment or level to enter this area."
        ), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', 
            error_code=404,
            error_type_en="Not Found",
            error_icon="🎲",
            error_title="Critical Fail",
            error_msg="Natural 1 on Perception, you got lost. The room is shrouded in darkness, and the page you are looking for seems to have vanished into the Astral Plane or been devoured by a Mimic."
        ), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', 
            error_code=500,
            error_type_en="Internal Server Error",
            error_icon="⚡",
            error_title="The Weave is Tearing",
            error_msg="The Dungeon Master spilled coffee on the campaign notes. The fabric of reality is temporarily unstable."
        ), 500

    from flask import abort

    # ROTTA TEMPORANEA PER TESTARE GLI ERRORI
    @app.route('/test-error/<int:code>')
    def test_error(code):
        # La funzione abort interrompe la richiesta e lancia l'errore HTTP specificato
        abort(code)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


