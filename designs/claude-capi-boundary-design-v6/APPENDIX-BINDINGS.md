# C-API boundary consolidation v6: Appendix A-BIND (enforceable binding specification, delta over v5)

| | |
|---|---|
| Companion to | `DESIGN.md` in this directory (design v6). `§n` means a section of the v6 design, that is DESIGN.md v6 with the v5, v4 and v3 slices it carries. |
| Supersedes | v5 `APPENDIX-BINDINGS.md` (sha256 `f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2`, 94352 bytes). It is read only and unchanged (re-hashed while drafting). |
| Status | DRAFT_FOR_GPT61_REVIEW. **PROPOSAL ONLY.** No manifest code, table, source or control has been written, and no check has been run on any source tree. Every obligation is OPEN. |
| Base | S5 = `W/work/claude-composition-v5-beta/source` (lineage L0), unchanged. Line citations are S5 lines. |
| Normal form | N1 and N2 exactly as v4 (carried). |
| Answers | The sealed actual gpt-6.1-sol review of v5 (`…/claude-capi-boundary-design-v5/review/gpt61-v1/`): **V5-RC4-GATE-EXCEPTION** and **V5-RC4-QUAL-CAPTURE**. V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 stay NOT_CLOSED until a review rules otherwise. |
| **What this appendix consists of** | A-BIND v6 is (1) the text of this file, plus (2) the v5 A-BIND line ranges listed in §W.2 as CARRIED_VERBATIM or CARRIED_WITH_LINE_REPLACEMENTS. Each range is bound by the sha256 of its exact bytes (the lines, each followed by `\n`). The replacements and insertions of §W.3 are applied to them, and the code changes CR1–CR6 of B8.4 are applied to the v5 code. Through the carried v5 §V, the v4 A-BIND slices that v5 carries are carried too, exactly as v5 binds them. No other v5 or v4 text is part of A-BIND v6. |

Nothing in this appendix is evidence. A check that passes is a necessary guard. It is never proof of reachability, of faithful actuals beyond the bound text, of native behaviour, of custody or of correctness (§8.9).

---

## W. What changed from v5, and how v5 text is carried

### W.1 Summary

- **The sole WF-X exception is an invariant of its own (V5-RC4-GATE-EXCEPTION).** A new constant, `CAPI_WFX_PROTOCOL`, is part of the PK-1 check text and is never updated. It states the exception's identity (`Finalization_Decide`, `G21c`, `O`), its declaration (and with it the declared type), the sha256 of its exact region, its two assignments and its test. R-GATE compares the tables with this constant, not with a tile or with another table that an amendment could change in step:
  - before PK-6b, `CAPI_GATE_EXCLUSIVE` is empty and no gate row has kind `wfx`;
  - from PK-6b, `G21c` is the only key of `CAPI_GATE_EXCLUSIVE`, `(Finalization_Decide, G21c, O)` is the only `wfx` row, and its exclusive entry and gate text equal the protocol.

  This is CR2, CR5 and CR6 (B8.4), with B0.7 (W-A1, W-A2), B1.1 (W-A9), B10.3 (W-A15), B11 rows 14 and 43, and the B12 WF-X roster controls (W-A20).
- **R-QUAL (d) examines every mentioned unit and the parent specification (V5-RC4-QUAL-CAPTURE).** A with clause mentions its named unit and every prefix of that unit's name (RM 10.1.2(6/2)). (d) now refuses a with clause in which any mentioned prefix `I0.….Ij` with j ≥ 1 ends in a root. So `with Worldline.Evaluation_Pending.Child;` is refused through its ancestor `Worldline.Evaluation_Pending`, which v5's test of the last identifier missed. (d) also applies to the specification of the parent `Worldline` (`core/worldline.ads`), whose declarations and clauses reach the pair. It refuses a with clause that mentions a unit named by a listed simple name, and it refuses subunits. The scoped exceptions and the use-clause inventory are unchanged. This is CR3 and CR4 (B8.4), with B0.10 (W-A3–W-A8), B8.2, B8.3, B9.4.7 (W-A14), B11 rows 42 and 44, and the B12 capture controls (W-A19).
- **Latent v5 defects L13–L15**, found while drafting (DESIGN §A.3), are repaired by the same rules. L16, a wording defect in DESIGN §19 relayed from the parallel seam lane, is corrected in DESIGN §B-v6.4; (d1), R-INV (ii) and R-RES already cover declarations nested inside package bodies (W-A4, W-A8, MQ24).
- **Unchanged:** every tile, transport content, helper hash, clause tuple, residual hash, gate text, branch list, write row, diagnostic site sequence and refusal code; `CAPI_QUALIFIED`, `CAPI_QUALIFIER_EXCEPTIONS`, `CAPI_INVENTORY` and `CAPI_USE_PACKAGES`; and every v5 mutation control. No refusal is removed. The author simulation found no problem on the S5 texts and the designed texts at PK-1, PK-5, PK-6b and PK-7 (AUTHOR-NOTES §4).

### W.2 Disposition of every v5 A-BIND section

"v5 lines" are 1-based lines of the v5 file. The sha256 is that of the UTF-8 bytes of those lines, each followed by `\n` (observed by a read-only script).

