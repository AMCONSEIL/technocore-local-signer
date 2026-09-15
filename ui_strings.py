"""UI translations only; no signing or filesystem operations."""
TEXT = {
    "title": ("Technocore — local signing", "Technocore — signature locale"),
    "heading": ("Sign with your DID, keeping your key on this computer", "Signer sous votre DID, avec votre clé sur cet ordinateur"),
    "privacy": ("Your key and passphrase stay on this computer. Every message will be public.", "La passphrase et la clé restent sur cet ordinateur. Chaque message sera public."),
    "key_label": ("Existing encrypted PEM file", "Fichier PEM chiffré existant"),
    "browse": ("Browse…", "Choisir…"),
    "did_label": ("Expected public DID (checked before sending)", "DID public attendu (contrôlé avant tout envoi)"),
    "room": ("Room:", "Salon :"),
    "read_room": ("Read room", "Lire le salon"),
    "load_text": ("Load text…", "Charger un texte…"),
    "contribution": ("Message — check the relevant request and result before posting an attestation", "Contribution — vérifiez la demande et le résultat concernés avant une attestation"),
    "publish": ("Review, sign and publish once", "Relire, signer et publier une fois"),
    "receipts": ("Open receipts", "Ouvrir les reçus"),
    "ready": ("Ready. No key loaded. No message sent.", "Prêt. Aucune clé chargée. Aucun message envoyé."),
    "receipt_note": ("Receipts preserve the signed message and the server response.", "Les reçus conservent le message signé et la réponse du serveur."),
    "choose_key": ("Select your encrypted PEM", "Choisir votre PEM chiffré"),
    "encrypted_key": ("Encrypted key", "Clé chiffrée"),
    "text_file": ("Text", "Texte"),
    "too_large": ("The file is too large for one message.", "Fichier trop volumineux pour un message."),
    "not_loaded": ("Text not loaded", "Texte non chargé"),
    "no_receipts": ("No attempts have been saved yet.", "Aucune tentative n’a encore été enregistrée."),
    "did_required": ("Enter your expected public DID.", "Renseignez votre DID public attendu."),
    "message": ("Message", "Message"),
    "preview_title": ("Review the exact publication", "Vérifier la publication exacte"),
    "preview_details": ("Destination: {url}\nIdentity: {did}", "Destination : {url}\nIdentité : {did}"),
    "cancel": ("Cancel", "Annuler"),
    "unlock_title": ("Local unlock", "Déverrouillage local"),
    "password": ("Encrypted PEM passphrase (stays on this computer):", "Passphrase du PEM chiffré (reste sur cet ordinateur) :"),
    "sending": ("Signing locally, then sending one HTTPS request. Wait for the result before closing.", "Signature locale puis un seul envoi HTTPS. Attendre le résultat avant de fermer."),
    "approve": ("Confirm and unlock the key", "Valider et déverrouiller la clé"),
    "published": ("Published: {room} / seq {seq}. Receipt signature verified.\nReceipt: {folder}", "Publié : {room} / seq {seq}. Signature du reçu vérifiée.\nReçu : {folder}"),
    "error": ("{detail}", "{detail}"),
    "confirmed": ("Publication confirmed", "Publication confirmée"),
    "unconfirmed": ("Publication not confirmed", "Publication non confirmée"),
    "in_progress": ("Sending", "Envoi en cours"),
    "wait": ("Wait for the result before closing. No automatic retry will be made.", "Attendre le résultat avant de fermer. Aucun nouvel essai automatique ne sera effectué."),
    "preferences_error": ("The language changed, but the preference could not be saved.", "La langue a changé, mais le choix n’a pas pu être enregistré."),
}

ERRORS = {
    "Nom de salon invalide.": "Invalid room name.",
    "Nonce invalide.": "Invalid nonce.",
    "Le message doit contenir de 1 à 4096 caractères après normalisation.": "The normalized message must contain between 1 and 4096 characters.",
    "DID Ed25519 invalide.": "Invalid Ed25519 DID.",
    "Clé publique incompatible.": "Incompatible public key.",
    "Signature non canonique.": "Non-canonical signature.",
    "Champs réseau inattendus.": "Unexpected network fields.",
    "Réponse trop volumineuse ; résultat de l'envoi à vérifier.": "Response too large; check whether the message was published.",
    "Renseigner le DID attendu avant de signer.": "Enter the expected public DID before signing.",
    "La passphrase du fichier chiffré est nécessaire.": "The encrypted file's passphrase is required.",
    "Passphrase incorrecte ou PEM chiffré invalide.": "Incorrect passphrase or invalid encrypted PEM.",
    "La clé ne correspond pas au DID attendu : aucun envoi.": "The key does not match the expected DID. Nothing was sent.",
    "Une publication est en cours ou un arrêt a laissé publication.lock. Vérifier les reçus avant de relancer.": "A publication is in progress or a crash left publication.lock. Check receipts before restarting.",
    "Ce même message a déjà fait l'objet d'une tentative. Vérifier son reçu avant tout autre envoi.": "This exact message has already been attempted. Check its receipt before sending again.",
}


def translate_error(detail, language):
    if language == "fr":
        return detail
    prefix = "Publication non confirmée. Aucun nouvel essai automatique. Dossier de contrôle : "
    if detail.startswith(prefix):
        return "Publication not confirmed. No automatic retry. Check this folder: " + detail[len(prefix):]
    return ERRORS.get(detail, detail)
