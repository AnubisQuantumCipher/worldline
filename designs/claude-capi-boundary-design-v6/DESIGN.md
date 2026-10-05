# C-API raw-pointer boundary consolidation: design v6

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent) |
| Date | 2026-10-05 (session date) |
| Status | **DRAFT_FOR_GPT61_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author grants nothing, and no author check below is a review. |
| Supersedes | `W/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v5/`: `DESIGN.md` (sha256 `533f0e043fb991d015bcf16494674d791b6f8f8bd5049fef5a8e60594c9341de`, 46731 bytes), `decisions.json` (`a069632a035b62f18d886112763472f13040779d2d5dd79c872a6d6ce951c55b`, 62067 bytes), `APPENDIX-BINDINGS.md` (`f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2`, 94352 bytes), `jackal.json` (`612d189e4edc29cda39c8e61ac3668bf04adb6abcda12728f7ec14272d4f46d4`, 17950 bytes) and `AUTHOR-NOTES.md` (`ed45d1db766f3b03ec946946942a571ae50b0eae21e339c5724b5e2480280e47`, 15349 bytes). All five were read only and are unchanged (re-hashed while drafting). A-COST is v4's `APPENDIX-COST-MAP.md` (`5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4`, 73929 bytes), carried unchanged by reference. |
| Answers | The sealed actual gpt-6.1-sol review of v5 in `…/claude-capi-boundary-design-v5/review/gpt61-v1/`: `REVIEW.md` (sha256 `73e82489706e03ca465e7dea2aed1823df0b50a8ce1c5ab0555c545579dc34d8`, 33299 bytes, equal to its `report_sha256`), `review.json` (`800880d44bff4b234c82cc392a3008fd4d37139b0827d070120cf299370f403b`, 19071 bytes), `checks.json` (`c1398253713aa6d42ed11fda5194502ccae5a64825b36ef8100206f7d40719ef`, 135152 bytes) and `review-freeze.json` (`91bddf1a46763251940db658f5115cd13ab9de4aa67c0a41ae169de165649af1`, 560 bytes). Verdict ENDORSED_WITH_REQUIRED_CHANGES: V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 NOT_CLOSED; latent defects L9–L12 GENUINE and REPAIRED_AT_DESIGN_LEVEL; 31 rulings; required changes **V5-RC4-GATE-EXCEPTION** and **V5-RC4-QUAL-CAPTURE**. |
| Scope | Proof-source design only. It grants no execution, proof, build, test, review, operator or acceptance authority. |
| Location | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v6/` |
| **What this document consists of** | The v6 design is: (1) the text of this file; (2) the v5 `DESIGN.md` line ranges listed in §B-v6.2 as CARRIED_VERBATIM or CARRIED_WITH_LINE_REPLACEMENTS, each bound by the sha256 of its exact bytes, with the line replacements X-R1–X-R8 of §B-v6.4 applied; and (3) through the carried v5 §B and §19, the v4 and v3 `DESIGN.md` slices that v5 carries, with their replacements (v4's R1–R15 and v5's V-R1–V-R9). All earlier files are read only and pinned. No other v5, v4 or v3 text is part of v6. |
| Companion files | `APPENDIX-BINDINGS.md`: A-BIND v6, a delta over v5 A-BIND bound in the same way. `APPENDIX-COST-MAP.md` is **not** reissued: A-COST v4 is carried unchanged by reference, since nothing in it changes. `decisions.json` is the machine twin. `jackal.json` records the new JACKAL call J69 and carries J01–J68 by reference to v5's. `AUTHOR-NOTES.md` holds unresolved items, uncertainties, reviewer guidance and the process record. Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools, and no Write or Edit was refused. Bash was used for read-only inspection, with the deviations disclosed in AUTHOR-NOTES.md §5. |

---

## A. Closure tables: V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE

Each sub-requirement is quoted from the sealed v5 `review.json` `required_changes` (`change`, or `reason` where marked). "v6 answer" names what v6 supplies. "Evidence" gives file:line places: `A6` is `APPENDIX-BINDINGS.md` in this directory, `D5` is the v5 directory, and `S5` is the base. Every answer is a design statement for the reviewer. None is closed by the author, and every proof, native, control and acceptance obligation stays OPEN.

### A.1 V5-RC4-GATE-EXCEPTION: the sole WF-X exception as an independent invariant

| # | Sub-requirement (review text) | v6 answer | Evidence |
|---|---|---|---|
| E.1 | "Make the sole assignment exception an independent invariant" | `CAPI_WFX_PROTOCOL` is a constant of the PK-1 check text that no stage updates. It states the exception's identity and content. R-GATE compares the tables with it, not with a tile or with another table (CR2, CR5, CR6). B1.1 stages it. | A6:64-70 (W-A1, replacing D5/APPENDIX-BINDINGS.md:158); A6:227-241 (W-A15, B10.3); A6:325-334 (CR2); A6:156-163 (W-A9, B1.1) |
| E.2 | "before PK-6b the exclusive map is empty" | While `Finalization_Decide` is not in `CAPI_LAYOUT_EXPORTS`, CR6 requires `CAPI_GATE_EXCLUSIVE` to have no key and no row to have kind `wfx`. Control MX13 puts the G21c entry in the map at PK-1, and separately at PK-5. | A6:65 (W-A1); A6:238 (W-A15); A6:399-411 (CR6); A6:279 (W-A20) |
| E.3 | "from PK-6b its only key is G21c" | From PK-6b CR6 requires the key set of `CAPI_GATE_EXCLUSIVE` to be exactly `{G21c}`. Controls MX9 (a second key) and MX10 (a relabelled key). | A6:66, A6:239; A6:406 (CR6); A6:279 |
| E.4 | "and the only wfx row is (Finalization_Decide, G21c, O)" | CR6 requires the list of `(scope key, row id, object)` over all `wfx` rows to be exactly `[(Finalization_Decide, G21c, O)]`. CR5 also denies assignment permission to any `wfx` row whose row id and object are not `G21c` and `O`. Controls MX9 (added), MX10 and MX11 (relabelled row id; relabelled object), MX12 (moved to another scope). | A6:66, A6:68 (W-A1); A6:391-397 (CR5); A6:403, A6:406 (CR6); A6:279 |
| E.5 | "Validate that identity and its declared type/region/assignments against the normative G21c protocol independently of matching mutable tile/gate entries" | From PK-6b CR6 compares with the constant: the exclusive entry's declaration, and so the declared type and the absence of an initializer; the sha256 of its region; its then- and else-assignments; and the G21c row's gate text, and so the test. The row check (BR7) still binds the unit text to the entry, so the unit text equals the protocol. The region digest `34b1492a…` is that of the 644-byte N1 region of B4.20 segment 6 without its test (observed). Controls MX14 (assignment), MX15 (region), MX16 (declared type), MX17 (test). | A6:67 (W-A1); A6:227-237 (W-A15); A6:404-409 (CR6); A6:417-422 (B8.4.1); A6:279 |
| E.6 | "Add an amendment control for an added, relabelled or moved wfx exception" | The B12 row "WF-X roster and protocol": MX9 (added), MX10 (relabelled row id), MX11 (relabelled object), MX12 (moved to another scope). Each amends the tile, `CAPI_GATES`, `CAPI_GATE_EXCLUSIVE` and, where the qualified calls change, `CAPI_QUALIFIED`, consistently. In the author simulation, the v5 checks it runs reported nothing for any of them, and the v6 R-GATE refused each (AUTHOR-NOTES §4). | A6:276-280 (W-A20, inserted after D5/APPENDIX-BINDINGS.md:865) |
| E.7 | "plus positive controls for the unchanged staged tables" | Positive controls at PK-1 and PK-5 (empty map, no `wfx` row) and at PK-6b and PK-7 (only `G21c`, equal to the protocol). In the simulation, all four staged texts gave no problem from any check it runs, with the v5 code and with the v6 code. | A6:279 (W-A20, "Positive controls"); AUTHOR-NOTES §4 |
| E.8 | "Preserve every current gate, branch payload, diagnostic, refusal code, assignment, write and accepted case" | No tile, gate text, branch list, diagnostic site, refusal code, assignment, write row (B10.2) or residual text changes. v6 changes check text, one constant, and promise and control text only. The G21c branch list stays an ordinary R-GATE list. The 82 runs of the v5 mutations still produce their problems on the v6 code. | A6:28 (W.1); A6:241 (W-A15); A6:425 (B8.4.1); AUTHOR-NOTES §4 |
| E.9 | (reason) "BR7 admits assignment exceptions by an arbitrary row's wfx kind and CAPI_GATE_EXCLUSIVE.get(row_id); neither row validation nor the outer loop enforces the normative sole exception identity" | Row validation: CR5 adds the identity test to the `wfx` branch of `_capi_gate_row_problems` (v5 code line 526, which is D5/APPENDIX-BINDINGS.md:512). Outer loop: CR6 runs once after the row loop of `_capi_gate_problems` (after v5 code line 546, which is D5/APPENDIX-BINDINGS.md:532) and checks the whole roster and the map's keys. B8.2 and B8.3 now say so. | A6:391-397 (CR5); A6:399-411 (CR6); A6:180-186 (W-A12); A6:188-198 (W-A13) |

### A.2 V5-RC4-QUAL-CAPTURE: every mentioned unit, the parent specification and subunits

| # | Sub-requirement (review text) | v6 answer | Evidence |
|---|---|---|---|
| Q.1 | "Extend R-QUAL(d) …" | (d) is restated as (d1)–(d4) and is checked on three compilation units: the C_API specification, the C_API body and the parent specification `core/worldline.ads` (`CAPI_PARENT_SPEC`). | A6:89-110 (W-A4, replacing D5/APPENDIX-BINDINGS.md:202-205); A6:81-87 (W-A3, D5:198) |
| Q.2 | "… BR6 …" | The (d) part of BR6's `_capi_qualifier_problems` (v5 code lines 398-409, which are D5/APPENDIX-BINDINGS.md:384-395) is replaced by CR4. CR4 calls the new helper `_capi_capture` (CR3) on the C_API specification and body and on the parent specification. The with-clause test is now over every prefix, `any(word in roots for word in words[1:])`, instead of `words[-1] in roots`. | A6:336-364 (CR3); A6:366-389 (CR4); A6:168 (W-A10, B8.0) |
| Q.3 | "… the closure argument …" | Way 1 now rests on the revised (d) (W-A5). Way 3 adds the parent specification's use clauses (W-A6). Way 4 adds declarations of the parent specification and library units named like routines (W-A7). A new table lists every capture vector, the rule that refuses it and the S5 observation (W-A8). | A6:112-154 |
| Q.4 | "… promises …" | B11 row 42 is restated with the revised (d), and row 44 is new. DESIGN §8.4's R-QUAL bullet (X-R2) and §8.4.1's O6 (a) row (X-R5) are restated, and so are the B8.2 qualifier row (W-A11) and the B8.3 note (W-A13). | A6:260-268 (W-A18); A6:172-178; A6:188-198; §B-v6.4 X-R2, X-R5 |
| Q.5 | "… and machine twin …" | decisions.json `qualified_v6` states (d1)–(d4), the parent specification, the observations and the controls; `closure` maps each sub-clause. | decisions.json `qualified_v6`, `closure` |
| Q.6 | "… to examine every potentially capturing library-unit prefix mentioned by each with clause, including ancestor units mentioned through a named descendant" | (d2): a with clause that names `I0.I1.….Ik` mentions every prefix `I0.….Ij` (RM 10.1.2(6/2)). (d) refuses it if any `Ij` with j ≥ 1 is a root. So `with Worldline.Evaluation_Pending.Child;` is refused through its ancestor `Worldline.Evaluation_Pending` (MQ15), and `with Worldline.C_API.Evaluation_Pending_C.Child;` through `Worldline.C_API.Evaluation_Pending_C` (MQ16). The parent specification's with clauses, which reach the pair, are examined too (L13; MQ18). | A6:99 (d2); A6:146-147 (W-A8 rows 3 and 4); A6:273 (W-A19) |
| Q.7 | "Define the text-only refusal without changing the scoped exception or use-clause inventory" | (d) refuses by text and resolves no name; it refuses a mentioned unit whether or not that unit exists. `CAPI_QUALIFIER_EXCEPTIONS`, `CAPI_INVENTORY` and `CAPI_USE_PACKAGES` are unchanged, and so are `CAPI_QUALIFIED` and R-INV (vii). | A6:102 (W-A4); A6:425 (B8.4.1) |
| Q.8 | "Add a matching amendment control" | The B12 row "R-QUAL (d)": MQ15–MQ17 (with clauses of the pair, including `limited` and `private`), MQ18–MQ20 (with clauses, declarations and a use clause of the parent specification), MQ21 (a library unit named like a routine), MQ22 (a body stub), MQ23 (an unreadable parent text) and MQ24 (a declaration nested inside a package body, §A.3 L16). No table binds the with clauses of the C_API body or of the parent specification, so these edits are already amendments. In the simulation, the v6 R-QUAL refused each. The v5 R-QUAL reported nothing for MQ15–MQ23; it refused MQ24, which confirms that nested declarations were already covered. | A6:270-274 (W-A19, inserted after D5/APPENDIX-BINDINGS.md:862); AUTHOR-NOTES §4 |
| Q.9 | "and an unchanged-context positive control" | The unchanged S5 contexts of the C_API specification and body, and the unchanged parent specification, give no R-QUAL problem at PK-1, PK-5, PK-6b and PK-7. Neither does PK-7 with the context additions that later stages need. B9.4.7 records the observed contexts. | A6:273 ("Positive controls"); A6:200-221 (W-A14) |
| Q.10 | "Keep installed integrated name/overload resolution OPEN" | Kept OPEN (D-38). Child-unit capture and the RM 10.1.2, 10.1.1, 8.3 and 8.4 readings in context are added to D-38's installed obligations. | A6:103, A6:153; §17, §18 |
| Q.11 | (reason) "The normative with-clause restriction and BR6 check only the named dotted unit's last identifier … A capturing sibling child mentioned only as a prefix of a named descendant is outside that test, so the asserted no-capture conclusion does not follow from the rule." | Agreed. The v5 rule (D5/APPENDIX-BINDINGS.md:204; its code `words[-1] in roots` at D5/APPENDIX-BINDINGS.md:388) is replaced by (d2) over every prefix, and the conclusion (D5/APPENDIX-BINDINGS.md:205) is restated over the three units. While checking the conclusion, the author found further omissions of the same kind, L13–L15 (§A.3), which (d1)–(d4) also repair. | A6:97-109; §A.3 |

### A.3 Latent v5 defects found while drafting v6 (author's observations, not review findings)

| # | Defect | v6 correction |
|---|---|---|
| L13 | v5's (d) and its closure argument examined only the C_API pair (D5/APPENDIX-BINDINGS.md:198, 202-205, 207-227; code at :384-395). The parent specification `core/worldline.ads` is visible throughout `Worldline`'s declarative region, which includes the pair. So a declaration there named by a root (for example `Evaluation_Pending : constant Integer := 0;`), a use clause there, or a with clause there escaped (d). In S5 the parent declares only `Hash` and `Zero_Hash` (`core/worldline.ads:5-7`), has no use clause and withs only `Attest.SHA256`, so nothing is captured today. In the simulation, the v5 code accepts MQ18–MQ20 and MQ23. | (d1)–(d4) on the parent specification, and (d3) for its use clauses and listed simple names (A6:97-101; CR4 at A6:366-389). |
| L14 | Neither v5's (d) nor way 4 of its closure argument (D5/APPENDIX-BINDINGS.md:224) considered a library unit named by a listed simple name and made visible by a with clause, for example a library-level renaming `Decide_Value` of an Appendix C routine. The pair could then call the routine by its simple name. No other check binds the with clauses of the C_API body: R-RES hashes the body from `CAPI_BODY_HEAD`, and R-INV (iii) concerns use clauses, renamings and pragmas only. In the simulation, the v5 code accepts MQ21, and MQ18a for the parent. | (d2) also refuses a listed simple name at any position of a mentioned unit's name (A6:99; W-A7 at A6:128-134). |
| L15 | A body stub in the pair (`is separate`) would move text into a subunit, whose own context clause and declarations v5's (d) does not examine. The v5 R-QUAL accepts MQ22; R-RES refuses it only because the residual text changes. | (d4): no `separate` in the three units (A6:101). |
| L16 | A wording defect, relayed by the lead from the parallel seam lane (NF-5, an unreviewed author finding) and checked by the author against the source. v4 DESIGN line 778 (carried by v5 §19) and v5 DESIGN line 338 call the root-worker draft's package renamings `Y`, `J`, `D`, `A`, `X`, `E`, `T`, `N`, `W`, `O`, `Q` "C_API body level" and "body-level". In the draft (`RW/source/core/worldline-c_api.adb`, sha256 `806f3972…`, 148068 bytes, as v4 observed it) they are at lines 1199-1205 and 1217-1220, inside `package body Child_Boundary is` (line 1198) … `end Child_Boundary;` (line 2251). The sealed seam v2 review rules the same (`review.json` `findings_detail` N-5, VERIFIED_LEXICAL_SCOPE). The conclusions stand: the renamings are not roots; (d1) scans each unit's whole text, at any nesting depth; R-INV (ii) gives each clause to its innermost scope, and `Child_Boundary` is not a designed scope, so its renamings fall to RESIDUAL and are refused as unlisted; and R-RES refuses any change to the residual text. The capture hazard of v4 line 779 remains a hazard only if a rebase merges scopes; no current same-scope collision is asserted. | X-R7 and X-R8 correct the wording (§B-v6.4). A6:98 and A6:144 state the nesting coverage, and MQ24 exercises it (A6:273). |

---

## B. Carried forward (v6)

### B-v6.1 Items the v5 review ruled, carried unchanged

The ruling column quotes the sealed v5 review: its `rc_closure`, its `latent_defects` (leading clause) and all 31 `rulings` (the `ruling` field, verbatim). v6 removes or weakens none of them.

| Item | v5 review ruling | v6 |
|---|---|---|
| V4-RC4-GATE | NOT_CLOSED | Its remaining gap is V5-RC4-GATE-EXCEPTION, answered in §A.1. v5's §A.1 (carried) stands as amended. For the reviewer; NOT_CLOSED until reviewed. |
| V4-RC4-ALIAS | NOT_CLOSED | Its remaining gap is V5-RC4-QUAL-CAPTURE, answered in §A.2. v5's §A.2 (carried) stands as amended. For the reviewer; NOT_CLOSED until reviewed. |
| V3-RC4 | NOT_CLOSED | Its remaining required changes are answered above. For the reviewer. |
| L9 | GENUINE; REPAIRED_AT_DESIGN_LEVEL for the fixed staged inventory | Carried: the staged R-ALIAS pairs (v5 A-BIND B0.5, B1.1). The L9 control still holds in the v6 simulation. |
| L10 | GENUINE; REPAIRED_AT_DESIGN_LEVEL for the listed Boolean and case gates | Carried. The distinct sole-exception gap it names is answered in §A.1. |
| L11 | GENUINE; REPAIRED_AT_DESIGN_LEVEL | Carried: A-R2 and BR5 unchanged. |
| L12 | GENUINE; REPAIRED_AT_DESIGN_LEVEL for the fixed acceptance-type inventory | Carried. |
| RC1 | CLOSED_AT_DESIGN_LEVEL preserved | Carried unchanged. |
| RC2 | CLOSED_AT_DESIGN_LEVEL preserved | Carried; B4.20 segment 6 unchanged. The WF-X protocol states its region by digest; that is not a design change. |
| RC3 | CLOSED_AT_DESIGN_LEVEL for N-01 resolution discipline preserved | Carried unchanged. |
| LD1 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL preserved | Carried unchanged. |
| LD2 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL preserved | Carried unchanged. |
| LD3 | CONDITIONALLY_ACCEPTABLE_PENDING_D-13 preserved | Carried unchanged. |
| LD4 | WITHDRAWN preserved | Carried unchanged. |
| LD4-R | CLOSED_AT_DESIGN_LEVEL for RC1 preserved | Carried unchanged. |
| LD5 | CONDITIONALLY_ACCEPTABLE preserved | Carried unchanged. |
| LD6 | CONDITIONALLY_ACCEPTABLE; V3-RC5 design condition discharged preserved | Carried unchanged. |
| V3-RC5 | CLOSED_AT_DESIGN_LEVEL preserved | Carried unchanged. |
| V3-RC6 | CLOSED_AT_DESIGN_LEVEL preserved | Carried unchanged; A-COST v4 by reference. |
| L1-L8 | GENUINE and prior design repairs preserved; L3 installed warning UNVERIFIED; L5 separate RC4 gate obligation remains NOT_CLOSED | Carried. L5's gate obligation is the RC4 gate item answered in §A.1. |
| D-13 | OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE. Reservation concerns a concrete material component transport/library architecture choice, not editing pinned implementation files or recomputing effective pins. | Carried as ruled. No choice is made, and options (ii) and (iii) remain inadmissible. |
| N-06 | REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT; mismatch refusal remains. An old-library hold supplies no consolidated-candidate acceptance. | Carried as ruled. No deployment action. |
| N-01 | LEAD_OWNED_STRICT_OBLIGATION; confirming representation repairs preserve C1-C8 and satisfy E1-E6. Any nonconfirming material ABI change is separately operator-owned and grants no weakening of the original target. | Carried as ruled (v3 §10). |
| D-05 | OPEN | Carried. |
| D-18 | CLOSED_AT_DESIGN_LEVEL for index design; proof OPEN | Carried. |
| D-19 | OPEN | Carried. |
| D-28 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL | Carried. |
| D-36 | OPEN for every write form | Carried. |
| D-15/D-34/D-38 | OPEN | Carried OPEN. v6 adds to D-38 child-unit capture and the RM 10.1.2, 10.1.1, 8.3 and 8.4 readings of R-QUAL (d) in context. |
| N-03 | OPEN | Carried. |
| N-04 | CLOSED_AT_DESIGN_LEVEL for Classify enrollment; implementation obligations OPEN | Carried. |
| N-05 | OPEN | Carried. |
| N-07 | CLOSED_AT_DESIGN_LEVEL for pending Decide enrollments; implementation obligations OPEN | Carried. |
| APPENDIX_C | CLOSED_AT_DESIGN_LEVEL for exact append-only ordering/enrollment | Carried: Appendix C unchanged. |
| R2_NINE_CONDITIONS | NOT_CLOSED | Condition (4)'s gate and qualified-name invariants are repaired in §A (§17). For the reviewer. |
| PACKET_PLAN | NOT_CLOSED | Carried (§9 with V-R9; A-BIND B1.1 with W-A9). For the reviewer. |
| ROOT_WORKER_INTEGRATION | OPEN; no ruling on the other lane or integration order | Carried OPEN. v6 makes no ruling on the other lane or the integration order (§19). |
| OB-048 | OPEN for enlarged and pre-existing boundary | Carried OPEN. |

**Unchanged fixed targets**, as in v5:
- `MINIMUM_CHECKS = 251`;
- the 535-name ordered `REQUIRED_PROVED` prefix, append-only;
- `UNANALYZED_BOUNDARY == {"worldline-c_api"}`;
- 169 effective `CONTRACT_PINS` keys at L0;
- both builds;
- every checked assertion.

**Nothing weakened.** No cap, new public Pre, refusal relabelling, suppression, warning waiver, `pragma Assume`, new Off exception or ABI narrowing is introduced. No transport code, meaning, layout or caller protocol changes. v6 changes check, constant, table-staging, promise and control text only, and every change refuses more, never less.

### B-v6.2 Disposition of every v5 `DESIGN.md` section

"v5 lines" are 1-based lines of the v5 file. The sha256 is that of the UTF-8 bytes of those lines, each followed by `\n` (observed by a read-only script).

| v5 section | v5 lines | sha256 of the v5 slice | Disposition | v6 location |
|---|---|---|---|---|
| Header | 1-14 | — | REPLACED | header above |
| §A Closure tables for V4-RC4-GATE and V4-RC4-ALIAS, and latent defects L9–L12 | 18-49 | `7fa68bed33a1c5fe54743eaeda01d1c8ab3c67c01ded1b16d2def11b0971b32c` | CARRIED_VERBATIM as history (RR-W5) | v5 §A |
| §B v5's composition over v4 (B-v5.1–B-v5.4, with V-R1–V-R9) | 53-231 | `34e0da4296a4ae67c17c6f2168149b8a54957d62e1ce66a5e7ff1d1d6ab2a711` | CARRIED_WITH_LINE_REPLACEMENTS (X-R1 v5:156, X-R2 v5:173, X-R3 v5:189, X-R4 v5:198, X-R5 v5:206, X-R6 v5:222) | v5 §B; §B-v6.4 |
| §0 Truth boundary (v5 supplement) | 235-265 | `f15a3160fc962d88a1a5e7725808808f55d7d77b2bf21dfae68ab6917cca042b` | CARRIED_VERBATIM as v5's record, with the v6 supplement | §0 |
| §17 Rulings and carried items | 269-296 | — | REPLACED | §17 |
| §18 Everything OPEN | 300-328 | — | REPLACED | §18 |
| §19 Root-worker collision (v5 supplement, carrying v4 §19) | 332-339 | `68487dbac9c37ce7a51b3ea95fae6d8326e8aaa6cef7b97eb579ddd3dc2af9a8` | CARRIED_WITH_LINE_REPLACEMENTS (X-R7 v5:338; X-R8 the effective v4:778 that v5:334 carries), with the v6 supplement | §19; §B-v6.4 |
| Appendix A JACKAL and observed counts | 343-372 | — | REPLACED | Appendix A |
| Appendix B Bound inputs | 374-408 | — | REPLACED | Appendix B |
| Appendix C REQUIRED_PROVED append | 410-412 | `ff085fcce4b4423e88c00b313b8725fd894653759fadc9c035b20cfaa7ac5392` | CARRIED_VERBATIM | Appendix C |
| Appendix D Companion identities | 414-424 | — | REPLACED | Appendix D |
| Section separators | 16, 51, 233, 267, 298, 330, 341 | — | not carried (layout only) | — |

### B-v6.3 Reading rules for carried text

- **RR-W1.** Carried v5 text that states the design's current state ("v5 replaces", "in v5") states the v6 state, unless this file or A-BIND v6 replaces it.
- **RR-W2.** "JACKAL Jnn" in carried text means call Jnn of the v5 `jackal.json` (sha256 `612d189e…`, carried by reference) for J01–J68, and of the v6 `jackal.json` for J69.
- **RR-W3.** "A-BIND §Bn" in carried text means A-BIND v6: the v6 appendix together with the v5 slices it carries, and through them the v4 slices. "A-COST" means the v4 `APPENDIX-COST-MAP.md`, carried unchanged.
- **RR-W4.** References in carried text to §17, §18 and Appendices A, B and D resolve to the v6 replacements in this file.
- **RR-W5.** v5 §A is v5's answer to the v4 review, carried as history. Its row G.3 (the WF-X statement) and its rows Q.2 and Q.5 (rule (d) and the independent-invariant claim) stand as amended by §A.1 and §A.2 here. Its L9–L12 rows stand as the v5 review ruled them.
- **RR-W6.** v5 §0 and the v5 AUTHOR-NOTES describe v5's drafting. v6's process record is the §0 supplement below and the v6 AUTHOR-NOTES.

### B-v6.4 Line replacements in carried slices

Each item quotes the exact line and gives the v6 line that replaces it. The targets of X-R1–X-R6 lie in the "v5:" halves of v5's V-R blocks, so each changes the effective text of the v4 line that v5 replaced. X-R7 is a line of v5 §19, and X-R8 is v4 line 778, which v5 §19 carries verbatim (v5:334); both correct the wording defect L16. Nothing else in a slice changes.

**X-R1 (v5:156, the v5 text of V-R1; §8.1 rule tables).**
```text
v5:
- **Rule tables:** `CAPI_ALIAS_FORBIDDEN` (its `K.` pairs of removed names from PK-6b), `CAPI_SPARK_UNITS`, `CAPI_USE_PACKAGES`, `CAPI_ROUTINE_NAMES`, `CAPI_REMOVED_NAMES` (from PK-6b), `CAPI_QUALIFIED`, `CAPI_QUALIFIER_EXCEPTIONS`, `CAPI_WRITES`, `CAPI_GATES` (with kind and components by branch), `CAPI_GATE_EXCLUSIVE` (from PK-6b; replaces `CAPI_GATE_ASSIGNED`), `CAPI_DIAGNOSTIC_SITES` (from PK-6b).
v6:
- **Rule tables:** `CAPI_ALIAS_FORBIDDEN` (its `K.` pairs of removed names from PK-6b), `CAPI_SPARK_UNITS`, `CAPI_USE_PACKAGES`, `CAPI_ROUTINE_NAMES`, `CAPI_REMOVED_NAMES` (from PK-6b), `CAPI_QUALIFIED`, `CAPI_QUALIFIER_EXCEPTIONS`, `CAPI_WRITES`, `CAPI_GATES` (with kind and components by branch), `CAPI_GATE_EXCLUSIVE` (from PK-6b; replaces `CAPI_GATE_ASSIGNED`), `CAPI_DIAGNOSTIC_SITES` (from PK-6b). **Fixed constants (v6; PK-1, never updated):** `CAPI_WFX_PROTOCOL`, the normative G21c protocol, and `CAPI_PARENT_SPEC` (A-BIND §B8.4 CR2, §B10.3).
```

**X-R2 (v5:173, the v5 text of V-R3; §8.4 R-QUAL; V5-RC4-QUAL-CAPTURE).**
```text
v5:
- **R-QUAL (new in v5: the exact per-call expanded-qualifier invariant of V7 and O6 (a)).** On the whole C_API pair, the dotted names whose last selector is an Appendix C routine name (and, from PK-6b, a removed routine name) are counted per scope, case-insensitively. Each scope's multiset must equal `CAPI_QUALIFIED` exactly. Every listed text is either a full expanded name of `CAPI_ROUTINE_NAMES`, or one of the nine listed exceptions, each of which denotes another entity and has its scopes. In addition, no such name is selected from a non-name prefix; no full expanded name is the prefix of an attribute; the first identifier of a full expanded name is never declared or used alone outside the context clause; and no `with` clause names a unit that could capture that identifier. So every indirect, transport-qualified, `C_API`-qualified, parent-shortened, library-unit or `Standard`-prefixed spelling is refused without resolving the path (A-BIND §B0.10, §B9.4).
v6:
- **R-QUAL (new in v5: the exact per-call expanded-qualifier invariant of V7 and O6 (a); (d) revised in v6).** On the whole C_API pair, the dotted names whose last selector is an Appendix C routine name (and, from PK-6b, a removed routine name) are counted per scope, case-insensitively. Each scope's multiset must equal `CAPI_QUALIFIED` exactly. Every listed text is either a full expanded name of `CAPI_ROUTINE_NAMES`, or one of the nine listed exceptions, each of which denotes another entity and has its scopes. In addition, no such name is selected from a non-name prefix; no full expanded name is the prefix of an attribute; and no full expanded name can be captured. Rule (d) is checked on the C_API specification, the C_API body and the parent specification `core/worldline.ads`: the first identifier of a full expanded name is never declared or used alone outside the context clause; no with clause mentions, as its named unit or as a prefix `I0.….Ij` of it, a unit whose `Ij` is such a first identifier (j ≥ 1) or a listed routine name; the parent specification has no use clause and no listed routine name; and none of the three units contains `separate`. So every indirect, transport-qualified, `C_API`-qualified, parent-shortened, library-unit or `Standard`-prefixed spelling is refused without resolving the path (A-BIND §B0.10, §B9.4).
```

**X-R3 (v5:189, the v5 text of V-R4; §8.4 R-GATE; V5-RC4-GATE-EXCEPTION).**
```text
v5:
  - no acceptance object is assigned, passed whole or renamed, with one exception: finalization `O` (`wfx`, G21c), declared without an initializer and assigned exactly twice, as the last statement of the then branch and as the whole else branch of the one `if Evaluation_Finalization_C.Needs_Rows (X) then … else … end if;` (no `elsif`), which its test immediately follows (`CAPI_GATE_EXCLUSIVE`; R-W row W21 binds the same count);
