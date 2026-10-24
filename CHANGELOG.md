# Changelog

Implemented changes only. No published release exists.

## Unreleased — 0.1.0.dev0

### Added — 2026-10-24

- Dedicated repository, operating guide, state/roadmap/decisions, design and
  ignore coverage for machine config, credentials and generated artifacts.
- Python 3.11+ package, official MCP SDK 1.x stdio runtime, locked dependencies,
  typed `u1_capabilities`, `u1_status`, and `u1_materials` tools.
- Fixed-origin read-only HTTP transport with total deadlines, raw byte limits,
  redirect/compression refusal, no environment proxies, sanitized outcomes, and
  no automatic retries or stale cached success.
- Four-tool mapping, RFID identity, feed/toolhead-sensor evidence, conservative
  loaded/idle/unknown states, temperatures, progress and numeric exceptions.
- 59 tests including actual MCP subprocess calls and simulated printer failures;
  regression coverage for compressed-body amplification and SDK validation logs.
- Tested setup/check/build commands, local Codex registration with verified launch,
  isolated pinned REA/Node installer, camera research and read-contract evidence.
- Focused camera follow-up: isolated Rizin 0.9.1 via REA, pinned Orca 2.4.0 source
  comparison and native call/table evidence for the WCP TLS MQTT path. Documented
  separate authentication layers, omitted camera `clientid`, client timer policy,
  unresolved server contracts, and a bounded passive next probe. No camera tools added.

### Verification

- Full suite passed on Windows/Python 3.11.14 and 3.13.12; Ruff checks/formatting
  and wheel/source builds passed. Independent review returned no remaining findings.
- Registered MCP command initialized, listed/called all three tools against the
  installed U1, returning `ok` with empty stderr. All live checks were read-only.
- REA CLI/MCP and camera/lifecycle excerpts worked. Follow-up REA/Rizin inspected
  seven selected DLL functions (34,540 bytes) and seven additional GUI excerpts.
  Whole-bundle heap exhaustion is historical; full doctor/Ghidra readiness is
  not claimed. A fresh discovered capability tool returned `ok` on the same firmware.
- Follow-up checks passed: 59 tests on Python 3.13.12, Ruff check/format, wheel/
  source builds, documentation links and original-byte/source-provenance audits.

### Remaining scope

No upload, print-control, receipt or camera tools are shipped. Installed camera
wire/authentication compatibility, server expiry/ownership, image freshness and
authorized physical acceptance remain unresolved. Static native/source evidence,
simulated tests and live reads do not prove those capabilities.
