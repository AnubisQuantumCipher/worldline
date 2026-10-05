# WORLDLINE Phase One C-API PK-0 v2: independent source review

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**

This is a passive source review of the packet named below. It grants no source acceptance, run evidence, control evidence, proof acceptance, stage qualification or Phase One acceptance. The PK-0 stage gate is a baseline run on L0 in an admitted frame. That run, its recorded values and the six launch obligations remain **OPEN**. Frame v5 is UNQUALIFIED; V5-B01, V5-B02 and the capacity gate block execution (`packet.json:6`). This review does not qualify those gates.

**Reviewer.** An independent Claude Code review subagent (claude-opus-5-5) with a fresh context. It is different from the author and authored nothing under review. Following the lead's override file (sha256 `bdb0815d…0b00`), it replaces the brief's "actual gpt-6.1-sol". The original requirement texts say every required independent review uses actual gpt-6.1-sol, and that a Claude review cannot count as that gate (`W/outputs/claude-phase1-handoff-20261004/HANDOFF.md:173`; `/home/sicarii/Documents/complete-phase1-prompt.txt:60`). This review records that conflict and does not decide whether it satisfies the gate.

**What was and was not done.** No packet module, helper, S5 test or fixture, WORLDLINE library, compiler or prover was imported or run. Python was read as text, with `ast.parse` and `json.load` only. The review directory of the revision under review was not read.

- **Brief:** sha256 `02f7eff795ff99e621c0132f3099942023edc21d8d8bf8c693ccc54337847ea9`.

