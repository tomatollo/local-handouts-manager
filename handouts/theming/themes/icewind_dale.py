"""Icewind Dale -- endless night, frost, and one cold star."""

from ..base import Theme

THEME = Theme(
    id='icewind-dale',
    name='Icewind Dale',
    blurb='Endless night, frost, and one cold star.',
    fonts=('Cinzel', 'Lora'),
    scale=1.5,
    vars={
        '--bg': '#101822',
        '--bg-panel': '#1a2634',
        '--ink': '#e6f0f7',
        '--ink-dim': '#93a8bb',
        '--accent': '#7fd4e8',
        '--accent-2': '#c8dae6',
        '--border': '#060b11',
        '--shadow': '#000000',
        '--good': '#6aa9c4',
    },
    home_label='Back to the Fire (Home)',
    errors={
        400: ('\U0001F976', 'Frostbitten Fingers',
              'Your hands were shaking too much from the cold to type the URL '
              'correctly.'),
        401: ('\U0001F989', "Auril's Test",
              'The Frostmaiden requires a sacrifice of warmth before she '
              'grants you passage.'),
        403: ('\U0001F3F0', 'Ythryn Quarantine',
              'The ancient Netherese city is on magical lockdown to prevent '
              'the spread of arcane blight.'),
        404: ('\U0001F328\uFE0F', 'Whiteout Condition',
              'The blizzard is too thick! The page you are looking for is '
              'completely buried in snow.'),
        429: ('\U0001F32C\uFE0F', 'Biting Winds',
              "You're pushing into the blizzard too fast. Stop and build a "
              'fire before you freeze to death.'),
        500: ('\u2744\uFE0F', 'Everlasting Rime',
              "Auril's spell just froze the entire backend infrastructure "
              'solid.'),
    },
)
