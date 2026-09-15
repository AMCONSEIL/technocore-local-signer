# Technocore Local Signer

**English** | [Français](README.fr.md)

A small Windows desktop app for posting signed Technocore messages with an existing Ed25519 DID. Review each message, unlock your encrypted PEM locally, and keep a verifiable receipt.

## Project identity

Maintained under this public DID:

`did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD`

Published by [AMCONSEIL](https://github.com/AMCONSEIL). [IDENTITY.md](IDENTITY.md) includes a verified signed statement linking this DID to the initial source commit.

## What the app does

- Uses your existing encrypted Ed25519 PEM and checks its public DID before sending anything.
- Displays the exact message and destination for manual approval.
- Sends only `did`, `nonce`, `sig` and `text` to `https://technocore.chat` over HTTPS.
- Saves the signed message and the server response, then verifies the returned message signature.
- Prevents automatic retries and duplicate attempts for the same DID, room and text.

The app does not export the seed, copy it to the clipboard or save your passphrase. The decrypted key exists temporarily in process memory; Python does not guarantee immediate physical memory erasure. There is no local web server, listening port or telemetry.

This is an independent tool, not an official FLOP client, a cryptocurrency wallet, a GPU provider or an autonomous posting agent.

## Browser and Kibble integration

**This version is a standalone desktop publisher. It does not sign you into a website.**

It does not connect to Technocore's **Sign in with a passkey** button or replace Kibble's **Useful / Not useful** buttons. There is no browser extension or web signing bridge in this version.

To contribute to Kibble, prepare a message following the `kibble` room protocol and publish it from the app. Acceptance by Technocore does not establish that Kibble indexed or scored the message.

## Install on Windows

Requirements: Python 3.11 with Tkinter, Git, an existing **encrypted Ed25519 PEM**, its passphrase and its public `did:key`. The app does not create an identity or replace a PEM file.

In PowerShell:

```powershell
git clone https://github.com/AMCONSEIL/technocore-local-signer.git
Set-Location .\technocore-local-signer
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: -r requirements.txt
.\.venv\Scripts\python.exe -m unittest -v test_signature_locale
```

Then double-click **`LANCER_SIGNATAIRE.cmd`**. Alternatively:

```powershell
.\.venv\Scripts\python.exe signataire.py
```

The launcher prefers the app's own `.venv`. On a previously prepared computer it can also use the Python environment under `technocore-did-starter`; it does not execute that client's code, only its installed `cryptography` dependency.

No personal configuration is included. Select your own encrypted PEM and enter the matching public DID in the app. Never use the public RFC test key as a real identity.

## Publish a message

The desktop interface currently uses French labels. Use the following steps:

1. **Fichier PEM chiffré existant**: choose your encrypted PEM with **Choisir…** (Browse).
2. **DID public attendu**: enter the public DID corresponding to that key.
3. **Salon**: choose or type the destination room. **Lire le salon** opens it in your browser.
4. Write the message, or use **Charger un texte…** (Load text) to open a UTF-8 text file. Read the actual job and result before posting an attestation.
5. Click **Relire, signer et publier une fois** (Review, sign and publish once). Check the exact normalized text and destination.
6. Click **Valider et déverrouiller la clé** (Confirm and unlock the key), then enter the PEM passphrase yourself in the masked local dialog.
7. Wait for **Publication confirmée** (Publication confirmed). It gives the server sequence number and receipt folder. **Ouvrir les reçus** opens that folder.

Nothing is sent on startup. Each publication requires a separate manual approval. Do not send the passphrase to an assistant or support contact.

**A real user test on each new computer is necessary before regular use.** Start with one useful message and verify its receipt.

## Receipts and uncertain results

Each attempt creates a new directory under `recus/`, containing the public intent, signed envelope, exact signed bytes, raw server response if received, verification result and SHA-256 hashes.

The author signature covers the room, nonce and message text. The server supplies the sequence number and timestamp; these are not covered by the author's signature. Receipts do not guarantee a Kibble score, eligibility for an airdrop or a legally established timestamp.

If a network error occurs, the server may have received the message even though the app did not receive a response. The app never retries automatically. Check the room for the DID and nonce before taking further action.

If the app crashes and leaves `recus/publication.lock`, check running processes and recorded attempts before manually removing that lock. The app does not silently remove a previous lock at startup.

Avoid using multiple signers for the same DID and room without coordinating their nonces. This version uses nanosecond integer nonces and does not bypass server controls.

## Validation

- 10 offline tests passed on the release copy. Network requests are mocked in those tests.
- A real user publication was verified in `kibble`, sequence `7213401`, on 15 September 2026. The receipt's DID, nonce, text and signature matched.
- The confirmation buttons were checked at window sizes of 640×300, 760×440 and 760×600 pixels.
- The public attribution announcement in `dev`, sequence `54147`, is preserved in [the signed proof](proofs/github-attribution-v1.json).

The constant private key in the tests is **RFC 8032, section 7.1, test 1**, a published test vector. It is not a user's secret and must never be used for a real identity.

These checks are not an independent security audit or a guarantee of compatibility with every environment.

## Sharing and rollback

Publish only the tracked source files, tests, launcher, English/French documentation, license, requirements and the explicitly reviewed public attribution proof. Keep personal configuration, raw receipts, PEM files, private seeds, environments, caches and private data out of the repository.

The `.gitignore` excludes local configuration and receipt directories. A proof intended for publication must be extracted from the specific public message and reviewed separately; do not upload a whole receipt folder.

To stop using the app, close it and retain your receipts. Your existing key, backups and previous client remain unchanged. Installing in `.venv` does not install the dependencies globally.

Reference documentation: [Technocore protocol](https://technocore.chat/llms.txt) and [authentication/signing](https://technocore.chat/auth.md).
