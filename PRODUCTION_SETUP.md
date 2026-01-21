# OTA Management - Production Setup Guide

## Overview
This document describes how to build, package, and distribute the OTA Management System as a cross-platform desktop application for macOS, Windows, and Linux.

## Architecture
- **Frontend**: Electron-based desktop UI (HTML/CSS/JavaScript)
- **Backend**: Node.js Express server with Socket.IO
- **Database**: JSON files stored in user's home directory (editable)
- **Communication**: REST API + WebSocket for real-time updates

## Database Storage Locations

### Development
```
./backend/db/          # Local development database
./backend/firmware/    # Firmware files
```

### Production (User-Editable)

#### macOS
```
~/Library/Application Support/OTA Management/
├── devices.json
├── software_list.json
├── softwares.json
└── tasks/
    ├── 20251229_085302_758.json
    ├── 20251229_093745_758.json
    └── ... (task files)
```

#### Windows
```
C:\Users\<username>\AppData\Local\OTA Management\
├── devices.json
├── software_list.json
├── softwares.json
└── tasks/
```

#### Linux
```
~/.config/OTA Management/
├── devices.json
├── software_list.json
├── softwares.json
└── tasks/
```

## Building for Distribution

### Prerequisites
```bash
# macOS
brew install node npm

# Windows
# Install Node.js from https://nodejs.org/

# Linux (Ubuntu/Debian)
sudo apt-get install nodejs npm
```

### Install Dependencies
```bash
# Root level dependencies
npm install

# Backend dependencies
cd backend_nodejs
npm install
cd ..
```

### Create Application Icons (Optional but Recommended)

Create `assets/` directory with icons:
```bash
mkdir -p assets
# Add these files:
# - icon.icns (macOS, 512x512 or larger)
# - icon.ico (Windows, 256x256 or larger)
# - icon.png (Linux, 512x512)
```

You can generate icons using:
```bash
# Using ImageMagick or online tools like:
# https://icoconvert.com/ (PNG to ICO)
# https://convertio.co/png-icns/ (PNG to ICNS)
```

### Build Commands

#### Build for macOS Only
```bash
npm run build -- --mac
```
Output: `dist/OTA Management-X.X.X-*.dmg` (Disk Image for installation)

#### Build for Windows Only
```bash
npm run build -- --win
```
Output: 
- `dist/OTA Management Setup X.X.X.exe` (Installer)
- `dist/OTA Management X.X.X.exe` (Portable)

#### Build for Linux Only
```bash
npm run build -- --linux
```
Output:
- `dist/OTA Management-X.X.X-*.AppImage`
- `dist/OTA Management-X.X.X-*.deb`

#### Build for All Platforms (requires all tools)
```bash
npm run build
```

### Build Script (Alternative)
We provide a `build.sh` script for convenience:

```bash
chmod +x build.sh

# Build for macOS
./build.sh mac

# Build for Windows
./build.sh win

# Build for Linux
./build.sh linux

# Build for all platforms
./build.sh all

# Clean previous builds
./build.sh clean
```

## Distribution and Installation

### macOS Distribution
1. Build: `npm run build -- --mac`
2. User receives: `OTA Management-X.X.X-arm64.dmg` (Apple Silicon) or `-x64.dmg` (Intel)
3. Installation: User opens .dmg and drags app to Applications folder
4. First Launch: App creates user data directory at `~/Library/Application Support/OTA Management/`

