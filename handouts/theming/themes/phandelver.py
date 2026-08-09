"""Lost Mine of Phandelver.

Classic fantasy: forest, parchment, goblin country. The one LIGHT theme in the
table -- dark ink on a light parchment panel -- so --ink is dark here where
most themes keep it light. Everything reads from the tokens, so both directions
work without special-casing.
"""

from ..base import Theme

THEME = Theme(
    id='phandelver',
    name='Lost Mine of Phandelver',
    blurb='Classic fantasy: forest, parchment, goblin country.',
    fonts=('MedievalSharp', 'Merriweather'),
    scale=1.6,
    vars={
        '--bg': '#1a3300',
        '--bg-panel': '#1e2117',
        '--ink': '#e2dec3',
        '--ink-dim': '#9c9477',
        '--accent': '#499149',
        '--accent-2': '#b8913e',
        '--border': '#090b07',
        '--shadow': '#000000',
        '--good': '#5a8c46',
    },
    home_label='Back to the Mine Road (Home)',
    errors={
        400: ('\U0001F4DC', 'Illegible Map',
              "Gundren's map seems stained with ale. We couldn't read your "
              'request parameters.'),
        401: ('\U0001F6E1\uFE0F', 'Neverwinter Guard',
              '"Halt, traveler!" You don\'t have the proper identification '
              'papers to enter this district.'),
        403: ('\U0001F6AA', 'Sealed Vault',
              'The doors to the Tresendar vaults are locked tight. Only the '
              'guild master holds the key.'),
        404: ('\U0001F573\uFE0F', 'Empty Mine',
              'You dug too deep in the wrong spot. This tunnel leads to a dead '
              'end.'),
        429: ('\U0001F3F9', 'Goblin Swarm',
              'Too many arrows flying at once! Take cover and wait a moment '
              'before charging again.'),
        500: ('\U0001F30B', 'Cave-In!',
              'The ceiling of the mine just collapsed! Our goblin engineers '
              'are digging the server out of the rubble.'),
    },
)
