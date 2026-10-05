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
| Write history | Every file in the location above was created or changed only with the Write and Edit tools. No Write or Edit was refused. Bash was used only for read-only inspection. Its deviations from the brief's literal rule (a `2>/dev/null` stderr discard and commands outside the listed set) are disclosed in C.1 and AUTHOR-NOTES §5. |

Every statement about source in this document is **static**: read from files, or derived by reasoning from what was read. Nothing was compiled, run, imported, proved, tested or measured. Kernel, systemd and Ada-visibility statements marked **[unverified reasoning]** are the author's reading and need the evidence named next to them.

---

## A. Closure table

"Answer" is a design statement for the reviewer. The author closes nothing. Every proof, native, control, physical and acceptance obligation stays OPEN.

### A.1 Required changes RC-01 … RC-12

Sub-requirements quote the sealed `review.json` `required_changes[].change`, split at its clauses.

| # | Sub-requirement (review text) | v2 answer | Where |
|---|---|---|---|
| 01.1 | "Define the scoped canonical spec" | Additive unit `Worldline.Scoped_Canonical_Operation`: typed `Reference`, `Decide` with `Post => Decide'Result = Reference (…)`, clauses C1–C4 in the original order. The decision type is `subtype Decision is Worldline.Canonical_Operation.Decision` (reuse, no new enumeration). | §3.1–§3.3, §3.11 |
| 01.2 | "complete arena/span/decision mapping" | Production keeps one shared arena, exactly as the original wrapper (`canonical_operation_kernel.py:30-35`). The Ghost correspondence uses an explicit total `Rebase` with two-way validity preservation, including malformed and boundary spans. The decision mapping is the identity, by type reuse. | §3.6 |
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
| 04.5 | "independent physical collection" | Three independent collector futures: handler terminal, CLOSED and outer wait, raw drains. Physical settlement does not wait for the handler terminal. | §6.7 |
| 04.6 | "lossless acyclic retention" | A content-addressed blob table holding raw observed bytes only. A defined snapshot closure that excludes the custody journal and the blob store. Change-only re-append. No OOM or cost claim. | §6.8 |
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
| 07.2 | "Preserve native QUARANTINE_USE/K4 recovery" | CD-2: native `Quarantine_Use` from `Reserved | Effect_Observed | Quarantined` (`worldline-operation_authority.adb:129-130`) and K4 resolution (`:156-167`) stay available. COMMITTED is never changed. | §2, §10.2 |
| 07.3 | "NEVER_LAUNCHED held-capacity release" | CD-5 keeps both native release cases of `resource_run_ledger.ads:317-320`. | §2, §10.1 |
| 07.4 | "terminal replay and serial semantics" | The serial path keeps its exact order (`protected_operations.py:778-811`), including the SETTLED replay at `:786-790`. | §10.1 |
| 07.5 | "keep write-once original result plus additive reports" | The first `RESULT_CAPTURE` is write-once. Later captures are additive boundaries. The collector uses the retained capture. | §2 CD-8, §10.1, §10.3 |
| 08.1 | "Define full slot/drain transfer barriers" | T1 FREEZE: stop the reader at a chunk or message boundary and drain the asyncio buffers. | §7.3 |
| 08.2 | "buffered/in-flight bytes" | T1/T2: buffered bytes are spooled durably before the descriptor moves. | §7.3 |
| 08.3 | "durable positions" | Spool position P is recorded in FREEZE and INTAKE. The spool hash chain continues from P. | §7.3 |
| 08.4 | "acknowledgments" | T4 INTAKE (CAS) and T5: the front closes its copy only after it reads the durable INTAKE. | §7.3 |
| 08.5 | "failure ownership" | A failure-ownership table for every T-step crash point. Never two readers. | §7.3 |
| 08.6 | "OFD/lock custody" | Kernel evidence that the received descriptor is the same open file description (kcmp, recorded by the front), plus lock-held evidence. fstat equality alone is not used as OFD proof. | §7.3 |
| 08.7 | "genuine helper/outer-wait producer retention or relay" | Retention. The helper, namespace init and systemd remain the reapers and waiters. Only observation and reader roles move. No reaping right is claimed. | §7.2 |
| 09.1 | "Define explicit native requester correspondence" | Additive SPARK `Worldline.Requester_Correspondence`, whose `Join` consumes explicit raw fields, not a digest in `current_source`. | §8.1 |
| 09.2 | "authenticated socket/host-record custody" | Journaled raw host records before the descriptor moves, and a full-roster receive before any peer is built. Socket-object evidence is the `SO_COOKIE` pair (J5, K-14). Socket identity equality (J4) is necessary, not sufficient. | §8.1, §8.2 |
| 09.3 | "Label retained observations separately from fresh reads" | New exact type `RetainedRequestObservation`. No fresh-read gate accepts it. Per-gate enumeration. | §8.3 |
| 09.4 | "preserve exited/delegated/same-UID-new-process and full UID/GID domains" | Domain list D8-1…D8-6. Full unsigned UID/GID, including 0 and the maximum. | §8.4 |
| 09.5 | "without a new live-client or fresh-pidfd acceptance precondition" | Pidfd evidence is optional and never required. FRESH needs only what the original needs, the retained socket. Unestablished correspondence stays explicit and unresolved, never replaced by a PID label. | §8.4 |
| 10.1 | "Use reviewed appended effective pin overrides" | Append-only `CONTRACT_PINS.update` statements after the last existing line. The stale `protected_operations.py` pin is superseded only by an appended, reviewed override computed on reviewed final source. | §12.1 |
| 10.2 | "plus an external exact inventory/freeze for the manifest itself and all source/control/project/header/helper/dependency files" | An external freeze record of exact sha256, bytes and mode for every file of the integrated candidate, including `proof_manifest.py`. It is held outside the sources and bound by the review freeze. There is no self-hash. | §12.2 |
| 10.3 | "enroll every new native semantic unit" | `REQUIRED_PROVED` and `DECLARED_CORE_ADA_SOURCES` appends for every new unit in §3–§8. No name inside `Worldline.C_API` (observation N-2). | §12.3, §12.4 |
| 10.4 | "retain the full original strict scope" | Floor 251, the S5 535-name ordered prefix, the sole `worldline-c_api` boundary, zero unproved, justified and `pragma Assume`, and strict warnings. | §1 G-5, §12.3 |
| 11.1 | "Repair the spec/body/integration dependency DAG" | An acyclic spec DAG over S0–S4 and S6–S11 (no slice is named S5), body/caller nodes, integration gates and runtime gates, with the v1 plan's missing edges added. | §15 |
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
| D-8b | Lead prepares domain-preserving protocol; operator for kernel measurement; independent GPT-6.1 review | Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client. | No blanket fresh-pidfd or live-client precondition. The exited-peer path is defined. This seam's kernel measurement items, K-1…K-4 and K-14 (§8.5), go to the operator under OP-7, which holds every kernel measurement K-1…K-14. | §8.4, §8.5, §16 |
| D-9a | Lead additive SPARK relation and caller designer; independent GPT-6.1 review; operator for fault campaign | Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes. | Mandatory native phase relation under the actual CAS, with exclusive branches. | §6 |

### A.3 Statically observed draft defects and their required fixes

**Carried from v1 and the review.** All are static and none was executed.

| Id | Defect (static) | Evidence | Required fix in v2 | Where |
|---|---|---|---|---|
| DF-1 | The stale effective pin of `runtime/worldline/protected_operations.py` refuses every protected start. | Pin `8be1f9ab2c689ecc9e915464e8e454863c205ca2f1f4a1763a5125aa2b61139e`, recomputed `2a6d71c7ca81d456d41f242a880b8fa3e0f115d794f4772e115767236b183547` (review F-03). Refusals at `protected_startup.py:683-684` and `protected_root_worker.py:355-357`. | An appended, reviewed override computed on reviewed final source only. Never a refresh that makes incomplete source eligible. Plus the external exact freeze. | §12.1, §12.2 |
| DF-2 | Duplicate `attach_scoped_resource`. The later one (`protected_scoped_resource_runtime.py:961-964`) shadows the stricter one (`:52-58`) and drops `SCOPED_EXACT_EARLY_SELECTED_PRODUCER_REQUIRED`. Pre-existing. No caller. | F-05 | One definition, keeping the exact producer path, early-selected DATA membership and the already-attached refusal. Called only from v2 `construct()`. | §13.2, §11.7 |
| DF-3 | The root route omits three original pre-dispatch checks of `_invoke_serial`: the request-context check (`protected_operations.py:728`), the unresolved-use gate (`:730`), and the workload refusal (`:744-745`). It also drops the `DISPATCH_INTENT` boundary (`:749`). | F-06; `protected_root_worker.py:158-171` | Apply them in the original order and position: context and unresolved gate before `_reserve`, the workload refusal after `_reserve` with quarantine on exception, and `DISPATCH_INTENT` retained. | §13.3, §9.3 |
| DF-4 | Self-comparing `Root_Controller` identity pairs (`protected_root_observation.py:36-49`; the pairs are filled at `:43-49`). The process source lease comes from caller material (`:74-76`, `:121`). The named identity equalities are vacuous. Other `Controller_Valid` predicates are real (F-07). | F-07; `worldline-resource_child_execution.ads:48-59` | Tagged canonical comparable source records with native distinct-domain enforcement, in an additive V2 grammar. | §4 |
| DF-5 | The scoped historical settlement, lifecycle and owner-material adapters are undefined (`protected_scoped_resource_runtime.py:530-531`, `:548-549`, `:571-572`). | F-08 | Implement the three adapters on `CanonicalOperationPrincipal`, mirroring the originals over scoped committed history. | §10.4 |
| DF-6 | Conditional gate-mutex self-deadlock. `Gate.mutex` is a `threading.Lock` (`dependency-source/lab/intent_gate.py:371`). `intent_for_operation` holds it (`:385`) and calls `reconcile_context` (`:388`), which takes it again (`:357`). It is reached from `protected_operations.py:640`. Conditional on reaching it. Not reproduced. | F-02 | SL-0 lock discipline: one acquisition per public entry, `_locked` variants under an explicit holder marker, and a complete receiver-resolved audit including candidates N-6. The Gate is unchanged. No RLock substitution. No await inside a section. | §13.1 |

**New static observations by the v2 author.** They are for the reviewer to check. None is review and none was executed.

| Id | Observation (static) | Evidence (observed by read-only script or grep) | Consequence for the design | Where |
|---|---|---|---|---|
| N-1 | The lane's ordered `REQUIRED_PROVED` (614 names) and S5's (535) share an identical 419-name prefix and then diverge. 116 S5 names are absent from the lane, and 195 lane names are absent from S5 (J01, J02). The lane preimage has 485 names (419 + 66, J03). The draft adds 129 (J04). | AST literal evaluation of `proof_manifest.py` in the lane source, the lane preimage, S5 and commonV4. The common names keep identical order. | The integrated roster must keep S5's 535 names as the literal prefix and append lane names. The lane's own roster cannot serve as the integrated prefix. | §12.4 |
| N-2 | Eight `REQUIRED_PROVED` names (lane positions 606–613, J14) designate subprograms inside the `SPARK_Mode => Off` body of `Worldline.C_API`: `Child_Version`, `Child_Layout`, `Child_Decide` and `Child_Boundary.{Version,Shape,Array_Shape,Layout,Decide}`. `Child_Boundary` (draft `core/worldline-c_api.adb:1166-2251`) has no SPARK_Mode aspect. | SPARK UG release 28.0w ch04: "A non-SPARK subprogram body cannot enclose a separately analyzed SPARK region simply by adding a nested annotation." The required-proved check is at `proof_manifest.py:857`. The block came through the child-authority secondary union. Its sealed review records prefix, floor and boundary-set invariants (`REVIEW.md:15-17`) and does not discuss this point. | **[static reasoning, not executed]** These names cannot be proved under the unchanged boundary. The obligation they express must be carried by On units, with transport-only code in `C_API`. | §12.3, §14.3 |
| N-3 | 41 core files in the lane are `SPARK_Mode => Off` (J06). Two are `worldline-c_api.ad[sb]` (Off in both). 30 are the 15 C-API units, **On in S5 and Off in the lane**. 9 are protected-lineage C API files, **absent from S5 and Off in the lane**: `worldline-{actuation_full,canonical_exchange,canonical_operation,canonical_owner_completion,operation_authority}_c_api.*`. | grep over `core/*.ad[sb]` in the lane source and S5 | Composing lane files as-is would restore Off exemptions outside the sole boundary (P1:29 forbids that). Required: S5's On versions of the 15 units, plus a new consolidation successor L-CAPI-P for the 9 protected files. | §14.3, §15.1 |
| N-4 | Layout collision with C-API v4. The draft is the lane preimage C_API plus 6 inserted `with` lines and 1119 inserted lines (J07, J08) between `end Owner_Audit_Decide;` (draft `:1165`) and the final `end` (`:2285`). Its spec appends 32 lines (J15) after `wl_owner_audit_decide_v1`. S5 is the preimage plus one 53-byte line at `:32` (J09). v4's R-LAYOUT places the export runs at exactly those two positions. `External_Name` occurrences: 31 in S5 and 34 in the draft (J10). | difflib opcode summary; anchor lines; occurrence counts | A reviewed rebase is required. The tables are never edited to fit. | §14.1, §14.2 |
| N-5 | The draft renamings `Y J D A X E T N W O Q` (draft `:1199-1220`) are declared in the body of the nested package `Child_Boundary` (`package body Child_Boundary is` at `:1198`; end at `:2251`). Their scope is that body, not the whole C_API body. | Read at the cited lines. A heuristic scope scan agrees. | This refines the wording of C-API v4 §19 ("at C_API body level"). The hazard remains for any rebase that merges texts into one scope. | §14.2 |
| N-6 | Further nested `gate.mutex` acquisitions beyond P0-1. **Receiver-resolved by reading:**<br>(a) `submit_bound` holds the lock (`rw/protected_scoped_resource_runtime.py:412`) and calls `self.scoped_service.recover` (`:416`), which takes `self.gate.mutex` again (`rw/protected_scoped_resource_service.py:213`). The service's `gate` is the lease's Gate (`:62`, `:66`). This is on the reserve path (`rw/protected_operations.py:676`), right after P0-1.<br>(b) `reconcile_context` (`:357`) calls `scoped_service.commit` (`:373` → service `:223`) whenever a context advance is needed.<br>(c) **Same-object calls in `ProtectedScopedResourcePrincipal`, receiver read at every site.** While holding the lock:<br>- `settle_bound` (`:507`), `settle_historical` (`:526`), `resolve_historical` (`:567`), `reconcile` (`:612`), `machine_admission` (`:630`) and `launch_reserved` (`:701`) call `self.reconcile_context ()`;<br>- `launch_reserved` and `go_scoped` (`:854`) call `self.machine_admission`;<br>- `launch_reserved` and the `settle_bound` closure call `self.submit_bound`;<br>- the `settle_historical` and `resolve_historical` closures call `self.scoped_service.commit` (`:556`, `:596`).<br>Every callee takes the same `self.gate.mutex` at entry.<br>(d) **The base `ProtectedResourcePrincipal`** (`rw/protected_resource_runtime.py`) does the same. `launch_reserved` (`:534`) calls `self.machine_admission` (`:567` → `:474`) and `self.submit_bound` (`:570`, `:595` → `:404`). `settle_bound` (`:604`) calls `self.submit_bound` (`:615`–`:624`). This file and the scoped service were selected into the lane unchanged from L-A1 (origin `A1-v2-retry1`, `L/secondary-source-union-v1.json`).<br>(e) `RootControllerCapture._current` holds `p.gate.mutex` (`rw/protected_root_observation.py:57`) and calls `capture_execution (p, …)` (`:61`), which takes `p.gate.mutex` again (`rw/canonical_actor_execution.py:61`).<br>**Unresolved:** the base `settle_historical` calls `run_service.RunLedgerService` (`:652`, `:665`), which is outside the scan. | Reading at each call site. AST class membership. Name-based AST scan (AUTHOR-NOTES §3). `settle_bound` has no caller in the lane source (grep). | **[static reasoning; each is conditional on reaching it; none reproduced]** The lock is not reentrant, so each listed call blocks its own thread. Fixing P0-1 alone unblocks none of the reserve, launch, admission, GO, settlement or reconcile paths. SL-0 must cover every one, including the L-A1-lineage file (§13.1). The scan is a lower bound, not completeness. | §13.1 |
| N-7 | `RootCustodyJournal.append` is serialized by `BEGIN IMMEDIATE` but is not conditioned on a caller-supplied expected head or phase (`root_worker_journal.py:123-140`). | Read | This is why native CAS generations are needed. | §6.3 |
| N-8 | `capture_execution` appends an operation-journal `ACK` boundary inside the capture path (`canonical_actor_execution.py:125-127`). It is called by `RootControllerCapture._current` (`protected_root_observation.py:61`). | Read | This is the cause of the stale seed, defect 9(a). | §6.4 |
| N-9 | The draft block declares enumeration literals named `Size`, for example `type W_Raw_Id_Field is (Size, Alignment, …)` at draft `:1289`, and uses them in `when Size =>` choices. That is 84 whole-word occurrences not preceded by an apostrophe, besides 67 `'Size` attribute uses. C-API v4 adds a spec-level `subtype Size is Interfaces.C.size_t;`. | Script count (observed) | **[unverified reasoning, author's reading of RM 8.3/8.4]** The inner literals would hide the outer subtype inside `Child_Boundary`'s body. v2 does not rely on that and requires renaming. | §14.3 |
| N-10 | Classification `Facts` identity pairs, compared natively by `Custody` (`core/resource_observation_classification.ads:81-84`), are also filled from one value by producers. The root producer sets `held_namespace` and `namespace` to one value, `expected_helper_image` and `helper_image` to one value, and `held_challenge` and `challenge` to one value (`rw/root_worker_physical.py:93-94`). The child-authority producers set both image fields from `p.cfg['helper_sha256']` and both challenge fields from `self.held['challenge']` (`rw/protected_resource_runtime.py:887-888`; `rw/protected_scoped_supervisor_v3.py:190-191`). `peer` and `held_peer` come from distinct sources. | Read | This is the same OB-030 vacuity as DF-4, in the classifier's pairs. It is covered by tagged records in `Custody_V2` (§4.2 P8–P11, §5.2). The original `Custody` is unchanged. | §4.2, §5.2 |

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
| I9.7 deduplication as an unbounded-growth remedy (v1:1112-1113, 1128) | RC-04 | §6.8 |
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
- Bash was used for read-only inspection: `cat`, `sed -n`, `grep`, `find` (including `-printf`), `ls`, `sha256sum`, `wc`, `head`, `tail`, `awk` (printing only), `cut`, `cat -A`, `sort`, `uniq`, `tr`, `echo`, `printf`, `test`, `cd`, shell variables and `for` loops. Short Python scripts, run with `python3 -c` or from a quoted here-document on standard input, read files as text, JSON or `ast` and printed to standard output. Python's `difflib` was used for text-line comparisons.
- Some of these are outside the brief's literal list of commands. They are read-only and are disclosed in AUTHOR-NOTES §5.
- No output was redirected or teed to a regular file. Two forms of output redirection were used:
  - `2>&1`, which merges standard error into standard output, in 4 commands (J18).
  - `2>/dev/null`, which discards standard error, in 6 read-only commands with 7 occurrences (J16, J17). Writing to the null device stores nothing, but it is literally a redirect to a file, so it is disclosed as a deviation (AUTHOR-NOTES §5).
  - An earlier draft of this paragraph said five commands and six occurrences. The counts above come from a read-only audit of this agent's own session record.
- Here-documents (`<<'PY'`) pass script text on standard input. They redirect input, not output.
- No file was created, moved, copied, deleted or changed by Bash or Python.
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
- Every derived number is one of the JACKAL `jackal_exact` calls J01–J18 recorded in `jackal.json`. Each returned `status=exact`, `formal=false`, lane `rat`, evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, with these non_claims, verbatim:
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
  - Composition takes S5's `core/worldline-recovery.ads` (sha256 `09f82299af37c975b409596fb342f1ef961e309354765cde966189f23a2ee3fe`), never the lane's copy (`ab9555faadd4b46d294a09d8d74495b75ef017497acde9290849cf005aed921a`). CAPI3 §0 describes S5's copy as carrying packet 01's change under the lead-recorded approval `W/work/claude-lead-v2/approvals/optional-marker-api-v1/approval.json`. That was not re-verified here.
  - This lane alters no Optional_Marker API and needs none altered. The review's statement that Optional_Marker is not approved and the later approval record are both outside this lane to reconcile (AUTHOR-NOTES §2).
- **G-11. Lock discipline.** Locks follow §13.1 (SL-0).
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace and socket semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14, §16).
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
- **CD-8.** The first `RESULT_CAPTURE` boundary is write-once (`rw/protected_operations.py:780-785`). Later captures are additive report boundaries. Two already exist: `RETURN_REPORT` (`:763-764`) and `ROOT_WORKER_FINAL_RESULT_CAPTURE` (`rw/protected_root_worker.py:300-303`). Settlement uses the retained first capture.
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

