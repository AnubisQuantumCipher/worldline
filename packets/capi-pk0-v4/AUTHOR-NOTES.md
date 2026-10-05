# PK-0 v4 author notes

PK-0 v4 revises the C-API characterization packet PK-0 in answer to the sealed source review of v3.
- Review: `packets/capi-pk0-v3/review/claude-v1`, an independent Claude review subagent (human direction of 2026-10-05). This changes nothing that the packet must satisfy.
- Verdict: ENDORSED_WITH_REQUIRED_CHANGES. RC-v2-2, RC-v2-3 and RC-v2-4 CLOSED_IN_SOURCE; RC-v2-1 PARTIALLY_CLOSED; new required changes RC-v3-1 and RC-v3-2; two recommendations. No run, control, proof, phase or source acceptance is granted.
- v1, v2 and v3 (`packets/capi-pk0/`, `-v2/`, `-v3/`) are unchanged. v4 is a new directory with the same layout: `packet.json`, `files/tests/*`, this file and `jackal.json`.

**Status: authored source, never run.**
- Nothing in this packet was executed, imported or compiled. It holds no run evidence and grants no control, proof or acceptance credit.
- The `json.load` and `ast.parse` checks in section 9 are text inspection only.
- The gate is unchanged: a baseline run on L0 in an admitted frame. It is blocked by the confinement gate (V5-B01, V5-B02) and the capacity gate.

## 1. Review identity

`sha256sum` (read-only) over `packets/capi-pk0-v3/review/claude-v1/` gave these values. The first three equal the entries of `review-freeze.json`. Only REVIEW.md and review.json were read for content; `raw-final-message.txt` and `review-records/` were not used.

| File | sha256 | bytes |
|---|---|---|
| REVIEW.md | `302a3dddefddae09d1619c940c7c328efb71a1dbd0efb7f1b2a7422fc91d855f` | 26159 |
| review.json | `1a7b8fbbef76a3bf60f857d50c240405c14c16bb6626a8955cfe998a77e82109` | 8537 |
| checks.json | `6bffe9ee8a8c9d3448ca68d8bc7dae9b9a05c46ed188a66650d276f978b170b1` | 9749 |
| review-freeze.json | `af7ed675faa4de06e7fa1702e923cb7d69aea9b1c028b78e9dc00e20e265f920` | 612 |

## 2. Base and invariants (unchanged)

L0 is `W/work/claude-composition-v5-beta/source`. Its three identity files were re-observed and are unchanged:
- composition.json `a0e0bb5c…fa3e`;
- source-inventory.json `3407119b…937a`;
- review/gpt61-v1/review.json `df6cbc9d…3476`.

Invariants:
- REQUIRED_PROVED: 0 names appended; the 535-name prefix is carried (not recounted).
- `MINIMUM_CHECKS = 251` and `UNANALYZED_BOUNDARY = {"worldline-c_api"}`, re-read at `runtime/worldline/proof_manifest.py:22` and `:316`.
- 31 lines of `core/worldline-c_api.ads` contain External_Name (re-counted with `grep -c`).
- Movers: 0. No existing file is touched. None of the six payload paths exists in L0 (re-checked with `test -e`).

Bound inputs:
- All 100 v3 bound inputs were re-hashed. None differs in sha256 or size.
- v4 adds none. Every S5 path cited by the v4 record, `jackal.json` and the modules is already bound (checked by script); the new citations are `core/evaluation_completion_c.adb`, `runtime/worldline/completion_kernel.py` and `runtime/worldline/evaluation_context.py`, all bound since v1 or v2.
- The two host headers were re-hashed and are unchanged.

## 3. Answers to the required changes

### RC-v3-1: the Kind 1 overlap of R.Captured_Results and R.Required with the descriptor

