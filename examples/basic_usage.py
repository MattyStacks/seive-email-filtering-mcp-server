"""
Example usage of the Sieve Email Filtering MCP Server.
"""

import asyncio
import json
from seive_email_filtering_mcp_server.models import SieveScript, SieveRule
from seive_email_filtering_mcp_server.generator import SieveGenerator
from seive_email_filtering_mcp_server.utils import SieveFilterBuilder, SieveTemplates


async def main():
    """Demonstrate the Sieve email filtering capabilities."""
    generator = SieveGenerator()
    
    print("=== Sieve Email Filtering MCP Server Examples ===\n")
    
    # Example 1: Create a spam filter
    print("1. Creating a spam filter:")
    spam_rule = SieveFilterBuilder.create_spam_filter("Junk", priority=10)
    print(f"Rule: {spam_rule.name}")
    print(f"Description: {spam_rule.description}")
    
    script = SieveScript(
        name="Spam Filter Example",
        rules=[spam_rule],
        requires=["fileinto"]
    )
    
    print("\nGenerated Sieve script:")
    print(generator.generate_script(script))
    print("\n" + "="*60 + "\n")
    
    # Example 2: Create a comprehensive filtering setup
    print("2. Creating comprehensive email filtering:")
    
    rules = [
        # Whitelist important senders
        SieveFilterBuilder.create_whitelist_filter(
            ["boss@company.com", "important@client.com"],
            priority=1
        ),
        
        # Block spam
        SieveFilterBuilder.create_spam_filter("Spam", priority=10),
        
        # Filter mailing lists
        SieveFilterBuilder.create_mailing_list_filter(
            "python-dev@python.org", 
            "Lists/Python", 
            priority=20
        ),
        
        # Filter by domain
        SieveFilterBuilder.create_domain_filter(
            "company.com", 
            "Work", 
            priority=30
        ),
        
        # Size filter for large messages
        SieveFilterBuilder.create_size_filter(
            10,  # 10MB
            over=True,
            action="fileinto",
            mailbox="Large Messages",
            priority=5
        )
    ]
    
    comprehensive_script = SieveScript(
        name="Comprehensive Email Filtering",
        description="Complete email organization with multiple filters",
        rules=rules,
        requires=["fileinto"]
    )
    
    print(f"Script: {comprehensive_script.name}")
    print(f"Number of rules: {len(comprehensive_script.rules)}")
    print("\nGenerated Sieve script:")
    print(generator.generate_script(comprehensive_script))
    print("\n" + "="*60 + "\n")
    
    # Example 3: Vacation response
    print("3. Creating vacation response:")
    
    vacation_script = SieveTemplates.vacation_with_filtering()
    print(f"Script: {vacation_script.name}")
    print("\nGenerated Sieve script:")
    print(generator.generate_script(vacation_script))
    print("\n" + "="*60 + "\n")
    
    # Example 4: Show JSON representation
    print("4. JSON representation of a rule:")
    
    sender_rule = SieveFilterBuilder.create_sender_filter(
        "newsletter@example.com",
        "Newsletters",
        priority=25
    )
    
    print("Rule as JSON:")
    print(json.dumps(sender_rule.model_dump(), indent=2))
    
    print("\n" + "="*60 + "\n")
    
    # Example 5: Template usage
    print("5. Using pre-built templates:")
    
    templates = [
        ("Basic Email Organization", SieveTemplates.basic_email_organization()),
        ("Comprehensive Filtering", SieveTemplates.comprehensive_filtering()),
        ("Vacation with Filtering", SieveTemplates.vacation_with_filtering())
    ]
    
    for name, template in templates:
        print(f"\nTemplate: {name}")
        print(f"Rules: {len(template.rules)}")
        print(f"Required extensions: {', '.join(template.requires)}")
        
        # Show first few lines of generated script
        script_lines = generator.generate_script(template).split('\n')
        preview_lines = script_lines[:10]
        print("Preview:")
        for line in preview_lines:
            print(f"  {line}")
        if len(script_lines) > 10:
            print(f"  ... ({len(script_lines) - 10} more lines)")


if __name__ == "__main__":
    asyncio.run(main())
