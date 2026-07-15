"""UI themes: colour + font presets inspired by official D&D campaigns.

The two template-facing helpers (css_vars, fonts_url) return Markup, since
both emit CSS/URL syntax that Jinja's HTML autoescaping would corrupt. Every
value comes from the fixed table below, never from user input.

A theme is nothing but an override of the CSS custom properties already
declared on :root in style.css, injected as a small <style> block. The
stylesheet stays the single source of layout truth (and stays mobile-first);
themes only repaint it. The 8-bit look survives a font swap because it lives
in the hard borders and stepped shadows, not in the typeface.

Unlike language, the theme is GLOBAL: the Master picks it and players see it
too, so the whole table shares one look. It lives in the DB under `settings`.
"""

from markupsafe import Markup

# Every theme overrides the same token set, so switching can never leave a
# half-painted UI. `fonts` is (display, body): the heading face and the
# long-text face. Both are pulled from Google Fonts by fonts_url().
#
# `scale` multiplies every heading size. The CSS is calibrated for Press Start
# 2P, which is wide and short for its point size; a normal display face at the
# same size looks tiny, so each theme states its own correction.
#
# Note on --ink: most themes are dark (light ink on dark panel). Phandelver is
# the one parchment theme, so its ink is dark on a light panel. Everything
# reads from these tokens, so both directions work without special-casing.
THEMES = {
    'dungeon-torch': {
        'name': 'Dungeon Torch',
        'blurb': 'The default: soot, torchlight, and pixels.',
        'fonts': ('Press Start 2P', 'IM Fell English'),
        'scale': 1,
        'vars': {
            '--bg': '#1a1614',
            '--bg-panel': '#2a2320',
            '--ink': '#f4e9d8',
            '--ink-dim': '#b9a78d',
            '--accent': '#e8a83a',
            '--accent-2': '#c0532b',
            '--border': '#0d0b0a',
            '--shadow': '#000000',
            '--good': '#6a9c4f',
        },
    },
    'phandelver': {
        'name': 'Lost Mine of Phandelver',
        'blurb': 'Classic fantasy: forest, parchment, goblin country.',
        'fonts': ('MedievalSharp', 'Merriweather'),
        'scale': 1.6,
        'vars': {
            # The one light theme: aged parchment panels, dark brown ink.
            '--bg': '#1a3300',
            '--bg-panel': '#1e2117',
            '--ink': '#e2dec3',
            '--ink-dim': '#9c9477',
            '--accent': '#499149',
            '--accent-2': '#b8913e',
            '--border': '#090b07',
            '--shadow': '#000000',
            '--good': '#5a8c46',
        },
    },
    'tiamat': {
        'name': 'The Rise of Tiamat',
        'blurb': 'Draconic majesty: scale-grey, crimson, and gold hoards.',
        'fonts': ('Cinzel', 'Playfair Display'),
        'scale': 1.5,
        'vars': {
            '--bg': '#141517',          # metallic dragon-scale anthracite
            '--bg-panel': '#221818',    # dark crimson
            '--ink': '#f0eee9',         # cream
            '--ink-dim': '#a3998f',
            '--accent': '#d4b224',      # ducat gold
            '--accent-2': '#ab2c38',
            '--border': '#08090a',
            '--shadow': '#000000',
            '--good': '#4a8562',
        },
    },
    'out-of-the-abyss': {
        'name': 'Out of the Abyss',
        'blurb': 'Underdark: obsidian dark, drow violet, fungal neon.',
        'fonts': ('Metamorphous', 'Cardo'),
        'scale': 1.5,
        'vars': {
            '--bg': '#09080b',          
            '--bg-panel': '#17131e',
            '--ink': '#e6e3eb',
            '--ink-dim': '#9890a3',
            '--accent': '#9b6bd9',
            '--accent-2': '#32b88b',
            '--border': '#000000',
            '--shadow': '#000000',
            '--good': '#469c76',
        },
    },
    'tomb-of-annihilation': {
        'name': 'Tomb of Annihilation',
        'blurb': 'Jungle survival: moss, limestone, and Acererak gold.',
        'fonts': ('Pirata One', 'Lora'),
        'scale': 1.4,
        'vars': {
            '--bg': '#111713',
            '--bg-panel': '#1a241d',
            '--ink': '#e4e8e1',
            '--ink-dim': '#8a9a8f',
            '--accent': '#c99b22',
            '--accent-2': '#209a89',
            '--border': '#0a0f0c',
            '--shadow': '#000000',
            '--good': '#4e8c56',
        },
    },
    'curse-of-strahd': {
        'name': 'Curse of Strahd',
        'blurb': 'Gothic horror: pitch, velvet, and bright blood.',
        'fonts': ('UnifrakturMaguntia', 'Crimson Text'),
        # Blackletter is narrow and ornate; it needs the most help to read.
        'scale': 1.9,
        'vars': {
            '--bg': '#0a0a0a',          # pitch black
            '--bg-panel': '#2b1f2e',    # desaturated velvet plum
            '--ink': '#e3dac9',         # bone white
            '--ink-dim': '#948e98',
            '--accent': '#b22222',      # blood red
            '--accent-2': '#6e6a7a',
            '--border': '#000000',
            '--shadow': '#000000',
            '--good': '#5c7f5c',
        },
    },
    'icewind-dale': {
        'name': 'Icewind Dale',
        'blurb': 'Endless night, frost, and one cold star.',
        'fonts': ('Cinzel', 'Lora'),
        'scale': 1.5,
        'vars': {
            '--bg': '#101822',
            '--bg-panel': '#1a2634',
            '--ink': '#e6f0f7',
            '--ink-dim': '#93a8bb',
            '--accent': '#7fd4e8',
            '--accent-2': '#c8dae6',
            '--border': '#060b11',
            '--shadow': '#000000',
            '--good': '#6aa9c4',
        },
    },
}

