"""Mythic Odysseys of Theros -- Greek myth: marble, olive bronze, Nyx starlight.

Marcellus SC -- calligraphic Roman small-caps -- reads like letters carved into
a temple frieze, distinct from Tiamat's Cinzel. Playfair Display keeps the body
a high-contrast classical serif.
"""

from ..base import Theme

THEME = Theme(
    id='theros',
    name='Mythic Odysseys of Theros',
    blurb='Greek myth: sun-bleached marble, olive bronze, and Nyx starlight.',
    fonts=('Marcellus SC', 'Playfair Display'),
    scale=1.5,
    vars={
        '--bg': '#0d1016',          # Nyx night sky
        '--bg-panel': '#181c24',    # dark marble
        '--ink': '#f2ede2',         # sun-bleached stone
        '--ink-dim': '#9aa0ac',
        '--accent': '#d9a441',      # temple bronze / olive gold
        '--accent-2': '#5b8fd0',    # Nyx starfield blue
        '--border': '#070a0f',
        '--shadow': '#000000',
        '--good': '#5a9c86',
    },
    home_label='Return to the Temple (Home)',
    errors={
        400: ('\U0001F3FA', 'Rejected Offering',
              'Your offering displeased the gods. The malformed rite was cast '
              'back down from Nyx.'),
        401: ('\u26A1', "Without the Gods' Favour",
              'No deity vouches for you. The temple guardians will not grant '
              'passage to the unfavoured.'),
        403: ('\U0001F3DB\uFE0F', 'Sealed Temple',
              'This sanctum is closed to mortals. Only a hero of legend may '
              'cross its marble threshold.'),
        404: ('\U0001F30C', 'Lost to Nyx',
              'The path dissolved into the starfield. What you sought has '
              'drifted into the night sky of Nyx.'),
        429: ('\U0001F3C3', 'Hubris',
              'You demand too much, too fast -- the gods call it hubris. '
              'Temper your pride before they notice.'),
        500: ('\u26A1', 'Wrath of the Gods',
              'A god took offence and hurled a thunderbolt through the server. '
              'The oracles are restoring the mortal realm.'),
    },
)
