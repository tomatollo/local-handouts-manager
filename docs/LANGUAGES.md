# Aggiungere una lingua

L'app traduce l'interfaccia con un catalogo semplice: nessuna dipendenza
esterna, nessun passo di build. La chiave di ogni voce è **la stringa inglese
stessa**, così una stringa non tradotta si mostra comunque in inglese senza
rompere nulla.

La lingua è **per-utente**, non globale: ogni giocatore sceglie la sua, il
Master la sua. La scelta viaggia in un cookie, e `?lang=` la imposta (così un
link può portare con sé una lingua).

Il codice vive nel package `handouts/i18n/`:

```
handouts/i18n/
├── __init__.py       # ri-esporta l'API pubblica (translate, resolve, LANGUAGES...)
├── config.py         # LANGUAGES, DEFAULT_LANG, COOKIE_NAME, COOKIE_MAX_AGE
├── resolver.py       # la logica: clean_lang, translate, resolve
└── catalogs/
    ├── __init__.py   # assembla CATALOG da tutte le lingue
    └── it.py         # un file per lingua: TRANSLATIONS = { 'English': 'Italiano', ... }
```

L'inglese è la **lingua sorgente**: le sue stringhe sono le chiavi, quindi non
esiste un `en.py` e `translate()` con `lang='en'` restituisce il testo così
com'è.

---

## Passi per aggiungere una lingua (es. spagnolo, `es`)

### 1. Crea il file del catalogo — `handouts/i18n/catalogs/es.py`

Il modo più semplice è copiare `it.py` e tradurre i **valori** (le chiavi
restano l'inglese, invariate):

```python
"""Spanish (es) UI translations."""

TRANSLATIONS = {
    # ---- Player: hub + folder ----
    'Player Hub': 'Zona de Jugadores',
    'Welcome, Adventurers!': '¡Bienvenidos, Aventureros!',
    'Browse': 'Explorar',
    # ... tutte le altre chiavi ...
}
```

Regole:

- **Non tradurre le chiavi.** La chiave è la stringa inglese esatta che compare
  nei template (tramite il filtro `|t`). Se la cambi, la traduzione non viene
  più trovata.
- **Non serve tradurre tutto subito.** Ogni chiave che ometti si mostrerà in
  inglese. Puoi partire dalle sezioni più visibili e completare col tempo.
- Il file è **solo dati**: nessun import, nessuna logica.

### 2. Registra il modulo — `handouts/i18n/catalogs/__init__.py`

Aggiungi una riga a `_LANGUAGE_MODULES`:

```python
_LANGUAGE_MODULES = {
    'it': 'it',
    'es': 'es',   # <-- qui
}
```

### 3. Aggiungi la lingua alla lista — `handouts/i18n/config.py`

Aggiungi il codice a `LANGUAGES`, col nome mostrato nello switcher **scritto in
quella lingua**:

```python
LANGUAGES = {
    'en': 'English',
    'it': 'Italiano',
    'es': 'Español',   # <-- qui
}
```

Fatto. Lo switcher di lingua ora mostra la nuova opzione su ogni pagina, e
`?lang=es` la attiva. Nessun altro file va toccato: `translate()`, il cookie e
il context dei template la raccolgono in automatico.

---

## Come funziona la ricerca (per riferimento)

`translate(text, lang)`:

1. se `lang` è l'inglese (`DEFAULT_LANG`), restituisce `text` così com'è;
2. altrimenti cerca `text` nel catalogo di quella lingua;
3. se non lo trova (chiave mancante o lingua sconosciuta), restituisce `text`
   invariato — cioè l'inglese.

Questo è ciò che rende sicuro un catalogo incompleto: una chiave mancante non è
un errore, è solo una stringa che resta in inglese.

`clean_lang(raw)` normalizza qualunque input (querystring o cookie) a un codice
supportato, ripiegando sull'inglese per valori sconosciuti. `resolve(request)`
decide la lingua di una richiesta: `?lang=` vince (ed è poi salvato nel cookie),
altrimenti decide il cookie esistente.

---

## Note sulle chiavi

- Le chiavi possono contenere apici: usa la forma Python adatta
  (`"Master's Screen"` con apici doppi, oppure `'L\\'Area'` con escape).
- L'ordine delle voci è **cosmetico** — la ricerca è per chiave — quindi puoi
  raggruppare le nuove stringhe nella sezione tematica giusta con un commento,
  come già fa `it.py` (player hub, dashboard, pagine d'errore, guida...).
- Una chiave duplicata nello stesso file non è un errore in Python (vince
  l'ultima), ma è meglio evitarla: se due sezioni hanno la stessa stringa
  inglese, basta una voce sola.
