// requestBus.js
(() => {
  const requests = new Map();
  const DEFAULT_TIMEOUT_MS = 15000;

  function genRequestId() {
    return "req_" + Math.random().toString(36).slice(2) + Date.now();
  }

  function send(type, payload, opts = {}) {
    const requestId = opts.requestId || genRequestId();
    const timeoutMs = opts.timeoutMs || DEFAULT_TIMEOUT_MS;

    const msg = {
      msg_type: type,
      request_id: requestId,
      ...payload
    };

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        requests.delete(requestId);
        reject(new Error(`Request timeout: ${type} (${requestId})`));
      }, timeoutMs);

      requests.set(requestId, { resolve, reject, timer });

      // 通过 Socket.IO 发给后端
      SocketChannel.emit("client.request", msg);
    });
  }

  // 处理服务端针对请求的响应
  SocketChannel.on("server.response", (resp) => {
    const { request_id, status } = resp || {};
    const entry = requests.get(request_id);
    if (!entry) return;
    clearTimeout(entry.timer);
    requests.delete(request_id);
    status === "ok" ? entry.resolve(resp) : entry.reject(new Error(resp?.error || "unknown error"));
  });

  // 暴露到全局
  window.RequestBus = { send, genRequestId };
})();
