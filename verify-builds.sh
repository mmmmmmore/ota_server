#!/bin/bash

# Build Verification Script
# Checks which builds are complete and ready

echo "🔍 OTA Management Build Verification"
echo "===================================="
echo ""

cd "$(dirname "$0")" || exit 1

# Function to check file and report status
check_build() {
    local name=$1
    local files=$2
    
    echo -n "📦 $name: "
    
    found=false
    for file in $files; do
        if [ -f "dist/$file" ]; then
            size=$(ls -lh "dist/$file" | awk '{print $5}')
            echo "✅ Ready ($size)"
            echo "   → dist/$file"
            found=true
            break
        fi
    done
    
    if [ "$found" = false ]; then
        if [ -d "dist/${name,,}-unpacked" ]; then
            echo "⏳ Building... (unpacked folder found)"
        else
            echo "❌ Not started"
        fi
    fi
}

echo "BUILD STATUS:"
echo "============"
check_build "macOS" "OTA*.dmg"
check_build "Windows" "OTA*.exe"
check_build "Linux" "OTA*.AppImage"
echo ""

echo "SUPPORTING FILES:"
echo "================"
[ -f "dist/OTA*.dmg.blockmap" ] && echo "✅ macOS blockmap" || echo "❌ macOS blockmap"
[ -f "dist/OTA*.zip" ] && echo "✅ Portable ZIP" || echo "❌ Portable ZIP"
[ -d "dist/mac" ] && echo "✅ macOS .app bundle" || echo "❌ macOS .app bundle"
echo ""

echo "CACHE STATUS:"
echo "============="
cache_size=$(du -sh ~/.electron-builder-cache 2>/dev/null | awk '{print $1}')
if [ -n "$cache_size" ]; then
    echo "✅ Electron cache: $cache_size"
else
    echo "❌ No cache found"
fi
echo ""

echo "QUICK TEST COMMANDS:"
echo "=================="
echo ""
echo "macOS (DMG):"
echo "  open dist/OTA\\ Management-1.0.0-x64.dmg"
echo ""
echo "macOS (Direct app):"
echo "  open dist/mac/OTA\\ Management.app"
echo ""
echo "Build for Windows:"
echo "  npm run build-win"
echo ""
echo "Build for Linux:"
echo "  npm run build-linux"
echo ""