v6:
  - no acceptance object is assigned, passed whole or renamed, with one exception: finalization `O` (`wfx`, G21c), declared without an initializer and assigned exactly twice, as the last statement of the then branch and as the whole else branch of the one `if Evaluation_Finalization_C.Needs_Rows (X) then … else … end if;` (no `elsif`), which its test immediately follows (`CAPI_GATE_EXCLUSIVE`; R-W row W21 binds the same count). The exception is an invariant of its own (v6): before PK-6b `CAPI_GATE_EXCLUSIVE` is empty and no row has kind `wfx`; from PK-6b its only key is `G21c`, the only `wfx` row is `(Finalization_Decide, G21c, O)`, and its declaration (with its type), region, assignments and test equal the fixed `CAPI_WFX_PROTOCOL`, compared with the constant and not with the tile or another table (A-BIND §B0.7, §B10.3, §B8.4 CR5 and CR6);
```

**X-R4 (v5:198, the v5 text of V-R5; §8.4.1 O5 row).**
```text
v5:
| O5 gating (discriminant test after the declaration, at most `begin` between) | R-GATE (v5): the exact gate form per kind; the test occurs once, inside the gate; each component selected only where its variant is established (`False` components inside the rejection branch, `True` components after the gate, case components inside their alternative); the sole WF-X exception stated exactly | Makes A1 enforceable, branch-correctly (V4-RC4-GATE) |
v6:
| O5 gating (discriminant test after the declaration, at most `begin` between) | R-GATE (v5): the exact gate form per kind; the test occurs once, inside the gate; each component selected only where its variant is established (`False` components inside the rejection branch, `True` components after the gate, case components inside their alternative); the sole WF-X exception stated exactly and, from v6, checked against the fixed `CAPI_WFX_PROTOCOL` at every stage | Makes A1 enforceable, branch-correctly (V4-RC4-GATE; V5-RC4-GATE-EXCEPTION) |
```

**X-R5 (v5:206, the v5 text of V-R6; §8.4.1 O6 (a) row).**
```text
v5:
| O6 (a) full expanded names | R-QUAL (exact per-scope expanded qualifiers, no non-name prefix, no attribute of a routine, no capture of a full expanded name) with R-INV (v) and (vii) (v5), plus R-TILE; R-ALIAS kept as a named subset | Was enforced by tokens only; v4's R-ALIAS missed indirect paths (V4-RC4-ALIAS) |
v6:
| O6 (a) full expanded names | R-QUAL (exact per-scope expanded qualifiers, no non-name prefix, no attribute of a routine, and no capture of a full expanded name through the pair, its parent specification, any unit their with clauses mention as a named unit or as a prefix, or a subunit) with R-INV (v) and (vii) (v5; (d) revised in v6), plus R-TILE; R-ALIAS kept as a named subset | Was enforced by tokens only; v4's R-ALIAS missed indirect paths (V4-RC4-ALIAS); v5's (d) tested only the named unit's last identifier (V5-RC4-QUAL-CAPTURE) |
```

**X-R6 (v5:222, the v5 text of V-R8; §8.8 mutation row).**
```text
v5:
| v5 rules | A-BIND §B12 (v5), which covers R-TILE, R-TRANS, R-INV (with the path-independent (vii)), R-ALIAS, R-QUAL, R-W, R-GATE (with the `False`-variant, case-alternative and WF-X mutations), R-RES, R-GLUE, R-LAYOUT, K3, K5, G9 and K6 |
v6:
| v6 rules | A-BIND §B12 (v6), which covers R-TILE, R-TRANS, R-INV (with the path-independent (vii)), R-ALIAS, R-QUAL (with the capture controls MQ15–MQ24), R-W, R-GATE (with the `False`-variant, case-alternative and WF-X mutations, and the WF-X roster and protocol controls MX9–MX17), R-RES, R-GLUE, R-LAYOUT, K3, K5, G9 and K6 |
```

**X-R7 (v5:338, §19; L16).**
```text
v5:
  - The draft's body-level package renamings (`Y`, `J`, `D`, `A`, `X`, `E`, `T`, `N`, `W`, `O`, `Q`) are not roots. They are refused by R-INV (ii) and R-RES as unlisted residual text, as in v4.