---

## 4. Seam 7: canonical comparable source records, plan/cost crosswalk, enforcement correspondence (RC-02, D-7a)

Current draft state and quoted requirements are carried by slices **B-S7-CUR** (with replacement R-3) and **B-S7-REQ** (Appendix C).

### 4.1 Tagged source-record grammar (additive SPARK unit `Worldline.Source_Record`; DESIGN)

```ada
type Side is (Observed, Expected);
type Source_Domain is (Listener_Bind, Descriptor_Endpoint, Loader_Exec_Record, Owner_Plan_Sources,
   Host_Process_Exec, Helper_Exe_Read, Crosswalk_Helper_Digest, Worker_Process_Read,
   Crosswalk_Coordinator_Plan, Custody_Running_Event, Scoped_Running_Commit, Store_Meta_Read,
   Startup_Genesis_Store, Namespace_Read, Helper_Held_Frame, Channel_Peer_Read,
   Dispatch_Ticket, Helper_Ticket_Echo);
type Source_Record is record
   Domain : Source_Domain; Which : Side;
   Raw, Payload, Container, Anchor : L.Identity;   -- spans in the shared arena
end record;
```

- **`Domain_Allowed (Field, Which, Domain)`** is a static total table, one row per pair in §4.2.
- **`Payload_Extracted (Data, R)`** is a native per-domain extraction relation: the payload is the canonical comparable encoding (CCE) derived from `Raw` by that domain's grammar. Raw records use a fixed producer framing, `WL-SRC-V1`: magic, domain, field, side, value length, value, evidence length, evidence. Extraction is a total native parse of that framing plus the per-domain rule in §4.2.
- **`Container_Bound (Data, R)`** holds for expected-side domains whose container is owner-provisioned DATA (descriptor, owner plan, crosswalk, startup genesis):
  - `Anchor` equals the SHA-256 of `Container`, computed natively with the proved `Attest.SHA256` units already in the core;
  - `Raw` is a sub-span of `Container`.

  Observed-side anchors are custody-journal event identities. The native code checks only that they are valid and distinct. Their authenticity stays a producer obligation (P1:137).
- **`Pair_Valid (Data, Field, Obs, Exp)`** is the conjunction of:
  - `Obs.Which = Observed`, `Exp.Which = Expected`;
  - both domains allowed for the field and side, and `Obs.Domain /= Exp.Domain`;
  - `Payload_Extracted` for both;
  - `Container_Bound` for expected-side container domains;
  - `L.Same (Data, Obs.Payload, Exp.Payload)`;
  - both anchors valid, `not L.Same (Data, Obs.Anchor, Exp.Anchor)` and `not L.Same (Data, Obs.Raw, Exp.Raw)`.
- **What each copy attempt meets:**
  - Copying one record to both sides fails on side, domain or raw distinctness.
  - Relabelling a copy fails the other domain's grammar, or the container hash of the expected side.
  - One-side corruption fails payload equality.
- **What the native code cannot establish.** A forged but well-formed observed record stays a producer-authenticity obligation, which is the OS-correspondence workstream. No native claim is made about it.

### 4.2 Per-pair mapping (producer, raw record, CCE, custody)

Root_Controller pairs (`core/worldline-resource_child_execution.ads:19,53-59`):

| # | Pair | Observed side: producer → raw → anchor | Expected side: producer → raw → container | CCE (extraction) |
|---|---|---|---|---|
| P1 | owner_endpoint | Front at bind: `getsockname` bytes of the listening socket plus `stat` (dev, ino) of its path (`rw/protected_root_endpoint.py:36`) → custody-journal event | Descriptor `endpoint.path` (`rw/protected_startup.py:192-197`), carried in the crosswalk entry → descriptor bytes, whose digest the custody genesis binds as `startup_descriptor_sha256` (`rw/root_worker_journal.py:47`) | Absolute path bytes. Observed extraction is the `sun_path` prefix of the raw `sockaddr_un` at the reported length **[unverified reasoning, K-13]** |
| P2 | source_lease ↔ expected_source_lease | The worker's early-loader executed-file record (role, path, sha256), reported on the authenticated custody channel → custody event | Owner plan `sources` (`rw/protected_root_worker.py:109-114`) → plan bytes, bound by the genesis `owner_plan_sha256` (`rw/root_worker_journal.py:48`) | Sorted (path bytes, sha256) restricted to SOURCE and EXECUTABLE roles |
| P3 | source_lease ↔ process `P_source_lease` (`.ads:59`) | Host-side capture of the worker through host procfs and the worker pidfd: interpreter executable digest and mapped executables (`rw/root_worker_process_capture.py`) | The P2 loader record, a distinct producer | The intersection both can observe (interpreter and extension digests). Exact definition OPEN for spec slice S2 (RQ-5). Today's caller-provided value (`rw/protected_root_observation.py:74-76`, `:121`) is withdrawn. |
| P4 | worker_image ↔ expected_worker_image | sha256 of `/proc/<helper>/exe` read through the transferred host procfs, with pidfd pinning: fdinfo Pid checked before and after → custody event | Crosswalk helper-image digest → crosswalk container | sha256 bytes. The helper (supervisor) image keeps its distinct meaning. It joins `Facts.Helper_Image` (`.ads:87`). |
| P5 | handler_plan ↔ expected_handler_plan | Raw `/proc/<worker>/cmdline` and the `/proc/<worker>/exe` digest, through host procfs with pidfd pinning | Crosswalk coordinator plan: interpreter digest, entry, argv template | (exe digest, argv). The trailing custody-descriptor argument appended by the helper (`native_root_worker_supervisor_v1.c:289-290`) is excluded from the CCE and kept as an observed-only fact bound to the custody FD identity. Template instantiation is native. |
| P6 | running_event ↔ expected_running_event | Root custody-journal `RUNNING` record | The scoped committed `RECORD_RUNNING` packet and reply (scoped service committed history) → committed event digest | (reservation, planned unit, actual unit, cgroup, invocation, ledger head after commit). The two records do not share an encoding (review §2 seam 7). |
| P7 | store_genesis ↔ expected_store_genesis | StateStore meta `protectedStoreGenesis`, read under the store lock (`rw/protected_scoped_resource_runtime.py:116-118`) → store snapshot digest | Startup genesis `store.identity` (`rw/protected_startup.py:231-233`) → genesis bytes (`lease.genesis_raw`) | Identity string bytes |

Classification `Facts` pairs (`core/resource_observation_classification.ads:81-84`; observation N-10). These are enforced in `Custody_V2` (§5.2). The original `Custody` is unchanged.

| # | Pair | Observed side | Expected side | CCE |
|---|---|---|---|---|
| P8 | Namespace ↔ Held_Namespace | The namespace inode identity read now through host procfs and the namespace-init pidfd | The namespace identity in the helper's raw HELD frame, retained in the HELD custody event | (dev, ino) |
| P9 | Peer ↔ Held_Peer | `SO_PEERCRED` of the supervisor channel, read now | The HELD frame's peer | Raw ucred bytes. The producers are already distinct (`rw/root_worker_physical.py:93`). |
| P10 | Helper_Image ↔ Expected_Helper_Image | The helper `/proc/<pid>/exe` digest, as in P4 | Crosswalk or owner-configuration helper digest | sha256 |
| P11 | Challenge ↔ Held_Challenge | The ticket echoed by the helper in its HELD and CLOSED frames (`.c:359`) | The dispatch ticket generated by the front and journaled in `DISPATCH_INTENT` (`rw/protected_root_resource.py:65-66,80`) | Ticket bytes |

### 4.3 Native enforcement in additive versions

- **`Root_Controller_V2`.** Each of P1–P7 is a `(Obs, Exp)` pair of `Source_Record`s. It also carries an anchor roster: descriptor, owner-plan, crosswalk and genesis digests.
- **`Controller_Valid_V2`.** Every non-pair conjunct of `Controller_Valid` (`.ads:48-52`), reproduced literally, plus `Pair_Valid` for P1–P7. The original `Controller_Valid` is unchanged and keeps deciding V1 inputs.
- **`Root_Controller_Holds_V2` and `Root_Admission_V2`.** These are the originals with V2 controller records. `Original_Root_Holds` is unchanged.
- **ABI.** New versioned exports through the sole boundary (§14.3). No original export's code, meaning, layout or caller protocol changes. D2R C-ABI therefore triggers no operator item. A change to any original public API would be D-7a (operator) and is not proposed.
- **Re-review.** Per the D-7a owner, the additive grammar needs a re-review of the child-authority surface by an independent actual gpt-6.1-sol reviewer.

### 4.4 Dynamic plan and cost crosswalk

**Table.** `worldline.protected-root-operation-crosswalk-v1`, owner-provisioned (D-2a), bound by the v2 descriptor `files` and the early envelope (§11.2). It has one entry for each of:
- every original operation in the `OPS` roster (`rw/operation_authority_kernel.py:8`);
- every owner route (`owner.retry`, `owner.adopt`, `owner.recover`, `quarantine.resolve`);
- every follow-up right of `policy['broker']['followup_plans']` (`rw/canonical_full_broker.py:202-217`).

**Entry content:**
- the **digest** of the original plan (`policy['plans'][op]` or `followup_plans[right]`: `cost_key`, `parent`, `launch`). It binds the plan and never copies or replaces it;
- the coordinator plan: entry, envelope, interpreter, loader, argv template, `worker_policy`;
- the helper-image digest;
- the child adapter plans;
- the physical catalogue key;
- the header DATA selections, for example `/usr/include/asm-generic/socket.h` for `SO_PEERPIDFD` (`rw/root_worker_host_peer.py:14-17,32-33`).

**Rules:**
- **Dynamic binding.** Follow-up entries are chosen at run time by `(operation, right, event_id)` through the unchanged `followup_plan`. The crosswalk binds the right's plan digest. The event binding stays the broker's.
- **One source of plan truth.** `pre_effect`, `launch_root_worker`, `resource_launch_material` and `machine_admission` all read the same entry. That removes the dual policy source of seam 1 and the root `cost_key` equality refusal (`rw/protected_root_resource.py:40-41`) without weakening either comparison.
- **Magnitudes unchanged.** The reservation kind and amount still come from the catalogue `costs[cost_key]` of the operation's own plan (`rw/protected_scoped_resource_runtime.py:374-381`, `:392`). The crosswalk adds no cost, caps no magnitude and narrows no case. Two operations with different cost keys both dispatch.
- **Absence** of an entry is a named refusal that keeps the obligation OPEN. Nothing is defaulted.
- **Native cost.** Container hashing and extraction add checked-build native cost. That is a D2 item and stays OPEN.

### 4.5 Real enforced capacity correspondence (OB-176)

`Enforcement_Corresponds (Data, Row, Projection, Readback, Policy, Floors)` is an additive native predicate over:
- the manager properties and cgroup control files read back after HELD (observed, raw);
- the selected plan's original `ResourcePolicy`. Its fields, observed in `rw/admission.py:76-85`, are `memory_max_bytes`, `memory_high_bytes`, `memory_swap_max_bytes`, `cpu_quota_percent`, `cpu_weight`, `tasks_max`, `disk_growth_max_bytes`, `timeout_seconds`, `max_concurrent_workloads` and `enforcement`;
- the original admission floors (`rw/config.py:192-195`).

Its conjuncts:
- **E1.** Each enforced control equals the plan's policy value under the kernel's and manager's documented representation, for example page granularity of memory limits **[unverified reasoning, K-8]**. The relation is exact correspondence, not `≤`. A representation difference is a measurement question to settle before acceptance. It is never handled by a silent tolerance, and never by a refusal of an originally accepted plan (G-2).
- **E2.** Where the catalogue role is `MEMORY_BYTES`, the enforced hard memory limit is at most the reservation's projected amount, so the reservation bounds use.
- **E3.** Machine admission accepted at DISPATCH and at GO under the original floors and ledger withholding (`observe_ledger` and `observe_policy` natively, `rw/protected_scoped_resource_runtime.py:673-695`). The withholding includes every outstanding held capacity, so the reserved amount is actually kept available.
- **E4.** Concurrency, disk growth and timeout are enforced by their original mechanisms.

E2 and E3 together, not ceilings alone, are the design answer to "so it can finish". The original policy has no cgroup minimum or low protection field (observed), and v2 adds none. The review's term "minimum/low" is mapped to the original admission floors and `memory_high_bytes`. RQ-4 asks the reviewer to confirm that mapping. Nothing is invented and no cap is added.

### 4.6 Additive controls

- Corrupting one producer of any of P1–P11 gives `Controller_Refused`, or Unknown classification for P8–P11.
- The same record copied to both sides is refused, with and without relabelled tags.
- A relabelled copy whose container hash does not match is refused.
- Distinct-source equal payloads give the positive.
- An operation without a crosswalk entry gives a named refusal.
- Two operations with different cost keys both dispatch.
- Enforced `MemoryMax` above the projection is refused (E2).
- A policy value differing from the readback is refused (E1).
- A changed header digest is refused.
- Every original `Controller_Valid` vector, run against the unchanged V1 unit, still passes.

### 4.7 Dependencies, authority and review questions

- **Dependencies.**
  - **S2** (this grammar, `Root_Controller_V2`, `Controller_Valid_V2`) uses existing types only. Observed anchors are identity spans; their meaning as custody events comes from S9's callers, not from S9 types.
  - **S3** (crosswalk schema and `Enforcement_Corresponds`) depends on S2.
  - **S11** binds S3's table in the v2 descriptor.
  - Native enforcement and exports depend on G-CAPI.
- **Authority.** The schemas and predicates are lead work. Provisioning the crosswalk is an operator act (D-2a).
- **RQ-4.** Is mapping "minimum/low" to the original admission floors and `memory_high_bytes` correct?
- **RQ-5.** How should P3, the process source-lease pair, be defined exactly?

---

## 5. Seam 5: dynamic child dispatch with an additive delegation/custody successor (RC-03, D-5a, D-5b)

Current draft state and quoted requirements are carried by slices **B-S5-CUR** and **B-S5-REQ** (Appendix C).

### 5.1 Why a Python change cannot work (STATIC_REASONING; review F-12)

1. The native `Custody` requires `Text (F.Manager_Delegate, "no")` (`core/resource_observation_classification.ads:95`). `Live_Holds` and `Reaped_Holds` both require `Custody` (`:104`, `:109`).
2. The scoped classifier uses those holds (`core/resource_scoped_run_ledger.ads:241-243`), and scoped `Native_Valid` ties `Observed` to `Classify` (`:256-257`).
3. `Root_Controller_Holds` requires the root row to be observed `Live` (`core/worldline-resource_child_execution.ads:78`).
4. A delegated root unit therefore classifies `Unknown`, and root admission refuses.
5. Today the root unit is launched with `--property=Delegate=no` (`rw/protected_root_resource.py:70`). Changing a HELD expectation in Python does not change this native conjunction.

### 5.2 Additive native successor (separate review slice S4; DESIGN)

**New unit `Resource_Observation_Classification_V2`:**
- **`Facts_V2`** = `(Base : K.Facts; Pairs : P8–P11 tagged records (§4.2); Delegation : Delegation_Facts)`.
- **`Delegation_Facts`**, all raw observed spans:
  - the delegation-record digest selected by the owner plan;
  - the manager `Delegate` property;
  - the boundary (unit) cgroup path, its `cgroup.subtree_control` and its control files (outer limits), with their owner and mode;
  - the coordinator's `/proc/<pid>/status` capability, `NoNewPrivs` and `Seccomp` lines;
  - the coordinator's `mountinfo` cgroup entries and cgroup-namespace identity;
  - the helper-successor version;
  - the child-request journal head.
- **`Custody_V2 (Data, Item, F2, Selected)`** is the conjunction of:
  - every conjunct of the original `Custody` (`:80-95`) **except** its four pair equalities (`:81-84`) and the `Manager_Delegate` text test (`:95`), reproduced literally;
  - `Pair_Valid` for P8–P11;
  - if `Selected` is absent, `Text (Manager_Delegate, "no")`, exactly as the original; otherwise `Delegated_Custody (Data, Item, F2, Selected)`.
- **`Delegated_Custody`** is the conjunction of:
  - `Text (Manager_Delegate, "yes")`;
  - `Same (Delegation.Record, Selected)`;
  - the boundary cgroup is the row's unit cgroup;
  - `Enforcement_Corresponds` on the boundary's outer limits (§4.5);
  - `Coordinator_Contained`, the P-CE1 and P-CE2 observations (§5.3);
  - the original cgroup type, owner and write-bit conjuncts, unchanged and **[unverified reasoning, K-8]** under delegation.
- **`Never_Holds_V2`, `Live_Holds_V2`, `Reaped_Holds_V2` and `Classify_V2`** are the originals' structure with `Custody_V2`.

**Selection.** `Selected` comes from an authenticated record, never from a caller flag. The operation's crosswalk entry (§4.4) names a delegation-record digest. The row's dispatch fact `F.Dispatch` must bind that entry through a `Source_Record` whose container is the crosswalk. A row without a delegation record is decided by the no-delegation branch, which is the original model plus pair validity.

**New unit `Resource_Scoped_Run_Ledger_V2`:** `Classify_Reference_V2`, `Native_Valid_V2`, `Decision_Reference_V2` and `Check_V2` are textually the originals (`:232-268`, `:398-457`), with `Facts_V2` and `Classify_V2` substituted. `Shape`, `Physical`, `Contained`, `Current_Valid`, `Advance_Valid` and `Ordinary_Reference` are reused unchanged.

**New unit `Worldline.Resource_Child_Execution_V2`:**
- `Root_Controller_Holds_V2` and `Root_Admission_V2` use the V2 controller (§4.3) and `Native_Valid_V2`.
- `Parent_Holds`, `Child_Holds`, `Task_Request_Holds`, `Process_Ancestry`, `Namespace_Ancestry`, `Original_Root_Holds` and `L.Parent_Supports` are **reused unchanged**.
- Physical containment of a child in the root is the original `Cgroup_Inside (Parent.Cgroup, Child.Cgroup)` inside `Parent_Supports` (`resource_run_ledger.ads:252-253`).

**Compatibility lemmas (stated, not proved):**
- **L-V2-1.** For inputs with no delegation record and distinct-source-valid pairs, `Classify_V2 (Facts_V2) = Classify (Base)` and `Check_V2 = Check`. Rows whose pair fields were filled by self-copy, the OB-030 defect, are refused. That is the OB-030 target, not an accepted case.
- **L-V2-2.** `Root_Admission_V2` with a V2 controller whose pairs are valid gives the same status as `Root_Admission` on the V1 projection.

**Preserved unchanged:**
- the original no-delegation model and all original units, which still decide every v1 and actor V3 row;
- `Parent_Supports`, `Original_Holds`, equal and different workload cases, optional root and child world facts, actor credentials, and original stdin/EOF;
- the grammar rule that distinct operation and reservation identities do not justify inventing workload inequality (P1:97).

**Child rows, the primary design (DESIGN-5A).** The helper successor forks one **per-child sub-helper** outside the coordinator's namespaces.
- The sub-helper creates the child's PID namespace and init, is the child's helper for `Helper_Wait`, and terminates after the child's CLOSED and ECHILD.
- So the original Live and Reaped rules, with `Custody_V2`, apply to child rows unchanged.
- The alternative, child-specific holds rules, is needed only if per-child sub-helpers are rejected. A single long-lived helper's pidfd stays LIVE while the root runs, so the original `Reaped_Holds` (`Helper_Wait = "PIDFD_TERMINAL"`) could never classify a nested child as `Reaped`.

### 5.3 Coordinator enforcement argument (for D-5a; every item **[unverified reasoning]** until measured)

The coordinator is the root worker. `Controller_Valid` requires effective UID 0 (`.ads:51`), so ownership-based protection cannot apply. The argument rests on what the coordinator can *reach*, not on DAC.

