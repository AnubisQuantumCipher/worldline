# Root-worker runtime lane: seam design v5

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent, author role) |
| Date | 2026-10-05 |
| Status | **DRAFT_FOR_GPT61_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author reviews, accepts and closes nothing; author checks are self-checks. Every original obligation (OB-001 … OB-219), accepted case, deterministic fixture, control, contract, threshold, proof floor and scope remains **OPEN** and unchanged. |
| Supersedes | v4 `SEAM-DESIGN.md` (sha256 `f65629cb45e6e8a5ea798f5130a7f98e1d365758a7175343444f4022864efbda`, 233353 bytes, 1911 lines), v4 `seams.json` (`92a814a4883d3e01680dbfeae82cb7889b038930bc4e21bcaefd39b622a2a86c`), v4 `jackal.json` (`4d556a457caa268c80b5d7ef4edae949433034ffeb950a5b4d2f8a29fcafcfab`) and v4 `AUTHOR-NOTES.md` (`0bd92ccd556e39a358a5e93db5a57fe55ba206080d7b6dc1f033508d7f9c66e4`). All were read only and re-hashed unchanged; the first two equal the review's `design_sha256` and `seams_sha256`. |
| Answers | The sealed actual gpt-6.1-sol review of v4 in `WT/designs/claude-root-worker-seam-design-v4/review/gpt61-v1/`: `REVIEW.md` `340a62191e9f0c4135dc94a0282c033a64c3a55ac1884778fd0f8836c3fc95d4` (87144 bytes), `review.json` `d857f8ddd04f430097099f62688fb3f848d687c2f171f556db68ddefb16ba714` (145637), `checks.json` `58e3312e3ff655f438b32524a8a0034d0fac1b55815af20fd7207cb3e754529f` (154173), `review-freeze.json` `eef0ff2ca7816ddb79749f8cbddee7c3caa2c5f005dcace6dd3965462d010ee4` (561). The freeze names actual model `gpt-6.1-sol`, `different_from_author` true, and lists the first three files with exactly these hashes and sizes (recomputed, equal). Verdict **ENDORSED_WITH_REQUIRED_CHANGES**: V3-REQ-A … V3-REQ-L and RQ-1 PARTIALLY_CLOSED; clauses 28 CLOSED_AT_DESIGN_LEVEL, 29 PARTIALLY_CLOSED and 2 NOT_CLOSED (04.1, 07.3); D-2b CLOSED_AT_DESIGN_LEVEL and every other ruling PARTIALLY_CLOSED; NF4-1 … NF4-13 assessed; required changes V4-REQ-A … V4-REQ-L. The seven `checkpoint-*.json` files in that directory are not in the freeze and were not used. |
| C-API status | Unchanged from v4 (v4 header, carried in substance): **CAPI5R** (`review.json` `800880d44bff4b234c82cc392a3008fd4d37139b0827d070120cf299370f403b`, `REVIEW.md` `73e82489706e03ca465e7dea2aed1823df0b50a8ce1c5ab0555c545579dc34d8`, `checks.json` `c1398253713aa6d42ed11fda5194502ccae5a64825b36ef8100206f7d40719ef`, freeze `91bddf1a46763251940db658f5115cd13ab9de4aa67c0a41ae169de165649af1`) ENDORSED_WITH_REQUIRED_CHANGES with V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE; **CAPI6R** (`review.json` `bcfa259f8690c492b9284ef1ed9549efa7a5d3899edc1fbd5a0ae2ab7234d128`, `REVIEW.md` `12cfde3c3eed993b6056dc75d901710bdee1273e67cfe150a9648f99627da161`, `checks.json` `12642ce4501f12b0a608264d9bd93a23f39fd6c7d2c85cee69d94a91a3e2f284`, freeze `15fc9f07786eba0e0c1d3cde0250c8696e8ebeb96961ce6c22aeea2fcc590742`) of CAPI6 `DESIGN.md` `cfa0dca9e275e878b958f2f8da6b5cf54824534867773382965f2a887e98a417`: ENDORSED, those two and V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 CLOSED_AT_DESIGN_LEVEL only; ROOT_WORKER_INTEGRATION OPEN. All re-hashed unchanged. The PK-0 packet under revision in `WT/packets/capi-pk0/` was not read. |
| Scope | Design only, for the draft lane `W/work/protected-original-root-worker-repair-v1` (status `INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY`). The lane draft is someone else's unreviewed source and was not touched. v5 grants no execution, proof, build, test, review, operator or acceptance authority, and adds no approval gate. |
| Location | `WT/designs/claude-root-worker-seam-design-v5/` |
| **What this document consists of** | v5 is (1) the text of this file; (2) the v4 `SEAM-DESIGN.md` line ranges listed in §B.1 (slices C4-…), each bound by the sha256 of its exact bytes, with the quoted replacements R5-1 … R5-17 of §B.2 applied; (3) transitively, everything those v4 slices carry: v4 slice C4-B is v4's own §B, so the v3 slices it binds (C3-…) with R4-1 … R4-64, the v2 slices v3 binds (C2-…) with R3, and the v1 slices v2 binds, all as amended by R5, minus the withdrawals W5-1 and W5-2 of §B.3. Every other v4 text is superseded by the map of §B.3. |
| Companion files | `seams.json` (machine twin), `jackal.json` (JACKAL record), `AUTHOR-NOTES.md` (process record, uncertainties, OPEN items). Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools. Bash was used only for read-only inspection (AUTHOR-NOTES §2). |

Every statement about source is **static**: read from files, or reasoned from what was read. Nothing was compiled, run, imported, proved, tested or measured. Kernel, systemd, SQLite, interpreter and Ada-visibility statements marked **[unverified reasoning]** are the author's reading and name their evidence item.

---

## A. Closure tables

"Answer" is a design statement for the reviewer. The author closes nothing. Every proof, native, control, physical and acceptance obligation stays OPEN.

### A.1 Required changes V4-REQ-A … V4-REQ-L

Each change is quoted verbatim from the sealed `review.json` `required_changes[].change`.

| Id | Required change (verbatim) | v5 answer | Where |
|---|---|---|---|
| V4-REQ-A | "Complete every consumed typed native/producer/C-wire/export contract and its dependency edge in V4-A, including exact current observation, HMAC, requester, child and mutation operands. Keep V1 fallback additive and retain every original route/fixture/reference." | One wire convention, taken from the existing exports, and for every new or successor export its exact symbol family, every record with C type and Ada type per field, row arrays, results and refusal codes, its producer with the exact current observation it reads, the producer's pre and post, its callers and its dependency edges. The current-observation, HMAC, requester, child and mutation operands are given field by field. The V1 fallback adds nothing: no V1 route gains a refusal, and the lane's workload refusal is not part of it (V5-B.6). Every original export, route, fixture and reference is listed as kept. | V5-A |
| V4-REQ-B | "Make the carried witness forms and compaction union include every selected witness span, including N. Complete RQ-1's original-operation W0-W5 accepted/refusal, U/P recovery and exact-cost correspondence. Preserve exact serial guard/exception/dispatch boundaries while supplying the genuine workload dispatcher; treat the current root workload refusal as an OPEN containment gap." | The carried three-form text becomes four forms with (b′), and the compaction union takes every original span and every selected form-(b′) span (R5-1 … R5-3, R5-12, R5-13). RQ-1 is answered per operation class and window, against what the original serial route does for the same operation, with its accepted and refusal outcome, U and P records, recovery and exact cost, and no equivalence is claimed where the root route adds a launch (V5-B.5). The serial guard, exception and dispatch boundaries stay exactly as the source has them. A genuine workload dispatcher replaces the original `systemd` client inside the worker for the root's own operation (V5-B.6). The lane's workload refusal is recorded as the OPEN containment gap CG-1, never as preserved behaviour. | V5-B |
| V4-REQ-C | "Retain the lexical sign needed for accepted signed zero; specify native Number_Canonical/Repr/rounding/archive extraction and full costs on the matched original domain. Bound the rollback statement and its control to recorded cross-reference coverage, including tolerated append windows. Keep selection/currentness/producer/confinement premises as OPEN obligations without excluding any originally required case." | `Number_Canonical` carries the lexical sign separately from the exact magnitude, so `-0.0` is accepted. Rounding, the shortest-digit `Repr` and its layout rules, archive extraction and costs are specified natively, with exact overflow and underflow exponent thresholds (JACKAL J5-1 … J5-4). The rollback statement and its control are bounded to the recorded cross-references, and the tolerated append window is a stated non-detection. P-A1 … P-A4 are OPEN obligations; v4's "out of scope" exclusions are withdrawn (R5-14). | V5-C; R5-14 |
| V4-REQ-D | "Supply a faithful accounting alternative and complete the original kind/grant/owner/amount/plan/cost/epoch/physical/native-cost comparison against AO-1 through AO-11. Keep G unselected until its handler enforcement gap is solved. Preserve immutable outer bounds, independent request grants, no double count and original response progress; D-4a cannot waive them." | Option H: handler and runner code run in a service-class coordinator that holds no request's reservation, which is where the original runs them (in the daemon), and every request's workload runs on the original per-request scoped launch, with only the manager call relayed. The full nine-aspect comparison of H and of G against AO-1 … AO-11. G stays unselected. Nothing is selected; D-4a waives nothing. | V5-D |
| V4-REQ-E | "Provide one consistent CHILD_READY/CHILD_ABORT commit protocol with native sub-helper agreement before an authorizing exclusive decision and before actor exec. Permit collector/current-owner terminal commits in their legal phases. Complete helper command material, exact ABI/source/native-cost and process FD/argv/env/cwd/privilege surfaces, preserving every original used handler facility under RC-6." | A non-authorizing `CHILD_CANDIDATE`, then the sub-helper's native agreement frame, then exactly one of `CHILD_READY` or `CHILD_ABORT`, then the exec release; no READY can precede the sub-helper's decision. Terminal events may be committed by the generation's current owner in its legal phase: worker, collector or reconciler. The v2 helper protocol is given frame by frame; the sub-helper's library ABI, source binding and native cost; and every process's FD, argv, env, cwd and privilege surface. | V5-E; R5-4, R5-6, R5-11 |
| V4-REQ-F | "Define the complete orthogonal root/request/descriptor Legal/Next/owner relation, reconcile r1/r3' and express r6 as the closure barrier. Reconcile R4-48's capture-failure ABANDON requirement with M8(a)'s handoff-window qualifier; preserve the original pre-handoff failure stop and define a legal pre-transfer handoff abort. Supply replay recovery for committed intents whose effects or responses are pending. For M8(c), establish the original current request/world/active-job/unit authorization, error and cancellation correspondence before permitting a front generation-root stop." | Three separate relations, root, request and descriptor, each with its own Legal, Next and owner function, joined only by named cross-conditions. r1′ admits the no-launch release; r6 becomes a check inside `CLOSED_WITNESS`'s Legal row. `HANDOFF_ABORT` is the legal pre-transfer abort, followed by the original failure stop; ABANDON stays the only route after `TRANSFER_SENT` (R5-8). A pending-intent replay table. v4's M8 (c) front generation-root stop is **withdrawn**: its original correspondence (the store's world resolution and active-job set, the runner's cancelled set, the original errors and response) can be established only by a process that holds store custody, so no front stop is permitted for it. `job.cancel` is served, by its original handler, by a reachable owner: the worker, reattached if its channel was lost (V5-L.3), or the front of g+1. | V5-F; R5-5, R5-8, R5-9, W5-1 |
| V4-REQ-G | "Complete the legal Never_Dispatched/Never_Launched release and original-use quarantine/recovery/return route without requiring CLOSED_WITNESS. Retain the corrected original outer barrier and seed reconstruction without HANDLER_TERMINAL. Specify all RT-21 through RT-27 recovery actions with authentic closure/current material, immutable first committed result and original fatal-versus-unresolved exception mapping." | `HANDOFF_ABORT (g, NEVER_DISPATCHED)` releases by the original `Release_Hold`, quarantines U by the original exception path, answers with the original error, and returns the front to FRONT_OWNED (g+1), all without CLOSED_WITNESS. The barrier (C4-VG23) and the seed are kept; the escrow precondition now admits `CUSTODY_RETURNED` (R5-15). RT-21 … RT-27 each name their authentic material, exact calls, result immutability and fatal or unresolved mapping. | V5-G; R5-15 |
| V4-REQ-H | "Make each front/worker/host crash row consistent with actual surviving descriptor custody. Specify any surviving custodian and its complete authority/source/FD/cost/reaper coverage, or mark unavailable pipe recovery irrecoverably UNKNOWN while retaining the original successful controls. Arm durably before enabling reads, fold open intervals across chunk records, and specify real kcmp operands. Preserve last-writer EOF and measure the added read copy's writer/backpressure effects." | No surviving custodian is designed. Every row where the only read end dies with a process is irrecoverably UNKNOWN (`OUTPUT_CUSTODY_LOST`), exactly as an original daemon crash loses its pipe; reattachment is claimed only where a live process still holds a read end. `ARMED` is fsynced before the reader is registered. An interval fold over ARMED, CHUNK and DISARMED records. kcmp only between two live descriptors, with exact operands. Last-writer EOF is kept, and the retained read copy's backpressure effect is a measurement (K-25) with a close-on-failure rule. | V5-H |
| V4-REQ-I | "Separate pre-ACK root admission from already-worker-owned request Transfer_Join/Relay_Join and Serving_Join. Complete every own/transferred/retained/historical per-gate operand/head/presence contract, preserving optional providers. Specify the authenticated RELAY frame and per-gate freshness, request/generation/operation/gate/head/response binding, native ABI/cost, legal fallback state and propagation of original re-read errors." | `Root_Admission_Join` authorizes `CUSTODY_ACK (g)` over the `TRANSFER_SENT (g)` head while the front still owns; the three request joins need WORKER_OWNED. A three-valued presence rule (Required, Optional, Absent) per operand and mode, so providers stay optional. A complete gate table for every mode. The RELAY frame is specified byte by byte with HMAC, sequence and nonce freshness, the full binding, the native ABI and cost, the fallback state, and the rule that an original `RequestPeer` re-read error is raised as itself at that gate. | V5-I |
| V4-REQ-J | "Make empty-chain genesis/head foreign-key and native-origin encoding coherent without disabling integrity checks. Compare canonical JSON to its decoded typed archive relation. Specify full lossless native quantity/state storage and fold/order/replay, including root generation keys and every new state field. Define the new plan path/digest and retained old loader context for closed-v1 migration, preserving exclusive create and all history." | The head row is typed ORIGIN or EVENT; an ORIGIN head has a NULL foreign key and the origin digest, and `foreign_keys=ON` stays. The genesis check is v1's own relation, row = `archive (decode (file))`, plus a native decode-and-compare. Every quantity is stored as its minimal little-endian magnitude BLOB, the native `Quantity` representation, with `typeof` checks; the complete DDL, fold, order and replay are given. Migration uses a new plan file at a new path naming new journal and genesis paths, with the v1 descriptor and plan retained and bound for a read-only v1 verifier. | V5-J; W5-2 |
| V4-REQ-K | "Define the effective joined owning-On-unit, qualifier scope/layout/tile and gate checkviews separately from byte-immutable CAPI base tables, using the reviewed enrolled RW roster. Make MQ-RW2 target a newly added census member or a concrete changed old-scope call/path, and add an unchanged-old-context positive with an already-listed selector. Keep every sealed CAPI6 invariant, old row, fixed protocol and no-RW-wfx/no-RW-exclusive-key rule." | Five checkviews (units, qualified scopes, layout, tile, gates), computed from the unchanged CAPI tables and appended RW tables; the owning-unit view uses `RW_SPARK_UNITS`, the reviewed enrolled roster. MQ-RW2a adds an RW routine whose simple name newly brings `Owner_Wire.Raw_Request` (S5 `core/worldline-c_api.adb:882`) into an old scope's census; MQ-RW2b changes an old-scope call. PX-RW3 adds an RW routine named `Decide`, already listed, and expects no problem. CAPI6's invariants are restated unchanged. | V5-K |
| V4-REQ-L | "Complete original status/cancel/owner/quarantine/non-mutating response progress for unreachable workers, missing closure and UNKNOWN, with the full RELAY/collection/executor/storage model. Show authentic events that make each added wait end and legal service/recovery actions without the circular need for an unavailable owner. Preserve original thread placement, short router locks and response semantics; qualify optional QUEUED event compatibility." | An authenticated reattach endpoint makes an alive worker reachable again after channel loss or a front restart. `CUSTODY_RETURNED` returns custody when the worker and its namespace init are provably gone, without waiting for closure evidence that may never come. Each added wait ends with a named kernel or journal event. Per request class, the serving process, waits and progress. Thread placement and short router locks are kept. QUEUED events are withdrawn, so no client sees anything new. | V5-L |

### A.2 RQ-1 and its windows

| Item | Review text (verbatim, `review.json` `rq1.remaining_gap` and `rq1_window_assessment.windows`) | v5 answer | Where |
|---|---|---|---|
| RQ-1 (PARTIALLY_CLOSED) | "The W0-W5 table preserves the three scoped Context_Changed sites and Retained_Join, but W2/W3/W5 equivalence is overclaimed. The root route inserts launch/currentness/physical waits before handlers that may not launch on the serial route, and restoring an unintegrated lane guard adds a root workload refusal. Exact per-operation original durable outcomes, recovery, accepted cases and costs are still required." | The equivalence claim is withdrawn. Operations are split by what the original serial route does: in-process operations, which never launch there, and workload operations, which launch on the original scoped route. Each class gets its own window table against its own original (V5-B.5). The root route's added launch is a stated difference with its cost, OPEN for acceptance, not an equivalence. | V5-B.5 |
| W0 | "Correct native stale-context refusal at Reserve; original no-row/no-hold mapping needs per-command producer correspondence." | The producer of Reserve's current packet is named per command | V5-B.5 |
| W1 | "Retained_Join, unchanged C1 and frame-local history are retained; current original gates and actual-cost proofs remain required." | Kept; costs listed as OPEN proof items | V5-B.5 |
| W2 | "Same native Launch_Intent refusal site, but adding launch to a previously in-process handler does not establish the same accepted operation, new quarantine/K4 cost or legal no-launch return." | For in-process operations W2 exists only on the root route and is listed as an added refusal point with its K4 cost. The legal no-launch return is `HANDOFF_ABORT (g, NEVER_DISPATCHED)` | V5-B.5, V5-G.1 |
| W3 | "Correct native Running refusal and no-GO uncertainty consequence. R4-48 requires ABANDON for a capture failure, whereas M8(a) limits that requirement to the handoff window; the carried ABANDON edge starts only at TRANSFER_SENT/ROSTER_EVIDENCE. Preserve the original pre-handoff failure stop and specify a legal pre-transfer handoff failure route. The inserted launch/currentness dependency still needs operation-specific original correspondence." | `HANDOFF_ABORT (g, DISPATCHED)` before `TRANSFER_SENT`, then the original failure stop; ABANDON only after `TRANSFER_SENT` (R5-8) | V5-B.5, V5-F.2 |
| W4 | "The three Context_Changed guards cease after Running; this is not a claim that every subsequent original/current gate disappears or that added custody/costs are absent." | Restated with the remaining gates and the added custody costs | V5-B.5 |
| W5 | "A head-only change is not Context_Changed for those guards. Native Current_Valid, operation/canonical and physical gates still apply. 'normal/none' and all-window durable/cost equality overstate what the table proves." | "normal/none" withdrawn; the remaining gates are listed per window | V5-B.5 |

### A.3 V3-REQ-A … V3-REQ-L, V2-REQ and inherited RC items

Each V3-REQ is PARTIALLY_CLOSED. Its remaining gap is in `review.json` `required_change_detail` and is answered by the V4-REQ with the same letter (A.1). The review's `inherited_required_change_closure` keeps V2-REQ-A … V2-REQ-L PARTIALLY_CLOSED, and `inherited_rc_closure` keeps RC-05 and RC-10 CLOSED_AT_DESIGN_LEVEL and every other inherited RC PARTIALLY_CLOSED. Each is answered through the same-letter chain (v4 §A.3, v3 §A.1).

| Id | Remaining gap (verbatim) | Answered by |
|---|---|---|
| V3-REQ-A | "The specification waves repair the S1/S6 edge and include HMAC/request/child nodes. Most consumer rows still use schematic ABI/export and producer descriptions rather than complete typed consumed interfaces; V1 fallback also inherits a newly imposed root workload guard." | V4-REQ-A (V5-A; V5-B.6) |
| V3-REQ-B | "W2/W8 are frame-local, positional/compaction Rebase are distinguished and the C1 shortcut is removed. Compaction must retain the newly selected witness subspan as well as original packet spans, and the carried three-form text must agree. RQ-1 does not establish original operation-by-operation acceptance or cost equivalence." | V4-REQ-B (V5-B) |
| V3-REQ-C | "P3 scope and non-claims now agree. The exact-rational Decimal_Value intermediate has no explicit lexical-sign channel for accepted negative zero, and Repr remains an external CPython definition. Authentic selection/currentness is still an open premise; compromise exclusions and rollback-detection overstatement cannot discharge the original target." | V4-REQ-C (V5-C) |
| V3-REQ-D | "AO-1..AO-11 and unselected G improve the comparison and correctly reject F. The matrix admits that no option satisfies all obligations; qualitative cost labels and ledger checkmarks do not complete kind/amount/rollover/physical/native-cost correspondence. D-4a cannot authorize a weaker target." | V4-REQ-D (V5-D) |
| V3-REQ-E | "Launch ordering, measurement relay and native sub-helper redecision improve the design. READY followed by a disagreement ABORT violates the exclusive pair. The blanket worker-owned condition excludes collector finalization, and complete command material, C ABI and authority-preserving surfaces remain unfinished." | V4-REQ-E (V5-E) |
| V3-REQ-F | "Subject-kind replay and mutation choke points improve the proposal. The carried root graph still mixes request/drain and root transitions, root r1 excludes the newly permitted prelaunch release, r6 is written as an invariant instead of a barrier check, and M8(c) lacks an original job/unit authorization correspondence. The DDL cannot encode all new native fields/modes/quantities as specified." | V4-REQ-F, V4-REQ-J (V5-F, V5-J) |
| V3-REQ-G | "The inactive-unit condition is removed and the handoff seed no longer requires HANDLER_TERMINAL. Never_Launched release is permitted in r3 but no coherent root-product release/return route is supplied. Complete restart recovery still depends on descriptor/escrow survival and serving authority not supplied by the tables." | V4-REQ-G (V5-G) |
| V3-REQ-H | "Armed intervals detect uncertainty and duplicate writers are distinguished. Reattachment enables a reader before ARMED, READ interval detection is underspecified after chunk records, and front-crash/restart rows claim recovery of process-local pipe copies. Durable P/W cannot recreate an absent pipe or its consumed bytes." | V4-REQ-H (V5-H) |
| V3-REQ-I | "Request Transfer_Join no longer requires its future intake and PID/user namespaces are separated. RELAY framing, per-gate response/request/generation binding and costs are unspecified, optional presence is internally inconsistent, the root ACK path is conflated with already-worker-owned request joins, and all own/historical gate modes are not supplied." | V4-REQ-I (V5-I) |
| V3-REQ-J | "Tool keys, provisioner paths and explicit migration alternatives are supplied. Empty-genesis head references an absent events row under the retained foreign-key setting, genesis raw bytes versus archive representation are conflated, new State fields have no exact DDL/fold encoding, and plan-v1 migration needs an explicit changed-path/exclusive-create mapping." | V4-REQ-J (V5-J) |
| V3-REQ-K | "Define an explicit effective joined checkview for the owning On-unit roster, qualified scope attribution and appended layout/tile sets while retaining every CAPI base-table byte. CAPI5's carried qualifier check tests each routine prefix for membership in CAPI_SPARK_UNITS, and V4 adds RW_ROUTINE_NAMES but supplies no explicit corresponding effective owning-unit map; derive it from a reviewed enrolled RW unit roster, not from the candidate name alone. Repair MQ-RW2's stimulus/expected relation without narrowing any existing qualified/gate rule or C-API row." | V4-REQ-K (V5-K). The review's `closure_amendment` (V3-REQ-K PARTIALLY_CLOSED, superseding a preliminary checkpoint assessment) is carried. |
| V3-REQ-L | "The dedicated lane is withdrawn and router waits leave the lock. The progress table lists new custody/UNKNOWN/collection waits but does not show original accepted response progress when the owner or its physical evidence never becomes available. M8(c) is not a proved substitute; RELAY and executor/storage dependencies remain incomplete." | V4-REQ-L (V5-L) |

### A.4 Clauses NOT_CLOSED or PARTIALLY_CLOSED

The remaining gap is quoted from `review.json` `clause_detail[].remaining_gap`.

| Clause (status) | Remaining gap (verbatim) | v5 answer | Where |
|---|---|---|---|
| 01.1 (PARTIALLY_CLOSED) | "Typed interfaces are schematic; graph order repaired, caller/ABI contracts incomplete." | Complete per-export records, producers, callers and edges | V5-A.2 … V5-A.6 |
| 01.2 (PARTIALLY_CLOSED) | "Rebase variants remove the positional contradiction, but compaction needs a precise union including witness N and a consistent form roster." | Four forms everywhere; the compaction union includes every form-(b′) span | R5-1 … R5-3, R5-12, R5-13; V5-B.1 |
| 01.3 (PARTIALLY_CLOSED) | "Frame-local W2/W8 and unconditional positive-factor intent repair the old contradictions; saturated compaction/witness coverage and consistent carried forms remain incomplete." | The S-b union and residual R3 count the N span; forms consistent | R5-2, R5-3; V5-B.1 |
| 01.5 (PARTIALLY_CLOSED) | "Extra-conjunct and R0 audits are explicit and all originals remain, but D_prod coverage and saturated witness specification remain open." | Saturated witness specified; D_prod coverage (CV-B′, CV-R) stays OPEN as an obligation | V5-B.1, V5-B.4 |
| 01.7 (PARTIALLY_CLOSED) | "The W0-W5 table preserves the three scoped Context_Changed sites and Retained_Join, but W2/W3/W5 equivalence is overclaimed. The root route inserts launch/currentness/physical waits before handlers that may not launch on the serial route, and restoring an unintegrated lane guard adds a root workload refusal. Exact per-operation original durable outcomes, recovery, accepted cases and costs are still required." | Per operation class, against its own original | V5-B.5, V5-B.6 |
| 02.1 (PARTIALLY_CLOSED) | "Native canonicality is proposed, but signed zero and fully specified binary64/Repr/extraction correspondence remain unresolved." | Sign channel; native rounding and Repr; extraction | V5-C.3 |
| 02.2 (PARTIALLY_CLOSED) | "Independent selection and currentness remain premises; cross-references only constrain referenced prefixes and cannot justify the full detection claim." | Premises OPEN without exclusions; detection bounded to referenced prefixes | R5-14; V5-C.2 |
| 02.3 (PARTIALLY_CLOSED) | "Typed decoding/caller table improves the crosswalk; full consumed operands and authentic producer/ABI/native-cost contracts remain incomplete." | Crosswalk export records and costs | V5-A.3 (X-3) |
| 02.4 (PARTIALLY_CLOSED) | "Sampling stays separate from protection; no option meets enforcement/capacity/native-cost target." | Option H and the full comparison | V5-D |
| 03.2 (PARTIALLY_CLOSED) | "Helper redecision and launch order repaired; exclusive child decisions, collector completion, exact payload/C ABI and retained authority correspondence remain incomplete." | Candidate, agreement, exclusive decision; terminal committers; frames and ABI | V5-E |
| 03.3 (PARTIALLY_CLOSED) | "V1/V2 separation remains, but root-route refusal and schematic compatibility interfaces leave end-to-end accepted cases open." | No V1 fallback refusal; CG-1 recorded OPEN; dispatcher | V5-A.5, V5-B.6 |
| 04.1 (NOT_CLOSED) | "No complete consistent product: r1/release, r6, request-versus-root transitions, M8(c), State/DDL and predicate inputs conflict or are missing." | Orthogonal relations; r1′; r6 as barrier check; M8(c) correspondence; DDL | V5-F, V5-J.2 |
| 04.3 (PARTIALLY_CLOSED) | "Replay includes subject_kind; CAS/exclusivity intent preserved. Exact State/DDL/fold, transition ownership and replay-authorized recovery actions remain incomplete." | Owner functions; fold; pending-intent replay | V5-F.4, V5-F.6, V5-F.7, V5-J.3 |
| 04.4 (PARTIALLY_CLOSED) | "Durable seed and added routes improve recovery; process-local descriptor loss and legal post-crash serving/side-effect replay remain unresolved." | Irrecoverable UNKNOWN for lost pipes; pending-intent replay; CUSTODY_RETURNED | V5-H.4, V5-F.7, V5-G.4 |
| 06.2 (PARTIALLY_CLOSED) | "No option satisfies all AO obligations; actual costs and per-kind enforcement remain incomplete." | Option H against AO-1 … AO-11 | V5-D |
| 06.3 (PARTIALLY_CLOSED) | "UNKNOWN holds remain but job.cancel-root-stop mapping and owner diagnosis progress are incomplete." | v4's M8 (c) withdrawn; `job.cancel` and owner diagnosis served by a reachable owner; reattach; custody return | V5-F.5, V5-L.2, V5-L.3 |
| 06.4 (PARTIALLY_CLOSED) | "Serialized lane withdrawn; fair executor isolation is a proposal and custody/evidence waits still obstruct accepted responses." | Every added wait ends at a named event | V5-L.2 |
| 07.1 (PARTIALLY_CLOSED) | "O/U mapping carried; C/P/request/descriptor and mutation relation remains inconsistent." | Separate relations and cross-conditions | V5-F.2, V5-F.3 |
| 07.3 (NOT_CLOSED) | "r3 and INV-C4 now permit Never_Launched release, but r1 still restricts pre-HELD root rows to RESERVED/LAUNCH_INTENT and the root graph supplies no no-launch settlement/return branch. The complete product still cannot admit the case." | r1′ admits RELEASED by r3′; `HANDOFF_ABORT (g, NEVER_DISPATCHED)` is the settlement and return branch | V5-F.2, V5-F.3, V5-G.1 |
| 08.1 (PARTIALLY_CLOSED) | "STOP_INTENT spooling is authorized; reattachment and front-crash custody survival remain incomplete." | Reattach only where a live read end survives; otherwise UNKNOWN | V5-H.3, V5-H.4 |
| 08.2 (PARTIALLY_CLOSED) | "Armed/duplicate rules improve accounting; restart FD survival, exact open-interval detection and write truncation/progress remain incomplete." | Interval fold; per-row FD survival; write progress | V5-H.1, V5-H.2, V5-H.4 |
| 08.3 (PARTIALLY_CLOSED) | "Clean-stop P/W durability specified, but reattach starts reading before ARMED and crash-gap detection needs a precise interval fold." | ARMED before the reader; fold | V5-H.1, V5-H.3 |
| 08.5 (PARTIALLY_CLOSED) | "A-G table covers intended windows but several front-restart rows require lost FDs and gate states; no complete reconstruction route." | Rows rewritten against surviving custody | V5-H.4 |
| 09.1 (PARTIALLY_CLOSED) | "Request-intake circularity removed and namespace semantics separated; root ACK and native join operands/presence/independent selection remain incomplete." | `Root_Admission_Join`; operand record with presence | V5-I.1, V5-I.2 |
| 09.2 (PARTIALLY_CLOSED) | "Receive/validate before request intake retained. RELAY supplies a direction, but exact authentication/framing and real queue progress remain open." | RELAY frame; reattach; progress | V5-I.5, V5-L |
| 09.3 (PARTIALLY_CLOSED) | "Per-gate table exists but own/RETAINED/HISTORICAL modes and root-before-ACK versus request-intake phases remain incomplete." | Complete gate table with phases | V5-I.4 |
| 09.5 (PARTIALLY_CLOSED) | "Providers remain optional in intent; optional-field presence rules conflict and RELAY/queue adds unresolved service dependencies." | Three-valued presence; service dependencies listed with their end events | V5-I.2, V5-L.2 |
| 11.1 (PARTIALLY_CLOSED) | "Spec waves now follow declared edges; full consumed interfaces and exact exports/body dependencies still schematic." | Per-export edges; graph | V5-A.6 |
| 12.1 (PARTIALLY_CLOSED) | "Selection union improves; initial FK/encoding and native State-to-DDL/migration contracts remain inconsistent." | Head typing; DDL; migration path | V5-J |
| 12.2 (PARTIALLY_CLOSED) | "Closure inactivity removed, seed and recover_committed routes restored; no-launch product and crash custody survival still incomplete." | No-launch branch; CUSTODY_RETURNED; UNKNOWN for lost pipes | V5-G, V5-H.4 |
| 12.4 (PARTIALLY_CLOSED) | "Original K4 and unresolved exception preserved in intent; unavailable-owner/UNKNOWN serving progress still incomplete." | Reattach; CUSTODY_RETURNED; Reconciler on evidence | V5-L.2 |

