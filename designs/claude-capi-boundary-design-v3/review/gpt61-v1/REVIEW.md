**WORLDLINE Phase One C-API boundary consolidation — independent DESIGN v3 review**

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.** RC1, RC2 and RC3 are CLOSED_AT_DESIGN_LEVEL. RC4, RC5 and RC6 are NOT_CLOSED. Required changes are V3-RC4, V3-RC5 and V3-RC6 below. This is a design verdict only: proof_acceptance=false, phase_acceptance=false and source_acceptance=false. It authorizes no implementation, execution, adoption, deployment or operator decision.

Reviewer selection: actual gpt-6.1-sol; different_from_author=true. Author: Claude Code lead claude-opus-5-5, through a drafting subagent. This reviewer authored nothing under review. Earlier reviews are lineage; their evidence does not transfer to changed source.

**Scope, identities and method**

D3 is /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v3. Unprefixed DESIGN.md, decisions.json and appendix references below are in D3. W is /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow; S5 is W/work/claude-composition-v5-beta/source; S4 is W/work/reviewed-common-proof-source-composition-v4/source; V2 is W/work/claude-capi-boundary-design-v2; H is W/outputs/claude-phase1-handoff-20261004. P is /home/sicarii/Documents/complete-phase1-prompt.txt. G is /home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1. All cited source was read passively.

| Reviewed file | Independently computed sha256 | Supplied pin |
|---|---|---|
| DESIGN.md | a8a120c9a704177cdab5232a757f1ef405cb3ad1c694ff135cdd2e8f26a14aa7 | MATCH |
| decisions.json | 2517dd49f6b96e4fe23cd9631aead320ac038605b7286fe8fc5b72c92d99813a | MATCH |
| APPENDIX-BINDINGS.md | 5ffb8736b6ce89f655041129991ed0bce4133941129bc7b1566b0da68695d32e | MATCH |
| APPENDIX-COST-MAP.md | c2a320a266fdd088c203e0d61f4cd7c5ea94f7b3b731f5be400f6b2f3d5b114f | MATCH |

Every bound-input hash in decisions.json was checked: no mismatches. The V2 review freeze and S5 composition review freeze match their named files, bytes and modes. S5's whole source inventory also matches file bytes, hashes and modes with no extra files. Its review disposition is QUALIFIED_SOURCE_COMPOSITION with all acceptance flags false. The reviewed C-API unit pairs, existing C_API pair, completion contracts, core projects and pending component files specified at DESIGN.md:40-46 are byte-identical across S4/S5. The separately bound Optional_Marker approval and the S5 finalization changes remain their own deltas.

The inventory arithmetic uses actual JACKAL MCP, status=exact and formal=false: parsed=6+4+52+24+1 gives exact=87 bound inputs; the inventory partition expression retained in checks.json gives exact=637 source files. These are arithmetic checks conditional on the static inventories, not evidence authenticity or code correctness.

Only passive reads, hashing and standard-library JSON/text/whitelist AST reconstruction were performed. proof_manifest.py was never imported or executed. No compiler, prover, build, test, WORLDLINE code, service, window/reservation, vault/restic, SIA note or production action was run. Only the current review directory was written. Each numbered item has a create-only checkpoint. The review uses the automatic Ada/SPARK skills, relevant language/interfacing/exception/concurrency chapters, advanced-Ada RM 6.2 guidance, GNAT guidance and the high-integrity guidance. SPARK Guide release 28.0w guidance is distinct from installed GNAT/SPARK 16.1.0 evidence.

**1. Closure of V2 RC1–RC6**

