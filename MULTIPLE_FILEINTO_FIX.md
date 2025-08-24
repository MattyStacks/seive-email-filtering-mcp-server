# Multiple Fileinto Actions Fix Documentation

## Problem Description

The original MCP server implementation had a critical bug where it would create single Sieve rules with multiple `fileinto` actions. This violates Sieve syntax requirements because **multiple fileinto actions cannot be combined in a single rule**.

### Example of the Problem (INCORRECT):
```sieve
# INVALID Sieve syntax - multiple fileinto actions in one rule
if header :contains "Subject" ["sale", "discount"] {
    expire "day" "30";
    fileinto "expiring";
    fileinto "Promotions";  # ❌ ERROR: Second fileinto in same rule
}
```

## Solution Implemented

The fix ensures that **each fileinto action gets its own separate rule**, while preserving the same filtering logic.

### Example of the Solution (CORRECT):
```sieve
# Rule 1: Expire and file to expiring folder
if header :contains "Subject" ["sale", "discount"] {
    expire "day" "30";
    fileinto "expiring";
}

# Rule 2: File to promotions folder (separate rule required)
if header :contains "Subject" ["sale", "discount"] {
    fileinto "Promotions";
}
```

## Implementation Details

### 1. New Utility Functions (utils.py)

#### `split_multiple_fileinto_actions(rule: SieveRule) -> List[SieveRule]`
- Takes a rule with multiple fileinto actions
- Splits it into separate rules, one per fileinto action
- Preserves non-fileinto actions in the first rule
- Assigns slightly different priorities to maintain order

#### `create_expiring_fileinto_filter(...) -> List[SieveRule]`
- Creates two separate rules for expiring filters:
  1. **Expire rule**: `expire + fileinto "expiring"`
  2. **Filing rule**: `fileinto "regular_folder"`
- Ensures proper Sieve compliance from the start

### 2. Fixed MCP Tools (server.py)

#### `create_expiring_filter` Tool
- **Before**: Created single rule with `[expire, fileinto]` actions
- **After**: Uses `create_expiring_fileinto_filter` to create separate rules
- Returns multiple rules in JSON and proper Sieve script

#### New `split_multiple_fileinto_rule` Tool
- Demonstrates the splitting functionality
- Takes incorrect rule JSON and returns corrected separate rules
- Educational tool to show proper Sieve syntax

### 3. Fixed Templates (utils.py)

#### `protonmail_comprehensive()` Template
- **Before**: Steam and promotional rules had multiple fileinto actions
- **After**: Uses `create_expiring_fileinto_filter` for proper separation
- Creates 2 rules each for Steam and promotional filters

### 4. Enhanced Email Analysis (email_analyzer.py)

#### `generate_expiring_filter_from_analysis()` Method
- New method that returns multiple rules when expiration is needed
- Replaces old method that incorrectly added expire to existing rule
- Used by `analyze_eml_file` MCP tool for proper filter generation

## Files Modified

1. **`seive_email_filtering_mcp_server/utils.py`**
   - Added `split_multiple_fileinto_actions()` function
   - Added `create_expiring_fileinto_filter()` function
   - Fixed `protonmail_comprehensive()` template
   - Updated imports to include required models

2. **`seive_email_filtering_mcp_server/server.py`**
   - Fixed `create_expiring_filter` MCP tool implementation
   - Added new `split_multiple_fileinto_rule` MCP tool
   - Updated `analyze_eml_file` tool to use new analysis method
   - Added proper error handling and user feedback

3. **`seive_email_filtering_mcp_server/email_analyzer.py`**
   - Added `generate_expiring_filter_from_analysis()` method
   - Modified existing method to not add expire actions incorrectly
   - Improved integration with utility functions

## Testing and Validation

### Test Cases Covered
1. **Rule Splitting**: Verify rules with multiple fileinto actions are properly split
2. **Expiring Filter Creation**: Confirm new method creates separate rules
3. **Template Generation**: Ensure all templates produce valid Sieve syntax
4. **MCP Tool Functionality**: Test new and updated MCP tools

### Validation Points
- ✅ No rule has more than one fileinto action
- ✅ Expire actions are properly paired with fileinto actions
- ✅ Test conditions are correctly duplicated across split rules
- ✅ Rule priorities maintain proper execution order
- ✅ Generated Sieve scripts are syntactically valid

## Impact and Benefits

### Immediate Benefits
1. **Sieve Compliance**: All generated scripts now follow proper Sieve syntax
2. **Server Compatibility**: Works correctly with all Sieve-compliant email servers
3. **ProtonMail Support**: Maintains full ProtonMail feature compatibility
4. **Backward Compatibility**: Existing rules can be automatically fixed

### User Experience Improvements
1. **Clear Feedback**: Tools explain why separate rules are needed
2. **Educational Value**: Users learn proper Sieve syntax through examples
3. **Automatic Fixing**: No manual intervention required for correct filtering
4. **Error Prevention**: Impossible to generate invalid Sieve syntax

## Usage Examples

### Using the Fix in MCP Tools

```json
// Call create_expiring_filter tool
{
  "filter_type": "promotional",
  "criteria": "sales",
  "mailbox": "Promotions",
  "expire_period": "day",
  "expire_count": "30"
}
// Returns 2 separate rules automatically
```

### Using the Split Tool

```json
// Call split_multiple_fileinto_rule tool
{
  "rule_json": "{\"name\":\"Bad Rule\", \"actions\":[{\"action_type\":\"fileinto\",\"mailbox\":\"A\"},{\"action_type\":\"fileinto\",\"mailbox\":\"B\"}]}"
}
// Returns corrected separate rules
```

## Migration Guide

### For Existing Rules
1. Use the `split_multiple_fileinto_rule` MCP tool to fix existing incorrect rules
2. Update any custom templates to use the new utility functions
3. Regenerate scripts using the corrected templates

### For New Development
1. Always use `create_expiring_fileinto_filter()` for expiring filters
2. Use `split_multiple_fileinto_actions()` if manually creating complex rules
3. Validate generated scripts to ensure compliance

## Future Considerations

1. **Validation Enhancement**: Add automated checking for multiple fileinto actions
2. **Performance Optimization**: Consider rule consolidation where appropriate
3. **User Education**: Provide more examples of proper Sieve syntax
4. **Template Expansion**: Create more templates using the corrected patterns

---

**Note**: This fix resolves a fundamental architectural issue in the MCP server and ensures all generated Sieve scripts comply with RFC 5228 (Sieve Email Filtering Language) requirements.
