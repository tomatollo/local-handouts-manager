# Creating a Theme

A theme is an appearance preset: a color palette, two fonts, a scale for headings, an optional extra CSS block, and themed error pages. The theme is **global**: the Master chooses it from the *Appearance* page, and the players see it too, ensuring the entire table shares the same look. It lives in the database under `settings`.

The key point to understand first and foremost: **a theme does not redesign the layout**. The `static/css/style.css` file remains the single source of truth for the structure (and it is mobile-first). A theme simply **repaints** the custom CSS properties that `style.css` declares on `:root` - colors and fonts - by injecting them into a small `<style>` block. The "8-bit" look (sharp borders, stepped shadows) survives a font change because it lives in the borders and shadows, not in the typeface.

Each theme is a Python file inside `handouts/theming/themes/`, one theme per file.

---

## Anatomy of a Theme

The simplest possible file (`handouts/theming/themes/my_theme.py`):

```python
"""My Theme -- a one-liner describing the mood."""

from ..base import Theme

THEME = Theme(
    id='my-theme',
    name='My Theme',
    blurb='A short sentence, shown under the name in the picker.',
    fonts=('Cinzel', 'Lora'),
    scale=1.5,
    vars={
        '--bg':        '#101010',
        '--bg-panel':  '#1c1c1c',
        '--ink':       '#f0f0f0',
        '--ink-dim':   '#9a9a9a',
        '--accent':    '#e0a53a',
        '--accent-2':  '#3f8fb0',
        '--border':    '#000000',
        '--shadow':    '#000000',
        '--good':      '#5a9c86',
    },
)

```

The module **must** expose a module-level variable called `THEME`, which is an instance of `Theme`. This is all the registry looks for.

---

## The `Theme` Fields

| Field | Required | What it is |
| --- | --- | --- |
| `id` | yes | The slug used in the URL and saved in the DB, e.g., `'curse-of-strahd'`. It must be **unique**. This is the value the picker sends. |
| `name` | yes | The readable label shown in the picker (`'Curse of Strahd'`). |
| `blurb` | yes | A one-liner under the name in the picker. |
| `fonts` | yes | Tuple `(display, body)`: the font for headings and the one for long text. Both are Google Fonts family names. See *Fonts* below. |
| `scale` | yes | Multiplies the size of every heading. See *The Scale* below. |
| `vars` | yes | The dictionary of custom CSS properties to override. See *The Tokens* below. |
| `extra_css` | no | Raw CSS added **after** the `:root` block, only when the theme is active. For textures, animations, component tweaks. See *Extra CSS* below. Default: empty string. |
| `errors` | no | The themed error pages, `{http_code: (icon, title, message)}`. See *Error Pages* below. Default: `{}` (inherits from the default theme). |

---

## The Tokens (`vars`)

These are the nine custom CSS properties that `style.css` declares on `:root`. A theme repaints them. Define **all nine of them** - so a theme change never leaves the UI half-painted.

| Token | What it is |
| --- | --- |
| `--bg` | Page background. |
| `--bg-panel` | Background of panels/cards, one step above `--bg`. |
| `--ink` | Primary text color. |
| `--ink-dim` | Secondary/dimmed text. |
| `--accent` | The dominant color: buttons, headings, highlights. |
| `--accent-2` | The secondary color. |
| `--border` | The sharp border (usually black). |
| `--shadow` | The color of the stepped shadow (usually black). |
| `--good` | The "visible/public" green (revealed handouts). |

### Light vs. Dark Themes

Most themes are **dark**: light `--ink` on dark `--bg-panel`. But nothing is hardcoded: *Phandelver* is a light theme (dark ink on light parchment), and *Analog Archive* is a "board" theme (dark desk with light manila paper panels, so `--ink` is dark). Everything reads from these tokens, so both directions work without special cases - you just need to choose mutually consistent values.

---

## Fonts

`fonts=(display, body)`. The families are downloaded from Google Fonts.

If a family has variable axes (weight, italics) without a default position, Google's `css2` API **rejects** the request if passed as a bare `family=Name` - and, worse, makes the **entire** request fail, dragging down the other font too and causing the page to fallback to Georgia. This is why families with axes must be registered with their full `family=` string in `handouts/theming/fonts.py`, inside the `FONT_QUERY` dictionary.

