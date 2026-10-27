# Roadmap

Last updated: 2026-10-27 UTC

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
| G-code validation/verified uploads | 🟡 Software implemented, stock profiles blocked | Policy-9 receipts bind bounded job preferences; explicit machine IDLE codes and unpaused reporting required. All eight exports rejected. Hidden parameter parsing/reset/reprint and asynchronous persistence traced; file-bound effective provenance and upstream metadata correspondence remain unresolved. Full demand, job/transition/hook completion, chain/effective mesh/provenance, trapq and saved K remain unknown. Uploads disabled; hardware acceptance pending. |
| Print start/controls | 🔴 Not implemented | Saved-pause and machine/action reads plus source transition/SD/control ordering exist. No job-parameter/start/control tools; transition/hook completion, saved restore state, callback effects, control acceptance and physical authorization checks remain. |
| Camera snapshots/live sessions | 🟡 Investigation only | Native TLS MQTT/auth/client-ID limits plus saved server RPC/worker paths traced. Shared expiry/destructor exists, but flags precede completed cleanup and no owned lease/completion is exposed. Stop can acknowledge without cleanup. No camera tools or live session acceptance. |
| Automated/hardware verification | 🟡 Software verified, hardware partial | 700 tests on Python 3.11/3.13 and lint/build with actual MCP/HTTP simulation. Hidden-parameter evidence independently reviewed with no actionable findings; scope/package audit passed. No new live request. Upload/profile/control/camera hardware acceptance remains. |
| Full release/operator handoff | 🔴 Not released | `0.1.0.dev0` is development software with optional simulated-only uploads; full scope remains. |

See [state](PROJECT_STATE.md) for blockers, [decisions](DECISIONS.md) for durable
choices and [design](docs/superpowers/specs/2026-10-24-snapmaker-u1-mcp-design.md)
for detailed contracts. Historical observations never authorize a mutation.
