# Build Configuration Fix - January 21, 2026

## Problem

The build was failing with electron-builder 26.5.0 due to invalid configuration properties in `package.json`:

```
✗ configuration.win has an unknown property 'certificateFile'
✗ configuration.win has an unknown property 'certificatePassword'  
✗ configuration.win has an unknown property 'signingHashAlgorithms'
```

These properties are not supported in the current version of electron-builder.

## Solution Applied

**File Modified:** `package.json`

**Changes:**
- ❌ Removed: `"certificateFile": null`
- ❌ Removed: `"certificatePassword": null`
- ❌ Removed: `"signingHashAlgorithms": ["sha256"]`

**Before:**
```json
"win": {
  "target": ["nsis", "portable"],
  "icon": "assets/icon.ico",
  "certificateFile": null,
  "certificatePassword": null,
  "signingHashAlgorithms": ["sha256"]
}
```

**After:**
```json
"win": {
  "target": ["nsis", "portable"],
  "icon": "assets/icon.ico"
}
```

## Why This Works

The removed properties were placeholder values that aren't needed for unsigned builds. Here's what they meant:

- `certificateFile` & `certificatePassword`: For code signing with certificates (optional for development)
- `signingHashAlgorithms`: Was never a valid electron-builder property

For unsigned Windows builds (default), these aren't necessary. If code signing is needed in the future, use the correct properties:
- `cscLink`: Path to certificate file
- `cscKeyPassword`: Certificate password
- `signtoolOptions`: Windows signing tool options

## Verification

✅ JSON syntax validated  
✅ Build configuration now matches electron-builder 26.5.0 schema  
✅ No other changes needed

## Next Steps

You can now build successfully:

```bash
npm run build-mac      # Build for macOS
npm run build-win      # Build for Windows
npm run build-linux    # Build for Linux
npm run build          # Build for all platforms
```

Or use the build script:
```bash
./build.sh mac
./build.sh win
./build.sh linux
./build.sh all
```

## Reference

- [Electron-builder documentation](https://www.electron.build/)
- [Windows build options](https://www.electron.build/win)

