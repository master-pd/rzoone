"""
Configuration File
"""

CONFIG = {
    "app": {
        "name": "MAR-PD ",
        "version": "3.5",
        "author": "MASTER (RANA)"
    },
    
    "settings": {
        "request_timeout": 30,
        "delay_between_requests": 1.5,
        "max_retries": 3,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    
    "patterns": {
        "bd_phone": r'(?:\+?88)?01[3-9]\d{8}',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    },
    
    "output": {
        "save_json": True,
        "save_txt": True,
        "save_logs": True
    }
}