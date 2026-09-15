"use strict";
(() => {
  if (location.pathname !== "/humans" || window.top !== window) return;
  const send = document.getElementById("send");
  const input = document.getElementById("text");
  const roomInput = document.getElementById("room");
  if (!send || !input || !roomInput || document.getElementById("technocore-local-connector")) return;
  const host = document.createElement("div");
  host.id = "technocore-local-connector";
  send.parentElement.insertAdjacentElement("afterend", host);
  const panel = host.attachShadow({mode: "closed"});
  const style = document.createElement("style");
  style.textContent = ":host{display:block;margin:12px 0}section{padding:12px;border:1px solid #00acc8;border-radius:8px;background:#10192d;color:#eef7fc;font:13px system-ui}button,select{padding:7px;margin:4px;border-radius:4px}p{margin:6px;overflow-wrap:anywhere}a{color:#61dbff}";
  panel.append(style);
  const box = document.createElement("section");
  panel.append(box);
  const lang = document.createElement("select");
  lang.setAttribute("aria-label", "Language / Langue");
  for (const [value, label] of [["en", "English"], ["fr", "Français"]]) {
    const option = document.createElement("option"); option.value = value; option.textContent = label; lang.append(option);
  }
  lang.value = navigator.language.startsWith("fr") ? "fr" : "en";
  const connect = document.createElement("button"); connect.type = "button";
  const sign = document.createElement("button"); sign.type = "button"; sign.disabled = true;
  const identity = document.createElement("p");
  const note = document.createElement("p");
  const status = document.createElement("p"); status.setAttribute("role", "status");
  const link = document.createElement("a"); link.hidden = true; link.target = "_blank"; link.rel = "noopener noreferrer";
  box.append(lang, connect, sign, identity, note, status, link);
  let did = ""; let busy = false;
  const labels = {
    en: {connect:"Connect local signer",sign:"Sign locally",hint:"Use this button for your existing DID. The site's passkey sign-in and Send button are separate.",open:"Open published message / follow the room",waiting:"Check the local Windows confirmation window.",connected:"Local signer connected. Private key stays on this PC.",cancelled:"Cancelled: nothing sent.",busy:"Another approval is in progress. Check the local window.",configuration:"Set your DID and encrypted PEM path in the local app configuration.",disconnected:"Connector unavailable or disconnected. Check its installation and local receipts before retrying.",unconfirmed:"Publication not confirmed. Check local receipts; do not resend automatically.",room:"Open the desired room before signing.",empty:"Write a message first.",done:"Published and receipt verified. Sequence: "},
    fr: {connect:"Connecter le signataire local",sign:"Signer localement",hint:"Utilisez ce bouton pour votre DID actuel. La connexion passkey et le bouton Send du site sont indépendants.",open:"Voir le message publié / suivre le salon",waiting:"Vérifiez la fenêtre de confirmation locale Windows.",connected:"Signataire connecté. La clé privée reste sur ce PC.",cancelled:"Annulé : aucun envoi.",busy:"Une validation est déjà en cours. Vérifiez la fenêtre locale.",configuration:"Renseignez le DID et le chemin du PEM chiffré dans la configuration locale.",disconnected:"Connecteur indisponible ou déconnecté. Vérifiez l’installation et les reçus avant tout nouvel essai.",unconfirmed:"Publication non confirmée. Vérifiez les reçus locaux ; ne renvoyez pas automatiquement.",room:"Ouvrez le salon souhaité avant de signer.",empty:"Écrivez d’abord un message.",done:"Publié, reçu vérifié. Séquence : "}
  };
  const t = key => labels[lang.value][key] || labels[lang.value].unconfirmed;
  function render() {
    connect.textContent = t("connect"); sign.textContent = t("sign");
    note.textContent = t("hint"); identity.textContent = did ? "DID: " + did : "";
    link.textContent = t("open"); connect.disabled = busy; sign.disabled = busy || !did;
  }
  lang.addEventListener("change", render);
  function request(message, onSuccess) {
    busy = true; render(); status.textContent = t("waiting");
    try {
      chrome.runtime.sendMessage(message, result => {
        const failed = chrome.runtime.lastError;
        busy = false; render();
        if (failed || !result) { status.textContent = t("disconnected"); return; }
        if (!result.ok) { status.textContent = t(result.code); return; }
        onSuccess(result);
      });
    } catch (_) { busy = false; render(); status.textContent = t("disconnected"); }
  }
  connect.addEventListener("click", event => {
    if (!event.isTrusted || busy) return;
    request({op:"profile"}, result => { did = result.did; render(); status.textContent = t("connected"); });
  });
  sign.addEventListener("click", event => {
    if (!event.isTrusted || busy || !did) return;
    const match = /^#r\/([a-z0-9][a-z0-9_-]{0,47})(?:\/[0-9]+)?$/.exec(location.hash);
    if (!match || roomInput.value.trim() !== match[1]) { status.textContent = t("room"); return; }
    const room = match[1]; const text = input.value;
    if (!text.trim()) { status.textContent = t("empty"); return; }
    link.hidden = true;
    request({op:"publish",room,text,language:lang.value}, result => {
      did = result.did; render(); status.textContent = t("done") + result.seq;
      link.href = location.origin + "/humans#r/" + result.room + "/" + result.seq; link.hidden = false;
      if (input.value === text) input.value = "";
    });
  });
  render();
})();
