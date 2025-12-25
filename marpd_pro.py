#!/usr/bin/env python3
"""
MAR-PD ULTIMATE PRO v5.0
The Most Advanced Facebook Account Recovery Tool
Single File - Complete Solution
Author: Master
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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from urllib.parse import urlparse, parse_qs, quote, urljoin, unquote
import requests
from bs4 import BeautifulSoup, Comment
import threading
from queue import Queue
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import csv
import logging
from logging.handlers import RotatingFileHandler
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import getpass

# ==================== ADVANCED CONFIGURATION ====================
class Config:
    """এডভান্সড কনফিগারেশন"""
    APP_NAME = "MAR-PD ULTIMATE PRO"
    VERSION = "5.0"
    AUTHOR = "Master"
    
    # Request settings
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
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
        'mail.com', 'protonmail.com', 'yandex.com', 'zoho.com'
    ]
    
    # Regex patterns
    PATTERNS = {
        'bd_phone': r'(?:\+?88)?01[3-9]\d{8}',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        'facebook_id': r'\d{9,}',
        'profile_url': r'(?:https?://)?(?:www\.|m\.|web\.|touch\.)?(?:facebook\.com|fb\.com)/(?:profile\.php\?id=(\d+)|([^/?]+))',
        'graphql_response': r'"email":\s*"([^"]+)"|\'email\':\s*\'([^\']+)\'',
        'json_emails': r'[\w\.-]+@[\w\.-]+\.\w+'
    }
    
    # API endpoints
    ENDPOINTS = {
        'graphql': 'https://www.facebook.com/api/graphql/',
        'graphql_web': 'https://web.facebook.com/api/graphql/',
        'graphql_mobile': 'https://m.facebook.com/api/graphql/',
        'profile': 'https://www.facebook.com/{identifier}',
        'profile_mobile': 'https://m.facebook.com/{identifier}',
        'profile_web': 'https://web.facebook.com/{identifier}',
        'about': 'https://www.facebook.com/{identifier}/about',
        'friends': 'https://www.facebook.com/{identifier}/friends',
        'photos': 'https://www.facebook.com/{identifier}/photos'
    }
    
    # GraphQL queries (common ones)
    GRAPHQL_QUERIES = {
        'user_info': '3315274998225349',
        'user_contacts': '4270752577582839',
        'profile_data': '3581399441840129',
        'account_info': '4250402144846247'
    }

# ==================== ENCRYPTION MODULE ====================
class EncryptionManager:
    """এনক্রিপশন ম্যানেজার"""
    
    def __init__(self, key=None):
        self.key = key or self._generate_key()
    
    def _generate_key(self):
        """কী জেনারেট করুন"""
        return hashlib.sha256(getpass.getpass("Enter encryption password: ").encode()).digest()
    
    def encrypt(self, data):
        """ডাটা এনক্রিপ্ট করুন"""
        try:
            cipher = AES.new(self.key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
            iv = base64.b64encode(cipher.iv).decode('utf-8')
            ct = base64.b64encode(ct_bytes).decode('utf-8')
            return json.dumps({'iv': iv, 'ciphertext': ct})
        except:
            return data
    
    def decrypt(self, encrypted_data):
        """ডাটা ডিক্রিপ্ট করুন"""
        try:
            b64 = json.loads(encrypted_data)
            iv = base64.b64decode(b64['iv'])
            ct = base64.b64decode(b64['ciphertext'])
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode('utf-8')
        except:
            return encrypted_data

# ==================== LOGGING SYSTEM ====================
class AdvancedLogger:
    """এডভান্সড লগিং সিস্টেম"""
    
    def __init__(self):
        self.logger = logging.getLogger('MARPD_PRO')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        log_file = 'marpd_pro.log'
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log(self, level, message, data=None):
        """লগ রেকর্ড করুন"""
        log_msg = message
        if data:
            log_msg += f" | Data: {json.dumps(data)[:200]}"
        
        if level == 'info':
            self.logger.info(log_msg)
        elif level == 'warning':
            self.logger.warning(log_msg)
        elif level == 'error':
            self.logger.error(log_msg)
        elif level == 'critical':
            self.logger.critical(log_msg)

# ==================== DATA STRUCTURES ====================
@dataclass
class Contact:
    """কন্ট্যাক্ট ডাটা স্ট্রাকচার"""
    value: str
    type: str  # email, phone, username
    source: str
    confidence: int  # 0-100
    frequency: int = 1
    metadata: Dict = field(default_factory=dict)
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return asdict(self)
    
    def __hash__(self):
        return hash(f"{self.value}_{self.type}")

@dataclass
class ProfileInfo:
    """প্রোফাইল ইনফো"""
    uid: str = ""
    username: str = ""
    name: str = ""
    url: str = ""
    is_verified: bool = False
    friend_count: int = 0
    registration_date: str = ""
    last_active: str = ""

@dataclass
class ExtractionReport:
    """এক্সট্রাকশন রিপোর্ট"""
    target: str
    profile: ProfileInfo
    contacts: List[Contact]
    methods_used: List[str]
    statistics: Dict
    recommendations: List[str]
    confidence_score: float
    timestamp: str
    session_id: str
    
    def to_dict(self):
        result = asdict(self)
        result['profile'] = self.profile.to_dict() if self.profile else {}
        result['contacts'] = [c.to_dict() for c in self.contacts]
        return result

# ==================== CORE ENGINE ====================
class MARPDProEngine:
    """MAR-PD PRO মূল ইঞ্জিন"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(Config.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })
        
        self.logger = AdvancedLogger()
        self.encryption = EncryptionManager()
        self.cache = {}
        self.rate_limiter = RateLimiter()
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        # Ethical compliance
        self.ethical_check()
    
    def ethical_check(self):
        """নৈতিক চেক"""
        print("\n" + "="*70)
        print("⚠️  MAR-PD ULTIMATE PRO - ETHICAL COMPLIANCE CHECK")
        print("="*70)
        
        terms = """
        This tool is STRICTLY for LEGITIMATE ACCOUNT RECOVERY purposes ONLY.
        
        YOU MUST AGREE TO:
        1. Use ONLY for recovering YOUR OWN Facebook account
        2. NEVER attempt to access others' accounts without permission
        3. Respect all privacy laws and regulations
        4. Follow Facebook's Terms of Service
        5. Use the tool responsibly and ethically
        
        VIOLATIONS MAY RESULT IN:
        • Legal prosecution under computer fraud laws
        • Permanent Facebook account suspension
        • Civil lawsuits for privacy violations
        • Criminal charges in your jurisdiction
        
        By using this tool, you accept full responsibility for your actions.
        """
        
        print(terms)
        print("="*70)
        
        agreement = input("\nDo you agree to these terms? (Type 'I AGREE' to continue): ")
        
        if agreement.strip().upper() != "I AGREE":
            print("\n❌ Agreement not accepted. Tool will now exit.")
            sys.exit(0)
        
        # Log agreement
        self.logger.log('info', 'User accepted ethical agreement', {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat()
        })
        
        print("\n✅ Ethical agreement accepted")
        print("🔐 Starting secure session...")
    
    def extract(self, target: str) -> ExtractionReport:
        """মূল এক্সট্রাকশন ফাংশন"""
        print(f"\n🎯 Target: {target}")
        print("🚀 Starting advanced extraction...")
        
        start_time = time.time()
        
        try:
            # Parse target
            profile_info = self._parse_target(target)
            if not profile_info.uid and not profile_info.username:
                raise ValueError("Invalid target format")
            
            print(f"✅ Parsed: {profile_info.uid or profile_info.username}")
            
            # Run all extraction modules
            all_contacts = []
            methods_used = []
            
            extraction_modules = [
                ('Basic Profile Scan', self._extract_basic_profile),
                ('Advanced HTML Analysis', self._extract_advanced_html),
                ('GraphQL Intelligence', self._extract_graphql),
                ('Mobile Site Analysis', self._extract_mobile),
                ('Security Context', self._extract_security_context),
                ('Public Footprint', self._extract_public_footprint),
                ('Backup Sources', self._extract_backup_sources),
                ('Pattern Analysis', self._extract_patterns)
            ]
            
            for module_name, module_func in extraction_modules:
                try:
                    print(f"\n  🔍 {module_name}...")
                    
                    contacts = module_func(profile_info)
                    if contacts:
                        all_contacts.extend(contacts)
                        methods_used.append(module_name)
                        print(f"    ✅ Found {len(contacts)} contacts")
                    
                    self.rate_limiter.wait()
                    
                except Exception as e:
                    print(f"    ⚠️  {module_name} failed: {str(e)[:50]}")
                    continue
            
            # Process results
            processed_contacts = self._process_contacts(all_contacts)
            statistics = self._calculate_statistics(processed_contacts, methods_used)
            confidence = self._calculate_confidence(processed_contacts)
            recommendations = self._generate_recommendations(processed_contacts, profile_info)
            
            elapsed_time = time.time() - start_time
            
            # Create report
            report = ExtractionReport(
                target=target,
                profile=profile_info,
                contacts=processed_contacts,
                methods_used=methods_used,
                statistics=statistics,
                recommendations=recommendations,
                confidence_score=confidence,
                timestamp=datetime.now().isoformat(),
                session_id=self.session_id
            )
            
            # Log successful extraction
            self.logger.log('info', 'Extraction completed successfully', {
                'target': target,
                'contacts_found': len(processed_contacts),
                'confidence': confidence,
                'time_taken': elapsed_time
            })
            
            return report
            
        except Exception as e:
            self.logger.log('error', 'Extraction failed', {'error': str(e)})
            raise
    
    def _parse_target(self, target: str) -> ProfileInfo:
        """টার্গেট পার্স করুন"""
        profile = ProfileInfo()
        
        # Extract UID or username
        match = re.search(Config.PATTERNS['profile_url'], target, re.IGNORECASE)
        
        if match:
            if match.group(1):  # Numeric ID
                profile.uid = match.group(1)
                profile.url = f"https://facebook.com/profile.php?id={profile.uid}"
            else:  # Username
                profile.username = match.group(2)
                profile.url = f"https://facebook.com/{profile.username}"
        elif target.isdigit() and len(target) > 8:
            profile.uid = target
            profile.url = f"https://facebook.com/profile.php?id={profile.uid}"
        else:
            profile.username = target
            profile.url = f"https://facebook.com/{profile.username}"
        
        return profile
    
    # ==================== EXTRACTION MODULES ====================
    
    def _extract_basic_profile(self, profile: ProfileInfo) -> List[Contact]:
        """বেসিক প্রোফাইল স্ক্যান"""
        contacts = []
        
        try:
            response = self._make_request(profile.url)
            if not response:
                return contacts
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract from page text
            text = soup.get_text()
            
            # Emails
            emails = re.findall(Config.PATTERNS['email'], text, re.IGNORECASE)
            for email in emails:
                if self._validate_email(email):
                    contacts.append(Contact(
                        value=email.lower(),
                        type='email',
                        source='basic_profile',
                        confidence=65,
                        metadata={'context': 'page_text'}
                    ))
            
            # Phones
            phones = re.findall(Config.PATTERNS['bd_phone'], text)
            for phone in phones:
                clean_phone = self._clean_phone(phone)
                if clean_phone:
                    contacts.append(Contact(
                        value=clean_phone,
                        type='phone',
                        source='basic_profile',
                        confidence=70,
                        metadata={'context': 'page_text'}
                    ))
            
            # Meta tags
            for meta in soup.find_all('meta'):
                content = meta.get('content', '')
                if '@' in content:
                    emails = re.findall(Config.PATTERNS['email'], content, re.IGNORECASE)
                    for email in emails:
                        if self._validate_email(email):
                            contacts.append(Contact(
                                value=email.lower(),
                                type='email',
                                source='basic_profile_meta',
                                confidence=70,
                                metadata={'tag': meta.get('name', 'unknown')}
                            ))
            
        except Exception as e:
            self.logger.log('error', 'Basic profile extraction failed', {'error': str(e)})
        
        return contacts
    
    def _extract_advanced_html(self, profile: ProfileInfo) -> List[Contact]:
        """এডভান্সড HTML এনালাইসিস"""
        contacts = []
        
        try:
            # Try different profile sections
            sections = ['about', 'friends', 'photos', 'videos']
            
            for section in sections:
                try:
                    if profile.uid:
                        url = f"https://facebook.com/profile.php?id={profile.uid}&sk={section}"
                    else:
                        url = f"https://facebook.com/{profile.username}/{section}"
                    
                    response = self._make_request(url)
                    if not response:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Advanced parsing techniques
                    
                    # 1. JSON-LD data
                    for script in soup.find_all('script', type='application/ld+json'):
                        try:
                            data = json.loads(script.string)
                            contacts.extend(self._extract_from_json(data, f'jsonld_{section}'))
                        except:
                            continue
                    
                    # 2. Hidden inputs
                    for inp in soup.find_all('input', type='hidden'):
                        value = inp.get('value', '')
                        if '@' in value:
                            emails = re.findall(Config.PATTERNS['email'], value, re.IGNORECASE)
                            for email in emails:
                                if self._validate_email(email):
                                    contacts.append(Contact(
                                        value=email.lower(),
                                        type='email',
                                        source=f'hidden_input_{section}',
                                        confidence=75,
                                        metadata={'input_name': inp.get('name', 'unknown')}
                                    ))
                    
                    # 3. Data attributes
                    for elem in soup.find_all(attrs={"data-email": True}):
                        email = elem['data-email']
                        if self._validate_email(email):
                            contacts.append(Contact(
                                value=email.lower(),
                                type='email',
                                source=f'data_attr_{section}',
                                confidence=80,
                                metadata={'element': elem.name}
                            ))
                    
                    self.rate_limiter.wait()
                    
                except:
                    continue
            
        except Exception as e:
            self.logger.log('error', 'Advanced HTML extraction failed', {'error': str(e)})
        
        return contacts
    
    def _extract_graphql(self, profile: ProfileInfo) -> List[Contact]:
        """GraphQL ইন্টেলিজেন্স"""
        contacts = []
        
        try:
            identifier = profile.uid or profile.username
            
            # Try multiple GraphQL queries
            for query_name, query_id in Config.GRAPHQL_QUERIES.items():
                try:
                    for endpoint in [Config.ENDPOINTS['graphql'], Config.ENDPOINTS['graphql_web']]:
                        try:
                            headers = {
                                'User-Agent': random.choice(Config.USER_AGENTS),
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Origin': 'https://www.facebook.com',
                                'Referer': profile.url,
                                'X-FB-Friendly-Name': query_name
                            }
                            
                            data = {
                                'variables': json.dumps({'userID': identifier}),
                                'doc_id': query_id,
                                'fb_api_req_friendly_name': query_name
                            }
                            
                            response = requests.post(
                                endpoint,
                                headers=headers,
                                data=data,
                                timeout=15
                            )
                            
                            if response.status_code == 200:
                                # Parse response
                                response_data = response.text
                                
                                # Extract emails
                                emails = re.findall(Config.PATTERNS['email'], response_data, re.IGNORECASE)
                                for email in emails:
                                    if self._validate_email(email):
                                        contacts.append(Contact(
                                            value=email.lower(),
                                            type='email',
                                            source=f'graphql_{query_name}',
                                            confidence=85,
                                            metadata={'query': query_name, 'endpoint': endpoint}
                                        ))
                                
                                # Extract phones
                                phones = re.findall(Config.PATTERNS['bd_phone'], response_data)
                                for phone in phones:
                                    clean_phone = self._clean_phone(phone)
                                    if clean_phone:
                                        contacts.append(Contact(
                                            value=clean_phone,
                                            type='phone',
                                            source=f'graphql_{query_name}',
                                            confidence=90,
                                            metadata={'query': query_name, 'endpoint': endpoint}
                                        ))
                                
                                # Try to parse JSON
                                try:
                                    json_data = response.json()
                                    contacts.extend(self._extract_from_json(json_data, f'graphql_json_{query_name}'))
                                except:
                                    pass
                            
                            self.rate_limiter.wait()
                            
                        except:
                            continue
                        
                        break  # If successful, break endpoint loop
                    
                except:
                    continue
            
        except Exception as e:
            self.logger.log('error', 'GraphQL extraction failed', {'error': str(e)})
        
        return contacts
    
    def _extract_mobile(self, profile: ProfileInfo) -> List[Contact]:
        """মোবাইল সাইট এনালাইসিস"""
        contacts = []
        
        try:
            # Mobile versions often show different data
            mobile_versions = [
                ('https://m.facebook.com/', 'mobile'),
                ('https://touch.facebook.com/', 'touch'),
                ('https://mbasic.facebook.com/', 'mbasic')
            ]
            
            for base_url, version in mobile_versions:
                try:
                    if profile.uid:
                        url = f"{base_url}profile.php?id={profile.uid}"
                    else:
                        url = f"{base_url}{profile.username}"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Mobile sites often have simpler contact info
                        
                        # Check for contact links
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            
                            # mailto links
                            if 'mailto:' in href:
                                email = href.split('mailto:')[1].split('?')[0]
                                if self._validate_email(email):
                                    contacts.append(Contact(
                                        value=email.lower(),
                                        type='email',
                                        source=f'mobile_{version}',
                                        confidence=75,
                                        metadata={'link_text': link.get_text()[:50]}
                                    ))
                            
                            # tel links
                            elif 'tel:' in href:
                                phone = href.split('tel:')[1]
                                clean_phone = self._clean_phone(phone)
                                if clean_phone:
                                    contacts.append(Contact(
                                        value=clean_phone,
                                        type='phone',
                                        source=f'mobile_{version}',
                                        confidence=80,
                                        metadata={'link_text': link.get_text()[:50]}
                                    ))
                        
                        # Mobile specific sections
                        mobile_sections = soup.find_all(['div', 'section'], class_=re.compile(r'contact|info|detail'))
                        for section in mobile_sections:
                            text = section.get_text()
                            
                            emails = re.findall(Config.PATTERNS['email'], text, re.IGNORECASE)
                            for email in emails:
                                if self._validate_email(email):
                                    contacts.append(Contact(
                                        value=email.lower(),
                                        type='email',
                                        source=f'mobile_section_{version}',
                                        confidence=70,
                                        metadata={'section_type': 'mobile_specific'}
                                    ))
                    
                    self.rate_limiter.wait()
                    
                except:
                    continue
            
        except Exception as e:
            self.logger.log('error', 'Mobile extraction failed', {'error': str(e)})
        
        return contacts
    
    def _extract_security_context(self, profile: ProfileInfo) -> List[Contact]:
        """সিকিউরিটি কনটেক্সট"""
        contacts = []
        
        try:
            # Security related endpoints
            security_urls = [
                f"https://www.facebook.com/{profile.uid or profile.username}/settings",
                "https://www.facebook.com/security",
                "https://www.facebook.com/settings?tab=security"
            ]
            
            for url in security_urls:
                try:
                    response = self._make_request(url)
                    if not response:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for security context
                    security_keywords = [
                        'recovery', 'backup', 'secondary', 'alternative',
                        'verification', '2fa', 'authentication', 'trusted'
                    ]
                    
                    for keyword in security_keywords:
                        elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
                        
                        for element in elements:
                            parent = element.parent
                            if parent:
                                text = parent.get_text()
                                
                                # Emails in security context
                                emails = re.findall(Config.PATTERNS['email'], text, re.IGNORECASE)
                                for email in emails:
                                    if self._validate_email(email):
                                        contacts.append(Contact(
                                            value=email.lower(),
                                            type='email',
                                            source='security_context',
                                            confidence=90,
                                            metadata={
                                                'keyword': keyword,
                                                'context': text[:100]
                                            }
                                        ))
                                
                                # Phones in security context
                                phones = re.findall(Config.PATTERNS['bd_phone'], text)
                                for phone in phones:
                                    clean_phone = self._clean_phone(phone)
                                    if clean_phone:
                                        contacts.append(Contact(
                                            value=clean_phone,
                                            type='phone',
                                            source='security_context',
                                            confidence=95,
                                            metadata={
                                                'keyword': keyword,
                                                'context': text[:100]
                                            }
                                        ))
                    
                    self.rate_limiter.wait()
                    
                except:
                    continue
            
        except Exception as e:
            self.logger.log('error', 'Security context extraction failed', {'error': str(e)})
        
        return contacts
    
    def _extract_public_footprint(self, profile: ProfileInfo) -> List[Contact]:
        """পাবলিক ফুটপ্রিন্ট"""
        contacts = []
        
        try:
            # Search for public mentions
            if profile.username:
                # Google search simulation
                search_terms = [
                    f'"{profile.username}" email',
                    f'"{profile.username}" contact',
                    f'"{profile.username}" facebook',
                    f'"{profile.username}" @gmail.com',
                    f'"{profile.username}" @yahoo.com'
                ]
                
                for term in search_terms:
                    try:
                        # Limited public search simulation
                        google_url = "https://www.google.com/search"
                        params = {'q': term, 'num': 10}
                        
                        headers = {'User-Agent': random.choice(Config.USER_AGENTS)}
                        
                        response = requests.get(google_url, params=params, headers=headers, timeout=15)
                        
                        if response.status_code == 200:
                            # Extract from search results
                            text = response.text
                            
                            emails = re.findall(Config.PATTERNS['email'], text, re.IGNORECASE)
                            for email in emails:
                                if self._validate_email(email) and profile.username.lower() in email.lower():
                                    contacts.append(Contact(
                                        value=email.lower(),
                                        type='email',
                                        source='public_footprint',
                                        confidence=60,
                                        metadata={'search_term': term}
                                    ))
                        
                        time.sleep(2)  # Respect rate limits
                        
                    except:
                        continue
            
        except Exception as e:
            self.logger.log('error', 'Public footprint extraction failed', {'error': str(e)})
        
        return contacts
    
    def _extract_backup_sources(self, profile: ProfileInfo) -> List[Contact]:
        """ব্যাকআপ সোর্সেস"""
        contacts = []
        
        try:
            # Check alternative data sources
            
            # 1. Archive.org
            try:
                if profile.uid:
                    archive_url = f"https://web.archive.org/web/*/https://facebook.com/profile.php?id={profile.uid}"
                else:
                    archive_url = f"https://web.archive.org/web/*/https://facebook.com/{profile.username}"
                
                response = requests.get(archive_url, timeout=15)
                
                if response.status_code == 200:
                    # Parse for snapshots
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Get snapshot links
                    snapshot_links = soup.find_all('a', href=re.compile(r'/web/\d+/'))
                    
                    for link in snapshot_links[:3]:  # Check first 3 snapshots
                        try:
                            snapshot_url = urljoin('https://web.archive.org', link['href'])
                            snapshot_response = requests.get(snapshot_url, timeout=10)
                            
                            if snapshot_response.status_code == 200:
                                # Extract from snapshot
                                emails = re.findall(Config.PATTERNS['email'], snapshot_response.text, re.IGNORECASE)
                                for email in emails:
                                    if self._validate_email(email):
                                        contacts.append(Contact(
                                            value=email.lower(),
                                            type='email',
                                            source='archive_org',
                                            confidence=65,
                                            metadata={'snapshot_url': snapshot_url}
                                        ))
                            
                            time.sleep(1)
                            
                        except:
                            continue
            except:
                pass
            
            # 2. Social media cross-reference
            if profile.username:
                social_sites = [
                    f"https://twitter.com/{profile.username}",
                    f"https://instagram.com/{profile.username}",
                    f"https://github.com/{profile.username}"
                ]
                
                for site in social_sites:
                    try:
                        response = requests.get(site, timeout=10)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Look for bio/description
                            bio_selectors = ['bio', 'description', 'about', 'intro']
                            
                            for selector in bio_selectors:
                                elements = soup.find_all(['div', 'p', 'span'], class_=re.compile(selector, re.I))
                                
                                for element in elements:
                                    text = element.get_text()
                                    
                                    emails = re.findall(Config.PATTERNS['email'], text, re.IGNORECASE)
                                    for email in emails:
                                        if self._validate_email(email):
                                            contacts.append(Contact(
                                                value=email.lower(),
                                                type='email',
                                                source='social_crossref',
                                                confidence=70,
                                                metadata={'site': site, 'selector': selector}
                                            ))
                        
                        time.sleep(1)
                        
                    except:
                        continue
            
        except Exception as e:
            self.logger.log('error', 'Backup sources extraction failed', {'error': str(e)})
        
        return contacts
    
    def _extract_patterns(self, profile: ProfileInfo) -> List[Contact]:
        """প্যাটার্ন এনালাইসিস"""
        contacts = []
        
        try:
            # Try to guess email based on username patterns
            if profile.username:
                name_parts = profile.username.lower().split('.')
                if len(name_parts) >= 2:
                    first_part = name_parts[0]
                    
                    # Generate potential email patterns
                    patterns = []
                    
                    for domain in Config.EMAIL_DOMAINS[:3]:  # Top 3 domains
                        patterns.extend([
                            f"{first_part}@{domain}",
                            f"{profile.username}@{domain}",
                            f"{first_part}123@{domain}",
                            f"{first_part}{random.randint(10, 99)}@{domain}"
                        ])
                    
                    # These are just guesses, low confidence
                    for pattern in patterns:
                        if self._validate_email(pattern):
                            contacts.append(Contact(
                                value=pattern.lower(),
                                type='email',
                                source='pattern_analysis',
                                confidence=30,  # Low confidence guesses
                                metadata={'pattern_type': 'username_based'}
                            ))
            
        except Exception as e:
            self.logger.log('error', 'Pattern analysis failed', {'error': str(e)})
        
        return contacts
    
    # ==================== HELPER METHODS ====================
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """সেফ রিকোয়েস্ট"""
        try:
            self.rate_limiter.wait()
            
            headers = {'User-Agent': random.choice(Config.USER_AGENTS)}
            response = self.session.get(url, headers=headers, timeout=15)
            
            # Cache response
            cache_key = hashlib.md5(url.encode()).hexdigest()
            self.cache[cache_key] = {
                'response': response.text[:5000],
                'timestamp': time.time()
            }
            
            return response
            
        except Exception as e:
            self.logger.log('error', 'Request failed', {'url': url, 'error': str(e)})
            return None
    
    def _extract_from_json(self, data: Any, source: str) -> List[Contact]:
        """JSON থেকে কন্ট্যাক্টস এক্সট্র্যাক্ট করুন"""
        contacts = []
        
        try:
            data_str = json.dumps(data)
            
            # Extract emails
            emails = re.findall(Config.PATTERNS['email'], data_str, re.IGNORECASE)
            for email in emails:
                if self._validate_email(email):
                    contacts.append(Contact(
                        value=email.lower(),
                        type='email',
                        source=source,
                        confidence=80,
                        metadata={'data_type': 'json'}
                    ))
            
            # Extract phones
            phones = re.findall(Config.PATTERNS['bd_phone'], data_str)
            for phone in phones:
                clean_phone = self._clean_phone(phone)
                if clean_phone:
                    contacts.append(Contact(
                        value=clean_phone,
                        type='phone',
                        source=source,
                        confidence=85,
                        metadata={'data_type': 'json'}
                    ))
            
        except:
            pass
        
        return contacts
    
    def _validate_email(self, email: str) -> bool:
        """ইমেইল ভ্যালিডেশন"""
        email = email.lower().strip()
        
        # Basic format check
        if not re.match(Config.PATTERNS['email'], email):
            return False
        
        # Common invalid patterns
        invalid_terms = [
            'example', 'test', 'domain', 'email.com', 'mail.com',
            'noreply', 'no-reply', 'donotreply'
        ]
        
        for term in invalid_terms:
            if term in email:
                return False
        
        # Domain check
        domain = email.split('@')[1] if '@' in email else ''
        
        # Allow common domains and others
        if any(common_domain in domain for common_domain in Config.EMAIL_DOMAINS):
            return True
        
        # Also allow other valid domains
        return '.' in domain and len(domain.split('.')[-1]) >= 2
    
    def _clean_phone(self, phone: str) -> Optional[str]:
        """ফোন নাম্বার ক্লিন করুন"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Handle BD numbers
        if len(digits) == 11 and digits.startswith('01'):
            return digits
        elif len(digits) == 13 and digits.startswith('8801'):
            return f"0{digits[2:]}"  # Convert 8801... to 01...
        elif len(digits) == 10 and digits.startswith('1'):
            return f"0{digits}"
        
        return None
    
    def _process_contacts(self, contacts: List[Contact]) -> List[Contact]:
        """কন্ট্যাক্টস প্রসেস করুন"""
        if not contacts:
            return []
        
        # Group by value and type
        contact_map = {}
        
        for contact in contacts:
            key = (contact.value, contact.type)
            
            if key in contact_map:
                # Update existing contact
                existing = contact_map[key]
                existing.frequency += 1
                existing.confidence = min(100, existing.confidence + 5)
                existing.sources = list(set(existing.sources.split(', ') + [contact.source]))
                existing.last_seen = contact.last_seen
            else:
                # Add new contact
                contact_map[key] = contact
        
        # Convert to list and sort
        processed = list(contact_map.values())
        processed.sort(key=lambda x: (x.confidence, x.frequency), reverse=True)
        
        return processed
    
    def _calculate_statistics(self, contacts: List[Contact], methods: List[str]) -> Dict:
        """স্ট্যাটিস্টিক্স ক্যালকুলেট করুন"""
        stats = {
            'total_contacts': len(contacts),
            'emails': len([c for c in contacts if c.type == 'email']),
            'phones': len([c for c in contacts if c.type == 'phone']),
            'methods_used': len(methods),
            'top_sources': [],
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }
        
        if contacts:
            # Source frequency
            source_counts = {}
            for contact in contacts:
                source_counts[contact.source] = source_counts.get(contact.source, 0) + 1
            
            stats['top_sources'] = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Confidence distribution
            for contact in contacts:
                if contact.confidence >= 80:
                    stats['confidence_distribution']['high'] += 1
                elif contact.confidence >= 50:
                    stats['confidence_distribution']['medium'] += 1
                else:
                    stats['confidence_distribution']['low'] += 1
        
        return stats
    
    def _calculate_confidence(self, contacts: List[Contact]) -> float:
        """কনফিডেন্স স্কোর ক্যালকুলেট করুন"""
        if not contacts:
            return 0
        
        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0
        
        for contact in contacts[:5]:  # Consider top 5 contacts
            weight = min(contact.frequency, 5)  # Cap frequency weight at 5
            weighted_sum += contact.confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            confidence = weighted_sum / total_weight
        else:
            confidence = sum(c.confidence for c in contacts[:3]) / min(3, len(contacts))
        
        return round(min(confidence, 100), 1)
    
    def _generate_recommendations(self, contacts: List[Contact], profile: ProfileInfo) -> List[str]:
        """রিকমেন্ডেশন জেনারেট করুন"""
        recommendations = []
        
        if not contacts:
            recommendations = [
                "No contacts found via automated methods",
                "Try Facebook's official recovery process",
                "Check all your email accounts for Facebook messages",
                "Contact Facebook support with government ID",
                "Use Facebook's 'Trusted Contacts' feature if set up"
            ]
            return recommendations
        
        # Top contact recommendations
        top_email = next((c for c in contacts if c.type == 'email' and c.confidence >= 70), None)
        top_phone = next((c for c in contacts if c.type == 'phone' and c.confidence >= 75), None)
        
        if top_email:
            recommendations.append(f"Try logging in with email: {top_email.value}")
        
        if top_phone:
            recommendations.append(f"Try logging in with phone: {top_phone.value}")
        
        if top_email and top_phone:
            recommendations.append("Try email and phone combinations")
        
        # General recommendations
        recommendations.extend([
            "Visit: https://facebook.com/login/identify",
            "Check spam/junk folders in all email accounts",
            "Try password reset with each contact found",
            "Use different browsers or devices"
        ])
        
        # If high confidence contacts found
        high_confidence = [c for c in contacts if c.confidence >= 80]
        if len(high_confidence) >= 2:
            recommendations.append("Multiple high-confidence contacts found - try them all")
        
        # Security reminder
        recommendations.append("USE ONLY FOR YOUR ACCOUNT RECOVERY")
        
        return recommendations[:6]  # Limit to 6 recommendations

# ==================== RATE LIMITER ====================
class RateLimiter:
    """রেট লিমিটার"""
    
    def __init__(self):
        self.last_request = 0
        self.min_delay = 1.0  # Minimum delay between requests
    
    def wait(self):
        """অপেক্ষা করুন"""
        current_time = time.time()
        elapsed = current_time - self.last_request
        
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed
            time.sleep(sleep_time)
        
        self.last_request = time.time()

# ==================== REPORT GENERATOR ====================
class ReportGenerator:
    """রিপোর্ট জেনারেটর"""
    
    @staticmethod
    def generate(report: ExtractionReport, format: str = 'all'):
        """রিপোর্ট জেনারেট করুন"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target = re.sub(r'[^\w\-_]', '_', report.target)[:50]
        base_name = f"marpd_report_{timestamp}_{safe_target}"
        
        reports = {}
        
        if format in ['all', 'json']:
            json_file = f"{base_name}.json"
            ReportGenerator._save_json(report, json_file)
            reports['json'] = json_file
        
        if format in ['all', 'txt']:
            txt_file = f"{base_name}.txt"
            ReportGenerator._save_text(report, txt_file)
            reports['txt'] = txt_file
        
        if format in ['all', 'csv']:
            csv_file = f"{base_name}.csv"
            ReportGenerator._save_csv(report, csv_file)
            reports['csv'] = csv_file
        
        return reports
    
    @staticmethod
    def _save_json(report: ExtractionReport, filename: str):
        """JSON সেভ করুন"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def _save_text(report: ExtractionReport, filename: str):
        """টেক্সট রিপোর্ট সেভ করুন"""
        lines = []
        
        lines.append("=" * 70)
        lines.append(f"MAR-PD ULTIMATE PRO - ACCOUNT RECOVERY REPORT")
        lines.append("=" * 70)
        lines.append(f"Generated: {report.timestamp}")
        lines.append(f"Session ID: {report.session_id}")
        lines.append(f"Target: {report.target}")
        lines.append(f"Confidence Score: {report.confidence_score}/100")
        lines.append("")
        
        # Profile info
        if report.profile:
            lines.append("PROFILE INFORMATION:")
            lines.append("-" * 50)
            if report.profile.uid:
                lines.append(f"UID: {report.profile.uid}")
            if report.profile.username:
                lines.append(f"Username: {report.profile.username}")
            if report.profile.name:
                lines.append(f"Name: {report.profile.name}")
            lines.append(f"URL: {report.profile.url}")
            lines.append("")
        
        # Contacts
        if report.contacts:
            lines.append(f"CONTACTS FOUND ({len(report.contacts)}):")
            lines.append("-" * 50)
            
            # Group by type
            emails = [c for c in report.contacts if c.type == 'email']
            phones = [c for c in report.contacts if c.type == 'phone']
            
            if emails:
                lines.append("\n📧 EMAIL ADDRESSES:")
                for i, email in enumerate(emails[:10], 1):
                    lines.append(f"  {i}. {email.value}")
                    lines.append(f"     Confidence: {email.confidence}% | Source: {email.source}")
                    if email.frequency > 1:
                        lines.append(f"     Found {email.frequency} times")
                    lines.append("")
            
            if phones:
                lines.append("\n📱 PHONE NUMBERS:")
                for i, phone in enumerate(phones[:10], 1):
                    lines.append(f"  {i}. {phone.value}")
                    lines.append(f"     Confidence: {phone.confidence}% | Source: {phone.source}")
                    if phone.frequency > 1:
                        lines.append(f"     Found {phone.frequency} times")
                    lines.append("")
        
        # Statistics
        lines.append("STATISTICS:")
        lines.append("-" * 50)
        lines.append(f"Total Contacts: {report.statistics.get('total_contacts', 0)}")
        lines.append(f"Emails: {report.statistics.get('emails', 0)}")
        lines.append(f"Phones: {report.statistics.get('phones', 0)}")
        lines.append(f"Methods Used: {report.statistics.get('methods_used', 0)}")
        lines.append("")
        
        # Methods
        lines.append("METHODS USED:")
        lines.append("-" * 50)
        for method in report.methods_used:
            lines.append(f"• {method}")
        lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS:")
        lines.append("-" * 50)
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
        
        # Ethical reminder
        lines.append("=" * 70)
        lines.append("ETHICAL USE REMINDER")
        lines.append("=" * 70)
        lines.append("This report is for SELF-ACCOUNT RECOVERY ONLY.")
        lines.append("Do not use for unauthorized access or privacy violations.")
        lines.append("Respect all laws and Facebook's Terms of Service.")
        lines.append("The user is solely responsible for ethical use.")
        lines.append("=" * 70)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    @staticmethod
    def _save_csv(report: ExtractionReport, filename: str):
        """CSV সেভ করুন"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['MAR-PD ULTIMATE PRO - Account Recovery Report'])
            writer.writerow(['Generated', report.timestamp])
            writer.writerow(['Target', report.target])
            writer.writerow(['Confidence Score', f"{report.confidence_score}/100"])
            writer.writerow([])
            
            # Contacts
            writer.writerow(['CONTACTS'])
            writer.writerow(['Type', 'Value', 'Confidence', 'Source', 'Frequency'])
            
            for contact in report.contacts:
                writer.writerow([
                    contact.type.upper(),
                    contact.value,
                    f"{contact.confidence}%",
                    contact.source,
                    contact.frequency
                ])
            
            writer.writerow([])
            
            # Recommendations
            writer.writerow(['RECOMMENDATIONS'])
            for rec in report.recommendations:
                writer.writerow([rec])

