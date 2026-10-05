# C-API raw-pointer boundary consolidation: design v5

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent) |
| Date | 2026-10-04 to 2026-10-05 (session dates; drafting began on 2026-10-04) |
| Status | **DRAFT_FOR_GPT61_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author grants nothing, and no author check below is a review. |
| Supersedes | `W/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v4/`: `DESIGN.md` (sha256 `a9b5dcce5ca5808f8049ae8e7020a79c3fbfc33cc4dcbcc3706fd8f4f40fbfd6`, 97143 bytes), `decisions.json` (`59e71dd68724b0420b670d79a99ea74194134dbc6d219b7b91f146ad01843625`), `APPENDIX-BINDINGS.md` (`39ca995998d68b57d13c02796ee30d8826eecc07e750abf95a83f7d348f7d626`), `APPENDIX-COST-MAP.md` (`5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4`), `jackal.json` (`dec64a324685496195a7cb1c48e9ee3cf168255f8a1214d62b9491e42653f39d`), `AUTHOR-NOTES.md` (`ccac4f63a00ed36199642b8691535890719879187b135ecce69f67edc5214b07`). All six were read only and are unchanged (re-hashed while drafting). |
| Answers | The sealed actual gpt-6.1-sol review of v4 in `…/claude-capi-boundary-design-v4/review/gpt61-v1/`: `review.json` (sha256 `d7bf825a6c3d0da5f1b9302b64991d05759ae4754eb7347dcf187eb89b2e1f4e`), `REVIEW.md` (= its `report_sha256` `3d1ef7f82c2458f24ef9a8916e82db0d97c3e1730038cf20ac3d5e0e0323e4aa`), `checks.json` (`d70fe4677ae2159ad617a0dc6f9982fc976fd86b7d43f66dc9a3913e51e96963`) and `review-freeze.json` (`f1dcb0a77264dedd4c08be8b71ce390db66295cb25d1eb79eeb3701c7c0413dc`). Verdict ENDORSED_WITH_REQUIRED_CHANGES: V3-RC5 and V3-RC6 CLOSED_AT_DESIGN_LEVEL; V3-RC4 NOT_CLOSED; required changes **V4-RC4-GATE** and **V4-RC4-ALIAS**. |
| Scope | Proof-source design only. It grants no execution, proof, build, test, review, operator or acceptance authority. |
| Location | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v5/` |
| **What this document consists of** | The v5 design is: (1) the text of this file; (2) the v4 `DESIGN.md` line ranges listed in §B-v5.2 as CARRIED_VERBATIM or CARRIED_WITH_LINE_REPLACEMENTS, each bound by the sha256 of its exact bytes, with the line replacements V-R1–V-R8 of §B-v5.4 applied; and (3) through the carried v4 §B, the v3 `DESIGN.md` slices that v4 carries, with v4's replacements R1–R15 and v5's replacement V-R9. Both earlier files are read only and pinned. No other v4 or v3 text is part of v5. |
| Companion files | `APPENDIX-BINDINGS.md`: A-BIND v5, a delta over v4 A-BIND bound in the same way. `APPENDIX-COST-MAP.md` is **not** reissued: A-COST v4 is carried unchanged by reference (V3-RC6 is closed at design level), and "A-COST" means that file. `decisions.json` is the machine twin. `jackal.json` records every JACKAL call. `AUTHOR-NOTES.md` holds unresolved items, uncertainties, reviewer guidance and the process record. Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools, and no Write or Edit was refused. Bash was used for read-only inspection, with one disclosed slip (AUTHOR-NOTES.md §5). |

---

## A. Closure tables: V4-RC4-GATE and V4-RC4-ALIAS

Each sub-requirement is quoted from the sealed `review.json` `required_changes` (`change`, or `reason` where marked). "Answer" names what v5 supplies. Every answer is a design statement for the reviewer. None is closed by the author, and every proof, native, control and acceptance obligation stays OPEN.

### A.1 V4-RC4-GATE: one branch-sensitive gate rule everywhere

| # | Sub-requirement (review text) | v5 answer | Where |
|---|---|---|---|
| G.1 | "Reconcile normative B0.7, DESIGN 8.4, B4 tiles, B8 gate algorithm, B10 gate rows, B11 promises, mutation specifications and the machine twin" | R-GATE v5 is stated once, normatively, in A-BIND §B0.7, and every other place now states the same rule:<br>- DESIGN §8.4 bullets (V-R4) and the §8.4.1 O5 row (V-R5).<br>- The B4 tiles are unchanged: they already satisfy the rule, as the author simulation confirms (AUTHOR-NOTES §4).<br>- B8: `_capi_gate_problems` with `_capi_gate_row_problems` and `_capi_exclusive` (BR7), `CAPI_GATE_FORMS` (BR4), and `CAPI_GATES` with kind and components and `CAPI_GATE_EXCLUSIVE` (BR3).<br>- B10.3: each row now has its kind and its components by branch.<br>- B11: rows 7 and 14 restated, row 41 added.<br>- B12: mutations MG1–MG12 and MX1–MX8.<br>- decisions.json: `RC4-GATES-V5`. | A-BIND §B0.7, §B8.1, §B10.3, §B11, §B12; §8.4 (V-R4, V-R5); decisions.json |
| G.2 | "State branch-sensitive payload rules that permit the existing False-variant rejection diagnostic after its discriminant test" | **Kind `bool`.** A component of the `False` variant may be selected only inside the rejection branch: after `if not N.Ok then`, before the `return` that ends the branch. So G16a's original `Diagnostic_Transport.Value ("completion.context.field-rejected", FA.Rejected_Position);` is permitted, and the same selection on the accepted path is refused (MG1). `True` components may be selected only after the gate (MG2).<br>**Kind `case` (G16b).** Each component may be selected only inside the alternative that lists it: `RA.Rejected_Field_Position` in `Row_Field_Rejected`; `RA.Row` and `RA.Joined` in `Row_Accepted`; nothing after `end case;` (MG7–MG10). | A-BIND §B0.7, §B10.3 |
| G.3 | "State the sole WF-X finalization O assignment exception with exact exclusive assignments before its test" | **Kind `wfx` (G21c only).** `CAPI_GATE_EXCLUSIVE` gives the exact declaration (`O : Evaluation_Finalization_C.Decide_Acceptance;`, no initializer), the exact region (the §5.1 `if … else … end if;`), and the exact then- and else-assignments.<br>The rule requires:<br>- exactly two assignments, at exactly those places;<br>- a region that is one if statement with no `elsif` and no conditional expression;<br>- the then-assignment as the last statement of the then branch, and the else-assignment as the whole else branch;<br>- the test immediately after the region's `end if;`;<br>- no other use of `O` before the test, and `O.Value` only after it.<br>Every other acceptance object is never assigned, passed whole or renamed. G21c's gate text now begins at the then-assignment (MX1–MX8). | A-BIND §B0.7, §B10.3 |
| G.4 | "Preserve A1, diagnostics, codes, write order and the accepted domain" | **Carried unchanged by hash:** the tiles of B4 (every guard, read, diagnostic site, refusal code, write and handler), the site sequences of B6, the write rows W03–W22 of B10.2 and the read frontiers of §9.6.<br>**A1** is enforced as branch-correct domination (RR-V4).<br>No diagnostic is deleted or moved, and no refusal is added. R-GATE refuses successor text, never an input. | A-BIND §V.2; §B-v5.2; §B-v5.3 |
| G.5 | (reason) "B0.7 requires every non-discriminant selection after the entire gate and forbids every acceptance-object assignment … B8 implements the different after-test/assigned-exception rule. These are contradictory normative specifications" | Both v4 statements are withdrawn and replaced by one rule.<br>v4's B8 rule was also not branch-correct (latent defect L10): it accepted a `False` component on the accepted path, and a component in the wrong case alternative.<br>v4's completeness check missed `X.Verdict` uses outside `case` and objects that are never tested (L12). | §A.3; A-BIND §B0.7 |

### A.2 V4-RC4-ALIAS: the exact per-call expanded-qualifier invariant

| # | Sub-requirement (review text) | v5 answer | Where |
|---|---|---|---|
| Q.1 | "Complete the fully expanded naming invariant for indirect package paths admitted by the scoped inventory, including F.P.Decide and paths through the transport package qualifier" | **R-QUAL** (new). Every dotted name whose last selector is an Appendix C routine name (and, from PK-6b, a removed routine name) must, scope by scope, match `CAPI_QUALIFIED` exactly. Each listed text is either a full expanded name or a listed, scoped exception that denotes another entity.<br>The following are therefore refused, without resolving them:<br>- `F.P.Decide` and every other renaming path in the 80-path inventory (71 of which v4 missed: J65, J66);<br>- transport-qualified paths (`Pending_Transport.E.Decide`) and `C_API`- or `Worldline.C_API`-qualified paths;<br>- parent-visibility shortenings (`Recovery_C_API.Present`);<br>- library-unit paths (`Evaluation_Completion.P.Decide`);<br>- `Standard.` prefixes. | A-BIND §B0.10, §B9.4.4, §B9.4.5 |
| Q.2 | "Define deterministic path-aware exclusion or an exact per-call expanded-qualifier invariant" | v5 takes the second option, an **exact per-call expanded-qualifier invariant**.<br>(a) The exact per-scope multisets of qualified routine names (`CAPI_QUALIFIED`), each entry a full expanded name or one of the nine scoped exceptions (`CAPI_QUALIFIER_EXCEPTIONS`, each with what it denotes).<br>(b) No selection from a non-name prefix.<br>(c) No attribute of a full expanded name.<br>(d) No capture of a full expanded name's first identifier, whether by a declaration in the C_API pair or through a `with` clause.<br>It is deterministic: text comparison on N2, with no name resolution. | A-BIND §B0.10, §B8.1 (BR2, BR4, BR6), §B9.4 |
| Q.3 | "specify matching indirect-path mutation controls" | B12 R-QUAL mutations MQ1–MQ14 cover renaming paths, deeper paths, transport-qualified and `C_API`-qualified paths, parent shortening, `Standard.`, residual paths, library-unit paths, a non-name prefix, an attribute, capture by a declaration and through a `with` clause, a removed routine, and an exception outside its scope. B12 also gives R-INV (vii) mutations MV1–MV4, R-ALIAS MA1, and the L9 positive control. | A-BIND §B12 |
| Q.4 | "Do not weaken V7/O6(a) or relax the scoped inventory" | **Unchanged:** R-INV (i)–(vi), and the B9.1 and B9.2 tuples. The V7 text is carried unchanged.<br>**Strengthened:** R-INV (vii) is now a path-independent whitelist (A-R2; latent defect L11).<br>**R-ALIAS:** patterns unchanged, and kept as a named subset of R-QUAL. Only its staging changes, to stop refusing the unchanged S5 residual at PK-1…PK-5 (L9). No refusal of designed text is removed.<br>**O6 (a)** is now enforced by R-QUAL. | A-BIND §B0.4 (A-R2), §B0.5, §B1.1 |
| Q.5 | (reason) "the claimed independent invariant for later reviewed tile amendments is stronger than this checking specification" | v4's sentence "the only way left to denote an Appendix C routine is its full expanded name" is withdrawn as a consequence of R-ALIAS. R-QUAL's own argument supports it at text level (A-BIND §B0.10, "Why this closes O6 (a) at text level").<br>Because R-QUAL validates its own table entries, an amendment that adds an indirect spelling to both a tile and the table is still refused: the *amendment* mutations of B12 were simulated. Installed name resolution remains OPEN (D-38). | A-BIND §B0.5, §B0.10, §B8.3 |

### A.3 Latent v4 defects found while drafting v5 (author's observations, not review findings)

| # | Defect | v5 correction |
|---|---|---|
| L9 | v4 defined the `K.` pairs of the removed routines in `CAPI_ALIAS_FORBIDDEN` at PK-1 (v4 A-BIND §B1.1). The unchanged S5 residual contains `K.Raw_Decide`, `K.Context_Matches`, `K.Metadata_Base` and `K.Metadata_Matches` (`core/worldline-c_api.adb:784-870`) until GE1–GE8 at PK-6b. So v4's R-ALIAS would have refused every faithful PK-1…PK-5 successor. The author simulation of v4's table on the assembled PK-1 text reported exactly those four selections. | Those pairs are appended at PK-6b, with GE1–GE8 (A-BIND §B0.5, §B1.1). |
| L10 | v4's B8 `_capi_gate_problems` accepted any component selection after the discriminant test. It would therefore have accepted `FA.Rejected_Position` on the accepted path, `RA.Row` in `Row_Rejected`, and a selection after `end case;`. v4's B0.7 also accepted the last two. | Branch-sensitive R-GATE (§A.1). |
| L11 | v4's R-INV (vii) compared the names in a use clause with unit names and single renaming aliases only. `use F.P;`, `use Completion_Transport.P;` or `use Recovery_C_API;` would therefore have passed (vii); only R-INV (i) refused them, as unlisted clauses. | A path-independent whitelist (A-R2, BR5). |
| L12 | v4's R-GATE completeness check matched only `X.Ok` and `case X.Verdict is`. An `X.Verdict` used otherwise, or an acceptance object that is never tested, escaped it. | Completeness by every `X.Ok` and `X.Verdict` selection, and by every `…_Acceptance` declaration (A-BIND §B0.7). |

---

## B. Carried forward (v5)

### B-v5.1 Items the v4 review closed, preserved or accepted, carried unchanged

The ruling column quotes the sealed v4 review (its `rulings`, `rc_closure` and `latent_defects`), or its leading clause.

| Item | v4 review ruling | v5 |
|---|---|---|
| RC1 | CLOSED_AT_DESIGN_LEVEL preserved; diagnostic state/control/value logic stays in SPARK and the carried transport tiles are identical | Carried: v4 §4 (with v3 §4.1–§4.8 and §4.10), A-BIND B4.19, B4.24 and B6, all bound by hash. |
| RC2 | CLOSED_AT_DESIGN_LEVEL preserved; Operations 0/1 do not read or pass Captured, while the original allocation is retained | Carried: v3 §5 through v4 §5–6, and B4.20 segment 6 unchanged. The WF-X statement is now exact; this is not a design change. |
| RC3 | CLOSED_AT_DESIGN_LEVEL preserved for the N-01 resolution discipline | Carried: v3 §10 through v4 §10. |
| LD1 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL preserved | Carried. |
| LD2 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL preserved; no new transport-facing Pre or functional Post | Carried. A1 is enforced by R-GATE v5 (RR-V4). |
| LD3 | CONDITIONALLY_ACCEPTABLE_PENDING_D-13 preserved | Carried. |
| LD4 | WITHDRAWN preserved | Carried. |
| LD4-R | CLOSED_AT_DESIGN_LEVEL for RC1 preserved | Carried. |
| LD5 | CONDITIONALLY_ACCEPTABLE preserved | Carried. |
| LD6 | CONDITIONALLY_ACCEPTABLE preserved; its V3-RC5 design condition is now discharged at design level | Carried. |
| V3-RC5 | CLOSED_AT_DESIGN_LEVEL | Carried: v4 §9.6, and §15 with R13–R15. |
| V3-RC6 | CLOSED_AT_DESIGN_LEVEL | Carried: A-COST v4 unchanged by reference; v4 §3.4, §4.9 and §11. |
| L1–L8 | GENUINE, all eight. L1, L2, L4, L6, L7 and L8: REPAIRED_AT_DESIGN_LEVEL. L3: "GE9 is a correct design repair", with actual GNAT 16.1.0 warning behaviour UNVERIFIED. L5: repaired, but "Separate new B0.7 gating contradiction remains RC4". | The repairs are carried by hash: A-BIND B0.4, B2.3, B9.2, the B4.17 tile, the B10 rows and the B8 P2 pattern; v4 §9.6.6 and §15. The gate part of L5 is answered in §A.1. |
| APPENDIX_C | CLOSED_AT_DESIGN_LEVEL for exact append-only ordering/enrollment preserved | Carried: v4 lines 848-850, which carry v3 lines 2478-2589. The 535-name prefix, the 98-name suffix and the final length 633 (J20) are unchanged. |
| D-13 | OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE. "The reservation concerns concrete component transport/library architecture, not editing pinned files or recomputing pins." | Carried: v3 §16.1. The clarification is adopted as stated. The operator chooses the concrete component transport and library architecture. Edits to pinned files and recomputed effective pins follow HANDOFF acceptance-sequence item 1 (explicit, independently reviewed deltas) and are not operator-reserved. No choice is made here, and options (ii) and (iii) remain inadmissible. |
| N-06 | REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT preserved | Carried: v3 §16.2. No deployment action. |
| N-01 | LEAD_OWNED_STRICT_OBLIGATION preserved | Carried: v3 §10. |
| D-05 | OPEN preserved | Carried. |
| D-18 | CLOSED_AT_DESIGN_LEVEL for the index design preserved; proof remains OPEN | Carried. |
| D-19 | OPEN preserved | Carried. |
| D-28 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL preserved | Carried. |
| D-36 | OPEN for every write form | Carried. |
| D-15/D-34/D-38 | OPEN preserved | Carried. R-QUAL adds no claim about installed name resolution. |
| N-03, N-05 | OPEN preserved | Carried. |
| N-04, N-07 | CLOSED_AT_DESIGN_LEVEL … preserved | Carried. |
| R2_NINE_CONDITIONS | NOT_CLOSED pending V3-RC4; the normative gate and indirect naming invariants require reconciliation | §17 (v5). For the reviewer. |
| PACKET_PLAN | NOT_CLOSED pending V3-RC4 | §17 (v5). For the reviewer. |

**Unchanged fixed targets**, as in v4:
- `MINIMUM_CHECKS = 251`;
- the 535-name ordered `REQUIRED_PROVED` prefix, append-only;
- `UNANALYZED_BOUNDARY == {"worldline-c_api"}`;
- 169 effective `CONTRACT_PINS` keys at L0;
- both builds;
- every checked assertion.

**Nothing weakened.** No cap, new public Pre, refusal relabelling, suppression, warning waiver, `pragma Assume`, new Off exception or ABI narrowing is introduced. No transport code, meaning, layout or caller protocol changes. v5 changes rule, check, table and promise text only.

### B-v5.2 Disposition of every v4 `DESIGN.md` section

"v4 lines" are 1-based lines of the v4 file. The sha256 is that of the UTF-8 bytes of those lines, each followed by `\n` (observed by a read-only script).

| v4 section | v4 lines | sha256 of the v4 slice | Disposition | v5 location |
|---|---|---|---|---|
| Header | 1-14 | — | REPLACED | header above |
| §A Closure table for V3-RC4/5/6 and latent defects L1–L8 | 18-71 | `e431f6d450d8b93cb2c6d5ba900ee29407cb27bdf0b2aaa15171f35ade293bed` | CARRIED_VERBATIM as history (RR-V5) | v4 §A |
| §B Carried forward: v4's composition over v3, with replacements R1–R15 | 75-266 | `f743e0b189eaaaa5e120c196ec5cde9f585ec405f16e3cfa312f277f87ab9e6f` | CARRIED_VERBATIM; v3:1931 further replaced by V-R9 | v4 §B |
| §0 Truth boundary (v4 supplement) | 270-298 | `19f6559c98f31ffc37244511554783aceafbfb71d78f184ef01069983e80fd5d` | CARRIED_VERBATIM as v4's record, with the v5 supplement | §0 |
| §1, §2 | 302-304 | `b9adec269b9f48a2cd60be79ab3cfba8ae25c6bb69d2dd93da3c6debd925f854` | CARRIED_VERBATIM | — |
| §3 (§3.4, §3.6) | 308-372 | `36701578f9dc89fef175a1ad80725a4f8aae362b61d02141894a3b038a0cc3a9` | CARRIED_VERBATIM | — |
| §4 (§4.9) | 376-391 | `d392149c3d5671cd048a5fb546f6b1385058805a274fa310b0757a529c35502c` | CARRIED_VERBATIM | — |
| §5, §6 | 395-397 | `c43c64ff716d61c55eb85aff7cbcd62850338421d16c791adc6b40e69869f939` | CARRIED_VERBATIM | — |
| §7 | 401-403 | `44369d5d8558c58db9c3d2367c3485916ecccf930808833acdc701f924670bc6` | CARRIED_VERBATIM | — |
| §8 heading and §8.1 | 407-425 | `2eb54fafe287f1df395ba936f0fc04e51198befdc380b324fd0e8e9c850baa63` | CARRIED_WITH_LINE_REPLACEMENTS (V-R1, v4:422) | §B-v5.4 |
| §8.2, §8.3 | 427-446 | `84d501a70d16ee4e7d9aaff909f5711f9a3322a50c75991d1fcce49cf68a2e5b` | CARRIED_VERBATIM | — |
| §8.4, §8.4.1 | 448-506 | `d72122582db0678307cd496bd29a51ee2c4a84d3bd12023e29cafa761f4ff177` | CARRIED_WITH_LINE_REPLACEMENTS (V-R2 v4:469, V-R3 v4:472, V-R4 v4:479-484, V-R5 v4:500, V-R6 v4:501, V-R7 v4:504) | §B-v5.4 |
| §8.5–§8.7 | 508-510 | `3585ce95bac94ef1042c84163e438a13c1d33b278634afe058b9c47cb365555d` | CARRIED_VERBATIM | — |
| §8.8 | 512-522 | `1a6a6787ec5e93ef4a7733c29339a1f773e727c5e4206d86301c559dce90ec7d` | CARRIED_WITH_LINE_REPLACEMENTS (V-R8, v4:522) | §B-v5.4 |
| §8.9 | 524-526 | `fc3e348d965ec41f448e07e7c287351c1f7a98f757db1bab74cbc3971bbe2b36` | CARRIED_VERBATIM | — |
| §9 (§9.6) | 530-629 | `2aa0d9f9951a81bb064227c69235bb647876c0fd832242a224178cb83c5157c0` | CARRIED_VERBATIM (§9.4's effective line replaced by V-R9) | §B-v5.4 |
| §10 | 633-635 | `e57638c3186fe2df162de519bec392879770eb33f698ed1da9eaf74a4230c9fd` | CARRIED_VERBATIM | — |
| §11 | 639-704 | `e081b5163fe555af2804641161b7b894a680c9e198148fdac1472215193d98b0` | CARRIED_VERBATIM | — |
| §12–§16 | 708-710 | `f519786b774b7526f7701a4cb0146873dd3aaf8e914bc956bde88372b27d7666` | CARRIED_VERBATIM | — |
| §17 Rulings and carried items | 714-737 | — | REPLACED | §17 |
| §18 Everything OPEN | 741-764 | — | REPLACED | §18 |
| §19 Root-worker collision | 768-782 | `778557618deaa660ecd87c44ff657354b32885c2ed1ba9b9b23359d2a23abdc4` | CARRIED_VERBATIM, with the v5 supplement | §19 |
| Appendix A JACKAL and observed counts | 786-820 | — | REPLACED | Appendix A |
| Appendix B Bound inputs | 822-846 | — | REPLACED | Appendix B |
| Appendix C REQUIRED_PROVED append | 848-850 | `b84beecb0360a9cb2d09e9b780a8a6b49bd95ba2502c57579a0ff217b986e2d6` | CARRIED_VERBATIM | Appendix C |
| Appendix D Companion identities | 852-861 | — | REPLACED | Appendix D |

### B-v5.3 Reading rules for carried text

- **RR-V1.** Carried v4 text that states the design's current state ("v4 replaces", "in v4") states the v5 state, unless this file or A-BIND v5 replaces it.
- **RR-V2.** "JACKAL Jnn" in carried v4 or v3 text means call Jnn of the v5 `jackal.json`. v5 re-ran J01–J58 with the v4 inputs and obtained the same values. J59–J68 are new.
- **RR-V3.** "A-BIND §Bn" in carried text means A-BIND v5: the v5 appendix together with the v4 slices it carries. "A-COST" means the v4 `APPENDIX-COST-MAP.md`, carried unchanged.
- **RR-V4.** A1 (v3 §3.2 V4, carried) reads: "the transport tests the discriminant (`if not D.Ok then return <original code>; end if;` or `case D.Verdict`) before reading any payload component." R-GATE v5 enforces it as written:
  - the test precedes every component read;
  - each component is read only on a path where the test established its variant;
  - a rejection branch may carry the original diagnostics before its `return` (A-BIND §B0.7).

  A1's text is unchanged.
- **RR-V5.** v4 §A is v4's answer to the v3 review, carried as history. Its rows 4.2, 4.4 and 4.5 stated R-ALIAS as completing O6 (a), and R-GATE as v4 stated it. They are superseded by §A.1 and §A.2 here.
- **RR-V6.** v4 §0 and the v4 AUTHOR-NOTES describe v4's drafting, including the v4 TaskStop event. v5's process record is the §0 supplement below and the v5 AUTHOR-NOTES.
- **RR-V7.** References in carried text to §17, §18 and Appendices A, B and D resolve to the v5 replacements in this file.

### B-v5.4 Line replacements in carried slices

Each item quotes the exact v4 lines (or the exact effective line) and gives the v5 lines that replace them. Nothing else in the slice changes.

**V-R1 (v4:422, §8.1; tables).**
```text
v4:
- **Rule tables:** `CAPI_ALIAS_FORBIDDEN`, `CAPI_SPARK_UNITS`, `CAPI_WRITES`, `CAPI_GATES`, `CAPI_GATE_ASSIGNED`, `CAPI_DIAGNOSTIC_SITES` (from PK-6b).
v5:
- **Rule tables:** `CAPI_ALIAS_FORBIDDEN` (its `K.` pairs of removed names from PK-6b), `CAPI_SPARK_UNITS`, `CAPI_USE_PACKAGES`, `CAPI_ROUTINE_NAMES`, `CAPI_REMOVED_NAMES` (from PK-6b), `CAPI_QUALIFIED`, `CAPI_QUALIFIER_EXCEPTIONS`, `CAPI_WRITES`, `CAPI_GATES` (with kind and components by branch), `CAPI_GATE_EXCLUSIVE` (from PK-6b; replaces `CAPI_GATE_ASSIGNED`), `CAPI_DIAGNOSTIC_SITES` (from PK-6b).
```

**V-R2 (v4:469, §8.4 R-INV (vii); V4-RC4-ALIAS).**
```text
v4:
  - (vii) No `use` clause names a SPARK unit or a renaming of one.
