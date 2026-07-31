"""
元宝会话清理脚本 — 删除侧边栏聊天会话（避免积累）。

用法：
    python scripts/cleanup_yuanbao.py            # 删除全部会话
    python scripts/cleanup_yuanbao.py --keep 2   # 保留最新 2 个

流程（元宝实测 2026-08-01）：
    hover 会话项(.yb-recent-conv-list__item) → 点该项内 ...(icon-yb-ic_ellipsis)
    → 菜单点"删除"(.yb-dropdown__item 含文本"删除")
    → 确认弹窗点"确认删除"按钮

依赖：playwright + Chrome daemon(9222) + 元宝已登录。
"""
import sys, time

def cleanup(keep: int = 0, cdp_port: int = 9222, max_iter: int = 60):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{cdp_port}")
        page = None
        for ctx in b.contexts:
            for pg in ctx.pages:
                if "yuanbao" in pg.url:
                    page = pg; break
            if page: break
        if not page:
            print("NO_YUANBAO_TAB")
            b.close()
            return 0

        deleted = 0
        stuck = 0
        for _ in range(max_iter):
            items = page.locator(".yb-recent-conv-list__item")
            count = items.count()
            if count <= keep:
                break
            item = items.first
            try:
                item.hover(timeout=3000)
                time.sleep(0.5)
                # 点该项内的 ... 按钮（作用域限定，避免点到别的会话）
                ell = item.locator("[class*='ellipsis']").first
                ell.click(timeout=3000)
                time.sleep(0.6)
                del_item = page.locator(".yb-dropdown__item", has_text="删除").first
                del_item.click(timeout=3000)
                time.sleep(0.8)
                # 确认弹窗
                confirm = page.locator('button:has-text("确认删除")').first
                confirm.click(timeout=3000)
                time.sleep(1.2)
                deleted += 1
                stuck = 0
            except Exception:
                # 单项失败：关闭可能的菜单/弹窗后继续，卡死则退出防死循环
                try: page.keyboard.press("Escape")
                except Exception: pass
                time.sleep(0.6)
                stuck += 1
                if stuck >= 3:
                    break

        b.close()
        try:
            remain = page.locator(".yb-recent-conv-list__item").count()
        except Exception:
            remain = "?"
        print(f"DELETED {deleted} session(s), remaining {remain}")
        return deleted

if __name__ == "__main__":
    keep = 0
    if "--keep" in sys.argv:
        try: keep = int(sys.argv[sys.argv.index("--keep") + 1])
        except Exception: keep = 0
    cleanup(keep=keep)