v6:
  - The draft's package renamings `Y`, `J`, `D`, `A`, `X`, `E`, `T`, `N`, `W`, `O` and `Q`, which lie inside its nested `package body Child_Boundary` (draft lines 1198-2251), are not roots. They are refused by R-INV (ii) and R-RES as unlisted residual text, as in v4: R-INV (ii) gives each clause to its innermost scope, `Child_Boundary` is not a designed scope, and R-RES binds all residual text at any nesting depth.
```

**X-R8 (effective v4:778, §19, carried verbatim by v5 §19 (v5:334); L16).**
```text
v4:
  - The draft declares package renamings at C_API body level (draft lines 1199-1220): `Y`, `J`, `D`, `A`, `X`, `E`, `T`, `N`, `W`, `O`, `Q`.
v6:
  - The draft declares package renamings inside its nested `package body Child_Boundary is` (draft line 1198), not at C_API body level: `Y`, `J`, `D`, `A`, `X`, `E`, `T` (draft lines 1199-1205) and `N`, `W`, `O`, `Q` (draft lines 1217-1220), all before `end Child_Boundary;` (draft line 2251). Declarations of a package body are not visible outside it, so relocated export bodies placed at C_API body level after `end Owner_Audit_Decide;` would be outside their scope. The hazard below arises only if a rebase merges scopes.
