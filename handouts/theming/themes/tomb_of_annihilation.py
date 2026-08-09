"""Tomb of Annihilation -- jungle survival: moss, limestone, Acererak gold."""

from ..base import Theme

THEME = Theme(
    id='tomb-of-annihilation',
    name='Tomb of Annihilation',
    blurb='Jungle survival: moss, limestone, and Acererak gold.',
    fonts=('Pirata One', 'Lora'),
    scale=1.4,
    vars={
        '--bg': '#111713',
        '--bg-panel': '#1a241d',
        '--ink': '#e4e8e1',
        '--ink-dim': '#8a9a8f',
        '--accent': '#c99b22',
        '--accent-2': '#209a89',
        '--border': '#0a0f0c',
        '--shadow': '#000000',
        '--good': '#4e8c56',
    },
    home_label='Back to Camp (Home)',
    errors={
        400: ('\U0001F9ED', 'Broken Compass',
              'Your magnetic compass is spinning wildly in the jungle. Your '
              'navigation parameters are invalid.'),
        401: ('\U0001F525', 'Flaming Fist Toll',
              "You haven't paid for your charter of exploration. The Flaming "
              'Fist denies you passage.'),
        403: ('\U0001F9FF', "Soulmonger's Ward",
              'Acererak has sealed this chamber. Your soul is not strong '
              'enough to pierce the barrier.'),
        404: ('\U0001F5FA\uFE0F', "Syndra's Missing Map",
              "The hex grid for this area is blank. You haven't explored this "
              'part of Chult yet.'),
        429: ('\U0001F99F', 'Jungle Fever',
              "You're marching through the sweltering jungle too quickly. Take "
              'a sip of water and slow down.'),
        500: ('\U0001F9D9\u200D\u2642\uFE0F', "Acererak's Laugh",
              'The archlich just cast Meteor Swarm on the server! We are '
              'trying to cast Mending.'),
    },
)
