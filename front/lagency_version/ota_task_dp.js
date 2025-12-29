



function pushOTA(clientId, deviceName) {
  const version = document.getElementById(`ver-${clientId}`).value;

  fetch("https://localhost:8080/api/dispatch/push", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: clientId, device_name: deviceName, version: version })
  })
  .then(res => {
    if (!res.ok) {
      // 如果返回非200状态码，直接抛出错误
      return res.json().then(err => { throw new Error(err.error || "请求失败"); });
    }
    return res.json();
  })
  .then(data => {
    alert("Task_Triggered_Success: "+data.message)
  })
  .catch(err => {
    alert("Task_Triggered_Failed: " + err.message);
  });
}



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
        <td><button onclick="pushOTA('${dev.client_id}', '${dev.device_name}')">OTA推送</button></td>
        <td>
          <a href="#" onclick="showTaskHistory('${dev.client_id}')">OTA_Record</a>
        </td>
      `;

      tbody.appendChild(row);
    });
  })
  .catch(err => console.error("刷新任务列表失败:", err));
}



async function showStats() {
  // get target client id
  const clientId = document.getElementById("clientSelect").value;

  const requestId= genRequestId(); //need refer to requestBus
  const payload = {
    msg_type  : "task_summary",
    client_id : clientId,
    request_id : requestId
  };
  try {
    await ReqeusBus.send("task_summary", payload, {requestId});
    console.log("[APP] Request task summary", payload);
  } catch (err) {
    console.log("[APP] request task summary failed", err);
  }
}





// --------------- update task hsitory list ------------//

async function showTaskHistory(clientId){
  // request interface

  const request_id = genRequestId();
  const payload = {
    msg_type: "task_history",
    client_id: clientId,
    request_id:requestId
  };

  try {
    await requestBus.send("task_history", payload, {requestId});
    console.log("[APP] request update task history list");
  } catch (err) {
    console.log("[APP] request update task history failed", err);
  }

}



function closeTaskHistory(){
  document.getElementById("taskHistoryModal").classList.add("hidden");
}



function onTaskSummary(png, request_id){
  const imgEl = document.getElementById("stateImage")
  if (imgEl){
    imgEl.src = png;
  }
}


function onTaskHistory(client_id, json, request_id){
  //update the table list
  const listContainer = document.getElementById("taskHistoryList");
  listContainer.innerHTML = "";  //clear all info before update

    //create table
  const table = document.createElement("table");
  table.classList.add("history-table");

  const thead = document.createElement("thead");
  thead.innerHTML =`
    <tr>
      <th>TaskID</th>
      <th>Phase</th>
      <th>Result</th>
    </tr>
  `;
  table.appendChild(thead);

  //update table content
  const tbody = document.createElement("tbody");
  data.forEach(task =>{
    const row = document.createElement("tr");
    row.innerHTML=`<td>${task.task_id}</td><td>${task.phase}</td><td>${task.result}</td>`;
    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  listContainer.appendChild(table);
  //display the window
  document.getElementById("taskHistoryModal").classList.remove("hidden");
}
