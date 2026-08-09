"""Theme logic: id validation, picker data, and the CSS/error/font output.

This is the only theming module that imports Markup, because everything it
returns is CSS, URL, or attribute text going into a template, which Jinja's HTML
autoescaping would corrupt. The theme data itself (palettes, fonts, error copy)
lives in themes/ as plain Theme records; this module only reads them.

Public surface (re-exported by theming/__init__.py, which is what the app
imports): clean_theme, theme_list, theme_groups, theme_preview_style, css_vars,
theme_errors, theme_home_label, fonts_url, all_fonts_url. The id-based fonts_url
/ no-arg all_fonts_url here wrap the Theme-object helpers in fonts.py, so
callers keep passing a string id / no argument exactly as the old single module
accepted.
"""

from markupsafe import Markup

from .base import ERROR_TYPE_EN
from .groups import THEME_GROUPS
from .themes import THEMES, ALL_THEMES
from .fonts import fonts_url_for_theme, all_fonts_url_for

DEFAULT_THEME = 'dungeon-torch'


def clean_theme(raw):
    """Return a known theme id, falling back to the default for junk input."""
    raw = (raw or '').strip().lower()
    return raw if raw in THEMES else DEFAULT_THEME


def _theme(theme_id):
    """The Theme record for an id (cleaned first), never KeyError."""
    return THEMES[clean_theme(theme_id)]


def _card(theme):
    """The {id, name, blurb} dict the picker templates iterate."""
    return {'id': theme.id, 'name': theme.name, 'blurb': theme.blurb}


def theme_list():
    """Themes as [{id, name, blurb}], default first then alphabetical."""
    rest = sorted((t for t in THEMES.values() if t.id != DEFAULT_THEME),
                  key=lambda t: t.name.lower())
    return [_card(THEMES[DEFAULT_THEME])] + [_card(t) for t in rest]


def theme_groups():
    """Themes grouped for the picker: [{label, themes: [{id, name, blurb}]}].

    Reads THEME_GROUPS for labels + membership, then appends any theme no group
    named to the LAST group -- so a newly added non-D&D preset shows up under
    "Other Universes" without touching groups.py. Within a group the ids keep
    THEME_GROUPS order, except DEFAULT_THEME which is floated to the front of
    whichever group holds it. Empty groups are dropped so a label with nothing
    under it never renders a bare heading.
    """
    assigned = {tid for _, ids in THEME_GROUPS for tid in ids}
    leftover = [tid for tid in THEMES if tid not in assigned]

    groups = []
    last = len(THEME_GROUPS) - 1
    for i, (label, ids) in enumerate(THEME_GROUPS):
        # Keep only ids that really exist (guards a typo or a removed theme
        # lingering in the group list), preserving their order.
        members = [tid for tid in ids if tid in THEMES]
        if i == last:
            members += leftover
        if DEFAULT_THEME in members:
            members = [DEFAULT_THEME] + [t for t in members if t != DEFAULT_THEME]
        if not members:
            continue
        groups.append({
            'label': label,
            'themes': [_card(THEMES[tid]) for tid in members],
        })
    return groups


# The colour tokens a preview swatch carries verbatim from the theme. The two
# font faces are handled separately below because they become differently-named
# custom properties, not copied as-is.
_PREVIEW_KEYS = ('--bg', '--bg-panel', '--ink', '--ink-dim',
                 '--accent', '--accent-2', '--border')


def theme_preview_style(theme_id):
    """Inline `style` value that dresses one picker box in its own theme.

    Emits the colour custom properties plus `--preview-font-display` /
    `--preview-font-body` (that theme's two faces) and `--preview-scale` (its
    heading correction). The picker CSS reads those on `.theme-choice--preview`
    so each box's name and blurb render in the theme's ACTUAL typefaces + size,
    not the page's. (Needs every theme's font loaded; see all_fonts_url, which
    the Appearance template links for exactly that.)

    Markup because it is CSS going into an attribute; values are fixed strings
    from the theme table, never user input.
    """
    theme = _theme(theme_id)
    parts = [f'{k}: {theme.vars[k]}' for k in _PREVIEW_KEYS if k in theme.vars]
    # Same fallbacks as css_vars, so a box still reads if a face fails to load.
    parts.append(f"--preview-font-display: '{theme.display_font}', Georgia, serif")
    parts.append(f"--preview-font-body: '{theme.body_font}', Georgia, serif")
    parts.append(f"--preview-scale: {theme.scale}")
    return Markup('; '.join(parts) + ';')


