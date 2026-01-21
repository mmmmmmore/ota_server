/**
 * Routes - API endpoints for devices, software, upload, etc.
 */

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

function createRoutes(db, bus, firmwareDir) {
  const router = express.Router();

  // Configure multer for file uploads
  const storage = multer.diskStorage({
    destination: (req, file, cb) => {
      if (!fs.existsSync(firmwareDir)) {
        fs.mkdirSync(firmwareDir, { recursive: true });
      }
      cb(null, firmwareDir);
    },
    filename: (req, file, cb) => {
      const ext = path.extname(file.originalname);
      const name = path.basename(file.originalname, ext);
      cb(null, `${name}-${Date.now()}${ext}`);
    }
  });

  const upload = multer({ storage });

  // ============ DEVICES ============

  /**
   * GET /api/devices
   * Retrieve all devices
   */
  router.get('/api/devices', (req, res) => {
    const devices = db.getDevices();
    console.log('[API] GET /api/devices - returned', devices.length, 'devices');
    res.json(devices);
  });

  /**
   * POST /api/devices/register
   * Register a new device
   */
  router.post('/api/devices/register', (req, res) => {
    const { device_name, mac_address, client_id, version } = req.body;

    if (!device_name || !mac_address) {
      return res.status(400).json({ error: 'device_name and mac_address are required' });
    }

    // Check if device already exists
    const existing = db.getDevices().find(d => d.mac_address === mac_address);
    if (existing) {
      return res.status(409).json({ error: 'Device already exists' });
    }

    const newDevice = {
      device_name,
      mac_address,
      client_id: client_id || null,
      version: version || null,
      status: 'offline',
      partition: 'A',
      created_at: new Date().toISOString()
    };

    const device = db.addDevice(newDevice);
    console.log('[API] POST /api/devices/register - created device:', device);
    
    // Publish device update event
    bus.publish('device.update', { type: 'device_created', device });

    res.status(201).json(device);
  });

  /**
   * PUT /api/devices/:mac
   * Update device
   */
  router.put('/api/devices/:mac', (req, res) => {
    const mac = req.params.mac;
    const updates = req.body;

    const device = db.updateDevice(mac, updates);
    if (!device) {
      return res.status(404).json({ error: 'Device not found' });
    }

    console.log('[API] PUT /api/devices/:mac - updated device:', device);
    bus.publish('device.update', { type: 'device_updated', device });

    res.json(device);
  });

  /**
   * DELETE /api/devices/:mac
   * Delete device
   */
  router.delete('/api/devices/:mac', (req, res) => {
    const mac = req.params.mac;
    db.deleteDevice(mac);
    console.log('[API] DELETE /api/devices/:mac -', mac);
    res.json({ success: true, mac });
  });

  // ============ SOFTWARE ============

  /**
   * GET /api/software
   * Retrieve all software versions
   */
  router.get('/api/software', (req, res) => {
    const software = db.getSoftware();
    console.log('[API] GET /api/software - returned', software.length, 'versions');
    res.json(software);
  });

  /**
   * POST /api/software/upload
   * Upload new firmware
   */
  router.post('/api/software/upload', upload.single('file'), (req, res) => {
    const { version, md5, changes } = req.body;

    if (!req.file || !version) {
      return res.status(400).json({ error: 'file and version are required' });
    }

    // Check if version already exists
    const existing = db.getSoftware().find(s => s.version === version);
    if (existing) {
      fs.unlinkSync(req.file.path); // Clean up uploaded file
      return res.status(409).json({ error: 'Version already exists' });
    }

    const newSoftware = {
      version,
      release_date: new Date().toISOString().split('T')[0],
      changes: changes || '',
      md5: md5 || '',
      filename: req.file.filename,
      file_size: req.file.size,
      created_at: new Date().toISOString()
    };

    const software = db.addSoftware(newSoftware);
    console.log('[API] POST /api/software/upload - created version:', software);
    bus.publish('software.update', { type: 'software_uploaded', software });

    res.status(201).json(software);
  });

  /**
   * PUT /api/software/:version
   * Update software metadata
   */
  router.put('/api/software/:version', (req, res) => {
    const version = req.params.version;
    const updates = req.body;

    const software = db.updateSoftware(version, updates);
    if (!software) {
      return res.status(404).json({ error: 'Software version not found' });
    }

    console.log('[API] PUT /api/software/:version - updated:', software);
    bus.publish('software.update', { type: 'software_updated', software });

    res.json(software);
  });

  /**
   * DELETE /api/software/:version
   * Delete software version
   */
  router.delete('/api/software/:version', (req, res) => {
    const version = req.params.version;
    db.deleteSoftware(version);
    console.log('[API] DELETE /api/software/:version -', version);
    res.json({ success: true, version });
  });

  /**
   * GET /api/software/:version/download
   * Download firmware file
   */
  router.get('/api/software/:version/download', (req, res) => {
    const version = req.params.version;
    const software = db.getSoftware().find(s => s.version === version);

    if (!software) {
      return res.status(404).json({ error: 'Software version not found' });
    }

    const filePath = path.join(firmwareDir, software.filename);
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    console.log('[API] GET /api/software/:version/download -', version);
    res.download(filePath);
  });

  // ============ TASKS ============

  /**
   * GET /api/tasks
   * Retrieve all tasks
   */
  router.get('/api/tasks', (req, res) => {
    const tasks = db.getAllTasks();
    console.log('[API] GET /api/tasks - returned', tasks.length, 'tasks');
    res.json(tasks);
  });

  /**
   * GET /api/tasks/:taskId
   * Get specific task
   */
  router.get('/api/tasks/:taskId', (req, res) => {
    const task = db.getTask(req.params.taskId);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }
    res.json(task);
  });

  /**
   * POST /api/tasks
   * Create new task
   */
  router.post('/api/tasks', (req, res) => {
    const { client_id, device_name, version, action } = req.body;

    if (!client_id || !version) {
      return res.status(400).json({ error: 'client_id and version are required' });
    }

    const taskId = `${new Date().toISOString().replace(/[:-]/g, '').split('.')[0]}_${client_id}`;
    const task = {
      task_id: taskId,
      client_id,
      device_name: device_name || '',
      version,
      action: action || 'update',
      status: 'pending',
      result: null,
      created_at: new Date().toISOString()
    };

    db.saveTask(taskId, task);
    console.log('[API] POST /api/tasks - created task:', taskId);
    bus.publish('task.created', task);

    res.status(201).json(task);
  });

  /**
   * PUT /api/tasks/:taskId
   * Update task
   */
  router.put('/api/tasks/:taskId', (req, res) => {
    const task = db.getTask(req.params.taskId);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const updated = { ...task, ...req.body, updated_at: new Date().toISOString() };
    db.saveTask(req.params.taskId, updated);
    console.log('[API] PUT /api/tasks/:taskId - updated:', req.params.taskId);
    bus.publish('task.updated', updated);

    res.json(updated);
  });

  /**
   * DELETE /api/tasks/:taskId
   * Delete task
   */
  router.delete('/api/tasks/:taskId', (req, res) => {
    db.deleteTask(req.params.taskId);
    console.log('[API] DELETE /api/tasks/:taskId -', req.params.taskId);
    res.json({ success: true, taskId: req.params.taskId });
  });

  // ============ HEALTH CHECK ============

  /**
   * GET /api/health
   * Health check endpoint
   */
  router.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  return router;
}

module.exports = createRoutes;
