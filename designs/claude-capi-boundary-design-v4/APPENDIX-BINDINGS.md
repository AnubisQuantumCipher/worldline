# C-API boundary consolidation v4: Appendix A-BIND (enforceable binding specification)

| | |
|---|---|
| Companion to | `DESIGN.md` in this directory (design v4). `§n` means a section of DESIGN.md. |
| Supersedes | v3 `APPENDIX-BINDINGS.md` (sha256 `5ffb8736b6ce89f655041129991ed0bce4133941129bc7b1566b0da68695d32e`, 94959 bytes). |
| Status | DRAFT_FOR_GPT61_REVIEW. **PROPOSAL ONLY.** No manifest code, table, source or control has been written, and none of the checks below has been run. Every obligation is OPEN. |
| Base | S5 = `W/work/claude-composition-v5-beta/source` (lineage L0, §9.1). Line citations are S5 lines; for the files cited they are identical to S4 (§0). |
| Normal form | N1 = the manifest's own `normalized_ada` (`runtime/worldline/proof_manifest.py:420-434`): `--` comments outside string literals removed, all layout collapsed to single spaces. N2 = the N1 text with every character strictly inside a double-quoted string literal replaced by `_` (same length, so positions coincide). Boundaries, parentheses, identifiers and clauses are found on N2; tiles, hashes and literal comparisons use N1. |
| Answers | V3-RC4 (complete and reconciled enforceable binding), the binding parts of R2_NINE_CONDITIONS, and the binding half of RC1 (diagnostic confinement, carried). |

Nothing in this appendix is evidence. A check that passes is a necessary guard. It is never proof of reachability, of faithful actuals beyond the bound text, of native behaviour, of custody or of correctness (§8.9).

**What changed from v3 (summary; detail in each section).**
- B0 is rewritten. v3's ordered-subsequence tokens (R-ORD), occurrence counts (R-MUL), blanket constant-result rule (R-W) and deferred qualification rule (R-Q) are replaced by exact tiles (R-TILE), transport residue and helper hashes (R-TRANS), a per-form write table (R-W, B10), an enforceable gate rule (R-GATE), an exact scoped clause inventory (R-INV, B9), an alias exclusion that makes O6 (a) enforceable (R-ALIAS), whole-file residual identity (R-RES, S-RES), placement (R-LAYOUT) and exact Authority_Glue edits (R-GLUE).
- B2.3 states K3 as actual `Library_Interface` membership (parsed list equality), with K5 and K6 added.
- B4 is rewritten unit by unit: every relocated export body and moved helper is given as exact N1 text segments.
- B8 is rewritten so that every rule above has a matching check function.
- B9 (scoped rename/use inventory), B10 (write forms), B11 (promise-to-check matrix) and B12 (mutation controls for the new checks) are new.
- B1, B2.1, B2.2, B3, B5, B6 and B7 are carried verbatim from v3, with v4 additions placed after each carried block and marked as such.

---

## B0. Rules shared by every table (REVISED in v4)

### B0.1 Isolation (R-ISO; revises v3 R-ISO)

- **Subprogram `N` in region `T`** (a file, or a package span): `end N;` occurs exactly once in the N2 view of `T`. The span runs from the nearest preceding `function N ` or `procedure N ` to the end of `end N;`.
- **Package specification `N`:** `package N is` occurs exactly once in the N2 view of the file. The span runs to the first `end N;` after it.
- **Package body `N`:** `package body N is` occurs exactly once. The span runs to the first `end N;` after it.
- **Declaration `D`** (access type, generic instance, expression function, constant, subtype) **in region `T`:** its start text (`type D is `, `function D is new `, `package D is new `, `function D (`, `D : constant `, `subtype D is `) occurs exactly once in `T`. The span ends at the first `;` at parenthesis depth 0 after the start, on N2.
- Any isolation failure is a problem. It is never a skip.

### B0.2 Exact tiles (R-TILE; replaces v3 R-ORD, R-MUL and O1–O3)

- A **tiled subprogram** is one of the 20 relocated export bodies, `Completion_Transport.Context_Matches`, `Completion_Transport.Metadata_Base` or `Finalization_Transport.Final_Context_Matches` (23 in total, JACKAL J19).
- Its isolated N1 text must equal `HEAD + " " + " ".join(SEGMENTS)` exactly.
  - For an export, `HEAD` is its B3 successor declaration with the suffix ` with Export, Convention => C, External_Name => "<symbol>";` replaced by ` is`.
  - For a moved helper, `HEAD` is the literal head given in B4.
  - `SEGMENTS` are the numbered segments of its B4 entry, in order.
- `Diagnostic_Transport`'s package specification and package body spans must equal the two literal texts of B4.24 exactly.
- **Consequence.** In these units the text fixes every declaration, read, guard, gate, decision call, write, return and handler, and their order and adjacency. The rule checks of B0.4–B0.7 are kept as **invariants**. They hold for the B4 text, and they are re-run on every successor so that a later reviewed amendment of B4 cannot weaken a rule while staying textually self-consistent.
- **Why tiling replaces ordered tokens.** The v3 review found that ordered occurrence alone does not enforce adjacency, provenance or exclusive assignment (V3-RC4). An exact tile does.

### B0.3 Transport packages (R-TRANS; new)

For each of the 15 unit transports `T` (B4; the 16th designed package, `Diagnostic_Transport`, is tiled):
- **Specification content is exactly:**
  - the clause block `CLAUSES[T]` (B9.2): one contiguous N1 string;
  - the subtype declarations `SUBTYPES[T]` (B4);
  - every helper of kind `type`, `fn_inst`, `pkg_inst` or `expr` listed in `HELPERS[T]` (B9.3);
  - for every helper of kind `body` and every moved subprogram, one declaration equal to its isolated body's profile (the text before the first ` is ` at parenthesis depth 0) followed by `;`;
  - the constants `CONSTANTS[T]` (only `Recovery_Transport.Empty`).

  Removing each of these exactly once from the specification span and collapsing whitespace must leave exactly `package T is end T;`.
- **Body content is exactly** the `body` helpers and the moved subprograms. Removing each exactly once must leave exactly `package body T is end T;`. So no elaboration statements and no other declaration can be added.
- **Verbatim helpers.** Each helper's isolated N1 text has the sha256 listed in B9.3, which is the sha256 of the same helper's isolated N1 text in the S5 unit body (observed by a read-only script, 116 helpers).
- Moved subprograms are tiled (R-TILE).

### B0.4 Clause inventory (R-INV; replaces v3 O6 (b) and (c))

- **Scopes.** Each designed package specification span, package body span and tiled subprogram span is a scope. Nested subprograms (`Read_Ready`, `Context_Joined`, the three `Diagnostic_Transport` procedures) belong to their enclosing scope. Text before `package body Worldline.C_API` is the scope CONTEXT. All remaining text of the body is RESIDUAL.
- **Clauses.** On N2, a clause is any match of `package <id> renames <name>;`, `use all type <names>;`, `use type <names>;` or `use <names>;`. Each clause is assigned to the innermost scope that contains it.
  - The `use <names>;` pattern would also match the tail of a representation clause such as `for T'Size use 32;`. There is none in the S5 C_API pair (read-only check: the pattern finds exactly the 36 B9.1 clauses) and none in the designed text.
  - So a representation clause added later would be refused as an unlisted clause. That is conservative, and it is intended.
- **Requirements:**
  - (i) For each designed scope, the ordered tuple of its clause texts (N1) equals `INVENTORY[scope]` (B9.2) exactly.
  - (ii) The RESIDUAL tuple equals the observed S5 tuple of B9.1, with deletion R-DEL-1 applied from PK-6b.
  - (iii) CONTEXT contains no clause.
  - (iv) `core/worldline-c_api.ads` contains no clause. S5 has none (observed).
  - (v) In every scope, the number of occurrences of the word `renames` equals the number of package renamings listed for it. So subprogram, object and exception renamings are refused.
  - (vi) `use all type` occurs nowhere in the C_API pair.
  - (vii) No `use` clause (other than `use type`) names a unit of `CAPI_SPARK_UNITS` (B9.4) or a package renaming of one. A `use type` naming a type of such a unit occurs only where B9.2 lists it.
- **What this replaces.**
  - v3's (b) covered renamings only, and v3 deferred its check (DESIGN v3 §8.4 O6).
  - v3's (c) allowed exactly one non-`use type` clause per export body. That was unsatisfiable together with v3's own B4 tokens: they use `To_Integer`, `Storage_Offset` and address `+` directly, and these need `use System.Storage_Elements;` or re-export declarations that v3 never specified.
  - v4 replaces both with exact per-scope tuples (DESIGN §8.4 explains why this is not a silent generalization).

### B0.5 Alias exclusion (R-ALIAS; makes O6 (a) enforceable)

- `CAPI_ALIAS_FORBIDDEN` (B9.4) lists `(X, N)` pairs.
  - `X` is a package renaming that occurs in a designed or residual scope and whose target is, directly or through the renamings it is defined by, a unit owning Appendix C routines.
  - `N` is the simple name of such a routine, or of a routine that PK-6b removes from `Evaluation_Completion_C`.
- For every pair, the case-insensitive N2 pattern `(?<![\w.])X\s*\.\s*N(?!\w)` occurs zero times in the C_API body.
- **Why this makes O6 (a) enforceable.** R-INV (vi)–(vii) gives no use-visibility of any SPARK unit's subprograms, since `use type` exposes only operators (RM 8.4) and no listed clause names such a unit. R-INV (v) gives no subprogram renamings. R-ALIAS gives no selection through a renaming alias. So the only way left to denote an Appendix C routine in the C_API body is its full expanded name, which O6 (a) requires.

### B0.6 Write forms (R-W; replaces v3 O4 and R-W)

- Every foreign-memory write in a designed scope is an occurrence of `.all :=` or of a call `Write_Data (`, on N2. The helper's own declaration `procedure Write_Data (` is not a call. Each must be matched by exactly one row of `CAPI_WRITES` (B10), and each row's target text occurs exactly once in its scope.
- The check runs over **every** designed scope (each transport specification and body, and each tiled subprogram), so a scope without rows must contain no foreign write.
- Each row names a form, its spans and its closed identifiers:
  - Each **span** is an exact N1 substring that occurs exactly once in the scope.
  - Every case-insensitive occurrence of a **closed identifier** in the scope lies inside one of the row's span occurrences.
  - A closed identifier is never the target of an assignment, except where the row lists its assignments explicitly (form WF-X).
- The forms are WF-C, WF-A, WF-F, WF-O, WF-R, WF-P, WF-X, WF-B and WF-H (B10.1). Together they cover:
  - direct SPARK function-result stores;
  - mutable procedure-out buffers and the lifecycle mask;
  - completion `Response`;
  - finalization's two exclusive assignments;
  - the unchanged protocol pattern;
  - the one transport helper that writes.
- v3's single rule ("a constant result object, except finalization `O` and completion `Response`") contradicted its own B4 (ledger, policy, lifecycle and protocol rows; V3-RC4). It is withdrawn, not generalized: every form is stated and checked.

### B0.7 Gates (R-GATE; makes v3 A1 / R-G enforceable)

For every acceptance object `N` listed in `CAPI_GATES` (B10.3):
- its gate string occurs exactly once in the scope. The gate string is the exact N1 text from the start of `N`'s declaration through the end of its discriminant test and the original refusal statement, so it contains nothing else between them;
- every occurrence of `N.Ok` or `N.Verdict` lies inside the gate string;
- every other selection `N.<component>` begins after the end of the gate string;
- `N` is never an assignment target.

For `case N.Verdict is` gates, the gate string ends at `case N.Verdict is`, and the tile fixes the alternatives.

**Completeness.** Every `X.Ok` selection and every `case X.Verdict is` in a designed scope (attributed to its innermost scope) must belong to an object with a gate row in that scope. So an acceptance object cannot be added without its gate.

### B0.8 Residual identity, layout and glue edits (R-RES, S-RES, R-LAYOUT, R-GLUE; new)

- **R-RES.** Take the N1 body of `core/worldline-c_api.adb` from `package body Worldline.C_API with SPARK_Mode => Off is` to its end. Remove every designed package span and every relocated export body span. Apply the inverse of every recorded Authority_Glue edit (B4.23; from PK-6b). Collapse whitespace. The sha256 must equal `187242f4aaaddd7eaecc996659b305c1fd2329e419a090c3b1d4c55dcc08669e`, the observed S5 value of the same text. So the pre-existing code is unchanged apart from the recorded edits.
- **S-RES.** Take the N1 text of `core/worldline-c_api.ads`. Remove the four C_API subtype declarations and every relocated declaration. Collapse whitespace. The sha256 must equal `4c533f63b629146beea81b20c7bddcae385beafb61ffc62cc866212f6d5c4c6b` (observed S5).
- **R-LAYOUT (body).**
  - The designed packages form one contiguous run, in `CAPI_LAYOUT_PACKAGES` order (B4.0). The run begins immediately after `end Layout_Offset;` and ends immediately before `package body Authority_Glue is`.
  - The relocated export bodies form one contiguous run, in `CAPI_LAYOUT_EXPORTS` order. The run begins immediately after `end Owner_Audit_Decide;` and ends immediately before the final `end Worldline.C_API;`.
  - "Immediately" means that only one space separates them in N1.
- **R-LAYOUT (spec).** The four subtypes, then the relocated declarations in `CAPI_LAYOUT_EXPORTS` order, begin immediately after `External_Name => "wl_owner_audit_decide_v1";` and end immediately before the final `end Worldline.C_API;`.
- **R-GLUE.** Each of the nine recorded edits GE1–GE9 (B4.23; JACKAL J16: 8 retargeted call sites, JACKAL J17, plus deletion R-DEL-1) has its new text occurring exactly once in its function's isolated text. Undoing them reproduces that function's S5 text exactly:
  - `Decide_Raw_Context`: sha256 `56dc5c697554b1cc2efaa759b55999447d9676be6649df1e6c64b615fd6c6a99`;
  - `Decide_Raw_Metadata`: sha256 `99a1343621bec0a24433d797974f002ba9bbd61cabd8b49e72bbbe4daf26fbfa`.

  R-RES implies R-GLUE. The separate check names the exact edit that failed.

### B0.9 Carried rules and remaining notes

- Carried unchanged from v3:
  - G1–G8 (closure symbols, alternate bindings, projects, old-home absence, raw constructs, Text_IO/Exceptions);
  - K1, K2, K4;
  - P1–P3;
  - D1–D5;
  - PP1–PP3;
  - E1–E4.
- Revised: K3. New: K5, K6, G9, G10 (B2.3, DESIGN §8.2).
- **Spacing (carried).**
  - Tiles assume the GNAT layout these files already use: a space before each opening parenthesis of a call, aggregate or index, spaces around `=>` and `:=`, and no space before `;`.
  - A successor that is laid out differently fails the check. That outcome is intended, and the remedy is reformatting, not a weaker table.
- **Name resolution (carried, made explicit).** Use-visibility and overload resolution in the integrated C_API body cannot be confirmed until source exists and the installed compiler accepts it (D-38). That stays OPEN. Building the B4 text surfaced two operator-visibility gaps in v3's tokens:
  - `Status /= 0` on `Interfaces.C.int` in the two completion exports;
  - `V = …Join_Malformed` on `Join_Verdict` in `Context_Matches`.

  v4 closes them with two listed `use type` clauses (B9.2). If installed compilation shows any other gap, or reports a transported clause as unreferenced or redundant, the remedy is a reviewed amendment of B4/B9 in a new packet. No table is edited silently, and no warning is suppressed.

---

## B1. Stage table (RC5)

Exactly one packet is applied per stage (§9.1). In the "C_API `External_Name`" column, 31 is observed and every later figure is JACKAL exact (Appendix A of DESIGN.md).

| Stage | Exports relocated in this stage | Cumulative movers / C_API `External_Name` | Predecessor edit (B5) | Tables changed | Units bound in B4 from this stage | `CONTRACT_PINS` regenerated |
|---|---|---|---|---|---|---|
| PK-0 | none | 0 / 31 | none | none (no manifest change) | none | none (controls bound through I5 only) |
| PK-1 | `wl_resources_can_reserve`, `wl_recovery_select` | 2 / 33 | none | Defines every table and the override (B8). `CAPI_CORE_HOME` lists all 91 closure symbols, 2 of them relocated. | B4.1, B4.2 | C_API pair, U1 pair, U2 pair |
| PK-2 | `wl_recovery_authorization_decide_v2`, `wl_recovery_authorization_decide_v3`, `wl_recovery_protocol_decide_v1` | 5 / 36 | E1, E2 | `.update` for the 3 symbols | B4.3, B4.4, B4.5 | C_API pair, U3, U4, U5 pairs |
| PK-2R | none | 5 / 36 | none | none | none | the U3, U4, U5 specs and recovery wire specs it repairs |
| PK-3 | `wl_reservation_lifecycle_plan`, `wl_resource_ledger_compute`, `wl_resource_ledger_headroom`, `wl_resource_policy_admit` | 9 / 40 | none | `.update` for the 4 symbols | B4.6, B4.7, B4.8, B4.9 | C_API pair, U6, U7, U8 pairs |
| PK-3R | none | 9 / 40 | none | none | none | U6, U7, U8 specs it repairs |
| PK-4 | `wl_evaluation_history_select` | 10 / 41 | none | `.update` for 1 symbol | B4.10 | C_API pair, U9 pair |
| PK-4R | none | 10 / 41 | none | none | none | U9 spec it repairs |
| PK-5 | `wl_resource_run_ledger_check_v1`, `wl_chain_authority_replay_v1` | 12 / 43 | E3 | `.update` for 2 symbols | B4.12, B4.13 | C_API pair, U12, U13 pairs |
| PK-5R | none | 12 / 43 | none | none | none | U12, U13 specs and wire specs it repairs |
| PK-6a | none (value routines only, §9.5) | 12 / 43 | none | REQUIRED_PROVED append (57 names) | none | completion pair, finalization pair |
| PK-6b | `wl_completion_decide_v1`, `wl_completion_raw_decide_v1`, `wl_completion_metadata_matches_v1`, `wl_native_diagnostic_control_v1`, `wl_finalization_decide_v1`, `wl_collapse_decide_finalization_v1` | 18 / 49 | E4 | `.update` for 6 symbols. `CAPI_DIAGNOSTIC_SITES` defined (B6); D1–D5 enabled. | B4.14–B4.24 | C_API pair, completion pair, finalization pair |
| PK-6R | none | 18 / 49 | none | none | none | U14, U15 specs and wire specs it repairs |
| PK-7 (after operator D-13) | `wl_pending_decide_v1`, `wl_pending_decide_v2` | 20 / 51 | none | `.update` for 2 core symbols; `CAPI_COMPONENT_HOME` and `CAPI_COMPONENT_INTERFACE` per D-13 (B2.3) | B4.11 | C_API pair, U10, U11 pairs; new component keys (I3, B7) |
| PK-7R | none | 20 / 51 | none | none | none | U10, U11 specs and component specs it repairs |
| PK-S | none | 20 / 51 | none | none (seal limits, §9.8) | none | none (records only that re-pin equals the stage pins) |

At every stage the effective tables are complete for the whole closure. A relocated symbol's home is `core/worldline-c_api.ads`, and every other symbol keeps its S5 home. The final override is never disabled, and an earlier table entry is never removed or reordered. A later packet only appends `.update({...})` lines.

### B1.1 v4 additions to the stage table

The new tables of B8 follow the same stage discipline.

| Stage | New table content appended (`.update` only) |
|---|---|
| PK-1 | Defines `CAPI_TILES`, `CAPI_TRANSPORTS`, `CAPI_INVENTORY`, `CAPI_WRITES`, `CAPI_GATES` (entries for B4.1, B4.2; U1 and U2 have no writes and no acceptance objects), `CAPI_ALIAS_FORBIDDEN` (complete B9.4 table), `CAPI_SPARK_UNITS` (complete), `CAPI_RESIDUAL_SHA256`, `CAPI_SPEC_RESIDUAL_SHA256`, `CAPI_RESIDUAL_CLAUSES` (B9.1), `CAPI_LAYOUT_PACKAGES`, `CAPI_LAYOUT_EXPORTS` (stage-1 prefix), `CAPI_CORE_INTERFACE` (G9), `CAPI_COMPONENT_INTERFACE` (L0, K3), `CAPI_COMPONENT_LIBRARY` (K5) and an empty `CAPI_GLUE_EDITS` |
| PK-2 … PK-5, PK-7 | Entries of the stage's units in `CAPI_TILES`, `CAPI_TRANSPORTS`, `CAPI_INVENTORY`, `CAPI_WRITES` and `CAPI_GATES`; the next slice of `CAPI_LAYOUT_PACKAGES` and `CAPI_LAYOUT_EXPORTS` |
| PK-6b | The same for B4.14–B4.22 and B4.24, plus `CAPI_GLUE_EDITS` GE1–GE9 and the residual deletion R-DEL-1 |
| PK-7 | Under D-13 option (i) only: `CAPI_COMPONENT_INTERFACE` gains `'evaluation_pending_transport'`, and `CAPI_COMPONENT_MIRROR` (K6) is defined |
| PK-xR, PK-6a, PK-S | none |

---

## B2. Home tables

### B2.1 `CAPI_CORE_HOME` at L0 (91 symbols, observed)

Observed over the 137 core Ada files (`DECLARED_CORE_ADA_SOURCES`): 91 `Export` tokens, 91 `External_Name =>` tokens, 91 `"wl_…"` literals, 0 `Import` tokens.

| Home at L0 | Symbols that stay | Symbols that move to `core/worldline-c_api.ads` (stage) |
|---|---|---|
| `core/worldline-c_api.ads` | `wl_hash_file`, `wl_hash_bytes`, `wl_world_id`, `wl_causal_link`, `wl_receipt_link`, `wl_transition_allowed`, `wl_transaction_transition_allowed`, `wl_collapse_decide`, `wl_evaluation_classify`, `wl_evaluation_admissible`, `wl_evaluation_transition_allowed`, `wl_evaluation_advance`, `wl_evaluation_roster_complete`, `wl_abi_version`, `wl_layout_size`, `wl_layout_offset`, `wl_evaluation_wire_version`, `wl_evaluation_wire_layout`, `wl_evaluation_wire_classify`, `wl_evaluation_wire_admit`, `wl_evaluation_wire_report`, `wl_collapse_raw_dependencies_v1`, `wl_collapse_decide_raw_evaluation_v1`, `wl_collapse_decide_raw_evaluation_v2`, `wl_collapse_decide_raw_evaluation_v3`, `wl_owner_transition_version_v1`, `wl_owner_transition_layout_v1`, `wl_owner_transition_authorize_v1`, `wl_owner_audit_version_v1`, `wl_owner_audit_layout_v1`, `wl_owner_audit_decide_v1` | — |
| `core/worldline-resources_c_api.ads` | `wl_resources_abi_version` | `wl_resources_can_reserve` (PK-1) |
| `core/worldline-recovery_c_api.ads` | `wl_recovery_abi_version` | `wl_recovery_select` (PK-1) |
| `core/worldline-recovery_authorization_c_api.ads` | `wl_recovery_authorization_version_v2`, `wl_recovery_authorization_layout_v2` | `wl_recovery_authorization_decide_v2` (PK-2) |
| `core/worldline-recovery_authorization_v3_c_api.ads` | `wl_recovery_authorization_version_v3`, `wl_recovery_authorization_layout_v3` | `wl_recovery_authorization_decide_v3` (PK-2) |
| `core/worldline-recovery_protocol_c_api.ads` | `wl_recovery_protocol_version_v1`, `wl_recovery_protocol_layout_v1` | `wl_recovery_protocol_decide_v1` (PK-2) |
| `core/worldline-reservation_lifecycle_c_api.ads` | `wl_reservation_lifecycle_abi_version`, `wl_reservation_lifecycle_row_size`, `wl_reservation_lifecycle_row_offset` | `wl_reservation_lifecycle_plan` (PK-3) |
| `core/worldline-resource_ledger_c_api.ads` | `wl_resource_ledger_abi_version`, `wl_resource_ledger_layout_size`, `wl_resource_ledger_layout_offset` | `wl_resource_ledger_compute`, `wl_resource_ledger_headroom` (PK-3) |
| `core/worldline-resource_policy_c_api.ads` | `wl_resource_policy_abi_version`, `wl_resource_policy_layout_size`, `wl_resource_policy_layout_offset` | `wl_resource_policy_admit` (PK-3) |
| `core/worldline-evaluation_history_c_api.ads` | `wl_evaluation_history_abi_version`, `wl_evaluation_history_layout_size`, `wl_evaluation_history_layout_offset` | `wl_evaluation_history_select` (PK-4) |
| `core/resource_run_ledger_c_api.ads` | `wl_resource_run_ledger_version_v1`, `wl_resource_run_ledger_layout_v1` | `wl_resource_run_ledger_check_v1` (PK-5) |
| `core/worldline-chain_authority_c_api.ads` | `wl_chain_authority_version_v1`, `wl_chain_authority_layout_v1` | `wl_chain_authority_replay_v1` (PK-5) |
| `core/evaluation_completion_c.ads` | `wl_completion_abi_version_v1`, `wl_completion_layout_size_v1`, `wl_completion_layout_alignment_v1`, `wl_completion_layout_offset_v1`, `wl_completion_context_layout_v1`, `wl_completion_metadata_layout_v1` | `wl_native_diagnostic_control_v1`, `wl_completion_decide_v1`, `wl_completion_raw_decide_v1`, `wl_completion_metadata_matches_v1` (PK-6b) |
| `core/evaluation_finalization_c.ads` | `wl_finalization_version_v1`, `wl_finalization_layout_v1` | `wl_finalization_decide_v1`, `wl_collapse_decide_finalization_v1` (PK-6b) |
| `core/evaluation_pending_c.ads` | `wl_pending_abi_version_v1`, `wl_pending_layout_size_v1`, `wl_pending_layout_alignment_v1`, `wl_pending_layout_offset_v1` | `wl_pending_decide_v1` (PK-7) |
| `core/evaluation_pending_v2_c.ads` | `wl_pending_abi_version_v2`, `wl_pending_layout_size_v2`, `wl_pending_layout_alignment_v2`, `wl_pending_layout_offset_v2` | `wl_pending_decide_v2` (PK-7) |

### B2.2 Per-stage `.update` lines (literal form)

```python
CAPI_CORE_HOME.update({'wl_resources_can_reserve': 'core/worldline-c_api.ads', 'wl_recovery_select': 'core/worldline-c_api.ads'})  # PK-1 (inside the definition)
CAPI_CORE_HOME.update({'wl_recovery_authorization_decide_v2': 'core/worldline-c_api.ads', 'wl_recovery_authorization_decide_v3': 'core/worldline-c_api.ads', 'wl_recovery_protocol_decide_v1': 'core/worldline-c_api.ads'})  # PK-2
CAPI_CORE_HOME.update({'wl_reservation_lifecycle_plan': 'core/worldline-c_api.ads', 'wl_resource_ledger_compute': 'core/worldline-c_api.ads', 'wl_resource_ledger_headroom': 'core/worldline-c_api.ads', 'wl_resource_policy_admit': 'core/worldline-c_api.ads'})  # PK-3
CAPI_CORE_HOME.update({'wl_evaluation_history_select': 'core/worldline-c_api.ads'})  # PK-4
CAPI_CORE_HOME.update({'wl_resource_run_ledger_check_v1': 'core/worldline-c_api.ads', 'wl_chain_authority_replay_v1': 'core/worldline-c_api.ads'})  # PK-5
CAPI_CORE_HOME.update({'wl_completion_decide_v1': 'core/worldline-c_api.ads', 'wl_completion_raw_decide_v1': 'core/worldline-c_api.ads', 'wl_completion_metadata_matches_v1': 'core/worldline-c_api.ads', 'wl_native_diagnostic_control_v1': 'core/worldline-c_api.ads', 'wl_finalization_decide_v1': 'core/worldline-c_api.ads', 'wl_collapse_decide_finalization_v1': 'core/worldline-c_api.ads'})  # PK-6b
CAPI_CORE_HOME.update({'wl_pending_decide_v1': 'core/worldline-c_api.ads', 'wl_pending_decide_v2': 'core/worldline-c_api.ads'})  # PK-7
```

Each stage's `CAPI_DECLARATIONS.update` adds the B3 successor declarations of exactly its symbols. Its `CAPI_ORDERED`/`CAPI_COUNTS` `.update` adds exactly its B4 units.

*v4 note on the line above.* In v4 the `CAPI_ORDERED`/`CAPI_COUNTS` tables are replaced by `CAPI_TILES` and the other B1.1 tables. Each stage's `.update` adds exactly its B4 units to each of them.

### B2.3 `CAPI_COMPONENT_HOME` and `CAPI_COMPONENT_INTERFACE`

Observed at L0:
- The component has 14 Ada files under `pending-component/core/`.
- 10 symbols, 5 in each C spec, each preceded by `External_Name => `.
- `pending-component/pending.gpr` has `Library_Interface` = `("evaluation_pending", "evaluation_pending_c", "evaluation_pending_v2", "evaluation_pending_v2_c", "evaluation_epoch", "resource_quantities", "spark", "spark.big_integers")`, with switches `-gnat2022 -gnata -gnatVa -gnatwa -g -O0`.

| Symbol | Home at L0 | Home after PK-7 under D-13 option (i) (§16.1; proposal) |
|---|---|---|
| `wl_pending_abi_version_v1`, `wl_pending_layout_size_v1`, `wl_pending_layout_alignment_v1`, `wl_pending_layout_offset_v1` | `pending-component/core/evaluation_pending_c.ads` | unchanged |
| `wl_pending_decide_v1` | `pending-component/core/evaluation_pending_c.ads` | `pending-component/core/evaluation_pending_transport.ads` |
| `wl_pending_abi_version_v2`, `wl_pending_layout_size_v2`, `wl_pending_layout_alignment_v2`, `wl_pending_layout_offset_v2` | `pending-component/core/evaluation_pending_v2_c.ads` | unchanged |
| `wl_pending_decide_v2` | `pending-component/core/evaluation_pending_v2_c.ads` | `pending-component/core/evaluation_pending_transport.ads` |

