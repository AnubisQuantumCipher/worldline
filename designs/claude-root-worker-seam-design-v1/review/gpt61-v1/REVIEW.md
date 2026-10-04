WORLDLINE Phase One root-worker SEAM DESIGN v1 — independent design review

Verdict: **ENDORSED_WITH_REQUIRED_CHANGES**.

Actual model selection: gpt-6.1-sol. Author under review: Claude Code lead claude-opus-5-5 (analysis subagent). Different-author review: true. I authored none of this design or the lane source. This verdict reviews the Claude design; it grants no acceptance to the independently authored draft lane.

Design: [SEAM-DESIGN.md](/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1/SEAM-DESIGN.md)
SHA256: 531d11282f811518b868470c0012f23a5e34bdbe3891ef39194cd8f230933f46

Decisions: [seams.json](/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1/seams.json)
SHA256: b8fa87fb573596de9fa0a789b7a8c93c909eeeb18f4d192edad73e038a2caf5d

This review used passive text/AST reading and hashing only. No WORLDLINE, COSMOGONY or root-worker module or native code was imported or executed. No compiler, prover, test, service, namespace, lab, store, socket, window, sudo, project-vault or restic operation was used. No SIA note was written. Only create-only review artifacts were written in this directory. Linux namespace, OFD, wait and enforcement conclusions identified below are design reasoning, not kernel observations. Static identity is not authenticity or proof.

All original obligations remain OPEN. proof_acceptance=false; phase_acceptance=false; source_acceptance=false. The required changes must be incorporated and independently reviewed before this design is used as an implementation basis; that review still cannot supply absent proof or operational evidence.

File:line evidence uses these exact aliases. D:line and SEAM-DESIGN.md:line refer to the design above; seams.json:line refers to its paired decisions. R/<path>:line and L/<path>:line resolve below the stated source and lane roots. RW:line is the draft handoff. P1:line is the Phase One handoff; P1/<file>:line resolves in its directory. START-CLAUDE.txt:line resolves there too. LEAD/<path>:line and CAPI/<path>:line resolve in their stated design roots. An abbreviated filename after a full source citation retains that citation's directory.

- W = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow
- L = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/protected-original-root-worker-repair-v1
- R = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/protected-original-root-worker-repair-v1/source
- RW = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/protected-original-root-worker-repair-v1/handoff-to-claude-v1-retry1/HANDOFF.md
- P1 = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/outputs/claude-phase1-handoff-20261004/HANDOFF.md
- P1 directory = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/outputs/claude-phase1-handoff-20261004
- PROMPT = /home/sicarii/Documents/complete-phase1-prompt.txt
- LEAD = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1
- CAPI = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-capi-boundary-design-v2
- commonV4 = /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/reviewed-common-proof-source-composition-v4/source

1. Factual findings

The supplied SEAM-DESIGN.md and seams.json hashes match. The handoff, freeze, inventory, binary delta and readable delta also match the design's recorded basis identities. A passive whole-source read found the inventoried 736 regular files with matching byte hashes, lengths and file modes, and no extra or missing files. This is identity evidence only; directory modes, atomic snapshot authenticity and installed state are outside this check.

The Gate uses threading.Lock (L/dependency-source/lab/intent_gate.py:371). The scoped reservation path holds it at R/runtime/worldline/protected_scoped_resource_runtime.py:385, calls reconcile_context at :388, and reacquires it at :357; the same code is in the preimage. R/runtime/worldline/protected_operations.py:640 reaches that method. The deadlock finding is supported as static path reasoning conditional on reaching it and passing preceding guards. It was not reproduced; current startup can refuse earlier.

Standalone AST-literal extraction and a reviewer-written text normalization matching R/runtime/worldline/proof_manifest.py:420-450 found 171 effective preimage pins, all matching, and 191 effective draft pins with exactly one mismatch. The protected_operations.py effective pin at :1012 is 8be1f9ab2c689ecc9e915464e8e454863c205ca2f1f4a1763a5125aa2b61139e; recomputation gives 2a6d71c7ca81d456d41f242a880b8fa3e0f115d794f4772e115767236b183547. Construct and intake refuse on that mismatch (R/runtime/worldline/protected_startup.py:683-684; protected_root_worker.py:355-357). The observed source delta roster contains 60 paths, with 24 pin-covered and 36 unpinned; this describes delta paths, not the entire source tree. checks.json retains the complete unpinned roster.

Both attach_scoped_resource definitions and their shadowing are confirmed, already in the preimage. The later definition omits the selected producer path/lease membership check (R/runtime/worldline/protected_scoped_resource_runtime.py:52-58,961-964). Passive search finds no caller in source or dependency-source. The root route bypasses the original context, unresolved-use and workload checks (R/runtime/worldline/protected_operations.py:716-749; protected_root_worker.py:158-179).

The six expected identity pairs are assigned from the same values (R/runtime/worldline/protected_root_observation.py:36-49). The corresponding native identity equalities are vacuous, while other Controller_Valid predicates remain real predicates (R/core/worldline-resource_child_execution.ads:49-68). The process source lease also comes from caller-provided material (:74-83). The three scoped historical adapters have only getattr references and no implementation in the selected source/dependency trees (protected_scoped_resource_runtime.py:530-531,548-549,571-572).

