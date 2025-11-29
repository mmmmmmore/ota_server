// 统计数据
const stats = {
  "Vehicle_1": { success: 0, total: 0 },
  "Vehicle_2": { success: 0, total: 0 },
  "Vehicle_3": { success: 0, total: 0 }
};

// 分区状态：true=A运行；false=B运行
const partitions = {
  "Vehicle_1": true,
  "Vehicle_2": true,
  "Vehicle_3": true
};

// 菜单切换
function showSection(sectionId) {
  document.querySelectorAll('.section').forEach(sec => sec.classList.add('hidden'));
  document.getElementById(sectionId).classList.remove('hidden');
}

// 分区显示
function partitionHTML(isAActive) {
  return isAActive
    ? '<div class="partition-box active">A</div><div class="partition-box inactive">B</div>'
    : '<div class="partition-box inactive">A</div><div class="partition-box active">B</div>';
}

function uploadFirmware() {
  const fileInput = document.getElementById("firmwareFile");
  const versionInput = document.getElementById("firmwareVersion");
  const md5Input = document.getElementById("firmwareMD5");
  const changeInput = document.getElementById("changenote");

  if (!fileInput.files.length) {
    alert("请先选择固件文件");
    return;
  }
  const file = fileInput.files[0];
  const version = versionInput.value || "unknown";
  const md5 = md5Input.value || "";
  const changes =changeInput.value || "";

  const formData = new FormData();
  formData.append("file", file);
  formData.append("version", version);
  formData.append("md5",md5);
  formData.append("changes",changes)

    fetch("http://localhost:8080/api/software/upload", { method: "POST", body: formData })
    .then(res =>res.json() )  
    .then(data => {
      alert("Upload Success: "+JSON.stringify(data));
      querySoftware();  //fresh the sw list
      })
    .catch(err => console.error("请求失败:", err));
  
}


function renderPartition(deviceName) {
  const html = partitionHTML(partitions[deviceName]);
  const cells = document.querySelectorAll(`#partition-${deviceName}`);
  cells.forEach(cell => { cell.innerHTML = html; });
}

function setStatus(deviceName, text, color) {
  const cell = document.getElementById(`status-${deviceName}`);
  if (!cell) return;
  cell.textContent = text;
  cell.style.color = color;
}

// 图表对象
let updateChart = null;

// 更新统计并刷新图表
function updateStats(deviceName, success) {
  stats[deviceName].total++;
  if (success) stats[deviceName].success++;

  if (!updateChart) return;

  const successData = Object.values(stats).map(s => s.success);
  const failData = Object.values(stats).map(s => s.total - s.success);
  const ratioData = Object.values(stats).map(s =>
    s.total > 0 ? Math.round((s.success / s.total) * 100) : 0
  );

  updateChart.data.datasets[0].data = successData;
  updateChart.data.datasets[1].data = failData;
  updateChart.data.datasets[2].data = ratioData;
  updateChart.update();
}

// ---------------- API 对接 ---------------- //

// 查询设备信息
function queryDevices() {
  fetch("http://localhost:8080/api/devices")
    .then(response => response.json())
    .then(devices => {
      const tbody = document.getElementById("devices-tbody");
      tbody.innerHTML = ""; // 清空旧内容

      devices.forEach(dev => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${dev.device_name || ""}</td>
          <td>${dev.client_id || ""}</td>
          <td>${dev.mac_address || ""}</td>
          <td>${dev.ip || ""}</td>
          <td>${dev.firmware_version || ""}</td>
          <td>${dev.partition || ""}</td>
          <td>${dev.status || ""}</td>
          <td>
            <button onclick="editDevice('${dev.mac_address}')">Edit</button>
            <button onclick="deleteDevice('${dev.mac_address}')">Delete</button>
        `;

        tbody.appendChild(row);
      });
    })
    .catch(error => console.error("查询设备失败:", error));
}


//update device info
function editDevice(mac) {
  const newName = prompt("请输入新的设备名称:");
  const clientId = prompt("请输入设备Client ID (可选):");

  const payload = {
    device_name: newName,
    client_id: clientId,
  };

  fetch(`http://localhost:8080/api/devices/${mac}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    alert("设备修改成功: " + JSON.stringify(data));
    queryDevices();
  })
  .catch(err => console.error("修改失败:", err));
}

//delete device function
function deleteDevice(mac) {
  if (!confirm(`确定要删除设备 ${mac} 吗？`)) return;

  fetch(`http://localhost:8080/api/devices/${mac}`, {
    method: "DELETE"
  })
  .then(res => res.json())
  .then(data => {
    alert("设备删除成功: " + JSON.stringify(data));
    queryDevices();
  })
  .catch(err => console.error("删除失败:", err));
}


//add create new device function
function newDevices() {
  // 简单示例：弹出输入框收集信息
  const deviceName = prompt("请输入设备名称:");
  const macAddress = prompt("请输入设备MAC地址:");
  const clientId = prompt("请输入设备Client ID (可选):");
  const firmwareVersion = prompt("请输入初始固件版本 (可选):");

  if (!deviceName || !macAddress) {
    alert("设备名称和MAC地址是必填项！");
    return;
  }

  // 构造请求体
  const newDevice = {
    device_name: deviceName,
    mac_address: macAddress,
    client_id: clientId,
    firmware_version: firmwareVersion
  };

  // 调用后端接口
  fetch('http://localhost:8080/api/devices/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(newDevice)
  })
  .then(response => response.json())
  .then(data => {
    alert("设备创建成功: " + JSON.stringify(data));
    // TODO: 刷新设备列表
    queryDevices();
  })
  .catch(error => {
    console.error("创建设备失败:", error);
    alert("创建设备失败，请检查日志");
  });
}


