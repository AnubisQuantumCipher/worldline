# C-API raw-pointer boundary consolidation: design v3

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent) |
| Date | 2026-10-04 |
| Status | **DRAFT_FOR_GPT61_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. |
| Supersedes | `W/work/claude-capi-boundary-design-v2/DESIGN.md` (sha256 `554fe8b0…a705d3`) and its `decisions.json` (sha256 `db403247…bf159d`) |
| Answers | The actual gpt-6.1-sol review of v2, verdict ENDORSED_WITH_REQUIRED_CHANGES (`review/gpt61-v1/review.json` sha256 `42b762d9…e29ff`, `REVIEW.md` sha256 `485e5288…a95d`): required changes RC1–RC6, and the rulings LD1–LD6, D-13, N-01, N-06, D-05, D-18, D-19, D-28, D-36, D-15/D-34/D-38, N-03, N-04, N-05, R2_NINE_CONDITIONS, APPENDIX_C and PACKET_PLAN. |
| Scope | Proof-source design only. It grants no execution, proof, build, test, review, operator or acceptance authority. |
| Location | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v3/`: a linked git worktree (`wt-1`, branch `lead-wt-1`, identity recorded in `wt-1/ISOLATION.md`) that the lead created as the guard-compatible write destination. |
| Companion files | `decisions.json` (machine twin), `APPENDIX-BINDINGS.md` (A-BIND: RC4/RC5 detail — per-stage binding tables, exact declarations, ordered tokens, predecessor edits, identity bindings, override sketch) and `APPENDIX-COST-MAP.md` (A-COST: RC6 detail — the type- and call-site-resolved native cost map). All are in the location above; their identities are in Appendix D. |
| Write history | The Write tool refused the first location, `W/work/claude-capi-boundary-design-v3/DESIGN.md`, at 2026-10-04T19:29:13Z (the background-isolation guard). That directory had been created empty with `mkdir` at 19:17Z; it is preserved untouched and carries no clearance. A later heredoc attempt at 19:44Z, under a fallback that the operator's monitor has since withdrawn, failed at process spawn (E2BIG) and wrote nothing. Every file in the location above was written once, with the Write tool. |

---

## 0. Truth boundary, bases and reading rules

**Nothing was executed.**
- No compiler, prover, gprbuild, gnatprove, test, WORLDLINE code, service, vault or restic action was run to write this design.
- No WORLDLINE Python module was imported.
- The proof manifest was read as text and through Python's standard `ast` parser.
- The exact declarations, diagnostic site sequences and counts in the appendices were extracted by read-only Python scripts over S5 text. Those scripts reimplement `normalized_ada` rather than importing it.
- The burn-down ledger was read with `ledger.py report` (read-only) and by reading `ledger.json`.

**Nothing is closed by design.**
- Every proof, flow, RTE, termination, strict-warning, native-cost, ABI, layout, custody, control, review and acceptance obligation in this document is **OPEN**.
- Words such as "total", "proved", "initialized" and "preserves" describe design intent.
- That intent must still be established by:
  - the exact strict command;
  - the original ordered roster;
  - the lifetime and additive controls;
  - matching native evidence;
  - independent actual gpt-6.1-sol review.

**Bases.**
- `W` = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`.
- `S5` = `W/work/claude-composition-v5-beta/source`. This is the current QUALIFIED_SOURCE_COMPOSITION candidate. Its identities: composition.json sha256 `a0e0bb5c…fa3e`; source-inventory.json sha256 `3407119b…937a`; review `review/gpt61-v1/review.json` sha256 `df6cbc9d…3476`, disposition QUALIFIED_SOURCE_COMPOSITION, with proof, source and phase acceptance all false. **Unprefixed paths are relative to S5.**
- `S4` = `W/work/reviewed-common-proof-source-composition-v4/source`, the reviewed base that the v2 review read.
- **Observed identity between S4 and S5** (sha256 comparison, read-only):
  - Byte-identical: all 15 C-API units; `core/worldline-c_api.ads`/`.adb`; `core/evaluation_completion.ads`/`.adb`; `core/worldline_core.gpr`; `core/worldline_core_sources.gpr`; `pending-component/pending.gpr`; the four pending-component `evaluation_pending{,_v2}_c` files.
  - Different, and relevant here:
    - `core/worldline-recovery.ads`: S5 packet 01 removed the Optional_Marker default discriminants. Operator approval record: `W/work/claude-lead-v2/approvals/optional-marker-api-v1/approval.json`.
    - `core/evaluation_finalization.ads`/`.adb`: reassociation parentheses at ads:287 and :289 and adb:84-97; additive ghost lemmas at adb:151-257; one ghost lemma call at adb:280-281.
    - `runtime/worldline/proof_manifest.py`: lines 1–1023 identical; S5 appends lines 1024–1029.
  - Every `file:line` citation into the 15 units, the C_API pair and manifest lines ≤ 1023 therefore holds for S4 and S5 alike.
- `H` = `W/outputs/claude-phase1-handoff-20261004`; `P` = `/home/sicarii/Documents/complete-phase1-prompt.txt`.
- `MAP` = `W/work/claude-lead-v2/executions/f10k-retry1/diagnostic-map-v1.json`; `STRICT` = `…/strict-report-analysis-v1.json`; `LEDGER` = `W/work/claude-workflow-v1/ledger.json`. D-numbers such as D0075 below are ledger item ids.
- `G` = `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1` (installed tool, read-only).
- `v2:N` = line N of the v2 DESIGN.md. `A-BIND §x` and `A-COST §x` = sections of the two appendix files.

**Markers in staged sequences.**
- **[T]** Irreducible transport in `Worldline.C_API`, the sole `UNANALYZED_BOUNDARY` (`SPARK_Mode => Off` at `core/worldline-c_api.ads:6` and `core/worldline-c_api.adb:25`).
- **[S]** A SPARK routine in an existing On unit, analysed under the strict command.
- **[P]** Plumbing. The transport routes control on a value or verdict *returned by* SPARK or a nested transport, or converts such a scalar to a diagnostic argument. It never computes a value condition itself (D-03).

**Numbers.**
- A count read from a file or tool output is reported as *observed*.
- Every derived number (sum, difference, cumulative total) was routed through the JACKAL MCP tool `jackal_exact`. Each result was `status=exact`, `formal=false`, with assurance "exact rational arithmetic (not yet checker-covered)", and carries the non_claims listed verbatim in Appendix A.
- These are arithmetic facts about file observations, informational only about code correctness. They prove no source, ABI, proof or native property.

---

## 1. Trace: every required change and ruling to its v3 answer

### 1.1 Required changes RC1–RC6

| Item | What the review requires | v3 answer | Exact v2 text that changed | Remains OPEN |
|---|---|---|---|---|
| **RC1** | Keep diagnostic state/control/value logic in analysed SPARK; isolate only irreducible stderr/exception-text transport in `Worldline.C_API`; replace LD4; mirror in decisions.json. | §2.4 (LD4 withdrawn, LD4-R), §4 (complete SPARK state machine, transport, irreducibility, access-sequence equivalence, analysability), §8.5 (manifest confinement checks), §14 (boundary surface), A-BIND §B4.24 and §B6, A-COST §C18, decisions.json `LD4-R` | v2:128 "### LD4. The stateful diagnostic export moves into the boundary unchanged"; v2:131 "- These move into `Worldline.C_API` with unchanged behaviour:"; v2:1802 "**`Native_Diagnostic_Control` and the diagnostic procedures** are verbatim adb:39-88 (LD4)."; v2:2628 (D-16) "They move to the C_API body unchanged."; v2:2687 (I4) "LD4 relocates them to C_API." | Installed-tool legality of the external abstract state, `'Image` length modelling and catenation proofs (§4.7); full proof; C-06 controls |
| **RC2** | Initialized, total value interfaces for finalization `Captured` on Operations 0/1 and for every output of the completion context acceptors; exact non-narrowing array/index invariants for completion decisions. No new ABI refusal, count cap, unproved helper Pre or assumed initialization. | §5.1 (separate no-row and with-row value routines; `Captured` allocated but never passed or read on Operations 0/1), §5.2 (context acceptors become total variant-record functions), §5.3 (every out formal defined on every path), §5.4 (exact invariants; `History_Index` route; no bounds re-check), §5.5 (D-19 candidate), §5.6 (D-28) | v2:1889 and v2:1897, the two procedures annotated "`--  adb:795-804 loop, verbatim`" and "`--  adb:812-829, verbatim`"; v2:1927-1929 "(a) if not (Decide_Header_Valid (R) and then Decide_Fields_Valid (R)), or any fact the original declarations supplied fails (1-based arrays whose lengths match the R.*_Count fields, D-18), then Status := 255 …"; v2:210 "**Facts the original body had.** … the routine re-checks them at entry. It returns the original refusal code (255 / -1) if they fail."; v2:2058 "8. [S] `O := Decide_Value (X, A, Required, Captured)` …"; v2:2170 "Captured is unread when Operation <= 1." | Proof of every routine; D-05 decoder totality; installed-tool flow results |
| **RC3** | N-01 is an unchanged strict obligation; no informational waiver and no relocation-as-closure; any confirming representation clause repair is a reviewed ABI-preserving delta with strict proof and matching layout evidence. | §10 (strict obligation; 617 staying + 119 moved observed; moved occurrences are **not** counted as resolved; confirming-clause delta method, constraints, evidence, failure rule), §9.7 (placement PK-xR), §15 C-13 | v2:2651 N-01 row classified "**OPERATOR DECISION** … **(a)** The operator confirms they are informational for strict acceptance … **(c)** Move the layout queries into C_API." | Every representation warning until the strict command shows it resolved; layout identity on every actual target |
| **RC4** | Enforceable manifest binding: whole-closure alternate-binding checks; ordered required calls and exact result-to-write paths; preserved predecessor assertions; identity binding for all touched source/project/component/control/provider files. | §8 (checks G1–G8, K1–K4, P1–P3, O1–O7, D1–D5, PP1–PP3, identity layers I1–I7, mutation controls), A-BIND §B1–§B8 (literal tables per stage, exact declarations with sha256, ordered tokens per isolated unit, exact predecessor edit texts, identity per stage, override sketch) | v2:2311 "`for symbol, home in INVENTORY_HOME.items():`" and v2:2324 "`or any(call not in body for call in calls)`" (membership only); v2:2332 "The C_API body must contain no `Import`/`Link_Name` for any inventory symbol." (C_API only); v2:1344 "This design adds no component pin key, because adding keys would change `proof_source_files`"; v2:2289 "no `#` keys and no component keys are added (D-12)" | Manifest code unwritten; the O6 (b)/(c) inventory check is not yet in the sketch; mutation controls unrun; matching-library export evidence |
| **RC5** | Complete intermediate binding tables; monotonic append schedule matching the final Appendix C; PK-7a enrolled and pinned immediately; exact composition lineage; original-behaviour characterization; representation-repair placement; PK-8 seal limits. | §9 (lineage L0 = S5 with rebase rule; strictly linear single-packet stages; packet table PK-0…PK-7R and PK-S; append schedule equal to Appendix C order; PK-6a enrols and pins at once; characterization of defined effects only; PK-xR placement; seal limits), A-BIND §B1–§B2, §B7 | v2:2714 PK-1 "Adds the new final `export_problems` override with the full 60-symbol `INVENTORY_HOME` table."; v2:2716 PK-3 "U12 run ledger and U13 chain" (before U6–U11 in v2 Appendix C order); v2:2720 PK-7a lists no manifest delta; v2:2722 PK-8 "Every pin is regenerated by the tool."; v2:2706 "authored in a fresh isolated checkout from commonV4"; v2:2581 C-01 "must be byte-identical after every 255/-1 path" | All stages unauthored; reviews per stage; D-13 blocks PK-7 and therefore PK-S |
| **RC6** | Replace by-reference/no-copy and "all other evaluation deltas zero" statements with a type- and call-site-resolved native cost map (rechecks, acceptance/marker/result copies, initialization, assertions, allocation, exception/write effects); keep D-36 and the original native blockers OPEN. | §11 (withdrawn statements, classification rules, per-export summary, generalized D-36), A-COST §C0–§C21 (every call site, with RM 6.2 category per type) | v2:2510 "**Arrays are not copied into SPARK.** They are passed by reference as `in` or `in out` formals."; v2:2537 "\| all other exports \| 0 \| n/a \| n/a \|"; v2:2503 "Every existing relation is called … as many times as on the original path, with the three constant-time exceptions in §10.3."; v2:156 "Both `Well_Formed` relations are bounded and constant-time"; v2:2648 (D-36) "That aligns with the documented no-write-on-refusal contract … The reviewer is to confirm it is equal-or-stronger behaviour." | Every native cost, passing-mechanism, copy, allocation, assertion, failure and write-construction obligation; D-36; D1/D2/D-35 blockers |

### 1.2 Rulings

| Ruling | Review disposition | v3 answer | Exact v2 text that changed | Remains OPEN |
|---|---|---|---|---|
| LD1 | ACCEPTABLE_WITH_REQUIRED_REPAIRS | §2.1, §3.1 rules M1–M4 (short-circuit order within and between runs; every intervening transport operation, allocation and early return kept; no prevalidation) | v2:83 "Value checks move to SPARK…" kept; repairs added | Custody; installed proof |
| LD2 | CONDITIONALLY_ACCEPTABLE | §2.2, §3.2 rules V1–V9 (A1: discriminant tested before payload; out formals defined on every path; Global null is not functional) | v2:104 "Reading `.Item` when `Ok = False` raises in Off code, which fails closed into the original handler code."; v2:210 (bounds re-check) | D-05, D-18 proofs |
| LD3 | CONDITIONALLY_ACCEPTABLE_PENDING_D-13 | §2.3, §16.1 (D-13 operator item; only ABI-preserving routes) | v2:2625 option list (now an operator item with evidence per option) | Operator choice; component evidence |
| LD4 | NOT_ACCEPTABLE_AS_WRITTEN | Withdrawn; replaced by LD4-R (§2.4, §4) | v2:128-143 | See RC1 |
| LD5 | CONDITIONALLY_ACCEPTABLE | §2.5 (both wire contracts kept; extra checks costed, not called constant-time; D-36 OPEN; Ok/Value variant optional) | v2:156 "bounded and constant-time" | Native delta; D-36 |
| LD6 | ACCEPTABLE | §2.6, §9.6, §15 (controls added, never substituted; PK-0 encodes defined original behaviour only) | v2:2581 C-01 scope | Every control run |
| D-13 | OPERATOR_CHOICE_REQUIRED_BEFORE_PK-6; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE | §16.1 operator item (the pending packet is PK-7 in v3 numbering) | v2:2625 | Operator decision |
| N-01 | STRICT_OBLIGATIONS; CONFIRMING CLAUSES CONDITIONALLY ADMISSIBLE; NO WAIVER OR RELOCATION CLOSURE | §10 (lead-owned strict obligation; operator reviews only a material ABI decision, none proposed) | v2:2651 | All representation warnings |
| N-06 | REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT; OLD LIBRARY CANNOT COUNT | §16.2 operator item | v2:2656 option (b) "Keep the old library for the protected service" | Operator decision at deployment |
| D-05 | OPEN_FULL_DOMAIN_HELPER_AND_INSTALLED_TOOL_PROOF | §3.2 V8, §17 (decoder inventory, decision procedure, no helper Pre approved) | v2:2617 "LEAD_DECIDED (LD2); evidence OPEN" | OPEN |
| D-18 | OPEN_INDEX_PROOF; NO_NEW_ABI_REFUSAL_GUARD | §5.4 (exact invariants; `Evaluation_Completion.History_Index`, already in REQUIRED_PROVED, replaces the bare index; no bounds or equal-length guard) | v2:2630 "Refuse 255 if they fail, which is unreachable from the transport" | Proof |
| D-19 | OPEN_STRICT_WARNING_AND_BRANCH_CORRESPONDENCE | §5.5 (the raw value routine re-checks the Decide header predicate, not the raw Operation gate, so no branch becomes dead in SPARK; the gate stays in the transport chain) | v2:2631 "If `--proof-warnings=on` reports them as dead … escalate to the operator." | OPEN until strict evidence |
| D-28 | FIXED_VALID_LOCAL_INITIALIZATION_ACCEPTABLE; NATIVE_DELTA_OPEN | §5.6, A-COST §C16 | v2:2640 "This is unobservable" (now costed) | Native delta |
| D-36 | LOCAL_THEN_WRITE_IS_A_CANDIDATE; EQUIVALENCE NOT ESTABLISHED | §3.4, §11.4 and A-COST §C19 (generalized to every export whose write construction changes), C-14 separated from baseline | v2:2648 | OPEN |
| D-15/D-34/D-38 | OPEN_MATCHING_NATIVE_EXPORT_LAYOUT_AND_INSTALLED_TOOL_LEGALITY | §8.9, §17 | v2:2627, v2:2646, v2:2650 | OPEN |
| N-03 | OPEN_EXISTING_CALLEE_PROOF_AND_WARNING_OBLIGATIONS | §17, §18 | v2:2653 "Out of this design's scope." (kept OPEN, scope stated) | OPEN |
| N-04 | ADDITIVE_ENROLLMENT_RECOMMENDED | `Evaluation_Completion_Roster.Classify` appended (Appendix C position 68); new analogue N-07 enrols `Evaluation_Pending.Decide` and `Evaluation_Pending_V2.Decide` (positions 93, 98) | v2:2654 "It is not part of the 82-name append." | Proof |
| N-05 | STATIC_AUDIT_IMPORT_ROUTE_UNVERIFIED; DO NOT WEAKEN | §17 (import route resolved by reading; assertion retained; pre-existing inconsistency recorded OPEN) | v2:2655 "Not verified which module the test loads" | OPEN |
| R2_NINE_CONDITIONS | SOUND PROTECTIONS; INCOMPLETE ENFORCEMENT AND PACKET PLAN | §8 (all nine conditions with enforceable checks), §9 | v2:2282-2292, v2:2305-2332 | Manifest code, mutation runs |
| APPENDIX_C | LITERAL SUFFIX SOUND; STAGED ORDER REQUIRES REPAIR | Appendix C v3 (98 names) in packet order; §9.3 | v2:2921-3008 (82 names; U10/U11 before U12/U13) | Proof of every name |
| PACKET_PLAN | REVIEWABLE; NOT IMPLEMENTATION READY | §9 | v2:2702-2732 | Every stage |

### 1.3 v1 requirements R1–R6

The review recorded R4 and R5 as CLOSED_AT_DESIGN_LEVEL. v3 keeps their substance (§13, §14) and changes nothing they closed, except the boundary inventory (§14), which now lists only diagnostic I/O transport (RC1).

R1, R2, R3 and R6 were NOT_CLOSED. Their gaps are exactly RC1–RC6 above.

---

## 2. Lead decisions retained with their repairs, and the replacement for LD4

### 2.1 LD1. Transport follows the owner-transition precedent (retained)

**Decision.**
- Raw address, extent, alignment and null guards, and every raw read and write, live in `Worldline.C_API` in their original order.
- Value decisions live in SPARK.
- The enlarged unproved surface is enumerated per export (§14) under OB-048, which stays OPEN.

**Repairs required by the ruling, applied as rules M1–M4 (§3.1).**
- Maximal value runs preserve the original `and then`/`or else` order within and between runs.
- Every intervening transport operation, allocation and early return stays where it was.
- No value is prevalidated ahead of the original read stage.
- LD1 licenses no non-transport state and no semantic exemption, and establishes no custody.
- In v3 the diagnostic state is no longer in the boundary (§4).

### 2.2 LD2. Value routines are total and carry no added functional Post (retained)

**Decision.**
- No new `Pre` on any routine the transport calls, and no added functional `Post`.
- Existing relation contracts are unchanged and are evaluated where they were.

**Repairs, applied as rules V1–V9 (§3.2).**
- `Global => null` is an effect boundary, not a functional guarantee.
- Complete value-body/encoding correspondence and every malformed domain are preserved.
- Every out formal and every function result is defined on every path.
- An acceptance record's payload is read only after its discriminant has been tested (A1). A discriminant check is never a designed control path.
- The `Captured` input (RC2), D-05 and D-18 are handled in §5 and §17 without new narrowing guards or assumptions.

### 2.3 LD3. The pending-component Off copies mirror every core split (retained, pending D-13)

**Decision.**
- `pending-component/core/evaluation_pending{,_v2}_c.*` stay exact duplicates of the core files except for the `SPARK_Mode` line. Observed today: spec line 5, `evaluation_pending_c.adb` line 5, `evaluation_pending_v2_c.adb` line 6.
- The component's original separate native and ABI controls are kept (`W/work/integrated-proof-preparation/PLAN.md:104-107`).

**Repairs.**
- The mirror is never applied in a way that silently drops the component's `Decide` exports.
- Only an ABI- and scope-preserving component route is admissible. Choosing it is an operator decision (D-13, §16.1).
- A component-local Off transport relocates code that is already Off in the component. It creates no new WORLDLINE exception and earns no proof credit.

### 2.4 LD4 is withdrawn; LD4-R replaces it

v2's LD4 moved the two `Atomic` globals, the check-then-act control and the three diagnostic procedures wholesale into `Worldline.C_API`. The review ruled it NOT_ACCEPTABLE_AS_WRITTEN.

**LD4-R.** These stay in the analysed SPARK unit `Evaluation_Completion_C`:
- the diagnostic state and every state transition;
- the control decisions and return codes;
- the failure latch;
- the line text composition;
- the catenation-overflow handling.

`Worldline.C_API` keeps only:
- (T1) `Put_Line` and (T2) `Flush` on `Standard_Error`;
- (T3) the handlers that report their failure to SPARK;
- (T4) `Ada.Exceptions.Exception_Information`, on an occurrence that exists only in transport handlers;
- (T5) the call sequence that interleaves SPARK steps with T1–T4.

§4 gives the design, the irreducibility argument for each transported item and the equivalence of the atomic access sequences.

### 2.5 LD5. Recovery authorization v2/v3 uses option A plus a minimal wrapper (retained)

**Decision.**
- The transport calls the existing total `W.Well_Formed` directly before any write (`worldline-recovery_authorization_c_api.adb:141`, `worldline-recovery_authorization_v3_c_api.adb:158`).
- A minimal total wrapper, `Decide_Total`, discharges `W.Decide`'s `Pre => Well_Formed` (`worldline-recovery_authorization_wire.ads:165`; `worldline-recovery_authorization_v3_wire.ads:264`) inside SPARK.

**Repairs.**
- Both original wire contracts are unchanged.
- The wrapper re-evaluates `Well_Formed`. That re-evaluation is a costed native delta (A-COST §C5–§C6). By source reading it consists of bounded field checks independent of array lengths; it is **not** described as measured constant-time execution.
- D-36 stays OPEN.
- The cost-neutral `(Ok, Value)` variant remains an optional refinement, to be reviewed separately.

### 2.6 LD6. Coverage gaps get additive controls (retained)

**Decision.**
- Controls are added, never substituted.
- Every original ordered roster action, positive and refusal case, lifetime control and assertion is kept.

**Repairs.**
- PK-0 encodes only *defined* original behaviour (§9.6).
- It imposes no global no-write claim on exception paths and assumes no translation of foreign-pointer faults into Ada exceptions.
- Finite controls are characterization evidence. They are not proof, custody, coverage or native-cost closure.

---

## 3. Design rules applied to every unit

### 3.1 Classification and the maximal-run rule

1. **[T] in `Worldline.C_API`:**
   - null tests;
   - length and count bounds that describe foreign extents (`> Byte_Count'Last`, `< 0` on an extent length, `Count > Storage_Offset'Last / Stride`, `Length /= Rec'Size / Storage_Unit`, `Rows_Length /= Rows_Count * Stride`);
   - alignment, address wrap and address disjointness;
   - every raw read and write;
   - the declarative size and stride constants.

   Each original guard function is copied verbatim into a body-local transport package for its original unit (§3.6).
2. **[S] in the unit's On spec:**
   - every test of the value of a by-value scalar or of copied bytes: versions, operations, modes, kinds, presence flags, enumeration ranges, span/cursor/identity validity, count consistency between two copied records, and record equality such as `X.Agent /= Raw_Agent`;
   - every presence interpretation that gates a read;
   - all decoding, decision and result encoding;
   - (RC1) all diagnostic state and decisions.
3. **Maximal-run rule.** Where an original `or else` chain interleaves [T] and [S] conjuncts, the successor evaluates them in the original order. Each maximal run of consecutive value conjuncts becomes one SPARK predicate call at that position.
   - **M1** The relative order of all conjuncts, within and between runs, is the original order. Short-circuit evaluation is preserved, so a later conjunct (and any exception it could raise) is reached exactly when it was reached before.
   - **M2** Every transport operation, allocation, diagnostic mark and early return that the original performed between two decisions stays between them.
   - **M3** No value is validated before the original read stage that produced it, and no read is moved earlier than the decision that gated it.
   - **M4** Decoding that the original performed after validation may be evaluated inside the acceptor at the validation point, but only where the decode is pure and infallible once validity holds. Each such move is listed in the unit section and in A-COST.
4. **[P] plumbing.**
   - The boundary may compare a code, flag or verdict returned by SPARK or by a nested transport (`if not D.Ok`, `if Status /= 0`, `case RA.Verdict`).
   - It may convert a SPARK-returned scalar or a transport loop index to `I64`, solely as a diagnostic argument.
   - It computes no value condition (D-03).

### 3.2 Value-routine form

- **V1 Declaration.**
  - Each new routine is declared in the visible part of the unit's existing On spec.
  - It has `Global => null` (or, for the RC1 state machine, `Global => (In_Out => Diagnostic_State)`), and procedures carry `Always_Terminates`.
  - There is no `Pre` and no added functional `Post`.
- **V2 Completion.**
  - A definition that uses only spec-visible entities is an expression function in the visible part.
  - One that needs body-local helpers is completed in the body.
  - Body-local decoders keep their text and stay body-local; D-05 governs their proof (V8).
- **V3 Totality without narrowing.**
  - Where a routine's RTE-freedom depends on validity facts that the transport chain established, the routine re-evaluates **the identical SPARK predicate on the identical captured constant** (`R`, `X`, the request record read once by the transport). It returns a defined refusal value when that predicate fails.
  - SPARK functions with `Global => null` are deterministic, and the argument is the same constant the chain just accepted. The refusal branch is therefore dead on every transport path; the transport maps it to the original refusal code only for totality.
  - Each such re-evaluation is a costed native delta (A-COST) and is never a new ABI refusal.
  - **No routine re-checks array bounds, lengths or any relation the original did not test** (D-18).
  - Only §5.5 uses a weaker predicate implied by the transport chain, and that implication is stated there.
- **V4 Acceptance records.**
  - Per-element acceptance returns a discriminated record whose `True` variant carries the decoded payload.
  - **A1:** the transport tests the discriminant (`if not D.Ok then return <original code>; end if;` or `case D.Verdict`) before reading any payload component. The manifest binds this order (§8.4).
  - A discriminant-check exception is not a designed path.
