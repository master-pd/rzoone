"""
Advanced Contact Extraction Methods
60+ Techniques for Finding Registration Contacts
"""

import re
import json
import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple, Set
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

class ContactExtractor:
    """advance contact extension """
    
    def __init__(self):
        self.methods = [
            self.method_profile_html,
            self.method_about_section,
            self.method_mobile_site,
            self.method_graphql_leak,
            self.method_contact_point,
            self.method_work_education,
            self.method_friends_contacts,
            self.method_photos_metadata,
            self.method_groups_membership,
            self.method_events_participation,
            self.method_messenger_hints,
            self.method_backup_data,
            self.method_recovery_options,
            self.method_security_settings,
            self.method_login_activity
        ]
        
        # BD specific patterns
        self.bd_patterns = {
            'phone_full': r'(\+?88)?01[3-9]\d{8}',
            'phone_short': r'01[3-9]\d{8}',
            'operator_codes': ['013', '014', '015', '016', '017', '018', '019']
        }
    
    def extract_all(self, uid: str, username: str = None) -> Dict:
        """continue to all method use """
        all_contacts = {
            'emails': set(),
            'phones': set(),
            'registration_info': {},
            'confidence_score': 0
        }
        
        print("[+] Starting advanced contact extraction...")
        
        for i, method in enumerate(self.methods, 1):
            try:
                print(f"  [{i}/{len(self.methods)}] Running {method.__name__}...")
                
                if 'username' in method.__code__.co_varnames:
                    result = method(uid, username)
                else:
                    result = method(uid)
                
                if result:
                    if 'emails' in result:
                        all_contacts['emails'].update(result['emails'])
                    if 'phones' in result:
                        all_contacts['phones'].update(result['phones'])
                    if 'registration_info' in result:
                        all_contacts['registration_info'].update(result['registration_info'])
                    
                    time.sleep(random.uniform(0.5, 1.5))
                    
            except Exception as e:
                print(f"  [!] Method {method.__name__} failed: {str(e)[:50]}")
                continue
        
        # Convert sets to lists
        all_contacts['emails'] = list(all_contacts['emails'])
        all_contacts['phones'] = list(all_contacts['phones'])
        
        # Calculate confidence score
        all_contacts['confidence_score'] = self._calculate_confidence(all_contacts)
        
        return all_contacts
    
    def method_profile_html(self, uid: str) -> Optional[Dict]:
        """প্রোফাইল HTML থেকে কন্ট্যাক্ট তথ্য"""
        try:
            if uid.isdigit():
                url = f"https://www.facebook.com/profile.php?id={uid}"
            else:
                url = f"https://www.facebook.com/{uid}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                contacts = {'emails': set(), 'phones': set()}
                
                # Find all text content
                text = soup.get_text()
                
                # Extract emails
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, text, re.IGNORECASE)
                contacts['emails'].update(emails)
                
                # Extract BD phones
                phone_pattern = r'(?:\+?88)?01[3-9]\d{8}'
                phones = re.findall(phone_pattern, text)
                contacts['phones'].update(phones)
                
                # Look in meta tags
                for meta in soup.find_all('meta'):
                    content = meta.get('content', '')
                    if '@' in content:
                        emails = re.findall(email_pattern, content, re.IGNORECASE)
                        contacts['emails'].update(emails)
                    if '01' in content and len(content) >= 11:
                        phones = re.findall(phone_pattern, content)
                        contacts['phones'].update(phones)
                
                # Look in script tags (JSON data)
                for script in soup.find_all('script'):
                    if script.string:
                        script_text = script.string
                        # Check for email in script
                        emails = re.findall(email_pattern, script_text, re.IGNORECASE)
                        contacts['emails'].update(emails)
                        
                        # Check for phone in script
                        phones = re.findall(phone_pattern, script_text)
                        contacts['phones'].update(phones)
                
                # Convert sets to lists
                contacts['emails'] = list(contacts['emails'])
                contacts['phones'] = list(contacts['phones'])
                
                return contacts if contacts['emails'] or contacts['phones'] else None
                
        except Exception as e:
            pass
        
        return None
    
    def method_about_section(self, uid: str) -> Optional[Dict]:
        """about """
        try:
            if uid.isdigit():
                url = f"https://www.facebook.com/{uid}/about"
            else:
                url = f"https://www.facebook.com/{uid}/about"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                contacts = {'emails': set(), 'phones': set()}
                
                # Look for contact info sections
                contact_sections = soup.find_all(['div', 'section'], 
                                                class_=re.compile(r'contact|info|details|about'))
                
                for section in contact_sections:
                    section_text = section.get_text()
                    
                    # Extract emails
                    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                                       section_text, re.IGNORECASE)
                    contacts['emails'].update(emails)
                    
                    # Extract phones
                    phones = re.findall(r'(?:\+?88)?01[3-9]\d{8}', section_text)
                    contacts['phones'].update(phones)
                
                # Look for specific contact links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Mailto links
                    if 'mailto:' in href:
                        email = href.replace('mailto:', '').split('?')[0].strip()
                        if '@' in email:
                            contacts['emails'].add(email)
                    
                    # Tel links
                    elif 'tel:' in href:
                        phone = href.replace('tel:', '').strip()
                        if re.match(r'^01[3-9]\d{8}$', phone):
                            contacts['phones'].add(phone)
                
                # Convert sets to lists
                contacts['emails'] = list(contacts['emails'])
                contacts['phones'] = list(contacts['phones'])
                
                return contacts if contacts['emails'] or contacts['phones'] else None
                
        except Exception as e:
            pass
        
        return None
    
    def method_mobile_site(self, uid: str) -> Optional[Dict]:
        """mobile site"""
        try:
            if uid.isdigit():
                url = f"https://m.facebook.com/profile.php?id={uid}"
            else:
                url = f"https://m.facebook.com/{uid}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                contacts = {'emails': set(), 'phones': set()}
                
                # Mobile site often has simpler structure
                # Check for contact info in specific mobile divs
                mobile_divs = soup.find_all('div', id=re.compile(r'contact|mobile|phone|email'))
                
                for div in mobile_divs:
                    div_text = div.get_text()
                    
                    # Extract emails
                    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                                       div_text, re.IGNORECASE)
                    contacts['emails'].update(emails)
                    
                    # Extract phones
                    phones = re.findall(r'(?:\+?88)?01[3-9]\d{8}', div_text)
                    contacts['phones'].update(phones)
                
                # Also check the entire page
                page_text = soup.get_text()
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                                   page_text, re.IGNORECASE)
                contacts['emails'].update(emails)
                
                phones = re.findall(r'(?:\+?88)?01[3-9]\d{8}', page_text)
                contacts['phones'].update(phones)
                
                # Convert sets to lists
                contacts['emails'] = list(contacts['emails'])
                contacts['phones'] = list(contacts['phones'])
                
                return contacts if contacts['emails'] or contacts['phones'] else None
                
        except Exception as e:
            pass
        
        return None
    
    def method_graphql_leak(self, uid: str) -> Optional[Dict]:
        """GraphQL data """
        try:
            # Common GraphQL endpoints
            endpoints = [
                "https://www.facebook.com/api/graphql/",
                "https://graph.facebook.com/v15.0/",
                "https://web.facebook.com/api/graphql/"
            ]
            
            # Common GraphQL queries that might leak contact info
            queries = [
                {"doc_id": "3315274998225349", "vars": {"userID": uid}},  # User query
                {"doc_id": "3581618341890452", "vars": {"id": uid}},      # Profile query
                {"doc_id": "4270752577582839", "vars": {"userID": uid}},  # Contact query
            ]
            
            contacts = {'emails': set(), 'phones': set()}
            
            for endpoint in endpoints:
                for query in queries:
                    try:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Origin': 'https://www.facebook.com',
                            'Referer': f'https://www.facebook.com/{uid}'
                        }
                        
                        data = {
                            'variables': json.dumps(query['vars']),
                            'doc_id': query['doc_id']
                        }
                        
                        response = requests.post(endpoint, data=data, headers=headers, timeout=15)
                        
                        if response.status_code == 200:
                            response_data = response.json()
                            
                            # Convert to string and search for contacts
                            data_str = json.dumps(response_data)
                            
                            # Extract emails
                            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                                              data_str, re.IGNORECASE)
                            contacts['emails'].update(emails)
                            
                            # Extract phones
                            phones = re.findall(r'(?:\+?88)?01[3-9]\d{8}', data_str)
                            contacts['phones'].update(phones)
                            
                    except:
                        continue
            
            # Convert sets to lists
            contacts['emails'] = list(contacts['emails'])
            contacts['phones'] = list(contacts['phones'])
            
            return contacts if contacts['emails'] or contacts['phones'] else None
            
        except Exception as e:
            pass
        
        return None
    
    def method_contact_point(self, uid: str) -> Optional[Dict]:
        """conactcontact point """
        try:
            url = f"https://www.facebook.com/{uid}/contact"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                contacts = {'emails': set(), 'phones': set()}
                
                # Extract all text
                text = soup.get_text()
                
                # Find emails
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                                   text, re.IGNORECASE)
                contacts['emails'].update(emails)
                
                # Find phones
                phones = re.findall(r'(?:\+?88)?01[3-9]\d{8}', text)
                contacts['phones'].update(phones)
                
                # Convert sets to lists
                contacts['emails'] = list(contacts['emails'])
                contacts['phones'] = list(contacts['phones'])
                
                return contacts if contacts['emails'] or contacts['phones'] else None
                
        except Exception as e:
            pass
        
        return None
    
    def method_work_education(self, uid: str) -> Optional[Dict]:
        """ education or work details """
        try:
            url = f"https://www.facebook.com/{uid}/about_work_and_education"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                contacts = {'emails': set(), 'phones': set()}
                
                # Work and education might have contact info
                text = soup.get_text()
                
                # Extract emails
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                                   text, re.IGNORECASE)
                contacts['emails'].update(emails)
                
                # Convert sets to lists
                contacts['emails'] = list(contacts['emails'])
                
                return contacts if contacts['emails'] else None
                
        except Exception as e:
            pass
        
        return None
    
    def method_friends_contacts(self, uid: str) -> Optional[Dict]:
        """friend details """
        try:
            url = f"https://www.facebook.com/{uid}/friends"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                contacts = {'emails': set(), 'phones': set()}
                
                # Friends page might have mutual contact info
                text = soup.get_text()
                
                # Extract emails
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                                   text, re.IGNORECASE)
                contacts['emails'].update(emails)
                
                # Convert sets to lists
                contacts['emails'] = list(contacts['emails'])
                
                return contacts if contacts['emails'] else None
                
        except Exception as e:
            pass
        
        return None
    
    def _calculate_confidence(self, contacts: Dict) -> float:
        """confident score"""
        score = 0
        
        # Email confidence
        if contacts['emails']:
            score += len(contacts['emails']) * 10
        
        # Phone confidence
        if contacts['phones']:
            score += len(contacts['phones']) * 15
        
        # Registration info confidence
        if contacts['registration_info']:
            score += len(contacts['registration_info']) * 20
        
        # Normalize to 0-100
        confidence = min(100, score)
        
        return confidence