// socket.js
(() => {
  const ENDPOINT = "https://localhost:8080"; // 开发阶段可改为 http://localhost:8080

  const socket = io(ENDPOINT, {
    transports: ["websocket", "polling"], // 建议允许回退
    reconnection: true,
    reconnectionAttempts: 10,
    reconnectionDelay: 1000,
    timeout: 20000,
    secure: true
  });

  socket.on("connect", () => {
    console.log("[WS] connected:", socket.id);
  });

  socket.on("disconnect", (reason) => {
    console.log("[WS] disconnected:", reason);
  });

  socket.on("connect_error", (err) => {
    console.warn("[WS] connect_error:", err.message);
  });

  // 暴露全局接口
  window.SocketChannel = {
    socket,
    emit(event, data) {
      socket.emit(event, data);
    },
    on(event, handler) {
      socket.on(event, handler);
    },
    off(event, handler) {
      socket.off(event, handler);
    }
  };
})();
