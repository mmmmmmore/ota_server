# OTA Management - Quick Start Guide

Get the OTA Management System running in 5 minutes.

## For End Users (Using the App)

### macOS
```bash
# 1. Download OTA Management-X.X.X-arm64.dmg (Apple Silicon) or -x64.dmg (Intel)
# 2. Double-click the .dmg file
# 3. Drag OTA Management to Applications
# 4. Launch from Applications or Spotlight
```

### Windows
```bash
# 1. Download OTA Management Setup X.X.X.exe
# 2. Run the installer
# 3. Click through installation wizard
# 4. Launch from Start Menu
```

### Linux
```bash
# Option 1: AppImage (portable, no install needed)
chmod +x OTA\ Management-X.X.X.AppImage
./OTA\ Management-X.X.X.AppImage

# Option 2: Deb package
sudo dpkg -i OTA_Management-X.X.X.deb
ota-management
```

### Access Your Data
- **macOS**: Press `Cmd+Shift+D` → Opens: `~/Library/Application Support/OTA Management/`
- **Windows**: Press `Ctrl+Shift+D` → Opens: `%LOCALAPPDATA%\OTA Management\`
- **Linux**: Press `Ctrl+Shift+D` → Opens: `~/.config/OTA Management/`

## For Developers (Building the App)

### 1. Install Prerequisites
```bash
# macOS
brew install node npm

# Windows (from https://nodejs.org/)
# Download and run installer

# Linux (Ubuntu/Debian)
sudo apt-get install nodejs npm
```

### 2. Clone & Install Dependencies
```bash
cd ota_server
npm install
cd backend_nodejs
npm install
cd ..
```

### 3. Run Development Version
```bash
# Option A: Full integrated startup
npm start

# Option B: Manual startup
# Terminal 1: Start backend
cd backend_nodejs
node server.js

# Terminal 2: Start Electron app
npm run dev
```

### 4. Access Application
- **Frontend**: Automatic window opens
- **Backend API**: http://127.0.0.1:8000
- **WebSocket**: ws://127.0.0.1:8000
- **Data**: `./backend/db/` (local development)

### 5. Test Features
1. Click **Devices** tab → Add Device (e.g., ID: 758, IP: 192.168.1.100)
2. Click **Software** tab → Upload Firmware binary (.bin file)
3. Click **Tasks** tab → Create Task (select device + firmware)
4. Watch real-time updates as task progresses

## Building for Distribution

### Quick Build (Current Platform)
```bash
# Requires icons in assets/ (optional, uses defaults otherwise)
./build.sh mac      # macOS only
./build.sh win      # Windows only
./build.sh linux    # Linux only
```

### Build for All Platforms
```bash
# Requires build tools for all platforms
./build.sh all
```

### Outputs
Built packages appear in `dist/`:
```
dist/
├── OTA Management-1.0.0-arm64.dmg          # macOS (Apple Silicon)
├── OTA Management-1.0.0-x64.dmg            # macOS (Intel)
├── OTA Management Setup 1.0.0.exe          # Windows Installer
├── OTA Management 1.0.0.exe                # Windows Portable
├── OTA Management-1.0.0.AppImage           # Linux Portable
└── OTA Management-1.0.0.deb                # Linux Package
```

## Documentation Quick Links

| Document | Purpose |
|----------|---------|
| [USER_GUIDE.md](USER_GUIDE.md) | How to use the application |
| [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) | Detailed build instructions |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Complete project overview |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Release procedures |
| [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | Server deployment |
| [NODEJS_BACKEND_SOLUTION.md](NODEJS_BACKEND_SOLUTION.md) | Backend API reference |

## Common Tasks

### Add a Device
1. App → Devices tab → "Add Device" button
2. Enter: Device ID, Name, IP Address, Model
3. Click Save
4. TCP Gateway auto-connects

### Upload Firmware
1. App → Software tab → "Add Software" button
2. Enter: Name (e.g., "App v2.1"), Version (e.g., "2.1.0")
3. Click "Select File" → Choose .bin firmware file
4. Click Upload
5. Firmware appears in list

### Create OTA Task
1. App → Tasks tab → "Create Task" button
2. Select Target Device (dropdown)
3. Select Firmware Version (dropdown)
4. Choose: Immediate or Scheduled
5. Click Create Task
6. Watch progress bar

### Access Data Files
- **macOS**: Press `Cmd+Shift+D` or Menu → Open Data Folder
- **Windows**: Press `Ctrl+Shift+D` or Menu → Open Data Folder
- **Linux**: Press `Ctrl+Shift+D` or Menu → Open Data Folder

### Backup Data
```bash
# Backup your database
cp -r ~/Library/Application\ Support/OTA\ Management ~/Desktop/ota-backup   # macOS
cp -r %LOCALAPPDATA%\OTA\ Management %USERPROFILE%\Desktop\ota-backup       # Windows
cp -r ~/.config/OTA\ Management ~/ota-backup                                # Linux
```

### Restore Data
```bash
# Stop the application first, then restore backup
cp -r ~/Desktop/ota-backup/* ~/Library/Application\ Support/OTA\ Management/  # macOS
```

## Troubleshooting Quick Fixes

### App Won't Start
```bash
# 1. Check Node.js is installed
node -v npm -v

# 2. Reinstall dependencies
npm install
cd backend_nodejs && npm install && cd ..

# 3. Check port 8000 is free
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Cannot Connect to Devices
- Verify TCP Gateway IP: `ping 192.168.4.1`
- Check port 9001 is open: No firewall blocking
- Check device is on same network

### Database Corrupted
```bash
# Backup current state
cp backend/db/devices.json backend/db/devices.json.backup

# Delete corrupted file (app will recreate it)
rm backend/db/devices.json

# Restart app
npm start
```

### Build Fails
```bash
# Clean and reinstall
rm -rf dist node_modules backend_nodejs/node_modules
npm install
cd backend_nodejs && npm install && cd ..

# Try build again
./build.sh mac
```

## Network Configuration

### Default Settings
```
Backend Server: 127.0.0.1:8000
TCP Gateway: 192.168.4.1:9001
WebSocket: ws://127.0.0.1:8000
```

### Custom Configuration (Advanced)

Create `.env` file in data directory:

**macOS/Linux**: `~/.config/OTA Management/.env` or `~/Library/Application Support/OTA Management/.env`

**Windows**: `%LOCALAPPDATA%\OTA Management\.env`

```ini
GW_IP=192.168.100.1
GW_TCP_PORT=9001
PORT=9000
DB_PATH=/custom/path/db
```

Restart app for changes to take effect.

## Performance Notes

| Metric | Value |
|--------|-------|
| Startup Time | <5 seconds |
| Memory Usage | 150-300 MB at rest |
| Supported Devices | 100+ |
| Task History | 1000+ tasks |
| Firmware Upload | Up to 2 MB |

## Support

### Check Logs
```bash
# Logs are in the data directory under logs/ (if implemented)
# Or check browser console (F12) for frontend errors

# View backend console
npm start  # Shows all logs
```

### Get Help
- Read [USER_GUIDE.md](USER_GUIDE.md) for feature details
- Check [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) for technical setup
- Review [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for release procedures

## What's Next?

1. **Start building**: `npm start`
2. **Add test devices**: Devices tab → Add Device
3. **Upload test firmware**: Software tab → Add Software
4. **Create test task**: Tasks tab → Create Task
5. **Build for release**: `./build.sh mac` (or win/linux)
6. **Share with users**: Distribute from dist/

---

**Need more help?** See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for complete documentation index.