| Item | Property | Mechanism (DESIGN) | Observation consumed natively | Lab measurement (operator) | Negative control |
|---|---|---|---|---|---|
| P-CE1 | The coordinator cannot change any outer ceiling or guarantee. | The coordinator's mount namespace exposes cgroup2 read-only at its cgroup-namespace root, or not at all. Its capability bounding set excludes `CAP_SYS_ADMIN`, so it cannot remount, mount or unshare. `no_new_privs` is set. All cgroup writes are made by the helper successor outside the coordinator's namespaces. | `Coordinator_Status_Raw`, `Coordinator_Mountinfo_Raw`, `Coordinator_Cgroup_Ns` | K-10: read-only cgroup2 with no `CAP_SYS_ADMIN` prevents writes and remount | A writable cgroup mount, or `CAP_SYS_ADMIN` present → `Delegated_Custody` false |
| P-CE2 | The coordinator cannot move itself or descendants out of the subtree. | No coordinator write to any `cgroup.procs` (P-CE1). Children are created only by the helper via `clone3` with `CLONE_INTO_CGROUP` into leaves under the boundary. | Child cgroup paths are `Cgroup_Inside` the boundary (original predicate). Each child's `/proc/<pid>/cgroup`. | K-9: `CLONE_INTO_CGROUP` with nested PID namespaces. K-11: `cgroup.procs` migration rules. | A child outside the subtree → `Parent_Supports` false |
| P-CE3 | The subtree's total consumption is bounded by the root reservation. | Outer limits sit on the boundary cgroup, from the crosswalk (`Enforcement_Corresponds`). Hierarchical enforcement bounds every descendant. | `Outer_Limits_Raw` | K-8: Delegate=yes semantics; hierarchical limits; systemd non-interference with a delegated subtree | An outer limit above the projection → refused (E2) |
| P-CE4 | Actors never receive coordinator custody FDs or root rights. | The helper-mediated child exec uses an explicit FD roster, with every other descriptor close-on-exec. The actor runs with the original actor credentials (V3 lineage) inside the sub-helper's namespaces. | Child process ancestry and credentials (original `Process_Ancestry`). FD-roster record. | K-12: bwrap under a nested PID namespace with `/proc` remount | A leaked FD in the child → refused by the FD audit control |

`Delegate=yes` is still proposed for the root worker unit, so that systemd does not manage or migrate the helper-created subtree **[unverified reasoning, K-8]**. The coordinator's inability to write comes from P-CE1, not from delegation ownership. Installing the delegation policy and running any privileged lab action is operator work (D-5a).

### 5.4 Helper successor (D-5b)

- **Lineage.** `protected-root/native_root_worker_supervisor_v2.c` is a separately versioned successor. The V1 root supervisor, the V3 actor helper, the helper-stdin lineage and all their controls are retained unchanged. V3 is not extended in place.
- **Protocol.** The coordinator first obtains and journals the native child decision: `Task_Admission` (`.ads:248-257`), then `Decide = Child_Ready_Conjunction` after measurement. It then sends a child-creation request on a dedicated inherited channel with:
  - the task id;
  - the child reservation;
  - the child plan digest;
  - the leaf name;
  - limits derived from the child reservation through the crosswalk;
  - the parent namespace FD.

  The helper creates the leaf cgroup and its sub-helper, which creates the child namespace and init. It returns a pidfd and raw observations, and later HELD, CLOSED and ECHILD frames per child.
- **Exact surfaces:**
  - the input/native/source union;
  - ABI, protocol, argv, env, stdin and EOF, identical to the V3 actor helper for the actor itself;
  - an FD inheritance audit;
  - authentic ACK, ECHILD, waits and drains.
- **Retained obligations.** The C body is unproved native code with cost obligations (OB-048 class), and gets no proof credit. Installation and privileged execution are operator work (D-5b).

### 5.5 Dispatcher (DESIGN; v1 seam 5 items carried in substance, corrected)

1. **Interim.** On the root route, workload operations keep the named OPEN refusal (G-2). Their positive controls stay required.
2. **Worker-side dispatcher.** It replaces the runner's launch only under the root worker. The runner's capture (`rw/runner.py:649-656`) is unchanged.
   1. **Durable TaskIntent** holding:
      - the task id;
      - the complete original workload capture: adapter, context, SandboxSpec, argv, mission, stdin and EOF, env, world, instance, check and finalization;
      - the world ancestry;
      - the child plan from the crosswalk.
   2. **Child RESERVE.**
      - `new_row.parent` is the root reservation.
      - `operation` is the task id, which differs from the root operation and reservation.
      - Capability, grant use, owner and provenance are the root's.
      - The workload follows the original grammar.
      - No extra A use.
   3. **Native `task_reservation`** (`Task_Admission`: `S.Check_V2 ∧ Task_Request_Holds`), then a scoped commit.
   4. **Physical nesting** per §5.3, with the helper successor per §5.4.
   5. **Before exec:**
      - actor credential measurement;
      - `K.Check` and `Child_Ready_Conjunction` (`.ads:194-208`);
      - a durable witness, then ACK, then GO;
      - the original stdin/EOF pump (actor stdin V4).
   6. **Closure.**
      - Nested CLOSED and ECHILD, outer waits and raw drains, then `RECORD_TERMINAL`, then release or charge.
      - The root settles only after every child (CD-9).
      - An unknown child keeps the root held.
   7. **Follow-up rights** go through the same path, using the broker's follow-up plans.
3. **Race.** Three children under one root, with the same grant and use.

### 5.6 Additive controls

Lab controls need the operator, and real actors need operator quota.
- Every original fork, race, simulate, ghost, prune and revalidate accepted control on the root route.
- Refusals for:
  - a child with a different capability or use;
  - a sibling unit;
  - a missing parent namespace;
  - a stale TaskIntent;
  - a copied ready flag;
  - a delegated row without a selected delegation record;
  - each P-CE negative in §5.3.
- A child OOM is contained, and is never PASS (OB-020).
- An unknown child keeps the root held.
- A race with three children.
- Follow-up rights, positive and denied. A committed return without post rights stays COMMITTED with effects skipped.
- L-V2-1 parity vectors: no delegation, distinct pairs.

### 5.7 Dependencies and authority

- **Dependencies:**
  - spec S4 depends on S2 (P8–P11 records) and S3 (crosswalk delegation record and `Enforcement_Corresponds`). Its callers, the child-request records, also depend on S9;
  - bodies depend on S1, S6 and S7;
  - the child-authority secondary (controls UNBUILT and UNRUN), actor stdin V4 and SL-0;
  - D1/D2 cost, which affects helper, wrapper and native runtime cost as well as the new units.
- **Lead work:** the dispatcher, helper source and native specs.
- **Operator work:** the root lab, systemd delegation, helper installation, model quota.
- **Actors:** real actors may only be the WORLDLINE actor, `gpt-6-luna` with high reasoning, inside a world through the existing Codex adapter.

---

## 6. Seam 9: native custody phase relation (RC-04, D-9a)

Current draft state and quoted requirements are carried by slices **B-S9-CUR** and **B-S9-REQ** (Appendix C), defects (a)–(i).

### 6.1 Mandatory native relation (additive SPARK unit `Worldline.Root_Custody_Phase`; slice S9)

- **Why it is mandatory.** Custody determines who may mutate state, so its transition legality is decided natively and Python obeys it (D-9a).
- **What it decides.** One append at a time. The inputs are the operation's latest committed custody record, the proposed record (operation, generation, sub-generation, prior head, phase, actor, cause, evidence heads) and the evidence spans.
- **Result.** `Ready`, or a named refusal of the append. A refused actor does not act.
- **Contracts.** `Global => null`, `Post => Legal'Result = Legal_Reference (…)`, `Always_Terminates`. There is no recursion over history. The decision needs only the latest record and the proposed one, because chain integrity is checked by the journal load (`rw/root_worker_journal.py:93-114`).
- **ABI.** Exported through the C-API v4 pattern (§14.3). Python callers carry the complete inputs.

### 6.2 Phase graph with exclusive branches

The owner of each phase determines who may mutate (CD-6). There are three exclusive pairs per generation g: (`CUSTODY_ACK`, `ABANDON`), (`REQUEST_INTAKE`, `REQUEST_ABANDON`) and (`DRAIN_INTAKE`, `DRAIN_ABANDON`). The last two carry per-request and per-descriptor sub-generations.

| From | To | Actor | Required evidence (native inputs) |
|---|---|---|---|
| FRONT_OWNED | PREPARED | Front | RESERVED and `EFFECT_INTENT` committed: operation-journal head and native use observation |
| PREPARED | HELD | Front | Authentic HELD frame from the helper. Machine admission at DISPATCH. |
| HELD | RUNNING | Front | Native scoped `RECORD_RUNNING` committed |
| RUNNING | EXECUTION_NATIVE | Front | Native `ROOT_READY_CONJUNCTION` retained |
| EXECUTION_NATIVE | EXECUTION_ACK | Front | Before-exec witness and worker exec ACK |
| EXECUTION_ACK | HANDOFF_INTENT | Front | Custody frame intent |
| HANDOFF_INTENT | FRONT_CLOSE_INTENT | Front | No background owner. Acquisitions quiescent. |
| FRONT_CLOSE_INTENT | FRONT_CLOSED | Front | Owners closed. **Seed captured after close and after every retention append** (§6.4). |
| FRONT_CLOSED | TRANSFER_SENT | Front | All descriptors sent. Sending is not custody. |
| TRANSFER_SENT | CUSTODY_ACK | **Worker** | Intake native redecision `ROOT_READY_CONJUNCTION`. Seed equals current under the transferred OFDs. CAS on g. |
| TRANSFER_SENT | ABANDON | **Front** or Reconciler | CAS on g. No `CUSTODY_ACK(g)` committed. |
| CUSTODY_ACK | WORKER_OWNED | Worker | The same CAS transaction. Recorded once. |
| ABANDON | FRONT_RETAINED_ESCROW | Front | Only now may the front stop the worker. The CAS guarantees the worker never mutated in g. **No path from ABANDON reaches WORKER_OWNED.** |
| WORKER_OWNED | ORIGINAL_RESULT | Worker | Original handler result captured once (CD-8) |
| WORKER_OWNED, ORIGINAL_RESULT | REQUEST_TRANSFER_INTENT(r) | Front | Raw request, socket and host records journaled (§8.2, §9.4) |
| REQUEST_TRANSFER_INTENT(r) | REQUEST_INTAKE(r) / REQUEST_ABANDON(r) | Worker / Front | Exclusive CAS on r |
| WORKER_OWNED | DRAIN_FREEZE(d) → DRAIN_INTAKE(d) / DRAIN_ABANDON(d) | Front, then Worker / Front | §7.3 protocol, exclusive CAS on d |
| ORIGINAL_RESULT | HANDLER_TERMINAL | Worker | Final result capture, failures, owner state |
| HANDLER_TERMINAL | WORKER_RELINQUISH | Worker | Owners closed. Native root material retained. |
| WORKER_OWNED … WORKER_RELINQUISH, FRONT_RETAINED_ESCROW | CLOSED_NS, CLOSED_OUTER, CLOSED_RAW (each once, any order) | Collector | Helper `CLOSED … ECHILD` frame (`native_root_worker_supervisor_v1.c:359`). Outer wait. Pidfd terminal states. Complete raw drains. |
| all three CLOSED_* | CLOSED_WITNESS | Collector | Native `REAPED` and `CONSISTENT_SNAPSHOT` |
| CLOSED_WITNESS | PHYSICAL_SETTLED | Collector or Reconciler | Native `RECORD_TERMINAL` and `RELEASE_HOLD`/`CHARGE_BUDGET` committed (CD-5) |
| PHYSICAL_SETTLED | HISTORICAL_SETTLEMENT | Collector | Use settled natively (`SETTLE_USE`) if a terminal and retained result exist. Otherwise native `QUARANTINE_USE` (CD-2). Both are legal. |
| HISTORICAL_SETTLEMENT | FRONT_RECONSTRUCTION | Collector | Fresh owners constructed through v2 startup with the escrow (§6.5) |
| FRONT_RECONSTRUCTION | FRONT_OWNED (g+1) | Front | The fresh front binds |
| any non-terminal | UNKNOWN(cause) | The current phase owner or Reconciler | Failed durable capture, EOF without CLOSED, a deadline, crash evidence |
| UNKNOWN(cause) | the phase native evidence determines | **Reconciler only** | Authentic durable evidence redecided natively. Never EOF or a deadline alone. |

Invariants of the relation. These are proof obligations, all OPEN:
- **INV-C1.** One owner per generation.
- **INV-C2.** ABANDON(g) has no successor WORKER_OWNED(g).
- **INV-C3.** A worker mutation is legal only while the latest committed phase is worker-owned in its CUSTODY_ACK generation.
- **INV-C4.** PHYSICAL_SETTLED needs CLOSED_WITNESS on the root route.
- **INV-C5.** UNKNOWN is left only by the Reconciler.

### 6.3 Durable CAS generations and lost-ACK resolution

Today's `append` (`rw/root_worker_journal.py:123-140`) is serialized by `BEGIN IMMEDIATE` but is not conditioned on a caller's expectation (observation N-7).

**The v2 append protocol** runs inside one SQLite `BEGIN IMMEDIATE` transaction:
1. Load the chain (unchanged verification).
2. Require that the head equals the expected prior head, the operation's latest phase equals the expected phase, and its generation (and sub-generation) equal the expected values.
3. Obtain the native `Legal = Ready` for the proposed record. The record carries pre-commit observation digests: for CUSTODY_ACK, the intake capture; for ABANDON, the absence of a `CUSTODY_ACK(g)` in the loaded chain plus the worker pidfd state.
4. Insert. Update the head.
5. Read back and redecide natively.
6. Commit with `synchronous=FULL`, as today.

| Case | Durable state | Resolution, with no second mutation |
|---|---|---|
| The worker committed `CUSTODY_ACK(g)` and crashed before sending the ACK message | CUSTODY_ACK(g) | The front reads the journal: WORKER_OWNED. No stop. A dead worker goes to the collector. |
| The ACK message was lost | CUSTODY_ACK(g) | As above. |
| No ACK committed, worker alive | TRANSFER_SENT(g) | The front may CAS `ABANDON(g)`. The worker's later `CUSTODY_ACK(g)` fails its CAS, so the worker refuses intake, closes its received descriptors and exits without mutation. The front stops a worker only after ABANDON commits. |
| The worker crashed before ACK | TRANSFER_SENT(g) | `ABANDON(g)`, then physical collection. |
| ACK and ABANDON race | The first commit wins | The loser sees a CAS refusal and does not act. |
| The front crashed after TRANSFER_SENT | TRANSFER_SENT(g) or CUSTODY_ACK(g) | The startup reconciler decides (RT-9, RT-10, §11.5). |

### 6.4 Seed freshness (defect 9(a), observation N-8)

- **Read-only capture paths.** Capture paths become read-only. The operation-journal `ACK` append that `capture_execution` makes inside the capture (`rw/canonical_actor_execution.py:125-127`) moves to an explicit retention step that runs **before** the seed. `RootControllerCapture` appends nothing while capturing. `retain_root_native` runs after the decision and outside the seed window.
- **The seed** is the capture taken inside `transfer()` after `close_front_owners` and after every retention append. The frame binds:
  - the operation-journal head;
  - the scoped ledger head;
  - the store snapshot digest;
  - the custody-journal head before `TRANSFER_SENT`;
  - the OFD identities.
- **Protection through close and receive.** Between the seed and intake, the front's owners are closed and the escrowed OFD locks are exclusive, so no other writer exists **[unverified reasoning, K-6]**. Intake compares the seed with current state under the transferred OFDs (`same_logical_state`; custody SQLite is excluded as today, `rw/root_worker_current_state.py:75-115`). The custody journal is compared by generation chain, not by equality.

### 6.5 Reconstruction through the escrowed lock (defect 9(b))

- The fresh `RootWorkerFront` takes an exact-type `ClosedFrontEscrow` parameter and opens `RootCustodyJournal (…, preheld => escrow.claim (lock_path))`. The lock path is in the escrow roster (`rw/root_worker_custody.py:113-115`).
- The old journal object closes only after the fresh front binds.
- A new `os.open` of the lock path, which fails with `LOCK_NB` (`rw/root_worker_closed.py:164` → `rw/protected_root_worker.py:117-118` → `rw/root_worker_journal.py:59-62`), is never used during reconstruction.

### 6.6 EOF, deadlines and stops (defects 9(c), (d), (e))

- **EOF.** `poll_closed` distinguishes EOF from "no data yet". EOF without CLOSED records `UNKNOWN(ROOT_CHANNEL_EOF_WITHOUT_CLOSED)`, deregisters the descriptor so it is never re-armed (no spin), and continues on pidfd readiness and manager observation.
- **Deadlines.** Every blocking `accept`, `recvmsg` and wait carries a deadline joined to pidfd and manager state. Expiry records `UNKNOWN(DEADLINE_…)` with holds retained, and collection resumes later from durable state. A deadline never kills or settles the workload: the workload's own original `timeout_seconds` mechanism is unchanged. Deadline values are owner-plan parameters and affect only when UNKNOWN is recorded.
- **Stops.** `retain_and_stop_unknown` stops a worker only after `ABANDON(g)` commits. When `CUSTODY_ACK(g)` exists there is no stop.

### 6.7 Independent physical collection (defect 9(f))

- The collector runs three independent awaits: the handler terminal, CLOSED with the outer wait, and the raw drains.
- The escrow successor requires only the physical three. Today's `ClosedFrontEscrow` requires `handler_terminal` (`rw/root_worker_closed.py:27`).
- A missing terminal makes the U outcome uncertain, with native `QUARANTINE_USE` when needed (CD-2). Physical REAPED is still recorded, and P settles natively (CD-5). K4 decides U.

### 6.8 Lossless acyclic retention (defect 9(g))

- **Blob table** in custody journal v2: `blobs (sha256 TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK (…), bytes BLOB NOT NULL)`. Events reference blob digests. Bytes are hashed by streaming, not embedded in records.
- **Snapshot closure.** A state capture is the set of provisioned-state files, store files and non-custody journals, **excluding** the custody journal itself (its head digest is recorded instead) and the blob store.
- **Acyclicity.** Blobs contain only raw observed bytes, never events or journal content. No blob references another, so reconstruction is event → digests → bytes.
- **Change-only.** `intact()` and `claim()` re-append only when the captured state digest changes.
- **No claim.** No OOM, size or cost claim is made. A smaller encoding or deduplication does not establish an OOM remedy (P1:101). Growth is observed later, in the lab.

### 6.9 Lingering units and detached tasks (defects 9(h), (i))

- After CLOSED_WITNESS, an owner-plan-selected unit reset is recorded as factual cleanup, never as terminal authority.
- A durable registration intent precedes detached-task creation. If registration fails, the task is never created, so nothing needs cancelling (`rw/daemon.py:115-121`).

### 6.10 Crash-point table (selected rows; the complete table is a spec deliverable of slice S9)

| Crash after | Durable state | Legal recovery | Automatic or owner |
|---|---|---|---|
| PREPARED, before HELD | Root row RESERVED or LAUNCH_INTENT; no HELD | Never-launched classification: release (CD-5). Use per §11.5. | Automatic (native) |
| HELD or RUNNING, front alive | Row RUNNING, live slot | Continue | — |
| HANDOFF_INTENT, before FRONT_CLOSED | Front owners possibly partially closed | `UNKNOWN(FRONT_CLOSE)`. Reconciler. | Automatic when evidence is complete, otherwise owner |
| TRANSFER_SENT, no ACK | Generation g open | `ABANDON(g)`, then collection | Automatic |
| CUSTODY_ACK, worker alive, front restarts | Worker holds the locks | The front's startup refuses to construct owners (locks held). Diagnostic state. The worker continues. | Automatic (RT-10) |
| CUSTODY_ACK, worker dead before ORIGINAL_RESULT | No result | Physical collection. U uncertain, so native quarantine and K4. | Physical automatic; U via owner |
| HANDLER_TERMINAL, worker dead | Result retained | Physical collection, then `SETTLE_USE` | Automatic |
| CLOSED_* partial | Some closure facts | Resume collection. No settlement before CLOSED_WITNESS. | Automatic |
| CLOSED_WITNESS, before PHYSICAL_SETTLED | REAPED witness | Native terminal plus release or charge | Automatic |
| REQUEST_TRANSFER_INTENT(r), no intake | Request r open | `REQUEST_ABANDON(r)`. The front serves or refuses r by original rules. | Automatic |
| DRAIN_FREEZE(d), no intake | Descriptor d frozen at P | `DRAIN_ABANDON(d)`. The front resumes reading at P. | Automatic |

### 6.11 Custody journal v2 and provisioning

- **Additive successor schema** `worldline.protected-root-custody-v2`, with full DDL:
  - PK, NOT NULL;
  - `CHECK (kind IN …)` and `CHECK (actor IN …)`;
  - UNIQUE `event_id`;
  - UNIQUE `(operation, generation, kind)` for the exclusive pairs;
  - a single-row head;
  - the blob table.
- **Genesis.** If a v1 custody journal exists, the v2 genesis binds its final head and sha256, and the v1 file stays as retained history. Prior chain and history are never replaced by a new genesis (review §4).
- **Provisioning** is offline, one-shot and operator-run (§11.3, D-2a). There is no implicit migration.

### 6.12 Additive controls

Lab and fault-campaign controls need the operator (D-9a).
- A crash at each phase boundary ends in the legal state of §6.10.
- A lost CUSTODY_ACK: no stop, WORKER_OWNED.
- An ABANDON race.
- Worker SIGKILL before the terminal: physical closure collected, U quarantined natively.
- Helper death: EOF, then UNKNOWN, with bounded CPU.
- Reconstruction succeeds with the preheld lock.
- Retention growth recorded per distinct state (observed, with no bound claimed).
- Half-transfer: the front keeps its escrow and the worker refuses intake.
- Pure native value fixtures of `Legal` (no root): each exclusive pair, every illegal edge, the UNKNOWN exits.

