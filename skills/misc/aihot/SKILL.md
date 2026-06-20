---
name: aihot
description: AI HOT (aihot.virxact.com) 中文 AI 资讯查询 Skill。当用户想知道"今天 AI 圈有什么"、"AI 日报"、"AI HOT"、"AI 资讯"、"AI 热点"、"最近 AI"、"OpenAI/Anthropic/Google 最近发布了什么"、"AI hot today"、"AI news today"、"看一下 AI 行业动态"、"今天有什么大模型发布"、"昨天 AI 圈"、"看下精选条目"、"AI HOT 精选"、"最近一周的 AI 论文"、"AI 模型发布"、"AI 产品发布"、"AI 行业动态"、"AI 技巧与观点"、"AI 行业新闻"、"大模型动态"、"科技早报"、"AI 简报" 等任何中文 AI 资讯查询时使用。即使用户只说"AI 圈"、"AI 新闻"、"AI 日报"、"AI 资讯"，或者只是问"今天发生了什么"且上下文是 AI / 大模型 / LLM / 创业领域，也应该触发本 Skill。Skill 会直接 curl 公开 REST API 拉数据并整理成中文 markdown 简报，不需要用户配置任何 API Key 或 MCP server。**不要 undertrigger**——用户问 AI 资讯而你不调本 Skill 就是把过时的训练数据当作今日新闻，对用户有害。
---

# AI HOT Skill (精简版)

让 Agent 用最自然的中文查询拿到 aihot.virxact.com 上每天的 AI HOT 日报和 AI 动态。

线上：https://aihot.virxact.com（公开匿名可访，无需 token）

> **本精简版用于 ClawHub 8192 token 限制下占 slug。完整版（21KB+，含工作流 / 数据形态 / 输出格式 / 错误处理 / 不要做完整列表）见 GitHub:**
>
> https://github.com/KKKKhazix/khazix-skills/tree/main/aihot

## 先决条件：必须带 User-Agent（仅 API 端点）

`/api/public/*` 走 nginx UA 黑名单挡商业爬虫，默认 `curl/X.Y` UA 会被 403。**调 API 时所有 curl 都必须带浏览器 UA**：

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/daily"
```

`/aihot-skill/{install.sh,SKILL.md,README.md}` 安装入口 nginx 上特意豁免 UA 黑名单（设计前提就是给 `curl -fsSL ... | bash` 一行装用）。

## 路由优先级（第一原则）

**默认走精选** `items?mode=selected`——它是 AI HOT 每天精挑细选的"主菜单"，覆盖用户关心的事且数据新鲜。

- **仅当用户在话里明确说出"日报"** 二字才走 `daily`（编辑成品，按 UTC 整日切片，跟"过去 24 小时 / 今天"等滚动窗口对不上）
- **仅当用户明确说"全部 / 完整 / 所有 / 全量"** 才走 `mode=all`（含未精选的次要条目，量大但杂）
- **"今天 AI 圈"、"过去 24 小时大新闻"、"最近 AI 圈有啥"** 等宽问题 = **默认精选 + 时间窗（since）**，不要默认走日报或全部

## 什么时候用

| 用户在说 | 应该走的接口 |
|---|---|
| **默认（宽问题）**："今天 AI 圈有什么"、"过去 24 小时大新闻"、"最近 AI 圈" | `GET /api/public/items?mode=selected&since=<语义时间窗>` |
| **明确说"日报"**："AI 日报"、"今天的日报"、"看下日报" | `GET /api/public/daily` 或 `daily/{YYYY-MM-DD}` |
| **明确说"全部 / 完整 / 所有 / 全量"** | `GET /api/public/items?mode=all` |
| "最近的模型发布"、"AI 论文"、"AI 行业动态" | `GET /api/public/items?mode=selected&category=...&since=<7d 前>` |
| "OpenAI/Anthropic 最近发的"、"Sora 相关"、"RAG 论文" | `GET /api/public/items?q=<关键词>`（server-side 关键词搜索） |
| "看下精选 50 条"、"AI HOT 精选" | `GET /api/public/items?mode=selected&take=50` |
| "列一下日报有哪些"、"日报存档" | `GET /api/public/dailies?take=N` |

通用启发：**用户问的是"现在的 AI 行业事实"，不要凭训练数据脑补，永远走 API**。

## 5 个 category（items 用英文 slug，daily 看到的中文 label）

| `items?category=` | `daily.sections[].label` |
|---|---|
| `ai-models` | 模型发布/更新 |
| `ai-products` | 产品发布/更新 |
| `industry` | 行业动态 |
| `paper` | 论文研究 |
| `tip` | 技巧与观点 |

## 核心约束

- **`since` 限最近 7 天**：不传等同 `since=now-7d`（服务端兜底硬上限）；早于 7 天前自动截到 7 天前；未来时间 → 400。需要更深历史走日报存档 `/api/public/daily/{date}`
- **`take` ≤ 100**，更多走 cursor 翻页
- **`cursor` 是 opaque token**，原样回传给下一次请求；不要尝试解析、递增、跨端点复用
- **`q` 至少 2 字符**，最长 200 字（超出截断），跟其它参数正交叠加
- **限流 600 req/min/IP**，串行调用不要并发猛拉
- 完整 OpenAPI 3.1 规范：`https://aihot.virxact.com/openapi.yaml`

