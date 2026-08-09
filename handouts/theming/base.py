"""The Theme value object + the shared HTTP-status error type labels.

A theme is a small, typed record. It exists to make each theme file below
declare the same fields in the same order, so adding a preset is filling in a
blank form rather than copying a dict and hoping you matched the shape. The
registry (theming/registry.py) turns a list of these into the THEMES table the
rest of the app reads through the package's public API.

Nothing here touches Flask or Markup: a Theme is pure data + two tiny helpers
that format its own fonts/vars. The Markup-wrapped, template-facing functions
(css_vars, fonts_url, ...) live in the registry, which is the only module that
imports markupsafe. That keeps this file importable from a plain script or a
test with no web stack in sight.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Theme:
    """One UI preset: a palette, two fonts, a heading scale, optional extra CSS.

    Fields
    ------
    id      : the url/DB slug, e.g. 'curse-of-strahd'. Unique; it is the key
              the DB stores and the picker submits.
    name    : the human label shown in the picker ('Curse of Strahd').
    blurb   : one line under the name in the picker.
    fonts   : (display, body) -- the heading face and the long-text face. Both
              are Google Fonts family names; see theming/fonts.py for how they
              become a stylesheet URL.
    scale   : multiplies every heading size. The base CSS is calibrated for
              Press Start 2P (wide + short for its point size); a normal display
              face at the same size looks tiny, so each theme states its own
              correction. Press-Start themes use 1; blackletters go up to ~1.9.
    vars    : the CSS custom-property overrides ({'--bg': '#..', ...}). These
              repaint the tokens already declared on :root in style.css; the
              stylesheet stays the single source of layout truth.
    extra_css : optional raw CSS appended AFTER the :root block, only when this
              theme is active. For textures, animations and per-component
              tweaks that go beyond repainting tokens. Keep selectors real
              (.panel, .btn, body::before, ...) and wrap motion in
              `prefers-reduced-motion: no-preference`. Empty string = none.

    errors  : optional {status_code: (icon, title, msg)} for themed error
              pages. Any code a theme omits (or a theme with errors={}) falls
              back to the default theme's wording; see theming/registry.py's
              theme_errors(). Kept on the theme so a preset's whole identity --
              palette, fonts, and its 404 joke -- lives in one file.
    home_label : optional in-character label for the "back home" button on the
              error page, e.g. 'Flee the Dungeon (Home)' for Dungeon Torch or
              'Return to Base' for Military Terminal. Empty string means "use
              the default theme's label"; see registry.theme_home_label(). It
              is an English source string run through the |t filter in the
              template, so an Italian entry in the i18n catalogue translates it,
              exactly like a theme's error titles.
    """

    id: str
    name: str
    blurb: str
    fonts: tuple  # (display, body)
    scale: float
    vars: dict
    extra_css: str = ''
    errors: dict = field(default_factory=dict)
    home_label: str = ''

    @property
    def display_font(self):
        return self.fonts[0]

    @property
    def body_font(self):
        return self.fonts[1]


# The English "type" label per HTTP status, shown as `<label> / <code>` in
# error.html. Fixed per code (never per theme), so it lives here once and is
# read by registry.theme_errors().
ERROR_TYPE_EN = {
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
}
