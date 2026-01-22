#!/bin/bash
# Build script for OTA Management Desktop Application

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}OTA Management Desktop - Build Script${NC}\n"

# Check Node.js version
NODE_VERSION=$(node -v)
echo "Node.js version: $NODE_VERSION"

# Check npm version
NPM_VERSION=$(npm -v)
echo "npm version: $NPM_VERSION\n"

# Determine OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}Building for macOS...${NC}"
    
    # Check for M1/M2 chip
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        echo "Detected Apple Silicon (M1/M2/M3)"
    else
        echo "Detected Intel processor"
    fi
    
    echo ""
    echo "Build options:"
    echo "1) DMG Installer (Recommended for distribution)"
    echo "2) ZIP Portable (For advanced users)"
    echo "3) Both DMG and ZIP"
    echo ""
    read -p "Select option (1-3): " choice
    
    case $choice in
        1)
            echo -e "${BLUE}Building DMG installer...${NC}"
            npm run build-mac-dmg
            ;;
        2)
            echo -e "${BLUE}Building ZIP portable...${NC}"
            npm run build-mac-zip
            ;;
        3)
            echo -e "${BLUE}Building DMG and ZIP...${NC}"
            npm run build-mac
            ;;
        *)
            echo "Invalid option"
            exit 1
            ;;
    esac
    
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo -e "${GREEN}Building for Windows...${NC}"
    
    echo ""
    echo "Build options:"
    echo "1) NSIS Installer (.exe) - Recommended"
    echo "2) Portable Executable (.exe) - No installation needed"
    echo "3) Both NSIS and Portable"
    echo ""
    read -p "Select option (1-3): " choice
    
    case $choice in
        1)
            echo -e "${BLUE}Building NSIS installer...${NC}"
            npm run build-win-exe
            ;;
        2)
            echo -e "${BLUE}Building portable executable...${NC}"
            npm run build-win-portable
            ;;
        3)
            echo -e "${BLUE}Building NSIS and portable...${NC}"
            npm run build-win
            ;;
        *)
            echo "Invalid option"
            exit 1
            ;;
    esac
    
else
    echo -e "${GREEN}Building for Linux...${NC}"
    npm run build-linux
fi

echo ""
echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "${BLUE}Output directory: ./dist${NC}\n"

# List generated files
if [ -d "dist" ]; then
    echo "Generated files:"
    ls -lh dist/ | grep -v "^total" | awk '{print "  " $9 " (" $5 ")"}'
fi

echo ""
echo -e "${GREEN}Done! 🎉${NC}"
