# Roadmap

Last updated: 2026-10-24

**Legend:** 🟢 Complete with evidence · 🟡 Partial/in progress · 🔴 Not implemented.
The full intended scope remains status, materials, verified file handoff, print
controls, and camera access. This session implements the first read tools.

| Milestone | Status | Evidence / remaining work |
| --- | --- | --- |
| Repository and project documentation | 🟢 Complete | Dedicated checkout, operating rules, tested onboarding, evidence and ignores. |
| Scope and implementation design | 🟡 Partial | Owner directed Python/stdio read milestone; future transaction/camera choices remain proposed. |
| U1 protocol/firmware capability inventory | 🟡 Partial | Three live read tools on one firmware. Native camera TLS MQTT path has static evidence; installed camera wire behavior and advanced RPC remain unverified. |
| Targeted REA investigation | 🟡 Partial | Isolated CLI/MCP, focused GUI excerpts and seven native functions inspected through Rizin. Camera server ownership/expiry and firmware compatibility remain unresolved; no whole-app reconstruction. |
| MCP runtime/local configuration | 🟢 Read milestone complete | Real stdio tests pass; registered command called all three tools on hardware. A discovered capability tool subsequently succeeded in this chat. |
| Status/progress/errors/material tools | 🟢 Read milestone complete | Typed four-tool/mapping/feed/temperature/progress reads, simulated failures, live three-tool calls. Active hardware fault semantics need observation. |
| G-code validation/verified uploads | 🔴 Not implemented | Consumption/path/hash mismatch checks and verified handoff are later work. |
| Print start/controls | 🔴 Not implemented | Authorization, state checks, receipts, serialization and uncertain/repeated/restart reconciliation remain. |
| Camera snapshots/live sessions | 🟡 Investigation only | Native TLS MQTT, authentication layers, dropped camera `clientid` and 300-second GUI policy documented. Server expiry/ownership, image freshness and safe close unverified; no camera tools. |
| Automated/hardware verification | 🟡 Read milestone verified | 59 tests on Python 3.11/3.13, lint/build/review, actual live MCP reads. Future transaction/camera tests and physical acceptance remain. |
| Full release/operator handoff | 🔴 Not released | `0.1.0.dev0` is read-only development software; full scope remains. |

See [state](PROJECT_STATE.md) for blockers, [decisions](DECISIONS.md) for durable
choices and [design](docs/superpowers/specs/2026-10-24-snapmaker-u1-mcp-design.md)
for detailed contracts. Historical observations never authorize a mutation.
