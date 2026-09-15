"""Signature Ed25519 et publication Technocore. Aucun accès disque/réseau à l'import."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import time
import unicodedata
import urllib.error
import urllib.request
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

ORIGIN = "https://technocore.chat"
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
MAX_RESPONSE = 2 * 1024 * 1024


def canonical(room: str, nonce: str, text: str) -> tuple[str, bytes]:
    if re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,47}", room) is None:
        raise ValueError("Nom de salon invalide.")
    if re.fullmatch(r"[0-9]{1,19}", nonce) is None:
        raise ValueError("Nonce invalide.")
    swept = "".join(" " if unicodedata.category(c) in {"Cc", "Cf", "Cs", "Co", "Zl", "Zp"} else c for c in text).strip()
    if not swept or len(swept) > 4096:
        raise ValueError("Le message doit contenir de 1 à 4096 caractères après normalisation.")
    return swept, f"{room}|{nonce}|{swept}".encode("utf-8")


def did_for(key: Ed25519PrivateKey) -> str:
    raw = b"\xed\x01" + key.public_key().public_bytes_raw()
    n, encoded = int.from_bytes(raw, "big"), ""
    while n:
        n, rem = divmod(n, 58)
        encoded = B58[rem] + encoded
    return "did:key:z" + encoded


def verify(did: str, sig: str, payload: bytes) -> None:
    if not did.startswith("did:key:z6Mk") or len(did) != 56:
        raise ValueError("DID Ed25519 invalide.")
    n = 0
    for c in did[9:]:
        n = n * 58 + B58.index(c)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big")
    if len(raw) != 34 or raw[:2] != b"\xed\x01":
        raise ValueError("Clé publique incompatible.")
    if re.fullmatch(r"[A-Za-z0-9_-]{85}[AQgw]", sig) is None:
        raise ValueError("Signature non canonique.")
    Ed25519PublicKey.from_public_bytes(raw[2:]).verify(base64.urlsafe_b64decode(sig + "=="), payload)


def write_new(path: Path, content: bytes) -> None:
    """Refuse tout écrasement ; conserver aussi un fichier incomplet pour diagnostic."""
    with path.open("xb") as out:
        out.write(content)
        out.flush()
        os.fsync(out.fileno())


def json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "Redirection refusée", headers, fp)


def send_once(room: str, envelope: dict) -> bytes:
    """Un seul POST HTTPS, sans clé ni passphrase, sans suivi de redirection/retry."""
    if set(envelope) != {"did", "nonce", "sig", "text"}:
        raise ValueError("Champs réseau inattendus.")
    req = urllib.request.Request(
        f"{ORIGIN}/r/{room}?format=json",
        data=json_bytes(envelope), method="POST",
        headers={"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"},
    )
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(req, timeout=20) as response:
        raw = response.read(MAX_RESPONSE + 1)
    if len(raw) > MAX_RESPONSE:
        raise ValueError("Réponse trop volumineuse ; résultat de l'envoi à vérifier.")
    return raw


def check_receipt(room: str, envelope: dict, raw: bytes) -> dict:
    response = json.loads(raw)
    if not isinstance(response, dict) or response.get("room") != room:
        raise ValueError("Le reçu ne correspond pas au salon.")
    posted = response.get("posted")
    if not isinstance(posted, dict):
        raise ValueError("Le serveur n'a pas fourni de reçu posted.")
    nonce = posted.get("nonce")
    if isinstance(nonce, bool) or not isinstance(nonce, (int, str)) or str(nonce) != envelope["nonce"]:
        raise ValueError("Le nonce du reçu ne correspond pas.")
    if posted.get("from") != envelope["did"] or posted.get("text") != envelope["text"] or posted.get("sig") != envelope["sig"]:
        raise ValueError("Le reçu ne correspond pas au message signé.")
    if type(posted.get("seq")) is not int or posted["seq"] <= 0 or not isinstance(posted.get("ts"), str):
        raise ValueError("Séquence/date absente du reçu.")
    _, payload = canonical(room, envelope["nonce"], posted["text"])
    verify(envelope["did"], posted["sig"], payload)
    return posted


def publish(key_path: Path, password: str, expected_did: str, room: str,
            text: str, receipts: Path, transport=send_once) -> tuple[Path, dict]:
    """Appelé seulement après action explicite de l'utilisateur dans l'interface."""
    text, _ = canonical(room, "1", text)
    if not expected_did.startswith("did:key:z6Mk"):
        raise ValueError("Renseigner le DID attendu avant de signer.")
    if not password:
        raise ValueError("La passphrase du fichier chiffré est nécessaire.")
    # Seul cet appel utilisateur ouvre le PEM. Aucun export de seed n'existe.
    try:
        key = serialization.load_pem_private_key(key_path.read_bytes(), password=password.encode("utf-8"))
    except (ValueError, TypeError) as exc:
        raise ValueError("Passphrase incorrecte ou PEM chiffré invalide.") from exc
    if not isinstance(key, Ed25519PrivateKey) or did_for(key) != expected_did:
        raise ValueError("La clé ne correspond pas au DID attendu : aucun envoi.")

    receipts.mkdir(parents=True, exist_ok=True)
    # Verrou commun aux fenêtres pour sérialiser les nonces et éviter les doublons.
    lock_path = receipts / "publication.lock"
    try:
        lock_fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError("Une publication est en cours ou un arrêt a laissé publication.lock. Vérifier les reçus avant de relancer.") from exc
    os.close(lock_fd)
    attempt = None
    try:
        fingerprint = hashlib.sha256(f"{expected_did}|{room}|{text}".encode()).hexdigest()
        nonce = time.time_ns()
        for entry in receipts.glob("*/intention.json"):
            saved = json.loads(entry.read_bytes())
            if saved.get("fingerprint") == fingerprint:
                raise ValueError("Ce même message a déjà fait l'objet d'une tentative. Vérifier son reçu avant tout autre envoi.")
            if saved.get("did") == expected_did and saved.get("room") == room:
                nonce = max(nonce, int(saved["nonce"]) + 1)
        text, payload = canonical(room, str(nonce), text)
        sig = base64.urlsafe_b64encode(key.sign(payload)).decode("ascii").rstrip("=")
        verify(expected_did, sig, payload)
        del key
        envelope = {"did": expected_did, "nonce": str(nonce), "sig": sig, "text": text}
        attempt = receipts / (time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:10])
        attempt.mkdir()
        write_new(attempt / "intention.json", json_bytes({
            "schema": "technocore-local-signer-v1", "did": expected_did, "room": room,
            "nonce": str(nonce), "fingerprint": fingerprint,
            "note": "Tentative préparée, pas une preuve de publication ni de récompense.",
        }))
        write_new(attempt / "enveloppe-signee.json", json_bytes(envelope))
        write_new(attempt / "message-signe-utf8.txt", payload)
        # Toutes les écritures préparatoires doivent réussir avant le POST.
        raw = transport(room, envelope)
        write_new(attempt / "reponse-brute.json", raw)
        posted = check_receipt(room, envelope, raw)
        write_new(attempt / "verification.json", json_bytes({
            "status": "published_receipt_verified", "room": room, "did": expected_did,
            "posted_seq": posted["seq"], "server_ts": posted["ts"],
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "limits": "Signature vérifiée. Date serveur non signée par l'auteur. Score Kibble et admissibilité à un airdrop non établis.",
        }))
        return attempt, posted
    except Exception as exc:
        if attempt is not None:
            try:
                write_new(attempt / "A_VERIFIER.txt", (
                    "Résultat non confirmé. Ne pas renvoyer automatiquement.\n"
                    "Vérifier la salle avec le DID et le nonce de l'intention.\n"
                    f"Type d'erreur : {type(exc).__name__}.\n"
                ).encode("utf-8"))
            except OSError:
                pass
            raise RuntimeError(f"Publication non confirmée. Aucun nouvel essai automatique. Dossier de contrôle : {attempt}") from exc
        raise
    finally:
        lock_path.unlink(missing_ok=True)  # Uniquement le verrou créé par cet appel.
