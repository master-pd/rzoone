"""
Backup Data Extraction Methods
Finding registration contacts from backup sources
"""

import re
import json
import time
import random
from typing import Dict, List, Optional, Set
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class BackupDataExtractor:
    """ব্যাকআপ ডাটা এক্সট্র্যাকশন মেথডস"""
    
    def __init__(self):
        self.cache = {}
        
    def extract_from_backup_sources(self, uid: str, username: str = None) -> Dict:
        """ব্যাকআপ সোর্স থেকে তথ্য সংগ্রহ"""
        results = {
            'emails': set(),
            'phones': set(),
            'backup_sources': []
        }
        
        methods = [
            self._check_archive_org,
            self._check_wayback_machine,
            self._check_google_cache,
            self._check_bing_cache,
            self._check_public_records,
            self._check_social_links,
            self._check_profile_backups
        ]
        
        print("\n[+] Checking backup sources...")
        
        for method in methods:
            try:
                print(f"  ↳ Running {method.__name__}...")
                data = method(uid, username)
                
                if data:
                    if 'emails' in data:
                        results['emails'].update(data['emails'])
                    if 'phones' in data:
                        results['phones'].update(data['phones'])
                    if 'source' in data:
                        results['backup_sources'].append(data['source'])
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                continue
        
        # Convert sets to lists
        results['emails'] = list(results['emails'])
        results['phones'] = list(results['phones'])
        
        return results
    
    def _check_archive_org(self, uid: str, username: str) -> Optional[Dict]:
        """Archive.org থেকে চেক করুন"""
        try:
            if username:
                url = f"https://web.archive.org/web/*/https://facebook.com/{username}"
            else:
                url = f"https://web.archive.org/web/*/https://facebook.com/profile.php?id={uid}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for snapshots
                snapshots = soup.find_all('div', class_=re.compile(r'snapshot'))
                
                contacts = {'emails': set(), 'phones': set(), 'source': 'archive_org'}
                
                for snapshot in snapshots[:3]:  # Check first 3 snapshots
                    snapshot_url = snapshot.find('a', href=True)
                    if snapshot_url:
                        snapshot_response = requests.get(
                            urljoin('https://web.archive.org', snapshot_url['href']),
                            headers=headers,
                            timeout=15
                        )
                        
                        if snapshot_response.status_code == 200:
                            # Extract contacts from snapshot
                            emails = re.findall(
                                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                                snapshot_response.text,
                                re.IGNORECASE
                            )
                            contacts['emails'].update(emails)
                            
                            phones = re.findall(
                                r'(?:\+?88)?01[3-9]\d{8}',
                                snapshot_response.text
                            )
                            contacts['phones'].update(phones)
                
                return contacts if contacts['emails'] or contacts['phones'] else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_wayback_machine(self, uid: str, username: str) -> Optional[Dict]:
        """Wayback Machine চেক করুন"""
        try:
            # Similar to archive.org
            base_url = "https://archive.org/wayback/available"
            
            if username:
                target_url = f"https://facebook.com/{username}"
            else:
                target_url = f"https://facebook.com/profile.php?id={uid}"
            
            params = {'url': target_url}
            
            response = requests.get(base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'archived_snapshots' in data:
                    contacts = {'emails': set(), 'phones': set(), 'source': 'wayback_machine'}
                    
                    for snapshot in data['archived_snapshots'].values():
                        snapshot_url = snapshot.get('url')
                        if snapshot_url:
                            snapshot_response = requests.get(snapshot_url, timeout=15)
                            
                            if snapshot_response.status_code == 200:
                                # Extract contacts
                                emails = re.findall(
                                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                                    snapshot_response.text,
                                    re.IGNORECASE
                                )
                                contacts['emails'].update(emails)
                                
                                phones = re.findall(
                                    r'(?:\+?88)?01[3-9]\d{8}',
                                    snapshot_response.text
                                )
                                contacts['phones'].update(phones)
                    
                    return contacts if contacts['emails'] or contacts['phones'] else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_google_cache(self, uid: str, username: str) -> Optional[Dict]:
        """Google Cache চেক করুন"""
        try:
            if username:
                search_url = f"cache:https://facebook.com/{username}"
            else:
                search_url = f"cache:https://facebook.com/profile.php?id={uid}"
            
            # Google search for cached version
            google_url = "https://www.google.com/search"
            params = {
                'q': search_url,
                'btnI': 'I\'m Feeling Lucky'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(google_url, params=params, headers=headers, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                contacts = {'emails': set(), 'phones': set(), 'source': 'google_cache'}
                
                # Extract contacts from cached page
                emails = re.findall(
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    response.text,
                    re.IGNORECASE
                )
                contacts['emails'].update(emails)
                
                phones = re.findall(
                    r'(?:\+?88)?01[3-9]\d{8}',
                    response.text
                )
                contacts['phones'].update(phones)
                
                return contacts if contacts['emails'] or contacts['phones'] else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_bing_cache(self, uid: str, username: str) -> Optional[Dict]:
        """Bing Cache চেক করুন"""
        try:
            if username:
                search_query = f"cache:https://www.facebook.com/{username}"
            else:
                search_query = f"cache:https://www.facebook.com/profile.php?id={uid}"
            
            bing_url = "https://www.bing.com/search"
            params = {'q': search_query}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(bing_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find cached link
                cached_link = soup.find('a', href=re.compile(r'cc\.bing\.net|cache'))
                
                if cached_link:
                    cached_response = requests.get(cached_link['href'], timeout=15)
                    
                    if cached_response.status_code == 200:
                        contacts = {'emails': set(), 'phones': set(), 'source': 'bing_cache'}
                        
                        emails = re.findall(
                            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                            cached_response.text,
                            re.IGNORECASE
                        )
                        contacts['emails'].update(emails)
                        
                        phones = re.findall(
                            r'(?:\+?88)?01[3-9]\d{8}',
                            cached_response.text
                        )
                        contacts['phones'].update(phones)
                        
                        return contacts if contacts['emails'] or contacts['phones'] else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_public_records(self, uid: str, username: str) -> Optional[Dict]:
        """পাবলিক রেকর্ডস চেক করুন"""
        try:
            # Search for username/uid in various public databases
            search_engines = [
                ("https://www.google.com/search", f'"{username}" email OR phone site:facebook.com'),
                ("https://www.bing.com/search", f'"{username}" contact information'),
                ("https://search.yahoo.com/search", f'"{username}" facebook contact')
            ]
            
            contacts = {'emails': set(), 'phones': set(), 'source': 'public_records'}
            
            for engine, query in search_engines:
                try:
                    params = {'q': query}
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    
                    response = requests.get(engine, params=params, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        # Extract emails and phones from search results
                        emails = re.findall(
                            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                            response.text,
                            re.IGNORECASE
                        )
                        contacts['emails'].update(emails)
                        
                        phones = re.findall(
                            r'(?:\+?88)?01[3-9]\d{8}',
                            response.text
                        )
                        contacts['phones'].update(phones)
                        
                        time.sleep(random.uniform(2, 3))
                        
                except:
                    continue
            
            return contacts if contacts['emails'] or contacts['phones'] else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_social_links(self, uid: str, username: str) -> Optional[Dict]:
        """সোশ্যাল লিংকস চেক করুন"""
        try:
            # Check if username appears on other social media
            social_sites = [
                f"https://twitter.com/{username}",
                f"https://instagram.com/{username}",
                f"https://linkedin.com/in/{username}",
                f"https://github.com/{username}",
                f"https://pinterest.com/{username}"
            ]
            
            contacts = {'emails': set(), 'phones': set(), 'source': 'social_links'}
            
            for site in social_sites:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.get(site, headers=headers, timeout=10, allow_redirects=False)
                    
                    if response.status_code == 200:
                        # Extract bio/description for contact info
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for bio/description sections
                        bio_selectors = ['bio', 'description', 'about', 'intro', 'profile']
                        
                        for selector in bio_selectors:
                            elements = soup.find_all(['div', 'p', 'span'], class_=re.compile(selector, re.I))
                            for element in elements:
                                text = element.get_text()
                                
                                emails = re.findall(
                                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                                    text,
                                    re.IGNORECASE
                                )
                                contacts['emails'].update(emails)
                        
                        time.sleep(1)
                        
                except:
                    continue
            
            return contacts if contacts['emails'] else None
        
        except Exception as e:
            pass
        
        return None
    
    def _check_profile_backups(self, uid: str, username: str) -> Optional[Dict]:
        """প্রোফাইল ব্যাকআপস চেক করুন"""
        try:
            # Check alternative profile URLs
            profile_variations = []
            
            if username:
                profile_variations = [
                    f"https://fb.com/{username}",
                    f"https://web.facebook.com/{username}",
                    f"https://m.facebook.com/{username}",
                    f"https://touch.facebook.com/{username}",
                    f"https://mbasic.facebook.com/{username}"
                ]
            else:
                profile_variations = [
                    f"https://fb.com/profile.php?id={uid}",
                    f"https://web.facebook.com/profile.php?id={uid}",
                    f"https://m.facebook.com/profile.php?id={uid}",
                    f"https://touch.facebook.com/profile.php?id={uid}",
                    f"https://mbasic.facebook.com/profile.php?id={uid}"
                ]
            
            contacts = {'emails': set(), 'phones': set(), 'source': 'profile_backups'}
            
            for profile_url in profile_variations:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.get(profile_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        # Extract contacts from alternative profile page
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Different versions might show different info
                        text = soup.get_text()
                        
                        emails = re.findall(
                            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                            text,
                            re.IGNORECASE
                        )
                        contacts['emails'].update(emails)
                        
                        phones = re.findall(
                            r'(?:\+?88)?01[3-9]\d{8}',
                            text
                        )
                        contacts['phones'].update(phones)
                        
                        time.sleep(0.5)
                        
                except:
                    continue
            
            return contacts if contacts['emails'] or contacts['phones'] else None
        
        except Exception as e:
            pass
        
        return None