| Target | Verdict | Evidence and boundary |
|---|---|---|
| RC1 | CLOSED_AT_DESIGN_LEVEL | LD4-R retains state, control codes, latch, formatting and overflow decisions in SPARK; only irreducible transport remains Off. DESIGN.md:155-168,360-641. Installed legality, strict proof and native correspondence remain OPEN. |
| RC2 | CLOSED_AT_DESIGN_LEVEL | Separate no-row/row value interfaces; fully defined acceptance variants/out paths; non-narrowing completion index route. DESIGN.md:694-750,775-902. Actual body/caller/flow/RTE proof remains OPEN. |
| RC3 | CLOSED_AT_DESIGN_LEVEL | N-01 is strict, with no informational waiver or relocation-as-resolution; confirming representation packets require ABI identity and independent review. DESIGN.md:1997-2052. No warning is discharged here. |
| RC4 | NOT_CLOSED | O6(b)/(c) inventory/enforcement is deferred; R-W/O4 conflicts with actual write forms; K3's sketch does not establish Library_Interface membership. DESIGN.md:1791-1804; APPENDIX-BINDINGS.md:28-43,330-354,379-380,1014-1022,1039-1049. V3-RC4 is required. |
| RC5 | NOT_CLOSED | Stages, suffix, immediate enrollment and seal are repaired. PK-0 still misstates guard read frontiers and treats defined parts of handled exceptions as wholly undefined. DESIGN.md:1893-1984, especially 1943-1956; S5/core/evaluation_pending_c.adb:118-133; S5/core/worldline-resource_ledger_c_api.adb:162-176. V3-RC5 is required. |
| RC6 | NOT_CLOSED | The type/call-site inventory is substantially improved, but diagnostic fit counts, run-ledger actual classification and categorical native mechanism claims need correction. APPENDIX-COST-MAP.md:25,39-42,219,240,348-350,396-402. V3-RC6 is required. |

For RC1, the External abstract state has no narrowed volatility properties; its constituents remain the original Atomic Booleans initialized False. Reads use local initializers/assignment contexts and state changes use procedures, addressing the original E0004/E0005 structure. Start preserves the active read, failure reset and enable order before trace.begin; stop preserves trace.end before disabling and reading the failure latch. Nested Value/Exception paths retain the second active read in Mark. This does not turn the original check-then-act into a synchronized operation (DESIGN.md:360-410,437-502,599-625; S5/core/evaluation_completion_c.adb:39-88; G/share/spark/explain_codes/E0004.md and E0005.md).

T1 and T2 are stderr Put_Line/Flush through the installed Off Standard_Error entity. T3 is failure handling around those effects and native composition/storage failure; its sole semantic action calls the SPARK latch. T4 obtains exception information from a transport-held occurrence/choice parameter without adding a Global-null assumption. T5 routes the necessary interleaving on SPARK-returned flags/enumerations. Each is irreducible transport in this installed-tool setting; none licenses diagnostic state or value decisions in Off code (DESIGN.md:515-590; G/libexec/spark/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude/a-textio.ads:189,199 and a-except.ads:94). External/Atomic legality, Image modelling, exact concatenation proof and native allocation effects are explicitly OPEN (DESIGN.md:619-641). “Analyzable” here is the proposed scope, not an unperformed GNATprove result.

For RC2, Operations 0/1 keep the original caller-count-sized Captured allocation and Rows extent guard but never pass or read Captured. Operations 2/3 pass it only after the fully assigning row loop. Rejected/accepted context variants define all fields in their active variant, avoiding the V2 early-return/out-formal defect (DESIGN.md:694-750,775-846). The completion route relies on existing History_Index and Apply/Update_Reference contracts, preserving unequal-length History_Invalid output with return 0. Both Retain_Terminal and Already_Retained are covered; no new length equality refusal or helper Pre is introduced (DESIGN.md:848-878; S5/core/evaluation_completion.ads:325-338,351-362,414-433). The original raw Operation gate and post-decision malformed-span refusal remain; D-19 strict evidence stays OPEN (DESIGN.md:880-893).

**2. Source spot checks and cost-map assessment**

The following checks compare design sequences with the actual S5 bodies. They support the specified source staging; they do not establish every accepted native case or exception effect.

