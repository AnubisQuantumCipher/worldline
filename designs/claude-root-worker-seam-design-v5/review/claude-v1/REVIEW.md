**WORLDLINE Phase One root-worker SEAM DESIGN v5: independent design review**

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**

- Reviewer: an independent Claude Code review subagent (claude-opus-5-5) with a fresh context.
- Author: Claude Code lead claude-opus-5-5, through a drafting subagent. I authored nothing under review.
- Scope of the verdict: it endorses the design's direction, subject to V5-REQ-A … V5-REQ-M below. It grants no source, proof, runtime, lane, phase, deployment or operator acceptance. proof_acceptance=false, phase_acceptance=false, source_acceptance=false.
- Obligations: every original Phase One obligation, OB-001 … OB-219, stays OPEN. The draft lane stays INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY (L/handoff-to-claude-v1-retry1/HANDOFF.md:3).

**Aliases**

| Alias | Path |
|---|---|
| W | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow |
| WT | W/work/claude-lead-isolation-v1/wt-1 |
| D5 | WT/designs/claude-root-worker-seam-design-v5/SEAM-DESIGN.md |
| D4 | the v4 SEAM-DESIGN.md |
| D3 | the v3 SEAM-DESIGN.md |
| D2 | the v2 SEAM-DESIGN.md |
| D4R | WT/designs/claude-root-worker-seam-design-v4/review/gpt61-v1 |
| L | W/work/protected-original-root-worker-repair-v1 |
| rw/ | L/source/runtime/worldline/ |
| pre/ | L/preimage/runtime/worldline/ |
| core/ | L/source/core/ |
| C1 | L/source/protected-root/native_root_worker_supervisor_v1.c |
| P1 | W/outputs/claude-phase1-handoff-20261004 |
| CAPI5, CAPI6 | WT/designs/claude-capi-boundary-design-v5, -v6 |
| S5 | W/work/claude-composition-v5-beta/source |

**Identities (computed)**

| File | sha256 |
|---|---|
| Brief root-worker-seam-design-v5.md | e3d4f7f82e525c650a7edb6dfd2a1b9d6f605726cd80d089b5ca15aaee596190 |
| D5 | 938c832d03df0910506756ec295acef86ae2cacba4d7b2478a09c6d27f3685cf (matches the brief) |
| seams.json | a3d3ff5482c188705050f7f83709ff2f5e418547ed4a71f26f705f8c5fe18ebe (matches) |
| jackal.json | 9adaaa83960f7064552dee1f85ffa38ad5191f0e6d6cd02321b287121e931628 (matches) |
| AUTHOR-NOTES.md | d6e16bdfb23b2544218694508144ba32f72ab3c23f79fa9dcb0f2117d324b836 (matches) |

The v4 design, v4 seams.json and the four sealed D4R files all match their stated hashes. All 37 Appendix B input hashes (D5:1569-1605) match the current bytes. The sealed CAPI5R and CAPI6R hash prefixes match D5:10. The CAPI5R verdict reads ENDORSED_WITH_REQUIRED_CHANGES and the CAPI6R verdict reads ENDORSED.

**Process**

- **What I did.** Passive reading and hashing only: `cat`, `sed`, `grep`, `sha256sum`, `diff` and stdin Python that printed to stdout. Nothing was imported or executed. No compiler, prover, test, service, sudo, project-vault or restic was run. No file was written.
- **What I did not read.** The v5 review/ directory, any transcript, WT/packets, the in-progress reviews named by the brief, and the SIA gbrain store.
- **SIA.** I made no `sia.ask` call, so that this review stays independent of any recall about this revision. This deviates from the global CLAUDE.md start-of-task rule and is disclosed here. No SIA note was written.
- **Ada skills.** All eight Ada skills were loaded before reading the Ada specifications.
- **JACKAL.** J5-1 … J5-4 were re-run in one group of four (checks.json).

---

### 1. Closure of V4-REQ-A … V4-REQ-L, RQ-1, clauses and rulings