**Citation roots.**
- **P** = `WT/packets/capi-pk0-v2`. Unprefixed `packet.json`, `AUTHOR-NOTES.md` and `files/tests/...` mean P.
- **P1** = `WT/packets/capi-pk0`.
- **S5** = `W/work/claude-composition-v5-beta/source`.
- **W** = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`.
- **WT** = `W/work/claude-lead-isolation-v1/wt-1`.
- **CHAR** = `files/tests/test_capi_characterization.py`.
- **GP** = `files/tests/capi_guard_pages.py`.
- **DIAG** = `files/tests/test_capi_diagnostics.py`.
- **LAY** = `files/tests/test_capi_layout_identity.py`.
- **REC** = `files/tests/capi_characterization.json`.

## 1. Packet integrity and invariants

**Finding: the identities hold; the payload is additive; v1 is unchanged; every v1 case and diagnostic case is carried in content and in order.**

- **Packet files.** All nine sha256 values equal the brief.
  - packet.json `c5ce00cd…2032d`, AUTHOR-NOTES.md `4f50ad46…dde514`, jackal.json `f4b69fdf…7668e`.
  - Under files/tests/: capi_characterization.json `42d23d67…9befb`, capi_guard_pages.py `29e496d5…3d12b`, capi_layout_baseline.json `4df25239…bf0`, test_capi_characterization.py `acbdcc42…bc5b1`, test_capi_diagnostics.py `83537723…c8f7b`, test_capi_layout_identity.py `76f086dd…12fa`.
  - The six payload sha256 values and byte counts equal `packet.json:43-50`.
- **v1 unchanged.** P1 files hash to the "v1" values in `packet.json:52-61` (packet.json `9808145e…69f9`; byte counts equal too). The sealed v1 review equals its freeze: REVIEW.md `7d86d533…`, review.json `fc615b5be33f…dbdf5`, checks.json `949b6150…`, review-freeze.json `fa987ae0…`.
- **Bound inputs.** All 100 entries (`packet.json:99-200`) have distinct paths and match S5 in sha256 and size. The first 95 equal P1's list in order.
  - The two host headers also match (`packet.json:202-205`).
  - The base identities match `packet.json:37-41`: composition.json `a0e0bb5c…fa3e`, source-inventory.json `3407119b…937a`, review.json `df6cbc9d…3476`.
  - The v6 review.json `bcfa259f…d128` and REVIEW.md `12cfde3c…a161` match `packet.json:29-30`.
- **Nothing existing touched.** None of the six payload paths exists in S5. `existing_files_touched` is empty (`packet.json:63`).
- **Change list against v1 is exact.**
  - **capi_layout_baseline.json:** only line 5 differs.
  - **capi_guard_pages.py:** the docstring, the fault policy, `_map`/`_protect` factoring, `protected_probe` and strict decode change. Layout, placement and comparison logic are unchanged.
  - **test_capi_characterization.py:** v1 builders, mutations and expectation logic are unchanged. The hunks are additions, plus the `assert_child_ok` factoring at CHAR:1395-1415.
  - **jackal.json:** J01–J27 and common_result are identical to P1.
  - **capi_characterization.json:** by JSON comparison, the only changed keys are design.revision, rules, controls C-03/C-05/C-06/C-11 and the single export entry `wl_collapse_decide_finalization_v1`. The other 19 export entries are equal.
- **v1 cases carried.** P1's 609 cases equal REC's first 609 cases, and P1's 28 diagnostic cases equal REC's first 28, in order. In text, two lines differ only by an added trailing list comma: P1 REC:354 → REC:358 (D28) and P1 REC:965 → REC:996 (the last v1 case). The appended cases are 46 U15y cases and D29–D55. Case ids are unique.

| Invariant | Observation | Evidence |
|---|---|---|
| REQUIRED_PROVED | AST segments 280, 11, 4, 5, 8, 31, 34, 46, 1, 115; 535 unique names; nothing appended | `S5/runtime/worldline/proof_manifest.py:25,312,314,924,940,953,967,972,1003,1012` |
| MINIMUM_CHECKS | 251 | `proof_manifest.py:22` |
| UNANALYZED_BOUNDARY | `{"worldline-c_api"}` | `proof_manifest.py:316` |
| Movers | 0 | `packet.json:69` |
| External_Name in worldline-c_api.ads | 31 (grep -c) | `S5/core/worldline-c_api.ads` |

The JACKAL sum of the AST segments is **status=exact**, `parsed=280+11+4+5+8+31+34+46+1+115`, `exact=535`, formal=false, lane rat. Non_claims: "NOT formal-bounded: this lane carries no Lean-checked certificate"; "The epistemic class above is the STRONGEST claim this result supports"; "exact rational arithmetic (not yet checker-covered)".

These cross-checks were also `exact` with the same non_claims:
- 609+46=655 cases;
- 28+27=55 diagnostic cases;
- 95+5=100 bound inputs;
- 58+19=77 guarded cases;
- 46−19=27 unguarded U15y cases;
- 25+82+72=179 layout placeholders.

All of this arithmetic is informational only.

## 2. Closure of PK0-RC1 to PK0-RC5

| RC | Ruling | Remaining gap |
|---|---|---|
| PK0-RC1 | PARTIALLY_CLOSED | Context_Matches transport conjuncts reachable only through the mixed entry are not covered, including the refused descriptor overlaps that v4 C-03 names. "not_exercised" is a category the design does not define. The oracle, route and three-check claims are overstated. (RC-v2-1, RC-v2-2) |
| PK0-RC2 | PARTIALLY_CLOSED | The characterization `--record` bytecode gate runs after the non-stdlib imports. `--measure-headers` has no gate, yet claims to write only in scratch. (RC-v2-3) |
| PK0-RC3 | PARTIALLY_CLOSED | The fault policy and checks are sound as source. On its passing path the negative control emits no record of the abnormal status that RC3 and launch obligation 6 require to be retained. (RC-v2-4) |
| PK0-RC4 | CLOSED_IN_SOURCE | None in source. D06 bytes remain RECORD_ON_L0. |
| PK0-RC5 | CLOSED_IN_SOURCE | The isolation, import and layout statements are corrected (GP:8-36; CHAR:24-44; LAY:39-45; AUTHOR-NOTES.md:159-176). Launch properties are stated as OPEN. New overstatements are assigned to RC-v2-2 and RC-v2-3. |

### RC1 in detail

**Ready inputs are genuinely S5 producers and fixtures.**
- **Kind 2.** `_ready_kind2` (CHAR:996-1018) instantiates `TFK.FinalizationNativeControls` and sets core, library and kernel exactly as its setUpClass does (`S5/tests/test_finalization_kernel.py:25-28`). It then calls `kernel.prepare_finalization(fixture.sealed(fixture.capture()))` and the S5 `joined(prepared, request, agent, **changes)` (`:224-243`).
- **Kind 1.** `_ready_kind1` (CHAR:1021-1045) replicates the class setup of `RequiredFailureControls`/`RawRequiredFailureControls` (`S5/tests/test_evaluation_roster_d2.py:22-37`; `S5/tests/test_raw_evaluation_default.py:20-23`). It calls `setUp`, then the S5 `prepared` and `joined` (`:25-69`) with the S5 rows (`:79-80`).
- **Agent.** The Agent-origin agent is the S5 record (CHAR:985-987 = `test_finalization_kernel.py:252-254`).
- **Deltas.** Each delta mirrors an S5 test:
  - "field" = `test_raw_evaluation_default.py:149`;
  - "subject" = `:94`;
  - "binding_content" = `test_finalization_kernel.py:272`;
  - "no_metadata" = `:264`.
- **Owner indices match S5 attach.** `context_owners=(data, joined, qs, descriptor)` and `metadata_owners=(data, projected, descriptor, base)` (`S5/runtime/worldline/evaluation_context.py:194-198`, `:124`). So `[1]` is the ContextRow or MetadataRow array and `[2]` is the Required array, as CHAR:1054-1060 assume.

**Pointer-rewrite owner check is sound for the S5 shapes.**
- `_adopt` (CHAR:1086-1130) copies every reachable owner and rewrites only `c_void_p` fields of Structures. A pointer naming zero or two owners raises PlacementError, so the case fails.
- In S5, pointers occur only in top-level Request, ContextInput and MetadataContext. Array element types (Check_Row, ContextRow, MetadataRow, Row, Raw, Required_Row) contain none (`completion_kernel.py:13-47`, `evaluation_context.py:27-53`, `finalization_kernel.py:24-46`).
- `_pointer_fields` refuses pointer-bearing array fields (CHAR:1078-1082). An Array owner is never scanned for pointers (CHAR:1117-1118); that is safe for these types, but it would silently miss a future pointer-bearing element type.

**Authorized oracle.**
- `oracle_collapse_ready` (CHAR:1287-1299) recomputes `wl_collapse_decide` on the collapse request with assumed ready flags. It proves only that the request half can be Authorized. It does not observe Read_Ready validity or Promotion (`S5/core/evaluation_finalization_c.adb:370-398`), nor agent admission (`:453-470`).
- A fixture that fails Read_Ready returns 255 at `:433-436` or `:445-448`, or at `:464-466` for the agent. In such a fixture, the unguarded twin (255, no byte changed) and the guarded twin of a join refusal both still pass.
- The not-ready fixture is caught only by the paired positive case and by the case's D-case. All 27 unguarded U15y cases have a D-case naming the refusing site (REC:359-385; checked by script).
- Readiness is therefore discriminated at suite level, not per case as claimed (AUTHOR-NOTES.md:86; CHAR:1293-1295; REC:61 C-11 text). See RC-v2-2.

**Guard-page twins and end-of-object guards are correctly placed against the bodies.**
- **Transport twins.** They protect the base context data, rows and required arrays and the metadata data and rows. Context_Matches rejects at `S5/core/evaluation_completion_c.adb:765-783` before its copies at `:787-788`. Metadata_Base reads only the MetadataContext record (`:893-907`).
- **Field twin.** It leaves base data readable (copied at `:788`) and protects rows onward (rows are first read at `:807-810`).
- **Row and row-field twins.** They use `prefix` 1 on base rows. The K1 fixture has two captured rows, so row 2 is never read.
- **Required twin.** It protects only the metadata data and rows.
- **Binding and subject twins.** They protect only the metadata data and rows; a false join returns before Metadata_Matches (`evaluation_finalization_c.adb:339`; `:474-478`).
- **Metadata-row twin.** It uses `prefix` 1 on metadata rows (`evaluation_completion_c.adb:951-964`).
- **Engine twins.** They protect the whole metadata tree, which is never read when Agent_Ready=0 (`:473`).
- **Both-mode primary transport twin.** It protects every staged context and metadata object (primary first, `:474-483`).
- **Authorized `end` twins.** They name every adopted object (`_adopt` names derive as `name_path`).
- **Refusals with no twin.** Six unguarded refusal cases have no C-05 twin: k2_primary_context_metadata, k2_primary_context_null, k1_primary_context_null, k1_primary_metadata_payload, k1_staged_metadata_payload and both_staged_metadata_payload. For each, no context or metadata object lies beyond the frontier, so no twin is needed. The claim that every refusal case has three checks is nonetheless inaccurate (AUTHOR-NOTES.md:81-84).

**Coverage against the S5 bodies.**
- **Every mixed join site is reached at least once:**
  - primary-context-rejected: D31–D36, D41, D43–D45, D48, D49, D51;
  - staged-context-rejected: D47, D53, D55;
  - primary-metadata-rejected: D34, D42, D46;
  - staged-metadata-rejected: D40, D54.
- **Gaps:**
  - **(a) Context_Matches transport conjuncts.** These are `evaluation_completion_c.adb:765-780`. Context_Matches has no External_Name (`S5/core/evaluation_completion_c.ads:188-190`). Its only moving-export caller is the mixed entry; `worldline-c_api.adb:810` is a staying export.
    - The record covers only Agent_Confinement (REC:327).
    - Reachable through the mixed entry and uncovered: `X.Version`, X.Data extent, `X.Row_Count /= R.Captured_Count`, `X.Required_Count /= R.Required_Count`, `X.Policy`, the validity of `X.Expected_Binding`/`Expected_Current`/`Prepared_Current`, Array_Valid of X.Rows and X.Required, the overlap of R.Captured_Results and R.Required with the Context_Input descriptor, and `X.Agent /= Raw_Agent`.
    - The R-side Version, Operation, Policy, field-validity and Data conjuncts are refused earlier by Raw_Decide on the same bytes (`:545-562`).
    - v4 §9.6.6 C-03 names "context and metadata arrays against the descriptor" as refused overlaps to keep (`WT/designs/claude-capi-boundary-design-v4/DESIGN.md:623-624`). The v3 table says "One case per guard conjunct" (`WT/designs/claude-capi-boundary-design-v3/DESIGN.md:2229`), as does REC:56.
    - The v1 review held that the representative-operand limit "cannot excuse the reachable mixed guards missing under RC1" (`P1/review/gpt61-v1/REVIEW.md:110`).
    - The note that each conjunct "keeps its own coverage at its own export where it has one" is true for Metadata_Matches (U14m covers each conjunct, REC U14m_R0/R1/R2) and false for Context_Matches.
  - **(b) Route coverage.** The staged-only and both routes carry only a subset of the nested groups listed "for each route" (AUTHOR-NOTES.md:64-74):
    - staged K1 has authorized, subject and metadata_payload only;
    - staged K2 has authorized and transport only;
    - Engine-origin agent cases are primary only.
    - The both route covers K2 primary with K1 staged only. S5 `decide_mixed` accepts either kind on either side (`S5/runtime/worldline/finalization_kernel.py:296-306`), so "the genuine S5 decide_mixed mix" (AUTHOR-NOTES.md:67) is inaccurate.
    - Not covered: the both-mode ordering in which the primary Kind-1 metadata join precedes the staged one (`evaluation_finalization_c.adb:491-502`).
    - These are the same nested conjuncts, so I require a claim correction, not duplication. A K1-primary both-mode case is recommended.

**Not-exercised groups.**
- **(i) Start.Required extent conjuncts.** `Valid (X.Start.Required)` at `evaluation_finalization_c.adb:282` is unreachable outright, because Decide already required `Valid (X.Start)` (`:145`, `:59-63`).
  - The length and First conjuncts (`:283-286`) are unreachable given Seal's postcondition. Seal_Observed implies Seal_Equation, then Capture_Valid, Input_Valid, Same_Start, Start_Valid, Plan_Valid and finally Valid_Checks (`S5/core/evaluation_finalization.ads:394-398, 194-200, 121-125, 107-108, 95-106, 74-79`; `S5/core/evaluation_raw_roster.ads:153-155`). Decide sets Reason 0 at Op 3 only on Seal_Observed (`evaluation_finalization_c.adb:231-232`).
  - `Evaluation_Finalization.Seal` is on the required-proved roster (`proof_manifest.py` AST), but required is not proved. So this is a contract-conditional unexercisability, not an established fact.
  - The group must be recorded as unexercisable with that stated condition, not left in a third category (RC-v2-1).
- **(ii) Transport conjuncts.**
  - Metadata_Matches: acceptable as stated, given U14m's per-conjunct coverage of the same function at its own export.
  - Context_Matches: not acceptable; cases are required (RC-v2-1).

## 3. The Resulting_Requirement deviation and the S5 finding

**Finding: the author's finding is correct against the cited source, at contract level.**
- S5 `RawDependencyControls.checkpoint()` sets `resulting_requirement=None` (`S5/tests/test_raw_evaluation_default.py:530`).
- `bound_request` (`:71-75`) and `collapse_values` (`S5/tests/test_finalization_kernel.py:245-251`) switch to CANDIDATE_EVALUATION without setting it.
- `_optional_hash(None)` yields Present 0 (`S5/runtime/worldline/core.py:597-598`).
- `Decide_Wire` equals `Decide (Decode (R))` when well formed (`S5/core/worldline-collapse_wire.ads:255-260`).
- Decide's Post forbids Authorized whenever `Required_Present` fails (`S5/core/worldline-collapse.ads:213-220`), and `Required_Present` requires `Resulting_Requirement.Present` in candidate mode (`:148-151`).
- Yet `:88-89` and `:262-263` assert `'AUTHORIZED'`.
- This rests on the contracts, which are required-proved but not shown proved here. It is not run evidence.

**Effect of the deviation.**
- Setting Resulting_Requirement = Current_Requirement in the new U15y requests (CHAR:956-977) does not redefine original behaviour, edit an original fixture or control, or narrow a domain:
  - `_ready_request` builds a new dataclass via `replace`;
  - no S5 file changed (all bound hashes match);
  - every U15x zero-roster case is retained (REC:973 onward, unchanged).
- The shape is not a new assumption. S5's own positive control `test_collapse_recomputes_carried_roster` uses `current_requirement=h(8), resulting_requirement=h(8)` and asserts AUTHORIZED (`test_raw_evaluation_default.py:471-490`). The author did not cite this; it should be cited (recommendation).
- The deviation matters only for the primary and both shapes. The staged-only shape is CHECKPOINT_RETURN, where Resulting is not in Required_Present (`worldline-collapse.ads:155-156`; CHAR:973-974).

**What it means for the original AUTHORIZED controls, and who owns it.**
- Read by contract, those unchanged controls cannot pass. STATUS records this as author finding F32 and a NEW OPEN OBLIGATION F32-CONFLICT: OB-003 against those controls, to be resolved "weaken[ing] neither", with its own design and independent review, "not decided here" (`WT/STATUS.md:66, 312-324`). The F32 investigation is model-origin static prose and is not evidence.
- PK-0 must not resolve it, and does not. It neither edits the controls nor adds a case asserting a decision code for the exact S5 absent-Resulting request. Either would take a side.
- The owner is the F32-CONFLICT obligation. This review decides nothing beyond the source reading above.

## 4. Faithfulness of the new cases and diagnostics to original S5

**Finding: the sampled expectations follow the bodies exactly. No class-H code is treated as an accepted refusal, and no expectation is weakened.**

| Case | Checked against | Result |
|---|---|---|
| U15y_R3_k2_primary_authorized / D29 (mixed entry, Authorized) | `evaluation_finalization_c.adb:411-503` with Read_Ready Kind 2 (`:385-394`) running Decide (`:127,158,247-248`); Final_Context_Matches (`:272-346`), whose second Decide gives the same lines; Context_Matches (`evaluation_completion_c.adb:750,785,794,849,859`); Metadata_Matches (`:921,943,950,971,976`); collapse-decision 0 (`:488`); no Kind-1 metadata join for Kind 2 (`:491-502`) | every line, value and order matches; code 0, no writes |
| U15y_R3_k1_primary_authorized / D30 | Raw_Decide emits nothing (`evaluation_completion_c.adb:529-693`); context join, decision 0, then the Kind-1 metadata join (`:491-496`) | matches |
| U15y_R1_k1_primary_context_transport / D31 (nested context refusal) | Confinement 1 = Confinement_Not_Established ≤ Last (`S5/core/worldline-evaluation_report_facts.ads:42-44`). The Agent-origin record is not report-based and not External, so Confined_Admit_Wire gives 1 (`S5/core/worldline-evaluation_wire.ads:162-171`) and agent-ready stays 1. The context carries 0 (`evaluation_wire.py:153`; `evaluation_context.py:184`), so `X.Agent_Confinement /= Agent_Confinement` holds (`evaluation_completion_c.adb:780-783`). | 255 at primary-context-rejected; lines match |
| D35 (K2 transport) | Final_Context_Matches logs context-result 255 (`evaluation_finalization_c.adb:338`), then False | matches |
| D36 (K2 inner metadata) | Context joins; Metadata_Matches gives 0 (`:341-346`) → primary-context-rejected | matches |
| D41 / D49 (null context) | Metadata_Base(Null) = Null (`evaluation_completion_c.adb:896-898`) → input-extents-rejected (`:751-757`) | matches |
| D34 / D42 / D46 (Kind-1 metadata refusals after Authorized) | collapse-decision 0, then Metadata_Matches join-result 0, row-rejected 1 or transport-guard-rejected (`:932-941, 958-963, 976`) → primary-metadata-rejected (`evaluation_finalization_c.adb:491-496`) | matches |
| U15y_R3_k1/k2_primary_engine_agent / D37 / D52 (Engine origin) | The well-formed Engine record is not Invalid, then forced to 0 (`evaluation_finalization_c.adb:463-469`); flags 0; Decide_Wire (`:485-490`); code = oracle collapse_zeroed (CHAR:1274-1284); a non-Authorized decision returns before the metadata join | matches |
| D40 / D47 (both mode) | primary K2 context and inner metadata, then staged K1 context; Authorized; staged metadata refusal or staged context refusal | matches |

Further checks:
- **Diagnostic line format.** `I64'Image` gives a leading space (DIAG:65-67; Ada RM 3.5).
- **No stray lines.** The oracle's `wl_collapse_decide` emits no diagnostic line (`S5/core/worldline-c_api.adb:331-342`); only evaluation_completion_c.adb and evaluation_finalization_c.adb call Diagnostic_*.
- **No H or X cases.** Every U15y R1 case expects 255 = Invalid_Request, the defined R1 refusal (REC:321), and no case is class H or X (CHAR:1464-1465).
- **Positive cases.** Each still requires code 0 and oracle_value 0.

