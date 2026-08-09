"""Google Fonts URL building.

The css2 stylesheet URL for a set of faces. Two flavours are used:
  - one theme's two faces (fonts_url_for_theme), for the active-theme <head>;
  - every face at once (all_fonts_url_for), for the Appearance page's live
    preview, which renders each picker box in its own typeface.
Both return Markup because the `&` separators are URL syntax that Jinja's HTML
autoescaping would turn into `&amp;` and break.

These two take Theme objects. The app's public entry points -- fonts_url(id)
and all_fonts_url() -- live in registry.py, which has the THEMES table and so
can accept a string id / take no argument, exactly as the old module did.

FONT_QUERY holds the exact `family=` spec for faces that need more than a bare
family name. The css2 API rejects a bare `family=X` for families whose axes
have no default position, and it fails the WHOLE request when one family is
bad: a single unqualified name takes the other face down with it and the page
silently falls back to Georgia. So legacy/variable families spell their
ital/wght tuples out; axis tags stay alphabetical (ital before wght) and tuples
sorted, as the API requires.
"""

from markupsafe import Markup

# Faces needing more than a plain family name in the Google Fonts URL. Anything
# not listed here is requested as a bare `family=Name+With+Plusses`, which is
# correct for single-style faces.
FONT_QUERY = {
    'IM Fell English': 'family=IM+Fell+English:ital@0;1',
    'Merriweather': 'family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;'
                    '1,300;1,400;1,700;1,900',
    'Crimson Text': 'family=Crimson+Text:ital,wght@0,400;0,600;0,700;'
                    '1,400;1,600;1,700',
    'Cormorant Garamond': 'family=Cormorant+Garamond:ital,wght@0,300;0,400;'
                          '0,500;0,600;0,700;1,300;1,400;1,500;1,600;1,700',
    'Lora': 'family=Lora:ital,wght@0,400;0,500;0,600;0,700;'
            '1,400;1,500;1,600;1,700',
    'Playfair Display': 'family=Playfair+Display:ital,wght@0,400;0,500;0,600;'
                        '0,700;0,800;0,900;1,400;1,500;1,600;1,700;1,800;1,900',
    'Cinzel': 'family=Cinzel:wght@400;500;600;700;800;900',
    'Almendra Display': 'family=Almendra+Display',
    'MedievalSharp': 'family=MedievalSharp',
    'Pirata One': 'family=Pirata+One',
    'UnifrakturMaguntia': 'family=UnifrakturMaguntia',
    'Press Start 2P': 'family=Press+Start+2P',
    'Metamorphous': 'family=Metamorphous',
    'Cardo': 'family=Cardo:ital,wght@0,400;0,700;1,400',
    # Vecna theme. Grenze Gotisch (blackletter display) is a variable font on
    # the wght axis; EB Garamond (body) carries ital + wght. Both axes are
    # spelled out so the css2 API accepts them instead of failing the request.
    'Grenze Gotisch': 'family=Grenze+Gotisch:wght@300;400;500;600;700;800;900',
    'EB Garamond': 'family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;'
                   '1,400;1,500;1,600;1,700',
    # Tasha theme. Cinzel Decorative (ornate display) has a static wght axis;
    # its body face Cormorant Garamond is already listed above.
    'Cinzel Decorative': 'family=Cinzel+Decorative:wght@400;700;900',
    # Xanathar theme. Nova Square is a single-style squared display; Cardo
    # (body) is already listed above.
    'Nova Square': 'family=Nova+Square',
    # Vintage Arcade theme. VT323 is a single-style CRT-terminal monospace;
    # its display face Press Start 2P is already listed above.
    'VT323': 'family=VT323',
    # Military Terminal theme. Share Tech Mono is a single-style monospace;
    # its body face VT323 is already listed just above.
    'Share Tech Mono': 'family=Share+Tech+Mono',
    # Analog Archive theme. Special Elite (typewriter display) and Courier
    # Prime (report/screenplay body) are both single-family faces; Courier
    # Prime carries an ital+wght tuple so bold/italic report text renders.
    'Special Elite': 'family=Special+Elite',
    'Courier Prime': 'family=Courier+Prime:ital,wght@0,400;0,700;1,400;1,700',
    # Holo HUD theme. Orbitron (geometric sci-fi display) is a variable font on
    # the wght axis; its body face Share Tech Mono is already listed above.
    'Orbitron': 'family=Orbitron:wght@400;500;600;700;800;900',
    # Campaign themes with more distinctive display faces (see themes/):
    #   Dragon Heist -> Cormorant Unicase (elegant unicase, has weight axis),
    #   Mad Mage     -> Uncial Antiqua (single-style manuscript uncial),
    #   Theros       -> Marcellus SC (single-style Roman small-caps).
    # Their body faces (Lora, Playfair Display) are already listed above, and
    # Shattered Obelisk's new display (Metamorphous) is already listed too.
    'Cormorant Unicase': 'family=Cormorant+Unicase:wght@300;400;500;600;700',
    'Uncial Antiqua': 'family=Uncial+Antiqua',
    'Marcellus SC': 'family=Marcellus+SC',
}

_CSS2 = 'https://fonts.googleapis.com/css2?'
_TAIL = '&display=swap'


def _spec(family):
    """The `family=` query fragment for one face (qualified if it needs it)."""
    return FONT_QUERY.get(family, 'family=' + family.replace(' ', '+'))


def _url(families):
    """Build a css2 URL for an iterable of family names.

    Families are sorted: the css2 API rejects an unsorted family list. Callers
    de-duplicate first (a theme may reuse a face across display+body, and two
    themes may share one).
    """
    specs = [_spec(fam) for fam in sorted(families)]
    return Markup(_CSS2 + '&'.join(specs) + _TAIL)


def fonts_url_for_theme(theme):
    """css2 URL carrying just this theme's two faces (Theme-object core).

    Only the active theme's fonts are fetched, so switching themes never makes
    a page download every face in the table. `theme` is a Theme instance. The
    public, id-based fonts_url(theme_id) in registry.py wraps this so callers
    keep passing a string id exactly as before.
    """
    # dict.fromkeys de-duplicates while keeping order (a theme may reuse a face).
    return _url(dict.fromkeys((theme.display_font, theme.body_font)))


def all_fonts_url_for(themes):
    """css2 URL carrying EVERY face used by the given themes (core).

    Only the Appearance page links this: the theme picker previews each box in
    its own typeface, so it needs them all at once. `themes` is an iterable of
    Theme instances. Faces are de-duplicated so two themes sharing one don't
    request it twice. The public, no-argument all_fonts_url() in registry.py
    wraps this over every theme, matching the original signature.
    """
    families = set()
    for theme in themes:
        families.add(theme.display_font)
        families.add(theme.body_font)
    return _url(families)
