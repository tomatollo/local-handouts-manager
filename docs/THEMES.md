# Creare un tema

Un tema è un preset di aspetto: una palette di colori, due font, una scala per
i titoli, un eventuale blocco di CSS extra e le pagine d'errore a tema. Il tema
è **globale**: lo sceglie il Master dalla pagina *Appearance* e lo vedono anche
i giocatori, così tutto il tavolo condivide lo stesso look. Vive nel database
sotto `settings`.

Il punto chiave da capire prima di tutto: **un tema non ridisegna il layout**.
Il file `static/css/style.css` resta l'unica fonte di verità per la struttura
(ed è mobile-first). Un tema si limita a **ridipingere** le CSS custom
properties che `style.css` dichiara su `:root` — colori e font — iniettandole
in un piccolo blocco `<style>`. Il look "8-bit" (bordi netti, ombre a gradini)
sopravvive a un cambio di font perché vive nei bordi e nelle ombre, non nel
carattere.

Ogni tema è un file Python dentro `handouts/theming/themes/`, un tema per file.

---

## Anatomia di un tema

Il file più semplice possibile (`handouts/theming/themes/mio_tema.py`):

```python
"""Il Mio Tema -- una riga che descrive il mood."""

from ..base import Theme

THEME = Theme(
    id='mio-tema',
    name='Il Mio Tema',
    blurb='Una frase breve, mostrata sotto il nome nel picker.',
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

Il modulo **deve** esporre una variabile a livello di modulo chiamata `THEME`,
istanza di `Theme`. È tutto ciò che il registro cerca.

---

## I campi di `Theme`

| Campo | Obbligatorio | Cos'è |
|-------|:---:|-------|
| `id` | sì | Lo slug usato nell'URL e salvato nel DB, es. `'curse-of-strahd'`. Deve essere **unico**. È il valore che il picker invia. |
| `name` | sì | L'etichetta leggibile mostrata nel picker (`'Curse of Strahd'`). |
| `blurb` | sì | Una riga sotto il nome nel picker. |
| `fonts` | sì | Tupla `(display, body)`: il font dei titoli e quello del testo lungo. Entrambi nomi di famiglie Google Fonts. Vedi *Font* sotto. |
| `scale` | sì | Moltiplica la dimensione di ogni titolo. Vedi *La scala* sotto. |
| `vars` | sì | Il dizionario delle CSS custom property da sovrascrivere. Vedi *I token* sotto. |
| `extra_css` | no | CSS grezzo aggiunto **dopo** il blocco `:root`, solo quando il tema è attivo. Per texture, animazioni, ritocchi ai componenti. Vedi *CSS extra* sotto. Default: stringa vuota. |
| `errors` | no | Le pagine d'errore a tema, `{codice_http: (icona, titolo, messaggio)}`. Vedi *Pagine d'errore* sotto. Default: `{}` (eredita dal tema di default). |

---

## I token (`vars`)

Sono le nove CSS custom property che `style.css` dichiara su `:root`. Un tema
le ridipinge. Definiscile **tutte e nove** — così un cambio di tema non lascia
mai la UI mezza dipinta.

| Token | Cos'è |
|-------|-------|
| `--bg` | Sfondo della pagina. |
| `--bg-panel` | Sfondo dei pannelli/carte, un gradino sopra `--bg`. |
| `--ink` | Colore del testo principale. |
| `--ink-dim` | Testo secondario/attenuato. |
| `--accent` | Il colore dominante: bottoni, titoli, evidenziazioni. |
| `--accent-2` | Il colore secondario. |
| `--border` | Il bordo netto (di solito nero). |
| `--shadow` | Il colore dell'ombra a gradini (di solito nero). |
| `--good` | Il verde "visibile/pubblico" (handout rivelati). |

### Temi chiari vs scuri

La maggior parte dei temi è **scura**: `--ink` chiaro su `--bg-panel` scuro.
Ma niente è cablato: *Phandelver* è un tema chiaro (inchiostro scuro su
pergamena chiara), e *Analog Archive* è un tema "board" (scrivania scura con
pannelli di carta manila chiara, quindi `--ink` è scuro). Tutto legge da questi
token, quindi entrambe le direzioni funzionano senza casi speciali — basta
scegliere i valori coerenti tra loro.

---

## I font

`fonts=(display, body)`. Le famiglie vengono scaricate da Google Fonts.

Se una famiglia ha assi variabili (peso, corsivo) senza una posizione di
default, l'API `css2` di Google **rifiuta** la richiesta se passata come nudo
`family=Nome` — e, peggio, fa fallire l'**intera** richiesta, trascinando giù
anche l'altro font e facendo ripiegare la pagina su Georgia. Per questo le
famiglie con assi vanno registrate con la loro stringa `family=` completa in
`handouts/theming/fonts.py`, dentro il dizionario `FONT_QUERY`.

Regola pratica:

- **Font a stile singolo** (es. `Press Start 2P`, `VT323`, `Uncial Antiqua`):
  non serve fare nulla. Vengono richiesti come `family=Nome+Con+Più` in
  automatico.
- **Font con pesi/corsivo** (es. `Merriweather`, `Lora`, `Orbitron`,
  `EB Garamond`): aggiungi una riga in `FONT_QUERY` con gli assi enumerati.
  Gli assi vanno in ordine alfabetico (`ital` prima di `wght`) e le tuple
  ordinate — l'API lo richiede.

Esempio da `fonts.py`:

```python
FONT_QUERY = {
    'Orbitron': 'family=Orbitron:wght@400;500;600;700;800;900',
    'EB Garamond': 'family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;'
                   '1,400;1,500;1,600;1,700',
    # ...
}
```

Se un font non appare quando provi il tema, quasi sempre è questo: manca la sua
riga in `FONT_QUERY`, o gli assi non sono ordinati come vuole l'API.

Ogni tema scarica **solo** i suoi due font. La pagina *Appearance* è l'unica che
li scarica tutti insieme (`all_fonts_url`), perché il picker mostra ogni riquadro
nel suo carattere.

---

## La scala

`scale` moltiplica la dimensione di ogni titolo. Serve perché il CSS di base è
calibrato su **Press Start 2P**, un font pixel largo e basso per il suo corpo.
Un font normale alla stessa dimensione sembra minuscolo, quindi ogni tema
dichiara la propria correzione.

Valori tipici:

- `1` — solo per temi che usano Press Start 2P (Dungeon Torch, Vintage Arcade).
- `1.3–1.6` — la maggior parte dei serif/display normali (Cinzel, Lora, Orbitron).
- `1.75–1.9` — i blackletter, stretti e ornati, che hanno bisogno del bump più
  forte per restare leggibili (Curse of Strahd 1.9, Vecna 1.75).

Regola pratica: prova il tema, e se i titoli sembrano piccoli alza la scala; se
un titolo lungo trabocca (specie un blackletter), abbassala un filo.

C'è anche un automatismo collegato: l'ombra a gradini dietro i titoli
(`--display-shadow`) ha senso solo sotto un font pixel. Per ogni tema il cui
font display **non** è `Press Start 2P`, il sistema la spegne da solo — non devi
fare nulla.

---

## CSS extra (`extra_css`)

Serve quando un tema vuole fare di più che ridipingere i token: texture,
animazioni, ritocchi a componenti specifici. Il CSS extra sta **dentro il file
del tema**, come stringa, e viene aggiunto dopo il blocco `:root` **solo quando
quel tema è attivo** — quindi non serve nessun guard tipo `[data-theme=...]` e
gli altri temi non lo pagano mai.

Convenzione: definisci il CSS come costante a livello di modulo e passalo al
campo `extra_css`, così il `Theme(...)` resta leggibile:

```python
from ..base import Theme

