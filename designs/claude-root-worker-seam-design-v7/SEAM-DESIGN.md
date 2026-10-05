# Root-worker runtime lane: seam design v7

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent, author role) |
| Date | 2026-10-05 |
| Status | **DRAFT_FOR_INDEPENDENT_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author reviews, accepts and closes nothing; author checks are self-checks. Every original obligation (OB-001 … OB-219), accepted case, deterministic fixture, control, contract, threshold, proof floor and scope remains **OPEN** and unchanged. |
| Supersedes | v6 `SEAM-DESIGN.md` (sha256 `f41566d8bb694817f27efb4dd336d25e554357976808aad577b91365a9a10787`, 116337 bytes, 990 lines), v6 `seams.json` (`a54dc595051b582d8c4a06dca62ad00ca9d728896c063cb2d73e4c01d046ddbe`), v6 `jackal.json` (`5d6684296284d33d3580e5dc123401b493fdf2431d3d54c57b8b4d98abcc84b0`) and v6 `AUTHOR-NOTES.md` (`95826c1ee59c7ef11cd9cefbcb3e212053d5ecbd05908224ba59572ebf922633`). All were read only and re-hashed unchanged; the first two equal the review's `design_sha256` and `seams_sha256`. |
| Answers | The sealed independent review of v6 in `WT/designs/claude-root-worker-seam-design-v6/review/claude-v1/`: `REVIEW.md` `2f814fee89819789d6184b3802c3b77ffda45bd3e6e2fe43e264f47e05890d83` (24144 bytes), `review.json` `da28c753456d8ef10a0042c2ef2e62d9c4162f1cb1922e60e60b58aa2a5c1b39` (16300), `checks.json` `8fb88b0b13e74319a8ff27a4b677da386f6fce0528bb8f64e552918356e52b36` (6547), `review-freeze.json` `a148a6c86f7403f7e12915613b9c7cdc9408c932062b924d07cb5bba0e751c79` (613). The freeze names "claude-opus-5-5 (independent Claude Code review subagent, fresh context)", `reviewer_kind` claude-subagent, `different_from_author` true, and lists the first three files with exactly these hashes and sizes (recomputed, equal). Verdict **ENDORSED_WITH_REQUIRED_CHANGES**: V5-REQ-B, H, L and M CLOSED_AT_DESIGN_LEVEL; V5-REQ-A, C, D, E, F, G, I, J and K PARTIALLY_CLOSED; required changes V6-REQ-A … V6-REQ-L. Not read, as directed: that directory's `raw-final-message.txt`, `review-records/`, and every `gpt61-v*` directory. |
| C-API status | Bound normatively in §A.4 and Appendix B (no longer by reference to history): CAPI5R ENDORSED_WITH_REQUIRED_CHANGES (V5-RC4-GATE-EXCEPTION, V5-RC4-QUAL-CAPTURE); CAPI6R ENDORSED, those two and V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 CLOSED_AT_DESIGN_LEVEL only; ROOT_WORKER_INTEGRATION "OPEN; no ruling on the other lane or integration order". The PK-0 packet under `WT/packets/capi-pk0/` was not read. |
| Scope | Design only, for the draft lane `W/work/protected-original-root-worker-repair-v1` (status `INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY`). The lane draft is someone else's unreviewed source and was not touched. v7 grants no execution, proof, build, test, review, operator or acceptance authority, and adds no approval gate. |
| Location | `WT/designs/claude-root-worker-seam-design-v7/` |
| **What this document consists of** | v7 is (1) the text of this file; (2) the v6 `SEAM-DESIGN.md` line ranges listed in §B.1 (slices C6-…), each bound by the sha256 of its exact bytes, with the quoted replacements R7-1 … R7-86 of §B.2 applied; (3) transitively, everything those v6 slices carry: slice C6-B is v6's own §B, so the v5 slices it binds (C5-…) with R6-1 … R6-29, and through them the v4, v3, v2 and v1 chains, minus v5's withdrawals W5-1 and W5-2. Every other v6 text is superseded by the map of §B.3. Every identity a normative statement relies on is bound in Appendix B of this file, and every ruling's owner and evidence requirement is stated in §A.3 of this file. |
| Companion files | `seams.json` (machine twin), `jackal.json` (JACKAL record), `AUTHOR-NOTES.md` (process record, sweep record, uncertainties, deviations). Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools. Bash was used for read-only inspection, with the deviations recorded in AUTHOR-NOTES §5. |

Every statement about source is **static**: read from files, or reasoned from what was read. Nothing was compiled, run, imported, proved, tested or measured. Kernel, systemd, SQLite, interpreter and Ada-visibility statements marked **[unverified reasoning]** are the author's reading and name their evidence item.

---

## A. Closure tables

"Answer" is a design statement for the reviewer. The author closes nothing. Every proof, native, control, physical and acceptance obligation stays OPEN.

### A.1 Required changes V6-REQ-A … V6-REQ-L

Each change is quoted verbatim from the sealed `review.json` `required_changes[].change`.

