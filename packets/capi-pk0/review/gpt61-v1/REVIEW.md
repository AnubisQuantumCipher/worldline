# WORLDLINE Phase One C-API PK-0 — independent source review

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**

This is a passive source review of the exact packet identified below. It grants no source acceptance, run evidence, control evidence, proof acceptance, stage qualification or Phase One acceptance. The L0 baseline run and its recorded values remain **OPEN**. Frame v5 is UNQUALIFIED, with V5-B01/V5-B02 and the capacity gate blocking execution as stated in the task and `packet.json:5`; this review does not qualify those gates.

Reviewer actual model selection: **gpt-6.1-sol**. Different from author: **true**. Author: **Claude Code lead claude-opus-5-5 (drafting subagent)**. I authored none of the packet under review. No packet module, helper, test, WORLDLINE native library, compiler or prover was imported or executed. The author's historical “never run” and “no deviations” statements are recorded author statements, not authenticated execution provenance (`AUTHOR-NOTES.md:7-11,171-201`).

Citation roots:

- P = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/packets/capi-pk0`; unprefixed `files/tests/...`, `packet.json` and `AUTHOR-NOTES.md` citations are relative to P.
- S5 = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-composition-v5-beta/source`.
- WT = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1`; v3/v4/v5/v6 citations mean `WT/designs/claude-capi-boundary-design-v{version}/...`.
- W = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`.

## 1. Packet integrity and protected invariants

**Finding: current identities match; the payload is additive.** All packet-file SHA256 values and sizes match the requested identities and the packet manifest. All 95 bound L0 inputs have distinct paths and match both SHA256 and size. The 637 files named in S5's source inventory also match their recorded SHA256, size and mode. These observations were repeated before report sealing, without a mismatch. The six payload destination paths are absent in L0; `existing_files_touched` is empty and no payload changes an existing Ada source, runtime binding, project, test, manifest, pin or roster. This supports the present additive-source claim, not a claim about every historical action of the author. Evidence: `packet.json:13-43,58-153`; the complete observed binding records and inventory check are in `checks.json`.

| Protected value | Current source observation | Evidence |
|---|---|---|
| REQUIRED_PROVED | Ordered roster length 535, unique names 535; no appended packet names | `S5/runtime/worldline/proof_manifest.py:25,312,314,924,940,953,967,972,1003,1012`; `packet.json:35` |
| MINIMUM_CHECKS | 251 | `S5/runtime/worldline/proof_manifest.py:22`; `packet.json:36` |
| UNANALYZED_BOUNDARY | Exactly `{"worldline-c_api"}` | `S5/runtime/worldline/proof_manifest.py:316`; `packet.json:37` |
| Movers | 0; only new test/helper/JSON paths | `packet.json:23-40`; `v3/DESIGN.md:1897` |
| External_Name in worldline-c_api.ads | 31, unchanged | `S5/core/worldline-c_api.ads:72-243`; `packet.json:39` |

The AST inspection includes the literal append chain, rather than mistaking the initial list at line 25 for the final roster. The independent JACKAL MCP arithmetic returned **status=exact**, `parsed=280+11+4+5+8+31+34+46+1+115`, `exact=535`, `formal=false`, lane `rat`, assurance **exact rational arithmetic (not yet checker-covered)**. Its `non_claims` are carried verbatim:

- NOT formal-bounded: this lane carries no Lean-checked certificate
- The epistemic class above is the STRONGEST claim this result supports
- exact rational arithmetic (not yet checker-covered)

This arithmetic is informational about the literal lengths; it establishes no code, native, proof or acceptance result. The whole MCP response is retained in `checks.json`; the convenience ledger was not used as evidence.

The L0 composition, source inventory and sealed composition review match the packet's recorded identities; that review says QUALIFIED_SOURCE_COMPOSITION. The endorsed v6 review.json and REVIEW.md also match `packet.json:9-10`; its verdict is ENDORSED. Neither predecessor label supplies this packet's missing execution or acceptance.

## 2. Fidelity to the endorsed PK-0 design

**Finding: the declared scope, control roster and effect model match, but coverage and enforcement are incomplete.** The payload carries C-01 through C-07, C-11, C-13, C-15 and C-16 in baseline forms. C-12 is optional and not authored; C-14 is neither encoded nor a pass condition. C-08 through C-10 belong to later packets. No production mover or representation/ownership repair is supplied. Evidence: `packet.json:23-44`; `files/tests/capi_characterization.json:15-64`; `files/tests/test_capi_characterization.py:1-26`; `v3/DESIGN.md:1897,2225-2244`.

