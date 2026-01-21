/**
 * Socket.IO Handlers - Real-time communication with frontend
 */

const { v4: uuidv4 } = require('uuid');

function setupSocketHandlers(io, db, bus) {
  // Store active client connections
  const clients = new Map();

  io.on('connection', (socket) => {
    console.log(`[Socket.IO] Client connected: ${socket.id}`);

    // Register client
    clients.set(socket.id, {
      id: socket.id,
      connected_at: new Date(),
      subscriptions: []
    });

    // ============ HEARTBEAT ============
    socket.on('heartbeat', (data) => {
      socket.emit('heartbeat_ack', {
        ts: Date.now(),
        server_time: new Date().toISOString()
      });
    });

    // ============ DEVICE REQUESTS ============
    socket.on('device.query', (data, callback) => {
      console.log(`[Socket.IO] device.query from ${socket.id}`);
      const devices = db.getDevices();
      if (callback) callback({ status: 'ok', data: devices });
      socket.emit('device.response', devices);
    });

    socket.on('device.update', (data, callback) => {
      const { mac_address, updates } = data;
      console.log(`[Socket.IO] device.update for ${mac_address}`);
      const device = db.updateDevice(mac_address, updates);
      if (callback) callback({ status: 'ok', data: device });
      io.emit('device.updated', device);
    });

    // ============ SOFTWARE REQUESTS ============
    socket.on('software.query', (data, callback) => {
      console.log(`[Socket.IO] software.query from ${socket.id}`);
      const software = db.getSoftware();
      if (callback) callback({ status: 'ok', data: software });
      socket.emit('software.response', software);
    });

    // ============ TASK REQUESTS ============
    socket.on('task.query', (data, callback) => {
      console.log(`[Socket.IO] task.query from ${socket.id}`);
      const tasks = db.getAllTasks();
      if (callback) callback({ status: 'ok', data: tasks });
      socket.emit('task.response', tasks);
    });

    socket.on('task.push', (data, callback) => {
      const { client_id, device_name, version } = data;
      console.log(`[Socket.IO] task.push for ${client_id}:${version}`);

      const taskId = `${new Date().toISOString().replace(/[:-]/g, '').split('.')[0]}_${client_id}`;
      const task = {
        task_id: taskId,
        client_id,
        device_name,
        version,
        action: 'update',
        status: 'pending',
        created_at: new Date().toISOString()
      };

      db.saveTask(taskId, task);
      bus.publish('task.created', task);

      if (callback) callback({ status: 'ok', task_id: taskId });
      io.emit('task.created', task);
    });

    // ============ GENERIC REQUEST/RESPONSE ============
    socket.on('client.request', (msg) => {
      console.log(`[Socket.IO] client.request from ${socket.id}:`, msg.msg_type);
      
      // Echo the request back as response
      const response = {
        ...msg,
        status: 'ok',
        server_time: new Date().toISOString()
      };

      socket.emit('server.response', response);
    });

    // ============ CLEANUP ============
    socket.on('disconnect', (reason) => {
      console.log(`[Socket.IO] Client disconnected: ${socket.id}, reason: ${reason}`);
      clients.delete(socket.id);
    });

    socket.on('error', (error) => {
      console.error(`[Socket.IO] Error from ${socket.id}:`, error);
    });
  });

  // Subscribe to message bus events and broadcast to clients
  bus.subscribe('device.update', (data) => {
    console.log('[Socket.IO] Broadcasting device.update');
    io.emit('server.notify', {
      msg_type: 'device_update',
      payload: data
    });
  });

  bus.subscribe('software.update', (data) => {
    console.log('[Socket.IO] Broadcasting software.update');
    io.emit('server.notify', {
      msg_type: 'software_update',
      payload: data
    });
  });

  bus.subscribe('task.created', (task) => {
    console.log('[Socket.IO] Broadcasting task.created');
    io.emit('server.notify', {
      msg_type: 'task_created',
      payload: task
    });
  });

  bus.subscribe('task.updated', (task) => {
    console.log('[Socket.IO] Broadcasting task.updated');
    io.emit('server.notify', {
      msg_type: 'task_updated',
      payload: task
    });
  });

  return {
    clients,
    broadcast: (event, data) => io.emit(event, data),
    broadcastToRoom: (room, event, data) => io.to(room).emit(event, data)
  };
}

module.exports = setupSocketHandlers;
