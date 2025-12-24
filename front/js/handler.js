// websocket recv data and parse handle

import { resolveRequest } from "./requestBus.js";

socket.on("state_summary_result", (data) => {
  if (resolveRequest(data.request_id, data)) return;

  // 否则是“非请求触发”的推送事件
  updateSummaryUI(data);
});

socket.on("ota_progress", (data) => {
  updateProgressUI(data);
});



Handler.register("task_summary", (payload, msg) =>{
  const {png, request_id} =msg;

  console.log("[Handler] Rx summary from server", request_id);

  if (window.App && typeof window.App.onTaskSummary === "function"){
    window.App.onTaskSummary(png, request_id);
  }
});


Handler.register("task_history", (payload, msg) =>{
  const {client_id, request_id, json} = msg;

  console.log("[Handler] Rx history result from server", request_id);

  if (window.App && typeof window.App.onTaskHistory === "function"){
    window.App.onTaskHistory(client_id, json, request_id);
  }
});


Handler.register("device_update", (payload, msg) => {
  const { device_name, request_id} = msg;
  console.log("[Handler] Rx Device udpate notify");
  if (window.App && typeof window.App.onDeviceUpdate === "function"){
    window.App.onDeviceUpdate(device_name, request_id);
  }
});


