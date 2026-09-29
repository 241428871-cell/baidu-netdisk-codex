"""Read-only connection check that never prints private file names or tokens."""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


BRIDGE = Path(__file__).with_name("bridge.py")


async def check() -> int:
    params = StdioServerParameters(command=sys.executable, args=[str(BRIDGE)])
    async with stdio_client(params) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            result = await session.list_tools()
            names = {tool.name for tool in result.tools}
            print(f"MCP connected; {len(names)} Baidu tools available.")
            if "file_list" not in names:
                print("Baidu did not expose file_list.", file=sys.stderr)
                return 1
            listing = await session.call_tool("file_list", {"dir": "/"})
            if listing.isError:
                print("Root directory read failed.", file=sys.stderr)
                return 1
            print("Read-only root directory check passed.")
            return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(asyncio.wait_for(check(), timeout=90)))
    except Exception as exc:
        # Remote errors can include an access-token URL; show type only.
        print(f"Connection check failed: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(1)