- **V5 Out formals.** Every `out` formal is assigned on every path before return, including every refusal path (§5.3).
- **V6 Existing contracts.**
  - Pre-bearing relations (`W.Decide`, `W.Decode`, `Resource_Run_Ledger_Wire.Decide`) are wrapped as in v2.
  - Every existing `Pre`/`Post` is evaluated where it was evaluated before, and those evaluations are listed in A-COST.
- **V7 Naming.** New names are unique, unoverloaded and fully qualified at every transport call. This keeps the name-keyed coverage map and the ordered-token checks unambiguous (`proof_manifest.py:787-789`).
- **V8 Decoders (D-05).**
  - The body-local decoders that contain partial operations are listed in §17 (D-05).
  - The design depends on no contextual analysis that has not been demonstrated.
  - If the installed tool does not prove a decoder at every original caller, the decoder is restructured to be total by construction, as a separately reviewed delta (A-COST lists the cost class).
  - A helper-local `Pre` is used only if a separately reviewed proposal demonstrates a non-narrowing internal contract, every SPARK call-site proof, and its checked and native cost.
  - This design approves no helper `Pre`.
- **V9 Single source of each fact.** Where a value routine needs a decoded request field, it decodes it from the same captured constant with the same decoder text as the original. Decoding is not duplicated in the transport.

### 3.3 Staged reads

- A read that the original performed only after a value decision is performed only after the corresponding [S] result.
- Per-element rows are read one at a time, and row `I+1` is read only after row `I` was accepted.
- No bulk copy is introduced.
- Unconditional original reads stay unconditional: the v3 arena (`worldline-recovery_authorization_v3_c_api.adb:154-157`); the completion retained, history and required arrays (`evaluation_completion_c.adb:468-494`); the run-ledger arrays (`resource_run_ledger_c_api.adb:213-216`).

### 3.4 Writes and write construction

- There is no blanket output rule. Each export keeps its original write set, conditions and order.
- Accepted input/output aliasing is preserved by capturing every input before the first write. Existing overlap refusals are kept, and none is added.
- **Write construction is a native property and is not claimed equal.**
  - Where the original assigned a function result or aggregate directly through an access value (v2, v3, chain, run ledger, pending v1/v2, policy, ledger details/result), the successor completes a SPARK result first and copies it once.
  - Where the original already wrote a completed local (protocol, history, completion, finalization), the pattern is unchanged, but the local now comes from a SPARK result.
- §11.4 and A-COST §C19 tabulate every export. D-36 stays OPEN for all of them.

### 3.5 Exception and allocation scope

- Each export keeps its original handler and refusal code.
- Declarative size constants stay outside the handler.
- Every caller-count-sized allocation stays at its original position and order inside the handled region. That includes completion's unused arrays and finalization's `Captured` for Operations 0 and 1.
- Every SPARK call that could raise `Storage_Error` is inside the handler. This covers native Big_Integer `Normalize` (Bignum_Limit 200, per `H/native-cost-gap/REVIEW.md`) and the new temporaries listed in A-COST.
- **A caught native failure keeps its original refusal code and never closes the obligation that the original accepted computation succeeds.**

### 3.6 `Worldline.C_API` layout

**Spec.**
- 20 relocated export declarations. Each is the original normalized declaration with only the subprogram identifier changed (A-BIND §B3).
- Four package-level subtypes, with the same first-subtype resolutions as the originals:
  - `subtype U8 is Interfaces.Unsigned_8;`
  - `subtype U32 is Interfaces.Unsigned_32;`
  - `subtype I64 is Interfaces.Integer_64;`
  - `subtype Size is Interfaces.C.size_t;`
- `External_Name` occurrences in the spec: 31 observed today; 51 after the last move (JACKAL exact `31+20`).

**Body, in order.**
- (a) `Diagnostic_Transport` (RC1, §4.4). The body gains `with Ada.Text_IO;` and `with Ada.Exceptions;`.
- (b) One body-local transport package per original unit: `Resources_Transport`, `Recovery_Transport`, `Recovery_Authorization_Transport`, `Recovery_Authorization_V3_Transport`, `Recovery_Protocol_Transport`, `Lifecycle_Transport`, `Ledger_Transport`, `Policy_Transport`, `History_Transport`, `Run_Ledger_Transport`, `Chain_Transport`, `Completion_Transport`, `Finalization_Transport`, `Pending_Transport`, `Pending_V2_Transport`.
  - Each holds verbatim copies of its unit's guard functions, pointer instances and copy/write loops under their original names. There is no cross-unit sharing (D-08).
  - Each replicates the original unit's package renames and declares subtypes for the unit's own types, so that copied helper text stays textual.
  - Each export body contains exactly one `use <Unit>_Transport;` (A-BIND §B0, §B4).
  - `Completion_Transport.Context_Matches`, `.Metadata_Base` and `Finalization_Transport.Final_Context_Matches` are declared here, before `package body Authority_Glue` (`core/worldline-c_api.adb:671`).
- (c) The existing owner code, unchanged.
- (d) The export bodies.

**Authority_Glue retargeting** (unchanged from v2; A-BIND §B4.23). Arguments, order and gating are unchanged.

| Original call | Sites in `core/worldline-c_api.adb` | Retargeted to |
|---|---|---|
| `K.Raw_Decide` | `:784-785`, `:791-792` | `Completion_Raw_Decide` |
| `K.Context_Matches` | `:810-811`, `:813-814` | `Completion_Transport.Context_Matches` |
| `K.Metadata_Base` | `:852`, `:855` | `Completion_Transport.Metadata_Base` |
| `K.Metadata_Matches` | `:866-867`, `:869-870` | `Completion_Metadata_Matches` |

The existing Off value decisions in `Authority_Glue` (`:768-770`, `:783-819`) are pre-existing boundary surface (D-21).

### 3.7 What stays in each SPARK unit

Each unit keeps:
- all record types and their representation;
- every version/layout export;
- the body-local decoders;
- the new value routines;
- for `Evaluation_Completion_C`, the diagnostic state machine (§4).

Every unit stays `SPARK_Mode => On` with full body analysis.

`DECLARED_CORE_ADA_SOURCES`, `expected_units` (`proof_manifest.py:642-646`) and `Library_Interface` (`core/worldline_core.gpr:9-80`) are unchanged: no core unit is added or removed.

---

## 4. RC1: the diagnostic state machine stays in SPARK (LD4-R)

### 4.1 Original behaviour (`core/evaluation_completion_c.ads:12-22`, `core/evaluation_completion_c.adb:39-88`)

**State.** `Diagnostic_Active : Boolean := False with Atomic;` and `Diagnostic_Failed : Boolean := False with Atomic;` (adb:39-40). The control comment (ads:12-15) describes a serial, owned diagnostic call that "cannot supply or alter an authority input". The check-then-act in `Diagnostic_Control` is not atomic as a whole.

**Procedures.**
- `Diagnostic_Mark (Site)` (adb:42-51): if `Diagnostic_Active`, then `Put_Line (Standard_Error, "WORLDLINE_NATIVE_DIAGNOSTIC " & Site)` and `Flush (Standard_Error)`. Any exception sets `Diagnostic_Failed := True`.
- `Diagnostic_Value (Site, Value)` (adb:53-60): if active, then `Diagnostic_Mark (Site & "=" & I64'Image (Value))`. Any exception sets the latch.
- `Diagnostic_Exception (Site, Error)` (adb:62-71): if active, then `Diagnostic_Mark (Site & " exception=" & Ada.Exceptions.Exception_Information (Error))`. Any exception sets the latch.
- `Diagnostic_Control (Enable)`, export `wl_native_diagnostic_control_v1` (adb:73-88):

  | `Enable` | Behaviour |
  |---|---|
  | 1 | If active, return 1. Otherwise `Failed := False; Active := True; Mark ("trace.begin"); return 0`. |
  | 0 | `Mark ("trace.end"); Active := False; return (if Failed then 1 else 0)`. |
  | anything else | Return 2. |

**Installed-tool diagnostics on this code** (LEDGER, observed):

| Diagnostic | Location | Ledger ids |
|---|---|---|
| E0004 "volatile object in interfering context is not allowed in SPARK (SPARK RM 7.1.3(9))" | adb:44:10, :55:10, :65:10, :76:13, :84:21 | D0075, D0078, D0079, D0081, D0082; console D2582, D2585, D2586, D2588, D2589 |
| E0005 "function \"Diagnostic_Control\" with output global … is not allowed in SPARK" | ads:16:13 | D0044, D3173, D3174 |
| `"Standard_Error" is not allowed in SPARK (due to entity declared with SPARK_Mode Off)` | adb:46:13 and :47:29 | D2583, D2584 |
| Warning `no Global contract available for "Exception_Information" [assumed-global-null]` | adb:67:50 | D0080, D2587 |
| `choice parameter in handler is not allowed in SPARK` | completion adb:866:12, :983:12; finalization adb:254:12, :352:12, :506:12 | D0704, D0800, D0944, D1036, D1076 |

The installed library supports two of these causes: it declares `Standard_Error … with SPARK_Mode => Off` (`G/libexec/spark/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude/a-textio.ads:189` and `:199`), and `Exception_Information` has no Global contract (`a-except.ads:94`). The installed explain codes `G/share/spark/explain_codes/E0004.md` and `E0005.md` give the non-interfering-context and side-effect rules this design follows.

### 4.2 SPARK-owned declarations (added to `core/evaluation_completion_c.ads` in PK-6a)

*PROPOSAL ONLY: not compiled, not proved, not reviewed.*

```ada
package Evaluation_Completion_C with
  SPARK_Mode     => On,
  Abstract_State => (Diagnostic_State with External)
  --  External with no listed properties: Async_Readers, Async_Writers,
  --  Effective_Reads and Effective_Writes all True, the same as the
  --  defaults of the two unchanged Atomic constituents. No property is
  --  narrowed; narrowing one would be a new environmental assumption.
is
   ...                                              --  existing declarations unchanged
   type Diagnostic_Control_Kind is (Start_Trace, Stop_Trace, Invalid_Control);
   function Diagnostic_Control_Of (Enable : U32) return Diagnostic_Control_Kind is
     (if Enable = 1 then Start_Trace elsif Enable = 0 then Stop_Trace
      else Invalid_Control)                         --  adb:75, :81, :85
     with Global => null;
   function Diagnostic_Invalid_Code return U32 is (2)   --  adb:86
     with Global => null;
   procedure Diagnostic_Start (Code : out U32; Emit_Begin : out Boolean)
     with Global => (In_Out => Diagnostic_State), Always_Terminates;   --  adb:76-80
   procedure Diagnostic_Stop (Code : out U32)
     with Global => (In_Out => Diagnostic_State), Always_Terminates;   --  adb:83-84
   procedure Diagnostic_Observe (Active : out Boolean)
     with Global => (In_Out => Diagnostic_State), Always_Terminates;   --  adb:65
   procedure Diagnostic_Latch_Failure
     with Global => (In_Out => Diagnostic_State), Always_Terminates;   --  adb:50, :59, :70
   procedure Diagnostic_Begin_Line (Site : String; Write : out Boolean)
     with Global => (In_Out => Diagnostic_State), Always_Terminates;   --  adb:44-46
   function Diagnostic_Line (Site : String) return String
     with Global => null;                                              --  adb:46 text
   procedure Diagnostic_Begin_Value (Site : String; Value : I64; Compose : out Boolean)
     with Global => (In_Out => Diagnostic_State), Always_Terminates;   --  adb:55-56
   function Diagnostic_Value_Site (Site : String; Value : I64) return String
     with Global => null;                                              --  adb:56 text
   procedure Diagnostic_Begin_Exception
     (Site, Information : String; Compose : out Boolean)
     with Global => (In_Out => Diagnostic_State), Always_Terminates;   --  adb:66-67 catenation
   function Diagnostic_Exception_Site (Site, Information : String) return String
     with Global => null;                                              --  adb:67 text
```

During PK-6a the old `Diagnostic_Control` export and the procedures `Diagnostic_Mark`, `Diagnostic_Value` and `Diagnostic_Exception` (ads:16-22) coexist unchanged. PK-6b removes them from the SPARK unit, together with `with Ada.Exceptions;` (ads:1) and `with Ada.Text_IO;` (adb:2).

### 4.3 SPARK bodies

```ada
package body Evaluation_Completion_C with
  SPARK_Mode    => On,
  Refined_State => (Diagnostic_State => (Diagnostic_Active, Diagnostic_Failed))
is
   Diagnostic_Active : Boolean := False with Atomic;   --  adb:39, unchanged
   Diagnostic_Failed : Boolean := False with Atomic;   --  adb:40, unchanged
   Diagnostic_Prefix   : constant String := "WORLDLINE_NATIVE_DIAGNOSTIC ";  --  adb:46 literal
   Exception_Separator : constant String := " exception=";                   --  adb:67 literal

   --  Body-local; exactly when the original catenation could NOT raise
   --  Constraint_Error (RM 4.5.3: a non-null left operand gives the lower
   --  bound; a null left operand yields the right operand). Covered by the
   --  unit-wide all-proved rule; not enrolled by name.
   function Line_Fits (Site : String) return Boolean is
     (Site'Length <= Natural'Last - Diagnostic_Prefix'Length);
   function Value_Fits (Site, Image : String) return Boolean is
     (if Site'Length = 0 then Image'Length <= Positive'Last - 1
      else Site'Last <= Positive'Last - 1 - Image'Length);
   function Exception_Fits (Site, Information : String) return Boolean is
     (if Site'Length = 0
      then Information'Length <= Positive'Last - Exception_Separator'Length
      else Site'Last <= Positive'Last - Exception_Separator'Length - Information'Length);

   function Diagnostic_Line (Site : String) return String is
     (if Line_Fits (Site) then Diagnostic_Prefix & Site else "");      --  "" branch dead on transport paths
   function Diagnostic_Value_Site (Site : String; Value : I64) return String is
     (declare Image : constant String := I64'Image (Value);
      begin (if Value_Fits (Site, Image) then Site & "=" & Image else ""));
   function Diagnostic_Exception_Site (Site, Information : String) return String is
     (if Exception_Fits (Site, Information)
      then Site & Exception_Separator & Information else "");

   procedure Diagnostic_Observe (Active : out Boolean) is
   begin
      Active := Diagnostic_Active;                     --  one atomic read (non-interfering context)
   end Diagnostic_Observe;

   procedure Diagnostic_Latch_Failure is
   begin
      Diagnostic_Failed := True;                       --  adb:50, :59, :70
   end Diagnostic_Latch_Failure;

   procedure Diagnostic_Begin_Line (Site : String; Write : out Boolean) is
      Active : constant Boolean := Diagnostic_Active;  --  adb:44 read
   begin
      if Active and then not Line_Fits (Site) then
         Diagnostic_Failed := True;                    --  adb:46 catenation would raise; adb:50
         Write := False;
      else
         Write := Active;
      end if;
   end Diagnostic_Begin_Line;

   procedure Diagnostic_Begin_Value (Site : String; Value : I64; Compose : out Boolean) is
      Active : constant Boolean := Diagnostic_Active;  --  adb:55 read
   begin
      if Active and then not Value_Fits (Site, I64'Image (Value)) then
         Diagnostic_Failed := True;                    --  adb:56 catenation would raise; adb:59
         Compose := False;
      else
         Compose := Active;
      end if;
   end Diagnostic_Begin_Value;

   procedure Diagnostic_Begin_Exception
     (Site, Information : String; Compose : out Boolean) is
   begin
      if Exception_Fits (Site, Information) then
         Compose := True;
      else
         Diagnostic_Failed := True;                    --  adb:67 catenation would raise; adb:70
         Compose := False;
      end if;
   end Diagnostic_Begin_Exception;

   procedure Diagnostic_Start (Code : out U32; Emit_Begin : out Boolean) is
      Active : constant Boolean := Diagnostic_Active;  --  adb:76 read
   begin
      if Active then
         Code := 1;                                    --  adb:76 return 1, no write
         Emit_Begin := False;
      else
         Diagnostic_Failed := False;                   --  adb:77
         Diagnostic_Active := True;                    --  adb:78
         Code := 0;                                    --  adb:80
         Emit_Begin := True;                           --  adb:79 mark made by the transport
      end if;
   end Diagnostic_Start;

   procedure Diagnostic_Stop (Code : out U32) is
   begin
      Diagnostic_Active := False;                      --  adb:83
      declare
         Failed : constant Boolean := Diagnostic_Failed;   --  adb:84 read
      begin
         Code := (if Failed then 1 else 0);            --  adb:84
      end;
   end Diagnostic_Stop;
   ...
```

### 4.4 The only transport: `Diagnostic_Transport` in the `Worldline.C_API` body

```ada
package Diagnostic_Transport is                        --  body-local in core/worldline-c_api.adb
   procedure Mark (Site : String);
   procedure Value (Site : String; Number : Interfaces.Integer_64);
   procedure Exception_Text (Site : String; Error : Ada.Exceptions.Exception_Occurrence);
end Diagnostic_Transport;

package body Diagnostic_Transport is
   procedure Mark (Site : String) is
      Write : Boolean;
   begin
      Evaluation_Completion_C.Diagnostic_Begin_Line (Site, Write);             --  [S]
      if Write then                                                           --  [P]
         Ada.Text_IO.Put_Line (Ada.Text_IO.Standard_Error,                    --  [T] T1
                               Evaluation_Completion_C.Diagnostic_Line (Site)); --  [S] text
         Ada.Text_IO.Flush (Ada.Text_IO.Standard_Error);                      --  [T] T2
      end if;
   exception
      when others => Evaluation_Completion_C.Diagnostic_Latch_Failure;         --  [T] T3 -> [S]
   end Mark;

   procedure Value (Site : String; Number : Interfaces.Integer_64) is
      Compose : Boolean;
   begin
      Evaluation_Completion_C.Diagnostic_Begin_Value (Site, Number, Compose);  --  [S]
      if Compose then                                                         --  [P]
         Mark (Evaluation_Completion_C.Diagnostic_Value_Site (Site, Number));  --  [S] text, [T] Mark
      end if;
   exception
      when others => Evaluation_Completion_C.Diagnostic_Latch_Failure;         --  [T] T3 -> [S]
   end Value;

   procedure Exception_Text (Site : String; Error : Ada.Exceptions.Exception_Occurrence) is
      Active : Boolean;
   begin
      Evaluation_Completion_C.Diagnostic_Observe (Active);                     --  [S] read
      if Active then                                                          --  [P]
         declare
            Information : constant String :=
              Ada.Exceptions.Exception_Information (Error);                   --  [T] T4
            Compose : Boolean;
         begin
            Evaluation_Completion_C.Diagnostic_Begin_Exception (Site, Information, Compose);  --  [S]
            if Compose then                                                   --  [P]
               Mark (Evaluation_Completion_C.Diagnostic_Exception_Site (Site, Information));
            end if;
         end;
      end if;
   exception
      when others => Evaluation_Completion_C.Diagnostic_Latch_Failure;         --  [T] T3 -> [S]
   end Exception_Text;
end Diagnostic_Transport;

function Native_Diagnostic_Control (Enable : U32) return U32 is                --  export, same profile
   Code       : U32;
   Emit_Begin : Boolean;
begin
   case Evaluation_Completion_C.Diagnostic_Control_Of (Enable) is              --  [S]
      when Evaluation_Completion_C.Start_Trace =>
         Evaluation_Completion_C.Diagnostic_Start (Code, Emit_Begin);          --  [S]
         if Emit_Begin then Diagnostic_Transport.Mark ("trace.begin"); end if; --  [P], [T]
         return Code;
      when Evaluation_Completion_C.Stop_Trace =>
         Diagnostic_Transport.Mark ("trace.end");                              --  [T]
         Evaluation_Completion_C.Diagnostic_Stop (Code);                       --  [S]
         return Code;
      when Evaluation_Completion_C.Invalid_Control =>
         return Evaluation_Completion_C.Diagnostic_Invalid_Code;               --  [S]
   end case;
end Native_Diagnostic_Control;
```

`Native_Diagnostic_Control` has no handler, exactly as the original `Diagnostic_Control` (adb:73-88). Its only exception sources are the `Mark` calls, which catch their own exceptions as the original `Diagnostic_Mark` did.

### 4.5 Why each transported item is irreducible

| Item | What it is | Why it cannot be SPARK under the fixed rules |
|---|---|---|
| T1 | `Ada.Text_IO.Put_Line (Ada.Text_IO.Standard_Error, …)` | `Standard_Error` is declared `SPARK_Mode => Off` in the installed library (a-textio.ads:189, :199; LEDGER D2583/D2584). Writing the process's stderr is an external effect with no SPARK-visible channel in the installed runtime. A SPARK-callable wrapper would be an Off body or an imported contract, both forbidden (H/HANDOFF.md:29, :161; v1 alternatives 4 and 6). |
| T2 | `Ada.Text_IO.Flush (Ada.Text_IO.Standard_Error)` | Same as T1. |
| T3 | The `when others` handler around T1/T2 and around the composition calls, whose only action is the SPARK call `Diagnostic_Latch_Failure` | It guards T1/T2 (Off entities) and transport-side `Storage_Error`. The decision it implements, latching the failure, is the SPARK procedure it calls. |
| T4 | `Ada.Exceptions.Exception_Information (Error)` | The occurrence `Error` exists only in transport handlers with choice parameters, which the installed tool rejects in SPARK (D0704, D0800, D0944, D1036, D1076). The installed function has no Global contract (a-except.ads:94; D0080/D2587), so calling it from SPARK would add an assumption. |
| T5 | The call sequence of §4.4 | SPARK cannot call T1–T4, so the interleaving of SPARK steps with them must be driven from the boundary. Every branch in T5 routes on a SPARK-returned Boolean or enumeration ([P]). The transport computes no value condition and holds no state. |

Nothing else of the original diagnostics is transported. The following are all SPARK:
- the state (`Diagnostic_Active`, `Diagnostic_Failed`);
- the check-then-act and the latch;
- the three control codes;
- the line text and the value formatting (`I64'Image`);
- the overflow behaviour.

### 4.6 Atomic access and effect sequences are unchanged

`R(x)` is one atomic read, `W(x:=v)` one atomic write, `L` one stderr line plus flush.

| Original operation | Original sequence | Successor sequence |
|---|---|---|
| Mark (Site) | R(Active); if True: compose; L; on exception W(Failed:=True) | Begin_Line: R(Active); if True and overlong: W(Failed:=True) (the original raised in the catenation and the handler latched); transport: if Write: compose; L; on exception Latch W(Failed:=True) |
| Value (Site, V) | R(Active); if True: compose value site; Mark (R(Active); L); on exception W(Failed:=True) | Begin_Value: R(Active); if True and overlong: W(Failed:=True); transport: if Compose: compose; Mark (R(Active); L); on exception Latch |
| Exception (Site, E) | R(Active); if True: Exception_Information; compose; Mark (R(Active); L); on exception W(Failed:=True) | Observe: R(Active); transport: if True: Exception_Information; Begin_Exception (overlong: W(Failed:=True)); if Compose: compose; Mark (R(Active); L); on exception Latch |
| Control (1) | R(Active); if True return 1; else W(Failed:=False); W(Active:=True); Mark; return 0 | Control_Of; Start: R(Active); if True (1, no Mark) else W(Failed:=False); W(Active:=True) (0, Mark); transport Mark if Emit_Begin; return Code |
| Control (0) | Mark; W(Active:=False); R(Failed); return code | transport Mark; Stop: W(Active:=False); R(Failed); return Code |
| Control (other) | return 2 | Control_Of → Invalid_Control; return Diagnostic_Invalid_Code (2) |

- Every atomic access occurs in the same order, once, at the same point relative to every stderr line.
- No synchronization is added or removed. The non-atomic check-then-act is preserved, as the original documents it (ads:12-15).
- The only difference in mechanism concerns an overlong catenation:
  - the original detected it by `Constraint_Error`;
  - the successor detects it by an exact SPARK length test, with the same effect (latch, no line).
- For the actual call sites (literal sites, `I64` values, exception information) this case is unreachable, but it is kept exact for every input.

### 4.7 How the diagnostics remain analysable, and what is still OPEN

**Flow.**
- All state lives in one external abstract state with the default (all True) volatility properties of its `Atomic` constituents.
- Every read is in a non-interfering context (an object-declaration initializer or an assignment right-hand side). That is the documented fix for E0004.
- No function reads or writes the state. This removes the E0005 situation: the exported C function is now in the boundary and calls SPARK procedures.
- Expected flow obligations: Global In_Out for each procedure; full initialization of out formals.

**Proof.**
- RTE: the three catenations are proved inside the `Fits` guards, and the `Fits` arithmetic stays within `Integer`.
- The installed tool models `I64'Image` with "nothing … known about the evaluation of the attribute reference apart from a bound on its length" (message text in `G/libexec/spark/bin/gnat2why`).
- **OPEN:**
  - whether that modelling discharges the value-site catenation inside `Value_Fits`;
  - whether the `'Image` reference itself draws a strict warning or info;
  - installed-tool legality of an `External` abstract state refined to `Atomic` library-level objects in this unit.
- If any of these fails, the obligation stays OPEN and a reviewed alternative is required. There is no waiver.

**Termination.** `Always_Terminates` on each procedure; there are no loops.

**Functional correspondence.**
- No functional `Post` is added (LD2).
- Correspondence rests on the source equivalence of §4.6. §8.5 enforces it textually, and C-06 behaviourally (exact line sequences, codes 0/1/2, stop-without-start latch).
- A reviewer may require small Posts, for example `Code <= 1` on `Diagnostic_Start`. Each would add one checked comparison under `-gnata` (A-COST §C18).

### 4.8 Call-site migration

Every diagnostic call in the moved transports keeps its position and literal site. Only the callee changes:

| Original callee | Successor callee |
|---|---|
| `K.Diagnostic_Mark` | `Diagnostic_Transport.Mark` |
| `K.Diagnostic_Value` | `Diagnostic_Transport.Value` |
| `K.Diagnostic_Exception` | `Diagnostic_Transport.Exception_Text` |

Observed site sequences in S5:

| Function | Sites | Mark / Value / Exception |
|---|---|---|
| `Context_Matches` | 13 | 6 / 6 / 1 |
| `Metadata_Matches` | 9 | 6 / 2 / 1 |
| finalization `Decide` | 9 | 4 / 4 / 1 |
| `Final_Context_Matches` | 7 | 4 / 2 / 1 |
| `Decide_Mixed` | 16 | 11 / 4 / 1 |
| `Diagnostic_Control` | 2 | 2 / 0 / 0 |

§8.5 D3 checks the exact ordered site sequences; A-BIND §B6 lists them with their S5 lines.

### 4.9 Native cost