Receive-before-origin ordering and the exact peer comparison are confirmed (R/runtime/worldline/root_worker_custody.py:183-204; client_peer.py:73-89,110-117). The source contains PID namespace creation and proc remounting (R/protected-root/native_root_worker_supervisor_v1.c:257-258,336), and its comment acknowledges a relative PID concern (:125-128). Linux PID rendering, exited-peer behavior and consequent intake failure remain unverified reasoning. Correct SEAM-DESIGN.md:939-941 to a conditional failure for an outside-namespace client with a changed reread, rather than every worker intake.

Origin and handoff bind the actor-stdin V4 primary (L/origin.json:7-18; L/handoff-to-claude-v1-retry1/HANDOFF.md:11-13). The listed files are absent from commonV4; observed core entry counts are 149 commonV4 and 176 preimage. Startup differs. worldline-c_api.adb sizes are 56543 preimage, 148068 draft and 56596 commonV4. This confirms a shared-file integration obligation, not an executed textual merge conflict. The C-API v2 review is conditional design lineage, not acceptance of v3 (CAPI/review/gpt61-v1/REVIEW.md:3,260,454; P1/HANDOFF.md:91,153).

JACKAL returned status=exact, formal=false, parsed=24+36, exact=60 and status=exact, formal=false, parsed=63-3, exact=60. All returned non_claims are retained in checks.json: NOT formal-bounded: this lane carries no Lean-checked certificate; The epistemic class above is the STRONGEST claim this result supports; exact rational arithmetic (not yet checker-covered). These results establish arithmetic only and no program correctness or acceptance.

2. Each of the ten seams

Seam 1 — Full scoped pre-effect conjunction. Requirement: ACCURATE_BUT_REFINEMENT_COVERAGE_INCOMPLETE. Direction: REQUIRES_CHANGES.

C1/C3/C4 preserve the intended clauses, but C2 and Single_Frame_Identity do not yet establish an equivalence. Original Native_Valid does not consume Facts; scoped Native_Valid checks classification and observation-head joins. Scope-frame origin/current validity impose additional relations. Define structural embedding, coherent witnesses and total projection without assuming the conclusion; cover original accepted and refusal inputs. Projection_Valid requires a zero remainder, so describe exact division, not rounding. Use semantic Same_Context and explicit arena/span correspondence. Original single-frame models must stay byte exact and no runtime flattening is allowed.

Dependencies and authority: SL-0, seam-7 inputs, reviewed C-API successor, scoped committed-envelope/K4 lineage, D1/D2 and admitted proof frame. SL-1 drafting can be passive and independent; proof/native wiring cannot borrow dependency acceptance.

Evidence: RW:28; P1:27-29,107-109,125-131; D:217-246,260-288; R/core/worldline-canonical_operation.adb:10-32; R/core/resource_run_ledger.ads:223-282; R/core/resource_scoped_run_ledger.ads:92-152,181-268,303-312.

Seam 2 — Startup/provisioning correspondence. Requirement: ACCURATE_BUT_RECOVERY_AND_CONTROL_PLAN_INCOMPLETE. Direction: REQUIRES_CHANGES.

Exact v2 dispatch and one-shot offline provisioning are sound directions. Define an exact union across every constructor, loader, descriptor schema, early envelope and creation-slot caller, not only runtime keys. Full DDL/head/admission checks and provisioned lock/genesis paths must remain explicit. Diagnostic startup cannot fabricate a mutable Store/controller when prior state is missing. Reconcile authentic durable committed/abandoned work automatically where native evidence permits; dead WORKER_OWNED must not always require owner action. Retain genuine owner resolution when uncertainty remains. Do not retire the v1 frontier control by lead adoption; keep it unchanged on its version/domain and add v2 positives. Any proposed re-enrollment needs explicit adjudication, with original controls still OPEN.

Dependencies and authority: Seam-9 ownership/crash table, seam-3 transferred slots, seam-7 schemas, original one-shot issuer/head lineage and SL-0. Provisioning/lab execution is operator-gated; drafting source is lead work.

Evidence: RW:29; P1:99,121,147-149; D:372-423,429-438; R/runtime/worldline/protected_startup.py:264-270,467-472; R/protected-startup/controls/test_protected_startup_v1.py:97-105; R/runtime/worldline/root_worker_journal.py:43-62,85-114.

Seam 3 — Other-LIVE resource custody. Requirement: ACCURATE. Direction: REQUIRES_PROTOCOL_DETAIL.

Transfer of the complete roster preserves the original domain; requiring other actors to terminate first would remove accepted cases. A DRAIN_TRANSFER offset alone cannot establish lossless pipe transfer: define the reader freeze barrier, asyncio-buffer/in-flight chunk transfer, durable spool positions, acknowledgment and failure ownership. Descriptor identity checks are not an OFD/lock/wait-ownership proof. Preserve the actual helper parent/wait producer or provide an authenticated relay; a transferred pidfd is not a portable transfer of reaping rights. All non-terminal rows retain origin and UNKNOWN holds. No descriptor/row cap may replace genuine large-roster cases.

Dependencies and authority: Native custody-phase relation, requester receive ordering, request queue/task protocol, return escrow and original actor-helper wait/drain lifetime. Operator lab demonstration required.

