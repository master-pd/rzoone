#!/usr/bin/env python3
"""
MAR-PD ULTIMATE v4.0
Multi-Algorithmic Reconnaissance - Profile Decoder
COMPLETE SINGLE FILE SOLUTION
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
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set, Any
from urllib.parse import urlparse, parse_qs, quote, urljoin
import requests
from bs4 import BeautifulSoup
import threading
from queue import Queue
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== CONFIGURATION ====================
CONFIG = {
    "APP_NAME": "MAR-PD ULTIMATE",
    "VERSION": "4.0",
    "AUTHOR": "Master",
    "DESCRIPTION": "Complete Facebook Account Recovery Tool",
    
    "SETTINGS": {
        "REQUEST_TIMEOUT": 25,
        "DELAY_BETWEEN_REQUESTS": 1.2,
        "MAX_RETRIES": 3,
        "MAX_THREADS": 2,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
    
    "PATTERNS": {
        "BD_PHONE": r'(?:\+?88)?01[3-9]\d{8}',
        "INTERNATIONAL_PHONE": r'\+?88?01[3-9]\d{8}',
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "FACEBOOK_UID": r'\d{9,}',
        "FACEBOOK_USERNAME": r'[a-zA-Z0-9.]+',
        "PROFILE_URL": r'facebook\.com/(?:profile\.php\?id=(\d+)|([^/?]+))'
    },
    
    "BD_DATA": {
        "OPERATORS": {
            "Grameenphone": ["013", "017"],
            "Robi": ["018", "016"], 
            "Banglalink": ["019", "014"],
            "Airtel": ["015"],
            "Teletalk": ["013"]
        },
        "DOMAINS": ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "live.com"]
    }
}

# ==================== DATA STRUCTURES ====================
@dataclass
class ContactInfo:
    """কন্ট্যাক্ট ইনফো ডাটা স্ট্রাকচার"""
    value: str
    type: str  # email or phone
    source: str
    confidence: int
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)

@dataclass 
class ExtractionResult:
    """এক্সট্রাকশন রেজাল্ট"""
    success: bool
    target: str
    contacts: List[ContactInfo]
    methods_used: List[str]
    confidence_score: float
    recommendations: List[str]
    timestamp: str
    
    def to_dict(self):
        result = asdict(self)
        result['contacts'] = [contact.to_dict() for contact in self.contacts]
        return result

# ==================== UTILITY FUNCTIONS ====================
def print_banner():
    """ব্যানার প্রিন্ট করুন"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                   MAR-PD ULTIMATE v4.0                        ║
    ║         Multi-Algorithmic Reconnaissance Tool                ║
    ║           Facebook Account Recovery Solution                 ║
    ║                                                              ║
    ║                 ⚠️  FOR PERSONAL USE ONLY ⚠️                 ║
    ║               Only recover YOUR OWN accounts                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def setup_directories():
    """ডিরেক্টরি সেটআপ করুন"""
    dirs = ['data', 'results', 'results/exports', 'results/logs', 'data/cache']
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("✓ Directory structure created")

def validate_input(target: str) -> bool:
    """ইনপুট ভ্যালিডেশন"""
    patterns = [
        r'facebook\.com/',
        r'fb\.com/',
        r'profile\.php\?id=\d+',
        r'^\d{9,}$',
        r'^[a-zA-Z0-9\.]+$'
    ]
    
    for pattern in patterns:
        if re.search(pattern, target):
            return True
    
    return False

def extract_identifier(target: str) -> Tuple[Optional[str], Optional[str]]:
    """টার্গেট থেকে আইডেন্টিফায়ার এক্সট্র্যাক্ট করুন"""
    uid = None
    username = None
    
    # Case 1: Direct numeric UID
    if target.isdigit() and len(target) > 8:
        uid = target
    
    # Case 2: URL with profile.php
    elif 'profile.php?id=' in target:
        match = re.search(r'id=(\d+)', target)
        if match:
            uid = match.group(1)
    
    # Case 3: URL with username
    elif 'facebook.com/' in target:
        match = re.search(r'facebook\.com/([^/?]+)', target)
        if match:
            username = match.group(1)
            if username == 'profile.php':
                # Handle profile.php without id
                return None, None
    
    # Case 4: Just username
    elif not target.isdigit() and '.' not in target:
        username = target
    
    return uid, username

