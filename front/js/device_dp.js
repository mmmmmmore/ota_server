



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
    firmware_version: firmwareVersion,
  };

  // 调用后端接口
  fetch('https://localhost:8080/api/devices/register', {
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



// 单设备更新
function updateDevice(deviceName) {
  const version = document.getElementById(`ver-${deviceName}`).value;
  setStatus(deviceName, "更新中...", "black");

  fetch("https://localhost:8080/api/dispatch", {
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

  fetch("https://localhost:8080/api/dispatch", {
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




// 查询设备信息
function queryDevices() {
  fetch("https://localhost:8080/api/devices")
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
          <td>${renderPartition(dev.partition)}</td>
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
  const newPartition = prompt("Please input Partition A/B ");

  const payload = {
    device_name: newName,
    client_id: clientId,
    partition: newPartition
  };

  fetch(`https://localhost:8080/api/devices/${mac}`, {
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

  fetch(`https://localhost:8080/api/devices/${mac}`, {
    method: "DELETE"
  })
  .then(res => res.json())
  .then(data => {
    alert("设备删除成功: " + JSON.stringify(data));
    queryDevices();
  })
  .catch(err => console.error("删除失败:", err));
}



function renderDeviceRow(dev){
  return `
    <tr id="task-row-${dev.client_id}">
      <td>${dev.device_name}</td>
      <td>${dev.client_id}</td>
      <td>${dev.mac_address}</td>
      <td>${dev.ip}
  `;
}


function renderPartition(partition) {
  if (partition == "A"){
    return `<div class="parition"><div class="box active">A</div><div class="box inactive">B</div></div>`;
  } else if(partition =="B") {
    return `<div class="partition"><div class="box inactive">A</div><div class="box active">B</div></div>`;
  } else{
    return `<div class="partition"><div class="box inactive">A</div><div class="box active">B</div></div>`; 
  }
}

function renderDevice(dev){
  const row = document.getElementById(`task-row-${dev.client_id}`);
  if (row){
    row.innerHTML = renderDeviceRow(dev); 
  }
}

function onDeviceUpdate(device_name, request_id){
  updateDevice(device_name);
}