### 6.13 Dependencies and authority

- **Spec S9** depends on S8 (`Join` statuses consumed by `Legal`). It follows the §2 coupling rules as design constraints but uses no S6 types, because S6 depends on S9. Its PREPARED evidence uses identity heads supplied by S1's callers, not S1 types.
- **Bodies** depend on SL-0.
- **Schema change** needs operator provisioning (D-2a).
- **Fault campaigns** are operator work within the specialized-validation boundary (P1:163). A power-loss simulation is not power loss.

---

## 7. Seam 3: other-LIVE slot and drain custody transfer (RC-08, D-3a)

Current draft state and quoted requirements are carried by slices **B-S3-CUR** and **B-S3-REQ** (Appendix C).

### 7.1 Scope (D-3a)

- **What transfers.** The complete V3 slot custody of every non-terminal reservation that has an owned slot, plus the root slot itself.
- **No prior-terminal precondition.** Requiring other actors to terminate first would remove accepted cases (review §2 seam 3).
- **No cap.** There is no descriptor or row cap on the roster.
- **Rows.** Every non-terminal row keeps its origin. UNKNOWN keeps its holds.

The per-slot roster is observed in `rw/protected_scoped_supervisor_v3.py:16-18,482-525`:
- `connection`, the supervisor channel, which has a reader role;
- `listener`, if still open;
- `namespace_fd`, `namespace_pidfd`, `helper_pidfd`, `actor_pidfd`;
- `stdout_fd` and `stderr_fd`, with their asyncio read transports and `StreamReader` buffers (`:486-492`);
- `stdin_fd`, which has a writer role, with the input pump's progress;
- `credential_receiver`.

### 7.2 Producer retention, not transfer of reaping rights

- **Who reaps.** The waiting and reaping processes stay where they are. Observed in the root supervisor; the V3 helper lineage follows the same design:
  - the helper reaps its namespace init (`native_root_worker_supervisor_v1.c:357`);
  - the namespace init, a subreaper, reaps every descendant until ECHILD (`:253`, `:296-301`);
  - systemd reaps the helper, which is the unit's main process.
- **What the front holds.** The front is never a parent of these processes. It holds observation rights only: pidfds for poll and terminal-state reads, and channels for the helper's frames.
- **What moves.** Only these **observation and reader/writer roles** move. No reaping right is claimed, so no pidfd is treated as a transfer of reaping rights (review §2 seam 3).
- **Producers of the facts.** The genuine outer-wait and ECHILD producers are the retained helper and init. Their facts reach the current owner through the transferred channel role.

### 7.3 Role-transfer protocol per descriptor (DESIGN; every step is journaled under the §6.3 CAS with sub-generation d)

| Step | Actor | Action | Durable record |
|---|---|---|---|
| T1 FREEZE | Old owner (front) | Stop the reader or writer at a chunk boundary (pipes) or a message boundary (SEQPACKET channel): `transport.pause_reading()`, cancel and await the reader task, drain every byte held in the `StreamReader` buffer and any in-flight chunk. For the stdin writer, stop after a completed `write`, with W bytes written. | `DRAIN_FREEZE(d)`: descriptor id, role, spool position P or written count W, digest of the buffered bytes |
| T2 SPOOL | Old owner | Append every byte read before the freeze to the descriptor's durable spool (hash-chained chunks, `fsync`). P = total bytes durably spooled. Unread kernel-buffered bytes stay in the pipe for the next reader. | Spool head at P |
| T3 SEND | Old owner | Send the descriptor with the frame (P or W, spool head) by `SCM_RIGHTS`. Large rosters are batched across messages. The process descriptor limit comes from the operator-provisioned unit, never a row cap **[unverified reasoning, K-7]**. | — |
| T4 INTAKE | New owner (worker) | CAS `DRAIN_INTAKE(d)` (exclusive with `DRAIN_ABANDON(d)`). Report its received descriptor numbers and host PID through the custody channel. Resume reading, so the next byte is byte P+1 by exclusivity, or resume writing from W of the retained stdin payload with exactly one EOF. Continue the same spool from P. | `DRAIN_INTAKE(d)` with P or W |
| T5 RELEASE | Old owner | After reading the durable `DRAIN_INTAKE(d)`, record OFD-identity evidence: `kcmp (front_pid, worker_host_pid, KCMP_FILE, fd_front, fd_worker) = 0` **[unverified reasoning, K-5]**. Then close its own copy. | `DRAIN_RELEASED(d)` with the kcmp record |

**Failure ownership.** There are never two concurrent readers or writers.

| Crash point | Owner | Action |
|---|---|---|
| Before `DRAIN_FREEZE(d)` commits | Old owner | The old owner's reader never stopped, so nothing changes. |
| After FREEZE, before INTAKE | Old owner (frozen) | The old owner may CAS `DRAIN_ABANDON(d)` and resume from P or W. The new owner's later INTAKE fails its CAS and it closes its received copy unread. |
| After INTAKE | New owner | The old owner never resumes, even if it never saw the INTAKE message: it reads the journal. |
| After RELEASE | New owner | — |

**OFD and lock custody.**
- `fstat` equality (dev, ino, mode), used today at `rw/root_worker_custody.py:191-204`, is not proof of OFD identity, and v2 does not use it as such.
- OFD identity evidence is the kcmp record of T5, produced by the front while it still holds its copy.
- Lock-held evidence: a transferred `flock` lock belongs to the OFD, so it is shared by the transferred duplicate. A fresh `open` plus `LOCK_EX | LOCK_NB` on the path must fail with `EWOULDBLOCK`, showing the lock is held, and the kcmp record shows by whom **[unverified reasoning, K-6]**.
- If kcmp is unavailable on the lab kernel, OFD custody stays explicitly unresolved and its obligation OPEN. It is never replaced by `fstat` equality.

### 7.4 Worker-side `TransferredSlot` and classification

- A new exact type `TransferredSlot` is registered in the worker producer's `slots`.
- `observe()` reads through the transferred host procfs.
- Facts are computed exactly as the front computes them, and are classified only by native `Classify_V2` (§5.2).
- The root's own row is LIVE through its transferred slot, and UNKNOWN when its namespace pidfd is terminal without CLOSED.
- This replaces today's refusal of every other LIVE reservation (`rw/protected_root_observation.py:126-127`) and the empty-slot UNKNOWN of the root row in the worker (B-S3-CUR).

### 7.5 Return of custody at closure

- Slot custody returns to the reconstructed front through the `ClosedFrontEscrow` roster by the same T1–T5 protocol (§6.5).
- Relinquish rule: every live slot is in the transfer roster. A slot that cannot be transferred keeps the named refusal (`ROOT_CAPTURE_OTHER_LIVE_OWNED_DESCRIPTOR_ROSTER_UNAVAILABLE`), and its obligation stays OPEN (G-2).

### 7.6 Additive controls

These are lab controls (operator, D-3a).
- Handoff while an actor is LIVE: the actor is classified LIVE in the worker, and its terminal is collected.
- An UNKNOWN actor stays held.
- A substituted pidfd is refused.
- Drain continuity: complete bytes across the transfer, compared against an independent capture.
- Kernel-buffered bytes and asyncio-buffered bytes both survive the transfer.
- A crash at each T-step follows the failure table.
- Stdin transfer mid-pump: the payload completes exactly once, with exactly one EOF.
- A large roster spans multiple `SCM_RIGHTS` batches with no row cap.
- A missing kcmp leaves OFD custody unresolved and named.

### 7.7 Dependencies and authority

- **Spec S7** depends on S9 (CAS, sub-generations). The full-roster receive ordering it relies on is specified once, in S8 (§8.2).
  - The ordering is shared, not a spec dependency. S7 uses S9's custody records. S8 needs only identity spans (§8.8).
  - Their bodies are integrated through B-RECV and B7 (§15.2).
- **Bodies** depend on SL-0 and the original actor-helper wait and drain lifetime.
- **Lab demonstration and kernel measurements** K-5, K-6 and K-7 are operator work.

---

## 8. Seam 8: native requester correspondence (RC-09, D-8a, D-8b)

Current draft state and quoted requirements are carried by slices **B-S8-CUR** (with the conditional replacement R-4) and **B-S8-REQ** (Appendix C).

### 8.1 Explicit native correspondence inputs (additive SPARK unit `Worldline.Requester_Correspondence`; slice S8)

```ada
type Mode is (Fresh, Retained, Historical);
type Requester_Crosswalk is record
   Raw_Host_Ucred, Raw_Relative_Ucred         : L.Identity;  -- 12-byte "@iII" ucred records
   Host_Socket_Identity, Reader_Socket_Identity : L.Identity; -- (dev, ino, mode) encodings
   Host_Socket_Cookie, Reader_Socket_Cookie   : L.Identity;  -- SO_COOKIE records, or typed absence
   Origin_User_Ns, Reader_User_Ns, Origin_Pid_Ns, Reader_Pid_Ns : L.Identity;
   Pidfd_Record  : L.Identity;   -- optional: raw host fdinfo, or typed absence with errno
   Custody_Head  : L.Identity;   -- the intake or CUSTODY_ACK event that carried the socket
   Which         : Mode;
end record;
```

`Join (Data, X, Original_Raw_Ucred)` is decided natively. Its conjuncts:
- **J1.** Native decode of both ucred spans as signed PID and unsigned UID and GID. This is the original layout `UCRED = struct.Struct("@iII")` (`rw/client_peer.py:21`), so the full unsigned domain is kept.
- **J2.** `Raw_Host_Ucred` is byte-equal to the retained original document's `rawUcred` (`rw/client_peer.py:81`). This is the retained observation, labelled as such.
- **J3.** `Origin_User_Ns = Reader_User_Ns`, and relative UID and GID equal host UID and GID. The helper creates no user namespace: it calls `unshare (CLONE_NEWPID)` (`native_root_worker_supervisor_v1.c:336`) and `unshare (CLONE_NEWNS)` (`:257`) only.
- **J4.** Host and reader socket identities are equal. This is necessary, not sufficient.
- **J5. FRESH only.** Socket-object evidence: the two cookies are both present and equal **[unverified reasoning, K-14]**. The custody head is the current generation's intake. Where cookies are unavailable, the result is the explicit status `Socket_Custody_Unestablished`. It is never replaced by J4 or by a PID label.
- **J6.** The relative PID is recorded uninterpreted. No decision depends on it. The host PID is the original document's.
- **J7.** Pidfd evidence is optional. Its absence never blocks `Join_Ready` (D-8b).
- **J8. RETAINED and HISTORICAL.** No reader socket is required. J2 holds on retained bytes, and the custody head is the original operation's intake record.

Result values: `Join_Ready`, `Ucred_Malformed`, `Uid_Gid_Mismatch`, `Namespace_Mismatch`, `Socket_Mismatch`, `Socket_Custody_Unestablished` (an explicit, unresolved status that keeps the obligation OPEN), `Custody_Missing`.

**Where the native code consumes it (D-8a):**
1. `Legal` (§6.1) for `REQUEST_INTAKE(r)` and `CUSTODY_ACK(g)`. Their evidence includes the crosswalk, and they require `Join_Ready`.
2. `Root_Admission_V2` (§4.3). Its `Requester_Uid` and `Requester_Gid` must equal J1's decoded host values. Today Python unpacks them from `rawUcred` (`rw/protected_root_observation.py:35`).

No digest is hidden in an opaque `current_source`. The v1 proposal to do so is withdrawn (§B.5).

### 8.2 Authenticated socket and host-record custody

- **At accept** the front already reads `rawUcred` and `socketIdentity` in the host PID namespace (`rw/client_peer.py:79-84`, `:120-126`). Additively, it records the socket cookie in a separate record bound to the document's `observationId`. The original `worldline.client-request-observation-v1` schema is unchanged.
- **At transfer** the front journals `REQUEST_TRANSFER_INTENT(r)`, or the root `HANDOFF_INTENT`, before the descriptor moves. The record holds:
  - the original document, unchanged;
  - a fresh host re-read;
  - the front's user- and PID-namespace identities;
  - an optional `SO_PEERPIDFD` record (raw host fdinfo, or errno).
- **The worker receives the complete roster first** — frame, socket, locks, origins — before building any peer. This fixes the order at `rw/root_worker_custody.py:183-185`. It then reads its own relative ucred, its socket identity and cookie, and its namespace identities, raw.
- **`CrosswalkRequestPeer`** is a new exact type, **not** a subclass of `KernelPeer` or `RequestPeer`:
  - it holds the raw relative bytes, the retained document, the socket (for FRESH) and the crosswalk;
  - `observation()` returns a new exact type `RetainedRequestObservation`, labelled RETAINED, never a fresh-read dictionary;
  - `crosswalk()` returns the native input.

### 8.3 Gates

Each exact-type `RequestPeer` gate (v1 observed 11 modules, in B-S8-CUR) gets an explicit, enumerated decision in spec S8:
1. Gates that semantically need a fresh kernel read keep requiring `RequestPeer`, unchanged. They do not accept the crosswalk peer.
2. Gates inside worker custody that need the original request identity accept `CrosswalkRequestPeer` only with a native `Join_Ready` record of the current generation.
3. Historical and settlement gates accept `RetainedRequestObservation`.

Outside worker custody, no gate admits the crosswalk peer.

### 8.4 Domains preserved without new preconditions (D-8b)

| Id | Domain (original source) | How v2 preserves it |
|---|---|---|
| D8-1 | Full unsigned UID/GID, including 0 and the maximum unsigned 32-bit value (RQC "full UID/GID domain"; P1:137) | J1 decodes the original layout. No new restriction. |
| D8-2 | Same-UID new-process commit (RQC) | The join compares credentials and socket custody, never process liveness or PID. |
| D8-3 | A foreign UID or delegated socket gains no extra rights (RQC) | Rights come from the grant selected by host UID and operation (`rw/protected_operations.py:627-628`), unchanged. |
| D8-4 | Prepare versus commit peer joins (RQC) | The preparer binding (`tx['preparerPeer']`, `rw/protected_operations.py:666-667`) is unchanged. The crosswalk applies to the commit peer. |
| D8-5 | An exited client | FRESH requires what the original requires: the retained socket and its host-namespace re-read. No live-client and no fresh-pidfd precondition. Whether `SO_PEERCRED` re-reads stay stable after the peer exits is measured (K-2). |
| D8-6 | Historical settlement with no live client | RETAINED and HISTORICAL modes need no socket (J8). |

Where correspondence cannot be established, the result is an explicit named status, and the obligation stays OPEN. Examples: no socket cookie on the lab kernel, or unreadable namespace identities. Nothing is substituted: no sender PID label, no synthesized `SO_PEERCRED` bytes, and no `fstat` equality as custody.

### 8.5 Kernel measurement items (operator, D-8b; listed in §16)

- K-1: `SO_PEERCRED` PID rendering for a reader in a child PID namespace and a peer outside it. The helper's own comment (`.c:125-128`) is a source statement, not a measurement.
- K-2: `SO_PEERCRED` stability after the peer exits.
- K-3: `SO_PEERPIDFD` availability (header value 77 observed) and its exited-peer behaviour.
- K-4: pidfd fdinfo `NSpid` rendering through host procfs.
- K-14: `SO_COOKIE` availability and uniqueness.

K-5 (`kcmp`) belongs to slot and drain transfer (§7.3), not to this seam.

### 8.6 Actor isolation

No host PID or crosswalk record reaches an actor role (OB-110). The records stay in the coordinator's protected journals, and the P-CE4 FD and environment audit applies.

### 8.7 Additive controls

- A host client whose relative PID reads 0 is accepted through the crosswalk (lab).
- Socket identity mismatch, or cookie mismatch, is refused.
- A different user namespace is refused.
- A client that exited before intake is accepted when the socket and its re-read are valid (D8-5).
- Historical settlement after the client exited succeeds.
- Requester UID 0 and the maximum unsigned UID.
- A delegated foreign-UID socket gains no extra rights.
- Preparer versus commit peer joins.
- Pure native `Join` value fixtures (no root): every status.

### 8.8 Dependencies and authority

- **Spec S8** uses existing types only: custody heads are identity spans. S9 consumes it.
- **Bodies** depend on an exact-type caller audit and on OS-producer historical lineage.
- **Kernel measurement** is operator work (D-8b).

---

## 9. Seam 4: live request multiplexing (RC-06, D-4a)

Current draft state and quoted requirements are carried by slices **B-S4-CUR** and **B-S4-REQ** (Appendix C).

### 9.1 Full-domain accounting matrix (what any accounting option must preserve)

Original serial behaviour, read statically:
- Each request selects its own grant by (host UID, operation) (`rw/protected_operations.py:628-630`) and takes its own fresh use (`:636`, `:670-671`).
- Each request reserves its own row (`rw/protected_scoped_resource_runtime.py:382-404`):
  - scope = current context;
  - parent = the plan's `parent`;
  - kind and amount = the catalogue cost of its own `cost_key`.
- The native scoped `Check` decides `Within_Capacity` (`core/resource_scoped_run_ledger.ads:439`), plus `Parent_Supports` and `Contained` when a parent is declared.
- Operations are serialized by the principal's `operation_lock` only while a handler runs (`rw/protected_operations.py:717`). Detached jobs continue after the handler returns.

| Id | Dimension | Original behaviour per request |
|---|---|---|
| AM-1 | Charge kind | The request's own kind (`Held_Capacity` or `Irreversible_Budget`) |
| AM-2 | Grant | The request's own selected grant; native eligibility on that grant |
| AM-3 | Owner | The request's own requester; `Bound.Owner` from its own material |
| AM-4 | Amount | The request's own amount, which may exceed any earlier root's amount |
| AM-5 | Cost key | The request's own plan's `cost_key` |
| AM-6 | Parent | The plan's `parent`, which may be absent |
| AM-7 | Rollover | A later request reserves under the then-current context |
| AM-8 | Machine admission | Original floors and `max_concurrent_workloads` at DISPATCH and GO |
| AM-9 | Read-only and cancel | `ping`, `status`, `list`, `show` and `job.cancel` are grant-bearing operations with their own use and reservation (`rw/operation_authority_kernel.py:8`) |

### 9.2 Options (none selected; D-4a)

| Option | Sketch | Cells preserved | Known gaps (each would be a new refusal or an invented cost) |
|---|---|---|---|
| A | Contained child hold under the live root reservation | AM-3, AM-5, AM-8 (partly) | AM-1: `Parent_Supports` requires the same kind (`resource_run_ledger.ads:249`). AM-4: `Contained` bounds children by the parent amount (`:259-262`), so larger later requests are refused. AM-6: the plan's parent is replaced by the root. AM-2: `Task_Request_Holds` binds a child's capability and use to the root's (`worldline-resource_child_execution.ads:218-219`), which would borrow the first root grant, which is forbidden. AM-7: origin scope. |
| B | Per-request ownership handoff chain: worker → front custody return between requests | AM-1–AM-7 at ledger level | Availability: custody cannot return while detached tasks run, so later requests wait for detached jobs. That is a liveness regression against the original. |
| C | Long-lived coordinator with nested per-request units under the delegated subtree | AM-1–AM-7 at ledger level | Physical double counting of nested independent top-level rows in the root's counter. `machine_admission` charges a cgroup counter including descendants once (`rw/protected_scoped_resource_runtime.py:655-658`). The handler code runs in the coordinator process, not the nested unit, so real work is not metered. The root's outer ceiling bounds every nested request (AM-4). |
| E | An independent ledger-only hold per request, exactly as the serial path, with in-process execution in the coordinator | AM-1–AM-7 and AM-9 at ledger level | The in-process work of later requests is physically bounded by the **root's** enforced container. The root's limit may kill admitted work (OB-176), or the coordinator container needs headroom that no reservation backs, which would be an invented coordinator cost. |

No option preserves every cell. The lead prepares a native accounting comparison over AM-1–AM-9, with:
- a faithful host and ledger cost proof;
- no borrowing of the first root's grant;
- no new caps;
- concurrency, status, cancel and recovery controls.

An independent GPT-6.1 review follows. Any authoritative resource-policy change, for example coordinator container headroom backed by a new catalogue entry, is selected by the operator (D-4a). Until then, the root route serves later consequential requests only through the routing of §9.3, and their accepted cases stay OPEN.

### 9.3 Owner and recovery authority per phase

Original guard order, applied identically by whichever process serves a request (`rw/protected_operations.py:727-745`):
1. the genuine request-context check;
2. the unresolved-use gate, with **only** `quarantine.resolve` excepted (`:730`);
3. the owner branch: `owner.retry` keeps its named OPEN refusal (`:735-737`), and `owner.adopt` and `owner.recover` go through `OwnerCanonicalScope`;
4. `_reserve`;
5. the workload refusal, with quarantine on exception (`:744-745`, `:767-768`);
6. pre-effect, `EFFECT_INTENT` with `DISPATCH_INTENT`, the handler.

No owner route is widened beyond this.