```

---

## 0. Truth boundary (v5 §0 carried; v6 supplement)

v5 §0 (v5 lines 235-265) is carried verbatim as v5's record, and with it the v4 and v3 records it carries. The following supplements it for v6.

**What was executed while drafting v6.** Only read-only inspection, and one author simulation:
- **Bash** was used to read files and print. Commands outside the brief's literal list, and two deviations, are reported in AUTHOR-NOTES.md §5: nine commands merged standard error into their output pipe with `2>&1`, and one command ran `ls` on an S5 subpath. No file was created, moved, copied, deleted or changed with Bash or Python, and no output was written to a file.
- **The author simulation** (A-BIND W-A10). A read-only Python script rebuilt the v5 code from the v4 code and BR1–BR8, and the v6 code from the v5 code and CR1–CR6. It executed both in memory, with `normalized_ada` reimplemented and stubs for the manifest functions, on successor texts assembled in memory, and printed only results. No WORLDLINE module was imported, and `proof_manifest.py` was not opened in v6.
- **Reads beyond the design files, S5 and the skills:** for L16, the root-worker source draft at its cited lines and the sealed seam v2 review's finding N-5 (Appendix B); and, to recover details lost to a context compaction, session transcript files (AUTHOR-NOTES.md §5). The seam v3 design directory was not read.
- **Not run:** no compiler, prover, gprbuild, gnatprove, test, service, project-vault or restic.
- **No interruption.** No TaskStop, kill or `timeout` wrapper was used, and no command hung. One mid-task message from the coordinator (NF-5) was handled within the task (AUTHOR-NOTES.md §5).
- **SIA.** One `sia.ask` call was made at the start of the v6 work; it returned only `[model]`-origin notes, and nothing from it was used (AUTHOR-NOTES.md §5). No SIA note was written.

**Additional bases.**
- `D5` = `W/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v5`.
- `R5` = `D5/review/gpt61-v1`, the sealed review; its identities are in the header.

**v6 numbers.**
- The only derived number new in v6 is the JACKAL `jackal_exact` call J69, recorded in `jackal.json`. J01–J68 are carried by reference to the v5 `jackal.json`.
- J69 returned `status=exact`, `formal=false`, lane `rat`, evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, and the three non_claims quoted in Appendix A.
- Counts read from files or tool output by a script are reported as observed.

**Author checks are not review.** v6 cites read-only author scripts:
- the carried-slice hashes and quotes;
- the B8 reconstruction, its syntax parse and its diff against v5;
- the simulation and its mutations;
- the S5 context, parent-specification and tree observations;
- the bound-input re-hashes.

They are self-checks by the author. They grant nothing, and they do not substitute for the required independent actual gpt-6.1-sol review.

---

## 17. Rulings and carried items (REPLACED in v6)

| Item | v6 disposition |
|---|---|
| V5-RC4-GATE-EXCEPTION | Answered in §A.1 (A-BIND W-A1, W-A2, W-A9, W-A12, W-A13, W-A15, W-A17, W-A18, W-A20; B8.4 CR2, CR5, CR6). For the reviewer; NOT_CLOSED until reviewed. |
| V5-RC4-QUAL-CAPTURE | Answered in §A.2 (A-BIND W-A3–W-A8, W-A10, W-A11, W-A13, W-A14, W-A18, W-A19; B8.4 CR3, CR4). For the reviewer; NOT_CLOSED until reviewed. |
| V4-RC4-GATE, V4-RC4-ALIAS | NOT_CLOSED (review). Their remaining gaps are the two required changes above; v5's answers (v5 §A.1, §A.2, carried) stand as amended. For the reviewer. |
| V3-RC4 | NOT_CLOSED (review). For the reviewer. |
| L9–L12 | GENUINE; REPAIRED_AT_DESIGN_LEVEL (review), with the limits the review states. Carried. |
| L13–L16 | Latent v5 defects found while drafting v6 (§A.3); L16 was relayed from the parallel seam lane and checked by the author. For the reviewer. |
| V3-RC5, V3-RC6, RC1–RC3, LD1–LD6, LD4-R, L1–L8, APPENDIX_C | As the v5 review ruled (§B-v6.1). Carried unchanged. |
| D-01 … D-04, D-06 … D-12, D-14, D-17, D-20 … D-27, D-29 … D-33, D-35, D-37 | Carried from v3 (v3:2281) through v4 and v5, unchanged in substance. Each stays OPEN where v3 said OPEN. |
| D-05 | OPEN (review). Contextual proof is required at every original partial-decoder caller, or a separately reviewed non-narrowing total restructure. No helper Pre is approved. |
| D-13 | OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE. The reservation concerns a concrete material component transport/library architecture choice, not editing pinned implementation files or recomputing effective pins (review). Operator item §16.1; no choice is made. |
| D-15, D-34, D-38 | OPEN: matching native export, layout and loaded-library evidence; installed-tool legality, including integrated name and overload resolution in the C_API body (§3.6) and child-unit capture; any warning on a transported clause (A-BIND §B0.9); and the RM 8.4, 10.1.2, 10.1.1 and 8.3 readings that R-QUAL's argument uses, in context (A-BIND §B0.10). |
| D-16 | Withdrawn with LD4; replaced by LD4-R (§4). |
| D-18 | CLOSED_AT_DESIGN_LEVEL for the index design (review); proof OPEN (§5.4). |
| D-19 | OPEN (§5.5). |
| D-21 | The pre-existing `Authority_Glue` value decisions are unchanged and enforced by R-RES; they are boundary surface (§14). |
| D-28 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL (review); native costs OPEN (A-COST §C16). |
| D-36 | OPEN for every write form (§3.4, §11.4, A-COST §C19). C-14 is proposed behaviour for the WF-C and WF-A exports only. |
| N-01 | §10; LEAD_OWNED_STRICT_OBLIGATION (review). Confirming representation repairs preserve C1–C8 and satisfy E1–E6; a nonconfirming material ABI change is separately operator-owned and grants no weakening of the original target. |
| N-02 | Enforced by G7. |
| N-03 | OPEN (review); existing callees need full matching-source strict proof, and no PROVED_ROW transfers. |
| N-04 | CLOSED_AT_DESIGN_LEVEL for the explicit `Classify` enrollment (review); implementation obligations OPEN. |
| N-05 | OPEN (review); the original exact-set static-audit assertion stays. No exact-set-to-subset reinterpretation or removal. |
| N-06 | REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT; mismatch refusal remains. An old-library hold supplies no consolidated-candidate acceptance (review). Operator item §16.2. |
| N-07 | CLOSED_AT_DESIGN_LEVEL for the explicit pending `Decide` enrollments (review); implementation obligations OPEN. |
| R2_NINE_CONDITIONS | Mapped to v6 checks (§8, A-BIND §B11):<br>(1) relocation map: §6 and A-BIND §B2–§B3;<br>(2) one binding: G1–G10 and K1–K6;<br>(3) an identical C profile: P1–P3 and S-RES;<br>(4) an executable decision path: R-TILE, R-W, R-GATE (branch-sensitive, with the fixed WF-X protocol), R-ALIAS, R-QUAL (with (d) over every mentioned unit, the parent specification and subunits), R-GLUE and D1–D5;<br>(5) predecessors: PP1–PP3;<br>(6) complete pins: §8.7;<br>(7) append-only: §9.3;<br>(8) the exact exception set: the boundary unchanged, no core unit newly Off, all units On (`UNANALYZED_BOUNDARY` unchanged);<br>(9) full evidence identity and strictness: the unchanged command and floor, zero unproved, justified and `pragma Assume`, complete reports, and source and library identities.<br>NOT_CLOSED (review); for the reviewer. |
| PACKET_PLAN | §9, carried with §9.4's effective line replaced (V-R9) and §9.6 as v4, plus A-BIND §B1.1 (v5, with W-A9). It keeps linear lineage, representation-packet discipline and an identities-only seal. NOT_CLOSED (review); for the reviewer. |
| ROOT_WORKER_INTEGRATION | OPEN; no ruling on the other lane or integration order (review). §19. |
| OB-048 | OPEN for the enlarged and pre-existing boundary (review). |

---

## 18. Everything that remains OPEN (REPLACED in v6)

- **Source and installed legality.**
  - No successor source exists.
  - Installed-tool SPARK legality of every changed unit (D-38), of the External abstract state, and of the `'Image` use.
  - Name and overload resolution in the integrated C_API body, including child-unit capture, and any warning on a transported clause (§3.6; A-BIND §B0.9).
  - The RM readings in R-QUAL's argument (A-BIND §B0.10 with W-A4 and W-A8): RM 8.4 (use clauses are not transitive; `use type` exposes operators only; a parent specification's use clauses reach its children), RM 10.1.2(5), (6/2) and (7), RM 10.1.1(11), RM 8.3(8) and RM A.1.