| v5 section | v5 lines | sha256 of the v5 slice | Disposition |
|---|---|---|---|
| Header | 1-15 | — | REPLACED (header above, §W.1) |
| §V How v5 carries v4 (V.1–V.4 and the v4 slice table) | 17-81 | `cc2e66b1123883484777c5ae344c3c9cbecc27c63284608bb50fd07cb577afca` | CARRIED_VERBATIM. It binds the v4 slices that v5 carries. |
| B0 heading, B0.1–B0.6 | 85-112 | `c1997b91b05d2d4e94897d433780f8fa03927d3a217b7a6ca87cc9a839c1962b` | CARRIED_VERBATIM |
| B0.7 Gates (R-GATE) | 114-177 | `3bbe54bb2fbca4c5af64619066c482f3cdd14c09703b57967af14cb54c8e4302` | CARRIED_WITH_LINE_REPLACEMENTS (W-A1 v5:158, W-A2 v5:177) |
| B0.8, B0.9 | 179-181 | `022663b6551574958e528e9dd7092babc22a83e85188ecc6e78ceef845aa5430` | CARRIED_VERBATIM |
| B0.10 Fully expanded names (R-QUAL) | 183-234 | `5a0488a3f44e16c865149e0dedc225891e665ff3f0b61eb677dba6da4324fc42` | CARRIED_WITH_LINE_REPLACEMENTS (W-A3 v5:198, W-A4 v5:202-205, W-A5 v5:210, W-A6 v5:220, W-A7 v5:224, W-A8 after v5:229) |
| B1.1 Stage additions of the B8 tables | 238-250 | `2e1886e3b7a045daa50a20e027f1d87e8f7f63ce530a97e2663016f71026555e` | CARRIED_WITH_LINE_REPLACEMENTS (W-A9 after v5:250) |
| B8 heading and B8.0 | 254-270 | `096ea57f1ecaf03b46de1cd9e4e5258940af16e069ec6d416f7ed4736e376458` | CARRIED_WITH_LINE_REPLACEMENTS (W-A10 after v5:270) |
| B8.1 Code replacements BR1–BR8 | 272-557 | `206f07392321e24c330914cabe7028a884951f3cbc68e079a2fedeb5edb6e98d` | CARRIED_VERBATIM. The v6 code changes are in B8.4. |
| B8.2 Check-to-rule map | 559-575 | `7a1d60eb1d926b2f725bc09f74ffbf802f46056ee0f2857a592c74f250658d07` | CARRIED_WITH_LINE_REPLACEMENTS (W-A11 v5:571, W-A12 v5:573) |
| B8.3 Notes on the sketch | 577-587 | `3c4bf4f47fd96907301a61f039b948098195c6641edb520ed8056362ef13c728` | CARRIED_WITH_LINE_REPLACEMENTS (W-A13 v5:582-584) |
| (none) | — | — | NEW: B8.4 Code changes CR1–CR6 |
| B9.4 SPARK units, full expanded names and alias exclusion | 591-715 | `2ddae1af85bbdc2696effec550c12c21e5e8a7e63c49a3e9b0349cfdbdcbda90` | CARRIED_WITH_LINE_REPLACEMENTS (W-A14 after v5:715: B9.4.7) |
| B10.3 Gates | 719-790 | `9c269d9894c16bccdbcd8621c5a961f06873043fb1e3d00886529583b3c51f6a` | CARRIED_WITH_LINE_REPLACEMENTS (W-A15 after v5:776) |
| B11 Promise-to-check matrix | 794-841 | `0d7daa6243f99a1c477f13a80d69fa417b1ffb7e97d1e1c49bebd51b242bcc22` | CARRIED_WITH_LINE_REPLACEMENTS (W-A16 v5:796, W-A17 v5:813, W-A18 v5:841) |
| B12 Mutation controls | 845-868 | `b63258f1af0e4ab182b7fc9c34f15a4267540458f0707c351716ce39ac11604d` | CARRIED_WITH_LINE_REPLACEMENTS (W-A19 after v5:862, W-A20 after v5:865) |
| Section separators and the v5 end marker | 83, 236, 252, 589, 717, 792, 843, 870 | — | not carried (layout only) |

### W.3 Line replacements and insertions in carried v5 slices

Each replacement quotes the exact v5 lines after `v5:` and gives the v6 lines that replace them after `v6:`. Each insertion names the v5 line it follows, which is unchanged, and gives the inserted lines after `v6 (inserted):`. Nothing else in a slice changes.

**W-A1 (v5:158, replaced; B0.7 kind `wfx`; V5-RC4-GATE-EXCEPTION).**
```text
v5:
- This is the only exception to "an acceptance object is never assigned". R-W row W21 binds the same two assignments by its count (B10.2), and R-TILE fixes the text (segment 6).
v6:
- This is the only exception to "an acceptance object is never assigned". R-W row W21 binds the same two assignments by its count (B10.2), and R-TILE fixes the text (segment 6).
- **The exception is an invariant of its own (v6; V5-RC4-GATE-EXCEPTION).** `CAPI_WFX_PROTOCOL` (B10.3) is part of the PK-1 check text and is never updated. It fixes the exception's identity, its declaration, the sha256 of its region, its two assignments and its test. R-GATE compares the tables with this constant, not with a tile or with another table:
  - **Before PK-6b**, that is while `Finalization_Decide` is not in `CAPI_LAYOUT_EXPORTS`, `CAPI_GATE_EXCLUSIVE` is empty and no row of `CAPI_GATES` has kind `wfx`.
  - **From PK-6b**, `CAPI_GATE_EXCLUSIVE` has exactly one key, `G21c`, and exactly one row of `CAPI_GATES` has kind `wfx`: the row `G21c` for the object `O` under the scope key `Finalization_Decide`.
  - That entry's declaration equals the protocol's, so the declared type is `Evaluation_Finalization_C.Decide_Acceptance` and there is no initializer. The sha256 of its region equals the protocol's, and so do its then- and else-assignments. The row's gate text equals `<then-assignment> else <else-assignment> end if; if not O.Ok then return 255; end if;`.
  - The row check also refuses a `wfx` row whose row id or object is not the protocol's (CR5).
  - So the following are refused even when the tile, `CAPI_GATES` and `CAPI_GATE_EXCLUSIVE` are amended to match one another: an added exception; a relabelled one (another row id or object); a moved one (another scope); one staged before PK-6b; and a changed declaration, region, assignment or test (B12, the WF-X roster controls).
  - The stage is read from `CAPI_LAYOUT_EXPORTS`, which R-LAYOUT and R-RES bind to the body: the relocated exports must form one contiguous run in that order (B0.8). A misstated stage can only demand the exception where its scope does not exist, or forbid it where `O` is declared and tested; a problem is reported either way. At every stage the exception's content is compared with the constant, so a misstated stage cannot admit a second or a changed exception.
```

**W-A2 (v5:177, replaced; B0.7).**
```text
v5:
- Both v4 statements are withdrawn. The v5 rule is stated once, here. It is implemented by `_capi_gate_problems` with `_capi_gate_row_problems` and `_capi_exclusive` (B8), tabulated in B10.3, promised in B11 rows 7, 14 and 41, and exercised by the R-GATE and WF-X mutations of B12.
v6:
- Both v4 statements are withdrawn. The v5 rule is stated once, here, with the v6 protocol invariant above. It is implemented by `_capi_gate_problems` with `_capi_gate_row_problems` and `_capi_exclusive` (B8), and by CR5 and CR6 (B8.4). It is tabulated in B10.3 with `CAPI_WFX_PROTOCOL`, promised in B11 rows 7, 14, 41 and 43, and exercised by the R-GATE, WF-X and WF-X roster mutations of B12.
```

**W-A3 (v5:198, replaced; B0.10).**
```text
v5:
**Requirements.** They apply to the whole C_API specification and the whole C_API body, context clause included.
v6:
**Requirements.** They apply to the whole C_API specification and the whole C_API body, context clause included. (d) also applies to the specification of the parent `Worldline`, `core/worldline.ads` (v6).
```

