// ota_task.js
(() => {
  // 刷新任务列表：生成每个设备一行，右侧包含软件版本选择和操作按钮
  function refreshTask() {
    const devicesUrl = window.AppConfig.getAPIEndpoint('/api/devices');
    const softwareUrl = window.AppConfig.getAPIEndpoint('/api/software');
    Promise.all([
      fetch(devicesUrl).then(res => res.json()),
      fetch(softwareUrl).then(res => res.json())
    ])
      .then(([devices, software]) => {
        const tbody = document.getElementById("tasks-tbody");
        tbody.innerHTML = "";

        devices.forEach(dev => {
          const row = document.createElement("tr");

          // 构建软件版本下拉菜单
          let versionOptions = "";
          software.forEach(s => {
            versionOptions += `<option value="${s.version}">${s.version}</option>`;
          });

          row.innerHTML = `
            <td>${dev.device_name}</td>
            <td>${dev.client_id}</td>
            <td>
              <select id="ver-${dev.client_id}">
                ${versionOptions}
              </select>
            </td>
            <td>
              <button onclick="App.pushOTA('${dev.client_id}', '${dev.device_name}')">OTA推送</button>
            </td>
            <td>
              <a href="#" onclick="App.showTaskHistory('${dev.client_id}')">OTA_Record</a>
            </td>
          `;

          tbody.appendChild(row);
        });
      })
      .catch(err => console.error("刷新任务列表失败:", err));
  }

  // 推送 OTA 任务
  async function pushOTA(clientId, deviceName) {
    const version = document.getElementById(`ver-${clientId}`).value;

    const payload = {
      msg_type:"task_info",
      action:"pushtask",
      client_id:clientId,
      device_name:deviceName,
      version:version
    };

    try {
    const resp = await RequestBus.send(
      "task_info",
      payload,
      { timeoutMs: 20000 }
    );

    alert("OTA任务下发成功");
    console.log("[OTA] push success:", resp);

  } catch (err) {
    alert("OTA任务下发失败: " + err.message);
    console.error("[OTA] push failed:", err);
  }
  
  }

  // 查询任务统计结果 (summary)
  async function showTaskStats() {
    const clientId = document.getElementById("clientSelect").value;
    const requestId = RequestBus.genRequestId();

    const payload = {
      msg_type: "task_info",
      action:"queryTaskSummary",
      client_id: clientId,
      request_id: requestId
    };

    try {
      await RequestBus.send("task_summary", payload, { requestId });
      console.log("[OTA] 请求任务统计:", payload);
    } catch (err) {
      console.error("[OTA] 请求任务统计失败:", err);
    }
  }

  // 查询任务历史记录 (taskHistory)
  async function showTaskHistory(clientId) {
    const requestId = RequestBus.genRequestId();

    const payload = {
      msg_type: "task_info",
      action: "queryTasklist",
      client_id: clientId,
      request_id: requestId
    };

    try {
      await RequestBus.send("task_history", payload, { requestId });
      console.log("[OTA] 请求任务历史:", payload);
    } catch (err) {
      console.error("[OTA] 请求任务历史失败:", err);
    }
  }

  // 全局暴露接口
  window.OTAManager = {
    refreshTask,
    pushOTA,
    showTaskStats,
    showTaskHistory
  };
})();