- **Proof.**
  - Flow, RTE, termination and functional obligations of the 95 new routines (J36) and of every called relation, including the N-03 callees, the D-05 decoders, the D-18 index and the D-19 branches.
  - Zero unproved, zero justified, zero `pragma Assume`; floor 251; complete reports and per-unit coverage.
  - Every strict warning class, including N-01's 736 representation warnings (J51). The 119 in moving code (J54) are not resolved by moving.
- **Manifest and composition.**
  - The override, tables and edits are unwritten. The tiles and the B8 sketch, including R-GATE with CR5 and CR6 and R-QUAL with CR3 and CR4, are author text that awaits review.
  - The author simulation is not a run of the manifest.
  - `CAPI_QUALIFIED`, `CAPI_QUALIFIER_EXCEPTIONS` and the B10.3 component lists are author-derived.
  - Pins are not regenerated, the mutation controls (§8.8, A-BIND §B12, including MX9–MX17 and MQ15–MQ24) are unrun as controls, and every stage review is pending.
- **ABI and native.**
  - Symbol export and mapping (D-15); layouts (D-34, N-01 evidence); calling conventions.
  - Write construction for every form (D-36).
  - Every native item of A-COST, including §C21-a…§C21-h.
  - The original native blockers (§11.5).
- **PK-0 characterization.** The class-H failure location and the copy atomicity of a write in progress (§9.6.4). Foreign faults and premise violations are outside the characterization (§9.6.5).
- **Controls.** The 52-action roster, the lifetime controls, all additive controls C-01…C-16, and the provider and fault campaigns on the exact integrated candidate.
- **Boundary.** OB-048, custody, producer authenticity, immutability premises (D-27) and foreign faults (D-23).
- **Integration.** The root-worker lane's changes to `core/worldline-c_api.adb`, and any change to `core/worldline.ads`, which (d) now reads (§19).
- **Operator.** D-13 before PK-7; N-06 at deployment; all original Phase One operator gates.
- **Reviews.**
  - The independent actual gpt-6.1-sol review of this design: V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE, and with them V4-RC4-GATE, V4-RC4-ALIAS, V3-RC4, R2_NINE_CONDITIONS and PACKET_PLAN; L13–L16; and the carried items.
  - The reviews of every packet and stage, and of the final composition.

