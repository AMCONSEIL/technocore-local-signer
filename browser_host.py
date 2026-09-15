"""One manually approved publication per native-messaging invocation."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import struct
import sys

from signature_locale import canonical, publish

APP_DIR = Path(__file__).resolve().parent
MAX_INPUT = 32768
HOST_NAME = "org.amconseil.technocore_signer"


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def read_exact(stream, size):
    data = bytearray()
    while len(data) < size:
        chunk = stream.read(size - len(data))
        if not chunk:
            raise ValueError("Incomplete native message")
        data.extend(chunk)
    return bytes(data)


def read_message(stream):
    size = struct.unpack("=I", read_exact(stream, 4))[0]
    if not 0 < size <= MAX_INPUT:
        raise ValueError("Invalid native message size")
    return json.loads(read_exact(stream, size).decode("utf-8"), object_pairs_hook=no_duplicates)


def write_message(stream, message):
    raw = json.dumps(message, ensure_ascii=False).encode("utf-8")
    stream.write(struct.pack("=I", len(raw)) + raw)
    stream.flush()


def validate_request(request):
    if not isinstance(request, dict):
        raise ValueError("Invalid request")
    if request == {"op": "profile"}:
        return request
    if set(request) != {"op", "room", "text", "language"} or request["op"] != "publish":
        raise ValueError("Unsupported request")
    if request["language"] not in ("en", "fr"):
        raise ValueError("Unsupported language")
    if not isinstance(request["room"], str) or not isinstance(request["text"], str):
        raise ValueError("Invalid room or text")
    if len(request["text"]) > 4096:
        raise ValueError("Message too long")
    text, _ = canonical(request["room"], "1", request["text"])
    return {**request, "text": text}


def approve_locally(room, text, did, language):
    # No PEM access: this window returns a password only after explicit approval.
    import tkinter as tk
    from tkinter import ttk, simpledialog

    french = language == "fr"
    root = tk.Tk()
    root.title("Technocore — signature locale" if french else "Technocore — local signing")
    root.geometry("760x440")
    root.minsize(640, 300)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    title = ("Vérifiez le salon, le DID et le texte avant de signer." if french else
             "Check the room, DID and message before signing.")
    ttk.Label(root, text=f"{title}\nhttps://technocore.chat/r/{room}\n{did}", wraplength=720).grid(row=0, column=0, sticky="ew", padx=16, pady=12)
    view = tk.Text(root, wrap="word", height=1, font=("Segoe UI", 11))
    view.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
    view.insert("1.0", text)
    view.configure(state="disabled")
    footer = ttk.Frame(root, padding=12)
    footer.grid(row=2, column=0, sticky="ew")
    answer = [None]

    def unlock():
        value = simpledialog.askstring(
            "Déverrouillage local" if french else "Local unlock",
            "Passphrase du PEM (reste sur ce PC) :" if french else "PEM passphrase (stays on this PC):",
            show="*", parent=root)
        if value:
            answer[0] = value
            root.destroy()

    ttk.Button(footer, text="Annuler" if french else "Cancel", command=root.destroy).pack(side="left")
    ttk.Button(footer, text="Valider et signer" if french else "Confirm and sign", command=unlock).pack(side="right")
    root.lift()
    root.mainloop()
    return answer[0]


def handle(request, config, receipts, approve=approve_locally, publisher=publish):
    request = validate_request(request)
    did = config.get("did", "")
    if not isinstance(did, str) or re.fullmatch(r"did:key:z6Mk[1-9A-HJ-NP-Za-km-z]{44}", did) is None:
        return {"ok": False, "code": "configuration", "message": "Configure your existing public DID in the local app first."}
    if request["op"] == "profile":
        return {"ok": True, "did": did, "version": "1.1.0"}
    path = config.get("key_path")
    if not isinstance(path, str) or not path:
        return {"ok": False, "code": "configuration", "message": "Configure the encrypted PEM path locally first."}
    receipts.mkdir(parents=True, exist_ok=True)
    lock = receipts / "browser-request.lock"
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return {"ok": False, "code": "busy", "message": "Another local approval is open, or a previous session left a lock. Check the local app."}
    os.close(fd)
    password = None
    try:
        password = approve(request["room"], request["text"], did, request["language"])
        if not password:
            return {"ok": False, "code": "cancelled", "message": "Cancelled. Nothing was sent."}
        _, posted = publisher(Path(path), password, did, request["room"], request["text"], receipts)
        return {"ok": True, "did": did, "room": request["room"], "seq": posted["seq"]}
    except Exception:
        # Never return local paths, config, passphrases or exception internals to a page.
        return {"ok": False, "code": "unconfirmed", "message": "Publication not confirmed. Check local receipts before retrying; do not resend automatically."}
    finally:
        password = None
        lock.unlink(missing_ok=True)


def main():
    if os.name == "nt":
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    try:
        manifest = json.loads((APP_DIR / ".native" / "host.json").read_text(encoding="utf-8"))
        caller = sys.argv[1] if len(sys.argv) > 1 else ""
        if caller not in manifest["allowed_origins"] or not re.fullmatch(r"chrome-extension://[a-p]{32}/", caller):
            raise ValueError("Unauthorized extension")
        request = validate_request(read_message(sys.stdin.buffer))
        path = APP_DIR / "config.local.json"
        config = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        result = handle(request, config, APP_DIR / "recus")
    except Exception:
        result = {"ok": False, "code": "host_error", "message": "Local connector setup or request is invalid. No automatic retry."}
    write_message(sys.stdout.buffer, result)


if __name__ == "__main__":
    main()
