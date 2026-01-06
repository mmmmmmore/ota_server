// software.js
(() => {
  // 查询软件版本
  function querySoftware() {
    fetch("https://localhost:8080/api/software")
      .then(res => res.json())
      .then(list => {
        const tbody = document.getElementById("software-tbody");
        tbody.innerHTML = "";

        list.forEach(s => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${s.version}</td>
            <td>${s.release_date || s.date || ""}</td>
            <td>${s.changes}</td>
            <td>${s.md5}</td>
            <td>
              <button onclick="App.editSoftware('${s.version}')">Edit</button>
              <button onclick="App.deleteSoftware('${s.version}')">Delete</button>
            </td>
          `;
          tbody.appendChild(row);
        });
      })
      .catch(err => alert("软件查询失败: " + err));
  }

  // 上传固件（新增）
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
    const changes = changeInput.value || "";

    const formData = new FormData();
    formData.append("file", file);
    formData.append("version", version);
    formData.append("md5", md5);
    formData.append("changes", changes);

    fetch("https://localhost:8080/api/software/upload", {
      method: "POST",
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        alert("上传成功: " + JSON.stringify(data));
        querySoftware(); // 刷新软件列表
      })
      .catch(err => console.error("上传失败:", err));
  }

  // 修改软件版本信息
  function editSoftware(version) {
    const newChanges = prompt("请输入新的变化点说明:");
    const newMd5 = prompt("请输入新的MD5值:");

    const payload = { changes: newChanges, md5: newMd5 };

    fetch(`https://localhost:8080/api/software/${version}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => {
        alert("修改成功: " + JSON.stringify(data));
        querySoftware();
      })
      .catch(err => console.error("修改失败:", err));
  }

  // 删除软件版本
  function deleteSoftware(version) {
    if (!confirm(`确定要删除版本 ${version} 吗？`)) return;

    fetch(`https://localhost:8080/api/software/${version}`, {
      method: "DELETE"
    })
      .then(res => res.json())
      .then(data => {
        alert("删除成功: " + JSON.stringify(data));
        querySoftware();
      })
      .catch(err => console.error("删除失败:", err));
  }

  // 全局暴露接口
  window.SoftwareManager = {
    querySoftware,
    uploadFirmware,
    editSoftware,
    deleteSoftware
  };
})();
