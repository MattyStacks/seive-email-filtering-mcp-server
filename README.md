# Sieve Email Filtering MCP Server

A comprehensive Model Context Protocol (MCP) server for creating, managing, and maintaining Sieve email filters. This server provides tools to generate Sieve scripts programmatically, making email filter management easier and more maintainable.

## Features

- **Comprehensive Sieve Support**: Create all common Sieve filter types (spam, sender, domain, size, etc.)
- **Pre-built Templates**: Ready-to-use templates for common filtering scenarios
- **Validation**: Built-in validation for Sieve scripts and rules
- **JSON Integration**: Easy integration with other tools via JSON serialization
- **MCP Protocol**: Standard Model Context Protocol interface for AI assistants

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MattyStacks/seive-email-filtering-mcp-server.git
cd seive-email-filtering-mcp-server
```

2. Install the package:
```bash
pip install -e .
```

Or install dependencies manually:
```bash
pip install mcp pydantic click typing-extensions
```

## Quick Start

### Running the MCP Server

```bash
python -m seive_email_filtering_mcp_server.server
```

### Example Usage

```python
from seive_email_filtering_mcp_server.utils import SieveFilterBuilder
from seive_email_filtering_mcp_server.generator import SieveGenerator

# Create a spam filter
spam_rule = SieveFilterBuilder.create_spam_filter("Spam", priority=10)

# Create a mailing list filter
list_rule = SieveFilterBuilder.create_mailing_list_filter(
    "python-dev@python.org", 
    "Lists/Python", 
    priority=20
)

# Generate Sieve script
generator = SieveGenerator()
script = SieveScript(
    name="My Email Filters",
    rules=[spam_rule, list_rule],
    requires=["fileinto"]
)

print(generator.generate_script(script))
```

## Available Tools

The MCP server provides the following tools:

### Filter Creation Tools

- **`create_spam_filter`** - Create spam filtering rules
- **`create_mailing_list_filter`** - Filter mailing list messages
- **`create_sender_filter`** - Filter by specific sender email
- **`create_domain_filter`** - Filter by sender domain
- **`create_subject_filter`** - Filter by subject line patterns
- **`create_size_filter`** - Filter by message size
- **`create_vacation_response`** - Create vacation auto-reply
- **`create_blacklist_filter`** - Block specific senders
- **`create_whitelist_filter`** - Ensure important messages are kept

### Script Management Tools

- **`generate_sieve_script`** - Generate complete Sieve script from rules
- **`validate_sieve_script`** - Validate script for errors
- **`get_script_template`** - Get pre-built script templates

### Documentation Tools

- **`explain_sieve_syntax`** - Get help with Sieve syntax and capabilities

## Script Templates

Pre-built templates are available for common use cases:

### Basic Email Organization
- Spam filtering
- Large message handling

### Comprehensive Filtering
- Whitelist/blacklist management
- Spam filtering
- Mailing list organization
- Domain-based filtering
- Size limits

### Vacation with Smart Filtering
- Vacation auto-reply
- Skip automated messages
- Avoid mailing list replies

## MCP Client Configuration

### Claude Desktop Configuration
To use with MCP clients (like Claude Desktop), add to your configuration:

```json
{
  "mcpServers": {
    "seive-email-filtering": {
      "command": "python",
      "args": ["-m", "seive_email_filtering_mcp_server.server"],
      "env": {},
      "disabled": false
    }
  }
}
```

### GitHub Copilot Integration
While GitHub Copilot doesn't natively support MCP servers, you can integrate this server with your Sieve email filtering projects:

1. **Add as submodule to your email filtering repository**
2. **Set up VS Code tasks** to access MCP server functions
3. **Create context files** to help Copilot understand Sieve syntax
4. **Use CLI commands** in your development workflow

See [`COPILOT_INTEGRATION.md`](COPILOT_INTEGRATION.md) and [`examples/copilot_integration_example.md`](examples/copilot_integration_example.md) for detailed setup instructions.

**Quick setup for your email filtering project:**
```bash
# Add as submodule
git submodule add https://github.com/MattyStacks/seive-email-filtering-mcp-server.git tools/sieve-mcp-server

# Use CLI commands in your workflow
cd tools/sieve-mcp-server
python -m seive_email_filtering_mcp_server.cli template comprehensive_filtering --output my-filters.sieve
```

## Sieve Filter Examples

### Spam Filter
```sieve
# Rule: Spam Filter
# Move spam messages to spam folder
if anyof (header "X-Spam-Flag" "YES", 
          header :matches "X-Spam-Status" "*Yes*", 
          header :contains "Subject" ["***SPAM***", "[SPAM]", "***UCE***"]) {
  fileinto "Spam";
  stop;
}
```

### Mailing List Filter
```sieve
# Rule: Mailing List: python-dev@python.org
# Filter messages from python-dev@python.org mailing list
if anyof (header :matches "List-ID" "*python-dev@python.org*", 
          header :matches "List-Post" "*python-dev@python.org*", 
          header :matches "X-Mailing-List" "*python-dev@python.org*") {
  fileinto "Lists/Python";
}
```

### Size Filter
```sieve
# Rule: Size Filter: over 10MB
# Filter messages over 10MB in size
if size :over 10485760 {
  fileinto "Large Messages";
}
```

## API Reference

### Core Models

- **`SieveScript`** - Complete Sieve script with rules and metadata
- **`SieveRule`** - Individual filtering rule with test and actions
- **`SieveTest`** - Test conditions (header, address, body, size, etc.)
- **`SieveAction`** - Actions to take (fileinto, discard, reject, etc.)

### Utilities

- **`SieveFilterBuilder`** - Factory methods for common filter types
- **`SieveGenerator`** - Converts models to Sieve script text
- **`SieveValidator`** - Validates scripts for correctness
- **`SieveTemplates`** - Pre-built script templates

## Testing

Run the test suite:
```bash
python tests/test_sieve_server.py
```

Or with pytest (if installed):
```bash
pip install pytest pytest-asyncio
pytest tests/
```

## Examples

See the `examples/` directory for more detailed usage examples:

```bash
python examples/basic_usage.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Sieve Resources

- [RFC 5228 - Sieve Email Filtering Language](https://tools.ietf.org/html/rfc5228)
- [Sieve Extension RFCs](https://www.iana.org/assignments/sieve-extensions/sieve-extensions.xhtml)
- [Dovecot Sieve Documentation](https://doc.dovecot.org/configuration_manual/sieve/)

## Support

For questions or issues:
1. Check the [GitHub Issues](https://github.com/MattyStacks/seive-email-filtering-mcp-server/issues)
2. Create a new issue with details about your problem
3. Include sample code and expected vs actual behavior
