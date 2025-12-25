"""
Intelligent Data Processor
AI-based Contact Validation and Scoring
"""

import re
import json
from typing import Dict, List, Tuple, Set, Optional
from collections import Counter
import hashlib

class DataProcessor:
    """ data processing ai validate """
    
    def __init__(self):
        # BD-specific patterns and data
        self.bd_data = self._load_bd_data()
        
        # Common patterns
        self.patterns = {
            'gmail': r'[\w\.-]+@gmail\.com',
            'yahoo': r'[\w\.-]+@yahoo\.com',
            'hotmail': r'[\w\.-]+@(hotmail|outlook|live)\.com',
            'bd_phone': r'01[3-9]\d{8}'
        }
    
    def _load_bd_data(self) -> Dict:
        """bd data loading """
        return {
            'common_names': [
                'khan', 'ahmed', 'rahman', 'hossain', 'islam', 
                'ali', 'hasan', 'hosain', 'uddin', 'chowdhury'
            ],
            'common_domains': [
                'gmail.com', 'yahoo.com', 'hotmail.com', 
                'outlook.com', 'live.com', 'mail.com'
            ],
            'phone_operators': {
                'gp': ['013', '017'],
                'robi': ['018', '016'],
                'banglalink': ['019', '014'],
                'airtel': ['015'],
                'teletalk': ['013']
            }
        }
    
    def process_contacts(self, raw_contacts: Dict) -> Dict:
        """ contact process """
        processed = {
            'emails': self._process_emails(raw_contacts.get('emails', [])),
            'phones': self._process_phones(raw_contacts.get('phones', [])),
            'registration_info': raw_contacts.get('registration_info', {}),
            'confidence_scores': {},
            'recommendations': []
        }
        
        # Calculate confidence scores
        processed['confidence_scores'] = self._calculate_confidences(processed)
        
        # Generate recommendations
        processed['recommendations'] = self._generate_recommendations(processed)
        
        return processed
    
    def _process_emails(self, emails: List[str]) -> List[Dict]:
        """email process """
        processed_emails = []
        
        for email in emails:
            email = email.strip().lower()
            
            # Skip obviously invalid
            if not self._is_valid_email(email):
                continue
            
            # Score the email
            score = self._score_email(email)
            
            # Determine type
            email_type = self._determine_email_type(email)
            
            processed_emails.append({
                'address': email,
                'type': email_type,
                'score': score,
                'is_likely_registration': score >= 70,
                'domain': email.split('@')[1] if '@' in email else ''
            })
        
        # Sort by score (highest first)
        processed_emails.sort(key=lambda x: x['score'], reverse=True)
        
        return processed_emails
    
    def _process_phones(self, phones: List[str]) -> List[Dict]:
        """ phone process """
        processed_phones = []
        
        for phone in phones:
            phone = phone.strip()
            
            # Clean and format
            clean_phone = self._clean_phone(phone)
            if not clean_phone:
                continue
            
            # Score the phone
            score = self._score_phone(clean_phone)
            
            # Determine operator
            operator = self._get_operator(clean_phone)
            
            processed_phones.append({
                'number': clean_phone,
                'formatted': self._format_phone(clean_phone),
                'operator': operator,
                'score': score,
                'is_likely_registration': score >= 75
            })
        
        # Sort by score (highest first)
        processed_phones.sort(key=lambda x: x['score'], reverse=True)
        
        return processed_phones
    
    def _is_valid_email(self, email: str) -> bool:
        """email validation """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False
        
        # Check for common invalid patterns
        invalid_patterns = [
            'example.com',
            'test.com',
            'domain.com',
            'email.com',
            'mail.com$'  # Ends with mail.com (often fake)
        ]
        
        for pattern in invalid_patterns:
            if pattern in email:
                return False
        
        return True
    
    def _score_email(self, email: str) -> int:
        """email score  (0-100)"""
        score = 50  # Base score
        
        # Domain-based scoring
        domain = email.split('@')[1] if '@' in email else ''
        
        # Common personal domains score higher
        common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        if domain in common_domains:
            score += 20
        
        # Length and pattern
        local_part = email.split('@')[0] if '@' in email else ''
        
        # Realistic patterns score higher
        if '.' in local_part or '_' in local_part:
            score += 10
        
        if local_part.islower() and len(local_part) > 4:
            score += 10
        
        # Contains common name parts
        for name in self.bd_data['common_names']:
            if name in local_part:
                score += 5
                break
        
        # Cap at 100
        return min(100, score)
    
    def _score_phone(self, phone: str) -> int:
        """phone score (0-100)"""
        score = 60  # Base score for valid BD number
        
        # Check if it's a valid BD mobile
        if not phone.startswith('01') or len(phone) != 11:
            return 30
        
        # Operator-based scoring
        operator_prefix = phone[0:3]
        
        # Common operators score higher
        common_operators = ['017', '018', '019', '016', '015']
        if operator_prefix in common_operators:
            score += 20
        
        # Pattern scoring (not sequential or repeating)
        digits = phone[2:]  # Remove '01'
        
        # Check for suspicious patterns
        if self._is_suspicious_pattern(digits):
            score -= 20
        
        # Check for realistic patterns
        if self._is_realistic_pattern(digits):
            score += 10
        
        # Cap at 100
        return min(100, max(0, score))
    
    def _determine_email_type(self, email: str) -> str:
        """email type permission """
        domain = email.split('@')[1] if '@' in email else ''
        
        if 'gmail' in domain:
            return 'personal_gmail'
        elif 'yahoo' in domain:
            return 'personal_yahoo'
        elif 'hotmail' in domain or 'outlook' in domain or 'live' in domain:
            return 'personal_microsoft'
        elif 'edu' in domain:
            return 'educational'
        elif 'org' in domain:
            return 'organization'
        elif 'gov' in domain:
            return 'government'
        else:
            return 'other'
    
    def _clean_phone(self, phone: str) -> Optional[str]:
        """clean phone"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Handle BD numbers
        if digits.startswith('88') and len(digits) == 13:
            return f"0{digits[2:]}"  # Convert 8801... to 01...
        elif digits.startswith('1') and len(digits) == 11:
            return digits  # Already 01 format
        elif len(digits) == 10 and digits.startswith('1'):
            return f"0{digits}"  # Add leading 0
        
        return None if len(digits) != 11 or not digits.startswith('01') else digits
    
    def _get_operator(self, phone: str) -> str:
        """slectoparetor """
        prefix = phone[0:3]
        
        operators = {
            '013': 'Grameenphone/Teletalk',
            '014': 'Banglalink',
            '015': 'Airtel',
            '016': 'Robi',
            '017': 'Grameenphone',
            '018': 'Robi',
            '019': 'Banglalink'
        }
        
        return operators.get(prefix, 'Unknown')
    
    def _format_phone(self, phone: str) -> str:
        """enter your format """
        if len(phone) == 11:
            return f"+88{phone}"  # International format
        return phone
    
    def _is_suspicious_pattern(self, digits: str) -> bool:
        """check suspicious """
        # Check for sequential numbers
        if digits in ['123456789', '012345678', '987654321']:
            return True
        
        # Check for repeating numbers
        if len(set(digits)) < 3:
            return True
        
        # Check for common fake patterns
        fake_patterns = ['111111111', '000000000', '123123123', '321321321']
        if digits in fake_patterns:
            return True
        
        return False
    
    def _is_realistic_pattern(self, digits: str) -> bool:
        """রিয়েলিস্টিক প্যাটার্ন চেক করুন"""
        # Real numbers usually have variation
        digit_counts = Counter(digits)
        
        # Most digits should appear 1-3 times
        max_count = max(digit_counts.values())
        if max_count > 4:  # Too many repeats
            return False
        
        # Should have reasonable variation
        unique_digits = len(digit_counts)
        if unique_digits < 5:  # Too few unique digits
            return False
        
        return True
    
    def _calculate_confidences(self, processed: Dict) -> Dict:
        """কনফিডেন্স স্কোর ক্যালকুলেট করুন"""
        confidences = {
            'overall': 0,
            'email_confidence': 0,
            'phone_confidence': 0,
            'registration_confidence': 0
        }
        
        # Email confidence
        emails = processed.get('emails', [])
        if emails:
            email_scores = [e['score'] for e in emails]
            confidences['email_confidence'] = max(email_scores)
        
        # Phone confidence
        phones = processed.get('phones', [])
        if phones:
            phone_scores = [p['score'] for p in phones]
            confidences['phone_confidence'] = max(phone_scores)
        
        # Overall confidence
        if emails and phones:
            confidences['overall'] = (confidences['email_confidence'] + confidences['phone_confidence']) / 2
        elif emails:
            confidences['overall'] = confidences['email_confidence']
        elif phones:
            confidences['overall'] = confidences['phone_confidence']
        
        # Registration confidence
        reg_info = processed.get('registration_info', {})
        if reg_info:
            confidences['registration_confidence'] = min(90, len(reg_info) * 20)
        
        return confidences
    
    def _generate_recommendations(self, processed: Dict) -> List[str]:
        """রিকমেন্ডেশন জেনারেট করুন"""
        recommendations = []
        
        emails = processed.get('emails', [])
        phones = processed.get('phones', [])
        
        # Email recommendations
        high_score_emails = [e for e in emails if e['score'] >= 70]
        if high_score_emails:
            top_email = high_score_emails[0]['address']
            recommendations.append(f"Try logging in with email: {top_email}")
        
        # Phone recommendations
        high_score_phones = [p for p in phones if p['score'] >= 75]
        if high_score_phones:
            top_phone = high_score_phones[0]['formatted']
            recommendations.append(f"Try logging in with phone: {top_phone}")
        
        # Combined recommendations
        if high_score_emails and high_score_phones:
            recommendations.append("Try both email and phone combinations")
        
        # General recommendations
        if not recommendations:
            if emails:
                recommendations.append("Try the highest scored email first")
            elif phones:
                recommendations.append("Try the highest scored phone first")
            else:
                recommendations.append("Use Facebook's official account recovery")
                recommendations.append("Contact Facebook support with your ID")
        
        # Add ethical reminder
        recommendations.append("Use only for YOUR account recovery")
        
        return recommendations