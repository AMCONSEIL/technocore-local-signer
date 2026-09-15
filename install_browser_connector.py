"""Install a per-user Chromium native host; never opens a private key."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

from browser_host import HOST_NAME

APP_DIR = Path(__file__).resolve().parent
REGISTRY = 'Software\\Google\\Chrome\\NativeMessagingHosts\\' + HOST_NAME


def setup(extension_id, folder=APP_DIR, executable=None, register=True):
    if re.fullmatch(r"[a-p]{32}", extension_id) is None:
        raise ValueError("Paste the 32-letter extension ID from brave://extensions or chrome://extensions.")
    folder = folder.resolve()
    python = Path(executable or sys.executable).resolve()
    if python.name.lower() == "pythonw.exe":
        python = python.with_name("python.exe")
    script = folder / "browser_host.py"
    if not python.is_file() or not script.is_file():
        raise ValueError("Python or browser_host.py is missing.")
    # These paths become quoted literals in a generated Windows command file.
    if any(c in str(path) for path in (folder, python) for c in '%!&^"<>\r\n'):
        raise ValueError("Move the app to a folder without shell metacharacters.")
    native = folder / ".native"
    manifest_path = native / "host.json"
    if register:
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY) as key:
                old = winreg.QueryValue(key, None)
            if Path(old).resolve() != manifest_path.resolve():
                raise ValueError("Another installation is registered. Uninstall that connector first.")
        except FileNotFoundError:
            pass
    manifest = {
        "name": HOST_NAME, "description": "Technocore local signing with manual approval",
        "path": str(native / "host.cmd"), "type": "stdio",
        "allowed_origins": [f"chrome-extension://{extension_id}/"],
    }
    native.mkdir(exist_ok=True)
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("allowed_origins") != manifest["allowed_origins"]:
            raise ValueError("This app folder already allows another extension ID. Review it before changing.")
    command = f'@echo off\r\n@chcp 65001 >nul\r\n"{python}" -B "{script}" %*\r\n'
    (native / "host.cmd").write_bytes(command.encode("utf-8"))
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if register:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(manifest_path))
    return manifest_path


def uninstall(folder=APP_DIR):
    import winreg
    expected = (folder / ".native" / "host.json").resolve()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY) as key:
            actual = Path(winreg.QueryValue(key, None)).resolve()
        if actual != expected:
            raise ValueError("Registration points to another app; left unchanged.")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REGISTRY)
    except FileNotFoundError:
        pass
    # Files and receipts are deliberately preserved for rollback.


def configure_if_missing(root):
    from tkinter import simpledialog, filedialog
    path = APP_DIR / "config.local.json"
    if path.exists():
        config = json.loads(path.read_text(encoding="utf-8"))
        if config.get("did") and config.get("key_path"):
            return True
        raise ValueError("Existing local configuration is incomplete; it was not overwritten.")
    did = simpledialog.askstring("Public DID / DID public", "Existing did:key:z6Mk… / DID existant :", parent=root)
    if did is None:
        return False
    did = did.strip()
    if re.fullmatch(r"did:key:z6Mk[1-9A-HJ-NP-Za-km-z]{44}", did) is None:
        raise ValueError("Invalid Ed25519 public DID.")
    key_path = filedialog.askopenfilename(parent=root, title="Select encrypted PEM / Choisir le PEM chiffré", filetypes=[("Encrypted PEM", "*.pem")])
    if not key_path:
        return False
    with path.open("x", encoding="utf-8") as out:
        json.dump({"did": did, "key_path": key_path}, out, indent=2)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extension-id")
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    if os.name != "nt":
        raise SystemExit("This installer currently supports Windows only.")
    if args.uninstall:
        uninstall()
        print("Connector unregistered. Files, identity and receipts retained.")
        return
    if args.extension_id:
        print(setup(args.extension_id))
        return
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    root = tk.Tk()
    root.withdraw()
    try:
        extension_id = simpledialog.askstring(
            "Connect Brave or Chrome / Connecter Brave ou Chrome",
            "Open brave://extensions or chrome://extensions, enable Developer mode, load the extension folder.\n"
            "Ouvrez brave://extensions ou chrome://extensions, activez le mode développeur, chargez le dossier extension.\n\n"
            "Paste its 32-letter ID / Collez son identifiant de 32 lettres :", parent=root)
        if extension_id is None:
            return
        extension_id = extension_id.strip()
        if re.fullmatch(r"[a-p]{32}", extension_id) is None:
            raise ValueError("Invalid extension ID / Identifiant d'extension invalide.")
        if not configure_if_missing(root):
            return
        setup(extension_id)
        messagebox.showinfo("Ready / Prêt", "Reload Technocore, then click Connect local signer.\nRechargez Technocore puis cliquez sur Connecter le signataire local.", parent=root)
    except Exception as exc:
        messagebox.showerror("Connector setup / Installation", str(exc), parent=root)
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
