"""Exactly three parameterless read tools over the official MCP stdio transport."""

import asyncio
import json
import logging
import sys

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from .adapter import U1Reader, now
from .config import Settings
from .models import Capabilities, Issue, Materials, Observation, Status
from .transport import Moonraker


def create_server(reader: U1Reader) -> Server:
    server = Server("snapmaker-u1", version="0.1.0.dev0")
    definitions = {
        "u1_capabilities": (
            reader.capabilities,
            Capabilities,
            "Observe firmware, read endpoints, object inventory, and unresolved camera support.",
        ),
        "u1_status": (
            reader.status,
            Status,
            "Read print state, progress, temperatures, selected physical tool, and exceptions.",
        ),
        "u1_materials": (
            reader.materials,
            Materials,
            "Read four physical tools, logical mapping, RFID identity and feed evidence.",
        ),
    }

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=name,
                description=description,
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
                outputSchema=Observation[schema].model_json_schema(),
                annotations=types.ToolAnnotations(
                    readOnlyHint=True,
                    destructiveHint=False,
                    idempotentHint=True,
                    openWorldHint=True,
                ),
            )
            for name, (_, schema, description) in definitions.items()
        ]

    # SDK validation errors include supplied keys/values. Reject arguments ourselves
    # using a fixed message to keep machine data and credentials out of MCP results.
    @server.call_tool(validate_input=False)
    async def call_tool(name: str, arguments: dict) -> types.CallToolResult:
        if name not in definitions or arguments:
            return types.CallToolResult(
                isError=True,
                content=[
                    types.TextContent(
                        type="text",
                        text="Only the three listed read tools with empty arguments are accepted.",
                    )
                ],
            )
        started = now()
        try:
            result = await definitions[name][0]()
        except Exception:
            # Untrusted peer shapes must never turn a traceback into an MCP response.
            result = Observation(
                outcome="unknown",
                observation_started_at=started,
                observed_at=now(),
                errors=[
                    Issue(
                        code="normalization_failed",
                        message="Unrecognized printer data; verify firmware compatibility.",
                    )
                ],
            )
        data = result.model_dump(mode="json")
        return types.CallToolResult(
            isError=result.outcome in {"unavailable", "rejected", "unknown"},
            content=[types.TextContent(type="text", text=json.dumps(data, allow_nan=False))],
            structuredContent=data,
        )

    return server


async def run(settings: Settings) -> None:
    async with Moonraker(settings) as client:
        server = create_server(U1Reader(client))
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())


def main() -> None:
    # The SDK and HTTP dependencies can log validation payloads and private URLs
    # before our handlers run. Only fixed bridge diagnostics below go to stderr.
    logging.disable(logging.CRITICAL)
    try:
        settings = Settings.from_env()
    except ValueError:
        print("Local U1 configuration is missing or invalid.", file=sys.stderr)
        raise SystemExit(1) from None
    try:
        asyncio.run(run(settings))
    except KeyboardInterrupt:
        pass
    except Exception:
        print("U1 MCP transport stopped unexpectedly; check local setup.", file=sys.stderr)
        raise SystemExit(1) from None