| Item | Closure | Remaining gap | Evidence |
|---|---|---|---|
| V4-REQ-A | PARTIALLY_CLOSED | **The "one wire convention" is labelled observed, but the existing exports do not share it.** The child and scoped-ledger entries take only (pointer, size) pairs, with Input before Arena. The exchange and chain entries mix pairs and (pointer, count, stride) triples. The WL_ABI_CAPACITY retry is new. X-8 (V2 successors of pair-convention exports) and the sub-helper's material ("with counts and strides") therefore have no fixed convention. **X-5 `RootStateRec` disagrees with V5-F.1 `Root_State` and the V5-J.2 DDL.** It keeps the withdrawn `stop_intent` and a `returned` flag. It lacks Owners_Open, Abort, Launched, Witness, Settled, Released_Unlaunched and Reattach_Epoch. The V1 fallback is additive, and every original export is kept. | D5:455-461, 500, 518, 816, 851-862, 877, 1291-1317; rw/resource_child_execution.py:105-121, 207; rw/resource_scoped_run_ledger.py:316-321; rw/canonical_exchange_kernel.py:37; rw/chain_authority.py:75-76 |
| V4-REQ-B | PARTIALLY_CLOSED | **Witness union: closed at design level.** R5-1 … R5-3, R5-12 and R5-13 are exact and consistent with seams.json. **RQ-1 per class: improved, with three problems.** (i) IP requests served while a worker owns run inside the root unit admitted for the WL request, which is G's handler-bound gap (V5-REQ-B). (ii) The dispatcher's interface is incomplete (V5-REQ-D). (iii) The carried v4:1801 control contradicts V5-B.5 (V5-REQ-L). The serial order is kept, and CG-1 is correctly not counted as preserving anything. | D5:579-641; D4:1801; rw/runner.py:342, 804 |
| V4-REQ-C | PARTIALLY_CLOSED | **What is done.** The sign channel, Round/Repr layout, thresholds and the bounded rollback claim are specified. The premises are now OPEN obligations (R5-14). **The archive_equal premise is false.** It says the archive "stores the canonical text" and that numbers are "never" compared through binary64. In fact the archive stores an int as a sign plus little-endian magnitude bytes, and a float as its binary64 bit pattern. The comparison therefore needs decimal-to-binary conversion and binary64 rounding, and their correspondence and costs are unspecified (V5-REQ-E). The original's refusal class for overflow lexemes is also unmapped. | D5:683-703, 693; rw/operation_capture.py:34, 36; rw/evaluation_terminal.py:76-86; rw/finalization_journal.py:57-60; rw/protected_startup.py:35-51 |
| V4-REQ-D | PARTIALLY_CLOSED | **G stays unselected (correct). H is offered but incompletely compared.** The runner launches one unit per agent and can launch several per WL request. `launch_reserved` dispatches once per reservation, only for top-level rows, and has no static caller. H needs an undesigned per-agent mapping, and its AO-1/AO-2/AO-10 ✓ marks are not established (V5-REQ-K). **The default route shares G's AO-5/AO-6/AO-11 handler-bound gap** for IP requests served in the worker (V5-REQ-B). | D5:713-741; rw/runner.py:694-703; rw/protected_scoped_resource_runtime.py:705-706, 723, 769 |
| V4-REQ-E | PARTIALLY_CLOSED | **Done:** the candidate, then agreement, then the exclusive READY/ABORT protocol, the terminal committers and frame-by-frame commands are coherent. **Gap:** V5-E.2 places the sub-helper "outside the coordinator's namespaces". But the V1 root helper calls `unshare(CLONE_NEWPID)` before forking init. [Unverified reasoning, mine] Later forks of that process are then created in the new PID namespace. The mechanism is unspecified and has no measurement item (V5-REQ-J). | D5:749-820, 785-786; C1:336-337 |
| V4-REQ-F | PARTIALLY_CLOSED | **Done:** the three relations, XC-1 … XC-7, r1′, r6′ (as XC-5), HANDOFF_ABORT and the pending-intent table are given. The M8(c) withdrawal is acceptable. **Gaps:** (i) WORKER_REATTACHED is legal only in Worker_Owned … Worker_Relinquish, while Unknown is left only by RECONCILED on "authentic durable evidence". A live worker in Unknown has no durable path back (V5-REQ-G). (ii) The PREPARED ordering and the launch-journal state behind HANDOFF_ABORT are unspecified against the lane code (V5-REQ-H). (iii) The X-5 record mismatch above. | D5:883-1035, 902, 908-909, 1464 |
| V4-REQ-G | PARTIALLY_CLOSED | **Done:** the no-launch route is designed without CLOSED_WITNESS, and RT-21 … RT-29 are specified. **Gaps:** (i) it presumes the launch journal stays Never_Dispatched, but the lane's no-slot failure branch appends UNKNOWN unconditionally (V5-REQ-H). (ii) CUSTODY_RETURNED requires pidfds "held by the front since HELD". These are process-local and lost when the front restarts (V5-REQ-F). | D5:1043-1077, 903, 1074; rw/protected_root_resource.py:80-89, 142-148; rw/root_worker_closed.py:41-42 |
| V4-REQ-H | CLOSED_AT_DESIGN_LEVEL | Every row now matches actual descriptor custody. ARMED is written before the reader. The fold, the exact kcmp operands, last-writer EOF and K-25 are present. Physical and lab evidence (K-25, OP-7) stays OPEN. | D5:1085-1130; C1:348-349 |
| V4-REQ-I | PARTIALLY_CLOSED | **Done:** the joins are separated, presence is three-valued, and the gate table and RELAY frame are specified. **Gaps:** (i) RELAY transport loss maps onto "the exception the original re-read raises for a closed client connection" (RC-10). `KernelPeer._read` re-reads fstat and SO_PEERCRED on an owned duplicate. [Unverified reasoning, mine] After the client closes, that read likely returns cached credentials and raises nothing. No fallback is specified if so, so the mapping may add a refusal and quarantine. (ii) The daemon-level steps for transferred requests are unspecified (V5-REQ-I). | D5:1138-1233, 1225, 1518; rw/client_peer.py:73-90, 131-137; rw/daemon.py:307-360 |
| V4-REQ-J | PARTIALLY_CLOSED | **Done:** the ORIGIN/EVENT head under `foreign_keys=ON`, the lossless BLOB quantities, the complete DDL and fold, and migration to a new plan, journal and genesis path. **Gaps:** the native genesis archive_equal inherits the V5-REQ-E error, and the X-5 record does not match the DDL. | D5:1245-1386, 474; rw/root_worker_journal.py:13, 95-100; rw/root_worker_codec.py:19-20 |
| V4-REQ-K | CLOSED_AT_DESIGN_LEVEL | **Done:** five checkviews over byte-immutable base tables. RW_SPARK_UNITS is the reviewed enrolled roster. MQ-RW2a targets a new census member: `Owner_Wire.Raw_Request`, at S5:882; `Raw_Request` appears in no CAPI5/CAPI6 name table. MQ-RW2b changes an old-scope call. PX-RW3 uses `Decide`, which is already listed. There is no RW wfx row or RW exclusive-map key. **Still OPEN:** implementation, the stage reviews and IC-10. | D5:1402-1436; CAPI5/APPENDIX-BINDINGS.md:193, 366-367; CAPI6/APPENDIX-BINDINGS.md:401-404; S5/core/worldline-c_api.adb:879-882, 1024-1027 |
| V4-REQ-L | PARTIALLY_CLOSED | **Done:** the reattach endpoint and CUSTODY_RETURNED, and most added waits end at a named event. **Gaps:** (i) Later WL requests are queued for g+1 for the whole life of the first operation's detached jobs. That breaks P1's "original per-request concurrency", and v5 makes it depend on an operator D-4a selection (V5-REQ-C). (ii) CUSTODY_RETURNED after a front restart (V5-REQ-F). (iii) Unknown with a live worker (V5-REQ-G). (iv) `job.cancel` cannot be served while the worker is unreachable. | D5:600, 741, 1456-1473; rw/protected_root_worker.py:184-190; P1/HANDOFF.md:115 |
| RQ-1 | PARTIALLY_CLOSED | The equivalence claim is correctly withdrawn and the classes are split. Still open: the IP worker-served physical-bound difference is unstated; the WL W3 stop is a stated difference; and the WL queueing difference. The proofs and controls are absent. | D5:593-625; rw/protected_scoped_resource_runtime.py:770-776 |

