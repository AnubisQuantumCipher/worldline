# C-API boundary consolidation v5: Appendix A-BIND (enforceable binding specification, delta over v4)

| | |
|---|---|
| Companion to | `DESIGN.md` in this directory (design v5). `§n` means a section of the v5 design, that is DESIGN.md v5 with the v4 and v3 slices it carries. |
| Supersedes | v4 `APPENDIX-BINDINGS.md` (sha256 `39ca995998d68b57d13c02796ee30d8826eecc07e750abf95a83f7d348f7d626`, 225451 bytes). It is read only and unchanged (re-hashed while drafting). |
| Status | DRAFT_FOR_GPT61_REVIEW. **PROPOSAL ONLY.** No manifest code, table, source or control has been written, and no check has been run on any source tree. Every obligation is OPEN. |
| Base | S5 = `W/work/claude-composition-v5-beta/source` (lineage L0), unchanged. Line citations are S5 lines. |
| Normal form | N1 and N2 exactly as v4 (carried in B0 by reference). |
| Answers | The sealed actual gpt-6.1-sol review of v4 (`…/claude-capi-boundary-design-v4/review/gpt61-v1/`): **V4-RC4-GATE** and **V4-RC4-ALIAS**, the open binding half of V3-RC4. |
| **What this appendix consists of** | A-BIND v5 is (1) the text of this file, plus (2) the v4 A-BIND line ranges listed in §V.2 as CARRIED_VERBATIM or CARRIED_WITH_LINE_REPLACEMENTS. Each range is bound by the sha256 of its exact bytes (the lines, each followed by `\n`). The replacements of §V.3 and B8.1 are applied to them. Sections marked REPLACED or NEW are stated in full in this file. No other v4 text is part of A-BIND v5. |

Nothing in this appendix is evidence. A check that passes is a necessary guard. It is never proof of reachability, of faithful actuals beyond the bound text, of native behaviour, of custody or of correctness (§8.9).

---

## V. What changed from v4, and how v4 text is carried

### V.1 Summary

- **R-GATE (B0.7, REPLACED; V4-RC4-GATE).** One branch-sensitive rule with three gate kinds: `bool`, `case` and `wfx`. A `False`-variant component may be selected only inside its rejection branch, after the test. So the original G16a diagnostic `FA.Rejected_Position` is permitted there and refused on the accepted path. A `True`-variant component may be selected only after the gate, and a case component only inside the alternative that lists it. Finalization `O` (`wfx`, G21c) is the sole assigned acceptance object, with its exact exclusive assignments, region and test fixed by `CAPI_GATE_EXCLUSIVE`. B8 (BR3, BR4, BR7), B10.3, B11 and B12 now state the same rule.
- **R-QUAL (B0.10, NEW; V4-RC4-ALIAS).** This is the exact per-call expanded-qualifier invariant. In every scope, the multiset of dotted names whose last selector is an Appendix C routine name (and, from PK-6b, a removed routine name) must equal `CAPI_QUALIFIED` exactly. Each listed text must be a full expanded name or a listed exception that denotes another entity. In addition: no such name is selected from a non-name prefix, no full expanded name is the prefix of an attribute, and no full expanded name can be captured. Every indirect, transport-qualified, `C_API`-qualified, parent-shortened or `Standard`-prefixed spelling is therefore refused without resolving it. This covers `F.P.Decide`.
- **R-INV (vii) (A-R2).** Use clauses are now restricted by exact text: the only use clauses other than `use type` are `use <unit transport>;` and `use System.Storage_Elements;`. This is path-independent.
- **R-ALIAS (B0.5, REPLACED).** It is kept as a named subset of R-QUAL. v4's claim that it completed O6 (a) is withdrawn. Its `K.` pairs of removed names are now staged at PK-6b (latent v4 defect L9).
- **Tables and staging:** B1.1, B9.4, B10.3 (REPLACED). **Promises and mutations:** B11, B12 (REPLACED).
- **Unchanged:** every exact tile, transport content, helper hash, clause tuple and residual hash (B1–B7, B9.1–B9.3, B9.5, B10.1, B10.2). In particular A1, every diagnostic site and sequence, every refusal code, the write order, the write-form rows W03–W22 and the accepted domain are unchanged.

### V.2 Disposition of every v4 A-BIND section

"v4 lines" are 1-based lines of the v4 file. The sha256 is that of the UTF-8 bytes of those lines, each followed by `\n` (observed by a read-only script).

| v4 section | v4 lines | sha256 of the v4 slice | Disposition |
|---|---|---|---|
| Header and v4 summary | 1-22 | — | REPLACED (header above, §V.1) |
| B0 heading | 24 | — | REPLACED (heading below) |
| B0.1 Isolation (R-ISO) | 26-32 | `f7807da9d024f34b0b7d7312e0ae3bed9a2a0fce228503762cc4b9e06424770f` | CARRIED_VERBATIM |
| B0.2 Exact tiles (R-TILE) | 34-43 | `2e13a79785e767c10b64c29393f1584e81c17bc755adf68e9604a36c8eb32426` | CARRIED_WITH_LINE_REPLACEMENTS (A-R1, v4:42) |
| B0.3 Transport packages (R-TRANS) | 45-58 | `b340c1ae93ff419556fc1afcb99b24fa54255bb7fbd12430a73acaf633182a2e` | CARRIED_VERBATIM |
| B0.4 Clause inventory (R-INV) | 60-77 | `8ccc7cfef1e5c2e03a372d9c2196e2ef7b9c50f729466261e53495e0106f54c8` | CARRIED_WITH_LINE_REPLACEMENTS (A-R2, v4:73) |
| B0.5 Alias exclusion (R-ALIAS) | 79-85 | — | REPLACED |
| B0.6 Write forms (R-W) | 87-102 | `c9adc17d27b04d363890cb26d8a80c90983d058a10e7f967dd240befdf833a82` | CARRIED_VERBATIM |
| B0.7 Gates (R-GATE) | 104-114 | — | REPLACED |
| B0.8 Residual identity, layout, glue (R-RES, S-RES, R-LAYOUT, R-GLUE) | 116-129 | `729ba9ffaf86e3e50273d5f4515cd32df1f970f8062a2be1b4d9d3fee8f4b89c` | CARRIED_VERBATIM |
| B0.9 Carried rules and notes | 131-148 | `af6c7eb4db7f5f65e070474e66d1bb73f10b6e752ae4714849785bbc34c48336` | CARRIED_VERBATIM |
| (none) | — | — | NEW: B0.10 Fully expanded names (R-QUAL) |
| B1 Stage table | 152-175 | `64e4a008d2d26e8d58c1f0cad0bdd409c88bff718d2204a2ca64e64593d64ddb` | CARRIED_VERBATIM |
| B1.1 v4 additions to the stage table | 177-187 | — | REPLACED |
| B2 Home tables, B3 Relocated declarations, B4 Per-unit binding (all tiles, transport contents and glue edits), B5 Predecessor edits, B6 Diagnostic site sequences, B7 Identity binding | 191-906 | `4546e0f704f26efd2785f11ab6ce15ee103b4114732c5d8661254a27fbdcdc89` | CARRIED_VERBATIM |
| B8 heading and status | 910-916 | — | REPLACED (B8.0) |
| B8 code block (from `` ```python `` to `` ``` ``) | 918-1433 | `0c0c8ea8f5c1ed165b9a489be52bdd42e1616f145dad73319423349ac4ae8be1` | CARRIED_WITH_LINE_REPLACEMENTS (BR1–BR8, B8.1) |
| B8 check-to-rule map and notes | 1435-1458 | — | REPLACED (B8.2, B8.3) |
| B9 heading, B9.1 residual clauses, B9.2 designed clause tuples, B9.3 helper hashes | 1462-1696 | `98ad4e27ecf7c65a248b58fe2c05054c3356c540f685d4f50732f070801de413` | CARRIED_VERBATIM |
| B9.4 SPARK units and alias exclusion | 1698-1717 | — | REPLACED |
| B9.5 Core `Library_Interface` | 1719-1723 | `be0acc455dacec175b055b2f7b3888566e5aaa5ffcd300f971debffd5ed269bf` | CARRIED_VERBATIM |
| B10 heading, B10.1 Forms, B10.2 Rows | 1727-1775 | `c9d6773ab61790f4b6f8cd858e32b5cc25d30c2d4295dba2a92e8e658c27859a` | CARRIED_VERBATIM |
| B10.3 Gates | 1777-1822 | — | REPLACED |
| B11 Promise-to-check matrix | 1826-1871 | — | REPLACED |
| B12 Mutation controls and the v4 end marker | 1875-1891 | — | REPLACED |

### V.3 Line replacements in carried slices outside B8

Each item gives the v4 line, the exact v4 text and the v5 text that replaces it. Nothing else in the slice changes.

**A-R1 (v4:42, B0.2; R-QUAL joins the invariants).**
```text
v4: - **Consequence.** In these units the text fixes every declaration, read, guard, gate, decision call, write, return and handler, and their order and adjacency. The rule checks of B0.4–B0.7 are kept as **invariants**. They hold for the B4 text, and they are re-run on every successor so that a later reviewed amendment of B4 cannot weaken a rule while staying textually self-consistent.
v5: - **Consequence.** In these units the text fixes every declaration, read, guard, gate, decision call, write, return and handler, and their order and adjacency. The rule checks of B0.4–B0.7 and B0.10 are kept as **invariants**. They hold for the B4 text, and they are re-run on every successor so that a later reviewed amendment of B4 cannot weaken a rule while staying textually self-consistent.
```

**A-R2 (v4:73, B0.4 (vii); V4-RC4-ALIAS: path-independent).**
```text
v4:   - (vii) No `use` clause (other than `use type`) names a unit of `CAPI_SPARK_UNITS` (B9.4) or a package renaming of one. A `use type` naming a type of such a unit occurs only where B9.2 lists it.
v5:   - (vii) Every use clause other than a `use type` clause is exactly `use <T>;` for a unit transport `T` (a key of `CAPI_TRANSPORTS`) or `use System.Storage_Elements;` (`CAPI_USE_PACKAGES`), compared as whole N1 text, case-insensitively. This does not depend on what a name resolves to: a use clause naming a SPARK unit, a renaming of one or any path to one (`use F.P;`, `use Completion_Transport.P;`, `use Recovery_C_API;`, `use Standard.Evaluation_Pending;`) is refused. B9.1 and B9.2 contain no other use clause (author check). A `use type` naming a type of such a unit occurs only where B9.2 lists it (R-INV (i)).
```

### V.4 Reading rules for carried A-BIND text

- **AR1.** References to B0.5, B0.7, B1.1, B8, B9.4, B10.3, B11 and B12 resolve to the v5 sections of this file, and "R-INV (vii)" to A-R2.
- **AR2.** "JACKAL Jnn" in carried text means call Jnn of the v5 `jackal.json`. v5 re-ran J01–J58 with the v4 inputs and obtained the same values.
- **AR3.** Statements in carried text of the form "v4 does X" describe the binding as carried into v5. They are unchanged unless this file replaces them.
- **AR4.** "The rule checks of B0.4–B0.7" in carried text other than B0.2 includes B0.10.

---

## B0. Rules shared by every table (REVISED in v5)

**B0.1 Isolation (R-ISO).** Carried verbatim: v4 lines 26-32.

**B0.2 Exact tiles (R-TILE).** Carried: v4 lines 34-43, with A-R1.

**B0.3 Transport packages (R-TRANS).** Carried verbatim: v4 lines 45-58.

**B0.4 Clause inventory (R-INV).** Carried: v4 lines 60-77, with A-R2 for (vii).

### B0.5 Alias exclusion (R-ALIAS; REPLACED in v5: a named subset of R-QUAL, staged)

- `CAPI_ALIAS_FORBIDDEN` (B9.4) lists `(X, N)` pairs.
  - `X` is a single identifier that names a package renaming occurring in a designed or residual scope, whose target is, directly or through the renamings it is defined by, a unit owning Appendix C routines.
  - `N` is the simple name of such a routine, or, from PK-6b, of a routine that PK-6b removes from `Evaluation_Completion_C`.
