# OTA Management Desktop Application

## 🚀 Quick Start Guide

### Architecture Overview

This desktop application uses:
- **Frontend**: Electron (Node.js + Chromium)
- **Backend**: Python Flask (existing backend, unchanged)
- **Communication**: HTTPS REST API + WebSocket

```
┌─────────────────────────────────────┐
│   Electron Desktop Window           │
│  ┌─────────────────────────────┐   │
│  │   HTML/CSS/JavaScript       │   │
│  │   (Your existing frontend)  │   │
│  └─────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │ HTTPS + WebSocket
┌──────────────▼──────────────────────┐
│   Python Flask Backend              │
│   - REST API endpoints              │
│   - WebSocket (Socket.IO)           │
│   - TCP Gateway for ESP32           │
└─────────────────────────────────────┘
```

## 📋 Prerequisites

1. **Node.js** (v18 or later)
   - Download: https://nodejs.org/
   - Check: `node --version`

2. **Python 3** (v3.8 or later)
   - Download: https://www.python.org/
   - Check: `python3 --version`

3. **Python Dependencies**:
   ```bash
   pip3 install flask flask-cors flask-socketio python-socketio
   ```

## 🔧 Installation

### Step 1: Install Node.js Dependencies

```bash
cd /path/to/ota_server
npm install
```

This will install:
- `electron`: Desktop application framework
- `electron-builder`: Package builder for distribution
- `concurrently`: Run multiple processes
- `wait-on`: Wait for backend to start

### Step 2: Verify Python Backend

Make sure your Python backend dependencies are installed:

```bash
pip3 install flask flask-cors flask-socketio python-socketio
```

## 🏃 Running the Application

### Option 1: Quick Start (Recommended)

Use the provided startup script:

```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

**Terminal 1 - Start Backend:**
```bash
python3 backend/app.py
```

**Terminal 2 - Start Electron:**
```bash
npm start
```

### Option 3: Development Mode (Both processes)

```bash
npm run dev
```

This starts both backend and frontend together.

## 📦 Building Distributable App

### Build for macOS:
```bash
npm run build-mac
```
Output: `dist/OTA Management.dmg`

### Build for Windows:
```bash
npm run build-win
```
Output: `dist/OTA Management Setup.exe`

### Build for Linux:
```bash
npm run build-linux
```
Output: `dist/OTA Management.AppImage`

## 📁 Project Structure

```
ota_server/
├── package.json              # Node.js config & scripts
├── start.sh                  # Startup script
├── electron/                 # Electron app files
│   ├── main.js              # Main process (window creation)
│   └── preload.js           # Security bridge
├── front/                    # Frontend UI (unchanged)
│   ├── index.html
│   ├── css/
│   └── js/
│       ├── config.js        # NEW: Dynamic backend config
│       ├── app.js           # Updated with init
│       ├── device.js        # Updated API calls
│       ├── software.js      # Updated API calls
│       ├── ota_task.js      # Updated API calls
│       └── socket.js        # Updated connection
├── backend/                  # Python Flask (unchanged)
│   ├── app.py
│   ├── routes/
│   ├── models/
│   └── db/
└── config/
    └── server_config.json
```

## 🔑 Key Changes Made

### 1. Created Electron Infrastructure
- `electron/main.js`: Manages app window and lifecycle
- `electron/preload.js`: Secure bridge between processes
- `package.json`: Dependencies and build scripts

### 2. Updated Frontend for Electron
- `front/js/config.js`: Dynamic backend URL configuration
- Updated all fetch calls to use `AppConfig.getAPIEndpoint()`
- Updated socket.js to use config URLs
- Fixed file paths for Electron environment

### 3. Backend Integration
- Electron automatically starts Python backend
- Checks if backend is already running
- Cleans up processes on app quit

## 🛠️ Development Tips

### Open DevTools (Developer Console)

- macOS: `Cmd + Option + I`
- Windows/Linux: `Ctrl + Alt + I`

### Reload Application

- macOS: `Cmd + R`
- Windows/Linux: `Ctrl + R`

### View Backend Logs

Backend logs appear in the terminal where you started the app.

### Debug Frontend

Use the DevTools console (same as browser developer tools).

## 🔒 Security Notes

- Backend runs on `localhost:8000` by default
- HTTPS with self-signed certificates (configured in backend)
- `contextIsolation: true` in Electron for security
- No direct Node.js access from renderer process

## 🎯 Features

✅ All existing web features work in desktop app
✅ Native window controls (minimize, maximize, close)
✅ System tray integration (future enhancement)
✅ File system access for firmware uploads
✅ Auto-start backend on launch
✅ Cross-platform support (macOS, Windows, Linux)

## 🐛 Troubleshooting

### Backend doesn't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Verify Python dependencies: `pip3 list | grep -i flask`

### Electron window is blank
- Open DevTools to check for JavaScript errors
- Verify file paths in `electron/main.js`
- Check backend is running: `curl https://localhost:8000`

### Certificate errors
- Backend uses self-signed SSL certificates
- This is expected for local development
- Frontend is configured to accept self-signed certs

### "Module not found" errors
- Run `npm install` again
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

## 🚀 Next Steps

### Future Enhancements:
1. **Auto-updater**: Automatic app updates
2. **System tray**: Run in background
3. **Notifications**: Desktop notifications for OTA status
4. **Multi-window**: Separate windows for different views
5. **Full Node.js backend**: Replace Python with Node.js (future phase)

## 📞 Support

For issues or questions:
1. Check console logs (DevTools + Terminal)
2. Verify all dependencies are installed
3. Test backend independently: `python3 backend/app.py`

---

**Version**: 1.0.0  
**Platform**: Electron + Python Flask  
**License**: MIT
