# Camera RPC correlation and cleanup limits

Date: 2026-10-26. Static client/server investigation only: **no live request**,
camera session, preparation, upload, G-code, control, job-parameter, calibration
or configuration operation. No target code was executed or process attached.

## Result

The saved firmware identifies a server-side camera service in `unisrv`, extending
the earlier [native client trace](2026-10-24-camera.md). Its method registrations
and selected handlers corroborate distinct monitoring and time-lapse RPCs. They
also reveal a specific cleanup blocker: the inspected monitor-stop routine
validates a domain, logs and returns true without clearing monitoring flags or
calling stream/thread cleanup. Its caller can consequently construct a success
reply without this routine stopping monitoring.

There is a registered `camera.get_status` handler, but the inspected implementation
returns coarse monitoring/domain and time-lapse flags. It supplies no owner,
session handle, expiry, capture time or cleanup receipt. It cannot establish the
missing bridge-owned cleanup contract. This is **artifact evidence**, not an
observed installed-printer transaction, a supported HTTP endpoint or authorization
to publish MQTT requests. No camera tool or evidence field is added. Policy 9,
the five-tool inventory, disabled uploads and all existing guards remain.

## Evidence identity and bounded method

Reuse the already saved vendor image for observed firmware
`2.0.0.205_20260914173503`, whose identity and selected public-source comparison
are recorded in the [Orca report](2026-10-25-orca-u1-gcode.md). Release source stays
pinned to `bc271fb351f8c3ad84300e652e46fd93c53b9de1`. No discovery, download,
whole-image identity sweep or live snapshot was repeated. The three client
modules below agree with the existing extracted-file manifest; the earlier
public-source comparison includes `timelapse.py`, not the two transport modules.

| Saved artifact component | Bytes | SHA256 |
| --- | --- | --- |
| `timelapse.py` | 8,673 | `584da4f5e962d53be05b59171ae0732f597c43ca9393f3b5741dcea27c9d6143` |
| `jsonrpc.py` | 10,943 | `22993c0dc24b12ecc733dbc949d74174b5446522781386c58ffb08cc4b65fd14` |
| `mqtt.py` | 8,450 | `78fe3e4b9dfade3b4e24b749005fc45a822adbd194ea06c6645cde21bfd54642` |
| `S90lmd` | 523 | `99c3cc19f5cb77cb81fdffa3ff22509c9ea9c2aa5f99f9c7f5c10a8e507e2cfb` |
| `lmd` | 39,072 | `d4acff94ae40660f0d58a08b43ac4324453818ee72a84e63b49486aaa30ffb50` |
| `unisrv` | 2,191,176 | `229b3cf8a14780ef978e571ed033325b706fd3f23725ece9d4cde5d87aa95c16` |

A focused filename/service inventory in the saved SquashFS image led from
`S90lmd` to its launch-monitor daemon and `unisrv` candidate strings. Service
scripts were read as inert text. The separate isolated firmware Python environment
and existing REA 6.7.0 / Node 24.22.1 / Rizin 0.9.1 were reused. Only selected
image files were extracted under ignored `.tmp/camera-rpc-evidence/`.

REA's `execute-rizin-command --schema` was checked before invocation. `ij`, `iSj`,
`iij` and `izj` supplied layout/import/string leads; bounded `pDj` ranges then
decoded the selected ARM AArch64 instructions. The target is a stripped ELF64.
An inert ADRP/ADD scan supplied candidate string references; conclusions below
use decoded instructions and direct calls, not string presence alone. Names of
C++ roles are correlations with strings/RTTI and behavior, not recovered debug
symbols or proof of runtime selection. No automatic whole-program analysis,
decompiler, firmware installation, authentication bootstrap or target execution.