**Clauses still open after v4.** v5 changes the status of 04.1 and 07.3 from NOT_CLOSED to PARTIALLY_CLOSED. The 28 clauses that v4 closed are carried, and their text checks equal (§2).

| Clause | v5 closure | Remaining gap | Evidence |
|---|---|---|---|
| 01.1 | PARTIALLY_CLOSED | ABI convention and X-5 record (V5-REQ-A) | D5:455-525 |
| 01.2 | CLOSED_AT_DESIGN_LEVEL | Precise union and four-form roster | D5:221-246, 316-327, 579-585 |
| 01.3 | CLOSED_AT_DESIGN_LEVEL | The S-b union and R3 count N; the forms agree. RQ-2 coverage stays OPEN | D5:238, 245, 583-584 |
| 01.5 | PARTIALLY_CLOSED | Saturated witness specified; D_prod coverage (CV-B′, CV-R) OPEN | D5:589 |
| 01.7 | PARTIALLY_CLOSED | As RQ-1 | D5:593-625 |
| 02.1 | PARTIALLY_CLOSED | archive_equal numeric premise (V5-REQ-E) | D5:693; rw/evaluation_terminal.py:81-84 |
| 02.2 | PARTIALLY_CLOSED | Claim bounded honestly; authentic selection and currentness remain unmet obligations | D5:651-673 |
| 02.3 | PARTIALLY_CLOSED | Crosswalk record given; convention and costs OPEN | D5:485-489 |
| 02.4 | PARTIALLY_CLOSED | No option meets every AO; H incomplete | D5:717-741 |
| 03.2 | PARTIALLY_CLOSED | Sub-helper namespace placement (V5-REQ-J) | D5:785; C1:336 |
| 03.3 | PARTIALLY_CLOSED | CG-1 persists in deployments without a root worker; dispatcher interface incomplete | D5:629-641 |
| 04.1 | PARTIALLY_CLOSED (was NOT_CLOSED) | A complete product now exists; Unknown/reattach, PREPARED ordering and X-5 gaps remain | D5:883-1013 |
| 04.3 | PARTIALLY_CLOSED | X-5 record versus DDL | D5:500, 1291-1317 |
| 04.4 | PARTIALLY_CLOSED | CUSTODY_RETURNED after a front restart | D5:903, 1074 |
| 06.2 | PARTIALLY_CLOSED | As V4-REQ-D | D5:721-739 |
| 06.3 | PARTIALLY_CLOSED | M8(c) withdrawn (acceptable); cancel progress while unreachable or Unknown is open | D5:995, 1461-1464 |
| 06.4 | PARTIALLY_CLOSED | Later WL requests queued for g+1 | D5:1467 |
| 07.1 | CLOSED_AT_DESIGN_LEVEL | Separate relations, XC-1 … XC-7, r1′ … r6′ | D5:932-973 |
| 07.3 | PARTIALLY_CLOSED (was NOT_CLOSED) | Route admitted; its launch-journal and PREPARED preconditions do not hold against the lane code (V5-REQ-H) | D5:968, 1043-1055; rw/protected_root_resource.py:144-146 |
| 08.1 | CLOSED_AT_DESIGN_LEVEL | Reattach only through a live read end | D5:1097-1110 |
| 08.2 | CLOSED_AT_DESIGN_LEVEL | Interval fold, write fold and per-row survival | D5:1085-1095, 1116-1126 |
| 08.3 | CLOSED_AT_DESIGN_LEVEL | ARMED before the reader | D5:1088, 1104-1105 |
| 08.5 | CLOSED_AT_DESIGN_LEVEL | Rows rewritten against surviving custody | D5:1112-1126 |
| 09.1 | CLOSED_AT_DESIGN_LEVEL | Root_Admission_Join; operands with presence | D5:1138-1178 |
| 09.2 | PARTIALLY_CLOSED | RELAY transport-loss premise (RC-10) | D5:1225 |
| 09.3 | CLOSED_AT_DESIGN_LEVEL | Complete gate table by phase and mode | D5:1184-1206 |
| 09.5 | PARTIALLY_CLOSED | Unknown/reattach service dependency | D5:1464 |
| 11.1 | PARTIALLY_CLOSED | Per-export edges given; convention gap | D5:548-571 |
| 12.1 | PARTIALLY_CLOSED | X-5 versus DDL; native genesis compare | D5:500, 1369 |
| 12.2 | PARTIALLY_CLOSED | CUSTODY_RETURNED after restart; no-launch preconditions | D5:903, 1046-1047 |
| 12.4 | PARTIALLY_CLOSED | Unavailable-owner and Unknown progress | D5:1461-1464 |

