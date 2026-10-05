# Independent design review: WORLDLINE C-API boundary consolidation v4

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.** V3-RC4 is **NOT_CLOSED**. V3-RC5 and V3-RC6 are **CLOSED_AT_DESIGN_LEVEL**. The required repairs are V4-RC4-GATE and V4-RC4-ALIAS. No source, proof, execution, deployment or Phase One acceptance is granted.

Reviewer: actual model selection **gpt-6.1-sol**, different from the author, with no authorship of the design under review. Author: Claude Code lead **claude-opus-5-5**, through a drafting subagent. This review authored only its own artifacts.

## Evidence identities and method

Path aliases used in all file:line citations:

| Alias | Absolute location |
|---|---|
| W | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow |
| WT | W/work/claude-lead-isolation-v1/wt-1 |
| D4 | WT/designs/claude-capi-boundary-design-v4 |
| D3 | WT/designs/claude-capi-boundary-design-v3 |
| S5 | W/work/claude-composition-v5-beta/source |
| S4 | W/work/reviewed-common-proof-source-composition-v4/source |
| H | W/outputs/claude-phase1-handoff-20261004 |
| P | /home/sicarii/Documents/complete-phase1-prompt.txt |
| RW | W/work/protected-original-root-worker-repair-v1 |

All requested design hashes were independently recomputed and match:

| D4 file | SHA-256 |
|---|---|
| DESIGN.md | a9b5dcce5ca5808f8049ae8e7020a79c3fbfc33cc4dcbcc3706fd8f4f40fbfd6 |
| decisions.json | 59e71dd68724b0420b670d79a99ea74194134dbc6d219b7b91f146ad01843625 |
| APPENDIX-BINDINGS.md | 39ca995998d68b57d13c02796ee30d8826eecc07e750abf95a83f7d348f7d626 |
| APPENDIX-COST-MAP.md | 5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4 |
| jackal.json | dec64a324685496195a7cb1c48e9ee3cf168255f8a1214d62b9491e42653f39d |
| AUTHOR-NOTES.md | ccac4f63a00ed36199642b8691535890719879187b135ecce69f67edc5214b07 |

The sealed v3 review's report, checks and review metadata match its freeze hashes, byte sizes and modes; its report/check bindings also agree. Every hash row in D4 DESIGN §B.2 was recomputed against exact v3 slice bytes. Every R1–R15 quoted old line equals the cited v3 line. The extra hashed §8.8 row is marked REPLACED and is not carried text. These distinctions resolve the prompt/author-note difference about carried versus hashed slices without changing the bound design. Evidence: `D4/DESIGN.md:111-176`, `D4/AUTHOR-NOTES.md:73`; per-row observations are in checks.json.

Work was passive reading, hashing, JSON/string comparisons and text/AST inspection. No WORLDLINE module or proposed check sketch was imported or executed. No compiler, prover, build, test, service, reservation/window, vault/restic, process interruption or SIA note action was performed. Files were created only in this review directory with O_EXCL, mode 0600 and fsync. Checkpoints remain create-only.

JACKAL was initially not exposed to this session's tool discovery. A later discovery exposed its real MCP exact tool; relevant arithmetic was then independently replayed sequentially. The earlier checkpoint availability statements are historical, not the final verification state. Final results, parsed inputs, assurance and non_claims are retained in checks.json. The convenience ledger was not read or used as evidence.

The installed Ada/SPARK skills and relevant packages, interfacing, exceptions, parameter-passing and proof-workflow references were applied. SPARK Guide 28.0w guidance is distinct from the pinned installed 16.1.0 toolchain. No installed legality or generated-code claim follows from reading those references.

## 1. V3-RC4, V3-RC5 and V3-RC6 closure

### V3-RC4: NOT_CLOSED