- **Inactive path (the default).** Every Mark, Value and Exception site performs one SPARK call that does the single original atomic read, instead of an inline read. Cross-unit calls are not inlined under the core switches (`core/worldline_core_sources.gpr:11-12` has no `-gnatn`).
- **Active path.** There are extra `Fits` evaluations and one extra `I64'Image` per value site. Text is composed through SPARK functions returning `String` on the secondary stack; the original catenations also used it.

Detail: A-COST §C18.

### 4.10 OPEN

- Installed-tool legality and proof of §4.2–§4.3.
- Strict warnings of every kind in the changed unit.
- C-06 on the successor.
- The boundary surface of T1–T5 under OB-048 (§14).

---

## 5. RC2: initialized and total value interfaces

### 5.1 Finalization `Captured` on Operations 0 and 1: separate no-row and with-row value paths

**Original** (`core/evaluation_finalization_c.adb:159-201`):
- `Captured : F.Start_Rows (1 .. P.Count (X.Row_Count));` is declared for every operation (adb:162).
- Rows are read and `Captured` is assigned only for Operations 2 and 3 (adb:188-201). Operations 0/1 never read it.

**v2 defect.** `Decide_Value (X, A, Required, Captured)` was called for every operation. On Operations 0/1 an uninitialized array of `Start_Row` (enumeration and variant components, `evaluation_finalization.ads:60-72`) was therefore passed as an `in` actual. Under the core `-gnatVa` switch, the copy-in could even fail validity.

**v3 design.**

```ada
--  Evaluation_Finalization_C (spec): replaces v2's single Decide_Value
type Decide_Acceptance (Ok : Boolean := False) is record
   case Ok is
      when True  => Value : Result;
      when False => null;
   end case;
end record;
Initial_Result : constant Result :=
  (Reason => 1, State => 0, Outcome => 0, Promotion => 0, Finalization_State => 0,
   Finalization_Outcome => 0, Identity => (others => 0));          --  adb:164-166
function Decide_No_Rows_Value
  (X : Request; Arena : Evaluation_Pending.Bytes;
   Required : Evaluation_Raw_Roster.Check_Array) return Decide_Acceptance
  with Global => null;
--  Body: if not (Request_Header_Valid (X) and then Request_Fields_Valid (X))
--          or else X.Operation >= 2 then (Ok => False)          -- dead on every transport path (V3)
--        else S := Convert (X.Start) (adb:163); Response := Initial_Result (adb:164-166);
--             Operation 0: adb:183-184 verbatim; Operation 1: adb:185-187 verbatim;
--             (Ok => True, Value => Response)
function Decide_Rows_Value
  (X : Request; Arena : Evaluation_Pending.Bytes;
   Required : Evaluation_Raw_Roster.Check_Array;
   Captured : Evaluation_Finalization.Start_Rows) return Decide_Acceptance
  with Global => null;
--  Body: if not (header and fields) or else X.Operation <= 1 then (Ok => False)   -- dead on transport paths
--        else S, Response as above; Operation 2: adb:202-216 verbatim;
--             Operation 3: adb:217-244 verbatim (F.Seal's Post, evaluation_finalization.ads:387-407,
--             supplies Finalization.Present for adb:236-237: no guard, no Pre, D-31);
--             (Ok => True, Value => Response)
```

**Transport (`Finalization_Decide`, after the plan loop; `O : Evaluation_Finalization_C.Decide_Acceptance;` declared with the other locals):**

```ada
if Evaluation_Finalization_C.Needs_Rows (X) then                      --  [S] X.Operation >= 2
   for K in Captured'Range loop                                         --  adb:189
      declare
         Q  : constant Evaluation_Finalization_C.Row :=
                Finalization_Transport.Rows.To_Pointer
                  (X.Rows + Storage_Offset (I64 (K - 1) * Row_Size)).all;  --  [T] adb:191-192
         RA : constant Evaluation_Finalization_C.Row_Acceptance :=
                Evaluation_Finalization_C.Accept_Row (Q);              --  [S] adb:194
      begin
         if not RA.Ok then                                              --  [P] A1
            Diagnostic_Transport.Value ("finalization.decide.row-rejected", I64 (K));
            return 255;                                                 --  adb:195-197
         end if;
         Captured (K) := RA.Item;                                       --  adb:199
      end;
   end loop;
   O := Evaluation_Finalization_C.Decide_Rows_Value (X, A, Required, Captured);
else
   O := Evaluation_Finalization_C.Decide_No_Rows_Value (X, A, Required);
end if;
if not O.Ok then return 255; end if;                                    --  dead mapping (V3)
```

**Why this is an initialized interface.**
- `Captured` is an actual only of `Decide_Rows_Value`, which is reached only after the loop over `Captured'Range`.
- Each iteration of that loop either returns before assigning or assigns a complete `Start_Row` value produced by a SPARK function. So every element is assigned before the call.
- On Operations 0 and 1, `Captured` is still allocated at adb:162's position, with the same size and the same allocation-failure behaviour. It is never read, copied or passed.
- No `Relaxed_Initialization`, assumption, change to `Row_Count`, cap or new refusal is introduced.
- The selector `Needs_Rows (X)` is exactly the original `X.Operation >= 2` branch (adb:183-188), and the `Ok => False` branches are dead on transport paths by V3.

**Controls.**
- C-05: Operations 0/1 with `Rows` on a PROT_NONE page and a nonzero `Row_Count` (never read).
- The existing positive Operation 0/1 cases (`tests/test_finalization_kernel.py`, roster [43]) are unchanged.
- C-16 (new): `Row_Count` large but allocatable; the allocation is kept and the outcome is identical to the original.

### 5.2 Completion context acceptors: total variant-record functions

**Original** (`core/evaluation_completion_c.adb:795-831`): the field loop and the row loop assign locals piecewise and return 255 early. After an early return, the partially assigned locals are never used.

**v2 defect.** The two `out`-parameter procedures left outputs undefined on some paths:
- `Expected`/`Observed` and `Row`/`Joined` were partially undefined on early exit;
- `Rejected`/`Rejected_Field` were undefined on success.

**v3 design.** Both acceptors become functions whose result is fully defined for its variant. The variant itself records which outputs exist.

```ada
type Context_Fields_Acceptance (Ok : Boolean := False) is record
   case Ok is
      when True  => Expected, Observed : Worldline.Evaluation_Authority.Context_Fields;
      when False => Rejected_Position : I64;      --  Context_Field'Pos of the first rejected field
   end case;
end record;
function Accept_Context_Fields (X : Context_Input) return Context_Fields_Acceptance
  with Global => null;
--  Body (statement body in the package body):
--     Expected, Observed : CA.Context_Fields := (others => (Present => False));
--       --  the same values that the original declaration at adb:789 default-initializes
--     for K in CA.Context_Field loop                                          --  adb:795
--        if not Valid (X.Expected (K)) or else not Valid (X.Observed (K)) then --  adb:796
--           return (Ok => False,
--                   Rejected_Position => I64 (CA.Context_Field'Pos (K)));     --  adb:798-800
--        end if;
--        Expected (K) := Convert_Optional (X.Expected (K));                   --  adb:802
--        Observed (K) := Convert_Optional (X.Observed (K));                   --  adb:803
--     end loop;
--     return (Ok => True, Expected => Expected, Observed => Observed);

type Context_Row_Verdict is (Row_Accepted, Row_Rejected, Row_Field_Rejected);
type Context_Row_Acceptance (Verdict : Context_Row_Verdict := Row_Rejected) is record
   case Verdict is
      when Row_Accepted       => Row    : Evaluation_Completion.Result_Record;
                                 Joined : Worldline.Evaluation_Authority.Context_Row;
      when Row_Rejected       => null;
      when Row_Field_Rejected => Rejected_Field_Position : I64;   --  Row_Field'Pos
   end case;
end record;
function Accept_Context_Row (Original : Check_Row; Owned : Context_Row)
  return Context_Row_Acceptance with Global => null;
--  Body:
--     if not Valid (Original) or else not Valid (Owned.Item) then           --  adb:812
--        return (Verdict => Row_Rejected);                                  --  adb:813-814
--     end if;
--     declare
--        Row    : constant T.Result_Record := Convert (Original);           --  adb:816
--        Joined : CA.Context_Row :=
--          (Item            => Convert (Owned.Item),                         --  adb:817
--           Declared        => T.Captured_Bytes (Convert (Owned.Item.Declared)),  --  adb:818
--           Actual_Declared => T.Captured_Bytes (Convert (Original.Declared)),    --  adb:819
--           Expected | Observed => (others => (Present => False)));   --  values of the adb:791 default init
--     begin
--        for K in CA.Row_Field loop                                          --  adb:820
--           if not Valid (Owned.Expected (K)) or else not Valid (Owned.Observed (K)) then  --  adb:821
--              return (Verdict => Row_Field_Rejected,
--                      Rejected_Field_Position => I64 (CA.Row_Field'Pos (K)));  --  adb:822-825
--           end if;
--           Joined.Expected (K) := Convert_Optional (Owned.Expected (K));    --  adb:827
--           Joined.Observed (K) := Convert_Optional (Owned.Observed (K));    --  adb:828
--        end loop;
--        return (Verdict => Row_Accepted, Row => Row, Joined => Joined);
--     end;
```

- Every validity test and every decode keeps its original order (adb:812-828). The read gates, the diagnostic order (`row-rejected=I`, or `row-field-row=I` then `row-field-rejected=K`) and the stop-at-first-failure behaviour are therefore unchanged.
- Each conversion is guarded by the test immediately before it in the same routine, so the acceptors themselves need no loop invariant or contextual analysis. The decoder bodies remain under D-05.
- `Convert_Optional` (adb:746-748) and `Optional` (adb:917-919) become body-local functions of the SPARK unit, with unchanged text.

**Transport use (A1).**
- Fields: `if not FA.Ok then Diagnostic_Transport.Value ("completion.context.field-rejected", FA.Rejected_Position); return 255; end if;`
- Rows: `case RA.Verdict is when Row_Rejected => …; when Row_Field_Rejected => …; when Row_Accepted => Rows (I) := RA.Row; Joined (I) := RA.Joined; end case;`

### 5.3 Every out formal and every result defined on every path

- **`Evaluation_Completion_C.Decide_Value` and `Raw_Decide_Value`** (procedures with `Response : out Result; Status : out Interfaces.C.int`).
  - On the dead re-check path: `Response := Initial_Response; Status := 255; return;`. `Initial_Response` is the constant equal to the aggregate at adb:436-439 / :577-580.
  - On every other path: first `Response := Initial_Response` (as the original declaration did), then the original statements, then `Status := 0`.
  - On the raw post-decision refusal (adb:657-671), where the original returned 255 without writing: `Status := 255`.
- **Acceptance functions.** Each returns a record whose active variant is fully defined by an aggregate.
- **`Diagnostic_Start`, `Diagnostic_Stop`, `Diagnostic_Observe` and the three `Begin_*` procedures.** Every out formal is assigned on every path (§4.3).

### 5.4 Exact non-narrowing array and index invariants for completion decisions (D-18)

**Arrays the transport allocates and SPARK receives** (`core/evaluation_completion_c.adb:423-429` for Decide and :564-570 for Raw_Decide):

| Array | Transport declaration (verbatim) | Invariant established by the declaration | Relation the original never tested |
|---|---|---|---|
| `J` | `J : V.Journal (1 .. P.Count (R.Journal_Count));` | `J'First = 1`, `J'Length = R.Journal_Count` (≥ 0 by `Array_Valid`) | none with `History` |
| `Measures` | `Measures : Roster.Measured_Array (1 .. P.Count (R.Captured_Count));` (raw: `Raw_Roster.Measured_Array`) | `'First = 1`, `'Length = R.Captured_Count` | — |
| `Captured` | `Captured : T.Result_Array (1 .. P.Count (R.Captured_Count));` | `Captured'Range = Measures'Range` | — |
| `Retained_Results` | `Retained_Results : T.Result_Array (1 .. P.Count (R.Retained_Count));` | `'First = 1`, `'Length = R.Retained_Count` | — |
| `History` | `History : H.History (1 .. H.Byte_Count (R.History_Count));` | `'First = 1`, `'Length = R.History_Count` | **`J'Length = History'Length` is not required**: unequal lengths are a legal input |
| `Required` | `Required : Roster.Check_Array (1 .. P.Count (R.Required_Count));` | `'First = 1`, `'Length = R.Required_Count` | — |

**Non-narrowing.**
- No routine re-checks any of these facts, and no routine refuses on them.
- Mismatched journal/history lengths keep their original typed outcome. On Operation 1, `T.Apply`'s Post makes `Reason = History_Invalid`, because `History_Reference` requires equal lengths (`evaluation_completion.ads:325-331`). The transport then writes `Response` and returns 0, exactly as the original does.

**The index.** The original summary access `History (H.Byte_Index (Selected))` (adb:519, :684) is replaced by `History (H.Byte_Index (T.History_Index (J, History, Selected)))`. This uses `Evaluation_Completion.History_Index` (`evaluation_completion.ads:332-338`), which is already in REQUIRED_PROVED.

- **Proof route (no bounds facts needed).**
  1. On Operation 1, with `Reason` in Retain_Terminal or Already_Retained, `T.Apply`'s Post (`evaluation_completion.ads:414-433`) gives `Reason = Update_Reference (…, History'Old)`.
  2. By `History_Update_Reference` (ads:351-362), that reason requires `History_Index (J, History'Old, Find_Run (A, J, Capture.Binding.Run)) /= 0`.
  3. `History_Index`'s Post puts that value in `History'Range`; the bounds of an `in out` array are unchanged.
  4. `Selected = T.Find_Run (A, J, T.Run_Identity (Convert (R.Captured.Bound.Run)))` equals `Find_Run (A, J, Capture.Binding.Run)` by unfolding the body-local expression functions `Convert (Capture)` and `Convert (Binding)`.

  Both reasons are covered.
- **Equivalence to the original.** On every transport path `J'First = History'First = 1`, and Apply's Post gives `J'Length = History'Length` on those reasons. So `History_Index (J, History, Selected) = History'First + (Selected - J'First) = Selected`, and the same element is read.
- **Selected.** `Response.Selected := I64 (Selected)` needs no new fact (`P.Count` is `0 .. Long_Long_Integer'Last`, `resource_quantities.ads:7`).
- **Cost.** One `History_Index` evaluation and, under `-gnata`, its existing Post (A-COST §C15).

The invariants are bound by the exact transport declaration tokens (A-BIND §B4.14–§B4.15). C-15 exercises them: length-mismatched history/journal with its typed outcome, and exact Retain_Terminal and Already_Retained summaries.

### 5.5 D-19: no new dead branch in the raw value routine (candidate, OPEN)

- The raw entry's transport chain keeps the original gate `R.Operation /= 2 → 255` inside `[S] Raw_Header_Valid (R)`, at adb:545's position.
- `Raw_Decide_Value`'s totality re-check (V3) evaluates `Decide_Header_Valid (R) and then Raw_Fields_Valid (R)`.
- `Raw_Header_Valid` implies `Decide_Header_Valid` (Version = 1, Operation ≤ 2, Policy and Retained_Present bounds). So the re-check is true on every transport path, while Operation stays open in SPARK.
- The original `T.Apply` branch (adb:649-651) and summary branch (adb:682-685) are kept verbatim. As before, they are reachable in the SPARK routine's own domain and unreachable natively.
- Nothing is deleted.

**Evidence still required.**
- The strict report shows no dead-code or unreachable-branch warning for `Raw_Decide_Value`.
- The History access in that branch is proved by the §5.4 route.
- C-04 keeps the raw `Operation /= 2 → 255` gate, and C-01/C-04 keep the post-decision malformed-span 255.

If the reviewer rules that the split itself relocates the original warning, D-19 stays OPEN; no other route is proposed.

### 5.6 D-28: fixed valid initialization before nested calls

These locals are initialized with the complete fixed aggregates (finalization adb:264, :373-374):
- `Ordinary : aliased Evaluation_Completion_C.Result := Evaluation_Completion_C.Initial_Response;`
- `Finalized : aliased Evaluation_Finalization_C.Result := Evaluation_Finalization_C.Initial_Result;`
- `Native : aliased … := Initial_Result;`

The aggregates preserve every existing field and default. The short-circuit status and readiness decisions and all success fields are unchanged. The added writes and copies are native deltas (A-COST §C16). They do not touch `Captured` (§5.1).

---

## 6. Relocation map (all 60 inventory symbols) with the moving stage

Counts:
- 60 exports observed across the 15 specs (JACKAL exact `10+4+5+5+3+3+4+3+3+2+3+4+5+4+2` = 60);
- 20 move (JACKAL exact `2+3+4+1+2+6+2` = 20, by stage);
- 40 stay (JACKAL exact `60-20`). Staying exports keep their declarations, homes and pins.

| Unit | Staying exports | Moving export → `Worldline.C_API` name | Stage | C header | ctypes binding |
|---|---|---|---|---|---|
| U1 resources | `wl_resources_abi_version` | `wl_resources_can_reserve` → `Resources_Can_Reserve` | PK-1 | `core/worldline_core.h:282` | `runtime/worldline/resource_kernel.py:29,36` |
| U2 recovery | `wl_recovery_abi_version` | `wl_recovery_select` → `Recovery_Select` | PK-1 | `core/worldline_core.h:65` | `runtime/worldline/recovery_kernel.py:21,27-30` |
| U3 v2 | `…version_v2`, `…layout_v2` | `wl_recovery_authorization_decide_v2` → `Recovery_Authorization_Decide_V2` | PK-2 | none | `runtime/worldline/recovery_authority_kernel.py:102,116` |
| U4 v3 | `…version_v3`, `…layout_v3` | `wl_recovery_authorization_decide_v3` → `Recovery_Authorization_Decide_V3` | PK-2 | `core/worldline_recovery_authorization_v3.h:59` | `runtime/worldline/recovery_authority_kernel_v3.py:110,124` |
| U5 protocol | `…version_v1`, `…layout_v1` | `wl_recovery_protocol_decide_v1` → `Recovery_Protocol_Decide_V1` | PK-2 | `core/worldline_recovery_protocol.h:9` | `runtime/worldline/recovery_protocol_kernel.py:16,28` |
| U6 lifecycle | `…abi_version`, `…row_size`, `…row_offset` | `wl_reservation_lifecycle_plan` → `Reservation_Lifecycle_Plan` | PK-3 | `core/worldline_core.h:388` | `runtime/worldline/reservation_lifecycle.py:33` |
| U7 ledger | `…abi_version`, `…layout_size`, `…layout_offset` | `wl_resource_ledger_compute` → `Resource_Ledger_Compute`; `wl_resource_ledger_headroom` → `Resource_Ledger_Headroom` | PK-3 | `core/worldline_core.h:351`, `:361` | `runtime/worldline/resource_ledger.py:53`, `:195,198-202` |
| U8 policy | `…abi_version`, `…layout_size`, `…layout_offset` | `wl_resource_policy_admit` → `Resource_Policy_Admit` | PK-3 | `core/worldline_core.h:324` | `runtime/worldline/resource_policy.py:84` |
| U9 history | `…abi_version`, `…layout_size`, `…layout_offset` | `wl_evaluation_history_select` → `Evaluation_History_Select` | PK-4 | `core/worldline_core.h:410` | `runtime/worldline/evaluation_history.py:113` |
| U12 run ledger | `…version_v1`, `…layout_v1` | `wl_resource_run_ledger_check_v1` → `Run_Ledger_Check` | PK-5 | `core/resource_run_ledger_v1.h:98` | `runtime/worldline/resource_run_ledger.py:216,225` |
| U13 chain | `…version_v1`, `…layout_v1` | `wl_chain_authority_replay_v1` → `Chain_Replay` | PK-5 | `core/worldline_chain_authority_v1.h:20` | `runtime/worldline/chain_authority.py:62,75` |
| U14 completion | `wl_completion_abi_version_v1`, `…layout_size_v1`, `…layout_alignment_v1`, `…layout_offset_v1`, `…context_layout_v1`, `…metadata_layout_v1` | `wl_completion_decide_v1` → `Completion_Decide`; `wl_completion_raw_decide_v1` → `Completion_Raw_Decide`; `wl_completion_metadata_matches_v1` → `Completion_Metadata_Matches`; `wl_native_diagnostic_control_v1` → `Native_Diagnostic_Control` | PK-6b | `core/evaluation_completion.h:130`, `:135`, `:197`; none for the diagnostic export | `completion_kernel.py:122`; `raw_completion_kernel.py:30-32`; `evaluation_context.py:128,131`; `tests/revalidation_diagnostic.py:138-141` |
| U15 finalization | `wl_finalization_version_v1`, `wl_finalization_layout_v1` | `wl_finalization_decide_v1` → `Finalization_Decide`; `wl_collapse_decide_finalization_v1` → `Finalization_Decide_Mixed` | PK-6b | `core/evaluation_finalization.h:61`, `:67` | `finalization_kernel.py:89,102`; `:308-313` |
| U10 pending v1 | `wl_pending_abi_version_v1`, `…layout_size_v1`, `…layout_alignment_v1`, `…layout_offset_v1` | `wl_pending_decide_v1` → `Pending_Decide_V1` | PK-7 | `core/evaluation_pending.h:53` | `runtime/worldline/pending_kernel.py:92` |
| U11 pending v2 | `wl_pending_abi_version_v2`, `…layout_size_v2`, `…layout_alignment_v2`, `…layout_offset_v2` | `wl_pending_decide_v2` → `Pending_Decide_V2` | PK-7 | `core/evaluation_pending_v2.h:37` | `runtime/worldline/pending_kernel_v2.py:99` |

**Non-exported raw code that moves.**
- Every unit's guard, pointer-instance and copy/write helpers (the v2 §4 table, unchanged).
- In PK-6b: `Context_Matches` (adb:733-869), `Metadata_Base` (adb:893-907) and `Final_Context_Matches` (finalization adb:259-355).

**Existing bindings.**
- Five of the 20 movers have an `export_problems` binding today: finalization decide and mixed (`proof_manifest.py:488-499`), `decide_v3` (:500-504), protocol `decide_v1` (:929-937) and chain `replay_v1` (:943-950).
- The other 15 are protected only by pins. §8 binds them.

---

## 7. Per-unit designs (v3)

- Every Ada block below is a **PROPOSAL ONLY: not compiled, not proved, not reviewed.**
- Original lines are in S5 (= S4 for these files).
- A-BIND §B4 gives each export's ordered tokens, and A-COST gives each call site's cost row.
- Content unchanged from v2 is restated so that this document stands alone.

### U1. `worldline-resources_c_api` (PK-1)

- **Modes:** spec On (ads:7), body On (adb:6).
- **F10K (observed, MAP):** 1 error (adb:30:28, allocating-function placement), 1 address-to-access warning, 0 representation warnings.
- **C profile** (identical to ads:17-24 except the identifier):
```ada
function Resources_Can_Reserve
  (Available_Negative : Interfaces.Unsigned_8;
   Available : System.Address; Available_Length : Interfaces.C.size_t;
   Withheld : System.Address; Withheld_Length : Interfaces.C.size_t;
   Floor : System.Address; Floor_Length : Interfaces.C.size_t;
   Requested : System.Address; Requested_Length : Interfaces.C.size_t)
   return Interfaces.Unsigned_8
  with Export, Convention => C, External_Name => "wl_resources_can_reserve";
```
- **Staged order** (original adb:45-62):
  1. [S] `Negative_Flag_Valid (Available_Negative)` (adb:45, negated) → 255.
  2. [T] four `Resources_Transport.Valid` extent tests, in order (adb:46-49) → 255.
  3. [T] four `Resources_Transport.Decode` copies, as the actuals of step 4. Their mutual order is unspecified, exactly as at adb:53-58.
  4. [S] `Can_Reserve_Value`.
  5. Return the SPARK result.
- **Writes:** none.
- **Overlap:** there are no outputs.
- **Handler:** `when others => 255` (adb:63-64) covers all steps, including each `Decode` allocation.
- **Value routines** (the spec gains `with Worldline.Resource_Wire;` and `use type Interfaces.Unsigned_8;`):
```ada
function Negative_Flag_Valid (Available_Negative : Interfaces.Unsigned_8) return Boolean is
  (Available_Negative <= 1) with Global => null;                         --  adb:45
function Can_Reserve_Value
  (Available_Negative : Interfaces.Unsigned_8;
   Available, Withheld, Floor, Requested : Worldline.Resources.Byte_Array)
   return Interfaces.Unsigned_8 is
  (if not Negative_Flag_Valid (Available_Negative) then 255             --  V3 re-check (costed)
   elsif Worldline.Resource_Wire.Can_Reserve
           (Available_Negative = 1, Available, Withheld, Floor, Requested)
   then 1 else 0)                                                        --  adb:53-62
  with Global => null;
```
- **v3 deltas** (A-COST §C3): one flag re-check, and one extra call level for four arrays whose passing mechanism is unspecified.
- **REQUIRED_PROVED:** positions 1–2.
- **Pins:** unit pair and C_API pair regenerated.
- **Controls:**
  - `tests/test_resource_kernel.py:30-40` (roster [12]);
  - Ada `resource-tests` ([20]/[21]);
  - C-03: flags 2..255; NULL with zero length accepted; NULL with nonzero length 255; oversize length 255.
- **OPEN:**
  - proof;
  - `Worldline.Resources.Can_Reserve` is listed NOT_FULLY_PROVED in STRICT (diagnostic only, N-03);
  - installed legality (D-38).

### U2. `worldline-recovery_c_api` (PK-1)

- **Modes:** spec On (ads:8), body On (adb:5).
- **F10K:** 1 error (adb:32:23), 1 address-to-access, 0 representation.
- **S5 note.**
  - `Worldline.Recovery.Optional_Marker` has no default discriminants in S5 (`core/worldline-recovery.ads:9-16`, packet 01; operator approval record cited in §0).
  - An `Optional_Marker` object must therefore be constrained by its declaration or initialization; no unconstrained maximum-sized object can be declared.
  - The original's constrained-object pattern (adb:71-79) is kept exactly.
- **C profile:** identical to ads:16-23, with identifier `Recovery_Select` (A-BIND §B3).
- **Staged order** (original adb:61-86):
  1. Chain → 255 (adb:66):
     - [S] `Presence_Valid (Live_Present, Prepared_Present)` (the first two conjuncts of adb:61);
     - [T] `Recovery_Transport.Shape (Expected, Expected_Length)` (adb:62);
     - [S] `Present (Live_Present)` and then [T] not `Shape (Live, …)` (adb:63);
     - the same for Prepared (adb:64).

     An absent marker's pointer and length are never examined.
  2. [T] Copy Expected (adb:69-70).
  3. [P][T] If `Present (Live_Present)`, copy Live; otherwise use the empty constant `Recovery_Transport.Empty`. Absent memory is never read.
  4. The same for Prepared.
  5. [S] `return Select_Value (Expected_Value, Live_Present, Live_Value, Prepared_Present, Prepared_Value)`.
