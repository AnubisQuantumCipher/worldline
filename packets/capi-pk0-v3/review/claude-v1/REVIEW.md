# WORLDLINE Phase One C-API PK-0 v3: independent source review

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**

This is a passive source review of PK-0 revision 3. It grants nothing: no source acceptance, run evidence, control evidence, proof acceptance, stage qualification or Phase One acceptance.

The PK-0 stage gate is a baseline run on L0 in an admitted frame. That run, its recorded values, the six launch obligations and any stage qualification remain **OPEN**. Frame v5 is UNQUALIFIED. V5-B01, V5-B02 and the capacity gate block execution (`packet.json:6`).

**Reviewer.** An independent Claude Code review subagent (claude-opus-5-5) with a fresh context. It authored nothing under review.
- The lead's override file (sha256 `bdb0815d…0b00`) replaces the brief's "actual gpt-6.1-sol" with this reviewer.
- The original requirement texts say every required independent review uses actual gpt-6.1-sol, and that a Claude review cannot count as that gate (`W/outputs/claude-phase1-handoff-20261004/HANDOFF.md:173`; `/home/sicarii/Documents/complete-phase1-prompt.txt:60`).
- This review records that conflict and does not decide it.

**Brief:** sha256 `4732d70ea1aef59794a77feb5a9a1e37888783f33a7b4a3576ebdfbc32752d60`.

**What was and was not done.**
- No packet module, helper, S5 test or fixture, WORLDLINE library, compiler or prover was imported or run.
- Python was read as text. The only processing was `ast.parse` and `json.load`.
- No review directory of v3, review-records path or session transcript was read.
- All eight Ada skills were loaded before the Ada bodies were read.

