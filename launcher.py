# -*- coding: utf-8 -*-
"""
Local Handouts Manager - Server Launcher
=========================================
A lightweight desktop GUI (tkinter, standard library) to start and stop the
Flask server without touching the command line.

How it works, briefly
----------------------
- The server does NOT run inside this GUI. It is launched as a separate CHILD
  PROCESS via `waitress` (a WSGI server suited to long sessions). This gives:
  a clean stop (just terminate the child), isolation from crashes, and logs
  captured over a pipe.
- On Windows the child is started WITHOUT a console window (CREATE_NO_WINDOW),
  so starting the server does not pop up a second black terminal.
- The GUI stays event-driven: no busy polling. The log is drained via
  root.after(), and the /ping check runs ONLY while the server is up.

Features
--------
- Start / Stop with an always-visible status.
- Custom host / port, with defaults and a "Reset to defaults" button.
- Interface language switch (English / Italian).
- Light / dark appearance toggle.
- LAN IP shown in clear (the address to give players).
- Open Player / Master / QR in the browser; copy the player URL.
- Mini log (last lines only, capped).
- "Start on open" option.
- "Server responds" indicator (light /ping while running).
- Reset the Master passphrase (with confirmation), in case it is forgotten.

Requirements in the project venv:
    pip install waitress

Run:
    (with the venv active)  pythonw launcher.py
    or use the start_launcher.bat file.
"""

import json
import os
import queue
import socket
import subprocess
import sys
import threading
import tkinter as tk
import urllib.request
import webbrowser
from tkinter import messagebox, ttk

# ---------------------------------------------------------------------------
# CONFIGURATION - values you may want to change are grouped here
# ---------------------------------------------------------------------------

# Default host/port ("Reset to defaults" restores these).
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

# WSGI callable exposed by the app: app.py already defines `app = create_app()`
# at module level, so "app:app" works WITHOUT changing that code.
WSGI_TARGET = "app:app"

# Browser-button paths. Correct these if your routes differ.
PATH_PLAYER = "/"           # player home
PATH_MASTER = "/dm-panel"   # master dashboard
PATH_QR = "/qr"             # QR page
PATH_PING = "/ping"         # lightweight liveness endpoint (returns 204)

# Relative path (from this launcher) to the JSON database, used by the
# passphrase reset. Matches handouts/storage.py: data/database.json.
DB_RELPATH = os.path.join("data", "database.json")
# Key under settings that holds the master passphrase hash (see auth.py).
PASSPHRASE_KEY = "master_passphrase_hash"

# /ping cadence (ms) while the server is up. No pinging while it is stopped.
PING_INTERVAL_MS = 5000

# How often (ms) the GUI drains the log queue (memory read, not a network poll).
LOG_DRAIN_INTERVAL_MS = 200

# Max lines kept in the mini log: constant memory.
MAX_LOG_LINES = 200

CONFIG_FILENAME = "launcher_config.json"

# Directory holding this launcher (assumed to be the project root, next to
# app.py).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, CONFIG_FILENAME)


# ---------------------------------------------------------------------------
# Internationalisation (English / Italian)
# ---------------------------------------------------------------------------
# A tiny in-file dictionary. Keys are stable identifiers; each maps to the two
# languages. tr() looks the active language up and falls back to the key so a
# missing string is visible rather than blank.

LANGUAGES = ("en", "it")

