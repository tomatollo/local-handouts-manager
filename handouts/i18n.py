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
        'Tree': 'Albero',
        'Handout tree': 'Albero dei documenti',
        'empty': 'vuoto',
        'No handouts yet.': 'Ancora nessun documento.',
        'Ungrouped': 'Non raggruppati',
        'Group by': 'Raggruppa per',
        'View': 'Vista',
        'Details': 'Dettagli',
        'Select a handout from the tree to see it here.':
            'Seleziona un documento dall\'albero per vederlo qui.',
        'Open': 'Apri',
        'Icon background': 'Sfondo icona',
        # ---- Footer, Create page, status, passphrase nag ----
        'Create': 'Crea',
        'Create a Handout': 'Crea un Documento',
        'Upload a scroll, map or tome and file it away.':
            'Carica una pergamena, una mappa o un tomo e archivialo.',
        'Upload a new handout and manage folders on their own page.':
            'Carica un nuovo documento e gestisci le cartelle in una pagina dedicata.',
        'Footer': 'Piè di pagina',
        'Updated': 'Aggiornato',
        'Online': 'Online',
        'Offline': 'Offline',
        'Interactive Map': 'Mappa Interattiva',
        'Built for the table: for the maps unrolled, the secrets kept, and the handouts slid across to the right player at the right moment.':
            'Fatto per il tavolo: per le mappe srotolate, i segreti custoditi e i documenti fatti scivolare al giocatore giusto al momento giusto.',
        'Thanks to my players for every session, and to every Game Master keeping worlds alive.':
            'Grazie ai miei giocatori per ogni sessione, e a ogni Master che tiene vivi i suoi mondi.',
        'No passphrase set - the Master side is open to anyone on this network.':
            'Nessuna passphrase impostata - il lato Master è aperto a chiunque sia su questa rete.',
        'Set one': 'Impostane una',
        'Dismiss for now': 'Ignora per ora',
        # ---- QR join page ----
        'Join by QR': 'Accedi con QR',
        'QR': 'QR',
        'QR code': 'Codice QR',
        'Point a phone camera at the code to open the player page.':
            'Inquadra il codice con la fotocamera del telefono per aprire la pagina dei giocatori.',
        'Scan to open the players\' handouts on this device.':
            'Scansiona per aprire i documenti dei giocatori su questo dispositivo.',
        'Player URL': 'Indirizzo giocatori',
        'Copy link': 'Copia link',
        'Copied!': 'Copiato!',
        'Print': 'Stampa',
        'Open': 'Apri',
        'You opened this page on localhost, so the code points back to this computer only. Open the app using your computer\'s network address (e.g. 192.168.x.x) for other devices to connect.':
            'Hai aperto questa pagina su localhost, quindi il codice punta solo a questo computer. Apri l\'app usando l\'indirizzo di rete del computer (es. 192.168.x.x) perché altri dispositivi possano collegarsi.',
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
        'Zoom': 'Zoom',
        'Zoom in': 'Ingrandisci',
        'Zoom out': 'Riduci',
        'Reset zoom': 'Ripristina zoom',
        # ---- Player: secret reveal (password box in the viewer) ----
        'Reveal': 'Rivela',
        'Wrong password.': 'Password errata.',
        'Could not check that right now.':
            'Impossibile verificare al momento.',

        # ---- Master: dashboard ----
        'Master Dashboard': 'Pannello del Master',
        "Master's Screen": 'Schermo del Master',
        'View scrolls and ancient tomes from here.':
            'Visualizza pergamene e tomi antichi.',
        'Search handouts...': 'Cerca documenti...',
        'Search handouts': 'Cerca documenti',
        'No handouts match your search.': 'Nessun documento corrisponde alla ricerca.',
        'Hidden': 'Nascosti',
        'Public': 'Pubblici',
        # ---- Group by: Format ----
        'Format': 'Formato',
        'Other': 'Altro',
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
        # ---- Book covers (hard/soft) ----
        'Book covers': 'Copertine libro',
        'Hard covers': 'Copertine rigide',
        'Hard covers (Book viewer)': 'Copertine rigide (visualizzatore Libro)',
        'First and last page turn like a stiff cover. Uncheck to flip them softly.':
            'La prima e l\'ultima pagina si girano come una copertina rigida. Deseleziona per sfogliarle come pagine normali.',
        'When on, the first and last page turn like a stiff book cover. Turn off to flip them like normal pages.':
            'Se attivo, la prima e l\'ultima pagina si girano come una copertina rigida. Disattiva per sfogliarle come pagine normali.',
        'comma-separated': 'separate da virgola',
        'Session #': 'Sessione n.',
        'Session Title': 'Titolo Sessione',
        'Place of Discovery': 'Luogo del Ritrovamento',
        'Date of Discovery': 'Data del Ritrovamento',
        # ---- Secret reveal (master create/edit) ----
        'Password': 'Password',
        'Passwords': 'Password',
        'one per line, optional': 'una per riga, facoltativo',
        'One word per line. Any of them unlocks the handout.':
            'Una parola per riga. Una qualsiasi sblocca il documento.',
        'Ignore uppercase / lowercase': 'Ignora maiuscole / minuscole',
        'A word the players must type':
            'Una parola che i giocatori devono digitare',
        'Handout to reveal': 'Documento da rivelare',
        '— none —': '— nessuno —',
        'hidden': 'nascosto',
        "When a player types the password in this handout's info panel, the chosen handout opens in its place.":
            'Quando un giocatore digita la password nel pannello info di questo documento, il documento scelto si apre al suo posto.',
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
        'No folders yet, create one below.':
            'Ancora nessuna cartella, creane una qui sotto.',
        'Backup & Transfer': 'Backup e Trasferimento',
        'Move your whole library (handouts, images, folders) to another computer.':
            "Sposta l'intera libreria (documenti, immagini, cartelle) su un altro computer.",
        'Export everything (.zip)': 'Esporta tutto (.zip)',
        'Import from a .zip…': 'Importa da uno .zip…',
        'Appearance': 'Aspetto',
        'Theme': 'Tema',
        # Theme-group headings in the picker. 'Dungeons & Dragons' is left as-is
        # (it's the game's proper name); the second is the catch-all family.
        'Dungeons & Dragons': 'Dungeons & Dragons',
        'Other Universes': 'Altri Universi',
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
        # ---- Import: interactive map section ----
        'The bundle carries a map. Keep your current map, or replace it with the imported one. This is all-or-nothing: the map is a single scene, not a merge.':
            'Il pacchetto contiene una mappa. Tieni la tua mappa attuale oppure sostituiscila con quella importata. \u00c8 tutto-o-niente: la mappa \u00e8 una scena unica, non una fusione.',
        'Revealed hexes': 'Esagoni rivelati',
        'Points of interest': 'Punti di interesse',
        'Background image': 'Immagine di sfondo',
        'No map yet.': 'Ancora nessuna mappa.',
        'Keep my map': 'Tieni la mia mappa',
        'Use imported map': 'Usa la mappa importata',
        'Map imported': 'Mappa importata',
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
            
        # 500
        'The Weave is Tearing': 'La Trama è Lacerata',
        'The Dungeon Master spilled coffee on the campaign notes. The fabric of reality is temporarily unstable.': 
            'Il Dungeon Master ha rovesciato il caffè sugli appunti della campagna. Il tessuto della realtà è temporaneamente instabile.',

        # 429
        'Slow Down, Adventurer': 'Rallenta, Avventuriero',
        'You are hammering the gates faster than the guards can answer. Wait a moment and try again.':
            'Stai martellando i cancelli più in fretta di quanto le guardie riescano a rispondere. Aspetta un momento e riprova.',

        # ===== D&D: Lost Mine of Phandelver =====
        'Illegible Map': 'Mappa Illeggibile',
        "Gundren's map seems stained with ale. We couldn't read your request parameters.":
            'La mappa di Gundren è macchiata di birra. Non siamo riusciti a leggere i parametri della tua richiesta.',
        'Neverwinter Guard': 'Guardia di Neverwinter',
        '"Halt, traveler!" You don\'t have the proper identification papers to enter this district.':
            '"Alt, viaggiatore!" Non hai i documenti giusti per entrare in questo quartiere.',
        'Sealed Vault': 'Cripta Sigillata',
        'The doors to the Tresendar vaults are locked tight. Only the guild master holds the key.':
            'Le porte delle cripte di Tresendar sono ben serrate. Solo il maestro della gilda ha la chiave.',
        'Empty Mine': 'Miniera Vuota',
        'You dug too deep in the wrong spot. This tunnel leads to a dead end.':
            'Hai scavato troppo a fondo nel posto sbagliato. Questo tunnel porta a un vicolo cieco.',
        'Goblin Swarm': 'Sciame di Goblin',
        'Too many arrows flying at once! Take cover and wait a moment before charging again.':
            'Troppe frecce in volo tutte insieme! Mettiti al riparo e aspetta un momento prima di caricare di nuovo.',
        'Cave-In!': 'Crollo!',
        'The ceiling of the mine just collapsed! Our goblin engineers are digging the server out of the rubble.':
            'Il soffitto della miniera è appena crollato! I nostri ingegneri goblin stanno estraendo il server dalle macerie.',

        # ===== D&D: Phandelver and Below: The Shattered Obelisk =====
        'Cracked Rune': 'Runa Incrinata',
        'The rune you inscribed is fractured. Your malformed request crumbled before it could resolve.':
            'La runa che hai inciso è fratturata. La tua richiesta malformata si è sgretolata prima di risolversi.',
        'Redbrand Checkpoint': 'Posto di Blocco dei Mantelli Rossi',
        'The Redbrands bar your way. You lack the token that lets you pass into Tresendar.':
            'I Mantelli Rossi ti sbarrano la strada. Ti manca il pegno che permette di passare a Tresendar.',
        'Aberrant Ward': 'Barriera Aberrante',
        'The shattered obelisk pulses and rejects you. This chamber is sealed against the unworthy.':
            "L'obelisco frantumato pulsa e ti respinge. Questa camera è sigillata contro gli indegni.",
        'Collapsed Shaft': 'Pozzo Crollato',
        'The tunnel caved in ahead. Whatever you sought is buried somewhere beyond the rubble.':
            'Il tunnel è crollato più avanti. Ciò che cercavi è sepolto da qualche parte oltre le macerie.',
        'Warping Presence': 'Presenza Distorcente',
        'Reality is bending too fast around you. Step back from the obelisk and let it settle.':
            "La realtà si piega troppo in fretta attorno a te. Allontanati dall'obelisco e lascia che si assesti.",
        'Obelisk Backlash': 'Contraccolpo dell\'Obelisco',
        'The obelisk discharged raw aberrant power through the server. Containment routines are re-forming reality.':
            "L'obelisco ha scaricato potere aberrante grezzo attraverso il server. Le routine di contenimento stanno ricostruendo la realtà.",

        # ===== D&D: Curse of Strahd =====
        'Misread Tarokka': 'Tarokka Male Interpretati',
        'Madame Eva shakes her head. You misinterpreted the cards, and your request is malformed.':
            'Madame Eva scuote la testa. Hai interpretato male le carte, e la tua richiesta è malformata.',
        'No Invitation': 'Nessun Invito',
        'The gates of Castle Ravenloft remain closed. You have not been invited by the master of the domain.':
            'I cancelli del Castello di Ravenloft restano chiusi. Non sei stato invitato dal signore del dominio.',
        "Strahd's Command": 'Ordine di Strahd',
        '"I am the Ancient. I am the Land." The vampire lord strictly forbids your presence here.':
            '"Io sono l\'Antico. Io sono la Terra." Il signore vampiro proibisce severamente la tua presenza qui.',
        'Phantom Village': 'Villaggio Fantasma',
        'You arrived at the coordinates, but found only an abandoned, rotting husk of a page.':
            'Sei arrivato alle coordinate, ma hai trovato solo il guscio abbandonato e marcescente di una pagina.',
        'Frantic Knocking': 'Bussare Frenetico',
        "Pounding on the village doors won't make them open faster. The locals are terrified, wait a minute.":
            'Battere sulle porte del villaggio non le farà aprire più in fretta. Gli abitanti sono terrorizzati, aspetta un minuto.',
        'Dark Powers Intervene': 'I Poteri Oscuri Intervengono',
        "The mysterious entities of the shadowfell have corrupted the server's soul.":
            "Le misteriose entità dello Shadowfell hanno corrotto l'anima del server.",

        # ===== D&D: Tomb of Annihilation =====
        'Broken Compass': 'Bussola Rotta',
        'Your magnetic compass is spinning wildly in the jungle. Your navigation parameters are invalid.':
            'La tua bussola magnetica gira all\'impazzata nella giungla. I tuoi parametri di navigazione non sono validi.',
        'Flaming Fist Toll': 'Pedaggio del Pugno Fiammante',
        "You haven't paid for your charter of exploration. The Flaming Fist denies you passage.":
            'Non hai pagato la tua licenza di esplorazione. Il Pugno Fiammante ti nega il passaggio.',
        "Soulmonger's Ward": 'Barriera del Divoranime',
        'Acererak has sealed this chamber. Your soul is not strong enough to pierce the barrier.':
            'Acererak ha sigillato questa camera. La tua anima non è abbastanza forte da forare la barriera.',
        "Syndra's Missing Map": 'La Mappa Perduta di Syndra',
        "The hex grid for this area is blank. You haven't explored this part of Chult yet.":
            'La griglia esagonale di questa zona è vuota. Non hai ancora esplorato questa parte di Chult.',
        'Jungle Fever': 'Febbre della Giungla',
        "You're marching through the sweltering jungle too quickly. Take a sip of water and slow down.":
            'Stai marciando troppo in fretta nella giungla soffocante. Bevi un sorso d\'acqua e rallenta.',
        "Acererak's Laugh": 'La Risata di Acererak',
        'The archlich just cast Meteor Swarm on the server! We are trying to cast Mending.':
            "L'arcilich ha appena lanciato Sciame di Meteore sul server! Stiamo cercando di lanciare Aggiustare.",

        # ===== D&D: Waterdeep: Dragon Heist =====
        'Forged Deed': 'Atto Falsificato',
        'The property deed you presented is a forgery. The clerk at the Palace rejects your paperwork.':
            "L'atto di proprietà che hai presentato è un falso. Il funzionario del Palazzo respinge le tue scartoffie.",
        'No Guild Token': 'Nessun Pegno di Gilda',
        'You have no writ from the guilds. The Waterdhavian watch will not let you through.':
            'Non hai alcun lasciapassare delle gilde. La guardia di Waterdeep non ti farà passare.',
        "Dragon's Vault": 'Il Caveau del Drago',
        'The half-million gold is not for you. This vault is sealed to all but the holder of the Stone.':
            'Il mezzo milione d\'oro non è per te. Questo caveau è sigillato a chiunque tranne il detentore della Pietra.',
        'Trail Gone Cold': 'Pista Raffreddata',
        'The coin led nowhere. The lead you were chasing has vanished into the city crowds.':
            'La moneta non ha portato a nulla. L\'indizio che inseguivi è svanito tra la folla della città.',
        'Too Many Factions': 'Troppe Fazioni',
        "You're chasing every faction at once. Slow down before the whole city is on your tail.":
            'Stai inseguendo ogni fazione tutte insieme. Rallenta prima che l\'intera città ti stia alle calcagna.',
        'Guild War': 'Guerra tra Gilde',
        'The factions came to blows in the streets. The city is in chaos while order is restored.':
            'Le fazioni sono venute alle mani per le strade. La città è nel caos mentre si ripristina l\'ordine.',

        # ===== D&D: Waterdeep: Dungeon of the Mad Mage =====
        'Lost on the Level': 'Perso nel Livello',
        'Undermountain twisted your map. Your request wandered into the wrong corridor and never returned.':
            'Sottomonte ha stravolto la tua mappa. La tua richiesta si è persa nel corridoio sbagliato e non è più tornata.',
        'Warded Door': 'Porta Protetta',
        'A sigil-locked door blocks the way. You lack the phrase Halaster set upon it.':
            'Una porta chiusa da un sigillo sbarra la via. Ti manca la formula che Halaster vi ha posto.',
        "Halaster's Whim": 'Il Capriccio di Halaster',
        'The Mad Mage has decided you may not pass. His dungeon rearranges itself to keep you out.':
            'Il Mago Folle ha deciso che non puoi passare. Il suo dungeon si riorganizza per tenerti fuori.',
        'Empty Level': 'Livello Vuoto',
        'This level of Undermountain is bare stone. Nothing you sought is here -- or it moved when you blinked.':
            'Questo livello di Sottomonte è nuda pietra. Nulla di ciò che cercavi è qui — o si è spostato mentre sbattevi le palpebre.',
        'Teleport Trap': 'Trappola di Teletrasporto',
        'You keep tripping the same teleport glyph. Pause before the dungeon flings you somewhere worse.':
            'Continui a calpestare lo stesso glifo di teletrasporto. Fermati prima che il dungeon ti scaraventi in un posto peggiore.',
        'Arcane Meltdown': 'Collasso Arcano',
        "Halaster's experiments overloaded the weave. The dungeon is reshaping itself while it recovers.":
            'Gli esperimenti di Halaster hanno sovraccaricato la trama. Il dungeon si sta rimodellando mentre si riprende.',

        # ===== D&D: The Rise of Tiamat =====
        'Fake Tribute': 'Tributo Falso',
        'You tried to offer counterfeit gold to the hoard. The cult rejects your malformed request.':
            'Hai provato a offrire oro contraffatto al tesoro. Il culto respinge la tua richiesta malformata.',
        "Wyrmspeaker's Seal": 'Sigillo del Wyrmspeaker',
        'You lack the proper cult passphrase. The guards are drawing their scimitars.':
            'Ti manca la giusta parola d\'ordine del culto. Le guardie stanno sguainando le scimitarre.',
        'Chromatic Barrier': 'Barriera Cromatica',
        "Tiamat's magic seals this domain. Mortals without a Wyrmspeaker's blessing are strictly forbidden.":
            'La magia di Tiamat sigilla questo dominio. I mortali senza la benedizione di un Wyrmspeaker sono severamente banditi.',
        'Plundered Hoard': 'Tesoro Saccheggiato',
        'The treasure you seek is gone. Adventurers probably looted this page yesterday.':
            'Il tesoro che cerchi non c\'è più. Probabilmente degli avventurieri hanno saccheggiato questa pagina ieri.',
        'Hold the Line': 'Tenete la Linea',
        "You're sending troops to the frontline too quickly. Let the vanguard breathe!":
            'Stai mandando truppe al fronte troppo in fretta. Lascia respirare l\'avanguardia!',
        'Council Uproar': 'Tumulto del Consiglio',
        'The factions of Waterdeep are fighting again. Our backend diplomacy has completely broken down.':
            'Le fazioni di Waterdeep stanno di nuovo litigando. La nostra diplomazia di backend è completamente saltata.',

        # ===== D&D: Out of the Abyss =====
        'Tangled Web': 'Ragnatela Aggrovigliata',
        "Your request got caught in Lolth's webs. The syntax is completely tangled.":
            'La tua richiesta è rimasta impigliata nelle ragnatele di Lolth. La sintassi è tutta aggrovigliata.',
        'Velkynvelve Prisoner': 'Prigioniero di Velkynvelve',
        "Escaped slaves don't have access rights here. The Drow priestesses demand your surrender.":
            'Gli schiavi fuggiti non hanno diritti di accesso qui. Le sacerdotesse Drow esigono la tua resa.',
        'Illithid Enclave': 'Enclave Illithid',
        'The Elder Brain rejects your mind. Your psionic clearance level is insufficient.':
            'Il Cervello Antico respinge la tua mente. Il tuo livello di autorizzazione psionica è insufficiente.',
        'Swallowed by the Dark': 'Inghiottito dal Buio',
        'The page you seek has been consumed by the endless abyss of the Underdark.':
            "La pagina che cerchi è stata divorata dall'abisso senza fine del Sottosuolo.",
        'Descending Madness': 'Follia Discendente',
        'The madness of the Abyss is compounding too quickly. Take a long rest.':
            "La follia dell'Abisso si accumula troppo in fretta. Fai un riposo lungo.",
        'Mind Flayer Blast': 'Scarica del Mind Flayer',
        'An Illithid psychic blast just stunned our backend processes. Rebooting...':
            'Una scarica psichica Illithid ha appena stordito i nostri processi di backend. Riavvio in corso...',

        # ===== D&D: Icewind Dale: Rime of the Frostmaiden =====
        'Frostbitten Fingers': 'Dita Congelate',
        'Your hands were shaking too much from the cold to type the URL correctly.':
            'Le tue mani tremavano troppo dal freddo per digitare correttamente l\'URL.',
        "Auril's Test": 'La Prova di Auril',
        'The Frostmaiden requires a sacrifice of warmth before she grants you passage.':
            'La Vergine del Gelo esige un sacrificio di calore prima di concederti il passaggio.',
        'Ythryn Quarantine': 'Quarantena di Ythryn',
        'The ancient Netherese city is on magical lockdown to prevent the spread of arcane blight.':
            "L'antica città netherese è in isolamento magico per impedire il diffondersi della piaga arcana.",
        'Whiteout Condition': 'Condizioni di Whiteout',
        'The blizzard is too thick! The page you are looking for is completely buried in snow.':
            'La bufera è troppo fitta! La pagina che cerchi è completamente sepolta dalla neve.',
        'Biting Winds': 'Venti Pungenti',
        "You're pushing into the blizzard too fast. Stop and build a fire before you freeze to death.":
            'Ti stai spingendo nella bufera troppo in fretta. Fermati e accendi un fuoco prima di morire assiderato.',
        'Everlasting Rime': 'Brina Eterna',
        "Auril's spell just froze the entire backend infrastructure solid.":
            "L'incantesimo di Auril ha appena congelato di colpo l'intera infrastruttura di backend.",

        # ===== D&D: The Wild Beyond the Witchlight =====
        'Muddled Wish': 'Desiderio Confuso',
        'You phrased your wish carelessly and the carnival misheard it. Try asking again, more sweetly.':
            'Hai formulato il desiderio con leggerezza e il luna park ha frainteso. Prova a chiederlo di nuovo, più dolcemente.',
        'No Carnival Ticket': 'Nessun Biglietto del Luna Park',
        'You have no ticket to the Witchlight. The barkers turn you away from the gates.':
            'Non hai il biglietto per il Witchlight. Gli imbonitori ti allontanano dai cancelli.',
        'Hourglass Coven': 'Congrega della Clessidra',
        'The Hourglass has forbidden this path. Its hags do not care to let you wander here.':
            'La Clessidra ha proibito questo sentiero. Le sue megere non hanno voglia di lasciarti vagare qui.',
        'Lost in the Feywild': 'Perso nel Reame Fatato',
        'The path folded away like a dream. What you sought drifted off into the endless carnival.':
            'Il sentiero si è ripiegato come un sogno. Ciò che cercavi si è disperso nel luna park senza fine.',
        'Too Much Wonder': 'Troppa Meraviglia',
        'You are rushing the marvels too fast. The Feywild spins -- take a breath and wander slower.':
            'Stai divorando le meraviglie troppo in fretta. Il Reame Fatato gira — respira e vaga più piano.',
        'Carnival Collapse': 'Crollo del Luna Park',
        'The whole carnival winked out at once. The fey are stitching the dream back together.':
            "L'intero luna park si è spento di colpo. I folletti stanno ricucendo il sogno.",

        # ===== D&D: Candlekeep Mysteries =====
        'Smudged Ink': 'Inchiostro Sbavato',
        'Your query blotted across the page. The scribes cannot read a request written so carelessly.':
            'La tua richiesta si è sbavata sulla pagina. Gli scribi non riescono a leggere una richiesta scritta con tanta sciatteria.',
        'No Gift of Knowledge': 'Nessun Dono di Conoscenza',
        'Candlekeep admits only those who bring a book it lacks. You have brought nothing new.':
            'Candlekeep ammette solo chi porta un libro che le manca. Tu non hai portato nulla di nuovo.',
        'Restricted Stacks': 'Scaffali Riservati',
        'These shelves are sealed to visitors. Only the Avowed may walk the inner archives.':
            'Questi scaffali sono preclusi ai visitatori. Solo i Giurati possono percorrere gli archivi interni.',
        'Misfiled Tome': 'Tomo Mal Archiviato',
        'The book you seek is not on its shelf. Somewhere in a million volumes, it has been misplaced.':
            'Il libro che cerchi non è sul suo scaffale. Da qualche parte tra un milione di volumi, è stato smarrito.',
        'Reading Too Fast': 'Lettura Troppo Veloce',
        'You are pulling tomes faster than the Avowed can reshelve them. Slow down and let the dust settle.':
            'Stai tirando giù tomi più in fretta di quanto i Giurati riescano a riporli. Rallenta e lascia posare la polvere.',
        'Archive Ablaze': 'Archivio in Fiamme',
        'A candle tipped onto the manuscripts. The Avowed are fighting the flames while the archive recovers.':
            'Una candela si è rovesciata sui manoscritti. I Giurati stanno combattendo le fiamme mentre l\'archivio si riprende.',

        # ===== D&D: Tasha's Cauldron of Everything =====
        'Potion Explosion': 'Esplosione di Pozione',
        'You mixed the wrong ingredients in the cauldron. The request blew up in your face.':
            'Hai mescolato gli ingredienti sbagliati nel calderone. La richiesta ti è esplosa in faccia.',
        'Mirror of Identification': 'Specchio dell\'Identificazione',
        "The magic mirror doesn't recognize your reflection. Please log in.":
            'Lo specchio magico non riconosce il tuo riflesso. Accedi, per favore.',
        "Tasha's Diary": 'Il Diario di Tasha',
        "These are Iggwilv's private notes! A potent warding glyph prevents you from reading them.":
            'Questi sono gli appunti privati di Iggwilv! Un potente glifo protettivo ti impedisce di leggerli.',
        'Rabbit Gone': 'Il Coniglio è Sparito',
        "You reached into the magic hat, but there's absolutely nothing in there.":
            'Hai infilato la mano nel cilindro magico, ma lì dentro non c\'è assolutamente nulla.',
        'Scroll Burnout': 'Pergamene fino allo Sfinimento',
        'Reading that many scrolls at once is frying your retinas. Take a short rest.':
            'Leggere così tante pergamene tutte insieme ti sta friggendo le retine. Fai un riposo breve.',
        'Wild Magic Cascade': 'Cascata di Magia Selvaggia',
        'We rolled a 1 on the wild magic surge table. We are currently all potted plants.':
            'Abbiamo tirato un 1 sulla tabella della magia selvaggia. Al momento siamo tutti piante in vaso.',

        # ===== D&D: Xanathar's Guide to Everything =====
        'Loaded Dice': 'Dadi Truccati',
        'We detected an invalid roll in your request parameters. No cheating in the tavern!':
            'Abbiamo rilevato un tiro non valido nei parametri della tua richiesta. Niente imbrogli in taverna!',
        "Thieves' Cant Failed": 'Gergo Ladresco Fallito',
        "You don't know the secret slang. The rogue at the door won't let you in.":
            'Non conosci il gergo segreto. Il furfante alla porta non ti fa entrare.',
        'Blacklisted': 'Sulla Lista Nera',
        "You've been marked by the Zhentarim. You are permanently forbidden from this endpoint.":
            'Sei stato marchiato dagli Zhentarim. Ti è vietato in modo permanente questo endpoint.',
        'Disintegrated': 'Disintegrato',
        "A disintegration ray just vaporized the page you were looking for. There's only a pile of dust left.":
            'Un raggio di disintegrazione ha appena vaporizzato la pagina che cercavi. È rimasto solo un mucchietto di polvere.',
        'Coin Jam': 'Ingorgo di Monete',
        "You're throwing bribes at the guards too quickly. Let them count the gold first!":
            'Stai lanciando tangenti alle guardie troppo in fretta. Lascia prima che contino l\'oro!',
        'Beholder Dream': 'Sogno di Beholder',
        'Xanathar fell asleep and dreamed of a rogue server process, spawning a catastrophic anomaly!':
            'Xanathar si è addormentato e ha sognato un processo canaglia del server, generando un\'anomalia catastrofica!',

        # ===== D&D: Vecna: Eve of Ruin =====
        'Mispronounced Secret': 'Segreto Pronunciato Male',
        'You whispered the wrong dark secret into the void. The cosmos rejects your request.':
            'Hai sussurrato nel vuoto il segreto oscuro sbagliato. Il cosmo respinge la tua richiesta.',
        'Cult Interception': 'Intercettazione del Culto',
        'The cultists of the Whispered One demand the hidden password.':
            'I cultisti del Sussurrato esigono la password nascosta.',
        'Sigil Denied': 'Sigil Negata',
        'The Lady of Pain has barred the doors to this portal. Do not push your luck.':
            'La Dama del Dolore ha sbarrato le porte di questo portale. Non tentare la sorte.',
        'Lost in the Astral Sea': 'Perso nel Mare Astrale',
        'Your connection drifted off the silver cord and vanished into the void.':
            'La tua connessione è scivolata via dal cordone d\'argento ed è svanita nel vuoto.',
        'Time Paradox': 'Paradosso Temporale',
        'You are sending requests faster than time flows. Please wait for causality to catch up.':
            'Stai inviando richieste più in fretta di quanto scorra il tempo. Attendi che la causalità ti raggiunga.',
        'Reality Unraveling': 'La Realtà si Disfa',
        "The Weave of magic is tearing apart! Vecna's ritual is crashing the entire multiverse.":
            'La Trama della magia si sta lacerando! Il rituale di Vecna sta mandando in crash l\'intero multiverso.',

        # ===== D&D: Mythic Odysseys of Theros =====
        'Rejected Offering': 'Offerta Rifiutata',
        'Your offering displeased the gods. The malformed rite was cast back down from Nyx.':
            'La tua offerta ha dispiaciuto agli dèi. Il rito malformato è stato ricacciato giù da Nyx.',
        "Without the Gods' Favour": 'Senza il Favore degli Dèi',
        'No deity vouches for you. The temple guardians will not grant passage to the unfavoured.':
            'Nessuna divinità garantisce per te. I guardiani del tempio non concedono il passaggio a chi è privo di favore.',
        'Sealed Temple': 'Tempio Sigillato',
        'This sanctum is closed to mortals. Only a hero of legend may cross its marble threshold.':
            'Questo santuario è chiuso ai mortali. Solo un eroe leggendario può varcarne la soglia di marmo.',
        'Lost to Nyx': 'Perduto in Nyx',
        'The path dissolved into the starfield. What you sought has drifted into the night sky of Nyx.':
            'Il sentiero si è dissolto nel campo stellato. Ciò che cercavi è andato alla deriva nel cielo notturno di Nyx.',
        'Hubris': 'Hybris',
        'You demand too much, too fast -- the gods call it hubris. Temper your pride before they notice.':
            'Pretendi troppo, troppo in fretta — gli dèi la chiamano hybris. Modera il tuo orgoglio prima che se ne accorgano.',
        'Wrath of the Gods': 'Ira degli Dèi',
        'A god took offence and hurled a thunderbolt through the server. The oracles are restoring the mortal realm.':
            'Un dio si è offeso e ha scagliato un fulmine attraverso il server. Gli oracoli stanno ripristinando il regno mortale.',

        # ===== Other Universes: Vintage Arcade =====
        'Button Mash Error': 'Errore da Pigia-Pulsanti',
        "You hit A, B, X, Y, and Start all at once. The console didn't understand that combo.":
            'Hai premuto A, B, X, Y e Start tutti insieme. La console non ha capito quella combo.',
        'Insert Coin': 'Inserisci Gettone',
        'CREDITS: 0. You must insert a token to continue to this screen.':
            'CREDITI: 0. Devi inserire un gettone per proseguire a questa schermata.',
        'High Score Board Only': 'Solo Classifica dei Record',
        'You must beat the top score of "AAA" to view this secret level.':
            'Devi battere il punteggio record di "AAA" per vedere questo livello segreto.',
        'Missing ROM': 'ROM Mancante',
        '404_FILE_MISSING. The floppy disk containing this data seems to be corrupted.':
            '404_FILE_MISSING. Il floppy disk che contiene questi dati sembra corrotto.',
        'Chill Out, Player 1': 'Calma, Player 1',
        'The CPU is overheating from your frantic inputs. Pause the game for a second.':
            'La CPU si sta surriscaldando per i tuoi input frenetici. Metti in pausa il gioco per un secondo.',
        'Someone Tripped on the Cord': 'Qualcuno ha Inciampato sul Cavo',
        'The power cable got yanked out of the wall. Everything is gone.':
            'Il cavo di alimentazione è stato strappato dalla presa. È sparito tutto.',

        # ===== Other Universes: Military Terminal =====
        'INVALID_PROTOCOL': 'INVALID_PROTOCOL',
        'You used a civilian handshake for a military endpoint. Request rejected.':
            'Hai usato un handshake civile per un endpoint militare. Richiesta respinta.',
        'Authentication Timeout': 'Timeout di Autenticazione',
        'Your session in the war room has expired. Log in again, soldier.':
            'La tua sessione nella sala operativa è scaduta. Accedi di nuovo, soldato.',
        'Executive Lockout': 'Blocco Esecutivo',
        'The commander has sealed this terminal. Only a Five-Star General can bypass this block.':
            'Il comandante ha sigillato questo terminale. Solo un Generale a Cinque Stelle può aggirare questo blocco.',
        'DATA_EXPUNGED': 'DATA_EXPUNGED',
        'The file you are looking for has been heavily redacted and removed from the archives. That operation never existed. And if you keep asking about it, neither will you.':
            'Il file che cerchi è stato pesantemente censurato e rimosso dagli archivi. Quell\'operazione non è mai esistita. E se continui a chiederne, presto non esisterai nemmeno tu.',
        'DDoS Detected': 'DDoS Rilevato',
        'Incoming traffic exceeds radar capabilities. Initiating packet-dropping countermeasures.':
            'Il traffico in arrivo supera le capacità del radar. Avvio contromisure di scarto pacchetti.',
        'Satellite Uplink Lost': 'Collegamento Satellitare Perso',
        'A solar flare just destroyed our orbital relay. The internal network is totally dark.':
            'Un brillamento solare ha appena distrutto il nostro ripetitore orbitale. La rete interna è completamente al buio.',

        # ===== Other Universes: Analog Archive (Paperwork & Office Files) =====
        'Illegible Handwriting': 'Grafia Illeggibile',
        'We tried to process your file, but your cursive is unreadable. Please fill out a new form in block letters.':
            'Abbiamo provato a processare la tua pratica, ma il tuo corsivo è illeggibile. Compila un nuovo modulo in stampatello.',
        'Show Your Badge': 'Mostra il Tesserino',
        'The clerk refuses to take your folder. You need to show a valid company ID to the front desk first.':
            "L'impiegato si rifiuta di prendere la tua cartella. Devi prima mostrare un badge aziendale valido alla reception.",
        'Locked Cabinet': 'Schedario Chiuso a Chiave',
        'You are trying to pry open a locked filing drawer. You do not hold the key for this specific archive.':
            'Stai cercando di forzare un cassetto dello schedario chiuso. Non hai la chiave di questo specifico archivio.',
        'Shredded Paper': 'Carta Tritata',
        'The file you are looking for has been sent to the industrial shredder. There are only thin paper ribbons left.':
            'La pratica che cerchi è stata mandata al distruggidocumenti industriale. Sono rimaste solo sottili striscioline di carta.',
        'Overworked Clerk': 'Impiegato Oberato',
        'The archivist can only stamp documents so fast! Give them a moment to catch up with your massive stack of requests.':
            "L'archivista può timbrare i documenti solo a una certa velocità! Dagli un momento per smaltire la tua enorme pila di richieste.",
        'Archive Fire': 'Incendio in Archivio',
        'Someone left a cigarette burning on a stack of old reports. The back office is currently dealing with a chaotic emergency.':
            'Qualcuno ha lasciato una sigaretta accesa su una pila di vecchi rapporti. Il retro ufficio sta gestendo un\'emergenza caotica.',

        # ===== Other Universes: Holo HUD =====
        'Malformed Packet': 'Pacchetto Malformato',
        'The data stream failed checksum. Your request packet was rejected by the input parser.':
            'Il flusso di dati non ha superato il checksum. Il pacchetto della tua richiesta è stato respinto dal parser di input.',
        'Biometric Mismatch': 'Mancata Corrispondenza Biometrica',
        'Identity not recognised. This terminal requires a valid access signature before it will respond.':
            'Identità non riconosciuta. Questo terminale richiede una firma di accesso valida prima di rispondere.',
        'Clearance Denied': 'Autorizzazione Negata',
        'Your access level is insufficient for this sector. The system has logged the attempt.':
            'Il tuo livello di accesso è insufficiente per questo settore. Il sistema ha registrato il tentativo.',
        'Signal Lost': 'Segnale Perso',
        'No telemetry at these coordinates. The node you are querying is offline or was never mapped.':
            'Nessuna telemetria a queste coordinate. Il nodo che stai interrogando è offline o non è mai stato mappato.',
        'Bandwidth Exceeded': 'Banda Superata',
        'Input rate over threshold. Throttling engaged -- wait for the buffer to clear before transmitting again.':
            'Frequenza di input oltre soglia. Limitazione attivata — attendi che il buffer si svuoti prima di ritrasmettere.',
        'Core Fault': 'Guasto del Nucleo',
        'A critical exception cascaded through the main core. Automatic recovery routines are re-initialising the system.':
            'Un\'eccezione critica si è propagata nel nucleo principale. Le routine di ripristino automatico stanno reinizializzando il sistema.',

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