| Unit | Source comparison and finding |
|---|---|
| U2 recovery select | Flags precede Expected shape, then present-only Live/Prepared shape checks. Captures remain Expected, Live, Prepared. Absent pointers/lengths stay ignored and absent differs from present-empty. No writes; 255 handler covers copies. Marker_Of/Select_Value describe total flag handling without a new accepted-case refusal. The extra byte constants and marker construction can change peak storage, so native accepted-domain preservation remains OPEN. DESIGN.md:1007-1051; S5/core/worldline-recovery_c_api.adb:37-85; APPENDIX-COST-MAP.md:110-122. |
| U7 ledger compute/headroom | Size constants remain outside handlers. Compute keeps extent guards, Data before rows, per-row refusal before later rows, existing L.Compute, then unconditional Detail_Data, Total_Data, ascending Details and Result writes. Headroom captures A/W/F and gates Data through their acceptance first, then writes Output and Result unconditionally. No new overlap guard replaces the documented disjointness premise. Handler 255 can follow earlier writes; no transactional guarantee is established. Decoder proof and result construction/native costs remain OPEN. DESIGN.md:1201-1245; S5/core/worldline-resource_ledger_c_api.adb:115-176,184-223; APPENDIX-BINDINGS.md:307-359; APPENDIX-COST-MAP.md:179-191. |
| U14 completion/context | Header/extent/value runs remain interleaved. Original arrays stay unconditional in decide/raw; context rows remain staged with first-failure diagnostics and later rows unread. Defined variants and initialized Response cover all outputs. Existing raw Operation and malformed-span refusals remain. No journal/history equality guard is added. Proof of conversions/indexing and all relevant callers is still required. DESIGN.md:775-891,1380-1548; S5/core/evaluation_completion_c.adb:393-528,530-696,785-868; APPENDIX-BINDINGS.md:498-587. |
| U15 finalization decide | Fixed extents, captured X, later per-array extents/disjointness and fields keep order. Rows is validated for every operation. Data/Required/Captured allocations remain ordered in the handler. Plans precede the row-dependent branch; Operations 0/1 perform no row read. Reasons 0/1/2 remain written on transport success, reason then promotion diagnostics precede the single output write, and the handler returns 255. Pure/infallible decode movement and new result/initialization costs remain OPEN. DESIGN.md:694-750,1554-1573; S5/core/evaluation_finalization_c.adb:122-199,235-256; APPENDIX-BINDINGS.md:626-663; APPENDIX-COST-MAP.md:284-297. |

Additional checks of U3/U4 support capture-before-write and retained accepted overlap, direct Well_Formed before Decide_Total, unchanged wire contracts and refusal -1. The wrapper repeats Well_Formed; it is a native delta. The source-path tally is JACKAL status=exact: parsed=1+1 gives exact=2 release evaluations and parsed=1+1+1 gives exact=3 checked evaluations on an accepted call. This counts described source evaluations, not independently observed emitted instructions (DESIGN.md:1053-1099; S5/core/worldline-recovery_authorization_c_api.adb:129-150; S5/core/worldline-recovery_authorization_v3_c_api.adb:139-167; APPENDIX-COST-MAP.md:124-151).

RM 6.2 classification is now appropriate: elementary parameters are by copy; plain nonlimited untagged composites with no by-reference subcomponent have an unspecified mechanism. “in” or “in out” does not imply reference passing. The proposed type reading identifies no by-reference profile type, while exhaustive type closure and each matching GNAT choice remain OPEN (DESIGN.md:2068-2071; APPENDIX-COST-MAP.md:21-24,60-96; /home/sicarii/.agents/skills/advanced-ada/chapters/ch12-subprograms.md:8-12).

The cost statements are **not yet resolved as claimed**:

- The normal active fitting Mark path calls Line_Fits in Begin_Line and again in Diagnostic_Line. Value_Fits and Exception_Fits likewise occur in both their Begin procedure and guarded composer. For each reached fitting pair, JACKAL status=exact, parsed=1+1, exact=2 source predicate evaluations. Nested Mark has its own active gate and fit pair. C18's “one length test” statements therefore undercount the design. The Image source delta is status=exact, parsed=2-1, exact=1, as the map already observes (DESIGN.md:429-434,450-472,519-552; APPENDIX-COST-MAP.md:348-350).
- Run-ledger has Data, Before, Proposed and Observed arrays, plus Raw as a record. JACKAL status=exact, parsed=1+2+1, exact=4 array actuals. C12 calls them “five array actuals” despite its own correct type list (APPENDIX-COST-MAP.md:219; DESIGN.md:1327-1334).
- X3's “it executes” is not established merely by absence of suppression. The mandatory source semantics of a check differ from whether matching code emits a redundant test. The Ri mandatory storage/copy wording and “at -O0 no temporary is elided” also overstate the available native evidence. Cross-unit source calls should be separated from emitted calls/inlining, particularly where V2 completes expression functions in visible specs. Installed GNAT documentation gives ordinary cross-unit inlining conditions, but is not object-code evidence for each new call site (DESIGN.md:229-230,2073-2079; APPENDIX-COST-MAP.md:25,39-42,240; /home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/share/info/gnat_ugn.info:14798-14835,11252-11260).
- C9's ALLOC “=” must be restricted to the original allocations it describes; X4 and new result/copy temporaries remain separate OPEN costs. Direct Encode_Quantity/Result_Of/Encode_Decision stores also need a consistent construction account rather than a blanket completed-local claim (APPENDIX-COST-MAP.md:182-191,364-370; DESIGN.md:266-269).

C21 correctly requires generated-code, stack/storage, accepted-domain allocation, assertion and exception-write evidence and independent review. Keeping these OPEN is sound, but does not repair the inconsistent map. D-36, original Big_Integer representability/runtime/Normalize failure, checked Ghost/reference/contract costs and implicit Adjust/Finalize remain required. A caught new Storage_Error is failure to preserve an originally accepted computation, never an accepted refusal or a reason for a cap (DESIGN.md:271-277,2122-2134; APPENDIX-COST-MAP.md:376-402; H/HANDOFF.md:129-131).

**3. Binding, stage identity and append-only review**

Whole-closure home checks are a sound improvement over V2's C_API-only checks: all core Ada files, component Ada files and their projects are covered, with literal symbol homes, exact relocated declarations, alternate-binding prohibitions, old-home absence and raw-pointer removal from moved SPARK units. Every relocated declaration text and old/new declaration hash matches the original with only the identifier changed (DESIGN.md:1746-1778; APPENDIX-BINDINGS.md:76-190).

The conditional arithmetic is JACKAL status=exact: parsed=66+71 gives exact=137 core Ada files; parsed=6+8 gives exact=14 component Ada files; parsed=10+4+5+5+3+31+3+4+3+3+2+3+4+5+4+2 gives exact=91 core symbols; parsed=91-31 gives exact=60 inventory symbols; parsed=2+3+4+1+2+6+2 gives exact=20 relocated exports. These calculations are not closure or native symbol evidence. Matching executable symbol resolution and ABI remain OPEN (DESIGN.md:1768-1778,1854-1864).

RC4 remains incomplete for concrete reasons. DESIGN.md:1802 defers the scoped renames/use inventory. B8 checks K3 by looking for quoted unit strings anywhere, not actual Library_Interface membership (APPENDIX-BINDINGS.md:1014-1022). O4/R-W requires constant result objects except its stated completion/finalization exceptions, but B4 directly stores SPARK encoder results for ledger/policy and writes mutable buffers produced by L.Compute/L.Compute_Headroom; lifecycle also stores a Mask_Byte function result from Plan's mutable out mask (DESIGN.md:1791-1795; APPENDIX-BINDINGS.md:28-34,281-305,330-354,379-380). The tables and checking plan must define these forms consistently. B8's ordered-subsequence/count algorithm alone does not enforce the advertised immediate discriminant gate, sole assignments or absence of earlier payload selections. Full-body/caller review is also explicitly required; tokens never prove reachability/custody (APPENDIX-BINDINGS.md:1039-1049; DESIGN.md:1854-1864). V3-RC4 asks for a complete design specification, not an unauthorized build or implementation in this review.