---

## 19. Integration collision with the root-worker lane (v5 §19 carried; v6 supplement)

v5 §19 (v5 lines 332-339) is carried, and with it v4 §19, with X-R7 and X-R8 applied (L16). v6 adds:
- **Where the draft's renamings are (L16).** The draft's package renamings lie inside its nested `package body Child_Boundary` (draft lines 1198-2251), not at C_API body level, as the sealed seam v2 review also records (N-5). The v4 and v5 conclusions stand, because (d1), R-INV (ii) and R-RES do not depend on nesting depth (§A.3 L16; A-BIND MQ24).
- **(d) now also reads the parent specification `core/worldline.ads`.** A change the root-worker lane makes to that file must satisfy (d1)–(d4). A with clause that either lane adds to the C_API body must satisfy (d2).
- **The WF-X exception is fixed.** A rebase cannot add, relabel or move an assignment exception. Any acceptance object that the other lane brings into the C_API pair is an ordinary gate row.
- **A rebase needs new tables.** As in v5, `CAPI_QUALIFIED['RESIDUAL']` and the residual tables would have to be re-observed on the rebased base and reviewed, and so would the B9.4.7 context observations. They are never edited merely to fit (§9.1).
- The review's note that v4-labelled integration rules need reconciliation with v5's R-QUAL and repaired gate invariant in the eventual reviewed composition applies to v6's rules as well. v6 makes no ruling on the other lane or the integration order. The other lane's seam design drafts were not read for v6; for L16 only the root-worker source draft, at the lines cited, and the sealed seam v2 review's N-5 were read.

