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

## Production Usage Examples

### Example 1: AI-Driven Testing (Primary Method)
```bash
# Simply ask your AI client to execute the test suite
# Example prompts:
"Run the Android UI test suite on my connected device"
"Execute all android-ui-test skill tests"
"Run TC001-TC008 tests and provide a report"

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

### TC009: Network State Testing

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

### Pattern 1: Device-Specific Adaptation
```markdown
# When working with different Android manufacturers:

Samsung devices: Adjust element selectors for Samsung UI
Huawei devices: Handle EMUI-specific behaviors  
Xiaomi devices: Account for MIUI optimizations
```

### Pattern 2: Test Result Analysis
```bash
# Analyzing test failures
grep -A 5 "FAIL" test-report.txt | grep -E "(TC[0-9]+|Error)"
```

### Pattern 3: Test Result Monitoring
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
#   [SKIP] TC008: Clipboard Operations (Android security restriction)
#
# Total: 7 passed, 1 skipped, 0 failed

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

### Issue: Test Case Failures
```markdown
Common solutions:
- Update element selectors for device UI changes
- Adjust timing for slower devices
- Handle orientation differences
- Account for regional language settings
```

## Best Practice Recommendations

1. **Always deploy globally** for consistent availability
2. **Run regularly** to catch regressions early
3. **Customize for your devices** to improve reliability
4. **Monitor results** to identify patterns and improvements
5. **Document extensions** to maintain clarity for team members

This skill exemplifies how to create robust, maintainable, and educational AI skills.
