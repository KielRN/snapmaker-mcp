# Camera worker renewal, expiry and teardown

Date: 2026-10-26. Saved-artifact investigation only; **no live request**, camera
session, target execution, process attach or printer mutation. This continues the
[RPC report](2026-10-26-camera-rpc-evidence.md), without repeating its stop/status
trace. No tool, field, policy, command or intact export is newly accepted.

## Result and evidence identity

The saved server has a shared monitor-worker expiry path and an object destructor
that clears domain flags and joins the worker. This resolves the earlier narrow
question of whether any automatic teardown path exists. It does **not** establish
a bridge-owned lease, an installed expiry deadline or an observable completed
cleanup contract. A false monitoring flag can precede callbacks and resource
release. Waiting for a timer or repeatedly reading coarse status cannot safely
close a bridge-owned session or prove a fresh image.

Reused the existing extracted `unisrv`: 2,191,176 bytes, SHA256
`229b3cf8a14780ef978e571ed033325b706fd3f23725ece9d4cde5d87aa95c16`.
The observed firmware identity remains historical `2.0.0.205_20260914173503`;
release source remains pinned to `bc271fb351f8c3ad84300e652e46fd93c53b9de1`.
The [Orca report](2026-10-25-orca-u1-gcode.md) and prior RPC report own provenance.
No new download, whole-image identity sweep, credential setup or hardware probe.
Static artifact identity does not attest code loaded on the printer.

Existing isolated REA 6.7.0 / Node 24.22.1 / Rizin 0.9.1 produced bounded AArch64
instruction windows. Saved ELF section metadata and little-endian data pointers
connect the constructed thread's vtable to its run wrapper; RTTI/data pointers
separately identify the monitor shared-object disposal path. Pointer/string
matches are leads until verified against instructions and calls. Raw commands,
results, pointer/constant checks and byte-verification receipts stay ignored in
`.tmp/camera-worker-evidence/`. Neighboring code in windows is not claimed as a
reconstructed function. No whole-program analysis or decompiler was used.

All ten new REA results and one reused start window completed without truncation
or artifact changes. The combined windows cover **4,560 unique instructions /
18,240 bytes**, checked individually against ELF offsets. Six selected data
pointers, eight strings, the sleep timespec and timer-branch constants were
checked directly. Two focused source identities were checked against the saved
manifest for the feed continuation. These are static verification checks only.

## Start and renewal share state across domains

| Artifact anchor | Established behavior |
| --- | --- |
| `0xbf180–0xbf1cc`, `0xbfa14–0xbfa88` | Start validates `lan` or `wan`. The complete start contract, handler argument validation and all failure effects remain outside this bounded trace. |
| `0xbf24c–0xbf290`, `0xbf980–0xbfa10` | WAN start sets byte `+0x61`; either accepted domain sets renewal byte `+0x62`. If LAN byte `+0x60` is already true, the path can return true without constructing another worker or storing the new interval. Otherwise it locks, sets LAN byte `+0x60` and stores the interval at `+0x64`. Thus these bytes are shared domain/activity reports, not per-client ownership. |
| `0xbf920–0xbf97c`; data `0x212e68–0x212e88` | Constructs a thread state holding the monitor pointer, with vtable entries `0xbc5b0`, `0xbc5d0`, `0xc11f0`; starts the thread and saves its handle at `+0xe0`. |
| `0xc11f0–0xc1218` | Run wrapper loads the captured monitor pointer and calls worker `0xc01a0`. Thread-state destructors `0xbc5b0–0xbc604` release the thread-state allocation; they are distinct from the monitor destructor. |
| `0xc0290–0xc02f8` | Worker initializes a steady-clock time; when renewal byte `+0x62` is set, refreshes that time and clears the byte. Both domain flags share this one timer; both false leads toward normal exit. |

The inspected renewal branch carries no caller ID or separate LAN/WAN deadline.
Another accepted start can renew the same worker. This is not a per-owner lease,
even if normal external routing eventually becomes verified.

## Timer expiry is internal and is not a cleanup deadline

At `0xc06a8–0xc0708`, absent renewal, the worker subtracts the saved steady-clock
count and compares it against **360,999,999,999**, taking the expiry branch only
when greater. A lower threshold **310,999,999,999** gates a warning callback,
passing `360 - converted_elapsed_seconds` to `0xbd410`. The integer arithmetic
and interval multiplier are consistent with nanosecond steady-clock counts:
approximately 311 seconds for warnings and 361 seconds for expiry. This unit/time
interpretation is an inference from compiled arithmetic, not an observed timer
or installed library/clock attestation. Do not round it into a guaranteed
300- or 360-second server lease.

