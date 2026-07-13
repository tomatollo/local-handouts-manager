# Local Handouts Manager for Dungeons and Dragons

A lightweight, self-hosted web application designed for Tabletop Roleplaying Games (TTRPGs). It allows Game Masters to easily share handouts, maps, lore documents, and interactive books with players over a local Wi-Fi network, without requiring an active internet connection.

## Features
* **Zero Setup for Players:** Anyone on the same Wi-Fi can access the hub via a simple IP address on their phone, tablet, or laptop.
* **Interactive Book Reader:** Browse through multi-page tomes, journals, or grimoires seamlessly.
* **Media Hub:** Dedicated sections for high-resolution maps and PDF documents.
* **Privacy First:** Everything runs locally on your machine. No cloud, no lag.

## Roadmap / Upcoming Features
* 🛠️ **GM Dashboard:** A secure web interface for the Game Master to dynamically upload new handouts and maps mid-session.
* 👁️ **Reveal Mechanics:** Push specific images or documents to players' screens instantly.

## How to Run

This is a Flask application. Install the dependencies and run `app.py`:

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:8000` (players) or `http://localhost:8000/dm-panel` (Game Master).
Other devices on the same Wi-Fi can connect using your machine's local IP address, e.g. `http://192.168.1.42:8000`.

## Credits
The retro 8-bit visual style is inspired by [8bitcn/ui](https://8bitcn.com) by
[OrcDev](https://orcdev.com) (MIT-licensed). The look is reimplemented here in
plain CSS, with no React or Tailwind dependency.
