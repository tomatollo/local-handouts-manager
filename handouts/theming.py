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
        'fonts': ('Bokor', 'IM Fell English'),
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
    'vintage-arcade': {
        'name': 'Vintage Arcade',
        'blurb': 'CRT phosphor and neon synthwave: insert coin to continue.',
        # Press Start 2P is the pixel display face the base CSS already
        # sugars with a stepped "pixel" shadow. VT323 is a monospace CRT
        # terminal face for the long text.
        'fonts': ('Press Start 2P', 'VT323'),
        # Press Start 2P is the calibrated face, so no correction needed.
        'scale': 1,
        'vars': {
            # Deep terminal black with a cold blue cast -- a powered-down CRT.
            '--bg': '#050510',
            # Panels lift just enough to read as a glowing screen bezel.
            '--bg-panel': '#0d0d1f',
            # Phosphor cyan ink, softened from pure white so it doesn't glare.
            '--ink': '#a8ddd4',
            '--ink-dim': '#5f8785',
            # Neon accents dialled back from full saturation: a dusty synthwave
            # magenta and a muted CRT green, so they still read as neon on the
            # dark screen without the eye-searing glare of pure #ff2ec4/#39ff14.
            '--accent': '#d15fa8',      # softened synthwave magenta
            '--accent-2': '#5fb85a',    # muted phosphor green
            '--border': '#02020a',
            '--shadow': '#000000',
            '--good': '#5fb85a',        # "visible" = live phosphor green
        },
        # The juice: a CRT screen look without the seizure-inducing motion.
        # Scanlines and a phosphor tint texture the screen, a retro crosshair/
        # pixel cursor replaces the pointer, buttons fire a mechanical stepped
        # snap plus a soft neon bloom on hover, panels carry a thin neon bezel,
        # and headings glow neon in the dark. No flicker, no roll -- the CRT
        # sits still so it never triggers a headache.
        'extra_css': """
/* ==== Vintage Arcade: CRT terminal / 80s cabinet ==================== */

/* ---- CRT scanlines -------------------------------------------------
   A repeating dark stripe laid over the whole page simulates the gaps
   between a cathode-ray tube's scan lines. Kept very low-contrast so
   text stays readable; a faint magenta/green wash sits under it for the
   "phosphor screen" tint. background-attachment:fixed pins the lines to
   the viewport, so they read as the glass, not the content. */
body {
  background-color: var(--bg);
  background-image:
    repeating-linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.28) 0px,
      rgba(0, 0, 0, 0.28) 1px,
      transparent 1px,
      transparent 3px
    ),
    radial-gradient(80% 60% at 50% 0%, rgba(209, 95, 168, 0.06), transparent 60%),
    radial-gradient(90% 70% at 50% 120%, rgba(95, 184, 90, 0.05), transparent 60%);
  background-attachment: fixed;
  /* Custom retro cursor everywhere: a phosphor-green crosshair. */
  cursor: crosshair;
}

/* ---- Custom 8-bit "hand" cursor for anything clickable -------------
   A tiny base64 pixel-pointer (a chunky white arrow with a black
   outline, 16x16) replaces the OS hand on buttons and links. Falls
   back to `pointer` if the data URI is ever stripped. */
.btn, a, button, [role="button"], summary, label[for] {
  cursor:
    url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgc2hhcGUtcmVuZGVyaW5nPSJjcmlzcEVkZ2VzIiB2aWV3Qm94PSIwIDAgMTYgMTYiPjxwYXRoIGZpbGw9IiMwMDAiIGQ9Ik0yIDBoMnYyaC0yem0yIDJoMnYyaC0yem0yIDJoMnYyaC0yem0yIDJoMnYyaC0yem0yIDJoMnYyaC0yek00IDEwaDJ2Mmgtem0wIDJoLTJ2LTJoMnptLTQtMTBoMnYxMGgtMnoiLz48cGF0aCBmaWxsPSIjZmZmIiBkPSJNMiAyaDJ2MTBoLTJ6bTIgMGgydjJoLTJ6bTIgMmgydjJoLTJ6bTIgMmgydjJoLTJ6bTIgMmgydjJoLTJ6bS02IDJoMnYyaC0yeiIvPjwvc3ZnPg==') 2 2,
    pointer;
}

/* ---- Neon glow on headings -----------------------------------------
   Layered text-shadows build a tight magenta core fading to a broad
   green halo, so titles "burn" into the dark screen. */
h1, h2, h3, .pixel {
  color: var(--ink);
  text-shadow:
    0 0 2px rgba(168, 221, 212, 0.6),
    0 0 6px var(--accent),
    0 0 12px rgba(209, 95, 168, 0.35);
}

/* ---- Button hover: neon bloom + mechanical snap --------------------
   steps() makes the transform jump in hard stages instead of easing,
   for a clunky arcade-relay feel; the box-shadow layers the stepped
   retro shadow under an intense magenta/green neon bloom. */
@media (hover: hover) {
  .btn {
    transition:
      box-shadow 0.12s steps(3, end),
      transform  0.08s steps(2, end),
      background 0.12s steps(2, end);
  }
  .btn:hover {
    background: var(--accent);
    color: var(--border);
    box-shadow:
      var(--px) var(--px) 0 0 var(--shadow),
      0 0 6px rgba(209, 95, 168, 0.55),
      0 0 14px rgba(209, 95, 168, 0.3);
  }
  /* The "pop" call-to-action blooms green (Matrix/Pac-Man) instead. */
  .btn--pop:hover {
    background: var(--accent-2);
    color: var(--border);
    box-shadow:
      var(--px) var(--px) 0 0 var(--shadow),
      0 0 6px rgba(95, 184, 90, 0.6),
      0 0 16px rgba(95, 184, 90, 0.3);
  }
}

/* ---- Panels: a thin neon bezel ------------------------------------- */
.panel {
  box-shadow:
    var(--px) var(--px) 0 0 var(--shadow),
    inset 0 0 0 1px rgba(209, 95, 168, 0.18),
    inset 0 0 18px rgba(95, 184, 90, 0.04);
}
""",
    },
    'military-terminal': {
        'name': 'Military Terminal',
        'blurb': 'Cold War readout: phosphor green on black, strictly business.',
        # Share Tech Mono is a clean monospace with a technical, stencilled
        # feel -- a field terminal, not an arcade. VT323 (already loaded for
        # Vintage Arcade) carries the body as a matching CRT monospace.
        'fonts': ('Share Tech Mono', 'VT323'),
        # Share Tech Mono is a normal-width mono, not the tiny-and-wide Press
        # Start 2P, so headings need a bump to fill the calibrated sizes.
        'scale': 1.5,
        'vars': {
            # Near-black with the faintest green cast: an unlit phosphor screen.
            '--bg': '#030602',
            '--bg-panel': '#0a110a',    # a powered panel, barely lifted
            '--ink': '#33ff66',         # classic phosphor green, the readout text
            '--ink-dim': '#4a7a52',     # dimmer green for secondary lines
            '--accent': '#7dff9a',      # brighter green: active fields, headings
            '--accent-2': '#e0a53a',    # amber: the one warning/alert colour
            '--border': '#0e1c0e',      # dark green-black hairline
            '--shadow': '#000000',
            '--good': '#33ff66',        # "visible" reuses the phosphor green
        },
        # Minimal on purpose: a military terminal is spartan. Just fine, still
        # scanlines and a phosphor tint (no motion at all), a blinking-free
        # block prompt feel from squared panels, and amber only where something
        # needs attention. No glow storms, no animation -- it should read as a
        # utilitarian readout, the quiet counterpoint to Vintage Arcade.
        'extra_css': """
/* ==== Military Terminal: spartan phosphor readout ================== */

/* ---- Faint, static scanlines + a low phosphor wash ---------------
   Same CRT-glass idea as the arcade theme but dialled right down: the
   lines are barely there and nothing moves, so it reads as a serious
   field terminal rather than a games cabinet. Pinned to the viewport. */
body {
  background-color: var(--bg);
  background-image:
    repeating-linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.22) 0px,
      rgba(0, 0, 0, 0.22) 1px,
      transparent 1px,
      transparent 3px
    ),
    radial-gradient(100% 80% at 50% 0%, rgba(51, 255, 102, 0.04), transparent 70%);
  background-attachment: fixed;
}

/* ---- Squared, hard-edged panels: no soft anything --------------- */
.panel {
  box-shadow:
    var(--px) var(--px) 0 0 var(--shadow),
    inset 0 0 0 1px rgba(51, 255, 102, 0.14);
}

/* ---- Headings as terminal labels: a leading prompt glyph and a
        subtle phosphor glow, nothing more. ------------------------- */
h1, h2, h3, .pixel {
  color: var(--accent);
  text-shadow: 0 0 4px rgba(51, 255, 102, 0.35);
}
h1::before, h2::before {
  content: "> ";
  color: var(--ink-dim);
}

/* ---- Buttons: flat, hard, phosphor. Hover just inverts to the
        green, like selecting a field on a text UI. No bloom. ------- */
@media (hover: hover) {
  .btn { transition: background 0.1s linear, color 0.1s linear; }
  .btn:hover {
    background: var(--ink);
    color: var(--bg);
  }
  /* The one alert colour: POP is the button that shouts, in amber. */
  .btn--pop:hover {
    background: var(--accent-2);
    color: var(--bg);
  }
}
""",
    },
}

