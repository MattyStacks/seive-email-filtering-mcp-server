"""
Sieve Email Filtering MCP Server

A Model Context Protocol server that provides tools for creating, managing,
and maintaining Sieve email filters.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .models import SieveScript, SieveRule
from .generator import SieveGenerator, SieveValidator
from .utils import SieveFilterBuilder, SieveTemplates
from .email_analyzer import EmailAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
app = Server("seive-email-filtering-mcp-server")

# Initialize utilities
generator = SieveGenerator()
validator = SieveValidator()
email_analyzer = EmailAnalyzer()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for Sieve email filter management."""
    return [
        Tool(
            name="create_spam_filter",
            description="Create a Sieve rule to filter spam messages into a spam folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "mailbox": {
                        "type": "string",
                        "description": "Name of the mailbox to move spam to",
                        "default": "Spam"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="create_mailing_list_filter",
            description="Create a Sieve rule to filter mailing list messages",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "string",
                        "description": "Mailing list identifier (e.g., 'python-list.python.org')"
                    },
                    "mailbox": {
                        "type": "string",
                        "description": "Name of the mailbox to move list messages to"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 20
                    }
                },
                "required": ["list_id", "mailbox"]
            }
        ),
        Tool(
            name="create_sender_filter",
            description="Create a Sieve rule to filter messages from a specific sender",
            inputSchema={
                "type": "object",
                "properties": {
                    "sender_email": {
                        "type": "string",
                        "description": "Email address of the sender to filter"
                    },
                    "mailbox": {
                        "type": "string",
                        "description": "Name of the mailbox to move messages to"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 30
                    }
                },
                "required": ["sender_email", "mailbox"]
            }
        ),
        Tool(
            name="create_domain_filter",
            description="Create a Sieve rule to filter messages from a specific domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain name to filter (e.g., 'example.com')"
                    },
                    "mailbox": {
                        "type": "string",
                        "description": "Name of the mailbox to move messages to"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 30
                    }
                },
                "required": ["domain", "mailbox"]
            }
        ),
        Tool(
            name="create_subject_filter",
            description="Create a Sieve rule to filter messages by subject line patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of subject patterns to match"
                    },
                    "mailbox": {
                        "type": "string",
                        "description": "Name of the mailbox to move messages to"
                    },
                    "comparator": {
                        "type": "string",
                        "enum": ["is", "contains", "matches", "regex"],
                        "description": "How to compare subject patterns",
                        "default": "contains"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 40
                    }
                },
                "required": ["subject_patterns", "mailbox"]
            }
        ),
        Tool(
            name="create_size_filter",
            description="Create a Sieve rule to filter messages by size",
            inputSchema={
                "type": "object",
                "properties": {
                    "size_mb": {
                        "type": "integer",
                        "description": "Size threshold in megabytes"
                    },
                    "over": {
                        "type": "boolean",
                        "description": "True to filter messages over the size, false for under",
                        "default": True
                    },
                    "action": {
                        "type": "string",
                        "enum": ["discard", "fileinto"],
                        "description": "Action to take on matching messages",
                        "default": "discard"
                    },
                    "mailbox": {
                        "type": "string",
                        "description": "Mailbox name (required if action is 'fileinto')"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 5
                    }
                },
                "required": ["size_mb"]
            }
        ),
        Tool(
            name="create_vacation_response",
            description="Create a Sieve vacation auto-reply rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Vacation message content"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Subject for vacation replies"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Days between responses to same sender",
                        "default": 7
                    },
                    "addresses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Email addresses that trigger vacation response"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 1
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="create_blacklist_filter",
            description="Create a Sieve rule to block messages from blacklisted addresses",
            inputSchema={
                "type": "object",
                "properties": {
                    "blacklisted_addresses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of email addresses to blacklist"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["discard", "reject", "fileinto"],
                        "description": "Action to take on blacklisted messages",
                        "default": "discard"
                    },
                    "mailbox": {
                        "type": "string",
                        "description": "Mailbox name (required if action is 'fileinto')"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 8
                    }
                },
                "required": ["blacklisted_addresses"]
            }
        ),
        Tool(
            name="create_whitelist_filter",
            description="Create a Sieve rule to ensure whitelisted messages are kept",
            inputSchema={
                "type": "object",
                "properties": {
                    "whitelisted_addresses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of email addresses to whitelist"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 2
                    }
                },
                "required": ["whitelisted_addresses"]
            }
        ),
        Tool(
            name="generate_sieve_script",
            description="Generate a complete Sieve script from a list of rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_name": {
                        "type": "string",
                        "description": "Name for the Sieve script"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what the script does"
                    },
                    "rules_json": {
                        "type": "string",
                        "description": "JSON string containing the rules array"
                    },
                    "requires": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Sieve extensions required",
                        "default": ["fileinto"]
                    }
                },
                "required": ["script_name", "rules_json"]
            }
        ),
        Tool(
            name="validate_sieve_script",
            description="Validate a Sieve script and return any errors",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_json": {
                        "type": "string",
                        "description": "JSON string containing the complete script"
                    }
                },
                "required": ["script_json"]
            }
        ),
        Tool(
            name="get_script_template",
            description="Get a pre-built Sieve script template",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "enum": ["basic_email_organization", "comprehensive_filtering", "vacation_with_filtering", "protonmail_comprehensive"],
                        "description": "Name of the template to retrieve"
                    }
                },
                "required": ["template_name"]
            }
        ),
        Tool(
            name="analyze_eml_file",
            description="Analyze an .eml email file and suggest Sieve filter rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "eml_content": {
                        "type": "string",
                        "description": "Content of the .eml file to analyze"
                    },
                    "generate_filter": {
                        "type": "boolean",
                        "description": "Whether to generate a Sieve filter rule from the analysis",
                        "default": True
                    }
                },
                "required": ["eml_content"]
            }
        ),
        Tool(
            name="create_protonmail_script",
            description="Generate a ProtonMail-compatible Sieve script with mandatory spam checks",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_name": {
                        "type": "string",
                        "description": "Name for the Sieve script"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what the script does"
                    },
                    "rules_json": {
                        "type": "string",
                        "description": "JSON string containing the rules array"
                    },
                    "variables": {
                        "type": "object",
                        "description": "Script-level variables as key-value pairs",
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": ["script_name", "rules_json"]
            }
        ),
        Tool(
            name="create_expiring_filter",
            description="Create a Sieve rule with ProtonMail auto-expiration",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_type": {
                        "type": "string",
                        "enum": ["sender", "domain", "subject", "promotional"],
                        "description": "Type of filter to create"
                    },
                    "criteria": {
                        "type": "string",
                        "description": "Filter criteria (email, domain, subject pattern, etc.)"
                    },
                    "mailbox": {
                        "type": "string",
                        "description": "Destination mailbox"
                    },
                    "expire_period": {
                        "type": "string",
                        "enum": ["day", "week", "month"],
                        "description": "Expiration period unit",
                        "default": "day"
                    },
                    "expire_count": {
                        "type": "string",
                        "description": "Number of periods before expiration",
                        "default": "7"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower numbers execute first)",
                        "default": 30
                    }
                },
                "required": ["filter_type", "criteria", "mailbox"]
            }
        ),
        Tool(
            name="split_multiple_fileinto_rule",
            description="Split a rule with multiple fileinto actions into separate rules for Sieve compliance",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_json": {
                        "type": "string",
                        "description": "JSON string containing a rule with multiple fileinto actions"
                    }
                },
                "required": ["rule_json"]
            }
        ),
        Tool(
            name="explain_sieve_syntax",
            description="Get explanation of Sieve syntax and capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Specific topic to explain (optional)"
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """Handle tool calls for Sieve email filter management."""
    
    try:
        if name == "create_spam_filter":
            mailbox = arguments.get("mailbox", "Spam")
            priority = arguments.get("priority", 10)
            
            rule = SieveFilterBuilder.create_spam_filter(mailbox, priority)
            rule_json = rule.model_dump_json(indent=2)
            script_text = generator.generate_script(SieveScript(
                name="Spam Filter",
                rules=[rule],
                requires=["fileinto"]
            ))
            
            return [TextContent(
                type="text",
                text=f"Created spam filter rule:\n\n**JSON:**\n```json\n{rule_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "create_mailing_list_filter":
            list_id = arguments["list_id"]
            mailbox = arguments["mailbox"]
            priority = arguments.get("priority", 20)
            
            rule = SieveFilterBuilder.create_mailing_list_filter(list_id, mailbox, priority)
            rule_json = rule.model_dump_json(indent=2)
            script_text = generator.generate_script(SieveScript(
                name=f"Mailing List Filter: {list_id}",
                rules=[rule],
                requires=["fileinto"]
            ))
            
            return [TextContent(
                type="text",
                text=f"Created mailing list filter rule:\n\n**JSON:**\n```json\n{rule_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "create_sender_filter":
            sender_email = arguments["sender_email"]
            mailbox = arguments["mailbox"]
            priority = arguments.get("priority", 30)
            
            rule = SieveFilterBuilder.create_sender_filter(sender_email, mailbox, priority)
            rule_json = rule.model_dump_json(indent=2)
            script_text = generator.generate_script(SieveScript(
                name=f"Sender Filter: {sender_email}",
                rules=[rule],
                requires=["fileinto"]
            ))
            
            return [TextContent(
                type="text",
                text=f"Created sender filter rule:\n\n**JSON:**\n```json\n{rule_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "create_domain_filter":
            domain = arguments["domain"]
            mailbox = arguments["mailbox"]
            priority = arguments.get("priority", 30)
            
            rule = SieveFilterBuilder.create_domain_filter(domain, mailbox, priority)
            rule_json = rule.model_dump_json(indent=2)
            script_text = generator.generate_script(SieveScript(
                name=f"Domain Filter: {domain}",
                rules=[rule],
                requires=["fileinto"]
            ))
            
            return [TextContent(
                type="text",
                text=f"Created domain filter rule:\n\n**JSON:**\n```json\n{rule_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "create_subject_filter":
            from .models import SieveComparator
            
            subject_patterns = arguments["subject_patterns"]
            mailbox = arguments["mailbox"]
            comparator_str = arguments.get("comparator", "contains")
            priority = arguments.get("priority", 40)
            
            comparator = SieveComparator(comparator_str)
            rule = SieveFilterBuilder.create_subject_filter(subject_patterns, mailbox, comparator, priority)
            rule_json = rule.model_dump_json(indent=2)
            script_text = generator.generate_script(SieveScript(
                name="Subject Filter",
                rules=[rule],
                requires=["fileinto"]
            ))
            
            return [TextContent(
                type="text",
                text=f"Created subject filter rule:\n\n**JSON:**\n```json\n{rule_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "create_size_filter":
            size_mb = arguments["size_mb"]
            over = arguments.get("over", True)
            action = arguments.get("action", "discard")
            mailbox = arguments.get("mailbox")
            priority = arguments.get("priority", 5)
            
            rule = SieveFilterBuilder.create_size_filter(size_mb, over, action, mailbox, priority)
            rule_json = rule.model_dump_json(indent=2)
            
            requires = ["fileinto"] if action == "fileinto" else []
            script_text = generator.generate_script(SieveScript(
                name="Size Filter",
                rules=[rule],
                requires=requires
            ))
            
            return [TextContent(
                type="text",
                text=f"Created size filter rule:\n\n**JSON:**\n```json\n{rule_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "create_vacation_response":
            message = arguments["message"]
            subject = arguments.get("subject")
            days = arguments.get("days", 7)
            addresses = arguments.get("addresses")
            priority = arguments.get("priority", 1)
            
            rule = SieveFilterBuilder.create_vacation_response(message, subject, days, addresses, priority)
            rule_json = rule.model_dump_json(indent=2)
            script_text = generator.generate_script(SieveScript(
                name="Vacation Response",
                rules=[rule],
                requires=["vacation"]
            ))
            
            return [TextContent(
                type="text",
                text=f"Created vacation response rule:\n\n**JSON:**\n```json\n{rule_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "create_blacklist_filter":
            blacklisted_addresses = arguments["blacklisted_addresses"]
            action = arguments.get("action", "discard")
            mailbox = arguments.get("mailbox")
            priority = arguments.get("priority", 8)
            
            rule = SieveFilterBuilder.create_blacklist_filter(blacklisted_addresses, action, mailbox, priority)
            rule_json = rule.model_dump_json(indent=2)
            
            requires = []
            if action == "fileinto":
                requires.append("fileinto")
            elif action == "reject":
                requires.append("reject")
            
            script_text = generator.generate_script(SieveScript(
                name="Blacklist Filter",
                rules=[rule],
                requires=requires
            ))
            
            return [TextContent(
                type="text",
                text=f"Created blacklist filter rule:\n\n**JSON:**\n```json\n{rule_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "create_whitelist_filter":
            whitelisted_addresses = arguments["whitelisted_addresses"]
            priority = arguments.get("priority", 2)
            
            rule = SieveFilterBuilder.create_whitelist_filter(whitelisted_addresses, priority)
            rule_json = rule.model_dump_json(indent=2)
            script_text = generator.generate_script(SieveScript(
                name="Whitelist Filter",
                rules=[rule],
                requires=[]
            ))
            
            return [TextContent(
                type="text",
                text=f"Created whitelist filter rule:\n\n**JSON:**\n```json\n{rule_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "generate_sieve_script":
            script_name = arguments["script_name"]
            description = arguments.get("description")
            rules_json = arguments["rules_json"]
            requires = arguments.get("requires", ["fileinto"])
            
            # Parse rules from JSON
            rules_data = json.loads(rules_json)
            rules = [SieveRule.model_validate(rule_data) for rule_data in rules_data]
            
            script = SieveScript(
                name=script_name,
                description=description,
                rules=rules,
                requires=requires
            )
            
            # Validate the script
            errors = validator.validate_script(script)
            if errors:
                error_text = "\n".join(f"- {error}" for error in errors)
                return [TextContent(
                    type="text",
                    text=f"Script validation failed:\n\n{error_text}"
                )]
            
            script_text = generator.generate_script(script)
            script_json = script.model_dump_json(indent=2)
            
            return [TextContent(
                type="text",
                text=f"Generated Sieve script:\n\n**JSON:**\n```json\n{script_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "validate_sieve_script":
            script_json = arguments["script_json"]
            
            try:
                script_data = json.loads(script_json)
                script = SieveScript.model_validate(script_data)
                errors = validator.validate_script(script)
                
                if errors:
                    error_text = "\n".join(f"- {error}" for error in errors)
                    return [TextContent(
                        type="text",
                        text=f"Script validation failed:\n\n{error_text}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text="Script validation passed! No errors found."
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Failed to parse script JSON: {str(e)}"
                )]
        
        elif name == "get_script_template":
            template_name = arguments["template_name"]
            
            if template_name == "basic_email_organization":
                script = SieveTemplates.basic_email_organization()
            elif template_name == "comprehensive_filtering":
                script = SieveTemplates.comprehensive_filtering()
            elif template_name == "vacation_with_filtering":
                script = SieveTemplates.vacation_with_filtering()
            elif template_name == "protonmail_comprehensive":
                script = SieveTemplates.protonmail_comprehensive()
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown template: {template_name}"
                )]
            
            script_text = generator.generate_script(script)
            script_json = script.model_dump_json(indent=2)
            
            return [TextContent(
                type="text",
                text=f"Template: {template_name}\n\n**JSON:**\n```json\n{script_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
            )]
        
        elif name == "analyze_eml_file":
            eml_content = arguments["eml_content"]
            generate_filter = arguments.get("generate_filter", True)
            
            try:
                # Parse the email
                email_msg = email_analyzer.parse_eml_file(eml_content)
                
                # Analyze the email
                analysis = email_analyzer.analyze_email(email_msg)
                
                # Create response
                response_text = f"**Email Analysis Results:**\n\n"
                response_text += f"**From:** {email_msg.from_address}\n"
                response_text += f"**Subject:** {email_msg.subject}\n"
                response_text += f"**Suggested Filter Name:** {analysis.suggested_filter_name}\n"
                response_text += f"**Suggested Folder:** {analysis.suggested_folder}\n"
                response_text += f"**Confidence Score:** {analysis.confidence_score:.2f}\n\n"
                
                response_text += f"**Detected Patterns:**\n"
                if analysis.sender_patterns:
                    response_text += f"- Sender patterns: {', '.join(analysis.sender_patterns)}\n"
                if analysis.domain_patterns:
                    response_text += f"- Domain patterns: {', '.join(analysis.domain_patterns)}\n"
                if analysis.subject_patterns:
                    response_text += f"- Subject patterns: {', '.join(analysis.subject_patterns[:3])}\n"
                if analysis.content_keywords:
                    response_text += f"- Content keywords: {', '.join(analysis.content_keywords[:5])}\n"
                
                response_text += f"\n**Recommended Actions:** {', '.join(analysis.recommended_actions)}\n"
                response_text += f"**Auto-expiration recommended:** {'Yes' if analysis.requires_expiration else 'No'}\n"
                
                if generate_filter:
                    # Generate the filter(s) - may create multiple rules for expiring filters
                    if analysis.requires_expiration and "expire" in analysis.recommended_actions:
                        rules = email_analyzer.generate_expiring_filter_from_analysis(analysis)
                        rules_json = [rule.model_dump() for rule in rules]
                        rules_json_str = json.dumps(rules_json, indent=2)
                        
                        response_text += f"\n\n**Generated Filter Rules (Separate rules for proper Sieve syntax):**\n```json\n{rules_json_str}\n```\n\n"
                    else:
                        # Single rule for non-expiring filters
                        rule = email_analyzer.generate_filter_from_analysis(analysis)
                        rules = [rule]
                        rule_json = rule.model_dump_json(indent=2)
                        
                        response_text += f"\n\n**Generated Filter Rule:**\n```json\n{rule_json}\n```\n\n"
                    
                    # Generate script
                    script = SieveScript(
                        name=analysis.suggested_filter_name,
                        description=f"Filter generated from email analysis",
                        rules=rules,
                        requires=["fileinto"] + (["vnd.proton.expire"] if analysis.requires_expiration else []),
                        protonmail_mode=True,
                        include_spam_check=True
                    )
                    script_text = generator.generate_script(script)
                    
                    response_text += f"**Generated Sieve Script:**\n```sieve\n{script_text}\n```"
                    
                    if analysis.requires_expiration:
                        response_text += f"\n\n**Note:** Created {len(rules)} separate rules to comply with Sieve syntax - multiple fileinto actions require separate rules."
                
                return [TextContent(type="text", text=response_text)]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error analyzing email: {str(e)}"
                )]
        
        elif name == "create_protonmail_script":
            script_name = arguments["script_name"]
            description = arguments.get("description")
            rules_json = arguments["rules_json"]
            variables = arguments.get("variables", {})
            
            try:
                # Parse rules from JSON
                rules_data = json.loads(rules_json)
                rules = [SieveRule.model_validate(rule_data) for rule_data in rules_data]
                
                script = SieveScript(
                    name=script_name,
                    description=description,
                    rules=rules,
                    requires=["fileinto", "vnd.proton.expire"],
                    protonmail_mode=True,
                    include_spam_check=True,
                    variables=variables
                )
                
                # Validate the script
                errors = validator.validate_script(script)
                if errors:
                    error_text = "\n".join(f"- {error}" for error in errors)
                    return [TextContent(
                        type="text",
                        text=f"Script validation failed:\n\n{error_text}"
                    )]
                
                script_text = generator.generate_script(script)
                script_json = script.model_dump_json(indent=2)
                
                return [TextContent(
                    type="text",
                    text=f"Generated ProtonMail Sieve script:\n\n**JSON:**\n```json\n{script_json}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```"
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error creating ProtonMail script: {str(e)}"
                )]
        
        elif name == "create_expiring_filter":
            from .models import SieveExpireAction, SieveComparator
            
            filter_type = arguments["filter_type"]
            criteria = arguments["criteria"]
            mailbox = arguments["mailbox"]
            expire_period = arguments.get("expire_period", "day")
            expire_count = arguments.get("expire_count", "7")
            priority = arguments.get("priority", 30)
            
            try:
                # Create the base test based on filter type
                if filter_type == "sender":
                    from .models import SieveAddressTest, SieveAddressPart
                    test = SieveAddressTest(
                        header_list=["From"],
                        key_list=[criteria],
                        comparator=SieveComparator.IS,
                        address_part=SieveAddressPart.ALL
                    )
                elif filter_type == "domain":
                    from .models import SieveAddressTest, SieveAddressPart
                    test = SieveAddressTest(
                        header_list=["From"],
                        key_list=[criteria],
                        comparator=SieveComparator.IS,
                        address_part=SieveAddressPart.DOMAIN
                    )
                elif filter_type == "subject":
                    from .models import SieveHeaderTest
                    test = SieveHeaderTest(
                        header_list=["Subject"],
                        key_list=[criteria],
                        comparator=SieveComparator.CONTAINS
                    )
                elif filter_type == "promotional":
                    from .models import SieveHeaderTest
                    test = SieveHeaderTest(
                        header_list=["Subject"],
                        key_list=["sale", "discount", "offer", "promotion"],
                        comparator=SieveComparator.CONTAINS
                    )
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown filter type: {filter_type}"
                    )]
                
                # Create separate rules for expiring + regular filing
                rules = SieveFilterBuilder.create_expiring_fileinto_filter(
                    test=test,
                    expire_mailbox="expiring",
                    regular_mailbox=mailbox,
                    expire_period=expire_period,
                    expire_count=expire_count,
                    name=f"{filter_type.title()} Filter",
                    description=f"Auto-expiring filter for {criteria}",
                    priority=priority
                )
                
                # Convert rules to JSON for display
                rules_json = [rule.model_dump() for rule in rules]
                rules_json_str = json.dumps(rules_json, indent=2)
                
                # Generate script with both rules
                script = SieveScript(
                    name=f"Expiring {filter_type.title()} Filter",
                    description=f"Auto-expiring filter for {criteria} with separate rules for proper Sieve syntax",
                    rules=rules,
                    requires=["fileinto", "vnd.proton.expire"],
                    protonmail_mode=True,
                    include_spam_check=True
                )
                script_text = generator.generate_script(script)
                
                return [TextContent(
                    type="text",
                    text=f"Created expiring {filter_type} filter with separate rules:\n\n**Rules JSON:**\n```json\n{rules_json_str}\n```\n\n**Sieve Script:**\n```sieve\n{script_text}\n```\n\n**Note:** This creates two separate rules to comply with Sieve syntax requirements - multiple fileinto actions cannot be in the same rule."
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error creating expiring filter: {str(e)}"
                )]
        
        elif name == "split_multiple_fileinto_rule":
            rule_json = arguments["rule_json"]
            
            try:
                # Parse the rule
                rule_data = json.loads(rule_json)
                rule = SieveRule.model_validate(rule_data)
                
                # Split the rule if it has multiple fileinto actions
                split_rules = SieveFilterBuilder.split_multiple_fileinto_actions(rule)
                
                if len(split_rules) == 1:
                    return [TextContent(
                        type="text",
                        text="No splitting needed - the rule has only one or no fileinto actions.\n\n" +
                             "**Original Rule:**\n```json\n" + rule.model_dump_json(indent=2) + "\n```"
                    )]
                
                # Convert split rules to JSON
                split_rules_json = [rule.model_dump() for rule in split_rules]
                split_rules_json_str = json.dumps(split_rules_json, indent=2)
                
                # Generate script with split rules
                script = SieveScript(
                    name="Split Rules Script",
                    description="Rules split to comply with Sieve syntax - separate rules for each fileinto action",
                    rules=split_rules,
                    requires=["fileinto"],
                    protonmail_mode=True,
                    include_spam_check=True
                )
                script_text = generator.generate_script(script)
                
                return [TextContent(
                    type="text",
                    text=f"Successfully split rule into {len(split_rules)} separate rules:\n\n" +
                         f"**Original Rule:**\n```json\n{rule.model_dump_json(indent=2)}\n```\n\n" +
                         f"**Split Rules:**\n```json\n{split_rules_json_str}\n```\n\n" +
                         f"**Generated Sieve Script:**\n```sieve\n{script_text}\n```\n\n" +
                         f"**Note:** Sieve syntax requires separate rules for each fileinto action. " +
                         f"Multiple fileinto actions in a single rule are not allowed."
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error splitting rule: {str(e)}"
                )]
        
        elif name == "explain_sieve_syntax":
            topic = arguments.get("topic", "")
            
            if not topic or topic.lower() in ["overview", "general"]:
                explanation = """
# Sieve Email Filtering Syntax Overview

Sieve is a standardized email filtering language (RFC 5228) used to automatically process incoming email messages.

## Basic Structure
A Sieve script consists of:
1. **require** statements (optional) - declare needed extensions
2. **rules** - conditional statements that test messages and take actions

## Tests
Common test types:
- `header` - test email headers
- `address` - test email addresses in headers
- `body` - test message body content
- `size` - test message size
- `exists` - check if headers exist
- `allof` - all tests must be true
- `anyof` - any test must be true
- `not` - negate a test

## Actions
Common actions:
- `keep` - keep message in inbox
- `fileinto` - move to specified folder
- `discard` - delete message
- `redirect` - forward to another address
- `reject` - reject with error message
- `vacation` - send auto-reply
- `stop` - stop processing further rules

## Example Rule
```sieve
if header :contains "subject" "spam" {
    fileinto "Spam";
    stop;
}
```
"""
            elif topic.lower() in ["test", "tests"]:
                explanation = """
# Sieve Tests

Tests are conditions that evaluate email messages.

## Header Test
```sieve
header [:comparator] <header-names> <key-list>
```
- `:is` - exact match (default)
- `:contains` - substring match
- `:matches` - wildcard match (* and ?)
- `:regex` - regular expression match

## Address Test
```sieve
address [:comparator] [:address-part] <header-names> <key-list>
```
- `:all` - entire address (default)
- `:localpart` - part before @
- `:domain` - part after @

## Size Test
```sieve
size :over <limit>
size :under <limit>
```

## Logical Tests
```sieve
allof (test1, test2, test3)  # all must be true
anyof (test1, test2, test3)  # any must be true
not test                     # negate result
```
"""
            elif topic.lower() in ["action", "actions"]:
                explanation = """
# Sieve Actions

Actions specify what to do when a test matches.

## Basic Actions
- `keep;` - keep in inbox (default)
- `discard;` - silently delete
- `stop;` - stop processing more rules

## File Management
- `fileinto "folder";` - move to folder
- `redirect "email@example.com";` - forward message

## Response Actions
- `reject "reason";` - reject with bounce message
- `vacation :days 7 "I'm away";` - auto-reply

## Vacation Parameters
```sieve
vacation :days 7 
         :subject "Out of Office"
         :addresses ["me@work.com"]
         "I am currently away...";
```
"""
            else:
                explanation = f"Unknown topic: {topic}. Available topics: overview, tests, actions"
            
            return [TextContent(
                type="text",
                text=explanation
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]


def main():
    """Main entry point for the server."""
    import asyncio
    
    async def run_server():
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
