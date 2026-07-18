# Reasonix 工作区

> 个人 Reasonix 配置与技能工作区 · Windows

## 概览

| 项目 | 值 |
|------|-----|
| OS | Windows / amd64 |
| 模型 | DeepSeek V4 Flash (默认) + Mimo V2.5 (备用/视觉) |
| Git | v2.54.0 MinGit → `github.com/3432530644/reasonix-workspace.git` |
| Python | 3.11.3 |

## 已安装技能（共 20+）

### 💰 金融（10个 — finance-pack 插件包）
`mx-finance-data` · `akshare-stock` · `stock-price-query` · `stock-market-pro` ·
`stock-monitor-pro` · `stock-watcher` · `valuation-analysis` ·
`fund-analyzer` · `fund-news-daily` · `fund-invest-advisor`

### 📄 文档处理
`docx` · `pdf` · `pptx` · `xlsx`

### 🛠️ 开发工具
`mcp-builder` · `skill-creator` · `webapp-testing`

### 🎨 设计
`canvas-design` · `frontend-design`

### 🌐 其他
`aihot` · `dailyhot-skill` · `weather` · `ontology` · `organize-vault`
`codebase-design` · `diagnosing-bugs` · `domain-modeling` · `grilling` ·
`handoff` · `improve-codebase-architecture` · `tdd` · `teach` · `to-spec` ·
`writing-great-skills` · `skill-assistant-pro`

## MCP 服务

| 服务 | 用途 |
|:--|:--|
| `mcp-server-time` | 多时区时间获取/转换 |
| `mcp-server-fetch` | 网页内容抓取（新闻/公告） |
| `mcp-server-git` | Git 版本控制 |
| `mcp-server-playwright` | 浏览器自动化（导航/截图/点击） |

## 插件包

- **finance-pack** — 10个金融技能 + Playwright MCP 的捆绑包

## Agnes API（多模态）

从 `.env` 读取密钥，支持：
- 🔍 **视觉识别** — 截图分析（`agnes-2.0-flash` / chat/completions）
- 🎨 **图片生成** — 文生图/图生图（`agnes-image-2.0-flash` / images/generations）

## 关键记忆（共 13 条）

- `agnes-api-complete` — Agnes API 完整使用指南
- `em-api-key-eastmoney` — 东方财富 API Key
- `finance-analysis-skills` — 金融分析技能调用优先级
- `git-github-setup` — Git 配置 + 半自动提交推送工作流
- `installed-mcp-servers` — MCP 服务列表
- `loaded-extra-skills` — 全部技能清单（含目录结构）
- `user-stock-fund-repository` — 用户当前持仓
- `skills-first-workflow` — 先查技能再动手
- `new-skill-install-flow` — 新技能必须走 skill-assistant-pro 质检
- 等

## Git 工作流

Reasonix 半自动模式：完成有意义变更后主动询问 → 用户确认后 `add → commit → push`。
涉及 memory/ 的修改默认只提交不推送。
