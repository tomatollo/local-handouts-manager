'''Vintage Arcade -- CRT phosphor and neon synthwave: insert coin to continue.

Press Start 2P is the pixel display face the base CSS already sugars with a
stepped "pixel" shadow; VT323 is a monospace CRT terminal face for long text.
Press Start 2P is the calibrated face, so scale stays 1.

The extra_css is a CRT screen look without seizure-inducing motion: scanlines
and a phosphor tint texture the screen, a retro crosshair/pixel cursor replaces
the pointer, buttons fire a mechanical stepped snap plus a soft neon bloom on
hover, panels carry a thin neon bezel, and headings glow neon in the dark. No
flicker, no roll -- the CRT sits still so it never triggers a headache.
'''

from ..base import Theme

_EXTRA_CSS = """
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
"""

THEME = Theme(
    id='vintage-arcade',
    name='Vintage Arcade',
    blurb='CRT phosphor and neon synthwave: insert coin to continue.',
    fonts=('Press Start 2P', 'VT323'),
    scale=1,
    vars={
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
    extra_css=_EXTRA_CSS,
    home_label='Insert Coin to Continue (Home)',
    errors={
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
)
