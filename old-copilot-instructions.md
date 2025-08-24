# Copilot Instructions for Sieve Email Filtering MCP Server

## Project Overview
This repository contains a comprehensive Sieve Email Filtering MCP (Model Context Protocol) Server designed primarily for ProtonMail but compatible with other Sieve-supporting email services. The project provides 16 specialized tools for creating, managing, and maintaining email filters with advanced features like .eml file analysis, auto-expiration, and intelligent filter generation.

## MCP Server Integration

### Primary Usage: MCP Tools
This project is primarily designed as an MCP server with 16 specialized tools:

1. **Email Analysis Tools**:
   - `analyze_eml_file` - Parse .eml files and suggest filters
   - `create_protonmail_script` - Generate ProtonMail-compatible scripts
   - `create_expiring_filter` - Create filters with auto-expiration

2. **Filter Creation Tools**:
   - `create_spam_filter` - Spam detection and filtering
   - `create_sender_filter` - Filter by specific email addresses
   - `create_domain_filter` - Filter by sender domains
   - `create_subject_filter` - Pattern-based subject filtering
   - `create_size_filter` - Size-based message filtering
   - `create_mailing_list_filter` - Mailing list organization
   - `create_vacation_response` - Auto-reply functionality
   - `create_blacklist_filter` - Block unwanted senders
   - `create_whitelist_filter` - Prioritize important senders

3. **Script Management Tools**:
   - `generate_sieve_script` - Compile multiple rules into complete scripts
   - `validate_sieve_script` - Validate Sieve script syntax and logic
   - `get_script_template` - Access pre-built filtering templates
   - `explain_sieve_syntax` - Get Sieve language documentation

### Integration with GitHub Copilot
While GitHub Copilot doesn't natively support MCP servers, the project includes:
- **CLI Interface**: Command-line tools for script generation
- **VS Code Integration**: Configuration files and task definitions
- **Example Templates**: Comprehensive examples for Copilot training
- **Context Documentation**: Detailed context files for AI assistance

## Email-Driven Filter Development

### Analyzing .eml Files
When users place .eml files in the `eml-samples/` directory and ask you to create filters:

1. **Use the MCP server**: Call `analyze_eml_file` tool with .eml content
2. **Automatic analysis**: The server will parse headers, content, and patterns
3. **Filter suggestions**: Get confidence-scored filter recommendations
4. **Automatic generation**: Server can generate complete Sieve rules
5. **ProtonMail compatibility**: All generated filters include required spam checks
6. **Smart categorization**: Intelligent folder and action suggestions

### Enhanced Analysis Capabilities
The MCP server provides sophisticated email analysis:
- **Pattern Recognition**: Automatic detection of sender, subject, and content patterns
- **Category Detection**: Smart categorization (promotional, financial, notifications, etc.)
- **Confidence Scoring**: Analysis confidence ratings for filter recommendations
- **Multi-format Support**: Parse various .eml file formats and encodings
- **Keyword Extraction**: Intelligent content keyword identification

## Code Style and Standards

### MCP Server Priority
1. **Use MCP tools first**: Always prefer using the MCP server tools over manual Sieve generation
2. **Tool-based workflow**: Use `analyze_eml_file`, `create_*_filter`, and `generate_sieve_script` tools
3. **Validation**: Always use `validate_sieve_script` to check generated scripts
4. **ProtonMail mode**: Use `create_protonmail_script` for ProtonMail-specific features

### Sieve Script Guidelines
1. **Always include required extensions** at the top of each script
2. **Use descriptive variable names** with clear prefixes (e.g., `steam_sender`, `finance_pattern`)
3. **MANDATORY: Include spam threshold checks** using the standard ProtonMail pattern (see below)
4. **Add comprehensive comments** explaining the purpose of each filter
5. **Use regex patterns** when multiple variations need to be matched
6. **Prefer case-insensitive matching** using `:comparator "i;ascii-casemap"`
7. **Separate rules for multiple fileinto actions** - CRITICAL: Cannot combine multiple fileinto actions in a single rule

### CRITICAL: Multiple Fileinto Actions
**IMPORTANT SIEVE SYNTAX RULE**: Multiple fileinto actions cannot be combined in a single rule. Each fileinto action must be in a separate rule:

**❌ INCORRECT (will not work):**
```sieve
if allof (conditions) {
    expire "day" "30";
    fileinto "expiring";
    fileinto "Promotions";  # This is invalid Sieve syntax
}
```

