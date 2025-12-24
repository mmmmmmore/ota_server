// handler.js
(() => {
  const routes = new Map();

  function register(msgType, fn) {
    routes.set(msgType, fn);
  }

  function handleNotify(msg) {
    const { msg_type } = msg || {};
    const fn = routes.get(msg_type);
    if (!fn) {
      console.warn("[Handler] unhandled msg_type:", msg_type, msg);
      return;
    }
    try {
      fn(msg.payload, msg); // 注意这里传两个参数：payload 和完整消息
    } catch (e) {
      console.error("[Handler] route error:", msg_type, e);
    }
  }

  // 监听服务端推送
  SocketChannel.on("server.notify", handleNotify);

  // 暴露全局接口
  window.Handler = { register };

  // ---------------- 默认注册的事件解析 ----------------
  Handler.register("task_summary", (payload, msg) => {
    const { png, request_id } = msg;
    console.log("[Handler] Rx summary from server", request_id);

    if (window.App && typeof window.App.onTaskSummary === "function") {
      window.App.onTaskSummary(png, request_id);
    }
  });

  Handler.register("task_history", (payload, msg) => {
    const { client_id, request_id, json } = msg;
    console.log("[Handler] Rx history result from server", request_id);

    if (window.App && typeof window.App.onTaskHistory === "function") {
      window.App.onTaskHistory(client_id, json, request_id);
    }
  });

  Handler.register("device_update", (payload, msg) => {
    const { device_name, request_id } = msg;
    console.log("[Handler] Rx Device update notify");

    if (window.App && typeof window.App.onDeviceUpdate === "function") {
      window.App.onDeviceUpdate(device_name, request_id);
    }
  });
})();
