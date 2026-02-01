# uiautomator2-mcp-server

[![PyPI](https://img.shields.io/pypi/v/uiautomator2-mcp-server)](https://pypi.org/project/uiautomator2-mcp-server/)
[![CI](https://github.com/tanbro/uiautomator2-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/tanbro/uiautomator2-mcp-server/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/gh/tanbro/uiautomator2-mcp-server)](https://codecov.io/gh/tanbro/uiautomator2-mcp-server)
[![GitHub release](https://img.shields.io/github/v/release/tanbro/uiautomator2-mcp-server)](https://github.com/tanbro/uiautomator2-mcp-server/releases)
[![Language](https://img.shields.io/badge/lang-English-blue)](README.md)
[![Language](https://img.shields.io/badge/lang-中文-red)](README.zh-CN.md)

> **注**：本文件包含有关中国大陆用户加速下载（`pip` / `uv` 镜像源）的**详细说明**；英文版仅包含指向本文件的提示。

一个 [MCP](https://modelcontextprotocol.io/) 服务器，提供使用 [uiautomator2](https://github.com/openatx/uiautomator2) 控制 Android 设备的工具。

> 使用 AI 自动化你的 Android 设备：截图、点击/滑动、管理应用、发送文本等。

## 从 v0.1.x 版本迁移

**如果你正在从 v0.1.3 或更早版本升级：** CLI 现在需要显式指定子命令。请将你的命令从：

```bash
# 旧版本（v0.1.3 及更早）
u2mcp

# 新版本（v0.2.0+）
u2mcp stdio
```

所有其他命令保持不变（只需添加传输子命令）。

## 前置条件

- [Python][] 3.11+
- `adb` 在你的 PATH 中（通过 [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) 安装)
- Android 设备已开启 **USB 调试**

------

> **💡 工具选择建议：**
>
> - **MCP 客户端使用**（Claude Desktop、Cursor 等）：推荐安装 **[uv][]**，使用 `uvx` 直接运行 Python 包
> - **独立运行/调试**：可以使用 **[uv][]**、**[pip][]** 或 **[pipx][]**
>
> 大多数情况下，安装 **uv** 即可满足所有需求。

------

> **💡 中国大陆用户加速：**
>
> 如果使用 `pip` 安装软件包的速度较慢，建议配置国内镜像源。
>
> **方法一：使用 pip config 命令（推荐）**
>
> ```bash
> # 设置（操作系统用户级别的）全局镜像源
> pip config set --user global.index-url https://mirrors.aliyun.com/pypi/simple/
>
> # 验证配置
> pip config list
> ```
>
> **方法二：配置文件**
>
> 创建或编辑配置文件：
> - **Unix/macOS**: `~/.config/pip/pip.conf` 或 `~/.pip/pip.conf`（旧路径，仍支持）
> - **Windows**: `%APPDATA%\pip\pip.ini`
>
> ```ini
> [global]
> index-url = https://mirrors.aliyun.com/pypi/simple/
> ```
>
> **方法三：环境变量**
>
> - **macOS/Linux** (添加到 `~/.bashrc`、`~/.zshrc` 等):
> ```bash
> export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
> ```
>
> - **Windows** (系统环境变量):
> ```
> PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
> ```
>
> 其他可用的镜像源：
> - **腾讯云**：`https://mirrors.cloud.tencent.com/pypi/simple/`
> - **华为云**：`https://mirrors.huaweicloud.com/repository/pypi/simple/`
> - **清华大学**：`https://pypi.tuna.tsinghua.edu.cn/simple/`
> - **中科大**：`https://pypi.mirrors.ustc.edu.cn/simple/`
>
> 此配置对 `pip` 和 `pipx` 都生效。

### 安装 `uv`（推荐用于 MCP 客户端）

大多数 MCP 客户端（如 Claude Desktop）使用 `uvx` 来运行 Python MCP 服务器。`uvx` 是 [uv][] 工具套件的一部分。

> **为什么选择 `uvx`？** `uvx` 可以直接从 PyPI 运行 Python 包，无需手动安装——只需使用 `uvx package-name`，其余的它会自动处理。这使得它非常适合 MCP 客户端配置。

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

或使用 `winget`:
```powershell
winget install --id=astral-sh.uv -e
```

验证安装：
```bash
uv --version
uvx --version
```

> **💡 中国大陆用户加速：**
>
> 安装完毕之后，如果 [uv][] 下载软件包的速度较慢，可以配置国内镜像源。
>
> **方法一：配置文件**
>
> 创建或编辑 `~/.config/uv/uv.toml`（macOS/Linux）或 `%APPDATA%\uv\uv.toml`（Windows）：
>
> ```toml
> [[index]]
> url = "https://mirrors.aliyun.com/pypi/simple/"
> default = true
> ```
>
> **方法二：环境变量**
>
> - **macOS/Linux** (添加到 `~/.bashrc`、`~/.zshrc` 等):
> ```bash
> export UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple/
> ```
>
> - **Windows** (系统环境变量):
> ```
> UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple/
> ```
>
> 其他可用的镜像源：
> - **腾讯云**：`https://mirrors.cloud.tencent.com/pypi/simple/`
> - **华为云**：`https://mirrors.huaweicloud.com/repository/pypi/simple/`
> - **清华大学**：`https://pypi.tuna.tsinghua.edu.cn/simple/`
> - **中科大**：`https://pypi.mirrors.ustc.edu.cn/simple/`

### 安装 `pipx`（替代方案）

[pipx][] 是另一个用于在隔离环境中安装和运行 Python CLI 应用程序的工具。

> **`pipx` vs `uvx`：** 和 `uvx` 一样，`pipx` 也可以通过 `pipx run package-name` 直接运行包。不过 `uvx` 通常更快，在 MCP 生态系统中也更常用。

**macOS / Linux:**
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

**Windows:**
```powershell
python -m pip install --user pipx
python -m pipx ensurepath
```

> **注意**：`pipx` 会使用上面配置的 pip 镜像源，无需额外配置。

## 安装

**首选：免安装直接运行**，使用 `uvx`（推荐）或 `pipx run` 从 PyPI 直接运行包：

```bash
# 使用 uvx（推荐）直接运行
uvx uiautomator2-mcp-server stdio

# 或使用 pipx 直接运行
pipx run uiautomator2-mcp-server stdio
```

**如果需要全局安装命令或长期使用**，你也可以选择安装：

```bash
# 使用 uv（tool 方式安装）
uv tool install uiautomator2-mcp-server

# 或使用 pipx 安装
pipx install uiautomator2-mcp-server

# 或使用 pip 安装
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
u2mcp http --host 0.0.0.0 --port 8000 --no-token

# 带认证令牌
u2mcp http --host 0.0.0.0 --port 8000 --token YOUR_SECRET_TOKEN
```

服务器将监听 `http://localhost:8000/mcp`（或你指定的主机/端口）。

### CLI 实用命令

`u2mcp` CLI 提供了几个实用命令用于探索可用的工具和标签：

```bash
# 列出所有可用工具
u2mcp tools

# 显示特定工具的详细信息
u2mcp info screenshot

# 显示匹配模式的所有工具（支持通配符）
u2mcp info "device:*"     # 所有设备工具
u2mcp info "*screenshot*" # 名称中包含 'screenshot' 的工具

# 列出所有可用的工具标签
u2mcp tags

# 显示版本信息
u2mcp version
```

### 工具过滤

你可以使用基于标签的过滤来选择性暴露工具。这会减少 LLM 可用的工具数量，从而提高性能并减少困惑。

```bash
# 只暴露设备管理工具
u2mcp stdio --include-tags device:manage

# 只暴露触摸和手势操作
u2mcp stdio --include-tags action:touch,action:gesture

# 排除屏幕镜像工具
u2mcp stdio --exclude-tags screen:mirror

# 只暴露应用生命周期和元素交互工具
u2mcp stdio --include-tags app:lifecycle,element:interact

# 排除 shell 命令工具（出于安全考虑）
u2mcp stdio --exclude-tags device:shell

# 只暴露输入相关工具
u2mcp stdio --include-tags input:text,input:keyboard

# 组合使用 include 和 exclude
u2mcp stdio --include-tags device:info,action:touch --exclude-tags screen:capture

# 通配符模式 - 包含所有设备工具
u2mcp stdio --include-tags "device:*"

# 通配符模式 - 包含所有触摸和手势工具
u2mcp stdio --include-tags "action:to*"

# 通配符模式 - 排除所有屏幕工具
u2mcp stdio --exclude-tags "screen:*"

# 通配符模式 - 排除所有镜像工具（screen:mirror 等）
u2mcp stdio --exclude-tags "*:mirror"

# 列出所有可用标签
u2mcp tags
```

**通配符支持：**

`--include-tags` 和 `--exclude-tags` 选项支持通配符模式：
- `*` 匹配任意字符
- `?` 匹配恰好一个字符
- `device:*` 匹配所有 device:* 标签
- `*:mirror` 匹配所有镜像标签（screen:mirror 等）
- `action:to*` 匹配 action:touch、action:tool（如果存在）

**可用标签：**

| 标签 | 描述 |
|-----|------|
| `device:manage` | 设备连接、初始化和管理 |
| `device:info` | 设备信息和状态 |
| `device:capture` | 截图和 UI 层级 |
| `device:shell` | Shell 命令执行 |
| `action:touch` | 点击和触摸操作 |
| `action:gesture` | 滑动和拖动手势 |
| `action:key` | 物理按键操作 |
| `action:screen` | 屏幕控制（开/关） |
| `app:manage` | 安装和卸载应用 |
| `app:lifecycle` | 启动和停止应用 |
| `app:info` | 应用信息和列表 |
| `app:config` | 应用配置（清除数据、权限） |
| `element:wait` | 等待元素/活动 |
| `element:interact` | 点击和交互元素 |
| `element:query` | 获取元素信息（文本、边界） |
| `element:modify` | 修改元素（设置文本） |
| `element:gesture` | 元素特定手势（滑动、滚动） |
| `element:capture` | 元素截图 |
| `input:text` | 文本输入和清除 |
| `input:keyboard` | 键盘控制 |
| `clipboard:read` | 读取剪贴板 |
| `clipboard:write` | 写入剪贴板 |
| `screen:mirror` | 屏幕镜像（scrcpy） |
| `screen:capture` | 屏幕截图 |
| `util:delay` | 延迟/休眠实用工具 |

## 测试和调试

### 使用 MCP Inspector

[MCP Inspector](https://github.com/modelcontextprotocol/inspector) 是一个命令行工具，用于测试和调试 MCP 服务器，无需 AI 客户端。

```bash
# 安装 MCP Inspector
npm install -g @modelcontextprotocol/inspector

# 在 STDIO 模式下检查服务器
npx @modelcontextprotocol/inspector u2mcp stdio

# 或在 HTTP 模式下检查服务器
# 首先启动服务器：u2mcp http --host 0.0.0.0 --port 8000
# 然后使用 URL 运行 inspector
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

Inspector 将显示：
- 可用工具及其参数
- 服务器资源和提示
- 实时工具执行结果
- 请求/响应日志

### 使用 Postman

[Postman](https://www.postman.com/) 具有原生 MCP 支持，用于测试和调试 MCP 服务器。

1. 打开 Postman 并创建一个新的 **MCP Request**
2. 输入服务器连接详情：

**STDIO 模式：**
```
Command: u2mcp
Arguments: stdio
```

**HTTP 模式：**
```
URL: http://localhost:8000/mcp
```
（首先启动服务器：`u2mcp http --host 0.0.0.0 --port 8000`）

3. 点击 **Load Capabilities** 连接并发现可用工具
4. 使用 **Tools**、**Resources** 和 **Prompts** 标签与服务器交互
5. 点击 **Run** 执行工具调用并查看响应

有关更多信息，请参阅 [Postman MCP 文档](https://learning.postman.com/docs/postman-ai/mcp-requests/overview/)。

### 使用 cURL

你也可以使用 cURL 通过 JSON-RPC 2.0 请求测试 HTTP 端点：

```bash
# 1. 首先启动服务器
u2mcp http --host 0.0.0.0 --port 8000

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
u2mcp http --host 0.0.0.0 --port 8000 --no-token
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
u2mcp http --host 0.0.0.0 --port 8000 --no-token
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

## AI 驱动的 UI 测试

本项目包含一个 AI 驱动的 UI 测试技能，允许你使用自然语言在 Android 设备上运行全面的自动化测试。AI 充当自动化测试员，根据设备状态自适应地执行测试步骤。

### 运行 UI 测试

只需让 AI 执行 UI 测试：

```
执行 u2mcp UI 测试
```

AI 将会：
- 自动检测并连接到第一个可用设备
- 运行涵盖所有设备操作的全面测试
- 提供详细的测试报告，包括通过/失败状态

### 测试覆盖

| 类别 | 测试内容 |
|------|---------|
| 设备 | 连接、信息、截图、层级 |
| 触摸 | 点击、长按、双击 |
| 手势 | 滑动、拖拽、按键 |
| 应用 | 列表、启动、等待、信息 |
| 元素 | 等待、边界、获取文本、点击 |
| 输入 | 文本输入、键盘 |
| 剪贴板 | 读取/写入（有已知限制） |

### 测试规范

测试套件定义在 `.skills/u2mcp-uitest/test.spec.md` 中。你可以通过编辑此文件来查看或扩展测试用例。

### 测试报告示例

```
u2mcp UI 测试总结
==================

设备: UGAILFCIU88TT469 (PDKM00, Android 11, SDK 31)

测试用例:
  [通过] TC001: 设备连接与初始化
  [通过] TC002: 设备信息与捕获
  [通过] TC003: 触摸操作
  [通过] TC004: 手势操作
  [通过] TC005: 应用管理
  [通过] TC006: 元素操作
  [通过] TC007: 输入与键盘
  [跳过] TC008: 剪贴板操作（Android 安全限制）

总计: 7 通过, 1 跳过, 0 失败
```

### 创建自定义测试

你可以通过在 `.skills/` 下添加新的技能目录来创建自己的测试规范。每个技能应包含：

- `skill.md` - 技能描述和使用说明
- `test.spec.md` - 测试用例，包含步骤和预期结果

参考 `.skills/u2mcp-uitest/` 获取完整示例。

## 可用工具

### 设备
| 工具 | 描述 |
|------|-------------|
| `device_list` | 列出连接的 Adb 设备 |
| `init` | 安装所需资源到设备（**首先运行**） |
| `purge` | 从设备移除已安装的 uiautomator 资源 |
| `connect` | 连接到设备并返回设备信息 |
| `disconnect` | 断开单个设备的连接 |
| `disconnect_all` | 断开所有设备连接 |
| `shell_command` | 在设备上运行 shell 命令，返回 `(exit_code, output)` |
| `window_size` | 获取窗口尺寸（`width`, `height`） |
| `screenshot` | 截图，返回 `width`、`height` 和 `image`（JPEG data URL） |
| `save_screenshot` | 保存截图到文件（返回文件路径，格式由文件扩展名决定） |
| `dump_hierarchy` | 获取 UI 层次结构 XML |
| `info` | 获取设备信息 |

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
| `send_text` | 输入文本（支持 `clear` 参数） |
| `clear_text` | 清除文本字段 |
| `screen_on` | 打开屏幕 |
| `screen_off` | 关闭屏幕 |
| `hide_keyboard` | 隐藏软键盘 |

### 应用
| 工具 | 描述 |
|------|-------------|
| `app_install` | 安装 APK（文件路径或 URL） |
| `app_uninstall` | 卸载应用 |
| `app_uninstall_all` | 卸载多个应用（支持排除列表） |
| `app_start` | 启动应用 |
| `app_wait` | 等待应用启动（`timeout`, `front`） |
| `app_stop` | 停止应用 |
| `app_stop_all` | 停止所有第三方应用（支持排除） |
| `app_clear` | 清除应用数据 |
| `app_info` | 获取应用信息（`versionName`, `versionCode`） |
| `app_current` | 获取当前前台应用 |
| `app_list` | 列出已安装应用（支持 `filter`） |
| `app_list_running` | 列出正在运行的应用 |
| `app_auto_grant_permissions` | 自动授予应用运行时权限 |

### 剪切板
| 工具 | 描述 |
|------|-------------|
| `read_clipboard` | 读取设备剪切板文本 |
| `write_clipboard` | 写入设备剪切板文本 |

### 元素操作
| 工具 | 描述 |
|------|-------------|
| `activity_wait` | 等待某个 Activity 出现 |
| `element_wait` | 等待元素出现 |
| `element_wait_gone` | 等待元素消失 |
| `element_click` | 按 xpath 查找并点击（带等待） |
| `element_click_nowait` | 立即点击元素（不等待） |
| `element_click_until_gone` | 点击直到元素消失 |
| `element_long_click` | 长按元素 |
| `element_screenshot` | 截取元素图片（返回与 `screenshot` 相同格式） |
| `element_get_text` | 获取元素文本 |
| `element_set_text` | 设置元素文本 |
| `element_bounds` | 获取元素边界（left, top, right, bottom） |
| `element_swipe` | 在元素内部滑动 |
| `element_scroll` | 滚动元素（`forward`/`backward`） |
| `element_scroll_to` | 滚动到元素，最多指定次数 |

### scrcpy
| 工具 | 描述 |
|------|-------------|
| `start_scrcpy` | 后台启动 `scrcpy` 并返回进程 id（pid） |
| `stop_scrcpy` | 通过 pid 停止运行的 `scrcpy` 进程 |

> **说明：**
> - `screenshot` 与 `element_screenshot` 会返回 JPEG data URL（`data:image/jpeg;base64,...`）以及 `width`/`height`。
> - `shell_command` 返回 `(exit_code, output)`。
> - `start_scrcpy` 会返回后台进程 id（pid），可用于后续调用 `stop_scrcpy`。

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