| Sub-requirement | Finding |
|---|---|
| Exact scoped rename/use inventory | Supplied: residual clauses, T/L/A transport/export/helper tuples, exclusions and GE9. The former impossible single non-use-type clause rule is explicitly replaced. Installed scope resolution and warning behavior remain OPEN. Evidence: `D4/APPENDIX-BINDINGS.md:60-77,1466-1571`. |
| Deterministic O6(b)/(c) | Supplied by exact per-scope tuple/residual equality, renaming-kind restrictions, context/spec hygiene and clause checks. The separate stronger fully expanded naming claim has the indirect-path gap below. Evidence: `D4/APPENDIX-BINDINGS.md:60-85,1249-1263`. |
| K3 actual Library_Interface membership | CLOSED_AT_DESIGN_LEVEL: parse a single literal attribute list, require exact ordered membership and refuse Interfaces alternatives. This addresses the old quoted-anywhere false pass; the original project uses the same string as Library_Name and an interface member. Evidence: `D4/APPENDIX-BINDINGS.md:232-265,1043-1060`; `S5/pending-component/pending.gpr:5-13`; `D3/APPENDIX-BINDINGS.md:1018-1020`. |
| Provenance and gating for every write form | Explicit forms and rows now cover direct function stores, procedure-out buffers/mask, completion Response, protocol state, helper writes and exclusive finalization assignments. Provenance is specified per form; gating is internally contradictory in B0.7. Evidence: `D4/APPENDIX-BINDINGS.md:87-114,1729-1815`. |
| O4/R-W/B4/B8 alignment | NOT_CLOSED because the normative gate rule differs from B4/B10 and the B8 algorithm. The qualification invariant also overclaims the alias pattern. Exact current tiles do not excuse either specification defect. Evidence: `D4/DESIGN.md:450,479-484`; `D4/APPENDIX-BINDINGS.md:104-114,1259-1263,1313-1327,1455`. |

**V4-RC4-GATE — required.** B0.7 says every other selection begins after the *end of the gate* and an acceptance object is never assigned. G16a's exact gate includes `FA.Rejected_Position` inside the False branch after `if not FA.Ok`; the original rejection diagnostic must remain. Finalization's `O` is assigned on the two exclusive paths before its test. B8 instead checks selection after the discriminant *test* and makes the assigned-O exception. These are incompatible normative rules, not an installed-tool uncertainty. Evidence: `D4/APPENDIX-BINDINGS.md:104-114,681-688,1313-1327,1779,1803-1815`; `D4/DESIGN.md:450,479-484`; the rejection variant is `D3/DESIGN.md:775-794`.

Repair the rule, rows, checker specification, promises, mutation specification and machine twin together. Preserve A1's branch-correct discriminant domination, the False-variant diagnostic payload and the exact exclusive WF-X assignments. Do not delete diagnostics, ban a valid rejection payload, allow arbitrary assignments or weaken the accepted domain merely to obtain consistency.

**V4-RC4-ALIAS — required.** The allowed finalization renamings include `F` and `P renames F.P`. The source establishes `Evaluation_Finalization.P -> Evaluation_Completion.P -> Evaluation_Pending`. Thus `F.P.Decide` is an indirect spelling of an enrolled routine, while B9.4 lists simple `P.Decide`, `E.Decide`, etc. The negative preceding-dot condition prevents matching the `P.Decide` suffix within that indirect path. The claimed conclusion that only full expanded names remain therefore does not follow. Evidence: `D4/APPENDIX-BINDINGS.md:79-85,1259-1263,1541,1702-1717,1841`; `S5/core/evaluation_finalization.ads:12-13`; `S5/core/evaluation_completion.ads:10`.

Current exact tiles and residual hashes still bind their specified text. This finding does **not** claim an unreviewed changed successor passes the whole checker, and no mutation was executed. It concerns the explicitly promised independent invariant for later reviewed tile amendments (`D4/APPENDIX-BINDINGS.md:34-43,1455`). Complete indirect-path handling, including transport-qualified paths, or specify exact expanded qualifiers for every relevant call with the same guarantee. Add indirect-path mutation requirements to `D4/APPENDIX-BINDINGS.md:1884`; do not relax V7/O6(a).