The JSON explicitly distinguishes R0 (before capture), R1 (after capture), R2 (element frontier), R3 (typed outcome), S, H and X. It records handler codes and canonical write statements, preserves completed multi-write effects in H, and leaves failure location, copy atomicity, native write construction and possible-outcome preservation OPEN. There are no H or X characterization cases. Class X says “nothing asserted,” including no promise that a foreign fault becomes a handler code. Evidence: `files/tests/capi_characterization.json:22-41,66-324`; `files/tests/test_capi_characterization.py:1144-1155`; `v4/DESIGN.md:534-629`.

The static records contain 609 distinct characterization cases, 28 diagnostic cases and 58 guarded cases; layout records name 15 version exports, 25 layout exports, 82 ctypes records and 72 header types. Those are source-record counts, not controls run or coverage proved. Static AST/JSON checks found no duplicate generated characterization names or unresolved diagnostic case references.

The corrected v4 model closes the historical v3 read-frontier classification issue and is carried by v5/v6 (`v4/review/gpt61-v1/REVIEW.md:62-68`; `v5/review/gpt61-v1/REVIEW.md:96`; `v6/review/gpt61-v1/REVIEW.md:229-230,287`). It does not excuse PK0-RC1's missing mixed context/metadata cases or PK0-RC3/RC4's failure/exact-diagnostic weaknesses.

## 3. Faithfulness to original S5 behavior

**Finding: sampled existing expectations follow S5, including defects; the mixed ready/authorized routes are missing.** I compared the following exports' bodies, fixture construction, expected codes, source read frontiers, writes and handlers.

| Export | Source-grounded finding | Evidence |
|---|---|---|
| wl_resource_ledger_compute | Initial and element refusals return 255 without writes. Data precedes rows. All typed statuses return 0, with unconditional writes in order: Detail_Data, Total_Data, ascending Details, Result. Handler 255 does not undo earlier completed writes. Typed refusal fixtures retain zero arenas and empty descriptors. | `S5/core/worldline-resource_ledger_c_api.adb:118-176`; `S5/core/resource_ledger.ads:161-205`; `files/tests/capi_characterization.json:148-165,504-508,538-540`; `files/tests/test_capi_characterization.py:328-349` |
| wl_resource_ledger_headroom | A, W and F are captured in that order before their Shape refusal; Data remains unread on that refusal. Normal writes are Output, then Result; return 0, handler 255. | `S5/core/worldline-resource_ledger_c_api.adb:186-223`; `files/tests/capi_characterization.json:169-185,563-570`; `files/tests/test_capi_characterization.py:353-368` |
| wl_pending_decide_v1 | Fixed extents/disjointness are R0. The Input capture precedes header/transport/value R1 guards; then Data and rows through the refusing element. One result write and return 0; handler 255. Reserve_New/Write_Pending expectations are source-derived predictions, not proof of Is_Successor. | `S5/core/evaluation_pending_c.adb:111-173`; `S5/core/evaluation_pending.ads:123-165`; `S5/core/evaluation_epoch.ads:13-22`; `files/tests/capi_characterization.json:216-231,645-686`; `files/tests/test_capi_characterization.py:460-518` |
| wl_completion_decide_v1 | Input capture precedes R1; Data and journal/captured/retained/history/required arrays are then staged in order. Typed Response is written with return 0; handler 255. C-15 retains the original length-mismatched History_Invalid result with return 0 and the terminal/already-retained summaries. | `S5/core/evaluation_completion_c.adb:393-527`; `S5/core/evaluation_completion.ads:351-433`; `files/tests/capi_characterization.json:249-261,787-843`; `files/tests/test_capi_characterization.py:678-768` |
| wl_completion_raw_decide_v1 | Operation must be 2. A check row is validated before its Wire and Confinement; both are captured before their validity refusal. Post-decision span and binding guards return 255 before the sole output write; handler 255. These guards remain original behavior, not a stronger repair. | `S5/core/evaluation_completion_c.adb:529-692`; `files/tests/capi_characterization.json:263-273,846-869`; `files/tests/test_capi_characterization.py:751-768` |
| wl_finalization_decide_v1 | Diagnostic entry precedes R0; Input, transport guards, Data and plans follow. Operations 0/1 allocate Captured but read no Rows. Operations 2/3 stage Rows. Reason/promotion lines precede one Result write with return 0; the exception diagnostic precedes handler 255. C-16 preserves unwritten and PROT_NONE Rows. | `S5/core/evaluation_finalization_c.adb:121-256`; `files/tests/capi_characterization.json:299-311,896-941`; `files/tests/test_capi_characterization.py:805-854` |
| wl_collapse_decide_finalization_v1 | Sampled collapse/dependency/nested/agent guards preserve Invalid_Request=255 and the no-foreign-output behavior. Current relational cases correctly target the roster-clear route. They do not characterize ready-agent context joins or authorized metadata joins. | `S5/core/evaluation_finalization_c.adb:357-508`; `S5/core/worldline-collapse_wire.ads:71`; `S5/core/worldline-evaluation_authority.ads:23-38`; `S5/core/worldline-c_api.adb:331-342`; `files/tests/capi_characterization.json:313-323,942-965`; `files/tests/test_capi_characterization.py:862-911,979-991` |

