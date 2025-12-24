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
