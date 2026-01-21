#!/bin/bash

# OTA Management Desktop App - Startup Script
# This script starts the Python backend and then launches the Electron app

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

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed."
    echo "Please install Python3 from https://www.python.org/"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
    echo ""
fi

# Check Python dependencies
echo "Checking Python dependencies..."
python3 -c "import flask, flask_cors, flask_socketio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Python dependencies..."
    pip3 install flask flask-cors flask-socketio python-socketio
fi

echo ""
echo "Starting application..."
echo "- Python Backend: Starting on port 8000"
echo "- Electron Frontend: Starting desktop window"
echo ""

# Start the application
npm start