v5:
  - (vii) The only use clauses other than `use type` clauses are `use <T>;` for a unit transport `T` and `use System.Storage_Elements;`, compared as exact text. So no use clause names a SPARK unit, a renaming of one, or any path to one, whatever the path resolves to (A-BIND §B0.4, A-R2).
```

**V-R3 (v4:472, §8.4 R-ALIAS; V4-RC4-ALIAS).**
```text
v4:
- **R-ALIAS (makes O6 (a) enforceable).** None of the listed `(alias, routine)` selections occurs, for example `K.Diagnostic_Start` or `E.Decide`. With R-INV (v)–(vii), the only way left to denote an Appendix C routine is its full expanded name (A-BIND §B0.5, §B9.4).
v5:
- **R-ALIAS (kept as a named subset of R-QUAL).** None of the listed single-renaming selections `(alias, routine)` occurs, for example `K.Diagnostic_Start` or `E.Decide`. The `K.` pairs of the nine removed routines are appended at PK-6b with GE1–GE8, not at PK-1 (§A.3 L9). v4's conclusion that R-ALIAS leaves the full expanded name as the only denotation is withdrawn: its patterns do not see indirect or qualified paths such as `F.P.Decide` (A-BIND §B0.5, §B9.4.6).
- **R-QUAL (new in v5: the exact per-call expanded-qualifier invariant of V7 and O6 (a)).** On the whole C_API pair, the dotted names whose last selector is an Appendix C routine name (and, from PK-6b, a removed routine name) are counted per scope, case-insensitively. Each scope's multiset must equal `CAPI_QUALIFIED` exactly. Every listed text is either a full expanded name of `CAPI_ROUTINE_NAMES`, or one of the nine listed exceptions, each of which denotes another entity and has its scopes. In addition, no such name is selected from a non-name prefix; no full expanded name is the prefix of an attribute; the first identifier of a full expanded name is never declared or used alone outside the context clause; and no `with` clause names a unit that could capture that identifier. So every indirect, transport-qualified, `C_API`-qualified, parent-shortened, library-unit or `Standard`-prefixed spelling is refused without resolving the path (A-BIND §B0.10, §B9.4).
```

**V-R4 (v4:479-484, §8.4 R-GATE; V4-RC4-GATE).**
```text
v4:
- **R-GATE (replaces v3 O5 and A1 by order).** For every acceptance object:
  - its gate text occurs exactly once;
  - its discriminant (`.Ok` or `.Verdict`) is selected exactly once in the scope, inside the gate;
  - no other selection precedes that test;
  - the object is never assigned, except finalization `O`, whose assignments R-W binds (A-BIND §B0.7, §B10.3);
  - completeness: every `X.Ok` and `case X.Verdict is` in a designed scope belongs to an object with a gate row there.
