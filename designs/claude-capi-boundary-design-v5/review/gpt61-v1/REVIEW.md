# Independent design review: WORLDLINE Phase One C-API boundary consolidation DESIGN v5

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**

Actual reviewer model: **gpt-6.1-sol**. I am a different author from the Claude Code lead claude-opus-5-5 and its drafting subagent, and authored none of the material under review. This is a passive design verdict. **proof_acceptance=false; source_acceptance=false; phase_acceptance=false.** The required changes are V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE below.

Paths used for file:line evidence:

- W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow
- WT = W/work/claude-lead-isolation-v1/wt-1
- D5 = WT/designs/claude-capi-boundary-design-v5
- D4 = WT/designs/claude-capi-boundary-design-v4
- D3 = WT/designs/claude-capi-boundary-design-v3
- S5 = W/work/claude-composition-v5-beta/source
- H = W/outputs/claude-phase1-handoff-20261004
- P = /home/sicarii/Documents/complete-phase1-prompt.txt
- RW = WT/designs/claude-root-worker-seam-design-v2

## Identity and review boundary

The requested input hashes all match:

| Input | Computed sha256 |
|---|---|
| D5/DESIGN.md | 533f0e043fb991d015bcf16494674d791b6f8f8bd5049fef5a8e60594c9341de |
| D5/decisions.json | a069632a035b62f18d886112763472f13040779d2d5dd79c872a6d6ce951c55b |
| D5/APPENDIX-BINDINGS.md | f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2 |
| D5/jackal.json | 612d189e4edc29cda39c8e61ac3668bf04adb6abcda12728f7ec14272d4f46d4 |
| D5/AUTHOR-NOTES.md | ed45d1db766f3b03ec946946942a571ae50b0eae21e339c5724b5e2480280e47 |
| D4/APPENDIX-COST-MAP.md, carried | 5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4 |

D4's sealed review files and their freeze also verify. Their complete observed identities, all carried slices and replacement observations are retained in checks.json. The reconstructed B8 fenced block has sha256 e739e0395cd4e513920baa9b6e916bcafefecf66c1f53bef21e032c71eee79cb and parses as an AST. **It was never executed.** S5 proof_manifest.py was inspected as text/AST literals only, never imported or invoked.

I applied the installed Ada/SPARK, package/overloading/generic and high-integrity review guidance, retaining their revision labels. No WORLDLINE code, compiler, prover, build, test, service, reservation, window or storage operation ran. No SIA note was written. The ongoing root-worker review was not read. Writes are restricted to this review directory. The author's simulation and process disclosures are model-origin records, not control, proof or acceptance evidence.

## 1. V4-RC4-GATE: NOT_CLOSED

The fixed tiles, normative branch forms, gate rows and machine twin are reconciled for the currently designed objects. The remaining gap is the independent enforcement of the *sole* assignment exception across reviewed amendments.

| Sub-requirement | Assessment | Evidence |
|---|---|---|
| G.1: one identical rule in B0.7, DESIGN §8.4, tiles, B8, B10.3, B11, B12 and twin | B0.7 is the normative definition; V-R4/V-R5, the fixed tiles, forms and branch lists implement its Boolean/case rules. The twin's scope/object/kind/component rows equal B10.3, and its G21c exclusive texts agree. BR7 does not independently restrict assignment permission to the normative sole identity; that prevents complete closure. | D5/APPENDIX-BINDINGS.md:114-177,304-320,463-540,719-790,806-813,840-865; D5/DESIGN.md:176-198; D5/decisions.json:216-224 |
| G.2: False-variant rejection diagnostics only inside their rejection branch | Correct for the current rows. The Boolean form admits the existing Mark/Value diagnostics between the test and return. False components are confined to that interval; True components are after the completed gate. G16b confines components to their listed case alternative and permits none after end case. | D5/APPENDIX-BINDINGS.md:120-143,475-501,758-760; D4/APPENDIX-BINDINGS.md:628-631 |
| G.3: sole WF-X O exception with exact exclusive assignments before its test; no other assignment, whole pass or rename | The *normative and fixed-table* statement is exact: G21c, Finalization_Decide, O; uninitialized declaration; exact Needs_Rows region; then-assignment last in then; else-assignment the whole else; no elsif/conditional expression; immediate single test; Value only afterwards. BR7 rejects bare whole uses and assignments for non-wfx rows, and validates the recorded region/assignment positions for a wfx row. It lacks the independent sole-identity check described below. | D5/APPENDIX-BINDINGS.md:145-158,442-460,491-519,770-776; D4/APPENDIX-BINDINGS.md:684-688 |
| G.4: unchanged A1, diagnostics, codes, order and accepted domain | Preserved as a design obligation. RR-V4 enforces the unchanged A1 text: test before any payload; it does not license a discriminant exception or prohibit the original tested rejection payload. No diagnostic is removed or moved. B4, B6, B10.2 and the corrected read-frontier text are carried. Native/full-domain preservation remains OPEN. | D3/DESIGN.md:238-246; D5/DESIGN.md:137-142; D5/APPENDIX-BINDINGS.md:48,55,806,840; S5/core/evaluation_completion_c.adb:795-828; S5/core/evaluation_finalization_c.adb:168-256 |
| G.5: remove the contradictory after-entire-gate versus after-test/assigned-exemption rules | The earlier contradictory statements are explicitly replaced. Boolean and case branch restrictions repair their local defect. The new wfx mechanism is more precise about the existing region, but is still generic about which row may obtain assignment permission. | D5/DESIGN.md:26-30,176-198; D5/APPENDIX-BINDINGS.md:405-540 |

