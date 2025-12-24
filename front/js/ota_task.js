// ota_task.js
(() => {
  // 刷新任务列表：生成每个设备一行，右侧包含软件版本选择和操作按钮
  function refreshTask() {
    Promise.all([
      fetch("https://localhost:8080/api/devices").then(res => res.json()),
      fetch("https://localhost:8080/api/software").then(res => res.json())
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
  function pushOTA(clientId, deviceName) {
    const version = document.getElementById(`ver-${clientId}`).value;

    fetch("https://localhost:8080/api/dispatch/push", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client_id: clientId, device_name: deviceName, version: version })
    })
      .then(res => {
        if (!res.ok) {
          return res.json().then(err => { throw new Error(err.error || "请求失败"); });
        }
        return res.json();
      })
      .then(data => {
        alert("任务下发成功: " + data.message);
      })
      .catch(err => {
        alert("任务下发失败: " + err.message);
      });
  }

  // 查询任务统计结果 (summary)
  async function showTaskStats() {
    const clientId = document.getElementById("clientSelect").value;
    const requestId = RequestBus.genRequestId();

    const payload = {
      msg_type: "task_summary",
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
      msg_type: "task_history",
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
