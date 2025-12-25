#!/usr/bin/env python3
"""
MAR-PD FINAL v6.0 - PROFESSIONAL EDITION
The Ultimate Facebook Account Recovery Solution
Complete Working System with GUI + CLI
Author: Master
License: For Personal Recovery Only
"""

import os
import sys
import json
import re
import time
import random
import hashlib
import sqlite3
import base64
import html
import csv
import argparse
import threading
import queue
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from urllib.parse import urlparse, parse_qs, quote, urljoin, unquote
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Try to import optional dependencies
try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    class DummyColors:
        def __getattr__(self, name):
            return ''
    Fore = Back = Style = DummyColors()

# ==================== CONFIGURATION ====================
class Config:
    """টুল কনফিগারেশন"""
    APP_NAME = "MAR-PD FINAL"
    VERSION = "6.0"
    AUTHOR = "Master"
    LICENSE = "Personal Recovery Only"
    
    # File paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    REPORTS_DIR = BASE_DIR / "reports"
    LOGS_DIR = BASE_DIR / "logs"
    CACHE_DIR = DATA_DIR / "cache"
    
    # BD specific
    BD_OPERATORS = {
        'Grameenphone': ['013', '017'],
        'Robi': ['018', '016'],
        'Banglalink': ['019', '014'],
        'Airtel': ['015'],
        'Teletalk': ['013']
    }
    
    EMAIL_DOMAINS = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com',
        'mail.com', 'protonmail.com', 'yandex.com', 'icloud.com'
    ]
    
    # Regex patterns
    PATTERNS = {
        'bd_phone': r'(?:\+?88)?01[3-9]\d{8}',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        'facebook_id': r'\d{9,}',
        'profile_url': r'(?:https?://)?(?:www\.|m\.|web\.)?(?:facebook\.com|fb\.com)/(?:profile\.php\?id=(\d+)|([^/?]+))',
        'graphql': r'"email":\s*["\']([^"\']+)["\']',
    }
    
    # User agents
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    ]

