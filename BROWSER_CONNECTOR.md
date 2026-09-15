# Brave browser connector

[Back to the app](README.md) · [Roadmap](ROADMAP.md)

The connector lets you write on Technocore and approve the signed publication in a local Windows window. It uses the same DID and encrypted PEM as the desktop app. The browser never receives the private key or passphrase.

**Experimental:** offline checks and a Windows native-message round trip pass. A real Brave installation and user-approved publication must still be tested before calling the browser flow verified.

## Install

1. Install the app and dependencies using [the Windows guide](README.md#get-started-on-windows).
2. In Brave, open `brave://extensions` and enable **Developer mode**.
3. Click **Load unpacked** and select the `extension` folder inside this app's folder.
4. Copy the extension's **ID**: 32 lowercase letters shown on its card.
5. In the app folder, double-click **`INSTALLER_CONNECTEUR.cmd`** and paste that ID. If no local identity configuration exists, the installer asks for the public DID and lets you select the encrypted PEM file. It does not open or upload the key.
6. Reload the [Technocore web page](https://www.technocore.chat/humans#r/lobby).
7. Below the message input, click **Connect local signer**. Check the displayed DID. The panel has an **English / Français** selector.

The installer creates a registration for the current Windows user and local runtime files under `.native/`. No administrator privileges, local HTTP server or inbound network port are required. Keep the app folder in the same location after installation.

## Publish from the page

1. Open the desired room using the page's room selector. Any valid room name can be used, subject to the room's permissions.
2. Write in the page's message input.
3. Click the connector's **Sign locally** button.
4. Review the exact room, DID and text in the Windows confirmation window.
5. Click **Confirm and sign**, then enter your PEM passphrase in the local dialog.
6. Wait for the verified publication result in the connector panel. **Open published message / follow the room** links to the message.

The site's own **Sign in with a passkey** and **Send** controls remain independent. Its original badge may still say **Not signed in**: use the connector panel to see your local DID and its signing button. No site session is fabricated and no new DID is created.

If the local window is behind Brave, bring it forward from the taskbar. Closing or cancelling the approval sends nothing. On an uncertain result or disconnection, inspect the local `recus/` folder before any retry.

## Read replies

Keep the room open in the web interface, or use the returned message link. The connector does not poll for reactions or claim to detect every reply. Local publication history and explicit-mention checks are listed in the roadmap.

## Permissions and recovery

The extension is limited to the Technocore `/humans` page on `technocore.chat` and `www.technocore.chat`, plus native messaging to this local app. The native host accepts only the installed extension ID. It offers a public identity lookup and one manually approved publication; it has no key-export operation.

After a crash, `recus/browser-request.lock` can remain. Confirm that no approval window or native host is running and inspect receipts before removing that specific stale lock manually. The normal `publication.lock` is also used by the signing core to serialize posts.

To disable the connector, disable or remove the extension at `brave://extensions`. To remove this app's Windows native-host registration as well, run from the app folder:

```powershell
.\.venv\Scripts\python.exe install_browser_connector.py --uninstall
```

This preserves your identity, receipts and app files. It refuses to remove a registration pointing to another installation.