_EXTRA_CSS = """
/* ---- Il Mio Tema: descrizione dell'effetto ---- */
.panel {
  box-shadow: var(--px) var(--px) 0 0 var(--shadow),
              inset 0 0 0 1px rgba(224,165,58,0.2);
}
h1, h2, h3, .pixel {
  text-shadow: 0 0 6px rgba(224,165,58,0.4);
}
"""

THEME = Theme(
    id='mio-tema',
    # ... gli altri campi ...
    extra_css=_EXTRA_CSS,
)
```

### Regole per scrivere `extra_css`

1. **Usa selettori reali.** Aggancia classi che esistono davvero nella UI:
   `.panel`, `.btn`, `.btn--pop`, `.handout-card`, `.folder-card`, `.wiki-card`,
   `.count-badge`, `.tag`, `.lightbox__*`, `body`, `body::before`, ecc. Guarda
   `style.css` per l'elenco.
2. **Riusa i token, non hard-coddare i colori** dove puoi: `var(--accent)`,
   `var(--shadow)`, `var(--px)` (l'unità pixel di base). Così se un domani ritocchi
   la palette, il CSS extra segue.
3. **Ogni animazione va dietro `prefers-reduced-motion`.** Chi ha chiesto meno
   movimento non deve vederne:
   ```css
   @media (prefers-reduced-motion: no-preference) {
     body { animation: mio-effetto 20s ease-in-out infinite alternate; }
     @keyframes mio-effetto { /* ... */ }
   }
   ```
4. **Gli effetti hover solo dove c'è un puntatore vero**, per non incastrarli su
   touch:
   ```css
   @media (hover: hover) {
     .btn:hover { /* ... */ }
   }
   ```
5. **I pseudo-elementi decorativi non devono intercettare i click:** aggiungi
   `pointer-events: none;` a ogni `::before`/`::after` ornamentale.

Esempi completi e commentati: apri `tashas_cauldron.py` (animazione di sfondo +
gradiente sui titoli), `analog_archive.py` (il più ricco: carta su lavagna,
polaroid, timbro CLASSIFIED) o `holo_hud.py` (cornici tagliate con `clip-path`).

---

## Pagine d'errore (`errors`)

Ogni tema può avere le sue pagine d'errore a tema: un 404 sotto *Curse of
Strahd* recita "Phantom Village", lo stesso 404 sotto *Vintage Arcade* recita
"Missing ROM". Il campo è un dizionario `{codice: (icona, titolo, messaggio)}`:

```python
    errors={
        400: ('\U0001F4A5', 'Titolo', 'Messaggio più lungo che spiega.'),
        401: ('\U0001F6D1', 'Titolo', 'Messaggio.'),
        403: ('...', '...', '...'),
        404: ('...', '...', '...'),
        429: ('...', '...', '...'),
        500: ('...', '...', '...'),
    },
