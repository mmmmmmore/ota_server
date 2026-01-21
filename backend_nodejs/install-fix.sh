#!/bin/bash

# NPM Installation Troubleshooting Script
# Helps diagnose and fix npm connectivity issues

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     NPM Installation Troubleshooting                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Check network connectivity
echo "1. Testing network connectivity..."
ping -c 1 8.8.8.8 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Internet connection: OK"
else
    echo "   ❌ Internet connection: FAILED"
    echo "   Please check your network connection"
    exit 1
fi

# 2. Check npm registry connectivity
echo ""
echo "2. Testing npm registry connectivity..."
curl -s -I https://registry.npmjs.org/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ NPM registry: OK"
else
    echo "   ❌ NPM registry: FAILED"
    echo "   The npm registry may be temporarily unavailable"
fi

# 3. Clear npm cache
echo ""
echo "3. Clearing npm cache..."
npm cache clean --force
echo "   ✅ Cache cleared"

# 4. Set npm registry
echo ""
echo "4. Setting npm registry..."
npm config set registry https://registry.npmjs.org/
echo "   ✅ Registry configured"

# 5. Retry installation with verbose logging
echo ""
echo "5. Attempting npm install with verbose output..."
npm install --verbose

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Installation Complete                                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
