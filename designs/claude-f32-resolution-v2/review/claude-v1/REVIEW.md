# Independent design review: F32-CONFLICT resolution design v2

**What this is.** An independent design review by a Claude Code review subagent (claude-opus-5-5) with a fresh context. I authored nothing under review and I am not the drafting agent. It grants no acceptance. Every original Phase One obligation stays OPEN. It does not claim the original GPT-6.1 review gate. That gate was superseded by the human's 2026-10-05 ~17:05Z direction (WT/STATUS.md:279-291) and is recorded at DESIGN.md:524-528.

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**
- R-A and its exact patch are sound and weaken nothing. I reproduced them independently again.
- RC-1, RC-2 and RC-4 are CLOSED.
- RC-3 is CLOSED in substance, but the transaction-level controls v2 names as "the 1.9.1 control" are wrong: neither exists in 1.9.1. That needs one new required change, RC-5. It touches no patch byte and changes no conclusion about R-A.

## Inputs and identities
- **Brief:** `WT/briefs/f32-resolution-design-v2.md`, sha256 `81bd8f9479d7590cbc21e386622ecd73d10703fe8275203adf0005cb545d0379` (53 lines).
- **Under review:** the three hashes match the brief.
  - DESIGN.md `e52a9227…349df9`
  - evidence.json `9a27640a…77eb25c`
  - f32-r-a.patch `226e7fc8…2c136650`. Its hash equals v1's patch hash.
- **v2 has no `review/` directory.** I read no review of v2 and no session transcript.
- **Closure target read:** the sealed v1 review in `WT/designs/claude-f32-resolution-v1/review/claude-v1/`.
  - REVIEW.md `b491d9d2…`
  - review.json `98e7dbe1…`
  - review-freeze.json `cdbc9787…`
- **Method:**
  - sha256 and reading only.
  - `git apply --check` against S5 (rc=0). It writes nothing.
  - Post-images built in memory and checked with Python `hashlib` and the standard-library `ast` module.
  - No WORLDLINE code imported or executed.
  - All eight Ada skills loaded before reading the Ada specs and bodies.

## 0. RC closure and what else changed versus v1

**RC-1: CLOSED.**
- **A1 and the raw :92-160 twins in metadata-tests.**
  - Inventoried at DESIGN.md:189-202.
  - Verified: `test_evaluation_row_projection.py:12` imports `RawRequiredFailureControls`, :20 subclasses it, and the file has no `load_tests`.
  - Recorded metadata-tests `child.stderr`, in both roots: :3 (MetadataNativeControls A1), :47 (RawRequiredFailureControls A1), :10/:54, :40/:79, :82 "Ran 79 tests", :84 "OK". `child-wait.json` returncode 0.
  - stderr hashes `3276de09…` and `d21d8bb1…` match evidence.json.
- **A1 collection count** (default-tests once, metadata-tests twice): JACKAL exact, parsed=1+2, exact=3. This matches DESIGN.md:189.
- **Lifetime :92-105.** Inventoried at DESIGN.md:206-215, §3.2 :281-287, §7 :488 and E4 :545.
  - Verified at `test_context_cast_lifetime.py:93-105`: both statuses build from `collapse_values()` (:95) and assert `new_result == old_result` (:104).
  - The codes are recorded as evidence only, not as a criterion (DESIGN.md:214-215, :545).
- **E2 names both collected instances** (DESIGN.md:543).
- **`collapse_values` call sites** at lifetime :95, :109, :122, :137 and :154 (DESIGN.md:168) are confirmed by grep.
- **Inventory completeness** (grep of S5 `*.py`):
  - The only callers of `bound_request` are raw :84, :93-156 and :217, and row :87 and :106.
  - The only callers of `collapse_values` are fin :258 and :269, and lifetime :95-154.
  - `test_finalization_cast_lifetime.py:19`, `test_context_cast_lifetime.py:15` and `test_tagged_object_cursor.py:11` import the *module*, not the class, so the loader does not re-collect `FinalizationNativeControls`.
  - `test_recovery_packet_producer.py:13-14` imports both classes, but `load_tests` at :207-212 restricts collection to its own methods.
  - Nothing is missing.

