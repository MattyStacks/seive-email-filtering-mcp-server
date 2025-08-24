"""
Utility functions for creating common Sieve filter patterns.
"""

from typing import List, Optional
from .models import (
    SieveRule, SieveScript,
    SieveHeaderTest, SieveAddressTest, SieveBodyTest, SieveExistsTest, SieveSizeTest,
    SieveAllOfTest, SieveAnyOfTest, SieveNotTest,
    SieveFileintoAction, SieveRedirectAction, SieveDiscardAction, SieveRejectAction,
    SieveVacationAction, SieveStopAction, SieveKeepAction, SieveExpireAction,
    SieveComparator, SieveAddressPart, SieveSizeComparator, SieveActionType, SieveTestUnion
)


class SieveFilterBuilder:
    """Builder class for creating common Sieve filter patterns."""
    
    @staticmethod
    def split_multiple_fileinto_actions(rule: SieveRule) -> List[SieveRule]:
        """
        Split a rule with multiple fileinto actions into separate rules.
        
        This ensures Sieve compliance since multiple fileinto actions 
        cannot be combined in a single rule.
        """
        # Find all fileinto actions
        fileinto_actions = [action for action in rule.actions if action.action_type == SieveActionType.FILEINTO]
        non_fileinto_actions = [action for action in rule.actions if action.action_type != SieveActionType.FILEINTO]
        
        if len(fileinto_actions) <= 1:
            # No splitting needed
            return [rule]
        
        rules = []
        
        # Create first rule with non-fileinto actions + first fileinto
        if fileinto_actions:
            first_rule = SieveRule(
                name=f"{rule.name} (File to {fileinto_actions[0].mailbox})",
                description=f"{rule.description} - files to {fileinto_actions[0].mailbox}",
                enabled=rule.enabled,
                test=rule.test,
                actions=non_fileinto_actions + [fileinto_actions[0]],
                priority=rule.priority
            )
            rules.append(first_rule)
        
        # Create additional rules for remaining fileinto actions
        for i, fileinto_action in enumerate(fileinto_actions[1:], 2):
            additional_rule = SieveRule(
                name=f"{rule.name} (File to {fileinto_action.mailbox})",
                description=f"{rule.description} - files to {fileinto_action.mailbox}",
                enabled=rule.enabled,
                test=rule.test,
                actions=[fileinto_action],
                priority=rule.priority + i  # Slightly higher priority to ensure order
            )
            rules.append(additional_rule)
        
        return rules
    
    @staticmethod
    def create_expiring_fileinto_filter(
        test: SieveTestUnion,
        expire_mailbox: str,
        regular_mailbox: str,
        expire_period: str = "day",
        expire_count: str = "7",
        name: str = "Expiring Filter",
        description: str = "Filter with auto-expiration",
        priority: int = 30
    ) -> List[SieveRule]:
        """
        Create separate rules for expiring + fileinto actions.
        
        Returns two rules:
        1. Expire action + file to expiring folder
        2. File to regular folder
        """
        # Rule 1: Expire and file to expiring folder
        expire_rule = SieveRule(
            name=f"{name} (Expiring)",
            description=f"{description} - expires after {expire_count} {expire_period}(s)",
            test=test,
            actions=[
                SieveExpireAction(period=expire_period, count=expire_count),
                SieveFileintoAction(mailbox=expire_mailbox)
            ],
            priority=priority
        )
        
        # Rule 2: File to regular folder
        fileinto_rule = SieveRule(
            name=f"{name} (Filing)",
            description=f"{description} - files to {regular_mailbox}",
            test=test,
            actions=[
                SieveFileintoAction(mailbox=regular_mailbox)
            ],
            priority=priority + 1
        )
        
        return [expire_rule, fileinto_rule]
    
    @staticmethod
    def create_spam_filter(mailbox: str = "Spam", priority: int = 10) -> SieveRule:
        """Create a rule to filter spam messages."""
        test = SieveAnyOfTest(
            tests=[
                SieveHeaderTest(
                    header_list=["X-Spam-Flag"],
                    key_list=["YES"],
                    comparator=SieveComparator.IS
                ),
                SieveHeaderTest(
                    header_list=["X-Spam-Status"],
                    key_list=["*Yes*"],
                    comparator=SieveComparator.MATCHES
                ),
                SieveHeaderTest(
                    header_list=["Subject"],
                    key_list=["***SPAM***", "[SPAM]", "***UCE***"],
                    comparator=SieveComparator.CONTAINS
                )
            ]
        )
        
        actions = [
            SieveFileintoAction(mailbox=mailbox),
            SieveStopAction()
        ]
        
        return SieveRule(
            name="Spam Filter",
            description="Move spam messages to spam folder",
            test=test,
            actions=actions,
            priority=priority
        )
    
    @staticmethod
    def create_mailing_list_filter(
        list_id: str,
        mailbox: str,
        priority: int = 20
    ) -> SieveRule:
        """Create a rule to filter mailing list messages."""
        test = SieveAnyOfTest(
            tests=[
                SieveHeaderTest(
                    header_list=["List-ID"],
                    key_list=[f"*{list_id}*"],
                    comparator=SieveComparator.MATCHES
                ),
                SieveHeaderTest(
                    header_list=["List-Post"],
                    key_list=[f"*{list_id}*"],
                    comparator=SieveComparator.MATCHES
                ),
                SieveHeaderTest(
                    header_list=["X-Mailing-List"],
                    key_list=[f"*{list_id}*"],
                    comparator=SieveComparator.MATCHES
                )
            ]
        )
        
        actions = [SieveFileintoAction(mailbox=mailbox)]
        
        return SieveRule(
            name=f"Mailing List: {list_id}",
            description=f"Filter messages from {list_id} mailing list",
            test=test,
            actions=actions,
            priority=priority
        )
    
    @staticmethod
    def create_sender_filter(
        sender_email: str,
        mailbox: str,
        priority: int = 30
    ) -> SieveRule:
        """Create a rule to filter messages from a specific sender."""
        test = SieveAddressTest(
            header_list=["From"],
            key_list=[sender_email],
            comparator=SieveComparator.IS,
            address_part=SieveAddressPart.ALL
        )
        
        actions = [SieveFileintoAction(mailbox=mailbox)]
        
        return SieveRule(
            name=f"From: {sender_email}",
            description=f"Filter messages from {sender_email}",
            test=test,
            actions=actions,
            priority=priority
        )
    
    @staticmethod
    def create_domain_filter(
        domain: str,
        mailbox: str,
        priority: int = 30
    ) -> SieveRule:
        """Create a rule to filter messages from a specific domain."""
        test = SieveAddressTest(
            header_list=["From"],
            key_list=[domain],
            comparator=SieveComparator.IS,
            address_part=SieveAddressPart.DOMAIN
        )
        
        actions = [SieveFileintoAction(mailbox=mailbox)]
        
        return SieveRule(
            name=f"Domain: {domain}",
            description=f"Filter messages from {domain} domain",
            test=test,
            actions=actions,
            priority=priority
        )
    
    @staticmethod
    def create_subject_filter(
        subject_patterns: List[str],
        mailbox: str,
        comparator: SieveComparator = SieveComparator.CONTAINS,
        priority: int = 40
    ) -> SieveRule:
        """Create a rule to filter messages by subject line."""
        test = SieveHeaderTest(
            header_list=["Subject"],
            key_list=subject_patterns,
            comparator=comparator
        )
        
        actions = [SieveFileintoAction(mailbox=mailbox)]
        
        pattern_str = ", ".join(subject_patterns)
        return SieveRule(
            name=f"Subject Filter: {pattern_str[:50]}{'...' if len(pattern_str) > 50 else ''}",
            description=f"Filter messages with subject containing: {pattern_str}",
            test=test,
            actions=actions,
            priority=priority
        )
    
    @staticmethod
    def create_size_filter(
        size_mb: int,
        over: bool = True,
        action: str = "discard",
        mailbox: Optional[str] = None,
        priority: int = 5
    ) -> SieveRule:
        """Create a rule to filter messages by size."""
        size_bytes = size_mb * 1024 * 1024
        
        test = SieveSizeTest(
            comparator=SieveSizeComparator.OVER if over else SieveSizeComparator.UNDER,
            limit=size_bytes
        )
        
        if action == "discard":
            actions = [SieveDiscardAction()]
        elif action == "fileinto" and mailbox:
            actions = [SieveFileintoAction(mailbox=mailbox)]
        else:
            raise ValueError("Invalid action or missing mailbox for fileinto")
        
        direction = "over" if over else "under"
        return SieveRule(
            name=f"Size Filter: {direction} {size_mb}MB",
            description=f"Filter messages {direction} {size_mb}MB in size",
            test=test,
            actions=actions,
            priority=priority
        )
    
    @staticmethod
    def create_vacation_response(
        message: str,
        subject: Optional[str] = None,
        days: int = 7,
        addresses: Optional[List[str]] = None,
        priority: int = 1
    ) -> SieveRule:
        """Create a vacation auto-response rule."""
        # Always respond (true test)
        from .models import SieveTrueTest
        test = SieveTrueTest()
        
        vacation_action = SieveVacationAction(
            message=message,
            subject=subject,
            days=days,
            addresses=addresses
        )
        
        actions = [vacation_action]
        
        return SieveRule(
            name="Vacation Response",
            description="Auto-reply vacation message",
            test=test,
            actions=actions,
            priority=priority
        )
    
    @staticmethod
    def create_blacklist_filter(
        blacklisted_addresses: List[str],
        action: str = "discard",
        mailbox: Optional[str] = None,
        priority: int = 8
    ) -> SieveRule:
        """Create a rule to block messages from blacklisted addresses."""
        test = SieveAddressTest(
            header_list=["From"],
            key_list=blacklisted_addresses,
            comparator=SieveComparator.IS,
            address_part=SieveAddressPart.ALL
        )
        
        if action == "discard":
            actions = [SieveDiscardAction()]
        elif action == "reject":
            actions = [SieveRejectAction(reason="Message rejected by blacklist filter")]
        elif action == "fileinto" and mailbox:
            actions = [SieveFileintoAction(mailbox=mailbox)]
        else:
            raise ValueError("Invalid action or missing mailbox for fileinto")
        
        return SieveRule(
            name="Blacklist Filter",
            description="Block messages from blacklisted senders",
            test=test,
            actions=actions,
            priority=priority
        )
    
    @staticmethod
    def create_whitelist_filter(
        whitelisted_addresses: List[str],
        priority: int = 2
    ) -> SieveRule:
        """Create a rule to ensure whitelisted messages are kept."""
        test = SieveAddressTest(
            header_list=["From"],
            key_list=whitelisted_addresses,
            comparator=SieveComparator.IS,
            address_part=SieveAddressPart.ALL
        )
        
        actions = [
            SieveKeepAction(),
            SieveStopAction()  # Stop processing further rules
        ]
        
        return SieveRule(
            name="Whitelist Filter",
            description="Keep messages from whitelisted senders",
            test=test,
            actions=actions,
            priority=priority
        )


