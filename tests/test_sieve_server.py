"""
Tests for the Sieve Email Filtering MCP Server.
"""

import json
from seive_email_filtering_mcp_server.models import (
    SieveScript, SieveRule, SieveHeaderTest, SieveFileintoAction,
    SieveComparator, SieveTestType, SieveActionType
)
from seive_email_filtering_mcp_server.generator import SieveGenerator, SieveValidator
from seive_email_filtering_mcp_server.utils import SieveFilterBuilder, SieveTemplates


class TestSieveModels:
    """Test Sieve data models."""
    
    def test_header_test_creation(self):
        """Test creating a header test."""
        test = SieveHeaderTest(
            header_list=["Subject"],
            key_list=["spam"],
            comparator=SieveComparator.CONTAINS
        )
        
        assert test.test_type == SieveTestType.HEADER
        assert test.header_list == ["Subject"]
        assert test.key_list == ["spam"]
        assert test.comparator == SieveComparator.CONTAINS
    
    def test_fileinto_action_creation(self):
        """Test creating a fileinto action."""
        action = SieveFileintoAction(mailbox="Spam")
        
        assert action.action_type == SieveActionType.FILEINTO
        assert action.mailbox == "Spam"
    
    def test_rule_creation(self):
        """Test creating a complete rule."""
        test = SieveHeaderTest(
            header_list=["Subject"],
            key_list=["spam"]
        )
        action = SieveFileintoAction(mailbox="Spam")
        
        rule = SieveRule(
            name="Spam Filter",
            description="Filter spam messages",
            test=test,
            actions=[action],
            priority=10
        )
        
        assert rule.name == "Spam Filter"
        assert rule.enabled == True  # default
        assert rule.priority == 10
        assert len(rule.actions) == 1


class TestSieveGenerator:
    """Test Sieve script generation."""
    
    def setUp(self):
        self.generator = SieveGenerator()
    
    def test_header_test_generation(self):
        """Test generating header test code."""
        test = SieveHeaderTest(
            header_list=["Subject"],
            key_list=["spam"],
            comparator=SieveComparator.CONTAINS
        )

        generator = SieveGenerator()
        result = generator._generate_test(test)
        expected = 'header:contains "Subject" "spam"'
        assert result == expected

    def test_fileinto_action_generation(self):
        """Test generating fileinto action code."""
        action = SieveFileintoAction(mailbox="Spam")
        
        generator = SieveGenerator()
        result = generator._generate_action(action)
        expected = 'fileinto "Spam";'
        assert result == expected
    
    def test_complete_script_generation(self):
        """Test generating a complete script."""
        test = SieveHeaderTest(
            header_list=["Subject"],
            key_list=["spam"]
        )
        action = SieveFileintoAction(mailbox="Spam")
        
        rule = SieveRule(
            name="Spam Filter",
            test=test,
            actions=[action]
        )
        
        script = SieveScript(
            name="Test Script",
            rules=[rule],
            requires=["fileinto"]
        )
        
        generator = SieveGenerator()
        result = generator.generate_script(script)
        
        assert 'require "fileinto";' in result
        assert "# Rule: Spam Filter" in result
        assert 'if header "Subject" "spam"' in result
        assert 'fileinto "Spam";' in result


class TestSieveValidator:
    """Test Sieve script validation."""
    
    def test_valid_script(self):
        """Test validation of a valid script."""
        test = SieveHeaderTest(
            header_list=["Subject"],
            key_list=["spam"]
        )
        action = SieveFileintoAction(mailbox="Spam")
        
        rule = SieveRule(
            name="Spam Filter",
            test=test,
            actions=[action]
        )
        
        script = SieveScript(
            name="Test Script",
            rules=[rule]
        )
        
        errors = SieveValidator.validate_script(script)
        assert len(errors) == 0
    
    def test_invalid_script_empty_name(self):
        """Test validation with empty script name."""
        script = SieveScript(
            name="",
            rules=[]
        )
        
        errors = SieveValidator.validate_script(script)
        assert len(errors) > 0
        assert any("name cannot be empty" in error for error in errors)
    
    def test_invalid_rule_no_actions(self):
        """Test validation of rule with no actions."""
        test = SieveHeaderTest(
            header_list=["Subject"],
            key_list=["spam"]
        )
        
        rule = SieveRule(
            name="Test Rule",
            test=test,
            actions=[]  # No actions
        )
        
        errors = SieveValidator.validate_rule(rule)
        assert len(errors) > 0
        assert any("must have at least one action" in error for error in errors)


