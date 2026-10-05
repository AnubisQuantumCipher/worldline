# C-API raw-pointer boundary consolidation: design v4

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent) |
| Date | 2026-10-04 (EDT); writing finished 2026-10-05 UTC |
| Status | **DRAFT_FOR_GPT61_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author grants nothing, and no author check below is a review. |
| Supersedes | `W/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v3/`: `DESIGN.md` (sha256 `a8a120c9a704177cdab5232a757f1ef405cb3ad1c694ff135cdd2e8f26a14aa7`), `decisions.json` (`2517dd49f6b96e4fe23cd9631aead320ac038605b7286fe8fc5b72c92d99813a`), `APPENDIX-BINDINGS.md` (`5ffb8736b6ce89f655041129991ed0bce4133941129bc7b1566b0da68695d32e`), `APPENDIX-COST-MAP.md` (`c2a320a266fdd088c203e0d61f4cd7c5ea94f7b3b731f5be400f6b2f3d5b114f`). All four were read only and are unchanged (re-hashed while drafting). |
| Answers | The sealed actual gpt-6.1-sol review of v3 in `…/claude-capi-boundary-design-v3/review/gpt61-v1/`: `review.json` (sha256 `ab7efb2bc69d426f9480246bc2dd1f5e381d99879485d4385837ec1105d85223`), `REVIEW.md` (= its `report_sha256` `9fe93d9dd4257aa6ea188278fecedf5971a0ac34135a390f45908d3ac80b14b0`), `checks.json` (`e60cdead79d4db12c413a75044894c6cd793aafa20efb7c340c50d4c9d438f7e`), `review-freeze.json` (`7314f4de53972acbac91541d6a895072a50c264119dfe25e5c20b04ae63512ca`). Verdict ENDORSED_WITH_REQUIRED_CHANGES: RC1–RC3 CLOSED_AT_DESIGN_LEVEL; RC4–RC6 NOT_CLOSED; required changes **V3-RC4, V3-RC5, V3-RC6**. |
| Scope | Proof-source design only. It grants no execution, proof, build, test, review, operator or acceptance authority. |
| Location | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v4/` |
| **What this document consists of** | v4 is self-contained in the following exact sense. The v4 design is (1) the text of this file, plus (2) the v3 `DESIGN.md` line ranges listed as CARRIED_VERBATIM or CARRIED_WITH_LINE_REPLACEMENTS in §B.2, each bound by the sha256 of its exact bytes, with the listed line replacements applied. The v3 file is read-only and pinned above. No other v3 text is part of v4. Every changed passage is restated in full in this file. |
| Companion files | `APPENDIX-BINDINGS.md` (A-BIND v4: the enforceable binding specification), `APPENDIX-COST-MAP.md` (A-COST v4: the source and native cost map), `decisions.json` (machine twin), `jackal.json` (every JACKAL call), `AUTHOR-NOTES.md` (unresolved items, uncertainties, reviewer guidance, process record). Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools. No Write or Edit was refused. Bash was used only for read-only inspection (AUTHOR-NOTES.md §5 states this, including the one interrupted read-only command). |

---

## A. Closure table: V3-RC4, V3-RC5, V3-RC6

Each sub-requirement is quoted from the sealed `review.json` `required_changes`. "Answer" names what v4 supplies. Every answer is a design statement for the reviewer. None is closed by the author, and every proof, native, control and acceptance obligation stays OPEN.

### A.1 V3-RC4: complete and reconcile the enforceable binding specification

| # | Sub-requirement (review text) | v4 answer | Where |
|---|---|---|---|
| 4.1 | "Supply the exact scoped pre-existing and transported renames/use inventory" | The 36 pre-existing clauses of the S5 C_API body, each with its line and enclosing scope (14 renamings and 22 use clauses, JACKAL J15). The exact clause tuple of every designed scope: 15 transport clause blocks CL-T1…CL-T15 and the export and moved-subprogram tuples, each clause classed T (transported, package level), L (transported, subprogram level) or A (added, with its reason), and the excluded renamings with the reason for each. All tuples were checked by a read-only author script against the S5 sources and against segment 1 of every tile. | A-BIND §B9.1, §B9.2; §8.4 |
| 4.2 | "deterministic O6(b)/(c) checks" | R-INV (i)–(vii): exact per-scope tuple equality, residual equality with R-DEL-1, no clause in the context or the C_API specification, one `renames` per listed package renaming, no `use all type`, and no `use` of a SPARK unit. R-ALIAS (`CAPI_ALIAS_FORBIDDEN`) makes O6 (a) enforceable as well. Check functions `_capi_clause_problems` and `_capi_alias_problems`; mutation controls in A-BIND §B12. | A-BIND §B0.4, §B0.5, §B8, §B9.4, §B12; §8.4 |
| 4.3 | "specify actual Library_Interface membership for K3" | K3 parses the single `for Library_Interface use (…);` literal list of `pending.gpr` and requires ordered tuple equality with `CAPI_COMPONENT_INTERFACE` (8 units at L0; 9 after PK-7 under D-13 option (i), JACKAL J16) and no `for Interfaces use`. K5 binds the library attributes, K6 the D-13 (i) mirror, and G9 the core 71-unit interface (observed). v3's false pass is a listed mutation: removing `"evaluation_pending"` from the interface while it remains the `Library_Name`. | A-BIND §B2.3, §B9.5, §B12; §8.2 |
| 4.4 | "define result provenance and gating checks for every write form in B4, including direct SPARK function-result stores, mutable procedure-out buffers/mask, completion Response, and the exclusive finalization assignments" | Nine write forms (WF-C, WF-A, WF-F, WF-O, WF-B, WF-R, WF-P, WF-X, WF-H). Each has a provenance rule and a gate rule. Every foreign write in a designed scope is matched to exactly one row W03–W22 with exact target text, provenance spans and closed identifiers with assignment counts. WF-F covers direct SPARK function-result stores; WF-O the mutable procedure-out buffers and the lifecycle mask; WF-R completion `Response`; WF-X finalization `O`, assigned exactly twice on the two exclusive branches. Every acceptance object has an exact gate row (G06…G21c); R-GATE requires the discriminant to be tested exactly once, inside the gate, before any payload selection. | A-BIND §B0.6, §B0.7, §B10; §3.4, §8.4 |
| 4.5 | "Align O4/R-W, the B4 tables and B8 check algorithms" | B4 is rewritten as exact tiles: every relocated export body and moved helper is given as exact N1 segments, and R-TILE requires equality. The rule checks (R-INV, R-ALIAS, R-W, R-GATE) are kept as invariants that also hold for the tile text. B8 has one function per rule (check-to-rule map). A-BIND §B11 maps each promised condition to its check, or labels it as evidence that no text check can close. An author-run read-only simulation found that the B4 tiles satisfy every R-W row of a tiled scope (W03–W21; W22 is the hash-bound transport helper) and every R-GATE row, that every foreign write in a tile has a row, and that every `.Ok`/`.Verdict` object in a tile has a gate. This is an author check, not a review. | A-BIND §B0.2, §B4, §B8, §B10, §B11; §8.4 |
| 4.6 | "Ordered occurrence checks alone do not enforce adjacency/provenance/exclusive-assignment" (reason) | Exact tiles fix adjacency and order. Provenance spans and closed identifiers fix provenance. Assignment counts (WF-X: exactly two, inside the §5.1 segment) fix exclusivity. | A-BIND §B0.2, §B0.6 |
| 4.7 | "do not silently generalize or waive a rule to fit code" | Every v3 rule that v4 replaces is listed with its replacement and the reason (§8.4.1). v3's blanket O4/R-W rule is withdrawn and replaced by per-form rows, not widened. v3's O6 (c), "exactly one non-`use type` use clause per export body", was unsatisfiable with v3's own tokens, which use `To_Integer`, `Storage_Offset` and address `+` directly. v4 replaces it with exact listed tuples in which every additional clause is named, classed and justified. Nothing is waived. | §8.4.1; A-BIND §B0.4 |
| 4.8 | "full-body/caller review and matching native evidence remain separate" (reason) | Unchanged: §8.9 is carried with one word changed ("token" to "tile"), and A-BIND §B11 row 40 lists those obligations as evidence, OPEN. | §8.9; A-BIND §B11 |

### A.2 V3-RC5: correct PK-0's original-effect classification

| # | Sub-requirement (review text) | v4 answer | Where |
|---|---|---|---|
| 5.1 | "Correct PK-0's original-effect classification" | §9.6 is replaced. Effect classes: R0 pre-capture guard refusal, R1 post-capture guard refusal, R2 element refusal, R3 typed outcome, S success, H handled internal exception, and X outside the premises. | §9.6.1 |
| 5.2 | "Distinguish pre-capture extent guards from post-capture header/transport/value guards and list their exact read frontiers" | For each of the 20 exports, the per-export table gives the R0 guards with their S5 lines; every capture in source order; every R1 guard with its exact frontier (the foreign objects read before it); every R2 frontier; and the canonical write order. v3's "guard refusals: return before any foreign read or write" is withdrawn. Pending captures `R` and finalization captures `X` before their transport guards, and history reads the whole Data arena before the query check. | §9.6.2 |
| 5.3 | "Preserve defined handler/refusal mappings and the order/possible persistence of preceding writes on handled internal exceptions" | Class H is defined, not "undefined". It asserts the handler's code (255, -1, `Null_Address`, `False` or `Invalid_Request`) and the exception diagnostic line where one exists. The handler undoes no write: writes that completed before the raise point persist and were made in the export's canonical order. The ledger example is stated (its writes have a canonical order and its handler maps handled exceptions to 255). Handler codes are failure mappings, never accepted semantic refusals (D2 review C-ABI). | §9.6.3 |
| 5.4 | "label only unresolved copy atomicity/failure-location/native effects as OPEN or implementation-dependent" | Only these are OPEN or implementation-dependent: the raise location and which writes have completed (native failure location; RM 11.6 permissions for language-defined check failures); copy atomicity of a write in progress; build-in-place construction; the successor's native write construction (D-36). | §9.6.4 |
| 5.5 | "Keep foreign-fault/outside-premise cases separate" | Class X is separate: foreign-pointer faults and violated documented premises, each listed. PK-0 asserts nothing for X. | §9.6.5 |
| 5.6 | "keep stronger C-14 no-partial-write behavior outside baseline pass conditions" | C-14 stays proposed behaviour only, never a baseline or PK-0 pass condition. Its scope is corrected to the WF-C and WF-A exports: v3 listed policy and ledger, which are WF-F direct stores. | §9.6.6, §15 |
| 5.7 | (consequential) carried text that asserted the old classification | §7 U7 handler line (v3:1232) replaced; §15 C-01 and C-05 rows replaced. | §B.4, §15 |

### A.3 V3-RC6: correct and qualify the cost map

| # | Sub-requirement (review text) | v4 answer | Where |
|---|---|---|---|
| 6.1 | "Correct and qualify the cost map throughout DESIGN.md, APPENDIX-COST-MAP.md and decisions.json" | A-COST is rewritten. In DESIGN, §3.4, the §3.5 line, §4.9, the §7 delta lines and §11 are replaced. decisions.json carries the corrected entries (RC6-*). | A-COST; §3.4, §3.5, §4.9, §B.4, §11; decisions.json |
| 6.2 | "Count both the Begin_* Fits evaluation and the guarded composer's Fits re-evaluation on active fitting diagnostic paths, with nested Mark's pair separately" | One fit pair = 2 source evaluations (JACKAL J06). An active fitting value or exception path evaluates its own pair, plus the nested `Mark`'s `Line_Fits` pair when that `Mark`'s own read is True: 4 (J08). `I64'Image`: +1 per active fitting value site (J09). Inactive paths evaluate no `Fits` and no `'Image`. | A-COST §C18; §4.9 |
| 6.3 | "correct run-ledger's array/record actual classification" | Four array actuals (J10) and one record actual `Raw` (J11: five actuals in all). | A-COST §C12 |
| 6.4 | "Separate source calls/constructions/language checks from emitted calls/checks/copies, result storage, elision, allocation and lifetimes" | Two layers in every row: source (S-CALL, S-RECHECK, S-OBJ, S-ASSIGN, S-CHECK, S-INIT, S-ASSERT, S-ALLOC) and native (N-CALL, N-CHECK, N-PASS, N-OBJ, N-COPY, N-LIFE, N-VALID, N-ASSERT, N-ALLOC, all OPEN). X1–X5 restated in that form. The D2 review corrections C-UNIT and C-COPY are applied. | A-COST §C0, X1–X5, §C3–§C18 |
| 6.5 | "Remove categorical 'check executes', 'no temporary is elided at -O0', and mandatory Ri copy/storage claims unless tied to matching generated-code evidence" | Withdrawn with exact quotations: X3's "but it executes", C14's "At `-O0` no temporary is elided", the Ri legend's "returned on the secondary stack and copied", X1's "real call", and the matching DESIGN v3 text (§4.9, §11.2). The installed User's Guide is cited only as documentation of ordinary behaviour, never as object-code evidence. | A-COST §C1.2, §C0 |
| 6.6 | "Restrict 'ALLOC =' to the original allocations actually unchanged" | `ALLOC =` is defined to cover only the original allocation statements a row names. Every ALLOC line names them and lists the new objects separately, with native storage OPEN. | A-COST §C0 (S-ALLOC) and every ALLOC line |
| 6.7 | "Preserve D-36 and every original/full-domain native obligation" | D-36 is OPEN for every write form (A-COST §C19, one construction account per form aligned with A-BIND §B10). The original native blockers are carried (§C20). The evidence list is carried and extended by C21-h, source-to-native correspondence. | A-COST §C19–§C21; §11.4–§11.5; §18 |
| 6.8 | (consequential) "a consistent construction account rather than a blanket completed-local claim" for direct stores (review text in REVIEW.md §2) | §3.4 replaced: write forms; v3:267 withdrawn for policy and ledger. | §3.4; A-COST §C19 |

### A.4 Latent v3 defects found while drafting v4 (author's observations, not review findings)

| # | Defect | v4 correction |
|---|---|---|
| L1 | v3 O6 (c) could not be satisfied together with v3's own B4 tokens, which use `To_Integer`, `Storage_Offset` and address `+` directly; these need `use System.Storage_Elements;` or re-exports. | R-INV exact tuples (A.1 item 4.7). |
| L2 | Two operator-visibility gaps in v3's tokens: `Status /= 0` on `Interfaces.C.int` in the two completion exports, and `V = …Join_Malformed` on `Join_Verdict` in `Context_Matches`. | Two listed class-A clauses: `use type Interfaces.C.int;` and `use type Evaluation_Completion_C.Join_Verdict;` (A-BIND §B9.2). |
| L3 | After the retargeting, `package K renames Evaluation_Completion_C;` in `Decide_Raw_Metadata` (S5 `core/worldline-c_api.adb:836`) has no remaining reference. The core builds use `-gnatwa`, which includes `-gnatwu` (unreferenced entities; GN `gnat_ugn.info:8982-8999`). v3 said the renaming "stays and may still name types". | GE9 / R-DEL-1 deletes it as a recorded edit (A-BIND §B4.23). Whether GNAT 16.1.0 would have warned is unverified installed-tool behaviour. |
| L4 | v3's K3 sketch accepted a unit name quoted anywhere in `pending.gpr`. `"evaluation_pending"` is also the `Library_Name` value, so the sketch passed with that interface unit missing. | K3 parses the attribute (A.1 item 4.3). |
| L5 | v3's blanket R-W rule contradicted its own B4 rows for ledger, policy, lifecycle and protocol (protocol's `Owned_Result` is a mutable `in out` actual). | Per-form rows (A.1 item 4.4). |
| L6 | v3 A-BIND B4.17 token 14, `return Evaluation_Completion_C.Join_Code (Joined);`, names `Joined`, but the S5 local is `Joined_Metadata` (`core/evaluation_completion_c.adb:973-978`), so a faithful successor would have failed it. v3 DESIGN:1472 says the same. | The v4 tile uses `Join_Code (Joined_Metadata)`. v3:1472 is replaced (§B.4). Every other v3 B4 token is a substring of the v4 tile or of the successor glue text (author's read-only check; the other non-matching backtick spans are line-citation annotations such as `:129-137`). |
| L7 | v3's C-14 scope listed policy and ledger as "local-then-write" exports, but they store SPARK function results directly. | C-14 scope corrected (A.2 item 5.6). |
| L8 | v3's P2 sketch counted `(?<![\w.'])Size\s*:` and the like as an extra declaration of the subtype name. That pattern also matches `Row_Size : constant Size := …`, `Request_Size : constant I64 := …` and `… : U8 := 0;`, which the designed tiles contain, so the check would have failed a faithful successor. | The pattern excludes `:=` (`… :(?!=)`; A-BIND §B8 `_capi_profile_problems`). An author script confirmed that the corrected pattern finds no hit in the tile text, where the v3 pattern found some. |

---

## B. Carried forward

### B.1 Items the v3 review closed or ruled on, carried unchanged

The disposition column quotes the sealed review's ruling string (or its leading clause).

| Item | v3 review disposition | v4 |
|---|---|---|
| RC1 | CLOSED_AT_DESIGN_LEVEL | Carried: §2.4 and §4.1–§4.8, §4.10 verbatim; §8.5 (D1–D5) verbatim; A-BIND §B6 verbatim. §4.9 is restated for RC6 cost wording only, with no design change. A-BIND B4.19 and B4.24 are now exact tiles equal to the v3 §4.4 text (derived by a read-only script). |
| RC2 | CLOSED_AT_DESIGN_LEVEL | §5 verbatim. The §5.1 transport text is the exact WF-X segment of A-BIND B4.20. |
| RC3 | CLOSED_AT_DESIGN_LEVEL | §10 verbatim. |
| LD1 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL | §2.1, §3.1 verbatim. |
| LD2 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL | §2.2, §3.2 verbatim except the V7 line (rationale wording only). |
| LD3 | CONDITIONALLY_ACCEPTABLE_PENDING_D-13 | §2.3, §16.1 verbatim. |
| LD4 | WITHDRAWN | §2.4 verbatim. |
| LD4-R | CLOSED_AT_DESIGN_LEVEL for RC1 | §2.4, §4 as RC1. |
| LD5 | CONDITIONALLY_ACCEPTABLE | §2.5 verbatim; costs in A-COST §C5–§C6 (source counts unchanged, J06/J07). |
| LD6 | CONDITIONALLY_ACCEPTABLE subject to V3-RC5 | §2.6 verbatim; the V3-RC5 condition is answered in §9.6 and §15. |
| D-13 | OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE | §16.1 verbatim. No choice is made here. |
| N-06 | REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT | §16.2 verbatim. No deployment action. |
| N-01 | LEAD_OWNED_STRICT_OBLIGATION | §10 verbatim. |
| D-05 | OPEN | §3.2 V8 and §17 (inventory carried). |
| D-18 | CLOSED_AT_DESIGN_LEVEL for the index design; proof remains OPEN | §5.4 verbatim. |
| D-19 | OPEN | §5.5 verbatim. |
| D-28 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL | §5.6 verbatim; costs A-COST §C16. |
| D-36 | OPEN for all write-construction forms | §3.4 (replaced), §11.4, A-COST §C19. |
| D-15/D-34/D-38 | OPEN | §8.2, §8.9, §17. |
| N-03 | OPEN | §17. |
| N-04, N-07 | CLOSED_AT_DESIGN_LEVEL for explicit enrollment | Appendix C verbatim (positions 68, 93, 98). |
| N-05 | OPEN | §17 (text carried). |
| APPENDIX_C | CLOSED_AT_DESIGN_LEVEL | Appendix C verbatim (v3 lines 2478-2589). The 535-name prefix, the 98-name ordered suffix and the final length 633 (J20) are unchanged. |
| R2_NINE_CONDITIONS | NOT_CLOSED pending V3-RC4 | §8 (v4) and A-BIND §B11. |
| PACKET_PLAN | NOT_CLOSED pending V3-RC4/V3-RC5/V3-RC6 | §9 (carried, with §9.4's line and §9.6 replaced) and A-BIND §B1.1 (table discipline per stage). |

Unchanged fixed targets: `MINIMUM_CHECKS = 251`; the 535-name ordered `REQUIRED_PROVED` prefix, append-only; `UNANALYZED_BOUNDARY == {"worldline-c_api"}`; 169 effective `CONTRACT_PINS` keys at L0 (observed by AST in v3 and by the v3 review); both builds; every checked assertion. No cap, new public Pre, refusal relabelling, suppression, warning waiver, `pragma Assume`, new Off exception or ABI narrowing is introduced. No public transport code, meaning, layout or caller protocol changes (D2 review C-ABI). The nine Authority_Glue edits change internal call targets and delete one unreferenced renaming.

### B.2 Disposition of every v3 `DESIGN.md` section

"v3 lines" are 1-based line numbers of the v3 file. The sha256 is that of the UTF-8 bytes of those lines, each followed by `\n` (observed by a read-only script). CARRIED_VERBATIM slices are part of v4 exactly. CARRIED_WITH_LINE_REPLACEMENTS slices are part of v4 with the listed lines replaced by the listed v4 text. REPLACED sections are restated in this file.

| v3 section | v3 lines | sha256 of the v3 slice | Disposition | v4 location |
|---|---|---|---|---|
| Header table | 1-13 | — | REPLACED | header above |
| §0 Truth boundary, bases, reading rules | 17-60 | `5eee9c6f40b16b659b513cdf6be29961bc03dc40f05dae3129f2a0f35cf8c65b` | CARRIED_VERBATIM, with the §0 supplement | §0 |
| §1 Trace of the v2 review (history) | 64-107 | `4bf7a3025d1c9b1b1880b7f870ed2b128221f8aa514236a195e3bdd48ac4817b` | CARRIED_VERBATIM as history; §A supersedes its RC4–RC6 answers (reading rule RR6) | §1 |
| §2 Lead decisions | 111-191 | `7f8950643713d597c974b32ac251ca7fffb741499ad973b89b0124478754d63c` | CARRIED_VERBATIM | §2 |
| §3.1 Classification, maximal-run rule | 197-220 | `de660be2d570ffc0427de909bf00fb86aa0a4c4900f1ef853153cd31752dcbb6` | CARRIED_VERBATIM | §3 |
| §3.2 Value-routine form | 222-253 | `2ed8bbeae1f60c1be2cfa7581843af4eab1762c4d83960627561e34addcee0c2` | CARRIED_WITH_LINE_REPLACEMENTS (v3:246) | §3, §B.4 |
| §3.3 Staged reads | 255-260 | `e0ebd131536e3a1b41d0aea6b12651d2807d564ac9e324c165dc90dccafb0a25` | CARRIED_VERBATIM | §3 |
| §3.4 Writes and write construction | 262-269 | — | REPLACED (V3-RC4, V3-RC6) | §3.4 |
| §3.5 Exception and allocation scope | 271-277 | `1c392a5de31bf37ce3fae7ce125e1ba6c819f95963704362655573f4629fd411` | CARRIED_WITH_LINE_REPLACEMENTS (v3:276) | §3, §B.4 |
| §3.6 `Worldline.C_API` layout | 279-309 | — | REPLACED (V3-RC4) | §3.6 |
| §3.7 What stays in each SPARK unit | 311-322 | `64fb82d9b368abfb6ea1f6d40a67b3d011d5681d6eac5bd38f1b72441fdf2a16` | CARRIED_VERBATIM; enforced in v4 by G9 | §3 |
| §4.1–§4.8 Diagnostics (RC1) | 326-664 | `8e42f710e70279905392be9aa653b3e03465a96a5f11f1b0d8ff956309d99ec1` | CARRIED_VERBATIM | §4 |
| §4.9 Native cost of diagnostics | 666-671 | — | REPLACED (V3-RC6) | §4.9 |
| §4.10 OPEN | 673-678 | `677c19ee8e23d504de3da97558f431a038da6bf1c7d3ecc4f3a973ea0463c059` | CARRIED_VERBATIM | §4 |
| §5 RC2 | 682-902 | `8a8f96b476a32e6e525637e8ab9f2c7de89d10ec24bd6232f2a32457a622dd97` | CARRIED_VERBATIM | §5 |
| §6 Relocation map | 906-937 | `e442efc0ad095cc6e63b9872c403e87d626c140b2bb7249ecd8148f586f9676e` | CARRIED_VERBATIM (reading rule RR7) | §6 |
| §7 Per-unit designs | 941-1726 | `5724c0ca257a3105c87381963f7e4cf3fd43aa95ffc0a7dcdc9842520e3e27b5` | CARRIED_WITH_LINE_REPLACEMENTS (v3:945, :1069, :1192, :1232, :1238, :1270, :1472) | §7, §B.4 |
| §8.1 Tables | 1736-1744 | — | REPLACED | §8.1 |
| §8.2 Whole-closure checks | 1746-1770 | `3d60cfb16ba2290bea917012218a5335f58623b357628edd10a878f58a383ecc` | CARRIED_WITH_LINE_REPLACEMENTS (v3:1765, K3), plus the additions G9, G10, K5, K6 | §8.2 |
| §8.3 Resolved C profile | 1772-1778 | `26c2096c65e4d1bd997f55f90180bdddae4c53c90b59163f9274a83b56b4be17` | CARRIED_VERBATIM | §8.3 |
| §8.4 Ordered calls, result-to-write | 1780-1804 | — | REPLACED (V3-RC4) | §8.4 |
| §8.5 Diagnostic confinement | 1806-1812 | `604808012ae22c11cf332e3f368c5eb7384ede49b3b6804190054bcc3d825431` | CARRIED_VERBATIM | §8.5 |
| §8.6 Preserved predecessor assertions | 1814-1827 | `f4fde5a89f55d275e19b46a0af11ab7da09b136b2cbc55a0aa39bec2f2a42189` | CARRIED_VERBATIM | §8.6 |
| §8.7 Identity binding | 1829-1841 | `e59632c2911a3d6fc6145c2e968f5d291e196c37558f74412bc2cee882ed583d` | CARRIED_VERBATIM | §8.7 |
| §8.8 Mutation controls | 1843-1852 | `19668c3c5cf9218413ef26eedab5484580ae395f1f5f800ec99a6569604dbac1` | REPLACED (v3 rows reinterpreted for tiles; A-BIND §B12 added) | §8.8 |
| §8.9 What the checks do not establish | 1854-1864 | `f262ea5ecf99af3d16da545aa09d7ce63cc00ee8c7e539a581d2e22653d6549f` | CARRIED_WITH_LINE_REPLACEMENTS (v3:1858) | §8.9 |
| §9.1–§9.3 Lineage, packets, append schedule | 1868-1925 | `088d7f047669b947b1d1715f83c6308de0feb3c550e605a7b7d05b0b13623357` | CARRIED_VERBATIM | §9 |
| §9.4 Intermediate binding tables | 1927-1934 | `5158b5cb891cbbcf9364bfe33b81a619cd923ed23306d51d97778b0bcd7d045d` | CARRIED_WITH_LINE_REPLACEMENTS (v3:1931) | §9, §B.4 |
| §9.5 PK-6a enrolment, PK-6b | 1936-1939 | `314052df868511897fff559c64820ff6c85a2b9c71a6dd340da613827bc54a7c` | CARRIED_VERBATIM | §9 |
| §9.6 PK-0 characterization | 1941-1968 | — | REPLACED (V3-RC5) | §9.6 |
| §9.7–§9.9 Representation placement, seal, after PK-S | 1970-1993 | `ff5c8475549cd9a687f0ad70c9115d771d0b4679e0f0875f75b86c049cc9a39a` | CARRIED_VERBATIM | §9 |
| §10 RC3 | 1997-2052 | `258b3d2361e5f8e3ba34315d100c8ac2a37164bbe96f0dd846aadcfbf01943f6` | CARRIED_VERBATIM | §10 |
| §11.1–§11.4 Cost summary | 2056-2120 | — | REPLACED (V3-RC6) | §11 |
| §11.5 Original native blockers | 2122-2132 | `e5c9c9f85482d18f0858d858ecccead7f916b2abce45d93b9c46873053c7ddae` | CARRIED_VERBATIM | §11.5 |
| §12 ABI and behaviour matrix | 2136-2175 | `25bafa834c6179064480c1581c71f464c3e8d8712833f231fbbff0bb5348c612` | CARRIED_VERBATIM | §12 |
| §13 R4 | 2179-2188 | `6d60ea058fb75aef9f43ece9dd726cc7c56b08c358330c6e2a516a67aa8c1e41` | CARRIED_VERBATIM | §13 |
| §14 R5, OB-048 | 2192-2211 | `703c7c03a8729ea248150b26d18f47f1cf848505e2796b7653c68181c09076fc` | CARRIED_VERBATIM | §14 |
| §15 Controls | 2215-2244 | `8fc979e135f23a9554b41c644126a212c0ea437850e4bac1f8c3a860b1c1f18d` | CARRIED_WITH_LINE_REPLACEMENTS (v3:2227, :2231, :2240) | §15 |
| §16 Operator decision items | 2248-2273 | `30badbdefecb6639788dc40e4cf77aecd42afc7e521ca9123e4f954611ff6713` | CARRIED_VERBATIM | §16 |
| §17 Rulings and carried items | 2277-2299 | — | REPLACED | §17 |
| §18 Everything OPEN | 2303-2324 | — | REPLACED | §18 |
| Appendix A Counts, JACKAL | 2328-2384 | — | REPLACED (v4 calls; v3's observed counts carried by reference in Appendix A) | Appendix A |
| Appendix B Bound inputs | 2386-2476 | — | REPLACED (v3's list carried and re-verified) | Appendix B |
| Appendix C REQUIRED_PROVED append | 2478-2589 | `cee26f7f6c66613cdae339b9765b1ebe5f447a045c37999b7a571ed9200a45c6` | CARRIED_VERBATIM | Appendix C |
| Appendix D Companion identities | 2591-2602 | — | REPLACED | Appendix D |

### B.3 Reading rules for carried text

- **RR1.** "Ordered tokens" or "tokens" of A-BIND §B4 means the v4 exact tile of the same §B4 entry. Each tile contains every v3 token of that entry, except the corrected B4.17 token (§A.4 L6).
- **RR2.** "O1–O7" means the v4 checks of §8.4, mapped in §8.4.1.
- **RR3.** "A-COST §Cn" means the v4 A-COST section with the same number. The numbering is unchanged; v4 adds §C1.2, §C21-h and §C22.
- **RR4.** References to §3.4, §3.6, §4.9, §8.1, §8.4, §8.8, §9.6, §11.1–§11.4, §17 and §18 resolve to the v4 replacements in this file.
- **RR5.** "Appendix A", "Appendix B" and "Appendix D" mean the v4 appendices of this file.
- **RR6.** v3 §1 is the historical trace of the v2 review's required changes. Its "v3 answer" and "Remains OPEN" cells are not statements of v4 status; §A is.
- **RR7.** v3 §6's "the v2 §4 table, unchanged" (v3:932) refers to the helper set whose exact members and sha256 are A-BIND §B9.3.
- **RR8.** In carried §0, "this design" means v4, and "the appendices" means the v4 appendices.

### B.4 Line replacements in carried slices

Each item gives the v3 line number, the exact v3 line, and the v4 line that replaces it in the carried slice. Nothing else in the slice changes.

**R1 (v3:246, §3.2 V7; V3-RC4 wording).**
```text
v3: - **V7 Naming.** New names are unique, unoverloaded and fully qualified at every transport call. This keeps the name-keyed coverage map and the ordered-token checks unambiguous (`proof_manifest.py:787-789`).
v4: - **V7 Naming.** New names are unique, unoverloaded and fully qualified at every transport call. This keeps the name-keyed coverage map, the exact tiles (R-TILE) and the alias exclusion (R-ALIAS) unambiguous (`proof_manifest.py:787-789`; A-BIND §B0.2, §B0.5).
```

**R2 (v3:276, §3.5; V3-RC6).**
```text
v3: - Every SPARK call that could raise `Storage_Error` is inside the handler. This covers native Big_Integer `Normalize` (Bignum_Limit 200, per `H/native-cost-gap/REVIEW.md`) and the new temporaries listed in A-COST.
v4: - Every SPARK call that could raise `Storage_Error` is inside the handler. This covers native Big_Integer `Normalize` (Bignum_Limit 200, per `H/native-cost-gap/REVIEW.md`) and any storage that the successor's new source objects and function results need (A-COST S-OBJ entries); whether, where and how much storage they need natively is OPEN (A-COST N-OBJ, N-ALLOC).
```

**R3 (v3:945, §7 preamble; V3-RC4).**
```text
v3: - A-BIND §B4 gives each export's ordered tokens, and A-COST gives each call site's cost row.
v4: - A-BIND §B4 gives each export's exact tile (v4; reading rule RR1), and A-COST gives each call site's source row and its native counterpart.
```

**R4 (v3:1069, §7 U3; V3-RC6).**
```text
v3: - **v3 deltas** (A-COST §C5): one extra `Well_Formed` per call in both builds; the `Owned` local and its copy.
v4: - **v3 deltas** (A-COST §C5): one extra `Well_Formed` source evaluation per accepted call in both builds; one constant object `Owned` and one source assignment of it through the access value (WF-C). Emitted calls, copies and construction are OPEN (A-COST §C19, D-36).
```

**R5 (v3:1192, §7 U6; V3-RC6).**
```text
v3: - **v3 deltas** (A-COST §C8): one `Request_Valid` re-check; per-row acceptance temporaries; one SPARK call per mask byte over a loop whose length the caller sets.
v4: - **v3 deltas** (A-COST §C8): one `Request_Valid` re-check; one acceptance object per row (X4); one SPARK call per mask byte over a loop whose length the caller sets, its result stored directly (WF-F). Native temporaries, calls and inlining are OPEN.
```

**R6 (v3:1232, §7 U7 handler; V3-RC5).**
```text
v3: - **Handler:** 255, covering the nested allocations. **A partial write is possible if an exception occurs during writeback, exactly as in the original.** PK-0 does not assert otherwise (§9.6).
v4: - **Handler:** 255, covering the nested allocations. The handler undoes no write. On a handled internal exception raised after the first write of step 6, the writes already completed persist, in the canonical order of step 6. Which writes have completed, and whether a write in progress completed partly, is implementation-dependent and OPEN (§9.6.3, §9.6.4). On that path PK-0 asserts the code, and that nothing outside the write set changed.
```

**R7 (v3:1238, §7 U7; V3-RC6).**
```text
v3: - **v3 deltas** (A-COST §C9): per-row temporaries; a per-detail call into another unit to `Encode_Quantity` instead of a body-local expression; result temporaries.
v4: - **v3 deltas** (A-COST §C9): one acceptance object per row; per detail, a source call into another unit to `Encode_Quantity` instead of a body-local expression function, its result stored directly (WF-F); the `Result_Of` result stored directly (WF-F). Native calls, temporaries and construction are OPEN.
```

**R8 (v3:1270, §7 U8; V3-RC4/V3-RC6).**
```text
v3: - **v3 deltas** (A-COST §C10): the write construction changes from a direct aggregate store to a SPARK result copied once.
v4: - **v3 deltas** (A-COST §C10): the aggregate of adb:171-176 is built in SPARK by `Encode_Decision`, and the function result is stored directly through the access value (WF-F), as the original stored the aggregate directly. Native construction is OPEN (A-COST §C19, D-36).
```

**R9 (v3:1472, §7 U14 metadata; §A.4 L6).**
```text
v3: 9. Value join-result; return `Join_Code (Joined)`.
v4: 9. Value join-result; return `Join_Code (Joined_Metadata)` (the S5 local is `Joined_Metadata`, adb:973-978).
```

**R10 (v3:1765, §8.2 K3; V3-RC4).**
```text
v3: - **K3** `pending.gpr`'s `Library_Interface` lists every unit that holds a component export (after PK-7, including any D-13 transport unit) and keeps every original interface unit. Observed: 8 units (A-BIND §B2.3).
v4: - **K3** (actual membership) `pending.gpr` contains exactly one `for Library_Interface use (…);` declaration, whose value is a list of string literals only (no `&`, variable, `external` or attribute reference). Its lowercased tuple equals `CAPI_COMPONENT_INTERFACE` exactly, in order and without duplicates: the 8 observed L0 units, plus `evaluation_pending_transport` from PK-7 under D-13 option (i) (9 units, JACKAL J16). `for Interfaces use` occurs zero times (A-BIND §B2.3).
```

**R11 (v3:1858, §8.9; V3-RC4 wording).**
```text
v3: - faithful actuals beyond the token text;
v4: - faithful actuals beyond the tile text;
```

**R12 (v3:1931, §9.4; V3-RC4).**
```text
v3: - Every stage enforces G1–G8, P1–P3 and O1–O7 for the relocated set, and from PK-6b also D1–D5.
v4: - Every stage enforces G1–G10, K1–K5 (K6 from PK-7), P1–P3, R-TILE, R-TRANS, R-INV, R-ALIAS, R-W, R-GATE, R-RES, S-RES, R-LAYOUT and R-GLUE for the units bound so far (§8, A-BIND §B1.1), and from PK-6b also D1–D5.
```

**R13 (v3:2227, §15 C-01; V3-RC5).**
```text
v3: | C-01 | No-write on *defined* refusal paths only (§9.6), with outputs pre-filled `0xA5` | exports with outputs |
v4: | C-01 | No-write only on the defined refusal paths of §9.6: R0, R1 and R2 refusals and the no-write R3 outcomes, with outputs pre-filled `0xA5`. Never asserted on class H or class X paths. | exports with outputs |
```

**R14 (v3:2231, §15 C-05; V3-RC5).**
```text
v3: | C-05 | Read gating with PROT_NONE pages in child processes; asserts normal exit and the expected code only | as §9.6 |
v4: | C-05 | Read gating with PROT_NONE pages in child processes, placed exactly beyond each refusal's read frontier (§9.6.2) and on absent or unneeded inputs; asserts normal exit and the expected code only | as §9.6 |
```

**R15 (v3:2240, §15 C-14; V3-RC5, §A.4 L7).**
```text
v3: | C-14 | **Proposed** behaviour only (D-36): no partial write on internal exceptions for local-then-write exports; review evidence, never baseline | v2, v3, chain, run ledger, pending, policy, ledger |
v4: | C-14 | **Proposed** behaviour only (D-36): no partial write on an internal exception for the WF-C and WF-A exports, which complete the stored value before the write; review evidence, never baseline and never a PK-0 pass condition | v2, v3, run ledger, chain, pending v1/v2 |
```

---

## 0. Truth boundary, bases and reading rules (v3 §0 carried; v4 supplement)

v3 §0 (v3 lines 17-60) is part of v4 verbatim (§B.2). The following supplements it.

**Nothing was executed while drafting v4.**
- Bash was used only for read-only inspection: mainly `cat`, `sed -n`, `grep`, `find`, `sha256sum`, `wc`, and short Python scripts that read files as text or through `ast` and printed to standard output.
  - Pipelines also used the read-only filters `head`, `cut`, `awk`, `sort`, `uniq` and `printf`, plus `cd`, a few `for` loops and `ls`. These are outside the brief's literal list, and the deviation is reported (AUTHOR-NOTES.md §5).
  - Python scripts were fed on standard input through quoted heredocs, which wrote no file.
- No file was created, moved, copied, deleted or changed with Bash or Python, and no output was redirected to a file.
- No compiler, prover, gprbuild, gnatprove, test, WORLDLINE code, service, project-vault, restic or SIA action was run, and `proof_manifest.py` was read as text only.
- **One process event.** A read-only inspection command hung after its `sha256sum` step, at an `ls` of the v3 review directory. It was stopped with TaskStop (task `ba0hhwegp`; the lead's record gives 2026-10-05T01:22:20.621Z). Before the stop it had printed three sha256 lines, for `review.json`, `REVIEW.md` and `checks.json`. The read was then completed with a bounded command. No other interruption occurred. The lead has since relayed the operator's standing rule against interrupting any tool, and the rest of the drafting followed it (AUTHOR-NOTES.md §5).

**Additional bases.**
- `D3` = `W/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v3` and `R3` = `D3/review/gpt61-v1` (the sealed review; identities in the header).
- `RW` = `W/work/protected-original-root-worker-repair-v1`, the root-worker lane. Its draft `source/core/worldline-c_api.adb` is observed at 148068 bytes, sha256 `806f3972277d9385b0d32c5e3faf1bf6fb24f9024dbc1c8274411b8c1d0e3420`.
- `RWD` = `W/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1`, with its review.
- `D2D` = `W/work/claude-lead-isolation-v1/wt-1/designs/claude-d2-checked-ghost-inventory-v1`, with its review (corrections C-UNIT, C-COPY and C-ABI applied here).
- `GN` = `/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1` (installed compiler documentation, read only).

**v4 numbers.** Every derived number in v4 and its appendices is one of the JACKAL `jackal_exact` calls J01–J58 recorded in `jackal.json`. Each returned `status=exact`, `formal=false`, lane `rat`, evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, and the three non_claims quoted in Appendix A. Numbers carried from v3 were re-run. Counts read from files by a script are reported as observed.

**Author checks are not review.** v4 cites several read-only author scripts:
- the S5 helper hashes, clause inventories, residual and glue hashes and `Library_Interface` lists;
- the simulation of R-W and R-GATE on the tiles;
- the containment of the v3 tokens;
- the identifier-collision scan;
- the re-hash of the 87 v3 bound inputs (all matched).

They are self-checks by the author. They grant nothing, and they do not substitute for the required independent actual gpt-6.1-sol review.

---

## 1. and 2. (carried)

v3 §1 (history; reading rule RR6) and v3 §2 are part of v4 verbatim.

---

## 3. Design rules applied to every unit

v3 §3.1, §3.3 and §3.7 are carried verbatim; v3 §3.2 and §3.5 are carried with replacements R1 and R2. §3.4 and §3.6 are replaced:

### 3.4 Writes and write construction (REPLACED in v4)

- There is no blanket output rule. Each export keeps its original write set, conditions and source order (§9.6.2).
- Accepted input/output aliasing is preserved by capturing every input before the first write. Existing overlap refusals are kept, and none is added.
- **Write forms.** Every foreign write in a designed scope has exactly one form, with a checked provenance (A-BIND §B10.1, rows W03–W22):
  - **WF-C**: assignment of a constant completed from the listed SPARK call (v2, v3, history).
  - **WF-A**: assignment of the payload of an acceptance constant, after its gate (run ledger, chain, pending v1 and v2).
  - **WF-F**: direct store of the listed SPARK function result, whose actuals are closed WF-O buffers or WF-C constants (lifecycle mask bytes; ledger detail quantities and result; headroom result; policy result).
  - **WF-O**: a mutable buffer, variable or mask that is an `out` or `in out` actual of exactly one listed SPARK procedure call (lifecycle `Mask` and `Status`; ledger `Detail_Arena`, `Total_Arena`, `Typed_Details`, `Total`, `Status`; headroom `Output_Arena`, `Typed_Result`, `Status`).
  - **WF-B**: the `Write_Data` copy-out of a WF-O buffer (ledger compute twice, headroom once).
  - **WF-R**: completion `Response`, the `out` actual of exactly one `Decide_Value` or `Raw_Decide_Value` call, gated by `Status`.
  - **WF-P**: protocol `Owned_Result` and `Status`, unchanged from S5.
  - **WF-X**: finalization `O`, assigned exactly twice, once on each of the two exclusive branches of §5.1, and gated once (G21c).
  - **WF-H**: the one transport helper that writes (`Ledger_Transport.Write_Data`), hash-bound.
- **Write construction is a native property and is not claimed equal.** In source:
  - the WF-C and WF-A exports assign a completed constant (or its payload) where the original assigned a function result or an aggregate directly;
  - the WF-F exports store a SPARK function result directly, as their originals stored a function result or an aggregate directly;
  - WF-P, WF-R and WF-X keep the pattern of writing a completed local, which is now produced by SPARK.

  How each stored value is constructed natively (in place or through a temporary), copied and padded, and what happens on an exception during construction, is OPEN (A-COST §C19, D-36).
- v3's statement that policy and ledger details/result "complete a SPARK result first and copy it once" (v3:267) is withdrawn (A-COST §C1.2).

### 3.6 `Worldline.C_API` layout (REPLACED in v4)

**Specification.**
- 20 relocated export declarations (A-BIND §B3), each the original normalized declaration with only the identifier changed, and four package-level subtypes: `U8`, `U32`, `I64`, `Size` (P2).
- They form one run, the subtypes first and then the declarations in `CAPI_LAYOUT_EXPORTS` order. The run begins immediately after `External_Name => "wl_owner_audit_decide_v1";` and ends immediately before the final `end Worldline.C_API;` (R-LAYOUT).
- `External_Name` occurrences: 31 observed today; 51 after the last move (JACKAL J05).
- The specification declares no clause and no renaming (R-INV (iv), G10). S-RES binds everything else in it to S5.

**Body.**
- **Context.** It gains `with Ada.Text_IO;` and `with Ada.Exceptions;` (PK-6b) and `with` clauses for the SPARK units its new code names. These are bound by the C_API pin and the packet review. The context holds no use clause, renaming or pragma (R-INV (iii), G10).
- **(a) The designed packages.** The 15 unit transports and `Diagnostic_Transport` (16 packages, JACKAL J18) form one contiguous run between `end Layout_Offset;` (S5 `:667`) and `package body Authority_Glue is` (S5 `:671`), in `CAPI_LAYOUT_PACKAGES` order (A-BIND §B4.0).
  - Each stage appends its packages at the end of the run. So `Diagnostic_Transport` (PK-6b) follows the PK-1…PK-5 transports and precedes `Completion_Transport` and `Finalization_Transport`, which use it.
  - v3 listed `Diagnostic_Transport` first. v4 keeps every earlier stage's text unchanged instead. Both orders satisfy Ada's declare-before-use.
- **Each transport** is `package T is … end T; package body T is … end T;` (R-TRANS):
  - The specification holds exactly its clause block (A-BIND §B9.2), its listed subtypes, its verbatim helpers (A-BIND §B9.3, sha256-bound), its constants and the profiles of its body helpers and moved subprograms.
  - The body holds only the body helpers and the moved subprograms. There is no elaboration code.
- **Clauses (R-INV).**
  - Each transport specification carries its unit's package-level clauses in original order. The only exclusions are renamings that no transported text references, each listed with its reason.
  - Each export body holds `use <Unit>_Transport;`, then the unit's package-level use clauses, then the original subprogram's own clauses, then the listed additions (two `use type` clauses, §A.4 L2).
  - This replaces v3's rule "exactly one non-`use type` use clause per export body" (§A.4 L1).
- **Moved subprograms.** `Completion_Transport.Context_Matches`, `Completion_Transport.Metadata_Base` and `Finalization_Transport.Final_Context_Matches` are tiled (A-BIND §B4.16, §B4.18, §B4.21).
- **(b) The existing code** is unchanged except for the recorded edits GE1–GE9 (R-RES, R-GLUE).
- **(c) The 20 export bodies** form one contiguous run immediately after `end Owner_Audit_Decide;`, in `CAPI_LAYOUT_EXPORTS` order, ending immediately before the final `end Worldline.C_API;`.

**Authority_Glue edits** (A-BIND §B4.23). The four retargeted callees of v3 are unchanged, at eight call sites (JACKAL J17); arguments, order and gating are unchanged. In addition, GE9 (R-DEL-1) deletes the then-unreferenced `package K renames Evaluation_Completion_C;` of `Decide_Raw_Metadata` (JACKAL J16: nine edits). The pre-existing Off value decisions in `Authority_Glue` (`:768-770`, `:783-819`) remain boundary surface (D-21).

| Original call | Sites in `core/worldline-c_api.adb` | Retargeted to |
|---|---|---|
| `K.Raw_Decide` | `:784-785`, `:791-792` | `Completion_Raw_Decide` |
| `K.Context_Matches` | `:810-811`, `:813-814` | `Completion_Transport.Context_Matches` |
| `K.Metadata_Base` | `:852`, `:855` | `Completion_Transport.Metadata_Base` |
| `K.Metadata_Matches` | `:866-867`, `:869-870` | `Completion_Metadata_Matches` |

**Name resolution in the integrated body (author scan; OPEN for the installed compiler, D-38).**
- A read-only scan found that no identifier used in the B4 tile text is declared at `Worldline.C_API` specification or body level in S5 outside `Authority_Glue`. Such a declaration would hide a use-visible transport name of the same name in the export bodies (RM 8.4: a potentially use-visible declaration is not use-visible at a place within the immediate scope of a homograph; the author's reading of the rule, since no RM text is installed locally).
- `Byte_Pointers` (S5 `core/worldline-c_api.adb:34`) is declared at body level and also in the two pending transports. No export tile names it, and inside each transport its own declaration hides the outer one.
- The transport subtype names (`Request`, `Result`, `Row`, `Row_C`, …) collide with no C_API-level declaration.
- The root-worker draft would introduce such collisions (§19).
- Installed-compiler confirmation of every resolution, and of the absence of any warning for a transported clause, remains OPEN (D-38; A-BIND §B0.9).

---

## 4. RC1 (carried) and §4.9 (REPLACED in v4)

v3 §4.1–§4.8 and §4.10 are part of v4 verbatim. Only §4.9 changes (V3-RC6). The design of §4.2–§4.6 is unchanged.

### 4.9 Native cost (REPLACED in v4)

Source counts are from A-COST §C18 and are counts of source evaluations, not emitted instructions (D2 review C-UNIT).

- **Inactive path (the default).** Every Mark, Value and Exception site performs one more source call level, and the same single atomic read. No `*_Fits` predicate and no `I64'Image` is evaluated: the `Active and then …` short circuit skips them. Whether the calls are emitted or inlined is OPEN (A-COST X1).
- **Active path, fitting.**
  - Each reached composition evaluates its `*_Fits` predicate twice, once in `Begin_*` and once in the guarded composer: one fit pair, 2 evaluations (JACKAL J06).
  - An active value or exception site evaluates its own pair, plus the nested `Mark`'s `Line_Fits` pair when that `Mark`'s own atomic read is True: 4 evaluations (JACKAL J08).
  - `I64'Image` is evaluated twice instead of once per active value site: +1 (JACKAL J09).
  - Atomic reads per active value or exception site: 2, as in the original (J06).
- **Storage.** Text is composed by SPARK functions returning `String`. Where those results, and the original's catenation results, are stored, and for how long, is OPEN. The installed User's Guide's statement that the secondary stack holds unconstrained function results (GN `gnat_ugn.info:11252-11260`) is documentation, not evidence for these call sites (A-COST §C18, C21-c).
- v3's "Cross-unit calls are not inlined under the core switches" and "returning `String` on the secondary stack; the original catenations also used it" (v3:668-669) are withdrawn (A-COST §C1.2).

---

## 5. and 6. (carried)

v3 §5 (RC2, closed at design level) and v3 §6 (relocation map; reading rule RR7) are part of v4 verbatim.

---

## 7. Per-unit designs (carried with line replacements)

v3 §7 (v3 lines 941-1726) is part of v4 with replacements R3–R9 (§B.4). The exact text of every relocated export body and moved helper is in A-BIND §B4 (tiles); its writes and gates are in A-BIND §B10; its read frontiers are in §9.6.2.

---

## 8. RC4: enforceable manifest-binding specification (v4)

These checks are additions to the export check chain. They never disable or weaken a predecessor. Their literal tables are given per stage in A-BIND (§B1, §B1.1). They are necessary guards only. Reachability, actuals beyond the text, native identity and use of the real result also require the pinned full-body and caller review. No textual check closes that obligation (§8.9).

### 8.1 Tables appended by PK-1 and extended by every later stage (REPLACED in v4)

- **Closure and profile tables:** `CAPI_CORE_HOME` (all 91 closure symbols, JACKAL J04), `CAPI_DECLARATIONS`, `CAPI_C_API_SUBTYPES`, `CAPI_ALTERNATE_BINDINGS`, `CAPI_PROJECT_FORBIDDEN`, `CAPI_MOVED_UNITS`.
- **Exact text tables:**
  - `CAPI_TILES`: 23 tiled subprograms once PK-7 is applied (JACKAL J19);
  - `CAPI_DIAGNOSTIC_PACKAGE`;
  - `CAPI_TRANSPORTS`: clauses, subtypes, constants, helpers with kind and sha256, moved subprograms;
  - `CAPI_INVENTORY`;
  - `CAPI_RESIDUAL_CLAUSES` and `CAPI_RESIDUAL_DELETED`;
  - `CAPI_RESIDUAL_SHA256`, `CAPI_SPEC_RESIDUAL_SHA256`, `CAPI_GLUE_EDITS` and `CAPI_GLUE_SHA256`;
  - `CAPI_LAYOUT_PACKAGES` and `CAPI_LAYOUT_EXPORTS`.
- **Rule tables:** `CAPI_ALIAS_FORBIDDEN`, `CAPI_SPARK_UNITS`, `CAPI_WRITES`, `CAPI_GATES`, `CAPI_GATE_ASSIGNED`, `CAPI_DIAGNOSTIC_SITES` (from PK-6b).
- **Project tables:** `CAPI_CORE_INTERFACE` (71 units, observed), `CAPI_COMPONENT_HOME`, `CAPI_COMPONENT_INTERFACE`, `CAPI_COMPONENT_LIBRARY`, and from PK-7 under D-13 option (i) `CAPI_COMPONENT_MIRROR` and `CAPI_COMPONENT_DECLARATIONS`.
- Each later stage appends `.update({...})` lines to dictionaries, or extends a tuple by a reassignment that keeps the earlier prefix, as the manifest already extends `DECLARED_CORE_ADA_SOURCES` (`proof_manifest.py:640`). Nothing earlier is deleted or reordered. `CAPI_RESIDUAL_DELETED` receives index 22 at PK-6b. It is the append that records the one reviewed deletion in the residual source (R-DEL-1).
- The `export_problems` override is defined once at PK-1 and reads the tables at call time. So every stage's effective tables are complete for the whole closure (§9.4).

### 8.2 Whole-closure checks (v3 §8.2 carried with R10; additions)

v3 §8.2 (G1–G8, K1, K2, K4 and the matching-library evidence) is part of v4, with K3 replaced by R10. Added in v4:

- **G9 (core interface).** `core/worldline_core.gpr` contains exactly one `for Library_Interface use (…);` declaration, a list of string literals only. Its lowercased tuple equals the observed S5 71-unit tuple `CAPI_CORE_INTERFACE` (A-BIND §B9.5), and `for Interfaces use` occurs zero times. The file is also pinned. G9 turns §3.7's "`Library_Interface` … unchanged" into its own check.
- **G10 (context and specification hygiene).**
  - The text of `core/worldline-c_api.adb` before `package body Worldline.C_API with SPARK_Mode => Off is` contains no `pragma` and no use or renaming clause.
  - `core/worldline-c_api.ads` contains no use clause and no `renames`.
  - `use all type` occurs nowhere in the pair. (S5 observed: none of these.)
- **K5 (component library attributes).** `for Library_Name use "evaluation_pending";`, `for Library_Kind use "dynamic";`, `for Library_Standalone use "encapsulated";` and `for Library_Auto_Init use "true";` each occur exactly once in `pending-component/pending.gpr` (observed at L0). No other declaration of those attributes exists.
- **K6 (component mirror, from PK-7 under D-13 option (i)).**
  - The component transport unit's specification declares exactly B3 declarations 19 and 20.
  - Its `Pending_Transport` and `Pending_V2_Transport` package spans and its two export bodies are N1-identical to the corresponding scopes of `core/worldline-c_api.adb`.
  - Its exact text is fixed in PK-7's packet review, because D-13 is the operator's choice.

Check functions: `_capi_closure_problems` (G1–G4, G6, G7), `_capi_core_project_problems` (G5, G9), `_capi_component_problems` (K1–K3, K5, K6), `_capi_clause_problems` (G10 with R-INV), `_capi_diagnostic_problems` (G8, D1–D5) (A-BIND §B8).

### 8.3 Resolved C profile

v3 §8.3 (P1–P3) is part of v4 verbatim. `_capi_profile_problems` checks P1 and P2. S-RES enforces P3 and the unchanged staying declarations textually (§8.4).

### 8.4 Exact tiles and rule invariants (REPLACED in v4)

All rules are stated normatively in A-BIND §B0; B9 and B10 give their tables, and B8 gives the check functions.

- **R-ISO (isolation).**
  - A subprogram `N` is isolated by its unique `end N;` in the region (the file, or a package span) and the nearest preceding `function N ` or `procedure N `.
  - A package specification or body is isolated by its unique `package [body] N is` and the next `end N;`.
  - A declaration is isolated by its unique start text and the first `;` at parenthesis depth 0.
  - All of this is on the N2 view, so string-literal contents cannot interfere. Any isolation failure is a problem, never a skip.
- **R-TILE (exact text).** Each of the 23 tiled subprograms (J19) equals `HEAD + " " + " ".join(SEGMENTS)` exactly (A-BIND §B4). `Diagnostic_Transport`'s two spans equal B4.24 exactly.
  - So the text fixes every declaration, read, guard, gate, decision call, write, return and handler, and their order and adjacency.
  - Each tile was derived from the S5 original and the v3 design by the author. Each v3 token is contained in it (§B.3 RR1).
- **R-TRANS (transports).** Removing the listed clause block, subtypes, helpers, constants and profiles exactly once from each transport specification must leave `package T is end T;`. Removing the body helpers and moved subprograms from its body must leave `package body T is end T;`.
  - Each helper's isolated N1 text has the listed sha256: 116 helpers, each identical to its S5 original (observed by a read-only author script; A-BIND §B9.3).
- **R-INV (scoped clause inventory; replaces v3 O6 (b) and (c)).**
  - (i) Each designed scope's ordered clause tuple equals its listed tuple.
  - (ii) The residual tuple equals the 36 observed S5 clauses (J15) with R-DEL-1 applied from PK-6b (35 clauses, J14; 13 renamings, J13).
  - (iii) The context holds no clause.
  - (iv) The specification holds no clause.
  - (v) Each scope has exactly one `renames` per listed package renaming.
  - (vi) `use all type` occurs nowhere.
  - (vii) No `use` clause names a SPARK unit or a renaming of one.

  The original 15 unit bodies hold 126 clauses (J12), of which 122 are at package level (J21).
- **R-ALIAS (makes O6 (a) enforceable).** None of the listed `(alias, routine)` selections occurs, for example `K.Diagnostic_Start` or `E.Decide`. With R-INV (v)–(vii), the only way left to denote an Appendix C routine is its full expanded name (A-BIND §B0.5, §B9.4).
- **R-W (write forms; replaces v3 O4 and R-W).**
  - Every `.all :=` and `Write_Data (` call in every designed scope is matched by exactly one row W03–W22. A scope without rows must contain no foreign write.
  - The row's target text occurs exactly once.
  - Its provenance spans occur exactly once.
  - Every occurrence of a closed identifier lies inside a span.
  - The assignment counts are exact: zero everywhere except WF-X `O`, which has two (A-BIND §B0.6, §B10).
- **R-GATE (replaces v3 O5 and A1 by order).** For every acceptance object:
  - its gate text occurs exactly once;
  - its discriminant (`.Ok` or `.Verdict`) is selected exactly once in the scope, inside the gate;
  - no other selection precedes that test;
  - the object is never assigned, except finalization `O`, whose assignments R-W binds (A-BIND §B0.7, §B10.3);
  - completeness: every `X.Ok` and `case X.Verdict is` in a designed scope belongs to an object with a gate row there.
- **R-RES, S-RES (residual identity).**
  - In the body, removing the designed spans and undoing the recorded glue edits must reproduce the S5 residual sha256 `187242f4aaaddd7eaecc996659b305c1fd2329e419a090c3b1d4c55dcc08669e`.
  - In the specification, removing the four subtypes and the relocated declarations must reproduce `4c533f63b629146beea81b20c7bddcae385beafb61ffc62cc866212f6d5c4c6b`.
  - Both values were observed on S5 by a read-only author script and re-computed while drafting.
- **R-LAYOUT.** The runs and boundaries of §3.6.
- **R-GLUE.** Each of GE1–GE9 occurs once. Undoing them reproduces the S5 sha256 of `Decide_Raw_Context` (`56dc5c69…6a99`) and of `Decide_Raw_Metadata` (`99a13436…bfa`). An author script applied and undid the nine edits on the S5 text and obtained both values.

#### 8.4.1 What each v3 rule became (no silent generalization, no waiver)

| v3 rule | v4 | Why |
|---|---|---|
| O1 isolation | R-ISO, carried and extended to declarations and package spans | — |
| O2 order (ordered subsequence) | R-TILE | Ordered occurrence does not fix adjacency or provenance (V3-RC4); exact text does |
| O3 multiplicity | R-TILE, with R-W's exact write matching kept as an invariant | as above |
| O4 result-to-write (constant result, with two stated exceptions) | R-W per form (WF-C/A/F/O/B/R/P/X/H) | The blanket rule contradicted the B4 rows (§A.4 L5). It is withdrawn and every form is stated, not widened. |
| O5 gating (discriminant test after the declaration, at most `begin` between) | R-GATE: exact gate text; the test occurs once, inside the gate; no earlier payload selection | Makes A1 enforceable |
| O6 (a) full expanded names | R-ALIAS with R-INV (v)–(vii), plus R-TILE | Was enforced by tokens only |
| O6 (b) renames | R-INV (i), (ii), (v), with B9 inventories | Was deferred |
| O6 (c) "only non-`use type` clause is `use <Unit>_Transport;`" | R-INV (i): exact listed tuples, each clause classed T, L or A with a reason | The v3 restriction could not be satisfied (§A.4 L1); v4 lists, rather than permits, every clause |
| O7 retargeting | R-GLUE and R-RES (exact edits; whole-residual identity) and R-ALIAS (no `K.` call of a removed or Appendix C routine) | — |
| K3 quoted strings | K3 parsed membership | §A.4 L4 |
| (none) | R-TRANS, G9, G10, K5, K6, S-RES, R-LAYOUT | v3 promised these properties without a check (A-BIND §B11) |

### 8.5 Diagnostic confinement, 8.6 Preserved predecessor assertions, 8.7 Identity binding

v3 §8.5 (D1–D5), §8.6 (PP1–PP3 and the four recorded edits E1–E4) and §8.7 (identity layers I1–I7) are part of v4 verbatim. The new tables of §8.1 follow the same stage discipline (A-BIND §B1.1). The identity layers bind every touched file exactly as in v3.

### 8.8 Mutation controls (C-09, static, temporary trees, no WORLDLINE run) (REPLACED in v4)

Each mutation must produce at least one problem. The v3 list is kept, reinterpreted for tiles, and A-BIND §B12 adds mutations for every v4 rule.

| Target | Mutations |
|---|---|
| Each relocated export | Move its declaration back to the old spec; duplicate it; rename the external name; add an `Import` or `Link_Name` alias anywhere in the closure; change a parameter subtype; reorder two statements of its tile; delete a required SPARK call or move it outside the isolated body; replace the written object; add a second write; remove the discriminant test; add a `renames` of a SPARK unit |
| The component | Alias a pending symbol from a second component file; the K3, K5 and K6 mutations of A-BIND §B12 |
| RC1 | Declare an `Atomic` object in the C_API body; call `Put_Line` outside `Mark`; drop or reorder a diagnostic site |
| Predecessors | Apply any edit outside the four recorded ones; reorder the override chain |
| v4 rules | A-BIND §B12, which covers R-TILE, R-TRANS, R-INV, R-ALIAS, R-W, R-GATE, R-RES, R-GLUE, R-LAYOUT, K3, K5, G9 and K6 |

### 8.9 What these checks do not establish

v3 §8.9 is part of v4 with R11. D-15, D-34 and D-38 remain OPEN.

---

## 9. RC5: lineage, stages, append schedule, characterization, representation placement and seal limits

v3 §9.1–§9.3, §9.5 and §9.7–§9.9 are part of v4 verbatim; v3 §9.4 is carried with R12. §9.6 is replaced. PACKET_PLAN status is unchanged by the author: it remains for the reviewer, NOT_CLOSED until reviewed.

### 9.6 PK-0: original-behaviour characterization (REPLACED in v4; V3-RC5)

PK-0 records, in `tests/capi_characterization.json` (I5), the original source's defined effect for every export and input class. It must pass on L0's original library and on every later stage. A baseline behaviour exposed as a defect stays an original obligation; PK-0 cannot delete or redefine it.

#### 9.6.1 Effect classes

| Class | When | Defined effect asserted | Not asserted |
|---|---|---|---|
| **R0** pre-capture guard refusal | A refusal decided only from by-value arguments and address arithmetic, before the first foreign read | The refusal code. No foreign read and no foreign write. The diagnostic lines, where the export emits them (C-06). | — |
| **R1** post-capture guard refusal | A header, transport or value guard evaluated after one or more captures | The refusal code. The reads performed are exactly the frontier listed for that guard in §9.6.2, and nothing beyond it is read. No foreign write. | — |
| **R2** element refusal | A refusal at element k of a staged loop (row, plan, disk, pair) | The refusal code. Frontier: everything read before the loop, plus elements 1..k (for paired elements, both members of pair k in source order). Later elements and later arrays are unread. No foreign write. | — |
| **R3** typed outcome | A result that the code or a typed record encodes: protocol `Status`; ledger `Status` inside `Result`; lifecycle status; finalization `Reason` 0/1/2; completion reasons including `History_Invalid`; the mixed entry's `Decision` | The code and the exact writes, in canonical order (none for protocol refusals and for the mixed entry) | — |
| **S** success | Normal completion | The code and the exact writes, in canonical order | — |
| **H** handled internal exception | An Ada exception raised inside the handled region by the export's own code or a callee: for example `Storage_Error` from an allocation or from runtime `Big_Integer` code, or a language-defined check failure | The handler's code (255, -1, `Null_Address`, `False` or `Invalid_Request`); the exception diagnostic line when diagnostics are active, for exports whose handler calls the exception transport. No foreign byte outside the export's write set changes. The handler undoes no write: writes that completed before the raise point persist, and they were made in the export's canonical order. | Which writes have completed when the handler runs, and whether a write in progress completed partly (§9.6.4) |
| **X** outside the premises | Foreign-pointer faults; violated documented premises | nothing | everything (§9.6.5) |

Class-H codes are failure mappings, never accepted semantic refusals (D2 review C-ABI). A handled native failure on an originally accepted input remains a failure of the obligation (§3.5; H/HANDOFF.md:129-131).

#### 9.6.2 Read frontiers per export (S5 lines; observed by reading)

"R0" lists the guards that refuse before any foreign read. "Capture" lists the first foreign reads in source order. "R1" gives each post-capture guard with its exact frontier (the foreign objects read before it). "R2" gives the element frontiers. "Writes" gives the canonical order.

| # | Export (S5 body) | R0 (no foreign read) | Capture, then R1 with its frontier | R2 frontiers | Writes (canonical order); handler |
|---|---|---|---|---|---|
| 1 | `wl_resources_can_reserve` (`worldline-resources_c_api.adb:36-64`) | the whole chain `:45-52` (flag, four extents) → 255 | no R1. Reads: the four `Decode` copies, actuals of one call (`:53-58`), in an unspecified mutual order | — | none; returns 1/0; handler 255 (`:63-64`) |
| 2 | `wl_recovery_select` (`worldline-recovery_c_api.adb:53-85`) | the chain `:61-66` (flags; Expected shape; Live and Prepared shapes only when present) → 255. Absent markers' pointers are never examined. | no R1. Reads: Expected (`:69-70`), then Live if present (`:71-74`), then Prepared if present (`:75-78`). Absent markers are never read. | — | none; handler 255 (`:84-85`) |
| 3 | `wl_recovery_authorization_decide_v2` (`worldline-recovery_authorization_c_api.adb:123-150`) | `:129-136` (lengths, shapes, alignments) → -1 | capture Input (`:139`). R1 `not W.Well_Formed (Raw)` (`:141-142`) → -1; frontier: Input. | — | Output once (`:146`); return 0; handler -1 (`:149-150`) |
| 4 | `wl_recovery_authorization_decide_v3` (`worldline-recovery_authorization_v3_c_api.adb:132-167`) | `:139-148` → -1. A zero-length arena's pointer is not checked. | capture Input (`:151`); allocate Data (`:152`); read the whole Arena unconditionally (`:154-157`). R1 `not W.Well_Formed (Data, Raw)` (`:158-159`) → -1; frontier: Input and the whole Arena. | — | Output once (`:163`); handler -1 (`:166-167`) |
| 5 | `wl_recovery_protocol_decide_v1` (`worldline-recovery_protocol_c_api.adb:44-70`) | `:49-55` → -1 | capture Input (`:58`). R3: `Apply` (`:62`); `Status /= Success` → return `Status` (`:63-64`); frontier: Input; no write. | — | Output once (`:66`); return 0; handler -1 (`:69-70`) |
| 6 | `wl_reservation_lifecycle_plan` (`worldline-reservation_lifecycle_c_api.adb:53-118`) | `:61-74` (bounds, flags, request fields, three extents) → 255 | reads: Data (`:77`); rows one at a time (`:95-96`) | row k (`:98-101`) → 255; frontier: Data and rows 1..k | R3: mask bytes ascending, only for `No_Change`/`Removal_Planned` (`:109-114`); returns the status code (`:115`); handler 255 (`:117-118`) |
| 7 | `wl_resource_ledger_compute` (`worldline-resource_ledger_c_api.adb:108-176`) | `:118-133` → 255 | reads: Data (`:136`); rows one at a time (`:147-148`) | row k (`:150-155`) → 255; frontier: Data and rows 1..k; no write | unconditional, in this order: Detail_Data bytes ascending (`:164`), Total_Data bytes ascending (`:165`), Details entries ascending (`:166-170`), Result (`:171-172`); return 0 for every typed status (R3 inside Result); handler 255 (`:175-176`): class H after a write leaves the earlier writes in place |
| 8 | `wl_resource_ledger_headroom` (`:178-223`) | `:186-196` → 255 | capture A, W, F (`:199-201`, in this order). R1 `Shape` of A/W/F (`:203-204`) → 255; frontier: the three quantity records (Data unread). Then Data (`:207`). | — | Output bytes ascending (`:215`), Result (`:216-218`); return 0; handler 255 (`:222-223`) |
| 9 | `wl_resource_policy_admit` (`worldline-resource_policy_c_api.adb:113-182`) | `:120-130` → 255 | capture Input (`:133`). R1 ten `Shape` tests (`:135-143`) → 255; frontier: Input (Disks and Data unread). | disk k (`:156-162`) → 255; frontier: Input and disks 1..k (Data unread). Data is read last (`:168`). | Result once (`:171-176`); return 0; handler 255 (`:181-182`) |
| 10 | `wl_evaluation_history_select` (`worldline-evaluation_history_c_api.adb:127-190`) | `:133-143` → 255 | capture Query (`:146`), then the whole Data arena (`:147`). R1 query validity (`:151-155`) → 255; frontier: Query and Data (Final_Row and rows unread). | if `Final_Present = 1`: Final_Row (`:159`) → 255 at `:161`; frontier: Query, Data, Final_Row. Row k (`:167-170`) → 255; frontier: Query, Data, Final_Row if present, rows 1..k. | Output once (`:185`); return 0; handler 255 (`:189-190`) |
| 11 | `wl_pending_decide_v1` (`evaluation_pending_c.adb:105-173`) | `:111-115` (Input and Output extents, their disjointness) → 255 | capture Input (`:118`). R1 the header, transport and value chain (`:120-133`) → 255; frontier: Input (Data and Rows unread). Then Data (`:136`). | row k (`:143-151`) → 255; frontier: Input, Data, rows 1..k | Output once (`:165-168`); return 0; handler 255 (`:172-173`) |
| 12 | `wl_pending_decide_v2` (`evaluation_pending_v2_c.adb:126-197`) | `:132-136` → 255 | capture Input (`:139`). R1 `:141-154` → 255; frontier: Input. Then Data (`:157`). | row k (`:164-173`) → 255; frontier: Input, Data, rows 1..k | Output once (`:188-192`); handler 255 (`:196-197`) |
| 13 | `wl_resource_run_ledger_check_v1` (`resource_run_ledger_c_api.adb:185-222`) | `:195-205` → -1 | capture Input (`:207`); allocations (`:208-211`); unconditional reads of Data (`:213`), Before (`:214`), Proposed (`:215`), Native (`:216`). R1 `not W.Well_Formed (…)` (`:217`) → -1; frontier: Input and all four arrays. | — | Output once (`:219`); return 0; handler -1 (`:222`) |
| 14 | `wl_chain_authority_replay_v1` (`worldline-chain_authority_c_api.adb:64-102`) | `:72-83` → -1 | capture Anchors (`:85`); allocate Owned (`:86`). R1 `not W.Well_Formed (H)` (`:88`) → -1; frontier: Anchors (rows unread). | row k (`:91-94`) → -1; frontier: Anchors and rows 1..k | Output once (`:99`); return 0; handler -1 (`:102`) |
| 15 | `wl_completion_decide_v1` (`evaluation_completion_c.adb:393-527`) | `:401-404` (Input and Output extents, disjointness) → 255 | capture Input (`:406`). R1 the chain `:408-421` → 255; frontier: Input. Then Data (`:423`). | journal row k (`:443-447`), captured (`:458-461`), retained (`:470-473`), history (`:479-482`), required (`:488-491`), each loop after the previous one → 255; frontier: Input, Data, every earlier array, elements 1..k of the current one | Output once (`:522`; R3 reasons written in `Response`); return 0; handler 255 (`:526-527`) |
| 16 | `wl_completion_raw_decide_v1` (`:529-692`) | `:538-541` → 255 | capture Input (`:543`). R1 `:545-562` → 255; frontier: Input. Then Data. | as 15, except that captured element k is staged as check row k (`:599-602`), then Wire k (`:605-606`), then Confinement k (`:607-608`) → 255 at `:609-612`. Post-decision refusal 255 (`:657-671`) after all reads, before any write. | Output once (`:687`); handler 255 (`:691-692`) |
| 17 | `wl_completion_metadata_matches_v1` (`:909-985`) | after the enter mark (`:921`): `:922-926` → mark, 255 | capture Input, then Context (`:929-930`). R1 `:932-941` → mark, 255; frontier: Input and Context. Then Data and Projected_Data (`:945-946`). | pair k: Original (`:953-954`), then Owned (`:955-956`) → value, 255 (`:957-963`); frontier: Input, Context, both arenas, pairs 1..k | no foreign write; returns 1 or 0 (`:978`); handler: exception line, 255 (`:982-985`) |
| 18 | `wl_native_diagnostic_control_v1` (`:73-88`) | no foreign memory | — | — | codes 0/1/2 and stderr lines (§4.6); no handler |
| 19 | `wl_finalization_decide_v1` (`evaluation_finalization_c.adb:121-256`) | after the enter mark (`:127`): `:128-133` → mark, 255 | capture Input (`:136`). R1 the chain `:138-156` → mark, 255; frontier: Input. Then Data (`:160`). | plan k (`:170-177`) → value, 255; frontier: Input, Data, plans 1..k. Operations 0 and 1 read no row. Operations 2 and 3: row k (`:191-197`) → value, 255; frontier: Input, Data, all plans, rows 1..k. | R3: Reason 0/1/2 in `Response`; values reason and promotion (`:247-248`); Output once (`:249`); return 0; handler: exception line, 255 (`:253-256`) |
| 20 | `wl_collapse_decide_finalization_v1` (`:357-508`) | after the enter mark (`:411`): collapse extent `:412-416` → mark, `Invalid_Request` | capture Collapse (`:419`). R1 `Needed = Invalid_Collapse` (`:420-425`) → mark, `Invalid_Request`; frontier: Collapse. Then, per needed source, the nested entry with its own frontiers (Kind 1: row 16; Kind 2: row 19, then a re-read of the Input header, `:390`), readiness refusals (`:429-447`). Agent: extent refusal with no agent read (`:453-458`); then `Owned_Agent` (`:461`) and its refusal (`:462-466`). Context joins with nested frontiers (`:473-483`). | — | no foreign write (nested entries write Ada-owned locals, D-26); not Authorized → `Decision`, metadata unread (`:489-490`); metadata joins only when authorized (`:491-502`); handler: exception line, `Invalid_Request` (`:505-508`) |

v3's "guard refusals: return before any foreign read or write" (v3:1946) is withdrawn. It holds for R0 only.
- Rows 3, 4, 8–17, 19 and 20 have R1 refusals that follow captures.
- Row 5's post-capture refusal is the typed R3 status.
- In rows 11, 12, 15, 16, 17 and 19 the transport guards (extents and disjointness of fields of the captured record) are themselves post-capture.

#### 9.6.3 Handled internal exceptions (class H): the defined part

- **Single-write exports** (v2, v3, protocol, policy, history, pending v1 and v2, run ledger, chain, completion decide and raw, finalization decide). Every read and allocation precedes the one write statement. In v2, v3, run ledger and chain the final `W.Decide` call is evaluated inside that statement.
  - An exception raised before that statement gives the handler code and no write.
  - An exception raised while that statement executes (for example inside `W.Decide`, whose result the original assigns directly through the access value) gives the handler code. Whether the target is then unchanged, partly or fully written is OPEN (§9.6.4).
- **Multi-write exports** (ledger compute, ledger headroom, the lifecycle mask loop). The canonical write order is fixed (§9.6.2, rows 6–8).
  - An exception raised after some writes gives the handler code.
  - The completed writes are not undone and may persist. They are earlier writes in the canonical order.
  - This is the defined original behaviour that the review identified for the ledger (`worldline-resource_ledger_c_api.adb:162-176`, `:212-223`).
- **No-write exports** (resources, recovery, completion metadata, the mixed entry, diagnostic control). The handler code only (none for diagnostic control, which has no handler).
- **Exceptions identified by source reading:**
  - `Storage_Error` from caller-count-sized allocations, in every export that declares such arrays;
  - `Storage_Error` from runtime `Big_Integer` code reached through `Resource_Run_Ledger_Wire.Decide` and `Evaluation_Finalization.Seal` (D1);
  - language-defined check failures, which the proof obligations require to be unreachable.

  PK-0 asserts class H only through the optional C-12, under `RLIMIT_AS`, at allocation points: the code, and that no byte outside the write set changed. That is never native-cost closure and never an accepted refusal.

#### 9.6.4 OPEN or implementation-dependent (only these)

- **(a) Failure location.** Where a native failure is raised: inside runtime `Big_Integer` code, an allocation, or a check. Hence which writes have completed when the handler runs. For language-defined check failures, RM 11.6 permits the implementation flexibility about whether assignments near the raise point were performed (advanced-ada ch13).
- **(b) Copy atomicity** of a write in progress: a record assignment through an access value, a `Write_Data` loop, or a function result built in place in the foreign object.
- **(c) Native write construction** of every successor form (A-COST §C19, D-36).
- **(d) Preservation of possible outcomes.** That the successor adds no class-H outcome on an originally accepted input (C21-d) and removes no defined outcome.

#### 9.6.5 Outside the premises (class X), kept separate

- **Foreign-pointer faults.** There is no expectation that a fault becomes 255 or -1, and none that it becomes an Ada exception in a Python-created thread (D-23).
- **Violated documented premises:**
  - ledger output disjointness (`worldline-resource_ledger_c_api.ads:6-9`);
  - lifecycle Removed disjointness (`worldline-reservation_lifecycle_c_api.ads:5-8`);
  - history and chain output disjointness (unchecked header premises);
  - the immutability of re-read objects (D-27);
  - live allocation and custody (§14).

PK-0 asserts nothing for class X, and no control encodes an expectation for it.

#### 9.6.6 Controls built on the table

- **C-01:** no write on R0, R1, R2 and no-write R3 paths only, with outputs pre-filled `0xA5` (R13). Never on H or X.
- **C-03:** overlap expectations are export-specific; both kinds are kept, as in v3:
  - refused overlaps: pending v1/v2 Output against the request, Data and Rows; completion Output against its inputs; context and metadata arrays against the descriptor; finalization decide;
  - accepted overlaps: v2, v3, protocol same buffer, run ledger, policy Result against inputs.
- **C-05:** PROT_NONE pages placed exactly beyond each refusal's frontier and on absent or unneeded inputs, in child processes. It asserts normal exit and the expected code only (R14).
- **C-12 (optional):** forced allocation failure, as in §9.6.3.
- **C-13 baseline:** unchanged from v3. On L0's library it records every layout export value, the ctypes sizes, offsets and alignments, and the C header `sizeof`/`offsetof`/`_Alignof`, for every record type a representation repair may touch.
- **Proposed stronger behaviour is separate.** C-14 (WF-C and WF-A exports only; R15) is review evidence for D-36. It is never a baseline assertion and never a PK-0 pass condition.

---

## 10. RC3 (carried)

v3 §10 is part of v4 verbatim.

---

## 11. RC6: source and native cost summary (REPLACED in v4; complete map in A-COST)

### 11.1 Withdrawn statements

- **v2 statements** (carried): v2:2510 ("passed by reference"); v2:2503 and v2:2537 ("as many times as on the original path … all other exports 0"); v2:156 ("constant-time"); and v2:2543's per-row statement as a complete account.
- **v3 statements** (new; quoted exactly in A-COST §C1.2):
  - the Ri "returned on the secondary stack and copied" legend;
  - X1's "real call";
  - X3's "but it executes";
  - X4's mandatory temporary;
  - the C14 "-O0" elision claim;
  - C12's "five array actuals";
  - C18's single length tests;
  - the blanket `ALLOC: =` lines;
  - v3:267's "completes a SPARK result first and copies it once" for policy and ledger;
  - v3:668-669;
  - v3:2074 and v3:2077.

### 11.2 Classification rules

- **Two layers.** Every A-COST row separates the source layer (what the text and the language semantics fix) from the native layer (generated code). Every native item is OPEN and is closed only by C21 evidence.
- **Parameters (RM 6.2).** Elementary types are passed by copy. These are all `U8`, `U32`, `I64`, `Size`, `Interfaces.C.int`, `Boolean`, the enumerations, and `System.Address` (a private type whose full type is modular, `G/…/adainclude/system.ads:67`, `:117`).
  - Reading the declarations found no by-reference type in any value-routine profile. An exhaustive type-closure analysis is OPEN (A-COST §C2).
  - Every other parameter type (untagged records and arrays) has an unspecified mechanism (RM 6.2(11)). GNAT's choice for the matching build is OPEN. No row claims "no copy".
- **Results.**
  - A definite result is one source result per call; whether it is built in place or copied is OPEN.
  - An indefinite result into a constrained object includes the language-defined length or discriminant check (source). Storage and copy are OPEN; the installed User's Guide's secondary-stack statement is documentation only (A-COST §C0).
- **Calls.** A new value-routine call is a source call into another unit. Emitted calls and inlining are OPEN. The documented ordinary inlining conditions (GN `gnat_ugn.info:14798-14835`) are cited, not relied on (A-COST X1).
- **Checks.** Language-defined checks required by the source semantics are listed (S-CHECK). Whether matching code emits each test is OPEN (A-COST X3).
- **Allocation.** `ALLOC =` covers only the original allocation statements named in each row. New source objects are listed separately, and their native storage is OPEN.
- **Builds.** Both core builds use `-gnatVa` and `-O2` without `-gnatn` (`core/worldline_core_sources.gpr:11-12`); the checks build adds `-gnata` (`:16-17`); the component build uses `-O0`. Every existing `Pre`/`Post` on a called relation is evaluated under `-gnata` wherever the call occurs.
- **Units and improvements.** Source counts are not allocation or instruction counts (D2 review C-UNIT). No native improvement is claimed (C-COPY).

### 11.3 Per-export summary (source layer; native layer OPEN throughout)

| Export | Re-evaluations added (V3, LD5) | New source calls and objects | New initialization | New `-gnata` evaluation | Original allocations (`=`) | Write form (A-BIND §B10) |
|---|---|---|---|---|---|---|
| resources | flag re-check | one call level for four arrays | — | — | four `Decode` results | none |
| recovery select | `Presence_Valid` re-check; `Present` per marker | transport marker constants, plus the `Marker_Of` result per marker | — | — | Expected's `Copy`; the marker objects move into SPARK (not `=`) | none |
| v2, v3 | one `Well_Formed` each (rel 1 → 2, chk 2 → 3 per accepted call; J06, J07) | the `Owned` constant | — | — | v3 `Data` | WF-C |
| protocol | none | none | — | — | as original | WF-P |
| lifecycle | `Request_Valid` in `Requested_Of` | per-row acceptance; one `Mask_Byte` call per byte | — | — | `Arena`, `Typed_Rows`, `Mask` | WF-F, WF-O |
| ledger compute/headroom | none | per-row acceptance; per-detail cross-unit `Encode_Quantity`; `Result_Of` results; `HI` | — | — | `Arena`, `Typed_Rows`, `Slots`, `Detail_Arena`, `Total_Arena`, `Typed_Details`; `Arena`, `Output_Arena` | WF-B, WF-F, WF-O |
| policy | none | input and per-row acceptance; `Encode_Decision` result | — | — | `Rows`, `Arena` | WF-F (WF-C `Decision`) |
| history | none | query, final-row and per-row acceptance; `Select_Result` | — | — | `A`, `History`, `F` | WF-C |
| pending v1/v2 | header and fields re-check | per-row acceptance; `Decide_Value` result | — | — | `A`, `J` | WF-A |
| run ledger | none | `Check_Decision` result (four array actuals and one record actual; J10, J11) | — | — | `Data`, `Before`, `Proposed`, `Observed` | WF-A |
| chain | `Well_Formed (H)` re-check | per-row acceptance; `Replay_Value` result | — | — | `Owned` | WF-A |
| completion decide/raw | header and fields re-check; `History_Index` | per-row acceptance for five arrays; `in out History` and `out Response` actuals | `Response := Initial_Response` (moved, same values) | `History_Index` Post | the seven arrays (A-BIND §B4.14) | WF-R |
| completion context/metadata | `Context_Header_Valid`, `Context_Fields_Valid` re-check | field, row and required-pair acceptances | acceptor locals (same values as the original default initialization) | — | the original arrays (A-COST §C15) | none |
| finalization decide | header and fields re-check; operation selector | plan and row acceptances | `S`, `Response` moved inside (same work) | — | `A`, `Required`, `Captured` | WF-X |
| final context / mixed | `Promotion <= 1`; `Bound` rebuilt per projected row | `Final_Projected_Row`, `Final_Projection`, readiness results; the delta aggregate | `Native`, `Ordinary`, `Finalized` (D-28) | — | as original | none |
| diagnostics | none (atomic accesses unchanged) | one call level per site; two `*_Fits` evaluations per reached composition and the nested `Mark`'s pair (J06, J08); +1 `'Image` per active value site (J09); `String` results | — | optional Posts only if required | none | none |

### 11.4 D-36: write construction per form

A-COST §C19 gives the construction account per export and form: original source construction, successor source construction, and the native items, all OPEN. For every row the matching builds must establish:
- the order in which the stored value is constructed;
- its copy and padding effects;
- its exception and no-write semantics.

The malformed-input fixture (`tests/test_recovery_witness_relation.py:174-179`) establishes none of them. No global transactional-write claim is made. No `Storage_Error` is accepted as a refusal of a genuine accepted computation.

### 11.5 Original native blockers (all OPEN)

v3 §11.5 is part of v4 verbatim.

---

## 12. to 16. (carried)

v3 §12 (ABI and behaviour matrix), §13 (R4), §14 (R5, OB-048) and §16 (operator items D-13 and N-06) are part of v4 verbatim. v3 §15 (controls) is carried with R13–R15. No operator item is decided, approved or authorized here.

---

## 17. Rulings and carried items (REPLACED in v4)

| Item | v4 disposition |
|---|---|
| D-01 … D-04, D-06 … D-12, D-14, D-17, D-20 … D-27, D-29 … D-33, D-35, D-37 | Carried from v3 (v3:2281), unchanged in substance; each stays OPEN where v3 said OPEN. |
| D-05 | OPEN (review ruling). v3:2282's decoder inventory and decision procedure are carried unchanged. No helper Pre is approved. |
| D-13 | Operator item §16.1 (OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7). |
| D-15, D-34, D-38 | OPEN: matching native export, layout and loaded-library evidence, and installed-tool legality, including name resolution in the integrated body (§3.6) and any warning on a transported clause (A-BIND §B0.9). |
| D-16 | Withdrawn with LD4; replaced by LD4-R (§4). |
| D-18 | CLOSED_AT_DESIGN_LEVEL for the index design (review); proof OPEN (§5.4). |
| D-19 | OPEN (§5.5). |
| D-21 | Pre-existing `Authority_Glue` value decisions: unchanged, enforced by R-RES; boundary surface (§14). |
| D-28 | Conditionally acceptable at design level (review); native costs OPEN (A-COST §C16). |
| D-36 | OPEN for every write form (§3.4, §11.4, A-COST §C19). C-14 is proposed behaviour for WF-C and WF-A exports only. |
| N-01 | §10; a lead-owned strict obligation. |
| N-02 | Enforced by G7. |
| N-03 | OPEN; v3:2292 carried unchanged (existing callee full strict proof; no PROVED_ROW transfer). |
| N-04 | CLOSED_AT_DESIGN_LEVEL for the explicit `Classify` enrollment (review); unit-wide body coverage still required. |
| N-05 | OPEN; v3:2294 carried unchanged. No exact-set-to-subset reinterpretation or removal. |
| N-06 | Operator item §16.2. |
| N-07 | CLOSED_AT_DESIGN_LEVEL for the explicit pending `Decide` enrollments (review); proof and native body obligations OPEN. |
| R2_NINE_CONDITIONS | Mapped to v4 checks (§8, A-BIND §B11): (1) relocation map, §6 and A-BIND §B2–§B3; (2) one binding, G1–G10 and K1–K6; (3) an identical C profile, P1–P3 and S-RES; (4) an executable decision path, R-TILE, R-W, R-GATE, R-ALIAS, R-GLUE and D1–D5; (5) predecessors, PP1–PP3; (6) complete pins, §8.7; (7) append-only, §9.3; (8) the exact exception set: boundary unchanged, no core unit newly Off, all units On (`UNANALYZED_BOUNDARY` unchanged); (9) full evidence identity and strictness: the unchanged command and floor, zero unproved, justified and `pragma Assume`, complete reports, source and library identities. For the reviewer; NOT_CLOSED until reviewed. |
| APPENDIX_C | CLOSED_AT_DESIGN_LEVEL (review); Appendix C carried verbatim. |
| PACKET_PLAN | §9 with §9.4 (R12) and §9.6 replaced, plus A-BIND §B1.1. For the reviewer; NOT_CLOSED until reviewed. |

---

## 18. Everything that remains OPEN

- **Source and installed legality.**
  - No successor source exists.
  - Installed-tool SPARK legality of every changed unit (D-38), of the External abstract state and of the `'Image` use.
  - Name resolution in the integrated C_API body, and any warning on a transported clause (§3.6; A-BIND §B0.9).
- **Proof.**
  - Flow, RTE, termination and functional obligations of the 95 new routines (J36) and of every called relation, including the N-03 callees, the D-05 decoders, the D-18 index and the D-19 branches.
  - Zero unproved, zero justified, zero `pragma Assume`; floor 251; complete reports and per-unit coverage.
  - Every strict warning class, including N-01's 736 representation warnings (J51); the 119 in moving code (J54) are not resolved by moving.
- **Manifest and composition.**
  - The override, tables and edits are unwritten, and the tile text is an author derivation awaiting review.
  - Pins are not regenerated, mutation controls (§8.8, A-BIND §B12) are unrun, and every stage review is pending.
- **ABI and native.**
  - Symbol export and mapping (D-15); layouts (D-34, N-01 evidence); calling conventions.
  - Write construction for every form (D-36).
  - Every native item of A-COST, including §C21-a…§C21-h.
  - The original native blockers (§11.5).
- **PK-0 characterization.** The class-H failure location and the copy atomicity of a write in progress (§9.6.4); foreign faults and premise violations are outside the characterization (§9.6.5).
- **Controls.** The 52-action roster, the lifetime controls, all additive controls C-01…C-16, and the provider and fault campaigns on the exact integrated candidate.
- **Boundary.** OB-048, custody, producer authenticity, immutability premises (D-27), foreign faults (D-23).
- **Integration.** The root-worker lane's changes to `core/worldline-c_api.adb` (§19).
- **Operator.** D-13 before PK-7; N-06 at deployment; all original Phase One operator gates.
- **Reviews.** The independent actual gpt-6.1-sol review of this design (V3-RC4, V3-RC5 and V3-RC6 closure, and the carried items), of every packet and stage, and of the final composition.

---

## 19. Integration collision with the root-worker lane (noted, not resolved)

The root-worker draft (`RW/source/core/worldline-c_api.adb`, 148068 bytes, sha256 `806f3972277d9385b0d32c5e3faf1bf6fb24f9024dbc1c8274411b8c1d0e3420`; observed) changes the file this design changes. S5's file is 56596 bytes (observed with `wc -c`, as in the v3 review). The draft has 25 package renamings and 29 lines beginning with `use` (observed by `grep`). This is an OPEN integration overlap, not an executed merge and not a qualification of the draft. The root-worker design and its review already record it (RWD `SEAM-DESIGN.md` P0-6; its review §1).

What v4 adds:
- **The v4 checks fail closed on the draft's additions.**
  - R-RES (the residual sha256), R-INV (ii) (the residual clause tuple) and R-LAYOUT (the export run must directly follow `end Owner_Audit_Decide;` and end at the final `end`) all refuse a C_API body that contains the draft's new code.
  - So the overlap cannot pass silently.
  - The remedy is a reviewed rebase (§9.1): a new L0 or packet base whose residual tables and hashes are re-observed and re-reviewed. The tables are never edited merely to fit.
- **Name-capture hazard.**
  - The draft declares package renamings at C_API body level (draft lines 1199-1220): `Y`, `J`, `D`, `A`, `X`, `E`, `T`, `N`, `W`, `O`, `Q`.
  - If the v4 export bodies were placed inside the scope of these declarations, use-visible transport renamings of the same name (`W`, `Q`, `A`, `E`, `T`) would not be use-visible there (RM 8.4). Tile text such as `W.Well_Formed (Raw)` or `use type Q.Byte_Count;` would then resolve to the draft's packages, or fail to resolve.
  - A rebase must rename or re-scope one side, and must re-run the identifier scan of §3.6 and the installed-compiler check (D-38).
- **Shared `Authority_Glue` text.** The draft's `Authority_Glue` differs in line numbers (for example `package K renames Evaluation_Completion_C;` at draft lines 766 and 841, against S5 761 and 836). GE1–GE9 and the glue hashes are S5-based, and they too must be re-observed on any rebased base.
- Nothing here chooses an integration order. That is a lead decision, reviewed as part of the affected packets.

---

## Appendix A. JACKAL results and observed counts

**JACKAL calls.**
- Every derived number in v4 is one of the calls J01–J58 to the MCP tool `jackal_exact`, recorded with input, `parsed`, `exact`, status and use in `jackal.json`.
- Each returned `status=exact`, `formal=false`, lane `rat`, assurance "exact rational arithmetic (not yet checker-covered)", evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`.
- Each carries these non_claims, verbatim:
  - "NOT formal-bounded: this lane carries no Lean-checked certificate"
  - "The epistemic class above is the STRONGEST claim this result supports"
  - "exact rational arithmetic (not yet checker-covered)"
- `exact` is exact rational arithmetic outside the Lean certificate chain. It is not `formal-bounded`, and it is informational about code correctness only.
- No ledger was used as evidence.

| Use | Calls |
|---|---|
| Inventory and relocation counts (60, 20, 40, 91, 51) | J01–J05 |
| Source evaluation counts: fit pairs, atomic reads, `Well_Formed (Raw)`, `*_Fits` with the nested pair, `'Image` delta | J06–J09 |
| Run-ledger actuals: four arrays; five actuals | J10, J11 |
| Clause counts: 126 in the original units, 13 and 35 after R-DEL-1, 36 in S5's C_API body, 122 at package level | J12–J15, J21 |
| Interface units under D-13 (i), and glue edits (9); retargeted sites (8) | J16, J17 |
| Designed packages (16); tiled subprograms (23) | J18, J19 |
| REQUIRED_PROVED lengths and slices (633, 98, 541, 543, 557, 563, 566, 623; 14, 57, 10, 37, 20; 98, 95; 633 by unit group) | J20, J22–J36, J57, J58 |
| CONTRACT_PINS keys (176, 178) | J37, J38 |
| C_API `External_Name` counts per stage (33, 36, 40, 41, 43, 49) and cumulative movers (5, 9, 10, 12, 18) | J39–J49 |
| Representation warnings (736 three ways; 617 staying; 119 moving), console errors (1158), address-to-access warnings (88) | J50–J56 |

**Observed counts carried from v3.** v3 Appendix A's observed rows remain valid for S5, which is unchanged. They are: REQUIRED_PROVED today 535; CONTRACT_PINS keys 169; the per-unit representation, console and address-to-access counts; the diagnostic site counts; 52 roster launches; and the burn-down ledger report. They are cited by reference (v3:2340-2384) and are not re-derived here.

**v4 observations** (read-only scripts or `grep`; not derived):
- the 36 residual clauses of the S5 C_API body with their lines and scopes;
- 116 transported helpers and their sha256;
- the 71-unit core `Library_Interface` and the 8-unit component `Library_Interface`;
- the residual, specification-residual and glue sha256 values;
- the 17 units of `CAPI_SPARK_UNITS`, equal to the Appendix C unit prefixes;
- the root-worker draft's size, sha256, 25 renamings and 29 `use` lines;
- the 87 v3 bound inputs re-hashed, all matching.

## Appendix B. Bound inputs (sha256, read while drafting v4)

- **v3's list** (v3 Appendix B, v3:2388-2476; the same files as v3 decisions.json `bound_inputs`) was re-hashed by a read-only script while drafting v4. All 87 entries matched.
- **Additional v4 inputs:**

```
a8a120c9a704177cdab5232a757f1ef405cb3ad1c694ff135cdd2e8f26a14aa7  D3/DESIGN.md
2517dd49f6b96e4fe23cd9631aead320ac038605b7286fe8fc5b72c92d99813a  D3/decisions.json
5ffb8736b6ce89f655041129991ed0bce4133941129bc7b1566b0da68695d32e  D3/APPENDIX-BINDINGS.md
c2a320a266fdd088c203e0d61f4cd7c5ea94f7b3b731f5be400f6b2f3d5b114f  D3/APPENDIX-COST-MAP.md
ab7efb2bc69d426f9480246bc2dd1f5e381d99879485d4385837ec1105d85223  D3/review/gpt61-v1/review.json
9fe93d9dd4257aa6ea188278fecedf5971a0ac34135a390f45908d3ac80b14b0  D3/review/gpt61-v1/REVIEW.md
e60cdead79d4db12c413a75044894c6cd793aafa20efb7c340c50d4c9d438f7e  D3/review/gpt61-v1/checks.json
7314f4de53972acbac91541d6a895072a50c264119dfe25e5c20b04ae63512ca  D3/review/gpt61-v1/review-freeze.json
806f3972277d9385b0d32c5e3faf1bf6fb24f9024dbc1c8274411b8c1d0e3420  W/work/protected-original-root-worker-repair-v1/source/core/worldline-c_api.adb
531d11282f811518b868470c0012f23a5e34bdbe3891ef39194cd8f230933f46  RWD/SEAM-DESIGN.md
a1e54a5b0f58e54fec854d3b3eda8780ddaa1a956169f1ac547e1a033722f496  RWD/review/gpt61-v1/REVIEW.md
721bce3ae3e7444fed19ee502c6ac6f3620c0aaedb3a5caa26c6c5a596f00bd4  RWD/review/gpt61-v1/review.json
e5b9984d2beadf12f35e3018aff33c23a47d93adea7bd886abe8df2db46574b6  D2D/INVENTORY.md
03fbf2461e857ddf9a3a0bdcf2515a14ccb6cd8498ade4e682a8a4bb60f02820  D2D/review/gpt61-v1/REVIEW.md
20e0447f556d9f18e9b8a24e5c96056317b52ccee3d29fe804c65cdee2c9c578  D2D/review/gpt61-v1/review.json
07f6d253c1a536946cdd0d5a26ddc4338d23c7c560a0f35bf918be51f576f17c  GN/share/info/gnat_ugn.info
```

These S5 files are read again and remain unchanged from v3 Appendix B: `core/worldline-c_api.ads`/`.adb`, `core/worldline_core.gpr`, `pending-component/pending.gpr`, `core/evaluation_completion.ads`, `core/evaluation_finalization.ads`, `runtime/worldline/proof_manifest.py`, the 15 unit pairs, `H/HANDOFF.md`, `H/START-CLAUDE.txt`, `P`, MAP and STRICT.

## Appendix C. REQUIRED_PROVED append, in packet order (98 names)

v3 Appendix C (v3 lines 2478-2589, sha256 `cee26f7f6c66613cdae339b9765b1ebe5f447a045c37999b7a571ed9200a45c6`) is part of v4 verbatim. The 535-name prefix is unchanged. The suffix has 98 names (J23) in packet order, and the final length is 633 (J20).

## Appendix D. Companion file identities

Each companion file was written with the Write and Edit tools to the location in the header. By last edit, they were completed in this order: `jackal.json`, `APPENDIX-COST-MAP.md`, `APPENDIX-BINDINGS.md`, `AUTHOR-NOTES.md`, then this file, then `decisions.json`. The identities below were observed with `sha256sum` and `wc -c` after each file's last edit. `decisions.json` records this file's sha256, and its own identity is reported in the handoff.

| File | sha256 | Bytes |
|---|---|---|
| `APPENDIX-BINDINGS.md` | `39ca995998d68b57d13c02796ee30d8826eecc07e750abf95a83f7d348f7d626` | 225451 |
| `APPENDIX-COST-MAP.md` | `5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4` | 73929 |
| `jackal.json` | `dec64a324685496195a7cb1c48e9ee3cf168255f8a1214d62b9491e42653f39d` | 13041 |
| `AUTHOR-NOTES.md` | `ccac4f63a00ed36199642b8691535890719879187b135ecce69f67edc5214b07` | 11329 |
