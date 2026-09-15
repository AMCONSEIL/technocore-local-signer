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

APP_DIR = Path(__file__).resolve().parent


class SignerWindow:
    def __init__(self, root, config=None):
        self.root = root
        self.events = queue.Queue()
        self.busy = False
        config = config or {}
        self.receipts = APP_DIR / "recus"
        root.title("Technocore — signature locale")
        root.geometry("890x700")
        root.minsize(730, 570)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.frame = ttk.Frame(root, padding=18)
        self.frame.pack(fill="both", expand=True)
        ttk.Label(self.frame, text="Signer sous votre DID, avec votre clé sur cet ordinateur", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(self.frame, text="La passphrase et la clé ne sont jamais envoyées au site. Chaque message sera public.", wraplength=830).pack(anchor="w", pady=(4, 14))
        self.key = tk.StringVar(value=config.get("key_path", str(Path.home() / "FLOP-Identite" / "identity.pem")))
        self.did = tk.StringVar(value=config.get("did", ""))
        self.room = tk.StringVar(value="kibble")
        ttk.Label(self.frame, text="Fichier PEM chiffré existant").pack(anchor="w")
        keyrow = ttk.Frame(self.frame)
        keyrow.pack(fill="x", pady=(3, 8))
        ttk.Entry(keyrow, textvariable=self.key).pack(side="left", fill="x", expand=True)
        ttk.Button(keyrow, text="Choisir…", command=self.choose_key).pack(side="left", padx=(8, 0))
        ttk.Label(self.frame, text="DID public attendu (contrôlé avant tout envoi)").pack(anchor="w")
        ttk.Entry(self.frame, textvariable=self.did).pack(fill="x", pady=(3, 8))
        row = ttk.Frame(self.frame)
        row.pack(fill="x", pady=(4, 8))
        ttk.Label(row, text="Salon :").pack(side="left")
        ttk.Combobox(row, textvariable=self.room, values=("kibble", "dev", "meta", "gpu-miners", "lobby"), width=24).pack(side="left", padx=8)
        ttk.Button(row, text="Lire le salon", command=self.read_room).pack(side="left")
        ttk.Button(row, text="Charger un texte…", command=self.load_text).pack(side="right")
        ttk.Label(self.frame, text="Contribution — vérifiez la demande et le résultat concernés avant une attestation").pack(anchor="w")
        self.text = tk.Text(self.frame, height=12, wrap="word", font=("Segoe UI", 11), undo=True)
        self.text.pack(fill="both", expand=True, pady=(5, 8))
        self.button = ttk.Button(self.frame, text="Relire, signer et publier une fois", command=self.confirm)
        self.button.pack(anchor="e", pady=5)
        ttk.Button(self.frame, text="Ouvrir les reçus", command=self.open_receipts).pack(anchor="e")
        self.status = tk.StringVar(value="Prêt. Aucune clé chargée. Aucun message envoyé.")
        ttk.Label(self.frame, textvariable=self.status, wraplength=830).pack(anchor="w", pady=(12, 6))
        ttk.Label(self.frame, text="Les reçus prouvent le contenu signé et conservent la réponse serveur ; ils ne garantissent pas un airdrop.", wraplength=830).pack(anchor="w")
        root.after(150, self.poll)

    def choose_key(self):
        value = filedialog.askopenfilename(parent=self.root, title="Choisir votre PEM chiffré", filetypes=[("Clé chiffrée", "*.pem")])
        if value:
            self.key.set(value)

    def load_text(self):
        value = filedialog.askopenfilename(parent=self.root, initialdir=APP_DIR / "brouillons", filetypes=[("Texte", "*.txt")])
        if value:
            try:
                path = Path(value)
                if path.stat().st_size > 20000:
                    raise ValueError("Fichier trop volumineux pour un message.")
                text = path.read_text(encoding="utf-8-sig")
                canonical(self.room.get().strip(), "1", text)
                self.text.delete("1.0", "end")
                self.text.insert("1.0", text)
            except Exception as exc:
                messagebox.showerror("Texte non chargé", str(exc), parent=self.root)

    def read_room(self):
        try:
            room = self.room.get().strip()
            canonical(room, "1", "lecture")
            webbrowser.open(f"{ORIGIN}/r/{room}")
        except ValueError as exc:
            messagebox.showerror("Salon", str(exc), parent=self.root)

    def open_receipts(self):
        if self.receipts.is_dir():
            os.startfile(str(self.receipts))
        else:
            messagebox.showinfo("Reçus", "Aucune tentative n'a encore été enregistrée.", parent=self.root)

    def confirm(self):
        if self.busy:
            return
        try:
            room = self.room.get().strip()
            text, _ = canonical(room, "1", self.text.get("1.0", "end-1c"))
            did = self.did.get().strip()
            if not did.startswith("did:key:z6Mk"):
                raise ValueError("Renseignez votre DID public attendu.")
        except ValueError as exc:
            messagebox.showerror("Message", str(exc), parent=self.root)
            return
        preview = tk.Toplevel(self.root)
        preview.title("Vérifier la publication exacte")
        width, height = 760, 440
        x = max(0, min(self.root.winfo_rootx() + 40, preview.winfo_screenwidth() - width - 20))
        y = max(30, min(self.root.winfo_rooty() + 60, preview.winfo_screenheight() - height - 60))
        preview.geometry(f"{width}x{height}+{x}+{y}")
        preview.minsize(640, 300)
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(1, weight=1)
        preview.transient(self.root)
        preview.grab_set()
        ttk.Label(preview, text=f"Destination : {ORIGIN}/r/{room}\nIdentité : {did}", wraplength=720).grid(row=0, column=0, sticky="ew", padx=16, pady=12)
        view = tk.Text(preview, height=1, wrap="word", font=("Segoe UI", 11))
        view.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        view.insert("1.0", text)
        view.configure(state="disabled")
        row = ttk.Frame(preview, padding=12)
        row.grid(row=2, column=0, sticky="ew")
        ttk.Button(row, text="Annuler", command=preview.destroy).pack(side="left")

        def approve():
            preview.destroy()
            password = simpledialog.askstring("Déverrouillage local", "Passphrase du PEM chiffré (reste sur cet ordinateur) :", show="*", parent=self.root)
            if not password:
                return
            key_path = Path(self.key.get()).expanduser()
            self.busy = True
            self.button.configure(state="disabled")
            self.status.set("Signature locale puis un seul envoi HTTPS. Ne pas fermer pendant l'envoi.")
            threading.Thread(target=self.work, args=(key_path, password, did, room, text), daemon=False).start()

        ttk.Button(row, text="Valider et déverrouiller la clé", command=approve).pack(side="right")

    def work(self, path, password, did, room, text):
        try:
            folder, posted = publish(path, password, did, room, text, self.receipts)
            self.events.put((True, f"Publié : {room} / seq {posted['seq']}. Signature du reçu vérifiée.\nReçu : {folder}"))
        except Exception as exc:
            self.events.put((False, str(exc)))
        finally:
            password = None

    def poll(self):
        try:
            ok, detail = self.events.get_nowait()
            self.busy = False
            self.button.configure(state="normal")
            self.status.set(detail)
            if ok:
                messagebox.showinfo("Publication confirmée", detail, parent=self.root)
            else:
                messagebox.showerror("Publication non confirmée", detail, parent=self.root)
        except queue.Empty:
            pass
        self.root.after(150, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo("Envoi en cours", "Attendre le résultat avant de fermer : aucun nouvel essai automatique n'est effectué.", parent=self.root)
            return
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        path = APP_DIR / "config.local.json"
        config = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        SignerWindow(root, config)
        root.mainloop()
    except Exception as exc:
        messagebox.showerror("Signataire", str(exc), parent=root)
        root.destroy()


if __name__ == "__main__":
    main()