**W-A4 (v5:202-205, replaced; B0.10 (d); V5-RC4-QUAL-CAPTURE).**
```text
v5:
- **(d) No capture of a full expanded name.** The nine first identifiers of the full expanded names are `Worldline`, `Resource_Run_Ledger_C_API`, `Evaluation_Completion_C`, `Evaluation_Completion_Roster`, `Evaluation_Finalization_C`, `Evaluation_Pending_C`, `Evaluation_Pending`, `Evaluation_Pending_V2_C` and `Evaluation_Pending_V2` (B9.4). The context clause is the text before the first `package`.
  - Outside the context clause, these identifiers occur only in two ways: as the first identifier of a dotted name, or as the target of a package renaming (`renames <root>;`).
  - In the context clause, no `with` clause names a dotted unit whose last identifier is one of them. Such a unit, for example a child `Worldline.Evaluation_Pending`, would be directly visible by that identifier inside `Worldline.C_API` and would hide the library unit.
  - So no declaration in the C_API pair, and no unit the pair names in a `with` clause, can make a full expanded name denote anything other than its library unit's routine. The declarations excluded include an object, parameter, package, subprogram, type, loop parameter, enumeration literal or renaming of that name.
v6:
- **(d) No capture of a full expanded name (REVISED in v6; V5-RC4-QUAL-CAPTURE).** The nine first identifiers of the full expanded names, the *roots*, are `Worldline`, `Resource_Run_Ledger_C_API`, `Evaluation_Completion_C`, `Evaluation_Completion_Roster`, `Evaluation_Finalization_C`, `Evaluation_Pending_C`, `Evaluation_Pending`, `Evaluation_Pending_V2_C` and `Evaluation_Pending_V2` (B9.4). (d) is checked on N2 of three compilation units: the C_API specification, the C_API body, and the specification of their parent `Worldline`, `core/worldline.ads` (`CAPI_PARENT_SPEC`). A unit's context clause is its text before its first `package`. If a unit's text has no `package`, (d) reports a problem.
  - **(d1) Declarations.** Outside the context clause, a root occurs only as the first identifier of a dotted name, or as the target of a package renaming (`renames <root>;`). In the parent specification, `Worldline` may also occur as the unit's own name: right after its first `package`, and in its final `end Worldline;`. (d1) scans the unit's whole text, so it holds at every nesting depth: a declaration inside a nested package specification or body (such as the root-worker draft's `Child_Boundary`), a subprogram or a block is covered as well as one at body level.
  - **(d2) Every mentioned unit.** A with clause, with or without `limited` or `private`, that names `I0.I1.….Ik` mentions every prefix `I0.….Ij` (0 ≤ j ≤ k): the named unit and each ancestor it is denoted through. For every such prefix, `Ij` is not a root when j ≥ 1, and `Ij` is not a listed simple name for any j. So `with Worldline.Evaluation_Pending;` (refused in v5 too) and `with Worldline.Evaluation_Pending.Child;` (v6: the capturing unit is mentioned only as a prefix) are both refused. So is a with clause of a library unit named like a routine, for example `with Decide_Value;`.
  - **(d3) The parent specification** also contains no use clause and no identifier equal to a listed simple name.
  - **(d4) No subunit.** None of the three units contains the reserved word `separate`. So no body stub moves text of the pair into a subunit, whose own context clause and declarations (d) would not examine.
  - (d) refuses by text. It resolves no name, and it refuses a mentioned unit whether or not that unit exists. The scoped exceptions of (a) (`CAPI_QUALIFIER_EXCEPTIONS`) and the use-clause inventory of R-INV (vii) (`CAPI_INVENTORY`, `CAPI_USE_PACKAGES`) are unchanged.
  - **Why these are the places to look.** This is the author's reading of RM 10.1.2(5), (6/2) and (7), RM 10.1.1(11) and RM 8.3(8). No RM text is installed locally, and installed name resolution stays OPEN (D-38).
    - A library unit is visible only within the scope of a with clause that mentions it, as the named unit or as a prefix of it.
    - A child of `Worldline` lies within `Worldline`'s declarative region, and so does the pair. Once such a child is visible, it is directly visible inside the pair by its own identifier. As an inner homograph it hides a library unit of the same name, such as the root `Evaluation_Pending`.
    - The scope of a with clause on a library unit declaration is the declaration's whole declarative region, which includes its children. So the parent specification's with clauses reach the pair, and so do its declarations and, as the author reads RM 8.4, its use clauses.
    - A library unit named like a routine, for example a library-level renaming, would let the pair call that routine by its simple name once a with clause makes the unit visible.
    - A subunit has its own context clause.
  - So no declaration in the C_API pair or in its parent specification, and no unit that a with clause of any of the three units mentions, can make a full expanded name denote anything other than its library unit's routine. The declarations excluded include an object, parameter, package, subprogram, type, loop parameter, enumeration literal or renaming of that name.
```

**W-A5 (v5:210, replaced; B0.10, the closure argument, way 1).**
```text
v5:
   - By (d), the full expanded name denotes `R`'s library unit.
v6:
   - By (d), the first identifier of the full expanded name denotes the library unit of that name, and nothing hides it: no declaration in the pair or in its parent specification, no unit that a with clause of either mentions, and no subunit (v6; "Capture vectors considered", below). So the full expanded name denotes `R`.
```

**W-A6 (v5:220, replaced; B0.10, way 3).**
```text
v5:
   - R-INV (vii) admits no use clause except `use <unit transport>;` and `use System.Storage_Elements;`.
v6:
   - R-INV (vii) admits no use clause in the pair except `use <unit transport>;` and `use System.Storage_Elements;`. (d3) admits none in the parent specification, whose use clauses would otherwise reach the pair (v6).
```

**W-A7 (v5:224, replaced; B0.10, way 4).**
```text
v5:
4. **By its simple name alone, through a declaration in the C_API pair** (a renaming or instance). Refused by R-INV (v), R-TRANS and R-TILE.
v6:
4. **By its simple name alone, through a declaration in the C_API pair** (a renaming or instance). Refused by R-INV (v), R-TRANS and R-TILE. **Or through a declaration in the parent specification, or through a library unit that a with clause mentions** (for example a library-level renaming named `Decide_Value`). Refused by (d2) and (d3) (v6).
```

