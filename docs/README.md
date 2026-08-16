# Documentation

Everything written about the **Local Handouts Manager**, in one place. If you
are not sure where to start, use the map below.

## Start here

- **[Main README](../README.md)** — what the app is, its features, screenshots,
  the routes table, and the project layout. Read this first.
- **[Installation & Update Guide](../INSTALL.md)** — step-by-step setup on
  Windows, macOS and Linux, both the double-click launcher and the terminal,
  plus connecting phones, running a real session, updating safely, and
  troubleshooting.

## Using the app

Task-oriented guides for the people at the table.

- **[user-guide/GM-GUIDE.md](user-guide/GM-GUIDE.md)** — the Game Master's
  guide: setting a passphrase, adding handouts, the three viewers, Publish vs
  POP, folders/tags/sessions, password-gated secrets, the interactive map,
  themes, backup, and a session-day checklist.
- **[user-guide/PLAYER-GUIDE.md](user-guide/PLAYER-GUIDE.md)** — the player's
  one-pager: getting in, finding things, reading handouts, and what a POP is.

> The app also has an in-app guide at `/guide`, handy during a session. The
> written guides above are the fuller, more current reference.

## Reference — how it works

Explanation-oriented docs: read these to understand the system.

- **[reference/DATA-MODEL.md](reference/DATA-MODEL.md)** — every object the app
  stores and its fields: handouts, folders, maps, POIs, settings, POP.
- **[reference/STORAGE.md](reference/STORAGE.md)** — the `handouts/storage/`
  persistence package: its module map, the acyclic dependency graph, the maps
  model, and the draft/confirm staging.
- **[reference/SECURITY.md](reference/SECURITY.md)** — the threat model and the
  reasoning behind every access-control, request-integrity and availability
  decision, with sources.

## Dev — how to extend

Task-oriented guides: read these to add something. Each is self-contained.

- **[dev/THEMES.md](dev/THEMES.md)** — create a new theme: the `Theme` fields,
  the design tokens, fonts, the scale, `extra_css`, themed error pages, and how
  to register it.
- **[dev/LANGUAGES.md](dev/LANGUAGES.md)** — add an interface language: the
  catalogue format, registering the module, and how translation lookup works.
  *(Written in Italian.)*

---

## Where things live

```
README.md              # project overview, features, routes, layout
INSTALL.md             # install / update / troubleshoot (all OSes)
LICENSE
docs/
  README.md            # this index
  user-guide/          # using the app
    GM-GUIDE.md        # the Game Master's guide
    PLAYER-GUIDE.md    # the player's one-pager
  reference/           # how it works
    DATA-MODEL.md      # every stored object and its fields
    STORAGE.md         # the storage package internals
    SECURITY.md        # threat model + security design
  dev/                 # how to extend
    THEMES.md          # write & register a theme
    LANGUAGES.md       # add an interface language
  screenshots/         # images used across the docs
```
