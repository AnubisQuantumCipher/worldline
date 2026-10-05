# PK-0 v3 author notes

PK-0 v3 revises the C-API characterization packet PK-0 in answer to the sealed source review of v2.
- Review: `packets/capi-pk0-v2/review/claude-v1`, an independent Claude review subagent. Under the human's direction of 2026-10-05 (about 17:05Z), independent reviews are now done by independent Claude review subagents. This changes nothing that the packet must satisfy.
- Verdict: ENDORSED_WITH_REQUIRED_CHANGES, with required changes RC-v2-1 to RC-v2-4. No run, control, proof, phase or source acceptance is granted.
- v1 (`packets/capi-pk0/`) and v2 (`packets/capi-pk0-v2/`) are unchanged. v3 is a new directory with the same layout: `packet.json`, `files/tests/*`, this file and `jackal.json`.

**Status: authored source, never run.**
- Nothing in this packet was executed, imported or compiled. It holds no run evidence and grants no control, proof or acceptance credit.
- The `json.load` and `ast.parse` checks in section 9 are text inspection only.
- The gate is unchanged: a baseline run on L0 in an admitted frame. It is blocked by the confinement gate (V5-B01, V5-B02) and the capacity gate.

## 1. Review identity

`sha256sum` (read-only) over `packets/capi-pk0-v2/review/claude-v1/` gave these values. The first three equal the entries of `review-freeze.json`.

| File | sha256 | bytes |
|---|---|---|
| REVIEW.md | `0246243a9c4e0bf83b77bd9482b2a864dc7d8862e6be326895ce6d12cc85ebcf` | 31756 |
| review.json | `d42e962d1d9271f06311898990a39b08c46c53c287fe2eefb7785b73eb8eb689` | 8679 |
| checks.json | `432c3a40025940261bc87ae545216733434ce15b7fb813316f02233ad7306ee7` | 8545 |
| review-freeze.json | `8d799c0faa1b05bd7552982a06b37f201bc763d82a104ba44323bf75db29d988` | 612 |

The REVIEW.md digest equals the one in the task message. `raw-final-message.txt` was not used.

## 2. Base and invariants (unchanged)

L0 is `W/work/claude-composition-v5-beta/source`. Its three identity files were re-observed and are unchanged:
- composition.json `a0e0bb5c…fa3e`;
- source-inventory.json `3407119b…937a`;
- review/gpt61-v1/review.json `df6cbc9d…3476`.

Invariants:
- REQUIRED_PROVED: 0 names appended. The 535-name prefix is carried; the v2 review counted it from the AST, and v3 did not recount it.
- `MINIMUM_CHECKS = 251` and `UNANALYZED_BOUNDARY = {"worldline-c_api"}`, re-read at `runtime/worldline/proof_manifest.py:22` and `:316`.
- 31 lines of `core/worldline-c_api.ads` contain External_Name (re-counted with `grep -c`).
- Movers: 0. No existing file is touched. None of the six payload paths exists in L0 (re-checked with `test -e`).

Bound inputs:
- All 100 v2 bound inputs were re-hashed. None differs in sha256 or size.
- v3 adds none. Every S5 path cited by the v3 record and modules is already bound (checked by script).
- The two host headers (`/usr/include/signal.h`, `/usr/include/bits/signum-generic.h`) were re-hashed and are unchanged.

## 3. Answers to the required changes

### RC-v2-1: one case per reachable nested guard conjunct of the mixed entry

The v2 C-03 text narrowed the rule to "one case per nested guard group". v3 restores v1's "one case per exercisable guard conjunct" without narrowing it. v3 adds the context arrays against the Context_Input descriptor to the list of refused overlaps, and says what the rule means for the mixed entry: Metadata_Base and Context_Matches have no export of their own (`core/evaluation_completion_c.ads:188-190`), so each of their exercisable conjuncts gets one U15y case.