**The v3 OPEN reason was wrong, and is withdrawn.** v3 (REC:393 and AUTHOR-NOTES.md:106) said an overlap would put fixture row bytes into descriptor words that the earlier transport conjuncts "through X.Agent and X.Agent_Confinement" must accept. That misread the conjunct order. In `core/evaluation_completion_c.adb`:
- CC:777-778 (the two request-array overlaps) are evaluated before CC:780 (X.Agent and X.Agent_Confinement).
- CC:765-776 read X.Version, X.Data and X.Data_Length, the counts, X.Policy, X.Expected_Binding, X.Expected_Current, X.Prepared_Current, X.Rows and X.Required. They never read X.Expected, X.Observed or X.Projection.
- Raw_Decide's own address checks are only against its own Output (CC:538-556), so moving the rows, unchanged, inside the descriptor leaves readiness 1.

So the rows can sit in the Expected/Observed region, and CC:777 (or CC:778) is the first conjunct that fails.

**Two new cases, each with a twin and a stream.**

| Conjunct | Case suffix | Placement | D-case |
|---|---|---|---|
| `Array_Valid (R.Captured_Results, …, Context, CS)` (`:777`) | `context_captured_overlap` | the request's two captured rows copied into [Expected, Rows) of the descriptor; `p_input.captured_results` pointed at the copy | D88 |
| `Array_Valid (R.Required, …, Context, CS)` (`:778`) | `context_request_required_overlap` | the request's one required row copied into the same region; `p_input.required` pointed at the copy | D89 |

**How the placement is made: the `embed` mutation** (`test_capi_characterization.py`, CHAR:1277-1278 and CHAR:1283-1330).
- It takes the region's bounds from the library's own layout export: `wl_completion_context_layout_v1 (1, 8)` (X.Expected'Position) and `(1, 10)` (X.Rows'Position), read at CC:695-720.
- It requires those two answers to equal the ctypes offsets of `expected` and `rows` in S5's `ContextInput`.
- It also requires:
  - that the request's pointer field currently names the source array;
  - that the count field is positive and the source holds that many elements;
  - that the bytes fit the region, and the region start and the descriptor's alignment are multiples of the element alignment.
- It copies the bytes unchanged into the adopted descriptor at the region start, and points the request field there with `to(name, offset)`.
- If any condition fails, it raises PlacementError, so the case fails.

**Layout offsets are predictions.** The source-derived LP64 layout puts Expected at byte 208 and Rows at byte 880, a 672-byte region (J43-J46). Two 304-byte Check_Rows take 608 bytes, leaving 64 bytes of slack (J47-J50). One 32-byte Required_Row fits (J51).
- These numbers are stated in each case's `provenance`. The cases do not use them.
- The cases use the measured answers. A measured layout that differs from the prediction fails visibly as a PlacementError (C-13), and never silently passes or places the bytes elsewhere.
- S5's own attach already compares the ctypes layout with the same export (CONTEXT_OFFSET_MISMATCH).

**Twins and streams.**
- Each twin puts the context arena, the context rows and plans, and the metadata arena and rows on PROT_NONE.
- D88 and D89 use the exact transport stream (`completion.context.enter`, then `completion.context.transport-guard-rejected`, then `finalization.mixed.primary-context-rejected`).
- The embed runs in the diagnostic children too, because they call `T.mutate` with the library.

**Record changes.**
- `nested_conjuncts` maps CC:777 and CC:778 to the two cases.
- The `not_exercised` OPEN item is removed, and so is v3 deviation 2.
- The Kind 2 overlap stays in `unexercisable`, with its reason: the arrays are Ada locals of Final_Context_Matches, which is class X.

### RC-v3-2: the reachable sub-conjuncts, and the completeness claims

**Fourteen new nested refusals.** All are Kind 1 primary with ready sources and an admitted Agent-origin record, and all expect 255 at primary-context-rejected. Each has a guarded C-05 twin and an exact C-06 stream.

