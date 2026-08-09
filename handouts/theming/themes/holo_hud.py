'''Holo HUD -- sci-fi interface: black glass, amber telemetry, cut-corner frames.

Orbitron is THE spaceship-UI display face (geometric, angular, neon); Share
Tech Mono is the clean terminal/data monospace for the body, exactly the
dashboard look. Orbitron is normal-width and runs a little wide, so a moderate
scale bump.

The extra_css is a heads-up display: cut-corner frames (clip-path) on the
panels with amber corner brackets, a faint dot-grid + scanline wash on the
board, monospace data glow on headings, and hover states that snap like a
targeting reticle. Motion is minimal and behind prefers-reduced-motion; the HUD
mostly sits still and precise.
'''

from ..base import Theme

_EXTRA_CSS = """
/* ==== Holo HUD: sci-fi heads-up display =========================== */

/* ---- The board: black glass, dot-grid + faint scanlines ----------
   A technical dot grid and very low-contrast scanlines texture the
   black so it reads as a screen, plus a soft amber/cyan glow bleeding
   from the corners like a powered console. Pinned to the viewport. */
body {
  background-color: var(--bg);
  background-image:
    radial-gradient(circle at 50% 50%, rgba(255,255,255,0.05) 0.5px, transparent 0.5px),
    repeating-linear-gradient(0deg, rgba(0,0,0,0.30) 0 1px, transparent 1px 3px),
    radial-gradient(70% 50% at 0% 0%, rgba(245,165,36,0.06), transparent 60%),
    radial-gradient(70% 50% at 100% 100%, rgba(49,210,242,0.06), transparent 60%);
  background-size: 22px 22px, 100% 100%, 100% 100%, 100% 100%;
  background-attachment: fixed;
  color: var(--ink);
}
.subtitle { color: var(--ink-dim); }

/* ---- Panels: cut-corner HUD frames -------------------------------
   clip-path bevels the top-left and bottom-right corners so a panel
   reads as an angular HUD plate, not a rounded card. A thin cyan inner
   line + amber corner brackets (::before/::after) complete the frame.
   All bracket pseudo-elements are non-interactive. */
.panel, .wiki-card, .handout-card, .folder-card {
  position: relative;
  background:
    linear-gradient(160deg, rgba(49,210,242,0.03), rgba(0,0,0,0) 45%),
    var(--bg-panel);
  border: 1px solid var(--border);
  clip-path: polygon(
    14px 0, 100% 0, 100% calc(100% - 14px),
    calc(100% - 14px) 100%, 0 100%, 0 14px);
  box-shadow: inset 0 0 0 1px rgba(49,210,242,0.10),
              inset 0 0 24px rgba(0,0,0,0.5);
}
/* Amber corner bracket, top-left. */
.panel::before {
  content: "";
  position: absolute;
  top: 6px; left: 6px;
  width: 16px; height: 16px;
  border-top: 2px solid var(--accent);
  border-left: 2px solid var(--accent);
  pointer-events: none;
  opacity: 0.85;
}
/* Amber corner bracket, bottom-right. */
.panel::after {
  content: "";
  position: absolute;
  bottom: 6px; right: 6px;
  width: 16px; height: 16px;
  border-bottom: 2px solid var(--accent);
  border-right: 2px solid var(--accent);
  pointer-events: none;
  opacity: 0.85;
}

/* ---- Headings: telemetry readouts with a soft amber glow --------- */
h1, h2, h3, .pixel {
  color: var(--accent);
  letter-spacing: 2px;
  text-transform: uppercase;
  text-shadow: 0 0 6px rgba(245,165,36,0.4);
}
/* A leading bracket glyph on the top titles, like a HUD label. */
h1::before { content: "[ "; color: var(--accent-2); }
h1::after  { content: " ]"; color: var(--accent-2); }
/* Section heads use the cyan data colour to separate them from the amber. */
h2, h3 { color: var(--accent-2); text-shadow: 0 0 5px rgba(49,210,242,0.35); }

/* ---- Buttons: reticle-snap on hover ------------------------------
   A flat dark plate with a cut corner and an amber label. Hover fills
   with amber and snaps the text to black, like selecting a system on a
   targeting readout. */
.btn {
  background: #0e1219;
  color: var(--accent);
  border: 1px solid var(--accent);
  clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px),
                     calc(100% - 8px) 100%, 0 100%, 0 8px);
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: background 0.1s steps(2, end), color 0.1s steps(2, end),
              box-shadow 0.15s ease;
}
@media (hover: hover) {
  .btn:hover {
    background: var(--accent);
    color: #05060a;
    box-shadow: 0 0 10px rgba(245,165,36,0.6);
  }
  /* Ghost / nav buttons stay outline-only until hovered, so a toolbar of
     them reads as a HUD strip rather than a wall of filled chips. */
  .btn--ghost {
    background: transparent;
    color: var(--ink-dim);
    border-color: var(--border);
  }
  .btn--ghost:hover {
    background: rgba(49,210,242,0.12);
    color: var(--accent-2);
    border-color: var(--accent-2);
    box-shadow: 0 0 8px rgba(49,210,242,0.4);
  }
  /* POP is the priority alert: cyan glow instead of amber. */
  .btn--pop:hover {
    background: var(--accent-2);
    color: #05060a;
    box-shadow: 0 0 12px rgba(49,210,242,0.7);
  }
}
/* Active nav = a lit amber system. */
.hub-mode__btn--active,
.view-btn--active,
.drawer__link--active {
  background: var(--accent);
  color: #05060a;
  border-color: var(--accent);
  box-shadow: 0 0 8px rgba(245,165,36,0.5);
}

/* ---- Count badges: hex-ish data chips ---------------------------- */
.count-badge {
  background: rgba(49,210,242,0.15);
  color: var(--accent-2);
  border: 1px solid var(--accent-2);
  clip-path: polygon(4px 0, 100% 0, 100% calc(100% - 4px),
                     calc(100% - 4px) 100%, 0 100%, 0 4px);
}

/* ---- Tags: bracketed labels -------------------------------------- */
.tag {
  background: rgba(245,165,36,0.10);
  color: var(--accent);
  border: 1px solid rgba(245,165,36,0.4);
}
.tag--session { color: var(--accent-2); border-color: rgba(49,210,242,0.4); }

/* ---- Tree view: terminal readout, cyan connectors ---------------- */
.handout-tree { color: rgba(49,210,242,0.5); }
.handout-tree .tree-node { color: var(--accent); }
.handout-tree .tree-leaf { color: var(--ink); }
.handout-tree .tree-leaf:hover,
.handout-tree .tree-leaf--active { color: var(--accent-2); }
"""