Rule of thumb:

* **Single-style fonts** (e.g., `Press Start 2P`, `VT323`, `Uncial Antiqua`): nothing needs to be done. They are automatically requested as `family=Name+With+More`.
* **Fonts with weights/italics** (e.g., `Merriweather`, `Lora`, `Orbitron`, `EB Garamond`): add a row in `FONT_QUERY` with the enumerated axes. The axes must be in alphabetical order (`ital` before `wght`) and the tuples sorted - the API requires this.

Example from `fonts.py`:

```python
FONT_QUERY = {
    'Orbitron': 'family=Orbitron:wght@400;500;600;700;800;900',
    'EB Garamond': 'family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;'
                   '1,400;1,500;1,600;1,700',
    # ...
}

```

If a font does not appear when testing the theme, this is almost always the reason: its row is missing from `FONT_QUERY`, or the axes are not ordered as the API demands.

Each theme downloads **only** its own two fonts. The *Appearance* page is the only one that downloads all of them together (`all_fonts_url`), because the picker displays each box in its respective typeface.

---

## The Scale

`scale` multiplies the size of every heading. This is needed because the base CSS is calibrated on **Press Start 2P**, a pixel font that is wide and short for its body size. A normal font at the same size looks tiny, so every theme declares its own correction.

Typical values:

* `1` - only for themes using Press Start 2P (Dungeon Torch, Vintage Arcade).
* `1.3–1.6` - most normal serif/display fonts (Cinzel, Lora, Orbitron).
* `1.75–1.9` - blackletters, which are narrow and ornate, needing the strongest bump to remain readable (Curse of Strahd 1.9, Vecna 1.75).

Rule of thumb: test the theme, and if the headings look small, raise the scale; if a long heading overflows (especially a blackletter), lower it slightly.

There is also an associated automatic feature: the stepped shadow behind headings (`--display-shadow`) only makes sense under a pixel font. For every theme where the display font is **not** `Press Start 2P`, the system turns it off on its own - you don't need to do anything.

---

## Extra CSS (`extra_css`)

This is used when a theme wants to do more than repaint tokens: textures, animations, or tweaks to specific components. The extra CSS lives **inside the theme file**, as a string, and is added after the `:root` block **only when that theme is active** - so no guard like `[data-theme=...]` is needed, and the other themes never pay the performance cost.

Convention: define the CSS as a module-level constant and pass it to the `extra_css` field, keeping the `Theme(...)` call readable:

```python
from ..base import Theme

_EXTRA_CSS = """
/* ---- My Theme: description of the effect ---- */
.panel {
  box-shadow: var(--px) var(--px) 0 0 var(--shadow),
              inset 0 0 0 1px rgba(224,165,58,0.2);
}
h1, h2, h3, .pixel {
  text-shadow: 0 0 6px rgba(224,165,58,0.4);
}
"""

THEME = Theme(
    id='my-theme',
    # ... the other fields ...
    extra_css=_EXTRA_CSS,
)

```

### Rules for Writing `extra_css`

1. **Use real selectors.** Hook into classes that actually exist in the UI: `.panel`, `.btn`, `.btn--pop`, `.handout-card`, `.folder-card`, `.wiki-card`, `.count-badge`, `.tag`, `.lightbox__*`, `body`, `body::before`, etc. Check `style.css` for the list.
2. **Reuse tokens, do not hardcode colors** where possible: `var(--accent)`, `var(--shadow)`, `var(--px)` (the base pixel unit). This way, if you tweak the palette later, the extra CSS follows along.
3. **Put every animation behind `prefers-reduced-motion`.** Those who requested less motion should not see them:
```css
@media (prefers-reduced-motion: no-preference) {
  body { animation: my-effect 20s ease-in-out infinite alternate; }
  @keyframes my-effect { /* ... */ }
}

```


4. **Hover effects only where there is a real pointer**, so they don't get stuck on touch devices:
```css
@media (hover: hover) {
  .btn:hover { /* ... */ }
}

```


5. **Decorative pseudo-elements must not intercept clicks:** add `pointer-events: none;` to every ornamental `::before`/`::after`.