**v4 (replaces v3's paragraph after this table; V3-RC4 K3).** `CAPI_COMPONENT_INTERFACE` is an exact ordered tuple, not a set of quoted strings found anywhere in the project.

- L0 value (observed by parsing the one `Library_Interface` declaration):
  `('evaluation_pending', 'evaluation_pending_c', 'evaluation_pending_v2', 'evaluation_pending_v2_c', 'evaluation_epoch', 'resource_quantities', 'spark', 'spark.big_integers')`.
- Under D-13 option (i), PK-7 appends `'evaluation_pending_transport'`, giving 9 units (JACKAL J16). No original entry is removed or reordered. Options (ii) and (iii) are inadmissible (§16.1), so no table exists for them.
- **K3 (actual membership).** In N1 of `pending-component/pending.gpr`, case-insensitive:
  - `for Library_Interface use (` occurs exactly once, and the word `Library_Interface` occurs exactly once;
  - the parenthesized value is a comma-separated list of string literals only, with no `&`, variable, `external` or attribute reference, and is closed by `);`;
  - the lowercased tuple of the literals equals `CAPI_COMPONENT_INTERFACE` exactly, in order and without duplicates;
  - `for Interfaces use` occurs zero times.

  The v3 sketch accepted a unit name quoted anywhere in the file. For example, `"evaluation_pending"` is also the `Library_Name` value, so v3's sketch passed with that interface unit missing. v4 parses the attribute itself.
- **K5 (library attributes).** `for Library_Name use "evaluation_pending";`, `for Library_Kind use "dynamic";`, `for Library_Standalone use "encapsulated";` and `for Library_Auto_Init use "true";` each occur exactly once in N1 (observed at L0), and no other declaration of those four attributes exists.
- **K6 (D-13 option (i) mirror; defined at PK-7).**
  - The component transport unit `pending-component/core/evaluation_pending_transport.ads`/`.adb` declares exactly B3 declarations 19 and 20 in its specification.
  - Its body's `Pending_Transport` and `Pending_V2_Transport` package spans and its two export bodies are N1-identical to the corresponding scopes of `core/worldline-c_api.adb`.
  - The exact unit text is fixed in PK-7's packet review, because D-13 is an operator choice (§16.1).
- **G9 (core interface).** `core/worldline_core.gpr`'s `Library_Interface`, parsed the same way, equals the observed S5 71-unit tuple (B9.5), and `for Interfaces use` occurs zero times. The file is also pinned. G9 states the membership promise of §3.7 as its own check.

---

## B3. Relocated declarations (exact; P1)

The **Original** column gives the S5 normalized declaration from `function <old> ` to `External_Name => "<symbol>";`. That span was extracted by a read-only script that reimplemented `normalized_ada` without importing any WORLDLINE module. The **Successor** column is the same text with only the identifier replaced. `CAPI_DECLARATIONS[symbol]` is the successor text, which must occur exactly once in normalized `core/worldline-c_api.ads`, while the symbol must occur zero times in its old spec (G6).

| # | Symbol (stage) | Original file, identifier, sha256 of original text | Successor identifier, sha256 of successor text |
|---|---|---|---|
| 1 | `wl_resources_can_reserve` (PK-1) | `core/worldline-resources_c_api.ads`, `Can_Reserve`, `761a7c70159087f9228a14f843d8edc055d9e6ed5ed220397eab700cc490cdbb` | `Resources_Can_Reserve`, `65d9b861141b233af68fc167fe1497cf21568e437c27721e3675af4ee3675936` |
| 2 | `wl_recovery_select` (PK-1) | `core/worldline-recovery_c_api.ads`, `Select_Action`, `988c15a573320c11ab6e9a393a3da7bb02586e384b86702b81e1a82e59a12471` | `Recovery_Select`, `a1c63a2b04a28da4e920af7a2c11d82396a431a0660e0ca5b4c89112ac4a2ffc` |
| 3 | `wl_recovery_authorization_decide_v2` (PK-2) | `core/worldline-recovery_authorization_c_api.ads`, `Decide`, `704c77637a52b387cd75cd957a6b1b55d56019cb727534b94d6333df90d15af2` | `Recovery_Authorization_Decide_V2`, `8b2c82bbf3facccd9f7ee313858633f624592f81ecba073b86584731b94992fa` |
| 4 | `wl_recovery_authorization_decide_v3` (PK-2) | `core/worldline-recovery_authorization_v3_c_api.ads`, `Decide`, `03d0494051074ebaff9c4db2a5fd08118797dce90212d2dbdaba1dcdf06e244a` | `Recovery_Authorization_Decide_V3`, `4c32c093ce4611b2d81b3b58ce2e65c7882bd0b745a0ff04bfad86ba33348e3a` |
| 5 | `wl_recovery_protocol_decide_v1` (PK-2) | `core/worldline-recovery_protocol_c_api.ads`, `Decide`, `cfd44d57ff5aba0995503e73875fe4be0348ebf5c32b3295099980d5a0df0cb6` | `Recovery_Protocol_Decide_V1`, `32257ea85c221b59587bc114eab11b4ec816181d21932abd7608ccf3d6a95aec` |
| 6 | `wl_reservation_lifecycle_plan` (PK-3) | `core/worldline-reservation_lifecycle_c_api.ads`, `Plan`, `6497503f0494300417d7a1e2fc8afd634117a5dfdc36b6f71d4e1f2d91a916e4` | `Reservation_Lifecycle_Plan`, `0589d8b8f42d419ac400edf7a890804a7246863b758d5bf765f346a21bcbccd0` |
| 7 | `wl_resource_ledger_compute` (PK-3) | `core/worldline-resource_ledger_c_api.ads`, `Compute`, `6bb6d3a8b88d85d6442a0de425e055baca3b906cc1aee62844877685d789bd37` | `Resource_Ledger_Compute`, `eba57b58f9b90422a00c185aed7f3a1bf853da126182d43ae12f8a1a7c0729eb` |
| 8 | `wl_resource_ledger_headroom` (PK-3) | `core/worldline-resource_ledger_c_api.ads`, `Headroom`, `ffcc6dd9ba035d37f480411e799cde8255481bcb0acaf81f74473e26f1716619` | `Resource_Ledger_Headroom`, `7c066a1314d62cb59fe8b9f36e6f1555d2661ff1e706875ba1aeb4b75cc57470` |
| 9 | `wl_resource_policy_admit` (PK-3) | `core/worldline-resource_policy_c_api.ads`, `Admit`, `fa5dcd37d081f3dcd56f32edaec2f12cf6e47237547e12bdc7160f00c32b7699` | `Resource_Policy_Admit`, `2e6c8b4ec45b9e7a05ff5b3d89743c9765c4bdff0c7659fbb3df9ae2deadb314` |
| 10 | `wl_evaluation_history_select` (PK-4) | `core/worldline-evaluation_history_c_api.ads`, `Select_Evidence`, `f7b69dc152ed180aed8713064432a6a0f7cff2610dd1b4734a66bdd8b892c7b5` | `Evaluation_History_Select`, `7dd65cab5d4d8c46a22803771ca9796d41bd13a6887d0cd0eebbc62c7a61eb85` |
| 11 | `wl_resource_run_ledger_check_v1` (PK-5) | `core/resource_run_ledger_c_api.ads`, `Check`, `da2d307ccd3ce10c13683caa5a7a7bcdc6f93bfb973e7b209aab30d24736c746` | `Run_Ledger_Check`, `31a87eb960174130db8155f88687b357df5cf636c22de21f669de67d092836db` |
| 12 | `wl_chain_authority_replay_v1` (PK-5) | `core/worldline-chain_authority_c_api.ads`, `Replay`, `9f1d04c4681fe7d76148f32543b34fd8122926b87a53fdab8c8290168e2f6275` | `Chain_Replay`, `bb24be87f17871cc6946d1aff018875d218bb008ad4e71943fd054bb937c2047` |
| 13 | `wl_completion_decide_v1` (PK-6b) | `core/evaluation_completion_c.ads`, `Decide`, `20a88b0f1ca98f4c0d8ddf5df2b6f29bfd1b3f3221b989835e8ed9e1e600bebc` | `Completion_Decide`, `633b5e10cefa3a2730223dbed01081d9dc22ab8a7577920e19ae4da2bc923135` |
| 14 | `wl_completion_raw_decide_v1` (PK-6b) | `core/evaluation_completion_c.ads`, `Raw_Decide`, `15bfe93d566a2145164c221b0a6e491af2aa2b38acad02bc80f3d852055dfdc3` | `Completion_Raw_Decide`, `f953c68e4ca2b1dd31e5f4660d966a29702dc211245d770ccfb5b74d6255e594` |
| 15 | `wl_completion_metadata_matches_v1` (PK-6b) | `core/evaluation_completion_c.ads`, `Metadata_Matches`, `5d35ca057cd49546791e10c70de11a6d1b682a5c378ecfad78eaeff7a842ee93` | `Completion_Metadata_Matches`, `af3087fd991fb5b8664260497c732829beaa2b4c35371c06b98823e7020fac3f` |
| 16 | `wl_native_diagnostic_control_v1` (PK-6b) | `core/evaluation_completion_c.ads`, `Diagnostic_Control`, `38c8fec72ac32fed3bab9d9af0fcde544db5748bdd2a1c920564658bcbbbe511` | `Native_Diagnostic_Control`, `be2802255d649baba0a0956f3960bf9b022646d9db19feb97ba0725d40185524` |
| 17 | `wl_finalization_decide_v1` (PK-6b) | `core/evaluation_finalization_c.ads`, `Decide`, `ad24b6a8d75928c7e1fd08142c8acb30525630b7be13ba5bbc470f6ce40d8a0f` | `Finalization_Decide`, `926da24505ec1b14b63e2e01176ac36144242151cbc3d27f9075277cf525e97e` |
| 18 | `wl_collapse_decide_finalization_v1` (PK-6b) | `core/evaluation_finalization_c.ads`, `Decide_Mixed`, `fc1ea3df6ad5ca8ead51a9ddb6b173b5c41e8a167c994da89ef5cb7258f5f2e0` | `Finalization_Decide_Mixed`, `cd470941b2cda2ef68f74c3de6d3bdd8cd81c36794ed18f579d8be6c34814693` |
| 19 | `wl_pending_decide_v1` (PK-7) | `core/evaluation_pending_c.ads`, `Decide`, `1342b938e6ce1a9ef8b2f4c6364391681ef31c2ecc3a71a53f1dbf286f96b570` | `Pending_Decide_V1`, `deff63d3aab3015da305c8a53c2c8969e07f43e360d9b752ece03a1d8723bef1` |
| 20 | `wl_pending_decide_v2` (PK-7) | `core/evaluation_pending_v2_c.ads`, `Decide`, `dfe6ce06f81381cf5583f58c7812d16f7bc64623202e725433384e7cd8a67cd6` | `Pending_Decide_V2`, `32e00118ed4dab033466ebada78bf52e3f06c6a7b7f7ddab8c71e60e1cbf5a59` |

Successor texts. Each is the literal value of `CAPI_DECLARATIONS[symbol]`, and each original is identical except for the identifier shown in the table above.

```text
1  function Resources_Can_Reserve (Available_Negative : Interfaces.Unsigned_8; Available : System.Address; Available_Length : Interfaces.C.size_t; Withheld : System.Address; Withheld_Length : Interfaces.C.size_t; Floor : System.Address; Floor_Length : Interfaces.C.size_t; Requested : System.Address; Requested_Length : Interfaces.C.size_t) return Interfaces.Unsigned_8 with Export, Convention => C, External_Name => "wl_resources_can_reserve";
2  function Recovery_Select (Expected : System.Address; Expected_Length : Interfaces.C.size_t; Live_Present : Interfaces.Unsigned_8; Live : System.Address; Live_Length : Interfaces.C.size_t; Prepared_Present : Interfaces.Unsigned_8; Prepared : System.Address; Prepared_Length : Interfaces.C.size_t) return Interfaces.Unsigned_8 with Export, Convention => C, External_Name => "wl_recovery_select";
3  function Recovery_Authorization_Decide_V2 (Input : System.Address; Input_Length : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_recovery_authorization_decide_v2";
4  function Recovery_Authorization_Decide_V3 (Input : System.Address; Input_Length : Interfaces.C.size_t; Arena : System.Address; Arena_Length : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_recovery_authorization_decide_v3";
5  function Recovery_Protocol_Decide_V1 (Input : System.Address; Input_Length : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_recovery_protocol_decide_v1";
6  function Reservation_Lifecycle_Plan (Data : System.Address; Data_Length : Size; Rows : System.Address; Row_Count : Size; Mode, Present : U8; Requested_First, Requested_Length : Size; Removed : System.Address; Removed_Length : Size) return U8 with Export, Convention => C, External_Name => "wl_reservation_lifecycle_plan";
7  function Resource_Ledger_Compute (Data : System.Address; Data_Length : Size; Rows : System.Address; Row_Count : Size; Detail_Data : System.Address; Detail_Length : Size; Total_Data : System.Address; Total_Length : Size; Details : System.Address; Result : System.Address) return U8 with Export, Convention => C, External_Name => "wl_resource_ledger_compute";
8  function Resource_Ledger_Headroom (Data : System.Address; Data_Length : Size; Available, Withheld, Floor : System.Address; Output : System.Address; Output_Length : Size; Result : System.Address) return U8 with Export, Convention => C, External_Name => "wl_resource_ledger_headroom";
9  function Resource_Policy_Admit (Data : System.Address; Data_Length : Size; Input : System.Address; Disks : System.Address; Disk_Count : Size; Result : System.Address) return U8 with Export, Convention => C, External_Name => "wl_resource_policy_admit";
10 function Evaluation_History_Select (Data : System.Address; Data_Length : Size; Rows : System.Address; Row_Count : Size; Final_Present : U8; Final_Row, Query, Output : System.Address) return U8 with Export, Convention => C, External_Name => "wl_evaluation_history_select";
11 function Run_Ledger_Check (Input : System.Address; Input_Length : Interfaces.C.size_t; Arena : System.Address; Arena_Length : Interfaces.C.size_t; Before_Rows : System.Address; Before_Count : Interfaces.C.size_t; Proposed_Rows : System.Address; Proposed_Count : Interfaces.C.size_t; Native : System.Address; Native_Count : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_resource_run_ledger_check_v1";
12 function Chain_Replay (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t; Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t; Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_chain_authority_replay_v1";
13 function Completion_Decide (Input, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_completion_decide_v1";
14 function Completion_Raw_Decide (Input, Raw_Rows, Confinements, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_completion_raw_decide_v1";
15 function Completion_Metadata_Matches (Input, Context : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_completion_metadata_matches_v1";
16 function Native_Diagnostic_Control (Enable : U32) return U32 with Export, Convention => C, External_Name => "wl_native_diagnostic_control_v1";
17 function Finalization_Decide (Input, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_finalization_decide_v1";
18 function Finalization_Decide_Mixed (Collapse : System.Address; Primary_Kind : U32; Primary, Primary_Raw, Primary_Confinement, Primary_Context : System.Address; Staged_Kind : U32; Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address; Agent_Confinement : U8) return U8 with Export, Convention => C, External_Name => "wl_collapse_decide_finalization_v1";
19 function Pending_Decide_V1 (Input, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_pending_decide_v1";
20 function Pending_Decide_V2 (Input, Output : System.Address) return Interfaces.C.int with Export, Convention => C, External_Name => "wl_pending_decide_v2";
```

**Subtype resolution (P2).**
- The originals of 6–10 use their unit's `Size`, `U8` and `U32`, and 16 and 18 use `U32` and `U8`.
- The successors resolve those names to the four `Worldline.C_API` subtypes (§3.6), which denote the same first subtypes: `Interfaces.C.size_t`, `Interfaces.Unsigned_8` and `Interfaces.Unsigned_32`.
- Observed today: `core/worldline-c_api.ads` declares no `U8`, `U32`, `I64` or `Size`. It does declare `subtype Byte is Interfaces.Unsigned_8;` (`:185`). The body uses `Size` only as the attribute `'Size` (`core/worldline-c_api.adb:550-555`) and refers to `K.U32` inside `Authority_Glue` (`:764`).
- Matching resolution in compiled code, and the native ABI, are OPEN (D-15, D-34).

*v4 note.* `subtype Byte is Interfaces.Unsigned_8;` (`:185`) is declared inside the nested specification `package Authority_Glue` (`core/worldline-c_api.ads:184-216`), so it is not directly visible at C_API package level. P2 is unaffected.

---

## B4. Per-unit binding (REVISED in v4: exact tiles, transport contents, write and gate rows)

### B4.0 Conventions and layout

- **Tiles.** For each tiled subprogram, segments S1…Sn are exact N1 strings. The isolated text must equal `HEAD + " " + " ".join(S1, …, Sn)` (R-TILE).
  - For exports, `HEAD` is B3 item *n* with ` with Export, Convention => C, External_Name => "…";` replaced by ` is`.
  - S1 is always the declarative part: the scope's clause block (B9.2), then any local declarations. The next segment begins with `begin`.
- **Transport package entries** list:
  - the clause block (B9.2, by id);
  - `SUBTYPES[T]`;
  - `HELPERS[T]` (B9.3 gives kind and sha256 of each);
  - `CONSTANTS[T]`;
  - moved subprograms.

  Expression-function, access-type and instance helpers are placed in the specification. `body` helpers are declared in the specification by their profile and completed verbatim in the body (R-TRANS).
- **Write and gate rows** refer to B10.
- **Read staging** for each export is in §9.6 (DESIGN), the per-export effect table.
- **`CAPI_LAYOUT_PACKAGES`** (final order; each stage appends its packages at the end of the run):
  `Resources_Transport, Recovery_Transport, Recovery_Authorization_Transport, Recovery_Authorization_V3_Transport, Recovery_Protocol_Transport, Lifecycle_Transport, Ledger_Transport, Policy_Transport, History_Transport, Run_Ledger_Transport, Chain_Transport, Diagnostic_Transport, Completion_Transport, Finalization_Transport, Pending_Transport, Pending_V2_Transport` (16, JACKAL J18).
  - Each is `package T is … end T; package body T is … end T;`.
  - The run lies between `end Layout_Offset;` and `package body Authority_Glue is` (S5 `core/worldline-c_api.adb:667` and `:671`).
  - Every package that uses another one follows it: `Completion_Transport` uses `Diagnostic_Transport`, and `Finalization_Transport` uses both.
- **`CAPI_LAYOUT_EXPORTS`** (final order = B3 order 1–20): `Resources_Can_Reserve, Recovery_Select, Recovery_Authorization_Decide_V2, Recovery_Authorization_Decide_V3, Recovery_Protocol_Decide_V1, Reservation_Lifecycle_Plan, Resource_Ledger_Compute, Resource_Ledger_Headroom, Resource_Policy_Admit, Evaluation_History_Select, Run_Ledger_Check, Chain_Replay, Completion_Decide, Completion_Raw_Decide, Completion_Metadata_Matches, Native_Diagnostic_Control, Finalization_Decide, Finalization_Decide_Mixed, Pending_Decide_V1, Pending_Decide_V2`.
  - The body run lies between `end Owner_Audit_Decide;` and the final `end Worldline.C_API;`.
  - The specification run (subtypes first) lies between `External_Name => "wl_owner_audit_decide_v1";` and the final `end Worldline.C_API;`.
- **The four C_API subtypes (PK-1, specification):** `subtype U8 is Interfaces.Unsigned_8; subtype U32 is Interfaces.Unsigned_32; subtype I64 is Interfaces.Integer_64; subtype Size is Interfaces.C.size_t;` (P2, carried).

### B4.1 `Resources_Can_Reserve` (U1, PK-1)

**Transport `Resources_Transport`.**
- Clauses: CL-T1 (B9.2).
- Subtypes: none. Constants: none. Moved subprograms: none.
- Helpers: `Byte_Access` (type), `As_Byte` (fn_inst), `Valid` (expr), `Decode` (body), copied from `core/worldline-resources_c_api.adb:12-34`.

**Export.** HEAD = B3 #1.
1. `use Resources_Transport; use type Interfaces.Unsigned_8; use type Interfaces.C.size_t; use type System.Address; use System.Storage_Elements;`
2. `begin if not Worldline.Resources_C_API.Negative_Flag_Valid (Available_Negative) or else not Valid (Available, Available_Length) or else not Valid (Withheld, Withheld_Length) or else not Valid (Floor, Floor_Length) or else not Valid (Requested, Requested_Length) then return 255; end if;`
3. `return Worldline.Resources_C_API.Can_Reserve_Value (Available_Negative, Decode (Available, Available_Length), Decode (Withheld, Withheld_Length), Decode (Floor, Floor_Length), Decode (Requested, Requested_Length));`
4. `exception when others => return 255; end Resources_Can_Reserve;`

Writes: none. Gates: none.

### B4.2 `Recovery_Select` (U2, PK-1)

**Transport `Recovery_Transport`.**
- Clauses: CL-T2. The S5 body-local `subtype Size is Interfaces.C.size_t;` (`core/worldline-recovery_c_api.adb:8`) is not transported. P2 forbids a second `Size`, and `Worldline.C_API.Size` denotes the same first subtype.
- Subtypes: none.
- Helpers: `Byte_Access`, `As_Byte`, `Shape` (expr), `Copy` (body), from `:13-35`. The original `Marker` (`:37-51`) is not copied; its decision logic is `Marker_Of` in SPARK.
- Constants: `Empty : constant Worldline.Recovery.Identity_Bytes (1 .. 0) := (others => 0);`

**Export.** HEAD = B3 #2.
1. `use Recovery_Transport; use type R.Byte_Count; use type Size; use type Interfaces.Unsigned_8; use type System.Address; use System.Storage_Elements;`
2. `begin if not Worldline.Recovery_C_API.Presence_Valid (Live_Present, Prepared_Present) or else not Shape (Expected, Expected_Length) or else (Worldline.Recovery_C_API.Present (Live_Present) and then not Shape (Live, Live_Length)) or else (Worldline.Recovery_C_API.Present (Prepared_Present) and then not Shape (Prepared, Prepared_Length)) then return 255; end if;`
3. `declare Expected_Value : constant Worldline.Recovery.Identity_Bytes := Copy (Expected, Expected_Length); Live_Value : constant Worldline.Recovery.Identity_Bytes := (if Worldline.Recovery_C_API.Present (Live_Present) then Copy (Live, Live_Length) else Empty); Prepared_Value : constant Worldline.Recovery.Identity_Bytes := (if Worldline.Recovery_C_API.Present (Prepared_Present) then Copy (Prepared, Prepared_Length) else Empty); begin return Worldline.Recovery_C_API.Select_Value (Expected_Value, Live_Present, Live_Value, Prepared_Present, Prepared_Value); end;`
4. `exception when others => return 255; end Recovery_Select;`

Writes: none. Gates: none.

### B4.3 `Recovery_Authorization_Decide_V2` (U3, PK-2)

**Transport `Recovery_Authorization_Transport`.**
- Clauses: CL-T3. Subtypes: none.
- Helpers: `Request_Access`, `Result_Access` (type), `Request_At`, `Result_At` (fn_inst), `Shape` (expr), from `core/worldline-recovery_authorization_c_api.adb:12-17` and `:116-121`. The `Layout` function (`:18-114`) stays in SPARK.

**Export.** HEAD = B3 #3.
1. `use Recovery_Authorization_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int;`
2. `begin if Input_Length /= W.Raw_Request'Size / System.Storage_Unit or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length) or else To_Integer (Input) mod W.Raw_Request'Alignment /= 0 or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;`
3. `declare Raw : constant W.Raw_Request := Request_At (Input).all; begin if not W.Well_Formed (Raw) then return -1; end if; declare Owned : constant W.Raw_Result := Worldline.Recovery_Authorization_C_API.Decide_Total (Raw); begin Result_At (Output).all := Owned; end; end; return 0;`
4. `exception when others => return -1; end Recovery_Authorization_Decide_V2;`

Segment 2 is the S5 guard verbatim (`:131-138`). Writes: W03 (WF-C). Gates: none; the `W.Well_Formed (Raw)` predicate gate lies inside W03's span.

### B4.4 `Recovery_Authorization_Decide_V3` (U4, PK-2)

**Transport `Recovery_Authorization_V3_Transport`.**
- Clauses: CL-T4. Subtypes: none.
- Helpers: `Byte_Access`, `Byte_At`, `Request_Access`, `Result_Access`, `Request_At`, `Result_At`, `Shape`, from `core/worldline-recovery_authorization_v3_c_api.adb:15-23` and `:125-130`.

**Export.** HEAD = B3 #4.
1. `use Recovery_Authorization_V3_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int; use type Q.Byte_Count;`
2. `begin if Input_Length /= W.Raw_Request'Size / System.Storage_Unit or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length) or else Arena_Length > Interfaces.C.size_t (Q.Byte_Count'Last) or else (Arena_Length > 0 and then not Shape (Arena, Arena_Length)) or else To_Integer (Input) mod W.Raw_Request'Alignment /= 0 or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;`
3. `declare Raw : constant W.Raw_Request := Request_At (Input).all; Data : Q.Byte_Array (1 .. Q.Byte_Count (Arena_Length)); begin for Position in Data'Range loop Data (Position) := Byte_At (Arena + Storage_Offset (Position - 1)).all; end loop; if not W.Well_Formed (Data, Raw) then return -1; end if; declare Owned : constant W.Raw_Result := Worldline.Recovery_Authorization_V3_C_API.Decide_Total (Data, Raw); begin Result_At (Output).all := Owned; end; end; return 0;`
4. `exception when others => return -1; end Recovery_Authorization_Decide_V3;`

Segment 2 is the S5 guard verbatim (`:139-149`), and the capture, unconditional arena copy and `Well_Formed` gate of segment 3 are verbatim (`:150-160`). Writes: W04 (WF-C). Gates: none.

### B4.5 `Recovery_Protocol_Decide_V1` (U5, PK-2)

**Transport `Recovery_Protocol_Transport`.**
- Clauses: CL-T5. Subtypes: none.
- Helpers: `Request_Access`, `Result_Access`, `Request_At`, `Result_At`, `Shape`, from `core/worldline-recovery_protocol_c_api.adb:12-15` and `:40-43`.

**Export.** HEAD = B3 #5.
1. `use Recovery_Protocol_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int;`
2. `begin if Input_Length /= W.Raw_Request'Size / System.Storage_Unit or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length) or else To_Integer (Input) mod W.Raw_Request'Alignment /= 0 or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;`
3. `declare Raw : constant W.Raw_Request := Request_At (Input).all; Owned_Result : W.Raw_Result := (After => 0); Status : Interfaces.C.int; begin Worldline.Recovery_Protocol_ABI.Apply (Raw, Owned_Result, Status); if Status /= Worldline.Recovery_Protocol_ABI.Success then return Status; end if; Result_At (Output).all := Owned_Result; end; return 0;`
4. `exception when others => return -1; end Recovery_Protocol_Decide_V1;`

Segments 2–4 are the S5 body verbatim after `is` (`:48-71`); only segment 1 and the identifier are new. Writes: W05 (WF-P). Gates: none.

### B4.6 `Reservation_Lifecycle_Plan` (U6, PK-3)

**Transport `Lifecycle_Transport`.**
- Clauses: CL-T6.
- Subtypes: `subtype Row_C is Worldline.Reservation_Lifecycle_C_API.Row_C;`
- Helpers: `Byte_Access`, `Row_Access`, `As_Byte`, `As_Row`, `Extent_Valid` (expr), `Copy_Data` (body), from `core/worldline-reservation_lifecycle_c_api.adb:15-18`, `:33-51`.

**Export.** HEAD = B3 #6.
1. `use Lifecycle_Transport; use type U8; use type Size; use type System.Address; use System.Storage_Elements; use type L.Result_Status; Row_Size : constant Size := Worldline.Reservation_Lifecycle_C_API.Layout_Size;`
2. `begin if Data_Length > Size (R.Byte_Count'Last) or else Row_Count > Size (R.Byte_Count'Last) or else Removed_Length > Size (R.Byte_Count'Last) or else Row_Count > Size (Storage_Offset'Last) / Row_Size or else not Worldline.Reservation_Lifecycle_C_API.Request_Valid (Present, Requested_First, Requested_Length) or else not Extent_Valid (Data, Data_Length) or else not Extent_Valid (Rows, Row_Count * Row_Size, Row_C'Alignment) or else not Extent_Valid (Removed, Removed_Length) then return 255; end if;`
3. `declare Arena : constant R.Byte_Array := Copy_Data (Data, Data_Length); Typed_Rows : L.Entry_Array (1 .. R.Byte_Count (Row_Count)); Mask : L.Removal_Array (1 .. R.Byte_Count (Removed_Length)) := (others => False); Requested : constant L.Optional_Identity := Worldline.Reservation_Lifecycle_C_API.Requested_Of (Present, Requested_First, Requested_Length); Selected_Mode : constant L.Operation := Worldline.Reservation_Lifecycle_C_API.Operation_Of (Mode); Status : L.Result_Status; begin`
4. `for I in Typed_Rows'Range loop declare Row : constant Row_C := As_Row (Rows + Storage_Offset (Size (I - 1) * Row_Size)).all; D : constant Worldline.Reservation_Lifecycle_C_API.Row_Acceptance := Worldline.Reservation_Lifecycle_C_API.Accept_Row (Row); begin if not D.Ok then return 255; end if; Typed_Rows (I) := D.Item; end; end loop;`
5. `L.Plan (Arena, Typed_Rows, Requested, Selected_Mode, Mask, Status); if Worldline.Reservation_Lifecycle_C_API.Publishes_Mask (Status) then for I in Mask'Range loop As_Byte (Removed + Storage_Offset (I - 1)).all := Worldline.Reservation_Lifecycle_C_API.Mask_Byte (Mask (I)); end loop; end if; return Worldline.Reservation_Lifecycle_C_API.Status_Code (Status); end;`
6. `exception when others => return 255; end Reservation_Lifecycle_Plan;`

Writes: W06 (WF-F with WF-O argument). Gates: G06 (`D`).

### B4.7 `Resource_Ledger_Compute` (U7, PK-3)

**Transport `Ledger_Transport`** (shared with B4.8).
- Clauses: CL-T7.
- Subtypes: `subtype Row_C is Worldline.Resource_Ledger_C_API.Row_C; subtype Quantity_C is Worldline.Resource_Ledger_C_API.Quantity_C; subtype Result_C is Worldline.Resource_Ledger_C_API.Result_C;`
- Helpers: `Byte_Access`, `Row_Access`, `Quantity_Access`, `Result_Access`, `As_Byte`, `As_Row`, `As_Quantity`, `As_Result`, `Extent_Valid` (expr), `Copy_Data` (body), `Write_Data` (body), from `core/worldline-resource_ledger_c_api.adb:15-24`, `:64-72`, `:90-106`. `Shape`, `Decode` and `Encode` (`:74-88`) move to SPARK and are not copied.

**Export.** HEAD = B3 #7.
1. `use Ledger_Transport; use type U8; use type Size; use type System.Address; use System.Storage_Elements; use type Q.Byte_Count; Row_Size : constant Size := Row_C'Object_Size / System.Storage_Unit; Quantity_Size : constant Size := Quantity_C'Object_Size / System.Storage_Unit;`
2. `begin if Data_Length > Size (Q.Byte_Count'Last) or else Detail_Length > Size (Q.Byte_Count'Last) or else Total_Length > Size (Q.Byte_Count'Last) or else Row_Count > Size (Q.Byte_Count'Last) or else Row_Count > Size (Storage_Offset'Last) / Row_Size or else Row_Count > Size (Storage_Offset'Last) / Quantity_Size or else not Extent_Valid (Data, Data_Length) or else not Extent_Valid (Detail_Data, Detail_Length) or else not Extent_Valid (Total_Data, Total_Length) or else not Extent_Valid (Rows, Row_Count * Row_Size, Row_C'Alignment) or else not Extent_Valid (Details, Row_Count * Quantity_Size, Quantity_C'Alignment) or else not Extent_Valid (Result, Result_C'Object_Size / System.Storage_Unit, Result_C'Alignment) then return 255; end if;`
3. `declare Arena : constant Q.Byte_Array := Copy_Data (Data, Data_Length); Typed_Rows : L.Reservation_Array (1 .. Q.Byte_Count (Row_Count)); Slots : L.Span_Array (Typed_Rows'Range); Detail_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Detail_Length)); Total_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Total_Length)); Typed_Details : L.Quantity_Array (Typed_Rows'Range); Total : Q.Quantity; Status : L.Result_Status; begin`
4. `for I in Typed_Rows'Range loop declare V : constant Row_C := As_Row (Rows + Storage_Offset (Size (I - 1) * Row_Size)).all; D : constant Worldline.Resource_Ledger_C_API.Row_Acceptance := Worldline.Resource_Ledger_C_API.Accept_Row (V); begin if not D.Ok then return 255; end if; Typed_Rows (I) := D.Row; Slots (I) := D.Slot; end; end loop;`
5. `L.Compute (Arena, Typed_Rows, Slots, Detail_Arena, Total_Arena, Typed_Details, Total, Status); Write_Data (Detail_Data, Detail_Arena); Write_Data (Total_Data, Total_Arena); for I in Typed_Details'Range loop As_Quantity (Details + Storage_Offset (Size (I - 1) * Quantity_Size)).all := Worldline.Resource_Ledger_C_API.Encode_Quantity (Typed_Details (I)); end loop; As_Result (Result).all := Worldline.Resource_Ledger_C_API.Result_Of (Status, Total); return 0; end;`
6. `exception when others => return 255; end Resource_Ledger_Compute;`

Segments 2 and 3 are the S5 guard and declarations verbatim (`:118-144`). Segment 5 keeps the S5 writeback order (`:162-173`). Writes: W07 and W08 (WF-B), W09 and W10 (WF-F). Gates: G07 (`D`).

### B4.8 `Resource_Ledger_Headroom` (U7, PK-3)

**Export.** HEAD = B3 #8. Transport: B4.7.
1. `use Ledger_Transport; use type U8; use type Size; use type System.Address; use System.Storage_Elements; use type Q.Byte_Count; Quantity_Size : constant Size := Quantity_C'Object_Size / System.Storage_Unit;`
2. `begin if Data_Length > Size (Q.Byte_Count'Last) or else Output_Length > Size (Q.Byte_Count'Last) or else not Extent_Valid (Data, Data_Length) or else not Extent_Valid (Output, Output_Length) or else not Extent_Valid (Available, Quantity_Size, Quantity_C'Alignment) or else not Extent_Valid (Withheld, Quantity_Size, Quantity_C'Alignment) or else not Extent_Valid (Floor, Quantity_Size, Quantity_C'Alignment) or else not Extent_Valid (Result, Result_C'Object_Size / System.Storage_Unit, Result_C'Alignment) then return 255; end if;`
3. `declare A : constant Quantity_C := As_Quantity (Available).all; W : constant Quantity_C := As_Quantity (Withheld).all; F : constant Quantity_C := As_Quantity (Floor).all; HI : constant Worldline.Resource_Ledger_C_API.Headroom_Acceptance := Worldline.Resource_Ledger_C_API.Accept_Headroom_Inputs (A, W, F); begin if not HI.Ok then return 255; end if;`
4. `declare Arena : constant Q.Byte_Array := Copy_Data (Data, Data_Length); Output_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Output_Length)); Typed_Result : Q.Quantity; Status : L.Result_Status; begin L.Compute_Headroom (Arena, HI.Available, HI.Withheld, HI.Floor, Output_Arena, Typed_Result, Status); Write_Data (Output, Output_Arena); As_Result (Result).all := Worldline.Resource_Ledger_C_API.Result_Of (Status, Typed_Result); return 0; end; end;`
5. `exception when others => return 255; end Resource_Ledger_Headroom;`

The three decodes of S5 `:213` move into `Accept_Headroom_Inputs` (M4, §3.1); the Data copy stays after the acceptance (`:207`). Writes: W11 (WF-B), W12 (WF-F). Gates: G08 (`HI`).

### B4.9 `Resource_Policy_Admit` (U8, PK-3)

**Transport `Policy_Transport`.**
- Clauses: CL-T8.
- Subtypes: `subtype Input_C is Worldline.Resource_Policy_C_API.Input_C; subtype Disk_C is Worldline.Resource_Policy_C_API.Disk_C; subtype Result_C is Worldline.Resource_Policy_C_API.Result_C;`
- Helpers: `Byte_Access`, `Input_Access`, `Disk_Access`, `Result_Access`, `As_Byte`, `As_Input`, `As_Disk`, `As_Result`, `Extent_Valid` (expr), `Decode_Data` (body), from `core/worldline-resource_policy_c_api.adb:15-22`, `:78-86`, `:102-111`. `Shape` and `Decode` move to SPARK.

**Export.** HEAD = B3 #9.
1. `use Policy_Transport; use type U8; use type Size; use type System.Address; use System.Storage_Elements; use type Q.Byte_Count; Disk_Size : constant Size := Disk_C'Object_Size / System.Storage_Unit;`
2. `begin if Data_Length > Size (Q.Byte_Count'Last) or else Disk_Count > Size (Q.Byte_Count'Last) or else Disk_Count > Size (Storage_Offset'Last) / Disk_Size or else not Extent_Valid (Data, Data_Length) or else not Extent_Valid (Input, Input_C'Object_Size / System.Storage_Unit, Input_C'Alignment) or else not Extent_Valid (Result, Result_C'Object_Size / System.Storage_Unit, Result_C'Alignment) or else not Extent_Valid (Disks, Disk_Count * Disk_Size, Disk_C'Alignment) then return 255; end if;`
3. `declare V : constant Input_C := As_Input (Input).all; IA : constant Worldline.Resource_Policy_C_API.Input_Acceptance := Worldline.Resource_Policy_C_API.Accept_Input (V); begin if not IA.Ok then return 255; end if; declare Rows : P.Disk_Array (1 .. Q.Byte_Count (Disk_Count)); begin`
4. `for I in Rows'Range loop declare Row : constant Disk_C := As_Disk (Disks + Storage_Offset (Size (I - 1) * Disk_Size)).all; D : constant Worldline.Resource_Policy_C_API.Disk_Acceptance := Worldline.Resource_Policy_C_API.Accept_Disk (Row); begin if not D.Ok then return 255; end if; Rows (I) := D.Item; end; end loop;`
5. `declare Arena : constant Q.Byte_Array := Decode_Data (Data, Data_Length); Decision : constant P.Decision := P.Admit (Arena, IA.State, Rows); begin As_Result (Result).all := Worldline.Resource_Policy_C_API.Encode_Decision (Decision); return 0; end; end; end;`
6. `exception when others => return 255; end Resource_Policy_Admit;`

Writes: W13 (WF-F with a WF-C argument). Gates: G09a (`IA`), G09b (`D`).

### B4.10 `Evaluation_History_Select` (U9, PK-4)

**Transport `History_Transport`.**
- Clauses: CL-T9.
- Subtypes: `subtype Row_C is Worldline.Evaluation_History_C_API.Row_C; subtype Query_C is Worldline.Evaluation_History_C_API.Query_C; subtype Selection_C is Worldline.Evaluation_History_C_API.Selection_C;`
- Helpers: `Byte_Access`, `Row_Access`, `Query_Access`, `Selection_Access`, `As_Byte`, `As_Row`, `As_Query`, `As_Selection`, `Extent_Valid` (expr), `Copy_Data` (body), from `core/worldline-evaluation_history_c_api.adb:14-21`, `:66-72`, `:115-122`. The validity predicates, decoders and `Ref_Index` move to SPARK.

**Export.** HEAD = B3 #10.
1. `use History_Transport; use type U8; use type R.Byte_Count; use type Size; use type System.Address; use System.Storage_Elements; Stride : constant Size := Worldline.Evaluation_History_C_API.Layout_Size (4);`
2. `begin if Data_Length > Size (R.Byte_Count'Last) or else Row_Count > Size (R.Byte_Count'Last) or else Row_Count > Size (Storage_Offset'Last) / Stride or else not Worldline.Evaluation_History_C_API.Final_Flag_Valid (Final_Present) or else not Extent_Valid (Data, Data_Length) or else not Extent_Valid (Rows, Row_Count * Stride, Row_C'Alignment) or else (Worldline.Evaluation_History_C_API.Final_Row_Present (Final_Present) and then not Extent_Valid (Final_Row, Stride, Row_C'Alignment)) or else not Extent_Valid (Query, Worldline.Evaluation_History_C_API.Layout_Size (5), Query_C'Alignment) or else not Extent_Valid (Output, Worldline.Evaluation_History_C_API.Layout_Size (6), Selection_C'Alignment) then return 255; end if;`
3. `declare Raw_Q : constant Query_C := As_Query (Query).all; A : constant R.Byte_Array := Copy_Data (Data, Data_Length); History : H.History (1 .. R.Byte_Count (Row_Count)); F : H.Optional_Record; QA : constant Worldline.Evaluation_History_C_API.Query_Acceptance := Worldline.Evaluation_History_C_API.Accept_Query (Raw_Q); begin if not QA.Ok then return 255; end if;`
4. `if Worldline.Evaluation_History_C_API.Final_Row_Present (Final_Present) then declare V : constant Row_C := As_Row (Final_Row).all; FA : constant Worldline.Evaluation_History_C_API.Final_Acceptance := Worldline.Evaluation_History_C_API.Accept_Final_Row (V); begin if not FA.Ok then return 255; end if; F := FA.Item; end; end if;`
5. `for I in History'Range loop declare V : constant Row_C := As_Row (Rows + Storage_Offset (Size (I - 1) * Stride)).all; D : constant Worldline.Evaluation_History_C_API.Row_Acceptance := Worldline.Evaluation_History_C_API.Accept_Row (V); begin if not D.Ok then return 255; end if; History (I) := D.Item; end; end loop;`
6. `declare Result : constant Selection_C := Worldline.Evaluation_History_C_API.Select_Result (A, History, F, QA.Item); begin As_Selection (Output).all := Result; return 0; end; end;`
7. `exception when others => return 255; end Evaluation_History_Select;`

The S5 order is kept: the query capture, the Data copy, the `History` allocation and `F` all precede the query validation (`:146-156`). So Data is read before a query refusal (§9.6). Writes: W14 (WF-C). Gates: G10a (`QA`), G10b (`FA`), G10c (`D`).

### B4.11 `Pending_Decide_V1` and `Pending_Decide_V2` (U10, U11, PK-7)

**Transport `Pending_Transport`.**
- Clauses: CL-T10.
- Subtypes: `subtype Request is Evaluation_Pending_C.Request; subtype Result is Evaluation_Pending_C.Result; subtype Row is Evaluation_Pending_C.Row;`
- Helpers: `Request_Pointers`, `Result_Pointers`, `Row_Pointers`, `Byte_Pointers` (pkg_inst), `Extent_Valid`, `Disjoint` (expr), `Copy_Data` (body), from `core/evaluation_pending_c.adb:12-15`, `:67-83`, `:95-103`.

**Transport `Pending_V2_Transport`.**
- Clauses: CL-T11.
- Subtypes: `subtype Request is Evaluation_Pending_V2_C.Request; subtype Result is Evaluation_Pending_V2_C.Result; subtype Row is Evaluation_Pending_V2_C.Row;`
- Helpers: the same names, from `core/evaluation_pending_v2_c.adb:14-17`, `:78-94`, `:116-124`.

**Export `Pending_Decide_V1`.** HEAD = B3 #19.
1. `use Pending_Transport; use type System.Address; use type I64; use type U32; use type E.Count; use System.Storage_Elements; Request_Size : constant I64 := Evaluation_Pending_C.Layout_Size (4); Result_Size : constant I64 := Evaluation_Pending_C.Layout_Size (5); Stride : constant I64 := Evaluation_Pending_C.Layout_Size (3);`
2. `begin if not Extent_Valid (Input, Request_Size, Request'Alignment) or else not Extent_Valid (Output, Result_Size, Result'Alignment) or else not Disjoint (Input, Request_Size, Output, Result_Size) then return 255; end if;`
3. `declare R : constant Request := Request_Pointers.To_Pointer (Input).all; begin if not Evaluation_Pending_C.Header_Valid (R) or else R.Data_Length < 0 or else R.Row_Count < 0 or else Stride <= 0 or else R.Row_Count > I64 (Storage_Offset'Last) / Stride or else not Extent_Valid (R.Data, R.Data_Length, E.Byte'Alignment) or else not Extent_Valid (R.Rows, R.Row_Count * Stride, Row'Alignment) or else not Disjoint (Output, Result_Size, R.Data, R.Data_Length) or else not Disjoint (Output, Result_Size, R.Rows, R.Row_Count * Stride) or else not Evaluation_Pending_C.Request_Fields_Valid (R) then return 255; end if;`
4. `declare A : constant E.Bytes := Copy_Data (R.Data, R.Data_Length); J : E.Journal (1 .. E.Count (R.Row_Count)); begin`
5. `for I in J'Range loop declare V : constant Row := Row_Pointers.To_Pointer (R.Rows + Storage_Offset (I64 (I - 1) * Stride)).all; D : constant Evaluation_Pending_C.Row_Acceptance := Evaluation_Pending_C.Accept_Row (V); begin if not D.Ok then return 255; end if; J (I) := D.Item; end; end loop;`
6. `declare O : constant Evaluation_Pending_C.Decide_Acceptance := Evaluation_Pending_C.Decide_Value (A, J, R); begin if not O.Ok then return 255; end if; Result_Pointers.To_Pointer (Output).all := O.Value; end; return 0; end; end;`
7. `exception when others => return 255; end Pending_Decide_V1;`

**Export `Pending_Decide_V2`.** HEAD = B3 #20.
1. `use Pending_V2_Transport; use type System.Address; use type I64; use type U32; use type E.Count; use System.Storage_Elements; Request_Size : constant I64 := Evaluation_Pending_V2_C.Layout_Size (4); Result_Size : constant I64 := Evaluation_Pending_V2_C.Layout_Size (5); Stride : constant I64 := Evaluation_Pending_V2_C.Layout_Size (3);`
2. `begin if not Extent_Valid (Input, Request_Size, Request'Alignment) or else not Extent_Valid (Output, Result_Size, Result'Alignment) or else not Disjoint (Input, Request_Size, Output, Result_Size) then return 255; end if;`
3. `declare R : constant Request := Request_Pointers.To_Pointer (Input).all; begin if not Evaluation_Pending_V2_C.Header_Valid (R) or else R.Data_Length < 0 or else R.Row_Count < 0 or else Stride <= 0 or else R.Row_Count > I64 (Storage_Offset'Last) / Stride or else not Extent_Valid (R.Data, R.Data_Length, E.Byte'Alignment) or else not Extent_Valid (R.Rows, R.Row_Count * Stride, Row'Alignment) or else not Disjoint (Output, Result_Size, R.Data, R.Data_Length) or else not Disjoint (Output, Result_Size, R.Rows, R.Row_Count * Stride) or else not Evaluation_Pending_V2_C.Request_Fields_Valid (R) then return 255; end if;`
4. `declare A : constant E.Bytes := Copy_Data (R.Data, R.Data_Length); J : V2.Journal (1 .. E.Count (R.Row_Count)); begin`
5. `for I in J'Range loop declare V : constant Row := Row_Pointers.To_Pointer (R.Rows + Storage_Offset (I64 (I - 1) * Stride)).all; D : constant Evaluation_Pending_V2_C.Row_Acceptance := Evaluation_Pending_V2_C.Accept_Row (V); begin if not D.Ok then return 255; end if; J (I) := D.Item; end; end loop;`
6. `declare O : constant Evaluation_Pending_V2_C.Decide_Acceptance := Evaluation_Pending_V2_C.Decide_Value (A, J, R); begin if not O.Ok then return 255; end if; Result_Pointers.To_Pointer (Output).all := O.Value; end; return 0; end; end;`
7. `exception when others => return 255; end Pending_Decide_V2;`

Writes: W19 and W20 (WF-A). Gates: G19a and G20a (`D`), G19b and G20b (`O`). Under D-13 option (i), K6 requires the component transport unit to carry the same scopes N1-identically (B2.3).

### B4.12 `Run_Ledger_Check` (U12, PK-5)

**Transport `Run_Ledger_Transport`.**
- Clauses: CL-T12. Subtypes: none.
- Helpers: `Packet_Access`, `Packet_At`, `Result_Access`, `Result_At`, `Row_Access`, `Row_At`, `Native_Access`, `Native_At`, `Byte_Access`, `Byte_At`, `Shape`, `Array_Shape`, from `core/resource_run_ledger_c_api.adb:14-33`. The `Layout` function stays in SPARK.

**Export.** HEAD = B3 #11.
1. `use Run_Ledger_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int; use type Q.Byte_Count; Row_Size : constant Interfaces.C.size_t := W.Raw_Row'Size / System.Storage_Unit; Native_Size : constant Interfaces.C.size_t := W.Raw_Native'Size / System.Storage_Unit;`
2. `begin if Input_Length /= W.Raw_Packet'Size / System.Storage_Unit or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length) or else To_Integer (Input) mod W.Raw_Packet'Alignment /= 0 or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 or else Arena_Length > Interfaces.C.size_t (Q.Byte_Count'Last) or else (Arena_Length > 0 and then not Shape (Arena, Arena_Length)) or else not Array_Shape (Before_Rows, Before_Count, Row_Size, W.Raw_Row'Alignment) or else not Array_Shape (Proposed_Rows, Proposed_Count, Row_Size, W.Raw_Row'Alignment) or else not Array_Shape (Native, Native_Count, Native_Size, W.Raw_Native'Alignment) then return -1; end if;`
3. `declare Raw : constant W.Raw_Packet := Packet_At (Input).all; Data : Q.Byte_Array (1 .. Q.Byte_Count (Arena_Length)); Before : W.Raw_Row_Array (1 .. Q.Byte_Count (Before_Count)); Proposed : W.Raw_Row_Array (1 .. Q.Byte_Count (Proposed_Count)); Observed : W.Raw_Native_Array (1 .. Q.Byte_Count (Native_Count)); begin for I in Data'Range loop Data (I) := Byte_At (Arena + Storage_Offset (I - 1)).all; end loop; for I in Before'Range loop Before (I) := Row_At (Before_Rows + Storage_Offset (Interfaces.C.size_t (I - 1) * Row_Size)).all; end loop; for I in Proposed'Range loop Proposed (I) := Row_At (Proposed_Rows + Storage_Offset (Interfaces.C.size_t (I - 1) * Row_Size)).all; end loop; for I in Observed'Range loop Observed (I) := Native_At (Native + Storage_Offset (Interfaces.C.size_t (I - 1) * Native_Size)).all; end loop;`
4. `declare O : constant Resource_Run_Ledger_C_API.Check_Acceptance := Resource_Run_Ledger_C_API.Check_Decision (Data, Raw, Before, Proposed, Observed); begin if not O.Ok then return -1; end if; Result_At (Output).all := O.Value; end; end; return 0;`
5. `exception when others => return -1; end Run_Ledger_Check;`

Segments 1–3 keep the S5 sizes, guard, capture, allocations and four unconditional copy loops verbatim (`:192-216`). `W.Well_Formed` is evaluated once in source, inside `Check_Decision`, as the original evaluated it once. Writes: W17 (WF-A). Gates: G17 (`O`).

### B4.13 `Chain_Replay` (U13, PK-5)

**Transport `Chain_Transport`.**
- Clauses: CL-T13. Subtypes: none.
- Helpers: `Anchors_Access`, `Row_Access`, `Result_Access`, `Anchors_At`, `Row_At`, `Result_At`, `Shape`, from `core/worldline-chain_authority_c_api.adb:13-18` and `:60-63`.

**Export.** HEAD = B3 #12.
1. `use Chain_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int; use type A.Q.Byte_Count; Stride : constant Interfaces.C.size_t := W.Raw_Row'Size / System.Storage_Unit;`
2. `begin if Anchors_Length /= W.Raw_Anchors'Size / System.Storage_Unit or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit or else not Shape (Anchors, Anchors_Length) or else not Shape (Output, Output_Length) or else To_Integer (Anchors) mod W.Raw_Anchors'Alignment /= 0 or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 or else Rows_Count > Interfaces.C.size_t (A.Q.Byte_Count'Last) or else Rows_Count > Interfaces.C.size_t'Last / Stride or else Rows_Length /= Rows_Count * Stride or else (Rows_Length > 0 and then (not Shape (Rows, Rows_Length) or else To_Integer (Rows) mod W.Raw_Row'Alignment /= 0)) then return -1; end if;`
3. `declare H : constant W.Raw_Anchors := Anchors_At (Anchors).all; Owned : A.Retained_Rows (1 .. A.Q.Byte_Count (Rows_Count)); begin if not W.Well_Formed (H) then return -1; end if;`
4. `for I in Owned'Range loop declare Raw : constant W.Raw_Row := Row_At (Rows + Storage_Offset (Interfaces.C.size_t (I - 1) * Stride)).all; D : constant Worldline.Chain_Authority_C_API.Row_Acceptance := Worldline.Chain_Authority_C_API.Accept_Row (Raw); begin if not D.Ok then return -1; end if; Owned (I) := D.Item; end; end loop;`
5. `declare RV : constant Worldline.Chain_Authority_C_API.Replay_Acceptance := Worldline.Chain_Authority_C_API.Replay_Value (Owned, H); begin if not RV.Ok then return -1; end if; Result_At (Output).all := RV.Value; end; end; return 0;`
6. `exception when others => return -1; end Chain_Replay;`

Segments 2 and 3 keep the S5 guard, capture, allocation-before-check and anchors gate (`:72-88`). Writes: W18 (WF-A). Gates: G18a (`D`), G18b (`RV`). E3 (B5) additionally binds `Result_At (Output).all := RV.Value;` exactly once in `Chain_Replay` and `return (Ok => True, Value => W.Decide (Owned, H));` exactly once in `Replay_Value`.

### B4.14 `Completion_Decide` (U14, PK-6b)

**Transport `Completion_Transport`** (shared by B4.14–B4.18).
- Clauses: CL-T14. These are S5 `core/evaluation_completion_c.adb:15-31`, except `package E renames Worldline.Evaluation;` (`:19`), which no transported text references (`E.` occurs only in decoders and decisions that stay in SPARK), and except the instance at `:24`, which is a helper.
- Subtypes: `subtype Request is Evaluation_Completion_C.Request; subtype Result is Evaluation_Completion_C.Result; subtype Journal_Row is Evaluation_Completion_C.Journal_Row; subtype Check_Row is Evaluation_Completion_C.Check_Row; subtype History_Row is Evaluation_Completion_C.History_Row; subtype Required_Row is Evaluation_Completion_C.Required_Row; subtype Context_Input is Evaluation_Completion_C.Context_Input; subtype Context_Row is Evaluation_Completion_C.Context_Row; subtype Metadata_Context is Evaluation_Completion_C.Metadata_Context; subtype Row_Metadata is Evaluation_Completion_C.Row_Metadata;`
- Helpers: `Raw_Records`, `Requests`, `Outputs`, `Journals`, `Checks`, `Histories`, `Requirements`, `Octets` (pkg_inst), `Extent_Valid`, `Disjoint`, `Array_Valid` (expr), `Copy_Data` (body), from `:24`, `:32-38`, `:258-278`, `:385-392`.
- Moved subprograms: `Context_Matches` (B4.16) and `Metadata_Base` (B4.18), declared in the specification by profile.
- **Acceptance type names fixed by v4.** v3 named the functions but not their result types. The PK-6a specification declares `Journal_Acceptance`, `Captured_Acceptance`, `Result_Acceptance`, `History_Acceptance`, `Required_Acceptance`, `Raw_Check_Acceptance`, `Raw_Measure_Acceptance`, `Required_Pair_Acceptance` and `Metadata_Row_Acceptance`. Each has a defaulted `Boolean` discriminant `Ok` and a fully defined `True` variant carrying the components v3 §7 U14 lists. A read-only search of the S5 specifications found no existing declaration with these names.

**Export.** HEAD = B3 #13.
1. `use Completion_Transport; use type P.Byte; use type System.Address; use type I64; use type U32; use type P.Count; use type H.Byte_Count; use type T.Decision; use System.Storage_Elements; use type Interfaces.C.int; Input_Size : constant I64 := Request'Object_Size / System.Storage_Unit; Output_Size : constant I64 := Result'Object_Size / System.Storage_Unit; J_Stride : constant I64 := Journal_Row'Object_Size / System.Storage_Unit; C_Stride : constant I64 := Check_Row'Object_Size / System.Storage_Unit; H_Stride : constant I64 := History_Row'Object_Size / System.Storage_Unit; S_Stride : constant I64 := Required_Row'Object_Size / System.Storage_Unit;`
2. `begin if not Extent_Valid (Input, Input_Size, Request'Alignment) or else not Extent_Valid (Output, Output_Size, Result'Alignment) or else not Disjoint (Input, Input_Size, Output, Output_Size) then return 255; end if;`
3. `declare R : constant Request := Requests.To_Pointer (Input).all; begin if not Evaluation_Completion_C.Decide_Header_Valid (R) or else not Extent_Valid (R.Data, R.Data_Length, P.Byte'Alignment) or else not Disjoint (R.Data, R.Data_Length, Output, Output_Size) or else not Array_Valid (R.Journal, R.Journal_Count, J_Stride, Journal_Row'Alignment, Output, Output_Size) or else not Array_Valid (R.Captured_Results, R.Captured_Count, C_Stride, Check_Row'Alignment, Output, Output_Size) or else not Array_Valid (R.Retained_Results, R.Retained_Count, C_Stride, Check_Row'Alignment, Output, Output_Size) or else not Array_Valid (R.History, R.History_Count, H_Stride, History_Row'Alignment, Output, Output_Size) or else not Array_Valid (R.Required, R.Required_Count, S_Stride, Required_Row'Alignment, Output, Output_Size) or else not Evaluation_Completion_C.Decide_Fields_Valid (R) then return 255; end if;`
4. `declare A : constant P.Bytes := Copy_Data (R.Data, R.Data_Length); J : V.Journal (1 .. P.Count (R.Journal_Count)); Measures : Roster.Measured_Array (1 .. P.Count (R.Captured_Count)); Captured : T.Result_Array (1 .. P.Count (R.Captured_Count)); Retained_Results : T.Result_Array (1 .. P.Count (R.Retained_Count)); History : H.History (1 .. H.Byte_Count (R.History_Count)); Required : Roster.Check_Array (1 .. P.Count (R.Required_Count)); Response : Result; Status : Interfaces.C.int; begin`
5. `for I in J'Range loop declare X : constant Journal_Row := Journals.To_Pointer (R.Journal + Storage_Offset (I64 (I - 1) * J_Stride)).all; JA : constant Evaluation_Completion_C.Journal_Acceptance := Evaluation_Completion_C.Accept_Journal_Row (X); begin if not JA.Ok then return 255; end if; J (I) := JA.Item; end; end loop;`
6. `for I in Captured'Range loop declare X : constant Check_Row := Checks.To_Pointer (R.Captured_Results + Storage_Offset (I64 (I - 1) * C_Stride)).all; CR : constant Evaluation_Completion_C.Captured_Acceptance := Evaluation_Completion_C.Accept_Captured_Row (X); begin if not CR.Ok then return 255; end if; Captured (I) := CR.Item; Measures (I) := CR.Measure; end; end loop;`
7. `for I in Retained_Results'Range loop declare X : constant Check_Row := Checks.To_Pointer (R.Retained_Results + Storage_Offset (I64 (I - 1) * C_Stride)).all; RR : constant Evaluation_Completion_C.Result_Acceptance := Evaluation_Completion_C.Accept_Result_Row (X); begin if not RR.Ok then return 255; end if; Retained_Results (I) := RR.Item; end; end loop;`
8. `for I in History'Range loop declare X : constant History_Row := Histories.To_Pointer (R.History + Storage_Offset (I64 (I - 1) * H_Stride)).all; HR : constant Evaluation_Completion_C.History_Acceptance := Evaluation_Completion_C.Accept_History_Row (X); begin if not HR.Ok then return 255; end if; History (I) := HR.Item; end; end loop;`
9. `for I in Required'Range loop declare X : constant Required_Row := Requirements.To_Pointer (R.Required + Storage_Offset (I64 (I - 1) * S_Stride)).all; QR : constant Evaluation_Completion_C.Required_Acceptance := Evaluation_Completion_C.Accept_Required_Row (X); begin if not QR.Ok then return 255; end if; Required (I) := QR.Item; end; end loop;`
10. `Evaluation_Completion_C.Decide_Value (R, A, J, Captured, Measures, Retained_Results, History, Required, Response, Status); if Status /= 0 then return Status; end if; Outputs.To_Pointer (Output).all := Response; return 0; end; end;`
11. `exception when others => return 255; end Completion_Decide;`

**Notes.**
- The six array declarations of segment 4 are the S5 declarations verbatim (`:423-429`). Their bounds give the §5.4 invariants (D-18), and tiling fixes them.
- `use type Interfaces.C.int;` is an added clause (B9.2, class A). It makes `Status /= 0` legal; v3's token 18 needed it but listed no clause.

Writes: W15 (WF-R). Gates: G13a `JA`, G13b `CR`, G13c `RR`, G13d `HR`, G13e `QR`.

### B4.15 `Completion_Raw_Decide` (U14, PK-6b)

**Export.** HEAD = B3 #14.
1. `use Completion_Transport; use type P.Byte; use type System.Address; use type I64; use type U32; use type P.Count; use type H.Byte_Count; use type T.Decision; use System.Storage_Elements; use type Interfaces.C.int; Input_Size : constant I64 := Request'Object_Size / System.Storage_Unit; Output_Size : constant I64 := Result'Object_Size / System.Storage_Unit; Raw_Stride : constant I64 := W.Raw_Record'Object_Size / System.Storage_Unit; J_Stride : constant I64 := Journal_Row'Object_Size / System.Storage_Unit; C_Stride : constant I64 := Check_Row'Object_Size / System.Storage_Unit; H_Stride : constant I64 := History_Row'Object_Size / System.Storage_Unit; S_Stride : constant I64 := Required_Row'Object_Size / System.Storage_Unit;`
2. `begin if not Extent_Valid (Input, Input_Size, Request'Alignment) or else not Extent_Valid (Output, Output_Size, Result'Alignment) or else not Disjoint (Input, Input_Size, Output, Output_Size) then return 255; end if;`
3. `declare R : constant Request := Requests.To_Pointer (Input).all; begin if not Evaluation_Completion_C.Raw_Header_Valid (R) or else not Extent_Valid (R.Data, R.Data_Length, P.Byte'Alignment) or else not Disjoint (R.Data, R.Data_Length, Output, Output_Size) or else not Array_Valid (R.Journal, R.Journal_Count, J_Stride, Journal_Row'Alignment, Output, Output_Size) or else not Array_Valid (R.Captured_Results, R.Captured_Count, C_Stride, Check_Row'Alignment, Output, Output_Size) or else not Array_Valid (R.Retained_Results, R.Retained_Count, C_Stride, Check_Row'Alignment, Output, Output_Size) or else not Array_Valid (R.History, R.History_Count, H_Stride, History_Row'Alignment, Output, Output_Size) or else not Array_Valid (R.Required, R.Required_Count, S_Stride, Required_Row'Alignment, Output, Output_Size) or else not Array_Valid (Raw_Rows, R.Captured_Count, Raw_Stride, W.Raw_Record'Alignment, Output, Output_Size) or else not Array_Valid (Confinements, R.Captured_Count, 1, P.Byte'Alignment, Output, Output_Size) or else not Evaluation_Completion_C.Raw_Fields_Valid (R) then return 255; end if;`
4. `declare A : constant P.Bytes := Copy_Data (R.Data, R.Data_Length); J : V.Journal (1 .. P.Count (R.Journal_Count)); Measures : Raw_Roster.Measured_Array (1 .. P.Count (R.Captured_Count)); Captured : T.Result_Array (1 .. P.Count (R.Captured_Count)); Retained_Results : T.Result_Array (1 .. P.Count (R.Retained_Count)); History : H.History (1 .. H.Byte_Count (R.History_Count)); Required : Roster.Check_Array (1 .. P.Count (R.Required_Count)); Response : Result; Status : Interfaces.C.int; begin`
5. `for I in J'Range loop declare X : constant Journal_Row := Journals.To_Pointer (R.Journal + Storage_Offset (I64 (I - 1) * J_Stride)).all; JA : constant Evaluation_Completion_C.Journal_Acceptance := Evaluation_Completion_C.Accept_Journal_Row (X); begin if not JA.Ok then return 255; end if; J (I) := JA.Item; end; end loop;`
6. `for I in Captured'Range loop declare X : constant Check_Row := Checks.To_Pointer (R.Captured_Results + Storage_Offset (I64 (I - 1) * C_Stride)).all; KA : constant Evaluation_Completion_C.Raw_Check_Acceptance := Evaluation_Completion_C.Accept_Raw_Check_Row (X); begin if not KA.Ok then return 255; end if; Captured (I) := KA.Item; declare Wire : constant W.Raw_Record := Raw_Records.To_Pointer (Raw_Rows + Storage_Offset (I64 (I - 1) * Raw_Stride)).all; Confined : constant P.Byte := Octets.To_Pointer (Confinements + Storage_Offset (I - 1)).all; MA : constant Evaluation_Completion_C.Raw_Measure_Acceptance := Evaluation_Completion_C.Accept_Raw_Measure (KA.Item, KA.Declared, Wire, Confined); begin if not MA.Ok then return 255; end if; Measures (I) := MA.Item; end; end; end loop;`
7. `for I in Retained_Results'Range loop declare X : constant Check_Row := Checks.To_Pointer (R.Retained_Results + Storage_Offset (I64 (I - 1) * C_Stride)).all; RR : constant Evaluation_Completion_C.Result_Acceptance := Evaluation_Completion_C.Accept_Result_Row (X); begin if not RR.Ok then return 255; end if; Retained_Results (I) := RR.Item; end; end loop;`
8. `for I in History'Range loop declare X : constant History_Row := Histories.To_Pointer (R.History + Storage_Offset (I64 (I - 1) * H_Stride)).all; HR : constant Evaluation_Completion_C.History_Acceptance := Evaluation_Completion_C.Accept_History_Row (X); begin if not HR.Ok then return 255; end if; History (I) := HR.Item; end; end loop;`
9. `for I in Required'Range loop declare X : constant Required_Row := Requirements.To_Pointer (R.Required + Storage_Offset (I64 (I - 1) * S_Stride)).all; QR : constant Evaluation_Completion_C.Required_Acceptance := Evaluation_Completion_C.Accept_Required_Row (X); begin if not QR.Ok then return 255; end if; Required (I) := QR.Item; end; end loop;`
10. `Evaluation_Completion_C.Raw_Decide_Value (R, A, J, Captured, Measures, Retained_Results, History, Required, Response, Status); if Status /= 0 then return Status; end if; Outputs.To_Pointer (Output).all := Response; return 0; end; end;`
11. `exception when others => return 255; end Completion_Raw_Decide;`

**Notes.**
- Segment 6 keeps the S5 staging (`:597-616`): check row `I` is read and accepted before raw wire `I` and confinement `I` are read.
- The genuine post-decision 255 (`:657-671`) is returned through `Status` by `Raw_Decide_Value` (§5.3). Segment 10's `return Status` is therefore real, not dead.

Writes: W16 (WF-R). Gates: G14a `JA`, G14b `KA`, G14c `MA`, G14d `RR`, G14e `HR`, G14f `QR`.

### B4.16 `Completion_Transport.Context_Matches` (U14, PK-6b; moved helper)

HEAD (literal): `function Context_Matches (Input, Context, Collapse, Agent : System.Address; Agent_Confinement : Interfaces.Unsigned_8) return Interfaces.C.int is`
1. `package CA renames Worldline.Evaluation_Authority; package CW renames Worldline.Collapse_Wire; package Contexts is new System.Address_To_Access_Conversions (Context_Input); package Context_Items is new System.Address_To_Access_Conversions (Context_Row); package Collapse_Requests is new System.Address_To_Access_Conversions (CW.Raw_Request); use type W.Raw_Record; use type Evaluation_Completion_C.Join_Verdict; CS : constant I64 := Context_Input'Object_Size / System.Storage_Unit; RS : constant I64 := Context_Row'Object_Size / System.Storage_Unit; ISz : constant I64 := Check_Row'Object_Size / System.Storage_Unit; QS : constant I64 := Required_Row'Object_Size / System.Storage_Unit;`
2. `begin Diagnostic_Transport.Mark ("completion.context.enter"); if not Extent_Valid (Input, Request'Object_Size / System.Storage_Unit, Request'Alignment) or else not Extent_Valid (Context, CS, Context_Input'Alignment) or else not Extent_Valid (Collapse, CW.Raw_Request'Object_Size / System.Storage_Unit, CW.Raw_Request'Alignment) or else not Extent_Valid (Agent, W.Raw_Record'Object_Size / System.Storage_Unit, W.Raw_Record'Alignment) then Diagnostic_Transport.Mark ("completion.context.input-extents-rejected"); return 255; end if;`
3. `declare R : constant Request := Requests.To_Pointer (Input).all; X : constant Context_Input := Contexts.To_Pointer (Context).all; Raw_Collapse : constant CW.Raw_Request := Collapse_Requests.To_Pointer (Collapse).all; Raw_Agent : constant W.Raw_Record := Raw_Records.To_Pointer (Agent).all; begin if not Evaluation_Completion_C.Context_Header_Valid (R, X) or else not Extent_Valid (X.Data, X.Data_Length, P.Byte'Alignment) or else not Evaluation_Completion_C.Context_Fields_Valid (R, X) or else not Extent_Valid (R.Data, R.Data_Length, P.Byte'Alignment) or else not Array_Valid (X.Rows, X.Row_Count, RS, Context_Row'Alignment, Context, CS) or else not Array_Valid (R.Captured_Results, R.Captured_Count, ISz, Check_Row'Alignment, Context, CS) or else not Array_Valid (R.Required, R.Required_Count, QS, Required_Row'Alignment, Context, CS) or else not Array_Valid (X.Required, X.Required_Count, QS, Required_Row'Alignment, Context, CS) or else not Evaluation_Completion_C.Context_Agent_Matches (X, Raw_Agent, Agent_Confinement) then Diagnostic_Transport.Mark ("completion.context.transport-guard-rejected"); return 255; end if;`
4. `Diagnostic_Transport.Mark ("completion.context.copy-arenas"); declare Data : constant P.Bytes := Copy_Data (R.Data, R.Data_Length); Context_Data : constant P.Bytes := Copy_Data (X.Data, X.Data_Length); Rows : T.Result_Array (1 .. P.Count (R.Captured_Count)); Joined : CA.Context_Rows (Rows'Range); Required, Expected_Required : Roster.Check_Array (1 .. P.Count (R.Required_Count)); begin Diagnostic_Transport.Mark ("completion.context.arenas-copied");`
5. `declare FA : constant Evaluation_Completion_C.Context_Fields_Acceptance := Evaluation_Completion_C.Accept_Context_Fields (X); begin if not FA.Ok then Diagnostic_Transport.Value ("completion.context.field-rejected", FA.Rejected_Position); return 255; end if;`
6. `for I in Rows'Range loop declare Original : constant Check_Row := Checks.To_Pointer (R.Captured_Results + Storage_Offset (I64 (I - 1) * ISz)).all; Owned : constant Context_Row := Context_Items.To_Pointer (X.Rows + Storage_Offset (I64 (I - 1) * RS)).all; RA : constant Evaluation_Completion_C.Context_Row_Acceptance := Evaluation_Completion_C.Accept_Context_Row (Original, Owned); begin case RA.Verdict is when Evaluation_Completion_C.Row_Rejected => Diagnostic_Transport.Value ("completion.context.row-rejected", I64 (I)); return 255; when Evaluation_Completion_C.Row_Field_Rejected => Diagnostic_Transport.Value ("completion.context.row-field-row", I64 (I)); Diagnostic_Transport.Value ("completion.context.row-field-rejected", RA.Rejected_Field_Position); return 255; when Evaluation_Completion_C.Row_Accepted => Rows (I) := RA.Row; Joined (I) := RA.Joined; end case; end; end loop;`
7. `for I in Required'Range loop declare Original : constant Required_Row := Requirements.To_Pointer (R.Required + Storage_Offset (I64 (I - 1) * QS)).all; Owned : constant Required_Row := Requirements.To_Pointer (X.Required + Storage_Offset (I64 (I - 1) * QS)).all; QA : constant Evaluation_Completion_C.Required_Pair_Acceptance := Evaluation_Completion_C.Accept_Required_Pair (Original, Owned); begin if not QA.Ok then Diagnostic_Transport.Value ("completion.context.required-rejected", I64 (I)); return 255; end if; Required (I) := QA.Item; Expected_Required (I) := QA.Expected; end; end loop;`
8. `Diagnostic_Transport.Mark ("completion.context.join"); declare V : constant Evaluation_Completion_C.Join_Verdict := Evaluation_Completion_C.Context_Join_Value (R, X, Raw_Collapse, Data, Context_Data, FA.Expected, FA.Observed, Rows, Joined, Required, Expected_Required); begin if V = Evaluation_Completion_C.Join_Malformed then return 255; end if; Diagnostic_Transport.Value ("completion.context.join-result", I64 (Evaluation_Completion_C.Join_Code (V = Evaluation_Completion_C.Join_Match))); return Evaluation_Completion_C.Join_Code (V = Evaluation_Completion_C.Join_Match); end; end; end; end;`
9. `exception when Error : others => Diagnostic_Transport.Exception_Text ("completion.context", Error); return 255; end Context_Matches;`

**Notes.**
- The local `Convert_Optional` (S5 `:746-748`) moves to SPARK (§5.2), and the locals `Expected, Observed` (S5 `:789`) are replaced by `FA`'s payload.
- `use type Evaluation_Completion_C.Join_Verdict;` is an added clause (class A). It makes `V = …` legal; v3 tokens 21–23 needed it but listed no clause.
- The site order equals B6.

Writes: none (only Ada-owned locals). Gates: G16a `FA`, G16b `RA` (case gate), G16c `QA`.

### B4.17 `Completion_Metadata_Matches` (U14, PK-6b)

**Export.** HEAD = B3 #15.
1. `use Completion_Transport; use type P.Byte; use type System.Address; use type I64; use type U32; use type P.Count; use type H.Byte_Count; use type T.Decision; use System.Storage_Elements; package CA renames Worldline.Evaluation_Authority; package Inputs is new System.Address_To_Access_Conversions (Metadata_Context); package Metadata_Items is new System.Address_To_Access_Conversions (Row_Metadata); CS : constant I64 := Metadata_Context'Object_Size / System.Storage_Unit; RS : constant I64 := Row_Metadata'Object_Size / System.Storage_Unit; ISz : constant I64 := Check_Row'Object_Size / System.Storage_Unit;`
2. `begin Diagnostic_Transport.Mark ("completion.metadata.enter"); if not Extent_Valid (Input, Request'Object_Size / System.Storage_Unit, Request'Alignment) or else not Extent_Valid (Context, CS, Metadata_Context'Alignment) then Diagnostic_Transport.Mark ("completion.metadata.input-extents-rejected"); return 255; end if;`
3. `declare R : constant Request := Requests.To_Pointer (Input).all; X : constant Metadata_Context := Inputs.To_Pointer (Context).all; begin if not Evaluation_Completion_C.Metadata_Header_Valid (R, X) or else not Extent_Valid (X.Data, X.Data_Length, P.Byte'Alignment) or else not Extent_Valid (R.Data, R.Data_Length, P.Byte'Alignment) or else not Array_Valid (X.Rows, X.Row_Count, RS, Row_Metadata'Alignment, Context, CS) or else not Array_Valid (R.Captured_Results, R.Captured_Count, ISz, Check_Row'Alignment, Context, CS) then Diagnostic_Transport.Mark ("completion.metadata.transport-guard-rejected"); return 255; end if;`
4. `Diagnostic_Transport.Mark ("completion.metadata.copy-arenas"); declare Data : constant P.Bytes := Copy_Data (R.Data, R.Data_Length); Projected_Data : constant P.Bytes := Copy_Data (X.Data, X.Data_Length); Rows : T.Result_Array (1 .. P.Count (R.Captured_Count)); Projected : CA.Row_Metadata_Array (Rows'Range); begin Diagnostic_Transport.Mark ("completion.metadata.arenas-copied");`
5. `for I in Rows'Range loop declare Original : constant Check_Row := Checks.To_Pointer (R.Captured_Results + Storage_Offset (I64 (I - 1) * ISz)).all; Owned : constant Row_Metadata := Metadata_Items.To_Pointer (X.Rows + Storage_Offset (I64 (I - 1) * RS)).all; MA : constant Evaluation_Completion_C.Metadata_Row_Acceptance := Evaluation_Completion_C.Accept_Metadata_Row (Original, Owned); begin if not MA.Ok then Diagnostic_Transport.Value ("completion.metadata.row-rejected", I64 (I)); return 255; end if; Rows (I) := MA.Row; Projected (I) := MA.Projected; end; end loop;`
6. `Diagnostic_Transport.Mark ("completion.metadata.join"); declare Joined_Metadata : constant Boolean := CA.Join_Metadata (Data, Projected_Data, Rows, Projected); begin Diagnostic_Transport.Value ("completion.metadata.join-result", Boolean'Pos (Joined_Metadata)); return Evaluation_Completion_C.Join_Code (Joined_Metadata); end; end; end;`
7. `exception when Error : others => Diagnostic_Transport.Exception_Text ("completion.metadata", Error); return 255; end Completion_Metadata_Matches;`

The local `Optional` (S5 `:917-919`) moves to SPARK. Writes: none. Gates: G15 `MA`.

### B4.18 `Completion_Transport.Metadata_Base` (U14, PK-6b; moved helper)

HEAD (literal): `function Metadata_Base (Context : System.Address) return System.Address is`
1. `package Inputs is new System.Address_To_Access_Conversions (Metadata_Context);`
2. `begin if not Extent_Valid (Context, Metadata_Context'Object_Size / System.Storage_Unit, Metadata_Context'Alignment) then return System.Null_Address; end if; declare X : constant Metadata_Context := Inputs.To_Pointer (Context).all; begin if not Evaluation_Completion_C.Metadata_Version_Valid (X) or else not Extent_Valid (X.Base, Context_Input'Object_Size / System.Storage_Unit, Context_Input'Alignment) then return System.Null_Address; end if; return X.Base; end; exception when others => return System.Null_Address; end Metadata_Base;`

Writes: none. Gates: none.

### B4.19 `Native_Diagnostic_Control` (RC1, PK-6b; carried design, tile added)

HEAD = B3 #16.
1. `Code : U32; Emit_Begin : Boolean;`
2. `begin case Evaluation_Completion_C.Diagnostic_Control_Of (Enable) is when Evaluation_Completion_C.Start_Trace => Evaluation_Completion_C.Diagnostic_Start (Code, Emit_Begin); if Emit_Begin then Diagnostic_Transport.Mark ("trace.begin"); end if; return Code; when Evaluation_Completion_C.Stop_Trace => Diagnostic_Transport.Mark ("trace.end"); Evaluation_Completion_C.Diagnostic_Stop (Code); return Code; when Evaluation_Completion_C.Invalid_Control => return Evaluation_Completion_C.Diagnostic_Invalid_Code; end case; end Native_Diagnostic_Control;`

**Notes.**
- HEAD plus the two segments equals the N1 form of v3 DESIGN §4.4 (lines 561-577), derived by a read-only script. v3's five B4.19 tokens are substrings of it.
- Clauses: none. The word `exception` occurs 0 times: there is no handler, as in the original (`core/evaluation_completion_c.adb:73-88`).

### B4.20 `Finalization_Decide` (U15, PK-6b)

**Transport `Finalization_Transport`** (shared by B4.20–B4.22).
- Clauses: CL-T15. These are S5 `core/evaluation_finalization_c.adb:9-27`, except `package T renames F.T;` (`:10`) and `package H renames F.H;` (`:13`): every `T.` and `H.` use in S5 lies in decoders and decisions that move to SPARK.
- Subtypes: `subtype Request is Evaluation_Finalization_C.Request; subtype Result is Evaluation_Finalization_C.Result; subtype Row is Evaluation_Finalization_C.Row; subtype Required_Row is Evaluation_Finalization_C.Required_Row;`
- Helpers: `Requests`, `Outputs`, `Rows`, `Plans`, `Octets` (pkg_inst), `Extent_Valid`, `Disjoint`, `Array_Valid` (expr), `Copy_Data` (body), from `:28-32`, `:35-55`, `:112-119`.
- Moved subprogram: `Final_Context_Matches` (B4.21).

**Export.** HEAD = B3 #17.
1. `use Finalization_Transport; use type Interfaces.C.int; use type Authority.Raw_Dependency; use type System.Address; use type I64; use type U32; use type U8; use type P.Count; use type F.Capture_Decision; use type F.Seal_Decision; use System.Storage_Elements; Input_Size : constant I64 := Request'Object_Size / System.Storage_Unit; Output_Size : constant I64 := Result'Object_Size / System.Storage_Unit; Row_Size : constant I64 := Row'Object_Size / System.Storage_Unit; Plan_Size : constant I64 := Required_Row'Object_Size / System.Storage_Unit;`
2. `begin Diagnostic_Transport.Mark ("finalization.decide.enter"); if not Extent_Valid (Input, Input_Size, Request'Alignment) or else not Extent_Valid (Output, Output_Size, Result'Alignment) or else not Disjoint (Input, Input_Size, Output, Output_Size) then Diagnostic_Transport.Mark ("finalization.decide.input-extents-rejected"); return 255; end if;`
3. `declare X : constant Request := Requests.To_Pointer (Input).all; begin if not Evaluation_Finalization_C.Request_Header_Valid (X) or else not Extent_Valid (X.Data, X.Data_Length, P.Byte'Alignment) or else not Disjoint (X.Data, X.Data_Length, Output, Output_Size) or else not Array_Valid (X.Required, X.Required_Count, Plan_Size, Required_Row'Alignment, Output, Output_Size) or else not Array_Valid (X.Rows, X.Row_Count, Row_Size, Row'Alignment, Output, Output_Size) or else not Evaluation_Finalization_C.Request_Fields_Valid (X) then Diagnostic_Transport.Mark ("finalization.decide.transport-guard-rejected"); return 255; end if;`
4. `Diagnostic_Transport.Mark ("finalization.decide.copy-arena"); declare A : constant P.Bytes := Copy_Data (X.Data, X.Data_Length); Required : R.Check_Array (1 .. P.Count (X.Required_Count)); Captured : F.Start_Rows (1 .. P.Count (X.Row_Count)); O : Evaluation_Finalization_C.Decide_Acceptance; begin`
5. `for K in Required'Range loop declare Q : constant Evaluation_Finalization_C.Required_Row := Finalization_Transport.Plans.To_Pointer (X.Required + Storage_Offset (I64 (K - 1) * Plan_Size)).all; PA : constant Evaluation_Finalization_C.Plan_Acceptance := Evaluation_Finalization_C.Accept_Plan (Q); begin if not PA.Ok then Diagnostic_Transport.Value ("finalization.decide.required-rejected", I64 (K)); return 255; end if; Required (K) := PA.Item; end; end loop;`
6. `if Evaluation_Finalization_C.Needs_Rows (X) then for K in Captured'Range loop declare Q : constant Evaluation_Finalization_C.Row := Finalization_Transport.Rows.To_Pointer (X.Rows + Storage_Offset (I64 (K - 1) * Row_Size)).all; RA : constant Evaluation_Finalization_C.Row_Acceptance := Evaluation_Finalization_C.Accept_Row (Q); begin if not RA.Ok then Diagnostic_Transport.Value ("finalization.decide.row-rejected", I64 (K)); return 255; end if; Captured (K) := RA.Item; end; end loop; O := Evaluation_Finalization_C.Decide_Rows_Value (X, A, Required, Captured); else O := Evaluation_Finalization_C.Decide_No_Rows_Value (X, A, Required); end if; if not O.Ok then return 255; end if;`
7. `Diagnostic_Transport.Value ("finalization.decide.reason", I64 (O.Value.Reason)); Diagnostic_Transport.Value ("finalization.decide.promotion", I64 (O.Value.Promotion)); Outputs.To_Pointer (Output).all := O.Value; return 0; end; end;`
8. `exception when Error : others => Diagnostic_Transport.Exception_Text ("finalization.decide", Error); return 255; end Finalization_Decide;`

**Notes.**
- Segment 6 is the N1 form of the carried §5.1 transport block (v3 DESIGN lines 729-749), derived by a read-only script. It is the RC2-closed design text.
- `Captured` is allocated for every operation (segment 4, S5 `:162`). Operations 0 and 1 neither read rows nor pass `Captured`.
- The loop parameter `K` hides the use-visible renaming `K` inside the loops, as the S5 loop parameter hid the directly visible renaming (S5 `:168`, `:189`).

Writes: W21 (WF-X). Gates: G21a `PA`, G21b `RA`, G21c `O` (exclusive-assignment gate).

### B4.21 `Finalization_Transport.Final_Context_Matches` (U15, PK-6b; moved helper)

HEAD (literal): `function Final_Context_Matches (Input, Metadata, Collapse, Agent : System.Address; Agent_Confinement : U8) return Boolean is`
1. `Native : aliased Evaluation_Finalization_C.Result := Evaluation_Finalization_C.Initial_Result; Plan_Size : constant I64 := Required_Row'Object_Size / System.Storage_Unit; Row_Size : constant I64 := Row'Object_Size / System.Storage_Unit; type Check_Array is array (P.Index range <>) of aliased K.Check_Row with Convention => C; type Plan_Array is array (P.Index range <>) of aliased K.Required_Row with Convention => C; Seal_Status : Interfaces.C.int;`
2. `begin Diagnostic_Transport.Mark ("finalization.context.enter"); Seal_Status := Finalization_Decide (Input, Native'Address); if not Evaluation_Finalization_C.Final_Seal_Ready (Seal_Status, Native) then Diagnostic_Transport.Mark ("finalization.context.seal-rejected"); return False; end if;`
3. `declare X : constant Request := Requests.To_Pointer (Input).all; begin if not Evaluation_Finalization_C.Final_Plans_Valid (X) then Diagnostic_Transport.Mark ("finalization.context.required-extent-rejected"); return False; end if;`
4. `declare Projected_Rows : aliased Check_Array (1 .. P.Count (X.Row_Count)); Projected_Plans : aliased Plan_Array (1 .. P.Count (X.Start.Required.Length)); Projection : aliased K.Request; begin for I in Projected_Rows'Range loop declare Original : constant Row := Rows.To_Pointer (X.Rows + Storage_Offset (I64 (I - 1) * Row_Size)).all; begin Projected_Rows (I) := Evaluation_Finalization_C.Final_Projected_Row (X, Original); end; end loop; for I in Projected_Plans'Range loop Projected_Plans (I) := Plans.To_Pointer (X.Required + Storage_Offset ((X.Start.Required.First - 1 + I64 (I - 1)) * Plan_Size)).all; end loop;`
5. `Projection := Evaluation_Finalization_C.Final_Projection (X, Native, Projected_Rows'Address, Projected_Plans'Address); Diagnostic_Transport.Mark ("finalization.context.projected"); declare Context_Result : constant Interfaces.C.int := Completion_Transport.Context_Matches (Projection'Address, Completion_Transport.Metadata_Base (Metadata), Collapse, Agent, Agent_Confinement); begin Diagnostic_Transport.Value ("finalization.context.context-result", I64 (Context_Result)); if Context_Result /= 1 then return False; end if; declare Metadata_Result : constant Interfaces.C.int := Completion_Metadata_Matches (Projection'Address, Metadata); begin Diagnostic_Transport.Value ("finalization.context.metadata-result", I64 (Metadata_Result)); return Metadata_Result = 1; end; end; end; end;`
6. `exception when Error : others => Diagnostic_Transport.Exception_Text ("finalization.context", Error); return False; end Final_Context_Matches;`

**Notes.**
- `Seal_Status` is assigned after the enter mark, so `Finalization_Decide` is still called first, before `Native` is read, as in S5's left-to-right `or else` (`:273`).
- The local array types are S5 `:267-270` verbatim.
- `Bound` and `Empty_Capture` (S5 `:294-297`) are built inside `Final_Projected_Row` and `Final_Projection` (v3 §7 U15).

Writes: none foreign. `Projected_Rows`, `Projected_Plans`, `Projection` and `Native` are Ada-owned (D-26). Gates: none.

### B4.22 `Finalization_Decide_Mixed` (U15, PK-6b)

**Export.** HEAD = B3 #18.
1. `use Finalization_Transport; use type Interfaces.C.int; use type Authority.Raw_Dependency; use type System.Address; use type I64; use type U32; use type U8; use type P.Count; use type F.Capture_Decision; use type F.Seal_Decision; use System.Storage_Elements; package Collapse_Requests is new System.Address_To_Access_Conversions (CW.Raw_Request); package Raw_Records is new System.Address_To_Access_Conversions (W.Raw_Record); P_Ready, S_Ready, Agent_Ready : U8 := 0;`
2. `function Read_Ready (Kind : U32; Input, Raw, Confined : System.Address) return Evaluation_Finalization_C.Readiness_Result is begin case Evaluation_Finalization_C.Kind_Of (Kind) is when Evaluation_Finalization_C.Absent_Source => return (Valid => True, Ready => 0); when Evaluation_Finalization_C.Ordinary_Source => declare Ordinary : aliased Evaluation_Completion_C.Result := Evaluation_Completion_C.Initial_Response; Status : constant Interfaces.C.int := Completion_Raw_Decide (Input, Raw, Confined, Ordinary'Address); begin return Evaluation_Finalization_C.Ordinary_Readiness (Status, Ordinary); end; when Evaluation_Finalization_C.Finalized_Source => declare Finalized : aliased Evaluation_Finalization_C.Result := Evaluation_Finalization_C.Initial_Result; Status : constant Interfaces.C.int := Finalization_Decide (Input, Finalized'Address); R1 : constant Evaluation_Finalization_C.Readiness_Result := Evaluation_Finalization_C.Finalized_Readiness (Status, Finalized); begin if not R1.Valid then return R1; end if; declare X : constant Request := Requests.To_Pointer (Input).all; begin return Evaluation_Finalization_C.Finalized_Operation_Readiness (X, Finalized); end; end; when Evaluation_Finalization_C.Invalid_Source => return (Valid => False, Ready => 0); end case; end Read_Ready;`
3. `function Context_Joined (Kind : U32; Input, Metadata : System.Address) return Boolean is begin case Evaluation_Finalization_C.Kind_Of (Kind) is when Evaluation_Finalization_C.Ordinary_Source => return Completion_Transport.Context_Matches (Input, Completion_Transport.Metadata_Base (Metadata), Collapse, Agent, Agent_Confinement) = 1; when Evaluation_Finalization_C.Finalized_Source => return Final_Context_Matches (Input, Metadata, Collapse, Agent, Agent_Confinement); when Evaluation_Finalization_C.Absent_Source | Evaluation_Finalization_C.Invalid_Source => return False; end case; end Context_Joined;`
4. `begin Diagnostic_Transport.Mark ("finalization.mixed.enter"); if not Extent_Valid (Collapse, CW.Raw_Request'Object_Size / System.Storage_Unit, CW.Raw_Request'Alignment) then Diagnostic_Transport.Mark ("finalization.mixed.collapse-extent-rejected"); return CW.Invalid_Request; end if;`
5. `declare Bound : constant CW.Raw_Request := Collapse_Requests.To_Pointer (Collapse).all; Needed : constant Authority.Raw_Dependency := Authority.Dependencies (Bound); Decision : U8; begin if Needed = Authority.Invalid_Collapse then Diagnostic_Transport.Mark ("finalization.mixed.dependency-rejected"); return CW.Invalid_Request; end if;`
6. `if Authority.Needs_Primary (Needed) then declare Observed : constant Evaluation_Finalization_C.Readiness_Result := Read_Ready (Primary_Kind, Primary, Primary_Raw, Primary_Confinement); begin P_Ready := Observed.Ready; if not Observed.Valid then Diagnostic_Transport.Mark ("finalization.mixed.primary-ready-rejected"); return CW.Invalid_Request; end if; end; end if; if Authority.Needs_Staged (Needed) then declare Observed : constant Evaluation_Finalization_C.Readiness_Result := Read_Ready (Staged_Kind, Staged, Staged_Raw, Staged_Confinement); begin S_Ready := Observed.Ready; if not Observed.Valid then Diagnostic_Transport.Mark ("finalization.mixed.staged-ready-rejected"); return CW.Invalid_Request; end if; end; end if; Diagnostic_Transport.Value ("finalization.mixed.primary-ready", I64 (P_Ready)); Diagnostic_Transport.Value ("finalization.mixed.staged-ready", I64 (S_Ready));`
7. `if Authority.Needs_Agent (Needed) and then Agent /= System.Null_Address then if not Extent_Valid (Agent, W.Raw_Record'Object_Size / System.Storage_Unit, W.Raw_Record'Alignment) then Diagnostic_Transport.Mark ("finalization.mixed.agent-extent-rejected"); return CW.Invalid_Request; end if; declare Owned_Agent : constant W.Raw_Record := Raw_Records.To_Pointer (Agent).all; begin Agent_Ready := Evaluation_Finalization_C.Agent_Readiness (Owned_Agent, Agent_Confinement); if Agent_Ready = W.Invalid_Record then Diagnostic_Transport.Mark ("finalization.mixed.agent-record-rejected"); return CW.Invalid_Request; end if; end; end if; Diagnostic_Transport.Value ("finalization.mixed.agent-ready", I64 (Agent_Ready));`
8. `if Evaluation_Finalization_C.Context_Join_Needed (Agent_Ready, P_Ready) and then not Context_Joined (Primary_Kind, Primary, Primary_Context) then Diagnostic_Transport.Mark ("finalization.mixed.primary-context-rejected"); return CW.Invalid_Request; end if; if Evaluation_Finalization_C.Context_Join_Needed (Agent_Ready, S_Ready) and then not Context_Joined (Staged_Kind, Staged, Staged_Context) then Diagnostic_Transport.Mark ("finalization.mixed.staged-context-rejected"); return CW.Invalid_Request; end if;`
9. `Decision := Evaluation_Finalization_C.Mixed_Collapse_Decision (Bound, Agent_Ready, P_Ready, S_Ready); Diagnostic_Transport.Value ("finalization.mixed.collapse-decision", I64 (Decision)); if not Evaluation_Finalization_C.Mixed_Authorized (Decision) then return Decision; end if; if Evaluation_Finalization_C.Mixed_Metadata_Needed (Needed, True, Primary_Kind) and then Completion_Metadata_Matches (Primary, Primary_Context) /= 1 then Diagnostic_Transport.Mark ("finalization.mixed.primary-metadata-rejected"); return CW.Invalid_Request; end if; if Evaluation_Finalization_C.Mixed_Metadata_Needed (Needed, False, Staged_Kind) and then Completion_Metadata_Matches (Staged, Staged_Context) /= 1 then Diagnostic_Transport.Mark ("finalization.mixed.staged-metadata-rejected"); return CW.Invalid_Request; end if; return Decision; end;`
10. `exception when Error : others => Diagnostic_Transport.Exception_Text ("finalization.mixed", Error); return CW.Invalid_Request; end Finalization_Decide_Mixed;`

**Notes.**
- `Bound` is a constant. The S5 in-place mutation (`:485-486`) is replaced by the delta aggregate inside `Mixed_Collapse_Decision` (v3 §7 U15). Assignments `Bound.` therefore occur 0 times.
- `Read_Ready` and `Context_Joined` have no handlers, as in S5.
- The site order equals B6.
- `R1` and `Observed` are plain (undiscriminated) `Readiness_Result` records, so they have no discriminant gate. Their `Valid` component is tested before return as in S5.

Writes: none foreign. Nested exports write Ada-owned `Ordinary` and `Finalized` (D-26). Gates: none.

### B4.23 `Authority_Glue` edits (residual; PK-6b; R-GLUE)

The two functions are pre-existing residual code. Only the nine recorded edits apply (JACKAL J16):

| Edit | Function (S5 lines) | Old N1 text (occurs once in S5) | New N1 text (occurs once in the successor) |
|---|---|---|---|
| GE1 | `Decide_Raw_Context` (`:784-785`) | `K.Raw_Decide (Primary, Primary_Raw, Primary_Confinement, P_Result'Address)` | `Completion_Raw_Decide (Primary, Primary_Raw, Primary_Confinement, P_Result'Address)` |
| GE2 | `Decide_Raw_Context` (`:791-792`) | `K.Raw_Decide (Staged, Staged_Raw, Staged_Confinement, S_Result'Address)` | `Completion_Raw_Decide (Staged, Staged_Raw, Staged_Confinement, S_Result'Address)` |
| GE3 | `Decide_Raw_Context` (`:810-811`) | `K.Context_Matches (Primary, Primary_Context, Request, Agent, Agent_Confinement)` | `Completion_Transport.Context_Matches (Primary, Primary_Context, Request, Agent, Agent_Confinement)` |
| GE4 | `Decide_Raw_Context` (`:813-814`) | `K.Context_Matches (Staged, Staged_Context, Request, Agent, Agent_Confinement)` | `Completion_Transport.Context_Matches (Staged, Staged_Context, Request, Agent, Agent_Confinement)` |
| GE5 | `Decide_Raw_Metadata` (`:852`) | `K.Metadata_Base (Primary_Context)` | `Completion_Transport.Metadata_Base (Primary_Context)` |
| GE6 | `Decide_Raw_Metadata` (`:855`) | `K.Metadata_Base (Staged_Context)` | `Completion_Transport.Metadata_Base (Staged_Context)` |
| GE7 | `Decide_Raw_Metadata` (`:866-867`) | `K.Metadata_Matches (Primary, Primary_Context)` | `Completion_Metadata_Matches (Primary, Primary_Context)` |
| GE8 | `Decide_Raw_Metadata` (`:869-870`) | `K.Metadata_Matches (Staged, Staged_Context)` | `Completion_Metadata_Matches (Staged, Staged_Context)` |
| GE9 (R-DEL-1) | `Decide_Raw_Metadata` (`:835-837`) | `return Byte is package K renames Evaluation_Completion_C; use type Interfaces.C.int;` | `return Byte is use type Interfaces.C.int;` |

**Why GE9 exists.**
- After GE5–GE8, the renaming `K` of `Decide_Raw_Metadata` (S5 `:836`) has no reference left; `K.` occurs there only at `:852`, `:855`, `:867` and `:870`.
- The core builds use `-gnatwa`, which includes `-gnatwu`. The installed GNAT User's Guide (`gnat_ugn.info:8982-8999`) states that `-gnatwu` warns about entities that are declared but not referenced.
- Keeping v3's rule "pre-existing renames unchanged" would therefore knowingly add a warning. GE9 deletes the dead renaming as a recorded, reviewed edit, which has no semantic effect. Whether GNAT 16.1.0 actually warns here is unverified installed-tool behaviour; GE9 is justified either way.
- `K` in `Decide_Raw_Context` (`:761`) stays referenced through `K.Result` and `K.U32`.

**Undo check (R-GLUE).** Replacing each new text by its old text in the successor's isolated function must give:
- `Decide_Raw_Context`: sha256 `56dc5c697554b1cc2efaa759b55999447d9676be6649df1e6c64b615fd6c6a99`;
- `Decide_Raw_Metadata`: sha256 `99a1343621bec0a24433d797974f002ba9bbd61cabd8b49e72bbbe4daf26fbfa`.

Both are observed S5 values. v3 B4.23's ordered tokens are substrings of the new texts. The pre-existing Off value decisions in `Authority_Glue` remain boundary surface (D-21).

### B4.24 `Diagnostic_Transport` (RC1, PK-6b; carried design, tile added)

The package specification span and package body span must equal these N1 texts. They are the N1 form of v3 DESIGN §4.4 (lines 509-559), derived by a read-only script.

Specification:
`package Diagnostic_Transport is procedure Mark (Site : String); procedure Value (Site : String; Number : Interfaces.Integer_64); procedure Exception_Text (Site : String; Error : Ada.Exceptions.Exception_Occurrence); end Diagnostic_Transport;`

Body:
`package body Diagnostic_Transport is procedure Mark (Site : String) is Write : Boolean; begin Evaluation_Completion_C.Diagnostic_Begin_Line (Site, Write); if Write then Ada.Text_IO.Put_Line (Ada.Text_IO.Standard_Error, Evaluation_Completion_C.Diagnostic_Line (Site)); Ada.Text_IO.Flush (Ada.Text_IO.Standard_Error); end if; exception when others => Evaluation_Completion_C.Diagnostic_Latch_Failure; end Mark; procedure Value (Site : String; Number : Interfaces.Integer_64) is Compose : Boolean; begin Evaluation_Completion_C.Diagnostic_Begin_Value (Site, Number, Compose); if Compose then Mark (Evaluation_Completion_C.Diagnostic_Value_Site (Site, Number)); end if; exception when others => Evaluation_Completion_C.Diagnostic_Latch_Failure; end Value; procedure Exception_Text (Site : String; Error : Ada.Exceptions.Exception_Occurrence) is Active : Boolean; begin Evaluation_Completion_C.Diagnostic_Observe (Active); if Active then declare Information : constant String := Ada.Exceptions.Exception_Information (Error); Compose : Boolean; begin Evaluation_Completion_C.Diagnostic_Begin_Exception (Site, Information, Compose); if Compose then Mark (Evaluation_Completion_C.Diagnostic_Exception_Site (Site, Information)); end if; end; end if; exception when others => Evaluation_Completion_C.Diagnostic_Latch_Failure; end Exception_Text; end Diagnostic_Transport;`

**Notes.**
- Clauses: none in either span.
- v3's B4.24 tokens and the D2 count rule, which compares the whole body's `Put_Line`/`Flush`/`Standard_Error`/`Exception_Information` counts with those inside `Mark` and `Exception_Text`, are carried unchanged.

---

## B5. Predecessor edits E1–E4 (PP1; exact text)

Each edit is one entry of compose's single-occurrence `manifest-edits.json`. The old text is the exact S5 text and occurs once in the manifest. Indentation is shown exactly. Each edit keeps the problem message text, and no other line of the predecessor function changes (PP2).

### E1 (PK-2): `proof_manifest.py:500-504`, base `export_problems`

Old:
```python
    v3 = normalized_ada((root / 'core/worldline-recovery_authorization_v3_c_api.ads').read_text(encoding='utf-8'))
    for symbol in ('wl_recovery_authorization_version_v3', 'wl_recovery_authorization_layout_v3',
                   'wl_recovery_authorization_decide_v3'):
        if v3.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'full-domain recovery export binding differs: {symbol}')
```
New:
```python
    v3 = normalized_ada((root / 'core/worldline-recovery_authorization_v3_c_api.ads').read_text(encoding='utf-8'))
    v3_capi = normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8'))
    for symbol, home in (('wl_recovery_authorization_version_v3', v3), ('wl_recovery_authorization_layout_v3', v3),
                         ('wl_recovery_authorization_decide_v3', v3_capi)):
        if home.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'full-domain recovery export binding differs: {symbol}')
```

### E2 (PK-2): `proof_manifest.py:932-936`, protocol override

Old:
```python
    text = normalized_ada((root / 'core/worldline-recovery_protocol_c_api.ads').read_text(encoding='utf-8'))
    for symbol in ('wl_recovery_protocol_version_v1', 'wl_recovery_protocol_layout_v1',
                   'wl_recovery_protocol_decide_v1'):
        if text.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'protected recovery protocol export binding differs: {symbol}')
```
New:
```python
    text = normalized_ada((root / 'core/worldline-recovery_protocol_c_api.ads').read_text(encoding='utf-8'))
    capi = normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8'))
    for symbol, home in (('wl_recovery_protocol_version_v1', text), ('wl_recovery_protocol_layout_v1', text),
                         ('wl_recovery_protocol_decide_v1', capi)):
        if home.count(f'External_Name => "{symbol}"') != 1:
            problems.append(f'protected recovery protocol export binding differs: {symbol}')
```

### E3 (PK-5): `proof_manifest.py:946-949`, chain override

Old:
```python
    spec = (root / 'core/worldline-chain_authority_c_api.ads').read_text()
    body = (root / 'core/worldline-chain_authority_c_api.adb').read_text()
    if spec.count('External_Name => "wl_chain_authority_replay_v1"') != 1 or 'Result_At (Output).all := W.Decide (Owned, H);' not in body:
        problems.append('complete-chain native export is not bound to the selected full-row wire decision')
```
New:
```python
    spec = normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8'))
    body = normalized_ada((root / 'core/worldline-chain_authority_c_api.adb').read_text(encoding='utf-8'))
    capi = normalized_ada((root / 'core/worldline-c_api.adb').read_text(encoding='utf-8'))
    if (spec.count('External_Name => "wl_chain_authority_replay_v1"') != 1
            or _capi_isolate(body, 'Replay_Value').count('return (Ok => True, Value => W.Decide (Owned, H));') != 1
            or _capi_isolate(capi, 'Chain_Replay').count('Result_At (Output).all := RV.Value;') != 1):
        problems.append('complete-chain native export is not bound to the selected full-row wire decision')
```
`_capi_isolate` is defined by the PK-1 tail (B8) and resolved at call time. It returns `''` on any isolation failure and never raises. The decision-to-output protection the predecessor gave is kept and strengthened with exact, isolated tokens. The B4.13 ordered list adds the rest.

### E4 (PK-6b): `proof_manifest.py:488-491`, base `export_problems`

Old:
```python
    finalization = normalized_ada((root / 'core/evaluation_finalization_c.ads').read_text(encoding='utf-8'))
    final_entry = ('function Decide (Input, Output : System.Address) return Interfaces.C.int '
        'with Export, Convention => C, External_Name => "wl_finalization_decide_v1";')
    mixed_entry = ('function Decide_Mixed (Collapse : System.Address; Primary_Kind : U32; '
```
New:
```python
    finalization = normalized_ada((root / 'core/worldline-c_api.ads').read_text(encoding='utf-8'))
    final_entry = ('function Finalization_Decide (Input, Output : System.Address) return Interfaces.C.int '
        'with Export, Convention => C, External_Name => "wl_finalization_decide_v1";')
    mixed_entry = ('function Finalization_Decide_Mixed (Collapse : System.Address; Primary_Kind : U32; '
```
Lines 492–499, which hold the rest of `mixed_entry`, the two count checks and the two messages, are unchanged. The resulting strings equal B3 items 17 and 18.

**No other predecessor changes.** The owner override (`:956-964`) counts the owner symbols in raw `core/worldline-c_api.ads`, and the owner audit override (`:975-994`) checks an exact declaration there. Neither touches a relocated symbol. Both stay byte-identical, as do `:453-487`. PP2's reconstruction check undoes E1–E4, deletes the appended tails, and must reproduce the S5 manifest exactly.

*v4 note.* In v4, "the B4.13 ordered list" in the paragraph after E3 means the B4.13 tile. `_capi_isolate` keeps its v3 contract: it returns `''` on any isolation failure and never raises (B8).

---

## B6. Diagnostic site sequences (`CAPI_DIAGNOSTIC_SITES`; observed in S5, enforced from PK-6b)

The observed sequences were extracted read-only from `core/evaluation_completion_c.adb` and `core/evaluation_finalization_c.adb`. Each is an ordered tuple of (kind, literal); in the successor, kind `Mark` maps to `Diagnostic_Transport.Mark`, `Value` to `.Value`, and `Exception` to `.Exception_Text`. D3 extracts `Diagnostic_Transport\.(Mark|Value|Exception_Text) \("([^"]*)"` from each isolated successor unit and requires the identical tuple.

| Successor unit | S5 origin | Sequence (S5 line of each call) |
|---|---|---|
| `Native_Diagnostic_Control` | `Diagnostic_Control` (`:73-88`) | Mark `trace.begin` (79); Mark `trace.end` (82) |
| `Completion_Transport.Context_Matches` | `Context_Matches` (`:733-869`) | Mark `completion.context.enter` (750); Mark `completion.context.input-extents-rejected` (756); Mark `completion.context.transport-guard-rejected` (782); Mark `completion.context.copy-arenas` (785); Mark `completion.context.arenas-copied` (794); Value `completion.context.field-rejected` (798); Value `completion.context.row-rejected` (813); Value `completion.context.row-field-row` (822); Value `completion.context.row-field-rejected` (823); Value `completion.context.required-rejected` (842); Mark `completion.context.join` (849); Value `completion.context.join-result` (859); Exception `completion.context` (867) |
| `Completion_Transport.Metadata_Base` | `Metadata_Base` (`:893-907`) | none |
| `Completion_Metadata_Matches` | `Metadata_Matches` (`:909-986`) | Mark `completion.metadata.enter` (921); Mark `completion.metadata.input-extents-rejected` (925); Mark `completion.metadata.transport-guard-rejected` (940); Mark `completion.metadata.copy-arenas` (943); Mark `completion.metadata.arenas-copied` (950); Value `completion.metadata.row-rejected` (962); Mark `completion.metadata.join` (971); Value `completion.metadata.join-result` (976); Exception `completion.metadata` (984) |
| `Finalization_Decide` | `Decide` (`core/evaluation_finalization_c.adb:121-257`) | Mark `finalization.decide.enter` (127); Mark `finalization.decide.input-extents-rejected` (132); Mark `finalization.decide.transport-guard-rejected` (155); Mark `finalization.decide.copy-arena` (158); Value `finalization.decide.required-rejected` (175); Value `finalization.decide.row-rejected` (195); Value `finalization.decide.reason` (247); Value `finalization.decide.promotion` (248); Exception `finalization.decide` (255) |
| `Finalization_Transport.Final_Context_Matches` | `Final_Context_Matches` (`:259-355`) | Mark `finalization.context.enter` (272); Mark `finalization.context.seal-rejected` (276); Mark `finalization.context.required-extent-rejected` (288); Mark `finalization.context.projected` (332); Value `finalization.context.context-result` (338); Value `finalization.context.metadata-result` (344); Exception `finalization.context` (353) |
| `Finalization_Decide_Mixed` | `Decide_Mixed` (`:357-509`) | Mark `finalization.mixed.enter` (411); Mark `finalization.mixed.collapse-extent-rejected` (415); Mark `finalization.mixed.dependency-rejected` (424); Mark `finalization.mixed.primary-ready-rejected` (434); Mark `finalization.mixed.staged-ready-rejected` (446); Value `finalization.mixed.primary-ready` (451); Value `finalization.mixed.staged-ready` (452); Mark `finalization.mixed.agent-extent-rejected` (457); Mark `finalization.mixed.agent-record-rejected` (465); Value `finalization.mixed.agent-ready` (472); Mark `finalization.mixed.primary-context-rejected` (476); Mark `finalization.mixed.staged-context-rejected` (481); Value `finalization.mixed.collapse-decision` (488); Mark `finalization.mixed.primary-metadata-rejected` (494); Mark `finalization.mixed.staged-metadata-rejected` (500); Exception `finalization.mixed` (507) |

Observed sequence lengths: 2, 13, 0, 9, 9, 7, 16. Textual sequence equality does not establish the runtime line sequence. C-06 checks that on the integrated library.

*v4 note.* The B4.16–B4.22 tiles reproduce exactly these sequences, so D3 and R-TILE agree.

---

## B7. Identity binding per stage (RC4, RC5; §8.7)

| Stage | I1: core Ada pins regenerated by compose re-pin | I3/I4: new `CONTRACT_PINS` keys | I5: controls bound by `source-inventory.json` and execution frames | Manifest changes recorded in `composition.json` |
|---|---|---|---|---|
| PK-0 | none | none | `tests/test_capi_characterization.py`, `tests/test_capi_layout_identity.py`, `tests/test_capi_diagnostics.py`, `tests/capi_guard_pages.py`, `tests/capi_characterization.json`, `tests/capi_layout_baseline.json` | none |
| PK-1 | `core/worldline-c_api.ad[sb]`, `core/worldline-resources_c_api.ad[sb]`, `core/worldline-recovery_c_api.ad[sb]` | none | `tests/test_capi_symbol_binding.py` (C-08), `tests/test_capi_manifest_mutations.py` (C-09) | tail append (B8 tables, override, 6 REQUIRED_PROVED names, pins) |
| PK-2 | C_API pair; U3, U4, U5 pairs | none | C-09 data updated in the same files under the stage's own inventory hash | tail append; E1, E2 |
| PK-xR | the repaired specs (and wire specs) only | none | `tests/test_capi_layout_identity.py` data (C-13) | tail append (pins) |
| PK-3, PK-4 | C_API pair and the stage's unit pairs | none | C-09 data | tail append |
| PK-5 | C_API pair; U12, U13 pairs | none | C-09 data | tail append; E3 |
| PK-6a | `core/evaluation_completion_c.ad[sb]`, `core/evaluation_finalization_c.ad[sb]` | none | optional Ada value-level control projects (I4 keys if added) | tail append (57 names, pins) |
| PK-6b | C_API pair; completion pair; finalization pair | none | C-06 and C-09 data | tail append; E4 |
| PK-7 | C_API pair; U10, U11 pairs | `pending-component/core/evaluation_pending_c.ads`, `…_c.adb`, `evaluation_pending_v2_c.ads`, `…_v2_c.adb`, `evaluation_pending_transport.ads`, `…_transport.adb`, `pending-component/pending.gpr` (169 → 176 keys, JACKAL exact); optionally `core/evaluation_pending.ads`/`.adb` (→ 178) | C-10 | tail append |
| PK-S | none | none | none | identities only |

In every stage, every file outside the touched list has the same raw sha256 as in the base stage's `source-inventory.json` (I7, "untouched means identical"). This covers the provider files (`runtime/worldline/*.py`, `core/*.h`, `pending-component/core/*.h`), which this design does not touch (I6). Adding a key changes `proof_source_files` (`proof_manifest.py:662-667`). That change is reviewed in the stage that makes it, and it is never a side effect.

*v4 note.* The PK-0 controls of the I5 column now encode the corrected effect classes and frontiers of DESIGN §9.6 (V3-RC5). Their file names are unchanged. The 176 and 178 key counts are re-run in v4 as JACKAL J37 and J38.

---

## B8. The `export_problems` override (PK-1 tail; PROPOSAL sketch, REVISED in v4)

**Status of this sketch.**
- The text is not executed and not reviewed. After its last edit its syntax was parsed, read-only, with Python's `ast` module from this file (AUTHOR-NOTES). Parsing is a syntax check only.
- It imports nothing beyond what the manifest already imports (`hashlib`, `json`, `Path`, `re`, `typing`).
- It is appended after the last S5 line (`:1029`). Later stages only append `.update(...)` lines to the tables.
- **Every rule of B0 has its own check function.** The table at the end of this section maps each function to its rules.

```python
# C-API raw-pointer boundary consolidation (design v4, stage PK-1). Whole-closure binding, exact
# tiles, transport residues, scoped clause inventory, alias exclusion, write forms, gates,
# residual identity and component interface membership. Every predecessor check runs first.
CAPI_ALTERNATE_BINDINGS = ('Link_Name', 'pragma Export', 'pragma Import', 'pragma Linker_Section',
    'Export_Function', 'Export_Procedure', 'Export_Object', 'Import_Function', 'Import_Procedure',
    'Import_Object', 'Import_Valued_Procedure')
CAPI_PROJECT_FORBIDDEN = ('Linker_Options', '--defsym', '--wrap', '-Wl,', 'version-script')
CAPI_CORE_HOME = {...}            # B2.1 literal: all 91 symbols at their L0 homes, then the PK-1 .update
CAPI_DECLARATIONS = {...}         # symbol -> B3 successor text, for the symbols relocated so far
CAPI_C_API_SUBTYPES = ('subtype U8 is Interfaces.Unsigned_8;', 'subtype U32 is Interfaces.Unsigned_32;',
    'subtype I64 is Interfaces.Integer_64;', 'subtype Size is Interfaces.C.size_t;')
CAPI_TILES = {...}                # scope key -> (head, (segment, ...)); B4. Keys: 'Export_Name' or 'Transport.Name'
CAPI_DIAGNOSTIC_PACKAGE = {}      # {'spec': text, 'body': text} (B4.24), filled at PK-6b
CAPI_TRANSPORTS = {...}           # transport -> {'clauses': text, 'subtypes': (...), 'constants': (...),
                                  #   'helpers': ((kind, name, sha256), ...), 'moved': (name, ...)}; B4, B9.2, B9.3
CAPI_INVENTORY = {...}            # scope key ('spec:T', 'body:T', tile key) -> tuple of clause texts; B9.2
CAPI_RESIDUAL_CLAUSES = (...)     # B9.1: the 36 S5 residual clause texts, in order
CAPI_RESIDUAL_DELETED = ()        # indices into CAPI_RESIDUAL_CLAUSES; PK-6b appends 22 (R-DEL-1)
CAPI_ALIAS_FORBIDDEN = (...)      # B9.4: (alias, routine) pairs
CAPI_SPARK_UNITS = (...)          # B9.4: the units that own Appendix C names (17, observed by script) (R-INV vii)
CAPI_WRITES = {...}               # scope key -> ((id, target, form, (span, ...), (closed, ...), {name: assignments}), ...); B10.2
CAPI_GATES = {...}                # scope key -> ((id, object, gate text), ...); B10.3
CAPI_GATE_ASSIGNED = ('G21c',)    # the one gated object that is assigned (its assignments are bound by W21)
CAPI_GLUE_EDITS = ()              # ((function, old, new), ...); B4.23, filled at PK-6b
CAPI_GLUE_SHA256 = {'Decide_Raw_Context': '56dc5c697554b1cc2efaa759b55999447d9676be6649df1e6c64b615fd6c6a99',
    'Decide_Raw_Metadata': '99a1343621bec0a24433d797974f002ba9bbd61cabd8b49e72bbbe4daf26fbfa'}
CAPI_RESIDUAL_SHA256 = '187242f4aaaddd7eaecc996659b305c1fd2329e419a090c3b1d4c55dcc08669e'
CAPI_SPEC_RESIDUAL_SHA256 = '4c533f63b629146beea81b20c7bddcae385beafb61ffc62cc866212f6d5c4c6b'
CAPI_LAYOUT_PACKAGES = (...)      # B4.0, the prefix relocated so far
CAPI_LAYOUT_EXPORTS = (...)       # B4.0, the prefix relocated so far (also the spec declaration order)
CAPI_DIAGNOSTIC_SITES = {}        # B6, filled at PK-6b
CAPI_CORE_INTERFACE = (...)       # B9.5: the observed S5 71-unit tuple (G9)
CAPI_COMPONENT_HOME = {...}       # B2.3 literal, L0 homes
CAPI_COMPONENT_INTERFACE = ('evaluation_pending', 'evaluation_pending_c', 'evaluation_pending_v2',
    'evaluation_pending_v2_c', 'evaluation_epoch', 'resource_quantities', 'spark', 'spark.big_integers')
CAPI_COMPONENT_LIBRARY = ('for Library_Name use "evaluation_pending";', 'for Library_Kind use "dynamic";',
    'for Library_Standalone use "encapsulated";', 'for Library_Auto_Init use "true";')
CAPI_COMPONENT_MIRROR = {}        # PK-7, D-13 option (i): component file -> ((name, kind), ...) (K6)
CAPI_COMPONENT_DECLARATIONS = {}  # PK-7, D-13 option (i): component spec -> (B3 #19, B3 #20) (K6)
CAPI_MOVED_UNITS = ('core/worldline-resources_c_api.ads', 'core/worldline-resources_c_api.adb',
    'core/worldline-recovery_c_api.ads', 'core/worldline-recovery_c_api.adb')   # extended per stage (G7)
CAPI_DIAGNOSTIC_CALL = re.compile(r'Diagnostic_Transport\.(Mark|Value|Exception_Text) \("([^"]*)"')
CAPI_CLAUSE = re.compile(r'\b(?:package\s+\w+\s+renames\s+[\w.]+|use\s+all\s+type\s+[\w.,\s]+?'
                         r'|use\s+type\s+[\w.,\s]+?|use\s+[\w.,\s]+?)\s*;', re.IGNORECASE)
CAPI_BODY_HEAD = 'package body Worldline.C_API with SPARK_Mode => Off is'


def _capi_text(root: Path, relative: str) -> str:
    return normalized_ada((root / relative).read_text(encoding='utf-8'))


def _capi_code(text: str) -> str:
    """N2: blank every character inside a double-quoted literal, keeping all positions."""
    return re.sub(r'"[^"]*"', lambda match: '"' + '_' * (len(match.group()) - 2) + '"', text)


def _capi_span(text: str, name: str, kind: str = 'subprogram', low: int = 0, high: int | None = None):
    """R-ISO on N2 inside text[low:high]; returns (start, end) or None and never raises."""
    code = _capi_code(text)
    high = len(code) if high is None else high
    region = code[low:high]
    if kind in ('spec', 'body'):
        head = f'package body {name} is' if kind == 'body' else f'package {name} is'
        if region.count(head) != 1:
            return None
        start = region.find(head)
        end = region.find(f'end {name};', start)
        return None if end < 0 else (low + start, low + end + len(f'end {name};'))
    if kind == 'declaration':                      # name is the declaration's start text
        if region.count(name) != 1:
            return None
        start, depth = region.find(name), 0
        for index in range(start, len(region)):
            depth += (region[index] == '(') - (region[index] == ')')
            if region[index] == ';' and depth == 0:
                return (low + start, low + index + 1)
        return None
    end_token = f'end {name};'
    if region.count(end_token) != 1:
        return None
    end = region.find(end_token)
    start = max(region.rfind(f'function {name} ', 0, end), region.rfind(f'procedure {name} ', 0, end))
    return None if start < 0 else (low + start, low + end + len(end_token))


def _capi_isolate(text: str, name: str, kind: str = 'subprogram') -> str:
    span = _capi_span(text, name, kind)
    return '' if span is None else text[span[0]:span[1]]


def _capi_scope_span(text: str, key: str):
    if key.startswith(('spec:', 'body:')):
        kind, name = key.split(':', 1)
        return _capi_span(text, name, kind)
    if '.' in key:                                 # 'Transport.Subprogram': isolated inside the transport body
        container, name = key.split('.', 1)
        outer = _capi_span(text, container, 'body')
        return None if outer is None else _capi_span(text, name, 'subprogram', outer[0], outer[1])
    return _capi_span(text, key)


def _capi_profile(text: str) -> str:
    """The text before the first ' is ' at parenthesis depth 0 (a body's profile)."""
    code, depth = _capi_code(text), 0
    for index, char in enumerate(code):
        depth += (char == '(') - (char == ')')
        if depth == 0 and code.startswith(' is ', index):
            return text[:index]
    return ''


def _capi_named(code: str, name: str):
    return re.finditer(rf'(?<![\w.]){re.escape(name)}(?!\w)', code, re.IGNORECASE)


def _capi_assigned(code: str, name: str) -> int:
    return len(re.findall(rf'(?<![\w.]){re.escape(name)}(?:\s*\([^;]*?\))?(?:\s*\.\s*\w+)*\s*:=',
                          code, re.IGNORECASE))


def _capi_sha256(text: str) -> str:
    return hashlib.sha256(' '.join(text.split()).encode('utf-8')).hexdigest()


def _capi_library_interface(project: str):
    """K3/G9: the parsed Library_Interface unit tuple, or None if it is not a single literal list."""
    text = normalized_ada(project)                 # GPR comments also start with --
    code = _capi_code(text)
    heads = list(re.finditer(r'\bfor\s+Library_Interface\s+use\s*\(', code, re.IGNORECASE))
    if len(heads) != 1 or len(re.findall(r'\bLibrary_Interface\b', code, re.IGNORECASE)) != 1:
        return None
    if re.search(r'\bfor\s+Interfaces\s+use\b', code, re.IGNORECASE):
        return None
    start = heads[0].end()
    end = code.find(')', start)
    if end < 0 or not code.startswith(');', end):
        return None
    items = [item.strip() for item in text[start:end].split(',')]
    if not items or not all(re.fullmatch(r'"[A-Za-z][\w.]*"', item) for item in items):
        return None
    names = tuple(item.strip('"').lower() for item in items)
    return names if len(set(names)) == len(names) else None


def _capi_symbols(root: Path, files, home_table, label: str) -> list[str]:
    problems, seen, counts = [], {}, {'Export': 0, 'External_Name': 0, 'literal': 0}
    for relative in files:
        text = _capi_text(root, relative)
        for word in CAPI_ALTERNATE_BINDINGS:
            if word in text:
                problems.append(f'{relative}: alternate binding construct {word}')
        if re.search(r'\bImport\b', text):
            problems.append(f'{relative}: Import aspect or pragma')
        counts['Export'] += len(re.findall(r'\bExport\b', text))
        counts['External_Name'] += text.count('External_Name =>')
        for match in re.finditer(r'"(wl_[a-z0-9_]+)"', text):
            counts['literal'] += 1
            seen.setdefault(match.group(1), []).append(relative)
            if not text[:match.start()].endswith('External_Name => '):
                problems.append(f'{relative}: {match.group(1)} is not an External_Name literal')
    if set(seen) != set(home_table):
        problems.append(f'{label} C symbol set differs from the binding table')
    for symbol, homes in seen.items():
        if homes != [home_table.get(symbol)]:
            problems.append(f'{symbol} is bound in {homes}, expected exactly once in {home_table.get(symbol)}')
    if len(set(counts.values())) != 1:
        problems.append(f'{label} Export/External_Name/literal counts differ: {counts}')
    return problems


def _capi_closure_problems(root: Path) -> list[str]:                                       # G1-G4, G6, G7
    core = sorted(name for name in DECLARED_CORE_ADA_SOURCES if name.endswith(('.ads', '.adb')))
    problems = _capi_symbols(root, core, CAPI_CORE_HOME, 'core closure')
    for unit in CAPI_MOVED_UNITS:
        text = _capi_text(root, unit)
        for word in ('Address_To_Access_Conversions', 'Unchecked_Conversion', "'Address"):
            if word in text:
                problems.append(f'{unit}: {word} remains after relocation')
    return problems


def _capi_core_project_problems(root: Path) -> list[str]:                                  # G5, G9
    problems = []
    for relative in ('core/worldline_core.gpr', 'core/worldline_core_sources.gpr', 'core/attest_sha256.gpr'):
        project = (root / relative).read_text(encoding='utf-8')
        problems += [f'{relative}: linker option {word}' for word in CAPI_PROJECT_FORBIDDEN if word in project]
    core = (root / 'core/worldline_core.gpr').read_text(encoding='utf-8')
    if _capi_library_interface(core) != CAPI_CORE_INTERFACE:
        problems.append('worldline_core.gpr Library_Interface differs from the S5 unit list')
    return problems


def _capi_component_problems(root: Path) -> list[str]:                                     # K1-K3, K5, K6
    files = sorted(path.relative_to(root).as_posix()
                   for path in (root / 'pending-component/core').glob('*.ad[sb]'))
    problems = _capi_symbols(root, files, CAPI_COMPONENT_HOME, 'component')
    project = (root / 'pending-component/pending.gpr').read_text(encoding='utf-8')
    if _capi_library_interface(project) != CAPI_COMPONENT_INTERFACE:
        problems.append('pending.gpr Library_Interface differs from the exact unit list')
    normalized = normalized_ada(project)
    for declaration in CAPI_COMPONENT_LIBRARY:
        attribute = declaration.split()[1]
        if (normalized.count(declaration) != 1
                or len(re.findall(rf'\bfor\s+{attribute}\s+use\b', normalized, re.IGNORECASE)) != 1):
            problems.append(f'pending.gpr {attribute} differs')
    problems += [f'pending.gpr: linker option {word}' for word in CAPI_PROJECT_FORBIDDEN if word in project]
    core = _capi_text(root, 'core/worldline-c_api.adb')
    for relative, scopes in CAPI_COMPONENT_MIRROR.items():
        component = _capi_text(root, relative)
        for name, kind in scopes:
            mirrored = _capi_isolate(component, name, kind)
            if not mirrored or mirrored != _capi_isolate(core, name, kind):
                problems.append(f'{relative}: {name} differs from the core transport')
    for relative, declarations in CAPI_COMPONENT_DECLARATIONS.items():
        spec = _capi_text(root, relative)
        problems += [f'{relative}: declaration differs' for item in declarations if spec.count(item) != 1]
    return problems                                                                        # K4 is C-10 plus pins (I3)


def _capi_profile_problems(root: Path) -> list[str]:                                       # P1, P2
    spec = _capi_text(root, 'core/worldline-c_api.ads')
    body = _capi_text(root, 'core/worldline-c_api.adb')
    problems = [f'{symbol}: relocated declaration differs' for symbol, declaration in CAPI_DECLARATIONS.items()
                if spec.count(declaration) != 1]
    problems += [f'C_API subtype differs: {line}' for line in CAPI_C_API_SUBTYPES if spec.count(line) != 1]
    for name in ('U8', 'U32', 'I64', 'Size'):
        declared = len(re.findall(rf'\b(?:sub)?type {name} is\b', spec + ' ' + body))
        objects = len(re.findall(rf"(?<![\w.']){name}\s*:(?!=)", spec + ' ' + body))   # not ': T :='
        if declared != 1 or objects:
            problems.append(f'C_API declares {name} more than once')
    return problems


def _capi_tile_problems(root: Path) -> list[str]:                                          # R-TILE
    body = _capi_text(root, 'core/worldline-c_api.adb')
    problems = []
    for key, (head, segments) in CAPI_TILES.items():
        span = _capi_scope_span(body, key)
        actual = '' if span is None else body[span[0]:span[1]]
        if actual != head + ' ' + ' '.join(segments):
            problems.append(f'{key}: text differs from its exact tile')
    for kind, text in CAPI_DIAGNOSTIC_PACKAGE.items():
        if _capi_isolate(body, 'Diagnostic_Transport', kind) != text:
            problems.append(f'Diagnostic_Transport {kind} differs from its exact text')
    return problems


def _capi_transport_problems(root: Path) -> list[str]:                                     # R-TRANS
    body = _capi_text(root, 'core/worldline-c_api.adb')
    starts = {'type': 'type {} is ', 'fn_inst': 'function {} is new ', 'pkg_inst': 'package {} is new ',
              'expr': 'function {} ('}
    problems = []
    for package, table in CAPI_TRANSPORTS.items():
        spec_span, body_span = _capi_span(body, package, 'spec'), _capi_span(body, package, 'body')
        if spec_span is None or body_span is None:
            problems.append(f'{package}: specification or body cannot be isolated')
            continue
        spec_text, body_text = body[spec_span[0]:spec_span[1]], body[body_span[0]:body_span[1]]
        spec_items = [table['clauses'], *table['subtypes'], *table['constants']]
        body_items = []
        for kind, name, digest in table['helpers']:
            if kind == 'body':
                isolated = _capi_isolate(body_text, name)
                body_items.append(isolated)
                spec_items.append(_capi_profile(isolated) + ';' if isolated else '')
            else:
                span = _capi_span(spec_text, starts[kind].format(name), 'declaration')
                isolated = '' if span is None else spec_text[span[0]:span[1]]
                spec_items.append(isolated)
            if hashlib.sha256(isolated.encode('utf-8')).hexdigest() != digest:
                problems.append(f'{package}.{name}: helper text differs from the S5 original')
        for moved in table['moved']:
            isolated = _capi_isolate(body_text, moved)                     # its text is bound by its tile
            body_items.append(isolated)
            spec_items.append(_capi_profile(isolated) + ';' if isolated else '')
        for text, items, empty in ((spec_text, spec_items, f'package {package} is end {package};'),
                                   (body_text, body_items, f'package body {package} is end {package};')):
            residue = text
            for item in items:
                if not item or residue.count(item) != 1:
                    problems.append(f'{package}: specified content missing or repeated')
                    break
                residue = residue.replace(item, ' ', 1)
            else:
                if ' '.join(residue.split()) != empty:
                    problems.append(f'{package}: content beyond the specified transport')
    return problems


def _capi_scopes(body: str) -> list[tuple[str, int, int]]:
    keys = [f'{kind}:{package}' for package in CAPI_LAYOUT_PACKAGES for kind in ('spec', 'body')]
    keys += list(CAPI_TILES)
    return [(key, *span) for key in keys if (span := _capi_scope_span(body, key)) is not None]


def _capi_owner(scopes, position: int) -> str:
    inner = [scope for scope in scopes if scope[1] <= position < scope[2]]
    return min(inner, key=lambda scope: scope[2] - scope[1])[0] if inner else 'RESIDUAL'


def _capi_clause_problems(root: Path) -> list[str]:                                        # R-INV, G10
    body = _capi_text(root, 'core/worldline-c_api.adb')
    spec_code = _capi_code(_capi_text(root, 'core/worldline-c_api.ads'))
    code = _capi_code(body)
    head = code.find(CAPI_BODY_HEAD)
    if head < 0:
        return ['C_API body head not found']
    problems = []
    if CAPI_CLAUSE.search(code[:head]) or re.search(r'\bpragma\b', code[:head], re.IGNORECASE):
        problems.append('C_API context clause holds a use clause or pragma')
    if CAPI_CLAUSE.search(spec_code) or re.search(r'\brenames\b', spec_code, re.IGNORECASE):
        problems.append('C_API specification declares a clause or renaming')
    if re.search(r'\buse\s+all\s+type\b', code + ' ' + spec_code, re.IGNORECASE):
        problems.append('use all type occurs in the C_API pair')
    scopes = _capi_scopes(body)
    found = {key: [] for key, _, _ in scopes}
    found['RESIDUAL'] = []
    renames = dict.fromkeys(found, 0)
    for match in CAPI_CLAUSE.finditer(code, head):
        found[_capi_owner(scopes, match.start())].append(' '.join(body[match.start():match.end()].split()))
    for match in re.finditer(r'\brenames\b', code[head:], re.IGNORECASE):
        renames[_capi_owner(scopes, head + match.start())] += 1
    spark = {name.lower() for name in CAPI_SPARK_UNITS} | {alias.lower() for alias, _ in CAPI_ALIAS_FORBIDDEN}
    for key, clauses in found.items():                                                     # R-INV (vii)
        for clause in clauses:
            words = clause.rstrip(';').split()
            if (words[0].lower() == 'use' and words[1].lower() not in ('type', 'all')
                    and any(name.strip().lower() in spark for name in ' '.join(words[1:]).split(','))):
                problems.append(f'{key}: a use clause names a SPARK unit or a renaming of one')
    residual = [clause for index, clause in enumerate(CAPI_RESIDUAL_CLAUSES) if index not in CAPI_RESIDUAL_DELETED]
    for key, clauses in found.items():
        expected = tuple(residual) if key == 'RESIDUAL' else tuple(CAPI_INVENTORY.get(key, ()))
        if tuple(clauses) != expected:
            problems.append(f'{key}: clause inventory differs')
        if renames[key] != sum(1 for clause in expected if ' renames ' in clause):
            problems.append(f'{key}: a renaming other than the listed package renamings')
    problems += [f'{key}: scope missing' for key in CAPI_INVENTORY if key not in found]
    return problems


def _capi_alias_problems(root: Path) -> list[str]:                                         # R-ALIAS (O6 a)
    code = _capi_code(_capi_text(root, 'core/worldline-c_api.adb'))
    return [f'{alias}.{routine}: a routine of a SPARK unit is named through a renaming'
            for alias, routine in CAPI_ALIAS_FORBIDDEN
            if re.search(rf'(?<![\w.]){alias}\s*\.\s*{routine}(?!\w)', code, re.IGNORECASE)]


def _capi_write_problems(root: Path) -> list[str]:                                         # R-W
    body = _capi_text(root, 'core/worldline-c_api.adb')
    problems = []
    scopes = {key: (low, high) for key, low, high in _capi_scopes(body)}
    problems += [f'{key}: scope cannot be isolated' for key in CAPI_WRITES if key not in scopes]
    for key, (low, high) in scopes.items():               # every designed scope, with or without rows
        rows = CAPI_WRITES.get(key, ())
        unit = body[low:high]
        code = _capi_code(unit)
        writes = [match.start() for match in                 # the helper's own declaration is not a call
                  re.finditer(r'\.all\s*:=|(?<![\w.])(?<!procedure )Write_Data\s*\(', code)]
        claimed = set()
        for row_id, target, form, spans, closed, assignments in rows:
            if unit.count(target) != 1:
                problems.append(f'{row_id}: write target missing or repeated')
                continue
            where = unit.find(target)
            claimed |= {write for write in writes if where <= write < where + len(target)}
            intervals = []
            for text in spans:
                if unit.count(text) != 1:
                    problems.append(f'{row_id}: provenance span missing or repeated')
                    continue
                intervals.append((unit.find(text), unit.find(text) + len(text)))
            if not any(start <= where and where + len(target) <= end for start, end in intervals):
                problems.append(f'{row_id}: write target lies outside its provenance spans')
            for name in closed:
                if any(not any(start <= use.start() < end for start, end in intervals)
                       for use in _capi_named(code, name)):
                    problems.append(f'{row_id}: {name} is used outside its provenance spans')
                if _capi_assigned(code, name) != assignments.get(name, 0):
                    problems.append(f'{row_id}: {name} assignment count differs from {form}')
        if claimed != set(writes):
            problems.append(f'{key}: a foreign write has no write-form row')
    return problems


def _capi_gate_problems(root: Path) -> list[str]:                                          # R-GATE (A1)
    body = _capi_text(root, 'core/worldline-c_api.adb')
    problems = []
    for key, rows in CAPI_GATES.items():
        span = _capi_scope_span(body, key)
        if span is None:
            problems.append(f'{key}: scope cannot be isolated')
            continue
        unit = body[span[0]:span[1]]
        code = _capi_code(unit)
        for row_id, name, gate in rows:
            if unit.count(gate) != 1:
                problems.append(f'{row_id}: gate missing or repeated')
                continue
            start = unit.find(gate)
            end = start + len(gate)
            selections = list(re.finditer(rf'(?<![\w.]){re.escape(name)}\s*\.\s*(\w+)', code, re.IGNORECASE))
            tests = [match for match in selections if match.group(1).lower() in ('ok', 'verdict')]
            if len(tests) != 1 or not start <= tests[0].start() < end:
                problems.append(f'{row_id}: the discriminant of {name} is not tested exactly once inside its gate')
                continue
            if any(match.start() <= tests[0].start() for match in selections if match not in tests):
                problems.append(f'{row_id}: a payload of {name} is selected before its discriminant test')
            if _capi_assigned(code, name) and row_id not in CAPI_GATE_ASSIGNED:
                problems.append(f'{row_id}: {name} is assigned')
    scope_list = _capi_scopes(body)                           # completeness: every tested object has a row
    for match in re.finditer(r'(?<![\w.])(\w+)\s*\.\s*Ok\b|\bcase\s+(\w+)\s*\.\s*Verdict\s+is\b',
                             _capi_code(body), re.IGNORECASE):
        key = _capi_owner(scope_list, match.start())
        name = (match.group(1) or match.group(2)).lower()
        if key != 'RESIDUAL' and name not in {row[1].lower() for row in CAPI_GATES.get(key, ())}:
            problems.append(f'{key}: {name} has a discriminant test but no gate row')
    return problems


def _capi_residual_problems(root: Path) -> list[str]:                                      # R-RES, S-RES, R-LAYOUT, R-GLUE
    body = _capi_text(root, 'core/worldline-c_api.adb')
    spec = _capi_text(root, 'core/worldline-c_api.ads')
    problems = []
    packages = [_capi_span(body, package, kind) for package in CAPI_LAYOUT_PACKAGES for kind in ('spec', 'body')]
    exports = [_capi_span(body, name) for name in CAPI_LAYOUT_EXPORTS]
    if None in packages or None in exports:
        return ['a designed package or relocated export cannot be isolated']
    for spans, before, after in ((packages, 'end Layout_Offset;', 'package body Authority_Glue is'),
                                 (exports, 'end Owner_Audit_Decide;', None)):
        if not spans:
            continue
        anchor = body.find(before)
        closing = body.find(after) if after else body.rfind('end Worldline.C_API;')
        if body.count(before) != 1 or spans[0][0] != anchor + len(before) + 1 or closing != spans[-1][1] + 1:
            problems.append(f'designed run after {before} is not where the layout requires')
        if any(later[0] != earlier[1] + 1 for earlier, later in zip(spans, spans[1:])):
            problems.append(f'designed run after {before} is not contiguous in order')
    residual = body
    for start, end in sorted(packages + exports, reverse=True):
        residual = residual[:start] + ' ' + residual[end:]
    for function, old, new in CAPI_GLUE_EDITS:
        if residual.count(new) != 1:
            problems.append(f'{function}: recorded Authority_Glue edit missing or repeated')
            continue
        residual = residual.replace(new, old, 1)
    for function, digest in CAPI_GLUE_SHA256.items():
        if CAPI_GLUE_EDITS and _capi_sha256(_capi_isolate(residual, function)) != digest:
            problems.append(f'{function}: Authority_Glue differs beyond its recorded edits')
    head = residual.find(CAPI_BODY_HEAD)
    if head < 0 or _capi_sha256(residual[head:]) != CAPI_RESIDUAL_SHA256:
        problems.append('pre-existing C_API body text differs from S5 beyond the designed scopes')
    items = [*CAPI_C_API_SUBTYPES, *(CAPI_DECLARATIONS[symbol] for symbol in CAPI_DECLARATIONS)]
    order = [*CAPI_C_API_SUBTYPES, *(CAPI_DECLARATIONS[symbol] for symbol in CAPI_DECLARATION_ORDER
                                     if symbol in CAPI_DECLARATIONS)]
    anchor = spec.find('External_Name => "wl_owner_audit_decide_v1";') + len('External_Name => "wl_owner_audit_decide_v1";')
    if items and ' '.join(order) != spec[anchor + 1:spec.rfind('end Worldline.C_API;') - 1]:
        problems.append('C_API specification additions are not the ordered subtypes and declarations')
    spec_residual = spec
    for item in items:
        if spec_residual.count(item) != 1:
            problems.append('C_API specification addition missing or repeated')
            break
        spec_residual = spec_residual.replace(item, ' ', 1)
    if _capi_sha256(spec_residual) != CAPI_SPEC_RESIDUAL_SHA256:
        problems.append('pre-existing C_API specification text differs from S5')
    return problems


def _capi_diagnostic_problems(root: Path) -> list[str]:                                    # D1-D5, G8
    if not CAPI_DIAGNOSTIC_SITES:
        return []
    body = _capi_text(root, 'core/worldline-c_api.adb')
    unit_spec = _capi_text(root, 'core/evaluation_completion_c.ads')
    unit_body = _capi_text(root, 'core/evaluation_completion_c.adb')
    problems = []
    for key, sites in CAPI_DIAGNOSTIC_SITES.items():                                       # D3
        span = _capi_scope_span(body, key)
        unit = '' if span is None else body[span[0]:span[1]]
        if tuple(CAPI_DIAGNOSTIC_CALL.findall(unit)) != sites:
            problems.append(f'{key}: diagnostic site sequence differs')
    transport = _capi_isolate(body, 'Diagnostic_Transport', 'body')
    mark, text = _capi_isolate(transport, 'Mark'), _capi_isolate(transport, 'Exception_Text')
    for token, home in (('Ada.Text_IO.Put_Line', mark), ('Ada.Text_IO.Flush', mark),
                        ('Standard_Error', mark), ('Ada.Exceptions.Exception_Information', text)):  # D2
        if not home.count(token) or body.count(token) != home.count(token):
            problems.append(f'{token} occurs outside its diagnostic transport procedure')
    if 'with Atomic' in body or re.search(r'Diagnostic_(?:Active|Failed)\b', body):        # D1
        problems.append('diagnostic state appears in the boundary')
    if (unit_body.count('Diagnostic_Active : Boolean := False with Atomic;') != 1
            or unit_body.count('Diagnostic_Failed : Boolean := False with Atomic;') != 1
            or 'Abstract_State => (Diagnostic_State with External)' not in unit_spec):     # D5
        problems.append('SPARK diagnostic state declarations differ')
    for word in ('Ada.Text_IO', 'Ada.Exceptions'):                                          # G8
        if word in unit_spec or word in unit_body:
            problems.append(f'{word} remains in Evaluation_Completion_C')
    return problems


CAPI_DECLARATION_ORDER = (...)    # B3 symbol order 1-20 (equals CAPI_LAYOUT_EXPORTS order)
CAPI_CHECKS = (_capi_closure_problems, _capi_core_project_problems, _capi_component_problems,
               _capi_profile_problems, _capi_tile_problems, _capi_transport_problems,
               _capi_clause_problems, _capi_alias_problems, _capi_write_problems,
               _capi_gate_problems, _capi_residual_problems, _capi_diagnostic_problems)
_capi_predecessor_export_problems = export_problems


def export_problems(root: Path) -> list[str]:
    problems = _capi_predecessor_export_problems(root)                                     # PP3
    for check in CAPI_CHECKS:
        try:
            problems += check(root)
        except Exception as exc:                                                           # fail closed
            problems.append(f'C-API binding check {check.__name__} could not run: {exc!r}')
    return problems
```

**Check-to-rule map.**

| Function | Rules enforced | Replaces in v3 |
|---|---|---|
| `_capi_closure_problems` | G1–G4, G6, G7 | same |
| `_capi_core_project_problems` | G5, **G9** (actual core `Library_Interface` membership) | G5 |
| `_capi_component_problems` | K1, K2, **K3 (actual membership)**, **K5**, **K6** | quoted-string K3 |
| `_capi_profile_problems` | P1, P2 | same |
| `_capi_tile_problems` | **R-TILE** (order, adjacency, provenance, exclusivity and gating by exact text) | O1–O3 ordered tokens and counts |
| `_capi_transport_problems` | **R-TRANS** (exact transport contents, verbatim helper hashes) | none (v3 promised verbatim helpers without a check) |
| `_capi_clause_problems` | **R-INV** (i)–(vii), **G10** | O6 (b)/(c), deferred in v3 |
| `_capi_alias_problems` | **R-ALIAS**, which with R-INV makes O6 (a) enforceable | O6 (a) by tokens only |
| `_capi_write_problems` | **R-W** per form (B10), over every designed scope | O4 / R-W blanket rule |
| `_capi_gate_problems` | **R-GATE** (A1: discriminant tested once, inside the gate, before any payload; every tested object has a gate row) | O5 / R-G by order only |
| `_capi_residual_problems` | **R-RES**, **S-RES**, **R-LAYOUT**, **R-GLUE** | O7 tokens; P3 by reading |
| `_capi_diagnostic_problems` | D1–D5, G8 | same |

**Notes on the sketch.**
- **G6 (old-spec absence)** follows from the closure check. Each symbol must occur exactly once, at its `CAPI_CORE_HOME` entry, so any occurrence in the old spec fails (carried).
- **Isolation failure is a problem, never a skip.** Every isolation helper returns `None` or `''` instead of raising. The override converts any exception of a check into a problem (fail closed), because `contract_problems` (`proof_manifest.py:622-637`) catches only `OSError` from `export_problems`.
- **Invariant checks.** `_capi_clause_problems`, `_capi_alias_problems`, `_capi_write_problems` and `_capi_gate_problems` are implied by `_capi_tile_problems` and `_capi_transport_problems` for the B4 text. They are kept so that a reviewed amendment of B4 cannot weaken a rule while staying textually consistent (B0.2).
- **Residual identity.** `_capi_residual_problems` removes only designed spans and undoes only the recorded glue edits. Any other change to pre-existing C_API code therefore fails, including a change to `Authority_Glue`'s value decisions (D-21).
- **Mutation controls (§8.8, C-09, B12).** These run each mutation in a temporary copy of the stage tree and expect at least one problem. They read text only and never build or run WORLDLINE code.
- **Limits.** What these checks do not establish is listed in §8.9.

---

## B9. Scoped rename and use inventory (new; V3-RC4, O6 (b)/(c))

All clause texts are N1. They were extracted read-only from S5 by script (regex over each unit body, observed). The original 15 unit bodies contain 126 clauses (JACKAL J12): 122 at package level and 4 inside subprograms (JACKAL J21; the 4 are completion `:736`, `:737`, `:741` and `:911`).

### B9.1 Pre-existing residual clauses of the S5 C_API body (`CAPI_RESIDUAL_CLAUSES`)

Observed: 14 package renamings and 22 use clauses, 36 in total (JACKAL J15). The C_API specification and the context clause contain none. After R-DEL-1 (index 22, from PK-6b) the residual holds 13 renamings and 35 clauses (JACKAL J13, J14).

| Index | S5 line | Enclosing scope | Clause |
|---|---|---|---|
| 0 | 27 | package body level | `use type Interfaces.C.size_t;` |
| 1 | 28 | package body level | `use type Interfaces.Unsigned_8;` |
| 2 | 29 | package body level | `use type Ada.Streams.Stream_Element_Offset;` |
| 3 | 30 | package body level | `use type Interfaces.Unsigned_64;` |
| 4 | 31 | package body level | `use type System.Address;` |
| 5 | 32 | package body level | `use type System.Storage_Elements.Integer_Address;` |
| 6 | 51 | `Get_Byte` | `use System.Storage_Elements;` |
| 7 | 61 | `Put_Byte` | `use System.Storage_Elements;` |
| 8 | 93 | `Hash_File` | `package SIO renames Ada.Streams.Stream_IO;` |
| 9 | 508 | `Evaluation_Roster_Complete` | `use System.Storage_Elements;` |
| 10 | 565 | `Layout_Offset` | `use System.Storage_Elements;` |
| 11 | 672 | `Authority_Glue` body | `package A renames Worldline.Evaluation_Authority;` |
| 12 | 673 | `Authority_Glue` body | `package W renames A.W;` |
| 13 | 674 | `Authority_Glue` body | `package C renames Worldline.Collapse_Wire;` |
| 14 | 675 | `Authority_Glue` body | `use type System.Address;` |
| 15 | 676 | `Authority_Glue` body | `use System.Storage_Elements;` |
| 16 | 745 | `Dependencies` | `use type A.Raw_Dependency;` |
| 17 | 761 | `Decide_Raw_Context` | `package K renames Evaluation_Completion_C;` |
| 18 | 762 | `Decide_Raw_Context` | `package T renames Evaluation_Completion;` |
| 19 | 763 | `Decide_Raw_Context` | `use type Interfaces.C.int;` |
| 20 | 764 | `Decide_Raw_Context` | `use type K.U32;` |
| 21 | 777 | `Decide_Raw_Context` (inner block) | `use type A.Raw_Dependency;` |
| **22** | **836** | **`Decide_Raw_Metadata`** | **`package K renames Evaluation_Completion_C;` (deleted at PK-6b: R-DEL-1 = GE9)** |
| 23 | 837 | `Decide_Raw_Metadata` | `use type Interfaces.C.int;` |
| 24 | 845 | `Decide_Raw_Metadata` (inner block) | `use type A.Raw_Dependency;` |
| 25 | 879 | package body level | `package Owner_Wire renames Worldline.Owner_Transitions_Wire;` |
| 26 | 880 | package body level | `package Owner_Kernel renames Worldline.Owner_Transitions;` |
| 27 | 881 | package body level | `package Owner_History renames Evaluation_History;` |
| 28 | 982 | `Owner_Authorize` | `use System.Storage_Elements;` |
| 29 | 983 | `Owner_Authorize` | `use type Owner_History.Byte_Count;` |
| 30 | 1024 | package body level | `package Retry_Wire renames Worldline.Owner_Retry_Audit_Wire;` |
| 31 | 1025 | package body level | `package Retry_Kernel renames Worldline.Owner_Retry_Audit;` |
| 32 | 1026 | package body level | `package Join_Wire renames Worldline.Owner_Conjunction_Wire;` |
| 33 | 1027 | package body level | `package Join_Kernel renames Worldline.Owner_Conjunction;` |
| 34 | 1070 | `Owner_Audit_Decide` | `use System.Storage_Elements;` |
| 35 | 1071 | `Owner_Audit_Decide` | `use type Owner_History.Byte_Count;` |

v3 claimed that the `K` renamings at `:761` and `:836` "stay and name types only". That holds for `:761` (`K.Result`, `K.U32`), but not for `:836`, which loses its last reference at GE5–GE8. v4 corrects this with R-DEL-1 (B4.23).

### B9.2 Designed scopes and their exact clause tuples (`CAPI_INVENTORY`)

**Classes.**
- **T** = transported from the original unit body's package level, in original order.
- **L** = transported from the original subprogram.
- **A** = added, with the reason given.

**Rule (R-INV), with its derivation.**
- A transport specification holds its unit's package-level clauses in original order (class T). It excludes exactly the renamings that no transported text references; those are listed below, and keeping them would draw a `-gnatwu` warning (B4.23).
- An export body holds `use <Unit>_Transport;`, then the unit's package-level **use** clauses in original order (class T), then the original subprogram's own clauses (class L), then listed additions (class A). Renamings are not repeated in export bodies; they are use-visible through `use <Unit>_Transport;`.
- Transport bodies and `Diagnostic_Transport` hold no clause.

**Transport specifications (class T; one contiguous N1 string each).**

| Id = scope | Clause tuple | S5 source | Not transported |
|---|---|---|---|
| CL-T1 = `spec:Resources_Transport` | `use type Interfaces.Unsigned_8; use type Interfaces.C.size_t; use type System.Address; use System.Storage_Elements;` | resources `:7-10` | — |
| CL-T2 = `spec:Recovery_Transport` | `package R renames Worldline.Recovery; use type R.Byte_Count; use type Size; use type Interfaces.Unsigned_8; use type System.Address; use System.Storage_Elements;` | recovery `:6-7`, `:9-12` | `subtype Size …` (`:8`) is a declaration, not transported (P2) |
| CL-T3 = `spec:Recovery_Authorization_Transport` | `package W renames Worldline.Recovery_Authorization_Wire; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int;` | v2 `:6-11` | — |
| CL-T4 = `spec:Recovery_Authorization_V3_Transport` | `package W renames Worldline.Recovery_Authorization_V3_Wire; package Q renames Resource_Quantities; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int; use type Q.Byte_Count;` | v3 `:7-14` | — |
| CL-T5 = `spec:Recovery_Protocol_Transport` | `package W renames Worldline.Recovery_Protocol_Wire; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int;` | protocol `:6-11` | — |
| CL-T6 = `spec:Lifecycle_Transport` | `use type U8; use type Size; use type System.Address; use System.Storage_Elements; package L renames Resource_Reservation_Lifecycle; package R renames Worldline.Resources; use type L.Result_Status;` | lifecycle `:7-13` | — |
| CL-T7 = `spec:Ledger_Transport` | `use type U8; use type Size; use type System.Address; use System.Storage_Elements; package Q renames Resource_Quantities; package L renames Resource_Ledger; use type Q.Byte_Count;` | ledger `:7-13` | — |
| CL-T8 = `spec:Policy_Transport` | `use type U8; use type Size; use type System.Address; use System.Storage_Elements; package Q renames Resource_Quantities; package P renames Resource_Admission; use type Q.Byte_Count;` | policy `:7-13` | — |
| CL-T9 = `spec:History_Transport` | `package H renames Evaluation_History; package R renames Resource_Quantities; use type U8; use type R.Byte_Count; use type Size; use type System.Address; use System.Storage_Elements;` | history `:7-13` | — |
| CL-T10 = `spec:Pending_Transport` | `package E renames Evaluation_Pending; use type System.Address; use type I64; use type U32; use type E.Count; use System.Storage_Elements;` | pending v1 `:6-11` | — |
| CL-T11 = `spec:Pending_V2_Transport` | `package E renames Evaluation_Pending; package V2 renames Evaluation_Pending_V2; use type System.Address; use type I64; use type U32; use type E.Count; use System.Storage_Elements;` | pending v2 `:7-13` | — |
| CL-T12 = `spec:Run_Ledger_Transport` | `package Q renames Resource_Quantities; package W renames Resource_Run_Ledger_Wire; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int; use type Q.Byte_Count;` | run ledger `:6-13` | — |
| CL-T13 = `spec:Chain_Transport` | `package W renames Worldline.Chain_Authority_Wire; package A renames W.A; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int; use type A.Q.Byte_Count;` | chain `:5-12` | — |
| CL-T14 = `spec:Completion_Transport` | `package P renames Evaluation_Pending; package V renames Evaluation_Pending_V2; package T renames Evaluation_Completion; package H renames Evaluation_History; package Roster renames Evaluation_Completion_Roster; package Raw_Roster renames Evaluation_Raw_Roster; package W renames Worldline.Evaluation_Wire; use type P.Byte; use type System.Address; use type I64; use type U32; use type P.Count; use type H.Byte_Count; use type T.Decision; use System.Storage_Elements;` | completion `:15-18`, `:20-23`, `:25-31` | `package E renames Worldline.Evaluation;` (`:19`): referenced only by SPARK decoders and decisions |
| CL-T15 = `spec:Finalization_Transport` | `package F renames Evaluation_Finalization; package P renames F.P; package R renames F.R; package W renames F.W; package K renames Evaluation_Completion_C; package CW renames Worldline.Collapse_Wire; package Authority renames Worldline.Evaluation_Authority; use type Interfaces.C.int; use type Authority.Raw_Dependency; use type System.Address; use type I64; use type U32; use type U8; use type P.Count; use type F.Capture_Decision; use type F.Seal_Decision; use System.Storage_Elements;` | finalization `:9`, `:11-12`, `:14-27` | `package T renames F.T;` (`:10`) and `package H renames F.H;` (`:13`): referenced only by SPARK decoders and decisions |

**Export bodies and moved subprograms.**

| Scope | Clause tuple (N1, in order) | Classes |
|---|---|---|
| `Resources_Can_Reserve` | `use Resources_Transport; use type Interfaces.Unsigned_8; use type Interfaces.C.size_t; use type System.Address; use System.Storage_Elements;` | T |
| `Recovery_Select` | `use Recovery_Transport; use type R.Byte_Count; use type Size; use type Interfaces.Unsigned_8; use type System.Address; use System.Storage_Elements;` | T |
| `Recovery_Authorization_Decide_V2` | `use Recovery_Authorization_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int;` | T |
| `Recovery_Authorization_Decide_V3` | `use Recovery_Authorization_V3_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int; use type Q.Byte_Count;` | T |
| `Recovery_Protocol_Decide_V1` | `use Recovery_Protocol_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int;` | T |
| `Reservation_Lifecycle_Plan` | `use Lifecycle_Transport; use type U8; use type Size; use type System.Address; use System.Storage_Elements; use type L.Result_Status;` | T |
| `Resource_Ledger_Compute`, `Resource_Ledger_Headroom` | `use Ledger_Transport; use type U8; use type Size; use type System.Address; use System.Storage_Elements; use type Q.Byte_Count;` | T |
| `Resource_Policy_Admit` | `use Policy_Transport; use type U8; use type Size; use type System.Address; use System.Storage_Elements; use type Q.Byte_Count;` | T |
| `Evaluation_History_Select` | `use History_Transport; use type U8; use type R.Byte_Count; use type Size; use type System.Address; use System.Storage_Elements;` | T |
| `Pending_Decide_V1` | `use Pending_Transport; use type System.Address; use type I64; use type U32; use type E.Count; use System.Storage_Elements;` | T |
| `Pending_Decide_V2` | `use Pending_V2_Transport; use type System.Address; use type I64; use type U32; use type E.Count; use System.Storage_Elements;` | T |
| `Run_Ledger_Check` | `use Run_Ledger_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int; use type Q.Byte_Count;` | T |
| `Chain_Replay` | `use Chain_Transport; use System.Storage_Elements; use type System.Address; use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int; use type A.Q.Byte_Count;` | T |
| `Completion_Decide`, `Completion_Raw_Decide` | `use Completion_Transport; use type P.Byte; use type System.Address; use type I64; use type U32; use type P.Count; use type H.Byte_Count; use type T.Decision; use System.Storage_Elements; use type Interfaces.C.int;` | T; **A** `use type Interfaces.C.int;` makes `Status /= 0` (segment 10) legal; the completion unit never compared a `C.int` |
| `Completion_Metadata_Matches` | `use Completion_Transport; use type P.Byte; use type System.Address; use type I64; use type U32; use type P.Count; use type H.Byte_Count; use type T.Decision; use System.Storage_Elements; package CA renames Worldline.Evaluation_Authority;` | T; L (`:911`) |
| `Native_Diagnostic_Control` | none | — |
| `Finalization_Decide`, `Finalization_Decide_Mixed` | `use Finalization_Transport; use type Interfaces.C.int; use type Authority.Raw_Dependency; use type System.Address; use type I64; use type U32; use type U8; use type P.Count; use type F.Capture_Decision; use type F.Seal_Decision; use System.Storage_Elements;` | T |
| `Completion_Transport.Context_Matches` | `package CA renames Worldline.Evaluation_Authority; package CW renames Worldline.Collapse_Wire; use type W.Raw_Record; use type Evaluation_Completion_C.Join_Verdict;` | L (`:736`, `:737`, `:741`); **A** `use type Evaluation_Completion_C.Join_Verdict;` makes `V = …` (segment 8) legal |
| `Completion_Transport.Metadata_Base`, `Finalization_Transport.Final_Context_Matches` | none | — |
| `body:T` for every transport, `spec:Diagnostic_Transport`, `body:Diagnostic_Transport` | none | — |

**Notes.**
- `use type U8;`, `use type Size;`, `use type I64;` and `use type U32;` resolve to the `Worldline.C_API` subtypes of §3.6. These denote the same first subtypes as the originals' unit subtypes, so `use type` acts on the same types.
- Some transported `use type` clauses duplicate a C_API package-level clause (B9.1 indices 0–5). For example, `use type System.Address;` is already in effect throughout the body. The installed User's Guide lists no redundant-use-clause warning among `-gnatwr` constructs (`gnat_ugn.info:8826-8851`). Whether GNAT 16.1.0 diagnoses any transported clause in its new scope is OPEN (D-38). The remedy for a diagnosed clause is a reviewed amendment of this table, never a suppression.
- **The SPARK unit bodies.** After their moves they no longer contain the transported raw code. Each packet removes, from the SPARK unit, the context and use clauses that only the moved text used (for example `with Ada.Unchecked_Conversion;`, `with System.Address_To_Access_Conversions;`, and `use System.Storage_Elements;` where unreferenced). Those edits are bound by the unit pins and the packet review. Any warning they leave is a strict obligation; there is no waiver.

### B9.3 Transported helpers (`HELPERS[T]`; sha256 of the isolated N1 text in the S5 unit body)

Observed by a read-only script over S5 (116 helpers). Each helper's successor text must hash identically (R-TRANS). Kinds: `type` (access type), `fn_inst`/`pkg_inst` (generic instance), `expr` (expression function), `body` (subprogram body; declared by profile in the specification).

| Transport | Kind | Helper | S5 line | sha256 |
|---|---|---|---|---|
| Resources_Transport | type | Byte_Access | resources:12 | `24c8b9524af4944a82b386a2aed0e77b15fcbb5f2021f732fcd4fcb09b2d9972` |
| Resources_Transport | fn_inst | As_Byte | resources:13 | `b87e1eb751f1d27e4aed1716aecb31af712312de7dc8e2cf95d2491bf1429104` |
| Resources_Transport | expr | Valid | resources:18 | `cee0c6ccec6f3b8b2342fe84c803324f5c7e38100fb42a2c6b5e7d8237c28918` |
| Resources_Transport | body | Decode | resources:23 | `1563c9b6d7ff2d0f500bd4b3de8448b82f85621fc43b3a707e5d41db63945f14` |
| Recovery_Transport | type | Byte_Access | recovery:13 | `56b865d21050f4a60ac67372dcb96e04fe60f24150e08b88fa1f72065193b4d1` |
| Recovery_Transport | fn_inst | As_Byte | recovery:14 | `b87e1eb751f1d27e4aed1716aecb31af712312de7dc8e2cf95d2491bf1429104` |
| Recovery_Transport | expr | Shape | recovery:18 | `826f4ae9afcd3629b5100c6b01a64d88d30123644c0d914b3be48e793cb963ea` |
| Recovery_Transport | body | Copy | recovery:26 | `dfd8d084f7244297d30ddfb9338292c1f78392a2b112d2bc0890d762582be820` |
| Recovery_Authorization_Transport | type | Request_Access | v2:12 | `5f45efa1b0a7384ce28173a7b43da10923c1ce88eb8b1b34d2a5ced452536bff` |
| Recovery_Authorization_Transport | type | Result_Access | v2:13 | `68052d5f3e2198b0846ed1038315b5dae23bce5499d574e279919c30b2c63db2` |
| Recovery_Authorization_Transport | fn_inst | Request_At | v2:14 | `a143b3077f0df6ba3bc975ca996b1053002a61a780abf8594efaf2d36110cc66` |
| Recovery_Authorization_Transport | fn_inst | Result_At | v2:16 | `4c0c8c0ed218d8e91f50c2af131213fee3ed30f7fb136549c131ac1194954a4e` |
| Recovery_Authorization_Transport | expr | Shape | v2:116 | `e9afdbc7f30226c9729a4111dcc85460c1e4f4d589859f4cdd89a1ec3594164b` |
| Recovery_Authorization_V3_Transport | type | Byte_Access | v3:15 | `3acb790d3910eb1e72db32208ca9c35cc5b22bf235a3edb4ebe3adfbc753d345` |
| Recovery_Authorization_V3_Transport | fn_inst | Byte_At | v3:16 | `826ce762bd5549ad59d24cbaaed21a20883cab90a4f5412790f0683e25e1ddc9` |
| Recovery_Authorization_V3_Transport | type | Request_Access | v3:18 | `5f45efa1b0a7384ce28173a7b43da10923c1ce88eb8b1b34d2a5ced452536bff` |
| Recovery_Authorization_V3_Transport | type | Result_Access | v3:19 | `68052d5f3e2198b0846ed1038315b5dae23bce5499d574e279919c30b2c63db2` |
| Recovery_Authorization_V3_Transport | fn_inst | Request_At | v3:20 | `a143b3077f0df6ba3bc975ca996b1053002a61a780abf8594efaf2d36110cc66` |
| Recovery_Authorization_V3_Transport | fn_inst | Result_At | v3:22 | `4c0c8c0ed218d8e91f50c2af131213fee3ed30f7fb136549c131ac1194954a4e` |
| Recovery_Authorization_V3_Transport | expr | Shape | v3:125 | `e9afdbc7f30226c9729a4111dcc85460c1e4f4d589859f4cdd89a1ec3594164b` |
| Recovery_Protocol_Transport | type | Request_Access | protocol:12 | `5f45efa1b0a7384ce28173a7b43da10923c1ce88eb8b1b34d2a5ced452536bff` |
| Recovery_Protocol_Transport | type | Result_Access | protocol:13 | `68052d5f3e2198b0846ed1038315b5dae23bce5499d574e279919c30b2c63db2` |
| Recovery_Protocol_Transport | fn_inst | Request_At | protocol:14 | `a143b3077f0df6ba3bc975ca996b1053002a61a780abf8594efaf2d36110cc66` |
| Recovery_Protocol_Transport | fn_inst | Result_At | protocol:15 | `4c0c8c0ed218d8e91f50c2af131213fee3ed30f7fb136549c131ac1194954a4e` |
| Recovery_Protocol_Transport | expr | Shape | protocol:40 | `e9afdbc7f30226c9729a4111dcc85460c1e4f4d589859f4cdd89a1ec3594164b` |
| Lifecycle_Transport | type | Byte_Access | lifecycle:15 | `6d804273ec478f6e7cb1ba66a542976aad4f5b6ba00e0d7739cbccd8c114e302` |
| Lifecycle_Transport | type | Row_Access | lifecycle:16 | `1e945f7a83c020a402895848e06d488b7b31daef06ab4eb7d179d0c97cf5798f` |
| Lifecycle_Transport | fn_inst | As_Byte | lifecycle:17 | `b87e1eb751f1d27e4aed1716aecb31af712312de7dc8e2cf95d2491bf1429104` |
| Lifecycle_Transport | fn_inst | As_Row | lifecycle:18 | `1da72227cd1cda4c876ab81a4cf133798b5165f11aa9110de5a623e1be6b308c` |
| Lifecycle_Transport | expr | Extent_Valid | lifecycle:33 | `64998e141fc8c80fed40acaec4806c0d51b45dfad645ed0803d12137c8d65f3e` |
| Lifecycle_Transport | body | Copy_Data | lifecycle:43 | `c09cd5b321d2b2c0107a0f490ab237ac1632b44ef138eb6c3a97ed0de7587808` |
| Ledger_Transport | type | Byte_Access | ledger:15 | `3acb790d3910eb1e72db32208ca9c35cc5b22bf235a3edb4ebe3adfbc753d345` |
| Ledger_Transport | type | Row_Access | ledger:16 | `1e945f7a83c020a402895848e06d488b7b31daef06ab4eb7d179d0c97cf5798f` |
| Ledger_Transport | type | Quantity_Access | ledger:17 | `605aab1f07967c80d5764b97eb857e53a2c856db44a704d81a0051c1e0918079` |
| Ledger_Transport | type | Result_Access | ledger:18 | `f387a84c416f7e2601624d8366892780f147823c88ca9f5929affb40a679d832` |
| Ledger_Transport | fn_inst | As_Byte | ledger:19 | `b87e1eb751f1d27e4aed1716aecb31af712312de7dc8e2cf95d2491bf1429104` |
| Ledger_Transport | fn_inst | As_Row | ledger:20 | `1da72227cd1cda4c876ab81a4cf133798b5165f11aa9110de5a623e1be6b308c` |
| Ledger_Transport | fn_inst | As_Quantity | ledger:21 | `237bf5443967ce30af9b844411c8a479b8127e230f3bc3c223f7219d348beb93` |
| Ledger_Transport | fn_inst | As_Result | ledger:23 | `2e9a9bf55902c73a0d0d772fdf91d386a38d8e58eae039cd84163b30306c6442` |
| Ledger_Transport | expr | Extent_Valid | ledger:64 | `64998e141fc8c80fed40acaec4806c0d51b45dfad645ed0803d12137c8d65f3e` |
| Ledger_Transport | body | Copy_Data | ledger:90 | `4e329875319b082905d9cebab41b4ded98f089441f12ea3b2030b1eaf67f388b` |
| Ledger_Transport | body | Write_Data | ledger:101 | `7fbdb7418028c11d44ca92ba8be2d80ae75b220235628f327e3e5a2a911bd35c` |
| Policy_Transport | type | Byte_Access | policy:15 | `3acb790d3910eb1e72db32208ca9c35cc5b22bf235a3edb4ebe3adfbc753d345` |
| Policy_Transport | type | Input_Access | policy:16 | `22eaaf064d3d597c2e6be266f517f7b52a810dbe7f9f4d1ab01b6ce632a5a86e` |
| Policy_Transport | type | Disk_Access | policy:17 | `1a0433cfebdfb7a4dc0eb19bc3252a3ef4fe7317938a91bf75dce3ceb71fb9ba` |
| Policy_Transport | type | Result_Access | policy:18 | `f387a84c416f7e2601624d8366892780f147823c88ca9f5929affb40a679d832` |
| Policy_Transport | fn_inst | As_Byte | policy:19 | `b87e1eb751f1d27e4aed1716aecb31af712312de7dc8e2cf95d2491bf1429104` |
| Policy_Transport | fn_inst | As_Input | policy:20 | `bf4d57bc5d010fd135caba6de27b919cce1b104e782c8333beb6bff41a160ea8` |
| Policy_Transport | fn_inst | As_Disk | policy:21 | `fa2ba12c9547f598f68d0b7d39714e2d68de9c701d5a0cba48dee9511b7600da` |
| Policy_Transport | fn_inst | As_Result | policy:22 | `2e9a9bf55902c73a0d0d772fdf91d386a38d8e58eae039cd84163b30306c6442` |
| Policy_Transport | expr | Extent_Valid | policy:78 | `64998e141fc8c80fed40acaec4806c0d51b45dfad645ed0803d12137c8d65f3e` |
| Policy_Transport | body | Decode_Data | policy:102 | `5167aa5a692cd12d68655752b3fa2e8bd40d8384a667313e457ec06461cb2240` |
| History_Transport | type | Byte_Access | history:14 | `6d804273ec478f6e7cb1ba66a542976aad4f5b6ba00e0d7739cbccd8c114e302` |
| History_Transport | type | Row_Access | history:15 | `1e945f7a83c020a402895848e06d488b7b31daef06ab4eb7d179d0c97cf5798f` |
| History_Transport | type | Query_Access | history:16 | `0edc36c8f4fe077af41a6918b9d4dd2e6c42da2512a8080289683174c604dae4` |
| History_Transport | type | Selection_Access | history:17 | `c3b14b33efc2fe933c563efbd14cc31d6037b804c7df983ec042ca058c9d59c4` |
| History_Transport | fn_inst | As_Byte | history:18 | `b87e1eb751f1d27e4aed1716aecb31af712312de7dc8e2cf95d2491bf1429104` |
| History_Transport | fn_inst | As_Row | history:19 | `1da72227cd1cda4c876ab81a4cf133798b5165f11aa9110de5a623e1be6b308c` |
| History_Transport | fn_inst | As_Query | history:20 | `b49c67788cc4c9bf6ca1b5240eb9c39a57b56277bdf1a9fb64e0416bb6812db6` |
| History_Transport | fn_inst | As_Selection | history:21 | `0f79eb1a1eb4a2e0dba6f2b123c34ab582ba2bbc335bd22966d7f1bf5633f6e5` |
| History_Transport | expr | Extent_Valid | history:66 | `d1bc80d97c1e2424096d66f29fdb64fc2c0880ae12f37717894a2bcf4d29343e` |
| History_Transport | body | Copy_Data | history:115 | `d1ec124c69f2841f4a37c4155a8de8546c554d266b23dd094a95db1328bc9652` |
| Pending_Transport | pkg_inst | Request_Pointers | pending:12 | `43441790fda792c5def96ccd3771ce72d48f189990c12549089f4ba4bb4835b4` |
| Pending_Transport | pkg_inst | Result_Pointers | pending:13 | `d9162042e8fbed15c5ca22831ff94e3f5f10c977a9e36f4e6559ce7b252a3832` |
| Pending_Transport | pkg_inst | Row_Pointers | pending:14 | `d627a68c65c2d13096adfe585c100dac360e6a3ad5dc140ed487e21337b72b5a` |
| Pending_Transport | pkg_inst | Byte_Pointers | pending:15 | `7cfd61aa9ad6d503d23d3758c0196cfc4dfe27407386fc35779a746768cfdf77` |
| Pending_Transport | expr | Extent_Valid | pending:67 | `9d4f674d1c8aa48793eada169fcc93203981defea7e7e4a2a778a552878ce9eb` |
| Pending_Transport | expr | Disjoint | pending:77 | `523581046cf093f02e236502214145909393585688da0f4f0dc187e9ea80c0f8` |
| Pending_Transport | body | Copy_Data | pending:95 | `9cb1e57423be334f76cee66d3fbeb537fed20d2655b83d2ba9b56e5ab7c48a24` |
| Pending_V2_Transport | pkg_inst | Request_Pointers | pending_v2:14 | `43441790fda792c5def96ccd3771ce72d48f189990c12549089f4ba4bb4835b4` |
| Pending_V2_Transport | pkg_inst | Result_Pointers | pending_v2:15 | `d9162042e8fbed15c5ca22831ff94e3f5f10c977a9e36f4e6559ce7b252a3832` |
| Pending_V2_Transport | pkg_inst | Row_Pointers | pending_v2:16 | `d627a68c65c2d13096adfe585c100dac360e6a3ad5dc140ed487e21337b72b5a` |
| Pending_V2_Transport | pkg_inst | Byte_Pointers | pending_v2:17 | `7cfd61aa9ad6d503d23d3758c0196cfc4dfe27407386fc35779a746768cfdf77` |
| Pending_V2_Transport | expr | Extent_Valid | pending_v2:78 | `9d4f674d1c8aa48793eada169fcc93203981defea7e7e4a2a778a552878ce9eb` |
| Pending_V2_Transport | expr | Disjoint | pending_v2:88 | `523581046cf093f02e236502214145909393585688da0f4f0dc187e9ea80c0f8` |
| Pending_V2_Transport | body | Copy_Data | pending_v2:116 | `9cb1e57423be334f76cee66d3fbeb537fed20d2655b83d2ba9b56e5ab7c48a24` |
| Run_Ledger_Transport | type | Packet_Access | run_ledger:14 | `2a8679003161811660ffd9d4e8a1fa9084f43ae7375f0c6540bae1f0ceda9c22` |
| Run_Ledger_Transport | fn_inst | Packet_At | run_ledger:15 | `cd692f0ccac2e1108e2e168ea5ef6672230a51723756a93ffb58bb7011f4cebe` |
| Run_Ledger_Transport | type | Result_Access | run_ledger:16 | `68052d5f3e2198b0846ed1038315b5dae23bce5499d574e279919c30b2c63db2` |
| Run_Ledger_Transport | fn_inst | Result_At | run_ledger:17 | `4c0c8c0ed218d8e91f50c2af131213fee3ed30f7fb136549c131ac1194954a4e` |
| Run_Ledger_Transport | type | Row_Access | run_ledger:18 | `d02a51e4e21d1e7944b66f1b1d8ca5409037b11761d48aa38ad304391543532f` |
| Run_Ledger_Transport | fn_inst | Row_At | run_ledger:19 | `efa1bf5fdf12a9877275938fc1789ce6bbed5184040734ccf01326af49cac591` |
| Run_Ledger_Transport | type | Native_Access | run_ledger:20 | `0758e608df38e6cff988c413aa99b36ebc5e24547c0461cd809f039b60908bcf` |
| Run_Ledger_Transport | fn_inst | Native_At | run_ledger:21 | `68f0ca91073a259dd4958cbc3203a4c86725c305ebdd96174d9c06196e8af6fc` |
| Run_Ledger_Transport | type | Byte_Access | run_ledger:22 | `3acb790d3910eb1e72db32208ca9c35cc5b22bf235a3edb4ebe3adfbc753d345` |
| Run_Ledger_Transport | fn_inst | Byte_At | run_ledger:23 | `826ce762bd5549ad59d24cbaaed21a20883cab90a4f5412790f0683e25e1ddc9` |
| Run_Ledger_Transport | expr | Shape | run_ledger:25 | `e9afdbc7f30226c9729a4111dcc85460c1e4f4d589859f4cdd89a1ec3594164b` |
| Run_Ledger_Transport | expr | Array_Shape | run_ledger:29 | `4cb16d508d01e77c9875609cfa299dae60ac658a6f5300137839823be50db433` |
| Chain_Transport | type | Anchors_Access | chain:13 | `b4edcd82d7f50b2b894af24c655489cdb38dfd2cf76781e3b1da371f47f0f772` |
| Chain_Transport | type | Row_Access | chain:14 | `d02a51e4e21d1e7944b66f1b1d8ca5409037b11761d48aa38ad304391543532f` |
| Chain_Transport | type | Result_Access | chain:15 | `68052d5f3e2198b0846ed1038315b5dae23bce5499d574e279919c30b2c63db2` |
| Chain_Transport | fn_inst | Anchors_At | chain:16 | `022572b0f4c2ad5ac4ec51af966b2a583cec838eb74b01952d2bf83b1ab1317e` |
| Chain_Transport | fn_inst | Row_At | chain:17 | `efa1bf5fdf12a9877275938fc1789ce6bbed5184040734ccf01326af49cac591` |
| Chain_Transport | fn_inst | Result_At | chain:18 | `4c0c8c0ed218d8e91f50c2af131213fee3ed30f7fb136549c131ac1194954a4e` |
| Chain_Transport | expr | Shape | chain:60 | `e9afdbc7f30226c9729a4111dcc85460c1e4f4d589859f4cdd89a1ec3594164b` |
| Completion_Transport | pkg_inst | Raw_Records | completion:24 | `c086e887b89b39d3c1fc94d9667a6717c33cd9f76563dcbba13dd88bc8607f21` |
| Completion_Transport | pkg_inst | Requests | completion:32 | `3647e7aa9e501e4e7c66c4c7ec5ed3127d5cfa8b22086992b3c7c7d15b949a61` |
| Completion_Transport | pkg_inst | Outputs | completion:33 | `393d82bcf198ba5b186b022ba4ea9c9028df6cd9f492bb1f9b4fcaae38a28512` |
| Completion_Transport | pkg_inst | Journals | completion:34 | `43da75589173347b1c76806583f61b34b8f382f8f466937706ec371cb4f9c1d0` |
| Completion_Transport | pkg_inst | Checks | completion:35 | `5b2e7821009ddbc312ec7fb912dd4c1927249583adbf25f4b12c7906966dc258` |
| Completion_Transport | pkg_inst | Histories | completion:36 | `a4e02e24f06ada65896c9ee3bbdbfc40348a41d019cf2015caa56f00311bd64b` |
| Completion_Transport | pkg_inst | Requirements | completion:37 | `524e8d5f6efde221f19a581ea70cc3e7a9f9bac33a856a28e5c85ec70df9bdc2` |
| Completion_Transport | pkg_inst | Octets | completion:38 | `38b209420239751058cf52f8a61c48cdc5e53f9acc694ebc443f92bada97d1d7` |
| Completion_Transport | expr | Extent_Valid | completion:258 | `9d4f674d1c8aa48793eada169fcc93203981defea7e7e4a2a778a552878ce9eb` |
| Completion_Transport | expr | Disjoint | completion:266 | `6024f7a9f832d3d66ba3e26ccab3731ee9ab38493dc2d06b3713a75397047be4` |
| Completion_Transport | expr | Array_Valid | completion:272 | `1f04ec717050fedabb23553cc812d8e848e85ef229d33590478ba8e48b9e5c21` |
| Completion_Transport | body | Copy_Data | completion:385 | `5cd961c965062568a987aa4b76e0ef7644e053138d423769c82fd8ae012543ab` |
| Finalization_Transport | pkg_inst | Requests | finalization:28 | `3647e7aa9e501e4e7c66c4c7ec5ed3127d5cfa8b22086992b3c7c7d15b949a61` |
| Finalization_Transport | pkg_inst | Outputs | finalization:29 | `393d82bcf198ba5b186b022ba4ea9c9028df6cd9f492bb1f9b4fcaae38a28512` |
| Finalization_Transport | pkg_inst | Rows | finalization:30 | `eac5f4ad45becec6fbd8035617b96e21e0b05319cea2eab85f16177385fd2173` |
| Finalization_Transport | pkg_inst | Plans | finalization:31 | `13f5c23ed05b4f28155611663d59c2506c55091fc6041341f5150079d1635720` |
| Finalization_Transport | pkg_inst | Octets | finalization:32 | `38b209420239751058cf52f8a61c48cdc5e53f9acc694ebc443f92bada97d1d7` |
| Finalization_Transport | expr | Extent_Valid | finalization:35 | `9d4f674d1c8aa48793eada169fcc93203981defea7e7e4a2a778a552878ce9eb` |
| Finalization_Transport | expr | Disjoint | finalization:43 | `6024f7a9f832d3d66ba3e26ccab3731ee9ab38493dc2d06b3713a75397047be4` |
| Finalization_Transport | expr | Array_Valid | finalization:49 | `1f04ec717050fedabb23553cc812d8e848e85ef229d33590478ba8e48b9e5c21` |
| Finalization_Transport | body | Copy_Data | finalization:112 | `0cf22b89d0b01651aa3a6033f172df6296d92a650efd81c525c49b9b06f83da5` |

Short names: resources = `core/worldline-resources_c_api.adb`; recovery = `core/worldline-recovery_c_api.adb`; v2 = `core/worldline-recovery_authorization_c_api.adb`; v3 = `core/worldline-recovery_authorization_v3_c_api.adb`; protocol = `core/worldline-recovery_protocol_c_api.adb`; lifecycle = `core/worldline-reservation_lifecycle_c_api.adb`; ledger = `core/worldline-resource_ledger_c_api.adb`; policy = `core/worldline-resource_policy_c_api.adb`; history = `core/worldline-evaluation_history_c_api.adb`; pending = `core/evaluation_pending_c.adb`; pending_v2 = `core/evaluation_pending_v2_c.adb`; run_ledger = `core/resource_run_ledger_c_api.adb`; chain = `core/worldline-chain_authority_c_api.adb`; completion = `core/evaluation_completion_c.adb`; finalization = `core/evaluation_finalization_c.adb`. Identical hashes in different rows mean that the original units contain text-identical helpers; each transport still carries its own copy (no cross-unit sharing, D-08).

### B9.4 SPARK units and alias exclusion (`CAPI_ALIAS_FORBIDDEN`)

**`CAPI_SPARK_UNITS`** are the units that own Appendix C names (a read-only script confirmed that this set equals the set of unit prefixes of the Appendix C names): `Worldline.Resources_C_API`, `Worldline.Recovery_C_API`, `Worldline.Recovery_Authorization_C_API`, `Worldline.Recovery_Authorization_V3_C_API`, `Worldline.Reservation_Lifecycle_C_API`, `Worldline.Resource_Ledger_C_API`, `Worldline.Resource_Policy_C_API`, `Worldline.Evaluation_History_C_API`, `Resource_Run_Ledger_C_API`, `Worldline.Chain_Authority_C_API`, `Evaluation_Completion_C`, `Evaluation_Completion_Roster`, `Evaluation_Finalization_C`, `Evaluation_Pending_C`, `Evaluation_Pending`, `Evaluation_Pending_V2_C` and `Evaluation_Pending_V2`.

**Renamings in designed or residual scopes whose target is such a unit,** directly or through the renaming they are defined by:
- `E` → `Evaluation_Pending` (both pending transports);
- `V2` → `Evaluation_Pending_V2`;
- `P` → `Evaluation_Pending` (completion transport) and `F.P` = `Evaluation_Finalization.P` → `T.P` → `Evaluation_Pending` (finalization transport; `core/evaluation_finalization.ads:12-13` and `core/evaluation_completion.ads:10`, observed);
- `V` → `Evaluation_Pending_V2`;
- `Roster` → `Evaluation_Completion_Roster`;
- `K` → `Evaluation_Completion_C` (finalization transport and residual B9.1 index 17).

`P` also names `Resource_Admission` in the policy transport. The exclusion below is body-wide and therefore conservative: it can only refuse more, never less.

**Forbidden selections** (each pattern must occur zero times in the C_API body):
- `E.Decide`, `P.Decide`, `V2.Decide`, `V.Decide`, `Roster.Classify`;
- `K.` followed by any of the `Evaluation_Completion_C` Appendix C simple names (36, observed by a read-only script as the `Evaluation_Completion_C.` lines of v3 Appendix C, which v4 carries unchanged): `Decide_Header_Valid`, `Decide_Fields_Valid`, `Accept_Journal_Row`, `Accept_Captured_Row`, `Accept_Result_Row`, `Accept_History_Row`, `Accept_Required_Row`, `Decide_Value`, `Raw_Header_Valid`, `Raw_Fields_Valid`, `Accept_Raw_Check_Row`, `Accept_Raw_Measure`, `Raw_Decide_Value`, `Context_Header_Valid`, `Context_Fields_Valid`, `Context_Agent_Matches`, `Accept_Context_Fields`, `Accept_Context_Row`, `Accept_Required_Pair`, `Context_Join_Value`, `Join_Code`, `Metadata_Version_Valid`, `Metadata_Header_Valid`, `Accept_Metadata_Row`, `Diagnostic_Control_Of`, `Diagnostic_Invalid_Code`, `Diagnostic_Start`, `Diagnostic_Stop`, `Diagnostic_Observe`, `Diagnostic_Latch_Failure`, `Diagnostic_Begin_Line`, `Diagnostic_Line`, `Diagnostic_Begin_Value`, `Diagnostic_Value_Site`, `Diagnostic_Begin_Exception`, `Diagnostic_Exception_Site`;
- `K.` followed by any name that PK-6b removes from `Evaluation_Completion_C` (O7 carried; each observed in S5 `core/evaluation_completion_c.ads`): `Decide`, `Raw_Decide`, `Metadata_Matches`, `Context_Matches`, `Metadata_Base`, `Diagnostic_Mark`, `Diagnostic_Value`, `Diagnostic_Exception`, `Diagnostic_Control`.

A pattern is `(?<![\w.])X\s*\.\s*N(?!\w)`, case-insensitive on N2. For example, `K.Diagnostic_Value` does not match `K.Diagnostic_Value_Site`, so both are listed. Type selections (`K.Result`, `K.U32`, `K.Check_Row`, `K.Required_Row`, `K.Request`, `E.Bytes`, `P.Count`, `Roster.Check_Array`, …) remain allowed.

### B9.5 Core `Library_Interface` (`CAPI_CORE_INTERFACE`; G9)

Observed by parsing the one `for Library_Interface use (…);` declaration of S5 `core/worldline_core.gpr` (71 units, lowercased, in order):

`attest, attest.sha256, worldline, worldline.world, worldline.ancestry, worldline.transitions, worldline.identities, worldline.collapse, worldline.collapse_wire, worldline.evaluation, worldline.evaluation_v2, worldline.evaluation_wire, worldline.evaluation_report_facts, worldline.evaluation_report_wire, evaluation_raw_roster, worldline.evaluation_authority, worldline.resources, worldline.resource_wire, worldline.resources_c_api, worldline.recovery, worldline.recovery_c_api, worldline.recovery_authorization, worldline.recovery_authorization_wire, worldline.recovery_authorization_c_api, worldline.recovery_authorization_v3, worldline.recovery_authorization_v3_wire, worldline.recovery_authorization_v3_c_api, resource_reservation_transition, resource_quantities, resource_admission, resource_ledger, evaluation_history, evaluation_epoch, evaluation_pending, evaluation_pending_c, evaluation_pending_v2, evaluation_pending_v2_c, evaluation_completion, evaluation_completion_c, evaluation_completion_roster, canonical_artifacts, evaluation_finalization, evaluation_finalization_c, worldline.evaluation_history_c_api, resource_reservation_lifecycle, worldline.reservation_lifecycle_c_api, worldline.resource_ledger_c_api, spark, spark.big_integers, worldline.resource_policy_c_api, worldline.causal_graph, worldline.receipts, worldline.c_api, worldline.recovery_protocol, worldline.recovery_protocol_wire, worldline.recovery_protocol_c_api, worldline.chain_authority, worldline.chain_authority_wire, worldline.chain_authority_c_api, resource_run_ledger, resource_run_ledger_wire, resource_run_ledger_c_api, worldline.owner_transitions, worldline.owner_transitions_wire, worldline.owner_retry_audit, worldline.owner_retry_audit_wire, worldline.owner_conjunction, worldline.owner_conjunction_wire, worldline.owner_subject_projection, worldline.recovery_protocol_abi, evaluation_finalization.values`

---

## B10. Write forms, provenance and gates (new; V3-RC4)

### B10.1 Forms

Every form is checked by R-W (B0.6). A *span* is an exact N1 substring that occurs once in the scope; "segment *n*" means the exact segment *n* of the scope's tile in B4. A *closed* identifier may occur only inside the listed spans, and is never assigned except as listed.

| Form | Write shape | Provenance rule | Gate rule |
|---|---|---|---|
| **WF-C** constant result object | `<target>.all := N;` | `N : constant T := <listed SPARK call>;` inside the span; `N` closed; 0 assignments | A predicate gate, if any, lies in the same span and precedes the declaration |
| **WF-A** acceptance payload | `<target>.all := N.Value;` | `N : constant Acc := <listed SPARK call>;` inside the span; `N` closed | R-GATE: `if not N.Ok then return <code>; end if;` immediately after `begin`, before `N.Value` |
| **WF-F** direct SPARK function-result store | `<target>.all := <Unit>.<Function> (<args>);` | The right-hand side is the listed SPARK function with the listed actuals. Each actual is a closed WF-O buffer or WF-C constant whose declaration and producer lie in the listed spans. | Any condition guarding the store (the lifecycle `Publishes_Mask (Status)`) lies in the span |
| **WF-O** mutable procedure-out buffer, variable or mask | (argument of a WF-F or WF-B write) | Declared once in the listed span. Its initializer is exactly the S5 one (lifecycle `Mask … := (others => False)`) or absent. It is an `out` or `in out` actual of exactly the one listed SPARK procedure call. Closed; 0 assignments. | — |
| **WF-B** buffer copy-out | `Write_Data (<address>, N);` | `N` is a WF-O buffer of the listed producer; closed | — |
| **WF-R** completion `Response` | `Outputs.To_Pointer (Output).all := Response;` | `Response : Result; Status : Interfaces.C.int;` declared once without initializers. Both are `out` actuals of exactly the one listed `Decide_Value`/`Raw_Decide_Value` call. Both closed; 0 assignments. | `if Status /= 0 then return Status; end if;` contiguous between the call and the write |
| **WF-P** protocol (S5 pattern unchanged) | `Result_At (Output).all := Owned_Result;` | `Owned_Result : W.Raw_Result := (After => 0);` is the `in out` actual and `Status` the `out` actual of `Worldline.Recovery_Protocol_ABI.Apply`. Both closed; 0 assignments. | `if Status /= Worldline.Recovery_Protocol_ABI.Success then return Status; end if;` before the write |
| **WF-X** exclusive finalization assignment | `Outputs.To_Pointer (Output).all := O.Value;` | `O : Evaluation_Finalization_C.Decide_Acceptance;` is declared once. It is assigned **exactly twice**: once as the last statement of the `then` branch and once as the only statement of the `else` branch of the one `if Evaluation_Finalization_C.Needs_Rows (X) then … end if;` statement (segment 6, the §5.1 text). `O` closed. | G21c: `if not O.Ok then return 255; end if;` immediately after `end if;`, before any `O.Value` |
| **WF-H** transport helper | the store inside `Ledger_Transport.Write_Data` | Bound by the helper hash (B9.3); the only `.all :=` in any transport | — |

### B10.2 Rows (`CAPI_WRITES`)

Row ids follow the B3 export numbers where possible. U1 and U2 write nothing, so W01 and W02 do not exist.

| Id | Scope | Target (exact N1) | Form | Spans | Closed (assignments) |
|---|---|---|---|---|---|
| W03 | `Recovery_Authorization_Decide_V2` | `Result_At (Output).all := Owned;` | WF-C (`Decide_Total (Raw)` after `if not W.Well_Formed (Raw) then return -1; end if;`) | segment 3 | `Owned` (0) |
| W04 | `Recovery_Authorization_Decide_V3` | `Result_At (Output).all := Owned;` | WF-C (`Decide_Total (Data, Raw)` after `if not W.Well_Formed (Data, Raw) then return -1; end if;`) | segment 3 | `Owned` (0) |
| W05 | `Recovery_Protocol_Decide_V1` | `Result_At (Output).all := Owned_Result;` | WF-P | segment 3 | `Owned_Result` (0), `Status` (0) |
| W06 | `Reservation_Lifecycle_Plan` | `As_Byte (Removed + Storage_Offset (I - 1)).all := Worldline.Reservation_Lifecycle_C_API.Mask_Byte (Mask (I));` | WF-F of `Mask_Byte (Mask (I))`. `Mask` is WF-O (`in out` of `L.Plan`, S5 initializer). `Status` is WF-O (`out` of `L.Plan`) and guards the store through `Publishes_Mask (Status)`. | segments 3 and 5 | `Mask` (0), `Status` (0) |
| W07 | `Resource_Ledger_Compute` | `Write_Data (Detail_Data, Detail_Arena);` | WF-B (`out` of `L.Compute`) | segments 3 and 5 | `Detail_Arena` (0) |
| W08 | `Resource_Ledger_Compute` | `Write_Data (Total_Data, Total_Arena);` | WF-B (`out` of `L.Compute`) | segments 3 and 5 | `Total_Arena` (0) |
| W09 | `Resource_Ledger_Compute` | `As_Quantity (Details + Storage_Offset (Size (I - 1) * Quantity_Size)).all := Worldline.Resource_Ledger_C_API.Encode_Quantity (Typed_Details (I));` | WF-F of `Encode_Quantity`; `Typed_Details` is WF-O (`out` of `L.Compute`) | segments 3 and 5 | `Typed_Details` (0) |
| W10 | `Resource_Ledger_Compute` | `As_Result (Result).all := Worldline.Resource_Ledger_C_API.Result_Of (Status, Total);` | WF-F of `Result_Of`; `Status`, `Total` are WF-O (`out` of `L.Compute`) | segments 3 and 5 | `Status` (0), `Total` (0) |
| W11 | `Resource_Ledger_Headroom` | `Write_Data (Output, Output_Arena);` | WF-B (`out` of `L.Compute_Headroom`) | segment 4 | `Output_Arena` (0) |
| W12 | `Resource_Ledger_Headroom` | `As_Result (Result).all := Worldline.Resource_Ledger_C_API.Result_Of (Status, Typed_Result);` | WF-F of `Result_Of`; `Status`, `Typed_Result` are WF-O (`out` of `L.Compute_Headroom`) | segment 4 | `Status` (0), `Typed_Result` (0) |
| W13 | `Resource_Policy_Admit` | `As_Result (Result).all := Worldline.Resource_Policy_C_API.Encode_Decision (Decision);` | WF-F of `Encode_Decision`; `Decision` is WF-C (`constant P.Decision := P.Admit (Arena, IA.State, Rows)`) | segment 5 | `Decision` (0) |
| W14 | `Evaluation_History_Select` | `As_Selection (Output).all := Result;` | WF-C (`Select_Result (A, History, F, QA.Item)`) | segment 6 | `Result` (0) |
| W15 | `Completion_Decide` | `Outputs.To_Pointer (Output).all := Response;` | WF-R (`Decide_Value`) | segments 4 and 10 | `Response` (0), `Status` (0) |
| W16 | `Completion_Raw_Decide` | `Outputs.To_Pointer (Output).all := Response;` | WF-R (`Raw_Decide_Value`) | segments 4 and 10 | `Response` (0), `Status` (0) |
| W17 | `Run_Ledger_Check` | `Result_At (Output).all := O.Value;` | WF-A (`Check_Decision`; gate G17) | segment 4 | `O` (0) |
| W18 | `Chain_Replay` | `Result_At (Output).all := RV.Value;` | WF-A (`Replay_Value`; gate G18b) | segment 5 | `RV` (0) |
| W19 | `Pending_Decide_V1` | `Result_Pointers.To_Pointer (Output).all := O.Value;` | WF-A (`Decide_Value`; gate G19b) | segment 6 | `O` (0) |
| W20 | `Pending_Decide_V2` | `Result_Pointers.To_Pointer (Output).all := O.Value;` | WF-A (`Decide_Value`; gate G20b) | segment 6 | `O` (0) |
| W21 | `Finalization_Decide` | `Outputs.To_Pointer (Output).all := O.Value;` | WF-X (gate G21c) | segments 4, 6 and 7 | `O` (**2**) |
| W22 | `body:Ledger_Transport` | `As_Byte (Address + Storage_Offset (I - Value'First)).all := Value (I);` | WF-H | the isolated `Write_Data` body | none |

**Non-foreign writes (no row).** The following write only Ada-owned locals, which nested exports may write through addresses (D-26):
- `Typed_Rows (I) := …`, `Slots (I) := …`, `Rows (I) := …`, `J (I) := …`, `History (I) := …`, `Captured (K) := …`, `Required (K) := …`, `F := FA.Item;`, `Projected_Rows (I) := …`, `Projected_Plans (I) := …`, `Projection := …`, `Seal_Status := …`, `P_Ready`, `S_Ready`, `Agent_Ready`, `Decision`.

They are fixed by the tiles. Payload-derived ones are covered by the gates below.

### B10.3 Gates (`CAPI_GATES`)

Each gate text is exact N1 and occurs once in its scope. The discriminant test (`.Ok` or `.Verdict`) occurs exactly once in the scope, inside the gate. Every payload selection begins after that test, including the refusal-branch reads of `FA.Rejected_Position` and `RA.Rejected_Field_Position`, which select components of the `False` and `Row_Field_Rejected` variants after the test.

| Id | Scope | Object | Gate text |
|---|---|---|---|
| G06 | `Reservation_Lifecycle_Plan` | `D` | `D : constant Worldline.Reservation_Lifecycle_C_API.Row_Acceptance := Worldline.Reservation_Lifecycle_C_API.Accept_Row (Row); begin if not D.Ok then return 255; end if;` |
| G07 | `Resource_Ledger_Compute` | `D` | `D : constant Worldline.Resource_Ledger_C_API.Row_Acceptance := Worldline.Resource_Ledger_C_API.Accept_Row (V); begin if not D.Ok then return 255; end if;` |
| G08 | `Resource_Ledger_Headroom` | `HI` | `HI : constant Worldline.Resource_Ledger_C_API.Headroom_Acceptance := Worldline.Resource_Ledger_C_API.Accept_Headroom_Inputs (A, W, F); begin if not HI.Ok then return 255; end if;` |
| G09a | `Resource_Policy_Admit` | `IA` | `IA : constant Worldline.Resource_Policy_C_API.Input_Acceptance := Worldline.Resource_Policy_C_API.Accept_Input (V); begin if not IA.Ok then return 255; end if;` |
| G09b | `Resource_Policy_Admit` | `D` | `D : constant Worldline.Resource_Policy_C_API.Disk_Acceptance := Worldline.Resource_Policy_C_API.Accept_Disk (Row); begin if not D.Ok then return 255; end if;` |
| G10a | `Evaluation_History_Select` | `QA` | `QA : constant Worldline.Evaluation_History_C_API.Query_Acceptance := Worldline.Evaluation_History_C_API.Accept_Query (Raw_Q); begin if not QA.Ok then return 255; end if;` |
| G10b | `Evaluation_History_Select` | `FA` | `FA : constant Worldline.Evaluation_History_C_API.Final_Acceptance := Worldline.Evaluation_History_C_API.Accept_Final_Row (V); begin if not FA.Ok then return 255; end if;` |
| G10c | `Evaluation_History_Select` | `D` | `D : constant Worldline.Evaluation_History_C_API.Row_Acceptance := Worldline.Evaluation_History_C_API.Accept_Row (V); begin if not D.Ok then return 255; end if;` |
| G13a | `Completion_Decide` | `JA` | `JA : constant Evaluation_Completion_C.Journal_Acceptance := Evaluation_Completion_C.Accept_Journal_Row (X); begin if not JA.Ok then return 255; end if;` |
| G13b | `Completion_Decide` | `CR` | `CR : constant Evaluation_Completion_C.Captured_Acceptance := Evaluation_Completion_C.Accept_Captured_Row (X); begin if not CR.Ok then return 255; end if;` |
| G13c | `Completion_Decide` | `RR` | `RR : constant Evaluation_Completion_C.Result_Acceptance := Evaluation_Completion_C.Accept_Result_Row (X); begin if not RR.Ok then return 255; end if;` |
| G13d | `Completion_Decide` | `HR` | `HR : constant Evaluation_Completion_C.History_Acceptance := Evaluation_Completion_C.Accept_History_Row (X); begin if not HR.Ok then return 255; end if;` |
| G13e | `Completion_Decide` | `QR` | `QR : constant Evaluation_Completion_C.Required_Acceptance := Evaluation_Completion_C.Accept_Required_Row (X); begin if not QR.Ok then return 255; end if;` |
| G14a | `Completion_Raw_Decide` | `JA` | as G13a |
| G14b | `Completion_Raw_Decide` | `KA` | `KA : constant Evaluation_Completion_C.Raw_Check_Acceptance := Evaluation_Completion_C.Accept_Raw_Check_Row (X); begin if not KA.Ok then return 255; end if;` |
| G14c | `Completion_Raw_Decide` | `MA` | `MA : constant Evaluation_Completion_C.Raw_Measure_Acceptance := Evaluation_Completion_C.Accept_Raw_Measure (KA.Item, KA.Declared, Wire, Confined); begin if not MA.Ok then return 255; end if;` |
| G14d | `Completion_Raw_Decide` | `RR` | as G13c |
| G14e | `Completion_Raw_Decide` | `HR` | as G13d |
| G14f | `Completion_Raw_Decide` | `QR` | as G13e |
| G15 | `Completion_Metadata_Matches` | `MA` | `MA : constant Evaluation_Completion_C.Metadata_Row_Acceptance := Evaluation_Completion_C.Accept_Metadata_Row (Original, Owned); begin if not MA.Ok then Diagnostic_Transport.Value ("completion.metadata.row-rejected", I64 (I)); return 255; end if;` |
| G16a | `Completion_Transport.Context_Matches` | `FA` | `FA : constant Evaluation_Completion_C.Context_Fields_Acceptance := Evaluation_Completion_C.Accept_Context_Fields (X); begin if not FA.Ok then Diagnostic_Transport.Value ("completion.context.field-rejected", FA.Rejected_Position); return 255; end if;` |
| G16b | `Completion_Transport.Context_Matches` | `RA` | `RA : constant Evaluation_Completion_C.Context_Row_Acceptance := Evaluation_Completion_C.Accept_Context_Row (Original, Owned); begin case RA.Verdict is` |
| G16c | `Completion_Transport.Context_Matches` | `QA` | `QA : constant Evaluation_Completion_C.Required_Pair_Acceptance := Evaluation_Completion_C.Accept_Required_Pair (Original, Owned); begin if not QA.Ok then Diagnostic_Transport.Value ("completion.context.required-rejected", I64 (I)); return 255; end if;` |
| G17 | `Run_Ledger_Check` | `O` | `O : constant Resource_Run_Ledger_C_API.Check_Acceptance := Resource_Run_Ledger_C_API.Check_Decision (Data, Raw, Before, Proposed, Observed); begin if not O.Ok then return -1; end if;` |
| G18a | `Chain_Replay` | `D` | `D : constant Worldline.Chain_Authority_C_API.Row_Acceptance := Worldline.Chain_Authority_C_API.Accept_Row (Raw); begin if not D.Ok then return -1; end if;` |
| G18b | `Chain_Replay` | `RV` | `RV : constant Worldline.Chain_Authority_C_API.Replay_Acceptance := Worldline.Chain_Authority_C_API.Replay_Value (Owned, H); begin if not RV.Ok then return -1; end if;` |
| G19a | `Pending_Decide_V1` | `D` | `D : constant Evaluation_Pending_C.Row_Acceptance := Evaluation_Pending_C.Accept_Row (V); begin if not D.Ok then return 255; end if;` |
| G19b | `Pending_Decide_V1` | `O` | `O : constant Evaluation_Pending_C.Decide_Acceptance := Evaluation_Pending_C.Decide_Value (A, J, R); begin if not O.Ok then return 255; end if;` |
| G20a | `Pending_Decide_V2` | `D` | `D : constant Evaluation_Pending_V2_C.Row_Acceptance := Evaluation_Pending_V2_C.Accept_Row (V); begin if not D.Ok then return 255; end if;` |
| G20b | `Pending_Decide_V2` | `O` | `O : constant Evaluation_Pending_V2_C.Decide_Acceptance := Evaluation_Pending_V2_C.Decide_Value (A, J, R); begin if not O.Ok then return 255; end if;` |
| G21a | `Finalization_Decide` | `PA` | `PA : constant Evaluation_Finalization_C.Plan_Acceptance := Evaluation_Finalization_C.Accept_Plan (Q); begin if not PA.Ok then Diagnostic_Transport.Value ("finalization.decide.required-rejected", I64 (K)); return 255; end if;` |
| G21b | `Finalization_Decide` | `RA` | `RA : constant Evaluation_Finalization_C.Row_Acceptance := Evaluation_Finalization_C.Accept_Row (Q); begin if not RA.Ok then Diagnostic_Transport.Value ("finalization.decide.row-rejected", I64 (K)); return 255; end if;` |
| G21c | `Finalization_Decide` | `O` | `else O := Evaluation_Finalization_C.Decide_No_Rows_Value (X, A, Required); end if; if not O.Ok then return 255; end if;` (WF-X: the gate starts at the second exclusive assignment, and `O` is in `CAPI_GATE_ASSIGNED`) |

Undiscriminated SPARK results are not acceptance records and have no gate row:
- `Readiness_Result` values `Observed` and `R1`;
- `Boolean` and `U8` results;
- the `K.Check_Row` and `K.Request` results of `Final_Projected_Row` and `Final_Projection`.

Their provenance is fixed by the tiles.

---

## B11. Promise-to-check matrix (new; V3-RC4 "every promised condition has a matching enforceable check")

"Text" means a manifest check in B8. "Evidence" means an obligation that no text check can close; it is listed so that no promise is silently assumed to be enforced.

| # | Promised condition (where stated) | Matching check | Kind |
|---|---|---|---|
| 1 | Guards copied verbatim, value runs replaced in original order, short-circuit kept (§3.1 rule 1, M1) | R-TILE (guard segments exact) | Text |
| 2 | Every intervening transport operation, allocation and early return kept (M2) | R-TILE | Text |
| 3 | No prevalidation; reads only after their gating decision; per-row staging; no bulk copy; unconditional reads kept (M3, §3.3) | R-TILE; read frontiers §9.6 with C-05 | Text + behavioural |
| 4 | Only the listed pure, infallible decodes move into acceptors (M4) | R-TILE (moved text visible as absent); unit pins and full-body review for the SPARK side | Text + review |
| 5 | Value routines: `Global => null`, no `Pre`, no functional `Post` (V1, LD2) | Unit pins of the PK-xa/PK-x specifications, full-body review and the strict command | Evidence |
| 6 | Re-check of the identical predicate on the identical constant (V3) | R-TILE (same constant passed) and proof of the SPARK body | Text + evidence |
| 7 | Discriminant tested before any payload (A1, V4) | R-GATE (B10.3), plus R-TILE | Text |
| 8 | Every out formal defined on every path (V5) | Strict flow analysis on the exact candidate | Evidence |
| 9 | Existing contracts evaluated where they were (V6) | R-TILE (call sites); A-COST tallies | Text + evidence |
| 10 | Unique, fully qualified names at every call to an Appendix C routine (V7, O6 (a)) | R-INV (vi)–(vii), R-ALIAS and R-INV (v), plus R-TILE | Text |
| 11 | Capture every input before the first write; existing overlap refusals kept, none added (§3.4) | R-TILE; C-03 behavioural | Text + behavioural |
| 12 | Each export's write set, conditions and order (§3.4, §12) | R-TILE and R-W (every foreign write has exactly one row) | Text |
| 13 | Result provenance for every write form (O4/R-W revised) | R-W per form WF-C/A/F/O/B/R/P/X/H (B10) | Text |
| 14 | Finalization `O` assigned on exactly two exclusive paths (§5.1) | R-W WF-X (assignment count 2 inside segment 6) and R-TILE (segment 6 = §5.1 text) | Text |
| 15 | Completion `Response` is the `out` actual of exactly one call and is not otherwise assigned | R-W WF-R | Text |
| 16 | `Captured` never passed or read on Operations 0/1 (§5.1, RC2) | R-TILE (segment 6) | Text |
| 17 | Handler and refusal code of each export unchanged (§3.5, LD1) | R-TILE (exception segments) | Text |
| 18 | Size constants outside handlers; allocations at original positions (§3.5) | R-TILE | Text |
| 19 | Transport helpers verbatim; no cross-unit sharing (§3.6, D-08) | R-TRANS helper hashes and per-transport residue | Text |
| 20 | Transports replicate the original renamings and declare only the listed subtypes (§3.6) | R-INV (B9.2) and R-TRANS | Text |
| 21 | No package renaming beyond the inventory (O6 (b)) | R-INV (i), (ii), (v) | Text |
| 22 | Export-body use clauses exactly as listed (O6 (c), revised) | R-INV (i) | Text |
| 23 | No elaboration code or extra declarations in transports | R-TRANS (empty residue) | Text |
| 24 | Pre-existing C_API code unchanged except the recorded glue edits (§3.6 (c), D-21, O7) | R-RES, R-GLUE, R-ALIAS (O7 names) | Text |
| 25 | Placement: transports before `Authority_Glue`; exports at the end; spec additions at the end (§3.6) | R-LAYOUT | Text |
| 26 | Staying declarations and assertions unchanged (P3) | S-RES (whole spec), unit pins | Text |
| 27 | One binding per C symbol at its designed home; no alternate binding (G1–G4, G6) | `_capi_closure_problems` | Text |
| 28 | Relocated profiles identical except the identifier; C_API subtypes (P1, P2) | `_capi_profile_problems` | Text |
| 29 | No raw constructs left in moved SPARK units (G7, N-02) | `_capi_closure_problems` | Text |
| 30 | Core `Library_Interface` unchanged (§3.7) | G9, plus the existing pin on `core/worldline_core.gpr` | Text |
| 31 | Component `Library_Interface` keeps every original unit and, under D-13 (i), adds only the transport unit (K3) | K3 parse | Text |
| 32 | Component library attributes unchanged (K5) | K5 | Text |
| 33 | Component mirror equals the core files except `SPARK_Mode` (K4) | C-10 and I3 pins (carried) | Behavioural + identity |
| 34 | Component transport equals the core transport (D-13 option (i)) | K6 | Text |
| 35 | Diagnostic state and decisions in SPARK; transport only T1–T5 (RC1, LD4-R) | D1, D2, D4 (tile), D5, G8, R-TILE (B4.19, B4.24) | Text |
| 36 | Diagnostic site sequences unchanged | D3 and R-TILE | Text |
| 37 | Predecessor assertions preserved; override calls predecessor first (PP1–PP3) | Compose's single-occurrence edits, PP2 reconstruction, override chaining | Text |
| 38 | Append-only REQUIRED_PROVED, floor 251, sole boundary (AS1–AS5) | Compose's asserted invariants; the existing manifest checks | Text |
| 39 | Identity of every touched file (I1–I7) | Compose re-pin, `source-inventory.json`, review freezes, frames | Identity |
| 40 | Reachability, actuals beyond the text, native symbols, ABI, layouts, custody, proof | Full-body/caller review, matching native evidence (D-15, D-34, D-38), strict command, OB-048 | Evidence (OPEN) |

---

## B12. Mutation controls for the v4 checks (C-09 additions; static, temporary trees, no WORLDLINE run)

Each mutation runs in a temporary copy of the stage tree and must produce at least one problem. This adds to the v3 list in §8.8.

| Rule | Mutations |
|---|---|
| R-TILE | Insert a statement between an acceptance declaration and its gate. Swap two loops. Read a row before its gate. Delete an early return. Change a refusal code. Add a second write. Reorder the exclusive branches. Change one character of a guard. |
| R-TRANS | Change one character in a copied helper. Add an elaboration `begin … end` part to a transport body. Add an extra declaration to a transport specification. Move a helper to another transport. Share one helper between two transports. |
| R-INV | Add `use Evaluation_Completion_C;` to an export body. Add `use all type Request;`. Move a use clause from a transport specification into a transport body. Drop `use System.Storage_Elements;` from an export body. Add `function Present (…) return Boolean renames Worldline.Recovery_C_API.Present;` to a transport. Add a clause to the context clause or to the C_API specification. Keep residual index 22 after PK-6b. |
| R-ALIAS | Add `package S renames Worldline.Recovery_C_API;` and call `S.Present` (also refused by R-INV). Call `K.Diagnostic_Start` from `Final_Context_Matches`. Call `E.Decide` from a pending export. |
| R-W | Write `O.Value` before the gate. Add a third assignment to finalization `O`. Assign `Response` directly. Pass `Detail_Arena` to a second procedure. Store `Encode_Decision` of a value other than the `P.Admit` result. Add an unlisted `.all :=` anywhere in a designed scope, including a scope that has no rows, such as a transport body. Add a `Write_Data (` call to `Resources_Can_Reserve`. |
| R-GATE | Select `D.Item` before `if not D.Ok`. Test `D.Ok` twice. Replace the discriminant test with a `case` on another object. Add a new acceptance object with an `.Ok` test but no gate row (completeness). |
| R-RES, R-GLUE, R-LAYOUT | Edit a value decision in `Authority_Glue`. Apply GE5 but keep the old `K.Metadata_Base` call. Keep `package K renames …` at `:836` after PK-6b. Place a transport inside `Authority_Glue`. Place an export before the owner code. Reorder the spec additions. Edit any owner export. |
| K3, K5, G9 | Remove `"evaluation_pending"` from `Library_Interface` while keeping `Library_Name "evaluation_pending"`; this was v3's false pass. Add `for Interfaces use (…)`. Duplicate a unit. Reorder the list. Add `& Extra` or an `external` reference. Change `Library_Standalone`. Remove a core interface unit. |
| K6 | Change one character of the component transport relative to the core transport. |

<!-- A-BIND-V4-END -->
