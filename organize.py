import os
import shutil
import re
import json
import requests
from guessit import guessit

WATCH_DIR = "/sdcard/Download"
CONFIG_FILE = os.path.expanduser("~/.organizer_config.json")

# ANSI Color Codes for Termux
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"

SPECIAL_REGEX = r'(?i)\b(twi-yaba|ova|oav|special|specials|sp|ona|extra|side\s*story)\b'

def select_media_directory(start_dir="/sdcard"):
    """Interactive CLI directory picker for choosing the main media destination."""
    current = os.path.abspath(start_dir)
    while True:
        print("=" * 60)
        print("📁 SELECT MEDIA DOWNLOAD DIRECTORY")
        print("=" * 60)
        print(f"Current Location: {current}\n")
        print("  [0] ✅ SELECT THIS FOLDER HERE")
        print("  [+] ➕ Create new folder here")
        print("  [..] ⬆️ Go back up\n")

        try:
            subfolders = sorted([
                d for d in os.listdir(current)
                if os.path.isdir(os.path.join(current, d)) and not d.startswith('.')
            ])
        except Exception as e:
            print(f"Error reading directory: {e}")
            subfolders = []

        if subfolders:
            print("Subfolders:")
            for idx, folder in enumerate(subfolders, 1):
                print(f"  [{idx}] 📁 {folder}")
        else:
            print("  (No subfolders found)")

        print("-" * 60)
        choice = input("Enter choice: ").strip()

        if choice == "0":
            return current
        elif choice == "..":
            parent = os.path.dirname(current)
            if os.path.exists(parent) and parent != current:
                current = parent
            else:
                print("\n⚠️ Already at top directory.\n")
        elif choice == "+":
            new_name = input("Enter new folder name: ").strip()
            if new_name:
                new_path = os.path.join(current, new_name)
                try:
                    os.makedirs(new_path, exist_ok=True)
                    current = new_path
                except Exception as e:
                    print(f"\n❌ Failed to create folder: {e}\n")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(subfolders):
                current = os.path.join(current, subfolders[idx])
            else:
                print("\n⚠️ Invalid selection number.\n")
        else:
            print("\n⚠️ Invalid input.\n")

def load_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        except Exception:
            config = {}

    tmdb_key = config.get("TMDB_API_KEY", "").strip()
    if not tmdb_key:
        print("\n--- TMDB API Setup ---")
        tmdb_key = input("Paste TMDB API Key: ").strip()
        config["TMDB_API_KEY"] = tmdb_key

    media_dir = config.get("MEDIA_DIR", "").strip()
    if not media_dir or not os.path.exists(media_dir):
        media_dir = select_media_directory("/sdcard")
        config["MEDIA_DIR"] = media_dir

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save config file: {e}")

    return tmdb_key, media_dir

TMDB_API_KEY, MEDIA_DIR = load_config()
NOISE_PREFIXES = r'(?i)^(animepahe|subsplease|erai-raws|judas|horriblesubs|crunchyroll)[_\s\-]*'

def clean_title(filename):
    info = guessit(filename)
    raw_title = str(info.get("title", "Unknown Title"))
    cleaned = re.sub(NOISE_PREFIXES, '', raw_title)
    cleaned = cleaned.replace('_', ' ').strip()
    
    has_explicit_season = "season" in info and info["season"] is not None
    season = info.get("season", 1)
    episode = info.get("episode")
    
    special_match = re.search(SPECIAL_REGEX, filename)
    is_special = bool(special_match) or info.get("type") == "special" or season == 0

    if is_special and not has_explicit_season:
        season = 0

    extra_tag = ""
    if special_match:
        matched_kw = special_match.group(1)
        if matched_kw.lower() not in ["special", "specials", "sp", "ova", "oav", "ona"]:
            extra_tag = matched_kw.title()

    return cleaned, season, episode, info.get("type"), is_special, extra_tag

def format_clean_filename(title, season, episode, is_movie, ext, extra_tag=""):
    safe_title = re.sub(r'[\\/*?:"<>|]', '', title)
    if is_movie:
        return f"{safe_title}{ext}"
    
    season_str = f"S{season:02d}"
    if isinstance(episode, list):
        ep_str = "".join([f"E{e:02d}" for e in episode])
    elif episode is not None:
        ep_str = f"E{int(episode):02d}"
    else:
        ep_str = "E01"

    if extra_tag:
        safe_tag = re.sub(r'[\\/*?:"<>|]', '', extra_tag).strip()
        return f"{safe_title} - {season_str}{ep_str} - {safe_tag}{ext}"
    
    return f"{safe_title} - {season_str}{ep_str}{ext}"