The mixed export entry gains a `nested_conjuncts` table. It maps every conjunct of Metadata_Base, of the Context_Matches input-extent and transport guards, and of the Context_Matches field, row, row-field, required and join guards to its case and C-06 stream, or to `unexercisable`.

**New cases.** All are Kind 1 primary, with ready sources and an admitted Agent-origin record, and all expect 255 at primary-context-rejected. The conjunct is the same on every route. Each case changes one field of an adopted object through `mut`; every earlier conjunct still holds.

| Conjunct | Case suffix | Mutation | D-case |
|---|---|---|---|
| Metadata_Base `X.Version /= 1` (`:901`) | `metadata_version` | `p_meta.version` 2 | D56 |
| Metadata_Base `Extent_Valid (X.Base)` (`:901-903`) | `metadata_base_null` | `p_meta.base` null | D57 |
| `X.Version /= 1` (`:765`) | `context_version` | `p_meta_base.version` 2 | D58 |
| `Extent_Valid (X.Data)` (`:766`) | `context_data_extent` | Data_Length -1 | D59 |
| `X.Row_Count /= R.Captured_Count` (`:767`) | `context_row_count` | Row_Count 0 (the fixture has two captured rows) | D60 |
| `X.Required_Count /= R.Required_Count` (`:768`) | `context_required_count` | Required_Count 0 (the fixture has one required row) | D61 |
| `X.Policy` bound (`:769`) | `context_policy` | Policy U32_MAX (J04) | D62 |
| `Valid (X.Expected_Binding)` (`:773`) | `context_expected_binding` | Store_Id.First 0 | D63 |
| `Valid (X.Expected_Current)` (`:773`) | `context_expected_current` | Present 2 | D64 |
| `Valid (X.Prepared_Current)` (`:774`) | `context_prepared_current` | Present 2 | D65 |
| `Array_Valid (X.Rows)` extent (`:776`) | `context_rows_extent` | Rows null, count nonzero | D66 |
| `Array_Valid (X.Rows)` overlap with the descriptor (`:776`) | `context_rows_overlap` | Rows at the descriptor | D67 |
| `Array_Valid (X.Required)` extent (`:779`) | `context_required_extent` | Required null, count nonzero | D68 |
| `Array_Valid (X.Required)` overlap with the descriptor (`:779`) | `context_required_overlap` | Required at the descriptor | D69 |
| `X.Agent /= Raw_Agent` (`:780`) | `context_agent` | the context's agent source byte 0 (Engine), while the admitted Agent argument's is 1 (Agent; `runtime/worldline/core.py:72`, observed per case by the readiness probe) | D70 |
| `Valid (X.Observed (K))` (`:796`) | `context_field_observed` | observed field 0 First 0 | D71 |
| `Valid (Owned.Expected (K))` (`:821`) | `context_row_field_expected` | row 1 expected field 0 Present 2 | D72 |
| `Valid (Owned.Declared)` (`:840`) | `context_required_declared` | required pair 1 Declared.First 0 | D73 |

- Each has a guarded C-05 twin (`U15y_C05_k1_primary_<suffix>`). The twin puts every context and metadata object beyond the frontier on PROT_NONE, using `prefix` 1 for the row-field case.
- Each has an exact C-06 stream. The transport cases end in `completion.context.transport-guard-rejected`. The Metadata_Base cases end in `completion.context.input-extents-rejected` (Context_Matches receives Null). The field, row-field and required cases end at their own sites.
- The last three rows go beyond the transport conjuncts that RC-v2-1 names. The restored C-03 text covers every guard conjunct, and v2 exercised only one conjunct of each of those disjunctions (Expected but not Observed, Observed but not Expected, Check_Id but not Declared). Leaving them uncovered would have narrowed C-03 by omission.
- Agent_Confinement keeps its four v2 cases (D31, D35, D48, D53). The input-extents conjunct on Context keeps its two null-context cases (D41, D49) and gains D56 and D57.