- **Writes:** none.
- **Handler:** 255 (adb:84-85), covering every copy and allocation.
- **Value routines** (the spec gains `with Worldline.Recovery;`):
```ada
function Presence_Valid (Live_Present, Prepared_Present : Interfaces.Unsigned_8) return Boolean is
  (Live_Present <= 1 and then Prepared_Present <= 1) with Global => null;   --  adb:61
function Present (Flag : Interfaces.Unsigned_8) return Boolean is (Flag = 1)
  with Global => null;                                                       --  adb:63-64, 72-78
function Marker_Of
  (Present_Flag : Interfaces.Unsigned_8; Value : Worldline.Recovery.Identity_Bytes)
   return Worldline.Recovery.Optional_Marker with Global => null;
--  Body: adb:37-51 minus the raw Copy: if Present_Flag /= 1 then the extended return of
--  adb:42-44 (Present => False, Length => 0); otherwise the extended return of adb:46-50
--  with (Present => True, Length => Value'Length) and Result.Value := Value.
function Select_Value
  (Expected : Worldline.Recovery.Identity_Bytes;
   Live_Present : Interfaces.Unsigned_8; Live : Worldline.Recovery.Identity_Bytes;
   Prepared_Present : Interfaces.Unsigned_8; Prepared : Worldline.Recovery.Identity_Bytes)
   return Interfaces.Unsigned_8 with Global => null;
--  Body: if not Presence_Valid then 255 (V3, dead on transport paths); otherwise constrained
--  constants exactly as adb:71-79 (Present => Flag = 1, Length => (if Flag = 1 then Value'Length
--  else 0)) initialized by Marker_Of, and Recovery_Action'Pos (Select_Action (...)) (adb:81-82).
```
- **v3 deltas** (A-COST §C4).
  - The copy graph changes. Each present marker's bytes now live as a transport constant until `Select_Value` returns, in addition to the marker copy built by `Marker_Of`.
  - Flag tests are re-evaluated: one transport `Present` per marker, one `Presence_Valid` re-check, the two constraint expressions, and `Marker_Of`'s test.
  - The peak-memory and copy effects are native obligations, OPEN.
- **REQUIRED_PROVED:** 3–6.
- **Controls:**
  - `tests/test_recovery_kernel.py:23-45`, `:58-85` (roster [12]);
  - C-03: flags 2..255; a present marker that is NULL with nonzero length; oversize and wrap;
  - C-05: an absent marker on a PROT_NONE page with nonzero length (not read).
- **OPEN:** proof; full native accepted-domain evidence for the marker copy graph.

### U3. `worldline-recovery_authorization_c_api` (v2) (PK-2)

- **Modes:** On/On. No C header declares `_v2`; its ABI is the Ada profile plus ctypes.
- **F10K:** 7 errors, 2 address-to-access, 61 representation (57 staying in `Layout` adb:18-114, 4 moving).
- **C profile:** identical to ads:15-20, with identifier `Recovery_Authorization_Decide_V2`.
- **Staged order** (original adb:129-150):
  1. [T] Guards, verbatim: lengths against `'Size`, `Shape` on Input and Output, both alignments → -1.
  2. [T] `Raw := Request_At (Input).all` (whole-record capture).
  3. [S] `if not Worldline.Recovery_Authorization_Wire.Well_Formed (Raw) then return -1` (the existing total relation, LD5).
  4. [S] `Owned : constant Raw_Result := Decide_Total (Raw)`.
  5. [T] `Result_At (Output).all := Owned` (one write of a completed local; D-36).
  6. Return 0.
- **Writes:** one record, on success only.
- **Overlap:** accepted (adb:144-145 comment). All input is captured at step 2.
- **Handler:** -1 (adb:149-150), covering all steps.
- **Value routine:** `function Decide_Total (Raw : W.Raw_Request) return W.Raw_Result is (if W.Well_Formed (Raw) then W.Decide (Raw) else (Action => 0, State => 0)) with Global => null;`. The else value is never published, because step 3 refused first.
- **v3 deltas** (A-COST §C5): one extra `Well_Formed` per call in both builds; the `Owned` local and its copy.
- **REQUIRED_PROVED:** 7.
- **Controls:**
  - `tests/test_recovery_witness_relation.py:59-218` (roster [47]);
  - C-03: same buffer for Input and Output (accepted); NULL, length and alignment refusals;
  - C-14 (proposed behaviour, not baseline): no partial write on an internal exception.
- **OPEN:** D-36; proof; native delta.

### U4. `worldline-recovery_authorization_v3_c_api` (v3) (PK-2)

- **Modes:** On/On.
- **F10K:** 8 errors, 3 address-to-access, 64 representation (60 staying, 4 moving).
- **C profile:** identical to ads:15-21, with identifier `Recovery_Authorization_Decide_V3`.
- **Staged order** (original adb:139-167):
  1. [T] Guards, verbatim (adb:139-146), including `Arena_Length > Q.Byte_Count'Last` and `(Arena_Length > 0 and then not Shape (Arena, …))`. A zero-length arena's pointer is never checked. → -1.
  2. [T] `Raw` capture (adb:151) and `Data` allocation (adb:152).
  3. [T] The arena is copied unconditionally (adb:154-157).
  4. [S] `if not W.Well_Formed (Data, Raw) then return -1` (adb:158-160).
  5. [S] `Owned := Decide_Total (Data, Raw)`.
  6. [T] `Result_At (Output).all := Owned` (adb:163); return 0.
- **Writes:** one record, on success only.
- **Overlap:** accepted (adb:161-162).
- **Handler:** -1 (adb:166-167).
- **Value routine:** `Decide_Total (Data : Resource_Quantities.Byte_Array; Raw : W.Raw_Request) return W.Raw_Result is (if W.Well_Formed (Data, Raw) then W.Decide (Data, Raw) else (Action => 0, State => 0))`.
- **Manifest:** re-maps the predecessor at `proof_manifest.py:500-504` (A-BIND §B5 E1).
- **Symbol mapping:** `runtime/worldline/protected_recovery_capture.py:166-172` requires the symbol in an executable mapping of the loaded library (D-15).
- **REQUIRED_PROVED:** 8.
- **Controls:**
  - `tests/test_recovery_witness_relation_v3.py:59-282` (roster [49]);
  - C-03: `Arena_Length = 0` with a NULL arena accepted; Output aliasing Input or lying inside Arena; refusals.
- **OPEN:** D-36; D-15; proof; native delta.

### U5. `worldline-recovery_protocol_c_api` (PK-2)

- **Modes:** On/On; `Worldline.Recovery_Protocol_ABI` is On.
- **F10K:** 6 errors, 2 address-to-access, 11 representation (7 staying, 4 moving).
- **C profile:** identical to ads:9-13, with identifier `Recovery_Protocol_Decide_V1`.
- **Staged order** (original adb:49-70):
  1. Guards → -1.
  2. [T] `Raw` capture.
  3. [T] `Owned_Result : Raw_Result := (After => 0)`, a local; Output is never read.
  4. [S] The existing `Worldline.Recovery_Protocol_ABI.Apply (Raw, Owned_Result, Status)` (Global null; Post at `worldline-recovery_protocol_abi.ads:14-24`).
  5. [P] `if Status /= Success then return Status` (no write).
  6. [T] `Result_At (Output).all := Owned_Result`; return 0.
- **Writes:** one, on success only.
- **Overlap:** accepted. The typed adapter passes the same buffer (`tests/test_recovery_protocol_typed_adapter.py:12-22`).
- **Handler:** -1.
- **Value routines:** none new (`Apply` is already enrolled, `proof_manifest.py:1003`).
- **Manifest:** re-maps `proof_manifest.py:929-937` (A-BIND §B5 E2).
- **Controls** (all outside the 52-action roster, retained):
  - the typed adapter, `tests/test_recovery_protocol_native.py:9-29`, `protocol-adapter-tests`, `recovery-protocol-tests`;
  - C-03: length mismatch, oversize input.
- **OPEN:** D-15; controls; native correspondence (no source delta besides location).

### U6. `worldline-reservation_lifecycle_c_api` (PK-3)

- **Modes:** On/On.
- **F10K:** 13 errors, 3 address-to-access, 5 representation (4 staying, 1 moving).
- **C profile:** identical to ads:34-40, with identifier `Reservation_Lifecycle_Plan` (it uses the C_API subtypes `Size` and `U8`).
- **Staged order** (original adb:59-118):
  1. [T] `Row_Size := Worldline.Reservation_Lifecycle_C_API.Layout_Size` (adb:59, outside the handler).
  2. Chain (adb:61-74) → 255:
     - [T] the three `Byte_Count'Last` bounds and the row-count overflow (adb:61-64);
     - [S] `not Request_Valid (Present, Requested_First, Requested_Length)` (adb:65-69);
     - [T] three `Extent_Valid` (adb:70-72).

     `Mode` is never checked here; an unknown mode becomes `Unknown_Operation`, a typed refusal.
  3. [T] `Arena := Copy_Data (Data, Data_Length)` (adb:77), `Typed_Rows` (adb:78), and `Mask := (others => False)` (adb:79-80, kept in the transport).
  4. [S] `Requested := Requested_Of (…)` (adb:81-85) and [S] `Selected_Mode := Operation_Of (Mode)` (adb:86-90).
  5. Per row:
     - [T] read `Row_C` (adb:95-96);
     - [S] `D := Accept_Row (Row)`;
     - [P] `if not D.Ok then return 255` (later rows unread, nothing written);
     - `Typed_Rows (I) := D.Item` (adb:103-105).
  6. [S] The existing `Resource_Reservation_Lifecycle.Plan (…)` (`resource_reservation_lifecycle.ads:98-104`).
  7. [S] `if Publishes_Mask (Status)`, then for each mask byte a [T] store of [S] `Mask_Byte (Mask (I))` (adb:109-114).
  8. Return [S] `Status_Code (Status)` (adb:115).
- **Writes:** mask bytes only, and only for No_Change or Removal_Planned. Typed refusals leave Removed unchanged (ads:32-33).
- **Overlap:** a disjointness premise (ads:5-8), unchecked.
- **Handler:** 255.
- **Value routines** (unchanged from v2):
```ada
function Request_Valid (Present : U8; Requested_First, Requested_Length : Size) return Boolean is
  (not (Present > 1 or else
        (Present = 1 and then
          (Requested_First < 1
           or else Requested_First > Size (Worldline.Resources.Byte_Count'Last)
           or else Requested_Length > Size (Worldline.Resources.Byte_Count'Last)))))  --  adb:65-69
  with Global => null;
function Requested_Of (Present : U8; Requested_First, Requested_Length : Size)
   return Resource_Reservation_Lifecycle.Optional_Identity is
  (if Present = 1 and then Request_Valid (Present, Requested_First, Requested_Length)
   then (Present => True,
         Value => (Worldline.Resources.Byte_Index (Requested_First),
                   Worldline.Resources.Byte_Count (Requested_Length)))
   else (Present => False)) with Global => null;                                   --  adb:81-85
function Operation_Of (Mode : U8) return Resource_Reservation_Lifecycle.Operation is
  (case Mode is
     when 1 => Resource_Reservation_Lifecycle.Release_Exact,
     when 2 => Resource_Reservation_Lifecycle.Reconcile_Observed,
     when others => Resource_Reservation_Lifecycle.Unknown_Operation) with Global => null;  --  adb:86-90
type Row_Acceptance (Ok : Boolean := False) is record
   case Ok is
      when True  => Item : Resource_Reservation_Lifecycle.Reservation_Entry;
      when False => null;
   end case;
end record;
function Accept_Row (Row : Row_C) return Row_Acceptance is
  (if Row.First < 1 or else Row.First > Size (Worldline.Resources.Byte_Count'Last)
      or else Row.Length > Size (Worldline.Resources.Byte_Count'Last) or else Row.Observed > 2
   then (Ok => False)
   else (Ok => True,
         Item => (Identity => (Worldline.Resources.Byte_Index (Row.First),
                               Worldline.Resources.Byte_Count (Row.Length)),
                  Observed => Resource_Reservation_Lifecycle.Liveness'Val (Row.Observed))))  --  adb:98-105
  with Global => null;
function Publishes_Mask (Status : Resource_Reservation_Lifecycle.Result_Status) return Boolean is
  (Status in Resource_Reservation_Lifecycle.No_Change
           | Resource_Reservation_Lifecycle.Removal_Planned) with Global => null;   --  adb:109
function Mask_Byte (Remove : Boolean) return U8 is (Boolean'Pos (Remove)) with Global => null;  --  adb:111-112
function Status_Code (Status : Resource_Reservation_Lifecycle.Result_Status) return U8 is
  (Resource_Reservation_Lifecycle.Result_Status'Pos (Status)) with Global => null;  --  adb:115
```
- **v3 deltas** (A-COST §C8): one `Request_Valid` re-check; per-row acceptance temporaries; one SPARK call per mask byte over a loop whose length the caller sets.
- **REQUIRED_PROVED:** 9–15.
- **Controls:**
  - `tests/test_reservation_lifecycle.py:30-179` (roster [12]);
  - Ada `reservation-tests` ([18]/[19]);
  - C-02: No_Change over a nonzero mask;
  - C-05: a malformed row k with later rows on PROT_NONE.
- **OPEN:** proof; native per-byte call cost.

### U7. `worldline-resource_ledger_c_api` (PK-3)

- **Modes:** On/On.
- **F10K:** 34 errors, 9 address-to-access, 27 representation (15 staying, 12 moving).
- **C profiles:** identical to ads:38-44 and ads:51-57, with identifiers `Resource_Ledger_Compute` and `Resource_Ledger_Headroom`.
- **Compute staged order** (original adb:115-176):
  1. [T] `Row_Size`, `Quantity_Size` (adb:115-116).
  2. [T] Guards, verbatim (adb:118-131) → 255.
  3. [T] Data is read first (adb:136), then the allocations in order (adb:137-143).
  4. Per row:
     - [T] read (adb:147-148);
     - [S] `D := Accept_Row (V)`;
     - [P] `if not D.Ok then return 255` (later rows unread, nothing written);
     - `Typed_Rows (I) := D.Row; Slots (I) := D.Slot` (adb:157-159).
  5. [S] The existing `Resource_Ledger.Compute (…)` (`resource_ledger.ads:199-206`; its outputs are `out`).
  6. **Unconditional writes, in this order, whatever `Status` is:**
     - [T] `Write_Data (Detail_Data, Detail_Arena)` (adb:164);
     - [T] `Write_Data (Total_Data, Total_Arena)` (adb:165);
     - per detail, a [T] store of [S] `Encode_Quantity (Typed_Details (I))` (adb:166-170);
     - a [T] store of [S] `Result_Of (Status, Total)` (adb:171-172).
  7. Return 0.
- **Headroom staged order** (original adb:184-223):
  1. [T] `Quantity_Size`.
  2. [T] Guards (adb:186-194) → 255.
  3. [T] Read A, W, F (adb:199-201).
  4. [S] `HI := Accept_Headroom_Inputs (A, W, F)`, then [P] `if not HI.Ok then return 255`. This gates the Data read (adb:203-204).
  5. [T] Data copy (adb:207) and `Output_Arena` allocation (adb:208).
  6. [S] The existing `Resource_Ledger.Compute_Headroom (Arena, HI.Available, HI.Withheld, HI.Floor, Output_Arena, Typed_Result, Status)` (adb:212-214). The three decodes move from adb:213 into the acceptor (M4).
  7. [T] `Write_Data (Output, Output_Arena)` (adb:215), then a store of [S] `Result_Of (Status, Typed_Result)` (adb:216-218); return 0.
- **Writes:** unconditional after the compute (not a blanket rule).
- **Overlap:** a disjointness premise (ads:6-9), unchecked. All reads precede the first write.
- **Handler:** 255, covering the nested allocations. **A partial write is possible if an exception occurs during writeback, exactly as in the original.** PK-0 does not assert otherwise (§9.6).
- **Value routines** (unchanged from v2; the completions in the body use the body-local `Shape`/`Decode`/`Encode`, adb:74-88):
  - `Row_Acceptance (Ok; Row : Resource_Ledger.Reservation_Row; Slot : Resource_Ledger.Output_Span)` and `Accept_Row`;
  - `Encode_Quantity (V) return Quantity_C` (= `Encode (V)`);
  - `Result_Of (Status, Total) return Result_C` (= `(Status => Result_Status'Pos (Status), Total => Encode (Total))`);
  - `Headroom_Acceptance (Ok; Available, Withheld, Floor : Quantity)` and `Accept_Headroom_Inputs`.
- **v3 deltas** (A-COST §C9): per-row temporaries; a per-detail call into another unit to `Encode_Quantity` instead of a body-local expression; result temporaries.
- **REQUIRED_PROVED:** 16–19.
- **Controls:**
  - `tests/test_resource_ledger.py:237-371` and `tests/test_resource_headroom.py:51-121` (roster [12]);
  - Ada `resource-ledger-correspondence-tests` (retained);
  - C-02: outputs pre-filled with 0xA5 for typed refusals;
  - C-05: a malformed row k, with later rows and all outputs on PROT_NONE.
- **OPEN:** `Resource_Ledger.Compute` is NOT_FULLY_PROVED in STRICT (N-03); D-05 decoders; proof.

### U8. `worldline-resource_policy_c_api` (PK-3)

- **Modes:** On/On.
- **F10K:** 41 errors, 4 address-to-access, 33 representation (27 staying, 6 moving).
- **C profile:** identical to ads:58-62, with identifier `Resource_Policy_Admit`.
- **Staged order** (original adb:118-182):
  1. [T] `Disk_Size`.
  2. [T] Guards (adb:120-128) → 255.
  3. [T] `V := As_Input (Input).all` (adb:133).
  4. [S] `IA := Accept_Input (V)`, then [P] `if not IA.Ok then return 255`. This gates every Disks and Data read. The ten decodes of adb:146-151 move into the acceptor (M4).
  5. [T] `Rows` allocation (adb:152).
  6. Per row:
     - [T] read (adb:156-157);
     - [S] `D := Accept_Disk (Row)`;
     - [P] refuse 255 (later rows and Data are never read);
     - `Rows (I) := D.Item`.
  7. [T] Data is read last (adb:168).
  8. [S] The existing `Resource_Admission.Admit (Arena, IA.State, Rows)` (adb:169).
  9. [T] Store [S] `Encode_Decision (Decision)` into Result (adb:171-176); return 0.
- **Writes:** one `Result_C` on every transport-success path.
- **Overlap:** Result may alias inputs (not forbidden, ads:6-8). Capture-before-write is preserved.
- **Handler:** 255.
- **Value routines** (unchanged from v2): `Input_Acceptance`/`Accept_Input`, `Disk_Acceptance`/`Accept_Disk`, and `Encode_Decision` (the aggregate of adb:171-176, verbatim).
- **v3 deltas** (A-COST §C10): the write construction changes from a direct aggregate store to a SPARK result copied once.
- **REQUIRED_PROVED:** 20–22.
- **Controls:**
  - `tests/test_resource_policy.py:52-176` and the admission paths in `test_resource_kernel.py`/`test_resource_ledger.py` (roster [12]);
  - C-01: a malformed row k with Result pre-filled;
  - C-03: Result aliasing an input (accepted);
  - C-05.
- **OPEN:** proof; D-05; D-36 (write construction).

### U9. `worldline-evaluation_history_c_api` (PK-4)

- **Modes:** On/On.
- **F10K:** 34 errors, 5 address-to-access, 36 representation (32 staying, 4 moving).
- **C profile:** identical to ads:52-57, with identifier `Evaluation_History_Select`.
- **Staged order** (original adb:131-190):
  1. [T] `Stride := Layout_Size (4)` (adb:131).
  2. One chain → 255, with no overlap check:
     - [T] the three bounds (adb:133-135);
     - [S] `not Final_Flag_Valid (Final_Present)` (adb:136);
     - [T] Data and Rows extents (adb:137-138);
     - [S] `Final_Row_Present (Final_Present)` and then [T] not `Extent_Valid (Final_Row, …)` (adb:139-140);
     - [T] Query and Output extents (adb:141-142).
  3. [T] Read `Raw_Q` (adb:146); copy Data (adb:147), before the query is validated, as the original does; allocate `History` (adb:148); declare `F : H.Optional_Record` (adb:149), default-initialized to absent.
  4. [S] `QA := Accept_Query (Raw_Q)`, then [P] refuse 255. This gates every row read. The query decode moves from adb:175-178 into the acceptor (M4).
  5. If [S] `Final_Row_Present (Final_Present)` (adb:157):
     - [T] read `Final_Row` (adb:159);
     - [S] `FA := Accept_Final_Row (V)`;
     - [P] refuse 255 (history rows unread);
     - `F := FA.Item`.
  6. Per row:
     - [T] read (adb:167-168);
     - [S] `D := Accept_Row (V)`;
     - [P] refuse 255;
     - `History (I) := D.Item`.
  7. [S] `Result := Select_Result (A, History, F, QA.Item)` (adb:179-183).
  8. [T] `As_Selection (Output).all := Result` (adb:185); return 0.
- **Writes:** one `Selection_C`, on success only (ads:49-50).
- **Overlap:** unchecked (a header premise).
- **Handler:** 255 (adb:189-190).
- **Value routines** (unchanged from v2): `Final_Flag_Valid`, `Final_Row_Present`, `Query_Acceptance`/`Accept_Query`, `Row_Acceptance`/`Accept_Row`, `Final_Acceptance`/`Accept_Final_Row`, `Select_Result`.
- **REQUIRED_PROVED:** 23–28.
- **Controls:**
  - `tests/test_evaluation_history.py:29-191` (roster [14]);
  - Ada `evaluation-history-tests` ([16]/[17]);
  - C-01: every 255 path, with Output pre-filled;
  - C-05: a malformed query, with Rows and Final_Row on PROT_NONE (Data is read; rows are not).
- **OPEN:** proof; D-05; D-11 flow on the staying `Layout_Offset` locals (adb:34-39).

### U12. `resource_run_ledger_c_api` (PK-5)

- **Modes:** On/On.
- **F10K:** 11 errors, 6 address-to-access, 99 representation (90 staying in `Layout` adb:34-184, 9 moving).
- **Deployment:** a digest-pinned library loaded by `protected-resource/run_service.py:117-119` (N-06).
- **C profile:** identical to ads:9-16, with identifier `Run_Ledger_Check`.
- **Staged order** (original adb:192-222):
  1. [T] `Row_Size` and `Native_Size` keep `'Size` (adb:192-193).
  2. [T] Guards, verbatim (adb:195-204) → -1.
  3. [T] Packet capture and four allocations (adb:207-211).
  4. [T] Read Data, Before, Proposed and Native **unconditionally** (adb:213-216).
  5. [S] `O := Check_Decision (Data, Raw, Before, Proposed, Observed)`, then [P] `if not O.Ok then return -1` (no write; adb:217).
  6. [T] `Result_At (Output).all := O.Value` (adb:219); return 0.
- **Writes:** one, on success only. `tests/test_resource_run_ledger_v1.py:215-219` asserts that the output is untouched on refusal.
- **Overlap:** accepted (adb:218 comment).
- **Handler:** -1. It covers `Storage_Error` from release-build Big_Integer arithmetic reached through `W.Decide`; such a refusal never counts as success.
- **Value routine** (the cost-neutral pattern; `W.Well_Formed` is evaluated once, as in the original): `Check_Acceptance (Ok; Value : Resource_Run_Ledger_Wire.Raw_Result)`, and `Check_Decision … is (if W.Well_Formed (Data, Raw, Before, Proposed, Observed) then (Ok => True, Value => W.Decide (…)) else (Ok => False))`.
- **REQUIRED_PROVED:** 29.
- **Controls:**
  - `tests/test_resource_run_ledger_v1.py:59-225` and `protected-resource/controls/test_full_resource_replay_v2.py` (outside the roster; retained);
  - Ada `wire-initialization-tests` and `decision-correspondence-tests`;
  - C-03: per guard, and accepted overlap.
- **OPEN:**
  - N-06;
  - D-35 native cost;
  - `Resource_Run_Ledger_Wire.Decode_Native` is NOT_FULLY_PROVED (N-03);
  - D-34;
  - D-36 (the write construction changes).

### U13. `worldline-chain_authority_c_api` (PK-5)

- **Modes:** On/On.
- **F10K:** 11 errors, 3 address-to-access, 27 representation (21 staying, 6 moving).
- **C profile:** identical to ads:9-14, with identifier `Chain_Replay`.
- **Staged order** (original adb:70-102):
  1. [T] `Stride := W.Raw_Row'Size / Storage_Unit` (adb:70).
  2. [T] Guards, verbatim (adb:72-81), including the exact `Rows_Length /= Rows_Count * Stride` → -1.
  3. [T] Anchors capture (adb:85) and `Owned` allocation, **before** the anchors check (adb:86).
  4. [S] `if not W.Well_Formed (H) then return -1` (adb:88; no row is read on failure).
  5. Per row:
     - [T] read (adb:91-92);
     - [S] `D := Accept_Row (Raw)`;
     - [P] refuse -1 (later rows unread);
     - `Owned (I) := D.Item` (adb:95).
  6. [S] `RV := Replay_Value (Owned, H)`, then [P] refuse -1 (dead by V3).
  7. [T] `Result_At (Output).all := RV.Value`; return 0.
- **Writes:** one, on success only.
- **Overlap:** unchecked; none added.
- **Handler:** -1.
- **Value routines:**
  - `Accept_Row`: `Well_Formed (Raw)` then `Decode (Raw)`; Pre at `wire.ads:48-53`.
  - `Replay_Value`: re-checks `Well_Formed (H)`, then `W.Decide (Owned, H)`; Pre at `wire.ads:59-60`. Its result type is `Replay_Acceptance (Ok; Value : Worldline.Chain_Authority_Wire.Raw_Result)`.
  - `Replay_Value` is completed in `core/worldline-chain_authority_c_api.adb`, where `W` is declared (`:5`). It has a statement body ending `end Replay_Value;`, and its accepting return is `return (Ok => True, Value => W.Decide (Owned, H));` (A-BIND §B5 E3).
- **Manifest:** re-maps `proof_manifest.py:943-950` (A-BIND §B5 E3). It keeps the decision-to-output protection, with isolated exact tokens.
- **REQUIRED_PROVED:** 30–31.
- **Controls:**
  - `tests/test_chain_authority_native.py:25-68` (outside the roster; retained) and Ada `chain-bounds-tests`;
  - C-01;
  - C-05: a malformed digest, with Rows on PROT_NONE.
- **OPEN:** `Worldline.Chain_Authority.Replay` is NOT_FULLY_PROVED (N-03); D-36; proof.

### U14. `evaluation_completion_c` (`Evaluation_Completion_C`) (PK-6a value routines, PK-6b transport)

