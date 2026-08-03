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
    'vecna-eve-of-ruin': {
        'name': 'Vecna: Eve of Ruin',
        'blurb': 'Necromancy: grave-dark, corpse-light green, and rotten violet.',
        # Grenze Gotisch is a blackletter that stays legible at UI sizes -- the
        # Whispered One's gothic menace without Strahd's near-unreadable
        # Unifraktur. EB Garamond keeps the long text an old-grimoire serif.
        'fonts': ('Grenze Gotisch', 'EB Garamond'),
        # A blackletter display face, so it needs a strong bump like Strahd,
        # though Grenze is wider and more even than Unifraktur, so a touch less.
        'scale': 1.75,
        'vars': {
            # The one green theme in the table: Vecna's necrotic pallor. No
            # other preset uses corpse-green as its accent, so it reads as
            # unmistakably "the lich" beside the golds, blues and reds.
            '--bg': '#0b0f0b',          # grave earth, near-black with a green cast
            '--bg-panel': '#141a16',    # mausoleum stone
            '--ink': '#e4e2d0',         # bone / old vellum
            '--ink-dim': '#8f9c86',     # lichen grey-green
            '--accent': '#7bc74d',      # necrotic corpse-light green
            '--accent-2': '#8a4fbf',    # rotten arcane violet (Vecna's magic)
            '--border': '#050705',
            '--shadow': '#000000',
            '--good': '#5f9e6a',
        },
    },
    'tashas-cauldron': {
        'name': "Tasha's Cauldron of Everything",
        'blurb': 'Chaotic arcana: bubbling violet brew, copper, and malachite.',
        # Cinzel Decorative is an ornate, flourished display -- the grimoire
        # feel of an experimental spellbook. Cormorant Garamond keeps the long
        # text a fine alchemical serif.
        'fonts': ('Cinzel Decorative', 'Cormorant Garamond'),
        'scale': 1.45,
        'vars': {
            '--bg': '#170f1e',          # deep witch-violet, near black
            '--bg-panel': '#241633',    # brewed amethyst
            '--ink': '#f2e9d8',         # warm parchment
            '--ink-dim': '#b49bc4',     # dilute lilac
            '--accent': '#c084e0',      # arcane violet glow
            '--accent-2': '#c9822e',    # cauldron copper
            '--border': '#0c0713',
            '--shadow': '#000000',
            '--good': '#3fae8f',        # malachite bubbling
        },
        # Tasha is chaos and experiment: the cauldron never sits still. A slow
        # radial "brew" simmers on the page background, panels shimmer a copper
        # rim, headings pour a violet-to-copper gradient, and buttons pulse an
        # arcane glow on hover. All motion is behind prefers-reduced-motion.
        'extra_css': """
/* ---- Tasha's Cauldron: bubbling arcane brew ---- */
body {
  background-color: var(--bg);
  background-image:
    radial-gradient(60% 45% at 22% 88%, rgba(192,132,224,0.22), transparent 60%),
    radial-gradient(50% 40% at 82% 78%, rgba(201,130,46,0.18), transparent 62%),
    radial-gradient(45% 35% at 50% 108%, rgba(63,174,143,0.20), transparent 60%);
  background-attachment: fixed;
}
@media (prefers-reduced-motion: no-preference) {
  body {
    background-size: 140% 140%, 130% 130%, 160% 160%;
    animation: tasha-brew 26s ease-in-out infinite alternate;
  }
  @keyframes tasha-brew {
    0%   { background-position: 20% 90%, 80% 80%, 50% 110%; }
    50%  { background-position: 26% 82%, 74% 86%, 46% 104%; }
    100% { background-position: 18% 94%, 86% 74%, 54% 112%; }
  }
}
/* Panels get a faint copper inner rim that slowly breathes. */
.panel, .h-item, .wiki-card, .handout-card, .folder-card {
  position: relative;
}
.panel::after {
  content: "";
  position: absolute; inset: 0;
  pointer-events: none;
  border: 1px solid rgba(201,130,46,0.35);
  box-shadow: inset 0 0 18px rgba(192,132,224,0.10);
  mix-blend-mode: screen;
}
@media (prefers-reduced-motion: no-preference) {
  .panel::after { animation: tasha-rim 7s ease-in-out infinite alternate; }
  @keyframes tasha-rim {
    from { opacity: 0.55; }
    to   { opacity: 1; }
  }
}
/* Headings pour a violet-to-copper gradient into the letterforms. */
h1, h2, h3, .pixel {
  background: linear-gradient(100deg, var(--accent) 0%, #e6c7a0 55%, var(--accent-2) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  -webkit-text-fill-color: transparent;
}
/* Buttons glow like a stirred brew when hovered. */
@media (hover: hover) {
  .btn { transition: box-shadow 0.25s ease, transform 0.06s steps(2); }
  .btn:hover {
    box-shadow: var(--px) var(--px) 0 0 var(--shadow),
                0 0 14px rgba(192,132,224,0.65);
  }
}
/* The POP button simmers copper instead. */
@media (hover: hover) {
  .btn--pop:hover {
    box-shadow: var(--px) var(--px) 0 0 var(--shadow),
                0 0 16px rgba(201,130,46,0.7);
  }
}
""",
    },
    'xanathars-guide': {
        'name': "Xanathar's Guide to Everything",
        'blurb': 'The beholder watches: acid green, magenta, and a staring eye.',
        # Nova Square is a squared, alien-tech display face -- criminal-
        # syndicate signage / a surveillance readout, but fully legible
        # (unlike the earlier Rubik Glitch, which was decorative to the point
        # of unreadable). Cardo keeps the body text a clean serif.
        'fonts': ('Nova Square', 'Cardo'),
        'scale': 1.5,
        'vars': {
            '--bg': '#06090a',          # black observation room
            '--bg-panel': '#0e1518',    # dark scrying glass
            '--ink': '#e7f5ec',         # cold white
            '--ink-dim': '#7fa597',     # dim eye-shine
            '--accent': '#8cff3b',       # aberrant acid green
            '--accent-2': '#ff2fd0',    # eye-stalk magenta
            '--border': '#020404',
            '--shadow': '#000000',
            '--good': '#48d97a',
        },
        # Xanathar IS an eye. A magenta/green pupil dilates at the centre of
        # the page, faint scanlines crawl like a surveillance feed, panels iris
        # a thin ring, and buttons fire an eye-ray flash on hover. All motion
        # is behind prefers-reduced-motion.
        'extra_css': """
/* ---- Xanathar's Guide: the watching beholder ---- */
body {
  background-color: var(--bg);
  background-image:
    radial-gradient(closest-side at 50% 42%, rgba(255,47,208,0.20), rgba(140,255,59,0.08) 45%, transparent 70%),
    repeating-linear-gradient(0deg, rgba(140,255,59,0.05) 0 1px, transparent 1px 3px);
  background-attachment: fixed, fixed;
  background-size: 120% 120%, 100% 100%;
}
/* A dark vignette so the centre reads as a staring pupil. */
body::before {
  content: "";
  position: fixed; inset: 0; z-index: -1;
  pointer-events: none;
  background: radial-gradient(closest-side at 50% 42%, transparent 40%, rgba(0,0,0,0.55) 100%);
}
@media (prefers-reduced-motion: no-preference) {
  body {
    animation: xan-pupil 9s ease-in-out infinite alternate;
  }
  /* The pupil dilates and contracts. */
  @keyframes xan-pupil {
    from { background-size: 118% 118%, 100% 100%; }
    to   { background-size: 138% 138%, 100% 100%; }
  }
}
/* Panels get a thin aberrant iris ring. */
.panel {
  position: relative;
  box-shadow: var(--px) var(--px) 0 0 var(--shadow),
              inset 0 0 0 1px rgba(255,47,208,0.30),
              inset 0 0 22px rgba(140,255,59,0.06);
}
/* Headings: acid green with a magenta chromatic-aberration shadow. */
h1, h2, h3, .pixel {
  color: var(--accent);
  text-shadow: -1px 0 rgba(255,47,208,0.65), 1px 0 rgba(140,255,59,0.35);
}
/* Count badges become little pupils. */
.count-badge {
  border-radius: 50%;
  background: radial-gradient(circle at 50% 45%, var(--accent-2) 0 32%, var(--border) 34%);
  color: var(--accent);
}
/* Buttons fire an eye-ray flash on hover. */
@media (hover: hover) {
  .btn { transition: box-shadow 0.2s ease, transform 0.06s steps(2); }
  .btn:hover {
    box-shadow: var(--px) var(--px) 0 0 var(--shadow),
                0 0 12px rgba(140,255,59,0.75),
                0 0 4px rgba(255,47,208,0.9);
  }
}
/* Public handouts already glow green; make their edge pulse like a live feed. */
@media (prefers-reduced-motion: no-preference) {
  .h-item--public { animation: xan-scan 3.2s ease-in-out infinite; }
  @keyframes xan-scan {
    0%, 100% { box-shadow: var(--px) var(--px) 0 0 var(--good); }
    50%      { box-shadow: var(--px) var(--px) 0 0 var(--good),
                           0 0 12px rgba(140,255,59,0.55); }
  }
}
""",
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
    # Vecna theme. Grenze Gotisch (blackletter display) is a variable font on
    # the wght axis; EB Garamond (body) carries ital + wght. Both axes are
    # spelled out so the css2 API accepts them instead of failing the request.
    'Grenze Gotisch': 'family=Grenze+Gotisch:wght@300;400;500;600;700;800;900',
    'EB Garamond': 'family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;'
                   '1,400;1,500;1,600;1,700',
    # Tasha theme. Cinzel Decorative (ornate display) has a static wght axis;
    # its body face Cormorant Garamond is already listed above.
    'Cinzel Decorative': 'family=Cinzel+Decorative:wght@400;700;900',
    # Xanathar theme. Nova Square is a single-style squared display; Cardo
    # (body) is already listed above.
    'Nova Square': 'family=Nova+Square',
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

    A theme may also carry an optional `extra_css` string: extra rules (custom
    textures, animations, per-theme component tweaks) that go BEYOND repainting
    tokens. It is appended after the :root block and is emitted ONLY when that
    theme is active -- css_vars is always called with the current theme -- so
    no `[data-theme=...]` guard is needed and other themes never pay for it.
    Keep such rules scoped to real selectors (.panel, .btn, body::before, ...)
    and wrap motion in `prefers-reduced-motion: no-preference`.
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
    block = ':root {\n' + '\n'.join(lines) + '\n}'
    extra = theme.get('extra_css')
    if extra:
        block += '\n' + extra.strip() + '\n'
    return Markup(block)
