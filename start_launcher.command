#!/usr/bin/env bash
# ============================================================
#  Local Handouts Manager - launcher (macOS)
#
#  Double-click this file in Finder to start the desktop
#  launcher. On first run it checks the prerequisites and sets
#  up everything it needs (virtual environment + dependencies),
#  so a fresh machine works with one click.
#
#  Keep this file in the project root, next to app.py and
#  launcher.py. If double-click does nothing, run once in a
#  terminal:  chmod +x start_launcher.command
# ============================================================

# Stop on the first genuine error; treat unset vars as errors.
set -euo pipefail

# --- Always work from the project root (this script's folder) -----------
# On macOS a double-clicked .command runs from $HOME, not its own folder,
# so we must cd into it explicitly or every relative path breaks.
cd "$(dirname "$0")"

# Small helpers for readable, coloured status lines (fall back to plain
# text if the terminal doesn't support colour).
if [ -t 1 ]; then
    BOLD="$(printf '\033[1m')"; DIM="$(printf '\033[2m')"
    RED="$(printf '\033[31m')"; GRN="$(printf '\033[32m')"
    YLW="$(printf '\033[33m')"; RST="$(printf '\033[0m')"
else
    BOLD=""; DIM=""; RED=""; GRN=""; YLW=""; RST=""
fi
say()  { printf '%s\n' "$*"; }
ok()   { printf '%s[ok]%s %s\n'   "$GRN" "$RST" "$*"; }
info() { printf '%s[..]%s %s\n'   "$DIM" "$RST" "$*"; }
warn() { printf '%s[warn]%s %s\n' "$YLW" "$RST" "$*"; }
err()  { printf '%s[error]%s %s\n' "$RED" "$RST" "$*"; }

# If anything fails, keep the window open so the user can read why (a
# double-clicked Terminal window would otherwise vanish instantly).
hold_open() {
    echo
    read -r -p "Press Return to close this window." _ || true
}
trap 'code=$?; if [ "$code" -ne 0 ]; then echo; printf "%s[error]%s Setup stopped (exit %s). See the messages above.\n" "$RED" "$RST" "$code"; hold_open; fi' EXIT

say "${BOLD}Local Handouts Manager - launcher (macOS)${RST}"
say "${DIM}$(pwd)${RST}"
echo

# --- 1. Find a suitable Python (3.9+) -----------------------------------
# macOS ships an old python; prefer python3. We accept either name but
# require version >= 3.9 so the app and launcher run.
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
    say "    Install it from https://www.python.org/downloads/macos/"
    say "    or with Homebrew:  brew install python"
    exit 1
fi
ok "Python found: $("$PYTHON" --version 2>&1)  ($(command -v "$PYTHON"))"

# --- 2. Ensure the virtual environment exists ---------------------------
# The launcher looks for .venv automatically; create it if missing so a
# brand-new checkout just works.
if [ ! -d ".venv" ]; then
    info "No virtual environment yet - creating .venv (first-time setup)..."
    "$PYTHON" -m venv .venv
    ok "Created .venv"
    FRESH_VENV=1
else
    FRESH_VENV=0
fi

# Use the venv's own interpreter directly (no need to 'activate' in a
# script): it always points pip and python at the right place.
VENV_PY=".venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
    err "The virtual environment looks broken (no $VENV_PY)."
    say "    Delete the .venv folder and run this again to rebuild it."
    exit 1
fi

# --- 3. Ensure dependencies are installed -------------------------------
# Cheap check: can we import the key packages? If not (fresh venv, or a
# new dependency was added on update), install from requirements.txt.
need_install=0
if [ "$FRESH_VENV" -eq 1 ]; then
    need_install=1
else
    "$VENV_PY" - <<'PYCHECK' >/dev/null 2>&1 || need_install=1
import importlib.util as u
# Import names differ from the pip names for a couple of these.
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

# --- 4. Launch the GUI --------------------------------------------------
# On success we don't want the "press Return" hold, so clear the trap.
trap - EXIT
echo
ok "Starting the launcher..."
# Run detached so closing the Terminal window doesn't kill the GUI, and
# so this script returns immediately.
"$VENV_PY" launcher.py >/dev/null 2>&1 &
disown 2>/dev/null || true
