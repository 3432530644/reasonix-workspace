# Reasonix Git/GitHub 使用指南

> 记录于 2026-06-10，Git v2.54.0，Reasonix 工作区

---

## 1. 环境信息

| 项目 | 值 |
|------|-----|
| Git 版本 | v2.54.0 (MinGit) |
| 安装路径 | `C:\tools\Git` |
| 远程仓库 | `https://github.com/3432530644/reasonix-workspace.git` |
| 默认分支 | `main` |
| 用户 | 3432530644 |

## 2. 常用 Git 命令速查

```bash
# 查看当前状态
git status

# 暂存所有修改
git add .

# 提交
git commit -m "描述你改了什么"

# 推送到 GitHub
git push

# 拉取最新代码
git pull

# 查看提交历史
git log --oneline

# 查看变更内容
git diff
```

## 3. 日常流程（半自动）

Reasonix 检测到修改后会主动询问：

> **检测到变更，要提交并推送到 GitHub 吗？**
> - ✅ 提交推送
> - ⏸ 稍后再说
> - ❌ 跳过此变更

你也可以主动让我操作：
- *"帮我提交推送"*
- *"看看 Git 状态"*
- *"回退到上一个版本"*

## 4. 与 Reasonix 联动

安装了 `mcp-server-git`，重启 Reasonix 后可通过 Git MCP 工具操作 Git。

## 5. .gitignore 已排除内容

- OS 文件：`Thumbs.db`、`.DS_Store`、`*.swp`
- Python：`__pycache__/`、`*.pyc`
- Node：`node_modules/`
