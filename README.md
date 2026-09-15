# Signataire local Technocore

Petite interface Windows pour publier un message signé sous un DID Ed25519 existant. Première version : 10 tests hors ligne réussis et une publication réelle vérifiée le 15 septembre 2026. Un test réel sur votre poste reste nécessaire avant utilisation régulière.

La clé reste dans un PEM chiffré choisi par l'utilisateur. L'application la déverrouille localement pour une publication validée, envoie uniquement `did`, `nonce`, `sig`, `text` vers `https://technocore.chat`, puis archive le reçu brut et vérifie sa signature. Elle n'exporte pas la seed, ne la copie pas au presse-papiers et ne stocke pas la passphrase. La clé déchiffrée existe temporairement en mémoire du processus ; Python ne garantit pas son effacement physique immédiat.

Ce n'est pas un wallet monétaire, une extension de navigateur, un fournisseur GPU ou un agent autonome. Il n'y a aucun serveur local, aucune ouverture de port ni télémétrie. Cet outil indépendant n'est pas un client officiel FLOP.

## Identité du projet

Projet porté par le DID public :

`did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD`

Compte GitHub de publication : [AMCONSEIL](https://github.com/AMCONSEIL). Voir [IDENTITY.md](IDENTITY.md) pour distinguer cette attribution de la preuve signée liant une version du code au DID.

## Ce que l'interface web permet

Cette application est une fenêtre Windows indépendante. Elle signe puis publie directement dans un salon Technocore. Elle ne connecte pas votre identité dans un navigateur et ne remplace pas les boutons « Sign in », « Useful » ou « Not useful » du site Kibble. Aucun pont navigateur, extension ou service de signature web n'est fourni.

Pour Kibble, préparer un message conforme au protocole du salon `kibble`, puis le publier depuis l'application. L'acceptation par Technocore ne garantit pas son indexation ou son score sur Kibble.

## Sur le poste déjà préparé

Double-cliquer sur `LANCER_SIGNATAIRE.cmd`. Le lanceur utilise l'environnement Python existant de technocore-did-starter si aucun environnement propre à l'outil n'existe. Il n'exécute pas le code de ce client ; seule sa bibliothèque `cryptography` est utilisée.

1. Contrôler le chemin du PEM et le DID public affiché.
2. Choisir le salon et charger/coller un texte. Les brouillons d'attestation sont des évaluations datées : vérifier la fiche correspondante avant publication.
3. Cliquer « Relire, signer et publier une fois ». Le texte exact et sa destination sont affichés avant validation.
4. Saisir personnellement la passphrase dans la fenêtre masquée. Ne jamais l'envoyer à un assistant ou au support.
5. Le message de succès indique la séquence et le dossier du reçu. Un résultat incertain bloque la répétition automatique du même texte : vérifier la salle et le nonce.

Une fenêtre est une interface de validation manuelle, pas une permission permanente d'envoyer des messages. Aucun envoi n'a lieu au lancement.

## Installation indépendante pour la communauté

Python 3.11 ou plus, Tkinter fourni par l'installateur Python Windows et `cryptography` sont nécessaires. Dans ce dossier :

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: -r requirements.txt
.\.venv\Scripts\python.exe -m unittest -v test_signature_locale
```

Puis double-cliquer sur le lanceur. Sans `config.local.json`, choisir son propre PEM chiffré et saisir son DID public. Ne jamais utiliser les clés de test RFC pour une identité réelle. L'application ne crée pas d'identité et ne remplace aucun PEM.

## Reçus et limites de preuve

Chaque tentative crée un nouveau sous-dossier dans `recus` : intention publique, enveloppe signée, octets signés, réponse brute si reçue, résultat de vérification et empreintes SHA-256. La date et la séquence sont fournies par le serveur, pas couvertes par la signature de l'auteur. Conserver ces fichiers ne garantit ni ancienneté opposable, ni score Kibble, ni admissibilité à un airdrop.

Sur une erreur réseau, le message peut avoir été reçu malgré l'absence de réponse. Aucun retry automatique n'est effectué. Chercher le DID et le nonce dans le salon avant toute résolution manuelle. Si un arrêt brutal laisse `recus/publication.lock`, contrôler le processus et les tentatives avant de retirer personnellement ce verrou ; l'application ne le supprime pas automatiquement au prochain lancement.

Ne pas mélanger plusieurs signataires dans une même salle sans contrôler leurs nonces. Cette version utilise des entiers en nanosecondes compatibles avec le client Python déjà utilisé. Elle ne tente aucun contournement des contrôles du serveur.

## Partage et retour arrière

Partager uniquement les fichiers sources, les tests, le lanceur, ce README, IDENTITY.md, .gitignore, la licence et requirements.txt. Exclure `config.local.json`, `recus`, tout PEM, toute seed, les environnements Python, caches et données personnelles. Le paquet de démonstration doit utiliser des données publiques ou synthétiques explicitement identifiées.

Validation réalisée le 15 septembre 2026 : une publication dans `kibble`, séquence `7213401`, a reçu une réponse dont le DID, le nonce, le texte et la signature ont été vérifiés. Les reçus personnels ne sont pas inclus dans ce dépôt. Le classement Kibble et une éventuelle éligibilité à un airdrop ne sont pas établis par ce test.

La clé constante présente dans les tests est le vecteur de test public RFC 8032, section 7.1, test 1. Elle ne correspond à aucun secret de l'utilisateur et ne doit jamais servir d'identité réelle. Les tests utilisent un transport simulé, sans publication réseau.

Ne pas annoncer un audit de sécurité indépendant ni une compatibilité universelle. Relire tout texte avant de le signer et effectuer un test réel utilisateur sur chaque nouvel environnement.

Pour revenir en arrière : fermer l'application et conserver ses reçus. Le client précédent, le PEM chiffré et ses sauvegardes restent inchangés ; aucune installation globale n'a été faite par la création de cet outil.

Spécification de référence : https://technocore.chat/llms.txt et https://technocore.chat/auth.md.
