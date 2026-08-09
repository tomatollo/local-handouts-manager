"""Candlekeep Mysteries -- the great library.

Candle-warm parchment, ink, and old leather. A library of mysteries, so it
leans scholarly: EB Garamond as an old-book display with a matching serif body.
"""

from ..base import Theme

THEME = Theme(
    id='candlekeep',
    name='Candlekeep Mysteries',
    blurb='The great library: candle-warm parchment, ink, and old leather.',
    fonts=('EB Garamond', 'Lora'),
    scale=1.55,
    vars={
        '--bg': '#15110a',          # dim library, candle shadow
        '--bg-panel': '#201a10',    # old leather binding
        '--ink': '#efe6cf',         # candle-lit page
        '--ink-dim': '#a99a7a',
        '--accent': '#e0a53a',      # candle flame amber
        '--accent-2': '#8a6f3a',    # aged gilt
        '--border': '#0b0805',
        '--shadow': '#000000',
        '--good': '#6a8c52',
    },
    home_label='Return to the Stacks (Home)',
    errors={
        400: ('\U0001FAB6', 'Smudged Ink',
              'Your query blotted across the page. The scribes cannot read a '
              'request written so carelessly.'),
        401: ('\U0001F4D6', 'No Gift of Knowledge',
              'Candlekeep admits only those who bring a book it lacks. You '
              'have brought nothing new.'),
        403: ('\U0001F5DD\uFE0F', 'Restricted Stacks',
              'These shelves are sealed to visitors. Only the Avowed may walk '
              'the inner archives.'),
        404: ('\U0001F4DA', 'Misfiled Tome',
              'The book you seek is not on its shelf. Somewhere in a million '
              'volumes, it has been misplaced.'),
        429: ('\U0001F56F\uFE0F', 'Reading Too Fast',
              'You are pulling tomes faster than the Avowed can reshelve them. '
              'Slow down and let the dust settle.'),
        500: ('\U0001F525', 'Archive Ablaze',
              'A candle tipped onto the manuscripts. The Avowed are fighting '
              'the flames while the archive recovers.'),
    },
)
