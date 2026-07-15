"""UI translations.

Plain-dict catalogue, no external dependency and no build step: a key is the
English string itself, so an untranslated string still renders sensibly.

Language is per-user, not global: each player picks their own, the Master picks
their own. The choice rides in a cookie, and `?lang=` sets it (so a link can
carry a language). Resolution happens once per request in `resolve()`.
"""

# Supported languages: code -> the name shown in the switcher (in that language).
LANGUAGES = {
    'en': 'English',
    'it': 'Italiano',
}
DEFAULT_LANG = 'en'
COOKIE_NAME = 'lang'
# Roughly a year; the choice is a preference, not a session detail.
COOKIE_MAX_AGE = 60 * 60 * 24 * 365

# Only non-English needs entries. Keys are the exact English source strings.
CATALOG = {
    'it': {
        # ---- Player: hub + folder ----
        'Player Hub': 'Area Giocatori',
        'Welcome, Adventurers!': 'Benvenuti, Avventurieri!',
        'Handouts revealed by your Game Master appear below.':
            'Qui sotto compaiono i documenti rivelati dal vostro Master.',
        'Browse': 'Sfoglia',
        'Folders': 'Cartelle',
        'Sessions': 'Sessioni',
        'Tags': 'Etichette',
        'Recent': 'Recenti',
        'Rows': 'Elenco',
        'Cards': 'Schede',
        'View mode': 'Modalità di visualizzazione',
        'Clear': 'Azzera',
        'Search': 'Cerca',
        'Search everything': 'Cerca ovunque',
        'Title, tag, session...': 'Titolo, etichetta, sessione...',
        'Organize by': 'Organizza per',
        'Browse handouts': 'Sfoglia i documenti',
        'Close': 'Chiudi',
        'Session': 'Sessione',
        "No folders yet. Your Master hasn't grouped anything into collections.":
            'Ancora nessuna cartella. Il tuo Master non ha raccolto nulla in collezioni.',
        'Nothing matches your search.': 'Nessun risultato per la tua ricerca.',
        "Nothing revealed yet. Await your Master's word...":
            'Ancora nulla di rivelato. Attendi la parola del tuo Master...',
        'All collections': 'Tutte le collezioni',
        'Collection': 'Collezione',
        'This collection is empty.': 'Questa collezione è vuota.',
        'Language': 'Lingua',

        # ---- Player: lightbox ----
        'Previous': 'Precedente',
        'Next': 'Successivo',
        'Show info': 'Mostra info',
        'Hide info': 'Nascondi info',
        'Found at': 'Trovato a',

        # ---- Master: dashboard ----
        'Master Dashboard': 'Pannello del Master',
        "Master's Screen": 'Schermo del Master',
        'Forge scrolls and ancient tomes from here.':
            'Forgia pergamene e tomi antichi da qui.',
        'Search handouts...': 'Cerca documenti...',
        'Search handouts': 'Cerca documenti',
        'No handouts match your search.': 'Nessun documento corrisponde alla ricerca.',
        'Hidden': 'Nascosti',
        'Public': 'Pubblici',
        'Nothing hidden. Everything is public.':
            'Niente di nascosto. È tutto pubblico.',
        'Nothing published yet.': 'Ancora nulla di pubblicato.',
        'Edit': 'Modifica',
        'Publish': 'Pubblica',
        'Unpublish': 'Ritira',
        'Delete': 'Elimina',
        'Upload a Handout': 'Carica un Documento',
        'Title': 'Titolo',
        'Description': 'Descrizione',
        'Category': 'Categoria',
        'Viewer': 'Visualizzatore',
        'comma-separated': 'separate da virgola',
        'Session #': 'Sessione n.',
        'Session Title': 'Titolo Sessione',
        'Place of Discovery': 'Luogo del Ritrovamento',
        'Date of Discovery': 'Data del Ritrovamento',
        'Files': 'File',
        'images or PDF': 'immagini o PDF',
        'Select several images to build a carousel or book.':
            'Seleziona più immagini per creare un carosello o un libro.',
        'Back Cover': 'Retrocopertina',
        'Book viewer, optional': 'visualizzatore Libro, facoltativo',
        'Shown as the last page in the Book viewer.':
            "Mostrata come ultima pagina nel visualizzatore Libro.",
        'Forge Handout': 'Forgia Documento',
        'Group handouts any way you like. A handout can sit in several folders.':
            'Raggruppa i documenti come vuoi. Un documento può stare in più cartelle.',
        'New folder name': 'Nome nuova cartella',
        'Add': 'Aggiungi',
        'Folder name': 'Nome cartella',
        'Rename': 'Rinomina',
        'No folders yet — create one below.':
            'Ancora nessuna cartella — creane una qui sotto.',
        'Backup & Transfer': 'Backup e Trasferimento',
        'Move your whole library (handouts, images, folders) to another computer.':
            "Sposta l'intera libreria (documenti, immagini, cartelle) su un altro computer.",
        'Export everything (.zip)': 'Esporta tutto (.zip)',
        'Import from a .zip…': 'Importa da uno .zip…',
        'Appearance': 'Aspetto',
        'Theme': 'Tema',
        'Colours and fonts for everyone — players see this too.':
            'Colori e font per tutti — lo vedono anche i giocatori.',
        'Apply theme': 'Applica tema',
        'Interface language': 'Lingua interfaccia',
        'Your own choice — it does not affect the players.':
            'Scelta personale — non influisce sui giocatori.',

        # ---- Master: confirmations ----
        'Are you sure you want to publish this handout to the players?':
            'Vuoi davvero pubblicare questo documento per i giocatori?',
        'Delete this handout permanently? This removes the file too.':
            'Eliminare definitivamente questo documento? Rimuove anche il file.',
        "Delete this folder? Handouts stay, they're just unfiled from it.":
            'Eliminare questa cartella? I documenti restano, vengono solo tolti da essa.',

        # ---- Master: edit ----
        'Edit Handout': 'Modifica Documento',
        "Back to Master's Screen": 'Torna allo Schermo del Master',
        'optional': 'facoltativo',
        'Current Files': 'File Attuali',
        'Drag by the handle to reorder. The first file is the cover. Tick to remove on save.':
            "Trascina dalla maniglia per riordinare. Il primo file è la copertina. Spunta per rimuovere al salvataggio.",
        'What players see for this file': 'Cosa vedono i giocatori per questo file',
        'Remove': 'Rimuovi',
        'Add More Files': 'Aggiungi altri file',
        'A handout can live in several folders.':
            'Un documento può stare in più cartelle.',
        "No folders yet — create some on the Master's Screen.":
            'Ancora nessuna cartella — creane qualcuna nello Schermo del Master.',
        'Remove back cover': 'Rimuovi retrocopertina',
        'Upload a new file to replace it:':
            'Carica un nuovo file per sostituirla:',
        'Save Changes': 'Salva Modifiche',
        'Description (optional)': 'Descrizione (facoltativa)',

        # ---- Master: import/export ----
        'Import Library': 'Importa Libreria',
        'Import a Library': 'Importa una Libreria',
        'Upload a .zip you exported from another computer. Nothing is changed until you review and confirm.':
            'Carica uno .zip esportato da un altro computer. Nulla cambia finché non controlli e confermi.',
        "Couldn't read that file.": 'Impossibile leggere quel file.',
        'Export file (.zip)': 'File di esportazione (.zip)',
        "New handouts are added. Where the same handout exists on both sides but differs, you'll choose which version to keep.":
            'I documenti nuovi vengono aggiunti. Dove lo stesso documento esiste da entrambe le parti ma differisce, sceglierai quale versione tenere.',
        'Review import…': 'Controlla importazione…',
        'Choose a different file': 'Scegli un altro file',
        'Review Import': 'Controlla Importazione',
        'Summary': 'Riepilogo',
        'New handouts': 'Documenti nuovi',
        'Conflicts': 'Conflitti',
        'These handouts exist on both sides but differ. Choose which to keep for each.':
            'Questi documenti esistono da entrambe le parti ma differiscono. Scegli quale tenere per ognuno.',
        'Local': 'Locale',
        'Imported': 'Importato',
        'Identical (skipped)': 'Identici (saltati)',
        'Added': 'Aggiunti',
        'Replaced': 'Sostituiti',
        'Kept local': 'Tenuti locali',
        'Keep Local': 'Tieni il locale',
        'Replace with imported': "Sostituisci con l'importato",
        'Apply import': 'Applica importazione',
        'Cancel': 'Annulla',
        'Import Complete': 'Importazione Completata',
    },
}


def clean_lang(raw):
    """Return a supported language code, falling back to the default."""
    raw = (raw or '').strip().lower()
    return raw if raw in LANGUAGES else DEFAULT_LANG


def translate(text, lang):
    """Look the string up in the catalogue; unknown keys pass through as-is."""
    if lang == DEFAULT_LANG:
        return text
    return CATALOG.get(lang, {}).get(text, text)


def resolve(request):
    """Work out the language for this request.

    `?lang=` wins (it's an explicit click) and is then persisted to a cookie by
    the after_request hook; otherwise the existing cookie decides.
    """
    if 'lang' in request.args:
        return clean_lang(request.args.get('lang')), True
    return clean_lang(request.cookies.get(COOKIE_NAME)), False
