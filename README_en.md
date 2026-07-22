# 🎵 Interactive Chord Viewer & Harmonic Catalog

[![pt-br](https://img.shields.io/badge/Language-Portugu%C3%AAs-green.svg)](README.md) [![en](https://img.shields.io/badge/Language-English-blue.svg)](README_en.md)
*Read in / Leia em:* 🇺🇸 **English** | 🇧🇷 [Português](README.md)

An interactive and automated ecosystem for real-time chord visualization, harmonic analysis, instant key transposition, and song cataloging designed for **Acoustic Guitar (Violão)**, **Cavaquinho**, and **Piano/Keyboard**.

---

## ✨ Key Features

- **Interactive Hub (`index.html`):** Unified catalog with real-time search by title, artist, or composer, quick difficulty-level filters (Beginner, Intermediate, Advanced, Expert), and dynamic grouping (A-Z, by artist, or chord count).
- **Instant Key Transposition:** Change the pitch/key of any song with on-the-fly recalculation of musical intervals, notes, and chord voicings.
- **Multi-Instrument Visualizers:**
  - **Acoustic Guitar (`viewer.html` / `viewer-violao.html`):** Harmonic diagrams and instant transposition.
  - **Cavaquinho (`viewer-cavaquinho.html`):** Dedicated chord voicings and interactive fretboard diagrams in standard tuning (D-G-B-D).
  - **Piano / Keyboard (`viewer-piano.html`):** Interactive virtual keyboard highlighting exact component notes of every transposed chord.
- **Harmonic Engine (`chord_parser.py`):** Mathematical calculation engine capable of breaking down complex chords, identifying root notes, intervals, qualities, and extensions.
- **CLI Import Pipeline (`tools/gerar_musica.py`):** Automated command-line tool to import chords directly from URLs (such as Cifra Club and Ultimate Guitar), parsing HTML/Markdown into structured JSON/JS data and rebuilding the catalog index instantly.

---

## 📂 Project Structure

```text
visualizador_de_cifras/
├── index.html                  # Interactive Hub / Catalog overview
├── viewer.html                 # Acoustic Guitar transposer & visualizer
├── viewer-cavaquinho.html      # Dedicated Cavaquinho visualizer
├── viewer-piano.html           # Dedicated Piano/Keyboard visualizer
├── assets/
│   ├── css/style.css           # Global application styles (Dark Mode & UI)
│   └── js/                     # Rendering scripts and visualizer controllers
├── data/
│   ├── catalog.js / .json      # Centralized song index (188+ songs)
│   └── songs/                  # Structured song database in .json and .js
├── tools/
│   ├── gerar_musica.py         # CLI tool to import chord sheets via URL
│   ├── generate_catalog.py     # Unified alphabetical index generator
│   └── chord_parser.py         # Chord analysis & breakdown engine
└── audio_to_cifra/             # Experimental acoustic audio-to-chord transcription module
```

---

## 🚀 CLI Song Import Pipeline (`tools/gerar_musica.py`)

To add one or more songs to the catalog using a web link (e.g., Cifra Club or Ultimate Guitar), run the following command from the project root directory:

```powershell
python tools/gerar_musica.py "https://www.cifraclub.com.br/artista/nome-da-musica/#tabs=false"
```

### What the command does automatically:
1. **Download & Clean:** Fetches the webpage content, extracts lyrics, and removes unnecessary metadata or ads.
2. **Chord Detection:** Wraps detected chord names inside interactive tags `<span class="chord" data-chord="...">`.
3. **Harmonic Breakdown:** Analyzes every chord through `chord_parser.py`, computing musical intervals and notes.
4. **Data Generation:** Saves structured files (`data/songs/SongTitle.json` and `.js`) ready for front-end rendering.
5. **Catalog Update:** Triggers `generate_catalog.py` to re-sort `data/catalog.js` in alphabetical order, keeping `index.html` and difficulty badges fully synchronized.

To manually regenerate the unified index (e.g., after editing `.json` files by hand):
```powershell
python tools/generate_catalog.py
```

---

## 💻 How to Run Locally

Because the front-end is built using standard HTML5, Vanilla CSS3, and modern JavaScript, no build steps or bundlers are required.

1. **Open Directly:** You can open `index.html` directly in any web browser.
2. **Local Web Server (Recommended):** To prevent potential CORS restrictions when loading scripts or data, start a simple HTTP server from the root folder:
   ```powershell
   python -m http.server 8000
   ```
   Then navigate to `http://localhost:8000` in your browser.

---

## 🎸 Current Repertoire

The repository currently contains **188 structured songs** spanning Brazilian MPB, Samba, Rock, and Blues classics (including Cartola, Ismael Silva, David Bowie, Tom Jobim, Luiz Tatit, Adoniran Barbosa, Muddy Waters, and many more).

---
*Maintained for harmonic analysis, instrument practice, and musical education.*
