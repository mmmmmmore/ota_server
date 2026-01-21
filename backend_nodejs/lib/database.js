/**
 * Database Module - JSON file-based storage
 * Manages devices, software, and tasks
 */

const fs = require('fs');
const path = require('path');

class Database {
  constructor(basePath) {
    this.basePath = basePath;
    this.devicesFile = path.join(basePath, 'devices.json');
    this.softwareFile = path.join(basePath, 'software_list.json');
    this.taskDir = path.join(basePath, 'tasks');

    this.ensureDirectories();
  }

  ensureDirectories() {
    // Ensure base directory exists
    if (!fs.existsSync(this.basePath)) {
      fs.mkdirSync(this.basePath, { recursive: true });
      console.log(`[DB] Created directory: ${this.basePath}`);
    }

    // Ensure task directory exists
    if (!fs.existsSync(this.taskDir)) {
      fs.mkdirSync(this.taskDir, { recursive: true });
      console.log(`[DB] Created directory: ${this.taskDir}`);
    }

    // Initialize empty JSON files if they don't exist
    if (!fs.existsSync(this.devicesFile)) {
      fs.writeFileSync(this.devicesFile, JSON.stringify([], null, 2));
      console.log(`[DB] Created file: ${this.devicesFile}`);
    }

    if (!fs.existsSync(this.softwareFile)) {
      fs.writeFileSync(this.softwareFile, JSON.stringify([], null, 2));
      console.log(`[DB] Created file: ${this.softwareFile}`);
    }
  }

  // Device operations
  getDevices() {
    try {
      const data = fs.readFileSync(this.devicesFile, 'utf-8');
      return JSON.parse(data);
    } catch (err) {
      console.error('[DB] Error reading devices:', err.message);
      return [];
    }
  }

  saveDevices(devices) {
    try {
      fs.writeFileSync(this.devicesFile, JSON.stringify(devices, null, 2));
      return true;
    } catch (err) {
      console.error('[DB] Error saving devices:', err.message);
      return false;
    }
  }

  addDevice(device) {
    const devices = this.getDevices();
    device.created_at = new Date().toISOString();
    devices.push(device);
    this.saveDevices(devices);
    return device;
  }

  updateDevice(mac, updates) {
    const devices = this.getDevices();
    const idx = devices.findIndex(d => d.mac_address === mac);
    if (idx === -1) return null;
    devices[idx] = { ...devices[idx], ...updates, updated_at: new Date().toISOString() };
    this.saveDevices(devices);
    return devices[idx];
  }

  deleteDevice(mac) {
    const devices = this.getDevices();
    const filtered = devices.filter(d => d.mac_address !== mac);
    this.saveDevices(filtered);
  }

  // Software operations
  getSoftware() {
    try {
      const data = fs.readFileSync(this.softwareFile, 'utf-8');
      return JSON.parse(data);
    } catch (err) {
      console.error('[DB] Error reading software:', err.message);
      return [];
    }
  }

  saveSoftware(software) {
    try {
      fs.writeFileSync(this.softwareFile, JSON.stringify(software, null, 2));
      return true;
    } catch (err) {
      console.error('[DB] Error saving software:', err.message);
      return false;
    }
  }

  addSoftware(entry) {
    const software = this.getSoftware();
    entry.created_at = new Date().toISOString();
    software.push(entry);
    this.saveSoftware(software);
    return entry;
  }

  updateSoftware(version, updates) {
    const software = this.getSoftware();
    const idx = software.findIndex(s => s.version === version);
    if (idx === -1) return null;
    software[idx] = { ...software[idx], ...updates, updated_at: new Date().toISOString() };
    this.saveSoftware(software);
    return software[idx];
  }

  deleteSoftware(version) {
    const software = this.getSoftware();
    const filtered = software.filter(s => s.version !== version);
    this.saveSoftware(filtered);
  }

  // Task operations
  saveTask(taskId, taskData) {
    const taskFile = path.join(this.taskDir, `${taskId}.json`);
    try {
      fs.writeFileSync(taskFile, JSON.stringify(taskData, null, 2));
      return true;
    } catch (err) {
      console.error('[DB] Error saving task:', err.message);
      return false;
    }
  }

  getTask(taskId) {
    const taskFile = path.join(this.taskDir, `${taskId}.json`);
    try {
      if (!fs.existsSync(taskFile)) return null;
      const data = fs.readFileSync(taskFile, 'utf-8');
      return JSON.parse(data);
    } catch (err) {
      console.error('[DB] Error reading task:', err.message);
      return null;
    }
  }

  getAllTasks() {
    try {
      if (!fs.existsSync(this.taskDir)) return [];
      const files = fs.readdirSync(this.taskDir).filter(f => f.endsWith('.json'));
      const tasks = [];
      files.forEach(file => {
        const taskId = file.replace('.json', '');
        const task = this.getTask(taskId);
        if (task) tasks.push(task);
      });
      return tasks;
    } catch (err) {
      console.error('[DB] Error reading tasks:', err.message);
      return [];
    }
  }

  deleteTask(taskId) {
    const taskFile = path.join(this.taskDir, `${taskId}.json`);
    try {
      if (fs.existsSync(taskFile)) {
        fs.unlinkSync(taskFile);
      }
    } catch (err) {
      console.error('[DB] Error deleting task:', err.message);
    }
  }
}

module.exports = Database;