**PK0-RC1:** every current mixed builder uses no agent, an all-zero Engine-origin agent, or an invalid agent. S5 forces a non-Agent origin back to Agent_Ready=0 at `S5/core/evaluation_finalization_c.adb:468-469`. Hence no mixed fixture reaches Agent_Ready=1, the primary/staged context rejections at lines 473-483 are omitted, and the original authorized Kind-1 metadata joins at lines 491-502 are omitted. The R1 table stops at the agent check (`files/tests/capi_characterization.json:318`); mentioning later joins in R3's note at line 319 does not give their exact frontiers or controls. This fails the exercisable-guard/frontier requirement in `v3/DESIGN.md:2229,2231-2232,2237` and `v4/DESIGN.md:554,577,626`.

No sampled fixed expectation changes a required successful return 0 into 255, treats a source-defined H outcome as an accepted refusal, repairs away C-15/C-16's original behavior, or deletes an original fixture. This is a sampled source conclusion, not exhaustive full-domain assurance. PK0-RC3 separately addresses the possibility that the harness could mistake an unexpected protected-memory failure for an expected 255.

## 4. Placeholders and recording

**Finding: current placeholders fail closed; the literal output-only recording requirement is violated.**

The placeholder audit finds only the declared run-dependent values: every layout/ctypes/header value, U14d_R3_classify_op2_record's written output, U15f_R3_capture_op2_record's written output, U15f_R3_seal_op3_record's written output, and D06_failure_latch's first/final stop results and fd 2 lines. All three written-result placeholders occur in unguarded cases, so the guard-only early return cannot bypass them. Written-result return code 0 remains required. Evidence: `files/tests/capi_characterization.json:332,796,901-902`; `files/tests/test_capi_characterization.py:999-1006,1095-1136`.

C-13 explicitly fails each placeholder (`files/tests/test_capi_layout_identity.py:173-200`). D06 accumulates pending values and fails after checking its fixed returns and latch relation (`files/tests/test_capi_diagnostics.py:135-164`). Nothing skips them or automatically installs observations. The record modes print observations rather than rewriting either JSON fixture (`files/tests/test_capi_characterization.py:1178-1203`; `files/tests/test_capi_diagnostics.py:188-205`; `files/tests/test_capi_layout_identity.py:213-231`).

**PK0-RC2:** layout record_main calls header_layouts at line 222. That function creates a TemporaryDirectory, writes probe.c and invokes a compiler that writes probe (`files/tests/test_capi_layout_identity.py:112-132`). Thus the stronger “--record writes no file” claim in `packet.json:47`, `AUTHOR-NOTES.md:124`, `files/tests/capi_layout_baseline.json:5` and `files/tests/test_capi_layout_identity.py:14-15` is false. Normal header measurement scratch is a separate allowed operation under an admitted frame; that does not make this record path output-only. Split that measurement and consume bound results read-only. Top-level bytecode creation must also be suppressed by the actual reviewed launch before imports.

No run values were supplied or recorded during this review. Any future disagreement is a finding requiring review; it is not permission to weaken an expectation, accept a native failure, or erase an original defect.

## 5. Static test mechanics and author uncertainties

