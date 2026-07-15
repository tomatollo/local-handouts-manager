# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not use formal version numbers yet, so changes are grouped by
the phase of work that produced them, newest first.

## Unreleased

### Added
- **POP Handout.** The Master can now push a handout onto every player's
  screen, instead of publishing it and asking the table to refresh.
  - **POP** on any public handout (dashboard) broadcasts it immediately.
  - **Publish & POP** does both in one click for a hidden handout, and
    **Forge & POP** does the same straight from the upload form.
  - Players' screens open the handout in the existing lightbox, so carousel,
    book, PDFs and back covers all behave exactly as they do on a click. A
    player already reading something is not interrupted: they get a banner
    offering the new handout instead of having the viewer swapped underneath
    them.
  - **Sync:** the project had no client sync layer, so one was added. Players
    poll `GET /api/pop` every 3s; the endpoint returns a monotonic `seq` plus
    the handout to show. Polling was chosen over SSE/WebSockets because it
    holds no connections open (the app runs on the Werkzeug dev server) and
    recovers by itself from sleeping phones and Wi-Fi drops.
  - **Persistent by design:** the POP lives in `settings.pop` in the DB, not in
    memory, so a player who joins late, reloads, or wakes their phone still
    receives the POP the Master fired, and a server restart does not replay an
    old one. Only the newest POP is kept — there is no queue, because a queue
    would make the table work through a backlog of reveals in the wrong order.
  - Popping is refused on hidden handouts (`400`): a route named "pop" must
    not be a back door to publishing. `/api/pop` re-checks `visible` on every
    read, so unpublishing or deleting a popped handout retires the broadcast
    and a stale pointer can never leak a handout the Master pulled back.
- **Master access control.** A single passphrase now separates the Master from
  the table, stored as a salted hash and carried in a signed session cookie.
  New `/unlock` prompt, `Lock master mode`, and a `Master Access` settings page.
  The signing key can be supplied via the `HANDOUTS_SECRET_KEY` environment
  variable; otherwise one is generated and persisted on first run.
  - Every `/dm-panel*`, `/export` and `/import` route is now enforced
    server-side. Previously they were reachable by anyone on the Wi-Fi.
  - On first run the app stays open (there is nothing to authenticate against
    yet) and the dashboard shows a warning banner until a passphrase is set.
- **Quick Wiki**, split into two collections:
  - **Players Wiki** (`/wiki`) — read-only, lore the party has learnt.
  - **Master Wiki** (`/dm-panel/wiki/master`) — secrets, guarded.
  - Pages carry a `scope`; the player routes only ever query the players'
    scope, so there is no request parameter that could reach master pages.
    Requesting a master page's id from the player side returns `404`, not
    `403`, so the existence of a secret page is not leaked.
  - One-click **Reveal to players** / **Hide from players** flips a page
    between the two wikis, for when the party learns something.
  - Pages are plain text (no markdown, no HTML), so a wiki body cannot inject
    script into a player's browser.
  - Wiki content is included in export/import bundles.
- **Master navigation menu** (hamburger drawer) on every master page, reusing
  the player hub's existing drawer machinery.

### Changed
- **Decluttered the Master's Screen.** The dashboard was holding the two
  handout lists, the upload form, folder management, the theme picker, the
  export/import panel and a language switcher at once. The occasional controls
  moved behind the new menu into pages of their own:
  - Theme + interface language → `/dm-panel/appearance`
  - Export / import → `/dm-panel/transfer`
  - Passphrase → `/dm-panel/security`
  The dashboard now carries only what is used constantly: search, the
  hidden/public lists, upload and folders.
- `POST /settings/theme` now redirects to `/dm-panel/appearance` (was
  `/dm-panel`), so the Master sees the new theme applied where they chose it.
- The player browse drawer gained a **Wiki** section linking to the Players
  Wiki.

### Fixed
- **Export bundles no longer carry credentials.** `export_bytes()` dumped the
  whole DB, and the new passphrase hash + session signing key live under
  `settings` — so every `.zip` would have shipped them. A bundle is emailed or
  carried on a USB stick, so it is now treated as public: both are stripped
  (`transfer.PRIVATE_SETTINGS`). The signing key mattered most — holding it
  lets anyone forge an `is_master` cookie without knowing the passphrase.
- **Import now carries wiki pages.** The merge only handled handouts and
  folders, so wiki pages would have been silently dropped on transfer. New
  pages are added with their scope intact (a master page stays secret); pages
  whose id already exists are left alone. The review screen lists incoming
  pages and which wiki each lands in, so importing someone else's secrets is
  never a surprise.
- `'Summary'` was about to be defined twice in the Italian catalogue, where the
  second definition would have silently overwritten the import-review page's
  translation. Since catalogue keys *are* the English source string, the wiki's
  field is named `'Page summary'` instead.
- Password, search, number and textarea inputs were not covered by the base
  input styling (which predates them) and rendered as unstyled native boxes.

## Earlier phases

### Theming
- Seven themes, each overriding the full token set (palette + display/body font
  pair + heading scale), inspired by official D&D campaigns.
- Only the active theme's fonts are fetched, and font families needing explicit
  axis tuples are spelled out — the Google Fonts `css2` API fails the whole
  request if one family is under-specified, which silently killed both faces.

### Internationalisation
- English and Italian, per-user via a cookie (`?lang=` sets it). The `|t`
  filter takes the Jinja context so it is evaluated per render; without that,
  Jinja constant-folds it and bakes one language into the cached template.

### Handouts
- Multi-file handouts, per-file descriptions, drag-and-drop reordering.
- Carousel and Book (page-curl) viewers; optional back cover.
- PDF pages rendered to images for the Book viewer; first-page thumbnails for
  card previews, backfilled for older records.
- Folders (multi-membership), tags, categories, session numbers/titles,
  discovery place/date.
- Export/import of the whole library with a conflict review step.
