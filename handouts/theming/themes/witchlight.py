"""The Wild Beyond the Witchlight -- a feywild carnival.

Candy pinks, dream teal, and fairy lights. A whimsical fey carnival, so it
takes an ornate storybook display (Cinzel Decorative) with a soft Cormorant
Garamond body.
"""

from ..base import Theme

THEME = Theme(
    id='witchlight',
    name='The Wild Beyond the Witchlight',
    blurb='A feywild carnival: candy pinks, dream teal, and fairy lights.',
    fonts=('Cinzel Decorative', 'Cormorant Garamond'),
    scale=1.45,
    vars={
        '--bg': '#14101e',          # twilight feywild sky
        '--bg-panel': '#221a30',    # dusky carnival violet
        '--ink': '#f4e9f2',         # moonlit cream
        '--ink-dim': '#b79cc0',
        '--accent': '#f06eaa',      # witchlight carnival pink
        '--accent-2': '#48c9c0',    # fey dream teal
        '--border': '#0b0713',
        '--shadow': '#000000',
        '--good': '#5fc0a0',
    },
    home_label='Follow the Lights Home',
    errors={
        400: ('\U0001F3A0', 'Muddled Wish',
              'You phrased your wish carelessly and the carnival misheard it. '
              'Try asking again, more sweetly.'),
        401: ('\U0001F39F\uFE0F', 'No Carnival Ticket',
              'You have no ticket to the Witchlight. The barkers turn you away '
              'from the gates.'),
        403: ('\U0001F344', 'Hourglass Coven',
              'The Hourglass has forbidden this path. Its hags do not care to '
              'let you wander here.'),
        404: ('\U0001F98B', 'Lost in the Feywild',
              'The path folded away like a dream. What you sought drifted off '
              'into the endless carnival.'),
        429: ('\U0001F36D', 'Too Much Wonder',
              'You are rushing the marvels too fast. The Feywild spins -- take '
              'a breath and wander slower.'),
        500: ('\U0001F387', 'Carnival Collapse',
              'The whole carnival winked out at once. The fey are stitching '
              'the dream back together.'),
    },
)
