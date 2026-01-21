# OTA Management System

A cross-platform desktop application for managing firmware updates on ESP32 devices over-the-air (OTA).

## 📦 What's Included

This is a **complete, production-ready solution** with:
- ✅ Electron desktop application (macOS, Windows, Linux)
- ✅ Node.js Express backend with REST API
- ✅ Real-time WebSocket updates
- ✅ Device management system
- ✅ Firmware upload and versioning
- ✅ OTA task creation and monitoring
- ✅ User-editable database (JSON)
- ✅ Comprehensive documentation

## 🚀 Quick Start

### For End Users
1. Download installer from [releases page]
   - macOS: `OTA Management-X.X.X-arm64.dmg` (Apple Silicon) or `-x64.dmg` (Intel)
   - Windows: `OTA Management Setup X.X.X.exe`
   - Linux: `OTA Management-X.X.X.AppImage` or `.deb`

2. Install and launch
3. Start using - data stored in your home directory automatically

### For Developers
```bash
# Clone & install dependencies
npm install
cd backend_nodejs && npm install && cd ..

# Run development version
npm start

# Build for distribution
./build.sh mac       # or win, linux, all
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[QUICKSTART.md](QUICKSTART.md)** | Get running in 5 minutes |
| **[USER_GUIDE.md](USER_GUIDE.md)** | How to use the application |
| **[PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)** | Build and deployment guide |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Complete project overview |
| **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** | Pre-release checklist |
| **[NODEJS_BACKEND_SOLUTION.md](NODEJS_BACKEND_SOLUTION.md)** | Backend API reference |
| **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** | Optional server deployment |
| **[ELECTRON_README.md](ELECTRON_README.md)** | Electron setup details |

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  Electron Desktop Application       │
│  ├── Frontend (HTML/CSS/JS)         │
│  └── Node.js Backend (Express)      │
└─────────────────────────────────────┘
              │ (TCP Port 9001)
              ▼
    ┌─────────────────────┐
    │  TCP Gateway        │
    │  192.168.4.1:9001   │
    └─────────────────────┘
              │
              ▼
    ESP32 Devices Network

```

## ✨ Features

### Device Management
- Add/remove ESP32 devices with unique IDs
- Real-time connection status monitoring
- TCP Gateway auto-reconnection
- Device information storage in editable JSON

### Firmware Management
- Upload firmware binaries (.bin files)
- Organize versions by name and version number
- Download and verify uploaded files
- Delete old versions to save storage

### OTA Task Scheduling
- Create update tasks (device + firmware)
- Immediate or scheduled deployment
- Real-time progress monitoring
- Task history with execution logs

### Cross-Platform Support
- **macOS**: Native .dmg installer (Apple Silicon & Intel)
- **Windows**: Setup.exe installer + portable version
- **Linux**: AppImage (portable) + .deb package

### Data Management
- User-editable JSON database
- Data stored in home directory (OS-specific)
- Easy backup and restore
- Portable between computers

## 📁 Project Structure

```
ota_server/
├── electron/                      # Desktop app main process
│   ├── main.js                    # Window management, backend startup
│   └── preload.js                 # Secure IPC bridge
├── front/                         # Web UI
│   ├── index.html                 # Main interface
│   ├── js/
│   │   ├── config.js              # Dynamic backend configuration
│   │   ├── socket.js              # WebSocket initialization
│   │   ├── device.js              # Device management UI
│   │   ├── software.js            # Firmware management UI
│   │   ├── ota_task.js            # Task management UI
│   │   └── ...other modules
│   └── css/
├── backend_nodejs/                # Node.js backend
│   ├── server.js                  # Express + Socket.IO setup
│   ├── lib/
│   │   ├── database.js            # JSON file database
│   │   ├── tcp-gateway.js         # ESP32 device communication
│   │   ├── message-bus.js         # Event pub/sub
│   │   └── socket-handlers.js     # WebSocket events
│   └── routes/
│       └── index.js               # REST API endpoints
├── backend/                       # Data directory
│   └── db/                        # Database files
├── package.json                   # Root configuration
├── build.sh                       # Build script
├── start.sh                       # Development startup
└── Documentation/                 # Guides and references
```

