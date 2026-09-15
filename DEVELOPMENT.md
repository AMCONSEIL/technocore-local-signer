# Development and verification

[Back to the app](README.md)

## Run the desktop tests

From the repository directory after installation:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_signature_locale test_browser_host
```

The original desktop suite contains 10 offline tests. It uses a mocked transport and the published RFC 8032 section 7.1 test 1 key. Never use this test key as a real identity.

The desktop confirmation layout was checked at 640×300, 760×440 and 760×600 pixels. A real user publication and its receipt were verified on 15 September 2026. These checks are not a security audit or proof of compatibility with every environment.

## Receipts

The signed UTF-8 payload is `room|nonce|text`, after Technocore's text normalization. The DID, nonce, text and signature in the response must match the submitted envelope. The sequence and timestamp are assigned by the server and are not covered by the author's signature.

A network failure does not prove that a write failed. The app does not retry. Before resolving a duplicate-attempt block or a stale `recus/publication.lock`, inspect the local attempts and the public room.

The passphrase is not stored. Python cannot guarantee immediate physical erasure of all decrypted key material from memory.

## Publication and privacy

Publish reviewed source files, documentation, tests and explicitly reviewed public proofs only. Do not add PEM files, private seeds, personal configuration, raw receipt folders, local runtime manifests, environments, caches or generated builds.

The attribution proof contains only the project's public signed announcement. It intentionally excludes other users' messages from the server response. See [IDENTITY.md](IDENTITY.md) for verification instructions.

A real user test is required on a new environment before distribution as working there. Browser features remain experimental until tested through the selected browser and the local confirmation flow.

## References

- [Technocore protocol](https://technocore.chat/llms.txt)
- [Technocore signing](https://technocore.chat/auth.md)
- [Chromium native messaging](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging)

## Browser checks

The combined Python suite has 17 offline tests. Native framing was also exercised through the Windows command wrapper with a synthetic public DID and a nonexistent PEM path; the wrong extension origin was rejected. No user key or registry entry was used in that probe.

Run the service-worker boundary checks with `node extension/test_background.cjs`. These checks cover site/frame filtering, accepted fields, single pending approval, response filtering and no automatic retry. They do not replace a real browser/user test.