STRINGS = {
    "window_title": {"en": "Local Handouts Manager - Launcher",
                     "it": "Local Handouts Manager - Launcher"},
    "server_status": {"en": "Server status", "it": "Stato del server"},
    "running": {"en": "RUNNING", "it": "IN ESECUZIONE"},
    "stopped": {"en": "STOPPED", "it": "FERMO"},
    "responds": {"en": "responds", "it": "risponde"},
    "no_response": {"en": "no response", "it": "non risponde"},
    "config": {"en": "Configuration", "it": "Configurazione"},
    "host": {"en": "Host (IP):", "it": "Host (IP):"},
    "port": {"en": "Port:", "it": "Porta:"},
    "reset_defaults": {"en": "Reset to defaults", "it": "Reimposta ai default"},
    "lan_ip": {"en": "Local network IP (for players):",
               "it": "IP di rete locale (per i giocatori):"},
    "start_on_open": {"en": "Start the server on open",
                      "it": "Avvia il server all'apertura"},
    "start": {"en": "Start server", "it": "Avvia server"},
    "stop": {"en": "Stop server", "it": "Ferma server"},
    "links": {"en": "Links", "it": "Collegamenti"},
    "open_player": {"en": "Open Player", "it": "Apri Player"},
    "open_master": {"en": "Open Master", "it": "Apri Master"},
    "open_qr": {"en": "Open QR", "it": "Apri QR"},
    "copy_player_url": {"en": "Copy player URL", "it": "Copia URL giocatori"},
    "log": {"en": "Server log (last lines)", "it": "Log del server (ultime righe)"},
    "language": {"en": "Language", "it": "Lingua"},
    "appearance": {"en": "Appearance", "it": "Aspetto"},
    "dark": {"en": "Dark", "it": "Scuro"},
    "light": {"en": "Light", "it": "Chiaro"},
    "maintenance": {"en": "Maintenance", "it": "Manutenzione"},
    "reset_passphrase": {"en": "Reset master passphrase",
                         "it": "Reimposta passphrase master"},

    # Messages / dialogs
    "invalid_host_title": {"en": "Invalid host", "it": "Host non valido"},
    "invalid_host_msg": {"en": "'{host}' is not a valid host.",
                         "it": "'{host}' non e' un host valido."},
    "invalid_port_title": {"en": "Invalid port", "it": "Porta non valida"},
    "invalid_port_msg": {"en": "The port must be a number.",
                         "it": "La porta deve essere un numero."},
    "port_range_title": {"en": "Port out of range", "it": "Porta fuori range"},
    "port_range_msg": {"en": "The port must be between 1024 and 65535.",
                       "it": "La porta deve essere tra 1024 e 65535."},
    "port_busy_title": {"en": "Port in use", "it": "Porta occupata"},
    "port_busy_msg": {
        "en": "Port {port} appears to be in use already.\n"
              "Choose another port or close the app using it.",
        "it": "La porta {port} risulta gia' in uso.\n"
              "Scegli un'altra porta o chiudi l'applicazione che la occupa."},
    "started_msg": {"en": "Server started on {host}:{port}",
                    "it": "Server avviato su {host}:{port}"},
    "already_running": {"en": "The server is already running.",
                        "it": "Il server e' gia' in esecuzione."},
    "not_running": {"en": "The server is not running.",
                    "it": "Il server non e' in esecuzione."},
    "start_failed": {"en": "Start failed: {err}", "it": "Avvio fallito: {err}"},
    "stopped_msg": {"en": "Server stopped.", "it": "Server fermato."},
    "stop_error": {"en": "Error while stopping: {err}",
                   "it": "Errore durante lo stop: {err}"},
    "server_ended": {"en": "[server ended]", "it": "[server terminato]"},
    "url_copied": {"en": "URL copied: {url}", "it": "URL copiato: {url}"},
    "close_running_title": {"en": "Server running", "it": "Server attivo"},
    "close_running_msg": {
        "en": "The server is still running.\nStop it and close the launcher?",
        "it": "Il server e' ancora in esecuzione.\nVuoi fermarlo e chiudere il launcher?"},

    # Passphrase reset flow (two confirmations, since it is destructive-ish).
    "reset_pp_confirm1_title": {"en": "Reset passphrase?",
                                "it": "Reimpostare la passphrase?"},
    "reset_pp_confirm1_msg": {
        "en": "This removes the current Master passphrase. The Master side "
              "will be open to anyone on the network until a new passphrase "
              "is set.\n\nContinue?",
        "it": "Questo rimuove l'attuale passphrase del Master. Il lato Master "
              "sara' aperto a chiunque sulla rete finche' non ne imposti una "
              "nuova.\n\nContinuare?"},
    "reset_pp_confirm2_title": {"en": "Are you sure?", "it": "Sei sicuro?"},
    "reset_pp_confirm2_msg": {
        "en": "Final confirmation: really clear the Master passphrase now?",
        "it": "Conferma finale: cancellare davvero la passphrase del Master adesso?"},
    "reset_pp_running_title": {"en": "Stop the server first",
                               "it": "Ferma prima il server"},
    "reset_pp_running_msg": {
        "en": "Please stop the server before resetting the passphrase, so the "
              "change is read cleanly on the next start.",
        "it": "Ferma il server prima di reimpostare la passphrase, cosi' la "
              "modifica viene letta correttamente al prossimo avvio."},
    "reset_pp_done_title": {"en": "Passphrase reset", "it": "Passphrase reimpostata"},
    "reset_pp_done_msg": {
        "en": "The Master passphrase has been cleared. Set a new one from the "
              "Master side (Master Access) after starting the server.",
        "it": "La passphrase del Master e' stata cancellata. Impostane una nuova "
              "dal lato Master (Accesso Master) dopo aver avviato il server."},
    "reset_pp_none_title": {"en": "Nothing to reset", "it": "Niente da reimpostare"},
    "reset_pp_none_msg": {
        "en": "No passphrase is currently set.",
        "it": "Nessuna passphrase risulta impostata."},
    "reset_pp_error_title": {"en": "Reset failed", "it": "Reimpostazione fallita"},
    "reset_pp_error_msg": {
        "en": "Could not update the database:\n{err}",
        "it": "Impossibile aggiornare il database:\n{err}"},
    "reset_pp_nodb_msg": {
        "en": "Database file not found at:\n{path}",
        "it": "File database non trovato in:\n{path}"},
}


