# Root-worker runtime lane: seam design v4

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent, author role) |
| Date | 2026-10-05 |
| Status | **DRAFT_FOR_GPT61_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author reviews, accepts and closes nothing; author checks are self-checks. Every original obligation (OB-001 … OB-219), accepted case, deterministic fixture, control, contract, threshold, proof floor and scope remains **OPEN** and unchanged. |
| Supersedes | v3 `SEAM-DESIGN.md` (sha256 `a0f2f411d654f1cce472a1ad2a13d3c082fff42def050c5ed4694a8b094d07a0`, 217264 bytes, 2128 lines), v3 `seams.json` (`093f31176dd9560a236b8ad00f5fd28a683c810c8f400d646631318ca1b582e8`), v3 `jackal.json` (`8cce45e34f12d9d7976cb9b04ab6ac47e3a99ae8cacc22708a84abe06ec0c024`) and v3 `AUTHOR-NOTES.md` (`dd382e1b0f74e825735e168ab6856b1c85e93f9a39312f3bc15019faf390a0ea`). All were read only and re-hashed unchanged. |
| Answers | The sealed actual gpt-6.1-sol review of v3 in `WT/designs/claude-root-worker-seam-design-v3/review/gpt61-v1/`: `REVIEW.md` `1e1c5ef8bb396d7e3fe75b63bb9c788616dfb6b26561d729c2d867064cfea879` (84061 bytes), `review.json` `35b264e77922b028443b6b36718f0db2c14efc14f06746dc7510c727141463cf` (141527), `checks.json` `63bcb753990a9dbc0d2caf3a49db68baa103f5720cf7546bb9e7af68083c05ed` (112304), `review-freeze.json` `c52bd9ee470d1b29dbfcd44a1bd00331a922af6323ead6a601db65814c09de40`. The freeze names actual model `gpt-6.1-sol`, different from the author, and lists the first three files with exactly these hashes and sizes (recomputed, equal). Verdict **ENDORSED_WITH_REQUIRED_CHANGES**: V2-REQ-A … V2-REQ-L and RQ-1 PARTIALLY_CLOSED; D-2b CLOSED_AT_DESIGN_LEVEL; every other ruling PARTIALLY_CLOSED; NF-1 … NF-11 verified statically; required changes V3-REQ-A … V3-REQ-L. |
| C-API status | **CAPI5R**, the sealed actual gpt-6.1-sol review of C-API design v5 (`review.json` `800880d44bff4b234c82cc392a3008fd4d37139b0827d070120cf299370f403b`, `REVIEW.md` `73e82489706e03ca465e7dea2aed1823df0b50a8ce1c5ab0555c545579dc34d8`, `checks.json` `c1398253713aa6d42ed11fda5194502ccae5a64825b36ef8100206f7d40719ef`, freeze `91bddf1a46763251940db658f5115cd13ab9de4aa67c0a41ae169de165649af1`): ENDORSED_WITH_REQUIRED_CHANGES, required changes V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE. **CAPI6R**, the sealed actual gpt-6.1-sol review of C-API design v6 (`review.json` `bcfa259f8690c492b9284ef1ed9549efa7a5d3899edc1fbd5a0ae2ab7234d128`, `REVIEW.md` `12cfde3c3eed993b6056dc75d901710bdee1273e67cfe150a9648f99627da161`, `checks.json` `12642ce4501f12b0a608264d9bd93a23f39fd6c7d2c85cee69d94a91a3e2f284`, freeze `15fc9f07786eba0e0c1d3cde0250c8696e8ebeb96961ce6c22aeea2fcc590742`) of CAPI6 `DESIGN.md` `cfa0dca9e275e878b958f2f8da6b5cf54824534867773382965f2a887e98a417`: ENDORSED, no required changes; V5-RC4-GATE-EXCEPTION, V5-RC4-QUAL-CAPTURE, V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 CLOSED_AT_DESIGN_LEVEL only; ROOT_WORKER_INTEGRATION "OPEN; no ruling on the other lane or integration order". Both freezes name `gpt-6.1-sol`, different from the author, and match their files (recomputed). The PK-0 packet in progress under `WT/packets/capi-pk0/` was not read. |
| Scope | Design only, for the draft lane `W/work/protected-original-root-worker-repair-v1` (status `INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY`). The lane draft is someone else's unreviewed source and was not touched. v4 grants no execution, proof, build, test, review, operator or acceptance authority, and adds no approval gate. |
| Location | `WT/designs/claude-root-worker-seam-design-v4/` |
| **What this document consists of** | v4 is (1) the text of this file; (2) the v3 `SEAM-DESIGN.md` line ranges listed in §B.1, each bound by the sha256 of its exact bytes, with the quoted replacements R4-1 … R4-64 of §B.2 applied; (3) transitively, everything v3 carried: the v2 slices that v3 binds in its §B.1 (inside slice C3-B) with v3's R3 replacements as amended by R4, and the v1 slices that v2 binds in its Appendix C (slice C2-APC). Every other v3 text is superseded by the map of §B.3. |
| Companion files | `seams.json` (machine twin, same schema family), `jackal.json` (JACKAL record), `AUTHOR-NOTES.md` (process record, uncertainties, OPEN items). Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools. Bash was used only for read-only inspection (AUTHOR-NOTES §2). |

Every statement about source is **static**: read from files, or reasoned from what was read. Nothing was compiled, run, imported, proved, tested or measured. Kernel, systemd, interpreter and Ada-visibility statements marked **[unverified reasoning]** are the author's reading and name their evidence item.

---

## A. Closure tables

"Answer" is a design statement for the reviewer. The author closes nothing. Every proof, native, control, physical and acceptance obligation stays OPEN.

### A.1 Required changes V3-REQ-A … V3-REQ-L

Each change is quoted verbatim from the sealed `review.json` `required_changes[].change`.

| Id | Required change (verbatim) | v4 answer | Where |
|---|---|---|---|
| V3-REQ-A | "Finish the typed V1/V2 consumer, current-fact, producer and wrapper contracts and the native-input dependencies. Reconcile V-M's preparation order with S6 depending on S1, and account for the HMAC/roster/request-product units. Keep original families/ABIs and accepted routes until the authentic successor is available." | A contract per consumer: inputs, current-fact packet and its producer, producer pre/post, wrapper dispatch and ABI. A native-input dependency table. Family selection keeps V1 and every original route until an authentic V2 producer exists, with no interim refusal (R4-18). The graph adds S2H (HMAC and chain), S12 (child relation) and the request product (S8, S9), and the preparation order follows every edge: S1 precedes S6. | V4-A; R4-18 |
| V3-REQ-B | "Give one consistent witness/Rebase specification covering multiframe and saturated arenas: reconcile W8 with frame-local universe heads, reconcile L-RB-1 with compaction, and reconcile W3 with short-circuit authority refusal. Audit every extra conjunct and residual class; preserve all original inputs/fixtures and leave any unclosed correspondence obligation OPEN. Complete RQ-1's root/serial exception and recovery/cost mapping through rollover without moving native guards or weakening retained authority." | W8 and W2 become frame-local and reduce to themselves on one frame (R4-46, R4-58). L-RB-1 splits into a positional variant and a compaction variant over one position-independence audit (R4-45, R4-2). L-SAT-1′ gives a positive N on every input, C1 refusal included, so W3 holds unconditionally (R4-20). The audit tables every extra conjunct and every residual class, adds the unclassified residual R0, and keeps CV-R OPEN (R4-14, R4-15, R4-19). RQ-1: the root route takes the serial route's exact guard and exception order, and every rollover window is mapped to its native refusal, durable records, physical outcome, recovery and cost. No guard moves and Retained_Join is unchanged. | V4-B |
| V3-REQ-C | "Specify independently selected issuer-key/genesis/current-head custody and its native/producer correspondence, initial authentication and anti-rollback limits; do not treat self-consistent HMAC/hash inputs as authentic selection. Complete both unchanged JSON-form extraction semantics, including numeric canonicality and native domain/cost obligations. Make P3's mapping scope and all non-claims identical in the replacement, prose and twin; preserve the original executed-source target." | The selection chain (installation → descriptor → plan → genesis and journal; fixed-path key) is stated with its authenticity premise P-A1 … P-A4, the native/producer split, one-shot initial authentication and the anti-rollback limits. v3's claim that HMAC verification authenticates the genesis is withdrawn (R4-22). Both forms get native number canonicality, no depth cap, and stated domain and cost obligations (R4-21). P3 has one definition, every file-backed mapping, identical in R4-3, R4-23, V4-C.4 and the twin. | V4-C |
| V3-REQ-D | "Complete the full-domain kind/grant/owner/amount/rollover enforcement and native-cost design comparison. Keep sampling separate from protected future capacity and compare option F against the preserved immutable outer reservation bound. Leave every actual policy selection to the existing D-4a decision, with no new cap, provider prerequisite, borrowing or accepted native failure." | A full-domain matrix (kind, grant, owner, amount, rollover, physical enforcement, immutable outer bound, double counting, interference, availability, native cost, added prerequisites) for options A, B, C, E, F, F′ and G. F as stated raises an admitted outer bound, so it fails AO-5 and inherits no permission; `SET_ROOT_CEILING` is withdrawn (R4-24, R4-28). Sampling stays a sample (v3 V-D.3). No option is selected. | V4-D |
| V3-REQ-E | "Complete the exact E1-E12 successor event/command/native relation, ABI/argv/env/stdin/EOF/FD inheritance roster and Child_Ready enforcement at COMMIT_CHILD. Enumerate every retained capability, descriptor, writable view, IPC/device/control path and justified privilege; define authentic helper ticket/decision/ancestry bindings. Retain all original coordinator/actor containment and immutable ceiling obligations and unperformed measurement status." | The relation `Child_Event_Legal` over E1 … E12 and their failure and alternative events. The exact ABI, argv, env, stdin, EOF and FD roster of each process. COMMIT_CHILD is enforced by the relaying sub-helper, which runs the native decision itself over inputs bound to its own ticket, relayed measurement and observed ancestry. An exhaustive inventory of retained authority: every capability, descriptor, writable view, IPC path, device and control path. Original containment and immutable ceilings are kept, and every measurement stays unperformed. | V4-E; R4-26 … R4-28, R4-54, R4-59 … R4-64 |
| V3-REQ-F | "Define the complete native custody State/Event/Legal_Reference/Next/Mutation_Allowed relation with all request/descriptor transitions and actual mutations. Apply custody gates to operation-journal and scoped-ledger mutations as well as store/custody writes. Harmonize STOP_INTENT spooling and original cancellation/helper-stop permissions. Include subject_kind in replay identity and complete generation/initial-state/CAS/alternative joins, preserving exclusive branches." | Types; `Legal_Reference` as complete root, request and descriptor transition tables; `Next`; `Mutation_Allowed` for M1 … M11, enforced at the journal, ledger and store choke points. M6 permits the front's STOP_INTENT spooling. M8 permits the original cancellation, failure-capture and helper stops and never settles. The replay identity includes `subject_kind`. The generation, initial-state, CAS and alternative joins are given, and ACK/ABANDON and both INTAKE/ABANDON pairs stay exclusive. | V4-F; R4-29, R4-48, R4-49 |
| V3-REQ-G | "Reconcile r3 with genuine Never_Launched release while retaining the full CLOSED_WITNESS floor for every possibly launched row. Preserve original terminal manager/pidfd/wait semantics without an unjustified new inactive-unit condition or reset cycle. Specify durable reconstruction/physical material independent of HANDLER_TERMINAL and the complete automatic retained-result, EFFECT_OBSERVED, SETTLED, broker-progress and post-intake crash routes; retain COMMITTED and first RESULT_CAPTURE immutability." | r3′ permits release of a genuine `Never_Dispatched`/`Never_Launched` row, and every row with a dispatch fact keeps the full CLOSED_WITNESS floor (R4-47). CLOSED_OUTER is exactly the original helper-pidfd, launcher-wait and `MainPID = 0` test (R4-30); unit reset stays after CLOSED_WITNESS (C2-68). The reconstruction seed is the custody intent frame's `root_native` event and `original_native_use` plus the front's own CLOSED events, with HANDLER_TERMINAL optional. RT-21 … RT-27 add the routes. COMMITTED and the first RESULT_CAPTURE stay immutable. | V4-G |
| V3-REQ-H | "Cover kernel-read-to-spool and kernel-write-to-durable-W crash/cancellation windows, including detection of unretained bytes. Define reconstruction after closing transports, complete before/after INTAKE and RELEASE failure/restart behavior, and exact writer-duplicate ownership/EOF rules. Make the product mutation gates authorize the same quiescence/spooling protocol. Preserve full LIVE/UNKNOWN rosters and authentic reapers and keep uncertainty holds." | Durable read-armed and write-armed intervals detect, at every crash or cancellation window, possibly unretained bytes and unknown write positions, and turn them into recorded UNKNOWN completeness. Reattachment after a closed transport. A complete failure and restart table before and after INTAKE and RELEASE. Exactly one writing owner, explicit duplicate-close points, and EOF only when the last write description closes. M6 and M7 authorize exactly this protocol. Rosters, reapers and holds are kept. | V4-H; R4-32 … R4-36 |
| V3-REQ-I | "Separate pre-intake authenticated transfer/head validation from post-intake serving authority so Join can authorize intake without requiring its own future event. Type and decode every request/operation/transaction/reservation/source/custody operand, with complete per-gate mode contracts. Distinguish user-namespace equality from deliberately different PID-namespace correspondence. Preserve optional corroboration and define authentic queued-not-refused progress for requests that cannot be joined, including status/cancel/recovery under live/UNKNOWN/stalled custody." | `Transfer_Join` validates the authenticated `REQUEST_TRANSFER_INTENT` head before intake and authorizes the intake CAS. `Serving_Join` uses the committed `REQUEST_INTAKE` after it. Every operand is typed and decoded, and each of the gates has a mode contract. User-namespace equality is separate from PID-namespace correspondence, which is never an equality. Corroboration stays optional. A request that cannot be FRESH-joined is served in RELAY mode, with the front's original re-read at every gate use. It waits only when no owner is reachable, under V4-L's progress conditions. | V4-I; R4-7 … R4-10, R4-52 |
| V3-REQ-J | "Finish the exact startup/loader/schema/tool/provisioner selection union, one-shot initial genesis/event/head/state authentication and prior-v1 migration paths, with no implicit creation or re-genesis. Complete each original recovery/owner mapping and keep plan-v1 consistently named. Retain exact v1 frontier/version behavior and additive v2 controls." | Exact tool keys and provisioner entries. One-shot authentication of genesis, initial event, head and state. Three prior-v1 migration paths, with a live v1 journal refused until resolved. No implicit creation and no re-genesis. Every original recovery and owner branch is mapped (V4-G.4), and the owner plan is plan-v1 everywhere (V4-O). v1 and the frontier control are unchanged. | V4-J; R4-16, R4-37 … R4-40, R4-53 |
| V3-REQ-K | "Bind the sealed C-API v5 review and carry both V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE as unmet dependencies. Hard-bind the sole staged G21c/Finalization_Decide/O exception independently of mutable tables and forbid any RW assignment exception; cover every capturing with-clause prefix/ancestor. Define the append-only canonical-name/scope inventory union and affected-stage controls, preserving GE1-GE9, old residuals/clauses, the complete stage floor and the gate chain." | Both sealed reviews are bound. Both v5 repairs are carried as dependencies, which CAPI6R closes at design level only, so they stay unmet for implementation, stage review and controls. RW stages compose under CAPI6's fixed `CAPI_WFX_PROTOCOL`: CR5 and CR6 run over the union gate table, so no RW row can be `wfx` and no RW key can enter `CAPI_GATE_EXCLUSIVE`. (d1)–(d4) run over the union root and simple-name sets, including every prefix of every RW with clause. Union rules U-1 … U-8, with affected-stage controls. GE1–GE9, residuals, clauses, the floor and the gate chain are preserved. | V4-K; R4-4, R4-11, R4-12, R4-17, R4-41 … R4-43 |
| V3-REQ-L | "Specify protected status/cancel/recovery response progress through shared asyncio/thread locks, stalled protected storage, registered I/O and executor occupancy, preserving original authorization at mutation. Reconcile the no-refusal queue path with that progress model. Apply all repairs to prose and seams.json, including preparation order, plan version, complete K-15..K-21 range and current sealed C-API dependency status. Retain non-reentrant Gate, SL-0 and separate A1 review lineage; add no approval gate." | A progress model per request class, through every shared lock, storage stall, registered I/O path and executor. v3's single-thread protected lane is withdrawn because it could serialize more than the original does. The router never awaits closure. Queue, relay and transfer are reconciled with the model. The prose and the twin are repaired together: preparation order, plan-v1, the K-15 … K-23 range (K-22 and K-23 are new), and the sealed C-API status. Gate, SL-0 and the A1 lineage are kept, and no approval gate is added. | V4-L; R4-1, R4-5, R4-44, R4-55 |

### A.2 RQ-1

| Item | Review text (verbatim, `review.json` `rq1.rollover_tradeoff`) | v4 answer | Where |
|---|---|---|---|
| RQ-1 (PARTIALLY_CLOSED) | "Conditional on all other pre-effect conjuncts, scope/universe rollover now passes pre-effect, writes EFFECT_INTENT, and can fail Record_Launch_Intent before dispatch or Record_Running after HELD. The original quarantine/K4 route is the intended outcome. That is a changed durable path and physical classification; the complete root/serial exception and known/uncertain recovery mapping and accepted-case costs are not proved. Head-only changes do not by themselves trigger this specific Context_Changed guard, but other original native/source gates still apply." | The durable path is shown, statically, to be the original serial route's own path for the same refusal point (`rw/protected_operations.py:742-768`). It is not a v4 change. The root route is put on the identical guard, boundary and exception order (V4-B.5). Each rollover window has its native refusal, durable U records, physical classification, automatic or owner recovery and cost (V4-B.6). RQ-1 stays OPEN until fixtures and proofs exist. | V4-B.5, V4-B.6 |

### A.3 V2-REQ-A … V2-REQ-L (each PARTIALLY_CLOSED)

The remaining gap is quoted from `review.json` `required_change_detail`. Each is answered by the V3-REQ with the same letter.

| Id | Remaining gap (verbatim) | Answered by |
|---|---|---|
| V2-REQ-A | "Typed families and V2 consumer names are supplied. Complete consumed native input/producer/ABI contracts and reconcile the declared graph with its preparation order; family selection must not substitute an interim refusal for an original accepted case." | V3-REQ-A (V4-A; R4-18) |
| V2-REQ-B | "The multiframe construction contradicts carried W8; compaction contradicts carried L-RB-1; the C1-refusal factor shortcut contradicts unconditional W3. R1-R3 completeness and original-domain correspondence remain unestablished." | V3-REQ-B (V4-B) |
| V2-REQ-C | "Container extraction and roster joins are better specified, but native key/genesis/current-head trust is not independently established, numeric canonicality remains Python-only, and P3 has conflicting executable-only versus all-file-backed coverage." | V3-REQ-C (V4-C) |
| V2-REQ-D | "False future-capacity and memory_high claims are withdrawn. No accounting/enforcement/native-cost option establishes the full target; option F is unselected and must preserve the immutable outer reservation bound." | V3-REQ-D (V4-D) |
| V2-REQ-E | "Create/GO_FORK/measure/decide/ACK/exec ordering is repaired. Exact successor event/FD/native-command authorization and the exhaustive coordinator authority inventory remain incomplete." | V3-REQ-E (V4-E) |
| V2-REQ-F | "Subject states, DDL, alternatives and replay-before-CAS improve the design. Legal/Next is not a complete product relation; actual mutation gates conflict with other sections, and replay identity omits subject_kind." | V3-REQ-F (V4-F) |
| V2-REQ-G | "Typed physical futures and first-capture recovery without handler terminal are supplied. Inactive-unit closure is an additional condition beyond the original terminal check; Never_Launched release conflicts with r3; complete post-intake and recovery-seed paths remain unspecified." | V3-REQ-G (V4-G) |
| V2-REQ-H | "Stop intent and validate-before-intake order are supplied. Kernel-read-to-spool and write-to-durable-W windows, consumer reconstruction, retained writer duplicates and post-intake/release failures are not covered coherently." | V3-REQ-H (V4-H) |
| V2-REQ-I | "Optional corroboration, typed modes and the observed exact gate inventory improve the design. J8 requires the intake event before the Join that authorizes it; namespace comparisons and native join operands are incomplete; queued fallback does not establish protected response progress." | V3-REQ-I (V4-I) |
| V2-REQ-J | "Version union, exclusive creation and no missing-state initialization are retained. Exact tool/provisioner selection, genesis/head initialization, prior-v1 migration paths and every automatic recovery state still need a consistent specification." | V3-REQ-J (V4-J, V4-G.4) |
| V2-REQ-K | "The stage floor, dependency chain, new-scope qualifier inventory and no root-worker assignment exception are sound directions. Both sealed C-API reviews keep gate/alias closure open; the v5 sole-exception and with-prefix capture repairs are not incorporated." | V3-REQ-K (V4-K) |
| V2-REQ-L | "Single-acquisition Gate discipline, thread placement and callback constraints are normative. Status/cancel/recovery and declined intake can wait indefinitely behind custody or stalled protected storage; response progress and prose/twin consistency remain incomplete." | V3-REQ-L (V4-L) |

The inherited v1 required changes keep the review's `inherited_rc_closure`: RC-05 and RC-10 CLOSED_AT_DESIGN_LEVEL; RC-01 … RC-04, RC-06 … RC-09, RC-11 and RC-12 PARTIALLY_CLOSED, each answered through the V3-REQ that targets it (v3 §A.1's target column, carried in substance).

### A.4 Clauses NOT_CLOSED or PARTIALLY_CLOSED

The remaining gap is quoted from `review.json` `clause_detail[].remaining_gap`.

| Clause (status) | Remaining gap (verbatim) | v4 answer | Where |
|---|---|---|---|
| 01.1 (PARTIALLY_CLOSED) | "V-A supplies Facts_V2 families and typed consumer names; native input, current-observation, producer and wrapper obligations are not yet complete contracts, and preparation order disagrees with the declared graph." | Contract table per consumer; native-input table; corrected order | V4-A.1 … V4-A.5 |
| 01.2 (NOT_CLOSED) | "Carried L-RB-1 keeps valid span positions; V-B.6 compacts and moves them. The declared Rebase cannot satisfy both rules." | L-RB-1P (positional) and L-RB-1C (compaction), each tied to its constructions; W9 restated | V4-B.1; R4-45, R4-2 |
| 01.3 (NOT_CLOSED) | "Carried W8 requires every row universe head to equal the state head; V-B.5 constructs unequal-head histories without replacing W8. W3 also contradicts the arbitrary-factor shortcut on C1 refusal." | W8′ and W2′ frame-local; L-SAT-1′ positive on every input | V4-B.1; R4-46, R4-58, R4-20 |
| 01.5 (PARTIALLY_CLOSED) | "Invalid-predicate controls and valid multiframe/multibucket positives are specified. CV-B-prime/CV-R and all extra-conjunct correspondence are still unproved and the constructions are inconsistent." | Constructions made consistent; extra-conjunct audit; R0; CV-B′ and CV-R stay OPEN | V4-B.1 … V4-B.4 |
| 01.7 (PARTIALLY_CLOSED) | "Canonical/B2b/B2c use retained joins and the three native command guards are correctly distinguished. Rollover now crosses EFFECT_INTENT before launch refusal/quarantine; complete root/serial recovery and accepted-case cost/outcome mapping remain open." | Root route on the serial order; window-by-window recovery and cost mapping | V4-B.5, V4-B.6 |
| 02.1 (PARTIALLY_CLOSED) | "Expected JSON containers are preserved and extraction/form parameters are supplied. Numeric canonicality is entrusted to Python and UTF8/escape/path/no-cap native semantics remain unspecified or unverified." | Native number canonicality per form; escape, path and depth semantics with no cap; RC-4, RC-5 | V4-C.3; R4-21 |
| 02.2 (PARTIALLY_CLOSED) | "Roster_Join is explicit, but genesis/key/head authenticity requires an independently selected trust/custody/currentness chain; self-consistent packet hashes and MACs cannot supply that premise." | Independent selection chain and premises P-A1 … P-A4; MAC consistency withdrawn as authenticity | V4-C.1, V4-C.2; R4-22 |
| 02.3 (PARTIALLY_CLOSED) | "Crosswalk schema and operation/plan/cost/follow-up joins are proposed. Complete typed native decode, dynamic producer/caller correspondence and full costs remain open." | Typed decode table for the crosswalk; producer and caller correspondence rows; cost items | V4-A.3, V4-C.5 |
| 02.4 (PARTIALLY_CLOSED) | "Sampling and memory_high are no longer described as reserved future capacity. No full-domain resource enforcement/interference/cost correspondence is supplied." | Full-domain matrix; no completion claim | V4-D |
| 03.2 (PARTIALLY_CLOSED) | "The sequencing error is repaired; exact event relation, FD inheritance and helper enforcement of authentic native Child_Ready remain incomplete. Kernel/OS evidence remains unmeasured." | `Child_Event_Legal`; FD roster; COMMIT_CHILD enforcement; measurements stay OPEN | V4-E.1 … V4-E.3 |
| 03.3 (PARTIALLY_CLOSED) | "V1 and additive V2 families are retained; compatibility and accepted-case preservation are still stated lemmas with incomplete typed producer/caller coverage." | Producer and caller coverage per consumer; V1 route kept until the V2 producer exists | V4-A.2, V4-A.4 |
| 04.1 (NOT_CLOSED) | "M1/M2 omit a native custody-product gate, M6 excludes STOP_INTENT spooling, M8 conflicts with cancellation/helper stop, and r3 contradicts Never_Launched release. The complete Legal/Next reference is not defined." | Complete relation; M1/M2 gated; M6 and M8 harmonized; r3′ | V4-F, V4-G.1 |
| 04.3 (PARTIALLY_CLOSED) | "Independent subjects/subgenerations and an exclusive alternative primary key are supplied. Replay identity must include subject_kind; legal request/descriptor transitions and initial-head/state mapping remain incomplete." | Replay key with `subject_kind`; request and descriptor tables; initial state and head | V4-F.2, V4-F.6, V4-J.3 |
| 04.4 (PARTIALLY_CLOSED) | "PR-a/PR-b and retained-result recovery distinguish the old contradictions. Full post-intake/release failure and reconstruction seed/result-state mapping remain incomplete." | Seed independent of the terminal; RT-21 … RT-27; V4-H.4 table | V4-G.3, V4-G.4, V4-H.4 |
| 04.5 (PARTIALLY_CLOSED) | "The physical futures are now separately typed. CLOSED_OUTER adds unit inactivity beyond the original MainPID-zero/pidfd/wait test and can obstruct the original closure/reset route." | CLOSED_OUTER is exactly the original test | V4-G.2; R4-30 |
| 06.2 (PARTIALLY_CLOSED) | "A/B/C/E/F are compared and unselected; no option proves full-domain independent-request accounting, immutable parent bounds, enforcement and costs." | Full-domain matrix including F, F′ and G; none selected | V4-D |
| 06.3 (PARTIALLY_CLOSED) | "UNKNOWN holds and owner routes are retained, but r3/M8 and shared-lock/custody waits prevent a complete original cancel/quarantine/owner recovery progress argument." | r3′, M8 harmonized, progress model | V4-F.5, V4-G.1, V4-L |
| 06.4 (PARTIALLY_CLOSED) | "Event-loop responsiveness is improved in intent. A dedicated serialized lane blocked on protected storage or held asyncio operation ownership can still prevent protected response completion." | Lane withdrawn; original thread placement; progress table | V4-L.1, V4-L.3 |
| 07.1 (PARTIALLY_CLOSED) | "O mapping and O-by-U cells are supplied; C/P/request/descriptor event transitions and their actual mutation gates remain incomplete and inconsistent." | C×P rules r1 … r6; request and descriptor tables; mutation gates | V4-F.3 … V4-F.5 |
| 07.3 (NOT_CLOSED, REOPENED) | "REOPENED: carried original Never_Launched release and PR-a require release without CLOSED_WITNESS, while r3 forbids it. Repair without weakening closure requirements for any possibly launched row." | r3′ and INV-C4′ | V4-G.1; R4-47 |
| 08.1 (PARTIALLY_CLOSED) | "Durable stop intent precedes quiescence. M6 does not authorize required STOP_INTENT spooling, and restart does not specify reconstruction of the closed transport/consumer." | M6 authorizes it; reattachment rule | V4-F.5, V4-H.3 |
| 08.2 (PARTIALLY_CLOSED) | "Raw stdin and buffer rules are proposed. Kernel write versus durable W and kernel read versus durable spool still have unclassified uncertainty windows; writer duplicates invalidate unconditional owner-death EOF." | Armed intervals; duplicate rules | V4-H.1, V4-H.2, V4-H.5 |
| 08.3 (PARTIALLY_CLOSED) | "FREEZE requires spool fsync, but durable exact P/W and detection/recovery of pre-FREEZE consumption windows are not established." | Durable P/W at DISARMED; detection rule | V4-H.1, V4-H.2 |
| 08.5 (PARTIALLY_CLOSED) | "The table covers more windows but post-INTAKE/new-owner failure and post-RELEASE restart, partial drain/spool and stdin progress recovery are incomplete." | Complete window × failure table | V4-H.4 |
| 09.1 (NOT_CLOSED) | "J8 requires committed REQUEST_INTAKE before Join, while Join authorizes that intake. Request/transaction/reservation inputs are named in prose but not fully represented in the native Join interface; PID versus user namespace comparison is ambiguous." | `Transfer_Join` / `Serving_Join`; typed operand record; namespace split | V4-I.1 … V4-I.3 |
| 09.2 (PARTIALLY_CLOSED) | "Provider absence no longer directly refuses; validation precedes intake by rule. Circular Join and queued-only fallback still leave accepted transfer/protected response progress open." | Non-circular join; RELAY path; progress model | V4-I.1, V4-I.5, V4-L |
| 09.3 (PARTIALLY_CLOSED) | "The exact source gate list verifies. Mode-specific types improve the design, but all own-operation/transferred/historical caller operands and admission-head phases need complete contracts." | Per-gate contracts with operands and admission-head phase | V4-I.4 |
| 09.5 (PARTIALLY_CLOSED) | "Cookie/namespace/pidfd absence is optional. Declining transfer then waiting until custody returns is not an accepted-case-neutral service path for live/UNKNOWN/stalled owners." | RELAY; progress under LIVE, UNKNOWN and stalled custody | V4-I.5, V4-L.2 |
| 11.1 (PARTIALLY_CLOSED) | "Body/gate edges are richer, but V-M.4 preparation order places S6 before S1 although S6 depends on S1; native HMAC/roster/request product dependencies and consumed interfaces remain incomplete." | Corrected order; S2H, S12; consumed interfaces per node | V4-A.5 |
| 12.1 (PARTIALLY_CLOSED) | "Exact principal keysets and selection rules are proposed. Tool keys/provisioner paths, custody initial event/head/state authentication, migration paths and all constructor/loader selection artifacts remain unfinished." | Exact tool keys and provisioner paths; initial authentication; migration; selection artifacts | V4-J |
| 12.2 (PARTIALLY_CLOSED) | "No handler terminal is required for retained first capture. Inactive-unit barrier, r3 versus PR-a, recovery material previously seeded by handler_terminal, and observed/settled mappings prevent complete closure." | All four repaired | V4-G |
| 12.4 (PARTIALLY_CLOSED) | "Original K4/quarantine.resolve remain. Native mutation and actual serving progress through UNKNOWN, shared locks and unavailable custody are still incomplete." | Mutation gates; progress model | V4-F.5, V4-L |