| Custody phase (§6.2) | Ordinary and read-only (OPS) | `job.cancel` | `owner.retry`, `owner.adopt`, `owner.recover` | `quarantine.resolve` | Recovery authority |
|---|---|---|---|---|---|
| FRONT_OWNED | Front, serial guards. The root route has the three guards restored (DF-3). | Front | Front: original branch | Front: original exception | Front |
| FRONT_CLOSE_INTENT … TRANSFER_SENT | Durably queued. Served by the worker after `CUSTODY_ACK(g)`, or by a reconstructed front after `ABANDON(g)`. | Queued | Queued | Queued | Front, until CUSTODY_ACK or ABANDON |
| WORKER_OWNED … WORKER_RELINQUISH | Transferred to the worker (§9.4). Same guards, same order. Accounting per §9.2 (OPEN). | Transferred, reaching worker-owned jobs | Transferred. The unresolved gate applies exactly as original. | Transferred. The original exception applies. | Worker |
| FRONT_RETAINED_ESCROW, CLOSED_* … FRONT_RECONSTRUCTION | Queued until FRONT_OWNED (g+1) | Queued | Queued | Queued | Collector |
| UNKNOWN(cause) | Queued. No process mutates. | Queued | Queued | Queued | **Reconciler**: native redecision from durable custody, operation and physical evidence (§6.2). If a worker may still own state, it is never stopped (§6.6). Once evidence shows that no worker can act (its pidfds are terminal, with CLOSED or ABANDON), collection and reconstruction proceed. Use uncertainty then goes to K4 through `quarantine.resolve` on the reconstructed front (CD-2). |

Queued requests are durable, are never dropped, and are never refused for phase reasons. A phase transition is not a refusal.

### 9.4 Durable request transfer (WORKER_OWNED)

1. The front appends `REQUEST_TRANSFER_INTENT(r)`. The record holds the full raw request line, the original host observation, the socket identity and cookie, and the namespace identities.
2. It sends the client socket and a sealed memfd.
3. The worker computes the native `Join` (§8.1) and CASes `REQUEST_INTAKE(r)`, which is exclusive with `REQUEST_ABANDON(r)`. Then it acknowledges.
4. The front closes its copy only after it reads the durable intake.
5. A lost ACK is resolved from the journal: exactly once, never dropped, never dispatched twice.
6. Responses and progress are written only by the admitting owner, on the transferred socket.

### 9.5 Availability beyond the router lock

- **No await under the router lock.** No `await gather (collectors)` under the router lock (`rw/root_worker_endpoint_router.py:20-25`). The router waits on custody-phase changes, not on collectors.
- **Protected sections off the event loop.**
  - Protected synchronous sections run through `asyncio.to_thread`, with the entire critical section inside the thread function. That covers `gate.mutex` holders, SQLite, native calls, `fsync` and `/proc` reads.
  - There is no `await` inside a critical section, and the lock order is §13.1's.
  - This addresses OB-158 and OB-163. A filesystem stall blocks a worker thread, not the loop. Its effect on operations is UNKNOWN, never a refusal (G-3).
- **The original `operation_lock` is unchanged** (`rw/protected_operations.py:717`). It serializes handler execution as the original does.
- **Fairness (OB-186).**
  - Requests are queued per requester host UID, served round-robin across requesters and FIFO within one requester.
  - It uses only original policy inputs.
  - No new priority class, no depth cap.
  - Resource exhaustion of the queue is UNKNOWN for the affected requests, never an accepted refusal.

### 9.6 Pre-dispatch refusals keep FRONT_OWNED

- Today any exception after `_reserve` sets `UNKNOWN_WORKER_OWNERSHIP` (`rw/protected_root_worker.py:191-199`) and wedges every later route.
- In v2:
  - A failure before `TRANSFER_SENT` follows the original `_invoke_serial` semantics: native `quarantine (operation, error)`. The phase stays FRONT_OWNED, so `quarantine.resolve` stays reachable.
  - Only failures after `TRANSFER_SENT` produce custody transitions: `ABANDON` or `UNKNOWN`, per §6.3.

### 9.7 Worker lifetime

The worker closes only when it has no in-flight request, no detached task and no live child hold.

### 9.8 Additive controls

These are lab controls (operator).
- `status`, `list` and `show` during a long detached fork or race, answered through transfer.
- `job.cancel` of a worker-owned job.
- A second consequential operation while the first one's detached job runs: its own `RESERVED_NEW`, pre-effect and `EFFECT_INTENT`. Accounting per the selected option, once selected.
- Two concurrent intents on a grant with one remaining use: exactly one succeeds, natively (RQC).
- A pre-effect denial keeps FRONT_OWNED, and `quarantine.resolve` succeeds.
- `owner.adopt` with a non-empty unresolved set is refused exactly as original.
- A lost transfer ACK is handled exactly once.
- Requests during TRANSFER_PENDING and COLLECTING are queued, never refused.
- Round-robin fairness across two requesters.
- An event-loop stall injected in a protected section does not block another requester's response.

### 9.9 Dependencies and authority

- **Spec S10** depends on S1, S3, S4, S7, S8 and S9, and on the D-4a selection.
- **Bodies** depend on SL-0.
- **Lab demonstrations** are operator work. The authoritative resource-policy choice is the operator's (D-4a).

---

## 10. Seam 6: committed outcome versus physical closure (RC-07, D-6a)

Current draft state and quoted requirements are carried by slices **B-S6-CUR** and **B-S6-REQ** (Appendix C). The state model is §2.

### 10.1 `finish` split into three named steps, with serial semantics unchanged

- **`observe_committed_effect (operation, result_capture)`** covers dimensions O and U:
  - `RESULT_CAPTURE` is write-once (`rw/protected_operations.py:780-785`). On the serial path, a later different capture keeps today's `OPERATION_RETAINED_RESULT_CHANGED` refusal unchanged. On the root route, the worker's later capture is the additive boundary that already exists, `ROOT_WORKER_FINAL_RESULT_CAPTURE` (`rw/protected_root_worker.py:300-303`). Settlement uses the retained first capture (CD-8).
  - `EFFECT_INTENT` → canonical effect → native `OBSERVE_EFFECT` = `EFFECT_ACCEPTED` → `EFFECT_OBSERVED` (`:791-798`).
  - Per-right follow-up outcomes.
- **`settle_physical (operation)`** covers dimension P. It calls the scoped `settle_historical` with the three adapters of §10.4, deciding natively by CD-5: REAPED → `RECORD_TERMINAL` → release or charge, or a never-launched release.
- **`settle_use (operation)`** covers dimension U: native `SETTLE_USE` = `SETTLED_NEW` (`:806-811`), after replay equality (`:803-804`).
- **Serial path.** `finish` runs the three steps in exactly today's order, with every `require` kept in place and the `SETTLED` terminal replay retained (`:786-790`). This refactor changes source text, not behaviour. That must be shown by the serial controls on matching source, with an appended pin override for the changed file (§12.1).

### 10.2 Root route while the coordinator is LIVE

- When the `OperationScope` carries the typed `RootWorkerProcess` owner, `after_committed` (`rw/canonical_followup.py:72-84`) runs only `observe_committed_effect` and records `ROOT_PHYSICAL_SETTLEMENT_DEFERRED`.
- No settlement is attempted while LIVE. A deferral is not uncertainty and never quarantines (CD-2).
- Genuine uncertainty may still quarantine the use natively (D-6a): an unknown result capture, a failed durable capture, or a custody `UNKNOWN` hiding the result. `COMMITTED` is unchanged (CD-1).
- The worker's `except` path, `p.quarantine (…)` (`rw/protected_root_worker.py:306-308`), applies only to such genuine uncertainty. It no longer fires because an adapter is missing (DF-5) or because settlement was deferred.

### 10.3 Collector

- After `CLOSED_WITNESS`, the collector runs `settle_physical`, then `settle_use`, against the **retained** first `RESULT_CAPTURE`.
- That fixes the mismatch caused by passing the worker's later capture (`rw/root_worker_closed.py:150-151` → `rw/protected_operations.py:780-781`).
- With no handler terminal, P still settles. U follows CD-2 and K4 (§6.7).

### 10.4 The three scoped historical adapters (DF-5)

All three are defined on `CanonicalOperationPrincipal`, in HISTORICAL mode (§3.4): no fresh peer, grant or exchange. None may reacquire `gate.mutex`, because they run inside `settle_historical`'s and `resolve_historical`'s critical sections (§13.1).

| Adapter (required by) | Keys required | Mirrors (original) | Scoped source |
|---|---|---|---|
| `resource_scoped_historical_settlement` (`rw/protected_scoped_resource_runtime.py:530-534`) | `original_request, scope, bound, native_use, event_id, effects, receipts, causal, resource_packets` | `resource_historical_settlement` (`rw/protected_operations.py:505-520`), `_retain_resource_packets` (`:521-566`) | The scoped service's committed history (`committed_resource_history`, `rw/protected_scoped_resource_runtime.py:606-610`), not the original service's `run_events` |
| `resource_scoped_historical_lifecycle_binding` (`:548-554`) | `scope, bound, request, native_use, event_id` | `resource_historical_lifecycle_binding` (`rw/protected_operations.py:572-585`) | The scoped launch journal rows |
| `resource_scoped_owner_resolution_material` (`:571-577`) | `operation, event_id, proof, original_request, original_capture, original_native_use, scope, bound, packets, retained_resource_history, owner_event_id, owner_capture, owner_native_intent` | `resource_owner_resolution_material` (`rw/protected_operations.py:852-897`) | The scoped committed history and the K4 proof |

### 10.5 Ordering

Child holds settle before the root (CD-9).

### 10.6 Additive controls

Lab controls (operator) unless marked.
- Commit through the worker: `EFFECT_OBSERVED` while LIVE, `SETTLED` after CLOSED.
- Revoke after commit and before CLOSED: settlement still succeeds without a new use.
- A lost result ACK and a lost settlement ACK, on exactly the same operation.
- A committed return without post rights stays COMMITTED with effects skipped.
- A worker crash after commit: `EFFECT_OBSERVED` retained, physical UNKNOWN held, K4 available.
- A deferred settlement never quarantines (negative of the defect).
- An injected unknown result capture quarantines natively, with `COMMITTED` unchanged.
- Serial path: every original serial control on matching source, including the never-launched held-capacity release and the `SETTLED` terminal replay.
- Pure value fixtures (no root): each adapter's key and binding refusals.

### 10.7 Dependencies and authority

- **Spec S6** depends on S1 (the scoped exchange and K4 successors) and S9 (custody, for the root-route branch).
- **Bodies** depend on the L-A1 scoped committed-envelope lineage (§15.1) and SL-0.
- **Lead work:** source. **Operator work:** lab demonstrations.

---

## 11. Seam 2: startup version union, reconciliation, frontier control (RC-12, D-2a, D-2b)

Current draft state and quoted requirements are carried by slices **B-S2-CUR** and **B-S2-REQ** (Appendix C).

### 11.1 Version, loader, schema and creation-slot union (DESIGN)

The descriptor schema is selected by its exact `schema` value in **every** consumer. Nothing is defaulted between versions, and neither version reads the other's state as its own.

| Id | Version | Constructor or entry | Early-loader entry | Descriptor schema (exact key sets) | Early-envelope DATA | Creation slot | Absence or failure behaviour |
|---|---|---|---|---|---|---|---|
| U-1 | v1 | `StartupLease (descriptor)`, then `construct ()` via `serve ()` | Existing daemon entry | `worldline.protected-startup-v1` (`rw/protected_startup.py:173-176`; runtime keys `:264-266`) | Descriptor and genesis (`:275-277`) | none | Named refusals. `construct ()` raises `PROTECTED_FULL_LEDGER_STARTUP_RECONCILER_UNAVAILABLE` (frontier, §11.6), then diagnostics (`:799-812`). |
| U-2 | v1 | `StartupLease (descriptor, operation_head_creation => path)` | `protected-canonical/provision_operation_head.py` (ENTRY, `:340-344`) | v1 | As U-1 | Operation-head DB, one-shot (`:328-350`) | Refuses if it exists (`:319-320`) |
| U-3 | v2 | `StartupLease (descriptor)`, then `construct_v2 ()` via `serve ()` | Daemon entry | `worldline.protected-startup-v2`: v1 keys plus `runtime.resource_scoped_producer`; `tools` adds `resource_supervisor_v3`, `bwrap`, `systemctl`, `systemd_run`; `provisioned_state` adds the owner plan, crosswalk, custody v2 DB, lock and genesis | Descriptor, genesis, owner plan, crosswalk, run-scoped config, custody v2 genesis, header DATA | none | Named refusal, or the genuine reconciler (§11.5) |
| U-4 | v2 | `StartupLease (descriptor, operation_head_creation => path)` | `provision_operation_head.py`, dispatching on schema | v2 | As U-3 | Operation-head DB, one-shot | Refuses if it exists |
| U-5 | v2 | `StartupLease (descriptor, custody_creation => slot)` (new) | `protected-root/provision_root_custody.py` (new ENTRY) | v2 | Plus the custody genesis | Custody v2 DB, lock and genesis, one-shot. It binds the v1 journal head if a v1 journal exists. | Refuses if any target exists. Never re-geneses existing history. |
| U-6 | v2 | `RootWorkerIntake (descriptor)` | `protected-root/worker_entry.py` | v2 | Descriptor. Owner plan from the custody frame (`rw/protected_root_worker.py:362-377`). | none | Refuses without the early loader (`:343-344`) |
| U-7 | v2 | `StartupLease (descriptor, custody => CustodyReceipt)`, then `construct_v2 ()` in the worker | `worker_entry.py` | v2 | As U-6 | none | Refuses on roster, descriptor or genesis change (`rw/protected_startup.py:205-212`) |
| U-8 | v2 | `protected-root/launcher.py` | Launcher ENTRY | v2 | Selected by the launcher | none | euid 0 check (`launcher.py:12-13`) |
| U-9 | v2 | `RootWorkerFront (principal, owner_descriptor)` | Daemon | v2 | Owner plan (`rw/protected_root_worker.py:95-104`) | none | Refuses on a plan key-set change |
| U-10 | v2 | `StartupLease (descriptor, custody => ClosedFrontEscrow)`, then `construct_v2 ()` (collector reconstruction) | Daemon | v2 | As U-3 | none | Named refusal. `UNKNOWN_CLOSED_RECONSTRUCTION` is retained. |
| U-11 | v2 | One `attach_scoped_resource`, in `construct_v2` between `StateStore` and `RuntimeController` | — | v2 only | Run-scoped config (`rw/protected_scoped_resource_runtime.py:54-56`) | none | `SCOPED_EXACT_EARLY_SELECTED_PRODUCER_REQUIRED` |
| U-12 | v2 | Crosswalk provisioner (offline) | `protected-root/provision_root_crosswalk.py` (new ENTRY) | v2 | Crosswalk schema | The crosswalk file, operator-provisioned | One-shot |

### 11.2 The v2 descriptor and its schemas

- Exact key sets as in U-3.
- The descriptor's `files` bind:
  - an owner-plan JSON schema for `worldline.protected-root-worker-plan-v1`, which today has no schema file;
  - the crosswalk schema `worldline.protected-root-operation-crosswalk-v1`;
  - the custody-genesis schema.
- The early envelope selects `/usr/include/asm-generic/socket.h` as DATA for `SO_PEERPIDFD`.
- v1 descriptors keep their exact accepted behaviour.

### 11.3 One-shot provisioning (operator-run, D-2a)

- **Modelled on** `provision_operation_head.py` and `_offline_operation_slot` (`rw/protected_startup.py:328-355`): an exact ENTRY, the creation slot declared in the descriptor, and an exclusive create.
- **Custody journal v2:**
  - full DDL (§6.11);
  - admission `UNUSED → INTENT → CONSUMED` with the owner envelope;
  - a MAC'd genesis row; the initial head binds `initial_event`, which today's `_load` requires but never uses;
  - `fsync` of the file and the directory.
- **At run time** the database opens `mode=rw` only. The complete `sqlite_master.sql` text is verified as well as the columns. Today only `(name, type)` pairs are checked (`rw/root_worker_journal.py:85-92`).
- **Never** is a missing journal, key, genesis, lock or head created by a startup path (P1:99).

### 11.4 Diagnostic startup fabricates no mutable authority

- A v2 `construct_v2` refusal follows the v1 diagnostic pattern: `IntentDispatcher (startup_error => …)`, diagnostics only (`rw/protected_startup.py:752-756`, `:799-812`).
- No `RuntimeController` or principal is constructed for mutation. No genesis, history or Store is created when prior state is missing.
- The daemon always starts (OB-202). Recovery runs before any consequential request is served.

### 11.5 Native full-ledger reconciliation table (DESIGN; every decision uses the existing native relations)

The relations are: scoped `Check`/`Check_V2` and `Classify`/`Classify_V2` for P; `Operation_Authority.Decide` for U; `Root_Custody_Phase.Legal` for C; the canonical exchange for O.

| Id | Durable and observed state | Native decision | Action | Automatic or owner |
|---|---|---|---|---|
| RT-1 | Row RESERVED; launch journal NEVER_DISPATCHED; classified NEVER_LAUNCHED | P: `Release_Hold` from Reserved with Never_Launched | Release | Automatic |
| RT-2 | Row LAUNCH_INTENT; dispatch journaled; no HELD; classified UNKNOWN (a present `Dispatch` defeats `Never_Holds`, `resource_observation_classification.ads:97`) | P: `Retain_Uncertain` | Holds retained | Automatic retain. Resolution through owner or recovery. |
| RT-3 | Row RUNNING; live owned slot | P: LIVE | No change. Resume ownership per C. | — |
| RT-4 | Row RUNNING or TERMINATING; authentic retained CLOSED witness | P: REAPED → `Record_Terminal` → release or charge | Settle | Automatic |
| RT-5 | Row RUNNING or TERMINATING; no slot; no witness | P: UNKNOWN → `Retain_Uncertain` | Holds retained | Automatic retain |
| RT-6 | Row SETTLEMENT_UNKNOWN; a later authentic CLOSED witness | P: REAPED → `Record_Terminal` (legal from Settlement_Unknown, `resource_run_ledger.ads:313-314`) → release or charge | Settle | Automatic |
| RT-7 | U EFFECT_INTENT; C WORKER_OWNED; worker dead; HANDLER_TERMINAL with retained `RESULT_CAPTURE`; authentic chain | U: `OBSERVE_EFFECT`, then, after P, `SETTLE_USE` | Complete | Automatic |
| RT-8 | U EFFECT_INTENT; no retained `RESULT_CAPTURE` | U: `QUARANTINE_USE`, matching `recover_committed`'s requirement of exactly one retained capture (`rw/protected_operations.py:812-816`) | Quarantine | Owner (K4) |
| RT-9 | C TRANSFER_SENT(g); no CUSTODY_ACK; the front restarted | C: `ABANDON(g)` by the Reconciler | Collect, then decide U by RT-7 or RT-8 | Automatic |
| RT-10 | C CUSTODY_ACK(g); worker alive; the front restarted | The front cannot lock: the worker holds the transferred OFD locks (`rw/protected_startup.py:374-385`) | Diagnostic `WORKER_OWNED_LIVE`. No stop. Collect when the worker closes. | Automatic |
| RT-11 | C CUSTODY_ACK(g); worker dead | C: collection (§6.7) | Settle P. U by RT-7 or RT-8. | Automatic or owner |
| RT-12 | C UNKNOWN; authentic physical terminal evidence | C: Reconciler redecision | Collect | Automatic |
| RT-13 | C UNKNOWN; worker possibly alive | none | Wait. Never stop. Diagnostic. | Automatic retain |
| RT-14 | A journal, key, genesis or head missing or changed | none | Named refusal. No reinitialization. | Owner (restore; never genesis) |
| RT-15 | Bootstrap INTENT without its file | Existing refusal `STARTUP_GENESIS_INTENT_MISSING_FILE_REVIEW_REQUIRED` (`rw/protected_startup.py:587`) | Diagnostic | Owner |
| RT-16 | U QUARANTINED | none | Retained | Owner (K4 through `quarantine.resolve`) |

v1's blanket rule, that a dead daemon's WORKER_OWNED operations become QUARANTINED, is withdrawn. Authentic known outcomes complete automatically (RT-4, RT-6, RT-7, RT-9, RT-11, RT-12). Uncertain ones retain holds and quarantine natively (RT-2, RT-5, RT-8, RT-13). The protected owner route stays available (RT-16).

### 11.6 Frontier control (D-2b; RC-05)

- **Retained byte-exact.** `R/protected-startup/controls/test_protected_startup_v1.py` (sha256 `a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb`). The test `test_current_source_frontier_names_full_ledger_startup_gap` is at `:97-105`.
- **Its exact version and domain:**
  - a v1 descriptor named by `WORLDLINE_PROTECTED_BOOTSTRAP_CONTROL_COMPOSED_NATIVE_PROOF`, with schema `worldline.protected-startup-v1`;
  - expected: `construct ()` raises `PROTECTED_FULL_LEDGER_STARTUP_RECONCILER_UNAVAILABLE`, `gate` and `store` are constructed, `controller` is `None`.
