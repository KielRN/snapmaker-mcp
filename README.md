# Snapmaker U1 MCP

A local Python/stdio MCP bridge for a Snapmaker U1. Repository:
[KielRN/snapmaker-mcp](https://github.com/KielRN/snapmaker-mcp).

The first milestone implements `u1_capabilities`, `u1_status`, and `u1_materials`.
All three were called through a real MCP subprocess against the installed U1.
This is unreleased development software, `0.1.0.dev0`. Upload, print controls,
and camera tools are not implemented.

## Setup

Python 3.11+ and [uv](https://docs.astral.sh/uv/) are required for these commands.
They were exercised on Windows with Python 3.11.14 and 3.13.12. From this checkout:

```powershell
uv sync --locked --extra dev
New-Item -ItemType Directory -Force .local | Out-Null
Copy-Item config.example.json .local/config.json
```

Edit the ignored local JSON to set your trusted LAN printer origin. The example
uses a deliberately nonworking `.invalid` host. The origin must be HTTP(S), with
no credentials, path, query, or fragment. `U1_PRINTER_URL` can override the JSON
origin; `U1_API_KEY` optionally supplies the normal `X-Api-Key` header. Credentials
belong in a secret store/local environment, not in JSON examples or Git.

```powershell
$env:U1_CONFIG_FILE = (Resolve-Path .local/config.json).Path
uv run --locked --extra dev python tools/check_connection.py
```

This launches the actual stdio server, initializes MCP, checks its exact tool
inventory, calls all three read tools, and prints normalized JSON. It never starts
a print or camera session. A raw launch is:

```powershell
uv run --locked python -m snapmaker_u1_mcp
```

The raw launch waits for an MCP client on stdin; stdout is reserved for MCP.
Invalid setup exits with a fixed stderr message. SDK/HTTP diagnostic logging is
suppressed because it can echo private payloads; tool failures carry sanitized
error codes and guidance.

## Connect an MCP client

Configure stdio with this checkout's absolute `.venv` Python executable, arguments
`-m snapmaker_u1_mcp`, and `U1_CONFIG_FILE` pointing to the absolute ignored JSON.
The editable install makes the working directory immaterial. No endpoint or file
path can be supplied in tool arguments.

The local Codex entry `snapmaker_u1` was added. Its exact configured command/env
were used for successful MCP initialize/list/calls. Reload MCP or start a new
client session if the running chat has not discovered the new tools. Remove the
entry in Codex MCP settings when no longer wanted. Stop its clients before
removing this checkout's `.venv`; no printer cleanup/configuration is needed.

## Tools and interpretation

Call each tool with `{}`. Discovery includes typed output schemas.

| Tool | Result |
| --- | --- |
| `u1_capabilities` | Observed firmware/Moonraker identity, HTTP/object inventory, implemented/future tools, unresolved camera support. |
| `u1_status` | Klipper/print state, virtual SD, progress fraction (0–1), layers/duration, selected physical tool, four nozzle/bed temperatures in °C, numeric exceptions. |
| `u1_materials` | Four physical tools, T0–T3/API names, 32 logical mapping slots, job-use flags, RFID identity/color, feed/toolhead sensor evidence, loaded state. |

Results include the observation window, source event time when available,
outcome, errors, and data. `ok` means reported read fields were understood, not
that an action is safe. `partial` retains usable data and marks missing evidence
as null/unknown. `unavailable` covers failed reads, `rejected` includes error
objects on HTTP 200, and `unknown` covers unexpected normalization failures.
No cached success is returned after failure. Failed outcomes set MCP `isError`;
partial results do not.

Physical tools are one-based. `logical_to_physical[0]` is logical T0's one-based
physical tool. Unused mapping defaults do not imply material use; `used_by_job`
is the current physical job-use flag. Klipper ready can coexist with printing.
Idle requires an inactive print state, inactive virtual SD, ready Klipper, and
known clear exceptions. Separate HTTP requests are not atomic. Exception levels
2/3 are classified as blocking from pinned public source; active hardware fault
semantics remain untested. Raw messages, filenames, machine identity/paths, RFID
card UIDs, and camera credentials are omitted.

`loaded` requires an enabled positive toolhead sensor plus present/positive feed
module reporting completed loading without a feed error. An enabled negative
toolhead sensor gives `not_loaded`; missing, disabled, contradictory, or
transitional evidence gives `unknown`. RFID describes identity only. Sensor
reports do not establish physical inspection or suitability for a future job.

## Verification and recovery

```powershell
uv run --locked --extra dev pytest -q
uv run --locked --extra dev ruff check .
uv run --locked --extra dev ruff format --check .
uv build
```

The suite exercises the actual stdio process and a local HTTP simulator, including
mapping/feed failures, partial objects, HTTP-200 errors, authentication,
timeouts/disconnects, no stale success, malformed MCP input, redaction, redirects,
and oversized/compressed responses. Tests need neither a printer nor credentials.
No hardware-control tests have run.

Reads use fixed routes/objects, disable environment proxies/redirects, request
uncompressed data, reject other encodings, and cap raw bytes and total request
duration. Defaults are 256 KiB and five seconds per request. On failure, check
local config, normal authentication, printer availability and firmware, then
repeat the read. There are no automatic retries or printer mutations.

## Camera and remaining scope

REA 6.7.0/Node 24.22.1 are isolated under ignored tooling. The tested installer is
`powershell -File tools/setup_rea.ps1`; it changes neither global Node nor agent
registrations. Camera/lifecycle excerpts parsed, but full REA doctor readiness
and native decompilation remain unavailable. The [camera report](docs/research/2026-10-24-camera.md)
separates static findings from live evidence and identifies missing contracts.

Future controls must retain per-plate authorization and fresh human confirmation
of an installed, clear bed. Slicing stays in the separate OrcaSlicer integration.
This bridge introduces no firmware/calibration/configuration changes, cloud
dependence, or automatic product-order dispatch.

## Project documents

| Document | Purpose |
| --- | --- |
| [PROJECT_STATE.md](PROJECT_STATE.md) | Evidence, blockers, next actions. |
| [ROADMAP.md](ROADMAP.md) | Traffic-light milestones. |
| [DECISIONS.md](DECISIONS.md) | Confirmed choices and proposals. |
| [CHANGELOG.md](CHANGELOG.md) | Actual changes and release status. |
| [AGENTS.md](AGENTS.md) | Agent and printer operating rules. |
| [Design](docs/superpowers/specs/2026-10-24-snapmaker-u1-mcp-design.md) | Full scope and future safety contracts. |
| [Milestone plan](docs/superpowers/plans/2026-10-24-read-milestone.md) | Implementation record. |
| [Read evidence](docs/research/2026-10-24-read-contracts.md) | Live observations, pinned source, software checks. |
| [Camera report](docs/research/2026-10-24-camera.md) | Tooling, artifact identity, findings and gaps. |