**Finding: core placement/comparison mechanics are credible as source, with required fault/diagnostic repairs and corrected execution claims.**

**Placement and comparison.** Each object receives its own page group. The mapping is filled with 0xA5; only the readable initialized prefix is copied before protection. “end” places a record immediately before PROT_NONE; “prefix” places element k's end at that boundary; “unreadable” protects the whole declared object. Unknown objects, non-array prefix placement, excessive prefixes and incompatible alignment fail placement. Evidence: `files/tests/capi_guard_pages.py:152-203,206-239`. The fixed fixtures use valid prefix placements; this is not a universal placement proof.

For ordinary cases the helper snapshots all readable mapping ranges, compares every readable byte outside the union of output windows, and reports any changes. A no-write window compares raw bytes, including padding; a written record compares all typed fields, while padding inside its permitted write window is not a specified typed value. C-05 deliberately checks normal exit and the expected code only, as required by v4 R14. Evidence: `files/tests/capi_guard_pages.py:242-295`; `files/tests/test_capi_characterization.py:1009-1016,1078-1084,1095-1136`; `v4/DESIGN.md:622,626`. This covers readable bytes in the owned mapping, not unrelated heap, globals or the full address space. Final snapshots do not observe temporal write order, completed partial H writes or every byte read within a frontier; those limits do not close native construction or full-body proof.

**Forks and faults.** Decision calls and their relational oracle run inside run_forked. Python child errors produce a nonzero exit, and OS-signaled/nonzero exits fail before the report can be used as a passing result. The parent drains the report pipe before waitpid, then checks status before trusting its contents; the docstring's literal “only then reads” chronology is inaccurate. Evidence: `files/tests/capi_guard_pages.py:299-351`; `files/tests/test_capi_characterization.py:1059-1109`.

**PK0-RC3:** the helper does not establish a fatal SIGSEGV/SIGBUS policy after loading the native runtime. Checking normal exit plus expected 255 alone cannot exclude a protected over-read converted by that runtime into a handled exception returning 255. S5 has such handler mappings (`S5/core/evaluation_completion_c.adb:526-527`; `S5/core/evaluation_finalization_c.adb:505-508`) and an auto-initialized standalone library (`S5/core/worldline_core.gpr:81-82`). This is an unenforced distinction, not an observed runtime fault conversion. Enforce the harness's fault-fails rule and validate it through a harness-only negative control when a frame is admitted. Do not add a WORLDLINE class-X return/write expectation or infer D-23 closure.

**D06 and exact diagnostics.** Fresh interpreters isolate diagnostic active/failed state. Replacing Python sys.stderr with /dev/null does not replace native fd 2; subprocess capture retains fd 2. D06 duplicates fd 2, redirects it to /dev/full and restores it in that child alone; it changes no host descriptor or device configuration. Its failed-write/latch consequences remain runtime-dependent placeholders. Evidence: `files/tests/test_capi_diagnostics.py:57-116`; `files/tests/capi_characterization.json:332`; `S5/core/evaluation_completion_c.adb:39-88`.

**PK0-RC4:** observed() decodes fd 2 with UTF-8 “replace” and record_main saves only the resulting lines (`files/tests/test_capi_diagnostics.py:119-124,188-198`). That transformation loses invalid bytes. Preserve the raw stream and use byte equality or strict decoding; explicitly retain line order, empty lines and terminators. A lossy D06 baseline cannot establish the promised exact diagnostic sequence.

**ctypes and native boundaries.** The 82 named ctypes classes resolve by static AST inspection, and the 72 header field-name rosters agree lexically with their referenced ctypes field rosters. This measures no size, alignment, offsets, native semantics or C compiler behavior. Core's constructor validates only its own _LAYOUTS (`S5/runtime/worldline/core.py:171-173,317-335,402-425`). Pending, completion, finalization and recovery check their component layouts in their separate constructors (`S5/runtime/worldline/pending_kernel.py:85-108`; `S5/runtime/worldline/completion_kernel.py:115-136`; `S5/runtime/worldline/finalization_kernel.py:81-101`; `S5/runtime/worldline/recovery_authority_kernel.py:97-115`). Importing their classes at `files/tests/test_capi_characterization.py:44-59` does not invoke those constructors. Therefore `AUTHOR-NOTES.md:145` and `files/tests/test_capi_layout_identity.py:21-22` overstate automatic layout agreement. C-13 correctly records each original spelling separately; any measured mismatch remains an original defect, not permission to repair the record or reject an originally accepted domain silently.