**✅ CORRECT (separate rules):**
```sieve
# First rule - expire and file to expiring folder
if allof (conditions) {
    expire "day" "30";
    fileinto "expiring";
}

# Second rule - file to promotions folder  
if allof (conditions) {
    fileinto "Promotions";
}
```

### MANDATORY: New Sieve File Requirements
**Every new Sieve script MUST include the following patterns:**

1. **Required Extensions** - Include all necessary require statements at the top
2. **Spam Test Check** - Include the standard spam threshold check immediately after variables
3. **File Purpose Comment** - Add a descriptive comment block explaining the script's purpose
4. **Separate Rules** - Use separate rules for each fileinto action

### File Structure
- **Primary usage**: Use MCP server tools via VS Code or compatible MCP clients
- **Generated scripts**: Place generated Sieve scripts in the `sieves/` directory
- **Email samples**: Place .eml files in `eml-samples/` directory for analysis
- **Documentation**: Update `docs-personal/` for personal notes
- **Examples**: Reference `examples/` directory for usage patterns
- **CLI usage**: Use `python -m seive_email_filtering_mcp_server.cli` for command-line operations

### MCP Server Tools Usage Examples
```bash
# Using CLI interface
python -m seive_email_filtering_mcp_server.cli template comprehensive_filtering
python -m seive_email_filtering_mcp_server.cli spam-filter --mailbox Junk
python -m seive_email_filtering_mcp_server.cli validate script.json

# MCP integration in VS Code
# Use Ctrl+Shift+P -> "Tasks: Run Task" to access pre-configured tasks
```

### Required Extensions Pattern
**MANDATORY for all new Sieve scripts:**
Always start scripts with the appropriate require statements. Use this standard pattern:
```sieve
require ["include", "environment", "variables", "relational", "comparator-i;ascii-numeric", "spamtest", "regex"];
require ["fileinto", "imap4flags", "vnd.proton.expire"];
```

**Note:** Adjust extensions based on your script needs:
- Add `"regex"` if using regex patterns
- Add `"vnd.proton.expire"` if using expiration features
- Add other extensions as needed for your specific filters

### Spam Check Pattern
**MANDATORY for all new Sieve scripts:**
Include this standard spam threshold check immediately after variable declarations and before any filtering logic:
```sieve
# Generated: Do not run this script on spam messages
if allof (environment :matches "vnd.proton.spam-threshold" "*", spamtest :value "ge" :comparator "i;ascii-numeric" "${1}") {
    return;
}
```

**This check must be included in every script to prevent filters from running on spam messages.**

### New Sieve File Template
When creating any new Sieve script, use this mandatory template structure:

```sieve
require ["include", "environment", "variables", "relational", "comparator-i;ascii-numeric", "spamtest", "regex"];
require ["fileinto", "imap4flags", "vnd.proton.expire"];

/*
 * [DESCRIPTION OF WHAT THIS FILTER DOES]
 * Purpose: Brief explanation of the filter's functionality
 * Target: What emails this filter processes
 * Actions: What happens to matching emails
 */

# Set up variables (if needed)
set "variable_name" "value";

# Generated: Do not run this script on spam messages
if allof (environment :matches "vnd.proton.spam-threshold" "*", spamtest :value "ge" :comparator "i;ascii-numeric" "${1}") {
    return;
}

# Your filtering logic goes here
if allof (
    # conditions
) {
    # actions
}
```

**CRITICAL:** The spam check block is mandatory and must be included after variables but before any filtering logic.

### Variable Declaration
Use clear, descriptive variable names:
```sieve
set "steam_sender" "noreply@steampowered.com";
set "steam_subject_pattern" "Steam wishlist (is|are) now on sale";
```

### Regex Patterns
When matching multiple variations, use regex with alternation:
```sieve
# Match both "is" and "are" variations
header :regex :comparator "i;ascii-casemap" "Subject" "Steam wishlist (is|are) now on sale"
```

## ProtonMail-Specific Features
- Use `vnd.proton.expire` for auto-expiring messages
- Use `vnd.proton.spam-threshold` for spam detection  
- File messages into standard folders: "finance", "promotions", "expiring"
- **MCP Integration**: Use `create_protonmail_script` tool for automatic ProtonMail compatibility
- **Automatic requires**: Server automatically adds required ProtonMail extensions
- **Spam protection**: All ProtonMail scripts include mandatory spam threshold checks

