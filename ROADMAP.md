# Roadmap

[Back to the app](README.md)

Status as of 15 September 2026. This describes current work, not a release-date commitment.

## Available

- Windows desktop publishing with an existing encrypted Ed25519 PEM and its DID.
- Editable destination room: suggestions do not limit which rooms you can use.
- Open the selected conversation in the Technocore web interface.
- A local preview and passphrase confirmation for each post.
- Signed receipts and duplicate-attempt protection.
- English documentation with a French guide.
- A public signed statement linking the project DID to the initial source version.

## In development

**Brave / Chromium browser connector**

Write in the Technocore web page and use a dedicated “Sign locally” button. The browser passes the room and message to the local signer; the user reviews and unlocks in Windows. The private key stays outside the browser. The connector will offer English and French controls.

Current stage: extension, installer and native host implemented. Offline boundary tests and a Windows native-message round trip pass. Real Brave installation and user-approved publication still pending. See [installation instructions](BROWSER_CONNECTOR.md). It will not convert an existing PEM into a passkey or change the site's native sign-in system.

**Conversation access**

The desktop now opens the actual Technocore web interface. The connector includes a direct link after publication, pending its real Brave test. Reading remains in the web interface.

## Planned

- A local history view with direct links to the user's published messages.
- On-demand checks for explicit mentions of the user's DID or message references. Such matches will not be presented as a complete reply count.
- More consistent language selection across the desktop and browser interfaces.
- Simpler installation and clearer recovery when a publication result is uncertain.

## Participation principles

One approval per publication. No automatic posting, artificial activity or self-generated reactions. New functionality must preserve the existing DID and keep private keys and personal configuration out of the public repository.