- For every pair, the case-insensitive N2 pattern `(?<![\w.])X\s*\.\s*N(?!\w)` occurs zero times in the C_API body. This is unchanged from v4.
- **Staging (v5; latent v4 defect L9).** At PK-1 the table holds the 41 pairs of Appendix C names (JACKAL J60). The nine `K.` pairs of removed names are appended at PK-6b, in the packet that applies GE1–GE8, giving 50 pairs (J61).
  - v4 defined all pairs at PK-1. But the unchanged S5 residual contains `K.Raw_Decide` (`core/worldline-c_api.adb:784-785`, `:791-792`), `K.Context_Matches` (`:810-811`, `:813-814`), `K.Metadata_Base` (`:852`, `:855`) and `K.Metadata_Matches` (`:866-867`, `:869-870`) until GE1–GE8 retarget them. v4's table would therefore have refused every faithful PK-1…PK-5 successor.
  - An author simulation (B8.0) of v4's table on the assembled PK-1 text reported exactly those four selections. The v5 PK-1 table reports none.
  - This corrects a false refusal of unchanged residual text. No refusal of designed text is removed, and from PK-6b the table equals v4's.
- **What R-ALIAS does not establish (v4 claim withdrawn).** v4 said that, with R-INV (v)–(vii), "the only way left to denote an Appendix C routine in the C_API body is its full expanded name". That does not follow from these patterns. The list holds single identifiers, and the lookbehind excludes a match preceded by a dot. So the following are outside its patterns:
  - indirect paths through renamings declared in SPARK unit specifications: `F.P.Decide`, where `Evaluation_Finalization.P` renames `T.P` and `Evaluation_Completion.P` renames `Evaluation_Pending` (S5 `core/evaluation_finalization.ads:12-13`, `core/evaluation_completion.ads:10`);
  - transport-qualified paths: `Pending_Transport.E.Decide`, `Worldline.C_API.Finalization_Transport.K.Decide_Value`;
  - parent-visibility shortenings: `Recovery_C_API.Present`.

  The fully expanded naming invariant is R-QUAL (B0.10). R-ALIAS keeps its v4 patterns, so no v4 check is withdrawn. Every selection it refuses is also refused by R-QUAL (a): no `X.N` whose qualifier `X` is one of these renaming identifiers is a full expanded name or a listed exception.

**B0.6 Write forms (R-W).** Carried verbatim: v4 lines 87-102. Its statement that a closed identifier is never assigned "except where the row lists its assignments explicitly (form WF-X)" is the same exception that B0.7 states for gates.

### B0.7 Gates (R-GATE; REPLACED in v5: branch-sensitive, one rule)

**Terms.** Each row of `CAPI_GATES` (B10.3) gives an object `N`, a kind (`bool`, `case` or `wfx`), an exact N1 gate text, and the components allowed in each branch. On the N2 view of the row's scope:
- the *discriminant selection* is `N.Ok` (kinds `bool` and `wfx`) or `N.Verdict` (kind `case`);
- a *component selection* is any other `N.<c>`;
- an *assignment* is `N :=`;
- a *declaration* is `N :` not followed by `=`.

**Rules for every kind.**
1. The gate text has its kind's exact form (`CAPI_GATE_FORMS`, below) and occurs exactly once in the scope.
2. `N` is declared exactly once in the scope, and its discriminant is selected exactly once in the scope, inside the gate text.
3. Every occurrence of the identifier `N` in the scope is one of the following: its declaration; its one discriminant selection; a listed component selection at a place where the row allows that component; or (kind `wfx` only) one of its two exclusive assignments. Any other use is a problem, including passing `N` whole, renaming it, assigning it or taking an attribute of it.

