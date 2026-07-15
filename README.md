# Local Handouts Manager for Dungeons and Dragons

A lightweight, self-hosted web application designed for Tabletop Roleplaying Games (TTRPGs). It allows Game Masters to share handouts, maps, lore documents and interactive books with players over a local Wi-Fi network, without requiring an active internet connection.

Everything runs on your own machine. No cloud, no accounts, no lag.

## Features

### For players
* **Zero setup:** anyone on the same Wi-Fi opens the hub via a simple IP address on their phone, tablet or laptop. Nothing to install.
* **Browse however you think:** handouts organised by collection, session, or tag, plus a free-text search across titles, descriptions, tags and session notes.
* **Two readers:** a **Carousel** for images and PDFs, and a page-curling **Book** viewer for multi-page tomes, journals and grimoires (with an optional back cover).
* **Handouts that come to you:** when the Master POPs something, it opens on your screen by itself. If you are already reading a handout you are not interrupted — a banner offers the new one and you open it when you are ready.
* **Players Wiki:** a quick-reference of the lore the party has actually learnt.

### For the Game Master
* **Reveal mechanics:** every handout starts hidden. Publish it and it appears on the players' hub, ready for them the next time they look.
* **POP Handout:** when you want the table looking *now*, POP it — the handout opens on every player's screen without anyone touching their phone. Use **POP** on anything already public, **Publish & POP** to reveal and pop in one click, or **Forge & POP** to do it straight from the upload form. Popping the same handout again re-opens it, for when half the table missed it.
* **Master's Screen:** upload, edit, reorder pages by drag-and-drop, per-file descriptions, folders, tags, session numbers and discovery notes.
* **Dual Wiki:** a **Players Wiki** the table can read, and a **Master Wiki** for secrets and plot hooks that players cannot reach. Any page can be revealed to the players in one click when the party learns it.
* **Theme manager:** five D&D campaign presets plus two more, each swapping the whole palette *and* both typefaces (see below).
* **Backup & Transfer:** export the whole library — handouts, images, folders, wiki — as a single `.zip` and import it on another computer, with a conflict review step so nothing is overwritten without your say-so.
* **Bilingual interface:** English and Italian, switchable per person. Your players can each read the UI in their own language while you use another.

## Themes

The theme is table-wide: the Master picks it and everyone sees it. Each preset overrides the same design tokens, so switching can never leave a half-painted UI.

| Theme | Mood |
| --- | --- |
| **Dungeon Torch** *(default)* | Soot, torchlight and pixels |
| **Lost Mine of Phandelver** | Forest, parchment, goblin country |
| **The Rise of Tiamat** | Scale-grey, crimson and gold hoards |
| **Out of the Abyss** | Obsidian dark, drow violet, fungal neon |
| **Tomb of Annihilation** | Jungle moss, limestone and Acererak gold |
| **Curse of Strahd** | Pitch, velvet and bright blood |
| **Icewind Dale** | Endless night, frost and one cold star |

## Master access

The Master side is protected by a single passphrase — there are no user accounts, because there is only ever one Master per table.

On first run the app is **unprotected** and says so on the dashboard. Open **Menu → Master Access** and set a passphrase before your first session; until you do, anyone on the Wi-Fi can open the Master Wiki.

The passphrase is stored as a salted hash, and unlocking sets a signed session cookie, so it cannot be forged by editing the cookie. **Lock master mode** from the menu if you hand your device to a player.

> **Scope of the protection.** This is designed to stop a curious player at the table from reading your notes. The app speaks plain HTTP and is meant for a trusted home network — it is not hardened against an attacker on the LAN, and it should not be exposed to the public internet.

Optionally, set the session signing key yourself instead of letting the app generate and store one:

```bash
export HANDOUTS_SECRET_KEY="some-long-random-string"   # Windows: set HANDOUTS_SECRET_KEY=...
```

## How to Run

This is a Flask application. Install the dependencies and run `app.py`:

```bash
pip install -r requirements.txt
python app.py
```

Then open:

| Who | Where |
| --- | --- |
| Players | `http://localhost:8000` |
| Game Master | `http://localhost:8000/dm-panel` |

