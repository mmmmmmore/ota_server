# Network Download Issues - Solutions

The build is failing to download Electron due to network connection drops. Here are solutions in order of effectiveness:

## ✅ Solution 1: Use the Enhanced Build Script (AUTOMATIC RETRIES)

The build.sh script has been updated with automatic retry logic:

```bash
./build.sh mac    # Will retry up to 3 times automatically
./build.sh win
./build.sh linux
```

This now:
- Sets longer download timeouts (2 minutes)
- Configures retry settings (3 retries, up to 30 seconds between attempts)
- Automatically retries the entire build up to 3 times
- Waits 5 seconds between retry attempts

**Try this first** - it should work now with the automatic retries!

## ✅ Solution 2: Pre-Download Electron Binary

Use the new pre-download script to download Electron separately with even longer timeouts:

```bash
chmod +x predownload-electron.sh
./predownload-electron.sh
```

This:
- Sets 10-minute timeout for downloads
- Uses 10 retry attempts
- Caches Electron in `~/.electron-builder-cache`

Then build:
```bash
./build.sh mac
```

## ✅ Solution 3: Manual npm Configuration

Set environment variables before building:

```bash
# macOS/Linux
export npm_config_fetch_timeout=600000
export npm_config_fetch_retry=10
export npm_config_fetch_retry_mintimeout=10000
export npm_config_fetch_retry_maxtimeout=60000
export ELECTRON_BUILDER_CACHE=$HOME/.electron-builder-cache

./build.sh mac
```

Or on Windows (PowerShell):
```powershell
$env:npm_config_fetch_timeout = "600000"
$env:npm_config_fetch_retry = "10"
$env:npm_config_fetch_retry_mintimeout = "10000"
$env:npm_config_fetch_retry_maxtimeout = "60000"
$env:ELECTRON_BUILDER_CACHE = "$env:USERPROFILE/.electron-builder-cache"

./build.sh win
```

## ✅ Solution 4: Check Your Network

Verify your connection isn't being rate-limited:

```bash
# Test direct download
curl -I https://github.com/electron/electron/releases/download/v35.7.5/electron-v35.7.5-darwin-x64.zip

# Check if redirected to GitHub CDN
curl -L https://github.com/electron/electron/releases/download/v35.7.5/electron-v35.7.5-darwin-x64.zip --max-time 30 -o /dev/null -w "HTTP: %{http_code}\n"
```

## ✅ Solution 5: Use Alternative Electron Version

If downloads keep failing, downgrade Electron to a more stable version:

Edit `package.json` and change:
```json
"electron": "^35.7.5"
```

To:
```json
"electron": "^31.0.0"
```

Then:
```bash
rm -rf node_modules
npm install
./build.sh mac
```

## 📊 What Environment Variables Do

| Variable | Effect | Default |
|----------|--------|---------|
| `npm_config_fetch_timeout` | Download timeout in ms | 30000 (30s) |
| `npm_config_fetch_retry` | Number of retries | 3 |
| `npm_config_fetch_retry_mintimeout` | Min wait between retries | 1000ms |
| `npm_config_fetch_retry_maxtimeout` | Max wait between retries | 8000ms |
| `ELECTRON_BUILDER_CACHE` | Where to cache Electron | ~/.cache/electron-builder |

## 🆘 If Still Failing

### Check network connectivity
```bash
ping github.com
ping githubusercontent.com
```

### Check DNS resolution
```bash
nslookup github.com
```

### Try from different network
- Mobile hotspot
- Different WiFi network
- Wired connection

### Check for proxies/VPN
```bash
# macOS
scutil -d -v computername

# Check if VPN is active
networksetup -getwebproxy wi-fi
```

### Check disk space
```bash
# Need ~2GB free for build
df -h
```

### Clear all caches
```bash
npm cache clean --force
rm -rf ~/.electron-builder-cache
rm -rf node_modules
npm install
```

## 📝 Build Script Updates

The `build.sh` script now includes:

✅ **Automatic retries** - Up to 3 attempts per platform  
✅ **Extended timeouts** - 2 minutes per download  
✅ **Environment optimization** - Sets optimal npm download settings  
✅ **Better error messages** - Shows which attempt failed  
✅ **Progress tracking** - Shows attempt count  

## 🚀 Quick Start

Try in this order:

1. **First**: `./build.sh mac` (uses new automatic retry logic)
2. **If still fails**: `./predownload-electron.sh && ./build.sh mac`
3. **If still fails**: Use Solution 3 (manual environment variables)
4. **Last resort**: Use Solution 5 (older Electron version)

---

**Status**: Build infrastructure enhanced with network resilience ✅

The system should now handle network interruptions gracefully with automatic retries.

