# Root-worker runtime lane: seam design v2

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent, author role) |
| Date | 2026-10-04 (EDT); written 2026-10-05 UTC |
| Status | **DRAFT_FOR_GPT61_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author grants nothing, and no author check in this document is a review. Every original obligation (OB-001 … OB-219), accepted case, deterministic fixture, control, contract, threshold, proof floor and scope remains **OPEN** and unchanged. |
| Supersedes | v1 `SEAM-DESIGN.md` (sha256 `531d11282f811518b868470c0012f23a5e34bdbe3891ef39194cd8f230933f46`) and v1 `seams.json` (`b8fa87fb573596de9fa0a789b7a8c93c909eeeb18f4d192edad73e038a2caf5d`). Both were read only and re-hashed unchanged. |
| Answers | The sealed actual gpt-6.1-sol review of v1 in `…/claude-root-worker-seam-design-v1/review/gpt61-v1/`: `REVIEW.md` (`a1e54a5b…f496`, equal to its `report_sha256`), `review.json` (`721bce3a…0bd4`), `checks.json` (`b1834ee4…d498`), `review-freeze.json` (`f6f31ddc…1603`). The freeze lists the three reviewed files with hashes equal to those observed. Verdict **ENDORSED_WITH_REQUIRED_CHANGES**: required changes RC-01 … RC-12; rulings D-1a, D-1b, D-2a, D-2b, D-3a, D-4a, D-5a, D-5b, D-6a, D-7a, D-8a, D-8b, D-9a. Full hashes: Appendix B. |
| Scope | Design only, for the draft lane `W/work/protected-original-root-worker-repair-v1` (status `INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY`). It grants no execution, proof, build, test, review, operator or acceptance authority. |
| Location | `W/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v2/` |
| **What this document consists of** | v2 is (1) the text of this file, plus (2) the v1 `SEAM-DESIGN.md` line ranges listed in Appendix C as CARRIED_VERBATIM or CARRIED_WITH_LINE_REPLACEMENTS, each bound by the sha256 of its exact bytes, with the listed replacements applied. The carried slices are only: the v1 notation table, the P0 findings, and each seam's "Current draft state" and "Original requirement (quoted)" blocks. Every v1 design direction, invariant, decision, dependency, authority statement, control list, plan, operator list and concern is **REPLACED** by this file. No other v1 text is part of v2. |
| Companion files | `seams.json` (machine twin, same schema family as v1), `jackal.json` (every JACKAL call), `AUTHOR-NOTES.md` (unresolved items, uncertainties, reviewer guidance, process record). Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools. No Write or Edit was refused. Bash was used only for bounded read-only inspection (AUTHOR-NOTES §5). |

Every statement about source in this document is **static**: read from files, or derived by reasoning from what was read. Nothing was compiled, run, imported, proved, tested or measured. Kernel, systemd and Ada-visibility statements marked **[unverified reasoning]** are the author's reading and need the evidence named next to them.

---

## A. Closure table

"Answer" is a design statement for the reviewer. The author closes nothing. Every proof, native, control, physical and acceptance obligation stays OPEN.

### A.1 Required changes RC-01 … RC-12

Sub-requirements quote the sealed `review.json` `required_changes[].change`, split at its clauses.

| # | Sub-requirement (review text) | v2 answer | Where |
|---|---|---|---|
| 01.1 | "Define the scoped canonical spec" | Additive unit `Worldline.Scoped_Canonical_Operation`: typed `Reference`, `Decide` with `Post => Decide'Result = Reference (…)`, clauses C1–C4 in the original order. The decision type is `subtype Decision is Worldline.Canonical_Operation.Decision` (reuse, no new enumeration). | §3.1–§3.3, §3.11 |
| 01.2 | "complete arena/span/decision mapping" | Production keeps one shared arena, exactly as the original wrapper (`canonical_operation_kernel.py:30-36`). The Ghost correspondence uses an explicit total `Rebase` with two-way validity preservation, including malformed and boundary spans. The decision mapping is the identity, by type reuse. | §3.6 |
| 01.3 | "structural embedding" | Total Ghost `Emb (Orig, W)` from an original packet and a witness to a scoped packet, field by field. Runtime never builds it. | §3.7 |
| 01.4 | "non-circular coherent witness relation" | `Coherent (Orig, W)` is a list of field-level relations W1–W10. It mentions no decision, `Reference`, C2 predicate or scoped validity result. Its only classifier reference is the original producer's `K.Classify`, an input-generation relation that is not under comparison. | §3.8, §3.10 |
| 01.5 | "prove original accepted/refusal coverage later" | Lemma statements: L-EQ (decision equality on coherent witnesses), per-clause lemmas, the reachability invariant L-INV-1, producer coverage CV-B, fixture coverage CV-C, refusal preservation CV-D. Six known potential gaps G1–G6 stay OPEN until proved or until the scoped model is revised (never the original). | §3.9 |
| 01.6 | "Correct the rounding claim" | Withdrawn. `Projection_Valid` requires a zero remainder and exact quotient (`resource_scoped_run_ledger.ads:149-152`). The containment bound uses the exact quotient form at `:210-211`. No rounding lane exists. | §3.5 |
| 01.7 | "distinguish fresh reservation from retained rollover/lifecycle cases" | Three domains. FRESH (pre-effect and in-request exchange) needs native current-context `Same_Context`. RETAINED (rollover-separated K4 and recovery successors) needs a proved origin/current/authority join. HISTORICAL (settlement) needs no fresh peer, use or exchange. | §3.4 |
| 02.1 | "Specify canonical comparable source records" | A per-pair table of producer, raw record, extraction rule and canonical comparable encoding (CCE) for each of the six `Root_Controller` identity pairs and the process source-lease pair. | §4.1, §4.2 |
| 02.2 | "native enforcement of distinct authenticated source domains for every RootController pair" | Additive SPARK grammar `Worldline.Source_Record` and `Pair_Valid`. Native code requires distinct per-side domains, native payload extraction from the raw record, payload equality, and anchors to distinct authenticated containers. Additive `Root_Controller_V2` / `Controller_Valid_V2` / `Root_Admission_V2`. The originals are unchanged. | §4.1, §4.3 |
| 02.3 | "define full dynamic plan/cost … correspondence" | An owner-provisioned per-operation crosswalk covering every original operation, owner route and follow-up right, with dynamic event binding. Original plan identity and magnitudes are bound, never replaced. | §4.4 |
| 02.4 | "real enforced capacity correspondence" | Native `Enforcement_Corresponds` over observed manager and cgroup readbacks. It covers every original `ResourcePolicy` field and every original admission floor and ledger withholding, not ceilings alone. No new field and no new cap. | §4.5 |
| 03.1 | "Replace the Delegate=yes-only proposal with a separately reviewed additive native delegation/custody model" | Additive `Resource_Delegated_Custody`, `Classify_V2`, `Native_Valid_V2`/`Check_V2` and `Root_Controller_Holds_V2`, as separate review slice S4. | §5.2 |
| 03.2 | "actual enforcement/provenance design" | Coordinator enforcement properties P-CE1–P-CE4, each with its observation, native clause, lab measurement and negative control. Helper-mediated cgroup writes. A delegation record authenticated through the owner plan and crosswalk. | §5.3, §5.4 |
| 03.3 | "preserve the old no-delegation model, Parent_Supports, Original_Holds and every original child case" | The original `Custody` (`Manager_Delegate = "no"`), `Classify`, `Check` and `Parent_Supports` stay byte-exact and decide every row without a delegation record. `Original_Holds`, workload grammar, world facts, credentials and stdin/EOF are unchanged. | §5.2, §5.5 |
| 04.1 | "Make native custody legality mandatory" | Additive SPARK `Worldline.Root_Custody_Phase`. Every custody append is decided natively under the same SQLite write transaction, and Python obeys. | §6.1 |
| 04.2 | "exclusive CUSTODY_ACK/ABANDON graph" | Exclusive branches from TRANSFER_SENT. ABANDON never reaches WORKER_OWNED. Exactly one of the two commits per generation. | §6.2 |
| 04.3 | "complete durable CAS generations" | Per-operation generation, expected prior head and expected phase, checked inside `BEGIN IMMEDIATE`, plus a native decision and readback before commit. Request sub-generations. | §6.3 |
| 04.4 | "crash/ACK/seed/reconstruction rules" | Lost local or remote ACK resolved from the journal without a second mutation. Seed taken after the last append, with read-only capture paths. Reconstruction through the escrowed custody-lock OFD. Crash-point table. | §6.3–§6.5, §6.10 |
| 04.5 | "independent physical collection" | Three independent collector futures: handler terminal, CLOSED and outer wait, raw drains. Physical settlement does not wait for the handler terminal. | §6.8 |
| 04.6 | "lossless acyclic retention" | A content-addressed blob table holding raw observed bytes only. A defined snapshot closure that excludes the custody journal and the blob store. Change-only re-append. No OOM or cost claim. | §6.9 |
| 05.1 | "Retain every original required control and roster" | The 52-action ordinary roster, the lifetime controls, the inherited protected roster (RQC), the protected-startup controls and every lane control file are retained, run first, and replaced by none. | §17.1 |
| 05.2 | "including the unchanged v1 frontier control on its exact version/domain" | `test_current_source_frontier_names_full_ledger_startup_gap` is retained byte-exact. The v1 descriptor path keeps raising `PROTECTED_FULL_LEDGER_STARTUP_RECONCILER_UNAVAILABLE`. | §11.6 |
| 05.3 | "add v2 controls" | Additive `protected-root/required_controls_v2.json`, enumerated per seam. | §17.2 |
| 05.4 | "Remove lead-only retirement authority" | The v1 retirement text (v1 seam 2 item 6, I10.5) is withdrawn. | §11.6, §B.5 |
| 05.5 | "expose any concrete re-enrollment proposal for explicit applicable adjudication" | None is proposed in v2. The procedure, if one is ever proposed, is recorded, and the original obligation stays OPEN. | §11.6, §16 |
| 06.1 | "Leave in-coordinator option A unselected" | Unselected. No option is selected. | §9.2 |
| 06.2 | "until a full-domain accounting design covers independent grants/owners/kinds/costs/rollovers and requests larger than the first root hold" | Domain matrix AM-1…AM-9 with the original serial behaviour per cell. Options A, B, C and E are evaluated against it, each with its known gaps. | §9.1, §9.2 |
| 06.3 | "specify actual owner/recovery authority in every phase" | A phase × request-class routing table, including UNKNOWN and its protected recovery authority. The exact original `quarantine.resolve` exception is preserved, with no widening to other owner routes. | §9.3 |
| 06.4 | "availability beyond router-lock changes" | Protected synchronous sections run off the event loop with no await inside. A per-requester fair queue uses only original policy inputs. A durable queue without a depth cap. | §9.5 |
| 07.1 | "Separate canonical committed outcome, native use quarantine, custody and physical resource states" | Four orthogonal dimensions O/U/C/P, each with its own native relation, plus the coupling rules CD-1…CD-9. | §2 |
| 07.2 | "Preserve native QUARANTINE_USE/K4 recovery" | CD-2: native `Quarantine_Use` from `Reserved | Effect_Observed | Quarantined` (`worldline-operation_authority.adb:129-130`) and K4 resolution (`:156-167`) stay available. COMMITTED is never changed. | §2, §10.3 |
| 07.3 | "NEVER_LAUNCHED held-capacity release" | CD-5 keeps both native release cases of `resource_run_ledger.ads:317-320`. | §2, §10.2 |
| 07.4 | "terminal replay and serial semantics" | The serial path keeps its exact order (`protected_operations.py:778-811`), including the SETTLED replay at `:786-790`. | §10.2 |
| 07.5 | "keep write-once original result plus additive reports" | The first `RESULT_CAPTURE` is write-once. Later captures are additive `RESULT_REPORT` boundaries. The collector uses the retained capture. | §2 CD-8, §10.4 |
| 08.1 | "Define full slot/drain transfer barriers" | T1 FREEZE: stop the reader at a chunk or message boundary and drain the asyncio buffers. | §7.3 |
| 08.2 | "buffered/in-flight bytes" | T1/T2: buffered bytes are spooled durably before the descriptor moves. | §7.3 |
| 08.3 | "durable positions" | Spool position P is recorded in FREEZE and INTAKE. The spool hash chain continues from P. | §7.3 |
| 08.4 | "acknowledgments" | T4 INTAKE (CAS) and T5: the front closes its copy only after it reads the durable INTAKE. | §7.3 |
| 08.5 | "failure ownership" | A failure-ownership table for every T-step crash point. Never two readers. | §7.3 |
| 08.6 | "OFD/lock custody" | Kernel evidence that the received descriptor is the same open file description (kcmp, recorded by the front), plus lock-held evidence. fstat equality alone is not used as OFD proof. | §7.3 |
| 08.7 | "genuine helper/outer-wait producer retention or relay" | Retention. The helper, namespace init and systemd remain the reapers and waiters. Only observation and reader roles move. No reaping right is claimed. | §7.2 |
| 09.1 | "Define explicit native requester correspondence" | Additive SPARK `Worldline.Requester_Correspondence`, whose `Join` consumes explicit raw fields, not a digest in `current_source`. | §8.1 |
| 09.2 | "authenticated socket/host-record custody" | Journaled raw host records before the descriptor moves, a full-roster receive before any peer is built, and kcmp OFD evidence. | §8.2 |
| 09.3 | "Label retained observations separately from fresh reads" | New exact type `RetainedRequestObservation`. No fresh-read gate accepts it. Per-gate enumeration. | §8.3 |
| 09.4 | "preserve exited/delegated/same-UID-new-process and full UID/GID domains" | Domain list D8-1…D8-6. Full unsigned UID/GID, including 0 and the maximum. | §8.4 |
| 09.5 | "without a new live-client or fresh-pidfd acceptance precondition" | Pidfd evidence is optional and never required. FRESH needs only what the original needs, the retained socket. Unestablished correspondence stays explicit and unresolved, never replaced by a PID label. | §8.4 |
| 10.1 | "Use reviewed appended effective pin overrides" | Append-only `CONTRACT_PINS.update` statements after the last existing line. The stale `protected_operations.py` pin is superseded only by an appended, reviewed override computed on reviewed final source. | §12.1 |
| 10.2 | "plus an external exact inventory/freeze for the manifest itself and all source/control/project/header/helper/dependency files" | An external freeze record of exact sha256, bytes and mode for every file of the integrated candidate, including `proof_manifest.py`. It is held outside the sources and bound by the review freeze. There is no self-hash. | §12.2 |
| 10.3 | "enroll every new native semantic unit" | `REQUIRED_PROVED` and `DECLARED_CORE_ADA_SOURCES` appends for every new unit in §3–§8. No name inside `Worldline.C_API` (observation N-2). | §12.3, §12.4 |
| 10.4 | "retain the full original strict scope" | Floor 251, the S5 535-name ordered prefix, the sole `worldline-c_api` boundary, zero unproved, justified and `pragma Assume`, and strict warnings. | §1 G-5, §12.3 |
| 11.1 | "Repair the spec/body/integration dependency DAG" | Spec DAG S0–S11, body/caller nodes, integration gates and runtime gates, with the v1 plan's missing edges added. | §15 |
| 11.2 | "bind reviewed C-API and scoped committed-envelope lineages separately" | Distinct lineage nodes L-CAPI and L-A1. A third node, L-CAPI-P, is required by observation N-3. | §15.1 |
| 11.3 | "Correct operator-item scope for protected runtime versus pure value work and draft publication" | Pure value fixtures need no root or `/srv`. Draft commit, push and draft PR come under the original prompt after reviews. Only merge, tag, release, install, sudo, production and PRIME are operator-gated. | §16 |
| 11.4 | "retain Optional_Marker and paused frame/capacity/storage gates" | This lane changes no Optional_Marker API and routes no change through its dependencies (G-10). The frame, capacity and storage gates stay in force and uninspected. | §1, §14.3, §16 |
| 12.1 | "Complete startup version/loader/schema/creation-slot correspondence" | Union table U-1…U-12 over every constructor, loader entry, descriptor schema, early envelope and creation slot. | §11.1–§11.3 |
| 12.2 | "a native full-ledger reconciliation table that automatically completes authentic known outcomes" | Table RT-1…RT-16. Automatic rows are decided by the existing native relations. | §11.5 |
| 12.3 | "retains all uncertain holds" | RT rows with UNKNOWN or uncertain evidence retain holds and quarantine natively. | §11.5 |
| 12.4 | "preserves the protected owner route" | K4 and `quarantine.resolve` stay reachable for genuine uncertainty, with the exact original guard set. | §11.5, §9.3 |
| 12.5 | "without initializing absent prior state" | Diagnostic startup constructs no mutable owner. Absence refuses by name. One-shot provisioning is offline and operator-run. | §11.3, §11.4 |

