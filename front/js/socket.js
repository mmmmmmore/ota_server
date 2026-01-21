// socket.js
(() => {
  let socket = null;
  const emitQueue = [];

  function flushQueue() {
    if (!socket) return;
    while (emitQueue.length) {
      const { event, data } = emitQueue.shift();
      socket.emit(event, data);
    }
  }

  async function initSocket() {
    try {
      if (window.AppConfig && typeof window.AppConfig.ready === 'function') {
        await window.AppConfig.ready();
      }

      const ENDPOINT = window.AppConfig ? window.AppConfig.wsURL : "ws://127.0.0.1:8000";

      socket = io(ENDPOINT, {
        transports: ["websocket"],
        reconnection: true,
        reconnectionAttempts: 10,
        reconnectionDelay: 1000,
        timeout: 20000,
        secure: true,
        rejectUnauthorized: false
      });

      socket.on("connect", () => {
        console.log("[WS] connected:", socket.id);
        flushQueue();
        setInterval(() => {
          if (socket.connected) {
            socket.emit("heartbeat", { ts: Date.now() });
          }
        }, 30000);
      });

      socket.on("disconnect", (reason) => {
        console.log("[WS] disconnected:", reason);
      });

      socket.on("connect_error", (err) => {
        console.warn("[WS] connect_error:", err.message);
      });

      socket.on("heartbeat_ack", (data) => {
        console.log("[WS] Rx HB ack from Server success", data);
      });

      window.SocketChannel.socket = socket;
    } catch (error) {
      console.error('[WS] Failed to initialize socket:', error);
    }
  }

  // 暴露全局接口
  window.SocketChannel = {
    socket,
    ready: () => socket ? Promise.resolve(socket) : initSocket(),
    emit(event, data) {
      if (!socket) {
        emitQueue.push({ event, data });
        initSocket();
        return;
      }
      socket.emit(event, data);
    },
    on(event, handler) {
      if (!socket) {
        initSocket().then(() => socket.on(event, handler));
        return;
      }
      socket.on(event, handler);
    },
    off(event, handler) {
      if (!socket) return;
      socket.off(event, handler);
    }
  };

  // Initialize immediately
  initSocket();
})();