# ==================== MAIN APPLICATION ====================
class MARPDProApp:
    """মূল অ্যাপ্লিকেশন"""
    
    def __init__(self):
        self.engine = MARPDProEngine()
        self.setup_directories()
    
    def setup_directories(self):
        """ডিরেক্টরি সেটআপ"""
        dirs = ['reports', 'logs', 'cache']
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def run_interactive(self):
        """ইন্টারেক্টিভ মোড"""
        self._print_banner()
        
        print("\n" + "="*70)
        print("MAR-PD ULTIMATE PRO - Interactive Mode")
        print("="*70)
        
        # Get target
        print("\n📥 Enter Facebook Profile Information:")
        print("\nExamples:")
        print("  • https://facebook.com/username")
        print("  • https://facebook.com/profile.php?id=1000123456789")
        print("  • username (without https://)")
        print("  • 1000123456789 (numeric UID)")
        print()
        
        target = input("🔍 Your input: ").strip()
        
        if not target:
            print("\n❌ No input provided")
            return
        
        print(f"\n✅ Target accepted: {target}")
        print("🚀 Starting advanced extraction...")
        
        try:
            # Run extraction
            start_time = time.time()
            report = self.engine.extract(target)
            elapsed_time = time.time() - start_time
            
            # Display results
            self._display_results(report, elapsed_time)
            
            # Save reports
            self._save_reports(report)
            
            # Show next steps
            self._show_next_steps(report)
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Process interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("\n💡 Try:")
            print("  • Check internet connection")
            print("  • Verify the profile URL/username")
            print("  • Ensure profile is publicly accessible")
    
    def run_batch(self, targets_file: str):
        """ব্যাচ মোড"""
        try:
            with open(targets_file, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
            
            print(f"\n📋 Processing {len(targets)} targets...")
            
            for i, target in enumerate(targets, 1):
                print(f"\n[{i}/{len(targets)}] Processing: {target}")
                
                try:
                    report = self.engine.extract(target)
                    
                    # Save individual report
                    reports = ReportGenerator.generate(report, 'json')
                    print(f"   ✅ Saved: {reports['json']}")
                    
                    time.sleep(2)  # Delay between targets
                    
                except Exception as e:
                    print(f"   ❌ Failed: {str(e)[:50]}")
                    continue
            
            print("\n✅ Batch processing complete!")
            
        except FileNotFoundError:
            print(f"❌ File not found: {targets_file}")
        except Exception as e:
            print(f"❌ Batch processing error: {str(e)}")
    
    def _print_banner(self):
        """ব্যানার প্রিন্ট"""
        banner = """
        ╔══════════════════════════════════════════════════════════════════╗
        ║                    MAR-PD ULTIMATE PRO v5.0                       ║
        ║           Advanced Facebook Account Recovery Tool                ║
        ║                     For Legitimate Use Only                      ║
        ║                                                                  ║
        ║           🔒 Secure | 🔍 Advanced | ✅ Ethical                   ║
        ╚══════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def _display_results(self, report: ExtractionReport, elapsed_time: float):
        """রেজাল্টস ডিসপ্লে"""
        print("\n" + "="*70)
        print("📊 EXTRACTION RESULTS")
        print("="*70)
        
        print(f"\n🎯 Target: {report.target}")
        print(f"⏱️  Time: {elapsed_time:.1f} seconds")
        print(f"📈 Confidence: {report.confidence_score}/100")
        print(f"🔧 Methods: {len(report.methods_used)} used")
        
        if report.contacts:
            print(f"\n📞 Contacts Found: {len(report.contacts)}")
            print("-" * 60)
            
            # Top contacts
            top_contacts = report.contacts[:5]
            
            print("\n🏆 TOP CONTACTS:")
            for i, contact in enumerate(top_contacts, 1):
                icon = "📧" if contact.type == 'email' else "📱"
                print(f"  {i}. {icon} {contact.value}")
                print(f"     Confidence: {contact.confidence}% | Source: {contact.source}")
                if contact.frequency > 1:
                    print(f"     Found {contact.frequency} times")
                print()
        
        else:
            print("\n❌ No contacts found via automated methods")
        
        print("💡 RECOMMENDED ACTIONS:")
        print("-" * 60)
        for i, rec in enumerate(report.recommendations[:3], 1):
            print(f"  {i}. {rec}")
    
    def _save_reports(self, report: ExtractionReport):
        """রিপোর্টস সেভ"""
        print("\n💾 Saving reports...")
        
        try:
            reports = ReportGenerator.generate(report, 'all')
            
            print("✅ Reports saved:")
            for format, filename in reports.items():
                print(f"   • {format.upper()}: {filename}")
                
        except Exception as e:
            print(f"⚠️  Could not save reports: {str(e)}")
    
    def _show_next_steps(self, report: ExtractionReport):
        """পরবর্তী স্টেপস"""
        print("\n" + "="*70)
        print("🚀 NEXT STEPS FOR ACCOUNT RECOVERY")
        print("="*70)
        
        if report.contacts:
            print("\n1. IMMEDIATE ACTION:")
            print("   Go to: https://facebook.com/login/identify")
            print("   Try the top contacts from the report")
            
            print("\n2. IF THAT DOESN'T WORK:")
            print("   • Try all contacts in the report")
            print("   • Check email spam folders")
            print("   • Use different browser/device")
            
            print("\n3. LAST RESORT:")
            print("   • Contact Facebook support")
            print("   • Provide government ID for verification")
            print("   • Use Facebook's 'Trusted Contacts'")
        
        else:
            print("\nNO CONTACTS FOUND - TRY THESE:")
            print("1. Facebook Official Recovery:")
            print("   https://facebook.com/login/identify")
            
            print("\n2. Manual Search:")
            print("   • Search all email accounts for 'Facebook'")
            print("   • Check old phones for saved numbers")
            print("   • Ask friends if they have your contact")
            
            print("\n3. Contact Support:")
            print("   • https://facebook.com/help")
            print("   • Be prepared with ID proof")
        
        print("\n" + "="*70)
        print("⚠️  ETHICAL USE - YOUR RESPONSIBILITY")
        print("="*70)
        print("This tool is for YOUR account recovery ONLY.")
        print("Unauthorized access is illegal and unethical.")
        print("You are responsible for using this tool properly.")

# ==================== COMMAND LINE INTERFACE ====================
def main():
    """মেইন এন্ট্রি পয়েন্ট"""
    parser = argparse.ArgumentParser(
        description='MAR-PD ULTIMATE PRO - Advanced Facebook Account Recovery Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                         # Interactive mode
  %(prog)s -t "facebook.com/username"
  %(prog)s -t "1000123456789"
  %(prog)s --batch targets.txt
  %(prog)s --install               # Install dependencies
        
Ethical Use:
  This tool is STRICTLY for recovering YOUR OWN Facebook account
  when you've lost access. Never use for unauthorized access.
        """
    )
    
    parser.add_argument('-t', '--target', help='Facebook profile URL, username, or UID')
    parser.add_argument('-b', '--batch', help='File containing list of targets (one per line)')
    parser.add_argument('--install', action='store_true', help='Install dependencies')
    parser.add_argument('--version', action='store_true', help='Show version')
    
    args = parser.parse_args()
    
    # Show version
    if args.version:
        print(f"MAR-PD ULTIMATE PRO v{Config.VERSION}")
        print(f"Author: {Config.AUTHOR}")
        return
    
    # Install dependencies
    if args.install:
        install_dependencies()
        return
    
    # Create app instance
    app = MARPDProApp()
    
    # Run based on arguments
    if args.batch:
        app.run_batch(args.batch)
    elif args.target:
        # Quick single target mode
        print(f"\n🎯 Target: {args.target}")
        print("🚀 Starting extraction...\n")
        
        try:
            report = app.engine.extract(args.target)
            reports = ReportGenerator.generate(report, 'json')
            print(f"✅ Report saved: {reports['json']}")
            
            # Show summary
            if report.contacts:
                print(f"\n📊 Found {len(report.contacts)} contacts")
                print(f"📈 Confidence: {report.confidence_score}/100")
                
                top_email = next((c for c in report.contacts if c.type == 'email'), None)
                top_phone = next((c for c in report.contacts if c.type == 'phone'), None)
                
                if top_email:
                    print(f"📧 Top email: {top_email.value} ({top_email.confidence}%)")
                if top_phone:
                    print(f"📱 Top phone: {top_phone.value} ({top_phone.confidence}%)")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        # Interactive mode
        app.run_interactive()

def install_dependencies():
    """ডিপেন্ডেন্সি ইনস্টল"""
    print("\n🔧 Installing dependencies...")
    
    try:
        import subprocess
        import sys
        
        dependencies = [
            'requests',
            'beautifulsoup4',
            'lxml',
            'pycryptodome'  # For encryption
        ]
        
        for dep in dependencies:
            print(f"  Installing {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
        
        print("\n✅ All dependencies installed!")
        print("\n📁 Creating directories...")
        
        # Create directories
        for dir_path in ['reports', 'logs', 'cache']:
            os.makedirs(dir_path, exist_ok=True)
            print(f"  Created: {dir_path}/")
        
        print("\n🎉 MAR-PD ULTIMATE PRO is ready to use!")
        print("\nRun: python marpd_pro.py")
        
    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        print("\n💡 Try manual installation:")
        print("  pip install requests beautifulsoup4 lxml pycryptodome")

# ==================== EXECUTION ====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 MAR-PD ULTIMATE PRO stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print("\n💡 Try:")
        print("  • Running with --install flag")
        print("  • Checking Python version (3.7+ required)")
        print("  • Verifying internet connection")