Spot checks against the bound B4 tiles and S5:

| Row | Correspondence |
|---|---|
| G16a | FA.Rejected_Position is selected only after if not FA.Ok, inside the field-rejection diagnostic before return 255. Expected/Observed are on the accepted path. This preserves S5's field-position diagnostic; it does not turn that False payload into an accepted-path read. D5/APPENDIX-BINDINGS.md:758; D4/APPENDIX-BINDINGS.md:628; S5/core/evaluation_completion_c.adb:795-804. |
| G16b | Row_Rejected carries no payload; Row_Field_Rejected uses Rejected_Field_Position in its own rejection alternative; Row_Accepted uses Row/Joined there. Original diagnostic sites and 255 outcomes remain. D5/APPENDIX-BINDINGS.md:759; D4/APPENDIX-BINDINGS.md:631; S5/core/evaluation_completion_c.adb:812-828. |
| G21c | The exact region equals the carried v3 §5.1 block. Operations 0/1 do not read or pass Captured; its allocation still occurs for all operations. Reason/promotion diagnostics precede the sole output write and return 0; handler diagnostics and 255 remain. D3/DESIGN.md:729-749; D4/APPENDIX-BINDINGS.md:684-692; S5/core/evaluation_finalization_c.adb:155-256. |
| G07 | D.Row and D.Slot are used after the 255 rejection gate; the original staged row acceptance and write order remain. D5/APPENDIX-BINDINGS.md:739; D4/APPENDIX-BINDINGS.md:454-461; S5/core/worldline-resource_ledger_c_api.adb:115-176. |
| G19a/G19b | D.Item follows the per-row gate; O.Value follows the final gate and is stored once. Original fixed guards, R capture, value/transport guard order, per-row reads, success 0 and handler 255 remain. D5/APPENDIX-BINDINGS.md:764-765; D4/APPENDIX-BINDINGS.md:522-528; S5/core/evaluation_pending_c.adb:105-173. |

**Required change V5-RC4-GATE-EXCEPTION.** In BR7, assignment permission is selected by kind == 'wfx' and CAPI_GATE_EXCLUSIVE.get(row_id). The row helper receives no scope identity, and the outer loop validates neither the sole wfx tuple nor the exclusive-map key roster. Thus the algorithm's rule is “any correctly shaped listed wfx row”, while B0.7's rule is “G21c/Finalization_Decide/O only”. The fixed table contains only the intended exception; this finding concerns the explicitly promised independent invariant when matching tiles/tables are amended, not a claim that changed source passes the whole checker. Evidence: D5/APPENDIX-BINDINGS.md:145-158,463-540,581-583.

Hard-bind that sole identity independently of amended rows, including the empty pre-PK-6b and sole-G21c post-PK-6b exclusive maps and the normative declaration/region/assignments. Add an amendment control for an extra, relabelled or moved wfx exception and unchanged-stage positive controls. MX1–MX8 cover misuse of existing O, but omit expanding the exception roster (D5/APPENDIX-BINDINGS.md:244-246,865). Preserve A1, all existing payload lists, diagnostics, codes, writes and accepted cases.