DEFAULT_THEME = 'dungeon-torch'

# Themes gathered into labelled families for the picker. The first group holds
# the official D&D campaign presets; "Other Universes" collects everything that
# isn't D&D (Vintage Arcade is the first of these). Membership is by explicit
# id list so a theme's place is stated in one spot; any theme NOT named in a
# group falls through to the last group automatically, so a future non-D&D
# preset lands in "Other Universes" without a second edit here. Order of the
# groups, and of ids within a group, is the order the picker renders them --
# except the default theme, which theme_groups() always floats to the top of
# its own group.
THEME_GROUPS = (
    ('Dungeons & Dragons', (
        'dungeon-torch',
        'phandelver',
        'tiamat',
        'out-of-the-abyss',
        'tomb-of-annihilation',
        'curse-of-strahd',
        'icewind-dale',
        'vecna-eve-of-ruin',
        'tashas-cauldron',
        'xanathars-guide',
    )),
    ('Other Universes', (
        'vintage-arcade',
        'military-terminal',
    )),
)

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
    # Vintage Arcade theme. VT323 is a single-style CRT-terminal monospace;
    # its display face Press Start 2P is already listed above.
    'VT323': 'family=VT323',
    # Military Terminal theme. Share Tech Mono is a single-style monospace;
    # its body face VT323 is already listed just above.
    'Share Tech Mono': 'family=Share+Tech+Mono',
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