---

## Appendix A. JACKAL results and observed counts

**JACKAL calls.**
- J01–J68 are carried by reference: the v5 `jackal.json` (sha256 `612d189e4edc29cda39c8e61ac3668bf04adb6abcda12728f7ec14272d4f46d4`, 17950 bytes), with their uses as in v5 Appendix A (v5 lines 355-363).
- J69 is the only new call: `jackal_exact` with input `42+2`, returning `parsed=42+2` and `exact=44`, the number of B11 rows in v6 (A-BIND W-A16, W-A18).
- J69 returned `status=exact`, `formal=false`, lane `rat`, assurance "exact rational arithmetic (not yet checker-covered)", evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, and these non_claims, verbatim:
  - "NOT formal-bounded: this lane carries no Lean-checked certificate"
  - "The epistemic class above is the STRONGEST claim this result supports"
  - "exact rational arithmetic (not yet checker-covered)"
- `exact` is exact rational arithmetic outside the Lean certificate chain. It is not `formal-bounded`, and it is informational about code correctness only.
- No ledger was used as evidence.

**Observed counts carried from v5, v4 and v3.** v5 Appendix A's observed rows remain valid, since S5 is unchanged and was re-hashed. They are cited by reference (v5 lines 365-372), with v4's and v3's.

**v6 observations** (read-only scripts; not derived):
- The G21c exclusive region is 644 bytes of N1 text with sha256 `34b1492a5b5a757dab0cd1c62fcc241155be318e42a728da6649387d62c5b4d0`, which is item 5 of `CAPI_WFX_PROTOCOL`.
- Context clauses on N2: C_API specification, 4 with clauses naming 4 units and mentioning 5; C_API body, 23, 23 and 26; parent specification, 1, 1 and 2. (d2) refuses none.
- The parent specification declares `Hash` and `Zero_Hash` only; its only root is its own name; it has no use clause and no listed simple name.
- The S5 tree has 223 Ada source files with 123 distinct unit names, and their with clauses name 83 distinct units. None is refused by (d2), and none of the files contains `separate`.
- The v6 code block has 693 code lines and sha256 `e0360db00ee2c2316cb2bcfc56851816575267c101f3e938daffb3cb512fc081`; difflib against the v5 block reports 6 hunks, at the CR places.
- Simulation runs, counted by the script (AUTHOR-NOTES.md §4): 82 runs of the v5 mutations, 23 runs of the new ones, and 9 positive runs.
- The root-worker draft `RW/source/core/worldline-c_api.adb` still has sha256 `806f3972277d9385b0d32c5e3faf1bf6fb24f9024dbc1c8274411b8c1d0e3420` and 148068 bytes, as v4 recorded. Its renamings `Y` … `Q` are at lines 1199-1205 and 1217-1220, inside `package body Child_Boundary is` (line 1198) and `end Child_Boundary;` (line 2251).

