# PK-0 author notes

Packet PK-0 of the endorsed C-API boundary design: characterization only.
- Packet row: v3 DESIGN.md §9.2.
- Specification: v4 DESIGN.md §9.6, carried unchanged into v6. The v6 review (gpt61-v1, review.json `bcfa259f…d128`) endorsed it.

**Status: authored source, never run.**
- Nothing in this packet was executed, imported or compiled.
- The packet holds no run evidence and grants no control, proof or acceptance credit.
- The `json.load` and `ast.parse` checks in §8 are text inspection. As the review's IMPLEMENTATION_AND_STAGE_REVIEWS obligation says of B8, text or AST inspection supplies no control-run evidence.
- The PK-0 gate is a baseline run on L0 in an admitted frame. The confinement and capacity gates block that run now, so it remains open.

## 1. Base

L0 = `W/work/claude-composition-v5-beta/source`. Its identity as design §0 records it (v3 §0, carried by v4 §0):
- composition.json sha256 `a0e0bb5c…fa3e`;
- source-inventory.json sha256 `3407119b…937a`;
- review/gpt61-v1/review.json sha256 `df6cbc9d…3476`;
- disposition QUALIFIED_SOURCE_COMPOSITION, with proof, source and phase acceptance all false.

`sha256sum` re-observed the three full digests, which agree with those prefixes and suffixes. packet.json records them and the 95 S5 files the packet relies on.

None of the six target paths exists in L0, so no existing file is touched. The REQUIRED_PROVED prefix, the floor (`MINIMUM_CHECKS = 251`) and the boundary (`UNANALYZED_BOUNDARY = {"worldline-c_api"}`) are unchanged: nothing is appended, and the length stays 535.

S5 constraints the new modules respect:
- `tests/test_assurance_instrument.py:236-256` refuses pytest and requires every `test_*.py` to import under `unittest discover` (top level `tests`).
- The new modules use unittest only. At import they read JSON and nothing else.
- The library is chosen as most S5 tests choose it: `Core(Path(os.environ['WORLDLINE_CORE_LIB']))`, then `core._lib`.
- `tests/test_proof_source_inventory.py:64` inventories only `core/*.ad[bs]`, so new test files do not change it.

## 2. Method

1. I read every moving export's S5 body and spec, the relation specs behind its outcomes, its runtime ctypes binding and its S5 tests. I wrote down each guard conjunct with its line number.
   - A read-only script over the S5 text extracted the defined kinds and fields of the 25 staying layout functions. Its output matched my reading for all 25.
2. For each export, `tests/capi_characterization.json` records the defined effect per class (§9.6.1–§9.6.3): codes, frontiers, the canonical write order, the handler code, OPEN items, class X, and the unexercisable conjuncts with their reasons. It also records the cases, one JSON line each.
3. Each case names:
   - a builder (`test_capi_characterization.py`; most packers mirror the S5 runtime packers line for line, as cited in the comments);
   - mutations (`set`, `bytes`, `object`) that move the built call into one input class;
   - optional C-05 guard placement;
   - the expected code and exact writes.
4. Each expectation has one of three sources:
   - asserted by an S5 test (cited);
   - derived from a relation's contract or expression function (cited, with the derivation noted where a body is unproved);
   - `RECORD_ON_L0`.
   Every derived numeral went through JACKAL (`jackal.json`, J01–J27).
5. Every native call runs in a forked child (`capi_guard_pages.run_forked`). The parent requires a normal exit before it reads anything.
   - A fault fails the case. It is never mapped to a code (class X).
   - The child fills its whole mapping with 0xA5, places each object in its own page group and compares all readable bytes before and after the call. This gives "no byte outside the write set changed" on every unguarded case.
   - Output windows are compared field by field after decoding with the runtime ctypes type. Expected dicts must name every field (exact writes), and padding bytes inside a written record are not compared.

## 3. How each control is expressed