def theme_groups():
    """Themes grouped for the picker: [{label, themes: [{id, name, blurb}]}].

    Reads THEME_GROUPS for the labels and membership, then appends any theme
    that no group named to the LAST group -- so a newly added non-D&D preset
    shows up under "Other Universes" without touching this function. Within a
    group the ids keep THEME_GROUPS order, except DEFAULT_THEME which is floated
    to the front of whichever group holds it (it is the one the picker should
    show first). Empty groups are dropped so a label with nothing under it
    never renders a bare heading.
    """
    assigned = {tid for _, ids in THEME_GROUPS for tid in ids}
    leftover = [tid for tid in THEMES if tid not in assigned]

    groups = []
    last = len(THEME_GROUPS) - 1
    for i, (label, ids) in enumerate(THEME_GROUPS):
        # Keep only ids that really exist in THEMES (guards against a typo or a
        # removed theme lingering in the group list), preserving their order.
        members = [tid for tid in ids if tid in THEMES]
        # Anything no group claimed rides along with the final group.
        if i == last:
            members += leftover
        # Float the default theme to the front of its group.
        if DEFAULT_THEME in members:
            members = [DEFAULT_THEME] + [t for t in members if t != DEFAULT_THEME]
        if not members:
            continue
        groups.append({
            'label': label,
            'themes': [{'id': tid,
                        'name': THEMES[tid]['name'],
                        'blurb': THEMES[tid]['blurb']}
                       for tid in members],
        })
    return groups


# The colour tokens a preview swatch carries verbatim from the theme. The two
# font faces are handled separately (see theme_preview_style) because they need
# to become differently-named custom properties, not copied as-is.
_PREVIEW_KEYS = ('--bg', '--bg-panel', '--ink', '--ink-dim',
                 '--accent', '--accent-2', '--border')


def theme_preview_style(theme_id):
    """Inline `style` value that dresses one picker box in its own theme.

    Emits the colour custom properties (`--bg: #..; --ink: #..; ...`) plus two
    preview-only font properties, `--preview-font-display` and
    `--preview-font-body`, carrying that theme's heading and body faces. The
    picker CSS reads those two on `.theme-choice--preview` so each box's name
    and blurb render in the theme's ACTUAL typefaces, not the page's -- a true
    font+colour preview. (This needs every theme's font loaded on the page;
    see all_fonts_url, which the Appearance template links for exactly that.)

    Returned as Markup because it is CSS going into an attribute, not HTML; the
    values are fixed strings from the theme table, never user input.
    """
    theme = THEMES.get(clean_theme(theme_id))
    vars_ = theme['vars']
    display, body = theme['fonts']
    parts = [f'{k}: {vars_[k]}' for k in _PREVIEW_KEYS if k in vars_]
    # Same fallbacks as css_vars, so a box still reads if a face fails to load.
    parts.append(f"--preview-font-display: '{display}', Georgia, serif")
    parts.append(f"--preview-font-body: '{body}', Georgia, serif")
    # The display face's own size correction, so each preview name is sized by
    # the SAME factor the real UI would use for that theme (Press Start 2P is
    # tiny, blackletters are huge -- the scale evens them out).
    parts.append(f"--preview-scale: {theme['scale']}")
    return Markup('; '.join(parts) + ';')


def all_fonts_url():
    """Google Fonts URL carrying EVERY face used by any theme.

    Only the Appearance page links this: the theme picker previews each box in
    its own typeface, so it needs them all at once, unlike the rest of the app
    where fonts_url fetches just the active theme's two faces. Families are
    de-duplicated and sorted so the css2 API accepts the request (it rejects an
    unsorted family list) and so two themes sharing a face don't request it
    twice.

    Returned as Markup: the `&` separators are URL syntax that Jinja's HTML
    autoescaping would turn into `&amp;` and break.
    """
    families = set()
    for theme in THEMES.values():
        display, body = theme['fonts']
        families.add(display)
        families.add(body)
    specs = [_FONT_QUERY.get(fam, 'family=' + fam.replace(' ', '+'))
             for fam in sorted(families)]
    return Markup('https://fonts.googleapis.com/css2?'
                  + '&'.join(specs) + '&display=swap')


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
