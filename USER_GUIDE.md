# OTA Management - User Guide

## Welcome
This guide helps you use the OTA Management System to manage device firmware updates over-the-air (OTA).

## Installation

### macOS
1. Download `OTA Management-X.X.X-*.dmg`
2. Open the file in Finder
3. Drag "OTA Management" to the "Applications" folder
4. Launch from Applications or Spotlight (Cmd+Space, type "OTA Management")

### Windows
1. Download `OTA Management Setup X.X.X.exe`
2. Run the installer (Administrator recommended)
3. Follow the installation wizard
4. Launch from Start Menu or Desktop shortcut

### Linux

**Option 1: AppImage (Portable)**
```bash
chmod +x OTA\ Management-X.X.X.AppImage
./OTA\ Management-X.X.X.AppImage
```

**Option 2: Debian Package**
```bash
sudo dpkg -i OTA_Management-X.X.X.deb
# Then launch from applications menu or command:
ota-management
```

## First Launch

### System Requirements
- **Memory**: 512 MB minimum, 2 GB recommended
- **Storage**: 100 MB for application + database
- **Network**: Local network access to ESP32 devices
- **Port**: TCP 9001 for device gateway

### Initial Setup
1. Open OTA Management
2. Application creates data folder automatically:
   - **macOS**: `~/Library/Application Support/OTA Management/`
   - **Windows**: `%LOCALAPPDATA%\OTA Management\`
   - **Linux**: `~/.config/OTA Management/`
3. Main window shows three tabs: **Devices**, **Software**, **Tasks**

## Core Features

### Devices Tab
Manage ESP32 devices for OTA updates.

#### Adding a Device
1. Click "Add Device" button
2. Enter device information:
   - **Device ID**: Unique identifier (e.g., "758")
   - **Device Name**: Display name (e.g., "Warehouse_01")
   - **IP Address**: Device's IP on network (e.g., "192.168.1.100")
   - **Model**: Device model (e.g., "ESP32-CAM")
3. Click "Save"
4. Device appears in list and TCP gateway connects automatically

#### Viewing Device Status
- **Connected**: Green dot - device reachable via TCP
- **Disconnected**: Red dot - device offline or unreachable
- **Last Seen**: Timestamp of last communication

#### Removing a Device
1. Select device in list
2. Click "Delete" button
3. Confirm deletion

#### Testing Connection
1. Select device
2. Click "Ping" button
3. Status message shows connection status

### Software Tab
Manage firmware versions for deployment.

#### Adding Firmware
1. Click "Add Software" button
2. Fill in details:
   - **Name**: Version name (e.g., "App v2.1")
   - **Version**: Version string (e.g., "2.1.0")
   - **Description**: Release notes (e.g., "Bug fixes and improvements")
3. Click "Select File" and choose firmware binary (`.bin` file)
4. Click "Upload"

#### Managing Versions
- **List View**: Shows all uploaded firmware versions
- **Download**: Click version to download/verify
- **Delete**: Select and delete old versions to save storage

#### Firmware File Format
- **Type**: ELF binary or binary format (.bin)
- **Size**: Typically 300 KB - 2 MB for ESP32
- **Location**: Stored in user data directory

### Tasks Tab
Monitor and manage OTA update tasks.

#### Creating an OTA Task
1. Select target **Device** from dropdown
2. Select firmware **Version** to deploy
3. Choose deployment method:
   - **Immediate**: Update starts right now
   - **Scheduled**: Set date/time for update
4. Optional: Add notes (e.g., "Production rollout")
5. Click "Create Task"

#### Monitoring Tasks
- **Status Column** shows:
  - 🔵 **Pending**: Waiting for device
  - 🟡 **In Progress**: Update running
  - 🟢 **Completed**: Update successful
  - 🔴 **Failed**: Error during update
- **Progress Bar**: Shows completion percentage
- **Details**: Click to see full task log

#### Task History
- Tasks are recorded with timestamps
- Each entry shows: device, version, status, duration
- Files saved to `tasks/` subfolder in data directory

### Real-Time Updates
WebSocket connection provides:
- Live device connection status
- Instant task status updates
- No manual refresh needed
- Automatic reconnection if network drops

## Data Management

### Accessing Your Data

#### Option 1: Menu (Recommended)
- **macOS/Linux**: Press `Cmd+Shift+D`
- **Windows**: Press `Ctrl+Shift+D`
- Opens file explorer to data directory

#### Option 2: Manual Navigation
**macOS**:
```
Finder → Go → Go to Folder → ~/Library/Application Support/OTA Management/
```

**Windows**:
```
File Explorer → address bar → %LOCALAPPDATA%\OTA Management\
```

**Linux**:
```
File manager → ~/.config/OTA Management/
```

### Data Structure
```
OTA Management/
├── devices.json         # Device registry
├── software_list.json   # Firmware metadata
├── softwares.json       # Firmware file references
├── firmware/            # Binary firmware files
└── tasks/               # Task history
    ├── 20251229_085302_758.json
    ├── 20251229_093745_758.json
    └── ...
