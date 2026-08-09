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
    blurb='Necromancy: arcane violet, magenta magic, and lich gold.',
    fonts=('Grenze Gotisch', 'EB Garamond'),
    scale=1.75,
    vars={
        '--bg': '#130026',
        '--bg-panel': '#281140',
        '--ink': '#f4e09e',
        '--ink-dim': '#b388b3',
        '--accent': '#ff4791',
        '--accent-2': '#d4af37',
        '--border': '#080012',
        '--shadow': '#000000',
        '--good': '#b89645',
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