THEME = Theme(
    id='holo-hud',
    name='Holo HUD',
    blurb='Sci-fi interface: black glass, amber telemetry, and cut-corner frames.',
    fonts=('Orbitron', 'Share Tech Mono'),
    scale=1.3,
    vars={
        # Pure black glass panel with the faintest blue lift, like the
        # dashboard screens in the references.
        '--bg': '#05060a',
        '--bg-panel': '#0b0e14',    # a powered readout panel, barely lifted
        '--ink': '#d8e0ea',         # cool white telemetry text
        '--ink-dim': '#6f7d90',     # dimmed labels / secondary readouts
        '--accent': '#f5a524',      # amber: the dominant HUD accent
        '--accent-2': '#31d2f2',    # cyan: the secondary data highlight
        '--border': '#1c2430',      # dark blue-grey hairline
        '--shadow': '#000000',
        '--good': '#31d2f2',        # "visible" reuses the cyan data glow
    },
    extra_css=_EXTRA_CSS,
    home_label='Reset Navigation (Home)',
    errors={
        400: ('\u26A0\uFE0F', 'Malformed Packet',
              'The data stream failed checksum. Your request packet was '
              'rejected by the input parser.'),
        401: ('\U0001F510', 'Biometric Mismatch',
              'Identity not recognised. This terminal requires a valid access '
              'signature before it will respond.'),
        403: ('\U0001F6F0\uFE0F', 'Clearance Denied',
              'Your access level is insufficient for this sector. The system '
              'has logged the attempt.'),
        404: ('\U0001F4E1', 'Signal Lost',
              'No telemetry at these coordinates. The node you are querying is '
              'offline or was never mapped.'),
        429: ('\u23F1\uFE0F', 'Bandwidth Exceeded',
              'Input rate over threshold. Throttling engaged -- wait for the '
              'buffer to clear before transmitting again.'),
        500: ('\u26A1', 'Core Fault',
              'A critical exception cascaded through the main core. Automatic '
              'recovery routines are re-initialising the system.'),
    },
)
