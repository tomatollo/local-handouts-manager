"""Verify every theme's Google Fonts URL against the live API.

Run from the project root:  python check_fonts.py

The css2 API fails a whole request when one family is malformed, so a single
bad name silently kills both faces of a theme. This asks Google for each
theme's URL and checks that every requested family actually comes back.
"""

import urllib.error
import urllib.request

from handouts import theming

# Google serves different @font-face sets per UA; a modern one gets woff2.
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')


def families_in(css):
    """Family names Google actually returned in the CSS."""
    found = set()
    for line in css.splitlines():
        line = line.strip()
        if line.startswith('font-family:'):
            found.add(line.split(':', 1)[1].strip().rstrip(';').strip('\'"'))
    return found


def main():
    failures = 0
    for theme_id in theming.THEMES:
        url = theming.fonts_url(theme_id)
        wanted = set(theming.THEMES[theme_id]['fonts'])
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            css = urllib.request.urlopen(req, timeout=20).read().decode()
        except urllib.error.HTTPError as exc:
            failures += 1
            print(f'FAIL  {theme_id}: HTTP {exc.code}')
            print(f'      {url}')
            continue
        except Exception as exc:
            print(f'SKIP  {theme_id}: no network ({exc})')
            continue

        missing = wanted - families_in(css)
        if missing:
            failures += 1
            print(f'FAIL  {theme_id}: Google did not return {sorted(missing)}')
            print(f'      {url}')
        else:
            print(f'ok    {theme_id}: {sorted(wanted)}')

    print()
    print('All themes load their fonts.' if not failures
          else f'{failures} theme(s) broken.')


if __name__ == '__main__':
    main()