### A.5 PARTIALLY_CLOSED rulings

Owner and evidence are quoted verbatim from the sealed v3 `review.json` `rulings` (unchanged since v1). "Remaining gap" is the review's `remaining_gap`, verbatim. Each ruling stays with its owner. v4 neither narrows nor adds to any of them.

| Ruling | Owner (verbatim) | Evidence required (verbatim) | Remaining gap (verbatim) | v4 answer | Where |
|---|---|---|---|---|---|
| D-1a | Lead source designer; independent GPT-6.1 source/spec reviewer | Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls. | Typed consumer contracts and graph are incomplete; W8/Rebase/W3 contradictions prevent coherent multiframe/saturated correspondence. Original references, accepted vectors and full body/native-cost target remain fixed. | Contracts and graph; consistent witness laws | V4-A, V4-B |
| D-1b | Lead scoped model/caller designer; independent GPT-6.1 reviewer | Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof. | Per-command placement is better specified. Rollover may now write EFFECT_INTENT before launch refusal; root/serial quarantine, physical classification, recovery and cost/accepted-case correspondence remain incomplete. | Root/serial order; rollover mapping | V4-B.5, V4-B.6 |
| D-2a | Lead authors schema/callers; operator provisions or installs authoritative state | Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls. | Version selection and exclusive creation are supplied, but exact tool/provisioner/initial-genesis/head/state/migration and full automatic recovery semantics remain unfinished. | Exact union, initial authentication, migration, recovery mapping. Provisioning stays operator-run (OP-1). | V4-J, V4-G.4 |
| D-3a | Lead protocol designer; operator for lab execution | Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection. | OFD/roster evidence before use is repaired at design level. STOP_INTENT mutation, read/spool and write/W crash windows, reconstruction and post-intake/release handling remain incomplete. | Armed intervals, reattachment, complete table | V4-H |
| D-4a | Lead prepares native accounting comparison; independent GPT-6.1 review; operator selects any authoritative resource-policy change | Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls. | No accounting option selected and no complete original-domain reservation/cost/interference or protected-response progress design; immutable outer-bound and independent grants remain required. | Matrix (no selection); progress model | V4-D, V4-L |
| D-5a | Lead prepares native/OS design; independent GPT-6.1 review; operator for delegation and privileged lab action | Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls. | Typed V2 direction is supplied; native producers/commands, exhaustive coordinator authority reachability and reserved capacity remain incomplete and unmeasured. | Producer contracts; exhaustive inventory; capacity matrix | V4-A.2, V4-E.4, V4-D |
| D-5b | Lead helper designer; independent GPT-6.1 review; operator for privileged execution/installation | Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations. | Create/measure/native-decision/ACK ordering is repaired; successor event relation, exact retained surfaces and helper enforcement are still incomplete. | Event relation; surfaces; COMMIT_CHILD | V4-E.1 … V4-E.3 |
| D-6a | Lead historical/canonical model designer; independent GPT-6.1 review | Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement. | COMMITTED, first result and original K4 stay fixed; Never_Launched release, physical barrier, full product and independent automatic reconstruction/retained-result routes need repair. | r3′; CLOSED_OUTER; seed; routes | V4-G, V4-F |
| D-7a | Lead native/provenance designer; child-authority and GPT-6.1 re-review; operator for any original API/owner-policy alteration | Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation. | JSON/source-record/roster/crosswalk direction is useful, but key/genesis/current-head trust, native canonicality, P3 coverage and C-API dependency closure remain open; no original API/owner-policy change selected. | Premises; canonicality; P3; sealed C-API binding. No original API or owner policy is altered. | V4-C, V4-K |
| D-8a | Lead OS/native requester designer; independent GPT-6.1 review | Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage. | Mode fields and source gate inventory supplied. Pre-intake Join is circular; complete typed joins, PID/user namespace treatment and all per-gate own/transferred/history contracts are missing. | Non-circular joins; typed operands; per-gate contracts | V4-I |
| D-8b | Lead prepares domain-preserving protocol; operator for kernel measurement; independent GPT-6.1 review | Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client. | Optional provider corroboration and no live-client/pidfd condition are retained. Queued fallback lacks original response progress; all actual kernel evidence remains OPEN under the existing reservation. | RELAY and the progress model; measurements stay with the operator (OP-7, K-1 … K-23) | V4-I.5, V4-L, V4-N |
| D-9a | Lead additive SPARK relation and caller designer; independent GPT-6.1 review; operator for fault campaign | Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes. | Exclusive alternatives and replay-before-CAS improve the design; complete native event/product/mutation relation, subject identity, crash/reconstruction and physical barrier remain incomplete. | Complete relation; subject identity; crash and reconstruction; barrier. Fault campaigns stay operator work (OP-8). | V4-F, V4-G, V4-H |

### A.6 Carried exactly as the review closed or assessed them