Evidence: RW:30; P1:125-127; D:484-527; R/runtime/worldline/protected_root_observation.py:57-97,122-142.

Seam 4 — Live request multiplexing. Requirement: ACCURATE_BUT_AVAILABILITY_AND_ACCOUNTING_INCOMPLETE. Direction: REQUIRES_CHANGES.

Fresh per-request admission and durable exactly-once routing are sound directions. Option A is not selected by this review: tying all new independent requests to the first root's amount/kind may refuse requests the original host/ledger domain accepts. Parent_Supports requires equal charge kind; different grants, owners, costs, larger later requests and rollovers need a full-domain accounting design. Do not borrow the first root grant or invent a coordinator cost. UNKNOWN has no known current owner to forward to; identify a protected recovery authority and actual original owner guards for every phase. Preserve the original quarantine.resolve exception rather than silently widening all owner routes. Removing gather-under-lock alone does not prove availability: synchronous filesystem/native/SQLite work and queue fairness remain obligations.

Dependencies and authority: Seams 1,3,5,7,8,9 and SL-0. The slice list omits seam-7 cost/interface dependencies. Lab demonstrations are operator-gated.

Evidence: RW:31; P1:113-115,127,141,149; D:562-608,612-626; R/core/resource_run_ledger.ads:247-262; R/runtime/worldline/protected_operations.py:728-745,391-397.

Seam 5 — Dynamic child dispatch. Requirement: ACCURATE. Direction: REQUIRES_NATIVE_DELEGATION_SUCCESSOR.

The full original workload capture, distinct task hold, same original use and physical ancestry requirements are preserved in intent. Delegate=yes conflicts with native Custody's literal Manager_Delegate=no. Changing only the HELD Python check cannot make root/child classification valid. Require a separately reviewed additive native delegation/custody model that retains the old no-delegation predicates and their accepted cases, proves coordinator inability to change ceilings or escape the budget, and feeds actual kernel observations. Preserve Parent_Supports, Original_Holds, equal/different workloads, optional world facts, actor credentials and original stdin/EOF. Kernel nesting/clone support are unmeasured. Helper source can be drafted; privileged delegation and real actor quota require operator action.

Dependencies and authority: All producer/parent/child/native classifier layers, child-authority secondary, actor stdin V4, seam-7 costs and admitted frame. D1/D2 affect helper/wrapper/native runtime cost as well as the new unit.

Evidence: RW:32; P1:97,113-115,125-131; D:674-725; R/core/resource_observation_classification.ads:79-114; R/core/resource_scoped_run_ledger.ads:232-268; R/core/worldline-resource_child_execution.ads:127-133,203-230.

Seam 6 — Committed outcome versus physical closure. Requirement: ACCURATE_BUT_NATIVE_USE_AND_SERIAL_CASES_INCOMPLETE. Direction: REQUIRES_CHANGES.

Separate canonical COMMITTED evidence from physical closure; retain write-once original result plus additive reports, authentic historical packets and follow-up outcomes. The canonical committed outcome must not be undone, but native QUARANTINE_USE already admits Effect_Observed and K4 currently requires Quarantined. I6.1 must not prohibit that original use-state recovery domain. Specify separate canonical, use, custody and resource states. I6.2's CLOSED-only wording also excludes original native NEVER_LAUNCHED held-capacity release; preserve that case and terminal replay on the serial path. Physical UNKNOWN retains holds without manufacturing an abort or settling on handler return/EOF.

Dependencies and authority: Scoped exchange/K4 successors, scoped committed envelope, full reconciler, child ordering and native phase relation. Serial exact-semantic controls and historical current-denial controls remain required.

Evidence: RW:33; P1:115,141-149; D:779-812; R/core/worldline-operation_authority.adb:129-130,147-152; R/runtime/worldline/protected_operations.py:391-397,770-811; R/runtime/worldline/protected_scoped_resource_runtime.py:517-524,558-565.

Seam 7 — Cost/source crosswalk. Requirement: ACCURATE_BUT_OB030_AND_RESOURCE_GUARANTEE_INCOMPLETE. Direction: REQUIRES_CHANGES.

Owner-selected crosswalks are legitimate selection inputs, not authority labels. Define a canonical comparable value and independently authenticated record for each pair: endpoint object versus pathname, full handler plan versus observed argv/exe, root RUNNING versus scoped RECORD_RUNNING are not inherently identical encodings. OB-030 requires distinct source tags or source-record hashing enforced by native Decide/Well_Formed and a copied-tag negative, not sourcing alone. Expected helper image and actual coordinator executable must retain their distinct meanings. Preserve full dynamic operation/owner/follow-up plans and D1/D2 cost correspondence. Ceilings at or below the reservation are insufficient for OB-176's real enforced capacity/availability guarantee; retain original minimum/low/weight accounting and host-pressure requirements. No static cost table may narrow original magnitudes or cases.

Dependencies and authority: Schema/provisioning, actual listener/source/process producers, native tagged-record grammar and ABI/caller re-review, native costs and host profile. Operator provisions authoritative plan selections.

Evidence: RW:34; P1:107,125-137; D:868-907; P1/OBLIGATIONS-v2.json:1043; P1/ALL-ORIGINAL-OBLIGATIONS.md:587,3507; R/core/worldline-resource_child_execution.ads:48-59.