def check_tmdb(title):
    if not TMDB_API_KEY:
        return None, title, False

    words = title.split()
    for i in range(len(words), 0, -1):
        sub_query = " ".join(words[:i])
        if len(sub_query) < 2:
            break

        encoded = requests.utils.quote(sub_query)
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={encoded}"
        try:
            res = requests.get(url, timeout=5).json()
            results = res.get("results", [])
            if results:
                top = results[0]
                media_type = top.get("media_type")
                canonical_title = top.get("name") or top.get("title") or sub_query
                origin_countries = top.get("origin_country", [])
                original_lang = top.get("original_language", "")
                is_japanese = "JP" in origin_countries or original_lang == "ja"
                return media_type, canonical_title, is_japanese
        except Exception:
            pass
    return None, title, False

def check_anilist(title):
    url = "https://graphql.anilist.co"
    query = """
    query ($search: String) {
      Media (search: $search, type: ANIME) {
        format
        title {
          english
          romaji
        }
      }
    }
    """
    words = title.split()
    for i in range(len(words), 0, -1):
        sub_query = " ".join(words[:i])
        if len(sub_query) < 2:
            break
        try:
            response = requests.post(
                url, json={"query": query, "variables": {"search": sub_query}}, timeout=5
            )
            data = response.json()
            if "data" in data and data["data"]["Media"]:
                media = data["data"]["Media"]
                eng_title = media["title"].get("english") or ""
                rom_title = media["title"].get("romaji") or ""
                canonical_title = eng_title or rom_title or sub_query
                is_movie = media.get("format") == "MOVIE"
                return True, is_movie, canonical_title
        except Exception:
            pass
    return False, False, title

def organize_media():
    if not os.path.exists(WATCH_DIR):
        print(f"Directory not found: {WATCH_DIR}")
        return

    video_extensions = (".mp4", ".mkv", ".avi", ".webm")

    for file_name in os.listdir(WATCH_DIR):
        ext = os.path.splitext(file_name)[1]
        if ext.lower() not in video_extensions:
            continue

        file_path = os.path.join(WATCH_DIR, file_name)
        if os.path.isdir(file_path):
            continue

        title_query, season, episode, guessed_type, is_special, extra_tag = clean_title(file_name)
        tmdb_type, canonical_title, is_japanese = check_tmdb(title_query)

        is_movie = False
        icon = "🎬"

        if tmdb_type:
            if is_japanese:
                icon = "⛩️"
                if tmdb_type == "movie":
                    is_movie = True
                    target_dir = os.path.join(MEDIA_DIR, "Anime", "Movies", canonical_title)
                else:
                    target_dir = os.path.join(MEDIA_DIR, "Anime", "Shows", canonical_title, f"Season {season:02d}")
            else:
                if tmdb_type == "tv":
                    icon = "📺"
                    target_dir = os.path.join(MEDIA_DIR, "TV", "Shows", canonical_title, f"Season {season:02d}")
                else:
                    icon = "🎥"
                    is_movie = True
                    target_dir = os.path.join(MEDIA_DIR, "Movies", canonical_title)
        else:
            is_anime, is_anime_movie, ani_title = check_anilist(title_query)
            if is_anime:
                icon = "⛩️"
                canonical_title = ani_title
                if is_anime_movie:
                    is_movie = True
                    target_dir = os.path.join(MEDIA_DIR, "Anime", "Movies", ani_title)
                else:
                    target_dir = os.path.join(MEDIA_DIR, "Anime", "Shows", ani_title, f"Season {season:02d}")
            elif guessed_type == "episode":
                icon = "📺"
                canonical_title = title_query.title()
                target_dir = os.path.join(MEDIA_DIR, "TV", "Shows", canonical_title, f"Season {season:02d}")
            elif guessed_type == "movie":
                icon = "🎥"
                is_movie = True
                canonical_title = title_query.title()
                target_dir = os.path.join(MEDIA_DIR, "Movies", canonical_title)
            else:
                icon = "📦"
                canonical_title = title_query.title()
                target_dir = os.path.join(MEDIA_DIR, "Unsorted")

        new_file_name = format_clean_filename(canonical_title, season, episode, is_movie, ext, extra_tag)

        os.makedirs(target_dir, exist_ok=True)
        dest_path = os.path.join(target_dir, new_file_name)

        print(f"\n{C_BOLD}{C_GREEN}🚀 [MOVING MEDIA]{C_RESET}")
        print(f"  {C_BOLD}📄 Original :{C_RESET} {file_name}")
        print(f"  {C_BOLD}🏷️  Renamed  :{C_RESET} {C_CYAN}{new_file_name}{C_RESET}")
        print(f"  {C_BOLD}{icon} Category :{C_RESET} {C_MAGENTA}{target_dir.replace(MEDIA_DIR, '')}{C_RESET}")
        print(f"  {C_BOLD}📂 Full Path:{C_RESET} {C_YELLOW}{dest_path}{C_RESET}")

        shutil.move(file_path, dest_path)

if __name__ == "__main__":
    organize_media()