Each old E1–E4 block occurs exactly once in S5's manifest. The exact old/new pairs preserve unrelated predecessor checks and their problem text. E1/E2 remap only the V3/protocol symbols at PK-2; E3 binds the chain SPARK replay/result path at PK-5; E4 remaps finalization names/home at PK-6b. PP2's undo-edits/delete-tails reconstruction plus PP3's predecessor-first call is a sound preservation rule (DESIGN.md:1814-1827; APPENDIX-BINDINGS.md:794-879; S5/runtime/worldline/proof_manifest.py:488-504,929-950). The independent block hashes are retained in checks.json. The existing compose code appends the final effective pin refresh rather than changing original pin literals, consistent with this reconstruction design (W/work/claude-workflow-v1/compose.py:162-190).

Identity layers I1–I7 correctly bind touched Ada/core/wire sources, projects/headers, component additions, optional Ada controls, raw Python/helper/data bytes, provider correspondence and the whole inventory/manifest/frame. Raw Python/control bytes are not laundered through normalized Ada pins. Every stage binds its exact predecessor and inventory; untouched files keep their raw base hashes (DESIGN.md:1829-1841; APPENDIX-BINDINGS.md:899-914). Component keys are additive: JACKAL status=exact, parsed=169+4+2+1, exact=176 under D-13(i), or parsed=169+4+2+1+2, exact=178 with optional pending core pins. New keys alter proof_source_files and are explicitly part of the packet's reviewed install set.

Passive AST reconstruction yields the original ordered required prefix: status=exact, parsed=280+11+4+5+8+31+34+46+1+115, exact=535. Effective pins: status=exact, parsed=82+8+8+6+4+6+10+0+0+4+0+38+0+1+0+2+0, exact=169. Existing pin values independently match the source normalization. The floor remains 251 and the boundary remains exactly {worldline-c_api}; no candidate code was evaluated to obtain these facts (S5/runtime/worldline/proof_manifest.py:22-25,312-316,329-426,924-1029).

Appendix C and decisions.json contain identical ordered suffix names, with no duplicates or original-prefix collisions. The monotonic stages agree:

| Packet | Suffix slice | Required length after packet (status=exact, parsed input) | C_API symbol count (status=exact, parsed input) |
|---|---|---|---|
| PK-1 | 1–6 | 541; parsed=535+6 | 33; parsed=31+2 |
| PK-2 | 7–8 | 543; parsed=535+6+2 | 36; parsed=31+2+3 |
| PK-3 | 9–22 | 557; parsed=535+6+2+14 | 40; parsed=31+2+3+4 |
| PK-4 | 23–28 | 563; parsed=535+6+2+14+6 | 41; parsed=31+2+3+4+1 |
| PK-5 | 29–31 | 566; parsed=535+6+2+14+6+3 | 43; parsed=31+2+3+4+1+2 |
| PK-6a | 32–88 | 623; parsed=535+6+2+14+6+3+57 | 43; transport not yet moved |
| PK-6b | no append | 623; unchanged | 49; parsed=31+2+3+4+1+2+6 |
| PK-7 | 89–98 | 633; parsed=535+6+2+14+6+3+57+10 | 51; parsed=31+2+3+4+1+2+6+2 |

Each slice endpoint/start calculation and receipt is in checks.json. Suffix total: status=exact, parsed=6+2+14+6+3+57+10, exact=98. PK-6a enrolls and pins its semantic bodies immediately. PK-6b, representation packets and PK-S append no names. The original ordered prefix remains exact, and full per-unit coverage/callers are not replaced by names (DESIGN.md:1893-1940,2478-2588; APPENDIX-BINDINGS.md:47-72).