- **Modes:** On/On. There is no pending-component copy.
- **F10K:** 600 errors, 30 address-to-access, 205 representation (154 staying in the layout functions adb:90-257, 695-731 and 871-891; 51 moving).
- **Exports and helpers:**
  - Four exports move: `Completion_Decide`, `Completion_Raw_Decide`, `Completion_Metadata_Matches` and `Native_Diagnostic_Control`.
  - `Context_Matches` and `Metadata_Base` move as `Completion_Transport` helpers.
  - `Copy_Data`, `Extent_Valid`, `Disjoint`, `Array_Valid` and the pointer instances move to `Completion_Transport`.
  - The diagnostic procedures are replaced per §4.
  - Six layout/version exports stay.
- **C profiles:** only the identifiers change (A-BIND §B3).

**`Completion_Decide` staged order** (original adb:394-527):
1. [T] Six size constants (adb:394-399).
2. [T] Input/Output extents and disjointness (adb:401-404) → 255.
3. [T] `R` capture (adb:405-406).
4. Chain → 255:
   - [S] `not Decide_Header_Valid (R)` (adb:408);
   - [T] adb:409-415 (Data extent, Data/Output disjointness, five `Array_Valid`);
   - [S] `not Decide_Fields_Valid (R)` (adb:416-420).
5. [T] In the original order: `A := Copy_Data (R.Data, R.Data_Length)`, then `J`, `Measures`, `Captured`, `Retained_Results`, `History` and `Required` (adb:423-429; the exact declarations of §5.4), then `Response : Result; Status : Interfaces.C.int`. The `Retained` construction (adb:431-433) and the `Response` initialization move into `Decide_Value`.
6. Journal rows: [T] read (adb:443-444); [S] `JA := Accept_Journal_Row (X)`; [P] refuse 255; `J (I) := JA.Item`.
7. Captured rows: [S] `CR := Accept_Captured_Row (X)`; [P] refuse 255; `Captured (I) := CR.Item; Measures (I) := CR.Measure` (adb:458-465).
8. Retained rows, regardless of `Retained_Present` (adb:468-475).
9. History rows, for every operation (adb:477-484).
10. Required rows, for every operation (adb:486-493).
11. [S] `Decide_Value (R, A, J, Captured, Measures, Retained_Results, History, Required, Response, Status)` (adb:431-439, :495-520, with the §5.4 index).
12. [P] `if Status /= 0 then return Status` (dead by V3).
13. [T] `Outputs.To_Pointer (Output).all := Response` (adb:522); return 0.

Handler: 255 (adb:526-527).

**`Completion_Raw_Decide`** (original adb:530-692). As above, with these differences:
- [S] `Raw_Header_Valid` (adb:545), which includes the `Operation /= 2` gate.
- [T] The guards add `Raw_Rows` and `Confinements` (adb:546-556).
- [S] `Raw_Fields_Valid` (adb:557-561, text identical to adb:416-420).
- `Measures : Raw_Roster.Measured_Array` (adb:566).
- The captured loop is staged per row:
  1. [T] read check row I (adb:599-600);
  2. [S] `KA := Accept_Raw_Check_Row (X)`;
  3. [P] refuse 255 (the raw wire and confinement of row I are not read when it fails);
  4. `Captured (I) := KA.Item` (adb:603);
  5. [T] read `Wire` (adb:605-606), then `Confined` (adb:607-608);
  6. [S] `MA := Accept_Raw_Measure (KA.Item, KA.Declared, Wire, Confined)`;
  7. [P] refuse 255;
  8. `Measures (I) := MA.Item` (adb:613-614).
- The retained, history and required loops are unconditional (adb:618-643).
- [S] `Raw_Decide_Value (…)` keeps the genuine post-decision 255 (adb:657-671), so `if Status /= 0 then return Status` is real.
- [T] Write (adb:687); handler 255.

**`Completion_Transport.Context_Matches`** (original adb:742-868):
1. [T] `Diagnostic_Transport.Mark ("completion.context.enter")`.
2. [T] Four extents (adb:751-754) → Mark `…input-extents-rejected`, 255.
3. [T] Read `R`, `X`, `Raw_Collapse` and `Raw_Agent`, in that order (adb:760-763; collapse and agent are re-read, D-27).
4. Chain (adb:765-780) → Mark `…transport-guard-rejected`, 255:
   - [S] `Context_Header_Valid (R, X)` (adb:765);
   - [T] `Extent_Valid (X.Data, …)` (adb:766);
   - [S] `Context_Fields_Valid (R, X)` (adb:767-774);
   - [T] adb:775-779;
   - [S] `Context_Agent_Matches (X, Raw_Agent, Agent_Confinement)` (adb:780).
5. [T] Mark `copy-arenas`; copy `Data`, then `Context_Data`; allocate `Rows`, `Joined`, `Required` and `Expected_Required` (adb:785-792); Mark `arenas-copied`.
6. [S] `FA := Accept_Context_Fields (X)` (§5.2). [P] If not Ok: `Value ("…field-rejected", FA.Rejected_Position)`, 255.
7. Per row pair:
   - [T] read `Original`, then `Owned` (adb:807-810);
   - [S] `RA := Accept_Context_Row (Original, Owned)`;
   - [P] `case RA.Verdict` with the original marks (adb:813, :822-824) and 255;
   - otherwise `Rows (I) := RA.Row; Joined (I) := RA.Joined`.
8. Per required pair:
   - [T] reads (adb:834-837);
   - [S] `QA := Accept_Required_Pair (Original, Owned)`;
   - [P] Value `required-rejected=I`, 255;
   - otherwise assign both items (adb:845-846).
9. [T] Mark `join`.
10. [S] `V := Context_Join_Value (R, X, Raw_Collapse, Data, Context_Data, FA.Expected, FA.Observed, Rows, Joined, Required, Expected_Required)` (adb:850-857).
11. [P] `Join_Malformed` → 255 (dead by V3).
12. [T] `Value ("…join-result", I64 (Join_Code (V = Join_Match)))` (adb:859-860).
13. Return `Join_Code (V = Join_Match)` (adb:861).

Handler: `when Error : others => Diagnostic_Transport.Exception_Text ("completion.context", Error); return 255;` (adb:865-868).

**`Completion_Metadata_Matches`** (original adb:914-985):
1. Mark enter.
2. Two extents (adb:922-923) → Mark, 255.
3. Read `R`, then `X` (adb:929-930).
4. Chain: [S] `Metadata_Header_Valid (R, X)` (adb:932-933), then [T] adb:934-938 → Mark, 255.
5. Mark copy-arenas; copy `Data`, then `Projected_Data`; allocate `Rows` and `Projected`; Mark arenas-copied.
6. Per row:
   - [T] read `Original`, then `Owned` (adb:953-956);
   - [S] `MA := Accept_Metadata_Row (Original, Owned)`;
   - [P] Value `row-rejected=I`, 255;
   - otherwise assign.
7. Mark join.
8. [S] The existing `Worldline.Evaluation_Authority.Join_Metadata (Data, Projected_Data, Rows, Projected)` (no Pre, `worldline-evaluation_authority.ads:270-273`).
9. Value join-result; return `Join_Code (Joined)`.

Handler: `Exception_Text ("completion.metadata", Error)`, 255.

**`Completion_Transport.Metadata_Base`** (original adb:893-907):
1. [T] Extent → `Null_Address`.
2. [T] Read `X`.
3. [S] `Metadata_Version_Valid (X)`, then [T] `Extent_Valid (X.Base, …)` → `Null_Address`.
4. Return `X.Base`.

Handler: `Null_Address`.

**`Native_Diagnostic_Control`** and `Diagnostic_Transport`: §4.4.

**Writes.**
- Decide and Raw_Decide write the whole `Result` once, on success. The others write nothing.
- The padding of `Result` is copied from the locally built object and is unspecified, as before (D-20).

**Overlap.**
- Decide and Raw_Decide refuse an Output that overlaps any input array (adb:403, :410-415, :540, :547-556).
- Context and metadata refuse arrays that overlap the descriptor (adb:776-779, :936-938).
- Ada callers pass the addresses of Ada-owned locals (D-26).

**Value routines (SPARK, PK-6a).** The 24 of v2, with these changes:
- `Accept_Context_Fields` and `Accept_Context_Row` are the total functions of §5.2.
- `Decide_Value`/`Raw_Decide_Value` follow §5.3–§5.5: no bounds re-check; the `History_Index` index; the raw re-check uses `Decide_Header_Valid`.
- `Context_Join_Value` re-checks `Context_Header_Valid` and `Context_Fields_Valid` (V3) before `Worldline.Evaluation_Authority.Join_Context`.

Added: the 12 diagnostic routines of §4.2 and the constant `Initial_Response`. The remaining v2 profiles are unchanged:
```ada
function Decide_Header_Valid (R : Request) return Boolean with Global => null;  --  adb:408 negated
function Decide_Fields_Valid (R : Request) return Boolean with Global => null;  --  adb:416-420 negated
function Raw_Header_Valid    (R : Request) return Boolean with Global => null;  --  adb:545 negated
function Raw_Fields_Valid    (R : Request) return Boolean with Global => null;  --  adb:557-561 negated
function Context_Header_Valid (R : Request; X : Context_Input) return Boolean with Global => null;   --  adb:765
function Context_Fields_Valid (R : Request; X : Context_Input) return Boolean with Global => null;   --  adb:767-774
function Context_Agent_Matches (X : Context_Input; Raw_Agent : Worldline.Evaluation_Wire.Raw_Record;
   Agent_Confinement : Interfaces.Unsigned_8) return Boolean with Global => null;                     --  adb:780
function Metadata_Version_Valid (X : Metadata_Context) return Boolean is (X.Version = 1)
  with Global => null;                                                                                 --  adb:901
function Metadata_Header_Valid (R : Request; X : Metadata_Context) return Boolean with Global => null; --  adb:932-933
--  Acceptance records and functions, each returning a fully defined active variant:
--  Accept_Journal_Row (adb:446-453), Accept_Captured_Row (Item and Measure, adb:461-465),
--  Accept_Result_Row (adb:473-474), Accept_History_Row (adb:482-483), Accept_Required_Row
--  (adb:491-492), Accept_Raw_Check_Row (Item and Declared, adb:602-603, :614),
--  Accept_Raw_Measure (adb:610-614), Accept_Required_Pair (Item and Expected, adb:839-846),
--  Accept_Metadata_Row (Row and Projected, adb:958-968).
procedure Decide_Value
  (R : Request; Arena : Evaluation_Pending.Bytes; Journal : Evaluation_Pending_V2.Journal;
   Captured : Evaluation_Completion.Result_Array;
   Measures : Evaluation_Completion_Roster.Measured_Array;
   Retained_Results : Evaluation_Completion.Result_Array;
   History : in out Evaluation_History.History;
   Required : Evaluation_Completion_Roster.Check_Array;
   Response : out Result; Status : out Interfaces.C.int)
  with Global => null, Always_Terminates;
--  Raw_Decide_Value: the same profile with Measures : Evaluation_Raw_Roster.Measured_Array.
type Join_Verdict is (Join_Malformed, Join_Mismatch, Join_Match);
--  Context_Join_Value (R, X, Raw_Collapse, Data, Context_Data, Expected, Observed, Rows, Joined,
--  Required, Expected_Required) return Join_Verdict, adb:850-857.
function Join_Code (Joined : Boolean) return Interfaces.C.int is (if Joined then 1 else 0)
  with Global => null;                                                       --  adb:861, :978
```

**Existing relations, called as before:** `T.Decide`, `T.Apply`, `T.Find_Run`, `Roster.Classify` (now enrolled, N-04), `Decide_Envelope`, `Raw_Roster.Row_Bound`/`Classify`, `Join_Context`, `Join_Metadata` and `W.Well_Formed`. None has a Pre (v2 citations re-checked). New: `T.History_Index` (§5.4).

**REQUIRED_PROVED:** 32–68.

**Pins:** the unit pair, the C_API pair, and (PK-6b) `core/evaluation_finalization_c.*`.

**Controls:**
- roster [4], [6], [7]/[8], [22], [23], [24]/[25], [31]–[36], [40], [48];
- lifetime `tests/test_context_cast_lifetime.py` (UNRUN);
- additive C-01, C-04, C-05, C-06, C-15.

**OPEN:** D-05, D-18 proof, D-19, D-20 padding, D-23 foreign faults, N-01's 154 staying warnings, proof of all routines, all controls.

### U15. `evaluation_finalization_c` (`Evaluation_Finalization_C`) (PK-6a value routines, PK-6b transport)

- **Modes:** On/On.
- **F10K:** 255 errors, 11 address-to-access, 79 representation (67 staying in `Layout` adb:511-567 and `Version` adb:34; 12 moving).

**`Finalization_Decide`** (original adb:122-256):
1. [T] Constants (adb:122-125).
2. [T] `Mark ("finalization.decide.enter")`.
3. [T] Extents/disjointness (adb:128-130) → Mark `input-extents-rejected`, 255.
4. [T] Read `X` (adb:136).
5. Chain → Mark `transport-guard-rejected`, 255:
   - [S] `Request_Header_Valid (X)` (adb:138);
   - [T] adb:139-144 (the Rows extent is checked for every operation);
   - [S] `Request_Fields_Valid (X)` (adb:145-153).
6. [T] Mark `copy-arena`; `A := Copy_Data` (adb:160); allocate `Required` (adb:161) and **`Captured (1 .. P.Count (X.Row_Count))` for every operation** (adb:162). `S` and `Response` (adb:163-166) move into the value routines.
7. Per plan:
   - [T] read (adb:170-171);
   - [S] `PA := Accept_Plan (Q)`;
   - [P] `Value ("…required-rejected", I64 (K))`, 255;
   - otherwise `Required (K) := PA.Item`.
8. §5.1: if [S] `Needs_Rows (X)`, the row loop and `Decide_Rows_Value`; otherwise `Decide_No_Rows_Value`.
9. [P] Dead `not O.Ok` → 255.
10. [T] `Value ("…reason", I64 (O.Value.Reason))` and `Value ("…promotion", I64 (O.Value.Promotion))` (adb:247-248); `Outputs.To_Pointer (Output).all := O.Value` (adb:249); return 0.

Handler: `Exception_Text ("finalization.decide", Error)`, 255 (adb:253-256).

**`Finalization_Transport.Final_Context_Matches`** (original adb:261-354):
1. [T] `Native : aliased Evaluation_Finalization_C.Result := Evaluation_Finalization_C.Initial_Result;` (D-28).
2. Mark enter.
3. [T] `Seal_Status := Finalization_Decide (Input, Native'Address)`. This is an address-based self-call with every guard (D-26). It is called before `Native` is read, as in the original's left-to-right `or else`.
4. [S] `Final_Seal_Ready (Seal_Status, Native)` → Mark `seal-rejected`, False.
5. [T] Re-read `X` (adb:280).
6. [S] `Final_Plans_Valid (X)` (adb:282-286) → Mark, False.
7. [T] Allocate `Projected_Rows`, `Projected_Plans` and `Projection`, with the local Convention C array types of adb:267-270.
8. Per row: [T] read `Original` (adb:302-303); [S] `Projected_Rows (I) := Final_Projected_Row (X, Original)` (adb:307-311; not re-validated, as in the original).
9. Per plan: [T] verbatim copy (adb:314-318).
10. [S] `Projection := Final_Projection (X, Native, Projected_Rows'Address, Projected_Plans'Address)`. The addresses are computed in the transport and passed as values (D-29).
11. Mark projected.
12. [T] `Context_Result := Completion_Transport.Context_Matches (Projection'Address, Completion_Transport.Metadata_Base (Metadata), Collapse, Agent, Agent_Confinement)`. The order of the actuals is unspecified, as before.
13. Value context-result; [P] `/= 1` → False.
14. [T] `Metadata_Result := Completion_Metadata_Matches (Projection'Address, Metadata)`.
15. Value metadata-result; return `Metadata_Result = 1`.

Handler: `Exception_Text ("finalization.context", Error)`, False.

**`Finalization_Decide_Mixed`** (original adb:363-508).

The nested `Read_Ready` switches on [S] `Kind_Of (Kind)`:
- Absent → `(True, 0)`.
- Ordinary:
  1. [T] `Ordinary : aliased Evaluation_Completion_C.Result := Evaluation_Completion_C.Initial_Response;` (D-28);
  2. [T] `Completion_Raw_Decide (Input, Raw, Confined, Ordinary'Address)`;
  3. return [S] `Ordinary_Readiness (Status, Ordinary)`.
- Finalized:
  1. [T] `Finalized : aliased Result := Initial_Result;`;
  2. [T] `Finalization_Decide (Input, Finalized'Address)`;
  3. [S] `R1 := Finalized_Readiness (Status, Finalized)`, then [P] `if not R1.Valid then return R1`;
  4. [T] re-read the header (adb:390);
  5. return [S] `Finalized_Operation_Readiness (X, Finalized)`.
- Invalid → `(False, 0)`.

The nested `Context_Joined` also switches on [S] `Kind_Of`.

Main sequence:
1. Mark enter.
2. Collapse extent → Mark, `Invalid_Request`.
3. [T] `Bound` read (adb:419).
4. [S] The existing `Worldline.Evaluation_Authority.Dependencies (Bound)` (adb:420). [P] `Invalid_Collapse` → Mark, return.
5. If [S] `Needs_Primary`: `Read_Ready` primary. [P] Invalid → Mark, return.
6. The same for staged.
7. Values primary-ready and staged-ready.
8. If [S] `Needs_Agent (Needed)` and then [T] `Agent /= Null_Address`:
   - [T] agent extent → Mark, return;
   - [T] read `Owned_Agent`;
   - [S] `Agent_Ready := Agent_Readiness (Owned_Agent, Agent_Confinement)` (one `Confined_Admit_Wire`);
   - [P] `= W.Invalid_Record` → Mark, return.
9. Value agent-ready.
10. If [S] `Context_Join_Needed (Agent_Ready, P_Ready)` and then not `Context_Joined (Primary_Kind, Primary, Primary_Context)` → Mark, return. The same for staged.
11. [S] `Decision := Mixed_Collapse_Decision (Bound, Agent_Ready, P_Ready, S_Ready)`.
12. Value collapse-decision.
13. [P] If not [S] `Mixed_Authorized (Decision)`, return `Decision` (no metadata read).
14. If [S] `Mixed_Metadata_Needed (Needed, True, Primary_Kind)` and then [T] `Completion_Metadata_Matches (Primary, Primary_Context) /= 1` → Mark, return. The same for staged.
15. Return `Decision`.

Handler: `Exception_Text ("finalization.mixed", Error)`, `Invalid_Request`. `Read_Ready` and `Context_Joined` have no handlers, as before.

**Writes.**
- `Finalization_Decide` writes `Result` once on transport success (Reason 0, 1 or 2).
- The others write only Ada-owned locals.

**Overlap.**
- Decide refuses an Output that overlaps Input, Data, Required or Rows.
- Mixed-entry pointers may overlap (read-only).
- Repeated reads are preserved: the header (adb:280, :390); collapse and agent inside Context_Matches; the double Seal on the Kind-2 path (D-27).

**Value routines (SPARK, PK-6a; 20):** `Request_Header_Valid`, `Request_Fields_Valid`, `Plan_Acceptance`/`Accept_Plan`, `Needs_Rows`, `Row_Acceptance`/`Accept_Row`, **`Decide_No_Rows_Value`, `Decide_Rows_Value`** (§5.1), `Final_Seal_Ready`, `Final_Plans_Valid`, `Final_Projected_Row`, `Final_Projection`, `Kind_Of`, `Ordinary_Readiness`, `Finalized_Readiness`, `Finalized_Operation_Readiness`, `Agent_Readiness`, `Context_Join_Needed`, `Mixed_Collapse_Decision`, `Mixed_Authorized` and `Mixed_Metadata_Needed`, plus the constant `Initial_Result`. The bodies are as in v2, except the §5.1 split:
```ada
function Request_Header_Valid (X : Request) return Boolean is
  (X.Version = 1 and then X.Operation <= 3) with Global => null;           --  adb:138
function Needs_Rows (X : Request) return Boolean is (X.Operation >= 2) with Global => null;   --  adb:183-188
function Final_Seal_Ready (Status : Interfaces.C.int; Native : Result) return Boolean is
  (Status = 0 and then Native.Reason = 0 and then Native.Promotion = 1) with Global => null;   --  adb:273-274
type Source_Kind is (Absent_Source, Ordinary_Source, Finalized_Source, Invalid_Source);
function Kind_Of (Kind : U32) return Source_Kind is
  (if Kind = 0 then Absent_Source elsif Kind = 1 then Ordinary_Source
   elsif Kind = 2 then Finalized_Source else Invalid_Source) with Global => null;
type Readiness_Result is record Valid : Boolean; Ready : U8; end record;    --  moved from adb:366-369
function Agent_Readiness
  (Owned_Agent : Worldline.Evaluation_Wire.Raw_Record; Agent_Confinement : U8) return U8 is
  (declare
     Admitted : constant U8 :=
       Worldline.Evaluation_Wire.Confined_Admit_Wire (Owned_Agent, Agent_Confinement);
   begin
     (if Admitted = Worldline.Evaluation_Wire.Invalid_Record then Admitted
      elsif Owned_Agent.Observations (Worldline.Evaluation_Wire.Source_Field)
            /= Worldline.Evaluation_Wire.E.Origin'Pos (Worldline.Evaluation_Wire.E.Agent)
      then 0 else Admitted)) with Global => null;                             --  adb:463-469
function Mixed_Collapse_Decision
  (Bound : Worldline.Collapse_Wire.Raw_Request; Agent_Ready, P_Ready, S_Ready : U8) return U8 is
  (Worldline.Collapse_Wire.Decide_Wire
     ((Bound with delta
         Roster_Complete => (if Agent_Ready = 1 then P_Ready else 0),
         Staged_Roster_Complete => (if Agent_Ready = 1 then S_Ready else 0)))) with Global => null;  --  adb:485-487
```

**Manifest:** re-maps `proof_manifest.py:488-499` (A-BIND §B5 E4).

**REQUIRED_PROVED:** 69–88.

**Controls:**
- roster [43], [44], [4];
- lifetime `tests/test_finalization_cast_lifetime.py` and `tests/test_context_cast_lifetime.py` (UNRUN);
- Ada `finalization-value-controls` (retained);
- additive:
  - C-05: Operations 0/1 with Rows on PROT_NONE; `Decision /= Authorized` with the metadata descriptor on PROT_NONE;
  - C-11: mixed-entry coverage;
  - C-06: diagnostic sequences;
  - C-16.

**OPEN:** D-24…D-31; `Evaluation_Finalization.Seal` is listed NOT_FULLY_PROVED in STRICT (N-03); N-01's 67 staying warnings; proof; controls; native deltas.

### U10 and U11. `evaluation_pending_c` and `evaluation_pending_v2_c` (PK-7, gated by D-13)

- **Modes:** On/On; the component copies are Off (LD3).
- **F10K:** v1 66 errors, 4 address-to-access, 41 representation (38 staying, 3 moving); v2 70, 4, 48 (45, 3).
- **C profiles:** `Pending_Decide_V1 (Input, Output : System.Address) return Interfaces.C.int` and `Pending_Decide_V2`, identical to ads:45-46 and ads:52-53 apart from the identifier.

**v1 staged order** (original adb:106-173):
1. [T] `Request_Size := Evaluation_Pending_C.Layout_Size (4)`, `Result_Size := … (5)`, `Stride := … (3)` (adb:106-108).
2. [T] Fixed extents and `Disjoint (Input, …, Output, …)` (adb:111-115) → 255.
3. [T] `R` capture (adb:118).
4. Chain (adb:120-131) → 255:
   - [S] `not Header_Valid (R)` (adb:120: Version, Operation);
   - [T] adb:121-127 (length signs, stride, overflow, Data and Rows extents, Output disjoint from Data and Rows);
   - [S] `not Request_Fields_Valid (R)` (adb:128-131).
5. [T] `A := Copy_Data (R.Data, R.Data_Length)` (adb:136) and the `J` allocation (adb:137).
6. Per row:
   - [T] read at `Object_Size` stride (adb:143-144);
   - [S] `D := Accept_Row (V)`;
   - [P] refuse 255;
   - `J (I) := D.Item`.
7. [S] `O := Decide_Value (A, J, R)`, which re-checks header and fields (V3); [P] dead refusal.
8. [T] `Result_Pointers.To_Pointer (Output).all := O.Value` (adb:165); return 0.

**v2** (original adb:127-197) has the same shape, with Version 2, `Valid (R.Required)` in the field run (adb:151), `Valid (V.Requirement)` in rows (adb:171) and `Export_Requirement` in the result (adb:188-192).

- **Writes:** one `Result`, on success only.
- **Overlap:** an Output that overlaps the request, Data or Rows is refused (adb:113, :126-127).
- **Handler:** 255.
- **Value routines** (unchanged from v2): `Header_Valid`, `Request_Fields_Valid`, `Row_Acceptance`/`Accept_Row` and `Decide_Acceptance`/`Decide_Value`, for each version.
- **Component.** The mirror and the component's export surface follow the operator's D-13 choice (§16.1). Identity binding: CONTRACT_PINS keys for the four component files, `pending-component/pending.gpr` and any new component transport unit (§8.7).
- **REQUIRED_PROVED:** 89–98, including `Evaluation_Pending.Decide` (93) and `Evaluation_Pending_V2.Decide` (98) (N-07).
- **Controls:**
  - `tests/test_evaluation_pending.py` (roster [15]);
  - `tests/test_evaluation_pending_requirements.py` (roster [9]);
  - roster [2] `pending-build`;
  - additive C-01/C-03/C-04/C-05 (every 255 path; none is produced today) and C-10 correspondence.
- **OPEN:** D-13; proof; D-11 flow on the `'Position` locals; native deltas; component evidence.

---

## 8. RC4: enforceable manifest-binding specification

The checks below are additions to the export check chain. They never disable or weaken a predecessor, and their literal tables are given per stage in A-BIND.

They are necessary guards only. Reachability, exact actuals, gating and use of the real result also require the pinned full-body and caller review. No textual occurrence closes that obligation.

### 8.1 Tables appended by PK-1 and extended by every later stage

- `CAPI_CORE_HOME`: every C symbol of the core closure → its designed home file at this stage. That is the 60 inventory symbols plus the 31 existing `Worldline.C_API` symbols, 91 observed in total (JACKAL exact `60+31`).
- `CAPI_DECLARATIONS`: for each export relocated at or before this stage, its exact normalized declaration (A-BIND §B3).
- `CAPI_ORDERED` and `CAPI_COUNTS`: for each isolated unit, the isolation rule, the ordered token list with its write rules, and exact token multiplicities (A-BIND §B4). Isolated units are the export bodies, the transport helpers, `Diagnostic_Transport` and the two retargeted `Authority_Glue` functions.
- `CAPI_DIAGNOSTIC_SITES`: the ordered site-literal sequences, from PK-6b (A-BIND §B6).
- `CAPI_COMPONENT_HOME` and `CAPI_COMPONENT_INTERFACE`: the ten `wl_pending_*` symbols → their component home, and the component's `Library_Interface` units. These are the original values until PK-7, and after PK-7 whatever the D-13 choice requires (A-BIND §B2.3).
- Each later stage appends `.update({...})` lines only; nothing earlier is deleted or reordered.
- The `export_problems` override is defined once (PK-1) and reads the tables at call time. So every stage's effective table is complete for all 91 closure symbols (§9.4).

