# Focused transform lifecycle evidence

Continue inline on main from `f7f712bd90c61161e0a1bb3e0967fec77b8137a9`
under the owner's implementation/review/commit/push authorization. All printer
interactions remain read-only. The [design](../specs/2026-10-24-snapmaker-u1-mcp-design.md)
and [runtime evidence](../../research/2026-10-25-runtime-evidence.md) govern scope.

## Contract and review focus

- Reverify the existing matched source identities. Trace exclusion transform
  installation/removal, mesh fade/offset/profile provenance and coordinate frames.
- One fixed GET selecting only `exclude_object.excluded_objects,current_object,
  in_excluded_region` answers availability/type questions left by prior reads.
  Do not requery fields already known absent or use G-code as a read substitute.
- Extend existing status and repeated receipt observations with bounded exclusion
  label digests, count, current-object presence/digest and reported region state.
  Never publish raw labels/geometry or infer transform installation from them.
- Missing/null current-object are different: explicit null is known absence;
  absent or malformed is unknown. A region report can lag a marker/reset, so do
  not assert membership/region consistency unsupported by source.
- Increment receipt policy to 5; policies 1–4 cannot dispatch/promote uncertain
  operations. Keep no-replay, timestamps, serialization and every existing guard.
- Leave mesh fade/lookup offsets/ZFADE, provenance, chain identity and machine
  safety unknown. No command or intact export becomes newly accepted.

## Tasks / execution ledger

1. [x] Read sources, verify baseline/identities and make the one focused GET.
2. [x] Write failing synthetic normalization, fixed-query, binding/race/old-policy
   and actual MCP tests. Implement only the established contract, then verify.
3. [x] Recheck all eight untouched exports; update research, design and project docs.
4. [x] Obtain one independent fresh-context review of the entire scope. Fix material
   findings with failing regressions. Run Python 3.11/3.13 suites, Ruff/builds and
   privacy/artifact/link/ignore audit.
5. Inspect full scope; commit/push main.

Preflight: status normalization feeds the receipt digest automatically; both
runtime queries must use the same fixed exclusion projection. Model defaults
must still deserialize historical receipts without permitting old-policy reuse.

## Execution evidence

- Baseline main was clean at `f7f712b`; no existing Graphify graph or unrelated
  work. All required state/research/design/plan documents read. All 20 existing
  source-manifest SHA256/Git blob entries and two focused artifact-only entries
  reverified. No paid graph rebuild, downloads, REA or target execution needed.
- One GET at 15:23:02 UTC, 151 bytes, confirmed empty exclusion list, explicit
  null current object and boolean false region. Raw output ignored. No other
  live request or preparation/mutation; local uploads remain disabled.
- Initial regressions: 21 normalization/query/policy failures, plus 18 binding/
  actual-MCP failures observed before implementation. The first focused green
  run passed 152 tests; subsequent same-size label/transport checks are included
  in the complete suites. Policy 5 and the fixed three-field projection are the
  only collection/acceptance changes; G-code command semantics are unchanged.
- All eight intact export bytes/hashes/rejections rechecked unchanged. Complete
  suites passed 342/342 on Python 3.11.14 and 3.13.12. Ruff check/format and wheel/
  source builds passed. Audit: 51 files, 89 links, two archives, 11 ignore samples;
  zero configured private-literal/generated-runtime matches or broken links.
- Independent fresh-context review: no actionable findings or deferred minors.
  Reviewer separately passed all 342 tests on Python 3.13.12, Ruff and direct
  malformed/default probes; verified source identities/claims and old-policy
  refusal. Hardware compatibility, loaded bytes, physical transform state and
  calibration validity remain unjudged/unestablished, as required by scope.
- Integration preflight fetched origin/main, still baseline `f7f712b`. Branch
  main and full scope inspected; no unrelated changes. The resulting Git commit
  and remote ref are the final integration receipt; no branch/PR is created.
