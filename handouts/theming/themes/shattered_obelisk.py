"""Phandelver and Below: The Shattered Obelisk.

The mine goes wrong: shattered stone, aberrant violet, dread. Metamorphous --
a heavy stone-carved display -- gives the sequel its own grim, aberrant weight
rather than reusing Phandelver's MedievalSharp. Same face Out of the Abyss uses
at the same 1.5 scale.
"""

from ..base import Theme

THEME = Theme(
    id='shattered-obelisk',
    name='Phandelver and Below: The Shattered Obelisk',
    blurb='The mine goes wrong: shattered stone, aberrant violet, and dread.',
    fonts=('Metamorphous', 'Merriweather'),
    scale=1.5,
    vars={
        '--bg': '#141019',          # cracked-stone dark with a violet cast
        '--bg-panel': '#1e1826',    # obelisk basalt
        '--ink': '#e8e0d0',         # weathered parchment
        '--ink-dim': '#9a8fa0',
        '--accent': '#a06fd0',      # aberrant obelisk violet
        '--accent-2': '#c98a3e',    # the old Phandelver gold, tarnished
        '--border': '#0a0710',
        '--shadow': '#000000',
        '--good': '#5a8c72',
    },
    home_label='Back to the Surface (Home)',
    errors={
        400: ('\U0001FAA8', 'Cracked Rune',
              'The rune you inscribed is fractured. Your malformed request '
              'crumbled before it could resolve.'),
        401: ('\U0001F6E1\uFE0F', 'Redbrand Checkpoint',
              'The Redbrands bar your way. You lack the token that lets you '
              'pass into Tresendar.'),
        403: ('\U0001F52E', 'Aberrant Ward',
              'The shattered obelisk pulses and rejects you. This chamber is '
              'sealed against the unworthy.'),
        404: ('\U0001F573\uFE0F', 'Collapsed Shaft',
              'The tunnel caved in ahead. Whatever you sought is buried '
              'somewhere beyond the rubble.'),
        429: ('\U0001F300', 'Warping Presence',
              'Reality is bending too fast around you. Step back from the '
              'obelisk and let it settle.'),
        500: ('\U0001F311', 'Obelisk Backlash',
              'The obelisk discharged raw aberrant power through the server. '
              'Containment routines are re-forming reality.'),
    },
)
