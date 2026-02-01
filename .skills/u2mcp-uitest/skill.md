# u2mcp UI Test

Execute AI-driven UI automation tests on real Android devices.

## Usage

```
/uitest
```

## Description

AI acts as an automated tester to comprehensively test uiautomator2-mcp-server functionality on a connected Android device. The AI will:

- Auto-detect and select the first available device from `device_list`
- Verify device connection and initialization
- Test all touch and gesture actions
- Validate application management operations
- Execute element-based UI interactions
- Test input and clipboard operations
- Adapt to device state and provide intelligent feedback

## Requirements

- Connected Android device with USB debugging enabled
- ADB server running
- Device automatically selected from connected devices list

## Test Coverage

| Category | Tests |
|----------|-------|
| Device | Connection, Info, Screenshot, Hierarchy |
| Touch | Click, Long Click, Double Click |
| Gesture | Swipe, Drag, Key Press |
| App | List, Start, Wait, Info |
| Element | Wait, Bounds, Get Text, Click |
| Input | Text Input, Keyboard |
| Clipboard | Read/Write (with known limitations) |

## Output

Detailed test report with:
- Device information
- Pass/fail/skip status per test
- Error details if any
- Summary statistics