**Rulings.**

- D-2b stays CLOSED_AT_DESIGN_LEVEL. It is carried through C2-116, and the frontier sha256 is a0d2d529… (D5:136).
- D-1a, D-1b, D-2a, D-3a, D-4a, D-5a, D-5b, D-6a, D-7a, D-8a, D-8b and D-9a all stay PARTIALLY_CLOSED. The gaps are those of the required changes mapped to each (D5:132).
- The owner and evidence strings at D5:117-130 equal review.json byte for byte (script check).
- D-3a is not closed even though V4-REQ-H is closed at design level, because its lab and physical evidence is still OPEN.

### 2. Carried items

**Slices and replacements.**

- **Slices verify.** All 14 C4 slices (D5:189-204) hash-verify against D4. There is no overlap. Every D4 line falls in a slice, in a superseded range, or is blank or `---` (34 lines).
- **R5 quotes are exact.** Each of R5-1 … R5-17 quotes its stated lines exactly.
- **R5 targets are where they say.**
  - R5-1 … R5-3 (in C3-VB, 796-955) avoid the R4-19 (814) and R4-20 (846-849) targets.
  - R5-4 (D3:1179) sits between R4-63 (1178) and R4-64 (1180) and is replaced by no R4.
  - R5-5 lies in C3-VF1 (verbatim).
  - R5-6/7/8/9/10/11/16/17 each target the `v4:` result line of R4-27/31/48/49/56/64/1/5 respectively (D4:443, 480, 628, 636, 692, 748, 227, 259).