### Windows Distribution
1. Build: `npm run build -- --win`
2. User receives: `OTA Management Setup X.X.X.exe` (recommended for most users)
3. Installation: User runs installer, selects install location
4. First Launch: App creates user data directory at `%LOCALAPPDATA%\OTA Management\`
5. Uninstall: Windows Control Panel → Programs → Uninstall

### Linux Distribution
1. Build: `npm run build -- --linux`
2. Options:
   - **AppImage**: `OTA Management-X.X.X.AppImage` (portable, no installation needed)
   - **Deb Package**: `OTA Management-X.X.X.deb` (for Debian/Ubuntu)
3. Installation:
   - AppImage: Make executable (`chmod +x *.AppImage`) and run
   - Deb: `sudo dpkg -i OTA Management-X.X.X.deb`
4. First Launch: App creates user data directory at `~/.config/OTA Management/`

## User Data Management

### Accessing Data
Users can access their data through:

1. **Menu Option** (Recommended):
   - macOS/Linux: Press `Cmd+Shift+D` (or menu: Application → Open Data Folder)
   - Windows: Press `Ctrl+Shift+D` (or menu: Application → Open Data Folder)
   - Opens file explorer to data directory

2. **Manual Navigation**:
   - macOS: `~/Library/Application Support/OTA Management/`
   - Windows: `%LOCALAPPDATA%\OTA Management\` (copy path to Explorer)
   - Linux: `~/.config/OTA Management/`

### Data Structure
```
userData/
├── devices.json          # Device registry
│   └── [{"id": "758", "ip": "192.168.1.100", ...}, ...]
│
├── software_list.json    # Metadata for software versions
│   └── [{"id": "sw1", "name": "App v1.0", ...}, ...]
│
├── softwares.json        # Software binary storage references
│   └── [{"id": "sw1", "version": "1.0", "file": "path", ...}, ...]
│
└── tasks/                # OTA task history
    └── YYYYMMDD_HHMMSS_DEVID.json
        └── {"taskId": "...", "deviceId": "758", "status": "completed", ...}
```

### Editing Data
Users can:
- Manually edit JSON files (requires JSON editor)
- Delete task files to clean up history
- Backup entire folder for disaster recovery
- Share data between computers (copy userData folder)

**Important**: App must be closed before manually editing JSON files to avoid conflicts.

## Runtime Configuration

### Environment Variables (Advanced Users)

Users can create a `.env` file in the application data directory to override default settings:

```bash
# ~/.config/OTA Management/.env (Linux)
# ~/Library/Application Support/OTA Management/.env (macOS)
# %LOCALAPPDATA%\OTA Management\.env (Windows)

# Database location override
DB_PATH=/custom/path/to/database

# Firmware location override
FIRMWARE_PATH=/custom/path/to/firmware

# Backend settings
PORT=8000
HOST=127.0.0.1
GW_IP=192.168.4.1
GW_TCP_PORT=9001
```

Note: Environment variables in `.env` must be set before app startup. Modify and restart.

## Troubleshooting

### Application Won't Start
- **macOS**: If "App is damaged", allow in Security & Privacy → Open Anyway
- **Windows**: Run installer as Administrator
- **Linux**: Ensure AppImage is executable: `chmod +x *.AppImage`

### Data Directory Not Found
- Check OS-specific paths listed above
- Ensure application has write permissions to home directory
- Try "Open Data Folder" from menu to verify path

### Cannot Connect to Devices
- Verify TCP Gateway IP: `GW_IP=192.168.4.1` (default)
- Check firewall allows port 9001
- Confirm device is on same network segment

### Database Corruption
- Close application
- Navigate to data directory
- Backup current `devices.json` and `softwares.json`
- Delete files, restart app (will create fresh copies)
- Re-register devices

## Security Considerations

1. **Local Network Only**: Backend server listens on 127.0.0.1 (localhost only)
2. **No Authentication**: Suitable for trusted networks (office, lab)
3. **Data Access**: User has full read/write access to JSON files
4. **HTTPS**: Can be enabled by modifying backend (not in v1)

## Migration from Web Version

If users are migrating from the web-based version:

1. **Export Data**: From old web interface, export devices and software list
2. **Manual Migration**: Copy JSON files to new app's data directory
3. **Restart App**: Application will load imported data
4. **Verification**: Check devices/software appear in UI

## Support and Updates

### Checking Version
Menu → About OTA Management → Version X.X.X

### Getting Help
- Check logs: Application menu → Help → Open Logs
- Logs location: Same as data directory in `logs/` subfolder
- Send logs with bug reports

### Updating
1. Download new `.dmg`, `.exe`, or `.AppImage`
2. Install over existing installation (data preserved)
3. Restart application

## Performance Notes

- **Database Size**: App handles 100+ devices and 1000+ tasks smoothly
- **Memory Usage**: ~150-250 MB at rest, ~500 MB under heavy use
- **Storage**: ~5-10 MB for typical database + firmware files

## Next Steps

1. **Icon Creation**: Create icons for your branding (see "Create Application Icons" section)
2. **Version Bump**: Update version in `package.json` if needed
3. **Build**: Run build commands above
4. **Testing**: Test installers on target platforms
5. **Distribution**: Upload installers to web server or app store
6. **Documentation**: Provide users with installation instructions and data location info