```

- L'**icona** è un'emoji (comoda come escape `\U0001F4A5`, ma va bene anche
  l'emoji letterale).
- **Titolo** e **messaggio** sono stringhe inglesi: passano dal filtro `|t` in
  `error.html`, quindi se hai una traduzione italiana nel catalogo i18n verrà
  applicata, altrimenti si vede l'inglese.
- I codici gestiti sono **400, 401, 403, 404, 429, 500**.

Il campo è **opzionale** e anche parziale: qualunque codice tu ometta (o l'intero
`errors={}`) ripiega sul testo del tema di default (Dungeon Torch). Così un tema
nuovo mostra pagine d'errore sensate ancora prima che tu ne scriva le tue.

Nota: l'etichetta tipo ("Bad Request", "Not Found") **non** si mette qui — è
fissa per codice e vive una volta sola in `base.py` (`ERROR_TYPE_EN`).

---

## Registrare il tema

Creato il file, il tema va dichiarato in due punti (nessun altro file va toccato):

### 1. L'ordine — `handouts/theming/themes/__init__.py`

Aggiungi il **nome del modulo** (senza `.py`) alla tupla `_ORDER`, nella
posizione in cui vuoi che appaia:

```python
_ORDER = (
    'dungeon_torch',
    'phandelver',
    # ...
    'mio_tema',          # <-- qui
)
```

`_ORDER` è la fonte di verità unica di quali temi esistono e in che ordine. Un
modulo che esiste ma **non** è in `_ORDER` semplicemente non viene mostrato —
comodo per parcheggiare un tema work-in-progress senza cancellarlo.

### 2. La famiglia nel picker — `handouts/theming/groups.py`

Il picker raggruppa i temi in famiglie ("Dungeons & Dragons", "Other
Universes"). Aggiungi l'`id` del tema alla tupla della famiglia giusta in
`THEME_GROUPS`:

```python
THEME_GROUPS = (
    ('Dungeons & Dragons', (
        'phandelver',
        # ...
    )),
    ('Other Universes', (
        'dungeon-torch',
        'mio-tema',       # <-- qui, se non è D&D
    )),
)
```

Se **dimentichi** questo passo non è un dramma: un tema che nessuna famiglia
nomina finisce automaticamente nell'**ultima** famiglia ("Other Universes").
Ma metterlo esplicitamente rende chiaro dove vive.

---

## Checklist finale

- [ ] File in `handouts/theming/themes/<nome>.py` con una variabile `THEME`.
- [ ] Tutti e nove i token in `vars`.
- [ ] I font con assi variabili aggiunti a `FONT_QUERY` in `fonts.py`.
- [ ] `scale` provata a occhio (titoli né minuscoli né traboccanti).
- [ ] Eventuale `extra_css`: selettori reali, `prefers-reduced-motion` sulle
      animazioni, `@media (hover: hover)` sugli hover, `pointer-events: none`
      sui decori.
- [ ] Modulo aggiunto a `_ORDER` in `themes/__init__.py`.
- [ ] `id` aggiunto a una famiglia in `groups.py`.
- [ ] Riavvia l'app e controlla: il tema appare nel picker, si applica, le
      pagine d'errore funzionano.

---

## Architettura del package (per riferimento)

```
handouts/theming/
├── __init__.py       # ri-esporta l'API pubblica (css_vars, fonts_url, ...)
├── base.py           # la dataclass Theme + ERROR_TYPE_EN
├── registry.py       # la logica: clean_theme, theme_list, theme_groups,
│                     #   css_vars, theme_errors, theme_preview_style,
│                     #   e i wrapper id-based fonts_url / all_fonts_url
├── fonts.py          # FONT_QUERY + costruzione degli URL Google Fonts
├── groups.py         # THEME_GROUPS (le famiglie del picker)
└── themes/
    ├── __init__.py   # _ORDER -> raccoglie i temi in THEMES
    └── <un file per tema>.py
```

L'API pubblica che il resto dell'app usa (`theming.css_vars`,
`theming.fonts_url`, `theming.theme_errors`, ecc.) è esportata da `__init__.py`
e non cambia mai quando aggiungi un tema — tocchi solo `themes/` e i due file di
registrazione.
