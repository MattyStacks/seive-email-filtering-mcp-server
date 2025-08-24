"""
Email message analysis for Sieve filter generation.
Parses .eml files and generates appropriate Sieve filters.
"""

import re
import email
import email.utils
from typing import List, Dict, Optional, Tuple
from email.message import EmailMessage
from .models import EmailMessage as EmailMessageModel, FilterAnalysis, SieveRule
from .utils import SieveFilterBuilder


class EmailAnalyzer:
    """Analyzes email messages to suggest Sieve filters."""
    
    def __init__(self):
        self.common_promotional_keywords = [
            "sale", "discount", "offer", "promotion", "deal", "coupon",
            "limited time", "special offer", "save", "% off", "free shipping",
            "clearance", "flash sale", "exclusive", "bonus"
        ]
        
        self.common_financial_keywords = [
            "statement", "balance", "payment", "transaction", "account",
            "invoice", "bill", "due", "credit", "debit", "bank", "card"
        ]
        
        self.common_notification_keywords = [
            "notification", "alert", "reminder", "update", "status",
            "confirmation", "receipt", "delivery", "tracking"
        ]
        
        self.spam_indicators = [
            "urgent", "act now", "limited time", "winner", "congratulations",
            "free money", "guaranteed", "risk free", "no obligation"
        ]
    
    def parse_eml_file(self, file_path: str) -> EmailMessageModel:
        """Parse an .eml file from disk and extract email components."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                eml_content = f.read()
            return self.parse_eml_content(eml_content)
        except Exception as e:
            raise ValueError(f"Failed to read or parse email file {file_path}: {str(e)}")
    
    def parse_eml_content(self, eml_content: str) -> EmailMessageModel:
        """Parse an .eml file content and extract email components."""
        try:
            # Parse the email message
            msg = email.message_from_string(eml_content)
            
            # Extract headers
            headers = {}
            for key, value in msg.items():
                headers[key.lower()] = value
            
            # Extract specific header values
            from_address = headers.get('from', '')
            to_addresses = []
            if 'to' in headers:
                to_addresses = [addr.strip() for addr in headers['to'].split(',')]
            
            subject = headers.get('subject', '')
            
            # Extract body content
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            
            return EmailMessageModel(
                headers=headers,
                from_address=from_address,
                to_addresses=to_addresses,
                subject=subject,
                body=body,
                raw_content=eml_content
            )
        
        except Exception as e:
            raise ValueError(f"Failed to parse email: {str(e)}")
    
    def analyze_email(self, email_msg: EmailMessageModel) -> FilterAnalysis:
        """Analyze an email message and suggest filter criteria."""
        analysis = FilterAnalysis(
            suggested_filter_name="",
            suggested_folder="",
            confidence_score=0.0
        )
        
        # Analyze sender patterns
        sender_patterns = self._analyze_sender(email_msg.from_address or "")
        analysis.sender_patterns = sender_patterns
        
        # Analyze subject patterns
        subject_patterns = self._analyze_subject(email_msg.subject or "")
        analysis.subject_patterns = subject_patterns
        
        # Analyze domain patterns
        domain_patterns = self._extract_domain_patterns(email_msg.from_address or "")
        analysis.domain_patterns = domain_patterns
        
        # Analyze content for keywords
        content_keywords = self._analyze_content(email_msg.body or "")
        analysis.content_keywords = content_keywords
        
        # Determine email category and suggested actions
        category_analysis = self._categorize_email(email_msg, subject_patterns, content_keywords)
        analysis.suggested_filter_name = category_analysis["name"]
        analysis.suggested_folder = category_analysis["folder"]
        analysis.recommended_actions = category_analysis["actions"]
        analysis.requires_expiration = category_analysis["expire"]
        analysis.confidence_score = category_analysis["confidence"]
        
        return analysis
    
    def _analyze_sender(self, from_address: str) -> List[str]:
        """Extract sender patterns for filtering."""
        patterns = []
        
        if not from_address:
            return patterns
        
        # Extract email address if it's in "Name <email>" format
        parsed = email.utils.parseaddr(from_address)
        email_addr = parsed[1] if parsed[1] else from_address
        
        patterns.append(email_addr)
        
        # Extract domain
        if '@' in email_addr:
            domain = email_addr.split('@')[1]
            patterns.append(domain)
        
        # Check for common patterns
        if 'noreply' in email_addr.lower():
            patterns.append("noreply")
        
        if 'no-reply' in email_addr.lower():
            patterns.append("no-reply")
        
        return patterns
    
    def _analyze_subject(self, subject: str) -> List[str]:
        """Extract subject patterns for filtering."""
        patterns = []
        
        if not subject:
            return patterns
        
        patterns.append(subject)
        
        # Extract common promotional patterns
        for keyword in self.common_promotional_keywords:
            if keyword.lower() in subject.lower():
                patterns.append(keyword)
        
        # Extract financial patterns
        for keyword in self.common_financial_keywords:
            if keyword.lower() in subject.lower():
                patterns.append(keyword)
        
        # Look for bracketed tags like [PROMOTIONAL] or [NOTIFICATION]
        bracket_matches = re.findall(r'\[([^\]]+)\]', subject)
        patterns.extend(bracket_matches)
        
        # Look for common subject prefixes
        if subject.lower().startswith('re:'):
            patterns.append("re:")
        if subject.lower().startswith('fwd:'):
            patterns.append("fwd:")
        
        return patterns
    
    def _extract_domain_patterns(self, from_address: str) -> List[str]:
        """Extract domain patterns from email address."""
        patterns = []
        
        if not from_address or '@' not in from_address:
            return patterns
        
        # Extract email if in "Name <email>" format
        parsed = email.utils.parseaddr(from_address)
        email_addr = parsed[1] if parsed[1] else from_address
        
        if '@' in email_addr:
            domain = email_addr.split('@')[1].lower()
            patterns.append(domain)
            
            # Extract root domain (e.g., "example.com" from "mail.example.com")
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                root_domain = '.'.join(domain_parts[-2:])
                if root_domain != domain:
                    patterns.append(root_domain)
        
        return patterns
    
    def _analyze_content(self, body: str) -> List[str]:
        """Extract keywords from email content."""
        keywords = []
        
        if not body:
            return keywords
        
        body_lower = body.lower()
        
        # Check for promotional content
        for keyword in self.common_promotional_keywords:
            if keyword in body_lower:
                keywords.append(keyword)
        
        # Check for financial content
        for keyword in self.common_financial_keywords:
            if keyword in body_lower:
                keywords.append(keyword)
        
        # Check for notification content
        for keyword in self.common_notification_keywords:
            if keyword in body_lower:
                keywords.append(keyword)
        
        # Look for URLs and extract domains
        url_pattern = r'https?://([^\s/]+)'
        url_matches = re.findall(url_pattern, body)
        for domain in url_matches[:5]:  # Limit to first 5 domains
            keywords.append(f"url:{domain}")
        
        return keywords
    
    def _categorize_email(self, email_msg: EmailMessageModel, subject_patterns: List[str], 
                         content_keywords: List[str]) -> Dict[str, any]:
        """Categorize email and suggest folder and actions."""
        from_address = (email_msg.from_address or "").lower()
        subject = (email_msg.subject or "").lower()
        
        # Steam-specific detection
        if 'steam' in from_address or 'steampowered.com' in from_address:
            if any('sale' in pattern.lower() for pattern in subject_patterns):
                return {
                    "name": "Steam Sales",
                    "folder": "promotions",
                    "actions": ["fileinto", "expire"],
                    "expire": True,
                    "confidence": 0.95
                }
            else:
                return {
                    "name": "Steam Notifications", 
                    "folder": "gaming",
                    "actions": ["fileinto"],
                    "expire": False,
                    "confidence": 0.9
                }
        
        # Financial institution detection
        financial_domains = ['bankofamerica.com', 'chase.com', 'wellsfargo.com', 'citi.com', 
                            'paypal.com', 'venmo.com', 'cashapp.com']
        if any(domain in from_address for domain in financial_domains):
            return {
                "name": f"Financial - {self._extract_institution_name(from_address)}",
                "folder": "finance",
                "actions": ["fileinto"],
                "expire": False,
                "confidence": 0.9
            }
        
        # Promotional content detection
        promo_score = sum(1 for keyword in self.common_promotional_keywords 
                         if keyword in subject.lower() or keyword in ' '.join(content_keywords))
        
        if promo_score >= 2:
            return {
                "name": "Promotional Email",
                "folder": "promotions", 
                "actions": ["fileinto", "expire"],
                "expire": True,
                "confidence": min(0.9, 0.5 + promo_score * 0.1)
            }
        
        # Newsletter/notification detection
        if any(keyword in from_address for keyword in ['newsletter', 'notifications', 'noreply']):
            return {
                "name": "Newsletter/Notification",
                "folder": "notifications",
                "actions": ["fileinto"],
                "expire": False,
                "confidence": 0.7
            }
        
        # Default categorization
        domain = self._extract_domain(from_address)
        return {
            "name": f"Filter for {domain}",
            "folder": "filtered",
            "actions": ["fileinto"],
            "expire": False,
            "confidence": 0.5
        }
    
    def _extract_institution_name(self, from_address: str) -> str:
        """Extract institution name from email address."""
        if 'bankofamerica' in from_address:
            return "Bank of America"
        elif 'chase' in from_address:
            return "Chase"
        elif 'wellsfargo' in from_address:
            return "Wells Fargo"
        elif 'paypal' in from_address:
            return "PayPal"
        else:
            domain = self._extract_domain(from_address)
            return domain.replace('.com', '').title()
    
    def _extract_domain(self, from_address: str) -> str:
        """Extract domain from email address."""
        if '@' in from_address:
            parsed = email.utils.parseaddr(from_address)
            email_addr = parsed[1] if parsed[1] else from_address
            if '@' in email_addr:
                return email_addr.split('@')[1]
        return "unknown"
    
    def generate_filter_from_analysis(self, analysis: FilterAnalysis) -> SieveRule:
        """Generate a Sieve rule based on email analysis."""
        # Determine the best filtering approach
        if analysis.sender_patterns:
            # Use sender-based filtering
            sender_email = analysis.sender_patterns[0]
            if '@' in sender_email:
                rule = SieveFilterBuilder.create_sender_filter(
                    sender_email,
                    analysis.suggested_folder,
                    priority=30
                )
            else:
                # Domain-based filtering
                domain = analysis.domain_patterns[0] if analysis.domain_patterns else sender_email
                rule = SieveFilterBuilder.create_domain_filter(
                    domain,
                    analysis.suggested_folder,
                    priority=30
                )
        elif analysis.subject_patterns:
            # Use subject-based filtering
            rule = SieveFilterBuilder.create_subject_filter(
                analysis.subject_patterns[:3],  # Use top 3 patterns
                analysis.suggested_folder,
                priority=40
            )
        else:
            # Fallback to basic sender filter
            sender = analysis.sender_patterns[0] if analysis.sender_patterns else "unknown"
            rule = SieveFilterBuilder.create_sender_filter(
                sender,
                analysis.suggested_folder,
                priority=50
            )
        
        # Update rule name and description
        rule.name = analysis.suggested_filter_name
        rule.description = f"Auto-generated filter (confidence: {analysis.confidence_score:.2f})"
        
        # Add expiration if recommended
        if analysis.requires_expiration and "expire" in analysis.recommended_actions:
            from .models import SieveExpireAction
            expire_action = SieveExpireAction(period="day", count="7")
            rule.actions.insert(0, expire_action)  # Add expire before fileinto
        
        return rule