**Unexercisable, each with its reason** (`exports.wl_collapse_decide_finalization_v1.unexercisable`):
- The v2 entries are carried: Collapse misalignment, the seal refusal and Operation /= 3.
- `Valid (X.Start.Required)` (`evaluation_finalization_c.adb:282`) cannot be reached at all: Read_Ready's Decide refused every request without `Valid (X.Start)` (`:145`, `:59-64`), on the same bytes.
- **The Start.Required length and First conjuncts (`:283-286`) are unexercisable only on a condition.** The condition is Seal's postcondition, which is on the required-proved roster but is not proved here, so this is stated as conditional, not as fact. The chain is:
  - Decide gives Reason 0 at Operation 3 only on Seal_Observed (`:231-232`).
  - Seal's Post makes the result Seal_Reference (`evaluation_finalization.ads:394-398`), and Seal_Reference's Post makes it Seal_Equation (`:377-386`).
  - Seal_Equation is Seal_Observed only under Capture_Valid (`:353-374`).
  - Capture_Valid implies Input_Valid (`:194-200`), then Same_Start (`:121-125`), then Start_Valid (`:107-108`), then Plan_Valid (`:95-106`), then Valid_Checks (`:74-79`; `evaluation_raw_roster.ads:153-155`).
  - Valid_Checks over the Plans array `1 .. Required_Count` bounds First and Length.
  - The entry also says that, if the postcondition did not hold, these conjuncts would need a case.
- Context_Matches Input, Collapse and Agent extents, each refused earlier on the same address:
  - Input: Raw_Decide `:538` for Kind 1; Kind 2 passes the local projection.
  - Collapse: the entry's own check at `:412-414`.
  - Agent: Agent_Ready = 1 requires the agent extent check at `:453-458`.
- A non-null bad Context address cannot be produced: Metadata_Base returns Null or an address it has already extent-checked.
- The R-side transport conjuncts (R.Version, R.Operation, R.Policy, the roots, Captured, Current, R.Data):
  - Kind 1: Raw_Decide refused them on the same bytes (`:545-560`).
  - Kind 2: the projection is built from constants and from fields that the finalization Decide validated. Captured's State and Outcome come from Seal's Classification, whose State has subtype Terminal_State (`evaluation_raw_roster.ads:31-35`), so Valid (Capture) holds by type.
- The extent parts of R.Captured_Results and R.Required are already checked: by Raw_Decide (Kind 1), or they are Ada locals (Kind 2). Their overlap with the descriptor on Kind 2 involves locals, so it is outside the premises (class X).
- The count and stride sub-conditions of Array_Valid on X.Rows and X.Required follow from the count equalities and from the nested decisions that read every row.
- The request-side row and required-pair validity conjuncts (`:812`, `:839`):
  - Kind 1: Raw_Decide refused invalid rows on the same bytes (`:602`, `:641`).
  - Kind 2: the projected rows are built from rows that passed `Valid (Row)` (`evaluation_finalization_c.adb:67-72`) and from constant zero fields.

**`not_exercised` is kept only for the two items that carry their own reason:**
1. The Metadata_Matches transport conjuncts through this entry. Each is covered at Metadata_Matches' own export (U14m), which the review accepted.
2. **The Kind 1 refused overlap of R.Captured_Results and R.Required with the Context_Input descriptor (`:777-778`). This is OPEN: reachable in the source, but not constructed.** Those arrays are the Input's own rows. Raw_Decide reads them in full before readiness is set. With 64-bit fields, any overlap makes at least one descriptor word equal to bytes of the S5 fixture's accepted rows. The descriptor's earlier transport conjuncts (X.Version = 1 first, through X.Agent and X.Agent_Confinement at its end) would then have to hold on those bytes. I found no placement that satisfies them without changing the fixture's row bytes, which are Read_Ready's input. The harness has no straddling placement either. I record this as an engineering obligation, not an unexercisability claim (deviation 2).