class TestSieveFilterBuilder:
    """Test the filter builder utilities."""
    
    def test_spam_filter_creation(self):
        """Test creating a spam filter."""
        rule = SieveFilterBuilder.create_spam_filter("Junk", priority=5)
        
        assert rule.name == "Spam Filter"
        assert rule.priority == 5
        assert len(rule.actions) == 2  # fileinto + stop
        assert rule.actions[0].mailbox == "Junk"
    
    def test_mailing_list_filter_creation(self):
        """Test creating a mailing list filter."""
        rule = SieveFilterBuilder.create_mailing_list_filter(
            "python-dev@python.org",
            "Lists/Python",
            priority=20
        )
        
        assert "python-dev@python.org" in rule.name
        assert rule.priority == 20
        assert rule.actions[0].mailbox == "Lists/Python"
    
    def test_sender_filter_creation(self):
        """Test creating a sender filter."""
        rule = SieveFilterBuilder.create_sender_filter(
            "test@example.com",
            "Test Folder",
            priority=15
        )
        
        assert "test@example.com" in rule.name
        assert rule.priority == 15
        assert rule.actions[0].mailbox == "Test Folder"


class TestSieveTemplates:
    """Test pre-built script templates."""
    
    def test_basic_template(self):
        """Test basic email organization template."""
        script = SieveTemplates.basic_email_organization()
        
        assert script.name == "Basic Email Organization"
        assert len(script.rules) >= 2  # Should have spam filter and size filter
        assert "fileinto" in script.requires
    
    def test_comprehensive_template(self):
        """Test comprehensive filtering template."""
        script = SieveTemplates.comprehensive_filtering()
        
        assert script.name == "Comprehensive Email Filtering"
        assert len(script.rules) >= 5  # Should have multiple types of filters
        assert "fileinto" in script.requires
    
    def test_vacation_template(self):
        """Test vacation response template."""
        script = SieveTemplates.vacation_with_filtering()
        
        assert script.name == "Vacation with Smart Filtering"
        assert len(script.rules) >= 2
        assert "vacation" in script.requires


def test_json_serialization():
    """Test that models can be serialized to/from JSON."""
    test = SieveHeaderTest(
        header_list=["Subject"],
        key_list=["test"]
    )
    action = SieveFileintoAction(mailbox="Test")
    
    rule = SieveRule(
        name="Test Rule",
        test=test,
        actions=[action]
    )
    
    # Serialize to JSON
    json_str = rule.model_dump_json()
    
    # Deserialize from JSON
    rule_data = json.loads(json_str)
    restored_rule = SieveRule.model_validate(rule_data)
    
    assert restored_rule.name == rule.name
    assert restored_rule.test.header_list == rule.test.header_list
    assert restored_rule.actions[0].mailbox == rule.actions[0].mailbox


if __name__ == "__main__":
    # Simple test runner
    test_classes = [
        TestSieveModels,
        TestSieveGenerator,
        TestSieveValidator,
        TestSieveFilterBuilder,
        TestSieveTemplates
    ]
    
    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    print(f"  {method_name}...", end=" ")
                    if hasattr(instance, "setUp"):
                        instance.setUp()
                    getattr(instance, method_name)()
                    print("PASS")
                except Exception as e:
                    print(f"FAIL: {e}")
    
    # Run standalone tests
    print(f"\nRunning standalone tests...")
    try:
        print("  test_json_serialization...", end=" ")
        test_json_serialization()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
    
    print("\nTest run complete!")