| Sub-conjunct | Case suffix | Mutation | D-case |
|---|---|---|---|
| Metadata_Base `Extent_Valid (Context)` misaligned (`:896-898`) | `metadata_misaligned` | Metadata argument one byte past `p_meta` | D76 |
| the same, address overflow | `metadata_overflow` | aligned Metadata argument whose extent passes the top of the address space | D77 |
| Metadata_Base `Extent_Valid (X.Base)` misaligned (`:901-903`) | `metadata_base_misaligned` | `p_meta.base` one byte past the descriptor | D78 |
| the same, address overflow | `metadata_base_overflow` | aligned `p_meta.base` overflowing | D79 |
| `Extent_Valid (X.Data)` null with nonzero length (`:766`) | `context_data_null` | `p_meta_base.data` null | D80 |
| the same, address overflow | `context_data_overflow` | `p_meta_base.data` overflowing | D81 |
| `Valid (X.Expected_Current)` present, invalid Sequence (`:773`) | `context_expected_current_sequence` | Sequence.First 0 | D82 |
| the same, invalid Run | `context_expected_current_run` | Run.First 0 | D83 |
| `Valid (X.Prepared_Current)` present, invalid Sequence (`:774`) | `context_prepared_current_sequence` | Sequence.First 0 | D84 |
| the same, invalid Run | `context_prepared_current_run` | Run.First 0 | D85 |
| `Array_Valid (X.Rows)` misaligned (`:776`) | `context_rows_misaligned` | Rows one byte past the context rows | D86 |
| the same, address overflow | `context_rows_overflow` | aligned Rows overflowing | D87 |
| `Array_Valid (X.Required)` misaligned (`:779`) | `context_required_misaligned` | Required one byte past the context plans | D90 |
| the same, address overflow | `context_required_overflow` | aligned Required overflowing | D91 |

- With the two RC-v3-1 cases, that makes 16 new refusals (J64): 4 Metadata_Base and 12 transport (J63). With their 16 twins, that makes 32 new cases (J62), and the refusals have D76-D91.
- The Metadata_Base cases end in `completion.context.input-extents-rejected`, because Context_Matches receives Null. Their twins also put the Metadata_Context record (`p_meta`, for the argument cases) or the descriptor (`p_meta_base`, for the Base cases) on PROT_NONE, because the refused extent is never read.
- The transport cases end in `completion.context.transport-guard-rejected`.

**Every other sub-conjunct is now accounted for by name, in one of three places.**