Seam 8 — Requester PID-namespace join. Requirement: ACCURATE_BUT_JOIN_AUTHORITY_INCOMPLETE. Direction: REQUIRES_CHANGES.

Receive the full roster first and keep raw relative versus retained host credentials distinct. CrosswalkRequestPeer can be an additive exact type, but observation() returning the old document must be labeled retained and must not satisfy a fresh-kernel gate by renaming. fstat equality alone does not prove OFD identity, transport origin or the peer/request join. A digest hidden in opaque current_source does not make native code decide its semantics. Define explicit native correspondence inputs plus authenticated custody. Preserve UID/GID and preparer/same-UID-new-process domains. Neither missing a fresh pidfd after client exit nor a new live-process requirement may replace an originally accepted request; obtain/retain original kernel observations under custody and define unavailable evidence honestly. Historical settlement needs no socket/client.

Dependencies and authority: Seams 3,4,7,9, exact-type caller audit and OS-producer historical lineage. Actual relative PID/exited-peer behavior needs authorized lab observation.

Evidence: RW:35; P1:119,137,141-149; D:961-1009; R/runtime/worldline/client_peer.py:58-89,110-117; R/runtime/worldline/root_worker_custody.py:183-207.

Seam 9 — Closure/current ownership. Requirement: ACCURATE_BUT_PHASE_GRAPH_AND_RETENTION_INCOMPLETE. Direction: REQUIRES_CHANGES.

Native ownership transition legality is required, not optional, because it gates mutation. Replace the printed (CUSTODY_ACK|ABANDON)->WORKER_OWNED chain with exclusive branches: ABANDON never grants worker ownership. Define the transfer generation, per-request head, durable expected phase and actual pre-/post-commit observations under one CAS; protect the last capture through close/receive and resolve lost local or remote acknowledgments without a second mutation. Physical closure must remain collectible when handler/result records are absent. Keep EOF/deadline/missing cgroup as UNKNOWN, with no release/charge. Escrow reuse and cleanup-after-CLOSED are sound directions. Lossless content addressing needs an acyclic reconstruction scheme and a defined source snapshot closure; distinct full-state snapshots can still grow or recursively contain earlier captures, so deduplication alone is not an OOM remedy or storage/cost proof. Unknown canonical result must not erase an independently durable committed broker result.

Dependencies and authority: Startup one-shot schema/crash table, slot drains and inherited wait producers, request ownership, committed/historical states, requester correspondence, D1/D2 retention costs. Fault campaigns remain operator/lab work; actual power loss is not established by a simulation.

Evidence: RW:36; P1:113-115,147-149,163; D:1084-1147; R/runtime/worldline/root_worker_journal.py:123-143.

Seam 10 — Review/control/proof seal. Requirement: ACCURATE_BUT_SEAL_AND_CONTROL_CONSISTENCY_INCOMPLETE. Direction: REQUIRES_CHANGES.

Preserve original ordered proof/ordinary/lifetime rosters, floor, boundary, bodies/references/callers, zero unproved/justified/Assume and strict warnings. Use an appended reviewed pin override for protected_operations, preserving the original policy prefix. Pin semantics and exact full-source identity are separate: proof_manifest cannot carry its own exact content hash in CONTRACT_PINS without a hash cycle, and the existing normalizer is Ada-oriented even for Python/C. Bind manifest, controls, projects, headers, native helper and the dependency overlays through an external exact inventory/freeze. Do not broaden the Off boundary or treat C hardening/sanitizers as full-body proof. Add the native custody, delegation, tagged-source and crosswalk units to ordered enrollment. Resolve the frontier retirement contradiction with I10.3 and retain all required controls on their defined domains.

Dependencies and authority: All seams, explicit common composition, reviewed C-API successor, D1/D2, whole native/library closure, admitted successor frame and capacity gates. Source review grants no proof/runtime credit.

Evidence: RW:37,43; P1:153-165; P1/REQUIRED-LIFETIME-CONTROLS.json:2-24; D:1177-1203; R/runtime/worldline/proof_manifest.py:420-450,622-638,1012.

3. SL-0, SL-1 and the equivalence lemma

SL-0 is a sound, independently reviewable source-hygiene direction, conditional on a complete lock/call audit. Keep the selected Gate's threading.Lock unchanged. Public entry points acquire gate.mutex once; internal _locked variants carry explicit caller-held-lock discipline and preserve lock order, observation freshness, protected transition boundaries and original default branches. Audit service, capture, reconcile, submit, historical, owner and callback paths, not only syntactically nested with-statements. The design itself identifies cross-module reacquisition (D:88-91); direct AST nesting alone does not rule it out. Do not hold the critical section across an await or substitute an RLock to hide uncertain ownership. This review does not establish implemented deadlock freedom.

Consolidating attach_scoped_resource around the stricter original definition is sound: retain the exact producer path, early-selected DATA membership and already-attached refusal (R/runtime/worldline/protected_scoped_resource_runtime.py:52-58,961-964). Pin work at SL-0 should be a concrete append-only override/external-freeze plan, not a semantic waiver or a refresh that makes incomplete source eligible. Its exact changes still require different-author source review (D:1219; P1:153).

