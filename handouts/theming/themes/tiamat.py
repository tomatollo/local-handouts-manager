"""The Rise of Tiamat -- draconic majesty: scale-grey, crimson, gold hoards."""

from ..base import Theme

THEME = Theme(
    id='tiamat',
    name='The Rise of Tiamat',
    blurb='Draconic majesty: scale-grey, crimson, and gold hoards.',
    fonts=('Cinzel', 'Playfair Display'),
    scale=1.5,
    vars={
        '--bg': '#141517',          # metallic dragon-scale anthracite
        '--bg-panel': '#221818',    # dark crimson
        '--ink': '#f0eee9',         # cream
        '--ink-dim': '#a3998f',
        '--accent': '#d4b224',      # ducat gold
        '--accent-2': '#ab2c38',
        '--border': '#08090a',
        '--shadow': '#000000',
        '--good': '#4a8562',
    },
    home_label='Retreat to the Council (Home)',
    errors={
        400: ('\U0001FA99', 'Fake Tribute',
              'You tried to offer counterfeit gold to the hoard. The cult '
              'rejects your malformed request.'),
        401: ('\U0001F5DD\uFE0F', "Wyrmspeaker's Seal",
              'You lack the proper cult passphrase. The guards are drawing '
              'their scimitars.'),
        403: ('\U0001F534', 'Chromatic Barrier',
              "Tiamat's magic seals this domain. Mortals without a "
              "Wyrmspeaker's blessing are strictly forbidden."),
        404: ('\U0001F48E', 'Plundered Hoard',
              'The treasure you seek is gone. Adventurers probably looted this '
              'page yesterday.'),
        429: ('\U0001F6D1', 'Hold the Line',
              "You're sending troops to the frontline too quickly. Let the "
              'vanguard breathe!'),
        500: ('\u2694\uFE0F', 'Council Uproar',
              'The factions of Waterdeep are fighting again. Our backend '
              'diplomacy has completely broken down.'),
    },
)