- **Withdrawals are bounded correctly.** W5-1 ends at D2:1003, which is empty; D2:1004 begins "Invariants of the relation.". W5-2 equals C3-VF5 (D3:1299-1374), including R4-29's result.

**Are the withdrawals justified?**

- **W5-1 is justified.** V5-F.2 restates every root row. The PHYSICAL_SETTLED → HISTORICAL_SETTLEMENT row (R3-13) is replaced by Custody_Returned → HISTORICAL_SETTLEMENT plus phase-independent physical events. That is correct only once V5-REQ-F is met, because the normal completion path now also passes through CUSTODY_RETURNED.
- **W5-2 is justified** (V5-J.2).

**Are R5 and W5 the only changes? No.** RR5-7 and V5-M prose also change carried text:

- **v4:1804 (CARRIED_VERBATIM).** "M8 admits … the M8 (c) stop" is turned into a refusal check by prose (D5:407, 1491). This is a strengthening.
- **v4:1801 (CARRIED_VERBATIM).** It still reads "Windows W0 … W5 on the root route … The root route's guard order equals the serial route's". That contradicts V5-B.5: IP operations no longer take the root route, and the root route omits step 5 (D5:598-602). No R5 corrects it.

Both need explicit quoted replacements (V5-REQ-L).

**Quoted review text matches, and carried assessments are unchanged.**

- Every V4-REQ change, PARTIALLY_CLOSED and NOT_CLOSED clause gap, ruling owner, evidence and gap, the RQ-1 windows and gap, the ten open_design_dependencies, and the OP-7 reservation text are found verbatim in D5.
- The NF-1 … NF-11, N-1 … N-10 and DF-1 … DF-6 labels equal `carried_assessments`. Each NF4 status equals `findings_detail[].status`.
- The 28 closed clauses and RC-05/RC-10 are carried by their slices. 04.5's outer test is carried in C4-VG23. R5-15 adds a custody-only alternative but no settlement (D5:139, 346).
- OP-1 … OP-9 owners and kinds are unchanged.
- One condition on clause 09.4: it stays closed only if V5-REQ-I keeps RELAY transport loss from becoming a new refusal.

### 3. NF5-1 … NF5-7, checked statically

| Id | Assessment | Consequence for the design | Evidence |
|---|---|---|---|
| NF5-1 | VERIFIED_STATIC_WITH_OWNER_ROUTE_EXCEPTION | Every request goes through `principal.invoke` when a principal exists. But the owner operations return before `_reserve`, so not every request reserves a use. `retain_client_request` precedes `_invoke` (a store write). The lane's router redirect at :313 runs before it. The design must say which daemon-level steps run in the custody owner for FRESH and RELAY requests (V5-REQ-I). | rw/daemon.py:307-313, 342-360, 379-386; rw/protected_operations.py:731-742 |
| NF5-2 | VERIFIED_STATIC_INCOMPLETE | The runner also calls `systemd.outcome(...)`. It reads `unit.pid` and `unit.launcher.wait()`, uses the launcher's stdin, stdout and stderr, and branches on the supervision dict. A four-method dispatcher is not the interface the runner uses (V5-REQ-D). | rw/runner.py:276, 342-347, 697-703, 804, 837-908, 935-982; rw/linux/systemd.py:156-170, 472, 492, 623, 717 |
| NF5-3 | VERIFIED_STATIC | The command is `systemd-run --system --no-block`, with Type=exec, RemainAfterExit=yes, Delegate=no, User=root, Group=root, the plan's properties and the V3 helper argv. Also: `launch_reserved` has no static caller, and it allows one dispatch per NEVER_DISPATCHED reservation with `parent is None`. That matters for H (V5-REQ-K). | rw/protected_scoped_resource_runtime.py:698-776 |
| NF5-4 | VERIFIED_STATIC_ABSENCE_IN_SELECTED_SOURCE | No `wl_scoped_*` symbol exists anywhere in L/source. Both X-9 entries are new. | grep over L/source (checks.json) |
| NF5-5 | VERIFIED_STATIC | The custody channel is SOCK_STREAM with SO_PASSCRED on both ends; the actor channel is SOCK_SEQPACKET (it also sets SO_PASSCRED). | C1:323-330 |
| NF5-6 | VERIFIED_STATIC | It supports withdrawing M8(c). | rw/controller.py:811-826; rw/runner.py:471-483 |
| NF5-7 | VERIFIED_STATIC | The store also sets foreign_keys=ON and synchronous=FULL. | rw/store.py:278-284 |