SL-1 is a suitable spec-only review unit after RC-01 below. Reference, Decide/Post, literal authority/binding/collapse clauses and complete scoped resource inputs preserve the intended architecture. A declaration-only lemma is an unproved obligation, not permission to use its postcondition as established evidence. No Ghost Import, Assume, exemption, hidden narrowed precondition or contract-suppression route is admissible. Ghost-only means no authorization-time flattening; checked-build Ghost evaluation still has native time/allocation/copy costs under D2 (P1:129-131; SPARK guide release 28.0w, ch09 and ch20).

The proposed theorem is not established by Single_Frame_Identity plus equal projection factors. Important differences remain:
- S.History_Valid/Retained_Origin add frame-head, origin-universe and epoch-interval relations (R/core/resource_scoped_run_ledger.ads:92-127) beyond L.Shape (:223-235 in resource_run_ledger.ads).
- S.Current_Valid adds current/history/physical/source relations (:215-231).
- S.Native_Valid requires a Facts roster, observation-head equality and Classify equality (:247-268); L.Native_Valid consumes no Facts and does not demand those joins (resource_run_ledger.ads:266-282).
- Physical bucket coverage, common physical key, all parent/child links and conservation need a precise mapping. A single scope frame does not by itself mean a single physical bucket.
- Projection_Valid requires zero remainder (:149-152); there is no accepted rounding lane to weaken or change.
- Optional identities/epochs must be compared by the original semantic predicates over the correct byte arena, not Ada record equality or equal absent values.

Thus an old resource tuple with an otherwise admissible native roster is unaffected by changing a separate scoped Facts field, while the scoped clause can change its decision. A structural single-frame/factor predicate alone cannot rule that out. This is static logical reasoning, not an executed counterexample or a numeric derivation.

An equivalence lemma is statable additively without editing either original Reference. Define an explicit total Ghost projection/embedding relation over typed packets, the complete coherent history/current/physical/classification witnesses, span/arena rebasing and an exact decision correspondence. Reuse Canonical_Operation.Decision as a subtype, or define a total bijection before comparing independently declared enumeration types (R/core/worldline-canonical_operation.ads:11-12,21-31). The original wrapper currently builds one shared arena (R/runtime/worldline/canonical_operation_kernel.py:30-39); preserve that or prove explicit separate-arena correspondence.

Prove both the decision-equivalence obligation on the stated structural/witness domain and coverage of all required original accepted and refusal cases. A theorem whose antecedent already asserts equal decisions/resource predicates proves nothing useful; a theorem about only convenient valid fixtures does not establish original-domain coverage. Do not fabricate missing current/Facts/history inputs at runtime to make the embedding apply. If it fails, retain the original references byte exact and revise the additive model; keep the full compatibility obligation OPEN (D:236-246,315; RW:28; P1:27-29).

D-1b cannot be settled by epoch equality alone: contexts contain policy, instance, unit, host and other identities, and the original scoped lifecycle relation permits retained originating scopes (R/core/resource_scoped_run_ledger.ads:353-391). Fresh new reservation must obey its native current-context requirement. A replay/rollover route needs a proved full origin/current/authority crosswalk, without silently removing the original retained lifecycle cases. Use L.Same_Context for semantic scope comparison. Historical settlement is a separate domain and must never be subjected to a fresh-peer/fresh-use requirement.

SL-1 drafting needs no root lab. Calling it independent of every other seam is too broad (D:1220,1234-1238): its definition depends on authority/collapse types and semantics, classifier Facts, arena/span conventions and complete original body/reference inputs, beyond the three files named there. Final wire/ABI adoption waits on the independently reviewed C-API successor; actual source legality and proof wait on admitted matching-source checks. The packet under review contains no actual SL-1 spec or proof.

4. Operator authority and paused infrastructure

The substantive privileged gates are accurate: selected StartupLease, Gate, front and worker entries require root; Gate constrains the actual root to /srv/cosmogony-canonical-v1.* (R/runtime/worldline/protected_startup.py:153; L/dependency-source/lab/intent_gate.py:157,172-175; R/protected-root/worker_entry.py:19-20; launcher.py:12-13). Source specifies User=root and delegation behavior in the manager unit (protected_root_resource.py:68-71). Namespace/mount feature claims remain source intent and unverified kernel reasoning, not evidence of available capabilities.

Require operator authority for actual lab creation/use, provisioning/migration or re-provisioning of authoritative custody/operation-head/crosswalk/descriptor state, privileged helper/delegation changes, real actor quota, invasive fault campaigns within the existing specialized-validation boundary, sudo, merge, tag/release, install, production services and real PRIME mutation. A changed custody schema must never be repaired by replacing lost prior state with a new genesis; any reviewed authorized migration keeps prior chain/history and has its own rollback/crash evidence (D:396-438,1147,1245-1269; P1:99,147-149,163,166).

Source drafting, schemas, pure value/spec design, pin plans and concrete operator packages are lead work. An additive versioned spec/export can be proposed without an operator choosing a weaker guarantee. Actual alteration of an original public API or owner policy needs its applicable explicit decision; Optional_Marker is specifically not approved and cannot be changed indirectly through this lane's dependencies (P1:121; START-CLAUDE.txt:10). Delegation policy installation and authoritative table selection are operator acts even if the helper/schema source is authored by the lead. No source-only reviewer may authorize a lower guarantee.