The sixteen investigation REA results completed without truncation or artifact changes.
The overlapping disassembly windows cover **2,976 unique instructions / 11,904
bytes**; every instruction byte matches its reported offset in the extracted
ELF. Layout reports `.text` and `.rodata` with equal file/virtual offsets in
this artifact. Addresses below are static image addresses, not live ASLR values.
Some windows include neighboring code; they are not claimed as complete function
extents. The monitor-stop routine is bounded separately by its entry and returns.
Raw commands/results, source copies, lead inventories and verification receipts
remain ignored. No private broker/client/session information was collected.

## Time-lapse client: acknowledgment and local state differ

Anchors here refer to the saved `klippy/extras/` modules.

| Anchor | Established behavior and limit |
| --- | --- |
| `timelapse.py:11–15,51–65` | Creates a separate JSON-RPC client using `camera/request` and `camera/response`, passing subscription QoS 0. These are local service topics, distinct from the native GUI's device-prefixed TLS MQTT topics. They are not an authenticated external transport contract. |
| `jsonrpc.py:24–36,59–74,95–129` | A process-shared locked ID generator increments from 1 and wraps after `0x7fffffff`. Requests contain version/method/params/ID; asynchronous calls retain a pending entry only after transport send succeeds. Numeric request correlation is not a camera owner or idempotency token. |
| `:131–197,199–236` | Synchronous calls wait for a matching ID, accept the associated envelope and finally clear their local wait state. A caller-supplied five-second response wait follows a separate wait of up to the default 30 seconds for a prior synchronous call. A timeout does not cancel or reconcile server work. A later numeric-ID reply has no matching synchronous waiter after cleanup. The handler also supports batches; it does not authenticate a camera owner from an ID. |
| `:248–295`; `mqtt.py:65–96,138–175` | JSON-RPC transport `is_connected` is a local subscription-setup flag. Subscribe can register a local handle while the underlying client is disconnected; it is not a SUBACK or current broker/session guarantee. The MQTT provider's separate status delegates to the underlying client's connection report, still not camera ownership/cleanup. |
| `jsonrpc.py:300–317`; `mqtt.py:197–224` | Send invokes `publish_topic` without forwarding the transport's QoS and does not wait for PUBACK or inspect the publish result. Provider QoS defaults therefore matter; the passed zero is not proof of wire QoS 0. Neither successful local send nor broker delivery proves server execution. |
| `timelapse.py:28,79–145,148–181` | Local activity starts false, becomes true after `result.state == success`, and clears after a stop attempt even on an error/timeout; missing MQTT also clears it. An inactive, non-forced stop can return without sending anything. No server reconciliation occurs on this path. Start can also switch the cavity LED before RPC. |
| `:183–224` | Frame capture is an asynchronous `camera.take_a_photo` request with local throttling. No callback is supplied by this caller, and no returned image/capture timestamp is verified. Debug capture creates directories and requests a file, so it is not a passive status diagnostic. |

Do not reuse these client deadlines as server camera leases, retry a camera
mutation after a timeout, or promote a local flag to cleanup evidence. Existing
source logging of raw responses is not a safe bridge logging recipe.

## Server registrations and passive status candidate

At `unisrv:0x9b140–0x9b3ac`, decoded method-string loads and callback pointer
construction register `camera.get_status`, `camera.start_monitor`,
`camera.stop_monitor`, `camera.start_timelapse` and `camera.stop_timelapse`.
The relevant invoke wrappers lead to these handlers:

| Registration / wrapper | Handler and bounded observation |
| --- | --- |
| `get_status`: string load `0x9b144–0x9b148`, invoke `0x9ed80`, call `0x9edf0` | Handler `0x9e6f0–0x9ed74` builds JSON/logging reports. It inserts the literal `interface_type: MIPI`; that field is not a measured camera-type discovery. |
| Status `0x9e8d4–0x9ec4c`; getter `0xbc8a0–0xbc900` | Reads two domain bytes through separate `wan`/`lan` getter calls. `monitoring` is their OR; `monitor_domain` selects `wan` when both are true, otherwise `lan` when only LAN is true. Absent monitor or both false yields false and can omit the domain. A single chosen domain does not expose the full pair or clients. No owner/lease/last-frame/cleanup record is constructed on this path. |
| Status `0x9ea18–0x9eb08` | `timelapse` is false if the instance pointer is null or its atomic state equals numeric 4; otherwise true. The numeric test does not report a completed stop/generation operation, owner or per-job identity. |
| `stop_monitor`: string load `0x9b224–0x9b228`, invoke `0xa1e50`, call `0xa1ec0` | Handler `0xa1830–0xa1e28` parses domain and calls `0xbf060` at `0xa1c00`. A true return leads to success JSON construction at `0xa1c5c–0xa1cb8`. |
| `stop_timelapse`: string load `0x9b374–0x9b378`, invoke `0xa4bf0`, call `0xa4c60` | Handler `0xa4440–0xa4be8` checks the stored instance, calls `0xf3710` at `0xa4534`, and branches on its boolean. This is distinct from monitor stop. |

Status is a promising passive **candidate** at the server level, but these
reports cannot answer the ownership/cleanup question. Its authenticated routing,
installed registration and supported external availability are unverified. No
RPC or guessed Moonraker endpoint was called; MQTT connection alone would itself
require the normal supported authentication and a bounded lifecycle design.

## Specific stop limitations

**Monitor stop:** complete decoded routine `0xbf060–0xbf178` compares the domain
against `wan` and `lan`. For either it logs and returns true; otherwise it logs
and returns false. The instructions do not retain/use the monitor object,
change its two monitoring bytes, signal a worker, unlink an image, close a
stream or call another cleanup routine. Apart from string comparison, logging
and the stack guard, there is no such call on either path. Thus the inspected
handler's success reply does not establish stopping. This does not prove that
all other code lacks automatic expiry or cleanup; those paths were not traced.
It also does not attest the implementation loaded by the printer.

**Time-lapse stop:** on one accepted branch, `0xf37cc–0xf388c` calls a state
setter with numeric 3, stores a callback, starts a thread, detaches it and returns
true. A successful stop-handler acknowledgment can therefore precede detached
work completion. The complete detached worker, finalization, file durability
and callback delivery are outside this trace. Do not describe that acknowledgment
as finished video generation, physical camera release or monitor-session close.

These server findings strengthen the earlier local-inactive warning. They do
not supply a safe cleanup implementation, and they do not justify changing any
printer firmware, configuration, camera session or machine safety behavior.

## Verification, blocker and next action

The [execution ledger](../superpowers/plans/2026-10-26-camera-rpc-evidence.md)
records independent review, software verification, audit and integration.
Independent review checked every reported instruction/identity and corrected one
reversed domain-precedence statement: WAN wins when both flags are true. No
actionable findings remain. A supplemental 48-instruction inert decode confirms
the state setter stores its supplied numeric value at object offset `0x4c`;
the complete setter/worker is not reconstructed. Both parent Python suites and
the reviewer's separate suite passed 700 tests; lint, builds and scope/package
audits passed. Existing
bridge tests validate the unchanged bridge, not these firmware instructions or
hardware camera compatibility. No command or intact export is newly accepted.
Stock-file, transform/provenance, hidden feed/thermal/consumption, action/control
and hardware acceptance gaps remain as listed in PROJECT_STATE.md.

The camera blocker is concrete: no inspected diagnostic supplies ownership,
expiry/freshness or completed cleanup, and the traced monitor-stop path can
acknowledge without implementing cleanup. Do not add a camera tool around it.
The next nonduplicative source action is to trace the monitor start/capture
worker's exit/expiry and destructor paths from this same `unisrv` artifact,
beginning with the `0xbf180` start routine and its constructed worker. Determine
whether an independently completed cleanup/lease signal exists before proposing
any bridge lifecycle. Do not repeat this stop trace, local status snapshots,
credential bootstrap or live camera transactions to substitute for that contract.
If the bounded worker trace cannot establish it, record the precise remaining
server limitation and advance hidden feed/flow demand research instead.
