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

- Every foreign-memory write in a designed scope is an occurrence of `.all :=` or of a call `Write_Data (`, on N2. Each must be matched by exactly one row of `CAPI_WRITES` (B10), and each row's target text occurs exactly once in its scope.
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

<!-- A-BIND-V4-CONTINUES -->
