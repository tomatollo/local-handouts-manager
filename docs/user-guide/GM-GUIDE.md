# Game Master's Guide

How to actually run a session with the Local Handouts Manager once it's
installed. If you still need to get it running, start with
[INSTALL.md](../../INSTALL.md); this guide assumes the server is up and you can
reach the Master's Screen at `/dm-panel`.

Everything here happens from the **Master's Screen**. Players never see any of
it — they only ever see what you choose to reveal.

## Contents

- [First-time setup](#first-time-setup)
- [The core idea: hidden until you reveal](#the-core-idea-hidden-until-you-reveal)
- [Adding handouts](#adding-handouts)
- [The three viewers](#the-three-viewers)
- [Publishing and POP](#publishing-and-pop)
- [Organising: folders, tags, sessions](#organising-folders-tags-sessions)
- [Password-gated secrets](#password-gated-secrets)
- [The interactive map](#the-interactive-map)
- [Themes and the welcome header](#themes-and-the-welcome-header)
- [Backup & transfer](#backup--transfer)
- [A session-day checklist](#a-session-day-checklist)

---

## First-time setup

Before your first game, do these once:

1. **Set a passphrase.** Open **Menu → Master Access** and set one. Until you
   do, the app is open — anyone on the Wi-Fi can reach the Master side, and the
   dashboard shows a warning saying so. Setting the passphrase is what turns
   that off. (Forgot it later? The launcher has a **Reset master passphrase**
   button.)
2. **Note your LAN address.** The launcher shows it (e.g.
   `http://192.168.1.42:8000`). That's the address players type, or they can
   scan the **QR code** (the launcher's *Open QR* button, or `/qr`).
3. **Lock when you hand your device around.** **Menu → Lock master mode** drops
   your master rights on that browser, so passing your phone to a player doesn't
   expose your notes. Unlock again with your passphrase.

---

## The core idea: hidden until you reveal

Every handout starts **hidden**. A hidden handout is a private draft: it exists
in your library, but players cannot see it, search it, or reach it by URL. It
becomes visible only when you **publish** it — and it lands on the players' hub
the next time they look.

This is the whole safety model: you prepare everything in advance while it's all
hidden, then reveal each piece at the moment the party earns it. Nothing you
haven't published can leak.

---

## Adding handouts

From the dashboard, use **Create** (or the menu) to open the upload form. A
handout is one *or more* files shown together — a single map, or a multi-page
letter, or a whole grimoire.

On the form you set:

- **Title** (required) and an optional **description** shown in the viewer.
- The **files** themselves — images (PNG/JPG/GIF/WebP), **PDF** (rendered to
  page images automatically), or a **`.glb` 3D model**. You can drag to reorder
  pages and give each file its own caption.
- The **viewer** (see below), **folders**, **tags**, a **session number/title**,
  and optional in-fiction **discovery place/date**.

New handouts are hidden by default. There's also **Forge & POP** on the form,
which uploads, publishes, *and* pushes it to every screen in one click — handy
when the party finds something you hadn't prepared.

---

## The three viewers

Each handout is shown one of three ways; you pick it per handout:

- **Carousel** — the default. Swipe through images and PDF pages. Best for maps,
  portraits, single documents.
- **Book** — a realistic page-curl for multi-page tomes, journals and
  grimoires. Optionally add a **back cover**. Covers can be rigid "hard" boards
  or flip like inner leaves.
- **3D Inspect** — opens the handout in a full-screen canvas the player can
  rotate, zoom and pan. It shows either a **`.glb` model**, or a **double-sided
  sheet** built from a front image and an optional **back texture**, where PNG
  transparency punches real holes through the paper (torn scrolls, bullet
  holes).

> The Book and 3D Inspect viewers use JavaScript libraries bundled in the repo
> (`static/vendor/`), so they work out of the box. If either opens blank on a
> particular install, those files may be missing — see
> [INSTALL.md](../../INSTALL.md#3-vendor-libraries-already-included).

---

## Publishing and POP

There are two separate ideas here, and keeping them straight is the key to
running a smooth table:

- **Publish** makes a hidden handout visible. It now appears on the hub, ready
  the next time a player looks or refreshes. Quiet, no interruption.
- **POP** puts a handout on **every player's screen right now**, without anyone
  touching their phone. It opens in the same viewer a tap would.

The dashboard gives you the combinations:

- **POP** — on anything already public. Broadcasts it immediately.
- **Publish & POP** — reveals a hidden handout *and* pops it in one click.
- **Forge & POP** — does the same straight from the upload form.

A few things worth knowing about POP:

- **You can't POP a hidden handout** — popping is a spotlight, not a back-door
  publish. Publish (or Publish & POP) first.
- **Only the newest POP counts.** Popping a second handout replaces the first;
  there's no queue building up in the wrong order.
- **It reaches latecomers.** A player who joins mid-session, reloads, or wakes a
  sleeping phone still catches the POP — for a couple of minutes, after which it
  expires so nobody is ambushed by an old reveal.
- **Pop again to re-open.** Popping the same handout a second time re-opens it,
  for when half the table wasn't looking.
- Players already reading something aren't yanked away — they get a banner
  offering the new handout and open it when ready.

---

## Organising: folders, tags, sessions

Handouts can be sliced several ways, and players get the same views:

- **Folders** — named collections ("Maps", "Letters", "NPCs"). A handout can be
  in several at once. Empty folders never show to players, so a folder you
  created but haven't filled won't clutter their view.
- **Tags** — free-text labels, searchable and groupable, separate from folders.
- **Session number / title** — lets everyone browse the library as a timeline
  and reconstruct when things were found.

Players also get a **free-text search** across titles, descriptions, tags and
session notes, so "that medallion from a few sessions ago" is findable.

---

## Password-gated secrets

You can hide a twist behind a password. On a handout, set one or more
**passwords** and link them to **another handout**. When a player types a
correct password into the open handout's info panel, the linked handout opens on
the spot.

- Any one of the passwords unlocks the target; you can turn on
  case-insensitive matching.
- A wrong or empty guess looks **identical** to a handout that has no secret at
  all — so the feature never even reveals that a secret exists to find.

This is table theatre, not security: the passwords are stored as plain text so
you can see them when editing. Don't use it for anything you'd mind a determined
player eventually seeing.

---

## The interactive map

Upload one or more campaign maps and reveal them as the party explores. Reach
the map controls from **Menu → Maps**, then pick or create a map.

What you can do on a map:

- **Calibrate a grid** over the image — hex (default) or square — and set its
  size and origin.
- **Reveal cells** as the party moves; only revealed terrain is ever sent to
  players (unrevealed areas aren't hidden client-side, they're simply absent
  from the image the players receive, so there's nothing to peek at).
- **Drop points of interest** — labelled pins with custom icons, colours and an
  optional category.
- **Move the party marker.**
- **Focus** — a "everyone look here" action that pushes every player's view to a
  spot on the map at once (like a POP, but for the map camera).

The crucial workflow detail: **your edits are a private draft until you
confirm.** Revealing hexes, dragging the marker, moving pins — all of it lands
in a draft layer only you see. Players' screens don't change until you press
**Confirm**. So a stray click during prep never flashes onto the table
mid-scene. **Discard** throws the draft away and snaps back to what players
currently see. (Uploading a background image and firing a Focus are the two
exceptions — those take effect immediately, since a half-set-up map would only
confuse.)

A table can hold **several maps** — a world map, a city, a dungeon level — each
an independent scene.

---

## Themes and the welcome header

From **Menu → Appearance**:

- **Theme** — twenty presets (fifteen from D&D sourcebooks, five from other
  universes). The theme is **table-wide**: you pick it, and every player's
  screen changes to match, live. Two of them (Tasha, Xanathar) add animated
  textures. To build your own, see
  [docs/dev/THEMES.md](../dev/THEMES.md).
- **Welcome header** — override the player hub's greeting with your own title(s)
  and subtitle(s); give a list and it can pick one at random per visit.
- **Interface language** — English or Italian, chosen **per person**: each
  player can read the UI in their own language while you use the other.

---

## Backup & transfer

From **Menu → Backup & Transfer**:

- **Export** bundles the whole library — handouts, images, folders, and the
  interactive map (its state *and* background image) — into one `.zip`. Your
  passphrase and signing key are stripped out, so the bundle is safe to email or
  carry on a USB stick.
- **Import** takes a bundle on another computer, with a **review step** so
  nothing is overwritten (or wiped) without your say-so. If the incoming bundle
  has a map that differs from yours, you choose per-map whether to keep yours or
  take theirs (default: keep yours).

Export is also the safest campaign backup — far better than copying files by
hand. Make one before you update the app.

---

## A session-day checklist

A quick run-through before your friends arrive:

1. Start the server (launcher → **Start server**), and note the LAN address /
   QR.
2. Confirm your passphrase is set and you're **unlocked** on your own device.
3. Have this session's handouts uploaded and still **hidden**, ready to publish.
4. If you'll use the map, open it once and check the background and grid look
   right (visiting the map list also makes a fresh install's map addressable).
5. Send players the address or QR, and check one handout opens on a player
   device to confirm the Wi-Fi path works.

Then run your game: **Publish** quietly as things are found, **POP** when you
want the whole table looking at once.