### A.2 Rulings D-1a … D-9a

Owner and evidence text are quoted from the sealed `review.json` `rulings`. Each stays with its owner. v2 neither narrows nor adds to any of them.

| Ruling | Owner (review text) | Evidence required (review text) | How v2 applies it | Where |
|---|---|---|---|---|
| D-1a | Lead source designer; independent GPT-6.1 source/spec reviewer | Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls. | C2 is a lifted model whose faithfulness is an OPEN obligation stated as L-EQ plus coverage. The projection is exact. The original references are untouched. | §3 |
| D-1b | Lead scoped model/caller designer; independent GPT-6.1 reviewer | Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof. | FRESH uses `L.Same_Context (Row.Scope, S.Current)`, never record equality. RETAINED uses the `Retained_Join` obligation. HISTORICAL has no fresh peer or use. | §3.4 |
| D-2a | Lead authors schema/callers; operator provisions or installs authoritative state | Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls. | Additive exact `worldline.protected-startup-v2`, selected by exact schema. v1 is unchanged. No migration, default, bypass or missing-history genesis. Provisioning is operator-run. | §11 |
| D-2b | Lead prepares concrete equivalence/adoption package; applicable operator authority; independent GPT-6.1 review | Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit. | The frontier control is unchanged on v1, with additive v2 controls. No re-enrollment is proposed. The obligation stays OPEN. | §11.6 |
| D-3a | Lead protocol designer; operator for lab execution | Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection. | Complete V3 slot custody transfers, with no prior-terminal precondition. Protocol T1–T5. | §7 |
| D-4a | Lead prepares native accounting comparison; independent GPT-6.1 review; operator selects any authoritative resource-policy change | Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls. | No option selected. Matrix and option comparison are provided for review. | §9 |
| D-5a | Lead prepares native/OS design; independent GPT-6.1 review; operator for delegation and privileged lab action | Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls. | Additive native successor plus coordinator enforcement argument P-CE1–P-CE4, before any operator deployment choice. | §5.2, §5.3 |
| D-5b | Lead helper designer; independent GPT-6.1 review; operator for privileged execution/installation | Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations. | A separately versioned helper successor. V3 and the helper-stdin lineage and their controls are retained. | §5.4 |
| D-6a | Lead historical/canonical model designer; independent GPT-6.1 review | Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement. | Orthogonal O/U/C/P dimensions. COMMITTED is immutable. The native use-quarantine and K4 domain is permitted for genuine uncertainty. | §2, §10 |
| D-7a | Lead native/provenance designer; child-authority and GPT-6.1 re-review; operator for any original API/owner-policy alteration | Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation. | Native `Pair_Valid` over tagged records in an additive grammar version. No original API or owner policy is altered. | §4 |
| D-8a | Lead OS/native requester designer; independent GPT-6.1 review | Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage. | Explicit native correspondence inputs, carried by journaled producers. | §8.1–§8.3 |
| D-8b | Lead prepares domain-preserving protocol; operator for kernel measurement; independent GPT-6.1 review | Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client. | No blanket fresh-pidfd or live-client precondition. The exited-peer path is defined. Kernel measurement items K-1…K-5 go to the operator. | §8.4, §16 |
| D-9a | Lead additive SPARK relation and caller designer; independent GPT-6.1 review; operator for fault campaign | Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes. | Mandatory native phase relation under the actual CAS, with exclusive branches. | §6 |

