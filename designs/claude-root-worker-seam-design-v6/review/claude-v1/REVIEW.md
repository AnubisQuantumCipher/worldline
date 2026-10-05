**WORLDLINE Phase One root-worker SEAM DESIGN v6: independent design review**

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**

- **Reviewer.** An independent Claude Code review subagent (claude-opus-5-5) with a fresh context. I authored nothing under review and I am not the drafting agent.
- **Author.** Claude Code lead claude-opus-5-5, through a drafting subagent.
- **What the verdict covers.** It endorses the design's direction, subject to V6-REQ-A … V6-REQ-L below. It grants no source, proof, runtime, lane, phase, deployment or operator acceptance: proof_acceptance=false, phase_acceptance=false, source_acceptance=false.
- **Obligations.** OB-001 … OB-219 all stay OPEN. The draft lane stays INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY (L/handoff-to-claude-v1-retry1/HANDOFF.md:3).

**Aliases**

| Alias | Path |
|---|---|
| W | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow |
| WT | W/work/claude-lead-isolation-v1/wt-1 |
| D6 | WT/designs/claude-root-worker-seam-design-v6/SEAM-DESIGN.md |
| D5, D4 | the v5 and v4 SEAM-DESIGN.md |
| D5R | WT/designs/claude-root-worker-seam-design-v5/review/claude-v1 |
| L | W/work/protected-original-root-worker-repair-v1 |
| rw/ | L/source/runtime/worldline/ |
| pre/ | L/preimage/runtime/worldline/ |
| core/ | L/source/core/ |
| C1 | L/source/protected-root/native_root_worker_supervisor_v1.c |
| P1 | W/outputs/claude-phase1-handoff-20261004 |

**Identities (computed with sha256sum)**

| File | sha256 |
|---|---|
| Brief root-worker-seam-design-v6.md | 48e874f426a41f854791da0a8da2b108514dd7c2d8ad47965eb4880bf3bb5ca0 |
| D6 | f41566d8bb694817f27efb4dd336d25e554357976808aad577b91365a9a10787 (matches the brief) |
| seams.json | a54dc595051b582d8c4a06dca62ad00ca9d728896c063cb2d73e4c01d046ddbe (matches) |
| jackal.json | 5d6684296284d33d3580e5dc123401b493fdf2431d3d54c57b8b4d98abcc84b0 (matches) |
| AUTHOR-NOTES.md | 95826c1ee59c7ef11cd9cefbcb3e212053d5ecbd05908224ba59572ebf922633 (matches) |

Other identities checked:
- The v5 design, seams.json, jackal.json and AUTHOR-NOTES.md match D6:8.
- D5R's REVIEW.md, review.json, checks.json and review-freeze.json match D6:9.
- D4 is f65629cb….
- All 36 entries of D6 Appendix B (D6:932-968) match the current bytes.
- The CAPI5 and CAPI6 APPENDIX-BINDINGS.md files are unchanged against v5's pins: f22944b4… and 9f9f3dfa….

**Process**

