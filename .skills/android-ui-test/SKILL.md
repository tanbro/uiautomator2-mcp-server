---
name: android-ui-test
description: Demonstration skill showing how to use uiautomator2-mcp-server for AI-driven Android UI testing. Also serves as the project's own automated UI test suite for continuous validation.
license: MIT
compatibility: Requires connected Android device with USB debugging enabled and ADB server running
metadata:
  author: uiautomator2-mcp-server team
  version: 1.0.0
  purpose: dual-purpose demonstration and production testing
---

# Android UI Test Automation (Demo & Production)

This skill serves a dual purpose:
1. **Demonstration**: Shows how to build AI-driven Android UI testing skills
2. **Production Testing**: Acts as the project's own automated UI test suite

## Goals

- Demonstrate best practices for Android UI automation skills
- Provide comprehensive testing for uiautomator2-mcp-server functionality
- Enable AI agents to validate Android device interactions
- Serve as a reference implementation for similar skills

## Prerequisites

- Connected Android device with USB debugging enabled
- ADB server running (`adb start-server`)
- uiautomator2-mcp-server properly configured

## Usage Scenarios

### Scenario 1: Learning Example
When developers want to understand how to create Android UI testing skills:
- Study the structured approach in this skill
- Learn proper YAML metadata formatting
- Understand test case organization and execution flow
- See how to handle device-specific considerations

### Scenario 2: Production Testing
When validating uiautomator2-mcp-server functionality:
- Execute complete test suite automatically
- Generate detailed pass/fail reports
- Validate all core device interaction capabilities
- Ensure consistent performance across device variations

## Test Execution Flow

### Phase 1: Device Setup and Validation
1. List connected devices via `device_list`
2. Select first available device
3. Initialize device via `init` tool
4. Verify device connectivity and basic info

### Phase 2: Comprehensive Functionality Tests
1. **Device Operations**: Info, screenshot, UI hierarchy dump
2. **Touch Actions**: Click, long press, double click at various positions
3. **Gesture Operations**: Swipe, drag, system key presses
4. **Application Management**: List apps, launch apps, get app info
5. **Element Interactions**: Wait for elements, get bounds, text extraction, element clicks
6. **Input Operations**: Text input, keyboard management
7. **Clipboard Operations**: Read/write clipboard content

### Phase 3: Intelligent Reporting
Generate comprehensive test report with:
- Device information and specifications
- Detailed pass/fail/skip status for each test case
- Error messages and troubleshooting guidance
- Performance metrics and recommendations

## Key Features Demonstrated

✅ **Structured Skill Organization**: Clear directory structure and file naming
✅ **Proper Metadata**: Standard YAML frontmatter with complete information
✅ **Progressive Disclosure**: Light metadata, detailed content on demand
✅ **Error Handling**: Graceful handling of device-specific limitations
✅ **Comprehensive Testing**: Covers all major uiautomator2-mcp-server capabilities
✅ **Self-Documentation**: Clear instructions for both learning and execution

## Expected Outcomes

### For Learning:
- Clear understanding of skill structure and best practices
- Working example of Android UI automation implementation
- Reference for creating similar skills

### For Testing:
- ✅ All core functionality tests pass
- ✅ Device operations work reliably
- ✅ UI interactions execute correctly
- ✅ Comprehensive test report generated

## Best Practices Highlighted

- **Modular Design**: Separate concerns into scripts, references, and documentation
- **Clear Documentation**: Self-explanatory structure and comprehensive guides
- **Robust Error Handling**: Anticipate and handle common failure scenarios
- **Scalable Architecture**: Easy to extend with additional test cases
- **Cross-Platform Considerations**: Handle device manufacturer variations

## Extension Points

This skill can be easily extended for:
- Additional device types and manufacturers
- Custom test scenarios and workflows
- Integration with CI/CD pipelines
- Advanced reporting and analytics
- Performance benchmarking

## Release Workflow

This skill is also used during the release process to validate uiautomator2-mcp-server functionality:

### Pre-Release Testing
Before each release:
1. Ensure all 69 unit tests pass
2. Run doctor command: `u2mcp doctor -v`
3. Execute Android UI tests on physical device
4. Verify all 77 MCP tools are registered

### Release Process
The project uses automated CI/CD pipeline:

1. **Version Tag**: Create a PEP 440 compliant tag (e.g., `v0.3.3`)
2. **CI Build**: GitHub Actions automatically:
   - Runs lint, type check, and tests
   - Builds distribution packages
   - Publishes to PyPI
   - Creates GitHub Release with CHANGELOG notes
   - **Updates server.json version** automatically
   - Publishes to MCP Registry

3. **server.json Update**:
   ```bash
   # CI automatically does this during release:
   jq --arg v "0.3.3" '.version = $v | .packages[0].version = $v' server.json > server.json.tmp
   mv server.json.tmp server.json
   ```

4. **MCP Registry Publish**:
   - Uses GitHub OIDC for authentication
   - Validates package ownership via PyPI
   - Publishes server.json to official MCP registry

For implementation details, see the accompanying scripts and documentation.