### V3-RC5: CLOSED_AT_DESIGN_LEVEL

The new R0/R1/R2/R3/S/H/X classification supplies the missing distinction between pre-capture guards, post-capture guards and per-element refusal frontiers. In particular, pending reads R before its header/transport/value guards; history reads Query and the whole Data arena before validating the query; ledger headroom captures A/W/F before Shape; finalization captures X before transport-field checks. The raw completion frontier also retains the check-row refusal before reading the corresponding Wire/Confined pair. Evidence: `D4/DESIGN.md:540-577`; `S5/core/evaluation_pending_c.adb:111-152`; `S5/core/worldline-evaluation_history_c_api.adb:144-155`; `S5/core/worldline-resource_ledger_c_api.adb:195-209`; `S5/core/evaluation_completion_c.adb:599-612`.

Handled internal exceptions are defined mappings with the original codes and exception diagnostics where present. Earlier completed writes persist in canonical source order; no rollback is invented. The ledger's order is Detail_Data, Total_Data, Details, Result. Only failure location, completed-write extent, in-progress copy atomicity and native construction effects remain OPEN/implementation-dependent. A native failure is never counted as an accepted semantic refusal. Evidence: `D4/DESIGN.md:547-550,564,586-606`; `S5/core/worldline-resource_ledger_c_api.adb:164-176`.

Foreign faults and violated documented premises remain separate class X. C-01 is confined to the stated defined no-write refusals; C-05 places guard pages beyond the actual read frontier. C-14 is a stronger proposal outside baseline and PK-0 pass conditions, with policy/ledger removed from its local-completion scope. These are corrections of erroneous classification, not dropped original successful controls. Evidence: `D4/DESIGN.md:250-265,608-629`; `D4/APPENDIX-COST-MAP.md:451`. Runtime/native correspondence remains OPEN.

### V3-RC6: CLOSED_AT_DESIGN_LEVEL

The cost map now distinguishes source calls/evaluations/constructions/check semantics from emitted calls/checks, copies, storage, elision, allocation and lifetimes. E/U/R and Rd/Ri are qualified; the categorical mandatory secondary-stack copy, real-call, emitted-check and no-elision claims are withdrawn. ALLOC = names only retained original allocation statements, with new objects/results and their native storage separately OPEN. Evidence: `D4/APPENDIX-COST-MAP.md:7-72,93-112`; `D4/DESIGN.md:641-700`.

Both the Begin_* fit evaluation and guarded composer's fit re-evaluation are included. A nested Mark contributes its own pair only when its own active read is True. Reviewer MCP results: status=exact, parsed=1+1, exact=2 for a fit pair; status=exact, parsed=2+2, exact=4 for the stated path with active nested Mark; status=exact, parsed=2-1, exact=1 for the additional Image source evaluation. Evidence: `D3/DESIGN.md:429-472,519-552`; `D4/APPENDIX-COST-MAP.md:412-425`.

Run-ledger Data, Before, Proposed and Observed are array actuals; Raw is a record actual. Reviewer results: status=exact, parsed=1+2+1, exact=4 array actuals; status=exact, parsed=4+1, exact=5 total actuals. Evidence: `D4/APPENDIX-COST-MAP.md:279`; `S5/core/resource_run_ledger_c_api.adb:213-219`.

The per-form construction account replaces the blanket completed-local claim. D-36, every N-mark, C21-a through C21-h and every original full-domain native blocker remain OPEN. Arithmetic establishes none of them. Evidence: `D4/APPENDIX-COST-MAP.md:435-482`. The JACKAL assurance/non_claims below apply to each arithmetic result.

## 2. Source spot checks: tiles, frontiers, write rows and cost labels