```

### Backing Up Data
1. Open data folder (Cmd/Ctrl+Shift+D)
2. Copy entire folder to external drive or cloud storage
3. Recommended backup frequency: after each production deployment

### Restoring from Backup
1. Close OTA Management
2. Navigate to data folder location
3. Replace all files with backup copies
4. Restart OTA Management

### Sharing Data Between Computers
1. On source computer: Open data folder, copy entire directory
2. On target computer: Paste into same location
3. Restart application
4. All devices and firmware versions appear on new computer

## Troubleshooting

### Application Won't Start

**macOS**: "App is damaged"
```
System Preferences → Security & Privacy → General
Click "Open Anyway" next to OTA Management
```

**Windows**: "Windows protected your PC"
```
Click "More info" → "Run anyway"
```

**Linux**: Permission denied
```bash
chmod +x OTA\ Management-X.X.X.AppImage
```

### Cannot Connect to Devices

**Check TCP Gateway IP**
1. Menu → Help → Logs
2. Look for "TCP Gateway" connection messages
3. Verify IP matches device configuration
   - Default: `192.168.4.1`
   - Default port: `9001`

**Verify Network**
```
ping 192.168.4.1    # macOS/Linux
ping 192.168.4.1    # Windows (Command Prompt)
```

**Check Firewall**
- Ensure port 9001 is not blocked
- Windows Defender → Firewall → Allow app through firewall

### Task Status Shows "Failed"

**View Error Details**
1. Click on task in Tasks tab
2. Open "Log" or "Details" pane
3. Error message explains the issue

**Common Issues**
- **Device Offline**: Device not reachable - check network
- **Invalid Firmware**: Corrupted file - re-upload
- **Timeout**: Device too slow - try again with larger timeout

### Database Corruption

**Symptoms**
- Devices/software disappear after restart
- Application crashes when loading data
- JSON files show invalid data

**Recovery**
1. Close application
2. Open data folder (Cmd/Ctrl+Shift+D)
3. Backup current files (copy to Desktop)
4. Delete corrupted file (e.g., `devices.json`)
5. Restart application (creates fresh file)
6. Re-add devices manually or restore from backup

### High Memory Usage

**Normal**: 150-300 MB
**High**: Over 500 MB (with many tasks)

**Solution**
1. Delete old tasks from Tasks tab
2. Restart application
3. Memory usage resets

## Advanced Features

### Command Line Configuration (Advanced)

Users can create `.env` file in data directory for custom settings:

**macOS/Linux**: `~/.config/OTA Management/.env`
**Windows**: `%LOCALAPPDATA%\OTA Management\.env`

```ini
# Database path override (for shared storage)
DB_PATH=/mnt/shared/ota_db

# Firmware storage path
FIRMWARE_PATH=/external/drive/firmware

# Backend server settings (local only)
PORT=8000
HOST=127.0.0.1

# TCP Gateway settings
GW_IP=192.168.4.1
GW_TCP_PORT=9001
```

Restart app after changes.

### Exporting Data for Analysis

**Export Devices**
1. Open data folder
2. Open `devices.json` with text editor
3. Copy data, paste into Excel/Google Sheets using JSON to Table tool

**Export Task History**
1. Open data folder → `tasks/` subfolder
2. All `.json` files can be imported into analysis tools
3. Use JSON parser or script for bulk processing

## Performance & Limits

| Aspect | Capacity | Notes |
|--------|----------|-------|
| Devices | 100+ | Tested with 100 devices |
| Firmware Versions | 50+ | Per model type |
| Task History | 1000+ | 1000 tasks = ~50 MB |
| Memory | ~200 MB | At rest, 500 MB under load |
| Storage | ~100 MB | Base + database/firmware |

## Security & Safety

### What's Transmitted Over Network
- Device IP addresses and status
- Firmware binary data (once per task)
- Task updates and status
- **NOT**: Passwords or credentials (v1)

### Local Storage
- All data stored in user's home directory
- Only local users can access data
- Data not sent to cloud (local only)

### Best Practices
- ✅ Backup data before major deployments
- ✅ Test firmware on single device first
- ✅ Verify device connectivity before deployment
- ✅ Monitor task progress until completion
- ✅ Have rollback plan if update fails

## Support & Help

### View Logs
Menu → Help → Open Logs
- Shows application events and errors
- Useful for troubleshooting
- Can be shared with support

### Get Help
- Check TROUBLESHOOTING section above
- Read device documentation
- Contact support with logs if stuck

### Report Issues
When reporting problems, include:
1. Application version (Menu → About)
2. Operating system version
3. Relevant logs (Menu → Help → Logs)
4. Description of what happened
5. Steps to reproduce

## Updates & Support

### Checking Version
Menu → About OTA Management → Version X.X.X

### Updating to New Version
1. Download new installer
2. Run installer (same location)
3. All data preserved during upgrade
4. Restart application

### Uninstall

**macOS**
```
Applications folder → drag OTA Management to Trash
Data remains in ~/Library/Application Support/OTA Management/
```

**Windows**
```
Settings → Apps → Apps & Features → OTA Management → Uninstall
Data remains in %LOCALAPPDATA%\OTA Management\
```

**Linux (AppImage)**
```
Delete the .AppImage file
Data remains in ~/.config/OTA Management/
```

**Linux (Deb)**
```bash
sudo apt remove ota-management
```

## Tips & Tricks

### Batch Device Management
1. Export devices.json
2. Edit in spreadsheet or text editor
3. Import back into application
4. Good for adding 20+ devices at once

### Firmware Organization
- Use clear version numbering (e.g., 1.0.0)
- Document changes in description field
- Keep old versions for 1-2 weeks for rollback

### Task Scheduling
- Schedule updates for maintenance windows
- Avoid during peak usage times
- Stagger deployments across devices

### Monitoring
- Check "Last Seen" timestamp regularly
- Set up external monitoring (script to parse logs)
- Archive completed tasks monthly

## Feedback & Suggestions

We'd love to hear from you!
- What features would help?
- Bugs or issues?
- Performance suggestions?

Please include version and OS when providing feedback.

---

**Version**: 1.0  
**Last Updated**: December 2024  
**For technical details, see**: PRODUCTION_SETUP.md, NODEJS_BACKEND_SOLUTION.md
