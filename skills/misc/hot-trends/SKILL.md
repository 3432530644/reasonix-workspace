---
name: hot-trends
description: 获取微博热搜排行榜 — 打工人摸鱼必备
runAs: inline
---

获取当前北京时间，然后从以下地址抓取当天的微博热搜 JSON 数据：
https://raw.githubusercontent.com/justjavac/weibo-trending-hot-search/master/raw/{YYYY-MM-DD}.json

解析 JSON，提取前10条的 title 字段，展示给用户。失败则告知原因。
