# Roadmap

[Back to the app](README.md)

Status as of 15 September 2026. This describes current work, not a release-date commitment.

## Available

- Windows desktop publishing with an existing encrypted Ed25519 PEM and its DID.
- Editable destination room: suggestions do not limit which rooms you can use.
- Open the selected conversation in the Technocore web interface.
- A local preview and passphrase confirmation for each post.
- Signed receipts and duplicate-attempt protection.
- English / French desktop controls, with English as the default and a saved language preference.
- English documentation with a French guide.
- An illustrated Windows installation guide with copy-and-paste commands, real Brave screenshots and troubleshooting.
- A public signed statement linking the project DID to the initial source version.

## In development

**Brave / Chrome browser connector**

Write in the Technocore web page and use a dedicated “Sign locally” button. The browser passes the room and message to the local signer; the user reviews and unlocks in Windows. The private key stays outside the browser. The connector offers English and French controls.

Current stage: extension, installer and native host implemented. Offline boundary tests and a Windows native-message round trip pass; the panel and public DID connection have been observed in Brave. User-approved end-to-end publication still needs verification in Brave and Chrome. See the [illustrated installation guide](INSTALLATION.md). It will not convert an existing PEM into a passkey or change the site's native sign-in system.

**Conversation access**

The desktop now opens the actual Technocore web interface. The connector includes a direct link after publication, pending real browser tests. Reading remains in the web interface.

## Planned

- A local history view with direct links to the user's published messages.
- On-demand checks for explicit mentions of the user's DID or message references. Such matches will not be presented as a complete reply count.
- Simpler installation and clearer recovery when a publication result is uncertain.

## Participation principles

One approval per publication. No automatic posting, artificial activity or self-generated reactions. New functionality must preserve the existing DID and keep private keys and personal configuration out of the public repository.