### A.5 PARTIALLY_CLOSED rulings

Owner and evidence are quoted verbatim from the sealed `review.json` `rulings` (unchanged since v1). "Remaining gap" is the review's `remaining_gap`, verbatim. Each ruling stays with its owner. v5 neither narrows nor adds to any of them.

| Ruling | Owner (verbatim) | Evidence required (verbatim) | Remaining gap (verbatim) | v5 answer |
|---|---|---|---|---|
| D-1a | Lead source designer; independent GPT-6.1 source/spec reviewer | Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls. | V4-A/B improve specification but typed interfaces, compaction witnesses and full original domain remain unfinished. | V5-A, V5-B |
| D-1b | Lead scoped model/caller designer; independent GPT-6.1 reviewer | Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof. | The W0-W5 table preserves the three scoped Context_Changed sites and Retained_Join, but W2/W3/W5 equivalence is overclaimed. The root route inserts launch/currentness/physical waits before handlers that may not launch on the serial route, and restoring an unintegrated lane guard adds a root workload refusal. Exact per-operation original durable outcomes, recovery, accepted cases and costs are still required. | V5-B.5, V5-B.6 |
| D-2a | Lead authors schema/callers; operator provisions or installs authoritative state | Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls. | Initial genesis FK/encoding, exact native-state storage and migration/reconstruction remain unfinished; provisioning/install stay operator-owned. | V5-J, V5-F.7; provisioning stays OP-1 |
| D-3a | Lead protocol designer; operator for lab execution | Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection. | Crash/restart pipe custody, reader-before-ARMED ordering and complete role-state reconstruction unresolved; physical lab evidence OPEN. | V5-H |
| D-4a | Lead prepares native accounting comparison; independent GPT-6.1 review; operator selects any authoritative resource-policy change | Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls. | No admissible accounting option selected; fixed costs/enforcement and accepted response progress unresolved. Operator cannot waive original guarantees. | V5-D (H, unselected), V5-L |
| D-5a | Lead prepares native/OS design; independent GPT-6.1 review; operator for delegation and privileged lab action | Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls. | Exhaustive inventory remains contingent on RC-6; retained capabilities/views/helper commands and original handler compatibility unestablished. | V5-A, V5-D, V5-E.2, V5-E.4 |
| D-5b | Lead helper designer; independent GPT-6.1 review; operator for privileged execution/installation | Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations. | Child decision alternatives, collector completion and native C-helper ABI/payload/cost remain unfinished; no privileged execution or installation authority granted. | V5-E |
| D-6a | Lead historical/canonical model designer; independent GPT-6.1 review | Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement. | Seed/outer semantics repaired, but no-launch product and crash-safe automatic/historical recovery remain incomplete. | V5-F, V5-G |
| D-7a | Lead native/provenance designer; child-authority and GPT-6.1 re-review; operator for any original API/owner-policy alteration | Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation. | P3 repaired and C-API integration specified, but signed-zero canonicality and authenticity/currentness/producer/native-cost remain unfinished. | V5-C, V5-K. No original API or owner policy is altered. |
| D-8a | Lead OS/native requester designer; independent GPT-6.1 review | Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage. | Request transfer join repaired, but root ACK phases, full gate modes/operands and RELAY protocol remain incomplete. | V5-I |
| D-8b | Lead prepares domain-preserving protocol; operator for kernel measurement; independent GPT-6.1 review | Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client. | Providers optional in intent; optional-field contracts, queue progress and all kernel measurements remain unresolved. | V5-H, V5-I, V5-L; measurements stay with the operator (OP-7, K-1 … K-27) |
| D-9a | Lead additive SPARK relation and caller designer; independent GPT-6.1 review; operator for fault campaign | Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes. | Complete legal product, serialization, crash custody and mutation/cancellation correspondence remain incomplete. | V5-F, V5-G, V5-H, V5-J. Fault campaigns stay operator work (OP-8). |

The review's ruling-to-repair mapping (D-1a → V4-REQ-A, V4-REQ-B; D-1b → V4-REQ-B; D-2a → V4-REQ-F, V4-REQ-J; D-3a → V4-REQ-H; D-4a → V4-REQ-D, V4-REQ-L; D-5a → V4-REQ-A, V4-REQ-D, V4-REQ-E; D-5b → V4-REQ-E; D-6a → V4-REQ-F, V4-REQ-G; D-7a → V4-REQ-C, V4-REQ-K; D-8a → V4-REQ-I; D-8b → V4-REQ-H, V4-REQ-I, V4-REQ-L; D-9a → V4-REQ-F, V4-REQ-G, V4-REQ-H, V4-REQ-J) is followed in the "v5 answer" column.

### A.6 Carried exactly as the review closed or assessed them

- **D-2b, CLOSED_AT_DESIGN_LEVEL.** Owner, verbatim: "Lead prepares concrete equivalence/adoption package; applicable operator authority; independent GPT-6.1 review". Evidence required, verbatim: "Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit." Carried unchanged by slice C2-116 (through C3-B inside C4-B). The frontier control stays byte-exact on its v1 domain, with no re-enrollment proposed; `frontier_sha256` `a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb` (the review's `carried_assessments`).
- **RC-05 and RC-10, CLOSED_AT_DESIGN_LEVEL**, carried by the same slices as in v4 (C2-17, C2-116, C2-12, inside C3-B inside C4-B).
- **The 28 CLOSED_AT_DESIGN_LEVEL clauses**, carried by the slices that hold the review's evidence: 01.4, 01.6, 03.1, 04.2, 04.5, 04.6, 05.1, 05.2, 05.3, 05.4, 05.5, 06.1, 07.2, 07.4, 07.5, 08.4, 08.6, 08.7, 09.4, 10.1, 10.2, 10.3, 10.4, 11.2, 11.3, 11.4, 12.3, 12.5. Where an R5 or a V5 section touches the evidence, it keeps the closed property:
  - **04.5** (newly closed): the original MainPID, helper-pidfd and launcher-wait test is carried unchanged in C4-VG23 and R4-30. `CUSTODY_RETURNED` (V5-F.2) does not stand in for CLOSED_OUTER or for any part of the barrier; it returns custody only, and the row stays held.
  - **04.2**: CUSTODY_ACK and ABANDON stay exclusive; `HANDOFF_ABORT` joins the same alternative set (R5-5), so exclusivity is only strengthened.
  - **08.4, 08.6**: VALIDATE still precedes INTAKE; the roster evidence (v3 V-H.2 H4, carried) is unchanged, and its kcmp operands are restated exactly in V5-H.3.
  - **09.4**: nothing is refused for correspondence; RELAY and the queue are kept, and RELAY's frame only adds authentication.
  - **12.3**: uncertain holds stay; no stop settles (R5-7, R5-8).
  - **01.4**: W1 … W10 still presuppose no equal decision; R5-1 … R5-3 change only span forms.
- **Assessments carried unchanged** (`carried_assessments`): NF-1 VERIFIED_STATIC_OPEN_FLAG_KERNEL_CONSEQUENCE_UNMEASURED; NF-2 VERIFIED_STATIC_CONTROL_FLOW_NOT_RUNTIME_COMMIT; NF-3 VERIFIED_STATIC_LOCK_PATH; NF-4 VERIFIED_STATIC_AUTOMATIC_RECOVERY_BRANCH; NF-5 VERIFIED_TEXT_AND_LEXICAL_SCOPE; NF-6 VERIFIED_STATIC_MANAGER_CALLS_REACHABILITY_UNMEASURED; NF-7 VERIFIED_STATIC_ROUTER_WAIT_AND_FRONT_GATE; NF-8 VERIFIED_STATIC_ENCODING_FORMS; NF-9 VERIFIED_BYTE_IDENTITY_AND_STATIC_RELAY_JOIN_KERNEL_VIEW_UNMEASURED; NF-10 VERIFIED_STATIC_PLAN_SELECTION_GAP; NF-11 VERIFIED_STATIC_GENESIS_AND_HMAC_BOUNDARY; N-1 VERIFIED_STATIC; N-2 SUPPORTED_STATIC_TOOL_BEHAVIOR_OPEN; N-3 VERIFIED_STATIC; N-4 VERIFIED_BYTE_DIFF_AND_LAYOUT; N-5 VERIFIED_LEXICAL_SCOPE; N-6 SUPPORTED_STATIC_CONDITIONAL_RECEIVER_RESOLVED; N-7 VERIFIED_STATIC; N-8 VERIFIED_STATIC_ORDER; N-9 VERIFIED_TEXT_SCOPE_RESOLUTION_OPEN; N-10 VERIFIED_STATIC_PAIR_FILLING; DF-1 VERIFIED_STATIC_RECOMPUTATION; DF-2 VERIFIED_STATIC; DF-3 VERIFIED_STATIC; DF-4 VERIFIED_STATIC; DF-5 VERIFIED_STATIC_ABSENCE_IN_SELECTED_TREES; DF-6 SUPPORTED_STATIC_CONDITIONAL. DF-3's serial guard and exception order is kept exactly in V5-B.5; NF4-2's consequence is answered there (CG-1).
- **Operator items** (`operator_items`): OP-1 … OP-6, OP-8 and OP-9 WITHIN_RESERVED_SCOPE; OP-7 WITHIN_RESERVED_SCOPE_RANGE_REPAIR_COMPLETED for K-1 … K-23. v5 adds measurement items K-24 … K-27 (V5-N). The reservation reads, verbatim, "D-8b: original and additive kernel measurements, now K-1 through K-23, in an authorized lab"; K-24 … K-27 are additive kernel measurements of the same kind, and R5-16 and R5-17 make the same range repair v4 made with R4-1 and R4-5, for the reviewer to assess. The reservation's owner and kind are unchanged. No operator item is added, lowered or widened, and no approval gate is added (`no_new_operator_gate` true).
- **Open obligations.** The review's `open_obligations` lists OB-001 … OB-219, every one OPEN with `closure_credited` false (observed: 219 entries). `original_obligation_registry` is `P1/OBLIGATIONS-v2.json` `1587e068fc2c31a562e38b459728a75dbf7e8d7d9f8afb8efa1474e2a702aeec`. `open_design_dependencies` are carried in V5-O.

### A.7 The review's assessments of NF4-1 … NF4-13

| Id | Status (verbatim) | The review's consequence, and v5's answer | Where |
|---|---|---|---|
| NF4-1 | VERIFIED_STATIC_CONDITIONAL | Exception order, the durable `DISPATCH_INTENT` boundary and original quarantine are preserved; a custody failure never makes quarantine impossible while the use is RESERVED | V5-B.5 |
| NF4-2 | VERIFIED_STATIC_ROUTING_CONSEQUENCE_QUALIFIED | Restoring the serial guard on the root route would refuse workload operations; v5 does not restore it there. The guard stays on the serial route as the lane has it, and is recorded as OPEN containment gap CG-1 | V5-B.6 |
| NF4-3 | VERIFIED_STATIC_RETAINED_SEED_NOT_RECOVERY_PROOF | The seed is an input, not a recovery proof; authentic current physical or custody-return evidence and legal settlement stay separate. v4's `:105-109` was `protected_root_observation.py` (corrected in V5-G.3) | V5-G.3, V5-G.4 |
| NF4-4 | VERIFIED_STATIC_FULL_PATH_MAPPING_SCOPE | NC-P3 exclusions stay explicit (C4-VC45) | — |
| NF4-5 | VERIFIED_STATIC_ABSENCE_IN_SELECTED_SOURCE | The empty-chain head is made consistent with the foreign key | V5-J.2, V5-J.3 |
| NF4-6 | VERIFIED_STATIC_RELATIVE_KEY_AND_PREFIX_LIMIT | Detection bounded to referenced prefixes | V5-C.2 |
| NF4-7 | VERIFIED_STATIC_TOOL_SELECTION | Unchanged (C4-VJ12) | — |
| NF4-8 | VERIFIED_STATIC_ORIGINAL_JOB_CANCEL | The source does not authorize a front generation-root stop; v4's M8 (c) is withdrawn, and `job.cancel` runs only in a store-custody owner | V5-F.5 |
| NF4-9 | VERIFIED_STATIC_EXPLICIT_HELPER_FD_FLOW_RUNTIME_COMPLETENESS_OPEN | Authenticated material, native decision, source, privilege and fixed event order for the relaying sub-helper; the READY-then-ABORT contradiction is removed | V5-E |
| NF4-10 | VERIFIED_STATIC_EXCEPTION_BOUNDARY | The startup refusal stays a refusal; no recovery reinterprets it as settlement | V5-G.4 |
| NF4-11 | VERIFIED_STATIC_STATUS_MUTATION | `status` keeps its mutating semantics and dependencies; the added waits each end at a named event | V5-L.2 |
| NF4-12 | VERIFIED_STATIC_SCOPED_LAUNCH_ORDER | The helper READY commit and native gates are the separate protocol of V5-E.1 | V5-E.1 |
| NF4-13 | VERIFIED_STATIC_DDL_KIND_OMISSION_REPAIR | The product transition, owner projection, native encoding and DDL-to-Next correspondence are given | V5-F.2, V5-F.4, V5-J.2, V5-J.3 |

### A.8 New author observations (static; for the reviewer to check; none is review)

| Id | Observation | Evidence (read) | Consequence | Where |
|---|---|---|---|---|
| NF5-1 | Every protected operation, mutating or not, goes through the principal's `invoke` when one exists (`rw/daemon.py:379-386`), and so through `_reserve` and an operation-journal append. The daemon also writes `store.retain_client_request` before every handler (`rw/daemon.py:342-348`), and holds `_mutation_lock` around mutating handlers only (`:354-359`). | Read | No request, not even a read, can be served while another process owns the store; serving progress needs a reachable owner | V5-L |
| NF5-2 | The original job runner launches agent work through `self.systemd.launch (instance_id, argv, description=…, nice=…, resource_properties=…)` and stops it through `self.systemd.stop (unit)` (`rw/runner.py:697-703`, `:471-483`; `rw/linux/systemd.py:156-170`, `:717`). | Read | The interface a genuine workload dispatcher must present | V5-B.6 |
| NF5-3 | The original scoped launch runs `systemd-run` itself from the daemon process, with `RemainAfterExit=yes`, `Delegate=no`, `User=root` and the plan's `systemd_properties`, and the V3 actor helper as the unit's command (`rw/protected_scoped_resource_runtime.py:739-769`). | Read | Option H relays exactly this command | V5-D |
| NF5-4 | The lane exports for the decisions this design consumes are the existing `wl_canonical_operation_*_v1`, `wl_canonical_exchange_*_v1`, `wl_canonical_owner_completion_*_v1`, `wl_resource_scoped_run_ledger_{version,layout,check,validate,classify}_v1`, `wl_resource_child_execution_{version,layout,decide}_v1` and `wl_resource_observation_*_v1` (a `grep` of `_lib.wl_…_v1` in `rw/`). No `wl_scoped_canonical_operation_*` export exists; v4 V4-A.2 called that ABI "`…_v1` / `…_v2`" as if a V1 one existed. Both its entries are new. | Observed (grep) | Corrected in V5-A.3 (X-9) | V5-A.3 |
| NF5-5 | The V1 helper's custody channel is a `SOCK_STREAM` socketpair with `SO_PASSCRED` on both ends (`protected-root/native_root_worker_supervisor_v1.c:325-328`); the actor credential channel is `SOCK_SEQPACKET` (`:324`). | Read | RELAY frames are length-prefixed on a byte stream | V5-I.5 |
| NF5-6 | `job.cancel` validates its argument, resolves the world with `store.world`, raises `NO_ACTIVE_JOB` on an empty `active_jobs_for_world`, and for each job adds it to the runner's cancelled set and stops its recorded unit (`rw/controller.py:811-826`; `rw/runner.py:471-483`). | Read | Each part needs the store or the runner of the custody owner, which is why v4's M8 (c) is withdrawn | V5-F.5 |
| NF5-7 | The store opens its database in WAL mode (`rw/store.py:281`). | Read | A store reader in another process would be a separate SQLite question; v5 never reads the store outside its custody owner | V5-L.2 |

---

## B. What v5 carries from v4, and how to read it

### B.1 Bound v4 slices

- v4 `SEAM-DESIGN.md` has 1911 lines and ends with a newline (observed). Its whole-file sha256 is `f65629cb45e6e8a5ea798f5130a7f98e1d365758a7175343444f4022864efbda`.
- Each slice's sha256 is that of the UTF-8 bytes of its lines, each followed by `\n`. A read-only script computed them (Appendix C).
- CARRIED_VERBATIM slices are part of v5 exactly. CARRIED_WITH_LINE_REPLACEMENTS slices are part of v5 with the listed lines replaced by the §B.2 text. Slice C4-B is v4's §B; it carries v3 by its own slice table (C3-…), so an R5 may also replace a v3 line inside a C3 slice, or a line of an R4 block's `v4:` text (RR5-4).

| Slice | v4 lines | sha256 | Disposition | Content |
|---|---|---|---|---|
| C4-B | 181-790 | `0d561bbf1c146e1148bcb7ef9e929172e97d7cae881740fdefa579acc0bf94ee` | CARRIED_WITH_LINE_REPLACEMENTS (R5-1 … R5-11, R5-16, R5-17), minus W5-1 and W5-2 | v4 §B: the C3 slice table, R4-1 … R4-64, v4's map and reading rules |
| C4-VB14 | 958-1009 | `c3d9379fa59e6fb72f66ee01468a58bdcaffa8713434b69068e4c29c44ca72f8` | CARRIED_WITH_LINE_REPLACEMENTS (R5-12, R5-13) | V4-B.1 … V4-B.4: witness laws, conjunct audit, residual classes, obligations |
| C4-VC1 | 1047-1067 | `1f5b43cdd64585f49bcddf88d368908fe9e2e0ff6a9aad90174c6a47fe46b822` | CARRIED_WITH_LINE_REPLACEMENTS (R5-14) | V4-C.1: the selection chain and its premises |
| C4-VC45 | 1106-1134 | `9f19804bb9b75eb501428e8fff4e7e891f32cfc457d8bf54d888460f55017e65` | CARRIED_VERBATIM | V4-C.4 P3; V4-C.5 crosswalk decode |
| C4-VD1 | 1142-1156 | `6e4246d52d91c24270d31877831daab0f38820d0915bec9a001b087af2280377` | CARRIED_VERBATIM | V4-D.1: obligations AO-1 … AO-11 |
| C4-VE4 | 1229-1259 | `ece2a2323cb7b4e63a1b01007c805fda0234028e432988ca387fd74b61d9800b` | CARRIED_VERBATIM | V4-E.4: retained authority of the coordinator |
| C4-VG23 | 1415-1439 | `f2fbbc45ded63474743e8ec24207a2accf266877ea04f45c53279f0147e11b5f` | CARRIED_WITH_LINE_REPLACEMENTS (R5-15) | V4-G.2 barrier; V4-G.3 seed |
| C4-VH2 | 1468-1472 | `2c05923289180e0ad4054947397e648a8b2be119f6df902051ecf47fae3bd528` | CARRIED_VERBATIM | V4-H.2: write-armed intervals |
| C4-VH56 | 1499-1512 | `dca343ce4f65e7ac25b881fe07d5ffded9426ad06ef3abf0869207d87727b41b` | CARRIED_VERBATIM | V4-H.5 writer duplicates and EOF; V4-H.6 gates, rosters, reapers |
| C4-VI3 | 1595-1598 | `a0a07f40cf293dd1c3e31ec1d8185100ff018d1d56f01f75b4b4e4b4aef4f887` | CARRIED_VERBATIM | V4-I.3: user versus PID namespace |
| C4-VJ12 | 1642-1660 | `a589df7a2c26e06659a40740041685581aba8bc0b519554bb38eeb81fb41dfca` | CARRIED_VERBATIM | V4-J.1 v1 exactly; V4-J.2 selection union |
| C4-VJ5 | 1694-1698 | `68807edb999cc78d85e3762c55ad968d0a9f8519d0827b2b81f09fc32a0ee6bf` | CARRIED_VERBATIM | V4-J.5: recovery mapping, plan version, frontier |
| C4-VK1 | 1706-1713 | `14b1ec87d217eb956fe8cdbaeceda65878a66c8b553099b7fb0b6b94a8ac7584` | CARRIED_VERBATIM | V4-K.1: sealed C-API status |
| C4-VMNOP | 1796-1852 | `ab7ac01e4595e4b430cfd8f64f8969a7e6248e1efcabe31bf8e882e13ebd89bb` | CARRIED_VERBATIM | V4-M controls, V4-N measurements, V4-O open list, V4-P non-claims |

### B.2 Line replacements

Each replacement quotes the exact v4, v3 or v2 line or lines, then gives the v5 text.

**R5-1 replaces v3 lines 825-832 (in C3-VB, carried by C4-B).** The carried form roster names (b′) (01.2, 01.3).
```text
v3:
Each witness field takes one of three forms:
1. **(a) A present zero-length span.**
   - Identity validity holds for length 0 anywhere (`core/resource_reservation_transition.ads:85-88`).
   - Two present zero-length identities are `Same` (`:93-100`).
   - A zero-length quantity has value 0 (little-endian magnitude, `core/resource_quantities.ads:12-17`, `:25-28`).
2. **(b) An alias of an original span.**
   - `Same` compares bytes (`core/resource_reservation_transition.ads:93-100`), and `Q.Value` reads content, so aliases preserve every relation.
3. **(c) Fresh bytes**, only where (a) and (b) cannot supply a value: text constants, or a positive numeral.
v5:
Each witness field takes one of four forms (v4 V4-B.1 with v5 R5-12):
1. **(a) A present zero-length span.**
   - Identity validity holds for length 0 anywhere (`core/resource_reservation_transition.ads:85-88`).
   - Two present zero-length identities are `Same` (`:93-100`).
   - A zero-length quantity has value 0 (little-endian magnitude, `core/resource_quantities.ads:12-17`, `:25-28`).
2. **(b) An alias of an original span.**
   - `Same` compares bytes (`core/resource_reservation_transition.ads:93-100`), and `Q.Value` reads content, so aliases preserve every relation.
3. **(b′) A one-byte sub-span of `Data` over a non-zero byte** (`Negative => False, First => p, Length => 1`), used only for N = D. It is a *selected witness span*: every construction's `Rebase` maps it, and the compaction union of V-B.6 case S-b contains it.
4. **(c) Fresh bytes**, only where (a), (b) and (b′) cannot supply a value: text constants, or a positive numeral.
```

**R5-2 replaces v3 line 876 (in C3-VB, carried by C4-B).** The compaction union includes N's span.
```text
v3:
| S-b: constants are needed and absent | **Compaction.** `Data2` is the maximal intervals of the union of every span the original packet references, in order, followed by the constants. `Rebase` maps each span to its compacted position. | Holds when the union's length plus the constants' length is at most `Byte_Count'Last`. |
v5:
| S-b: constants are needed and absent | **Compaction.** `Data2` is the maximal intervals of the union of every span the original packet references and every selected form-(b′) witness span, in order, followed by the constants. `Rebase` maps each of those spans to its compacted position. | Holds when the length of that union plus the constants' length is at most `Byte_Count'Last`. |
```

**R5-3 replaces v3 line 879 (in C3-VB, carried by C4-B).**
```text
v3:
- **Residual R3.** A Live or Reaped row is present, the constants are absent from `Data`, and the referenced union is longer than `Byte_Count'Last` minus the constants' length. Such an arena exceeds anything a producer can allocate. No claim is made about it. The original unit decides it, and its coverage stays OPEN (RQ-2).
v5:
- **Residual R3.** A Live or Reaped row is present, the constants are absent from `Data`, and the union of every referenced span and every selected form-(b′) span is longer than `Byte_Count'Last` minus the constants' length. Such an arena exceeds anything a producer can allocate. No claim is made about it. The original unit decides it, and its coverage stays OPEN (RQ-2).
```

**R5-4 replaces v3 line 1179 (in C3-VE, carried by C4-B).** E9 becomes the non-authorizing candidate stage with native sub-helper agreement (V4-REQ-E).
```text
v3:
| E9 | Worker | Build the actor observation and the process and namespace ancestry rosters | — | `Decide` / `Decide_V2` = `Child_Ready_Conjunction` (`core/worldline-resource_child_execution.ads:194-208`): K.Check, `Parent_Holds` (`:127-133`), `Child_Holds` (`:103-126`), `Process_Ancestry`, `Namespace_Ancestry` |
v5:
| E9 | Worker, then sub-helper | Build the actor observation and the process and namespace ancestry rosters and decide; journal the non-authorizing `CHILD_CANDIDATE(t)` with the material digest and the worker's decision; send `COMMIT_CHILD_REQUEST` with the complete material; the sub-helper binds and decides natively on the same material and answers `AGREE_CHILD` or `REFUSE_CHILD` (v5 V5-E.1, V5-E.3) | `CHILD_CANDIDATE(t)`, then `CHILD_AGREED(t)` or `CHILD_REFUSED(t)` with the sub-helper's frame | `Decide` / `Decide_V2` = `Child_Ready_Conjunction` (`core/worldline-resource_child_execution.ads:194-208`): K.Check, `Parent_Holds` (`:127-133`), `Child_Holds` (`:103-126`), `Process_Ancestry`, `Namespace_Ancestry`; in the worker, then in the sub-helper |
```

**R5-5 replaces v3 line 1242 (in C3-VF1, carried by C4-B).** The pre-transfer abort joins the exclusive set (V4-REQ-F).
```text
v3:
  - `ACK(g)` = {CUSTODY_ACK, ABANDON};
v5:
  - `ACK(g)` = {CUSTODY_ACK, ABANDON, HANDOFF_ABORT}. `HANDOFF_ABORT` is legal only before `TRANSFER_SENT (g)`; once any member commits, neither other can (v5 V5-F.2);
```

**R5-6 replaces v4 line 443 (in C4-B; R4-27's result, the helper command row).**
```text
v4:
| `COMMIT_CHILD` | E10 | v4 V4-E.3: the ticket of a measured child; byte equality of the relayed measurement frame; the helper-observed ancestry; and the sub-helper's own native `Decide` or `Decide_V2` = Ready on the bound material |
v5:
| `COMMIT_CHILD_REQUEST`, `COMMIT_CHILD_GO`, `ABORT_CHILD` | E9, E10 | v5 V5-E.3: the ticket of a measured child; byte equality of the relayed measurement frame; the helper-observed ancestry; the sub-helper's own native `Decide` or `Decide_V2` on the bound material, answered before any authorizing record exists; GO accepted only with the material digest the sub-helper agreed to and the id of the committed `CHILD_READY` |
```

**R5-7 replaces v4 line 480 (in C4-B; R4-31's result, RT-13).**
```text
v4:
| RT-13 | UNKNOWN; worker possibly alive | — | any | — | none | Wait. Never stop on EOF, a deadline or the reconciler's own initiative. An authorized `job.cancel`, or the owner's own original failure capture, stops per M8 (v4 V4-F.5). A stop never settles or releases, and every hold stays | Automatic retain |
v5:
| RT-13 | UNKNOWN; worker possibly alive | — | any | — | none | Wait for authentic evidence: the worker's reattachment (v5 V5-L.3), or the worker and namespace-init pidfds terminal (`CUSTODY_RETURNED`, v5 V5-F.2). Never stop on EOF, a deadline or the reconciler's own initiative. Only the custody owner's own original failure capture, or its original `job.cancel` handler, stops, per M8 (a) (v5 V5-F.5; v4's M8 (c) is withdrawn). A stop never settles or releases, and every hold stays | Automatic retain |
```

**R5-8 replaces v4 line 628 (in C4-B; R4-48's result, Stops).** The pre-transfer failure stop is the original one (W3; V4-REQ-F).
```text
v4:
- **Stops.** For a handoff or capture failure, `retain_and_stop_unknown` stops a worker only after `ABANDON(g)` commits, and when `CUSTODY_ACK(g)` exists it does not stop it. Every other stop follows M8 (v4 V4-F.5): the original cancellation, failure-capture and helper stops of the current owner, and an authorized `job.cancel` when no owner is reachable. A stop never settles, releases or relabels anything, and EOF or a deadline alone never stops.
v5:
- **Stops.** Before `TRANSFER_SENT (g)`, when no descriptor has been sent, any launch, capture or handoff failure first commits `HANDOFF_ABORT (g)` and then runs the original failure stop exactly as `retain_and_stop_unknown` does (`rw/protected_root_supervisor.py:346-362`); after that commit no worker can own g (v5 V5-F.2). After `TRANSFER_SENT (g)` and while no `CUSTODY_ACK (g)` is committed, the front stops a worker only after `ABANDON (g)` commits. When `CUSTODY_ACK (g)` exists the front does not stop it. Every other stop follows M8 (v5 V5-F.5). A stop never settles, releases or relabels anything, and EOF or a deadline alone never stops.
```

**R5-9 replaces v4 line 636 (in C4-B; R4-49's result, UNKNOWN routing).**
```text
v4:
| UNKNOWN(cause) | Queued, with authenticated QUEUED progress events (v4 V4-L.2). No process mutates the store. | Queued. An authorized `job.cancel` whose world owns this generation's root unit also causes the M8 stop of that unit (v4 V4-F.5); the stop settles nothing, and the response is the original handler's once custody returns | Queued | Queued | **Reconciler**: native redecision from durable custody, operation and physical evidence (§6.2). A worker that may still own state is never stopped on the reconciler's own initiative, on EOF or on a deadline (§6.6 with R4-48). Once evidence shows that no worker can act (its pidfds are terminal, with CLOSED or ABANDON), collection and reconstruction proceed. Use uncertainty then goes to K4 through `quarantine.resolve` on the reconstructed front (CD-2). |
v5:
| UNKNOWN(cause) | Queued. No process mutates the store. No QUEUED event is sent (v5 V5-L.4). | Queued until a store-custody owner serves it with the original handler: the reattached worker (v5 V5-L.3) or the front of g+1. v4's M8 (c) front stop is withdrawn (v5 V5-F.5) | Queued | Queued | **Reconciler**: native redecision from durable custody, operation and physical evidence (§6.2). A worker that may still own state is never stopped on the reconciler's own initiative, on EOF or on a deadline (§6.6 with R4-48 as replaced by R5-8). The wait ends at the worker's reattachment (v5 V5-L.3), at `CUSTODY_RETURNED` once the worker and namespace-init pidfds are terminal, or at collection (v5 V5-F.2). Use uncertainty then goes to K4 through `quarantine.resolve` on the front of g+1 (CD-2). |
```

**R5-10 replaces v4 line 692 (in C4-B; R4-56's result, RT-10).**
```text
v4:
| RT-10 | CUSTODY_ACK(g); worker alive; front restarted | — | any | worker holds the transferred OFD locks (`rw/protected_startup.py:374-385` `_lock`; `rw/root_worker_journal.py:59-62`) | — | Diagnostic WORKER_OWNED_LIVE. The reconciler does not stop it. The worker completes its root operation under the original time limit and relinquishes (v4 V4-L.2); an authorized `job.cancel` follows M8 (v4 V4-F.5) | Automatic |
v5:
| RT-10 | CUSTODY_ACK(g); worker alive; front restarted | — | any | worker holds the transferred OFD locks (`rw/protected_startup.py:374-385` `_lock`; `rw/root_worker_journal.py:59-62`) | — | Diagnostic WORKER_OWNED_LIVE. The reconciler does not stop it. The restarted front reconnects through the authenticated reattach endpoint (v5 V5-L.3) and requests are served by transfer or RELAY; the worker completes its root operation and relinquishes. A `job.cancel` is served by the worker's original handler (M8 (a), v5 V5-F.5) | Automatic |
```

**R5-11 replaces v4 line 748 (in C4-B; R4-64's result, E10).** One exclusive decision after agreement (V4-REQ-E; R4-64 NOT_SUFFICIENT_AS_WRITTEN).
```text
v4:
| E10 | Worker → sub-helper → actor | The durable `CHILD_READY(t)` witness, then `COMMIT_CHILD`. The sub-helper checks its bindings and decides natively itself (v4 V4-E.3), and only then sends the commit ACK to the actor (the `wait_credential_commit` pattern, `native_root_worker_supervisor_v1.c:93`, `:224`). The actor execs. | `CHILD_READY(t)` | `Decide` / `Decide_V2` again, in the sub-helper |
v5:
| E10 | Worker, then sub-helper, then actor | Exactly one of `CHILD_READY(t)` and `CHILD_ABORT(t)` commits (alternative set `CHILD(t)`). `CHILD_READY` is legal only after `CHILD_AGREED(t)` with both decisions `Child_Ready_Conjunction` on one material digest. After it commits, the worker sends `COMMIT_CHILD_GO` (ticket, material digest, READY event id); the sub-helper checks it against its own agreement and only then sends the commit ACK to the actor (the `wait_credential_commit` pattern, `native_root_worker_supervisor_v1.c:93`, `:224`). The actor execs. After `CHILD_ABORT` the worker sends `ABORT_CHILD`; the sub-helper kills init, and the actor never execs (v5 V5-E.1) | `CHILD_READY(t)` or `CHILD_ABORT(t)` | none added: the exclusive record follows the two decisions of E9 |
```

**R5-12 replaces v4 line 960 (in C4-VB14).**
```text
v4:
**Field forms.** (a) a present zero-length span; (b) an alias of an original span; (b′) a one-byte sub-span `(Negative => False, First => p, Length => 1)` of `Data` over a non-zero byte, used only for N; (c) fresh bytes outside every rebased original span. Every form-(b) and form-(b′) span is a span of `Data`, so it is subject to the construction's `Rebase` like any original span.
v5:
**Field forms.** (a) a present zero-length span; (b) an alias of an original span; (b′) a one-byte sub-span `(Negative => False, First => p, Length => 1)` of `Data` over a non-zero byte, used only for N; (c) fresh bytes outside every rebased original span. These are exactly the four forms of v3 V-B.3 as replaced by R5-1. Every form-(b) and form-(b′) span is a span of `Data`, so it is subject to the construction's `Rebase` like any original span; under compaction (case S-b) the selected form-(b′) span is a member of the union that `Data2` keeps (R5-2), so its byte, non-zero, survives with its value.
```

**R5-13 replaces v4 line 969 (in C4-VB14).**
```text
v4:
| Saturated, case S-b (compaction) | `Data2`: the maximal intervals of the union of every referenced span, in order, then the constants | the compaction map (L-RB-1C) | (a), (b), (b′) mapped; (c) in the appended constants | the same |
v5:
| Saturated, case S-b (compaction) | `Data2`: the maximal intervals of the union of every referenced original span and every selected form-(b′) span, in order, then the constants | the compaction map (L-RB-1C) | (a), (b), (b′) mapped; (c) in the appended constants | the same |
```

**R5-14 replaces v4 lines 1061-1063 (in C4-VC1).** Premises are obligations, not exclusions (V4-REQ-C).
```text
v4:
**Premises.** The chain above establishes consistency, not authenticity. Authenticity rests on four premises, which are stated, not proved. Each stays OPEN with the OS and installation workstream (OB-030 class) and the operator's provisioning (OP-1):
- **P-A1 (installed integrity).** The descriptor, plan, genesis, key and journal at their installed paths are the operator-provisioned objects, and no principal other than root can write them (the `protected` owner and mode checks). A compromised root is out of scope.
- **P-A2 (key secrecy).** Only the owner processes (front, worker, provisioner) read the key. Any process that holds it can write valid custody events, so a compromise of the front or the worker is out of scope. The key's lifetime and zeroization stay OPEN.
v5:
**Premises.** The chain above establishes consistency, not authenticity. Authenticity rests on four premises, which are stated, not proved. Each is an OPEN obligation of the OS and installation workstream (OB-030 class) and of the operator's provisioning (OP-1). None excludes an originally required case: where a premise does not hold, the original requirement it supports is unmet and stays OPEN, and nothing is declared out of scope (v5 V5-C.1).
- **P-A1 (installed integrity).** The descriptor, plan, genesis, key and journal at their installed paths are the operator-provisioned objects, and no principal other than root can write them (the `protected` owner and mode checks). This design does not establish integrity against a compromised root; that original requirement stays OPEN.
- **P-A2 (key secrecy).** Only the owner processes (front, worker, provisioner) read the key. Any process that holds it can write valid custody events, so this design does not establish integrity against a compromised front or worker; that original requirement stays OPEN, with the key's lifetime and zeroization.
```

**R5-15 replaces v4 line 1438 (in C4-VG23).** Custody can return without the barrier; settlement cannot (V4-REQ-G, V4-REQ-L).
```text
v4:
- The escrow's precondition `owned.handler_terminal is not None` (`rw/root_worker_closed.py:26-29`) is replaced by the physical barrier (v3 V-G.2).
v5:
- The escrow's precondition `owned.handler_terminal is not None` (`rw/root_worker_closed.py:26-29`) is replaced by the physical barrier (v3 V-G.2) or, for a custody return without the barrier, by a committed `CUSTODY_RETURNED (g)` (v5 V5-F.2). In the second case the escrow returns custody only: no row is released or charged, holds stay, and U is decided by V5-G.4 (a retained first `RESULT_CAPTURE` goes to the original `finish`, whose native checks decide; otherwise native `QUARANTINE_USE`, then K4).
```

**R5-16 replaces v4 line 227 (in C4-B; R4-1's result, G-12).** The measurement range names v5's items.
```text
v4:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace, socket and interpreter semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14 in §16, K-15 … K-21 in v3 V-O, K-22 and K-23 in v4 V4-N) or its installed-runtime check (RC-1 … RC-4 in v3 V-O, RC-5 and RC-6 in v4 V4-N).
v5:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace, socket, SQLite and interpreter semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14 in §16, K-15 … K-21 in v3 V-O, K-22 and K-23 in v4 V4-N, K-24 … K-27 in v5 V5-N) or its installed-runtime check (RC-1 … RC-4 in v3 V-O, RC-5 and RC-6 in v4 V4-N, RC-7, RC-9 and RC-10 in v5 V5-N).
```

**R5-17 replaces v4 line 259 (in C4-B; R4-5's result, OP-7).** The same range repair v4 made, for v5's items; no operator item is added.
```text
v4:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 (§16), K-15 … K-21 (v3 V-O) and K-22 and K-23 (v4 V4-N) in an authorized lab | §3–§9, v3 V-B … V-I and v4 V4-B … V4-L runtime evidence |
v5:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 (§16), K-15 … K-21 (v3 V-O), K-22 and K-23 (v4 V4-N) and K-24 … K-27 (v5 V5-N) in an authorized lab | §3–§9, v3 V-B … V-I, v4 V4-B … V4-L and v5 V5-B … V5-L runtime evidence |
```

### B.3 Superseded v4 text, and withdrawals from the carried chain

| v4 lines | v4 content | Status in v5 |
|---|---|---|
| 1-179 | Header; §A.1 … §A.8 (answers to the v3 review) | Superseded by the v5 header and §A. History, not normative. |
| 792-839 | §C truth boundary, bases, labels, numbers | v5 §C |
| 841-952 | V4-A | V5-A |
| 954-957 | V4-B heading and its carry sentence | V5-B (which carries C4-VB14) |
| 1011-1041 | V4-B.5 root order; V4-B.6 rollover table | V5-B.5, V5-B.6 |
| 1043-1046 | V4-C heading and carry sentence | V5-C |
| 1069-1104 | V4-C.2 anti-rollback; V4-C.3 JSON forms and `Number_Canonical` | V5-C.2, V5-C.3 |
| 1138-1141 | V4-D heading and carry sentence | V5-D |
| 1158-1177 | V4-D.2 matrix | V5-D.2 |
| 1180-1228 | V4-E heading; V4-E.1 relation; V4-E.2 surfaces; V4-E.3 COMMIT_CHILD | V5-E.1, V5-E.2, V5-E.3 |
| 1263-1402 | V4-F (types, Legal_Reference, C×P rules, Next, Mutation_Allowed, CAS) | V5-F |
| 1405-1414 | V4-G heading; V4-G.1 | V5-G.1 |
| 1441-1454 | V4-G.4 routes RT-21 … RT-27 | V5-G.4 |
| 1457-1467 | V4-H heading; V4-H.1 read-armed intervals | V5-H.1 |
| 1474-1498 | V4-H.3 reattachment; V4-H.4 failure table | V5-H.3, V5-H.4 |
| 1516-1594 | V4-I heading; V4-I.1 joins; V4-I.2 operands | V5-I.1, V5-I.2 |
| 1600-1636 | V4-I.4 gate contracts; V4-I.5 service path; V4-I.6 ordering | V5-I.4, V5-I.5, V5-I.6 |
| 1638-1641 | V4-J heading and carry sentence | V5-J |
| 1662-1693 | V4-J.3 provisioning and startup; V4-J.4 migration | V5-J.3, V5-J.4 |
| 1700-1705 | V4-K heading and carry sentence | V5-K |
| 1715-1745 | V4-K.2 composition; V4-K.3 controls | V5-K.2, V5-K.3 |
| 1747-1794 | V4-L | V5-L |
| 1854-1911 | Appendices A … D | v5 Appendices A … D |

Every other v4 line outside the §B.1 slices is a separator or an empty line.

**Withdrawals from text that C4-B carries:**
- **W5-1.** v2 lines 970-1003, the §6.2 heading, prose and root phase graph inside C2-62 (with R3-10 … R3-13's results), are withdrawn and superseded by V5-F.2, which restates every root row in its own relation and moves the request and descriptor rows to theirs. v2 lines 1004-1010 (INV-C1 … INV-C5, with INV-C4 as replaced by R4-47) stay carried.
- **W5-2.** v3 lines 1299-1374, V-F.5's DDL and its notes (slice C3-VF5, with R4-29's result), are withdrawn and superseded by V5-J.2.

### B.4 Reading rules

- **RR5-1.** Inside carried v4 slices, v4's reading rules RR4-1 … RR4-8 (in C4-B) apply, and the aliases are those of v5 §C.2.
- **RR5-2.** A reference inside carried text to a superseded v4 section resolves through §B.3 to the v5 section with the same letter and number: V4-A.n → V5-A; V4-B.5, V4-B.6 → V5-B.5, V5-B.6; V4-C.2, V4-C.3 → V5-C.2, V5-C.3; V4-D.2 → V5-D.2; V4-E.1 … V4-E.3 → V5-E.1 … V5-E.3; V4-F.n → V5-F.n; V4-G.1, V4-G.4 → V5-G.1, V5-G.4; V4-H.1, V4-H.3, V4-H.4 → V5-H.1, V5-H.3, V5-H.4; V4-I.1, V4-I.2, V4-I.4 … V4-I.6 → V5-I.1, V5-I.2, V5-I.4 … V5-I.6; V4-J.3, V4-J.4 → V5-J.3, V5-J.4; V4-K.2, V4-K.3 → V5-K.2, V5-K.3; V4-L.n → V5-L.n. A reference to v3 V-F.5 resolves to V5-J.2 (W5-2), and one to C2-62's graph to V5-F.2 (W5-1).
- **RR5-3.** "v4 X" inside an R5 text means v4 section X as carried; "v5 Y" means this file's section Y.
- **RR5-4.** An R5 that replaces a line of an R4 block's `v4:` text changes that R4 replacement's result; the block's `v3:` or `v2:` text is unchanged. An R5 that replaces a v3 line names the C3 slice that contains it; no R5 replaces a line that an R4 replaces.
- **RR5-5.** Numbers inside carried slices keep the status their source gave them: observed, or JACKAL exact (v2 J01 … J18). They are not re-derived.
- **RR5-6.** "AUTHOR-NOTES" inside a carried v4 slice means v4's `AUTHOR-NOTES.md` (`0bd92ccd…e66e4`).
- **RR5-7.** v4's M8 (c) front generation-root stop is withdrawn (V5-F.5). Carried text that names it, or "an authorized `job.cancel` when no owner is reachable", has no effect; `job.cancel` is served by a store-custody owner under M8 (a). "QUEUED progress events" inside carried text are withdrawn (V5-L.4).
- **RR5-8.** "Join" inside carried text means `Root_Admission_Join` before `CUSTODY_ACK (g)`, `Transfer_Join` or `Relay_Join` before a request intake, and `Serving_Join` after it (V5-I.1).

---

## C. Truth boundary, bases and method

### C.1 What was done

- **Reading only.** The Read tool and read-only Bash (`sed -n`, `grep`, `sha256sum`, `wc`, `cut`, `nl`, `awk`, `command ls`, `test -e`, and Python scripts on standard input that read files and printed to standard output). No output was redirected to a file. Details: AUTHOR-NOTES §2.
- **Not run.** No compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. Nothing under `/srv`.
- **Not read.** `WT/packets/capi-pk0/`; `~/.local/share/sia/.gbrain/`; the lead's top-level session transcript. The lane draft was read and not changed.
- **SIA.** One `sia.ask` at the start of this task. Nothing from SIA is used as evidence (AUTHOR-NOTES §3). No SIA note was written.
- **Skills.** The eight Ada skills were loaded for this task and applied: `ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`. The SPARK User's Guide is release 28.0w documentation, not evidence about the installed toolchain.

### C.2 Bases (aliases)

| Alias | Path |
|---|---|
| `W` | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` |
| `WT` | `W/work/claude-lead-isolation-v1/wt-1` |
| `L` | `W/work/protected-original-root-worker-repair-v1` (the draft lane) |
| `R` | `L/source`. Unprefixed `core/…`, `runtime/…` and `protected-*/…` paths are relative to `R`. |
| `rw/` | `R/runtime/worldline/` |
| `D2`, `D3`, `D4` | `WT/designs/claude-root-worker-seam-design-v2`, `-v3`, `-v4`; `D4R` is `D4/review/gpt61-v1` |
| `CAPI4` … `CAPI6`, `CAPI5R`, `CAPI6R` | `WT/designs/claude-capi-boundary-design-v4` … `-v6`, and their sealed reviews `review/gpt61-v1` |
| `S5` | `W/work/claude-composition-v5-beta/source` |
| `A1` | `W/work/scoped-committed-envelope-repair-v2-retry1` |
| `CHILD` | `W/work/resource-child-authority-source-v1` |
| `P1/` | `W/outputs/claude-phase1-handoff-20261004/` (`P1:n` is `HANDOFF.md`, line n) |
| `D2:n`, `D3:n`, `D4:n` | v2, v3 or v4 `SEAM-DESIGN.md`, line n, as the reviews cite |

