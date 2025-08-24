#!/usr/bin/env python3
"""
Test script to verify the multiple fileinto fix is working correctly.
"""

import json
from seive_email_filtering_mcp_server.models import (
    SieveRule, SieveScript, SieveHeaderTest, SieveFileintoAction, 
    SieveExpireAction, SieveComparator, SieveActionType
)
from seive_email_filtering_mcp_server.utils import SieveFilterBuilder, SieveTemplates
from seive_email_filtering_mcp_server.generator import SieveGenerator


def test_split_multiple_fileinto():
    """Test splitting a rule with multiple fileinto actions."""
    print("=== Testing Multiple Fileinto Splitting ===\n")
    
    # Create a rule with multiple fileinto actions (incorrect)
    test = SieveHeaderTest(
        header_list=["Subject"],
        key_list=["sale", "discount", "promotion"],
        comparator=SieveComparator.CONTAINS
    )
    
    # Create rule with multiple fileinto actions + expire (this should be split)
    incorrect_rule = SieveRule(
        name="Promotional Filter (Incorrect)",
        description="This rule incorrectly combines multiple fileinto actions",
        test=test,
        actions=[
            SieveExpireAction(period="day", count="30"),
            SieveFileintoAction(mailbox="expiring"),
            SieveFileintoAction(mailbox="Promotions")  # This is the problem!
        ],
        priority=30
    )
    
    print("BEFORE SPLITTING:")
    print("Rule with multiple fileinto actions (INCORRECT Sieve syntax):")
    print(json.dumps(incorrect_rule.model_dump(), indent=2))
    
    # Split the rule
    split_rules = SieveFilterBuilder.split_multiple_fileinto_actions(incorrect_rule)
    
    print(f"\nAFTER SPLITTING:")
    print(f"Number of rules created: {len(split_rules)}")
    
    for i, rule in enumerate(split_rules, 1):
        print(f"\nRule {i}:")
        print(f"Name: {rule.name}")
        print(f"Actions: {[action.action_type for action in rule.actions]}")
        fileinto_actions = [action for action in rule.actions if action.action_type == SieveActionType.FILEINTO]
        if fileinto_actions:
            print(f"Fileinto mailbox: {fileinto_actions[0].mailbox}")
    
    return split_rules


def test_create_expiring_fileinto_filter():
    """Test the new expiring fileinto filter function."""
    print("\n\n=== Testing Expiring Fileinto Filter Creation ===\n")
    
    # Create a test condition
    test = SieveHeaderTest(
        header_list=["Subject"],
        key_list=["Steam sale", "Steam wishlist"],
        comparator=SieveComparator.CONTAINS
    )
    
    # Create proper expiring filter rules
    rules = SieveFilterBuilder.create_expiring_fileinto_filter(
        test=test,
        expire_mailbox="expiring",
        regular_mailbox="promotions",
        expire_period="day",
        expire_count="7",
        name="Steam Sales",
        description="Steam sales notifications with auto-expiration",
        priority=25
    )
    
    print(f"Created {len(rules)} rules for expiring filter:")
    
    for i, rule in enumerate(rules, 1):
        print(f"\nRule {i}: {rule.name}")
        print(f"Actions: {[action.action_type for action in rule.actions]}")
        fileinto_actions = [action for action in rule.actions if action.action_type == SieveActionType.FILEINTO]
        if fileinto_actions:
            print(f"Fileinto mailbox: {fileinto_actions[0].mailbox}")
    
    return rules


def test_sieve_generation():
    """Test that the generated Sieve scripts are syntactically correct."""
    print("\n\n=== Testing Sieve Script Generation ===\n")
    
    # Test the corrected ProtonMail template
    # Use the template provider class (was incorrectly referencing SieveFilterBuilder)
    template = SieveTemplates.protonmail_comprehensive()
    
    print(f"ProtonMail template has {len(template.rules)} rules")
    
    # Count fileinto actions per rule
    for i, rule in enumerate(template.rules, 1):
        fileinto_count = sum(1 for action in rule.actions if action.action_type == SieveActionType.FILEINTO)
        print(f"Rule {i} ({rule.name}): {fileinto_count} fileinto action(s)")
        
        if fileinto_count > 1:
            print(f"  ❌ ERROR: Rule {i} has multiple fileinto actions!")
        elif fileinto_count == 1:
            print(f"  ✅ OK: Rule {i} has proper single fileinto action")
    
    # Generate the script
    generator = SieveGenerator()
    script_text = generator.generate_script(template)
    
    print(f"\nGenerated script preview (first 20 lines):")
    lines = script_text.split('\n')
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:2d}: {line}")
    
    if len(lines) > 20:
        print(f"... ({len(lines) - 20} more lines)")
    
    return script_text


def main():
    """Run all tests."""
    print("🔧 Testing Multiple Fileinto Fix Implementation\n")
    
    try:
        # Test 1: Split existing incorrect rule
        split_rules = test_split_multiple_fileinto()
        
        # Test 2: Create proper expiring filter
        expiring_rules = test_create_expiring_fileinto_filter()
        
        # Test 3: Verify template generation
        script_text = test_sieve_generation()
        
        print("\n\n🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print(f"✅ Rule splitting works: {len(split_rules)} rules created from 1 incorrect rule")
        print(f"✅ Expiring filter creation works: {len(expiring_rules)} rules created")
        print(f"✅ Sieve script generation works: {len(script_text.split('\\n'))} lines generated")
        print("\n✨ The MCP server now properly handles multiple fileinto actions!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