### 8.2 Whole-closure alternate-binding checks

**Core closure** = every `core/*.ad[sb]` and `core/attest/*.ad[sb]` file, each read through `normalized_ada`. Observed: 137 Ada files, equal to the `DECLARED_CORE_ADA_SOURCES` set that the existing `stray_sources`/`missing_sources` checks enforce (`proof_manifest.py:611-620`).

- **G1** The set of string literals matching `"wl_[a-z0-9_]+"` across the closure equals the key set of `CAPI_CORE_HOME`, and each occurs exactly once. Observed today: 91 literals, 91 `Export` tokens, 91 `External_Name =>` tokens, 0 `Import` tokens.
- **G2** Each occurrence is immediately preceded by `External_Name => ` and lies in its designed home file.
  - For relocated exports, the enclosing declaration text equals the `CAPI_DECLARATIONS` entry.
  - For staying exports, the enclosing spec's pin is unchanged unless a reviewed packet changed it.
- **G3** None of these occurs anywhere in the closure: `Link_Name`, the identifier `Import`, `pragma Export`, `pragma Import`, `pragma Linker_Section`, `Export_Function`, `Export_Procedure`, `Export_Object`, `Import_Function`, `Import_Procedure`, `Import_Object`, `Import_Valued_Procedure`.
- **G4** The counts of `Export` tokens, `External_Name =>` tokens and `"wl_…"` literals are equal across the closure: no export lacks an explicit literal name, and no external name is renamed or computed.
- **G5** The three closure projects `core/worldline_core.gpr`, `core/worldline_core_sources.gpr` and `core/attest_sha256.gpr` contain no `Linker_Options`, `--defsym`, `--wrap`, `-Wl,` or version-script option. They are pinned and in `source_paths`, and this design does not change them.
- **G6** No relocated symbol occurs in its old spec (zero count).
- **G7** After a unit's move stage, its spec and body contain no `Address_To_Access_Conversions`, no `Ada.Unchecked_Conversion` and no `'Address` attribute (N-02). Observed today: every moving unit uses one of the two conversion forms (A-BIND §B4 transport lists).
- **G8** After PK-6b, `Ada.Text_IO` and `Ada.Exceptions` do not occur in `core/evaluation_completion_c.ad[sb]`.

**Component closure** = `pending-component/core/*.ad[sb]` (observed: 14 Ada files) plus `pending-component/pending.gpr`.

- **K1** The ten `wl_pending_*` literals occur exactly once each in the component closure, at their `CAPI_COMPONENT_HOME` file, each preceded by `External_Name => `. Observed today: five in each component spec.
- **K2** G3 and G4 hold for the component closure.
- **K3** `pending.gpr`'s `Library_Interface` lists every unit that holds a component export (after PK-7, including any D-13 transport unit) and keeps every original interface unit. Observed: 8 units (A-BIND §B2.3).
- **K4** The mirrored component files equal the core files except for the `SPARK_Mode` line. C-10 is the behavioural complement, and identity is bound separately (§8.7).

**Matching-library evidence** (native, OPEN, D-15):
- The built `libworldline_core` exports exactly the closure symbols, each resolving to the expected Ada subprogram and lying in an executable mapping. This is the `protected_recovery_capture.py:166-172` check, for v3, protocol and raw v3.
- The built `libevaluation_pending` exports exactly its ten symbols.

### 8.3 Resolved C profile

- **P1** Each relocated declaration equals the original normalized declaration with only the subprogram identifier replaced. A-BIND §B3 gives both texts' sha256 and the successor text.
- **P2** `core/worldline-c_api.ads` contains each of `subtype U8 is Interfaces.Unsigned_8;`, `subtype U32 is Interfaces.Unsigned_32;`, `subtype I64 is Interfaces.Integer_64;` and `subtype Size is Interfaces.C.size_t;` exactly once. No other declaration of `U8`, `U32`, `I64` or `Size` occurs in the C_API spec or body.
  - Observed today: there is none. The spec declares `subtype Byte is Interfaces.Unsigned_8;` (`:185`). The body uses `Size` only as the attribute `'Size` (`core/worldline-c_api.adb:550-555`) and `K.U32` inside `Authority_Glue` (`:764`).
- **P3** The 40 staying declarations, and every unchanged version/layout assertion (v3 `version`/`layout`, protocol `version`/`layout`), stay as they are.
- Compiler and native ABI evidence (calling convention, record layout, actual symbol profile) remains OPEN. Unchanged text is not that evidence.

### 8.4 Ordered required calls and exact result-to-write paths

- **O1 Isolation.**
  - For a subprogram `N`: `end N;` occurs exactly once in the file. The isolated text runs from the nearest preceding `function N ` or `procedure N ` to that `end N;`.
  - This is a variant of `contract_text` (`proof_manifest.py:437-446`) that tolerates a separate declaration earlier in the file, which the body-local transport packages need.
  - For a body-local package: from the unique `package body N is` to the following `end N;`.
  - An isolation failure is a problem, never a skip.
- **O2 Order.** The tokens of the unit's list occur in the isolated text as an ordered subsequence. Each token is found after the end of the previous token's match, so repeated substrings cannot satisfy the order early.
- **O3 Multiplicity.**
  - Tokens marked with an exact count occur exactly that many times.
  - In particular, every write statement into foreign memory (`… .all :=`, `Write_Data`) occurs exactly the listed number of times.
- **O4 Result-to-write.**
  - The written expression is exactly the listed SPARK result variable or component.
  - That variable is declared `constant` from exactly the listed SPARK call. The one exception is `Finalization_Decide`, whose variable is assigned exactly once on each of two exclusive paths, from the two listed calls, and nowhere else.
  - Its discriminant test precedes the write (A1).
- **O5 Gating.** Each acceptance declaration or assignment is followed by its discriminant test and the original refusal statement, with at most `begin` between them.
- **O6 Qualification and renames.**
  - (a) Every call to a routine named in Appendix C uses its full expanded name.
  - (b) The C_API body declares no package `renames` beyond:
    - the pre-existing S5 ones, with their occurrences unchanged;
    - inside each transport package or moved subprogram, exactly the renames the original unit declares there (A-BIND §B4).
  - (c) The only non-`use type` use clause in an export body is `use <Unit>_Transport;`.
  - The B4 tokens enforce (a). Checking (b) and (c) needs a renames/use inventory that the A-BIND §B8 sketch does not yet contain. That check is OPEN and part of PK-1.
  - The pre-existing `package K renames Evaluation_Completion_C;` inside `Authority_Glue` stays and may still name types (`K.Result`, `K.U32`).
- **O7 Retargeting.** The two `Authority_Glue` functions contain the four retargeted calls in their original positions, and no call through `K.` remains.

### 8.5 Diagnostic confinement (RC1 enforcement, from PK-6b)

- **D1** The C_API body contains no object declared `with Atomic` and no occurrence of `Diagnostic_Active` or `Diagnostic_Failed`.
- **D2** `Ada.Text_IO.Put_Line`, `Ada.Text_IO.Flush` and `Standard_Error` occur only inside the isolated `Diagnostic_Transport.Mark`. `Ada.Exceptions.Exception_Information` occurs only inside `Diagnostic_Transport.Exception_Text`.
- **D3** In each isolated transport, the ordered list of diagnostic site literals equals the S5 list for the corresponding original function (A-BIND §B6).
- **D4** `Diagnostic_Transport` contains the ordered tokens of A-BIND §B4.24: each SPARK step precedes its I/O, and each handler calls only `Diagnostic_Latch_Failure`.
- **D5** `core/evaluation_completion_c.adb` declares `Diagnostic_Active : Boolean := False with Atomic;` and `Diagnostic_Failed : Boolean := False with Atomic;` exactly once each. Its spec declares the `Diagnostic_State` abstract state with `External` and no narrowed property.

### 8.6 Preserved predecessor assertions

- **PP1** Exactly four in-place edits are made to existing manifest code. Each goes through compose's single-occurrence `manifest-edits.json` and is recorded with its old and new text (A-BIND §B5):

  | Edit | Stage | Lines replaced | Inside |
  |---|---|---|---|
  | E1 | PK-2 | `:500-504` | the v3 decide check of the base function |
  | E2 | PK-2 | `:932-936` | the protocol override `:929-937` |
  | E3 | PK-5 | `:946-949` | the chain override `:943-950` |
  | E4 | PK-6b | `:488-491` | the finalization entries `:488-499` |

  Each edit changes only the moved symbol's check, keeps every other symbol's check and keeps the problem message text.
- **PP2** Every other predecessor function and assertion is byte-identical to the base. This covers the base collapse, raw v1/v2/v3, dependency and metadata checks (`:453-487`), the owner transition (`:956-964`), the owner audit (`:975-994`), all pins and the policy lines. Check: undoing the recorded edits in the successor manifest text and deleting the appended tails must reproduce the base manifest exactly.
- **PP3** The new override calls its predecessor first, as every existing override does (`:927-931`).

### 8.7 Identity binding for every touched file

| Layer | Files | Binding |
|---|---|---|
| I1 | Touched core Ada sources: the 15 unit pairs, the C_API pair, and wire specs touched by representation repairs. `evaluation_completion_roster.ads` is not touched. | `CONTRACT_PINS` regenerated per stage by compose's re-pin, with the manifest's own normalization (`proof_manifest.py:9-10`); `sourceHashes` (raw bytes) at proof time (`:870-878`); `DECLARED_CORE_ADA_SOURCES` unchanged |
| I2 | Core projects and headers | `sourceHashes` (`source_paths`, `:649-660`) and their existing pins; unchanged by this design |
| I3 | Component Ada sources and project: `pending-component/core/evaluation_pending_c.ads`/`.adb`, `evaluation_pending_v2_c.ads`/`.adb`, any D-13 transport unit, `pending-component/pending.gpr` | **New `CONTRACT_PINS` keys.** Precedent: `pending-component/core/resource_quantities.*` and `evaluation_epoch.*` are pinned today. This changes `proof_source_files` (`:662-667`) by those paths; that additive install-set change is part of PK-7's review. Under D-13 option (i), the key count goes from 169 (observed in S5) to 176 (JACKAL exact `169+4+2+1`). |
| I4 | New Ada control projects, if a packet adds any | New `CONTRACT_PINS` keys. Precedent: S5 packet 01 pinned `explicit-recovery-marker-tests/*`. |
| I5 | New Python controls, helpers and data tables (`tests/test_capi_*.py`, `tests/capi_guard_pages.py`, `tests/capi_characterization.json`, `tests/capi_layout_baseline.json`) | Exact raw-bytes sha256 in each stage's composition `source-inventory.json`, bound by the stage review freeze, and bound again as inputs by every execution frame that runs them (a mismatch refuses). **Not** `CONTRACT_PINS`: `normalized_ada` strips text after `--` outside double quotes, which would leave parts of Python code unbound. A gate-level raw-bytes table is an option for the reviewer, but it would need its own reviewed change to `proof_source_files`. |
| I6 | Provider files (`runtime/worldline/*.py` ctypes bindings, headers) | This design touches none. A packet that touches one must add I5 binding and a review of the caller correspondence. |
| I7 | The manifest and the whole tree | Each stage's `source-inventory.json` (every file, bytes and mode); `composition.json` (base identity, packet identities, pin delta, recorded manifest edits); the review freeze. The final frame binds the exact manifest bytes. Every file a stage does not touch keeps its base raw sha256 (A-BIND §B7). |

Optional additive protection, recommended but not required by any touched-file rule: pin `core/evaluation_pending.ads`/`.adb`. They are unpinned today (observed: 9 core files are unpinned), and N-07 makes `Evaluation_Pending.Decide` an explicit claim. The key count would become 178 (JACKAL exact `169+4+2+1+2`).

### 8.8 Mutation controls (C-09, static, temporary trees, no WORLDLINE run)

Each mutation must produce a problem.

| Target | Mutations |
|---|---|
| Each relocated export | Move its declaration back to the old spec; duplicate it; rename the external name; add an `Import` or `Link_Name` alias anywhere in the closure; change a parameter subtype; reorder two ordered tokens; delete a required SPARK call, or move it outside the isolated body; replace the written variable; add a second write; remove the discriminant test; add a `renames` of a SPARK unit |
| The component | Alias a pending symbol from a second component file |
| RC1 | Declare an `Atomic` object in the C_API body; call `Put_Line` outside `Mark`; drop or reorder a diagnostic site |
| Predecessors | Apply any edit outside the four recorded ones; reorder the override chain |

### 8.9 What these checks do not establish

They do not establish:
- reachability;
- faithful actuals beyond the token text;
- the native symbol table, calling conventions or layouts;
- custody of foreign memory;
- producer authenticity;
- that a passing check implies proof.

D-15, D-34 and D-38 remain OPEN.

---

## 9. RC5: lineage, stages, append schedule, characterization, representation placement and seal limits

### 9.1 Composition lineage

- **L0** = `claude-composition-v5-beta` (identities in §0).
  - A newer GPT-6.1-qualified composition may supersede it before PK-0 is composed. In that case L0 becomes that composition, and every touched-file base hash in A-BIND is re-read and re-recorded.
  - Any overlap with this design's touched files (the 15 units, the C_API pair, the manifest, wire specs, component files) is then re-reviewed before PK-0.
- **Strictly linear, single-packet stages.** `L(k) = compose.py (L(k-1), PK-k)`.
  - Each packet is authored against the exact bytes of `L(k-1)`, and each touched file records its base sha256.
  - No two packets are composed in parallel.
  - There is no fresh checkout from commonV4 (v2:2706 withdrawn).
- **Per-stage record.** Each stage records:
  - the base composition sha256;
  - packet.json and the file identities;
  - the recorded manifest tails and edits;
  - the full pin delta;
  - compose's asserted invariants: floor 251; the sole `worldline-c_api` boundary; the REQUIRED_PROVED base list as an exact prefix; `DECLARED_CORE_ADA_SOURCES` and pin keys as supersets;
  - the `source-inventory.json` sha256;
  - the stage's control inventory;
  - a review freeze from an actual gpt-6.1-sol reviewer who is not the author.

  Only a reviewed `L(k)` is a base for `L(k+1)`.
- **Rebase.** If `L(k-1)` changes for any reason, every later packet is re-authored against the new bytes and its affected scope re-reviewed. No pin or review transfers.
- **Conflicts.** The C_API pair, tables, roster and pins are resolved only by a reviewed delta. The representation repairs (§9.7) are packets in the same chain, never edits folded into a seal.

### 9.2 Packet table

| Packet | Content | Touched files | Movers (cumulative) | C_API `External_Name` count | REQUIRED_PROVED appended → length | Predecessor edits | Controls added | Gate |
|---|---|---|---|---|---|---|---|---|
| PK-0 | Characterization only (§9.6) | new `tests/test_capi_characterization.py`, `tests/test_capi_layout_identity.py`, `tests/test_capi_diagnostics.py`, `tests/capi_guard_pages.py`, `tests/capi_characterization.json`, `tests/capi_layout_baseline.json` (I5) | 0 | 31 | 0 → 535 | none | C-01…C-07, C-11, C-13, C-15, C-16 (baseline forms) | baseline run on L0 in an admitted frame |
| PK-1 | C_API subtypes; `Resources_Transport`, `Recovery_Transport`; U1, U2; the override and stage-1 tables | C_API pair; U1, U2 pairs; manifest tail; new `tests/test_capi_symbol_binding.py`, `tests/test_capi_manifest_mutations.py` (I5) | 2 | 33 | 6 → 541 | none | C-08, C-09 (U1, U2) | review |
| PK-2 | U3, U4, U5 | C_API pair; U3–U5 pairs; manifest tail + edits | 5 | 36 | 2 → 543 | E1, E2 | C-09 (U3–U5) | review |
| PK-2R | Representation repair U3–U5 and the recovery wires (§10) | U3–U5 specs; `worldline-recovery_authorization_wire.ads`, `…_v3_wire.ads`, `worldline-recovery_protocol_wire.ads` as needed | 5 | 36 | 0 → 543 | none | C-13 | review + independent ABI review |
| PK-3 | U6, U7, U8 | C_API pair; U6–U8 pairs; manifest tail | 9 | 40 | 14 → 557 | none | C-09 | review |
| PK-3R | Representation repair U6–U8 | U6–U8 specs | 9 | 40 | 0 → 557 | none | C-13 | review + ABI review |
| PK-4 | U9 | C_API pair; U9 pair; manifest tail | 10 | 41 | 6 → 563 | none | C-09 | review |
| PK-4R | Representation repair U9 | U9 spec | 10 | 41 | 0 → 563 | none | C-13 | review + ABI review |
| PK-5 | U12, U13 | C_API pair; U12, U13 pairs; manifest tail + edit | 12 | 43 | 3 → 566 | E3 | C-09 | review |
| PK-5R | Representation repair U12, U13 and their wires | U12, U13 specs; `resource_run_ledger_wire.ads`, `worldline-chain_authority_wire.ads` | 12 | 43 | 0 → 566 | none | C-13 | review + ABI review |
| PK-6a | **Value routines only** for U14/U15, including the RC1 state machine, additive; enrolment and pins **in the same packet** | `core/evaluation_completion_c.*`, `core/evaluation_finalization_c.*`; manifest tail (append + pins) | 12 | 43 | 57 → 623 | none | optional Ada value-level controls | review |
| PK-6b | Transport move for U14/U15, `Diagnostic_Transport`, `Authority_Glue` retargeting, removal of raw and Text_IO code from the SPARK units | C_API pair; completion and finalization pairs; manifest tail + edit | 18 | 49 | 0 → 623 (no duplicate names) | E4 | C-06, C-09 (U14, U15) | review |
| PK-6R | Representation repair U14, U15 and any referenced wire type (collapse, evaluation wires) | U14, U15 specs; `worldline-collapse_wire.ads`, `worldline-evaluation_wire.ads` as needed | 18 | 49 | 0 → 623 | none | C-13 | review + ABI review |
| PK-7 | U10, U11 and the component per D-13 | C_API pair; U10, U11 pairs; component files and `pending.gpr`; manifest tail (+ component keys) | 20 | 51 | 10 → 633 | none | C-09, C-10 | **operator D-13**, review |
| PK-7R | Representation repair U10, U11 and the mirrored component specs | U10, U11 specs; component specs | 20 | 51 | 0 → 633 | none | C-13 | review + ABI review |
| PK-S | Seal (§9.8) | none | 20 | 51 | 0 → 633 | none | all retained | review |

All cumulative numbers are JACKAL exact (Appendix A). Without an operator D-13 decision, the chain stops after PK-6R and PK-S cannot occur, because the pending units would remain SPARK-illegal.

### 9.3 Monotonic append schedule

- **AS1** The final suffix is Appendix C: 98 names (JACKAL exact `95+3`), in packet order PK-1, PK-2, PK-3, PK-4, PK-5, PK-6a, PK-7. The final length is 633 (JACKAL exact `535+98`).
- **AS2** Each packet appends exactly its Appendix C slice, after the previous packet's slice. No packet removes, reorders or re-appends an enrolled name. PK-6b, PK-xR and PK-S append nothing.
- **AS3** These stay unchanged at every stage:
  - the original ordered 535-name prefix (segments at `proof_manifest.py:25`, `:312`, `:314`, `:924`, `:940`, `:953`, `:967`, `:972`, `:1003`, `:1012`);
  - `MINIMUM_CHECKS = 251` (`:22`);
  - `UNANALYZED_BOUNDARY = {"worldline-c_api"}` (`:316`).
- **AS4** Pending is appended last because its packet waits on D-13. Composing PK-7 earlier would require a reviewed change of Appendix C before any enrolment.
- **AS5** Enrolment by name never replaces complete per-unit body coverage (`:863-868`) or caller proof.

### 9.4 Intermediate binding tables

- At every stage the effective `CAPI_CORE_HOME` lists all 91 closure symbols. Relocated exports are at `core/worldline-c_api.ads`, and every other export is at its unchanged original home.
- A predecessor assertion stays intact until the stage that relocates its symbol. At that stage, exactly its recorded edit is applied.
- Every stage enforces G1–G8, P1–P3 and O1–O7 for the relocated set, and from PK-6b also D1–D5.
- The final override is never disabled.

A-BIND §B1–§B2 gives the per-stage tables.

### 9.5 PK-6a enrolment and PK-6b

- PK-6a appends the 57 completion/finalization names and regenerates the effective pins of the two unit pairs in the same packet. No new semantic body is unenrolled or unbound at any stage.
- PK-6b performs only transport, deletion, retargeting, its predecessor edit and its pin regeneration. It appends no name.

### 9.6 PK-0: original-behaviour characterization

**Per-export effect table** (`tests/capi_characterization.json`, I5). For every export and input class it records the original source's *defined* effect: return code; write set and order; read gating; or "undefined", in which case nothing is asserted.

**Defined, asserted:**
- guard refusals: return before any foreign read or write;
- malformed-row and malformed-header refusals: return before any write, with later rows unread;
- typed refusals with their exact writes: ledger zeroing, lifecycle mask untouched, finalization Reason 1/2 written, completion History_Invalid written;
- successes with their exact writes;
- read gating, via guard pages.

**Undefined, not asserted:**
- behaviour after an internal exception during writeback (ledger partial writes are possible, `worldline-resource_ledger_c_api.adb:162-176`, :212-223);
- whether an in-place function result could partially write before an exception (v2, v3, chain, run ledger, pending, policy, ledger details/result);
- behaviour under foreign-pointer faults (there is no expectation that a fault becomes 255 or -1);
- behaviour when documented premises are violated (ledger output disjointness, lifecycle removed disjointness, history/chain output disjointness).

**Controls built on the table:**
- **C-01** asserts no-write only on the defined refusal paths above.
- **C-03** overlap expectations are export-specific. Both kinds are kept:
  - refused overlaps: pending v1/v2 Output against the request, Data and Rows; completion Output against its inputs; context/metadata arrays against the descriptor; finalization decide;
  - accepted overlaps: v2, v3, protocol same buffer, run ledger, policy Result against inputs.
- **C-05** places must-not-touch memory on PROT_NONE pages in a child process. It asserts only a normal exit with the expected code, never a code for an access fault.
- **C-13 baseline** records, on L0's library, every layout export value (all kinds, fields and sentinels), the ctypes sizes/offsets/alignments, and the C header `sizeof`/`offsetof`/`_Alignof`, for every record type the representation repairs may touch.

**Proposed stronger behaviour is separate.** C-14 (no partial write on an internal exception for local-then-write exports) is review evidence for D-36 only. It is never a baseline assertion and never a PK-0 pass condition.

PK-0 must pass on L0's original library and on every later stage. A baseline behaviour exposed as a defect stays an original obligation; PK-0 cannot delete or redefine it.

### 9.7 Representation-repair placement

- Each PK-xR immediately follows its family's move packet and comes before PK-S. The reason: the installed tool can report representation warnings for a unit only once the unit is SPARK-legal, and today all 15 stop at marking (MAP `STOP_REASON_ERROR_MARKING`).
- Each PK-xR is a separately reviewed ABI-preserving delta (§10.3), with C-13 identity evidence and an independent ABI review.
- A PK-xR that cannot remove a warning without changing a layout leaves N-01 OPEN for those warnings. Nothing is folded into the seal.

### 9.8 PK-S seal limits

- PK-S changes no source, manifest semantics, table, control or enrolment.
- It may only:
  - freeze the identities of the last reviewed stage (source inventory, manifest bytes, control list, pin set, the four recorded edits);
  - assemble the review package;
  - record that compose's re-pin equals the stage's pins.
- Any needed change is a new reviewed packet before PK-S. That includes a late representation fix, a missed enrolment, a control or a reorder.
- PK-S grants no proof, native, control or acceptance credit.

### 9.9 After PK-S (all OPEN, each needing its own admission)

- Scratch-frame engineering (not acceptance).
- The exact strict command on the reviewed integrated candidate.
- The complete original ordered 52-action roster.
- The lifetime, additive, provider, fault and native controls.
- The matching-library checks.
- The final independent actual gpt-6.1-sol review.

---

## 10. RC3: N-01 is an unchanged strict obligation

### 10.1 Observation

MAP lists 736 `[representation-attribute-value]` warnings, all in these 15 units (observed; JACKAL exact `205+79+41+48+99+27+36+61+64+0+11+5+27+33+0` = 736 over the per-unit counts).

| Breakdown | Counts | Basis |
|---|---|---|
| By attribute | `Position` 477, `Alignment` 129, `Object_Size` 88, `Size` 42 | observed; JACKAL exact `477+129+88+42` = 736 |
| By placement | 617 in staying version/layout bodies, 119 in code that moves | script line-range split (ranges in Appendix A); JACKAL exact `617+119` = 736 |

Every `Position` warning is in staying code.

The prefixes include unit-local record types and wire types of other units: `Resource_Run_Ledger_Wire.Raw_*`, `Worldline.Chain_Authority_Wire.Raw_*`, `Worldline.Recovery_Authorization_Wire.Raw_*`, `…_V3_Wire.Raw_*`, `Worldline.Recovery_Protocol_Wire.Raw_*` and `Worldline.Collapse_Wire.Raw_Request`.

### 10.2 Status

- Every applicable representation warning is a strict obligation under the unchanged strict command. There is no operator waiver and no "informational" classification (v2 option (a) withdrawn).
- Moving layout queries into C_API is not resolution (v2 option (c) withdrawn).
- The 119 occurrences in moving guard code leave analysed SPARK because LD1 places irreducible extent/alignment transport in the boundary. **They are not counted as resolved.**
  - The layout facts they use, that each `'Object_Size`, `'Size` and `'Alignment` equals the C and ctypes layout, remain OPEN as boundary surface (OB-048) and as ABI layout obligations (D-34).
  - The confirming clauses of §10.3 pin the same values for the same types.

### 10.3 The confirming-representation-clause delta (PK-xR)

**Scope.** Every record or array type whose `'Position`, `'First_Bit`, `'Last_Bit`, `'Size`, `'Object_Size`, `'Alignment` or `'Component_Size` is queried by analysed SPARK code after the move. This includes wire types in other units, and is enumerated from the successor's own strict report for the family.

**Form.**
- A record representation clause giving every component's position and bit range.
- `Size`, `Object_Size` and `Alignment` attribute definition clauses.
- `Component_Size` for arrays where it is queried.
- `Convention => C` kept.

The installed tool's own message states that component position attributes are imprecise "if the record does not have a record representation clause" (`G/libexec/spark/bin/gnat2why` message text).

**Constraints (C1–C8).**
- **C1** Every clause confirms the layout the compiler already chooses for the target.
- **C2** Every scalar width, signedness and convention is unchanged.
- **C3** Every record `Size`, `Object_Size`, `Alignment`, component position, bit range, array stride and relevant padding is unchanged.
- **C4** Every layout export result is unchanged, including the `I64'Last`, `SIZE_MAX` and -1 sentinels.
- **C5** Every C header and ctypes layout is unchanged, for every actual provider and build scenario: the checks and release builds, the `-O0` component build, and every target the candidate is built for (currently observed: aarch64-linux).
- **C6** Component copies mirror the core clauses (LD3).
- **C7** No new assumption, `pragma Assume`, justification, Pre or suppression.
- **C8** No ABI version change.

**Evidence (E1–E6).**
- **E1** The clause values are derived from the compiler's representation output on the exact stage source, for each target.
- **E2** Installed-tool legality.
- **E3** The strict command on the integrated candidate shows no `[representation-attribute-value]` warning for the family, and the full proof is otherwise unchanged.
- **E4** C-13 shows identity with PK-0's baseline on the matching library.
- **E5** An independent ABI review.
- **E6** A review of the delta by an actual gpt-6.1-sol reviewer who is not its author.

**Failure rule.** If the installed tool still reports the warning with confirming clauses, or a clause would change a defined layout or accepted case, N-01 stays OPEN for those occurrences. Controls alone cannot resolve model imprecision.

**Operator role.** The lead resolves diagnostics, and a confirming clause is not an ABI decision. A non-confirming layout change would be a material ABI change outside this design, and would need the operator's decision first.

---

## 11. RC6: native cost map (summary; complete map in A-COST)

### 11.1 Withdrawn v2 statements

The following are withdrawn and replaced by A-COST (§C1 quotes each):
- v2:2510 ("passed by reference");
- v2:2503 and v2:2537 ("as many times as on the original path … all other exports 0");
- v2:156 ("constant-time");
- v2:2543's per-row statement, as a complete account.

### 11.2 Classification rules used in A-COST

- **Parameters (RM 6.2).**
  - Elementary types are by copy. These are all `U8`, `U32`, `I64`, `Size`, `Interfaces.C.int`, `Boolean` and enumerations, and `System.Address`, a private type whose full type is a modular integer (`G/…/adainclude/system.ads:67`, `:117`).
  - Reading the declarations found no by-reference type in any SPARK value-routine profile: nothing tagged, task, protected, explicitly limited, or containing one. An exhaustive type-closure analysis is OPEN (A-COST §C2).
  - Every other parameter type (untagged records and arrays) has an **unspecified** passing mechanism (RM 6.2(11)). GNAT's selection for the matching build is OPEN and must be resolved from generated code. No row claims "no copy".
- **Results.**
  - Definite results (constrained records, and the acceptance records with defaulted discriminants) are returned through a return object; the copy into the target may or may not be elided.
  - Indefinite results (`String`, unconstrained arrays, `Optional_Marker` in S5) are returned on the secondary stack and copied into constrained targets with a discriminant or length check.
- **Build modes.**
  - Both builds use `-gnatVa` and `-O2` without `-gnatn` (`core/worldline_core_sources.gpr:11-12`); the checks build adds `-gnata` (`:16-17`).
  - Cross-unit calls are therefore real calls.
  - Every new copy point may add validity checks under `-gnatVa`.
  - Every existing `Pre`/`Post` on a called relation is evaluated under `-gnata` wherever the call occurs.

### 11.3 Per-export summary

| Export | Re-evaluations added (V3, LD5) | New temporaries and copies | New initialization | New `-gnata` evaluation | Allocation | Exception/write |
|---|---|---|---|---|---|---|
| resources | flag re-check | one call level for four arrays (mechanism unspecified) | — | — | as original | as original |
| recovery select | `Presence_Valid` re-check; `Present` per marker | marker bytes live as transport constants, plus the marker copy | — | — | marker copies on the secondary stack (as original), with a longer lifetime | as original |
| v2, v3 | one `Well_Formed` each (rel 1 → 2, chk 2 → 3 per accepted call; JACKAL exact `1+1`, `1+1+1`) | `Owned` local and one copy | — | — | v3 `Data` as original | D-36 |
| protocol | none | none | — | — | as original | as original |
| lifecycle | `Request_Valid` in `Requested_Of` | per-row acceptance; a per-byte `Mask_Byte` call | — | — | as original | as original |
| ledger compute/headroom | none | per-row acceptance (two copies); a per-detail cross-unit `Encode_Quantity`; result temporaries | — | — | as original | partial writeback as original; D-36 for result construction |
| policy | none | input acceptance; per-row acceptance; `Encode_Decision` result | — | — | as original | D-36 |
| history | none | query, final-row and per-row acceptance; `Select_Result` | — | — | as original | as original |
| pending v1/v2 | header and fields re-check | per-row acceptance; `Decide_Value` result; `O.Value` copy | — | — | as original | D-36 |
| run ledger | none | `Check_Decision` result; `O.Value` copy | — | — | as original | D-36 |
| chain | `Well_Formed (H)` re-check | per-row acceptance; `Replay_Value` result | — | — | as original | D-36 |
| completion decide/raw | header and fields re-check; `History_Index` | per-row acceptance for five arrays; `in out History` (mechanism unspecified) | `Response` (as original) | `History_Index` Post | as original | as original |
| completion context/metadata | `Context_Header_Valid`, `Context_Fields_Valid` re-check | field and row acceptances; required-pair acceptance; large `Context_Input` parameters | acceptor locals (same values as the original default initialization) | — | as original | as original |
| finalization decide | header and fields re-check | plan and row acceptances (`Start_Row` is large); `O.Value` copy | — | — | `Captured` as original | as original |
| final context / mixed | `Promotion <= 1` in `Finalized_Operation_Readiness`; `Bound` rebuilt per projected row | `Final_Projected_Row`, `Final_Projection` results; `Bound with delta` temporary; readiness results | `Native`, `Ordinary`, `Finalized` (D-28) | — | as original | as original |
| diagnostics | none (atomic accesses unchanged) | SPARK calls per site; `String` results when active; +1 `'Image` per active value site | — | optional Posts only if required | secondary stack when active | latch semantics unchanged |

### 11.4 D-36 generalized: write construction per export

| Export | Original construction | Successor construction | Status |
|---|---|---|---|
| v2, v3 | `Result_At (Output).all := W.Decide (…)` (function result assigned through an access value) | `Owned : constant … := Decide_Total (…)`; one copy | OPEN |
| chain | `Result_At (Output).all := W.Decide (Owned, H)` | `RV := Replay_Value (…)`; one copy of `RV.Value` | OPEN |
| run ledger | `Result_At (Output).all := W.Decide (…)` | `O := Check_Decision (…)`; one copy | OPEN |
| pending v1/v2 | aggregate of `P` fields assigned through an access value | `O := Decide_Value (…)`; one copy | OPEN |
| policy | aggregate of `D` fields assigned through an access value | `Encode_Decision (Decision)` result assigned | OPEN |
| ledger details/result | `Encode (…)` results and an aggregate assigned through access values | `Encode_Quantity`/`Result_Of` results assigned | OPEN |
| lifecycle mask | `Boolean'Pos (Mask (I))` per byte | `Mask_Byte (Mask (I))` per byte | OPEN (cost only) |
| protocol, history, completion, finalization | completed local written once | completed local (now from SPARK) written once | unchanged pattern; copy counts OPEN |

For every row, the matching v2/v3/chain/run-ledger/pending/policy/ledger builds must establish:
- the order in which the completed result is constructed;
- copy and padding effects;
- exception and no-write semantics.

The malformed-input fixture (`tests/test_recovery_witness_relation.py:174-179`) establishes none of them. No global transactional-write claim is made, and no `Storage_Error` is accepted as a refusal of a genuine accepted computation. A-COST §C19 gives the original S5 line of each write.

### 11.5 Original native blockers (all OPEN)

- `H/native-cost-gap/REVIEW.md` full-acceptance blockers: Big_Integer `Normalize` with Bignum_Limit 200 raising `Storage_Error`; runtime selection; representability; allocation failures.
- D1: release-path Big_Integer correspondence (`Resource_Run_Ledger` executables; `Canonical_Artifacts` via `Seal`).
- D2: checks-build Ghost and contract Big_Integer evaluation.
- D-35.
- Implicit controlled `Adjust`/`Finalize`.
- Primary-stack, secondary-stack and heap lifetimes.
- Checked Ghost.
- The actual assertion-build selection.
- Full native accepted-domain correspondence.

---

## 12. ABI and behaviour matrix (R3)

Unchanged by construction for every row, but still needing demonstration:
- symbol name and `Convention => C`;
- parameter order, modes (all `in`) and resolved types;
- return type;
- all record types (they stay in their specs);
- every header and ctypes binding (no provider file is edited);
- the library and its `Library_Interface`.

| Export | Codes | Guard → read staging | Writes | Overlap | Handler | Existing → additive controls |
|---|---|---|---|---|---|---|
| `wl_resources_can_reserve` | 1, 0, 255 | S flag → T four extents → T four copies → S | none | n/a | 255 | [12] → C-03 |
| `wl_recovery_select` | 0/1/2, 255 | S presence → T shapes (present only) → T copies (absent never read) → S | none | n/a | 255 | [12] → C-03, C-05 |
| `wl_recovery_authorization_decide_v2` | 0, -1 | T guards → T capture → S Well_Formed → S Decide_Total | one record, success | accepted | -1 | [47] → C-01, C-03 |
| `wl_recovery_authorization_decide_v3` | 0, -1 | T guards → T capture and unconditional arena → S | one record, success | accepted | -1 | [49] → C-01, C-03 |
| `wl_recovery_protocol_decide_v1` | 0, -1, typed status | T guards → T capture → S Apply → refuse before write | one record, success | accepted (same buffer) | -1 | additive set → C-03 |
| `wl_reservation_lifecycle_plan` | 0–3, 255 | T bounds → S request → T extents → T Data → rows → S Plan | mask only for No_Change or Removal_Planned | premise | 255 | [12], [18]/[19] → C-02, C-05 |
| `wl_resource_ledger_compute` | 0, 255; Result.Status 0–3 | T guards → T Data first → rows → S Compute | unconditional Detail, Total, Details, Result | premise | 255 | [12] → C-02, C-05 |
| `wl_resource_ledger_headroom` | 0, 255 | T guards → T A/W/F → S acceptance gates Data → T Data → S | unconditional Output, Result | premise | 255 | [12] → C-02, C-05 |
| `wl_resource_policy_admit` | 0, 255 | T guards → T Input → S acceptance gates all → rows → T Data last → S | one record | allowed | 255 | [12] → C-01, C-03, C-05 |
| `wl_evaluation_history_select` | 0, 255 | T bounds → S flag → T extents → T query → T Data → S query → final → rows → S | one record, success | unchecked | 255 | [14], [16]/[17] → C-01, C-05 |
| `wl_pending_decide_v1`/`_v2` | 0, 255 | T fixed extents → T request → S header → T extents/overlaps → S fields → T Data → rows → S | one record, success | Output refused | 255 | [9], [15] → C-01, C-03, C-04, C-05, C-10 |
| `wl_resource_run_ledger_check_v1` | 0, -1 | T guards → T all reads unconditional → S Check_Decision | one record, success | accepted | -1 | outside roster → C-01, C-03 |
| `wl_chain_authority_replay_v1` | 0, -1 | T guards → T anchors and allocation → S Well_Formed gates rows → rows → S | one record, success | unchecked | -1 | outside roster → C-01, C-05 |
| `wl_completion_decide_v1` | 0, 255 | T → T R → S header → T extents → S fields → T Data → five arrays, all unconditional → S | one record, success | Output refused | 255 | [22], [4], [23] → C-01, C-04, C-05, C-15 |
| `wl_completion_raw_decide_v1` | 0, 255 incl. post-decision | as decide, with per-row check → wire → confinement staging | one record, success | refused | 255 | [35], [36], [40], [48] → C-04, C-05, C-15 |
| `wl_completion_metadata_matches_v1` | 1, 0, 255 | marks → T → T R, X → S header → T extents → T arenas → rows → S join | none | arrays vs descriptor refused | Exception_Text; 255 | [36] → C-04, C-06 |
| `wl_finalization_decide_v1` | 0 (Reason 0/1/2), 255 | marks → T → T X → S header → T extents → S fields → T Data → plans → rows only if S Needs_Rows → S | one record, success | refused | Exception_Text; 255 | [43], [44] → C-01, C-05, C-16 |
| `wl_collapse_decide_finalization_v1` | `Decide_Wire` code or `Invalid_Request` | T collapse → S dependencies → per source S kind → nested entry → S readiness → agent → joins → S decision → metadata | none | read-only | Exception_Text; `Invalid_Request` | [43] → C-11 |
| `wl_native_diagnostic_control_v1` | 0, 1, 2 | no memory | stderr lines; SPARK atomics | n/a | none | [6] → C-06 |

**Provider closures.**
- `libworldline_core`: all movers; `Library_Interface` unchanged; D-15.
- `libevaluation_pending`: D-13.
- The protected resource service: N-06.
- Protected recovery capture (`protected_recovery_capture.py:166-172`): D-15.
- The epoch-correspondence tests that link the component: retained.

**Ignored fields stay ignored:** absent optional payloads in policy, ledger and history; absent recovery markers; absent lifecycle request fields; a zero-length v3 arena pointer; unneeded mixed-entry sources. Completion's unused arrays are validated, not ignored.

---

## 13. R4: alternatives and precedent (closed at design level by the review; restated)

No evidenced route that is SPARK-legal and fully proved reads arbitrary caller memory with the unchanged ABI and no added assumption:
- Address-to-access conversions in SPARK draw validity and no-alias assumption warnings. These units carry 88 `[address-to-access-conversion]` warnings (observed; JACKAL exact sum `30+11+4+4+6+3+5+2+3+1+2+3+9+4+1` = 88), including through the installed `System.Address_To_Access_Conversions` intrinsic (`G/libexec/spark/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude/s-atacco.ads:45-74`).
- Overlays are imprecise.
- Imported trampolines and Off bodies are forbidden.

The owner-transition and owner-audit precedent is a source precedent. Its checks are body-wide substring and exact-declaration checks (`proof_manifest.py:956-964`, `:975-994`), and its Off code makes scalar value decisions. This design is stricter, and its own checks (§8) are stronger.

These are evidence-limited statements, not impossibility theorems, and they grant nothing.

---

## 14. R5: OB-048 and the boundary surface (updated for RC1)

OB-048 (`H/ALL-ORIGINAL-OBLIGATIONS.md:947-961`) targets a minimal unproved C surface. **This consolidation moves away from that target.** OB-048 stays OPEN for the whole enlarged and pre-existing surface, and no Phase One dependency is relabelled Phase 2.

**Per export, the following become (or stay) unproved boundary code:**
- the extent, null, alignment, length, overflow and overlap guards;
- every raw read and write;
- caller-count-sized allocations;
- handlers and their refusal mappings;
- the address arithmetic of projections;
- the call sequences ([P] plumbing).

**Changed from v2.** The diagnostic subsystem contributes only T1–T5 (§4.5): two stderr operations, one handler per transport procedure whose only action is a SPARK call, one `Exception_Information` call, and the interleaving. The two `Atomic` objects, every state transition, the control codes, the latch and the text composition are SPARK.

**Pre-existing surface, unchanged:** `Authority_Glue`'s Off value decisions (`core/worldline-c_api.adb:768-770`, `:783-819`, `:862-863`), owner transport (`:967-1160`), `wl_hash_file`/`wl_hash_bytes`.

**What no guard establishes:**
- Custody: live allocation, initialization, immutability during the call, producer authenticity.
- The immutability premises of re-read objects (the collapse request, the agent, the finalization header) remain OPEN (D-27).
- Whether a foreign fault becomes an Ada exception in a Python-created thread (D-23).

---

## 15. Controls (LD6)

**Retained, unchanged, OPEN until run on the integrated successor:**
- the complete 52-action ordinary roster (`H/ORIGINAL-ORDINARY-ROSTER.json`, observed 52 launches);
- the lifetime controls (`H/REQUIRED-LIFETIME-CONTROLS.json`);
- the additive controls outside the roster that must be carried explicitly: `test_recovery_protocol_typed_adapter.py`, `test_recovery_protocol_native.py`, `test_resource_run_ledger_v1.py`, `test_chain_authority_native.py`, `test_proof_manifest_shapes.py`, `test_owner_transitions.py`, `test_owner_retry_audit.py`, `protocol-adapter-tests`, `chain-bounds-tests`, `resource-ledger-correspondence-tests`, `resources-prefix-correspondence-tests`, `decision-correspondence-tests`, `wire-initialization-tests`, `finalization-value-controls`, `explicit-recovery-marker-tests`;
- roster [30] `proof-source-tests`, with the unchanged source inventory.

**Additive controls.** New files only; no existing test is edited. They are unwritten and unrun, and admission is in a separately reviewed frame.

| ID | Control | Scope |
|---|---|---|
| C-01 | No-write on *defined* refusal paths only (§9.6), with outputs pre-filled `0xA5` | exports with outputs |
| C-02 | Typed-refusal zeroing (ledger) and mask writes (lifecycle) observable | U6, U7 |
| C-03 | One case per guard conjunct; export-specific overlap expectations (refused and accepted overlaps both kept) | all with pointers |
| C-04 | Malformed header/descriptor refusals; the raw `Operation /= 2` gate; the post-decision malformed-span 255 | U10–U15 |
| C-05 | Read gating with PROT_NONE pages in child processes; asserts normal exit and the expected code only | as §9.6 |
| C-06 | Diagnostics: control codes 0/1/2, double enable, stop-without-start latch, exact `WORLDLINE_NATIVE_DIAGNOSTIC` line sequences (fd 2 in a child) | U14, U15, control export |
| C-07 | Layout sentinels for unknown kinds/fields | staying layout exports |
| C-08 | Static symbol binding over the closure (G1–G8, K1–K4); the native part needs a built library | all |
| C-09 | Manifest mutation controls (§8.8) | all |
| C-10 | Component correspondence (behavioural complement to I3) | U10, U11 |
| C-11 | Mixed-entry coverage | U15 |
| C-12 | (Optional) exception mapping under `RLIMIT_AS`; never native-cost closure | pointer exports |
| C-13 | Layout identity: baseline (PK-0) and every PK-xR | all touched types |
| C-14 | **Proposed** behaviour only (D-36): no partial write on internal exceptions for local-then-write exports; review evidence, never baseline | v2, v3, chain, run ledger, pending, policy, ledger |
| C-15 | D-18: length-mismatched journal/history on Operation 1 gives History_Invalid written with return 0; exact Retain_Terminal and Already_Retained summaries | U14 |
| C-16 | Finalization Operations 0/1 with nonzero `Row_Count`: Rows never read; outcome identical to the original | U15 |

Optional Ada value-level controls may exercise value routines over small exhaustive domains against independent oracles. They replace nothing.

---

## 16. Operator decision items

The lead recommends; the operator decides. Nothing here is decided, approved or authorized by this document.

### 16.1 D-13: how `libevaluation_pending` keeps `wl_pending_decide_v1`/`_v2` after the mirror

| Option | What it is | Consequences | Evidence it needs |
|---|---|---|---|
| (i) **Recommended** | A component-local Off transport unit (for example `pending-component/core/evaluation_pending_transport.ads`/`.adb`) whose two functions are text-identical to the C_API pending transports (with component-local helper names), added to `pending.gpr` `Library_Interface`. The mirrored component specs/bodies equal the core files except for `SPARK_Mode`. | Relocates already-Off component transport, so the component's unproved surface is unchanged in kind. The ABI is preserved. Creates no new WORLDLINE exception and earns no proof credit. Changes the component install set (I3). | A concrete component source/project/link closure; both original Decide exports, with their profiles and layouts; real-library positive and refusal controls (roster [2] build, pending tests); exact mirror correspondence (C-10, K4); full source/library/header identity (I3 pins); the retained native-body obligations for the Off component |
| (ii) | Let the component stop exporting `Decide` | Narrows the component ABI against `PLAN.md:106` | Incompatible with current requirements (review D-13); not admissible |
| (iii) | Do not mirror | Abandons exact correspondence, contradicting LD3 and `PLAN.md:104-107` | Incompatible with current requirements; not admissible |

PK-7 cannot start without the operator's choice, and PK-S cannot occur without PK-7.

### 16.2 N-06: the protected resource service's library digest at deployment

Any change to `libworldline_core.so` breaks the digest pin of `protected-resource/run_service.py:117-120`.

| Option | What it is | Consequences | Evidence it needs |
|---|---|---|---|
| (a) **Recommended** | At the deployment gate, re-provision `native_sha256` under operator custody for the installed reviewed library | The service runs the consolidated code; refusal on mismatch is retained | The library actually installed and loaded, bound to the same source, proof and control identity; an operator-controlled provisioning record; the protected `native_sha256`; mismatch refusal demonstrated |
| (b) | Leave the old library running for the service as a deployment hold | The changed integrated candidate is **not** accepted for that service. The old library cannot count as the candidate, and identity diverges from the proved source until (a). | A recorded hold, with its scope and the outstanding obligation |

No deployment action is authorized here.

N-01 is not an operator item. It is a lead-owned strict obligation (§10). The operator reviews only a material ABI decision, and none is proposed.

---

## 17. Rulings and carried items

| Item | v3 disposition |
|---|---|
| D-01 … D-04, D-06 … D-12, D-14, D-17, D-20 … D-27, D-29 … D-33, D-35, D-37 | Carried from v2, unchanged in substance. Each stays OPEN where v2 said OPEN. They cover: guard placement; presence predicates; plumbing; no functional Posts; LD5; unit placement; layout; enrolment by unique names; layout facts; flow on `'Position` locals; the mirror; `wl_pending_decide_v1` kept; line sequence preserved; padding unspecified; `Authority_Glue` untouched; per-element acceptance; the foreign-fault limitation; one finalization path per row presence; `Captured` allocation kept; address-based self-calls; repeated reads and the double Seal; addresses as values; Kind-0/NULL behaviours kept; `Seal` mapping by its Post; re-mapped chain/protocol bindings; anchors-before-rows; run-ledger native cost OPEN; zeroing/mask controls. |
| D-05 | OPEN. **Decoder inventory with partial operations** (script, read-only): ledger `Decode` (adb:80); policy `Decode` (adb:95); history `Span`/`Epoch`/`Row` and their callers (adb:90-114); pending v1 `Convert` (adb:87-93); pending v2 `Convert` (adb:98-110); completion `Convert`/`Previous`/`H_Span` overloads (adb:288-375), `Convert_Optional` (adb:746-748) and `Optional` (adb:917-919); finalization `Convert` overloads (adb:73-111). **Decision procedure:** first, installed-tool evidence of contextual proof at every original caller; otherwise a separately reviewed total restructure; a helper-local Pre only through a separately reviewed non-narrowing proposal. No transport-facing Pre and no assumption. |
| D-13 | Operator item §16.1 |
| D-15, D-34, D-38 | OPEN: matching native export/layout evidence and installed-tool legality. Marking-stage errors and old libraries give no coverage of the successor. |
| D-16 | Withdrawn with LD4; replaced by LD4-R (§4) |
| D-18 | §5.4; OPEN for proof |
| D-19 | §5.5; OPEN for strict evidence |
| D-28 | §5.6; native delta OPEN |
| D-36 | §11.4 and A-COST §C19; OPEN for every export listed |
| N-01 | §10; a strict obligation |
| N-02 | Enforced by G7 |
| N-03 | OPEN. `STRICT` (diagnostic only, observed) lists NOT_FULLY_PROVED=14 and PROVED_ROW=521 required names, Total row `[7037, 1516 (22%), 5503 (78%), ., 18 (0%)]`, and 15 skipped units. The existing callees used by value routines need full matching-source strict proof: `Worldline.Resources.Can_Reserve`, `Resource_Ledger.Compute`, `Evaluation_Finalization.Seal`, `Worldline.Chain_Authority.Replay` and `Resource_Run_Ledger_Wire.Decode_Native`. No PROVED_ROW transfers. |
| N-04 | `Evaluation_Completion_Roster.Classify` appended (position 68). Unit-wide body coverage is already required. |
| N-05 | Resolved by reading; assertion retained; OPEN. **Import route:** `tests/test_authority_static_audit.py:268-280` loads `ROOT / "verify_proof_manifest.py"` through `importlib`. `verify_proof_manifest.py:22-44` puts `runtime/` on the path and re-exports `CONTRACT_PINS` from `runtime/worldline/proof_manifest.py`. So `test_the_pinned_set_is_exactly_the_claimed_contracts` (`:314-321`) compares the full effective pin set (169 keys in S5, observed by AST) with a 15-key set. By static inference (not executed), it cannot pass on S4 or S5 as written. The test is not in the 52-action roster (observed). **Status:** this is a pre-existing control/manifest inconsistency that this design neither creates nor edits; the design's added pin keys widen the gap. The test's meaningful property, that the claimed contracts are pinned, is retained. Any change to its expected contract needs its own reviewed decision. |
| N-06 | Operator item §16.2 |
| N-07 (new) | `Evaluation_Pending.Decide` and `Evaluation_Pending_V2.Decide` are called by the pending value routines and are not in REQUIRED_PROVED (observed). They are appended as positions 93 and 98, by the same reasoning as N-04. |
| R2_NINE_CONDITIONS | §8 maps the nine conditions: (1) the relocation map, §6 and A-BIND; (2) one binding, G1–G8 and K1–K4; (3) an identical C profile, P1–P3; (4) an executable decision path, O1–O7 and D1–D5; (5) predecessors, PP1–PP3; (6) complete pins, §8.7; (7) append-only, §9.3; (8) the exact exception set: the boundary is unchanged, no core unit is newly Off, and all units are On; (9) full evidence identity and strictness: the unchanged command and floor; zero unproved, justified and `pragma Assume`; complete reports; source and library identities. |
| APPENDIX_C | Appendix C v3 |
| PACKET_PLAN | §9 |

---

## 18. Everything that remains OPEN

- **Source and installed legality.**
  - No successor source exists.
  - Installed-tool SPARK legality of every changed unit (D-38), of the external abstract state, and of the `'Image` use.
  - Name-resolution conflicts in the integrated C_API body (A-BIND §B0).
- **Proof.**
  - Flow, RTE, termination and functional obligations of the 95 new routines and of every called relation, including the N-03 callees, the D-05 decoders, the D-18 index and the D-19 branches.
  - Zero unproved, zero justified, zero `pragma Assume`; floor 251; complete reports and per-unit coverage.
  - Every strict warning class, including N-01.
- **Manifest and composition.**
  - The override, tables and edits are unwritten; the O6 (b)/(c) renames/use inventory check is not yet specified as code.
  - Pins are not regenerated, mutation controls are unrun, and every stage review is pending.
- **ABI and native.**
  - Symbol export and mapping (D-15) and layouts (D-34, N-01 evidence).
  - Calling conventions and write construction (D-36).
  - Every cost in A-COST, including its §C21 evidence list.
  - The original native blockers (§11.5).
- **Controls.** The 52-action roster, the lifetime controls, all additive controls (C-01…C-16), and the provider and fault campaigns on the exact integrated candidate.
- **Boundary.** OB-048, custody, producer authenticity, immutability premises, foreign faults (D-23).
- **Operator.** D-13 before PK-7; N-06 at deployment; all original Phase One operator gates.
- **Reviews.** The independent actual gpt-6.1-sol review of this design, of every packet and stage, and of the final composition.

---

## Appendix A. Counts, JACKAL results and how each was obtained

**JACKAL calls.**
- Every call was the MCP tool `jackal_exact`.
- Each returned `status=exact`, `formal=false`, lane `rat`, assurance "exact rational arithmetic (not yet checker-covered)", evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`.
- Each carries these non_claims, verbatim:
  - "NOT formal-bounded: this lane carries no Lean-checked certificate"
  - "The epistemic class above is the STRONGEST claim this result supports"
  - "exact rational arithmetic (not yet checker-covered)"
- Every derived number in this design and its appendices was routed through JACKAL again on 2026-10-04, after a context compaction, and each value was unchanged.
- No consequence ceiling stronger than informational about code correctness was declared, and none is claimed.

| Quantity | Value | Method |
|---|---|---|
| Inventory exports across the 15 specs | 60 | observed per spec; JACKAL `parsed=10+4+5+5+3+3+4+3+3+2+3+4+5+4+2` → `exact=60` |
| Moving exports | 20 | by stage; JACKAL `parsed=2+3+4+1+2+6+2` → `exact=20` |
| Staying exports | 40 | JACKAL `parsed=60-20` → `exact=40` |
| Cumulative movers after PK-1/2/3/4/5/6b/7 | 2, 5, 9, 10, 12, 18, 20 | JACKAL `2+3`→5, `2+3+4`→9, `2+3+4+1`→10, `2+3+4+1+2`→12, `2+3+4+1+2+6`→18 |
| C_API `External_Name` count per stage | 31 (observed) → 33, 36, 40, 41, 43, 49, 51 | JACKAL `31+2`→33, `31+2+3`→36, `31+2+3+4`→40, `31+2+3+4+1`→41, `31+2+3+4+1+2`→43, `31+2+3+4+1+2+6`→49, `31+20`→51 |
| Core closure exports | 91 | observed (script: 91 `Export`, 91 `External_Name =>`, 91 `"wl_…"` literals, 0 `Import` over 137 Ada files); JACKAL `parsed=60+31` → `exact=91` |
| New routine names; existing relations enrolled | 95; 3 | script over the Appendix C list (no collision with existing names in the units or with REQUIRED_PROVED); JACKAL `parsed=95+3` → `exact=98` |
| U14 names; U15 names | 37; 20 | JACKAL `24+12+1`→37; `19-1+2`→20 |
| Appended per packet | 6, 2, 14, 6, 3, 57, 10 | JACKAL `7+4+3`→14, `37+20`→57, `5+5`→10 (6, 2, 6 and 3 are list counts) |
| Total appended | 98 | JACKAL `parsed=2+4+1+1+7+4+3+6+1+2+37+20+5+5` → `exact=98` |
| REQUIRED_PROVED length after PK-1/2/3/4/5/6a/7 | 541, 543, 557, 563, 566, 623, 633 | JACKAL `535+2+4`→541, `535+2+4+1+1`→543, `…+7+4+3`→557, `…+6`→563, `…+1+2`→566, `…+37+20`→623, `…+5+5`→633; also `535+98`→633 |
| REQUIRED_PROVED today | 535 (535 distinct) | observed by `ast` over the S5 manifest |
| CONTRACT_PINS keys in S5 | 169 | observed by `ast` |
| Pin keys after PK-7 under D-13 (i); with the optional pending pins | 176; 178 | JACKAL `169+4+2+1`→176; `169+4+2+1+2`→178 |
| `Well_Formed (Raw)` evaluations per accepted v2/v3 call (A-COST §C5–§C6) | original rel 1, chk 2; successor rel 2, chk 3 | counted by reading the call sites; JACKAL `parsed=1+1` → `exact=2`; `parsed=1+1+1` → `exact=3` |
| Representation warnings by attribute | Position 477, Alignment 129, Object_Size 88, Size 42 | observed (MAP); JACKAL `477+129+88+42` → `exact=736` |
| Representation warnings per unit (completion, finalization, pending v1, pending v2, run ledger, chain, history, v2, v3, recovery, protocol, lifecycle, ledger, policy, resources) | 205, 79, 41, 48, 99, 27, 36, 61, 64, 0, 11, 5, 27, 33, 0 | observed (MAP); JACKAL sum → `exact=736` |
| Staying / moving split | 617 / 119 | script line-range split (ranges below); JACKAL `154+67+38+45+90+21+32+57+60+7+4+15+27`→617, `51+12+3+3+9+6+4+4+4+4+1+12+6`→119, `617+119`→736 |
| Console error entries per unit (same order) | 600, 255, 66, 70, 11, 11, 34, 7, 8, 1, 6, 13, 34, 41, 1 | observed (MAP); JACKAL sum → `exact=1158` |
| Address-to-access warnings per unit (same order) | 30, 11, 4, 4, 6, 3, 5, 2, 3, 1, 2, 3, 9, 4, 1 | observed (MAP); JACKAL sum → `exact=88` |
| Diagnostic sites | Context_Matches 13 (6/6/1), Metadata_Matches 9 (6/2/1), finalization Decide 9 (4/4/1), Final_Context_Matches 7 (4/2/1), Decide_Mixed 16 (11/4/1), Diagnostic_Control 2 Marks | observed (script over S5; A-BIND §B6) |
| Ordinary roster launches | 52 | observed (`literal_launches_count_observed`) |
| Burn-down ledger | total 3187: OPEN 3028, DRAFTED 159, later states 0 | observed (`ledger.py report`) |

**Staying version/layout line ranges used for the 617/119 split** (body files):

| Unit | Ranges |
|---|---|
| completion | 90-257, 695-731, 871-891 |
| finalization | 34, 511-567 |
| pending v1 | 17-64 |
| pending v2 | 19-75 |
| history | 23-65 |
| run ledger | 24, 34-184 |
| chain | 19-59 |
| v2 | 18-114 |
| v3 | 24-123 |
| protocol | 16-39 |
| lifecycle | 20-31 |
| ledger | 26-62 |
| policy | 24-76 |
| recovery | 16 |
| resources | 16 |

## Appendix B. Bound inputs (sha256, read during drafting)

```
554fe8b08577fd74a5ca5ece30e6674c605c7a46bd35c97ae3f5c699a9a705d3  work/claude-capi-boundary-design-v2/DESIGN.md
db403247b328df70573600653e4eec40007473be0f164cfb15f3748bfcbf159d  work/claude-capi-boundary-design-v2/decisions.json
485e52888cba7b133acc0d72f1c058629b8306cf274390aab6ba72c8320ca95d  work/claude-capi-boundary-design-v2/review/gpt61-v1/REVIEW.md
42b762d94d53fe84a38cfa08d190b1e65d4b5f023f52980f78446b771a29e2ff  work/claude-capi-boundary-design-v2/review/gpt61-v1/review.json
eb1e7b0dd08abfa2f3be887fc4ba3bc19d857d915c1881a14603dec67d06a28a  work/claude-capi-boundary-design-v2/review/gpt61-v1/checks.json
d4d43694658c428070e46ca0ab56bf121eca61ac2dfc7675b3d48f369b281652  work/claude-capi-boundary-design-v2/review/gpt61-v1/review-freeze.json
2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237  outputs/claude-phase1-handoff-20261004/HANDOFF.md
004c71a8da3cb4e917812af427a1701bde226a18da615bcdbf483414d75f187e  outputs/claude-phase1-handoff-20261004/START-CLAUDE.txt
4a4cd1b3f605f4f078e15be6ffd75b71dbd80b2420491de80221d42f1a23c41e  outputs/claude-phase1-handoff-20261004/ORIGINAL-ORDINARY-ROSTER.json
9c836b3e42158c0e71629fda69f3e07e863abf2cd959678075e780c229b178a9  outputs/claude-phase1-handoff-20261004/REQUIRED-LIFETIME-CONTROLS.json
16d28b04bf937ecc7003a0a4fcf1b62d78b1478cb79542d9341022acc5f95acb  outputs/claude-phase1-handoff-20261004/ALL-ORIGINAL-OBLIGATIONS.md
1b228f4b07209c91c8f8770851906a8ebbf90db12f0af605954aff392946b327  /home/sicarii/Documents/complete-phase1-prompt.txt
1587b41b87d95dde1a76d80cd0b7922fce751948680ce8448160cb051465e59e  work/claude-lead-v2/executions/f10k-retry1/diagnostic-map-v1.json
b53c2c180727c54034b18e03251158bb70d34f13d35740df72d2446bedc61e3f  work/claude-lead-v2/executions/f10k-retry1/strict-report-analysis-v1.json
172b51fee23e76ebc2e3d0b7126802160b4e9b6aa1377a822195a3571f0a608c  work/claude-workflow-v1/ledger.json
ee186ab25ed9c05c54a9d433bc9f1cef2b1f85a4f750d7e6b9e1b2e432ec7549  work/claude-workflow-v1/compose.py
05a99c06accad5a0eb717e6ca4195625c4ccbf9081e6dc471aa3c6ad16f27ec9  work/claude-workflow-v1/REPAIR-MAP.md
a0e0bb5cbca667ad8e02eff9ea79c80459f4066544542178362257dbe347fa3e  work/claude-composition-v5-beta/composition.json
49a344a48f796295735f9161abc0be39e6493d8c9f32d0a7e8376365a67784bb  work/claude-composition-v5-beta/source-binding.json
3407119bdf9e8497ed8259d76ea783f6d207f15fd155ee9c45534c3b0eaf937a  work/claude-composition-v5-beta/source-inventory.json
df6cbc9dd0791232a3ac169908237798909955abe3d896a328ccf3bc55843476  work/claude-composition-v5-beta/review/gpt61-v1/review.json
a5cc89bbe21c80796f74a236f0c053da7ca94ec82efbf4a9924f8e489b798ebe  work/claude-composition-v5-beta/review/gpt61-v1/REVIEW.md
79d9f875bdcd17d8c2bb8add0155d15235a045706ecdb7bf60e946697ae62a40  work/claude-lead-v2/approvals/optional-marker-api-v1/approval.json
943ea95ec98bd770ae9dd22ff1ea85bbf932db3192f6ba07f120284c1122e3bf  work/reviewed-common-proof-source-composition-v4/source-inventory.json
dad210ac27bbe6bf78a6c127528607ba432a4307491457f69f54f9749ffd5b82  work/integrated-proof-preparation/PLAN.md
ab9555faadd4b46d294a09d8d74495b75ef017497acde9290849cf005aed921a  S4 core/worldline-recovery.ads
6eb37dc6e7d2bcf9dd320edf682c3cffde8cb4a00b8f3fb5e55984189c8dfb01  S4 core/evaluation_finalization.ads
d9f144be28256acd91e80918f6099eb0923d9e812df0b950454e8facb015c36d  S4 core/evaluation_finalization.adb
8ae6c3c14b835af3825acca806649b11daeb839b45a6506a5fbd29732bbfcd23  S4 runtime/worldline/proof_manifest.py
3a3b17c47bb289e24adc3009e0a5a7510972fac07323f636cbd5722e6344319a  S5 core/worldline-c_api.ads
0a17c0efb95904ee865182a20d3bcabceeef93b1cc3639687aab27696339f35b  S5 core/worldline-c_api.adb
5cb92b4cf731de16954c05af89274e120ed2c13e56d3a9d06ef16c976afc7eb5  S5 core/worldline-resources_c_api.ads
f31c2dd39a50f9bf02cd345b2617b41ab4a2b02bc0947a8b4f23c917c2be50cb  S5 core/worldline-resources_c_api.adb
aec1866769caf987b60ca822b04387d49b5ac181579e163d8e901ded3a6e6c59  S5 core/worldline-recovery_c_api.ads
120c6c488284f5af09efc7abbdba0831a72b7cb3222fa1c8b543ef3bad3636a9  S5 core/worldline-recovery_c_api.adb
9e2e0dde6408d1cdd6666d7f5833cd472d66eb4b6cf3a3c5b6da17d7c303cd5d  S5 core/worldline-recovery_authorization_c_api.ads
60309a05b5b6ec468dc46625b433c7e0ba953717ab806993a7f9ce429e21501a  S5 core/worldline-recovery_authorization_c_api.adb
ab62cd25cb96661435a0dea612efddf574844bb4064ab3cc25ff8d1c1e29c51d  S5 core/worldline-recovery_authorization_v3_c_api.ads
7c82035c13f36b289e1c02ca5d0ced5d79674870e7fc8daced3d0547388d929d  S5 core/worldline-recovery_authorization_v3_c_api.adb
b1a980f5785b0456f7b1449e0bc058c04bfa0b5bf09beeb63978f25613b22228  S5 core/worldline-recovery_protocol_c_api.ads
01b256d06f0e0b7148c3685b8dbed945a4e25a1f45ee69f4cd8030536dc5dcf5  S5 core/worldline-recovery_protocol_c_api.adb
a465fd5c1659e0dcd1f66d15b223c31e2ff022f9f1224f5f2e50f1d2979c6c60  S5 core/worldline-reservation_lifecycle_c_api.ads
9d235d2f84ff73b8408e3187c4f78c1826af2b2b63fd8ff229e8672041fa8934  S5 core/worldline-reservation_lifecycle_c_api.adb
c3a52b1e8a2a7bbcdaee4a219e965f9bd4beb69a79b30b16efc0f9fdda1795ab  S5 core/worldline-resource_ledger_c_api.ads
112a8ef5321240f9d13fe3135dce1b6085d6fecda1590a553f30b4dc4bf1247a  S5 core/worldline-resource_ledger_c_api.adb
24929690c6e983a054f212e4192b6d4a39da2129e9321e4786ace16d8260448c  S5 core/worldline-resource_policy_c_api.ads
794d9a4c16a0bbdd9a95da51cd762f190778aeae66ac07c000f1972eda6f5b04  S5 core/worldline-resource_policy_c_api.adb
c38738bbbfb544d019e13c57923e5778663e8244fdee8f921b602c5e26758344  S5 core/worldline-evaluation_history_c_api.ads
d58a26e0b9fcd774921d00740449569824377b4bca6a40d4036aa1e5fce90e5e  S5 core/worldline-evaluation_history_c_api.adb
6bd1472201c595be3f53b8a4ce4a73fde9bef9fb41576c9f246be6480ca0a897  S5 core/evaluation_pending_c.ads
56500a7c614a5a6ac4d74107226538bd84b152730265b89703bebabf5e3e3f15  S5 core/evaluation_pending_c.adb
10f7505c97d34a022ad51784fbad2ec9c4615992bb4fa0e08762f2f34accf350  S5 core/evaluation_pending_v2_c.ads
84409e222fe43cba4b3dc8edbfe42279904bd164e68950b6ef6ae717d8ee17fc  S5 core/evaluation_pending_v2_c.adb
ece3bc0eb7f332438be9938fd84b4b4e0ccc091ae8e2b7a5db5a0342118a4751  S5 core/resource_run_ledger_c_api.ads
fbc97b4c17ee0a0a17e74bae669fa11e674bb234ce5cd8f73d374b7d7e114581  S5 core/resource_run_ledger_c_api.adb
03d00cb9172e919507ba74b47fe8fa0431dce7fce062bc3ab409df1c8946d9f3  S5 core/worldline-chain_authority_c_api.ads
dae2748bdb87c55b90ed73bd82fe882d5d4c64ca3af944f463dd4798ca66328a  S5 core/worldline-chain_authority_c_api.adb
e0a50887d10159aa8350734ed2acc88b8a454fbfeb0eea7d0c727ca28ac17dd7  S5 core/evaluation_completion_c.ads
b799e93af37ca90104050473119aaca380b54244a491c2cc57226db8eaa77d69  S5 core/evaluation_completion_c.adb
2ca8602e87eb4605ddeda8e61c223ff39d765a81d3e22baec3e7d981bb74010b  S5 core/evaluation_finalization_c.ads
bdcf333878aebe4aca55333bc3b9a9a50007c187fc4b380dec1adb18127f83d3  S5 core/evaluation_finalization_c.adb
2b2a87a7a1f554486caad6c680e2c39dd4bb7b5e48619933f033cda15ea0a2f5  S5 core/evaluation_completion.ads
e20808c44b84e02485e10a3eb1e1e36a2f2f88defd75eb97c536cee6851c287a  S5 core/evaluation_finalization.ads
c64f17246f0dfa3d88299a534e3e716ada35fd05120983a3d8f53a7c28d1a738  S5 core/evaluation_finalization.adb
09f82299af37c975b409596fb342f1ef961e309354765cde966189f23a2ee3fe  S5 core/worldline-recovery.ads
29ea441b1bcc0212db70143c09b961b1f911827c8f30b40cc52f88080f4c222b  S5 core/worldline-evaluation_authority.ads
f290ca5e5b39d351359227115081ab3fe09c9976a0e5de6a844a48b394742946  S5 core/resource_ledger.ads
8750cacbebb849baba47f8319e179cab78dfefac7bee10760f96fa2e0dcf861e  S5 core/evaluation_pending.ads
2faea7935397bebf07a330b7d64c457716c40d8613076696f62359c5723fb48a  S5 core/evaluation_pending_v2.ads
bc086393ebdf98d397273905aa3425afe4b7cc29cbc9ac9ac1ac1a7f499d8111  S5 core/evaluation_completion_roster.ads
5497fabb698d53efc2bfb39104bdcd48b1c0f46e0c706c2643c8ce1af72fd5b0  S5 core/worldline_core.gpr
701931bc94f17aae8a14268cf7051f9a6d7b5bf8c7a1e0adccb9be0f5c0dff3c  S5 core/worldline_core_sources.gpr
d8f1a3ef831c1186eb99e0b729a89f7f379a81e04f2f2bbd7f68f06add739b5e  S5 pending-component/pending.gpr
963488e96bdc4faa56a9659de557731d9a7e78ad660afd359e18350f44fb164d  S5 pending-component/core/evaluation_pending_c.ads
9b0bc60e3144ad2a2dfbd1361a4e8e8c608164cb9bb0f067df724043dbf559ff  S5 pending-component/core/evaluation_pending_c.adb
155611e01d236e0f2a200245b453e49847f58aa01a68e4c8b3c8d902b898b4a8  S5 pending-component/core/evaluation_pending_v2_c.ads
b6df858e6a11e8c55ee0cff5cc4e46d90416629080000198d3c4e6d6de4cb240  S5 pending-component/core/evaluation_pending_v2_c.adb
51dd30d1a2c19cea4b9794e869400c5cb7c4193043f66678e62efa695b058fcb  S5 runtime/worldline/proof_manifest.py
9b5bcbae627fe755eada5ca7e1cd503144a87e89ebf5208af6d972b98df02a9f  S5 verify_proof_manifest.py
cea28ef16f4a12c8c5859741cbdd6c2e18cb8f27017e30bbd6cb4749e555359b  S5 tests/test_authority_static_audit.py
7c55efd017338f7fe68352479f7b9087cb4495bc9e64f7468260869e3738526e  S5 tests/revalidation_diagnostic.py
2ced279c28898b6d56e0cacb75cc7a64793a9c7dc710e1841954469464b7e267  G .../adainclude/a-textio.ads
61cac87bb1541705da0a2dbcf2d4afe7bb0e95215d41e2583b0c632dcb16444a  G .../adainclude/a-except.ads
23f10a63aab7541fb42e6acddd167d80555f7f2e619ebb31d738a5eaea7cb360  G .../adainclude/s-atacco.ads
3a5b4293192d2a8792ea61074be763a411466abdbd9937f07b5a0ead55b3c1b1  G .../adainclude/system.ads
4cd4a59fd1efdf92265ba1ae14a03916749c8676178ff59a9d9f5285cba8e315  G share/spark/explain_codes/E0004.md
e44a739556b9718cb9b8913d94d5d14dbc1e5a810c38c109e9ae5f0d88ba7f80  G share/spark/explain_codes/E0005.md
```

## Appendix C. REQUIRED_PROVED append, in packet order (98 names)

The names are appended after the last existing segment, one slice per packet (§9.3). The 535-name prefix is unchanged, and the final length is 633.

```
# PK-1
Worldline.Resources_C_API.Negative_Flag_Valid
Worldline.Resources_C_API.Can_Reserve_Value
Worldline.Recovery_C_API.Presence_Valid
Worldline.Recovery_C_API.Present
Worldline.Recovery_C_API.Marker_Of
Worldline.Recovery_C_API.Select_Value
# PK-2
Worldline.Recovery_Authorization_C_API.Decide_Total
Worldline.Recovery_Authorization_V3_C_API.Decide_Total
# PK-3
Worldline.Reservation_Lifecycle_C_API.Request_Valid
Worldline.Reservation_Lifecycle_C_API.Requested_Of
Worldline.Reservation_Lifecycle_C_API.Operation_Of
Worldline.Reservation_Lifecycle_C_API.Accept_Row
Worldline.Reservation_Lifecycle_C_API.Publishes_Mask
Worldline.Reservation_Lifecycle_C_API.Mask_Byte
Worldline.Reservation_Lifecycle_C_API.Status_Code
Worldline.Resource_Ledger_C_API.Accept_Row
Worldline.Resource_Ledger_C_API.Encode_Quantity
Worldline.Resource_Ledger_C_API.Result_Of
Worldline.Resource_Ledger_C_API.Accept_Headroom_Inputs
Worldline.Resource_Policy_C_API.Accept_Input
Worldline.Resource_Policy_C_API.Accept_Disk
Worldline.Resource_Policy_C_API.Encode_Decision
# PK-4
Worldline.Evaluation_History_C_API.Final_Flag_Valid
Worldline.Evaluation_History_C_API.Final_Row_Present
Worldline.Evaluation_History_C_API.Accept_Query
Worldline.Evaluation_History_C_API.Accept_Row
Worldline.Evaluation_History_C_API.Accept_Final_Row
Worldline.Evaluation_History_C_API.Select_Result
# PK-5
Resource_Run_Ledger_C_API.Check_Decision
Worldline.Chain_Authority_C_API.Accept_Row
Worldline.Chain_Authority_C_API.Replay_Value
# PK-6a
Evaluation_Completion_C.Decide_Header_Valid
Evaluation_Completion_C.Decide_Fields_Valid
Evaluation_Completion_C.Accept_Journal_Row
Evaluation_Completion_C.Accept_Captured_Row
Evaluation_Completion_C.Accept_Result_Row
Evaluation_Completion_C.Accept_History_Row
Evaluation_Completion_C.Accept_Required_Row
Evaluation_Completion_C.Decide_Value
Evaluation_Completion_C.Raw_Header_Valid
Evaluation_Completion_C.Raw_Fields_Valid
Evaluation_Completion_C.Accept_Raw_Check_Row
Evaluation_Completion_C.Accept_Raw_Measure
Evaluation_Completion_C.Raw_Decide_Value
Evaluation_Completion_C.Context_Header_Valid
Evaluation_Completion_C.Context_Fields_Valid
Evaluation_Completion_C.Context_Agent_Matches
Evaluation_Completion_C.Accept_Context_Fields
Evaluation_Completion_C.Accept_Context_Row
Evaluation_Completion_C.Accept_Required_Pair
Evaluation_Completion_C.Context_Join_Value
Evaluation_Completion_C.Join_Code
Evaluation_Completion_C.Metadata_Version_Valid
Evaluation_Completion_C.Metadata_Header_Valid
Evaluation_Completion_C.Accept_Metadata_Row
Evaluation_Completion_C.Diagnostic_Control_Of
Evaluation_Completion_C.Diagnostic_Invalid_Code
Evaluation_Completion_C.Diagnostic_Start
Evaluation_Completion_C.Diagnostic_Stop
Evaluation_Completion_C.Diagnostic_Observe
Evaluation_Completion_C.Diagnostic_Latch_Failure
Evaluation_Completion_C.Diagnostic_Begin_Line
Evaluation_Completion_C.Diagnostic_Line
Evaluation_Completion_C.Diagnostic_Begin_Value
Evaluation_Completion_C.Diagnostic_Value_Site
Evaluation_Completion_C.Diagnostic_Begin_Exception
Evaluation_Completion_C.Diagnostic_Exception_Site
Evaluation_Completion_Roster.Classify
Evaluation_Finalization_C.Request_Header_Valid
Evaluation_Finalization_C.Request_Fields_Valid
Evaluation_Finalization_C.Accept_Plan
Evaluation_Finalization_C.Needs_Rows
Evaluation_Finalization_C.Accept_Row
Evaluation_Finalization_C.Decide_No_Rows_Value
Evaluation_Finalization_C.Decide_Rows_Value
Evaluation_Finalization_C.Final_Seal_Ready
Evaluation_Finalization_C.Final_Plans_Valid
Evaluation_Finalization_C.Final_Projected_Row
Evaluation_Finalization_C.Final_Projection
Evaluation_Finalization_C.Kind_Of
Evaluation_Finalization_C.Ordinary_Readiness
Evaluation_Finalization_C.Finalized_Readiness
Evaluation_Finalization_C.Finalized_Operation_Readiness
Evaluation_Finalization_C.Agent_Readiness
Evaluation_Finalization_C.Context_Join_Needed
Evaluation_Finalization_C.Mixed_Collapse_Decision
Evaluation_Finalization_C.Mixed_Authorized
Evaluation_Finalization_C.Mixed_Metadata_Needed
# PK-7
Evaluation_Pending_C.Header_Valid
Evaluation_Pending_C.Request_Fields_Valid
Evaluation_Pending_C.Accept_Row
Evaluation_Pending_C.Decide_Value
Evaluation_Pending.Decide
Evaluation_Pending_V2_C.Header_Valid
Evaluation_Pending_V2_C.Request_Fields_Valid
Evaluation_Pending_V2_C.Accept_Row
Evaluation_Pending_V2_C.Decide_Value
Evaluation_Pending_V2.Decide
# count (script): 98
```

## Appendix D. Companion file identities

Each was written once with the Write tool to the location in the header, before this file. The identities are observed with `sha256sum` and `wc -c`.

| File | sha256 | Bytes |
|---|---|---|
| `APPENDIX-BINDINGS.md` | `5ffb8736b6ce89f655041129991ed0bce4133941129bc7b1566b0da68695d32e` | 94959 |
| `APPENDIX-COST-MAP.md` | `c2a320a266fdd088c203e0d61f4cd7c5ea94f7b3b731f5be400f6b2f3d5b114f` | 48792 |

`decisions.json` is written after this file and records this file's sha256. Its own identity is reported in the handoff.

*End of design v3. Nothing in this document is accepted. Every obligation listed in §18 remains OPEN.*