## 5. Mechanics, read statically

- **Fatal-fault policy.** Acceptable as source.
  - `establish_fatal_faults` sets SIG_DFL for SEGV, BUS, ILL and FPE through libc `signal` (GP:61-99; host headers bound).
  - `execute` establishes the policy after mapping (GP:299-300) and re-verifies it immediately before and after the export (GP:324-326). The verification fails on any disposition other than SIG_DFL, including SIG_IGN.
  - Diagnostic control calls are bracketed the same way (DIAG:125-127).
  - The policy is established in the case child after the runtime was initialized in the parent (CHAR:1408-1410) or in the fresh interpreter (DIAG:108-110).
  - Producers called by child-only builders run before the policy. A fault there can only raise a child_error, which fails the case.
- **Abnormal child exit.** It fails before any code comparison: `assert_child_ok` comes first (CHAR:1413-1415, 1395-1401), and DIAG checks the returncode first (DIAG:188-190).
- **HarnessFaultControl.**
  - It calls no WORLDLINE export, reads one PROT_NONE byte placed by the helper's own layout code (GP:362-377), and requires SIGSEGV or SIGBUS, an empty report and a failing `assert_child_ok` (CHAR:1483-1506).
  - It is reachable only through unittest discovery; nothing runs it at import or in `record_main`.
  - On its passing path nothing records the observed status. RC3 required it to be retained (`P1/review/gpt61-v1/REVIEW.md:142`), and launch obligation 6 depends on it (`packet.json:93`). → RC-v2-4.