### C.3 Status labels

As v4 §C.3: OBSERVED; STATIC_REASONING; [unverified reasoning] naming a K or RC item; (bound to the sealed CAPI6R); DESIGN; OPEN.

### C.4 Numbers

Line numbers, counts and hashes in this document are observed. Four numerals were derived by arithmetic, all in V5-C.3; each was computed by JACKAL (`jackal_exact`, status `exact`, lane `rat`, `formal=false`, not checker-covered) in one group of four, and is recorded in `jackal.json` as J5-1 … J5-4 (Appendix A). The author's own arithmetic was not used for any of them.

---

## V5-A. Complete typed export contracts, current observations and edges (V4-REQ-A; 01.1, 02.3, 03.3, 11.1; D-1a, D-5a)

v3 V-A (C3-VA with R4-18, inside C4-B) is carried: the two families V1 and V2, deployment-level selection, L-BR-1 and the unchanged V1 references. V5-A replaces v4 V4-A.

### V5-A.1 One wire convention, taken from the existing exports

Observed in the existing wrappers (`rw/canonical_exchange_kernel.py:25-36`; `rw/chain_authority.py:58-73`; `rw/resource_child_execution.py:105-121`; `rw/resource_scoped_run_ledger.py:296-310`), and used unchanged by every new export:
- **Version.** `uint32_t wl_<unit>_version_v<N> (void)` returns N. The wrapper refuses any other value (`CoreUnavailable`).
- **Layout.** `long wl_<unit>_layout_v<N> (uint32_t kind, uint32_t field)`: field 0 is the record's size, field 1 its alignment, field k ≥ 2 the byte offset of its (k−1)th field in declaration order. New exports number their record kinds from 1 in the order listed below (the existing child export numbers from 0; it is unchanged). The wrapper compares every record, size, alignment and offset with its ctypes declaration before the first call.
- **Entry.** `int wl_<unit>_<entry>_v<N> (const uint8_t *arena, size_t arena_len, const In *in, size_t in_size, [const Row *rows, size_t count, size_t stride] …, Out *out, size_t out_size [, uint8_t *out_arena, size_t out_capacity])`. Return 0: the decision is written to `out`. A negative return is an ABI refusal (a size, stride or alignment mismatch, or `WL_ABI_CAPACITY` when `out_capacity` is too small); it carries no decision, and the wrapper raises `CoreUnavailable`. On `WL_ABI_CAPACITY` the result reports the capacity needed, and the wrapper calls again with exactly that capacity, so there is no output cap.
- **Arena.** All variable-length data lives in the caller's arena and is referenced by spans; spans are checked against `arena_len` natively (`Span_Valid`, `core/resource_quantities.ads:25-28`). Output quantities (for example generation g+1) are written to `out_arena` and returned as spans into it.
- **Primitive records,** existing and unchanged: `Id` = `L.RawId {present: uint8; first: int64; length: int64}` (`rw/resource_run_ledger.py:91-92`), an `L.Identity` or optional span; `Qty` = `L.RawQuantity {negative: uint8; first: int64; length: int64}` (`:94-95`), a `Q.Quantity`; `OptQty` = `L.RawEpoch {present: uint8; value: Qty}` (`:97-98`), a `Q.Optional_Quantity`; `Dig` = `_Digest {present: uint8; value: uint8[32]}` (`rw/chain_authority.py:39-40`); enumerations are `uint8` holding the Ada `'Pos`.
- **No caller flag selects a branch.** Mode fields are enumerations that the native unit checks against the other inputs; a mode that disagrees with them is a named refusal.

### V5-A.2 What stays exactly as it is

- **Existing exports, unchanged in symbol, version, layout and semantics** (NF5-4): `wl_canonical_operation_*_v1`, `wl_canonical_exchange_*_v1`, `wl_canonical_owner_completion_*_v1`, `wl_operation_authority_*_v1`, `wl_recovery_protocol_*_v1`, `wl_owner_*_v1`, `wl_chain_authority_*_v1`, `wl_full_physical_*_v1`, `wl_resource_run_ledger_*_v1`, `wl_resource_scoped_run_ledger_*_v1`, `wl_resource_observation_*_v1`, `wl_resource_child_execution_*_v1`, `wl_resource_actor_*_v1`, `wl_completion_*_v1`, `wl_pending_*_v1`, and every other export in the frozen roster.
- **Every original route, fixture and reference.** Every original wrapper, its exact-type dispatch, its callers and its fixtures stay; each V2 or new export is additive under a new symbol family. No original reference function or `Post` is edited.

### V5-A.3 New and successor exports

Each entry gives: symbol family; records (kind order); entries; result codes; producer and the exact current observation it reads; producer pre and post; callers; dependency edges (native units consumed, and units that consume it). Everything here is DESIGN; every body, `Post`, cost and caller correspondence stays OPEN.

**X-1 `wl_source_json_{version,layout,recognize,number_canonical,extract,archive_equal}_v1`** (unit `Worldline.Source_Json`, spec S2).
- Records: (1) `JsonInput {container: Id; form: uint8 (UTF8, ASCII); trailing_lf: uint8 (Forbidden, One_Permitted)}`; (2) `PathStep {kind: uint8 (Key, Index); key: Id; index: Qty}`; (3) `NumberInput {lexeme: Id; form: uint8}`; (4) `ArchiveInput {container: Id; form: uint8; archive: Id}`; (5) `JsonResult {status: uint8; value: Id; value_kind: uint8 (Object, Array, String, Number, True_Lit, False_Lit, Null_Lit); failing_offset: Qty}`.
- Entries: `recognize (JsonInput)`; `extract (JsonInput, PathStep rows)`; `number_canonical (NumberInput)` (V5-C.3); `archive_equal (ArchiveInput)`: decodes the archive by the grammar of `rw/operation_capture.py:15-39` and compares its typed tree with the JSON value tree (V5-J.3).
- Status: `Ready`, `Not_Utf8`, `Bad_Token`, `Duplicate_Key`, `Key_Order`, `Spacing`, `Escape_Form`, `Number_Form`, `Number_Not_Finite`, `Trailing_Bytes`, `Path_Absent`, `Archive_Malformed`, `Archive_Mismatch`.
- Producer: the Python loader that read the container; current observation: the exact bytes the source lease binds as DATA (`source.file (path, ('DATA',))`, `rw/root_worker_journal.py:40` pattern). Pre: the Python exact check (`exact_json` or `exact`) accepted the same bytes. Post: `Ready` exactly when that check accepts (obligation CJ-JSON).
- Callers: the startup descriptor loader, the custody v2 loader (genesis), the crosswalk loader, the run-scoped config loader, X-6 (request document).
- Edges: consumes nothing native; consumed by X-2, X-3, X-4, X-6.

**X-2 `wl_roster_join_{version,layout,join}_v1`** (unit `Worldline.Roster_Join`, S2).
- Records: (1) `RosterInput {descriptor: Id; genesis: Id; kind: uint8 (Policy, Run_Config, Header_Data, Source)}`; (2) `RosterEntry {path: Id; sha256: Dig; role: uint8}`; (3) `RosterResult {status: uint8; mismatch_index: Qty}`.
- Producer: the loader's DATA bindings; pre: X-1 `Ready` on both containers. Post: every entry's path and digest equal the container's.
- Edges: consumes X-1 and `Attest.SHA256`; consumed by X-3, X-6, the V2 producers.