# ==================== CORE EXTRACTION ENGINE ====================
class MARPDUltimate:
    """MAR-PD ULTIMATE মূল ইঞ্জিন"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG['SETTINGS']['USER_AGENT'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.results = []
        self.methods_used = []
        
        # Ethical agreement
        self._ethical_agreement()
    
    def _ethical_agreement(self):
        """নৈতিক চুক্তি"""
        agreement = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                     ETHICAL USE AGREEMENT                     ║
        ╠══════════════════════════════════════════════════════════════╣
        ║                                                              ║
        ║  This tool is STRICTLY for recovering YOUR OWN Facebook      ║
        ║  account when you've lost access to it.                      ║
        ║                                                              ║
        ║  BY USING THIS TOOL, YOU AGREE TO:                           ║
        ║  1. Use only for YOUR account recovery                       ║
        ║  2. Never access others' accounts                            ║
        ║  3. Respect privacy and laws                                 ║
        ║  4. Follow Facebook's Terms of Service                       ║
        ║                                                              ║
        ║  VIOLATION MAY RESULT IN:                                    ║
        ║  • Legal consequences                                        ║
        ║  • Account suspension                                        ║
        ║  • Criminal charges                                          ║
        ║                                                              ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        
        print(agreement)
        
        agree = input("\nDo you agree to use this tool ONLY for YOUR account recovery? (yes/no): ")
        if agree.lower() != 'yes':
            print("\n❌ Agreement not accepted. Exiting...")
            sys.exit(0)
        
        print("\n✓ Ethical agreement accepted")
        print("✓ Starting MAR-PD ULTIMATE...\n")
    
    def extract_contacts(self, target: str) -> ExtractionResult:
        """মূল কন্ট্যাক্ট এক্সট্র্যাকশন"""
        print(f"\n🎯 Target: {target}")
        print("⏳ Starting extraction process...\n")
        
        # Parse target
        uid, username = extract_identifier(target)
        
        if not uid and not username:
            return ExtractionResult(
                success=False,
                target=target,
                contacts=[],
                methods_used=[],
                confidence_score=0,
                recommendations=["Invalid target format"],
                timestamp=datetime.now().isoformat()
            )
        
        identifier = uid or username
        print(f"✓ Identifier: {identifier} ({'UID' if uid else 'Username'})")
        
        # Run all extraction methods
        all_contacts = self._run_all_methods(identifier, uid, username)
        
        # Process and score contacts
        processed_contacts = self._process_contacts(all_contacts)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(processed_contacts)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(processed_contacts)
        
        # Create result
        result = ExtractionResult(
            success=len(processed_contacts) > 0,
            target=target,
            contacts=processed_contacts,
            methods_used=self.methods_used,
            confidence_score=confidence,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        return result
    
    def _run_all_methods(self, identifier: str, uid: Optional[str], username: Optional[str]) -> List[ContactInfo]:
        """সব মেথড রান করুন"""
        all_contacts = []
        
        methods = [
            (self._method_basic_profile, "Basic Profile Scan"),
            (self._method_about_page, "About Page Analysis"),
            (self._method_mobile_site, "Mobile Site Scan"),
            (self._method_graphql, "GraphQL Analysis"),
            (self._method_contact_point, "Contact Point Check"),
            (self._method_security_hints, "Security Hints"),
            (self._method_public_records, "Public Records"),
            (self._method_backup_sources, "Backup Sources")
        ]
        
        for method, method_name in methods:
            try:
                print(f"  ↳ Running: {method_name}...")
                
                contacts = method(identifier, uid, username)
                if contacts:
                    all_contacts.extend(contacts)
                    self.methods_used.append(method_name)
                    print(f"    ✓ Found {len(contacts)} contacts")
                
                time.sleep(CONFIG['SETTINGS']['DELAY_BETWEEN_REQUESTS'])
                
            except Exception as e:
                print(f"    ✗ {method_name} failed: {str(e)[:50]}")
                continue
        
        return all_contacts
    
    def _method_basic_profile(self, identifier: str, uid: Optional[str], username: Optional[str]) -> List[ContactInfo]:
        """বেসিক প্রোফাইল স্ক্যান"""
        contacts = []
        
        try:
            # Build URL
            if uid:
                url = f"https://www.facebook.com/profile.php?id={uid}"
            else:
                url = f"https://www.facebook.com/{username}"
            
            response = self.session.get(url, timeout=CONFIG['SETTINGS']['REQUEST_TIMEOUT'])
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Extract emails
                emails = re.findall(CONFIG['PATTERNS']['EMAIL'], text, re.IGNORECASE)
                for email in emails:
                    if self._is_valid_email(email):
                        contacts.append(ContactInfo(
                            value=email.lower(),
                            type='email',
                            source='basic_profile',
                            confidence=60,
                            metadata={'page': 'main_profile'}
                        ))
                
                # Extract phones
                phones = re.findall(CONFIG['PATTERNS']['BD_PHONE'], text)
                for phone in phones:
                    clean_phone = self._clean_phone(phone)
                    if clean_phone:
                        contacts.append(ContactInfo(
                            value=clean_phone,
                            type='phone',
                            source='basic_profile',
                            confidence=65,
                            metadata={'page': 'main_profile'}
                        ))
        
        except Exception as e:
            pass
        
        return contacts
    
    def _method_about_page(self, identifier: str, uid: Optional[str], username: Optional[str]) -> List[ContactInfo]:
        """About পেজ এনালাইসিস"""
        contacts = []
        
        try:
            if uid:
                url = f"https://www.facebook.com/profile.php?id={uid}&sk=about"
            else:
                url = f"https://www.facebook.com/{username}/about"
            
            response = self.session.get(url, timeout=CONFIG['SETTINGS']['REQUEST_TIMEOUT'])
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for contact sections
                contact_sections = soup.find_all(text=re.compile(r'contact|email|phone|number', re.IGNORECASE))
                
                for section in contact_sections:
                    parent = section.parent
                    if parent:
                        text = parent.get_text()
                        
                        # Emails
                        emails = re.findall(CONFIG['PATTERNS']['EMAIL'], text, re.IGNORECASE)
                        for email in emails:
                            if self._is_valid_email(email):
                                contacts.append(ContactInfo(
                                    value=email.lower(),
                                    type='email',
                                    source='about_page',
                                    confidence=70,
                                    metadata={'section': 'about'}
                                ))
                        
                        # Phones
                        phones = re.findall(CONFIG['PATTERNS']['BD_PHONE'], text)
                        for phone in phones:
                            clean_phone = self._clean_phone(phone)
                            if clean_phone:
                                contacts.append(ContactInfo(
                                    value=clean_phone,
                                    type='phone',
                                    source='about_page',
                                    confidence=75,
                                    metadata={'section': 'about'}
                                ))
        
        except Exception as e:
            pass
        
        return contacts
    
    def _method_mobile_site(self, identifier: str, uid: Optional[str], username: Optional[str]) -> List[ContactInfo]:
        """মোবাইল সাইট স্ক্যান"""
        contacts = []
        
        try:
            if uid:
                url = f"https://m.facebook.com/profile.php?id={uid}"
            else:
                url = f"https://m.facebook.com/{username}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=CONFIG['SETTINGS']['REQUEST_TIMEOUT'])
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Mobile often shows contact info differently
                emails = re.findall(CONFIG['PATTERNS']['EMAIL'], text, re.IGNORECASE)
                for email in emails:
                    if self._is_valid_email(email):
                        contacts.append(ContactInfo(
                            value=email.lower(),
                            type='email',
                            source='mobile_site',
                            confidence=65,
                            metadata={'site': 'mobile'}
                        ))
                
                phones = re.findall(CONFIG['PATTERNS']['BD_PHONE'], text)
                for phone in phones:
                    clean_phone = self._clean_phone(phone)
                    if clean_phone:
                        contacts.append(ContactInfo(
                            value=clean_phone,
                            type='phone',
                            source='mobile_site',
                            confidence=70,
                            metadata={'site': 'mobile'}
                        ))
        
        except Exception as e:
            pass
        
        return contacts
    
    def _method_graphql(self, identifier: str, uid: Optional[str], username: Optional[str]) -> List[ContactInfo]:
        """GraphQL এনালাইসিস"""
        contacts = []
        
        try:
            # Try common GraphQL endpoints
            endpoints = [
                'https://www.facebook.com/api/graphql/',
                'https://web.facebook.com/api/graphql/'
            ]
            
            for endpoint in endpoints:
                try:
                    headers = {
                        'User-Agent': CONFIG['SETTINGS']['USER_AGENT'],
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'https://www.facebook.com',
                        'Referer': f'https://www.facebook.com/{identifier}'
                    }
                    
                    data = {
                        'variables': json.dumps({'userID': identifier}),
                        'doc_id': '3315274998225349'  # Common user query
                    }
                    
                    response = requests.post(endpoint, headers=headers, data=data, timeout=15)
                    
                    if response.status_code == 200:
                        response_text = response.text
                        
                        # Extract from JSON response
                        emails = re.findall(CONFIG['PATTERNS']['EMAIL'], response_text, re.IGNORECASE)
                        for email in emails:
                            if self._is_valid_email(email):
                                contacts.append(ContactInfo(
                                    value=email.lower(),
                                    type='email',
                                    source='graphql',
                                    confidence=80,
                                    metadata={'endpoint': endpoint}
                                ))
                        
                        phones = re.findall(CONFIG['PATTERNS']['BD_PHONE'], response_text)
                        for phone in phones:
                            clean_phone = self._clean_phone(phone)
                            if clean_phone:
                                contacts.append(ContactInfo(
                                    value=clean_phone,
                                    type='phone',
                                    source='graphql',
                                    confidence=85,
                                    metadata={'endpoint': endpoint}
                                ))
                        
                        break
                        
                except:
                    continue
        
        except Exception as e:
            pass
        
        return contacts
    
    def _method_contact_point(self, identifier: str, uid: Optional[str], username: Optional[str]) -> List[ContactInfo]:
        """কন্ট্যাক্ট পয়েন্ট চেক"""
        contacts = []
        
        try:
            if uid:
                url = f"https://www.facebook.com/profile.php?id={uid}&sk=info"
            else:
                url = f"https://www.facebook.com/{username}/info"
            
            response = self.session.get(url, timeout=CONFIG['SETTINGS']['REQUEST_TIMEOUT'])
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Contact info page
                emails = re.findall(CONFIG['PATTERNS']['EMAIL'], text, re.IGNORECASE)
                for email in emails:
                    if self._is_valid_email(email):
                        contacts.append(ContactInfo(
                            value=email.lower(),
                            type='email',
                            source='contact_point',
                            confidence=75,
                            metadata={'page': 'info'}
                        ))
                
                phones = re.findall(CONFIG['PATTERNS']['BD_PHONE'], text)
                for phone in phones:
                    clean_phone = self._clean_phone(phone)
                    if clean_phone:
                        contacts.append(ContactInfo(
                            value=clean_phone,
                            type='phone',
                            source='contact_point',
                            confidence=80,
                            metadata={'page': 'info'}
                        ))
        
        except Exception as e:
            pass
        
        return contacts
    
    def _method_security_hints(self, identifier: str, uid: Optional[str], username: Optional[str]) -> List[ContactInfo]:
        """সিকিউরিটি হিন্টস"""
        contacts = []
        
        try:
            # Try security/recovery related pages
            urls = [
                f"https://www.facebook.com/{identifier}/settings",
                f"https://www.facebook.com/recover"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text = soup.get_text()
                        
                        # Look for security/recovery hints
                        if 'recovery' in text.lower() or 'security' in text.lower():
                            emails = re.findall(CONFIG['PATTERNS']['EMAIL'], text, re.IGNORECASE)
                            for email in emails:
                                if self._is_valid_email(email):
                                    contacts.append(ContactInfo(
                                        value=email.lower(),
                                        type='email',
                                        source='security_hints',
                                        confidence=85,
                                        metadata={'page': url}
                                    ))
                            
                            phones = re.findall(CONFIG['PATTERNS']['BD_PHONE'], text)
                            for phone in phones:
                                clean_phone = self._clean_phone(phone)
                                if clean_phone:
                                    contacts.append(ContactInfo(
                                        value=clean_phone,
                                        type='phone',
                                        source='security_hints',
                                        confidence=90,
                                        metadata={'page': url}
                                    ))
                    
                    time.sleep(1)
                    
                except:
                    continue
        
        except Exception as e:
            pass
        
        return contacts
    
    def _method_public_records(self, identifier: str, uid: Optional[str], username: Optional[str]) -> List[ContactInfo]:
        """পাবলিক রেকর্ডস"""
        contacts = []
        
        try:
            # Search engine lookups
            if username:
                search_queries = [
                    f'"{username}" email',
                    f'"{username}" contact',
                    f'"{username}" phone'
                ]
                
                for query in search_queries:
                    try:
                        # Simulate search (limited)
                        search_url = "https://www.google.com/search"
                        params = {'q': query}
                        
                        response = requests.get(search_url, params=params, timeout=15)
                        
                        if response.status_code == 200:
                            text = response.text
                            
                            emails = re.findall(CONFIG['PATTERNS']['EMAIL'], text, re.IGNORECASE)
                            for email in emails:
                                if self._is_valid_email(email) and username.lower() in email.lower():
                                    contacts.append(ContactInfo(
                                        value=email.lower(),
                                        type='email',
                                        source='public_records',
                                        confidence=50,
                                        metadata={'query': query}
                                    ))
                        
                        time.sleep(2)
                        
                    except:
                        continue
        
        except Exception as e:
            pass
        
        return contacts
    
    def _method_backup_sources(self, identifier: str, uid: Optional[str], username: Optional[str]) -> List[ContactInfo]:
        """ব্যাকআপ সোর্সেস"""
        contacts = []
        
        try:
            # Check alternative Facebook domains
            domains = [
                ('https://web.facebook.com/', 'web_facebook'),
                ('https://mbasic.facebook.com/', 'mbasic_facebook'),
                ('https://touch.facebook.com/', 'touch_facebook')
            ]
            
            for base_url, source_name in domains:
                try:
                    if uid:
                        url = f"{base_url}profile.php?id={uid}"
                    else:
                        url = f"{base_url}{username}"
                    
                    response = requests.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        text = response.text
                        
                        emails = re.findall(CONFIG['PATTERNS']['EMAIL'], text, re.IGNORECASE)
                        for email in emails:
                            if self._is_valid_email(email):
                                contacts.append(ContactInfo(
                                    value=email.lower(),
                                    type='email',
                                    source=f'backup_{source_name}',
                                    confidence=55,
                                    metadata={'domain': base_url}
                                ))
                        
                        phones = re.findall(CONFIG['PATTERNS']['BD_PHONE'], text)
                        for phone in phones:
                            clean_phone = self._clean_phone(phone)
                            if clean_phone:
                                contacts.append(ContactInfo(
                                    value=clean_phone,
                                    type='phone',
                                    source=f'backup_{source_name}',
                                    confidence=60,
                                    metadata={'domain': base_url}
                                ))
                    
                    time.sleep(1)
                    
                except:
                    continue
        
        except Exception as e:
            pass
        
        return contacts
    
    def _is_valid_email(self, email: str) -> bool:
        """ইমেইল ভ্যালিডেশন"""
        email = email.lower().strip()
        
        # Basic regex check
        if not re.match(CONFIG['PATTERNS']['EMAIL'], email):
            return False
        
        # Invalid patterns
        invalid_patterns = [
            'example.com',
            'test.com',
            'domain.com',
            'email.com',
            'mail.com$'
        ]
        
        for pattern in invalid_patterns:
            if pattern in email:
                return False
        
        # Valid domain check
        domain = email.split('@')[1] if '@' in email else ''
        if domain in CONFIG['BD_DATA']['DOMAINS']:
            return True
        
        return True  # Allow other domains
    
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
            return f"0{digits}"  # Add leading 0
        
        return None
    
    def _process_contacts(self, contacts: List[ContactInfo]) -> List[ContactInfo]:
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
        
        # Sort by confidence (highest first)
        unique_contacts.sort(key=lambda x: x.confidence, reverse=True)
        
        # Adjust confidence based on frequency
        contact_counts = {}
        for contact in unique_contacts:
            if contact.value in contact_counts:
                contact_counts[contact.value] += 1
            else:
                contact_counts[contact.value] = 1
        
        # Boost confidence for frequently found contacts
        for contact in unique_contacts:
            count = contact_counts.get(contact.value, 1)
            if count > 1:
                contact.confidence = min(100, contact.confidence + (count * 5))
        
        return unique_contacts
    
    def _calculate_confidence(self, contacts: List[ContactInfo]) -> float:
        """কনফিডেন্স স্কোর ক্যালকুলেট করুন"""
        if not contacts:
            return 0
        
        # Average confidence of top 3 contacts
        top_contacts = contacts[:3]
        avg_confidence = sum(c.confidence for c in top_contacts) / len(top_contacts)
        
        # Adjust based on number of sources
        unique_sources = len(set(c.source for c in contacts))
        source_bonus = min(20, unique_sources * 5)
        
        final_confidence = min(100, avg_confidence + source_bonus)
        
        return round(final_confidence, 1)
    
    def _generate_recommendations(self, contacts: List[ContactInfo]) -> List[str]:
        """রিকমেন্ডেশন জেনারেট করুন"""
        recommendations = []
        
        if not contacts:
            recommendations.extend([
                "No contacts found via automated methods",
                "Try Facebook's official recovery: https://facebook.com/login/identify",
                "Check your email for Facebook recovery emails",
                "Contact Facebook support with ID proof"
            ])
            return recommendations
        
        # Top recommendations based on contacts
        top_email = None
        top_phone = None
        
        for contact in contacts:
            if contact.type == 'email' and not top_email:
                top_email = contact
            elif contact.type == 'phone' and not top_phone:
                top_phone = contact
            
            if top_email and top_phone:
                break
        
        if top_email:
            recommendations.append(f"Try logging in with email: {top_email.value}")
        
        if top_phone:
            recommendations.append(f"Try logging in with phone: {top_phone.value}")
        
        if top_email and top_phone:
            recommendations.append("Try both email and phone combinations")
        
        # General recommendations
        recommendations.extend([
            "Use Facebook's official recovery if above doesn't work",
            "Check spam folder for Facebook recovery emails",
            "Try account recovery with trusted contacts",
            "Contact Facebook support as last resort"
        ])
        
        # Ethical reminder
        recommendations.append("USE ONLY FOR YOUR ACCOUNT RECOVERY")
        
        return recommendations[:5]  # Limit to 5 recommendations

# ==================== MAIN APPLICATION ====================
class MARPDApplication:
    """মূল অ্যাপ্লিকেশন"""
    
    def __init__(self):
        self.extractor = MARPDUltimate()
        setup_directories()
    
    def run(self):
        """অ্যাপ্লিকেশন রান করুন"""
        print_banner()
        
        # Get target
        print("\n📥 Enter Facebook Profile Information:")
        print("   Examples:")
        print("   • https://facebook.com/username")
        print("   • https://facebook.com/profile.php?id=1000123456789")
        print("   • username (without URL)")
        print("   • 1000123456789 (numeric UID)")
        print()
        
        target = input("🔍 Your input: ").strip()
        
        if not target:
            print("\n❌ No input provided")
            return
        
        if not validate_input(target):
            print("\n❌ Invalid input format")
            print("   Please enter a valid Facebook URL, username, or UID")
            return
        
        # Run extraction
        print("\n" + "="*60)
        print("🚀 Starting MAR-PD ULTIMATE Extraction")
        print("="*60 + "\n")
        
        start_time = time.time()
        
        try:
            result = self.extractor.extract_contacts(target)
            elapsed_time = time.time() - start_time
            
            # Display results
            self._display_results(result, elapsed_time)
            
            # Save results
            self._save_results(result)
            
            # Show next steps
            self._show_next_steps(result)
            
        except KeyboardInterrupt:
            print("\n\n❌ Process interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    def _display_results(self, result: ExtractionResult, elapsed_time: float):
        """রেজাল্টস ডিসপ্লে করুন"""
        print("\n" + "="*60)
        print("📊 EXTRACTION RESULTS")
        print("="*60)
        
        print(f"\n🎯 Target: {result.target}")
        print(f"⏱️  Time taken: {elapsed_time:.1f} seconds")
        print(f"✅ Success: {'Yes' if result.success else 'No'}")
        print(f"📈 Confidence Score: {result.confidence_score}/100")
        print(f"🔧 Methods Used: {', '.join(result.methods_used)}")
        
        if result.contacts:
            print(f"\n📞 CONTACTS FOUND ({len(result.contacts)}):")
            print("-" * 50)
            
            # Group by type
            emails = [c for c in result.contacts if c.type == 'email']
            phones = [c for c in result.contacts if c.type == 'phone']
            
            if emails:
                print("\n📧 Email Addresses:")
                for i, email in enumerate(emails[:5], 1):  # Show top 5
                    print(f"  {i}. {email.value} (Confidence: {email.confidence}%)")
                    print(f"     Source: {email.source}")
            
            if phones:
                print("\n📱 Phone Numbers:")
                for i, phone in enumerate(phones[:5], 1):  # Show top 5
                    print(f"  {i}. {phone.value} (Confidence: {phone.confidence}%)")
                    print(f"     Source: {phone.source}")
        
        else:
            print("\n❌ No contacts found")
        
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 50)
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")
    
    def _save_results(self, result: ExtractionResult):
        """রেজাল্টস সেভ করুন"""
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_target = re.sub(r'[^\w\-_]', '_', result.target)[:50]
            filename = f"results/exports/{timestamp}_{safe_target}"
            
            # Save as JSON
            json_file = f"{filename}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Save as text report
            txt_file = f"{filename}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(self._generate_text_report(result))
            
            print(f"\n💾 Results saved to:")
            print(f"   JSON: {json_file}")
            print(f"   Text: {txt_file}")
            
        except Exception as e:
            print(f"\n⚠️  Could not save results: {str(e)}")
    
    def _generate_text_report(self, result: ExtractionResult) -> str:
        """টেক্সট রিপোর্ট জেনারেট করুন"""
        report = []
        
        report.append("=" * 60)
        report.append("MAR-PD ULTIMATE - ACCOUNT RECOVERY REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {result.timestamp}")
        report.append(f"Target: {result.target}")
        report.append(f"Confidence Score: {result.confidence_score}/100")
        report.append("")
        
        if result.contacts:
            report.append("CONTACTS FOUND:")
            report.append("-" * 50)
            
            for contact in result.contacts:
                report.append(f"• {contact.value.upper()}")
                report.append(f"  Type: {contact.type}")
                report.append(f"  Source: {contact.source}")
                report.append(f"  Confidence: {contact.confidence}%")
                report.append("")
        
        report.append("METHODS USED:")
        report.append("-" * 50)
        for method in result.methods_used:
            report.append(f"• {method}")
        report.append("")
        
        report.append("RECOMMENDATIONS:")
        report.append("-" * 50)
        for rec in result.recommendations:
            report.append(f"• {rec}")
        report.append("")
        
        report.append("=" * 60)
        report.append("ETHICAL USE REMINDER")
        report.append("=" * 60)
        report.append("This report is for SELF-ACCOUNT RECOVERY ONLY.")
        report.append("Do not use for unauthorized access.")
        report.append("Respect privacy and follow all applicable laws.")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def _show_next_steps(self, result: ExtractionResult):
        """পরবর্তী স্টেপস দেখান"""
        print("\n" + "="*60)
        print("🚀 NEXT STEPS FOR ACCOUNT RECOVERY")
        print("="*60)
        
        if result.contacts:
            print("\n1. TRY LOGGIN WITH TOP CONTACTS:")
            top_email = next((c for c in result.contacts if c.type == 'email'), None)
            top_phone = next((c for c in result.contacts if c.type == 'phone'), None)
            
            if top_email:
                print(f"   • Email: {top_email.value}")
            if top_phone:
                print(f"   • Phone: {top_phone.value}")
            
            print("\n2. GO TO FACEBOOK RECOVERY:")
            print("   https://facebook.com/login/identify")
            
            print("\n3. IF STILL STUCK:")
            print("   • Check email spam folder")
            print("   • Try 'Forgot Password' with each contact")
            print("   • Use Facebook's 'Trusted Contacts' feature")
            print("   • Contact Facebook support with ID proof")
        
        else:
            print("\nNO CONTACTS FOUND - ALTERNATIVE METHODS:")
            print("1. Facebook Official Recovery:")
            print("   https://facebook.com/login/identify")
            
            print("\n2. Search Your Email:")
            print("   • Search: 'facebook' 'recovery' 'account'")
            print("   • Check all email accounts")
            print("   • Look in spam/junk folders")
            
            print("\n3. Contact Facebook Support:")
            print("   • https://facebook.com/help")
            print("   • Provide government ID for verification")
        
        print("\n" + "="*60)
        print("⚠️  REMEMBER: USE ONLY FOR YOUR ACCOUNT")
        print("="*60)

# ==================== QUICK INSTALL SCRIPT ====================
def quick_install():
    """কুইক ইন্সটল স্ক্রিপ্ট"""
    print("\n" + "="*60)
    print("MAR-PD ULTIMATE - Quick Installation")
    print("="*60)
    
    # Check Python
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher required!")
        sys.exit(1)
    
    print("✓ Python version OK")
    
    # Install dependencies
    print("\nInstalling dependencies...")
    dependencies = [
        "requests",
        "beautifulsoup4",
        "lxml"
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ Installed: {dep}")
        except:
            print(f"⚠️  Could not install: {dep}")
    
    # Create directories
    setup_directories()
    
    print("\n" + "="*60)
    print("✅ INSTALLATION COMPLETE!")
    print("="*60)
    print("\nTo run MAR-PD ULTIMATE:")
    print("  python marpd_ultimate.py")
    print("\nOr copy the code and run directly.")
    print("\n⚠️  Use ONLY for your account recovery!")

# ==================== MAIN ENTRY POINT ====================
if __name__ == "__main__":
    # Check if running as install script
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        quick_install()
    else:
        # Run the application
        try:
            app = MARPDApplication()
            app.run()
        except KeyboardInterrupt:
            print("\n\n👋 MAR-PD ULTIMATE stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("\nTry running with: python marpd_ultimate.py --install")