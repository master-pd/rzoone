#!/usr/bin/env python3
"""
MAR-PD Runner Script
Simplified version for easy execution
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    # Check if setup is needed
    if not os.path.exists('requirements.txt'):
        print("Running setup...")
        from setup import main as setup_main
        setup_main()
    
    # Run main application
    main()