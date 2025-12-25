"""
Security and Recovery Methods
Finding contacts from security/recovery hints
"""

import re
import json
import time
import random
from typing import Dict, List, Optional, Set
import requests
from bs4 import BeautifulSoup

class SecurityRecoveryExtractor:
    """সিকিউরিটি ও রিকভারি মেথডস"""
    
    def __init__(self):
        self.recovery_patterns = {
            'email_patterns': [
                r'recovery[_-]?email',
                r'backup[_-]?email', 
                r'secondary[_-]?email',
                r'alternative[_-]?email',
                r'contact[_-]?email'
            ],
            'phone_patterns': [
                r'recovery[_-]?phone',
                r'backup[_-]?phone',
                r'secondary[_-]?phone',
                r'2fa[_-]?phone',
                r'contact[_-]?phone'
            ]
        }
    
    def extract_security_info(self, uid: str, username: str = None) -> Dict:
        """সিকিউরিটি ইনফো এক্সট্র্যাক্ট করুন"""
        results = {
            'recovery_emails': set(),
            'recovery_phones': set(),
            'security_hints': [],
            'recovery_options': []
        }
        
        methods = [
            self._check_recovery_options,
            self._check_security_settings,
            self._check_login_attempts,
            self._check_account_activity,
            self._check_verification_methods
        ]
        
        print("\n[+] Analyzing security and recovery options...")
        
        for method in methods:
            try:
                print(f"  ↳ Running {method.__name__}...")
                data = method(uid, username)
                
                if data:
                    if 'recovery_emails' in data:
                        results['recovery_emails'].update(data['recovery_emails'])
                    if 'recovery_phones' in data:
                        results['recovery_phones'].update(data['recovery_phones'])
                    if 'security_hints' in data:
                        results['security_hints'].extend(data['security_hints'])
                    if 'recovery_options' in data:
                        results['recovery_options'].extend(data['recovery_options'])
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                continue
        
        # Convert sets to lists
        results['recovery_emails'] = list(results['recovery_emails'])
        results['recovery_phones'] = list(results['recovery_phones'])
        
        return results
    
    def _check_recovery_options(self, uid: str, username: str) -> Optional[Dict]:
        """রিকভারি অপশনস চেক করুন"""
        try:
            # Try Facebook's recovery page
            recovery_url = "https://www.facebook.com/login/identify"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.facebook.com/'
            }
            
            # Simulate recovery flow
            session = requests.Session()
            response = session.get(recovery_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                results = {
                    'recovery_emails': set(),
                    'recovery_phones': set(),
                    'recovery_options': []
                }
                
                # Look for recovery hints
                recovery_elements = soup.find_all(text=re.compile(
                    r'recovery|backup|secondary|alternative|contact',
                    re.IGNORECASE
                ))
                
                for element in recovery_elements:
                    parent = element.parent
                    if parent:
                        text = parent.get_text()
                        
                        # Extract emails
                        emails = re.findall(
                            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                            text,
                            re.IGNORECASE
                        )
                        results['recovery_emails'].update(emails)
                        
                        # Extract phones
                        phones = re.findall(
                            r'(?:\+?88)?01[3-9]\d{8}',
                            text
                        )
                        results['recovery_phones'].update(phones)
                        
                        # Extract recovery options
                        if 'option' in text.lower() or 'method' in text.lower():
                            results['recovery_options'].append(text.strip())
                
                return results if (results['recovery_emails'] or 
                                  results['recovery_phones'] or 
                                  results['recovery_options']) else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_security_settings(self, uid: str, username: str) -> Optional[Dict]:
        """সিকিউরিটি সেটিংস চেক করুন"""
        try:
            # Try to access security settings page
            if username:
                settings_url = f"https://www.facebook.com/{username}/settings"
            else:
                settings_url = f"https://www.facebook.com/profile.php?id={uid}&sk=settings"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(settings_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                results = {
                    'security_hints': [],
                    'recovery_options': []
                }
                
                # Look for security-related sections
                security_terms = [
                    'password',
                    'login',
                    'security',
                    'two-factor',
                    '2fa',
                    'authentication',
                    'recovery',
                    'backup'
                ]
                
                for term in security_terms:
                    elements = soup.find_all(text=re.compile(term, re.IGNORECASE))
                    
                    for element in elements:
                        parent = element.parent
                        if parent:
                            text = parent.get_text()
                            
                            # Check for contact hints
                            if '@' in text:
                                results['security_hints'].append(
                                    f"Security setting mentions email: {text[:100]}..."
                                )
                            elif '01' in text and len(text) > 10:
                                results['security_hints'].append(
                                    f"Security setting mentions phone: {text[:100]}..."
                                )
                            
                            # Check for recovery options
                            if any(word in text.lower() for word in ['recover', 'backup', 'reset']):
                                results['recovery_options'].append(text.strip())
                
                return results if (results['security_hints'] or results['recovery_options']) else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_login_attempts(self, uid: str, username: str) -> Optional[Dict]:
        """লগইন অ্যাটেম্পটস থেকে তথ্য"""
        try:
            # Check for login-related pages
            login_urls = [
                "https://www.facebook.com/login.php",
                "https://www.facebook.com/login/",
                "https://www.facebook.com/recover"
            ]
            
            results = {
                'recovery_emails': set(),
                'recovery_phones': set(),
                'security_hints': []
            }
            
            for url in login_urls:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for email/phone input fields
                        input_fields = soup.find_all('input', {
                            'type': ['email', 'text', 'tel'],
                            'name': re.compile(r'email|phone|contact', re.I)
                        })
                        
                        for field in input_fields:
                            # Check for placeholder hints
                            placeholder = field.get('placeholder', '')
                            value = field.get('value', '')
                            
                            if placeholder:
                                results['security_hints'].append(
                                    f"Login field placeholder: {placeholder}"
                                )
                            
                            if value and '@' in value:
                                results['recovery_emails'].add(value)
                            elif value and re.match(r'^01[3-9]\d{8}$', value):
                                results['recovery_phones'].add(value)
                        
                        time.sleep(1)
                        
                except:
                    continue
            
            return results if (results['recovery_emails'] or 
                              results['recovery_phones'] or 
                              results['security_hints']) else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_account_activity(self, uid: str, username: str) -> Optional[Dict]:
        """অ্যাকাউন্ট অ্যাক্টিভিটি চেক করুন"""
        try:
            # Try activity log page
            if username:
                activity_url = f"https://www.facebook.com/{username}/allactivity"
            else:
                activity_url = f"https://www.facebook.com/profile.php?id={uid}&sk=allactivity"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(activity_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                results = {
                    'security_hints': [],
                    'recovery_options': []
                }
                
                # Look for security-related activities
                activity_elements = soup.find_all('div', class_=re.compile(r'activity|log|history'))
                
                for element in activity_elements[:20]:  # Limit to first 20
                    text = element.get_text().lower()
                    
                    # Check for security events
                    security_events = [
                        'password changed',
                        'login from',
                        'device added',
                        'recovery email',
                        'phone added',
                        'security check'
                    ]
                    
                    for event in security_events:
                        if event in text:
                            results['security_hints'].append(
                                f"Security event found: {event}"
                            )
                            
                            # Extract potential contact info from context
                            parent_text = element.parent.get_text() if element.parent else ''
                            if '@' in parent_text:
                                emails = re.findall(
                                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                                    parent_text,
                                    re.IGNORECASE
                                )
                                if emails:
                                    results['security_hints'].append(
                                        f"Associated email in security event: {emails[0]}"
                                    )
                
                return results if results['security_hints'] else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_verification_methods(self, uid: str, username: str) -> Optional[Dict]:
        """ভেরিফিকেশন মেথডস চেক করুন"""
        try:
            # Try verification/recovery endpoints
            verification_urls = [
                "https://www.facebook.com/confirmemail.php",
                "https://www.facebook.com/checkpoint",
                "https://www.facebook.com/identity/confirm"
            ]
            
            results = {
                'recovery_emails': set(),
                'recovery_phones': set(),
                'recovery_options': []
            }
            
            for url in verification_urls:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://www.facebook.com/'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for verification hints
                        verification_text = soup.find_all(text=re.compile(
                            r'verify|confirm|authenticate|recover|reset',
                            re.IGNORECASE
                        ))
                        
                        for text_element in verification_text:
                            text = text_element.strip()
                            
                            # Check for email/phone in verification context
                            if '@' in text:
                                emails = re.findall(
                                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                                    text,
                                    re.IGNORECASE
                                )
                                results['recovery_emails'].update(emails)
                            
                            if '01' in text and len(text) > 10:
                                phones = re.findall(
                                    r'(?:\+?88)?01[3-9]\d{8}',
                                    text
                                )
                                results['recovery_phones'].update(phones)
                            
                            # Extract recovery options
                            if any(word in text.lower() for word in ['option', 'method', 'way']):
                                results['recovery_options'].append(text)
                        
                        time.sleep(1)
                        
                except:
                    continue
            
            return results if (results['recovery_emails'] or 
                              results['recovery_phones'] or 
                              results['recovery_options']) else None
        
        except Exception as e:
            pass
        
        return None