- **Lossless fd 2.**
  - Comparison is byte-exact (DIAG:77-81, 211-214) with a `{"hex"}` fallback (DIAG:79-80).
  - The report is decoded strictly (DIAG:167-173), and record output is a lossless latin-1 split plus hex (DIAG:84-95).
  - The renderer self-test is at DIAG:231-241.
  - Interpreter-level writes to fd 2 (startup or fatal errors) can only cause a mismatch, never a pass.
  - Accepted (RC4 closed).
- **`--record` output-only.**
  - **Layout:** the gate precedes any non-stdlib import (LAY:47-60, 295-297). `--headers PATH SHA256` reads the bytes once, hashes them and parses only after a match (LAY:272-283), so there is no TOCTOU.
  - **Diagnostics:** the gate is at DIAG:255-259, after stdlib-only imports, and the children run with PYTHONDONTWRITEBYTECODE=1 (DIAG:162).
  - **Characterization:** the gate `require_output_only_launch()` runs inside `record_main` (CHAR:1533-1535), after module-level imports of `capi_guard_pages` and `worldline.*` (CHAR:61-77). Without -B those imports can write `__pycache__` before the refusal, which contradicts "refuses to start" (CHAR:21-22; `packet.json:79`; AUTHOR-NOTES.md:111-114). → RC-v2-3.
  - "Opens no file" is literally inaccurate: JSON is read, modules are imported, the library is loaded. The substantive property is "writes no file".