- **v2 keeps that behaviour.** v1's `reconcile_admission` (`rw/protected_startup.py:467-472`) stays unchanged for v1 descriptors.
- **v2 positives are additive**, on v2 descriptors, in a separate control file (§17.2).
- **No re-enrollment is proposed.** v1's retirement text is withdrawn.
- **If a re-enrollment is ever proposed:**
  1. The lead prepares a concrete equivalence and adoption package:
     - original bytes and roster retained;
     - an exact version and domain mapping;
     - all original negative cases and genuine positives;
     - no passing-history credit.
  2. Applicable operator authority adjudicates.
  3. Independent GPT-6.1 review.

  The original obligation stays OPEN throughout.

### 11.7 `attach_scoped_resource`

There is one definition, keeping the stricter exact-producer check (DF-2). It is called only from `construct_v2` (U-11).

### 11.8 Additive controls

Lab controls (operator, D-2a).
- A positive v2 startup.
- A missing journal, genesis, key or head refuses, with inode and bytes unchanged before and after.
- A second provisioner run refuses.
- DDL constraint violations are rejected.
- A crash between INTENT and CONSUMED resolves without reinitialization.
- A restart with LIVE or UNKNOWN rows keeps the holds.
- The OB-202 analog: a hung or missing `systemctl` still lets the daemon start, in a diagnostic state.
- v1 descriptor parity: every v1 control, including the frontier control.
- One control per RT row.

### 11.9 Dependencies and authority

- **Spec S11** depends on S3 (crosswalk schema), S4 (`Classify_V2`), S6 (state model), S7 (slot custody) and S9 (crash table).
- **Lead work:** the schemas, provisioner source, reconciler source and attach wiring.
- **Operator work:** running provisioners, any `/srv` lab installation, and every startup control. All need root (`rw/protected_startup.py:153`).

---

## 12. Seam 10: pins, external freeze, enrollment, controls (RC-10, RC-05)

Current draft state and quoted requirements are carried by slices **B-S10-CUR** and **B-S10-REQ** (Appendix C).

### 12.1 Reviewed appended effective pin overrides

- **How pins work.** `CONTRACT_PINS` is updated in sequence, and the effective pin of a key is its last update (`rw/proof_manifest.py:1002-1034`). The v2 author's AST count observes 16 pin statements and 191 effective keys in the lane source, and 171 in the preimage (consistent with F-03).
- **Append only.** v2 appends new `CONTRACT_PINS.update ({…})` statements after the last existing statement. In the lane that is `:1034`; in an integrated base it is that base's last statement. No earlier line is edited. The original policy stays a literal byte prefix (as the CHILD review observed for its own append, `REVIEW.md:17`).
- **The stale pin (DF-1)** is superseded only by an appended override computed on the **reviewed final** text of `protected_operations.py`. A refresh on draft or incomplete source, which would only make startup pass, is excluded.
- **Every changed or new pinned file** gets an appended override at slice freeze: Python, C, Ada and documents.
- **Limits of `normalized_ada`.** It strips `--` comments and collapses whitespace (`:420-434`) in every pinned file, including Python and C. In Python that hides indentation changes and treats `#` comments as code. A pin is therefore a semantic-change tripwire, not an exact identity. Hence §12.2.
- **No new approval gate.** A file being pinned triggers no operator approval. Only the reserved decisions of G-7 apply.

### 12.2 External exact inventory and freeze

- **Record.** A freeze record held **outside** every source tree, produced at each slice freeze and for the integrated candidate. For every file it lists the relative path, the sha256 of the whole bytes, the length and the mode, plus directory modes and key sets. Files covered:
  - sources;
  - controls, including `R/protected-startup/controls/*` and RQC;
  - project files;
  - headers selected as DATA;
  - the native helper source;
  - the dependency overlays `lab/intent_gate.py`, `universe_source/issuer/protected.py` and `universe_source/universe_authority/protected.py` (`L/origin.json`);
  - `runtime/worldline/proof_manifest.py` **itself**.
- **Binding.** The freeze is bound by the independent GPT-6.1 review's `review-freeze.json`, not by the manifest. There is no self-hash cycle, because the manifest never holds its own content hash (review RC-10).
- **Installation binding** stays the descriptor's exact `files`/`trees` check (`rw/protected_startup.py:250-262`).
- Pins and the exact freeze are complementary. Neither replaces the other.

### 12.3 Enrollment of every new native semantic unit

- **`REQUIRED_PROVED` appends**, in packet order, for each of:
  - `Worldline.Scoped_Canonical_Operation` and its `_Wire`;
  - the scoped exchange and K4 successors;
  - `Worldline.Source_Record`;
  - `Worldline.Resource_Child_Execution_V2`;
  - `Resource_Observation_Classification_V2`;
  - `Resource_Scoped_Run_Ledger_V2`;
  - `Worldline.Root_Custody_Phase`;
  - `Worldline.Requester_Correspondence`;
  - the unit of `Enforcement_Corresponds`;
  - each one's wire unit.

  Lists are fixed at each spec freeze. `DECLARED_CORE_ADA_SOURCES` additions follow. `export_problems` extensions bind each new export symbol exactly once, in the pattern of `:929-937` and `:957-964`.
- **No `REQUIRED_PROVED` name inside `Worldline.C_API` (N-2).** The lane's eight `Worldline.C_API.Child_*` names (lane positions 606–613) are draft additions and appear in no original roster: the preimage roster is the lane's first 485 names (LCP 485, observed). Their obligation — proof of the child boundary's decoding, shape, layout and decision transport logic — is carried by On units: `Worldline.Resource_Child_Execution_Wire` or a new On wire unit, enrolled by name. `C_API` keeps transport only (§14.3).
- **Strict scope retained** (G-5).

### 12.4 Integrated roster order (observation N-1)

The integrated `REQUIRED_PROVED` is the concatenation, each block append-only and never reordered:
1. **S5's 535 names**, the literal prefix.
2. **The C-API successor's 98 names** in packet order, if it composes first (§14.4 O1). Final length 633 is CAPI4's own figure (its J20).
3. **The protected canonical lineage's names absent from S5:** the lane preimage's 66 names after the common 419 (J03), in lane order. Examples are `Worldline.Operation_Authority.*` and `Worldline.Canonical_Operation.*`.
4. **The child and root additions:** the lane's 129 added names (J04), with the eight `Worldline.C_API.*` names replaced by their On-unit carriers. That leaves 121 carried names (J13) plus the carriers.
5. **v2's new unit names** (§12.3).

The exact final list is a reviewed integration artifact. Where a unit exists in both S5 and the protected lineage, S5's version is the base, and the protected units' callers must compile and prove against it. That is a shared caller and ABI resolution inside G-PROT (§15.1; P1:153). The 116 S5 names absent from the lane (J01) are S5's and stay.

### 12.5 The C helper

- A build recipe with exact compiler identity, warnings as errors, stack protector, FORTIFY, PIE and full RELRO.
- Static analysis, plus sanitizer and fuzz fixtures for the frame parsers, in the lab.
- All recorded as unproved native-body obligations (OB-048 class). C hardening is not full-body proof and gives no proof credit.

### 12.6 Seal controls

- A manifest audit that recomputes the effective pins and compares against the external freeze.
- An unpinned-file detector: every changed file is pinned, or is in the freeze with a stated reason.
- A stale-pin mutant.
- A C hardening-flag check.
- **No `REQUIRED_PROVED` name with the prefix `Worldline.C_API.`.**
- **No `SPARK_Mode => Off` outside `worldline-c_api`** (N-3).
- Roster-prefix check: S5's 535 names literal.
- `UNANALYZED_BOUNDARY == {"worldline-c_api"}`.
- `MINIMUM_CHECKS ≥ 251`.

---

## 13. SL-0: source hygiene (DF-2, DF-3, DF-6, N-6)

### 13.1 Lock discipline and audit

**Observed facts:**
- `Gate.mutex` is a `threading.Lock` (`dependency-source/lab/intent_gate.py:371`; preimage `:362`).
- The producer's `order` is a `threading.RLock` (`rw/protected_resource_runtime.py:150`).
- The `gate.mutex` sites per runtime file (grep): scoped runtime 12, base resource runtime (`protected_resource_runtime.py`, L-A1 origin) 5, scoped service 2, actor execution 1, root observation 1, scoped supervisor V3 1.

**Discipline (DESIGN):**
1. **One acquisition per public entry.** Public entry points acquire `gate.mutex` and then `order` exactly once, through one wrapper `_protected_section ()`. The wrapper also sets a thread-local holder marker for the current thread.
2. **`_locked` variants.** Every internal `_…_locked` variant requires the marker, and otherwise raises a named refusal. It never acquires `gate.mutex`. Each public method that nests today is split into a public wrapper and a `_locked` body, and calls inside a section go to `_locked` variants. From N-6 (a)–(e), that includes at least `reconcile_context`, `submit_bound`, `machine_admission`, the scoped `current_context`, `capture_execution`, and the scoped service's `recover` and `commit`.
3. **Lock order:** `gate.mutex` → `order` → `store._lock` → service and database locks. No later lock is ever held while acquiring `gate.mutex`.
4. **No `await` inside a section.** Sections run in worker threads (§9.5).
5. **The Gate and its `threading.Lock` are unchanged.** No `RLock` substitution hides uncertain ownership.
6. **Unchanged semantics.** Each section re-reads its inputs after acquiring, so observation freshness is kept. Protected transition boundaries and the original default branches are unchanged.

**Audit scope.**
- Service, capture, reconcile, submit, historical, owner and callback paths, resolved by receiver type and by thread. That includes cross-module calls such as the scoped service, actor execution and root observation, not only syntactically nested `with` statements.
- The deliverable is a complete call-and-lock table. Every candidate in N-6 and AUTHOR-NOTES §3 is classified as nested, or as not nested with a reason.
- **Lineage.** `protected_resource_runtime.py` and `protected_scoped_resource_service.py` were taken unchanged from L-A1 (N-6 (d)). Fixing their nestings changes L-A1-lineage files, so those fixes are bound to G-A1's separate selection and freeze as well as to the SL-0 review.
- Implemented deadlock freedom is **not** claimed here.

### 13.2 One `attach_scoped_resource` (DF-2)

There is one definition, keeping:
- the exact producer path (`selected == gate.root / 'authority/resource/run-scoped-config-v1.json'`);
- early-selected DATA membership;
- the already-attached refusal (`rw/protected_scoped_resource_runtime.py:52-58`).

The shadowing definition at `:961-964` is removed. It is called only from v2 `construct_v2` (U-11).

### 13.3 The root route's pre-dispatch guards in the original order (DF-3)

`RootWorkerFront.invoke` applies the following, as `_invoke_serial` does:
1. The genuine request-context check (`rw/protected_operations.py:728`) and the unresolved-use gate with the exact `quarantine.resolve` exception (`:730`), **before** `_reserve`.
2. The workload refusal **after** `_reserve`, inside the same `try` whose handler quarantines the reserved use (`:742-745`, `:767-768`).
3. `DISPATCH_INTENT` retained in the `EFFECT_INTENT` boundaries (`:749`).
4. Pre-dispatch failures keep FRONT_OWNED (§9.6).

### 13.4 The rest of SL-0

- The self-comparing pairs (DF-4) go to §4.
- The adapters (DF-5) go to §10.4.
- The pin plan (DF-1) is §12.1.
- These SL-0 changes need different-author GPT-6.1 source review (P1:153). They give no runtime or proof credit.

---

## 14. Shared `core/worldline-c_api.adb` integration with C-API DESIGN v4 (a design obligation with its own checks)

This section neither accepts nor resolves either lane. CAPI4 is itself DRAFT_FOR_GPT61_REVIEW, and nothing here changes it.

### 14.1 Observed facts (read-only scripts, `difflib`, `grep`)