**PK0-RC5:** “every native call” and hang containment are also too broad. Core initialization executes native queries in the parent; scalar layout/version tests and layout recording do so directly (`files/tests/test_capi_characterization.py:1090-1093`; `files/tests/test_capi_layout_identity.py:82-86,144-158,213-222`). Importing the helper loads libc at `files/tests/capi_guard_pages.py:39-42`, contrary to the “JSON and nothing else” author claim (`AUTHOR-NOTES.md:27`). select, waitpid, diagnostic subprocesses and header compile/probe subprocesses have no deadlines (`files/tests/capi_guard_pages.py:299-339`; `files/tests/test_capi_diagnostics.py:115-116`; `files/tests/test_capi_layout_identity.py:131-132`). A hang does not pass but does block the current parent. Correct the statements and establish actual reviewed launch supervision before baseline execution; an arbitrary semantic domain/time cap is not a remedy.

The diagnostic subprocess explicitly disables bytecode writes. Top-level discovery/record imports do not; header TemporaryDirectory follows the launch's ambient temporary-directory selection. Anonymous mappings, pipe reports and D06's device writes are process-local, but the source alone does not prove that every scratch/cache write remains in the admitted scratch. Bind bytecode suppression and owned scratch in the actual launch; do not infer confinement from these fixtures. Evidence: `files/tests/test_capi_diagnostics.py:110-116`; `files/tests/test_capi_layout_identity.py:127-132`; `files/tests/test_capi_characterization.py:30-59`.

Author uncertainties adjudicated:

| Uncertainty | Source-review ruling |
|---|---|
| Unproved bodies behind derived expectations | Acceptable as explicit unrun predictions that fail on disagreement. They establish no proof/native result and cannot justify rewriting required success into failure. `AUTHOR-NOTES.md:141-144`; `S5/core/evaluation_epoch.ads:13-22`. |
| Finite U32 probe domains | Acceptable as declared finite characterization, retaining the original API domain. Complete U8 enumeration and finite U32 edge probes do not supply full-U32 proof. `AUTHOR-NOTES.md:155`; `files/tests/test_capi_layout_identity.py:52-79`. |
| No timeouts / inherited fork locks | A hang remains failure/unknown, never a pass. The hang-containment claim needs correction, and bounded execution supervision must be concretely established by the admitted launch before baseline. `AUTHOR-NOTES.md:156-158`; `files/tests/capi_guard_pages.py:299-339`. |
| Header probe without -Werror | Acceptable only as separately labeled measurement with compiler warnings retained. It does not waive the original strict test or warning obligations. The original `S5/tests/test_abi_layout.py:103-125` still uses -Werror; no existing test is edited. `AUTHOR-NOTES.md:159`; `files/tests/test_capi_layout_identity.py:17-19,131`. |
| Layout/overflow/alignment assumptions | ABI measurements remain OPEN; source declarations and finite fixtures are not native correspondence. Correct the overly broad automatic-check claim under RC5; retain independent spellings and the original domains. `AUTHOR-NOTES.md:145-149`. |
| Relational C-11 oracle | Acceptable for the current explicitly limited roster-clear route, with original independent collapse tests retained. It co-moves with CW.Decide_Wire and cannot replace RC1's ready/authorized positive and refusal cases. `AUTHOR-NOTES.md:154`; `files/tests/test_capi_characterization.py:979-994`. |
| C-03 representative helper operands | An explicit finite granularity limit supplies no universal guard proof. It cannot excuse the reachable mixed guards missing under RC1. `AUTHOR-NOTES.md:150-153`; `files/tests/capi_characterization.json:318-323`. |
| D06 GNAT/libc failed-write behavior | Correctly left unrecorded. Baseline must retain exact bytes, returns and actual process status after RC4. `AUTHOR-NOTES.md:160`; `files/tests/capi_characterization.json:332`. |
| Author did not read B6 site tables | Recorded as an author uncertainty, not acceptance evidence. Source-derived selected sequences do not cover the mixed sites omitted by RC1. `AUTHOR-NOTES.md:161`; `S5/core/evaluation_finalization_c.adb:473-502`. |

## 6. Other weakening, assumptions and fixed obligations

