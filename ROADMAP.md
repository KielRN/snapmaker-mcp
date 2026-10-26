# Roadmap

Last updated: 2026-10-25

**Legend:** 🟢 Complete with evidence · 🟡 Partial/in progress · 🔴 Not implemented.
The full intended scope remains status, materials, verified file handoff, print
controls, and camera access. File transactions now have simulator verification;
hardware acceptance and broad U1 profile compatibility remain pending.

| Milestone | Status | Evidence / remaining work |
| --- | --- | --- |
| Repository and project documentation | 🟢 Complete | Dedicated checkout, operating rules, tested onboarding, evidence and ignores. |
| Scope and implementation design | 🟡 Partial | Owner directed Python/stdio read milestone; future transaction/camera choices remain proposed. |
| U1 protocol/firmware capability inventory | 🟡 Partial | Three live read tools on one firmware. Native camera TLS MQTT path has static evidence; installed camera wire behavior and advanced RPC remain unverified. |
| Targeted REA investigation | 🟡 Partial | Isolated CLI/MCP, focused GUI excerpts and seven native functions inspected through Rizin. Camera server ownership/expiry and firmware compatibility remain unresolved; no whole-app reconstruction. |
| MCP runtime/local configuration | 🟢 Read milestone complete | Real stdio tests pass; registered command called all three tools on hardware. A discovered capability tool subsequently succeeded in this chat. |
| Status/progress/errors/material tools | 🟢 Read milestone complete | Typed four-tool/mapping/feed/temperature/progress reads, simulated failures, live three-tool calls. Active hardware fault semantics need observation. |
| G-code validation/verified uploads | 🟡 Software implemented, stock profiles blocked | Policy-7 receipts bind saved pause alongside head/coordinate/mesh/exclusion evidence; explicit false is required for idle. All eight normal exports rejected. Chain/effective mesh/provenance, actual trapq, saved K and hidden demand remain unknown. Macro/feed/end/camera/metadata contracts incomplete. Uploads disabled; hardware acceptance pending. |
| Print start/controls | 🔴 Not implemented | Saved-pause read and source pause/end/callback inventory exist. No job-parameter/start/control tools; saved restore state, callback effects, control acceptance and physical authorization checks remain. |
| Camera snapshots/live sessions | 🟡 Investigation only | Native TLS MQTT, authentication layers, dropped camera `clientid` and 300-second GUI policy documented. Server expiry/ownership, image freshness and safe close unverified; no camera tools. |
| Automated/hardware verification | 🟡 Software verified, hardware partial | 454 tests on Python 3.11/3.13 and lint/build with actual MCP/HTTP simulation; independent review and final scope/package audit passed. One historical fixed passive pause GET confirmed false; no new read during closeout. Upload/profile/control/camera hardware acceptance remains. |
| Full release/operator handoff | 🔴 Not released | `0.1.0.dev0` is development software with optional simulated-only uploads; full scope remains. |

See [state](PROJECT_STATE.md) for blockers, [decisions](DECISIONS.md) for durable
choices and [design](docs/superpowers/specs/2026-10-24-snapmaker-u1-mcp-design.md)
for detailed contracts. Historical observations never authorize a mutation.