def css_vars(theme_id):
    """The theme's :root override block, ready to drop into a <style> tag.

    Markup because this is CSS, not HTML: autoescaping would rewrite the quotes
    around font names to `&#39;`, an invalid font-family value, so the browser
    would drop those declarations and keep the default face.

    A theme may also carry `extra_css`: rules that go BEYOND repainting tokens
    (textures, animations, per-component tweaks). It is appended after the
    :root block and emitted ONLY when that theme is active -- css_vars is always
    called with the current theme -- so no `[data-theme=...]` guard is needed
    and other themes never pay for it.
    """
    theme = _theme(theme_id)
    lines = [f'  {k}: {v};' for k, v in theme.vars.items()]
    # Fallbacks keep text readable if Google Fonts is unreachable (a self-hosted
    # app on a table's Wi-Fi may well have no internet).
    lines.append(f"  --font-display: '{theme.display_font}', Georgia, serif;")
    lines.append(f"  --font-body: '{theme.body_font}', Georgia, serif;")
    lines.append(f"  --display-scale: {theme.scale};")
    # The stepped heading shadow only reads as pixel-art under a pixel face;
    # under a blackletter or serif it just looks smudged.
    if theme.display_font != 'Press Start 2P':
        lines.append('  --display-shadow: none;')
    block = ':root {\n' + '\n'.join(lines) + '\n}'
    if theme.extra_css:
        block += '\n' + theme.extra_css.strip() + '\n'
    return Markup(block)


def fonts_url(theme_id):
    """Google Fonts URL carrying just the two faces this theme needs.

    Id-based public wrapper over fonts.fonts_url_for_theme, so switching themes
    never makes a page download every face in the table. Markup: the `&`
    separators are URL syntax Jinja would escape to `&amp;` and break.
    """
    return fonts_url_for_theme(_theme(theme_id))


def all_fonts_url():
    """Google Fonts URL carrying EVERY face used by any theme.

    No-argument public wrapper over fonts.all_fonts_url_for(ALL_THEMES). Only
    the Appearance page links this: the picker previews each box in its own
    typeface, so it needs them all at once. Markup, same reason as fonts_url.
    """
    return all_fonts_url_for(ALL_THEMES)


def theme_errors(theme_id, code):
    """Return (icon, title, msg, type_en) for one theme + HTTP status code.

    Looks up the active theme's error set, falling back to DEFAULT_THEME for
    any theme (or any individual status) that hasn't defined its own copy, so
    every page renders a sensible error even before a new theme's wording is
    written. `type_en` comes from ERROR_TYPE_EN, keyed by status alone. A
    completely unknown status falls back to 500's set.
    """
    code = int(code)
    theme = _theme(theme_id)
    default = THEMES[DEFAULT_THEME]
    entry = theme.errors.get(code)
    if entry is None:
        # This theme doesn't define this code: try the default theme, then 500.
        entry = default.errors.get(code) or default.errors[500]
    icon, title, msg = entry
    type_en = ERROR_TYPE_EN.get(code, ERROR_TYPE_EN[500])
    return icon, title, msg, type_en


def theme_home_label(theme_id):
    """The in-character 'back home' button label for a theme's error page.

    Returns the theme's own home_label, falling back to the default theme's
    label when a theme leaves it blank -- same fallback shape as theme_errors,
    so a new theme still shows a sensible button before its own wording is
    written. The returned string is English and is run through the |t filter in
    error.html, so an Italian entry in the i18n catalogue translates it.
    """
    theme = _theme(theme_id)
    return theme.home_label or THEMES[DEFAULT_THEME].home_label
