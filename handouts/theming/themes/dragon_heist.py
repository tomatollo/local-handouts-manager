"""Waterdeep: Dragon Heist -- city of splendors: harbour blue, gold, intrigue.

Cormorant Unicase -- an elegant high-contrast unicase display -- gives the
grand, moneyed Waterdhavian nameplate its own look (not another Cinzel). Lora
keeps the body a readable serif for a city adventure.
"""

from ..base import Theme

THEME = Theme(
    id='dragon-heist',
    name='Waterdeep: Dragon Heist',
    blurb='City of splendors: harbour blue, gold coin, and intrigue.',
    fonts=('Cormorant Unicase', 'Lora'),
    scale=1.5,
    vars={
        '--bg': '#0e1622',          # Waterdeep harbour at night
        '--bg-panel': '#172433',    # deep sea-blue stone
        '--ink': '#eef2f7',
        '--ink-dim': '#93a5ba',
        '--accent': '#e6b422',      # dragon (gold coin) yellow
        '--accent-2': '#3f8fb0',    # harbour teal
        '--border': '#070b11',
        '--shadow': '#000000',
        '--good': '#4e9c8a',
    },
    home_label='Back to the Tavern (Home)',
    errors={
        400: ('\U0001F4DC', 'Forged Deed',
              'The property deed you presented is a forgery. The clerk at the '
              'Palace rejects your paperwork.'),
        401: ('\U0001F5DD\uFE0F', 'No Guild Token',
              'You have no writ from the guilds. The Waterdhavian watch will '
              'not let you through.'),
        403: ('\U0001F409', "Dragon's Vault",
              'The half-million gold is not for you. This vault is sealed to '
              'all but the holder of the Stone.'),
        404: ('\U0001FA99', 'Trail Gone Cold',
              'The coin led nowhere. The lead you were chasing has vanished '
              'into the city crowds.'),
        429: ('\U0001F3C3', 'Too Many Factions',
              "You're chasing every faction at once. Slow down before the "
              'whole city is on your tail.'),
        500: ('\u2694\uFE0F', 'Guild War',
              'The factions came to blows in the streets. The city is in '
              'chaos while order is restored.'),
    },
)
