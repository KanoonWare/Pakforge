import base64
import html
import os
import re

from urllib.parse import unquote
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from utils import format_bytes


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