- **D-2b, CLOSED_AT_DESIGN_LEVEL**, carried unchanged by slice C2-116 inside C3-B. Owner, verbatim: "Lead prepares concrete equivalence/adoption package; applicable operator authority; independent GPT-6.1 review". Evidence required, verbatim: "Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit." The frontier control stays byte-exact on its v1 domain, with no re-enrollment proposed; `frontier_sha256` `a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb` (from the review's `carried_items`).
- **RC-05 and RC-10, CLOSED_AT_DESIGN_LEVEL**, carried by slices C2-17, C2-116 and C2-12 (inside C3-B). R4-6 only extends C2-17's enumeration to v4's controls.
- **CLOSED_AT_DESIGN_LEVEL clauses**, carried by the slices that hold the review's evidence: 01.4, 01.6, 03.1, 04.2, 04.6, 05.1 … 05.5, 06.1, 07.2, 07.4, 07.5, 08.4, 08.6, 08.7, 09.4, 10.1 … 10.4, 11.2, 11.3, 11.4, 12.3, 12.5. Where an R4 touches a cited line, it keeps the closed property: W1 … W10 still presuppose no equal decision (01.4; R4-2, R4-46); ACK/ABANDON stay exclusive (04.2); VALIDATE still precedes INTAKE and the roster evidence is unchanged (08.4, 08.6; V-H.2 and V-H.4 carried); 09.4's domain-preserving path keeps every listed case and still refuses nothing for correspondence (R4-7 changes only which owner serves); 12.3's uncertain holds stay, and a stop never settles (R4-31).
- **07.3** is REOPENED_NOT_CLOSED (the review's `carried_items`). It is answered in A.4, not carried as closed.
- **New author observations NF-1 … NF-11** are carried verbatim by slice C3-A7, with the review's assessments, verbatim: NF-1 VERIFIED_STATIC_OPEN_FLAG_KERNEL_CONSEQUENCE_UNMEASURED; NF-2 VERIFIED_STATIC_CONTROL_FLOW_NOT_RUNTIME_COMMIT; NF-3 VERIFIED_STATIC_LOCK_PATH; NF-4 VERIFIED_STATIC_AUTOMATIC_RECOVERY_BRANCH; NF-5 VERIFIED_TEXT_AND_LEXICAL_SCOPE; NF-6 VERIFIED_STATIC_MANAGER_CALLS_REACHABILITY_UNMEASURED; NF-7 VERIFIED_STATIC_ROUTER_WAIT_AND_FRONT_GATE; NF-8 VERIFIED_STATIC_ENCODING_FORMS; NF-9 VERIFIED_BYTE_IDENTITY_AND_STATIC_RELAY_JOIN_KERNEL_VIEW_UNMEASURED; NF-10 VERIFIED_STATIC_PLAN_SELECTION_GAP; NF-11 VERIFIED_STATIC_GENESIS_AND_HMAC_BOUNDARY. Each review consequence is answered: NF-1 and NF-6 by V4-E.4; NF-2 by V4-B.6; NF-3 and NF-7 by V4-L; NF-4 by V4-G.4; NF-5 by V4-K (no correction of the other lane); NF-8 by V4-C.3; NF-9 by V4-I; NF-10 by V4-J.2; NF-11 by V4-C.1, V4-C.2.
- **N-1 … N-10 and DF-1 … DF-6** keep their assessments (slice C2-A3 inside C3-B): N-1 VERIFIED_STATIC; N-2 SUPPORTED_STATIC_TOOL_BEHAVIOR_OPEN; N-3 VERIFIED_STATIC; N-4 VERIFIED_BYTE_DIFF_AND_LAYOUT; N-5 VERIFIED_LEXICAL_SCOPE; N-6 SUPPORTED_STATIC_CONDITIONAL_RECEIVER_RESOLVED; N-7 VERIFIED_STATIC; N-8 VERIFIED_STATIC_ORDER; N-9 VERIFIED_TEXT_SCOPE_RESOLUTION_OPEN; N-10 VERIFIED_STATIC_PAIR_FILLING; DF-1 VERIFIED_STATIC_RECOMPUTATION; DF-2 VERIFIED_STATIC; DF-3 VERIFIED_STATIC; DF-4 VERIFIED_STATIC; DF-5 VERIFIED_STATIC_ABSENCE_IN_SELECTED_TREES; DF-6 SUPPORTED_STATIC_CONDITIONAL. DF-3's required restoration of the exact serial guard and exception order is designed in V4-B.5.
- **Operator items OP-1 … OP-9**: WITHIN_RESERVED_SCOPE, and OP-7 WITHIN_RESERVED_SCOPE_RANGE_REPAIR_REQUIRED. The range repair is R4-1 and R4-5: OP-7's D-8b reservation names K-15 … K-23, which includes K-20 and K-21 and v4's K-22 and K-23. No item is added, lowered or widened.
- **The review's clarifications** are applied: the C-API and root-worker review gates are not operator gates; RC-1 … RC-4, and v4's RC-5 and RC-6, are ordinary lead-owned installed-runtime checks, OPEN and unperformed; S10 may be drafted passively as alternatives before D-4a, and its selected accounting specification cannot be claimed complete without that already-reserved decision (V4-A.5, with no drafting gate); this design authorizes no operational action and resumes no paused infrastructure.
- **IC assessments** of the review are carried: IC-2 … IC-9 as assessed; IC-10 OPEN_UNPERFORMED; IC-1, IC-11 and IC-12 are repaired in V4-K.

### A.7 The review's accepted-case risks and C-API repairs

| Item (review) | Review assessment (verbatim) | v4 answer | Where |
|---|---|---|---|
| EMBEDDING | "R1-R3 is not an exhaustive coherent partition as written; W8/L-RB-1/W3 contradictions remain. No original raw or fixture case may disappear while repaired." | Contradictions removed; R0 names every unclassified input; nothing is excluded, because the original unit decides every flat input | V4-B |
| NEVER_LAUNCHED | "r3 adds a release prohibition before CLOSED_WITNESS even for genuine never-dispatched rows; conflicts with preserved original release and PR-a." | r3′ | V4-G.1 |
| UNIT_INACTIVE | "CLOSED_OUTER adds inactive-unit status beyond original terminal conditions. The source launches RemainAfterExit=yes and retains reset-after-closure; equivalence is not established." | Inactive-unit condition removed | V4-G.2 |
| QUEUED_NOT_REFUSED | "Declining intake is not an operation refusal. QUEUED fallback must nevertheless preserve service progress; FRONT_OWNED g+1 may never arrive under LIVE/UNKNOWN/stalled custody. No join may be fabricated and no timeout/deadline may settle authority." | RELAY, the worker's original completion, authorized cancellation, and progress conditions; no fabricated join, no deadline settlement | V4-I.5, V4-L |
| REQUEST_INTAKE | "J8 is circular, namespace comparisons can incorrectly compare deliberately distinct PID namespaces, and not all native join operands are typed." | Non-circular joins; PID-namespace correspondence; typed operands | V4-I.1 … V4-I.3 |
| UNSELECTED_POLICY | "No new accounting policy/cap is selected. Option F must remain unselected and may not weaken immutable outer reservation ceilings or first-root independent grant/cost obligations." | F stays unselected and fails AO-5 as stated; no option selected | V4-D |
| AUTHENTICITY_PREMISE | "Native HMAC/head consistency with packet-selected key/genesis is not an established independent authenticity/currentness premise. Source-lease DATA remains Python producer/custody work, not a native proof shortcut." | Premises P-A1 … P-A4 stated as premises, with native verification conditional on them | V4-C.1, V4-C.2 |

| C-API repair (review `required_integration_repairs`, verbatim) | v4 answer | Where |
|---|---|---|
| "Bind the now-sealed CAPI5 review and its two required repairs without treating ENDORSED_WITH_REQUIRED_CHANGES as closure." | Bound; the v5 repairs are dependencies, closed only at design level by the sealed CAPI6R | V4-K.1 |
| "Enforce empty exclusive-map roster before PK-6b, sole G21c/Finalization_Decide/O thereafter, independent of mutable tables, and prohibit any RW assignment exception." | CAPI6's CR2, CR5 and CR6 evaluated over the union gate table; `CAPI_WFX_PROTOCOL` never extended; no RW exclusive table | V4-K.2 (U-4, U-5) |
| "Extend qualifier no-capture checks to every relevant with-clause prefix/ancestor and align argument, tables, controls and machine twin." | (d1)–(d4) over the union root and simple-name sets, including every prefix of every RW with clause; controls MQ-RW1 … MQ-RW5; twin aligned | V4-K.2 (U-2, U-3), V4-K.3 |
| "Specify the canonical-name/scope attribution union and actual staged per-call inventories, preserving all predecessor rows, residuals and exceptions." | U-1 … U-8 | V4-K.2 |
| "Retain original and additive mutation/positive controls and the full native proof/cost/ABI/warning floor." | Floor and controls retained (C3-VK2, C3-VK5) | V4-K.2 (U-8), V4-K.3 |

### A.8 New author observations (static; for the reviewer to check; none is review)

| Id | Observation | Evidence (read) | Consequence | Where |
|---|---|---|---|---|
| NF4-1 | On a failure after launch, the root route calls `retain_and_stop_unknown` and does not quarantine the use (`rw/protected_root_worker.py:191-199`), while the serial route quarantines every exception after `_reserve` (`rw/protected_operations.py:767-768`). The root route's `EFFECT_INTENT` also lacks the serial route's `DISPATCH_INTENT` boundary (`rw/protected_root_worker.py:170-171` against `rw/protected_operations.py:749`). | Read | The root/serial exception order (DF-3) | V4-B.5 |
| NF4-2 | With a root worker present, every non-owner operation goes to the root route (`rw/protected_operations.py:723-725`). The serial route refuses `fork`, `race`, `revalidate`, `simulate`, `ghost.run`, `ghost.enable`, `root.add` and `init` after `_reserve` with `OPERATION_ORIGINAL_WORKLOAD_RESOURCE_ROUTE_UNINTEGRATED`, then quarantines (`:744-745`, `:767-768`). | Read | In the lane, the scoped launch commands occur only on the root route | V4-B.6 |
| NF4-3 | The custody intent frame retained as `ROOT_WORKER_CUSTODY_INTENT` carries `root_native`, the `EXECUTION_NATIVE` custody event of `retain_root_native`, and `original_native_use` (`rw/root_worker_custody.py:125-133`; `rw/protected_root_observation.py:157-164`). The worker requires the same seed through `frame['root_native']` (`:105-109`). | Read | A durable reconstruction seed exists without HANDLER_TERMINAL | V4-G.3 |
| NF4-4 | The original process capture checks the exe against roles INTERPRETER and EXECUTABLE, and every `maps` line whose pathname begins with `/` against INTERPRETER, EXECUTABLE, EXTENSION and DATA, whatever its permissions (`rw/root_worker_process_capture.py:69-74`). | Read | P3's scope is every file-backed mapping; v3's R3-5 wording "executable mapping" was narrower | V4-C.4 |
| NF4-5 | The custody genesis key `initial_event` has no producer or consumer in the lane beyond the keyset check (`rw/root_worker_journal.py:43-44`; a grep of the lane source found no other occurrence). | Observed (grep) | v2 defines it | V4-J.3 |
| NF4-6 | The issuer key path is fixed under the descriptor's `authority_root` (`rw/root_worker_journal.py:50-53`). The head MAC covers only the head and the genesis (`:111-113`), so a byte-identical older journal validates under the same key. | Read | Anti-rollback limit | V4-C.2 |
| NF4-7 | Plan-v1 `native_components` is exactly {`systemctl`, `systemd_run`, `approved_loader`} (`rw/root_worker_plan.py:18-20`). The scoped runtime takes `bwrap` and `resource_supervisor_v3` from `runtime.tools` (`rw/protected_scoped_resource_runtime.py:73-74`, `:732`) and requires the config's `systemd_run` and `systemctl` paths among the tools values (`rw/protected_resource_runtime.py:171-172`). | Read | The exact U-3 tool roster | V4-J.2 |
| NF4-8 | `job.cancel` is registered as mutating (`rw/controller.py:423`). It reads the store and calls `runner.cancel` for every active job of the world (`:811-826`). | Read | Cancellation is a store-reading, unit-stopping action of the custody owner (M8) | V4-F.5 |
| NF4-9 | The V1 and V3 C helpers give the exec'd process descriptors 0, 1 and 2 only, from pipes and socketpairs created `CLOEXEC`; V1 also clears `FD_CLOEXEC` on its custody sender and appends its number to argv (`protected-root/native_root_worker_supervisor_v1.c:271-291`, `:323-335`; `protected-resource/native_namespace_supervisor_v3.c:297-305`, `:337-346`). The measurement frame and the commit travel on a socketpair whose receiving end goes to the owner in HELD (`native_namespace_supervisor_v3.c:265-275`, `:358`), so the helper never sees the frame. | Read | COMMIT_CHILD enforcement needs a relaying sub-helper | V4-E.2, V4-E.3 |
| NF4-10 | Startup reconciliation calls `recover_committed` for `EFFECT_OBSERVED`, `SETTLED`, and `EFFECT_INTENT` with a `RESULT_CAPTURE`, outside any `try` (`rw/protected_operations.py:366-368`). A refusal there propagates out of reconciliation, while broker, owner-resolution and K4 failures go to `unresolved` (`:363-365`, `:369-375`, `:377-382`). | Read | Those rows map to a startup refusal for owner diagnosis, exactly as original | V4-G.4 |
| NF4-11 | `status` is mutating and may run `_reconcile_status` (a PRIME re-capture) when the store is dirty (`rw/daemon.py:84`, `:407-419`). | Read | `status` progress depends on storage and registered roots, as in the original | V4-L.2 |
| NF4-12 | The original scoped launch commits `RECORD_LAUNCH_INTENT` before `DISPATCH_INTENT` and the dispatch, and `RECORD_RUNNING` after HELD (`rw/protected_scoped_resource_runtime.py:741`, `:756`, `:760-762`, `:767`). v3's E6 placed both commits after HELD, a v3 author error. | Read | The child order is corrected (R4-59, R4-61) | V4-E.1 |
| NF4-13 | C2-62 names the transition FRONT_RECONSTRUCTION → FRONT_OWNED (g+1), but v3's DDL kind list had no event kind that records it (`D3:1316-1323`), another v3 author error. | Read | `FRONT_OWNED` is added to the kinds (R4-29) | V4-F.2 |

---

## B. What v4 carries from v3, and how to read it

### B.1 Bound v3 slices

- v3 `SEAM-DESIGN.md` has 2128 lines and ends with a newline (observed). Its whole-file sha256 is `a0f2f411d654f1cce472a1ad2a13d3c082fff42def050c5ed4694a8b094d07a0`.
- Each slice's sha256 is that of the UTF-8 bytes of its lines, each followed by `\n`. A read-only script computed them (Appendix C).
- CARRIED_VERBATIM slices are part of v4 exactly. CARRIED_WITH_LINE_REPLACEMENTS slices are part of v4 with the listed lines replaced by the §B.2 text.

| Slice | v3 lines | sha256 | Disposition | Content |
|---|---|---|---|---|
| C3-A7 | 178-192 | `5c07c30f76c7c480d6fb23d321b0659c5657e49ee196546b703bfcd8c9a81080` | CARRIED_VERBATIM | v3 §A.7: NF-1 … NF-11 (assessed in §A.6) |
| C3-B | 196-691 | `7f770eb7006abb991e676062f57da00898026771ed3951751af373a07b8c66cc` | CARRIED_WITH_LINE_REPLACEMENTS (R4-1 … R4-17, R4-52) | v3 §B: the v2 slices C2-A3 … C2-APC, R3-1 … R3-43, v3's map, reading rules and withdrawals |
| C3-VA | 744-793 | `5d6600e199279605b4890015dc16e9e269e8b0f01e3de898d908265852e47d52` | CARRIED_WITH_LINE_REPLACEMENTS (R4-18) | V-A: the two families, the consumer table, selection, L-BR-1 |
| C3-VB | 796-955 | `eba45664dab8c9df0fa3131e5967a2fbe16c4dc1fbc237412d21519a667d4f38` | CARRIED_WITH_LINE_REPLACEMENTS (R4-19, R4-20) | V-B: domains, span forms, constructions, residuals, PD lemmas, fixtures, the RQ-1 table |
| C3-VC | 959-1106 | `de8b15e2b007d60f216abfcdf1f8da3ba8fd68b3bbded44ed8cda12e3b11d9cd` | CARRIED_WITH_LINE_REPLACEMENTS (R4-21 … R4-23) | V-C: containers, framed records, `Roster_Join`, grammar, crosswalk, P3 |
| C3-VD | 1110-1155 | `5e5d1e6dbd88bcb5b55fa2df7236a920fac3d54c07f2160bdaf1d5a4f7949aaa` | CARRIED_WITH_LINE_REPLACEMENTS (R4-24, R4-25) | V-D: withdrawals, per-class correspondence, E1–E4, options |
| C3-VE | 1159-1231 | `71a7780cddc94e607e565e2ea4c0d6905a9fade1361aa158040c240d21fbd02d` | CARRIED_WITH_LINE_REPLACEMENTS (R4-26 … R4-28, R4-54, R4-59 … R4-64) | V-E: E1–E12, surfaces, reachability and helper commands |
| C3-VF1 | 1234-1275 | `57c06a24ff21b87bd1f7605289879bb8bf724d3f0e432a6810109c588e9e95fe` | CARRIED_VERBATIM | V-F.1 product state, V-F.2 O mapping, V-F.3 heading and O×U table |
| C3-VF5 | 1299-1374 | `b262e46822f6fa1df6f5562f2e62b541f0fdd4e2fd1ca0f089cff7ba0d5dedf6` | CARRIED_WITH_LINE_REPLACEMENTS (R4-29) | V-F.5 custody journal v2 DDL |
| C3-VG | 1391-1454 | `306b743e0cfef06baa4d6d9938de9b7c0efe6aef877e250b6e8e7229cf66feb2` | CARRIED_WITH_LINE_REPLACEMENTS (R4-30 … R4-33, R4-56) | V-G: barrier, futures, U decision, NEVER_DISPATCHED split, crash table |
| C3-VH1 | 1458-1494 | `3d75bffbf71d9ee7e4953b39652bb4608529073973bc636fba6a4a5eec821ace` | CARRIED_WITH_LINE_REPLACEMENTS (R4-34 … R4-36) | V-H.1, V-H.2: descriptor states and H0–H6 |
| C3-VH4 | 1516-1521 | `b9a8bcb47af453524c4c19eb706c78096c7f7302ddbf83b6cd34fc9d32628b37` | CARRIED_VERBATIM | V-H.4: the root handoff's lock roster |
| C3-VI1 | 1525-1533 | `ea9f9d61dc020416728b9f6a8b3ab34039f901f5c0942d447abddf02f38468bf` | CARRIED_VERBATIM | V-I.1: the original evidence baseline |
| C3-VI45 | 1593-1629 | `ba30a22e41ee223d3b2baac70e692cd207c8eac36c03fd015c131eebf013acd8` | CARRIED_VERBATIM | V-I.4 joins (typed in V4-I.2), V-I.5 gate list |
| C3-VJ | 1650-1717 | `1c62c4e50cd47c29741327c937acc549caa55b4ac117db9b1edb3be23f968dd1` | CARRIED_WITH_LINE_REPLACEMENTS (R4-37 … R4-40, R4-53) | V-J: v1 keysets, v2 keysets, slots, DDL, recovery map, v1 parity |
| C3-VK2 | 1738-1768 | `9279a36162787286562fec5ea5e6972f3ceb98c2e6b5a1563a3584c150a5cd8e` | CARRIED_WITH_LINE_REPLACEMENTS (R4-41, R4-42) | V-K.2 gate chain, V-K.3 floor and appended RW tables |
| C3-VK5 | 1777-1833 | `43c9cd0f838890f572b5482704c095d9205ffae349cb71aef06e7fa13c62ba84` | CARRIED_WITH_LINE_REPLACEMENTS (R4-43) | V-K.5 … V-K.10: write and gate rules, glue, hygiene scope, R-RW, IC checks, ordering |
| C3-VL1 | 1837-1851 | `5366d957d66239900c181e57bb7be69e84eadaacbe3f63ca9110234d804fc88c` | CARRIED_VERBATIM | V-L.1 lock inventory |
| C3-VL3 | 1859-1865 | `cfab791373814513e5c25257cb1982f0b44dfdf585a40f7e1320521448111e34` | CARRIED_WITH_LINE_REPLACEMENTS (R4-44) | V-L.3 lock order, SL-0, A1 |
| C3-VL6 | 1885-1890 | `7264dbf84cdab8dc5dff79019a7a580aad9e18627e4f99a10d818f70aa56dc42` | CARRIED_VERBATIM | V-L.6 fairness |
| C3-VN | 1950-1964 | `490f27c2e00f25eacec9b470a49b5060101212000f6c04f25709be3fe1b4ba35` | CARRIED_WITH_LINE_REPLACEMENTS (R4-50, R4-55) | V-N: additive controls of v3 |
| C3-VO | 1968-1984 | `635a7a87b4bba6c331c71873f3caaa53f0e004aacab57e89be1353c4761090b2` | CARRIED_WITH_LINE_REPLACEMENTS (R4-57) | V-O: K-15 … K-21, RC-1 … RC-4 |
| C3-VQ | 2023-2033 | `1c5f3e2b73c1d592b8f70400c857afcf931c8851b7c037b610d06ebd94451ba6` | CARRIED_WITH_LINE_REPLACEMENTS (R4-51) | V-Q: non-claims |
| C3-APB | 2041-2108 | `328a57676f3b567ae3a648d3fef80473e1da596d0dd9d4b39e1a3c1a64934dd7` | CARRIED_VERBATIM | v3 Appendix B: inputs bound while drafting v3 |

R4-45 … R4-49 and R4-58 replace v2 lines inside C2 slices that C3-B binds (RR4-4).

### B.2 Line replacements

Each replacement quotes the exact v3 (or v2) line or lines, then gives the v4 text.

**R4-1 replaces v3 line 259 (in C3-B; R3-1's result, G-12).** OP-7 range repair.
```text
v3:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace, socket and interpreter semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14 in §16, K-15 … K-19 in v3 V-O) or its installed-runtime check (RC-1 … RC-4 in v3 V-O).
v4:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace, socket and interpreter semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14 in §16, K-15 … K-21 in v3 V-O, K-22 and K-23 in v4 V4-N) or its installed-runtime check (RC-1 … RC-4 in v3 V-O, RC-5 and RC-6 in v4 V4-N).
```

**R4-2 replaces v3 line 283 (in C3-B; R3-4's result, W9).**
```text
v3:
- **W9.** Every witness field has one of the three forms of v3 V-B.3: a present zero-length span, an alias of an original span, or fresh bytes placed outside every rebased original span. `Rebase` satisfies L-RB-1 … L-RB-4 (v3 V-B.6).
v4:
- **W9.** Every witness field has one of the forms of v4 V4-B.1: (a) a present zero-length span, (b) an alias of an original span, (b′) a one-byte sub-span of `Data` over a non-zero byte, or (c) fresh bytes placed outside every rebased original span. `Rebase` satisfies L-RB-1P for the constructions that extend `Data` (v3 V-B.4, V-B.5 and case S-a of V-B.6) and L-RB-1C for compaction (case S-b), together with L-RB-2 … L-RB-4 (v4 V4-B.1).
```

**R4-3 replaces v3 line 291 (in C3-B; R3-5's result, the P3 row).**
```text
v3:
| P3 | source_lease ↔ process `P_source_lease` (`.ads:59`) | Host-side capture of the worker's executable images (exe plus every file-backed executable mapping, each with dev, ino and sha256) through a read-only host procfs view and the worker pidfd | The P2 loader lease record, a distinct producer | Native subset relation `Process_Images_Covered`, defined in v3 V-C.7 with its non-claims. Today's caller-provided value (`rw/protected_root_observation.py:74-76`, `:121`) is withdrawn. |
v4:
| P3 | source_lease ↔ process `P_source_lease` (`.ads:59`) | Host-side capture of the worker's images: the exe plus every file-backed mapping, meaning every `maps` line whose pathname begins with `/`, whatever its permissions, exactly as the original capture checks (`rw/root_worker_process_capture.py:69-74`); each with path, dev, ino and sha256, read through a read-only host procfs view and the worker pidfd | The P2 loader lease record, a distinct producer | Native subset relation `Process_Images_Covered` of v3 V-C.7 as amended by v4 V4-C.4, with the non-claims NC-P3-1 … NC-P3-4 there. Today's caller-provided value (`rw/protected_root_observation.py:74-76`, `:121`) is withdrawn. |
```

**R4-4 replaces v3 line 307 (in C3-B; R3-7's result, L-CAPI).**
```text
v3:
| **L-CAPI** | The C-API consolidation successor | The sealed actual gpt-6.1-sol review of CAPI4 is ENDORSED_WITH_REQUIRED_CHANGES, with V4-RC4-GATE and V4-RC4-ALIAS OPEN. CAPI5 answers both and is UNREVIEWED. Source packets PK-0 … PK-S are unwritten. |
v4:
| **L-CAPI** | The C-API consolidation successor | The sealed actual gpt-6.1-sol review of CAPI5 is ENDORSED_WITH_REQUIRED_CHANGES, with V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE. The sealed review of CAPI6 is ENDORSED with no required changes and closes those two, V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 at design level only. Implementation, stage reviews, controls, proof and ROOT_WORKER_INTEGRATION stay OPEN (v4 V4-K.1). Source packets are unwritten here. |
```

**R4-5 replaces v3 line 315 (in C3-B; R3-8's result, OP-7).** OP-7 range repair.
```text
v3:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 (§16) and K-15 … K-19 (v3 V-O) in an authorized lab | §3–§9 and v3 V-B … V-I runtime evidence |
v4:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 (§16), K-15 … K-21 (v3 V-O) and K-22 and K-23 (v4 V4-N) in an authorized lab | §3–§9, v3 V-B … V-I and v4 V4-B … V4-L runtime evidence |
```

**R4-6 replaces v3 line 323 (in C3-B; R3-9's result).**
```text
v3:
- It enumerates every control of §4.6, §5.6, §6.12, §7.6, §8.7, §9.8, §10.6, §11.8 and §12.6 (carried) and of v3 V-B.9 and V-N (which replace v2 §3.14 and §14.5). Each entry gives:
v4:
- It enumerates every control of §4.6, §5.6, §6.12, §7.6, §8.7, §9.8, §10.6, §11.8 and §12.6 (carried), of v3 V-B.9 and V-N (which replace v2 §3.14 and §14.5), and of v4 V4-M. Each entry gives:
```

**R4-7 replaces v3 line 372 (in C3-B; R3-15's result).**
```text
v3:
Where the worker cannot establish correspondence for a transferred request, it declines intake (`REQUEST_ABANDON(r)`). The request stays queued and is served by the front under the original `RequestPeer` gate (v3 V-I.6). It is never refused for that reason. An absent socket cookie or an unreadable namespace identity never blocks (v3 V-I.3). Nothing is substituted: no sender PID label, no synthesized `SO_PEERCRED` bytes, and no `fstat` equality as custody.
v4:
Where the worker cannot establish a FRESH correspondence for a transferred request, it declines intake (`REQUEST_ABANDON(r, s)`). The front then offers the request in RELAY mode, in which the front keeps the client socket and re-reads it under the original `RequestPeer` at every gate use (v4 V4-I.5). Only when no owner can serve does the request stay queued, under v4 V4-L's progress conditions. It is never refused for that reason. An absent socket cookie or an unreadable namespace identity never blocks (v4 V4-I.2). Nothing is substituted: no sender PID label, no synthesized `SO_PEERCRED` bytes, and no `fstat` equality as custody.
```

**R4-8 replaces v3 line 380 (in C3-B; R3-16's result).**
```text
v3:
- Socket identity mismatch, or a cookie mismatch when both cookies are present, makes the worker decline intake. The front then serves the request under the original gate (v3 V-I.6), and the original checks decide it.
v4:
- Socket identity mismatch, or a cookie mismatch when both cookies are present, makes the worker decline FRESH intake. The request is then served in RELAY mode (v4 V4-I.5), and the original checks decide it.
```

**R4-9 replaces v3 line 388 (in C3-B; R3-17's result).**
```text
v3:
- A worker in a different user namespace declines intake. The front serves the request under the original gate (v3 V-I.6).
v4:
- A worker whose user namespace differs from the front's, when both records are present, declines FRESH intake, and the request is served in RELAY mode (v4 V4-I.5). PID namespaces are deliberately different and are never compared for equality (v4 V4-I.3).
```

**R4-10 replaces v3 line 404 (in C3-B; R3-19's result).** J8 circularity removed.
```text
v3:
3. The worker receives everything first, validates it, computes the native `Join` in FRESH mode (v3 V-I.3, V-I.7) and CASes `REQUEST_INTAKE(r)`, which is exclusive with `REQUEST_ABANDON(r)`. Then it acknowledges. If `Join` is not Ready, it declines and the front CASes `REQUEST_ABANDON(r)`. The request stays queued, and the front serves it under the original gate once custody returns (v3 V-I.6).
v4:
3. The worker receives everything first and validates it. It computes the native `Transfer_Join` over the authenticated `REQUEST_TRANSFER_INTENT(r, s)` head (v4 V4-I.1) and CASes `REQUEST_INTAKE(r, s)`, which is exclusive with `REQUEST_ABANDON(r, s)`. Then it acknowledges. If `Transfer_Join` is not Ready, it declines and the front CASes `REQUEST_ABANDON(r, s)`; the front then offers sub-generation s+1 in RELAY mode (v4 V4-I.5).
```

**R4-11 replaces v3 line 428 (in C3-B; R3-22's result).**
```text
v3:
  - R-RW-1 … R-RW-10 and IC-1 … IC-12 (v3 V-K.8, V-K.9); IC-10 needs the admitted frame.
v4:
  - R-RW-1 … R-RW-10 and IC-1 … IC-14 (v3 V-K.8, V-K.9 as amended by v4 V4-K.3); IC-10 needs the admitted frame.
```

**R4-12 replaces v3 line 436 (in C3-B; R3-23's result).**
```text
v3:
  - The sealed CAPI4 review leaves V4-RC4-GATE and V4-RC4-ALIAS OPEN. CAPI5 is unreviewed (v3 V-K.1).
v4:
  - CAPI5R requires V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE; CAPI6R closes them at design level only. Their implementation, stage reviews and controls, and ROOT_WORKER_INTEGRATION, stay OPEN (v4 V4-K.1).
```

**R4-13 replaces v3 line 444 (in C3-B; R3-24's result).**
```text
v3:
- **Process.** The independent actual gpt-6.1-sol review of v3, of every slice and of the full lane. The sealed review of v2 is its predecessor.
v4:
- **Process.** The independent actual gpt-6.1-sol review of v4, of every slice and of the full lane. The sealed reviews of v2 and v3 are its predecessors.
```

**R4-14 replaces v3 line 530 (in C3-B; R3-34's result).**
```text
v3:
The **multi-frame variant** is v3 V-B.5, and the saturated-arena construction is v3 V-B.6. Coverage is exactly D_emb (v3 V-B.2). The residuals R1, R2 and R3 are decided by the unchanged original unit.
v4:
The **multi-frame variant** is v3 V-B.5, and the saturated-arena construction is v3 V-B.6, under the witness laws of v4 V4-B.1. Coverage is exactly D_emb (v3 V-B.2). The residuals R0, R1, R2 and R3 (v4 V4-B.3) are decided by the unchanged original unit.
```

**R4-15 replaces v3 line 546 (in C3-B; R3-36's result).**
```text
v3:
- **CV-C (fixture coverage).** Every original native fixture vector that exercises `Worldline.Canonical_Operation`, accepted or refusal, is either embedded with a coherent witness and shown to give the same decision, or is identified as residual R1, R2 or R3 (v3 V-B.2), whose correspondence obligation stays OPEN. In every case the original unit and its fixture remain unchanged and keep running and deciding.
v4:
- **CV-C (fixture coverage).** Every original native fixture vector that exercises `Worldline.Canonical_Operation`, accepted or refusal, is either embedded with a coherent witness and shown to give the same decision, or is identified as residual R0, R1, R2 or R3 (v3 V-B.2, v4 V4-B.3), whose correspondence obligation stays OPEN. In every case the original unit and its fixture remain unchanged and keep running and deciding.
```

**R4-16 replaces v3 line 628 (in C3-B; R3-43's result, U-3).**
```text
v3:
| U-3 | v2 | `StartupLease (descriptor)`, then `construct_v2 ()` via `serve ()` | Daemon entry | `worldline.protected-startup-v2`, with the exact key sets of v3 V-J.2: the v1 keys plus `root_worker`; `runtime` adds `resource_scoped_producer`; `tools` includes the V3 supervisor helper, `bwrap`, `systemctl` and `systemd-run` under their installed names; `provisioned_state` adds the owner plan, crosswalk, custody v2 DB, lock and genesis | Descriptor, genesis, owner plan, crosswalk, run-scoped config, custody v2 genesis, header DATA | none | Named refusal, or the genuine reconciler (§11.5) |
v4:
| U-3 | v2 | `StartupLease (descriptor)`, then `construct_v2 ()` via `serve ()` | Daemon entry | `worldline.protected-startup-v2`, with the exact key sets of v3 V-J.2 as amended by v4 V4-J.2: the v1 keys plus `root_worker`; `runtime` adds `resource_scoped_producer`; `runtime.tools` includes the keys `bwrap`, `resource_supervisor_v3`, `systemctl` and `systemd-run`, with v1 semantics; `provisioned_state` adds the owner plan, crosswalk, custody v2 DB, lock and genesis | Descriptor, genesis, owner plan, crosswalk, run-scoped config, custody v2 genesis, header DATA | none | Named refusal, or the genuine reconciler (§11.5) |
```

**R4-17 replaces v3 line 664 (in C3-B; RR3-5).**
```text
v3:
- **RR3-5.** R-2's phrase "design v4, unreviewed" inside C2-APC is historical. The current C-API predecessor status is V-K.1.
v4:
- **RR3-5.** R-2's phrase "design v4, unreviewed" inside C2-APC is historical. The current C-API status is v4 V4-K.1.
```

**R4-18 replaces v3 line 777 (in C3-VA).** No interim refusal (V2-REQ-A, V3-REQ-A).
```text
v3:
- **Before the V2 producers exist,** a v2 deployment refuses the V2 route by name: `SCOPED_V2_PRODUCER_UNAVAILABLE`. This is an interim refusal that keeps its obligation OPEN, under G-2. v1 deployments are unaffected, so no original accepted case moves.
v4:
- **Before an authentic V2 producer exists** for every live row, the deployment stays on the V1 family and on every original route: no V2 export is selected, and nothing is refused for the producer's absence (v4 V4-A.4). The V2 route is additive and is selected only by the condition of the first bullet.
```

**R4-19 replaces v3 line 814 (in C3-VB).**
```text
v3:
- **CV-R.** D_raw \ D_emb equals exactly R1 ∪ R2 ∪ R3 (V-B.5 … V-B.7).
v4:
- **CV-R.** D_raw \ D_emb equals exactly R0 ∪ R1 ∪ R2 ∪ R3 (V-B.5 … V-B.7, v4 V4-B.3), where R0 is every input not otherwise classified. The obligation is that R0 is empty, and it stays OPEN.
```

**R4-20 replaces v3 lines 846-849 (in C3-VB).** W3 on every input (01.3).
```text
v3:
**L-SAT-1** (statement, to prove).
- If clause C1 does not refuse, some grant is `Grant_Valid`.
- `Grant_Valid` requires `Issued_At < Expires_At` with both non-negative (`core/worldline-operation_authority.ads:72-82`), so its `Expires_At` span has a positive value. That span is the alias for N.
- If C1 refuses, the decision is `Authority_Refused` before C2, by the original clause order (`core/worldline-canonical_operation.adb:10-34`), so N may be any span.
v4:
**L-SAT-1′** (statement, to prove; replaces L-SAT-1). The factor N is chosen without reference to any clause, decision or refusal (W10), and is positive on every input, so W3 holds whether or not C1 refuses:
- if `Data` has a non-zero byte, N is the one-byte span `(Negative => False, First => p, Length => 1)` at the least such index p; its value is `Data (p)` (`core/resource_quantities.ads:13-17`, `:25-28`, `:92-96`), and it is `Nonnegative_Valid` (`core/resource_reservation_transition.ads:135-138`). This is form (b′) of v4 V4-B.1;
- otherwise N is one fresh byte 0x01 (form (c)), placed after `Data'Last` or before `Data'First` when a position is free there, and otherwise by compaction (case S-b);
- when neither placement exists, the input belongs to residual R3 (v4 V4-B.3).
```

**R4-21 replaces v3 line 980 (in C3-VC).** Native number canonicality (02.1).
```text
v3:
   The unchanged Python check (`exact_json` or `exact`) runs first and establishes canonicality. The native recognizer must accept every byte string that check accepts and give each nested value's exact span. On its own it refuses whitespace, unsorted or duplicate keys, malformed UTF-8 and non-canonical string escapes. It accepts number lexemes by the RFC 8259 grammar, so the canonicality of numbers rests on the Python check alone. That is a stated limit, not a claim.
v4:
   The unchanged Python check (`exact_json` or `exact`) still runs first, as today. The native recognizer must accept exactly the byte strings that check accepts and give each nested value's exact span. On its own it refuses whitespace, unsorted or duplicate keys, malformed UTF-8, non-canonical string escapes and non-canonical number lexemes: a lexeme is accepted only when it equals the encoder's own rendering of the value it denotes, by the native relation `Number_Canonical` of v4 V4-C.3 **[unverified reasoning, RC-4, RC-5]**. Number canonicality therefore no longer rests on the Python check alone. Its proof and native cost stay OPEN.
```

**R4-22 replaces v3 lines 1012-1013 (in C3-VC).** Self-consistency is not authenticity (02.2, AUTHENTICITY_PREMISE).
```text
v3:
- v3 adds a native `Hmac_Sha256` over `Attest.SHA256`, with the key passed inside the private arena. It verifies every event MAC and the head MAC natively, so the genesis content is authenticated under the issuer key and not only by Python.
- Key handling, meaning the arena's lifetime and zeroization, is a non-claim and stays OPEN.
v4:
- The native `Hmac_Sha256` over `Attest.SHA256` verifies every event MAC and the head MAC under the key passed in the private arena. That establishes chain integrity relative to that key only. It does not establish that the key, the genesis or the head is the authentic, current selection: self-consistent MACs and digests cannot supply that premise. The selection chain, the premises P-A1 … P-A4 and the anti-rollback limits are v4 V4-C.1 and V4-C.2.
- Key handling, meaning the arena's lifetime and zeroization, is a non-claim and stays OPEN.
```

**R4-23 replaces v3 line 1096 (in C3-VC).** One P3 scope.
```text
v3:
**Coverage.** Natively mapped code: the interpreter, extensions and shared objects.
v4:
**Coverage.** The exe and every file-backed mapping: every `maps` line whose pathname begins with `/`, whatever its permissions, which is exactly the set the original capture checks (`rw/root_worker_process_capture.py:69-74`). That includes the interpreter, extensions, shared objects and DATA-role mappings (v4 V4-C.4).
```

**R4-24 replaces v3 line 1153 (in C3-VD).** F against the immutable outer bound.
```text
v3:
| **F (new): per-request handler subprocess in its own nested unit** under the delegated subtree. Its limits and protection derive from that request's own reservation. The root's outer ceiling is raised by the helper by exactly the nested reservations, on a native ledger-backed request. | AM-1–AM-9 at ledger level | each request's own unit | per request (if P-M1) | no, if the root's own reservation excludes nested units and the ceiling equals root plus nested | good | higher: a process per request | The helper must change the root's ceiling dynamically (a helper command, V-E); the coordinator cannot raise its own (P-CE1). Interpreter start-up cost. **[unverified reasoning, K-8, K-16]** |
v4:
| **F (v3, as stated): per-request handler subprocess in its own nested unit** under the delegated subtree, with the root's outer ceiling raised by the helper by the nested reservations | AM-1–AM-9 at ledger level | each request's own unit | per request (if P-M1) | no | good | higher: a process per request | **Fails AO-5 as stated:** it raises an admitted outer bound, which the preserved immutable outer reservation bound forbids, and no decision grants that permission. The completed comparison, with F′ and G, is v4 V4-D.2. |
```

**R4-25 replaces v3 line 1155 (in C3-VD).**
```text
v3:
No option is selected. The lead's comparison is ready for independent review. Any authoritative policy change, such as F's dynamic ceiling policy or P-M1, is the operator's selection (D-4a). Until then, later consequential requests on the root route are served only through the routing of C2-93, and their accepted cases stay OPEN.
v4:
No option is selected. The comparison, completed in v4 V4-D.2, is ready for independent review. Any authoritative policy change is the operator's selection (D-4a), and none may raise an admitted outer bound, borrow the first root's grant, add a cap or provider prerequisite, or accept a native failure. Until a selection exists, later consequential requests on the root route are served by the routing of C2-93 as amended by v4 V4-I.5 and V4-L, and their accepted cases stay OPEN.
```

**R4-26 replaces v3 line 1194 (in C3-VE).**
```text
v3:
- FD inheritance is an explicit roster; every other descriptor is `O_CLOEXEC`.
v4:
- FD inheritance is the exact per-process roster of v4 V4-E.2; every other descriptor is `O_CLOEXEC`.
```

**R4-27 replaces v3 line 1219 (in C3-VE).** Child_Ready enforced at COMMIT_CHILD.
```text
v3:
| `COMMIT` | E10 | ticket of a measured child |
v4:
| `COMMIT_CHILD` | E10 | v4 V4-E.3: the ticket of a measured child; byte equality of the relayed measurement frame; the helper-observed ancestry; and the sub-helper's own native `Decide` or `Decide_V2` = Ready on the bound material |
```

**R4-28 replaces v3 line 1223 (in C3-VE).** No command raises an admitted bound.
```text
v3:
| `SET_ROOT_CEILING` | option F only, if selected (D-4a) | raise or lower exactly by a reservation |
v4:
| (withdrawn in v4) | v3's `SET_ROOT_CEILING` would raise an admitted outer bound; no helper command changes an admitted bound (v4 V4-D.2, AO-5) | — |
```

**R4-29 replaces v3 lines 1321-1323 (in C3-VF5).** Three event kinds added (V4-F.2): `FRONT_OWNED` records the transition to FRONT_OWNED (g+1), which C2-62 names but v3's list lacked.
```text
v3:
    'HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION','UNKNOWN','RECONCILED',
    'REQUEST_QUEUED','REQUEST_TRANSFER_INTENT','REQUEST_INTAKE','REQUEST_ABANDON','REQUEST_RESPONDED',
    'DRAIN_STOP_INTENT','DRAIN_FREEZE','DRAIN_OFD_EVIDENCE','DRAIN_INTAKE','DRAIN_ABANDON','DRAIN_RELEASED')),
v4:
    'HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION','FRONT_OWNED','UNKNOWN','RECONCILED','ROOT_STOP_INTENT',
    'REQUEST_QUEUED','REQUEST_TRANSFER_INTENT','REQUEST_INTAKE','REQUEST_ABANDON','REQUEST_RESPONDED',
    'DRAIN_STOP_INTENT','DRAIN_FREEZE','DRAIN_OFD_EVIDENCE','DRAIN_INTAKE','DRAIN_ABANDON','DRAIN_RELEASED',
    'DRAIN_RECLAIMED')),
```

**R4-30 replaces v3 line 1397 (in C3-VG).** The original outer test, exactly (04.5, UNIT_INACTIVE).
```text
v3:
- `CLOSED_OUTER`: the helper pidfd terminal and the unit's inactive state with its main exit, observed through `OBSERVE_UNIT`;
v4:
- `CLOSED_OUTER`: exactly the original outer test of `actual_closed_and_outer_wait` (`rw/protected_root_supervisor.py:218-227`): after `CLOSED_NS`, the helper pidfd terminal (`:219`), the owned launcher's arguments equal to the dispatch's and its `wait ()` returned (`:220-222`), and the manager's `MainPID` equal to `0` (`:223-224`). No unit active-state condition applies. The root unit is launched with `RemainAfterExit=yes` (`rw/protected_root_resource.py:69`), and its reset happens only after `CLOSED_WITNESS`, as factual cleanup (C2-68);
```

**R4-31 replaces v3 line 1445 (in C3-VG).** RT-13 with harmonized stops (12.3 kept).
```text
v3:
| RT-13 | UNKNOWN; worker possibly alive | — | any | — | none | Wait; never stop | Automatic retain |
v4:
| RT-13 | UNKNOWN; worker possibly alive | — | any | — | none | Wait. Never stop on EOF, a deadline or the reconciler's own initiative. An authorized `job.cancel`, or the owner's own original failure capture, stops per M8 (v4 V4-F.5). A stop never settles or releases, and every hold stays | Automatic retain |
```

**R4-32 replaces v3 line 1451 (in C3-VG).**
```text
v3:
| RT-19 | descriptor `STOP_INTENT` … `OFD_EVIDENCE` | — | any | — | V-H.3 | Resume or ABANDON | Automatic |
v4:
| RT-19 | descriptor `STOP_INTENT` … `RELEASED`, or `RECLAIMED` | — | any | — | v4 V4-H.4 | Per window: resume, ABANDON, keep the new owner, or reclaim. Completeness is UNKNOWN wherever an armed interval was open | Automatic |
```

**R4-33 replaces v3 line 1452 (in C3-VG).**
```text
v3:
| RT-20 | request `TRANSFER_INTENT` without intake | — | any | — | `REQUEST_ABANDON(r)` | The request stays queued; the front serves it under the original gate once custody returns (V-I.6) | Automatic |
v4:
| RT-20 | request `TRANSFER_INTENT` without intake | — | any | — | `REQUEST_ABANDON(r, s)` | Offered at s+1 in RELAY mode while a reachable worker owns; otherwise queued, carried into g+1 and served by the front under the original gate (v4 V4-I.5, V4-L) | Automatic |
```

**R4-34 replaces v3 line 1466 (in C3-VH1).**
```text
v3:
1. **H0 STOP_INTENT(d)**, durable and **before any pause.** It records the role and the current spool head.
v4:
1. **H0 STOP_INTENT(d)**, durable and **before any pause.** It records the role, the current spool head and the open read-armed interval for a reader, or the open write-armed interval for the stdin writer (v4 V4-H.1, V4-H.2).
```

**R4-35 replaces v3 line 1477 (in C3-VH1).**
```text
v3:
   - **Successor slots.** These read raw, spool-first: `os.read` on readiness, append and hash-chain, then deliver.
v4:
   - **Successor slots.** These read raw and spool-first inside a durable read-armed interval: `os.read` on readiness, append, hash-chain and fsync, then deliver. A durable `DISARMED(P)` closes the interval only after the last fsync (v4 V4-H.1).
```

**R4-36 replaces v3 lines 1480-1483 (in C3-VH1).** Kernel write versus durable W (08.2, 08.3).
```text
v3:
     - A stop flag is checked after each `os.write` return and before any await.
     - The written count W is updated immediately after each `os.write` (`:328-329`).
     - So at a stop, W equals exactly the bytes the kernel accepted. Non-blocking pipe writes return their exact count **[unverified reasoning, RC-2]**.
     - No bytes are buffered in user space, because the remaining payload is the retained `payload[W:]`.
v4:
     - A stop flag is checked after each `os.write` return and before any await.
     - Every `os.write` happens inside a durable write-armed interval opened at the durable position W (v4 V4-H.2). W is updated in memory immediately after each `os.write` (`:328-329`) and made durable, closing the interval, before a stop is acknowledged.
     - So at a clean stop, the durable W equals exactly the bytes the kernel accepted. Non-blocking pipe writes return their exact count **[unverified reasoning, RC-2]**. After a crash inside an open interval, the position is unknown and no owner resumes the stream (v4 V4-H.2).
     - No bytes are buffered in user space, because the remaining payload is the retained `payload[W:]`.
```

**R4-37 replaces v3 line 1673 (in C3-VJ).** Exact tool keys (12.1).
```text
v3:
  - `runtime.tools`: a roster map with v1 semantics (`:285-295`). It must include every command the v2 root route runs by name (U-3: the V3 supervisor helper, `bwrap`, `systemctl` and `systemd-run`, under their installed names);
v4:
  - `runtime.tools`: a roster map with v1 semantics (`rw/protected_startup.py:285-295`: non-empty, every value inside the installation inventory, and each key a command name that `shutil.which` resolves to exactly its value). It must include the keys `bwrap` (`rw/protected_scoped_resource_runtime.py:732`), `resource_supervisor_v3` (`:73-74`), `systemctl` and `systemd-run`. The values of the last two are the run-scoped config's `systemctl` and `systemd_run` (`rw/protected_resource_runtime.py:171-172`) and plan-v1's `native_components` `systemctl` and `systemd_run` (`rw/root_worker_plan.py:18-20`). Any other key keeps its v1 meaning (v4 V4-J.2);
```

**R4-38 replaces v3 line 1678 (in C3-VJ).**
```text
v3:
- **Custody genesis v2** (`worldline.owner-provisioned-root-custody-v2`): the six v1 keys plus `prior_custody`, which is either `null` or exactly {`journal_sha256`, `head_event`} binding a retained v1 journal (C2-113).
v4:
- **Custody genesis v2** (`worldline.owner-provisioned-root-custody-v2`): exactly the six v1 keys plus `prior_custody`. `initial_event` is `null` in v2: the chain begins at the genesis origin (v4 V4-J.3). `prior_custody` is either `null` or exactly {`journal_path`, `journal_sha256`, `head_event`}, binding a retained, closed v1 journal (v4 V4-J.4, C2-113).
```

**R4-39 replaces v3 line 1689 (in C3-VJ).**
```text
v3:
| Crosswalk file (U-12) | v2 | The crosswalk provisioner, an offline ENTRY | Exclusive create. Refuses if present. |
v4:
| Crosswalk file (U-12) | v2 | The offline ENTRY `protected-root/provision_root_crosswalk.py` (v4 V4-J.2) | Exclusive create. Refuses if present. |
```

**R4-40 replaces v3 line 1690 (in C3-VJ).**
```text
v3:
| Custody v2 database, its `.lock` and the custody genesis (U-5) | v2 | The custody provisioner, an offline ENTRY | Exclusive create of all three. Refuses if any exists. The paths are exactly the plan's `handoff_journal`, that path plus `.lock` (today's lock rule, `rw/root_worker_journal.py:38`) and the plan's `handoff_genesis`. The database is in no source-lease selection (the `rw/protected_startup.py:345-346` pattern). When a v1 journal exists, `prior_custody` binds its sha256 and final head, and existing history is never re-genesised. |
v4:
| Custody v2 database, its `.lock` and the custody genesis (U-5) | v2 | The offline ENTRY `protected-root/provision_root_custody_v2.py` (v4 V4-J.3) | Exclusive create of all three. Refuses if any exists. The paths are exactly the plan's `handoff_journal`, that path plus `.lock` (today's lock rule, `rw/root_worker_journal.py:38`) and the plan's `handoff_genesis`. The database is in no source-lease selection (the `rw/protected_startup.py:345-346` pattern). When a v1 journal exists, `prior_custody` binds its path, sha256 and final head, and existing history is never re-genesised (v4 V4-J.4). |
```

**R4-41 replaces v3 lines 1749-1751 (in C3-VK2).** Bound to the sealed reviews.
```text
v3:
- R-QUAL **[depends on unreviewed CAPI5]**;
- R-W;
- R-GATE in the form that repairs V4-RC4-GATE **[depends on unreviewed CAPI5]**;
v4:
- R-QUAL (a)–(d) as fixed by CAPI6, with (d1)–(d4) (`CAPI6/APPENDIX-BINDINGS.md:90-101`), evaluated over the union sets of v4 V4-K.2 (bound to the sealed CAPI6R, closed at design level only);
- R-W;
- R-GATE as fixed by CAPI6, with the WF-X protocol checks CR5 and CR6 against the never-updated `CAPI_WFX_PROTOCOL` (`CAPI6/APPENDIX-BINDINGS.md:391-424`), evaluated over the union gate table of v4 V4-K.2 (bound to the sealed CAPI6R, closed at design level only);
```

**R4-42 replaces v3 line 1755 (in C3-VK2).**
```text
v3:
All are as defined in `CAPI4/DESIGN.md:450-490` and its stage rule (`:247`), with CAPI5's replacements as labelled.
v4:
All are as defined in `CAPI4/DESIGN.md:450-490` and its stage rule (`:247`), with CAPI5's and CAPI6's replacements as sealed by CAPI5R and CAPI6R (v4 V4-K.1).
```

**R4-43 replaces v3 lines 1828-1829 (in C3-VK5).** IC-11 and IC-12 repaired (IC assessments).
```text
v3:
| IC-11 | Per-call expanded qualifiers of root-worker routines, with indirect and transport-qualified mutation controls **[depends on unreviewed CAPI5]** | `F.P`-style path; `Pending_Transport.X` path |
| IC-12 | Branch-correct `RW_GATES` with exact accepted rejection diagnostics. Positive: a rejection diagnostic inside the rejection branch. Negative: the same selection on the accepted path. **[depends on unreviewed CAPI5]** | A `False` component on the accepted path |
v4:
| IC-11 | Per-call expanded qualifiers of root-worker routines over the union sets (v4 V4-K.2, U-1 … U-3), with (d1)–(d4) on the C_API specification, body and parent specification, including every prefix of every with clause. Indirect and transport-qualified mutation controls, and MQ-RW1 … MQ-RW5 | An `F.P`-style path; a `Pending_Transport.X` path; a with clause whose prefix is a listed simple name; an RW routine name occurring in an old scope |
| IC-12 | Branch-correct `RW_GATES` of kind `bool` or `case` only, with exact accepted rejection diagnostics; CAPI6's CR5 and CR6 over the union gate table, with `CAPI_WFX_PROTOCOL` unchanged (v4 V4-K.2, U-4 and U-5). Positive: a rejection diagnostic inside the rejection branch; the unchanged staged tables at every RW stage. Negative: the same selection on the accepted path; MX-RW1 … MX-RW3 | A `False` component on the accepted path; an RW `wfx` row; an RW key in `CAPI_GATE_EXCLUSIVE` |
```

**R4-44 replaces v3 line 1862 (in C3-VL3).** The dedicated lane is withdrawn (06.4).
```text
v3:
- Thread locks are acquired in this order: `Gate.mutex` → `order` → `store._lock` → journal and SQLite. They are acquired only inside synchronous lane functions, which contain no await.
v4:
- Thread locks are acquired in this order: `Gate.mutex` → `order` → `store._lock` → journal and SQLite. They are acquired only inside synchronous functions, which contain no await, on the threads the original code uses (v4 V4-L.1; v3's dedicated single-thread lane is withdrawn).
```

**R4-45 replaces v2 line 522 (in C2-36, carried through C3-B).** L-RB-1 reconciled with compaction (01.2).
```text
v2:
  - **L-RB-1.** A span valid in `Data` keeps its position and length, and its bytes are equal in `Data'`. Identity on `Data'Range`.
v4:
  - **L-RB-1.** Two variants, one per construction family (v4 V4-B.1). **L-RB-1P** (positional; the constructions that extend `Data`): a span valid in `Data` keeps its position and length, and its bytes are equal in `Data'`; identity on `Data'Range`. **L-RB-1C** (compaction, case S-b of v3 V-B.6): a span valid in `Data` maps to a span of the same length with equal bytes, valid in `Data2`, and two valid spans that lie in one maximal interval of the referenced union keep their relative offset, so overlap and aliasing are preserved. Both variants rest on L-RB-4.
```

**R4-46 replaces v2 line 571 (in C2-38, carried through C3-B).** W8 made frame-local (01.3).
```text
v2:
- **W8.** Every `Rows (i).Bound.Universe_Head` is `Same` as `State.Universe_Head`. This holds for reachable states by L-INV-1.
v4:
- **W8′ (frame-local; replaces W8).** For every i, `Rows (i).Bound.Universe_Head` is `Same` as the `Universe_Head` of the frame in which row i has its origin (the frame of `Retained_Origin`, `core/resource_scoped_run_ledger.ads:110-121`), and the last frame's `Universe_Head` is `Same` as `State.Universe_Head` (`History_Valid`, `:108`). With one frame this is exactly W8, which holds for reachable states by L-INV-1 (v4 V4-B.1).
```

**R4-47 replaces v2 line 1008 (in C2-62, carried through C3-B).** Never_Launched release kept (07.3).
```text
v2:
- **INV-C4.** PHYSICAL_SETTLED needs CLOSED_WITNESS on the root route.
v4:
- **INV-C4′.** On the root route, PHYSICAL_SETTLED, and any `Release_Hold` or charge of the root row, needs CLOSED_WITNESS for every row that is possibly launched, meaning any row with a present `Dispatch` fact. Only a row whose launch journal is `Never_Dispatched` and whose native class is `Never_Launched` may be released without it, by the original `Release_Hold` (v4 V4-G.1, r3′).
```

**R4-48 replaces v2 line 1053 (in C2-64, carried through C3-B).** Stops harmonized (04.1).
```text
v2:
- **Stops.** `retain_and_stop_unknown` stops a worker only after `ABANDON(g)` commits. When `CUSTODY_ACK(g)` exists there is no stop.
v4:
- **Stops.** For a handoff or capture failure, `retain_and_stop_unknown` stops a worker only after `ABANDON(g)` commits, and when `CUSTODY_ACK(g)` exists it does not stop it. Every other stop follows M8 (v4 V4-F.5): the original cancellation, failure-capture and helper stops of the current owner, and an authorized `job.cancel` when no owner is reachable. A stop never settles, releases or relabels anything, and EOF or a deadline alone never stops.
```

**R4-49 replaces v2 line 1383 (in C2-93, carried through C3-B).** UNKNOWN routing with cancellation.
```text
v2:
| UNKNOWN(cause) | Queued. No process mutates. | Queued | Queued | Queued | **Reconciler**: native redecision from durable custody, operation and physical evidence (§6.2). If a worker may still own state, it is never stopped (§6.6). Once evidence shows that no worker can act (its pidfds are terminal, with CLOSED or ABANDON), collection and reconstruction proceed. Use uncertainty then goes to K4 through `quarantine.resolve` on the reconstructed front (CD-2). |
v4:
| UNKNOWN(cause) | Queued, with authenticated QUEUED progress events (v4 V4-L.2). No process mutates the store. | Queued. An authorized `job.cancel` whose world owns this generation's root unit also causes the M8 stop of that unit (v4 V4-F.5); the stop settles nothing, and the response is the original handler's once custody returns | Queued | Queued | **Reconciler**: native redecision from durable custody, operation and physical evidence (§6.2). A worker that may still own state is never stopped on the reconciler's own initiative, on EOF or on a deadline (§6.6 with R4-48). Once evidence shows that no worker can act (its pidfds are terminal, with CLOSED or ABANDON), collection and reconstruction proceed. Use uncertainty then goes to K4 through `quarantine.resolve` on the reconstructed front (CD-2). |
```

**R4-50 replaces v3 line 1961 (in C3-VN).**
```text
v3:
- **V-I** (lab). A FRESH join without cookies → Ready. An unavailable correspondence → served later by the front, never refused. RETAINED and HISTORICAL with sockets Absent → Ready. Every gate in V-I.5 exercised by its mode.
v4:
- **V-I** (lab). A FRESH join without cookies → Ready. A declined FRESH join → served in RELAY mode, never refused. RETAINED and HISTORICAL with sockets Absent → Ready. Every gate in V-I.5 exercised by its mode and by its v4 V4-I.4 contract (v4 V4-M).
```

**R4-51 replaces v3 line 2028 (in C3-VQ).**
```text
v3:
- **[unverified reasoning]** and **[depends on unreviewed CAPI5]** statements need the named evidence or review.
v4:
- **[unverified reasoning]** statements need the named evidence. Statements bound to CAPI5R or CAPI6R carry those reviews' design-level status only (v4 V4-K.1).
```

**R4-52 replaces v3 line 396 (in C3-B; R3-18's result).**
```text
v3:
1. The front appends `REQUEST_TRANSFER_INTENT(r)`. The record holds the full raw request line, the original host observation, the front's own re-read at transfer (JF) and the socket identity. When available, it also holds the socket cookie and the namespace identities, as optional corroboration (v3 V-I.3).
v4:
1. The front appends `REQUEST_TRANSFER_INTENT(r, s)` with its mode, FRESH or RELAY (v4 V4-I.1). The record holds the full raw request line, the original host observation, the front's own re-read at transfer (JF) and the socket identity. When available, it also holds the socket cookie and the namespace identities, as optional corroboration (v4 V4-I.2).
```

**R4-53 replaces v3 line 1707 (in C3-VJ).**
```text
v3:
| `EFFECT_OBSERVED` or `SETTLED` → `recover_committed` (`:366`) | RT-7′ (U already observed) and RT-4 |
v4:
| `EFFECT_OBSERVED` or `SETTLED` → `recover_committed` (`:366`), outside any `try`, so a refusal there is a startup refusal for owner diagnosis (NF4-10) | RT-21 and RT-22 (v4 V4-G.4) |
```

**R4-54 replaces v3 line 1211 (in C3-VE).**
```text
v3:
| Capabilities (full root today; the C helper only measures them, `:178-199`) | full set | everything | partly | **M-3**: bounding set reduced to an enumerated list, each item justified (for example `CAP_SYS_PTRACE` for procfs reads of other uids and for kcmp). Excluded: `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_SYS_MODULE`, `CAP_SYS_RAWIO`, `CAP_SYS_BOOT`, `CAP_MKNOD`, `CAP_SETPCAP`, `CAP_BPF`, `CAP_PERFMON`, `CAP_SYS_RESOURCE`. Also `no_new_privs`, and a seccomp list excluding mount, unshare, setns, kexec, bpf and `pidfd_send_signal`. | measured by the credential frame | K-10, K-20 |
v4:
| Capabilities (full root today; the C helper only measures them, `:178-199`) | full set | everything | partly | **M-3**, made exact in v4 V4-E.4: every Linux capability is listed there with keep or drop and its justification; `no_new_privs`; the seccomp list | measured by the credential frame | K-10, K-20; RC-6 |
```

**R4-55 replaces v3 line 1964 (in C3-VN).**
```text
v3:
- **V-L** (lab). A stalled registered-root path does not block `status` for another requester. Lane FIFO. No callback acquires a lock (static audit).
v4:
- **V-L** (lab). A stalled registered-root path does not block `status` for another requester. No callback acquires a lock (static audit). Every row of the progress table of v4 V4-L.2 (v4 V4-M).
```

**R4-56 replaces v3 line 1442 (in C3-VG).**
```text
v3:
| RT-10 | CUSTODY_ACK(g); worker alive; front restarted | — | any | worker holds the transferred OFD locks (`rw/protected_startup.py:374-385` `_lock`; `rw/root_worker_journal.py:59-62`) | — | Diagnostic WORKER_OWNED_LIVE. No stop. | Automatic |
v4:
| RT-10 | CUSTODY_ACK(g); worker alive; front restarted | — | any | worker holds the transferred OFD locks (`rw/protected_startup.py:374-385` `_lock`; `rw/root_worker_journal.py:59-62`) | — | Diagnostic WORKER_OWNED_LIVE. The reconciler does not stop it. The worker completes its root operation under the original time limit and relinquishes (v4 V4-L.2); an authorized `job.cancel` follows M8 (v4 V4-F.5) | Automatic |
```

**R4-57 replaces v3 line 1983 (in C3-VO).**
```text
v3:
| RC-3 | Default executor and `to_thread` behaviour on the installed CPython (the lane design does not rely on its size) | V-L.2 |
v4:
| RC-3 | Default executor and `to_thread` behaviour on the installed CPython, which v4 keeps as the original thread placement (v3's dedicated lane is withdrawn) | v4 V4-L.1, V4-L.2 |
```

**R4-59 replaces v3 line 1173 (in C3-VE).** Launch intent before dispatch, as the original launch orders it (NF4-12).
```text
v3:
| E3 | Worker → helper | `CREATE_CHILD` on the helper command channel: task id, child reservation, leaf name, limits from the crosswalk child plan, delegation record digest | `CHILD_CREATE_INTENT(t)` | — |
v4:
| E3 | Worker, then helper | `Record_Launch_Intent` for the child row with its planned leaf unit, before any dispatch (as `rw/protected_scoped_resource_runtime.py:741`); then `CHILD_DISPATCH_INTENT(t)` with the ticket (v4 V4-E.3); then `CREATE_CHILD` on the helper command channel: task id, child reservation, ticket, leaf name, limits from the crosswalk child plan, delegation record digest | scoped commit; `CHILD_DISPATCH_INTENT(t)` | `Check_V2` with the native scope and universe guard |
```

**R4-60 replaces v3 line 1175 (in C3-VE).** The sub-helper keeps and relays the measurement channel.
```text
v3:
| E5 | Sub-helper → worker | `HELD_CHILD`: ticket, init pid; descriptors for namespace, pidfd, out, err, credential receiver and stdin writer | `CHILD_HELD(t)` | — |
v4:
| E5 | Sub-helper → worker | `HELD_CHILD`: ticket echo and init pid; descriptors for namespace, pidfd, out, err and stdin writer. The sub-helper keeps the credential receiver and relays (v4 V4-E.3) | `CHILD_HELD(t)` | — |
```

**R4-61 replaces v3 line 1176 (in C3-VE).**
```text
v3:
| E6 | Worker | Record_Launch_Intent, then Record_Running for the child row, with actual unit, cgroup and invocation from `HELD_CHILD` | scoped commits | `Check_V2`: Live classification under `Custody_V2` and `Delegated_Custody` (C2-51) |
v4:
| E6 | Worker | `Record_Running` for the child row, with actual unit, cgroup and invocation from `HELD_CHILD` (as `rw/protected_scoped_resource_runtime.py:767`) | scoped commit | `Check_V2`: Live classification under `Custody_V2` and `Delegated_Custody` (C2-51), with the native scope and universe guard |
```

**R4-62 replaces v3 line 1177 (in C3-VE).** GO keeps the original machine admission.
```text
v3:
| E7 | Worker → sub-helper | `GO_FORK` (`'G'`). Init forks the actor, which measures itself and waits for the commit (the `native_root_worker_supervisor_v1.c:166-227` pattern). | `CHILD_GO_FORK(t)` | — |
v4:
| E7 | Worker → sub-helper | `CHILD_GO_INTENT(t)` with the original machine admission (the `go_scoped` pattern, `rw/protected_scoped_resource_runtime.py:851-865`), then `GO_FORK` (`'G'`). Init forks the actor, which measures itself and waits for the commit (the `native_root_worker_supervisor_v1.c:166-227` pattern). | `CHILD_GO_INTENT(t)` | machine admission |
```

**R4-63 replaces v3 line 1178 (in C3-VE).**
```text
v3:
| E8 | Actor → worker | Credential frame: uids, gids, capabilities, securebits, no_new_privs, groups | `CHILD_MEASURED(t)` | — |
v4:
| E8 | Actor → sub-helper → worker | Credential frame: uids, gids, capabilities, securebits, no_new_privs, groups. The sub-helper receives it with `SO_PASSCRED`, keeps its exact bytes and relays a copy | `CHILD_MEASURED(t)`, with the frame's sha256 | — |
```

**R4-64 replaces v3 line 1180 (in C3-VE).** Child_Ready enforced where the commit is sent.
```text
v3:
| E10 | Worker → actor | Durable witness, then the commit ACK (the `wait_credential_commit` pattern, `native_root_worker_supervisor_v1.c:93`, `:224`). The actor execs. | `CHILD_READY(t)` | — |
v4:
| E10 | Worker → sub-helper → actor | The durable `CHILD_READY(t)` witness, then `COMMIT_CHILD`. The sub-helper checks its bindings and decides natively itself (v4 V4-E.3), and only then sends the commit ACK to the actor (the `wait_credential_commit` pattern, `native_root_worker_supervisor_v1.c:93`, `:224`). The actor execs. | `CHILD_READY(t)` | `Decide` / `Decide_V2` again, in the sub-helper |
```

**R4-58 replaces v2 line 561 (in C2-38, carried through C3-B).** W2 made frame-local, like W8.
```text
v2:
- **W2.** `Value (W.First_Epoch) ≤ Value (Rows (i).Bound.Resource_Epoch)` for every i, and `≤ Value (State.Resource_Epoch)`.
v4:
- **W2′ (frame-local; replaces W2).** For every frame F_j, `Value (F_j.First_Epoch) ≤ Value (Rows (i).Bound.Resource_Epoch)` for every row i whose origin is F_j, and `≤ Value (State.Resource_Epoch)`; the first frame's `First_Epoch` is a present zero-length quantity, whose value is 0. With one frame this is exactly W2 (v4 V4-B.1).
```

### B.3 Superseded v3 text

| v3 lines | v3 content | Status in v4 |
|---|---|---|
| 1-177, 193-195 | Header, §A.1 … §A.6 (answers to the v2 review) | Superseded by the v4 header and §A. History, not normative. |
| 692-741 | §C (truth boundary, aliases, labels, numbers) | Superseded by v4 §C |
| 1276-1298 | V-F.3's C×P rules; V-F.4 mutation table | V4-F.3; V4-F.5 |
| 1375-1390 | V-F.6 CAS and replay | V4-F.6 |
| 1495-1515 | V-H stdin EOF rules; V-H.3 failure table | V4-H.5; V4-H.4 |
| 1534-1592 | V-I.2 inputs; V-I.3 mode predicates | V4-I.1 … V4-I.3 |
| 1630-1649 | V-I.6 path; V-I.7 ordering | V4-I.5; V4-I.6 |
| 1718-1737 | V-K heading; V-K.1 status | V4-K.1 |
| 1769-1776 | V-K.4 aliases | V4-K.2 |
| 1852-1858 | V-L.2 thread placement (the dedicated lane) | V4-L.1 |
| 1866-1884 | V-L.4 router and collector; V-L.5 progress table | V4-L.2, V4-L.3 |
| 1891-1949 | V-M dependency graph | V4-A.5 |
| 1985-2022 | V-P open list | V4-O |
| 2034-2040, 2109-2128 | Appendices A, C, D | v4 Appendices A, C, D |

Every other line outside the §B.1 slices is a separator or an empty line.

### B.4 Reading rules

- **RR4-1.** Inside carried v3 slices, v3's reading rules RR3-1 … RR3-8 (in C3-B, with R4-17) apply, and the aliases are those of v4 §C.2.
- **RR4-2.** A reference inside a carried slice to a superseded v3 section resolves through §B.3: V-F.3's C×P rules → V4-F.3; V-F.4 → V4-F.5; V-F.6 → V4-F.6; V-H.3 → V4-H.4; V-I.2 and V-I.3 → V4-I.1 … V4-I.3; V-I.6 → V4-I.5; V-I.7 → V4-I.6; V-K.1 → V4-K.1; V-K.4 → V4-K.2; V-L.2 → V4-L.1; V-L.4 and V-L.5 → V4-L.2 and V4-L.3; V-M → V4-A.5; V-P → V4-O. A reference to a carried section means that slice with its R4 replacements.
- **RR4-3.** "v3 X" inside an R4 text means v3 section X as carried; "v4 Y" means this file's section Y.
- **RR4-4.** An R4 that replaces a line of an R3 block's `v3:` text changes that R3 replacement's result; the block's `v2:` text is unchanged. R4-45 … R4-49 and R4-58 replace v2 lines that no R3 replaces, inside the C2 slices that C3-B binds.
- **RR4-5.** Numbers inside carried slices keep the status their source gave them: observed, or JACKAL exact (v2 J01 … J18). They are not re-derived.
- **RR4-6.** "AUTHOR-NOTES" inside a carried v3 slice means v3's `AUTHOR-NOTES.md` (`dd382e1b…a0ea`); inside a carried v2 slice it means v2's (RR3-7).
- **RR4-7.** Any remaining "UNREVIEWED" or "[depends on unreviewed CAPI5]" wording inside carried text is historical. The current C-API status is V4-K.1.
- **RR4-8.** "Join" inside carried text means `Transfer_Join` before intake and `Serving_Join` after it (V4-I.1). "J8" means the head conjunct of whichever of the two applies.

---

## C. Truth boundary, bases and method

### C.1 What was done

- **Reading only.** The Read tool and read-only Bash (`sed -n`, `grep`, `sha256sum`, `wc`, `cut`, `nl`, `fold`, `awk`, `command ls`, and Python scripts on standard input that read files and printed to standard output). No output was redirected to a file; `2>&1` only into a pipe. Details and one process deviation: AUTHOR-NOTES §2.
- **Not run.** No compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. Nothing under `/srv`.
- **Not read.** `WT/packets/capi-pk0/`; `~/.local/share/sia/.gbrain/`. The lane draft was read and not changed.
- **SIA.** One `sia.ask` at the start of this task. Nothing from SIA is used as evidence here (AUTHOR-NOTES §3). No SIA note was written.
- **Skills.** The eight Ada skills were loaded for this task and applied: `ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`. The SPARK User's Guide is release 28.0w documentation, not evidence about the installed toolchain.

### C.2 Bases (aliases)

| Alias | Path |
|---|---|
| `W` | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` |
| `WT` | `W/work/claude-lead-isolation-v1/wt-1` |
| `L` | `W/work/protected-original-root-worker-repair-v1` (the draft lane) |
| `R` | `L/source`. Unprefixed `core/…`, `runtime/…` and `protected-*/…` paths are relative to `R`. |
| `rw/` | `R/runtime/worldline/` |
| `D2`, `D2R` | `WT/designs/claude-root-worker-seam-design-v2`, and its `review/gpt61-v1` |
| `D3`, `D3R` | `WT/designs/claude-root-worker-seam-design-v3`, and its `review/gpt61-v1` |
| `CAPI4`, `CAPI4R` | `WT/designs/claude-capi-boundary-design-v4`, and its sealed review |
| `CAPI5`, `CAPI5R` | `WT/designs/claude-capi-boundary-design-v5`, and its sealed review `review/gpt61-v1` |
| `CAPI6`, `CAPI6R` | `WT/designs/claude-capi-boundary-design-v6`, and its sealed review `review/gpt61-v1` |
| `S5` | `W/work/claude-composition-v5-beta/source` |
| `A1` | `W/work/scoped-committed-envelope-repair-v2-retry1` |
| `CHILD` | `W/work/resource-child-authority-source-v1` |
| `P1/` | `W/outputs/claude-phase1-handoff-20261004/` (`P1:n` is `HANDOFF.md`, line n) |
| `PROMPT` | `/home/sicarii/Documents/complete-phase1-prompt.txt` |
| `D:n`, `D2:n`, `D3:n` | v2 or v3 `SEAM-DESIGN.md`, line n, as the reviews cite |

### C.3 Status labels

| Label | Meaning |
|---|---|
| OBSERVED | Read from a file or printed by a read-only command. |
| STATIC_REASONING | The author's inference from read source. Not executed. |
| [unverified reasoning] | Kernel, systemd, interpreter or Ada-visibility semantics as the author reads them, naming a K or RC item. |
| (bound to the sealed CAPI6R) | Relies on a C-API rule whose sealed review closes it at design level only. |
| DESIGN | A proposal for review. |
| OPEN | An obligation not discharged. |

### C.4 Numbers

Every count or line number in this document is observed: read from a file or printed by a read-only command. Counts quoted from the reviews, v2, v3 or the C-API designs keep their own status. No numeral here was derived by arithmetic, so no JACKAL call was needed (Appendix A, `jackal.json`).

---

## V4-A. Typed contracts, native inputs and the dependency graph (V3-REQ-A; 01.1, 03.3, 11.1; D-1a, D-5a)

v3 V-A (C3-VA, with R4-18) is carried: the two families V1 and V2, the consumer table, deployment-level selection, L-BR-1 and the unchanged V1 references. V4-A completes each contract.

### V4-A.1 Contract form

Every consumer below has five parts. Each is an obligation of its spec node (V4-A.5) and stays OPEN until proved with its caller.
1. **Inputs.** The exact Ada types of its export, V1 or V2, and nothing else. No caller flag selects a branch.
2. **Current-fact packet.** The single current observation it consumes, with the producer that builds it and the re-read that keeps it current.
3. **Producer contract.** What the producer guarantees about the packet (its post), and what it may assume (its pre).
4. **Wrapper contract.** Exact-type dispatch (`type (x) is …`), the export's version and layout check against the loaded library, and the named refusal for any other type.
5. **ABI.** The exported symbol family (`…_v1` / `…_v2`), unchanged for V1.

### V4-A.2 Consumers

| Consumer | Inputs (V1 / V2) | Current-fact packet and producer | Producer pre → post | Wrapper | ABI |
|---|---|---|---|---|---|
| S1 scoped canonical operation (pre-effect) | V1: `Decide` over `S.Facts_Array`, `S.Native_Valid`, `S.Current_Facts` (`core/resource_scoped_run_ledger.ads:44`, `:247-268`, `:296-300`). V2: `Decide_V2` over `S2.Facts_V2_Array`, `S2.Selection_Array`, `S2.Native_Valid_V2`, `S2.Current_Facts_V2` | `current_snapshot ()` re-read under `operation_lock` (`rw/protected_scoped_resource_runtime.py:642-646`, `:696`); V2: `ScopedV2Producer` over the same snapshot | pre: the deployment selects the family (V4-A.4) and the caller holds `operation_lock`. post: every row's facts are built from that one snapshot (PD-1); `before == current_snapshot ()` (PD-4); in V2, each P8–P11 pair has records from distinct producers (C2-42, V-C) and each `Base` equals the V1 producer's facts for the same snapshot | `ScopedCanonicalOperationKernel.observe` (v3 V-A.2) | `wl_scoped_canonical_operation_{version,layout,decide}_v1` and `…_v2` |
| B2b scoped exchange (in request and recovery) | V1 `Scoped_Canonical_Exchange.Decide`; V2 `Decide_V2` | in request: the broker's current snapshot (`rw/canonical_full_broker.py:147-174`); recovery: the retained original snapshot (`rw/protected_operations.py:430-438`) | post: Retained_Join inputs (v3 V-B.10) and, for recovery, `Reserved_New` replay on the retained snapshot | `ScopedCanonicalExchangeKernel` | `…_v1` / `…_v2` |
| B2c scoped K4 | V1 `Scoped_Owner_Completion.Decide`; V2 `Decide_V2` | the quarantined row's retained capture, plus the resolving request's own fresh use (`rw/protected_operations.py:820-830`) | post: retained origin, quarantine head equality (`:824`) | `ScopedOwnerCompletionKernel` | `…_v1` / `…_v2` |
| Root admission | V1 `Root_Admission` (`core/worldline-resource_child_execution.ads:172-184`); V2 `Root_Admission_V2` | the root capture (`rw/protected_root_observation.py:98-135`) | post: the V1 controller's pairs from distinct producers in V2 (P1–P7, v3 V-C.4); P3 by `Process_Images_Covered` (V4-C.4) | existing root wrapper / new V2 wrapper | unchanged / new |
| Child decision and task admission | V1 `Decide` (`:194-208`), `Task_Admission` (`:248-257`); V2 `Decide_V2`, `Task_Admission_V2` | the child measurement and ancestry of V4-E.1 (E8, E9) | post: actor observation from the relayed frame; ancestry from helper frames and the read-only procfs view (V4-E.3) | existing / new; and the sub-helper's own call at COMMIT_CHILD (V4-E.3) | unchanged / new |
| Scoped ledger transition | V1 `S.Check` (`:443-457`); V2 `S2.Check_V2` | the scoped service's current packet (`rw/protected_scoped_resource_service.py:56`) | post: `Shape`, `Physical`, `Contained`, `History_Prefix` (PD-2, PD-3, PD-5) | scoped commit: `ScopedPacket` → `Check`, `ScopedPacketV2` → `Check_V2` | unchanged / new |
| Custody relation | `Root_Custody_Phase.Legal`, `Next`, `Mutation_Allowed` (V4-F) | the loaded custody chain and state rows (V4-F.6) | pre: `Custody_Chain_Valid` under the selected key (V4-C.1). post: state rows equal the native fold of `Next` (V4-J.3) | `RootCustodyKernel`, exact types `CustodyState`, `CustodyEvent` | new |
| Requester correspondence | `Transfer_Join`, `Serving_Join`, `Relay_Join` (V4-I.1) | the typed operand record of V4-I.2 | post: every operand decoded from retained bytes; no PID label substituted | `RequesterKernel`; exact types `CrosswalkRequestPeer`, `RelayRequestPeer` | new |
| Source records and roster | `Source_Json`, `Roster_Join`, `Number_Canonical` (V4-C) | the selected containers as DATA | pre: the Python exact check passed. post: native recognition agrees | `SourceKernel` | new |
| HMAC and chain | `Hmac_Sha256`, `Custody_Chain_Valid` (V4-C.1, V4-C.2) | key bytes, genesis bytes, event rows and head row in a private arena | pre: P-A1 … P-A4 (premises, not proved) | `ChainKernel` | new |
| Child relation | `Child_Event_Legal` (V4-E.1) | the child's scoped observation events | post: one legal successor per event | `ChildKernel` | new |

### V4-A.3 Native-input dependencies

| Native unit | Consumes (other native units) | Consumed by |
|---|---|---|
| `Hmac_Sha256`, `Custody_Chain_Valid` (S2H) | `Attest.SHA256` | `Root_Custody_Phase` loader (B9), startup (B11) |
| `Source_Json`, `Number_Canonical`, `Roster_Join` (S2) | `Attest.SHA256` | `Source_Record` (`Container_Bound`), `Root_Crosswalk`, `Requester_Correspondence` (source containers), V2 controllers |
| `Root_Crosswalk` (S3) | `Source_Json`, `Roster_Join` | `Enforcement_Corresponds`, S1 (plan and cost joins), dispatcher (child plans) |
| `Resource_Observation_Classification_V2`, `Resource_Scoped_Run_Ledger_V2`, `Resource_Child_Execution_V2` (S4) | `Source_Record` (`Pair_Valid`), `Root_Crosswalk` (delegation record), the V1 units unchanged | S1 (V2 entries), B2b, B2c, child decisions |
| `Requester_Correspondence` (S8) | `Source_Json` (request document), `Roster_Join` | `Root_Custody_Phase.Legal` for `REQUEST_INTAKE` (input: a `Transfer_Join` result), gate successors |
| `Root_Custody_Phase` (S9) | `Custody_Chain_Valid` (load), the `Transfer_Join` result | every mutation gate (V4-F.5), S6, S7 |
| `Child_Event_Legal` (S12) | S4 decisions as recorded inputs, `Root_Custody_Phase` (generation and owner) | dispatcher, sub-helper |
| S1 scoped canonical operation | S2, S3, S4 | pre-effect, B2b, B2c |

### V4-A.4 Which family decides, and the original routes

- **V2 is selected** only when the startup descriptor's exact schema is `worldline.protected-startup-v2` (V4-J.2) **and** the crosswalk names an authentic V2 producer for every live row (v3 V-A.3, first bullet).
- **Otherwise everything stays V1,** including on a v2 descriptor. The original families, ABIs and routes keep serving, and the V2 route's absence refuses nothing (R4-18). Where a V2-only capability is absent (for example delegated child rows), a request keeps the treatment it has without the V2 family. On the lane, workload operations keep the named OPEN refusal of the serial route (`rw/protected_operations.py:744-745`; NF4-2) and of C2-55 item 1 (G-2). That refusal predates this design; v4 adds none.
- **No conversion.** No function converts a V1 packet into a V2 packet or back.

### V4-A.5 Dependency graph and preparation order (replaces v3 V-M)

**Spec nodes.** Passive lead drafting, each independently reviewed by actual GPT-6.1.

| Spec | Content | Depends on |
|---|---|---|
| S0 | SL-0 hygiene and the lock model (V4-L); no native spec | — |
| S2 | `Source_Record`, `Source_Json`, `Number_Canonical`, `Roster_Join`, `Root_Controller_V2` (V-C, V4-C) | existing types, `Attest` |
| S2H | `Hmac_Sha256`, `Custody_Chain_Valid`, and the archive grammar they read (V4-C.1) | `Attest` |
| S8 | `Requester_Correspondence`: `Transfer_Join`, `Serving_Join`, `Relay_Join` and the operand record (V4-I) | S2 |
| S3 | `Root_Crosswalk`, `Enforcement_Corresponds` (V-C.6, V-D.3) | S2 |
| S9 | `Root_Custody_Phase`: State, Event, `Legal_Reference`, `Next`, `Mutation_Allowed`, including the request and descriptor products (V4-F) | S2H, S8 |
| S4 | Classification and ledger V2 (C2-51) | S2, S3 |
| S7 | Slot and drain transfer with armed intervals (V-H, V4-H) | S9 |
| S1 | Scoped canonical operation, V1 and V2 entries (V-A, V-B, V4-B) | S2, S3, S4 |
| S12 | `Child_Event_Legal` (V4-E.1) | S4, S9 |
| S6 | State model, O mapping, `finish` split, adapters, crash routes (V-F.2, V4-G) | S1, S9 |
| S10 | Multiplexing and accounting: alternatives may be drafted before D-4a; a selected specification needs the D-4a decision (V4-D, V4-L) | S1, S3, S4, S7, S8, S9 |
| S11 | Startup union, initial authentication, migration and reconciliation (V4-J, V4-G.4) | S2H, S3, S4, S6, S7, S9 |

**Preparation order**, consistent with every edge above:
1. S0, S2, S2H;
2. S8, S3;
3. S9, S4;
4. S7, S1, S12;
5. S6, S10 (alternatives only);
6. S11.

Every node's dependencies are in earlier waves: S1 (wave 4) precedes S6 (wave 5). S10 is drafted passively; its completion claim waits for the already-reserved D-4a decision, and that is not a drafting gate (review clarification).

**Body and caller nodes.**

| Body | Content | Needs |
|---|---|---|
| B0 | SL-0 source changes | S0; G-A1 for the A1-origin files |
| B2H | HMAC and chain bodies; custody v2 loader | S2H, B0 |
| B9 | Custody bodies, journal v2, provisioners, mutation-gate choke points (V4-F.5) | S9, B2H, B0 |
| B-RECV | Full-roster receive, `CrosswalkRequestPeer`, `RelayRequestPeer`, gate successors, relay channel | S8, B9 |
| B7 | Slot transfer with armed intervals | S7, B9, B-RECV |
| B3 | Crosswalk, pair producers, V2 controller callers, number canonicality | S2, S3, B9 |
| B1 | Scoped canonical operation bodies and wrappers (V1 and V2); the root route's restored serial order (V4-B.5) | S1, S2, S3, S4, B3, B0 |
| B2b, B2c | Exchange and K4 successors | S1, S4, S6, B1, G-A1 |
| B6 | `finish` split, adapters, collector settlement, reconstruction seed (V4-G) | S6, B1, B2b, B2c, B9 |
| B4 | Delegation bodies, helper successor and sub-helper, dispatcher (V4-E) | S4, S12, B3, B6, B7, B9 |
| B10 | Request multiplexing, relay and the progress model | S10, B1, B3, B4, B7, B9, B-RECV |
| B11 | Startup union, migration and reconciler | S11, B2H, B3, B6, B7, B9 |
| B12 | Seal: pins, freeze, enrollment, rosters (C2-12) | all bodies |
| Exports of B1, B2b, B2c, B2H, B3, B4, B9 and B-RECV | | G-RW |

**Integration gates** (unchanged in meaning; review dependencies, not operator gates):

| Gate | Condition | Needs |
|---|---|---|
| G-CAPI | The C-API successor composed after its own stage reviews; CAPI6R closes its rules at design level only | — |
| G-CAPI-P | L-CAPI-P reviewed and composed | G-CAPI |
| G-PROT | L-PROT composed by explicit reviewed import (P1:153) | G-CAPI-P |
| G-RW | Root-worker stages rebased under V4-K.2; IC-1 … IC-14 pass | G-PROT |
| G-A1 | L-A1 selected and frozen separately | — |
| G-DEP | L-DEP selected, reviewed and frozen | — |
| G-REVIEW | Different-author actual gpt-6.1-sol review per slice and for the full lane | every node |

**Runtime gates** R-PROOF, R-LAB and R-PUB are unchanged in meaning (C2-16).

---

## V4-B. One witness and Rebase specification; residual audit; RQ-1 (V3-REQ-B; 01.2, 01.3, 01.5, 01.7; D-1a, D-1b)

v3 V-B (C3-VB, with R4-19 and R4-20) is carried. The witness laws are C2-38 with R3-4 as replaced by R4-2, R4-46 and R4-58, and the arena lemmas are C2-36 with R3-32 as replaced by R4-45.

### V4-B.1 The consistent set of witness laws

**Field forms.** (a) a present zero-length span; (b) an alias of an original span; (b′) a one-byte sub-span `(Negative => False, First => p, Length => 1)` of `Data` over a non-zero byte, used only for N; (c) fresh bytes outside every rebased original span. Every form-(b) and form-(b′) span is a span of `Data`, so it is subject to the construction's `Rebase` like any original span.

**Which construction uses which arena law.**

| Construction | Arena | `Rebase` | Field forms | Witness laws |
|---|---|---|---|---|
| Single frame (v3 V-B.4) | `Data'` = `Data` plus a region `WD` after `Data'Last` or before `Data'First` | identity on `Data'Range` (L-RB-1P) | (a), (b), (b′), (c) in `WD` | W1, W2′, W3 … W7, W8′, W9, W10; with one frame W2′ = W2 and W8′ = W8 |
| Multi-frame (v3 V-B.5) | as above | L-RB-1P | as above | the same; W2′ and W8′ per frame |
| Saturated, case S-a (v3 V-B.6) | `Data` itself; no `WD` | identity | (a), (b), (b′) only | the same; L-RB-3 holds vacuously |
| Saturated, case S-b (compaction) | `Data2`: the maximal intervals of the union of every referenced span, in order, then the constants | the compaction map (L-RB-1C) | (a), (b), (b′) mapped; (c) in the appended constants | the same |

**Consistency, law by law.**
- **W2′ and W8′** (R4-58, R4-46). The multi-frame construction gives each run of equal universe head its own frame, whose `First_Epoch` is the run's least epoch (zero-length for the first frame) and whose `Universe_Head` aliases the run's head. Each row's origin is its run's frame, by validity condition (i) of v3 V-B.5 and `Retained_Origin` (`core/resource_scoped_run_ledger.ads:116-121`). So both laws hold frame by frame, and the last frame carries the state's head (`History_Valid`, `:108`). On one frame they are the carried W2 and W8, so the single-frame construction and the closed clause 01.4 are unchanged.
- **W3** (L-SAT-1′, R4-20). N is form (b′) when `Data` has a non-zero byte, and form (c) otherwise. Its choice reads no clause and no decision (W10), so a C1 refusal changes nothing. W3 (`Value (W.N) > 0`) therefore holds on every input that has any construction. `Projection_Valid` and `Contained_Reference` need positive numerator and denominator (`:144-145`, `:200-201`), and N = D makes the projection exact with no remainder (`:149-152`).
- **L-RB-1P and L-RB-1C** (R4-45). The positional variant serves the constructions that only extend `Data`; the compaction variant serves case S-b. L-RB-2 (invalid spans map to a canonical invalid span) and L-RB-3 (no overlap with `WD` or with the appended constants) hold in both. Under compaction, every referenced span lies inside one maximal interval of the union, and that interval moves as a block, so content, length, validity, overlap and aliasing are kept.
- **L-RB-4** (position independence; statement, to prove). Every predicate used by the original `Reference` and by the scoped `Reference` depends only on span contents, lengths and validity, never on absolute positions. A first static audit (OBSERVED, `grep` of the specifications): the positional uses in `core/resource_quantities.ads`, `core/resource_reservation_transition.ads`, `core/resource_run_ledger.ads`, `core/resource_scoped_run_ledger.ads`, `core/resource_observation_classification.ads` and `core/worldline-canonical_operation.ads` are span validity (`resource_quantities.ads:25-28`; `resource_reservation_transition.ads:85-88`), content reads of the form `Data (X.First + Offset)` within the span (`resource_quantities.ads:34-35`; `resource_reservation_transition.ads:97-100`; `resource_run_ledger.ads:216-221`; `resource_observation_classification.ads:35-36`; `worldline-canonical_operation.ads:16`), and array-index alignment between parallel arrays (`resource_scoped_run_ledger.ads:271-284`). No comparison of two spans' positions was found. Bodies whose `Post` equals a reference function inherit it. The audit of every called body, and of the new successor units, stays OPEN.
- **W9** (R4-2) names the forms and the arena laws above.
- **W10** is unchanged. No witness field is computed from any decision.

### V4-B.2 Audit of every scoped conjunct that has no flat counterpart

The scoped C2 is C2-31's lifted clause with R3-25: `S.Valid` (= `Shape`, `Physical_Reference`, `Contained_Reference`, `Current_Valid`; `core/resource_scoped_run_ledger.ads:303-308`), `S.Native_Valid` (`:247-268`), `S.Current_Facts` (`:296-300`) and the bound row's `Retained_Origin`. The flat C2 is `L.Conserved`, `L.Contained`, `L.Native_Valid` and the bound-row join.

| Scoped conjunct | Flat counterpart | Discharged on D_emb by | Inputs on which no construction discharges it |
|---|---|---|---|
| `History_Valid` (`:92-109`) | none | every frame field by form (a) or (b); first epochs strictly increasing (validity (i)); `Prior_Frame` chain; common store genesis and id; distinct frame heads (rows have distinct reservations, `core/resource_run_ledger.ads:233-235`); last frame = state scope, head and history head (W8′) | R1 (validity (i) or (ii) violated); R3 (no distinct last-frame head can be placed) |
| `Retained_Origin` of every row (`Shape`, `:122-127`) | none (flat `Shape` checks contexts, `core/resource_run_ledger.ads:223-235`) | W2′, W8′ and the frame epoch intervals; row scope `Same_Context` with the state's (flat `Shape`) | R1 |
| Distinct reservations and operations (`Shape`) | flat `Shape` (`core/resource_run_ledger.ads:233-235`) | identical predicate on unchanged rows | none: equal decisions |
| `Projection_Valid` of every row (`:135-152`) | none | key from W (zero-length resource and unit; machine aliases the scope host); binding and origin aliases; N = D positive (L-SAT-1′); amount equal to `L.Amount` (W4) | R3 (no positive N can be placed) |
| Bucket rules of `Physical_Reference` (`:181-191`) | `L.Conserved` | one bucket whose totals alias `State'`; equality with `Charge_Reference` on D_emb by W4 (C2-39's L-C2 lemmas) | none: a flat `Conserved` failure is a scoped `Physical_Reference` failure, and both give `Resource_Refused` |
| `Contained_Reference` (`:195-211`) | `L.Contained` | N = D; one key for every row | none: L-C2 lemmas |
| `Current_Valid` (`:215-231`) | none | current fields from `State'` and the last frame (W5) | R3 (a needed constant cannot be placed) |
| scoped `Native_Valid`, including `Classify` per row (`:232-268`) | flat `L.Native_Valid` (`core/resource_run_ledger.ads:266-282`) | W5, W6 (`Observed` = `K.Classify` of the facts), W7 | R2 |
| `Current_Facts` (`:296-300`) | none | W5 (each fact's current header is the state's) | R2 (when W5 and W6 cannot hold together) |
| C1, and C3 with the bound row's scope (R3-26) | flat C1, C3 | identical; L-C3 | none |

### V4-B.3 Residual classes

| Class | Definition | Who decides | Status |
|---|---|---|---|
| R1 | Multi-frame inputs that violate validity condition (i) or (ii) of v3 V-B.5 | the unchanged original unit, as for every flat input | Not in D_prod (L-INV-1); coverage OPEN |
| R2 | Inputs for which no facts make W5, W6 and W7 hold together | the original unit | Not in D_prod; coverage OPEN |
| R3 | Inputs that need a constant (a text constant of `Custody`, `Live_Holds` or `Reaped_Holds`, the positive numeral of form (c), or a distinct last-frame head) that can be placed neither in `WD` nor after compaction | the original unit | Beyond any producer-allocatable arena (STATIC_REASONING); coverage OPEN (RQ-2) |
| R0 | Every input of D_raw \ D_emb that is not in R1, R2 or R3 | the original unit | CV-R is the obligation that R0 is empty. It stays OPEN; v4 does not claim it. |

No original raw input or fixture leaves the system: every flat input is decided by the unchanged original unit (G-1), and every fixture keeps running (CV-C with R4-15). Scoped callers present only scoped packets made by the scoped producer (v3 V-B.2).

### V4-B.4 Obligations, unchanged in strength

CV-B′ (D_prod ⊆ D_emb) and CV-R stay stated and unproved. L-SAT-1′, L-RB-1P, L-RB-1C, L-RB-4 and W2′/W8′ are added statements. Their proofs, and every carried lemma of C2-38, C2-39 and C2-310, stay OPEN. The qualified fixtures and positives of v3 V-B.9 stay required, and V4-M adds the law-specific vectors.

### V4-B.5 The root route's guard and exception order (RQ-1 root/serial exception; DF-3; NF4-1)

The root route runs the serial route's order (`rw/protected_operations.py:727-768`), with the root launch in place of the in-process handler:

| Step | Serial route (source) | Root route (v4) |
|---|---|---|
| 1 | genuine request context (`:728`) | same check, same refusal |
| 2 | unresolved-use gate, only `quarantine.resolve` excepted (`:730`) | same |
| 3 | owner branch (`:731-741`) | owner operations never reach the root route (`:723-725`) |
| 4 | `_reserve` (`:742`) | same |
| 5 | workload refusal, then quarantine on exception (`:744-745`, `:767-768`) | same refusal for the same operations, until a reviewed dispatcher exists (C2-55 item 1; NF4-2) |
| 6 | `pre_effect`, `RESERVE_USE` replay must be `RESERVED_REPLAY`, `EFFECT_INTENT` with boundaries `[pre-effect, DISPATCH_INTENT]` (`:746-749`) | identical, including the `DISPATCH_INTENT` boundary that the draft omits (`rw/protected_root_worker.py:170-171`) |
| 7 | the handler inside `OperationScope` (`:750-754`) | `Record_Launch_Intent`, dispatch, HELD, `Record_Running`, GO, `EXECUTION_NATIVE`, ACK, then the handoff; the worker then runs the handler inside the same `OperationScope` semantics |
| 8 | any exception after step 4: `quarantine (operation, exc)`, native `QUARANTINE_USE`, unless the row is SETTLED or RELEASED (`:767-768`, `:770-777`) | **before `CUSTODY_ACK(g)` commits:** the front quarantines exactly so, and physical failure capture follows the original (`retain_and_stop_unknown`), with the handoff-window rule of §6.6 as amended by R4-48. **After `CUSTODY_ACK(g)`:** the worker owns U (M1), and its own invoke path applies the same quarantine on its exceptions; the front never writes the operation journal; a dead worker's U is decided by the collector (RT-7′, RT-8). |

### V4-B.6 Rollover, window by window (RQ-1 recovery and cost mapping)

Scope or universe rollover is refused only by the three native commands that check current context: Reserve, `Record_Launch_Intent` and `Record_Running` (`core/resource_scoped_run_ledger.ads:359`, `:436-438`). A rollover of the root head, PRIME, catalogue head or physical head alone is not `Context_Changed` there (NF-2), but every other original gate still applies, including each command's own `Current_Valid` (`:426-430`).

| Window (root route) | Native refusal | U (operation journal) | P (scoped row and physical) | Recovery | Cost |
|---|---|---|---|---|---|
| W0: before Reserve | Reserve with a stale request scope: `Context_Changed` | no row | no hold | none needed | the request fails, as original |
| W1: Reserve → pre-effect | none: the pre-effect uses Retained_Join, with C1 unchanged (R3-25 … R3-31) | `EFFECT_INTENT` | RESERVED | continues to W2 | none |
| W2: `EFFECT_INTENT` → `Record_Launch_Intent` | `Record_Launch_Intent`: `Context_Changed` | `QUARANTINED` by step 8 | launch journal `Never_Dispatched`, class `Never_Launched` → `Release_Hold` (PR-a, r3′) | P automatic; U by K4 through `quarantine.resolve` | one owner K4 resolution; no physical effect |
| W3: Launch_Intent and HELD → `Record_Running` | `Record_Running`: `Context_Changed` | `QUARANTINED` by step 8 | dispatched, held init, no GO; the failure capture stops the unit. Without the helper's `CLOSED … ECHILD` frame, `Reaped_Holds` cannot hold (`core/resource_observation_classification.ads:108-114`), so the class is `Unknown` → `Retain_Uncertain` (PR-b, RT-5) | U by K4; P by owner recovery from authentic closure evidence | an uncertain hold until the owner acts, and one K4 resolution |
| W4: after `Record_Running` | none of the three guards applies after Running (GO has none) | normal | normal; settlement joins the origin (v3 V-B.10) | normal | none |
| W5: head-only rollover, any time | none from the three guards | normal | normal | normal | none |

**Equality with the original.** In every window the durable outcome is what the original native scoped kernel and the serial route's exception mapping give for the same refusal point. Any launch performed by a handler happens after `EFFECT_INTENT` (`:749-754`), and any exception reaches `:767-768`. No window turns an originally accepted request into a refusal; W2 and W3 are original native refusals. Their costs are the original costs: a K4 owner resolution, and in W3 an uncertain hold. RQ-1 stays OPEN until the rollover positives and refusals of v3 V-B.9, V-B.10 and V4-M exist with proofs.

---

## V4-C. Authenticity premises, JSON forms and P3 (V3-REQ-C; 02.1, 02.2, 02.3; D-7a)

v3 V-C (C3-VC, with R4-21 … R4-23) is carried.

### V4-C.1 Independent selection chain, and the premises it rests on

Each object is selected by an earlier link, never by the bytes it carries:

| Link | Selects | How (source) | v2 change |
|---|---|---|---|
| 1. Installation | the startup descriptor | the daemon's installed entry passes the descriptor path; `StartupLease` binds it as DATA (`rw/protected_startup.py:172`) | none |
| 2. Descriptor | the owner plan | v1: an endpoint argument, bound only as DATA (NF-10). v2: `root_worker.owner_plan`, and any argument must equal it (V-J.2) | v2 only |
| 3. Plan (plan-v1 keyset, `rw/protected_root_worker.py:98-104`) | the custody journal and genesis paths | `handoff_journal`, `handoff_genesis` (`rw/root_worker_journal.py:37-38`) | none |
| 4. Genesis (exact JSON, DATA) | the expected descriptor, plan and key digests | `:39-53`; v2 adds `prior_custody` (R4-38) | v2 keyset |
| 5. Descriptor's `paths.authority_root` | the issuer key | the fixed path `authority/issuer/state/issuer-key.bin` under it, whose digest must equal the genesis's (`:50-53`; NF4-6) | none |
| 6. Plan and descriptor | the journal file | the path must be in `provisioned_state` (`:54-55`); file identity pinned while open (`:69-77`) | none |
| 7. Chain | the current head | the last event of the verified chain, MAC-checked (`:99-113`) | v2: the state rows must equal the native fold (V4-J.3) |

**Premises.** The chain above establishes consistency, not authenticity. Authenticity rests on four premises, which are stated, not proved. Each stays OPEN with the OS and installation workstream (OB-030 class) and the operator's provisioning (OP-1):
- **P-A1 (installed integrity).** The descriptor, plan, genesis, key and journal at their installed paths are the operator-provisioned objects, and no principal other than root can write them (the `protected` owner and mode checks). A compromised root is out of scope.
- **P-A2 (key secrecy).** Only the owner processes (front, worker, provisioner) read the key. Any process that holds it can write valid custody events, so a compromise of the front or the worker is out of scope. The key's lifetime and zeroization stay OPEN.
- **P-A3 (one provisioning).** The genesis, key and empty journal were created once, by the operator-run provisioner. First-start authentication (V4-J.3) checks their mutual consistency and emptiness; it cannot tell a re-provisioned set from the original.
- **P-A4 (currentness).** The journal presented is the latest committed one, within the limits of V4-C.2.

**Native and producer correspondence.** The Python producer `RootCustodyJournal` selects and reads every object (links 1–7). It passes the key bytes, the genesis bytes, each event's archived base bytes (`rw/root_worker_codec.py:19-28`, over `rw/operation_capture.py:15-39`) and the head row to the native `Custody_Chain_Valid` (S2H) in a private arena. The native unit recomputes the digests with `Attest.SHA256` and the MACs with `Hmac_Sha256`, recognizes the archive grammar far enough to check that each row's `previous`, `operation` and `kind` columns equal the archived fields, and folds `Next` over the events (V4-F). It establishes chain integrity relative to the key it is given. It does not select the key, the genesis or the journal; those remain producer work under P-A1 … P-A4 (R4-22).

### V4-C.2 Anti-rollback: what is detected and what is not

**Detected:**
- a journal file replaced while open (identity pinned, `rw/root_worker_journal.py:69-77`);
- an event or head edited, inserted or removed without the key (`:99-113`);
- **(v4) a custody journal restored alone** to an older valid state. After each `HANDOFF_INTENT`, `CUSTODY_ACK`, `CLOSED_WITNESS` and `FRONT_RECONSTRUCTION` commit, the same owner appends an observation event `CUSTODY_REFERENCE` carrying that event id to the scoped observation journal under the root reservation (`ScopedObservationJournal`, `rw/protected_scoped_resource_runtime.py:70`). At startup the reconciler requires every recorded id to be in the loaded chain, and every operation-journal head that a custody frame binds (v2 §6.4's seed) to be in the operation journal's history. A mismatch is RT-14: a named refusal, never a re-genesis. A crash between the two appends leaves an event without its reference, which the check tolerates; it never accepts a reference without its event.

**Not detected (non-claims):**
- a coordinated restore of every journal and the store to an earlier consistent snapshot;
- any action by a holder of the key (P-A2);
- a rollback before the first cross-reference exists.

An external monotonic witness, such as a hardware counter or an off-host log, would detect the first of these. None is proposed: choosing one would be an installation decision and a new provider prerequisite.

### V4-C.3 Both JSON forms, natively, with number canonicality

| | Form UTF8 | Form ASCII |
|---|---|---|
| Encoder | `json.dumps (sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)`, UTF-8 (`rw/protected_startup.py:35-37`) | the same with `ensure_ascii=True`, ASCII (`rw/protected_resource_runtime.py:20`) |
| Python check | `exact_json`: duplicate keys refused, non-finite constants refused, raw equal to the encoding or the encoding plus one LF (`rw/protected_startup.py:40-51`) | `exact`: raw equal to the encoding of the parsed value, no LF (`rw/protected_resource_runtime.py:22-23`) |
| Containers | descriptor, startup genesis, custody genesis, owner plan, crosswalk | run-scoped config |
| Strings | `"` and `\` as `\"` and `\\`; U+0008, U+000C, U+000A, U+000D, U+0009 as `\b`, `\f`, `\n`, `\r`, `\t`; other controls below U+0020 as `\u00XX`; every other character as its raw UTF-8 bytes. A lone surrogate cannot appear, because UTF-8 encoding refuses it. | the same escapes; every character above U+007F as `\uXXXX`, a non-BMP character as a surrogate pair, a lone surrogate as its own `\uXXXX` |
| Numbers | `Number_Canonical` (below) | `Number_Canonical` |

All of these are **[unverified reasoning, RC-4]** for the installed CPython encoder, including the hex-digit case.

**`Number_Canonical (Lexeme)`** (S2; native; statement, to prove). It holds exactly when the encoder renders the value that the decoder reads from `Lexeme` as `Lexeme` itself:
- **an integer lexeme** (no `.`, `e` or `E`) holds iff it is an optional `-` followed by `0` or by a non-zero digit and further digits, and is not `-0` (Python reads `-0` as the integer zero and writes `0`);
- **any other lexeme** holds iff `Lexeme = Repr (Round (Decimal_Value (Lexeme)))`, where `Decimal_Value` is the exact rational value of the decimal lexeme (big integers); `Round` is round-to-nearest-even into IEEE binary64, and the lexeme fails when the result is not finite (the encoder refuses non-finite values); and `Repr` is CPython's `float.__repr__`: the shortest decimal digit string that rounds back to the same binary64 value, laid out in fixed or exponent notation by CPython's own thresholds and formatting rules **[unverified reasoning, RC-5]**.

`Number_Canonical` makes the native recognizer refuse exactly the number lexemes that the Python check refuses, so number canonicality no longer rests on Python alone (R4-21).

**Domain, depth and cost.**
- The recognizer, `Path_Value` and `Extract` are total over every byte string the private arena holds. They impose no depth or length cap: nesting uses an explicit stack in the arena, bounded only by the input length. Python's own recursion limit refuses some deep containers; the native side accepts every container the Python check accepts and adds no refusal of its own.
- Keys are compared by decoded code-point sequence. `Path_Value` resolves object keys and array indices by structural scan, with a `Subprogram_Variant` on the remaining length.
- **Native cost (OPEN, D2 class).** Structure and strings are linear in the container length. `Number_Canonical` adds big-integer work per non-integer lexeme, which grows with its digit count. No cost bound is claimed.

### V4-C.4 P3: one definition, in every place

**Scope.** The exe and every file-backed mapping, meaning every `/proc/<pid>/maps` line whose pathname begins with `/`, whatever its permissions. This is exactly the set the original capture checks: the exe against roles INTERPRETER and EXECUTABLE, and every such mapping against INTERPRETER, EXECUTABLE, EXTENSION and DATA (`rw/root_worker_process_capture.py:69-74`; NF4-4). The original executed-source target is kept unchanged: those role checks, and the before/after equality of `maps`, `cgroup` and `cmdline` (`:75-88`).

**Relation `Process_Images_Covered (Images, Lease)`** (native subset relation): every image is a lease entry with the role the original requires for it and an equal sha256, and its (dev, ino) equals the identity of the file hashed **[unverified reasoning, K-19]**.

**Non-claims, identical in R4-3, R4-23, this section and `seams.json`:**
- **NC-P3-1.** SOURCE-role files are read, not mapped. Their identity rests on the P2 loader lease alone.
- **NC-P3-2.** Anonymous executable memory (JIT, `ctypes`) is not covered.
- **NC-P3-3.** Mappings created and removed outside the capture interval are not covered; the capture is a point-in-time snapshot with before/after equality.
- **NC-P3-4.** The relation does not establish that the process runs only those images, or what their code computes.

### V4-C.5 Crosswalk: typed native decode and correspondence (02.3)

| Field (v3 V-C.6) | Native type | Decode | Join | Python caller that must use the decoded value |
|---|---|---|---|---|
| `schema`, `installation` | string | `Extract` | equal to the constant and to the descriptor's `installation_id` | the loader |
| `policy_sha256`, `catalogue_sha256` | 64 lowercase hex | `Extract` | `Roster_Join` kinds `Policy` and `Run_Config` (v3 V-C.3) | the loader |
| `entries[i].kind`, `name`, `right` | enumeration, string, string or null | `Extract` | `Entry_For` unique per (kind, name, right) | `pre_effect`, `launch_root_worker`, `resource_launch_material`, `machine_admission` |
| `plan_sha256` | hex | `Extract` | `Plan_Join` against the policy's plan value span | the same four |
| `cost_key` | string | `Extract` | `Cost_Join`: equal to the plan's `cost_key`; the catalogue's `costs[cost_key]` kind and amount equal the reservation's | `_reserve`, `machine_admission` |
| `coordinator` | object | `Extract` (canonical object) | P5 pair (v3 V-C.4) | the root launch (`rw/root_worker_plan.py:13-38`) |
| `helper_image_sha256` | hex | `Extract` | P4 and P10 pairs | the root launch; the sub-helper (V4-E) |
| `child_plans[j]` | (task kind, hex) | `Extract` | the child plan of `TASK_INTENT` (V4-E.1) | the dispatcher |
| `delegation_record_sha256` | hex or null | `Extract` | `Selected` of `Custody_V2` (C2-51) | the V2 producer |
| `physical_key` | three strings | `Extract` | the projection key (V4-B.2) | the scoped producer |
| `header_data[k]` | (path, hex) | `Extract` | `Roster_Join` for header DATA | the loader |

Each caller reads the crosswalk only through the native decode, never by its own JSON parse. Native cost stays OPEN.

---

## V4-D. Full-domain accounting comparison (V3-REQ-D; 02.4, 06.2; D-4a)

v3 V-D (C3-VD, with R4-24 and R4-25) is carried: the withdrawals, the per-class correspondence and E1–E4. E3 stays a sample taken at DISPATCH and GO; it asserts nothing about future capacity, and sampling is never counted as protection.

### V4-D.1 Obligations every option is measured against

| Id | Obligation | Source |
|---|---|---|
| AO-1 | Each request holds its own grant and use; no request borrows the first root's grant | D-4a evidence; C2-91 AM-1, AM-2 |
| AO-2 | Kind (`Held_Capacity` or `Irreversible_Budget`) and amount are the catalogue's `costs[cost_key]` for the request's own plan, for every amount, with no cap | `Cost_Join` (V4-C.5); `rw/protected_scoped_resource_runtime.py:374-381` |
| AO-3 | Owner and requester bind to the request (C3) | C2-31 |
| AO-4 | The request's own row meets the native scope and universe guards (rollover) | V4-B.6 |
| AO-5 | **Immutable outer reservation bound:** no admitted outer bound is ever raised or reassigned | D-5a evidence; P-CE1, P-CE3 (C2-53) |
| AO-6 | Each request's own limits are physically enforced (E1, E2, E4) | v3 V-D.3 |
| AO-7 | No double counting in the withholding or the admission sample | `rw/protected_scoped_resource_runtime.py:655-658` |
| AO-8 | Future capacity is protected against interference only by a selected and measured mechanism (P-M1, P-M2, P-D1); otherwise no claim | v3 V-D.2 |
| AO-9 | Response progress (V4-L) | V3-REQ-L |
| AO-10 | Native cost: decisions and processes per request | D2 class |
| AO-11 | No new cap, provider prerequisite, borrowing or accepted native failure | D-4a ruling |

### V4-D.2 Matrix (no option is selected)

✓ meets the obligation at design level; ✗ fails it; "part" meets it only in part, as stated.

| Option | AO-1 | AO-2 | AO-3 | AO-4 | AO-5 | AO-6 | AO-7 | AO-8 | AO-9 | AO-10 | AO-11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A: contained child hold under the root (C2-92) | ✗ the child row's parent is the root reservation, so it draws on the root's grant | ✓ ledger | ✓ | ✓ child Reserve guard | ✓ | part: one root bound covers every child | ✓ | none | good | low: `Task_Admission` and `Check` per child | ✗ (borrowing) |
| B: ownership handoff between requests (C2-92) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ each request on its original route | ✓ | none | poor: a request waits for the detached job | as original | ✓ |
| C: nested units under the delegated subtree, handler in the coordinator (C2-92) | ✓ ledger | ✓ | ✓ | ✓ | ✗ unless the root bound is raised; sizing the root for nested demand instead is a cap and a borrowing | part: handler work is unmetered per request | ✗ the root counter includes descendants | per nested unit, only with P-M1 | good | moderate | ✗ |
| E: ledger-only hold, handler in the coordinator (C2-92) | ✓ ledger | ✓ | ✓ | ✓ | ✓ | ✗ in-process work shares the root's limits | ✓ | none | good | low | ✗ the root limit can kill admitted work (an accepted native failure) |
| F, as stated in v3: per-request nested unit, root bound raised by the nested reservations | ✓ | ✓ | ✓ | ✓ | **✗ raises an admitted bound** | ✓ | ✓ | per request, only with P-M1 | good | higher: a process per request | ✗ needs a bound-changing policy |
| F′: F with the root's bound left immutable | ✗ nested units draw on the root's admitted capacity | ✓ | ✓ | ✓ | ✓ | part | ✗ descendants count in the root | — | good | higher | ✗ (borrowing) |
| G (new): a sibling top-level unit per request, outside the root's cgroup, launched by a helper command with the original launch properties (`rw/protected_root_resource.py:68-71`; `rw/protected_scoped_resource_runtime.py:760-762`) for that request's own reservation; the request's handler code stays in the coordinator | ✓ | ✓ | ✓ | ✓ its own Reserve, Launch_Intent and Running | ✓ each unit's bound is set once at launch | part: workload units are enforced by their own bounds; handler code in the coordinator shares the root's limits, as in E | ✓ siblings are outside the root's counter | per unit, only with P-M1 | good | higher: a unit and a V3-pattern helper per request, as on the original serial route | part: adds one helper command (`LAUNCH_SIBLING`, designed only if G is selected) and no cap or prerequisite, but handler code keeps E's risk of being killed by the root limit |

**Result.** No option meets every obligation at design level. A fails AO-1 and AO-11; B fails AO-9; C fails AO-5 or AO-11, and AO-7; E fails AO-6 and AO-11; F fails AO-5 and AO-11; F′ fails AO-1, AO-7 and AO-11; G leaves E's gaps for handler code in the coordinator (AO-6 and AO-11, part). Metering each request's handler code separately would need per-request store access, which conflicts with single-writer custody unless store custody itself moves per request, which is B. That trade-off is the decision the operator holds under D-4a.

**F and the immutable bound.** F as stated raises the root's admitted outer bound. The preserved immutable outer reservation bound forbids that, and no decision grants it. `SET_ROOT_CEILING` is withdrawn (R4-28), and F is not a candidate as stated (R4-24).

**No selection.** No option, mechanism, cap, prerequisite or policy field is selected or added. Any authoritative choice is the operator's under D-4a (OP-3). Until one exists, later consequential requests are served by the routing of C2-93 as amended (V4-I.5, V4-L), and their accepted cases stay OPEN.

---

## V4-E. Child relation, surfaces, COMMIT_CHILD and retained authority (V3-REQ-E; 03.2; D-5a, D-5b)

v3 V-E (C3-VE, with R4-26 … R4-28, R4-54 and R4-59 … R4-64) is carried. The E-table now records Launch_Intent before dispatch, Running after HELD and GO with machine admission, as the original launch does (NF4-12).

### V4-E.1 `Child_Event_Legal` (native relation; spec S12)

Events are scoped observation-journal events under the child reservation (v3 V-E.1), plus the child row's scoped commits. Each event requires the root generation g to be WORKER_OWNED in its `CUSTODY_ACK` generation with the worker as owner (M2, V4-F.5), and requires the listed predecessor for the same task t.

| Event (step) | Predecessor | Writer | Native decision at this step | Command after durable commit |
|---|---|---|---|---|
| `TASK_INTENT` (E1) | none for t | worker | — | — |
| child Reserve commit (E2) | `TASK_INTENT` | worker | `Task_Admission` / `Task_Admission_V2` | — |
| child `Record_Launch_Intent` commit (E3) | E2 | worker | `Check_V2` with the scope and universe guard | — |
| `CHILD_DISPATCH_INTENT` (E3) | E3 commit | worker | — | `CREATE_CHILD` |
| `CHILD_HELD` (E5) | `CHILD_DISPATCH_INTENT` | worker, from the sub-helper's frame | ticket echo equality (P11) | — |
| child `Record_Running` commit (E6) | `CHILD_HELD` | worker | `Check_V2`: Live | — |
| `CHILD_GO_INTENT` (E7) | E6 commit | worker | machine admission | `GO_FORK` |
| `CHILD_MEASURED` (E8) | `CHILD_GO_INTENT` | worker, from the relayed frame | — | — |
| `CHILD_READY` (E10) **or** `CHILD_ABORT` | `CHILD_MEASURED` | worker | `Decide` / `Decide_V2` (E9) | `COMMIT_CHILD` or `ABORT_CHILD` |
| `ACTOR_STDIN_*` (E11) | `CHILD_READY` | worker | — | — |
| `CHILD_CLOSED` (E12) | `CHILD_DISPATCH_INTENT` or later | worker, from the sub-helper's `CLOSED_CHILD … ECHILD` frame | — | — |
| child `Record_Terminal` and release or charge | `CHILD_CLOSED` | worker or collector | `Check_V2`: Reaped | — |
| `CHILD_UNKNOWN (cause)` | any event from `CHILD_DISPATCH_INTENT` on | current owner | — | holds retained |

- **Exclusive pair.** `CHILD_READY` and `CHILD_ABORT` form the alternative set `CHILD (t)`; exactly one commits.
- **Failures.** Before E7 the sub-helper kills init on channel loss, as the V1 helper does (`native_root_worker_supervisor_v1.c:352-353`). Without a `CLOSED_CHILD … ECHILD` frame the child row cannot classify `Reaped` (`core/resource_observation_classification.ads:108-114`), so it is `Unknown` with holds retained, exactly as for a root (V4-B.6, W3). After `CHILD_ABORT` the actor never execs.
- **Root settlement** waits for every child (CD-9). An unknown child keeps the root held.

### V4-E.2 Exact surfaces of every process

| Process | Launched by | argv | env | cwd and credentials | Descriptors at exec (everything else `CLOEXEC`) |
|---|---|---|---|---|---|
| Root helper successor (`native_root_worker_supervisor_v2`, D-5b) | the original root launch (`rw/protected_root_resource.py:67-71`) | the V1 helper's: endpoint, ticket, uid, gid, cwd, `--env` triples, `--`, the coordinator argv (`native_root_worker_supervisor_v1.c:307-322`) | as V1 | as V1 | as V1 (the unit's standard streams) |
| Coordinator (worker) | forked by the root helper's namespace init after GO; it execs only after the native commit (the V1 order) | plan-v1's `handler_plan` argv (`rw/root_worker_plan.py:32-34`), then the custody-channel descriptor number (V1, `native_root_worker_supervisor_v1.c:289-290`), then (v2) the helper-command-channel descriptor number | cleared; plan-v1's `environment` is empty (`rw/root_worker_plan.py:37`) | `paths.state` (`:36`); euid 0 with the reduced capability set of V4-E.4 | 0 stdin pipe read end; 1 and 2 output pipe write ends; the custody channel; (v2) the command channel |
| Sub-helper (one per child) | a fork of the root helper, outside the coordinator's namespaces; no exec | — | — | root, outside the coordinator's namespaces | holds: the child init pidfd, the go and report pipes, the actor's credential socketpair end, and a socketpair with the root helper, which routes commands and frames by ticket |
| Child init | the sub-helper, after `unshare (CLONE_NEWPID)` | — (fork) | — | PID 1 of the child namespace; private mount namespace with its own proc (the V3 pattern, `native_namespace_supervisor_v3.c:277-290`) | the go, report and stdio pipes |
| Actor | child init, after GO and the commit | the original workload argv from `TASK_INTENT`'s capture, exactly as the V3 actor helper execs it (`native_namespace_supervisor_v3.c:305`) | cleared, then the captured `--env` triples (`:302-304`) | the captured cwd (`:302`); dropped to the workload uid and gid, never 0 (`:300`, `:336`) | exactly 0 (stdin pipe read end), 1 and 2 (output pipe write ends) (`:297-299`) |

**Stdin and EOF.** The only write end of the actor's stdin belongs to the custody owner, which writes the original payload exactly once through the original pump (v3 V-E.1 E11). EOF reaches the actor when the last write description closes (V4-H.5). The helper and init close their copies before GO (`native_namespace_supervisor_v3.c:350`, `:359`), as V1 does (`native_root_worker_supervisor_v1.c:339`, `:348`).

### V4-E.3 COMMIT_CHILD: enforcement, ticket, decision and ancestry bindings

- **Ticket.** `ticket = SHA-256 (canonical ({row, task, generation, launch_head}))`, where the row is the child row's DTO after `Record_Launch_Intent` and `launch_head` is the scoped journal head after that commit. This is the original root ticket's construction (`rw/protected_root_resource.py:65-66`) applied to the child. It is journaled in `CHILD_DISPATCH_INTENT` before `CREATE_CHILD`, echoed in `HELD_CHILD` and `CLOSED_CHILD`, and checked natively as P11.
- **Measurement binding.** The sub-helper keeps the actor's credential socketpair end. It receives the frame with `SO_PASSCRED`, keeps its exact bytes and relays a copy to the worker (E8). `COMMIT_CHILD` carries the complete decision material, and the sub-helper requires the actor-observation part to be byte-equal to the frame it received.
- **Ancestry binding.** The sub-helper requires the material's process and namespace ancestry to equal what it observed itself: the init pid and namespace identity it created, the leaf cgroup the helper created, and the actor's host pid read from its own view **[unverified reasoning, K-4]**.
- **Decision.** The sub-helper calls the native `Decide` or `Decide_V2` export of the same reviewed library, with version and layout checked as every wrapper checks them, over the bound material. Only `Child_Ready_Conjunction` sends the commit ACK. Anything else, or any binding mismatch, kills init before the actor execs, and the worker commits `CHILD_ABORT` with the cause.
- **Agreement.** The worker decides first (E9) and journals the decision in `CHILD_READY`. A disagreement between the two decisions is `CHILD_ABORT` with an UNKNOWN cause; it never sends the ACK.
- **Non-claim.** The ledger-state parts of the material (rows, frames, current packet) come from the custody owner's store. A compromised coordinator could misstate them; it already holds the store (v3 V-E.3 non-claims). The C bodies are unproved native code with cost obligations (OB-048 class).

### V4-E.4 Retained authority of the euid-0 coordinator, exhaustively

v3 V-E.3's table (descriptors, mount view, systemd and D-Bus, capabilities) is carried; this inventory makes it exhaustive. **Rule:** an item is dropped only when RC-6 (V4-N), the inventory of the original handler paths' privileged operations, shows the original handler does not use it. An item the original handler uses is kept with its justification rather than refusing an original accepted case.

| Category | Item | Kept or dropped | Justification and mechanism | Evidence |
|---|---|---|---|---|
| Identity | euid 0 | kept | `Controller_Valid` requires it (v2 §5.3) | — |
| Capabilities | `CAP_CHOWN`, `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH`, `CAP_FOWNER`, `CAP_FSETID` | kept, pending RC-6 | the store's and registered roots' file operations as the original handler performs them | RC-6 |
| | `CAP_SYS_PTRACE` | kept | procfs reads of other uids, `kcmp` (V-H.2 H4); the `ptrace` and `process_vm_*` syscalls are denied by seccomp | K-5, K-20 |
| | `CAP_KILL`, `CAP_SETUID`, `CAP_SETGID`, `CAP_SETPCAP`, `CAP_SETFCAP` | dropped | signals go through helper commands; credential changes happen in the helper | K-20 |
| | `CAP_SYS_ADMIN`, `CAP_SYS_MODULE`, `CAP_SYS_RAWIO`, `CAP_SYS_BOOT`, `CAP_SYS_TIME`, `CAP_SYS_CHROOT`, `CAP_SYS_PACCT`, `CAP_SYS_TTY_CONFIG`, `CAP_SYS_RESOURCE`, `CAP_SYS_NICE`, `CAP_MKNOD`, `CAP_LINUX_IMMUTABLE`, `CAP_LEASE` | dropped, pending RC-6 | P-CE1; no mount, module, raw I/O, clock or device control | K-10, K-20, RC-6 |
| | `CAP_NET_ADMIN`, `CAP_NET_RAW`, `CAP_NET_BIND_SERVICE`, `CAP_NET_BROADCAST` | dropped | no network control | K-20 |
| | `CAP_IPC_LOCK`, `CAP_IPC_OWNER` | dropped, pending RC-6 | no locked memory beyond limits; no IPC owner override | K-20, RC-6 |
| | `CAP_AUDIT_WRITE`, `CAP_AUDIT_CONTROL`, `CAP_AUDIT_READ`, `CAP_MAC_OVERRIDE`, `CAP_MAC_ADMIN`, `CAP_SYSLOG`, `CAP_WAKE_ALARM`, `CAP_BLOCK_SUSPEND`, `CAP_PERFMON`, `CAP_BPF`, `CAP_CHECKPOINT_RESTORE` | dropped | none is a handler need | K-20 |
| Privilege flags | `no_new_privs` | set | no gain through exec | K-20 |
| Descriptors | the custody roster (v3 V-E.3 rows); the custody and command channels; transferred client sockets (after intake); transferred slot descriptors (after `DRAIN_INTAKE`); SQLite connections it opens inside the writable view; the mapped native library (read and execute) | kept | custody (V4-F, V4-H, V4-I) | K-5, K-6 |
| | the host procfs directory descriptor | replaced | a read-only procfs view (M-2; NF-1) | K-18 |
| Writable views | read-only bind of `/`; writable: the descriptor's `provisioned_state` directories, the spool directories, and registered roots exactly where and when the original handler writes them | M-1 | RC-6 | K-10, K-17 |
| | `/tmp`, `/dev/shm` | private empty tmpfs | no shared temporary space | K-10 |
| | `/proc/sys`, `/proc/sysrq-trigger`, `/sys`, `/sys/fs/cgroup` | read-only | P-CE1 | K-10 |
| IPC | AF_UNIX path sockets | kept inside the mount view only | `/run` is an empty tmpfs except binds RC-6 shows are needed; `/run/systemd` and `/run/dbus` are absent (M-1, M-4) | K-17 |
| | AF_UNIX abstract sockets, IP networking | separated when RC-6 allows | they live in the network namespace, which V1 does not separate (`native_root_worker_supervisor_v1.c:257`, `:336`). **M-6:** a separate network namespace when RC-6 shows the handler needs no network; otherwise abstract-socket reachability remains a measured gap (K-17), never a silent claim | K-17, RC-6 |
| | SysV IPC and POSIX message queues | separated, unless RC-6 shows use | **M-7:** a separate IPC namespace | K-10 |
| | signals | restricted | `kill` can name only processes visible in its own PID namespace **[unverified reasoning, K-23]**; `pidfd_send_signal` denied (M-3) | K-21, K-23 |
| | keyrings | denied, unless RC-6 shows use | `add_key`, `keyctl`, `request_key` in the seccomp list | K-20 |
| Devices | `/dev` | a minimal set: `null`, `zero`, `full`, `random`, `urandom` | `CAP_MKNOD` dropped | K-10 |
| Control paths | systemd and D-Bus | unreachable | hidden from the mount view (M-1); manager operations only through helper commands (M-4) | K-17 |
| | cgroupfs | read-only | P-CE1; every cgroup write is the helper's | K-8, K-9 |
| | seccomp deny list (M-3) | denied | `mount`, `umount2`, `pivot_root`, `move_mount`, `open_tree`, `fsopen`, `fsconfig`, `fsmount`, `unshare`, `setns`, namespace-creating `clone` flags, `ptrace`, `process_vm_readv`, `process_vm_writev`, `pidfd_send_signal`, `bpf`, `perf_event_open`, `init_module`, `finit_module`, `delete_module`, `kexec_load`, `kexec_file_load`, `reboot`, `swapon`, `swapoff`, `acct`, `quotactl`, `iopl`, `ioperm`, `settimeofday`, `clock_settime`, `adjtimex`, `open_by_handle_at` (which `CAP_DAC_READ_SEARCH` would otherwise let reach outside the mount view), `userfaultfd`, `io_uring_setup` | K-20, K-21 |

**Retained obligations.** The original coordinator and actor containment predicates (`Process_Ancestry`, `Namespace_Ancestry`, `Parent_Supports` with `Cgroup_Inside`) still decide every child natively (M-5). The immutable outer ceilings stay (P-CE1, P-CE3, AO-5). Every K item and RC-6 stays unperformed. Installation and privileged execution remain operator work (D-5a, D-5b; OP-4, OP-5).

---

## V4-F. The complete native custody relation (V3-REQ-F; 04.1, 04.3, 07.1; D-9a)

Carried: the product state and O mapping (C3-VF1: v3 V-F.1, V-F.2 and the O×U table of V-F.3) and the DDL (C3-VF5 with R4-29). The root phase graph is C2-62 with R3-10 … R3-13 and R4-47. Superseded: v3's C×P rules, mutation table and CAS section.

### V4-F.1 Types (additive SPARK unit `Worldline.Root_Custody_Phase`, spec S9; DESIGN)

```ada
type Actor            is (Front, Worker, Collector, Reconciler);
type Owner            is (Front, Worker, Collector, Reconciler, None);
type Root_Phase       is (Front_Owned, Prepared, Held, Running, Execution_Native, Execution_Ack,
                          Handoff_Intent, Front_Close_Intent, Front_Closed, Transfer_Sent,
                          Roster_Evidence, Worker_Owned, Original_Result, Handler_Terminal,
                          Worker_Relinquish, Abandoned, Front_Retained_Escrow, Collecting,
                          Closed_Witness, Physical_Settled, Historical_Settlement,
                          Front_Reconstruction, Unknown);
type Subject_Kind     is (Root, Request, Descriptor);
type Request_Phase    is (Queued, Transfer_Intent, Intake, Abandoned, Responded);
type Descriptor_Phase is (Front_Held, Stop_Intent, Frozen, Ofd_Evidence, Intake, Abandoned,
                          Released, Reclaimed);
type Transfer_Mode    is (Fresh, Relay);
type Event_Kind       is (...);  -- exactly the DDL list of v3 V-F.5 with R4-29
type Mutation         is (M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11);
type Root_State is record
   Generation    : Q.Quantity;          -- arbitrary precision; no new bound
   Operation     : L.Identity;
   Phase         : Root_Phase;
   Before_Unknown: Root_Phase;          -- the phase UNKNOWN interrupted
   Owner         : Owner;
   NS, Outer, Raw: Boolean;             -- closure flags
   Stop_Intent   : Boolean;             -- a ROOT_STOP_INTENT is recorded (M8)
   Unknown_Cause : L.Identity;          -- zero-length when absent
   Head          : L.Identity;
end record;
type Subject_State is record
   Kind          : Subject_Kind;        -- Request or Descriptor
   Subject       : L.Identity;
   Subgeneration : Q.Quantity;
   Request       : Request_Phase;       -- meaningful when Kind = Request
   Descriptor    : Descriptor_Phase;    -- meaningful when Kind = Descriptor
   Mode          : Transfer_Mode;
   Position      : Q.Optional_Quantity; -- P or W
   Head          : L.Identity;
end record;
type Event is record
   Kind; Generation; Operation; Subject_Kind; Subject; Subgeneration; Actor;
   Evidence      : Evidence_Spans;      -- the native inputs of the transition's row
   Record_Digest : L.Identity;
end record;
function Legal_Reference (Data; S : State; E : Event) return Status with Ghost;
function Legal (Data; S : State; E : Event) return Status
  with Global => null, Always_Terminates, Post => Legal'Result = Legal_Reference (Data, S, E);
function Next (Data; S : State; E : Event) return State
  with Global => null, Pre => Legal (Data, S, E) = Ready;
function Mutation_Allowed (Data; S : State; A : Actor; M : Mutation; Subject : L.Identity) return Boolean
  with Global => null, Always_Terminates;
```

`Status` is `Ready` or a named refusal (`Wrong_Generation`, `Wrong_Actor`, `Illegal_Root_Transition`, `Illegal_Subject_Transition`, `Alternative_Taken`, `Evidence_Missing`, `Join_Not_Ready`, `Subject_Unknown`). A refused actor does not act.

### V4-F.2 `Legal_Reference`: every transition

**Root subject.** Exactly C2-62's table, with R3-10 … R3-13 and R4-47, and these rows:

| From | Event | To | Actor | Native evidence |
|---|---|---|---|---|
| any phase with a launched unit (HELD … WORKER_RELINQUISH, FRONT_RETAINED_ESCROW, UNKNOWN) | `ROOT_STOP_INTENT` | unchanged; `Stop_Intent` set | the M8 actor (V4-F.5) | the authorizing request or failure record |
| any non-terminal phase | `UNKNOWN (cause)` | UNKNOWN; `Before_Unknown` set | the phase owner or the Reconciler | the cause record |
| UNKNOWN | `RECONCILED`, recording the redecision, then the event that native evidence determines | that event's target | the Reconciler only (INV-C5) | authentic durable evidence; never EOF or a deadline alone |
| FRONT_RECONSTRUCTION (g) | `FRONT_OWNED (g+1)` | FRONT_OWNED, generation g+1 | Front | the fresh front binds (C2-62) |
| no row (initial state) | `PREPARED` (g = 1) | PREPARED (1) | Front | the operation's RESERVED and `EFFECT_INTENT` heads |

**Request subjects** (alternative set `REQUEST (g, r, s)`):

| From | Event | To | Actor | Native evidence |
|---|---|---|---|---|
| no row | `REQUEST_QUEUED (r, 0)` | Queued | Front | the raw request and its original observation; any root phase in which the front does not serve the request itself (FRONT_CLOSE_INTENT onwards, UNKNOWN included), or carried from generation g−1 (`carried_from`). A request is queued durably before any transfer |
| Queued or Abandoned | `REQUEST_TRANSFER_INTENT (r, s, mode)` | Transfer_Intent | Front | root phase WORKER_OWNED or ORIGINAL_RESULT (C2-62) with owner Worker; for FRESH the socket roster, for RELAY the live relay channel; s is 0 from Queued and s+1 from Abandoned |
| Transfer_Intent | `REQUEST_INTAKE (r, s)` | Intake | Worker | `Transfer_Join` (FRESH) or `Relay_Join` (RELAY) = Ready over the authenticated `REQUEST_TRANSFER_INTENT (r, s)` head (V4-I.1) |
| Transfer_Intent | `REQUEST_ABANDON (r, s)` | Abandoned | Front or Reconciler | no `REQUEST_INTAKE (r, s)` in the chain |
| Intake | `REQUEST_RESPONDED (r, s)` | Responded | Worker | the response digest; for RELAY the front writes those exact bytes afterwards (M5) |
| Queued (generation g+1, FRONT_OWNED) | `REQUEST_RESPONDED (r, 0)` | Responded | Front | served under the original gate |

**Descriptor subjects** (alternative set `DRAIN (g, d, s)`):

| From | Event | To | Actor | Native evidence |
|---|---|---|---|---|
| no row, or Front_Held | `DRAIN_STOP_INTENT (d, s)` | Stop_Intent | Front | root phase WORKER_OWNED with owner Worker; d in the front's LIVE roster; the open armed interval (V4-H) |
| Stop_Intent | `DRAIN_FREEZE (d, s)` | Frozen | Front | spool fsync and `DISARMED (P)`, or durable W with the write interval closed |
| Frozen | `DRAIN_OFD_EVIDENCE (d, s)` | Ofd_Evidence | Front | `kcmp` and lock-held evidence after SEND (V-H.2 H4) |
| Ofd_Evidence | `DRAIN_INTAKE (d, s)` | Intake | Worker | the evidence matches the worker's report |
| Stop_Intent, Frozen or Ofd_Evidence | `DRAIN_ABANDON (d, s)` | Front_Held, sub-generation s+1 | Front or Reconciler | no `DRAIN_INTAKE (d, s)` in the chain |
| Intake | `DRAIN_RELEASED (d, s)` | Released | Front | the front closed its active copy (V4-H.5) |
| Intake or Released | `DRAIN_RECLAIMED (d, s)` | Reclaimed | Collector or Reconciler | the worker pidfd terminal, with custody returning (V4-H.4) |

### V4-F.3 C×P rules (replace v3's r1 … r5)

- **r1.** While the root phase is FRONT_*, any P phase is legal for non-root rows. The root row is RESERVED or LAUNCH_INTENT before HELD, and RUNNING from RUNNING onwards.
- **r2.** While the root is WORKER_OWNED … WORKER_RELINQUISH, the root row is RUNNING or TERMINATING, and child rows follow `Parent_Supports`.
- **r3′.** Before CLOSED_WITNESS, a root row that is possibly launched (a present `Dispatch` fact) is never RELEASED or CHARGED. A row whose launch journal is `Never_Dispatched` and whose native class is `Never_Launched` may be released by the original `Release_Hold` (PR-a; INV-C4′, R4-47).
- **r4.** While the root is UNKNOWN, rows are retained or SETTLEMENT_UNKNOWN, never released. A stop under M8 changes no row.
- **r5′.** Request and descriptor phases other than Queued and Front_Held exist only from TRANSFER_SENT (g) on. Intake requires `CUSTODY_ACK (g)`.
- **r6.** Before CLOSED_WITNESS (g), every Intake request and descriptor is Responded, Released, Reclaimed or under an UNKNOWN cause.

### V4-F.4 `Next`

`Next` applies the target phase and owner of the row, sets `Head` to the event id, increments the sub-generation on `DRAIN_ABANDON` and on a `REQUEST_TRANSFER_INTENT` from Abandoned, records `Position` from `DRAIN_FREEZE`, and creates generation g+1 at `FRONT_OWNED (g+1)`, carrying every Queued or Abandoned request into it (`REQUEST_QUEUED` with `carried_from`). The state rows of V-F.5's DDL hold exactly `Next` folded over the chain (V4-J.3).

### V4-F.5 `Mutation_Allowed`: every actual mutation

On a v1 deployment there is no custody state, and every mutation keeps its original behaviour. On a v2 deployment each mutation is gated at a single choke point:

| Id | Mutation (choke point) | Allowed when | Actor |
|---|---|---|---|
| M1 | operation-journal append (`OperationJournal.append`, `rw/protected_operations.py:230`) | the actor is the generation's owner for the store: Front in FRONT_OWNED … FRONT_CLOSE_INTENT and from ABANDON(g) on; Worker in WORKER_OWNED … WORKER_RELINQUISH of its `CUSTODY_ACK` generation; Collector, for the root operation's settlement and quarantine appends, in CLOSED_* … HISTORICAL_SETTLEMENT; Reconciler for the original startup branches before the endpoint | as stated |
| M2 | scoped-ledger commit (`ScopedRunLedgerService`, `rw/protected_scoped_resource_service.py:56`) | the M1 owner rule; the Collector only for `Record_Terminal`, `Release_Hold`, `Charge_Budget` and `Retain_Uncertain` of the generation's rows | as stated |
| M3 | store mutation (`rw/store.py` writers) | the M1 owner rule, without the Collector | Front or Worker |
| M4 | custody append (`RootCustodyJournal.append`, `rw/root_worker_journal.py:123`) | `Legal (S, E) = Ready`, with `E.Actor` the caller | per row |
| M5 | client response write | FRESH: the intaking worker, after `REQUEST_INTAKE`; RELAY: the front, after the worker's `REQUEST_RESPONDED` and only those bytes; front-served: the front | Worker or Front |
| M6 | slot read and spool | Front in Front_Held **and in Stop_Intent, spooling until FREEZE** (H1); Worker from Intake; Collector or Reconciler in Reclaimed; nobody in Frozen or Ofd_Evidence | as stated |
| M7 | stdin write | Front in Front_Held until its stop flag; Worker from Intake; nobody after a crash inside an open write-armed interval (V4-H.2) | as stated |
| M8 | unit stop or kill | (a) the current owner of the unit's slot, in the original paths: failure capture (`retain_and_stop_unknown`, `rw/protected_root_supervisor.py:346-362`; the V3 slot's `capture_owned_failure` → `stop_owned_transport`, `rw/protected_scoped_supervisor_v3.py:286-306`, `:434`) and an authorized `job.cancel` (`rw/controller.py:811-826`; NF4-8). For the root in the handoff window, only after `ABANDON (g)` (§6.6 with R4-48). The worker stops only through the helper command `STOP_UNIT` (M-4). (b) The helper's own kill of init on channel loss before GO (`native_root_worker_supervisor_v1.c:352-353`). (c) When no owner is reachable (the worker's channel is lost, or the phase is UNKNOWN): an authorized `job.cancel` naming the world whose root unit belongs to this generation, executed by the front after a durable `ROOT_STOP_INTENT`. Never on EOF, a deadline or the reconciler's own initiative. A stop never settles, releases or relabels anything. | as stated |
| M9 | helper command | Worker in WORKER_OWNED of its generation; Front in FRONT_* for its own root helper (original) | Worker or Front |
| M10 | unit reset | after CLOSED_WITNESS (C2-68) | Collector |
| M11 | escrow claim | FRONT_RECONSTRUCTION | Collector |

**Choke points, and their audit.** M1 … M4 are enforced inside the four append and commit methods, so every call site is covered without editing it. M5 … M11 each have one call site. **AU-1 (OPEN):** a static audit that every write to each database, journal and store file goes through its choke point, starting from the `grep` census of `journal.append(` call sites (AUTHOR-NOTES §2).

### V4-F.6 CAS, replay and joins (replaces v3 V-F.6)

`append (expected, proposed)` runs in one `BEGIN IMMEDIATE` with `synchronous=FULL`:
1. **Load.** `Custody_Chain_Valid` over the chain (V4-C.1), and the state rows equal to the native fold of `Next` (V4-J.3).
2. **Replay identity** is (generation, operation, **subject_kind**, subject, sub-generation, kind, record digest). An existing event with that identity is returned unchanged: no second mutation and no action. This runs before the CAS, so a caller whose acknowledgement was lost gets its own committed event back.
3. **Alternative join.** If `kind` belongs to an alternative set, the `alternatives` row keyed by (generation, operation, subject_kind, subject, sub-generation, set) must be free or hold this kind; otherwise `CUSTODY_ALTERNATIVE_TAKEN`, and the loser does not act. ACK/ABANDON, REQUEST INTAKE/ABANDON and DRAIN INTAKE/ABANDON stay exclusive.
4. **CAS join.** `root_state [generation]` and `subject_state [generation, subject_kind, subject]` must equal `expected` (head, generation, root phase, subject phase, sub-generation); otherwise `CUSTODY_CAS_STALE`, and the caller re-reads and re-decides.
5. **Generation join.** The event's generation is the current root generation, except the two events that create generation g+1 (`FRONT_OWNED (g+1)` and the carried `REQUEST_QUEUED`).
6. **Initial-state join.** With no `root_state` row, the state is the initial state (V4-J.3), and only `PREPARED (1)` is legal.
7. **Decide.** `Legal = Ready`; compute `Next`.
8. **Write.** Insert the event, the `alternatives` row and the new state rows; update the head and its MAC.
9. **Read back,** re-verify and re-decide natively (`Legal` and `Next` equal), then commit.

---

## V4-G. Release, closure, reconstruction seed and recovery routes (V3-REQ-G; 07.3, 04.4, 04.5, 12.2; D-6a)

v3 V-G (C3-VG, with R4-30 … R4-33 and R4-56) is carried: the barrier, the futures, the U decision, the NEVER_DISPATCHED split and the crash table.

### V4-G.1 Never_Launched release and the CLOSED_WITNESS floor (07.3)

r3′ (V4-F.3) and INV-C4′ (R4-47) restore the original release of a genuine never-launched row and keep the full floor for every other row:
- a row whose launch journal is `Never_Dispatched` and whose facts satisfy `Never_Holds` (no dispatch, protocol, peer, namespace, unit, cgroup or invocation; no effect; `core/resource_observation_classification.ads:96-102`) classifies `Never_Launched` and is released by the original `Release_Hold` (`core/resource_run_ledger.ads:319-320`), with no CLOSED_WITNESS. That is PR-a.
- any row with a present `Dispatch` fact is possibly launched. It is never released or charged before CLOSED_WITNESS, and a dispatch without HELD stays `Unknown` with its holds (PR-b).

### V4-G.2 The closure barrier, exactly as the original

`Physical_Closure` is the three custody events and the terminal pidfds of v3 V-G.1, with `CLOSED_OUTER` replaced by R4-30:
1. `CLOSED_NS`: the helper's `CLOSED … ECHILD` frame with the dispatch ticket and the HELD init pid, a waited status, and the namespace pidfd terminal; then the ACK `'A'` (`rw/protected_root_supervisor.py:177-207`).
2. `CLOSED_OUTER`: after `CLOSED_NS`, the helper pidfd terminal, the owned launcher's `wait ()` returned, and `MainPID = 0` (`:218-227`). Nothing about the unit's active state.
3. `CLOSED_RAW`: every raw drain complete and fsynced, with no drain error (`:251`, `:260-269`).
4. The worker, helper and namespace pidfds terminal (`rw/root_worker_closed.py:48-51`).

The unit is launched with `RemainAfterExit=yes` (`rw/protected_root_resource.py:69`), so it may still be "active (exited)" when the barrier completes. That does not matter to the barrier. The reset of C2-68 happens only after CLOSED_WITNESS, as factual cleanup, so there is no reset cycle.

### V4-G.3 Reconstruction seed independent of HANDLER_TERMINAL

| Seed part | Durable source, written before or without the worker's terminal | Used by |
|---|---|---|
| Historical root native | the `EXECUTION_NATIVE` custody event of `retain_root_native` (`rw/protected_root_observation.py:157-164`), named as `root_native` by the custody intent frame (`rw/root_worker_custody.py:125-133`; NF4-3) | the native replay `root_controller (**material) == observation` (`rw/root_worker_closed.py:53-56`) |
| Original use | the frame's `original_native_use` (`rw/root_worker_custody.py:128`) | the use join (`rw/root_worker_closed.py:59`) |
| Original request | the frame's `original_request` and the retained peer (`:127`) | `seed['provenance']['original_request']` equality (`rw/root_worker_closed.py:60`) |
| Physical closure | the front's own `CLOSED` events: namespace (`rw/protected_root_supervisor.py:203`), outer (`:225-227`), raw (`:268`) | the barrier (V4-G.2) |
| Current physical observation | a fresh `observe ()` at reconstruction (`rw/root_worker_closed.py:66-67`) | native `REAPED` and `CONSISTENT_SNAPSHOT` (`:71-77`) |

**The `_physical_native` successor** takes the seed from the frame, not from the terminal. It keeps every other check of `rw/root_worker_closed.py:44-83`: the terminal pidfds, the native replay, the packet type and operation, the request equality, the single RUNNING row, the fresh physical classification and the consistent snapshot.
- **When HANDLER_TERMINAL is present,** it must agree: its `native_event` is the frame's `root_native` event and its `original_native_use` equals the frame's. The pre-constructor correspondence is checked against its `owner_state`, as today (`:89-92`).
- **When it is absent,** the pre-constructor correspondence is recorded against the handoff seed's `owner_state` (`rw/protected_root_observation.py:110-111`) and labelled as handoff-time correspondence. No terminal-state equality is claimed.
- The escrow's precondition `owned.handler_terminal is not None` (`rw/root_worker_closed.py:26-29`) is replaced by the physical barrier (v3 V-G.2).
- U is then decided by v3 V-G.3: a retained first `RESULT_CAPTURE` settles by `recover_committed`; otherwise native `QUARANTINE_USE`, then K4.

### V4-G.4 Every automatic and owner route (adds to v3 V-G.5)

| Id | Root phase | U (operation journal) | Physical facts | Original branch | Action | Automatic or owner |
|---|---|---|---|---|---|---|
| RT-21 | any; on the root route, after the barrier | `EFFECT_OBSERVED` | — | `recover_committed` (`rw/protected_operations.py:366`) | Complete | Automatic. A refusal propagates out of startup reconciliation and is a startup refusal for owner diagnosis (NF4-10), as original |
| RT-22 | as RT-21 | `SETTLED` | — | `recover_committed` (`:366`) | Complete idempotently | as RT-21 |
| RT-23 | as RT-21 | `EFFECT_INTENT` with `FULL_BROKER_PREPARED` and any later broker progress (`NATIVE`, `WORKER_INTENT`, `WORKER_RESULT`, `CANONICAL_INTENT`, `PHYSICAL_RESULT`; `rw/canonical_full_broker.py:115-170`), no `RESULT_CAPTURE` | — | `broker.recover`, then `finish` (`rw/protected_operations.py:369-375`) | Complete | Automatic; a failure goes to `unresolved` and the owner |
| RT-24 | as RT-21 | `EFFECT_INTENT` with `STAGING_INTENT` only | — | unresolved (`:376`) | Owner, with quarantine and K4 as original | Owner |
| RT-25 | WORKER_OWNED; worker dead after `REQUEST_INTAKE (r, s)` and before `REQUEST_RESPONDED` | the worker's rows for r | worker pidfd terminal | the rows are recovered at reconstruction by RT-17 … RT-24, according to their U | FRESH: the client socket's last copy died with the worker, as a daemon crash closes it. RELAY: the front closes the client connection unanswered, the same outcome. The client's retry uses the original request-id semantics | Automatic |
| RT-26 | descriptor Released; worker dead | — | worker pidfd terminal | — | `DRAIN_RECLAIMED`. Outputs: the reconstructed front reattaches from the durable P through the escrow's retained read copy (V4-H.3), with completeness UNKNOWN if the worker's read-armed interval was open. Stdin: the worker's write copy is gone, so the actor sees EOF; W below the payload length is `STDIN_TRUNCATED` → UNKNOWN | Automatic |
| RT-27 | descriptor Intake, not yet Released; worker dead | — | worker pidfd terminal | — | `DRAIN_RECLAIMED`. The front closes its stdin write copy at once, so EOF reaches the actor, and reattaches outputs as RT-26 | Automatic |

COMMITTED stays absorbing (CD-1), and the first `RESULT_CAPTURE` stays write-once (CD-8). No route settles on EOF, a deadline or a terminal frame alone.

---

## V4-H. Read and write windows, reattachment and EOF (V3-REQ-H; 08.1, 08.2, 08.3, 08.5; D-3a)

v3 V-H.1, V-H.2 (C3-VH1, with R4-34 … R4-36) and V-H.4 (C3-VH4) are carried. v3's stdin EOF rules and failure table are superseded by V4-H.4 and V4-H.5.

### V4-H.1 Kernel read to durable spool: read-armed intervals

- **Rule.** Before its first `read` of an ownership interval, a reader appends `ARMED (d, s, owner, P)` to the descriptor's spool chain and fsyncs it. Every chunk is appended and fsynced before it is delivered (R4-35). When the reader stops (the H1 stop, FREEZE, EOF or a clean end), it appends `DISARMED (d, s, P)` after its last fsync.
- **Detection.** At recovery, a descriptor whose last spool record is `ARMED` may have lost bytes: the kernel handed them to a reader that died before the spool kept them. Its completeness is recorded `READ_GAP_POSSIBLE`, which is UNKNOWN, and no PASS rests on it. The bytes still in the pipe are read by the next owner after P.
- **Original V3 slots.** The same records bracket the interval from the slot's attach to FREEZE. A crash between the transport's kernel read and the consumer's spool append now falls inside an open interval, so it is detected and marked UNKNOWN. That is today's consequence of a V3 slot crash; the change is that it is no longer silent.
- **Limit.** A pipe keeps no record of consumed bytes, so lost bytes are detected, not recovered.

### V4-H.2 Kernel write to durable W: write-armed intervals

- **Rule.** Before its first write of an ownership interval, the stdin owner appends `WRITE_ARMED (d, s, W)` and fsyncs. After each `os.write` returns, W is updated in memory at once (`rw/protected_scoped_supervisor_v3.py:328-329`). At a stop, before FREEZE, and at completion, the owner appends `W_DONE (d, s, W)`, closing the interval.
- **Cancellation.** The stop flag is checked after each `os.write` and before any await (R4-36), so a cancellation lands where the in-memory W is exact. The owner then closes the interval cleanly.
- **Crash.** A crash inside an open interval leaves the true position between the durable W and that W plus the bytes in flight. No owner resumes such a stream: resuming could duplicate or skip bytes. EOF reaches the actor when the last write description closes (V4-H.5), and the outcome is `STDIN_POSITION_UNKNOWN`, which is UNKNOWN, never PASS.

### V4-H.3 Reattachment after a closed transport

When custody of d returns to the front (`DRAIN_ABANDON` → Front_Held at s+1, or `DRAIN_RECLAIMED`), the front:
1. checks the descriptor's identity (dev, ino, mode) against the FREEZE record, and for a reclaimed descriptor `kcmp` between its retained copy and that identity **[unverified reasoning, K-5]**;
2. verifies the spool chain to its last record;
3. starts a new reader: for an original V3 slot, `attach_output` over a fresh `os.dup` (`rw/protected_scoped_supervisor_v3.py:482-493`); for a successor slot, a raw reader;
4. appends `ARMED (d, s', front, P)` at the durable P;
5. resumes the slot's consumer from P with the spool prefix as its input, carrying any `READ_GAP_POSSIBLE` mark.

**Retained read copy.** At the handoff, the front keeps one non-reading read-end copy of every transferred output pipe in the `ClosedFrontEscrow` roster until CLOSED_WITNESS or reclaim. A read copy does not affect EOF, which depends only on write ends. Stdin write ends are never retained (V4-H.5).

### V4-H.4 Failure and restart table (replaces v3 V-H.3)

| Window | Front crashes or restarts | Worker dies | Host restarts | Cancellation, processes alive |
|---|---|---|---|---|
| A: before `DRAIN_STOP_INTENT` | as today: the front's readers die, an open `ARMED` marks `READ_GAP_POSSIBLE`, and the front's stdin write end closes (EOF; `STDIN_TRUNCATED` if W is short) | nothing was transferred | as a front crash | nothing changes |
| B: STOP_INTENT → FREEZE (front reading and spooling, M6) | `READ_GAP_POSSIBLE` if `ARMED` was open; an open `WRITE_ARMED` means no resume. The Reconciler commits `DRAIN_ABANDON`, and the restarted front reattaches from P | nothing was transferred | as a front crash | the stop completes (`DISARMED`, `W_DONE`); FREEZE follows, or the front resumes |
| C: FREEZE → SEND | P and W are durable. The Reconciler commits `DRAIN_ABANDON`; the front reattaches from P and resumes stdin from W | — | as a front crash | the front resumes |
| D: SEND → OFD_EVIDENCE | the Reconciler commits `DRAIN_ABANDON`; the worker's INTAKE then loses the alternative, and it closes its copies unread; the front reattaches | the front commits `DRAIN_ABANDON` and reattaches | `DRAIN_ABANDON` by the Reconciler | the front commits `DRAIN_ABANDON` |
| E: OFD_EVIDENCE → INTAKE or ABANDON | the CAS decides: with INTAKE the worker owns (row F); otherwise the Reconciler commits `DRAIN_ABANDON` | with no INTAKE, the front commits ABANDON and resumes; with INTAKE, row F | INTAKE committed → row F at reconstruction; otherwise ABANDON | the CAS decides; the loser does not act |
| F: INTAKE → RELEASE | the worker owns. The restarted front reads INTAKE and never resumes; its output read copies stay in the escrow, and it holds no stdin write copy | RT-27: `DRAIN_RECLAIMED`; the front closes its stdin write copy at once; outputs reattach from P; `READ_GAP_POSSIBLE` if the worker's `ARMED` was open | every process and pipe is gone; the rows settle by the crash table (no CLOSED frame: `Unknown`, holds kept) | the worker stops per M8; its intervals close cleanly |
| G: after RELEASE | the worker owns; the front's restart is RT-10 | RT-26 | as row F | as row F |

Two readers or two writers never act on one descriptor at once.

### V4-H.5 Writer duplicates, ownership and EOF

- **One writing owner** at any time (M7): the front in Front_Held until its stop flag, the worker from Intake.
- **Where duplicates exist.** SEND creates the worker's copy; the front's copy remains until RELEASE. Between SEND and INTAKE the worker never writes, and between INTAKE and RELEASE the front never writes.
- **Where each surviving copy closes.** The worker closes its copy, unwritten, on ABANDON or failed validation (H4). The front closes its copy at RELEASE, and at once when the worker dies while Intake (RT-27). The helper and init close theirs before GO (V4-E.2).
- **EOF.** The actor sees EOF only when the last write description closes, so an owner's death produces EOF only once every other copy is closed. The close points above guarantee that for every window.
- **`STDIN_EOF`** is journaled when the owner has written W equal to the payload length and closed its copy, and `DRAIN_RELEASED` (or no transfer) shows that no other copy exists. Otherwise the outcome is `STDIN_TRUNCATED` or `STDIN_POSITION_UNKNOWN`, which are UNKNOWN, never PASS (OB-020 class).
- **Read ends.** A retained read copy never delays or produces EOF.

### V4-H.6 Gates, rosters, reapers and holds

- M6 and M7 (V4-F.5) authorize exactly this protocol: the front reads and spools in Front_Held and Stop_Intent; nobody reads in Frozen or Ofd_Evidence; the worker reads and writes from Intake; the collector or reconciler reads in Reclaimed.
- No LIVE or UNKNOWN row is relabelled by a transfer. The full rosters stay. The draft's refusal of other LIVE rows at capture (`rw/protected_root_observation.py:122-127`) is lifted only for descriptors whose INTAKE commits.
- The authentic reapers stay the helper, init and the outer wait (C2-71). Every uncertainty hold stays (PR-b, RT-5, RT-13).

---

## V4-I. Requester correspondence: non-circular joins, typed operands, gate contracts (V3-REQ-I; 09.1, 09.2, 09.3, 09.5; D-8a, D-8b)

Carried: v3 V-I.1 (the original baseline; C3-VI1) and V-I.4 and V-I.5 (the joins in prose and the gate list; C3-VI45). Superseded: v3 V-I.2, V-I.3, V-I.6 and V-I.7.

### V4-I.1 Three joins in the additive unit `Worldline.Requester_Correspondence` (spec S8)

| Join | When | Head it reads | Authorizes |
|---|---|---|---|
| `Transfer_Join` (FRESH) | before intake | the authenticated `REQUEST_TRANSFER_INTENT (r, s)` event: in the verified chain (V4-C.1), of the current generation, whose owner is the worker, in root phase WORKER_OWNED or ORIGINAL_RESULT, subject r, sub-generation s, mode FRESH, with a record digest equal to the transferred frame's | the `REQUEST_INTAKE (r, s)` CAS (V4-F.2) |
| `Relay_Join` (RELAY) | before intake | the same head, mode RELAY, and the authenticated relay channel (the custody channel, whose peer is the front) | the `REQUEST_INTAKE (r, s)` CAS |
| `Serving_Join` | at every gate use after intake | the committed `REQUEST_INTAKE (r, s)` of the current generation; for the root's own operation, its `CUSTODY_ACK (g)` (RETAINED) | that gate's use (V4-I.4) |

The pre-intake joins read only the earlier transfer intent, and intake is the event they authorize, so no join requires its own future event (09.1). HISTORICAL gates keep the exact type `RetainedRequestObservation`, built from retained bytes (v3 V-I.5).

**Conjuncts by mode** (replaces v3 V-I.3):

| Conjunct | FRESH (`Transfer_Join`, then `Serving_Join`) | RELAY | RETAINED | HISTORICAL |
|---|---|---|---|---|
| J1 decode the retained host ucred | required | required | required | required |
| J1′ the worker's re-read of the transferred socket | required at intake and at every gate use | Absent (typed) | Absent | Absent |
| J2 retained host bytes equal the document's `rawUcred` | required | required | required | required |
| JF the front's re-read at transfer, journaled in the transfer intent | required | required | — | — |
| JG the front's re-read **at each gate use**, over the relay channel, by the original `RequestPeer.observation ()` (`rw/client_peer.py:131-137`) | — | required; a re-read error is the original error at that gate | — | — |
| J3 relative uid/gid equal host uid/gid; user namespaces equal when both records are present | required | Absent | Absent | Absent |
| J4 socket identity (dev, ino, mode): the front's journaled value equals the worker's fstat while the front still holds its copy **[unverified reasoning, K-15]** | required | Absent | Absent | Absent |
| J5 cookies equal when both are present; absence never blocks | corroboration | Absent | Absent | Absent |
| J6 relative pid recorded uninterpreted | recorded | — | — | — |
| JN PID-namespace correspondence (V4-I.3), never equality | when both records are present | — | — | — |
| J7 pidfd | optional, never required | optional | — | — |
| J8 head | transfer intent before intake; intake after | the same | `CUSTODY_ACK (g)` | the original capture |
| J9 explicit joins (V4-I.2) | required | required | required | required |

`Join` results: `Join_Ready`, `Ucred_Malformed`, `Uid_Gid_Mismatch`, `Front_Reread_Mismatch`, `Gate_Reread_Mismatch`, `Socket_Mismatch`, `User_Namespace_Mismatch`, `Pid_Namespace_Unrelated`, `Presence_Invalid`, `Head_Missing`, `Join_Operand_Mismatch`. For FRESH, any result but `Join_Ready` declines intake and the request goes to RELAY (V4-I.5). For RELAY, a result other than `Join_Ready` keeps the request queued (V4-I.5). Nothing is refused for correspondence.

### V4-I.2 Typed operands (replaces v3 V-I.2's record)

```ada
type Mode is (Fresh, Relay, Retained, Historical);
type Optional_Record (Present : Boolean := False) is record
   case Present is
      when True  => Value : L.Identity;              -- a raw span
      when False => Errno : Interfaces.Integer_32;   -- typed absence; 0 when not applicable
   end case;
end record;
type Requester_Operands is record
   Which                 : Mode;
   Raw_Host_Ucred        : L.Identity;       -- the retained 12-byte record (rw/client_peer.py:79-84)
   Raw_Relative_Ucred    : Optional_Record;  -- J1'
   Front_Reread          : Optional_Record;  -- JF
   Gate_Reread           : Optional_Record;  -- JG
   Host_Socket_Identity, Reader_Socket_Identity : Optional_Record;  -- J4
   Host_Socket_Cookie,   Reader_Socket_Cookie   : Optional_Record;  -- J5
   Origin_User_Ns,       Reader_User_Ns         : Optional_Record;  -- J3
   Origin_Pid_Ns,        Reader_Pid_Ns          : Optional_Record;  -- JN
   Held_Pid_Ns           : Optional_Record;  -- the worker's namespace identity recorded at HELD
   Pidfd_Record          : Optional_Record;  -- J7
   Request_Document      : L.Identity;       -- the canonical observation document
   Request_Id, Operation_Name, Raw_Request : L.Identity;  -- decoded from it
   Row_Request_Capture   : Optional_Record;  -- capture['request'] of the operation row
   Transaction_Preparer  : Optional_Record;  -- preparerPeer, for transaction operations
   Reservation           : Optional_Record;  -- capture['resource_intent'].reservation
   Generation, Subgeneration : Q.Quantity;
   Transfer_Head         : L.Identity;       -- REQUEST_TRANSFER_INTENT (r, s)
   Intake_Head           : Optional_Record;  -- REQUEST_INTAKE (r, s), after intake
   Descriptor_Anchor, Genesis_Anchor : L.Identity;  -- Roster_Join (v3 V-C.3)
end record;
```

| Operand | Decoded from | Native check (J9) |
|---|---|---|
| `Request_Document` | the canonical observation bytes (`rw/client_peer.py:113-117`), in form UTF8 without the LF (`rw/canonical.py:41-49`), by `Source_Json` | its `requestId`, `operation`, `rawRequest` and `peer` fields equal `Request_Id`, `Operation_Name`, `Raw_Request` and the decoded host record |
| `Row_Request_Capture` | the operation row's `capture['request']` (`rw/protected_operations.py:402-403`, `:415`) | equal to `Request_Document` when present |
| `Transaction_Preparer` | the transaction record's `preparerPeer` (`rw/client_peer.py:204-220`) | equal to the original preparer observation when the operation is a transaction; typed absence otherwise |
| `Reservation` | `capture['resource_intent'].reservation` | equal to the scoped row's bound reservation |
| `Transfer_Head`, `Intake_Head`, `Generation`, `Subgeneration` | the verified custody chain | as V4-I.1 |
| `Descriptor_Anchor`, `Genesis_Anchor` | the selected containers | `Roster_Join` |

**Presence by mode** follows the conjunct table: a field present against its mode, or absent where its mode requires it, is `Presence_Invalid`.

### V4-I.3 User namespace equality versus PID namespace correspondence

- **User namespace.** The helper creates only PID and mount namespaces (`native_root_worker_supervisor_v1.c:257`, `:336`), so the worker shares the front's user namespace by construction. When both records are present they must be equal (J3); a difference declines FRESH, and RELAY serves.
- **PID namespace.** It is deliberately different. `Reader_Pid_Ns` must equal `Held_Pid_Ns`, the worker's namespace identity recorded at HELD, and `Origin_Pid_Ns` must be the front's own (JN). The two are never compared with each other. The relative pid is recorded, never interpreted (J6), and the kernel's translation of pids across namespaces stays a measurement (K-1).

### V4-I.4 Per-gate contracts (adds the operand and head columns to v3 V-I.5's list)

| Gate (v3 V-I.5) | Worker-side modes | Operands beyond J1, J2 | Admission head required at use |
|---|---|---|---|
| `rw/canonical_actor_execution.py:64` before-exec capture | RETAINED for the root's own operation; FRESH or RELAY for a transferred request | `Row_Request_Capture`, `Reservation` | own: `CUSTODY_ACK (g)`; transferred: `REQUEST_INTAKE (r, s)` |
| `rw/protected_operations.py:401` `resource_request_material` | FRESH, RELAY | `Request_Document`, `Reservation` once reserved | `REQUEST_INTAKE` |
| `rw/protected_operations.py:414` `_row_for_request` | FRESH, RELAY; RETAINED for its own operation | `Row_Request_Capture` | as the first row |
| `rw/protected_operations.py:686` pre-effect boundary | FRESH, RELAY | `Row_Request_Capture`, `Reservation` | `REQUEST_INTAKE` |
| `rw/protected_operations.py:728` `_invoke_serial` context | FRESH, RELAY | `Request_Document` | `REQUEST_INTAKE` |
| `rw/protected_owner.py:323` owner peer | FRESH, RELAY | `Request_Document`; the owner-only uid from `Raw_Host_Ucred` | `REQUEST_INTAKE` |
| `rw/canonical_owner_witness.py:22` | FRESH, RELAY | `Request_Document` | `REQUEST_INTAKE` |
| `rw/protected_resource_runtime.py:229` `credential_join` | FRESH, RELAY | `Raw_Host_Ucred` | `REQUEST_INTAKE` |
| `rw/protected_resource_runtime.py:387` reserve packet | FRESH, RELAY | `Request_Document` | `REQUEST_INTAKE` |
| `rw/protected_scoped_resource_runtime.py:386` `intent_for_operation` | FRESH, RELAY | `Request_Document`; `Transaction_Preparer` for transactions | `REQUEST_INTAKE` |
| `rw/protected_scoped_resource_runtime.py:625` `lifecycle_packet` | RETAINED | `Row_Request_Capture` | the operation's own head (`CUSTODY_ACK (g)` or its capture) |
| `rw/protected_scoped_resource_runtime.py:702` `launch_reserved` | FRESH, RELAY | `Reservation` | `REQUEST_INTAKE` |
| `rw/protected_scoped_resource_runtime.py:858` `go_scoped` | RETAINED | `Reservation` | the operation's own head |
| `rw/protected_root_observation.py:28` `RootControllerCapture` | RETAINED | the frame's `original_request` | `CUSTODY_ACK (g)` |
| `rw/protected_root_resource.py:33`, `rw/protected_root_supervisor.py:21`, `rw/root_worker_custody.py:97`, `rw/protected_root_worker.py:53` | front only, the original `RequestPeer` | — | the front's own FRONT_* phase |

Every gate checks `Serving_Join` (or the RETAINED equality) at each use, as the original re-reads at each use (`rw/client_peer.py:131-137`). The front's gates stay exactly `type (x) is RequestPeer`, and no gate accepts two types.

### V4-I.5 Service path for requests that cannot be joined (replaces v3 V-I.6)

1. **While a reachable worker owns** (WORKER_OWNED or ORIGINAL_RESULT): FRESH transfer. If the worker declines, `REQUEST_ABANDON (r, s)` commits and the front offers s+1 in RELAY mode. In RELAY the front keeps the client socket, re-reads it under the original `RequestPeer` at every gate use (JG), and writes the worker's response bytes (M5). The original authorization is applied at every mutation, by the worker's original guards.
2. **When RELAY also cannot join,** or no worker is reachable, the request stays Queued, with authenticated QUEUED progress events (V4-L.2). It is served by the first owner that can serve it: the reachable worker, or the front at FRONT_OWNED (g+1) under the original gate. V4-L.2 states when that happens.
3. **Never** is a request refused for correspondence, provider absence, a missing cookie, namespace records or queueing. No join is fabricated, and no deadline settles anything.

### V4-I.6 Ordering (replaces v3 V-I.7)

1. Receive the full roster: frame, sockets (FRESH), locks and origins. This repairs `rw/root_worker_custody.py:183-185`, where a `RequestPeer` is built before the roster arrives.
2. Validate every element.
3. `Transfer_Join` or `Relay_Join` over the transfer-intent head.
4. CAS `REQUEST_INTAKE (r, s)`, or `CUSTODY_ACK (g)` for the root.
5. Only then use any gate, each time through `Serving_Join`.

---

## V4-J. Startup union, initial authentication and migration (V3-REQ-J; 12.1, 12.4; D-2a)

v3 V-J (C3-VJ, with R4-37 … R4-40 and R4-53) is carried: the exact v1 keysets, the v2 keysets, creation slots, DDL, the recovery map and v1 parity.

### V4-J.1 v1, exactly

v3 V-J.1 is carried unchanged: every v1 keyset, loader, creation slot and check stays as observed.

### V4-J.2 Selection union, exactly

| Artifact | v1 selects it by | v2 selects it by | Loader or constructor |
|---|---|---|---|
| Startup descriptor | the installed entry (`rw/protected_startup.py:172`) | the same | `StartupLease`; `schema` exactly `worldline.protected-startup-v1` or `-v2` chooses every path below (C2-111). Nothing defaults between versions. |
| Owner plan (plan-v1 under both) | an endpoint argument (NF-10) | `root_worker.owner_plan`; any argument must equal it | `RootWorkerFront` plan check (`rw/protected_root_worker.py:96-114`), unchanged |
| Crosswalk | — | `root_worker.crosswalk`, bound in `files` | `Root_Crosswalk` (V4-C.5) |
| Custody genesis | the plan's `handoff_genesis` | the same | v1: `RootCustodyJournal` (`rw/root_worker_journal.py:28-114`), unchanged. v2: the v2 loader (V4-J.3) |
| Custody database and lock | the plan's `handoff_journal`, plus `.lock` | the same | as above |
| Issuer key | `authority_root/authority/issuer/state/issuer-key.bin` | the same | `private_bytes` with the digest check (`:50-53`) |
| Run-scoped config | `runtime.resource_scoped_producer` (the draft's read, `rw/protected_scoped_resource_runtime.py:54-56`) | the same, now a v2 key | `exact` (form ASCII) |
| Tools | `runtime.tools`, v1 semantics | the same, with the required keys of R4-37 | `shutil.which` resolution (`rw/protected_startup.py:293-295`) |
| Helper images | the plan's `helper` | the same, and the crosswalk's `helper_image_sha256` | the source lease |
| Schema files | — | `files` (v2 §11.2) | the startup inventory |
| Provisioners | `protected-canonical/provision_operation_head.py` | that one, plus `protected-root/provision_root_crosswalk.py` and `protected-root/provision_root_custody_v2.py` | offline ENTRY selections only (the `_offline_operation_slot` pattern, `rw/protected_startup.py:340-344`), bound in `files`, run by the operator (OP-1), never by startup |

### V4-J.3 One-shot provisioning, and authentication at every startup

**What the custody provisioner creates,** each by exclusive create (R4-40):
- the genesis file: canonical form UTF8, exactly the v2 keys (R4-38), with `initial_event` set to `null`;
- the database, with exactly the DDL of v3 V-F.5 (with R4-29), and these rows:
  - `genesis`: (`owner-genesis`, the genesis archive, HMAC-SHA256 under the issuer key over `DOMAIN_V2 ‖ archive ({genesis})`);
  - no events;
  - `head`: (`current`, the origin, HMAC over `DOMAIN_V2 ‖ archive ({head: origin, genesis})`), where the origin is the SHA-256 of the genesis archive, exactly v1's rule (`rw/root_worker_journal.py:98`, `:112`);
  - empty `root_state`, `subject_state`, `alternatives` and `blobs`;
- the lock file.

`DOMAIN_V2` is `worldline.protected-root-custody-v2` followed by a zero byte, beside v1's `-v1` domain (`:15`), so no v1 MAC verifies as a v2 MAC.

**At every startup,** first included, by the same path:
1. open with `mode=rw`, never creating (`:78-84`);
2. the complete `sqlite_master.sql` text equals the DDL (v3 V-J.4);
3. the genesis file's bytes, bound as DATA, equal the row's archived genesis, and the genesis MAC verifies;
4. the chain verifies from the origin, and the head MAC verifies (`Custody_Chain_Valid`, V4-C.1);
5. the state rows equal `Next` folded over the events from the initial state **S0**: no `root_state` row means generation 1 in FRONT_OWNED with owner Front and no subjects. With zero events, the head is the origin;
6. the cross-references of V4-C.2 hold.

Any failure is a named refusal (RT-14). Nothing is created, initialized or re-genesised, and the premise P-A3 bounds what this establishes.

### V4-J.4 Prior-v1 migration paths

| Starting point | Path | Never |
|---|---|---|
| v1 deployment with no custody journal | provision v2 with `prior_custody = null` | create or reuse v1 custody objects |
| v1 deployment with a custody v1 journal whose every generation is closed (it loads under the v1 loader, and no generation is open or UNKNOWN) | the v2 genesis binds `prior_custody = {journal_path, journal_sha256, head_event}`. The v1 journal stays in place, read-only; each v2 startup checks its sha256 and its v1-loaded head. The v2 database is a new file at the plan's `handoff_journal` | modify, truncate, re-MAC or re-genesis the v1 journal |
| a v1 journal with an open or UNKNOWN generation | the provisioner refuses by name; the operator resolves it first under v1 (its reconciler and owner routes) | migrate a live custody |
| v2 back to v1 | no provisioner offers it. A v1 descriptor selects only v1 paths, and while a v2 worker lives, the transferred OFD locks make the v1 startup's lock acquisition fail (`rw/protected_startup.py:374-385`) | ignore a live v2 owner |

### V4-J.5 Recovery and owner mapping, plan version, frontier

- Every branch of `reconcile_before_endpoint` (`rw/protected_operations.py:355-384`) is mapped: v3 V-J.5 (with R4-53) and RT-21 … RT-27 (V4-G.4). The owner routes are C2-93's, with R4-49.
- The owner plan is plan-v1, `worldline.protected-root-worker-plan-v1`, everywhere. v3 V-P's "owner plan v2" (`D3:2004`) is an error, corrected in V4-O.
- v1 behaviour and the frontier control are exactly C2-116 (D-2b). v2's controls stay additive (v3 V-N, V4-M).

---

## V4-K. Sealed C-API status and root-worker stage composition (V3-REQ-K; IC-1, IC-11, IC-12; D-7a)

Carried: v3 V-K.2, V-K.3 (C3-VK2, with R4-41 and R4-42) and V-K.5 … V-K.10 (C3-VK5, with R4-43). Superseded: v3 V-K.1 and V-K.4.

### V4-K.1 Status (replaces v3 V-K.1)

- **CAPI4R** (sealed): ENDORSED_WITH_REQUIRED_CHANGES, requiring V4-RC4-GATE and V4-RC4-ALIAS (v3 V-K.1's record).
- **CAPI5R** (sealed; identities in the header): ENDORSED_WITH_REQUIRED_CHANGES; V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 NOT_CLOSED. Its required changes, verbatim from its `review.json`:
  - **V5-RC4-GATE-EXCEPTION:** "Make the sole assignment exception an independent invariant: before PK-6b the exclusive map is empty; from PK-6b its only key is G21c and the only wfx row is (Finalization_Decide, G21c, O). Validate that identity and its declared type/region/assignments against the normative G21c protocol independently of matching mutable tile/gate entries. Add an amendment control for an added, relabelled or moved wfx exception, plus positive controls for the unchanged staged tables. Preserve every current gate, branch payload, diagnostic, refusal code, assignment, write and accepted case."
  - **V5-RC4-QUAL-CAPTURE:** "Extend R-QUAL(d), BR6, the closure argument, promises and machine twin to examine every potentially capturing library-unit prefix mentioned by each with clause, including ancestor units mentioned through a named descendant. Define the text-only refusal without changing the scoped exception or use-clause inventory. Add a matching amendment control and an unchanged-context positive control. Keep installed integrated name/overload resolution OPEN."
- **CAPI6R** (sealed): ENDORSED with no required changes. V5-RC4-GATE-EXCEPTION, V5-RC4-QUAL-CAPTURE, V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 are CLOSED_AT_DESIGN_LEVEL. Its ruling ROOT_WORKER_INTEGRATION is "OPEN; no ruling on the other lane or integration order". Its open obligations include IMPLEMENTATION_AND_STAGE_REVIEWS, D-38_AND_RM_APPLICATION, FULL_STRICT_PROOF, ROOT_WORKER_INTEGRATION, D-13 (OPEN_OPERATOR) and N-06 (OPEN_OPERATOR_AT_DEPLOYMENT).
- **For this lane,** both v5 repairs are carried as dependencies. CAPI6R closes them at design level only, so they stay unmet for implementation, stage review, controls and proof, and G-CAPI is not met until the C-API successor is implemented and stage-reviewed. This is a review dependency, not an operator gate. Neither lane's acceptance and no integration order is decided here, and the other lane is neither reviewed nor corrected (NF-5).

### V4-K.2 Composition of RW stages with CAPI6's fixed invariants (replaces v3 V-K.4)

| Rule | Statement | CAPI6 basis |
|---|---|---|
| U-1 Append-only names | `RW_ROUTINE_NAMES` is a new table, disjoint from `CAPI_ROUTINE_NAMES` and `CAPI_REMOVED_NAMES`. The effective sets are: routines = `CAPI_ROUTINE_NAMES` ∪ `RW_ROUTINE_NAMES`; simple names = the last selectors of those routines and of `CAPI_REMOVED_NAMES`; roots = the first identifiers of the routines. No C-API row is edited, removed or reordered; a stage only appends (`.update` with new keys, or a tuple extension that keeps its prefix). | R-QUAL (a), (d) (`CAPI6/APPENDIX-BINDINGS.md:90-101`) |
| U-2 Old scopes unchanged | Before an RW stage adds a name or a root, it re-observes the per-call qualified inventory of every pre-existing scope (designed scopes, RESIDUAL, SPEC) under the effective simple names, and each must equal its unchanged `CAPI_QUALIFIED` row. It also re-checks (d1)–(d4) on the C_API specification, body and parent specification under the effective roots and simple names. Any difference fails closed. The remedy is a reviewed renaming of the new RW routine or scope, never an edit to an old row. | CAPI6 §19: tables are re-observed and reviewed, never edited to fit (`CAPI6/DESIGN.md:319-324`) |
| U-3 RW scopes and with clauses | `RW_QUALIFIED` adds only new scope keys, each an exact multiset of full expanded names. Every RW with clause, with or without `limited` or `private`, satisfies (d2) for every prefix: no identifier after the first is an effective root, and none is an effective simple name. RW adds no use clause beyond R-INV (vii)'s, makes no change to `core/worldline.ads`, and adds no `separate`. | (d1)–(d4), R-INV (vii) |
| U-4 Gate rows | `RW_GATES` rows join the effective gate table under new scope keys, with kind `bool` or `case` only. CR5 and CR6 run over the union of `CAPI_GATES` and `RW_GATES`, so the `wfx` roster stays exactly `[(Finalization_Decide, G21c, O)]` from PK-6b and empty before. An RW `wfx` row fails CR6, and CR5 gives it no assignment permission. | CR5, CR6 (`CAPI6/APPENDIX-BINDINGS.md:391-424`) |
| U-5 Exclusive map and protocol | RW has no exclusive-map table and never extends `CAPI_GATE_EXCLUSIVE`; CR6's key-set equality catches any added key. `CAPI_WFX_PROTOCOL` and `CAPI_PARENT_SPEC` are PK-1 constants that no stage appends to or reassigns. | W-A9, CR2 |
| U-6 Staging | RW stages append after the C-API successor's last stage and after L-CAPI-P and G-PROT. At every RW stage each C-API table equals its value at the C-API successor's last stage, byte for byte, and RW tables gain only RW keys. | stage discipline |
| U-7 Glue, residuals, clauses | GE1–GE9 and `Authority_Glue` are unchanged; the R-RES, S-RES and R-GLUE identities are preserved; the S5 residual renamings and clause tuples CL-T3, CL-T4, CL-T5, CL-T12, CL-T13 and CL-T15 are unchanged (v3 V-K.6, V-K.7). | — |
| U-8 Floor and chain | The complete stage floor of v3 V-K.3 (with R4-41) holds on every RW stage, on the composed text. The gate chain G-CAPI → G-CAPI-P → G-PROT → G-RW is unchanged. | — |

### V4-K.3 Affected-stage controls

| Control | Mutation or positive | Expected |
|---|---|---|
| MX-RW1 | an RW gate row of kind `wfx`, in any scope | CR6 problem |
| MX-RW2 | an RW key added to `CAPI_GATE_EXCLUSIVE` | CR6 problem |
| MX-RW3 | an RW gate row of a kind other than `bool` or `case` | an RW gate-kind problem |
| MQ-RW1 | an RW with clause `with Worldline.X.Y;` in which a prefix after the first identifier is an effective root or simple name | (d2) problem |
| MQ-RW2 | an RW routine whose simple name occurs as a last selector in a pre-existing scope | U-2 problem |
| MQ-RW3 | a declaration of an effective root identifier inside an RW scope, at any nesting depth | (d1) problem |
| MQ-RW4 | `separate` in the C_API pair | (d4) problem |
| MQ-RW5 | a use clause in an RW scope beyond R-INV (vii)'s | R-INV problem |
| PX-RW1 (positive) | every C-API table byte-identical to its last C-API stage value, and the unchanged C-API contexts, at each RW stage | no problem |
| PX-RW2 (positive) | an RW stage with its own `bool` and `case` rows and its own qualified inventories | no problem |

They mirror CAPI6's MX9 … MX17 and MQ15 … MQ24 for the RW additions. The integration checks become IC-1 … IC-14: IC-11 and IC-12 as replaced by R4-43; **IC-13**, the U-2 re-observation of every old scope at each RW stage; **IC-14**, the U-6 byte identity of every C-API table at each RW stage. IC-10 stays OPEN until the admitted frame and installed compiler exist (CAPI6R's D-38_AND_RM_APPLICATION).

---

## V4-L. Response progress (V3-REQ-L; 06.3, 06.4, 09.5, 12.4; D-4a, D-8b)

Carried: v3 V-L.1 (lock inventory), V-L.3 (lock order and SL-0, with R4-44) and V-L.6 (fairness). Superseded: v3 V-L.2, V-L.4 and V-L.5.

### V4-L.1 Thread placement (replaces v3 V-L.2)

- **Original placement kept.** In whichever process owns custody, protected sections run where the original code runs them, under SL-0's single acquisition and the original non-reentrant `Gate.mutex`. v3's dedicated single-thread lane is **withdrawn**: it could serialize sections the original runs concurrently, and so could block a response the original would complete (06.4).
- **Registered-root I/O executor, kept.** I/O on user-registered paths runs in its own executor with per-requester fair shares, holds no protected lock, and is revalidated inside a protected section. A stalled registered path therefore never occupies the default executor.
- **Callbacks** (`add_reader`, `add_writer`, done-callbacks) take no lock and only complete futures.
- The A1-origin files change only under G-A1's separate selection, freeze and review (V-L.3).

### V4-L.2 Progress, request class by custody phase

"Waits on" lists everything a request can wait for in the process that serves it. The original's own waits are the daemon mutation lock for mutating operations (`rw/daemon.py:350-357`), `operation_lock` for every protected request (`rw/protected_operations.py:716-717`; NF-3) and protected storage. A row adds nothing beyond those unless it says so.

| Custody phase | Who serves | Waits on | Progress happens when | Added beyond the original |
|---|---|---|---|---|
| FRONT_OWNED | the front, as original | the original waits | as original | nothing |
| HANDOFF_INTENT … ROSTER_EVIDENCE (handoff window) | queued; then the worker after `CUSTODY_ACK`, or the front after `ABANDON` | the handoff's own steps, and storage | the worker's intake commits, or the worker dies and the front commits `ABANDON (g)`. The front never abandons on a deadline, because that would turn a healthy root operation into a quarantine | the handoff window |
| WORKER_OWNED or ORIGINAL_RESULT, worker reachable | the worker, through FRESH transfer or RELAY, at once | the original waits, in the worker. The front's root invoke returns after the initial result and leaves the detached job to its collector (`rw/protected_root_worker.py:184-190`); the worker's serving path keeps that shape (DESIGN), so no `operation_lock` is held for the detached job | as original, in the worker | the transfer or relay round trip |
| WORKER_OWNED, worker unreachable (custody channel lost, worker alive) | queued; then the front at FRONT_OWNED (g+1) | the worker's completion, or a cancel | the worker completes its root operation under the original workload time limit and relinquishes, then collection and reconstruction run; or an authorized `job.cancel` stops the root unit (M8 (c)), and collection follows the physical evidence | the wait for the worker; no deadline settles anything |
| HANDLER_TERMINAL … FRONT_RECONSTRUCTION | queued; then the front at FRONT_OWNED (g+1) | physical closure (kernel events) and storage | the barrier completes and reconstruction binds | the collection |
| UNKNOWN | queued; then the front once the Reconciler decides | durable evidence | the Reconciler's native redecision on authentic evidence (pidfds terminal with CLOSED or ABANDON), including the evidence that an authorized `job.cancel`'s stop produces | the wait for evidence |
| any phase, protected storage stalled | — | storage | when storage resumes, as in the original. Accepting connections and recording queue entries in memory continue, but are not counted as progress | nothing |

**By request class.**
- **`status`** is mutating and may re-capture PRIME (NF4-11). It is served by the custody owner under the original waits, including the registered-root I/O of a dirty store.
- **`job.cancel`** is served by the custody owner (original `runner.cancel`; the worker through `STOP_UNIT`). When no owner is reachable, it also causes the M8 (c) stop (R4-49), and its response is the original handler's once custody returns.
- **Owner routes and `quarantine.resolve`** keep the original guard order and the unresolved-gate exception, in whichever process serves (C2-93).
- **Non-mutating requests** wait only on what they wait on in the original, in the serving process.

**QUEUED progress events.** While a request is queued, the front may send events on the original progress channel (`RequestContext.progress`) naming the custody phase and generation. They are informational and are never counted as response progress.

**No unconditional liveness claim.** Each row states its condition. The only waits added to the original's are the handoff, an unreachable worker's completion or cancellation, collection, and evidence for UNKNOWN. Each ends with an authentic event or an authorized cancellation, never with a deadline or a fabricated join.

### V4-L.3 Router and collector (replaces v3 V-L.4)

- The router holds its lock only for the routing decision. It never awaits a collector, a custody event or closure under its lock, which removes NF-7's wait.
- It reads the custody state, cached and refreshed on every custody commit, and routes: to the front in FRONT_OWNED; to the worker by FRESH or RELAY while a reachable worker owns; otherwise to the durable queue (`REQUEST_QUEUED`), returning at once.
- Queued requests are re-evaluated on every custody commit, through a condition the custody journal's commit notifies, and in per-requester fair FIFO order (V-L.6).
- `RootWorkerFront.invoke`'s FRONT_OWNED refusal (`rw/protected_root_worker.py:159`) is replaced by this routing.
- The collector runs as its own task and holds neither `operation_lock` nor the router lock.

### V4-L.4 The no-refusal queue, reconciled

Queue entries are durable and never dropped. Every exit from the queue is one of: transfer or relay to the worker; service by the front at FRONT_OWNED (g+1); or the original response, error included, of the handler that serves the request under the original guards and the mutation gates of V4-F.5. None is a refusal for queueing, phase, correspondence or provider absence. Resource exhaustion of the queue itself makes the affected outcome UNKNOWN, never an accepted refusal (V-L.6).

---

## V4-M. Additive controls added by v4

These join the additive roster (C2-17 with R3-9 and R4-6). Pure value fixtures need no root; lab controls need the operator (OP-4, OP-7, OP-8). No original control is retired, and the frontier control is unchanged (C2-116).

- **V4-B** (pure). W2′ and W8′: multi-frame vectors with several runs and distinct heads → `Ready`. L-SAT-1′: a C1-refused input with a non-zero byte gives `Authority_Refused` on both sides; an all-zero `Data` needs form (c); a saturated all-zero arena needs compaction. Compaction with overlapping and aliased spans gives equal decisions. A residual census: every original native fixture is classified D_emb, R1, R2, R3 or R0, and any R0 member keeps CV-R OPEN.
- **RQ-1** (pure and lab). Windows W0 … W5 on the root route, each with its refusal or `Ready`, its U records, its P class and its recovery. The root route's guard order equals the serial route's, with the `DISPATCH_INTENT` boundary present and quarantine before `CUSTODY_ACK`.
- **V4-C** (pure). `Number_Canonical` accepts every lexeme the Python checks accept, and refuses `-0`, `1.50`, `1E5`, `1e16`, leading zeros and a non-finite magnitude; it accepts `1e+16`, `-0.0` and `0.1` **[RC-5]**. Form ASCII accepts a lone-surrogate escape. Deep nesting that the Python check accepts is accepted natively. P3: an unleased mapping of any permission is refused, as in the original. A custody database restored alone to an older valid state is refused (RT-14).
- **V4-E** (lab). `COMMIT_CHILD` with a wrong ticket, altered measurement bytes, altered ancestry, a non-Ready decision, or a disagreement between worker and sub-helper → the actor never execs; the correct case → exec. Launch_Intent precedes dispatch. FD audits: the actor holds exactly 0, 1 and 2; the coordinator exactly its roster. A capability readback against V4-E.4. Seccomp refuses each listed call, including `open_by_handle_at` and `io_uring_setup`.
- **V4-F** (pure). `Legal` and `Next` for every row of the root, request and descriptor tables. A REQUEST and a DESCRIPTOR subject with the same subject string do not collide on replay. `CUSTODY_CAS_STALE`; `CUSTODY_ALTERNATIVE_TAKEN`; an event of an older generation refused; the initial state admits only `PREPARED (1)`. M1, M2 and M3 refuse a non-owner. M6 lets the front spool in Stop_Intent. M8 admits the original owner cancellation, the helper's kill before GO and the M8 (c) stop, and refuses a stop on a deadline.
- **V4-G** (pure and lab). A `Never_Dispatched` row released without CLOSED_WITNESS; a dispatched row without HELD retained. A unit still "active (exited)" under `RemainAfterExit=yes` does not hold up the barrier. Reconstruction without HANDLER_TERMINAL uses the frame's seed; a disagreeing HANDLER_TERMINAL refuses. RT-21 … RT-27.
- **V4-H** (lab). A crash in each window A … G of V4-H.4, for front, worker and host. `READ_GAP_POSSIBLE` on an open `ARMED`; no resume after an open `WRITE_ARMED`, with `STDIN_POSITION_UNKNOWN`. Reattachment after a closed transport. EOF only after the last write copy closes, including the RT-27 case.
- **V4-I** (lab). Intake is authorized by `Transfer_Join` over the transfer intent alone. RELAY with the front's re-read at every gate use. A client that exits after transfer → `Ready`. Different PID namespaces → `Ready`. Different user-namespace records → FRESH declines and RELAY serves. Every gate of V4-I.4 by its mode.
- **V4-J** (lab). A first start on a freshly provisioned set → `Ready`. Any missing or extra key → schema refusal. A state row that differs from the fold → refusal. Migration over a closed v1 journal → `Ready`; over an open one → the provisioner's refusal. v1 parity.
- **V4-K** (static). MX-RW1 … MX-RW3, MQ-RW1 … MQ-RW5, PX-RW1, PX-RW2, IC-13, IC-14.
- **V4-L** (lab). Each row of V4-L.2. A static audit that the router awaits nothing under its lock.

## V4-N. Measurement items and installed-runtime checks added by v4

K items are reserved to the operator under OP-7 (R4-5). RC items are ordinary lead-owned installed-runtime checks; a traced run that needs root is operator work.

| Id | Question | Used in |
|---|---|---|
| K-22 | A pipe's reader sees EOF only when every write description is closed, including one held by another process through `SCM_RIGHTS`; a retained read copy changes nothing | V4-H.5 |
| K-23 | `kill` from a process in a child PID namespace can name no process outside that namespace, whatever its uid | V4-E.4 |
| RC-5 | The installed CPython's number rendering in `json.dumps`: integers, and `float.__repr__`'s shortest round-trip digits, notation thresholds and formatting | V4-C.3 |
| RC-6 | An inventory of the privileged operations the original handler paths use on the installed runtime: capabilities, syscalls, written paths, connected sockets, IPC and keyrings. A static audit by the lead; a traced run needing root is operator work (OP-4) | V4-E.4 |

## V4-O. Everything that remains OPEN (replaces v3 V-P)

v2's §18 list stays carried (C2-18 with R3-20 … R3-24, as amended by R4-11 … R4-13). In addition:
- **All original obligations.** OB-001 … OB-219 stay OPEN, with no closure credited (the v3 review's `open_obligations`, all OPEN, observed). Nothing here closes any of them.
- **Required changes, clauses and rulings.** V3-REQ-A … V3-REQ-L, V2-REQ-A … V2-REQ-L, RQ-1 … RQ-5, the inherited RC items other than RC-05 and RC-10, and every NOT_CLOSED or PARTIALLY_CLOSED clause and ruling, until reviewed with source, proofs and controls on matching source.
- **C-API.** CAPI6R's open obligations, including IMPLEMENTATION_AND_STAGE_REVIEWS, D-38_AND_RM_APPLICATION, FULL_STRICT_PROOF, ROOT_WORKER_INTEGRATION, D-13 (operator) and N-06 (operator, at deployment). G-CAPI is unmet.
- **Lemmas.** L-BR-1, L-SAT-1′, L-RB-1P, L-RB-1C, L-RB-4 (over every called body and every successor unit), W2′ and W8′ consistency, CJ-1, `Number_Canonical`, PD-1 … PD-5, CV-B′, CV-R (R0 empty), and every carried lemma.
- **Residuals** R0, R1, R2 and R3: coverage limits, decided by the original unit.
- **Native units, unwritten:** `Source_Json` with `Number_Canonical`; `Roster_Join`; `Root_Crosswalk`; `Hmac_Sha256` and `Custody_Chain_Valid`; `Root_Custody_Phase` (the complete relation); `Requester_Correspondence` (three joins); `Child_Event_Legal`; the V2 successors; the B2b and B2c successors.
- **Design tables to review:** V4-B.2, V4-B.6, V4-D.2, V4-E.1, V4-E.2, V4-E.4, V4-F.2, V4-F.5, V4-G.4, V4-H.4, V4-I.4, V4-J.2, V4-K.2 and V4-L.2.
- **Premises and audits.** P-A1 … P-A4 (OS and installation workstream; OP-1) and the anti-rollback non-claims; AU-1; the L-RB-4 body audit; RC-6; the SL-0 audit, including `run_service` and the A1-origin files under G-A1.
- **Schemas and provisioners.** The startup descriptor v2, the plan-v1 schema file, the custody genesis v2, the crosswalk, `protected-root/provision_root_crosswalk.py` and `protected-root/provision_root_custody_v2.py`. The owner plan stays plan-v1 (v3 V-P line 2004 said "owner plan v2"; that was wrong). Provisioning is operator work (OP-1).
- **Accounting.** No option is selected (D-4a, OP-3). P-M1, P-M2, P-D1 and option G are unselected.
- **Confinement and measurement.** M-1 … M-7; K-1 … K-23 (OP-7); RC-1 … RC-6.
- **Integration.** L-CAPI-P (not designed), G-PROT, IC-10.
- **Proof and runtime.** The admitted strict frame (R-PROOF); the full matching-source campaign, with protected floor 251, the sole boundary and zero unproved, justified and `pragma Assume` (P1:161); the 52-action ordinary roster (P1:162); the lifetime controls; RQC; every additive control; hosted assurance and publication (R-PUB).
- **Operator.** OP-1 … OP-9, and the paused frame, capacity and storage gates.
- **Process.** The independent actual gpt-6.1-sol review of v4, of every slice and of the full lane.

## V4-P. Non-claims (adds to v3 V-Q, carried with R4-51)

- v4 reviews, accepts, proves and authorizes nothing, and adds no approval gate. Every original obligation and every lane seam stays OPEN.
- Nothing was compiled, run, imported, proved, tested or measured.
- No authenticity of the key, genesis or head is claimed beyond the premises P-A1 … P-A4, and no rollback detection beyond V4-C.2.
- No completion, reserved-capacity, confinement, deadlock-freedom or unconditional liveness property is claimed. Progress is stated with its conditions (V4-L.2).
- Bytes lost by a crashed reader are detected, never recovered (V4-H.1).
- No C-API acceptance or integration order is decided, and the other lane is neither reviewed nor corrected.
- No accounting option, cap, prerequisite or policy field is selected or added.
- No original accepted case gains a refusal. The named OPEN refusals that predate this design keep their obligations OPEN, unchanged.
- SIA recall is not evidence and is not used as evidence.

---

## Appendix A. JACKAL

No numeral in v4 was derived by arithmetic (§C.4), so no JACKAL call was made. `jackal.json` records this. Inside carried slices, v2's J01 … J18 keep their status: exact, `formal=false`, lane `rat`, informational about arithmetic only.

## Appendix B. Inputs bound while drafting v4 (sha256, observed)

v3's list is carried as slice C3-APB. A read-only script recomputed every one of its entries; none had changed (observed). New or newly cited inputs:

```
a0f2f411d654f1cce472a1ad2a13d3c082fff42def050c5ed4694a8b094d07a0  D3/SEAM-DESIGN.md
093f31176dd9560a236b8ad00f5fd28a683c810c8f400d646631318ca1b582e8  D3/seams.json
8cce45e34f12d9d7976cb9b04ab6ac47e3a99ae8cacc22708a84abe06ec0c024  D3/jackal.json
dd382e1b0f74e825735e168ab6856b1c85e93f9a39312f3bc15019faf390a0ea  D3/AUTHOR-NOTES.md
1e1c5ef8bb396d7e3fe75b63bb9c788616dfb6b26561d729c2d867064cfea879  D3R/REVIEW.md
35b264e77922b028443b6b36718f0db2c14efc14f06746dc7510c727141463cf  D3R/review.json
63bcb753990a9dbc0d2caf3a49db68baa103f5720cf7546bb9e7af68083c05ed  D3R/checks.json
c52bd9ee470d1b29dbfcd44a1bd00331a922af6323ead6a601db65814c09de40  D3R/review-freeze.json
73e82489706e03ca465e7dea2aed1823df0b50a8ce1c5ab0555c545579dc34d8  CAPI5R/REVIEW.md
800880d44bff4b234c82cc392a3008fd4d37139b0827d070120cf299370f403b  CAPI5R/review.json
c1398253713aa6d42ed11fda5194502ccae5a64825b36ef8100206f7d40719ef  CAPI5R/checks.json
91bddf1a46763251940db658f5115cd13ab9de4aa67c0a41ae169de165649af1  CAPI5R/review-freeze.json
f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2  CAPI5/APPENDIX-BINDINGS.md
cfa0dca9e275e878b958f2f8da6b5cf54824534867773382965f2a887e98a417  CAPI6/DESIGN.md
9f9f3dfa897d0c320226df39c89bc5c156fc87ebc3e24959ab0c08bba5db1946  CAPI6/APPENDIX-BINDINGS.md
12cfde3c3eed993b6056dc75d901710bdee1273e67cfe150a9648f99627da161  CAPI6R/REVIEW.md
bcfa259f8690c492b9284ef1ed9549efa7a5d3899edc1fbd5a0ae2ab7234d128  CAPI6R/review.json
12642ce4501f12b0a608264d9bd93a23f39fd6c7d2c85cee69d94a91a3e2f284  CAPI6R/checks.json
15fc9f07786eba0e0c1d3cde0250c8696e8ebeb96961ce6c22aeea2fcc590742  CAPI6R/review-freeze.json
33dbdb12904ef70c57809fed581e2e03a1e35b9f3935b30916f2c5e3cd8f0782  R/core/worldline-canonical_operation.ads
71019128a1f613ed641052737ecafaa425a842e078f066308e655b24f94c15f8  R/protected-resource/native_namespace_supervisor_v3.c
f2bc319b69f3491b9b16fde710fde122d94203ab2d5cfb94fb348d7c79d65793  rw/root_worker_codec.py
d133785f88a76f09f816f484a58a85d4cd75052a96424b12a52c5434121afb05  rw/operation_capture.py
25b590b09ebcf81f46726bdc276093a6e9861b6ab60859924eb151525f4adfe3  rw/root_worker_plan.py
17ccd237864d4b11a19fbd836ad9e585df718558d0d0c83569c1397761cb7aba  rw/controller.py
```

These are byte identities at the time of reading. They establish no authenticity, installed state or atomic snapshot.

## Appendix C. Slice and quote verification

A read-only Python script read the v1, v2 and v3 designs, the sealed v3 review and this file. It printed to standard output and wrote no file. It checked (observed; the final run is in AUTHOR-NOTES §2):
- v3 `SEAM-DESIGN.md`: sha256 `a0f2f411…a07a0`, 2128 lines, ending with a newline;
- every row of §B.1: the sha256 of the stated v3 lines equals the stated hash; no two slices overlap;
- every R4 replacement: the quoted `v3:` or `v2:` text equals the stated lines exactly; each v3 target lies inside its stated slice; each v2 target lies inside its stated C2 slice and is replaced by no R3; no line is targeted twice;
- transitively, every C2 slice of v3's §B.1 against v2 `SEAM-DESIGN.md` (`db512ddb…e1b5`), and every v1 slice of v2's Appendix C against v1 `SEAM-DESIGN.md` (`531d1128…3f46`);
- every quotation in §A from the sealed `review.json`: equal to the field it quotes.

## Appendix D. Companion file identities

Observed with `sha256sum` and `wc -c` after the files were written. This file cannot contain its own hash; `seams.json` records it.

| File | sha256 | Bytes |
|---|---|---|
| `jackal.json` | `4d556a457caa268c80b5d7ef4edae949433034ffeb950a5b4d2f8a29fcafcfab` | 3606 |
| `AUTHOR-NOTES.md` | `0bd92ccd556e39a358a5e93db5a57fe55ba206080d7b6dc1f033508d7f9c66e4` | 10119 |
| `seams.json` | recorded in the handback (it binds this file's hash) | — |