Full and commented examples: open `tashas_cauldron.py` (background animation + gradient on headings), `analog_archive.py` (the richest one: paper on chalkboard, polaroids, CLASSIFIED stamp), or `holo_hud.py` (frames cut with `clip-path`).

---

## Error Pages (`errors`)

Every theme can have its themed error pages: a 404 under *Curse of Strahd* reads "Phantom Village", while the same 404 under *Vintage Arcade* reads "Missing ROM". The field is a dictionary `{code: (icon, title, message)}`:

```python
    errors={
        400: ('\U0001F4A5', 'Title', 'Longer message explaining.'),
        401: ('\U0001F6D1', 'Title', 'Message.'),
        403: ('...', '...', '...'),
        404: ('...', '...', '...'),
        429: ('...', '...', '...'),
        500: ('...', '...', '...'),
    },

```

* The **icon** is an emoji (convenient as an escape `\U0001F4A5`, but the literal emoji works too).
* **Title** and **message** are English strings: they pass through the `|t` filter in `error.html`, so if you have an Italian translation in the i18n catalog it will be applied; otherwise, English is shown.
* The handled codes are **400, 401, 403, 404, 429, 500**.

The field is **optional** and also partial: any code you omit (or the entire `errors={}`) falls back to the text of the default theme (Dungeon Torch). Thus, a new theme shows sensible error pages even before you write your own.

Note: the type label (like "Bad Request", "Not Found") is **not** placed here - it is fixed per code and lives only once in `base.py` (`ERROR_TYPE_EN`).

---

## Registering the Theme

Once the file is created, the theme must be declared in two places (no other file should be touched):

### 1. The Order - `handouts/theming/themes/__init__.py`

Add the **module name** (without `.py`) to the `_ORDER` tuple, in the position where you want it to appear:

```python
_ORDER = (
    'dungeon_torch',
    'phandelver',
    # ...
    'my_theme',          # <-- here
)

```

`_ORDER` is the single source of truth for which themes exist and in what order. A module that exists but is **not** in `_ORDER` simply won't be shown - handy for parking a work-in-progress theme without deleting it.

### 2. The Family in the Picker - `handouts/theming/groups.py`

The picker groups themes into families ("Dungeons & Dragons", "Other Universes"). Add the theme's `id` to the correct family's tuple in `THEME_GROUPS`:

```python
THEME_GROUPS = (
    ('Dungeons & Dragons', (
        'phandelver',
        # ...
    )),
    ('Other Universes', (
        'dungeon-torch',
        'my-theme',       # <-- here, if it is not D&D
    )),
)

```

If you **forget** this step, it's not a drama: a theme that no family names automatically ends up in the **last** family ("Other Universes"). But putting it explicitly makes it clear where it belongs.

---

## Final Checklist

* File in `handouts/theming/themes/<name>.py` with a `THEME` variable.
* All nine tokens in `vars`.
* Fonts with variable axes added to `FONT_QUERY` in `fonts.py`.
* `scale` tested visually (headings neither tiny nor overflowing).
* Any `extra_css`: real selectors, `prefers-reduced-motion` on animations, `@media (hover: hover)` on hovers, `pointer-events: none` on decorations.
* Module added to `_ORDER` in `themes/__init__.py`.
* `id` added to a family in `groups.py`.
* Restart the app and check: the theme appears in the picker, applies correctly, and error pages work.

---

## Package Architecture (for reference)

```text
handouts/theming/
├── __init__.py       # re-exports the public API (css_vars, fonts_url, ...)
├── base.py           # the Theme dataclass + ERROR_TYPE_EN
├── registry.py       # the logic: clean_theme, theme_list, theme_groups,
│                     #   css_vars, theme_errors, theme_preview_style,
│                     #   and the id-based wrappers fonts_url / all_fonts_url
├── fonts.py          # FONT_QUERY + Google Fonts URL construction
├── groups.py         # THEME_GROUPS (the picker families)
└── themes/
    ├── __init__.py   # _ORDER -> gathers themes into THEMES
    └── <one file per theme>.py

```

The public API that the rest of the app uses (`theming.css_vars`, `theming.fonts_url`, `theming.theme_errors`, etc.) is exported by `__init__.py` and never changes when you add a theme - you only touch `themes/` and the two registration files.