D:1247 and :1275 are accurate for the actual protected front/worker entry route, but should not imply that merely authoring or later running a separately admitted pure value fixture intrinsically requires root or a /srv installation. Such dispatch still waits on its own reviewed frame, ordinary admission and present capacity gates. Likewise seams.json OP-7's blocks=[publication and deployment] is too broad: the original prompt authorizes eventual reviewed commit/push/draft PR work; merge, tag/release and deployment remain operator-gated (PROMPT:72-74; P1:165-166). This session is passive only and authorizes none of those actions.

The lead STATUS is a read-only index, not a fresh capacity or operating-state measurement. It reports frame v5 unqualified, capacity blocked, no operator approvals, W-1 pending, C-API v3 and D1 v3 drafting, and D2 under analysis (LEAD/STATUS.md:3-24,38-46). The root-worker design correctly retains these blockers. No lab, store, socket, window, service or kernel state was inspected. No statement about a reusable paused window, healthy backup, available kernel feature or admissible future run follows from this review (RW:45; P1:177-181; D:1273-1291).

The dependency root and its selected overlays are explicit COSMOGONY lab dependencies (L/origin.json:2-7; RW:23; D:1278-1282). They need their own exact selection, source review, pin/freeze and accepted producer/caller correspondence; commonV4 and old finite component reviews supply no runtime authority. Keep the scoped committed-envelope A1 lineage distinct from the C-API consolidation successor despite the design's shared A1 shorthand (RW:13; D:293,814).

Repair the claimed dependency-ordered plan (D:1219-1231). SL-4b consumes transferred slots and historical outcomes, yet SL-7 and SL-6 appear later without being declared dependencies. SL-5's phase/peer protocol consumes descriptor, crosswalk and slot/request schemas; SL-9 consumes seam-7 accounting; final ABI adoption consumes the reviewed C-API successor. Define a source-spec DAG first, followed by caller/body composition and integration gates, rather than presenting mutually dependent implementations as independently complete. SL-0 and revised SL-1 drafting remain possible while runtime/proof gates are blocked.

The control-supersession clause is not a lead-only authority to drop an original mandatory control. Prefer exact v1 frontier behavior plus additive v2 positive/negative enrollment. If a concrete version/snapshot binding change is proposed, expose it for explicit applicable operator/adoption adjudication with independent GPT-6.1 review, original bytes retained, full requirement/control equivalence and no reduction of the target. Until resolved, the original control obligation stays OPEN (D:411-414,1196-1198; R/protected-startup/controls/test_protected_startup_v1.py:97-105; P1:29,153,162).

No approval question or operational action is needed for this verdict. No operator choice, frame qualification, storage repair or paused goal resume is granted.

5. Weakening and assumption audit; required changes and rulings

Verdict: ENDORSED_WITH_REQUIRED_CHANGES. The architecture directions can preserve the original requirement, but this packet cannot be implemented unchanged. The endorsement applies to revised design work only. It accepts no source, proof, native behavior, control campaign or Phase One outcome.

The explicit no-flattening, no-startup-initialization, no-EOF/handler-return settlement, no-domain-cap, no-failure-as-refusal and no-source-review-as-proof invariants are retained. The problems are concrete ways the proposed implementation could fail those invariants: a restrictive/vacuous refinement domain; source tags without native semantics or authenticity; a first-root budget restricting later requests; delegation inconsistent with the classifier; caller-only ownership authorization; ambiguous ACK/ABANDON branches; record identity mislabeled OFD custody; copied/retained credentials relabeled fresh; loss of native quarantine or never-launched release; frontier retirement; and self-referential/incomplete sealing.

Do not add an assumption to resolve any of these. Complete body/reference, caller, flow, RTE, termination, native semantic/cost, checked-Ghost, physical/custody and producer authenticity obligations stay required. Keep the original decision order, named cases, strict warnings, assertion behavior, proof floor and sole boundary. A C helper, a renamed predicate, a successful value fixture, a signed/MAC'd label, hash agreement or a documented OPEN gap does not establish acceptance (PROMPT:32-34,64-66; P1:27-29,119,129-131,153-164; RW:43).

Every original register ID is carried as OPEN in review.json, including later-roadmap/COSMOGONY rows and their original dependencies/owners. The observed register has 219 unique IDs from OB-001 through OB-219. This review closes none; proof_acceptance=false, phase_acceptance=false, source_acceptance=false.

Required changes:
RC-01: Define the scoped canonical spec, complete arena/span/decision mapping, structural embedding and non-circular coherent witness relation; prove original accepted/refusal coverage later. Correct the rounding claim and distinguish fresh reservation from retained rollover/lifecycle cases.
Reason: C2 adds history/current/Facts relations absent from the original flat Reference; single-frame identity factors alone do not establish equality or full-domain compatibility.
Evidence: D:217-246,285-288,315,1220,1234-1238; R/core/worldline-canonical_operation.adb:10-32; R/core/resource_run_ledger.ads:223-282; R/core/resource_scoped_run_ledger.ads:92-152,215-268,303-312.