- **`--measure-headers` scratch confinement.**
  - Probe source, binary and TMPDIR are confined to an existing absolute `WORLDLINE_PK0_SCRATCH` (LAY:138-146, 167-174). A missing binding fails (deviation 4; acceptable).
  - But `measure_main` has no bytecode gate (LAY:286-292). It imports `worldline.*` through `ctypes_class` (LAY:128-130, 164), so "It writes only inside WORLDLINE_PK0_SCRATCH" (LAY:22-23) holds only under launch obligation 1. → RC-v2-3.
- **Isolation boundary.** Correctly stated (GP:10-20; CHAR:24-40; LAY:44-45; DIAG:23-29):
  - parent-side Core init and the b_chain native hashes run in the parent (CHAR:623-656);
  - the recovery builders are Python-only (CHAR:242-304);
  - libc is loaded at import;
  - no deadline is set.
  - Acceptable as a stated limit, not as containment.
- **Six OPEN launch obligations** (`packet.json:87-94`; AUTHOR-NOTES.md:170-176).
  - These are legitimately launch properties, not source properties. Acceptable as OPEN, but none is evidenced.
  - Obligation 6 needs RC-v2-4 to be satisfiable from the run's own output.
  - Obligation 1 must cover `--measure-headers` and the normal header test, which the source does not gate.

