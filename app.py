"""Local Handouts Manager — application entry point.

Thin by design: it builds the Flask app, wires up the cross-cutting concerns
every template needs (language + theme), and registers the player and master
blueprints. All data logic lives in the `handouts` package.
"""

from flask import Flask, g, request
from jinja2 import pass_context

from handouts import i18n, storage, theming
from handouts.routes_player import bp as player_bp
from handouts.routes_master import bp as master_bp


def create_app():
    app = Flask(__name__)

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
        theme = storage.get_theme(storage.load_db())
        return {
            'lang': g.lang,
            'languages': i18n.LANGUAGES,
            'theme_css': theming.css_vars(theme),
            'theme_fonts_url': theming.fonts_url(theme),
        }

    app.register_blueprint(player_bp)
    app.register_blueprint(master_bp)
    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