### A.3 Statically observed draft defects and their required fixes

**Carried from v1 and the review.** All are static and none was executed.

| Id | Defect (static) | Evidence | Required fix in v2 | Where |
|---|---|---|---|---|
| DF-1 | The stale effective pin of `runtime/worldline/protected_operations.py` refuses every protected start. | Pin `8be1f9ab2c689ecc9e915464e8e454863c205ca2f1f4a1763a5125aa2b61139e`, recomputed `2a6d71c7ca81d456d41f242a880b8fa3e0f115d794f4772e115767236b183547` (review F-03). Refusals at `protected_startup.py:683-684` and `protected_root_worker.py:355-357`. | An appended, reviewed override computed on reviewed final source only. Never a refresh that makes incomplete source eligible. Plus the external exact freeze. | §12.1, §12.2 |
| DF-2 | Duplicate `attach_scoped_resource`. The later one (`protected_scoped_resource_runtime.py:961-964`) shadows the stricter one (`:52-58`) and drops `SCOPED_EXACT_EARLY_SELECTED_PRODUCER_REQUIRED`. Pre-existing. No caller. | F-05 | One definition, keeping the exact producer path, early-selected DATA membership and the already-attached refusal. Called only from v2 `construct()`. | §13.2, §11.7 |
| DF-3 | The root route omits three original pre-dispatch checks of `_invoke_serial`: the request-context check (`protected_operations.py:728`), the unresolved-use gate (`:730`), and the workload refusal (`:744-745`). It also drops the `DISPATCH_INTENT` boundary (`:749`). | F-06; `protected_root_worker.py:158-171` | Apply them in the original order and position: context and unresolved gate before `_reserve`, the workload refusal after `_reserve` with quarantine on exception, and `DISPATCH_INTENT` retained. | §13.3, §9.3 |
| DF-4 | Self-comparing `Root_Controller` identity pairs (`protected_root_observation.py:36-49`; the pairs are filled at `:43-49`). The process source lease comes from caller material (`:74-76`, `:121`). The named identity equalities are vacuous. Other `Controller_Valid` predicates are real (F-07). | F-07; `worldline-resource_child_execution.ads:48-59` | Tagged canonical comparable source records with native distinct-domain enforcement, in an additive V2 grammar. | §4 |
| DF-5 | The scoped historical settlement, lifecycle and owner-material adapters are undefined (`protected_scoped_resource_runtime.py:530-531`, `:548-549`, `:571-572`). | F-08 | Implement the three adapters on `CanonicalOperationPrincipal`, mirroring the originals over scoped committed history. | §10.5 |
| DF-6 | Conditional gate-mutex self-deadlock. `Gate.mutex` is a `threading.Lock` (`dependency-source/lab/intent_gate.py:371`). `intent_for_operation` holds it (`:385`) and calls `reconcile_context` (`:388`), which takes it again (`:357`). It is reached from `protected_operations.py:640`. Conditional on reaching it. Not reproduced. | F-02 | SL-0 lock discipline: one acquisition per public entry, `_locked` variants under an explicit holder marker, and a complete receiver-resolved audit including candidates N-6. The Gate is unchanged. No RLock substitution. No await inside a section. | §13.1 |

**New static observations by the v2 author.** They are for the reviewer to check. None is review and none was executed.

