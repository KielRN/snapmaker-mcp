# Decisions

Last updated: 2026-10-24

Record durable choices with their date, status, and reason. **Confirmed** means
directly established by owner direction or carried-forward printer operating
instructions. **Proposed** means a working design choice awaiting resolution;
documentation alone does not make it owner-approved. Supersede an entry
explicitly when its direction changes.

## D001 — Dedicated repository

Date: 2026-10-24 · Status: Confirmed

Develop the bridge in `KielRN/snapmaker-mcp`, as requested by the owner. Keep
bridge code, tests, research, and documentation here. The 3DPrintPosters product
repository remains a separate project; changes to it need their own task scope.

## D002 — Full connection scope

Date: 2026-10-24 · Status: Confirmed

Cover printer status, file upload and start, pause/resume/cancel controls,
physical tool/material mapping, and camera access. The owner confirmed all of
these capabilities. Snapshot and live camera behavior are described in the
draft design; their actual protocol remains under investigation.

## D003 — Per-plate physical authorization

Date: 2026-10-24 · Status: Confirmed operating constraint

Every start requires authorization for the specific plate and fresh human
confirmation that the build plate is installed and clear. One start does not
authorize the next plate. Check current printer state, material feed, mapping,
exceptions, and the actual exported file before a start. An MCP argument cannot
independently establish physical clearance.

Do not change firmware, persistent printer configuration, or calibration as part
of this bridge workflow. Read-only inspection is appropriate while printing;
control actions must stay within the authorized job scope.

## D004 — Local connection using the verified protocol

Date: 2026-10-24 · Status: Confirmed for read milestone; advanced RPC proposed

The owner's implementation request adopts local Moonraker HTTP for the first
three read tools. All three were verified through actual MCP stdio on the
installed firmware. Build around the local HTTP connection exercised on the studio
U1. Add U1-specific RPC and subscriptions only after verifying the installed
version's transport and behavior. Public repository source is a research lead,
not evidence that the installed firmware has identical behavior.

Keep the printer interface private to the trusted LAN. Cloud-account dependence
is not assumed; a camera limitation that requires cloud login needs an explicit
decision rather than silently changing the architecture.

## D005 — Keep slicing outside the connection bridge

Date: 2026-10-24 · Status: Confirmed by focused upload implementation request

Use the existing OrcaSlicer integration for slicing. The new bridge validates
exported G-code, checks physical tool/material requirements, uploads it, and
coordinates verified printer operations. It does not generate geometry or
automatically send product-app customer orders to the printer.

## D006 — Python server over stdio

Date: 2026-10-24 · Status: Confirmed for this milestone by owner implementation request

Use Python 3.11+ and the official Python MCP SDK, with HTTP and WebSocket clients
where the verified protocol needs them. Run locally over stdio; send diagnostic
logs to stderr. This follows the existing local Python tooling. Exact compatible
dependencies and module layout are implementation choices. The implemented
package uses official MCP SDK 1.30.0 and HTTPX 0.28.1, with a committed uv lock.
No WebSocket dependency is introduced before the needed contract is verified.

## D007 — REA as a focused development tool

Date: 2026-10-24 · Status: Confirmed development direction by owner request