## 2. V4-RC4-ALIAS: NOT_CLOSED

R-QUAL(a) is deterministic text comparison: an exact case-insensitive per-scope multiset, with each entry independently canonical or a scoped exception. My passive extraction agrees with the twin for the named tiled scopes, including the diagnostic body and the separately attributed pending exports. The early residual selectors and GE3–GE6 account for the stated residual transition. No exception applies outside its listed scope. Evidence: D5/APPENDIX-BINDINGS.md:183-201,362-401,616-660; D4/APPENDIX-BINDINGS.md:742-750; S5/core/worldline-c_api.adb:374,571-572,656-660,885-905,1015,1112.

Every exception denotes what is claimed:

| Exception | Observed denotation and scope |
|---|---|
| Evaluation.Classify | Worldline.Evaluation.Classify in the residual; distinct from the Appendix C Completion_Roster Classify. S5/core/worldline-evaluation.ads:113; S5/core/worldline-c_api.adb:374; D5/APPENDIX-BINDINGS.md:616. |
| Hash_Probe.Present / Counter_Probe.Present | Fields of the local optional-record probes used for Position, not calls to a listed Present routine. S5/core/worldline-c_api.adb:571-572,656-660; D5/APPENDIX-BINDINGS.md:617-618. |
| V1.Present / V2.Present | Local Owner_Layout record components used for Position. S5/core/worldline-c_api.adb:885-905; D5/APPENDIX-BINDINGS.md:619-620. |
| Owner_Wire.Decide / Retry_Wire.Decide | Residual aliases of the existing owner-transition/retry wire routines, not an Appendix C or removed routine. S5/core/worldline-c_api.adb:879,1015,1024,1112; S5/core/worldline-owner_transitions_wire.ads:138; S5/core/worldline-owner_retry_audit_wire.ads:56; D5/APPENDIX-BINDINGS.md:621-622. |
| Completion_Transport.Context_Matches / Metadata_Base | The tiled moved transport helpers, limited to RESIDUAL, Finalization_Decide_Mixed and Finalization_Transport.Final_Context_Matches from PK-6b. Their canonical-looking removed Evaluation_Completion_C counterparts are not excepted. D4/APPENDIX-BINDINGS.md:623-656,704-719,744-747; D5/APPENDIX-BINDINGS.md:623-624. |

The visible-package-renaming graph extracted from S5's specifications yields exactly the documented path sets. In particular, F.P follows Evaluation_Finalization.P through its T alias to Evaluation_Completion.P; K.A.Roster and Authority.T.R.P follow the authority aliases; V2.P follows the pending-v2 alias. The core-specification hash-list identity agrees with the pinned e6276e7919d0bf39f41c696ec25e5c74c676d9c1e8ec3400763a2a7685a4a217. This is a textual inventory, not installed name-resolution evidence. Source evidence: S5/core/evaluation_finalization.ads:12-17; evaluation_completion.ads:10-12; evaluation_completion_roster.ads:3-4; evaluation_raw_roster.ads:8-11; worldline-evaluation_authority.ads:42,119; evaluation_completion_c.ads:159; evaluation_pending_v2.ads:3. The inventory itself is D5/APPENDIX-BINDINGS.md:664-686.

None of those indirect spellings is canonical or excepted. The same (a) validation refuses transport-qualified, C_API-qualified, library-renaming, parent-shortened and Standard-prefixed paths, even when the matching multiset is amended. Rule (b) refuses a listed selector after a non-name prefix; (c) refuses an attribute of a full routine name. Direct in-pair root declarations are refused by (d). V7's uniqueness/unoverloaded/full-name requirement and the exact scoped clause tuples remain unchanged. Evidence: D5/APPENDIX-BINDINGS.md:198-229,345-401; D3/DESIGN.md:246; D5/DESIGN.md:36-40.

