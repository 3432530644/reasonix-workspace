"""
任务外包脚本 — 把大文本任务发给国内免费 AI（元宝/豆包/Kimi）处理，省主模型 token。

为什么用：主模型上下文宝贵。长文本（翻译/总结/改写/提取）经本脚本直送免费网页 AI，
结果作为工具输出返回，大文本不进主模型上下文。

用法：
    python scripts/offload.py <文件路径> "<处理指令>" [--provider yuanbao|doubao|kimi] [--keep N]
    python scripts/offload.py -t "<直接文本>" "<处理指令>" [--provider yuanbao] [--keep N]

示例：
    python scripts/offload.py 报告.txt "用100字总结以下内容"
    python scripts/offload.py -t "原文..." "翻译成英文"
    python scripts/offload.py 文章.md "提取关键要点，分点列出" --provider kimi

原理：读文件/文本 → 拼成 prompt 经 stdin 发给 AgentChat-OneWeb（--from 指定 provider）
→ 打印 AI 回复。默认走元宝（主力）。
"""
import sys, os, subprocess, argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(REPO, "skills", "AgentChat-OneWeb", "index.js")

def main():
    ap = argparse.ArgumentParser(description="外包大文本任务给国内免费 AI")
    ap.add_argument("path", nargs="?", help="文件路径（或配合 -t 省略）")
    ap.add_argument("instruction", nargs="?", default="请处理以下内容", help="处理指令")
    ap.add_argument("-t", "--text", help="直接传文本（替代文件）")
    ap.add_argument("--provider", default="yuanbao", choices=["yuanbao", "doubao", "kimi"])
    ap.add_argument("--keep", type=int, default=0, help="清理会话时保留个数")
    args = ap.parse_args()

    if args.text:
        content = args.text
    elif args.path and os.path.isfile(args.path):
        with open(args.path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    else:
        print("需要提供文件路径或 -t 文本")
        sys.exit(2)

    prompt = f"{args.instruction}\n\n{content}"

    # 经 stdin 传给 OneWeb（长文本不经过命令行参数，规避长度限制）
    import subprocess
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(
        ["node", INDEX, f"--from={args.provider}", "--single"],
        input=prompt, capture_output=True, text=True, encoding="utf-8",
        env=env, timeout=600,
    )
    # 输出 AI 回复（去除 receipt 行由调用方决定）
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.stderr.strip():
        sys.stderr.write(r.stderr.strip() + "\n")

    # 清理会话（默认清理，保持侧边栏干净）
    try:
        cleanup = os.path.join(REPO, "scripts", "cleanup_yuanbao.py")
        if args.provider == "yuanbao" and os.path.isfile(cleanup):
            subprocess.run(["python", cleanup, "--keep", str(args.keep)],
                           capture_output=True, timeout=180)
    except Exception:
        pass

if __name__ == "__main__":
    main()