**W-A8 (inserted after v5:229, `- R-QUAL never resolves names. It compares texts.`; B0.10).**
```text
v6 (inserted):

**Capture vectors considered (v6; V5-RC4-QUAL-CAPTURE, L13–L15).** A full expanded name can be captured only by a declaration of its first identifier that is visible in the pair and hides the library unit. A routine can be denoted by its simple name only through a visible declaration of that name. The places such a declaration can come from, and the rule that refuses each, are:

| # | Source of a visible declaration | Refused by | S5 (observed by a read-only script; B9.4.7) |
|---|---|---|---|
| 1 | A declaration in the C_API pair, at any nesting depth: at body level, or inside a nested package specification or body (such as the root-worker draft's `Child_Boundary`), a subprogram or a block | (d1) on the pair (v5), which scans the unit's whole text; for a routine's simple name, R-INV (v), R-TRANS and R-TILE; for a package renaming outside the designed scopes, also R-INV (ii) (each clause belongs to its innermost scope, and text outside the designed scopes is RESIDUAL) and R-RES (MQ24) | none |
| 2 | A declaration in the parent specification, visible throughout `Worldline`'s declarative region, which includes the pair (L13) | (d1) and (d3) on the parent specification (v6) | `Hash` and `Zero_Hash` only (`core/worldline.ads:5-7`) |
| 3 | A unit that a with clause of the C_API specification or body mentions, as the named unit or as a prefix (V5-RC4-QUAL-CAPTURE) | (d2) on the pair (v6; v5 tested only the last identifier of the named unit) | the specification's 4 with clauses mention 5 units, and the body's 23 mention 26; none is refused |
| 4 | A unit that a with clause of the parent specification mentions; such a clause has scope over the pair (L13) | (d2) on the parent specification (v6) | `with Attest.SHA256;` mentions `Attest` and `Attest.SHA256`; neither is refused |
| 5 | A library unit named by a listed simple name, mentioned by a with clause of any of the three units (L14) | (d2) (v6) | none |
| 6 | A use clause | in the pair, R-INV (vii) (v5, unchanged); in the parent specification, (d3) (v6, L13) | the pair holds only the B9.1 and B9.2 use clauses; the parent specification holds none |
| 7 | A subunit, whose own context clause and declarations lie outside the three units (L15) | (d4) (v6) | the word `separate` occurs in none of the 223 S5 Ada source files |
| 8 | The enclosing declarative regions | Between `Standard` and the pair there is only `Worldline` (row 2). `Standard` declares none of the roots or listed simple names (author's reading of RM A.1). | — |

These are the author's readings of the RM clauses cited in (d). The RM text is authoritative and is not installed locally. The installed skills ground the terms used: "named" and "mentioned" (`ada-2005-amendment` ch08, line 44, RM 10.1.2); a child's automatic visibility of its parent's specification, and its need of a with clause for siblings and children (`advanced-ada` ch14, line 53); and homographs (`ada-2005-amendment` ch06, line 26, RM 8.3). Installed integrated name and overload resolution, including child-unit capture, remains OPEN (D-38).
```

**W-A9 (inserted after v5:250, the paragraph `Before PK-6b the residual calls …`; B1.1).**
```text
v6 (inserted):

**v6 additions (V5-RC4-GATE-EXCEPTION, V5-RC4-QUAL-CAPTURE).**
- `CAPI_WFX_PROTOCOL` and `CAPI_PARENT_SPEC` (CR2) are part of the PK-1 check text. They are not staged tables: no stage appends to them or reassigns them. A reassignment that extended `CAPI_WFX_PROTOCOL` would make its unpacking in CR6 fail, and `export_problems` reports a check that cannot run as a problem (fail closed).
- At PK-1 … PK-5, `CAPI_GATE_EXCLUSIVE` stays empty and no `CAPI_GATES` row has kind `wfx`. The PK-6b `.update` adds exactly the entry `G21c`, equal to `CAPI_WFX_PROTOCOL`, and no later stage adds a key (B0.7, CR6).
```

**W-A10 (inserted after v5:270, `- **One check function per rule.** …`; B8.0).**
```text
v6 (inserted):
- **v6 (B8.4).** The v6 code is the v5 code with CR1–CR6 applied by v5 code line number. CR4 replaces the with-clause and declaration part of BR6's R-QUAL (d) by the helper `_capi_capture` (CR3), which it applies to the C_API specification, the C_API body and the parent specification. CR5 and CR6 add the WF-X protocol check to BR7's `_capi_gate_row_problems` and `_capi_gate_problems`. Every v5 code line that CR1–CR6 do not name is unchanged. The reconstructed v6 code block is given by sha256 in AUTHOR-NOTES.md, which also lists how it was checked.
- **v6 author simulation** (a self-check, not a review and not evidence). The method above was repeated with the v6 code, with the parent specification added to the in-memory texts. It ran on four assembled successor texts, PK-1, PK-5, PK-6b and PK-7, each with its staged tables, and on every mutation of B12, old and new, that is marked *(sim)*. Its results are in AUTHOR-NOTES.md §4.
```

**W-A11 (v5:571, replaced; B8.2).**
```text
v5:
| `_capi_qualifier_problems` (with `_capi_qualified`) | **R-QUAL** (a)–(d) (B0.10) | new (V4-RC4-ALIAS) |
v6:
| `_capi_qualifier_problems` (with `_capi_qualified` and `_capi_capture`) | **R-QUAL** (a)–(d) (B0.10); (d) on the C_API specification, the C_API body and the parent specification (`CAPI_PARENT_SPEC`) | new in v5 (V4-RC4-ALIAS); (d) extended in v6 to every mentioned unit, the parent specification and subunits (CR3, CR4; V5-RC4-QUAL-CAPTURE; L13–L15) |
```

**W-A12 (v5:573, replaced; B8.2).**
```text
v5:
| `_capi_gate_problems` (with `_capi_gate_row_problems` and `_capi_exclusive`) | **R-GATE** (B0.7): the exact gate form per kind; the discriminant once, inside the gate; branch-sensitive component places; the sole WF-X exception; completeness by discriminant selection and by `_Acceptance` declaration | replaces v4's after-test rule and its listed assigned-object exemption (V4-RC4-GATE; L10, L12) |
v6:
| `_capi_gate_problems` (with `_capi_gate_row_problems` and `_capi_exclusive`) | **R-GATE** (B0.7): the exact gate form per kind; the discriminant once, inside the gate; branch-sensitive component places; the sole WF-X exception, whose identity, staging and content equal the fixed `CAPI_WFX_PROTOCOL`; completeness by discriminant selection and by `_Acceptance` declaration | replaces v4's after-test rule and its listed assigned-object exemption (V4-RC4-GATE; L10, L12); v6 adds the row identity (CR5) and the roster and protocol check (CR6) (V5-RC4-GATE-EXCEPTION) |
```

