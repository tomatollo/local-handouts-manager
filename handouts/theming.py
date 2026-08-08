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
    'analog-archive': {
        'name': 'Analog Archive',
        'blurb': 'Noir case files: manila folders, redacted ink, and a CLASSIFIED stamp.',
        # Special Elite mimics a smudged typewriter for headings/stamps;
        # Courier Prime is the clean report/screenplay monospace for body.
        'fonts': ('Special Elite', 'Courier Prime'),
        # Both faces sit at a normal width (unlike Press Start 2P), so headings
        # need a bump to fill the calibrated sizes. Special Elite runs a touch
        # large already, so a moderate 1.35 keeps stamps from overflowing.
        'scale': 1.35,
        'vars': {
            # This is the one "board" theme: a dark corkboard/leather desk with
            # LIGHT manila-paper panels sitting on it. So --ink is DARK
            # (typewriter ink on paper), like Phandelver's inverted logic.
            '--bg': '#1c1b18',          # shadowed cork/leather desk, near-black
            '--bg-panel': '#e6ddc5',    # aged manila folder / paper
            '--ink': '#2b2b2b',         # typewriter ink on the paper
            '--ink-dim': '#6a6353',     # faded pencil / carbon-copy grey
            '--accent': '#9e2a2b',      # faded red rubber stamp
            '--accent-2': '#1c3d5a',    # biro / fountain-pen ink blue
            '--border': '#3a352c',      # soft brown paper edge (not hard black)
            '--shadow': 'rgba(0,0,0,0.55)',  # soft desk shadow, not pure black
            '--good': '#3f6d4e',        # green string / "verified" ink
        },
        # The juice: paper on a board. Panels get a rough-paper wash + stacked-
        # paper shadow and a strip of translucent tape; the h1 reads as a red
        # CLASSIFIED stamp pressed into the page; buttons redact to a marker-
        # black bar on hover; count badges become tilted yellow post-its.
        # Everything with motion sits behind prefers-reduced-motion.
        'extra_css': """
/* ==== Analog Archive: noir case-file board ========================= */

/* ---- The board itself ---------------------------------------------
   A dark desk/corkboard: a faint fibrous noise (layered low-alpha
   gradients) breaks up the flat --bg so it reads as leather/cork, not
   a void. Text placed directly on the board (outside a paper panel) is
   light, since --ink is dark for the paper; we restore that here. */
body {
  background-color: var(--bg);
  background-image:
    radial-gradient(circle at 18% 22%, rgba(255,255,255,0.020) 0 2px, transparent 3px),
    radial-gradient(circle at 63% 71%, rgba(255,255,255,0.018) 0 2px, transparent 3px),
    radial-gradient(circle at 84% 34%, rgba(0,0,0,0.22) 0 3px, transparent 4px),
    linear-gradient(135deg, rgba(0,0,0,0.25), rgba(0,0,0,0) 40%);
  background-size: 140px 140px, 190px 190px, 220px 220px, 100% 100%;
  background-attachment: fixed;
  color: #d9d2c2;               /* light "chalk" text when on the bare board */
}
/* Body copy sitting on the board (subtitles, muted lines) stays light. */
.subtitle { color: #b7ae99; }

/* ---- Paper panels: manila stock, rough wash, stacked-paper shadow --
   A subtle diagonal gradient dirties the flat manila so it feels like
   rough paper; the layered box-shadow fakes 2-3 sheets stacked under
   the top one. position:relative anchors the tape pseudo-element.
   NB: .handout-card is intentionally NOT in this list -- in Cards view
   it becomes a transparent polaroid, in Rows a folder spine (below). */
.panel, .wiki-card, .folder-card {
  position: relative;
  background-color: var(--bg-panel);
  background-image:
    linear-gradient(115deg, rgba(0,0,0,0.05), rgba(0,0,0,0) 45%),
    radial-gradient(circle at 88% 8%, rgba(120,100,60,0.10), transparent 42%);
  border: 1px solid var(--border);
  box-shadow:
    2px 3px 0 0 rgba(214,203,170,0.85),   /* sheet 2 peeking out */
    4px 6px 0 0 rgba(198,186,150,0.55),   /* sheet 3 */
    6px 9px 14px 0 var(--shadow);         /* soft cast shadow onto board */
}

/* ---- Pinned to the board: one object per element type -------------
   Anti-"tape everywhere" rule: tape stays ONLY on the big .panel. The
   wiki-card gets a thumbtack; handout cards get a tack in Cards view
   (further down); folders get a real tab, not a tack. Post-its are the
   count badges. All pseudo-elements are non-clickable and sit above the
   paper. */

/* Tape: only on the big panel, a single strip up top. */
.panel::before {
  content: "";
  position: absolute;
  top: -11px; left: 50%;
  width: 96px; height: 24px;
  transform: translateX(-50%) rotate(-2.5deg);
  background: linear-gradient(90deg,
      rgba(228,222,200,0.12),
      rgba(228,222,200,0.32) 22%,
      rgba(228,222,200,0.20) 80%,
      rgba(228,222,200,0.12));
  border-left: 1px solid rgba(255,255,255,0.16);
  border-right: 1px solid rgba(255,255,255,0.16);
  box-shadow: 0 1px 2px rgba(0,0,0,0.22);
  pointer-events: none;
  z-index: 3;
}

/* Thumbtack: on the wiki-card. A glossy red disc with a centre hole,
   drawn purely with radial-gradients. No tape here. */
.wiki-card::before {
  content: "";
  position: absolute;
  top: -7px; left: 50%;
  width: 16px; height: 16px;
  transform: translateX(-50%);
  border-radius: 50%;
  background:
    radial-gradient(circle at 38% 32%, #ffffff 0 2px, transparent 3px),   /* highlight */
    radial-gradient(circle at 50% 60%, rgba(0,0,0,0.35) 0 2px, transparent 3px), /* hole */
    radial-gradient(circle at 50% 45%, #c0392f 0 55%, #8a1f20 100%);       /* head */
  box-shadow: 0 2px 3px rgba(0,0,0,0.4);
  pointer-events: none;
  z-index: 4;
}

/* ---- The CLASSIFIED stamp: the main h1 ----------------------------
   A tilted red box with a thick red rubber border stamped onto a scrap
   of manila paper. The background is opaque paper (not a grey wash) so
   on the dark board it reads as a stamped card, not a floating grey box.
   The home-title link inherits the stamp colour. */
h1 {
  display: inline-block;
  color: #8a1f20;                       /* darker stamp red = more contrast */
  background: #e6ddc5;                  /* opaque manila scrap under the stamp */
  border: 3px solid #8a1f20;
  border-radius: 2px;
  padding: 4px 14px;
  transform: rotate(-2deg);
  mix-blend-mode: normal;
  text-shadow: 0 1px 0 rgba(255,255,255,0.5);   /* lift ink off the paper */
  box-shadow: inset 0 0 0 1px rgba(138,31,32,0.35),
              2px 3px 6px rgba(0,0,0,0.4);       /* the scrap casts a shadow */
  letter-spacing: 1px;
}
h1 a, h1 .home-title { color: inherit; text-decoration: none; }
/* h2/h3 are section headers sitting on the dark board, so they need a
   LIGHT ink, not the dark biro-blue (which vanished on the board). A soft
   blue-tinted parchment reads as chalk-on-corkboard. */
h2, h3 { color: #b9c4d4; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }
/* When a heading sits INSIDE a paper panel, dark biro-blue is right. */
.panel h2, .panel h3, .wiki-card h2, .wiki-card h3 {
  color: var(--accent-2);
  text-shadow: none;
}

/* ---- Buttons -------------------------------------------------------
   Every button is a manila field with a typed ink label and an ink
   border -- legible on both paper panels and the dark board. */
.btn {
  background: #e6ddc5;                   /* manila, like the panels */
  color: var(--ink);
  border: 2px solid var(--ink);
  box-shadow: 2px 2px 0 0 var(--shadow);
  transition: background 0.12s steps(2, end), color 0.12s steps(2, end),
              border-color 0.12s steps(2, end);
}

/* Redaction hover: ONLY plain action buttons get the marker-black
   "censored" bar. Navigation buttons (mode/view/drawer) and ghost
   buttons are excluded, because hiding their label breaks wayfinding.
   A thin light strike-through hints at redaction without erasing text. */
@media (hover: hover) {
  .btn:not(.hub-mode__btn):not(.view-btn):not(.drawer__link):not(.btn--ghost):not(.btn--pop):not(.hub-mode__btn--active):not(.view-btn--active):hover {
    background: #141414;                 /* marker black */
    color: #cfc8b8;                      /* still readable, like ghosted ink */
    border-color: #141414;
    text-decoration: line-through;
    text-decoration-color: rgba(255,255,255,0.5);
  }
}

/* Navigation & ghost buttons: a quiet paper hover, NEVER black. */
@media (hover: hover) {
  .hub-mode__btn:hover,
  .view-btn:hover,
  .btn--ghost:hover,
  .drawer__link:hover {
    background: #f0e9d2;                 /* paper lifts a shade */
    color: var(--ink);
    border-color: var(--accent);
  }
}

/* Active / selected navigation = a red rubber stamp, light ink, so the
   current tab is obvious and readable (base CSS made text --border, too
   dark on red). */
.hub-mode__btn--active,
.view-btn--active,
.drawer__link--active {
  background: var(--accent) !important;
  color: #f3e7d0 !important;
  border-color: #7f2122 !important;
}
.hub-mode__btn--active:hover,
.view-btn--active:hover,
.drawer__link--active:hover {
  background: #7f2122 !important;        /* deeper red, still light text */
  color: #f3e7d0 !important;
}

/* Ghost buttons (mode chips in the drawer, view switches) sit on the
   dark board or paper; give them an explicit manila base so they never
   inherit the dark --bg-panel-as-board confusion. */
.btn--ghost {
  background: #ded3b6;
  color: var(--ink);
  border-color: var(--ink);
}

/* The POP call-to-action is a red stamp button, deepening on hover. */
.btn--pop {
  background: var(--accent);
  color: #f3e7d0;
  border-color: #7f2122;
}
@media (hover: hover) {
  .btn--pop:hover { background: #7f2122; color: #f3e7d0; border-color: #7f2122; }
}

/* Drawer navigation links: the base gives them background:var(--bg) (the
   dark board) which is invisible inside the light drawer panel. Put them
   on paper with ink text. */
.drawer__link {
  background: #ded3b6;
  color: var(--ink);
  border-color: var(--border);
}

/* ---- Editable fields: light card, dark ink ------------------------
   The base CSS gives inputs `color: --ink; background: --bg`. Here --bg
   is the dark board, so dark ink vanished on it. Force them onto a light
   card. The <select> has appearance:none in the base, so its <option>
   list also needs an explicit light background + dark text or it renders
   on the OS dark theme and looks broken. !important beats the base rule. */
input, select, textarea {
  color: #2b2b2b !important;             /* ink, beats the base --ink */
  background-color: #f4eeda !important;  /* yellowed index card */
  border: 2px solid var(--border);
  box-shadow: inset 1px 1px 0 0 rgba(0,0,0,0.10);
  -webkit-text-fill-color: #2b2b2b;      /* Safari: force text colour */
}
input::placeholder, textarea::placeholder { color: #8a8065; }
/* Redraw the select arrow dark (the base draws it with light --ink-dim,
   invisible on the card). */
select {
  background-image:
    linear-gradient(45deg, transparent 50%, #2b2b2b 50%),
    linear-gradient(135deg, #2b2b2b 50%, transparent 50%) !important;
}
select option { color: #2b2b2b; background-color: #f4eeda; }
input:focus, select:focus, textarea:focus { border-color: var(--accent); outline: none; }

/* ---- Tags & PDF placeholders: paper labels, not black holes -------
   These used `background: var(--bg)` (black) + --accent text. Turn them
   into little paper labels with red stamp text on the manila panel. */
.tag,
.h-thumb--pdf,
.handout-card__pdf {
  background: #ded3b6;                    /* manila a touch darker */
  color: var(--accent);
  border-color: var(--border);
}
.tag--session { color: var(--ink-dim); }

/* The lightbox panel stays dark by design, so its caption must be LIGHT
   (here --ink is dark). */
.lightbox__caption { color: #f3e7d0; }

/* ---- Count badges: little yellow post-its -------------------------
   Square sticky note, tilted, its own soft shadow, biro-blue number.
   Overflow on the parent thumb is allowed so tilt/shadow aren't clipped. */
.count-badge {
  font-family: var(--font-body);
  font-weight: 700;
  color: var(--accent-2);
  background: #f2e06a;
  background-image: linear-gradient(180deg, #f7e884, #ecd44e);
  border: none;
  border-radius: 1px;
  padding: 5px 7px;
  transform: rotate(-6deg);
  box-shadow: 1px 2px 3px rgba(0,0,0,0.35);
}
.h-thumb { overflow: visible; }

/* ================= HANDOUTS: CARDS view = pinned polaroids ========= */
/* The card itself all but disappears (no filled rectangle); the PHOTO
   is the object -- a slightly-crooked polaroid tacked to the board. The
   title becomes a typed caption underneath. */
.view--cards .handout-card {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 6px 4px 12px;
  position: relative;
  transform: rotate(-1.2deg);
  transition: transform 0.12s ease;
}
.view--cards .handout-card:nth-child(even) { transform: rotate(1.4deg); }
.view--cards .handout-card:nth-child(3n)   { transform: rotate(-0.6deg); }
@media (hover: hover) {
  .view--cards .handout-card:hover { transform: rotate(0deg) scale(1.03); }
}
/* The photo carries the polaroid frame, not the card. */
.view--cards .handout-card .h-thumb {
  background: #f6f1e2;
  padding: 6px 6px 8px;
  border: 1px solid rgba(0,0,0,0.15);
  box-shadow: 2px 3px 7px rgba(0,0,0,0.45);
}
.view--cards .handout-card img,
.view--cards .handout-card .h-thumb--pdf { border: none; height: 130px; }
.view--cards .handout-card .h-title {
  font-family: var(--font-display);      /* Special Elite = typewriter */
  /* The polaroid caption sits on the dark board, so it needs LIGHT ink,
     not the dark paper --ink (which was invisible). */
  color: #ece3cf;
  text-shadow: 0 1px 2px rgba(0,0,0,0.6);
  margin-top: 8px;
}
.view--cards .handout-card .h-desc {
  color: #c3bba6;                        /* dimmer light for the description */
  font-style: italic;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}
/* A single thumbtack at the top of each polaroid (Cards view only). */
.view--cards .handout-card::before {
  content: "";
  position: absolute;
  top: -3px; left: 50%;
  width: 16px; height: 16px;
  transform: translateX(-50%);
  border-radius: 50%;
  background:
    radial-gradient(circle at 38% 32%, #ffffff 0 2px, transparent 3px),
    radial-gradient(circle at 50% 60%, rgba(0,0,0,0.35) 0 2px, transparent 3px),
    radial-gradient(circle at 50% 45%, #c0392f 0 55%, #8a1f20 100%);
  box-shadow: 0 2px 3px rgba(0,0,0,0.4);
  pointer-events: none;
  z-index: 4;
}

/* ================= HANDOUTS: ROWS view = folder spines ============= */
/* Not photos but the "spines" of case files: a horizontal manila strip
   with a coloured tab on the left and a typed title, stacked like files
   in a drawer with a slight overlap. */
.view--rows .handout-card {
  background:
    linear-gradient(90deg, rgba(0,0,0,0.06), rgba(0,0,0,0) 12%),
    var(--bg-panel);
  border: 1px solid var(--border);
  border-left: 8px solid var(--accent-2);   /* the folder's coloured tab */
  border-radius: 0 3px 3px 0;
  box-shadow: 1px 2px 4px rgba(0,0,0,0.35);
  padding: 8px 12px;
  margin-bottom: -2px;                        /* slight overlap = a stack */
  transform: none;
}
.view--rows .handout-card::before { display: none; }   /* no tack here */
/* Tab colour cycles like coloured file dividers. */
.view--rows .handout-card:nth-child(3n+1) { border-left-color: var(--accent); }
.view--rows .handout-card:nth-child(3n+2) { border-left-color: var(--accent-2); }
.view--rows .handout-card:nth-child(3n)   { border-left-color: var(--good); }
/* Thumbnail shrinks to a little photo clipped to the file. */
.view--rows .handout-card .h-thumb {
  background: #f6f1e2;
  padding: 2px;
  border: 1px solid rgba(0,0,0,0.15);
  box-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}
.view--rows .handout-card img,
.view--rows .handout-card .h-thumb--pdf { height: 56px; border: none; }
.view--rows .handout-card .h-title {
  font-family: var(--font-display);
  color: var(--ink);
  text-shadow: none;
  text-align: left;
  letter-spacing: 0.5px;
}
@media (hover: hover) {
  .view--rows .handout-card:hover { border-left-width: 12px; }  /* pull the file out */
}

/* ================= TREE view = index-card outline ================= */
/* The terminal tree sits directly on the dark board, so its leaves need
   LIGHT ink (the base gives .tree-leaf color:--ink = dark, invisible).
   Nodes (session headers) stay stamp-red; leaves are typed light text. */
.handout-tree { color: #b7ae99; }                 /* connector lines */
.handout-tree .tree-node { color: var(--accent); }   /* red section heads */
.handout-tree .tree-leaf { color: #ded5c0; }         /* light typed titles */
.handout-tree .tree-leaf:hover,
.handout-tree .tree-leaf--active { color: var(--accent); }
/* The detail panel's hint + border read on the board. */
.tree-detail { border-left-color: var(--border); }
.tree-detail__hint { color: #b7ae99; }

/* ================= FOLDERS = manila file folders ================== */
/* The folder-card becomes an actual folder: a manila body with a tab up
   top-left (a pseudo-element that sticks out above the border) and the
   cover mosaic reading as documents peeking out of the pocket. */
.folder-card {
  position: relative;
  background:
    linear-gradient(180deg, rgba(0,0,0,0.05), rgba(0,0,0,0) 20%),
    #dcd0ac;                              /* manila, a touch warmer */
  border: 1px solid var(--border);
  border-radius: 0 6px 6px 6px;           /* squared top-left for the tab */
  outline: none;                          /* drop the base double pixel border */
  box-shadow: 2px 4px 8px rgba(0,0,0,0.4);
  overflow: visible;
  margin-top: 14px;                       /* room for the protruding tab */
}
/* The folder tab: sticks up above the body, top-left. This REPLACES the
   old blue tack on .folder-card::before. */
.folder-card::before {
  content: "";
  position: absolute;
  top: -13px; left: -1px;
  width: 96px; height: 16px;
  background: #dcd0ac;
  border: 1px solid var(--border);
  border-bottom: none;
  border-radius: 6px 10px 0 0;
  box-shadow: 0 -1px 2px rgba(0,0,0,0.15);
  z-index: 1;
}
/* The mosaic: documents in the pocket. Paper edge, not a black grid. */
.folder-card__mosaic {
  background: #b8ab86;
  border-bottom: none;
  margin: 8px 8px 0;
  border: 1px solid rgba(0,0,0,0.2);
}
.folder-card__cell { background: #efe8d2; }   /* the light "sheets" inside */
.folder-card__pdf { color: var(--ink-dim); }
.folder-card__foot { padding: 8px 12px 10px; }
.folder-card__name {
  font-family: var(--font-display);
  color: var(--ink);
  text-shadow: none;
}
@media (hover: hover) {
  .folder-card:hover { transform: translateY(-3px); border-color: var(--accent); }
}

/* ---- "Visible/public" items get green case-string --------------- */
.h-item--public { box-shadow: 2px 2px 0 0 var(--good); }

/* ---- Motion: only a small settle on load, and only when the user
        hasn't asked for reduced motion. --------------------------- */
@media (prefers-reduced-motion: no-preference) {
  .panel, .wiki-card {
    animation: aa-settle 0.5s ease-out both;
  }
  @keyframes aa-settle {
    from { transform: translateY(-3px) rotate(-0.3deg); opacity: 0.6; }
    to   { transform: none; opacity: 1; }
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
    # Dungeon Torch lives here (not D&D-specific -- it's the generic pixel
    # default). It is still DEFAULT_THEME, and theme_groups() floats the
    # default to the front of whichever group holds it, so it shows first
    # inside Other Universes.
    ('Other Universes', (
        'dungeon-torch',
        'vintage-arcade',
        'military-terminal',
        'analog-archive',
    )),
)

# Per-theme error pages. Each theme maps HTTP status -> (icon, title, msg).
# The error handlers in app.py read the ACTIVE theme and pull its set, so a
# 404 under Curse of Strahd reads "Phantom Village" while the same 404 under
# Vintage Arcade reads "Missing ROM". Titles/messages are English strings run
# through the `|t` filter in error.html, exactly like the old hardcoded ones.
#
# `error_type_en` (the "Bad Request" label) is NOT stored here: it is fixed per
# status code and supplied by app.py, so it never needs translating per theme.
#
# Any theme absent from this table -- or any status a theme omits -- falls back
# to DEFAULT_THEME's set via theme_errors(), so a new theme still renders sane
# error pages before its own copy is written. Dungeon Torch is that fallback and
# carries the original generic D&D wording the app shipped with.
THEME_ERRORS = {
    'dungeon-torch': {
        400: ('\U0001F4A5', 'Wild Magic Surge',
              'You mixed up the spell components. Your request fizzled out in '
              'a shower of harmless sparks.'),
        401: ('\U0001F6D1', 'Failed Stealth Check',
              "'Halt! Who goes there?' The guards caught you trying to sneak "
              'in without the proper passphrase.'),
        403: ('\U0001F6E1\uFE0F', 'Magic Circle',
              'A powerful barrier blocks your path. You lack the required '
              'alignment or level to enter this area.'),
        404: ('\U0001F3B2', 'Critical Fail',
              'Natural 1 on Perception, you got lost. The room is shrouded in '
              'darkness, and the page you are looking for seems to have '
              'vanished into the Astral Plane or been devoured by a Mimic.'),
        429: ('\U0001F6D1', 'Slow Down, Adventurer',
              'You are hammering the gates faster than the guards can answer. '
              'Wait a moment and try again.'),
        500: ('\u26A1', 'The Weave is Tearing',
              'The Dungeon Master spilled coffee on the campaign notes. The '
              'fabric of reality is temporarily unstable.'),
    },
    'phandelver': {
        400: ('\U0001F4DC', 'Illegible Map',
              "Gundren's map seems stained with ale. We couldn't read your "
              'request parameters.'),
        401: ('\U0001F6E1\uFE0F', 'Neverwinter Guard',
              '"Halt, traveler!" You don\'t have the proper identification '
              'papers to enter this district.'),
        403: ('\U0001F6AA', 'Sealed Vault',
              'The doors to the Tresendar vaults are locked tight. Only the '
              'guild master holds the key.'),
        404: ('\U0001F573\uFE0F', 'Empty Mine',
              'You dug too deep in the wrong spot. This tunnel leads to a dead '
              'end.'),
        429: ('\U0001F3F9', 'Goblin Swarm',
              'Too many arrows flying at once! Take cover and wait a moment '
              'before charging again.'),
        500: ('\U0001F30B', 'Cave-In!',
              'The ceiling of the mine just collapsed! Our goblin engineers '
              'are digging the server out of the rubble.'),
    },
    'tiamat': {
        400: ('\U0001FA99', 'Fake Tribute',
              'You tried to offer counterfeit gold to the hoard. The cult '
              'rejects your malformed request.'),
        401: ('\U0001F5DD\uFE0F', "Wyrmspeaker's Seal",
              'You lack the proper cult passphrase. The guards are drawing '
              'their scimitars.'),
        403: ('\U0001F534', 'Chromatic Barrier',
              "Tiamat's magic seals this domain. Mortals without a "
              "Wyrmspeaker's blessing are strictly forbidden."),
        404: ('\U0001F48E', 'Plundered Hoard',
              'The treasure you seek is gone. Adventurers probably looted this '
              'page yesterday.'),
        429: ('\U0001F6D1', 'Hold the Line',
              "You're sending troops to the frontline too quickly. Let the "
              'vanguard breathe!'),
        500: ('\u2694\uFE0F', 'Council Uproar',
              'The factions of Waterdeep are fighting again. Our backend '
              'diplomacy has completely broken down.'),
    },
    'out-of-the-abyss': {
        400: ('\U0001F578\uFE0F', 'Tangled Web',
              "Your request got caught in Lolth's webs. The syntax is "
              'completely tangled.'),
        401: ('\u26D3\uFE0F', 'Velkynvelve Prisoner',
              "Escaped slaves don't have access rights here. The Drow "
              'priestesses demand your surrender.'),
        403: ('\U0001F9E0', 'Illithid Enclave',
              'The Elder Brain rejects your mind. Your psionic clearance level '
              'is insufficient.'),
        404: ('\U0001F573\uFE0F', 'Swallowed by the Dark',
              'The page you seek has been consumed by the endless abyss of the '
              'Underdark.'),
        429: ('\U0001F300', 'Descending Madness',
              'The madness of the Abyss is compounding too quickly. Take a '
              'long rest.'),
        500: ('\U0001F9E0', 'Mind Flayer Blast',
              'An Illithid psychic blast just stunned our backend processes. '
              'Rebooting...'),
    },
    'tomb-of-annihilation': {
        400: ('\U0001F9ED', 'Broken Compass',
              'Your magnetic compass is spinning wildly in the jungle. Your '
              'navigation parameters are invalid.'),
        401: ('\U0001F525', 'Flaming Fist Toll',
              "You haven't paid for your charter of exploration. The Flaming "
              'Fist denies you passage.'),
        403: ('\U0001F9FF', "Soulmonger's Ward",
              'Acererak has sealed this chamber. Your soul is not strong '
              'enough to pierce the barrier.'),
        404: ('\U0001F5FA\uFE0F', "Syndra's Missing Map",
              "The hex grid for this area is blank. You haven't explored this "
              'part of Chult yet.'),
        429: ('\U0001F99F', 'Jungle Fever',
              "You're marching through the sweltering jungle too quickly. Take "
              'a sip of water and slow down.'),
        500: ('\U0001F9D9\u200D\u2642\uFE0F', "Acererak's Laugh",
              'The archlich just cast Meteor Swarm on the server! We are '
              'trying to cast Mending.'),
    },
    'curse-of-strahd': {
        400: ('\U0001F0CF', 'Misread Tarokka',
              'Madame Eva shakes her head. You misinterpreted the cards, and '
              'your request is malformed.'),
        401: ('\u2709\uFE0F', 'No Invitation',
              'The gates of Castle Ravenloft remain closed. You have not been '
              'invited by the master of the domain.'),
        403: ('\U0001F9DB', "Strahd's Command",
              '"I am the Ancient. I am the Land." The vampire lord strictly '
              'forbids your presence here.'),
        404: ('\U0001F3DA\uFE0F', 'Phantom Village',
              'You arrived at the coordinates, but found only an abandoned, '
              'rotting husk of a page.'),
        429: ('\U0001F6AA', 'Frantic Knocking',
              "Pounding on the village doors won't make them open faster. The "
              'locals are terrified, wait a minute.'),
        500: ('\U0001F311', 'Dark Powers Intervene',
              'The mysterious entities of the shadowfell have corrupted the '
              "server's soul."),
    },
    'icewind-dale': {
        400: ('\U0001F976', 'Frostbitten Fingers',
              'Your hands were shaking too much from the cold to type the URL '
              'correctly.'),
        401: ('\U0001F989', "Auril's Test",
              'The Frostmaiden requires a sacrifice of warmth before she '
              'grants you passage.'),
        403: ('\U0001F3F0', 'Ythryn Quarantine',
              'The ancient Netherese city is on magical lockdown to prevent '
              'the spread of arcane blight.'),
        404: ('\U0001F328\uFE0F', 'Whiteout Condition',
              'The blizzard is too thick! The page you are looking for is '
              'completely buried in snow.'),
        429: ('\U0001F32C\uFE0F', 'Biting Winds',
              "You're pushing into the blizzard too fast. Stop and build a "
              'fire before you freeze to death.'),
        500: ('\u2744\uFE0F', 'Everlasting Rime',
              "Auril's spell just froze the entire backend infrastructure "
              'solid.'),
    },
    'vecna-eve-of-ruin': {
        400: ('\U0001F92B', 'Mispronounced Secret',
              'You whispered the wrong dark secret into the void. The cosmos '
              'rejects your request.'),
        401: ('\U0001F977', 'Cult Interception',
              'The cultists of the Whispered One demand the hidden password.'),
        403: ('\U0001F5DD\uFE0F', 'Sigil Denied',
              'The Lady of Pain has barred the doors to this portal. Do not '
              'push your luck.'),
        404: ('\U0001F300', 'Lost in the Astral Sea',
              'Your connection drifted off the silver cord and vanished into '
              'the void.'),
        429: ('\u23F3', 'Time Paradox',
              'You are sending requests faster than time flows. Please wait '
              'for causality to catch up.'),
        500: ('\U0001F30C', 'Reality Unraveling',
              "The Weave of magic is tearing apart! Vecna's ritual is crashing "
              'the entire multiverse.'),
    },
    'tashas-cauldron': {
        400: ('\U0001F9EA', 'Potion Explosion',
              'You mixed the wrong ingredients in the cauldron. The request '
              'blew up in your face.'),
        401: ('\U0001FA9E', 'Mirror of Identification',
              "The magic mirror doesn't recognize your reflection. Please log "
              'in.'),
        403: ('\U0001F4D3', "Tasha's Diary",
              "These are Iggwilv's private notes! A potent warding glyph "
              'prevents you from reading them.'),
        404: ('\U0001F3A9', 'Rabbit Gone',
              "You reached into the magic hat, but there's absolutely nothing "
              'in there.'),
        429: ('\U0001F4DC', 'Scroll Burnout',
              'Reading that many scrolls at once is frying your retinas. Take '
              'a short rest.'),
        500: ('\u2728', 'Wild Magic Cascade',
              'We rolled a 1 on the wild magic surge table. We are currently '
              'all potted plants.'),
    },
    'xanathars-guide': {
        400: ('\U0001F3B2', 'Loaded Dice',
              'We detected an invalid roll in your request parameters. No '
              'cheating in the tavern!'),
        401: ('\U0001F5E3\uFE0F', "Thieves' Cant Failed",
              "You don't know the secret slang. The rogue at the door won't "
              'let you in.'),
        403: ('\U0001F6AB', 'Blacklisted',
              "You've been marked by the Zhentarim. You are permanently "
              'forbidden from this endpoint.'),
        404: ('\U0001F4A5', 'Disintegrated',
              'A disintegration ray just vaporized the page you were looking '
              "for. There's only a pile of dust left."),
        429: ('\U0001F4B0', 'Coin Jam',
              "You're throwing bribes at the guards too quickly. Let them "
              'count the gold first!'),
        500: ('\U0001F4A4', 'Beholder Dream',
              'Xanathar fell asleep and dreamed of a rogue server process, '
              'spawning a catastrophic anomaly!'),
    },
    'vintage-arcade': {
        400: ('\U0001F579\uFE0F', 'Button Mash Error',
              'You hit A, B, X, Y, and Start all at once. The console didn\'t '
              'understand that combo.'),
        401: ('\U0001FA99', 'Insert Coin',
              'CREDITS: 0. You must insert a token to continue to this '
              'screen.'),
        403: ('\U0001F451', 'High Score Board Only',
              'You must beat the top score of "AAA" to view this secret '
              'level.'),
        404: ('\U0001F4C1', 'Missing ROM',
              '404_FILE_MISSING. The floppy disk containing this data seems to '
              'be corrupted.'),
        429: ('\U0001F6D1', 'Chill Out, Player 1',
              'The CPU is overheating from your frantic inputs. Pause the game '
              'for a second.'),
        500: ('\U0001F50C', 'Someone Tripped on the Cord',
              'The power cable got yanked out of the wall. Everything is '
              'gone.'),
    },
    'military-terminal': {
        400: ('\u274C', 'INVALID_PROTOCOL',
              'You used a civilian handshake for a military endpoint. Request '
              'rejected.'),
        401: ('\U0001F6E1\uFE0F', 'Authentication Timeout',
              'Your session in the war room has expired. Log in again, '
              'soldier.'),
        403: ('\U0001F512', 'Executive Lockout',
              'The commander has sealed this terminal. Only a Five-Star '
              'General can bypass this block.'),
        404: ('\u2B1B', 'DATA_EXPUNGED',
              'The file you are looking for has been heavily redacted and '
              'removed from the archives. That operation never existed. And if '
              'you keep asking about it, neither will you.'),
        429: ('\U0001F4E1', 'DDoS Detected',
              'Incoming traffic exceeds radar capabilities. Initiating '
              'packet-dropping countermeasures.'),
        500: ('\U0001F6F0\uFE0F', 'Satellite Uplink Lost',
              'A solar flare just destroyed our orbital relay. The internal '
              'network is totally dark.'),
    },
    'analog-archive': {
        400: ('\U0001F4DD', 'Illegible Handwriting',
              'We tried to process your file, but your cursive is unreadable. '
              'Please fill out a new form in block letters.'),
        401: ('\U0001FAAA', 'Show Your Badge',
              'The clerk refuses to take your folder. You need to show a valid '
              'company ID to the front desk first.'),
        403: ('\U0001F5C4\uFE0F', 'Locked Cabinet',
              'You are trying to pry open a locked filing drawer. You do not '
              'hold the key for this specific archive.'),
        404: ('\U0001F5D1\uFE0F', 'Shredded Paper',
              'The file you are looking for has been sent to the industrial '
              'shredder. There are only thin paper ribbons left.'),
        429: ('\U0001F975', 'Overworked Clerk',
              'The archivist can only stamp documents so fast! Give them a '
              'moment to catch up with your massive stack of requests.'),
        500: ('\U0001F525', 'Archive Fire',
              'Someone left a cigarette burning on a stack of old reports. The '
              'back office is currently dealing with a chaotic emergency.'),
    },
}

# The English "type" label per HTTP status, shown as `<label> / <code>` in
# error.html. Fixed per code (never per theme), so it lives here once.
ERROR_TYPE_EN = {
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
}


def theme_errors(theme_id, code):
    """Return (icon, title, msg, type_en) for one theme + HTTP status code.

    Looks up the active theme's set in THEME_ERRORS, falling back to
    DEFAULT_THEME for any theme (or any individual status) that hasn't defined
    its own copy, so every page renders a sensible error even before a new
    theme's wording is written. `type_en` comes from ERROR_TYPE_EN, which is
    keyed by status alone. A completely unknown status falls back to 500's set.
    """
    code = int(code)
    theme = clean_theme(theme_id)
    table = THEME_ERRORS.get(theme, THEME_ERRORS[DEFAULT_THEME])
    entry = table.get(code)
    if entry is None:
        # This theme doesn't define this code: try the default theme, then 500.
        entry = (THEME_ERRORS[DEFAULT_THEME].get(code)
                 or THEME_ERRORS[DEFAULT_THEME][500])
    icon, title, msg = entry
    type_en = ERROR_TYPE_EN.get(code, ERROR_TYPE_EN[500])
    return icon, title, msg, type_en


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
    # Analog Archive theme. Special Elite (typewriter display) and Courier
    # Prime (report/screenplay body) are both single-family faces; Courier
    # Prime carries an ital+wght tuple so bold/italic report text renders.
    'Special Elite': 'family=Special+Elite',
    'Courier Prime': 'family=Courier+Prime:ital,wght@0,400;0,700;1,400;1,700',
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
