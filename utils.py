import json
import os
import subprocess
import sys

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