## 6. Placeholders

**Finding: unchanged from v1, none added, none can pass.**
- RECORD_ON_L0 occurrences per file are equal in v1 and v2.
- Placeholder cases are exactly U14d_R3_classify_op2_record, U15f_R3_capture_op2_record, U15f_R3_seal_op3_record and D06_failure_latch.
- Layout values are 25 layout exports, 82 ctypes and 72 headers (179 by JACKAL, exact).
- The fail paths are unchanged:
  - written-result placeholders `self.fail` in unguarded cases (CHAR:1446-1450);
  - D06 accumulates pending failures (DIAG:199-216);
  - C-13 fails each placeholder (LAY:228-229, 237-238, 250-251).
- No U15y or D29–D55 expectation holds a placeholder.

## 7. Other weakening, assumptions or gates

- **C-03 granularity.** REC:56 adds, for the mixed entry, "one case per nested guard group … not separately exercised are listed under not_exercised". This relaxes the design's "one case per guard conjunct" (v3:2229; v4:623-624) for Context_Matches. It is disclosed (deviation 3), but disclosure does not make it acceptable. → RC-v2-1.
- **No other weakening found.** No contract, floor, accepted case, original fixture or control is lowered or edited. No C-14 condition is encoded. No class-H code is treated as a refusal.
- **Model-identity conflict.** Recorded in the header above, not decided. This review adds no approval gate.

