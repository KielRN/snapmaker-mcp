# Firmware-matched Orca U1 validation plan

> Execute inline with superpowers:executing-plans under the owner's explicit
> implementation/commit/push request. Stay on main; all live interactions are GETs.

**Goal:** Establish the exact stock-profile blockers and implement only command
forms whose effects are established by the version-matched vendor artifact.

**Architecture:** Preserve the five-tool bridge and all file/receipt safeguards.
Extend the bounded inspector for numeric progress, auxiliary cooling, acceleration
and conservative XY arcs. Reject dynamic macros and transforms; do not rewrite
files or treat a macro name as proof of an inert effect.

**Tech stack:** Existing Python 3.11+, MCP, HTTPX and Pydantic. Firmware extraction
uses an ignored isolated analysis environment; no added product dependencies.

**Spec:** [Bridge design](../specs/2026-10-24-snapmaker-u1-mcp-design.md), validation,
transaction/data boundaries and acceptance sections, plus the owner's focused
2026-10-25 request. Full stock-profile acceptance is conditional on evidence.

## Constraints and review focus

- No live upload, camera start/stop, control, calibration or configuration changes.
- Keep every tool's consumption, temperatures, modes, bounds and mapping checks.
- Arcs require known XYZ, absolute coordinates, XY plane and nonzero IJ offsets;
  bound the entire supporting circle and the endpoint, including helical Z.
- Preserve cold-extrusion checks and absolute-E resets for arcs and tool changes.
- Reject unknown named parameters, relative arcs, R arcs, other planes and macros.
- Reject settings outside conservative software limits; those are not measured
  hardware limits. A raw export is never sanitized into passing input.
- Existing receipts must not silently survive a changed inspection policy.

## Tasks and execution ledger

1. [x] Inspect representative exports privately. Identify command/parameter and
   metadata differences without publishing filenames, paths or geometry.
2. [x] Read current firmware/configuration; download the matching vendor release;
   compare pinned release source and live macro bodies. Record identities and
   unresolved state-dependent effects in the research report.
3. [x] Add failing tests in `tests/test_gcode.py` for the established numeric
   forms, arc interior/endpoint bounds, temperatures, consumption, malformed
   parameters and blocked macros. Implement in `gcode.py`; change the policy
   identity in `uploads.py` and test old-policy receipt rejection.
4. [x] Exercise the accepted fragments and intact blocked stock-shaped files
   through actual MCP subprocess/HTTP simulation in `test_upload_stdio.py`.
   Retain hash, mapping, feed, expiry, reconciliation and disabled-upload tests.
5. [x] Review the complete change; update state, roadmap, decisions, changelog,
   README and design with exact limits. Run both Python suites, Ruff and builds;
   audit secrets, artifacts and links.

**Integration:** The owner-requested commit/push to main follows this audit;
Git history and the remote ref are the integration receipt.

**Ruling:** A matching release artifact establishes static source effects, not
the entire installed runtime or a bounded model of conditional calibration and
toolchanger motion. Full normal exports stay blocked until those effects can be
validated. Do not invent a whitelist for the unresolved macro chain.

**Evidence so far:** Eight exports inspected; firmware identity unchanged;
vendor image SHA256 verified; 14 selected Python sources and two configuration
files match pinned release source byte for byte. Of 87 comparable active macro
bodies, 86 match after removing blank/comment-only lines and indentation;
`SET_PRINT_STATS_INFO` differs. No target code executed; no REA reconstruction
needed because the artifact contains the relevant Python source.

**Clarification:** The one macro textual difference is two inline comments; the
executable body agrees. Independent review found inherited arc-plane state and
decimal fan-selector syntax acceptance. Both were reproduced RED, fixed, and
rechecked with no remaining material finding. Actual-MCP tests cover both fixes
and both interior/endpoint bounds. Product dependencies and five-tool schemas
remain unchanged.

**Final verification:** 215 tests passed on Python 3.11.14 and 3.13.12. Ruff
check/format and wheel/source builds passed. All 41 tracked/staged files, 54 local
documentation links, both build archives and nine runtime ignore samples passed
the privacy/artifact audit. No configured private value was found. Sixteen files
are in scope; the baseline working tree was clean. Fetched origin/main still
matched df03ffe before integration. No branch change or live mutation occurred.
