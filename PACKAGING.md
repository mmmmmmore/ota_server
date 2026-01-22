# 📦 OTA Management - Application Packaging Setup

## ✅ What's Been Configured

### Build Scripts
- **`build.sh`** - Interactive build for macOS (select DMG/ZIP/Both)
- **`build.bat`** - Interactive build for Windows (select Installer/Portable/Both)
- **`QUICK_BUILD.md`** - Fast reference guide
- **`BUILD.md`** - Complete detailed guide

### Build Commands in package.json

#### macOS
```
npm run build-mac        # Build DMG + ZIP
npm run build-mac-dmg    # Build DMG only
npm run build-mac-zip    # Build ZIP only
```

#### Windows
```
npm run build-win        # Build Installer + Portable
npm run build-win-exe    # Build Installer (.exe)
npm run build-win-portable # Build Portable
```

#### Linux
```
npm run build-linux      # Build AppImage + DEB
```

#### All Platforms
```
npm run build-all        # Build for macOS, Windows, Linux
```

---

## 🚀 Quick Start

### For macOS
```bash
cd /Users/maochun/esp32prj/Project_CAM/branch/ota_Server/server_node/ota_server
./build.sh
```
Then select option 1, 2, or 3

### For Windows
```cmd
cd C:\path\to\ota_server
build.bat
```
Then select option 1, 2, or 3

---

## 📂 Output Location

All built applications go to: **`dist/`** folder

### macOS Output
- `OTA-Management-1.0.0-arm64.dmg` - DMG installer (Apple Silicon)
- `OTA-Management-1.0.0-x64.dmg` - DMG installer (Intel)
- `OTA-Management-1.0.0-arm64.zip` - Portable ZIP
- `OTA-Management-1.0.0-x64.zip` - Portable ZIP

### Windows Output
- `OTA-Management-1.0.0.exe` - NSIS Installer
- `OTA-Management-1.0.0-portable.exe` - Portable Executable

---

## 📋 Build Configuration

The build is configured in **`package.json`** under the `"build"` section:

### Included in Package
✅ electron/ - Application main file
✅ front/ - Frontend files
✅ backend_nodejs/ - Node.js backend server
✅ node_modules/ - All dependencies
✅ package.json - Configuration
✅ certs/ - SSL certificates (for future HTTPS)
✅ assets/ - Icons and resources

### macOS Specifics
- **Target**: DMG installer + ZIP portable
- **Icon**: `assets/icon.icns`
- **Min OS**: Not restricted (will run on recent macOS)

### Windows Specifics
- **Target**: NSIS Installer + Portable EXE
- **Icon**: `assets/icon.ico`
- **Architecture**: x64 (64-bit)
- **Admin Rights**: Not required

---

## 🔧 System Requirements for Building

### Build on macOS (for macOS binaries)
- Node.js v20+
- Xcode Command Line Tools (install with: `xcode-select --install`)
- ~500MB disk space for build artifacts

### Build on Windows (for Windows binaries)
- Node.js v20+
- ~500MB disk space for build artifacts
- Optional: Visual Studio Build Tools

### Cross-Platform Building
⚠️ **Note**: You must build on each platform to generate binaries for that platform
- Can't build Windows .exe on macOS
- Can't build macOS .dmg on Windows
- For CI/CD, use GitHub Actions or similar

---

## 📦 Installation Methods

### macOS DMG
1. Double-click the `.dmg` file
2. Drag "OTA Management" to Applications folder
3. Open from Applications (or Launchpad)

### macOS ZIP
1. Extract the `.zip` file
2. Double-click "OTA Management.app"
3. Can move it anywhere or run from Downloads

### Windows Installer
1. Run `OTA-Management-1.0.0.exe`
2. Follow the installation wizard
3. Choose installation directory (default: Program Files)
4. Creates Start Menu shortcut and optional Desktop shortcut

### Windows Portable
1. Download `OTA-Management-1.0.0-portable.exe`
2. Run directly - no installation needed!
3. Can run from any location (USB drive, etc.)

---

## 🎯 First Build Steps

1. **Ensure Node.js is installed**
   ```bash
   node --version  # Should be v20+
   npm --version
   ```

2. **Install dependencies** (if not done)
   ```bash
   npm install
   ```

3. **Build for your platform**
   ```bash
   # macOS
   ./build.sh
   
   # Windows
   build.bat
   
   # or direct command
   npm run build-mac-dmg
   ```

4. **Wait for completion** (5-15 minutes on first build)

5. **Find your files in `dist/` folder**

---

## 📊 Expected File Sizes

- macOS DMG: ~150-200 MB
- macOS ZIP: ~150-200 MB
- Windows Installer: ~180-220 MB
- Windows Portable: ~200-250 MB
- Linux AppImage: ~180-220 MB

---

## 🔐 Security & Signing (Optional/Future)

For production distribution, you may want to:

### macOS Code Signing
```bash
export CSC_LINK=/path/to/certificate.p12
export CSC_KEY_PASSWORD=your_password
npm run build-mac
```

### Windows Code Signing
```bash
export WIN_CSC_LINK=/path/to/certificate.pfx
export WIN_CSC_KEY_PASSWORD=your_password
npm run build-win
```

---

## 📝 Distribution Checklist

Before distributing:
- [ ] Test the built app on actual hardware
- [ ] Verify all features work (devices, software, tasks)
- [ ] Check icon displays correctly
- [ ] Verify menu shortcuts work
- [ ] Test on minimum supported OS versions
- [ ] Create release notes
- [ ] Test upgrade from previous version (if applicable)

---

## 🐛 Troubleshooting

### "electron-builder: command not found"
```bash
npm install
```

### Build fails with "cannot find node"
- Ensure Node.js is in your PATH
- Try: `npm run build-mac -- --help`

### macOS: "Cannot open app" security error
```bash
# Trust the app
xattr -d com.apple.quarantine /path/to/app
```

### Windows: Build hangs on first run
- First build downloads NSIS (~20MB)
- Ensure stable internet connection
- Try again or check firewall settings

---

## 📚 More Information

- Detailed guide: [BUILD.md](./BUILD.md)
- Quick reference: [QUICK_BUILD.md](./QUICK_BUILD.md)
- Electron Builder: https://www.electron.build/
- Electron: https://www.electronjs.org/

---

## ✨ You're All Set!

Your OTA Management application is ready to be built and packaged for distribution!

**Next Step:** Run `./build.sh` (macOS) or `build.bat` (Windows) to create your first package.