**W-A13 (v5:582-584, replaced; B8.3).**
```text
v5:
  - R-QUAL and R-GATE also validate their own table entries. Each listed qualified text must be a full expanded name or an exception listed for its scope, and each gate text must have its kind's form.
  - So an amendment that adds an indirect spelling, or a gate that is not branch-correct, to both the tile and the table is still refused (B12, the mutations marked *amendment*).
- **R-QUAL compares texts and never resolves names.** A path that happens to denote an Appendix C routine is refused because its text is not a full expanded name. Rule (d) makes each full expanded name denote its library unit.
v6:
  - R-QUAL and R-GATE also validate their own table entries. Each listed qualified text must be a full expanded name or an exception listed for its scope, and each gate text must have its kind's form. The WF-X exception's identity, staging, declaration, region, assignments and test must equal the fixed `CAPI_WFX_PROTOCOL` (v6; CR5, CR6), which no stage amends.
  - So an amendment that adds an indirect spelling, a gate that is not branch-correct, or an added, relabelled, moved or altered WF-X exception, to both the tile and the tables is still refused (B12, the mutations marked *amendment*).
- **R-QUAL compares texts and never resolves names.** A path that happens to denote an Appendix C routine is refused because its text is not a full expanded name. Rule (d) makes each full expanded name denote its library unit. In v6 it examines the C_API pair and its parent specification, every unit that their with clauses mention as a named unit or as a prefix, and subunits. It refuses a mentioned unit by its text, whether or not that unit exists.
```

**W-A14 (inserted after v5:715, the last line of B9.4.6; new B9.4.7).**
```text
v6 (inserted):

### B9.4.7 Context clauses and the parent specification (NEW in v6; R-QUAL (d))

Observed by a read-only script on N2 of the S5 files. A unit's mentioned units are its named units and every prefix of their names.

| Unit | With clauses | Named units | Mentioned units | Refused by (d2) |
|---|---|---|---|---|
| C_API specification, `core/worldline-c_api.ads` | 4 | 4 | 5 | none |
| C_API body, `core/worldline-c_api.adb` | 23 | 23 | 26 | none |
| Parent specification, `core/worldline.ads` (sha256 `6b171d3fa0b9a0cdbd7e3777e4af35e557ed74e67f6b3ee9bdc1bbfe41305286`, 164 bytes) | 1 | 1 | 2 | none |

- **The parent specification** (`core/worldline.ads:1-9`) is `with Attest.SHA256;` (`:1`), then `package Worldline with SPARK_Mode is` (`:3`), declaring `subtype Hash is Attest.SHA256.Digest;` (`:5`) and `Zero_Hash : constant Hash := [others => 0];` (`:7`), then `end Worldline;` (`:9`). Its only root is its own name, at `:3` and `:9`. It has no use clause and no identifier equal to a listed simple name. So (d1)–(d4) report nothing for it.
- **The S5 tree.** There are 223 Ada source files (`*.ads`, `*.adb`, recursively). On their N2 texts:
  - none contains the word `separate`;
  - their 123 distinct unit names (the name after the first `package`, `package body`, `procedure` or `function`) include no root as a component at position 1 or later, and no listed simple name as any component;
  - their with clauses name 83 distinct units, none of which (d2) refuses.
- **Context additions of later stages.** v4 DESIGN line 343 states that the C_API body's context gains `with Ada.Text_IO;` and `with Ada.Exceptions;` (PK-6b) and with clauses for the SPARK units its new code names, bound by the C_API pin and the packet review. All 17 `CAPI_SPARK_UNITS` are among the S5 unit names above, so (d2) admits their with clauses, and it admits the two `Ada` clauses (B12 positive control).
- R-RES hashes the C_API body from `CAPI_BODY_HEAD` (`_capi_residual_problems`, unchanged since v4), and R-INV (iii) covers only use clauses, renamings and pragmas in the context. So (d) is the only text rule on the with clauses of the C_API body, as it was in v5, and on those of the parent specification. The with clauses of the C_API specification are also bound by S-RES, which binds the whole specification outside its designed additions.
```

**W-A15 (inserted after v5:776, the else-assignment line of `CAPI_GATE_EXCLUSIVE`; B10.3).**
```text
v6 (inserted):

**`CAPI_WFX_PROTOCOL`** (NEW in v6; V5-RC4-GATE-EXCEPTION; CR2). The normative G21c protocol. It is fixed at PK-1 in the check text, and no stage updates it. It is a tuple of eight texts:
1. the scope key `Finalization_Decide`;
2. the row id `G21c`;
3. the object `O`;
4. the declaration `O : Evaluation_Finalization_C.Decide_Acceptance;`: the declared type is `Evaluation_Finalization_C.Decide_Acceptance`, with no initializer;
5. the region sha256 `34b1492a5b5a757dab0cd1c62fcc241155be318e42a728da6649387d62c5b4d0`, which is the sha256 of the UTF-8 bytes of the exact N1 region above (644 bytes; observed by a read-only script from B4.20 segment 6 without its final ` if not O.Ok then return 255; end if;`);
6. the then-assignment, as above;
7. the else-assignment, as above;
8. the test `if not O.Ok then return 255; end if;`.

The G21c gate text in the table above is item 6, ` else `, item 7, ` end if; ` and item 8, joined. R-GATE checks the tables against the tuple at every stage (B0.7 as amended by W-A1; CR5, CR6):
- while `Finalization_Decide` is not in `CAPI_LAYOUT_EXPORTS` (before PK-6b): `CAPI_GATE_EXCLUSIVE` is empty and no row has kind `wfx`;
- otherwise (PK-6b, PK-7): `CAPI_GATE_EXCLUSIVE` has the one key `G21c`, whose entry is item 4, a region whose sha256 is item 5, item 6 and item 7; and the only `wfx` row is the row `G21c` for `O` under the key `Finalization_Decide`, with the gate text above.

The components of G21c (T: `Value`; F: none) remain an ordinary R-GATE branch list, as for every row; they are not part of the exception.
```

**W-A16 (v5:796, replaced; B11).**
```text
v5:
"Text" means a manifest check in B8. "Evidence" means an obligation that no text check can close; it is listed so that no promise is silently assumed to be enforced. Rows 1–40 are v4's, with rows 7, 10, 14 and 24 restated. Rows 41 and 42 are new, giving 42 rows (J68).
v6:
"Text" means a manifest check in B8. "Evidence" means an obligation that no text check can close; it is listed so that no promise is silently assumed to be enforced. Rows 1–40 are v4's, with rows 7, 10, 14 and 24 restated in v5. Rows 41 and 42 are v5's. In v6, rows 14 and 42 are restated again, and rows 43 and 44 are new, giving 44 rows (J69).
```

