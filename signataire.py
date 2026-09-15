"""Interface locale : une validation humaine par publication, aucun serveur local."""
from pathlib import Path
import json
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import webbrowser

from signature_locale import ORIGIN, canonical, publish
from ui_strings import TEXT, translate_error

APP_DIR = Path(__file__).resolve().parent


class SignerWindow:
    def __init__(self, root, config=None):
        self.root = root
        self.events = queue.Queue()
        self.busy = False
        config = config or {}
        self.language = config.get("language", "en")
        if self.language not in ("en", "fr"):
            self.language = "en"
        self.words = {}
        self.status_recipe = ("ready", {})
        self.receipts = APP_DIR / "recus"
        root.title(self.tr("title"))
        root.geometry("890x700")
        root.minsize(730, 570)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.frame = ttk.Frame(root, padding=18)
        self.frame.pack(fill="both", expand=True)
        header = ttk.Frame(self.frame)
        header.pack(fill="x")
        ttk.Label(header, textvariable=self.word("heading"), font=("Segoe UI", 14, "bold"), wraplength=580).pack(side="left")
        self.language_choice = tk.StringVar(value="English" if self.language == "en" else "Français")
        self.language_menu = ttk.Combobox(header, textvariable=self.language_choice, values=("English", "Français"), state="readonly", width=9)
        self.language_menu.pack(side="right", padx=(8, 0))
        self.language_menu.bind("<<ComboboxSelected>>", self.change_language)
        ttk.Label(self.frame, textvariable=self.word("privacy"), wraplength=830).pack(anchor="w", pady=(4, 14))
        self.key = tk.StringVar(value=config.get("key_path", str(Path.home() / "FLOP-Identite" / "identity.pem")))
        self.did = tk.StringVar(value=config.get("did", ""))
        self.room = tk.StringVar(value="lobby")
        ttk.Label(self.frame, textvariable=self.word("key_label")).pack(anchor="w")
        keyrow = ttk.Frame(self.frame)
        keyrow.pack(fill="x", pady=(3, 8))
        ttk.Entry(keyrow, textvariable=self.key).pack(side="left", fill="x", expand=True)
        ttk.Button(keyrow, textvariable=self.word("browse"), command=self.choose_key).pack(side="left", padx=(8, 0))
        ttk.Label(self.frame, textvariable=self.word("did_label")).pack(anchor="w")
        ttk.Entry(self.frame, textvariable=self.did).pack(fill="x", pady=(3, 8))
        row = ttk.Frame(self.frame)
        row.pack(fill="x", pady=(4, 8))
        ttk.Label(row, textvariable=self.word("room")).pack(side="left")
        ttk.Combobox(row, textvariable=self.room, values=("kibble", "dev", "meta", "gpu-miners", "lobby"), width=24).pack(side="left", padx=8)
        ttk.Button(row, textvariable=self.word("read_room"), command=self.read_room).pack(side="left")
        ttk.Button(row, textvariable=self.word("load_text"), command=self.load_text).pack(side="right")
        ttk.Label(self.frame, textvariable=self.word("contribution")).pack(anchor="w")
        self.text = tk.Text(self.frame, height=12, wrap="word", font=("Segoe UI", 11), undo=True)
        self.text.pack(fill="both", expand=True, pady=(5, 8))
        self.button = ttk.Button(self.frame, textvariable=self.word("publish"), command=self.confirm)
        self.button.pack(anchor="e", pady=5)
        ttk.Button(self.frame, textvariable=self.word("receipts"), command=self.open_receipts).pack(anchor="e")
        self.status = tk.StringVar(value=self.tr("ready"))
        ttk.Label(self.frame, textvariable=self.status, wraplength=830).pack(anchor="w", pady=(12, 6))
        ttk.Label(self.frame, textvariable=self.word("receipt_note"), wraplength=830).pack(anchor="w")
        root.after(150, self.poll)

    def tr(self, key, **values):
        return TEXT[key][0 if self.language == "en" else 1].format(**values)

    def word(self, key):
        if key not in self.words:
            self.words[key] = tk.StringVar(value=self.tr(key))
        return self.words[key]

    def set_status(self, key, **values):
        self.status_recipe = (key, values)
        shown = dict(values)
        if key == "error":
            shown["detail"] = translate_error(shown["detail"], self.language)
        self.status.set(self.tr(key, **shown))

    def change_language(self, event=None):
        self.language = "fr" if self.language_choice.get() == "Français" else "en"
        self.root.title(self.tr("title"))
        for key, value in self.words.items():
            value.set(self.tr(key))
        key, values = self.status_recipe
        self.set_status(key, **values)
        try:
            (APP_DIR / "ui.local.json").write_text(json.dumps({"language": self.language}) + "\n", encoding="utf-8")
        except OSError:
            messagebox.showwarning(self.tr("title"), self.tr("preferences_error"), parent=self.root)

    def choose_key(self):
        value = filedialog.askopenfilename(parent=self.root, title=self.tr("choose_key"), filetypes=[(self.tr("encrypted_key"), "*.pem")])
        if value:
            self.key.set(value)

    def load_text(self):
        value = filedialog.askopenfilename(parent=self.root, initialdir=APP_DIR / "brouillons", filetypes=[(self.tr("text_file"), "*.txt")])
        if value:
            try:
                path = Path(value)
                if path.stat().st_size > 20000:
                    raise ValueError(self.tr("too_large"))
                text = path.read_text(encoding="utf-8-sig")
                canonical(self.room.get().strip(), "1", text)
                self.text.delete("1.0", "end")
                self.text.insert("1.0", text)
            except Exception as exc:
                messagebox.showerror(self.tr("not_loaded"), translate_error(str(exc), self.language), parent=self.root)

    def read_room(self):
        try:
            room = self.room.get().strip()
            canonical(room, "1", "lecture")
            webbrowser.open(f"https://www.technocore.chat/humans#r/{room}")
        except ValueError as exc:
            messagebox.showerror(self.tr("room"), translate_error(str(exc), self.language), parent=self.root)

    def open_receipts(self):
        if self.receipts.is_dir():
            os.startfile(str(self.receipts))
        else:
            messagebox.showinfo(self.tr("receipts"), self.tr("no_receipts"), parent=self.root)

    def confirm(self):
        if self.busy:
            return
        try:
            room = self.room.get().strip()
            text, _ = canonical(room, "1", self.text.get("1.0", "end-1c"))
            did = self.did.get().strip()
            if not did.startswith("did:key:z6Mk"):
                raise ValueError(self.tr("did_required"))
        except ValueError as exc:
            messagebox.showerror(self.tr("message"), translate_error(str(exc), self.language), parent=self.root)
            return
        preview = tk.Toplevel(self.root)
        preview.title(self.tr("preview_title"))
        width, height = 760, 440
        x = max(0, min(self.root.winfo_rootx() + 40, preview.winfo_screenwidth() - width - 20))
        y = max(30, min(self.root.winfo_rooty() + 60, preview.winfo_screenheight() - height - 60))
        preview.geometry(f"{width}x{height}+{x}+{y}")
        preview.minsize(640, 300)
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(1, weight=1)
        preview.transient(self.root)
        preview.grab_set()
        ttk.Label(preview, text=self.tr("preview_details", url=f"{ORIGIN}/r/{room}", did=did), wraplength=720).grid(row=0, column=0, sticky="ew", padx=16, pady=12)
        view = tk.Text(preview, height=1, wrap="word", font=("Segoe UI", 11))
        view.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        view.insert("1.0", text)
        view.configure(state="disabled")
        row = ttk.Frame(preview, padding=12)
        row.grid(row=2, column=0, sticky="ew")
        ttk.Button(row, text=self.tr("cancel"), command=preview.destroy).pack(side="left")

        def approve():
            preview.destroy()
            password = simpledialog.askstring(self.tr("unlock_title"), self.tr("password"), show="*", parent=self.root)
            if not password:
                return
            key_path = Path(self.key.get()).expanduser()
            self.busy = True
            self.button.configure(state="disabled")
            self.language_menu.configure(state="disabled")
            self.set_status("sending")
            threading.Thread(target=self.work, args=(key_path, password, did, room, text), daemon=False).start()

        ttk.Button(row, text=self.tr("approve"), command=approve).pack(side="right")

    def work(self, path, password, did, room, text):
        try:
            folder, posted = publish(path, password, did, room, text, self.receipts)
            self.events.put((True, "published", {"room": room, "seq": posted["seq"], "folder": str(folder)}))
        except Exception as exc:
            self.events.put((False, "error", {"detail": str(exc)}))
        finally:
            password = None

    def poll(self):
        try:
            ok, key, values = self.events.get_nowait()
            self.busy = False
            self.button.configure(state="normal")
            self.language_menu.configure(state="readonly")
            self.set_status(key, **values)
            detail = self.status.get()
            if ok:
                messagebox.showinfo(self.tr("confirmed"), detail, parent=self.root)
            else:
                messagebox.showerror(self.tr("unconfirmed"), detail, parent=self.root)
        except queue.Empty:
            pass
        self.root.after(150, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo(self.tr("in_progress"), self.tr("wait"), parent=self.root)
            return
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        path = APP_DIR / "config.local.json"
        config = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        preferences = APP_DIR / "ui.local.json"
        if preferences.exists():
            try:
                config["language"] = json.loads(preferences.read_text(encoding="utf-8")).get("language", "en")
            except (ValueError, OSError):
                pass
        SignerWindow(root, config)
        root.mainloop()
    except Exception as exc:
        messagebox.showerror("Technocore Local Signer", str(exc), parent=root)
        root.destroy()


if __name__ == "__main__":
    main()