// 查询软件版本
function querySoftware() {
  fetch("http://localhost:8080/api/software")
    .then(res => res.json())
    .then(list => {
      const tbody = document.getElementById("software-tbody");
      tbody.innerHTML = "";

      list.forEach(s => {
        const row = document.createElement("tr");
        tbody.innerHTML += `<tr>
          <td>${s.version}</td>
          <td>${s.date}</td>
          <td>${s.changes}</td>
          <td>${s.md5}</td>
          <td>
            <button onclick="editSoftware('${s.version}')">Edit</button>
            <button onclick="deleteSoftware('${s.version}')">Delete</button>
          <td>
        </tr>
        `;
        tbody.appendChild(row);
      });
    })
    .catch(err => alert("软件查询失败: " + err));
}


function editSoftware(version) {
  const newChanges = prompt("请输入新的变化点说明:");
  const newMd5 = prompt("请输入新的MD5值:");

  fetch(`http://localhost:8080/api/software/${version}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ changes: newChanges, md5: newMd5 })
  })
  .then(res => res.json())
  .then(data => {
    alert("修改成功: " + JSON.stringify(data));
    querySoftware();
  });
}



function deleteSoftware(version) {
  if (!confirm(`确定要删除版本 ${version} 吗？`)) return;

  fetch(`http://localhost:8080/api/software/${version}`, { method: "DELETE" })
    .then(res => res.json())
    .then(data => {
      alert("删除成功: " + JSON.stringify(data));
      querySoftware();
    });
}







// 单设备更新
function updateDevice(deviceName) {
  const version = document.getElementById(`ver-${deviceName}`).value;
  setStatus(deviceName, "更新中...", "black");

  fetch("http://localhost:8080/api/dispatch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target: [deviceName],
      version: version,
      url: "/firmware/firmware.bin"
    })
  })
    .then(res => res.json())
    .then(resp => {
      setStatus(deviceName, "任务已下发", "blue");
      // 查询任务结果
      pollTaskStatus(resp.task_id, deviceName);
    })
    .catch(err => setStatus(deviceName, "下发失败", "red"));
}

// 更新全部设备
function updateAll() {
  const version = document.getElementById("ver-All").value;
  const statusAll = document.getElementById("status-All");
  statusAll.textContent = "更新中...";
  statusAll.style.color = "black";

  fetch("http://localhost:8080/api/dispatch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target: ["Vehicle_1", "Vehicle_2", "Vehicle_3"],
      version: version,
      url: "/firmware/firmware.bin"
    })
  })
    .then(res => res.json())
    .then(resp => {
      statusAll.textContent = "任务已下发";
      statusAll.style.color = "blue";
      pollTaskStatus(resp.task_id, "All");
    })
    .catch(err => {
      statusAll.textContent = "下发失败";
      statusAll.style.color = "red";
    });
}

// 轮询任务状态
function pollTaskStatus(taskId, deviceName) {
  setTimeout(() => {
    fetch(`http://localhost:8080/api/status?task_id=${taskId}`)
      .then(res => res.json())
      .then(results => {
        results.forEach(r => {
          const success = r.result === "success";
          setStatus(r.name, success ? "成功" : "失败", success ? "green" : "red");
          partitions[r.name] = success ? !partitions[r.name] : partitions[r.name];
          renderPartition(r.name);
          updateStats(r.name, success);
        });

        if (deviceName === "All") {
          const allSuccess = results.every(r => r.result === "success");
          const statusAll = document.getElementById("status-All");
          statusAll.textContent = allSuccess ? "全部成功" : "部分失败";
          statusAll.style.color = allSuccess ? "green" : "orange";
        }
      })
      .catch(err => console.error("状态查询失败:", err));
  }, 2000);
}

// ---------------- 初始化 ---------------- //
document.addEventListener("DOMContentLoaded", () => {
  ["Vehicle_1", "Vehicle_2", "Vehicle_3"].forEach(renderPartition);

  const ctx = document.getElementById('updateChart').getContext('2d');
  updateChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ["Vehicle_1", "Vehicle_2", "Vehicle_3"],
      datasets: [
        { label: "成功次数", data: [0, 0, 0], backgroundColor: 'green' },
        { label: "失败次数", data: [0, 0, 0], backgroundColor: 'orange' },
        { label: "成功比例 (%)", data: [0, 0, 0], backgroundColor: 'blue' }
      ]
    },
    options: {
      responsive: false,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
});







