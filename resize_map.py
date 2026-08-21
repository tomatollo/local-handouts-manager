# -*- coding: utf-8 -*-
"""Ridimensiona un PNG di mappa per alleggerire la generazione dei composite.

PERCHE'
-------
Il composite fog-of-war (handouts/mapmask.build_composite) viene ricalcolato ad
ogni reveal: carica il PNG intero, disegna la maschera esagono per esagono su un
canvas grande quanto l'immagine, e salva. Tutto questo lavoro scala con l'AREA in
pixel del PNG sorgente. Una mappa da molti MB / molti megapixel rende ogni
ricostruzione lenta, e sotto il polling di piu' giocatori questo satura i thread
del server (le pagine "non caricano" finche' non si riavvia).

Ridurre la risoluzione del PNG sorgente e' la leva singola piu' efficace: dimezzare
il lato lungo = circa un quarto del lavoro per ogni ricostruzione.

SICUREZZA DELLA GRIGLIA
-----------------------
La geometria della griglia (hex_size, offset_x, offset_y) e' salvata in
PERCENTUALE dell'immagine, non in pixel -> la calibrazione resta valida a
qualunque risoluzione. Ridimensionare non sposta la griglia.

COSA FA QUESTO SCRIPT
---------------------
- NON sovrascrive nulla: crea una copia "<nome>.resized.png" a fianco.
- Stampa dimensioni e peso prima/dopo, cosi' decidi tu se tenerla.

COME USARLO
-----------
1) Con la venv attiva:  .venv\\Scripts\\python resize_map.py
   (oppure passa un nome file:  python resize_map.py map_1785788892.png)
2) Apri la copia .resized.png e controlla che il dettaglio regga lo zoom.
3) Se ti va bene, SOSTITUISCI l'originale mantenendo lo STESSO nome file
   (il nome e' registrato in data/database.json come map_image):
     - fai un backup del vecchio (rinominalo .orig.png), poi
     - rinomina la .resized.png col nome originale.
4) Svuota la cache dei composite: cancella il contenuto di data/map_cache
   (sono calcolati sulla vecchia risoluzione; si rigenerano da soli).
"""

import os
import sys

import fitz  # PyMuPDF: gia' tra le dipendenze del progetto
from PIL import Image

# Import dello stesso modulo storage dell'app, cosi' MAP_DIR e' identico a
# quello che usa il server (nessun path hard-coded che potrebbe divergere).
from handouts import storage

# Lato lungo target in pixel. 3500 e' un buon compromesso per una mappa da
# tavolo: nitida allo zoom ma molto piu' leggera. Abbassa per alleggerire
# ancora, alza se ti serve piu' dettaglio.
MAX_LONG_SIDE = 3500

# Livello di compressione del PNG in uscita: 6 e' un buon equilibrio
# dimensione/tempo per un'operazione una-tantum come questa (non e' il percorso
# caldo del server, quindi qui va bene comprimere di piu' che in mapmask).
OUT_COMPRESS_LEVEL = 6


def pick_map_filename():
    """Nome del PNG da ridimensionare: argomento CLI, o l'unico file in maps/,
    altrimenti chiede di specificarlo."""
    if len(sys.argv) > 1:
        return os.path.basename(sys.argv[1])
    pngs = [f for f in os.listdir(storage.MAP_DIR)
            if f.lower().endswith('.png')]
    if len(pngs) == 1:
        return pngs[0]
    print("Trovati piu' PNG in", storage.MAP_DIR)
    for f in pngs:
        print("  -", f)
    print("Rilancia indicando il file, es:  python resize_map.py",
          pngs[0] if pngs else "<nome>.png")
    sys.exit(1)


def main():
    name = pick_map_filename()
    src = os.path.join(storage.MAP_DIR, name)
    if not os.path.exists(src):
        print("File non trovato:", src)
        sys.exit(1)

    # Carico via fitz (stesso backend di mapmask) e normalizzo a RGB.
    pix = fitz.Pixmap(src)
    if pix.n not in (3, 4) or pix.colorspace is None:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    mode = 'RGBA' if pix.alpha else 'RGB'
    img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
    img = img.convert('RGB')

    w, h = img.size
    src_mb = os.path.getsize(src) / 1e6
    print(f"Originale: {w}x{h}px, {src_mb:.1f} MB  ({name})")

    scale = MAX_LONG_SIDE / max(w, h)
    if scale >= 1:
        print(f"Il lato lungo e' gia' <= {MAX_LONG_SIDE}px: niente da ridurre.")
        print("Se vuoi comunque una copia piu' compressa, abbassa MAX_LONG_SIDE.")
        return

    new_size = (round(w * scale), round(h * scale))
    resized = img.resize(new_size, Image.LANCZOS)

    stem, ext = os.path.splitext(name)
    out_name = f"{stem}.resized{ext}"
    out = os.path.join(storage.MAP_DIR, out_name)
    resized.save(out, 'PNG', compress_level=OUT_COMPRESS_LEVEL)

    out_mb = os.path.getsize(out) / 1e6
    print(f"Ridotta:   {new_size[0]}x{new_size[1]}px, {out_mb:.1f} MB")
    print(f"           -> {out}")
    print()
    print("Controlla la copia. Se ti va bene, sostituisci l'originale tenendo")
    print(f"lo stesso nome ({name}) e svuota data/map_cache. Dettagli nel")
    print("commento in cima a questo script.")


if __name__ == '__main__':
    main()
