"""
元宝 (Tencent Yuanbao) 看图脚本 — 国内直连多模态，无需 Clash。

原理：把图片放入系统剪贴板 → CDP 聚焦元宝 Quill 输入框 → Ctrl+V 粘贴 → 输入 prompt → 发送 → 提取响应。

用法（在 AgentChat 仓库根目录运行）：
    python agentchat/yuanbao_vision.py <图片路径> ["问题"]

依赖：playwright + 已登录元宝的 Chrome daemon（9222）。
"""
import sys, os, time, subprocess

def _copy_windows(image_path: str) -> bool:
    ps = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$i = [System.Drawing.Image]::FromFile('{image_path}')
[System.Windows.Forms.Clipboard]::SetImage($i)
$i.Dispose()
"""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           capture_output=True, timeout=10)
        return r.returncode == 0
    except Exception:
        return False

def yuanbao_ask_with_image(image_path: str, prompt: str = "请描述这张图片的内容", cdp_port: int = 9222, wait_s: int = 25):
    from playwright.sync_api import sync_playwright

    image_path = os.path.abspath(image_path)
    if not os.path.isfile(image_path):
        print(f"Image not found: {image_path}")
        return None
    if not _copy_windows(image_path):
        print("Failed to copy image to clipboard")
        return None

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{cdp_port}")
        page = None
        for ctx in b.contexts:
            for pg in ctx.pages:
                if "yuanbao" in pg.url:
                    page = pg; break
            if page: break
        if not page:
            page = b.contexts[0].new_page()
            page.goto("https://yuanbao.tencent.com/chat", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)

        page.goto("https://yuanbao.tencent.com/chat", wait_until="domcontentloaded")
        time.sleep(4)
        editor = page.locator(".ql-editor").first
        editor.click()
        time.sleep(0.5)
        page.keyboard.press("Control+v")
        time.sleep(2.5)
        # 输入文本（用 type 触发真实键盘事件，Angular 状态才更新）
        page.keyboard.type(prompt, delay=20)
        time.sleep(0.5)
        page.locator('a[aria-label="发送"]').first.click()
        time.sleep(wait_s)
        resp = page.evaluate("""() => {
            const els = document.querySelectorAll('.agent-chat__speech-text');
            const last = els[els.length - 1];
            return last ? last.innerText.trim() : '';
        }""")
        b.close()
        return resp or "(no response)"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    img = sys.argv[1]
    q = sys.argv[2] if len(sys.argv) > 2 else "请描述这张图片的内容"
    text = yuanbao_ask_with_image(img, q)
    print(text)
