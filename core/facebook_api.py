"""
Facebook API Handler
Advanced API Interactions for Contact Discovery
"""

import requests
import json
import re
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class FacebookAPI:
    """faapi handlers """
    
    base_urls = {
        'graph': 'https://graph.facebook.com',
        'api': 'https://api.facebook.com',
        'web': 'https://web.facebook.com',
        'mobile': 'https://m.facebook.com'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.facebook.com',
            'Referer': 'https://www.facebook.com/',
            'DNT': '1'
        })
    
    def get_public_profile_info(self, user_id: str) -> Optional[Dict]:
        """public profile info """
        try:
            # Try Graph API (public fields only)
            url = f"{self.base_urls['graph']}/{user_id}"
            params = {
                'fields': 'id,name,first_name,last_name,middle_name,name_format,picture,short_name',
                'access_token': '1348564698517390|007c0a9101b9e1c8ffab727666805038'  # Public token
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
        
        except Exception as e:
            pass
        
        return None
    
    def extract_contact_hints(self, user_id: str) -> List[Dict]:
        """ contact hints """
        contact_hints = []
        
        methods = [
            self._hint_from_about,
            self._hint_from_friends,
            self._hint_from_photos,
            self._hint_from_posts,
            self._hint_from_comments
        ]
        
        for method in methods:
            try:
                hints = method(user_id)
                if hints:
                    contact_hints.extend(hints)
                time.sleep(random.uniform(0.5, 1))
            except:
                continue
        
        return contact_hints
    
    def _hint_from_about(self, user_id: str) -> List[Dict]:
        """About page hint"""
        hints = []
        
        try:
            url = f"https://www.facebook.com/{user_id}/about"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Parse HTML for contact hints
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for contact sections
                contact_sections = soup.find_all(text=re.compile(r'email|phone|contact|number', re.I))
                
                for section in contact_sections:
                    parent = section.parent
                    if parent:
                        text = parent.get_text()
                        
                        # Extract potential emails
                        emails = re.findall(r'\b\w+@\w+\.\w+\b', text)
                        for email in emails:
                            hints.append({
                                'type': 'email_hint',
                                'value': email,
                                'source': 'about_page',
                                'confidence': 0.6
                            })
                        
                        # Extract potential phones
                        phones = re.findall(r'\b01[3-9]\d{8}\b', text)
                        for phone in phones:
                            hints.append({
                                'type': 'phone_hint',
                                'value': phone,
                                'source': 'about_page',
                                'confidence': 0.7
                            })
        
        except:
            pass
        
        return hints
    
    def _hint_from_friends(self, user_id: str) -> List[Dict]:
        """friend hints"""
        hints = []
        
        try:
            url = f"https://www.facebook.com/{user_id}/friends"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Friends might have similar contact patterns
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for mutual friends or patterns
                friend_elements = soup.find_all('div', class_=re.compile(r'friend|mutual'))
                
                for element in friend_elements[:10]:  # Limit to first 10
                    text = element.get_text()
                    
                    # Check for patterns
                    if '@' in text:
                        emails = re.findall(r'\b\w+@\w+\.\w+\b', text)
                        for email in emails:
                            hints.append({
                                'type': 'email_pattern',
                                'value': email,
                                'source': 'friends_page',
                                'confidence': 0.4
                            })
        
        except:
            pass
        
        return hints
    
    def _hint_from_photos(self, user_id: str) -> List[Dict]:
        """photo hint"""
        hints = []
        
        try:
            url = f"https://www.facebook.com/{user_id}/photos"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Photo metadata might have hints
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look in alt text, captions
                img_elements = soup.find_all('img', alt=True)
                
                for img in img_elements[:20]:  # Limit
                    alt = img.get('alt', '')
                    if '@' in alt:
                        emails = re.findall(r'\b\w+@\w+\.\w+\b', alt)
                        for email in emails:
                            hints.append({
                                'type': 'photo_metadata',
                                'value': email,
                                'source': 'photos_page',
                                'confidence': 0.3
                            })
        
        except:
            pass
        
        return hints
    
    def _hint_from_posts(self, user_id: str) -> List[Dict]:
        """post hints"""
        hints = []
        
        try:
            url = f"https://www.facebook.com/{user_id}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look in posts
                post_elements = soup.find_all('div', class_=re.compile(r'post|story|status'))
                
                for post in post_elements[:10]:
                    text = post.get_text()
                    
                    # Check for contact info in posts
                    if '@' in text:
                        emails = re.findall(r'\b\w+@\w+\.\w+\b', text)
                        for email in emails:
                            hints.append({
                                'type': 'post_content',
                                'value': email,
                                'source': 'posts',
                                'confidence': 0.5
                            })
                    
                    if '01' in text and len(text) > 10:
                        phones = re.findall(r'\b01[3-9]\d{8}\b', text)
                        for phone in phones:
                            hints.append({
                                'type': 'post_content',
                                'value': phone,
                                'source': 'posts',
                                'confidence': 0.6
                            })
        
        except:
            pass
        
        return hints
    
    def _hint_from_comments(self, user_id: str) -> List[Dict]:
        """comment himts"""
        hints = []
        
        try:
            # Try to access comments
            url = f"https://www.facebook.com/{user_id}/posts"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look in comments
                comment_elements = soup.find_all('div', class_=re.compile(r'comment|reply'))
                
                for comment in comment_elements[:15]:
                    text = comment.get_text()
                    
                    # People might tag with emails
                    if '@' in text:
                        emails = re.findall(r'\b\w+@\w+\.\w+\b', text)
                        for email in emails:
                            hints.append({
                                'type': 'comment_mention',
                                'value': email,
                                'source': 'comments',
                                'confidence': 0.4
                            })
        
        except:
            pass
        
        return hints