**Kind `bool`** (31 rows: G06–G15, G16a, G16c, G17–G21b).
- Form: `N : constant <T> := <call>; begin if not N.Ok then <D> return <code>; end if;`. Here `<D>` is zero or more statements, each `Diagnostic_Transport.Mark ("…");` or `Diagnostic_Transport.Value ("…", <expression>);`. The *rejection branch* is `<D>`: it lies after the test and before the `return` that ends the branch.
- A component of the `False` variant (the row's **F** list) may be selected only inside `<D>`. This permits G16a's original rejection diagnostic `Diagnostic_Transport.Value ("completion.context.field-rejected", FA.Rejected_Position);` after its test, and refuses `FA.Rejected_Position` anywhere on the accepted path.
- A component of the `True` variant (the row's **T** list) may be selected only after the end of the gate text. The branch's final `return` makes that text reachable only when `N.Ok` is True.

**Kind `case`** (G16b).
- Form: `N : constant <T> := <call>; begin case N.Verdict is`.
- The *case region* runs from the end of the gate text to the first `end case;` after it. It contains:
  - exactly the listed alternative heads (`when <choice> =>`), each once, the first one immediately after the gate text;
  - no other `when`;
  - no nested `case`.
- Each alternative runs from its head to the next head, or to `end case;`.
- A component may be selected only inside an alternative that lists it:
  - `RA.Rejected_Field_Position` only in `Row_Field_Rejected`;
  - `RA.Row` and `RA.Joined` only in `Row_Accepted`;
  - nothing in `Row_Rejected`;
  - nothing after `end case;`.

**Kind `wfx`** (G21c only; finalization `O`, the sole assigned acceptance object).
- `CAPI_GATE_EXCLUSIVE` gives four exact texts:
  - the declaration `O : Evaluation_Finalization_C.Decide_Acceptance;`, with no initializer;
  - the exclusive region: B4.20 segment 6 without its final test, that is, the `if Evaluation_Finalization_C.Needs_Rows (X) then … end if;` statement of §5.1;
  - the then-assignment `O := Evaluation_Finalization_C.Decide_Rows_Value (X, A, Required, Captured);`;
  - the else-assignment `O := Evaluation_Finalization_C.Decide_No_Rows_Value (X, A, Required);`.
- Form of the gate text: `<then-assignment> else <else-assignment> end if; if not O.Ok then return <code>; end if;`.
- Requirements:
  - The declaration and the region each occur once, the declaration first.
  - The region is one if statement with no `elsif` and no conditional expression. The then-assignment is the last statement of its then branch, and the else-assignment is its whole else branch. This is checked by `if` nesting depth on N2 (`_capi_exclusive`), with `or else` skipped.
  - The gate text begins at the then-assignment, and its test immediately follows the region's own `end if;`.
  - `O` is assigned exactly twice in the scope, at exactly those two places. So on every path through the region exactly one assignment completes before the test, and no other assignment exists.
  - By rule 3, `O` is not used in any other way before the test. Its only `True` component, `O.Value`, is selected only after the gate. The `False` variant of `Decide_Acceptance` is null.
- This is the only exception to "an acceptance object is never assigned". R-W row W21 binds the same two assignments by its count (B10.2), and R-TILE fixes the text (segment 6).

**`CAPI_GATE_FORMS`** (B8, BR4), on N2:
- `bool`: `(\w+) : constant [\w.]+ := [^;]+; begin if not \1\.Ok then ((?:Diagnostic_Transport\.(?:Mark \("_*"\)|Value \("_*", [^;]+\)); )*)return -?\d+; end if;`
- `case`: `(\w+) : constant [\w.]+ := [^;]+; begin case \1\.Verdict is`
- `wfx`: `(\w+) := [^;]+; else \1 := [^;]+; end if; if not \1\.Ok then return -?\d+; end if;`

In every form, group 1 must equal the row's object.

**Completeness.** In every designed scope (each occurrence attributed to its innermost scope), each of the following must belong to an object with a gate row in that scope:
- every `X.Ok` and every `X.Verdict` selection;
- every object declared with a subtype mark whose last identifier ends in `_Acceptance`.

RESIDUAL is bound by R-RES instead. So an acceptance object cannot be added without its gate, even if it is never tested.

**What this replaces (V4-RC4-GATE).**
- v4's B0.7 required every component selection to begin after the end of the gate string, and it forbade every assignment. That refused the original G16a diagnostic and finalization's exclusive assignments.
- v4's B8 instead checked "after the discriminant test" and exempted G21c by a list.
- Neither statement was branch-correct. v4's B8 rule would also have accepted a `False`-variant selection on the accepted path (for example `FA.Rejected_Position` after `end if;`), `RA.Row` in the `Row_Rejected` alternative, and a selection after `end case;` (latent v4 defect L10). The last two also satisfied v4's B0.7.
- Both v4 statements are withdrawn. The v5 rule is stated once, here. It is implemented by `_capi_gate_problems` with `_capi_gate_row_problems` and `_capi_exclusive` (B8), tabulated in B10.3, promised in B11 rows 7, 14 and 41, and exercised by the R-GATE and WF-X mutations of B12.

**B0.8 Residual identity, layout and glue edits (R-RES, S-RES, R-LAYOUT, R-GLUE).** Carried verbatim: v4 lines 116-129.

**B0.9 Carried rules and remaining notes.** Carried verbatim: v4 lines 131-148.

### B0.10 Fully expanded names (R-QUAL; NEW in v5; V7, O6 (a); the exact per-call expanded-qualifier invariant)

**Tables** (B9.4):
- `CAPI_ROUTINE_NAMES`: the 98 Appendix C full names, complete from PK-1.
- `CAPI_REMOVED_NAMES`: the nine `Evaluation_Completion_C` routines that PK-6b removes; empty before PK-6b.
- `CAPI_SPARK_UNITS`: the 17 units that own them.
- `CAPI_QUALIFIED`: for each scope, the exact multiset of qualified routine names.
- `CAPI_QUALIFIER_EXCEPTIONS`: each text that is not a full expanded name, with the scopes where it may occur. B9.4 says what each one denotes.

**Terms.**
- The *listed simple names* are the last selectors of both name tables: 85 at PK-1 (observed by script), and 93 from PK-6b (J59; `Decide` is in both tables).
- A *full expanded name* is an entry of `CAPI_ROUTINE_NAMES`, compared case-insensitively. A removed name is never a full expanded name.
- A *dotted name* is, on N2, a maximal run `I0 . I1 . … . Ik` (k ≥ 1) of identifiers joined by dots, with optional spaces, not preceded by an identifier character, a dot or an apostrophe.
- A *qualified routine name* is any prefix `I0.….Ij` (j ≥ 1) of a dotted name whose last selector `Ij` is a listed simple name. Its text is those identifiers joined by single dots.

**Requirements.** They apply to the whole C_API specification and the whole C_API body, context clause included.
- **(a) Exact per-scope expanded qualifiers.** Scopes are: each designed scope (by innermost attribution), RESIDUAL, and SPEC (the specification). For each scope, the case-insensitive multiset of qualified routine names equals `CAPI_QUALIFIED[scope]` exactly; a scope without an entry must contain none. Every listed text is either a full expanded name, or an entry of `CAPI_QUALIFIER_EXCEPTIONS` listed for that scope.
- **(b) No selection from a non-name prefix.** No listed simple name is selected from a prefix that is not a pure dotted name, for example `Request_Pointers.To_Pointer (Input).all.Header_Valid` or `F (X).Decide`.
- **(c) No attribute of a routine.** No full expanded name is the prefix of an attribute reference such as `'Access` or `'Address`.
- **(d) No capture of a full expanded name.** The nine first identifiers of the full expanded names are `Worldline`, `Resource_Run_Ledger_C_API`, `Evaluation_Completion_C`, `Evaluation_Completion_Roster`, `Evaluation_Finalization_C`, `Evaluation_Pending_C`, `Evaluation_Pending`, `Evaluation_Pending_V2_C` and `Evaluation_Pending_V2` (B9.4). The context clause is the text before the first `package`.
  - Outside the context clause, these identifiers occur only in two ways: as the first identifier of a dotted name, or as the target of a package renaming (`renames <root>;`).
  - In the context clause, no `with` clause names a dotted unit whose last identifier is one of them. Such a unit, for example a child `Worldline.Evaluation_Pending`, would be directly visible by that identifier inside `Worldline.C_API` and would hide the library unit.
  - So no declaration in the C_API pair, and no unit the pair names in a `with` clause, can make a full expanded name denote anything other than its library unit's routine. The declarations excluded include an object, parameter, package, subprogram, type, loop parameter, enumeration literal or renaming of that name.

**Why this closes O6 (a) at text level.** Let `R` be an Appendix C routine or, from PK-6b, a removed routine. In the C_API pair, `R` can only be denoted in these ways:
1. **By a dotted name ending in its simple name.**
   - By (a), the text is either `R`'s full expanded name or a listed exception. B9.4 records what each exception denotes, none of which is `R`.
   - By (d), the full expanded name denotes `R`'s library unit.
   - None of the following has the text of a full expanded name, and none is an exception, so (a) refuses each of them without resolving the path:
     - renamings declared in SPARK unit specifications (`F.P.Decide`);
     - transport-qualified paths (`Pending_Transport.E.Decide`);
     - paths through `C_API` or `Worldline.C_API`;
     - parent-visibility shortenings (`Recovery_C_API.Present`);
     - `Standard.` prefixes;
     - library units reached through renamings (`Evaluation_Completion.P.Decide`).
2. **By a selection from a non-name prefix.** Refused by (b).
3. **By its simple name alone, through use-visibility.**
   - R-INV (vii) admits no use clause except `use <unit transport>;` and `use System.Storage_Elements;`.
   - The unit transports declare no subprogram renaming (R-INV (v)). They contain only S5-verbatim helpers (R-TRANS hashes) and tiled subprograms.
   - A use clause makes potentially use-visible only declarations of the named package itself, not what that package makes visible by its own use clauses (RM 8.4; the author's reading, since no RM text is installed locally).
   - `use type` makes only primitive operators visible, and none of the 98 names is an operator symbol (author scan).
4. **By its simple name alone, through a declaration in the C_API pair** (a renaming or instance). Refused by R-INV (v), R-TRANS and R-TILE.
5. **Through an attribute of a full expanded name** (for example `'Access`). Refused by (c).

So every remaining denotation of an Appendix C routine is its full expanded name.
- This is a static, text-level argument. Installed-compiler name resolution in the integrated body remains OPEN (D-38).
- R-QUAL never resolves names. It compares texts.

**Indirect-path inventory.** B9.4 lists every path that reaches an Appendix C unit, starting from any package renaming visible in a designed or residual scope and following package renamings in the visible parts of the S5 specifications.
- The list was observed by a read-only script. The renaming graph is acyclic, and its longest chain has 5 renamings.
- There are 80 paths (J65): 9 single identifiers (J67), which R-ALIAS also lists, and 71 with two or more identifiers (J66).
- (a) refuses all of them and needs no such list. The list is documentation and the source of the B12 indirect-path mutations.

---

## B1.1 Stage additions of the B8 tables (REPLACED in v5)

The tables of B8 follow the v4 stage discipline: each stage only appends `.update({...})` lines or extends a tuple by reassignment that keeps the earlier prefix.

| Stage | Table content appended |
|---|---|
| PK-1 | **As v4:** `CAPI_TILES`, `CAPI_TRANSPORTS`, `CAPI_INVENTORY`, `CAPI_WRITES`, `CAPI_GATES` (entries for B4.1 and B4.2: U1 and U2 have no writes and no acceptance objects), `CAPI_SPARK_UNITS` (complete), `CAPI_RESIDUAL_SHA256`, `CAPI_SPEC_RESIDUAL_SHA256`, `CAPI_RESIDUAL_CLAUSES` (B9.1), `CAPI_LAYOUT_PACKAGES`, `CAPI_LAYOUT_EXPORTS` (stage-1 prefix), `CAPI_CORE_INTERFACE` (G9), `CAPI_COMPONENT_INTERFACE` (L0, K3), `CAPI_COMPONENT_LIBRARY` (K5) and an empty `CAPI_GLUE_EDITS`.<br>**Changed:** `CAPI_ALIAS_FORBIDDEN` holds only the 41 pairs of Appendix C names (J60).<br>**New in v5:** `CAPI_USE_PACKAGES`; `CAPI_ROUTINE_NAMES` (complete, 98 names); an empty `CAPI_REMOVED_NAMES`; an empty `CAPI_GATE_EXCLUSIVE`; `CAPI_QUALIFIER_EXCEPTIONS` with the seven RESIDUAL entries; and `CAPI_QUALIFIED` with the RESIDUAL entry at L0 (seven texts, one occurrence each) and the U1 and U2 scopes (B9.4). |
| PK-2 … PK-5, PK-7 | Entries of the stage's units in `CAPI_TILES`, `CAPI_TRANSPORTS`, `CAPI_INVENTORY`, `CAPI_WRITES`, `CAPI_GATES` and `CAPI_QUALIFIED`; the next slices of `CAPI_LAYOUT_PACKAGES` and `CAPI_LAYOUT_EXPORTS` |
| PK-6b | The same for B4.14–B4.22 and B4.24. In addition:<br>- `CAPI_GLUE_EDITS` GE1–GE9 and R-DEL-1 (as v4);<br>- `CAPI_GATE_EXCLUSIVE` G21c;<br>- `CAPI_REMOVED_NAMES` (nine names);<br>- the nine `K.` pairs of removed names, appended to `CAPI_ALIAS_FORBIDDEN` (50 pairs, J61);<br>- the two `Completion_Transport` entries, added to `CAPI_QUALIFIER_EXCEPTIONS` (nine entries, J63);<br>- `CAPI_QUALIFIED['RESIDUAL']` takes its PK-6b value: the seven L0 texts plus the four calls that GE3–GE6 create (eleven occurrences, J64). This uses the same `.update` mechanism by which a later stage moves a symbol's home in `CAPI_CORE_HOME`. |
| PK-7 | Under D-13 option (i) only, as v4: `CAPI_COMPONENT_INTERFACE` gains `'evaluation_pending_transport'`, and `CAPI_COMPONENT_MIRROR` (K6) is defined |
| PK-xR, PK-6a, PK-S | none |

Before PK-6b the residual calls `K.Raw_Decide`, `K.Context_Matches`, `K.Metadata_Base` and `K.Metadata_Matches` are not R-QUAL occurrences. Their selectors are not Appendix C simple names, and the removed names join the listed simple names only when PK-6b sets `CAPI_REMOVED_NAMES`, in the same packet as GE1–GE8.

---

## B8. The `export_problems` override (PK-1 tail; PROPOSAL sketch, REVISED in v5)

### B8.0 Status of the sketch (REPLACED in v5)

- **Composition.** The v5 code is the v4 code block (v4 A-BIND lines 918-1433, sha256 `0c0c8ea8f5c1ed165b9a489be52bdd42e1616f145dad73319423349ac4ae8be1`) with replacements BR1–BR8 (B8.1) applied. Each replacement names its v4 lines and quotes them verbatim. The reconstructed v5 code block is given by sha256 in AUTHOR-NOTES.md, which also lists how it was checked.
- **Unchanged parts.** Every function and table line that BR1–BR8 do not name is byte-identical to v4. This includes all helpers and the closure, project, component, profile, tile, transport, write, residual and diagnostic checks.
- **Not reviewed or run on a tree.** The text is not reviewed. After its last edit the author reconstructed it with a read-only script and parsed it with Python's `ast` module. That is a syntax check only.
- **Author simulation** (a self-check, not a review and not evidence).
  - The same script executed the reconstructed definitions in an isolated in-memory namespace. `normalized_ada` was reimplemented, and the predecessor `export_problems` was replaced by a stub returning no problem.
  - It ran on two in-memory successor texts assembled from S5, the B4 tiles and transport contents, the B9.3 helpers and the B3 declarations: the final PK-7 text, and the PK-1 text.
  - No WORLDLINE module was imported, no file was written, and no tree was built.
  - R-GATE, R-QUAL and R-INV reported no problem on either text.
  - Every mutation that B12 marks *(sim)* produced at least one problem from the check named for it.
  - This shows only that the sketch, the tables and the author's assembled text agree. It is not a run of the manifest, and it grants nothing.
- **Imports.** It imports nothing beyond the manifest's imports (`hashlib`, `json`, `Path`, `re`, `typing`).
- **Placement.** As in v4, it is appended after the last S5 line (`:1029`). Later stages only append `.update(...)` lines to the tables.
- **One check function per rule.** Every rule of B0 has its own check function (B8.2).

### B8.1 Code replacements BR1–BR8

Each replacement quotes the v4 lines it removes, exactly, followed by the v5 lines. An insertion names the v4 line it follows, and that v4 line is unchanged. Each inserted block is preceded by two empty lines. Replacements are applied by v4 line number.

**BR1 (v4 lines 919-921, replaced): header comment.**
```text
# C-API raw-pointer boundary consolidation (design v4, stage PK-1). Whole-closure binding, exact
# tiles, transport residues, scoped clause inventory, alias exclusion, write forms, gates,
# residual identity and component interface membership. Every predecessor check runs first.
```
```python
# C-API raw-pointer boundary consolidation (design v5, stage PK-1). Whole-closure binding, exact
# tiles, transport residues, scoped clause inventory, alias exclusion, fully expanded names, write
# forms, branch-sensitive gates, residual identity and component interface membership. Every
# predecessor check runs first.
```

**BR2 (v4 lines 937-938, replaced): R-ALIAS and R-QUAL tables.**
```text
CAPI_ALIAS_FORBIDDEN = (...)      # B9.4: (alias, routine) pairs
CAPI_SPARK_UNITS = (...)          # B9.4: the units that own Appendix C names (17, observed by script) (R-INV vii)
```
```python
CAPI_ALIAS_FORBIDDEN = (...)      # B9.4: (alias, routine) pairs; PK-6b appends the K. pairs of removed names
CAPI_SPARK_UNITS = (...)          # B9.4: the units that own Appendix C names (17, observed by script) (R-QUAL)
CAPI_USE_PACKAGES = ('System.Storage_Elements',)  # R-INV (vii): with the unit transports, all a use clause may name
CAPI_ROUTINE_NAMES = (...)        # B9.4: the 98 Appendix C full names, in Appendix C order (R-QUAL)
CAPI_REMOVED_NAMES = ()           # B9.4: the 9 removed Evaluation_Completion_C full names, set at PK-6b (R-QUAL)
CAPI_QUALIFIED = {...}            # B9.4: scope key, 'RESIDUAL' or 'SPEC' -> ((dotted text, count), ...) (R-QUAL)
CAPI_QUALIFIER_EXCEPTIONS = {...} # B9.4: non-canonical dotted text -> (scope key, ...) where it may occur (R-QUAL)
```

**BR3 (v4 lines 940-941, replaced): gate tables.**
```text
CAPI_GATES = {...}                # scope key -> ((id, object, gate text), ...); B10.3
CAPI_GATE_ASSIGNED = ('G21c',)    # the one gated object that is assigned (its assignments are bound by W21)
```
```python
CAPI_GATES = {...}                # scope key -> ((id, kind, object, gate text, variants), ...); B10.3
CAPI_GATE_EXCLUSIVE = {}          # B10.3: 'G21c' -> (declaration, region, then assignment, else assignment), PK-6b
```

**BR4 (inserted after v4 line 963, `CAPI_BODY_HEAD = 'package body Worldline.C_API with SPARK_Mode => Off is'`, which is unchanged): gate forms and dotted names.** This insertion has no empty lines before it; it continues the table block.
```python
CAPI_GATE_FORMS = {               # B0.7: the exact form of each kind of gate text, on N2
    'bool': re.compile(r'(\w+) : constant [\w.]+ := [^;]+; begin if not \1\.Ok then ((?:Diagnostic_Transport\.'
                       r'(?:Mark \("_*"\)|Value \("_*", [^;]+\)); )*)return -?\d+; end if;'),
    'case': re.compile(r'(\w+) : constant [\w.]+ := [^;]+; begin case \1\.Verdict is'),
    'wfx': re.compile(r'(\w+) := [^;]+; else \1 := [^;]+; end if; if not \1\.Ok then return -?\d+; end if;')}
CAPI_DOTTED = re.compile(r"(?<![\w.'])[A-Za-z]\w*(?:\s*\.\s*[A-Za-z]\w*)+")   # B0.10: a maximal dotted name
```

**BR5 (v4 lines 1241-1247, replaced): R-INV (vii) in `_capi_clause_problems`.**
```text
    spark = {name.lower() for name in CAPI_SPARK_UNITS} | {alias.lower() for alias, _ in CAPI_ALIAS_FORBIDDEN}
    for key, clauses in found.items():                                                     # R-INV (vii)
        for clause in clauses:
            words = clause.rstrip(';').split()
            if (words[0].lower() == 'use' and words[1].lower() not in ('type', 'all')
                    and any(name.strip().lower() in spark for name in ' '.join(words[1:]).split(','))):
                problems.append(f'{key}: a use clause names a SPARK unit or a renaming of one')
```
```python
    allowed = {f'use {name};'.lower() for name in (*CAPI_TRANSPORTS, *CAPI_USE_PACKAGES)}
    for key, clauses in found.items():                                                     # R-INV (vii)
        for clause in clauses:
            words = clause.split()
            if words[0].lower() == 'use' and words[1].lower() not in ('type', 'all') and clause.lower() not in allowed:
                problems.append(f'{key}: a use clause names a package other than a unit transport '
                                'or System.Storage_Elements')
```

**BR6 (inserted after v4 line 1263, the last line of `_capi_alias_problems`, which is unchanged): R-QUAL.**
```python
def _capi_qualified(code: str, simple: set):
    """R-QUAL on N2: (text, start, end) of every dotted-name prefix whose last selector is a listed simple
    name, and the positions of listed simple names selected from a prefix that is not a name."""
    found, covered = [], set()
    for match in CAPI_DOTTED.finditer(code):
        words = list(re.finditer(r'[A-Za-z]\w*', match.group()))
        for index in range(1, len(words)):
            if words[index].group().lower() in simple:
                found.append(('.'.join(word.group() for word in words[:index + 1]),
                              match.start() + words[index].start(), match.start() + words[index].end()))
                covered.add(match.start() + words[index].start())
    loose = [match.start(1) for match in re.finditer(r'\.\s*([A-Za-z]\w*)(?!\w)', code)
             if match.group(1).lower() in simple and match.start(1) not in covered]
    return found, loose


def _capi_qualifier_problems(root: Path) -> list[str]:                                     # R-QUAL (V7, O6 a)
    canonical = {name.lower() for name in CAPI_ROUTINE_NAMES}
    simple = {name.rsplit('.', 1)[1].lower() for name in (*CAPI_ROUTINE_NAMES, *CAPI_REMOVED_NAMES)}
    roots = {name.split('.', 1)[0].lower() for name in CAPI_ROUTINE_NAMES}
    problems = [f'{name}: not a routine of a listed SPARK unit' for name in CAPI_ROUTINE_NAMES
                if name.rsplit('.', 1)[0] not in CAPI_SPARK_UNITS]
    for key, listed in CAPI_QUALIFIED.items():                       # each listed text is canonical or excepted
        for text, _ in listed:
            if text.lower() not in canonical and key not in CAPI_QUALIFIER_EXCEPTIONS.get(text, ()):
                problems.append(f'{key}: {text} is neither a full expanded name nor a listed exception')
    body = _capi_text(root, 'core/worldline-c_api.adb')
    scopes, seen = _capi_scopes(body), {}
    for label, text in (('SPEC', _capi_text(root, 'core/worldline-c_api.ads')), ('BODY', body)):
        code = _capi_code(text)
        found, loose = _capi_qualified(code, simple)
        problems += [f'{label}: a routine name is selected from a prefix that is not a name' for _ in loose]
        for name, low, high in found:
            key = 'SPEC' if label == 'SPEC' else _capi_owner(scopes, low)
            counts = seen.setdefault(key, {})
            counts[name.lower()] = counts.get(name.lower(), 0) + 1
            if name.lower() in canonical and code[high:].lstrip().startswith("'"):
                problems.append(f'{key}: {name} is the prefix of an attribute')
        context = code.find('package ')                              # the context clause precedes it
        for match in re.finditer(r'\bwith\s+([\w.,\s]+?)\s*;', code[:context]):
            for unit in match.group(1).split(','):
                words = ''.join(unit.split()).lower().split('.')
                if len(words) > 1 and words[-1] in roots:
                    problems.append(f'{label}: the with clause unit {unit.strip()} can capture a full expanded name')
        for match in re.finditer(r"(?<![\w.'])[A-Za-z]\w*(?!\w)", code):
            if (match.group().lower() in roots and match.start() > context
                    and not re.match(r'\s*\.', code[match.end():])
                    and not (code.endswith('renames ', 0, match.start()) and code.startswith(';', match.end()))):
                problems.append(f'{label}: {match.group()}, the first name of a full expanded name, '
                                'is declared or used alone')
    for key in sorted(set(seen) | set(CAPI_QUALIFIED)):
        expected = {}
        for text, count in CAPI_QUALIFIED.get(key, ()):
            expected[text.lower()] = expected.get(text.lower(), 0) + count
        if seen.get(key, {}) != expected:
            problems.append(f'{key}: qualified routine names differ from the exact per-scope table')
    return problems
```

**BR7 (v4 lines 1303-1335, replaced): R-GATE.**
```text
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
```
```python
def _capi_exclusive(region: str, then_text: str, else_text: str) -> bool:
    """WF-X (B0.7): region is one if statement with no elsif and no conditional expression; then_text is the
    last statement of its then branch and else_text is its whole else branch."""
    code = _capi_code(region)
    tail = f'{then_text} else {else_text} end if;'
    if not code.startswith('if ') or not region.endswith(tail) or re.search(r'\(\s*if\b', code, re.IGNORECASE):
        return False
    depth, branches = 0, []
    for match in re.finditer(r'\bend\s+if\b|\bor\s+else\b|\belsif\b|\belse\b|\bif\b', code, re.IGNORECASE):
        word = ' '.join(match.group().lower().split())
        if word == 'end if':
            depth -= 1
            if depth == 0 and match.end() + 1 != len(code):
                return False
        elif word == 'if':
            depth += 1
        elif word != 'or else' and depth == 1:
            branches.append((word, match.start()))
    return depth == 0 and branches == [('else', len(code) - len(tail) + len(then_text) + 1)]


def _capi_gate_row_problems(unit: str, row) -> list[str]:
    """R-GATE for one CAPI_GATES row inside its scope text (B0.7)."""
    row_id, kind, name, gate, variants = row
    code = _capi_code(unit)
    form = CAPI_GATE_FORMS[kind].fullmatch(_capi_code(gate))
    if form is None or form.group(1) != name:
        return [f'{row_id}: the gate text does not have the {kind} form for {name}']
    if unit.count(gate) != 1:
        return [f'{row_id}: gate missing or repeated']
    start = unit.find(gate)
    end = start + len(gate)
    problems, branches = [], dict(variants)
    if kind == 'bool':                       # where each component may be selected: (low, high, components)
        places = [(start + form.start(2), start + form.end(2), branches['False']), (end, len(unit), branches['True'])]
    elif kind == 'wfx':
        places = [(end, len(unit), branches['True'])]
    else:                                    # each case alternative runs to the next one or to `end case;`
        close = code.find('end case;', end)
        heads = sorted(code.find(head, end) for head, _ in variants)
        if (close < 0 or heads[0] != end + 1 or heads[-1] > close
                or any(code[end:close].count(head) != 1 for head, _ in variants)
                or len(re.findall(r'\bwhen\b', code[end:close])) != len(variants)
                or re.search(r'\bcase\b', code[end:close])):
            return [f'{row_id}: the alternatives of {name} are not exactly the listed ones']
        places = [(code.find(head, end), min([high for high in heads if high > code.find(head, end)] + [close]),
                   components) for head, components in variants]
    discriminant = 'verdict' if kind == 'case' else 'ok'
    tests, declarations, assignments = 0, 0, []
    for match in re.finditer(rf'(?<![\w.]){re.escape(name)}(?!\w)', code, re.IGNORECASE):
        after = code[match.end():]
        selected = re.match(r'\s*\.\s*(\w+)', after)
        if selected and selected.group(1).lower() == discriminant:
            tests += 1
            if not start <= match.start() < end:
                problems.append(f'{row_id}: the discriminant of {name} is selected outside its gate')
        elif selected:
            if not any(low <= match.start() < high and selected.group(1).lower() in {c.lower() for c in components}
                       for low, high, components in places):
                problems.append(f'{row_id}: {name}.{selected.group(1)} is selected where its variant is not established')
        elif re.match(r'\s*:(?!=)', after):
            declarations += 1
        elif kind == 'wfx' and re.match(r'\s*:=', after):
            assignments.append(match.start())
        else:
            problems.append(f'{row_id}: {name} is used other than in its declaration, test and listed selections')
    if tests != 1 or declarations != 1:
        problems.append(f'{row_id}: {name} is not declared once and tested once')
    if kind == 'wfx':
        declaration, region, then_text, else_text = CAPI_GATE_EXCLUSIVE.get(row_id, ('', '', '', ''))
        if (not re.fullmatch(rf'{re.escape(name)} : [\w.]+;', declaration)
                or unit.count(declaration) != 1 or unit.count(region) != 1
                or not unit.find(declaration) < unit.find(region)
                or not gate.startswith(f'{then_text} else {else_text} end if; ')
                or unit.find(region) + len(region) != start + len(f'{then_text} else {else_text} end if;')
                or not _capi_exclusive(region, then_text, else_text)
                or assignments != [start, start + len(f'{then_text} else ')]):
            problems.append(f'{row_id}: {name} is not assigned exactly once on each exclusive branch before its test')
    return problems


def _capi_gate_problems(root: Path) -> list[str]:                                          # R-GATE (A1, V4)
    body = _capi_text(root, 'core/worldline-c_api.adb')
    problems = []
    for key, rows in CAPI_GATES.items():
        span = _capi_scope_span(body, key)
        if span is None:
            problems.append(f'{key}: scope cannot be isolated')
            continue
        for row in rows:
            problems += _capi_gate_row_problems(body[span[0]:span[1]], row)
    scope_list = _capi_scopes(body)              # completeness: every tested or acceptance object has a row
    code = _capi_code(body)
    for pattern, what in ((r'(?<![\w.])(\w+)\s*\.\s*(?:Ok|Verdict)\b', 'has a discriminant selection'),
                          (r'(?<![\w.])(\w+)\s*:\s*(?:constant\s+)?[\w.]*_Acceptance\b', 'is an acceptance object')):
        for match in re.finditer(pattern, code, re.IGNORECASE):
            key = _capi_owner(scope_list, match.start())
            if key != 'RESIDUAL' and match.group(1).lower() not in {row[2].lower() for row in CAPI_GATES.get(key, ())}:
                problems.append(f'{key}: {match.group(1)} {what} but no gate row')
    return problems
```

**BR8 (v4 lines 1418-1421, replaced): the check list.**
```text
CAPI_CHECKS = (_capi_closure_problems, _capi_core_project_problems, _capi_component_problems,
               _capi_profile_problems, _capi_tile_problems, _capi_transport_problems,
               _capi_clause_problems, _capi_alias_problems, _capi_write_problems,
               _capi_gate_problems, _capi_residual_problems, _capi_diagnostic_problems)
```
```python
CAPI_CHECKS = (_capi_closure_problems, _capi_core_project_problems, _capi_component_problems,
               _capi_profile_problems, _capi_tile_problems, _capi_transport_problems,
               _capi_clause_problems, _capi_alias_problems, _capi_qualifier_problems,
               _capi_write_problems, _capi_gate_problems, _capi_residual_problems,
               _capi_diagnostic_problems)
```

### B8.2 Check-to-rule map (REPLACED in v5)

| Function | Rules enforced | Change from v4 |
|---|---|---|
| `_capi_closure_problems` | G1–G4, G6, G7 | unchanged |
| `_capi_core_project_problems` | G5, G9 | unchanged |
| `_capi_component_problems` | K1, K2, K3 (actual membership), K5, K6 | unchanged |
| `_capi_profile_problems` | P1, P2 | unchanged |
| `_capi_tile_problems` | R-TILE | unchanged |
| `_capi_transport_problems` | R-TRANS | unchanged |
| `_capi_clause_problems` | R-INV (i)–(vii), G10 | (vii) is path-independent (BR5; latent v4 defect L11) |
| `_capi_alias_problems` | R-ALIAS: the listed single-renaming selections; a named subset of R-QUAL | patterns unchanged; staging corrected (B1.1; L9); v4's O6 (a) completeness claim withdrawn |
| `_capi_qualifier_problems` (with `_capi_qualified`) | **R-QUAL** (a)–(d) (B0.10) | new (V4-RC4-ALIAS) |
| `_capi_write_problems` | R-W per form (B10), over every designed scope | unchanged |
| `_capi_gate_problems` (with `_capi_gate_row_problems` and `_capi_exclusive`) | **R-GATE** (B0.7): the exact gate form per kind; the discriminant once, inside the gate; branch-sensitive component places; the sole WF-X exception; completeness by discriminant selection and by `_Acceptance` declaration | replaces v4's after-test rule and its listed assigned-object exemption (V4-RC4-GATE; L10, L12) |
| `_capi_residual_problems` | R-RES, S-RES, R-LAYOUT, R-GLUE | unchanged |
| `_capi_diagnostic_problems` | D1–D5, G8 | unchanged |

### B8.3 Notes on the sketch (REPLACED in v5)

- **G6 (old-spec absence)** follows from the closure check. Each symbol must occur exactly once, at its `CAPI_CORE_HOME` entry, so any occurrence in the old spec fails (carried).
- **Isolation failure is a problem, never a skip.** Every isolation helper returns `None` or `''` instead of raising. The override converts any exception of a check into a problem (fail closed), because `contract_problems` (`proof_manifest.py:622-637`) catches only `OSError` from `export_problems` (carried).
- **Invariant checks.** `_capi_clause_problems`, `_capi_alias_problems`, `_capi_qualifier_problems`, `_capi_write_problems` and `_capi_gate_problems` are implied, for the B4 text and the S5 residual, by `_capi_tile_problems`, `_capi_transport_problems` and `_capi_residual_problems`. They are kept so that a reviewed amendment of B4 or of a table cannot weaken a rule while staying textually consistent (B0.2).
  - R-QUAL and R-GATE also validate their own table entries. Each listed qualified text must be a full expanded name or an exception listed for its scope, and each gate text must have its kind's form.
  - So an amendment that adds an indirect spelling, or a gate that is not branch-correct, to both the tile and the table is still refused (B12, the mutations marked *amendment*).
- **R-QUAL compares texts and never resolves names.** A path that happens to denote an Appendix C routine is refused because its text is not a full expanded name. Rule (d) makes each full expanded name denote its library unit.
- **Residual identity** (carried). `_capi_residual_problems` removes only designed spans and undoes only the recorded glue edits. Any other change to pre-existing C_API code therefore fails, including a change to `Authority_Glue`'s value decisions (D-21).
- **Mutation controls** (§8.8, C-09, B12; carried). These run each mutation in a temporary copy of the stage tree and expect at least one problem. They read text only and never build or run WORLDLINE code.
- **Limits** (carried). What these checks do not establish is listed in §8.9.

---

## B9.4 SPARK units, full expanded names and alias exclusion (REPLACED in v5)

### B9.4.1 `CAPI_SPARK_UNITS` (unchanged from v4)

These are the units that own Appendix C names. A read-only script confirmed that this set equals the set of unit prefixes of the Appendix C names.

`Worldline.Resources_C_API`, `Worldline.Recovery_C_API`, `Worldline.Recovery_Authorization_C_API`, `Worldline.Recovery_Authorization_V3_C_API`, `Worldline.Reservation_Lifecycle_C_API`, `Worldline.Resource_Ledger_C_API`, `Worldline.Resource_Policy_C_API`, `Worldline.Evaluation_History_C_API`, `Resource_Run_Ledger_C_API`, `Worldline.Chain_Authority_C_API`, `Evaluation_Completion_C`, `Evaluation_Completion_Roster`, `Evaluation_Finalization_C`, `Evaluation_Pending_C`, `Evaluation_Pending`, `Evaluation_Pending_V2_C` and `Evaluation_Pending_V2`.

### B9.4.2 R-QUAL name tables

- **`CAPI_ROUTINE_NAMES`** (PK-1, complete): the 98 names of Appendix C, in Appendix C order (v3 DESIGN lines 2478-2589, carried verbatim in v4 and v5).
  - All 98 are identifiers. None is an operator symbol.
  - They have 85 distinct last selectors.
  - They have 9 first identifiers (the roots of rule (d)): `Worldline`, `Resource_Run_Ledger_C_API`, `Evaluation_Completion_C`, `Evaluation_Completion_Roster`, `Evaluation_Finalization_C`, `Evaluation_Pending_C`, `Evaluation_Pending`, `Evaluation_Pending_V2_C` and `Evaluation_Pending_V2`.

  All of these were observed by a read-only script.
- **`CAPI_REMOVED_NAMES`** (PK-6b): the nine routines that PK-6b removes from `Evaluation_Completion_C` (O7, carried; each observed in S5 `core/evaluation_completion_c.ads`): `Evaluation_Completion_C.Decide`, `Evaluation_Completion_C.Raw_Decide`, `Evaluation_Completion_C.Metadata_Matches`, `Evaluation_Completion_C.Context_Matches`, `Evaluation_Completion_C.Metadata_Base`, `Evaluation_Completion_C.Diagnostic_Mark`, `Evaluation_Completion_C.Diagnostic_Value`, `Evaluation_Completion_C.Diagnostic_Exception` and `Evaluation_Completion_C.Diagnostic_Control`. From PK-6b there are 93 listed simple names (J59).
- **`CAPI_USE_PACKAGES`** = `('System.Storage_Elements',)` (R-INV (vii)).

### B9.4.3 `CAPI_QUALIFIER_EXCEPTIONS` (texts that are not full expanded names)

Each entry is observed in S5 or in the B4 text. Each denotes an entity that is neither an Appendix C routine nor a removed routine.

| Text | Scopes | From | What it denotes |
|---|---|---|---|
| `Evaluation.Classify` | RESIDUAL | PK-1 | `Worldline.Evaluation.Classify` (`core/worldline-evaluation.ads:113`), named through parent visibility in `Evaluation_Classify` (`core/worldline-c_api.adb:374`). It is not `Evaluation_Completion_Roster.Classify`. |
| `Hash_Probe.Present` | RESIDUAL | PK-1 | the component `Present` of the local object `Hash_Probe : Collapse_Wire.Raw_Optional_Hash` of `Layout_Offset` (`:571`), the prefix of `'Position` (`:656`) |
| `Counter_Probe.Present` | RESIDUAL | PK-1 | the component `Present` of the local object `Counter_Probe : Collapse_Wire.Raw_Optional_Counter` (`:572`), the prefix of `'Position` (`:660`) |
| `V1.Present` | RESIDUAL | PK-1 | a component of the local object `V1` of `Owner_Layout` (`:885`), the prefix of `'Position` (`:897`) |
| `V2.Present` | RESIDUAL | PK-1 | a component of the local object `V2` of `Owner_Layout`, the prefix of `'Position` (`:905`) |
| `Owner_Wire.Decide` | RESIDUAL | PK-1 | `Worldline.Owner_Transitions_Wire.Decide` (`core/worldline-owner_transitions_wire.ads:138`) through the residual renaming `Owner_Wire` (B9.1 index 25); `:1015` |
| `Retry_Wire.Decide` | RESIDUAL | PK-1 | `Worldline.Owner_Retry_Audit_Wire.Decide` (`core/worldline-owner_retry_audit_wire.ads:56`) through `Retry_Wire` (B9.1 index 30); `:1112` |
| `Completion_Transport.Context_Matches` | RESIDUAL, `Finalization_Decide_Mixed`, `Finalization_Transport.Final_Context_Matches` | PK-6b | the moved, tiled transport subprogram of B4.16 (`SPARK_Mode => Off`), called by GE3, GE4, B4.22 and B4.21. It is not the removed routine `Evaluation_Completion_C.Context_Matches`. |
| `Completion_Transport.Metadata_Base` | RESIDUAL, `Finalization_Decide_Mixed`, `Finalization_Transport.Final_Context_Matches` | PK-6b | the moved, tiled transport subprogram of B4.18, called by GE5, GE6, B4.22 and B4.21 |

There are seven entries from PK-1 and nine from PK-6b (J63).

### B9.4.4 `CAPI_QUALIFIED` (the exact per-scope expanded qualifiers)

Notation: `P.` + `A`, `B` ×2 means the texts `P.A` (once) and `P.B` (twice); every count not shown is 1. The table was derived by a read-only author script from the assembled B4 and S5 text with each occurrence attributed to its innermost scope, and it agrees with the B4 tiles (B8.0).

| Scope | From | Qualified routine names (exact multiset) |
|---|---|---|
| RESIDUAL | PK-1 | `Evaluation.Classify`, `Hash_Probe.Present`, `Counter_Probe.Present`, `V1.Present`, `V2.Present`, `Owner_Wire.Decide`, `Retry_Wire.Decide` (7 occurrences) |
| RESIDUAL | PK-6b value | the seven above, plus `Completion_Transport.Context_Matches` ×2 (GE3, GE4) and `Completion_Transport.Metadata_Base` ×2 (GE5, GE6): 11 occurrences (J64) |
| `Resources_Can_Reserve` | PK-1 | `Worldline.Resources_C_API.` + `Negative_Flag_Valid`, `Can_Reserve_Value` |
| `Recovery_Select` | PK-1 | `Worldline.Recovery_C_API.` + `Presence_Valid`, `Present` ×4, `Select_Value` |
| `Recovery_Authorization_Decide_V2` | PK-2 | `Worldline.Recovery_Authorization_C_API.Decide_Total` |
| `Recovery_Authorization_Decide_V3` | PK-2 | `Worldline.Recovery_Authorization_V3_C_API.Decide_Total` |
| `Reservation_Lifecycle_Plan` | PK-3 | `Worldline.Reservation_Lifecycle_C_API.` + `Request_Valid`, `Requested_Of`, `Operation_Of`, `Accept_Row`, `Publishes_Mask`, `Mask_Byte`, `Status_Code` |
| `Resource_Ledger_Compute` | PK-3 | `Worldline.Resource_Ledger_C_API.` + `Accept_Row`, `Encode_Quantity`, `Result_Of` |
| `Resource_Ledger_Headroom` | PK-3 | `Worldline.Resource_Ledger_C_API.` + `Accept_Headroom_Inputs`, `Result_Of` |
| `Resource_Policy_Admit` | PK-3 | `Worldline.Resource_Policy_C_API.` + `Accept_Input`, `Accept_Disk`, `Encode_Decision` |
| `Evaluation_History_Select` | PK-4 | `Worldline.Evaluation_History_C_API.` + `Final_Flag_Valid`, `Final_Row_Present` ×2, `Accept_Query`, `Accept_Final_Row`, `Accept_Row`, `Select_Result` |
| `Run_Ledger_Check` | PK-5 | `Resource_Run_Ledger_C_API.Check_Decision` |
| `Chain_Replay` | PK-5 | `Worldline.Chain_Authority_C_API.` + `Accept_Row`, `Replay_Value` |
| `Completion_Decide` | PK-6b | `Evaluation_Completion_C.` + `Decide_Header_Valid`, `Decide_Fields_Valid`, `Accept_Journal_Row`, `Accept_Captured_Row`, `Accept_Result_Row`, `Accept_History_Row`, `Accept_Required_Row`, `Decide_Value` |
| `Completion_Raw_Decide` | PK-6b | `Evaluation_Completion_C.` + `Raw_Header_Valid`, `Raw_Fields_Valid`, `Accept_Journal_Row`, `Accept_Raw_Check_Row`, `Accept_Raw_Measure`, `Accept_Result_Row`, `Accept_History_Row`, `Accept_Required_Row`, `Raw_Decide_Value` |
| `Completion_Transport.Context_Matches` | PK-6b | `Evaluation_Completion_C.` + `Context_Header_Valid`, `Context_Fields_Valid`, `Context_Agent_Matches`, `Accept_Context_Fields`, `Accept_Context_Row`, `Accept_Required_Pair`, `Context_Join_Value`, `Join_Code` ×2 |
| `Completion_Transport.Metadata_Base` | PK-6b | `Evaluation_Completion_C.Metadata_Version_Valid` |
| `Completion_Metadata_Matches` | PK-6b | `Evaluation_Completion_C.` + `Metadata_Header_Valid`, `Accept_Metadata_Row`, `Join_Code` |
| `Native_Diagnostic_Control` | PK-6b | `Evaluation_Completion_C.` + `Diagnostic_Control_Of`, `Diagnostic_Start`, `Diagnostic_Stop`, `Diagnostic_Invalid_Code` |
| `body:Diagnostic_Transport` | PK-6b | `Evaluation_Completion_C.` + `Diagnostic_Begin_Line`, `Diagnostic_Line`, `Diagnostic_Latch_Failure` ×3, `Diagnostic_Begin_Value`, `Diagnostic_Value_Site`, `Diagnostic_Observe`, `Diagnostic_Begin_Exception`, `Diagnostic_Exception_Site` |
| `Finalization_Decide` | PK-6b | `Evaluation_Finalization_C.` + `Request_Header_Valid`, `Request_Fields_Valid`, `Accept_Plan`, `Needs_Rows`, `Accept_Row`, `Decide_Rows_Value`, `Decide_No_Rows_Value` |
| `Finalization_Transport.Final_Context_Matches` | PK-6b | `Evaluation_Finalization_C.` + `Final_Seal_Ready`, `Final_Plans_Valid`, `Final_Projected_Row`, `Final_Projection`; and `Completion_Transport.Context_Matches`, `Completion_Transport.Metadata_Base` (exceptions) |
| `Finalization_Decide_Mixed` | PK-6b | `Evaluation_Finalization_C.` + `Kind_Of` ×2, `Ordinary_Readiness`, `Finalized_Readiness`, `Finalized_Operation_Readiness`, `Agent_Readiness`, `Context_Join_Needed` ×2, `Mixed_Collapse_Decision`, `Mixed_Authorized`, `Mixed_Metadata_Needed` ×2; and `Completion_Transport.Context_Matches`, `Completion_Transport.Metadata_Base` (exceptions) |
| `Pending_Decide_V1` | PK-7 | `Evaluation_Pending_C.` + `Header_Valid`, `Request_Fields_Valid`, `Accept_Row`, `Decide_Value` |
| `Pending_Decide_V2` | PK-7 | `Evaluation_Pending_V2_C.` + `Header_Valid`, `Request_Fields_Valid`, `Accept_Row`, `Decide_Value` |

Every other scope has no entry, so it must contain no qualified routine name. These scopes are: `Recovery_Protocol_Decide_V1`; `spec:` and `body:` of the 15 unit transports, outside their tiled moved subprograms; `spec:Diagnostic_Transport`; and SPEC, the C_API specification.

### B9.4.5 Indirect-path inventory (documentation; R-QUAL (a) refuses every entry without using it)

**Method (read-only script).**
- The script collected the package renamings declared in the visible parts of all S5 `core/*.ads` specifications. Each renaming target was resolved within its own unit. The resulting graph is acyclic, and its longest chain is 5 renamings (from `Evaluation_Finalization` and from `Evaluation_Completion_C`).
- It then enumerated, from every package renaming visible in a designed or residual scope, every path that reaches a unit of `CAPI_SPARK_UNITS`.
- The routine names reachable along these paths are:
  - `Decide` (in `Evaluation_Pending` and `Evaluation_Pending_V2`);
  - `Classify` (in `Evaluation_Completion_Roster`);
  - every `Evaluation_Completion_C` Appendix C name, through `K`;
  - from PK-6b, every removed name, through `K`.

| Renamings visible in | Paths to Appendix C units (target unit: paths) | Count |
|---|---|---|
| `Finalization_Transport` (CL-T15): use-visible in `Finalization_Decide` and `Finalization_Decide_Mixed`, directly visible in the transport and in `Final_Context_Matches` | `Evaluation_Completion_C`: `K`. `Evaluation_Completion_Roster`: `Authority.Roster`, `F.R.Old`, `K.A.Roster`, `R.Old`. `Evaluation_Pending`: `P`, `F.P`, `F.T.P`, `F.T.R.P`, `F.R.T.P`, `F.R.T.R.P`, `F.R.Old.T.P`, `F.R.Old.T.R.P`, `R.T.P`, `R.T.R.P`, `R.Old.T.P`, `R.Old.T.R.P`, `Authority.T.P`, `Authority.T.R.P`, `Authority.Roster.T.P`, `Authority.Roster.T.R.P`, `K.A.T.P`, `K.A.T.R.P`, `K.A.Roster.T.P`, `K.A.Roster.T.R.P`. `Evaluation_Pending_V2`: `F.T.R`, `F.R.T.R`, `F.R.Old.T.R`, `R.T.R`, `R.Old.T.R`, `Authority.T.R`, `Authority.Roster.T.R`, `K.A.T.R`, `K.A.Roster.T.R` | 34 |
| `Completion_Transport` (CL-T14): use-visible in `Completion_Decide`, `Completion_Raw_Decide` and `Completion_Metadata_Matches`, directly visible in `Context_Matches` and `Metadata_Base` | `Evaluation_Pending`: `P`, `T.P`, `T.R.P`, `V.P`, `Roster.T.P`, `Roster.T.R.P`, `Raw_Roster.T.P`, `Raw_Roster.T.R.P`, `Raw_Roster.Old.T.P`, `Raw_Roster.Old.T.R.P`. `Evaluation_Pending_V2`: `V`, `T.R`, `Roster.T.R`, `Raw_Roster.T.R`, `Raw_Roster.Old.T.R`. `Evaluation_Completion_Roster`: `Roster`, `Raw_Roster.Old` | 17 |
| `Pending_Transport` (CL-T10) | `Evaluation_Pending`: `E` | 1 |
| `Pending_V2_Transport` (CL-T11) | `Evaluation_Pending`: `E`, `V2.P`. `Evaluation_Pending_V2`: `V2` | 3 |
| the tile-local `CA` of `Context_Matches` and `Completion_Metadata_Matches` | `Evaluation_Completion_Roster`: `CA.Roster`. `Evaluation_Pending`: `CA.T.P`, `CA.T.R.P`, `CA.Roster.T.P`, `CA.Roster.T.R.P`. `Evaluation_Pending_V2`: `CA.T.R`, `CA.Roster.T.R` | 7 |
| the residual `Authority_Glue` body (`A`, B9.1 index 11) | `Evaluation_Completion_Roster`: `A.Roster`. `Evaluation_Pending`: `A.T.P`, `A.T.R.P`, `A.Roster.T.P`, `A.Roster.T.R.P`. `Evaluation_Pending_V2`: `A.T.R`, `A.Roster.T.R` | 7 |
| the residual `Decide_Raw_Context` (`K`, `T`, B9.1 indices 17, 18; and `K` of `Decide_Raw_Metadata`, index 22, until R-DEL-1) | `Evaluation_Completion_C`: `K`. `Evaluation_Completion_Roster`: `K.A.Roster`. `Evaluation_Pending`: `K.A.T.P`, `K.A.T.R.P`, `K.A.Roster.T.P`, `K.A.Roster.T.R.P`, `T.P`, `T.R.P`. `Evaluation_Pending_V2`: `K.A.T.R`, `K.A.Roster.T.R`, `T.R` | 11 |

**Totals.**
- 80 paths in all (J65).
- 71 have two or more identifiers (J66). v4 covered none of these.
- 9 are single identifiers (J67). v4 already listed them in R-ALIAS: `K` and `P` (finalization); `P`, `V` and `Roster` (completion); `E` (pending); `E` and `V2` (pending v2); `K` (residual).

**Families with no fixed length** (every member is refused by (a), since none equals a full expanded name):
- **Transport-qualified paths.** A designed transport is directly visible by name in all later C_API body text, including the residual `Authority_Glue`, which follows the transport run. So `<Transport>.<path>.<routine>` can be written for every path above declared in that transport, in any later scope. Examples: `Pending_Transport.E.Decide`, `Finalization_Transport.F.P.Decide`, `Completion_Transport.Roster.Classify`, `Finalization_Transport.K.Decide_Value`.
- **`C_API.` or `Worldline.C_API.` followed by any transport-qualified path.** Example: `Worldline.C_API.Pending_Transport.E.Decide`.
- **Parent-visibility shortenings.** These cover the ten `Worldline.*_C_API` units of `CAPI_SPARK_UNITS`, for example `Recovery_C_API.Present` and `Resources_C_API.Can_Reserve_Value`. They also cover paths through shortened parents, for example `Evaluation_Authority.Roster.Classify`.
- **Library units reached through with clauses.** Examples: `Evaluation_Completion.P.Decide`, `Evaluation_Completion_C.A.Roster.Classify`, `Worldline.Evaluation_Authority.Roster.Classify` and `Evaluation_Pending_V2.P.Decide`. Once the finalization transport's `with Evaluation_Finalization;` is present, `Evaluation_Finalization.P.Decide` is another.
- **`Standard.` followed by any of the above, or by a full expanded name.**

### B9.4.6 R-ALIAS pairs (`CAPI_ALIAS_FORBIDDEN`; patterns unchanged, staging corrected)

**Renamings in designed or residual scopes whose target is an Appendix C unit**, directly or through the renaming they are defined by. These are unchanged from v4:
- `E` → `Evaluation_Pending` (both pending transports);
- `V2` → `Evaluation_Pending_V2`;
- `P` → `Evaluation_Pending` (completion transport); and `P` = `F.P` = `Evaluation_Finalization.P` → `T.P` → `Evaluation_Pending` (finalization transport);
- `V` → `Evaluation_Pending_V2`;
- `Roster` → `Evaluation_Completion_Roster`;
- `K` → `Evaluation_Completion_C` (finalization transport and residual B9.1 index 17).

`P` also names `Resource_Admission` in the policy transport. The exclusion is body-wide and therefore conservative: it can only refuse more, never less.

**Pairs from PK-1** (41, J60):
- `E.Decide`, `P.Decide`, `V2.Decide`, `V.Decide` and `Roster.Classify`;
- `K.` followed by each of the 36 `Evaluation_Completion_C` Appendix C simple names: `Decide_Header_Valid`, `Decide_Fields_Valid`, `Accept_Journal_Row`, `Accept_Captured_Row`, `Accept_Result_Row`, `Accept_History_Row`, `Accept_Required_Row`, `Decide_Value`, `Raw_Header_Valid`, `Raw_Fields_Valid`, `Accept_Raw_Check_Row`, `Accept_Raw_Measure`, `Raw_Decide_Value`, `Context_Header_Valid`, `Context_Fields_Valid`, `Context_Agent_Matches`, `Accept_Context_Fields`, `Accept_Context_Row`, `Accept_Required_Pair`, `Context_Join_Value`, `Join_Code`, `Metadata_Version_Valid`, `Metadata_Header_Valid`, `Accept_Metadata_Row`, `Diagnostic_Control_Of`, `Diagnostic_Invalid_Code`, `Diagnostic_Start`, `Diagnostic_Stop`, `Diagnostic_Observe`, `Diagnostic_Latch_Failure`, `Diagnostic_Begin_Line`, `Diagnostic_Line`, `Diagnostic_Begin_Value`, `Diagnostic_Value_Site`, `Diagnostic_Begin_Exception` and `Diagnostic_Exception_Site`.

**Pairs appended at PK-6b** (9; 50 in all, J61): `K.` followed by `Decide`, `Raw_Decide`, `Metadata_Matches`, `Context_Matches`, `Metadata_Base`, `Diagnostic_Mark`, `Diagnostic_Value`, `Diagnostic_Exception` and `Diagnostic_Control`.

A pattern is `(?<![\w.])X\s*\.\s*N(?!\w)`, matched case-insensitively on N2.
- `K.Diagnostic_Value` does not match `K.Diagnostic_Value_Site`, so both are listed.
- Type selections remain allowed: `K.Result`, `K.U32`, `K.Check_Row`, `K.Required_Row`, `K.Request`, `E.Bytes`, `P.Count`, `Roster.Check_Array`, and so on.

---

## B10.3 Gates (`CAPI_GATES`, `CAPI_GATE_EXCLUSIVE`; REPLACED in v5)

**What each row gives.** The gate kind, the object, its exact N1 gate text, and the components allowed in each branch. R-GATE (B0.7) checks every row:
- the gate text occurs once in its scope;
- the object is declared once;
- its discriminant is selected exactly once, inside the gate;
- each component is selected only in a branch that lists it.

**Branch lists.**
- `bool`: **T** lists `True`-variant components, allowed only after the gate. **F** lists `False`-variant components, allowed only inside the rejection branch: the diagnostic statements between `then` and the branch's `return`.
- `case`: each alternative's components, allowed only inside that alternative.
- `wfx`: **T** only after the gate. The exclusive assignments are fixed by `CAPI_GATE_EXCLUSIVE`.

**Where the lists come from.** They are the components that the B4 tiles select in each branch (author script). Each is a component of the variant that the branch establishes in the design's record types (v3 §5.2 and §7, carried). The `False` variant of every acceptance type except `Context_Fields_Acceptance` is null, and so is the `Row_Rejected` variant of `Context_Row_Acceptance`.

There are 33 rows (J62): 31 `bool`, 1 `case` and 1 `wfx`.

| Id | Scope | Object | Kind | Gate text (exact N1) | Components by branch |
|---|---|---|---|---|---|
| G06 | `Reservation_Lifecycle_Plan` | `D` | bool | `D : constant Worldline.Reservation_Lifecycle_C_API.Row_Acceptance := Worldline.Reservation_Lifecycle_C_API.Accept_Row (Row); begin if not D.Ok then return 255; end if;` | T: `Item`; F: none |
| G07 | `Resource_Ledger_Compute` | `D` | bool | `D : constant Worldline.Resource_Ledger_C_API.Row_Acceptance := Worldline.Resource_Ledger_C_API.Accept_Row (V); begin if not D.Ok then return 255; end if;` | T: `Row`, `Slot`; F: none |
| G08 | `Resource_Ledger_Headroom` | `HI` | bool | `HI : constant Worldline.Resource_Ledger_C_API.Headroom_Acceptance := Worldline.Resource_Ledger_C_API.Accept_Headroom_Inputs (A, W, F); begin if not HI.Ok then return 255; end if;` | T: `Available`, `Withheld`, `Floor`; F: none |
| G09a | `Resource_Policy_Admit` | `IA` | bool | `IA : constant Worldline.Resource_Policy_C_API.Input_Acceptance := Worldline.Resource_Policy_C_API.Accept_Input (V); begin if not IA.Ok then return 255; end if;` | T: `State`; F: none |
| G09b | `Resource_Policy_Admit` | `D` | bool | `D : constant Worldline.Resource_Policy_C_API.Disk_Acceptance := Worldline.Resource_Policy_C_API.Accept_Disk (Row); begin if not D.Ok then return 255; end if;` | T: `Item`; F: none |
| G10a | `Evaluation_History_Select` | `QA` | bool | `QA : constant Worldline.Evaluation_History_C_API.Query_Acceptance := Worldline.Evaluation_History_C_API.Accept_Query (Raw_Q); begin if not QA.Ok then return 255; end if;` | T: `Item`; F: none |
| G10b | `Evaluation_History_Select` | `FA` | bool | `FA : constant Worldline.Evaluation_History_C_API.Final_Acceptance := Worldline.Evaluation_History_C_API.Accept_Final_Row (V); begin if not FA.Ok then return 255; end if;` | T: `Item`; F: none |
| G10c | `Evaluation_History_Select` | `D` | bool | `D : constant Worldline.Evaluation_History_C_API.Row_Acceptance := Worldline.Evaluation_History_C_API.Accept_Row (V); begin if not D.Ok then return 255; end if;` | T: `Item`; F: none |
| G13a | `Completion_Decide` | `JA` | bool | `JA : constant Evaluation_Completion_C.Journal_Acceptance := Evaluation_Completion_C.Accept_Journal_Row (X); begin if not JA.Ok then return 255; end if;` | T: `Item`; F: none |
| G13b | `Completion_Decide` | `CR` | bool | `CR : constant Evaluation_Completion_C.Captured_Acceptance := Evaluation_Completion_C.Accept_Captured_Row (X); begin if not CR.Ok then return 255; end if;` | T: `Item`, `Measure`; F: none |
| G13c | `Completion_Decide` | `RR` | bool | `RR : constant Evaluation_Completion_C.Result_Acceptance := Evaluation_Completion_C.Accept_Result_Row (X); begin if not RR.Ok then return 255; end if;` | T: `Item`; F: none |
| G13d | `Completion_Decide` | `HR` | bool | `HR : constant Evaluation_Completion_C.History_Acceptance := Evaluation_Completion_C.Accept_History_Row (X); begin if not HR.Ok then return 255; end if;` | T: `Item`; F: none |
| G13e | `Completion_Decide` | `QR` | bool | `QR : constant Evaluation_Completion_C.Required_Acceptance := Evaluation_Completion_C.Accept_Required_Row (X); begin if not QR.Ok then return 255; end if;` | T: `Item`; F: none |
| G14a | `Completion_Raw_Decide` | `JA` | bool | as G13a | T: `Item`; F: none |
| G14b | `Completion_Raw_Decide` | `KA` | bool | `KA : constant Evaluation_Completion_C.Raw_Check_Acceptance := Evaluation_Completion_C.Accept_Raw_Check_Row (X); begin if not KA.Ok then return 255; end if;` | T: `Item`, `Declared`; F: none |
| G14c | `Completion_Raw_Decide` | `MA` | bool | `MA : constant Evaluation_Completion_C.Raw_Measure_Acceptance := Evaluation_Completion_C.Accept_Raw_Measure (KA.Item, KA.Declared, Wire, Confined); begin if not MA.Ok then return 255; end if;` | T: `Item`; F: none |
| G14d | `Completion_Raw_Decide` | `RR` | bool | as G13c | T: `Item`; F: none |
| G14e | `Completion_Raw_Decide` | `HR` | bool | as G13d | T: `Item`; F: none |
| G14f | `Completion_Raw_Decide` | `QR` | bool | as G13e | T: `Item`; F: none |
| G15 | `Completion_Metadata_Matches` | `MA` | bool | `MA : constant Evaluation_Completion_C.Metadata_Row_Acceptance := Evaluation_Completion_C.Accept_Metadata_Row (Original, Owned); begin if not MA.Ok then Diagnostic_Transport.Value ("completion.metadata.row-rejected", I64 (I)); return 255; end if;` | T: `Row`, `Projected`; F: none |
| G16a | `Completion_Transport.Context_Matches` | `FA` | bool | `FA : constant Evaluation_Completion_C.Context_Fields_Acceptance := Evaluation_Completion_C.Accept_Context_Fields (X); begin if not FA.Ok then Diagnostic_Transport.Value ("completion.context.field-rejected", FA.Rejected_Position); return 255; end if;` | T: `Expected`, `Observed`; F: `Rejected_Position` |
| G16b | `Completion_Transport.Context_Matches` | `RA` | case | `RA : constant Evaluation_Completion_C.Context_Row_Acceptance := Evaluation_Completion_C.Accept_Context_Row (Original, Owned); begin case RA.Verdict is` | `when Evaluation_Completion_C.Row_Rejected =>`: none; `when Evaluation_Completion_C.Row_Field_Rejected =>`: `Rejected_Field_Position`; `when Evaluation_Completion_C.Row_Accepted =>`: `Row`, `Joined` |
| G16c | `Completion_Transport.Context_Matches` | `QA` | bool | `QA : constant Evaluation_Completion_C.Required_Pair_Acceptance := Evaluation_Completion_C.Accept_Required_Pair (Original, Owned); begin if not QA.Ok then Diagnostic_Transport.Value ("completion.context.required-rejected", I64 (I)); return 255; end if;` | T: `Item`, `Expected`; F: none |
| G17 | `Run_Ledger_Check` | `O` | bool | `O : constant Resource_Run_Ledger_C_API.Check_Acceptance := Resource_Run_Ledger_C_API.Check_Decision (Data, Raw, Before, Proposed, Observed); begin if not O.Ok then return -1; end if;` | T: `Value`; F: none |
| G18a | `Chain_Replay` | `D` | bool | `D : constant Worldline.Chain_Authority_C_API.Row_Acceptance := Worldline.Chain_Authority_C_API.Accept_Row (Raw); begin if not D.Ok then return -1; end if;` | T: `Item`; F: none |
| G18b | `Chain_Replay` | `RV` | bool | `RV : constant Worldline.Chain_Authority_C_API.Replay_Acceptance := Worldline.Chain_Authority_C_API.Replay_Value (Owned, H); begin if not RV.Ok then return -1; end if;` | T: `Value`; F: none |
| G19a | `Pending_Decide_V1` | `D` | bool | `D : constant Evaluation_Pending_C.Row_Acceptance := Evaluation_Pending_C.Accept_Row (V); begin if not D.Ok then return 255; end if;` | T: `Item`; F: none |
| G19b | `Pending_Decide_V1` | `O` | bool | `O : constant Evaluation_Pending_C.Decide_Acceptance := Evaluation_Pending_C.Decide_Value (A, J, R); begin if not O.Ok then return 255; end if;` | T: `Value`; F: none |
| G20a | `Pending_Decide_V2` | `D` | bool | `D : constant Evaluation_Pending_V2_C.Row_Acceptance := Evaluation_Pending_V2_C.Accept_Row (V); begin if not D.Ok then return 255; end if;` | T: `Item`; F: none |
| G20b | `Pending_Decide_V2` | `O` | bool | `O : constant Evaluation_Pending_V2_C.Decide_Acceptance := Evaluation_Pending_V2_C.Decide_Value (A, J, R); begin if not O.Ok then return 255; end if;` | T: `Value`; F: none |
| G21a | `Finalization_Decide` | `PA` | bool | `PA : constant Evaluation_Finalization_C.Plan_Acceptance := Evaluation_Finalization_C.Accept_Plan (Q); begin if not PA.Ok then Diagnostic_Transport.Value ("finalization.decide.required-rejected", I64 (K)); return 255; end if;` | T: `Item`; F: none |
| G21b | `Finalization_Decide` | `RA` | bool | `RA : constant Evaluation_Finalization_C.Row_Acceptance := Evaluation_Finalization_C.Accept_Row (Q); begin if not RA.Ok then Diagnostic_Transport.Value ("finalization.decide.row-rejected", I64 (K)); return 255; end if;` | T: `Item`; F: none |
| G21c | `Finalization_Decide` | `O` | wfx | `O := Evaluation_Finalization_C.Decide_Rows_Value (X, A, Required, Captured); else O := Evaluation_Finalization_C.Decide_No_Rows_Value (X, A, Required); end if; if not O.Ok then return 255; end if;` | T: `Value`; F: none (null variant) |

**`CAPI_GATE_EXCLUSIVE`** (PK-6b): `'G21c'` maps to four texts.
- **Declaration:** `O : Evaluation_Finalization_C.Decide_Acceptance;` (B4.20 segment 4).
- **Region:** B4.20 segment 6 without its final ` if not O.Ok then return 255; end if;`. That is the exact text from `if Evaluation_Finalization_C.Needs_Rows (X) then` through the `end if;` that follows the else-assignment (the §5.1 text, RC2).
- **Then-assignment:** `O := Evaluation_Finalization_C.Decide_Rows_Value (X, A, Required, Captured);`
- **Else-assignment:** `O := Evaluation_Finalization_C.Decide_No_Rows_Value (X, A, Required);`

**Changes from v4 in this table.**
- Every row now has a kind and its components by branch.
- G21c's gate text now begins at the then-assignment; v4's began at `else`. So one exact text fixes both exclusive assignments, the `else`, the region's `end if;` and the test.
- `CAPI_GATE_ASSIGNED` is replaced by `CAPI_GATE_EXCLUSIVE`.
- v4's sentence "Every payload selection begins after that test, including the refusal-branch reads of `FA.Rejected_Position` and `RA.Rejected_Field_Position` …" is replaced by the branch lists above.
- Every other gate text is byte-identical to v4.

Undiscriminated SPARK results are not acceptance records and have no gate row (carried):
- `Readiness_Result` values `Observed` and `R1`;
- `Boolean` and `U8` results;
- the `K.Check_Row` and `K.Request` results of `Final_Projected_Row` and `Final_Projection`.

Their provenance is fixed by the tiles. None is declared with an `_Acceptance` subtype, so completeness does not apply to them.

---

## B11. Promise-to-check matrix (REPLACED in v5)

"Text" means a manifest check in B8. "Evidence" means an obligation that no text check can close; it is listed so that no promise is silently assumed to be enforced. Rows 1–40 are v4's, with rows 7, 10, 14 and 24 restated. Rows 41 and 42 are new, giving 42 rows (J68).

| # | Promised condition (where stated) | Matching check | Kind |
|---|---|---|---|
| 1 | Guards copied verbatim, value runs replaced in original order, short-circuit kept (§3.1 rule 1, M1) | R-TILE (guard segments exact) | Text |
| 2 | Every intervening transport operation, allocation and early return kept (M2) | R-TILE | Text |
| 3 | No prevalidation; reads only after their gating decision; per-row staging; no bulk copy; unconditional reads kept (M3, §3.3) | R-TILE; read frontiers §9.6 with C-05 | Text + behavioural |
| 4 | Only the listed pure, infallible decodes move into acceptors (M4) | R-TILE (moved text visible as absent); unit pins and full-body review for the SPARK side | Text + review |
| 5 | Value routines: `Global => null`, no `Pre`, no functional `Post` (V1, LD2) | Unit pins of the PK-xa/PK-x specifications, full-body review and the strict command | Evidence |
| 6 | Re-check of the identical predicate on the identical constant (V3) | R-TILE (same constant passed) and proof of the SPARK body | Text + evidence |
| 7 | Discriminant tested before any component is read, and each component read only where its variant is established (A1, V4) | R-GATE v5 (B0.7, B10.3): the exact gate form per kind; the discriminant once, inside the gate; `False` components only in the rejection branch; `True` components only after the gate; case components only in their alternative; completeness. Plus R-TILE. | Text |
| 8 | Every out formal defined on every path (V5) | Strict flow analysis on the exact candidate | Evidence |
| 9 | Existing contracts evaluated where they were (V6) | R-TILE (call sites); A-COST tallies | Text + evidence |
| 10 | Unique, fully qualified names at every call to an Appendix C routine (V7, O6 (a)) | R-QUAL (B0.10: exact per-scope expanded qualifiers, no non-name prefix, no attribute, no capture), R-INV (v) and (vii) (path-independent), R-ALIAS (named subset), plus R-TILE | Text |
| 11 | Capture every input before the first write; existing overlap refusals kept, none added (§3.4) | R-TILE; C-03 behavioural | Text + behavioural |
| 12 | Each export's write set, conditions and order (§3.4, §12) | R-TILE and R-W (every foreign write has exactly one row) | Text |
| 13 | Result provenance for every write form (O4/R-W revised) | R-W per form WF-C/A/F/O/B/R/P/X/H (B10) | Text |
| 14 | Finalization `O` assigned on exactly two exclusive paths, before its single test (§5.1) | R-GATE `wfx` (G21c: the exact declaration without initializer, region, then- and else-assignments and test; `_capi_exclusive`; exactly two assignments at those places), R-W WF-X (count 2) and R-TILE (segment 6 = §5.1 text) | Text |
| 15 | Completion `Response` is the `out` actual of exactly one call and is not otherwise assigned | R-W WF-R | Text |
| 16 | `Captured` never passed or read on Operations 0/1 (§5.1, RC2) | R-TILE (segment 6) | Text |
| 17 | Handler and refusal code of each export unchanged (§3.5, LD1) | R-TILE (exception segments) | Text |
| 18 | Size constants outside handlers; allocations at original positions (§3.5) | R-TILE | Text |
| 19 | Transport helpers verbatim; no cross-unit sharing (§3.6, D-08) | R-TRANS helper hashes and per-transport residue | Text |
| 20 | Transports replicate the original renamings and declare only the listed subtypes (§3.6) | R-INV (B9.2) and R-TRANS | Text |
| 21 | No package renaming beyond the inventory (O6 (b)) | R-INV (i), (ii), (v) | Text |
| 22 | Export-body use clauses exactly as listed (O6 (c), revised) | R-INV (i) | Text |
| 23 | No elaboration code or extra declarations in transports | R-TRANS (empty residue) | Text |
| 24 | Pre-existing C_API code unchanged except the recorded glue edits (§3.6 (c), D-21, O7) | R-RES, R-GLUE, R-ALIAS (O7 names; removed-name pairs from PK-6b) and R-QUAL (from PK-6b, no dotted name of a removed routine except the listed `Completion_Transport` subprograms) | Text |
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
| 41 | The original rejection diagnostics stay inside their rejection branches, after the discriminant test, and never run on the accepted path. They are G15, G16a (`FA.Rejected_Position`), G16b (`RA.Rejected_Field_Position`, in `Row_Field_Rejected`), G16c, G21a and G21b (V4-RC4-GATE). | R-GATE (gate texts include the diagnostics; `False` and case components confined to their branch), D3 (site sequences), R-TILE | Text |
| 42 | Every remaining denotation of an Appendix C or removed routine in the C_API pair is its full expanded name. Indirect, transport-qualified, `C_API`-qualified, parent-shortened and `Standard`-prefixed spellings are refused (V4-RC4-ALIAS). | R-QUAL (a)–(d) with R-INV (v) and (vii); the B9.4.5 inventory is documentation | Text (static; installed resolution OPEN, D-38) |

---

## B12. Mutation controls for the v5 checks (REPLACED in v5; C-09 additions; static, temporary trees, no WORLDLINE run)

**How each mutation runs.** Each mutation runs in a temporary copy of the stage tree and must produce at least one problem. This adds to the v3 list in §8.8.

**Two variants.**
- **body:** a mutation that changes only the source. R-TILE also refuses it; the row names the invariant check that must refuse it as well.
- **amendment:** a mutation that also changes the matching table entries (`CAPI_TILES`, `CAPI_GATES`, `CAPI_GATE_EXCLUSIVE`, `CAPI_QUALIFIED`, `CAPI_INVENTORY`, `CAPI_TRANSPORTS`), as a later reviewed amendment would. R-TILE and the table-equality checks then pass, and the named invariant must still refuse it.

**Simulation.** *(sim)* marks the mutations that the author simulation of B8.0 exercised on the assembled text. Each produced at least one problem from the named check. That is a self-check of the sketch, not the control.

| Rule | Mutations |
|---|---|
| R-TILE | Carried from v4: Insert a statement between an acceptance declaration and its gate. Swap two loops. Read a row before its gate. Delete an early return. Change a refusal code. Add a second write. Reorder the exclusive branches. Change one character of a guard. |
| R-TRANS | Carried from v4: Change one character in a copied helper. Add an elaboration `begin … end` part to a transport body. Add an extra declaration to a transport specification. Move a helper to another transport. Share one helper between two transports. |
| R-INV | Carried from v4: Add `use Evaluation_Completion_C;` to an export body. Add `use all type Request;`. Move a use clause from a transport specification into a transport body. Drop `use System.Storage_Elements;` from an export body. Add `function Present (…) return Boolean renames Worldline.Recovery_C_API.Present;` to a transport. Add a clause to the context clause or to the C_API specification. Keep residual index 22 after PK-6b. |
| R-INV (vii), path-independent | The (vii) check must refuse each of the following (amendment, with `CAPI_INVENTORY` and `CAPI_QUALIFIED` amended to match) *(sim)*: MV1 `use F.P;` in `Finalization_Decide`. MV2 `use Recovery_C_API;` in `Recovery_Select`. MV3 `use Completion_Transport.P;` in `Completion_Decide`. MV4 `use Evaluation_Pending_C;` in `Pending_Decide_V1`, with its `Decide_Value (A, J, R)` call left unprefixed. |
| R-ALIAS | Carried from v4: Add `package S renames Worldline.Recovery_C_API;` and call `S.Present` (also refused by R-INV and R-QUAL). Call `K.Diagnostic_Start` from `Final_Context_Matches`. Call `E.Decide` from a pending export. **New:** MA1, at PK-6b, leave `K.Raw_Decide` in `Decide_Raw_Context` (GE1 not applied); R-ALIAS, R-GLUE and R-QUAL refuse *(sim)*. **Positive control (L9):** the unchanged S5 residual with the PK-1 designed text gives no R-ALIAS problem *(sim)*; with v4's complete table it gave four. |
| R-QUAL | Each in the scope named *(sim)*. The simulation ran MQ1–MQ4, MQ8, MQ9 and MQ13 twice. With `CAPI_QUALIFIED` unchanged, (a) refused them by the multiset. With `CAPI_QUALIFIED` amended to match, (a) refused them by its table validation, or (b) did. MQ5, MQ6 and MQ10–MQ12 ran with the table amended, and the table validation, (c) or (d) refused them. MQ7 and MQ14 ran in the body only.<br>MQ1 `F.P.Decide` in `Finalization_Decide`.<br>MQ2 deeper renaming paths: `F.T.P.Decide`, `F.T.R.Decide`, `F.R.Old.Classify`, `R.T.P.Decide`, `K.A.Roster.Classify` and `Authority.Roster.Classify` in `Finalization_Decide`; `V.P.Decide`, `T.R.Decide` and `Raw_Roster.Old.Classify` in `Completion_Decide`; `V2.P.Decide` in `Pending_Decide_V2`; `CA.Roster.Classify` in `Completion_Metadata_Matches`.<br>MQ3 transport-qualified paths: `Pending_Transport.E.Decide` in `Pending_Decide_V1`; `Completion_Transport.P.Decide` in `Completion_Decide`; `Finalization_Transport.K.Decide_Value` in `Finalization_Decide_Mixed`; `Finalization_Transport.F.P.Decide` in `Pending_Decide_V2`.<br>MQ4 `Worldline.C_API.Pending_Transport.E.Decide` and `C_API.Finalization_Transport.F.P.Decide` in `Pending_Decide_V1`.<br>MQ5 one `Worldline.Recovery_C_API.Present` of `Recovery_Select` rewritten as `Recovery_C_API.Present`.<br>MQ6 `Evaluation_Pending_C.Decide_Value` of `Pending_Decide_V1` rewritten as `Standard.Evaluation_Pending_C.Decide_Value`.<br>MQ7 (body only, RESIDUAL; R-RES refuses too) `T.P.Decide`, `A.Roster.Classify` and `K.A.T.R.Decide` added to `Decide_Raw_Context`.<br>MQ8 library-unit paths: `Evaluation_Completion.P.Decide`, `Worldline.Evaluation_Authority.Roster.Classify`, `Evaluation_Pending_V2.P.Decide` and `Evaluation_Completion_C.A.Roster.Classify` in `Completion_Decide`.<br>MQ9 non-name prefix: `Request_Pointers.To_Pointer (Input).all.Header_Valid` in `Pending_Decide_V1`.<br>MQ10 attribute: `Evaluation_Pending_C.Decide_Value'Address` in `Pending_Decide_V1`.<br>MQ11 capture: declare `Evaluation_Pending_C : constant Integer := 0;` in `Pending_Decide_V1`; add `package Evaluation_Pending renames Evaluation_Pending_V2;` to `Pending_Transport`'s specification.<br>MQ12 removed routine: `Completion_Transport.Context_Matches` of `Finalization_Decide_Mixed` rewritten as `Evaluation_Completion_C.Context_Matches`.<br>MQ13 exception out of its scope: `Completion_Transport.Context_Matches` called from `Completion_Decide`.<br>MQ14 capture through the context clause: `with Worldline.Evaluation_Pending;` added to the C_API body's context (body only). |
| R-W | Carried from v4: Write `O.Value` before the gate. Add a third assignment to finalization `O`. Assign `Response` directly. Pass `Detail_Arena` to a second procedure. Store `Encode_Decision` of a value other than the `P.Admit` result. Add an unlisted `.all :=` anywhere in a designed scope, including a scope that has no rows, such as a transport body. Add a `Write_Data (` call to `Resources_Can_Reserve`. |
| R-GATE | Carried from v4: Select `D.Item` before `if not D.Ok`. Test `D.Ok` twice. Replace the discriminant test with a `case` on another object. Add a new acceptance object with an `.Ok` test but no gate row (completeness). **New, branch-sensitive** *(sim)*:<br>MG1 (body and amendment) `Diagnostic_Transport.Value ("completion.context.field-rejected", FA.Rejected_Position);` added immediately after G16a's `end if;` (a `False` component on the accepted path).<br>MG2 (amendment) G16a's diagnostic reads `FA.Expected` instead of `FA.Rejected_Position` (a `True` component in the rejection branch).<br>MG3 (amendment) G06's rejection branch becomes `null;` without `return`.<br>MG4 (amendment) G19a selects `D.Item` between `begin` and `if not D.Ok`.<br>MG5 (amendment) G19a tests `D.Ok` a second time after the gate.<br>MG6 (amendment) `D` passed whole after G19a's gate.<br>MG7 (amendment) `RA.Row` read in the `Row_Rejected` alternative.<br>MG8 (amendment) `RA.Rejected_Field_Position` read in the `Row_Accepted` alternative.<br>MG9 (amendment) `RA.Joined` read after `end case;`.<br>MG10 (amendment) `when others => return 255;` added to G16b's case statement.<br>MG11 (amendment) a new `Z : constant Evaluation_Pending_C.Row_Acceptance := …;` used as `Z.Item`, with no gate row and no test (completeness by declaration).<br>MG12 (amendment) an `X.Verdict` selection of an object with no gate row (completeness by selection). |
| WF-X (R-GATE `wfx`) | *(sim)*:<br>MX1 (amendment) a third assignment `O := Evaluation_Finalization_C.Decide_No_Rows_Value (X, A, Required);` before the region.<br>MX2 (amendment) an `elsif` branch added to the region.<br>MX3 (amendment) `O` declared with an initializer.<br>MX4 (amendment) `O.Ok` read at the start of the then branch.<br>MX5 (amendment) `O.Value` selected before the region.<br>MX6 (amendment) a statement between the region's `end if;` and the test.<br>MX7 (body) the two assignments swapped.<br>MX8 (amendment) the else-assignment moved after `end if;` (`else null; end if; O := …;`). |
| R-RES, R-GLUE, R-LAYOUT | Carried from v4: Edit a value decision in `Authority_Glue`. Apply GE5 but keep the old `K.Metadata_Base` call. Keep `package K renames …` at `:836` after PK-6b. Place a transport inside `Authority_Glue`. Place an export before the owner code. Reorder the spec additions. Edit any owner export. |
| K3, K5, G9 | Carried from v4: Remove `"evaluation_pending"` from `Library_Interface` while keeping `Library_Name "evaluation_pending"`; this was v3's false pass. Add `for Interfaces use (…)`. Duplicate a unit. Reorder the list. Add `& Extra` or an `external` reference. Change `Library_Standalone`. Remove a core interface unit. |
| K6 | Carried from v4: Change one character of the component transport relative to the core transport. |

<!-- A-BIND-V5-END -->