def tr(key, lang, **kwargs):
    """Translate `key` into `lang`, formatting with any kwargs.

    Falls back to English, then to the raw key, so nothing renders blank.
    """
    entry = STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("en") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


# ---------------------------------------------------------------------------
# Appearance palettes (light / dark). ttk needs explicit colours to actually
# look dark; we keep two small palettes and repaint on toggle.
# ---------------------------------------------------------------------------

PALETTES = {
    "dark": {
        "bg": "#1e1b18",
        "panel": "#2a2320",
        "fg": "#f0e6d6",
        "fg_dim": "#b9a78d",
        "entry_bg": "#141110",
        "accent": "#e8a83a",
        "running": "#5bb060",
        "stopped": "#e0685f",
        "log_bg": "#141110",
        "log_fg": "#d8ccb8",
    },
    "light": {
        "bg": "#f2efe9",
        "panel": "#ffffff",
        "fg": "#1e1b18",
        "fg_dim": "#6b5f4f",
        "entry_bg": "#ffffff",
        "accent": "#a5731a",
        "running": "#1a7f37",
        "stopped": "#a40e26",
        "log_bg": "#ffffff",
        "log_fg": "#1e1b18",
    },
}


# ---------------------------------------------------------------------------
# Network / environment helpers
# ---------------------------------------------------------------------------

def detect_lan_ip():
    """Detect the machine's 'visitable' LAN IP (e.g. 192.168.x.x).

    Opens a UDP socket toward an external IP (nothing is actually sent) and
    reads the local address the OS picked. No real traffic.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def find_python_executable():
    """Interpreter to run the child with.

    Prefer the project venv (Windows: .venv\\Scripts\\pythonw.exe -- the 'w'
    variant has no console), then POSIX venv, then whatever runs this launcher.
    Using pythonw is part of keeping a stray terminal from appearing.
    """
    venv_pyw = os.path.join(BASE_DIR, ".venv", "Scripts", "pythonw.exe")
    if os.path.exists(venv_pyw):
        return venv_pyw
    venv_py = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_py):
        return venv_py
    venv_py_posix = os.path.join(BASE_DIR, ".venv", "bin", "python")
    if os.path.exists(venv_py_posix):
        return venv_py_posix
    return sys.executable


def port_is_free(host, port):
    """True if the port is free on host. Tests 127.0.0.1 when host is 0.0.0.0."""
    test_host = "127.0.0.1" if host in ("0.0.0.0", "") else host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((test_host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def validate_host(host):
    """Accept 0.0.0.0, localhost/127.0.0.1, or a syntactically valid IPv4."""
    host = host.strip()
    if host in ("0.0.0.0", "localhost", "127.0.0.1"):
        return True
    try:
        socket.inet_aton(host)
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Config persistence (host/port/options, incl. language + theme)
# ---------------------------------------------------------------------------

def load_config():
    """Load config from JSON; return defaults if missing/corrupt."""
    defaults = {
        "host": DEFAULT_HOST,
        "port": DEFAULT_PORT,
        "autostart": False,
        "lang": "en",
        "theme": "dark",
    }
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in defaults:
            if k in data:
                defaults[k] = data[k]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    # Guard against junk values for the enumerated settings.
    if defaults["lang"] not in LANGUAGES:
        defaults["lang"] = "en"
    if defaults["theme"] not in PALETTES:
        defaults["theme"] = "dark"
    return defaults


def save_config(cfg):
    """Save config to JSON (best-effort; never crash the GUI over it)."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Server controller: wraps the child process lifecycle