**Reviewer static findings (RF).** Each feeds the required change named.

| Id | Finding | Required change | Evidence |
|---|---|---|---|
| RF-1 | The archive stores ints as sign plus LE magnitude and floats as binary64 bits | V5-REQ-E | rw/evaluation_terminal.py:81-84 |
| RF-2 | `owner.retry` is refused UNINTEGRATED on the serial route, yet D5 calls the OW class "unchanged". CG-1's refusal predates the lane. | V5-REQ-L | rw/protected_operations.py:735-737; pre/protected_operations.py:720-722, 729-730; D5:594, 629 |
| RF-3 | Sub-helper placement relative to the root helper's PID-namespace unshare | V5-REQ-J | C1:336 |
| RF-4 | The lane's no-slot failure branch appends UNKNOWN to the launch journal unconditionally. The original's equivalent branch appends UNKNOWN only in dispatched phases. | V5-REQ-H | rw/protected_root_resource.py:144-146; rw/protected_scoped_resource_runtime.py:771-773 |
| RF-5 | `KernelPeer` re-reads SO_PEERCRED on an owned duplicate | V5-REQ-I | rw/client_peer.py:73-90 |
| RF-6 | X-5 `RootStateRec` mismatch with `Root_State` and the DDL | V5-REQ-A | D5:500 |
| RF-7 | IP requests served in the worker run under the WL root unit's bound | V5-REQ-B | D5:599, 730, 784 |
| RF-8 | The lane commits PREPARED after DISPATCH_INTENT, while V5-G.1 needs it before the launch | V5-REQ-H | rw/protected_root_resource.py:80-89; D5:885, 1046 |
| RF-9 | v4:1801 stale | V5-REQ-L | D4:1801 |
| RF-10 | CUSTODY_RETURNED evidence after a front restart; no-escape premise appears only in AUTHOR-NOTES:59 | V5-REQ-F | D5:903 |
| RF-11 | Unknown/reattach circularity | V5-REQ-G | D5:902, 909 |
| RF-12 | Later-WL serialization made contingent on D-4a | V5-REQ-C | D5:741; P1/HANDOFF.md:115 |
| RF-13 | H's per-agent launch mapping | V5-REQ-K | — |

### 4. New refusals, caps, narrowed domains, changed behaviour, added assumptions

- **Routing change: right direction, overclaimed costs.**
  - Serving IP operations serially in the custody owner removes the lane's added launches (rw/protected_operations.py:718-725), which is correct.
  - While a worker owns, though, IP handlers run in the coordinator, under the systemd properties admitted for the WL request's reservation (D5:599, 784; rw/root_worker_plan.py:37).
  - That is exactly the handler-bound gap for which G stays unselected (D5:730, 737).
  - So the statement that IP "durable outcome, recovery and cost … are the serial route's" (D5:625) overclaims for worker-served IP. This is a changed original behaviour that must be stated and kept OPEN (V5-REQ-B).
- **M8(c) withdrawal: acceptable.**
  - It removes a non-original stop that lacked authority (D4R REVIEW.md:277-278). `job.cancel` keeps its original handler and stays in the store-custody owner.
  - It weakens no control; the V4-M check becomes a refusal check.
  - What remains is a progress obligation: cancel while unreachable or Unknown.
- **CG-1: classified correctly as an OPEN containment gap.**
  - It is the only route for WL requests in deployments without a root worker (D5:632).
  - It is inherited from the reviewed preimage (pre/protected_operations.py:729-730), not added by the lane.
  - The analogous `owner.retry` refusal is unrecorded (V5-REQ-L).
