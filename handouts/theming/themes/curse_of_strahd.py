"""Curse of Strahd -- gothic horror: pitch, velvet, and bright blood.

Blackletter is narrow and ornate, so it needs the strongest scale bump of any
theme (1.9) to read at UI sizes.
"""

from ..base import Theme

THEME = Theme(
    id='curse-of-strahd',
    name='Curse of Strahd',
    blurb='Gothic horror: pitch, velvet, and bright blood.',
    fonts=('Bokor', 'IM Fell English'),
    scale=1.9,
    vars={
        '--bg': '#0a0a0a',          # pitch black
        '--bg-panel': '#2b1f2e',    # desaturated velvet plum
        '--ink': '#e3dac9',         # bone white
        '--ink-dim': '#948e98',
        '--accent': '#b22222',      # blood red
        '--accent-2': '#6e6a7a',
        '--border': '#000000',
        '--shadow': '#000000',
        '--good': '#5c7f5c',
    },
    home_label='Flee the Mists (Home)',
    errors={
        400: ('\U0001F0CF', 'Misread Tarokka',
              'Madame Eva shakes her head. You misinterpreted the cards, and '
              'your request is malformed.'),
        401: ('\u2709\uFE0F', 'No Invitation',
              'The gates of Castle Ravenloft remain closed. You have not been '
              'invited by the master of the domain.'),
        403: ('\U0001F9DB', "Strahd's Command",
              '"I am the Ancient. I am the Land." The vampire lord strictly '
              'forbids your presence here.'),
        404: ('\U0001F3DA\uFE0F', 'Phantom Village',
              'You arrived at the coordinates, but found only an abandoned, '
              'rotting husk of a page.'),
        429: ('\U0001F6AA', 'Frantic Knocking',
              "Pounding on the village doors won't make them open faster. The "
              'locals are terrified, wait a minute.'),
        500: ('\U0001F311', 'Dark Powers Intervene',
              'The mysterious entities of the shadowfell have corrupted the '
              "server's soul."),
    },
)