# ---------------------------------------------------------------------------

class ServerController:
    """Start/stop the Flask server as a child process (waitress).

    A reader thread drains the child's stdout/stderr into a thread-safe queue
    the GUI reads, so the GUI never touches shared state directly.
    """

    def __init__(self, log_queue):
        self.proc = None
        self.reader_thread = None
        self.log_queue = log_queue

    def is_running(self):
        return self.proc is not None and self.proc.poll() is None

    def start(self, host, port):
        """Launch waitress in a child process. Returns (ok, message_key, kwargs)."""
        if self.is_running():
            return False, "already_running", {}

        python_exe = find_python_executable()
        cmd = [
            python_exe, "-u",           # unbuffered -> live logs
            "-m", "waitress",
            "--host", host,
            "--port", str(port),
            WSGI_TARGET,
        ]

        # Windows: new process group (clean CTRL_BREAK stop) AND no console
        # window (so no stray black terminal appears when starting the server).
        creationflags = 0
        if os.name == "nt":
            creationflags = (subprocess.CREATE_NEW_PROCESS_GROUP
                             | subprocess.CREATE_NO_WINDOW)

        try:
            self.proc = subprocess.Popen(
                cmd,
                cwd=BASE_DIR,                 # so "app:app" imports
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=creationflags,
            )
        except Exception as e:
            self.proc = None
            return False, "start_failed", {"err": e}

        self.reader_thread = threading.Thread(
            target=self._drain_output, daemon=True)
        self.reader_thread.start()
        return True, "started_msg", {"host": host, "port": port}

    def _drain_output(self):
        if not self.proc or not self.proc.stdout:
            return
        for line in self.proc.stdout:
            self.log_queue.put(line.rstrip("\n"))
        self.log_queue.put("__ENDED__")   # sentinel, translated by the GUI

    def stop(self):
        """Stop cleanly, forcing a kill if it does not exit in time."""
        if not self.is_running():
            return False, "not_running", {}
        try:
            if os.name == "nt":
                self.proc.send_signal(subprocess.signal.CTRL_BREAK_EVENT)
            else:
                self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        except Exception as e:
            return False, "stop_error", {"err": e}
        finally:
            self.proc = None
        return True, "stopped_msg", {}


# ---------------------------------------------------------------------------
# Passphrase reset (edits the JSON DB directly, with confirmations in the GUI)
# ---------------------------------------------------------------------------