| Id | Required change (verbatim) | v7 answer | Where |
|---|---|---|---|
| V6-REQ-A | "Disambiguate material layout (count vs digest 'm'; material kind vs layout record kind; decide_v2 roster); extend output-capacity rule to every successor Next writes (generation, Reattach_Epoch, sub-generations); replace carried D5:1493 (WL_ABI_CAPACITY, stride) by quotation; state X-5 fold's no-Input T variant." | The material's parameter count is `param_count`; `m` names only the SHA-256 digest. The material's per-parameter kind is `slot_kind` (record, arena, roster); the layout's record-kind index is `record_kind`. The `decide_v2` roster is V1's `PARAMETERS` with `FactsV2` and `Selection` inserted, in that order, immediately before `Output`. The capacity rule covers every span field `next` and `fold` write, every successor included (generation g+1, `Reattach_Epoch` n, sub-generation s+1), by sizing from the largest input span plus one byte per output span field. D5:1493 is replaced by quotation. `fold` is T with no Input record, stated in the export table. | V7-A; R7-27, R7-43 … R7-48 |
| V6-REQ-B | "Correct V6-B: the root unit properties are the root-worker plan's worker_policy admitted under the WL reservation, not the WL request's plan." | Corrected by quotation: the root unit's properties are `worker_policy`'s `unit_properties ()` (`rw/root_worker_plan.py:22`, `:37`), admitted at DISPATCH under the WL reservation (`rw/protected_root_resource.py:38`, `:50-51`, `:68-71`); only the catalogue `cost_key` is the WL operation's (`:39-41`). CG-2 is unchanged. | V7-B; R7-49 |
| V6-REQ-C | "Replace carried D5:566 (S10 'a selected specification needs D-4a') by quotation consistent with CG-3 and V6-K.4; state CG-4's closure independence from D-4a." | S10 is replaced by quotation with no D-4a dependence; CG-4's closure condition is stated independent of D-4a. The full sweep found and replaced three further carried D-4a dependences (v2:1363, v2:1909, v4:427). | V7-C; R7-1, R7-2, R7-6, R7-17, R7-73 |
| V6-REQ-D | "Remove result='oom-kill' from the dispatcher outcome (original never returns it); route OOM via telemetry oomKilled; restate CJ-DISP-4 to cover persisted supervision fields and messages; fix the V6-D lab control." | `result` takes only the original's values (`stopped`, `failure`, `success`, `None`). An OOM kill reaches the runner through `resource_telemetry`'s `oomKilled` and `hitMemoryCeiling`, from the leaf's `memory.events`, as the original's sampled telemetry does. CJ-DISP-4 lists every persisted field and message (`rw/runner.py:944-950`, `:967`, `:982`, `:986`), equal or different. The control is fixed. | V7-D; R7-53 … R7-56, R7-75 |
| V6-REQ-E | "Give X-1 a per-caller mode equal to exact_json's canonical_required; add the lenient-mode refusal table (overflow -> inf accepted; NaN -> STARTUP_NONFINITE_JSON; duplicates); require CJ-JSON per mode so SOURCE_JSON_NATIVE_DISAGREES is unreachable for any Python-accepted input; add the int max-str-digits ValueError row (RC-5)." | `JsonInput.mode` (Canonical, Lenient) equals the call site's `canonical_required`; every caller is listed with its mode. Both refusal tables are given; Lenient accepts overflow as an infinity, refuses `NaN` tokens with `STARTUP_NONFINITE_JSON` and duplicates with `STARTUP_DUPLICATE_JSON_KEY`; both modes carry the integer-digit-limit `ValueError` row. CJ-JSON is stated per mode, so the disagreement refusal is reachable only through a false CJ-JSON. | V7-E (supersedes V6-E.4); R7-16, R7-85 |
| V6-REQ-F | "Replace RT-25..RT-27 (D5:1071-1073) and OWN-1 (D5:1000) evidence by quotation with worker-gone/E-CR; read the init start tick while holding the HELD-frame init pidfd and confirm the pairing; record boot identity with start ticks." | RT-25 … RT-27 and OWN-1 are replaced by quotation (worker gone, or E-CR). The sweep also replaced the pidfd-only evidence of RT-13 (v5:278), the UNKNOWN routing row (v5:294) and "Finding the worker" (v5:1478). The init start tick is read while the HELD frame's init pidfd is held, with the fdinfo pairing and a liveness check after the read. The boot identity is recorded at HELD and in `EXECUTION_NATIVE`; a different boot identity is identity-gone evidence (K-29, OP-7). | V7-F; R7-12, R7-13, R7-21, R7-23 … R7-26, R7-33 … R7-35, R7-57 … R7-59, R7-61, R7-76, R7-86 |
| V6-REQ-G | "Make the C-APPEND route non-circular (RECONCILED then a Legal re-append, or a replay hit); align R6-19, R6-24 and V6-G.2 on cause classes; make the cause class an X-5 operand; drop 'as in the original'." | C-APPEND: `RECONCILED` to `Before_Unknown` on the verified chain; then either the replay hit stands (the event persisted) or the phase owner re-appends it under `Legal`. R6-19's and R6-24's results and V6-G.2 now give the same per-class routes. The cause record is an X-5 operand (`EvidenceRec` kind `Cause_Record`, joined to `unknown_cause`); no column is added, so 04.3 stays closed. "as in the original" is replaced by a stated difference. | V7-G; R7-36, R7-38, R7-43, R7-60 … R7-63 |
| V6-REQ-H | "Specify the front's in-memory phase after HANDOFF_ABORT, replacing the unconditional UNKNOWN_WORKER_OWNERSHIP at rw/protected_root_worker.py:192 so FRONT_OWNED(g+1) serves; qualify Release_Hold to Held_Capacity rows." | `:192` is replaced: with owners open, the front's in-memory phase becomes `FRONT_OWNED` together with the committed `FRONT_OWNED (g+1)`, so `:159` and the router's `:22` pass; with owners closed, a reconstruction task is registered in `front.collectors`, which the router awaits; `UNKNOWN_WORKER_OWNERSHIP` remains only while the custody chain is Unknown. `Release_Hold` applies only to a `Held_Capacity` root row; an `Irreversible_Budget` row has no never-launched command and keeps its state for owner resolution. | V7-H; R7-4, R7-5, R7-19, R7-20, R7-22, R7-64, R7-65, R7-77 |
| V6-REQ-I | "Branch (a) must not raise while the front may be alive (relay_frame failure, channel-only loss): wait for reattach and raise only on authenticated client-gone evidence; specify frame order and request re-derivation in the custody owner." | On any transport loss the worker waits, with no deadline, for a reattach. The reattached front answers each (g, r, s) with an authenticated `PEER_STATUS`: `PEER_HELD` (it holds the request's connection; the gate is re-issued) or `PEER_LOST_WITH_FRONT` (the front that held it is gone by the identity test of V7-F.2). Only the second leads to branch (a) or (b). One output sequence per (g, r, s) orders `PROGRESS_BYTES` and `RESPONSE_BYTES`. The custody owner re-derives `id`, `op` and `args` by the same parse code over the recorded line bytes. | V7-I; R7-29, R7-37, R7-66 … R7-70, R7-78 |
| V6-REQ-J | "Fix the factory's fork point before C1:323, or give an explicit close-all-except list; add a control that F holds no owner/custody/actor/go/report/out/err/stdin descriptor." | Both: F is forked after argument validation (`C1:308-322`) and before `connect_owner` (`C1:323`), and at entry F closes everything except descriptors 0, 1, 2 and its own socketpair end. Control V7-N.J. | V7-J; R7-71, R7-72 |
| V6-REQ-K | "Add the request-root launch delta for launches while the coordinator owns custody; fix the request root's policy source; mark AO-9 (and AO-5) as part until designed; list every resource-policy field and show each unchanged before treating adoption as the lead's call." | D-H7 designs the request-root launch while the coordinator owns custody: the coordinator's root helper executes the request root's `systemd-run` (helper command `LAUNCH_REQUEST_ROOT`). The policy source is the WL operation's own launch plan's `policy` (`rw/protected_operations.py:476`, `:687`), as `launch_reserved` enforces it (`rw/protected_scoped_resource_runtime.py:729-731`). AO-5 and AO-9 are "part" until D-H7 is reviewed. Every `ResourcePolicy` field is listed; each is unchanged against the original. Non-field differences are listed too. H′ is not adopted. | V7-K (supersedes V6-K); R7-28, R7-30, R7-39, R7-50, R7-51, R7-79, R7-83 |
| V6-REQ-L | "Re-bind the CAPI5/CAPI6 APPENDIX-BINDINGS and CAPI5R/CAPI6R identities in Appendix B; restate or bind the ruling owners and evidence normatively; resolve the RC-10 name collision; replace the dangling G-comparison reference; correct D6:83." | Appendix B binds every identity, CAPI included. §A.3 states every ruling's owner and evidence requirement verbatim and normatively. The installed-runtime checks RC-10, RC-11 and RC-12 are renamed RC-13, RC-14 and RC-15 by quotation everywhere they appear; the inherited required changes keep RC-01 … RC-12. The options comparison (A … G) is restated normatively in V7-K.6. D6:83's description is corrected in §A.4. | V7-L; §A.3, §A.4, §C.5, Appendix B |

### A.2 Status after the v6 review

From `review.json` `rc_closure`: V5-REQ-B, H, L and M CLOSED_AT_DESIGN_LEVEL (carried unchanged, §A.4); V5-REQ-A, C, D, E, F, G, I, J and K PARTIALLY_CLOSED, each answered by the V6-REQs the review maps to it. V4-REQ-H "CLOSED_AT_DESIGN_LEVEL (carried verbatim; conditional on V6-REQ-J keeping factory free of pipe ends)" and V4-REQ-K "CLOSED_AT_DESIGN_LEVEL (carried verbatim; CAPI identity pins must be re-bound, V6-REQ-L)".

The 20 PARTIALLY_CLOSED clauses, with the review's remaining gap quoted verbatim from REVIEW.md's clause table:

| Clause | Remaining gap (verbatim) | v7 answer |
|---|---|---|
| 01.1 | "V6-REQ-A" | V7-A |
| 01.5 | "D_prod coverage OPEN (unchanged)" | Stays OPEN as an obligation; nothing in v7 claims D_prod coverage |
| 01.7 | "RQ-1 proofs and controls absent; CG-2 and CG-3 are stated correctly" | Unchanged: proofs and controls stay OPEN; V7-B corrects CG-2's basis |
| 02.1 | "V6-REQ-E (lenient request-document mode)" | V7-E |
| 02.2 | "P-A1 … P-A4 (unchanged)" | Unchanged: P-A1 … P-A4 stay OPEN obligations |
| 02.3 | "Costs OPEN" | Costs stay OPEN |
| 02.4 | "V6-REQ-K" | V7-K |
| 03.2 | "V6-REQ-J" | V7-J |
| 03.3 | "CG-1; V6-REQ-D" | V7-D; CG-1 stays OPEN |
| 04.1 | "V6-REQ-G, V6-REQ-H" | V7-G, V7-H |
| 04.4 | "V6-REQ-F" | V7-F |
| 06.2 | "V6-REQ-K" | V7-K |
| 06.3 | "Never-reattach stays OPEN (stated, D6:342)" | Unchanged; stays OPEN |
| 06.4 | "CG-3 OPEN; V6-REQ-C" | V7-C; CG-3 stays OPEN |
| 07.3 | "V6-REQ-H (:192 wedge)" | V7-H |
| 09.2 | "V6-REQ-I" | V7-I |
| 09.5 | "V6-REQ-G; C-EVIDENCE has no liveness" | V7-G; C-EVIDENCE's liveness stays OPEN |
| 11.1 | "X-5 capacity rule (V6-REQ-A)" | V7-A.2 |
| 12.2 | "V6-REQ-F, V6-REQ-H" | V7-F, V7-H |
| 12.4 | "V6-REQ-F, V6-REQ-G" | V7-F, V7-G |

Clauses 04.3 and 12.1 are now CLOSED_AT_DESIGN_LEVEL (`clause_closure`); v7 adds no `RootStateRec` field or root_state column (V7-G.1), so both stay as the review closed them. 09.4: "CLOSED_AT_DESIGN_LEVEL (carried; its condition is met only after V6-REQ-I: branch (a) must not raise while the front may be alive)" — V7-I meets that condition at design level. 07.1: "CLOSED_AT_DESIGN_LEVEL (carried; D6:83 description of the R6-15..R6-20 changes to be corrected, V6-REQ-L)" — corrected in §A.4.

### A.3 Rulings, stated normatively

Each ruling, owner and evidence requirement is quoted verbatim from the sealed v6 `review.json` `rulings[]`. This table is normative in v7: the owners and evidence requirements bind here, not through any superseded text. Where an owner or carried text names a GPT-6.1 review, the sealed review reads it as follows (REVIEW.md, verbatim): "\"Independent GPT-6.1 reviewer\" reads as \"independent Claude review subagent\" under the 17:05Z direction (WT/STATUS.md:279-292)." v7 does not decide that reading; it records it.

| Ruling | Ruling (verbatim) | Owner (verbatim) | Evidence required (verbatim) | v7 answer |
|---|---|---|---|---|
| D-1a | "PARTIALLY_CLOSED; V6-REQ-A, V6-REQ-B" | "Lead source designer; independent reviewer (Claude review subagent under the 2026-10-05 17:05Z direction)" | "Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls." | V7-A, V7-B |
| D-1b | "PARTIALLY_CLOSED; V6-REQ-B, V6-REQ-C" | "Lead scoped model/caller designer; independent reviewer" | "Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof." | V7-B, V7-C |
| D-2a | "PARTIALLY_CLOSED; V6-REQ-A, V6-REQ-E" | "Lead authors schema/callers; operator provisions or installs authoritative state" | "Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls." | V7-A, V7-E |
| D-2b | "CLOSED_AT_DESIGN_LEVEL (carried by C2-116)" | "Lead prepares concrete equivalence/adoption package; applicable operator authority; independent review" | "Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit." | Carried unchanged (§A.4) |
| D-3a | "PARTIALLY_CLOSED; lab evidence OPEN; V6-REQ-J protects the carried V4-REQ-H closure" | "Lead protocol designer; operator for lab execution" | "Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection." | V7-J; lab evidence stays OPEN |
| D-4a | "PARTIALLY_CLOSED; V6-REQ-C, V6-REQ-K" | "Lead prepares native accounting comparison; independent review; operator selects any authoritative resource-policy change" | "Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls." | V7-C, V7-K |
| D-5a | "PARTIALLY_CLOSED; V6-REQ-A, V6-REQ-D, V6-REQ-J" | "Lead prepares native/OS design; independent review; operator for delegation and privileged lab action" | "Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls." | V7-A, V7-D, V7-J |
| D-5b | "PARTIALLY_CLOSED; V6-REQ-J" | "Lead helper designer; independent review; operator for privileged execution/installation" | "Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations." | V7-J |
| D-6a | "PARTIALLY_CLOSED; V6-REQ-F, V6-REQ-H" | "Lead historical/canonical model designer; independent review" | "Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement." | V7-F, V7-H |
| D-7a | "PARTIALLY_CLOSED; V6-REQ-E" | "Lead native/provenance designer; child-authority and independent re-review; operator for any original API/owner-policy alteration" | "Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation." | V7-E |
| D-8a | "PARTIALLY_CLOSED; V6-REQ-I" | "Lead OS/native requester designer; independent review" | "Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage." | V7-I |
| D-8b | "PARTIALLY_CLOSED; V6-REQ-F, V6-REQ-I, V6-REQ-J; measurements stay with the operator under OP-7" | "Lead prepares domain-preserving protocol; operator for kernel measurement; independent review" | "Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client." | V7-F, V7-I, V7-J; K-29 joins OP-7 by the same range repair |
| D-9a | "PARTIALLY_CLOSED; V6-REQ-A, V6-REQ-F, V6-REQ-G, V6-REQ-H" | "Lead additive SPARK relation and caller designer; independent review; operator for fault campaign" | "Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes." | V7-A, V7-F, V7-G, V7-H |

D-3a is not closed: its lab and physical evidence stays OPEN. No ruling's owner or evidence requirement is changed by v7.

### A.4 Carried exactly as the review closed them

Nothing below is changed by v7, except where an R7 is named, and then only as stated.
- **V5-REQ-B (CLOSED_AT_DESIGN_LEVEL):** V6-B, carried as C6-VB. R7-49 makes the factual correction the review required (V6-REQ-B); the gap, its closure condition and its control are unchanged. R7-50 replaces only the claim that H′ meets the condition (V6-REQ-K).
- **V5-REQ-H (CLOSED_AT_DESIGN_LEVEL):** V6-H, carried as C6-VH. R7-64 qualifies `Release_Hold` and R7-65 replaces the `:192` wedge, the two items the review attached to it (V6-REQ-H). The launch order and the phase-conditional append are unchanged.
- **V5-REQ-L (CLOSED_AT_DESIGN_LEVEL):** R6-1, R6-4, R6-5 and R6-8 inside C6-B, and V6-L inside C6-VL; R7-73 adds CG-4's independence from D-4a (V6-REQ-C).
- **V5-REQ-M (CLOSED_AT_DESIGN_LEVEL):** K-27 as narrowed (R6-27) and V6-M; the loader check is renamed RC-14 (R7-40, R7-74, R7-80), with no change of content.
- **V4-REQ-H (CLOSED_AT_DESIGN_LEVEL):** v5 V5-H, carried verbatim as slice C5-VH through C6-B. No R7 targets it. Its condition, the factory holding no pipe end, is met by V7-J. K-25 and OP-7 lab evidence stay OPEN.
- **V4-REQ-K (CLOSED_AT_DESIGN_LEVEL) and the C-API integration:** v5 V5-K, carried verbatim as slice C5-VK through C6-B. No R7 targets it. Its CAPI identities are bound in Appendix B of this file: CAPI5 `APPENDIX-BINDINGS.md` `f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2` and CAPI6 `APPENDIX-BINDINGS.md` `9f9f3dfa897d0c320226df39c89bc5c156fc87ebc3e24959ab0c08bba5db1946` (recomputed), and the CAPI5R and CAPI6R review identities (recorded; see Appendix B for why they were not recomputed). Implementation, stage reviews and IC-10 stay OPEN.
- **The CLOSED_AT_DESIGN_LEVEL clauses** (`clause_closure`, "other_37_closed" with 04.3, 12.1, 09.4 and 07.1): their text is carried in the slices that held it.
  - **09.4** stays closed only if branch (a) never raises while the front may be alive, which V7-I meets.
  - **07.1, corrected description (V6-REQ-L).** v6's §A.4 (D6:83) said the R6-15 … R6-20 changes "only add conditions to existing rows". That was inaccurate. Exactly: R6-15 and R6-16 add conditions and record content to existing rows; R6-17 makes `WORKER_REATTACHED` legal in one more phase (Unknown with a worker `Before_Unknown`); R6-18 and R6-20 add an **alternative** evidence (the restarted-front regime) to `CUSTODY_RETURNED` and XC-4; R6-19 adds a **target** (`Before_Unknown`) to `RECONCILED`. v7's R7-36 (R6-19's result) adds the per-class routes of V7-G, and R7-35 (R6-16's result) adds record content. No relation row, cross-condition or C×P rule is removed, and every added path ends in a phase the relation already had.
  - **04.5**'s outer test (C4-VG23, R4-30) is unchanged.
- **D-2b (CLOSED_AT_DESIGN_LEVEL),** carried by C2-116 through C6-B; `frontier_sha256` `a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb`. No R7 targets C2-116, and the frontier control is unchanged.
- **R6-1 … R6-29,** which the review found exact, are carried inside C6-B. Eight R7s (R7-33 … R7-40) change the `v6:` result lines of R6-2, R6-3, R6-16, R6-19, R6-23, R6-24, R6-25 and R6-27 (RR7-4); none changes an R6's `v5:` or `v4:` text.
- **Operator items:** OP-1 … OP-9 within their reserved scope, unchanged. K-29 joins OP-7's existing D-8b reservation by the same range repair as K-22 … K-28 (R7-33, R7-34). No operator item is added, lowered or widened; no approval gate is added.

### A.5 The review's other concerns

| Concern (REVIEW.md) | v7 answer | Where |
|---|---|---|
| "Release_Hold scope" | Held_Capacity only; Irreversible_Budget rows keep their state | V7-H.2 |
| "R2 identity. It should record the boot identity (K-4)." | Recorded at HELD and in `EXECUTION_NATIVE`; K-29 | V7-F |
| CG-4: "seams.json has no depends_on_d4a field for CG-4" | `seams.json` now records `depends_on_d4a: false` for every gap | V7-C; `seams.json` |
| "the m and kind collisions" | `param_count`, `m`, `slot_kind`, `record_kind` | V7-A.1 |
| "\"RC-10\" names both the inherited, closed required change … and the open installed-runtime check" | Installed checks renamed RC-13 … RC-15 | §C.5 |
| "D6:779 points G's comparison at superseded history" | Restated normatively | V7-K.6 |
| AO-5 depends on the holder-mode root's policy | The request's own plan policy | V7-K.3 |

---

## B. What v7 carries from v6, and how to read it

### B.1 Bound v6 slices

- v6 `SEAM-DESIGN.md` has 990 lines and ends with a newline (observed). Its whole-file sha256 is `f41566d8bb694817f27efb4dd336d25e554357976808aad577b91365a9a10787`.
- Each slice's sha256 is that of the UTF-8 bytes of its lines, each followed by `\n`. A read-only script computed them (Appendix C).
- CARRIED_VERBATIM slices are part of v7 exactly. CARRIED_WITH_LINE_REPLACEMENTS slices are part of v7 with the listed lines replaced by the §B.2 text. Slice C6-B is v6's §B; it carries v5 through its own slice table (C5-…) with R6-1 … R6-29, and through C5-B the v4, v3, v2 and v1 chains, so an R7 may also replace a line of an earlier version inside a slice that chain carries, or a line of an R6 block's `v6:` text (RR7-4).

| Slice | v6 lines | sha256 | Disposition | Content |
|---|---|---|---|---|
| C6-B | 117-409 | `a7611b3cd4910c785846f0f93769a5c21ef199a555da69ccc34f76c7057f1953` | CARRIED_WITH_LINE_REPLACEMENTS (R7-33 … R7-42), and through it R7-1 … R7-32 and R7-86 | v6 §B: the C5 slice table, R6-1 … R6-29, v6's map and reading rules |
| C6-VA | 449-518 | `fb86cd5637a41f8f55b3d5fa7583286f4575e04619e9dc832974582e2adc95fd` | CARRIED_WITH_LINE_REPLACEMENTS (R7-43 … R7-48) | V6-A: conventions, export table, material, `RootStateRec` |
| C6-VB | 521-533 | `16f11877aa50016b4435afbbd46113e5f804fea787484d0ab2add404aeb2e0b6` | CARRIED_WITH_LINE_REPLACEMENTS (R7-49, R7-50) | V6-B: CG-2 |
| C6-VC | 536-546 | `7db1c226b4340bac273ad40950e64959e8dd94aac9669ae3229d4bda4f548379` | CARRIED_WITH_LINE_REPLACEMENTS (R7-51) | V6-C: CG-3 |
| C6-VD | 549-575 | `1e0ac708015611b61b9c797d53c6f3f5ceb1dafc0f88df1006c29e3666a69fab` | CARRIED_WITH_LINE_REPLACEMENTS (R7-52 … R7-56) | V6-D: the dispatcher |
| C6-VE | 578-614 | `9accc3431095341d3c1387b5781aa47df646e73465041929c42bf68a2b050d57` | CARRIED_VERBATIM | V6-E.1 … V6-E.3: archive encoding, comparison, costs |
| C6-VF | 632-668 | `30a9a83442d278150ac6f6c8898e6176b0c69a521a9d6e864cbeb4b0cc2284f4` | CARRIED_WITH_LINE_REPLACEMENTS (R7-57 … R7-59) | V6-F: custody-return evidence, OB-ESC |
| C6-VG | 671-697 | `c97e35aaa09106a00a2640283afd63b723e0a44856cf6978bc72d79e4b153e92` | CARRIED_WITH_LINE_REPLACEMENTS (R7-60 … R7-63) | V6-G: Unknown back to service |
| C6-VH | 700-721 | `4c2c7a4986a0dd3c545d5d2225364d0fb8e9a5984ef9107fcc39cd617a40b46d` | CARRIED_WITH_LINE_REPLACEMENTS (R7-64, R7-65) | V6-H: `PREPARED` first, no-slot branch |
| C6-VI | 724-756 | `fae11ad33bd161e7665ce949634fb45bda69a8fec29b0480a111a0d450cf7385` | CARRIED_WITH_LINE_REPLACEMENTS (R7-66 … R7-70) | V6-I: transport loss, daemon steps, `PROGRESS_BYTES` |
| C6-VJ | 759-774 | `3c2e1144dc3e0bef26aa5f5b4f5b1f8bbd10b098b64fb318e5390f7896d0e1e4` | CARRIED_WITH_LINE_REPLACEMENTS (R7-71, R7-72) | V6-J: the child factory, K-28 |
| C6-VL | 818-829 | `d8816b982b2dfa28b18258ce542fde5471cfff11677292e2392bdee5583c9c20` | CARRIED_WITH_LINE_REPLACEMENTS (R7-73) | V6-L: CG-1, CG-4 |
| C6-VM | 832-837 | `4c3f1c7352e41598535522ea488ea6e303203d8ee1a3738dfe906731b410db02` | CARRIED_WITH_LINE_REPLACEMENTS (R7-74) | V6-M: K-27 split |
| C6-VNOPQ | 840-923 | `b237a140db76d0bbc8205fcb08304beb1d31b9e781b7c6289b029a72ab1bade5` | CARRIED_WITH_LINE_REPLACEMENTS (R7-75 … R7-85) | V6-N controls, V6-O measurements, V6-P open list, V6-Q non-claims |

### B.2 Line replacements

Each replacement quotes the exact earlier line, then gives the v7 text. For a line of an earlier version, the header names the slice that holds it and the chain that carries that slice. The reason names the required change or the sweep finding (V7-M).

**R7-1 replaces v2 line 1363 (in C2-92, carried by C3-B inside C4-B inside C5-B inside C6-B).** Sweep: D-4a dependence of later requests (V6-REQ-C's principle).
```text
v2:
An independent GPT-6.1 review follows. Any authoritative resource-policy change, for example coordinator container headroom backed by a new catalogue entry, is selected by the operator (D-4a). Until then, the root route serves later consequential requests only through the routing of §9.3, and their accepted cases stay OPEN.
v7:
An independent GPT-6.1 review follows. Any authoritative resource-policy change, for example coordinator container headroom backed by a new catalogue entry, is selected by the operator (D-4a). Later consequential requests do not wait for that selection: while a worker owns, a later WL request is queued for g+1 (OPEN containment gap CG-3, v6 V6-C) and an IP request is served by the custody owner on the serial route (v5 V5-B.5 as replaced by R6-9; OPEN containment gap CG-2, v6 V6-B). The closure conditions of CG-2 and CG-3 do not depend on D-4a, and their accepted cases stay OPEN.
```

**R7-2 replaces v2 line 1909 (in C2-153, carried by C3-B inside C4-B inside C5-B inside C6-B).** Sweep: D-4a dependence.
```text
v2:
- **v1 SL-9 (multiplexing)** depends on the seam-7 accounting (S3) and on the D-4a selection.
v7:
- **v1 SL-9 (multiplexing)** depends on the seam-7 accounting (S3) and on a route that meets the closure conditions of CG-2 and CG-3 (v6 V6-B, V6-C; the candidate H′ is v7 V7-K). Those conditions do not depend on D-4a; any authoritative resource-policy change a route would need stays the operator's under D-4a's existing reservation (OP-3).
```

**R7-3 replaces v3 line 660 (in C3-B, carried by C4-B inside C5-B inside C6-B).** Sweep: a reading rule pointed into superseded text (v3 §C.2).
```text
v3:
- **RR3-1.** Inside carried v2 slices, v2's aliases and notation apply (v2 §C.2, restated in §C.2 below).
v7:
- **RR3-1.** Inside carried v2 slices, v2's aliases and notation apply; v7 §C.2 restates them, with the version each applies to.
```

**R7-4 replaces v3 line 1424 (in C3-VG, carried by C4-B inside C5-B inside C6-B).** V6-REQ-H: `Release_Hold` applies only to `Held_Capacity`.
```text
v3:
| `Never_Dispatched`, no dispatch, no protocol or unit fact | `Never_Launched` (`Never_Holds`, `:96-102`) | `Release_Hold` (`core/resource_run_ledger.ads:319-320`) |
v7:
| `Never_Dispatched`, no dispatch, no protocol or unit fact | `Never_Launched` (`Never_Holds`, `:96-102`) | `Release_Hold` (`core/resource_run_ledger.ads:317-320`) for a `Held_Capacity` row; no command for an `Irreversible_Budget` row, which keeps its state, because `Release_Hold` requires `Held_Capacity` and `Charge_Budget` requires `Terminal` and `Reaped` (`:317-322`; v7 V7-H.2) |
```

**R7-5 replaces v3 line 1433 (in C3-VG, carried by C4-B inside C5-B inside C6-B).** V6-REQ-H.
```text
v3:
| PR-a (RT-1) | none or PREPARED | `Never_Dispatched` | RESERVED or EFFECT_INTENT | none | `Never_Launched` → `Release_Hold` | Release P. U follows the original restart path: a RESERVED row, or an EFFECT_INTENT row with neither a retained result nor a broker preparation, is unresolved (`rw/protected_operations.py:376`, `:383-384`) and goes to the owner, with quarantine and K4 as the original does | P automatic; U owner |
v7:
| PR-a (RT-1) | none or PREPARED | `Never_Dispatched` | RESERVED or EFFECT_INTENT | none | `Never_Launched` → `Release_Hold` for a `Held_Capacity` row; no command for an `Irreversible_Budget` row (v7 V7-H.2) | Release P when the row is `Held_Capacity`; an `Irreversible_Budget` row keeps its state and budget for the owner. U follows the original restart path: a RESERVED row, or an EFFECT_INTENT row with neither a retained result nor a broker preparation, is unresolved (`rw/protected_operations.py:376`, `:383-384`) and goes to the owner, with quarantine and K4 as the original does | P automatic; U owner |
```

**R7-6 replaces v4 line 427 (in C4-B, R4-25's result; carried by C5-B inside C6-B).** Sweep: D-4a dependence, and a reference to superseded V4-D.2.
```text
v4:
No option is selected. The comparison, completed in v4 V4-D.2, is ready for independent review. Any authoritative policy change is the operator's selection (D-4a), and none may raise an admitted outer bound, borrow the first root's grant, add a cap or provider prerequisite, or accept a native failure. Until a selection exists, later consequential requests on the root route are served by the routing of C2-93 as amended by v4 V4-I.5 and V4-L, and their accepted cases stay OPEN.
v7:
No option is selected. The comparison of options A … H′ is restated in v7 V7-K.6. Any authoritative policy change is the operator's selection (D-4a), and none may raise an admitted outer bound, borrow the first root's grant, add a cap or provider prerequisite, or accept a native failure. Later consequential requests do not wait for a selection: while a worker owns, a later WL request is queued for g+1 (OPEN containment gap CG-3, v6 V6-C) and an IP request is served by the custody owner (v5 V5-B.5 as replaced by R6-9; CG-2, v6 V6-B). The closure conditions of CG-2 and CG-3 do not depend on D-4a, and their accepted cases stay OPEN.
```

**R7-7 replaces v4 line 451 (in C4-B, R4-28's result; carried by C5-B inside C6-B).** Sweep: a reference to superseded V4-D.2.
```text
v4:
| (withdrawn in v4) | v3's `SET_ROOT_CEILING` would raise an admitted outer bound; no helper command changes an admitted bound (v4 V4-D.2, AO-5) | — |
v7:
| (withdrawn in v4) | v3's `SET_ROOT_CEILING` would raise an admitted outer bound; no helper command changes an admitted bound (AO-5 in C4-VD1; option F's row as restated in v7 V7-K.6) | — |
```

**R7-8 replaces v4 line 774 (in C4-B, carried by C5-B inside C6-B).** Sweep: V4-A.5's body nodes had no live successor.
```text
v4:
| 1891-1949 | V-M dependency graph | V4-A.5 |
v7:
| 1891-1949 | V-M dependency graph | V4-A.5, itself superseded: its spec nodes and order by v5 V5-A.6, its body and caller nodes and its gates by v7 V7-L.3 |
```

**R7-9 replaces v4 line 782 (in C4-B, carried by C5-B inside C6-B).** Sweep: a reading rule pointed into superseded text (v4 §C.2).
```text
v4:
- **RR4-1.** Inside carried v3 slices, v3's reading rules RR3-1 … RR3-8 (in C3-B, with R4-17) apply, and the aliases are those of v4 §C.2.
v7:
- **RR4-1.** Inside carried v3 slices, v3's reading rules RR3-1 … RR3-8 (in C3-B, with R4-17 and R7-3) apply, and the aliases are those that v7 §C.2 restates for v3 text.
```

**R7-10 replaces v4 line 783 (in C4-B, carried by C5-B inside C6-B).** Sweep: V-M mapped to V4-A.5, whose body nodes had no live successor.
```text
v4:
- **RR4-2.** A reference inside a carried slice to a superseded v3 section resolves through §B.3: V-F.3's C×P rules → V4-F.3; V-F.4 → V4-F.5; V-F.6 → V4-F.6; V-H.3 → V4-H.4; V-I.2 and V-I.3 → V4-I.1 … V4-I.3; V-I.6 → V4-I.5; V-I.7 → V4-I.6; V-K.1 → V4-K.1; V-K.4 → V4-K.2; V-L.2 → V4-L.1; V-L.4 and V-L.5 → V4-L.2 and V4-L.3; V-M → V4-A.5; V-P → V4-O. A reference to a carried section means that slice with its R4 replacements.
v7:
- **RR4-2.** A reference inside a carried slice to a superseded v3 section resolves through §B.3: V-F.3's C×P rules → V4-F.3; V-F.4 → V4-F.5; V-F.6 → V4-F.6; V-H.3 → V4-H.4; V-I.2 and V-I.3 → V4-I.1 … V4-I.3; V-I.6 → V4-I.5; V-I.7 → V4-I.6; V-K.1 → V4-K.1; V-K.4 → V4-K.2; V-L.2 → V4-L.1; V-L.4 and V-L.5 → V4-L.2 and V4-L.3; V-M → v5 V5-A.6 (spec nodes and order) and v7 V7-L.3 (body and caller nodes and gates); V-P → V4-O. A reference to a carried section means that slice with its R4 replacements.
```

**R7-11 replaces v4 line 1832 (in C4-VMNOP, carried by C5-B inside C6-B).** Sweep: the list named superseded tables.
```text
v4:
- **Design tables to review:** V4-B.2, V4-B.6, V4-D.2, V4-E.1, V4-E.2, V4-E.4, V4-F.2, V4-F.5, V4-G.4, V4-H.4, V4-I.4, V4-J.2, V4-K.2 and V4-L.2.
v7:
- **Design tables to review:** V4-B.2 (C4-VB14), V4-E.4 (C4-VE4) and V4-J.2 (C4-VJ12), carried; and the live successors of the v4 tables later superseded: v5 V5-B.5 (the windows that replace V4-B.6's rollover table), v7 V7-K.6 (V4-D.2), v5 V5-E.1 and V5-E.2, v5 V5-F.2 and V5-F.5, v5 V5-G.4, v5 V5-H.4, v5 V5-I.4, v5 V5-K.2 and v5 V5-L.2, each as carried with its replacements.
```

**R7-12 replaces v5 line 278 (in C5-B, R5-7's result, RT-13; carried by C6-B).** V6-REQ-F sweep: pidfd-only evidence.
```text
v5:
| RT-13 | UNKNOWN; worker possibly alive | — | any | — | none | Wait for authentic evidence: the worker's reattachment (v5 V5-L.3), or the worker and namespace-init pidfds terminal (`CUSTODY_RETURNED`, v5 V5-F.2). Never stop on EOF, a deadline or the reconciler's own initiative. Only the custody owner's own original failure capture, or its original `job.cancel` handler, stops, per M8 (a) (v5 V5-F.5; v4's M8 (c) is withdrawn). A stop never settles or releases, and every hold stays | Automatic retain |
v7:
| RT-13 | UNKNOWN; worker possibly alive | — | any | — | none | Wait for authentic evidence: `RECONCILED` by the route of the cause class (v7 V7-G.2; for C-CHANNEL and C-DEADLINE, the worker's reattachment, v5 V5-L.3), or evidence E-CR (`CUSTODY_RETURNED`, v5 V5-F.2 as replaced by R6-18; v6 V6-F with v7 V7-F). Never stop on EOF, a deadline or the reconciler's own initiative. Only the custody owner's own original failure capture, or its original `job.cancel` handler, stops, per M8 (a) (v5 V5-F.5; v4's M8 (c) is withdrawn). A stop never settles or releases, and every hold stays | Automatic retain |
```

**R7-13 replaces v5 line 294 (in C5-B, R5-9's result, UNKNOWN routing; carried by C6-B).** V6-REQ-F and V6-REQ-G sweep.
```text
v5:
| UNKNOWN(cause) | Queued. No process mutates the store. No QUEUED event is sent (v5 V5-L.4). | Queued until a store-custody owner serves it with the original handler: the reattached worker (v5 V5-L.3) or the front of g+1. v4's M8 (c) front stop is withdrawn (v5 V5-F.5) | Queued | Queued | **Reconciler**: native redecision from durable custody, operation and physical evidence (§6.2). A worker that may still own state is never stopped on the reconciler's own initiative, on EOF or on a deadline (§6.6 with R4-48 as replaced by R5-8). The wait ends at the worker's reattachment (v5 V5-L.3), at `CUSTODY_RETURNED` once the worker and namespace-init pidfds are terminal, or at collection (v5 V5-F.2). Use uncertainty then goes to K4 through `quarantine.resolve` on the front of g+1 (CD-2). |
v7:
| UNKNOWN(cause) | Queued. No process mutates the store. No QUEUED event is sent (v5 V5-L.4). | Queued until a store-custody owner serves it with the original handler: the reattached worker (v5 V5-L.3) or the front of g+1. v4's M8 (c) front stop is withdrawn (v5 V5-F.5) | Queued | Queued | **Reconciler**: native redecision from durable custody, operation and physical evidence (§6.2). A worker that may still own state is never stopped on the reconciler's own initiative, on EOF or on a deadline (§6.6 with R4-48 as replaced by R5-8). The wait ends at `RECONCILED` by the route of the cause class (v7 V7-G.2; for C-CHANNEL and C-DEADLINE, the worker's reattachment, v5 V5-L.3), at `CUSTODY_RETURNED` on evidence E-CR (v6 V6-F with v7 V7-F), or at collection (v5 V5-F.2). Use uncertainty then goes to K4 through `quarantine.resolve` on the front of g+1 (CD-2). |
```

**R7-14 replaces v5 line 401 (in C5-B, carried by C6-B).** Sweep: a reading rule pointed into superseded text (v5 §C.2).
```text
v5:
- **RR5-1.** Inside carried v4 slices, v4's reading rules RR4-1 … RR4-8 (in C4-B) apply, and the aliases are those of v5 §C.2.
v7:
- **RR5-1.** Inside carried v4 slices, v4's reading rules RR4-1 … RR4-8 (in C4-B, with R7-9 and R7-10) apply, and the aliases are those that v7 §C.2 restates for v4 text.
```

**R7-15 replaces v5 line 402 (in C5-B, carried by C6-B).** Sweep: V4-A.5's body nodes and V4-D.2 mapped to text that is no longer live.
```text
v5:
- **RR5-2.** A reference inside carried text to a superseded v4 section resolves through §B.3 to the v5 section with the same letter and number: V4-A.n → V5-A; V4-B.5, V4-B.6 → V5-B.5, V5-B.6; V4-C.2, V4-C.3 → V5-C.2, V5-C.3; V4-D.2 → V5-D.2; V4-E.1 … V4-E.3 → V5-E.1 … V5-E.3; V4-F.n → V5-F.n; V4-G.1, V4-G.4 → V5-G.1, V5-G.4; V4-H.1, V4-H.3, V4-H.4 → V5-H.1, V5-H.3, V5-H.4; V4-I.1, V4-I.2, V4-I.4 … V4-I.6 → V5-I.1, V5-I.2, V5-I.4 … V5-I.6; V4-J.3, V4-J.4 → V5-J.3, V5-J.4; V4-K.2, V4-K.3 → V5-K.2, V5-K.3; V4-L.n → V5-L.n. A reference to v3 V-F.5 resolves to V5-J.2 (W5-2), and one to C2-62's graph to V5-F.2 (W5-1).
v7:
- **RR5-2.** A reference inside carried text to a superseded v4 section resolves through §B.3 to the v5 section with the same letter and number: V4-A.n → V5-A, except V4-A.5's body and caller nodes and its integration and runtime gates → v7 V7-L.3; V4-B.5, V4-B.6 → V5-B.5, V5-B.6; V4-C.2, V4-C.3 → V5-C.2, V5-C.3; V4-D.2 → v7 V7-K.6; V4-E.1 … V4-E.3 → V5-E.1 … V5-E.3; V4-F.n → V5-F.n; V4-G.1, V4-G.4 → V5-G.1, V5-G.4; V4-H.1, V4-H.3, V4-H.4 → V5-H.1, V5-H.3, V5-H.4; V4-I.1, V4-I.2, V4-I.4 … V4-I.6 → V5-I.1, V5-I.2, V5-I.4 … V5-I.6; V4-J.3, V4-J.4 → V5-J.3, V5-J.4; V4-K.2, V4-K.3 → V5-K.2, V5-K.3; V4-L.n → V5-L.n. A reference to v3 V-F.5 resolves to V5-J.2 (W5-2), and one to C2-62's graph to V5-F.2 (W5-1).
```

**R7-16 replaces v5 line 473 (in C5-VA, carried by C6-B).** V6-REQ-E: one mode per caller.
```text
v5:
- Records: (1) `JsonInput {container: Id; form: uint8 (UTF8, ASCII); trailing_lf: uint8 (Forbidden, One_Permitted)}`; (2) `PathStep {kind: uint8 (Key, Index); key: Id; index: Qty}`; (3) `NumberInput {lexeme: Id; form: uint8}`; (4) `ArchiveInput {container: Id; form: uint8; archive: Id}`; (5) `JsonResult {status: uint8; value: Id; value_kind: uint8 (Object, Array, String, Number, True_Lit, False_Lit, Null_Lit); failing_offset: Qty}`.
v7:
- Records: (1) `JsonInput {container: Id; form: uint8 (UTF8, ASCII, Detected); trailing_lf: uint8 (Forbidden, One_Permitted); mode: uint8 (Canonical, Lenient)}`, where `mode` is Canonical exactly when the call site's `canonical_required` is true (or the call site is `exact`), and `Detected` is the encoding detection `json.loads` applies to bytes (v7 V7-E.4); (2) `PathStep {kind: uint8 (Key, Index); key: Id; index: Qty}`; (3) `NumberInput {lexeme: Id; form: uint8}`; (4) `ArchiveInput {container: Id; form: uint8; archive: Id}`; (5) `JsonResult {status: uint8; value: Id; value_kind: uint8 (Object, Array, String, Number, True_Lit, False_Lit, Null_Lit); failing_offset: Qty}`.
```

**R7-17 replaces v5 line 566 (in C5-VA, carried by C6-B).** V6-REQ-C.
```text
v5:
| S10 | Multiplexing and accounting: alternatives, including H, drafted before D-4a; a selected specification needs D-4a (V5-D, V5-L) | S1, S3, S4, S7, S8, S9 |
v7:
| S10 | Multiplexing and accounting: the routes that close CG-2 and CG-3 (v6 V6-B, V6-C), with the candidate H′ (v7 V7-K) and the comparison of v7 V7-K.6. Neither the specification nor its completion depends on D-4a; an authoritative resource-policy change, if a route needed one, would stay the operator's under D-4a's existing reservation (OP-3), and none is proposed (v7 V7-K.7) | S1, S3, S4, S7, S8, S9 |
```

**R7-18 replaces v5 line 571 (in C5-VA, carried by C6-B).** Sweep: body nodes and gates were defined only in superseded V4-A.5.
```text
v5:
**Body nodes** are v4's (C4-B carries none of them; they were in V4-A.5) with these changes: B2H also implements the reattach handshake; B9 implements the three relations and `HANDOFF_ABORT` and `CUSTODY_RETURNED`; B-RECV implements the RELAY codec of V5-I.5; B4 implements the v2 helper protocol of V5-E.3; **B13** (new) implements the dispatcher of V5-B.6 and needs S13, B4, B6 and B9. B0, B3, B1, B2b, B2c, B6, B7, B10, B11 and B12 keep v4's content and needs. The integration gates G-CAPI, G-CAPI-P, G-PROT, G-RW, G-A1, G-DEP, G-REVIEW and the runtime gates R-PROOF, R-LAB, R-PUB are unchanged in meaning; none is an operator gate.
v7:
**Body nodes, integration gates and runtime gates** are restated in full in v7 V7-L.3: v4's (which no carried slice held) with v5's changes (B2H, B9, B-RECV, B4, and the new B13) and v6's and v7's changes applied. None is an operator gate.
```

**R7-19 replaces v5 line 905 (in C5-VF, carried by C6-B).** V6-REQ-H.
```text
v5:
| Handoff_Aborted | `HISTORICAL_SETTLEMENT` | Historical_Settlement | Front when `Owners_Open`, else Collector | the original exception path's U record (`QUARANTINED`, or SETTLED or RELEASED left as is, `rw/protected_operations.py:770-772`); for `Never_Dispatched`, `Release_Hold` committed |
v7:
| Handoff_Aborted | `HISTORICAL_SETTLEMENT` | Historical_Settlement | Front when `Owners_Open`, else Collector | the original exception path's U record (`QUARANTINED`, or SETTLED or RELEASED left as is, `rw/protected_operations.py:770-772`); for `Never_Dispatched`, `Release_Hold` committed when the root row is `Held_Capacity`, and no ledger command when it is `Irreversible_Budget` (v7 V7-H.2) |
```

**R7-20 replaces v5 line 920 (in C5-VF, carried by C6-B).** V6-REQ-H.
```text
v5:
| (no event) | `Released_Unlaunched` | Front | set by `HANDOFF_ABORT (Never_Dispatched)` with its `Release_Hold`; no CLOSED event is needed or legal |
v7:
| (no event) | `Released_Unlaunched` | Front | set by `HANDOFF_ABORT (Never_Dispatched)` with its `Release_Hold` when the root row is `Held_Capacity`; left unset for an `Irreversible_Budget` root row, which no command releases (v7 V7-H.2); no CLOSED event is needed or legal |
```

**R7-21 replaces v5 line 1000 (in C5-VF, carried by C6-B).** V6-REQ-F.
```text
v5:
**Lemma OWN-1** (statement, to prove over the relation): `Owner_Root` can change away from an actor only by an event that actor appends, or by `CUSTODY_RETURNED`, `ABANDON` or a Reconciler event, each of which needs evidence that the actor cannot act (its pidfds terminal) or has never owned (no `CUSTODY_ACK`). So a choke point that read the owner in one custody transaction cannot be overtaken by a concurrent change that would make its mutation illegal. **Choke-point audit AU-1** stays OPEN as in v4.
v7:
**Lemma OWN-1** (statement, to prove over the relation): `Owner_Root` can change away from an actor only by an event that actor appends, or by `CUSTODY_RETURNED`, `ABANDON` or a Reconciler event, each of which needs evidence that the actor cannot act (the actor gone: for `CUSTODY_RETURNED`, evidence E-CR of v6 V6-F with v7 V7-F; otherwise the worker gone as XC-4 states it after R6-20, its pidfd terminal while the front holds it or its identity gone after a front restart, v7 V7-F.2) or has never owned (no `CUSTODY_ACK`). So a choke point that read the owner in one custody transaction cannot be overtaken by a concurrent change that would make its mutation illegal. **Choke-point audit AU-1** stays OPEN as in v4.
```

**R7-22 replaces v5 line 1049 (in C5-VG, carried by C6-B).** V6-REQ-H.
```text
v5:
4. **P.** The original `Release_Hold` (`core/resource_run_ledger.ads:319-320`) for the root row, with no CLOSED_WITNESS (PR-a, r1′, r3′). No physical event of g is legal afterwards, because `Launched` was never set.
v7:
4. **P.** For a root row of kind `Held_Capacity`, the original `Release_Hold` with `Never_Launched` (`core/resource_run_ledger.ads:317-320`), with no CLOSED_WITNESS (PR-a, r1′, r3′). For a root row of kind `Irreversible_Budget`, no ledger command: `Release_Hold` requires `Held_Capacity` and `Charge_Budget` requires `Terminal` and `Reaped` (`:317-322`), so the row keeps its state and budget, as the original leaves it, for the owner resolution that step 5's U record leads to (v7 V7-H.2). No physical event of g is legal afterwards, because `Launched` was never set.
```

**R7-23 replaces v5 line 1071 (in C5-VG, carried by C6-B).** V6-REQ-F.
```text
v5:
| RT-25 | root Worker_Owned … Worker_Relinquish; worker dead after `REQUEST_INTAKE (r, s)` and before `REQUEST_RESPONDED` | worker pidfd terminal (XC-4) | `REQUEST_LOST (r, s)`; the request's operation row (if one was reserved in the worker) is recovered by RT-17 … RT-24 according to its U, after `CUSTODY_RETURNED` and reconstruction | per its U row | Automatic |
v7:
| RT-25 | root Worker_Owned … Worker_Relinquish; worker dead after `REQUEST_INTAKE (r, s)` and before `REQUEST_RESPONDED` | worker gone (XC-4 as replaced by R6-20: its pidfd terminal while the front holds it, or its identity gone after a front restart, v6 V6-F.2 with v7 V7-F.2) | `REQUEST_LOST (r, s)`; the request's operation row (if one was reserved in the worker) is recovered by RT-17 … RT-24 according to its U, after `CUSTODY_RETURNED` and reconstruction | per its U row | Automatic |
```

**R7-24 replaces v5 line 1072 (in C5-VG, carried by C6-B).** V6-REQ-F.
```text
v5:
| RT-26 | descriptor Released; worker dead | worker pidfd terminal | `DRAIN_RECLAIMED`. Outputs: reattach only if the front still holds a live read copy (V5-H.3); otherwise `OUTPUT_CUSTODY_LOST`, completeness UNKNOWN. Stdin: the worker's write copy is gone; W below the payload length is `STDIN_TRUNCATED` → UNKNOWN | — (no refusal; UNKNOWN is recorded) | Automatic |
v7:
| RT-26 | descriptor Released; worker dead | worker gone (XC-4 as replaced by R6-20; v7 V7-F.2) | `DRAIN_RECLAIMED`. Outputs: reattach only if the front still holds a live read copy (V5-H.3); otherwise `OUTPUT_CUSTODY_LOST`, completeness UNKNOWN. Stdin: the worker's write copy is gone; W below the payload length is `STDIN_TRUNCATED` → UNKNOWN | — (no refusal; UNKNOWN is recorded) | Automatic |
```

**R7-25 replaces v5 line 1073 (in C5-VG, carried by C6-B).** V6-REQ-F.
```text
v5:
| RT-27 | descriptor Intake, not yet Released; worker dead | worker pidfd terminal | `DRAIN_RECLAIMED`; the front closes its stdin write copy at once (EOF by V4-H.5) and reattaches outputs as RT-26 | — | Automatic |
v7:
| RT-27 | descriptor Intake, not yet Released; worker dead | worker gone (XC-4 as replaced by R6-20; v7 V7-F.2) | `DRAIN_RECLAIMED`; the front closes its stdin write copy at once (EOF by V4-H.5) and reattaches outputs as RT-26 | — | Automatic |
```

**R7-26 replaces v5 line 1478 (in C5-VL, carried by C6-B).** V6-REQ-F: boot identity.
```text
v5:
- **Finding the worker.** A front that has lost the channel (or a restarted front) reads the worker's host pid and start tick from the custody chain (the HELD and measured records), opens `pidfd_open (host_pid)`, and requires `/proc/<pid>/stat`'s start tick to equal the recorded one, so a reused pid is refused **[unverified reasoning, K-4]**.
v7:
- **Finding the worker.** A front that has lost the channel (or a restarted front) reads the worker's host pid, start tick and boot identity from the custody chain (the HELD and measured records, v7 V7-F.1). It requires the current boot identity to equal the recorded one, opens `pidfd_open (host_pid)`, and requires `/proc/<pid>/stat`'s start tick, read while that pidfd is held, to equal the recorded one, so a reused pid, or a pid of a later boot, is refused **[unverified reasoning, K-4, K-29]**.
```

**R7-27 replaces v5 line 1493 (in C5-VMNOP, carried by C6-B).** V6-REQ-A: `WL_ABI_CAPACITY` and "stride" were withdrawn by v6.
```text
v5:
- **V5-A** (static). Every new export's version and layout entries equal its wrapper's records (V5-A.1); a record with a field moved, a stride changed or a capacity too small gives `CoreUnavailable` or `WL_ABI_CAPACITY`, never a decision. Every existing export of V5-A.2 is byte-unchanged in the library's export table.
v7:
- **V5-A** (static). Every new export's version and layout entries equal its wrapper's records (v6 V6-A.1); a record with a field moved, or a triple whose total byte size disagrees with its element count, gives `CoreUnavailable`, never a decision. An output roster and output arena sized by the capacity rule of v7 V7-A.2 never give `Capacity_Short`. Every existing export of V5-A.2 is byte-unchanged in the library's export table.
```

**R7-28 replaces v5 line 1496 (in C5-VMNOP, carried by C6-B).** Sweep: H is now H′, and the control set it would need is listed.
```text
v5:
- **V5-D** (none). Nothing is selected, so no accounting control is added; H's controls would be designed with its deltas on selection.
v7:
- **V5-D** (none). No accounting option is selected and H′ is not adopted, so no accounting control is added to the roster; the controls H′ would need if adopted are listed in v7 V7-N.K, outside the roster.
```

**R7-29 replaces v5 line 1501 (in C5-VMNOP, carried by C6-B).** V6-REQ-I: channel loss no longer raises.
```text
v5:
- **V5-I** (lab). `Root_Admission_Join` in Transfer_Sent and Roster_Evidence → `Join_Ready`, and in Worker_Owned → `Phase_Mismatch`; `Transfer_Join` before `CUSTODY_ACK` → `Phase_Mismatch`. Each presence value of V5-I.2 tested with its field present and absent. RELAY: a replayed, reordered, cross-gate, cross-request and earlier-epoch frame → `Relay_Frame_Invalid`; a front re-read raising `PEER_REQUEST_MISMATCH` → the worker raises it at that gate and the original exception path follows; channel loss → the closed-connection exception of RC-10.
v7:
- **V5-I** (lab). `Root_Admission_Join` in Transfer_Sent and Roster_Evidence → `Join_Ready`, and in Worker_Owned → `Phase_Mismatch`; `Transfer_Join` before `CUSTODY_ACK` → `Phase_Mismatch`. Each presence value of V5-I.2 tested with its field present and absent. RELAY: a replayed, reordered, cross-gate, cross-request and earlier-epoch frame → `Relay_Frame_Invalid`; a front re-read raising `PEER_REQUEST_MISMATCH` → the worker raises it at that gate and the original exception path follows; channel loss → the worker raises nothing and waits for a reattach; after it, `PEER_HELD` → the gate request is re-issued, and `PEER_LOST_WITH_FRONT` → the branch that RC-13 selects (v7 V7-I.1).
```

**R7-30 replaces v5 line 1517 (in C5-VMNOP, carried by C6-B).** Sweep: option H is now H′.
```text
v5:
| RC-9 | The installed daemon service's resource properties, read back, for option H's coordinator limits | V5-D |
v7:
| RC-9 | The installed daemon service's resource properties, read back, for H′'s service-class coordinator limits | v6 V6-B, v7 V7-K |
```

**R7-31 replaces v5 line 1518 (in C5-VMNOP, carried by C6-B).** V6-REQ-L: the installed check is renamed (v7 §C.5).
```text
v5:
| RC-10 | The exception that the original `KernelPeer.observation ()` raises for a closed client connection on the installed CPython | V5-I.5 |
v7:
| RC-13 | The exception that the original `KernelPeer.observation ()` raises for a closed client connection on the installed CPython (this check was named RC-10 in v5 and v6; v7 §C.5) | V5-I.5 |
```

**R7-32 replaces v5 line 1532 (in C5-VMNOP, carried by C6-B).** V6-REQ-L.
```text
v5:
- **Measurements and checks.** K-1 … K-27 (OP-7); RC-1 … RC-7, RC-9, RC-10.
v7:
- **Measurements and checks.** K-1 … K-27 (OP-7); RC-1 … RC-7, RC-9, RC-13 (named RC-10 in v5; v7 §C.5).
```

**R7-33 replaces v6 line 158 (in C6-B, R6-2's result, G-12).** V6-REQ-L (renamed checks) and V6-REQ-F (K-29).
```text
v6:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace, socket, SQLite, loader and interpreter semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14 in §16, K-15 … K-21 in v3 V-O, K-22 and K-23 in v4 V4-N, K-24 … K-27 in v5 V5-N with K-27 as narrowed by v6 V6-M, K-28 in v6 V6-O) or its installed-runtime check (RC-1 … RC-4 in v3 V-O, RC-5 and RC-6 in v4 V4-N, RC-7, RC-9 and RC-10 in v5 V5-N, RC-11 and RC-12 in v6 V6-O).
v7:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace, socket, SQLite, loader and interpreter semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14 in §16, K-15 … K-21 in v3 V-O, K-22 and K-23 in v4 V4-N, K-24 … K-27 in v5 V5-N with K-27 as narrowed by v6 V6-M, K-28 in v6 V6-O, K-29 in v7 V7-O) or its installed-runtime check (RC-1 … RC-4 in v3 V-O, RC-5 and RC-6 in v4 V4-N, RC-7, RC-9 and RC-13 in v5 V5-N, RC-14 and RC-15 in v6 V6-O; RC-13, RC-14 and RC-15 were named RC-10, RC-11 and RC-12 before v7, §C.5).
```

**R7-34 replaces v6 line 166 (in C6-B, R6-3's result, OP-7).** The same range repair as R6-3, for K-29; no operator item is added.
```text
v6:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 (§16), K-15 … K-21 (v3 V-O), K-22 and K-23 (v4 V4-N), K-24 … K-27 (v5 V5-N, K-27 narrowed by v6 V6-M) and K-28 (v6 V6-O) in an authorized lab | §3–§9, v3 V-B … V-I, v4 V4-B … V4-L, v5 V5-B … V5-L and v6 V6-B … V6-M runtime evidence |
v7:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 (§16), K-15 … K-21 (v3 V-O), K-22 and K-23 (v4 V4-N), K-24 … K-27 (v5 V5-N, K-27 narrowed by v6 V6-M), K-28 (v6 V6-O) and K-29 (v7 V7-O) in an authorized lab | §3–§9, v3 V-B … V-I, v4 V4-B … V4-L, v5 V5-B … V5-L, v6 V6-B … V6-M and v7 V7-A … V7-K runtime evidence |
```

**R7-35 replaces v6 line 270 (in C6-B, R6-16's result).** V6-REQ-F.
```text
v6:
| Prepared | `HELD` | Held | Front | authentic HELD frame; machine admission at DISPATCH, `Record_Launch_Intent` and `DISPATCH_INTENT` already committed; the record carries the full launch packet, launch reply and dispatch (moved from the lane's `PREPARED` record) and the namespace init's host pid and start tick (v6 V6-F.2); sets `Launched` |
v7:
| Prepared | `HELD` | Held | Front | authentic HELD frame; machine admission at DISPATCH, `Record_Launch_Intent` and `DISPATCH_INTENT` already committed; the record carries the full launch packet, launch reply and dispatch (moved from the lane's `PREPARED` record), the namespace init's host pid, its start tick read under the pidfd pairing of v7 V7-F.1 (or the fact that the init pidfd was already terminal), and the boot identity (v6 V6-F.2 with v7 V7-F.1); sets `Launched` |
```

**R7-36 replaces v6 line 294 (in C6-B, R6-19's result).** V6-REQ-G: one set of routes per cause class, aligned with R7-38 and V6-G.2 as replaced.
```text
v6:
| Unknown | `RECONCILED`, then the event that native evidence determines | that event's target | Reconciler only (INV-C5) | authentic durable evidence; never EOF or a deadline alone. For a cause of class C-CHANNEL or C-DEADLINE with `Before_Unknown` a worker phase, a committed `WORKER_REATTACHED (n)` after the `UNKNOWN` event, with the worker's identity live, is such evidence, and the target is `Before_Unknown` (v6 V6-G) |
v7:
| Unknown | `RECONCILED`, then the event that native evidence determines | that event's target | Reconciler only (INV-C5) | authentic durable evidence; never EOF or a deadline alone. The cause record is an operand, and the evidence depends on its class (v7 V7-G.1, V7-G.2): for C-CHANNEL or C-DEADLINE with `Before_Unknown` a worker phase, a committed `WORKER_REATTACHED (n)` after the `UNKNOWN` event, with the worker's identity live (v7 V7-F.2), and the target is `Before_Unknown`; for C-APPEND, the chain verified in the custody transaction (X-4 `Ready`, X-5 `fold` equal to the stored rows), with the worker's identity live when `Before_Unknown` is a worker phase, and the target is `Before_Unknown`; for C-EVIDENCE, none of these. Evidence E-CR leads instead to `CUSTODY_RETURNED` (R6-18) |
```

**R7-37 replaces v6 line 330 (in C6-B, R6-23's result).** V6-REQ-I: never raise while the front may be alive.
```text
v6:
**Transport loss: the legal fallback state.** If the channel closes or a frame fails `relay_frame`, the gate use cannot complete over RELAY. A RELAY client connection lives only in the front, so a front that lost the channel has lost the client connection too. The worker then does what the original re-read does when its client has gone, which RC-10 settles before B-RECV is reviewed (v6 V6-I.1): (a) if the original re-read raises, the worker raises the same class, code, message and details at that gate, and the original exception path follows; (b) if it raises nothing (it re-reads an owned descriptor, `rw/client_peer.py:73-90`), the worker takes as the gate's re-read the last authenticated front re-read for (g, r, s), which is exactly what the original re-read would return, and continues, adding no refusal and no quarantine; the response is produced and `REQUEST_RESPONDED` committed, and only its write is lost, as the original `_send` drops writes to a closed writer (`rw/daemon.py:394-400`). No gate waits on a deadline, nothing is fabricated, and `REQUEST_LOST` applies if the worker dies.
v7:
**Transport loss: the legal fallback state.** If the channel closes or a frame fails `relay_frame`, the gate use cannot complete over RELAY. The front that holds the request's client connection may still be alive, with its client still connected (only the channel closed, or one frame failed), so the worker decides nothing from the loss itself. It closes the channel if it is still open, keeps the gate pending, and waits, with no deadline, for a front to complete the reattach handshake (V5-L.3, with R6-26). For each pending (g, r, s) the reattached front answers one authenticated `PEER_STATUS` frame (v7 V7-I.1). On `PEER_HELD` the front still holds that request's connection; the worker re-issues the gate request over the new channel, the front performs the original re-read, and the gate gets whatever the original re-read gives. On `PEER_LOST_WITH_FRONT` the front that held the connection has ended (its recorded identity is gone by the test of v7 V7-F.2) and the reattached front holds no connection for the request. Only then does the worker do what the original re-read does when its client has gone, which RC-13 settles before B-RECV is reviewed (v6 V6-I.1): (a) if the original re-read raises, the worker raises the same class, code, message and details at that gate, and the original exception path follows; (b) if it raises nothing (it re-reads an owned descriptor, `rw/client_peer.py:73-90`), the worker takes as the gate's re-read the last authenticated front re-read for (g, r, s), which is exactly what the original re-read would return, and continues, adding no refusal and no quarantine; the response is produced and `REQUEST_RESPONDED` committed, and only its write is lost, as the original `_send` drops writes to a closed writer (`rw/daemon.py:394-400`). No gate decides on a deadline, nothing is fabricated, and `REQUEST_LOST` applies if the worker dies.
```

**R7-38 replaces v6 line 344 (in C6-B, R6-24's result).** V6-REQ-G.
```text
v6:
| Unknown | queued; the worker mutates nothing and waits at its refused choke point (v6 V6-G) | evidence | the Reconciler's `RECONCILED` on: a committed `WORKER_REATTACHED` with the worker live (back to `Before_Unknown`), or evidence E-CR (`CUSTODY_RETURNED`) | as the rows above |
v7:
| Unknown | queued; the worker mutates nothing and waits at its refused choke point (v6 V6-G) | evidence | by the route of the cause class (v7 V7-G.2): for C-CHANNEL or C-DEADLINE, the Reconciler's `RECONCILED` on a committed `WORKER_REATTACHED` with the worker live (back to `Before_Unknown`); for C-APPEND, the Reconciler's `RECONCILED` on the verified chain (back to `Before_Unknown`, then the phase owner's re-append if the failed event is absent); for any class, evidence E-CR (`CUSTODY_RETURNED`) | as the rows above |
```

**R7-39 replaces v6 line 352 (in C6-B, R6-25's result).** V6-REQ-K: "meets it at design level" was not established.
```text
v6:
| A later WL request while a worker owns | queued for g+1 | until g+1 | `FRONT_OWNED (g+1)` | **OPEN containment gap CG-3** against the original per-request concurrency (v6 V6-C); its closure condition does not depend on D-4a, and H′ (v6 V6-K) meets it at design level |
v7:
| A later WL request while a worker owns | queued for g+1 | until g+1 | `FRONT_OWNED (g+1)` | **OPEN containment gap CG-3** against the original per-request concurrency (v6 V6-C); its closure condition does not depend on D-4a. H′ (v7 V7-K) is a candidate route; whether it meets the condition stays OPEN until D-H1 … D-H7 are reviewed and their controls pass |
```

**R7-40 replaces v6 line 368 (in C6-B, R6-27's result).** V6-REQ-L.
```text
v6:
| K-27 | A sealed `memfd` (`F_SEAL_WRITE`, `F_SEAL_SHRINK`, `F_SEAL_GROW`) cannot be changed by any holder, its creator included, and mapping it maps exactly its sealed bytes. The dynamic loader's part is RC-11, lead-owned (v6 V6-M) | V5-E.3 |
v7:
| K-27 | A sealed `memfd` (`F_SEAL_WRITE`, `F_SEAL_SHRINK`, `F_SEAL_GROW`) cannot be changed by any holder, its creator included, and mapping it maps exactly its sealed bytes. The dynamic loader's part is RC-14 (named RC-11 in v6; v7 §C.5), lead-owned (v6 V6-M) | V5-E.3 |
```

**R7-41 replaces v6 line 402 (in C6-B).** Sweep: a reading rule pointed into superseded text (v6 §C.2).
```text
v6:
- **RR6-1.** Inside carried v5 slices, v5's reading rules RR5-1 … RR5-8 (in C5-B; RR5-7 as replaced by R6-1) apply, and the aliases are those of v6 §C.2.
v7:
- **RR6-1.** Inside carried v5 slices, v5's reading rules RR5-1 … RR5-8 (in C5-B; RR5-7 as replaced by R6-1, RR5-1 and RR5-2 as replaced by R7-14 and R7-15) apply, and the aliases are those that v7 §C.2 restates for v5 text.
```

**R7-42 replaces v6 line 403 (in C6-B).** Sweep: the rule mapped into v6 §A, §C and appendices, which v7 supersedes, and into V6-K, which v7 supersedes.
```text
v6:
- **RR6-2.** A reference inside carried text to a superseded v5 section resolves through §B.3: V5-A.1 → V6-A.1 and V6-A.2; V5-B.6 → V6-D (the dispatcher) and V6-L (CG-1); V5-D, V5-D.1, V5-D.2 → V6-K; v5 §A, §C and the appendices → v6 §A, §C and the appendices.
v7:
- **RR6-2.** A reference inside carried text to a superseded v5 section resolves through §B.3: V5-A.1 → V6-A.1 and V6-A.2; V5-B.6 → V6-D (the dispatcher) and V6-L (CG-1); V5-D, V5-D.1, V5-D.2 → v7 V7-K (which supersedes V6-K); v5 §A, §C and the appendices → v7 §A, §C and the appendices (v6's are superseded, v7 §B.3).
```

**R7-43 replaces v6 line 482 (in C6-VA).** V6-REQ-A (`fold`'s variant) and V6-REQ-G (the cause record as an operand).
```text
v6:
| X-5 `wl_root_custody_phase_*_v1` | T, with output triples | `legal`: `EventRec`, Arena, `RootStateRec`, `SubjectStateRec` and `EvidenceRec` triples, `PhaseResult`. `next`: the same, then an output `RootStateRec` triple and an output `SubjectStateRec` triple (writable, count = capacity), then an output-arena pair (pointer, byte capacity), then `PhaseResult`. `fold`: Arena, the `EventRow` triple, the stored `RootStateRec` and `SubjectStateRec` triples, the same outputs, `PhaseResult`. `mutation_allowed`: `MutationInput`, Arena, the two state triples, `PhaseResult` |
v7:
| X-5 `wl_root_custody_phase_*_v1` | T, with output triples; `fold` is T with no Input record | `legal`: `EventRec`, Arena, `RootStateRec`, `SubjectStateRec` and `EvidenceRec` triples, `PhaseResult`; while the root is Unknown the `EvidenceRec` roster carries the cause record as kind `Cause_Record` (v7 V7-G.1). `next`: the same, then an output `RootStateRec` triple and an output `SubjectStateRec` triple (writable, count = the roster capacity of v7 V7-A.2), then an output-arena pair (pointer, the byte capacity of v7 V7-A.2), then `PhaseResult`. `fold`: no Input record, because every operand is a roster, just as `wl_chain_authority_replay_v1` is the variant with no arena: the Arena pair, the `EventRow` triple, the stored `RootStateRec` and `SubjectStateRec` triples, the same outputs, `PhaseResult`. `mutation_allowed`: `MutationInput`, Arena, the two state triples, `PhaseResult` |
```

**R7-44 replaces v6 line 490 (in C6-VA).** V6-REQ-A: the capacity rule covers every successor.
```text
v6:
**Output capacity, no negotiation.** v5's `WL_ABI_CAPACITY` retry is withdrawn; it was a new mechanism that v5 had labelled as observed. `next` and `fold` write only rows whose number the wrapper knows from the inputs, and new quantity bytes only for a generation successor. The successor of an n-byte magnitude needs at most n + 1 bytes **[static reasoning]**. So the wrapper passes output rosters and an output arena sized from the inputs. The native unit reports `Capacity_Short` in `PhaseResult.status` only if the wrapper broke that rule, which is a wrapper defect and not a refusal of any input.
v7:
**Output capacity, no negotiation.** v5's `WL_ABI_CAPACITY` retry is withdrawn; it was a new mechanism that v5 had labelled as observed. `next` and `fold` write only rows whose number the wrapper knows from the inputs, and every span field they write (an Id or a quantity) is a copy of an input span or, for a quantity, the successor of one: the root's generation g+1, `Reattach_Epoch` n = current + 1, a subject's sub-generation s+1, and any other quantity `Next` increments. The successor of an n-byte magnitude needs at most n + 1 bytes **[static reasoning; JACKAL J7-1 and J7-2 check two instances]**. The wrapper sizes the output rosters and the output arena by the rule of v7 V7-A.2, which reserves the largest input span length plus one byte for every output span field, so every copy and every successor fits. The native unit reports `Capacity_Short` in `PhaseResult.status` only if the wrapper broke that rule, which is a wrapper defect and not a refusal of any input.
```

**R7-45 replaces v6 line 495 (in C6-VA).** V6-REQ-A: the count is not `m`.
```text
v6:
1. 4 bytes `WLMP`; a 16-bit version, 1; a 16-bit export version (1 for `decide_v1`, 2 for `decide_v2`); a 32-bit count m of serialized parameters, which is the export's `PARAMETERS` roster without `Output`.
v7:
1. 4 bytes `WLMP`; a 16-bit version, 1; a 16-bit export version (1 for `decide_v1`, 2 for `decide_v2`); a 32-bit `param_count`, the number of serialized parameters, which is the export's `PARAMETERS` roster without `Output` (for `decide_v2`, the roster of v7 V7-A.1).
```

**R7-46 replaces v6 line 496 (in C6-VA).** V6-REQ-A: the material's kind is not the layout's record kind.
```text
v6:
2. For each serialized parameter, in `PARAMETERS` order: a 32-bit index; an 8-bit kind (0 record, 1 arena, 2 roster); a 64-bit size word, exactly the value passed to `decide`; a 64-bit byte length (the size word for a record or an arena; the size word times the element's layout size for a roster); then that many bytes.
v7:
2. For each serialized parameter, in `PARAMETERS` order: a 32-bit `param_index` (its position in that roster, from 0); an 8-bit `slot_kind` (0 record, 1 arena, 2 roster), the material's own classification, which is not the layout's `record_kind`; a 64-bit size word, exactly the value passed to `decide`; a 64-bit byte length (the size word for a record or an arena; for a roster, the size word times `layout (record_kind, 0)` of the roster's element record); then that many bytes.
```

**R7-47 replaces v6 line 497 (in C6-VA).** V6-REQ-A.
```text
v6:
3. The material digest m is the SHA-256 of the whole byte string (V5-E.3).
v7:
3. The material digest `m` is the SHA-256 of the whole byte string (V5-E.3). In the material and in every frame and record that carries it (`CHILD_MEASURED`, `COMMIT_CHILD_REQUEST`, `COMMIT_CHILD_GO`), `m` names this digest and nothing else.
```

**R7-48 replaces v6 line 499 (in C6-VA).** V6-REQ-A.
```text
v6:
The sub-helper checks the magic and versions; that m equals its own compiled roster's length without `Output`; every index in order; every kind against its own roster table; every record's size against `layout (kind, 0)`; and every byte length against the size word. Spans are arena indices, so the copies keep their meaning. The sub-helper calls `decide` with pointers to its own copies, the same size words, and its own output record.
v7:
The sub-helper checks the magic and versions; that `param_count` equals its own compiled roster's length without `Output`; every `param_index` in order; every `slot_kind` against its own roster table; every record's size word against `layout (record_kind, 0)`, where `record_kind` is the layout kind its own roster table gives for that parameter; and every byte length against the size word. Spans are arena indices, so the copies keep their meaning. The sub-helper calls `decide` with pointers to its own copies, the same size words, and its own output record.
```

**R7-49 replaces v6 line 523 (in C6-VB).** V6-REQ-B.
```text
v6:
**What happens (static).** While a worker owns generation g, an IP request is served by the worker (V5-B.5 as R6-9). Its handler runs in the coordinator. The coordinator is the main workload of g's root unit, which the front launched with the properties of the **WL request's** plan: `handler_plan (self.front, capture['resource_intent'].bound)` (`rw/protected_root_resource.py:38`), its policy (`:50`), and `--property=` for each of `plan['systemd_properties']` (`:68-71`). The IP handler's CPU, memory and tasks therefore count against the bound admitted for that WL request. This is G's handler-bound gap: AO-5 and AO-6 for handler code, and AO-11, because an IP handler can exhaust a bound admitted for another request and so kill admitted work.
v7:
**What happens (static).** While a worker owns generation g, an IP request is served by the worker (V5-B.5 as R6-9). Its handler runs in the coordinator. The coordinator is the main workload of g's root unit. The front launched that unit with the properties of the **root-worker plan's `worker_policy`**, admitted under the WL request's reservation: `handler_plan (self.front, capture['resource_intent'].bound)` (`rw/protected_root_resource.py:38`) builds its policy from the front plan's `worker_policy` (`rw/root_worker_plan.py:22`) and its `systemd_properties` as that policy's `unit_properties ()` (`:37`); `launch_root_worker` admits that policy at DISPATCH for the WL request's reservation (`rw/protected_root_resource.py:50-51`) and passes `--property=` for each of `plan['systemd_properties']` (`:68-71`). Only the catalogue cost is the WL operation's: the front plan's `cost_key` must equal the WL operation's own plan's (`:39-41`). The IP handler's CPU, memory and tasks therefore count against the `worker_policy` bound admitted under that WL request's reservation. This is G's handler-bound gap: AO-5 and AO-6 for handler code, and AO-11, because an IP handler can exhaust a bound admitted for another request and so kill admitted work.
```

**R7-50 replaces v6 line 532 (in C6-VB).** V6-REQ-K.
```text
v6:
- **A design that meets the condition:** H′ (V6-K). Its coordinator runs handler code under the installed service's own limits and holds no request's reservation. Whether H′ is adopted is for the lead (§V6-K.4). The author does not adopt it.
v7:
- **A candidate route:** H′ (v7 V7-K). Its coordinator runs handler code under the installed service's own limits (RC-9) and holds no request's reservation. Whether it meets the closure condition stays OPEN until its deltas D-H1 … D-H7 are reviewed and its controls (v7 V7-N.K) pass. Its adoption is the lead's only after the showing of v7 V7-K.7, and otherwise falls under D-4a's existing reservation (OP-3). The author does not adopt it.
```

**R7-51 replaces v6 line 545 (in C6-VC).** V6-REQ-K.
```text
v6:
- **A design that meets the condition:** H′ (V6-K). Each WL request gets its own request-root unit while the service-class coordinator keeps serving.
v7:
- **A candidate route:** H′ (v7 V7-K). Each WL request gets its own request-root unit, launched by D-H7 while the service-class coordinator owns custody and keeps serving (v7 V7-K.2). Whether it meets the closure condition stays OPEN, as for CG-2.
```

**R7-52 replaces v6 line 560 (in C6-VD).** V6-REQ-L.
```text
v6:
| `unit.launcher.wait ()` (`:276`) | `Popen.wait ()` of `systemd-run --pipe` | blocks until `CLOSED_CHILD`; returns the integer `systemd-run --pipe` returns for the same main-process status, or for a unit that never started (RC-12) | — | CJ-DISP-1, RC-12 |
v7:
| `unit.launcher.wait ()` (`:276`) | `Popen.wait ()` of `systemd-run --pipe` | blocks until `CLOSED_CHILD`; returns the integer `systemd-run --pipe` returns for the same main-process status, or for a unit that never started (RC-15, named RC-12 in v6) | — | CJ-DISP-1, RC-15 |
```

**R7-53 replaces v6 line 563 (in C6-VD).** V6-REQ-D: `result` takes only the original's values.
```text
v6:
| `systemd.outcome (unit, exit_code, stopped=…, _raw_observer=…)` (`:342-347`) | `outcome` (`:623-714`) | returns a dict with exactly the original keys, `kind`, `unit`, `source`, `launcherExit`, `started`, `supervisionEvidence`, `stoppedByManager`, `exitCode`, `exitStatus`, `result`, `windowMilliseconds`, `events`, `launcherStderr`, as follows. **`kind`:** `SUPERVISED` exactly when `CHILD_READY` is committed and `CLOSED_CHILD` reports the exec released (the counterpart of the manager's started or process-exit entry); `LAUNCH_FAILED` when the actor never exec'd and the launcher exit is non-zero; otherwise `INDETERMINATE`, including when no `CLOSED_CHILD` frame exists. **`source`:** `child-closure`, or `child-closure-unavailable` when the frames cannot be read. **`started`:** `kind = SUPERVISED`. **`supervisionEvidence`:** `child-ready-and-closed` or `None`. **`stoppedByManager`:** a `STOP_UNIT` was executed for the leaf. **`exitCode` and `exitStatus`:** from the main status in `CLOSED_CHILD`. **`result`:** `stopped` after `STOP_UNIT`; `oom-kill` when the leaf's `memory.events` reports an OOM kill (the runner tests this value, `:937-938`); `failure` for a non-zero main status; `success` when started with launcher exit 0; otherwise `None`. **`windowMilliseconds`:** the original adapter's value. **`events`:** the closure-frame records. **`launcherStderr`:** the helper's diagnostic text, truncated as the original truncates. `_raw_observer` is called with (ordinal, record) for each acquired frame, as the original calls it | the original `UNIT_LAUNCH_FAILED` raised by the runner (`:944-950`) follows from `kind` unchanged | CJ-DISP-4 |
v7:
| `systemd.outcome (unit, exit_code, stopped=…, _raw_observer=…)` (`:342-347`) | `outcome` (`:623-714`) | returns a dict with exactly the original keys, `kind`, `unit`, `source`, `launcherExit`, `started`, `supervisionEvidence`, `stoppedByManager`, `exitCode`, `exitStatus`, `result`, `windowMilliseconds`, `events`, `launcherStderr`, as follows. **`kind`:** `SUPERVISED` exactly when `CHILD_READY` is committed and `CLOSED_CHILD` reports the exec released (the counterpart of the manager's started or process-exit entry); `LAUNCH_FAILED` when the actor never exec'd and the launcher exit is non-zero; otherwise `INDETERMINATE`, including when no `CLOSED_CHILD` frame exists. **`source`:** `child-closure`, or `child-closure-unavailable` when the frames cannot be read. **`started`:** `kind = SUPERVISED`. **`supervisionEvidence`:** `child-ready-and-closed` or `None`. **`stoppedByManager`:** a `STOP_UNIT` was executed for the leaf. **`exitCode` and `exitStatus`:** from the main status in `CLOSED_CHILD`. **`result`:** exactly the original's value set (`rw/linux/systemd.py:704-709`): `stopped` after `STOP_UNIT`; `failure` for a non-zero or signalled main status, an OOM-killed actor included; `success` when started with launcher exit 0; otherwise `None`. It is never `oom-kill`, which the original `outcome` never returns; an OOM kill reaches the runner as in the original, through `resource_telemetry`'s `oomKilled` and `hitMemoryCeiling` (the next row). **`windowMilliseconds`:** the original adapter's value. **`events`:** the closure-frame records. **`launcherStderr`:** the helper's diagnostic text, truncated as the original truncates. `_raw_observer` is called with (ordinal, record) for each acquired frame, as the original calls it | the original `UNIT_LAUNCH_FAILED` raised by the runner (`:944-950`) follows from `kind` unchanged; its message and details carry `launcherStderr` and the supervision dict (CJ-DISP-4) | CJ-DISP-4 |
```

**R7-54 replaces v6 line 564 (in C6-VD).** V6-REQ-D: OOM through telemetry.
```text
v6:
| `systemd.effective_limits`, `systemd.resource_telemetry` through `systemd_call (provider, unit, cancel_event=…)` (`:746`, `:761`, `:780`) | `:472-492` and following | dicts of the same shapes and `state` values (`OBSERVED`, `UNIT_GONE`, `UNAVAILABLE`). The `kernel` values come from the leaf's cgroup files, read through the read-only view. The `systemd` sub-dict's values are `None`, because a leaf cgroup has no manager properties | cancellation through `systemd_call` unchanged | CJ-DISP-5 |
v7:
| `systemd.effective_limits`, `systemd.resource_telemetry` through `systemd_call (provider, unit, cancel_event=…)` (`:746`, `:761`, `:780`) | `:472-492` and following; `resource_telemetry` at `rw/linux/systemd.py:499-546` | dicts of the same keys and `state` values (`OBSERVED`, `UNIT_GONE`, `UNAVAILABLE`). The `kernel` values come from the leaf's cgroup files, read through the read-only view. The `systemd` sub-dict's values are `None`, because a leaf cgroup has no manager properties. `resource_telemetry` parses the leaf's `memory.events` exactly as the original parses its unit's (`:518-531`): `memoryEvents` holds the counters, `hitMemoryCeiling` comes from `max`, `oom` or `oom_kill`, and `oomKilled` from `oom_kill`. The original also sets `oomKilled` from the manager's `Result=oom-kill` (`:530-531`); a leaf has no manager `Result`, so its `result` and `activeState` are `None`. The leaf answers `OBSERVED` from the actor's exec until `CLOSED_CHILD`, and `UNAVAILABLE` afterwards, as the original answers `UNAVAILABLE` once the unit is gone (`:500-508`) | cancellation through `systemd_call` unchanged | CJ-DISP-5 |
```

**R7-55 replaces v6 line 572 (in C6-VD).** V6-REQ-D: the persisted fields and messages.
```text
v6:
- **CJ-DISP-4:** the supervision dict's evidence fields come from helper closure frames, not from the manager's journal. The runner branches only on `kind` and `result` (`:937-982`), so those two must classify the same runs as the original does; the other fields are diagnostic and differ in source.
v7:
- **CJ-DISP-4:** the supervision dict's evidence comes from helper closure frames, not from the manager's journal. (i) `kind` and `result` must classify every run as the original classifies it, with only the original's values; the runner branches on them (`rw/runner.py:937-982`). (ii) `unit`, `launcherExit`, `started`, `stoppedByManager`, `exitCode`, `exitStatus` and `windowMilliseconds` must equal the original's for the same run. (iii) `source`, `supervisionEvidence`, `events` and `launcherStderr` differ in value, because their source differs, and they are persisted: the whole dict in `agent_result['supervision']` (`:967`) and in the manager-return raw record (`:986`); `source` in the `SUPERVISION_INDETERMINATE` reason text (`:982`); the first line of `launcherStderr` in the `UNIT_LAUNCH_FAILED` message, with the whole dict in its details (`:944-950`). Those persisted texts are a **stated difference** in durable evidence, listed field by field in v7 V7-D.2. No classification, result status, refusal or decision depends on them, and no equivalence is claimed for them.
```

**R7-56 replaces v6 line 573 (in C6-VD).** V6-REQ-D.
```text
v6:
- **CJ-DISP-5:** limits and telemetry come from the kernel's cgroup files with the manager-property values absent; the runner's `ceilingFired` and `ceilingEvidence` (`:935-943`) must give the original classification.
v7:
- **CJ-DISP-5:** limits and telemetry come from the kernel's cgroup files with the manager-property values absent; the runner's `ceilingFired` and `ceilingEvidence` (`:935-943`) must give the original classification for the same run. Neither side's `outcome` returns `oom-kill`, so both reach an OOM kill only through telemetry, and with `hitMemoryCeiling` set `ceilingEvidence` is "cgroup memory.events sampled during the run" on both. The OPEN part is the sampling window: the original reads `memory.events`, and `Result=oom-kill`, while the manager still shows the unit; the dispatcher reads the leaf's `memory.events` until `CLOSED_CHILD`. That both windows classify every run the same way is the obligation.
```

**R7-57 replaces v6 line 636 (in C6-VF).** V6-REQ-F; also removes a reference to superseded v5 text ("As in v5").
```text
v6:
As in v5: the worker pidfd terminal, and the root namespace-init pidfd terminal (K-24). Both are held by the front since HELD. OB-ESC (V6-F.4) is part of the evidence's premise.
v7:
The front holds the root namespace-init pidfd since HELD (the HELD frame passes it, `C1:247`) and the worker pidfd since the worker's measurement (it opens it from the measured host pid, `rw/protected_root_resource.py:129`). The evidence is both pidfds terminal (K-24). OB-ESC (V6-F.4) is part of the evidence's premise.
```

**R7-58 replaces v6 line 640 (in C6-VF).** V6-REQ-F: pairing and boot identity.
```text
v6:
1. **Recorded identities.** The worker's host pid and start tick are in the `EXECUTION_NATIVE` record, whose process capture holds `host_pid` and `start_tick` (`RawProcess`, `rw/resource_child_execution.py:18`; captured at `rw/protected_root_resource.py:129-134`). The namespace init's host pid comes from the HELD frame (`C1:241`). Its start tick is read by the front from `/proc/<pid>/stat` at HELD and recorded in the `HELD` event (R6-16).
v7:
1. **Recorded identities.** The boot identity, `/proc/sys/kernel/random/boot_id` read as the original reads it (`rw/protected_scoped_resource_runtime.py:145`), is recorded in the custody `HELD` event and in the `EXECUTION_NATIVE` record. The worker's host pid and start tick are in the `EXECUTION_NATIVE` record, whose process capture holds `host_pid` and `start_tick` (`RawProcess`, `rw/resource_child_execution.py:18`; captured through the worker pidfd at `rw/protected_root_resource.py:129-134`). The namespace init's host pid comes from the HELD frame (`C1:241`); its start tick is read by the front while it holds the init pidfd that the same frame passes (`C1:247`), under the pairing of v7 V7-F.1, and is recorded in the `HELD` event (R6-16 as replaced by R7-35), or the event records that the init pidfd was already terminal.
```

**R7-59 replaces v6 line 641 (in C6-VF).** V6-REQ-F.
```text
v6:
2. **Identity gone.** For each of the two: `pidfd_open (pid)` fails with `ESRCH`; or it succeeds, and `/proc/<pid>/stat` read while that pidfd is held shows a different start tick. A pid is unique among live processes, so a different start tick means the recorded process has exited **[unverified reasoning, K-4]**. An equal start tick means it is alive, and no custody return follows.
v7:
2. **Identity gone.** For each of the two, any one of: the current boot identity differs from the recorded one; `pidfd_open (pid)` fails with `ESRCH`; it succeeds, and `/proc/<pid>/stat` read while that pidfd is held shows a different start tick; or, for the init, the `HELD` event records its pidfd already terminal. Within one boot a pid is unique among live processes, so a different start tick means the recorded process has exited **[unverified reasoning, K-4]**; a different boot identity means the recorded process belonged to an earlier boot and has exited **[unverified reasoning, K-29]**. An equal boot identity and an equal start tick mean it is alive, and no custody return follows.
```

**R7-60 replaces v6 line 680 (in C6-VG).** V6-REQ-G: the cause class is an X-5 operand.
```text
v6:
The cause record names its class.
v7:
The cause record names its class; for C-APPEND it also names the failed event's replay identity and record digest (V5-F.6). The cause record is an X-5 operand (v7 V7-G.1).
```

**R7-61 replaces v6 line 685 (in C6-VG).** V6-REQ-G and V6-REQ-F.
```text
v6:
2. **Reconcile.** The Reconciler commits `RECONCILED` with target `Before_Unknown` (legal by R6-19). It may do so only when the cause is C-CHANNEL or C-DEADLINE, the committed `WORKER_REATTACHED` follows the `UNKNOWN` event, and the worker's identity is live (its pidfd not terminal in R1; `pidfd_open` with an equal start tick in R2).
v7:
2. **Reconcile.** The Reconciler commits `RECONCILED` with target `Before_Unknown` (legal by R6-19 as replaced by R7-36). On this route it may do so only when the cause record, as an X-5 operand, has class C-CHANNEL or C-DEADLINE, the committed `WORKER_REATTACHED` follows the `UNKNOWN` event, and the worker's identity is live (its pidfd not terminal in R1; in R2 the recorded boot identity current and `pidfd_open` with an equal start tick, v7 V7-F.2).
```

**R7-62 replaces v6 line 686 (in C6-VG).** V6-REQ-G: the C-APPEND route is not circular.
```text
v6:
3. **C-APPEND.** The owner's own replay of the failed append succeeds, by the replay identity of V5-F.6. That committed event is the durable evidence, and the target is `Before_Unknown`.
v7:
3. **C-APPEND.** The `UNKNOWN` event's `Before_Unknown` is the phase the chain folds to when `UNKNOWN` is appended, so it already reflects the failed event E if E persisted. The Reconciler commits `RECONCILED` with target `Before_Unknown` on the chain itself as evidence: X-4 `Ready` and X-5 `fold` equal to the stored rows in the custody transaction (V5-F.6 step 1), and, when `Before_Unknown` is a worker phase, the worker's identity live (v7 V7-F.2). Then exactly one of: (a) the chain holds an event with E's replay identity and record digest (a replay hit): E persisted, nothing is re-appended, and a replay of E by its owner returns it unchanged (V5-F.6 step 2); (b) it holds none: E did not persist, and the phase owner re-decides and re-appends E, which is `Legal` under E's own row because the root is back in `Before_Unknown`. Neither step uses E as evidence for `RECONCILED`, so the route is not circular (v7 V7-G.2).
```

**R7-63 replaces v6 line 692 (in C6-VG).** V6-REQ-G: "as in the original" overclaimed.
```text
v6:
2. A protected section that reaches a refused choke point **does not raise**. It does not quarantine, and it does not fail the operation for this reason. It waits on the custody-commit condition, with no deadline, and re-evaluates `Mutation_Allowed` after each commit. It keeps the locks it holds, as any long protected section does; other requests in the worker wait behind it as in the original.
v7:
2. A protected section that reaches a refused choke point **does not raise**. It does not quarantine, and it does not fail the operation for this reason. It waits on the custody-commit condition, with no deadline, and re-evaluates `Mutation_Allowed` after each commit. It keeps the locks it holds, as any long protected section does, and other requests in the worker wait behind those locks. The original has no Unknown phase and so no such wait: this wait is a **stated difference**, present only while the root is Unknown, OPEN under 09.5, and it ends only as item 6 states.
```

**R7-64 replaces v6 line 717 (in C6-VH).** V6-REQ-H: `Release_Hold` only for `Held_Capacity`.
```text
v6:
- **Phase still `NEVER_DISPATCHED`** (a failure in steps 3 or 4): nothing is appended. The facts satisfy `Never_Holds` (`core/resource_observation_classification.ads:96-102`), the class is `Never_Launched`, and the original `Release_Hold` applies (`core/resource_run_ledger.ads:317-320`). Custody commits `HANDOFF_ABORT (g, Never_Dispatched)`, and V5-G.1's route follows (with R6-21).
v7:
- **Phase still `NEVER_DISPATCHED`** (a failure in steps 3 or 4): nothing is appended. The facts satisfy `Never_Holds` (`core/resource_observation_classification.ads:96-102`), the class is `Never_Launched`, and the original `Release_Hold` applies to a root row of kind `Held_Capacity` (`core/resource_run_ledger.ads:317-320`). A root row of kind `Irreversible_Budget` has no never-launched command (`Release_Hold` requires `Held_Capacity`, `Charge_Budget` requires `Terminal` and `Reaped`, `:317-322`), so it keeps its state and budget, as the original leaves it (v7 V7-H.2). Custody commits `HANDOFF_ABORT (g, Never_Dispatched)`, and V5-G.1's route follows (with R6-21 and R7-22).
```

**R7-65 replaces v6 line 720 (in C6-VH).** V6-REQ-H: the `:192` wedge.
```text
v6:
- U is quarantined by the invoke path's original exception handling (`rw/protected_root_worker.py:191-198`), unchanged.
v7:
- U is quarantined by the invoke path's original exception handling (`rw/protected_root_worker.py:193-198`): `owned.retain_and_stop_unknown` when a dispatch owner exists (`:193-194`), otherwise `p.quarantine (operation, error)` (`:195-198`, the `elif` becoming the plain alternative). Line `:192`, which sets the front's in-memory phase to `UNKNOWN_WORKER_OWNERSHIP` on every failure and so makes `:159` refuse every later root invoke, is replaced by v7 V7-H.1: the in-memory phase follows the committed custody phase, so after `FRONT_OWNED (g+1)` the front serves.
```

**R7-66 replaces v6 line 726 (in C6-VI).** V6-REQ-L.
```text
v6:
### V6-I.1 RC-10 decides the branch before the code is reviewed
v7:
### V6-I.1 RC-13 decides the branch before the code is reviewed
```

**R7-67 replaces v6 line 728 (in C6-VI).** V6-REQ-I and V6-REQ-L.
```text
v6:
R6-23 gives both branches. RC-10 is a lead-owned installed-runtime check of what `KernelPeer.observation ()` (`rw/client_peer.py:73-90`) returns or raises on an owned duplicate after the client has closed. It is performed before B-RECV is reviewed, and the implementation contains only the branch RC-10 selects. Nothing is chosen at run time.
v7:
R6-23 (as replaced by R7-37) gives both branches, and either applies only after a reattached front has answered `PEER_LOST_WITH_FRONT` (v7 V7-I.1). RC-13 (named RC-10 in v6) is a lead-owned installed-runtime check of what `KernelPeer.observation ()` (`rw/client_peer.py:73-90`) returns or raises on an owned duplicate after the client has closed. It is performed before B-RECV is reviewed, and the implementation contains only the branch RC-13 selects. Nothing is chosen at run time.
```

**R7-68 replaces v6 line 732 (in C6-VI).** V6-REQ-L.
```text
v6:
The original re-read compares a fresh `_read` (an `fstat` and `SO_PEERCRED` on the owned duplicate) with `_initial` and raises `PEER_TRANSPORT_CHANGED` on any difference (`:86-90`). If RC-10 shows that `_read` is unchanged after the client closes, the original returns `_initial` at every later gate. The front's re-read at transfer (JF), and every later authenticated relay response, already equal `_initial`: a difference would have raised and propagated. So the last authenticated re-read is exactly the value the original returns, and the worker loses nothing by using it. No refusal and no quarantine is added, which keeps clause 09.4 closed.
v7:
The original re-read compares a fresh `_read` (an `fstat` and `SO_PEERCRED` on the owned duplicate) with `_initial` and raises `PEER_TRANSPORT_CHANGED` on any difference (`:86-90`). If RC-13 shows that `_read` is unchanged after the client closes, the original returns `_initial` at every later gate. The front's re-read at transfer (JF), and every later authenticated relay response, already equal `_initial`: a difference would have raised and propagated. So the last authenticated re-read is exactly the value the original returns, and the worker loses nothing by using it. No refusal and no quarantine is added, which keeps clause 09.4 closed.
```

**R7-69 replaces v6 line 739 (in C6-VI).** V6-REQ-I: re-derivation in the custody owner.
```text
v6:
| parse and validate: JSON, `id`, `op`, `args`, unknown operation, owner-only account (`:316-337`) | yes, exactly. Its error responses (`InvalidRequest`, `UNKNOWN_OPERATION`, `OPERATION_NEEDS_DAEMON_ACCOUNT`) are sent by the front through `_send`. No store write precedes them in the original either | — | — |
v7:
| parse and validate: JSON, `id`, `op`, `args`, unknown operation, owner-only account (`:316-337`) | yes, exactly. Its error responses (`InvalidRequest`, `UNKNOWN_OPERATION`, `OPERATION_NEEDS_DAEMON_ACCOUNT`) are sent by the front through `_send`. No store write precedes them in the original either | re-derives `request_id`, `operation_name`, `args` and the operation entry by running the code of `:318-332` over the exact line bytes that `REQUEST_TRANSFER_INTENT` records (v7 V7-I.2); the account check (`:333-337`) is not repeated, because the front made it for the same peer and the same line | the same |
```

**R7-70 replaces v6 line 755 (in C6-VI).** V6-REQ-I: frame order.
```text
v6:
`PROGRESS_BYTES` is one more RELAY frame type, worker to front, with the same framing, MAC and binding as V5-I.5's frames. Its payload is one progress line (`{"id", "event", "data"}`, `:339-340`) of the request, sent before or after the response, as the original sends progress to the request's writer (`:390-393`). The front writes it while the client connection is open, and drops it otherwise, exactly as `_send` drops writes to a closing writer (`:394-400`).
v7:
`PROGRESS_BYTES` is one more RELAY frame type, worker to front, with the same framing, MAC and binding as V5-I.5's frames. Its payload is one progress line (`{"id", "event", "data"}`, `:339-340`) of the request. Every frame whose bytes the front writes to the client for (g, r, s), `PROGRESS_BYTES` and `RESPONSE_BYTES` alike, carries an output sequence number `out_seq` inside its MAC'd binding, assigned in production order (v7 V7-I.3): progress emitted before the handler returns precedes the response, and progress emitted afterwards by detached work (`:390-393`) follows it. The front writes the frames strictly in `out_seq` order, so the client receives the bytes in the order the original's writer would; it writes while the client connection is open, and drops a frame otherwise, exactly as `_send` drops writes to a closing writer (`:394-400`).
```

**R7-71 replaces v6 line 764 (in C6-VJ).** V6-REQ-J: the fork point.
```text
v6:
1. **Before** its `unshare (CLONE_NEWPID)`, the root helper forks a **child factory** F. It is connected by a `SOCK_SEQPACKET` socketpair created close-on-exec. F never unshares, never execs, and stays in the host PID and mount namespaces.
v7:
1. **Fork point.** The root helper forks a **child factory** F after its argument validation (`C1:308-322`) and before `connect_owner` (`C1:323`): before the owner connection, the actor and custody socketpairs and the go, report, out, err and actor-stdin pipes exist (`C1:323-335`), and before its `unshare (CLONE_NEWPID)` (`C1:336`). Immediately before the fork the root helper creates F's `SOCK_SEQPACKET` socketpair, close-on-exec, and after the fork each side closes the other's end. F never unshares, never execs, and stays in the host PID and mount namespaces.
```

**R7-72 replaces v6 line 767 (in C6-VJ).** V6-REQ-J: the close-all-except list.
```text
v6:
4. **F's surface.** argv, env and cwd are inherited, since F is a fork with no exec. Credentials are root, as the helper's. F holds its socketpair end and, only during one request, the leaf descriptor and the new socketpair's end. F holds no custody descriptor (OB-ESC (iv)).
v7:
4. **F's surface.** argv, env and cwd are inherited, since F is a fork with no exec. Credentials are root, as the helper's. **Close-all-except list:** at entry F closes every descriptor except 0, 1 and 2 (the unit's standard input, output and error, not the actor's out and err pipes) and its own socketpair end, by `close_range` over the ranges on either side of that end where the installed kernel provides it, and otherwise by closing each other entry of `/proc/self/fd`. It then holds exactly those four and, only during one request, the leaf cgroup descriptor and its end of the new sub-helper socketpair, both closed before it reads the next request. So F holds no owner, custody, actor, go, report, out, err or stdin descriptor, and no custody descriptor (OB-ESC (iv)); the fork point of item 1 already ensures this before F's own close runs (control V7-N.J).
```

**R7-73 replaces v6 line 827 (in C6-VL).** V6-REQ-C: CG-4 does not depend on D-4a.
```text
v6:
  - Closure condition: a genuine full-resource owner adapter in which the native owner reservation and an actual protected launch join before evaluation (the refusal's own message), implemented, reviewed, with every original `owner.retry` case served.
v7:
  - Closure condition: a genuine full-resource owner adapter in which the native owner reservation and an actual protected launch join before evaluation (the refusal's own message), implemented, reviewed, with every original `owner.retry` case served. The closure condition does not depend on D-4a: D-4a can neither waive nor close CG-4, and no resource-policy change is proposed for it.
```

**R7-74 replaces v6 line 835 (in C6-VM).** V6-REQ-L.
```text
v6:
- **RC-11 (lead-owned installed-runtime check):** the installed dynamic loader, given `/proc/self/fd/N` of that sealed `memfd`, loads exactly those bytes and resolves the export symbols from them. This is used by V5-E.3 step 4.
v7:
- **RC-14 (lead-owned installed-runtime check; named RC-11 in v6, v7 §C.5):** the installed dynamic loader, given `/proc/self/fd/N` of that sealed `memfd`, loads exactly those bytes and resolves the export symbols from them. This is used by V5-E.3 step 4.
```

**R7-75 replaces v6 line 853 (in C6-VNOPQ).** V6-REQ-D: the lab control.
```text
v6:
  - For each row of V6-D's table, the dispatcher's result or exception equals the original's for the same unit and status: a normal exit, a non-zero exit, a signalled actor, an OOM-killed leaf (`result = oom-kill`), a `CREATE_CHILD` refusal (`SYSTEMD_LAUNCH_FAILED`), an abort before exec (`LAUNCH_FAILED`), and missing closure (`INDETERMINATE`).
v7:
  - For each row of V6-D's table, the dispatcher's result or exception equals the original's for the same unit and status: a normal exit, a non-zero exit, a signalled actor, an OOM-killed leaf (`result` = `failure`, as the original gives for a killed main process, never `oom-kill`; telemetry `oomKilled` and `hitMemoryCeiling` true; the runner's `ceilingFired` true with `ceilingEvidence` "cgroup memory.events sampled during the run"), a `CREATE_CHILD` refusal (`SYSTEMD_LAUNCH_FAILED`), an abort before exec (`LAUNCH_FAILED`), and missing closure (`INDETERMINATE`). For each run the persisted fields of CJ-DISP-4 (iii) are recorded on both sides and listed as differing, never counted as equal.
```

**R7-76 replaces v6 line 861 (in C6-VNOPQ).** V6-REQ-F.
```text
v6:
  - R2: a restarted front with the worker gone (`ESRCH`, and a reused pid with a different start tick) and fresh `flock`s succeeding → `CUSTODY_RETURNED`.
v7:
  - R2: a restarted front with the worker gone (`ESRCH`; a reused pid with a different start tick; a recorded boot identity different from the current one) and fresh `flock`s succeeding → `CUSTODY_RETURNED`.
```

**R7-77 replaces v6 line 870 (in C6-VNOPQ).** V6-REQ-H.
```text
v6:
  - A machine-admission refusal and a `Record_Launch_Intent` refusal each leave the launch journal `NEVER_DISPATCHED`, with no `UNKNOWN` appended, `Release_Hold`, and `HANDOFF_ABORT (Never_Dispatched)`.
v7:
  - A machine-admission refusal and a `Record_Launch_Intent` refusal each leave the launch journal `NEVER_DISPATCHED`, with no `UNKNOWN` appended, `Release_Hold` for a `Held_Capacity` root row and no ledger command for an `Irreversible_Budget` one (its state unchanged), and `HANDOFF_ABORT (Never_Dispatched)`.
```

**R7-78 replaces v6 line 873 (in C6-VNOPQ).** V6-REQ-I and V6-REQ-L.
```text
v6:
  - RC-10's outcome; then RELAY transport loss in the selected branch adds no refusal and no quarantine.
v7:
  - RC-13's outcome (named RC-10 in v6); then RELAY transport loss adds no refusal and no quarantine: with the front alive, the worker waits, the front reattaches and answers `PEER_HELD`, and the gate completes; only `PEER_LOST_WITH_FRONT` leads to the branch RC-13 selected (v7 V7-I).
```

**R7-79 replaces v6 line 878 (in C6-VNOPQ).** V6-REQ-K.
```text
v6:
- **V6-K** (none). H′ is not adopted, so no control is added. CJ-H-1 … CJ-H-4 are listed in V6-P.
v7:
- **V6-K** (none added to the roster). H′ is not adopted, so no control is added to the roster. The controls H′ would need are listed in v7 V7-N.K, and CJ-H-1 … CJ-H-5 in v7 V7-P.
```

**R7-80 replaces v6 line 887 (in C6-VNOPQ).** V6-REQ-L.
```text
v6:
| RC-11 | The installed dynamic loader loads exactly the bytes of `/proc/self/fd/N` of a sealed `memfd` and resolves the export symbols from them | V5-E.3, V6-M |
v7:
| RC-14 | The installed dynamic loader loads exactly the bytes of `/proc/self/fd/N` of a sealed `memfd` and resolves the export symbols from them (named RC-11 in v6) | V5-E.3, V6-M |
```

**R7-81 replaces v6 line 888 (in C6-VNOPQ).** V6-REQ-L.
```text
v6:
| RC-12 | The exit status the installed `systemd-run --pipe` returns for a normally exited, a signalled, and a never-started service | V6-D (`launcher.wait`) |
v7:
| RC-15 | The exit status the installed `systemd-run --pipe` returns for a normally exited, a signalled, and a never-started service (named RC-12 in v6) | V6-D (`launcher.wait`) |
```

**R7-82 replaces v6 line 890 (in C6-VNOPQ).** V6-REQ-L and K-29.
```text
v6:
K items belong to OP-7's existing D-8b reservation, with R6-2 and R6-3's range repair. RC items are lead-owned. RC-10 is now also the selector of V6-I.1's branch.
v7:
K items belong to OP-7's existing D-8b reservation, with R6-2 and R6-3's range repair and R7-33 and R7-34's for K-29. RC items are lead-owned. RC-13 (named RC-10 in v6) is now also the selector of V6-I.1's branch.
```

**R7-83 replaces v6 line 906 (in C6-VNOPQ).** V6-REQ-K.
```text
v6:
- **H′.** Deltas D-H1 … D-H6; its adoption (lead) and any D-4a policy change (operator), none proposed.
v7:
- **H′.** Deltas D-H1 … D-H7 (v7 V7-K.5), CJ-H-1 … CJ-H-5 and the controls of v7 V7-N.K; its adoption (the lead's only after the showing of v7 V7-K.7, otherwise D-4a's existing reservation, OP-3) and any D-4a policy change (operator), none proposed.
```

**R7-84 replaces v6 line 907 (in C6-VNOPQ).** V6-REQ-L and K-29.
```text
v6:
- **Measurements.** K-1 … K-28 (OP-7); RC-1 … RC-7, RC-9 … RC-12.
v7:
- **Measurements.** K-1 … K-29 (OP-7); RC-1 … RC-7, RC-9, RC-13, RC-14 and RC-15 (RC-13 … RC-15 named RC-10 … RC-12 in v6).
```

**R7-85 replaces v6 line 919 (in C6-VNOPQ).** V6-REQ-E: V6-E.4 is superseded by V7-E.4.
```text
v6:
- `archive_equal`'s rounding and bit layout are the author's reading until RC-5. The refusal classes of V6-E.4 are the author's reading of CPython's `json` until RC-5.
v7:
- `archive_equal`'s rounding and bit layout are the author's reading until RC-5. The refusal classes of v7 V7-E.4, in both modes, are the author's reading of CPython's `json` until RC-5.
```

**R7-86 replaces v5 line 1498 (in C5-VMNOP, carried by C6-B).** V6-REQ-F sweep, found by the verification sweep after R7-1 … R7-85 were written (V7-M): the control still required both pidfds, which no restarted front holds. Numbered last, out of line order.
```text
v5:
- **V5-F** (pure). Every row of the root, request and descriptor relations, and each of XC-1 … XC-7, with a positive and a refusal. `HANDOFF_ABORT` after `TRANSFER_SENT` is refused; `CUSTODY_ACK` after `HANDOFF_ABORT` is refused (set ACK). `CLOSED_WITNESS` with an Intake subject is `Barrier_Subjects_Open`. `CUSTODY_RETURNED` without both pidfds terminal is refused. A REQUEST and a DESCRIPTOR subject with the same string do not collide on replay. Every row of V5-F.7 at restart, each idempotent.
v7:
- **V5-F** (pure). Every row of the root, request and descriptor relations, and each of XC-1 … XC-7, with a positive and a refusal. `HANDOFF_ABORT` after `TRANSFER_SENT` is refused; `CUSTODY_ACK` after `HANDOFF_ABORT` is refused (set ACK). `CLOSED_WITNESS` with an Intake subject is `Barrier_Subjects_Open`. `CUSTODY_RETURNED` without evidence E-CR (in R1 both pidfds terminal; in R2 both identities gone and the fresh `flock`s held; v6 V6-F with v7 V7-F) is refused. A REQUEST and a DESCRIPTOR subject with the same string do not collide on replay. Every row of V5-F.7 at restart, each idempotent.
```

### B.3 Superseded v6 text

| v6 lines | v6 content | Status in v7 |
|---|---|---|
| 1-115 | Header; §A.1 … §A.5 (answers to the v5 review) | Superseded by the v7 header and §A. History, not normative; §A.3 of this file states every ruling's owner and evidence. |
| 410-446 | §C truth boundary, bases, labels, numbers | v7 §C, which restates every alias and label |
| 616-628 | V6-E.4 refusal classes of the original JSON checks | V7-E.4 |
| 777-815 | V6-K: H′ | V7-K |
| 924-990 | Appendices A … D | v7 Appendices A … D |

Every other v6 line outside the §B.1 slices is a separator or an empty line (Appendix C). v5's withdrawals W5-1 and W5-2 stay in force (inside C5-B). v7 makes no new withdrawal.

### B.4 Reading rules

- **RR7-1.** Inside carried v6 slices, v6's reading rules RR6-1 … RR6-7 (in C6-B; RR6-1 and RR6-2 as replaced by R7-41 and R7-42) apply, and the aliases are those of v7 §C.2.
- **RR7-2.** A reference inside carried text to a superseded v6 section resolves through §B.3: V6-E.4 → V7-E.4; V6-K, V6-K.1 … V6-K.4 → V7-K (V6-K.4 → V7-K.7); v6 §A, §C and the appendices → v7 §A, §C and the appendices.
- **RR7-3.** "v6 X" inside an R7 text means v6 section X as carried, with its R7 replacements; "v7 Y" means this file's section Y.
- **RR7-4.** An R7 that replaces a line of an R6 block's `v6:` text, or of an R5 or R4 block's result text, changes that replacement's result; the block's older text is unchanged. An R7 that replaces a line of an earlier version names the slice that holds it; no R7 replaces a line that an earlier R replaces, and no line is replaced twice (Appendix C).
- **RR7-5.** Numbers inside carried slices keep their status: observed, or JACKAL exact (v2 J01 … J18; v5 J5-1 … J5-4). They are not re-derived.
- **RR7-6.** "AUTHOR-NOTES" inside a carried v6 slice means v6's `AUTHOR-NOTES.md` (`95826c1e…2633`), bound in Appendix B; it is a process record and binds nothing normative.
- **RR7-7.** The installed-runtime checks named RC-10, RC-11 and RC-12 before v7 are RC-13, RC-14 and RC-15 (§C.5). Every carried line that named them as installed checks is replaced by quotation (R7-29, R7-31 … R7-33, R7-37, R7-40, R7-52, R7-66 … R7-68, R7-74, R7-78, R7-80 … R7-82, R7-84); this rule only records the mapping and neutralises no sentence. RC-01 … RC-12 written with a leading zero, and RC-10, RC-11 and RC-12 where carried text calls them inherited required changes (§C.5), are the v1 review's required changes and are untouched.

---

## C. Truth boundary, bases and method

### C.1 What was done

- **Reading only.** The Read tool and read-only Bash (`sed -n`, `awk`, `grep`, `sha256sum`, `wc`, `command ls`, and Python scripts on standard input that read files and printed to standard output). No git command was run. Some commands of this task broke the read-only Bash form (one created an empty scratchpad file); AUTHOR-NOTES §5 lists each.
- **Not run.** No compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. Nothing under `/srv`.
- **Not read.** `WT/packets/capi-pk0/`; every `gpt61-v*` directory; the v6 review's `raw-final-message.txt` and `review-records/`; `~/.local/share/sia/.gbrain/`; any other agent's transcript. The lane draft and its preimage were read and not changed.
- **SIA.** No SIA call was made in the v7 task. No SIA note was written.
- **Skills.** The eight Ada skills were loaded in this session before Ada reading: `ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`.
- **JACKAL.** Two calls (Appendix A).

### C.2 Bases (aliases), for every version's text

Carried text of every version uses the aliases below. Where two versions gave one alias different meanings, the column "Applies in" says which meaning holds inside which version's text. Inside v1 slices, v1's own notation applies as well (slice B-NOTATION, v2 RR1).

| Alias | Path | Applies in |
|---|---|---|
| `W` | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` | all |
| `WT` | `W/work/claude-lead-isolation-v1/wt-1` | all |
| `L` | `W/work/protected-original-root-worker-repair-v1` (the draft lane) | all |
| `R` | `L/source`. Unprefixed `core/…`, `runtime/…` and `protected-*/…` paths are relative to `R`. | all |
| `rw/` | `R/runtime/worldline/` | all |
| `pre/` | `L/preimage/runtime/worldline/` (the lane's immutable primary copy) | v6, v7 |
| `C1` | `R/protected-root/native_root_worker_supervisor_v1.c` | v6, v7 |
| `RW:n` | `L/handoff-to-claude-v1-retry1/HANDOFF.md`, line n | v1, v2 |
| `P1/`, `P1:n` | the directory `W/outputs/claude-phase1-handoff-20261004/`; its `HANDOFF.md`, line n | all |
| `PROMPT`, `PROMPT:n` | `/home/sicarii/Documents/complete-phase1-prompt.txt` (line n) | v1 … v4 |
| `S4` | `W/work/reviewed-common-proof-source-composition-v4/source` (commonV4) | v2 |
| `S5` | `W/work/claude-composition-v5-beta/source` | v2 on |
| `D1V` | `WT/designs/claude-root-worker-seam-design-v1` (v1 design and its sealed review) | v2 |
| `D2` … `D6` | `WT/designs/claude-root-worker-seam-design-v2` … `-v6` | v3 on |
| `D2R` | inside v2 text: `WT/designs/claude-d2-checked-ghost-inventory-v1/review/gpt61-v1` (the D2 checked-Ghost inventory review); inside v3 and later text: `D2/review/gpt61-v1` | as stated |
| `D2D` | `WT/designs/claude-d2-checked-ghost-inventory-v1` | v2 |
| `D3R`, `D4R` | `D3/review/gpt61-v1`, `D4/review/gpt61-v1` | v4, v5 |
| `D5R`, `D6R` | `D5/review/claude-v1`, `D6/review/claude-v1` | v6, v7 |
| `D:n` | v2 `SEAM-DESIGN.md`, line n | v3, v4 |
| `D2:n` … `D6:n` | that version's `SEAM-DESIGN.md`, line n | v4 on |
| `CAPI3R` | `WT/designs/claude-capi-boundary-design-v3/review/gpt61-v1` | v2 |
| `CAPI4`, `CAPI5`, `CAPI6` | `WT/designs/claude-capi-boundary-design-v4`, `-v5`, `-v6` | v2 on |
| `CAPI4R`, `CAPI5R`, `CAPI6R` | `CAPI4/review/gpt61-v1`, `CAPI5/review/gpt61-v1`, `CAPI6/review/gpt61-v1` (sealed) | v3 on |
| `CHILD` | `W/work/resource-child-authority-source-v1` | v2 on |
| `A1` | `W/work/scoped-committed-envelope-repair-v2-retry1` (as an alias; as a lane name, v2 RR3) | v2 on |
| `RQC` | `R/protected-canonical/required_controls.json` | v2 on |

### C.3 Status labels

- **OBSERVED:** read from a file or from a command's output in this task.
- **[static reasoning] / STATIC_REASONING:** reasoned from what was read; nothing was executed.
- **[unverified reasoning, X]:** the author's reading of kernel, systemd, SQLite, interpreter or loader behaviour. It is settled only by the named measurement item (K-n, under OP-7) or installed-runtime check (RC-n, lead-owned).
- **(bound to the sealed CAPI6R):** relies on a C-API rule whose sealed review closes it at design level only.
- **DESIGN:** proposed by a design; unimplemented and unreviewed.
- **OPEN:** an obligation not met.

### C.4 Numbers

Line numbers, counts, sizes and hashes in this document are observed. Two arithmetic facts behind the capacity rule were checked with JACKAL: J7-1 and J7-2 (Appendix A). Numbers inside carried slices keep their status (RR7-5).

### C.5 Two families named "RC"

- **Inherited required changes** of the v1 review: RC-01 … RC-12 (v2 §A.1, carried). Carried text sometimes writes RC-10, RC-11 or RC-12 without the leading zero, always as a required change: for example v2:235, v2:236, v2:1625, v2:1648, v2:1936, v2:2261, v4:1827, v5:137 and v5:1525. These are untouched.
- **Lead-owned installed-runtime checks:** RC-1 … RC-9 as before, and the checks earlier named RC-10, RC-11 and RC-12, renamed here **RC-13**, **RC-14** and **RC-15**. RC-13 is the `KernelPeer.observation ()` closed-connection check (V5-N; the selector of V6-I.1's branch); RC-14 is the dynamic-loader check (V6-M); RC-15 is the `systemd-run --pipe` exit-status check (V6-O). The rename is made by quotation at every carried occurrence (RR7-7). No check's content changes.

---

## V7-A. Material names, the `decide_v2` roster, the capacity rule and `fold` (V6-REQ-A; 01.1, 11.1; D-1a, D-2a, D-5a, D-9a)

### V7-A.1 Names and the `decide_v2` roster

| Name | Meaning | Where |
|---|---|---|
| `param_count` | the number of serialized parameters in a material | material header (R7-45) |
| `param_index` | a parameter's position in its export's `PARAMETERS` roster, from 0 | each material entry (R7-46) |
| `slot_kind` | the material's own classification of a parameter: 0 record, 1 arena, 2 roster | each material entry (R7-46) |
| `record_kind` | the layout's record-kind index, the first argument of `wl_<unit>_layout_v<N> (kind, field)` (V6-A.1) | the sub-helper's roster table (R7-48) |
| `m` | the SHA-256 of the whole material, and nothing else | material, `CHILD_MEASURED`, `COMMIT_CHILD_REQUEST`, `COMMIT_CHILD_GO` (R7-47) |

For a record parameter the roster table gives its `record_kind`; for an arena, none (its byte length is its size word); for a roster, the `record_kind` of its element record.

**The `decide_v2` roster.** `wl_resource_child_execution_decide_v2`'s `PARAMETERS` roster is V1's (`rw/resource_child_execution.py:207`) in V1 order, with `FactsV2` and then `Selection` inserted immediately before `Output` (R6-7). Both are rosters (`slot_kind` 2; size word = element count) whose `record_kind`s are R6-7's (k) and (k+1). The material serializes this roster without `Output`, so `decide_v2`'s `param_count` is V1's `param_count` plus the two inserted rosters. The X-8 convention-P argument list (R6-7) is exactly this roster's pairs, in this order, then the output record.

### V7-A.2 The capacity rule

For one call of `next` or `fold`, the wrapper passes:
- **Output roster capacities.** `next`: one `RootStateRec`; and `SubjectStateRec`s numbering the input subject rows plus the rows the event creates: one for an event that creates a subject, and, for `FRONT_OWNED (g+1)`, one per Queued or Abandoned request carried from g (v5 V5-F.2). All of these the wrapper counts from the inputs. `fold`: one `RootStateRec`, and as many `SubjectStateRec`s as the stored subject rows plus one. A fold that would need more rows than that already disagrees with the stored rows, and reports the stored-rows mismatch (RT-14 class), never `Capacity_Short`.
- **Output arena capacity** C = F × (M + 1), where F is the number of span fields (Id and quantity fields) in the output rows those capacities allow, and M is the largest span length in the input arena.

**Why it suffices [static reasoning].** Every span `next` or `fold` writes is a copy of an input span, of length at most M, or the successor of an input quantity: the generation g+1, `Reattach_Epoch` n = current + 1, a sub-generation s+1, or any other quantity `Next` increments. The successor of an n-byte magnitude needs at most n + 1 bytes, because only the magnitude whose n bytes are all `0xff` carries into a new byte, and it becomes 256ⁿ, one followed by n zero bytes (JACKAL J7-1 for n = 8 and J7-2 for n = 16: (2^64 − 1) + 1 − 256^8 = 0 and (2^128 − 1) + 1 − 256^16 = 0, status `exact`). So each of the at most F output spans fits in M + 1 bytes. The review's own example, epoch 255 → 256 (its J6-1), is the case n = 1.

### V7-A.3 `fold`'s convention

`fold` is convention T with no Input record: every operand is a roster, so there is nothing for an Input record to carry. Its arguments are the Arena pair, the `EventRow` triple, the stored `RootStateRec` and `SubjectStateRec` triples, the output triples, the output-arena pair and `PhaseResult` (R7-43). It is the second observed-style variant of T, beside `wl_chain_authority_replay_v1`, which has no arena (V6-A.2).

---

## V7-B. CG-2's basis corrected (V6-REQ-B; 01.7; D-1a, D-1b)

R7-49 replaces V6-B's statement of where the root unit's properties come from. They are the root-worker plan's `worker_policy`, as `unit_properties ()`, admitted at DISPATCH under the WL request's reservation (`rw/root_worker_plan.py:22`, `:37`; `rw/protected_root_resource.py:38`, `:50-51`, `:68-71`). The catalogue `cost_key` is the WL operation's (`:39-41`). CG-2's gap, closure condition, independence from D-4a and control V6-N.B are unchanged; the bound an IP handler draws on is that `worker_policy` bound.

---

## V7-C. No carried D-4a dependence; CG-4 (V6-REQ-C; 06.4; D-1b, D-4a)

- **S10** (R7-17) no longer says a selected specification needs D-4a. It is consistent with CG-3 (v6 V6-C) and with V7-K.7: closure of CG-2 and CG-3 does not depend on D-4a, and an authoritative resource-policy change would stay the operator's under the existing reservation (OP-3).
- **CG-4** (R7-73): its closure condition does not depend on D-4a; D-4a can neither waive nor close it; no resource-policy change is proposed for it. `seams.json` records `depends_on_d4a: false` for CG-1 … CG-4.
- **The full sweep's other D-4a findings.** Three further carried lines made later requests wait for a D-4a selection: v2:1363 (R7-1), v2:1909 (R7-2) and v4:427 (R7-6). Each is replaced by quotation. Every other carried mention of D-4a is a reservation of the operator's authority over an authoritative resource-policy change, or a heading or ruling label, and is kept (AUTHOR-NOTES §2 lists each).

---

## V7-D. The dispatcher's outcome and the persisted supervision text (V6-REQ-D; 03.3; D-5a)

### V7-D.1 `result` and OOM

The original `outcome` returns `result` ∈ {`stopped`, `failure`, `success`, `None`} (`rw/linux/systemd.py:704-709`). The dispatcher returns the same set (R7-53). An OOM kill reaches the runner in the original only through sampled telemetry: `resource_telemetry` reads the unit's `memory.events` and sets `hitMemoryCeiling` and `oomKilled` (`:518-531`), and the runner keeps any `true` it has seen (`rw/runner.py:794-797`); `ceilingFired` then holds (`:937-939`). The runner's `manager_result == "oom-kill"` branch (`:938`, `:942`) is unreachable in the original, because `outcome` never returns that value, and it stays unreachable with the dispatcher. The dispatcher's `resource_telemetry` reads the leaf's `memory.events` the same way (R7-54).

### V7-D.2 Every persisted field and message

| Supervision field (`rw/linux/systemd.py:694-715`) | Original value | Dispatcher value | Persisted at (`rw/runner.py`) | CJ-DISP-4 |
|---|---|---|---|---|
| `kind` | `SUPERVISED`, `LAUNCH_FAILED`, `INDETERMINATE` | the same classification | `:967`, `:986`, `UNIT_LAUNCH_FAILED` details `:949` | (i) must equal |
| `unit` | the unit name | the leaf unit name, the same string | as above | (ii) equal |
| `source` | `journal`, `journal-unavailable` | `child-closure`, `child-closure-unavailable` | as above; and the `SUPERVISION_INDETERMINATE` reason text (`:982`) | (iii) differs |
| `launcherExit` | the launcher's exit | the integer `launcher.wait ()` returns (RC-15) | as above | (ii) must equal |
| `started` | the journal's started entry | `kind = SUPERVISED` | as above | (ii) must equal |
| `supervisionEvidence` | `started-entry`, `process-exit-entry`, `None` | `child-ready-and-closed`, `None` | as above | (iii) differs |
| `stoppedByManager` | the manager stopped the unit | a `STOP_UNIT` was executed | as above | (ii) must equal |
| `exitCode`, `exitStatus` | from the exit entry | from `CLOSED_CHILD`'s main status, in the original's form | as above | (ii) must equal |
| `result` | `stopped`, `failure`, `success`, `None` | the same | as above | (i) must equal |
| `windowMilliseconds` | the adapter's window | the same value | as above | (ii) equal |
| `events` | journal entries | closure-frame records | as above | (iii) differs |
| `launcherStderr` | `systemd-run`'s stderr, truncated | the helper's diagnostic text, truncated the same way | as above; and its first line in the `UNIT_LAUNCH_FAILED` message (`:945-948`) | (iii) differs |

| Message (`rw/runner.py`) | Code and template | What differs |
|---|---|---|
| `UNIT_LAUNCH_FAILED` (`:944-950`) | equal: raised from `kind` | the message's suffix (first line of `launcherStderr`) and the `supervision` detail |
| `SUPERVISION_INDETERMINATE` reason (`:981-982`) | equal template, including its words "the manager's journal" | the `source` value; with the dispatcher, the template's words name a journal that was not the evidence source |
| `RESOURCE_LIMIT_EXCEEDED` reason (`:977-980`) | equal; `ceilingEvidence` "cgroup memory.events sampled during the run" on both when `hitMemoryCeiling` is set | none, subject to CJ-DISP-5's sampling window |

The runner's code is unchanged, so these texts are produced by the original code from the dispatcher's values. Every (iii) difference is a stated difference in durable evidence text. No classification, status, refusal or decision depends on it, and no equivalence is claimed for it.

---

## V7-E. X-1 per-caller modes and both refusal tables (V6-REQ-E; supersedes V6-E.4; 02.1, 12.1; D-2a, D-7a)

### V7-E.1 One mode per call site

The original Python check runs first, unchanged, and raises its original class at its original point. X-1 is consulted only after that check has accepted the bytes, with `JsonInput.mode` equal to the call site's own setting (R7-16):

| Call site (`rw/…`) | Original check | `canonical_required` | X-1 `mode`, `form` |
|---|---|---|---|
| `protected_startup.py:172` (descriptor), `:189` (genesis) | `exact_json` | true (default) | Canonical, UTF8 |
| `root_worker_journal.py:42` (custody genesis) | `exact_json` | true (default) | Canonical, UTF8 |
| `protected_startup.py:682` (proof manifest), `:706` (run-scoped `config.json`) | `exact_json` | false | Lenient, Detected |
| `protected_operations.py:624`, `:723`, `:729`; `canonical_owner_witness.py:25` (the request document, X-6) | `exact_json` over the request's `rawRequest` | false | Lenient, Detected |
| `protected_resource_runtime.py:22-23` | `exact` | (canonical comparison always) | Canonical, ASCII |
| the crosswalk loader (new in v4; no original call site) | — | — | Canonical, UTF8; its file is new and provisioned canonical (OP-1), so no original accepted input exists to refuse |

`Detected` means the encoding `json.loads` selects for bytes (`json.detect_encoding`: UTF-8, UTF-8 with a byte-order mark, UTF-16 or UTF-32) **[unverified reasoning, RC-5]**. In Lenient mode `trailing_lf` is ignored: leading and trailing JSON whitespace of any length is accepted, as `json.loads` accepts it.

### V7-E.2 Canonical mode (`exact_json` with `canonical_required` true, and `exact`)

| Input | `exact_json` (form UTF8; `rw/protected_startup.py:40-51`) | `exact` (form ASCII; `rw/protected_resource_runtime.py:22-23`) |
|---|---|---|
| not JSON, bad UTF-8 | `json.JSONDecodeError` (a `ValueError`), or `UnicodeDecodeError` | the same |
| a duplicate key | `StartupRefusal` `STARTUP_DUPLICATE_JSON_KEY` | the last value is kept by `json.loads`; the canonical comparison then fails: `ResourceProducerRefusal` `RESOURCE_NONCANONICAL_PROTECTED_RECORD` |
| `NaN`, `Infinity`, `-Infinity` tokens | `StartupRefusal` `STARTUP_NONFINITE_JSON` (`:48`) | a non-finite float, then `ValueError` from `json.dumps (…, allow_nan=False)` |
| an overflow lexeme such as `1e309` | an infinite float, then **`ValueError`** from `canonical`'s `json.dumps (…, allow_nan=False)` (`:35-37`, called at `:50`) | the same `ValueError` |
| an integer lexeme longer than the interpreter's integer string-conversion limit (`sys.get_int_max_str_digits ()`) | `ValueError` raised inside `json.loads`, before any comparison | the same |
| a string escape that decodes to a lone surrogate | accepted by `json.loads`; then `canonical`'s UTF-8 encoding raises `UnicodeEncodeError` (a `ValueError`) | accepted: `ensure_ascii=True` re-escapes it, so the comparison can hold |
| any non-canonical spacing, order, escape or number form | `StartupRefusal` `STARTUP_NONCANONICAL_JSON` | `ResourceProducerRefusal` `RESOURCE_NONCANONICAL_PROTECTED_RECORD` |

### V7-E.3 Lenient mode (`exact_json` with `canonical_required` false)

| Input | Original outcome | X-1 Lenient verdict when consulted |
|---|---|---|
| not JSON, or non-whitespace after the value | `json.JSONDecodeError` | not consulted |
| bytes not valid in the detected encoding | `UnicodeDecodeError` | not consulted |
| a duplicate key, at any depth | `StartupRefusal` `STARTUP_DUPLICATE_JSON_KEY` (the pairs hook, `:41-46`) | not consulted |
| `NaN`, `Infinity`, `-Infinity` tokens | `StartupRefusal` `STARTUP_NONFINITE_JSON` (`:47-48`) | not consulted |
| an integer lexeme over the conversion limit | `ValueError` inside `json.loads` | not consulted |
| an overflow lexeme such as `1e309` or `-1e309` | **accepted**; the value holds an infinity with the lexeme's sign | `Ready`, value kind Number; `Number_Not_Finite` is never returned for a lexeme in Lenient mode |
| an underflow lexeme such as `1e-400` | accepted; a zero with the lexeme's sign | `Ready` |
| any non-canonical spacing, key order, escape or number form; leading or trailing whitespace | accepted | `Ready` |
| a string escape that decodes to a lone surrogate | accepted | `Ready` |
| a byte-order mark, UTF-16 or UTF-32 (bytes callers) | accepted by encoding detection | `Ready` (form `Detected`) |

All rows are **[unverified reasoning, RC-5]** for the installed CPython's `json`. `archive_equal` over a Lenient container compares an overflowing non-integer lexeme with the binary64 infinity of its sign, and an underflowing one with the zero of its sign: `Round` (v5 V5-C.3) gains these two saturating results, which CJ-ARCH-2 then covers.

### V7-E.4 CJ-JSON per mode

**CJ-JSON (OPEN).** For every call site of V7-E.1 and every byte string the site's original check accepts, X-1 with that site's `mode` and `form` returns `Ready`. Native statuses never stand in for an original exception: the original raises first. So `SOURCE_JSON_NATIVE_DISAGREES` can be reached only if CJ-JSON is false for that mode; the proof of CJ-JSON must exclude it for every input Python accepts, in both modes. It is a correspondence failure refused fail-closed, never an accepted refusal of an original case.

---

## V7-F. Custody-return evidence: rows, pairing and boot identity (V6-REQ-F; 04.4, 12.2, 12.4; D-6a, D-8b, D-9a)

### V7-F.1 What the front records at HELD

When the HELD frame arrives (it carries the init's host pid p at `C1:241` and its pidfd P at `C1:247`), the front:
1. reads `/proc/self/fdinfo/<P>` and requires its `Pid:` to equal p (the pairing of pid and pidfd) **[unverified reasoning, K-4]**;
2. reads the start tick t from `/proc/p/stat`;
3. then polls P. If P is not readable, the process P refers to was alive throughout, so p could not be reused between steps 1 and 3 and t belongs to it **[unverified reasoning, K-4]**; the `HELD` event records p, t and the boot identity. If P is readable at step 1 or step 3, the init has already exited; the `HELD` event records p, the boot identity and `init_exited_at_held`, with no start tick. This adds no refusal: the launch path continues exactly as before, and that generation's closure follows from P, as it would anyway;
4. reads the boot identity, `/proc/sys/kernel/random/boot_id`, as the original reads it (`rw/protected_scoped_resource_runtime.py:145`).

The worker's start tick is already read through the worker pidfd (`rw/protected_root_resource.py:129-134`). The `EXECUTION_NATIVE` record also carries the boot identity.

### V7-F.2 Identity gone

As R7-59 states: a different boot identity, `ESRCH`, a different start tick read while the new pidfd is held, or `init_exited_at_held`. K-29 is new under OP-7's existing D-8b reservation (V7-O).

### V7-F.3 Carried rows replaced

RT-25, RT-26 and RT-27 (R7-23 … R7-25) and lemma OWN-1 (R7-21) now require the worker gone or E-CR. The sweep found four more pidfd-only statements and replaced them: RT-13 (R7-12), the UNKNOWN routing row (R7-13), "Finding the worker" (R7-26) and the V5-F control's `CUSTODY_RETURNED` refusal (R7-86). The closure-barrier rows that say "pidfd terminal" (`CLOSED_NS`, `CLOSED_OUTER`, the terminal pidfds of `Physical_Closure`) concern physical closure, which the front can only observe through the pidfds it holds; clause 04.5 closed them, and they are not custody-return evidence. They are kept.

---

## V7-G. Cause classes as operands, and one set of routes back (V6-REQ-G; 04.1, 09.5, 12.4; D-9a)

### V7-G.1 The cause record as an X-5 operand

While the root is Unknown, the `EvidenceRec` roster passed to `legal` and `next` carries the cause record as kind `Cause_Record`, with `value` its bytes (R7-43). X-5 requires its SHA-256 to equal the root state's `unknown_cause` (`RootStateRec`, V6-A.4) and reads from it the class and, for C-APPEND, the failed event's replay identity and record digest. A roster with no `Cause_Record`, or one whose digest differs, gives no decision for `RECONCILED`. No `RootStateRec` field, root_state column or DDL entry is added, so 04.3 and 12.1 stay as the review closed them.

### V7-G.2 Routes back, by class

| Class | `RECONCILED` target | Evidence (the operand and durable records) | After it |
|---|---|---|---|
| C-CHANNEL | `Before_Unknown` (a worker phase) | a committed `WORKER_REATTACHED (n)` after the `UNKNOWN` event; the worker's identity live (V7-F.2) | service resumes |
| C-DEADLINE | as C-CHANNEL | as C-CHANNEL | service resumes |
| C-APPEND | `Before_Unknown` | the chain verified in the custody transaction (X-4 `Ready`, X-5 `fold` equal); the worker's identity live if `Before_Unknown` is a worker phase | (a) replay hit: nothing more; (b) no event with that replay identity: the phase owner re-decides and re-appends it under `Legal` |
| C-EVIDENCE | none | — | only E-CR (`CUSTODY_RETURNED`) or other authentic evidence; no liveness is claimed |

For every class, evidence E-CR leads to `CUSTODY_RETURNED` (R6-18) instead. `Before_Unknown` is the folded phase at the `UNKNOWN` append, so it already reflects a persisted failed event; that is why C-APPEND's route needs no re-append in case (a) and is not circular in case (b).

### V7-G.3 One statement in three places

R6-19's result (R7-36), R6-24's Unknown row (R7-38) and V6-G.2 (R7-61, R7-62) now give exactly the table above. V6-G.3 item 2 states its wait as a difference (R7-63).

---

## V7-H. The front after `HANDOFF_ABORT`, and `Release_Hold`'s scope (V6-REQ-H; 07.3, 12.2; D-6a, D-9a)

### V7-H.1 The in-memory phase replaces `rw/protected_root_worker.py:192`

In the lane, `:192` sets `self.phase='UNKNOWN_WORKER_OWNERSHIP'` on every failure after `_reserve`; `invoke` then refuses at `:159` (`ROOT_WORKER_PRIOR_OWNER_UNKNOWN_OR_LIVE`), and the router at `rw/root_worker_endpoint_router.py:22` sends every later request to the collectors path. DESIGN for the successor:

| Situation after the failure | Custody commits | Front's in-memory phase | Next request |
|---|---|---|---|
| `HANDOFF_ABORT (g, class)` with `Owners_Open` (the front's owners were never closed) | `HANDOFF_ABORT`, then after the original exception handling (`:193-198`) `HISTORICAL_SETTLEMENT (g)` and `FRONT_OWNED (g+1)` | `FRONT_OWNED`, set in the same step as the `FRONT_OWNED (g+1)` commit, with the front's generation g+1 | passes `:159`; the router at `:22` sees `FRONT_OWNED` and dispatches to the same daemon (`:32-34`) |
| `HANDOFF_ABORT (g, class)` without `Owners_Open` | as above through `HISTORICAL_SETTLEMENT (g)`; then the Collector's `FRONT_RECONSTRUCTION` and `FRONT_OWNED (g+1)` | `HANDOFF_ABORTED`, and a reconstruction task is registered in `front.collectors` before `invoke` re-raises; the task ends with `RECONSTRUCTED_CLOSED` and `fresh_front` set, exactly as `collect_and_reconstruct` does | the router awaits that task (`:22-25`) and switches to the fresh front (`:26-31`) |
| a custody commit of the rows above fails | `UNKNOWN (C-APPEND)` (V7-G) | `UNKNOWN_WORKER_OWNERSHIP`, and a task is registered in `front.collectors` that waits for `RECONCILED` and the follow-up commits and then sets the phase as in the rows above | the router awaits that task; the router successor also accepts the same front back in `FRONT_OWNED` after the wait (a successor change to `:26-31`) |

The original exception handling is unchanged: `owned.retain_and_stop_unknown` when a dispatch owner exists, otherwise `p.quarantine`. With `:192` gone, the `elif` at `:195` becomes the plain alternative (R7-65). No refusal is added; the response to the failed request is the original error response (V5-G.1 step 6).

### V7-H.2 `Release_Hold` only for `Held_Capacity`

`Release_Hold` requires `Before.Kind = Held_Capacity`, and `Charge_Budget` requires `Irreversible_Budget` with `Terminal` and `Reaped` (`core/resource_run_ledger.ads:317-322`). On a `Never_Launched` abort the root row (one row per reservation, `rw/protected_root_resource.py:42-44`) is therefore released only if it is `Held_Capacity`. An `Irreversible_Budget` root row has no command; it keeps its state and budget, as the original leaves it, and the U record's quarantine leads to owner resolution (K4). `Released_Unlaunched` is set only with a `Release_Hold`. R7-4, R7-5, R7-19, R7-20, R7-22, R7-64 and R7-77 carry this into every carried statement.

---

## V7-I. RELAY transport loss, re-derivation and frame order (V6-REQ-I; 09.2, 09.4; D-8a, D-8b)

### V7-I.1 Waiting for evidence, not deciding from the loss

The worker never raises because the channel failed (R7-37). It waits for a reattach. For each pending (g, r, s) the reattached front sends one `PEER_STATUS` frame in the RELAY framing of V5-I.5 for the new epoch n, MAC'd and bound to (g, r, s):
- **`PEER_HELD`**, with `next_out_seq`: the front holds the request's `RequestPeer` (its connection, open or closed by the client). The worker re-issues the pending gate request, and re-sends every output frame from `next_out_seq` on (V7-I.3). The front performs the original re-read, so the gate gets exactly what the original gives.
- **`PEER_LOST_WITH_FRONT`**, with the recorded identity of the front that held the connection (its host pid, start tick and boot identity, which `REQUEST_TRANSFER_INTENT` records, V7-I.2) and the result of V7-F.2's test on it. The reattached front sends it only when it is a different process from that front and that front's identity is gone; a front that ends closes every descriptor it holds, the client connection included **[unverified reasoning, K-6]**. Only then does the worker take branch (a) or (b), as RC-13 selects.

A front that is alive and lost only the channel reattaches itself and answers `PEER_HELD`, so branch (a) is never taken while the client may be connected. A worker whose front never reattaches waits, which is V5-L.2's carried "does not complete the reattach" row (OP-8).

### V7-I.2 Re-derivation in the custody owner

`RequestPeer.capture (writer, line=line, …)` keeps the line (`rw/daemon.py:342-343`), and the request observation carries it as `rawRequest` (`rw/protected_operations.py:624`). `REQUEST_TRANSFER_INTENT`'s record holds that observation and the transferring front's identity (pid, start tick, boot identity). The custody owner, FRESH or RELAY, re-derives `request_id`, `operation_name`, `args` and the operation entry by running the daemon's parse and validation code (`rw/daemon.py:318-332`) over exactly those bytes; it obtains what the front obtained, because the same code runs on the same bytes **[static reasoning]**. The owner-only account check (`:333-337`) is not repeated (R7-69).

### V7-I.3 One output order per request

Every frame the front writes to the client for (g, r, s) carries `out_seq`, from 0 and increasing by one in production order: each progress line takes the next number when the handler emits it; the response takes the next number when `canonical_bytes (value) + b"\n"` is produced (`rw/daemon.py:397`); later progress from detached work takes later numbers. The front writes frames strictly in `out_seq` order, holds a frame whose predecessor has not arrived, and drops a frame whose number it has already written. The worker keeps each frame until `RESPONSE_WRITTEN` or a `PEER_STATUS` shows it written. So the client's writer receives progress and response in the order the original's single writer receives them (`:339-340`, `:390-400`).

---

## V7-J. The child factory's fork point and descriptors (V6-REQ-J; 03.2; D-3a, D-5a, D-5b, D-8b)

R7-71 fixes the fork point: after argument validation (`C1:308-322`), before `connect_owner` (`C1:323`), so before any of the descriptors of `C1:323-335` exists. R7-72 adds the close-all-except list: 0, 1, 2 and F's socketpair end, plus, during one request only, the leaf cgroup descriptor and F's end of the new sub-helper socketpair. Each alone keeps F free of the owner connection, the custody and actor socketpairs and the go, report, out, err and stdin pipes; together they make the property independent of what the unit inherited. Last-writer EOF (V4-H.5, the closed V4-REQ-H) and channel EOF (C-CHANNEL) are therefore unaffected by F. Control V7-N.J.

---

## V7-K. H′, complete (V6-REQ-K; supersedes V6-K; 02.4, 06.2; D-4a)

### V7-K.1 Structure

- **Service-class coordinator.** One per custody generation. It holds store custody and runs every handler and the job runner, as the original daemon does (`rw/protected_operations.py:750-754`; `rw/runner.py:694-703`). Its unit's limits are the installed daemon service's own, read back (RC-9) and set once. It holds no request's reservation.
- **Request root.** For each WL request, its own top-level reservation (parent none) is reserved by `_reserve`, passes pre-effect and commits `EFFECT_INTENT` as the root invoke does (`rw/protected_root_worker.py:162-171`), and is dispatched **once**, as a request-root unit, by D-H7 (V7-K.2), with the policy of V7-K.3. Its main process is the root helper v2 in holder mode: its init holds the delegated subtree and execs nothing.
- **Per-agent launches.** Each runner launch (`rw/runner.py:697-703`; one per agent, several per request) is a **child task of that same request's root**: `TASK_INTENT`, child Reserve with `Task_Admission` (parent = the request's own root reservation), the child `Record_Launch_Intent`, `CREATE_CHILD` to that request's helper, HELD, Running, GO, measurement, agreement, READY and exec. The dispatcher (V6-D) presents it to the runner. No reservation is dispatched twice, and no child is made top-level: the lane's own text keeps child dispatch for "the child task/parent controller successor" (`rw/protected_scoped_resource_runtime.py:720-723`).

### V7-K.2 D-H7: launching a request root while the coordinator owns custody (DESIGN)

The front's owners are closed while a coordinator owns custody (`rw/protected_root_resource.py:161`), and the coordinator cannot reach the manager (M-4). `launch_reserved` requires a sandbox `argv[0]` (`rw/protected_scoped_resource_runtime.py:732-735`), and `launch_root_worker` uses `handler_plan`'s `worker_policy` and coordinator argv; neither fits. D-H7 is the request-root launch, run by the coordinator as custody owner, step for step against `launch_reserved` (`:698-776`):

| Step | `launch_reserved` (original) | D-H7 |
|---|---|---|
| 1. checks | journal row `NEVER_DISPATCHED`, no slot, original request unchanged (`:703-708`) | the same, in the coordinator |
| 2. plan | `resource_launch_material` (`:711`), whose non-root branch returns `policy['plans'][op]['launch']` with its executable checks (`rw/protected_operations.py:476-485`) | the same branch and checks. The plan's `policy` and `systemd_properties` are used, with `enforcement == 'cgroup2'` and `systemd_properties == policy.unit_properties ()` required exactly (`:729-731`). The plan's `argv`, `environment` and sandbox check (`:732-736`) apply to each per-agent child (V7-K.1), not to the request root's main process |
| 3. reservation | one RESERVED top-level row whose bound is the plan's (`:714-723`) | the same |
| 4. machine admission | `machine_admission (reservation, policy, 'DISPATCH')` (`:739`) | the same call, the same policy |
| 5. launch intent | `RECORD_LAUNCH_INTENT` with planned unit `worldline-resource-<reservation>.service` (`:740-742`) | the same command and unit name |
| 6. endpoint | a `SOCK_SEQPACKET` listener at `<runtime>/resource-supervisor/<reservation>` (`:744-748`) | the coordinator's root helper (outside the namespaces) creates the listener at that path and passes the listening descriptor to the coordinator over the helper channel; the coordinator holds it as a custody descriptor of the request slot |
| 7. dispatch intent | `DISPATCH_INTENT` with ticket, endpoint, row, plan, launch packet and helper arguments (`:749-757`) | the same record; helper arguments are `[helper, endpoint, ticket, '0', '0', cwd, '--holder']` |
| 8. launch | the daemon runs `systemd-run --system --no-block --unit=… --property=Type=exec --property=RemainAfterExit=yes --property=Delegate=no --property=User=root --property=Group=root` with `--property=` for each of the plan's `systemd_properties`, then the helper arguments (`:760-765`) | helper command **`LAUNCH_REQUEST_ROOT`**: the coordinator sends that exact argv in a sealed memfd (V5-E.3 framing) to its own root helper, which checks the frame, runs it with the original's environment (`PATH`, `LANG`) and returns the exit status; non-zero is the original `SCOPED_SYSTEM_MANAGER_DISPATCH_UNKNOWN` (`:765`) |
| 9. held and running | `accept_held`, `RECORD_RUNNING` with the actual unit, cgroup and invocation, `go`, close empty input (`:766-769`) | the same commands; the holder init then waits and execs nothing |
| 10. failure | phase-conditional `UNKNOWN` append (`:770-776`) | the same, as V6-H.2 |

The request slot (endpoint, HELD descriptors) is a custody slot of the coordinator's generation, transferred at the coordinator's handoff as any slot is (V5-H, D-H4).

### V7-K.3 Policy source, and every resource-policy field

The request root's policy is the WL operation's own launch plan's `policy`, `policy['plans'][op]['launch']['policy']`: the policy the serial route admits at its fresh boundary (`rw/protected_operations.py:687`) and the one `launch_reserved` enforces for that reservation (`rw/protected_scoped_resource_runtime.py:729-731`). It is not `worker_policy`. Per-agent leaves take the runner's own `resource_properties=self.gate.unit_properties ()` (`rw/runner.py:697-703`).

Every `ResourcePolicy` field (`rw/admission.py:76-85`):

| Field | Enforced as (`unit_properties`, `rw/admission.py:146-177`) | Original request unit (`launch_reserved`) | H′ request root | Original per-agent unit (the runner's gate) | H′ per-agent leaf | Changed? |
|---|---|---|---|---|---|---|
| `memory_max_bytes` | `MemoryMax=` | the plan's value | the same plan's value | the gate's value | the same value, as the leaf's `memory.max` (CJ-DISP-6) | no |
| `memory_high_bytes` | `MemoryHigh=` | plan | same | gate | same, `memory.high` | no |
| `memory_swap_max_bytes` | `MemorySwapMax=` | plan | same | gate | same, `memory.swap.max` | no |
| `cpu_quota_percent` | `CPUQuota=` | plan | same | gate | same, `cpu.max` | no |
| `cpu_weight` | `CPUWeight=` | plan | same | gate | same, `cpu.weight` | no |
| `tasks_max` | `TasksMax=` | plan | same | gate | same, `pids.max` | no |
| `disk_growth_max_bytes` | no unit property; read by its original users | plan | same policy object | gate | same policy object | no |
| `timeout_seconds` | no unit property; the runner's timeout | plan | same | gate | same; the runner's own code | no |
| `max_concurrent_workloads` | no unit property; admission's concurrency limit (`rw/admission.py:696`, `:716`) | plan, at machine admission | same, at the same machine admission | gate, at `gate.guard` | the same `gate.guard`, unchanged code | no |
| `enforcement` | `cgroup2` required (`:730`; `rw/admission.py:162-163`) | plan | same | gate | same | no |

The accounting properties `MemoryAccounting`, `CPUAccounting`, `TasksAccounting` and `IOAccounting` are always on, on both sides. No field is added, removed or changed, and the catalogue `cost_key` and its `Cost_Join` are the request's own.

**Differences that are not policy fields (stated, OPEN where marked):**
- the request root's main process is the root helper v2 in holder mode (uid 0, no plan argv), where `launch_reserved`'s is the V3 actor helper running the plan's sandbox argv (D-H3, D-H7);
- each agent's leaf is nested inside its request root, so the request root's limits also bound the sum of its agents. That matches `launch_reserved`, where the request's workload runs inside the unit with the plan's limits; but the original runner's per-agent units (`systemd-run --user`, `rw/linux/systemd.py:179-197`) are not nested in any per-request unit. Whether that nesting refuses any original accepted case is **CJ-H-5 (OPEN)**;
- child ledger rows (`Task_Admission`) exist for each agent; their correspondence with `gate.guard` admission and with the per-agent amounts is CJ-H-1 and CJ-H-2 (OPEN);
- D-H2 adds a native decision mode for the coordinator's launch. It adds no field to `ResourcePolicy`, the plan catalogue, the operation policy or the admission ledger, writes no run-ledger row, and decides on no machine-admission or run-ledger quantity: it checks only that a coordinator launch matches the installed service's read-back properties (RC-9) and the custody generation, as the daemon itself is admitted by no reservation;
- AO-8: the coordinator's service-class limits exist beside the front's.

### V7-K.4 AO marks (revised)

| AO | H′ | Basis, or the obligation left OPEN |
|---|---|---|
| AO-1 grant and use | part | Each request reserves its own grant and use, and the coordinator holds none; CJ-H-1 (the runner's `gate.guard` against the child rows) OPEN |
| AO-2 kind, amount, plan, cost | part | The request root uses its own plan and `Cost_Join`; CJ-H-2 (child plans' amounts against the gate's) OPEN |
| AO-3 owner and requester | ✓ | Bound to the request |
| AO-4 epoch and rollover | ✓ | The request root's Reserve, `Record_Launch_Intent` and `Record_Running` guards (V7-K.2 steps 3, 5 and 9), and each child's |
| AO-5 immutable outer bound | part | Designed: each request root's bound is set once at launch from its own plan (V7-K.2, V7-K.3), the coordinator's limits are read once and never raised. Part until D-H7 is reviewed |
| AO-6 physical enforcement | part | Agents at their leaves inside their own request root; handler code under the service's limits (CJ-H-3, RC-9); the nesting difference (CJ-H-5) |
| AO-7 no double count | ✓ | Request roots are siblings; each agent counts only in its own request's root |
| AO-8 future capacity | part | No protection is claimed; the coordinator's service-class limits exist beside the front's |
| AO-9 response progress | part | Designed: the coordinator serves requests concurrently, with `operation_lock` only around the handler call, and D-H7 launches a later WL request's root while it owns custody. Part until D-H7 is reviewed and V7-N.K's controls pass |
| AO-10 native and process cost | part | Per WL request: the original root decisions and one request-root unit with its helper and factory; per agent: `Task_Admission`, the child launch and run commands, two child decisions, one sub-helper, one init and the actor, against one user-manager unit per agent in the original (`rw/linux/systemd.py:179-197`). CJ-H-4 OPEN |
| AO-11 no new cap, prerequisite, borrowing or accepted failure | part | No cap, no borrowing, no policy field (V7-K.3). It adds the service-class coordinator launch kind, the holder mode, `LAUNCH_REQUEST_ROOT` and the RC-9 read; CJ-H-5 OPEN |

### V7-K.5 Deltas

- **D-H1:** the coordinator's `PREPARED` evidence is its service launch record.
- **D-H2:** a native admission mode for a service-class coordinator, with no request binding (its limits in V7-K.3).
- **D-H3:** the helper's holder mode, and its command routing from the coordinator.
- **D-H4:** reattach and handoff per generation for the coordinator, request slots included.
- **D-H5:** the first WL request is an ordinary request.
- **D-H6:** the mapping of every runner launch onto a child task, with the dispatcher (V6-D, V7-D).
- **D-H7:** the request-root launch while the coordinator owns custody (V7-K.2). Designed in v7; review OPEN.

D-H1 … D-H6 stay undesigned in detail.

### V7-K.6 The options compared, restated

This restates normatively the comparison that v4 V4-D.2 and v5 V5-D.2 made; both are otherwise superseded. The obligations AO-1 … AO-11 are v4 V4-D.1's (C4-VD1, carried).
- **A, B, C, E, F, F′** (v4 V4-D.2's result, restated): "No option meets every obligation at design level. A fails AO-1 and AO-11; B fails AO-9; C fails AO-5 or AO-11, and AO-7; E fails AO-6 and AO-11; F fails AO-5 and AO-11; F′ fails AO-1, AO-7 and AO-11; G leaves E's gaps for handler code in the coordinator (AO-6 and AO-11, part)." F as stated raises the root's admitted outer bound, and `SET_ROOT_CEILING` is withdrawn (R4-24, R4-28). The options themselves are described in v2 §9.2 (C2-92) and v3 V-D (C3-VD, with R4-24 and R4-25 as replaced by R7-6).
- **G** (sibling units, handler in the first root's coordinator; v5 V5-D.2's column, restated): AO-1, AO-2, AO-3, AO-4 and AO-7 ✓; AO-5 and AO-6 ✓ for workload units but ✗ for handler code, which shares the first root unit's admitted bound, so a later request's handler can exhaust a bound admitted for another request; AO-8 none, as original; AO-9 ✓; AO-10: the original's, plus per child the child decisions of V5-E, and per generation one root launch with `Root_Admission`, `EXECUTION_NATIVE` and handoff; AO-11 part: handler code can be killed by another request's bound (an accepted native failure). G keeps its handler-enforcement gap and stays unselected.
- **H′:** V7-K.4.

No option is selected.

### V7-K.7 Who decides

The review's criterion (REVIEW.md §4, verbatim): "If the request root uses the request's own plan policy, the per-agent amounts equal the original's, and D-H2 changes no authoritative admission field, then adoption is the lead's routine engineering call. Otherwise it falls under D-4a's **existing** reservation (OP-3). That is not a new gate."

Against it, at design level:
- the request root uses the request's own plan policy (V7-K.3): designed;
- the per-agent physical amounts equal the original's field for field (V7-K.3); the child ledger rows' correspondence, CJ-H-1 and CJ-H-2, is OPEN;
- D-H2 changes no authoritative admission field (V7-K.3): designed.

So the criterion is not yet shown in full: CJ-H-1 and CJ-H-2 are open, and the nesting difference CJ-H-5 is open. Until they are shown, the author does not read adoption as routine. If any row of V7-K.3 or any of these correspondences fails, D-4a's existing reservation (OP-3) applies; that is not a new gate. The author does not adopt H′, and CG-2 and CG-3 stay OPEN until a route meeting their closure conditions is implemented and shown.

---

## V7-L. Normative carriage repaired (V6-REQ-L; all rulings)

### V7-L.1 Identities

Appendix B binds every identity a normative statement relies on: the v1 … v6 designs, the v5 and v6 reviews, CAPI4 … CAPI6 and their `APPENDIX-BINDINGS.md`, the CAPI5R and CAPI6R review identities, the preimage, and every source file cited.

### V7-L.2 Rulings

§A.3 states every ruling, owner and evidence requirement verbatim and normatively.

### V7-L.3 Body nodes and gates, restated

Spec nodes and their order are v5 V5-A.6's (C5-VA, with R7-17). Body and caller nodes, restated from v4 V4-A.5 with every later change:

| Body | Content | Needs |
|---|---|---|
| B0 | SL-0 source changes | S0; G-A1 for the A1-origin files |
| B2H | HMAC and chain bodies; custody v2 loader; the reattach handshake (v5) | S2H, B0 |
| B9 | Custody bodies, journal v2, provisioners, mutation-gate choke points; the three relations, `HANDOFF_ABORT` and `CUSTODY_RETURNED` (v5); the cause-record operand and the C-APPEND route (V7-G); the front's in-memory phase (V7-H) | S9, B2H, B0 |
| B-RECV | Full-roster receive, `CrosswalkRequestPeer`, `RelayRequestPeer`, gate successors, relay channel; the RELAY codec (v5 V5-I.5); `PROGRESS_BYTES`, `PEER_STATUS`, `out_seq` order and re-derivation (V6-I, V7-I) | S8, B9 |
| B7 | Slot transfer with armed intervals | S7, B9, B-RECV |
| B3 | Crosswalk, pair producers, V2 controller callers, number canonicality; X-1's modes (V7-E) | S2, S3, B9 |
| B1 | Scoped canonical operation bodies and wrappers (V1 and V2); the root route's restored serial order | S1, S2, S3, S4, B3, B0 |
| B2b, B2c | Exchange and K4 successors | S1, S4, S6, B1, G-A1 |
| B6 | `finish` split, adapters, collector settlement, reconstruction seed | S6, B1, B2b, B2c, B9 |
| B4 | Delegation bodies, helper successor and sub-helper; the v2 helper protocol (v5 V5-E.3), the material layout (V6-A.3, V7-A.1) and the child factory (V6-J, V7-J) | S4, S12, B3, B6, B7, B9 |
| B10 | Request multiplexing, relay and the progress model | S10, B1, B3, B4, B7, B9, B-RECV |
| B11 | Startup union, migration and reconciler | S11, B2H, B3, B6, B7, B9 |
| B12 | Seal: pins, freeze, enrollment, rosters (C2-12) | all bodies |
| B13 | The genuine workload dispatcher (V6-D, V7-D) (v5) | S13, B4, B6, B9 |
| Exports of B1, B2b, B2c, B2H, B3, B4, B9 and B-RECV | | G-RW |

Integration gates, restated (review dependencies, not operator gates):

| Gate | Condition | Needs |
|---|---|---|
| G-CAPI | The C-API successor composed after its own stage reviews; CAPI6R closes its rules at design level only | — |
| G-CAPI-P | L-CAPI-P reviewed and composed | G-CAPI |
| G-PROT | L-PROT composed by explicit reviewed import (P1:153) | G-CAPI-P |
| G-RW | Root-worker stages rebased under V5-K.2; IC-1 … IC-14 pass | G-PROT |
| G-A1 | L-A1 selected and frozen separately | — |
| G-DEP | L-DEP selected, reviewed and frozen | — |
| G-REVIEW | Different-author actual gpt-6.1-sol review per slice and for the full lane (read as §A.3 records) | every node |

Runtime gates R-PROOF, R-LAB and R-PUB are unchanged in meaning (C2-16). None of these is an operator gate, and none is added.

### V7-L.4 The RC collision

§C.5 and RR7-7.

### V7-L.5 D6:83

Corrected in §A.4.

### V7-L.6 The G comparison

Restated in V7-K.6; v6's pointer (D6:779) was in the superseded V6-K.

---

## V7-M. The full sweep of carried lines (process point 1)

**Method.** A read-only script composed v7 mechanically: the v6 slices of §B.1; through C6-B the C5 slices of v6 §B.1; through C5-B the C4 slices; through C4-B the C3 slices; through C3-B the C2 slices; through C2-APC the v1 slices. From every carried line it removed the lines any R-block replaces (R-1 … R-4, R3, R4, R5, R6) and the withdrawn ranges W5-1 and W5-2, and the old-text lines inside R-block fences, keeping each block's result text. What remained is every carried normative line. The script then searched every one of them, not only the lines the review named, for each class of statement a v6 or v7 change could make stale or contradictory:

| Class | Search | Result |
|---|---|---|
| capacity and stride | `WL_ABI_CAPACITY`, `stride`, `Capacity_Short`, capacity | D5:1493 replaced (R7-27); V6-A's capacity paragraph replaced (R7-44). Remaining hits are v6's own correction ("not a stride") and capacity in the sense of held capacity or capacity gates: kept |
| D-4a dependence | D-4a with "needs", "depends on", "until", "unless", "selection" | v5:566 (R7-17, the review's finding), v2:1363 (R7-1), v2:1909 (R7-2), v4:427 (R7-6) replaced. Kept: reservations of the operator's authority over an authoritative policy change (for example v2:347, v2:1928, v2:2027, v4:1835, v3:1956's protection claim), headings and ruling labels |
| pidfd-only evidence | "pidfd(s) terminal", "both pidfds", "since HELD" | RT-25 … RT-27, OWN-1 (the review's findings), RT-13, the UNKNOWN routing row, "Finding the worker", the V5-F control (R7-12, R7-13, R7-21, R7-23 … R7-26, R7-86) replaced; R1's statement replaced (R7-57). Kept: closure-barrier rows (`CLOSED_NS`, `CLOSED_OUTER`, `Physical_Closure`, the LIVE/UNKNOWN row of C2-74), which are physical-closure evidence under the closed 04.5, not custody return; R6-18 and R6-20's results, which already give both regimes |
| RC-10 … RC-12 | `RC-10`, `RC-11`, `RC-12` | every installed-check occurrence renamed by quotation (RR7-7's list); the inherited required changes kept (§C.5) |
| withdrawn conventions | "one wire convention", "stride", count `m` | D5:1493 (R7-27); material names (R7-45 … R7-48). V5-A.1's heading is superseded text; references to it resolve by RR6-2 to V6-A.1 and V6-A.2 |
| history used normatively | "not normative", "they were in", `V4-A.5`, "v4/v5/v6 §A or §C", "§C.2 below", "As in v5", "as v4 and v5 compared them" | v5:571 body nodes (R7-18, restated in V7-L.3), the alias rules RR3-1, RR4-1, RR5-1, RR6-1 (R7-3, R7-9, R7-14, R7-41; restated in §C.2), RR4-2's and RR5-2's mappings into V4-A.5 and V4-D.2 (R7-10, R7-15), v4:774 (R7-8), v4:451 (R7-7), v4:1832 (R7-11), RR6-2 (R7-42), V6-F.1's "As in v5" (R7-57), V6-K's G pointer (superseded; V7-K.6). Kept: the §B.3 disposition rows of v4, v5 and v6, which record what was superseded and on which no statement relies |
| claims a review found unsupported | "meets it", "meets the condition", "as in the original", `oom-kill`, `UNKNOWN_WORKER_OWNERSHIP`, `Release_Hold` | R7-39, R7-50, R7-51 (H′), R7-63, R7-53 … R7-56, R7-75, R7-65, and the `Release_Hold` set R7-4, R7-5, R7-19, R7-20, R7-22, R7-64, R7-77. Kept: v1:542 and v2:1412, which describe the lane's `:192` wedge accurately; `Release_Hold` statements that already say held capacity (v2:393 … v2:395) or concern terminal settlement |
| review-kind wording | `GPT-6.1`, `gpt-6.1-sol` | kept unchanged, including C2-116's frontier control (D-2b) and C2-12; the sealed review records how a GPT-6.1 review requirement reads under the 17:05Z direction (§A.3). v7 changes no review requirement |

The search found one statement after the first draft of §B.2 was complete, the V5-F control at v5:1498; it is R7-86. The counts, the per-hit classification and the final re-run, in which every remaining hit is one of the kept classes above, are in Appendix C and AUTHOR-NOTES §2.

---

## V7-N. Controls added by v7

These join the additive roster (C2-17 with R3-9, R4-6, V4-M as amended by R6-4 and R6-5, V5-M as amended by R7-27 … R7-29 and R7-86, and V6-N as amended by R7-75 … R7-79). **No original control is retired, and the frontier control is unchanged (C2-116).**

- **V7-N.A** (static and pure).
  - A material whose `param_count` differs from the roster's length without `Output`, a `param_index` out of order, a `slot_kind` that disagrees with the roster table, or a record size word unequal to `layout (record_kind, 0)` is refused by the sub-helper before any decision.
  - The `decide_v2` material serializes V1's parameters, then `FactsV2`, then `Selection`, and X-8's arguments are in that order.
  - `next` at `WORKER_REATTACHED` from a one-byte epoch whose byte is `0xff`, at `FRONT_OWNED (g+1)` from an eight-byte generation of all `0xff` bytes, and at a sub-generation successor of the same form, each with the output arena sized by V7-A.2: no `Capacity_Short`.
  - `fold`'s argument list has no Input record.
- **V7-N.D** (lab). An OOM-killed actor: `outcome`'s `result` is `failure`, telemetry `oomKilled` and `hitMemoryCeiling` are true, and the runner's `ceilingFired` and `RESOURCE_LIMIT_EXCEEDED` reason equal the original's for the same run. Every persisted field of V7-D.2 is recorded on both sides, and the (iii) fields are listed as differing.
- **V7-N.E** (pure). Each row of V7-E.2 and V7-E.3 at each call site of V7-E.1, with the original check run first: the original class at the original point; and, for every accepted input, X-1 `Ready` in the site's mode (an overflow lexeme, an underflow lexeme, non-canonical spacing and a lone surrogate in Lenient mode; canonical fixtures in Canonical mode). An integer over the conversion limit raises the original `ValueError` before any native call, in both modes.
- **V7-N.F** (lab). At HELD: the fdinfo pairing; an init that exits before the start-tick read is recorded `init_exited_at_held`, and the launch path proceeds as before. In R2: a recorded boot identity different from the current one gives identity-gone; a reused pid with an equal boot identity and a different start tick gives identity-gone; the live worker gives no return.
- **V7-N.G** (pure and lab). `RECONCILED` without a `Cause_Record`, or with one whose digest differs from `unknown_cause`, gives no decision. C-APPEND with the failed event present: `RECONCILED` to `Before_Unknown`, no re-append, and the owner's replay returns the existing event. C-APPEND with it absent: a re-append before `RECONCILED` is refused by `Legal`; after `RECONCILED` it is legal. C-EVIDENCE: no `RECONCILED` by these routes.
- **V7-N.H** (lab). A machine-admission refusal on the root route: `HANDOFF_ABORT (Never_Dispatched)`, the original error response, the front's in-memory phase `FRONT_OWNED`, and the next request passes `:159` and the router and is served. An abort with owners closed: the next request waits on the registered task and is served by the fresh front. An `Irreversible_Budget` root row: no `Release_Hold`, its state unchanged, `Released_Unlaunched` unset.
- **V7-N.I** (lab). A `relay_frame` failure with the front alive and the client connected: the worker does not raise, the front reattaches, `PEER_HELD`, the gate re-issued, and the request completes as without the failure. A killed front after a RELAY transfer: the restarted front answers `PEER_LOST_WITH_FRONT` with the identity evidence, and the RC-13 branch follows. Progress before and after the response, with a reattach between them: the client receives the original order with no frame lost or repeated. The custody owner's re-derived `id`, `op` and `args` equal the front's.
- **V7-N.J** (lab). Between requests, `/proc/<F>/fd` lists exactly 0, 1, 2 and F's socketpair end; during one request, also the leaf descriptor and one socketpair end. No descriptor of F is the owner connection, a custody or actor socketpair end, or a go, report, out, err or stdin pipe end (compared by `kcmp` or by the inode identity with the helper's). Last-writer EOF on the actor's stdin and EOF on the custody channel occur when the worker and the helper close their ends, with F alive.
- **V7-N.K** (outside the roster; added only if H′ is adopted).
  - D-H7: the request-root unit's properties equal the plan policy's `unit_properties ()`; machine admission at DISPATCH with that policy; the unit name of `launch_reserved`; `RECORD_LAUNCH_INTENT`, `DISPATCH_INTENT` and `RECORD_RUNNING` as `launch_reserved` makes them; a failure at each step gives the original phase-conditional `UNKNOWN` and no other effect.
  - Each per-agent leaf's limits equal the runner's `gate.unit_properties ()`.
  - A WL request accepted while another request's detached job runs is launched and served concurrently (CG-3's closure condition).
  - An IP handler runs under the coordinator's read-back service limits (CG-2's closure condition, RC-9).
  - The nesting fixture of CJ-H-5: an original accepted WL case whose agents' total use exceeds no limit of the original is not refused or killed under the request root.

## V7-O. Measurement items and installed-runtime checks added or changed by v7

| Id | Question | Used in |
|---|---|---|
| K-29 | `/proc/sys/kernel/random/boot_id` is constant within one boot and differs after a reboot, and no process of an earlier boot is alive after it | V7-F |
| K-4 (as used) | `/proc/self/fdinfo/<pidfd>` `Pid:` names the process the pidfd refers to, and a pid is not reused while that process is alive (unchanged question; V7-F.1 relies on both parts) | V7-F.1 |
| RC-5 (extended) | the rows of V7-E.2 and V7-E.3 for the installed CPython: the integer-conversion `ValueError`, lone surrogates, `json.detect_encoding`, and overflow and underflow lexemes in lenient parsing | V7-E |
| RC-13, RC-14, RC-15 | renamed from RC-10, RC-11 and RC-12; questions unchanged | §C.5 |

K-29 belongs to OP-7's existing D-8b reservation, by the same range repair as K-22 … K-28 (R7-33, R7-34). RC items are lead-owned. No operator item is added, lowered or widened.

## V7-P. Everything that remains OPEN (adds to V6-P, V5-O and V4-O, carried)

- **All original obligations.** OB-001 … OB-219, every one OPEN, with no closure credited.
- **Required changes and closures.**
  - V6-REQ-A … V6-REQ-L.
  - V5-REQ-A, C, D, E, F, G, I, J and K (PARTIALLY_CLOSED); V5-REQ-B, H, L and M, and V4-REQ-H and V4-REQ-K, closed at design level only.
  - V4-REQ, V3-REQ and V2-REQ as carried; RQ-1 … RQ-5.
  - Every PARTIALLY_CLOSED clause and ruling; 09.4's condition until reviewed.
- **Containment gaps.** CG-1, CG-2, CG-3 and CG-4, each with its closure condition; none depends on D-4a.
- **Correspondences.**
  - CJ-DISP-1 … CJ-DISP-6, with CJ-DISP-4 (iii)'s stated differences;
  - CJ-ARCH-1 … CJ-ARCH-3 (CJ-ARCH-2 with `Round`'s saturating results); CJ-JSON per mode;
  - CJ-H-1 … CJ-H-5;
  - OB-ESC, with audit AU-2.
- **H′.** Deltas D-H1 … D-H7; its adoption (the lead's only after V7-K.7's showing, otherwise D-4a's existing reservation) and any D-4a policy change (operator), none proposed.
- **New designs, unreviewed.** The material names and capacity rule (V7-A); the cause-record operand and C-APPEND route (V7-G); the front's in-memory phase and the router successor (V7-H); `PEER_STATUS`, re-derivation and `out_seq` (V7-I); the factory's fork point and close list (V7-J); D-H7 (V7-K.2).
- **Measurements.** K-1 … K-29 (OP-7); RC-1 … RC-7, RC-9, RC-13, RC-14 and RC-15.
- **Bodies and proofs.** All bodies, `Post`s, proofs, native costs and controls; P-A1 … P-A4.
- **C-API.** CAPI6R's open obligations; ROOT_WORKER_INTEGRATION; L-CAPI-P; G-PROT; IC-10.
- **Acceptance.** Hosted assurance; publication, deployment and final Phase One acceptance.
- **Review.** The independent review of v7, of every slice and of the full lane.

## V7-Q. Non-claims (adds to V6-Q, V5-P and V4-P, carried)

- v7 reviews, accepts, proves and authorizes nothing, and adds no approval gate. Every original obligation stays OPEN.
- Nothing was compiled, run, imported, proved, tested or measured.
- No equivalence is claimed for the dispatcher's persisted evidence texts (CJ-DISP-4 (iii)), for worker-served IP requests (CG-2), for later WL requests (CG-3), or for H′'s nesting of agents (CJ-H-5).
- The pairing and boot-identity evidence of V7-F rests on K-4 and K-29; `PEER_LOST_WITH_FRONT` rests on V7-F.2's test and on K-6.
- The refusal tables of V7-E are the author's reading of CPython's `json` until RC-5.
- H′ is not adopted, and the author does not read its adoption as routine while CJ-H-1, CJ-H-2 and CJ-H-5 are open.
- No liveness is claimed for a worker whose front never reattaches, or for a root in Unknown with a C-EVIDENCE cause.
- SIA recall is not evidence and is not used as evidence.

---

## Appendix A. JACKAL

| Id | Expression | `parsed=` | Result | Status | Used in |
|---|---|---|---|---|---|
| J7-1 | `(2^64 - 1) + 1 - 256^8` | `2^64-1+1-256^8` | 0 | `exact`, lane `rat`, `formal=false` | V7-A.2 (n = 8) |
| J7-2 | `(2^128 - 1) + 1 - 256^16` | `2^128-1+1-256^16` | 0 | `exact`, lane `rat`, `formal=false` | V7-A.2 (n = 16) |

Both are exact rational arithmetic, NOT formal-bounded (no Lean-checked certificate), and informational about arithmetic only; evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`. They check two instances; the general statement "at most n + 1 bytes" is the author's static reasoning. v5's J5-1 … J5-4 and v2's J01 … J18 keep their status inside carried slices. No other numeral in v7 was derived by arithmetic.

## Appendix B. Every identity a normative statement relies on (sha256)

Recomputed with `sha256sum` while drafting v7 (observed), except where marked "recorded".

```
531d11282f811518b868470c0012f23a5e34bdbe3891ef39194cd8f230933f46  D1V/SEAM-DESIGN.md
db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5  D2/SEAM-DESIGN.md
a0f2f411d654f1cce472a1ad2a13d3c082fff42def050c5ed4694a8b094d07a0  D3/SEAM-DESIGN.md
f65629cb45e6e8a5ea798f5130a7f98e1d365758a7175343444f4022864efbda  D4/SEAM-DESIGN.md
0bd92ccd556e39a358a5e93db5a57fe55ba206080d7b6dc1f033508d7f9c66e4  D4/AUTHOR-NOTES.md
938c832d03df0910506756ec295acef86ae2cacba4d7b2478a09c6d27f3685cf  D5/SEAM-DESIGN.md
a3d3ff5482c188705050f7f83709ff2f5e418547ed4a71f26f705f8c5fe18ebe  D5/seams.json
9adaaa83960f7064552dee1f85ffa38ad5191f0e6d6cd02321b287121e931628  D5/jackal.json
d6e16bdfb23b2544218694508144ba32f72ab3c23f79fa9dcb0f2117d324b836  D5/AUTHOR-NOTES.md
d385baca2e5eba7a9605c486d1b5afb2f3fc56cae1d893eed9ba163bf1cc0a50  D5R/REVIEW.md
0b9a3b0705df9d40f7b4e109d4f2042cb6236dcc848fd48f32f27a0de5ff8187  D5R/review.json
6f24f1a44718ce7f8d0b5159b3b78de1cb45ddbf4a2681cacdba9cfe10ead0ab  D5R/checks.json
04b87e452db87f791194a633b8602bf716edc3a41dc4451a002e10d85d000a36  D5R/review-freeze.json
f41566d8bb694817f27efb4dd336d25e554357976808aad577b91365a9a10787  D6/SEAM-DESIGN.md
a54dc595051b582d8c4a06dca62ad00ca9d728896c063cb2d73e4c01d046ddbe  D6/seams.json
5d6684296284d33d3580e5dc123401b493fdf2431d3d54c57b8b4d98abcc84b0  D6/jackal.json
95826c1ee59c7ef11cd9cefbcb3e212053d5ecbd05908224ba59572ebf922633  D6/AUTHOR-NOTES.md
2f814fee89819789d6184b3802c3b77ffda45bd3e6e2fe43e264f47e05890d83  D6R/REVIEW.md
da28c753456d8ef10a0042c2ef2e62d9c4162f1cb1922e60e60b58aa2a5c1b39  D6R/review.json
8fb88b0b13e74319a8ff27a4b677da386f6fce0528bb8f64e552918356e52b36  D6R/checks.json
a148a6c86f7403f7e12915613b9c7cdc9408c932062b924d07cb5bba0e751c79  D6R/review-freeze.json
a9b5dcce5ca5808f8049ae8e7020a79c3fbfc33cc4dcbcc3706fd8f4f40fbfd6  CAPI4/DESIGN.md
39ca995998d68b57d13c02796ee30d8826eecc07e750abf95a83f7d348f7d626  CAPI4/APPENDIX-BINDINGS.md
533f0e043fb991d015bcf16494674d791b6f8f8bd5049fef5a8e60594c9341de  CAPI5/DESIGN.md
f22944b4d52bd196f1823f9f0abf1a0f1578db14f5697bd7b63c6899af15a5a2  CAPI5/APPENDIX-BINDINGS.md
cfa0dca9e275e878b958f2f8da6b5cf54824534867773382965f2a887e98a417  CAPI6/DESIGN.md
9f9f3dfa897d0c320226df39c89bc5c156fc87ebc3e24959ab0c08bba5db1946  CAPI6/APPENDIX-BINDINGS.md
73e82489706e03ca465e7dea2aed1823df0b50a8ce1c5ab0555c545579dc34d8  CAPI5R/REVIEW.md            (recorded)
800880d44bff4b234c82cc392a3008fd4d37139b0827d070120cf299370f403b  CAPI5R/review.json          (recorded)
c1398253713aa6d42ed11fda5194502ccae5a64825b36ef8100206f7d40719ef  CAPI5R/checks.json          (recorded)
91bddf1a46763251940db658f5115cd13ab9de4aa67c0a41ae169de165649af1  CAPI5R/review-freeze.json   (recorded)
12cfde3c3eed993b6056dc75d901710bdee1273e67cfe150a9648f99627da161  CAPI6R/REVIEW.md            (recorded)
bcfa259f8690c492b9284ef1ed9549efa7a5d3899edc1fbd5a0ae2ab7234d128  CAPI6R/review.json          (recorded)
12642ce4501f12b0a608264d9bd93a23f39fd6c7d2c85cee69d94a91a3e2f284  CAPI6R/checks.json          (recorded)
15fc9f07786eba0e0c1d3cde0250c8696e8ebeb96961ce6c22aeea2fcc590742  CAPI6R/review-freeze.json   (recorded)
7674f11c26107d6c984ed8f8a883a2263f07a19e56e5a467f503ce90ae8b5e24  pre/protected_operations.py
9031e0bdd6fd10e911a908f1e15d8241aed94b0445946b5da45d821899133710  rw/runner.py
9d448dcc8741b698750147a8a0ccb9aaaf0215cba6a16c702facde394b6b52e4  rw/daemon.py
1022187a02c19fb25ecfcafcc9a43a91e5ab62cf243ae38014c14d4c73463ade  rw/client_peer.py
f1089a091399dd0c1a0602aebb027edff4737fbf562750e95e3a0c561067f723  rw/protected_root_resource.py
acf5ac0fb4035d53c3e053e7a3a10b4f29fd29d5bc0aefbdb0d9de181665080f  rw/protected_scoped_resource_runtime.py
76ae777b375b3ad2785399c73d9e14055b2f6cca58a30e2078b2b847ac87176e  rw/resource_child_execution.py
e506348f1efb6615151114a21ef238aca4dd0e81592aad7f1bb64b184ddd8076  rw/resource_scoped_run_ledger.py
e0148f27abfa652d8594a87660fc996e1e402101593f348824cae6a08dd41c6f  rw/canonical_exchange_kernel.py
b7c44b329c8c92701c06fcdfd7b5e6692b8b164ae7f699729afe60d0d30036a0  rw/canonical_operation_kernel.py
0c3998337f998f1961f3573a3e0743dce750b5777d47bb8bb205d3a74faffa06  rw/canonical_owner_completion_kernel.py
0fc7f5fde1357f1a97da2ce1977c60290cb15bb4e4e5b77205b4e678f6a5f482  rw/operation_authority_kernel.py
9f123d62282c8189a9b7b5f300b37d94d2544626820ca5d08ee9a72c81cab7f2  rw/chain_authority.py
d133785f88a76f09f816f484a58a85d4cd75052a96424b12a52c5434121afb05  rw/operation_capture.py
f2bc319b69f3491b9b16fde710fde122d94203ab2d5cfb94fb348d7c79d65793  rw/root_worker_codec.py
bf5472672be296d4b37c5cae113407a733625611b79b34c46316da729e1df8d7  rw/finalization_journal.py
9f5e97446797f09633008c3d8c1f7d6759b674122681887e73a7a6e78db53033  rw/evaluation_terminal.py
559dc067399ade18658116727cbe2f364f718791cb299bd563765075de5569fa  rw/evaluation_pending.py
e29a14a63d67fa3228ede57f0ad12aaa55cbf7c7cf61a8bc09971d5731680ca6  rw/protected_startup.py
fc6f00f698160f1a854ef7ae72c425f3c7ed11243809b6dac1a5132c0e2ad33f  rw/protected_resource_runtime.py
2510f8edac3937509d36bc3b38511af89f81ecf9a5eff77fefc87f927f3aa811  rw/root_worker_journal.py
15cbbfcd61a98da55a704af16fd5d853a3af64bc0aba84599d936440ba8f74a1  rw/protected_root_worker.py
ea1a01df19ddef2418d4e4ec14dab6cea1eaa70423172eedea36a48ec383f0cb  rw/protected_operations.py
25f38ae7c1b63f14329400155562c18e459b80f46797851ef81d82db03172169  rw/root_worker_custody.py
25b590b09ebcf81f46726bdc276093a6e9861b6ab60859924eb151525f4adfe3  rw/root_worker_plan.py
a0781e70e8a4b2b630f6956d0c89208140edc871c4a2a003666573767a32d13d  rw/admission.py
774e35565b93aef70420183a591ceb3acf9ddc9148c0b4ae55fb83bb9efc83ce  rw/root_worker_endpoint_router.py
4a8c71fa4617b09af2aab8724375c09fabfb2acb5c1676e10f6690b7153270d9  rw/canonical_owner_witness.py
68740eda2668faddfe28bd3a8ac1720adac3de32f0bc68d8d95e45f94170d07b  rw/root_worker_closed.py
710d37c77de105bdd62d96e1ce31d5b0ad79fcbd7ae8b7e556bd1b7656462784  rw/linux/systemd.py
65a38d24f3c5444bd21bc15ecf8dee6ec9e2e93a71ba911f6678ca9b4797562d  R/core/resource_run_ledger.ads
23c43aaaad873052b8e2e192a4c33a46b1d08f7b427f11f7b27f10602553c07f  R/core/resource_observation_classification.ads
f2a321d07e667e80f4359634e8e4a956b555368b8d449e8c8c930b8f511aeff7  C1
2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237  P1/HANDOFF.md
```

- **Recorded, not recomputed:** the eight CAPI5R and CAPI6R files live under `review/gpt61-v1`, and the lead's instructions for this task forbid reading any `gpt61-v*` directory, hashing included. Their identities are bound here as recorded in D4's Appendix B (D4:1873-1876, D4:1880-1883) and header (D4:10); D4's file identity, `f65629cb…bda`, was recomputed and equals the line above. The sealed v6 review found the CAPI5 and CAPI6 `APPENDIX-BINDINGS.md` files unchanged against v5's pins (REVIEW.md, "Other identities checked"); those two are recomputed above.
- **The C-API verdicts these identities carry** (from D4:10, recorded): CAPI5R ENDORSED_WITH_REQUIRED_CHANGES, required changes V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE; CAPI6R, of CAPI6 `DESIGN.md` `cfa0dca9…a417`, ENDORSED with no required changes, closing V5-RC4-GATE-EXCEPTION, V5-RC4-QUAL-CAPTURE, V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 at design level only; ROOT_WORKER_INTEGRATION "OPEN; no ruling on the other lane or integration order".
- Lists of inputs carried inside slices (v2 Appendix B in C2 slices, v3's C3-APB) keep their own identities; this list binds every identity a v7 normative statement relies on.

These are byte identities at the time of reading. They establish no authenticity, installed state or atomic snapshot.

## Appendix C. Verification (observed)

A read-only Python script read the v1 … v6 designs, the sealed v6 review and this file, and printed to standard output; it wrote no file. Its final run (AUTHOR-NOTES §2) checked:
- v6 `SEAM-DESIGN.md`: sha256 `f41566d8…0787`, 990 lines, ending with a newline;
- §B.1: every slice's sha256 equals the stated hash; no two slices overlap; no slice overlaps a superseded range of §B.3; every v6 line is in a slice, in a superseded range, or is empty or `---`;
- §B.2: every R7's quoted old text equals the stated lines of the stated version exactly; every target lies in a carried slice of the stated name; no target is replaced by any earlier R-block or lies in a withdrawn range; no line is targeted twice; R7-1 … R7-86 are numbered without gaps;
- every quotation in §A from the sealed `review.json` and REVIEW.md equals the text it quotes;
- every markdown table: each row has its header's cell count;
- the sweep of V7-M, re-run on the composed v7: every remaining hit is in a kept class.

**Final run, observed.** 14 slices hash-verified; superseded ranges 1-115, 410-446, 616-628, 777-815 and 924-990; no uncovered non-blank v6 line. 86 R7 blocks, contiguous, every quote exact, every target carried, in its stated slice, untouched by any earlier R and targeted once; no `R7-n` reference without a block. All 12 required-change texts, all 13 rulings with their owners and evidence requirements, and all 20 PARTIALLY_CLOSED clause gaps quoted verbatim (the clause set equals `review.json`'s). Every table row has its header's cell count. Problems: none.

**The sweep on the composed v7, observed.** 4698 carried normative lines (v1 415, v2 1227, v3 1086, v4 541, v5 944, v6 485) plus 86 R7 result lines. Remaining hits, each in a kept class of V7-M:
- capacity and stride (3): v6:472 (v6's own correction), R7-27, R7-44 (the replacements, which name the withdrawn mechanism as withdrawn);
- D-4a dependence (2): v3:1956 (a protection claim reserved to D-4a, not a later request's progress), R7-17 (the replacement, which states the independence);
- pidfd evidence (16): v2:1183, v3:1396, v3:1399, v4:472, v4:1418, v4:1419, v4:1421, v5:915, v5:916, v6:860 (physical closure, R1's pidfds); v6:286, v6:302 (both regimes already); R7-21, R7-23, R7-57, R7-86 (replacements);
- RC-10 … RC-12 (22): v2:222, v2:235, v2:236, v2:241, v2:1625, v2:1648, v2:1936, v2:2261, v4:1827, v5:1525 (inherited required changes, §C.5); twelve R7 results, each naming the old name only as "named … before v7";
- history (10): v4:763, v4:764, v5:369, v5:370, v6:391, v6:392 (§B.3 disposition rows); v5:548 (a heading that records a replacement); R7-8, R7-15, R7-42 (replacements that map history to live text);
- unsupported claims (9): v1:542, v2:1412 (accurate descriptions of the lane's `:192`), v2:520 and v4:1802 (statements of original behaviour); R7-53, R7-54, R7-56, R7-65, R7-75 (replacements that name `oom-kill` or `:192` as removed);
- review-kind wording (12): kept, as V7-M states.

## Appendix D. Companion file identities

Observed with `sha256sum` and `wc -c` after the files were written. This file cannot contain its own hash; `seams.json` records it, and the handback records both.

| File | sha256 | Bytes |
|---|---|---|
| `jackal.json` | `f691a36b3a9efbd49e6d56ad2c264f85b0b83f17ab64ef1fd58db698f181263f` | 1612 |
| `AUTHOR-NOTES.md` | `b651f5e61fe3deca19e6bed1753bb83e7b93d059cc39a2fbc1ea1768968e9da6` | 12720 |
| `seams.json` | recorded in the handback (it binds this file's hash) | — |
