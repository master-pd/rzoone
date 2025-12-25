"""
Advanced GraphQL Parser
Extracting contacts from Facebook's GraphQL API
"""

import re
import json
import time
import random
from typing import Dict, List, Optional, Any
import requests

class GraphQLParser:
    """এডভান্সড GraphQL পার্সার"""
    
    def __init__(self):
        self.common_queries = {
            'user_profile': '3315274998225349',
            'user_contact': '4270752577582839',
            'user_friends': '5271533905546916',
            'user_photos': '5500311907444321',
            'user_posts': '6232751770344865'
        }
        
        self.endpoints = [
            'https://www.facebook.com/api/graphql/',
            'https://web.facebook.com/api/graphql/',
            'https://graph.facebook.com/v15.0/'
        ]
    
    def extract_contacts_via_graphql(self, uid: str) -> Dict:
        """GraphQL API এর মাধ্যমে কন্ট্যাক্টস এক্সট্র্যাক্ট করুন"""
        results = {
            'emails': set(),
            'phones': set(),
            'graphql_data': {},
            'queries_successful': 0
        }
        
        print("\n[+] Querying GraphQL API...")
        
        for query_name, query_id in self.common_queries.items():
            try:
                print(f"  ↳ Running {query_name} query...")
                
                data = self._execute_graphql_query(uid, query_id)
                
                if data:
                    contacts = self._parse_graphql_response(data)
                    
                    if contacts:
                        results['emails'].update(contacts.get('emails', []))
                        results['phones'].update(contacts.get('phones', []))
                        
                        if 'extra_data' in contacts:
                            results['graphql_data'][query_name] = contacts['extra_data']
                        
                        results['queries_successful'] += 1
                
                time.sleep(random.uniform(2, 3))
                
            except Exception as e:
                continue
        
        # Convert sets to lists
        results['emails'] = list(results['emails'])
        results['phones'] = list(results['phones'])
        
        return results
    
    def _execute_graphql_query(self, uid: str, query_id: str) -> Optional[Dict]:
        """GraphQL কোয়েরি এক্সিকিউট করুন"""
        for endpoint in self.endpoints:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'https://www.facebook.com',
                    'Referer': f'https://www.facebook.com/{uid}',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'X-FB-Friendly-Name': 'ProfileCometHeaderQuery'
                }
                
                # Construct variables
                variables = {
                    'userID': uid,
                    'scale': 1
                }
                
                # Form data
                form_data = {
                    'variables': json.dumps(variables),
                    'doc_id': query_id,
                    'fb_api_req_friendly_name': 'ProfileCometHeaderQuery'
                }
                
                response = requests.post(
                    endpoint,
                    headers=headers,
                    data=form_data,
                    timeout=20,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    try:
                        return response.json()
                    except:
                        # Try to extract JSON from response text
                        json_match = re.search(r'({.*})', response.text)
                        if json_match:
                            return json.loads(json_match.group(1))
                
            except Exception as e:
                continue
        
        return None
    
    def _parse_graphql_response(self, data: Dict) -> Optional[Dict]:
        """GraphQL রেসপন্স পার্স করুন"""
        try:
            results = {
                'emails': set(),
                'phones': set(),
                'extra_data': {}
            }
            
            # Convert entire response to string for pattern matching
            data_str = json.dumps(data)
            
            # Extract emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, data_str, re.IGNORECASE)
            results['emails'].update(emails)
            
            # Extract BD phones
            phone_pattern = r'(?:\+?88)?01[3-9]\d{8}'
            phones = re.findall(phone_pattern, data_str)
            results['phones'].update(phones)
            
            # Try to parse structured data
            if 'data' in data:
                user_data = data.get('data', {}).get('user', {})
                
                # Check common fields that might contain contact info
                contact_fields = [
                    'email_addresses',
                    'contact_points',
                    'messenger_contacts',
                    'account_recovery_info',
                    'security_settings'
                ]
                
                for field in contact_fields:
                    if field in str(user_data):
                        # Extract field value using regex
                        field_pattern = f'"{field}":\\s*(\[.*?\])'
                        match = re.search(field_pattern, json.dumps(user_data))
                        
                        if match:
                            try:
                                field_data = json.loads(match.group(1))
                                results['extra_data'][field] = field_data
                            except:
                                results['extra_data'][field] = match.group(1)
                
                # Check for profile fields
                profile_fields = ['bio', 'about', 'intro', 'description']
                for field in profile_fields:
                    if field in user_data:
                        field_value = user_data[field]
                        if isinstance(field_value, str):
                            # Extract contacts from text fields
                            emails = re.findall(email_pattern, field_value, re.IGNORECASE)
                            results['emails'].update(emails)
                            
                            phones = re.findall(phone_pattern, field_value)
                            results['phones'].update(phones)
            
            # Convert sets to lists
            results['emails'] = list(results['emails'])
            results['phones'] = list(results['phones'])
            
            return results if (results['emails'] or results['phones'] or results['extra_data']) else None
            
        except Exception as e:
            return None
    
    def find_registration_info(self, uid: str) -> Optional[Dict]:
        """রেজিস্ট্রেশন ইনফো খুঁজুন"""
        try:
            # Special query for registration/account info
            registration_queries = [
                '3581399441840129',  # Account information query
                '4250402144846247',  # Registration details
                '5026166250934672'   # Account creation info
            ]
            
            registration_info = {}
            
            for query_id in registration_queries:
                try:
                    data = self._execute_graphql_query(uid, query_id)
                    
                    if data:
                        # Parse for registration info
                        info = self._parse_registration_data(data)
                        if info:
                            registration_info.update(info)
                    
                    time.sleep(random.uniform(2, 3))
                    
                except:
                    continue
            
            return registration_info if registration_info else None
            
        except Exception as e:
            return None
    
    def _parse_registration_data(self, data: Dict) -> Dict:
        """রেজিস্ট্রেশন ডাটা পার্স করুন"""
        info = {}
        
        try:
            data_str = json.dumps(data)
            
            # Look for registration patterns
            patterns = {
                'registration_email': r'registration[_-]?email[":\s]+([^",}\s]+@[^",}\s]+)',
                'registration_phone': r'registration[_-]?phone[":\s]+(\+?88?01[3-9]\d{8})',
                'account_created_with': r'created[_-]?with[":\s]+([^",}\s]+)',
                'signup_method': r'signup[_-]?method[":\s]+([^",}\s]+)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, data_str, re.IGNORECASE)
                if match:
                    info[key] = match.group(1).strip()
            
            # Look for date patterns
            date_pattern = r'(?:created|joined|registered)[":\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})'
            date_match = re.search(date_pattern, data_str, re.IGNORECASE)
            if date_match:
                info['registration_date'] = date_match.group(1)
            
        except Exception as e:
            pass
        
        return info