### RC-v2-2: readiness observed per case, and the corrected claims

**Readiness is observable per case (the preferred option).**
- Every U15y case (84; J39) now declares `expect.readiness`.
- In the same forked child, after the oracle prelude and immediately before the export call, `probe_readiness` (passed to `capi_guard_pages.execute` as `probe`) observes the needed sources and the agent:
  - Kind 1: `wl_completion_raw_decide_v1` on the source's Input, Raw and Confinement. Valid when it returns 0, the reason is Retain_Terminal or Already_Retained, and Promotion is at most 1. Ready is the Promotion.
  - Kind 2: `wl_finalization_decide_v1`. Valid when it returns 0, Reason is 0, Promotion is at most 1, and the re-read header has Operation 3. This is Read_Ready, `evaluation_finalization_c.adb:370-398`.
  - Agent: `wl_evaluation_wire_admit`, whose body is Confined_Admit_Wire on the same record bytes (`worldline-c_api.adb:729-735`), together with the record's source byte. Ready is 0 for a non-Agent source, as at `evaluation_finalization_c.adb:463-469`.
- `assert_ready` then requires, for each declared side:
  - a needed source is valid;
  - the agent record is admitted (not 255);
  - the observed readiness equals the declared value. That is 1 for each needed source and for the agent, and 0 for the agent in the Engine-origin cases.
- `test_record_shape` requires every child-built case to declare readiness, including the agent.
- A fixture that fails Read_Ready or agent admission now fails each refusal case on its own, guarded twins included, instead of passing as a 255.
- The probe's outputs are child-local and outside the guarded mapping. Diagnostic children do not run the probe, so the C-06 streams are unchanged.

**Corrected claims.**
- The `collapse_ready` oracle checks only the collapse half: that the request with the ready roster flags is Authorized. Its docstring, C-11 and this note say so. Readiness is the probe's job.
- **Route coverage, stated per route.** It is not "for each route". The nested conjuncts are the same on every route, and per-conjunct coverage is on the Kind 1 primary route:

  | Route | Cases |
  |---|---|
  | primary, Kind 1 | Authorized (and an `end` twin); Engine-origin agent; every nested Context_Matches and Metadata_Base case above; null context; metadata payload, row and transport after Authorized |
  | primary, Kind 2 | Authorized (and an `end` twin); transport (confinement); join false (binding); inner metadata; null metadata; Engine-origin agent |
  | staged, Kind 2 | Authorized (and an `end` twin); transport |
  | staged, Kind 1 | Authorized; join false (subject); metadata payload |
  | both, Kind 2 primary / Kind 1 staged | Authorized; primary transport first; staged join false; staged metadata payload |
  | both, Kind 1 primary / Kind 2 staged (new) | Authorized: U15y_R3_both_k1_primary_authorized, D74 |
  | both, Kind 1 / Kind 1 (new) | the primary Kind-1 metadata join runs and holds before the staged one is refused: U15y_R1_both_k1k1_staged_metadata_payload, D75 (`:491-502`) |

  Engine-origin agent cases are primary-only.
- **The both route is not "the genuine S5 decide_mixed mix".** S5 `decide_mixed` accepts either kind on either side (`finalization_kernel.py:296-306`). v3 covers three of the four kind pairs. The fourth pair, Kind 2 / Kind 2, adds no nested conjunct and is not claimed.
- **Not every refusal has three checks.** These seven refusal cases have no C-05 twin because no context or metadata object remains unread after them (J42):
  - k2_primary_context_metadata;
  - k2_primary_context_null;
  - k1_primary_context_null;
  - k1_primary_metadata_payload;
  - k1_staged_metadata_payload;
  - both_staged_metadata_payload;
  - the new both_k1k1_staged_metadata_payload.

  They are listed with reasons in `no_twin`. Every other U15y refusal has an unguarded case, a guarded twin and a C-06 stream. Every refusal case now also has its own readiness observation.

