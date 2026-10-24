"""Exercise the actual stdio MCP server; no printer mutations or raw responses."""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def check() -> None:
    env = {k: v for k, v in os.environ.items() if k.startswith("U1_")}
    params = StdioServerParameters(command=sys.executable, args=["-m", "snapmaker_u1_mcp"], env=env)
    async with asyncio.timeout(90), stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            names = [t.name for t in tools]
            expected = ["u1_capabilities", "u1_status", "u1_materials"]
            if sorted(names) != sorted(expected):
                raise RuntimeError("Unexpected MCP tool inventory")
            results = {}
            for name in expected:
                response = await session.call_tool(name, {})
                data = response.structuredContent
                if not data or response.isError:
                    raise RuntimeError(
                        "A read tool failed; inspect local setup and printer availability"
                    )
                results[name] = data
            print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        asyncio.run(check())
    except Exception:
        print(
            "MCP connection check failed; inspect local setup and printer availability.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
