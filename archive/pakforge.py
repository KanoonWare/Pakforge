import asyncio
import base64
import html
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import traceback
import urllib.request
import webbrowser
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import unquote

import customtkinter as ctk
import requests
from PIL import Image

# Modern cryptography for pure-Python MEGA downloads
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# ---------------------------------------------------------------------------
# App identity
# ---------------------------------------------------------------------------
APP_NAME = "PakForge"
APP_TAGLINE = "HD Texture Pack Manager for Emulators"
APP_VERSION = "v0.3.0-multipack"

DISCLAIMER_TEXT = (
    f"{APP_NAME} links to HD texture packs created and hosted by third-party "
    f"community members. {APP_NAME} does not create, host, or claim ownership "
    "of any texture pack content, and does not distribute game ROMs or "
    "copyrighted game assets of any kind.\n\n"
    "You are responsible for ensuring you own a legal copy of any game you "
    "use with these texture packs. Texture pack availability depends on "
    "third-party hosts and may change or be removed at any time.\n\n"
    "If you are a texture pack creator and would like your work credited "
    "differently or removed from this list, please reach out through the "
    "contact info on kanoonware.com."
)

CONFIG_FILENAME = "pakforge_config.json"

# Game Configurations — PlayStation 2
PS2_GAMES = [
    {
        "game_id": "SLUS-21385",
        "title": "The Godfather",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://1drv.ms/u/c/f4ce8a5d6475446d/EaNC-gaxq_xHg5Z9zMvQPysBrktZ58km6pGHeCi1SGKjhA?e=BJa6PQ&download=1",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            },
        ]
    },
    {
        "game_id": "SLUS-21268",
        "title": "24: The Game",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://www.mediafire.com/file_premium/6l0b8ca2axm8nt5/SLUS-21268.zip/file",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SLUS-20246",
        "title": "Capcom vs SNK 2",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://1drv.ms/u/s!ApJOQlD7y1v-kHerIYC-c6gIc9yG?e=B4TJ0x&download=1",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SLUS-21722",
        "title": "Chaos Wars",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://1drv.ms/u/c/f4ce8a5d6475446d/EckdwFfoBPpCiH0BtJwZPpUBOu7bcTLQNyJyEDusum1ORw?e=OjXr0m&download=1",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SLUS-20845",
        "title": "Cold Winter",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://www.mediafire.com/file_premium/0dr9yadp0vi72q7/SLUS-20845.zip/file",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SLUS-20836",
        "title": "Digimon World 4",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://1drv.ms/u/s!ApJOQlD7y1v-kQt6geUpBAx2HccT?e=3gv30c&download=1",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SLUS-21598",
        "title": "Digimon World Data Squad",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://1drv.ms/u/s!ApJOQlD7y1v-kQU8HEPKh60zfU84?e=fHqSO8&download=1",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SLUS-20439",
        "title": "Futurama",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://www.mediafire.com/file_premium/37wfnjb6kxo8bwb/SLUS-20439.zip/file",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SCUS-97558",
        "title": "Jak and Dexter: The Lost Frontier",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://www.mediafire.com/file_premium/4nuuebgqbqzstcb/SCUS-97558.zip/file",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SLUS-20265",
        "title": "James Bond 007: Agent Under Fire",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://www.mediafire.com/file_premium/2k5ukbe621edbaw/SLUS-20265.zip/file",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SLUS-21735",
        "title": "Mana Khemia: Alchemists of Al-Revis",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://mega.nz/file/ZrNwyRJT#2f8InukW7GiEDs8yVkAU0v-vaA6PISO9HyeUIerCerM",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    }, 
    {
        "game_id": "SLUS-20875",
        "title": "Predator: Concrete Jungle",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://1drv.ms/u/s!ApJOQlD7y1v-kHYKTix4M4GkleJO?e=Mhj8LZ&download=1",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
    {
        "game_id": "SLUS-20442",
        "title": "Red Faction II",
        "cover_url": "https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{game_id}.jpg",
        "packs": [
            {
                "pack_id": "sombershroud",
                "pack_name": "SomberShroud HD Pack",
                "download_url": "https://www.mediafire.com/file_premium/12rgic4i7brhl3i/SLUS-20442.zip/file",
                "credit_name": "SomberShroud",
                "credit_url": "https://gbatemp.net/members/sombershroud.668052/",
            }
        ]
    },
]

# Game Configurations — Nintendo 64
N64_GAMES = [
    {
        "game_id": "Banjo-Kazooie",
        "title": "Banjo-Kazooie",
        "cover_url": "https://www.arcadeartwork.org/galleries/N64-box/Banjo-Kazooie--U---V1.1-----.jpg",
        "packs": [
            {
                "pack_id": "nikachu",
                "pack_name": "Nikachu HD Pack",
                "download_url": "https://files.emulationking.com/n64/texturepacks/banjokazooie/Banjo-Kazooie-by-nikachu.zip",
                "credit_name": "Nikachu",
                "credit_url": "https://emulationking.com/nintendo/n64/games/banjokazooie/texturepacks/nikachu/",
            }
        ]
    },
    {
        "game_id": "MARIOKART64",
        "title": "Mario Kart 64",
        "cover_url": "https://www.arcadeartwork.org/action.php?id=82362&part=e&download",
        "packs": [
            {
                "pack_id": "BFrancois_Mario_Kart",
                "pack_name": "BFrancois Mario Kart 64 Texture Pack",
                "download_url": "https://files.emulationking.com/n64/texturepacks/mariokart64/Mario_Kart_64-BFrancois.zip",
                "credit_name": "BFrancois",
                "credit_url": "https://emulationking.com/nintendo/n64/games/mariokart64/texturepacks/bfrancois/",
            },
            {
                "pack_id": "MK64_Reloaded",
                "pack_name": "MK64 Reloaded",
                "download_url": "https://github.com/GhostlyDark/MK64-Reloaded/releases/download/v2026.04.03/mk64-reloaded-v2026.04.03-gliden64-hts-4k.7z",
                "credit_name": "GhostlyDark",
                "credit_url": "https://evilgames.eu/texture-packs/mk64-reloaded.htm",
            },
            {
                "pack_id": "Kerber2k_mk64",
                "pack_name": "Kerber2k's Mario Kart 64 Texture Pack",
                "download_url": "https://files.emulationking.com/n64/texturepacks/mariokart64/Mario_kart_64-Kerber2k.zip",
                "credit_name": "kerberk2k",
                "credit_url": "https://emulationking.com/nintendo/n64/games/mariokart64/texturepacks/kerberk2k/",
            }
        ]
    },
    {
        "game_id": "RESIDENT EVIL 2",
        "title": "Resident Evil 2",
        "cover_url": "https://www.arcadeartwork.org/action.php?id=82443&part=e&download",
        "packs": [
            {
                "pack_id": "re2_reloaded",
                "pack_name": "RE2 Reloaded",
                "download_url": "https://evilgames.eu/files/texture-packs/re2-reloaded-v2.0.0-png-4k.zip",
                "credit_name": "GhostlyDark",
                "credit_url": "https://evilgames.eu/texture-packs/re2-reloaded.htm",
            }
        ]
    },
    {
        "game_id": "SHADOW MAN",
        "title": "Shadowman",
        "cover_url": "https://www.arcadeartwork.org/action.php?id=82455&part=e&download",
        "packs": [
            {
                "pack_id": "Master V's Shadow Man Texture Pack",
                "pack_name": "Shadow Man",
                "download_url": "https://files.emulationking.com/n64/texturepacks/shadowman/Shadowman-MasterV.zip",
                "credit_name": "MasterV",
                "credit_url": "https://emulationking.com/nintendo/n64/games/shadowman/texturepacks/masterv/",
            }
        ]
    },
    {
        "game_id": "STAR Fox",
        "title": "Star Fox 64",
        "cover_url": "https://www.arcadeartwork.org/action.php?id=82465&part=e&download",
        "packs": [
            {
                "pack_id": "starfox_64",
                "pack_name": "UnaidedCoder's Star Fox 64 Texture Pack",
                "download_url": "https://files.emulationking.com/n64/texturepacks/starfox64/StarFox64-Unaidedcoder.zip",
                "credit_name": "UnaidedCoder",
                "credit_url": "https://emulationking.com/nintendo/n64/games/starfox64/texturepacks/unaidedcoder/",
            }
        ]
    }
]

CONSOLES = [
    {"id": "ps2", "name": "PS2", "active": True, "games": PS2_GAMES},
    {"id": "n64", "name": "N64", "active": True, "games": N64_GAMES},
    {"id": "gamecube", "name": "GameCube", "active": False, "games": []},
    {"id": "wii", "name": "Wii", "active": False, "games": []},
    {"id": "switch", "name": "Switch", "active": False, "games": []},
    {"id": "ps3", "name": "PS3", "active": False, "games": []},
    {"id": "xbox360", "name": "Xbox 360", "active": False, "games": []},
    {"id": "xbox", "name": "Xbox", "active": False, "games": []},
    {"id": "psp", "name": "PSP", "active": False, "games": []},
]

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg": "#14101b",
    "panel": "#1e1730",
    "panel_alt": "#150f22",
    "line": "#332a45",
    "accent": "#f2a63d",
    "accent_hover": "#ffb955",
    "accent_text": "#1a1300",
    "mint": "#5fe1a6",
    "mint_hover": "#4bc98f",
    "text": "#f4efe6",
    "muted": "#9c93ae",
    "danger": "#d9534f",
    "danger_hover": "#b23b38",
}
FONT_FAMILY = "Segoe UI"


