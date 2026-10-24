# Read-only U1 milestone implementation plan

> Execute in this session using the planning, execution, and TDD skills. The
> owner's request authorizes the existing Python/stdio design for this milestone.

**Goal:** Deliver `u1_capabilities`, `u1_status`, and `u1_materials` through a real
MCP stdio connection, and a bounded, isolated REA camera investigation.

**Architecture:** A configured, fixed-origin HTTP reader feeds a typed U1 adapter.
The MCP layer exposes only three parameterless read tools. Fresh observations
carry timestamps, partial/unavailable outcomes, and sanitized errors; no stale
cache is substituted for a failed read.

**Tech stack:** Python 3.11+, official MCP Python SDK 1.x, HTTPX, Pydantic,
pytest/pytest-asyncio, Ruff. REA and its compatible Node stay under ignored tooling.

**Spec:** [Bridge design](../specs/2026-10-24-snapmaker-u1-mcp-design.md).

## Constraints and review focus

- Stay on `main`; preserve existing files. Commit/push only at the session end,
  as subsequently requested by the owner.
- All live requests are read-only. No camera session start/stop in this session.
- No addresses, installation paths, credentials, raw responses, or camera session
  values in tracked evidence, MCP results, or diagnostics.
- Tests must catch: ready-but-printing; missing/disabled feed sensors despite
  RFID; malformed or partial mappings; HTTP-200 errors and failed reads; malicious
  upstream strings, redirects, oversized bodies, and tool argument substitution.
- Upload, consumption validation, mutation races/receipts, and stale camera image
  tests belong to later tools; this milestone must not claim they passed.

## Tasks

1. [x] Establish fresh read contracts and isolated tooling. Inspect local object
   shapes and pinned public source; run REA against the identified app artifact.
   Record exact version/hash identities and unresolved live contracts.
2. [x] Write failing tests for fixed-origin bounded reads and conservative U1
   normalization. Implement configuration, transport, schemas, and adapter.
   Cover all four physical tools and 32 logical slots without treating unused
   mapping defaults as evidence that a tool is required by the job.
3. [x] Write a failing subprocess integration test using the official MCP client
   against a local simulated printer. Implement exactly three typed read-only
   tools and verify discovery, calls, failures, argument rejection, and clean stdio.
4. [x] Exercise the same stdio tools against the live printer using local config;
   save ignored receipts and publish only sanitized evidence. Update onboarding,
   state, roadmap, decisions, changelog, and focused camera findings.
5. [x] Review the complete working tree, run final tests/lint/build checks, and
   inspect tracked content for machine-local data. Owner-directed integration is
   a commit and push to `main` at the end; Git is the integration receipt.

## Execution record

- Initial state: documentation-only, unborn `main`, existing files untracked.
- Existing design and current task settle the implementation scope; no new
  approval gate is needed. No separate worktree/branch is created under the
  repository's explicit branch rule.
- Tests were written and observed failing before their implementations. The
  normalization/transport suite and real MCP subprocess tests passed. Independent
  review found compression allocation and SDK logging gaps; regression tests
  failed, fixes passed, and the reviewer independently rechecked both.
- Current verification: 59 tests on Python 3.11.14 and 3.13.12, Ruff checks and
  formatting, wheel/sdist builds. Live registered stdio command returned all
  three tools `ok` with empty stderr at 17:34:05 UTC. Only reads were issued.
- REA 6.7.0/Node 24.22.1 are isolated; focused static excerpts parsed. Whole-bundle
  heap exhaustion, full doctor failure, missing native provider and absent live
  camera session contracts are documented as remaining gaps.
- Final audit: 28 staged files; Markdown links valid; staged content and MCP
  receipts contain no configured origin/hostname, credentials or installation
  paths. Wheel/sdist exclude ignored local data. Remote `main` was absent before
  the owner-directed initial push; no history rewrite is required.