def clear_passphrase_in_db():
    """Remove the master passphrase hash from the DB file.

    Returns one of: 'ok', 'none' (no passphrase was set), 'nodb' (file
    missing), or ('error', message). Kept side-effect-only and free of any
    tkinter reference so the GUI owns all the dialogs.
    """
    db_path = os.path.join(BASE_DIR, DB_RELPATH)
    if not os.path.exists(db_path):
        return "nodb"
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return ("error", str(e))

    settings = db.get("settings", {})
    if not settings.get(PASSPHRASE_KEY):
        return "none"

    # Remove the key and write back, preserving everything else.
    settings.pop(PASSPHRASE_KEY, None)
    db["settings"] = settings
    try:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except OSError as e:
        return ("error", str(e))
    return "ok"


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.cfg = load_config()
        self.lang = self.cfg["lang"]
        self.theme = self.cfg["theme"]

        self.log_queue = queue.Queue()
        self.controller = ServerController(self.log_queue)
        self.lan_ip = detect_lan_ip()
        self._ping_job = None

        self.style = ttk.Style()
        # 'clam' honours custom colours far better than the native themes.
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self._build_ui()
        self._apply_language()
        self._apply_theme()
        self._refresh_status(running=False)

        self.root.after(LOG_DRAIN_INTERVAL_MS, self._drain_log_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        if self.cfg.get("autostart"):
            self.root.after(300, self.start_server)

    # ---- UI construction -------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}
        self.root.minsize(600, 620)

        # Top bar: language + appearance controls.
        top = ttk.Frame(self.root)
        top.pack(fill="x", **pad)
        self.lang_label = ttk.Label(top, text="")
        self.lang_label.pack(side="left", padx=(4, 4))
        self.lang_combo = ttk.Combobox(top, values=list(LANGUAGES), width=5,
                                       state="readonly")
        self.lang_combo.set(self.lang)
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_lang_change)

        self.theme_btn = ttk.Button(top, text="", command=self._toggle_theme)
        self.theme_btn.pack(side="right", padx=4)
        self.appearance_label = ttk.Label(top, text="")
        self.appearance_label.pack(side="right")

        # Status
        self.status_frame = ttk.LabelFrame(self.root, text="")
        self.status_frame.pack(fill="x", **pad)
        self.status_label = ttk.Label(self.status_frame, text="",
                                      font=("Segoe UI", 12, "bold"))
        self.status_label.pack(side="left", padx=8, pady=6)
        self.ping_label = ttk.Label(self.status_frame, text="")
        self.ping_label.pack(side="right", padx=8)

        # Configuration
        self.cfg_frame = ttk.LabelFrame(self.root, text="")
        self.cfg_frame.pack(fill="x", **pad)

        self.host_lbl = ttk.Label(self.cfg_frame, text="")
        self.host_lbl.grid(row=0, column=0, sticky="w", **pad)
        self.host_var = tk.StringVar(value=str(self.cfg["host"]))
        self.host_entry = ttk.Entry(self.cfg_frame, textvariable=self.host_var,
                                    width=18)
        self.host_entry.grid(row=0, column=1, sticky="w", **pad)

        self.port_lbl = ttk.Label(self.cfg_frame, text="")
        self.port_lbl.grid(row=0, column=2, sticky="w", **pad)
        self.port_var = tk.StringVar(value=str(self.cfg["port"]))
        self.port_entry = ttk.Entry(self.cfg_frame, textvariable=self.port_var,
                                    width=8)
        self.port_entry.grid(row=0, column=3, sticky="w", **pad)

        self.reset_btn = ttk.Button(self.cfg_frame, text="",
                                    command=self.reset_defaults)
        self.reset_btn.grid(row=0, column=4, **pad)

        self.lan_lbl = ttk.Label(self.cfg_frame, text="")
        self.lan_lbl.grid(row=1, column=0, columnspan=3, sticky="w", **pad)
        self.lan_value = ttk.Label(self.cfg_frame, text=self.lan_ip,
                                   font=("Segoe UI", 10, "bold"))
        self.lan_value.grid(row=1, column=3, columnspan=2, sticky="w", **pad)

        self.autostart_var = tk.BooleanVar(value=bool(self.cfg.get("autostart")))
        self.autostart_chk = ttk.Checkbutton(
            self.cfg_frame, text="", variable=self.autostart_var,
            command=self._persist)
        self.autostart_chk.grid(row=2, column=0, columnspan=4, sticky="w", **pad)

        # Commands
        btns = ttk.Frame(self.root)
        btns.pack(fill="x", **pad)
        self.start_btn = ttk.Button(btns, text="", command=self.start_server)
        self.start_btn.pack(side="left", padx=8)
        self.stop_btn = ttk.Button(btns, text="", command=self.stop_server)
        self.stop_btn.pack(side="left", padx=8)

        # Links
        self.link_frame = ttk.LabelFrame(self.root, text="")
        self.link_frame.pack(fill="x", **pad)
        self.player_btn = ttk.Button(
            self.link_frame, text="",
            command=lambda: self.open_in_browser(PATH_PLAYER))
        self.player_btn.pack(side="left", padx=6, pady=6)
        self.master_btn = ttk.Button(
            self.link_frame, text="",
            command=lambda: self.open_in_browser(PATH_MASTER))
        self.master_btn.pack(side="left", padx=6, pady=6)
        self.qr_btn = ttk.Button(
            self.link_frame, text="",
            command=lambda: self.open_in_browser(PATH_QR))
        self.qr_btn.pack(side="left", padx=6, pady=6)
        self.copy_btn = ttk.Button(self.link_frame, text="",
                                   command=self.copy_player_url)
        self.copy_btn.pack(side="right", padx=6, pady=6)

        # Maintenance (passphrase reset)
        self.maint_frame = ttk.LabelFrame(self.root, text="")
        self.maint_frame.pack(fill="x", **pad)
        self.reset_pp_btn = ttk.Button(self.maint_frame, text="",
                                       command=self.reset_passphrase)
        self.reset_pp_btn.pack(side="left", padx=6, pady=6)

        # Log
        self.log_frame = ttk.LabelFrame(self.root, text="")
        self.log_frame.pack(fill="both", expand=True, **pad)
        self.log_text = tk.Text(self.log_frame, height=10, wrap="word",
                                state="disabled", font=("Consolas", 9),
                                relief="flat", borderwidth=0)
        self.log_text.pack(side="left", fill="both", expand=True,
                           padx=(8, 0), pady=8)
        self.log_scroll = ttk.Scrollbar(self.log_frame,
                                        command=self.log_text.yview)
        self.log_scroll.pack(side="right", fill="y", pady=8)
        self.log_text.config(yscrollcommand=self.log_scroll.set)

    # ---- Language + theme ------------------------------------------------

    def _t(self, key, **kwargs):
        return tr(key, self.lang, **kwargs)

    def _apply_language(self):
        """(Re)label every widget in the current language."""
        self.root.title(self._t("window_title"))
        self.lang_label.config(text=self._t("language") + ":")
        self.appearance_label.config(text=self._t("appearance") + ":")
        self.theme_btn.config(
            text=self._t("light") if self.theme == "dark" else self._t("dark"))
        self.status_frame.config(text=self._t("server_status"))
        self.cfg_frame.config(text=self._t("config"))
        self.host_lbl.config(text=self._t("host"))
        self.port_lbl.config(text=self._t("port"))
        self.reset_btn.config(text=self._t("reset_defaults"))
        self.lan_lbl.config(text=self._t("lan_ip"))
        self.autostart_chk.config(text=self._t("start_on_open"))
        self.start_btn.config(text=self._t("start"))
        self.stop_btn.config(text=self._t("stop"))
        self.link_frame.config(text=self._t("links"))
        self.player_btn.config(text=self._t("open_player"))
        self.master_btn.config(text=self._t("open_master"))
        self.qr_btn.config(text=self._t("open_qr"))
        self.copy_btn.config(text=self._t("copy_player_url"))
        self.maint_frame.config(text=self._t("maintenance"))
        self.reset_pp_btn.config(text=self._t("reset_passphrase"))
        self.log_frame.config(text=self._t("log"))
        # Status text depends on state, so refresh it too.
        self._refresh_status(running=self.controller.is_running())

    def _on_lang_change(self, _event=None):
        choice = self.lang_combo.get()
        if choice in LANGUAGES:
            self.lang = choice
            self._apply_language()
            self._persist()

    def _toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self._apply_theme()
        # The toggle button's label names the OTHER theme.
        self.theme_btn.config(
            text=self._t("light") if self.theme == "dark" else self._t("dark"))
        self._persist()

    def _apply_theme(self):
        """Repaint the window and ttk widgets with the active palette."""
        p = PALETTES[self.theme]
        self.root.configure(bg=p["bg"])

        self.style.configure(".", background=p["bg"], foreground=p["fg"],
                             fieldbackground=p["entry_bg"])
        self.style.configure("TFrame", background=p["bg"])
        self.style.configure("TLabelframe", background=p["bg"],
                             foreground=p["fg"], bordercolor=p["fg_dim"])
        self.style.configure("TLabelframe.Label", background=p["bg"],
                             foreground=p["accent"])
        self.style.configure("TLabel", background=p["bg"], foreground=p["fg"])
        self.style.configure("TCheckbutton", background=p["bg"],
                             foreground=p["fg"])
        self.style.map("TCheckbutton", background=[("active", p["bg"])])
        self.style.configure("TButton", background=p["panel"],
                             foreground=p["fg"])
        self.style.map("TButton",
                       background=[("active", p["accent"]),
                                   ("disabled", p["bg"])],
                       foreground=[("disabled", p["fg_dim"])])
        self.style.configure("TEntry", fieldbackground=p["entry_bg"],
                             foreground=p["fg"], insertcolor=p["fg"])
        self.style.configure("TCombobox", fieldbackground=p["entry_bg"],
                             foreground=p["fg"], background=p["panel"])

        self.log_text.config(bg=p["log_bg"], fg=p["log_fg"],
                             insertbackground=p["fg"])
        # Status colours are palette-specific; re-apply.
        self._refresh_status(running=self.controller.is_running())

    # ---- Validation + actions -------------------------------------------

    def _current_host_port(self):
        host = self.host_var.get().strip()
        port_raw = self.port_var.get().strip()
        if not validate_host(host):
            messagebox.showerror(self._t("invalid_host_title"),
                                 self._t("invalid_host_msg", host=host))
            return None
        try:
            port = int(port_raw)
        except ValueError:
            messagebox.showerror(self._t("invalid_port_title"),
                                 self._t("invalid_port_msg"))
            return None
        if not (1024 <= port <= 65535):
            messagebox.showerror(self._t("port_range_title"),
                                 self._t("port_range_msg"))
            return None
        return host, port

    def start_server(self):
        hp = self._current_host_port()
        if hp is None:
            return
        host, port = hp
        if not port_is_free(host, port):
            messagebox.showerror(self._t("port_busy_title"),
                                 self._t("port_busy_msg", port=port))
            return
        ok, key, kw = self.controller.start(host, port)
        self._append_log(self._t(key, **kw))
        if ok:
            self._persist()
            self._refresh_status(running=True)
            self._schedule_ping()

    def stop_server(self):
        ok, key, kw = self.controller.stop()
        self._append_log(self._t(key, **kw))
        self._cancel_ping()
        self._refresh_status(running=False)

    def reset_defaults(self):
        self.host_var.set(DEFAULT_HOST)
        self.port_var.set(str(DEFAULT_PORT))
        self._persist()

    def open_in_browser(self, path):
        hp = self._current_host_port()
        if hp is None:
            return
        host, port = hp
        visitable = self.lan_ip if host == "0.0.0.0" else host
        webbrowser.open(f"http://{visitable}:{port}{path}")

    def copy_player_url(self):
        hp = self._current_host_port()
        if hp is None:
            return
        host, port = hp
        visitable = self.lan_ip if host == "0.0.0.0" else host
        url = f"http://{visitable}:{port}{PATH_PLAYER}"
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self._append_log(self._t("url_copied", url=url))

    def reset_passphrase(self):
        """Clear the Master passphrase, behind two confirmations."""
        # Editing the DB while the server holds it open risks the change being
        # overwritten on the next save. Ask the user to stop it first.
        if self.controller.is_running():
            messagebox.showwarning(self._t("reset_pp_running_title"),
                                   self._t("reset_pp_running_msg"))
            return
        if not messagebox.askyesno(self._t("reset_pp_confirm1_title"),
                                   self._t("reset_pp_confirm1_msg")):
            return
        if not messagebox.askyesno(self._t("reset_pp_confirm2_title"),
                                   self._t("reset_pp_confirm2_msg")):
            return

        result = clear_passphrase_in_db()
        if result == "ok":
            messagebox.showinfo(self._t("reset_pp_done_title"),
                                self._t("reset_pp_done_msg"))
        elif result == "none":
            messagebox.showinfo(self._t("reset_pp_none_title"),
                                self._t("reset_pp_none_msg"))
        elif result == "nodb":
            path = os.path.join(BASE_DIR, DB_RELPATH)
            messagebox.showerror(self._t("reset_pp_error_title"),
                                 self._t("reset_pp_nodb_msg", path=path))
        elif isinstance(result, tuple) and result[0] == "error":
            messagebox.showerror(self._t("reset_pp_error_title"),
                                 self._t("reset_pp_error_msg", err=result[1]))

    # ---- Status / log / ping --------------------------------------------

    def _refresh_status(self, running):
        p = PALETTES[self.theme]
        if running:
            self.status_label.config(
                text="\u25CF  " + self._t("running"), foreground=p["running"])
            self.start_btn.state(["disabled"])
            self.stop_btn.state(["!disabled"])
        else:
            self.status_label.config(
                text="\u25CF  " + self._t("stopped"), foreground=p["stopped"])
            self.start_btn.state(["!disabled"])
            self.stop_btn.state(["disabled"])
            self.ping_label.config(text="")

    def _append_log(self, line):
        self.log_text.config(state="normal")
        self.log_text.insert("end", line + "\n")
        line_count = int(self.log_text.index("end-1c").split(".")[0])
        if line_count > MAX_LOG_LINES:
            self.log_text.delete("1.0", f"{line_count - MAX_LOG_LINES}.0")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _drain_log_queue(self):
        try:
            while True:
                line = self.log_queue.get_nowait()
                if line == "__ENDED__":
                    self._append_log(self._t("server_ended"))
                    if not self.controller.is_running():
                        self._cancel_ping()
                        self._refresh_status(running=False)
                else:
                    self._append_log(line)
        except queue.Empty:
            pass
        self.root.after(LOG_DRAIN_INTERVAL_MS, self._drain_log_queue)

    def _schedule_ping(self):
        self._cancel_ping()
        self._ping_job = self.root.after(PING_INTERVAL_MS, self._do_ping)

    def _cancel_ping(self):
        if self._ping_job is not None:
            self.root.after_cancel(self._ping_job)
            self._ping_job = None

    def _do_ping(self):
        if not self.controller.is_running():
            self.ping_label.config(text="")
            return
        hp = self._current_host_port()
        if hp is None:
            return
        host, port = hp
        target = "127.0.0.1" if host == "0.0.0.0" else host
        url = f"http://{target}:{port}{PATH_PING}"

        def worker():
            reachable = False
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    # /ping returns 204; treat any 2xx as alive.
                    reachable = 200 <= resp.status < 300
            except Exception:
                reachable = False
            self.root.after(0, lambda: self._set_ping_result(reachable))

        threading.Thread(target=worker, daemon=True).start()

    def _set_ping_result(self, reachable):
        if not self.controller.is_running():
            self.ping_label.config(text="")
            return
        p = PALETTES[self.theme]
        if reachable:
            self.ping_label.config(text="\u25CF " + self._t("responds"),
                                   foreground=p["running"])
        else:
            self.ping_label.config(text="\u25CF " + self._t("no_response"),
                                   foreground=p["stopped"])
        self._schedule_ping()

    # ---- Persistence / close --------------------------------------------

    def _persist(self):
        try:
            port = int(self.port_var.get())
        except ValueError:
            port = DEFAULT_PORT
        self.cfg = {
            "host": self.host_var.get().strip() or DEFAULT_HOST,
            "port": port,
            "autostart": bool(self.autostart_var.get()),
            "lang": self.lang,
            "theme": self.theme,
        }
        save_config(self.cfg)

    def _on_close(self):
        if self.controller.is_running():
            if not messagebox.askyesno(self._t("close_running_title"),
                                       self._t("close_running_msg")):
                return
            self.controller.stop()
        self._persist()
        self.root.destroy()


def main():
    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