class SieveTemplates:
    """Pre-built Sieve script templates for common use cases."""
    
    @staticmethod
    def basic_email_organization() -> SieveScript:
        """Create a basic email organization script."""
        rules = [
            SieveFilterBuilder.create_spam_filter(),
            SieveFilterBuilder.create_size_filter(10, over=True, action="fileinto", mailbox="Large Messages"),
        ]
        
        return SieveScript(
            name="Basic Email Organization",
            description="Basic spam filtering and size management",
            rules=rules,
            requires=["fileinto"]
        )
    
    @staticmethod
    def comprehensive_filtering() -> SieveScript:
        """Create a comprehensive email filtering script."""
        rules = [
            # High priority whitelist
            SieveFilterBuilder.create_whitelist_filter(
                ["important@example.com", "boss@company.com"],
                priority=1
            ),
            
            # Blacklist
            SieveFilterBuilder.create_blacklist_filter(
                ["spam@badsite.com", "noreply@ads.com"],
                action="discard",
                priority=5
            ),
            
            # Size filter
            SieveFilterBuilder.create_size_filter(
                25, over=True, action="fileinto", mailbox="Large Messages", priority=8
            ),
            
            # Spam filter
            SieveFilterBuilder.create_spam_filter(priority=10),
            
            # Mailing lists
            SieveFilterBuilder.create_mailing_list_filter(
                "python-list.python.org", "Lists/Python", priority=20
            ),
            
            # Work emails
            SieveFilterBuilder.create_domain_filter(
                "company.com", "Work", priority=30
            ),
        ]
        
        return SieveScript(
            name="Comprehensive Email Filtering",
            description="Complete email filtering with whitelist, blacklist, spam, and organization",
            rules=rules,
            requires=["fileinto", "reject"]
        )
    
    @staticmethod
    def vacation_with_filtering() -> SieveScript:
        """Create a vacation script that also does basic filtering."""
        rules = [
            # Don't reply to mailing lists or automated messages
            SieveRule(
                name="Skip Vacation for Automated Messages",
                description="Don't send vacation replies to automated messages",
                test=SieveAnyOfTest(
                    tests=[
                        SieveHeaderTest(
                            header_list=["Precedence"],
                            key_list=["bulk", "list", "junk"],
                            comparator=SieveComparator.IS
                        ),
                        SieveHeaderTest(
                            header_list=["Auto-Submitted"],
                            key_list=["auto-generated", "auto-replied"],
                            comparator=SieveComparator.IS
                        ),
                        SieveExistsTest(header_list=["List-ID"]),
                    ]
                ),
                actions=[SieveStopAction()],
                priority=1
            ),
            
            # Vacation response
            SieveFilterBuilder.create_vacation_response(
                message="I am currently on vacation and will respond to your email when I return.",
                subject="Out of Office",
                days=1,
                priority=2
            ),
        ]
        
        return SieveScript(
            name="Vacation with Smart Filtering",
            description="Vacation auto-reply that skips automated messages",
            rules=rules,
            requires=["vacation"]
        )
    
    @staticmethod
    def protonmail_comprehensive() -> SieveScript:
        """Create a comprehensive ProtonMail-compatible script."""
        from .models import SieveExpireAction, SieveHeaderTest
        
        # Create Steam sales filter with proper separate rules
        steam_test = SieveHeaderTest(
            header_list=["Subject"],
            key_list=["Steam wishlist", "Steam sale", "Steam Daily Deal"],
            comparator=SieveComparator.CONTAINS
        )
        steam_rules = SieveFilterBuilder.create_expiring_fileinto_filter(
            test=steam_test,
            expire_mailbox="expiring",
            regular_mailbox="promotions",
            expire_period="day",
            expire_count="7",
            name="Steam Sales",
            description="Filter Steam sales notifications with auto-expiration",
            priority=25
        )
        
        # Create promotional filter with proper separate rules
        promotional_test = SieveHeaderTest(
            header_list=["Subject"],
            key_list=["sale", "discount", "offer", "promotion"],
            comparator=SieveComparator.CONTAINS
        )
        promotional_rules = SieveFilterBuilder.create_expiring_fileinto_filter(
            test=promotional_test,
            expire_mailbox="expiring",
            regular_mailbox="promotions",
            expire_period="day",
            expire_count="7",
            name="Promotional Email",
            description="Filter promotional emails with auto-expiration",
            priority=30
        )
        
        # Financial filter (no expiration needed)
        finance_rule = SieveFilterBuilder.create_domain_filter(
            "bankofamerica.com",
            "finance", 
            priority=20
        )
        finance_rule.name = "Bank of America"
        
        # Combine all rules
        rules = [
            # Whitelist
            SieveFilterBuilder.create_whitelist_filter(
                ["important@work.com"],
                priority=1
            ),
            
            # Size filter
            SieveFilterBuilder.create_size_filter(
                15, over=True, action="fileinto", mailbox="Large Messages", priority=8
            ),
            
            # Spam filter
            SieveFilterBuilder.create_spam_filter("Spam", priority=10),
            
            # Financial
            finance_rule,
        ]
        
        # Add Steam rules (2 separate rules)
        rules.extend(steam_rules)
        
        # Add Promotional rules (2 separate rules)  
        rules.extend(promotional_rules)
        
        return SieveScript(
            name="ProtonMail Comprehensive Filtering",
            description="Complete ProtonMail filtering with expiration and spam protection using proper separate rules",
            rules=rules,
            requires=["fileinto", "vnd.proton.expire"],
            protonmail_mode=True,
            include_spam_check=True,
            variables={
                "steam_sender": "noreply@steampowered.com",
                "finance_domains": "bankofamerica.com,chase.com"
            }
        )
