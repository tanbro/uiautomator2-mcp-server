# Android UI Test Skill - Usage Examples

This document demonstrates how to use this skill for both learning purposes and production testing.

## Learning Examples

### Example 1: Understanding Skill Structure
```markdown
# Key Learning Points:

1. **Metadata Format**:
   - YAML frontmatter with required fields
   - Clear naming conventions
   - Proper licensing and compatibility info

2. **Content Organization**:
   - Progressive disclosure pattern
   - Separation of concerns (scripts vs docs)
   - Self-contained package structure

3. **Best Practices**:
   - Clear prerequisites and setup instructions
   - Structured execution flow
   - Comprehensive error handling
```

### Example 2: Test Case Design
```markdown
# From references/test-specification.md - demonstrates proper test structure

### TC001: Device Connection & Initialization

**Steps:**
1. List connected devices via `device_list`
2. Select the first available device from the list
3. Initialize device via `init` tool
4. Get device info via `info`

**Expected Results:**
- At least one device found in connected devices list
- Init completes without errors
- Device info returns valid model, SDK version, screen size

Key elements of well-structured test case:
- Clear objective with unique ID (TC001)
- Step-by-step instructions with tool names
- Specific expected outcomes
- Proper error handling considerations
```

### Example 3: v0.3.0 XPath Tool Usage
```markdown
# The v0.3.0 release introduced XPath-based element tools

# Waiting for elements:
xpath_wait_appear(serial, "//node[@text='Hello']", timeout=10.0)
xpath_wait_gone(serial, "//node[@text='Loading']", timeout=5.0)

# Checking element existence (new in v0.3.0):
xpath_exists(serial, "//button[@text='Submit']")

# Getting element information (new in v0.3.0):
xpath_get_info(serial, "//node[@text='Sample']")
# Returns: {"text": "Sample", "bounds": "(100,200)(300,400)", "className": "android.widget.TextView", ...}

# Getting specific attributes (new in v0.3.0):
xpath_get_attrib(serial, "//node[@text='Sample']", "className")
# Returns: "android.widget.TextView"

# Element screenshots:
xpath_screenshot(serial, "//node[@resource-id='screenshot']", "jpeg")
# Returns: (base64_data_url, height, width)

xpath_save_screenshot(serial, "//node[@resource-id='screenshot']", "/path/to/file.png")
# Returns: "/absolute/path/to/file.png"
```

## Production Usage Examples

### Example 1: AI-Driven Testing (Primary Method)
```bash
# Simply ask your AI client to execute the test suite
# Example prompts:
"Run the Android UI test suite on my connected device"
"Execute all android-ui-test skill tests"
"Run TC001-TC010 tests and provide a report"

# The AI will:
# 1. Read the test specification from references/test-specification.md
# 2. Execute each test case step by step
# 3. Generate a comprehensive pass/fail report
```

### Example 2: Demo Script (For Understanding)
```bash
# Run the demonstration script to understand how the skill works
python scripts/demo-android-test.py

# This shows:
# - How AI discovers and parses the skill
# - Test execution flow
# - Expected test results format
# - Educational benefits of the skill
```

### Example 3: Custom Test Extensions
```markdown
# To add new test cases, edit references/test-specification.md:

### TC011: Network State Testing

**Steps:**
1. Check current network connectivity via shell command
2. Toggle airplane mode via `shell_command` with `settings put global airplane_mode_on`
3. Broadcast airplane mode change
4. Verify network state changes

**Expected Results:**
- Network state toggles correctly
- Device enters/exits airplane mode

This skill uses AI-driven execution, so test cases are defined
as structured markdown rather than Python code.
```

## Common Usage Patterns

### Pattern 1: Element Location with XPath (v0.3.0)
```markdown
# v0.3.0 uses XPath as the primary element location method

# Find by text:
xpath_click(serial, "//*[@text='Settings']", timeout=10.0)

# Find by resource-id:
xpath_wait_appear(serial, "//*[@resource-id='com.android.settings:id/title']", timeout=5.0)

# Find by content description:
xpath_click(serial, "//*[@content-desc='Navigate up']", timeout=5.0)

# Complex queries:
xpath_click(serial, "//android.widget.Button[@text='Submit' and @clickable='true']", timeout=10.0)
```

### Pattern 2: Device-Specific Adaptation
```markdown
# When working with different Android manufacturers:

Samsung devices: Adjust element selectors for Samsung UI
Huawei devices: Handle EMUI-specific behaviors
Xiaomi devices: Account for MIUI optimizations
```

### Pattern 3: Test Result Analysis
```bash
# Analyzing test failures
grep -A 5 "FAIL" test-report.txt | grep -E "(TC[0-9]+|Error)"
```

### Pattern 4: Test Result Monitoring
```bash
# When AI completes the test suite, it will generate a report like:

# Android UI Test Summary
# =======================
#
# Device: UGAILFCIU88TT469 (PDKM00, Android 11, SDK 31)
#
# Test Cases:
#   [PASS] TC001: Device Connection & Initialization
#   [PASS] TC002: Device Info & Capture
#   [PASS] TC006: XPath Element Operations
#   [PASS] TC007: Element Screenshot
#   [SKIP] TC010: Clipboard Operations (Android security restriction)
#
# Total: 9 passed, 1 skipped, 0 failed

# Save this report for CI/CD integration and regression tracking
```

## Troubleshooting Examples

### Issue: Device Not Detected
```bash
# Solution steps:
1. adb kill-server && adb start-server
2. Check USB debugging is enabled
3. Verify device authorization
4. Try different USB port/cable
```

### Issue: Element Not Found (v0.3.0)
```markdown
# Common solutions:
1. Use xpath_exists to verify element presence without waiting
2. Use dump_hierarchy to inspect current screen structure
3. Adjust XPath expressions for device UI variations
4. Increase timeout values for slower devices
5. Handle different locales (e.g., "Settings" vs "设置")
```

### Issue: Test Case Failures
```markdown
Common solutions:
- Update element selectors for device UI changes
- Adjust timing for slower devices
- Handle orientation differences
- Account for regional language settings
```

## v0.3.0 Migration Guide

### Tool Name Changes
```markdown
# Old tool names (v0.2.x) → New tool names (v0.3.0)

element_wait → xpath_wait_appear
element_wait_gone → xpath_wait_gone
element_click → xpath_click
element_click_nowait → xpath_click_nowait
element_long_click → xpath_long_press
element_screenshot → xpath_screenshot
element_get_text → xpath_get_text
element_set_text → xpath_set_text
element_bounds → xpath_get_bounds
element_swipe → xpath_swipe
element_scroll → xpath_scroll
element_scroll_to → xpath_scroll_to
```

### New Features in v0.3.0
```markdown
# New query tools:
- xpath_exists: Check if element exists without waiting
- xpath_get_info: Get complete element information dict
- xpath_get_attrib: Get specific attribute value by key

# New screenshot tool:
- xpath_save_screenshot: Save element screenshot to file

# Return value changes:
- xpath_screenshot now returns tuple: (base64_data_url, height, width)
- xpath_scroll returns bool: True if can scroll further, False otherwise
```

## Best Practice Recommendations

1. **Always deploy globally** for consistent availability
2. **Run regularly** to catch regressions early
3. **Customize for your devices** to improve reliability
4. **Monitor results** to identify patterns and improvements
5. **Document extensions** to maintain clarity for team members
6. **Use XPath** as the primary element location method (v0.3.0)
7. **Leverage new query tools** (xpath_get_info, xpath_get_attrib) for better element introspection

This skill exemplifies how to create robust, maintainable, and educational AI skills.
