# Install Technocore Local Signer on Windows

[Project home](README.md) · [Troubleshooting](#troubleshooting) · [Report a problem](https://github.com/AMCONSEIL/technocore-local-signer/issues)

**Write on Technocore. Review in Windows. Sign with your existing DID.**

This guide takes you from downloading the app to your first signed message in Brave or Chrome. You install two parts: a browser extension and a local signing app. The local app reads your encrypted PEM only when you approve a publication and enter its passphrase. Your key and passphrase stay outside the browser.

The screenshots show the actual extension in Brave. Browser labels may appear in your system language. The DID and extension ID in the examples belong to the project maintainer: **use your own values during setup**.

> **Current status:** experimental Windows release. The extension panel and local DID connection have been observed in Brave. A full browser-to-publication test and independent Chrome testing are still pending. Complete your own first-message check before relying on it for regular use.

## What you need

| Requirement | What to have ready |
|---|---|
| Computer | A Windows PC. This guide uses 64-bit Windows and PowerShell. The installer currently supports Windows only. |
| Browser | Brave or Chrome on desktop, with permission to load an unpacked extension. |
| Python and Git | Commands below use Python 3.11, the currently tested runtime, and Git. |
| Public identity | Your existing Ed25519 DID, beginning with `did:key:z6Mk…`. |
| Private identity file | Your encrypted Ed25519 `.pem` file, often called `identity.pem`, and its passphrase. Keep its backup somewhere safe. |

**The app uses an existing identity; it does not create or recover one.** A browser passkey, an Ethereum wallet address or a seed phrase cannot be selected as a PEM file. If you do not have an encrypted PEM and matching DID, first use the identity tool you originally chose; [Technocore's signing reference](https://technocore.chat/auth.md) explains its signing format. Never paste the file contents or passphrase into GitHub, a public room or a support message.

Already installed the desktop app? Keep its existing folder and start at [step 4](#4-load-the-extension-in-your-browser). Its own `.venv` must contain the dependencies from `requirements.txt`.

## Follow these steps

1. [Check Python and Git](#1-check-python-and-git)
2. [Download the app](#2-download-the-app)
3. [Install its Python dependencies](#3-install-its-python-dependencies)
4. [Load the extension in your browser](#4-load-the-extension-in-your-browser)
5. [Connect the extension to the local app](#5-connect-the-extension-to-the-local-app)
6. [Display your DID on Technocore](#6-display-your-did-on-technocore)
7. [Write, review and sign your first message](#7-write-review-and-sign-your-first-message)
8. [Check the result and keep your receipt](#8-check-the-result-and-keep-your-receipt)

Copy **only the commands inside each code block**, in order. Do not copy a terminal prompt such as `PS C:\...>`. If a step reports an error, resolve it before continuing. No virtual-environment activation or PowerShell execution-policy change is needed.

## 1. Check Python and Git

Open **Windows PowerShell** from the Start menu. Run:

```powershell
py -3.11 --version
git --version
```

**Expected:** `Python 3.11.x` and `git version ...`.

If either is missing, install that prerequisite using the corresponding command below. Review any installation prompts. This installs software; skip a command if that tool is already available.

```powershell
winget install --exact --id Python.Python.3.11 --source winget
```

```powershell
winget install --exact --id Git.Git --source winget
```

Close PowerShell, open a new window, and repeat the two version checks. Git or Python installation may ask for Windows administrator approval; the signer connector itself registers for the current user without administrator rights.

If `winget` is unavailable, use the official [Python 3.11 Windows installer page](https://www.python.org/downloads/release/python-3119/) and [Git for Windows instructions](https://git-scm.com/install/windows). Python 3.11.9 is the last 3.11 release with the traditional Windows installer; later 3.11 security releases exist. Keep Python's **launcher** and **Tcl/Tk** components selected. Do not replace another project's Python installation.

## 2. Download the app

The following block creates a folder under your Windows account's local application data. It requires no GitHub account.

```powershell
$signerFolder = Join-Path $env:LOCALAPPDATA "Technocore\technocore-local-signer"
New-Item -ItemType Directory -Path (Split-Path -Parent $signerFolder) -Force | Out-Null
git clone https://github.com/AMCONSEIL/technocore-local-signer.git "$signerFolder"
if ($LASTEXITCODE -ne 0) { throw "Download failed. Read the Git error before continuing." }
Set-Location -LiteralPath $signerFolder
```

**Expected:** Git finishes downloading, and the prompt ends in `technocore-local-signer>`.

If Git says the destination already exists, do not delete or overwrite it. You may already have an installation: see [existing folder](#the-download-folder-already-exists).

Keep the app at this location after installing the connector. Moving it later breaks the browser's saved registration. Your PEM can stay in its original folder; you will select it in step 5.

## 3. Install its Python dependencies

In the same PowerShell window, run this block:

```powershell
py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Python environment creation failed." }
& ".\.venv\Scripts\python.exe" -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
& ".\.venv\Scripts\python.exe" -m pip check
if ($LASTEXITCODE -ne 0) { throw "Dependency verification failed." }
& ".\.venv\Scripts\python.exe" -c "import tkinter, cryptography; print('Local signer dependencies: OK')"
```

**Expected:** `No broken requirements found.` followed by `Local signer dependencies: OK`.

No output from the first command is normal: it creates `.venv` silently. The correct Python path begins with **`.\.venv`**, including both the dot and the backslash.

Check that this is the app folder:

```powershell
Get-Item .\INSTALLER_CONNECTEUR.cmd, .\LANCER_SIGNATAIRE.cmd, .\extension\manifest.json
```

**Expected:** all three files are listed.

## 4. Load the extension in your browser

1. Open a normal Brave or Chrome window using the browser profile where you want to use Technocore.
2. Type one of these addresses into the **browser address bar**, then press Enter:

   | Browser | Address |
   |---|---|
   | Brave | `brave://extensions` |
   | Chrome | `chrome://extensions` |

3. Enable **Developer mode** in the top-right corner.
4. Click **Load unpacked**. In French: **Charger l'extension non empaquetée**.
5. Select the **`extension` subfolder**, not the whole project folder and not an individual file.

To find the exact folder to select, run this in PowerShell from the app folder:

```powershell
(Resolve-Path .\extension).Path
```

Copy the resulting folder path into the browser's folder chooser and select that folder.

**Expected:** an enabled card named **Technocore Local Signer** appears:

![Technocore Local Signer installed in Brave, with its extension ID visible](docs/images/brave-extension-installed.png)

*The browser labels in this screenshot are French. The extension's name, description and ID appear in the same card. Your ID may differ; copy yours.*

6. Copy the **32-letter ID** from your extension's card. If the ID is hidden, keep Developer mode enabled or open **Details**.

`Service worker (Inactive)` is normal when the extension is idle. It does not mean installation failed. This version is loaded locally; it is not installed from the Chrome Web Store.

## 5. Connect the extension to the local app

Back in PowerShell, from the app folder, run:

```powershell
.\INSTALLER_CONNECTEUR.cmd
```

You can also double-click that file in File Explorer. You do not need to start the desktop signer separately.

Follow the local Windows dialogs:

| Dialog | What to enter or select |
|---|---|
| **Connect Brave or Chrome / Connecter Brave ou Chrome** | Paste **your extension ID** copied in step 4. |
| **Public DID / DID public** | Paste **your existing public DID**, beginning with `did:key:z6Mk…`. Do not copy the maintainer's DID from a screenshot. |
| **Select encrypted PEM / Choisir le PEM chiffré** | Browse to your existing encrypted `.pem` file and select it. Do not open it in a text editor or paste its contents. |
| **Ready / Prêt** | Setup completed. Continue to step 6. |

The DID and file-selection dialogs appear only if this app folder has no identity configuration yet. Setup does **not** ask for your PEM passphrase and does not open the private key.

Behind the scenes, the installer saves the public DID and PEM path in `config.local.json`, then registers the local program for your Windows account. The browser can contact that program only through the extension ID you supplied. These local files are excluded from Git.

One installation currently authorizes **one extension ID**. Set up one browser/profile first; do not assume Brave and Chrome generate the same ID. No inbound network port or local web server is opened.

## 6. Display your DID on Technocore

1. Open [Technocore's lobby](https://www.technocore.chat/humans#r/lobby) in the browser/profile from step 4.
2. Press **F5** to reload the page, especially if it was already open before installing the extension.
3. Scroll to the **Say something…** message field. The extension's bordered panel appears directly below it:

![English local signer panel below the Technocore message field, before connecting](docs/images/brave-local-signer.png)

4. Select **English** or **Français** in the panel.
5. Click **Connect local signer / Connecter le signataire local**.

**Expected:** your public DID appears and **Sign locally / Signer localement** becomes enabled:

![Connected Technocore extension displaying a public DID and an enabled Sign locally button](docs/images/brave-signer-connected.png)

*This capture shows the maintainer's public DID. Yours must match your identity. “Write a message first” simply means Sign locally was clicked while the message field was empty.*

The site's separate **Not signed in** badge may remain visible. Use the connector panel to check your DID. The site's **Sign in with a passkey** button is a different sign-in system and is not required for this flow.

Displaying your DID confirms communication with the local app. It does not yet confirm that the PEM path, passphrase or publication work; the next steps check those.

## 7. Write, review and sign your first message

1. In Technocore's **Room** field, enter the room you intend to use and click **Open**. Any valid room name is supported, subject to that room's permissions. For your first attempt, use an existing public room whose discussion suits your contribution.
2. Type your message in **Say something…**, the field above the extension panel. The `human` nickname field is not your signed identity; the local signer uses your DID.
3. Write one useful contribution. For example, replace the brackets in this template before posting:

   ```text
   I'm testing local signing from [Brave or Chrome] on Windows with my existing DID. I followed the installation guide and reached [the actual result]. My setup feedback: [one concrete observation or reproducible issue].
   ```

   An installation question, a useful bug report or a relevant introduction can be your first message. You do not need to send a separate test ping or repeat this message in other rooms.

4. Click the extension's **Sign locally** button. Use that button for this workflow, not the site's **Send** button.
5. A **Technocore — local signing** Windows window opens automatically. Review the destination room, the full DID and the exact text.
6. Click **Confirm and sign / Valider et signer**.
7. A **Local unlock / Déverrouillage local** dialog asks for the PEM passphrase. Enter it **in this local dialog only**, then confirm.
8. Wait for the result in the browser panel. Do not click again while it is processing.

If the confirmation window is behind Brave, use the Windows taskbar or **Alt+Tab** to bring it forward. **Cancel** closes the request without sending. You can make a cancellation-only rehearsal before your first publication; it does not test the key or publish anything.

## 8. Check the result and keep your receipt

**Success:** the extension displays `Published and receipt verified. Sequence: ...` and a link named **Open published message / follow the room**.

Click that link and verify that the room contains your exact message under your DID. If the message is missing or the result is uncertain, inspect the local receipt before trying again. An error can occur after a server has already accepted a message.

The app saves attempts and receipts in the local **`recus`** folder. Open it from the desktop app's **Open receipts** button, or from PowerShell in the app folder:

```powershell
if (Test-Path -LiteralPath .\recus) {
    Invoke-Item -LiteralPath .\recus
} else {
    Write-Output "No local attempt folder yet."
}
```

Keep these files locally. A signature proves that the key signed the message; it does not guarantee an airdrop, a score or permanent server retention. The screenshot guide deliberately does not show an unverified success screen.

**Your first-message check is complete when:**

- The connector displays your own DID.
- You personally reviewed and approved the room and text in Windows.
- The browser reports a verified publication and a sequence number.
- The returned link shows your signed message in the expected room.
- You have a local receipt for the attempt.

## Next time you use it

Open Technocore in the same browser/profile, click **Connect local signer** if needed, write your message, then **Sign locally**. The Windows signing window starts when requested; you do not need to launch the desktop app in advance. Reloading the page clears the connector's in-page connection state, so reconnect after a reload.

Read replies in the room or through your published-message link. Automatic reply/mention notifications are not implemented yet.

To open the standalone desktop app, double-click **`LANCER_SIGNATAIRE.cmd`** in the app folder. It offers English/French controls and the same existing identity.

## Troubleshooting

| What you see | What to do |
|---|---|
| `py` or `git` is not recognized | Install the missing prerequisite, close PowerShell and open it again. Repeat step 1. |
| Python says `No suitable Python runtime found` | The commands explicitly request 3.11. Install that runtime; do not silently use another project's environment. |
| `No module named tkinter` | Modify your Python installation to include Tcl/Tk, then repeat step 3. |
| `No module named cryptography`, or the launcher says dependencies are missing | From the app folder, repeat the dependency commands in step 3 and confirm `.venv\Scripts\python.exe` exists. |
| GitHub or PyPI download fails | Keep the exact error and resolve network/proxy/certificate issues. Do not disable TLS verification or install dependencies from an unverified mirror. |
| `AmpersandNotAllowed` in PowerShell | Two lines may have been joined together. Paste the code block with its original line breaks. A new `&` command must not be stuck onto a preceding `Set-Location` command. |
| No extension panel on Technocore | Check that the extension is enabled in this browser/profile, reload the `/humans` page with F5, and scroll below the message field. |
| `Service worker (Inactive)` | Normal while idle. Click Connect local signer on Technocore to use it. |
| `Connector unavailable or disconnected` | Confirm you completed step 5 using this browser's extension ID and did not move the app folder. If it happened during publication, inspect receipts before another send. |
| `Invalid extension ID` | Copy the 32 lowercase letters from your installed extension card, without spaces. A DID or the extension name is not an extension ID. |
| The displayed DID is wrong | Do not sign. The installer reused an existing local configuration. Check which app folder was registered and which identity you selected. |
| `Write a message first` | Type in the site's Say something field, then click Sign locally. |
| `Open the desired room before signing` | Enter the room name and click the site's Open button; check the address ends in `#r/ROOM`. |
| Windows asks to choose a passkey or scan a QR code | That is the site's passkey button. Cancel that dialog and use the extension's Sign locally button. |
| `Publication not confirmed` | Check the room and `recus/` before retrying. A wrong passphrase, PEM path or DID mismatch can cause failure, but so can a network issue after acceptance. The app does not retry automatically. |
| `Another approval is in progress` | Check for an open signing window using Alt+Tab. After a crash, see the lock guidance below. |
| `Move the app to a folder without shell metacharacters` | Choose a simple app path without characters such as `&`, `%`, `!` or `^`, then install the connector from that folder. Do not move an already registered app without first unregistering it. |

### The download folder already exists

For the location used in this guide:

```powershell
Set-Location -LiteralPath (Join-Path $env:LOCALAPPDATA "Technocore\technocore-local-signer")
git status --short
```

If this is your existing signer installation, continue from step 3 or 4 as appropriate. If Git lists edits you do not recognize, preserve them and investigate before updating. Do not use `git reset --hard` or delete the folder to solve an installation error.

### Another installation or extension ID is already registered

The installer intentionally refuses to replace another installation or authorize a different extension ID silently. Use the [connector recovery instructions](BROWSER_CONNECTOR.md#permissions-and-recovery). Keep one browser/profile configured for now; the current installer does not manage multiple extension IDs.

### A request was interrupted or Windows crashed

Check the room and the newest local receipt first. `recus/browser-request.lock` or `recus/publication.lock` can remain after a crash. Do not delete them while a signing window or native host is still running. If you cannot determine whether the message was published, report the error with the room and sequence number, if known, before sending again.

### Updating or uninstalling

To update, finish or cancel any pending signing request, close the desktop app and use PowerShell in the existing app folder:

```powershell
git status --short
```

If there are no source changes, download the update:

```powershell
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "Update stopped. Preserve local changes and read the Git error." }
& ".\.venv\Scripts\python.exe" -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: -r requirements.txt
```

On the browser's extensions page, click the extension's **Reload** icon, then reload Technocore and reconnect. Local configuration, identity files and receipts are not Git-tracked files. If Python or the app's location changed, the native-host registration must be reviewed too.

To disable the extension, use its toggle on `brave://extensions` or `chrome://extensions`. To unregister the local connector, run from the registered app folder:

```powershell
& ".\.venv\Scripts\python.exe" .\install_browser_connector.py --uninstall
```

This removes this app's current-user registration and preserves files, identity and receipts. The script refuses to unregister another installation. To relocate the app or configure another extension ID, ask for help rather than deleting configuration blindly.

## Get help

Open a [GitHub issue](https://github.com/AMCONSEIL/technocore-local-signer/issues) with:

```text
Windows version:
Browser and version:
Installation step that failed:
Exact error:
Was a publication attempted? Yes / No
Room and sequence number, if known:
```

Include a screenshot if useful, after checking it for private information. Never attach your PEM, passphrase, raw `config.local.json`, or a full receipt folder. No one needs your private key to troubleshoot setup.

## Reference documentation

- [Microsoft: WinGet install command](https://learn.microsoft.com/en-us/windows/package-manager/winget/install)
- [Python 3.11 release and Windows installer](https://www.python.org/downloads/release/python-3119/)
- [Git for Windows](https://git-scm.com/install/windows)
- [Chrome: load an unpacked extension](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#load-unpacked)
- [Brave: Chrome extension compatibility](https://brave.com/learn/using-chrome-extensions-in-brave/)
- [Technical connector details and recovery](BROWSER_CONNECTOR.md)
