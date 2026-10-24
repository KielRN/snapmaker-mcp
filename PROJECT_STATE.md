# Project state

Last updated: 2026-10-24

## Current stage

The first read-only Python/stdio milestone is implemented as unreleased
`0.1.0.dev0`: `u1_capabilities`, `u1_status`, and `u1_materials`. The owner directed
this design's implementation and subsequently requested a push to `main`.
Future print transactions and camera implementation remain proposed; this does
not complete the full bridge.

## Verified evidence

- 59 tests passed on Python 3.11.14 and 3.13.12. Ruff checks/formatting and wheel/
  source-distribution builds passed. Tests exercise actual stdio MCP plus local
  HTTP simulation, without hardware or credentials.
- Independent review reproduced compression memory amplification and SDK logging
  of malformed request payloads. Both fixes were regression-tested and rechecked;
  no findings remained.
- Local Codex entry `snapmaker_u1` was registered. Its configured command/env were
  exercised by the official MCP client: initialize, exactly three tools listed,
  all three calls `ok`, empty stderr, **2026-10-24 17:34:05 UTC**. Discovery in
  this chat was subsequently confirmed by a discovered `u1_capabilities` call at
  **2026-10-24 17:54:59.822526 UTC**, returning `ok` and the same firmware.
- Live reads reported firmware `2.0.0.205_20260914173503`, Moonraker `2.0.0`,
  Klipper ready while printing, active virtual SD, and selected physical tool 2
  (`extruder1` / T1). Exceptions were empty in that snapshot.
- All four enabled toolhead sensors and feed modules reported filament present
  and completed/error-free loading. Four loaded states and the 32-slot mapping
  were returned. This is time-specific sensor evidence, not physical inspection
  or a continuing loading guarantee.
- All live checks were reads. No upload/control, motion, camera start/stop,
  firmware/configuration, or calibration action was issued.
- Isolated REA 6.7.0/Node 24.22.1 and checksum-verified Rizin 0.9.1 now support
  focused native inspection. Seven DLL functions (34,540 bytes) and seven more
  GUI excerpts were inspected without executing target code. The native WCP
  camera branch reaches JSON-RPC over TLS MQTT; pinned Orca 2.4.0 source describes
  certificate bootstrap and response correlation. This is static evidence, not
  an installed-printer camera transaction. Full doctor/Ghidra readiness is not claimed.
- The native camera branch drops the GUI's optional `clientid`. A 300-second GUI
  renewal/close timer is established; server expiry and ownership are not. See
  the [camera report](docs/research/2026-10-24-camera.md) for anchors and limits.

Raw replies, local config, receipts, app excerpts, and REA artifacts are ignored.
Tracked fixtures are synthetic. [Read evidence](docs/research/2026-10-24-read-contracts.md)
records pinned public source and installed-contract limits.

## Remaining gaps and next actions

1. Broader firmware versions, real outages, and active exceptions have
   simulated/source evidence, not hardware acceptance.
2. Validate the native camera branch against installed firmware with one bounded,
   redacted passive trace of an ordinary operator-authorized transaction. No
   camera opening/closing is authorized by this investigation. Server ownership,
   expiry, credential provisioning, freshness and safe cleanup remain prerequisites
   for camera tools; the trace alone will not resolve them all.
3. Implement file/per-tool-consumption/path validation, upload/download hash
   verification, persistent receipts, serialized controls and uncertain-outcome
   reconciliation in later milestones.
4. Obtain specific-job authorization and fresh clear-bed confirmation before any
   start/control hardware acceptance. Print completion/quality checks remain.

The [roadmap](ROADMAP.md) owns milestone status. This milestone is neither a
release nor full print/camera capability.
