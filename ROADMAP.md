# Roadmap

Last updated: 2026-10-26

**Legend:** 🟢 Complete with evidence · 🟡 Partial/in progress · 🔴 Not implemented.
The full intended scope remains status, materials, verified file handoff, print
controls, and camera access. File transactions now have simulator verification;
hardware acceptance and broad U1 profile compatibility remain pending.

| Milestone | Status | Evidence / remaining work |
| --- | --- | --- |
| Repository and project documentation | 🟢 Complete | Dedicated checkout, operating rules, tested onboarding, evidence and ignores. |
| Scope and implementation design | 🟡 Partial | Owner directed Python/stdio read milestone; future transaction/camera choices remain proposed. |
| U1 protocol/firmware capability inventory | 🟡 Partial | Three live read tools on one firmware. Native camera TLS MQTT path has static evidence; installed camera wire behavior and advanced RPC remain unverified. |
| Targeted REA investigation | 🟡 Partial | Isolated CLI/MCP, GUI/native client and focused firmware server instructions inspected through Rizin. Server stop/status limits established statically; ownership/expiry and loaded compatibility unresolved. No whole-app reconstruction. |
| MCP runtime/local configuration | 🟢 Read milestone complete | Real stdio tests pass; registered command called all three tools on hardware. A discovered capability tool subsequently succeeded in this chat. |
| Status/progress/errors/material tools | 🟢 Read milestone complete | Typed four-tool/mapping/feed/temperature/progress reads, simulated failures, live three-tool calls. Active hardware fault semantics need observation. |
| G-code validation/verified uploads | 🟡 Software implemented, stock profiles blocked | Policy-9 receipts also bind bounded job preferences; explicit machine IDLE codes and unpaused reporting required for idle. All eight normal exports rejected. Job/transition/hook completion, reprint/parameters, chain/effective mesh/provenance, actual trapq, saved K and hidden demand remain unknown. Macro/feed/end/camera/metadata contracts incomplete. Uploads disabled; hardware acceptance pending. |
| Print start/controls | 🔴 Not implemented | Saved-pause and machine/action reads plus source transition/SD/control ordering exist. No job-parameter/start/control tools; transition/hook completion, saved restore state, callback effects, control acceptance and physical authorization checks remain. |
| Camera snapshots/live sessions | 🟡 Investigation only | Native TLS MQTT/auth/client-ID limits plus saved server RPC handlers traced. Monitor stop can acknowledge without cleanup; time-lapse stop detaches work. Coarse server status cannot establish ownership/expiry/freshness/cleanup. No camera tools or live session acceptance. |
| Automated/hardware verification | 🟡 Software verified, hardware partial | 700 tests on Python 3.11/3.13 and lint/build with actual MCP/HTTP simulation. Camera evidence independently reviewed; one domain-precedence statement corrected, no findings remaining; scope/package audit passed. No new live request. Upload/profile/control/camera hardware acceptance remains. |
| Full release/operator handoff | 🔴 Not released | `0.1.0.dev0` is development software with optional simulated-only uploads; full scope remains. |

See [state](PROJECT_STATE.md) for blockers, [decisions](DECISIONS.md) for durable
choices and [design](docs/superpowers/specs/2026-10-24-snapmaker-u1-mcp-design.md)
for detailed contracts. Historical observations never authorize a mutation.
