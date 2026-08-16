# Installation & Update Guide

> Part of the project documentation — see the full index in
> [docs/README.md](docs/README.md).

This guide gets the **Local Handouts Manager** running on your machine and keeps
it updated later without losing your campaign data.

There are two ways to run it:

- **The desktop launcher** - a small window with Start/Stop buttons. Best if you
  would rather not touch a terminal. Each OS has its own double-click starter
  (`start_launcher.bat` on Windows, `start_launcher.command` on macOS,
  `start_launcher.sh` on Linux) and **the first run sets everything up for you**
  - it checks the prerequisites and installs what is missing.
- **The terminal** - one command to start the server. Best for quick tests, or
  if you already live in a shell.

Both use the same app and the same data, so you can switch freely.

> **In a hurry?** Install [Python](#prerequisites) (3.9+), get the code, then
> double-click the starter for your system. It creates the virtual environment,
> installs the dependencies, and opens the launcher - no terminal needed. The
> manual steps below are there if you prefer to do it yourself or something goes
> wrong.

---

## Contents

- [Prerequisites](#prerequisites)
- [1. Get the code](#1-get-the-code)
- [2. Create a virtual environment & install](#2-create-a-virtual-environment--install)
- [3. Vendor libraries (already included)](#3-vendor-libraries-already-included)
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
Python.

> **You can skip this whole step if you use the launcher.** The double-click
> starters (`start_launcher.bat` / `.command` / `.sh`) create `.venv` and
> install the dependencies on their first run. Do this manually only if you
> prefer the terminal, or want to see each step yourself.

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

## 3. Vendor libraries (already included)

The **Book** viewer (page-curl) and the **3D Inspect** viewer rely on two
JavaScript libraries (StPageFlip and Three.js) that the app serves *itself*
rather than from a CDN, so the table stays fully offline. **These are already
committed to the repository**, in `static/vendor/`, so a normal clone or ZIP
download has everything — there is nothing to do here.

You only need `fetch_vendor.py` if you want to **re-download or update** those
libraries (for example after bumping a version):

```bash
# optional — with the venv active, from the project folder
python fetch_vendor.py        # or: python3 fetch_vendor.py
```

It overwrites the copies in `static/vendor/` and needs internet access while it
runs. For a normal install you can skip it entirely.

---

## Option A: the desktop launcher (recommended)

The launcher is a small window: Start/Stop the server, see a live status light,
copy your LAN address for the players, open the player/master/QR pages in a
browser, switch language, toggle dark/light, and reset the master passphrase if
you ever forget it.

Each system has its own starter in the project folder. **On first run it checks
the prerequisites and installs whatever is missing** - it creates `.venv` and
installs the dependencies for you - then opens the launcher. Later runs skip
straight to opening it.

### Windows

Double-click **`start_launcher.bat`**. The first time, a small setup window
reports its progress (finding Python, creating `.venv`, installing packages);
after that it opens the launcher with no stray console window.

*Want a shortcut?* Right-click `start_launcher.bat` -> **Send to -> Desktop
(create shortcut)**. You can give the shortcut a nicer name and icon.

### macOS

Double-click **`start_launcher.command`** in Finder. The first run opens a
Terminal window that sets things up (Python check, `.venv`, dependencies) and
then launches the app.

> The very first time, macOS may need you to make it runnable: either
> right-click -> **Open** and confirm once, or run `chmod +x
> start_launcher.command` in a Terminal in the project folder. If Gatekeeper
> blocks it, **System Settings -> Privacy & Security** has an *Open anyway*
> button.

### Linux

Run **`start_launcher.sh`** - `./start_launcher.sh` from a terminal, or
double-click it in your file manager and choose *Run* (mark it executable first
with `chmod +x start_launcher.sh`, or via Properties -> Permissions). The first
run sets up `.venv` and the dependencies, then opens the launcher.

> The launcher's window needs Python's Tk toolkit. If the script says tkinter is
> missing, install it: `sudo apt install python3-tk` (Debian/Ubuntu),
> `sudo dnf install python3-tkinter` (Fedora), or `sudo pacman -S tk` (Arch),
> then run the script again.

### Using the launcher

1. Press **Start server**. The status light turns to *RUNNING*.
2. The window shows your **local network IP** - that is the address to give the
   players (e.g. `http://192.168.1.42:8000`).
3. Use **Open Player / Open Master / Open QR** to jump straight to a page.
4. Press **Stop server** when you are done, or just close the window (it offers
   to stop the server for you).

> **Changing the host.** The server listens on `0.0.0.0` by default, which is
> what lets phones on your Wi-Fi reach it - you rarely need to change it. If you
> do (for example `127.0.0.1` to keep it to this computer only), open the
> **Advanced configuration** section in the launcher to reveal the Host field.
> The port stays on the main view.

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
The starter now keeps its setup window open and prints the reason on failure -
read the last lines. The usual cause is Python not being found: install it and
tick *Add python.exe to PATH*. You can also run `python launcher.py` from a
terminal (with `.venv` active) to see the raw error.

**The starter says "Python 3.9 or newer was not found."**
Either Python isn't installed, or it isn't on your PATH, or it's older than 3.9.
Install a current version (see [Prerequisites](#prerequisites)); on Windows,
re-run the installer and enable *Add python.exe to PATH*. The starter also tries
the `py` launcher on Windows, so `py -3 --version` is a good thing to check.

**macOS / Linux: the starter won't run or "permission denied."**
Mark it executable once: `chmod +x start_launcher.command` (macOS) or
`chmod +x start_launcher.sh` (Linux). On macOS you can instead right-click ->
**Open** the first time. If a file manager only *opens* the script in an editor,
use the terminal (`./start_launcher.sh`) or enable "run executable text files"
in its preferences.

**"waitress not found."**
The venv isn't active, or dependencies weren't installed. Activate it (step 2)
and run `pip install -r requirements.txt` again.

**The Book or 3D Inspect viewer opens blank.**
Those viewers use the self-hosted libraries in `static/vendor/`, which ship with
the repo. If the folder is missing or the files were damaged, restore them: from
the project folder with the venv active, run `python fetch_vendor.py` (it needs
internet access while it runs). The Carousel viewer works regardless, so a blank
Book/3D viewer with working image handouts is the tell-tale sign.

**I set a passphrase and forgot it.**
Use the launcher's **Reset master passphrase** button (it asks for confirmation
twice), then set a new one from **Master Access**. Your handouts and map are not
touched.