## Appendix B. Bound inputs (sha256, read while drafting v6)

- **v3's list** (v3 decisions.json `bound_inputs`, 87 entries), **v4's additional inputs** (16) and **v5's additional inputs** (24, v5 Appendix B) were re-hashed by a read-only script while drafting v6. All matched.
- **Additional v6 inputs:**

```
533f0e043fb991d015bcf16494674d791b6f8f8bd5049fef5a8e60594c9341de  D5/DESIGN.md
a069632a035b62f18d886112763472f13040779d2d5dd79c872a6d6ce951c55b  D5/decisions.json
f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2  D5/APPENDIX-BINDINGS.md
612d189e4edc29cda39c8e61ac3668bf04adb6abcda12728f7ec14272d4f46d4  D5/jackal.json
ed45d1db766f3b03ec946946942a571ae50b0eae21e339c5724b5e2480280e47  D5/AUTHOR-NOTES.md
800880d44bff4b234c82cc392a3008fd4d37139b0827d070120cf299370f403b  D5/review/gpt61-v1/review.json
73e82489706e03ca465e7dea2aed1823df0b50a8ce1c5ab0555c545579dc34d8  D5/review/gpt61-v1/REVIEW.md
c1398253713aa6d42ed11fda5194502ccae5a64825b36ef8100206f7d40719ef  D5/review/gpt61-v1/checks.json
91bddf1a46763251940db658f5115cd13ab9de4aa67c0a41ae169de165649af1  D5/review/gpt61-v1/review-freeze.json
e86b9c32d6f0fd9fdc21192d5c7a43c15c3d2763c7dcdb9fabba5f392ee99252  W/work/claude-lead-isolation-v1/wt-1/deviations/capi-v5-author-process/NOTE.md
6b171d3fa0b9a0cdbd7e3777e4af35e557ed74e67f6b3ee9bdc1bbfe41305286  S5/core/worldline.ads
e88e6eaf916c9876b3dfb83b41c2113fdfdcfd9337b71ba06a4cfff4e4b3e296  ~/.claude/skills/ada-2005-amendment/chapters/ch08-program-structure.md
049066433c8f46b6ae3978eeeccf21a6c582ae233488c3ba81873f1a5fd5a64f  ~/.claude/skills/ada-2005-amendment/chapters/ch06-visibility-rules.md
4fd4eae2b1fcf5d6acead094f8b3ed4126cd703cd47467a617d653b42f8b808d  ~/.claude/skills/advanced-ada/chapters/ch14-packages.md
806f3972277d9385b0d32c5e3faf1bf6fb24f9024dbc1c8274411b8c1d0e3420  W/work/protected-original-root-worker-repair-v1/source/core/worldline-c_api.adb
84c176dfc3f2f49deb2a0967da90179ab1e80681e00fa33203a158066d01b942  W/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v2/review/gpt61-v1/review.json
```

- **The last two entries** were read for L16 only: the root-worker draft at its cited lines, and the sealed seam v2 review's finding N-5. The seam v3 design directory was not read.

- **The S5 tree observations** (A-BIND §B9.4.7) were made over the 223 Ada source files (`*.ads`, `*.adb`, recursively) of S5. The sha256 of their list, lines `sha256  <path relative to S5>` in path order joined by newlines with a final newline, is `8239e5ae7393f70ecff97e2352b69c8351f93de3fcae16b869c72a0e923628e2`.
- **The v5 renaming-graph sources** (the 69 S5 `core/*.ads` files) again give the list sha256 `e6276e7919d0bf39f41c696ec25e5c74c676d9c1e8ec3400763a2a7685a4a217`, with the lines in file-name order.
- **The lead's deviation notes** were re-read: `capi-v5-author-process/NOTE.md` (above) and `capi-v4-author-taskstop/NOTE.md` (`f5dada7c3ea424b8f404571cf5cfeef0ad7b2eb4f6a07634c6fd481e18e5a88b`, as in v5).

## Appendix C. REQUIRED_PROVED append, in packet order (98 names)

v5 Appendix C (v5 lines 410-412; sha256 in §B-v6.2) is carried verbatim, and with it v4's and v3's (v3 lines 2478-2589). The 535-name prefix is unchanged. The suffix has 98 names (J23) in packet order, and the final length is 633 (J20). R-QUAL's `CAPI_ROUTINE_NAMES` is exactly this list.

## Appendix D. Companion file identities

**How they were produced.** Each companion file was written with the Write and Edit tools to the location in the header. By last edit, they were completed in this order: `jackal.json`, `APPENDIX-BINDINGS.md`, `AUTHOR-NOTES.md`, then this file, then `decisions.json`. The identities below were observed with `sha256sum` and `wc -c` after each file's last edit.

**Where the rest are recorded.** `decisions.json` records this file's sha256, and its own identity is reported in the handoff. `APPENDIX-COST-MAP.md` is v4's, identified in the header.

| File | sha256 | Bytes |
|---|---|---|
| `APPENDIX-BINDINGS.md` | `9f9f3dfa897d0c320226df39c89bc5c156fc87ebc3e24959ab0c08bba5db1946` | 50088 |
| `jackal.json` | `34a7a3ab2c27552e94ce8a114119e4b14988bd03fafe3747b0bc3fec274a94de` | 3983 |
| `AUTHOR-NOTES.md` | `414fd7363ed415ce5dd5c2f1c675780bb5917e9e9a08bc5ab0751ae48ba2aa08` | 19208 |
