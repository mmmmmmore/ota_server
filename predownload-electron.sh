#!/bin/bash

# Pre-download Electron binary to cache
# This helps avoid network timeouts during build

set -e

# Source shell environment for proper PATH configuration
if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc" 2>/dev/null || true
elif [ -f "$HOME/.bashrc" ]; then
  source "$HOME/.bashrc" 2>/dev/null || true
elif [ -f "$HOME/.bash_profile" ]; then
  source "$HOME/.bash_profile" 2>/dev/null || true
fi

echo "🔄 Pre-downloading Electron binary..."
echo ""

# Create cache directory
ELECTRON_CACHE="$HOME/.electron-builder-cache"
mkdir -p "$ELECTRON_CACHE"

echo "Cache directory: $ELECTRON_CACHE"
echo ""

# Set environment variables for npm to use longer timeouts
export npm_config_fetch_timeout=600000
export npm_config_fetch_retry=10
export npm_config_fetch_retry_mintimeout=10000
export npm_config_fetch_retry_maxtimeout=60000

# Pre-build to download Electron
echo "Starting download with extended timeout (10 minutes)..."
echo ""

npm install || {
  echo "⚠️  npm install had issues, but continuing..."
}

cd backend_nodejs
npm install || {
  echo "⚠️  backend npm install had issues, but continuing..."
}
cd ..

echo ""
echo "✅ Electron pre-download complete!"
echo ""
echo "You can now run: ./build.sh mac (or win, linux, all)"
echo ""
