# Signataire local Technocore

[English](README.md) | **Français**

**Publiez sous votre DID existant sans coller votre clé privée dans un site web.**

L’application conserve la clé chiffrée sur votre ordinateur. Vous choisissez le salon, rédigez un message et vérifiez le texte avant de déverrouiller la clé localement. Le message signé est envoyé à Technocore et un reçu est conservé.

## Installation et utilisation

Le [guide principal en anglais](README.md#get-started-on-windows) donne les commandes d’installation. Il faut Python 3.11, Git, un PEM Ed25519 chiffré existant, sa passphrase et le DID public correspondant.

Après installation, double-cliquez sur **LANCER_SIGNATAIRE.cmd**.

1. Cliquez sur **Choisir…** pour sélectionner votre PEM chiffré.
2. Renseignez votre **DID public attendu**.
3. Dans **Salon**, écrivez le nom du salon souhaité. Vous pouvez saisir un nom différent des suggestions ; les permissions du salon s’appliquent.
4. Rédigez votre message ou utilisez **Charger un texte…**.
5. Cliquez sur **Relire, signer et publier une fois**, vérifiez l’aperçu puis choisissez **Valider et déverrouiller la clé**.
6. Saisissez la passphrase dans la fenêtre locale et attendez la confirmation. **Ouvrir les reçus** affiche les preuves conservées sur votre PC.

Faites un premier test réel sur votre poste avant un usage régulier. En cas de résultat incertain, vérifiez le salon et les reçus avant tout nouvel envoi.

## Lire les réponses

**Lire le salon** ouvre l’interface web du salon pour suivre la conversation. L’application ne détecte pas encore automatiquement les réponses, réactions ou mentions. Conservez vos reçus : l’historique d’un salon peut expirer.

## En développement

Un connecteur Brave permettra d’écrire sur Technocore, de cliquer sur **Signer localement**, puis de confirmer dans Windows avec le même DID. L’installation navigateur et le test utilisateur complet restent à réaliser. Voir la [feuille de route](ROADMAP.md).

## Identité et code

DID du projet : `did:key:z6Mkt3DNtpGBNh1KHYwLQEk6QtCcJ7vVaRPze1SU7MyhFMVD`.

[Preuve d’attribution signée](IDENTITY.fr.md) · [Licence MIT](LICENSE) · [Documentation technique](DEVELOPMENT.md)