`unexercisable`, each with its source reason. New in v4:
- Extent_Valid's Length >= 0, Alignment > 0 and Length <= Storage_Offset'Last at Metadata_Base and at the Context_Matches input extents: Length and Alignment there are constants.
- X.Data misalignment (Byte'Alignment is 1) and X.Data's Length bound (an I64; J01).
- The count and stride sub-conditions of `Array_Valid (X.Rows)` and `Array_Valid (X.Required)` (see the recommendation below).

`representative_operands`, a new list with five entries, each naming the case that exercises the same predicate and the reason:
- the five Span fields and one Optional_Span of `Valid (Binding)`;
- the First >= 1 and Length >= 0 branches of `Valid (Span)`;
- the Present and value branches of `Valid (Optional_Span)`;
- the per-field sub-conditions of `Valid (Check_Row)`;
- element positions beyond the first.

`not_exercised` keeps only the Metadata_Matches transport item, with its own reason (covered at its own export, U14m).

**The completeness claims are corrected.**
- C-03 now says that every exercisable sub-conjunct of the extent, array and cursor tests has a case (null, misalignment, address overflow, refused overlap, each span of a cursor). Every other conjunct or sub-conjunct is listed under `unexercisable`, `representative_operands` or `not_exercised`.
- The `nested_conjuncts` note says the same, and each table entry now names its sub-conjunct cases.
- C-06 now cites D29-D91.

### Recommendations taken

1. **The class-X stride premise is stated** (v3 REC:388, now REC:391).
   - A count that fails the X.Rows stride bound exceeds (2^63-1)/688 rows, against a source-derived Context_Row of 688 bytes (J52).
   - The nested Raw_Decide (Kind 1) or finalization Decide (Kind 2) reads every such row before readiness is set. So the row array would be a live, readable object of more than 2^52 bytes (J55). For 304-byte Kind 1 rows the size is more than 2^52 but less than 2^64 (J53-J54).
   - The entry is class X under two stated premises: a virtual-address width of at most 52 bits (aarch64 Linux user space), and every array an input names being live and readable for its declared extent. It is not a consequence of the 64-bit Integer_Address range.
2. **`test_record_shape` checks readiness sides against the shape.** For every child-built case, the declared readiness keys other than `agent` must equal the sides the shape needs: `primary` → {primary}, `staged` → {staged}, `both` → {primary, staged} (CHAR:1634-1639).

## 4. Change list against v3

`packet.json` lists each file with its v3 and v4 sha256 and bytes.

| File | Change |
|---|---|
| `capi_characterization.json` | `design.revision`; C-03 and C-06 text (RC-v3-1, RC-v3-2). The mixed entry: `nested_conjuncts` note and entries gain the new cases; `unexercisable` gains the constant-length, X.Data and generalized stride entries (stride premise stated); new `representative_operands`; the OPEN `not_exercised` item removed. 32 U15y cases (16 refusals, 16 twins; J62) and 16 diagnostic cases (D76-D91; J57) appended. By JSON comparison, all 693 v3 cases and all 75 v3 diagnostic cases are unchanged in content and order, and so are the other 19 export entries and the mixed entry's classes, `join_frontiers` and `no_twin`. |
| `test_capi_characterization.py` | Docstring revision v4. `mutate` accepts `embed`. New `embed` (RC-v3-1). `test_record_shape` checks readiness sides against the shape (recommendation). Nothing else changes. |
| `capi_guard_pages.py`, `test_capi_diagnostics.py`, `test_capi_layout_identity.py`, `capi_layout_baseline.json` | Unchanged (byte-identical to v3, checked with `cmp`). |
| `jackal.json` | J01-J42 carried (J32 and J42 gain an `also_used_in_v4` note); J43-J64 added. |
| `AUTHOR-NOTES.md`, `packet.json` | Rewritten for v4. |

## 5. Placeholders (RECORD_ON_L0; none can pass)

These are unchanged from v3:
- the 179 layout values (J33);
- the written results of U14d_R3_classify_op2_record, U15f_R3_capture_op2_record and U15f_R3_seal_op3_record;
- D06.

v4 adds no placeholder. The count of RECORD_ON_L0 occurrences in the record is the same as in v3. Every new expectation is derived from the source. The two layout-dependent placements read their bounds from the library at run time and fail on a mismatch.

## 6. F32-CONFLICT: not decided

- Every new U15y request keeps the Resulting_Requirement = Current_Requirement shape of S5's own positive control, `test_collapse_recomputes_carried_roster` (`test_raw_evaluation_default.py:471-490`).
- No case asserts a decision code for the exact S5 request with Resulting_Requirement absent.
- No S5 test or original control is edited.

## 7. Uncertainties (in addition to v3's, which stand)

1. The overflow cases on `p_meta_base_data` use the harness default `back` (the object's alignment, 1 for a byte arena). They need the fixture's context arena to be longer than one byte. If it is not, the case returns something other than 255 and fails visibly.
2. The misaligned cases need the element alignment of Context_Row, Required_Row, Metadata_Context and Context_Input to exceed one byte. Their ctypes declarations hold 64-bit fields; S5's attach compares the alignment with the library's layout export. If the alignment were 1, the case would fail visibly.
3. The embed cases assume the adopted descriptor `p_meta_base` is a ctypes Structure whose type is S5's `ContextInput`, so that its `expected` and `rows` field descriptors give the ctypes offsets. A different adoption fails the case as an AttributeError or a PlacementError.

## 8. Deviations

1. Carried: the review is by an independent Claude review subagent (human direction of 2026-10-05). This packet takes no position on the model-identity question the review records.
2. Removed in v4. v3's deviation 2, the unconstructed Kind 1 overlap, is closed by RC-v3-1. The remaining numbers are kept so that references stay stable.
3. Carried: readiness is observed by a separate per-case probe, not by the oracle prelude.
4. Carried: three element-guard conjuncts were added in v3 beyond the letter of RC-v2-1.
5. Carried from v2: the U15y requests add Resulting_Requirement (§6). The header test requires the scratch binding. Launch obligations remain OPEN.
6. **New.** RC-v3-1 asks for "a builder delta before _adopt". v4 instead places the bytes with a post-adopt mutation (`embed`).
   - The effect is the same: the accepted row bytes, unchanged, are inside the adopted descriptor copy, and the request field names them through `to(name, offset)`.
   - The mutation form is what lets the bounds come from the library's measured layout rather than from the ctypes alone, so a differing layout fails visibly.
   - It applies identically in the C-06 children.
   - No builder changes.
7. **New.** v4 goes beyond the letter of RC-v3-2, so that C-03 is not narrowed by omission:
   - address-overflow cases for X.Data, X.Rows and X.Required (the review listed null for X.Data and misalignment for X.Rows and X.Required);
   - a separate Sequence and Run case for each of the two cursors.
8. **New, process.** No `sia.ask` was made when v4 began; one was made late, before hand-back. After a compaction during v4, four short CC excerpts were re-read before the eight Ada skills were reloaded (§9).

## 9. Process record

**Writes.** Write and Edit only, only under `WT/packets/capi-pk0-v4/`. No write was refused.
- The four unchanged files were written byte-identical and compared with `cmp`.
- The record was built by Write followed by Edit appends. After each append, the reproduced v3 text was compared with `diff` against v3; every comparison printed no difference.

**Bash, read-only.** `sha256sum`, `sed -n`, `grep`, `wc`, `test -e`, `cmp`, `diff`, and Python heredoc scripts that only read and print (`json.load`, `ast.parse`, `hashlib`). No redirection, mkdir, cp, mv, rm, tee, chmod or touch. Nothing touched `/home/sicarii` itself, `~/iPad`, `~/iPadBackup` or `.gbrain`.
- My own subagent transcript was read only at the permitted path, to recover pre-compaction context.
- No other transcript and no `review-records/` file was read.

**Nothing executed or interrupted.**
- No test, pytest, WORLDLINE module, packet module, compiler, prover or native build was run or imported.
- No TaskStop, kill, timeout wrapper or background task was used.

**Services.**
- SIA, recorded as a process lapse: no `sia.ask` was made when v4 began. The last one was at the start of v3, in the same agent session. One `sia.ask` was made late, after drafting and before hand-back. It returned only model-origin design notes from 2026-10-04 and nothing on v4. Its boundary line was: senses live, chains pass, graph complete, semantic recall, and absence of recall is not evidence of absence. No note was written.
- JACKAL:
  - J43-J64 were called in seven sequential groups of at most four (15-21), with literal exponents. Each is exact, formal false, lane rat, evaluator `4c0ae28d…d872`.
  - J01-J42 are carried.
- Ada skills:
  - All eight were loaded during v3, after a compaction, and were still in context when v4 began. They were not reloaded then.
  - After a context compaction during v4, four short excerpts of `core/evaluation_completion_c.adb` were re-read (CC:255-290, :695-736, :745-790, :890-908) before the eight were reloaded. All eight were then reloaded before this note was written.
  - This ordering is recorded as a process lapse. No Ada source is changed by the packet.

**Verification, by text only.**
- Every JSON file loads and every Python file parses.
- 725 cases (J56) with unique ids, and 91 diagnostic cases (J57).
- All 693 v3 cases and all 75 v3 diagnostic cases are identical in content and order.
- Every diagnostic call names an existing case. All 63 unguarded U15y cases have a D-case (J58). There are 53 guarded U15y cases (J59) and 111 guarded cases in all (J60). There are 116 U15y cases, each declaring readiness (J61).
- Every new guard name is one that v3's guards already use, and so one that `_adopt` derives.
- Every child-built case declares readiness for exactly its needed sides plus the agent.
- Every U15y refusal has a twin with the same build, mutation and expectation, or is listed in `no_twin`. `no_twin` is unchanged at 7 (J42).
- Every case id that `nested_conjuncts`, `unexercisable`, `representative_operands`, `not_exercised` and `no_twin` cite exists. Every D-number they cite exists.
- RECORD_ON_L0 occurs as often as in v3.
