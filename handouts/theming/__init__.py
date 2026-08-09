"""UI themes: colour + font presets, one module per theme.

This package replaces the former single theming.py. Its public surface is
unchanged, so the rest of the app keeps calling `theming.css_vars(...)`,
`theming.fonts_url(...)`, etc. exactly as before -- only the internals are split
up:

    base.py        the Theme dataclass + the fixed ERROR_TYPE_EN labels
    themes/        one module per preset (its palette, fonts, extra_css,
                   and error copy), gathered into THEMES by themes/__init__.py
    groups.py      which family each theme belongs to in the picker
    fonts.py       Google Fonts URL building (Theme-object helpers)
    registry.py    the logic: clean_theme, theme_list, theme_groups,
                   theme_preview_style, css_vars, theme_errors,
                   theme_home_label, and the id-based fonts_url / all_fonts_url
                   wrappers

A theme is nothing but an override of the CSS custom properties already
declared on :root in style.css, injected as a small <style> block. The
stylesheet stays the single source of layout truth (and stays mobile-first);
themes only repaint it. The 8-bit look survives a font swap because it lives in
the hard borders and stepped shadows, not in the typeface.

Unlike language, the theme is GLOBAL: the Master picks it and players see it
too, so the whole table shares one look. It lives in the DB under `settings`.

To add a theme, see docs/THEMES.md. The short version: drop a module in themes/,
list its module name in themes/__init__._ORDER, and add its id to a family in
groups.py. Nothing here needs editing.
"""

# Data tables, re-exported so `theming.THEMES` / `theming.DEFAULT_THEME` keep
# working for any caller (and template) that read them directly.
from .themes import THEMES, ALL_THEMES
from .base import Theme, ERROR_TYPE_EN
from .groups import THEME_GROUPS
from .fonts import FONT_QUERY
from .registry import (
    DEFAULT_THEME,
    clean_theme,
    theme_list,
    theme_groups,
    theme_preview_style,
    css_vars,
    theme_errors,
    theme_home_label,
    fonts_url,
    all_fonts_url,
)

__all__ = [
    'THEMES', 'ALL_THEMES', 'Theme', 'ERROR_TYPE_EN', 'THEME_GROUPS',
    'FONT_QUERY', 'DEFAULT_THEME', 'clean_theme', 'theme_list', 'theme_groups',
    'theme_preview_style', 'css_vars', 'theme_errors', 'theme_home_label',
    'fonts_url', 'all_fonts_url',
]
