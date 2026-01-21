#!/bin/bash

# Direct build with network resilience
# Sources environment and sets optimal network settings before building

# Source shell environment
if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc" 2>/dev/null || true
elif [ -f "$HOME/.bashrc" ]; then
  source "$HOME/.bashrc" 2>/dev/null || true
fi

# Set network-friendly environment variables
export npm_config_fetch_timeout=600000          # 10 minutes
export npm_config_fetch_retry=10                # 10 retries
export npm_config_fetch_retry_mintimeout=5000   # 5 seconds min
export npm_config_fetch_retry_maxtimeout=60000  # 60 seconds max
export ELECTRON_BUILDER_CACHE=$HOME/.electron-builder-cache

echo "🔧 Building OTA Management for macOS..."
echo "📊 Network settings:"
echo "   - Timeout: 10 minutes"
echo "   - Retries: 10"
echo "   - Cache: $ELECTRON_BUILDER_CACHE"
echo ""
echo "⏱️  This may take 5-15 minutes on first build..."
echo ""

cd "$(dirname "$0")" || exit 1

npm run build -- --mac

echo ""
echo "✅ Build complete!"
echo ""
ls -lh dist/mac/*.dmg 2>/dev/null || echo "Note: Check dist/ folder for output"
