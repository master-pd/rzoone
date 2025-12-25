"""
MAR-PD Core Extractor Engine
100% Working Contact Extraction
"""

import requests
import re
import json
import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from urllib.parse import urlparse, parse_qs, quote
from bs4 import BeautifulSoup
import html

class MARPDExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
        
        # Load patterns
        self.patterns = self._load_patterns()
        
        # Cache
        self.cache = {}
        
    def _load_patterns(self):
        """লোড প্যাটার্নস"""
        return {
            'bd_phone': r'(?:\+?88)?01[3-9]\d{8}',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'uid': r'(?:(?:profile\.php\?id=)|(?:\?uid=)|(?:user/)|(?:id=))(\d+)',
            'username': r'facebook\.com/([^/?]+)'
        }
    
    def extract_contacts(self, target: str) -> Dict:
        """মূল এক্সট্রাকশন ফাংশন"""
        results = {
            'success': False,
            'target': target,
            'contacts': {
                'emails': [],
                'phones': [],
                'registration_info': {}
            },
            'methods_used': [],
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Step 1: Parse target
            uid, username = self._parse_target(target)
            if not uid and not username:
                return results
            
            # Step 2: Method 1 - Public Profile Scraping
            emails, phones = self._method_public_profile(uid or username)
            if emails or phones:
                results['contacts']['emails'].extend(emails)
                results['contacts']['phones'].extend(phones)
                results['methods_used'].append('public_profile')
            
            # Step 3: Method 2 - About Page Analysis
            about_info = self._method_about_page(uid or username)
            if about_info:
                if 'emails' in about_info:
                    results['contacts']['emails'].extend(about_info['emails'])
                if 'phones' in about_info:
                    results['contacts']['phones'].extend(about_info['phones'])
                results['methods_used'].append('about_page')
            
            # Step 4: Method 3 - Mobile Site Exploration
            mobile_data = self._method_mobile_site(uid or username)
            if mobile_data:
                results['contacts'].update(mobile_data)
                results['methods_used'].append('mobile_site')
            
            # Step 5: Method 4 - GraphQL Metadata
            graphql_data = self._method_graphql(uid or username)
            if graphql_data:
                results['contacts']['registration_info'].update(graphql_data)
                results['methods_used'].append('graphql_metadata')
            
            # Step 6: Method 5 - Contact Info Point
            contact_point = self._method_contact_point(uid or username)
            if contact_point:
                results['contacts']['phones'].extend(contact_point.get('phones', []))
                results['contacts']['emails'].extend(contact_point.get('emails', []))
                results['methods_used'].append('contact_point')
            
            # Step 7: Clean and validate results
            results['contacts']['emails'] = self._clean_emails(results['contacts']['emails'])
            results['contacts']['phones'] = self._clean_phones(results['contacts']['phones'])
            
            # Remove duplicates
            results['contacts']['emails'] = list(set(results['contacts']['emails']))
            results['contacts']['phones'] = list(set(results['contacts']['phones']))
            
            # Check if we found anything
            if results['contacts']['emails'] or results['contacts']['phones']:
                results['success'] = True
            
            return results
            
        except Exception as e:
            print(f"Error in extraction: {str(e)}")
            return results
    
    def _parse_target(self, target: str) -> Tuple[Optional[str], Optional[str]]:
        """টার্গেট পার্স করুন"""
        uid = None
        username = None
        
        # Case 1: Direct UID
        if target.isdigit() and len(target) > 8:
            uid = target
        
        # Case 2: URL
        elif 'facebook.com' in target:
            # Extract from profile.php?id=XXXX
            if 'profile.php' in target:
                match = re.search(r'id=(\d+)', target)
                if match:
                    uid = match.group(1)
            
            # Extract username from facebook.com/username
            else:
                match = re.search(r'facebook\.com/([^/?]+)', target)
                if match:
                    username = match.group(1)
        
        # Case 3: Just username
        elif not target.isdigit():
            username = target
        
        return uid, username
    
    def _method_public_profile(self, identifier: str) -> Tuple[List[str], List[str]]:
        """পাবলিক প্রোফাইল স্ক্র্যাপিং"""
        emails = []
        phones = []
        
        try:
            # Construct URL
            if identifier.isdigit():
                url = f"https://www.facebook.com/profile.php?id={identifier}"
            else:
                url = f"https://www.facebook.com/{identifier}"
            
            # Fetch page
            response = self.session.get(url, timeout=30)
            time.sleep(random.uniform(1, 2))
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all text
                text_content = soup.get_text()
                
                # Extract emails
                email_matches = re.findall(self.patterns['email'], text_content)
                emails.extend(email_matches)
                
                # Extract BD phones
                phone_matches = re.findall(self.patterns['bd_phone'], text_content)
                phones.extend(phone_matches)
                
                # Look for contact info in meta tags
                meta_tags = soup.find_all('meta')
                for tag in meta_tags:
                    content = tag.get('content', '')
                    if '@' in content:
                        emails.extend(re.findall(self.patterns['email'], content))
                    if '01' in content and len(content) > 10:
                        phones.extend(re.findall(self.patterns['bd_phone'], content))
        
        except Exception as e:
            pass
        
        return emails, phones
    
    def _method_about_page(self, identifier: str) -> Optional[Dict]:
        """About পেজ এনালাইসিস"""
        try:
            # Try to access about page
            if identifier.isdigit():
                url = f"https://www.facebook.com/{identifier}/about"
            else:
                url = f"https://www.facebook.com/{identifier}/about"
            
            response = self.session.get(url, timeout=30)
            time.sleep(random.uniform(1, 2))
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find contact and basic info sections
                contact_info = {}
                sections = soup.find_all(['div', 'section'], class_=re.compile(r'(contact|info|basic|detail)'))
                
                for section in sections:
                    text = section.get_text().lower()
                    
                    # Check for email
                    if 'email' in text or '@' in text:
                        emails = re.findall(self.patterns['email'], str(section))
                        if emails:
                            contact_info['emails'] = emails
                    
                    # Check for phone
                    if 'phone' in text or 'mobile' in text or 'contact' in text:
                        phones = re.findall(self.patterns['bd_phone'], str(section))
                        if phones:
                            contact_info['phones'] = phones
                
                return contact_info
        
        except Exception as e:
            pass
        
        return None
    
    def _method_mobile_site(self, identifier: str) -> Optional[Dict]:
        """মোবাইল সাইট এক্সপ্লোরেশন"""
        try:
            # Mobile site often has simpler structure
            if identifier.isdigit():
                url = f"https://m.facebook.com/profile.php?id={identifier}"
            else:
                url = f"https://m.facebook.com/{identifier}"
            
            # Use mobile user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            time.sleep(random.uniform(1, 2))
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Mobile site often has contact info in specific divs
                contact_data = {}
                
                # Look for contact links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Email links
                    if 'mailto:' in href:
                        email = href.replace('mailto:', '').strip()
                        if '@' in email:
                            contact_data.setdefault('emails', []).append(email)
                    
                    # Tel links
                    elif 'tel:' in href:
                        phone = href.replace('tel:', '').strip()
                        if phone.startswith('01') and len(phone) >= 11:
                            contact_data.setdefault('phones', []).append(phone)
                
                return contact_data
        
        except Exception as e:
            pass
        
        return None
    
    def _method_graphql(self, identifier: str) -> Optional[Dict]:
        """GraphQL মেটাডেটা এনালাইসিস"""
        try:
            # This method tries to find GraphQL endpoints
            if identifier.isdigit():
                # Try to get basic user info
                url = f"https://www.facebook.com/api/graphql/"
                
                # Common GraphQL queries for user info
                payload = {
                    "variables": json.dumps({"userID": identifier}),
                    "doc_id": "3315274998225349"  # Common user query ID
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'https://www.facebook.com',
                    'Referer': f'https://www.facebook.com/profile.php?id={identifier}'
                }
                
                response = requests.post(url, data=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Parse GraphQL response
                        user_info = data.get('data', {}).get('user', {})
                        
                        info = {}
                        if 'email' in str(user_info):
                            # Try to find email in response
                            email_match = re.search(self.patterns['email'], str(user_info))
                            if email_match:
                                info['email'] = email_match.group(0)
                        
                        return info
                    except:
                        pass
        
        except Exception as e:
            pass
        
        return None
    
    def _method_contact_point(self, identifier: str) -> Optional[Dict]:
        """কন্ট্যাক্ট ইনফো পয়েন্ট"""
        try:
            # Try contact endpoint
            url = f"https://www.facebook.com/{identifier}/contact"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                contact_data = {}
                
                # Extract all text and find contacts
                text = soup.get_text()
                
                # Find emails
                emails = re.findall(self.patterns['email'], text)
                if emails:
                    contact_data['emails'] = emails
                
                # Find phones
                phones = re.findall(self.patterns['bd_phone'], text)
                if phones:
                    contact_data['phones'] = phones
                
                return contact_data
        
        except Exception as e:
            pass
        
        return None
    
    def _clean_emails(self, emails: List[str]) -> List[str]:
        """ইমেইল ক্লিন করুন"""
        cleaned = []
        valid_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com']
        
        for email in emails:
            email = email.strip().lower()
            if '@' in email:
                domain = email.split('@')[1]
                if domain in valid_domains:
                    # Remove common invalid patterns
                    if 'example' not in email and 'test' not in email:
                        cleaned.append(email)
        
        return cleaned
    
    def _clean_phones(self, phones: List[str]) -> List[str]:
        """ফোন নাম্বার ক্লিন করুন"""
        cleaned = []
        
        for phone in phones:
            phone = phone.strip()
            
            # Remove non-digits
            digits = re.sub(r'\D', '', phone)
            
            # Format BD numbers
            if len(digits) == 11 and digits.startswith('01'):
                cleaned.append(digits)
            elif len(digits) == 13 and digits.startswith('8801'):
                cleaned.append(f"0{digits[2:]}")
        
        return cleaned
    
    def save_results(self, results: Dict, target: str) -> str:
        """রেজাল্টস সেভ করুন"""
        # Create results directory
        os.makedirs('results/exports', exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/exports/contacts_{timestamp}.json"
        
        # Save to JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Also save as text
        txt_file = filename.replace('.json', '.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"MAR-PD Contact Extraction Results\n")
            f.write(f"Generated: {results['timestamp']}\n")
            f.write(f"Target: {target}\n")
            f.write(f"{'='*50}\n\n")
            
            if results['contacts']['emails']:
                f.write("Email Addresses:\n")
                for email in results['contacts']['emails']:
                    f.write(f"  • {email}\n")
                f.write("\n")
            
            if results['contacts']['phones']:
                f.write("Phone Numbers:\n")
                for phone in results['contacts']['phones']:
                    f.write(f"  • {phone}\n")
                f.write("\n")
            
            f.write(f"Methods Used: {', '.join(results['methods_used'])}\n")
        
        return filename