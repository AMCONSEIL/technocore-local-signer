"use strict";
const HOST = "org.amconseil.technocore_signer";
let pending = false;

function allowedSender(sender) {
  try {
    const url = new URL(sender.url);
    return sender.id === chrome.runtime.id && sender.frameId === 0 && !!sender.tab &&
      ["https://technocore.chat", "https://www.technocore.chat"].includes(url.origin) &&
      url.pathname === "/humans";
  } catch (_) { return false; }
}

function validRequest(message) {
  if (!message || typeof message !== "object" || Array.isArray(message)) return false;
  const keys = Object.keys(message).sort().join(",");
  if (keys === "op" && message.op === "profile") return true;
  return keys === "language,op,room,text" && message.op === "publish" &&
    ["en", "fr"].includes(message.language) && typeof message.room === "string" &&
    /^[a-z0-9][a-z0-9_-]{0,47}$/.test(message.room) && typeof message.text === "string" &&
    message.text.trim().length > 0 && message.text.length <= 4096;
}

chrome.runtime.onMessage.addListener((message, sender, reply) => {
  if (!allowedSender(sender) || !validRequest(message)) {
    reply({ok: false, code: "rejected"});
    return false;
  }
  if (pending) {
    reply({ok: false, code: "busy"});
    return false;
  }
  pending = true;
  let port;
  let finished = false;
  function finish(result) {
    if (finished) return;
    finished = true;
    pending = false;
    reply(result);
    if (port) port.disconnect();
  }
  try {
    // A native port keeps the worker alive during the user's local confirmation.
    port = chrome.runtime.connectNative(HOST);
    port.onMessage.addListener(result => {
      if (result && result.ok === true && typeof result.did === "string") {
        const clean = {ok: true, did: result.did};
        if (message.op === "publish") {
          if (result.room !== message.room || !Number.isSafeInteger(result.seq) || result.seq <= 0) {
            finish({ok: false, code: "unconfirmed"});
            return;
          }
          clean.room = result.room;
          clean.seq = result.seq;
        }
        finish(clean);
      } else {
        const codes = ["cancelled", "busy", "configuration", "unconfirmed", "host_error"];
        finish({ok: false, code: codes.includes(result?.code) ? result.code : "unconfirmed"});
      }
    });
    port.onDisconnect.addListener(() => {
      const ignored = chrome.runtime.lastError;
      finish({ok: false, code: "disconnected"});
    });
    port.postMessage(message);
  } catch (_) {
    finish({ok: false, code: "disconnected"});
  }
  return true;
});