DEFAULT_THEME = 'dungeon-torch'

# Faces needing more than a plain family name in the Google Fonts URL.
#
# The css2 API rejects a bare `family=X` for families whose axes have no
# default position, and it fails the WHOLE request when one family is bad:
# a single unqualified name takes the other face down with it and the page
# silently falls back to Georgia. Legacy static families (Merriweather,
# Crimson Text, Lora, Cormorant Garamond, Playfair Display...) need their
# ital/wght tuples spelled out. Axis tags stay alphabetical (ital before
# wght) and tuples sorted, as the API requires.
_FONT_QUERY = {
    'IM Fell English': 'family=IM+Fell+English:ital@0;1',
    'Merriweather': 'family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;'
                    '1,300;1,400;1,700;1,900',
    'Crimson Text': 'family=Crimson+Text:ital,wght@0,400;0,600;0,700;'
                    '1,400;1,600;1,700',
    'Cormorant Garamond': 'family=Cormorant+Garamond:ital,wght@0,300;0,400;'
                          '0,500;0,600;0,700;1,300;1,400;1,500;1,600;1,700',
    'Lora': 'family=Lora:ital,wght@0,400;0,500;0,600;0,700;'
            '1,400;1,500;1,600;1,700',
    'Playfair Display': 'family=Playfair+Display:ital,wght@0,400;0,500;0,600;'
                        '0,700;0,800;0,900;1,400;1,500;1,600;1,700;1,800;1,900',
    'Cinzel': 'family=Cinzel:wght@400;500;600;700;800;900',
    'Almendra Display': 'family=Almendra+Display',
    'MedievalSharp': 'family=MedievalSharp',
    'Pirata One': 'family=Pirata+One',
    'UnifrakturMaguntia': 'family=UnifrakturMaguntia',
    'Press Start 2P': 'family=Press+Start+2P',
    'Metamorphous': 'family=Metamorphous',
    'Cardo': 'family=Cardo:ital,wght@0,400;0,700;1,400',
}


def clean_theme(raw):
    """Return a known theme id, falling back to the default for junk input."""
    raw = (raw or '').strip().lower()
    return raw if raw in THEMES else DEFAULT_THEME


def theme_list():
    """Themes as [{id, name, blurb}], default first then alphabetical."""
    rest = sorted((tid for tid in THEMES if tid != DEFAULT_THEME),
                  key=lambda t: THEMES[t]['name'].lower())
    return [{'id': tid, 'name': THEMES[tid]['name'], 'blurb': THEMES[tid]['blurb']}
            for tid in [DEFAULT_THEME] + rest]


def fonts_url(theme_id):
    """Google Fonts URL carrying just the two faces this theme needs.

    Only the active theme's fonts are fetched, so switching themes never makes
    a page download every face in the table.

    The css2 API wants `family=` params in alphabetical order and rejects the
    whole request otherwise, so the faces are sorted by family name here
    rather than left in (display, body) order.

    Returned as Markup: the `&` separators are URL syntax, and Jinja's HTML
    autoescaping would turn them into `&amp;` and break the request.
    """
    display, body = THEMES[clean_theme(theme_id)]['fonts']
    # dict.fromkeys de-duplicates while keeping order (a theme may reuse a face).
    families = sorted(dict.fromkeys((display, body)))
    specs = [_FONT_QUERY.get(fam, 'family=' + fam.replace(' ', '+'))
             for fam in families]
    return Markup('https://fonts.googleapis.com/css2?'
                  + '&'.join(specs) + '&display=swap')


def css_vars(theme_id):
    """The theme's :root override block, ready to drop into a <style> tag.

    Returned as Markup: this is CSS, not HTML. Autoescaping would rewrite the
    quotes around font names to `&#39;`, which is not a valid font-family
    value, so the browser would drop those declarations and keep the default
    face while the (quote-free) colours still applied.
    """
    theme = THEMES[clean_theme(theme_id)]
    display, body = theme['fonts']
    lines = [f'  {k}: {v};' for k, v in theme['vars'].items()]
    # Fallbacks keep text readable if Google Fonts is unreachable (self-hosted
    # app on a table's Wi-Fi may well have no internet).
    lines.append(f"  --font-display: '{display}', Georgia, serif;")
    lines.append(f"  --font-body: '{body}', Georgia, serif;")
    lines.append(f"  --display-scale: {theme['scale']};")
    # The stepped heading shadow only reads as pixel-art under a pixel face;
    # under a blackletter or serif it just looks smudged.
    if theme['fonts'][0] != 'Press Start 2P':
        lines.append('  --display-shadow: none;')
    return Markup(':root {\n' + '\n'.join(lines) + '\n}')