The following comparisons examine guards, read staging, allocation positions, refusal codes, exception scope, writes and source/native cost separation. Reviewer MCP arithmetic for the named checks is status=exact, parsed=1+1+1+1+1+1+1+1, exact=8. Full-domain preservation is an engineering obligation, not established by this finite review.

| Export | Source correspondence and remaining obligations | Evidence |
|---|---|---|
| wl_resource_ledger_compute | Initial guard then Data allocation/copy, staged rows and first failing row refusal remain in order. Compute produces mutable out buffers. Writes remain unconditional Detail_Data, Total_Data, ascending Details, Result; typed refusals still write and return 0. Handler remains 255. WF-O/B/F distinguishes producers, buffer writes and direct encoders. Original allocation bounds retained; per-row acceptance/results/native passing and construction OPEN. | `S5/core/worldline-resource_ledger_c_api.adb:115-176`; `D4/APPENDIX-BINDINGS.md:454-461,1755-1758`; `D4/DESIGN.md:564`; `D4/APPENDIX-COST-MAP.md:238-247`. |
| wl_resource_ledger_headroom | A/W/F captures precede Shape; Data remains unread on Shape refusal. Output arena then Result writes and 255 handler retained. Earlier pure decoding in acceptance is conditional on M4/D-05 infallibility evidence. Array/result passing/storage and direct-result construction OPEN. | `S5/core/worldline-resource_ledger_c_api.adb:184-223`; `D4/APPENDIX-BINDINGS.md:466-470,1759-1760`; `D4/DESIGN.md:565`; `D4/APPENDIX-COST-MAP.md:243-247`. |
| wl_pending_decide_v1 | Fixed extents/disjointness precede R capture; header, arena/row transport guards and field predicates retain order. Data then per-row reads; completed O.Value written once, return 0; refusal/handler 255 retained. Totality rechecks the accepted captured constant, without a new array equality/length guard. Body/caller implication proof and native accepted-domain construction OPEN. | `S5/core/evaluation_pending_c.adb:105-173`; `D4/APPENDIX-BINDINGS.md:522-528,1767`; `D4/DESIGN.md:568`; `D3/DESIGN.md:1696-1718`; `D4/APPENDIX-COST-MAP.md:299-306`. |
| wl_finalization_decide_v1 | Entry diagnostic, fixed extents, X, transport/value gates, Data/Required/Captured allocation and plan loop remain staged. Operations 0/1 neither read rows nor pass Captured; 2/3 stage rows. O is assigned exclusively; Reason outcomes and reason/promotion diagnostics precede the sole output write. Original handler diagnostic and 255 retained. The RC2 segment is text-identical; allocation persists for all operations. Value proof/native cost OPEN; B0.7 contradiction separately required. | `S5/core/evaluation_finalization_c.adb:121-256`; `D3/DESIGN.md:694-757`; `D4/APPENDIX-BINDINGS.md:681-695,1769`; `D4/DESIGN.md:576`; `D4/APPENDIX-COST-MAP.md:356-363`. |
| wl_resource_policy_admit | Input shape refusal precedes disk reads; disks stage before Data. The typed Decision is stored unconditionally through Encode_Decision, return 0; 255 handler retained. No new Result/input overlap guard. WF-F and source construction are correctly distinguished from native build-in-place/copy/padding/failure, all OPEN. | `S5/core/worldline-resource_policy_c_api.adb:120-182`; `D4/APPENDIX-BINDINGS.md:482-489,1761`; `D4/DESIGN.md:566`; `D4/APPENDIX-COST-MAP.md:253-259`. |
| wl_evaluation_history_select | Query and whole Data copy remain before query validation; optional Final_Row and staged history rows retain frontiers. One result write and handler 255 retained. Earlier query decoding needs M4/D-05 proof. Original arrays and new acceptance/result objects are separately classified; native effects OPEN. | `S5/core/worldline-evaluation_history_c_api.adb:133-190`; `D4/APPENDIX-BINDINGS.md:499-507,1762`; `D4/DESIGN.md:567`; `D4/APPENDIX-COST-MAP.md:265-272`. |
| wl_resource_run_ledger_check_v1 | Raw then Data/Before/Proposed/Observed copies precede Well_Formed. Accepted overlaps remain permitted; completed O.Value written once, return 0; handler -1. Source actual categories corrected; passing/result storage and full native accepted-domain costs OPEN. | `S5/core/resource_run_ledger_c_api.adb:192-222`; `D4/APPENDIX-BINDINGS.md:548-554,1765`; `D4/DESIGN.md:570`; `D4/APPENDIX-COST-MAP.md:278-282`. |
| wl_recovery_authorization_decide_v2 | Length/null/alignment guards precede Raw; Well_Formed refusal precedes write. Original accepted overlap, -1 and 0 retained. Owned from total wrapper replaces the original direct W.Decide store; the extra recheck and changed construction are explicit source deltas with D-36/native costs OPEN. | `S5/core/worldline-recovery_authorization_c_api.adb:129-150`; `D4/APPENDIX-BINDINGS.md:394-399,1751`; `D4/DESIGN.md:560`; `D4/APPENDIX-COST-MAP.md:435`. |

