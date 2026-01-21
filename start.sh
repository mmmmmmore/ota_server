#!/bin/bash

# OTA Management Desktop App - Startup Script
# This script starts the Node.js backend and then launches the Electron app

echo "======================================"
echo "OTA Management Desktop Application"
echo "======================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if root node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing root Node.js dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install root dependencies"
        exit 1
    fi
    echo ""
fi

# Check if backend_nodejs dependencies are installed
if [ ! -d "backend_nodejs/node_modules" ]; then
    echo "Installing backend Node.js dependencies..."
    cd backend_nodejs
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install backend dependencies"
        exit 1
    fi
    cd ..
    echo ""
fi

echo ""
echo "Starting application..."
echo "- Node.js Backend: Starting on port 8000"
echo "- Electron Frontend: Starting desktop window"
echo ""

# Start the application
npm start
