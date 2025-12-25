#!/bin/bash
# quick_start.sh

echo "MAR-PD Quick Starter"
echo "===================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed!"
    echo "Install with: pkg install python"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install requests beautifulsoup4 lxml colorama tqdm

# Create directories
mkdir -p data results/exports results/logs data/cache

# Run the tool
echo "Starting MAR-PD..."
python3 main.py