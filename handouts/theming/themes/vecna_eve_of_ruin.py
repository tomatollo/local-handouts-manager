"""Vecna: Eve of Ruin -- necromancy: grave-dark, corpse-light green, violet.

The one green-accented theme in the table -- Vecna's necrotic pallor, so it
reads as unmistakably "the lich" beside the golds, blues and reds. Grenze
Gotisch is a blackletter that stays legible at UI sizes (the Whispered One's
gothic menace without Strahd's near-unreadable Unifraktur); it is wider and
more even than Unifraktur, so it needs a touch less scale bump than Strahd.
"""

from ..base import Theme

THEME = Theme(
    id='vecna-eve-of-ruin',
    name='Vecna: Eve of Ruin',
    blurb='Necromancy: grave-dark, corpse-light green, and rotten violet.',
    fonts=('Grenze Gotisch', 'EB Garamond'),
    scale=1.75,
    vars={
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
    home_label='Escape the Ritual (Home)',
    errors={
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
)
