# Identité publique du projet

DID du porteur du projet :

`did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD`

Compte GitHub de publication : [AMCONSEIL](https://github.com/AMCONSEIL).

Ce fichier attribue le projet au DID ci-dessus. Le DID est un identifiant public de clé Ed25519 ; il n'expose pas la clé privée et ne constitue pas une identité civile.

## Preuve du lien avec une version du code

Une mention dans un README est une déclaration. Une preuve cryptographique complémentaire consiste à publier, sous ce même DID, un message signé contenant l'URL exacte du dépôt et le hash complet du commit concerné.

Statut : cette annonce signée sera préparée après la publication du dépôt. Aucune signature liant le DID à un commit GitHub n'est encore fournie dans cette version.

La vérification consiste à contrôler la signature Ed25519 de l'annonce, puis l'URL du dépôt et le commit qu'elle désigne. Cela prouve que le détenteur de la clé a signé cette déclaration ; cela ne prouve pas à lui seul l'antériorité du développement ou la qualité du code.

La clé privée, la passphrase, les configurations personnelles et les reçus locaux ne font pas partie du code publié.