RC-02: Specify canonical comparable source records and native enforcement of distinct authenticated source domains for every RootController pair; define full dynamic plan/cost and real enforced capacity correspondence.
Reason: Independent sourcing or a digest in an opaque field alone does not close OB-030. Comparing differently encoded records can make every positive fail; ceilings alone do not establish OB-176's reservation guarantee.
Evidence: D:868-907; P1/OBLIGATIONS-v2.json:1043; P1/ALL-ORIGINAL-OBLIGATIONS.md:587,3507; R/core/worldline-resource_child_execution.ads:48-59; P1:125-137.

RC-03: Replace the Delegate=yes-only proposal with a separately reviewed additive native delegation/custody model and actual enforcement/provenance design; preserve the old no-delegation model, Parent_Supports, Original_Holds and every original child case.
Reason: Native Custody still requires Manager_Delegate=no and is consumed by scoped classification. A Python HELD change cannot satisfy the unchanged native conjunction.
Evidence: D:674-725; R/core/resource_observation_classification.ads:79-114; R/core/resource_scoped_run_ledger.ads:232-268; R/core/worldline-resource_child_execution.ads:127-133,203-230; P1:97.

RC-04: Make native custody legality mandatory; define an exclusive CUSTODY_ACK/ABANDON graph, complete durable CAS generations and crash/ACK/seed/reconstruction rules, independent physical collection and lossless acyclic retention.
Reason: ABANDON must never transition to WORKER_OWNED. A head-conditioned append and a read-only capture alone do not establish ownership/freshness through mutation; deduplication alone is no OOM or cost proof.
Evidence: D:1084-1147,1180,1311; R/runtime/worldline/root_worker_journal.py:123-143; P1:101,113-115,147-149,163.

RC-05: Retain every original required control and roster, including the unchanged v1 frontier control on its exact version/domain; add v2 controls. Remove lead-only retirement authority and expose any concrete re-enrollment proposal for explicit applicable adjudication.
Reason: The proposed supersession contradicts I10.3 and the fixed no-dropped-controls requirement. Historical retention is not matching-candidate execution credit.
Evidence: D:411-414,1186-1198; R/protected-startup/controls/test_protected_startup_v1.py:97-105; P1:29,153,162; P1/REQUIRED-LIFETIME-CONTROLS.json:23.

RC-06: Leave in-coordinator option A unselected until a full-domain accounting design covers independent grants/owners/kinds/costs/rollovers and requests larger than the first root hold; specify actual owner/recovery authority in every phase and availability beyond router-lock changes.
Reason: Parent_Supports constrains kind and parent budget. The first request's hold can impose a new refusal domain; UNKNOWN has no known owner to forward to. Synchronous work can still stall other requests.
Evidence: D:562-626; R/core/resource_run_ledger.ads:247-262; R/runtime/worldline/protected_operations.py:728-745,391-397; RW:31; P1:113-115,127,141-149.

RC-07: Separate canonical committed outcome, native use quarantine, custody and physical resource states. Preserve native QUARANTINE_USE/K4 recovery and NEVER_LAUNCHED held-capacity release, terminal replay and serial semantics; keep write-once original result plus additive reports.
Reason: A committed exchange must remain committed, while the original kernel admits quarantine from Effect_Observed. CLOSED-only settlement wording excludes an original no-launch release case.
Evidence: D:779-812; R/core/worldline-operation_authority.adb:129-130,147-152; R/runtime/worldline/protected_operations.py:391-397,770-811; R/runtime/worldline/protected_scoped_resource_runtime.py:517-524,558-565; RW:33.

RC-08: Define full slot/drain transfer barriers, buffered/in-flight bytes, durable positions, acknowledgments, failure ownership, OFD/lock custody and genuine helper/outer-wait producer retention or relay.
Reason: A pipe byte offset and matching fstat identity do not prove lossless transfer or ownership; descriptor transfer alone does not confer reaping rights. Original other-LIVE positives must remain required.
Evidence: D:484-527,1102-1109; R/runtime/worldline/protected_root_observation.py:57-97,122-142; RW:30; P1:113-115,125-127.

RC-09: Define explicit native requester correspondence and authenticated socket/host-record custody. Label retained observations separately from fresh reads; preserve exited/delegated/same-UID-new-process and full UID/GID domains without a new live-client or fresh-pidfd acceptance precondition.
Reason: The crosswalk cannot acquire authority by returning old bytes under a new exact type, fstat equality, sender PID labels or an opaque digest. Kernel namespace/exited-peer behavior remains unmeasured.
Evidence: D:939-941,961-1009; R/runtime/worldline/client_peer.py:58-89,110-117; R/runtime/worldline/root_worker_custody.py:183-207; RW:35; P1:119,137,149.

RC-10: Use reviewed appended effective pin overrides plus an external exact inventory/freeze for the manifest itself and all source/control/project/header/helper/dependency files; enroll every new native semantic unit and retain the full original strict scope.
Reason: A self-content hash produces a seal cycle. Ada-oriented normalized pins do not replace exact Python/C identities. C hardening and source review do not establish full-body/native/cost proof.
Evidence: D:1177-1203; R/runtime/worldline/proof_manifest.py:420-450,622-638,1012; L/origin.json:2-7; P1:129-131,153-164.

