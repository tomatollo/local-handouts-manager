'''Analog Archive -- noir case files: manila folders, redacted ink, a stamp.

Special Elite mimics a smudged typewriter for headings/stamps; Courier Prime is
the clean report/screenplay monospace for body. Both sit at normal width, so
headings need a bump; Special Elite runs large already, so a moderate 1.35
keeps stamps from overflowing.

This is the one "board" theme: a dark corkboard/leather desk with LIGHT
manila-paper panels on it, so --ink is DARK (typewriter ink on paper), like
Phandelver's inverted logic. The extra_css is the juice -- paper on a board:
panels get a rough-paper wash + stacked-paper shadow and a strip of translucent
tape; the h1 reads as a red CLASSIFIED stamp pressed into the page; buttons
redact to a marker-black bar on hover; count badges become tilted yellow
post-its. Everything with motion sits behind prefers-reduced-motion.
'''

from ..base import Theme

_EXTRA_CSS = """
/* ==== Analog Archive: noir case-file board ========================= */

/* ---- The board itself ---------------------------------------------
   A dark desk/corkboard: a faint fibrous noise (layered low-alpha
   gradients) breaks up the flat --bg so it reads as leather/cork, not
   a void. Text placed directly on the board (outside a paper panel) is
   light, since --ink is dark for the paper; we restore that here. */
body {
  background-color: var(--bg);
  background-image:
    radial-gradient(circle at 18% 22%, rgba(255,255,255,0.020) 0 2px, transparent 3px),
    radial-gradient(circle at 63% 71%, rgba(255,255,255,0.018) 0 2px, transparent 3px),
    radial-gradient(circle at 84% 34%, rgba(0,0,0,0.22) 0 3px, transparent 4px),
    linear-gradient(135deg, rgba(0,0,0,0.25), rgba(0,0,0,0) 40%);
  background-size: 140px 140px, 190px 190px, 220px 220px, 100% 100%;
  background-attachment: fixed;
  color: #d9d2c2;               /* light "chalk" text when on the bare board */
}
/* Body copy sitting on the board (subtitles, muted lines) stays light. */
.subtitle { color: #b7ae99; }

/* ---- Paper panels: manila stock, rough wash, stacked-paper shadow --
   A subtle diagonal gradient dirties the flat manila so it feels like
   rough paper; the layered box-shadow fakes 2-3 sheets stacked under
   the top one. position:relative anchors the tape pseudo-element.
   NB: .handout-card is intentionally NOT in this list -- in Cards view
   it becomes a transparent polaroid, in Rows a folder spine (below). */
.panel, .wiki-card, .folder-card {
  position: relative;
  background-color: var(--bg-panel);
  background-image:
    linear-gradient(115deg, rgba(0,0,0,0.05), rgba(0,0,0,0) 45%),
    radial-gradient(circle at 88% 8%, rgba(120,100,60,0.10), transparent 42%);
  border: 1px solid var(--border);
  box-shadow:
    2px 3px 0 0 rgba(214,203,170,0.85),   /* sheet 2 peeking out */
    4px 6px 0 0 rgba(198,186,150,0.55),   /* sheet 3 */
    6px 9px 14px 0 var(--shadow);         /* soft cast shadow onto board */
}

/* ---- Pinned to the board: one object per element type -------------
   Anti-"tape everywhere" rule: tape stays ONLY on the big .panel. The
   wiki-card gets a thumbtack; handout cards get a tack in Cards view
   (further down); folders get a real tab, not a tack. Post-its are the
   count badges. All pseudo-elements are non-clickable and sit above the
   paper. */

/* Tape: only on the big panel, a single strip up top. */
.panel::before {
  content: "";
  position: absolute;
  top: -11px; left: 50%;
  width: 96px; height: 24px;
  transform: translateX(-50%) rotate(-2.5deg);
  background: linear-gradient(90deg,
      rgba(228,222,200,0.12),
      rgba(228,222,200,0.32) 22%,
      rgba(228,222,200,0.20) 80%,
      rgba(228,222,200,0.12));
  border-left: 1px solid rgba(255,255,255,0.16);
  border-right: 1px solid rgba(255,255,255,0.16);
  box-shadow: 0 1px 2px rgba(0,0,0,0.22);
  pointer-events: none;
  z-index: 3;
}

/* Thumbtack: on the wiki-card. A glossy red disc with a centre hole,
   drawn purely with radial-gradients. No tape here. */
.wiki-card::before {
  content: "";
  position: absolute;
  top: -7px; left: 50%;
  width: 16px; height: 16px;
  transform: translateX(-50%);
  border-radius: 50%;
  background:
    radial-gradient(circle at 38% 32%, #ffffff 0 2px, transparent 3px),   /* highlight */
    radial-gradient(circle at 50% 60%, rgba(0,0,0,0.35) 0 2px, transparent 3px), /* hole */
    radial-gradient(circle at 50% 45%, #c0392f 0 55%, #8a1f20 100%);       /* head */
  box-shadow: 0 2px 3px rgba(0,0,0,0.4);
  pointer-events: none;
  z-index: 4;
}

/* ---- The CLASSIFIED stamp: the main h1 ----------------------------
   A tilted red box with a thick red rubber border stamped onto a scrap
   of manila paper. The background is opaque paper (not a grey wash) so
   on the dark board it reads as a stamped card, not a floating grey box.
   The home-title link inherits the stamp colour. */
h1 {
  display: inline-block;
  color: #8a1f20;                       /* darker stamp red = more contrast */
  background: #e6ddc5;                  /* opaque manila scrap under the stamp */
  border: 3px solid #8a1f20;
  border-radius: 2px;
  padding: 4px 14px;
  transform: rotate(-2deg);
  mix-blend-mode: normal;
  text-shadow: 0 1px 0 rgba(255,255,255,0.5);   /* lift ink off the paper */
  box-shadow: inset 0 0 0 1px rgba(138,31,32,0.35),
              2px 3px 6px rgba(0,0,0,0.4);       /* the scrap casts a shadow */
  letter-spacing: 1px;
}
h1 a, h1 .home-title { color: inherit; text-decoration: none; }
/* h2/h3 are section headers sitting on the dark board, so they need a
   LIGHT ink, not the dark biro-blue (which vanished on the board). A soft
   blue-tinted parchment reads as chalk-on-corkboard. */
h2, h3 { color: #b9c4d4; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }
/* When a heading sits INSIDE a paper panel, dark biro-blue is right. */
.panel h2, .panel h3, .wiki-card h2, .wiki-card h3 {
  color: var(--accent-2);
  text-shadow: none;
}

/* ---- Buttons -------------------------------------------------------
   Every button is a manila field with a typed ink label and an ink
   border -- legible on both paper panels and the dark board. */
.btn {
  background: #e6ddc5;                   /* manila, like the panels */
  color: var(--ink);
  border: 2px solid var(--ink);
  box-shadow: 2px 2px 0 0 var(--shadow);
  transition: background 0.12s steps(2, end), color 0.12s steps(2, end),
              border-color 0.12s steps(2, end);
}

/* Redaction hover: ONLY plain action buttons get the marker-black
   "censored" bar. Navigation buttons (mode/view/drawer) and ghost
   buttons are excluded, because hiding their label breaks wayfinding.
   A thin light strike-through hints at redaction without erasing text. */
@media (hover: hover) {
  .btn:not(.hub-mode__btn):not(.view-btn):not(.drawer__link):not(.btn--ghost):not(.btn--pop):not(.hub-mode__btn--active):not(.view-btn--active):hover {
    background: #141414;                 /* marker black */
    color: #cfc8b8;                      /* still readable, like ghosted ink */
    border-color: #141414;
    text-decoration: line-through;
    text-decoration-color: rgba(255,255,255,0.5);
  }
}

/* Navigation & ghost buttons: a quiet paper hover, NEVER black. */
@media (hover: hover) {
  .hub-mode__btn:hover,
  .view-btn:hover,
  .btn--ghost:hover,
  .drawer__link:hover {
    background: #f0e9d2;                 /* paper lifts a shade */
    color: var(--ink);
    border-color: var(--accent);
  }
}

/* Active / selected navigation = a red rubber stamp, light ink, so the
   current tab is obvious and readable (base CSS made text --border, too
   dark on red). */
.hub-mode__btn--active,
.view-btn--active,
.drawer__link--active {
  background: var(--accent) !important;
  color: #f3e7d0 !important;
  border-color: #7f2122 !important;
}
.hub-mode__btn--active:hover,
.view-btn--active:hover,
.drawer__link--active:hover {
  background: #7f2122 !important;        /* deeper red, still light text */
  color: #f3e7d0 !important;
}

/* Ghost buttons (mode chips in the drawer, view switches) sit on the
   dark board or paper; give them an explicit manila base so they never
   inherit the dark --bg-panel-as-board confusion. */
.btn--ghost {
  background: #ded3b6;
  color: var(--ink);
  border-color: var(--ink);
}

/* The POP call-to-action is a red stamp button, deepening on hover. */
.btn--pop {
  background: var(--accent);
  color: #f3e7d0;
  border-color: #7f2122;
}
@media (hover: hover) {
  .btn--pop:hover { background: #7f2122; color: #f3e7d0; border-color: #7f2122; }
}

/* Drawer navigation links: the base gives them background:var(--bg) (the
   dark board) which is invisible inside the light drawer panel. Put them
   on paper with ink text. */
.drawer__link {
  background: #ded3b6;
  color: var(--ink);
  border-color: var(--border);
}

/* ---- Editable fields: light card, dark ink ------------------------
   The base CSS gives inputs `color: --ink; background: --bg`. Here --bg
   is the dark board, so dark ink vanished on it. Force them onto a light
   card. The <select> has appearance:none in the base, so its <option>
   list also needs an explicit light background + dark text or it renders
   on the OS dark theme and looks broken. !important beats the base rule. */
input, select, textarea {
  color: #2b2b2b !important;             /* ink, beats the base --ink */
  background-color: #f4eeda !important;  /* yellowed index card */
  border: 2px solid var(--border);
  box-shadow: inset 1px 1px 0 0 rgba(0,0,0,0.10);
  -webkit-text-fill-color: #2b2b2b;      /* Safari: force text colour */
}
input::placeholder, textarea::placeholder { color: #8a8065; }
/* Redraw the select arrow dark (the base draws it with light --ink-dim,
   invisible on the card). */
select {
  background-image:
    linear-gradient(45deg, transparent 50%, #2b2b2b 50%),
    linear-gradient(135deg, #2b2b2b 50%, transparent 50%) !important;
}
select option { color: #2b2b2b; background-color: #f4eeda; }
input:focus, select:focus, textarea:focus { border-color: var(--accent); outline: none; }

/* ---- Checkbox rows: .folder-choice -------------------------------
   Every labelled checkbox in the forms (Hard covers, the folder picker
   chips, Ignore-case, Remove ticks) is a .folder-choice, which the base
   CSS paints background:var(--bg) (the dark board) + color:--ink (dark)
   -- a black chip with black text. Put them on a paper card with ink
   text, and tint the tick itself with the stamp red so it reads as a
   filled-in form box. */
.folder-choice {
  background: #ded3b6;                    /* manila chip */
  color: var(--ink);
  border-color: var(--border);
}
.folder-choice input[type="checkbox"],
.folder-choice input[type="radio"] {
  accent-color: var(--accent);           /* red rubber-stamp tick */
}
@media (hover: hover) {
  .folder-choice:hover { border-color: var(--accent); background: #e6dcc2; }
}
/* A checked chip reads as a stamped/approved box: subtle red wash. */
.folder-choice:has(input:checked) {
  background: #ecd9c4;
  border-color: var(--accent);
}
/* The edit page's remove-tick and per-file description labels live on the
   dark board too; keep their text light there, ink on the paper chip. */
.edit-file__remove { color: #d9d2c2; }
.edit-file__desc span { color: #d9d2c2; }

/* ---- Tags & PDF placeholders: paper labels, not black holes -------
   These used `background: var(--bg)` (black) + --accent text. Turn them
   into little paper labels with red stamp text on the manila panel. */
.tag,
.h-thumb--pdf,
.handout-card__pdf {
  background: #ded3b6;                    /* manila a touch darker */
  color: var(--accent);
  border-color: var(--border);
}
.tag--session { color: var(--ink-dim); }

/* The lightbox panel stays dark by design, so its caption must be LIGHT
   (here --ink is dark). */
.lightbox__caption { color: #f3e7d0; }

/* ---- Count badges: little yellow post-its -------------------------
   Square sticky note, tilted, its own soft shadow, biro-blue number.
   Overflow on the parent thumb is allowed so tilt/shadow aren't clipped. */
.count-badge {
  font-family: var(--font-body);
  font-weight: 700;
  color: var(--accent-2);
  background: #f2e06a;
  background-image: linear-gradient(180deg, #f7e884, #ecd44e);
  border: none;
  border-radius: 1px;
  padding: 5px 7px;
  transform: rotate(-6deg);
  box-shadow: 1px 2px 3px rgba(0,0,0,0.35);
}
.h-thumb { overflow: visible; }

/* ================= HANDOUTS: CARDS view = pinned polaroids ========= */
/* The card itself all but disappears (no filled rectangle); the PHOTO
   is the object -- a slightly-crooked polaroid tacked to the board. The
   title becomes a typed caption underneath. */
.view--cards .handout-card {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 6px 4px 12px;
  position: relative;
  transform: rotate(-1.2deg);
  transition: transform 0.12s ease;
}
.view--cards .handout-card:nth-child(even) { transform: rotate(1.4deg); }
.view--cards .handout-card:nth-child(3n)   { transform: rotate(-0.6deg); }
@media (hover: hover) {
  .view--cards .handout-card:hover { transform: rotate(0deg) scale(1.03); }
}
/* The photo carries the polaroid frame, not the card. */
.view--cards .handout-card .h-thumb {
  background: #f6f1e2;
  padding: 6px 6px 8px;
  border: 1px solid rgba(0,0,0,0.15);
  box-shadow: 2px 3px 7px rgba(0,0,0,0.45);
}
.view--cards .handout-card img,
.view--cards .handout-card .h-thumb--pdf { border: none; height: 130px; }
.view--cards .handout-card .h-title {
  font-family: var(--font-display);      /* Special Elite = typewriter */
  /* The polaroid caption sits on the dark board, so it needs LIGHT ink,
     not the dark paper --ink (which was invisible). */
  color: #ece3cf;
  text-shadow: 0 1px 2px rgba(0,0,0,0.6);
  margin-top: 8px;
}
.view--cards .handout-card .h-desc {
  color: #c3bba6;                        /* dimmer light for the description */
  font-style: italic;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}
/* A single thumbtack at the top of each polaroid (Cards view only). */
.view--cards .handout-card::before {
  content: "";
  position: absolute;
  top: -3px; left: 50%;
  width: 16px; height: 16px;
  transform: translateX(-50%);
  border-radius: 50%;
  background:
    radial-gradient(circle at 38% 32%, #ffffff 0 2px, transparent 3px),
    radial-gradient(circle at 50% 60%, rgba(0,0,0,0.35) 0 2px, transparent 3px),
    radial-gradient(circle at 50% 45%, #c0392f 0 55%, #8a1f20 100%);
  box-shadow: 0 2px 3px rgba(0,0,0,0.4);
  pointer-events: none;
  z-index: 4;
}

/* ================= HANDOUTS: ROWS view = folder spines ============= */
/* Not photos but the "spines" of case files: a horizontal manila strip
   with a coloured tab on the left and a typed title, stacked like files
   in a drawer with a slight overlap. */
.view--rows .handout-card {
  background:
    linear-gradient(90deg, rgba(0,0,0,0.06), rgba(0,0,0,0) 12%),
    var(--bg-panel);
  border: 1px solid var(--border);
  border-left: 8px solid var(--accent-2);   /* the folder's coloured tab */
  border-radius: 0 3px 3px 0;
  box-shadow: 1px 2px 4px rgba(0,0,0,0.35);
  padding: 8px 12px;
  margin-bottom: -2px;                        /* slight overlap = a stack */
  transform: none;
}
.view--rows .handout-card::before { display: none; }   /* no tack here */
/* Tab colour cycles like coloured file dividers. */
.view--rows .handout-card:nth-child(3n+1) { border-left-color: var(--accent); }
.view--rows .handout-card:nth-child(3n+2) { border-left-color: var(--accent-2); }
.view--rows .handout-card:nth-child(3n)   { border-left-color: var(--good); }
/* Thumbnail shrinks to a little photo clipped to the file. */
.view--rows .handout-card .h-thumb {
  background: #f6f1e2;
  padding: 2px;
  border: 1px solid rgba(0,0,0,0.15);
  box-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}
.view--rows .handout-card img,
.view--rows .handout-card .h-thumb--pdf { height: 56px; border: none; }
.view--rows .handout-card .h-title {
  font-family: var(--font-display);
  color: var(--ink);
  text-shadow: none;
  text-align: left;
  letter-spacing: 0.5px;
}
@media (hover: hover) {
  .view--rows .handout-card:hover { border-left-width: 12px; }  /* pull the file out */
}

/* ================= TREE view = index-card outline ================= */
/* The terminal tree sits directly on the dark board, so its leaves need
   LIGHT ink (the base gives .tree-leaf color:--ink = dark, invisible).
   Nodes (session headers) stay stamp-red; leaves are typed light text. */
.handout-tree { color: #b7ae99; }                 /* connector lines */
.handout-tree .tree-node { color: var(--accent); }   /* red section heads */
.handout-tree .tree-leaf { color: #ded5c0; }         /* light typed titles */
.handout-tree .tree-leaf:hover,
.handout-tree .tree-leaf--active { color: var(--accent); }
/* The detail panel's hint + border read on the board. */
.tree-detail { border-left-color: var(--border); }
.tree-detail__hint { color: #b7ae99; }

/* ================= FOLDERS = manila file folders ================== */
/* The folder-card becomes an actual folder: a manila body with a tab up
   top-left (a pseudo-element that sticks out above the border) and the
   cover mosaic reading as documents peeking out of the pocket. */
.folder-card {
  position: relative;
  background:
    linear-gradient(180deg, rgba(0,0,0,0.05), rgba(0,0,0,0) 20%),
    #dcd0ac;                              /* manila, a touch warmer */
  border: 1px solid var(--border);
  border-radius: 0 6px 6px 6px;           /* squared top-left for the tab */
  outline: none;                          /* drop the base double pixel border */
  box-shadow: 2px 4px 8px rgba(0,0,0,0.4);
  overflow: visible;
  margin-top: 14px;                       /* room for the protruding tab */
}
/* The folder tab: sticks up above the body, top-left. This REPLACES the
   old blue tack on .folder-card::before. */
.folder-card::before {
  content: "";
  position: absolute;
  top: -13px; left: -1px;
  width: 96px; height: 16px;
  background: #dcd0ac;
  border: 1px solid var(--border);
  border-bottom: none;
  border-radius: 6px 10px 0 0;
  box-shadow: 0 -1px 2px rgba(0,0,0,0.15);
  z-index: 1;
}
/* The mosaic: documents in the pocket. Paper edge, not a black grid. */
.folder-card__mosaic {
  background: #b8ab86;
  border-bottom: none;
  margin: 8px 8px 0;
  border: 1px solid rgba(0,0,0,0.2);
}
.folder-card__cell { background: #efe8d2; }   /* the light "sheets" inside */
.folder-card__pdf { color: var(--ink-dim); }
.folder-card__foot { padding: 8px 12px 10px; }
.folder-card__name {
  font-family: var(--font-display);
  color: var(--ink);
  text-shadow: none;
}
@media (hover: hover) {
  .folder-card:hover { transform: translateY(-3px); border-color: var(--accent); }
}

/* ---- "Visible/public" items get green case-string --------------- */
.h-item--public { box-shadow: 2px 2px 0 0 var(--good); }

/* ---- Motion: only a small settle on load, and only when the user
        hasn't asked for reduced motion. --------------------------- */
@media (prefers-reduced-motion: no-preference) {
  .panel, .wiki-card {
    animation: aa-settle 0.5s ease-out both;
  }
  @keyframes aa-settle {
    from { transform: translateY(-3px) rotate(-0.3deg); opacity: 0.6; }
    to   { transform: none; opacity: 1; }
  }
}
"""

