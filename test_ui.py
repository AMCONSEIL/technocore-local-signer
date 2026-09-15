"""Local GUI tests with a synthetic DID, no key access and no network."""
import json
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

import signataire as gui

DID = "did:key:z6MktwupdmLXVVqTzCw4i46r4uGyosGXRnR3XjN4Zq7oMMsw"


class UiLanguageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        self.location = patch.object(gui, "APP_DIR", self.folder)
        self.location.start()
        self.publisher = patch.object(gui, "publish", side_effect=AssertionError("GUI test must not publish"))
        self.publisher.start()
        self.root = tk.Tk()
        self.root.attributes("-alpha", 0)
        self.root.attributes("-toolwindow", True)
        self.app = gui.SignerWindow(self.root, {"did": DID, "key_path": str(self.folder / "never-open.pem")})
        self.root.update()

    def tearDown(self):
        for timer in self.root.tk.call("after", "info"):
            self.root.after_cancel(timer)
        self.root.destroy()
        self.publisher.stop()
        self.location.stop()
        self.tmp.cleanup()

    def test_language_switch_keeps_identity_message_and_room(self):
        self.assertEqual(self.app.language, "en")
        self.assertEqual(self.app.word("publish").get(), "Review, sign and publish once")
        self.app.room.set("custom-room")
        self.app.text.insert("1.0", "Useful contribution.")
        original_key = self.app.key.get()
        self.app.language_choice.set("Français")
        self.app.change_language()
        self.assertEqual(self.app.word("publish").get(), "Relire, signer et publier une fois")
        self.assertEqual(self.app.did.get(), DID)
        self.assertEqual(self.app.key.get(), original_key)
        self.assertEqual(self.app.room.get(), "custom-room")
        self.assertEqual(self.app.text.get("1.0", "end-1c"), "Useful contribution.")
        self.assertEqual(json.loads((self.folder / "ui.local.json").read_text())["language"], "fr")
        self.assertFalse((self.folder / "never-open.pem").exists())
        self.assertFalse((self.folder / "recus").exists())

    def test_status_and_error_follow_selected_language(self):
        self.app.set_status("published", room="dev", seq=42, folder="test-receipt")
        self.assertIn("Published: dev", self.app.status.get())
        self.app.language_choice.set("Français")
        self.app.change_language()
        self.assertIn("Publié : dev", self.app.status.get())
        self.app.set_status("error", detail="Passphrase incorrecte ou PEM chiffré invalide.")
        self.app.language_choice.set("English")
        self.app.change_language()
        self.assertEqual(self.app.status.get(), "Incorrect passphrase or invalid encrypted PEM.")

    def test_main_publish_button_fits_at_minimum_size(self):
        for language in ("English", "Français"):
            self.app.language_choice.set(language)
            self.app.change_language()
            self.root.geometry("730x570")
            self.root.update()
            button = self.app.button
            self.assertTrue(button.winfo_ismapped())
            self.assertGreaterEqual(button.winfo_width(), button.winfo_reqwidth())
            self.assertGreaterEqual(button.winfo_height(), button.winfo_reqheight())
            bottom = button.winfo_rooty() - self.root.winfo_rooty() + button.winfo_height()
            self.assertLessEqual(bottom, self.root.winfo_height())

    def test_confirmation_buttons_fit_both_languages(self):
        original = tk.Toplevel
        def hidden_window(*args, **kwargs):
            window = original(*args, **kwargs)
            window.attributes("-alpha", 0)
            window.attributes("-toolwindow", True)
            return window
        self.app.text.insert("1.0", "Review only, never publish.")
        for language in ("English", "Français"):
            self.app.language_choice.set(language)
            self.app.change_language()
            with patch.object(gui.tk, "Toplevel", hidden_window):
                self.app.confirm()
            preview = next(child for child in self.root.winfo_children() if isinstance(child, original))
            footer = next(child for child in preview.winfo_children() if isinstance(child, ttk.Frame))
            buttons = footer.winfo_children()
            self.assertEqual(len(buttons), 2)
            for size in ("640x300", "760x440"):
                preview.geometry(size)
                self.root.update()
                for button in buttons:
                    bottom = button.winfo_rooty() - preview.winfo_rooty() + button.winfo_height()
                    self.assertLessEqual(bottom, preview.winfo_height(), (language, size, bottom))
                    self.assertGreater(button.winfo_height(), 1)
            preview.destroy()


if __name__ == "__main__":
    unittest.main()
