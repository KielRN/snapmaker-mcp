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

### Verification

- Full suite passed on Windows/Python 3.11.14 and 3.13.12; Ruff checks/formatting
  and wheel/source builds passed. Independent review returned no remaining findings.
- Registered MCP command initialized, listed/called all three tools against the
  installed U1, returning `ok` with empty stderr. All live checks were read-only.
- REA CLI/MCP worked and camera/lifecycle excerpts parsed. Whole-bundle analysis
  exhausted its heap; full doctor/native-provider readiness did not pass.

### Remaining scope

No upload, print-control, receipt or camera tools are shipped. Camera wire
transport/authentication/ownership/freshness and authorized physical acceptance
remain unresolved. Simulated tests and live reads do not prove those capabilities.