**Finding: no protected policy/proof/source delta is supplied, but this packet cannot close the original obligations.** The additive fixtures retain the original domains and the original typed behavior in the sampled cases. They do not lower contracts, reduce proof floors, append exemptions, remove deterministic controls or turn C-14 into a baseline condition. Existing strict tests remain byte-identical. Their finite scope is a test scope, never a replacement for original accepted cases or full bodies.

The original completion standard remains fixed: full intended contracts and relevant bodies, authentic runtime producers, faithful callers, genuine accepted computations, strict warnings, original proof scope and complete original/additive controls. Evidence: `W/outputs/claude-phase1-handoff-20261004/HANDOFF.md:25-29,151-167,173-177`; `/home/sicarii/Documents/complete-phase1-prompt.txt:30-34,60-68`. This task's passive source-only boundary supersedes operational handoff instructions: no baseline launch, source overlay, compiler/prover action, reservation, storage operation or SIA note was performed.

Required changes preserve these obligations. RC1 expands missing coverage; RC2 repairs output-only recording; RC3 validates helper fault reporting without specifying class-X API behavior; RC4 preserves diagnostic bytes; RC5 corrects evidence ceilings and makes actual launch properties reviewable. None permits accepted computations to be reclassified as refusals, arbitrary input caps, assumption-based native correctness or proof-scope reduction.

## Required changes

### PK0-RC1

**Change:** Complete the mixed-entry characterization and C-03/C-05/C-06/C-11 coverage for the original ready/authorized paths: build faithful ready primary and staged Kind 1/2 inputs and a genuinely admitted Agent-origin record, exercise each reachable primary/staged context and metadata join rejection plus original successful joins, and record their precise nested read frontiers. Retain the current zero-roster relational cases and every original fixture.

**Reason:** The mixed R1 table stops at the agent-record check and the entire mixed fixture family cannot reach Agent_Ready = 1. Consequently the original context rejection guards and authorized Kind-1 metadata joins are not characterized or controlled. This fails the one-case-per-exercisable-guard and per-export-frontier requirements; a note about the joins is not coverage.

**Evidence:** `files/tests/capi_characterization.json:53,55-58,318-323,942-965`; `files/tests/test_capi_characterization.py:862-911,979-994`; `S5/core/evaluation_finalization_c.adb:468-502`; `v3/DESIGN.md:2229,2231-2232,2237`; `v4/DESIGN.md:577,620-626`.

### PK0-RC2

**Change:** Make every --record path output-only as requested. Split the compiled-header scratch measurement from layout --record and consume its independently bound measurements read-only; keep normal measurement artifacts confined to the admitted test scratch. Correct the packet and author claims accordingly, with reviewed changes and new hashes. Never add an automatic baseline/fixture writer.

**Reason:** Layout record_main calls header_layouts, which creates a TemporaryDirectory, writes probe.c and causes the compiler to create probe. There is no baseline JSON rewrite, but the stronger literal no-file-write record contract is not met.

**Evidence:** `files/tests/test_capi_layout_identity.py:13-19,112-132,213-226`; `packet.json:45-47`; `AUTHOR-NOTES.md:124`.

### PK0-RC3

**Change:** Enforce, in the guarded-call child after native-library initialization, that a protection fault is a failed case and cannot be converted to an expected handler/refusal code. Add a reviewed fatal-fault policy and a harness-only negative control for the protected-memory mechanism under that initialized runtime, retaining its abnormal status. This control must validate the helper's failure reporting without encoding any WORLDLINE class-X return/write expectation. Do not execute it before the confinement and capacity gates are satisfied.

**Reason:** The helper checks only process exit status and the returned code. It does not establish a SIGSEGV/SIGBUS policy. S5 handlers can return the same 255 expected by guarded refusal cases if a native runtime converts a protection fault to a handled exception. Thus normal exit plus 255 alone does not establish the promised fault-never-a-code rule. This is an unenforced distinction, not an observation that this unrun library performs such conversion.

**Evidence:** `files/tests/capi_guard_pages.py:7-12,237-263,314-351`; `files/tests/test_capi_characterization.py:1095-1115`; `files/tests/capi_characterization.json:40,55`; `S5/core/evaluation_completion_c.adb:526-527`; `S5/core/evaluation_finalization_c.adb:505-508`; `S5/core/worldline_core.gpr:81-82`; `v4/DESIGN.md:610,626`.

