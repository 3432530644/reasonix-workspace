# Reasonix 工作区

> 个人 Reasonix 配置与技能工作区 · Windows

## 概览

| 项目 | 值 |
|------|-----|
| OS | Windows / amd64 |
| 模型 | DeepSeek V4 Flash (默认) |
| Git | v2.54.0 MinGit → `github.com/3432530644/reasonix-workspace.git` |
| Python | 3.11.3 |

## 🤖 国内免费 AI 全家桶（2026-08-01，零代理）

**Gemini / Clash 已弃用**——全部走国内直连免费 AI：

| 能力 | 方案 | 依赖 |
|:--|:--|:--|
| 图片语义理解 / 生图 / 文本 | **doubao2api**（豆包 OpenAI 兼容 API `127.0.0.1:9090`） | doubao2api 服务 |
| 看图 / 生图 / 文本（元宝主力） | **AgentChat**（CDP 操作网页 AI，元宝→豆包→Kimi 降级链） | Chrome daemon 9222 |
| 纯文字提取（OCR） | **本地 rapidocr**（`ocr-vision` skill） | 无 |
| 多 AI 并行分发 | AgentChat-IndependentTasks（plan JSON） | AgentChat |
| 大文本任务外包（省 token） | `AgentChat/scripts/offload.py` | AgentChat |
| 会话自动清理 | `AgentChat/scripts/cleanup_yuanbao.py` | AgentChat |

### 相关目录
- `AgentChat/` — ziwang-Physics/AgentChat（547★，深度定制：元宝/豆包 adapter、外包、清理）
- `doubao2api/` — wangchuxiaoji-oss/doubao2api（豆包逆向 OpenAI API，识图 4 连修）
- `scripts/` — start_doubao2api.ps1 / offload.py / cleanup_yuanbao.py 等

## 已安装技能（20+）

### 💰 金融（10个 — finance-pack 插件包）
`mx-finance-data` · `akshare-stock` · `stock-price-query` · `stock-market-pro` ·
`stock-monitor-pro` · `stock-watcher` · `valuation-analysis` ·
`fund-analyzer` · `fund-news-daily` · `fund-invest-advisor`

### 🖼️ 图像处理（新增）
`ocr-vision`（本地 OCR） · `agentchat-web`（免费 AI 全家桶 playbook）

### 📄 文档处理
`docx` · `pdf` · `pptx` · `xlsx`

### 🛠️ 开发工具
`mcp-builder` · `skill-creator` · `webapp-testing` · `skill-assistant-pro`

### 🌐 其他
`aihot` · `dailyhot-skill` · `weather` · `codebase-design` · `diagnosing-bugs` ·
`domain-modeling` · `grilling` · `handoff` · `tdd` · `to-spec` · 等

## MCP 服务

| 服务 | 用途 |
|:--|:--|
| `mcp-server-time` | 多时区时间获取/转换 |
| `mcp-server-fetch` | 网页内容抓取（新闻/公告） |
| `mcp-server-git` | Git 版本控制 |
| `mcp-server-playwright` | 浏览器自动化（导航/截图/点击） |
| `vibe-trading`（HTTP 8900） | 54 个金融量化工具（`start_vibe_trading.ps1` 启动） |

## 关键记忆（13+ 条）

- `agentchat-skill-setup` — 国内 AI 全家桶安装/工具选择策略（AI 自主判断）
- `image-workflow-preferences` — 看图/生图工作流（本地 OCR + 豆包/元宝，不用 Agnes）
- `agnes-api-complete` — Agnes API 指南（视觉/生图已弃用）
- `user-stock-fund-repository` — 用户当前持仓（2026-07-31）
- `em-api-key-eastmoney` — 东方财富 API Key
- `git-github-setup` — Git 配置 + 半自动提交推送工作流
- `skills-first-workflow` — 先查技能再动手
- `new-skill-install-flow` — 新技能必须走 skill-assistant-pro 质检

## Git 工作流

Reasonix 半自动模式：完成有意义变更后主动询问 → 用户确认后 `add → commit → push`。
涉及 memory/ 的修改默认只提交不推送。