**RC-2: CLOSED.**
- The design requires every A1–A4 module in the baseline and in the E0–E6 source (DESIGN.md:503-515, §6 :422-424, §9 :536-537, :541, :545).
- Verified by `test -e` (no listing): all four of `test_context_cast_lifetime.py`, `test_finalization_cast_lifetime.py`, `oracle_finalization_kernel_cast_lifetime.py` and `oracle_evaluation_context_cast_lifetime.py` are ABSENT in both `W/work/item1-repair/source/tests` and `W/work/integrated-ordinary-v8/source/tests`.
- They are present in S5: `f6bc3e2f…`, `d9ae6698…`, `fe91b945…`, `b8b0d136…`.
- The control counts match REQUIRED-LIFETIME-CONTROLS.json:4-21 (DESIGN.md:545).
  - Context module, :5-9: JACKAL exact, parsed=1+1+1+1+1, exact=5.
  - Finalization module, :12-20: JACKAL exact, parsed=1+1+1+1+1+1+1+1+1, exact=9.

**RC-3: CLOSED in substance; a new factual error in the identification (RC-5).**
- The attribution to the preserved-controls rule is made at DESIGN.md:69-75 and :338-346. The citations hold:
  - WORKSPACE-RULES.md:6;
  - RECOVERY-AND-AUTONOMY.txt:5;
  - roster :2174-2198, :2199-2223, :2374-2398 and :2600-2605;
  - REQUIRED-LIFETIME-CONTROLS.json:3-24.
- The design also says, correctly, that OB-003's "1.9.1 control" (OBLIGATIONS-v2.json:95) is transaction-level and separate from A1–A4.
- **The error.** v2 names that control as `test_transaction.py:276-329` plus `test_typed_absence.py:1238-1252` (DESIGN.md:80-85, :352-357, :480). Neither is a 1.9.1 control:
  - `test_judge_mutations_refuse_even_when_freshness_shortcut_is_bypassed` is absent from the 1.9.1 release `tests/test_transaction.py` and from pre-item1 `ENG/source/tests/test_transaction.py`.
  - `test_original_positive_commit_retains_the_measured_staged_requirement` is absent from both. It is an item1-repair addition (`W/work/item1-repair/HANDOFF.md:34-36`).
  - The S5 family :276-329 contains only the three refusals. It has no unmutated AUTHORIZED leg under the same `_freshness` double.
  - A 1.9.1-era transaction-level AUTHORIZED control does exist: `test_clean_commit_exchanges_mapping_and_links_receipt`, 1.9.1 `tests/test_transaction.py:118`, S5 :148-151 (`prepared.decision == "AUTHORIZED"`). The design does not mention it.
- **Partly inherited.** The v1 review's own pointer (v1 REVIEW.md:101, "test_transaction.py:~300-330") was imprecise.
- **Why it matters.** As written, a reader could take OB-003's positive leg as already met by named controls. R-A and E5 are unaffected: E5 runs `test_transaction` and `test_typed_absence` whole.

**RC-4: CLOSED.**
- All three inventories are covered, with exact lines (DESIGN.md:169-181, :494). Verified:
  - `phase1-2026-10-02.json`: :2241/:2244 (`74a19597…`), :2276/:2279 (`76141dfb…`), :2456/:2459 (`53db45a0…`).
  - `phase1-bound-loader-2026-10-02.json`: :2407/:2410, :2452/:2455, :2632/:2635.
  - `phase1-native-lifetime-2026-10-03.json`: :2854-2855, :2890-2891.
- No `*.py`, `*.sh`, `*.gpr`, `*.json`, `*.toml` or `*.cfg` outside `assurance/checkpoints/` references them.

**Other changes versus v1** (full `diff` of the two DESIGN.md files):
- §0 is new.
- §5 changes wording only. Every verdict is unchanged.
- E5 adds `test_transaction` (:276-329) and `test_typed_absence` (:1238-1252). These are additive.
- E7's criterion changes from "No unresolved major findings" to "No unresolved required changes". This is not weaker.
- v1's §10 citation of WORKSPACE-RULES.md:7 is dropped. That line still requires gpt-6.1-sol, and the human's 17:05Z direction supersedes it (STATUS.md:279-291). The design records this rather than hiding it (DESIGN.md:524-528).
- The patch is byte-identical to v1's: equal sha256 values.
- No accepted case, assertion, criterion or control was removed.

