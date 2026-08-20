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
curl -sL [https://raw.githubusercontent.com/GUGUGAGA1423/piracy-media-sorter/main/install.sh](https://raw.githubusercontent.com/GUGUGAGA1423/piracy-media-sorter/main/install.sh) | bash
