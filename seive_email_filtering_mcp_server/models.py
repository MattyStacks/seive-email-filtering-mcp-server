"""
Sieve filter models and data structures.
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum


class SieveTestType(str, Enum):
    """Sieve test types."""
    ADDRESS = "address"
    ALLOF = "allof"
    ANYOF = "anyof"
    BODY = "body"
    EXISTS = "exists"
    FALSE = "false"
    HEADER = "header"
    NOT = "not"
    SIZE = "size"
    TRUE = "true"


class SieveActionType(str, Enum):
    """Sieve action types."""
    DISCARD = "discard"
    FILEINTO = "fileinto"
    KEEP = "keep"
    REDIRECT = "redirect"
    REJECT = "reject"
    STOP = "stop"
    VACATION = "vacation"
    # ProtonMail specific actions
    EXPIRE = "expire"
    ADDFLAG = "addflag"
    REMOVEFLAG = "removeflag"
    SETFLAG = "setflag"


class SieveComparator(str, Enum):
    """Sieve string comparison operators."""
    IS = "is"
    CONTAINS = "contains"
    MATCHES = "matches"
    REGEX = "regex"


class SieveAddressPart(str, Enum):
    """Address parts for address test."""
    ALL = "all"
    LOCALPART = "localpart"
    DOMAIN = "domain"


class SieveSizeComparator(str, Enum):
    """Size comparison operators."""
    OVER = "over"
    UNDER = "under"


class SieveTest(BaseModel):
    """Base class for Sieve tests."""
    test_type: SieveTestType
    
    class Config:
        use_enum_values = True


class SieveHeaderTest(SieveTest):
    """Header test for checking email headers."""
    test_type: Literal[SieveTestType.HEADER] = SieveTestType.HEADER
    comparator: SieveComparator = SieveComparator.IS
    header_list: List[str] = Field(..., description="List of header names to test")
    key_list: List[str] = Field(..., description="List of values to test against")


class SieveAddressTest(SieveTest):
    """Address test for checking email addresses."""
    test_type: Literal[SieveTestType.ADDRESS] = SieveTestType.ADDRESS
    comparator: SieveComparator = SieveComparator.IS
    address_part: SieveAddressPart = SieveAddressPart.ALL
    header_list: List[str] = Field(..., description="List of address headers (from, to, cc, etc.)")
    key_list: List[str] = Field(..., description="List of addresses to test against")


class SieveBodyTest(SieveTest):
    """Body test for checking email body content."""
    test_type: Literal[SieveTestType.BODY] = SieveTestType.BODY
    comparator: SieveComparator = SieveComparator.CONTAINS
    key_list: List[str] = Field(..., description="List of strings to search for in body")


class SieveExistsTest(SieveTest):
    """Exists test for checking if headers exist."""
    test_type: Literal[SieveTestType.EXISTS] = SieveTestType.EXISTS
    header_list: List[str] = Field(..., description="List of header names to check for existence")


class SieveSizeTest(SieveTest):
    """Size test for checking email size."""
    test_type: Literal[SieveTestType.SIZE] = SieveTestType.SIZE
    comparator: SieveSizeComparator
    limit: int = Field(..., description="Size limit in bytes")


class SieveAllOfTest(SieveTest):
    """AllOf test - all sub-tests must be true."""
    test_type: Literal[SieveTestType.ALLOF] = SieveTestType.ALLOF
    tests: List["SieveTestUnion"] = Field(..., description="List of tests that must all be true")


class SieveAnyOfTest(SieveTest):
    """AnyOf test - any sub-test must be true."""
    test_type: Literal[SieveTestType.ANYOF] = SieveTestType.ANYOF
    tests: List["SieveTestUnion"] = Field(..., description="List of tests where at least one must be true")


class SieveNotTest(SieveTest):
    """Not test - negates the result of a sub-test."""
    test_type: Literal[SieveTestType.NOT] = SieveTestType.NOT
    test: "SieveTestUnion" = Field(..., description="Test to negate")


class SieveTrueTest(SieveTest):
    """True test - always evaluates to true."""
    test_type: Literal[SieveTestType.TRUE] = SieveTestType.TRUE


class SieveFalseTest(SieveTest):
    """False test - always evaluates to false."""
    test_type: Literal[SieveTestType.FALSE] = SieveTestType.FALSE


# Union type for all possible tests
SieveTestUnion = Union[
    SieveHeaderTest,
    SieveAddressTest,
    SieveBodyTest,
    SieveExistsTest,
    SieveSizeTest,
    SieveAllOfTest,
    SieveAnyOfTest,
    SieveNotTest,
    SieveTrueTest,
    SieveFalseTest,
]


class SieveAction(BaseModel):
    """Base class for Sieve actions."""
    action_type: SieveActionType
    
    class Config:
        use_enum_values = True


class SieveDiscardAction(SieveAction):
    """Discard action - silently discards the message."""
    action_type: Literal[SieveActionType.DISCARD] = SieveActionType.DISCARD


class SieveKeepAction(SieveAction):
    """Keep action - keeps the message in the inbox."""
    action_type: Literal[SieveActionType.KEEP] = SieveActionType.KEEP


class SieveStopAction(SieveAction):
    """Stop action - stops processing further rules."""
    action_type: Literal[SieveActionType.STOP] = SieveActionType.STOP


class SieveFileintoAction(SieveAction):
    """Fileinto action - files the message into a specific mailbox."""
    action_type: Literal[SieveActionType.FILEINTO] = SieveActionType.FILEINTO
    mailbox: str = Field(..., description="Name of the mailbox to file into")


class SieveRedirectAction(SieveAction):
    """Redirect action - forwards the message to another address."""
    action_type: Literal[SieveActionType.REDIRECT] = SieveActionType.REDIRECT
    address: str = Field(..., description="Email address to redirect to")


class SieveRejectAction(SieveAction):
    """Reject action - rejects the message with a reason."""
    action_type: Literal[SieveActionType.REJECT] = SieveActionType.REJECT
    reason: str = Field(..., description="Reason for rejection")


class SieveVacationAction(SieveAction):
    """Vacation action - sends an auto-reply message."""
    action_type: Literal[SieveActionType.VACATION] = SieveActionType.VACATION
    subject: Optional[str] = Field(None, description="Subject for vacation message")
    message: str = Field(..., description="Vacation message content")
    days: Optional[int] = Field(7, description="Days between vacation responses to same sender")
    addresses: Optional[List[str]] = Field(None, description="Addresses that trigger vacation response")


class SieveExpireAction(SieveAction):
    """Expire action - automatically delete messages after specified time (ProtonMail)."""
    action_type: Literal[SieveActionType.EXPIRE] = SieveActionType.EXPIRE
    period: str = Field(..., description="Time period (day, week, month)")
    count: str = Field(..., description="Number of periods")


class SieveAddFlagAction(SieveAction):
    """Add flag action - adds IMAP flags to messages."""
    action_type: Literal[SieveActionType.ADDFLAG] = SieveActionType.ADDFLAG
    flags: List[str] = Field(..., description="IMAP flags to add")


class SieveRemoveFlagAction(SieveAction):
    """Remove flag action - removes IMAP flags from messages."""
    action_type: Literal[SieveActionType.REMOVEFLAG] = SieveActionType.REMOVEFLAG
    flags: List[str] = Field(..., description="IMAP flags to remove")


class SieveSetFlagAction(SieveAction):
    """Set flag action - sets IMAP flags on messages."""
    action_type: Literal[SieveActionType.SETFLAG] = SieveActionType.SETFLAG
    flags: List[str] = Field(..., description="IMAP flags to set")


# Union type for all possible actions
SieveActionUnion = Union[
    SieveDiscardAction,
    SieveKeepAction,
    SieveStopAction,
    SieveFileintoAction,
    SieveRedirectAction,
    SieveRejectAction,
    SieveVacationAction,
    SieveExpireAction,
    SieveAddFlagAction,
    SieveRemoveFlagAction,
    SieveSetFlagAction,
]


class SieveRule(BaseModel):
    """A Sieve email filtering rule."""
    name: str = Field(..., description="Human-readable name for the rule")
    description: Optional[str] = Field(None, description="Description of what the rule does")
    enabled: bool = Field(True, description="Whether the rule is enabled")
    test: SieveTestUnion = Field(..., description="The test condition for the rule")
    actions: List[SieveActionUnion] = Field(..., description="Actions to take when test is true")
    priority: int = Field(0, description="Rule priority (lower numbers execute first)")


class SieveScript(BaseModel):
    """A complete Sieve script containing multiple rules."""
    name: str = Field(..., description="Name of the Sieve script")
    description: Optional[str] = Field(None, description="Description of the script")
    rules: List[SieveRule] = Field(default_factory=list, description="List of rules in the script")
    requires: List[str] = Field(default_factory=list, description="Sieve extensions required")
    protonmail_mode: bool = Field(False, description="Generate ProtonMail-specific features")
    include_spam_check: bool = Field(False, description="Include mandatory spam threshold check")
    variables: Dict[str, str] = Field(default_factory=dict, description="Script-level variables")


class EmailMessage(BaseModel):
    """Parsed email message from .eml file."""
    headers: Dict[str, str] = Field(default_factory=dict, description="Email headers")
    from_address: Optional[str] = Field(None, description="From address")
    to_addresses: List[str] = Field(default_factory=list, description="To addresses")
    subject: Optional[str] = Field(None, description="Email subject")
    body: Optional[str] = Field(None, description="Email body content")
    raw_content: Optional[str] = Field(None, description="Raw email content")


class FilterAnalysis(BaseModel):
    """Analysis results from email message for filter generation."""
    suggested_filter_name: str = Field(..., description="Suggested name for the filter")
    sender_patterns: List[str] = Field(default_factory=list, description="Detected sender patterns")
    subject_patterns: List[str] = Field(default_factory=list, description="Detected subject patterns")
    domain_patterns: List[str] = Field(default_factory=list, description="Detected domain patterns")
    content_keywords: List[str] = Field(default_factory=list, description="Key content patterns")
    suggested_folder: str = Field(..., description="Suggested destination folder")
    confidence_score: float = Field(..., description="Confidence in the analysis (0-1)")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    requires_expiration: bool = Field(False, description="Whether message should auto-expire")


# Update forward references
SieveAllOfTest.model_rebuild()
SieveAnyOfTest.model_rebuild()
SieveNotTest.model_rebuild()
