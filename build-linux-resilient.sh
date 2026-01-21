#!/bin/bash

# Direct Linux build with network resilience

if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc" 2>/dev/null || true
elif [ -f "$HOME/.bashrc" ]; then
  source "$HOME/.bashrc" 2>/dev/null || true
fi

export npm_config_fetch_timeout=600000
export npm_config_fetch_retry=10
export npm_config_fetch_retry_mintimeout=5000
export npm_config_fetch_retry_maxtimeout=60000
export ELECTRON_BUILDER_CACHE=$HOME/.electron-builder-cache

echo "🔧 Building OTA Management for Linux..."
echo "📊 Network settings: 10 min timeout, 10 retries"
echo "⏱️  This may take 5-15 minutes on first build..."
echo ""

cd "$(dirname "$0")" || exit 1

npm run build -- --linux

echo ""
echo "✅ Build complete!"
ls -lh dist/linux/*.AppImage dist/linux/*.deb 2>/dev/null || echo "Check dist/ folder for output"