| Control | Where | How |
|---|---|---|
| C-01 | every unguarded R0/R1/R2 case and the no-write R3 cases (lifecycle statuses 0/1, protocol refusals, the raw post-decision 255) | All output windows are byte-identical after the call (0xA5 pre-fill; S5 mask bytes for the S5 lifecycle cases), and no byte of the mapping outside them changed. No case uses class H or X. |
| C-02 | U7c R3 (3 statuses), U7c S, U6 R3 | Ledger typed refusals zero both arenas and empty every descriptor over a 0xA5 pre-fill. The lifecycle mask is written only for statuses 2/3 (`a5` becomes `00`, or `0100`) and preserved for 0/1. |
| C-03 | ids `*_R0_*`, `*_R1_*`, `*_R2_*`, `*_C03_*` | At least one case for every exercisable guard conjunct; unexercisable ones are listed per export (`unexercisable`). Refused overlaps: U10/U11 Output vs Input/Data/Rows; U14 Output vs Input/Data/arrays; U14r Raw_Rows/Confinements vs Output; U14m metadata and captured rows vs the descriptor; U15f Output vs Input/Data/Required/Rows. Accepted overlaps: U3, U5 same buffer; U4 Output in Input and in Arena; U8 Result over Input; U12 Output in Input. |
| C-04 | U10–U15 R0/R1/R2 cases; `U14r_C04_operation_0/1`; `U14r_C04_post_decision_*`; `U15f_R3_op0_ignores_inputs` | Header and descriptor refusals; the raw `Operation /= 2` gate; the post-decision malformed-span 255 after every read and before any write. |
| C-05 | 58 cases with `guard` (ids `*_C05_*`, `U15f_C16_*_guard`) | In a child, PROT_NONE starts exactly where each frontier ends: `end` puts the last readable byte against a PROT_NONE page; `prefix` makes elements 1..k readable and k+1.. unreadable; `unreadable` covers absent or unneeded inputs. The case asserts a normal exit and the code only (R14). |
| C-06 | `test_capi_diagnostics.py`, 28 `diagnostic_cases` | A fresh child interpreter per case, with fd 2 captured whole. It covers control codes 0/1/2 (with U32'Last), double enable, invalid-while-active, stop without start, the failure latch (D06) and the exact line sequences of finalization decide, metadata matches and the mixed entry, including nested entries and value lines with Ada `'Image` spacing. |
| C-07 | `test_capi_layout_identity.test_c07_layout_sentinels` | Every undefined probed kind or field of the 24 staying layout exports with a sentinel (J27) returns the source sentinel (I64'Last J01, SIZE_MAX J03, -1). The row-size export takes no argument. |
| C-11 | U15x, 24 cases | R0 null/overflow collapse; R1 Invalid_Collapse (bad phase; checkpoint mode with Roster_Complete 1); invalid primary and staged kinds; nested kind 1/2 refusals; kind 2 with a non-seal request; kind 1 with Input_Invalid; agent extent, record and confinement refusals. Decision paths are compared with `wl_collapse_decide` on the same request with both roster flags cleared, and unneeded inputs sit on PROT_NONE pages. |
| C-12 | not authored | Optional. Class H is asserted by no case. |
| C-13 | `test_capi_layout_identity`, `capi_layout_baseline.json` | 15 version exports are asserted now (source constants). 25 layout exports over their probe domains, 82 ctypes records and 72 header types are compared with recorded values, all of which are RECORD_ON_L0. |
| C-14 | not encoded | Never a PK-0 pass condition. |
| C-15 | U14d_C15, 5 cases | Operation 1 with a short or long history gives History_Invalid, written with return 0 (D-18). Exact Retain_Terminal summaries (Completed/FAIL and Incomplete_Unknown) and the Already_Retained summary. |
| C-16 | U15f_C16, 4 cases | Operations 0 and 1 with Row_Count 3: unwritten rows (0xA5, which would refuse if read) give exactly the zero-row result, and rows on PROT_NONE give a normal exit and code 0. |

## 4. S5 lines relied on

Every case carries its own `s5` list, and every export entry carries its guard conjuncts with line numbers. In summary:

**Bodies and guards**
- resources `core/worldline-resources_c_api.adb:18-21, 36-65`
- recovery `core/worldline-recovery_c_api.adb:18-24, 53-86`
- v2 `core/worldline-recovery_authorization_c_api.adb:20-151`
- v3 `core/worldline-recovery_authorization_v3_c_api.adb:26-168`
- protocol `core/worldline-recovery_protocol_c_api.adb:17-71`
- lifecycle `core/worldline-reservation_lifecycle_c_api.adb:20-119`
- ledger `core/worldline-resource_ledger_c_api.adb:26-224`
- policy `core/worldline-resource_policy_c_api.adb:24-183`
- history `core/worldline-evaluation_history_c_api.adb:23-191`
- pending `core/evaluation_pending_c.adb:17-174` and `core/evaluation_pending_v2_c.adb:19-198`
- run ledger `core/resource_run_ledger_c_api.adb:24-223`
- chain `core/worldline-chain_authority_c_api.adb:19-103`
- completion `core/evaluation_completion_c.adb:39-88` (diagnostics), `:90-257, 258-392, 393-528, 529-693, 695-731, 871-986`
- finalization `core/evaluation_finalization_c.adb:34-257, 357-509, 510-567`
- collapse `core/worldline-c_api.adb:331-342` (oracle)

**Relations**
- `worldline-resource_wire.ads:6-16`, `worldline-resources.ads:28-52`
- `worldline-recovery.ads:18-38`
- `worldline-recovery_protocol{,_abi,_wire}.ads`
- `resource_reservation_lifecycle.ads:30-104`
- `resource_ledger.ads:20-264`
- `evaluation_pending.ads:34-165`, `evaluation_pending_v2.ads:12-88`, `evaluation_epoch.ads:13-22`
- `evaluation_completion.ads:98-433`, `worldline-evaluation_authority.ads:19-90, 142-273`
- `evaluation_raw_roster.ads:81-155`
- `evaluation_finalization.ads:32-135`
- `evaluation_history.ads:37-155`
- `worldline-collapse_wire.ads:71-136, 255-260`, `worldline-collapse.ads:166-169`
- `worldline-evaluation_wire.ads:18-70, 155-171`, `worldline-evaluation.ads:5-16`
- the run-ledger and chain wires' Well_Formed

**S5 tests whose assertions supply expectations**
- `test_recovery_witness_relation.py:24-60, 61-67, 181-218`
- `test_recovery_witness_relation_v3.py:24-61, 182-282`
- `test_recovery_protocol_native.py:10-24`
- `test_reservation_lifecycle.py:58-71`
- `test_resource_policy.py:42-100`
- `test_evaluation_history.py:23-57`
- `test_evaluation_pending.py:148-170`
- `test_evaluation_pending_requirements.py:30-56`
- `test_resource_run_ledger_v1.py:22-69`
- `test_chain_authority_native.py:15-34`
- `test_evaluation_roster_d2.py:30-36`

**Conventions**
- `tests/test_abi_layout.py`: compiler-probe precedent; a missing compiler is a failure.
- `scripts/assurance.py:236, 273`: runner and PYTHONPATH.

## 5. Placeholders that need a run on L0

All are written `RECORD_ON_L0`, and all fail until a reviewed change records the value printed by `--record`.

1. **C-13 layout export values**: all 25 layout exports over their probe domains (`capi_layout_baseline.json` `layout_exports[*].values`).
2. **C-13 ctypes layouts**: 82 runtime records (`ctypes[*].values`).
3. **C-13 header layouts**: 72 header types (`headers[*].values`), measured by a compiled probe.
4. **Unread write effects (cases)**:
   - `U14d_R3_classify_op2_record`: completion decide Operation 2 written result; code 0 is asserted.
   - `U15f_R3_capture_op2_record`: finalization Operation 2 written result; code 0 is asserted.
   - `U15f_R3_seal_op3_record`: finalization Operation 3 written result; code 0 is asserted.
5. **`D06_failure_latch`**:
   - the return of the first stop after a write to `/dev/full`;
   - the return of the final stop after fd 2 is restored;
   - the fd 2 lines.
   The latch relation (the second stop equals the first) and the start after the restore (0) are asserted now.

## 6. Uncertainties

1. **Derived expectations are predictions of L0, not observations.**
   - Some rest on bodies whose proof this packet does not establish. In particular `Evaluation_Epoch.Is_Successor` is declared unproved (`evaluation_epoch.ads:13-15`). Journal_Valid in the pending and completion expectations rests on it.
   - If the baseline run disagrees, the case fails. That is a finding. The record must not be edited to pass: a reviewed revision records the original behaviour, and any defect stays an original obligation.
   - If a case that expects code 0 on an accepted input sees 255, that is class H on an accepted input. It is never relabelled as an accepted refusal.
2. **ctypes and native layouts are assumed to agree.** The builders pack with the runtime ctypes classes, and the runtime bindings refuse a mismatched library at load. A disagreement would make cases fail rather than pass, and C-13 records each spelling separately.
3. **Overflow and misalignment cases rest on alignments and sizes read from the declarations.**
   - Records with 64-bit fields have alignment 8, and byte arrays have alignment 1.
   - `overflow` uses `2^64 - alignment` when an alignment test precedes the overflow test (Extent_Valid), and `2^64 - 1` where Shape precedes alignment (v2, v3, protocol, run ledger, chain, the mixed collapse and agent).
   - If a record's size were not larger than its alignment, the case would fail visibly.
4. **C-03 granularity.**
   - Each conjunct of each guard chain has a case.
   - For Extent_Valid and Array_Valid, the sub-conjuncts (null, misalignment, overflow, negative or oversized count, overlap) are covered fully for representative operands: Data, Journal, the fixed records. Other arrays get the null case, and the overlap case where an overlap rule exists.
   - Conjuncts that cannot be the sole failing one are listed under `unexercisable`, with the reason. Examples: equal 2^63-1 bounds checked twice; the ledger Quantity-stride bound behind the Row-stride bound; `Stride <= 0`; alignment-1 records.
5. **The C-11 decision oracle is relational.** Expected = `wl_collapse_decide` (bound with roster flags cleared), in the same child. A later change to `CW.Decide_Wire` itself would move both sides. The original roster tests (`test_abi_layout.py`, the collapse controls) cover that export.
6. **Probe domains.** U8 domains are complete. U32 domains are finite: 0 to one past the largest defined value, plus U32'Last.
7. **Fork.** A child forked from a process that other modules left multi-threaded could block on an inherited lock. The child imports nothing and logs nothing.
   - No timeout is set. A hang would be a hang, not a pass.
   - C-06 uses fresh interpreters through `subprocess.run`, also without a timeout.
8. **The header probe compiles with `-std=c11 -Wall` and without `-Werror`.** It is a measurement, so a header warning should not block recording it. This differs from `test_abi_layout.py`, which uses `-Werror` for `worldline_core.h`.
9. **D06 depends on how the GNAT runtime and libc behave on a failed write** (Device_Error from Text_IO, the stderr error flag). S5 does not determine this, hence the placeholders.
10. **Unread in this packet.** I did not read the B6 site tables in v4 A-BIND. The C-06 sequences are derived from the S5 bodies directly. The A-BIND counts (finalization Decide 9 = 4/4/1, Metadata_Matches 9 = 6/2/1, Decide_Mixed 16 = 11/4/1) match the marks, values and exception sites in those bodies.

## 7. Not expressible without a run

- Every C-13 value.
- The Operation 2 and 3 written results above.
- The D06 runtime-dependent values.
- Class H: failure location and copy atomicity (§9.6.4 a, b). These stay OPEN and are never expectations; C-12 is not authored.
- Native write construction and the preservation of possible outcomes (§9.6.4 c, d). These also stay OPEN.

## 8. Process record

**Tools**
- Write and Edit only, and only under `WT/packets/capi-pk0/`. No write was refused.
- No mkdir, cp, mv, rm, tee, chmod, touch or redirection was used. `Write` created the directories.

**Bash, read-only throughout**
- `cat`, `sed -n`, `grep`, `awk`, `find`, `ls` (an eza alias), `wc`, `sha256sum`, `head`, `cd`, `df -h`, `getconf PAGESIZE`, `uname -m`, `python3 --version`.
- Python heredoc scripts that read files and print: `json.load`, `ast.parse`, `hashlib`, and regex scans of S5 text.
- Before the context compaction, one `ls tests | grep -i polic` ran on an S5 subpath.
- No command touched `/home/sicarii` itself, `~/iPad`, `~/iPadBackup` or `~/.local/share/sia/.gbrain/`.

**Nothing executed**
- No WORLDLINE code was imported or run.
- No test, pytest, compiler, gprbuild, prover, native build, systemctl, sudo, project-vault or restic.
- None of this packet's code was imported or run.
- No TaskStop, kill, timeout wrapper or background task. Nothing was interrupted.

**Other services**
- SIA: one `sia.ask` at the start of the task (before compaction). No note was written.
- JACKAL: 27 `jackal_exact` calls in eight sequential groups of at most four (`jackal.json`). Each returned status exact, formal false, lane rat, evaluator `4c0ae28d…d872`.

**Verification (text only)**
- Every JSON file loads.
- Every Python file parses.
- The characterization record has 609 unique case ids and 28 diagnostic cases.
- Every diagnostic `call` names an existing unguarded case.
- Every refusal case's code equals its class code.
- These are author checks and grant nothing.

**Deviations from the brief:** none.
