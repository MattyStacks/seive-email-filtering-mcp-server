# Sieve Email Filtering MCP Server - Usage Guide

## Quick Setup

1. **Install the server:**
   ```bash
   cd seive-email-filtering-mcp-server
   pip install -e .
   ```

2. **Test the installation:**
   ```bash
   python examples/basic_usage.py
   ```

3. **Run the MCP server:**
   ```bash
   python -m seive_email_filtering_mcp_server.server
   ```

## MCP Client Configuration

### Claude Desktop Configuration
Add this to your Claude Desktop configuration file (usually located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "seive-email-filtering": {
      "command": "python",
      "args": ["-m", "seive_email_filtering_mcp_server.server"],
      "cwd": "C:\\Users\\{username}\\repos\\seive-email-filtering-mcp-server",
      "env": {}
    }
  }
}
```

### Other MCP Clients
Use the provided `mcp-server-config.json` as a template for other MCP clients.

## Available Tools

Once connected, you can use these tools:

### 1. Create Basic Filters

**Spam Filter:**
- Tool: `create_spam_filter`
- Creates rules to filter spam into a designated folder
- Looks for spam headers and subject markers

**Sender Filter:**
- Tool: `create_sender_filter` 
- Filter emails from specific senders
- Example: Move all emails from "newsletters@example.com" to "Newsletters" folder

**Domain Filter:**
- Tool: `create_domain_filter`
- Filter emails from entire domains
- Example: Move all emails from "company.com" to "Work" folder

### 2. Advanced Filters

**Mailing List Filter:**
- Tool: `create_mailing_list_filter`
- Automatically detects mailing list headers
- Organizes list emails into appropriate folders

**Size Filter:**
- Tool: `create_size_filter`
- Filter by message size (useful for large attachments)
- Can discard or move to specific folder

**Subject Filter:**
- Tool: `create_subject_filter`
- Filter by subject line patterns
- Supports various matching types (contains, exact, regex)

### 3. Special Actions

**Vacation Response:**
- Tool: `create_vacation_response`
- Create auto-reply messages
- Smart filtering to avoid replying to automated messages

**Blacklist/Whitelist:**
- Tools: `create_blacklist_filter`, `create_whitelist_filter`
- Block unwanted senders or ensure important emails are never filtered

### 4. Script Management

**Generate Complete Script:**
- Tool: `generate_sieve_script`
- Combine multiple rules into a complete Sieve script
- Handles priorities and dependencies

**Validate Script:**
- Tool: `validate_sieve_script`
- Check for errors and configuration issues

**Get Templates:**
- Tool: `get_script_template`
- Pre-built configurations for common scenarios

## Example Workflows

### Basic Email Organization
1. Use `create_spam_filter` to handle spam
2. Use `create_size_filter` for large messages
3. Use `generate_sieve_script` to create the final script

### Comprehensive Filtering
1. Use `create_whitelist_filter` for important contacts
2. Use `create_blacklist_filter` for unwanted senders
3. Use `create_mailing_list_filter` for each mailing list
4. Use `create_domain_filter` for work/personal separation
5. Use `generate_sieve_script` to combine all rules

### Vacation Setup
1. Use `get_script_template` with "vacation_with_filtering"
2. Customize the vacation message
3. Deploy to your email server

## Tips

- **Rule Priority:** Lower numbers execute first (whitelist=1, spam=10, organization=20+)
- **Testing:** Always validate scripts before deploying to production
- **Backup:** Keep copies of working configurations
- **Extensions:** The server automatically includes required Sieve extensions

## Deploying to Email Servers

The generated Sieve scripts work with most email servers that support Sieve:

- **Dovecot:** Copy script to user's sieve directory
- **Cyrus IMAP:** Use sieveshell to upload
- **Web interfaces:** Many email providers have web-based Sieve editors

Consult your email server documentation for specific deployment instructions.

## Troubleshooting

**Import Errors:** Ensure the package is installed: `pip install -e .`

**MCP Connection Issues:** Check the file paths in your MCP client configuration

**Sieve Syntax Errors:** Use the `validate_sieve_script` tool to check for issues

**Rule Not Working:** Check rule priority and ensure required extensions are available on your server