The loop calls capture, filesystem and WAN work between timer checks. It can
sleep in half-second pieces (`0xc062c–0xc06a4`; constant timespec at `0x1988f0`),
but no whole-worker wall-clock upper bound is established. The earlier GUI's
300-second timer is a separate client behavior. No elapsed-time assumption may
replace reconciliation or authorize stopping another client's camera.

The warning helper `0xbd410–0xbd5f4` constructs a remaining-time notification and
invokes an optional stored callback. The status-change helper beginning `0xbd690`
constructs `monitoring`, `monitor_domain` and a wall-clock `timestamp`, then invokes
its stored callback at `0xbdd64`. That timestamp belongs to notification building;
it is not a capture timestamp, owned lease or a cleanup receipt. Callback routing,
delivery and installed availability are unverified.

## Normal exit and destruction have different evidence

- Expiry `0xc0c00–0xc0c08` clears **both** domain bytes before further cleanup.
  With stream flag `+0x118`, it calls helper `0x345b0`, then clears that flag
  (`0xc0d88–0xc0da8`). The helper decrements a shared consumer count under a mutex;
  its last-consumer branch calls `0x4d440`. The worker does not test the helper's
  returned success. Full lower-level stream shutdown remains untraced.
- Normal exit `0xc0c0c–0xc0ca0` invokes the false/LAN status callback, then clears
  and releases a stored shared pointer at `+0x88/+0x90`. The callback therefore
  precedes that release. The subsequent task-exit log is not exposed as a durable
  external completion record. No owned session or captured-frame identity is
  supplied by this path.
- Capture path `0xc0310–0xc041c` invokes an optional capture callback, constructs
  shared filesystem paths and creates/replaces a symlink. The inspected normal
  exit does not unlink that symlink or validate an image timestamp. This is a
  specific path limit, not a claim that every service path leaves files behind.
  A readable image or false monitoring report cannot establish freshness.
- RTTI name/data pointers identify monitor shared-object disposal through
  `0x214028`, vtable `0x212c38`, and `0xaa4d0 -> 0xbcb60`. The destructor clears
  both flags at `0xbcb74` and joins a nonzero thread handle at `0xbcc64–0xbcc74`
  before releasing stored objects/callbacks/strings. There is no per-client
  close handle or timeout in this destructor. Its join does not create a remote
  completion API. It is not the routine called by the earlier stop handler.

These anchors establish available static normal/expiry/destruction paths, not
successful completion on every error/exception branch, safe inter-client races,
physical camera release, or installed execution. The earlier no-op monitor-stop
finding remains; automatic expiry does not repair its acknowledgment contract.

## Decision and next work

Camera implementation remains blocked by missing normal authenticated external
routing, owner isolation, bounded freshness and observable completed cleanup.
Do not add a tool around these flags, wait a guessed lease, delete shared images,
change firmware, or start/stop a camera to fill that gap. A future operator-
authorized passive trace can validate wire behavior but cannot alone establish
ownership and cleanup. This bounded investigation is complete; do not repeat it
in successive runs without changed evidence.

An independent [feed-resolution investigation](2026-10-26-feed-resolution-evidence.md)
now identifies table fallback/rollback and separate resolver calls as the next
source contract. Policy 9 and all prior guards remain unchanged. The
[execution ledger](../superpowers/plans/2026-10-26-camera-worker-evidence.md)
records independent review, software verification and integration. Bridge tests
exercise the bridge and simulation; they do not execute this firmware or prove
camera hardware acceptance. Full readiness remains incomplete.

Independent fresh-context review found no actionable findings. It independently
mapped ELF PT_LOAD bytes for all 4,560 instructions, decoded timer constants and
branches, checked clock/thread imports, pointers/RTTI/source anchors and separately
passed 700 tests on Python 3.13.12. Parent suites passed 700 tests on each supported
Python; Ruff, builds and complete scope/package/privacy/link checks passed. The
review expressly leaves installed execution, external routing/ownership, guaranteed
teardown, lower-level release, effective material tables and hardware acceptance
unestablished. Those limits are retained; no readiness milestone is promoted.