These comparisons support the intended source ordering and refusal mappings. They do not prove totality, installed legality, atomic copy behavior, padding, ABI/caller fidelity, source-to-object correspondence or preservation of every accepted native case. Size constants remain outside handlers; caller-sized nested allocations and original handlers remain where specified (`D3/DESIGN.md:271-277`). The full accepted domain remains fixed even if a new native object makes storage fail earlier.

## 3. Carried items and L1–L8

Carried RC1–RC3 and LD4-R are preserved at design level. Independent normalized-text comparisons found Diagnostic_Transport specification/body and Native_Diagnostic_Control equal the bound v3 §4.4 text, and finalization segment 6 equal v3 §5.1. The diagnostic site sequence block B6 and predecessor edits B5 are unchanged. B1, B2.1/B2.2, B3 and B7 also preserve their carried text; explicitly marked appended v4 notes do not replace it. Evidence: `D4/DESIGN.md:83-107`; `D3/DESIGN.md:509-577,729-749`; `D4/APPENDIX-BINDINGS.md:662-776,780-908`.

Appendix C was read in full. Its names, packet schedule and relocation map in the machine twin equal v3. The original ordered prefix and immediate PK-6a enrollment are preserved, with no reordering or reappend. Reviewer JACKAL: status=exact, parsed=6+2+14+6+3+57+10, exact=98; status=exact, parsed=535+98, exact=633. These are arithmetic over bound data, not proof coverage. Evidence: `D3/DESIGN.md:1918-1939,2478-2589`; `D4/DESIGN.md:105,109,160`; `D4/decisions.json:required_proved_append,append_schedule`.

All quoted replacements are correctly targeted and justified in purpose: naming/tile wording and actual interface checks repair binding; cost wording separates source/native claims; the ledger handler and C-01/C-05 rows repair effect classification; R9 fixes the actual metadata local; R15 removes the erroneous direct-store scope. R1/R10/R12 do not close the new gate/alias contradictions identified above. Evidence: `D4/DESIGN.md:178-265`.

