"""Offline boundary tests: no real key, browser, registry change or public post."""
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest

import browser_host as host

DID = "did:key:z6MktwupdmLXVVqTzCw4i46r4uGyosGXRnR3XjN4Zq7oMMsw"
REQUEST = {"op": "publish", "room": "my-custom-room", "text": "A useful test message.", "language": "en"}


class BrowserBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.receipts = Path(self.tmp.name) / "recus"
        self.config = {"did": DID, "key_path": str(Path(self.tmp.name) / "nonexistent.pem")}
        self.approvals = []
        self.calls = []

    def tearDown(self):
        self.tmp.cleanup()

    def approve(self, *args):
        self.approvals.append(args)
        return "mock-password-never-send"

    def publish(self, *args):
        self.calls.append(args)
        return self.receipts, {"seq": 123}

    def handle(self, request=REQUEST, approve=None, publisher=None):
        return host.handle(request, self.config, self.receipts, approve or self.approve, publisher or self.publish)

    def test_profile_returns_only_public_fields_and_never_approves(self):
        result = self.handle({"op": "profile"})
        self.assertEqual(set(result), {"ok", "did", "version"})
        self.assertEqual(self.approvals, [])
        self.assertEqual(self.calls, [])
        self.assertFalse(self.receipts.exists())

    def test_untrusted_fields_and_routes_rejected_before_approval(self):
        for request in [{**REQUEST, "key_path": "evil.pem"}, {**REQUEST, "did": DID},
                        {**REQUEST, "url": "https://example.org"}, {**REQUEST, "room": "../evil"},
                        {**REQUEST, "text": "x" * 4097}, {"op": "export_seed"}]:
            with self.assertRaises(ValueError):
                self.handle(request)
        self.assertEqual(self.approvals, [])
        self.assertEqual(self.calls, [])

    def test_cancellation_never_invokes_publisher(self):
        self.assertEqual(self.handle(approve=lambda *args: None)["code"], "cancelled")
        self.assertEqual(self.calls, [])
        self.assertFalse((self.receipts / "browser-request.lock").exists())

    def test_custom_room_preview_and_public_response_match(self):
        result = self.handle({**REQUEST, "text": "one\ntwo"})
        self.assertEqual(self.approvals[0], ("my-custom-room", "one two", DID, "en"))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][1], "mock-password-never-send")
        self.assertEqual(result, {"ok": True, "did": DID, "room": "my-custom-room", "seq": 123})
        self.assertNotIn("mock-password", json.dumps(result))
        self.assertNotIn(self.config["key_path"], json.dumps(result))

    def test_failed_publish_is_not_retried_and_does_not_leak_error(self):
        def fail(*args):
            self.calls.append(args)
            raise RuntimeError("sensitive-local-path mock-password-never-send")
        result = self.handle(publisher=fail)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(result["code"], "unconfirmed")
        self.assertNotIn("sensitive", json.dumps(result))
        self.assertFalse((self.receipts / "browser-request.lock").exists())

    def test_parallel_confirmation_is_rejected(self):
        self.receipts.mkdir()
        (self.receipts / "browser-request.lock").write_text("already-open")
        self.assertEqual(self.handle()["code"], "busy")
        self.assertEqual(self.calls, [])
        self.assertEqual(self.approvals, [])

    def test_utf8_protocol_and_bad_frames(self):
        stream = io.BytesIO()
        host.write_message(stream, {"text": "Ã©ðŸ˜Š"})
        stream.seek(0)
        self.assertEqual(host.read_message(stream), {"text": "Ã©ðŸ˜Š"})
        for data in [b"", struct.pack("=I", 0), struct.pack("=I", host.MAX_INPUT + 1),
                     struct.pack("=I", 10) + b"{}", struct.pack("=I", 15) + b'{"op":1,"op":2}']:
            with self.assertRaises(ValueError):
                host.read_message(io.BytesIO(data))


if __name__ == "__main__":
    unittest.main()
