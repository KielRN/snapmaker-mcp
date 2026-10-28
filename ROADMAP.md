# Roadmap

Last updated: 2026-10-28 UTC

**Legend:** 🟢 Complete with evidence · 🟡 Partial/in progress · 🔴 Not implemented.
The full intended scope remains status, materials, verified file handoff, print
controls, and camera access. File transactions now have simulator verification;
hardware acceptance and broad U1 profile compatibility remain pending.

| Milestone | Status | Evidence / remaining work |
| --- | --- | --- |
| Repository and project documentation | 🟢 Complete | Dedicated checkout, operating rules, tested onboarding, evidence and ignores. |
| Scope and implementation design | 🟡 Partial | Owner directed Python/stdio read milestone; future transaction/camera choices remain proposed. |
| U1 protocol/firmware capability inventory | 🟡 Partial | Three live read tools on one firmware. Native camera TLS MQTT path has static evidence; installed camera wire behavior and advanced RPC remain unverified. |
| Targeted REA investigation | 🟡 Partial | Isolated CLI/MCP, GUI/native client and focused firmware server instructions inspected through Rizin. Shared worker renewal/expiry/destruction now traced; external ownership/completion and loaded compatibility unresolved. No whole-app reconstruction. |
| MCP runtime/local configuration | 🟢 Read milestone complete | Real stdio tests pass; registered command called all three tools on hardware. A discovered capability tool subsequently succeeded in this chat. |
| Status/progress/errors/material tools | 🟢 Read milestone complete | Typed four-tool/mapping/feed/temperature/progress reads, simulated failures, live three-tool calls. Active hardware fault semantics need observation. |
| G-code validation/verified uploads | 🟡 Software implemented, stock profiles blocked | Policy 12 rejects ambiguous duplicate JSON evidence/acknowledgments; policies 1–11 cannot dispatch/promote uncertain results. Per-read source history and all prior job/runtime/material/hash guards remain. All eight exports rejected; effective file-bound parameters, full stock-file demand, transitions/hooks/transforms/provenance remain unresolved. Uploads disabled; hardware acceptance pending. |
| Print start/controls | 🔴 Not implemented | Saved-pause and machine/action reads plus source transition/SD/control ordering exist. No job-parameter/start/control tools; transition/hook completion, saved restore state, callback effects, control acceptance and physical authorization checks remain. |
| Camera snapshots/live sessions | 🟡 Investigation and vendor-UI observation | Connected ordinary viewer displayed a clear chamber image after lighting was enabled. No bridge camera tool, frame timestamp/ownership or completed cleanup acceptance; shared server lifecycle limits remain unresolved. |
| Automated/hardware verification | 🟡 Software verified, hardware partial | Fresh 785-test suites on each Python 3.11/3.13, including ambiguous JSON and old-policy refusal over actual MCP restart. Exact 49,972-byte diagnostic received one owner-directed native Send after fresh physical/material/state/hash checks; expected filename/printing/active-SD, layer progress and complete/inactive-SD observed without errors. Owner inspected/approved coupon with a photo. MCP upload/control acceptance and stock startup/camera lifecycle remain unresolved. |
| Full release/operator handoff | 🔴 Not released | `0.1.0.dev0` is development software with optional simulated-only uploads; full scope remains. |

See [state](PROJECT_STATE.md) for blockers, [decisions](DECISIONS.md) for durable
choices and [design](docs/superpowers/specs/2026-10-24-snapmaker-u1-mcp-design.md)
for detailed contracts. Historical observations never authorize a mutation.