| Defect | Independent assessment and repair |
|---|---|
| L1 | GENUINE; REPAIRED_AT_DESIGN_LEVEL. The old one non-use-type clause rule cannot support both transport use-visibility and unqualified Storage_Elements names. Exact scoped clauses now supply them. Installed resolution remains OPEN. `D4/APPENDIX-BINDINGS.md:75-77,1527-1565`; `D3/DESIGN.md:1789-1802`. |
| L2 | GENUINE; REPAIRED_AT_DESIGN_LEVEL. Status comparisons and Join_Verdict equality now have explicit operator visibility. The original C_API-level clauses do not already supply those types. `D4/APPENDIX-BINDINGS.md:1560,1564`; `S5/core/worldline-c_api.adb:27-32`. Compilation remains OPEN. |
| L3 | GENUINE unused rename after GE5–GE8; GE9 is a correct design repair. S5 uses K in Decide_Raw_Metadata only for the retargeted calls. Actual GNAT 16.1.0 warning behavior is UNVERIFIED, as the author now states. K in Decide_Raw_Context remains needed for types. `S5/core/worldline-c_api.adb:758-765,832-876`; `D4/APPENDIX-BINDINGS.md:742-756`. |
| L4 | GENUINE; REPAIRED_AT_DESIGN_LEVEL. The old sketch checked a quoted name anywhere, so Library_Name could mask missing membership. K3 now parses the actual ordered literal Library_Interface. `D3/APPENDIX-BINDINGS.md:1018-1020`; `S5/pending-component/pending.gpr:5-11`; `D4/APPENDIX-BINDINGS.md:1043-1060`. No sketch was executed. |
| L5 | GENUINE; REPAIRED_AT_DESIGN_LEVEL by per-form provenance for direct results and mutable out/in-out state. The separate B0.7 gate contradiction remains required RC4 work. `D4/DESIGN.md:68`; `D4/APPENDIX-BINDINGS.md:87-102,1729-1775`; `D3/DESIGN.md:1785-1788`. |
| L6 | GENUINE; REPAIRED_AT_DESIGN_LEVEL. S5's local is Joined_Metadata, and both the tile and carried R9 now name it. `S5/core/evaluation_completion_c.adb:973-978`; `D3/APPENDIX-BINDINGS.md:605`; `D4/APPENDIX-BINDINGS.md:649`; `D4/DESIGN.md:226-230`. |
| L7 | GENUINE; REPAIRED_AT_DESIGN_LEVEL. Policy and ledger directly store aggregates/function results, so they were wrongly in proposed local-then-write C-14 scope. Removal does not change baseline controls. `S5/core/worldline-resource_policy_c_api.adb:171-176`; `S5/core/worldline-resource_ledger_c_api.adb:166-172`; `D4/DESIGN.md:262-265`; `D4/APPENDIX-COST-MAP.md:451`. |
| L8 | GENUINE; REPAIRED_AT_DESIGN_LEVEL. The old object-name pattern also matches a subtype name followed by := in an initializer; the new colon negative lookahead excludes that operator while retaining actual declaration matching. `D3/APPENDIX-BINDINGS.md:1031-1035`; `D4/APPENDIX-BINDINGS.md:1144-1148,681`. Static reading only; deterministic mutation execution remains OPEN. |

Preserved rulings:

