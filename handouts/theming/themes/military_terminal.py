'''Military Terminal -- Cold War readout: phosphor green on black.

Share Tech Mono is a clean monospace with a technical, stencilled feel (a field
terminal, not an arcade); VT323 carries the body as a matching CRT monospace.
Share Tech Mono is normal-width, so headings need a scale bump to fill the
calibrated sizes.

The extra_css is minimal on purpose: a military terminal is spartan. Just fine,
static scanlines and a phosphor tint (no motion at all), squared panels, and
amber only where something needs attention. The quiet counterpoint to Vintage
Arcade.
'''

from ..base import Theme

_EXTRA_CSS = """
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
"""

THEME = Theme(
    id='military-terminal',
    name='Military Terminal',
    blurb='Cold War readout: phosphor green on black, strictly business.',
    fonts=('Share Tech Mono', 'VT323'),
    scale=1.5,
    vars={
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
    extra_css=_EXTRA_CSS,
    home_label='Return to Base (Home)',
    errors={
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
)
