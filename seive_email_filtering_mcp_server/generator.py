"""
Sieve script generation and parsing utilities.
"""

from typing import List, Dict, Any
from .models import (
    SieveScript, SieveRule, SieveTestUnion, SieveActionUnion,
    SieveTestType, SieveActionType, SieveComparator, SieveAddressPart,
    SieveSizeComparator
)


class SieveGenerator:
    """Generates Sieve script text from SieveScript objects."""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_size = 2
    
    def _indent(self) -> str:
        """Get current indentation string."""
        return " " * (self.indent_level * self.indent_size)
    
    def _escape_string(self, text: str) -> str:
        """Escape a string for Sieve script."""
        # Use quoted strings for simplicity
        return f'"{text.replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"'
    
    def _generate_string_list(self, strings: List[str]) -> str:
        """Generate a Sieve string list."""
        if len(strings) == 1:
            return self._escape_string(strings[0])
        return "[" + ", ".join(self._escape_string(s) for s in strings) + "]"
    
    def _generate_test(self, test: SieveTestUnion) -> str:
        """Generate Sieve test code."""
        if test.test_type == SieveTestType.HEADER:
            comparator = f":{test.comparator}" if test.comparator != SieveComparator.IS else ""
            return f"header{comparator} {self._generate_string_list(test.header_list)} {self._generate_string_list(test.key_list)}"
        
        elif test.test_type == SieveTestType.ADDRESS:
            comparator = f":{test.comparator}" if test.comparator != SieveComparator.IS else ""
            address_part = f":{test.address_part}" if test.address_part != SieveAddressPart.ALL else ""
            return f"address{comparator}{address_part} {self._generate_string_list(test.header_list)} {self._generate_string_list(test.key_list)}"
        
        elif test.test_type == SieveTestType.BODY:
            comparator = f":{test.comparator}" if test.comparator != SieveComparator.CONTAINS else ""
            return f"body{comparator} {self._generate_string_list(test.key_list)}"
        
        elif test.test_type == SieveTestType.EXISTS:
            return f"exists {self._generate_string_list(test.header_list)}"
        
        elif test.test_type == SieveTestType.SIZE:
            return f"size :{test.comparator} {test.limit}"
        
        elif test.test_type == SieveTestType.ALLOF:
            sub_tests = [self._generate_test(t) for t in test.tests]
            if len(sub_tests) == 1:
                return sub_tests[0]
            return f"allof ({', '.join(sub_tests)})"
        
        elif test.test_type == SieveTestType.ANYOF:
            sub_tests = [self._generate_test(t) for t in test.tests]
            if len(sub_tests) == 1:
                return sub_tests[0]
            return f"anyof ({', '.join(sub_tests)})"
        
        elif test.test_type == SieveTestType.NOT:
            return f"not {self._generate_test(test.test)}"
        
        elif test.test_type == SieveTestType.TRUE:
            return "true"
        
        elif test.test_type == SieveTestType.FALSE:
            return "false"
        
        else:
            raise ValueError(f"Unknown test type: {test.test_type}")
    
    def _generate_action(self, action: SieveActionUnion) -> str:
        """Generate Sieve action code."""
        if action.action_type == SieveActionType.DISCARD:
            return "discard;"
        
        elif action.action_type == SieveActionType.KEEP:
            return "keep;"
        
        elif action.action_type == SieveActionType.STOP:
            return "stop;"
        
        elif action.action_type == SieveActionType.FILEINTO:
            return f"fileinto {self._escape_string(action.mailbox)};"
        
        elif action.action_type == SieveActionType.REDIRECT:
            return f"redirect {self._escape_string(action.address)};"
        
        elif action.action_type == SieveActionType.REJECT:
            return f"reject {self._escape_string(action.reason)};"
        
        elif action.action_type == SieveActionType.VACATION:
            params = []
            if action.subject:
                params.append(f":subject {self._escape_string(action.subject)}")
            if action.days and action.days != 7:
                params.append(f":days {action.days}")
            if action.addresses:
                params.append(f":addresses {self._generate_string_list(action.addresses)}")
            
            param_str = " ".join(params)
            if param_str:
                param_str = " " + param_str
            return f"vacation{param_str} {self._escape_string(action.message)};"
        
        elif action.action_type == SieveActionType.EXPIRE:
            return f'expire {self._escape_string(action.period)} {self._escape_string(action.count)};'
        
        elif action.action_type == SieveActionType.ADDFLAG:
            flags_str = self._generate_string_list(action.flags)
            return f"addflag {flags_str};"
        
        elif action.action_type == SieveActionType.REMOVEFLAG:
            flags_str = self._generate_string_list(action.flags)
            return f"removeflag {flags_str};"
        
        elif action.action_type == SieveActionType.SETFLAG:
            flags_str = self._generate_string_list(action.flags)
            return f"setflag {flags_str};"
        
        else:
            raise ValueError(f"Unknown action type: {action.action_type}")
    
    def _generate_rule(self, rule: SieveRule) -> List[str]:
        """Generate Sieve rule code."""
        lines = []
        
        # Add comment with rule name and description
        lines.append(f"# Rule: {rule.name}")
        if rule.description:
            lines.append(f"# {rule.description}")
        
        if not rule.enabled:
            lines.append("# DISABLED")
            # Comment out the entire rule
            rule_lines = self._generate_enabled_rule(rule)
            for line in rule_lines:
                lines.append(f"# {line}")
        else:
            lines.extend(self._generate_enabled_rule(rule))
        
        return lines
    
    def _generate_enabled_rule(self, rule: SieveRule) -> List[str]:
        """Generate an enabled Sieve rule."""
        lines = []
        
        # Generate if statement
        test_code = self._generate_test(rule.test)
        lines.append(f"if {test_code} {{")
        
        # Generate actions
        self.indent_level += 1
        for action in rule.actions:
            action_code = self._generate_action(action)
            lines.append(f"{self._indent()}{action_code}")
        self.indent_level -= 1
        
        lines.append("}")
        
        return lines
    
    def generate_script(self, script: SieveScript) -> str:
        """Generate complete Sieve script."""
        lines = []
        
        # Add header comment
        lines.append(f"# Sieve Script: {script.name}")
        if script.description:
            lines.append(f"# {script.description}")
        lines.append("#")
        lines.append("# Generated by Sieve Email Filtering MCP Server")
        if script.protonmail_mode:
            lines.append("# ProtonMail compatible")
        lines.append("")
        
        # Add require statements - ProtonMail style if enabled
        if script.protonmail_mode:
            # Standard ProtonMail requires
            base_requires = [
                "include", "environment", "variables", "relational", 
                "comparator-i;ascii-numeric", "spamtest"
            ]
            action_requires = ["fileinto", "imap4flags"]
            
            # Add conditional requires based on script content
            all_requires = set(base_requires + action_requires)
            
            # Check if script uses regex
            if any("regex" in str(rule.test) for rule in script.rules):
                all_requires.add("regex")
            
            # Check if script uses ProtonMail features
            has_expire = any(
                hasattr(action, 'action_type') and action.action_type == SieveActionType.EXPIRE 
                for rule in script.rules for action in rule.actions
            )
            has_flags = any(
                hasattr(action, 'action_type') and action.action_type in [
                    SieveActionType.ADDFLAG, SieveActionType.REMOVEFLAG, SieveActionType.SETFLAG
                ]
                for rule in script.rules for action in rule.actions
            )
            
            if has_expire:
                all_requires.add("vnd.proton.expire")
            if has_flags:
                all_requires.add("imap4flags")
            
            # Add user-specified requires
            all_requires.update(script.requires)
            
            # Generate require statements
            base_requires_str = ', '.join(f'"{req}"' for req in sorted(base_requires) if req in all_requires)
            action_requires_list = [req for req in sorted(all_requires) if req not in base_requires]
            
            if base_requires_str:
                lines.append(f'require [{base_requires_str}];')
            if action_requires_list:
                action_requires_str = ', '.join(f'"{req}"' for req in action_requires_list)
                lines.append(f'require [{action_requires_str}];')
        else:
            # Standard requires
            if script.requires:
                for ext in script.requires:
                    lines.append(f'require "{ext}";')
        
        lines.append("")
        
        # Add script variables if any
        if script.variables:
            lines.append("# Script variables")
            for var_name, var_value in script.variables.items():
                lines.append(f'set "{var_name}" "{var_value}";')
            lines.append("")
        
        # Add ProtonMail spam check if enabled
        if script.include_spam_check or script.protonmail_mode:
            lines.append("# Generated: Do not run this script on spam messages")
            lines.append('if allof (environment :matches "vnd.proton.spam-threshold" "*", spamtest :value "ge" :comparator "i;ascii-numeric" "${1}") {')
            lines.append("    return;")
            lines.append("}")
            lines.append("")
        
        # Sort rules by priority
        sorted_rules = sorted(script.rules, key=lambda r: r.priority)
        
        # Generate each rule
        for i, rule in enumerate(sorted_rules):
            if i > 0:
                lines.append("")  # Add blank line between rules
            
            rule_lines = self._generate_rule(rule)
            lines.extend(rule_lines)
        
        return "\n".join(lines)


