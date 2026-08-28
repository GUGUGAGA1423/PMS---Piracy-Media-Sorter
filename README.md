# 🎬 PMS - Piracy Media Sorter

An automated media sorting and clean-renaming CLI tool designed specifically for **Termux** and **Linux**. It automatically detects Anime, TV Shows, Movies, and Specials/OVAs, moves them to structured folders, and formats filenames cleanly.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-brightgreen.svg)

---

## ✨ Features

* 🧠 **Smart Database Detection:** Integrates with TMDB and AniList APIs to automatically categorize media based on origin country, title matching, and release format.
* ⛩️ **Anime & TV Split:** Automatically separates standard TV Shows (`/TV/Shows/`) from Japanese Anime (`/Anime/Shows/`).
* 🏷️ **Clean File Renaming:** Strips codecs, video resolution, release group tags, and bloat—formatting output strictly to `Show Title - S01E01.mkv`.
* 🌸 **OVA & Special Handling:** Automatically routes OVAs, ONAs, and special episodes into `Season 00` with original subtitle tags preserved.
* 📁 **Interactive Folder Selector:** Choose or create your main destination folder straight from an interactive terminal menu.
* 🚀 **One-Command Shortcut:** Simply type `sort` anywhere in Termux to execute.

---

## ⚡ Quick Installation

Run this single command in Termux to install all dependencies and set up the `sort` executable:

```bash
curl -sL https://raw.githubusercontent.com/GUGUGAGA1423/PMS---piracy-media-sorter/main/install.sh | bash
```
(after everything finished downloading, just type source ~/.bashrc)
---

## 🛠️ Usage

Simply run:

```bash
sort
```

On first run, the tool will automatically prompt you to:
1. Paste your **TMDB API Key** (saved to `~/.organizer_config.json`).
2. Pick your primary media directory using the **Interactive Folder Selector** (e.g., `/sdcard/Media`).

To reset your settings or change your media directory in the future, delete the configuration file:

```bash
rm ~/.organizer_config.json
```

---

## 📂 Folder Output Structure

```text
Media/ (the main folder you pick)
├── Anime/
│   ├── Movies/
│   │   └── Your Name/
│   │       └── Your Name.mkv
│   └── Shows/
│       └── The Dangers in My Heart/
│           ├── Season 00/
│           │   └── The Dangers in My Heart - S00E01 - Twi-Yaba.mp4
│           └── Season 01/
│               └── The Dangers in My Heart - S01E01.mkv
└── TV/
    └── Shows/
        └── Rick and Morty/
            └── Season 01/
                └── Rick and Morty - S01E01.mkv
```