**W-A17 (v5:813, replaced; B11 row 14).**
```text
v5:
| 14 | Finalization `O` assigned on exactly two exclusive paths, before its single test (§5.1) | R-GATE `wfx` (G21c: the exact declaration without initializer, region, then- and else-assignments and test; `_capi_exclusive`; exactly two assignments at those places), R-W WF-X (count 2) and R-TILE (segment 6 = §5.1 text) | Text |
v6:
| 14 | Finalization `O` assigned on exactly two exclusive paths, before its single test (§5.1); it is the only assigned acceptance object at every stage | R-GATE `wfx` (G21c: the exact declaration without initializer, region, then- and else-assignments and test; `_capi_exclusive`; exactly two assignments at those places), checked against the fixed `CAPI_WFX_PROTOCOL` (CR5, CR6; row 43), R-W WF-X (count 2) and R-TILE (segment 6 = §5.1 text) | Text |
```

**W-A18 (v5:841, replaced; B11 row 42 restated, rows 43 and 44 added).**
```text
v5:
| 42 | Every remaining denotation of an Appendix C or removed routine in the C_API pair is its full expanded name. Indirect, transport-qualified, `C_API`-qualified, parent-shortened and `Standard`-prefixed spellings are refused (V4-RC4-ALIAS). | R-QUAL (a)–(d) with R-INV (v) and (vii); the B9.4.5 inventory is documentation | Text (static; installed resolution OPEN, D-38) |
v6:
| 42 | Every remaining denotation of an Appendix C or removed routine in the C_API pair is its full expanded name. Indirect, transport-qualified, `C_API`-qualified, parent-shortened and `Standard`-prefixed spellings are refused (V4-RC4-ALIAS). | R-QUAL (a)–(d) with R-INV (v) and (vii), with (d) as revised in v6 (row 44); the B9.4.5 inventory is documentation | Text (static; installed resolution OPEN, D-38) |
| 43 | The sole WF-X exception is fixed independently of the tile and gate tables. Before PK-6b no exclusive entry and no `wfx` row exist. From PK-6b the only exclusive key is `G21c` and the only `wfx` row is `(Finalization_Decide, G21c, O)`, and its declaration (with its type), region, assignments and test equal the normative protocol (V5-RC4-GATE-EXCEPTION). | R-GATE: `CAPI_WFX_PROTOCOL` (CR2) with the row identity (CR5) and the roster and content check (CR6) | Text |
| 44 | No full expanded name can be captured, and no routine can be denoted by its simple name, through any of: a declaration in the pair (at any nesting depth) or in its parent specification; a unit that a with clause of the pair or of the parent specification mentions, as the named unit or as a prefix of it; a use clause in the parent specification; a subunit (V5-RC4-QUAL-CAPTURE; L13–L15). | R-QUAL (d1)–(d4): `_capi_capture` (CR3), applied by CR4 to the C_API specification, the C_API body and `CAPI_PARENT_SPEC`; R-INV (vii) for use clauses in the pair | Text (static; installed resolution and child-unit capture OPEN, D-38) |
```

**W-A19 (inserted after v5:862, the B12 `R-QUAL` row, which is unchanged; sha256 of that line followed by `\n`: `73aad14473cc2343fe4e95168274c9272b1b2b7aaa6cae12355bc575e20c1190`).**
```text
v6 (inserted):
| R-QUAL (d): every mentioned unit and the parent specification (v6; V5-RC4-QUAL-CAPTURE) | Each must produce an R-QUAL problem *(sim)*. No table binds a with clause of the C_API body or of the parent specification: R-RES hashes the body from `CAPI_BODY_HEAD`, and R-INV (iii) covers only use clauses, renamings and pragmas. So each of these edits is already an amendment; nothing else has to change for it to be consistent. The C_API specification is bound whole by S-RES, which also refuses MQ17.<br>MQ15 `with Worldline.Evaluation_Pending.Child;` added to the C_API body's context. The capturing unit `Worldline.Evaluation_Pending` is mentioned only as a prefix.<br>MQ16 `with Worldline.C_API.Evaluation_Pending_C.Child;` added to the C_API body's context.<br>MQ17 `limited with Worldline.Evaluation_Pending.Child;`, and separately `private with Worldline.Evaluation_Pending.Child;`, added to the C_API specification's context.<br>MQ18 `with Decide_Value;`, and separately `limited with Worldline.Evaluation_Pending.Child;`, added to the parent specification's context. The second is refused by its text, whether or not Ada admits it there.<br>MQ19 `Evaluation_Pending : constant Integer := 0;`, and separately `Present : constant Boolean := True;`, added to the parent specification after `Zero_Hash`.<br>MQ20 `use Attest.SHA256;` added to the parent specification's context.<br>MQ21 `with Decide_Value;` added to the C_API body's context: a library unit named by a listed simple name.<br>MQ22 `procedure Capture_Stub is separate;` added after the C_API body's head (R-RES refuses it too).<br>MQ23 an empty parent specification text: the unit cannot be isolated.<br>MQ24 a nested package `Child_Boundary`, as in the root-worker draft, added after the C_API body's head, whose body declares `package Evaluation_Pending renames Evaluation_Pending_V2;` (a declaration nested inside a package body; R-INV (ii) and R-RES refuse it too).<br>**Positive controls** *(sim)*: the unchanged S5 contexts of the C_API specification and body, and the unchanged S5 parent specification, give no R-QUAL problem at PK-1, PK-5, PK-6b and PK-7. Neither does the PK-7 text with the context additions that later stages need: `with Ada.Text_IO;`, `with Ada.Exceptions;`, and a with clause for each of the 17 `CAPI_SPARK_UNITS` and for `Evaluation_Finalization`. |
```