| Fact | Value |
|---|---|
| S5 C_API body versus commonV4 | Byte-identical: 56596 bytes, sha256 `0a17c0efb95904ee865182a20d3bcabceeef93b1cc3639687aab27696339f35b` |
| Lane preimage → S5 (body) | One inserted line, `:32`, `use type System.Storage_Elements.Integer_Address;`, 53 bytes with its newline. That accounts for the 53-byte size difference (J09). |
| Lane preimage → draft (body) | 6 `with` lines inserted at the top, and 1119 lines inserted after `end Owner_Audit_Decide;` (draft `:1166-2284`), before the final `end` (`:2285`) (J07, J08). Nothing else differs. |
| Specs | S5 spec = preimage spec, byte-identical. The draft spec appends 32 lines (J15) after `wl_owner_audit_decide_v1`: `Child_Version`, `Child_Layout`, `Child_Decide`, exported as `wl_resource_child_execution_{version,layout,decide}_v1`. |
| `External_Name` occurrences | S5 31 (agrees with CAPI4's "31 observed today"). Draft 34 (J10). |
| Anchors, S5 / draft | `end Layout_Offset;` 667 / 672; `package body Authority_Glue is` 671 / 676; `end Owner_Audit_Decide;` 1160 / 1165; final `end` 1161 / 2285. The offset of +5 is 6 − 1 (J11, J12). |
| `Authority_Glue` text | Identical in preimage, S5 and draft except for line offsets. No `difflib` opcode falls inside it. |
| Package renamings / lines beginning with `use` | Draft 25 / 29. S5 14 / 22. The 11 added renamings are inside `Child_Boundary`'s package body (N-5). |
| Off units | N-3 |
| Enrolled names inside the Off body | N-2 |
| `Size` literals | N-9 |
| CAPI4 binding text | Contains no `Child_` identifier (grep count 0). The draft's new C_API-level names do not appear in any CAPI4 tile. |

### 14.2 Hazards

| Id | Hazard | Static consequence |
|---|---|---|
| H1 | Body layout collision: CAPI4's export run must directly follow `end Owner_Audit_Decide;` and end at the final `end` (R-LAYOUT, CAPI4 §3.6). The draft's block occupies exactly that region. | R-LAYOUT refuses the draft text (CAPI4 §19). |
| H2 | Spec layout collision: CAPI4's spec run (4 subtypes and 20 declarations) must directly follow `External_Name => "wl_owner_audit_decide_v1";`. The draft's 3 declarations occupy that region. | S-RES and R-LAYOUT refuse. |
| H3 | Residual hashes and clause tables are S5-based (R-RES, S-RES, R-INV (ii), K-checks). The draft's 6 `with` lines, 11 renamings and 8 `use` lines change the residual. | Refusal until a reviewed rebase. Tables are never edited to fit (CAPI4 §19). |
| H4 | `External_Name` census: CAPI4 counts 31 → 51 (its J05). The draft adds 3. | The census must be re-observed. |
| H5 | Identifier homographs: CAPI4's spec-level `U8`, `U32`, `I64`, `Size`; the draft's `Size` literals (N-9); the draft's single-letter renamings in `Child_Boundary`'s body; CAPI4 transports' and `Authority_Glue`'s single-letter renamings (`A`, `W`, `C`, `Q`, `E`, `T`, …). | **[unverified reasoning; author's reading of RM 8.4, RM 8.3; advanced-ada ch14 "multiple use clauses cause hiding"]** Merging texts into one scope can make a use-visible name not use-visible, so resolution fails or changes. Installed-compiler confirmation is OPEN (CAPI4 D-38). |
| H6 | The Off units (N-3): the lane's Off versions of the 15 C-API units, and the protected lineage's 9 Off C API files. | Composing them restores Off exemptions outside the sole boundary (P1:29; `rw/proof_manifest.py:316`). |
| H7 | Enrolled names inside the Off body (N-2). | The required-proved check fails (`rw/proof_manifest.py:857`) **[static reasoning]**. |
| H8 | Optional_Marker: the lane's `core/worldline-recovery.ads` differs from S5's (G-10). Recovery C API units depend on its form. | S5's and the C-API successor's recovery units are taken (R-RW-9). |

### 14.3 Design rules for root-worker additions to `C_API`

- **R-RW-1. The CAPI4 pattern for every root-worker export.** That covers the re-authored child execution v1 exports, the scoped canonical operation, `Root_Controller_V2`, the custody phase relation, the requester join and the V2 classification and ledger exports if they are exported. Each gets:
  - (a) one transport package, appended at the end of `CAPI_LAYOUT_PACKAGES`, after `Pending_V2_Transport`;
  - (b) one export body, appended at the end of `CAPI_LAYOUT_EXPORTS`, after `Pending_Decide_V2`;
  - (c) one spec declaration, appended at the end of the spec run;
  - (d) all value logic (decode, shape, layout, decision) in On units, enrolled by name.

  Proposed transport names: `Child_Execution_Transport`, `Scoped_Operation_Transport`, `Root_Controller_V2_Transport`, `Custody_Phase_Transport`, `Requester_Join_Transport`, `Classification_V2_Transport`, `Scoped_Ledger_V2_Transport`.
- **R-RW-2.** `Worldline.C_API` spec and body level declare nothing beyond transports, exports and CAPI4's subtypes. There is no package renaming at C_API body level. The draft's `Child_Boundary` nested package is not carried. Its content is split into `Child_Execution_Transport` (transport-only helpers) and On-unit value logic.
- **R-RW-3.** No identifier declared in a root-worker transport or export may be a homograph of any C_API-level declaration. That includes `U8`, `U32`, `I64`, `Size`, every `CAPI_LAYOUT_PACKAGES` name and every CAPI4 export name. The draft's enumeration literals `Size` and `Alignment` are renamed (for example `Field_Size`, `Field_Alignment`) or move into an On wire unit. Hiding rules are not relied on.
- **R-RW-4.** Root-worker clause blocks use distinctive renaming identifiers, such as `Child_Wire`, `Actor_Wire`, `Admission_Wire`, `Authority_Wire` and `Scoped_Wire`, instead of single letters. Each export body uses exactly its own transport, as CAPI4 R-INV requires, and no other.
- **R-RW-5.** Every new clause, renaming exclusion, write form and gate is listed in stage tables by CAPI4's rules (R-INV, R-ALIAS, R-W, R-GATE). Every export is tiled (R-TILE) in its own packet.
- **R-RW-6.** Writes use only the listed write forms (CAPI4 §3.4), with their gates.
- **R-RW-7.** No `REQUIRED_PROVED` name is under `Worldline.C_API` (§12.3).
- **R-RW-8.** S5's On versions of the 15 C-API units are taken, never the lane's Off versions. The 9 protected-lineage Off files are consolidated by a **new successor lineage L-CAPI-P** following CAPI4's pattern before the protected lineage composes (G-PROT). L-CAPI-P has its own independent review.
- **R-RW-9.** S5's recovery units, carrying the Optional_Marker form, and the C-API successor's recovery packets are taken. Nothing from the lane overrides them.
- **R-RW-10.** Every new On unit is accounted in the core `Library_Interface` per CAPI4's K3 and G9 checks (CAPI4 observed a 71-unit core interface). This is re-observed after the rebase.

### 14.4 Ordering (a proposal for the lead's decision; the reviewer checks it)

| Option | Order | Effect on CAPI4's tables | Note |
|---|---|---|---|
| **O1 (proposed)** | (1) C-API successor packets PK-0 … PK-S on S5, as CAPI4 designs; (2) L-CAPI-P; (3) G-PROT, the protected canonical lineage composed by explicit reviewed import; (4) root-worker packets per R-RW-1, appended at the run ends | CAPI4's L0 tables stay S5-based. Every later stage appends at the run ends (CAPI4's stage rule). | Matches the review: final ABI adoption waits on the reviewed C-API successor (review §3). |
| O2 | A rebase of CAPI4 onto S5 plus G-PROT plus the root-worker C_API changes first | Every CAPI4 residual table and hash is re-observed and re-reviewed (CAPI4 §19 remedy). | Delays C-API. Widens re-review. |
| O3 | Interleaved per packet | Re-observation at every interleave | Highest review cost |

In every option, the integration grants neither lane's acceptance.

### 14.5 Integration checks

These are static, run by the lead on each rebased candidate. Mutation controls run on temporary trees. No WORLDLINE code runs.

| Id | Check | Mutation that must refuse |
|---|---|---|
| IC-1 | CAPI4's R-LAYOUT, R-RES, S-RES, R-INV, R-ALIAS, R-W, R-GATE and R-TILE on the composed text, with the appended root-worker stage tables | A moved export run |
| IC-2 | C_API-level declaration census: no homograph between a root-worker transport or export identifier and any C_API-level identifier (R-RW-3) | A draft-style `Size` literal, or a C_API-level renaming |
| IC-3 | Renaming identifiers unique across all transports (R-RW-4) | A transport declaring `W` |
| IC-4 | Each export body uses exactly one transport, its own | An export using two transports |
| IC-5 | `External_Name` census equals CAPI4's final count plus the root-worker additions, each exactly once | A duplicated symbol |
| IC-6 | No `REQUIRED_PROVED` name under `Worldline.C_API` | An enrolled `Worldline.C_API.X` name |
| IC-7 | No `SPARK_Mode => Off` outside `worldline-c_api` | A restored Off unit |
| IC-8 | `Authority_Glue` identical to S5's except CAPI4's GE1–GE9 (glue hash re-observed) | A changed glue line |
| IC-9 | Optional_Marker files identical to S5's or the reviewed successor's | The lane's `worldline-recovery.ads` |
| IC-10 | Installed-compiler confirmation of name resolution, and no warning for any transported clause (CAPI4 D-38) | — OPEN: needs the admitted frame |

---

## 15. Dependency DAG (RC-11)

Spec slices are named S0–S4 and S6–S11. **"S5" is deliberately not used as a slice name**, so it cannot be confused with the S5 composition alias.

### 15.1 Lineage nodes, bound separately

| Node | What | Identity / status |
|---|---|---|
| L-S5 | Integration base | `W/work/claude-composition-v5-beta/source`: QUALIFIED_SOURCE_COMPOSITION. Proof, source and phase acceptance false. |
| L-PROT | The protected canonical lineage of the lane's primary (actor stdin V4, `L/origin.json` `primary`): `Operation_Authority`, `Canonical_Operation`, `Canonical_Exchange`, `Canonical_Owner_Completion`, `Actuation` and their wires and callers, **absent from S5** (P0-6, N-1, N-3) | Finite reviewed primary (RW:11). This draft gains no review credit from it. |
| L-CHILD | The child-authority source: the scoped ledger, classification, actor admission and execution, child execution, and the C_API child block | `CHILD`: finite actual GPT-6.1 source review. Controls UNBUILT and UNRUN. |
| **L-A1** | The scoped committed envelope, `W/work/scoped-committed-envelope-repair-v2-retry1` | Inventory `dee54c19…`, binding `7e83fc5c…`, freeze `1d65ca48…` (RW:13). It supplies `resource_actor_credentials.py` and `resource_machine_evidence.py` (closure v2) and the committed-envelope semantics for §10 and K4. |
| **L-CAPI** | The C-API consolidation successor | CAPI4 is DRAFT_FOR_GPT61_REVIEW. Its source packets PK-0 … PK-S are unwritten. The v3 review is sealed. |
| **L-CAPI-P** | **New.** Consolidation of the protected lineage's 9 Off C API files (N-3) | Not yet designed. An OPEN obligation of this lane, with its own review. |
| L-DEP | COSMOGONY dependency overlays (`dependency-source/`: `intent_gate`, issuer, universe), with draft preheld-lock overlays | Explicit lab dependencies. They need their own selection, review, pin and freeze (review §4). |
| L-RW | This lane | INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY |

L-CAPI and L-A1 are distinct nodes with distinct identities and gates. v1's shared "A1" shorthand is withdrawn (§B.5).

### 15.2 Spec, body and gate graph

**Spec nodes.** Each is passive lead drafting with an independent GPT-6.1 review.

| Spec | Content | Depends on |
|---|---|---|
| S0 | SL-0 hygiene: no new spec | — |
| S1 | Scoped canonical operation (§3) | Existing types only |
| S2 | `Source_Record`, `Root_Controller_V2`, `Controller_Valid_V2` (§4.1, §4.3) | Existing types and `Attest` |
| S8 | Requester correspondence (§8) | Existing types only |
| S3 | Crosswalk schema, `Enforcement_Corresponds` (§4.4, §4.5) | S2 |
| S9 | Custody phase relation (§6) | S8 |
| S4 | Delegation and classification successor (§5.2) | S2, S3 |
| S6 | State model, `finish` split, adapters (§2, §10) | S1, S9 |
| S7 | Slot and drain transfer (§7) | S9 |
| S10 | Multiplexing and accounting (§9) | S1, S3, S4, S7, S8, S9, plus the D-4a selection |
| S11 | Startup union and reconciliation (§11) | S3, S4, S6, S7, S9 |

**Body and caller nodes.** Each needs its spec plus the listed gates.

| Body | Content | Needs |
|---|---|---|
| B0 | SL-0 source changes (§13) | S0 |
| B9 | Custody bodies, journal v2, provisioner source | S9, B0 |
| B-RECV | Full-roster receive, `CrosswalkRequestPeer`, gate updates | S8, B9 |
| B7 | Slot transfer | S7, B9, B-RECV |
| B1 | Scoped canonical operation body, wrapper, `pre_effect` branch | S1, B0. Exports need G-CAPI. Proof credit needs R-PROOF. |
| B2b, B2c | Exchange and K4 successors | S1, S6, G-A1 |
| B3 | Crosswalk and pair producers, V2 controller callers | S2, S3, B9 |
| B6 | `finish` split, adapters, collector settlement | S6, B1, B9 |
| B4 | Delegation successor bodies, helper successor, dispatcher | S4, B3, B6, B7, B9 |
| B10 | Request multiplexing | S10, B1, B3, B4, B7, B9, B-RECV |
| B11 | Startup union and reconciler | S11, B3, B6, B7, B9 |
| B12 | Seal: pins, freeze, enrollment, control rosters | All bodies |

**Integration gates.**

| Gate | Condition |
|---|---|
| G-CAPI | The reviewed C-API successor is composed. Needed before any root-worker export or ABI adoption. |
| G-CAPI-P | L-CAPI-P is reviewed and composed. |
| G-PROT | L-PROT is composed into the base by explicit reviewed import. S5 versions of shared units are used, and shared callers and ABIs are resolved (P1:153). |
| G-A1 | L-A1 is selected and frozen separately. |
| G-DEP | L-DEP is selected, reviewed and frozen. |
| G-RW | Root-worker packets are rebased by R-RW-1 … R-RW-10, and IC-1 … IC-10 pass. |
| G-REVIEW | A different-author actual gpt-6.1-sol review per slice, and a full-lane review before source selection. |

**Runtime and proof gates** (operator or paused infrastructure; §16):
- **R-PROOF:** an admitted strict frame, capacity, storage, and matching-source strict proof.
- **R-LAB:** a root `/srv` lab, provisioning, delegation, kernel measurements, actors, and fault campaigns.
- **R-PUB:** publication. See §16.

### 15.3 Corrections to v1's plan

- **v1 SL-4b (reconciler)** now depends on slots (B7) and historical outcomes (B6), not only on custody (B11 above).
- **v1 SL-5 (phase and peer protocol)** is split:
  - the phase relation's spec (S9) needs only S8;
  - its bodies integrate with descriptor, crosswalk, slot and request schemas through B7, B3 and B-RECV.
- **v1 SL-9 (multiplexing)** depends on the seam-7 accounting (S3) and on the D-4a selection.
- **Final ABI adoption** depends on G-CAPI.
- **v1's claim that SL-1 is "independent of every other seam"** is replaced:
  - S1's spec uses authority, collapse, scoped-ledger and classification types, and the arena conventions;
  - its wire layout waits for G-CAPI;
  - its proof waits for R-PROOF (review §3).

### 15.4 What can proceed now

Passive lead drafting of S0, S1, S2 and S8, which depend only on existing types. Then S3 and S9, then S4, S6 and S7, then S10 and S11. Each is independently reviewed. None of this needs the lab, root or an operator decision.

---

## 16. Operator items (only the reserved decisions; G-7)

| Id | Reserved decision | Blocks |
|---|---|---|
| OP-1 | **D-2a.** Provisioning or installation of authoritative state:<br>- the v2 descriptor installation;<br>- custody journal v2 (U-5), operation head (U-4) and crosswalk (U-12);<br>- the owner plan and run-scoped configuration;<br>- any `/srv` lab installation.<br>Any migration keeps prior chain and history, with its own rollback and crash evidence. Never a re-genesis. | Every seam's runtime controls |
| OP-2 | **D-2b.** Frontier re-enrollment adjudication. **None is proposed.** | — |
| OP-3 | **D-4a.** Any authoritative resource-policy change selected for request accounting (§9.2). **None is selected.** | §9 accepted cases |
| OP-4 | **D-5a.** Delegation policy installation (the root unit's `Delegate=yes`, the coordinator's capability and mount profile). Privileged lab action, including real actor runs that spend model quota (`gpt-6-luna` with high reasoning, only as the WORLDLINE actor through the existing Codex adapter). | §5 runtime, fork and race accepted cases |
| OP-5 | **D-5b.** Privileged installation and execution of the helper successor | §5 runtime |
| OP-6 | **D-7a.** Original API or owner-policy alteration. **None is proposed.** | — |
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 in an authorized lab | §3–§9 runtime evidence |
| OP-8 | **D-9a.** Fault campaigns within the existing specialized-validation boundary: SIGKILL, OOM, systemd or daemon restart, disk full, read-only filesystem, and power-loss simulation labelled as simulation (P1:163) | §6 and §11 crash controls |
| OP-9 | Merge, tag/release, install, sudo, production services, real PRIME | Publication and deployment |

**Scope corrections (RC-11; review §4):**
- **Pure native value fixtures** need no root and no `/srv`. They wait only on their own reviewed frame, ordinary admission and present capacity gates. The protected front and worker entries, by contrast, do need root.
- **Draft publication** — commit, push and draft PR after the required reviews — is authorized by the original prompt (PROMPT:72-74). It is not an operator gate. Merge, tag/release and deployment are (OP-9). v1's OP-7, "blocks publication and deployment", is corrected accordingly.
- **Paused infrastructure.** The lead's STATUS index (a read-only index, not operating-state evidence) records: frame qualification BLOCKED, capacity BLOCKED, no operator approvals, and a storage alert. This design grants no authority to resume any paused window, lab, goal or storage operation. No lab, store, socket, window, service or kernel state was inspected.
- **Optional_Marker** is unchanged by this lane (G-10).

**Kernel and system measurement items.** Every one is unmeasured, and each is needed before the design element that relies on it can be accepted.

| Id | Question | Used in |
|---|---|---|
| K-1 | `SO_PEERCRED` PID rendering for a reader in a child PID namespace and a peer outside it | §8 |
| K-2 | `SO_PEERCRED` stability after the peer exits | §8.4 D8-5 |
| K-3 | `SO_PEERPIDFD` availability (header value 77 observed) and its behaviour for exited peers | §8 |
| K-4 | Pidfd fdinfo `NSpid` rendering through host procfs | §8 |
| K-5 | `kcmp (KCMP_FILE)` between front and worker across PID namespaces, including ptrace access mode | §7.3 |
| K-6 | `flock` semantics for `SCM_RIGHTS`-transferred OFDs versus fresh opens | §6.4, §6.5, §7.3 |
| K-7 | The `SCM_RIGHTS` per-message descriptor limit and `RLIMIT_NOFILE` under large rosters | §7.3 |
| K-8 | systemd `Delegate=yes` semantics: non-interference with a helper-created subtree; hierarchical limits; cgroup type, owner and mode under delegation. Also the readback representation of limits, for example page granularity, as used by E1. | §4.5, §5.2, §5.3 |
| K-9 | `CLONE_INTO_CGROUP` with nested PID namespaces | §5.3 |
| K-10 | A read-only cgroup2 mount without `CAP_SYS_ADMIN` prevents cgroup writes and remount by an euid-0 coordinator | §5.3 |
| K-11 | `cgroup.procs` migration restrictions | §5.3 |
| K-12 | bwrap under a nested PID namespace with `/proc` remounted | §5.3 |
| K-13 | `sockaddr_un` length and `sun_path` extraction for the listener identity | §4.2 P1 |
| K-14 | `SO_COOKIE` availability and uniqueness | §8.1 J5 |

---

## 17. Controls

### 17.1 Retained originals

All of these run first, on the exact integrated candidate. None is replaced.

| Roster | Identity | Content (observed) |
|---|---|---|
| Ordinary roster | `P1/ORIGINAL-ORDINARY-ROSTER.json`, sha256 `4a4cd1b3f605f4f078e15be6ffd75b71dbd80b2420491de80221d42f1a23c41e` | 52 actions (P1:162), with commands and dependency order |
| Lifetime controls | `P1/REQUIRED-LIFETIME-CONTROLS.json`, sha256 `9c836b3e42158c0e71629fda69f3e07e863abf2cd959678075e780c229b178a9` | `tests/test_context_cast_lifetime.py` (5 tests) and `tests/test_finalization_cast_lifetime.py` (9 tests). Status UNRUN. "these additions replace none". |
| RQC | `R/protected-canonical/required_controls.json`, sha256 `56fa3a2d40816c05f3f253ac4bfc4700bc262d5c50fb07b9a6ae3997cb55b2d0` | 27 required genuine cases, 8 additive protected cases, 2 additive native actions, 1 pure native action, 6 fixture requirements. `replacement_of_original_actions: NONE`. `no_skips_mocks_or_fallbacks: true`. Status `SOURCE_ONLY_UNRUN_UNADMITTED`. |
| Protected-startup controls | `R/protected-startup/controls/test_protected_startup_v1.py`, sha256 `a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb` | Includes the frontier control at `:97-105`, on its exact v1 domain (§11.6) |
| Lane and lineage controls | As selected by the freeze (§12.2) | Every other control: canonical stdin V3 controls, operation-authority value controls, canonical-exchange and owner-completion controls, child-authority controls (UNBUILT and UNRUN), and the original native fixture programs (CV-C) |

### 17.2 Additive v2 roster

- A new file, `protected-root/required_controls_v2.json`.
- It enumerates every control of §3.14, §4.6, §5.6, §6.12, §7.6, §8.7, §9.8, §10.6, §11.8, §12.6 and §14.5. Each entry gives:
  - an id and its seam;
  - its kind: pure native value fixture, lab control, fault campaign, or static check;
  - whether root is needed;
  - its operator item;
  - the original case or obligation it serves.
- It is enrolled after the complete ordered original roster and the lifetime controls, and replaces none.
- No skips, no mocks of readiness or custody, no fallbacks.
- Status SOURCE_ONLY_UNRUN.

---

## 18. Everything that remains OPEN

- **All original obligations.** OB-001 … OB-219 stay OPEN (review §5; 219 unique IDs). Nothing here closes any of them.
- **Seam 1.**
  - The specs, bodies and wrappers of S1 and of the exchange and K4 successors.
  - Every lemma of §3.9: L-EQ, L-C2a–f, L-C3, L-CL-1, L-SC-1, L-PJ-1, L-RB-1–3, L-INV-1, CV-B, CV-C, CV-D.
  - Gaps G1–G6. RQ-1 to RQ-3.
  - Checked-build native cost (D2).
- **Seam 7.**
  - `Source_Record` and V2 controller specs and bodies.
  - The exact definition of P3 (RQ-5). The mapping of "minimum/low" (RQ-4).
  - Producer authenticity of observed records (OS workstream).
  - Provisioning the crosswalk (OP-1). Re-review of the child-authority surface.
- **Seam 5.**
  - The delegation and classification successor specs and bodies, including L-V2-1 and L-V2-2.
  - The helper successor.
  - The coordinator enforcement argument (P-CE1–4) and its measurements K-8 … K-12.
  - The dispatcher. Every fork, race, simulate, ghost, prune and revalidate accepted case.
  - OP-4, OP-5.
- **Seam 9.**
  - The custody relation and its invariants INV-C1–5.
  - Journal v2 and its provisioning.
  - The complete crash-point table.
  - Fault campaigns (OP-8).
  - Retention growth, unmeasured.
- **Seam 3.**
  - The T1–T5 protocol bodies.
  - K-5, K-6, K-7.
  - The large-roster controls.
- **Seam 8.**
  - `Join` specs and bodies.
  - The per-gate enumeration.
  - K-1 … K-4 and K-14.
  - OFD and socket custody where kernel evidence is unavailable.
- **Seam 4.**
  - The accounting option (D-4a, OP-3), unselected.
  - Availability and fairness controls.
- **Seam 6.**
  - The `finish` split, the adapters, the collector settlement.
  - Serial parity on matching source.
- **Seam 2.**
  - The v2 descriptor and its schemas.
  - The provisioners and the reconciler (RT-1 … RT-16).
  - OP-1.
- **Seal.**
  - Appended overrides and the external freeze.
  - Enrollment and the integrated roster (§12.4).
  - The C helper's unproved body (OB-048 class).
- **Integration.**
  - L-CAPI-P, which is not yet designed.
  - G-PROT, with shared caller and ABI resolution.
  - R-RW-1 … R-RW-10 and IC-1 … IC-10; IC-10 needs the admitted frame.
  - CAPI4 is itself unreviewed.
- **SL-0.** The complete receiver-resolved lock audit (N-6), including the L-A1-lineage files and `run_service`. Implemented deadlock freedom is not claimed.
- **Proof and runtime.**
  - The admitted strict frame (R-PROOF).
  - The full matching-source campaign with floor 251, the sole boundary, and zero unproved, justified and `pragma Assume`.
  - The 52-action roster, the lifetime controls, RQC and every additive control.
  - Hosted assurance and publication (R-PUB).
- **Operator.** OP-1 … OP-9. Paused frame, capacity and storage gates.
- **Process.** The independent actual gpt-6.1-sol review of this v2, of every slice and of the full lane.

---

## 19. Non-claims

- This document reviews, accepts, qualifies, proves and authorizes nothing. Every original Phase One obligation and every lane seam remains OPEN.
- Nothing was compiled, run, imported, proved, tested or measured. Every design is an untested engineering hypothesis.
- Hash and inventory agreement establishes only byte identity. It establishes no authenticity, atomic snapshot, installed state or producer correctness.
- Statements marked [unverified reasoning] are the author's reading of kernel, systemd or Ada visibility semantics. Each needs the named measurement or the installed-compiler check.
- Observed counts are tool outputs. The derived numerals (J01–J18) are JACKAL `exact`, `formal=false`, informational about arithmetic only.
- SIA recall and prior Claude notes are model-origin recall, not evidence. The lead's STATUS index is not operating-state evidence.
- Author checks (scripts, scans, diffs) are self-checks. They do not substitute for the required independent review.
- Nothing here changes any original target, accepted case, deterministic fixture, control, contract, threshold, proof floor or scope. Temporary named refusals mentioned here keep their obligations OPEN.

---

## Appendix A. JACKAL results

Every call used the MCP tool `jackal_exact`. Each returned:
- `status=exact`, `formal=false`, lane `rat`;
- assurance "exact rational arithmetic (not yet checker-covered)";
- evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`;
- the three non_claims of §C.4, verbatim.

There is no consequence ceiling beyond informational use. Full records are in `jackal.json`.

| Id | parsed | exact | Use |
|---|---|---|---|
| J01 | `535-419` | 116 | S5 names after the common prefix, none in the lane (N-1) |
| J02 | `614-419` | 195 | Lane names after the common prefix, none in S5 (N-1) |
| J03 | `485-419` | 66 | Preimage names after the common prefix (N-1, §12.4) |
| J04 | `614-485` | 129 | Names added by the draft and child union (N-1, §12.4) |
| J05 | `66+129` | 195 | Consistency of J02 with J03 + J04 |
| J06 | `2+30+9` | 41 | Lane Off files by class (N-3) |
| J07 | `2284-1166+1` | 1119 | Lines of the draft's appended C_API block (N-4) |
| J08 | `1160+6+1119` | 2285 | Consistency with the observed draft line count (N-4) |
| J09 | `56596-56543` | 53 | S5 versus preimage C_API byte difference (§14.1) |
| J10 | `34-31` | 3 | `External_Name` occurrences added by the draft (N-4) |
| J11 | `1165-1160` | 5 | Anchor offset, draft versus S5 (§14.1) |
| J12 | `6-1` | 5 | Offset explained: 6 inserted `with` lines minus S5's one line (§14.1) |
| J13 | `129-8` | 121 | Additions carried after replacing the 8 C_API names (§12.4) |
| J14 | `613-606+1` | 8 | Count of enrolled names inside `Worldline.C_API` (N-2) |
| J15 | `275-244+1` | 32 | Lines appended to the draft C_API spec (N-4) |
| J16 | `1+1+1+1+1+1` | 6 | Bash commands that discarded standard error with `2>/dev/null` (C.1) |
| J17 | `1+1+1+2+1+1` | 7 | `2>/dev/null` occurrences in those commands (C.1) |
| J18 | `1+1+1+1` | 4 | Bash commands that used `2>&1` (C.1) |

**Observed counts used without derivation:**
- roster lengths 614, 485, 535 and 535;
- LCP 419 and 485;
- set differences 116, 195 and 66;
- effective pin keys 191, 171, 169 and 167;
- pin statements 16;
- `External_Name` occurrences 31 and 34;
- line counts 1160, 2285, 1161, 244 and 276;
- renamings 25 and 14, `use` lines 29 and 22;
- Off files 41;
- 84 non-attribute and 67 attribute uses of `Size`;
- `gate.mutex` sites per file;
- RQC list lengths;
- lifetime test counts 5 and 9;
- v1 slice line counts.

---

## Appendix B. Bound inputs (sha256 observed while drafting v2)

```
531d11282f811518b868470c0012f23a5e34bdbe3891ef39194cd8f230933f46  D1V/SEAM-DESIGN.md
b8fa87fb573596de9fa0a789b7a8c93c909eeeb18f4d192edad73e038a2caf5d  D1V/seams.json
a1e54a5b0f58e54fec854d3b3eda8780ddaa1a956169f1ac547e1a033722f496  D1V/review/gpt61-v1/REVIEW.md
721bce3ae3e7444fed19ee502c6ac6f3620c0aaedb3a5caa26c6c5a596f00bd4  D1V/review/gpt61-v1/review.json
b1834ee42369df2a907147874a671c39891c587852bb5b79229c0400db66d498  D1V/review/gpt61-v1/checks.json
f6f31ddc0bff4dd59ecccfa389f48ce85c7ad91900fe844cf72293a7d7cb1603  D1V/review/gpt61-v1/review-freeze.json
86e13a18d1e382db4291895a06eb99df623c7bc45edd2efcd1c061d063fa01fe  D1V/review/gpt61-v1/checkpoint-1.json
46f5db369033b812e859a9e8caafec0721a0de4e088621771c9aad66a526c2b2  D1V/review/gpt61-v1/checkpoint-2.json
c288826810d428957c6ba9927cf98db9dc7551728bf94db48a2fc99461802450  D1V/review/gpt61-v1/checkpoint-3.json
39d43cd4e158d56dc8e1ec9bd2e99d7719ff5c4c18585ebe835d1292f60e8064  D1V/review/gpt61-v1/checkpoint-4.json
a899122a4e145033816f8c073e16f492bdbefd969ef9fa38dba4995651f2e55c  D1V/review/gpt61-v1/checkpoint-5.json
2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237  P1/HANDOFF.md
004c71a8da3cb4e917812af427a1701bde226a18da615bcdbf483414d75f187e  P1/START-CLAUDE.txt
1587e068fc2c31a562e38b459728a75dbf7e8d7d9f8afb8efa1474e2a702aeec  P1/OBLIGATIONS-v2.json
16d28b04bf937ecc7003a0a4fcf1b62d78b1478cb79542d9341022acc5f95acb  P1/ALL-ORIGINAL-OBLIGATIONS.md
9c836b3e42158c0e71629fda69f3e07e863abf2cd959678075e780c229b178a9  P1/REQUIRED-LIFETIME-CONTROLS.json
4a4cd1b3f605f4f078e15be6ffd75b71dbd80b2420491de80221d42f1a23c41e  P1/ORIGINAL-ORDINARY-ROSTER.json
1b228f4b07209c91c8f8770851906a8ebbf90db12f0af605954aff392946b327  PROMPT (/home/sicarii/Documents/complete-phase1-prompt.txt)
f0d6add2f97011654d9a603df9f50f8c09d73e80cd4f3fcc37150af3ad77d14d  L/handoff-to-claude-v1-retry1/HANDOFF.md
c8c6e40addc56654f28f7517f0c5ff64cc999424e1ae9ccb831fd799da96f33c  L/handoff-to-claude-v1-retry1/handoff-freeze.json
be41995133b8641ba244397e1cf6068bade22f478bdbe15590ddaf55a2f6bb16  L/handoff-to-claude-v1-retry1/binary-delta.json
0a12d06d2b43a1949bac24369dc615576105b3d6de11e5653ebfe559235637f3  L/handoff-to-claude-v1-retry1/source-inventory.json
de2406cca971d51681a2b9c6265cbb4f5d22f6070c66f75f6e5d2349166c364b  L/handoff-to-claude-v1-retry1/human-delta.patch
d120385a97432f736e73454effe0ce00859ba2ace846e17f11ef5ee9226d4f74  L/origin.json
a87f12865e30789d850cff3a25c69f3ea1793f8dae47404b82acb751efb3a6f9  L/secondary-source-union-v1.json
f0162dc8d5371e6475ac97455943d88a039f91f4cb576ca6ff57ebb26c43a1ec  L/secondary-source-union-relative-import-closure-v2.json
74d3f2f95a830738fcfdb741494d0b9ee1f021e63d150bcb77d51a7cf56e14d5  L/dependency-source/lab/intent_gate.py
3000e60ec8e7ae3a0c8680c29bafa9e866452aea7901d5ebc034d6d35822aab3  L/preimage/runtime/worldline/proof_manifest.py
1cf650a0633ec83af3f2e23f3e87ed5a97199730114d3aa3a16813bb15cdd984  L/preimage/core/worldline-c_api.adb
acf5ac0fb4035d53c3e053e7a3a10b4f29fd29d5bc0aefbdb0d9de181665080f  L/preimage/runtime/worldline/protected_scoped_resource_runtime.py (equal to R's copy: unchanged by the draft)
aa3ab1fefeb75fe3f6cdd5ecf3b7c3107c8550e14c66b964b84c2ea244be5639  R/runtime/worldline/proof_manifest.py
806f3972277d9385b0d32c5e3faf1bf6fb24f9024dbc1c8274411b8c1d0e3420  R/core/worldline-c_api.adb
d09a7b669ea71dd4833a468c627a578d1459ccf1d18840f9ba9a31e40b6f6c8d  R/core/worldline-c_api.ads
33dbdb12904ef70c57809fed581e2e03a1e35b9f3935b30916f2c5e3cd8f0782  R/core/worldline-canonical_operation.ads
c5821527426f828807ed4eff37bc0be31df0b4cb8159e8c91fa4734410fe5f9c  R/core/worldline-canonical_operation.adb
65a38d24f3c5444bd21bc15ecf8dee6ec9e2e93a71ba911f6678ca9b4797562d  R/core/resource_run_ledger.ads
d25a94919a8bed008d007273ab6a887159bd1dd367d71e9a428f2e5bbd96f5ef  R/core/resource_scoped_run_ledger.ads
23c43aaaad873052b8e2e192a4c33a46b1d08f7b427f11f7b27f10602553c07f  R/core/resource_observation_classification.ads
5aafbe6337572c6be44801900387cde2be776b0cdf55775ef09331f48dfd0ba9  R/core/worldline-resource_child_execution.ads
fe3fd5583b5aa91ac902bc969c389ede02962976103118ed7c85e8f09d958b66  R/core/worldline-operation_authority.ads
c0c62623152021d578cd65b96efce18a0cc7805e5c4b25fdde923c949db193d7  R/core/worldline-operation_authority.adb
ea4397f3b8b1e4561603253dddcc5f9515116f4096d35b8ead50fbfe70470e0d  R/core/resource_quantities.ads
570a1cd5fc4ffb20cef000eb669cf0c15105e8a7e70f737c2933c8c2fd676c20  R/core/resource_reservation_transition.ads
ab9555faadd4b46d294a09d8d74495b75ef017497acde9290849cf005aed921a  R/core/worldline-recovery.ads
f2a321d07e667e80f4359634e8e4a956b555368b8d449e8c8c930b8f511aeff7  R/protected-root/native_root_worker_supervisor_v1.c
a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb  R/protected-startup/controls/test_protected_startup_v1.py
56fa3a2d40816c05f3f253ac4bfc4700bc262d5c50fb07b9a6ae3997cb55b2d0  R/protected-canonical/required_controls.json
ea1a01df19ddef2418d4e4ec14dab6cea1eaa70423172eedea36a48ec383f0cb  R/runtime/worldline/protected_operations.py
acf5ac0fb4035d53c3e053e7a3a10b4f29fd29d5bc0aefbdb0d9de181665080f  R/runtime/worldline/protected_scoped_resource_runtime.py
e062ff0335d312366c90517cca21c73c0879d0b95de469840c36cea46250248f  R/runtime/worldline/protected_scoped_resource_service.py
fc6f00f698160f1a854ef7ae72c425f3c7ed11243809b6dac1a5132c0e2ad33f  R/runtime/worldline/protected_resource_runtime.py
8d03960180e599f192d997a4b3809dc0f4e1a7624f9d4581a6b8a51fcae107ed  R/runtime/worldline/protected_scoped_supervisor_v3.py
2510f8edac3937509d36bc3b38511af89f81ecf9a5eff77fefc87f927f3aa811  R/runtime/worldline/root_worker_journal.py
25f38ae7c1b63f14329400155562c18e459b80f46797851ef81d82db03172169  R/runtime/worldline/root_worker_custody.py
1022187a02c19fb25ecfcafcc9a43a91e5ab62cf243ae38014c14d4c73463ade  R/runtime/worldline/client_peer.py
15cbbfcd61a98da55a704af16fd5d853a3af64bc0aba84599d936440ba8f74a1  R/runtime/worldline/protected_root_worker.py
f3cda07cf0556a515c9b41663d16a8a8f34bb3e4c27ed584869791628a8e4778  R/runtime/worldline/protected_root_observation.py
f1089a091399dd0c1a0602aebb027edff4737fbf562750e95e3a0c561067f723  R/runtime/worldline/protected_root_resource.py
100d635842c0df20b1a98921fbfcebc94f2ba862abc0b02a10d1792359c286b0  R/runtime/worldline/protected_root_endpoint.py
68740eda2668faddfe28bd3a8ac1720adac3de32f0bc68d8d95e45f94170d07b  R/runtime/worldline/root_worker_closed.py
774e35565b93aef70420183a591ceb3acf9ddc9148c0b4ae55fb83bb9efc83ce  R/runtime/worldline/root_worker_endpoint_router.py
474d775856a819ea7b5a333bb232651b3641cd4f4788a040a3a3193e847a9c5b  R/runtime/worldline/root_worker_physical.py
7c089300563f417c2467cb9c327202323071664762fa4c8c1df2d575915e3939  R/runtime/worldline/canonical_actor_execution.py
b7c44b329c8c92701c06fcdfd7b5e6692b8b164ae7f699729afe60d0d30036a0  R/runtime/worldline/canonical_operation_kernel.py
5ec258a2cbb06a8dbcc5ab02e214d111ff2845b26c19a456c5ba360cf7ea231d  R/runtime/worldline/canonical_full_broker.py
e29a14a63d67fa3228ede57f0ad12aaa55cbf7c7cf61a8bc09971d5731680ca6  R/runtime/worldline/protected_startup.py
a0781e70e8a4b2b630f6956d0c89208140edc871c4a2a003666573767a32d13d  R/runtime/worldline/admission.py
0a17c0efb95904ee865182a20d3bcabceeef93b1cc3639687aab27696339f35b  S5/core/worldline-c_api.adb (= commonV4)
3a3b17c47bb289e24adc3009e0a5a7510972fac07323f636cbd5722e6344319a  S5/core/worldline-c_api.ads
51dd30d1a2c19cea4b9794e869400c5cb7c4193043f66678e62efa695b058fcb  S5/runtime/worldline/proof_manifest.py
09f82299af37c975b409596fb342f1ef961e309354765cde966189f23a2ee3fe  S5/core/worldline-recovery.ads
a0e0bb5cbca667ad8e02eff9ea79c80459f4066544542178362257dbe347fa3e  W/work/claude-composition-v5-beta/composition.json
3407119bdf9e8497ed8259d76ea783f6d207f15fd155ee9c45534c3b0eaf937a  W/work/claude-composition-v5-beta/source-inventory.json
a9b5dcce5ca5808f8049ae8e7020a79c3fbfc33cc4dcbcc3706fd8f4f40fbfd6  CAPI4/DESIGN.md
39ca995998d68b57d13c02796ee30d8826eecc07e750abf95a83f7d348f7d626  CAPI4/APPENDIX-BINDINGS.md
5592df3a6330da44e60957c8754e50972b6ac0ccfbdc1a53308365e9ccc5f1a4  CAPI4/APPENDIX-COST-MAP.md
59e71dd68724b0420b670d79a99ea74194134dbc6d219b7b91f146ad01843625  CAPI4/decisions.json
9fe93d9dd4257aa6ea188278fecedf5971a0ac34135a390f45908d3ac80b14b0  CAPI3R/REVIEW.md
ab7efb2bc69d426f9480246bc2dd1f5e381d99879485d4385837ec1105d85223  CAPI3R/review.json
7314f4de53972acbac91541d6a895072a50c264119dfe25e5c20b04ae63512ca  CAPI3R/review-freeze.json
e5b9984d2beadf12f35e3018aff33c23a47d93adea7bd886abe8df2db46574b6  D2D/INVENTORY.md
03fbf2461e857ddf9a3a0bdcf2515a14ccb6cd8498ade4e682a8a4bb60f02820  D2R/REVIEW.md
20e0447f556d9f18e9b8a24e5c96056317b52ccee3d29fe804c65cdee2c9c578  D2R/review.json
f94a3cce4a2727340c64b16c638e0fc6f9572cf979741bd4fbf55e6e6c2ac7e9  D2R/review-freeze.json
5016becf1395e56f2fb01f1c2a2201d3add9c1b7caad98b00f608103c7bfce0a  CHILD/review/gpt61-v1/REVIEW.md
322ec24f74a742275ca34b1ec97ebabd88ce22fce5b75bfca0c5c53042e40d3c  CHILD/review/gpt61-v1/review.json
79d9f875bdcd17d8c2bb8add0155d15235a045706ecdb7bf60e946697ae62a40  W/work/claude-lead-v2/approvals/optional-marker-api-v1/approval.json
acf5ac0fb4035d53c3e053e7a3a10b4f29fd29d5bc0aefbdb0d9de181665080f  CHILD/source/runtime/worldline/protected_scoped_resource_runtime.py (equal to the lane's copy)
7c089300563f417c2467cb9c327202323071664762fa4c8c1df2d575915e3939  CHILD/source/runtime/worldline/canonical_actor_execution.py (equal to the lane's copy)
fc6f00f698160f1a854ef7ae72c425f3c7ed11243809b6dac1a5132c0e2ad33f  A1/source/runtime/worldline/protected_resource_runtime.py (equal to the lane's copy)
9d8cc8345f133cff4859a799580117bb2666ff59a53bb9c15557fd05a7390794  A1/review/gpt61-v1/review.json
47a775a2718fa721d357dcf948da2aa2216438f84cb109dd6dcbc4e4a1c74fcb  A1/review/gpt61-v1/review-freeze.json
```

`WT/STATUS.md` is the lead's live index. It is read only, it is not evidence, and it is **not bound**. It changed while v2 was being drafted: observed first as `775ca1a5…`, later as `afc93363…`.

---

## Appendix C. Bound v1 slices and line replacements

- v1 `SEAM-DESIGN.md` has 1329 lines and ends with a newline. Its whole-file sha256 is `531d11282f811518b868470c0012f23a5e34bdbe3891ef39194cd8f230933f46`.
- Each slice's sha256 is that of the UTF-8 bytes of its lines, each line followed by `\n`. A read-only script computed them.
- CARRIED_VERBATIM slices are part of v2 exactly. CARRIED_WITH_LINE_REPLACEMENTS slices are part of v2 with the listed v1 lines replaced by the text below.

| Slice | v1 lines | sha256 | Disposition | Used in |
|---|---|---|---|---|
| B-NOTATION | 46-61 | `08d331e08f8659a520bb86dac169b2f9b4985c948f503b3b314b5fb5befe7b41` | CARRIED_VERBATIM | RR1 |
| B-P0 | 72-151 | `e61cd9f936685c1931ad93429bb23fe4b669b3c6d54dbf0f652b482c0321a993` | CARRIED_WITH_LINE_REPLACEMENTS (R-1, R-2) | A.3, §13 |
| B-S1-CUR | 169-195 | `514de20c4d9ba15da31d8f48cdb1772c5a9dca559099de479dafb191df7b7a17` | CARRIED_VERBATIM | §3 |
| B-S1-REQ | 197-213 | `dc6c3d91efda0993ef6255f7fce95a96c2b9b4f644465418284753d07d1a2413` | CARRIED_VERBATIM | §3 |
| B-S2-CUR | 323-351 | `83d8232004997e316647ef43a37a1124470b1745ec5443dd6f2f5b88a9e80259` | CARRIED_VERBATIM | §11 |
| B-S2-REQ | 353-369 | `e79a931a292d012654378044fd7c9ac77e236b48358b481ce91665dc429478ac` | CARRIED_VERBATIM | §11 |
| B-S3-CUR | 456-471 | `705c8b7823440d001ece1ccf3205208980d6ea02e06bf7a07f825ee41c469768` | CARRIED_VERBATIM | §7 |
| B-S3-REQ | 473-481 | `ed1a12df1ae01dfb4743c4b1d80b3ab0e5a4d1457aed6eaa43ba357dd4145793` | CARRIED_VERBATIM | §7 |
| B-S4-CUR | 533-548 | `69b63f24b45323bf3e774aecb31765dbbf1e4639647dc187934908d536289a00` | CARRIED_VERBATIM | §9 |
| B-S4-REQ | 550-558 | `54c66b823906346a56597678473d5b6577b262e5d6b7b6829a7eb11293f1b31f` | CARRIED_VERBATIM | §9 |
| B-S5-CUR | 632-644 | `ff1c4209dd9e5d5e55f754eda03e846368f656ead39fd7f4eeeb70cd1bde2f2b` | CARRIED_VERBATIM | §5 |
| B-S5-REQ | 646-659 | `23e7c4449b6df68fb28d7370d4957a49c63eadf93669167ef521702ead7ace68` | CARRIED_VERBATIM | §5 |
| B-S6-CUR | 748-764 | `8a50e1d7df8408c52c65c0f725ec75fd3ec556c00cadb1aaa344d55eb7ceb698` | CARRIED_VERBATIM | §10 |
| B-S6-REQ | 766-776 | `41120d75c2c1c762dcbc61d237ca66c3a2ca647a20d4e3a849b3cf53e004c23b` | CARRIED_VERBATIM | §10 |
| B-S7-CUR | 832-856 | `1b1b53e6c79ddb34ef8f146377c75e9a1391a389bcd70e0d7106cc7042640a88` | CARRIED_WITH_LINE_REPLACEMENTS (R-3) | §4 |
| B-S7-REQ | 858-865 | `6576a14839ff9996b4bf54ae5453f5f04169a053b7c71f9fb39f9cba4d15266c` | CARRIED_VERBATIM | §4 |
| B-S8-CUR | 928-945 | `1a204ee1c9d87de6d996f003f456f2443b7e2daf686f19359aa3043ba71e6b02` | CARRIED_WITH_LINE_REPLACEMENTS (R-4) | §8 |
| B-S8-REQ | 947-958 | `1a2298439ca37d6656a57278cfb93124e240a80261ef55542ca4284c5911ceba` | CARRIED_VERBATIM | §8 |
| B-S9-CUR | 1033-1071 | `5092b947ea146505f7e5dfa764c4df55ba4e67069bd9062e18bd1e078591b919` | CARRIED_VERBATIM | §6 |
| B-S9-REQ | 1073-1082 | `eb731c8247643108b691bb810e1c9f6f4ae9b1d181bac48f0edf895bdaee940e` | CARRIED_VERBATIM | §6 |
| B-S10-CUR | 1153-1163 | `df8962cc5afe7519913582c624671971cae5e68c5bb80e6b2c89a6ae486c88b9` | CARRIED_VERBATIM | §12 |
| B-S10-REQ | 1165-1174 | `bc9f9c701a5df8616b3b44f92d70d4a1354e016f0336b1faf50cbc2967fb3d7e` | CARRIED_VERBATIM | §12 |

**R-1** replaces B-P0 lines 84-85 (the conditional deadlock, review F-02):

```
- `CanonicalOperationPrincipal._reserve` calls `intent_for_operation` (`rw/protected_operations.py:640`).
  A request that reaches this nesting with the selected `threading.Lock`, having passed the preceding
  checks, cannot progress (review F-02, SUPPORTED_STATIC_CONDITIONAL: source reasoning, not an observed
  hang; current startup refuses earlier). Further nestings on the same path: A.3 N-6.
```

**R-2** replaces B-P0 lines 139-140 (lineage naming, RC-11):

```
- The lane changes `core/worldline-c_api.adb` from 56543 to 148068 bytes (observed). That overlaps the
  C-API consolidation successor (L-CAPI; design v4, unreviewed). The scoped committed envelope is the
  separate lineage L-A1. The integration design is v2 §14.
```

**R-3** replaces B-S7-CUR lines 853-854 (review F-07):

```
  The process `source_lease` is caller-supplied the same way (`:74-76`, `:121`). The named native
  `Controller_Valid` identity equalities are therefore vacuous (OB-030); its other predicates remain
  real predicates (review F-07). Classification `Facts` pairs show the same pattern (v2 N-10).
```

**R-4** replaces B-S8-CUR lines 939-941 (review F-09):

```
- **[unverified reasoning]** A peer outside the reader's active PID namespace may read PID 0. The helper
  comment at `.c:125-128` says the same for its custody sender. Conditionally, for an outside-namespace
  original client whose re-read PID differs from the retained document, `RequestPeer` raises
  `PEER_REQUEST_MISMATCH` (review F-09). Not every intake; kernel behaviour unmeasured (K-1, K-2).
```

---

## Appendix D. Companion file identities

<!-- APPENDIX-D-PLACEHOLDER -->
