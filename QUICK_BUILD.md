# Quick Build Guide

## For macOS

### Option 1: Interactive Build (Recommended)
```bash
./build.sh
```
Then select: 1 (DMG), 2 (ZIP), or 3 (Both)

### Option 2: Direct Commands
```bash
# DMG Installer
npm run build-mac-dmg

# ZIP Portable
npm run build-mac-zip

# Both
npm run build-mac
```

**Result:** Check `dist/` folder for `.dmg` or `.zip` files

---

## For Windows

### Option 1: Interactive Build (Recommended)
```cmd
build.bat
```
Then select: 1 (Installer), 2 (Portable), or 3 (Both)

### Option 2: Direct Commands
```cmd
REM Installer (.exe)
npm run build-win-exe

REM Portable (.exe)
npm run build-win-portable

REM Both
npm run build-win
```

**Result:** Check `dist/` folder for `.exe` files

---

## Installation

### macOS
1. **DMG**: Double-click → Drag app to Applications folder
2. **ZIP**: Extract → Double-click app

### Windows
1. **Installer**: Run .exe → Follow wizard → Auto installed to Program Files
2. **Portable**: Run .exe from any location (no installation needed)

---

## First Time Build

First build may take 5-15 minutes (downloads dependencies for your platform).

```bash
# Install dependencies first (if not done)
npm install

# Then build
npm run build-mac    # or build-win
```

---

## Output Files

After successful build, check `dist/` directory:

**macOS:**
- `OTA-Management-1.0.0-arm64.dmg` (Apple Silicon M1/M2/M3)
- `OTA-Management-1.0.0-x64.dmg` (Intel)
- `OTA-Management-1.0.0-arm64.zip`
- `OTA-Management-1.0.0-x64.zip`

**Windows:**
- `OTA-Management-1.0.0.exe` (Installer)
- `OTA-Management-1.0.0-portable.exe` (Portable)

---

## Troubleshooting

### macOS: "Cannot open app" or security warning
```bash
# Build with unsigned app (for testing)
npm run build-mac -- --sign=""

# Or trust app in Security settings
xattr -d com.apple.quarantine "/Applications/OTA Management.app"
```

### Windows: "App won't run"
- Ensure Node.js is in your PATH
- Run build in Command Prompt (not PowerShell)
- Try: `npm run build-win -- --win portable`

### General: Build fails
```bash
# Clean and rebuild
rm -rf dist/
npm install
npm run build-mac   # or build-win
```

---

## Distribution

**Share with users:**
- macOS: `.dmg` file (professional installer)
- Windows: `.exe` installer (standard setup wizard)

**Advanced users:**
- macOS: `.zip` file (portable)
- Windows: `-portable.exe` (no installation)

---

## Need More Help?

See detailed guide: [BUILD.md](./BUILD.md)
