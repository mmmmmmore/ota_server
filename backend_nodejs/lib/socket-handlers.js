/**
 * Socket.IO Handlers - Real-time communication with frontend
 */

const { v4: uuidv4 } = require('uuid');

function setupSocketHandlers(io, db, bus) {
  // Lazy-load task manager to avoid startup issues
  let taskManager = null;
  function getTaskManager() {
    if (!taskManager) {
      try {
        const TaskManager = require('./task-manager');
        taskManager = new TaskManager(db);
      } catch (err) {
        console.error('[Socket.IO] Failed to load TaskManager:', err.message);
        throw err;
      }
    }
    return taskManager;
  }
  
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
    socket.on('client.request', async (msg) => {
      console.log(`[Socket.IO] client.request from ${socket.id}:`, msg.msg_type, msg.action);
      
      try {
        // Handle task_info messages
        if (msg.msg_type === 'task_info') {
          if (msg.action === 'queryTaskSummary') {
            try {
              // Generate task summary chart
              const clientId = msg.client_id || 'ALL';
              console.log(`[Socket.IO] Generating task summary for client: ${clientId}`);
              
              const tm = getTaskManager();
              console.log('[Socket.IO] TaskManager loaded, generating chart...');
              
              const base64Image = await tm.generateSummaryChart(clientId);
              console.log(`[Socket.IO] Chart generated, size: ${base64Image.length} chars`);
              
              // Send response
              socket.emit('server.response', {
                msg_type: msg.msg_type,
                request_id: msg.request_id,
                status: 'ok'
              });
              
              // Send the chart image via server.parsed
              socket.emit('server.parsed', {
                msg_type: 'ota_task_summary',
                action: 'response_url',
                url: base64Image
              });
              
              console.log('[Socket.IO] Task summary chart sent to client');
              return;
            } catch (error) {
              console.error('[Socket.IO] Error generating task summary:', error);
              socket.emit('server.response', {
                msg_type: msg.msg_type,
                request_id: msg.request_id,
                status: 'error',
                error: error.message
              });
              return;
            }
          }
          
          if (msg.action === 'queryTasklist') {
            // Get task history
            const clientId = msg.client_id;
            console.log(`[Socket.IO] Getting task history for client: ${clientId}`);
            
            const tm = getTaskManager();
            const history = tm.getTaskHistory(clientId);
            
            // Send response
            socket.emit('server.response', {
              msg_type: msg.msg_type,
              request_id: msg.request_id,
              status: 'ok'
            });
            
            // Send the task history
            socket.emit('server.parsed', {
              msg_type: 'ota_history_list',
              action: 'response_history_list',
              subarea: 'task_history',
              payload: JSON.stringify(history)
            });
            
            console.log('[Socket.IO] Task history sent to client');
            return;
          }

          if (msg.action === 'pushtask') {
            // Handle OTA task push
            const { client_id, device_name, version } = msg;
            console.log(`[Socket.IO] Pushing OTA task for ${client_id}:${version}`);

            const taskId = `${new Date().toISOString().replace(/[:-]/g, '').split('.')[0]}_${client_id}`;
            const task = {
              msg_type: 'ota_task',
              task_id: taskId,
              client_id,
              device_name,
              version,
              firmware_url: `https://192.168.4.2:8443/firmware/ota_client_${client_id}_${version}.bin`,
              timestamp: new Date().toISOString(),
              result: '0x01 0x00', // INITIATED, UNKNOWN
              features: ''
            };

            db.saveTask(taskId, task);
            bus.publish('task.created', task);

            socket.emit('server.response', {
              msg_type: msg.msg_type,
              request_id: msg.request_id,
              status: 'ok'
            });
            
            return;
          }
        }
        
        // Default response for other messages
        socket.emit('server.response', {
          ...msg,
          status: 'ok',
          server_time: new Date().toISOString()
        });
      } catch (error) {
        console.error('[Socket.IO] Error handling client.request:', error);
        socket.emit('server.response', {
          msg_type: msg.msg_type,
          request_id: msg.request_id,
          status: 'error',
          error: error.message
        });
      }
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
