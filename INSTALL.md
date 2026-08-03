# Installation & Update Guide

This guide gets the **Local Handouts Manager** running on your machine and keeps
it updated later without losing your campaign data.

There are two ways to run it:

- **The desktop launcher** - a small window with Start/Stop buttons. Best if you
  would rather not touch a terminal. *(Windows has a double-click `.bat`; macOS
  and Linux run the same launcher with one command.)*
- **The terminal** - one command to start the server. Best for quick tests, or
  if you already live in a shell.

Both use the same app and the same data, so you can switch freely.

---

## Contents

- [Prerequisites](#prerequisites)
- [1. Get the code](#1-get-the-code)
- [2. Create a virtual environment & install](#2-create-a-virtual-environment--install)
- [Option A: the desktop launcher (recommended)](#option-a-the-desktop-launcher-recommended)
- [Option B: the terminal](#option-b-the-terminal)
- [Connecting from phones & other devices](#connecting-from-phones--other-devices)
- [Running for a real session](#running-for-a-real-session)
- [Updating later](#updating-later)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.9 or newer.**
  - Windows: install from [python.org](https://www.python.org/downloads/windows/)
    and, on the first installer screen, **tick "Add python.exe to PATH"**.
  - macOS: `brew install python` (or from python.org). macOS ships an old
    Python; installing a current one is worth it.
  - Linux: use your package manager, e.g. `sudo apt install python3 python3-venv python3-pip`.
- **Git** (recommended, for easy updates) - or just download the code as a ZIP
  from the repository's green **Code** button.

Check Python is visible:

```bash
python --version      # Windows often uses "python"
python3 --version     # macOS/Linux often use "python3"
```

Use whichever of `python` / `python3` works on your system in the commands
below.

---

## 1. Get the code

With Git:

```bash
git clone https://github.com/tomatollo/local-handouts-manager.git
cd local-handouts-manager
```

Or download the ZIP from the repository, extract it, and open a terminal in the
extracted folder.

---

## 2. Create a virtual environment & install

A virtual environment (`.venv`) keeps this app's dependencies out of your system
Python. The launcher looks for `.venv` automatically, so this step is worth
doing.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> If PowerShell blocks the activate script with an execution-policy error, run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then try again -
> or use the classic `cmd` line instead: `.\.venv\Scripts\activate.bat`.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You only do this once. `requirements.txt` includes `waitress`, the small
production server the launcher uses.

---

## Option A: the desktop launcher (recommended)

The launcher is a small window: Start/Stop the server, see a live status light,
copy your LAN address for the players, open the player/master/QR pages in a
browser, switch language, toggle dark/light, and reset the master passphrase if
you ever forget it.

### Windows

Double-click **`start_launcher.bat`** in the project folder. It activates
`.venv` (if present) and opens the launcher with no stray console window.

*Want a shortcut?* Right-click `start_launcher.bat` -> **Send to -> Desktop
(create shortcut)**. You can give the shortcut a nicer name and icon.

### macOS / Linux

There is no `.bat`, but the launcher is the same Python file. With the venv
active:

```bash
python launcher.py
```

To make it one click later, create a tiny script `start_launcher.command`
(macOS) or `start_launcher.sh` (Linux):

```bash
#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -d .venv ] && source .venv/bin/activate
python launcher.py
```

Then `chmod +x start_launcher.command` (macOS) - double-clicking it in Finder
runs the launcher. On Linux, mark it executable and launch it from your file
manager or a `.desktop` entry.

### Using the launcher

1. Press **Start server**. The status light turns to *RUNNING*.
2. The window shows your **local network IP** - that is the address to give the
   players (e.g. `http://192.168.1.42:8000`).
3. Use **Open Player / Open Master / Open QR** to jump straight to a page.
4. Press **Stop server** when you are done, or just close the window (it offers
   to stop the server for you).

---

## Option B: the terminal

With the venv active (step 2), from the project folder:

```bash
python app.py        # or: python3 app.py
```

You will see the server start on port `8000`. Open `http://localhost:8000` for
the players' hub and `http://localhost:8000/dm-panel` for the Master's Screen.
Press **Ctrl+C** in the terminal to stop it.

> `python app.py` uses Flask's built-in development server. It is perfect for
> trying things out. For an actual multi-hour session with several players
> connected, prefer the launcher or `waitress` (below).

---

## Connecting from phones & other devices

Everyone must be on the **same Wi-Fi**. Players open your machine's LAN address
in any browser - no app to install.

Find your LAN address:

- **The launcher shows it** for you.
- **Windows:** run `ipconfig` and read the *IPv4 Address* (often `192.168.x.x`).
- **macOS:** `ipconfig getifaddr en0` (Wi-Fi) - or System Settings -> Network.
- **Linux:** `ip addr` (look for your `wlan`/`en` interface) or `hostname -I`.

So if your address is `192.168.1.42`, players open `http://192.168.1.42:8000`.
The **Open QR** button (or `/qr`) shows a QR code the table can scan instead of
typing.

> **Firewall.** The first time you start the server, Windows may pop up a
> Firewall prompt - allow access on **Private networks** so phones can connect.
> On macOS, allow incoming connections if asked. Corporate/guest Wi-Fi networks
> sometimes block device-to-device traffic ("client isolation"); a normal home
> network does not.

---

## Running for a real session

For a session that runs for hours with several devices, use a production server
instead of the development one. The launcher already does this for you (it runs
the app under `waitress`). To do the same by hand:

```bash
# with the venv active, from the project folder
waitress-serve --host 0.0.0.0 --port 8000 app:app
```

The **debug console is off by default** - good, because Flask's debugger can run
arbitrary code and must never be reachable by others. Only turn it on for your
own development, on a machine you trust:

```bash
# macOS / Linux
HANDOUTS_DEBUG=1 python app.py
# Windows (PowerShell)
$env:HANDOUTS_DEBUG=1 ; python app.py
```

Before your first game, open **Menu -> Master Access** and set a passphrase (see
[README - Master access & security](README.md#master-access--security)).

---

## Updating later

Your campaign data lives in `data/` and your uploaded files in
`static/uploads/` and `static/maps/`. These are **git-ignored**, so a normal
update never touches them.

With Git:

```bash
git pull
# then, with the venv active, in case dependencies changed:
pip install -r requirements.txt
```

**Always keep a backup anyway.** The safest campaign backup is the app's own
**Export** (Master -> Backup & Transfer): it bundles the database, every image,
and the interactive map (state *and* background) into one `.zip` you can re-import
anywhere. A plain copy of the `data/` and `static/` folders also works.

If you downloaded a ZIP instead of using Git, back up your `data/` and `static/`
folders, extract the new version over the old one, and put those folders back.

---

## Troubleshooting

**`python` / `pip` not found (Windows).**
Python was probably installed without "Add to PATH". Re-run the installer, choose
**Modify**, and enable it - or use the `py` launcher: `py -m venv .venv`, etc.

**PowerShell won't run the activate script.**
Run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then re-open
PowerShell. Or activate with `cmd`: `.\.venv\Scripts\activate.bat`.

**"Port 8000 is already in use."**
Another program (or a previous run) holds the port. Close it, or change the port
in the launcher, or with the terminal: `waitress-serve --port 8001 app:app`.

**Phones can't reach the server.**
Confirm they are on the same Wi-Fi, that you gave them the **LAN** address (not
`localhost`), and that the firewall allowed access on private networks. Try the
address in the host machine's own browser first to rule the app out.

**The launcher opens then closes immediately (Windows).**
It likely couldn't find Python. Make sure you created `.venv` (step 2). Running
`python launcher.py` from a terminal will show the actual error.

**"waitress not found."**
The venv isn't active, or dependencies weren't installed. Activate it (step 2)
and run `pip install -r requirements.txt` again.

**I set a passphrase and forgot it.**
Use the launcher's **Reset master passphrase** button (it asks for confirmation
twice), then set a new one from **Master Access**. Your handouts and map are not
touched.