- **WL W3 stop: a stated difference, not an equivalence.** The original scoped launch stops nothing (rw/protected_scoped_resource_runtime.py:770-776). The root launch stops the unit (rw/protected_root_supervisor.py:355-358). It stays OPEN (D5:621).
- **Queueing later WL requests for g+1 is a new progress restriction against P1/HANDOFF.md:115.**
  - The first WL operation's detached jobs keep the worker owning (rw/protected_root_worker.py:187-190), so later WL requests can wait for those jobs to finish.
  - Meeting an original obligation cannot be made conditional on an operator selection, because D-4a cannot waive it (D5:741; D4R REVIEW.md:284).
  - It must be an OPEN containment gap with its own closure route (V5-REQ-C).
- **Added assumption.** CUSTODY_RETURNED depends on the worker never passing a custody descriptor out of the namespace. This appears only in AUTHOR-NOTES.md:59, not in the design's obligations (V5-REQ-F).
- **Not found:** a new cap, a narrowed numeric domain, a retired or weakened control (the frontier control is unchanged, D5:136), or a lead-only acceptance.
- **Option H:** a promising faithful direction, but it rests on D-H1 … D-H5 plus the missing per-agent mapping (V5-REQ-K). Its "meets AO-1 … AO-7, AO-9, AO-10" (D5:739) is not established at design level.

### 5. C-API integration

- Sound and complete against CAPI5R and CAPI6R at design level, as summarised under V4-REQ-K.
- CR6's wfx roster comes from CAPI_WFX_PROTOCOL and CAPI_GATE_EXCLUSIVE in the base tables only (CAPI6/APPENDIX-BINDINGS.md:401-404; D5:1412).
- There is no RW wfx row or exclusive-map key (MX-RW1, MX-RW2; D5:1420-1421).
- Every CAPI table stays byte-immutable (D5:1404).
- MQ-RW2a's precondition guard is stated (D5:1424).
- Neither lane's acceptance or integration order is decided.

### 6. Operator items

- OP-1 … OP-9 keep exactly their reserved scope. Nothing is added or lowered.
- K-24 … K-27 extend OP-7's range the same way R4-1 and R4-5 did (D5:349-363, 1508-1515), within the D-8b kind.
- **K-27 includes a dynamic-loader component**: loading the library through `/proc/self/fd`. That is a userspace installed-runtime question and should be a lead-owned RC item, with only the kernel memfd-seal mapping kept under OP-7. Otherwise lead work moves into the operator reservation (V5-REQ-M).
- RC-7, RC-9 and RC-10 are correctly lead-owned.
- The kernel measurement V5-REQ-J requires belongs under the same OP-7 reservation. It is not a new gate.
- No approval gate is added.

### 7. Other concerns

- **[Unverified reasoning, RC-5] JSON overflow refusal class.** `exact_json` and `exact` would raise ValueError from `json.dumps(..., allow_nan=False)` for an overflow lexeme such as `1e309`. That is not their named refusal (rw/protected_startup.py:35-51; rw/protected_resource_runtime.py:20-23). The native `Number_Not_Finite` status must map to the original exception class at each caller.
- **K-24 as the sole evidence for CUSTODY_RETURNED.** The V1 init itself reaps until ECHILD (C1:296-305), so K-24 matters only when init dies abnormally. A fresh `flock` on the transferred lock files would be stronger no-holder evidence after a front restart (rw/root_worker_journal.py:59-62). This is offered as an option, not as a requirement.

### Required changes for v5

- **V5-REQ-A.** Correct V5-A.1:
  - Record the actual conventions per existing export: pairs for the child and scoped ledger; pairs plus triples for exchange and chain.
  - Fix the convention of each new and successor export, including X-8 and the sub-helper's material layout.
  - Make X-5 `RootStateRec` field-for-field equal to `Root_State` and the V5-J.2 columns, with no `stop_intent`.
  - Evidence: D5:455-461, 500, 518, 816, 851-862; rw/resource_child_execution.py:105-121; rw/canonical_exchange_kernel.py:37; rw/chain_authority.py:75-76.
