"""Out of the Abyss -- Underdark: obsidian dark, drow violet, fungal neon."""

from ..base import Theme

THEME = Theme(
    id='out-of-the-abyss',
    name='Out of the Abyss',
    blurb='Underdark: obsidian dark, drow violet, fungal neon.',
    fonts=('Metamorphous', 'Cardo'),
    scale=1.5,
    vars={
        '--bg': '#09080b',
        '--bg-panel': '#17131e',
        '--ink': '#e6e3eb',
        '--ink-dim': '#9890a3',
        '--accent': '#9b6bd9',
        '--accent-2': '#32b88b',
        '--border': '#000000',
        '--shadow': '#000000',
        '--good': '#469c76',
    },
    home_label='Escape the Underdark (Home)',
    errors={
        400: ('\U0001F578\uFE0F', 'Tangled Web',
              "Your request got caught in Lolth's webs. The syntax is "
              'completely tangled.'),
        401: ('\u26D3\uFE0F', 'Velkynvelve Prisoner',
              "Escaped slaves don't have access rights here. The Drow "
              'priestesses demand your surrender.'),
        403: ('\U0001F9E0', 'Illithid Enclave',
              'The Elder Brain rejects your mind. Your psionic clearance level '
              'is insufficient.'),
        404: ('\U0001F573\uFE0F', 'Swallowed by the Dark',
              'The page you seek has been consumed by the endless abyss of the '
              'Underdark.'),
        429: ('\U0001F300', 'Descending Madness',
              'The madness of the Abyss is compounding too quickly. Take a '
              'long rest.'),
        500: ('\U0001F9E0', 'Mind Flayer Blast',
              'An Illithid psychic blast just stunned our backend processes. '
              'Rebooting...'),
    },
)
