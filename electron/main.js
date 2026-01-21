const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Get user data directory (editable by users)
const userDataPath = app.getPath('userData');
const dbDir = path.join(userDataPath, 'data');
const logsDir = path.join(userDataPath, 'logs');

// Ensure directories exist
[dbDir, logsDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

console.log(`[Electron] User Data Path: ${userDataPath}`);
console.log(`[Electron] Database Path: ${dbDir}`);

let mainWindow;
let pythonProcess;
const BACKEND_PORT = 8000;
const BACKEND_HOST = '127.0.0.1';

// Work around noisy EGL driver warnings by disabling GPU acceleration on Electron
app.disableHardwareAcceleration();

// Check if backend is already running
function checkBackendRunning() {
  return new Promise((resolve) => {
    const net = require('net');
    const client = net.createConnection({ port: BACKEND_PORT, host: BACKEND_HOST }, () => {
      client.end();
      resolve(true);
    });
    client.on('error', () => {
      resolve(false);
    });
  });
}

// Start Node.js backend
async function startBackend() {
  const isRunning = await checkBackendRunning();
  
  if (isRunning) {
    console.log(`Backend already running on port ${BACKEND_PORT}`);
    return;
  }

  console.log('Starting Node.js backend...');
  
  const backendPath = path.join(__dirname, '..', 'backend_nodejs', 'server.js');
  
  // Pass database path to backend via environment
  const env = {
    ...process.env,
    DB_PATH: path.join(dbDir, 'backend', 'db'),
    FIRMWARE_PATH: path.join(dbDir, '..', 'firmware'),
    NODE_ENV: 'production',
    PORT: BACKEND_PORT.toString(),
    HOST: BACKEND_HOST
  };

  // Start Node.js process
  pythonProcess = spawn('node', [backendPath], {
    cwd: path.join(__dirname, '..'),
    stdio: 'pipe',
    env: env
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Node.js Backend]: ${data.toString()}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Node.js Backend Error]: ${data.toString()}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Node.js backend process exited with code ${code}`);
  });

  // Wait for backend to start
  await new Promise(resolve => setTimeout(resolve, 2000));
}

// Create main application window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
      allowRunningInsecureContent: false
    },
    icon: path.join(__dirname, '..', 'front', 'assets', 'icon.png'),
    titleBarStyle: 'default',
    backgroundColor: '#2c3e50'
  });

  // Create application menu
  const menuTemplate = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Open Data Folder',
          accelerator: 'CmdOrCtrl+Shift+D',
          click: () => {
            const { shell } = require('electron');
            shell.openPath(dbDir);
          }
        },
        { type: 'separator' },
        {
          label: 'Refresh',
          accelerator: 'CmdOrCtrl+R',
          click: () => mainWindow.reload()
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Toggle DevTools',
          accelerator: 'CmdOrCtrl+Alt+I',
          click: () => mainWindow.webContents.toggleDevTools()
        },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About OTA Management',
              message: 'OTA Management Desktop Application',
              detail: `Version 1.0.0\nFirmware update management for ESP32 devices\n\nData Folder: ${dbDir}`
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  // Load the frontend
  const frontPath = path.join(__dirname, '..', 'front', 'index.html');
  mainWindow.loadFile(frontPath);

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle page errors
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Failed to load page:', errorCode, errorDescription);
  });

  // Console messages from renderer
  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`[Renderer Console]: ${message}`);
  });
}

// App lifecycle
app.whenReady().then(async () => {
  await startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Kill Python backend when app quits
  if (pythonProcess) {
    console.log('Stopping Python backend...');
    pythonProcess.kill('SIGTERM');
    pythonProcess = null;
  }
});

// IPC handlers
ipcMain.handle('get-backend-url', () => {
  return `http://${BACKEND_HOST}:${BACKEND_PORT}`;
});

ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Firmware', extensions: ['bin', 'hex', 'elf'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  dialog.showErrorBox('Application Error', error.message);
});

console.log('Electron app started');