| Id | Observation (static) | Evidence (observed by read-only script or grep) | Consequence for the design | Where |
|---|---|---|---|---|
| N-1 | The lane's ordered `REQUIRED_PROVED` (614 names) and S5's (535) share an identical 419-name prefix and then diverge. 116 S5 names are absent from the lane, and 195 lane names are absent from S5 (J01, J02). The lane preimage has 485 names (419 + 66, J03). The draft adds 129 (J04). | AST literal evaluation of `proof_manifest.py` in the lane source, the lane preimage, S5 and commonV4. The common names keep identical order. | The integrated roster must keep S5's 535 names as the literal prefix and append lane names. The lane's own roster cannot serve as the integrated prefix. | §12.4 |
| N-2 | Eight `REQUIRED_PROVED` names (lane positions 606–613, J14) designate subprograms inside the `SPARK_Mode => Off` body of `Worldline.C_API`: `Child_Version`, `Child_Layout`, `Child_Decide` and `Child_Boundary.{Version,Shape,Array_Shape,Layout,Decide}`. `Child_Boundary` (draft `core/worldline-c_api.adb:1166-2251`) has no SPARK_Mode aspect. | SPARK UG release 28.0w ch04: "A non-SPARK subprogram body cannot enclose a separately analyzed SPARK region simply by adding a nested annotation." The required-proved check is at `proof_manifest.py:857`. The block came through the child-authority secondary union. Its sealed review records prefix, floor and boundary-set invariants (`REVIEW.md:15-17`) and does not discuss this point. | **[static reasoning, not executed]** These names cannot be proved under the unchanged boundary. The obligation they express must be carried by On units, with transport-only code in `C_API`. | §12.3, §14.3 |
| N-3 | 41 core files in the lane are `SPARK_Mode => Off` (J06). Two are `worldline-c_api.ad[sb]` (Off in both). 30 are the 15 C-API units, **On in S5 and Off in the lane**. 9 are protected-lineage C API files, **absent from S5 and Off in the lane**: `worldline-{actuation_full,canonical_exchange,canonical_operation,canonical_owner_completion,operation_authority}_c_api.*`. | grep over `core/*.ad[sb]` in the lane source and S5 | Composing lane files as-is would restore Off exemptions outside the sole boundary (P1:29 forbids that). Required: S5's On versions of the 15 units, plus a new consolidation successor L-CAPI-P for the 9 protected files. | §14.3, §15.1 |
| N-4 | Layout collision with C-API v4. The draft is the lane preimage C_API plus 6 inserted `with` lines and 1119 inserted lines (J07, J08) between `end Owner_Audit_Decide;` (draft `:1165`) and the final `end` (`:2285`). Its spec appends 32 lines (J15) after `wl_owner_audit_decide_v1`. S5 is the preimage plus one 53-byte line at `:32` (J09). v4's R-LAYOUT places the export runs at exactly those two positions. `External_Name` occurrences: 31 in S5 and 34 in the draft (J10). | difflib opcode summary; anchor lines; occurrence counts | A reviewed rebase is required. The tables are never edited to fit. | §14.1, §14.2 |
| N-5 | The draft renamings `Y J D A X E T N W O Q` (draft `:1199-1220`) are declared in the body of the nested package `Child_Boundary` (`package body Child_Boundary is` at `:1198`; end at `:2251`). Their scope is that body, not the whole C_API body. | Read at the cited lines. A heuristic scope scan agrees. | This refines the wording of C-API v4 §19 ("at C_API body level"). The hazard remains for any rebase that merges texts into one scope. | §14.2 |
| N-6 | A name-based AST scan finds further nested `gate.mutex` acquisition candidates beyond P0-1. Examples: `settle_bound`/`settle_historical`/`resolve_historical`/`reconcile`/`machine_admission`/`launch_reserved` calling `reconcile_context` or `submit_bound` while holding the lock. `RootControllerCapture._current` calls `capture_execution` (`canonical_actor_execution.py:61`). | Scan output (AUTHOR-NOTES §3). Receivers are not resolved, so some candidates are false positives. The original `settle_bound` has no caller (grep). | SL-0 must resolve each candidate by receiver type and thread. The scan is a lower bound, not completeness. | §13.1 |
| N-7 | `RootCustodyJournal.append` is serialized by `BEGIN IMMEDIATE` but is not conditioned on a caller-supplied expected head or phase (`root_worker_journal.py:123-140`). | Read | This is why native CAS generations are needed. | §6.3 |
| N-8 | `capture_execution` appends an operation-journal `ACK` boundary inside the capture path (`canonical_actor_execution.py:125-127`). It is called by `RootControllerCapture._current` (`protected_root_observation.py:61`). | Read | This is the cause of the stale seed, defect 9(a). | §6.4 |
| N-9 | The draft block declares enumeration literals named `Size`, for example `type W_Raw_Id_Field is (Size, Alignment, …)` at draft `:1289`, and uses them in `when Size =>` choices. That is 84 whole-word occurrences not preceded by an apostrophe, besides 67 `'Size` attribute uses. C-API v4 adds a spec-level `subtype Size is Interfaces.C.size_t;`. | Script count (observed) | **[unverified reasoning, author's reading of RM 8.3/8.4]** The inner literals would hide the outer subtype inside `Child_Boundary`'s body. v2 does not rely on that and requires renaming. | §14.3 |

### A.4 The other lead requirements

| Requirement in the drafting brief | Where |
|---|---|
| Design the shared `core/worldline-c_api.adb` integration with C-API DESIGN v4 (rename-capture hazards, transport names, ordering) as a design obligation with its own checks | §14 |
| Carry forward everything the v1 review verified or accepted, with every statically observed draft defect and its fix | §B, §A.3 |
| Make v2 self-contained, or bind v1 slices | Header, Appendix C |
| Reserved operator decisions only, with no invented gates | §1 G-7, §16 |

---

## B. Carried forward

### B.1 The review's fact checks

The status column quotes `review.json` `fact_checks[].status`.

| Id | Claim | Review status | v2 disposition |
|---|---|---|---|
| F-01 | Supplied design and decisions hashes | VERIFIED_BYTE_IDENTITY | Carried. Re-hashed while drafting v2, unchanged. |
| F-02 | Non-reentrant Gate mutex reacquired by scoped `intent_for_operation` | SUPPORTED_STATIC_CONDITIONAL | Carried as **conditional** (DF-6). The v1 sentence "Every scoped reservation would therefore block forever" is replaced (Appendix C, R-1). |
| F-03 | Stale `protected_operations` pin; preimage 171 / source 191 effective pins; exactly one mismatch | VERIFIED_STATIC_RECOMPUTATION | Carried (DF-1). The v2 author's AST count also observes 171 and 191 effective pin keys. |
| F-04 | Delta pin coverage and whole source inventory | VERIFIED_STATIC_RECOMPUTATION | Carried: 736 files; 60 source delta entries, 24 pin-covered and 36 not (the review's figures and its JACKAL results). This counts changed source paths, not every lane file. |
| F-05 | Duplicate `attach_scoped_resource`; lost exact selected-producer check | VERIFIED_STATIC | Carried (DF-2). Pre-existing in the preimage; no caller. |
| F-06 | Root route omits three pre-dispatch checks | VERIFIED_STATIC | Carried (DF-3). |
| F-07 | `RootController` expected identity pairs self-compare | VERIFIED_STATIC | Carried with the review's correction: only the named identity equalities are vacuous (Appendix C, R-3). |
| F-08 | Undefined scoped historical adapters | VERIFIED_STATIC_ABSENCE_IN_SELECTED_TREES | Carried (DF-5). |
| F-09 | `SO_PEERCRED` namespace join | SOURCE_ORDER_VERIFIED_KERNEL_CONCLUSION_REASONING_ONLY | Carried as **conditional**: for an outside-namespace original client whose re-read PID differs, `RequestPeer` raises `PEER_REQUEST_MISMATCH` (Appendix C, R-4). Kernel behaviour unmeasured. |
| F-10 | Lane lineage is actor-stdin V4, not commonV4; `worldline-c_api` collision | VERIFIED_BYTE_IDENTITY_AND_COMPOSITION_DEPENDENCY | Carried and extended by N-1, N-3, N-4 and N-5 (§14). |
| F-11 | C2 involves projection rounding | CORRECTED | Applied: §3.5. |
| F-12 | Changing the HELD delegation expectation closes Delegate=yes nesting | DESIGN_CONFLICT | Applied: §5 (additive native successor). |
| F-13 | Committed effect must never enter native use quarantine; settlement always needs CLOSED | DESIGN_CONFLICT_WITH_ORIGINAL_CASES | Applied: §2, §10. |
| F-14 | Frontier control may be retired by review and lead adoption | INTERNAL_DESIGN_CONFLICT | Applied: §11.6. Retirement text withdrawn. |

### B.2 Directions the review accepted, carried unchanged in substance

| Seam | Accepted direction (review §2 or §3, condensed) | v2 location |
|---|---|---|
| 1 | C1/C3/C4 preserve the intended clauses. Original single-frame models stay byte-exact. No runtime flattening. | §3 |
| 2 | Exact v2 dispatch and one-shot offline provisioning are sound directions. Reconcile authentic durable work automatically where native evidence permits. Retain genuine owner resolution when uncertainty remains. | §11 |
| 3 | Transferring the complete roster preserves the original domain. Requiring other actors to terminate first would remove accepted cases. All non-terminal rows retain origin, and UNKNOWN keeps its holds. | §7 |
| 4 | Fresh per-request admission and durable exactly-once routing are sound directions. | §9 |
| 5 | Full original workload capture, a distinct task hold, the same original use and physical ancestry are preserved in intent. Helper source can be drafted. | §5 |
| 6 | Separate canonical COMMITTED evidence from physical closure. Retain the write-once original result plus additive reports, authentic historical packets and follow-up outcomes. | §2, §10 |
| 7 | Owner-selected crosswalks are legitimate selection inputs, not authority labels. | §4 |
| 8 | Receive the full roster first. Keep raw relative and retained host credentials distinct. `CrosswalkRequestPeer` can be an additive exact type. Historical settlement needs no socket or client. | §8 |
| 9 | Escrow reuse and cleanup after CLOSED are sound directions. EOF, deadline and missing cgroup stay UNKNOWN, with no release or charge. | §6 |
| 10 | Preserve the original ordered proof, ordinary and lifetime rosters, floor, boundary, bodies, references and callers, with zero unproved, justified and Assume and strict warnings. Use an appended reviewed pin override. | §12 |
| SL-0 | A sound, independently reviewable source-hygiene direction, conditional on a complete lock/call audit. Keep the Gate's `threading.Lock` unchanged. Consolidate `attach_scoped_resource` around the stricter definition. | §13 |
| SL-1 | A suitable spec-only review unit once RC-01 is applied. A declaration-only lemma is an unproved obligation. No Ghost Import, Assume, exemption, hidden narrowed precondition or contract suppression. | §3, §15 |

### B.3 Authority statements the review accepted

These are carried unchanged:
- The substantive privileged gates are accurate. `StartupLease`, the Gate, the front and the worker entries require root. The Gate constrains the root to `/srv/cosmogony-canonical-v1.*`. The manager unit specifies `User=root`.
- Operator authority is needed for:
  - actual lab creation or use;
  - provisioning, migration or re-provisioning of authoritative custody, operation-head, crosswalk or descriptor state;
  - privileged helper and delegation changes;
  - real actor quota;
  - invasive fault campaigns within the existing specialized-validation boundary;
  - sudo, merge, tag/release, install, production services and real PRIME mutation.
- A changed custody schema is never repaired by replacing lost prior state with a new genesis. Any reviewed authorized migration keeps prior chain and history and has its own rollback and crash evidence.
- Lead work: source drafting, schemas, pure value and spec design, pin plans and concrete operator packages.
- Altering an original public API or owner policy needs its applicable explicit decision.
- Delegation policy installation and authoritative table selection are operator acts, even when the lead authors the source.

### B.4 Invariants the review retained

These invariants are retained. The review identified concrete ways the v1 implementation could fail them, and v2 addresses those ways:
- no flattening;
- no startup initialization;
- no settlement on EOF or handler return;
- no domain cap;
- no failure counted as refusal;
- no source review counted as proof.

### B.5 v1 statements withdrawn or replaced

| v1 text (location) | Why | Replacement |
|---|---|---|
| D-1a "projected-charge rounding" (v1:285-286) | F-11 | §3.5 exact projection |
| "Rows(I).Scope equals State.Current" as record equality (v1:232) | D-1b: use `Same_Context` | §3.3 C2, §3.4 |
| `Scoped_Refines_Original` with antecedent `Single_Frame_Identity` alone (v1:236-246) | RC-01: not a faithful equivalence | §3.7–§3.9 |
| Seam 2 item 3.4: dead daemon's WORKER_OWNED become durable QUARANTINED (v1:392-393) | RC-12: loses automatic progress | §11.5 |
| Seam 2 item 6 and I10.5: frontier retirement by review and lead adoption (v1:411-414, 1198) | F-14, D-2b | §11.6 |
| Seam 3 item 3: a `DRAIN_TRANSFER` byte offset as lossless transfer (v1:494-495); I3.2 "re-identified descriptors (dev/ino/fdinfo)" as custody (v1:503-504) | RC-08 | §7.3 |
| Seam 4 recommendation of option (A) (v1:587-589) | RC-06, D-4a | §9.2 |
| Seam 4 item 6: owner routes forwarded in every phase (v1:596-597) | Widens owner routes; review §2 seam 4 | §9.3 |
| Seam 5 item 2.4: "The HELD delegation check becomes an exact expected state" as a design (v1:676-682) | F-12, D-5a | §5 |
| I6.1 blanket "never demoted to QUARANTINED" and I6.2 "only from … CLOSED" (v1:802-804) | F-13, D-6a | §2, §10 |
| Seam 7 item 4 and I7.4: distinct tags alone (v1:885-894, 903) | D-7a | §4 |
| Seam 8 item 6: crosswalk digest into `current_source` (v1:995-996) | D-8a | §8.1 |
| Seam 8 item 3: host-PID evidence "must equal the original PID" as an acceptance precondition (v1:983-984) | D-8b | §8.4 |
| Seam 9 item 1: `(CUSTODY_ACK | ABANDON) → WORKER_OWNED` (v1:1087-1090) | RC-04 | §6.2 |
| I9.7 deduplication as an unbounded-growth remedy (v1:1112-1113, 1128) | RC-04 | §6.9 |
| §3: "SL-1 … needs no lab, root, operator or other seam" and its single-file check basis (v1:1234-1238) | Review §3: too broad | §15.2 |
| OP-7 "blocks publication and deployment" (seams.json) | RC-11 | §16 |
| "A1" shorthand for both the C-API successor and the scoped committed envelope (v1:140, 293, 814) | RC-11 | §15.1 |

### B.6 Reading rules for carried v1 slices

- **RR1.** Inside carried slices, v1's notation applies: `R/`, `rw/`, `RW:n`, `P1:n`, `PROMPT:n`, `ROADMAP:n`, `OB-nnn`, `GATE` (slice B-NOTATION).
- **RR2.** Inside carried slices, the bare notation `RC` means the inherited roster `R/protected-canonical/required_controls.json`. This document calls that roster **RQC**, so it cannot be confused with the required changes RC-01 … RC-12.
- **RR3.** Where a carried slice says "A1", read L-CAPI (the C-API consolidation successor) or L-A1 (the scoped committed envelope) as §15.1 assigns. The replaced line R-2 in Appendix C makes this explicit for P0-6.
- **RR4.** Numbers in carried slices keep the status v1 gave them, observed or JACKAL exact. They are not re-derived here.
- **RR5.** Carried "Current draft state" text describes the draft. It is not v2 design.

---

## C. Truth boundary, bases and method

### C.1 What was done

- Static reading only.
- Bash was used for bounded read-only inspection: `cat`, `sed -n`, `grep`, `find`, `ls`, `sha256sum`, `wc`, `head`, `awk` (printing only), and short Python scripts that read files as text, JSON or `ast` and printed to standard output. Python's `difflib` was used for text-line comparisons.
- No output was redirected or teed to any file. No file was created, moved, copied, deleted or changed by Bash or Python.
- Not run: no compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. No `/srv` lab, store, socket or window was touched.
- SIA was used read-only (`sia.search`, `sia.recall`). No SIA note was written. Recalled notes are model-origin recall, not evidence.
- Skills loaded: `ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`, `worldline`, `cosmogony`.
  - SPARK User's Guide release 28.0w was read at ch04 (identifying SPARK code), ch09 (specification and Ghost features), ch14 (concurrency), ch20 (writing contracts) and ch22 (package contracts).
  - ada-high-integrity was read at ch07 (dynamic features: exceptions and Ravenscar).
  - advanced-ada was read at ch14 (packages and visibility).
  - Guide statements are documentation of the 28.0w development release, not evidence about the installed 16.1.0 toolchain.

### C.2 Bases (aliases)

| Alias | Path |
|---|---|
| `W` | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` |
| `WT` | `W/work/claude-lead-isolation-v1/wt-1` |
| `L` | `W/work/protected-original-root-worker-repair-v1` (the draft lane) |
| `R` | `L/source` (unprefixed `core/…`, `runtime/…`, `protected-*/…` paths in §1–§17 are relative to `R` unless stated otherwise) |
| `rw/` | `R/runtime/worldline/` |
| `RW:n` | `L/handoff-to-claude-v1-retry1/HANDOFF.md`, line n |
| `P1:n` | `W/outputs/claude-phase1-handoff-20261004/HANDOFF.md`, line n |
| `PROMPT:n` | `/home/sicarii/Documents/complete-phase1-prompt.txt`, line n |
| `S5` | `W/work/claude-composition-v5-beta/source` (QUALIFIED_SOURCE_COMPOSITION; proof, source and phase acceptance false) |
| `S4` | `W/work/reviewed-common-proof-source-composition-v4/source` (commonV4) |
| `D1V` | `WT/designs/claude-root-worker-seam-design-v1` (v1 design and its sealed review) |
| `CAPI4` | `WT/designs/claude-capi-boundary-design-v4` (DRAFT_FOR_GPT61_REVIEW; its review directory existed and was empty when inspected) |
| `CAPI3R` | `WT/designs/claude-capi-boundary-design-v3/review/gpt61-v1` (sealed) |
| `D2R` | `WT/designs/claude-d2-checked-ghost-inventory-v1/review/gpt61-v1` (sealed, ACCURATE_WITH_CORRECTIONS) |
| `CHILD` | `W/work/resource-child-authority-source-v1` (finite actual GPT-6.1 source review) |
| `A1` | `W/work/scoped-committed-envelope-repair-v2-retry1` |
| `RQC` | `R/protected-canonical/required_controls.json` (status `SOURCE_ONLY_UNRUN_UNADMITTED`) |

### C.3 Status labels used in this document

| Label | Meaning |
|---|---|
| OBSERVED | Read from a file or printed by a read-only command. |
| STATIC_REASONING | The author's inference from read source. Not executed. |
| [unverified reasoning] | Kernel, systemd or language-rule semantics as the author reads them. Each names its needed evidence: a lab measurement, or the installed-compiler check D-38 of CAPI4. |
| DESIGN | A proposal for review. |
| OPEN | An obligation not discharged. |

### C.4 Numbers

- Observed counts are tool outputs.
- Every derived number is one of the JACKAL `jackal_exact` calls J01–J15 recorded in `jackal.json`. Each returned `status=exact`, `formal=false`, lane `rat`, evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, with these non_claims, verbatim:
  - "NOT formal-bounded: this lane carries no Lean-checked certificate"
  - "The epistemic class above is the STRONGEST claim this result supports"
  - "exact rational arithmetic (not yet checker-covered)"
- The results are informational about arithmetic only. They establish no source, proof, ABI or acceptance property.
- Numbers quoted from the review, from v1 or from CAPI4 keep their own stated status.

---

## 1. Global invariants and preservation rules

These bind every section. Each is a requirement on the design and on any later source, never a claim that source satisfies it.

- **G-1. Original units are byte-exact.** v2 adds units and additive versions only. It does not edit:
  - `Worldline.Canonical_Operation`, `Worldline.Operation_Authority`, `Worldline.Canonical_Exchange` or the owner-completion units;
  - `Resource_Run_Ledger`, `Resource_Scoped_Run_Ledger`, `Resource_Observation_Classification`;
  - `Worldline.Resource_Actor_Admission`, `Worldline.Resource_Actor_Execution`, `Worldline.Resource_Child_Execution`;
  - their wire units.

  The scoped, classification, actor and child units reached the lane through the child-authority secondary union (finite GPT-6.1 source review in `CHILD`). For this lane they are base text, and their successors are additive.
- **G-2. No narrowing.** There is no domain cap, no narrowed precondition and no new refusal of an accepted case. The following interim named refusals are retained only because their original positives are still required. Each keeps its obligation OPEN and none counts as acceptance:
  - `OPERATION_ORIGINAL_WORKLOAD_RESOURCE_ROUTE_UNINTEGRATED` (`rw/protected_operations.py:744-745`), until §5 is accepted;
  - `OWNER_ORIGINAL_FULL_RESOURCE_ATTEMPT_ROUTE_UNINTEGRATED` (`:735-737`);
  - `PROTECTED_FULL_LEDGER_STARTUP_RECONCILER_UNAVAILABLE` on v1 descriptors (`rw/protected_startup.py:467-472`), the frontier (§11.6);
  - `ROOT_CAPTURE_OTHER_LIVE_OWNED_DESCRIPTOR_ROSTER_UNAVAILABLE` (`rw/protected_root_observation.py:126-127`), until §7;
  - `ROOT_RESOURCE_OWNER_OPERATION_COST_CROSSWALK_UNAVAILABLE` (`rw/protected_root_resource.py:40-41`), until §4.4;
  - `OPERATION_SCOPED_FOLLOWUP_DISPATCH_UNAVAILABLE` (`rw/canonical_followup.py:95`), until §5 and §10.
- **G-3. A resource failure is never a refusal or a settlement.** This covers `Storage_Error`, an OOM kill, stack exhaustion, process death, a deadline or timeout, EOF, a missing cgroup, a handler return, and a catch-all-mapped native failure code. Each becomes UNKNOWN with every hold retained, through native `Retain_Uncertain` or `Quarantine_Use`. It is never an accepted semantic refusal (D2R hazard ruling H10), never a release or charge, and never a PASS.
- **G-4. No assumptions or exemptions.** No `pragma Assume`, no justification annotation, no Ghost `Import` or imported axiom, no warning waiver, no suppression of checked assertions, and no `SPARK_Mode => Off` outside `worldline-c_api`. That includes not restoring the Off units of observation N-3.
- **G-5. Proof scope is fixed.** It consists of:
  - `MINIMUM_CHECKS = 251` (`rw/proof_manifest.py:22`);
  - S5's 535-name ordered `REQUIRED_PROVED` prefix, literal and append-only;
  - `UNANALYZED_BOUNDARY == {"worldline-c_api"}` (`:316`);
  - the exact strict command (P1:158);
  - zero unproved, justified and `pragma Assume`, with complete reports;
  - every strict warning resolved;
  - every body, reference, caller, flow, RTE, termination, native semantic and native cost obligation.
- **G-6. Controls.** Every original control and roster is retained and run on the exact integrated candidate. Additive controls replace none, with no skips, mocks or fallbacks (RQC `no_skips_mocks_or_fallbacks: true`; §17).
- **G-7. Reserved operator decisions, and only these:**
  - authoritative state provisioning or installation (D-2a);
  - frontier re-enrollment adjudication (D-2b);
  - authoritative resource-policy change (D-4a);
  - delegation and privileged lab action or installation (D-5a, D-5b);
  - original API or owner-policy alteration (D-7a);
  - kernel measurement (D-8b);
  - fault campaigns (D-9a);
  - merge, tag/release, install, sudo, production services and real PRIME.

  No other approval gate is added. A review brief or finding is not new authority to add one.
- **G-8. No flattening.** No runtime projection of scoped state into an older `RunState`, and no copied readiness flag. Embeddings are Ghost-only. Scoped inputs come only from the scoped producer.
- **G-9. One authority.** Python has no independent definition of authorization. Every consequential condition is decided natively, and callers carry complete inputs and obey the decision (P1:27).
- **G-10. Optional_Marker is untouched.**
  - The lane's 63-entry delta touches no `core/worldline-recovery*` file (observed, binary-delta roster).
  - Composition takes S5's `core/worldline-recovery.ads` (sha256 `09f82299afc975b409596fb342f1ef961e309354765cde966189f23a2ee3fe`), never the lane's copy (`ab9555faadd4b46d294a09d8d74495b75ef017497acde9290849cf005aed921a`). CAPI3 §0 describes S5's copy as carrying packet 01's change under the lead-recorded approval `W/work/claude-lead-v2/approvals/optional-marker-api-v1/approval.json`. That was not re-verified here.
  - This lane alters no Optional_Marker API and needs none altered. The review's statement that Optional_Marker is not approved and the later approval record are both outside this lane to reconcile (AUTHOR-NOTES §2).
- **G-11. Lock discipline.** Locks follow §13.1 (SL-0).
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace and socket semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-12, §16).
- **G-13. Lab is not production.** Nothing here touches production, PRIME, installed services or `/srv`.

---

## 2. Orthogonal state model (RC-07, D-6a)

This model is the foundation that §6, §9, §10 and §11 use. Each operation has four state dimensions. Each dimension has **its own native relation**, and the couplings between dimensions are explicit rules. No dimension's transition is inferred from another's label.

### 2.1 Dimensions

| Dim | Name | Values | Native relation deciding transitions | Source anchors |
|---|---|---|---|---|
| O | Canonical outcome | `NO_EXCHANGE` (the operation has no exchange), `UNDECIDED`, `COMMITTED`, `ABORTED`, `UNKNOWN` | The canonical exchange relation and its broker records (scoped successor of `Worldline.Canonical_Exchange`, §3.4) | `rw/canonical_full_broker.py:117-140`; `rw/controller.py:680-699` |
| U | Native capability use | `Reserved`, `Effect_Observed`, `Settled`, `Released`, `Quarantined` (`A.Use_State`), journaled as `RESERVED`, `EFFECT_INTENT`, `EFFECT_OBSERVED`, `SETTLED`, `RELEASED`, `QUARANTINED`, `RESOLVED_EFFECT`, `RESOLVED_NO_EFFECT` | `Worldline.Operation_Authority.Decide` (unchanged) | `core/worldline-operation_authority.ads:109`; `.adb:111-173`; `rw/protected_operations.py:599-601` |
| C | Custody phase | §6.2 graph (FRONT_OWNED … WORKER_OWNED … CLOSED_WITNESS … plus `UNKNOWN(cause)`). The serial path has no custody dimension. | New `Worldline.Root_Custody_Phase` (§6) | `rw/root_worker_journal.py:21-23` |
| P | Physical resource | Row phase `Reserved`, `Launch_Intent`, `Running`, `Terminating`, `Terminal`, `Settlement_Unknown`, `Released`, `Charged`, plus observed liveness `Unknown`, `Live`, `Reaped`, `Never_Launched` | Scoped `Check`/`Classify` (unchanged), and the additive `Check_V2`/`Classify_V2` for delegated rows (§5) | `core/resource_run_ledger.ads:37-38,56`; `core/resource_scoped_run_ledger.ads:232-246,443-457` |

The exact mapping from O's values to the broker's and transaction store's record states is an SL-6 specification deliverable (OPEN). O is recorded once per exchange-bearing operation. Operations without an exchange keep `NO_EXCHANGE`, and their effect is tracked in U.

### 2.2 Coupling rules

- **CD-1.** `COMMITTED` is absorbing. Once a canonical exchange is committed, no dimension's transition aborts it, re-exchanges it or re-labels it.
- **CD-2.** U may enter `Quarantined` only through native `Quarantine_Use`. That command is legal from `Reserved`, `Effect_Observed` and `Quarantined` (`worldline-operation_authority.adb:129-130`). It is taken when a fact the next U transition needs is genuinely uncertain:
  - an unknown or failed durable result capture;
  - unestablished chain evidence;
  - a custody `UNKNOWN` that hides the result.

  This is permitted even when O = `COMMITTED`, and it does not change O. K4 `Resolve_Effect` and `Resolve_No_Effect` (`:156-167`) and `Resolve_Recovery` (`:131-146`) remain the exits. A deferred physical settlement (root LIVE) or a missing source adapter (DF-5) is **not** uncertainty and never triggers quarantine.
- **CD-3.** U `Observe_Effect` needs authentic `Chain_Effect` (`:147-149`). It is independent of P, so on the root route it may occur while P is `Running`.
- **CD-4.** U `Settle_Use` follows P settlement of the operation's own reservation. This preserves the original order, `settle_historical` before `SETTLE_USE` (`rw/protected_operations.py:805-808`), and the terminal replay at `:786-790`.
- **CD-5.** P `Release_Hold` and `Charge_Budget` are decided natively, and only in these cases (`core/resource_run_ledger.ads:317-322`):
  - `Release_Hold` from `Terminal` with `Reaped`;
  - `Release_Hold` from `Reserved | Launch_Intent | Settlement_Unknown` with no effect and `Never_Launched`, the never-launched held-capacity release;
  - `Charge_Budget` from `Terminal` with `Reaped`.

  `Retain_Uncertain` covers `Unknown`. Nothing in P moves on EOF, handler return, a deadline or a missing cgroup.
- **CD-6.** C decides which process may mutate which state:
  - FRONT_* phases: the front;
  - WORKER_OWNED: the worker;
  - collector phases: the collector in the front process, with no Store owner;
  - `UNKNOWN`: nobody, until the protected recovery authority redecides natively (§6.3, §9.3).
- **CD-7.** C transitions never change O. C = `UNKNOWN` changes U only through CD-2, and P only through native `Retain_Uncertain`.
- **CD-8.** The first `RESULT_CAPTURE` boundary is write-once (`rw/protected_operations.py:780-785`). Later captures are additive `RESULT_REPORT` boundaries, in the same pattern as the existing `RETURN_REPORT` (`:763-764`). Settlement uses the retained first capture.
- **CD-9.** Child rows settle before their root row. Native `Parent_Supports` already requires `(if Counted (Child) then Counted (Parent))` (`core/resource_run_ledger.ads:250`), so a root release while a child is counted fails containment natively. The Python order only follows the native rule.

### 2.3 Illustrative combinations (DESIGN; the full legal-product table is an SL-6 deliverable)

| O | U | C | P (root row) | Legal? | Why |
|---|---|---|---|---|---|
| COMMITTED | Effect_Observed | WORKER_OWNED | Running | yes | CD-3. Physical settlement deferred while LIVE. |
| COMMITTED | Effect_Observed | CLOSED_WITNESS | Released | yes, transient | The next step is native `Settle_Use` (CD-4). |
| COMMITTED | Quarantined | CLOSED_WITNESS | Released | yes | Physical settled. Use uncertain, so K4 owner route (CD-2). |
| COMMITTED | Released | any | any | no | `Release_Use` needs authentic no-effect evidence (`.adb:153-155`), which a committed exchange cannot supply. |
| NO_EXCHANGE | Settled | — (serial) | Released | yes | Serial path. Never-launched release (CD-5), then `Settle_Use`. |
| UNKNOWN | Quarantined | UNKNOWN | Settlement_Unknown | yes | Holds retained. Protected recovery authority (§9.3). |
| any | any | any | Released while P is Live | no | CD-5. |

### 2.4 Path mapping

- **Serial path.** O, U and P only. The sequence is unchanged from `rw/protected_operations.py:727-811`: reserve → pre-effect → `EFFECT_INTENT` (with `DISPATCH_INTENT`) → handler → `RESULT_CAPTURE` → `OBSERVE_EFFECT` → `settle_historical` → `SETTLE_USE`.
- **Root route.** `finish` is split (§10.2). `observe_committed_effect` runs while the root is LIVE. `settle_physical` and `settle_use` run after an authentic CLOSED witness, or after an authentic never-launched classification.

---

## 3. Seam 1: scoped canonical operation (RC-01, D-1a, D-1b)

Current draft state and quoted requirements are carried by slices **B-S1-CUR** and **B-S1-REQ** (Appendix C).

### 3.1 Unit and decision type (DESIGN; spec only in slice S1)

The unit is additive. It is a sketch for review, not source.

```ada
with Worldline.Operation_Authority; with Worldline.Collapse_Wire;
with Worldline.Canonical_Operation; with Resource_Run_Ledger; with Resource_Scoped_Run_Ledger;
package Worldline.Scoped_Canonical_Operation with SPARK_Mode is
   package A renames Worldline.Operation_Authority;
   package O renames Worldline.Canonical_Operation;
   package L renames Resource_Run_Ledger;
   package S renames Resource_Scoped_Run_Ledger;
   package C renames Worldline.Collapse_Wire;
   subtype Decision is O.Decision;   -- identity decision mapping; no new enumeration
   function Reference
     (Data : A.Q.Byte_Array; G : A.Grants; H : A.Uses; B : A.Binding;
      Now : A.Q.Quantity; E : A.Evidence;
      State : S.State; Frames : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      Bound : L.Binding; Requester : L.Identity; Peer : A.Optional_UID;
      Collapse : C.Raw_Request) return Decision with Global => null;
   function Decide (<same profile>) return Decision
     with Global => null, Post => Decide'Result = Reference (<same actuals>);
end Worldline.Scoped_Canonical_Operation;
```

- **Decision mapping.** `Decision` is a subtype of `Worldline.Canonical_Operation.Decision` (`core/worldline-canonical_operation.ads:11-12`). The decision correspondence is therefore the identity. There is no independently declared enumeration and no bijection to prove (review §3).
- **Naming.** The original uses `H` for capability uses. The scoped history parameter is named `Frames` to avoid that clash.
- **Contracts.** The shape follows the original `Reference`/`Decide` pair (`.ads:21-31`). `Reference` is an ordinary function, not `Ghost`, and `Decide`'s `Post` equates them. No new precondition is added.

### 3.2 Clauses, in the original order (DESIGN)

| Clause | Original (`core/worldline-canonical_operation.adb:10-34`) | Scoped |
|---|---|---|
| C1 authority (literal) | `A.Decide (Data,G,H,B,Now,A.Reserve_Use,E,Empty,Empty) /= A.Reserved_Replay` → `Authority_Refused` | Identical text. |
| C2 resource (lifted) | `not L.Conserved (Data,State,Rows) or else not L.Contained (Data,Rows) or else not L.Native_Valid (Data,State,Rows,Observed) or else not (for some I => L.Same_Binding (Rows(I).Bound,Bound) and then Rows(I).State in Reserved|Launch_Intent|Running)` → `Resource_Refused` | `not S.Valid (Data,State,Frames,Rows,Projection,Buckets,Current) or else not S.Native_Valid (Data,State,Frames,Rows,Observed,Facts) or else not S.Current_Facts (Data,Current,Facts) or else not (for some I => S.Retained_Origin (Data,State,Frames,Rows(I)) and then L.Same_Binding (Data,Rows(I).Bound,Bound) and then Rows(I).State in L.Reserved|L.Launch_Intent|L.Running and then L.Same_Context (Data,Rows(I).Scope,State.Current))` → `Resource_Refused` |
| C3 binding (literal, scope re-read) | Equalities of peer, owner and the seven bound digests; `State.Scope.Instance`, `.Policy`, `.Policy_Epoch` against `B`; `Bound.Resource_Epoch` against `B.Resource_Epoch` → `Binding_Mismatch` | Identical, with `State.Scope` replaced by `State.Current` (the scoped ledger's current context) and `O.Digest_Matches` reused. |
| C4 collapse (literal) | For `Commit_Collapse | Commit_Transaction`: well-formed, decoded phase `Commit`, `Decide_Wire = Authorized`, else `Collapse_Refused` | Identical text. |

- `S.Valid` is `Shape ∧ Physical_Reference ∧ Contained_Reference ∧ Current_Valid` (`core/resource_scoped_run_ledger.ads:303-312`).
- `S.Current_Facts` (`:296-300`) is included so that the fact roster belongs to the same current observation as `Current`. The scoped `Check` has the same conjunct (`:410-411`). It is a design choice for review (G4, §3.9).

### 3.3 Clause correspondence, stated for proof

| Original conjunct | Scoped conjunct | Correspondence obligation |
|---|---|---|
| C1 | C1 | Syntactic identity, over the rebased arena (L-RB). |
| `L.Conserved` (includes `L.Shape`) | `S.Shape` ∧ `S.Physical_Reference` | L-C2a, L-C2b |
| `L.Contained` | `S.Contained_Reference` | L-C2c |
| `L.Native_Valid` | `S.Native_Valid` ∧ `S.Current_Facts` | L-C2d, L-CL-1 |
| bound row ∈ {Reserved, Launch_Intent, Running} | the same, plus `Retained_Origin` and FRESH `Same_Context` | L-C2e |
| (no counterpart) | `S.Current_Valid` | L-C2f, by construction of the witness |
| C3 with `State.Scope` | C3 with `State.Current` | L-C3: `State.Current = State.Scope` under `Emb` |
| C4 | C4 | Syntactic identity |

### 3.4 Domains: FRESH, RETAINED, HISTORICAL (D-1b)

**FRESH.** This covers the pre-effect conjunction of this unit and an in-request scoped exchange input (SL-2b).
- The bound row's origin context must be `L.Same_Context` with `State.Current`. That is a semantic comparison, never record equality.
- Static consistency argument (STATIC_REASONING): a fresh reservation natively requires `Same_Context (Before.Current, R.New_Row.Scope)` (`resource_scoped_run_ledger.ads:359`). `Record_Launch_Intent` and `Record_Running` natively refuse `Context_Changed` when `Before.Current` differs from the request scope (`:436-438`), and a non-Reserve request scope must equal the row's origin scope (`:373-375`). So a rollover between reserve and launch already blocks the launch in the original scoped kernel. The FRESH clause asks the same of the pre-effect.
- A rollover between reserve and pre-effect therefore gives `Resource_Refused`, with holds retained and the native release still available (CD-5).
- This case has **no counterpart** in the original flat domain, because the single-frame embedding admits no rollover. Review question RQ-1 asks whether the reviewer treats it as an accepted case. If so, the pre-effect needs the RETAINED join below rather than refusal, and that join's obligations apply.

**RETAINED.** This covers the scoped successors that decide after a possible rollover: K4 owner completion (`rw/protected_operations.py:605-622`, slice SL-2c), and exchange recovery after restart (SL-2b). Each needs a `Retained_Join` obligation, as a native relation proved with its caller:
1. There is a frame index k such that `S.Origin (Row, Frames (k))`, and `Row.Bound.Resource_Epoch < Frames (k + 1).First_Epoch` when k < `Frames'Last`. This is exactly the witness of `Retained_Origin` (`:116-121`).
2. The authority binding equalities of C3 are evaluated against `Frames (k).Scope` (instance, policy, policy epoch): the context in which the use was reserved, not `State.Current`.
3. The original native use replays to `Reserved_New` on its retained snapshot (`_original_native_use`, `rw/protected_operations.py:430-438`). No fresh `Reserve_Use` is decided.
4. A resolving request (`quarantine.resolve`) carries its own fresh use, decided by `Resolve_Recovery` (`worldline-operation_authority.adb:131-146`) or `Resolve_Effect`/`Resolve_No_Effect` (`:156-167`).
5. Every original retained-origin lifecycle step of the scoped `Ordinary_Reference` (`:370-392`) is preserved. No retained case is removed.

**HISTORICAL.** Settlement and closure settlement use no canonical conjunction.
- The use dimension uses `Settle_Use` or `Replay_Use` with authentic `Chain_Effect` on the original binding (`.adb:150-152`, `:168-171`).
- The physical dimension uses scoped lifecycle `Check` on retained-origin rows (CD-5).
- There is no fresh peer, use, exchange or socket (RQC: "historical committed settlement after current deny/revocation without new use/exchange/socket").

### 3.5 Projection exactness (rounding claim withdrawn, F-11)

- `Projection_Valid` requires both conditions below (`core/resource_scoped_run_ledger.ads:149-152`). This is exact division, with no rounding lane.
  - `(L.Amount (Data, Item) * N) rem D = 0`
  - `Value (P.Amount) = (L.Amount (Data, Item) * N) / D`
- `Contained_Reference` bounds child charges by `(Q.Value (Data, Rows (I).Amount) * N) / D` (`:210-211`).
  - It uses the row's raw `Amount`.
  - `Projection_Valid` uses `L.Amount`, which is 0 for a released row and the observed usage when that exceeds the amount (`resource_run_ledger.ads:187-192`).
  - The embedding lemmas must treat the two separately (L-C2c).
- The embedding uses the identity factor N = D > 0. Lemma **L-PJ-1** is to be proved, not assumed: for N = D > 0, `(x * N) rem D = 0` and `(x * N) / D = x`, over `Valid_Big_Integer`.

### 3.6 Arena and span mapping

- **Production.** One shared arena, as in the original wrapper. That wrapper prepares the authority snapshot into an `Arena` and then marshals state, binding, requester, rows and observations into the same arena (`rw/canonical_operation_kernel.py:30-35`). The scoped wrapper marshals the scoped packet into that same arena through `S._marshal (value, arena)` (`rw/resource_scoped_run_ledger.py:275`). There is no rebasing at run time.
- **Ghost correspondence.** `Data' = Data` extended with a witness region `WD` of fresh bytes, placed after `Data'Last`, or before `Data'First` when there is no room after. Every original span-bearing field is mapped by `Rebase`. The required properties are lemmas **L-RB-1 … L-RB-3**:
  - **L-RB-1.** A span valid in `Data` keeps its position and length, and its bytes are equal in `Data'`. Identity on `Data'Range`.
  - **L-RB-2.** A nonzero-length span invalid in `Data` is mapped to a canonical invalid present span that is representable for any nonempty `Data'`, for example `First => Data''Last, Length => 2`. Validity is preserved both ways.
    - Zero-length spans are valid anywhere: `Identity_Valid` (`resource_reservation_transition.ads:85-88`) and `Span_Valid` (`resource_quantities.ads:25-28`).
    - So zero-length spans map to themselves. Empty identities are `Same`, and that stays true.
  - **L-RB-3.** No rebased original span overlaps `WD`.
- **Gap G3.** An arena with fewer free `Byte_Index` positions than `|WD|` on both sides has no room for `WD`. Example: `Data'First = 1` and `Data'Last` near `Byte_Count'Last` (`resource_quantities.ads:7-8`). Such arenas are not covered by this construction. This gap is a coverage gap of the lemma, not a runtime refusal. It stays OPEN until another construction covers it (RQ-2).

### 3.7 Structural embedding `Emb (Orig, W)` (total, Ghost)

The original packet is `Orig = (Data, G, H, B, Now, E, State, Rows, Observed, Bound, Requester, Peer, Collapse)`. The witness `W` consists of:
- `WD`;
- frame fields: `Frame_Head`, `First_Epoch`, `Store_Genesis`, `Store_Id`, `Root_Head`, `Root_Count`, optional `Prime`, `Cause`, `Requester`, `Receipt`, `Catalogue_Head`, `Observation_Head`;
- `Physical_Head`;
- key fields `K_Resource` and `K_Unit`;
- factor `N`;
- per-row amount spans `Amt (i)`;
- bucket fields `Cap_Source` and `Bucket_Observation_Head`;
- current-observation fields;
- per-row facts `Fct (i) : K.Facts`.

`Emb` applies `Rebase` to every span-bearing field of `Orig` (written `'` below), including the quantity spans in `G`, `H`, `E` and `Now`, and builds:

| Scoped component | Built from |
|---|---|
| `State` | `(Current => State'.Scope, Resource_Epoch => State'.Resource_Epoch, Universe_Head => State'.Universe_Head, Ledger_Head => State'.Ledger_Head, History_Head => W.Frame_Head, Physical_Head => W.Physical_Head)` |
| `Frames` | One frame: `Scope => State'.Scope, First_Epoch => W.First_Epoch, Universe_Head => State'.Universe_Head, Frame_Head => W.Frame_Head, Prior_Frame => absent`, and the other frame fields from `W` |
| `Rows` | `Rows'`, unchanged in content |
| `Projection (i)` | `Key => (Machine => State'.Scope.Host, Resource => W.K_Resource, Unit => W.K_Unit), Bound => Rows'(i).Bound, Origin => Rows'(i).Scope, Catalogue_Head => W.Catalogue_Head, Numerator => W.N, Denominator => W.N, Amount => W.Amt (i)` |
| `Buckets` | One bucket: `Key` as above; `Capacity`, `Held_Total` and `Charged_Total` from `State'`; `Capacity_Source`, `Catalogue_Head` and `Observation_Head` from `W` |
| `Observed` | `Observed'`, unchanged in content |
| `Facts` | `W.Fct` |
| `Current` | The heads of `State` above, plus the frame and current fields of `W` |
| others | `Bound'`, `Requester'`, `Peer`, `Collapse`, `G'`, `H'`, `B`, `Now'`, `E'` |

A **multi-frame variant** with more than one frame and a valid `Prior_Frame` chain is defined in the same way for gap G1. Its coverage is claimed only where L-INV-1 does not already apply.

### 3.8 Coherent witness relation `Coherent (Orig, W)` (field-level; non-circular)

- **W1.** Every witness identity span is `Id_Valid` in `Data'`. Every witness quantity is `Nonnegative_Valid`. `Prime` is absent or valid.
- **W2.** `Value (W.First_Epoch) ≤ Value (Rows (i).Bound.Resource_Epoch)` for every i, and `≤ Value (State.Resource_Epoch)`.
- **W3.** `Value (W.N) > 0`.
- **W4.** `Value (W.Amt (i)) = L.Amount (Data', Rows'(i))` for every i.
- **W5.** For every i, `Fct (i)` relates field by field to the row and the state:
  - `Observation_Head` is `Same` as `Observed (i).Observation_Head`;
  - `Retained` is `Same_Binding` with `Rows (i).Bound`;
  - its current header (`Current`, `Current_Epoch`, `Current_Universe_Head`, `Current_Ledger_Head`) is `Same`/`Same_Context`/`Same_Epoch` with `State`;
  - `Intent` is `Id_Valid`.
- **W6. Producer faithfulness.** `Observed (i).Observed = K.Classify (Data', State', Rows'(i), Fct (i))` for every i, where `K` is the original producer's classifier (`core/resource_observation_classification.ads:121-125`).
- **W7. Producer unit rule.** If `Observed (i).Observed ∈ {Live, Reaped}`, its unit, cgroup and invocation are `Optional_Same` as `Fct (i)`'s. Otherwise they are `Optional_Same` as `Rows (i)`'s. This mirrors `rw/protected_scoped_resource_runtime.py:242-244`.
- **W8.** Every `Rows (i).Bound.Universe_Head` is `Same` as `State.Universe_Head`. This holds for reachable states by L-INV-1.
- **W9.** `WD` is disjoint from every rebased original span. `Rebase` satisfies L-RB-1 … L-RB-3.
- **W10.** No witness field is computed from any `Reference`, `Decide`, `Check`, `Classify` of the scoped model, `Valid`, `Native_Valid` or decision result. This is a rule on how witnesses are constructed in the proofs.

### 3.9 Obligations (statements only; nothing here is proved)

All are Ghost procedures with `Always_Terminates` and `Global => null`. None uses `Import` or `Assume`. Recursive references use their existing variants.
- **L-EQ (decision equality on coherent witnesses).** `Coherent (Orig, W) ⇒ Scoped.Reference (Emb (Orig, W)) = O.Reference (Orig)`. A corollary is refusal preservation (**CV-D**): every original refusal maps to the same named refusal on coherent witnesses.
- **Per-clause lemmas.**
  - **L-C2a.** `L.Shape ∧ W2 ∧ W8 ⇒ S.Shape (Emb)`.
  - **L-C2b.** `L.Conserved ∧ W4 ⇒ S.Physical_Reference (Emb)`, by induction on `Count`, relating `Charge_Reference` with no parent and one key to `Sum_Reference` with no parent.
  - **L-C2c.** `L.Contained ⇔ S.Contained_Reference (Emb)` under W3, W4 and L-PJ-1. This separates `Q.Value (Amount)` from `L.Amount`.
  - **L-C2d.** `L.Native_Valid ∧ W5–W7 ⇒ S.Native_Valid (Emb) ∧ S.Current_Facts (Emb)`, and the converse on coherent witnesses.
  - **L-C2e.** The original bound-row existential implies the scoped one. This uses L.Shape's `Same_Context (State.Scope, Rows (I).Scope)` and L-SC-1.
  - **L-C2f.** `S.Current_Valid (Emb)` holds by construction.
  - **L-C3.** `State.Current = State'.Scope` under `Emb`.
  - **L-CL-1.** Under `Emb`, `S.Classify_Reference` equals `K.Reference`. This needs `Retained_Origin` under one frame to be equivalent to `Row_Valid ∧ Same_Context (State.Scope, Row.Scope)` together with W2 and W8.
  - **L-SC-1.** `Same_Context` is symmetric and transitive on valid contexts. This is derived from `Same_Identity` (`resource_reservation_transition.ads:93-100`) and `Same_Epoch`'s postcondition.
- **L-INV-1 (reachability invariant).** Every original ledger produced by `L.Check = Ready` steps from an authentic empty initial ledger satisfies W8, row epoch ≤ state epoch, and `L.Shape`'s per-row context equality.
  - Basis: `Check` refuses any change of `Universe_Head` (`resource_run_ledger.ads:342-345`).
  - Basis: `Reserve` binds the new row's universe head to the state's (`:367`).
- **CV-B (producer coverage).** For every original input that satisfies L-INV-1 and whose `Observed` was produced by `K.Classify` over facts `F_i` (W6, W7), a coherent witness exists. The proof is constructive: `Fct (i) := F_i`, and the frame, key, factor and amount fields are fresh bytes in `WD`.
- **CV-C (fixture coverage).** Every original native fixture vector that exercises `Worldline.Canonical_Operation`, accepted or refusal, is either embedded with a coherent witness and shown to give the same decision, or is listed as raw-domain-only. In every case the original unit and its fixture remain unchanged and keep running.

Known potential gaps. Each stays OPEN until proved, or until the **scoped** model is revised. The original references are never changed.

| Gap | Description | Resolution route |
|---|---|---|
| G1 | Original raw inputs whose rows carry a universe head different from the state's. `L.Shape` accepts them; scoped `Origin` refuses under one frame. | L-INV-1 covers reachable states. Raw-only inputs need the multi-frame variant or are raw-domain-only (CV-C). |
| G2 | `Observed` labels not produced by `K.Classify`, so W6 fails. `L.Native_Valid` does not re-check liveness, while scoped `Native_Valid` does (`:256-257`). | Raw-domain-only for fixtures. The scoped model refuses copied liveness labels by design (G-8). |
| G3 | Arenas with no room for `WD` (§3.6). | Another embedding construction (RQ-2). |
| G4 | The added `S.Current_Facts` conjunct. | Covered by W5 for coherent witnesses. RQ-3 asks the reviewer to confirm the choice. |
| G5 | The `Same_Context` algebra. | L-SC-1 must be proved from the existing definitions. |
| G6 | Live rows without effect (`Launch_Intent` rows classified Live). The original does not constrain observed unit fields for such rows. | W7, the producer rule. Raw-domain-only otherwise. |

### 3.10 Why the relation is not circular

- `Coherent` mentions no decision of either model. It mentions no `Valid`, `Native_Valid`, `Contained`, `Physical` or `Shape` result of the scoped model, and no C2 predicate.
- Its one classifier reference, W6, is the original producer's `K.Classify`. That is an input-generation relation and is not one of the two functions L-EQ compares.
- An antecedent of the form "the scoped and original decisions agree" is excluded by W10.
- A theorem proved only on convenient valid fixtures does not discharge CV-B or CV-C (review §3).

### 3.11 Contracts, termination and cost

- `Decide` has the `Post` shown in §3.1. No new `Pre` is added.
- `Reference` calls existing functions whose recursive references already carry `Subprogram_Variant`, for example `Sum_Reference` and `Charge_Reference`.
- Checked-build Ghost and contract evaluation has native time, allocation and copy costs under D2: `Contained` is cubic and `Sum` quadratic (D2R C-SUM), and the slot term is Θ(N²·S⁴) (D2R C-SLOT). These are OPEN native cost obligations (P1:129-131). Nothing here claims the checked build finishes within any bound, and no cap is added (G-2).

### 3.12 ABI and wrapper

- The exports are `wl_scoped_canonical_operation_{version,layout,decide}_v1`. They go only through the sole `worldline-c_api` boundary, in the C-API v4 pattern (§14.3):
  - transport package `Scoped_Operation_Transport`;
  - value decoding in an On unit `Worldline.Scoped_Canonical_Operation_Wire`;
  - no new Off unit.
- Final ABI adoption waits for the reviewed C-API successor (G-CAPI, §15).
- `Worldline.Canonical_Operation_C_API` is `SPARK_Mode => Off` outside the boundary (observation N-3). It is an original body obligation, not a precedent (review §1). Its consolidation belongs to L-CAPI-P.
- The Python wrapper `ScopedCanonicalOperationKernel` makes exact version, size, alignment and offset checks, as `rw/canonical_operation_kernel.py:13-27` does. It returns the raw input, arena, rosters and output, never a Python verdict.

### 3.13 Caller (`pre_effect`)

- An exact-type branch. The original branch stays byte-identical when `type (self.resources) is ProtectedResourcePrincipal`.
- The scoped branch runs when the type is `ProtectedScopedResourcePrincipal`, and it:
  - reads plan and policy from the single crosswalk entry (§4.4) for both `pre_effect` and `machine_admission`. That removes the `SCOPED_CALLER_MACHINE_POLICY_DIFFERS_FROM_ACTUAL_OWNER_PLAN` mismatch (`rw/protected_scoped_resource_runtime.py:640-641`) without weakening the comparison;
  - takes one `gate.mutex` section, through the §13.1 entry wrapper, across context → capture → inspect → decide;
  - re-checks `before == current_snapshot ()`;
  - leaves the collapse evaluation unchanged (`rw/protected_operations.py:692-706`);
  - retains the raw native input and output in `FULL_PRE_EFFECT_BOUNDARY`;
  - keeps `collapse_packet` and `collapse_values` byte-compatible for the broker.
- The root route keeps `DISPATCH_INTENT` (DF-3).
- The scoped exchange (SL-2b) and K4 (SL-2c) successors follow the same pattern, with the RETAINED join where §3.4 applies.

### 3.14 Additive controls (pure native value fixtures, Ada `-gnata`; no root needed)

- Each clause mutated gives its exact named decision.
- Every original `Canonical_Operation` fixture vector, embedded with a coherent witness, gives the same decision (CV-C). Raw-domain-only vectors are listed.
- Scoped-only vectors give `Resource_Refused`:
  - multi-frame;
  - multi-bucket;
  - a stale frame;
  - a missing parent row;
  - bucket conservation off by one unit;
  - a non-zero projection remainder.
- FRESH rollover pair: a rollover between reserve and pre-effect gives `Resource_Refused`, with holds retained and release available. No rollover gives `Ready`.
- RETAINED join vectors (SL-2c): origin-frame binding, a stale origin, and a wrong frame index.
- An ABI layout test per field.
- Mutants: a body dropping a clause, and a weakened `Same_Context`. Each must fail the proof gate (pins plus `REQUIRED_PROVED`).
- Lab controls (operator, §16): a scoped positive operation on both the serial and the root route, plus the RQC grant-refusal set.

### 3.15 Dependencies and authority

- **S1, the spec**, depends on existing types only: authority, collapse, scoped ledger and classification `Facts`.
- **Wire layout and exports** depend on G-CAPI. Bodies and proof depend on the admitted frame (R-PROOF). The successors SL-2b and SL-2c depend on S1, on §2 and on L-A1.
- Drafting is lead work, with independent GPT-6.1 review. Runtime positives need the lab (operator).

### 3.16 Review questions for this seam (not operator decisions)

- **RQ-1.** Is a rollover between reserve and pre-effect an original accepted case? If so, the pre-effect needs the RETAINED join rather than the FRESH refusal.
- **RQ-2.** Which embedding construction should cover G3?
- **RQ-3.** Is the `S.Current_Facts` conjunct in C2 acceptable (G4)?

<!-- V2-CONTINUE -->