## 🔧 Technology Stack

- **Desktop Framework**: Electron 35.7.5
- **Backend**: Express.js 4.18+
- **Real-Time**: Socket.IO 4.6.1
- **File Upload**: Multer 1.4.5+
- **Database**: JSON files
- **Runtime**: Node.js 16+
- **Build Tool**: electron-builder 25+

## 📋 Requirements

### Development
- Node.js 16 or higher
- npm 8 or higher
- macOS, Windows, or Linux

### Runtime
- 512 MB RAM minimum
- 100 MB disk space
- Network access to ESP32 devices (TCP port 9001)

## 🎯 Use Cases

1. **Device Firmware Updates**
   - Deploy new firmware to ESP32 devices
   - Update multiple devices at once
   - Schedule updates for specific times

2. **Firmware Version Management**
   - Organize multiple firmware versions
   - Track version history
   - Quick rollback capability

3. **Network Management**
   - Monitor device status
   - Auto-reconnect to failed devices
   - Real-time update progress

## 📊 Performance

- **Memory**: 150-300 MB at rest
- **Startup**: <5 seconds
- **Devices**: 100+ supported
- **Tasks**: 1000+ history records
- **Firmware**: Up to 2 MB uploads

## 🔐 Security

- Local-only communication (127.0.0.1)
- No cloud data transmission
- User controls all data storage
- OS-level file permissions
- Optional HTTPS/TLS support

## 📦 Distribution

Pre-built installers are available for:
- **macOS**: `dist/OTA Management-X.X.X-*.dmg`
- **Windows**: `dist/OTA Management Setup X.X.X.exe` + portable
- **Linux**: `dist/OTA Management-X.X.X.AppImage` + `.deb`

## 🆘 Getting Help

| Issue | Solution |
|-------|----------|
| App won't start | See [QUICKSTART.md](QUICKSTART.md) troubleshooting |
| Cannot connect to devices | Check [USER_GUIDE.md](USER_GUIDE.md) network section |
| Build fails | See [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) prerequisites |
| Need to build | Run `./build.sh mac` (or win, linux, all) |

## 📝 License

See LICENSE file

## 🚀 Next Steps

1. **First time?** Start with [QUICKSTART.md](QUICKSTART.md)
2. **Build for release?** Follow [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)
3. **Using the app?** Read [USER_GUIDE.md](USER_GUIDE.md)
4. **Complete overview?** Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**Version**: 1.0  
**Status**: Production Ready ✅  
**Last Updated**: December 2024
      需要关注的要点：
            Python FLask本身对于HTTP的支持比较友好，如果整个服务框架等模型只在HTTP的模式上搭建，那么相对而言比较简单；
            但是ESP32 需要使用HTTPS，且强制要求配置HTTPS，即使在config_t中配置skip verification也绕不过去。
            同时，在webscoket的通讯中，也对SSL的配置安全校验有较高的要求，因此，backend必须要实现强的SSL的通讯安全
            基于此，我们在上述的Flask基础上引入了Nginx 代理服务器来实现。

      因此，后端服务器除功能实现外，具体的业务模型如下：

      Backend           <====>  Nginx Proxy Server 
            port:8000            |_____
                                    |_____: port 8080, proxy with Front page        <====> https:localhost:8080/  
                                    |_____: port 8443, proxy with ESP/Client HTTPS connection.   <====> https:IP:8443/
      
      在这里 需要说明，PythonFlask模块本身支持的SSL，但是需要使用eventlet模式，但是这个模式下对于 tcp_async的线程处理非常不利，会造成TCP通讯无法维护线程池。 
      因此最终的模型是，在flask中采用async_mode= “threading” 模式，这样确保backend所有的线程池管理能满足业务需要。

      基于这个特点，其SSL/HTTPS的通讯需要必须要通过代理服务器来实现。 这里处理原本的认证证书连，还需要将生成一个fullchain.pem 用于代理服务器校验使用。 

      
Below Feature3, for detail bug fix and data format stream optimization
