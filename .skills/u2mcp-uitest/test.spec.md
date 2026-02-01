# u2mcp UI Test Specification

## Overview
Comprehensive test suite for uiautomator2-mcp-server using real Android device.

## Prerequisites
- ADB server running
- Android device connected via USB (USB debugging enabled)
- Device automatically selected from `device_list`

## Environment Variables
- `U2_SKIP_INIT` - Skip device initialization if already done (default: `false`)

---

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

---

### TC002: Device Info & Capture

**Steps:**
1. Get window size via `window_size`
2. Take screenshot via `screenshot`
3. Dump UI hierarchy via `dump_hierarchy` with max_depth=3

**Expected Results:**
- Window size returns [width, height]
- Screenshot returns image data with valid dimensions
- Hierarchy returns valid XML structure

---

### TC003: Touch Actions

**Steps:**
1. Perform single click at center screen via `click`
2. Perform long press via `long_click`
3. Perform double click via `double_click`

**Expected Results:**
- All touch actions complete without errors
- Visual confirmation on device (if visible)

---

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

---

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

---

### TC006: Element Operations

**Steps:**
1. Wait for status bar element via `element_wait` with xpath `//*[@resource-id='com.android.systemui:id/status_bar']`
2. Get element bounds via `element_bounds`
3. Get element text via `element_get_text` for Settings icon
4. Click Settings element via `element_click` with xpath `//*[@text='Settings']` (or `//*[@text='设置']` for Chinese UI)
5. Wait for Settings app to be in foreground

**Expected Results:**
- Element wait returns true
- Bounds returns [left, top, right, bottom]
- Get text returns expected text
- Click executes successfully
- Settings app becomes foreground

---

### TC007: Input & Keyboard

**Steps:**
1. Launch Settings app
2. Use shell command to input text: `input text "Hello World"`
3. Hide keyboard via `hide_keyboard`

**Expected Results:**
- Text input executes
- Keyboard hide command executes

---

### TC008: Clipboard Operations

**Steps:**
1. Write text to clipboard via `write_clipboard` with "Test clipboard content"
2. Read clipboard via `read_clipboard`

**Expected Results:**
- **Known Limitation:** Write may fail due to Android security restrictions
- Read returns null or content (depends on app context)

---

## Cleanup

**Steps:**
1. Press HOME key to return to launcher
2. (Optional) Clear test app data

---

## Test Report Format

After execution, provide summary in format:

```
u2mcp UI Test Summary
=====================

Device: UGAILFCIU88TT469 (PDKM00, Android 11, SDK 31)

Test Cases:
  [PASS] TC001: Device Connection & Initialization
  [PASS] TC002: Device Info & Capture
  [PASS] TC003: Touch Actions
  [PASS] TC004: Gesture Actions
  [PASS] TC005: Application Management
  [PASS] TC006: Element Operations
  [PASS] TC007: Input & Keyboard
  [SKIP] TC008: Clipboard Operations (Android security restriction)

Total: 7 passed, 1 skipped, 0 failed
```

---

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
