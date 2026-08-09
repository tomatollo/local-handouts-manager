'''Xanathar's Guide to Everything -- the watching beholder.

Acid green, magenta, and a staring eye. Nova Square is a squared, alien-tech
display face -- criminal-syndicate signage / a surveillance readout, but fully
legible. Cardo keeps the body text a clean serif.

The extra_css makes the page an eye: a magenta/green pupil dilates at the
centre, faint scanlines crawl like a surveillance feed, panels iris a thin
ring, and buttons fire an eye-ray flash on hover. All motion sits behind
prefers-reduced-motion.
'''

from ..base import Theme

_EXTRA_CSS = """
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
"""

THEME = Theme(
    id='xanathars-guide',
    name="Xanathar's Guide to Everything",
    blurb='The beholder watches: acid green, magenta, and a staring eye.',
    fonts=('Nova Square', 'Cardo'),
    scale=1.5,
    vars={
        '--bg': '#06090a',          # black observation room
        '--bg-panel': '#0e1518',    # dark scrying glass
        '--ink': '#e7f5ec',         # cold white
        '--ink-dim': '#7fa597',     # dim eye-shine
        '--accent': '#8cff3b',      # aberrant acid green
        '--accent-2': '#ff2fd0',    # eye-stalk magenta
        '--border': '#020404',
        '--shadow': '#000000',
        '--good': '#48d97a',
    },
    extra_css=_EXTRA_CSS,
    home_label='Slip Past the Eye (Home)',
    errors={
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
)
