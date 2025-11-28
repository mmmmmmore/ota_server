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

function renderPartition(deviceName) {
  const html = partitionHTML(partitions[deviceName]);
  const cells = document.query
