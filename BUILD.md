# Building OTA Management Desktop Application

This guide covers building the application for macOS and Windows.

## Prerequisites

### macOS
- Node.js v20+ and npm
- Xcode Command Line Tools: `xcode-select --install`

### Windows
- Node.js v20+ and npm
- Visual Studio Build Tools (optional, for better compatibility)

## Building for macOS

### 1. Build DMG (Installer)
```bash
npm run build-mac-dmg
```
Output: `dist/OTA-Management-1.0.0-arm64.dmg` or `dist/OTA-Management-1.0.0-x64.dmg`

**Installation:**
1. Open the .dmg file
2. Drag "OTA Management" to Applications folder
3. Launch from Applications

### 2. Build ZIP (Portable)
```bash
npm run build-mac-zip
```
Output: `dist/OTA-Management-1.0.0-arm64.zip` or `dist/OTA-Management-1.0.0-x64.zip`

**Usage:**
1. Extract the zip file
2. Double-click "OTA Management.app" to run

### 3. Build Both (DMG + ZIP)
```bash
npm run build-mac
```

## Building for Windows

### 1. Build NSIS Installer (.exe)
```bash
npm run build-win-exe
```
Output: `dist/OTA-Management-1.0.0.exe`

**Installation:**
1. Download and run the .exe installer
2. Follow the installation wizard
3. Choose installation directory (default: Program Files)
4. Application will be available in Start Menu and Desktop

### 2. Build Portable Executable
```bash
npm run build-win-portable
```
Output: `dist/OTA-Management-1.0.0-portable.exe`

**Usage:**
- No installation required
- Can run from any location
- No admin rights needed
- No entry in Add/Remove Programs

### 3. Build Both (NSIS + Portable)
```bash
npm run build-win
```

## Building for Linux

```bash
npm run build-linux
```
Outputs:
- `dist/OTA-Management-1.0.0.AppImage` (standalone executable)
- `dist/OTA-Management-1.0.0.deb` (Debian package)

## Build All Platforms
```bash
npm run build-all
```
Builds for macOS, Windows, and Linux in one command.

## Output Structure
```
dist/
├── OTA-Management-1.0.0.dmg          # macOS Installer
├── OTA-Management-1.0.0-arm64.zip    # macOS Portable (Apple Silicon)
├── OTA-Management-1.0.0-x64.zip      # macOS Portable (Intel)
├── OTA-Management-1.0.0.exe          # Windows Installer
├── OTA-Management-1.0.0-portable.exe # Windows Portable
├── OTA-Management-1.0.0.AppImage     # Linux Standalone
└── OTA-Management-1.0.0.deb          # Linux Debian Package
```

## Troubleshooting

### macOS Build Issues

**"Code sign failed" error:**
```bash
# Build without code signing
npm run build-mac -- --sign=""
```

**App won't run on other Macs:**
- Ensure compatibility with minimum macOS version
- Check that Node.js native modules are properly built

### Windows Build Issues

**"Cannot find node.exe":**
```bash
# Ensure Node.js is in PATH
node --version
# If not found, add Node.js installation to PATH
```

**NSIS Installation issues:**
- NSIS is automatically downloaded during first build
- May require internet connection

## Distribution

### macOS
1. **DMG**: Professional installer for end users
2. **ZIP**: For advanced users who prefer portable version
3. **Update mechanism**: Use electron-updater for auto-updates

### Windows
1. **NSIS Installer**: Standard Windows installation
2. **Portable EXE**: No installation, copy and run
3. **Notarization**: Consider code signing for production

## Signing & Notarization (Production)

### macOS Signing
```bash
# Set up for code signing
export CSC_IDENTITY_AUTO_DISCOVERY=false
export CSC_LINK=/path/to/certificate.p12
export CSC_KEY_PASSWORD=your_password

npm run build-mac
```

### Windows Signing
```bash
# Set up certificate paths in package.json or environment
export WIN_CSC_LINK=/path/to/certificate.pfx
export WIN_CSC_KEY_PASSWORD=your_password

npm run build-win
```

## Verification

After building, verify the package:

### macOS
```bash
# Check if app is properly signed
codesign -v dist/OTA\ Management.app

# Check code quality
spctl -a -v dist/OTA\ Management.app
```

### Windows
```bash
# Check if exe is valid
file dist/OTA-Management-1.0.0.exe

# Check digital signature (if signed)
signtool verify /v dist/OTA-Management-1.0.0.exe
```

## File Size Reference
- macOS DMG: ~150-200 MB
- macOS ZIP: ~150-200 MB
- Windows EXE (Installer): ~180-220 MB
- Windows Portable EXE: ~200-250 MB
- Linux AppImage: ~180-220 MB

## Environment Variables

```bash
# Control output directory
export OUT_DIR=./release

# Control build verbosity
export DEBUG=electron-builder

# Platform-specific signing
export CSC_IDENTITY_AUTO_DISCOVERY=false
export WIN_CSC_LINK=/path/to/cert
```

## Next Steps

1. Test the built application thoroughly before distribution
2. Create release notes for each version
3. Set up auto-update mechanism (electron-updater)
4. Consider code signing for trusted distribution
5. Upload to distribution channels (GitHub, website, etc.)

## Support

For issues with electron-builder, refer to:
- https://www.electron.build/
- https://github.com/electron-userland/electron-builder

For Electron issues:
- https://www.electronjs.org/docs