Lineage is strictly linear from qualified S5, with each packet based on the exact reviewed predecessor and any changed base requiring affected-scope re-review. Family representation repairs follow legal movement and precede the seal; failure to remove a warning without changing layout keeps N-01 OPEN. PK-S can freeze identities/assemble evidence only, never fix semantics, reorder enrollment or grant acceptance (DESIGN.md:1870-1891,1970-1984).

PK-0 remains the RC5 gap. “Guard refusals: return before any foreign read or write” is false for later guards: pending captures R before transport length/extent/disjointness checks, and finalization captures X before its named transport-guard refusal (DESIGN.md:1946,1557-1562,1698-1703; S5/core/evaluation_pending_c.adb:118-133; S5/core/evaluation_finalization_c.adb:136-156). Similarly, internal writeback exceptions are not wholly undefined: ledger's preceding writes are ordered and its handler maps handled exceptions to 255. Exact copy atomicity/native failure locations may be unresolved, but those defined effects must be retained (DESIGN.md:1953-1954; S5/core/worldline-resource_ledger_c_api.adb:162-176,212-223). Foreign-pointer faults/outside-premise behavior must remain separate. C-14 as a stronger proposed behavior rather than baseline is the correct distinction; V3-RC5 repairs the remaining classification.

**4. Operator ownership and confirming representation packets**

D-13 is correctly operator-owned before PK-7. Option (i) is a concrete design candidate: preserve both component Decide exports in a component-local existing-Off transport, retain all original interface units and exact SPARK_Mode-only mirrors, add source/project pins, and preserve separate component native/body/ABI controls. It creates no new core Off exemption or proof credit. Options (ii) dropping Decide and (iii) abandoning the mirror are inadmissible under the fixed target. The packet still needs exact source/project/link closure, profiles/layouts, matching positive/refusal controls, identity and independent review. This review chooses no option and grants no operator approval (DESIGN.md:140-149,2252-2260; decisions.json:146-157; APPENDIX-BINDINGS.md:113-127; W/work/integrated-proof-preparation/PLAN.md:104-107).

N-06 is correctly operator-owned at deployment. The service compares the protected native_sha256 against the library before loading it. Re-provisioning must bind the installed and loaded reviewed library to the same source/proof/control identity under operator custody, retain mismatch refusal and supply its provisioning/rollback evidence. Keeping the old library is a recorded deployment hold; it cannot count as successor-service or integrated acceptance (DESIGN.md:2262-2271; decisions.json:159-168; S5/protected-resource/run_service.py:117-119).

N-01 is correctly lead-owned strict engineering. Confirming representation clauses are conditionally admissible as reviewed ABI-preserving PK-xR packets. They must preserve scalar widths/signedness/conventions, every Size/Object_Size/Alignment/position/bit range/array stride/relevant padding, sentinels, headers/ctypes and ABI version across every actual target/scenario, including checks, release and component builds. They need exact compiler representation values, installed legality, full strict evidence, baseline-matching layout evidence and independent ABI/actual GPT-6.1 reviews. A layout fixture alone does not prove analysis precision. A nonconfirming layout proposal is outside this design, needs the applicable operator decision, and still cannot lower the original guarantee (DESIGN.md:1970-1984,2020-2052,2273).

The diagnostic dataset's representation-warning sum is JACKAL status=exact, parsed=205+79+41+48+99+27+36+61+64+0+11+5+27+33+0, exact=736. Relocated warnings are not counted as resolved; layout/boundary obligations remain. No informational or operator waiver remains (DESIGN.md:1997-2018). No additional operator/lead ownership mislabel was found. Neither operator choice nor a design-level closure discharges proof, domain or strict-warning obligations.

