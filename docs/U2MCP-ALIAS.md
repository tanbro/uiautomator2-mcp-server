# u2mcp 别名包发布说明

## 背景

为了提供更简洁的用户体验，我们计划在 v1.0.0 将主包名从 `uiautomator2-mcp-server` 改为 `u2mcp`。

在 v0.3.0 中，我们采用过渡方案：
- 主包名保持 `uiautomator2-mcp-server`
- 发布 `u2mcp` 作为别名包
- 用户可以用 `pip install u2mcp` 或 `uvx u2mcp stdio`

## 别名包设计

### 包结构

```
u2mcp/
├── pyproject.toml          # 依赖 uiautomator2-mcp-server>=0.3.0
├── README.md               # 简短说明
└── u2mcp/
    └── __init__.py         # 导出版本号
```

### 关键配置

```toml
[project]
name = "u2mcp"
version = "0.3.0"
dependencies = ["uiautomator2-mcp-server>=0.3.0"]

[project.scripts]
u2mcp = "u2mcp.__main__:main"  # 转发到主包的入口
```

### 工作原理

1. **依赖安装**：`pip install u2mcp` 会自动安装 `uiautomator2-mcp-server`
2. **入口转发**：`u2mcp` 命令转发到 `u2mcp.__main__:main`（来自主包）
3. **版本同步**：别名包版本与主包版本保持一致

## 用户使用方式

| 方式 | 命令 |
|------|------|
| uvx 直接运行 | `uvx u2mcp stdio` |
| pip 安装后使用 | `pip install u2mcp && u2mcp stdio` |
| uv tool 安装 | `uv tool install u2mcp` |
| pipx 安装 | `pipx install u2mcp` |

## 发布步骤

详见 [docs/PUBLISHING-U2MCP-ALIAS.md](docs/PUBLISHING-U2MCP-ALIAS.md)

简述：
1. 创建临时目录
2. 复制 `pyproject-u2mcp-alias.toml` → `pyproject.toml`
3. 复制 `README-ALIAS.md` → `README.md`
4. 创建 `u2mcp/__init__.py`（使用 `u2mcp-alias-init.py`）
5. `uv build --out-dir dist/`
6. `uv publish dist/u2mcp-*.whl dist/u2mcp-*.tar.gz`

## 版本策略

| 主包版本 | 别名包版本 | 说明 |
|---------|-----------|------|
| 0.3.0 | 0.3.0 | 首次发布别名包 |
| 0.4.0 | 0.4.0 | 同步版本 |
| 1.0.0 | 1.0.0 | 主包迁移到 u2mcp |

## 文件清单

| 文件 | 用途 |
|------|------|
| `pyproject-u2mcp-alias.toml` | 别名包配置模板 |
| `README-ALIAS.md` | 别名包 README 模板 |
| `u2mcp-alias-init.py` | 别名包 `__init__.py` 模板 |
| `docs/PUBLISHING-U2MCP-ALIAS.md` | 发布说明文档 |
| `README-PLACEHOLDER.md` | ~~旧版占位说明~~（已废弃） |
| `pyproject-u2mcp-placeholder.toml` | ~~旧版占位配置~~（已废弃） |

## 注意事项

1. **每次发布主包时同步发布别名包**
2. **保持版本号一致**
3. **v1.0.0 前不需要修改主包代码**
4. **PyPI 名称 `u2mcp` 确认空闲**（已验证）

## 下一步

- [ ] v0.3.0 发布前，按步骤发布 `u2mcp` 别名包
- [ ] 更新 CHANGELOG.md 添加别名包说明
- [ ] 在 README 中强调 `uvx u2mcp stdio` 的用法
