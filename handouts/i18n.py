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

        # ---- POP handout ----
        # 'POP' is left untranslated on purpose: it is the feature's name at
        # the table, and the megaphone glyph carries the meaning anyway.
        'POP': 'POP',
        'Publish & POP': 'Pubblica e POP',
        'Forge & POP': 'Forgia e POP',
        'Pop to all players': 'Fai apparire a tutti i giocatori',
        'Publishes immediately and shows it on every player screen.':
            'Pubblica subito e lo mostra su ogni schermo dei giocatori.',
        'Pop this handout onto every player screen now?':
            'Far apparire ora questo documento su ogni schermo dei giocatori?',
        'Publish this handout and pop it onto every player screen now?':
            'Pubblicare questo documento e farlo apparire ora su ogni schermo dei giocatori?',
        'Your Master is showing you something.':
            'Il tuo Master ti sta mostrando qualcosa.',
        'Open it': 'Apri',
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

        # ---- Master: navigation menu ----
        'Menu': 'Menù',
        "Master's menu": 'Menù del Master',
        'Handouts': 'Documenti',
        'Settings': 'Impostazioni',
        'Master Access': 'Accesso Master',
        'Lock master mode': 'Blocca modalità Master',

        # ---- Master: access / passphrase ----
        'This area is for the Game Master.':
            'Questa area è riservata al Master.',
        'Passphrase': 'Passphrase',
        'Unlock': 'Sblocca',
        'That passphrase is not right.': 'La passphrase non è corretta.',
        'Back to the Player Hub': "Torna all'Area Giocatori",
        'The master side is currently unprotected.':
            'Il lato Master non è attualmente protetto.',
        'Until you set a passphrase, anyone on this Wi-Fi can open the Master Wiki and the dashboard.':
            'Finché non imposti una passphrase, chiunque sia su questa rete Wi-Fi può aprire la Wiki del Master e il pannello.',
        'Set a passphrase': 'Imposta una passphrase',
        'Change passphrase': 'Cambia passphrase',
        'One passphrase for the Master. Players never need it.':
            'Una sola passphrase per il Master. Ai giocatori non serve mai.',
        'Current passphrase': 'Passphrase attuale',
        'New passphrase': 'Nuova passphrase',
        'Save passphrase': 'Salva passphrase',
        'This device': 'Questo dispositivo',
        'Lock master mode if you hand this device to a player.':
            'Blocca la modalità Master se passi questo dispositivo a un giocatore.',

        # ---- Wiki: shared ----
        'Wiki': 'Wiki',
        'Players Wiki': 'Wiki Giocatori',
        'Master Wiki': 'Wiki Master',
        'Master Wiki (secret)': 'Wiki Master (segreta)',
        'Quick reference for the campaign.':
            'Consultazione rapida per la campagna.',
        'What the party knows about the world.':
            'Ciò che il gruppo sa del mondo.',
        'Your own notes. Players never see these pages.':
            'I tuoi appunti. I giocatori non vedono mai queste pagine.',
        'Search the wiki...': 'Cerca nella wiki...',
        'Search the wiki': 'Cerca nella wiki',
        'Nothing written down yet.': 'Ancora nulla di scritto.',
        'No pages here yet. Create the first one.':
            'Ancora nessuna pagina. Creane una.',
        'This page is empty.': 'Questa pagina è vuota.',
        'Uncategorised': 'Senza categoria',
        'Master only': 'Solo Master',

        # ---- Wiki: editing ----
        'New page': 'Nuova pagina',
        'Edit page': 'Modifica pagina',
        'Create page': 'Crea pagina',
        # NB: not 'Summary' -- that key is already taken by the import review
        # page ('Riepilogo'). Keys ARE the English source string, so one key
        # cannot carry two meanings; the wiki's field is named distinctly.
        'Page actions': 'Azioni pagina',
        'Page summary': 'Sommario',
        'One line shown in the index.':
            "Una riga mostrata nell'indice.",
        'The Emerald Enclave': 'Enclave di Smeraldo',
        'Faction, Place, NPC...': 'Fazione, Luogo, PNG...',
        'Body': 'Testo',
        'Plain text. Line breaks are kept.':
            'Testo semplice. Gli a capo vengono mantenuti.',
        'Visible to': 'Visibile a',
        'Moving a page to the Players Wiki reveals it to the whole table.':
            "Spostare una pagina nella Wiki Giocatori la rivela a tutto il tavolo.",
        'Reveal to players': 'Rivela ai giocatori',
        'Hide from players': 'Nascondi ai giocatori',
        'Move this page to the Players Wiki? They will be able to read it.':
            'Spostare questa pagina nella Wiki Giocatori? Potranno leggerla.',
        'Move this page back to the Master Wiki? Players will no longer see it.':
            'Rispostare questa pagina nella Wiki Master? I giocatori non la vedranno più.',
        'Delete this wiki page permanently?':
            'Eliminare definitivamente questa pagina della wiki?',

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
        'New wiki pages': 'Nuove pagine wiki',
        'Wiki pages added': 'Pagine wiki aggiunte',
        'Keep Local': 'Tieni il locale',
        'Replace with imported': "Sostituisci con l'importato",
        'Apply import': 'Applica importazione',
        'Cancel': 'Annulla',
        'Import Complete': 'Importazione Completata',

        # ---- Error Pages ----
        'Page Not Found': 'Pagina Non Trovata',
        'Critical Fail': 'Fallimento Critico',
        'Natural 1 on Perception, you got lost. The room is shrouded in darkness, and the page you are looking for seems to have vanished into the Astral Plane or been devoured by a Mimic.': 
        "1 Naturale in Percezione, ti sei perso. La stanza è avvolta dall'oscurità e la pagina che stai cercando sembra essere svanita nel Piano Astrale o divorata da un Mimic.",
        'Flee the Dungeon (Home)': 'Fuggi dal Dungeon (Home)',
        
        # 400
        'Wild Magic Surge': 'Impulso di Magia Selvaggia',
        'You mixed up the spell components. Your request fizzled out in a shower of harmless sparks.': 
            'Hai mescolato male le componenti dell\'incantesimo. La tua richiesta si è dissolta in una pioggia di scintille inoffensive.',
            
        # 401
        'Failed Stealth Check': 'Fallimento in Furtività',
        "'Halt! Who goes there?' The guards caught you trying to sneak in without the proper passphrase.": 
            "'Alt! Chi va là?' Le guardie ti hanno sorpreso a intrufolarti senza la giusta parola d'ordine.",
            
        # 403
        'Magic Circle': 'Cerchio Magico',
        'A powerful barrier blocks your path. You lack the required alignment or level to enter this area.': 
            "Una potente barriera sbarra la strada. Ti manca l'allineamento o il livello necessario per accedere a quest'area.",
            
        # 404
        'Critical Fail': 'Fallimento Critico',
        'Natural 1 on Perception, you got lost. The room is shrouded in darkness, and the page you are looking for seems to have vanished into the Astral Plane or been devoured by a Mimic.': 
            "1 Naturale in Percezione, ti sei perso. La stanza è avvolta dall'oscurità e la pagina che stai cercando sembra essere svanita nel Piano Astrale o divorata da un Mimic.",
            
        # 500
        'The Weave is Tearing': 'La Trama è Lacerata',
        'The Dungeon Master spilled coffee on the campaign notes. The fabric of reality is temporarily unstable.': 
            'Il Dungeon Master ha rovesciato il caffè sugli appunti della campagna. Il tessuto della realtà è temporaneamente instabile.',

        # ---- App Guide ----
        'App Guide': 'Guida all\'App',
        'Help': 'Aiuto',
        'Back to Dashboard': 'Torna al Pannello',
        'For the Master': 'Per il Master',
        'Uploading Handouts:': 'Caricare i Documenti:',
        'Use the Dashboard to upload images or PDFs. You can assign them to folders, tag them, and write descriptions.': 
            'Usa il Pannello per caricare immagini o PDF. Puoi assegnarli a cartelle, etichettarli e scrivere descrizioni.',
        'Publishing vs Hidden:': 'Pubblicati vs Nascosti:',
        'Newly uploaded handouts are hidden by default. Click the Publish button to reveal them.': 
            'I nuovi documenti caricati sono nascosti di default. Clicca sul pulsante Pubblica per rivelarli.',
        'The POP Feature (Broadcast):': 'La funzione POP (Trasmissione):',
        'Click the POP button next to a handout. It will instantly pop up in full-screen on every player screen (expires in 2 minutes).': 
            'Clicca sul pulsante POP accanto a un documento. Apparirà istantaneamente a schermo intero su tutti gli schermi dei giocatori (scade dopo 2 minuti).',
        'For the Players': 'Per i Giocatori',
        'The Hub:': 'L\'Area Principale:',
        'The main page displays all the handouts the Master has revealed to you.': 
            'La pagina principale mostra tutti i documenti che il Master ti ha rivelato.',
        'Navigation:': 'Navigazione:',
        'You can browse by Folder, by Session, or search by tags and keywords.': 
            'Puoi sfogliare per Cartella, per Sessione, o cercare per etichette e parole chiave.',
        'Real-time Reveals:': 'Rivelazioni in Tempo Reale:',
        'Keep your tab open! If the Master triggers a POP broadcast, the handout will appear automatically.': 
            'Tieni la scheda aperta! Se il Master avvia una trasmissione POP, il documento apparirà automaticamente.',
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
