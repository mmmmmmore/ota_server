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
function onTaskSummary(png) {
    console.log('[Front-APP]', png);
    
    // Convert ArrayBuffer to string (the ArrayBuffer contains base64 text, not binary image data)
    const uint8Array = new Uint8Array(png);
    const base64String = new TextDecoder('utf-8').decode(uint8Array);
    
    //console.log('[Front-APP] base64String:', base64String.substring(0, 100)); // Log first 100 chars
    
    const imgEl = document.getElementById("stateImage");
    if (imgEl) {
        imgEl.src = "data:image/png;base64," + base64String;
        imgEl.style.display = "block";
        
        // Add error handler to debug
        imgEl.onerror = function() {
            console.error('Image failed to load');
        };
        imgEl.onload = function() {
            console.log('Image loaded successfully');
        };
    } else {
        console.error('Image element not found');
    }
}

  function onTaskHistory(payload) {
    const listContainer = document.getElementById("taskHistoryList");
    listContainer.innerHTML = "";

    const tasks = JSON.parse(payload)

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
    tasks.forEach(task => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${task.task_id}</td><td>${task.phase}</td><td>${task.result}</td>`;
      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    listContainer.appendChild(table);

    document.getElementById("taskHistoryModal").classList.remove("hidden");
  }

  function onDeviceUpdate() {
    if (window.DeviceManager && typeof DeviceManager.queryDevices === "function") {
      DeviceManager.queryDevices();
    }
  }

  function onSoftwareUpdate(){
    if (window.SoftwareManager && typeof SoftwareManager.queryDevices === "function"){
      SoftwareManager.queryDevices();
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

  // ---------------- 初始化应用 ----------------
  async function initApp() {
    try {
      // Initialize configuration
      await window.AppConfig.init();
      
      // Log environment info
      if (window.electronAPI) {
        console.log('[App] Running in Electron');
        console.log('[App] Platform:', window.electronAPI.platform);
        console.log('[App] Versions:', window.electronAPI.versions);
      } else {
        console.log('[App] Running in browser');
      }
      
      console.log('[App] Backend URL:', window.AppConfig.backendURL);
      console.log('[App] Application initialized successfully');
      
    } catch (error) {
      console.error('[App] Initialization error:', error);
    }
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }
})();
