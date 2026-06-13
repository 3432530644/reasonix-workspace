"""SQLite MCP Server 启动脚本"""
from mcp_server_sqlite import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
