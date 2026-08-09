"""Dungeon Torch -- the default theme.

Soot, torchlight and pixels: the generic 8-bit look the app ships with. It is
also DEFAULT_THEME (see theming/registry.py), so it is the fallback whenever a
stored theme id is unknown, and it supplies the fallback error-page wording any
other theme borrows for a status it hasn't written itself -- including the
home_label below, which is the button text a theme falls back to when it leaves
its own blank.
"""

from ..base import Theme

THEME = Theme(
    id='dungeon-torch',
    name='Dungeon Torch',
    blurb='The default: soot, torchlight, and pixels.',
    fonts=('Press Start 2P', 'IM Fell English'),
    scale=1,
    vars={
        '--bg': '#1a1614',
        '--bg-panel': '#2a2320',
        '--ink': '#f4e9d8',
        '--ink-dim': '#b9a78d',
        '--accent': '#e8a83a',
        '--accent-2': '#c0532b',
        '--border': '#0d0b0a',
        '--shadow': '#000000',
        '--good': '#6a9c4f',
    },
    home_label='Flee the Dungeon (Home)',
    errors={
        400: ('\U0001F4A5', 'Wild Magic Surge',
              'You mixed up the spell components. Your request fizzled out in '
              'a shower of harmless sparks.'),
        401: ('\U0001F6D1', 'Failed Stealth Check',
              "'Halt! Who goes there?' The guards caught you trying to sneak "
              'in without the proper passphrase.'),
        403: ('\U0001F6E1\uFE0F', 'Magic Circle',
              'A powerful barrier blocks your path. You lack the required '
              'alignment or level to enter this area.'),
        404: ('\U0001F3B2', 'Critical Fail',
              'Natural 1 on Perception, you got lost. The room is shrouded in '
              'darkness, and the page you are looking for seems to have '
              'vanished into the Astral Plane or been devoured by a Mimic.'),
        429: ('\U0001F6D1', 'Slow Down, Adventurer',
              'You are hammering the gates faster than the guards can answer. '
              'Wait a moment and try again.'),
        500: ('\u26A1', 'The Weave is Tearing',
              'The Dungeon Master spilled coffee on the campaign notes. The '
              'fabric of reality is temporarily unstable.'),
    },
)
