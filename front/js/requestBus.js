// websocket task pool
const pending = new Map();

export function sendRequest(action, payload, timeout = 5000) {
  const requestId = crypto.randomUUID();

  socket.emit("query", {
    action,
    request_id: requestId,
    ...payload
  });

  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      pending.delete(requestId);
      reject(new Error("Request timeout"));
    }, timeout);

    pending.set(requestId, { resolve, reject, timer });
  });
}




export function resolveRequest(requestId, data) {
  const entry = pending.get(requestId);
  if (!entry) return false;

  clearTimeout(entry.timer);
  entry.resolve(data);
  pending.delete(requestId);
  return true;
}