### RC-v2-3: bytecode refusal before any non-stdlib import; "writes no file"

- `test_capi_characterization.py` refuses `--record` immediately after its standard-library imports and before `HERE`, `capi_guard_pages` and any `worldline` import, when `sys.flags.dont_write_bytecode` is false. `record_main` keeps the same check.
- `--measure-headers` now has the same refusal as its first statement. The layout module's top-level imports are standard library only; `worldline` is imported inside functions.
- The normal header test cannot be gated from source, because unittest imports runtime modules first. Its scratch-only claim is now qualified in the module docstring as holding only under launch obligation 1.
- "Opens no file" is replaced by "writes no file" in the three modules, `packet.json`, and this note. The baseline JSON's status line (unchanged) never said "opens".

### RC-v2-4: the negative control's status reaches a captured channel

`HarnessFaultControl.test_protection_fault_is_never_a_code` writes one JSON line before any assertion: `{"harness_fault_control": {"wait_status", "signaled", "signal", "describe", "report_bytes"}}`.
- It writes the line with `os.write` to file descriptor 1, which the admitted launch captures byte for byte (launch obligation 5).
- A passing run therefore leaves the observed wait status and signal in the launch's stdout, and so does a failing run.
- Launch obligation 6 is now satisfiable from the run's own output. It stays OPEN until the launch runs.

## 4. Change list against v2

`packet.json` lists each file with its v2 and v3 sha256 and bytes.

| File | Change |
|---|---|
| `capi_characterization.json` | `design.revision`. C-03 restored and extended, plus C-05, C-06 and C-11 text. The mixed entry gains `nested_conjuncts` and `no_twin`. Its `unexercisable` gains the reasoned entries, and `not_exercised` keeps only its two reasoned items. Every U15y case gains `expect.readiness`. 38 U15y cases (18 refusals, J41; 18 twins; 2 both-mode cases; J40) and 20 diagnostic cases (D56-D75) are appended. Everything else is unchanged by JSON comparison: all 609 v1 cases, all 28 v1 diagnostic cases, the other 19 exports, and the classes and join frontiers of the mixed entry. v2's 46 U15y cases differ only by `readiness`, and v2's 27 diagnostic cases are unchanged. |
| `test_capi_characterization.py` | Revision v3. `--record` gate moved ahead of the non-stdlib imports (RC-v2-3). Readiness probe (`_call`, `_probe_side`, `_probe_agent`, `probe_readiness`), `assert_ready`, and the probe passed by `run_case`. Record-shape check for readiness (RC-v2-2). Oracle docstring corrected. Comment citing S5's own positive control. HarnessFaultControl stdout line (RC-v2-4). `EVALUATION_ORIGINS` import. "writes no file" wording. All v2 builders, mutations and expectation logic are unchanged. |
| `capi_guard_pages.py` | `execute` takes an optional `probe`. It runs after the fault policy is established and the prelude has run, and before the "before" snapshot and the export call. Its result is reported as `probe`. Docstring revision v3; "writes no file". |
| `test_capi_layout_identity.py` | `--measure-headers` gate (RC-v2-3). Qualified header-test claim. "writes no file" wording. `require_output_only_launch(mode)`. |
| `test_capi_diagnostics.py` | Revision v3 and "writes no file" wording only. |
| `capi_layout_baseline.json` | Unchanged (byte-identical to v2). |

## 5. Placeholders (RECORD_ON_L0; none can pass)

These are unchanged from v2:
- the 179 layout values (J33);
- the written results of U14d_R3_classify_op2_record, U15f_R3_capture_op2_record and U15f_R3_seal_op3_record;
- D06.

v3 adds no placeholder. The count of RECORD_ON_L0 occurrences in the record is the same as in v2. Every new expectation is derived from the source.

## 6. F32-CONFLICT: not decided