## Required changes

### RC-v2-1 (PK0-RC1 coverage)
- **Change:**
  - For every Context_Matches transport conjunct reachable through `wl_collapse_decide_finalization_v1` (`S5/core/evaluation_completion_c.adb:765-780`), add one U15y case (code 255), its C-05 twin where an object lies beyond, and its exact C-06 stream. This includes the refused overlaps of context and request arrays against the Context_Input descriptor and `X.Agent /= Raw_Agent`.
  - List each unreachable conjunct as `unexercisable` with its source reason (for example Raw_Decide `:545-562` on the same bytes).
  - Move the Final_Context_Matches Start.Required group to `unexercisable`, citing the Seal/Valid_Checks chain and stating explicitly that it depends on Seal's postcondition, which is required-proved but unproved here.
  - Remove the `not_exercised` category, or confine it to items that carry their own reason.
  - Do not narrow C-03's text.
- **Reason:** v3 C-03 requires one case per guard conjunct, and v4 §9.6.6 keeps context-array refused overlaps. Context_Matches has no export of its own, so these conjuncts are covered nowhere in PK-0.
- **Evidence:** REC:56, 327; `S5/core/evaluation_completion_c.ads:188-190`; `WT/designs/claude-capi-boundary-design-v3/DESIGN.md:2229`; `WT/designs/claude-capi-boundary-design-v4/DESIGN.md:623-624`; `P1/review/gpt61-v1/REVIEW.md:110,126`.

