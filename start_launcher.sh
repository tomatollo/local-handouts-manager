#!/usr/bin/env bash
# ============================================================
#  Local Handouts Manager - launcher (Linux)
#
#  Run this to start the desktop launcher. On first run it
#  checks the prerequisites and sets up everything it needs
#  (virtual environment + dependencies), so a fresh machine
#  works with a single command / double-click.
#
#  From a terminal:   ./start_launcher.sh
#  First time only:   chmod +x start_launcher.sh
#  From a file manager: mark it executable, then double-click
#  (some file managers ask "Run" vs "Display"; choose Run).
# ============================================================

set -euo pipefail

# --- Work from the project root (this script's folder) ------------------
cd "$(dirname "$0")"

if [ -t 1 ]; then
    BOLD="$(printf '\033[1m')"; DIM="$(printf '\033[2m')"
    RED="$(printf '\033[31m')"; GRN="$(printf '\033[32m')"
    YLW="$(printf '\033[33m')"; RST="$(printf '\033[0m')"
else
    BOLD=""; DIM=""; RED=""; GRN=""; YLW=""; RST=""
fi
say()  { printf '%s\n' "$*"; }
ok()   { printf '%s[ok]%s %s\n'    "$GRN" "$RST" "$*"; }
info() { printf '%s[..]%s %s\n'    "$DIM" "$RST" "$*"; }
warn() { printf '%s[warn]%s %s\n'  "$YLW" "$RST" "$*"; }
err()  { printf '%s[error]%s %s\n' "$RED" "$RST" "$*"; }

# Keep the window open on failure only when we're attached to a terminal
# (a double-click from a file manager may have no stdin to read from).
hold_open() {
    if [ -t 0 ]; then
        echo
        read -r -p "Press Return to close." _ || true
    fi
}
trap 'code=$?; if [ "$code" -ne 0 ]; then echo; printf "%s[error]%s Setup stopped (exit %s). See the messages above.\n" "$RED" "$RST" "$code"; hold_open; fi' EXIT

say "${BOLD}Local Handouts Manager - launcher (Linux)${RST}"
say "${DIM}$(pwd)${RST}"
echo

# --- 1. Find a suitable Python (3.9+) -----------------------------------
PYTHON=""
for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1; then
        if "$cand" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] >= (3, 9) else 1)' 2>/dev/null; then
            PYTHON="$cand"; break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    err "Python 3.9 or newer was not found."
    say "    Install it with your package manager, for example:"
    say "      Debian/Ubuntu:  sudo apt install python3 python3-venv python3-pip"
    say "      Fedora:         sudo dnf install python3 python3-pip"
    say "      Arch:           sudo pacman -S python"
    exit 1
fi
ok "Python found: $("$PYTHON" --version 2>&1)  ($(command -v "$PYTHON"))"

# The venv module ships separately on some distros (python3-venv). Detect a
# missing one now with a clear message rather than a cryptic failure later.
if ! "$PYTHON" -c 'import venv' >/dev/null 2>&1; then
    err "Python's venv module is missing."
    say "    Debian/Ubuntu:  sudo apt install python3-venv"
    exit 1
fi

# --- 2. Ensure the virtual environment exists ---------------------------
if [ ! -d ".venv" ]; then
    info "No virtual environment yet - creating .venv (first-time setup)..."
    "$PYTHON" -m venv .venv
    ok "Created .venv"
    FRESH_VENV=1
else
    FRESH_VENV=0
fi

VENV_PY=".venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
    err "The virtual environment looks broken (no $VENV_PY)."
    say "    Delete the .venv folder and run this again to rebuild it."
    exit 1
fi

# --- 3. Ensure dependencies are installed -------------------------------
need_install=0
if [ "$FRESH_VENV" -eq 1 ]; then
    need_install=1
else
    "$VENV_PY" - <<'PYCHECK' >/dev/null 2>&1 || need_install=1
import importlib.util as u
for mod in ("flask", "waitress", "fitz", "PIL"):
    if u.find_spec(mod) is None:
        raise SystemExit(1)
PYCHECK
fi

if [ "$need_install" -eq 1 ]; then
    info "Installing dependencies (this can take a minute the first time)..."
    "$VENV_PY" -m pip install --upgrade pip >/dev/null 2>&1 || true
    "$VENV_PY" -m pip install -r requirements.txt
    ok "Dependencies installed"
else
    ok "Dependencies already present"
fi

# tkinter is part of the standard library but packaged separately on some
# distros; the GUI can't open without it. Warn clearly if it's absent.
if ! "$VENV_PY" -c 'import tkinter' >/dev/null 2>&1; then
    warn "Python's tkinter (GUI toolkit) is not available."
    say  "    The launcher window needs it. Install it, for example:"
    say  "      Debian/Ubuntu:  sudo apt install python3-tk"
    say  "      Fedora:         sudo dnf install python3-tkinter"
    say  "      Arch:           sudo pacman -S tk"
    say  "    Then run this again."
    exit 1
fi

# --- 4. Launch the GUI --------------------------------------------------
trap - EXIT
echo
ok "Starting the launcher..."
# Detach so the GUI keeps running if this shell/window closes.
"$VENV_PY" launcher.py >/dev/null 2>&1 &
disown 2>/dev/null || true
