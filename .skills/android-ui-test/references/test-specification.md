# Android UI Test Specification

## Overview
Comprehensive test suite for Android device automation using uiautomator2-mcp-server v0.3.0.

## Prerequisites
- ADB server running
- Android device connected via USB (USB debugging enabled)
- Device automatically selected from `device_list`

## Environment Variables
- `U2_SKIP_INIT` - Skip device initialization if already done (default: `false`)

## Test Cases

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

### TC002: Device Info & Capture

**Steps:**
1. Get window size via `window_size`
2. Take screenshot via `screenshot`
3. Dump UI hierarchy via `dump_hierarchy` with max_depth=3

**Expected Results:**
- Window size returns {width: int, height: int}
- Screenshot returns image data with valid dimensions
- Hierarchy returns valid XML structure

### TC003: Touch Actions

**Steps:**
1. Perform single click at center screen via `click`
2. Perform long press via `long_click`
3. Perform double click via `double_click`

**Expected Results:**
- All touch actions complete without errors
- Visual confirmation on device (if visible)

### TC004: Gesture Actions

**Steps:**
1. Perform swipe up gesture via `swipe`
2. Perform drag gesture via `drag`
3. Press HOME key via `press_key`
4. Press BACK key via `press_key`

**Expected Results:**
- All gestures execute successfully
- Home key returns to launcher
- Back key navigates back

### TC005: Application Management

**Steps:**
1. Get current app via `app_current`
2. List running apps via `app_list_running`
3. Start Settings app via `app_start` with `com.android.settings/.Settings`
4. Wait for app via `app_wait` with timeout=5
5. Get app info via `app_info` for `com.android.settings`

**Expected Results:**
- Current app info returned
- Running apps list contains multiple entries
- Settings app launches successfully
- App info contains version information

### TC006: XPath Element Operations

**Steps:**
1. Wait for status bar element via `xpath_wait_appear` with xpath `//*[@resource-id='com.android.systemui:id/status_bar']` and timeout=5
2. Check if element exists via `xpath_exists` with xpath `//*[@text='Settings']` (or `//*[@text='设置']` for Chinese UI)
3. Get element bounds via `xpath_get_bounds`
4. Get element text via `xpath_get_text`
5. Get element info via `xpath_get_info`
6. Get element attribute via `xpath_get_attrib` with key="className"
7. Click Settings element via `xpath_click` with xpath `//*[@text='Settings']` (or `//*[@text='设置']`) and timeout=5
8. Wait for Settings app to be in foreground

**Expected Results:**
- Element wait returns true
- Element exists check returns true
- Bounds returns (left, top, right, bottom) tuple
- Get text returns expected text
- Get info returns dict with element properties
- Get attrib returns attribute value or empty string
- Click executes successfully
- Settings app becomes foreground

### TC007: Element Screenshot

**Steps:**
1. Find a visible UI element (e.g., status bar)
2. Take element screenshot via `xpath_screenshot` with format="jpeg"
3. Save element screenshot via `xpath_save_screenshot` to a temp file

**Expected Results:**
- xpath_screenshot returns tuple with base64 data URL, height, width
- xpath_save_screenshot returns absolute path to saved file
- Screenshots are valid JPEG images

### TC008: Element Gestures

**Steps:**
1. Find a scrollable container via xpath
2. Swipe within element via `xpath_swipe` with direction="left" and scale=0.6
3. Scroll within element via `xpath_scroll` with direction="forward"
4. Scroll screen to find element via `xpath_scroll_to` with direction="forward" and max_swipes=10

**Expected Results:**
- All gesture operations execute without errors
- Scroll returns True if can scroll further, False otherwise

### TC009: Input & Keyboard

**Steps:**
1. Launch Settings app
2. Use `shell_command` to input text: `input text "Hello World"`
3. Hide keyboard via `hide_keyboard`

**Expected Results:**
- Text input executes
- Keyboard hide command executes

### TC010: Clipboard Operations

**Steps:**
1. Write text to clipboard via `write_clipboard` with "Test clipboard content"
2. Read clipboard via `read_clipboard`

**Expected Results:**
- **Known Limitation:** Write may fail due to Android security restrictions
- Read returns null or content (depends on app context)

## Cleanup

**Steps:**
1. Press HOME key to return to launcher
2. (Optional) Clear test app data

## Test Report Format

After execution, provide summary in format:

```
Android UI Test Summary
=======================

Device: [DEVICE_SERIAL] ([MODEL], Android [VERSION], SDK [SDK_VERSION])

Test Cases:
  [PASS] TC001: Device Connection & Initialization
  [PASS] TC002: Device Info & Capture
  [PASS] TC003: Touch Actions
  [PASS] TC004: Gesture Actions
  [PASS] TC005: Application Management
  [PASS] TC006: XPath Element Operations
  [PASS] TC007: Element Screenshot
  [PASS] TC008: Element Gestures
  [PASS] TC009: Input & Keyboard
  [SKIP] TC010: Clipboard Operations (Android security restriction)

Total: 9 passed, 1 skipped, 0 failed
```

## Notes

### Device-Specific Considerations
- **Oppo/ColorOS devices:** May have additional security restrictions
- **Screen orientation:** Tests assume portrait mode (1080x2400)
- **Language:** Some tests may need adjustment for different locales (e.g., "Settings" vs "设置")

### Troubleshooting
- If element not found: Current screen may differ, dump hierarchy to inspect
- If app won't start: Check package/activity name for device variant
- If clipboard fails: Expected behavior due to security restrictions

### Extending Tests
Add new test cases following the TC### numbering scheme and include:
- Clear steps
- Expected results
- Cleanup requirements

## v0.3.0 API Changes

This test specification has been updated for v0.3.0 with the following changes:

1. **Element tools renamed to XPath:**
   - `element_wait` → `xpath_wait_appear`
   - `element_wait_gone` → `xpath_wait_gone`
   - `element_click` → `xpath_click`
   - `element_click_nowait` → `xpath_click_nowait`
   - `element_long_click` → `xpath_long_press`
   - `element_screenshot` → `xpath_screenshot`
   - `element_get_text` → `xpath_get_text`
   - `element_set_text` → `xpath_set_text`
   - `element_bounds` → `xpath_get_bounds`
   - `element_swipe` → `xpath_swipe`
   - `element_scroll` → `xpath_scroll`
   - `element_scroll_to` → `xpath_scroll_to`

2. **New XPath tools:**
   - `xpath_exists` - Check if element exists without waiting
   - `xpath_get_info` - Get complete element info dict
   - `xpath_get_attrib` - Get specific attribute value
   - `xpath_save_screenshot` - Save element screenshot to file

3. **Removed tools:**
   - `activity_wait` - Use `activity_wait_appear` from device tools instead
   - `element_click_until_gone` - No longer available