Other devices on the same Wi-Fi connect using your machine's local IP address, e.g. `http://192.168.1.42:8000`.

## Routes

| Route | Access | Purpose |
| --- | --- | --- |
| `/` | Players | The hub of revealed handouts |
| `/folder/<id>` | Players | A single collection |
| `/api/pop` | Players | Poll target: the current POP broadcast (JSON) |
| `/wiki/` | Players | Players Wiki index |
| `/wiki/<page_id>` | Players | A single players' wiki page |
| `/unlock` | Public | Master passphrase prompt |
| `/dm-panel` | **Master** | Master's Screen |
| `/pop/<id>` | **Master** | POP a public handout to every screen |
| `/publish/<id>` | **Master** | Publish a handout (`pop=1` to pop it too) |
| `/dm-panel/wiki/` | **Master** | Pick a wiki |
| `/dm-panel/wiki/players` | **Master** | Players Wiki, with editing |
| `/dm-panel/wiki/master` | **Master** | Master Wiki (secret) |
| `/dm-panel/appearance` | **Master** | Theme + language |
| `/dm-panel/transfer` | **Master** | Export / import |
| `/dm-panel/security` | **Master** | Set or change the passphrase |

Every **Master** route is enforced server-side. The players' wiki routes only ever query the players' scope, so there is no parameter a player could tamper with to reach the Master Wiki; requesting a secret page's id from the player side returns a plain `404`, indistinguishable from a page that does not exist.

## How POP works

A POP is stored, not pushed. When you pop a handout, the Master routes record
`{seq, handout_id, at}` under `settings.pop` in the database, where `seq` is a
counter that only ever grows.

Every player's page polls `GET /api/pop` every 3 seconds and compares the `seq`
it gets back against the last one that device showed (kept in `sessionStorage`).
Anything higher is a new POP, so the page opens it in the same lightbox a click
would — carousel, book, PDFs and back covers all work with no separate code
path. Polling pauses while a tab is hidden and fires immediately on return, so a
phone that was asleep catches up the moment it wakes.

Storing the POP rather than pushing it is what makes the late cases work: a
player who joins mid-session, reloads, or unlocks their phone still finds the
broadcast waiting. Only the newest POP is kept — popping a second handout
supersedes the first rather than queueing behind it.

Two rules keep a POP from becoming a leak:

* A hidden handout cannot be popped (`400`). Popping is a spotlight, not a
  publish button.
* `/api/pop` re-checks `visible` on every read, and unpublishing or deleting a
  popped handout retires the broadcast. The endpoint is public by definition —
  players are never authenticated — so it never trusts the stored pointer alone.

Polling was chosen over Server-Sent Events or WebSockets deliberately: the app
runs on the Werkzeug development server on a home network, where holding a
long-lived connection open per player costs a thread each and gains a couple of
seconds. A poll that fails is a poll that simply happens again.

## Project layout

```
app.py                    # entry point: app factory, language + theme + role context
handouts/
  auth.py                 # master passphrase, session unlock, @master_required
  wiki.py                 # wiki pages + the players/master scope split
  storage.py              # JSON database + uploads on disk
  organize.py             # grouping, sorting and search (pure functions)
  theming.py              # the theme table: palettes and font pairs
  i18n.py                 # EN/IT catalogue
  pdfs.py                 # PDF -> images, thumbnails
  transfer.py             # export / import bundles
  routes_player.py        # /            player hub + /api/pop (POP polling)
  routes_master.py        # /dm-panel    master screen + settings + POP
  routes_wiki.py          # /wiki, /dm-panel/wiki
templates/
  master/  player/  wiki/
  player/_lightbox.html   # the one viewer; exposes window.Lightbox
  player/_pop.html        # POP watcher: polls /api/pop, drives the lightbox
static/css/style.css      # mobile-first 8-bit stylesheet
```

## Credits

The retro 8-bit visual style is inspired by [8bitcn/ui](https://8bitcn.com) by
[OrcDev](https://orcdev.com) (MIT-licensed). The look is reimplemented here in
plain CSS, with no React or Tailwind dependency.

Page-curl reading is powered by [StPageFlip](https://github.com/Nodlik/StPageFlip) (MIT).
