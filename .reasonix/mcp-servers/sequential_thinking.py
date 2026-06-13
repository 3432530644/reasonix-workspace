"""
Sequential Thinking MCP Server
基于 mcp Python SDK 实现的多步推理工具
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import json
import uuid
from datetime import datetime
from typing import Any

server = Server("sequential-thinking")

# 存储推理会话
sessions: dict[str, dict[str, Any]] = {}

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="sequential_thinking",
            description="多步推理工具：将复杂问题（如股票分析、行业趋势、投资决策等）分解为逐步推理，支持分支探索和回溯",
            inputSchema={
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "当前推理步骤的内容"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "推理会话ID，留空则创建新会话"
                    },
                    "next_thought_needed": {
                        "type": "boolean",
                        "description": "是否需要继续推理"
                    },
                    "branch_from": {
                        "type": "string",
                        "description": "从某个步骤分支出去，格式: 'step_N'"
                    },
                    "branch_label": {
                        "type": "string",
                        "description": "分支标签名，用于区分不同推理方向"
                    }
                },
                "required": ["thought", "next_thought_needed"]
            }
        ),
        Tool(
            name="sequential_thinking_reset",
            description="重置推理会话，清空历史记录",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "要重置的会话ID"
                    }
                },
                "required": ["session_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "sequential_thinking":
        thought = arguments.get("thought", "")
        session_id = arguments.get("session_id", str(uuid.uuid4()))
        next_thought_needed = arguments.get("next_thought_needed", True)
        branch_from = arguments.get("branch_from")
        branch_label = arguments.get("branch_label")

        if session_id not in sessions:
            sessions[session_id] = {
                "id": session_id,
                "created_at": datetime.now().isoformat(),
                "thoughts": [],
                "branches": {}
            }

        session = sessions[session_id]
        step_number = len(session["thoughts"]) + 1
        step_id = f"step_{step_number}"

        thought_entry = {
            "step": step_number,
            "step_id": step_id,
            "thought": thought,
            "branch_from": branch_from,
            "branch_label": branch_label,
            "timestamp": datetime.now().isoformat()
        }

        session["thoughts"].append(thought_entry)

        result = {
            "session_id": session_id,
            "step": step_number,
            "step_id": step_id,
            "total_steps": step_number,
            "next_thought_needed": next_thought_needed,
            "thought_history": [
                {
                    "step": t["step"],
                    "step_id": t["step_id"],
                    "thought": t["thought"],
                    "branch_label": t.get("branch_label")
                }
                for t in session["thoughts"]
            ]
        }

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    elif name == "sequential_thinking_reset":
        session_id = arguments.get("session_id", "")
        if session_id in sessions:
            del sessions[session_id]
            return [TextContent(type="text", text=json.dumps({"status": "reset", "session_id": session_id}, ensure_ascii=False))]
        else:
            return [TextContent(type="text", text=json.dumps({"status": "not_found", "session_id": session_id}, ensure_ascii=False))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
