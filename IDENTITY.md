# Identité publique du projet

DID du porteur du projet :

`did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD`

Compte GitHub de publication : [AMCONSEIL](https://github.com/AMCONSEIL).

Ce fichier attribue le projet au DID ci-dessus. Le DID est un identifiant public de clé Ed25519 ; il n'expose pas la clé privée et ne constitue pas une identité civile.

## Preuve du lien avec une version du code

Une mention dans un README est une déclaration. Une preuve cryptographique complémentaire consiste à publier, sous ce même DID, un message signé contenant l'URL exacte du dépôt et le hash complet du commit concerné.

Statut : annonce signée vérifiée. La [preuve publique](proofs/github-attribution-v1.json) contient uniquement le message d'attribution, son DID, son nonce, sa signature et les références publiques du reçu.

- Dépôt déclaré : https://github.com/AMCONSEIL/technocore-local-signer
- Version du code désignée : `4adea7dd9afbdfefdc937734595e3f2f96e0982c`.
- Publication : salon `dev`, séquence `54147`, date serveur `2026-09-15T22:27:23.827828Z`.
- Format signé : les octets UTF-8 exacts de `room + "|" + nonce + "|" + text`.
- Signature : Ed25519, encodée en base64url sans remplissage ; clé publique extraite du DID `did:key`.

La preuve vise le commit initial ci-dessus, pas les versions futures. La séquence et la date sont des informations du serveur et ne sont pas couvertes par la signature de l'auteur. Le dépôt conserve le message signé pour permettre une vérification même si l'historique du salon expire.

Vérification locale, depuis le dossier du dépôt après installation des dépendances :

```python
import json
from pathlib import Path
from signature_locale import canonical, verify

proof = json.loads(Path("proofs/github-attribution-v1.json").read_text(encoding="utf-8"))
_, payload = canonical(proof["room"], proof["nonce"], proof["text"])
verify(proof["did"], proof["sig"], payload)
print("Signature Ed25519 valide ; relire le texte pour vérifier le dépôt et le commit.")
```

Ce fichier n'inclut ni configuration personnelle, ni chemin local, ni clé privée, ni messages d'autres participants.

La vérification consiste à contrôler la signature Ed25519 de l'annonce, puis l'URL du dépôt et le commit qu'elle désigne. Cela prouve que le détenteur de la clé a signé cette déclaration ; cela ne prouve pas à lui seul l'antériorité du développement ou la qualité du code.

La clé privée, la passphrase, les configurations personnelles et les reçus locaux ne font pas partie du code publié.
