/**
 * OTA Management Backend Server
 * Node.js Express + Socket.IO
 * 
 * Replaces Python Flask backend with full feature parity
 */

const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

// Import modules
const Database = require('./lib/database');
const TCPGateway = require('./lib/tcp-gateway');
const messageBus = require('./lib/message-bus');
const setupSocketHandlers = require('./lib/socket-handlers');
const createRoutes = require('./routes/index');

// Configuration
const PORT = process.env.PORT || 8000;
const HOST = process.env.HOST || '127.0.0.1';
const GW_IP = process.env.GW_IP || '192.168.4.1';
const GW_TCP_PORT = process.env.GW_TCP_PORT || 9001;

// Paths - Allow override via environment or use defaults
let dbDir = process.env.DB_PATH;
let firmwareDir = process.env.FIRMWARE_PATH;

if (!dbDir || !firmwareDir) {
  // Default development paths
  const baseDir = path.join(__dirname, '..');
  dbDir = dbDir || path.join(baseDir, 'backend', 'db');
  firmwareDir = firmwareDir || path.join(baseDir, 'backend', 'firmware');
}

const frontDir = path.join(__dirname, '..', 'front');

// Ensure directories exist
[dbDir, firmwareDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Initialize database
const db = new Database(dbDir);

// Initialize Express app
const app = express();
const server = http.createServer(app);

// Initialize Socket.IO
const io = socketIO(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  },
  transports: ['websocket', 'polling']
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Static files
app.use(express.static(frontDir));

// API Routes
app.use(createRoutes(db, messageBus, firmwareDir));

// Frontend routes
app.get('/', (req, res) => {
  res.sendFile(path.join(frontDir, 'index.html'));
});

app.get('/index.html', (req, res) => {
  res.sendFile(path.join(frontDir, 'index.html'));
});

// Socket.IO handlers
setupSocketHandlers(io, db, messageBus);

// TCP Gateway
const tcpGateway = new TCPGateway(GW_IP, GW_TCP_PORT);

tcpGateway.on('connected', () => {
  console.log('[Server] TCP Gateway connected, broadcasting to clients');
  io.emit('gateway.connected', { status: 'connected' });
});

tcpGateway.on('data', (data) => {
  console.log('[Server] Data from gateway:', data.length, 'bytes');
  // Forward to frontend via WebSocket
  io.emit('gateway.data', { data: data.toString('base64') });
});

tcpGateway.on('closed', () => {
  console.log('[Server] TCP Gateway disconnected');
  io.emit('gateway.disconnected', { status: 'disconnected' });
});

// Error handling
app.use((err, req, res, next) => {
  console.error('[Server] Error:', err);
  res.status(500).json({ error: err.message });
});

// Start server
server.listen(PORT, HOST, async () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║     OTA Management Backend Server - Node.js                ║
║                                                            ║
║  Server: http://${HOST}:${PORT}                          ║
║  WebSocket: ws://${HOST}:${PORT}                          ║
║  Database: ${dbDir}                  ║
║  Firmware: ${firmwareDir}                       ║
║  Gateway: ${GW_IP}:${GW_TCP_PORT}                              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
  `);

  // Connect to TCP Gateway
  try {
    await tcpGateway.connect();
    console.log('[Server] TCP Gateway connection initiated');
  } catch (err) {
    console.error('[Server] TCP Gateway connection failed:', err.message);
  }

  // Subscribe to key events
  messageBus.subscribe('device.update', (data) => {
    console.log('[Server] Device update event:', data);
  });

  messageBus.subscribe('software.update', (data) => {
    console.log('[Server] Software update event:', data);
  });

  messageBus.subscribe('task.created', (task) => {
    console.log('[Server] Task created:', task.task_id);
  });
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n[Server] Shutting down gracefully...');
  tcpGateway.disconnect();
  server.close(() => {
    console.log('[Server] Server closed');
    process.exit(0);
  });
});

process.on('unhandledRejection', (err) => {
  console.error('[Server] Unhandled rejection:', err);
});

module.exports = { app, server, io, db, tcpGateway };