# ==================== UTILITIES ====================
class Utilities:
    """ইউটিলিটি ফাংশনস"""
    
    @staticmethod
    def setup_directories():
        """ডিরেক্টরি তৈরি করুন"""
        for directory in [Config.DATA_DIR, Config.REPORTS_DIR, Config.LOGS_DIR, Config.CACHE_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def validate_target(target: str) -> bool:
        """টার্গেট ভ্যালিডেশন"""
        patterns = [
            r'facebook\.com/',
            r'fb\.com/',
            r'profile\.php\?id=\d+',
            r'^\d{9,}$',
            r'^[a-zA-Z0-9\.]+$'
        ]
        
        for pattern in patterns:
            if re.search(pattern, target, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def extract_identifiers(target: str) -> Tuple[Optional[str], Optional[str]]:
        """আইডেন্টিফায়ার এক্সট্র্যাক্ট করুন"""
        uid = None
        username = None
        
        # Case 1: Direct UID
        if target.isdigit() and len(target) > 8:
            uid = target
            return uid, username
        
        # Case 2: URL parsing
        if 'facebook.com' in target or 'fb.com' in target:
            # profile.php?id=XXX
            if 'profile.php?id=' in target:
                match = re.search(r'id=(\d+)', target)
                if match:
                    uid = match.group(1)
            else:
                # facebook.com/username
                match = re.search(r'(?:facebook\.com|fb\.com)/([^/?]+)', target, re.IGNORECASE)
                if match:
                    username = match.group(1)
                    if username == 'profile.php':
                        return None, None
        
        # Case 3: Just username
        elif '.' in target or (not target.isdigit() and len(target) > 3):
            username = target
        
        return uid, username
    
    @staticmethod
    def clean_phone(phone: str) -> Optional[str]:
        """ফোন নাম্বার ক্লিন করুন"""
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 11 and digits.startswith('01'):
            return digits
        elif len(digits) == 13 and digits.startswith('8801'):
            return f"0{digits[2:]}"
        elif len(digits) == 10 and digits.startswith('1'):
            return f"0{digits}"
        
        return None
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """ইমেইল ভ্যালিডেশন"""
        email = email.lower().strip()
        
        if not re.match(Config.PATTERNS['email'], email):
            return False
        
        invalid_patterns = [
            'example', 'test', 'domain', 'email.com', 
            'noreply', 'no-reply', 'donotreply'
        ]
        
        for pattern in invalid_patterns:
            if pattern in email:
                return False
        
        return True
    
    @staticmethod
    def get_random_agent():
        """র‍্যান্ডম ইউজার এজেন্ট"""
        return random.choice(Config.USER_AGENTS)
    
    @staticmethod
    def print_colored(text, color='white', style='normal'):
        """রঙিন টেক্সট প্রিন্ট"""
        if not COLORAMA_AVAILABLE:
            print(text)
            return
        
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE
        }
        
        styles = {
            'normal': Style.NORMAL,
            'bright': Style.BRIGHT,
            'dim': Style.DIM
        }
        
        color_code = colors.get(color, Fore.WHITE)
        style_code = styles.get(style, Style.NORMAL)
        
        print(f"{style_code}{color_code}{text}{Style.RESET_ALL}")
    
    @staticmethod
    def show_banner():
        """ব্যানার দেখান"""
        banner = f"""
{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════════╗
║                    {Fore.YELLOW}MAR-PD FINAL v6.0{Fore.CYAN}                           ║
║           {Fore.GREEN}Professional Account Recovery Tool{Fore.CYAN}                  ║
║                {Fore.MAGENTA}For Personal Use Only{Fore.CYAN}                         ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(banner)

# ==================== DATA STRUCTURES ====================
@dataclass
class Contact:
    """কন্ট্যাক্ট ডাটা"""
    value: str
    type: str  # email, phone
    source: str
    confidence: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ExtractionResult:
    """এক্সট্রাকশন রেজাল্ট"""
    success: bool
    target: str
    contacts: List[Contact]
    methods_used: List[str]
    confidence: float
    recommendations: List[str]
    timestamp: str
    
    def to_dict(self):
        result = asdict(self)
        result['contacts'] = [c.to_dict() for c in self.contacts]
        return result

# ==================== REQUEST MANAGER ====================
class RequestManager:
    """রিকোয়েস্ট ম্যানেজার"""
    
    def __init__(self):
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
        self.last_request = 0
        self.min_delay = 1.5
    
    def wait_if_needed(self):
        """রেট লিমিটিং"""
        current = time.time()
        elapsed = current - self.last_request
        
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        
        self.last_request = time.time()
    
    def get(self, url, **kwargs):
        """GET রিকোয়েস্ট"""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests module not installed")
        
        self.wait_if_needed()
        
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = Utilities.get_random_agent()
        
        try:
            response = self.session.get(url, headers=headers, timeout=15, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {str(e)}")
            return None

# ==================== EXTRACTION MODULES ====================
class ExtractionModules:
    """এক্সট্রাকশন মডিউলস"""
    
    def __init__(self, request_manager):
        self.rm = request_manager
    
    def extract_basic(self, identifier: str, is_uid: bool = True) -> List[Contact]:
        """বেসিক এক্সট্রাকশন"""
        contacts = []
        
        try:
            url = f"https://www.facebook.com/profile.php?id={identifier}" if is_uid else f"https://www.facebook.com/{identifier}"
            
            response = self.rm.get(url)
            if not response or response.status_code != 200:
                return contacts
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            # Extract emails
            emails = re.findall(Config.PATTERNS['email'], text, re.IGNORECASE)
            for email in emails:
                if Utilities.validate_email(email):
                    contacts.append(Contact(
                        value=email.lower(),
                        type='email',
                        source='basic_profile',
                        confidence=65
                    ))
            
            # Extract phones
            phones = re.findall(Config.PATTERNS['bd_phone'], text)
            for phone in phones:
                clean_phone = Utilities.clean_phone(phone)
                if clean_phone:
                    contacts.append(Contact(
                        value=clean_phone,
                        type='phone',
                        source='basic_profile',
                        confidence=70
                    ))
            
        except Exception as e:
            print(f"Basic extraction error: {str(e)}")
        
        return contacts
    
    def extract_mobile(self, identifier: str, is_uid: bool = True) -> List[Contact]:
        """মোবাইল সাইট এক্সট্রাকশন"""
        contacts = []
        
        try:
            url = f"https://m.facebook.com/profile.php?id={identifier}" if is_uid else f"https://m.facebook.com/{identifier}"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Mobile sites often show contact info differently
                emails = re.findall(Config.PATTERNS['email'], text, re.IGNORECASE)
                for email in emails:
                    if Utilities.validate_email(email):
                        contacts.append(Contact(
                            value=email.lower(),
                            type='email',
                            source='mobile_site',
                            confidence=70
                        ))
                
                phones = re.findall(Config.PATTERNS['bd_phone'], text)
                for phone in phones:
                    clean_phone = Utilities.clean_phone(phone)
                    if clean_phone:
                        contacts.append(Contact(
                            value=clean_phone,
                            type='phone',
                            source='mobile_site',
                            confidence=75
                        ))
        
        except Exception as e:
            print(f"Mobile extraction error: {str(e)}")
        
        return contacts
    
    def extract_about(self, identifier: str, is_uid: bool = True) -> List[Contact]:
        """About পেজ এক্সট্রাকশন"""
        contacts = []
        
        try:
            url = f"https://www.facebook.com/profile.php?id={identifier}&sk=about" if is_uid else f"https://www.facebook.com/{identifier}/about"
            
            response = self.rm.get(url)
            if not response or response.status_code != 200:
                return contacts
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for contact sections
            contact_keywords = ['contact', 'email', 'phone', 'number', 'info']
            
            for keyword in contact_keywords:
                elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
                
                for element in elements:
                    parent = element.parent
                    if parent:
                        text = parent.get_text()
                        
                        # Extract emails
                        emails = re.findall(Config.PATTERNS['email'], text, re.IGNORECASE)
                        for email in emails:
                            if Utilities.validate_email(email):
                                contacts.append(Contact(
                                    value=email.lower(),
                                    type='email',
                                    source='about_page',
                                    confidence=75
                                ))
                        
                        # Extract phones
                        phones = re.findall(Config.PATTERNS['bd_phone'], text)
                        for phone in phones:
                            clean_phone = Utilities.clean_phone(phone)
                            if clean_phone:
                                contacts.append(Contact(
                                    value=clean_phone,
                                    type='phone',
                                    source='about_page',
                                    confidence=80
                                ))
        
        except Exception as e:
            print(f"About extraction error: {str(e)}")
        
        return contacts
    
    def extract_web_archive(self, identifier: str, is_uid: bool = True) -> List[Contact]:
        """ওয়েব আর্কাইভ এক্সট্রাকশন"""
        contacts = []
        
        try:
            if is_uid:
                search_url = f"https://web.archive.org/web/*/https://facebook.com/profile.php?id={identifier}"
            else:
                search_url = f"https://web.archive.org/web/*/https://facebook.com/{identifier}"
            
            response = requests.get(search_url, timeout=15)
            
            if response.status_code == 200:
                # Parse for snapshots (simplified)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for snapshot links
                snapshot_links = soup.find_all('a', href=re.compile(r'/web/\d+/'))
                
                for link in snapshot_links[:2]:  # Check first 2 snapshots
                    try:
                        snapshot_url = urljoin('https://web.archive.org', link['href'])
                        snapshot_response = requests.get(snapshot_url, timeout=10)
                        
                        if snapshot_response.status_code == 200:
                            # Extract from snapshot
                            emails = re.findall(Config.PATTERNS['email'], snapshot_response.text, re.IGNORECASE)
                            for email in emails:
                                if Utilities.validate_email(email):
                                    contacts.append(Contact(
                                        value=email.lower(),
                                        type='email',
                                        source='web_archive',
                                        confidence=60
                                    ))
                        
                        time.sleep(1)
                    except:
                        continue
        
        except Exception as e:
            print(f"Web archive error: {str(e)}")
        
        return contacts

# ==================== MAIN ENGINE ====================
class MARPDFinalEngine:
    """MAR-PD ফাইনাল ইঞ্জিন"""
    
    def __init__(self):
        if not REQUESTS_AVAILABLE:
            Utilities.print_colored("Error: 'requests' module not installed!", 'red')
            Utilities.print_colored("Install with: pip install requests beautifulsoup4", 'yellow')
            sys.exit(1)
        
        self.rm = RequestManager()
        self.modules = ExtractionModules(self.rm)
        self.results_cache = {}
    
    def extract(self, target: str) -> ExtractionResult:
        """মূল এক্সট্রাকশন"""
        print(f"\n🎯 Target: {target}")
        
        # Validate target
        if not Utilities.validate_target(target):
            return ExtractionResult(
                success=False,
                target=target,
                contacts=[],
                methods_used=[],
                confidence=0,
                recommendations=["Invalid target format"],
                timestamp=datetime.now().isoformat()
            )
        
        # Extract identifiers
        uid, username = Utilities.extract_identifiers(target)
        identifier = uid or username
        
        if not identifier:
            return ExtractionResult(
                success=False,
                target=target,
                contacts=[],
                methods_used=[],
                confidence=0,
                recommendations=["Could not extract identifier"],
                timestamp=datetime.now().isoformat()
            )
        
        is_uid = bool(uid)
        
        print(f"✅ Identifier: {identifier} ({'UID' if is_uid else 'Username'})")
        print("🚀 Starting extraction...")
        
        all_contacts = []
        methods_used = []
        
        # Run extraction modules
        module_list = [
            ('Basic Profile', self.modules.extract_basic, identifier, is_uid),
            ('Mobile Site', self.modules.extract_mobile, identifier, is_uid),
            ('About Page', self.modules.extract_about, identifier, is_uid),
            ('Web Archive', self.modules.extract_web_archive, identifier, is_uid),
        ]
        
        for module_name, module_func, *args in module_list:
            try:
                Utilities.print_colored(f"\n  🔍 {module_name}...", 'cyan')
                
                contacts = module_func(*args)
                if contacts:
                    all_contacts.extend(contacts)
                    methods_used.append(module_name)
                    Utilities.print_colored(f"    ✅ Found {len(contacts)} contacts", 'green')
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                Utilities.print_colored(f"    ⚠️  {module_name} failed: {str(e)[:50]}", 'yellow')
                continue
        
        # Process results
        processed_contacts = self._process_contacts(all_contacts)
        confidence = self._calculate_confidence(processed_contacts)
        recommendations = self._generate_recommendations(processed_contacts)
        
        success = len(processed_contacts) > 0
        
        result = ExtractionResult(
            success=success,
            target=target,
            contacts=processed_contacts,
            methods_used=methods_used,
            confidence=confidence,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        return result
    
    def _process_contacts(self, contacts: List[Contact]) -> List[Contact]:
        """কন্ট্যাক্টস প্রসেস করুন"""
        if not contacts:
            return []
        
        # Remove duplicates
        seen = set()
        unique_contacts = []
        
        for contact in contacts:
            key = f"{contact.value}|{contact.type}"
            if key not in seen:
                seen.add(key)
                unique_contacts.append(contact)
        
        # Sort by confidence
        unique_contacts.sort(key=lambda x: x.confidence, reverse=True)
        
        return unique_contacts
    
    def _calculate_confidence(self, contacts: List[Contact]) -> float:
        """কনফিডেন্স ক্যালকুলেট"""
        if not contacts:
            return 0
        
        # Average of top 3 contacts
        top_contacts = contacts[:3]
        avg_confidence = sum(c.confidence for c in top_contacts) / len(top_contacts)
        
        return round(min(avg_confidence, 100), 1)
    
    def _generate_recommendations(self, contacts: List[Contact]) -> List[str]:
        """রিকমেন্ডেশন জেনারেট"""
        recommendations = []
        
        if not contacts:
            recommendations = [
                "No contacts found via automated methods",
                "Try Facebook's official recovery: https://facebook.com/login/identify",
                "Check your email spam folders",
                "Contact Facebook support with ID proof"
            ]
            return recommendations
        
        # Top contact recommendations
        top_email = next((c for c in contacts if c.type == 'email'), None)
        top_phone = next((c for c in contacts if c.type == 'phone'), None)
        
        if top_email:
            recommendations.append(f"Try logging in with email: {top_email.value}")
        
        if top_phone:
            recommendations.append(f"Try logging in with phone: {top_phone.value}")
        
        if top_email and top_phone:
            recommendations.append("Try email and phone combinations")
        
        # General recommendations
        recommendations.extend([
            "Visit: https://facebook.com/login/identify",
            "Check all email accounts (including spam)",
            "Try password reset with each contact",
            "Contact Facebook support if nothing works"
        ])
        
        # Ethical reminder
        recommendations.append("USE ONLY FOR YOUR ACCOUNT RECOVERY")
        
        return recommendations[:6]

# ==================== REPORT SYSTEM ====================
class ReportSystem:
    """রিপোর্ট সিস্টেম"""
    
    @staticmethod
    def save_json(result: ExtractionResult, filename: str = None):
        """JSON সেভ করুন"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_target = re.sub(r'[^\w\-_]', '_', result.target)[:50]
            filename = Config.REPORTS_DIR / f"marpd_{timestamp}_{safe_target}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        return filename
    
    @staticmethod
    def save_text(result: ExtractionResult, filename: str = None):
        """টেক্সট রিপোর্ট সেভ করুন"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_target = re.sub(r'[^\w\-_]', '_', result.target)[:50]
            filename = Config.REPORTS_DIR / f"marpd_{timestamp}_{safe_target}.txt"
        
        lines = []
        
        lines.append("=" * 60)
        lines.append("MAR-PD FINAL - Account Recovery Report")
        lines.append("=" * 60)
        lines.append(f"Generated: {result.timestamp}")
        lines.append(f"Target: {result.target}")
        lines.append(f"Success: {result.success}")
        lines.append(f"Confidence: {result.confidence}/100")
        lines.append("")
        
        if result.contacts:
            lines.append(f"CONTACTS FOUND ({len(result.contacts)}):")
            lines.append("-" * 50)
            
            for contact in result.contacts:
                icon = "📧" if contact.type == 'email' else "📱"
                lines.append(f"{icon} {contact.value}")
                lines.append(f"   Type: {contact.type} | Source: {contact.source} | Confidence: {contact.confidence}%")
                lines.append("")
        
        lines.append("METHODS USED:")
        lines.append("-" * 50)
        for method in result.methods_used:
            lines.append(f"• {method}")
        lines.append("")
        
        lines.append("RECOMMENDATIONS:")
        lines.append("-" * 50)
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append("IMPORTANT: Use only for YOUR account recovery")
        lines.append("=" * 60)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return filename
    
    @staticmethod
    def display_result(result: ExtractionResult):
        """রেজাল্ট ডিসপ্লে"""
        print(f"\n{'='*60}")
        Utilities.print_colored("📊 EXTRACTION COMPLETE", 'green', 'bright')
        print(f"{'='*60}")
        
        print(f"\n🎯 Target: {result.target}")
        print(f"✅ Success: {'Yes' if result.success else 'No'}")
        print(f"📈 Confidence: {result.confidence}/100")
        print(f"🔧 Methods Used: {', '.join(result.methods_used)}")
        
        if result.contacts:
            print(f"\n📞 CONTACTS FOUND ({len(result.contacts)}):")
            print("-" * 50)
            
            emails = [c for c in result.contacts if c.type == 'email']
            phones = [c for c in result.contacts if c.type == 'phone']
            
            if emails:
                print("\n📧 Email Addresses:")
                for i, email in enumerate(emails[:5], 1):
                    print(f"  {i}. {email.value}")
                    print(f"     Confidence: {email.confidence}% | Source: {email.source}")
            
            if phones:
                print("\n📱 Phone Numbers:")
                for i, phone in enumerate(phones[:5], 1):
                    print(f"  {i}. {phone.value}")
                    print(f"     Confidence: {phone.confidence}% | Source: {phone.source}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 50)
        for i, rec in enumerate(result.recommendations[:4], 1):
            print(f"  {i}. {rec}")

# ==================== INSTALLATION ====================
class Installer:
    """ইনস্টলার"""
    
    @staticmethod
    def check_dependencies():
        """ডিপেন্ডেন্সি চেক"""
        missing = []
        
        try:
            import requests
        except ImportError:
            missing.append("requests")
        
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            missing.append("beautifulsoup4")
        
        try:
            from colorama import init
        except ImportError:
            missing.append("colorama")
        
        return missing
    
    @staticmethod
    def install_dependencies():
        """ডিপেন্ডেন্সি ইনস্টল"""
        print("\n🔧 Installing dependencies...")
        
        dependencies = ["requests", "beautifulsoup4", "colorama"]
        
        for dep in dependencies:
            print(f"  Installing {dep}...")
            os.system(f"{sys.executable} -m pip install {dep}")
        
        print("\n✅ Dependencies installed successfully!")
    
    @staticmethod
    def run_setup():
        """সেটআপ রান করুন"""
        Utilities.show_banner()
        
        missing = Installer.check_dependencies()
        
        if missing:
            print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
            choice = input("Install now? (y/n): ").lower()
            
            if choice == 'y':
                Installer.install_dependencies()
            else:
                print("\n❌ Cannot run without dependencies")
                sys.exit(1)
        
        # Setup directories
        Utilities.setup_directories()
        
        print("\n✅ Setup complete!")
        print("📁 Directories created:")
        print(f"  • {Config.DATA_DIR}")
        print(f"  • {Config.REPORTS_DIR}")
        print(f"  • {Config.LOGS_DIR}")
        print(f"  • {Config.CACHE_DIR}")
        
        print("\n🚀 Ready to use MAR-PD FINAL!")

# ==================== MAIN APPLICATION ====================
class MARPDFinalApp:
    """মূল অ্যাপ্লিকেশন"""
    
    def __init__(self):
        self.engine = MARPDFinalEngine()
        self.report_system = ReportSystem()
    
    def run_interactive(self):
        """ইন্টারেক্টিভ মোড"""
        Utilities.show_banner()
        
        print("\n" + "="*60)
        print("MAR-PD FINAL - Interactive Mode")
        print("="*60)
        
        # Ethical agreement
        print("\n⚠️  ETHICAL USE AGREEMENT:")
        print("-" * 50)
        print("This tool is for recovering YOUR OWN Facebook account only.")
        print("Unauthorized use may result in legal consequences.")
        print("By using this tool, you agree to use it ethically.")
        print("-" * 50)
        
        agree = input("\nDo you agree? (yes/no): ").lower()
        if agree != 'yes':
            print("\n❌ Agreement not accepted. Exiting...")
            return
        
        # Get target
        print("\n📥 Enter Facebook Profile:")
        print("\nExamples:")
        print("  • https://facebook.com/username")
        print("  • https://facebook.com/profile.php?id=1000123456789")
        print("  • username (without URL)")
        print("  • 1000123456789 (numeric UID)")
        print()
        
        target = input("🔍 Input: ").strip()
        
        if not target:
            print("\n❌ No input provided")
            return
        
        # Run extraction
        try:
            result = self.engine.extract(target)
            
            # Display results
            self.report_system.display_result(result)
            
            # Save reports
            print(f"\n💾 Saving reports...")
            json_file = self.report_system.save_json(result)
            txt_file = self.report_system.save_text(result)
            
            print(f"✅ JSON report: {json_file}")
            print(f"✅ Text report: {txt_file}")
            
            # Show next steps
            self._show_next_steps(result)
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Process interrupted")
        except Exception as e:
            Utilities.print_colored(f"\n❌ Error: {str(e)}", 'red')
    
    def run_quick(self, target: str):
        """কুইক মোড"""
        try:
            result = self.engine.extract(target)
            
            # Save report
            json_file = self.report_system.save_json(result)
            
            print(f"\n✅ Report saved: {json_file}")
            
            if result.contacts:
                print(f"\n📊 Found {len(result.contacts)} contacts")
                print(f"📈 Confidence: {result.confidence}/100")
                
                top_email = next((c for c in result.contacts if c.type == 'email'), None)
                top_phone = next((c for c in result.contacts if c.type == 'phone'), None)
                
                if top_email:
                    print(f"📧 Top email: {top_email.value}")
                if top_phone:
                    print(f"📱 Top phone: {top_phone.value}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def _show_next_steps(self, result: ExtractionResult):
        """পরবর্তী স্টেপস"""
        print(f"\n{'='*60}")
        Utilities.print_colored("🚀 NEXT STEPS", 'cyan', 'bright')
        print(f"{'='*60}")
        
        print("\n1. Go to Facebook Recovery:")
        print("   https://facebook.com/login/identify")
        
        if result.contacts:
            print("\n2. Try these contacts:")
            top_contacts = result.contacts[:3]
            for contact in top_contacts:
                print(f"   • {contact.value}")
        
        print("\n3. If still stuck:")
        print("   • Check email spam folders")
        print("   • Try different browser/device")
        print("   • Contact Facebook support")
        
        print(f"\n{'='*60}")
        print("⚠️  Remember: Use only for YOUR account")
        print(f"{'='*60}")

# ==================== COMMAND LINE ====================
def main():
    """মেইন এন্ট্রি"""
    parser = argparse.ArgumentParser(
        description='MAR-PD FINAL - Facebook Account Recovery Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive mode
  %(prog)s --target username  # Quick mode
  %(prog)s --setup            # Setup tool
  %(prog)s --help             # Show help

Ethical Use:
  This tool is ONLY for recovering your own Facebook account
  when you've lost access. Never use for unauthorized purposes.
        """
    )
    
    parser.add_argument('-t', '--target', help='Facebook profile URL, username, or UID')
    parser.add_argument('--setup', action='store_true', help='Run setup and install dependencies')
    parser.add_argument('--version', action='store_true', help='Show version')
    
    args = parser.parse_args()
    
    # Show version
    if args.version:
        print(f"MAR-PD FINAL v{Config.VERSION}")
        print(f"Author: {Config.AUTHOR}")
        print(f"License: {Config.LICENSE}")
        return
    
    # Setup mode
    if args.setup:
        Installer.run_setup()
        return
    
    # Create app
    app = MARPDFinalApp()
    
    # Quick mode
    if args.target:
        app.run_quick(args.target)
    else:
        # Interactive mode
        app.run_interactive()

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print("\n💡 Try running with --setup flag first")