class SieveValidator:
    """Validates Sieve scripts and rules."""
    
    @staticmethod
    def validate_script(script: SieveScript) -> List[str]:
        """Validate a Sieve script and return list of validation errors."""
        errors = []
        
        if not script.name.strip():
            errors.append("Script name cannot be empty")
        
        if not script.rules:
            errors.append("Script must contain at least one rule")
        
        # Check for duplicate rule names
        rule_names = [rule.name for rule in script.rules]
        if len(rule_names) != len(set(rule_names)):
            errors.append("Rule names must be unique within a script")
        
        # Validate each rule
        for i, rule in enumerate(script.rules):
            rule_errors = SieveValidator.validate_rule(rule)
            for error in rule_errors:
                errors.append(f"Rule {i+1} ({rule.name}): {error}")
        
        return errors
    
    @staticmethod
    def validate_rule(rule: SieveRule) -> List[str]:
        """Validate a Sieve rule and return list of validation errors."""
        errors = []
        
        if not rule.name.strip():
            errors.append("Rule name cannot be empty")
        
        if not rule.actions:
            errors.append("Rule must have at least one action")
        
        # Validate test
        test_errors = SieveValidator._validate_test(rule.test)
        errors.extend(test_errors)
        
        # Validate actions
        for i, action in enumerate(rule.actions):
            action_errors = SieveValidator._validate_action(action)
            for error in action_errors:
                errors.append(f"Action {i+1}: {error}")
        
        return errors
    
    @staticmethod
    def _validate_test(test: SieveTestUnion) -> List[str]:
        """Validate a Sieve test."""
        errors = []
        
        if test.test_type == SieveTestType.HEADER:
            if not test.header_list:
                errors.append("Header test must specify at least one header")
            if not test.key_list:
                errors.append("Header test must specify at least one key")
        
        elif test.test_type == SieveTestType.ADDRESS:
            if not test.header_list:
                errors.append("Address test must specify at least one header")
            if not test.key_list:
                errors.append("Address test must specify at least one address")
        
        elif test.test_type == SieveTestType.BODY:
            if not test.key_list:
                errors.append("Body test must specify at least one search term")
        
        elif test.test_type == SieveTestType.EXISTS:
            if not test.header_list:
                errors.append("Exists test must specify at least one header")
        
        elif test.test_type == SieveTestType.SIZE:
            if test.limit <= 0:
                errors.append("Size test limit must be positive")
        
        elif test.test_type == SieveTestType.ALLOF:
            if not test.tests:
                errors.append("AllOf test must contain at least one sub-test")
            for i, sub_test in enumerate(test.tests):
                sub_errors = SieveValidator._validate_test(sub_test)
                for error in sub_errors:
                    errors.append(f"AllOf sub-test {i+1}: {error}")
        
        elif test.test_type == SieveTestType.ANYOF:
            if not test.tests:
                errors.append("AnyOf test must contain at least one sub-test")
            for i, sub_test in enumerate(test.tests):
                sub_errors = SieveValidator._validate_test(sub_test)
                for error in sub_errors:
                    errors.append(f"AnyOf sub-test {i+1}: {error}")
        
        elif test.test_type == SieveTestType.NOT:
            sub_errors = SieveValidator._validate_test(test.test)
            for error in sub_errors:
                errors.append(f"Not sub-test: {error}")
        
        return errors
    
    @staticmethod
    def _validate_action(action: SieveActionUnion) -> List[str]:
        """Validate a Sieve action."""
        errors = []
        
        if action.action_type == SieveActionType.FILEINTO:
            if not action.mailbox.strip():
                errors.append("Fileinto action must specify a mailbox")
        
        elif action.action_type == SieveActionType.REDIRECT:
            if not action.address.strip():
                errors.append("Redirect action must specify an address")
            # Basic email validation
            if "@" not in action.address:
                errors.append("Redirect address must be a valid email address")
        
        elif action.action_type == SieveActionType.REJECT:
            if not action.reason.strip():
                errors.append("Reject action must specify a reason")
        
        elif action.action_type == SieveActionType.VACATION:
            if not action.message.strip():
                errors.append("Vacation action must specify a message")
            if action.days is not None and action.days <= 0:
                errors.append("Vacation days must be positive")
        
        return errors