| Items | Disposition and evidence |
|---|---|
| LD1, LD2 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL; full body/caller proof and OB-048/custody evidence remain OPEN. `D3/DESIGN.md:113-138,197-260`. |
| LD3 | CONDITIONALLY_ACCEPTABLE_PENDING_D-13; exact mirror, original component ABI/native scope and no canonical proof credit. `D3/DESIGN.md:140-149`. |
| LD4 / LD4-R | WITHDRAWN / CLOSED_AT_DESIGN_LEVEL for RC1. `D3/DESIGN.md:151-168,326-664`. |
| LD5 | CONDITIONALLY_ACCEPTABLE; wire contracts preserved, source recheck cost explicit and native D-36 OPEN. `D3/DESIGN.md:170-180`. |
| LD6 | CONDITIONALLY_ACCEPTABLE; its V3-RC5 design condition is discharged here, but every original/additive control remains required. `D3/DESIGN.md:182-191,2215-2244`; `D4/DESIGN.md:534-629`. |
| D-05, D-19 | OPEN, with no helper Pre approved and no warning waiver by domain changes. `D3/DESIGN.md:247-252,880-893,2282`. |
| D-18 | CLOSED_AT_DESIGN_LEVEL for the index design; proof OPEN; unequal journal/history lengths retain the typed outcome. `D3/DESIGN.md:848-878`. |
| D-28 | CONDITIONALLY_ACCEPTABLE_AT_DESIGN_LEVEL; valid local initialization before nested calls, native costs OPEN. `D3/DESIGN.md:895-902`. |
| D-36; D-15/D-34/D-38 | OPEN for all construction forms and native/ABI/installed legality evidence. `D4/DESIGN.md:721,727,743-758`; `D4/APPENDIX-COST-MAP.md:435-482`. |
| N-03 | OPEN; full strict callee/body scope, no PROVED_ROW transfer. `D3/DESIGN.md:2292`. |
| N-04, N-07 | CLOSED_AT_DESIGN_LEVEL for explicit enrollments; proof/body/native obligations OPEN. `D3/DESIGN.md:2556,2578-2587`. |
| N-05 | OPEN; original exact-set control retained without subset reinterpretation. `D3/DESIGN.md:2294`; `D4/DESIGN.md:732`. |
| APPENDIX_C | CLOSED_AT_DESIGN_LEVEL for exact ordering/enrollment only. `D3/DESIGN.md:1918-1939,2478-2589`. |
| R2_NINE_CONDITIONS, PACKET_PLAN | NOT_CLOSED pending V3-RC4. RC5/RC6 design repairs do not clear implementation, adoption, execution or acceptance gates. `D4/DESIGN.md:735-737`; required findings above. |

## 4. Operator and lead ownership

**D-13:** retain the concrete operator choice before PK-7 for the component transport/library arrangement. Only the route preserving both original Decide exports, all interface units, SPARK_Mode-only mirror correspondence and original native controls is admissible. The lead prepares concrete source/project/link and evidence artifacts; this review chooses nothing. The reservation concerns the component architecture, not an approval requirement for pinning implementation files. Evidence: `D3/DESIGN.md:2252-2260`; `D4/decisions.json:187`; `W/work/integrated-proof-preparation/PLAN.md:104-107`.

**N-06:** protected native_sha256 provisioning and actual deployment remain under operator custody. The service refuses a changed digest before loading the library. An old-library deployment hold earns no consolidated-candidate or integrated-service acceptance credit. Evidence: `S5/protected-resource/run_service.py:117-120`; `D3/DESIGN.md:2262-2271`; `H/HANDOFF.md:164-166`.

**N-01:** confirming representation repair is lead-owned engineering, subject to the unchanged strict command, all C1–C8/E1–E6 constraints and independent ABI/GPT-6.1 review. Moving warnings into Off is not resolution; the warning remains OPEN if the confirming repair fails. A nonconfirming material ABI change is outside this design and operator-owned, with no authority to reduce the target. Evidence: `D3/DESIGN.md:2012-2052,2273`; `H/HANDOFF.md:158-161`; `P:32-34`.

I found no mislabelled routine engineering decision and no added approval gate merely because a file is pinned. HANDOFF acceptance item 1 expressly uses reviewed deltas and recomputed effective pins. Original reserved decisions and merge/release/install/sudo/production/PRIME gates remain. A brief or prior reviewer ruling supplies no new authority. Evidence: `H/HANDOFF.md:153,165-166`; `P:72-74`; `D4/DESIGN.md:763,782`.

## 5. Fixed guarantees, additional findings and open obligations

No additional contract/domain/accepted-case/floor/control/proof-scope weakening or assumption was found beyond the required RC4 specification gaps. This is a design-review finding, not proof that a future implementation satisfies the target.

