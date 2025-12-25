#!/bin/bash

echo "MAR-PD Installer for Linux/Termux"
echo "=================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed!"
    
    # For Termux
    if [ -d "/data/data/com.termux" ]; then
        echo "Installing Python for Termux..."
        pkg update && pkg install python -y
    else
        echo "Please install Python 3.7+"
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install requests beautifulsoup4 lxml colorama tqdm fake-useragent

# Create directories
echo "Creating directories..."
mkdir -p data data/cache results results/exports results/logs

# Make scripts executable
chmod +x main.py run.py

echo ""
echo "Installation complete!"
echo ""
echo "To run MAR-PD:"
echo "  python3 main.py"
echo ""
echo "For Termux users:"
echo "  Make sure to grant storage permission:"
echo "  termux-setup-storage"