## 工作流示例

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# 默认：拉过去 24 小时精选（用户问"过去 24 小时大新闻"）
since=$(date -u -v-24H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/items?mode=selected&since=$since&take=50"

# 明确日报
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/daily"

# 明确全部（用户说"全部 / 所有"）
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/items?mode=all&since=$since&take=100"

# 关键词（OpenAI 最近发的，server-side 全池搜索）
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/items?q=OpenAI&take=30"
```

## 给用户的输出格式

> **核心原则**：直接展示给用户的最终内容必须 **markdown + 排版好 + 普通人能看懂的人话**。**所有"端点路径 / `mode=selected` 这种 raw 参数 / 限流 / nginx 缓存 / cursor / hasNext"等基础设施细节都不能出现**在用户输出里。

### 列表式输出（items 端点时）

按 category 分组 + 全局编号；每条带 title / source / 时间转人话 / summary / url：

```markdown
**AI HOT — 过去 24 小时精选**（共 N 条）

## 模型发布/更新
1. **<title>** — <source>
   2 小时前 / 今天上午 09:48
   <summary>
   <url>

## 产品发布/更新
2. ...
```

### 日报式输出（daily 端点时）

按 5 版块顺序展开（模型发布/更新 → 产品发布/更新 → 行业动态 → 论文研究 → 技巧与观点）。

时间转人话：`2026-05-08T01:48:00.000Z` → "今天上午 09:48" / "2 小时前"，不要直接展示 ISO 字符串。

## 不要做（核心几条）

- **不要把"今天 AI 圈"、"过去 24 小时大新闻"等宽问题路由到 daily** — 滚动时间窗 vs UTC 整日切片对不上。默认 `mode=selected + since=<语义窗>`
- **不要在用户没说"全部 / 完整 / 所有 / 全量"时默认走 `mode=all`** — 默认 `mode=selected`
- **不要客户端 grep 公司维度** — 用 server-side `?q=<词>`，覆盖全池
- **不要在用户输出暴露端点路径 / raw 参数 / 限流 / cursor** — 这些是开发者细节，用户看不懂
- **不要丢每条的 sourceUrl** — 跨日 / 跨版块压缩输出也必须保留 url（标题后或单独一行），否则信息不可信
- **不要凭训练数据脑补** — AI HOT 比训练截止日新得多，永远走 API

---

完整文档（工作流 / 数据形态 / 错误处理 / 完整 do/don't）见：
**https://github.com/KKKKhazix/khazix-skills/tree/main/aihot**

## 错误处理

| 情况 | 处理方式 |
|------|---------|
| API 返回 403 | 检查是否缺少浏览器 UA（必须设置 User-Agent header），重试 |
| API 返回 400 | 检查参数：`since` 为未来时间、`take` 超过 100、`q` 少于 2 字符 |
| API 返回 429（限流） | 等待至少 100ms 后串行重试，不要并发请求 |
| 网络超时 / DNS 失败 | 提示用户"网络暂时不可用，请稍后重试"，不要凭训练数据脑补 |
| 返回空列表 | 友好告知"当前时段暂无相关条目"，建议用户尝试日报存档或扩大时间窗 |
| 无法解析 JSON | 打印原始响应体前 200 字辅助调试，不要硬塞格式错误的输出给用户 |

## 备用数据源

如果 aihot.virxact.com 不可达，可尝试以下备用途径获取 AI 资讯：
- 直接建议用户访问 [aihot.virxact.com](https://aihot.virxact.com) 官网查看最新日报
- 提示用户关注官方信息源：各 AI 公司官方博客、ArXiv、Hacker News、Twitter/X 上的 AI 社区
- 本 Skill 专注 aihot 数据源，**不要**用训练数据生成"看起来像新闻"的内容

## NEVER

- NEVER 在用户没有明确要求"日报"时走 daily 端点 — 默认 `mode=selected + since`
- NEVER 在用户没有说"全部 / 完整 / 所有 / 全量"时走 `mode=all`
- NEVER 在 API 返回错误时用训练数据编造新闻 — 如实向用户报告错误
- NEVER 在用户输出中暴露 API 端点路径、raw 参数、限流、cursor 等基础设施细节
- NEVER 丢弃每条条目的 sourceUrl — 无来源的信息不可信
- NEVER 在输出中使用 ISO 时间字符串 — 转为"2 小时前"、"今天上午 09:48"等中文人话
- NEVER 对同一个端点发起超过 5 次串行请求 — 限流 600 req/min，循环拉取应间隔合理