v5:
- **R-GATE (v5: branch-sensitive; replaces v4's statement and v3 O5).** For every acceptance object of `CAPI_GATES`, of kind `bool`, `case` or `wfx` (A-BIND §B0.7, §B10.3):
  - its gate text has its kind's exact form and occurs exactly once; the object is declared once, and its discriminant (`.Ok` or `.Verdict`) is selected exactly once in the scope, inside the gate;
  - every other occurrence of the object is a listed component selection where that component's variant is established: for `bool`, `False`-variant components only inside the rejection branch (after the test, before its `return`), which keeps G16a's original diagnostic `FA.Rejected_Position`, and `True`-variant components only after the gate; for `case`, each component only inside an alternative that lists it; for `wfx`, `O.Value` only after the gate;
  - no acceptance object is assigned, passed whole or renamed, with one exception: finalization `O` (`wfx`, G21c), declared without an initializer and assigned exactly twice, as the last statement of the then branch and as the whole else branch of the one `if Evaluation_Finalization_C.Needs_Rows (X) then … else … end if;` (no `elsif`), which its test immediately follows (`CAPI_GATE_EXCLUSIVE`; R-W row W21 binds the same count);
  - completeness: every `X.Ok` and `X.Verdict` selection, and every object declared with an `…_Acceptance` subtype, in a designed scope belongs to an object with a gate row there.
```

**V-R5 (v4:500, §8.4.1 O5 row).**
```text
v4:
| O5 gating (discriminant test after the declaration, at most `begin` between) | R-GATE: exact gate text; the test occurs once, inside the gate; no earlier payload selection | Makes A1 enforceable |
v5:
| O5 gating (discriminant test after the declaration, at most `begin` between) | R-GATE (v5): the exact gate form per kind; the test occurs once, inside the gate; each component selected only where its variant is established (`False` components inside the rejection branch, `True` components after the gate, case components inside their alternative); the sole WF-X exception stated exactly | Makes A1 enforceable, branch-correctly (V4-RC4-GATE) |
```

**V-R6 (v4:501, §8.4.1 O6 (a) row).**
```text
v4:
| O6 (a) full expanded names | R-ALIAS with R-INV (v)–(vii), plus R-TILE | Was enforced by tokens only |
v5:
| O6 (a) full expanded names | R-QUAL (exact per-scope expanded qualifiers, no non-name prefix, no attribute of a routine, no capture of a full expanded name) with R-INV (v) and (vii) (v5), plus R-TILE; R-ALIAS kept as a named subset | Was enforced by tokens only; v4's R-ALIAS missed indirect paths (V4-RC4-ALIAS) |
```

**V-R7 (v4:504, §8.4.1 O7 row).**
```text
v4:
| O7 retargeting | R-GLUE and R-RES (exact edits; whole-residual identity) and R-ALIAS (no `K.` call of a removed or Appendix C routine) | — |
v5:
| O7 retargeting | R-GLUE and R-RES (exact edits; whole-residual identity), R-ALIAS (no `K.` call of an Appendix C routine; of a removed routine from PK-6b) and R-QUAL (from PK-6b, no dotted name of a removed routine except the listed `Completion_Transport` subprograms) | — |
```

**V-R8 (v4:522, §8.8 mutation row).**
```text
v4:
| v4 rules | A-BIND §B12, which covers R-TILE, R-TRANS, R-INV, R-ALIAS, R-W, R-GATE, R-RES, R-GLUE, R-LAYOUT, K3, K5, G9 and K6 |
v5:
| v5 rules | A-BIND §B12 (v5), which covers R-TILE, R-TRANS, R-INV (with the path-independent (vii)), R-ALIAS, R-QUAL, R-W, R-GATE (with the `False`-variant, case-alternative and WF-X mutations), R-RES, R-GLUE, R-LAYOUT, K3, K5, G9 and K6 |
```

**V-R9 (effective v3:1931, §9.4, as replaced by v4 R12; R-QUAL joins every stage).**
```text
v4:
- Every stage enforces G1–G10, K1–K5 (K6 from PK-7), P1–P3, R-TILE, R-TRANS, R-INV, R-ALIAS, R-W, R-GATE, R-RES, S-RES, R-LAYOUT and R-GLUE for the units bound so far (§8, A-BIND §B1.1), and from PK-6b also D1–D5.
v5:
- Every stage enforces G1–G10, K1–K5 (K6 from PK-7), P1–P3, R-TILE, R-TRANS, R-INV, R-ALIAS, R-QUAL, R-W, R-GATE, R-RES, S-RES, R-LAYOUT and R-GLUE for the units bound so far (§8, A-BIND §B1.1), and from PK-6b also D1–D5.
```

---

## 0. Truth boundary (v4 §0 carried; v5 supplement)

v4 §0 (v4 lines 270-298) is carried verbatim as v4's record. That includes v3 §0 and v4's process event. The following supplements it for v5.

**What was executed while drafting v5.** Only read-only inspection, and one author simulation:
- **Bash** was used to read files and print. Commands outside the brief's literal list (`head`, `tail`, `cut`, `awk`, `printf`, `echo`, `cd`, `for` loops) and one slip, a command prefixed by `mkdir -p /dev/null 2>/dev/null` that created nothing, are reported in AUTHOR-NOTES.md §5. No file was created, moved, copied, deleted or changed with Bash or Python, and no output was redirected to a file.
- **The author simulation** (A-BIND §B8.0). A read-only Python script reconstructed the v5 B8 sketch from the v4 code and BR1–BR8. It executed the sketch's definitions in memory, with `normalized_ada` reimplemented and stubs for the manifest functions, on successor texts assembled in memory. It printed only results.
  - This executed the design's own sketch text, not WORLDLINE code. No WORLDLINE module was imported, and `proof_manifest.py` was read as text only.
  - v4's sketch was never executed. That difference is disclosed so that the lead can judge it.
- **Not run:** no compiler, prover, gprbuild, gnatprove, test, service, project-vault or restic.
- **No interruption.** No TaskStop, kill or `timeout` wrapper was used, and no command hung.
- **SIA.** One `sia.ask` call was made, late in the drafting, and its answer was not used (AUTHOR-NOTES.md §5). No SIA note was written.

**Additional bases.**
- `D4` = `W/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v4`.
- `R4` = `D4/review/gpt61-v1`, the sealed review; its identities are in the header.

**v5 numbers.**
- Every derived number in v5 and its appendix is one of the JACKAL `jackal_exact` calls J01–J68 recorded in `jackal.json`.
- Each returned `status=exact`, `formal=false`, lane `rat`, evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, and the three non_claims quoted in Appendix A.
- J01–J58 re-run v4's calls with the same inputs and gave the same values.
- Counts read from files or tool output by a script are reported as observed.

**Author checks are not review.** v5 cites read-only author scripts:
- the carried-slice hashes and quotes;
- the B8 reconstruction, its syntax parse and its diff against v4;
- the simulation and its mutations;
- the Appendix C, gate and renaming-graph scans;
- the bound-input re-hashes.

They are self-checks by the author. They grant nothing, and they do not substitute for the required independent actual gpt-6.1-sol review.

---

## 17. Rulings and carried items (REPLACED in v5)

| Item | v5 disposition |
|---|---|
| V4-RC4-GATE | Answered in §A.1 (A-BIND §B0.7, §B8.1, §B10.3, §B11, §B12). For the reviewer; NOT_CLOSED until reviewed. |
| V4-RC4-ALIAS | Answered in §A.2 (A-BIND §B0.4 A-R2, §B0.5, §B0.10, §B9.4, §B12). For the reviewer; NOT_CLOSED until reviewed. |
| V3-RC4 | NOT_CLOSED (review). Its two remaining required changes are answered above. For the reviewer. |
| V3-RC5, V3-RC6 | CLOSED_AT_DESIGN_LEVEL (review). Carried unchanged (§B-v5.1). |
| RC1, RC2, RC3, LD1–LD6, LD4-R, APPENDIX_C, L1–L8 | As the review ruled. Carried unchanged (§B-v5.1). |
| D-01 … D-04, D-06 … D-12, D-14, D-17, D-20 … D-27, D-29 … D-33, D-35, D-37 | Carried from v3 (v3:2281) through v4, unchanged in substance. Each stays OPEN where v3 said OPEN. |
| D-05 | OPEN (review). Contextual proof is required at every original partial-decoder caller, or a separately reviewed non-narrowing total restructure. No helper Pre is approved. |
| D-13 | OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE. The reservation concerns the concrete component transport and library architecture, not editing pinned files or recomputing pins (review). Operator item §16.1; no choice is made. |
| D-15, D-34, D-38 | OPEN: matching native export, layout and loaded-library evidence; installed-tool legality, including name resolution in the integrated body (§3.6); any warning on a transported clause (A-BIND §B0.9); and the RM 8.4 readings that R-QUAL's argument uses (A-BIND §B0.10). |
| D-16 | Withdrawn with LD4; replaced by LD4-R (§4). |
| D-18 | CLOSED_AT_DESIGN_LEVEL for the index design (review); proof OPEN (§5.4). |
| D-19 | OPEN (§5.5). |
| D-21 | The pre-existing `Authority_Glue` value decisions are unchanged and enforced by R-RES; they are boundary surface (§14). |
| D-28 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL (review); native costs OPEN (A-COST §C16). |
| D-36 | OPEN for every write form (§3.4, §11.4, A-COST §C19). C-14 is proposed behaviour for the WF-C and WF-A exports only. |
| N-01 | §10; a lead-owned strict obligation (review). |
| N-02 | Enforced by G7. |
| N-03 | OPEN (review); existing callees need full matching-source strict proof, and no PROVED_ROW transfers. |
| N-04 | CLOSED_AT_DESIGN_LEVEL for the explicit `Classify` enrollment (review); unit-wide body coverage still required. |
| N-05 | OPEN (review); the original exact-set static-audit assertion stays. No exact-set-to-subset reinterpretation or removal. |
| N-06 | REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT (review). Operator item §16.2. |
| N-07 | CLOSED_AT_DESIGN_LEVEL for the explicit pending `Decide` enrollments (review); proof and native body obligations OPEN. |
| R2_NINE_CONDITIONS | Mapped to v5 checks (§8, A-BIND §B11):<br>(1) relocation map: §6 and A-BIND §B2–§B3;<br>(2) one binding: G1–G10 and K1–K6;<br>(3) an identical C profile: P1–P3 and S-RES;<br>(4) an executable decision path: R-TILE, R-W, R-GATE (branch-sensitive), R-ALIAS, R-QUAL, R-GLUE and D1–D5;<br>(5) predecessors: PP1–PP3;<br>(6) complete pins: §8.7;<br>(7) append-only: §9.3;<br>(8) the exact exception set: the boundary unchanged, no core unit newly Off, all units On (`UNANALYZED_BOUNDARY` unchanged);<br>(9) full evidence identity and strictness: the unchanged command and floor, zero unproved, justified and `pragma Assume`, complete reports, and source and library identities.<br>For the reviewer; NOT_CLOSED until reviewed. |
| PACKET_PLAN | §9, carried with §9.4's effective line replaced (V-R9) and §9.6 as v4, plus A-BIND §B1.1 (v5). It keeps linear lineage, representation-packet discipline and an identities-only seal. For the reviewer; NOT_CLOSED until reviewed. |

---

## 18. Everything that remains OPEN (REPLACED in v5)

- **Source and installed legality.**
  - No successor source exists.
  - Installed-tool SPARK legality of every changed unit (D-38), of the External abstract state, and of the `'Image` use.
  - Name resolution in the integrated C_API body, and any warning on a transported clause (§3.6; A-BIND §B0.9).
  - The RM 8.4 readings in R-QUAL's argument: that use clauses are not transitive, and that `use type` exposes operators only (A-BIND §B0.10).
- **Proof.**
  - Flow, RTE, termination and functional obligations of the 95 new routines (J36) and of every called relation, including the N-03 callees, the D-05 decoders, the D-18 index and the D-19 branches.
  - Zero unproved, zero justified, zero `pragma Assume`; floor 251; complete reports and per-unit coverage.
  - Every strict warning class, including N-01's 736 representation warnings (J51). The 119 in moving code (J54) are not resolved by moving.
- **Manifest and composition.**
  - The override, tables and edits are unwritten. The tiles and the B8 sketch, including R-GATE v5 and R-QUAL, are author text that awaits review.
  - The author simulation is not a run of the manifest.
  - `CAPI_QUALIFIED`, `CAPI_QUALIFIER_EXCEPTIONS` and the B10.3 component lists are author-derived.
  - Pins are not regenerated, the mutation controls (§8.8, A-BIND §B12) are unrun as controls, and every stage review is pending.
- **ABI and native.**
  - Symbol export and mapping (D-15); layouts (D-34, N-01 evidence); calling conventions.
  - Write construction for every form (D-36).
  - Every native item of A-COST, including §C21-a…§C21-h.
  - The original native blockers (§11.5).
- **PK-0 characterization.** The class-H failure location and the copy atomicity of a write in progress (§9.6.4). Foreign faults and premise violations are outside the characterization (§9.6.5).
- **Controls.** The 52-action roster, the lifetime controls, all additive controls C-01…C-16, and the provider and fault campaigns on the exact integrated candidate.
- **Boundary.** OB-048, custody, producer authenticity, immutability premises (D-27) and foreign faults (D-23).
- **Integration.** The root-worker lane's changes to `core/worldline-c_api.adb` (§19).
- **Operator.** D-13 before PK-7; N-06 at deployment; all original Phase One operator gates.
- **Reviews.**
  - The independent actual gpt-6.1-sol review of this design: closure of V4-RC4-GATE and V4-RC4-ALIAS, and the carried items.
  - The reviews of every packet and stage, and of the final composition.

---

## 19. Integration collision with the root-worker lane (v4 §19 carried; v5 supplement)

v4 §19 (v4 lines 768-782) is carried verbatim. v5 adds:
- **R-QUAL also fails closed on the draft.**
  - Any new dotted spelling of an Appendix C routine would be refused by (a), whether it is introduced by the draft or by a rebase.
  - So would any declaration in the C_API pair of a root identifier of a full expanded name, by (d).
  - The draft's body-level package renamings (`Y`, `J`, `D`, `A`, `X`, `E`, `T`, `N`, `W`, `O`, `Q`) are not roots. They are refused by R-INV (ii) and R-RES as unlisted residual text, as in v4.
- **A rebase needs new tables.** `CAPI_QUALIFIED['RESIDUAL']` and the residual tables would have to be re-observed on the rebased base and reviewed. They are never edited merely to fit (§9.1).

---

## Appendix A. JACKAL results and observed counts

**JACKAL calls.**
- Every derived number in v5 is one of the calls J01–J68 to the MCP tool `jackal_exact`, recorded with input, `parsed`, `exact`, status and use in `jackal.json`.
- Each returned `status=exact`, `formal=false`, lane `rat`, assurance "exact rational arithmetic (not yet checker-covered)", evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`.
- Each carries these non_claims, verbatim:
  - "NOT formal-bounded: this lane carries no Lean-checked certificate"
  - "The epistemic class above is the STRONGEST claim this result supports"
  - "exact rational arithmetic (not yet checker-covered)"
- `exact` is exact rational arithmetic outside the Lean certificate chain. It is not `formal-bounded`, and it is informational about code correctness only.
- No ledger was used as evidence.

| Use | Calls |
|---|---|
| v4's calls, re-run with the same inputs and values (inventory, source evaluation counts, run-ledger actuals, clause counts, interface units and glue edits, designed packages and tiles, REQUIRED_PROVED lengths and slices, CONTRACT_PINS keys, External_Name counts and movers, warning and error counts) | J01–J58 |
| R-QUAL listed simple names from PK-6b (93) | J59 |
| R-ALIAS pairs at PK-1 (41) and from PK-6b (50) | J60, J61 |
| Gate rows by kind (33 = 31 + 1 + 1) | J62 |
| Qualifier exception entries from PK-6b (9); RESIDUAL qualified occurrences from PK-6b (11) | J63, J64 |
| Indirect-path inventory: 80 paths, 71 of two or more identifiers, 9 single identifiers | J65–J67 |
| B11 rows (42) | J68 |

**Observed counts carried from v4 and v3.** v4 Appendix A's observed rows remain valid, since S5 is unchanged and was re-hashed. They are cited by reference (v4 lines 786-820), together with v3's (v3:2340-2384).

**v5 observations** (read-only scripts; not derived):
- Appendix C: 98 names, all distinct; 85 distinct last selectors; 17 unit prefixes, equal to `CAPI_SPARK_UNITS`; 9 roots; no operator symbol.
- 9 removed names, of which only `Decide` is also an Appendix C simple name.
- 24 scopes with `CAPI_QUALIFIED` entries at PK-7 (A-BIND §B9.4.4).
- 31 `bool` gate rows; 21 distinct `…_Acceptance` type names in B10.3.
- The renaming graph over the 69 S5 `core/*.ads` files is acyclic, with a longest chain of 5 renamings; the 80 paths of A-BIND §B9.4.5.

## Appendix B. Bound inputs (sha256, read while drafting v5)

- **v3's list** (v3 Appendix B; the same files as v3 decisions.json `bound_inputs`, 87 entries) was re-hashed by a read-only script while drafting v5. All matched.
- **v4's additional inputs** (v4 Appendix B, 16 entries) were re-hashed. All matched.
- **Additional v5 inputs:**

```
a9b5dcce5ca5808f8049ae8e7020a79c3fbfc33cc4dcbcc3706fd8f4f40fbfd6  D4/DESIGN.md
59e71dd68724b0420b670d79a99ea74194134dbc6d219b7b91f146ad01843625  D4/decisions.json
39ca995998d68b57d13c02796ee30d8826eecc07e750abf95a83f7d348f7d626  D4/APPENDIX-BINDINGS.md
5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4  D4/APPENDIX-COST-MAP.md
dec64a324685496195a7cb1c48e9ee3cf168255f8a1214d62b9491e42653f39d  D4/jackal.json
ccac4f63a00ed36199642b8691535890719879187b135ecce69f67edc5214b07  D4/AUTHOR-NOTES.md
d7bf825a6c3d0da5f1b9302b64991d05759ae4754eb7347dcf187eb89b2e1f4e  D4/review/gpt61-v1/review.json
3d1ef7f82c2458f24ef9a8916e82db0d97c3e1730038cf20ac3d5e0e0323e4aa  D4/review/gpt61-v1/REVIEW.md
d70fe4677ae2159ad617a0dc6f9982fc976fd86b7d43f66dc9a3913e51e96963  D4/review/gpt61-v1/checks.json
f1dcb0a77264dedd4c08be8b71ce390db66295cb25d1eb79eeb3701c7c0413dc  D4/review/gpt61-v1/review-freeze.json
f5dada7c3ea424b8f404571cf5cfeef0ad7b2eb4f6a07634c6fd481e18e5a88b  W/work/claude-lead-isolation-v1/wt-1/deviations/capi-v4-author-taskstop/NOTE.md
374dd36340edde851d3e897c282800b7a626d07d441bbf798add4c546672e590  S5/core/worldline-evaluation.ads
39ed5300dd43112ed6507c89fddf4c96dcab86e51509eac121e37641f49360a1  S5/core/worldline-owner_transitions_wire.ads
2ee62008ccc9ff73abb3e386c5084ee147432925e69537abb5e373cba8e9e73b  S5/core/worldline-owner_retry_audit_wire.ads
1640ceda9cf05cc16af4609ed986590c85e541a8dd9d76eb1ca70275133b1cd8  S5/core/evaluation_raw_roster.ads
29ea441b1bcc0212db70143c09b961b1f911827c8f30b40cc52f88080f4c222b  S5/core/worldline-evaluation_authority.ads
bc086393ebdf98d397273905aa3425afe4b7cc29cbc9ac9ac1ac1a7f499d8111  S5/core/evaluation_completion_roster.ads
e0a50887d10159aa8350734ed2acc88b8a454fbfeb0eea7d0c727ca28ac17dd7  S5/core/evaluation_completion_c.ads
2faea7935397bebf07a330b7d64c457716c40d8613076696f62359c5723fb48a  S5/core/evaluation_pending_v2.ads
e20808c44b84e02485e10a3eb1e1e36a2f2f88defd75eb97c536cee6851c287a  S5/core/evaluation_finalization.ads
2b2a87a7a1f554486caad6c680e2c39dd4bb7b5e48619933f033cda15ea0a2f5  S5/core/evaluation_completion.ads
bb62783aefa5b2b105dcec33d0273165d2cb5ba86c07006df11f101f5a057fee  S5/core/canonical_artifacts.ads
0a17c0efb95904ee865182a20d3bcabceeef93b1cc3639687aab27696339f35b  S5/core/worldline-c_api.adb
3a3b17c47bb289e24adc3009e0a5a7510972fac07323f636cbd5722e6344319a  S5/core/worldline-c_api.ads
```

- **The renaming graph** was built from all 69 S5 `core/*.ads` files. The sha256 of their sorted `sha256  core/<file>` list is `e6276e7919d0bf39f41c696ec25e5c74c676d9c1e8ec3400763a2a7685a4a217`.
- **The deviation note** above has changed since it was first read before this session's context compaction, because the lead has updated it. The listed identity is the version read in full while drafting v5.

## Appendix C. REQUIRED_PROVED append, in packet order (98 names)

v4 Appendix C (v4 lines 848-850; sha256 in §B-v5.2) is carried verbatim. It carries v3 lines 2478-2589 (sha256 `cee26f7f6c66613cdae339b9765b1ebe5f447a045c37999b7a571ed9200a45c6`). The 535-name prefix is unchanged. The suffix has 98 names (J23) in packet order, and the final length is 633 (J20). R-QUAL's `CAPI_ROUTINE_NAMES` is exactly this list.

## Appendix D. Companion file identities

**How they were produced.** Each companion file was written with the Write and Edit tools to the location in the header. By last edit, they were completed in this order: `jackal.json`, `APPENDIX-BINDINGS.md`, `AUTHOR-NOTES.md`, then this file, then `decisions.json`. The identities below were observed with `sha256sum` and `wc -c` after each file's last edit.

**Where the rest are recorded.** `decisions.json` records this file's sha256, and its own identity is reported in the handoff. `APPENDIX-COST-MAP.md` is v4's, identified in the header.

| File | sha256 | Bytes |
|---|---|---|
| `APPENDIX-BINDINGS.md` | `f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2` | 94352 |
| `jackal.json` | `612d189e4edc29cda39c8e61ac3668bf04adb6abcda12728f7ec14272d4f46d4` | 17950 |
| `AUTHOR-NOTES.md` | `ed45d1db766f3b03ec946946942a571ae50b0eae21e339c5724b5e2480280e47` | 15349 |
