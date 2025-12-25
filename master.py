#!/usr/bin/env python3
"""
MAR-PD ULTIMATE FINAL v7.0
Complete Facebook Account Recovery Solution
Professional Grade with All Features
Author: Master
For: Personal Account Recovery Only
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
import webbrowser
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from urllib.parse import urlparse, parse_qs, quote, urljoin, unquote
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import platform
import subprocess

# ==================== DEPENDENCY CHECK ====================
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
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("💡 Install with: pip install requests beautifulsoup4")
        return False
    
    return True

# Import after check
import requests
from bs4 import BeautifulSoup

# ==================== ADVANCED CONFIGURATION ====================
class AdvancedConfig:
    """এডভান্সড কনফিগারেশন"""
    APP_NAME = "MAR-PD ULTIMATE FINAL"
    VERSION = "7.0"
    AUTHOR = "Master"
    LICENSE = "Personal Account Recovery Only"
    
    # Paths
    BASE_DIR = Path.home() / ".marpd" if platform.system() != "Windows" else Path.home() / "AppData" / "Local" / "MARPD"
    DATA_DIR = BASE_DIR / "data"
    REPORTS_DIR = BASE_DIR / "reports"
    LOGS_DIR = BASE_DIR / "logs"
    CACHE_DIR = BASE_DIR / "cache"
    DB_FILE = DATA_DIR / "marpd.db"
    
    # Bangladesh specific
    BD_OPERATORS = {
        'Grameenphone': ['013', '017'],
        'Robi': ['018', '016'],
        'Banglalink': ['019', '014'],
        'Airtel': ['015'],
        'Teletalk': ['013']
    }
    
    EMAIL_DOMAINS = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com',
        'mail.com', 'protonmail.com', 'yandex.com', 'icloud.com', 'zoho.com'
    ]
    
    # Advanced patterns
    PATTERNS = {
        'bd_phone': r'(?:\+?88)?01[3-9]\d{8}',
        'international_phone': r'\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,9}',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        'facebook_id': r'\d{9,15}',
        'username': r'[a-zA-Z0-9.]{5,50}',
        'profile_url': r'(?:https?://)?(?:www\.|m\.|web\.|touch\.)?(?:facebook\.com|fb\.com|fb\.me)/(?:profile\.php\?id=(\d+)|([^/?]+))',
        'graphql_email': r'["\'](email|email_address)["\']\s*:\s*["\']([^"\']+)["\']',
        'json_data': r'\{.*?"email".*?\}',
    }
    
    # User agents rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
    ]
    
    # API endpoints (for reference)
    ENDPOINTS = {
        'graphql': 'https://www.facebook.com/api/graphql/',
        'graphql_batch': 'https://www.facebook.com/api/graphqlbatch/',
        'profile': 'https://www.facebook.com/{}',
        'profile_mobile': 'https://m.facebook.com/{}',
        'profile_basic': 'https://mbasic.facebook.com/{}',
        'about': 'https://www.facebook.com/{}/about',
        'friends': 'https://www.facebook.com/{}/friends',
        'photos': 'https://www.facebook.com/{}/photos',
    }
    
    # Request settings
    REQUEST_SETTINGS = {
        'timeout': 25,
        'max_retries': 3,
        'delay_between': 1.2,
        'max_redirects': 5,
    }

# ==================== ADVANCED UTILITIES ====================
class AdvancedUtilities:
    """এডভান্সড ইউটিলিটিস"""
    
    @staticmethod
    def setup_environment():
        """এনভায়রনমেন্ট সেটআপ"""
        for directory in [AdvancedConfig.DATA_DIR, AdvancedConfig.REPORTS_DIR, 
                         AdvancedConfig.LOGS_DIR, AdvancedConfig.CACHE_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Setup database
        AdvancedUtilities._setup_database()
    
    @staticmethod
    def _setup_database():
        """ডাটাবেস সেটআপ"""
        conn = sqlite3.connect(AdvancedConfig.DB_FILE)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extraction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                contacts_found INTEGER,
                confidence_score REAL,
                extraction_time TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT NOT NULL,
                contact_type TEXT NOT NULL,
                contact_value TEXT NOT NULL,
                source TEXT,
                confidence INTEGER,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(identifier, contact_type, contact_value)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def validate_and_parse_target(target: str) -> Dict:
        """টার্গেট ভ্যালিডেশন এবং পার্সিং"""
        result = {
            'valid': False,
            'type': None,
            'uid': None,
            'username': None,
            'url': None,
            'error': None
        }
        
        if not target or not isinstance(target, str):
            result['error'] = "Empty or invalid input"
            return result
        
        target = target.strip()
        
        # Case 1: Direct numeric ID
        if target.isdigit() and 9 <= len(target) <= 15:
            result.update({
                'valid': True,
                'type': 'uid',
                'uid': target,
                'url': f"https://facebook.com/profile.php?id={target}"
            })
            return result
        
        # Case 2: Facebook URL
        facebook_patterns = [
            r'(?:https?://)?(?:www\.|m\.|web\.)?(?:facebook\.com|fb\.com)/profile\.php\?id=(\d+)',
            r'(?:https?://)?(?:www\.|m\.|web\.)?(?:facebook\.com|fb\.com)/([a-zA-Z0-9.]+)',
        ]
        
        for pattern in facebook_patterns:
            match = re.match(pattern, target, re.IGNORECASE)
            if match:
                if 'profile.php' in target:
                    result.update({
                        'valid': True,
                        'type': 'uid',
                        'uid': match.group(1),
                        'url': f"https://facebook.com/profile.php?id={match.group(1)}"
                    })
                else:
                    username = match.group(1)
                    if username != 'profile.php':  # Skip invalid matches
                        result.update({
                            'valid': True,
                            'type': 'username',
                            'username': username,
                            'url': f"https://facebook.com/{username}"
                        })
                return result
        
        # Case 3: Just username (simple validation)
        if re.match(r'^[a-zA-Z0-9.]{5,50}$', target):
            result.update({
                'valid': True,
                'type': 'username',
                'username': target,
                'url': f"https://facebook.com/{target}"
            })
            return result
        
        result['error'] = "Invalid Facebook profile URL, username, or UID"
        return result
    
    @staticmethod
    def clean_and_validate_email(email: str) -> Optional[str]:
        """ইমেইল ক্লিন এবং ভ্যালিডেশন"""
        if not email or not isinstance(email, str):
            return None
        
        email = email.strip().lower()
        
        # Basic email validation
        if not re.match(AdvancedConfig.PATTERNS['email'], email):
            return None
        
        # Common invalid patterns
        invalid_patterns = [
            'example.com', 'test.com', 'domain.com', 'email.com',
            'mailinator.com', 'tempmail.com', 'guerrillamail.com',
            '10minutemail.com', 'throwawaymail.com'
        ]
        
        domain = email.split('@')[1] if '@' in email else ''
        
        for pattern in invalid_patterns:
            if pattern in domain:
                return None
        
        # Valid domain check
        if domain in AdvancedConfig.EMAIL_DOMAINS:
            return email
        
        # Also allow other valid-looking domains
        if '.' in domain and len(domain) > 3 and len(domain.split('.')[-1]) >= 2:
            return email
        
        return None
    
    @staticmethod
    def clean_and_validate_phone(phone: str) -> Optional[str]:
        """ফোন নাম্বার ক্লিন এবং ভ্যালিডেশন"""
        if not phone or not isinstance(phone, str):
            return None
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Bangladesh mobile numbers
        if len(digits) == 11 and digits.startswith('01'):
            # Check if it's a valid BD operator
            prefix = digits[:3]
            for operator, prefixes in AdvancedConfig.BD_OPERATORS.items():
                if prefix in prefixes:
                    return digits
        
        # International format for BD
        elif len(digits) == 13 and digits.startswith('8801'):
            prefix = digits[2:5]  # 8801XXX -> 01XXX
            for operator, prefixes in AdvancedConfig.BD_OPERATORS.items():
                if f"0{prefix}"[1:] in prefixes:  # Adjust for comparison
                    return f"0{digits[2:]}"
        
        # 10 digit starting with 1 (assume missing leading 0)
        elif len(digits) == 10 and digits.startswith('1'):
            potential = f"0{digits}"
            prefix = potential[:3]
            for operator, prefixes in AdvancedConfig.BD_OPERATORS.items():
                if prefix in prefixes:
                    return potential
        
        return None
    
    @staticmethod
    def generate_report_filename(target_info: Dict, extension: str = 'json') -> str:
        """রিপোর্ট ফাইলনেম জেনারেট"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if target_info['type'] == 'uid':
            identifier = target_info['uid']
        else:
            identifier = target_info['username']
        
        # Safe filename
        safe_id = re.sub(r'[^\w\-]', '_', identifier)[:50]
        
        return f"marpd_{timestamp}_{safe_id}.{extension}"
    
    @staticmethod
    def get_random_user_agent() -> str:
        """র‍্যান্ডম ইউজার এজেন্ট"""
        return random.choice(AdvancedConfig.USER_AGENTS)
    
    @staticmethod
    def calculate_confidence_score(contacts: List[Dict]) -> float:
        """কনফিডেন্স স্কোর ক্যালকুলেট"""
        if not contacts:
            return 0.0
        
        total_score = 0
        weighted_sum = 0
        
        for contact in contacts:
            weight = contact.get('confidence', 50)
            frequency = contact.get('frequency', 1)
            
            # Higher frequency = higher weight
            frequency_weight = min(frequency, 5) / 5  # Normalize to 0-1
            
            # Source weight adjustment
            source = contact.get('source', '')
            source_weight = 1.0
            
            if 'graphql' in source.lower():
                source_weight = 1.3
            elif 'mobile' in source.lower():
                source_weight = 1.1
            elif 'about' in source.lower():
                source_weight = 1.2
            
            final_weight = weight * frequency_weight * source_weight
            weighted_sum += final_weight
            total_score += weight
        
        if total_score == 0:
            return 0.0
        
        # Normalize to 0-100
        confidence = (weighted_sum / total_score) * 100
        
        return min(100.0, round(confidence, 1))