RC-11: Repair the spec/body/integration dependency DAG; bind reviewed C-API and scoped committed-envelope lineages separately. Correct operator-item scope for protected runtime versus pure value work and draft publication; retain Optional_Marker and paused frame/capacity/storage gates.
Reason: The slice plan omits consumed slot/crosswalk/historical schemas and implementations. The live STATUS is not operating-state evidence; source-only review grants no authority to resume paused infrastructure.
Evidence: D:1219-1238,1245-1291; seams.json:operator_items OP-7/OP-8; LEAD/STATUS.md:8-24,38-46; P1:121,153-166,177-181; PROMPT:72-74; RW:13,45.

RC-12: Complete startup version/loader/schema/creation-slot correspondence and a native full-ledger reconciliation table that automatically completes authentic known outcomes, retains all uncertain holds and preserves the protected owner route without initializing absent prior state.
Reason: Blanket dead-worker quarantine-to-owner handling can lose required automatic reconciliation progress; diagnostic startup must not fabricate mutable authority or missing history.
Evidence: D:372-423,429-438; R/runtime/worldline/protected_startup.py:264-270,467-472; R/runtime/worldline/root_worker_journal.py:43-62,85-114; P1:99,147-149; P1/ALL-ORIGINAL-OBLIGATIONS.md:3687.

Rulings:
D-1a: C2 is a plausible lifted model, not an established faithful equivalence as written. Exact divisible projection replaces the draft's rounding description; require RC-01 with full-domain coverage and no changes to original references.
Owner: Lead source designer; independent GPT-6.1 source/spec reviewer.
Evidence required: Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls.

D-1b: Epoch equality alone is insufficient. Fresh new reservations obey native current-context equality; retained replay/rollover needs a complete proved origin/current/authority join and must preserve original lifecycle cases. Use Same_Context, not record equality.
Owner: Lead scoped model/caller designer; independent GPT-6.1 reviewer.
Evidence required: Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof.

D-2a: Prefer an additive exact v2 descriptor, selected by schema, with v1 behavior and controls retained. No implicit migration, defaults, bypass or missing-history genesis.
Owner: Lead authors schema/callers; operator provisions or installs authoritative state.
Evidence required: Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls.

D-2b: No lead-only retirement of the mandatory frontier control. Keep exact v1/domain behavior and additive v2 controls; any proposed re-enrollment must be explicitly adjudicated while the original obligation remains OPEN.
Owner: Lead prepares concrete equivalence/adoption package; applicable operator authority; independent GPT-6.1 review.
Evidence required: Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit.

D-3a: Transfer complete V3 slot custody; do not require prior terminal state as a domain restriction. The transfer protocol still needs RC-08.
Owner: Lead protocol designer; operator for lab execution.
Evidence required: Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection.

D-4a: No accounting option is selected for acceptance. A may be explored only if it preserves all original independent-request accepted cases and real cost/parent/availability guarantees; otherwise choose or design a faithful alternative.
Owner: Lead prepares native accounting comparison; independent GPT-6.1 review; operator selects any authoritative resource-policy change.
Evidence required: Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls.

D-5a: Delegate=yes is not endorsed as a complete native design. Require an additive native custody/delegation successor, unchanged original predicates/cases and a concrete coordinator enforcement argument before operator deployment choice.
Owner: Lead prepares native/OS design; independent GPT-6.1 review; operator for delegation and privileged lab action.
Evidence required: Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls.

D-5b: Prefer a separately versioned helper successor, preserving the exact V3/helper-stdin lineage and old controls. Extending V3 in place is not needed to obtain source design credit.
Owner: Lead helper designer; independent GPT-6.1 review; operator for privileged execution/installation.
Evidence required: Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations.

D-6a: Keep canonical COMMITTED immutable; permit the original native use-quarantine/K4 domain when needed for uncertainty. Define orthogonal outcome/use/resource/custody states rather than selecting a blanket ban on quarantine.
Owner: Lead historical/canonical model designer; independent GPT-6.1 review.
Evidence required: Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement.

D-7a: Independent sourcing alone does not close OB-030. Native Decide/Well_Formed must consume/enforce the distinct source-record domains or tags and canonical payload relation; use an additive grammar/version and preserve original references/ABI.
Owner: Lead native/provenance designer; child-authority and GPT-6.1 re-review; operator for any original API/owner-policy alteration.
Evidence required: Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation.

D-8a: Choose explicit native semantic correspondence inputs, carried by authentic producers. A producer-only label or digest in opaque current_source is insufficient.
Owner: Lead OS/native requester designer; independent GPT-6.1 review.
Evidence required: Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage.

D-8b: Do not add a blanket fresh-pidfd or still-live-client precondition. Retain original kernel socket/credential evidence under authenticated custody and define the exited-peer path; absent evidence remains explicit and unresolved where correspondence cannot be established.
Owner: Lead prepares domain-preserving protocol; operator for kernel measurement; independent GPT-6.1 review.
Evidence required: Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client.

D-9a: Yes: native custody-phase legality is mandatory because it determines who may mutate. Preserve exclusive ACK/ABANDON branches and authentic durable redecision under the actual CAS.
Owner: Lead additive SPARK relation and caller designer; independent GPT-6.1 review; operator for fault campaign.
Evidence required: Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes.