**W-A20 (inserted after v5:865, the B12 `WF-X` row, which is unchanged; sha256 of that line followed by `\n`: `d816d4e7899a2950a9c527cbf163041fcb1be1ce11d8ea3e9ebc174981c228e3`).**
```text
v6 (inserted):
| WF-X roster and protocol (v6; V5-RC4-GATE-EXCEPTION) | Each must produce an R-GATE problem from the protocol check (CR5 or CR6) *(sim)*. Each is an amendment: the tile, `CAPI_GATES`, `CAPI_GATE_EXCLUSIVE` and, where the qualified calls change, `CAPI_QUALIFIED` are amended to match one another. In the author simulation, none of the v5 checks it runs (R-TILE, R-INV, R-ALIAS, R-QUAL, R-GATE, and R-RES with S-RES, R-LAYOUT and R-GLUE) reported a problem for any of them; R-W was not simulated.<br>MX9 (added) G19b becomes a second `wfx` exception. `Pending_Decide_V1`'s `O` is declared without an initializer and assigned on both branches of `if J'Length > 0 then … else … end if;` before its test, with a matching `wfx` row and a `CAPI_GATE_EXCLUSIVE` entry `G19b`.<br>MX10 (relabelled) the row id `G21c` becomes `G21x` in `CAPI_GATES` and `CAPI_GATE_EXCLUSIVE`.<br>MX11 (relabelled) the object `O` becomes `Z` in the tile, the gate text and the exclusive entry.<br>MX12 (moved) the export holding the exception is renamed `Finalization_Decide_Moved` in its tile, its B3 declaration, its caller in `Final_Context_Matches`, `CAPI_LAYOUT_EXPORTS` and the scope keys of `CAPI_GATES`, `CAPI_INVENTORY` and `CAPI_QUALIFIED`.<br>MX13 (staged early) `CAPI_GATE_EXCLUSIVE` holds the G21c entry at PK-1, and separately at PK-5.<br>MX14 (assignment) the else-assignment becomes `O := Evaluation_Finalization_C.Decide_Rows_Value (X, A, Required, Captured);`.<br>MX15 (region) `null;` is added at the start of the region's then branch.<br>MX16 (declared type) the declaration becomes `O : Evaluation_Pending_C.Decide_Acceptance;`.<br>MX17 (test) the final test returns `254` instead of `255`.<br>**Positive controls** *(sim)*: the unchanged staged tables give no R-GATE problem: at PK-1 and PK-5, `CAPI_GATE_EXCLUSIVE` empty and no `wfx` row; at PK-6b and PK-7, only `G21c`, equal to the protocol. |
```

### W.4 Reading rules for carried v5 text

- **WR1.** In carried v5 text, "this file", "the v5 sections" and references to B0.5, B0.7, B0.10, B1.1, B8, B9.4, B10.3, B11 and B12 resolve to those sections as carried into A-BIND v6 with §W.3 applied. "B8" includes B8.4. "The v5 code" and "the B8 sketch" mean the v6 code (B8.4), except where the text records the v5 run.
- **WR2.** Statements in carried v5 text of the form "v5 does X" describe the binding as carried into v6, unless §W.3 or B8.4 replaces them. B8.0's account of the v5 author simulation remains the record of that run. The v6 run is W-A10 and AUTHOR-NOTES.md §4.
- **WR3.** "JACKAL Jnn" in carried text means call Jnn of the v5 `jackal.json` (sha256 `612d189e4edc29cda39c8e61ac3668bf04adb6abcda12728f7ec14272d4f46d4`) for J01–J68, carried by reference, and of the v6 `jackal.json` for J69 onward.
- **WR4.** Carried v5 §V keeps its reading rules AR1–AR4 for the v4 text it carries. Where AR1 says "the v5 sections of this file", read WR1.
- **WR5.** "The rule checks of B0.4–B0.7 and B0.10" (A-R1, AR4) include the v6 checks of B8.4.

---

## A-BIND v6 in reading order

1. Carried v5 §V (v5 lines 17-81).
2. B0: v5 lines 85-112; B0.7, v5 lines 114-177 with W-A1 and W-A2; B0.8 and B0.9, v5 lines 179-181; B0.10, v5 lines 183-234 with W-A3 to W-A8.
3. B1.1: v5 lines 238-250 with W-A9.
4. B8: the heading and B8.0, v5 lines 254-270 with W-A10; B8.1, v5 lines 272-557; B8.2, v5 lines 559-575 with W-A11 and W-A12; B8.3, v5 lines 577-587 with W-A13; then **B8.4**, below.
5. B9.4: v5 lines 591-715, then B9.4.7 (W-A14).
6. B10.3: v5 lines 719-790 with W-A15.
7. B11: v5 lines 794-841 with W-A16 to W-A18.
8. B12: v5 lines 845-868 with W-A19 and W-A20.

The v4 sections that v5 carries (B1–B7, B9.1–B9.3, B9.5, B10.1 and B10.2) keep their places, as v5 §V.2 binds them.

---

## B8.4 Code changes CR1–CR6 (NEW in v6)

"v5 code line n" is line n of the v5 code: the lines between the `` ```python `` and `` ``` `` fences of the v4 B8 code block after BR1–BR8 are applied (653 lines; sha256 of the fenced block `e739e0395cd4e513920baa9b6e916bcafefecf66c1f53bef21e032c71eee79cb`, v5 AUTHOR-NOTES.md §1). Each replacement quotes the v5 code lines it removes, exactly, and then gives the v6 lines. An insertion names the v5 code line it follows, and that line is unchanged. Changes are applied by v5 code line number, the highest first.

**CR1 (v5 code lines 1-4, replaced): header comment.**
```text
# C-API raw-pointer boundary consolidation (design v5, stage PK-1). Whole-closure binding, exact
# tiles, transport residues, scoped clause inventory, alias exclusion, fully expanded names, write
# forms, branch-sensitive gates, residual identity and component interface membership. Every
# predecessor check runs first.
```
```python
# C-API raw-pointer boundary consolidation (design v6, stage PK-1). Whole-closure binding, exact
# tiles, transport residues, scoped clause inventory, alias exclusion, fully expanded names without
# capture, write forms, branch-sensitive gates with one fixed assignment exception, residual identity
# and component interface membership. Every predecessor check runs first.
```

**CR2 (inserted after v5 code line 29, `CAPI_GATE_EXCLUSIVE = {} …`, which is unchanged): the WF-X protocol and the parent specification.** This insertion has no empty lines before it; it continues the table block.
```python
CAPI_WFX_PROTOCOL = ('Finalization_Decide', 'G21c', 'O',   # B10.3: the sole WF-X exception; PK-1, never updated
    'O : Evaluation_Finalization_C.Decide_Acceptance;',
    '34b1492a5b5a757dab0cd1c62fcc241155be318e42a728da6649387d62c5b4d0',   # sha256 of the exact N1 region
    'O := Evaluation_Finalization_C.Decide_Rows_Value (X, A, Required, Captured);',
    'O := Evaluation_Finalization_C.Decide_No_Rows_Value (X, A, Required);',
    'if not O.Ok then return 255; end if;')
