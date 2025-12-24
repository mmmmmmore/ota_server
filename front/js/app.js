// app.js
// update new structure code for app.js , only interface with Html 
(() => {
  // 菜单切换：显示对应的 section
  function showSection(sectionId) {
    document.querySelectorAll(".section").forEach(sec => sec.classList.add("hidden"));
    const el = document.getElementById(sectionId);
    if (el) el.classList.remove("hidden");
  }

  // ---------------- OTA设备接口 ----------------
  function queryDevices() {
    if (window.DeviceManager && typeof DeviceManager.queryDevices === "function") {
      DeviceManager.queryDevices();
    }
  }

  function newDevices() {
    if (window.DeviceManager && typeof DeviceManager.newDevice === "function") {
      DeviceManager.newDevice();
    }
  }

  function editDevice(mac) {
    if (window.DeviceManager && typeof DeviceManager.editDevice === "function") {
      DeviceManager.editDevice(mac);
    }
  }

  function deleteDevice(mac) {
    if (window.DeviceManager && typeof DeviceManager.deleteDevice === "function") {
      DeviceManager.deleteDevice(mac);
    }
  }

  // ---------------- OTA软件接口 ----------------
  function querySoftware() {
    if (window.SoftwareManager && typeof SoftwareManager.querySoftware === "function") {
      SoftwareManager.querySoftware();
    }
  }

  function uploadFirmware() {
    if (window.SoftwareManager && typeof SoftwareManager.uploadFirmware === "function") {
      SoftwareManager.uploadFirmware();
    }
  }

  function editSoftware(version) {
    if (window.SoftwareManager && typeof SoftwareManager.editSoftware === "function") {
      SoftwareManager.editSoftware(version);
    }
  }

  function deleteSoftware(version) {
    if (window.SoftwareManager && typeof SoftwareManager.deleteSoftware === "function") {
      SoftwareManager.deleteSoftware(version);
    }
  }

  // ---------------- OTA任务接口 ----------------
  function refreshTask() {
    if (window.OTAManager && typeof OTAManager.refreshTask === "function") {
      OTAManager.refreshTask();
    }
  }

  function pushOTA(clientId, deviceName) {
    if (window.OTAManager && typeof OTAManager.pushOTA === "function") {
      OTAManager.pushOTA(clientId, deviceName);
    }
  }

  function showStats() {
    if (window.OTAManager && typeof OTAManager.showTaskStats === "function") {
      OTAManager.showTaskStats();
    }
  }

  function showTaskHistory(clientId) {
    if (window.OTAManager && typeof OTAManager.showTaskHistory === "function") {
      OTAManager.showTaskHistory(clientId);
    }
  }

  function closeTaskHistory() {
    const modal = document.getElementById("taskHistoryModal");
    if (modal) modal.classList.add("hidden");
  }

  // ---------------- Handler回调接口 ----------------
  function onTaskSummary(png, request_id) {
    const imgEl = document.getElementById("stateImage");
    if (imgEl) {
      imgEl.src = "data:image/png;base64," + png;
      imgEl.style.display = "block";
    }
  }

  function onTaskHistory(client_id, json, request_id) {
    const listContainer = document.getElementById("taskHistoryList");
    listContainer.innerHTML = "";

    const table = document.createElement("table");
    table.classList.add("history-table");

    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>TaskID</th>
        <th>Phase</th>
        <th>Result</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    json.forEach(task => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${task.task_id}</td><td>${task.phase}</td><td>${task.result}</td>`;
      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    listContainer.appendChild(table);

    document.getElementById("taskHistoryModal").classList.remove("hidden");
  }

  function onDeviceUpdate(device_name, request_id) {
    if (window.DeviceManager && typeof DeviceManager.updateDeviceStatus === "function") {
      DeviceManager.updateDeviceStatus(device_name, request_id);
    }
  }

  // ---------------- 全局暴露 ----------------
  window.App = {
    showSection,
    queryDevices,
    newDevices,
    editDevice,
    deleteDevice,
    querySoftware,
    uploadFirmware,
    editSoftware,
    deleteSoftware,
    refreshTask,
    pushOTA,
    showStats,
    showTaskHistory,
    closeTaskHistory,
    onTaskSummary,
    onTaskHistory,
    onDeviceUpdate
  };
})();
