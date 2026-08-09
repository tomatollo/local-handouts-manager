'''Tasha's Cauldron of Everything -- chaotic arcana.

Bubbling violet brew, copper, and malachite. Cinzel Decorative is an ornate,
flourished display (the grimoire feel of an experimental spellbook); Cormorant
Garamond keeps the long text a fine alchemical serif.

The extra_css is the juice: Tasha is chaos and experiment, so the cauldron
never sits still. A slow radial "brew" simmers on the page background, panels
shimmer a copper rim, headings pour a violet-to-copper gradient, and buttons
pulse an arcane glow on hover. All motion sits behind prefers-reduced-motion.
'''

from ..base import Theme

_EXTRA_CSS = """
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
"""

THEME = Theme(
    id='tashas-cauldron',
    name="Tasha's Cauldron of Everything",
    blurb='Chaotic arcana: bubbling violet brew, copper, and malachite.',
    fonts=('Cinzel Decorative', 'Cormorant Garamond'),
    scale=1.45,
    vars={
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
    extra_css=_EXTRA_CSS,
    home_label='Back to the Cauldron (Home)',
    errors={
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
)
