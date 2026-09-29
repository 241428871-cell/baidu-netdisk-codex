"""Local stdio bridge to Baidu Netdisk's official SSE MCP server."""

from __future__ import annotations

import asyncio
import os
import sys
from urllib.parse import quote

import keyring
from mcp.client.sse import sse_client
from mcp import ClientSession
from mcp.server import Server
from mcp.server.stdio import stdio_server


SERVICE = "codex-baidu-netdisk-mcp"
SERVER = Server("baidu-netdisk-codex")


def official_url() -> str:
    token = os.environ.get("BAIDU_NETDISK_ACCESS_TOKEN") or keyring.get_password(
        SERVICE, "access_token"
    )
    if not token:
        raise RuntimeError(
            "Baidu Netdisk authorization is missing. Run "
            "'python scripts/bootstrap.py auth' locally."
        )
    return "https://mcp-pan.baidu.com/sse?access_token=" + quote(token, safe="")


@SERVER.list_tools()
async def list_tools():
    try:
        async with sse_client(
            official_url(), timeout=20, sse_read_timeout=90
        ) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                result = await session.list_tools()
                return result.tools
    except Exception as exc:
        raise RuntimeError(f"Baidu MCP tool discovery failed: {type(exc).__name__}") from None


@SERVER.call_tool()
async def call_tool(name, arguments):
    try:
        async with sse_client(
            official_url(), timeout=20, sse_read_timeout=90
        ) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                return await session.call_tool(name, arguments or {})
    except Exception as exc:
        raise RuntimeError(f"Baidu MCP tool call failed: {type(exc).__name__}") from None


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await SERVER.run(
            read_stream,
            write_stream,
            SERVER.create_initialization_options(),
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        # Never print an exception string or URL: Baidu's SSE URL contains the token.
        print(f"Baidu bridge stopped: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(1)