**X-3 `wl_root_crosswalk_{version,layout,decode}_v1`** (unit `Worldline.Root_Crosswalk`, S3).
- Records: (1) `CrosswalkInput {crosswalk: Id; policy: Id; catalogue: Id; plan: Id; descriptor: Id; entry_kind: uint8; name: Id; right: Id}` (`right.present = 0` for null); (2) `ChildPlan {task_kind: Id; plan: Dig}`; (3) `HeaderData {path: Id; sha256: Dig}`; (4) `CrosswalkResult {status: uint8; plan_sha256: Dig; cost_key: Id; cost_kind: uint8 (Held_Capacity, Irreversible_Budget); cost_amount: Qty; helper_image: Dig; decision_library: Dig; coordinator: Id; delegation_record: Dig; physical_resource: Id; physical_unit: Id; physical_machine: Id}`. `decision_library` is a crosswalk field added by v5 (`decision_library_sha256`, the sha256 of the core library whose `decide` the sub-helper calls, V5-E.3); every field of C4-VC45's table is unchanged.
- Joins: `Entry_For` unique per (kind, name, right); `Plan_Join`; `Cost_Join` (the catalogue's `costs[cost_key]` kind and amount); every field of C4-VC45's table.
- Producer: the crosswalk file bound in `files` (C4-VJ12). Callers, each reading only the decoded result: `_reserve`, `pre_effect`, `launch_root_worker`, `resource_launch_material`, `machine_admission`, the dispatcher (V5-B.6).
- Edges: consumes X-1, X-2; consumed by X-8, X-9 and the dispatcher.

**X-4 `wl_custody_chain_{version,layout,verify}_v2`** (unit `Worldline.Custody_Chain`, S2H).
- Records: (1) `ChainInput {key: Id; genesis_file: Id; genesis_row: Id; genesis_mac: Dig; head_kind: uint8 (Origin, Event); head_event: Dig; head_origin: Dig; head_mac: Dig}`; (2) `EventRow {event_id: Dig; previous: Dig; generation: Qty; operation: Id; subject_kind: uint8; subject: Id; subgeneration: Qty; kind: uint8; actor: uint8; record: Id; base_archive: Id; mac: Dig}`; (3) `ChainResult {status: uint8; failing_row: Qty; origin: Dig; head: Dig}`.
- **HMAC operands, exactly.** `Hmac_Sha256 (K, M)` is RFC 2104 HMAC with SHA-256 over the whole key K, whatever its length (a key longer than the block is hashed first; there is no key-length cap). K is the bytes of `authority/issuer/state/issuer-key.bin`. `DOMAIN_V2` is `worldline.protected-root-custody-v2` followed by one zero byte. The three messages are: genesis, `DOMAIN_V2 ‖ archive ({genesis})`; event, `DOMAIN_V2 ‖ base_archive`, where `base_archive` is `archive` of the record {previous, generation, operation, subject_kind, subject, subgeneration, kind, actor, record}; head, `DOMAIN_V2 ‖ archive ({head_kind, head, genesis})`.
- Checks: `base_archive` decodes (archive grammar) to exactly the row's columns; `event_id = SHA-256 (base_archive)`; each `previous` is the prior row's `event_id`, the first row's being the origin `SHA-256 (genesis_row)`; MACs equal; the head is ORIGIN with the origin when there are no rows, and EVENT with the last id otherwise; X-1 `archive_equal` holds between `genesis_file` and `genesis_row` (V5-J.3).
- Status: `Ready`, `Genesis_Mismatch`, `Genesis_Mac`, `Row_Malformed`, `Row_Link`, `Row_Id`, `Row_Mac`, `Head_Kind`, `Head_Value`, `Head_Mac`.
- Producer: the custody v2 loader, reading every row `ORDER BY seq` inside one SQLite transaction (`BEGIN` for loads, `BEGIN IMMEDIATE` for appends); current observation: those rows and the head row in that transaction, the key bytes and the DATA-bound genesis file. Pre: premises P-A1 … P-A4 (OPEN). Post: chain integrity relative to the key given; no selection claim.
- Edges: consumes `Attest.SHA256`, X-1; consumed by X-5 (fold), startup, the reattach handshake (V5-L.3).

**X-5 `wl_root_custody_phase_{version,layout,legal,next,fold,mutation_allowed}_v1`** (unit `Worldline.Root_Custody_Phase`, S9).
- Records: (1) `RootStateRec {present: uint8; generation: Qty; operation: Id; phase: uint8; before_unknown: uint8; owner: uint8; closure_ns, closure_outer, closure_raw, stop_intent, returned: uint8; unknown_cause: Dig; head: Dig}`; (2) `SubjectStateRec {kind: uint8; generation: Qty; subject: Id; subgeneration: Qty; phase: uint8; mode: uint8 (None, Fresh, Relay); position: OptQty; carried_from: OptQty; head: Dig}`; (3) `EventRec {kind: uint8; generation: Qty; operation: Id; subject_kind: uint8; subject: Id; subgeneration: Qty; actor: uint8; record_digest: Dig; event_id: Dig}`; (4) `EvidenceRec {kind: uint8; value: Id}`; (5) `MutationInput {actor: uint8; mutation: uint8; subject_kind: uint8; subject: Id; generation: Qty}`; (6) `PhaseResult {status: uint8; root_count: Qty; subject_count: Qty; allowed: uint8}`.
- Entries: `legal (root rows, subject rows, EventRec, evidence rows)`; `next (same) → out rows and out_arena`; `fold (EventRow rows of X-4, root rows, subject rows)`: folds `Next` from the initial state S0 and reports `Ready` only when the result equals the stored rows exactly; `mutation_allowed (root rows, subject rows, MutationInput)`.
- **Mutation operands, exactly.** The actor is the caller's own role, fixed at construction of its journal object (front, worker, collector or reconciler; never taken from a request). The mutation is the choke point's constant (M1 … M11). The subject is the operation id for M1 … M3, the request id for M5, the descriptor id for M6 and M7, the unit for M8 … M10, and empty for M4 and M11. The generation is the caller's own generation from its last committed custody event.
- Producer: the custody v2 loader after X-4 `Ready`; current observation: the state rows read in the same transaction as the chain. Callers: M1 … M11 choke points (V5-F.5), the CAS (V5-F.6), startup.
- Edges: consumes X-4, `Resource_Quantities` (generation and sub-generation successor, value equality), and the recorded results of X-6 and X-7 as evidence digests; consumed by X-6, X-7, every mutation.

**X-6 `wl_requester_correspondence_{version,layout,root_admission_join,transfer_join,relay_join,serving_join,relay_frame}_v1`** (unit `Worldline.Requester_Correspondence`, S8).
- Records: (1) `RequesterOperands` exactly as V5-I.2; (2) `RelayFrameInput {frame: Id; key: Id; expected_generation: Qty; expected_request: Id; expected_subgeneration: Qty; expected_operation: Id; expected_sequence: Qty; expected_nonce: Dig; intake_head: Dig}`; (3) `JoinResult {status: uint8}` with the results of V5-I.1.
- Producer and current observations: the transfer-intent record (custody chain, X-4 `Ready`); the worker's own `getsockopt` re-read of a transferred socket at each gate use (FRESH); the front's re-read returned in a RELAY frame (RELAY); the retained capture bytes (RETAINED, HISTORICAL).
- Callers: the worker at `CUSTODY_ACK (g)` (`root_admission_join`), at `REQUEST_INTAKE` (`transfer_join`, `relay_join`), and at every gate use (`serving_join`; `relay_frame` for each RELAY response).
- Edges: consumes X-1 (request document), X-2, X-4 (heads), X-5 (phase and owner), `Hmac_Sha256` (RELAY MAC); consumed by X-5 as recorded evidence.

**X-7 `wl_child_event_{version,layout,legal}_v1`** (unit `Worldline.Child_Event_Legal`, S12).
- Records: (1) `ChildEventRec {kind: uint8; task: Id; ticket: Dig; material: Dig; worker_decision: uint8; helper_decision: uint8; actor: uint8; generation: Qty; previous: Dig}`; (2) `ChildResult {status: uint8}`.
- Producer: the scoped observation journal under the child reservation (`ScopedObservationJournal`, `rw/protected_scoped_resource_runtime.py:70`), read under its own lock. Callers: the worker before each child event append and the sub-helper protocol (V5-E.1).
- Edges: consumes X-5 (root owner and phase of the generation), the S4 decisions as recorded values; consumed by the dispatcher.

**X-8 V2 successors in S4:** `wl_resource_scoped_run_ledger_{version,layout,check,validate,classify}_v2`, `wl_resource_observation_{version,layout,classify,current}_v2` and `wl_resource_child_execution_{version,layout,decide}_v2`.
- Records: every V1 record of the same unit, unchanged and first (the V1 `PARAMETERS` roster of `rw/resource_child_execution.py:207`; the scoped records `N_Raw_*` of `:75-82`), then (k) `FactsV2 {base: O.RawFacts; selected: uint8; delegation: Dig; producer_a: Dig; producer_b: Dig}` and (k+1) `Selection {row_index: Qty; family: uint8}`.
- Producer: `ScopedV2Producer` over exactly one `ScopedSnapshot {state, history, rows, projection, buckets}` (`rw/protected_scoped_resource_service.py:20-25`), taken by `current_snapshot ()` under `operation_lock`. Pre: the deployment selects V2 (V5-A.5). Post: each `base` equals the V1 producer's facts for the same snapshot (PD-1); each P8 … P11 pair comes from distinct producers.
- Edges: consume X-2, X-3 and the unchanged V1 units; consumed by X-9, X-10, the child decisions and the sub-helper.

**X-9 `wl_scoped_canonical_operation_{version,layout,decide}_v1` and `…_v2`** (unit `Worldline.Scoped_Canonical_Operation`, S1). Both are new (NF5-4); v4's wording that a `…_v1` existed is corrected.
- Records: (1) `ScopedOperationInput {operation: <the existing RawInput of rw/canonical_operation_kernel.py>; scoped_state: S.RawScopedState; bound_row: Qty; intent: S.RawScopedIntent; current: S.RawCurrentObservation}`; rows: `S.RawScopeFrame` (history), `L.RawRow`, `S.RawPhysicalProjection`, `S.RawPhysicalBucket`, `L.RawNative`, `O.RawFacts`; and for `_v2`, `FactsV2` and `Selection`; (2) `ScopedOperationResult {decision: uint8}` with the C1 … C3 decisions of C2-31 and R3-25.
- Producer: `pre_effect` (and the B2b and B2c successors) over `current_snapshot ()` under `operation_lock`, with `before == current_snapshot ()` re-checked after the decision (PD-4; as `rw/protected_operations.py:711` does for the flat path).
- Edges: consumes X-8 (V2), X-3 and the existing `wl_canonical_operation` unit for C1; consumed by `pre_effect`, X-10.

**X-10 Scoped exchange and owner-completion successors:** `wl_scoped_canonical_exchange_{version,layout,decide}_v1`/`_v2` and `wl_scoped_owner_completion_{version,layout,decide}_v1`/`_v2` (B2b, B2c). Records: the existing flat `Material`, `Input` and `Result` of `rw/canonical_exchange_kernel.py:16-20` (and of `rw/canonical_owner_completion_kernel.py`) with `ScopedOperationInput` in place of the flat operation input. Producers: the broker's current snapshot in request, the retained original snapshot in recovery (`rw/protected_operations.py:430-438`), the quarantined row's capture for K4 (`:820-830`). The flat exports stay as they are.

### V5-A.4 Current observations, per consumer

| Consumer | The one current observation | Re-read that keeps it current |
|---|---|---|
| S1 pre-effect | `ScopedSnapshot` from `current_snapshot ()` | under `operation_lock`, and equality re-checked at the boundary (PD-4) |
| Root admission (worker exec) | the root capture (`rw/protected_root_observation.py:98-135`) | taken after HELD and before EXECUTION_NATIVE; P3 by `Process_Images_Covered` |
| `CUSTODY_ACK` intake | the seed under the transferred OFDs (`same_logical_state`, v2 §6.4) | at intake, inside the worker, before the CAS |
| Child decision | the relayed credential frame, the helper ancestry frames and the read-only procfs view | per child at E9, in the worker and again in the sub-helper |
| Requester joins | V5-I.2 operands | at intake, and at every gate use (FRESH: own `getsockopt`; RELAY: the front's re-read in a fresh frame) |
| Custody legality and mutation | the chain and state rows in one transaction | at every append and at every choke point; ownership can be removed only by the owner's own commit or after its death (lemma OWN-1, V5-F.5) |
| HMAC | key bytes, genesis bytes, rows | at every load and every append's read-back |

### V5-A.5 Family selection and the V1 fallback

- **V2 is selected** only when the startup descriptor's exact schema is `worldline.protected-startup-v2` and the crosswalk names an authentic V2 producer for every live row (v3 V-A.3).
- **Otherwise V1 decides,** including on a v2 descriptor. The V1 fallback is purely additive: it uses only the existing exports and routes, and it adds no refusal of any original accepted case.
- **The lane's workload refusal is not part of the V1 fallback.** v4 V4-A.4 named it there; that sentence is withdrawn. The refusal at `rw/protected_operations.py:744-745` is the lane's containment, recorded as OPEN containment gap CG-1 (V5-B.6). No v5 route depends on it.
- **No conversion** between V1 and V2 packets in either direction.

### V5-A.6 Dependency graph and preparation order (replaces v4 V4-A.5)

**Spec nodes.**

| Spec | Content | Depends on |
|---|---|---|
| S0 | SL-0 hygiene and the lock model (V5-L); no native spec | — |
| S2 | X-1, X-2, `Root_Controller_V2` | existing types, `Attest` |
| S2H | X-4 and the archive grammar; the reattach handshake MAC (V5-L.3) | `Attest`, S2 |
| S8 | X-6, including the RELAY frame (V5-I.5) | S2, S2H |
| S3 | X-3, `Enforcement_Corresponds` | S2 |
| S9 | X-5: the three relations, cross-conditions, owner functions, Next, fold, Mutation_Allowed (V5-F) | S2H, S8 |
| S4 | X-8 | S2, S3 |
| S7 | Slot and drain transfer with armed intervals and the interval fold (V5-H) | S9 |
| S1 | X-9 | S2, S3, S4 |
| S12 | X-7 and the child commit protocol (V5-E) | S4, S9 |
| S6 | State model, O mapping, `finish` split, adapters, crash routes, `HANDOFF_ABORT` and `CUSTODY_RETURNED` routes (V5-G) | S1, S9 |
| S13 | Genuine workload dispatcher (V5-B.6) | S3, S12, S6 |
| S10 | Multiplexing and accounting: alternatives, including H, drafted before D-4a; a selected specification needs D-4a (V5-D, V5-L) | S1, S3, S4, S7, S8, S9 |
| S11 | Startup union, initial authentication, migration and reconciliation (V5-J, V5-G.4) | S2H, S3, S4, S6, S7, S9 |

**Preparation order,** consistent with every edge: (1) S0, S2; (2) S2H, S3; (3) S8, S4; (4) S9, S1; (5) S7, S12, S6; (6) S13, S10 (alternatives only); (7) S11. Each node's dependencies are in earlier waves.

**Body nodes** are v4's (C4-B carries none of them; they were in V4-A.5) with these changes: B2H also implements the reattach handshake; B9 implements the three relations and `HANDOFF_ABORT` and `CUSTODY_RETURNED`; B-RECV implements the RELAY codec of V5-I.5; B4 implements the v2 helper protocol of V5-E.3; **B13** (new) implements the dispatcher of V5-B.6 and needs S13, B4, B6 and B9. B0, B3, B1, B2b, B2c, B6, B7, B10, B11 and B12 keep v4's content and needs. The integration gates G-CAPI, G-CAPI-P, G-PROT, G-RW, G-A1, G-DEP, G-REVIEW and the runtime gates R-PROOF, R-LAB, R-PUB are unchanged in meaning; none is an operator gate.

---

## V5-B. Witness union, RQ-1 per operation, and the workload dispatcher (V4-REQ-B; 01.2, 01.3, 01.5, 01.7; D-1a, D-1b)

v4 V4-B.1 … V4-B.4 are carried (C4-VB14, with R5-12 and R5-13), and v3 V-B with R5-1 … R5-3 (in C4-B).

### V5-B.1 The selected witness spans and the compaction union

- **Selected witness spans.** For a given input and construction, the selected witness spans are every field of form (b) and every field of form (b′). Form (b) spans are spans the original packet already references. The one form-(b′) span is N's.
- **Every construction's `Rebase` maps them** (R5-1, R5-12): single-frame and multi-frame by L-RB-1P, which is the identity on `Data'Range`; S-a by the identity; S-b by L-RB-1C.
- **The compaction union** (case S-b; R5-2, R5-13) is the union of every span the original packet references and the selected form-(b′) span. L-RB-1C holds for every member, so N's single byte keeps its non-zero value in `Data2`, and W3 holds after compaction as before it.
- **Coverage** (R5-3): S-b holds when that union's length plus the constants' length is at most `Byte_Count'Last`; otherwise the input is R3, decided by the original unit. Adding one byte to the union can only move an input from S-b into R3; it excludes no input from the system, because every flat input is decided by the unchanged original unit (G-1).
- **One roster everywhere.** The carried v3 V-B.3 (R5-1), v3 V-B.6 (R5-2, R5-3), v4 V4-B.1 (R5-12, R5-13), R4-2's W9 and `seams.json` all name the same four forms and the same union.

### V5-B.2 … V5-B.4

Carried as v4 V4-B.2 … V4-B.4 (C4-VB14). CV-B′ (D_prod ⊆ D_emb) and CV-R stay OPEN; nothing in v5 claims D_prod coverage.

### V5-B.5 RQ-1: per operation, against its own original

**Operation classes,** by what the serial route does with the operation (`rw/protected_operations.py:727-768`):
- **OW (owner):** `owner.retry`, `owner.adopt`, `owner.recover` (`:284`, `:731-741`). Never on the root route (`:724`); unchanged.
- **IP (in-process):** every other protected operation except the workload set, including `quarantine.resolve` (`:751`). On the serial route its handler runs in the process that owns custody, without any launch.
- **WL (workload):** `fork`, `race`, `revalidate`, `simulate`, `ghost.run`, `ghost.enable`, `root.add`, `init` (`:744`). Their original accepted behaviour is to run workload under a protected launch; the lane's serial route refuses them (CG-1, V5-B.6).

**Routing (DESIGN).** The lane routes every non-owner operation to `RootWorkerFront.invoke` whenever a root worker is attached (`:723-725`), which adds a launch to IP operations. v5 routes:
- **OW and IP** to `_invoke_serial` in whichever process owns custody: the front in FRONT_* phases; the worker, by FRESH transfer or RELAY, while it owns (V5-I). No IP operation ever launches a root unit. So the W2 and W3 refusal sites that the root launch adds do not exist for IP operations, and their durable outcomes, recovery and costs are the original serial route's.
- **WL** to the root route, which launches the request's own unit and runs the handler in the worker with the dispatcher of V5-B.6, while the front owns. While a worker owns, a later WL request is queued for the next generation unless D-4a selects an option that serves it (V5-D, V5-L).

**The serial order, kept exactly** (DF-3, NF4-1). Steps 1–8 of `_invoke_serial` are unchanged wherever it runs: genuine request context (`:728`); unresolved-use gate with only `quarantine.resolve` excepted (`:730`); owner branch (`:731-741`); `_reserve` (`:742`); the WL check (`:744-745`, CG-1, reached only where no root route exists); `pre_effect`, `RESERVE_USE` replay `RESERVED_REPLAY`, `EFFECT_INTENT` with boundaries `[pre-effect, DISPATCH_INTENT]` (`:746-749`); the handler in `OperationScope` (`:750-754`); `finish` or the SETTLED ACK (`:757-765`); every exception after `_reserve` → `quarantine` unless SETTLED or RELEASED (`:767-777`). The root route for WL keeps steps 1–4 and 6 with the `DISPATCH_INTENT` boundary that the draft omits (`rw/protected_root_worker.py:170-171`), and step 8 by the rules of R5-8: before `TRANSFER_SENT (g)` the front quarantines exactly so; after `CUSTODY_ACK (g)` the worker's own `_invoke_serial`-equivalent path does; a dead worker's U is decided by V5-G.4.

**IP operations, window by window.** Original: the serial route. v5: the same route in the custody owner. Context rollover is refused only at Reserve for these operations, because no launch commands run.

| Window | Original accepted or refused | U records | P records | Recovery | Exact cost (original) | Added by v5 |
|---|---|---|---|---|---|---|
| W0 before Reserve | refused: `Context_Changed` at Reserve (the scoped Reserve guard, `core/resource_scoped_run_ledger.ads:359`) with the request's own current packet, produced by `intent_for_operation` (`rw/protected_scoped_resource_runtime.py:382`, its gate at `:386`) | no row | no hold | none | one Reserve decision | none in the front; in the worker, the transfer events of V5-I |
| W1 Reserve → `EFFECT_INTENT` | accepted through Retained_Join (R3-25 … R3-31) | `EFFECT_INTENT` | RESERVED, never launched | continues | Reserve, pre-effect (S1), `RESERVE_USE` replay | as W0 |
| W2, W3 | do not exist: no launch command runs | — | — | — | — | — |
| W4 handler and settlement | accepted or the handler's own error; an exception → `QUARANTINED` (`:767-768`) | `ACK`, `EFFECT_OBSERVED`, `SETTLED`, or `QUARANTINED` | settled through the use's own reservation, as original | RT-17, RT-18, RT-21 … RT-24 | `OBSERVE_EFFECT`, `SETTLE_USE`, or `QUARANTINE_USE` and one K4 | as W0 |
| W5 head-only change | not `Context_Changed` for the guards; `Current_Valid` (`:426-430`), the operation and canonical gates and the physical gates still decide | as W1 or W4 | as W1 or W4 | as W4 | as W4 | as W0 |

**WL operations, window by window.** Original: the protected scoped launch `launch_reserved` (`rw/protected_scoped_resource_runtime.py:698-769`): machine admission at DISPATCH (`:739`), `RECORD_LAUNCH_INTENT` (`:741`), `DISPATCH_INTENT` (`:756`), `systemd-run` (`:760-765`), HELD (`:766`), `RECORD_RUNNING` (`:767-768`), GO. v5: the root launch for the request's own reservation, the same native commands on the same row (`rw/protected_root_resource.py:64-141`), then the handoff.

| Window | Original accepted or refused | U records | P records | Recovery | Exact cost (original) | Added by v5 |
|---|---|---|---|---|---|---|
| W0 | refused at Reserve, as IP W0 | no row | no hold | none | one Reserve | none |
| W1 | accepted, as IP W1 | `EFFECT_INTENT` | RESERVED | continues | as IP W1 | none |
| W2 `RECORD_LAUNCH_INTENT` refused (`Context_Changed`) | refused; the launch raises, the handler's exception reaches quarantine | `QUARANTINED` | launch journal `Never_Dispatched`, class `Never_Launched` → `Release_Hold` (PR-a) | P automatic; U by K4 | one `Record_Launch_Intent` decision, `QUARANTINE_USE`, `Release_Hold`, one K4 | `HANDOFF_ABORT (g, NEVER_DISPATCHED)`, which also creates g+1 (V5-G.1); no CLOSED_WITNESS |
| W3 `RECORD_RUNNING` refused after HELD | refused; the original launch's failure branch journals `UNKNOWN` and keeps the capacity, endpoint and intent, with no retry and no terminal verdict (`:770-776`); the exception reaches quarantine | `QUARANTINED` | dispatched, no GO; without the helper's `CLOSED … ECHILD` frame the class is `Unknown` → `Retain_Uncertain` (PR-b) | U by K4; P by owner recovery from authentic closure | as W2, with `Retain_Uncertain` in place of release | `HANDOFF_ABORT (g, DISPATCHED)`; then the root launch's own failure stop (`rw/protected_root_resource.py:142-143` → `retain_and_stop_unknown`; R5-8), where the original scoped launch stops nothing and leaves the held unit to its helper; both keep every hold. This stop is a stated difference; collection of g's closure follows |
| W4 after Running | the three guards cease; every other gate still applies | per the handler | per closure | V5-G.4 | the original settlement commands | the handoff events, transfer of descriptors, and the custody costs of V5-F; listed as additions, not as equalities |
| W5 head-only | as IP W5 | as W4 | as W4 | as W4 | as W4 | as W4 |

**Statement.** For IP operations the durable outcome, recovery and cost in every window are the serial route's, because they run on it. For WL operations W0 … W3 use the same native commands at the same refusal points as the original scoped launch, and v5 adds the custody events listed; W4 adds the handoff and its custody costs. These are differences, stated; RQ-1 stays OPEN until the positives and refusals of v3 V-B.9, V-B.10, V4-M and V5-M exist with proofs.

### V5-B.6 The genuine workload dispatcher, and containment gap CG-1

**CG-1 (OPEN containment gap).** The lane's serial route refuses every WL operation with `OPERATION_ORIGINAL_WORKLOAD_RESOURCE_ROUTE_UNINTEGRATED` after `_reserve`, then quarantines it (`rw/protected_operations.py:744-745`, `:767-768`). That refuses originally accepted workload cases. It is the unfinished lane's containment, not original behaviour, and v5 treats it so:
- no v5 route, control or acceptance argument depends on it or counts it as preserving anything;
- it is not added to the root route (v4 V4-B.5 row 5 and V4-A.4 are withdrawn);
- it stays in the serial route's text only where no root route exists (a deployment without a root worker), and there the WL accepted cases are unmet and OPEN;
- CG-1 closes only when the dispatcher below is implemented, reviewed and its controls pass, and every original WL accepted case is served.

**The dispatcher (DESIGN; spec S13, body B13).** The original runner launches agent work through its `systemd` object (NF5-2): `launch (instance_id, argv, description=…, nice=…, resource_properties=…)`, `stop (unit)`, `effective_limits (unit)`, `resource_telemetry (unit)`. In the worker, for the root's own WL operation, the controller's runner is constructed with a `WorkerSystemdDispatcher` that has exactly those four methods and argument conventions:
- `launch` performs one child task through the child relation (V5-E.1): `TASK_INTENT` with the runner's argv, description, nice and resource properties and the original workload capture; child Reserve with `Task_Admission`; `Record_Launch_Intent`; `CHILD_DISPATCH_INTENT`; `CREATE_CHILD`; HELD; `Record_Running`; GO with machine admission; measurement; candidate and agreement; `CHILD_READY`; exec. It returns a `DispatchedProcess` whose `unit` is the child's leaf unit name and whose stdio are the child pipes, with the original raw drain and stdin pump (V4-H.2, V4-H.5).
- `stop` sends `STOP_UNIT` for that leaf unit (M8 (a)).
- `effective_limits` and `resource_telemetry` send `OBSERVE_UNIT` and read the leaf's cgroup files through the read-only view, returning the original dictionaries' keys.
- **What stays original.** The runner, its gate (`self.gate.guard`, `rw/runner.py:694-696`), its cancelled set, its sampling loops and its finalization writer are unchanged code. The handler is the original handler.
- **Correspondence obligations (OPEN).** CJ-DISP-1: each method returns what the original method returns for the same unit, or raises the original exception types. CJ-DISP-2: the runner's cancel takes its `owner.controller_call` branch only for an exact `SystemdProcess` (`rw/runner.py:477-481`); with a `DispatchedProcess` it takes the plain `self.systemd.stop` branch, and the two branches must be shown to stop the same unit with the same ownership effect. CJ-DISP-3: the actor argv built by the sandbox (`self.sandbox.build_argv`) runs inside the child namespaces exactly as under the original manager, which RC-6 and K-20 must establish.
- **Scope.** The dispatcher serves the root's own operation. Later WL requests while a worker owns follow the accounting decision of D-4a (V5-D); with none selected they are queued for g+1 (V5-L), and that progress difference stays OPEN.

---

## V5-C. Premises, bounded rollback detection, and native number canonicality (V4-REQ-C; 02.1, 02.2, 02.3; D-7a)

Carried: v3 V-C (C3-VC with R4-21 … R4-23, inside C4-B); v4 V4-C.1 (C4-VC1 with R5-14); v4 V4-C.4 and V4-C.5 (C4-VC45).

### V5-C.1 Premises as obligations

R5-14 restates P-A1 and P-A2 without exclusions. The four premises are OPEN obligations, and they are listed in V5-O against the original requirements they serve:
- **Selection** (P-A1, P-A3): the descriptor, plan, genesis, key and journal are the provisioned objects. Original requirement: authentic installation and provisioning (OB-030 class, OP-1).
- **Currentness** (P-A4): the journal presented is the latest. Original requirement: no rollback of custody (V5-C.2 says how much v5 detects).
- **Producer** (P-A2): only the owner processes hold the key and write events. Original requirement: authentic producers (P1 workstream 5).
- **Confinement**: the coordinator cannot reach authority beyond its roster (C4-VE4, M-1 … M-7). Original requirement: actor and coordinator containment (D-5a).
No case is excluded because a premise might fail; such a failure leaves the original requirement unmet, which is reported, never treated as out of scope.

### V5-C.2 Rollback detection, bounded to the recorded cross-references (replaces v4 V4-C.2)

**Mechanism.** After each commit of `HANDOFF_INTENT`, `CUSTODY_ACK`, `HANDOFF_ABORT`, `CUSTODY_RETURNED`, `CLOSED_WITNESS`, `FRONT_RECONSTRUCTION` and `FRONT_OWNED`, the committing owner appends an observation event `CUSTODY_REFERENCE {event_id, generation, kind}` to the scoped observation journal under the root reservation (`ScopedObservationJournal`, `rw/protected_scoped_resource_runtime.py:70`). The *referenced set* at a check is every event id named by a `CUSTODY_REFERENCE` present in that journal, plus every operation-journal head that a present custody frame binds.

**Detected (exactly):**
- the custody journal file replaced while open (identity pinned, `rw/root_worker_journal.py:69-77`);
- an event or head edited, inserted or removed by a party without the key (MAC, X-4);
- a custody journal restored alone to a valid prefix that lacks at least one member of the referenced set (RT-14; a named refusal, never a re-genesis).

**Not detected (non-claims, each tested by a control that expects no detection, V5-M):**
- **Tolerated append window.** A crash between a custody commit and its `CUSTODY_REFERENCE` append leaves an unreferenced event. A restore that removes such events, and only such events, loads as `Ready`.
- **Unreferenced kinds.** A restore that removes only events after the last referenced event (for example request, descriptor, `ORIGINAL_RESULT` or `UNKNOWN` events) loads as `Ready`.
- **Coordinated restores** of the custody journal and the scoped observation journal (and the store) to an earlier mutually consistent state.
- Any action by a holder of the key (P-A2), and any rollback before the first reference exists.

So the claim is exactly: a custody journal whose prefix ends before the latest referenced event is refused. Nothing is claimed about any other earlier valid prefix. An external monotonic witness would widen this; none is proposed (it would be a new installation prerequisite).

### V5-C.3 Number canonicality with a sign channel, natively specified (replaces v4 V4-C.3)

The two JSON forms, their encoders, Python checks, containers and string rules are v4 V4-C.3's table, unchanged (the encoders are `rw/protected_startup.py:35-37` and `rw/protected_resource_runtime.py:20`; the checks `rw/protected_startup.py:40-51` and `rw/protected_resource_runtime.py:22-23`). Strings and escapes stay **[unverified reasoning, RC-4]**. Numbers are now specified natively.

**Lexemes.** A number lexeme X follows the JSON grammar `-? (0 or [1-9][0-9]*) (. [0-9]+)? ([eE] [+-]? [0-9]+)?`. `Sign (X)` is Negative exactly when X begins with `-`. `Integer (X)` holds when X has no `.`, `e` or `E`.

**`Number_Canonical (X)`** (X-1, S2; statement, to prove):
- **Integers.** `Integer (X)` and X is `0`, or a non-zero digit followed by digits, optionally preceded by `-`, and X is not `-0`. (Python decodes `-0` as the integer zero and encodes it `0`.)
- **Non-integers.** Let `M (X)` be the exact non-negative rational magnitude of X without its sign: the mantissa digits as an integer, times ten to the power (exponent minus the number of fraction digits). Then X is canonical exactly when `X = Repr (Sign (X), Round (M (X)))` and `Round (M (X))` is finite.
  - **`Round (M)`**: the non-negative IEEE binary64 value nearest to M, ties to the even significand, over normal and subnormal values; `+∞` when M ≥ `T_ovf` = 2^1024 − 2^970. A non-finite result is never canonical, because the encoder refuses non-finite values (`allow_nan=False`). **[unverified reasoning, RC-5]**: that the installed decoder rounds exactly so.
  - **The sign is carried separately.** The value is the pair (Sign, `Round (M)`), so a lexeme with `Sign = Negative` and `Round (M) = 0` denotes −0.0. This is the channel the review required: `-0.0` is canonical, `0.0` is canonical, and `-0`, `-0.00` and `-1e-400` are not.
  - **`Repr (S, B)`** is `-` followed by `Repr_Mag (B)` when S is Negative, else `Repr_Mag (B)`.
  - **`Repr_Mag (0)`** is `0.0`.
  - **`Repr_Mag (B)` for B > 0.** Let d1 … dn (d1 ≠ 0, dn ≠ 0) and an integer `decpt` be the shortest digit string such that the decimal value `0.d1…dn × 10^decpt` rounds to B under `Round`; when several strings of that length round to B, the one nearest to B; when two are equally near, the one whose last digit is even **[unverified reasoning, RC-5]**. Then:
    - if −4 < `decpt` ≤ 16 (fixed notation): when `decpt` ≤ 0, `0.` followed by −`decpt` zeros and d1 … dn; when 0 < `decpt` < n, d1 … d`decpt`, `.`, then the remaining digits; when `decpt` ≥ n, d1 … dn, then `decpt` − n zeros, then `.0`;
    - otherwise (exponent notation): d1, then `.` and d2 … dn when n > 1, then `e`, then `+` when `decpt` − 1 ≥ 0 and `-` otherwise, then the decimal digits of |`decpt` − 1|, padded with leading zeros to at least two digits.
  - Examples that follow from these rules: `1e+16`, `1e-05`, `0.0001`, `1000000000000000.0`, `1.5`, `123.0`, `-0.0` are canonical; `1e16`, `1E5`, `1.50`, `0.00001` are not. Each is a V5-M vector, checked against the installed CPython by RC-5.

**Archive extraction.** `extract` returns the exact lexeme span; numbers are compared as lexemes after `Number_Canonical`, never through a binary64 value. `archive_equal` compares a JSON number with an archived number by the same lexical rule (the archive grammar of `rw/operation_capture.py:15-39` stores the canonical text), so the sign of −0.0 survives extraction and comparison.

**Exact thresholds, and why they cost nothing in domain.** Let E be the decimal exponent of X's leading non-zero digit, so that 10^E ≤ M < 10^(E+1). JACKAL (exact, J5-1 … J5-4) gives: 10^309 − `T_ovf` > 0; `T_ovf` − 10^308 > 0; 2^−1075 − 10^−324 > 0; 10^−323 − 2^−1075 > 0. Hence:
- E ≥ 309 ⇒ M ≥ 10^309 > `T_ovf` ⇒ `Round (M) = +∞` ⇒ not canonical, decided without big-integer work;
- E ≤ −325 ⇒ M < 10^−324 < 2^−1075, half the least subnormal ⇒ `Round (M) = 0` ⇒ `Repr` is `0.0` or `-0.0`, which X (having a non-zero digit) is not ⇒ not canonical, decided without big-integer work;
- −324 ≤ E ≤ 308: the exact comparison is computed. Rounding below half the least subnormal to zero, and at or above `T_ovf` to infinity, is IEEE round-to-nearest **[unverified reasoning, RC-5]**.
These shortcuts decide exactly what the exact computation would decide. They refuse nothing that the Python check accepts and accept nothing it refuses.

**Full costs (OPEN, D2 class).** Recognition and extraction are linear in the container length with an explicit stack and no depth cap. `Number_Canonical` on a lexeme of length λ: for −324 ≤ E ≤ 308, big integers whose digit counts are bounded by λ plus the window width set by the thresholds; shortest-digit generation is bounded by the fixed number of significant digits that a binary64 round trip needs **[unverified reasoning, RC-5]**; outside the window, linear in λ.

**What RC-5 must confirm.** The layout constants of `Repr_Mag` (the fixed-notation range −4 < `decpt` ≤ 16, the `.0` suffix, the sign and two-digit padding of the exponent), the tie rule, `T_ovf` = 2^1024 − 2^970 as the overflow threshold and 2^−1075 as half the least subnormal are the author's reading of IEEE 754 binary64 and of CPython's `float.__repr__` and `float ()`; none was read from installed source. RC-5 compares them with the installed CPython on the V5-M vectors. The JACKAL results J5-1 … J5-4 are exact comparisons of those stated constants, not evidence that the constants are the installed ones. The executable big-integer arithmetic falls under the native big-integer correspondence obligation of P1 workstream 4 (no domain cap, no light library); its proof and cost stay OPEN.

---

## V5-D. A faithful accounting alternative, and the full comparison (V4-REQ-D; 02.4, 06.2; D-4a)

Carried: v3 V-D (C3-VD with R4-24, R4-25) and v4 V4-D.1, AO-1 … AO-11 (C4-VD1). v4 V4-D.2's matrix is superseded by V5-D.2; its rows A, B, C, E, F and F′ and its result stand as v4 stated them, and G and the new H are compared in full below.

### V5-D.1 Option H: handler code where the original runs it, workload on the original launch

- **Where the original runs things.** The original daemon runs every handler and the job runner in its own process (`rw/protected_operations.py:750-754`; `rw/runner.py:697-703`), under the daemon service's own limits. Each workload launch is a top-level unit for that request's own reservation, started by `systemd-run` from the daemon with the original properties (NF5-3).
- **H.** A *service-class coordinator* holds store custody for a generation. It is launched by the front through the root helper with the limits read from the installed daemon service (RC-9), not under any request's reservation. It runs every handler and the runner, as the daemon does. Each WL request reserves its own use and its own reservation, and its workload runs on the original `launch_reserved` sequence for that reservation (`rw/protected_scoped_resource_runtime.py:698-769`), unchanged except that the `systemd-run` command of `:760-762` is executed by the root helper on the coordinator's behalf (helper command `LAUNCH_SCOPED`, carrying exactly that argv), because the coordinator cannot reach the manager (M-4). The V3 actor helper, its endpoint and its slot are the original ones.
- **Design deltas H would need if selected** (each designed only on selection, D-4a; listed so the comparison is complete): D-H1, `PREPARED` evidence becomes the coordinator's service launch record instead of a request's RESERVED and `EFFECT_INTENT`; D-H2, a native admission mode for a service-class coordinator (no request binding), in place of `Root_Admission` for a request; D-H3, `LAUNCH_SCOPED` in the v2 helper (V5-E.3 style frame, argv in a sealed memfd); D-H4, a reattach and handoff of the coordinator per generation, as for the root worker; D-H5, the first WL request is an ordinary request of the coordinator.

### V5-D.2 Comparison (no option is selected; replaces v4 V4-D.2)

✓ meets at design level; ✗ fails; "part" as stated. "Original" is the column every option is measured against.

| Aspect (AO) | Original | G: sibling units, handler in the first root's coordinator | H: service-class coordinator, original per-request launch |
|---|---|---|---|
| Kind (AO-2) | `costs[cost_key]` kind of the request's own plan | ✓ | ✓ the same `Cost_Join` per request |
| Grant and use (AO-1) | each request its own grant and use | ✓ | ✓ the coordinator holds no grant or use |
| Owner and requester (AO-3) | bound to the request (C3) | ✓ | ✓ |
| Amount (AO-2) | the catalogue amount, any size, no cap | ✓ | ✓ |
| Plan (AO-2) | the request's plan | ✓ | ✓ |
| Cost key and catalogue (AO-2) | `Cost_Join` | ✓ | ✓ |
| Epoch and rollover (AO-4) | the request row's Reserve, `Record_Launch_Intent`, `Record_Running` guards | ✓ | ✓ on the same commands as the original launch (V5-B.5 WL table) |
| Physical bound (AO-5, AO-6) | the request unit's properties, set once at launch, never raised | ✓ for workload units; ✗ handler code shares the first root unit's admitted bound, so a later request's handler can exhaust a bound admitted for another request | ✓ workload units as original; handler code under the coordinator's service limits, which are read from the installed service and set once (RC-9), as the daemon's are |
| Double count (AO-7) | none | ✓ siblings outside the root counter | ✓ request units are top-level; the coordinator holds no reservation |
| Interference with future capacity (AO-8) | no claim without P-M1 | none, as original | part: as original for workload units; during a generation the coordinator's service-class limits exist beside the front's, so the host's handler-code exposure has one more service-class bound. No protection is claimed |
| Response progress (AO-9) | handlers served concurrently with running jobs (`operation_lock` only around the handler call) | ✓ | ✓ every request is served by the coordinator as the daemon serves it |
| Native cost (AO-10), per WL request | Reserve; S1 pre-effect; `RESERVE_USE` replay; machine admission; `Record_Launch_Intent`; `Record_Running`; GO; `Record_Terminal`; release or charge; `OBSERVE_EFFECT`; `SETTLE_USE` | the original's, plus per child the child decisions of V5-E | the original's exactly; plus, per IP or WL request served while the coordinator owns, the transfer or RELAY joins of V5-I |
| Native and process cost, per generation | none | one root launch with `Root_Admission`, EXECUTION_NATIVE, handoff | one coordinator launch with the D-H2 admission, EXECUTION_NATIVE, handoff |
| Process cost, per WL request | one unit and one V3 actor helper | one unit and one helper | one unit and one V3 actor helper, as original |
| New cap, prerequisite, borrowing, accepted native failure (AO-11) | — | part: handler code can be killed by another request's bound (an accepted native failure) | part: no cap (limits equal the installed service's), no borrowing, no accepted native failure beyond the original's (a coordinator hitting its service limit fails its requests, as a daemon hitting its limit does); adds the service-class launch kind and the RC-9 read |

**Result.** G keeps its handler-enforcement gap (AO-5/AO-6 for handler code, AO-11) and stays unselected. H meets AO-1 … AO-7, AO-9 and AO-10 at design level; AO-8 and AO-11 are "part" for the stated reasons, and its deltas D-H1 … D-H5 are undesigned. H is the faithful alternative offered for the operator's D-4a decision.

**No selection.** No option, mechanism, cap, prerequisite or policy field is selected or added. D-4a (OP-3) decides; it cannot waive AO-1 … AO-11, and until it decides, later WL requests while a worker owns are queued for g+1 (V5-L.2), which is a progress difference that stays OPEN.

---

## V5-E. The child commit protocol, terminal committers, the v2 helper protocol and every surface (V4-REQ-E; 03.2; D-5a, D-5b)

Carried: v3 V-E (C3-VE with R4-26 … R4-28, R4-54, R4-59 … R4-64, inside C4-B) as replaced by R5-4, R5-6 and R5-11; v4 V4-E.4 (C4-VE4). V5-E replaces v4 V4-E.1 … V4-E.3.

### V5-E.1 `Child_Event_Legal`: one consistent protocol (X-7, spec S12)

Events are scoped observation-journal events under the child reservation, plus the child row's scoped commits. Alternative set `CHILD (t)` = {`CHILD_READY`, `CHILD_ABORT`}: exactly one commits.

| Event (step) | Predecessor for task t | Writer (phase of the generation's root) | Native decision | Command after durable commit |
|---|---|---|---|---|
| `TASK_INTENT` (E1) | none | Worker (WORKER_OWNED, ORIGINAL_RESULT) | — | — |
| child Reserve (E2) | `TASK_INTENT` | Worker (same) | `Task_Admission` / `_V2` | — |
| child `Record_Launch_Intent` (E3) | E2 | Worker (same) | `Check` / `Check_V2` with the scope and universe guard | — |
| `CHILD_DISPATCH_INTENT` (E3) | E3 commit | Worker (same) | — | `CREATE_CHILD` |
| `CHILD_HELD` (E5) | `CHILD_DISPATCH_INTENT` | Worker, from `HELD_CHILD` | ticket echo (P11) | — |
| child `Record_Running` (E6) | `CHILD_HELD` | Worker (same) | `Check_V2`: Live | — |
| `CHILD_GO_INTENT` (E7) | E6 commit | Worker (same) | machine admission | `GO_FORK` |
| `CHILD_MEASURED` (E8) | `CHILD_GO_INTENT` | Worker, from `MEASURED_CHILD` | — | — |
| `CHILD_CANDIDATE` (E9) | `CHILD_MEASURED` | Worker (same) | `Decide` / `Decide_V2` in the worker; the record holds the material digest m and the worker's decision; it authorizes nothing | `COMMIT_CHILD_REQUEST` (m) |
| `CHILD_AGREED` or `CHILD_REFUSED` (E9) | `CHILD_CANDIDATE` | Worker, recording the sub-helper's `AGREE_CHILD` or `REFUSE_CHILD` frame bytes | `Decide` / `Decide_V2` in the sub-helper, on m | — |
| `CHILD_READY` (E10) | `CHILD_AGREED` on the same m, with both decisions `Child_Ready_Conjunction`; `CHILD (t)` free | Worker (same) | — | `COMMIT_CHILD_GO` (m, READY id) |
| `CHILD_ABORT (cause)` (E10) | any event from `CHILD_DISPATCH_INTENT` on, with `CHILD (t)` free | the generation's current owner (below) | — | `ABORT_CHILD` when a sub-helper channel exists |
| `ACTOR_STDIN_*` (E11) | `CHILD_READY` | Worker (same) | — | — |
| `CHILD_CLOSED` (E12) | `CHILD_DISPATCH_INTENT` or later | the current owner, from `CLOSED_CHILD … ECHILD` | — | `ACK_CLOSED` |
| child `Record_Terminal`, release or charge | `CHILD_CLOSED` | the current owner | `Check_V2`: Reaped | — |
| `CHILD_UNKNOWN (cause)` | any from `CHILD_DISPATCH_INTENT` on | the current owner | — | holds retained |

- **No READY before agreement.** `CHILD_READY` needs a committed `CHILD_AGREED` on the same m, so the sub-helper's native decision always precedes the authorizing record, and an ABORT can never follow a READY (the alternative set is taken). A worker decision other than `Child_Ready_Conjunction`, a `CHILD_REFUSED`, a binding mismatch or a lost channel leads to `CHILD_ABORT` only.
- **No exec before READY.** The sub-helper sends the actor's commit ACK only on a `COMMIT_CHILD_GO` whose m equals the material it agreed to and which names a READY event id; otherwise, or on channel loss, it kills init (as the V1 helper does on loss before GO, `native_root_worker_supervisor_v1.c:352-353`). A READY whose GO was lost therefore ends with init killed and no exec; closure evidence then decides the row (Reaped or Unknown).
- **Current owner, for the terminal events** (`CHILD_ABORT`, `CHILD_CLOSED`, terminal commits, `CHILD_UNKNOWN`): the Worker while the root is WORKER_OWNED … WORKER_RELINQUISH; the Collector from `CUSTODY_RETURNED (g)` and in the physical phases of g after it; the Reconciler while the root is UNKNOWN, on authentic evidence. The launch-path events E1 … E11 stay the Worker's only. This replaces v4's blanket WORKER_OWNED condition.
- **Failures.** Before E7, as the V1 helper. Without `CLOSED_CHILD … ECHILD` the row cannot classify `Reaped` (`core/resource_observation_classification.ads:108-114`): `Unknown`, holds retained. Root settlement waits for every child (CD-9).

### V5-E.2 Every process surface (replaces v4 V4-E.2)

"CLOEXEC" means every other descriptor is close-on-exec; "held" lists what the process keeps open.

| Process | Launched by | argv | env | cwd | Credentials and privilege | Descriptors |
|---|---|---|---|---|---|---|
| Root helper v2 (unit main process; D-5b) | the original root launch, `systemd-run` with `Type=exec`, `RemainAfterExit=yes`, `Delegate=no`, `User=root`, `Group=root` and the plan's properties (`rw/protected_root_resource.py:67-71`) | V1's: endpoint, ticket, `0`, `0`, cwd, `--env` triples, `--`, the coordinator argv (`native_root_worker_supervisor_v1.c:307-322`); v2 adds `--library <path> <sha256>` before `--`, both from the crosswalk's `decision_library_sha256` entry (V5-E.3) | the unit's environment, as V1 | the unit's, as V1 | uid and gid 0 with the unit's full capability set, as V1; no reduction, because the helper is the privileged component | 0, 1, 2 from the manager; created CLOEXEC: the owner socket, go, report, out, err, actor-credential socketpair, actor stdin pipe, custody socketpair (V1, `:323-335`), and (v2) the command socketpair. After HELD, held: owner socket, go write end, report read end, init pidfd until waited, command socketpair end, one channel per sub-helper |
| Coordinator (worker) | the root helper's namespace init, after GO and the commit (V1 order) | plan-v1's `handler_plan` argv, then the custody-channel number (V1, `:289-290`), then (v2) the command-channel number | cleared, then plan-v1's `environment`, which is empty (`rw/root_worker_plan.py:37`) | `paths.state` | euid 0; capabilities, `no_new_privs` and seccomp of C4-VE4 | at exec exactly: 0 stdin read end, 1 and 2 output write ends, the custody channel, the command channel; received later by `SCM_RIGHTS` with close-on-exec set on receipt (K-26): the custody roster, client sockets after intake, slot descriptors after `DRAIN_INTAKE` |
| Sub-helper (one per child) | a fork of the root helper, outside the coordinator's namespaces; no exec | — | inherited | inherited | root, as the helper | held: its channel to the root helper; the child init's pidfd; go write end; report read end; the actor-credential receiving end with `SO_PASSCRED`; out, err and stdin-writer until sent in `HELD_CHILD`, then closed; the decision library mapped read-only from the descriptor it hashed (V5-E.3) |
| Child init | the sub-helper, after `unshare (CLONE_NEWPID)`; it unshares `CLONE_NEWNS`, makes mounts private and mounts proc (the V3 pattern, `native_namespace_supervisor_v3.c:277-290`) | — (fork) | inherited | inherited | PID 1 of the child namespace, root | before GO: go read end, report write end, out and err write ends, actor-credential sending end, stdin read end; after forking the actor it closes all but the report write end (V1 `:293-294`) |
| Actor | child init, after GO and the commit | the original workload argv from `TASK_INTENT` (`native_namespace_supervisor_v3.c:305`) | cleared, then the captured `--env` triples (`:302-304`) | the captured cwd (`:302`) | the workload uid and gid, never 0 (`:300`, `:336`) | exactly 0 (stdin read end), 1 and 2 (output write ends) (`:297-299`) |

**Original handler facilities (RC-6 rule, carried from C4-VE4).** An item is dropped from the coordinator only when RC-6 shows the original handler does not use it; an item it uses is kept with its justification. v5 adds no reduction beyond C4-VE4's.

### V5-E.3 The v2 helper protocol, frame by frame (replaces v4 V4-E.3)

**Framing.** The command channel is a `SOCK_SEQPACKET` socketpair, one message per frame, as V1's owner channel. A frame is ASCII text: `WL-ROOT-WORKER-SUPERVISOR-v2\n`, the verb, `\n`, then its fields, each followed by `\n`. Field forms: ticket and every digest, 64 lowercase hex; integers, canonical decimal; unit and leaf names, `[A-Za-z0-9_.@:-]+` under the boundary's prefix; byte strings, lowercase hex. **Every variable-length payload** (argv, env, cwd, decision material, credential frame, unit properties) travels as a sealed `memfd` passed by `SCM_RIGHTS` with `F_SEAL_WRITE`, `F_SEAL_SHRINK` and `F_SEAL_GROW` set (K-26), named in the frame by its length and sha256, so no frame or payload has a size cap beyond what the kernel holds.

| Direction | Verb | Fields (in order) | Descriptors | The helper's validation |
|---|---|---|---|---|
| Worker → helper | `CREATE_CHILD` | ticket, task id, child reservation, leaf name, uid, gid, payload length, payload sha256, delegation record digest | payload memfd (cwd, env triples, argv, limits from the crosswalk child plan) | leaf under the boundary; limits within the boundary's remaining ceiling; uid and gid not 0; ticket fresh |
| Helper → worker | `HELD_CHILD` | ticket, init pid, leaf cgroup (hex) | namespace, pidfd, out, err, stdin writer | — |
| Worker → helper | `GO_FORK` | ticket | — | ticket of a held child |
| Helper → worker | `MEASURED_CHILD` | ticket, frame length, frame sha256, actor host pid | frame memfd (the exact credential frame bytes received with `SO_PASSCRED`) | — |
| Worker → helper | `COMMIT_CHILD_REQUEST` | ticket, material length, material sha256 m | material memfd | ticket of a measured child; m equals the memfd's sha256 |
| Helper → worker | `AGREE_CHILD` | ticket, m, `CHILD_READY_CONJUNCTION`, decision library sha256 | — | sent only after the sub-helper's bindings and native decision (below) |
| Helper → worker | `REFUSE_CHILD` | ticket, m, reason (binding name or decision name) | — | init already killed |
| Worker → helper | `COMMIT_CHILD_GO` | ticket, m, `CHILD_READY` event id | — | m equals the agreed m; then the actor's commit ACK |
| Worker → helper | `ABORT_CHILD` | ticket, cause | — | kill init |
| Helper → worker | `CLOSED_CHILD` | ticket, init pid, main status, `ECHILD`, exec released (0 or 1) | — | — |
| Worker → helper | `ACK_CLOSED` | ticket | — | the child's `CLOSED_CHILD` was sent |
| Worker → helper | `OBSERVE_UNIT`, `STOP_UNIT`, `RESET_UNIT` | unit, and for `STOP_UNIT` a cause | — | unit under the boundary; `RESET_UNIT` only after the child's `CLOSED_CHILD` |
| Helper → worker | `UNIT_OBSERVED`, `UNIT_STOPPED`, `UNIT_RESET` | unit, return code, output length and sha256 | output memfd | — |

**The sub-helper's bindings and decision** (before `AGREE_CHILD`):
1. **Ticket** equals the ticket journaled in `CHILD_DISPATCH_INTENT` and echoed in `HELD_CHILD` (P11). The ticket is `SHA-256 (canonical ({row, task, generation, launch_head}))`, the original root ticket's construction applied to the child (`rw/protected_root_resource.py:65-66`).
2. **Measurement.** The material's actor-observation records equal, byte for byte, the records the sub-helper builds from the credential frame it received.
3. **Ancestry.** The material's process and namespace ancestry equal what the sub-helper observed: init's pid and namespace identity, the leaf cgroup the helper created, and the actor's host pid **[unverified reasoning, K-4]**.
4. **Library (ABI and source).** The sub-helper opens the `--library` path with `O_RDONLY | O_NOFOLLOW`, copies its bytes into a new `memfd`, seals it (`F_SEAL_WRITE`, `F_SEAL_SHRINK`, `F_SEAL_GROW`), hashes the sealed copy, requires the hash to equal the argv's sha256, and loads it through `/proc/self/fd/N`, so the loaded bytes are exactly the hashed bytes and cannot change afterwards **[unverified reasoning, K-27]**. It checks `wl_resource_child_execution_version_v1` (or `_v2`) and every layout entry exactly as the Python wrapper does (`rw/resource_child_execution.py:111-121`).
5. **Decision.** The material is the exact argument memory the worker passed to its own `decide`: the arena bytes and each record array, in the export's `PARAMETERS` order (`rw/resource_child_execution.py:207`), with counts and strides. The sub-helper rebuilds the pointers and calls `decide` in mode `CHILD_ADMISSION`. Only `Child_Ready_Conjunction` gives `AGREE_CHILD`.

**Native cost (OPEN, OB-048 class).** One more `decide` per child, of the same cost class as the worker's; one SHA-256 of the library per sub-helper; linear frame parsing. The C bodies are unproved native code. The library identity binds the bytes; it does not prove what they compute.

**Non-claim.** The ledger-state parts of the material come from the custody owner's store; a compromised coordinator could misstate them, as it already holds the store.

### V5-E.4

Carried as v4 V4-E.4 (C4-VE4).

---

## V5-F. Three orthogonal relations, the barrier, the handoff abort and pending intents (V4-REQ-F; 04.1, 04.3, 07.1, 07.3; D-2a, D-6a, D-9a)

Carried: the O mapping and the O×U table (C3-VF1, with R5-5) and INV-C1 … INV-C5 (v2 lines 1004-1010, INV-C4 as R4-47's INV-C4′). Withdrawn: C2-62's root graph (W5-1). V5-F replaces v4 V4-F; the DDL is V5-J.2.

### V5-F.1 Types (additive SPARK unit `Worldline.Root_Custody_Phase`, spec S9; DESIGN)

```ada
type Actor            is (Front, Worker, Collector, Reconciler);
type Owner            is (Front, Worker, Collector, Reconciler, None);
type Root_Phase       is (Front_Owned, Prepared, Held, Running, Execution_Native, Execution_Ack,
                          Handoff_Intent, Front_Close_Intent, Front_Closed, Transfer_Sent,
                          Roster_Evidence, Worker_Owned, Original_Result, Handler_Terminal,
                          Worker_Relinquish, Abandoned, Front_Retained_Escrow, Handoff_Aborted,
                          Custody_Returned, Historical_Settlement, Front_Reconstruction,
                          Ended, Unknown);
type Abort_Class      is (Never_Dispatched, Dispatched);
type Request_Phase    is (Queued, Transfer_Intent, Intake, Abandoned, Responded, Lost);
type Descriptor_Phase is (Front_Held, Stop_Intent, Frozen, Ofd_Evidence, Intake, Abandoned,
                          Released, Reclaimed);
type Transfer_Mode    is (None, Fresh, Relay);
type Physical_Flags is record
   Launched, NS, Outer, Raw, Witness, Settled, Released_Unlaunched : Boolean;
end record;
type Root_State is record
   Generation     : Q.Quantity;            -- arbitrary precision; stored losslessly (V5-J.2)
   Operation      : L.Identity;            -- the WL operation that started the generation; empty for g with no root
   Phase          : Root_Phase;
   Before_Unknown : Root_Phase;            -- meaningful only when Phase = Unknown
   Owners_Open    : Boolean;               -- the front's store, journals and leases are open
   Abort          : Abort_Class;           -- meaningful only from Handoff_Aborted
   Physical       : Physical_Flags;        -- the root unit of g, independent of custody
   Unknown_Cause  : Optional_Digest;
   Reattach_Epoch : Q.Quantity;            -- incremented by WORKER_REATTACHED
   Head           : Digest;
end record;
type Subject_State is record
   Kind          : Subject_Kind;           -- Request or Descriptor
   Generation    : Q.Quantity;
   Subject       : L.Identity;
   Subgeneration : Q.Quantity;
   Request       : Request_Phase;          -- meaningful when Kind = Request
   Descriptor    : Descriptor_Phase;       -- meaningful when Kind = Descriptor
   Mode          : Transfer_Mode;
   Position      : Q.Optional_Quantity;    -- P (readers) or W (stdin)
   Carried_From  : Q.Optional_Quantity;    -- the generation a queued request came from
   Head          : Digest;
end record;
```

`Status` is `Ready` or a named refusal: `Wrong_Generation`, `Wrong_Actor`, `Illegal_Root_Transition`, `Illegal_Request_Transition`, `Illegal_Descriptor_Transition`, `Cross_Condition`, `Alternative_Taken`, `Evidence_Missing`, `Join_Not_Ready`, `Subject_Unknown`, `Barrier_Subjects_Open`. A refused actor does not act. v4's `Stop_Intent` field and `ROOT_STOP_INTENT` event are withdrawn with M8 (c).

### V5-F.2 The root relation (replaces C2-62's graph, W5-1)

Each row: phase before, event, phase after, the only actor that may append it, and the native evidence `Legal` reads. "Physical events" do not change `Phase`; they are in the separate table below.

| From | Event | To | Actor | Native evidence |
|---|---|---|---|---|
| Front_Owned (g) | `PREPARED (g)` | Prepared | Front | a WL operation's RESERVED and `EFFECT_INTENT` heads (V5-B.5); no other operation starts a root |
| Prepared | `HELD` | Held | Front | authentic HELD frame; machine admission at DISPATCH; sets `Launched` |
| Held | `RUNNING` | Running | Front | `RECORD_RUNNING` committed |
| Running | `EXECUTION_NATIVE` | Execution_Native | Front | `ROOT_READY_CONJUNCTION` retained |
| Execution_Native | `EXECUTION_ACK` | Execution_Ack | Front | before-exec witness and exec ACK |
| Execution_Ack | `HANDOFF_INTENT` | Handoff_Intent | Front | custody frame intent |
| Handoff_Intent | `FRONT_CLOSE_INTENT` | Front_Close_Intent | Front | no background owner; acquisitions quiescent |
| Front_Close_Intent | `FRONT_CLOSED` | Front_Closed; `Owners_Open` false | Front | owners closed; seed taken after close and after every retention append (v2 §6.4) |
| Front_Closed | `TRANSFER_SENT` | Transfer_Sent | Front | every descriptor sent; ACK set free |
| Transfer_Sent | `ROSTER_EVIDENCE` | Roster_Evidence | Front | OFD evidence of the root roster (v3 V-H.2 H4) |
| Transfer_Sent or Roster_Evidence | `CUSTODY_ACK` | Worker_Owned | Worker | `Root_Admission_Join` = Ready (V5-I.1); seed equals current under the transferred OFDs; ACK set free |
| Transfer_Sent or Roster_Evidence | `ABANDON` | Abandoned | Front or Reconciler | ACK set free |
| Abandoned | `FRONT_RETAINED_ESCROW` | Front_Retained_Escrow | Front | the escrow holds the roster; the worker may now be stopped (R5-8) |
| Prepared … Front_Closed | `HANDOFF_ABORT (class)` | Handoff_Aborted | Front | ACK set free; no `TRANSFER_SENT (g)`; class `Never_Dispatched` needs launch journal `Never_Dispatched` and native class `Never_Launched`; otherwise class `Dispatched` |
| Worker_Owned | `ORIGINAL_RESULT` | Original_Result | Worker | original result captured once (CD-8) |
| Original_Result | `HANDLER_TERMINAL` | Handler_Terminal | Worker | final capture |
| Handler_Terminal | `WORKER_RELINQUISH` | Worker_Relinquish | Worker | owners closed; native root material retained |
| Worker_Owned … Worker_Relinquish | `WORKER_REATTACHED (n)` | unchanged; `Reattach_Epoch` = n | Worker | the handshake of V5-L.3: n is the current epoch + 1, and the front's MAC verifies |
| Worker_Owned … Worker_Relinquish, Front_Retained_Escrow, or Unknown with `Before_Unknown` in those | `CUSTODY_RETURNED` | Custody_Returned | Collector or Reconciler | the worker pidfd terminal **and** the root namespace-init pidfd terminal (K-24), both held by the front since HELD; no request or descriptor subject of g in Intake (XC-6) |
| Custody_Returned | `HISTORICAL_SETTLEMENT` | Historical_Settlement | Collector | the U decision of V5-G.4 committed in the operation journal |
| Handoff_Aborted | `HISTORICAL_SETTLEMENT` | Historical_Settlement | Front when `Owners_Open`, else Collector | the original exception path's U record (`QUARANTINED`, or SETTLED or RELEASED left as is, `rw/protected_operations.py:770-772`); for `Never_Dispatched`, `Release_Hold` committed |
| Historical_Settlement with `Owners_Open` false | `FRONT_RECONSTRUCTION` | Front_Reconstruction | Collector | fresh owners built through the v2 startup path with the escrow claim, or with the front's own lease descriptors when nothing was sent |
| Front_Reconstruction, or Historical_Settlement with `Owners_Open` | `FRONT_OWNED (g+1)` | g: Ended; g+1: Front_Owned | Front | creates generation g+1; carries every Queued or Abandoned request of g (`Carried_From` = g) |
| any phase except Ended | `UNKNOWN (cause)` | Unknown; `Before_Unknown` set | the phase owner or the Reconciler | the cause record |
| Unknown | `RECONCILED`, then the event that native evidence determines | that event's target | Reconciler only (INV-C5) | authentic durable evidence; never EOF or a deadline alone |

**Physical events of g's root unit** (independent of `Phase`; legal in any phase from `Launched`, including after g is Ended):

| Event | Flag set | Actor | Native evidence |
|---|---|---|---|
| `CLOSED_NS` | NS | the physical owner: Front while `Owners_Open` or in Abandoned, Front_Retained_Escrow or Handoff_Aborted; otherwise Collector | the helper's `CLOSED … ECHILD` frame with the dispatch ticket and HELD init pid, waited status, namespace pidfd terminal, then `'A'` (`rw/protected_root_supervisor.py:177-207`) |
| `CLOSED_OUTER` | Outer | as above | after NS: the helper pidfd terminal, the launcher's `wait ()` returned, `MainPID = 0` (R4-30; `:218-227`) |
| `CLOSED_RAW` | Raw | as above | every raw drain complete and fsynced (`:251`, `:260-269`) |
| `CLOSED_WITNESS` | Witness | as above | NS, Outer and Raw set; native `REAPED` and `CONSISTENT_SNAPSHOT`; **barrier XC-5**: no request or descriptor subject of g is in Transfer_Intent, Intake, Stop_Intent, Frozen or Ofd_Evidence |
| `PHYSICAL_SETTLED` | Settled | as above | Witness set; native `Record_Terminal` and `Release_Hold` or `Charge_Budget` committed (CD-5, INV-C4′) |
| (no event) | `Released_Unlaunched` | Front | set by `HANDOFF_ABORT (Never_Dispatched)` with its `Release_Hold`; no CLOSED event is needed or legal |

**Owner function** `Owner_Root (S)`, used by every mutation gate:

| Phase of the current generation | Store and journal owner |
|---|---|
| Front_Owned … Front_Close_Intent, and Handoff_Aborted or Historical_Settlement with `Owners_Open` | Front |
| Front_Closed, Transfer_Sent, Roster_Evidence, Abandoned, Front_Retained_Escrow, and Handoff_Aborted without `Owners_Open` | None (nobody mutates the store) |
| Worker_Owned … Worker_Relinquish | Worker |
| Custody_Returned, Historical_Settlement without `Owners_Open`, Front_Reconstruction | Collector |
| Unknown | Reconciler, only for the original startup branches and evidence-determined events |

### V5-F.3 The request and descriptor relations, and the cross-conditions

**Request relation** (per generation g and request r; alternative set `REQUEST (g, r, s)` = {`REQUEST_INTAKE`, `REQUEST_ABANDON`}):

| From | Event | To | Actor | Native evidence |
|---|---|---|---|---|
| no row | `REQUEST_QUEUED (r, 0)` | Queued | Front | the raw request and its original observation; XC-1 |
| Queued, or Abandoned at s | `REQUEST_TRANSFER_INTENT (r, s′, mode)` | Transfer_Intent | Front | XC-2; s′ = 0 from Queued, s + 1 from Abandoned; FRESH needs the socket roster, RELAY the reachable channel at the current `Reattach_Epoch` |
| Transfer_Intent | `REQUEST_INTAKE (r, s)` | Intake | Worker | XC-3; `Transfer_Join` (FRESH) or `Relay_Join` (RELAY) = Ready over the `REQUEST_TRANSFER_INTENT (r, s)` head |
| Transfer_Intent | `REQUEST_ABANDON (r, s)` | Abandoned | Front or Reconciler | set free |
| Intake | `REQUEST_RESPONDED (r, s)` | Responded | Worker | the response digest; for RELAY the front writes exactly those bytes afterwards (M5) |
| Intake | `REQUEST_LOST (r, s)` | Lost | Collector | XC-4 |
| Queued in a generation whose root owner is Front | `REQUEST_RESPONDED (r, 0)` | Responded | Front | served by the front under the original gate; XC-1 |

**Descriptor relation** (per g and descriptor d; alternative set `DRAIN (g, d, s)` = {`DRAIN_INTAKE`, `DRAIN_ABANDON`}):

| From | Event | To | Actor | Native evidence |
|---|---|---|---|---|
| no row, or Front_Held | `DRAIN_STOP_INTENT (d, s)` | Stop_Intent | Front | XC-2; d in the front's LIVE roster; the open read or write interval |
| Stop_Intent | `DRAIN_FREEZE (d, s)` | Frozen | Front | spool fsync and `DISARMED (P)`, or durable W with the write interval closed |
| Frozen | `DRAIN_OFD_EVIDENCE (d, s)` | Ofd_Evidence | Front | `kcmp` and lock evidence after SEND (V5-H.3) |
| Ofd_Evidence | `DRAIN_INTAKE (d, s)` | Intake | Worker | XC-3; the evidence matches the worker's report |
| Stop_Intent, Frozen or Ofd_Evidence | `DRAIN_ABANDON (d, s)` | Front_Held at s + 1 | Front or Reconciler | set free |
| Intake | `DRAIN_RELEASED (d, s)` | Released | Front | the front closed its active copy |
| Intake or Released | `DRAIN_RECLAIMED (d, s)` | Reclaimed | Collector or Reconciler | XC-4 |

**Cross-conditions** (the only places the three relations meet; each is a conjunct of `Legal` for the named rows):
- **XC-1** (queue and front service). `REQUEST_QUEUED` needs a root phase in which the front does not serve the request itself: anything but Front_Owned with `Owners_Open`. A front-served `REQUEST_RESPONDED (r, 0)` needs `Owner_Root` = Front in the request's generation.
- **XC-2** (transfer). `REQUEST_TRANSFER_INTENT` and `DRAIN_STOP_INTENT` need the root phase Worker_Owned, Original_Result or Handler_Terminal, with `Owner_Root` = Worker.
- **XC-3** (intake). `REQUEST_INTAKE` and `DRAIN_INTAKE` need `CUSTODY_ACK (g)` committed and the root phase still in Worker_Owned … Worker_Relinquish.
- **XC-4** (loss and reclaim). `REQUEST_LOST` and `DRAIN_RECLAIMED` need the worker pidfd terminal.
- **XC-5** (closure barrier; v4's r6, now a check). `CLOSED_WITNESS (g)` needs no request in Transfer_Intent or Intake and no descriptor in Stop_Intent, Frozen, Ofd_Evidence or Intake, in g.
- **XC-6** (custody return). `CUSTODY_RETURNED (g)` needs XC-5's subject condition, which the Collector reaches by `REQUEST_LOST`, `REQUEST_ABANDON` and `DRAIN_RECLAIMED` first.
- **XC-7** (generation). An event's generation is the current generation, except physical events of an Ended generation, `REQUEST_LOST`, `DRAIN_RECLAIMED` and `REQUEST_ABANDON` of g before `CUSTODY_RETURNED (g)`, and the creation events `FRONT_OWNED (g+1)` and the carried `REQUEST_QUEUED`.

**C×P rules** (replace v4's r1 … r6):
- **r1′.** While the root phase is Front_*, Prepared or Handoff_Aborted, non-root rows may be in any P phase. The root row is RESERVED or LAUNCH_INTENT before `Launched`; it is RELEASED before `Launched` only with `Released_Unlaunched` (that is, by `HANDOFF_ABORT (Never_Dispatched)` and the original `Release_Hold`); it is RUNNING from RUNNING onwards.
- **r2.** While the root is Worker_Owned … Worker_Relinquish, the root row is RUNNING or TERMINATING, and child rows follow `Parent_Supports`.
- **r3′.** Unchanged (INV-C4′): before `Witness`, a possibly launched root row (a present `Dispatch` fact) is never RELEASED or CHARGED.
- **r4.** While the root is Unknown or Custody_Returned without `Settled`, rows are retained or SETTLEMENT_UNKNOWN, never released. A stop changes no row.
- **r5′.** Request and descriptor phases other than Queued and Front_Held exist only under XC-2 … XC-4.
- **r6′** is XC-5, a precondition of `CLOSED_WITNESS`, not an invariant asserted elsewhere.

### V5-F.4 `Next`, per relation

- **Root.** `Next` sets the row's phase and the derived owner (`Owner_Root`), sets `Head` to the event id, sets `Owners_Open` false at `FRONT_CLOSED` and true at `FRONT_OWNED (g+1)`, records `Abort` at `HANDOFF_ABORT`, sets `Before_Unknown` at `UNKNOWN`, increments `Reattach_Epoch` at `WORKER_REATTACHED`, and sets physical flags at physical events. At `FRONT_OWNED (g+1)` it marks g Ended and creates g+1 = g + 1 (native big-integer successor, written to `out_arena`) in Front_Owned with `Owners_Open` true, zero `Reattach_Epoch` and no physical flags.
- **Request.** Sets the phase, sub-generation (s + 1 on a transfer intent from Abandoned), mode and head. At `FRONT_OWNED (g+1)` every Queued or Abandoned request of g is re-created in g+1 as Queued at sub-generation 0 with `Carried_From` = g, and g's row stays as history.
- **Descriptor.** Sets the phase, sub-generation (s + 1 on `DRAIN_ABANDON`), `Position` from `DRAIN_FREEZE`, and head.
- **Fold.** The state rows of V5-J.2 hold exactly `Next` folded over the chain from S0, in chain order (V5-J.3).

### V5-F.5 `Mutation_Allowed`: every actual mutation (replaces v4 V4-F.5)

On a v1 deployment there is no custody state, and every mutation keeps its original behaviour. On a v2 deployment each mutation is gated at one choke point, with the operands of X-5 (V5-A.3):

| Id | Mutation (choke point) | Allowed when | Actor |
|---|---|---|---|
| M1 | operation-journal append (`OperationJournal.append`, `rw/protected_operations.py:230`) | the caller is `Owner_Root` of the current generation; or the Collector, for the root operation's settlement and quarantine appends of g, from Custody_Returned on | as stated |
| M2 | scoped-ledger commit (`ScopedRunLedgerService`, `rw/protected_scoped_resource_service.py:56`) | the M1 rule; the Collector also for `Record_Terminal`, `Release_Hold`, `Charge_Budget` and `Retain_Uncertain` of g's rows and its children's, in g's physical events | as stated |
| M3 | store mutation (`rw/store.py` writers) | `Owner_Root` is Front or Worker, and the caller is it | Front or Worker |
| M4 | custody append (`RootCustodyJournal.append`, `rw/root_worker_journal.py:123`) | `Legal (S, E) = Ready` with `E.Actor` the caller | per row |
| M5 | client response write | FRESH: the intaking worker after `REQUEST_INTAKE`; RELAY: the front, after the worker's `REQUEST_RESPONDED`, only those bytes; front-served: the front | Worker or Front |
| M6 | slot read and spool | Front in Front_Held and in Stop_Intent until FREEZE (H1); Worker from Intake; Collector or Reconciler in Reclaimed; nobody in Frozen or Ofd_Evidence | as stated |
| M7 | stdin write | Front in Front_Held until its stop flag; Worker from Intake; nobody after a crash inside an open write-armed interval | as stated |
| M8 | unit stop or kill | **(a)** the store-custody owner, in the original paths: failure capture (`retain_and_stop_unknown`, `rw/protected_root_supervisor.py:346-362`; the V3 slot's `capture_owned_failure` → `stop_owned_transport`, `rw/protected_scoped_supervisor_v3.py:286-306`, `:434`) and the original `job.cancel` handler (`rw/controller.py:811-826`) through `runner.cancel`, which in the worker reaches the dispatcher's `STOP_UNIT` (V5-B.6). For g's root in the handoff window: before `TRANSFER_SENT (g)` only after `HANDOFF_ABORT (g)`, and after it only after `ABANDON (g)` (R5-8). **(b)** the helper's and sub-helper's own kill of init on channel loss before GO or before `COMMIT_CHILD_GO`, and on `ABORT_CHILD`. **(c) withdrawn.** v4's front stop of the generation root on `job.cancel` is withdrawn: the original command's world resolution, active-job set, error cases, runner cancelled-set and response are all functions of the store and the runner of the custody owner (NF5-6), and a front that does not own the store cannot establish them. Never on EOF, a deadline or the reconciler's own initiative. A stop never settles, releases or relabels anything. | as stated |
| M9 | helper command | Worker in Worker_Owned … Worker_Relinquish of its generation; Front in Front_* for its own root helper (original), and for `ACK_CLOSED` | Worker or Front |
| M10 | unit reset | after `CLOSED_WITNESS` (C2-68) | Collector |
| M11 | escrow claim | Front_Reconstruction | Collector |

**Lemma OWN-1** (statement, to prove over the relation): `Owner_Root` can change away from an actor only by an event that actor appends, or by `CUSTODY_RETURNED`, `ABANDON` or a Reconciler event, each of which needs evidence that the actor cannot act (its pidfds terminal) or has never owned (no `CUSTODY_ACK`). So a choke point that read the owner in one custody transaction cannot be overtaken by a concurrent change that would make its mutation illegal. **Choke-point audit AU-1** stays OPEN as in v4.

### V5-F.6 CAS, replay and joins

`append (expected, proposed)` runs in one `BEGIN IMMEDIATE` with `synchronous=FULL` and `foreign_keys=ON`:
1. **Load.** X-4 over the chain (V5-J.3), and X-5 `fold` equal to the stored rows.
2. **Replay identity** (generation, operation, subject_kind, subject, sub-generation, kind, record digest), compared with the lossless encodings of V5-J.2. An existing event with that identity is returned unchanged: no second mutation and no action.
3. **Alternative join.** For `CUSTODY_ACK`, `ABANDON`, `HANDOFF_ABORT` (set ACK), `REQUEST_INTAKE`, `REQUEST_ABANDON` (set REQUEST) and `DRAIN_INTAKE`, `DRAIN_ABANDON` (set DRAIN), the `alternatives` row keyed by (generation, operation, subject_kind, subject, sub-generation, set) must be free or hold this kind; otherwise `CUSTODY_ALTERNATIVE_TAKEN`, and the loser does not act.
4. **CAS join.** The root row of the event's generation, and the subject row when the event has a subject, must equal `expected` (head, phase, sub-generation, `Owners_Open`, `Reattach_Epoch`); otherwise `CUSTODY_CAS_STALE`, and the caller re-reads and re-decides.
5. **Generation join.** XC-7.
6. **Initial-state join.** With no `root_state` row the state is S0 (V5-J.3): generation 1, Front_Owned, `Owners_Open`, no subjects. Then only `PREPARED (1)` is legal, because XC-1 forbids queueing while the front serves.
7. **Decide.** `Legal = Ready`; compute `Next`.
8. **Write** the event, the `alternatives` row and the new or changed state rows; update the head (EVENT) and its MAC.
9. **Read back,** re-verify (X-4) and re-fold (X-5), then commit.

### V5-F.7 Committed intents whose effect or response is pending

At every startup, after the chain is verified and before the endpoint, the Reconciler lists every committed intent whose effect is not yet recorded and acts on it. Each action is idempotent, and each completion is recorded by its own event.

| Committed intent | Pending effect or response | Detected by | Action at restart | Actor |
|---|---|---|---|---|
| `PREPARED`, `HELD`, `RUNNING`, `EXECUTION_*` with no later root event, front restarted | the launch's next step | root phase Prepared … Execution_Ack and the front's process gone | the original pre-handoff failure route: `HANDOFF_ABORT (class)` by the restarted front, then the original failure stop and quarantine (R5-8, V5-G.1) | Front |
| `HANDOFF_INTENT`, `FRONT_CLOSE_INTENT`, `FRONT_CLOSED` | the transfer | phase in that range, nothing sent | `HANDOFF_ABORT (Dispatched)`; owners reopened by `FRONT_RECONSTRUCTION` with the front's own lease descriptors | Front, then Collector |
| `TRANSFER_SENT` or `ROSTER_EVIDENCE` without ACK | the worker's decision | ACK set free | `ABANDON (g)` by the Reconciler (RT-9) | Reconciler |
| `HANDOFF_ABORT` without its U record or stop | the original failure stop and quarantine | no `HISTORICAL_SETTLEMENT` after it | run `retain_and_stop_unknown`'s stop again (idempotent `systemctl stop`) and the original `quarantine (operation, cause)`; for `Never_Dispatched`, `Release_Hold` replayed through the native replay | Front or Collector |
| `REQUEST_TRANSFER_INTENT` without intake | the transfer | REQUEST set free | `REQUEST_ABANDON (r, s)`; the request is offered at s + 1 when a reachable worker owns, else stays queued (RT-20 as R4-33) | Front or Reconciler |
| `REQUEST_INTAKE` without `REQUEST_RESPONDED`, worker alive | the response | phase Intake | none: the worker owns it and answers; for RELAY the reattached front receives the response bytes (V5-I.5) | Worker |
| `REQUEST_INTAKE`, worker dead | the response | XC-4 | `REQUEST_LOST`: the client connection died with its holder, as a daemon crash closes it; the original request-id semantics apply to a retry | Collector |
| `REQUEST_RESPONDED (r, s)` with RELAY, front restarted before writing | the client write | the front lost the socket with its process | none possible: the bytes are kept as a `RESPONSE` blob for audit; the client sees a closed connection, as after a daemon crash | — |
| `DRAIN_STOP_INTENT`, `DRAIN_FREEZE`, `DRAIN_OFD_EVIDENCE` without intake | the drain | DRAIN set free | `DRAIN_ABANDON`; completeness by V5-H.4 | Reconciler |
| `DRAIN_INTAKE` or `DRAIN_RELEASED`, worker dead | reclaim | XC-4 | `DRAIN_RECLAIMED`; outputs by V5-H.4 (UNKNOWN where no read end survives) | Collector |
| `CHILD_DISPATCH_INTENT` without `CHILD_HELD` | the child launch | child phase | none by the front; the worker or the Collector commits `CHILD_ABORT` or `CHILD_UNKNOWN` by V5-E.1 | Worker or Collector |
| `CHILD_READY` without exec evidence | the GO release | no `CLOSED_CHILD` yet | none: the sub-helper killed init if GO was lost; closure decides | Collector |
| `CLOSED_NS` … `CLOSED_WITNESS` with later steps missing | the barrier or settlement | physical flags | the Collector resumes from the flags (V5-G.4) | Collector |
| `CUSTODY_RETURNED` or `HISTORICAL_SETTLEMENT` without reconstruction | the new front | phase | `FRONT_RECONSTRUCTION`, then `FRONT_OWNED (g+1)` | Collector, then Front |
| any intent whose own effect step refused | the effect | the refusal record | the original refusal mapping: a startup refusal for owner diagnosis where the original startup refuses (NF4-10), or the `unresolved` set where the original catches it | as original |

---

## V5-G. The no-launch route, custody return, and every recovery action (V4-REQ-G; 07.3, 04.4, 12.2; D-6a)

Carried: v3 V-G (C3-VG with R4-30 … R4-33, R4-56, as replaced by R5-7 and R5-10, inside C4-B); v4 V4-G.2 (barrier) and V4-G.3 (seed) (C4-VG23, with R5-15). V5-G replaces v4 V4-G.1 and V4-G.4.

### V5-G.1 Never_Dispatched release, quarantine, recovery and return, without CLOSED_WITNESS (07.3)

The complete route, every step legal in V5-F:
1. **Root.** `PREPARED (g)` committed; the WL operation's use is RESERVED with `EFFECT_INTENT` (`rw/protected_operations.py:746-749`).
2. **Failure before dispatch.** `Record_Launch_Intent` refuses (W2), or any step before `DISPATCH_INTENT` fails. The launch journal is `Never_Dispatched`; the facts satisfy `Never_Holds` (`core/resource_observation_classification.ads:96-102`), so the native class is `Never_Launched`.
3. **`HANDOFF_ABORT (g, Never_Dispatched)`** (Front; ACK set free; no `TRANSFER_SENT (g)`). It sets `Released_Unlaunched` only together with step 4's commit.
4. **P.** The original `Release_Hold` (`core/resource_run_ledger.ads:319-320`) for the root row, with no CLOSED_WITNESS (PR-a, r1′, r3′). No physical event of g is legal afterwards, because `Launched` was never set.
5. **U.** The original exception path: `quarantine (operation, exc)` → native `QUARANTINE_USE` → `QUARANTINED` (`:767-777`), unless the row is SETTLED or RELEASED. `HISTORICAL_SETTLEMENT (g)` records it (Front, `Owners_Open`).
6. **Response.** The exception propagates to the daemon, which sends the original error response (`rw/daemon.py:360-362` pattern: `WorldlineError` → `ok: false`).
7. **Return.** `FRONT_OWNED (g+1)` (Front): the front never closed its owners, so it serves the next request at once.
8. **Recovery.** U by K4 through `quarantine.resolve` (RT-16), as original.

A dispatched root (W3, or any failure after `DISPATCH_INTENT`) takes `HANDOFF_ABORT (g, Dispatched)` instead: the original failure stop runs, the root row keeps its holds until closure (`Retain_Uncertain`, PR-b), and the same U, response and return steps follow; g's physical events continue after g+1 exists (V5-F.2).

### V5-G.2, V5-G.3

Carried as v4 V4-G.2 and V4-G.3 (C4-VG23, with R5-15). The original outer test is exactly R4-30's. The seed is the custody frame's `root_native` and `original_native_use` (`rw/root_worker_custody.py:125-133`; `rw/protected_root_observation.py:157-164`); the worker's requirement on it is at `rw/protected_root_observation.py:105-117` (NF4-3's correction of v4's citation). The seed is an input: authentic current physical evidence, or the custody-return evidence, and the settlement commands still decide.

### V5-G.4 Every automatic and owner route, with its actions (replaces v4 V4-G.4)

"Material" names the authentic closure or current evidence the action reads; "exception mapping" says whether a refusal is fatal to startup (it propagates out of `reconcile_before_endpoint`, as `recover_committed` does outside any `try`, NF4-10) or unresolved (caught as `WorldlineError` into `self.unresolved`, `rw/protected_operations.py:363-382`). The first committed `RESULT_CAPTURE` is never replaced: every action reads it, and `finish` refuses a different capture (`:780-781`).

| Id | Trigger | Material | Action (exact calls) | Exception mapping | Automatic or owner |
|---|---|---|---|---|---|
| RT-21 | U `EFFECT_OBSERVED` | the retained first `RESULT_CAPTURE`; for a root operation also `CLOSED_WITNESS (g)` or `CUSTODY_RETURNED (g)` | `recover_committed (operation)` → `finish` with the restored capture → native replay of `OBSERVE_EFFECT` equal → `settle_historical` → `SETTLE_USE` = `SETTLED_NEW` (`:791-816`) | fatal, as original | Automatic |
| RT-22 | U `SETTLED` | as RT-21 | `recover_committed`; `finish` replays `SETTLED_NEW` and `settle_historical` idempotently (`:786-790`) | fatal, as original | Automatic |
| RT-23 | U `EFFECT_INTENT` with `FULL_BROKER_PREPARED` and later broker progress, no `RESULT_CAPTURE` | the broker's journaled boundaries (`rw/canonical_full_broker.py:115-170`) | `broker.recover`, then `finish` (`rw/protected_operations.py:369-375`) | unresolved, as original | Automatic; the owner on failure |
| RT-24 | U `EFFECT_INTENT` with `STAGING_INTENT` only | — | added to `unresolved` (`:376`) | unresolved | Owner, with quarantine and K4 |
| RT-25 | root Worker_Owned … Worker_Relinquish; worker dead after `REQUEST_INTAKE (r, s)` and before `REQUEST_RESPONDED` | worker pidfd terminal (XC-4) | `REQUEST_LOST (r, s)`; the request's operation row (if one was reserved in the worker) is recovered by RT-17 … RT-24 according to its U, after `CUSTODY_RETURNED` and reconstruction | per its U row | Automatic |
| RT-26 | descriptor Released; worker dead | worker pidfd terminal | `DRAIN_RECLAIMED`. Outputs: reattach only if the front still holds a live read copy (V5-H.3); otherwise `OUTPUT_CUSTODY_LOST`, completeness UNKNOWN. Stdin: the worker's write copy is gone; W below the payload length is `STDIN_TRUNCATED` → UNKNOWN | — (no refusal; UNKNOWN is recorded) | Automatic |
| RT-27 | descriptor Intake, not yet Released; worker dead | worker pidfd terminal | `DRAIN_RECLAIMED`; the front closes its stdin write copy at once (EOF by V4-H.5) and reattaches outputs as RT-26 | — | Automatic |
| RT-28 | root Worker_Owned … Worker_Relinquish, or Unknown from them; worker and namespace-init pidfds terminal; no `CLOSED_WITNESS` | the two pidfds (K-24); XC-6 | `CUSTODY_RETURNED (g)`; escrow claim; U by RT-21 … RT-24 if its row qualifies, otherwise native `QUARANTINE_USE` → `HISTORICAL_SETTLEMENT`; `FRONT_RECONSTRUCTION`; `FRONT_OWNED (g+1)`. The root row keeps its holds (`Retain_Uncertain`) until g's physical events settle it | per the U row's original mapping | Automatic; P by owner if closure never arrives |
| RT-29 | `HANDOFF_ABORT (g, class)` committed without its follow-up | the abort record | V5-F.7's row for it | as original | Automatic |

COMMITTED stays absorbing (CD-1). No route settles on EOF, a deadline, a terminal frame alone, or custody return alone.

---

## V5-H. Surviving custody, interval fold, kcmp operands and EOF (V4-REQ-H; 08.1, 08.2, 08.3, 08.5; D-3a)

Carried: v3 V-H.1, V-H.2 (C3-VH1 with R4-34 … R4-36) and V-H.4 (C3-VH4), inside C4-B; v4 V4-H.2 (C4-VH2), V4-H.5 and V4-H.6 (C4-VH56). V5-H replaces v4 V4-H.1, V4-H.3 and V4-H.4.

### V5-H.1 Read-armed intervals and their fold (replaces v4 V4-H.1)

- **Records** in each descriptor's spool chain, each appended and fsynced before the next action: `ARMED (d, s, owner, P)`; `CHUNK (d, s, owner, offset, length, sha256)`, appended and fsynced before the chunk is delivered (R4-35); `DISARMED (d, s, owner, P)`, after the last chunk's fsync.
- **Arm before read.** A reader is registered (`add_reader`, a reading task, or a `connect_read_pipe` transport) only after its `ARMED` record's fsync has returned. A reader whose `ARMED` append fails is never registered.
- **The fold.** Over the chain in order, with state (open, owner, P): `ARMED` needs the state closed and its P equal to the current P, and opens the interval for its owner; `CHUNK` needs an open interval of the same owner and `offset` = P, and sets P := P + length; `DISARMED` needs an open interval of the same owner and its P equal to the current P, and closes it. Any other record order is a chain refusal (RT-14 class).
- **Detection.** At recovery, an interval that is open at the end of the fold, whatever the last record is (an `ARMED` or any number of `CHUNK` records after it), may have lost bytes that the kernel gave to a reader that died before spooling them. Its completeness is `READ_GAP_POSSIBLE`, which is UNKNOWN; no PASS rests on it.
- **Limit.** Lost bytes are detected, never recovered.

### V5-H.2

Carried as v4 V4-H.2 (C4-VH2). The write fold is the same over `WRITE_ARMED (d, s, owner, W)` and `W_DONE (d, s, owner, W)`; an interval open at the end is `STDIN_POSITION_UNKNOWN`.

### V5-H.3 Reattachment, only where a live read end exists (replaces v4 V4-H.3)

**Which processes hold a pipe's read end** (static, from the helper code): the helper closes its own copies after HELD (`native_root_worker_supervisor_v1.c:348-349`), so the read ends of out and err are held only by the front (from HELD), the worker (from SEND, kept after INTAKE), and the front's retained escrow copy (from SEND until CLOSED_WITNESS or reclaim). Every copy is process-local: it dies with its process. The durable spool, P and W cannot recreate a pipe.

**Reattachment** happens only when the reattaching process itself still holds a live read end:
1. the front's retained copy is the descriptor it duplicated before SEND and has never closed; it checks the copy with `fstat` (dev, ino, mode) against the FREEZE record. No kcmp is used here, because there is no second live descriptor to compare;
2. it verifies the spool chain and folds it (V5-H.1);
3. it appends `ARMED (d, s′, front, P)` at the folded P and waits for the fsync;
4. **only then** it registers the new reader: for an original V3 slot, `attach_output` over a fresh `os.dup` (`rw/protected_scoped_supervisor_v3.py:482-493`); for a successor slot, a raw reader;
5. it resumes the slot's consumer from P with the spool prefix, carrying any `READ_GAP_POSSIBLE` mark.

**kcmp operands, exactly** (v3 V-H.2 H4, carried, restated): `kcmp (pid_front, pid_worker, KCMP_FILE, fd_front, fd_worker)`, where `pid_front` is the front's own pid; `pid_worker` is the worker's host pid, read by the front from the fdinfo of the worker pidfd it holds (`Pid:` line), in the host PID namespace **[unverified reasoning, K-4]**; `fd_front` is the front's descriptor number of its own still-open copy; `fd_worker` is the descriptor number the worker reports for its received copy in its H4 validation frame. Both descriptors are live at the call, which is made after SEND and before the front releases its copy. Permission: `PTRACE_MODE_READ` over the worker **[unverified reasoning, K-5]**. A kcmp result other than equal is a validation failure: the worker closes its copies unread and the front commits `DRAIN_ABANDON`.

**The retained read copy and the writer (measured, K-25).** While the escrow holds a non-reading read copy, a writer whose active reader has died does not get `EPIPE`; it blocks once the pipe is full. In the original, the writer gets `EPIPE` or `SIGPIPE` when its only reader dies. To keep the original behaviour as far as the design can: when a reattach is impossible (identity mismatch, or the front is not the custody target), the front closes its retained copy at once, so the writer sees what the original writer sees. Where the front does reattach, the writer's blocking lasts from the reader's death until step 4. K-25 measures both the blocking and the `EPIPE` timing; nothing is claimed before it.

### V5-H.4 Failure and restart table against actual custody (replaces v4 V4-H.4)

"Lost" means the pipe has no surviving read end, so its remaining output and completeness are irrecoverably UNKNOWN (`OUTPUT_CUSTODY_LOST`): this is exactly what the original daemon's crash does to a pipe whose only reader it is. The successful original controls stay required for the windows without failure.

| Window | Front crashes or restarts | Worker dies | Host restarts | Cancellation, processes alive |
|---|---|---|---|---|
| A: before `DRAIN_STOP_INTENT` | the front is the only reader: lost; an open `ARMED` also marks `READ_GAP_POSSIBLE`; the front's stdin write end closes (EOF; `STDIN_TRUNCATED` if W is short) | nothing transferred | lost | nothing changes |
| B: STOP_INTENT → FREEZE | lost (the front is still the only reader); the Reconciler commits `DRAIN_ABANDON` for the record | nothing transferred | lost | the stop completes; FREEZE follows, or the front resumes |
| C: FREEZE → SEND | lost (nothing sent); `DRAIN_ABANDON` by the Reconciler | — | lost | the front resumes from P and W |
| D: SEND → OFD_EVIDENCE | the worker holds a copy but has not intaked; the Reconciler commits `DRAIN_ABANDON`, the worker closes its copy unread: lost | the front commits `DRAIN_ABANDON` and resumes from its own live copy (it is still the reader) | lost | the front commits `DRAIN_ABANDON` and resumes |
| E: OFD_EVIDENCE → INTAKE or ABANDON | with INTAKE committed: the worker is the reader (row F); without it: as D | without INTAKE: the front commits `DRAIN_ABANDON` and resumes; with INTAKE: row F | lost | the CAS decides; the loser does not act |
| F: INTAKE → RELEASE | the worker reads; the front's process-local copies die with it, which changes nothing for the worker; after restart the front holds no copy and never resumes this descriptor | RT-27: if the front is alive, its retained copy is a live read end: reattach (V5-H.3); the front closes its stdin write copy at once. If the front is not alive: lost | lost; rows settle by the crash table (no CLOSED frame: `Unknown`, holds kept) | the worker stops per M8 (a); its intervals close cleanly |
| G: after RELEASE | as F | RT-26: reattach through the front's retained copy if the front is alive and still holds it; otherwise lost | lost | as F |

Two readers or two writers never act on one descriptor at once. No row claims recovery of a pipe that no live process holds.

### V5-H.5, V5-H.6

Carried as v4 V4-H.5 and V4-H.6 (C4-VH56). Last-writer EOF is unchanged: the actor sees EOF only when the last write description closes, and a retained read copy never delays or produces EOF (K-22).

---

## V5-I. Root admission, request joins, presence, gates and the RELAY frame (V4-REQ-I; 09.1, 09.2, 09.3, 09.5; D-8a, D-8b)

Carried: v3 V-I.1 (C3-VI1), V-I.4 and V-I.5 (C3-VI45), inside C4-B; v4 V4-I.3 (C4-VI3). V5-I replaces v4 V4-I.1, V4-I.2 and V4-I.4 … V4-I.6.

### V5-I.1 Four joins, in two phases (unit `Worldline.Requester_Correspondence`, X-6)

| Join | Phase | Head it reads | Authorizes |
|---|---|---|---|
| `Root_Admission_Join` | **before any worker ownership**: root phase Transfer_Sent or Roster_Evidence of the current generation, `Owner_Root` = None, ACK set free | the authenticated `TRANSFER_SENT (g)` (or `ROSTER_EVIDENCE (g)`) event, whose record binds the custody frame digest | the `CUSTODY_ACK (g)` CAS |
| `Transfer_Join` (FRESH) | after `CUSTODY_ACK (g)`: root phase Worker_Owned, Original_Result or Handler_Terminal, `Owner_Root` = Worker (XC-2, XC-3) | the authenticated `REQUEST_TRANSFER_INTENT (r, s)` with mode FRESH | the `REQUEST_INTAKE (r, s)` CAS |
| `Relay_Join` (RELAY) | as `Transfer_Join` | the same head with mode RELAY, and the channel of the current `Reattach_Epoch` | the `REQUEST_INTAKE (r, s)` CAS |
| `Serving_Join` | at every gate use after the authorizing event | `REQUEST_INTAKE (r, s)` for a transferred request; `CUSTODY_ACK (g)` for the root's own operation (RETAINED); the original capture (HISTORICAL) | that gate use |

`Root_Admission_Join` is never evaluated in a worker-owned phase, and the request joins are never evaluated before `CUSTODY_ACK`. None reads its own future event (09.1).

**`Root_Admission_Join` conjuncts.** J1 decode the root request's retained host ucred; J2 it equals the document's `rawUcred`; JR the frame's `original_request` equals the operation row's `capture['request']` and the root capture's (`rw/protected_root_observation.py:28`); J8 the head above; J9 the reservation equals the root row's bound reservation, and the descriptor and genesis anchors join (X-2). The root's own client socket stays with the front, which relays the original result (`rw/protected_root_worker.py:184`), so its gates in the worker are RETAINED, never FRESH.

**Results.** `Join_Ready`, `Ucred_Malformed`, `Uid_Gid_Mismatch`, `Front_Reread_Mismatch`, `Gate_Reread_Mismatch`, `Socket_Mismatch`, `User_Namespace_Mismatch`, `Pid_Namespace_Unrelated`, `Presence_Invalid`, `Head_Missing`, `Phase_Mismatch`, `Join_Operand_Mismatch`, `Relay_Frame_Invalid`. For `Root_Admission_Join`, anything but `Join_Ready` means no ACK: the front or Reconciler commits `ABANDON (g)`. For FRESH it declines intake and the request is offered in RELAY; for RELAY it keeps the request queued. Nothing is refused for correspondence.

### V5-I.2 Operands and three-valued presence (replaces v4 V4-I.2)

The record is v4's `Requester_Operands` with `Intake_Head` renamed `Admission_Head`, `Which` extended with `Root_Admission`, and one field added, `Relay_Sequence : Q.Quantity`. Each field has, per mode, one of three presence values: **R** (required present; absence is `Presence_Invalid`), **A** (required absent; presence is `Presence_Invalid`), **O** (optional: present or typed absence, and its absence never decides; when both sides of an equality conjunct are present, the conjunct applies). This replaces v4's conjunct table where "required" and "corroboration" were mixed.

| Field | Root_Admission | Fresh | Relay | Retained | Historical |
|---|---|---|---|---|---|
| `Raw_Host_Ucred` (J1, J2) | R | R | R | R | R |
| `Raw_Relative_Ucred` (J1′, the worker's re-read) | A | R | A | A | A |
| `Front_Reread` (JF, at transfer) | A | R | R | A | A |
| `Gate_Reread` (JG, per gate use) | A | A | R | A | A |
| `Host_Socket_Identity` | A | R | O | A | A |
| `Reader_Socket_Identity` (J4) | A | R | A | A | A |
| `Host_Socket_Cookie`, `Reader_Socket_Cookie` (J5) | A | O, O | O, A | A | A |
| `Origin_User_Ns`, `Reader_User_Ns` (J3) | A | O, O | A | A | A |
| `Origin_Pid_Ns`, `Reader_Pid_Ns`, `Held_Pid_Ns` (JN) | A | O, O, O | A | A | A |
| `Pidfd_Record` (J7) | A | O | O | A | A |
| `Request_Document`, `Request_Id`, `Operation_Name`, `Raw_Request` | R | R | R | R | R |
| `Row_Request_Capture`, `Reservation` | R | R after `_reserve`, A before | R after `_reserve`, A before | R | R |
| `Transaction_Preparer` | R for transaction operations, else A | same | same | same | same |
| `Generation`, `Subgeneration` | R | R | R | R | R |
| `Transfer_Head` | A | R | R | A | A |
| `Admission_Head` | R (`TRANSFER_SENT` or `ROSTER_EVIDENCE`) | A at `Transfer_Join`, R (`REQUEST_INTAKE`) at `Serving_Join` | as Fresh | R (`CUSTODY_ACK`) | R (the original capture head) |
| `Relay_Sequence` | A | A | R at each gate use | A | A |
| `Descriptor_Anchor`, `Genesis_Anchor` | R | R | R | R | R |

The decode sources and J9 checks are v4's operand table (`Request_Document` from the canonical observation bytes in form UTF8 without the LF, `rw/client_peer.py:113-117`, `rw/canonical.py:41-49`; `Row_Request_Capture` from `capture['request']`, `rw/protected_operations.py:402-403`, `:415`; `Transaction_Preparer` from `preparerPeer`, `rw/client_peer.py:204-220`; `Reservation` from `capture['resource_intent'].reservation`; heads from the verified chain; anchors by `Roster_Join`).

### V5-I.3

Carried as v4 V4-I.3 (C4-VI3).

### V5-I.4 Every gate, by phase and mode (replaces v4 V4-I.4)

"Own" is the root's own operation in the worker; "transferred" a request intaked by FRESH or RELAY; "historical" a retained capture in recovery or K4 (`historical_scope`, `rw/protected_operations.py:816`). Every gate checks `Serving_Join` at each use, exactly as the original re-reads at each use (`rw/client_peer.py:131-137`).

| Gate (v3 V-I.5) | Where it runs | Own | Transferred | Historical | Operands beyond J1, J2 and the document | Head at use |
|---|---|---|---|---|---|---|
| `rw/canonical_actor_execution.py:64` before-exec capture | worker | RETAINED | FRESH or RELAY | — | `Row_Request_Capture`, `Reservation` | own `CUSTODY_ACK`; transferred `REQUEST_INTAKE` |
| `rw/protected_operations.py:401` `resource_request_material` | custody owner | — | FRESH or RELAY | HISTORICAL | `Reservation` once reserved | `REQUEST_INTAKE`; historical capture |
| `rw/protected_operations.py:414` `_row_for_request` | custody owner | RETAINED | FRESH or RELAY | HISTORICAL | `Row_Request_Capture` | as above |
| `rw/protected_operations.py:686` pre-effect boundary | custody owner | RETAINED (front, before handoff) | FRESH or RELAY | — | `Row_Request_Capture`, `Reservation` | as above |
| `rw/protected_operations.py:728` `_invoke_serial` context | custody owner | — | FRESH or RELAY | — | — | `REQUEST_INTAKE` |
| `rw/protected_owner.py:323` owner peer | custody owner | — | FRESH or RELAY | HISTORICAL (K4) | the owner-only uid from `Raw_Host_Ucred` | `REQUEST_INTAKE`; historical capture |
| `rw/canonical_owner_witness.py:22` | custody owner | — | FRESH or RELAY | HISTORICAL | — | as above |
| `rw/protected_resource_runtime.py:229` `credential_join` | custody owner | RETAINED | FRESH or RELAY | — | — | as above |
| `rw/protected_resource_runtime.py:387` reserve packet | custody owner | — | FRESH or RELAY | — | — | `REQUEST_INTAKE` |
| `rw/protected_scoped_resource_runtime.py:386` `intent_for_operation` | custody owner | — | FRESH or RELAY | — | `Transaction_Preparer` for transactions | `REQUEST_INTAKE` |
| `rw/protected_scoped_resource_runtime.py:625` `lifecycle_packet` | custody owner | RETAINED | FRESH or RELAY when a transferred WL request launches under a selected D-4a option | HISTORICAL | `Row_Request_Capture` | the operation's own head |
| `rw/protected_scoped_resource_runtime.py:702` `launch_reserved` | custody owner | RETAINED (front, before handoff) | as the line above | — | `Reservation` | as above |
| `rw/protected_scoped_resource_runtime.py:858` `go_scoped` | custody owner | RETAINED | as the line above | — | `Reservation` | as above |
| `rw/protected_root_observation.py:28` `RootControllerCapture` | worker, at intake | RETAINED via `Root_Admission_Join` | — | — | the frame's `original_request` | `TRANSFER_SENT` or `ROSTER_EVIDENCE` |
| `rw/protected_root_resource.py:33`, `rw/protected_root_supervisor.py:21`, `rw/root_worker_custody.py:97`, `rw/protected_root_worker.py:53` | front | the original `RequestPeer`, exactly | — | — | — | the front's own Front_* phase |

The front's gates stay exactly `type (x) is RequestPeer`. In the worker a gate accepts exactly one type per mode (`RetainedRequestObservation`, `CrosswalkRequestPeer`, `RelayRequestPeer`), never two.

### V5-I.5 The RELAY frame (replaces v4 V4-I.5)

**Transport.** The custody channel, a `SOCK_STREAM` socketpair with `SO_PASSCRED` (NF5-5), or after a reattach the reattach connection (V5-L.3). Each frame is:
- 4 bytes `WLRY`; 4 bytes, the body length L, unsigned big-endian; L bytes of body; 32 bytes MAC.
- **Body:** `archive` (the grammar of `rw/operation_capture.py:15-39`) of the record {`type`, `generation`, `reattach_epoch`, `request`, `subgeneration`, `operation`, `gate`, `sequence`, `nonce`, `admission_head`, `payload`}. Quantities are canonical decimal strings; `nonce` and `admission_head` are 64 lowercase hex; `gate` is the gate's name from V5-I.4.
- **MAC** = `Hmac_Sha256 (K, DOMAIN_RELAY ‖ "WLRY" ‖ L ‖ body)`, with K the issuer key and `DOMAIN_RELAY` = `worldline.root-worker-relay-v1` followed by one zero byte.

**Types and payloads.**
- `GATE_REQUEST` (worker → front): payload empty. The worker assigns `sequence` = the previous sequence for (g, r, s) plus one, starting at 1, and a fresh random 32-byte `nonce`.
- `GATE_RESPONSE` (front → worker): echoes every field of the request; payload either `{observation: <the canonical observation bytes of RequestPeer.observation ()>}` or `{error: {class, code, message, details}}`.
- `RESPONSE_BYTES` (worker → front): payload `{line: <the exact response line bytes>, sha256}`, sent after `REQUEST_RESPONDED (r, s)` commits with that sha256.
- `RESPONSE_WRITTEN` (front → worker): echoes the sha256 after the front's write returns.

**Freshness and binding.** The front performs the re-read only after receiving a valid `GATE_REQUEST`, so every `GATE_RESPONSE` is a re-read made for that one gate use. The worker (X-6 `relay_frame`) accepts a response only if the MAC verifies and generation, `reattach_epoch` (the current epoch), request, sub-generation, operation, gate, sequence, nonce and `admission_head` (the committed `REQUEST_INTAKE (r, s)`) all equal its request's; each nonce is accepted once. A replayed, reordered, cross-request, cross-gate or previous-epoch frame is `Relay_Frame_Invalid`.

**Original re-read errors propagate as themselves.** The front's re-read is the original call. The original re-read path raises `WorldlineError` (for example `PEER_REQUEST_MISMATCH`, `rw/client_peer.py:134-135`) or an `OSError` from the socket query. The front encodes the class, code (or errno), message and details; the worker raises the same class with the same code, message and details at that gate. The original exception path then applies: quarantine after `_reserve` (`rw/protected_operations.py:767-768`) and the original error response. Any other class cannot arise from that path by static reading; if one does, it is treated as transport loss (below), never as an accepted value.

**Transport loss: the legal fallback state.** If the channel closes or a frame fails `relay_frame`, the gate use cannot complete. A RELAY client connection lives only in the front, so a front that lost the channel has lost the client connection too (its process ended, or it is reattaching after a restart). The worker therefore raises at that gate exactly what the original re-read raises when the client connection is gone **[unverified reasoning, RC-10: the exception `KernelPeer.observation ()` raises for a closed connection]**, and the original exception path follows, as for a client that disconnects mid-request in the original. No gate waits on a deadline, nothing is fabricated, and the request's custody events record the outcome (`REQUEST_RESPONDED` with the error response, or `REQUEST_LOST` if the worker dies).

**Native ABI and cost.** X-6 `relay_frame` (V5-A.3): records `RelayFrameInput` and `JoinResult`; cost linear in L for the archive recognition plus one HMAC over the magic, the length field and the body per frame (OPEN, D2 class); one round trip per gate use.

### V5-I.6 Ordering (replaces v4 V4-I.6)

**Root handoff (pre-ACK).** (1) Receive the full roster: frame, OFDs, locks and origins (repairing `rw/root_worker_custody.py:183-185`, where a `RequestPeer` is built before the roster arrives); (2) validate every element; (3) `Root_Admission_Join` over the `TRANSFER_SENT (g)` or `ROSTER_EVIDENCE (g)` head; (4) the intake native redecision `ROOT_READY_CONJUNCTION`, seed equal to current; (5) CAS `CUSTODY_ACK (g)`; (6) only then the own operation's gates, each through `Serving_Join` in RETAINED mode.

**Each transferred request (post-ACK).** (1) Receive its roster (FRESH: the socket; RELAY: nothing but the frame); (2) validate; (3) `Transfer_Join` or `Relay_Join` over its transfer-intent head; (4) CAS `REQUEST_INTAKE (r, s)`; (5) only then any gate, each use through `Serving_Join`.

---

## V5-J. Genesis and head, the complete DDL, lossless storage and migration (V4-REQ-J; 12.1, 04.3; D-2a)

Carried: v3 V-J (C3-VJ with R4-37 … R4-40, R4-53, inside C4-B); v4 V4-J.1, V4-J.2 (C4-VJ12) and V4-J.5 (C4-VJ5). V5-J replaces v4 V4-J.3 and V4-J.4, and v3 V-F.5's DDL (W5-2).

### V5-J.1

Carried as v4 V4-J.1 and V4-J.2 (C4-VJ12).

### V5-J.2 The complete custody v2 DDL (replaces v3 V-F.5, W5-2)

```sql
CREATE TABLE genesis (
  name  TEXT PRIMARY KEY CHECK (name = 'owner-genesis'),
  value BLOB NOT NULL CHECK (typeof(value) = 'blob'),
  mac   TEXT NOT NULL CHECK (typeof(mac) = 'text' AND length(mac) = 64)
);
CREATE TABLE events (
  seq           INTEGER PRIMARY KEY,
  event_id      TEXT NOT NULL UNIQUE CHECK (typeof(event_id) = 'text' AND length(event_id) = 64),
  previous      TEXT NOT NULL UNIQUE CHECK (typeof(previous) = 'text' AND length(previous) = 64),
  generation    BLOB NOT NULL CHECK (typeof(generation) = 'blob' AND length(generation) >= 1
                  AND substr(generation, length(generation), 1) <> x'00'),
  operation     TEXT NOT NULL CHECK (typeof(operation) = 'text'),
  subject_kind  TEXT NOT NULL CHECK (subject_kind IN ('ROOT','REQUEST','DESCRIPTOR')),
  subject       TEXT NOT NULL CHECK (typeof(subject) = 'text'),
  subgeneration BLOB NOT NULL CHECK (typeof(subgeneration) = 'blob' AND (length(subgeneration) = 0
                  OR substr(subgeneration, length(subgeneration), 1) <> x'00')),
  kind          TEXT NOT NULL CHECK (kind IN (
    'PREPARED','HELD','RUNNING','EXECUTION_NATIVE','EXECUTION_ACK','HANDOFF_INTENT',
    'FRONT_CLOSE_INTENT','FRONT_CLOSED','TRANSFER_SENT','ROSTER_EVIDENCE','CUSTODY_ACK','ABANDON',
    'FRONT_RETAINED_ESCROW','HANDOFF_ABORT','ORIGINAL_PROGRESS','ORIGINAL_RESULT','HANDLER_TERMINAL',
    'WORKER_RELINQUISH','WORKER_REATTACHED','CUSTODY_RETURNED','CLOSED_NS','CLOSED_OUTER','CLOSED_RAW',
    'CLOSED_WITNESS','PHYSICAL_SETTLED','HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION','FRONT_OWNED',
    'UNKNOWN','RECONCILED',
    'REQUEST_QUEUED','REQUEST_TRANSFER_INTENT','REQUEST_INTAKE','REQUEST_ABANDON','REQUEST_RESPONDED',
    'REQUEST_LOST',
    'DRAIN_STOP_INTENT','DRAIN_FREEZE','DRAIN_OFD_EVIDENCE','DRAIN_INTAKE','DRAIN_ABANDON',
    'DRAIN_RELEASED','DRAIN_RECLAIMED')),
  actor         TEXT NOT NULL CHECK (actor IN ('FRONT','WORKER','COLLECTOR','RECONCILER')),
  record        BLOB NOT NULL CHECK (typeof(record) = 'blob'),
  base          BLOB NOT NULL CHECK (typeof(base) = 'blob'),
  mac           TEXT NOT NULL CHECK (typeof(mac) = 'text' AND length(mac) = 64),
  CHECK ((subject_kind = 'ROOT') = (subject = ''))
);
CREATE TABLE alternatives (
  generation      BLOB NOT NULL CHECK (typeof(generation) = 'blob'),
  operation       TEXT NOT NULL,
  subject_kind    TEXT NOT NULL CHECK (subject_kind IN ('ROOT','REQUEST','DESCRIPTOR')),
  subject         TEXT NOT NULL,
  subgeneration   BLOB NOT NULL CHECK (typeof(subgeneration) = 'blob'),
  alternative_set TEXT NOT NULL CHECK (alternative_set IN ('ACK','REQUEST','DRAIN')),
  event_id        TEXT NOT NULL UNIQUE REFERENCES events(event_id),
  PRIMARY KEY (generation, operation, subject_kind, subject, subgeneration, alternative_set)
);
CREATE TABLE root_state (
  generation          BLOB PRIMARY KEY CHECK (typeof(generation) = 'blob' AND length(generation) >= 1
                        AND substr(generation, length(generation), 1) <> x'00'),
  operation           TEXT NOT NULL CHECK (typeof(operation) = 'text'),
  phase               TEXT NOT NULL CHECK (phase IN (
    'FRONT_OWNED','PREPARED','HELD','RUNNING','EXECUTION_NATIVE','EXECUTION_ACK','HANDOFF_INTENT',
    'FRONT_CLOSE_INTENT','FRONT_CLOSED','TRANSFER_SENT','ROSTER_EVIDENCE','WORKER_OWNED',
    'ORIGINAL_RESULT','HANDLER_TERMINAL','WORKER_RELINQUISH','ABANDONED','FRONT_RETAINED_ESCROW',
    'HANDOFF_ABORTED','CUSTODY_RETURNED','HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION','ENDED',
    'UNKNOWN')),
  before_unknown      TEXT,
  owners_open         INTEGER NOT NULL CHECK (owners_open IN (0,1)),
  abort_class         TEXT CHECK (abort_class IS NULL OR abort_class IN ('NEVER_DISPATCHED','DISPATCHED')),
  launched            INTEGER NOT NULL CHECK (launched IN (0,1)),
  closure_ns          INTEGER NOT NULL CHECK (closure_ns IN (0,1)),
  closure_outer       INTEGER NOT NULL CHECK (closure_outer IN (0,1)),
  closure_raw         INTEGER NOT NULL CHECK (closure_raw IN (0,1)),
  witness             INTEGER NOT NULL CHECK (witness IN (0,1)),
  settled             INTEGER NOT NULL CHECK (settled IN (0,1)),
  released_unlaunched INTEGER NOT NULL CHECK (released_unlaunched IN (0,1)),
  unknown_cause       TEXT CHECK (unknown_cause IS NULL OR length(unknown_cause) = 64),
  reattach_epoch      BLOB NOT NULL CHECK (typeof(reattach_epoch) = 'blob' AND (length(reattach_epoch) = 0
                        OR substr(reattach_epoch, length(reattach_epoch), 1) <> x'00')),
  head_event          TEXT NOT NULL REFERENCES events(event_id),
  CHECK ((phase = 'UNKNOWN') = (before_unknown IS NOT NULL)),
  CHECK (before_unknown IS NULL OR before_unknown NOT IN ('UNKNOWN','ENDED'))
);
CREATE TABLE subject_state (
  generation    BLOB NOT NULL REFERENCES root_state(generation),
  subject_kind  TEXT NOT NULL CHECK (subject_kind IN ('REQUEST','DESCRIPTOR')),
  subject       TEXT NOT NULL,
  subgeneration BLOB NOT NULL CHECK (typeof(subgeneration) = 'blob' AND (length(subgeneration) = 0
                  OR substr(subgeneration, length(subgeneration), 1) <> x'00')),
  phase         TEXT NOT NULL,
  mode          TEXT NOT NULL CHECK (mode IN ('NONE','FRESH','RELAY')),
  position      BLOB CHECK (position IS NULL OR (typeof(position) = 'blob' AND (length(position) = 0
                  OR substr(position, length(position), 1) <> x'00'))),
  carried_from  BLOB CHECK (carried_from IS NULL OR (typeof(carried_from) = 'blob' AND length(carried_from) >= 1
                  AND substr(carried_from, length(carried_from), 1) <> x'00')),
  head_event    TEXT NOT NULL REFERENCES events(event_id),
  PRIMARY KEY (generation, subject_kind, subject),
  CHECK ((subject_kind = 'REQUEST' AND phase IN
           ('QUEUED','TRANSFER_INTENT','INTAKE','ABANDONED','RESPONDED','LOST'))
      OR (subject_kind = 'DESCRIPTOR' AND phase IN
           ('FRONT_HELD','STOP_INTENT','FROZEN','OFD_EVIDENCE','INTAKE','ABANDONED','RELEASED','RECLAIMED')))
);
CREATE TABLE blobs (
  sha256 TEXT PRIMARY KEY CHECK (length(sha256) = 64),
  kind   TEXT NOT NULL CHECK (kind IN ('RAW_OBSERVATION','SPOOL_CHUNK','CAPTURE','RESPONSE')),
  bytes  BLOB NOT NULL
);
CREATE TABLE head (
  name      TEXT PRIMARY KEY CHECK (name = 'current'),
  head_kind TEXT NOT NULL CHECK (head_kind IN ('ORIGIN','EVENT')),
  event_id  TEXT REFERENCES events(event_id),
  origin    TEXT CHECK (origin IS NULL OR length(origin) = 64),
  mac       TEXT NOT NULL CHECK (length(mac) = 64),
  CHECK ((head_kind = 'ORIGIN' AND event_id IS NULL AND origin IS NOT NULL)
      OR (head_kind = 'EVENT' AND event_id IS NOT NULL AND origin IS NULL))
);
```

- **Empty-chain head and the foreign key.** With no events the head row is `ORIGIN`, its `event_id` is NULL and its `origin` holds the origin digest. A NULL child key satisfies a foreign key, so `foreign_keys=ON` stays and checks every EVENT head **[unverified reasoning, RC-7: the installed SQLite's foreign-key, `typeof`, BLOB `substr`/`length` and BLOB comparison semantics]**. The origin's value is checked natively (X-4: `origin = SHA-256 (genesis row value)`), not by SQL. Every other `REFERENCES` column is written in the same transaction as the event it names, so it never points to an absent row.
- **Lossless quantities.** `generation`, `subgeneration`, `reattach_epoch`, `position` and `carried_from` are stored as the native `Quantity` representation itself: little-endian magnitude bytes (`core/resource_quantities.ads:11-17`), non-negative, minimal (no high-order zero byte; zero is the empty BLOB). The `CHECK`s enforce the form, so value equality is byte equality, and primary keys, foreign keys and the replay identity compare values exactly. No column has an integer bound. `generation` ≥ 1 is "non-empty and minimal".
- **`seq`** is SQLite's rowid. It carries order only, never a native quantity, exactly as v1 reads `ORDER BY rowid` (`rw/root_worker_journal.py:100`); its range is v1's own, so no new bound is introduced. X-4 requires the `previous` links to agree with that order.
- **`phase` lists and the exact text.** The loader compares the complete `sqlite_master.sql` text with this DDL (v3 V-J.4 rule), so the lists cannot drift; `Legal` re-checks every phase natively.
- **Every state field has a column:** Generation, Operation, Phase, `Before_Unknown`, `Owners_Open`, `Abort`, the seven `Physical_Flags`, `Unknown_Cause`, `Reattach_Epoch`, Head (root); Kind, Generation, Subject, Subgeneration, the request or descriptor phase, Mode, Position, `Carried_From`, Head (subject).

### V5-J.3 Provisioning once, and authentication at every startup (replaces v4 V4-J.3)

**The custody provisioner creates,** each file by exclusive create (R4-40):
- the genesis file: canonical form UTF8, exactly the v2 keys (R4-38), `initial_event` null;
- the database with exactly the DDL above, and the rows: `genesis` = (`owner-genesis`, `archive (exact_json (genesis file bytes))`, `Hmac_Sha256 (K, DOMAIN_V2 ‖ archive ({genesis}))`); no events; `head` = (`current`, `ORIGIN`, NULL, origin, `Hmac_Sha256 (K, DOMAIN_V2 ‖ archive ({head_kind: 'ORIGIN', head: origin, genesis}))`), where the origin is `SHA-256` of the genesis row's value, exactly v1's rule (`rw/root_worker_journal.py:98`, `:112`); empty `alternatives`, `root_state`, `subject_state`, `blobs`;
- the lock file.

**At every startup,** first included, by the same path:
1. open with `mode=rw`, never creating, `foreign_keys=ON` (`:78-84`);
2. the complete `sqlite_master.sql` text equals the DDL;
3. **genesis, as the decoded-archive relation.** The row's value equals `archive (exact_json (genesis file bytes))`, which is exactly the relation v1 checks (`rows == [('owner-genesis', archive (self.genesis))]` with `self.genesis = exact_json (raw)`, `:42`, `:95-97`); natively, X-1 `archive_equal` decodes the row's archive and compares its typed tree with the JSON value tree of the file bytes; the genesis MAC verifies. The file is never compared byte for byte with the archive;
4. X-4: the chain from the origin, every MAC, and the head (ORIGIN with no events, EVENT otherwise);
5. X-5 `fold`: the state rows equal `Next` folded over the events in `seq` order from **S0** (generation 1, Front_Owned, `Owners_Open`, empty `Reattach_Epoch`, no subjects, no rows stored), with no extra and no missing row;
6. `PRAGMA foreign_key_check` returns no row;
7. the cross-references of V5-C.2 hold.

Any failure is a named refusal (RT-14). Nothing is created, initialized or re-genesised; P-A3 bounds what this establishes.

### V5-J.4 Migration from a closed v1 journal (replaces v4 V4-J.4)

| Starting point | Path | Never |
|---|---|---|
| v1 deployment with no custody journal | provision v2 with `prior_custody = null`, at the paths of a new plan file (below) | create or reuse v1 custody objects |
| v1 deployment with a custody v1 journal whose every operation is closed (it loads under the v1 checks, and each operation's last event is `HISTORICAL_SETTLEMENT` or `FRONT_RECONSTRUCTION`, with no later `UNKNOWN`) | **New plan, new paths.** The v2 descriptor's `root_worker.owner_plan` names a new plan file P2 at a new path. P2 has the plan-v1 schema and keyset (`worldline.protected-root-worker-plan-v1`, `rw/root_worker_plan.py:13-38`), and its `handoff_journal` and `handoff_genesis` are new paths J2 and G2, distinct from v1's J1 and G1; its digest therefore differs from v1's plan P1. The provisioner creates G2, J2 and J2's lock by exclusive create; J1, G1, P1 and J1's lock are never opened for writing. **Retained old context.** G2's `prior_custody` = {v1 descriptor path and sha256, P1 path and sha256, G1 path and sha256, J1 path and sha256, J1's final head event, issuer key sha256}. Those files stay at their paths, read-only, bound in the v2 descriptor's `files` as DATA. At each v2 startup an additive `RetainedV1CustodyVerifier` runs exactly v1's `_schema` and `_load` checks (`rw/root_worker_journal.py:85-114`) over J1, with the context v1's loader needs: the genesis keyset and its digests against the retained v1 descriptor bytes and P1 bytes (`:43-49`), the installation id, and the key at the same authority root (`:50-53`). It opens J1 with `mode=ro` and takes a shared lock on J1's lock file, so no v1 writer can run beside it **[unverified reasoning, K-6]**. It requires J1's sha256 and final head to equal `prior_custody`'s. v1's `RootCustodyJournal` class is unchanged | modify, truncate, re-MAC or re-genesis J1; create anything at a v1 path |
| a v1 journal with an open or UNKNOWN operation | the provisioner refuses by name; the operator resolves it first under v1 (its reconciler and owner routes) | migrate a live custody |
| v2 back to v1 | no provisioner offers it; a v1 descriptor selects only v1 paths, and a live v2 worker's transferred OFD locks make a v1 startup's lock acquisition fail (`rw/protected_startup.py:374-385`) | ignore a live v2 owner |

A rotated issuer key makes the retained v1 verification fail by name (RT-14); it never leads to a re-MAC.

### V5-J.5

Carried as v4 V4-J.5 (C4-VJ5).

---

## V5-K. Effective checkviews over byte-immutable C-API tables (V4-REQ-K; IC-1, IC-11, IC-12; D-7a)

Carried: v4 V4-K.1 (C4-VK1); v3 V-K.2, V-K.3 (C3-VK2 with R4-41, R4-42) and V-K.5 … V-K.10 (C3-VK5 with R4-43), inside C4-B. V5-K replaces v4 V4-K.2 and V4-K.3. Everything here is bound to the sealed CAPI6R, closed at design level only.

### V5-K.1

Carried as v4 V4-K.1 (C4-VK1).

### V5-K.2 Five checkviews (replaces v4 V4-K.2)

**Base tables are inputs, never edited.** Every C-API table (`CAPI_ROUTINE_NAMES`, `CAPI_REMOVED_NAMES`, `CAPI_SPARK_UNITS`, `CAPI_QUALIFIED`, `CAPI_QUALIFIER_EXCEPTIONS`, `CAPI_LAYOUT_EXPORTS`, the tile tables, `CAPI_GATES`, `CAPI_GATE_EXCLUSIVE`, `CAPI_DIAGNOSTIC_SITES`, `CAPI_INVENTORY`, `CAPI_USE_PACKAGES`, `CAPI_WRITES`, `CAPI_ALIAS_FORBIDDEN`) and every fixed constant (`CAPI_WFX_PROTOCOL`, `CAPI_PARENT_SPEC`) stays byte-identical to its value at the C-API successor's last stage (U-6, IC-14). RW stages add only RW tables. A **checkview** is a value computed inside a check from base and RW tables; it is never stored as a table.

| Checkview | Computed from | Used by | Rule |
|---|---|---|---|
| **CV-UNITS** (owning On-unit) | `CAPI_SPARK_UNITS` and `RW_SPARK_UNITS` | R-QUAL's owning-unit check (`CAPI5/APPENDIX-BINDINGS.md:366-367`: each routine's prefix must be a listed SPARK unit) | Each name of `CAPI_ROUTINE_NAMES` has its prefix in `CAPI_SPARK_UNITS` (the base check, unchanged); each name of `RW_ROUTINE_NAMES` has its prefix in `RW_SPARK_UNITS`. `RW_SPARK_UNITS` is the **reviewed enrolled RW roster**: exactly the SPARK units that the RW stage enrolls in its proof roster and pins (B12) and that its actual GPT-6.1 stage review lists. It is disjoint from `CAPI_SPARK_UNITS`. It is never derived from `RW_ROUTINE_NAMES`: a routine whose unit is missing from the roster is a problem, not a reason to add the unit. |
| **CV-QUAL** (qualifier scope attribution) | `CAPI_QUALIFIED` ∪ `RW_QUALIFIED`; simple names = last selectors of `CAPI_ROUTINE_NAMES`, `CAPI_REMOVED_NAMES` and `RW_ROUTINE_NAMES`; roots = first identifiers of `CAPI_ROUTINE_NAMES` and `RW_ROUTINE_NAMES` | R-QUAL (a) … (d) with (d1) … (d4) | `RW_QUALIFIED` has only new scope keys, attributed by the same innermost-scope rule (`_capi_scopes`, `_capi_owner`) extended with the RW scopes' own keys. Every old scope's census, re-observed under the effective simple names, equals its unchanged `CAPI_QUALIFIED` row (U-2). |
| **CV-LAYOUT** | `CAPI_LAYOUT_EXPORTS`, then `RW_LAYOUT_EXPORTS` | R-LAYOUT, R-RES | The C-API relocated exports form their contiguous run in the base order (B0.8), and the RW exports form their own run after it. The stage is still read from the **base** `CAPI_LAYOUT_EXPORTS` alone (`staged = scope in CAPI_LAYOUT_EXPORTS`, `CAPI6/APPENDIX-BINDINGS.md:402`), so no RW export can change which stage the sole WF-X exception belongs to. |
| **CV-TILE** | the C-API tile entries and the RW tile entries | R-TILE | RW tiles are new export tiles only; every C-API tile is unchanged. |
| **CV-GATE** | `CAPI_GATES` ∪ `RW_GATES` | R-GATE, CR5, CR6 (`CAPI6/APPENDIX-BINDINGS.md:391-424`) | RW rows have new scope keys and kind `bool` or `case` only. CR5 and CR6 run over the union, with `CAPI_GATE_EXCLUSIVE` and `CAPI_WFX_PROTOCOL` taken from the base only, so the `wfx` roster stays exactly `[(Finalization_Decide, G21c, O)]` from PK-6b and empty before. |

**Unchanged rules,** restated so nothing is lost: U-1 (append-only names, disjoint from the C-API tables), U-2 (old scopes unchanged; the remedy is a reviewed renaming of the RW name, never an edit of an old row), U-3 ((d2) for every prefix of every RW with clause; no use clause beyond R-INV (vii)'s; no change to `core/worldline.ads`; no `separate`), U-4 (RW gate rows), U-5 (no RW exclusive-map table; `CAPI_WFX_PROTOCOL` and `CAPI_PARENT_SPEC` never appended or reassigned; no RW `wfx` row; no RW key in `CAPI_GATE_EXCLUSIVE`), U-6 (staging after the C-API successor, L-CAPI-P and G-PROT; byte identity), U-7 (GE1–GE9, `Authority_Glue`, R-RES, S-RES, R-GLUE, the S5 residual renamings and clause tuples), U-8 (the complete stage floor and the gate chain G-CAPI → G-CAPI-P → G-PROT → G-RW). Every sealed CAPI6 invariant and old row is kept.

### V5-K.3 Affected-stage controls (replaces v4 V4-K.3)

| Control | Mutation or positive | Expected |
|---|---|---|
| MX-RW1 | an RW gate row of kind `wfx`, in any scope | CR6 problem |
| MX-RW2 | an RW key added to `CAPI_GATE_EXCLUSIVE` | CR6 problem (base table changed; also IC-14) |
| MX-RW3 | an RW gate row of a kind other than `bool` or `case` | RW gate-kind problem |
| MQ-RW1 | an RW with clause `with Worldline.X.Y;` in which a prefix after the first identifier is an effective root or simple name | (d2) problem |
| **MQ-RW2a** (new census member) | precondition, asserted by the control before mutating: `Raw_Request` is not an effective simple name. Stimulus: add the RW routine `Worldline.Requester_Correspondence.Raw_Request` (its unit in `RW_SPARK_UNITS`). The old C_API body text `Owner_Wire.Raw_Request` (S5 `core/worldline-c_api.adb:882`) then becomes a qualified routine name of its old scope | U-2 problem: that scope's re-observed census has a member its `CAPI_QUALIFIED` row lacks. If the precondition fails, the control is invalid (reported, not passed) |
| **MQ-RW2b** (changed old-scope call) | in the old scope that contains `Owner_Authorize` (S5 `core/worldline-c_api.adb:1024-1027`), add a call `Worldline.Root_Custody_Phase.Legal (…)` | U-2 problem: the old scope's census gains `Worldline.Root_Custody_Phase.Legal` |
| MQ-RW3 | a declaration of an effective root identifier inside an RW scope, at any depth | (d1) problem |
| MQ-RW4 | `separate` in the C_API pair | (d4) problem |
| MQ-RW5 | a use clause in an RW scope beyond R-INV (vii)'s | R-INV problem |
| MU-RW1 | an RW routine whose prefix is not in `RW_SPARK_UNITS` | CV-UNITS problem |
| MU-RW2 | `RW_SPARK_UNITS` gains a unit of `CAPI_SPARK_UNITS` | CV-UNITS problem (rosters not disjoint) |
| ML-RW1 | an RW export placed inside the C-API relocated run of the layout | R-LAYOUT problem |
| PX-RW1 (positive) | every C-API table byte-identical to its last C-API stage value, and the unchanged C-API contexts, at each RW stage | no problem |
| PX-RW2 (positive) | an RW stage with its own `bool` and `case` rows and its own qualified inventories | no problem |
| **PX-RW3** (positive, unchanged old context, already-listed selector) | add the RW routine `Worldline.Requester_Correspondence.Decide`, whose simple name `Decide` is already listed (it is in both C-API name tables, `CAPI5/APPENDIX-BINDINGS.md:193`), with its calls only in its own RW scope, and change no old scope | no problem: every old scope's census is unchanged, because `Decide` was already a listed simple name |

The integration checks become IC-1 … IC-15: IC-11 and IC-12 as R4-43; IC-13, the U-2 re-observation at each RW stage; IC-14, the byte identity of every C-API table; **IC-15**, CV-UNITS at each RW stage. IC-10 stays OPEN until the admitted frame and installed compiler exist.

---

## V5-L. Response progress without an unavailable owner (V4-REQ-L; 06.3, 06.4, 09.5, 12.4; D-4a, D-8b)

Carried: v3 V-L.1, V-L.3 (with R4-44) and V-L.6 (C3-VL1, C3-VL3, C3-VL6, inside C4-B). V5-L replaces v4 V4-L.

### V5-L.1 Thread placement and locks (as v4 V4-L.1 and V4-L.3, restated)

- Protected sections run where the original runs them, under SL-0's single acquisition and the original non-reentrant `Gate.mutex`; v3's dedicated lane stays withdrawn.
- Registered-root I/O runs in its own executor with per-requester fair shares, holds no protected lock, and is revalidated inside a protected section.
- Callbacks take no lock and only complete futures.
- **Router.** Its lock is held only for the routing decision; it never awaits a collector, a custody event, closure or a reattach under its lock (NF-7). It routes from the custody state cached and refreshed on every custody commit: OW and IP requests to the store-custody owner (the front, or the worker by FRESH or RELAY); WL requests to the root route while the front owns, otherwise to the queue (V5-B.5); a request with no reachable owner to the queue. It returns at once.
- **Storage model.** Custody appends are `BEGIN IMMEDIATE` with `synchronous=FULL` in the custody database, a file separate from the store, executed off the event loop where the original runs blocking I/O (RC-3). The collector is its own task and holds neither `operation_lock` nor the router lock.

### V5-L.2 Who serves, and the authentic event that ends each added wait

Every protected request, mutating or not, needs the store-custody owner (NF5-1). The original's own waits are the daemon mutation lock for mutating operations (`rw/daemon.py:354-355`), `operation_lock` for every protected request (`rw/protected_operations.py:716-717`) and protected storage.

| Situation | Who serves | Added wait | The authentic event that ends it | If that event never comes |
|---|---|---|---|---|
| Front_Owned | the front, as original | none | — | — |
| Handoff window (Prepared … Roster_Evidence) | queued; then the worker or the front | the handoff steps | `CUSTODY_ACK (g)`; or `ABANDON (g)` / `HANDOFF_ABORT (g)` on failure, both by the front | the steps are local to the front; a front crash leads to V5-F.7's rows at restart |
| Worker owns, reachable | the worker by FRESH or RELAY, at once | one transfer or relay round trip | `REQUEST_INTAKE`, then the original handler | — |
| Worker owns, channel lost (front restarted, or the channel closed), worker alive | queued; then the worker | the reattach | `WORKER_REATTACHED (n)` (V5-L.3) | see the wedged row |
| Worker owns, alive, does not complete the reattach | queued | — | none | **stated difference**: this is the counterpart of an original daemon that does not respond, and nothing in the design ends it; the operator's existing remedies apply, and it is an OPEN fault-campaign item (OP-8). No deadline settles anything |
| Worker dead | queued; then the front of g+1 | collection of custody | `CUSTODY_RETURNED (g)` on the worker and namespace-init pidfds (kernel events, K-24), after `REQUEST_LOST` and `DRAIN_RECLAIMED`; no closure evidence needed | if a process in the coordinator's namespace keeps init alive, custody stays with the generation until it exits; stated condition |
| Unknown | queued | evidence | the Reconciler's `RECONCILED` on: a reattach (back to `Before_Unknown`), or the two pidfds terminal (`CUSTODY_RETURNED`) | as the two rows above |
| Missing closure (no `CLOSED_*` ever) | not a serving wait any more: custody returns by `CUSTODY_RETURNED`; the root row keeps its holds (`Retain_Uncertain`) and its U goes to quarantine and K4 | — | — | P stays retained for owner recovery, as an original Unknown row |
| Protected storage stalled | — | storage | storage resumes, as original | as original |
| A later WL request while a worker owns | queued for g+1, unless D-4a selects an option such as H (V5-D) | until g+1 | `FRONT_OWNED (g+1)` | **stated progress difference**, OPEN with D-4a |

**By request class** (each in the store-custody owner, with the original handler, guards and response):
- **`status`**: mutating and protected; may re-capture PRIME (NF4-11). Served by the custody owner; in the worker by transfer or RELAY.
- **`job.cancel`**: the original handler and `runner.cancel` in the custody owner; in the worker its stop reaches the dispatcher's `STOP_UNIT` (V5-B.6). No front stop (v4's M8 (c) withdrawn).
- **Owner routes and `quarantine.resolve`**: the original guard order and unresolved-gate exception, in the custody owner.
- **Non-mutating protected requests**: the same rule as all protected requests (NF5-1); they wait only for the added waits of the table and the original's own.

### V5-L.3 The reattach endpoint (new; DESIGN)

- **Endpoint.** At `CUSTODY_ACK (g)` the worker listens on an `AF_UNIX`, `SOCK_STREAM` socket at `<spool directory>/reattach-<g>`, mode 0600, inside its writable view **[unverified reasoning, K-26: reachability of the path across the mount namespaces]**. Its accept loop runs on the worker's event loop and holds no protected lock.
- **Finding the worker.** A front that has lost the channel (or a restarted front) reads the worker's host pid and start tick from the custody chain (the HELD and measured records), opens `pidfd_open (host_pid)`, and requires `/proc/<pid>/stat`'s start tick to equal the recorded one, so a reused pid is refused **[unverified reasoning, K-4]**.
- **Handshake,** in RELAY framing under `DOMAIN_REATTACH` = `worldline.root-worker-reattach-v1` followed by one zero byte, all MACs `Hmac_Sha256 (K, DOMAIN_REATTACH ‖ …)` verified natively (S2H): front `HELLO {g, seen_epoch, nonce_f}`; worker `CHALLENGE {g, nonce_f, nonce_w, current_epoch}`; front `PROOF {g, nonce_f, nonce_w, current_epoch + 1}`; the worker requires its peer's `SO_PEERCRED` uid 0, verifies the MAC, commits `WORKER_REATTACHED (current_epoch + 1)` (M4, `Legal` per V5-F.2) and answers `READY {n}`. The new connection is then the transfer and RELAY channel for epoch n; frames of earlier epochs are refused.
- **What it restores.** Reachability only. The old front's process-local state (client sockets, escrow read copies, the root operation's relayed result) died with it, exactly as a daemon crash loses its connections (V5-H.4, V5-F.7).
- **Non-claim.** Anyone holding the key can complete the handshake (P-A2).

### V5-L.4 The queue, without QUEUED events (replaces v4 V4-L.4)

Queue entries are durable `REQUEST_QUEUED` events and are never dropped. Each leaves the queue only by: transfer or RELAY to a reachable worker; service by the front of g+1; or the original response, error included, of the handler that serves it. None is a refusal for queueing, phase, correspondence or provider absence. **QUEUED progress events are withdrawn:** nothing is sent to a client that the original would not send, so no client compatibility question arises. Resource exhaustion of the queue itself makes the affected outcome UNKNOWN, never an accepted refusal (v3 V-L.6).

---

## V5-M. Additive controls added by v5

These join the additive roster (C2-17 with R3-9 and R4-6, and V4-M, carried in C4-VMNOP). Pure value fixtures need no root; lab controls need the operator (OP-4, OP-7, OP-8). **No original control is retired, and the frontier control is unchanged (C2-116).** v4's own additive controls stay, with one change that only strengthens: V4-M's "M8 admits … the M8 (c) stop" becomes "M8 refuses a front stop of a worker-owned generation's root on `job.cancel`", because M8 (c) is withdrawn (RR5-7).

- **V5-A** (static). Every new export's version and layout entries equal its wrapper's records (V5-A.1); a record with a field moved, a stride changed or a capacity too small gives `CoreUnavailable` or `WL_ABI_CAPACITY`, never a decision. Every existing export of V5-A.2 is byte-unchanged in the library's export table.
- **V5-B** (pure). Compaction with N's (b′) byte outside every original span keeps that byte non-zero in `Data2`; an input whose union plus constants just exceeds the arena moves to R3 and is decided by the original unit. RQ-1: for an IP operation, a rollover in each of W0, W1, W4, W5 gives exactly the serial route's records and costs, and no `Record_Launch_Intent` or `Record_Running` call is made; for a WL operation, W2 gives `HANDOFF_ABORT (Never_Dispatched)`, `Release_Hold` without CLOSED_WITNESS, `QUARANTINED` and the original error response, and W3 gives `HANDOFF_ABORT (Dispatched)`, the original failure stop and retained holds. CG-1: no route, control or acceptance argument counts the lane's workload refusal as a pass. Dispatcher (lab): a WL operation's runner launches, stops and observes its actor through `WorkerSystemdDispatcher`, with the original results and exceptions (CJ-DISP-1 … CJ-DISP-3).
- **V5-C** (pure). `Number_Canonical` accepts `-0.0`, `0.0`, `1e+16`, `1e-05`, `0.0001`, `1000000000000000.0`, `1.5`, `123.0`, and refuses `-0`, `-0.00`, `-1e-400`, `1e16`, `1E5`, `1.50`, `0.00001`, `1e309`, `1e-400` (each **[RC-5]**). A lexeme with E ≥ 309 or E ≤ −325 is decided without big-integer work, with the same result as the exact path on a vector at E = 308 and E = −324. `archive_equal` keeps −0.0's sign. Rollback: a restore that removes a referenced event → RT-14; a restore inside the tolerated append window → loads (expected non-detection); a restore removing only unreferenced trailing events → loads (expected non-detection).
- **V5-D** (none). Nothing is selected, so no accounting control is added; H's controls would be designed with its deltas on selection.
- **V5-E** (lab). `CHILD_READY` cannot be appended before `CHILD_AGREED` on the same m (refused by `Child_Event_Legal`); a sub-helper `REFUSE_CHILD` leads to `CHILD_ABORT` only, with no READY in the chain; a lost `COMMIT_CHILD_GO` leaves the actor unexecuted; a `COMMIT_CHILD_GO` with a different m is refused by the sub-helper; the Collector may commit `CHILD_ABORT` and `CHILD_CLOSED` after `CUSTODY_RETURNED`, the Worker may not after it; a library whose bytes differ from the argv's sha256 is refused before any decision. FD audits per V5-E.2 for every process; memfd payloads over the frame size are accepted.
- **V5-F** (pure). Every row of the root, request and descriptor relations, and each of XC-1 … XC-7, with a positive and a refusal. `HANDOFF_ABORT` after `TRANSFER_SENT` is refused; `CUSTODY_ACK` after `HANDOFF_ABORT` is refused (set ACK). `CLOSED_WITNESS` with an Intake subject is `Barrier_Subjects_Open`. `CUSTODY_RETURNED` without both pidfds terminal is refused. A REQUEST and a DESCRIPTOR subject with the same string do not collide on replay. Every row of V5-F.7 at restart, each idempotent.
- **V5-G** (pure and lab). The eight steps of V5-G.1 end in Front_Owned (g+1) with no CLOSED event; RT-21 … RT-29 with their material, actions and exception mapping, including a refusal inside `recover_committed` that stays a startup refusal.
- **V5-H** (lab). A reader is never registered before its `ARMED` fsync; the fold marks an interval that ends in `CHUNK` records as `READ_GAP_POSSIBLE`; a front crash in windows A … E with the front as only reader gives `OUTPUT_CUSTODY_LOST`, never a reattach; RT-26 and RT-27 reattach only through a live front copy; kcmp with the exact operands of V5-H.3; K-25's writer behaviour.
- **V5-I** (lab). `Root_Admission_Join` in Transfer_Sent and Roster_Evidence → `Join_Ready`, and in Worker_Owned → `Phase_Mismatch`; `Transfer_Join` before `CUSTODY_ACK` → `Phase_Mismatch`. Each presence value of V5-I.2 tested with its field present and absent. RELAY: a replayed, reordered, cross-gate, cross-request and earlier-epoch frame → `Relay_Frame_Invalid`; a front re-read raising `PEER_REQUEST_MISMATCH` → the worker raises it at that gate and the original exception path follows; channel loss → the closed-connection exception of RC-10.
- **V5-J** (lab). A freshly provisioned database loads with an ORIGIN head and `foreign_keys=ON`; an ORIGIN head with a non-NULL `event_id`, an EVENT head with a NULL one, a non-minimal quantity BLOB, a quantity stored as INTEGER, and a state row differing from the fold are each refused. A genesis file that is canonical JSON whose decoded value differs from the archive is refused; equal bytes are never required. Migration: P2 at a new path with new J2 and G2; J1 untouched (sha256 equal before and after); the retained verifier passes with the retained descriptor and P1, and fails by name if either changes.
- **V5-K** (static). MX-RW1 … MX-RW3, MQ-RW1, MQ-RW2a, MQ-RW2b, MQ-RW3 … MQ-RW5, MU-RW1, MU-RW2, ML-RW1, PX-RW1 … PX-RW3, IC-13 … IC-15.
- **V5-L** (lab). Each row of V5-L.2 with its ending event; a reattach handshake with a wrong MAC, a non-root peer or a stale epoch is refused; a restarted front serves a request through the reattached worker; no QUEUED event is ever sent.

## V5-N. Measurement items and installed-runtime checks added by v5

K items belong to OP-7's existing D-8b reservation of original and additive kernel measurements in an authorized lab, with the range repair of R5-16 and R5-17; its owner and kind are unchanged. RC items are ordinary lead-owned installed-runtime checks.

| Id | Question | Used in |
|---|---|---|
| K-24 | When the init of a PID namespace exits, every other process of that namespace has exited, and closed its descriptors, before the init's pidfd reports terminal | V5-F.2 `CUSTODY_RETURNED`, V5-L.2 |
| K-25 | With a retained non-reading read copy, a writer whose active reader died blocks when the pipe is full instead of receiving `EPIPE`; the timing of both cases | V5-H.3 |
| K-26 | Descriptors received by `SCM_RIGHTS` with `MSG_CMSG_CLOEXEC` are close-on-exec; sealed `memfd` seals hold against the sender; an `AF_UNIX` path socket in the spool directory is reachable from the front across the worker's mount namespace | V5-E.2, V5-E.3, V5-L.3 |
| K-27 | Loading a library through `/proc/self/fd/N` of a sealed `memfd` maps exactly the sealed bytes | V5-E.3 |
| RC-7 | The installed SQLite's semantics for a NULL foreign-key child, `typeof`, BLOB `substr` and `length`, BLOB comparison in keys and `CHECK`s, and `PRAGMA foreign_key_check` | V5-J.2, V5-J.3 |
| RC-9 | The installed daemon service's resource properties, read back, for option H's coordinator limits | V5-D |
| RC-10 | The exception that the original `KernelPeer.observation ()` raises for a closed client connection on the installed CPython | V5-I.5 |

RC-5 (V4-N, carried) now also covers every constant listed under "What RC-5 must confirm" in V5-C.3. RC-8 is not used.

## V5-O. Everything that remains OPEN (adds to V4-O, carried in C4-VMNOP)

- **All original obligations.** OB-001 … OB-219, every one OPEN with no closure credited (the v4 review's `open_obligations`, observed). Nothing here closes any of them.
- **Required changes, clauses and rulings.** V4-REQ-A … V4-REQ-L, V3-REQ-A … V3-REQ-L, V2-REQ-A … V2-REQ-L, RQ-1 … RQ-5, the inherited RC items other than RC-05 and RC-10, and every PARTIALLY_CLOSED or NOT_CLOSED clause and ruling, until reviewed with source, proofs and controls on matching source.
- **The review's open design dependencies,** verbatim from `open_design_dependencies`: "All matching-source implementation/producer/body/reference/caller/flow/RTE/termination/native semantic and cost evidence"; "RQ-2 through RQ-5 where carried"; "All CAPI6R open obligations and implementation/stage reviews"; "ROOT_WORKER_INTEGRATION; L-CAPI-P; G-PROT; IC-10"; "All original ordinary/lifetime/genuine root/task/child/owner/provider/fault controls"; "All lemmas; full-domain embedding/residual/cost/representability obligations"; "Schemas/provisioners and migration"; "D-4a accounting choice and every existing operator reservation"; "All kernel measurements and installed-runtime checks; confinement; truthful producer currentness"; "Hosted assurance; publication/deployment/final Phase One acceptance".
- **Containment gap CG-1** and the dispatcher's CJ-DISP-1 … CJ-DISP-3 (V5-B.6).
- **New statements to prove:** X-1 … X-10 bodies, `Post`s and costs; CJ-JSON; `Number_Canonical` with the sign channel and `Repr`; the three relations, XC-1 … XC-7, OWN-1, the fold; `Child_Event_Legal` with the candidate stage; `Root_Admission_Join` and `relay_frame`; the union law of V5-B.1.
- **Premises** P-A1 … P-A4 as obligations (V5-C.1), and the rollback non-claims of V5-C.2.
- **Accounting.** No option selected; H's deltas D-H1 … D-H5 undesigned; the later-WL-request progress difference (V5-L.2).
- **Progress conditions stated, not closed:** a worker that never completes a reattach; a namespace that keeps its init alive (V5-L.2).
- **Measurements and checks.** K-1 … K-27 (OP-7); RC-1 … RC-7, RC-9, RC-10.
- **Process.** The independent actual gpt-6.1-sol review of v5, of every slice and of the full lane.

## V5-P. Non-claims (adds to V4-P, carried in C4-VMNOP)

- v5 reviews, accepts, proves and authorizes nothing, and adds no approval gate. Every original obligation stays OPEN.
- Nothing was compiled, run, imported, proved, tested or measured.
- No equivalence of the root route with the serial route is claimed for any operation that the serial route runs in process; such operations no longer take the root route. For WL operations the root route's additions are listed as differences.
- The lane's workload refusal preserves nothing; it is CG-1.
- No pipe is claimed recoverable unless a live process holds a read end. Lost output is detected and recorded UNKNOWN, never recovered.
- Rollback detection is exactly V5-C.2's; no earlier valid prefix beyond it is claimed detectable.
- `Number_Canonical`'s constants are the author's reading until RC-5; JACKAL's J5-1 … J5-4 compare the stated constants, they do not show that the installed CPython uses them.
- No accounting option, cap, prerequisite or policy field is selected or added. H is offered for D-4a, not chosen.
- v4's M8 (c) is withdrawn rather than repaired; no front stop of a worker-owned generation is claimed to correspond to `job.cancel`.
- No liveness is claimed for a worker that never completes a reattach, or for a namespace whose init stays alive.
- SIA recall is not evidence and is not used as evidence.

---

## Appendix A. JACKAL

Four numerals were derived by arithmetic, all in V5-C.3, each computed by `jackal_exact` in one group of four (status `exact`, lane `rat`, `formal=false`, assurance "exact rational arithmetic (not yet checker-covered)", evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`). Each result is positive; the exact values are in `jackal.json`.

| Id | `parsed=` | Result used |
|---|---|---|
| J5-1 | `10^309-(2^1024-2^970)` | positive: 10^309 > `T_ovf` |
| J5-2 | `2^1024-2^970-10^308` | positive: `T_ovf` > 10^308 |
| J5-3 | `2^-1075-10^-324` | positive: 2^−1075 > 10^−324 |
| J5-4 | `10^-323-2^-1075` | positive: 10^−323 > 2^−1075 |

The consequence ceiling is informational about arithmetic only; whether `T_ovf` and 2^−1075 are the installed runtime's thresholds is RC-5. Inside carried slices, v2's J01 … J18 keep their status.

## Appendix B. Inputs bound while drafting v5 (sha256, observed)

v4's list (Appendix B, superseded text) and v3's (C3-APB, carried) were not re-hashed one by one except where listed here. New or newly cited inputs:

```
f65629cb45e6e8a5ea798f5130a7f98e1d365758a7175343444f4022864efbda  D4/SEAM-DESIGN.md
92a814a4883d3e01680dbfeae82cb7889b038930bc4e21bcaefd39b622a2a86c  D4/seams.json
4d556a457caa268c80b5d7ef4edae949433034ffeb950a5b4d2f8a29fcafcfab  D4/jackal.json
0bd92ccd556e39a358a5e93db5a57fe55ba206080d7b6dc1f033508d7f9c66e4  D4/AUTHOR-NOTES.md
340a62191e9f0c4135dc94a0282c033a64c3a55ac1884778fd0f8836c3fc95d4  D4R/REVIEW.md
d857f8ddd04f430097099f62688fb3f848d687c2f171f556db68ddefb16ba714  D4R/review.json
58e3312e3ff655f438b32524a8a0034d0fac1b55815af20fd7207cb3e754529f  D4R/checks.json
eef0ff2ca7816ddb79749f8cbddee7c3caa2c5f005dcace6dd3965462d010ee4  D4R/review-freeze.json
a0f2f411d654f1cce472a1ad2a13d3c082fff42def050c5ed4694a8b094d07a0  D3/SEAM-DESIGN.md
db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5  D2/SEAM-DESIGN.md
f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2  CAPI5/APPENDIX-BINDINGS.md
9f9f3dfa897d0c320226df39c89bc5c156fc87ebc3e24959ab0c08bba5db1946  CAPI6/APPENDIX-BINDINGS.md
0a17c0efb95904ee865182a20d3bcabceeef93b1cc3639687aab27696339f35b  S5/core/worldline-c_api.adb
2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237  P1/HANDOFF.md
9d448dcc8741b698750147a8a0ccb9aaaf0215cba6a16c702facde394b6b52e4  rw/daemon.py
9031e0bdd6fd10e911a908f1e15d8241aed94b0445946b5da45d821899133710  rw/runner.py
fe8dc07d25d5da50d8678e644c1e19c076226774436abb56079aff3b02039e91  rw/store.py
1022187a02c19fb25ecfcafcc9a43a91e5ab62cf243ae38014c14d4c73463ade  rw/client_peer.py
ea1a01df19ddef2418d4e4ec14dab6cea1eaa70423172eedea36a48ec383f0cb  rw/protected_operations.py
15cbbfcd61a98da55a704af16fd5d853a3af64bc0aba84599d936440ba8f74a1  rw/protected_root_worker.py
f1089a091399dd0c1a0602aebb027edff4737fbf562750e95e3a0c561067f723  rw/protected_root_resource.py
37b58317dac57e21888a01c7b1254d20ec94e85cefe094e68df40fa4c5771d43  rw/protected_root_supervisor.py
2510f8edac3937509d36bc3b38511af89f81ecf9a5eff77fefc87f927f3aa811  rw/root_worker_journal.py
acf5ac0fb4035d53c3e053e7a3a10b4f29fd29d5bc0aefbdb0d9de181665080f  rw/protected_scoped_resource_runtime.py
e062ff0335d312366c90517cca21c73c0879d0b95de469840c36cea46250248f  rw/protected_scoped_resource_service.py
76ae777b375b3ad2785399c73d9e14055b2f6cca58a30e2078b2b847ac87176e  rw/resource_child_execution.py
14175c7da56f0c6b3425157e68bda7e19d9451cddac6dc9fc45ec3927a1588a9  rw/resource_run_ledger.py
e506348f1efb6615151114a21ef238aca4dd0e81592aad7f1bb64b184ddd8076  rw/resource_scoped_run_ledger.py
9f123d62282c8189a9b7b5f300b37d94d2544626820ca5d08ee9a72c81cab7f2  rw/chain_authority.py
e0148f27abfa652d8594a87660fc996e1e402101593f348824cae6a08dd41c6f  rw/canonical_exchange_kernel.py
b7c44b329c8c92701c06fcdfd7b5e6692b8b164ae7f699729afe60d0d30036a0  rw/canonical_operation_kernel.py
0fc7f5fde1357f1a97da2ce1977c60290cb15bb4e4e5b77205b4e678f6a5f482  rw/operation_authority_kernel.py
68740eda2668faddfe28bd3a8ac1720adac3de32f0bc68d8d95e45f94170d07b  rw/root_worker_closed.py
17ccd237864d4b11a19fbd836ad9e585df718558d0d0c83569c1397761cb7aba  rw/controller.py
710d37c77de105bdd62d96e1ce31d5b0ad79fcbd7ae8b7e556bd1b7656462784  rw/linux/systemd.py
f2a321d07e667e80f4359634e8e4a956b555368b8d449e8c8c930b8f511aeff7  R/protected-root/native_root_worker_supervisor_v1.c
ea4397f3b8b1e4561603253dddcc5f9515116f4096d35b8ead50fbfe70470e0d  R/core/resource_quantities.ads
```

These are byte identities at the time of reading. They establish no authenticity, installed state or atomic snapshot.

## Appendix C. Slice and quote verification

A read-only Python script read the v2, v3 and v4 designs, the sealed v4 review and this file. It printed to standard output and wrote no file. It checked (observed; the final run is in AUTHOR-NOTES §2):
- v4 `SEAM-DESIGN.md`: sha256 `f65629cb…efbda`, 1911 lines, ending with a newline;
- every row of §B.1: the sha256 of the stated v4 lines equals the stated hash; no two slices overlap; every v4 line is in a slice, in a superseded range of §B.3, or is empty or `---`;
- every R5 replacement: the quoted `v4:` or `v3:` text equals the stated lines exactly; each v4 target lies inside its stated C4 slice; each v3 target lies inside its stated C3 slice (as v4's §B.1 states the C3 ranges) and is replaced by no R4; no line is targeted twice;
- W5-1 and W5-2: the withdrawn v2 and v3 ranges lie inside C2-62 and C3-VF5;
- every quotation in §A from the sealed `review.json`: equal to the field it quotes;
- every markdown table: each row has its header's cell count.

## Appendix D. Companion file identities

Observed with `sha256sum` and `wc -c` after the files were written. This file cannot contain its own hash; `seams.json` records it, and the handback records both.

| File | sha256 | Bytes |
|---|---|---|
| `jackal.json` | `9adaaa83960f7064552dee1f85ffa38ad5191f0e6d6cd02321b287121e931628` | 4827 |
| `AUTHOR-NOTES.md` | `d6e16bdfb23b2544218694508144ba32f72ab3c23f79fa9dcb0f2117d324b836` | 9342 |
| `seams.json` | recorded in the handback (it binds this file's hash) | — |
