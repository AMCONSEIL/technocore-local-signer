# Public project identity

**English** | [Français](IDENTITY.fr.md)

Project maintainer's public DID:

`did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD`

Publishing GitHub account: [AMCONSEIL](https://github.com/AMCONSEIL).

This document attributes the project to the DID above. A DID identifies an Ed25519 public key; it does not disclose the private key or establish a person's legal identity.

## Signed link to a source version

A README attribution is a declaration. The [verified public statement](proofs/github-attribution-v1.json) adds a cryptographic signature from this DID over a message naming the repository and the complete initial commit hash.

- Declared repository: https://github.com/AMCONSEIL/technocore-local-signer
- Referenced source commit: `4adea7dd9afbdfefdc937734595e3f2f96e0982c`.
- Publication: `dev` room, sequence `54147`, server timestamp `2026-09-15T22:27:23.827828Z`.
- Signed payload: the exact UTF-8 bytes of `room + "|" + nonce + "|" + text`.
- Signature: Ed25519, encoded as unpadded base64url; the public key is extracted from the `did:key` identifier.

The statement names that initial commit, not future versions. Its server sequence number and timestamp are not covered by the author's signature. Keeping the signed statement in the repository allows verification even after the room history expires.

## Verify locally

After installing the dependencies, run this Python snippet from the repository directory:

```python
import json
from pathlib import Path
from signature_locale import canonical, verify

proof = json.loads(Path("proofs/github-attribution-v1.json").read_text(encoding="utf-8"))
_, payload = canonical(proof["room"], proof["nonce"], proof["text"])
verify(proof["did"], proof["sig"], payload)
print("Valid Ed25519 signature; read the statement to check the repository and commit.")
```

Verification establishes that the key holder signed the statement. It does not, by itself, establish when development began or the quality of the code.

The proof contains only the public attribution message, its DID, nonce, signature and public receipt references. It does not include private keys, passphrases, local paths, personal configuration or other participants' messages. Raw local receipts are not published.
