"""Tests hors réseau, avec la clé publique de test RFC 8032 seulement."""
import base64
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

import signature_locale as signer

RFC_SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")


class SignerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="technocore-signer-tests-")
        self.folder = Path(self.tmp.name)
        self.key = Ed25519PrivateKey.from_private_bytes(RFC_SEED)
        self.did = signer.did_for(self.key)
        self.pem = self.folder / "rfc8032-test-only.pem"
        self.pem.write_bytes(self.key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.BestAvailableEncryption(b"test-public-vector-only")))
        self.receipts = self.folder / "recus"
        self.calls = []

    def tearDown(self):
        self.tmp.cleanup()

    def transport(self, room, envelope):
        self.calls.append((room, dict(envelope)))
        self.assertEqual(set(envelope), {"did", "sig", "nonce", "text"})
        raw = json.dumps(envelope)
        self.assertNotIn("test-public-vector-only", raw)
        self.assertNotIn(RFC_SEED.hex(), raw)
        self.assertNotIn("PRIVATE KEY", raw)
        posted = {"from": envelope["did"], "nonce": int(envelope["nonce"]), "sig": envelope["sig"], "text": envelope["text"], "seq": 42, "ts": "2026-09-15T22:00:00Z"}
        return signer.json_bytes({"room": room, "posted": posted, "messages": [posted]})

    def publish(self, **overrides):
        params = dict(key_path=self.pem, password="test-public-vector-only", expected_did=self.did, room="kibble", text="Contribution test locale uniquement.", receipts=self.receipts, transport=self.transport)
        params.update(overrides)
        return signer.publish(**params)

    def test_rfc8032_known_signature(self):
        expected = "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
        self.assertEqual(self.key.sign(b"").hex(), expected)
        signer.verify(self.did, base64.urlsafe_b64encode(bytes.fromhex(expected)).decode().rstrip("="), b"")

    def test_canonical_sweep_and_nonce_precision(self):
        text, payload = signer.canonical("dev", "1789502793515697200", "  A\nB\u200bC é  ")
        self.assertEqual(text, "A B C é")
        self.assertEqual(payload, "dev|1789502793515697200|A B C é".encode())

    def test_fixed_public_fixture_and_tamper(self):
        did = "did:key:z6MktwupdmLXVVqTzCw4i46r4uGyosGXRnR3XjN4Zq7oMMsw"
        text = "Public RFC 8032 test fixture only."
        sig = "roHYCFNT5XboCZGT6ksdkbu8TBdi92dS9BDxps5XfxJLNiYcmE1s8-Y1XHsSplmU8v8ui-xgUqQXttyiKPU4BQ"
        _, payload = signer.canonical("dev", "1789502793515697200", text)
        signer.verify(did, sig, payload)
        with self.assertRaises(InvalidSignature):
            signer.verify(did, sig, payload + b"modified")

    def test_success_archives_only_public_data(self):
        folder, posted = self.publish()
        self.assertEqual(posted["seq"], 42)
        self.assertEqual(len(self.calls), 1)
        checked = json.loads((folder / "verification.json").read_bytes())
        self.assertEqual(checked["status"], "published_receipt_verified")
        self.assertFalse((self.receipts / "publication.lock").exists())
        for path in folder.iterdir():
            raw = path.read_bytes()
            self.assertNotIn(b"PRIVATE KEY", raw)
            self.assertNotIn(b"test-public-vector-only", raw)
            self.assertNotIn(RFC_SEED.hex().encode(), raw)

    def test_wrong_password_or_did_never_send(self):
        with self.assertRaises(ValueError):
            self.publish(password="wrong")
        with self.assertRaises(ValueError):
            self.publish(expected_did="did:key:z6Mk" + "1" * 44)
        self.assertEqual(self.calls, [])

    def test_timeout_is_not_retried_or_claimed_successful(self):
        def timeout(room, envelope):
            self.calls.append((room, envelope))
            raise TimeoutError("mock timeout")
        with self.assertRaises(RuntimeError):
            self.publish(transport=timeout)
        with self.assertRaises(ValueError):
            self.publish(transport=timeout)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(len(list(self.receipts.glob("*/A_VERIFIER.txt"))), 1)
        self.assertEqual(list(self.receipts.glob("*/verification.json")), [])

    def test_corrupt_receipt_not_confirmed(self):
        def corrupt(room, envelope):
            obj = json.loads(self.transport(room, envelope))
            obj["posted"]["nonce"] += 1
            return signer.json_bytes(obj)
        with self.assertRaises(RuntimeError):
            self.publish(transport=corrupt)
        self.assertEqual(list(self.receipts.glob("*/verification.json")), [])

    def test_disk_failure_prevents_network(self):
        with patch.object(signer, "write_new", side_effect=OSError("mock disk full")):
            with self.assertRaises(RuntimeError):
                self.publish()
        self.assertEqual(self.calls, [])

    def test_lock_prevents_concurrent_send(self):
        self.receipts.mkdir()
        (self.receipts / "publication.lock").write_text("other process")
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(self.calls, [])
        self.assertTrue((self.receipts / "publication.lock").exists())

    def test_confirmation_does_not_allow_second_identical_post(self):
        self.publish()
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(len(self.calls), 1)


if __name__ == "__main__":
    unittest.main()
