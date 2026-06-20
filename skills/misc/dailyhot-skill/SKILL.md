---
name: dailyhot-skill
description: 聚合热榜查询 — 从 56+ 中文平台获取今日热点数据，支持按关键词筛选和跨平台汇总。用户说"热点/热搜/热榜/今天流行什么/看看热点"时触发。
when_to_use: "热榜, 热搜, 热点, 今日热榜, 今日热搜, trending, hot search, hot topics, what's popular, 看看热点, 有什么热点, 最近的热点, AI热点, 科技热点, 热点汇总, 帮我汇总热点, 今天大家都在关注什么, 今天流行什么, 今天有什么新闻, 最新资讯, 看看热榜, 看看热搜, 帮我看看今天的热搜"
argument-hint: "[platform] [--limit N]"
arguments: [platform, options]
allowed-tools: Bash(node scripts/query-hot.mjs *) Bash(node scripts/start-server.mjs *) Bash(npm install *)
---

# DailyHot Skill

查询今日热榜数据，支持 56+ 中文内容平台。

## 智能响应规则

按以下优先级自动判断响应方式：

1. **指定平台**（"看看微博热搜"）→ 直接查询该平台热榜
2. **指定主题 + 要求汇总**（"看AI相关的热点，并帮我汇总"）→ 并行查询科技相关平台（36kr, ithome, sspai, zhihu, bilibili），按关键词筛选后合并为一份报告
3. **要求汇总但未指定主题**（"帮我汇总今日热点"）→ 并行查询 5 个头部平台（zhihu, weibo, bilibili, douyin, baidu），输出综合热榜
4. **模糊请求**（"看看热点"、"今天流行什么"）→ 推荐 3-5 个常用平台，引导用户选择
5. **列出所有平台**（"有哪些平台"）→ 执行 `--all` 命令

## 科技/AI 主题查询

用户要求科技、AI、互联网相关热点时，并行查询以下平台：

```bash
node scripts/query-hot.mjs 36kr --limit 10 &
node scripts/query-hot.mjs ithome --limit 10 &
node scripts/query-hot.mjs zhihu --limit 10 &
node scripts/query-hot.mjs sspai --limit 10 &
node scripts/query-hot.mjs bilibili --limit 10 &
wait
```

查询完成后，按关键词（AI、科技、互联网等）筛选相关条目，合并为一份汇总报告。

## 综合热榜查询

用户要求"综合热点"、"全网热点"、"汇总"时，并行查询以下 5 个头部平台：

```bash
node scripts/query-hot.mjs zhihu --limit 5 &
node scripts/query-hot.mjs weibo --limit 5 &
node scripts/query-hot.mjs bilibili --limit 5 &
node scripts/query-hot.mjs douyin --limit 5 &
node scripts/query-hot.mjs baidu --limit 5 &
wait
```

按平台分组输出，每个平台 Top 5。

## 输出格式

每条热榜数据按如下格式展示：

```
🔥 {platform_name} · Top {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━
 1. {title}          🔥 {heat_value}
    {description_truncated}  |  👤 {author}
 2. {title}          🔥 {heat_value}
...
📡 更新时间：{time}  |  总条数：{count}
```

- 标题为必选项
- 描述截断至 120 字
- 热度值格式化为 万/亿
- 作者信息可选展示

## 快速用法

```bash
# 查询指定平台（默认 10 条）
node scripts/query-hot.mjs <platform>

# 自定义条数
node scripts/query-hot.mjs <platform> --limit 20
```

## 常用平台速查表

### 综合新闻
| 平台 | 命令 | 说明 |
|------|------|------|
| 知乎 | `zhihu` | 知乎热榜 |
| 微博 | `weibo` | 微博热搜 |
| 百度 | `baidu` | 百度热搜 |
| 抖音 | `douyin` | 抖音热搜 |
| 快手 | `kuaishou` | 快手热榜 |
| 今日头条 | `toutiao` | 头条热榜 |

### 科技/互联网
| 平台 | 命令 | 说明 |
|------|------|------|
| B站 | `bilibili` | B站热门视频 |
| 36氪 | `36kr` | 科技商业资讯 |
| 少数派 | `sspai` | 数字生活 |
| IT之家 | `ithome` | 科技新闻 |
| CSDN | `csdn` | 开发者社区 |
| 掘金 | `juejin` | 技术社区 |
| V2EX | `v2ex` | 程序员社区 |
| GitHub | `github` | GitHub Trending |

### 媒体/社区
| 平台 | 命令 | 说明 |
|------|------|------|
| 虎嗅 | `huxiu` | 商业评论 |
| 澎湃新闻 | `thepaper` | 时政新闻 |
| 果壳 | `guokr` | 科普热点 |
| 爱范儿 | `ifanr` | 科技媒体 |
| 豆瓣 | `douban` | 豆瓣热议 |
| 虎扑 | `hupu` | 体育/游戏社区 |
| 贴吧 | `tieba` | 百度贴吧 |
| NGA | `ngabbs` | 游戏论坛 |

### 其他
| 平台 | 命令 | 说明 |
|------|------|------|
| 微信读书 | `weread` | 热门书籍 |
| 地震速报 | `地震` | 最新地震信息 |
| 历史上的今天 | `历史上的今天` | 历史事件 |

## 首次使用

首次查询前确认 API 服务是否运行：

```bash
node scripts/query-hot.mjs zhihu
```

如果连接失败（报错"无法连接到 DailyHot 服务"），先启动服务：

```bash
node scripts/start-server.mjs
```

服务启动后等待 3-5 秒再执行查询。服务常驻后台，后续查询无需重启。

## 列出所有可用平台

```bash
node scripts/query-hot.mjs --all
```

## 错误处理

| 情况 | 处理 |
|------|------|
| 服务未启动 | 自动启动 `node scripts/start-server.mjs`，等待 3-5 秒后重试 |
| 平台不存在 | 展示可用平台列表，提示用户选择 |
| API 超时 | 重试 1 次，仍失败则告知用户稍后重试 |
| 并行查询部分失败 | 成功平台正常展示，失败平台标注"暂不可用" |
| 无结果返回 | 告知用户"该平台暂无热点数据" |

## 注意事项

- 默认显示 10 条，除非用户指定 `--limit`
- 运行查询前先确认服务是否启动
- API 服务默认监听 `localhost:6688`，可通过 `DAILYHOT_URL` 环境变量覆盖
- 底层数据有 **60 分钟缓存**，短时间内重复查询会返回相同数据
- 用户同时查询 **3 个以上平台**时，**必须使用并行查询**（`&` + `wait`），避免串行等待
- 本技能有一个配套 API 后端服务支持，首次使用需要启动服务

## NEVER

- NEVER 编造或虚构热点数据 —— 数据必须来自 DailyHot API 返回
- NEVER 修改热点标题、排名顺序或热度值
- NEVER 用旧日期的数据当作今日热点展示
- NEVER 同步查询超过 2 个平台 —— 3 个以上必须并行
- NEVER 暴露 API 端口、服务地址等基础设施细节给用户
- NEVER 在服务未启动时返回空数据 —— 先尝试启动服务
