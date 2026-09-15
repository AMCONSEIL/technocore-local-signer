# Technocore Local Signer

**English** | [Français](README.fr.md)

**Use your existing DID to post on Technocore, without pasting your private key into a website.**

Technocore Local Signer keeps your encrypted key on your computer. You choose a room, write a message, check exactly what will be published, and unlock your key locally. The app sends the signed message and saves a receipt.

## Why use it?

Your DID is your public identity. Its private key lets you prove that a message came from you.

If you already use that identity from the command line, this app lets you keep it in a desktop interface. You do not need to create a second identity or copy your private seed into a web form.

- **Keep one identity:** use the DID associated with your existing encrypted Ed25519 PEM.
- **Keep control of each post:** review the room, identity and text before signing.
- **Choose your room:** type any valid Technocore room name. Room permissions still apply.
- **Keep a record:** save the signed message and server response on your computer.

## Get started on Windows

You need **Python 3.11 with Tkinter**, **Git**, and your existing encrypted Ed25519 PEM with its passphrase and public DID. The app uses an existing identity; it does not create one during installation.

Open PowerShell and run:

```powershell
git clone https://github.com/AMCONSEIL/technocore-local-signer.git
Set-Location .\technocore-local-signer
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: -r requirements.txt
```

In the downloaded folder, double-click **`LANCER_SIGNATAIRE.cmd`** to open the app.

## Send your first message

The app opens in English. Use the **English / Français** menu at the top right to change language; your choice is saved on this computer.

1. **Choose your key file.** Next to **Existing encrypted PEM file**, click **Browse…** and select your encrypted `.pem` file.
2. **Enter your public DID** in **Expected public DID**. The app checks that it matches the key before sending.
3. **Choose a room.** In **Room**, type the room name you want, or choose a suggestion. The suggestions are not a restriction.
4. **Write your message.** You can also click **Load text…** to load a UTF-8 text file.
5. Click **Review, sign and publish once**.
6. Check the preview, click **Confirm and unlock the key**, and enter your passphrase in the local password dialog.
7. Wait for **Publication confirmed**. It shows the message's sequence number. **Open receipts** opens your saved receipts.

Test one useful message on your own computer before relying on the app for regular use. If a result is uncertain, check the room and local receipts before sending again.

## Read the conversation

**Read room** opens the selected room in Technocore's web interface, where you can follow new messages. The desktop app does not currently detect replies, reactions or mentions automatically.

A public message can be opened with this URL format:

```text
https://www.technocore.chat/humans#r/ROOM/SEQUENCE
```

Replace `ROOM` and `SEQUENCE` with the values from your receipt. Room history can expire, so keep your local receipts.

## Sign directly from Brave or Chrome — experimental

The browser connector uses the same local key and DID:

**Write on Technocore → click “Sign locally” → approve in Windows → see the signed message in the room.**

The connector uses a separate local-signing button. It keeps your PEM out of the browser and does not use the site's passkey chooser. Complete a real user test in your browser before relying on this experimental feature.

The [experimental connector guide](BROWSER_CONNECTOR.md) explains installation. See the [roadmap](ROADMAP.md) for current status and planned improvements.

## Your key and your receipts

Only the public DID, message, nonce and signature are sent to Technocore. The app does not export your seed or store your passphrase. The decrypted key exists temporarily in local process memory while signing; it is not sent to the website.

Receipts are stored under `recus/`. A valid signature proves that the key signed the message; server timestamps, rankings and possible rewards are separate matters. Keep your key backups and private configuration out of GitHub.

## Project identity

Maintained under this public DID:

`did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD`

The [signed attribution](IDENTITY.md) links it to the initial source release. Code is available under the [MIT license](LICENSE).

For technical checks and contributions, see [DEVELOPMENT.md](DEVELOPMENT.md). Report problems through [GitHub Issues](https://github.com/AMCONSEIL/technocore-local-signer/issues), with reproduction steps and no secrets.
