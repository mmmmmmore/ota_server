#!/bin/bash

# OTA Management - Cross-Platform Build & Package Script
# Builds distributable packages for macOS, Windows, and Linux

set -e

# Source shell environment for proper PATH configuration
if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc" 2>/dev/null || true
elif [ -f "$HOME/.bashrc" ]; then
  source "$HOME/.bashrc" 2>/dev/null || true
elif [ -f "$HOME/.bash_profile" ]; then
  source "$HOME/.bash_profile" 2>/dev/null || true
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
print_header() {
  echo ""
  echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║${NC}  $1"
  echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
  echo ""
}

print_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
check_prerequisites() {
  print_info "Checking prerequisites..."
  
  # Try multiple ways to find node
  local node_path=""
  if command -v node &> /dev/null; then
    node_path=$(command -v node)
  elif [ -f "/usr/local/bin/node" ]; then
    node_path="/usr/local/bin/node"
  elif [ -f "/opt/homebrew/bin/node" ]; then
    node_path="/opt/homebrew/bin/node"
  elif [ -f "$HOME/.nvm/versions/node/*/bin/node" ]; then
    node_path=$(ls -1 "$HOME/.nvm/versions/node/*/bin/node" 2>/dev/null | head -1)
  fi
  
  if [ -z "$node_path" ] || ! "$node_path" --version &> /dev/null; then
    print_error "Node.js not found. Install from https://nodejs.org/"
    echo ""
    echo "If you have Node.js installed but it's not in PATH, try:"
    echo "  1. Close and reopen your terminal"
    echo "  2. Or add Node.js to PATH: export PATH=\$PATH:/usr/local/bin"
    exit 1
  fi
  
  NODE_VERSION=$("$node_path" -v)
  print_success "Node.js $NODE_VERSION found at $node_path"
  
  # Check npm
  local npm_path=""
  if command -v npm &> /dev/null; then
    npm_path=$(command -v npm)
  fi
  
  if [ -z "$npm_path" ]; then
    print_error "npm not found"
    exit 1
  fi
  
  NPM_VERSION=$("$npm_path" -v)
  print_success "npm $NPM_VERSION found at $npm_path"
}

# Install dependencies
install_dependencies() {
  print_info "Installing dependencies..."
  
  if [ ! -d "node_modules" ]; then
    npm install --legacy-peer-deps
  else
    print_warning "node_modules already exists"
  fi
  
  if [ ! -d "backend_nodejs/node_modules" ]; then
    cd backend_nodejs
    npm install --legacy-peer-deps
    cd - > /dev/null
  else
    print_warning "backend_nodejs/node_modules already exists"
  fi
  
  print_success "Dependencies installed"
}

# Clean build artifacts
clean_build() {
  print_info "Cleaning previous builds..."
  rm -rf dist/ out/ .webpack/ 2>/dev/null || true
  print_success "Cleaned"
}

# Build for specific platform with retries
build_platform() {
  local platform=$1
  local max_retries=3
  local retry_count=0
  
  # Set environment variables for better download handling
  export npm_config_fetch_timeout=120000
  export npm_config_fetch_retry=3
  export npm_config_fetch_retry_mintimeout=5000
  export npm_config_fetch_retry_maxtimeout=30000
  
  # Electron-builder specific settings
  export ELECTRON_BUILDER_CACHE=$HOME/.electron-builder-cache
  export ELECTRON_GET_USE_PROXY=false
  
  case $platform in
    mac)
      print_info "Building for macOS (max $max_retries attempts)..."
      while [ $retry_count -lt $max_retries ]; do
        print_info "Attempt $((retry_count + 1))/$max_retries..."
        npm run build -- --mac && { print_success "macOS build complete"; ls -lh dist/*.dmg 2>/dev/null | tail -1 || true; return 0; }
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
          print_warning "Build failed, retrying in 5 seconds..."
          sleep 5
        fi
      done
      print_error "macOS build failed after $max_retries attempts"
      return 1
      ;;
    win)
      print_info "Building for Windows (max $max_retries attempts)..."
      while [ $retry_count -lt $max_retries ]; do
        print_info "Attempt $((retry_count + 1))/$max_retries..."
        npm run build -- --win && { print_success "Windows build complete"; ls -lh dist/*Setup*.exe 2>/dev/null | tail -1 || true; return 0; }
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
          print_warning "Build failed, retrying in 5 seconds..."
          sleep 5
        fi
      done
      print_error "Windows build failed after $max_retries attempts"
      return 1
      ;;
    linux)
      print_info "Building for Linux (max $max_retries attempts)..."
      while [ $retry_count -lt $max_retries ]; do
        print_info "Attempt $((retry_count + 1))/$max_retries..."
        npm run build -- --linux && { print_success "Linux build complete"; ls -lh dist/*.AppImage 2>/dev/null | tail -1 || true; return 0; }
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
          print_warning "Build failed, retrying in 5 seconds..."
          sleep 5
        fi
      done
      print_error "Linux build failed after $max_retries attempts"
      return 1
      ;;
    all)
      print_info "Building for all platforms (max $max_retries attempts per platform)..."
      npm run build && { print_success "All builds complete"; return 0; }
      print_error "Build failed"
      return 1
      ;;
    *)
      print_error "Unknown platform: $platform"
      return 1
      ;;
  esac
}

# Show usage
show_usage() {
  cat << EOF
${BLUE}OTA Management - Build & Package Script${NC}

${YELLOW}Usage:${NC} $0 [COMMAND]

${YELLOW}Commands:${NC}
  mac     Build for macOS only
  win     Build for Windows only
  linux   Build for Linux only
  all     Build for all platforms
  clean   Remove build artifacts
  help    Show this message

${YELLOW}Examples:${NC}
  $0 mac          # Build macOS .dmg
  $0 win          # Build Windows .exe
  $0 linux        # Build Linux .AppImage
  $0 all          # Build everything
  $0 clean        # Clean dist/

${YELLOW}Output:${NC}
  All builds saved to ./dist/

${YELLOW}Requirements:${NC}
  - Node.js v16+
  - npm v8+
  - Platform-specific build tools (see PRODUCTION_SETUP.md)

EOF
}

# Main
main() {
  TARGET="${1:-all}"
  
  case $TARGET in
    help|--help|-h)
      show_usage
      ;;
    clean)
      clean_build
      print_header "Build & Package"
      ;;
    mac|win|linux|all)
      print_header "OTA Management - Build & Package"
      check_prerequisites
      install_dependencies
      clean_build
      build_platform "$TARGET"
      print_header "Build Complete!"
      ;;
    *)
      print_error "Unknown command: $TARGET"
      echo ""
      show_usage
      exit 1
      ;;
  esac
}

main "$@"
