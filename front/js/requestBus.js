// requestBus.js
(() => {
  const requests = new Map();
  const DEFAULT_TIMEOUT_MS = 15000;

  function genRequestId() {
    return "req_" + Math.random().toString(36).slice(2) + Date.now();
  }

  function send(msgType, payload, opts = {}) {
    const requestId = opts.requestId || genRequestId();
    const timeoutMs = opts.timeoutMs || DEFAULT_TIMEOUT_MS;

    const msg = {
      msg_type: msgType,
      request_id: requestId,
      ...payload
    };

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        requests.delete(requestId);
        reject(new Error(`Request timeout: ${msgType} (${requestId})`));
      }, timeoutMs);

      requests.set(requestId, { resolve, reject, timer });

      SocketChannel.emit("client.request", msg);
    });
  }

  // 处理服务端响应
  SocketChannel.on("server.response", (resp) => {
    const { request_id, status } = resp || {};
    const entry = requests.get(request_id);
    if (!entry) return;

    clearTimeout(entry.timer);
    requests.delete(request_id);

    if (status === "ok") {
      entry.resolve(resp);
    } else {
      entry.reject(new Error(resp?.error || "unknown error"));
    }
  });

  window.RequestBus = { send, genRequestId };
})();