**5. Fixed guarantees, carried rulings and remaining obligations**

No new domain cap, accepted-case reduction, lowered contract/floor, removed original deterministic control, suppressed checked assertion/Ghost route, assumption, restored core Off exemption or renamed-Boolean substitute for custody/confinement is authorized by the design. The original command, complete matching-source bodies/references/callers/flow/RTE/termination/native scope, zero unproved/justified/Assume and original ordinary/additive/lifetime/provider/fault controls remain required (DESIGN.md:222-253,271-277,1918-1925,2215-2244,2303-2324; H/HANDOFF.md:27-29,129-131,158-166; P:64-66). The RC4/RC5/RC6 defects above must be repaired without weakening any of those targets.

Carried rulings:

| Item | Design ruling and required evidence |
|---|---|
| LD1 / LD2 | Conditional scope/totality designs remain; complete body/caller/semantic/native evidence is OPEN. Global null gives no functional or custody guarantee. DESIGN.md:113-138,195-277. |
| LD3 / LD4 / LD4-R | LD3 waits for D-13; old wholesale LD4 is withdrawn; LD4-R closes RC1 at design level only. DESIGN.md:140-168,360-641. |
| LD5 / LD6 | Retained wire contracts/total wrappers and additive controls are conditional. Costs and faithful PK-0 baseline remain OPEN, including V3-RC5/V3-RC6. DESIGN.md:170-191. |
| D-05 | Partial-decoder inventory stays OPEN: demonstrate contextual proof at every original caller or separately review total restructuring. No helper Pre or assumed fact is approved. DESIGN.md:247-252,2282. |
| D-18 / D-19 | Index design is non-narrowing and design-closed; its proof is OPEN. Raw gate/branches remain and strict-warning disposition is OPEN. DESIGN.md:848-893. |
| D-28 | Fixed valid local initialization is design-admissible; original branch outcomes and full native initialization/copy/storage costs remain OPEN. DESIGN.md:895-902; APPENDIX-COST-MAP.md:299-323. |
| D-36 | OPEN across all listed construction forms; no malformed-input fixture or proposed stronger behavior settles original internal-exception equivalence. APPENDIX-COST-MAP.md:355-372,396-402. |
| D-15 / D-34 / D-38 | Native export/layout/loaded-library and installed-tool legality remain OPEN. DESIGN.md:1768-1778,1854-1864. |
| N-03 | Existing callee full strict proof remains required; reported PROVED_ROW entries transfer no credit. DESIGN.md:2292. |
| N-04 / N-07 | Classify and both pending Decide bodies are explicitly appended; unit-wide/caller proof remains required. DESIGN.md:2293,2296,2556,2582,2587. |
| N-05 | Original static-audit mismatch remains OPEN. Its exact-set assertion may not silently become only subset membership or be removed. Any concrete correction needs separate review preserving the original required guarantee. DESIGN.md:2294; S5/tests/test_authority_static_audit.py:268-280,314-321; S5/verify_proof_manifest.py:22-44. |
| R2_NINE_CONDITIONS | NOT_CLOSED pending V3-RC4; full-body/caller and native evidence remain separate from token matches. DESIGN.md:1730-1864,2297. |
| APPENDIX_C | CLOSED_AT_DESIGN_LEVEL for literal ordered append/enrollment; no proof or acceptance credit. DESIGN.md:1916-1940,2478-2588. |
| PACKET_PLAN | NOT_CLOSED pending V3-RC4/V3-RC5/V3-RC6; exact lineage and seal rules are sound elements. DESIGN.md:1870-1993. |

The Optional_Marker change is a separately approved S5 delta, not a new permission or proof in v3. Its later bound approval supersedes the historical unanswered-approval note in the handoff, while all original callers/native obligations remain required (DESIGN.md:38-46,1002-1005; W/work/claude-lead-v2/approvals/optional-marker-api-v1/approval.json; H/HANDOFF.md:121).