- Every U15y request keeps v2's Resulting_Requirement = Current_Requirement shape. The code now cites the S5 positive control of the same shape, `test_collapse_recomputes_carried_roster` (`test_raw_evaluation_default.py:471-490`).
- No case asserts a decision code for the exact S5 request with Resulting_Requirement absent.
- No S5 test or original control is edited.
- What those original AUTHORIZED controls mean is owned by the separate F32-CONFLICT obligation.

## 7. Uncertainties (in addition to v2's, which stand)

1. The new cases rest on the S5 Kind 1 fixture's shape:
   - two captured rows, one required row;
   - every context field and row pair as `joined` builds it (`tests/test_raw_evaluation_default.py:48-69, 79-80`).

   If the shape differs, the affected case fails visibly; nothing passes by another route. The readiness probe also checks the agent source byte that `context_agent` relies on.
2. `_adopt` must name the context objects `p_meta`, `p_meta_base` and `p_meta_base_rows`/`_required`/`_data` exactly as v2's guards already assume. A wrong name fails the case as a PlacementError or a KeyError.
3. Two Kind 1 fixtures in one child (D75) are independent `RawRequiredFailureControls` instances. That they share no module state is assumed from the source and not run.

## 8. Deviations

1. The review is by an independent Claude review subagent (human direction of 2026-10-05). This packet takes no position on the model-identity question the review records.
2. The Kind 1 request-array overlap with the descriptor, which RC-v2-1 names, is not constructed. It is OPEN with its reason (§3, RC-v2-1).
3. Readiness is observed by a separate per-case probe, not by the prelude the review gave as an example. The prelude remains the relational oracle; the probe is a distinct call so that the oracle's meaning does not change.
4. Three element-guard conjuncts were added beyond the letter of RC-v2-1 (§3), so that the restored C-03 is not narrowed by omission.
5. Carried from v2: the U15y requests add Resulting_Requirement (§6). The header test requires the scratch binding. Launch obligations remain OPEN.

## 9. Process record

**Writes.** Write and Edit only, only under `WT/packets/capi-pk0-v3/`. No write was refused. The record was built by Write followed by Edit appends. The reproduced v2 text was compared with `diff` after each append.

**Bash, read-only.** `sha256sum`, `sed -n`, `grep`, `awk`, `wc`, `test -e`, `diff`, and Python heredoc scripts that only read and print (`json.load`, `ast.parse`, `hashlib`). No redirection, mkdir, cp, mv, rm, tee, chmod or touch. Nothing touched `/home/sicarii` itself, `~/iPad`, `~/iPadBackup` or `.gbrain`. My own transcript was read once, to look for pre-compaction notes; no other transcript and no `review-records/` file was read.

**Nothing executed or interrupted.**
- No test, pytest, WORLDLINE module, packet module, compiler, prover or native build was run or imported.
- No TaskStop, kill, timeout wrapper or background task was used.

**Services.**
- SIA: one `sia.ask` at the start, and no note.
- JACKAL:
  - J34-J42 were called in three sequential groups of at most four. Each is exact, formal false, lane rat, evaluator `4c0ae28d…d872`.
  - J01-J33 are carried.
- All eight Ada skills were loaded again after a context compaction, before the Ada sources were re-read.

**Verification, by text only.**
- Every JSON file loads and every Python file parses.
- 693 cases (J34) with unique ids, and 75 diagnostic cases (J35).
- v1 and v2 content is carried as stated in §4.
- Every diagnostic call names an existing case. All 47 unguarded U15y cases have a D-case (J36). There are 37 guarded U15y cases (J37) and 95 guarded cases in all (J38).
- Every guard name is one that `_adopt` derives. Every child-built case declares readiness for exactly its needed sides plus the agent.
- Every U15y refusal either has a twin or is listed in `no_twin`.
- Every case id that `nested_conjuncts`, `unexercisable`, `not_exercised` and `no_twin` cite exists.