**Citation roots.**
- P = `WT/packets/capi-pk0-v3`; P2 = `WT/packets/capi-pk0-v2`; P1 = `WT/packets/capi-pk0`.
- S5 = `W/work/claude-composition-v5-beta/source`; W = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`; WT = `W/work/claude-lead-isolation-v1/wt-1`.
- CHAR, GP, DIAG, LAY and REC are P's `files/tests/` files: test_capi_characterization.py, capi_guard_pages.py, test_capi_diagnostics.py, test_capi_layout_identity.py and capi_characterization.json.
- CC = `S5/core/evaluation_completion_c.adb`; FC = `S5/core/evaluation_finalization_c.adb`.

## 1. Packet integrity and invariants

**Finding: the identities hold; the payload is additive; v1 and v2 are unchanged; the change list against v2 is exact.**

- **Packet files.** All nine sha256 values equal the brief. The six payload hashes and byte counts equal `packet.json:43-48`.
- **Change list against v2.** Every v2 and v3 sha256/byte pair in `packet.json:52-60` matches the files.
  - capi_layout_baseline.json is byte-identical to v2.
- **v1 and v2 unchanged.**
  - The P1 files equal `P2/packet.json` change_list_against_v1.
  - P2's six payload and two packet files equal P2's own manifest.
  - P2's packet.json is `c5ce00cd…2032d`.
  - The sealed v2 review files equal its review-freeze.json: REVIEW.md `0246243a…`, review.json `d42e962d…`, checks.json `432c3a40…`. These also equal `packet.json:12-15`.
  - The v1 review equals its freeze: REVIEW.md `7d86d533…`, review.json `fc615b5b…`.
- **Bound inputs.**
  - All 100 entries (`packet.json:98-199`) have distinct paths and match S5 in sha256 and size.
  - The list equals v2's, in order.
  - The two host headers match (`packet.json:202-203`).
  - The base identities match (`packet.json:37-39`). The v6 review.json `bcfa259f…` and REVIEW.md `12cfde3c…` match `packet.json:28-29`.
- **No existing file touched.** None of the six payload paths exists in S5 (`packet.json:62`).
- **Cases carried, by JSON comparison.**
  - REC's first 609 cases equal P1's. REC's first 655 cases equal P2's once `expect.readiness` is removed.
  - Exactly the 46 v2 U15y cases differ, and only by the added key `readiness`.
  - The first 55 diagnostic cases equal P2's, and the first 28 equal P1's, in order.
  - In text, D55's line differs only by an added trailing comma.
  - The changed keys are `design.revision`, controls C-03, C-05, C-06 and C-11, and four keys of the mixed export: `nested_conjuncts` and `no_twin` (new), and `unexercisable` and `not_exercised`. Every v2 `unexercisable` entry is retained.
  - The other 19 exports and the mixed entry's `classes` are equal.
  - The 38 new U15y cases and D56–D75 are appended. Case ids are unique.
- **jackal.json.** J01–J33 and common_result are equal to v2 apart from the `also_used_in_v3` notes on J04, J32 and J33. J34–J42 are new.

| Invariant | Observation | Evidence |
|---|---|---|
| REQUIRED_PROVED | AST segments 280, 11, 4, 5, 8, 31, 34, 46, 1, 115; 535 unique of 535; nothing appended | `S5/runtime/worldline/proof_manifest.py:25,312,314,924,940,953,967,972,1003,1012` |
| MINIMUM_CHECKS | 251 | `proof_manifest.py:22` |
| UNANALYZED_BOUNDARY | `{"worldline-c_api"}` | `proof_manifest.py:316` |
| Movers | 0 | `packet.json:68` |
| External_Name lines in worldline-c_api.ads | 31 (grep -c) | `S5/core/worldline-c_api.ads` |

**JACKAL results** (all lane rat, formal=false, assurance "exact rational arithmetic (not yet checker-covered)"):
- `parsed=280+11+4+5+8+31+34+46+1+115` gives **status=exact**, exact=535.
- The cross-checks are also **exact**: `609+46+38`=693 cases; `28+27+20`=75 diagnostic cases; `27+18+2`=47 unguarded U15y cases; `58+19+18`=95 guarded cases.
- Non_claims on every call: "NOT formal-bounded: this lane carries no Lean-checked certificate"; "The epistemic class above is the STRONGEST claim this result supports"; "exact rational arithmetic (not yet checker-covered)".
- This arithmetic is informational only.

## 2. Closure of RC-v2-1 to RC-v2-4 (PK0-RC4 and PK0-RC5)

| RC | Ruling | Remaining gap |
|---|---|---|
| RC-v2-1 | **PARTIALLY_CLOSED** | (a) The Kind 1 refused overlap of the request arrays with the descriptor is constructible, and the OPEN reason is factually wrong (RC-v3-1). (b) `nested_conjuncts` is incomplete at the packet's own C-03 granularity, yet claims to list every other conjunct (RC-v3-2). |
| RC-v2-2 | CLOSED_IN_SOURCE | None in source. |
| RC-v2-3 | CLOSED_IN_SOURCE | None in source. The normal header test is ungated by design and qualified under launch obligation 1. |
| RC-v2-4 | CLOSED_IN_SOURCE | None in source. "Every path" means every path on which `run_forked` returns. |
| PK0-RC4 | CLOSED_IN_SOURCE (unchanged) | DIAG changed only in its docstring (DIAG:4, :33). D06 stays RECORD_ON_L0. |
| PK0-RC5 | CLOSED_IN_SOURCE (unchanged) | The boundary statements now include the probe (GP:13-18; CHAR:34-40). |

### 2.1 RC-v2-1: what is correct

**C-03 text restored.** REC:56 again says "One case per exercisable guard conjunct", as in v1 (`P1` REC C-03). The "nested guard group" relaxation is gone. Context/descriptor overlaps are added for U15y.

**Every new case checked against the bodies (all 18 refusals, 18 twins, D56–D75).**

| Case / D | Body evidence | Code, frontier, twin, stream |
|---|---|---|
| metadata_version / D56 | `X.Version /= 1` returns Null (CC:901-903). Context_Matches(Null) fails `Extent_Valid (Context)` (CC:752) and gives input-extents-rejected (CC:756), then primary-context-rejected (FC:474-477). | 255. The twin's PROT_NONE `p_meta_base` is never read; Metadata_Base only extent-checks Base. Stream matches. |
| metadata_base_null / D57 | Base Null fails Extent_Valid (CC:901-903). | Same as D56. Matches. |
| context_version / D58 | `X.Version` is the first conjunct (CC:765). | 255 at transport-guard-rejected (CC:782). The twin's arenas, rows and required arrays are unread before CC:787. Matches. |
| context_data_extent / D59 | Data_Length -1 fails `Length >= 0` (CC:260, :766). The earlier conjuncts hold. | Matches. |
| context_row_count / D60 | The fixture has two captured rows (`S5/tests/test_raw_evaluation_default.py:79-80`). Row_Count 0 differs (CC:767). | Matches. |
| context_required_count / D61 | One required row on each side (`test_raw_evaluation_default.py:33,66`). Required_Count 0 (CC:768). | Matches. |
| context_policy / D62 | U32_MAX > Declaration'Last (CC:769). J04 is carried. | Matches. |
| expected_binding, expected_current, prepared_current / D63–D65 | Store_Id.First 0 fails `Valid (Span)` (CC:279, :285-287). Present 2 fails `Valid (Cursor)` (CC:282-284). Checked at CC:773-774. | Matches. |
| rows_extent, rows_overlap / D66–D67 | Null with count 2 fails Extent_Valid. Rows at offset 0 of the descriptor fails Disjoint against (Context, CS) (CC:266-278, :776). | Matches. |
| required_extent, required_overlap / D68–D69 | As above at CC:779. CC:777-778 hold because the fixture's request arrays are separate objects. | Matches. |
| context_agent / D70 | The context's agent comes from `agent.native()` (`S5/runtime/worldline/evaluation_context.py:184-186`). Observation 0 is Source_Field (`S5/core/worldline-evaluation_wire.ads:20`). Setting it to 0 makes `X.Agent /= Raw_Agent` (CC:780). The admitted argument is unchanged. | Matches. |
| field_observed / D71 | The fixture's observed fields are a copy of the expected fields, all Present 1 (`test_raw_evaluation_default.py:51-56`). The K=0 Observed value First 0 is invalid (CC:796). | field-rejected value 0 (CC:798-799). The twin keeps the data arena readable (copied at CC:788). Matches. |
| row_field_expected / D72 | The row pairs are all None, so Present is 0 (`:57-58`). Present 2 at row 1, K=0 (CC:821). | row-field-row=1, row-field-rejected=0 (CC:822-824). Twin prefix 1. Matches. |
| required_declared / D73 | Original valid and Owned.Check_Id valid; Owned.Declared.First 0 (CC:839-840). | required-rejected=1. Matches. |
| both_k1_primary_authorized / D74 | Read_Ready: Kind 1 emits nothing, Kind 2 Decide emits four lines (FC:127,158,247-248). Agent readiness. Primary Kind 1 context join; staged Final_Context_Matches with its context and metadata joins (FC:272-346). Decision 0. Primary Kind-1 metadata join (FC:491-496). No staged metadata join for Kind 2. | Code 0; every line and its order match. |
| both_k1k1_staged_metadata_payload / D75 | Two context joins, decision 0, primary metadata 1, staged metadata 0, then staged-metadata-rejected (FC:497-501). | Matches. |

- No new expectation is a placeholder, a class-H code or a weakened value.
- Every R1 case expects 255 = Invalid_Request, the defined R1 code (REC:320-321).

**Twins and records, checked by script.**
- 47 unguarded U15y cases each have a D-case.
- 39 unguarded refusals each have a twin or a `no_twin` entry.
- No `no_twin` case has a twin.
- Each twin's build, mut and expect equal its base case.
- Every case id and D-number cited by `nested_conjuncts`, `unexercisable`, `not_exercised` and `no_twin` exists, and each cited D-case calls its case.
- The seven `no_twin` reasons are correct against CC:929-978 and FC:339-346 and :491-502.

**Unexercisable entries: correct as reasoned.**
- **Context_Matches extents.**
  - Input: Raw_Decide uses the same Request size and alignment (CC:538 vs :751).
  - Collapse: FC:412-414 vs CC:753.
  - Agent: FC:453-458 and :473 vs CC:754.
- **Non-null bad Context.** Metadata_Base returns Null or an address checked with CS and Context_Input'Alignment (CC:901-904).
- **R-side transport, Kind 1.** Raw_Decide refuses the same bytes (CC:545-546, :558, :560).
- **R-side transport, Kind 2.** The projection is built from constants and Decide-validated fields (FC:319-331, :138-153). Captured.State has subtype `E.Terminal_State` (`S5/core/evaluation_raw_roster.ads:31-35`; `S5/core/worldline-evaluation.ads:5-12`).
- **Request-side row validity.** Kind 1: CC:602, :641. Kind 2: FC:67-72, :170-198, :307-311.
- **Kind 2 descriptor overlap with Ada locals.** Class X, outside the premises (FC:292-293).
- **Final_Context_Matches.**
  - Seal refusal: FC:273-278 vs :385-396.
  - Operation: FC:281 vs :389-392.
  - `Valid (X.Start.Required)`: FC:282 vs :145 and :59-64.
- **Start.Required length and First conjuncts (FC:283-286).** Correctly stated as CONDITIONAL on Seal's postcondition (REC:380). I re-traced the chain:
  - FC:231-232;
  - `S5/core/evaluation_finalization.ads:394-398` and :377-386;
  - Seal_Equation :353-374;
  - Capture_Valid :194-200;
  - Input_Valid → Same_Start → Start_Valid → Plan_Valid :95-125;
  - Valid_Checks (`evaluation_raw_roster.ads:153-155`): `S.First in 1..RC` and `S.Length-1 <= RC-First` exclude CC-side conjuncts FC:283-286.

### 2.2 RC-v2-1 gap (a): the Kind 1 request-array overlap is constructible

The packet records the refused overlap of R.Captured_Results (CC:777) and R.Required (CC:778) with the Context_Input descriptor as OPEN (REC:351-352, :393; AUTHOR-NOTES.md:106; `packet.json:218`).

The reason given is that any overlap puts accepted-row bytes in a descriptor word that "the descriptor's earlier transport conjuncts (X.Version = 1 first, … and X.Agent and X.Agent_Confinement at its end) would then have to hold". **That is incorrect, for two reasons.**

1. **The conjunct order is misread.** `X.Agent /= Raw_Agent` and `X.Agent_Confinement` are at CC:780, after CC:777-778 in the `or else` chain, so they need not hold for a refusal at CC:777 or CC:778.
2. **Not every descriptor word is read by an earlier conjunct.** Conjuncts CC:765-776 read only Version, Data/Data_Length, Expected_Binding, Expected_Current, Prepared_Current, Row_Count, Required_Count, Policy and Rows. They never read the `Expected` and `Observed` Context_Fields arrays, nor `Projection`. Those are first read at CC:796 and CC:857 (layout: `S5/core/evaluation_completion_c.ads:160-183`; `S5/runtime/worldline/evaluation_context.py:30-36`).

**Construction (source-derived; layouts unmeasured, C-13 placeholders).** Under C convention on LP64 the layout is as follows; every value is JACKAL exact:
- Binding is `5*16+24`=104 bytes.
- `Expected` begins at descriptor offset `8+8+8+104+40+40`=208, which is `208/8`=26 words, so 8-aligned.
- `Expected` and `Observed` together are `2*14*24`=672 contiguous bytes, ending at `208+672`=880. Context_Field has 14 values: `S5/core/worldline-evaluation_authority.ads:102-106`.
- Check_Row fields sum to 284 bytes and pad to 288 (`36*8-284`=4). The row size is `288+16`=304, and two rows are `2*304`=608, leaving `672-608`=64 bytes to spare.
- A Required_Row is `2*16`=32 bytes.

So:
- **For CC:778.** Place the Input's one Required_Row, with the fixture's accepted bytes unchanged, at descriptor offset 208, and point `R.Required` there.
  - Raw_Decide, and so Read_Ready, sees identical row bytes. Its only address-dependent checks are against its own Output (CC:538-556).
  - Readiness and classification are therefore unchanged.
  - CC:765-776 hold, because no field they read changed.
  - CC:777 holds, because Captured_Results is elsewhere.
  - CC:778 fails on Disjoint.
- **For CC:777.** Place the two captured Check_Rows (608 bytes) at the same offset.
- **Discrimination.** CC:779-780 also hold. If the conjunct were absent, the call would reach CC:796, where `Expected (K)` holds row bytes, and refuse at field-rejected, not transport-guard-rejected. The C-06 stream therefore distinguishes it.
- **Harness support.** The harness already supports interior pointers: `to(name, offset)` (CHAR:189-190) is resolved as `base + placement + offset` (GP:294), as used by `U15f_R0_output_overlaps_input` with offset 8. What is missing is a builder delta that copies the row bytes into the descriptor region before `_adopt` (CHAR:1069-1088, :1107-1151). That is engineering, not unexercisability.

**Ruling.**
- OPEN is honest only in that no case exists.
- A reasoned exemption is not acceptable, because its reason is false.
- C-03 and v4 §9.6.6 require this refused overlap (`WT/designs/claude-capi-boundary-design-v4/DESIGN.md:623-624`), and RC-v2-1 named it. → **RC-v3-1.**

### 2.3 RC-v2-1 gap (b): nested_conjuncts is incomplete at the packet's own granularity

The packet claims more coverage than it has:
- REC:327: "every other conjunct is listed under unexercisable".
- REC:56: "every other conjunct of those guards is listed under unexercisable … or under not_exercised".

**The packet's own C-03 granularity rule** (P1 AUTHOR-NOTES.md:150-153, accepted by the v1 review as a stated finite limit, P1 REVIEW.md:110):
- the Extent_Valid and Array_Valid sub-conjuncts (null, misalignment, overflow, count, overlap) are "covered fully for representative operands: Data, Journal, the fixed records";
- other arrays get null and overlap.

**The analogous Metadata_Matches operands** have separate cases: `U14m_R1_context_data_null`, `_context_data_length_negative`, `_meta_rows_misaligned` and `_captured_misaligned`, and `U14m_R0_context_misaligned` and `_address_overflow`. The v2 review accepted U14m as per-conjunct coverage.

**Reachable through the mixed entry, covered by no case and absent from `unexercisable`:**
- the Metadata argument's misalignment and address overflow at Metadata_Base `Extent_Valid (Context)` (CC:896-898). This is a fixed record of alignment 8, and only Null is covered (REC:329);
- `X.Base` misalignment and overflow (CC:901-903). Only Null is covered (D57);
- `X.Data` null with a nonzero length, and overflow (CC:766). Only Length -1 is covered (D59);
- `X.Rows` and `X.Required` misalignment (CC:776, :779). Context_Row and Required_Row have alignment 8; only null and overlap are covered;
- Expected_Current and Prepared_Current present with an invalid Sequence or Run (CC:282-284, :773-774). Only Present 2 is covered, whereas the record splits cursors as `U14d_R1_current_presence` and `U14d_R1_current_run`.

→ **RC-v3-2.**

### 2.4 RC-v2-2: closed in source

**probe_readiness makes exactly Read_Ready's checks** (CHAR:1336-1391 vs FC:370-398):
- **Kind 1.** `wl_completion_raw_decide_v1` must return 0, with Promotion ≤ 1 and Reason ∈ {Retain_Terminal, Already_Retained}. The probe maps the reason through `CK.REASONS`, which equals the order of T.Decision (`S5/runtime/worldline/completion_kernel.py:59-63`; `S5/core/evaluation_completion.ads:218-223`).
- **Kind 2.** `wl_finalization_decide_v1` must return 0, with Reason 0, Promotion ≤ 1 and a re-read Operation of 3.
- **Ready value.** Ready = Promotion only when the side is valid.
- **Agent.** The probe uses `wl_evaluation_wire_admit`, whose body is Fits followed by Confined_Admit_Wire (`S5/core/worldline-c_api.adb:730-736`), and then forces readiness to 0 for a non-Agent source. This matches FC:463-469.
- **Needs_Agent.** Needs_Agent = Needs_Primary or Needs_Staged (`S5/core/worldline-evaluation_authority.ads:35-36`), so it holds on every U15y shape.
- **Needed sides.** `ready_flags` follows the shape (CHAR:1206-1207), and a script confirmed that every U15y case declares exactly its needed sides plus the agent.

**assert_ready makes a not-ready fixture fail.**
- It runs before the guarded early return (CHAR:1521-1522 vs :1540-1541), so twins are covered too.
- It fails on an invalid side, a non-admitted agent (255) or a readiness mismatch (CHAR:1495-1505).
- The probe runs under the fatal-fault policy, before the snapshot, and reads no PROT_NONE object (GP:271-277, :324-325, :350).

**Claim corrections.**
- Oracle docstring: CHAR:1314-1317. C-11: REC:61.
- Route table, the decide_mixed mix and the seven twinless refusals: AUTHOR-NOTES.md:126-149.
- The recommended cases are D74 and D75.

### 2.5 RC-v2-3 and RC-v2-4, read statically

- **Characterization `--record`.** `require_output_only_launch()` runs at CHAR:68-70, after stdlib-only imports (CHAR:48-57) and before `HERE`, `capi_guard_pages` and every `worldline` import (CHAR:72-93; checked with the AST). `record_main` keeps its own check (CHAR:1650).
- **`--measure-headers`.** The gate is the first statement of `measure_main` (LAY:292-294). All top-level imports are stdlib (LAY:52-65), and `worldline` is imported only inside functions.
- **Normal header test.** Qualified under launch obligation 1 (LAY:21-24).
- **"Opens no file".** No occurrence remains in the modules, `packet.json` or AUTHOR-NOTES.md.
- **HarnessFaultControl.**
  - After `run_forked` returns, it builds `{"harness_fault_control": {wait_status, signaled, signal, describe, report_bytes}}`.
  - It writes the line with `os.write(1, …)` in a loop before any assertion (CHAR:1612-1621). `G.describe` exists (GP:433-438).
  - Every passing path therefore leaves the line on captured fd 1, and this does not depend on unittest buffering.
  - A hang inside `run_forked` writes no line. That is a failed run under launch obligation 4, never a pass.

## 3. Faithfulness and F32

- **The new cases follow original S5 behaviour (§2.1).** No class-H code is treated as a refusal. `test_record_shape` still forbids classes H and X (CHAR:1569-1570). No expectation is weakened. No S5 file changed (all 100 hashes match).
- **F32.** The comment (CHAR:957-967) and AUTHOR-NOTES §6 cite S5's positive control, `test_collapse_recomputes_carried_roster`, which has current = resulting = h(8) and asserts AUTHORIZED (`test_raw_evaluation_default.py:471-490`).
  - I re-read `S5/core/worldline-collapse.ads:139-156` and :211-217. Candidate mode requires `Resulting_Requirement.Present`, and Authorized holds exactly when All_Hold holds.
  - No case asserts a code for the S5 request with Resulting_Requirement absent.
  - F32 is not decided by the packet. It remains owned by F32-CONFLICT.

## 4. Placeholders

**Finding: unchanged, none added, none can pass.**
- The RECORD_ON_L0 count per file is equal in v2 and v3: REC 7, baseline 181, and 1 in each test module.
- The placeholder cases are the v1 ones: three written results and D06.
- The fail paths are unchanged: `check_case` fails on any placeholder (CHAR:1532-1533, :1556-1558).
- No U15y case or D56–D75 holds a placeholder.

## 5. Other weakening, assumptions or gates

- **C-03 and `not_exercised`.** REC:56 now admits "not_exercised with its own reason". That is acceptable only where the reason is valid. The Kind 1 item's reason is not (RC-v3-1).
  - REC:56's refused-overlap list for U15y names only the context arrays. It must name the request arrays once their cases exist.
- **Stride-bound entry (REC:388).** It says a stride-failing count "would need a row array larger than the address space".
  - Context_Row is `304+2*8*24`=688 bytes, so the stride bound for X.Rows is tighter than Raw_Decide's 304-byte bound.
  - At that bound, the Kind 1 captured array of N·304 bytes is below 2^64: `2^64-(2^63-1)*304/688` = 617965926469269979155/43 > 0. It is above 2^52: `(2^63-1)*304/688-2^52` = 175050413916263809005/43 > 0. Both are JACKAL exact.
  - The class-X ruling therefore rests on a virtual-address width of at most 52 bits and on the live-readable premise, not on the 64-bit Integer_Address range. State that premise (recommendation).
- **Readiness declarations.** `test_record_shape` does not check that the declared readiness sides equal the shape's needed sides. A script found that they do. Adding the check is recommended.
- **Nothing else found.** No contract, floor, accepted case, fixture or control is lowered or edited. No C-14 condition is encoded. No approval gate is added.

## Required changes

### RC-v3-1 (RC-v2-1 a)
- **Change:**
  - Author `U15y_R1_k1_primary_context_captured_overlap` (CC:777) and `U15y_R1_k1_primary_context_request_required_overlap` (CC:778), each with its C-05 twin and its exact C-06 stream (transport-guard-rejected, then primary-context-rejected).
  - Place the Input's accepted Check_Rows or Required_Row, byte-identical, inside the descriptor's Expected/Observed region (offset 208), and point the request field there.
  - Map these in `nested_conjuncts`.
  - Remove the OPEN `not_exercised` item and deviation 2.
  - Correct the reasoning in REC:393 and AUTHOR-NOTES.md:106.
- **Reason:** The conjuncts are reachable without changing any accepted row byte. The OPEN reason misreads the conjunct order (CC:780 follows CC:777-778) and overlooks descriptor regions that CC:765-776 do not read.
- **Evidence:** CC:765-780, :796, :857, :538-556; `S5/core/evaluation_completion_c.ads:160-183`; `S5/core/worldline-evaluation_authority.ads:102-106`; CHAR:189-190; GP:294; REC:351-352, :393; AUTHOR-NOTES.md:106; `packet.json:218`; v4 DESIGN.md:623-624.

### RC-v3-2 (RC-v2-1 b)
- **Change:** Add cases (code 255, with twin and stream) at least for:
  - the Metadata argument misaligned and address-overflow (CC:896-898);
  - X.Base misaligned and overflow (CC:901-903);
  - X.Data null with a nonzero length (CC:766);
  - X.Rows and X.Required misaligned (CC:776, :779);
  - Expected_Current and Prepared_Current present with an invalid span (CC:773-774).

  For each remaining sub-conjunct (for example X.Data, X.Rows and X.Required overflow), either add a case or record an explicit representative-operand entry with its reason. Correct the "every other conjunct is listed" claims.
- **Reason:** The restored C-03 and the packet's own accepted granularity rule cover these sub-conjuncts for fixed records and for the analogous U14m operands. As written, the completeness claim is inaccurate.
- **Evidence:** REC:56, :327-353; CC:258-278, :282-284, :766-779, :893-907; P1 AUTHOR-NOTES.md:150-153; P1 REVIEW.md:110; REC cases U14m_R0_context_misaligned/_address_overflow, U14m_R1_context_data_null, U14m_R1_meta_rows_misaligned, U14d_R1_current_run.

## OPEN obligations

- An independent re-review of a revised packet, with new identities, before baseline execution.
- The baseline run on L0 in an admitted frame, and reviewed recording of every placeholder: 179 layout values, three written results and the D06 bytes.
- The six launch obligations: bytecode suppression for every interpreter, including the unittest parent and the header test; owned scratch and TMPDIR; WORLDLINE_CORE_LIB and PYTHONPATH; reviewed supervision with deadlines; byte-exact capture; HarnessFaultControl with its stdout line retained.
- V5-B01, V5-B02 and the capacity gate.
- F32-CONFLICT, owned outside PK-0.
- Class H §9.6.4 a–d, native write construction, ABI and layout measurement, and full proof of the Collapse.Decide, Decide_Wire and Seal contracts. The Start.Required unexercisability rests on Seal's postcondition.
- The model-identity requirement of HANDOFF.md:173 against this Claude review.