THEME = Theme(
    id='analog-archive',
    name='Analog Archive',
    blurb='Noir case files: manila folders, redacted ink, and a CLASSIFIED stamp.',
    fonts=('Special Elite', 'Courier Prime'),
    scale=1.35,
    vars={
        # This is the one "board" theme: a dark corkboard/leather desk with
        # LIGHT manila-paper panels sitting on it. So --ink is DARK
        # (typewriter ink on paper), like Phandelver's inverted logic.
        '--bg': '#1c1b18',          # shadowed cork/leather desk, near-black
        '--bg-panel': '#e6ddc5',    # aged manila folder / paper
        '--ink': '#2b2b2b',         # typewriter ink on the paper
        '--ink-dim': '#6a6353',     # faded pencil / carbon-copy grey
        '--accent': '#9e2a2b',      # faded red rubber stamp
        '--accent-2': '#1c3d5a',    # biro / fountain-pen ink blue
        '--border': '#3a352c',      # soft brown paper edge (not hard black)
        '--shadow': 'rgba(0,0,0,0.55)',  # soft desk shadow, not pure black
        '--good': '#3f6d4e',        # green string / "verified" ink
    },
    extra_css=_EXTRA_CSS,
    home_label='Refile the Case (Home)',
    errors={
        400: ('\U0001F4DD', 'Illegible Handwriting',
              'We tried to process your file, but your cursive is unreadable. '
              'Please fill out a new form in block letters.'),
        401: ('\U0001FAAA', 'Show Your Badge',
              'The clerk refuses to take your folder. You need to show a valid '
              'company ID to the front desk first.'),
        403: ('\U0001F5C4\uFE0F', 'Locked Cabinet',
              'You are trying to pry open a locked filing drawer. You do not '
              'hold the key for this specific archive.'),
        404: ('\U0001F5D1\uFE0F', 'Shredded Paper',
              'The file you are looking for has been sent to the industrial '
              'shredder. There are only thin paper ribbons left.'),
        429: ('\U0001F975', 'Overworked Clerk',
              'The archivist can only stamp documents so fast! Give them a '
              'moment to catch up with your massive stack of requests.'),
        500: ('\U0001F525', 'Archive Fire',
              'Someone left a cigarette burning on a stack of old reports. The '
              'back office is currently dealing with a chaotic emergency.'),
    },
)