The manifest was read/AST-inspected only. Its observed SHA-256 is 51dd30d1a2c19cea4b9794e869400c5cb7c4193043f66678e62efa695b058fcb, equal to the sealed v3 review's source identity. The literal floor is 251 and the boundary is exactly {worldline-c_api}. The ordered required-name digest is bf1ec89a4421ad152213721a6bd49f558a4d8847ea1c3fbe84a864519368890b; the effective literal pin-map digest is 42f1809c2ec5a6ed4dbcb639a91c62f50ab80c75787d7110a0a69618bb9ec8c4. Both independently reconstructed digests equal v3. Evidence: `S5/runtime/worldline/proof_manifest.py:22-25,312-316,329,418,924-1029`; checks.json retains the AST segment observations.

Reviewer JACKAL totals are status=exact, parsed=280+11+4+5+8+31+34+46+1+115, exact=535 for the original prefix; status=exact, parsed=82+8+8+6+4+6+10+0+0+4+0+38+0+1+0+2+0, exact=169 for effective pin keys. The proposed component schedule is status=exact, parsed=169+4+2+1, exact=176; optional original pending-body pins give status=exact, parsed=169+4+2+1+2, exact=178. These conditional arithmetic results establish no semantic pin adequacy, installed identity or proof.

For **every** reviewer JACKAL result, the returned status is **exact**, formal=false, lane=rat, assurance **exact rational arithmetic (not yet checker-covered)**. Verbatim non_claims:

- NOT formal-bounded: this lane carries no Lean-checked certificate
- The epistemic class above is the STRONGEST claim this result supports
- exact rational arithmetic (not yet checker-covered)

The consequence for code correctness is informational and conditional on the observed inputs. No result is formal-bounded, a native measurement, proof credit or acceptance evidence.

The full body/unit/caller scope remains independent of named enrollment (`S5/runtime/worldline/proof_manifest.py:863-868`; `D3/DESIGN.md:1925`). No new array equality/length guard, transport-facing Pre, functional-contract reduction, canonical Off exemption, suppression, justification or assumption is proposed (`D3/DESIGN.md:222-260,311-322`; `D4/DESIGN.md:109,747-761`). No new native domain cap, proof-only light library, suppressed checked Ghost code or accepted-refusal credit for storage failure is introduced. Original runtime selection, Big_Integer/controlled operations, allocation/representability, stack/heap and checked assertion obligations stay OPEN (`D4/APPENDIX-COST-MAP.md:19,453-482`).

Original ordinary, lifetime, deterministic, additive, provider and fault controls remain required on the exact integrated candidate; none ran here (`D3/DESIGN.md:2217-2244`; `H/HANDOFF.md:162-164`). N-05's original exact-set assertion/import route was read, not executed or weakened (`S5/tests/test_authority_static_audit.py:268-280,314-321`; `S5/verify_proof_manifest.py:22-44`).

OB-048 still covers the enlarged and pre-existing Off surface. Pins and returned flags do not establish custody, immutability, authentic producers or measured confinement. None of those targets is deferred out of Phase One (`D3/DESIGN.md:2192-2211`; `H/HANDOFF.md:29`; `P:32-46`).

The root-worker draft overlap and rename-capture hazards remain OPEN. Its bound bytes were hashed, but the draft was not qualified, merged or resolved here. A changed base requires re-observed residual/glue/inventory identities and affected-scope re-review; integration order remains a lead decision (`D4/DESIGN.md:768-782`). The author's TaskStop deviation record was read as disclosed process history, with no transferred authority; this reviewer interrupted nothing (`WT/deviations/capi-v4-author-taskstop/NOTE.md:1-30`; `D4/AUTHOR-NOTES.md:78-94`).

Outstanding work includes the required RC4 repairs; installed legality and strict full proof; D-05/D-18/D-19/N-01/N-03; D-15/D-34/D-38; D-36 and all native C21 evidence; exact manifest/packet/pin/mutation implementation; all original and additive runtime controls; class-H failure/copy effects; OB-048/custody/provenance/confinement; N-05; the root-worker rebase; D-13/N-06 and original publication/deployment gates. The complete ruling and obligation lists are in review.json.

**proof_acceptance=false; source_acceptance=false; phase_acceptance=false.**