The root-worker draft lane shares core/worldline-c_api.adb with this design: S5's file is observed at 56596 bytes, sha256 0a17c0efb95904ee865182a20d3bcabceeef93b1cc3639687aab27696339f35b; the draft file is observed at 148068 bytes, sha256 806f3972277d9385b0d32c5e3faf1bf6fb24f9024dbc1c8274411b8c1d0e3420. This is an OPEN integration overlap, not an executed merge conflict or qualification of the draft. A qualified worker successor requires the exact-base and affected-scope re-review rules; neither a blind overlay nor review transfer is admissible (DESIGN.md:1872-1891; W/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1/review/gpt61-v1/REVIEW.md:44).

Remaining obligations include diagnostic legality/Image/overflow proof; full value/decoder/conversion/index/initialization/caller/flow/RTE/termination proofs; N-01 and every strict warning; D-15/D-34/D-38 ABI/native identity; D-28/D-35/D-36 and full original/new runtime, copy, allocation, Adjust/Finalize, stack, checked Ghost/reference/contract costs; every original control/campaign; OB-048 for the complete enlarged and pre-existing boundary; authentic producers, custody, confinement and repeated-read premises; D-13/N-06 and all original applicable operator gates; exact linear stage/frame/source/control identities and independent actual GPT-6.1 reviews. All remain OPEN until their original closure evidence exists. Finite controls, arithmetic and hashes do not replace it.

**Required design changes**

**V3-RC4.** Complete the exact scoped rename/use inventory and deterministic checks, make K3 check actual Library_Interface membership, and reconcile O4/R-W with every B4 write form. Specify and enforce direct function-result provenance, mutable SPARK out-result provenance, sole/exclusive assignments and discriminant-before-payload gating. Align the rules, tables and sketch without silently relaxing a guarantee. Evidence: DESIGN.md:1791-1804; APPENDIX-BINDINGS.md:28-43,330-354,379-380,1014-1022,1039-1049; APPENDIX-COST-MAP.md:364-370.

**V3-RC5.** Correct PK-0's per-export/per-input-class read frontiers and preserve defined handler/write-order effects on internal exceptions. Initial extent guards differ from later post-capture guards. Unknown native copy atomicity/failure locations remain OPEN; foreign faults/outside-premise cases remain separate. C-14's stronger no-partial-write proposal remains outside baseline conditions. Evidence: DESIGN.md:1943-1968; S5/core/evaluation_pending_c.adb:118-133; S5/core/evaluation_finalization_c.adb:136-156; S5/core/worldline-resource_ledger_c_api.adb:162-176,212-223.

**V3-RC6.** Correct diagnostic Fits counts and run-ledger actual categories, and distinguish source evaluation/construction points from emitted native calls/checks/copies/storage/elision/lifetimes. Remove unsupported categorical execution, Ri-copy/storage and -O0-elision claims; qualify ALLOC equality to the unchanged allocations actually identified. Keep all D-36 and full accepted-domain native blockers OPEN. Evidence: DESIGN.md:429-434,450-472,519-552,2073-2079; APPENDIX-COST-MAP.md:25,39-42,191,219,240,348-350,396-402.

These repairs require a new bound design and independent re-review. They grant no permission to lower the original target.

**JACKAL evidence boundary**

All derived arithmetic above was routed through the real MCP tool. Full parsed inputs, status=exact results, evaluator identity, assurance and non_claims are retained in checks.json. The assurance is verbatim: “exact rational arithmetic (not yet checker-covered)”; formal=false. These results are informational about code correctness and are conditional on the read inventories/call sites.

The returned non_claims are carried verbatim:

- NOT formal-bounded: this lane carries no Lean-checked certificate
- The epistemic class above is the STRONGEST claim this result supports
- exact rational arithmetic (not yet checker-covered)

No ledger is cited as evidence and no arithmetic result is presented as source, proof, native, phase or deployment acceptance.