- **Reading only.** Read, plus Python reading standard input and printing to standard output. Nothing was imported or executed. No compiler, prover, test, service, sudo, project-vault or restic was run. No file was written.
- **Not read.** Any v6 review directory, review-records/, any gpt61-v* directory, D5R's raw-final-message.txt, any transcript, and the SIA gbrain store.
- **SIA.** I made no `sia.ask` call, so the review stays independent of recall about this revision. This departs from the global CLAUDE.md start-of-task rule. No SIA note was written.
- **Ada skills.** All eight were loaded before I read the core/*.ads files.
- **JACKAL.** Three calls (checks.json). One was refused, and that refusal is reported as a refusal.

---

### 1. Closure of V5-REQ-A … V5-REQ-M, the 22 open clauses and the rulings

| Item | Closure | Remaining gap | Evidence |
|---|---|---|---|
| V5-REQ-A | PARTIALLY_CLOSED | **Done, and accurate against source:** conventions P and T, the per-export table and RootStateRec. The record matches Root_State and the DDL field for field, in order. **Gaps:** (i) The material layout uses "m" for both the parameter count and the SHA-256 digest, and the check "m equals its own compiled roster's length" is therefore ambiguous. "kind" means both the material kind (0, 1, 2) and the layout record-kind index. (ii) The stated capacity rule says new quantity bytes arise "only for a generation successor". `Next` also writes the Reattach_Epoch increment and the sub-generation successors s + 1. A wrapper that follows the rule as written can return Capacity_Short on a legal transition (for example epoch 255 → 256; JACKAL J6-1). (iii) The carried V5-A control at D5:1493 still promises `WL_ABI_CAPACITY` and "stride", both of which v6 withdraws. No R6 replaces it. (iv) X-5 `fold` has no Input record, so it is an unstated variant of T. | D6:490, 495-499, 482; D5:977-979, 1493; rw/resource_child_execution.py:113-121, 186-193, 207; rw/canonical_exchange_kernel.py:32-37, 62-66; rw/chain_authority.py:69-102; D5:1291-1317 |
| V5-REQ-B | CLOSED_AT_DESIGN_LEVEL | The statement, the withdrawal (R6-9, R6-11), CG-2 with a closure condition independent of D-4a, and control V6-N.B are present. **One factual correction (V6-REQ-B).** The root unit's properties come from the root-worker plan's `worker_policy`, admitted under the WL request's reservation. They are not "the properties of the WL request's plan". The gap is unchanged. | D6:523, 527-532; rw/root_worker_plan.py:22, 37; rw/protected_root_resource.py:38, 50-51, 68-71 |
| V5-REQ-C | PARTIALLY_CLOSED | CG-3 is recorded exactly, and R6-10, R6-25 and R6-29 are correct. **But the carried line D5:566 (spec node S10) still reads "a selected specification needs D-4a (V5-D, V5-L)".** That is the D-4a dependence the requirement removes, and no R6 replaces it. | D6:536-545; D5:566 |
| V5-REQ-D | PARTIALLY_CLOSED | Every attribute the runner uses is covered. **Two problems.** (i) The dispatcher's `result` returns `oom-kill`, a value the original `outcome` never produces: its results are only stopped, failure, success or None. So the runner's `ceilingFired` and `ceilingEvidence` ("the service manager recorded Result=oom-kill") classify differently from the original, contradicting CJ-DISP-4 and the V6-D lab control. (ii) CJ-DISP-4 calls the other fields "diagnostic". In fact `source` and `launcherStderr` go into durable result text, and the whole supervision dict is persisted in agent_result and the finalization record. | D6:563, 572, 853; rw/linux/systemd.py:694-715, 528-545; rw/runner.py:937-950, 967, 982, 986 |
| V5-REQ-E | PARTIALLY_CLOSED | **Done:** the four archive layers are verified against source, D5:693 is corrected, and correspondence and costs are given. **Gap:** V6-E.4 maps only canonical-mode `exact_json` and `exact`. X-1's caller X-6 (the request document) parses with `canonical_required=False`, so the original accepts non-canonical forms and overflow lexemes (as inf). JsonInput has no lenient mode, so the new fail-closed `SOURCE_JSON_NATIVE_DISAGREES` would be reachable for original accepted requests. Also missing: CPython's int max-str-digits `ValueError` for long integer lexemes (my unverified reasoning, RC-5). | D6:618-628; D5:473-477; rw/protected_operations.py:624, 723, 729; rw/canonical_owner_witness.py:25; rw/protected_startup.py:40-51, 682, 706 |
| V5-REQ-F | PARTIALLY_CLOSED | **Done:** regime R2, OB-ESC with AU-2, C-ESC-1 and C-ESC-2. The fresh flock is the right primitive, because every transferred lock is a `flock`. **Gaps:** (i) Carried RT-25, RT-26 and RT-27 (D5:1071-1073) and lemma OWN-1 (D5:1000) still require "worker pidfd terminal", which no restarted front holds; only XC-4 (R6-20) was updated. (ii) The start tick of the namespace init is read at HELD with no pairing to the init pidfd that the HELD frame itself carries, so pid reuse can race. (iii) No boot identity is recorded beside the start tick. | D6:640-645, 651-667; D5:1000, 1071-1073; C1:241, 247; rw/root_worker_journal.py:62; rw/protected_startup.py:374-385; rw/root_worker_custody.py:106-115 |
| V5-REQ-G | PARTIALLY_CLOSED | **Done:** the C-CHANNEL and C-DEADLINE route (R6-17, R6-19) and the worker's behaviour while refused. **Gaps:** (i) The C-APPEND route is circular when the failed append never persisted. Re-appending E in phase Unknown is illegal under E's own row, yet RECONCILED needs E as evidence. (ii) R6-19 (no C-APPEND), R6-24 (no cause filter) and V6-G.2 disagree on which causes may return to service. (iii) The cause class is not an X-5 operand. (iv) "as in the original" (D6:692) overclaims, because the original has no such wait. | D6:684-696, 294, 344; D5:908-909, 1006 |
| V5-REQ-H | CLOSED_AT_DESIGN_LEVEL | Both asks are met exactly. PREPARED comes first, and the phase-conditional append matches rw/protected_scoped_resource_runtime.py:771-773. **A new finding (V6-REQ-H) blocks 07.3.** V6-H.2 keeps rw/protected_root_worker.py:191-198 "unchanged". That includes line 192, which sets `self.phase='UNKNOWN_WORKER_OWNERSHIP'` on any failure. After that, :159 refuses every later root invoke with ROOT_WORKER_PRIOR_OWNER_UNKNOWN_OR_LIVE, which contradicts V5-G.1 step 7. Also, Release_Hold applies only to Held_Capacity rows. | D6:702-720; rw/protected_root_resource.py:51-63, 142-146; rw/protected_root_worker.py:159, 192; rw/root_worker_endpoint_router.py:22; core/resource_run_ledger.ads:317-319; core/resource_observation_classification.ads:96-102 |
| V5-REQ-I | PARTIALLY_CLOSED | **Done:** branch (b) is sound under RC-10 (KernelPeer re-reads an owned duplicate), and the daemon-step table is given. **Gap:** R6-23 assumes "a front that lost the channel has lost the client connection too". The design itself allows channel loss with the front alive (D5:1461 row; a `relay_frame` failure). In branch (a) the worker would then raise the client-gone exception while the client is still connected: a new refusal plus quarantine. That breaks 09.4's condition. Also unspecified: how the custody owner re-derives id, op and args from a transferred line, and the relative order of PROGRESS_BYTES and RESPONSE_BYTES. | D6:330, 728-755; D5:1461; rw/client_peer.py:73-90; rw/daemon.py:307-313, 339-360, 394-400 |
| V5-REQ-J | PARTIALLY_CLOSED | The factory design and K-28 under OP-7 are right. **Gap:** where F is forked is unspecified. C1 creates the owner connection, the custody and actor socketpairs, go, report, out, err and the stdin pipe at :323-335, just before the unshare at :336. A literal fork "before unshare" gives F all of them. F never execs, so close-on-exec does nothing. The result would defeat last-writer EOF (V4-H.5, closed V4-REQ-H) and channel EOF (C-CHANNEL). This contradicts F's stated surface. | D6:764-768; C1:323-337 |
| V5-REQ-K | PARTIALLY_CLOSED | The per-agent child mapping is coherent. **Missing:** a path that launches a request root while the coordinator owns custody. The front's owners are closed (rw/protected_root_resource.py:161). The coordinator cannot reach the manager (M-4). `launch_reserved` requires a bwrap argv[0] (:732-735), and `launch_root_worker` uses `handler_plan`, which takes `worker_policy` and the coordinator argv. Neither fits holder mode, and no D-H delta covers it. AO-9 ✓, and "meets CG-2/CG-3 at design level", are therefore not established. | D6:783-814; rw/protected_scoped_resource_runtime.py:704-706, 723, 729-735; rw/protected_root_resource.py:33-49, 161; rw/root_worker_plan.py:22-37 |
| V5-REQ-L | CLOSED_AT_DESIGN_LEVEL | R6-4 and R6-5 quote v4:1801 and v4:1804 exactly. R6-1 retires RR5-7, and a search of every C4 slice finds no other text naming M8 (c), "no owner is reachable" or QUEUED progress. CG-1 is attributed to the preimage, whose hash 7674f11c… matches. CG-4 is recorded from pre/protected_operations.py:720-722. | D6:145-183, 818-828; D4:480, 628, 636, 692, 1804; pre/protected_operations.py:720-730 |
| V5-REQ-M | CLOSED_AT_DESIGN_LEVEL | K-27 now covers only the kernel's memfd seals and mapping (OP-7). RC-11 (the loader) is lead-owned. | D6:367-368, 832-836 |

**The 22 clauses the v5 review left PARTIALLY_CLOSED**

| Clause | v6 status | Remaining gap |
|---|---|---|
| 01.1 | PARTIALLY_CLOSED | V6-REQ-A |
| 01.5 | PARTIALLY_CLOSED | D_prod coverage OPEN (unchanged) |
| 01.7 | PARTIALLY_CLOSED | RQ-1 proofs and controls absent; CG-2 and CG-3 are stated correctly |
| 02.1 | PARTIALLY_CLOSED | V6-REQ-E (lenient request-document mode) |
| 02.2 | PARTIALLY_CLOSED | P-A1 … P-A4 (unchanged) |
| 02.3 | PARTIALLY_CLOSED | Costs OPEN |
| 02.4 | PARTIALLY_CLOSED | V6-REQ-K |
| 03.2 | PARTIALLY_CLOSED | V6-REQ-J |
| 03.3 | PARTIALLY_CLOSED | CG-1; V6-REQ-D |
| 04.1 | PARTIALLY_CLOSED | V6-REQ-G, V6-REQ-H |
| 04.3 | CLOSED_AT_DESIGN_LEVEL | X-5 equals the DDL (D6:501-517) |
| 04.4 | PARTIALLY_CLOSED | V6-REQ-F |
| 06.2 | PARTIALLY_CLOSED | V6-REQ-K |
| 06.3 | PARTIALLY_CLOSED | Never-reattach stays OPEN (stated, D6:342) |
| 06.4 | PARTIALLY_CLOSED | CG-3 OPEN; V6-REQ-C |
| 07.3 | PARTIALLY_CLOSED | V6-REQ-H (:192 wedge) |
| 09.2 | PARTIALLY_CLOSED | V6-REQ-I |
| 09.5 | PARTIALLY_CLOSED | V6-REQ-G; C-EVIDENCE has no liveness |
| 11.1 | PARTIALLY_CLOSED | X-5 capacity rule (V6-REQ-A) |
| 12.1 | CLOSED_AT_DESIGN_LEVEL | X-5 equals the DDL; the genesis archive_equal is accurate. The genesis loader uses canonical `exact_json` (rw/root_worker_journal.py:42) |
| 12.2 | PARTIALLY_CLOSED | V6-REQ-F, V6-REQ-H |
| 12.4 | PARTIALLY_CLOSED | V6-REQ-F, V6-REQ-G |

**Rulings**

- D-2b stays CLOSED_AT_DESIGN_LEVEL, carried through C5-B and C2-116.
- D-1a, D-1b, D-2a, D-3a, D-4a, D-5a, D-5b, D-6a, D-7a, D-8a, D-8b and D-9a stay PARTIALLY_CLOSED. Their gaps are those of the V6-REQs mapped to each in review.json.
- The ruling strings at D6:76 are verbatim (13/13, by script).
- **Owners and evidence requirements are preserved only by reference.** D6:76 points to v5 §A.5, and v6 §B.3 marks v5 lines 1-178 "History, not normative" (D6:391). The owners and evidence requirements therefore sit in the sealed review.json, not in v6's normative text (V6-REQ-L). Their substance is unchanged. "Independent GPT-6.1 reviewer" reads as "independent Claude review subagent" under the 17:05Z direction (WT/STATUS.md:279-292).

### 2. Carried items

- **Slices.** 13/13 hash-verify. There is no overlap and no overlap with a superseded range. The 33 v5 lines outside both are blank or `---`. The table at D6:125-139 agrees with seams.json.
- **R6 quotes.** R6-1 … R6-29 are 29/29 exact quotes of their stated v5 or v4 lines. Each v5 target lies in its stated slice. v4:1801 and v4:1804 lie in C4-VMNOP and are not R5 targets.
- **Other quotations.** All 13 V5-REQ change texts, the 13 ruling texts and the 22 clause gaps are verbatim. The 37 closed and 22 partial clause sets equal review.json.
- **Are the R6s the only changes? Mostly.** RR6-2 and RR6-7 (D6:403, 408) re-point and define carried terms without neutralising sentences, which is acceptable. **But the remaining carried lines are now stale or contradictory:**
  - D5:1493: `WL_ABI_CAPACITY` and "stride";
  - D5:566: S10 says a selected specification needs D-4a;
  - D5:1000 (OWN-1) and D5:1071-1073 (RT-25 … RT-27): "pidfd terminal".
  
  The v5 review required explicit quoted replacements for exactly this kind of stale carried text (V5-REQ-L).
- **The closed items still hold.**
  - C5-VH (V4-REQ-H) is verbatim. It stays closed, provided V6-REQ-J prevents the factory from holding pipe ends.
  - C5-VK (V4-REQ-K and the C-API integration) is verbatim. But v6 no longer pins the CAPI identities: D6:10 says they are in "v5's header (carried by history) and Appendix B", and v6's Appendix B has none (V6-REQ-L).
  - D-2b is carried.
  - 09.4 stays closed only if V6-REQ-I is met.
  - D6:83 misdescribes the 07.1 changes: R6-18 and R6-20 add alternative evidence and R6-19 adds a target. The relation structure still holds.
- **Is the composed specification unambiguous?** It can be recomposed mechanically. It is not yet unambiguous:
  - the m and kind collisions;
  - "RC-10" names both the inherited, closed required change (D5:137, 1525) and the open installed-runtime check that now selects V6-I's branch;
  - D6:779 points G's comparison at superseded history.

### 3. Containment gaps

- **CG-1.** OPEN, attributed correctly to the preimage (pre/protected_operations.py:729-730).
- **CG-2.** Stated exactly, with a closure condition that does not depend on D-4a (D6:527-532). Only the plan attribution needs correcting (V6-REQ-B). Nothing is presented as preserved: front-served IP keeps cost equality, which is right.
- **CG-3.** Stated exactly, with a closure condition independent of D-4a (D6:540-544). The carried S10 line contradicts that independence (V6-REQ-C).
- **CG-4.** Stated exactly from pre/protected_operations.py:720-722. Its closure condition does not depend on D-4a, but v6 should say so (seams.json has no depends_on_d4a field for CG-4).
- **Overclaim.** V6-G.3 "as in the original".

### 4. Option H′

**The direction is sound. The mapping is right at child level. The request-root launch path is missing.**

**AO marks:**
- AO-3, AO-4 and AO-7 hold.
- AO-5 ✓ depends on which policy the holder-mode root uses: the request's own plan (rw/protected_scoped_resource_runtime.py:729-731) or `worker_policy` (rw/root_worker_plan.py:22, 37).
- AO-9 ✓ is not established (V6-REQ-K).

**Who decides adoption.** The author's reading, that H′ changes no resource-policy field (D6:814), is **not established**:
- D-H2 adds an admission mode with no request binding;
- the request root's unit properties have no stated source;
- the per-agent amounts (CJ-H-2) are OPEN;
- AO-8 is part, because the coordinator adds a service-class bound.

If the request root uses the request's own plan policy, the per-agent amounts equal the original's, and D-H2 changes no authoritative admission field, then adoption is the lead's routine engineering call. Otherwise it falls under D-4a's **existing** reservation (OP-3). That is not a new gate. I do not adopt H′.

### 5. V5-REQ-E, F, G, H, I and J against source

- **E: archive_equal.** Layers 1-4 match rw/resource_scoped_run_ledger.py:377-394, rw/operation_capture.py:15-39, rw/finalization_journal.py:44-60, rw/evaluation_terminal.py:76-91 and rw/evaluation_pending.py:74-76. The gap is the lenient-mode callers.
- **F: custody-return evidence.** The flock probe is sound for flock-type locks. OB-ESC is explicit. The R1 limit is stated honestly (D6:664, 918). Stale carried RT rows remain.
- **G: Unknown → service.** The C-CHANNEL and C-DEADLINE route is sound. C-APPEND is circular.
- **H: PREPARED ordering.** Exact. The :192 wedge is a new finding.
- **I: RC-10 dual outcome.** Branch (b) is exact. Branch (a) is unsafe when the front is alive.
- **J: pre-unshare factory.** It works only if F is forked before C1:323, or closes everything else it inherits.

### 6. New refusals, caps, narrowed domains, changed behaviour, assumptions, gates

**New refusals or changed behaviour:**
- `SOURCE_JSON_NATIVE_DISAGREES` can be reached for lenient-mode request documents (V6-REQ-E);
- branch (a) refuses while the client is still connected (V6-REQ-I);
- the :192 wedge refuses ROOT_WORKER_PRIOR_OWNER_UNKNOWN_OR_LIVE after Never_Dispatched (V6-REQ-H);
- the dispatcher's `oom-kill` classification and the changed persisted supervision text (V6-REQ-D);
- Capacity_Short on a legal epoch or sub-generation successor (V6-REQ-A);
- broken EOF if the factory inherits pipe ends (V6-REQ-J).

**Added assumptions:**
- the start tick is sampled at HELD without pairing it to the pidfd;
- pid plus start tick is treated as unique across reboot. Both are labelled K-4, and V6-REQ-F hardens them.

**Gates.** K-27, K-28 and RC-11 under OP-7 are within its scope, as the same kind of range repair. RC-11 and RC-12 are lead-owned. Ordering RC-10 before B-RECV's review is sequencing, not a gate.

**Not found:**
- a new cap;
- a narrowed numeric domain;
- a retired or weakened control (the frontier control is unchanged);
- a lead-only acceptance;
- an added or lowered approval gate.

### 7. Other concerns

- **Release_Hold scope.** Release_Hold requires Held_Capacity (core/resource_run_ledger.ads:317-319). V6-H.2 and the V6-H control should say that Irreversible_Budget rows are not released on Never_Launched.
- **R2 identity.** It should record the boot identity (K-4).

### Required changes for v6

- **V6-REQ-A.** Fix the material layout and the capacity rule:
  - give the count and the digest different names, and say which "kind" is meant;
  - state the decide_v2 roster;
  - extend the capacity rule to every successor quantity `Next` writes (generation, Reattach_Epoch, sub-generations);
  - replace D5:1493 by quotation;
  - state X-5 `fold`'s no-Input variant of T.
- **V6-REQ-B.** Correct D6:523: the properties come from `worker_policy`, admitted under the WL reservation.
- **V6-REQ-C.** Replace D5:566 (S10) by quotation, consistent with CG-3 and V6-K.4, and state that CG-4's closure condition is independent of D-4a.
- **V6-REQ-D.** Fix the dispatcher's outcome:
  - remove `result = oom-kill`, keeping the original's set of result values;
  - carry OOM through telemetry `oomKilled`;
  - restate CJ-DISP-4 to cover the persisted supervision fields and messages (rw/runner.py:945-949, 967, 982, 986);
  - fix the V6-D control.
- **V6-REQ-E.** Give X-1 one mode per caller, matching `canonical_required` at each call site, and give the lenient mode its refusal table. Make CJ-JSON hold per mode, so that `SOURCE_JSON_NATIVE_DISAGREES` cannot be reached for any input Python accepts. Add the int max-str-digits row (RC-5).
- **V6-REQ-F.** Replace RT-25, RT-26 and RT-27 (D5:1071-1073) and OWN-1 (D5:1000) by quotation, requiring "worker gone" or E-CR. Read the init's start tick while holding the init pidfd that the HELD frame passes (C1:247), and confirm the pid-to-pidfd pairing. Record the boot identity.
- **V6-REQ-G.** Fix the C-APPEND route:
  - make it non-circular: RECONCILED first, then a re-append under Legal, or the replay hit;
  - align R6-19, R6-24 and V6-G.2;
  - make the cause class an X-5 operand;
  - drop "as in the original".
- **V6-REQ-H.** Specify the front's in-memory phase after HANDOFF_ABORT, replacing rw/protected_root_worker.py:192, so that FRONT_OWNED (g+1) passes :159 and the router check at :22. Qualify Release_Hold to Held_Capacity.
- **V6-REQ-I.** In branch (a), never raise while the front may be alive. Wait for the reattach, and raise only on authenticated evidence that the client has gone. Specify the frame order and how the custody owner re-derives a transferred request.
- **V6-REQ-J.** Fix F's fork point before C1:323, or give an explicit close-all-except list. Add a control showing that F holds no owner, custody, actor, go, report, out, err or stdin descriptor.
- **V6-REQ-K.** Complete H′:
  - design the request-root launch path while the coordinator owns custody, as a new delta;
  - fix the request root's policy source;
  - mark AO-9 (and AO-5) as part until both are designed;
  - list every resource-policy field and show each unchanged before treating adoption as the lead's call.
- **V6-REQ-L.** Repair the normative carriage:
  - re-bind the CAPI5 and CAPI6 APPENDIX-BINDINGS.md files and the CAPI5R and CAPI6R review identities in v6 Appendix B;
  - restate or bind the ruling owners and evidence normatively;
  - remove the RC-10 name collision;
  - replace the dangling reference to G's comparison;
  - correct D6:83's description of the 07.1 changes.

No required change adds or lowers an operator gate, or weakens any contract, domain, accepted case, fixture, control, threshold or proof floor.

### Open obligations

- OB-001 … OB-219, all OPEN, with no closure credited.
- V6-REQ-A … V6-REQ-L; V5-REQ-A, C, D, E, F, G, I, J and K (PARTIALLY_CLOSED above).
- Every PARTIALLY_CLOSED clause and ruling.
- CG-1 … CG-4.
- CJ-DISP-1 … 6, CJ-ARCH-1 … 3, CJ-JSON, CJ-H-1 … 4, and OB-ESC with AU-2.
- K-1 … K-28 (OP-7); RC-1 … RC-7 and RC-9 … RC-12.
- D-4a; H′'s deltas D-H1 … D-H6, plus the missing request-root launch delta.
- All bodies, proofs, costs and controls; P-A1 … P-A4.
- CAPI6R's open items, ROOT_WORKER_INTEGRATION and IC-10.
- Hosted assurance, publication, deployment and Phase One acceptance.

JACKAL (checks.json):
- J6-1 `(2^8 - 1) + 1 - 2^8`: status=exact, 0.
- J6-2 `(2^(8*4) - 1) + 1 - 2^(8*4)`: **refused** (evaluator-refused: "^ requires an integer exponent in exact mode"). I then asked a different question.
- J6-3 `(2^32 - 1) + 1 - 2^32`: status=exact, 0.

Non-claims: NOT formal-bounded; exact rational arithmetic, not yet checker-covered; informational about arithmetic only.