# ==================== ADVANCED REQUEST MANAGER ====================
class AdvancedRequestManager:
    """এডভান্সড রিকোয়েস্ট ম্যানেজার"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.last_request_time = 0
        self.request_count = 0
        self.max_requests_per_minute = 30
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """সেফ রিকোয়েস্ট"""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Ensure minimum delay
        min_delay = AdvancedConfig.REQUEST_SETTINGS['delay_between']
        if time_since_last < min_delay:
            time.sleep(min_delay - time_since_last)
        
        # Rotate user agent
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = AdvancedUtilities.get_random_user_agent()
        
        # Set default timeout
        kwargs['timeout'] = kwargs.get('timeout', AdvancedConfig.REQUEST_SETTINGS['timeout'])
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, **kwargs)
            else:
                return None
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            # Reset counter every minute
            if self.request_count >= self.max_requests_per_minute:
                time.sleep(60)
                self.request_count = 0
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {url}: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error for {url}: {str(e)}")
            return None
    
    def get_facebook_page(self, identifier: str, page_type: str = 'profile') -> Optional[BeautifulSoup]:
        """ফেসবুক পেজ ফেচ"""
        url_templates = {
            'profile': 'https://www.facebook.com/{}',
            'profile_mobile': 'https://m.facebook.com/{}',
            'profile_basic': 'https://mbasic.facebook.com/{}',
            'about': 'https://www.facebook.com/{}/about',
            'friends': 'https://www.facebook.com/{}/friends',
            'photos': 'https://www.facebook.com/{}/photos',
        }
        
        if page_type not in url_templates:
            return None
        
        url = url_templates[page_type].format(identifier)
        
        response = self.make_request(url)
        if not response or response.status_code != 200:
            return None
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except Exception as e:
            print(f"Failed to parse page: {str(e)}")
            return None

# ==================== ADVANCED EXTRACTION ENGINE ====================
class AdvancedExtractionEngine:
    """এডভান্সড এক্সট্রাকশন ইঞ্জিন"""
    
    def __init__(self):
        self.request_manager = AdvancedRequestManager()
        self.extracted_contacts = []
        self.cache = {}
    
    def extract_all(self, target_info: Dict) -> Dict:
        """সব এক্সট্রাকশন মেথড রান করুন"""
        start_time = time.time()
        
        print(f"\n🚀 Starting advanced extraction for: {target_info.get('url')}")
        
        # Determine identifier
        if target_info['type'] == 'uid':
            identifier = f"profile.php?id={target_info['uid']}"
        else:
            identifier = target_info['username']
        
        all_contacts = []
        methods_used = []
        
        # List of extraction methods
        extraction_methods = [
            ('Basic Profile Analysis', self._extract_basic_profile, identifier),
            ('Mobile Site Scan', self._extract_mobile_site, identifier),
            ('About Page Analysis', self._extract_about_page, identifier),
            ('Advanced HTML Parsing', self._extract_advanced_html, identifier),
            ('Public Info Gathering', self._extract_public_info, identifier),
            ('Backup Sources Check', self._extract_backup_sources, identifier),
        ]
        
        # Run methods in sequence
        for method_name, method_func, method_arg in extraction_methods:
            try:
                print(f"\n  🔍 {method_name}...")
                
                contacts = method_func(method_arg)
                if contacts:
                    all_contacts.extend(contacts)
                    methods_used.append(method_name)
                    print(f"    ✅ Found {len(contacts)} potential contacts")
                
                time.sleep(AdvancedConfig.REQUEST_SETTINGS['delay_between'])
                
            except Exception as e:
                print(f"    ⚠️  {method_name} failed: {str(e)[:50]}")
                continue
        
        # Process and deduplicate contacts
        processed_contacts = self._process_contacts(all_contacts)
        
        # Calculate statistics
        elapsed_time = time.time() - start_time
        confidence_score = AdvancedUtilities.calculate_confidence_score(processed_contacts)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(processed_contacts, target_info)
        
        # Prepare result
        result = {
            'success': len(processed_contacts) > 0,
            'target': target_info['url'],
            'target_info': target_info,
            'contacts': processed_contacts,
            'statistics': {
                'total_contacts': len(processed_contacts),
                'emails': len([c for c in processed_contacts if c['type'] == 'email']),
                'phones': len([c for c in processed_contacts if c['type'] == 'phone']),
                'methods_used': methods_used,
                'confidence_score': confidence_score,
                'extraction_time': round(elapsed_time, 2),
                'sources_count': len(set(c['source'] for c in processed_contacts)),
            },
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
            'session_id': hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
        }
        
        # Save to cache
        self._save_to_cache(identifier, result)
        
        return result
    
    def _extract_basic_profile(self, identifier: str) -> List[Dict]:
        """বেসিক প্রোফাইল এনালাইসিস"""
        contacts = []
        
        try:
            soup = self.request_manager.get_facebook_page(identifier, 'profile')
            if not soup:
                return contacts
            
            # Get all text
            text = soup.get_text()
            
            # Extract emails
            email_matches = re.findall(AdvancedConfig.PATTERNS['email'], text, re.IGNORECASE)
            for email in email_matches:
                clean_email = AdvancedUtilities.clean_and_validate_email(email)
                if clean_email:
                    contacts.append({
                        'value': clean_email,
                        'type': 'email',
                        'source': 'basic_profile',
                        'confidence': 65,
                        'frequency': 1,
                        'context': 'page_text'
                    })
            
            # Extract phones
            phone_matches = re.findall(AdvancedConfig.PATTERNS['bd_phone'], text)
            for phone in phone_matches:
                clean_phone = AdvancedUtilities.clean_and_validate_phone(phone)
                if clean_phone:
                    contacts.append({
                        'value': clean_phone,
                        'type': 'phone',
                        'source': 'basic_profile',
                        'confidence': 70,
                        'frequency': 1,
                        'context': 'page_text'
                    })
            
            # Check meta tags
            for meta in soup.find_all('meta'):
                content = meta.get('content', '')
                if content:
                    # Check for emails in meta
                    meta_emails = re.findall(AdvancedConfig.PATTERNS['email'], content, re.IGNORECASE)
                    for email in meta_emails:
                        clean_email = AdvancedUtilities.clean_and_validate_email(email)
                        if clean_email:
                            contacts.append({
                                'value': clean_email,
                                'type': 'email',
                                'source': 'basic_profile_meta',
                                'confidence': 70,
                                'frequency': 1,
                                'context': f"meta_{meta.get('name', 'unknown')}"
                            })
            
        except Exception as e:
            print(f"Basic profile extraction error: {str(e)}")
        
        return contacts
    
    def _extract_mobile_site(self, identifier: str) -> List[Dict]:
        """মোবাইল সাইট স্ক্যান"""
        contacts = []
        
        try:
            soup = self.request_manager.get_facebook_page(identifier, 'profile_mobile')
            if not soup:
                return contacts
            
            # Mobile sites often have simpler contact info
            text = soup.get_text()
            
            # Check for mailto links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                if 'mailto:' in href:
                    email = href.split('mailto:')[1].split('?')[0]
                    clean_email = AdvancedUtilities.clean_and_validate_email(email)
                    if clean_email:
                        contacts.append({
                            'value': clean_email,
                            'type': 'email',
                            'source': 'mobile_site_mailto',
                            'confidence': 75,
                            'frequency': 1,
                            'context': 'mailto_link'
                        })
                
                elif 'tel:' in href:
                    phone = href.split('tel:')[1]
                    clean_phone = AdvancedUtilities.clean_and_validate_phone(phone)
                    if clean_phone:
                        contacts.append({
                            'value': clean_phone,
                            'type': 'phone',
                            'source': 'mobile_site_tel',
                            'confidence': 80,
                            'frequency': 1,
                            'context': 'tel_link'
                        })
            
            # Extract from text
            emails = re.findall(AdvancedConfig.PATTERNS['email'], text, re.IGNORECASE)
            for email in emails:
                clean_email = AdvancedUtilities.clean_and_validate_email(email)
                if clean_email:
                    contacts.append({
                        'value': clean_email,
                        'type': 'email',
                        'source': 'mobile_site_text',
                        'confidence': 70,
                        'frequency': 1,
                        'context': 'mobile_text'
                    })
            
            phones = re.findall(AdvancedConfig.PATTERNS['bd_phone'], text)
            for phone in phones:
                clean_phone = AdvancedUtilities.clean_and_validate_phone(phone)
                if clean_phone:
                    contacts.append({
                        'value': clean_phone,
                        'type': 'phone',
                        'source': 'mobile_site_text',
                        'confidence': 75,
                        'frequency': 1,
                        'context': 'mobile_text'
                    })
            
        except Exception as e:
            print(f"Mobile site extraction error: {str(e)}")
        
        return contacts
    
    def _extract_about_page(self, identifier: str) -> List[Dict]:
        """About পেজ এনালাইসিস"""
        contacts = []
        
        try:
            soup = self.request_manager.get_facebook_page(identifier, 'about')
            if not soup:
                return contacts
            
            # Look for contact sections
            contact_sections = soup.find_all(['div', 'section'], 
                                            class_=re.compile(r'contact|about|info|details', re.IGNORECASE))
            
            for section in contact_sections:
                text = section.get_text()
                
                # Extract emails
                emails = re.findall(AdvancedConfig.PATTERNS['email'], text, re.IGNORECASE)
                for email in emails:
                    clean_email = AdvancedUtilities.clean_and_validate_email(email)
                    if clean_email:
                        contacts.append({
                            'value': clean_email,
                            'type': 'email',
                            'source': 'about_page',
                            'confidence': 80,
                            'frequency': 1,
                            'context': 'about_section'
                        })
                
                # Extract phones
                phones = re.findall(AdvancedConfig.PATTERNS['bd_phone'], text)
                for phone in phones:
                    clean_phone = AdvancedUtilities.clean_and_validate_phone(phone)
                    if clean_phone:
                        contacts.append({
                            'value': clean_phone,
                            'type': 'phone',
                            'source': 'about_page',
                            'confidence': 85,
                            'frequency': 1,
                            'context': 'about_section'
                        })
            
            # Also check entire page
            page_text = soup.get_text()
            
            page_emails = re.findall(AdvancedConfig.PATTERNS['email'], page_text, re.IGNORECASE)
            for email in page_emails:
                clean_email = AdvancedUtilities.clean_and_validate_email(email)
                if clean_email:
                    # Check if not already added
                    if not any(c['value'] == clean_email for c in contacts):
                        contacts.append({
                            'value': clean_email,
                            'type': 'email',
                            'source': 'about_page_full',
                            'confidence': 75,
                            'frequency': 1,
                            'context': 'full_page'
                        })
            
        except Exception as e:
            print(f"About page extraction error: {str(e)}")
        
        return contacts
    
    def _extract_advanced_html(self, identifier: str) -> List[Dict]:
        """এডভান্সড HTML পার্সিং"""
        contacts = []
        
        try:
            # Try mbasic version (simpler HTML)
            soup = self.request_manager.get_facebook_page(identifier, 'profile_basic')
            if not soup:
                return contacts
            
            # Look for JSON data in scripts
            for script in soup.find_all('script'):
                if script.string:
                    script_text = script.string
                    
                    # Look for email patterns in script
                    emails = re.findall(AdvancedConfig.PATTERNS['email'], script_text, re.IGNORECASE)
                    for email in emails:
                        clean_email = AdvancedUtilities.clean_and_validate_email(email)
                        if clean_email:
                            contacts.append({
                                'value': clean_email,
                                'type': 'email',
                                'source': 'advanced_html_script',
                                'confidence': 85,
                                'frequency': 1,
                                'context': 'script_data'
                            })
                    
                    # Look for JSON data with emails
                    json_matches = re.findall(AdvancedConfig.PATTERNS['json_data'], script_text)
                    for json_str in json_matches:
                        try:
                            data = json.loads(json_str)
                            # Convert to string and search
                            data_str = json.dumps(data)
                            json_emails = re.findall(AdvancedConfig.PATTERNS['email'], data_str, re.IGNORECASE)
                            for email in json_emails:
                                clean_email = AdvancedUtilities.clean_and_validate_email(email)
                                if clean_email:
                                    contacts.append({
                                        'value': clean_email,
                                        'type': 'email',
                                        'source': 'advanced_html_json',
                                        'confidence': 90,
                                        'frequency': 1,
                                        'context': 'json_data'
                                    })
                        except:
                            continue
            
            # Check data attributes
            for elem in soup.find_all(attrs={"data-email": True}):
                email = elem['data-email']
                clean_email = AdvancedUtilities.clean_and_validate_email(email)
                if clean_email:
                    contacts.append({
                        'value': clean_email,
                        'type': 'email',
                        'source': 'advanced_html_dataattr',
                        'confidence': 88,
                        'frequency': 1,
                        'context': 'data_attribute'
                    })
            
        except Exception as e:
            print(f"Advanced HTML extraction error: {str(e)}")
        
        return contacts
    
    def _extract_public_info(self, identifier: str) -> List[Dict]:
        """পাবলিক ইনফো গ্যাদারিং"""
        contacts = []
        
        try:
            # Try friends page
            soup = self.request_manager.get_facebook_page(identifier, 'friends')
            if soup:
                text = soup.get_text()
                
                # Friends might have similar patterns
                emails = re.findall(AdvancedConfig.PATTERNS['email'], text, re.IGNORECASE)
                for email in emails:
                    clean_email = AdvancedUtilities.clean_and_validate_email(email)
                    if clean_email:
                        contacts.append({
                            'value': clean_email,
                            'type': 'email',
                            'source': 'public_info_friends',
                            'confidence': 60,
                            'frequency': 1,
                            'context': 'friends_page'
                        })
            
            # Try photos page
            soup = self.request_manager.get_facebook_page(identifier, 'photos')
            if soup:
                text = soup.get_text()
                
                emails = re.findall(AdvancedConfig.PATTERNS['email'], text, re.IGNORECASE)
                for email in emails:
                    clean_email = AdvancedUtilities.clean_and_validate_email(email)
                    if clean_email:
                        contacts.append({
                            'value': clean_email,
                            'type': 'email',
                            'source': 'public_info_photos',
                            'confidence': 55,
                            'frequency': 1,
                            'context': 'photos_page'
                        })
            
        except Exception as e:
            print(f"Public info extraction error: {str(e)}")
        
        return contacts
    
    def _extract_backup_sources(self, identifier: str) -> List[Dict]:
        """ব্যাকআপ সোর্সেস চেক"""
        contacts = []
        
        try:
            # Try web archive
            if 'profile.php?id=' in identifier:
                uid = identifier.split('=')[1]
                archive_url = f"https://web.archive.org/web/*/https://facebook.com/profile.php?id={uid}"
            else:
                archive_url = f"https://web.archive.org/web/*/https://facebook.com/{identifier}"
            
            response = self.request_manager.make_request(archive_url)
            if response and response.status_code == 200:
                # Simple extraction from archive page
                text = response.text
                
                emails = re.findall(AdvancedConfig.PATTERNS['email'], text, re.IGNORECASE)
                for email in emails:
                    clean_email = AdvancedUtilities.clean_and_validate_email(email)
                    if clean_email:
                        contacts.append({
                            'value': clean_email,
                            'type': 'email',
                            'source': 'backup_webarchive',
                            'confidence': 65,
                            'frequency': 1,
                            'context': 'web_archive'
                        })
            
            # Try alternative domains
            alt_domains = [
                ('https://web.facebook.com/', 'web_facebook'),
                ('https://mbasic.facebook.com/', 'mbasic'),
                ('https://touch.facebook.com/', 'touch')
            ]
            
            for base_url, source_name in alt_domains:
                try:
                    url = f"{base_url}{identifier}"
                    response = self.request_manager.make_request(url)
                    
                    if response and response.status_code == 200:
                        text = response.text
                        
                        emails = re.findall(AdvancedConfig.PATTERNS['email'], text, re.IGNORECASE)
                        for email in emails:
                            clean_email = AdvancedUtilities.clean_and_validate_email(email)
                            if clean_email:
                                contacts.append({
                                    'value': clean_email,
                                    'type': 'email',
                                    'source': f'backup_{source_name}',
                                    'confidence': 70,
                                    'frequency': 1,
                                    'context': source_name
                                })
                        
                        time.sleep(1)
                        
                except:
                    continue
            
        except Exception as e:
            print(f"Backup sources extraction error: {str(e)}")
        
        return contacts
    
    def _process_contacts(self, contacts: List[Dict]) -> List[Dict]:
        """কন্ট্যাক্টস প্রসেস এবং ডিডুপ্লিকেট"""
        if not contacts:
            return []
        
        # Group by value and type
        contact_map = {}
        
        for contact in contacts:
            key = (contact['value'], contact['type'])
            
            if key in contact_map:
                # Update existing contact
                existing = contact_map[key]
                existing['frequency'] += 1
                existing['confidence'] = min(100, existing['confidence'] + 5)
                
                # Add source if not already present
                if contact['source'] not in existing.get('all_sources', []):
                    existing.setdefault('all_sources', []).append(contact['source'])
                    existing['source'] = f"{existing['source']}, {contact['source']}"
            else:
                # Add new contact
                contact['all_sources'] = [contact['source']]
                contact_map[key] = contact
        
        # Convert to list and sort
        processed = list(contact_map.values())
        
        # Sort by confidence and frequency
        processed.sort(key=lambda x: (x['confidence'], x['frequency']), reverse=True)
        
        return processed
    
    def _generate_recommendations(self, contacts: List[Dict], target_info: Dict) -> List[str]:
        """রিকমেন্ডেশন জেনারেট"""
        recommendations = []
        
        if not contacts:
            recommendations = [
                "No contacts found through automated methods.",
                "Try Facebook's official recovery: https://facebook.com/login/identify",
                "Check all email accounts for Facebook recovery emails.",
                "Contact Facebook support with government ID proof.",
                "Ask trusted friends to check if they have your contact info."
            ]
            return recommendations
        
        # Top contacts
        top_email = next((c for c in contacts if c['type'] == 'email' and c['confidence'] >= 70), None)
        top_phone = next((c for c in contacts if c['type'] == 'phone' and c['confidence'] >= 75), None)
        
        if top_email:
            recommendations.append(f"Try logging in with email: {top_email['value']}")
        
        if top_phone:
            recommendations.append(f"Try logging in with phone: {top_phone['value']}")
        
        if top_email and top_phone:
            recommendations.append("Try email and phone combinations in different orders.")
        
        # Additional suggestions
        recommendations.extend([
            f"Visit Facebook Recovery: https://facebook.com/login/identify",
            "Check spam/junk folders in ALL your email accounts.",
            "Try password reset with each contact found above.",
            "Use incognito/private browsing mode for recovery attempts.",
            "Try different browsers (Chrome, Firefox, Edge)."
        ])
        
        # If multiple high-confidence contacts
        high_conf_contacts = [c for c in contacts if c['confidence'] >= 80]
        if len(high_conf_contacts) >= 2:
            recommendations.append("Multiple high-confidence contacts found - try them all systematically.")
        
        # Final ethical reminder
        recommendations.append("⚠️ USE ONLY FOR RECOVERING YOUR OWN ACCOUNT.")
        
        return recommendations
    
    def _save_to_cache(self, identifier: str, result: Dict):
        """ক্যাশে সেভ"""
        cache_key = hashlib.md5(identifier.encode()).hexdigest()
        cache_file = AdvancedConfig.CACHE_DIR / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
        except:
            pass

# ==================== PROFESSIONAL REPORT SYSTEM ====================
class ProfessionalReportSystem:
    """প্রফেশনাল রিপোর্ট সিস্টেম"""
    
    @staticmethod
    def generate_all_reports(result: Dict) -> Dict:
        """সব রিপোর্ট জেনারেট"""
        reports = {}
        
        # Generate filename
        filename_base = AdvancedUtilities.generate_report_filename(
            result['target_info'], ''
        ).replace('.json', '')
        
        # JSON report
        json_file = AdvancedConfig.REPORTS_DIR / f"{filename_base}.json"
        reports['json'] = ProfessionalReportSystem._save_json(result, json_file)
        
        # Text report
        txt_file = AdvancedConfig.REPORTS_DIR / f"{filename_base}.txt"
        reports['txt'] = ProfessionalReportSystem._save_text(result, txt_file)
        
        # CSV report
        csv_file = AdvancedConfig.REPORTS_DIR / f"{filename_base}.csv"
        reports['csv'] = ProfessionalReportSystem._save_csv(result, csv_file)
        
        # HTML report
        html_file = AdvancedConfig.REPORTS_DIR / f"{filename_base}.html"
        reports['html'] = ProfessionalReportSystem._save_html(result, html_file)
        
        return reports
    
    @staticmethod
    def _save_json(result: Dict, filepath: Path) -> str:
        """JSON রিপোর্ট সেভ"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return str(filepath)
    
    @staticmethod
    def _save_text(result: Dict, filepath: Path) -> str:
        """টেক্সট রিপোর্ট সেভ"""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append(f"MAR-PD ULTIMATE FINAL - ACCOUNT RECOVERY REPORT")
        lines.append("=" * 70)
        lines.append(f"Generated: {result['timestamp']}")
        lines.append(f"Session ID: {result['session_id']}")
        lines.append(f"Target: {result['target']}")
        lines.append(f"Success: {result['success']}")
        lines.append("")
        
        # Statistics
        stats = result['statistics']
        lines.append("📊 STATISTICS")
        lines.append("-" * 50)
        lines.append(f"Total Contacts Found: {stats['total_contacts']}")
        lines.append(f"Email Addresses: {stats['emails']}")
        lines.append(f"Phone Numbers: {stats['phones']}")
        lines.append(f"Confidence Score: {stats['confidence_score']}/100")
        lines.append(f"Extraction Time: {stats['extraction_time']} seconds")
        lines.append(f"Methods Used: {len(stats['methods_used'])}")
        lines.append("")
        
        # Contacts
        if result['contacts']:
            lines.append("📞 CONTACTS FOUND")
            lines.append("-" * 50)
            
            # Group by type
            emails = [c for c in result['contacts'] if c['type'] == 'email']
            phones = [c for c in result['contacts'] if c['type'] == 'phone']
            
            if emails:
                lines.append("\n📧 EMAIL ADDRESSES:")
                for i, email in enumerate(emails[:10], 1):
                    lines.append(f"  {i}. {email['value']}")
                    lines.append(f"     Confidence: {email['confidence']}%")
                    lines.append(f"     Source(s): {email['source']}")
                    if email.get('frequency', 1) > 1:
                        lines.append(f"     Found {email['frequency']} times")
                    lines.append("")
            
            if phones:
                lines.append("\n📱 PHONE NUMBERS:")
                for i, phone in enumerate(phones[:10], 1):
                    lines.append(f"  {i}. {phone['value']}")
                    lines.append(f"     Confidence: {phone['confidence']}%")
                    lines.append(f"     Source(s): {phone['source']}")
                    if phone.get('frequency', 1) > 1:
                        lines.append(f"     Found {phone['frequency']} times")
                    lines.append("")
        
        # Methods
        lines.append("🔧 METHODS USED")
        lines.append("-" * 50)
        for method in stats['methods_used']:
            lines.append(f"• {method}")
        lines.append("")
        
        # Recommendations
        lines.append("💡 RECOMMENDATIONS")
        lines.append("-" * 50)
        for i, rec in enumerate(result['recommendations'][:8], 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append("⚠️  ETHICAL USE REMINDER")
        lines.append("=" * 70)
        lines.append("This report is for SELF-ACCOUNT RECOVERY ONLY.")
        lines.append("Unauthorized access is illegal and unethical.")
        lines.append("You are responsible for using this information properly.")
        lines.append("=" * 70)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return str(filepath)
    
    @staticmethod
    def _save_csv(result: Dict, filepath: Path) -> str:
        """CSV রিপোর্ট সেভ"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['MAR-PD ULTIMATE FINAL - Account Recovery Report'])
            writer.writerow(['Generated', result['timestamp']])
            writer.writerow(['Target', result['target']])
            writer.writerow(['Success', result['success']])
            writer.writerow([])
            
            # Statistics
            writer.writerow(['STATISTICS'])
            stats = result['statistics']
            writer.writerow(['Total Contacts', stats['total_contacts']])
            writer.writerow(['Emails', stats['emails']])
            writer.writerow(['Phones', stats['phones']])
            writer.writerow(['Confidence Score', f"{stats['confidence_score']}/100"])
            writer.writerow([])
            
            # Contacts
            writer.writerow(['CONTACTS'])
            writer.writerow(['Type', 'Value', 'Confidence', 'Source', 'Frequency'])
            
            for contact in result['contacts']:
                writer.writerow([
                    contact['type'].upper(),
                    contact['value'],
                    f"{contact['confidence']}%",
                    contact['source'],
                    contact.get('frequency', 1)
                ])
            
            writer.writerow([])
            
            # Recommendations
            writer.writerow(['RECOMMENDATIONS'])
            for rec in result['recommendations']:
                writer.writerow([rec])
        
        return str(filepath)
    
    @staticmethod
    def _save_html(result: Dict, filepath: Path) -> str:
        """HTML রিপোর্ট সেভ"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MAR-PD Report - Account Recovery</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }}
                .header h1 {{ color: #333; }}
                .section {{ margin-bottom: 30px; }}
                .section h2 {{ color: #4CAF50; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat-card {{ background: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50; }}
                .contact-list {{ margin: 15px 0; }}
                .contact-item {{ background: #f9f9f9; margin: 10px 0; padding: 15px; border-radius: 5px; border: 1px solid #ddd; }}
                .email {{ border-left: 4px solid #2196F3; }}
                .phone {{ border-left: 4px solid #4CAF50; }}
                .recommendation {{ background: #e8f5e9; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #666; font-size: 0.9em; }}
                .confidence-bar {{ background: #ddd; height: 10px; border-radius: 5px; margin: 5px 0; }}
                .confidence-fill {{ background: #4CAF50; height: 100%; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MAR-PD ULTIMATE FINAL</h1>
                    <h2>Account Recovery Report</h2>
                    <p>Generated: {result['timestamp']}</p>
                    <p>Target: {result['target']}</p>
                </div>
                
                <div class="section">
                    <h2>📊 Statistics</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h3>Total Contacts</h3>
                            <p style="font-size: 24px; font-weight: bold;">{result['statistics']['total_contacts']}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Emails</h3>
                            <p style="font-size: 24px; font-weight: bold;">{result['statistics']['emails']}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Phones</h3>
                            <p style="font-size: 24px; font-weight: bold;">{result['statistics']['phones']}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Confidence</h3>
                            <p style="font-size: 24px; font-weight: bold;">{result['statistics']['confidence_score']}/100</p>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: {result['statistics']['confidence_score']}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📞 Contacts Found</h2>
        """
        
        # Add contacts
        if result['contacts']:
            html_content += '<div class="contact-list">'
            
            for contact in result['contacts'][:15]:  # Limit to 15
                contact_class = 'email' if contact['type'] == 'email' else 'phone'
                icon = '📧' if contact['type'] == 'email' else '📱'
                
                html_content += f"""
                    <div class="contact-item {contact_class}">
                        <h3>{icon} {contact['value']}</h3>
                        <p><strong>Type:</strong> {contact['type'].upper()} | 
                           <strong>Confidence:</strong> {contact['confidence']}% | 
                           <strong>Source:</strong> {contact['source']}</p>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {contact['confidence']}%"></div>
                        </div>
                    </div>
                """
            
            html_content += '</div>'
        else:
            html_content += '<p>No contacts found through automated methods.</p>'
        
        # Recommendations
        html_content += f"""
                </div>
                
                <div class="section">
                    <h2>💡 Recommendations</h2>
        """
        
        for rec in result['recommendations'][:10]:
            html_content += f'<div class="recommendation">• {rec}</div>'
        
        # Footer
        html_content += f"""
                </div>
                
                <div class="footer">
                    <p><strong>⚠️ ETHICAL USE REMINDER</strong></p>
                    <p>This report is for SELF-ACCOUNT RECOVERY ONLY.</p>
                    <p>Unauthorized access is illegal and unethical.</p>
                    <p>You are responsible for using this information properly.</p>
                    <p style="margin-top: 20px;">Generated by MAR-PD ULTIMATE FINAL v{AdvancedConfig.VERSION}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)

# ==================== MAIN APPLICATION ====================
class MARPDUltimateApp:
    """মূল অ্যাপ্লিকেশন"""
    
    def __init__(self):
        self.engine = AdvancedExtractionEngine()
        self.report_system = ProfessionalReportSystem()
        
        # Setup environment
        AdvancedUtilities.setup_environment()
    
    def run_interactive(self):
        """ইন্টারেক্টিভ মোড"""
        self._show_banner()
        self._show_ethical_warning()
        
        print("\n" + "="*70)
        print("MAR-PD ULTIMATE FINAL - Interactive Mode")
        print("="*70)
        
        while True:
            print("\n📥 Enter Facebook Profile (or 'quit' to exit):")
            print("\nExamples:")
            print("  • https://facebook.com/username")
            print("  • https://facebook.com/profile.php?id=1000123456789")
            print("  • username")
            print("  • 1000123456789")
            print()
            
            target = input("🔍 Input: ").strip()
            
            if target.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not target:
                print("❌ Please enter a valid input")
                continue
            
            # Validate target
            target_info = AdvancedUtilities.validate_and_parse_target(target)
            
            if not target_info['valid']:
                print(f"❌ {target_info['error']}")
                continue
            
            print(f"\n✅ Target accepted: {target_info['url']}")
            
            # Run extraction
            try:
                result = self.engine.extract_all(target_info)
                
                # Display results
                self._display_results(result)
                
                # Save reports
                reports = self.report_system.generate_all_reports(result)
                
                print("\n💾 Reports saved:")
                for format_name, filepath in reports.items():
                    print(f"  • {format_name.upper()}: {filepath}")
                
                # Ask to open report
                if reports.get('html'):
                    open_report = input("\n📄 Open HTML report in browser? (y/n): ").lower()
                    if open_report == 'y':
                        webbrowser.open(f"file://{reports['html']}")
                
                # Show next steps
                self._show_next_steps(result)
                
                # Ask for another search
                another = input("\n🔍 Search another profile? (y/n): ").lower()
                if another != 'y':
                    print("\n👋 Thank you for using MAR-PD!")
                    break
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Process interrupted")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("\n💡 Try again or check your input")
    
    def run_quick(self, target: str):
        """কুইক মোড"""
        target_info = AdvancedUtilities.validate_and_parse_target(target)
        
        if not target_info['valid']:
            print(f"❌ {target_info['error']}")
            return
        
        print(f"\n🎯 Target: {target_info['url']}")
        print("🚀 Starting extraction...")
        
        try:
            result = self.engine.extract_all(target_info)
            
            # Save reports
            reports = self.report_system.generate_all_reports(result)
            
            print(f"\n✅ Reports saved:")
            for format_name, filepath in reports.items():
                print(f"  • {format_name.upper()}: {filepath}")
            
            # Show summary
            if result['contacts']:
                print(f"\n📊 Found {result['statistics']['total_contacts']} contacts")
                print(f"📈 Confidence: {result['statistics']['confidence_score']}/100")
                
                top_email = next((c for c in result['contacts'] if c['type'] == 'email'), None)
                top_phone = next((c for c in result['contacts'] if c['type'] == 'phone'), None)
                
                if top_email:
                    print(f"📧 Top email: {top_email['value']} ({top_email['confidence']}%)")
                if top_phone:
                    print(f"📱 Top phone: {top_phone['value']} ({top_phone['confidence']}%)")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def run_batch(self, targets_file: str):
        """ব্যাচ মোড"""
        try:
            with open(targets_file, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
            
            print(f"\n📋 Processing {len(targets)} targets...")
            
            for i, target in enumerate(targets, 1):
                print(f"\n[{i}/{len(targets)}] Processing: {target}")
                
                target_info = AdvancedUtilities.validate_and_parse_target(target)
                
                if not target_info['valid']:
                    print(f"   ❌ Invalid: {target_info.get('error', 'Unknown error')}")
                    continue
                
                try:
                    result = self.engine.extract_all(target_info)
                    
                    # Save report
                    reports = self.report_system.generate_all_reports(result)
                    print(f"   ✅ Report: {reports.get('json', 'Unknown')}")
                    
                    time.sleep(2)  # Delay between targets
                    
                except Exception as e:
                    print(f"   ❌ Failed: {str(e)[:50]}")
                    continue
            
            print("\n✅ Batch processing complete!")
            
        except FileNotFoundError:
            print(f"❌ File not found: {targets_file}")
        except Exception as e:
            print(f"❌ Batch processing error: {str(e)}")
    
    def _show_banner(self):
        """ব্যানার দেখান"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║                 MAR-PD ULTIMATE FINAL v{AdvancedConfig.VERSION}                 ║
║           Professional Facebook Account Recovery Tool            ║
║                    For Personal Use Only                         ║
║                                                                  ║
║           🔒 Secure | 🔍 Advanced | ⚖️ Ethical | 📊 Professional ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def _show_ethical_warning(self):
        """নৈতিক ওয়ার্নিং"""
        warning = """
⚠️  IMPORTANT ETHICAL WARNING ⚠️

This tool is STRICTLY for recovering YOUR OWN Facebook account
when you have legitimately lost access.

YOU MUST AGREE:
1. Use ONLY for YOUR account recovery
2. NEVER access others' accounts without permission
3. Respect all privacy laws and regulations
4. Follow Facebook's Terms of Service
5. Use the tool responsibly and ethically

VIOLATIONS MAY RESULT IN:
• Legal prosecution
• Account suspension
• Criminal charges
• Civil lawsuits

By using this tool, you accept full responsibility for your actions.
"""
        print(warning)
        
        agree = input("Do you agree to these terms? (Type 'YES' to continue): ")
        
        if agree.strip().upper() != "YES":
            print("\n❌ Agreement not accepted. Exiting...")
            sys.exit(0)
        
        print("\n✅ Ethical agreement accepted")
        print("🔐 Starting secure session...\n")
    
    def _display_results(self, result: Dict):
        """রেজাল্টস ডিসপ্লে"""
        print(f"\n{'='*70}")
        print("📊 EXTRACTION RESULTS")
        print(f"{'='*70}")
        
        stats = result['statistics']
        
        print(f"\n🎯 Target: {result['target']}")
        print(f"✅ Success: {result['success']}")
        print(f"📈 Confidence Score: {stats['confidence_score']}/100")
        print(f"⏱️  Time Taken: {stats['extraction_time']} seconds")
        print(f"🔧 Methods Used: {len(stats['methods_used'])}")
        
        if result['contacts']:
            print(f"\n📞 CONTACTS FOUND ({stats['total_contacts']}):")
            print("-" * 60)
            
            # Show top contacts
            top_contacts = result['contacts'][:5]
            
            for i, contact in enumerate(top_contacts, 1):
                icon = "📧" if contact['type'] == 'email' else "📱"
                print(f"\n  {i}. {icon} {contact['value']}")
                print(f"     Confidence: {contact['confidence']}%")
                print(f"     Source: {contact['source']}")
                if contact.get('frequency', 1) > 1:
                    print(f"     Found {contact['frequency']} times")
        else:
            print("\n❌ No contacts found via automated methods")
        
        print(f"\n💡 TOP RECOMMENDATIONS:")
        print("-" * 60)
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"  {i}. {rec}")
    
    def _show_next_steps(self, result: Dict):
        """পরবর্তী স্টেপস"""
        print(f"\n{'='*70}")
        print("🚀 NEXT STEPS FOR ACCOUNT RECOVERY")
        print(f"{'='*70}")
        
        print("\n1. IMMEDIATE ACTION:")
        print("   Go to: https://facebook.com/login/identify")
        
        if result['contacts']:
            print("\n2. TRY THESE CONTACTS:")
            top_contacts = result['contacts'][:3]
            for contact in top_contacts:
                print(f"   • {contact['value']}")
        
        print("\n3. IF STILL STUCK:")
        print("   • Check ALL email spam folders")
        print("   • Try password reset with each contact")
        print("   • Use different browser/device")
        print("   • Contact Facebook support: https://facebook.com/help")
        
        print(f"\n{'='*70}")
        print("⚠️  REMEMBER: USE ONLY FOR YOUR ACCOUNT")
        print(f"{'='*70}")

# ==================== COMMAND LINE INTERFACE ====================
def main():
    """মেইন এন্ট্রি"""
    parser = argparse.ArgumentParser(
        description=f"{AdvancedConfig.APP_NAME} v{AdvancedConfig.VERSION} - Professional Facebook Account Recovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s                         # Interactive mode
  %(prog)s -t "facebook.com/username"
  %(prog)s -t "1000123456789"
  %(prog)s --batch targets.txt
  %(prog)s --setup                 # First-time setup
  %(prog)s --help                  # Show help

Version: {AdvancedConfig.VERSION}
Author: {AdvancedConfig.AUTHOR}
License: {AdvancedConfig.LICENSE}

Ethical Use:
  This tool is ONLY for recovering your own Facebook account
  when you've legitimately lost access. Never misuse.
        """
    )
    
    parser.add_argument('-t', '--target', help='Facebook profile URL, username, or UID')
    parser.add_argument('-b', '--batch', help='File containing list of targets (one per line)')
    parser.add_argument('--setup', action='store_true', help='First-time setup')
    parser.add_argument('--version', action='store_true', help='Show version')
    
    args = parser.parse_args()
    
    # Check dependencies first
    if not check_dependencies():
        print("\n💡 Try: pip install requests beautifulsoup4")
        return
    
    # Show version
    if args.version:
        print(f"{AdvancedConfig.APP_NAME} v{AdvancedConfig.VERSION}")
        print(f"Author: {AdvancedConfig.AUTHOR}")
        print(f"License: {AdvancedConfig.LICENSE}")
        return
    
    # Setup mode
    if args.setup:
        print(f"\n🔧 Setting up {AdvancedConfig.APP_NAME}...")
        AdvancedUtilities.setup_environment()
        print(f"\n✅ Setup complete!")
        print(f"📁 Data directory: {AdvancedConfig.BASE_DIR}")
        print(f"📄 Reports directory: {AdvancedConfig.REPORTS_DIR}")
        return
    
    # Create app instance
    app = MARPDUltimateApp()
    
    # Run based on arguments
    if args.batch:
        app.run_batch(args.batch)
    elif args.target:
        app.run_quick(args.target)
    else:
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