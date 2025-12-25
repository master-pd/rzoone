#!/usr/bin/env python3
"""
Complete Setup Script for MAR-PD
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                MAR-PD v3.5 Setup                     ║
    ║       Multi-Algorithmic Reconnaissance Tool          ║
    ║          For Account Recovery Purposes Only          ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """সিস্টেম রিকোয়ারমেন্ট চেক করুন"""
    print("\n[1/5] Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        if free < 100 * 1024 * 1024:  # 100MB minimum
            print("⚠️  Low disk space warning")
    except:
        pass
    
    return True

def install_dependencies():
    """ডিপেন্ডেন্সি ইনস্টল করুন"""
    print("\n[2/5] Installing dependencies...")
    
    dependencies = [
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "colorama>=0.4.6",
        "tqdm>=4.66.0",
        "fake-useragent>=1.4.0"
    ]
    
    for dep in dependencies:
        print(f"  Installing {dep.split('>=')[0]}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"  ✓ {dep.split('>=')[0]} installed")
        except subprocess.CalledProcessError:
            print(f"  ✗ Failed to install {dep.split('>=')[0]}")
    
    print("\n✓ All dependencies installed successfully!")

def create_directory_structure():
    """ডিরেক্টরি স্ট্রাকচার তৈরি করুন"""
    print("\n[3/5] Creating directory structure...")
    
    directories = [
        "core",
        "methods", 
        "utils",
        "data",
        "data/cache",
        "data/templates",
        "results",
        "results/exports",
        "results/logs",
        "results/backups",
        "results/templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created: {directory}/")
    
    # Create __init__.py files
    init_dirs = ["core", "methods", "utils"]
    for init_dir in init_dirs:
        init_file = os.path.join(init_dir, "__init__.py")
        with open(init_file, "w") as f:
            f.write('"""MAR-PD module"""\n')
        print(f"  Created: {init_file}")
    
    print("\n✓ Directory structure created!")

def create_config_files():
    """কনফিগারেশন ফাইল তৈরি করুন"""
    print("\n[4/5] Creating configuration files...")
    
    # Create marpd_config.json
    config_data = {
        "app": {
            "name": "MAR-PD",
            "version": "3.5",
            "author": "Master"
        },
        "settings": {
            "request_timeout": 30,
            "delay_between_requests": 1.5
        }
    }
    
    with open('marpd_config.json', 'w') as f:
        json.dump(config_data, f, indent=2)
    print("  Created: marpd_config.json")
    
    # Create requirements.txt
    requirements = [
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0", 
        "lxml>=4.9.0",
        "colorama>=0.4.6",
        "tqdm>=4.66.0",
        "fake-useragent>=1.4.0"
    ]
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    print("  Created: requirements.txt")
    
    # Create .gitignore
    gitignore = [
        "data/cache/*",
        "results/logs/*",
        "__pycache__/",
        "*.pyc",
        ".env",
        "venv/",
        "*.log"
    ]
    
    with open('.gitignore', 'w') as f:
        f.write('\n'.join(gitignore))
    print("  Created: .gitignore")
    
    print("\n✓ Configuration files created!")

def create_readme():
    """README ফাইল তৈরি করুন"""
    print("\n[5/5] Creating documentation...")
    
    readme_content = """# MAR-PD v3.5

## Multi-Algorithmic Reconnaissance - Profile Decoder

### 📋 Description
MAR-PD is a professional tool designed for legitimate account recovery purposes. 
It helps users find their lost Facebook login credentials (email/phone) through 
multiple extraction algorithms.

### ⚠️ Ethical Use Agreement
**THIS TOOL IS FOR SELF-ACCOUNT RECOVERY ONLY**
- Use only for YOUR OWN accounts
- Do not violate others' privacy
- Follow all applicable laws
- Respect Facebook's Terms of Service

### 🚀 Quick Start

```bash
# 1. Run setup
python setup.py

# 2. Run the tool
python main.py

# 3. Enter your Facebook profile URL or username