Use-visibility does not reopen the documented paths. A-R2 permits only the carried unit transports and System.Storage_Elements; use all type stays prohibited; the exact use type tuples stay pinned. R-INV(v)'s renames count excludes subprogram renaming declarations, including renaming-as-body. R-TRANS/R-TILE and residual identity exclude unlisted generic instances, added callable wrappers, overloads and homographs; copied Address_To_Access_Conversions instances remain bound verbatim. V7 remains a separate declaration/body-review obligation. The textual spelling check alone is not an overload/type resolver. Evidence: D4/APPENDIX-BINDINGS.md:45-77,1518-1541; D5/APPENDIX-BINDINGS.md:70-73,219-229; D3/DESIGN.md:246.

The narrow readings of use-visibility and use type are supported by the primary [Ada 2022 RM 8.4](https://www.adaic.org/resources/add_content/standards/22rm/html/RM-8-4.html), particularly paragraphs 8/3–9. That documentary support does not settle application to the assembled body. Installed integrated resolution, overloading/homographs, child-unit interactions, and the RM readings as used by this candidate remain **OPEN**, as D5/DESIGN.md:281,304-306 and D5/AUTHOR-NOTES.md:16-28 require.

**Required change V5-RC4-QUAL-CAPTURE.** R-QUAL(d)'s context rule and BR6 check only a named dotted unit's *last* identifier (D5/APPENDIX-BINDINGS.md:202-205,384-389). Ada visibility includes library units denoted by a with-clause name's prefixes, as well as the terminal named unit. Children occur within their parent's declarative region, and an inner homograph can hide an outer declaration. This follows from [RM 10.1.2, paragraphs 6/2 and 7](https://www.adaic.org/resources/add_content/standards/22rm/html/RM-10-1-2.html), [RM 10.1.1, paragraph 11](https://www.adaic.org/resources/add_content/standards/22rm/html/RM-10-1-1.html) and [RM 8.3, paragraph 8](https://www.adaic.org/resources/add_content/standards/22rm/html/RM-8-3.html).

Consequently, mentioning a capturing Worldline sibling child only as a prefix of a named descendant is not covered by the terminal-identifier test. The same full routine spelling can then start from the capturing unit. This is a specification omission in the promised independent no-capture invariant; I do not assert that such a child exists in frozen S5, that a mutation passes all fixed residual checks, or that installed compilation was performed. The current Worldline parent is read and has no such declaration (S5/core/worldline.ads:1-9). D5/AUTHOR-NOTES.md:56 specifically calls out capture starting outside the pair.

Extend the text-only context restriction to every potentially capturing library-unit prefix mentioned by a with clause, keeping current qualified names, exceptions and use inventory unchanged. Carry the repair through the argument, promises and twin; specify a matching amendment control and unchanged-context positive control. MQ14 only tests direct terminal child capture. MQ1–MQ13, MV1–MV4, MA1 and the L9 positive control are useful specifications for their stated families, but do not cover this prefix omission (D5/APPENDIX-BINDINGS.md:847-862). All controls remain unrun.

## 3. V3-RC4, R2_NINE_CONDITIONS and PACKET_PLAN: NOT_CLOSED

The v5 §17 mapping preserves the relocation map, whole-closure binding and profile checks, predecessor preservation, complete identity layers, append-only proof enrollment, exact exception set and full strict-evidence obligation. Condition (4)'s independent gate and qualified-name invariants remain incomplete for the findings above. Therefore neither R2_NINE_CONDITIONS nor overall V3-RC4 is closed. Evidence: D5/DESIGN.md:273-296; D5/APPENDIX-BINDINGS.md:800-841; D3/DESIGN.md:1746-1778,1814-1841.

PACKET_PLAN retains linear single-packet composition, exact predecessor bases and pins, re-review after a rebase, immediate PK-6a enrollment, separately reviewed confirming representation packets, and an identities-only PK-S. These are preserved directions; the required invariant repair prevents closing the packet plan at design level. V-R9 correctly replaces the effective v4 R12 line, not the raw superseded v3 line. Evidence: D3/DESIGN.md:1870-1939,1970-1993; D4/DESIGN.md:244-248; D5/DESIGN.md:219-228,296.

V3-RC5 and V3-RC6 remain CLOSED_AT_DESIGN_LEVEL, with implementation/native/control evidence OPEN. The corrected R0/R1/R2/R3/S/H/X characterization keeps completed writes and exact frontiers distinct from native failure location/copy atomicity. C-14 stays proposed behavior outside baseline. The carried cost map distinguishes source constructions/evaluations from native calls, copies, elision, storage, lifetime and accepted-domain failure. Evidence: D4/DESIGN.md:534-629,639-704; D4/APPENDIX-COST-MAP.md:7-72,93-112,435-482.

## 4. Carried items: identities and dispositions preserved

Every requested DESIGN and A-BIND slice hash verifies against v4. Every old quote in V-R1–V-R9 and A-R1/A-R2 equals its stated source, including V-R9's effective v4 replacement of v3:1931. BR1–BR8's old blocks/insertion anchors and old/new digests verify, and reconstruct the stated B8 identity. The unmentioned B8 text is retained byte-for-byte. The nested v3 slice hashes and canonical-JSON hashes of the carried twin values also verify. Checks.json retains per-slice/per-replacement observations. Evidence: D5/DESIGN.md:99-130,143-231; D5/APPENDIX-BINDINGS.md:16-81,273-556; D5/decisions.json:253-263; D4/DESIGN.md:111-172.

The replacements are correctly targeted and justified in purpose: rule-table/naming revisions, staged removed-name exclusion, branch restrictions/completeness, path-independent use exclusion, promise/control updates and the intermediate-stage rule. Their unresolved effectiveness is identified in items 1 and 2. No undeclared change to the carried B4 tiles, B5 predecessor edits, B6 diagnostic sequences, B10.2 write rows or cost map was found.

Independent normalized-text comparisons confirm the Diagnostic_Transport spec/body, Native_Diagnostic_Control and RC2 exclusive region equal their carried v3 texts. The required-name suffix, relocation map and append schedule are preserved; the v4 twin adds only carried_from_v3 metadata to the v3 required_proved_append object. The fixed S5 roster/pin identities were independently observed by AST literal inspection. Evidence: D3/DESIGN.md:509-577,729-749,1918-1939,2478-2589; D4/APPENDIX-BINDINGS.md:662-695,768-772; S5/runtime/worldline/proof_manifest.py:22,25,312-316,924,940,953,967,972,1003,1012.

| Carried ruling | Preserved disposition and practical limit |
|---|---|
| RC1–RC3, LD4-R | CLOSED_AT_DESIGN_LEVEL for their prior design questions. Diagnostic state/decisions/composition stay in SPARK; RC2 preserves allocation and no Captured read/pass on 0/1; N-01 discipline remains strict. Installed legality and implementation proof remain OPEN. D5/DESIGN.md:61-68; D3/DESIGN.md:356-400,599-642,729-749,2012-2052. |
| LD1, LD2 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL; full body/caller correspondence and custody remain required; no new transport-facing Pre or functional Post. D3/DESIGN.md:113-138,222-253. |
| LD3 | CONDITIONALLY_ACCEPTABLE_PENDING_D-13; original component ABI/control scope and SPARK_Mode-only mirror preserved; no canonical proof credit. D3/DESIGN.md:140-149,2252-2260. |
| LD4 | WITHDRAWN; no wholesale diagnostic-state relocation. D3/DESIGN.md:151-168. |
| LD5, LD6 | CONDITIONALLY_ACCEPTABLE; original wire contracts and costed rechecks stay; controls additive, with RC5's design condition discharged. D3/DESIGN.md:170-191; D4/DESIGN.md:620-629. |
| L1–L8 | GENUINE and prior design repairs preserved. L3's actual installed warning remains UNVERIFIED. L5's separate gate obligation is still not closed by this review. No prior local repair is withdrawn. D5/DESIGN.md:73; D4/review/gpt61-v1/REVIEW.md:105-114; D4/APPENDIX-BINDINGS.md:60-77,742-756,1043-1060,1144-1148,1560-1564. |
| APPENDIX_C | CLOSED_AT_DESIGN_LEVEL for exact append-only ordering/enrollment; original prefix and immediate PK-6a enrollment retained. Name enrollment does not replace unit-wide body/caller proof. D3/DESIGN.md:1918-1939,2478-2589; D5/DESIGN.md:74. |
| D-05, D-19 | OPEN. Contextual proof at every partial-decoder caller or a separately reviewed non-narrowing total restructuring; no helper Pre approved; no original branch deleted. D3/DESIGN.md:247-252,880-893; D5/DESIGN.md:279,284. |
| D-18 | CLOSED_AT_DESIGN_LEVEL for the non-narrowing index design; proof OPEN; unequal journal/history lengths retain their original typed outcome. D3/DESIGN.md:848-878. |
| D-28 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL; complete fixed local initialization; native costs OPEN. D3/DESIGN.md:895-902. |
| D-36; D-15/D-34/D-38 | OPEN for every write construction, native symbols, layouts and installed legality/name resolution. D5/DESIGN.md:281,287; D4/APPENDIX-COST-MAP.md:435-482. |
| N-03, N-05 | OPEN: complete strict matching-source callee/body scope with no PROVED_ROW transfer; original exact-set audit assertion preserved without subset reinterpretation. D5/DESIGN.md:290-292. |
| N-04, N-07 | CLOSED_AT_DESIGN_LEVEL for explicit Classify/pending Decide enrollments; complete proof/body/native obligations remain. D5/DESIGN.md:291,294; D3/DESIGN.md:2556,2578-2587. |
| D-13, N-06, N-01 | Ownership and qualifications preserved as item 6 explains. D5/DESIGN.md:75-77,280,288,293. |
| R2_NINE_CONDITIONS, PACKET_PLAN | NOT_CLOSED for the remaining RC4 invariants; no preparation/execution/acceptance transfer. D5/DESIGN.md:295-296. |

## 5. L9–L12: genuine; local repairs correct

| Defect | Independent assessment |
|---|---|
| L9 | GENUINE; REPAIRED_AT_DESIGN_LEVEL for the fixed staged inventory. V4 installs removed-routine K pairs at PK-1, while S5 still contains the original Raw_Decide/Context_Matches/Metadata_Base/Metadata_Matches calls until PK-6b. V5 defers only those removed-name pairs to the packet that applies GE1–GE8. The designed early tiles contain none of those selections, their clause inventories stay fixed, and R-RES permits no new residual call. The original requirements do not require removing the old residual before its mover packet. At PK-6b the full previous alias roster is restored. Thus this repair stops a false refusal of unchanged early residual text; it does not relax the designed inventory or a native accepted case. D4/APPENDIX-BINDINGS.md:177-185,1698-1717; D5/APPENDIX-BINDINGS.md:95-110,239-250,707-711; S5/core/worldline-c_api.adb:758-817,832-876. |
| L10 | GENUINE; REPAIRED_AT_DESIGN_LEVEL for the listed Boolean/case gates. V4's after-test check does not confine a False component to rejection or a case component to its own alternative. V5's places and whole-use check repair those omissions and retain the original rejection diagnostics. The separate sole-wfx validation gap remains required. D5/APPENDIX-BINDINGS.md:407-439,475-507,758-760; D5/DESIGN.md:47. |
| L11 | GENUINE; REPAIRED_AT_DESIGN_LEVEL. With the carried transport roster, the new whole-clause whitelist is strictly stronger than the earlier unit/single-alias comparison: every admitted whitelist entry was allowed before, while indirect paths and unrelated package use clauses are now excluded independently of exact clause-table equality. Existing B9.1/B9.2 clauses remain admitted; use type stays scoped and use all type stays forbidden. D5/APPENDIX-BINDINGS.md:70-73,324-342,860; D4/APPENDIX-BINDINGS.md:1466-1565. |
| L12 | GENUINE; REPAIRED_AT_DESIGN_LEVEL for the fixed acceptance-type inventory. Completeness now scans any Ok/Verdict selection, not just case Verdict, and declarations with the recorded _Acceptance naming convention. MG11/MG12 cover the stated omission families. This is not arbitrary Ada type inference; a new differently named type requires reviewed expansion, and installed legality remains OPEN. D5/APPENDIX-BINDINGS.md:533-540,864; D5/AUTHOR-NOTES.md:22-28. |

MA1 requires refusal when GE1 is omitted at PK-6b; the unchanged-S5 PK-1 positive control is necessary to prevent recreating L9's false refusal. The mutation specifications are retained as obligations, with the additions required above. The author's reported outcomes were not used as evidence.

## 6. Operator and lead ownership

**D-13:** OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE. The reserved choice concerns a concrete material component transport/library architecture. The lead prepares source/project/link and identity/control artifacts. Both original Decide exports, profiles/layouts, every original interface unit, SPARK_Mode-only mirror correspondence and original native positive/refusal/body obligations remain required. Dropping exports or abandoning the mirror remains inadmissible. The reservation does not extend to implementation-file pinning or recomputing effective pins. Evidence: D3/DESIGN.md:2252-2260; D5/DESIGN.md:75,280; D5/decisions.json:237; W/work/integrated-proof-preparation/PLAN.md:104-107; H/HANDOFF.md:153.

**N-06:** REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT. The protected service checks native_sha256 before loading the library. Reprovisioning must bind the installed/loaded reviewed library to matching source/proof/control identity, protected configuration and operator custody. Keeping the old library is a deployment hold, not acceptance of the consolidated candidate. Evidence: S5/protected-resource/run_service.py:117-120; D3/DESIGN.md:2262-2271; D5/decisions.json:238; H/HANDOFF.md:164-166.

**N-01:** LEAD_OWNED_STRICT_OBLIGATION. Confirming representation repairs retain every C1–C8 constraint and E1–E6 evidence requirement, including unchanged layouts/sentinels/scenarios, strict warnings/proof, matching baseline evidence, independent ABI review and actual GPT-6.1 different-author review. Moving code to Off is not resolution; failed confirming repairs leave the warning OPEN. A nonconfirming material ABI change is outside this design and operator-owned, without authority to lower the target. Evidence: D3/DESIGN.md:2012-2052,2273; H/HANDOFF.md:158-161; P:32-34.

I found no newly mislabelled routine engineering decision or approval gate merely because a file is pinned. The current user's supervision rule controls material API/ABI/owner-policy, reference/contract, custody, toolchain/runtime/deployment and operational reservations. A brief, prior reviewer ruling or this verdict creates no new authority. Original applicable operational gates remain, and none is exercised here. Evidence: H/HANDOFF.md:153-166; P:72-74; D5/DESIGN.md:325.

## 7. Further weakening, integration and open obligations

Beyond the incomplete independent invariants identified above, I found no v5 delta that narrows domains or accepted cases, lowers contracts/floors, removes deterministic controls, skips bodies/callers, waives warnings, adds an assumption, suppresses checked assertions or grants a new Off exemption. That conclusion is about the reviewed design delta, not proof of a successor.

The original floor, sole boundary, ordered proof prefix and effective pin map are independently observed in S5. The manifest identity is 51dd30d1a2c19cea4b9794e869400c5cb7c4193043f66678e62efa695b058fcb; ordered required-name JSON digest bf1ec89a4421ad152213721a6bd49f558a4d8847ea1c3fbe84a864519368890b; effective pin-map canonical JSON digest 42f1809c2ec5a6ed4dbcb639a91c62f50ab80c75787d7110a0a69618bb9ec8c4. These identities do not substitute for proof, authentic producers or loaded-library correspondence. Evidence: S5/runtime/worldline/proof_manifest.py:22,316,622-637,855-884; D5/DESIGN.md:89-97; H/HANDOFF.md:25-29,161-167.

The root-worker design hash matches db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5. Its §14 H1–H8, R-RW-1–10, O1 and IC-1–10 address the shared layout, residual, symbols, identifiers, Off units, enrolled names and Optional_Marker collision. D5 §19 also requires refusal of unlisted residual changes and new indirect spellings, followed by re-observed and reviewed tables on any rebase. Installed integrated name resolution remains OPEN. This review neither selects the integration order nor endorses/resolves the other lane; v4-labelled integration rules need reconciliation with v5's R-QUAL and repaired gate invariant in the eventual reviewed composition. Evidence: RW/SEAM-DESIGN.md:1750-1830; D5/DESIGN.md:332-339.

Remaining obligations include:

- Both required design repairs and subsequent different-author review; real manifest/tables and deterministic mutation controls, all still unwritten/unrun as controls.
- Installed-tool legality, transported-clause warnings, acceptance-record/branch correspondence and integrated name/overload resolution (D-38), including the diagnostic External state and Image modeling.
- Complete strict matching-source flow, RTE, termination, functional/reference/body/caller scope, zero unproved, zero justified, zero pragma Assume and the unchanged formal command/floor. Name enrollment and Global null alone establish none of that.
- N-01 strict representation obligations, D-05 decoder/caller obligations, D-18 proof, D-19 branch obligations, N-03 full callee scope and N-05's exact-set control.
- D-15 symbols/mappings, D-34 ABI/layouts, D-36 every write form; every A-COST native item and C21-a through C21-h; full-domain Big_Integer/runtime/representability/allocation/controlled-copy/Ghost/stack/cost correspondence. No cap, light proof-only library, native-failure accepted refusal or assertion/Ghost suppression.
- PK-0's actual original characterization, complete original ordinary/lifetime/positive/refusal roster and every additive/provider/fault campaign on the exact integrated source/library, retaining all failure evidence.
- OB-048 and the enlarged/pre-existing boundary; actual custody, producer authenticity, current immutability premises and faithful callers at the real state change. No renamed Boolean substitutes for them.
- Root-worker and protected-lineage composition/rebase, every packet/stage/final review, D-13 material architecture choice, N-06 deployment custody and all original applicable operator and acceptance dependencies.

Evidence: D5/DESIGN.md:300-328; D3/DESIGN.md:2192-2244; D4/APPENDIX-COST-MAP.md:453-482; H/HANDOFF.md:25-29,129-131,151-167; P:32-34,60-66.

The v5 author-process note and v4 TaskStop note were read and hashed as disclosed model-origin records. Their stated command effects and lead classifications were not re-derived or treated as permission for this reviewer. The reported in-memory sketch outcomes supply no control or acceptance credit. Evidence: D5/AUTHOR-NOTES.md:58-75; WT/deviations/capi-v5-author-process/NOTE.md:7-24,32-56; WT/deviations/capi-v4-author-taskstop/NOTE.md:3-29.

## Required changes and final rulings

| Id | Required design change |
|---|---|
| V5-RC4-GATE-EXCEPTION | Independently enforce the sole staged G21c/Finalization_Decide/O wfx exception and normative exclusive protocol, plus amendment and unchanged-stage controls. |
| V5-RC4-QUAL-CAPTURE | Cover every potentially capturing with-clause prefix/ancestor, align all normative/check/promise/twin text, and add amendment/unchanged-context controls without relaxing names, exceptions or scope. |

V4-RC4-GATE = NOT_CLOSED; V4-RC4-ALIAS = NOT_CLOSED; V3-RC4 = NOT_CLOSED. R2_NINE_CONDITIONS and PACKET_PLAN remain NOT_CLOSED. Prior design-level/conditional/OPEN rulings are preserved as specified above. L9–L12 are GENUINE with the stated local design repairs; they do not close the new invariant gaps. No source, proof, native, deployment or Phase One acceptance is granted.

## Reviewer JACKAL arithmetic and consequence ceiling

Each derived arithmetic result was obtained through the real JACKAL MCP front door, sequentially in modest groups. Full inputs and returned structured results, including identities and non_claims, are retained in checks.json. Selected non-trivial parsed inputs:

| Purpose | Returned status | parsed= | exact= |
|---|---|---|---|
| Carried DESIGN plus A-BIND slices | exact | 20+13 | 33 |
| Indirect-path inventory total | exact | 34+17+1+3+7+7+11 | 80 |
| Multiple-identifier paths | exact | 80-9 | 71 |
| Post-PK-6b listed selectors | exact | 85+9-1 | 93 |
| Staged alias pairs | exact | 41+9 | 50 |
| Unchanged early residual removed-routine call sites | exact | 2+2+2+2 | 8 |
| Gate-kind roster | exact | 31+1+1 | 33 |
| S5 required roster | exact | 280+11+4+5+8+31+34+46+1+115 | 535 |
| S5 effective pin keys | exact | 82+8+8+6+4+6+10+0+0+4+0+38+0+1+0+2+0 | 169 |
| Append schedule | exact | 6+2+14+6+3+57+10 | 98 |
| First appended index | exact | 535+1 | 536 |
| Final roster size | exact | 535+98 | 633 |

For every result, JACKAL returned assurance **exact rational arithmetic (not yet checker-covered)**, formal=false, lane=rat, and these non_claims verbatim:

- NOT formal-bounded: this lane carries no Lean-checked certificate
- The epistemic class above is the STRONGEST claim this result supports
- exact rational arithmetic (not yet checker-covered)

The consequence ceiling here is informational about code correctness. Arithmetic over the observed text does not establish name resolution, branch typing, source correspondence, proof coverage, custody or native accepted-domain behavior. The ledger was not cited as evidence.
