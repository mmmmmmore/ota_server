// device.js
(() => {
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
              <button onclick="App.editDevice('${dev.mac_address}')">Edit</button>
              <button onclick="App.deleteDevice('${dev.mac_address}')">Delete</button>
            </td>
          `;
          tbody.appendChild(row);
        });
      })
      .catch(error => console.error("查询设备失败:", error));
  }

  // 新建设备
  function newDevice() {
    const deviceName = prompt("请输入设备名称:");
    const macAddress = prompt("请输入设备MAC地址:");
    const clientId = prompt("请输入设备Client ID (可选):");
    const firmwareVersion = prompt("请输入初始固件版本 (可选):");

    if (!deviceName || !macAddress) {
      alert("设备名称和MAC地址是必填项！");
      return;
    }

    const newDevice = {
      device_name: deviceName,
      mac_address: macAddress,
      client_id: clientId,
      firmware_version: firmwareVersion,
    };

    fetch("https://localhost:8080/api/devices/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newDevice)
    })
      .then(res => res.json())
      .then(data => {
        alert("设备创建成功: " + JSON.stringify(data));
        queryDevices();
      })
      .catch(err => {
        console.error("创建设备失败:", err);
        alert("创建设备失败，请检查日志");
      });
  }

  // 修改设备
  function editDevice(mac) {
    const newName = prompt("请输入新的设备名称:");
    const clientId = prompt("请输入设备Client ID (可选):");
    const newPartition = prompt("请输入新的分区 (A/B):");

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

  // 删除设备
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

  // 更新设备状态（供 handler.js 调用）
  function updateDeviceStatus(deviceName, requestId) {
    const cell = document.getElementById(`status-${deviceName}`);
    if (cell) {
      cell.textContent = `更新完成 (req ${requestId})`;
      cell.style.color = "green";
    }
  }

  // 辅助函数：渲染分区显示
  function renderPartition(partition) {
    if (partition === "A") {
      return `<div class="partition"><div class="box active">A</div><div class="box inactive">B</div></div>`;
    } else if (partition === "B") {
      return `<div class="partition"><div class="box inactive">A</div><div class="box active">B</div></div>`;
    } else {
      return `<div class="partition"><div class="box inactive">A</div><div class="box inactive">B</div></div>`;
    }
  }

  // 全局暴露接口
  window.DeviceManager = {
    queryDevices,
    newDevice,
    editDevice,
    deleteDevice,
    updateDeviceStatus
  };
})();