## 1. Characterization
- **Correct.** At S5 candidate mode, every request built by the helpers has an absent Resulting (raw :71-75; fin :245-251; `checkpoint()` :530). On that basis:
  - `Required_Present` requires `Resulting_Requirement.Present` (`worldline-collapse.ads:149-151`);
  - `Evidence_Holds` requires `Same(Current, Resulting)` (:188);
  - `Post` gives Authorized ⇔ `All_Hold`, and nothing absent is ever authorized (:217-220);
  - `Same` is false on absence (`worldline-identities.ads:80-82`);
  - `Decide` returns EEI or Identity_Absent first (`collapse.adb:20-25`).
  - So AUTHORIZED is unreachable for A1–A4.
- **Cause correct.** The lineage hashes reproduce:
  - pre-item1 `53db45a0…`, V1 `979e4639…`, V2 `22b5b189…` (equal to S5's);
  - V2 HANDOFF.md:5 ("Valid checkpoint fixtures explicitly supply absence"; "no defaulting introduced") and :9 ("necessary valid-checkpoint fixture updates");
  - V1 HANDOFF.md:5 and :11 contain the quoted phrases.
- **OB-003's acceptance needs a positive case.** OBLIGATIONS-v2.json:95 does require a positive "1.9.1 control is AUTHORIZED". The design reads this correctly as a transaction-level control, not A1–A4. The named identity is wrong (RC-5).

## 2. Original intent
- **Supported.**
  - Pre-item1 had no Resulting field (ENG `worldline-collapse.ads` `ba6e2a53…`, per the design and the v1 review).
  - V1's fixture gives the candidate derivations `h(8)` = current.
  - V2 made checkpoint absence original only for checkpoint fixtures.
- **Further precedent in S5.** `test_revalidation_binding.py:303-316` derives from `RawDependencyControls.checkpoint()` in candidate mode. It explicitly supplies `resulting_requirement` (:315) equal to `current_requirement` (:314), the same pattern as R-A.

## 3. R-A preservation (reproduced)
- **Patch application.** `git apply --check` rc=0. Exactly one line changes per file.
- **Post-images:**
  - fin `76141dfb…` → `4da992dd…7327aa4`;
  - raw `22b5b189…` → `77f0cb99…ffad7262`;
  - both equal DESIGN.md:458-459.
- **Lines, methods and asserts unchanged:**
  - lines 289/289 and 561/561;
  - methods 26/26 and 43/43, same key sets;
  - only `FinalizationNativeControls.collapse_values` and `RawRequiredFailureControls.bound_request` change;
  - assert-call ASTs 38/38 and 62/62, identical and in order.
- **35-keyword equivalence.** The literal (raw :473-481) and `checkpoint()` (:525-533) both have 35 keywords over the same key set. Both define `h` identically (:472, :524).
  - Before R-A, the only difference is `resulting_requirement`.
  - After R-A, there is none.
- **Kernel, wire, ABI, contract and `checkpoint()` are untouched.** `checkpoint()` keeps None at raw :530, and the wire checkpoint rule is `collapse_wire.ads:132-136`.
- **Row :97-99 is handled.** Metadata is matched only after Authorized (`c_api.adb:862-868`).
- **Join safety.** The projection is built from the request itself (raw :67, fin :239). On the raw path the join precedes `Decide_Wire` (`c_api.adb:809-819`). So the :92-160 twins and lifetime :107-118 refuse at the join both before and after R-A.

## 4. Rejected options
- **Sound, and unchanged from v1.** No non-weakening option is missed.
- **R-D wording.** The fin :282-289 wording (it compares two calls, so it would pass vacuously rather than "refuse") is carried knowingly (DESIGN.md:58-60). The rejection stands.

## 5. Authority
- **Within the delegation.** RECOVERY-AND-AUTONOMY.txt:7 (`f0c36233…`) delegates "Routine engineering … that preserve the original external contract and success domain … Do not invent approval gates". STATUS.md:386-390 records it.
- **TEST_ONLY and reversible.** Two keyword arguments in two helpers. No API or contract change.
- **No gate added or lowered.** E7 is the original review requirement under the human's direction.

## 6. Closure plan
- **Complete.** E0–E7 cover:
  - matching-source runs;
  - all 14 REQUIRED-LIFETIME-CONTROLS (5 + 9, JACKAL above);
  - the OB-003 and typed-absence neighbours;
  - the full roster;
  - strict proof.
- **Frozen lanes are re-bound in their next revisions, never edited in place** (DESIGN.md:183-187, :495, :529-532).
  - Verified bindings: `packets/capi-pk0-v2/packet.json:198-199` and `claude-native-bigint-d1-design-v4/DESIGN.md:191`.
  - `packets/capi-pk0-v3/` holds only a `files` entry with no binding to either test file. `claude-native-bigint-d1-design-v5/` does not exist yet.
- **Everything listed in open_obligations remains open.**

## 7. Anything else
- I found no cap, domain narrowing, suppressed assertion or Ghost, added assumption or renamed readiness label.
- RC-5 is a fact-correction, not a gate.

## Required changes
- **RC-5.** Correct the identification of OB-003's "1.9.1 control" at DESIGN.md:80-85, :352-357 and :480.
  - The judge-mutation refusal family (S5 `test_transaction.py:276-329`) and `test_typed_absence.py:1238-1252` are post-1.9.1 additions. Neither is in 1.9.1 `tests/` or pre-item1 `ENG/source/tests`, and :1238-1252 is an item1-repair addition (item1-repair HANDOFF.md:34-36).
  - A 1.9.1-era transaction-level AUTHORIZED control exists: `test_clean_commit_exchanges_mapping_and_links_receipt`, 1.9.1 :118, S5 :148-151.
  - State that which control OB-003 means, and whether its positive leg holds under the same `_freshness` pass-through double, are not established here and stay part of the OPEN OB-003.
  - The conclusions stay as they are: the control is transaction-level, it is separate from A1–A4, and the two requirements are compatible.

## Non-blocking notes
1. **"S5 has three" inventories** (DESIGN.md:169). S5 `assurance/checkpoints/` holds eight files. Three record the patched files; the other five record none of them (JACKAL exact, parsed=8-3, exact=5). `phase1-native-lifetime-2026-10-03.json:1479` and :1483 also list the two test paths, without hashes.
2. **Live STATUS.md** has moved from the author's `ee2653d1…` to `24a309e5…`. The cited ranges :279-291, :323-324, :327-333, :348-354 and :386-390 still carry the cited text. :323-324 still says "Two original requirements conflict"; the design reclassifies it at :372-374.
3. **Roster cwd.** The roster launches record cwd `integrated-ordinary-v8/source` (ORIGINAL-ORDINARY-ROSTER.json:2182, :2207, :2382), and a parallel set records `full-formal-diagnostic-v7`. The roster has no lifetime launches. "Commands unchanged" (DESIGN.md:493) holds for argv. The design should say that cwd is re-targeted to the integrated candidate, consistent with :2604 `source_matching_rerun_required`.
4. **Null metadata on the raw path** (DESIGN.md:592-593, "unknown"). The bodies settle it statically. This is my unverified static reasoning; nothing was run.
   - `Metadata_Base(null)` returns Null (`evaluation_completion_c.adb:896-898`).
   - `Extent_Valid(Null, n>0)` is false (:258-265), so `Context_Matches` returns 255 (:751-757).
   - So `c_api.adb:810-812` returns Invalid_Request when P_Ready and Agent_Ready are 1. Otherwise the result is EEI.
   - Either way the result does not depend on Resulting, which supports "R-A does not change it".
5. **Un-routed derived count.** DESIGN.md:13 says no number was derived, but "collected three times" (:189) is a derived count. It is routed here (exact 3).
6. **R-D imprecision** for fin :282-289 is carried unchanged (DESIGN.md:58-60, :398).