CAPI_PARENT_SPEC = 'core/worldline.ads'   # R-QUAL (d): the parent unit; its declarations and clauses reach the pair
```

**CR3 (inserted after v5 code line 373, the last line of `_capi_qualified`, which is unchanged): R-QUAL (d) for one compilation unit.** The insertion is preceded by two empty lines.
```python
def _capi_capture(label: str, code: str, roots: set, simple: set, own: str = '') -> list[str]:
    """R-QUAL (d) on N2 of one compilation unit (B0.10). No with clause mentions, as its named unit or as a
    prefix I0.….Ij of it, a unit whose Ij is a root (j >= 1) or a listed simple name (any j). Outside the
    context clause a root occurs only as the first identifier of a dotted name, as a renaming target, or as
    the unit's own name `own` after its first `package` and in its final `end`. No subunit or body stub."""
    context = code.find('package ')                                  # the context clause precedes it
    if context < 0:
        return [f'{label}: the compilation unit cannot be isolated']
    problems = []
    if re.search(r'\bseparate\b', code, re.IGNORECASE):
        problems.append(f'{label}: a subunit or body stub has a context clause that (d) does not examine')
    for match in re.finditer(r'\bwith\s+([\w.,\s]+?)\s*;', code[:context], re.IGNORECASE):
        for unit in match.group(1).split(','):
            words = ''.join(unit.split()).lower().split('.')
            if any(word in roots for word in words[1:]) or any(word in simple for word in words):
                problems.append(f'{label}: the with clause unit {unit.strip()} mentions a unit that can capture '
                                'a full expanded name or name a routine')
    own_places = (context + len('package '), len(code) - len(own) - 1)
    for match in re.finditer(r"(?<![\w.'])[A-Za-z]\w*(?!\w)", code):
        if (match.group().lower() in roots and match.start() > context
                and not re.match(r'\s*\.', code[match.end():])
                and not (code.endswith('renames ', 0, match.start()) and code.startswith(';', match.end()))
                and not (own and match.group().lower() == own.lower() and match.start() in own_places)):
            problems.append(f'{label}: {match.group()}, the first name of a full expanded name, '
                            'is declared or used alone')
    return problems
```

**CR4 (v5 code lines 398-409, replaced): R-QUAL (d) on the pair and on the parent specification.**
```text
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
```
```python
        problems += _capi_capture(label, code, roots, simple)            # R-QUAL (d) on the pair
    parent = _capi_code(_capi_text(root, CAPI_PARENT_SPEC))              # R-QUAL (d) on the parent unit
    problems += _capi_capture('PARENT', parent, roots, simple, 'Worldline')
    if re.search(r'\buse\b', parent, re.IGNORECASE):
        problems.append('PARENT: a use clause can make a declaration directly visible in the C_API pair')
    problems += [f'PARENT: {match.group()} has the name of a routine of a listed SPARK unit'
                 for match in re.finditer(r"(?<![\w'])[A-Za-z]\w*(?!\w)", parent) if match.group().lower() in simple]
```

**CR5 (v5 code line 526, replaced): the row identity of a `wfx` row.**
```text
        if (not re.fullmatch(rf'{re.escape(name)} : [\w.]+;', declaration)
```
```python
        if ((row_id, name) != CAPI_WFX_PROTOCOL[1:3] or not re.fullmatch(rf'{re.escape(name)} : [\w.]+;', declaration)
```

**CR6 (inserted after v5 code line 546, `            problems += _capi_gate_row_problems(body[span[0]:span[1]], row)`, which is unchanged): the WF-X roster and protocol.** This insertion has no empty lines before it. Its lines are indented at function level, so it runs once, after the row loop of `_capi_gate_problems`.
```python
    scope, row_id, name, declaration, region_sha256, then_text, else_text, test = CAPI_WFX_PROTOCOL
    staged = scope in CAPI_LAYOUT_EXPORTS                    # the sole WF-X exception exists from PK-6b only
    wfx = [(key, row[0], row[2]) for key, rows in CAPI_GATES.items() for row in rows if row[1] == 'wfx']
    entry = tuple(CAPI_GATE_EXCLUSIVE.get(row_id, ('', '', '', '')))
    gate = [row[3] for row in CAPI_GATES.get(scope, ()) if row[0] == row_id]
    if (wfx != ([(scope, row_id, name)] if staged else []) or set(CAPI_GATE_EXCLUSIVE) != ({row_id} if staged else set())
            or staged and (entry[0] != declaration or entry[2:] != (then_text, else_text)
                           or hashlib.sha256(entry[1].encode('utf-8')).hexdigest() != region_sha256
                           or gate != [f'{then_text} else {else_text} end if; {test}'])):
        problems.append('the WF-X exception differs from the normative G21c protocol (CAPI_WFX_PROTOCOL)')
```

### B8.4.1 What CR1–CR6 enforce

- **CR2** defines `CAPI_WFX_PROTOCOL` (B10.3) and `CAPI_PARENT_SPEC`. Both are fixed at PK-1 (B1.1, W-A9). `hashlib` is already among the manifest's imports.
- **CR5.** A `wfx` row whose row id and object are not `G21c` and `O` gets no assignment permission: its row check reports that `O` is not assigned exactly once on each exclusive branch. This holds whatever its exclusive entry says.
- **CR6** checks the roster and content once per run, against the constant and not against the tile or another table:
  - the list of `(scope key, row id, object)` of every `wfx` row is exactly `[(Finalization_Decide, G21c, O)]` from PK-6b, and empty before;
  - the keys of `CAPI_GATE_EXCLUSIVE` are exactly `{G21c}` from PK-6b, and none before;
  - from PK-6b, the entry's declaration, region sha256 and assignments, and the G21c row's gate text, equal the protocol.

  The row check (BR7, unchanged apart from CR5) still binds the unit text to the table entry: the declaration and the region each occur once, the assignments are at their two places, and the test immediately follows. So the unit text equals the protocol.
- **CR3 and CR4** apply (d1)–(d4) to the C_API specification and body (labels `SPEC` and `BODY`) and to the parent specification (label `PARENT`, with `own` = `Worldline`), and add (d3) for the parent. `simple` is the stage's set of listed simple names: 85 before PK-6b and 93 from PK-6b (J59).
- **Fail closed.** `_capi_text` raises if the parent specification is missing, and `export_problems` reports a check that cannot run as a problem (`proof_manifest.py:622-637` catches only `OSError` from `export_problems`, which is why the override converts every exception, B8.3). A unit text without `package ` is a problem. An unexpected entry shape in `CAPI_GATE_EXCLUSIVE` fails a comparison or raises; either way a problem is reported.
- **Unchanged.** `CAPI_QUALIFIED`, `CAPI_QUALIFIER_EXCEPTIONS`, `CAPI_INVENTORY`, `CAPI_USE_PACKAGES`, every gate text and branch list, and every other check.

<!-- A-BIND-V6-END -->