### PK0-RC4

**Change:** Preserve the captured fd 2 byte stream in diagnostic observations and --record output, and compare its exact bytes or decode strictly with failure on undecodable data. Retain line order, empty lines and terminators explicitly; never use replacement decoding to establish the D06 baseline.

**Reason:** observed() uses UTF-8 replacement decoding and record_main retains only those decoded lines. Distinct invalid byte streams can collapse to the same recorded replacement characters, so a reviewed D06 fixture derived from this output could later pass after native diagnostic bytes changed. The exact diagnostic control must retain the original bytes.

**Evidence:** `files/tests/test_capi_diagnostics.py:5-17,110-124,158-164,188-198`; `files/tests/capi_characterization.json:56,332`; `v3/DESIGN.md:2232`.

### PK0-RC5

**Change:** Correct the source and author statements about intrinsic isolation, imports and layout checking. State the actual boundary: guarded decision calls are forked; library initialization and scalar layout/version calls also occur in the parent; a hung child blocks the current reader; importing the helper loads libc; Core validates only its own _LAYOUTS, while the other component constructors are not invoked by these builders. Bind the future admitted launch to bytecode suppression, owned scratch and reviewed supervision of every native/compile/probe process. Establish these launch properties as evidence, not semantic assumptions, before the baseline.

**Reason:** Several assurances are stronger than the code. There is no timeout in select/waitpid or subprocess.run, parent native initialization/queries are outside run_forked, and merely importing component ctypes classes does not invoke their ABI-checking constructors. Only the diagnostic subprocess explicitly disables bytecode writes; the header scratch follows ambient temporary-directory selection. These facts cannot justify whole-suite hang/fault containment or automatic agreement of all ctypes layouts. Preserve the separate original layout spellings, including any measured defect.

**Evidence:** `files/tests/capi_guard_pages.py:7-12,39-42,299-339`; `files/tests/test_capi_characterization.py:21-26,43-59,1090-1093`; `files/tests/test_capi_layout_identity.py:21-22,127-132,144-158,213-222`; `files/tests/test_capi_diagnostics.py:110-116`; `AUTHOR-NOTES.md:27,145,156-159`; `S5/runtime/worldline/core.py:171-173,317-335,402-425`; `S5/runtime/worldline/pending_kernel.py:85-108`; `S5/runtime/worldline/finalization_kernel.py:81-101`; `S5/runtime/worldline/completion_kernel.py:115-136`; `S5/runtime/worldline/recovery_authority_kernel.py:97-115`.

## OPEN obligations

- Repair and independently re-review the packet source with new identities before baseline execution.
- Confinement frame v5 is UNQUALIFIED; V5-B01 and V5-B02, and the capacity gate, remain blockers as stated by the user and packet, not independently qualified by this source review.
- Admitted L0 baseline and reviewed recording of every placeholder remain OPEN.
- Class-H failure location/copy atomicity and native write construction/possible-outcome preservation (design §9.6.4 a-d) remain OPEN.
- Actual native runtime/library/compiler/ABI identities, warnings, raw streams, waits, guard-fault mechanism and supervised process lifetimes remain unmeasured.
- Full original contracts, bodies, references, producers/callers, proof scope, successful cases and fault controls remain required. PK-0 supplies no proof, source, control or Phase acceptance.
- Exact source/library/tool/header/runtime selection and preservation of compiler diagnostics and raw diagnostic bytes must be bound by the admitted baseline frame.
- The packet's C-05 controls provide finite frontier over-read checks, not proof that each frontier byte was read, universal pointer validity or native fault/ABI/cost correspondence.
- Original strict warning/proof settings and complete original ordered ordinary/additive controls must be retained; no prior pass or source endorsement transfers to a changed packet.

The required changes need a new, independently reviewed source identity. This verdict supplies no authority to execute the packet before admission, and no acceptance transfers to a changed packet.

## Review artifacts and sealing

`checkpoint-1.json` through `checkpoint-6.json` were created after their respective items, create-only, fsynced, mode 0600. The item-6 clarification restricts RC3's negative control to helper infrastructure. `checks.json` retains passive identity observations, static audits, sampled source comparisons, the independent JACKAL response and these checkpoints' digests. `review.json` binds this report and checks; `review-freeze.json` is written last and binds exactly REVIEW.md, review.json and checks.json. All acceptance/evidence fields are false.
