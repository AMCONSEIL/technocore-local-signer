"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
let listener, nativeCalls = 0, port, replies = [];
const id = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const context = {URL, chrome: {runtime: {
  id, lastError: null,
  onMessage: {addListener(fn) { listener = fn; }},
  connectNative() {
    nativeCalls++;
    port = {
      onMessage: {addListener(fn) { port.receive = fn; }},
      onDisconnect: {addListener(fn) { port.closed = fn; }},
      postMessage(message) { port.sent = message; },
      disconnect() {}
    };
    return port;
  }
}}};
vm.runInNewContext(fs.readFileSync(require("node:path").join(__dirname, "background.js"), "utf8"), context);
const good = {id, frameId: 0, tab: {id: 1}, url: "https://www.technocore.chat/humans#r/lobby"};
const request = {op: "publish", room: "custom-room", text: "A useful message", language: "en"};
const reply = value => replies.push(value);
for (const sender of [{...good, url:"https://evil.example/humans"}, {...good, frameId:1},
  {...good, id:"other-extension"}, {...good, url:"https://www.technocore.chat.evil.example/humans"},
  {...good, url:"https://www.technocore.chat/humans-extra"}]) {
  assert.equal(listener(request, sender, reply), false);
}
assert.equal(nativeCalls, 0);
for (const invalid of [{...request, seed:"do-not-accept"}, {...request, room:"../room"}, {op:"export_seed"}]) {
  assert.equal(listener(invalid, good, reply), false);
}
assert.equal(nativeCalls, 0);
assert.equal(listener(request, good, reply), true);
assert.equal(nativeCalls, 1);
assert.equal(listener(request, good, reply), false);
assert.equal(nativeCalls, 1);
port.receive({ok:true, did:"public-did", room:"custom-room", seq:42, key_path:"must-not-leak", password:"must-not-leak"});
assert.deepEqual(JSON.parse(JSON.stringify(replies.at(-1))), {ok:true,did:"public-did",room:"custom-room",seq:42});
assert.equal(listener({op:"profile"}, good, reply), true);
port.closed();
assert.equal(replies.at(-1).code, "disconnected");
assert.equal(nativeCalls, 2);
console.log("Background boundary checks passed: allowed site/frame, strict fields, one pending request, public response only, no retry.");
