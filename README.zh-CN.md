# uiautomator2-mcp-server

[![PyPI](https://img.shields.io/pypi/v/uiautomator2-mcp-server)](https://pypi.org/project/uiautomator2-mcp-server/)
[![CI](https://github.com/tanbro/uiautomator2-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/tanbro/uiautomator2-mcp-server/actions/workflows/ci.yml)
[![Language](https://img.shields.io/badge/lang-English-blue)](README.md)
[![Language](https://img.shields.io/badge/lang-中文-red)](README.zh-CN.md)

一个 [MCP](https://modelcontextprotocol.io/) 服务器，提供使用 [uiautomator2](https://github.com/openatx/uiautomator2) 控制 Android 设备的工具。

> 使用 AI 自动化你的 Android 设备：截图、点击/滑动、管理应用、发送文本等。

## 前置条件

- [Python][] 3.11+
- `adb` 在你的 PATH 中（通过 [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) 安装）
- Android 设备已开启 **USB 调试**

## 安装

### 独立安装

使用 [pip][]、[uv][]（推荐）或 [pipx][] 在系统上全局安装服务器：

```bash
# 使用 uv（推荐）
uv tool install uiautomator2-mcp-server

# 或使用 pipx
pipx install uiautomator2-mcp-server

# 或使用 pip
pip install uiautomator2-mcp-server
```

### 运行模式

MCP 服务器可以两种模式运行：

#### STDIO 模式（用于本地 MCP 客户端）

```bash
u2mcp stdio
```

此模式通过标准输入/输出通信，通常由直接生成服务器进程的 MCP 客户端使用。

#### HTTP 模式（用于远程/网络访问）

```bash
# 基本 HTTP 服务器
u2mcp --host 0.0.0.0 --port 8000 --no-token http

# 带认证令牌
u2mcp --host 0.0.0.0 --port 8000 --token YOUR_SECRET_TOKEN http
```

服务器将监听 `http://localhost:8000/mcp`（或你指定的主机/端口）。

## 测试和调试

### 使用 MCP Inspector

[MCP Inspector](https://github.com/modelcontextprotocol/inspector) 是一个命令行工具，用于测试和调试 MCP 服务器，无需 AI 客户端。

```bash
# 安装 MCP Inspector
npm install -g @modelcontextprotocol/inspector

# 在 STDIO 模式下检查服务器
npx @modelcontextprotocol/inspector u2mcp stdio

# 或在 HTTP 模式下检查服务器
# 首先启动服务器：u2mcp --host 0.0.0.0 --port 8000 http
# 然后使用 URL 运行 inspector
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

Inspector 将显示：
- 可用工具及其参数
- 服务器资源和提示
- 实时工具执行结果
- 请求/响应日志

### 使用 Postman 或 cURL

你可以使用任何 HTTP 客户端（如 Postman 或 cURL）测试 HTTP 端点。

#### 使用 cURL

```bash
# 1. 首先启动服务器
u2mcp --host 0.0.0.0 --port 8000 http

# 2. 在另一个终端中，发送 MCP 请求
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# 调用工具（例如，列出设备）
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "device_list",
      "arguments": {}
    }
  }'
```

#### 使用 Postman

1. 启动服务器：`u2mcp --host 0.0.0.0 --port 8000 http`
2. 创建一个新的 POST 请求到 `http://localhost:8000/mcp`
3. 设置请求头：
   - `Content-Type: application/json`
4. 在请求体中发送 JSON-RPC 2.0 请求：

列出工具的请求体示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

调用工具的请求体示例：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "device_list",
    "arguments": {}
  }
}
```

## MCP 客户端配置

此 MCP 服务器可与任何兼容 MCP 的客户端一起使用。以下是热门客户端的配置说明。

### Claude Desktop

将以下内容添加到你的 Claude Desktop 配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "android": {
      "command": "uvx",
      "args": ["uiautomator2-mcp-server", "stdio"]
    }
  }
}
```

如果你全局安装了该包，也可以使用：

```json
{
  "mcpServers": {
    "android": {
      "command": "u2mcp",
      "args": ["stdio"]
    }
  }
}
```

### Cursor

Cursor 是一个具有原生 MCP 支持的 AI 代码编辑器。

1. 打开 Cursor 设置（Cmd/Ctrl + ,）
2. 导航到 **MCP Servers**
3. 添加新服务器：

```json
{
  "mcpServers": {
    "android": {
      "command": "u2mcp",
      "args": ["stdio"]
    }
  }
}
```

### Cherry Studio

[Cherry Studio](https://cherry-ai.com/) 是一个具有完整 MCP 支持的跨平台 AI 桌面客户端。非常适合 Android 设备自动化任务。

1. 下载并安装 [Cherry Studio](https://github.com/CherryHQ/cherry-studio)
2. 打开设置并导航到 **MCP Servers**
3. 点击 **Add Server** 并配置：

**选项 A: 使用 uvx（推荐）**
```
Command: uvx
Arguments: uiautomator2-mcp-server stdio
```

**选项 B: 使用已安装的 u2mcp 命令**
```
Command: u2mcp
Arguments: stdio
```

**选项 C: HTTP 模式**
首先启动服务器：
```bash
u2mcp --host 0.0.0.0 --port 8000 --no-token http
```

然后在 Cherry Studio 中，选择 HTTP 模式并输入：
```
URL: http://localhost:8000/mcp
```

有关 Cherry Studio 中 MCP 配置的详细信息，请参阅[官方文档](https://docs.cherry-ai.com/docs/en-us/advanced-basic/mcp/config)。

### ChatMCP

[ChatMCP](https://github.com/daodao97/chatmcp) 是一个实现 MCP 协议的开源 AI 聊天客户端。支持多个 LLM 提供商（OpenAI、Claude、Ollama）。

1. 下载并安装 [ChatMCP](https://github.com/daodao97/chatmcp)
2. 打开设置并导航到 **MCP Servers**
3. 添加新服务器：

**使用 uvx（推荐）**
```
Command: uvx
Arguments: uiautomator2-mcp-server stdio
```

**使用已安装的 u2mcp 命令**
```
Command: u2mcp
Arguments: stdio
```

**HTTP 模式**
首先启动服务器：
```bash
u2mcp --host 0.0.0.0 --port 8000 --no-token http
```

然后在 ChatMCP 中，选择 HTTP 模式并输入：
```
URL: http://localhost:8000/mcp
```

### Cline

Cline 是一个支持 MCP 的 AI 编码助手扩展。

1. 在 IDE 中打开 Cline 设置
2. 导航到 **MCP Servers** 部分
3. 添加服务器配置：

```json
{
  "android": {
    "command": "u2mcp",
      "args": ["stdio"]
  }
}
```

### Continue

Continue 是 VS Code 和 JetBrains 的 AI 结对程序员扩展。

1. 安装 [Continue 扩展](https://marketplace.visualstudio.com/items?itemName=Continue.continue)
2. 打开 Continue 设置
3. 添加到你的 MCP 服务器配置：

```json
{
  "mcpServers": {
    "android": {
      "command": "u2mcp",
      "args": ["stdio"]
    }
  }
}
```

### HTTP 模式配置

对于支持 HTTP 连接的客户端（或用于远程访问），首先启动服务器：

```bash
u2mcp --host 0.0.0.0 --port 8000 --no-token http
```

然后配置你的客户端连接到 `http://localhost:8000/mcp`。

**注意：** 查看客户端的文档以了解 HTTP MCP 服务器配置，因为设置因客户端而异。

### 其他 MCP 客户端

服务器遵循 [Model Context Protocol](https://modelcontextprotocol.io/) 规范，可与任何兼容 MCP 的客户端一起使用，包括：

- **Windsurf** - 具有 MCP 支持的开发环境
- **Zed** - 具有 MCP 功能的代码编辑器
- **LibreChat** - 支持 MCP 的聊天界面
- **Chainlit** - 用于构建 AI 应用程序的平台

有关特定配置详细信息，请参阅你客户端的文档。

## 快速开始

1. **连接你的 Android 设备**，通过 USB 并启用 USB 调试
2. **初始化设备**（首次必需）：

   > "初始化我的 Android 设备"

3. **开始自动化**：

   > "截图"
   > "点击坐标 500, 1000"
   > "向上滑动"
   > "打开 YouTube 应用"

## 可用工具

### 设备
| 工具 | 描述 |
|------|-------------|
| `device_list` | 列出连接的设备 |
| `init` | 安装所需资源到设备（**首先运行**） |
| `info` | 获取设备信息 |
| `screenshot` | 截图 |
| `dump_hierarchy` | 获取 UI 层次结构 XML |

### 操作
| 工具 | 描述 |
|------|-------------|
| `click` | 在坐标处点击 |
| `long_click` | 在坐标处长按 |
| `double_click` | 在坐标处双击 |
| `swipe` | 从点 A 滑动到点 B |
| `swipe_points` | 滑动经过多个点 |
| `drag` | 从点 A 拖动到点 B |
| `press_key` | 按键（主屏幕、返回等） |
| `send_text` | 输入文本 |
| `clear_text` | 清除文本字段 |

### 应用
| 工具 | 描述 |
|------|-------------|
| `app_start` | 启动应用 |
| `app_stop` | 停止应用 |
| `app_list` | 列出已安装的应用 |
| `app_current` | 获取当前前台应用 |
| `app_install` | 安装 APK |
| `app_uninstall` | 卸载应用 |
| `app_info` | 获取应用信息 |
| `app_clear` | 清除应用数据 |

## 使用示例

```txt
你: 截图
Claude: [使用截图工具，显示图像]

你: 安装了哪些应用？
Claude: [使用 app_list 列出已安装的应用]

你: 打开 YouTube 应用
Claude: [使用包名调用 app_start]

你: 搜索"cats"
Claude: [使用 click 点击搜索栏，然后使用 send_text 输入"cats"]

你: 向下滚动
Claude: [使用 swipe 向下滚动]
```

## 许可证

GPL-3.0

------

[python]: https://www.python.org/ "Python 是一种编程语言，可以让你快速工作并更有效地集成系统。"
[pip]: https://pip.pypa.io/ "最流行的安装 Python 包的工具，也是现代版本的 Python 中包含的工具。"
[pipx]: https://pipx.pypa.io/ "pipx 是一个用于安装和运行 Python 命令行应用程序的工具，不会引起与系统上安装的其他包的依赖冲突。"
[uv]: https://docs.astral.sh/uv/ "一个极其快速的 Python 包和项目管理器"