## Documentation Requirements

### When to Update Documentation
1. **After using MCP tools** - Document generated scripts and their purposes
2. **After adding new filters** - Update README.md with script descriptions  
3. **After modifying filter logic** - Update comments and changelog
4. **After changing file structure** - Update project documentation
5. **After adding new features** - Document usage patterns and examples

### Changelog Requirements
- Document all significant changes with date and description
- Include migration notes when changing existing filters
- Note any ProtonMail-specific dependencies or requirements
- Track version changes and compatibility updates
- **Use CHANGELOG.md** - Maintain comprehensive changelog using semantic versioning

### Comment Standards
- Include file purpose at the top of each script
- Comment complex regex patterns with examples
- Explain the logic behind multi-step filtering
- Note any ProtonMail-specific extensions or behaviors
- Document MCP tool usage and parameters

## Testing Guidelines
- **Use MCP validation**: Always use `validate_sieve_script` tool to check scripts
- **Test with examples**: Use the comprehensive examples in the `examples/` directory
- **Use server tools**: Prefer `analyze_eml_file` for testing with real email samples
- Test regex patterns using online tools like regex101.com
- Use Sieve testing tools like https://sieve.mimecast.com/
- Create test cases for common email scenarios
- Validate scripts before deploying to production
- **Run test suite**: Execute `python tests/test_sieve_server.py` for comprehensive testing

## Common Patterns

### Using MCP Server Tools
```python
# Primary workflow: Use MCP server tools
1. analyze_eml_file - for email analysis
2. create_*_filter - for specific filter types  
3. generate_sieve_script - to combine rules
4. validate_sieve_script - to check syntax
5. create_protonmail_script - for ProtonMail features
```

### Multiple Fileinto Actions (CORRECTED)
When you need multiple fileinto actions, use separate if statements:
```sieve
# CORRECT: Separate rules for each fileinto action
# First rule - expire and file to expiring folder
if allof (header :contains "Subject" ["sale", "discount"]) {
    expire "day" "30";
    fileinto "expiring";
}

# Second rule - file to promotions folder (separate rule required)
if allof (header :contains "Subject" ["sale", "discount"]) {
    fileinto "Promotions";
}
```

### Address Matching
Use `:contains` for domain matching and `:is` for exact matches:
```sieve
# Domain matching
address :all :comparator "i;unicode-casemap" :contains "From" ["bankofamerica.com", "chase.com"]

# Exact address matching
address :is "from" "noreply@steampowered.com"
```

## Error Handling
- **Use MCP validation**: Always use `validate_sieve_script` tool for syntax checking
- **Server error reporting**: MCP server provides detailed error messages and suggestions
- **Template validation**: All built-in templates are pre-validated
- Always validate Sieve syntax before committing
- Include error handling for edge cases
- Test with various email formats and encodings
- Ensure compatibility with ProtonMail's Sieve implementation
- **Check multiple fileinto rules**: Ensure separate rules for each fileinto action

## Security Considerations
- **MCP server safety**: All tools include built-in validation and safety checks
- **Privacy protection**: Server uses parameterized configurations to protect personal data
- Avoid overly broad filters that might catch legitimate emails
- Be cautious with auto-deletion or rejection rules
- Test spam filters thoroughly to avoid false positives
- Regular review and update of filter criteria
- **Whitelist protection**: Always include whitelist rules with high priority

## Recent Updates and Critical Changes

### CRITICAL: Sieve Syntax Correction (Latest)
**Discovery**: Multiple fileinto actions cannot be combined in a single Sieve rule
**Impact**: Previous examples with multiple fileinto actions were incorrect
**Fix**: Always use separate if/then rules for each fileinto action
**Example**: See `promotional_auto_expire.sieve` for corrected implementation

### Latest MCP Server Features
- **16 comprehensive tools** for all Sieve filtering needs
- **Email analysis** with confidence scoring and automatic filter generation
- **ProtonMail integration** with automatic spam checks and expiration support
- **Advanced validation** catching syntax errors before deployment
- **Template system** with pre-built, tested configurations

### Integration Improvements
- **VS Code integration** with task definitions and configuration
- **CLI interface** for standalone usage without MCP client
- **GitHub Copilot support** through context documentation and examples
- **Privacy protection** with parameterized configurations