# ---------------------------------------------------------------------------
# Path Resolution Helpers
# ---------------------------------------------------------------------------
def get_default_pcsx2_texture_path():
    if sys.platform.startswith("win"):
        try:
            import winreg
            reg_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key) as key:
                docs_path, _ = winreg.QueryValueEx(key, "Personal")
                docs_path = os.path.expandvars(docs_path)
                pcsx2_path = os.path.join(docs_path, "PCSX2", "textures")
                if os.path.exists(pcsx2_path):
                    return pcsx2_path
        except Exception:
            pass

        onedrive_docs = os.path.expanduser(r"~\OneDrive\Documents\PCSX2\textures")
        if os.path.exists(onedrive_docs):
            return onedrive_docs

    return os.path.expanduser(r"~\Documents\PCSX2\textures")


# ---------------------------------------------------------------------------
# Download Handlers
# ---------------------------------------------------------------------------
def _mega_base64_url_decode(data: str) -> bytes:
    data += '=' * ((4 - len(data) % 4) % 4)
    return base64.b64decode(data.replace('-', '+').replace('_', '/'))


def handle_mega_download(url: str, output_path: str, logger=None, progress_callback=None, cancel_event=None):
    if logger:
        logger("Initiating modern MEGA API payload resolution...")

    try:
        if "#" not in url:
            raise ValueError("Invalid MEGA URL format. Missing key fragment (#).")
        
        file_part, key_str = url.split("#", 1)
        file_id = file_part.split("/")[-1]
        
        raw_key = _mega_base64_url_decode(key_str)
        if len(raw_key) != 32:
            raise ValueError("Invalid MEGA decryption key length.")
        
        k = bytes(a ^ b for a, b in zip(raw_key[:16], raw_key[16:]))
        iv = raw_key[16:24] + b'\x00' * 8
    except Exception as e:
        raise Exception(f"Failed to parse MEGA URL fragment: {e}")

    api_url = "https://g.api.mega.co.nz/cs"
    payload = [{"a": "g", "g": 1, "p": file_id}]
    
    resp = requests.post(api_url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()[0]

    if isinstance(data, int):
        raise Exception(f"MEGA API error code {data}: file removed or restricted.")

    download_url = data["g"]
    file_size = data.get("s", 0)

    if logger:
        logger(f"Streaming {format_bytes(file_size)} from MEGA storage node...")

    cipher = Cipher(algorithms.AES(k), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    dest_dir = os.path.dirname(output_path)
    os.makedirs(dest_dir, exist_ok=True)

    with requests.get(download_url, stream=True, timeout=60) as dl_resp:
        if dl_resp.status_code == 509:
            raise Exception("MEGA Transfer Quota Exceeded (HTTP 509). IP bandwidth quota reached.")
        dl_resp.raise_for_status()
        downloaded = 0
        
        with open(output_path, "wb") as out_file:
            for chunk in dl_resp.iter_content(chunk_size=128 * 1024):
                if cancel_event and cancel_event.is_set():
                    raise InterruptedError("Download canceled by user.")
                if chunk:
                    decrypted_chunk = decryptor.update(chunk)
                    out_file.write(decrypted_chunk)
                    downloaded += len(chunk)
                    
                    if progress_callback and file_size > 0:
                        progress_callback(downloaded / file_size)

            out_file.write(decryptor.finalize())

    if logger:
        logger("MEGA download & decryption completed successfully.")


def resolve_mediafire_link(url: str, logger=None):
    if logger:
        logger("Resolving MediaFire link via direct HTML parsing...")
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        })
        
        response = session.get(url, timeout=30)
        response.raise_for_status()

        patterns = [
            r'href="([^"]*static\.mediafire\.com/download/[^"]+)"',
            r'href="([^"]*download\d*\.mediafire\.com/[^"]+)"',
            r'id="downloadButton"\s+href="([^"]+)"',
            r'aria-label="Download file"\s+href="([^"]+)"',
            r'href="(https?://download[^"]+\.mediafire\.com/[^"]+)"'
        ]

        for pattern in patterns:
            match = re.search(pattern, response.text, re.IGNORECASE)
            if match:
                direct_url = match.group(1)
                if logger:
                    logger(f"Resolved MediaFire Direct URL: {direct_url}")
                return direct_url

        raise Exception("Could not locate direct download link inside MediaFire page HTML.")

    except Exception as e:
        if logger:
            logger(f"MediaFire resolution failed: {e}")
        raise Exception(f"Failed to resolve MediaFire link. Error: {e}")