Use the official [REA project](https://github.com/morluto/rea) to investigate
specific missing contracts, beginning with the installed app's camera flow.
Inspect JavaScript and relevant native components as evidence directs. Keep
REA and any required Node/Ghidra runtime isolated from product environments.
The finished bridge should not require REA or the Snapmaker GUI to run.

REA 6.7.0 and checksum-verified Node 24.22.1 are isolated under ignored tooling.
The follow-up adds checksum-verified Rizin 0.9.1 through REA's child-scoped
`REA_RIZIN_COMMAND`, without changing product dependencies or global tools.
Focused GUI and native inspection worked; full doctor/Ghidra readiness is not
claimed. Native byte/call evidence and pinned source establish the selected WCP
camera transport statically, while installed camera compatibility remains
unverified. See the [camera report](docs/research/2026-10-24-camera.md).

## D008 — Verify effects and reconcile uncertain outcomes

Date: 2026-10-24 · Status: Implemented for preparation/uploads; controls remain proposed

Hash the selected file, download and verify uploaded bytes, bind preparation to
the selected mapping/materials, and check the actual printer outcome. Preserve
operation receipts across restarts. After a timeout or disconnect, reconcile
state before retrying; never blindly replay a start.

Represent accepted, rejected, unavailable, and unknown outcomes distinctly.
Print acceptance, first-layer success, print completion, and physical quality
are separate claims requiring separate evidence.

The upload implementation persists an atomic claim/inflight record before POST,
uses one receipt database/OS lock per printer, and never repeats a dispatched
POST. Reconciliation after expiry can establish byte transfer without renewing
preparation or authorizing start. Lost-reply reconciliation explicitly marks
response flags unconfirmed. Bad acknowledgment/hash results are terminal. See
the [upload contract](docs/research/2026-10-24-uploads.md) for exact limits.

## D009 — Traffic-light roadmap and honest project state

Date: 2026-10-24 · Status: Confirmed

Use a table with 🟢 / 🟡 / 🔴 status in [ROADMAP.md](ROADMAP.md), as requested by
the owner. Keep compact evidence and next actions in [PROJECT_STATE.md](PROJECT_STATE.md),
implemented changes in [CHANGELOG.md](CHANGELOG.md), and detailed contracts in
the [design draft](docs/superpowers/specs/2026-10-24-snapmaker-u1-mcp-design.md).
Do not promote a proposal or an untested capability to complete through a docs update.

## D010 — Strict read-only first milestone and conservative results

Date: 2026-10-24 · Status: Implemented engineering choice within owner scope

Expose exactly three parameterless, typed read tools. Use fixed HTTP routes and
known objects, bounded uncompressed raw reads with total deadlines, no redirects,
environment proxies or automatic retries, and no stale fallback cache. Return
partial/unknown values rather than coercing missing evidence. Suppress SDK/HTTP
diagnostics that can echo raw requests; publish fixed safe errors and selected
fields only. Do not expose raw exception messages, filenames, machine paths or
RFID card identifiers. Preserve the full future scope as unimplemented.

## D011 — Camera session changes deferred during this investigation

Date: 2026-10-24 · Status: Confirmed operating scope for this session

The owner's request requires read-only live checks. No camera start/stop or
printer mutation was issued. Inspect the pinned GUI artifact and isolated REA
results without executing target code. Keep installed-printer camera transport/
authentication compatibility and session ownership unresolved until demonstrated
through the ordinary supported flow; static findings alone do not authorize or
validate a session implementation.
This constraint continues through the focused native follow-up: its only fresh
printer interaction was the read-only capability tool.

## D012 — Separate native camera evidence from session guarantees

Date: 2026-10-24 · Status: Confirmed investigation boundary; implementation deferred

The selected native WCP branch publishes camera JSON-RPC through TLS MQTT. Its
camera handlers rebuild parameters without the GUI's optional `clientid`.
Preserve that branch-specific finding rather than substituting generic WebSocket
assumptions or treating a GUI client ID as proof of camera ownership.

Keep the GUI's 300-second monitoring policy, MQTT keepalive, native callback
timeouts, certificate lifetime, and server camera expiry distinct. None of the
first three establishes the latter two. Require installed-firmware evidence for
credential provisioning, ownership, expiry and noninterfering cleanup before
camera tools. A bounded passive trace is the next validation probe; it does not
authorize creating/closing a session or prove the remaining lifecycle contracts.

## D013 — Restricted preparation and simulator-only upload acceptance

Date: 2026-10-24 · Status: Implemented engineering choices within owner scope

Add two typed file tools while leaving print controls/camera absent. Preparation
has no printer effects; uploads require local enablement, default false. The
owner limited all hardware checks in this chat to reads, so source contracts
and simulated success do not establish installed upload compatibility.

Fail closed on unresolved macros, transforms, commands and job requirements.
Inspect every consumption entry and executable heater/move command. Use an
opened-file-handle check on Windows/Linux to reject symlink/junction escapes,
bounded streaming passes and worker-thread inspection. Enforce the documented
conservative envelope; do not claim those limits were measured on the printer.
Operator-configured nozzles are explicitly attested, not sensor evidence.

The pinned upload code supplies a narrow `print=false` no-start/no-queue contract
and raw HTTP-201 JSON envelope; no further REA/native work was needed for this
contract. Ordinary Orca U1 macros remain unresolved and rejected, rather than
inferred safe from names. Hardware upload acceptance and firmware-matched macro
analysis are required before broad profile support. Do not remove safety/setup
commands to bypass validation. This supersedes D010's exactly-three-tool
inventory only; its read behavior, redaction and data boundaries remain.