### RC-v2-2 (PK0-RC1 claims)
- **Change:** Correct the readiness claim. Preferably make readiness observable per refusal case: for example, the prelude also requires wl_finalization_decide_v1 Reason 0 and Promotion 1, or wl_completion_raw_decide_v1 Retain_Terminal or Already_Retained with Promotion 1, plus the agent's Confined_Admit_Wire result 1 for that origin. Otherwise state that the oracle checks only the collapse request and that readiness is discriminated by the paired positive case and the D-case. Also correct:
  - "for each route" (AUTHOR-NOTES.md:64-74);
  - "the genuine S5 decide_mixed mix" (AUTHOR-NOTES.md:67);
  - "each refusal case has three checks" (AUTHOR-NOTES.md:81-84), by naming the six refusal cases without a twin and why.
  - Recommended: add a K1-primary both-mode case.
- **Reason:** As written, the unguarded and guarded twins of a join refusal pass on a fixture that fails Read_Ready or agent admission, because both return 255.
- **Evidence:** CHAR:1287-1299; AUTHOR-NOTES.md:86; REC:61; `S5/core/evaluation_finalization_c.adb:433-436,445-448,464-466`; `S5/runtime/worldline/finalization_kernel.py:296-306`.

### RC-v2-3 (PK0-RC2)
- **Change:**
  - In test_capi_characterization.py, refuse `--record` before any non-stdlib import (ahead of CHAR:61) when `sys.flags.dont_write_bytecode` is false.
  - Give `--measure-headers` the same refusal, or qualify LAY:22-23 and AUTHOR-NOTES.md:105-108 as holding only under launch obligation 1.
  - Replace "opens no file" with "writes no file" wherever it appears.
- **Reason:** In the characterization module the refusal comes after imports that can write bytecode. The measurement path imports runtime modules with no gate, yet claims scratch-only writes.
- **Evidence:** CHAR:21-22, 61-77, 1525-1535; LAY:22-31, 128-130, 286-292; `packet.json:79`; AUTHOR-NOTES.md:111-114.

### RC-v2-4 (PK0-RC3)
- **Change:** On its passing path, make HarnessFaultControl emit the observed wait status and signal to a channel the launch captures (for example one JSON line on stdout).
- **Reason:** RC3 requires that the abnormal status be retained. Launch obligation 6 cannot be met from a passing test, which prints nothing.
- **Evidence:** CHAR:1497-1506; AUTHOR-NOTES.md:136; `packet.json:93`; `P1/review/gpt61-v1/REVIEW.md:142`.

## OPEN obligations
- An independent re-review of a revised packet, with new identities, is required before any baseline execution.
- The baseline run on L0 in an admitted frame, and reviewed recording of every placeholder (179 layout values, three written results, D06 bytes).
- Six launch obligations: bytecode suppression for every interpreter including `--measure-headers` and the header test; owned scratch and TMPDIR; WORLDLINE_CORE_LIB and PYTHONPATH; reviewed supervision with deadlines; byte-exact capture of launch streams; HarnessFaultControl with retained status.
- V5-B01, V5-B02 and the capacity gate.
- F32-CONFLICT (STATUS.md:323-324): the original AUTHORIZED controls versus OB-003. It needs its own design and independent review; PK-0 does not own it.
- Class H §9.6.4 a–d; native write construction; ABI and layout measurements; full proof of the contracts these predictions rest on (Collapse.Decide, Decide_Wire, Seal).
- The model-identity requirement of HANDOFF.md:173 against this Claude review.