def convert_onedrive_link(url: str, logger=None):
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    })

    if not ("1drv.ms" in url or "onedrive.live.com" in url):
        return session, url

    try:
        if logger:
            logger("Resolving OneDrive public share...")

        resp = session.get(url, allow_redirects=True, timeout=30)
        final_url = resp.url

        if logger:
            logger(f"Resolved OneDrive Redirect: {final_url}")

        content_type = resp.headers.get("content-type", "").lower()

        if "text/html" not in content_type and "text/plain" not in content_type and resp.status_code == 200:
            return session, final_url

        page = resp.text
        decoded = html.unescape(page).replace("\\/", "/").replace("\\u0026", "&").replace("\\u003d", "=")
        decoded = unquote(decoded)

        patterns = [
            r'https://my\.microsoftpersonalcontent\.com/[^"\']+?/_layouts/15/download\.aspx\?[^"\']+',
            r'https:\\/\\/my\.microsoftpersonalcontent\.com\\/[^"\']+?/_layouts/15/download\.aspx\?[^"\']+',
            r'https%3A%2F%2Fmy\.microsoftpersonalcontent\.com%2F[^"\']+?%2F_layouts%2F15%2Fdownload\.aspx%3F[^"\']+',
        ]

        candidates = []
        for pattern in patterns:
            candidates.extend(re.findall(pattern, decoded, flags=re.IGNORECASE))

        generic_patterns = [
            r'https://[^"\']+/_layouts/15/download\.aspx\?[^"\']+',
            r'https:\\/\\/[^"\']+/_layouts/15/download\.aspx\?[^"\']+',
        ]

        for pattern in generic_patterns:
            candidates.extend(re.findall(pattern, decoded, flags=re.IGNORECASE))

        cleaned = []
        for candidate in candidates:
            candidate = candidate.replace("\\/", "/").replace("&amp;", "&").rstrip("\\")
            candidate = candidate.rstrip('"\'>),;}')
            if "download.aspx" in candidate.lower():
                cleaned.append(candidate)

        unique_candidates = list(dict.fromkeys(cleaned))
        tempauth_candidates = [c for c in unique_candidates if "tempauth=" in c.lower()]

        if tempauth_candidates:
            if logger:
                logger("Found temporary OneDrive direct-download URL (tempauth token acquired).")
            return session, tempauth_candidates[0]

        if unique_candidates:
            if logger:
                logger("Found OneDrive download endpoint, but no tempauth parameter was visible.")
            return session, unique_candidates[0]

        host_match = re.search(
            r'(https?:(?:\\/\\/|//)[^"\']*microsoftpersonalcontent\.com[^"\']*download\.aspx[^"\']*)',
            decoded,
            flags=re.IGNORECASE,
        )

        if host_match:
            candidate = host_match.group(1).replace("\\/", "/").replace("&amp;", "&")
            if logger:
                logger("Found OneDrive download URL via fallback parser.")
            return session, candidate

        raise Exception("OneDrive returned HTML page without direct download URL exposed.")

    except Exception:
        if logger:
            logger("OneDrive URL resolution failed.")
        raise