- **V5-REQ-B.** State that IP requests served in the worker run under the WL request's root-unit bound (AO-5/AO-6/AO-11, as with G). Withdraw the cost-equality claim for them, and either design a route that borrows no other request's bound or record an OPEN containment gap with a closure condition. Evidence: D5:599, 625, 730, 784.
- **V5-REQ-C.** Record the later-WL queueing as an OPEN containment gap against P1/HANDOFF.md:115, with its own closure condition. Do not make the original per-request concurrency depend on a D-4a selection. Evidence: D5:600, 741, 1467.
- **V5-REQ-D.** Complete the dispatcher interface and CJ-DISP-1: `outcome`, `pid`, `launcher.wait()`, launcher stdio and the supervision dict semantics, with the original exception types. Evidence: rw/runner.py:276, 342-347, 804, 837-908, 935-982.
- **V5-REQ-E.** Specify archive_equal as a typed comparison against the actual archive encoding: int as sign plus magnitude; float as binary64 bits via Round, with the −0.0 sign bit. Give its correspondence and costs, correct D5:693, and map the original ValueError refusal class. Evidence: rw/evaluation_terminal.py:76-86; rw/operation_capture.py:34.
- **V5-REQ-F.** Define authentic CUSTODY_RETURNED (and XC-4) evidence when the front has restarted and holds no pidfds. Make the no-custody-descriptor-escape premise an explicit design obligation, with an audit and a control. Evidence: D5:903, 964, 1074; AUTHOR-NOTES.md:59.
- **V5-REQ-G.** Give a legal, durable route from Unknown back to service for a live, reattachable worker. Specify what the worker does while its mutations are refused. Evidence: D5:902, 908-909, 930, 1464.
- **V5-REQ-H.** Specify PREPARED before machine admission and Record_Launch_Intent. Replace the lane's unconditional UNKNOWN append in its no-slot failure branch with the original phase-conditional append, so that Never_Holds and Release_Hold apply. Evidence: rw/protected_root_resource.py:80-89, 144-146; rw/protected_scoped_resource_runtime.py:771-773; core/resource_observation_classification.ads:96-102; core/resource_run_ledger.ads:317-320.
- **V5-REQ-I.** Give RELAY transport loss an outcome for the case where RC-10 shows the original re-read raises nothing, without a new refusal or quarantine. Specify the daemon-level steps for FRESH and RELAY requests: peer capture, `retain_client_request`, the mutation lock, publish, and the send. Evidence: D5:1225; rw/client_peer.py:73-90; rw/daemon.py:342-360.
- **V5-REQ-J.** Specify how a sub-helper is created outside the coordinator's PID namespace given the root helper's `unshare(CLONE_NEWPID)`, and add a kernel measurement under OP-7. Evidence: D5:785; C1:336-337.
- **V5-REQ-K.** Complete H's comparison with the mapping from per-agent launches (several per request) onto `launch_reserved`, whose dispatch is single per reservation and top-level only, and revise its AO marks. Evidence: rw/runner.py:694-703; rw/protected_scoped_resource_runtime.py:705-706, 723.
- **V5-REQ-L.** Add explicit R5 replacements for v4:1801 and v4:1804 in place of reading-rule neutralisation. Correct CG-1's attribution to the preimage. Record `owner.retry`'s UNINTEGRATED refusal as an OPEN containment gap. Evidence: D4:1801, 1804; D5:407, 594, 629; pre/protected_operations.py:720-722, 729-730.
- **V5-REQ-M.** Split K-27: kernel memfd mapping stays under OP-7; the loader behaviour becomes a lead-owned RC item. Evidence: D5:1515.

No required change lowers or adds any operator gate, contract, domain, accepted case, fixture, control, threshold or proof floor.

### Open obligations

- OB-001 … OB-219, all OPEN with no closure credited.
- V5-REQ-A … V5-REQ-M; V4-REQ-A … V4-REQ-L except as closed at design level above; V3 and V2 REQs; RQ-1 … RQ-5.
- CG-1, the owner.retry containment, and the later-WL queueing gap.
- K-1 … K-27; RC-1 … RC-7, RC-9, RC-10.
- D-4a; H's deltas D-H1 … D-H5.
- All bodies, proofs, costs and controls; CAPI6R's open items, ROOT_WORKER_INTEGRATION and IC-10.
- Hosted, publication and deployment acceptance.

JACKAL (checks.json): J5-1 … J5-4 re-run; each `status=exact`, `lane=rat`, `formal=false`, positive. Non-claims: NOT formal-bounded; exact rational arithmetic (not yet checker-covered); informational about arithmetic only, not evidence of the installed CPython thresholds.
