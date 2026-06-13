"""
Playwright MCP Server - 浏览器自动化工具
基于 mcp Python SDK + Playwright
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, ImageContent
import json
import base64
from typing import Optional
from playwright.async_api import async_playwright

server = Server("playwright")
browser = None
page = None

async def get_page():
    global browser, page
    if page is None:
        p = await async_playwright().__aenter__()
        browser = await p.chromium.launch(headless=True, channel="chrome")
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
    return page

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="browser_navigate",
            description="导航到指定 URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "要访问的网页 URL"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="browser_screenshot",
            description="对当前页面截图，返回 Base64 编码的 PNG 图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "full_page": {
                        "type": "boolean",
                        "description": "是否截取整页（含滚动部分）",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="browser_click",
            description="点击页面上的元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS 选择器，如 '#id'、'.class'、'button'"}
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="browser_fill",
            description="在输入框中填入文本",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS 选择器"},
                    "text": {"type": "string", "description": "要填入的文本"}
                },
                "required": ["selector", "text"]
            }
        ),
        Tool(
            name="browser_get_text",
            description="获取页面上的文本内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS 选择器，不传则获取 body 文本",
                        "default": "body"
                    }
                }
            }
        ),
        Tool(
            name="browser_evaluate",
            description="在页面中执行 JavaScript 并返回结果",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "要执行的 JavaScript 代码"}
                },
                "required": ["script"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent]:
    p = await get_page()

    if name == "browser_navigate":
        url = arguments["url"]
        await p.goto(url, wait_until="domcontentloaded", timeout=30000)
        title = await p.title()
        return [TextContent(type="text", text=json.dumps({
            "title": title,
            "url": p.url,
            "status": "loaded"
        }, ensure_ascii=False))]

    elif name == "browser_screenshot":
        full_page = arguments.get("full_page", False)
        screenshot = await p.screenshot(full_page=full_page)
        b64 = base64.b64encode(screenshot).decode()
        return [ImageContent(type="image", data=b64, mimeType="image/png")]

    elif name == "browser_click":
        selector = arguments["selector"]
        await p.click(selector)
        return [TextContent(type="text", text=json.dumps({"clicked": selector}, ensure_ascii=False))]

    elif name == "browser_fill":
        selector = arguments["selector"]
        text = arguments["text"]
        await p.fill(selector, text)
        return [TextContent(type="text", text=json.dumps({"filled": selector}, ensure_ascii=False))]

    elif name == "browser_get_text":
        selector = arguments.get("selector", "body")
        text = await p.inner_text(selector)
        return [TextContent(type="text", text=text)]

    elif name == "browser_evaluate":
        script = arguments["script"]
        result = await p.evaluate(script)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