def format_bytes(n):
    if n is None:
        return "unknown size"
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def open_in_file_manager(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


class DisclaimerDialog(ctk.CTkToplevel):
    def __init__(self, master, on_ack, show_dont_show_again=True):
        super().__init__(master)
        self.title(f"{APP_NAME} — Disclaimer")
        self.geometry("480x380")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.on_ack = on_ack

        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(
            self,
            text="Before you continue",
            font=(FONT_FAMILY, 17, "bold"),
            text_color=COLORS["text"],
        ).pack(padx=22, pady=(22, 8), anchor="w")

        body = ctk.CTkTextbox(
            self,
            wrap="word",
            height=220,
            fg_color=COLORS["panel_alt"],
            border_color=COLORS["line"],
            border_width=1,
            text_color=COLORS["muted"],
            corner_radius=8,
        )
        body.pack(fill="both", expand=True, padx=22)
        body.insert("1.0", DISCLAIMER_TEXT)
        body.configure(state="disabled")

        self.dont_show_var = ctk.BooleanVar(value=False)
        if show_dont_show_again:
            ctk.CTkCheckBox(
                self,
                text="Don't show this again",
                variable=self.dont_show_var,
                text_color=COLORS["muted"],
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                checkmark_color=COLORS["accent_text"],
                border_color=COLORS["line"],
            ).pack(padx=22, pady=(14, 0), anchor="w")

        ctk.CTkButton(
            self,
            text="I Understand",
            command=self._acknowledge,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["accent_text"],
            font=(FONT_FAMILY, 13, "bold"),
            corner_radius=6,
        ).pack(padx=22, pady=18, fill="x")

        self.protocol("WM_DELETE_WINDOW", self._acknowledge)

    def _acknowledge(self):
        self.on_ack(self.dont_show_var.get())
        self.destroy()


class PakForge(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} — {APP_TAGLINE}")
        self.geometry("880x880")
        self.configure(fg_color=COLORS["bg"])

        self.config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), CONFIG_FILENAME
        )
        saved_config = self.load_config()

        default_downloads = os.path.join(os.getcwd(), "downloads")
        self.downloads_dir = ctk.StringVar(
            value=saved_config.get("downloads_dir", default_downloads)
        )

        self.replacements = saved_config.get("replacements", {})
        self.selected_packs = saved_config.get("selected_packs", {})

        self.console_paths = {}
        for console in CONSOLES:
            config_key = f"texture_path_{console['id']}"
            if console["id"] == "ps2":
                default_path = get_default_pcsx2_texture_path()
            else:
                default_path = os.path.expanduser(rf"~\Documents\{console['name']}\textures")
            self.console_paths[console["id"]] = ctk.StringVar(
                value=saved_config.get(config_key, default_path)
            )

        self._skip_disclaimer = saved_config.get("skip_disclaimer", False)

        self.game_cards = {}
        self.selected_game_id = None
        self.empty_state_label = None
        self.active_console_id = next(
            (c["id"] for c in CONSOLES if c["active"]), CONSOLES[0]["id"]
        )
        self.console_tab_buttons = {}
        self.active_cancellations = {}

        self.setup_ui()
        self.refresh_downloaded_list()

        if not self._skip_disclaimer:
            self.after(150, self.show_disclaimer)

    def get_console(self, console_id):
        return next(c for c in CONSOLES if c["id"] == console_id)

    def get_console_staging_dir(self, console_id, create_if_missing=False):
        path = os.path.join(self.downloads_dir.get(), console_id)
        if create_if_missing:
            os.makedirs(path, exist_ok=True)
        return path

    def get_selected_pack(self, game):
        game_id = game["game_id"]
        saved_pack_id = self.selected_packs.get(game_id)
        if saved_pack_id:
            for pack in game["packs"]:
                if pack["pack_id"] == saved_pack_id:
                    return pack
        return game["packs"][0]

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_config(self):
        data = {
            "downloads_dir": self.downloads_dir.get(),
            "skip_disclaimer": self._skip_disclaimer,
            "replacements": self.replacements,
            "selected_packs": self.selected_packs,
        }
        for console_id, var in self.console_paths.items():
            data[f"texture_path_{console_id}"] = var.get()
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def record_replacement_timestamp(self, game_id, pack_id):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.replacements[game_id] = {
            "active_pack_id": pack_id,
            "timestamp": now_str,
            "replaced": True
        }
        self.save_config()

    def show_disclaimer(self):
        def on_ack(dont_show_again):
            self._skip_disclaimer = bool(dont_show_again)
            self.save_config()

        DisclaimerDialog(self, on_ack=on_ack)

    def setup_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=18, pady=(18, 0))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left")

        logo_row = ctk.CTkFrame(title_box, fg_color="transparent")
        logo_row.pack(anchor="w")

        ctk.CTkLabel(
            logo_row, text="KW", font=("Consolas", 12, "bold"),
            fg_color=COLORS["accent"], text_color=COLORS["accent_text"],
            corner_radius=4, width=30, height=22,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            logo_row, text=APP_NAME, font=(FONT_FAMILY, 23, "bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        total_supported = sum(len(c["games"]) for c in CONSOLES if c["active"])
        ctk.CTkLabel(
            title_box,
            text=f"{APP_TAGLINE}  •  {total_supported} games supported  •  {APP_VERSION}",
            font=(FONT_FAMILY, 11), text_color=COLORS["muted"],
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            header_frame, text="Disclaimer", width=100, fg_color="transparent",
            hover_color=COLORS["panel"], border_width=1, border_color=COLORS["line"],
            text_color=COLORS["muted"], corner_radius=6, command=self.show_disclaimer,
        ).pack(side="right", pady=4)

        ctk.CTkButton(
            header_frame, text="Export Game List", width=140, fg_color="transparent",
            hover_color=COLORS["panel"], border_width=1, border_color=COLORS["line"],
            text_color=COLORS["muted"], corner_radius=6, command=self.export_games_json,
        ).pack(side="right", padx=(0, 8), pady=4)

        tabs_row1 = ctk.CTkFrame(self, fg_color="transparent")
        tabs_row1.pack(fill="x", padx=18, pady=(0, 4))
        tabs_row2 = ctk.CTkFrame(self, fg_color="transparent")
        tabs_row2.pack(fill="x", padx=18, pady=(0, 10))

        half = (len(CONSOLES) + 1) // 2
        for i, console in enumerate(CONSOLES):
            row = tabs_row1 if i < half else tabs_row2
            is_active = console["active"]
            is_selected = console["id"] == self.active_console_id
            btn = ctk.CTkButton(
                row,
                text=console["name"] if is_active else f"{console['name']} · Soon",
                height=28, corner_radius=6,
                font=(FONT_FAMILY, 11, "bold" if is_selected else "normal"),
                fg_color=COLORS["accent"] if is_selected else COLORS["panel"],
                hover_color=COLORS["accent_hover"] if is_active else COLORS["panel"],
                text_color=(
                    COLORS["accent_text"] if is_selected
                    else COLORS["text"] if is_active
                    else COLORS["muted"]
                ),
                border_width=0 if is_active else 1,
                border_color=COLORS["line"],
                state="normal" if is_active else "disabled",
                command=(lambda cid=console["id"]: self.switch_console(cid)) if is_active else None,
            )
            btn.pack(side="left", padx=(0, 6))
            self.console_tab_buttons[console["id"]] = btn

        path_frame = ctk.CTkFrame(
            self, fg_color=COLORS["panel"], border_color=COLORS["line"],
            border_width=1, corner_radius=10,
        )
        path_frame.pack(fill="x", padx=18, pady=(0, 14))

        active_console_name = self.get_console(self.active_console_id)["name"]
        self.texture_path_label = ctk.CTkLabel(
            path_frame, text=f"{active_console_name} Textures Path:",
            font=(FONT_FAMILY, 12, "bold"), text_color=COLORS["text"],
        )
        self.texture_path_label.pack(side="left", padx=12, pady=12)

        self.texture_path_entry = ctk.CTkEntry(
            path_frame, textvariable=self.console_paths[self.active_console_id], width=400,
            fg_color=COLORS["panel_alt"], border_color=COLORS["line"],
            text_color=COLORS["text"], corner_radius=6,
        )
        self.texture_path_entry.pack(side="left", padx=5, pady=12)
        ctk.CTkButton(
            path_frame, text="Browse", width=80, command=self.browse_texture_folder,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["accent_text"], corner_radius=6,
            font=(FONT_FAMILY, 12, "bold"),
        ).pack(side="left", padx=5, pady=12)
        ctk.CTkButton(
            path_frame, text="Open", width=70, fg_color="transparent",
            hover_color=COLORS["panel_alt"], border_width=1, border_color=COLORS["line"],
            text_color=COLORS["muted"], corner_radius=6,
            command=lambda: self.open_configured_folder(
                self.console_paths[self.active_console_id].get()
            ),
        ).pack(side="left", padx=(0, 12), pady=12)

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkLabel(
            search_frame, text="Search:", font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"]
        ).pack(side="left", padx=(0, 8))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_games)

        search_entry = ctk.CTkEntry(
            search_frame, textvariable=self.search_var,
            placeholder_text="Search by title or Game ID...",
            fg_color=COLORS["panel"], border_color=COLORS["line"],
            text_color=COLORS["text"], corner_radius=6,
        )
        search_entry.pack(side="left", fill="x", expand=True)

        self.games_count_label = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["muted"], anchor="w",
        )
        self.games_count_label.pack(fill="x", padx=20, pady=(0, 6))

        self.scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["panel"], border_color=COLORS["line"],
            border_width=1, corner_radius=10,
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        self.rebuild_game_cards()

        staging_frame = ctk.CTkFrame(
            self, fg_color=COLORS["panel"], border_color=COLORS["line"],
            border_width=1, corner_radius=10,
        )
        staging_frame.pack(fill="x", padx=18, pady=(0, 14))

        stg_header = ctk.CTkFrame(staging_frame, fg_color="transparent")
        stg_header.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkLabel(
            stg_header, text="Downloads Staging Folder:",
            font=(FONT_FAMILY, 11, "bold"), text_color=COLORS["text"],
        ).pack(side="left")

        ctk.CTkEntry(
            stg_header, textvariable=self.downloads_dir, width=360,
            fg_color=COLORS["panel_alt"], border_color=COLORS["line"],
            text_color=COLORS["text"], corner_radius=6,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            stg_header, text="Browse", width=80, command=self.browse_staging_folder,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["accent_text"], corner_radius=6,
            font=(FONT_FAMILY, 12, "bold"),
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            stg_header, text="Open", width=70, fg_color="transparent",
            hover_color=COLORS["panel_alt"], border_width=1, border_color=COLORS["line"],
            text_color=COLORS["muted"], corner_radius=6,
            command=lambda: self.open_configured_folder(
                self.get_console_staging_dir(self.active_console_id, create_if_missing=False)
            ),
        ).pack(side="left")

        self.downloaded_files_box = ctk.CTkTextbox(
            staging_frame, height=50, fg_color=COLORS["panel_alt"],
            border_color=COLORS["line"], border_width=1,
            text_color=COLORS["muted"], corner_radius=6,
        )
        self.downloaded_files_box.pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkLabel(
            staging_frame,
            text=(
                "Cached texture packs for the selected console (subfolders dynamically "
                "created upon download) — for confirming a download landed, or clearing space."
            ),
            font=(FONT_FAMILY, 9), text_color=COLORS["muted"],
        ).pack(anchor="w", padx=12, pady=(0, 12))

        debug_frame = ctk.CTkFrame(
            self, fg_color=COLORS["panel"], border_color=COLORS["line"],
            border_width=1, corner_radius=10,
        )
        debug_frame.pack(fill="x", padx=18, pady=(0, 6))

        ctk.CTkLabel(
            debug_frame, text="Debug Console Output:",
            font=(FONT_FAMILY, 11, "bold"), text_color=COLORS["accent"],
        ).pack(anchor="w", padx=12, pady=(10, 0))

        self.debug_box = ctk.CTkTextbox(
            debug_frame, height=120, font=("Consolas", 10),
            fg_color=COLORS["panel_alt"], border_color=COLORS["line"],
            border_width=1, text_color=COLORS["muted"], corner_radius=6,
        )
        self.debug_box.pack(fill="x", padx=12, pady=(6, 12))

        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=18, pady=(0, 14))
        ctk.CTkLabel(
            footer_frame,
            text=(
                f"{APP_NAME} links to community-made texture packs hosted by "
                "third parties — it doesn't host or own that content. "
                "Click \"Disclaimer\" above for details."
            ),
            font=(FONT_FAMILY, 9), text_color=COLORS["muted"],
            wraplength=800, justify="left",
        ).pack(anchor="w")

    def filter_games(self, *args):
        query = self.search_var.get().lower().strip()
        console = self.get_console(self.active_console_id)
        visible = 0
        for game in console["games"]:
            card = self.game_cards.get(game["game_id"])
            if not card:
                continue

            match_title = query in game["title"].lower()
            match_id = query in game["game_id"].lower()

            if match_title or match_id:
                card.pack(fill="x", padx=8, pady=6)
                visible += 1
            else:
                card.pack_forget()

        self.update_games_count_label(visible_override=visible if query else None)

    def switch_console(self, console_id):
        console = self.get_console(console_id)
        if not console["active"] or console_id == self.active_console_id:
            return

        self.active_console_id = console_id
        for cid, btn in self.console_tab_buttons.items():
            c = self.get_console(cid)
            if not c["active"]:
                continue
            selected = cid == console_id
            btn.configure(
                fg_color=COLORS["accent"] if selected else COLORS["panel"],
                text_color=COLORS["accent_text"] if selected else COLORS["text"],
                font=(FONT_FAMILY, 11, "bold" if selected else "normal"),
            )

        self.texture_path_label.configure(text=f"{console['name']} Textures Path:")
        self.texture_path_entry.configure(textvariable=self.console_paths[console_id])

        self.search_var.set("")
        self.rebuild_game_cards()
        self.refresh_downloaded_list()

    def rebuild_game_cards(self):
        for card in self.game_cards.values():
            card.destroy()
        self.game_cards = {}
        self.selected_game_id = None

        if self.empty_state_label is not None:
            self.empty_state_label.destroy()
            self.empty_state_label = None

        console = self.get_console(self.active_console_id)
        sorted_games = sorted(console["games"], key=lambda x: x["title"].lower())

        if not sorted_games:
            self.empty_state_label = ctk.CTkLabel(
                self.scroll_frame,
                text=f"No {console['name']} texture packs yet — check back soon.",
                font=(FONT_FAMILY, 12), text_color=COLORS["muted"],
            )
            self.empty_state_label.pack(pady=30)
        else:
            for game in sorted_games:
                self.create_game_card(game, self.active_console_id)

        self.update_games_count_label()

    def update_games_count_label(self, visible_override=None):
        console = self.get_console(self.active_console_id)
        total = len(console["games"])
        if visible_override is not None:
            text = f"{console['name']} — showing {visible_override} of {total} supported games"
        else:
            text = f"{console['name']} — {total} supported game" + ("" if total == 1 else "s")
        self.games_count_label.configure(text=text)

    def export_games_json(self):
        consoles_export = []
        for console in CONSOLES:
            games_export = []
            for g in console["games"]:
                packs = g.get("packs", [])
                primary_pack = packs[0] if packs else {}
                games_export.append({
                    "game_id": g["game_id"],
                    "title": g["title"],
                    "cover_url": g.get("cover_url", ""),
                    "credit_name": primary_pack.get("credit_name", "Pack creator not yet credited"),
                    "credit_url": primary_pack.get("credit_url"),
                    "packs_count": len(packs)
                })
            consoles_export.append({
                "id": console["id"],
                "name": console["name"],
                "active": console["active"],
                "games": games_export,
            })

        payload = {
            "app": APP_NAME,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z",
            "total_supported": sum(len(c["games"]) for c in consoles_export if c["active"]),
            "consoles": consoles_export,
        }

        export_dir = os.path.dirname(os.path.abspath(__file__))
        export_path = os.path.join(export_dir, "pakforge-games.json")

        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            self.log_debug(f"Exported game list for the website to: {export_path}")
            open_in_file_manager(export_dir)
        except Exception as e:
            self.log_debug(f"Export failed: {e}")

    def log_debug(self, message: str):
        self.after(0, self._append_debug, message)

    def _append_debug(self, message: str):
        self.debug_box.insert("end", message + "\n")
        self.debug_box.see("end")

    def browse_texture_folder(self):
        console_name = self.get_console(self.active_console_id)["name"]
        folder = ctk.filedialog.askdirectory(title=f"Select {console_name} Textures Directory")
        if folder:
            self.console_paths[self.active_console_id].set(folder)
            self.save_config()
            self.rebuild_game_cards()

    def browse_staging_folder(self):
        folder = ctk.filedialog.askdirectory(title="Select Downloads Staging Directory")
        if folder:
            self.downloads_dir.set(folder)
            self.refresh_downloaded_list()
            self.save_config()
            self.rebuild_game_cards()

    def open_configured_folder(self, path):
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            self.log_debug(f"Could not create/open folder '{path}': {e}")
            return
        open_in_file_manager(path)

    def refresh_downloaded_list(self):
        self.downloaded_files_box.delete("1.0", "end")
        target_path = self.get_console_staging_dir(self.active_console_id, create_if_missing=False)

        if os.path.exists(target_path):
            files = os.listdir(target_path)
            if not files:
                self.downloaded_files_box.insert("1.0", "No downloaded texture packs cached.")
            else:
                self.downloaded_files_box.insert("1.0", "\n".join(files))
        else:
            self.downloaded_files_box.insert("1.0", "No downloads directory created yet.")

    def select_game(self, game_id):
        self.selected_game_id = game_id
        for gid, card in self.game_cards.items():
            if gid == game_id:
                card.configure(border_color=COLORS["accent"], border_width=2)
            else:
                card.configure(border_color=COLORS["line"], border_width=1)

    def check_pack_status(self, game_id, pack_id, console_id):
        staging_dir = self.get_console_staging_dir(console_id, create_if_missing=False)
        has_zip = False
        if os.path.exists(staging_dir):
            for ext in [".zip", ".7z", ".rar"]:
                if os.path.isfile(os.path.join(staging_dir, f"{game_id}_{pack_id}{ext}")):
                    has_zip = True
                    break

        texture_path = self.console_paths[console_id].get()
        extracted_dir = os.path.join(texture_path, game_id, "replacement")
        
        meta = self.replacements.get(game_id, {})
        has_extracted = (
            os.path.isdir(extracted_dir) 
            and len(os.listdir(extracted_dir)) > 0 
            and meta.get("active_pack_id") == pack_id
        )

        return has_zip, has_extracted

    def create_game_card(self, game, console_id):
        cover_url = game["cover_url"].format(game_id=game["game_id"])

        card = ctk.CTkFrame(
            self.scroll_frame, fg_color=COLORS["panel_alt"],
            border_color=COLORS["line"], border_width=1, corner_radius=8,
        )
        card.pack(fill="x", padx=8, pady=6)
        self.game_cards[game["game_id"]] = card
        card.bind("<Button-1>", lambda e, gid=game["game_id"]: self.select_game(gid))

        img_label = ctk.CTkLabel(
            card, text="[Loading...]", width=60, height=60,
            fg_color=COLORS["accent"], text_color=COLORS["accent_text"],
            corner_radius=6, font=(FONT_FAMILY, 9),
        )
        img_label.pack(side="left", padx=12, pady=14)
        img_label.bind("<Button-1>", lambda e, gid=game["game_id"]: self.select_game(gid))
        threading.Thread(
            target=self.load_cover_art, args=(cover_url, img_label), daemon=True
        ).start()

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10)
        info_frame.bind("<Button-1>", lambda e, gid=game["game_id"]: self.select_game(gid))

        title_label = ctk.CTkLabel(
            info_frame, text=game["title"], font=(FONT_FAMILY, 15, "bold"),
            text_color=COLORS["text"], anchor="w", justify="left", wraplength=380,
        )
        title_label.pack(fill="x")
        title_label.bind("<Button-1>", lambda e, gid=game["game_id"]: self.select_game(gid))

        id_label = ctk.CTkLabel(
            info_frame, text=f"ID: {game['game_id']}",
            font=(FONT_FAMILY, 11), text_color=COLORS["muted"], anchor="w",
        )
        id_label.pack(fill="x")
        id_label.bind("<Button-1>", lambda e, gid=game["game_id"]: self.select_game(gid))

        # Dynamic multi-pack dropdown or single provider label
        packs = game.get("packs", [])
        active_pack = self.get_selected_pack(game)

        credit_line = ctk.CTkFrame(info_frame, fg_color="transparent")
        credit_line.pack(fill="x", pady=(4, 0))
        credit_line.bind("<Button-1>", lambda e, gid=game["game_id"]: self.select_game(gid))

        credit_label = ctk.CTkLabel(
            credit_line,
            text="",
            font=(FONT_FAMILY, 10),
            anchor="w", justify="left", wraplength=380,
        )

        def update_credit_display(selected_pack):
            c_name = selected_pack.get("credit_name", "Pack creator not yet credited")
            c_url = selected_pack.get("credit_url")
            
            credit_label.configure(
                #text=f"HD pack by {c_name}" + (" ↗" if c_url else ""),
                text=f"{c_name}" + (" ↗" if c_url else ""),
                font=(FONT_FAMILY, 10, "underline" if c_url else "normal"),
                text_color=COLORS["accent"] if c_url else COLORS["muted"],
                cursor="hand2" if c_url else "arrow"
            )
            
            credit_label.unbind("<Button-1>")
            if c_url:
                credit_label.bind("<Button-1>", lambda e, url=c_url: (webbrowser.open(url), "break")[1])
            else:
                credit_label.bind("<Button-1>", lambda e, gid=game["game_id"]: self.select_game(gid))

        if len(packs) > 1:
            pack_names = [p["pack_name"] for p in packs]
            pack_var = ctk.StringVar(value=active_pack["pack_name"])

            def on_pack_change(selected_name):
                for p in packs:
                    if p["pack_name"] == selected_name:
                        self.selected_packs[game["game_id"]] = p["pack_id"]
                        self.save_config()
                        update_credit_display(p)
                        self.refresh_card_actions(game, console_id, progress_bar, status_label, btn_container)
                        break

            dropdown = ctk.CTkOptionMenu(
                info_frame,
                values=pack_names,
                variable=pack_var,
                command=on_pack_change,
                height=24,
                font=(FONT_FAMILY, 10),
                fg_color=COLORS["panel"],
                button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
                dropdown_fg_color=COLORS["panel_alt"],
                dropdown_hover_color=COLORS["line"],
                text_color=COLORS["text"],
            )
            dropdown.pack(anchor="w", pady=(2, 2))

        update_credit_display(active_pack)
        credit_label.pack(side="left")

        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(side="right", padx=12)

        has_zip, has_extracted = self.check_pack_status(game["game_id"], active_pack["pack_id"], console_id)

        status_label = ctk.CTkLabel(
            action_frame, text="", font=(FONT_FAMILY, 10),
            width=150, wraplength=150, justify="center",
        )
        status_label.pack(pady=(0, 2))

        progress_bar = ctk.CTkProgressBar(
            action_frame, width=140, height=8,
            progress_color=COLORS["accent"], fg_color=COLORS["bg"],
            border_color=COLORS["line"], border_width=1,
        )
        progress_bar.pack(pady=6)

        btn_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_container.pack(pady=2)

        self.refresh_card_actions(game, console_id, progress_bar, status_label, btn_container)

    def refresh_card_actions(self, game, console_id, progress_bar, status_label, btn_container):
        active_pack = self.get_selected_pack(game)
        has_zip, has_extracted = self.check_pack_status(game["game_id"], active_pack["pack_id"], console_id)

        meta = self.replacements.get(game["game_id"], {})
        ts = meta.get("timestamp")

        if has_extracted and ts:
            status_text = f"Replaced!\n({ts})"
        elif has_extracted:
            status_text = "Replaced!"
        elif has_zip:
            status_text = "Downloaded!"
        else:
            status_text = "Ready"

        status_color = COLORS["mint"] if (has_extracted or has_zip) else COLORS["muted"]
        status_label.configure(text=status_text, text_color=status_color)
        progress_bar.set(1.0 if (has_zip or has_extracted) else 0)

        if has_zip or has_extracted:
            self.show_action_buttons(game, console_id, progress_bar, status_label, btn_container)
        else:
            self.reset_download_button(game, console_id, progress_bar, status_label, btn_container)

    def load_cover_art(self, url, label_widget):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                raw_data = response.read()
            image = Image.open(BytesIO(raw_data)).resize((64, 64))
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(64, 64))
            label_widget.configure(image=ctk_image, text="")
        except Exception:
            label_widget.configure(text="No Cover")

    def start_download(self, game, console_id, progress_bar, status_label, btn_container):
        self.select_game(game["game_id"])
        
        cancel_event = threading.Event()
        self.active_cancellations[game["game_id"]] = cancel_event

        for child in btn_container.winfo_children():
            child.destroy()

        cancel_btn = ctk.CTkButton(
            btn_container,
            text="Cancel Download",
            width=140,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            text_color=COLORS["text"],
            font=(FONT_FAMILY, 11, "bold"),
            corner_radius=6,
            command=lambda: self.cancel_download(game["game_id"]),
        )
        cancel_btn.pack()

        threading.Thread(
            target=self.download_task,
            args=(game, console_id, progress_bar, status_label, btn_container, cancel_event),
            daemon=True,
        ).start()

    def cancel_download(self, game_id):
        if game_id in self.active_cancellations:
            self.log_debug(f"User requested download cancellation for {game_id}...")
            self.active_cancellations[game_id].set()

    def download_task(self, game, console_id, progress_bar, status_label, btn_container, cancel_event):
        status_label.configure(text="Connecting...", text_color=COLORS["text"])
        progress_bar.set(0)

        active_pack = self.get_selected_pack(game)
        url = active_pack["download_url"]
        
        ext = ".zip"
        if ".7z" in url.lower():
            ext = ".7z"
        elif ".rar" in url.lower():
            ext = ".rar"

        staging_dir = self.get_console_staging_dir(console_id, create_if_missing=True)
        local_file = os.path.join(staging_dir, f"{game['game_id']}_{active_pack['pack_id']}{ext}")

        self.log_debug(f"\n--- Download Task Started: {game['title']} ({active_pack['pack_name']}) ---")
        self.log_debug(f"Input URL: {url}")

        try:
            if "mega.nz" in url or "mega.co.nz" in url:
                status_label.configure(text="Downloading (MEGA)...")
                handle_mega_download(
                    url,
                    local_file,
                    logger=self.log_debug,
                    progress_callback=lambda p: progress_bar.set(p),
                    cancel_event=cancel_event,
                )
            else:
                if "mediafire.com" in url:
                    direct_url = resolve_mediafire_link(url, logger=self.log_debug)
                    session = requests.Session()
                elif "1drv.ms" in url or "onedrive.live.com" in url:
                    session, direct_url = convert_onedrive_link(url, logger=self.log_debug)
                else:
                    session = requests.Session()
                    direct_url = url

                self.log_debug(f"Target Download URL: {direct_url}")
                response = session.get(direct_url, stream=True, timeout=60, allow_redirects=True)

                if response.status_code != 200:
                    raise Exception(f"HTTP Error {response.status_code} while downloading payload.")

                total_length = response.headers.get("content-length")

                with open(local_file, "wb") as f:
                    if total_length is None:
                        status_label.configure(text="Downloading...")
                        for chunk in response.iter_content(chunk_size=32768):
                            if cancel_event.is_set():
                                raise InterruptedError("Download canceled by user.")
                            if chunk:
                                f.write(chunk)
                        progress_bar.set(0.5)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        total_str = format_bytes(total_length)
                        for chunk in response.iter_content(chunk_size=32768):
                            if cancel_event.is_set():
                                raise InterruptedError("Download canceled by user.")
                            if chunk:
                                dl += len(chunk)
                                f.write(chunk)
                                fraction = dl / total_length
                                progress_bar.set(fraction)
                                status_label.configure(
                                    text=f"Downloading... {int(fraction * 100)}% "
                                    f"({format_bytes(dl)}/{total_str})"
                                )

            self.refresh_downloaded_list()
            self.log_debug(f"File size on disk: {os.path.getsize(local_file)} bytes")

            progress_bar.set(1.0)
            status_label.configure(text="Downloaded!", text_color=COLORS["mint"])

            self.after(0, lambda: self.show_action_buttons(game, console_id, progress_bar, status_label, btn_container))

        except InterruptedError as cancel_msg:
            status_label.configure(text="Canceled", text_color=COLORS["muted"])
            self.log_debug(f"Task status: {cancel_msg}")
            if os.path.exists(local_file):
                try:
                    os.remove(local_file)
                except Exception:
                    pass
            self.after(0, lambda: self.reset_download_button(game, console_id, progress_bar, status_label, btn_container))

        except Exception as err:
            status_label.configure(text="Failed!", text_color=COLORS["danger"])
            self.log_debug(f"ERROR: {err}")
            self.log_debug(traceback.format_exc())
            if os.path.exists(local_file):
                try:
                    os.remove(local_file)
                except Exception:
                    pass
            self.after(0, lambda: self.reset_download_button(game, console_id, progress_bar, status_label, btn_container))

        finally:
            self.active_cancellations.pop(game["game_id"], None)

    def reset_download_button(self, game, console_id, progress_bar, status_label, btn_container):
        for child in btn_container.winfo_children():
            child.destroy()

        download_btn = ctk.CTkButton(
            btn_container,
            text="Download Textures",
            width=140,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["accent_text"],
            font=(FONT_FAMILY, 12, "bold"),
            corner_radius=6,
            command=lambda: self.start_download(game, console_id, progress_bar, status_label, btn_container),
        )
        download_btn.pack()

    def show_action_buttons(self, game, console_id, progress_bar, status_label, btn_container):
        for child in btn_container.winfo_children():
            child.destroy()

        active_pack = self.get_selected_pack(game)
        has_zip, has_extracted = self.check_pack_status(game["game_id"], active_pack["pack_id"], console_id)

        delete_btn_text = "Remove Staging" if has_extracted else "Delete Textures"

        delete_btn = ctk.CTkButton(
            btn_container,
            text=delete_btn_text,
            width=110,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            text_color=COLORS["text"],
            font=(FONT_FAMILY, 11, "bold"),
            corner_radius=6,
            command=lambda: self.delete_textures(game, console_id, progress_bar, status_label, btn_container),
        )
        delete_btn.pack(side="left", padx=2)

        if has_zip:
            replace_btn_text = "Replace Again" if has_extracted else "Replace Textures"
            replace_btn = ctk.CTkButton(
                btn_container,
                text=replace_btn_text,
                width=110,
                fg_color=COLORS["mint"],
                hover_color=COLORS["mint_hover"],
                text_color=COLORS["accent_text"],
                font=(FONT_FAMILY, 11, "bold"),
                corner_radius=6,
                command=lambda: self.replace_textures(game, console_id, progress_bar, status_label),
            )
            replace_btn.pack(side="left", padx=2)

    def delete_textures(self, game, console_id, progress_bar, status_label, btn_container):
        active_pack = self.get_selected_pack(game)
        staging_dir = self.get_console_staging_dir(console_id, create_if_missing=False)
        
        if os.path.exists(staging_dir):
            for ext in [".zip", ".7z", ".rar"]:
                target_file = os.path.join(staging_dir, f"{game['game_id']}_{active_pack['pack_id']}{ext}")
                if os.path.exists(target_file):
                    try:
                        os.remove(target_file)
                        self.log_debug(f"Deleted staging file: {target_file}")
                    except Exception as e:
                        self.log_debug(f"Delete Error: {e}")

        self.refresh_downloaded_list()
        
        has_zip, has_extracted = self.check_pack_status(game["game_id"], active_pack["pack_id"], console_id)

        if has_extracted:
            meta = self.replacements.get(game["game_id"], {})
            ts = meta.get("timestamp")
            status_text = f"Replaced!\n({ts})" if ts else "Replaced!"
            status_label.configure(text=status_text, text_color=COLORS["mint"])
            self.show_action_buttons(game, console_id, progress_bar, status_label, btn_container)
        else:
            progress_bar.set(0)
            status_label.configure(text="Ready", text_color=COLORS["text"])
            self.reset_download_button(game, console_id, progress_bar, status_label, btn_container)

    def replace_textures(self, game, console_id, progress_bar, status_label):
        threading.Thread(
            target=self.extract_task,
            args=(game, console_id, progress_bar, status_label),
            daemon=True,
        ).start()

    def extract_task(self, game, console_id, progress_bar, status_label):
        status_label.configure(text="Extracting...", text_color=COLORS["text"])
        active_pack = self.get_selected_pack(game)
        staging_dir = self.get_console_staging_dir(console_id, create_if_missing=False)
        
        local_archive = None
        if os.path.exists(staging_dir):
            for ext in [".zip", ".7z", ".rar"]:
                candidate = os.path.join(staging_dir, f"{game['game_id']}_{active_pack['pack_id']}{ext}")
                if os.path.exists(candidate):
                    local_archive = candidate
                    break

        if not local_archive:
            status_label.configure(text="File Missing!", text_color=COLORS["danger"])
            self.log_debug("Extraction failed: Staging archive missing.")
            return

        texture_path = self.console_paths[console_id].get()
        target_dir = os.path.join(texture_path, game["game_id"], "replacement")

        try:
            os.makedirs(target_dir, exist_ok=True)
            self.log_debug(f"Extracting archive into target directory: {target_dir}")

            extracted_count = 0
            if zipfile.is_zipfile(local_archive):
                with zipfile.ZipFile(local_archive, "r") as zip_ref:
                    for member in zip_ref.infolist():
                        if member.is_dir():
                            continue
                        filename = os.path.basename(member.filename)
                        if filename:
                            dest_path = os.path.join(target_dir, filename)
                            with zip_ref.open(member) as source, open(dest_path, "wb") as target:
                                shutil.copyfileobj(source, target)
                            extracted_count += 1
            else:
                shutil.unpack_archive(local_archive, target_dir)
                extracted_count = len(os.listdir(target_dir))

            self.record_replacement_timestamp(game["game_id"], active_pack["pack_id"])
            ts = self.replacements[game["game_id"]]["timestamp"]

            status_label.configure(text=f"Replaced!\n({ts})", text_color=COLORS["mint"])
            self.log_debug(
                f"Extraction and replacement completed successfully! "
                f"({extracted_count} files written)"
            )

            self.after(0, lambda: self.show_open_folder_button(target_dir, status_label))

            btn_container = status_label.master.nametowidget(
                status_label.master.winfo_children()[-1]
            )
            self.after(
                0,
                lambda: self.show_action_buttons(
                    game, console_id, progress_bar, status_label, btn_container
                ),
            )

        except Exception as err:
            status_label.configure(text="Extract Failed!", text_color=COLORS["danger"])
            self.log_debug(f"Extraction Error [{game['game_id']}]: {err}")

    def show_open_folder_button(self, target_dir, status_label):
        for widget in status_label.master.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Open Folder":
                widget.destroy()

        link = ctk.CTkButton(
            status_label.master,
            text="Open Folder",
            width=90, height=20,
            font=(FONT_FAMILY, 9),
            fg_color="transparent",
            hover_color=COLORS["panel"],
            border_width=1, border_color=COLORS["line"],
            text_color=COLORS["muted"], corner_radius=6,
            command=lambda: open_in_file_manager(target_dir),
        )
        link.pack(pady=(2, 0))


if __name__ == "__main__":
    app = PakForge()
    app.mainloop()