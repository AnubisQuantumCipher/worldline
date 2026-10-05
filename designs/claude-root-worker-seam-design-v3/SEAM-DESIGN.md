# Root-worker runtime lane: seam design v3

| | |
|---|---|
| Author | Claude Code lead claude-opus-5-5 (drafting subagent, author role) |
| Date | 2026-10-05 |
| Status | **DRAFT_FOR_GPT61_REVIEW. No source was written. Nothing is accepted.** proof_acceptance=false, source_acceptance=false, phase_acceptance=false. The author grants nothing, and no author check in this document is a review. Every original obligation (OB-001 … OB-219), accepted case, deterministic fixture, control, contract, threshold, proof floor and scope remains **OPEN** and unchanged. |
| Supersedes | v2 `SEAM-DESIGN.md` (sha256 `db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5`, 224640 bytes, 2296 lines) and v2 `seams.json` (`65a8c73028ad1cb22550bf26ffb3d0027ce125c3ac4b29b64def7765a83415c4`). Both were read only and re-hashed unchanged. |
| Answers | The sealed actual gpt-6.1-sol review of v2 in `WT/designs/claude-root-worker-seam-design-v2/review/gpt61-v1/`: `REVIEW.md` (`1a41b5c5bc0b0fba759ecd66357c401a8b5cdee6c5bf1e3914d6989242f010ac`, equal to its `report_sha256`), `review.json` (`84c176dfc3f2f49deb2a0967da90179ab1e80681e00fa33203a158066d01b942`), `checks.json` (`63a36b12ec283916619a668162129ea4562dc316ec30a0410f45b42d2d124fe4`), `review-freeze.json` (`d40060e5d9cdea0f65c117b95a1048570a3e3d18c6ce002efa8d1d8a2198c32b`). The freeze lists the three files with hashes equal to those observed. Verdict **ENDORSED_WITH_REQUIRED_CHANGES**. RC-05, RC-10 and D-2b are CLOSED_AT_DESIGN_LEVEL. Every other required change and ruling is PARTIALLY_CLOSED. Required changes V2-REQ-A … V2-REQ-L. RQ-1 is PARTIALLY_CLOSED with its own required change. |
| C-API predecessor status | The sealed actual gpt-6.1-sol review of C-API design v4 in `WT/designs/claude-capi-boundary-design-v4/review/gpt61-v1/`: `REVIEW.md` `3d1ef7f8…23e4aa`, `review.json` `d7bf825a…1f4e`, `checks.json` `d70fe467…6963`, `review-freeze.json` `f1dcb0a7…13dc` (all recomputed and equal). Verdict ENDORSED_WITH_REQUIRED_CHANGES. **V4-RC4-GATE and V4-RC4-ALIAS are OPEN** and carried as predecessor obligations (V-K.1). C-API design v5 (`WT/designs/claude-capi-boundary-design-v5/DESIGN.md`, sha256 `533f0e043fb991d015bcf16494674d791b6f8f8bd5049fef5a8e60594c9341de`) answers both but is **UNREVIEWED**. Nothing under its `review/` directory was read. Every dependence of v3 on v5 is labelled **[depends on unreviewed CAPI5]**. |
| Scope | Design only, for the draft lane `W/work/protected-original-root-worker-repair-v1` (status `INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY`). The lane draft is someone else's unreviewed source and was not touched. v3 grants no execution, proof, build, test, review, operator or acceptance authority. |
| Location | `WT/designs/claude-root-worker-seam-design-v3/` |
| **What this document consists of** | v3 is (1) the text of this file; (2) the v2 `SEAM-DESIGN.md` line ranges listed in §B.1, each bound by the sha256 of its exact bytes, with the quoted line replacements R3-1 … R3-43 of §B.2 applied; and (3) transitively, the v1 slices that v2 binds in its Appendix C, which slice C2-APC carries verbatim. Every other v2 text is replaced, by the map in §B.3. |
| Companion files | `seams.json` (machine twin, same schema family as v1 and v2), `jackal.json` (JACKAL record), `AUTHOR-NOTES.md` (unresolved items, uncertainties, reviewer guidance, process record). Identities: Appendix D. |
| Write history | Every file in the location above was created or changed only with the Write and Edit tools. No Write or Edit was refused. Bash was used only for read-only inspection (AUTHOR-NOTES §5). |

Every statement about source in this document is **static**: read from files, or reasoned from what was read. Nothing was compiled, run, imported, proved, tested or measured. Kernel, systemd, interpreter and Ada-visibility statements marked **[unverified reasoning]** are the author's reading and name the evidence they need.

---

## A. Closure tables

"Answer" is a design statement for the reviewer. The author closes nothing. Every proof, native, control, physical and acceptance obligation stays OPEN.

### A.1 Required changes V2-REQ-A … V2-REQ-L

The change text is quoted verbatim from the sealed `review.json` `required_changes[].change`.

| Id (targets; rulings) | Required change (verbatim) | v3 answer | Where |
|---|---|---|---|
| V2-REQ-A (RC-01, RC-03, RC-07, RC-11; D-1a, D-5a, D-6a) | "Specify typed V2 consumers end to end: scoped canonical Reference/Decide, exchange and K4 successors, facts/current-observation packets, wrappers and producers. Use the delegated Classify_V2/Native_Valid_V2 relation where required; keep every V1 reference and ABI unchanged. Add the consumed crosswalk/V2 and B2b/B2c/B6 dependencies to the body/gate graph." | Two typed families with no implicit bridge. V1 (every original unit, unchanged) decides v1 deployments and every row produced by the original producers. V2 (additive) gives each consumer a `_V2` entry: scoped canonical operation, scoped exchange (B2b), scoped K4 (B2c), root admission, child decision, task admission and scoped `Check_V2`. Each is typed by `Facts_V2` and per-row delegation selection. A deployment-level selection, made by the exact v2 descriptor schema plus authenticated crosswalk entries, puts every row of a packet in one family. Exact-type wrappers dispatch `ScopedPacket` to V1 exports and `ScopedPacketV2` to V2 exports, and no conversion between them exists. The only bridge is the Ghost lemma L-BR-1. The graph adds the crosswalk, V2 and B2b/B2c/B6 edges. | V-A, V-M |
| V2-REQ-B (RC-01; D-1a, D-1b) | "Complete the original-domain correspondence rather than declaring a total embedding over uncovered arenas. Supply the multi-frame construction and saturated-arena construction, distinguish raw-invalid and legitimate producer domains without excluding original accepted cases, and prove each extra conjunct from the original caller domain. For RQ-1 give the command/caller/time mapping and retain Retained_Join wherever originally accepted; qualify multi-frame/multi-bucket refusal fixtures by the actual violated predicate and include valid positives." | The totality claims are withdrawn. Domains D_raw, D_prod and D_emb are defined, with three exactly stated residuals. A witness field is a present zero-length span, an alias of an original span, or fresh bytes. The single-frame, multi-frame and saturated-arena constructions are given, with lemma L-SAT-1 for the positive projection factor. Producer-domain lemmas PD-1 … PD-5 discharge the extra conjuncts. RQ-1 is answered by a command-by-caller-by-time table. The scoped conjunct uses the RETAINED join for every caller, and current-context checks stay only in the native Reserve, Record_Launch_Intent and Record_Running. Refusal fixtures are qualified by their violated predicate, with valid multi-frame and multi-bucket positives. | V-B; C2-31, C2-36, C2-37, C2-39 with their replacements |
| V2-REQ-C (RC-02; D-7a) | "Define feasible native extraction/framing for unchanged expected containers, explicitly join every expected Anchor to the authenticated controller/genesis roster, specify per-domain field/side grammars and the full dynamic crosswalk, and complete P3 with precise executed-source coverage and retained non-claims. Keep original producers/cases until authentic V2 producers and joins are designed; copied/relabelled-source assertions must follow from those exact predicates." | Expected records are a JSON path into an unchanged canonical container, extracted by a native canonical-JSON recognizer and path resolver. WL-SRC-V1 framing is kept only for new producer records: every observed-side record, and the expected records of producer domains. A native `Roster_Join` ties every expected anchor to the custody genesis, the descriptor's installed inventory (`files` and `trees`) and the crosswalk. The per-domain grammar table, the crosswalk schema with native decode and plan, cost and follow-up joins are given. P3 is defined as a native subset relation over mapped executable images, with stated non-claims. The V1 controller and producers stay for v1 deployments. | V-C; C2-41 with R3-38 … R3-40 |
| V2-REQ-D (RC-02, RC-06; D-4a, D-7a) | "Replace E3's future-capacity assertion and RQ-4's memory_high/minimum/low identification with a real full-domain host/ledger/enforcement/cost correspondence. Complete the independent-request accounting comparison without choosing an option or adding a cap, provider prerequisite, resource-policy field or accepted native failure. Any actual authoritative policy change retains D-4a operator selection." | Both statements are withdrawn. A per-resource correspondence covers memory, CPU, tasks, disk, concurrency, time and native cost: ledger quantity, original enforcement, admission sample, protection against interference, candidate mechanism, readback and status. Reserved-capacity completion is claimed for no resource class. Candidate mechanisms are listed for the operator's D-4a decision, and none is selected. The accounting comparison now covers options A, B, C, E and F, with metering, protection, double-counting, availability and cost columns. No option is selected. | V-D; C2-92 |
| V2-REQ-E (RC-03; D-5a, D-5b) | "Reconcile helper and dispatcher into one exact admission/create/measure/native Child_Ready/ACK/GO protocol, including all retained ABI/argv/env/stdin/EOF/FD surfaces. Complete the root coordinator reachability argument over every retained descriptor, writable view, capability and helper-channel command, with authentic native inputs and the original ancestry/containment predicates." | One protocol, E1–E12: admission (Task_Admission), then create (held init), then Running, then GO_FORK, then measure, then native `Child_Ready_Conjunction`, then a durable witness, then ACK (commit), then exec. It mirrors the existing V1 helper order (HELD, 'G', credential frame, commit, exec). The reachability table enumerates every retained descriptor, writable view, capability and helper-channel command, each with its constraint, its native input and its measurement item. Measures M-1 … M-5 close the reachable systemd, D-Bus and procfs write views. | V-E; C2-53; C2-55 with R3-41, R3-42 |
| V2-REQ-F (RC-04, RC-07; D-9a, D-6a) | "Define the full native custody product state and mutation table: root ownership phase, generation, independent per-request and per-descriptor states, and legal gates at actual mutations. Supply complete DDL and CAS/replay semantics keyed to operation, generation, sub-generation/subject and alternative set, preserving exclusive ACK/ABANDON branches." | The product state is: root (generation, phase, owner, closure flags, unknown cause), request(r) and descriptor(d) sub-states, and alternative sets. The O mapping to broker boundaries is given. The legal product relation is given as rules plus a complete O×U table. A mutation table covers every actual mutation and its native gate. The custody v2 DDL is complete, and an `alternatives` primary key enforces exclusivity. The CAS and replay semantics are stated, including idempotent replay and ALTERNATIVE_TAKEN. | V-F |
| V2-REQ-G (RC-04, RC-07, RC-12; D-9a, D-6a) | "Specify the independent physical collection barrier and a complete crash/recovery product table. Separate NEVER_DISPATCHED from any dispatched/no-HELD uncertainty, and preserve automatic recovery of authentic retained RESULT_CAPTURE without an additional HANDLER_TERMINAL prerequisite. Keep canonical COMMITTED absorbing, genuine native quarantine/K4 paths and write-once original results." | The typed barrier `Physical_Closure` holds exactly the namespace closure, the outer wait and the raw drains, plus terminal pidfds. The handler terminal is a separate optional input to the U decision only. A retained first RESULT_CAPTURE settles automatically, as the original startup recovery already does (`rw/protected_operations.py:367-368`, `:812-816`). NEVER_DISPATCHED and dispatched/no-HELD are separate rows. The crash/recovery product table replaces v2 §6.10 and §11.5, and R3-13 removes the handler-terminal prerequisite from the carried phase graph. | V-G; R3-13 |
| V2-REQ-H (RC-08; D-3a) | "Complete drain/slot transfer through stop intent, cancellation/quiescence, in-flight buffers/writes, FREEZE/SPOOL durability, received-roster validation, exclusive intake/abandon and failure/restart resumption. Establish OFD/lock/custody/freshness evidence before authorizing new-owner I/O or mutation, and retain the real helper/init/outer-wait producers." | Per-descriptor protocol H0–H6: durable STOP_INTENT, exact quiescence rules for asyncio readers (a dup-closed transport feeds EOF after its buffered bytes), raw stdin writes and SEQPACKET channels, FREEZE after spool fsync, SEND, VALIDATE (the front journals kcmp and lock-held evidence while it still holds its copy), INTAKE CAS (which alone authorizes I/O), and RELEASE. A failure and restart table covers every window. Stdin EOF is exactly-once or the outcome is UNKNOWN. The root custody lock roster gets the same evidence. | V-H |
| V2-REQ-I (RC-09; D-8a, D-8b) | "Give mode-specific native requester predicates and enumerate every exact-type gate. Bind raw credentials, request/operation/transaction/reservation, custody generation and source containers explicitly. RETAINED/HISTORICAL inputs require typed absence where no socket exists. Establish original accepted-profile coverage for FRESH cookies/namespace evidence or design an authentic domain-preserving path; no still-live-client, fresh-pidfd or unavailable-provider refusal may become accepted." | FRESH, RETAINED and HISTORICAL predicates have typed presence. FRESH requires exactly the original evidence: the front's own original-namespace re-read at transfer, socket identity while the front still holds the socket, and uid/gid equality. Cookies and namespace records are optional corroboration and never preconditions. Every gate (18 sites in 11 modules, observed) is listed with its mode. Original gates keep `RequestPeer` unchanged. When correspondence cannot be established, the request stays queued and is served by the front under the original gate, never refused. | V-I |
| V2-REQ-J (RC-12; D-2a, D-2b) | "Finish exact startup version/loader/schema/creation-slot union, keysets and one-shot provisioning DDL, and connect every original recovery/owner path to the complete native product relation. Preserve v1 behavior and the unchanged frontier control; never initialize missing prior state or replace chain history." | Exact v1 keysets are observed: descriptor, owner plan, custody genesis and custody schema. Exact v2 keysets are specified for the startup descriptor (top level, `root_worker` and `runtime`), the custody genesis and the crosswalk, with the provisioned-state roster, the `files` bindings and early selections. The owner plan keeps its v1 keyset, with a bound schema file. Creation slots and their provisioning order are exact. The DDL is V-F.5 plus the existing operation-head schema. Every original recovery and owner path of `reconcile_before_endpoint` (`rw/protected_operations.py:355-384`) and every RT row maps to the product relation. v1 behaviour and the frontier control are unchanged. | V-J; C2-111 with R3-43 |
| V2-REQ-K (RC-11; D-7a) | "Update C-API predecessor status to the sealed v4 review; carry V4-RC4-GATE and V4-RC4-ALIAS OPEN. Specify every appended stage's complete invariant/table set, indirect and transport-qualified alias handling, branch-correct write/gate rules, residual/glue preservation and explicit G-CAPI -> G-CAPI-P -> G-PROT -> G-RW dependencies. Preserve original rejection diagnostics and exclusive finalization assignments; decide neither lane's acceptance. Scope R-RW-2's declaration/renaming ban and IC-3's uniqueness to the newly designed root-worker additions, while preserving CAPI4's already bound S5 residual and per-scope clauses." | The predecessor status is the sealed v4 review, with V4-RC4-GATE and V4-RC4-ALIAS OPEN. v5 is labelled unreviewed. Each root-worker stage carries the complete floor plus appended RW tables. A per-call expanded-qualifier rule covers root-worker routines, including indirect and transport-qualified paths [depends on unreviewed CAPI5]. Branch-correct gate rows are required, and root-worker stages add no assignment exception. Root-worker stages make no glue edits, and every existing tile is untouched. The gate chain is explicit. The hygiene rules are scoped to the new additions; the S5 residual renames and per-scope `W` aliases are preserved. | V-K, V-M |
| V2-REQ-L (RC-06, RC-11; D-4a) | "Make the complete receiver/Gate/thread/callback lock and availability model part of the normative design. Retain SL-0's single acquisition and original non-reentrant Gate, separately bind A1-origin changes, and specify protected status/cancel/recovery progress through shared locks, stalled I/O and executor occupancy. Keep every original floor and control. Apply all required repairs to prose and seams.json together, including withdrawal of uncovered totality claims." | A normative lock inventory with owners. Thread placement: a dedicated single-thread protected lane, a separate registered-root I/O executor, and loop callbacks that take no locks. Lock order and await rules. Router and collector rules. A progress table for status, cancel and recovery through shared locks, stalled I/O and executor occupancy. SL-0's single acquisition, the non-reentrant Gate and the separate A1 binding are kept. The totality claims are withdrawn in prose and in `seams.json`. | V-L, §B.5, `seams.json` |

### A.2 RQ-1

| Item | Required change (verbatim from `review.json` `rq1.required_change`) | v3 answer | Where |
|---|---|---|---|
| RQ-1 (status PARTIALLY_CLOSED) | "Provide command-by-command and caller-by-caller domain correspondence. Apply current-context checks only where the original native command requires them; design Retained_Join for every required retained-origin path, and retain positive rollover controls. Keep RQ-1 and the original obligations OPEN until that mapping and evidence exist." | The mapping table of V-B.10 covers every caller, its native scoped commands, its time window and the source of each requirement. The scoped canonical conjunct, B2b and B2c carry **no** current-context conjunct; they use `Retained_Join`. Current-context checks remain only in the native Reserve, Record_Launch_Intent and Record_Running (`core/resource_scoped_run_ledger.ads:359`, `:436-438`). Positive rollover controls are listed. v2's FRESH placement is withdrawn. RQ-1 and the original obligations stay OPEN until the evidence exists. | V-B.10 |

### A.3 PARTIALLY_CLOSED required-change clauses

"Remaining gap" quotes the review's `rc_clause_closure` assessment verbatim.

| Clause | Remaining gap (verbatim) | v3 answer | Where |
|---|---|---|---|
| 01.1 | "Typed Reference/Decide/Post and decision subtype supplied; §3 still uses original Facts/Native_Valid, not the delegated V2 classifier." | `Decide_V2` and `Reference_V2` over `Facts_V2`, the delegation selection and `Native_Valid_V2`, with C2-31's clauses; `Decide` (V1) is kept for v1 deployments. | V-A.2; C2-31 with R3-25 … R3-31 |
| 01.2 | "Shared production arena and identity decision mapping supplied; Rebase/Emb is not total while G3 remains uncovered." | Totality withdrawn. Saturated-arena construction: zero-length and alias witnesses need no bytes; compaction when constants are needed; residual R3 stated exactly. | V-B.3, V-B.6; C2-36 with R3-32, C2-37 with R3-33 and R3-34 |
| 01.3 | "Field-level embedding supplied; multi-frame construction and saturated arenas are deferred." | Multi-frame construction with exact validity conditions and residual R1; saturated-arena construction. | V-B.5, V-B.6; C2-37 with R3-34 |
| 01.5 | "Coverage lemmas supplied, but raw-domain-only exclusions cannot discharge the original full-domain target; blanket multi-frame/multi-bucket refusal controls contradict the unrestricted scoped domain." | Domains D_raw, D_prod and D_emb. Residuals are stated and never excluded from the system: the original unit keeps deciding them. Refusal fixtures are qualified by their violated predicate, and valid multi-frame and multi-bucket positives are added. | V-B.2, V-B.7, V-B.9 |
| 01.7 | "Fresh/retained/historical separated; blanket pre-effect FRESH placement and RQ-1 are not established by the launch guard." | FRESH placement at pre-effect is withdrawn. The RETAINED join applies to every canonical caller; current context is checked only by the native commands that require it. | V-B.10; C2-31 with R3-25 … R3-31 |
| 02.1 | "CCE and per-pair producers supplied; P3 remains undefined, and framed Raw-as-subspan of unchanged JSON containers is not specified coherently." | Expected records of container domains are JSON-path values in unchanged canonical containers, resolved by a native recognizer; only producer records are framed. P3 is defined. | V-C.1, V-C.2, V-C.7; C2-41 with R3-38 … R3-40 |
| 02.2 | "Native distinct domains proposed; expected anchors must join the authenticated roster and each claimed raw grammar. Distinct labels/hash-valid containers alone do not establish distinct authentic sources." | `Roster_Join` (custody genesis, the descriptor's installed inventory, the crosswalk) plus per-domain grammar membership. The copy and relabel consequences are derived from these exact predicates; observed-producer authenticity stays a stated non-claim. | V-C.3, V-C.4, V-C.5; C2-41 with R3-40 |
| 02.3 | "Crosswalk covers operation/owner/follow-up dimensions in prose; exact schema, native decode, selected-plan joins and complete costs are pending." | Exact crosswalk schema. Native `Worldline.Root_Crosswalk`: `Entry_For`, `Plan_Join`, `Cost_Join` and `Followup_Join`. | V-C.6 |
| 02.4 | "E1-E4 cover original fields/floors. E3's sampled admission/ledger subtraction does not demonstrate reserved future capacity; memory_high is not a minimum/low guarantee." | The E3 assertion and the memory_high mapping are withdrawn. A per-class correspondence is given; protection is a candidate for D-4a only, and no completion claim is made. | V-D |
| 03.2 | "Concrete P-CE1-P-CE4 mechanisms/observations supplied; helper ordering requires Child_Ready before creation of its measured child. Exact protocol and OS/runtime evidence remain open." | The order is fixed as create (held), then Running, then fork, then measure, then decide, then commit, then exec. The reachability table and M-1 … M-5 are added. | V-E |
| 03.3 | "Original predicates/cases retained by rule; compatibility only covers distinct-pair inputs and S1/B2 consumers still use the old classifier. End-to-end original-domain preservation is not yet designed completely." | The deployment-level family selection keeps every original case on V1. V2 consumers are typed end to end. L-BR-1 states the V1/V2 agreement on no-delegation, pair-valid inputs. | V-A |
| 04.1 | "Native append legality mandatory, but complete Legal table and correspondence at each actual state mutation are pending." | The product relation and the mutation table name the native gate of every actual mutation. | V-F.3, V-F.4 |
| 04.3 | "Head/phase/generation CAS transaction supplied; operation phase and parallel request/drain sub-state need separate retained native state. UNIQUE(operation,generation,kind) does not itself enforce exclusive alternatives or represent repeated sub-generations." | Retained `root_state` and `subject_state` tables; an `alternatives` primary key keyed by operation, generation, subject, sub-generation and alternative set. | V-F.1, V-F.5, V-F.6 |
| 04.4 | "Seed/read-only capture, lost-ACK handling and escrow reuse supplied; selected crash table contradicts RT-2 for dispatch without HELD and omits complete crash/replay state." | The PREPARED row is split into "no dispatch" and "dispatch, no HELD"; the latter is consistent with RT-2. The crash/recovery product table is complete. | V-G.4, V-G.5 |
| 04.5 | "Physical independence intended; §6.7 ambiguously says three awaits while enumerating handler, combined closure/wait, drains, then says physical three. Missing-terminal barrier needs an exact field/future definition." | The typed barrier `Physical_Closure` covers exactly the namespace closure, the outer wait and the raw drains. The handler terminal is a typed optional field outside the barrier; "missing" means Absent when CLOSED_WITNESS commits. | V-G.1, V-G.2 |
| 06.2 | "AM-1-AM-9 and concrete A/B/C/E failures supplied; no accounting option meets the full target." | The comparison is completed with option F and the enforcement, protection, metering and cost columns. No option is selected (D-4a). | V-D.4; C2-92 |
| 06.3 | "Phase/owner/recovery table supplied with exact quarantine.resolve exception; UNKNOWN and collecting progress still depend on incomplete custody/reconciliation design." | Progress through UNKNOWN and collecting follows the product relation, the crash table and the V-L progress table. | V-F, V-G.5, V-L.5 |
| 06.4 | "to_thread and fair queue preserve loop responsiveness in intent, but shared gate/operation lock and bounded executor saturation can still block response progress; no full liveness argument supplied." | A single protected lane, a separate root-I/O executor, the lock order, no awaits under thread locks, and a progress table with its conditions. No unconditional liveness claim is made. | V-L |
| 07.1 | "O/U/C/P and couplings supplied; exact broker-state mapping/legal product table deferred." | The O mapping to broker boundaries, the O×U table, and the C×P rules. | V-F.2, V-F.3 |
| 08.1 | "T1-T5 supplied, but stopping before durable FREEZE conflicts with failure table's claim that reader never stopped." | Durable STOP_INTENT comes first, and the failure table is restated per window. | V-H.2, V-H.3 |
| 08.2 | "Buffers/in-flight bytes intended to spool; interrupted write/cancellation and already buffered stdin output need exact quiescence rules." | Exact rules for StreamReader transports, raw stdin writes and SEQPACKET channels. | V-H.2 H1 |
| 08.3 | "Durable P/W and spool head supplied; FREEZE/SPOOL crash and write-progress linearization incomplete." | FREEZE is written after the spool fsync. W is updated before any await. Crash windows are covered. | V-H.2 H1–H2, V-H.3 |
| 08.4 | "Durable intake/abandon acknowledgement supplied; new owner starts I/O before OFD evidence is recorded." | VALIDATE journals OFD evidence before INTAKE; only INTAKE authorizes I/O. | V-H.2 H4–H5 |
| 08.5 | "Ownership table excludes pre-commit stop/spool failure and post-intake failed validation." | Every window is in the failure table, including validation failure. | V-H.3 |
| 08.6 | "kcmp and lock evidence correctly replace fstat-only proof, but validate before role use and record full-root lock roster evidence, not only descriptor release." | Validation precedes role use. The root custody lock roster gets kcmp and lock-held evidence before CUSTODY_ACK. | V-H.2 H4, V-H.4 |
| 09.1 | "Native raw credential/socket/ns inputs supplied; request/operation/transaction/container joins and mode-specific presence need complete predicates." | Mode predicates with typed presence; explicit joins. | V-I.3, V-I.4 |
| 09.2 | "Journaled host records/full roster first supplied; cookie unavailable yields non-ready intake despite original domain, and validation/ownership ordering remains incomplete." | Cookies are optional. Ordering is: receive everything, validate, join, then CAS INTAKE; any gate use comes after. | V-I.3, V-I.7 |
| 09.3 | "Retained exact type supplied; per-gate list deferred and J1/J3/J4 unconditional fields conflict with socket-free J8 modes." | Every gate is listed. Socket-dependent conjuncts are FRESH-only, with typed Absent elsewhere. | V-I.3, V-I.5 |
| 09.5 | "No pidfd/live-client condition, but FRESH introduces mandatory cookies. No new accepted-case refusal may be approved on provider absence." | Cookies and namespace records never block. When correspondence is unavailable the request is queued and served by the original front path. | V-I.3, V-I.6 |
| 11.1 | "Spec/body graph is acyclic as declared; B1 omits consumed crosswalk/V2 inputs, B2b/B2c and B6 integration edges need explicit reconciliation, and gate precedence is not encoded in body Needs." | New graph with those edges and the gate chain in the body Needs. | V-M |
| 12.1 | "U-1-U-12 union supplied; exact descriptor/schema keysets, provisioner DDL and every early selection remain future spec deliverables." | Exact keysets, early selections, creation slots and their order, and DDL. | V-J; C2-111 with R3-43 |
| 12.2 | "RT table automatic known-outcome direction supplied; RT-7 requires HANDLER_TERMINAL, leaving authentic retained result without that frame unclassified; pre-launch table contradicts RT-2." | RT-7′ settles from the retained result without HANDLER_TERMINAL. The pre-launch rows are split. | V-G.5 |
| 12.4 | "Original K4/quarantine.resolve retained; exact recovery progress through UNKNOWN/locks depends on complete product/native relation." | The product relation, the crash table and the V-L progress conditions; the K4 routes are mapped. | V-F, V-G.5, V-J.5, V-L.5 |

### A.4 PARTIALLY_CLOSED rulings

Owner and evidence text are quoted verbatim from the sealed v2 `review.json` `rulings`, which preserve the v1 strings. "Remaining gap" is the review's `remaining_gap`, verbatim. Each ruling stays with its owner. v3 neither narrows nor adds to any of them.

| Ruling | Owner (verbatim) | Evidence required (verbatim) | Remaining gap (verbatim) | v3 answer | Where |
|---|---|---|---|---|---|
| D-1a | Lead source designer; independent GPT-6.1 source/spec reviewer | Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls. | Typed V2 integration, total arena/multi-frame coverage and all extra-conjunct/caller correspondence remain incomplete. | V2-typed entries; the constructions; PD lemmas; the caller table. | V-A, V-B |
| D-1b | Lead scoped model/caller designer; independent GPT-6.1 reviewer | Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof. | RQ-1 needs full per-command/per-caller placement, not a blanket inference from current-context launch guards. | Per-command, per-caller placement; rollover positives and refusals. | V-B.10 |
| D-2a | Lead authors schema/callers; operator provisions or installs authoritative state | Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls. | Exact version union, all schema keysets/provisioner DDL and full reconciliation remain incomplete; installation reservation preserved. | Exact keysets, DDL and recovery mapping. Provisioning stays operator-run. | V-J, V-F.5 |
| D-3a | Lead protocol designer; operator for lab execution | Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection. | Stop/freeze/spool crash and OFD-validation-before-use barriers remain incomplete; all slot/reaper roles are retained in intent. | H0–H6 and the failure table; validation before use. | V-H |
| D-4a | Lead prepares native accounting comparison; independent GPT-6.1 review; operator selects any authoritative resource-policy change | Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls. | No option selected; no full original-domain accounting/cost/enforcement or protected-response liveness argument. Operator policy selection is preserved. | Correspondence table and options A–F (none selected); progress model. | V-D, V-L |
| D-5a | Lead prepares native/OS design; independent GPT-6.1 review; operator for delegation and privileged lab action | Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls. | Additive model supplied, but old-classifier consumers, exact coordinator authority reachability and future-capacity correspondence remain incomplete. | V2 consumers; the reachability table; the capacity correspondence. | V-A, V-E, V-D |
| D-5b | Lead helper designer; independent GPT-6.1 review; operator for privileged execution/installation | Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations. | Separate helper successor is sound direction; create/measure/decide ordering and exact protocol surfaces still require a single complete design. | The single E1–E12 protocol and its surfaces. | V-E.1, V-E.2 |
| D-6a | Lead historical/canonical model designer; independent GPT-6.1 review | Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement. | Orthogonal directions preserve COMMITTED/quarantine/never-launched/result immutability; product relation and automatic missing-terminal known-result recovery still incomplete. | The product relation; the retained-result settlement without a terminal frame. | V-F, V-G |
| D-7a | Lead native/provenance designer; child-authority and GPT-6.1 re-review; operator for any original API/owner-policy alteration | Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation. | Native pair relation is a useful successor, but container/anchor authentication/extraction and P3/crosswalk coverage are incomplete. Original API/owner-policy reservation is preserved. | Container extraction, `Roster_Join`, P3, crosswalk. No original API is altered. | V-C, V-K |
| D-8a | Lead OS/native requester designer; independent GPT-6.1 review | Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage. | Complete request/transaction/custody joins, mode-specific predicates and exact gate list remain missing. | Joins, mode predicates and the gate list. | V-I |
| D-8b | Lead prepares domain-preserving protocol; operator for kernel measurement; independent GPT-6.1 review | Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client. | No live-client/pidfd requirement is added; mandatory FRESH cookies still need accepted-profile coverage or a domain-preserving design. Measurements remain reserved. | Optional cookies; the queued fallback onto the original front gate; measurements K-15 onwards stay with the operator (OP-7). | V-I.3, V-I.6, V-O |
| D-9a | Lead additive SPARK relation and caller designer; independent GPT-6.1 review; operator for fault campaign | Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes. | Mandatory Legal/exclusive branches/CAS are good direction; product state/schema, all actual mutation gates and complete crash/physical-barrier evidence remain incomplete. | Product state, DDL, mutation gates, barrier and crash table. Fault campaigns stay operator work (OP-8). | V-F, V-G |

### A.5 Items the review closed or preserved, carried exactly

- **CLOSED_AT_DESIGN_LEVEL required changes, carried unchanged:**
  - RC-05 (clauses 05.1–05.5): slices C2-17 (§17) and C2-116 (§11.6).
  - RC-10 (clauses 10.1–10.4): slice C2-12 (§12).
- **D-2b, CLOSED_AT_DESIGN_LEVEL, carried unchanged:** slice C2-116, which holds the frontier control byte-exact on its v1 domain with no re-enrollment proposed. Owner and evidence, verbatim:
  - Owner: "Lead prepares concrete equivalence/adoption package; applicable operator authority; independent GPT-6.1 review".
  - Evidence required: "Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit."
- **CLOSED_AT_DESIGN_LEVEL clauses.** Each is carried by the slices that hold the review's cited evidence. Where a replacement touches a cited line, it keeps the closed property:
  - 01.4 (D:558-611): C2-38 with R3-4, C2-39 with R3-35 … R3-37, and C2-310. W1 … W10 still do not presuppose equal decisions, and producer coverage stays an independent obligation (CV-B).
  - 01.6 (D:507-516): C2-35, verbatim.
  - 03.1 (D:818-859): C2-51, verbatim.
  - 04.2 (D:972-988, 1004-1008): C2-62. R3-10 and R3-11 insert the roster-evidence step; ACK and ABANDON stay exclusive, ABANDON still cannot reach WORKER_OWNED (line 988 and INV-C2 unchanged).
  - 04.6 (D:1061-1067): C2-68, verbatim.
  - 06.1 (D:1348-1363): C2-92, verbatim. V-D.4 extends the comparison, and every option, A included, stays unselected.
  - 07.2 and 07.3 (D:384-398, 1453-1462): C2-S2 and C2-101.
  - 07.4 (D:1447-1455, 1494): C2-101 and C2-104.
  - 07.5 (D:405, 1450, 1464-1468): C2-S2 (CD-8) and C2-101. v2 §10.3's collector rule, that the collector uses the first capture, is restated in V-G.3 (a).
  - 08.7 (D:1143-1151): C2-71, verbatim.
  - 09.4 (D:1274-1285): C2-84. R3-15 replaces line 1285 with the domain-preserving path and keeps every listed case.
  - 11.2 (D:1836-1849, 1890-1894): C2-151 with R3-7, and V-M for the replaced §15.2 rows.
  - 11.3 (D:1926-1940): C2-16 with R3-8.
  - 11.4 (D:357-363, 1799-1801, 1939-1940): C2-G with R3-1, C2-16, and R-RW-9 (V-K.8: Optional_Marker untouched).
  - 12.3 (D:1562-1568, 1573): V-G.5 keeps every uncertain hold (PR-b, RT-5, RT-13), with no EOF or deadline settlement (C2-64).
  - 12.5 (D:1538-1553, 1574-1575): C2-113, and V-J.6 (no missing state initialized).
- **Draft defects DF-1 … DF-6:** carried by slice C2-A3 with their required fixes. The review's assessments, verbatim:
  - DF-1 VERIFIED_STATIC_RECOMPUTATION;
  - DF-2 VERIFIED_STATIC;
  - DF-3 VERIFIED_STATIC;
  - DF-4 VERIFIED_STATIC;
  - DF-5 VERIFIED_STATIC_ABSENCE_IN_SELECTED_TREES;
  - DF-6 SUPPORTED_STATIC_CONDITIONAL.
- **Observations N-1 … N-10:** carried by slice C2-A3 as assessed, verbatim:
  - N-1 VERIFIED_STATIC;
  - N-2 SUPPORTED_STATIC_TOOL_BEHAVIOR_OPEN;
  - N-3 VERIFIED_STATIC;
  - N-4 VERIFIED_BYTE_DIFF_AND_LAYOUT;
  - N-5 VERIFIED_LEXICAL_SCOPE;
  - N-6 SUPPORTED_STATIC_CONDITIONAL_RECEIVER_RESOLVED;
  - N-7 VERIFIED_STATIC;
  - N-8 VERIFIED_STATIC_ORDER;
  - N-9 VERIFIED_TEXT_SCOPE_RESOLUTION_OPEN;
  - N-10 VERIFIED_STATIC_PAIR_FILLING.

  The review's erratum (checkpoint-6, `D2R/REVIEW.md:295`) is carried: N-3's protected canonical Off aspect is at `R/core/worldline-canonical_operation_c_api.adb:3`.
- **Operator items OP-1 … OP-9:** all WITHIN_RESERVED_SCOPE, carried by slice C2-16. R3-8 only extends OP-7's measurement range. No item is added, lowered or widened.

### A.6 The review's other findings and decisions

| Finding (review) | v3 answer | Where |
|---|---|---|
| TOTAL-EMBEDDING: "G3 and the unspecified multi-frame variant leave the declared total embedding incomplete. Raw-domain-only exclusions cannot narrow the original quantified domain." | Totality withdrawn; the constructions; residuals decided by the unchanged original unit. | V-B |
| SCOPED-CONTROLS: "The multi-frame/multi-bucket refusal vectors do not specify an invalid predicate. Qualify the exact violated condition and include genuinely valid multi-frame/multi-bucket positives; neither shape alone is a new refusal." | Qualified fixtures and positives. | V-B.9 |
| REQUESTER-PROVIDER: "Mandatory FRESH socket cookies and namespace records can add a provider restriction. Explicit non-ready status does not preserve an originally accepted case; establish profile coverage or an authentic domain-preserving design. No new live-client/pidfd requirement is introduced." | Optional cookies and namespace records; queued fallback onto the original gate. | V-I.3, V-I.6 |
| REQUESTER-MODES: "Unconditional J1/J3/J4 are inconsistent with J8's socket-free retained/historical modes. Mode-specific presence and request/operation/transaction joins must be explicit." | Mode predicates with typed presence; joins. | V-I.3, V-I.4 |
| RECOVERY-DOMAIN: "PREPARED-no-HELD release must exclude any dispatched/possibly-launched case; retained RESULT_CAPTURE recovery must not acquire an extra HANDLER_TERMINAL prerequisite." | Rows PR-a and PR-b; RT-7′. | V-G.4, V-G.5 |
| RQ-2 OPEN (G3 construction) | Saturated-arena construction; residual R3. | V-B.6 |
| RQ-3 OPEN (Current_Facts) | PD-1 derives it from the producer's single current observation. | V-B.8 |
| RQ-4 not endorsed | Withdrawn. | V-D.1 |
| RQ-5 (P3 undefined) | Defined. | V-C.7 |
| §6: E3 future capacity | Withdrawn; correspondence table. | V-D |
| §6: Source_Record `Container_Bound` must join the authenticated roster; distinct tags do not prove authentic independent producers | `Roster_Join`; producer non-claim kept. | V-C.3, V-C.5 |
| §6: euid-0 coordinator reachability, custody substate/DDL, drain durability barriers | V-E.3, V-F, V-H. | |
| C-API ordering (SOUND_CONDITIONAL_INCOMPLETE) | Explicit gate edges; every stage binds its tables. | V-K, V-M |
| C-API rules (REQUIRED_REPAIR) | V4-RC4-GATE/ALIAS carried OPEN; repaired rules adopted only as labelled CAPI5 dependencies. | V-K.1, V-K.4, V-K.5 |
| C-API checks (PARTIALLY_COMPLETE) | IC-1 now requires the complete floor; IC-11 and IC-12 added. | V-K.9 |
| CAPI-SCOPE-CONTRADICTION (REQUIRED_REPAIR) | R-RW-2 and IC-3 scoped to new root-worker additions; the S5 residual and per-scope clauses preserved. | V-K.7 |
| R-2's "unreviewed" C-API wording is historical (REVIEW.md:34) | Reading rule RR3-5. | §B.4 |

### A.7 New author observations (static; for the reviewer to check; none is review)

| Id | Observation | Evidence | Consequence | Where |
|---|---|---|---|---|
| NF-1 | The transferred host procfs descriptor is a directory fd opened `O_RDONLY` (`rw/root_worker_custody.py:117`). A directory fd's mode does not limit `openat` of its children for writing, so a euid-0 holder can open host procfs files for writing where root DAC permits. **[unverified reasoning, K-18]** | Read | This is a writable view; it is replaced by a read-only procfs view (M-2). | V-E.3 |
| NF-2 | Context rollover (`Advance_Context`) is committed by `reconcile_context` whenever scope, universe head, root head, PRIME, catalogue head or physical head differs from the last frame (`rw/protected_scoped_resource_runtime.py:356-373`). The native `Advance_Valid` accepts a change of any one of them (`core/resource_scoped_run_ledger.ads:334-339`). For Reserve, Record_Launch_Intent and Record_Running, the scoped check refuses `Context_Changed` only when the request's scope differs from `State.Current` by `Same_Context`, which compares the nine `L.Context` fields (`core/resource_run_ledger.ads:110-120`), or when its bound universe head differs from `State.Universe_Head` (`core/resource_scoped_run_ledger.ads:436-438`). So a rollover caused only by a root-head, PRIME, catalogue-head or physical-head change does not by itself block those commands. | Read | Informs the RQ-1 table: rollovers are routine, and most of them do not touch the launch-side conjuncts. | V-B.10 |
| NF-3 | The daemon registers `status` as mutating (`rw/daemon.py:84`), so `status` takes `_mutation_lock` (`rw/daemon.py:350-357`). It then enters `principal.invoke`, which takes `operation_lock` (`rw/protected_operations.py:716-717`). | Read | `status` shares both asyncio locks with every consequential request. | V-L.1 |
| NF-4 | The original startup recovery settles an EFFECT_INTENT row that has a retained RESULT_CAPTURE automatically, with no terminal-frame prerequisite (`rw/protected_operations.py:367-368` → `recover_committed`, `:812-816`). | Read | Grounds RT-7′. | V-G.3 |
| NF-5 | CAPI5 §19 still calls the draft's renamings "body-level" (`CAPI5/DESIGN.md:338`). The sealed v2 review verified that they lie inside `Child_Boundary`'s body (N-5, VERIFIED_LEXICAL_SCOPE). | Read | A wording item for CAPI5's own reviewer. v3 does not edit CAPI5. | V-K.1 |
| NF-6 | The V3 slot calls `systemctl --system show` and `stop` directly (`rw/protected_scoped_supervisor_v3.py:23-36`, `:298-301`). A euid-0 coordinator that can reach systemd's control interface can change any unit's properties, including its own ceilings. **[unverified reasoning, K-17]** | Read | Systemd and D-Bus control must be unreachable from the coordinator; manager operations go through helper commands (M-1, M-4). | V-E.3 |
| NF-7 | When the front is not FRONT_OWNED, the router awaits every collector while holding its asyncio lock (`rw/root_worker_endpoint_router.py:20-25`), so every later request waits for the detached root's complete closure and reconstruction. The front's own `invoke` also refuses unless FRONT_OWNED (`rw/protected_root_worker.py:159`). | Read | The availability gap of seam 4, restated for the V-L model. | V-L |
| NF-8 | Two canonical JSON forms exist. `protected_startup.canonical` emits UTF-8 with `ensure_ascii=False` (`rw/protected_startup.py:35-37`), and `exact_json` enforces it, allowing one trailing LF (`:40-51`). `protected_resource_runtime.canonical` emits ASCII (`rw/protected_resource_runtime.py:20`), and `exact` enforces it with no trailing LF (`:22-23`). The run-scoped config that holds the resource catalogue is read by `exact` (`rw/protected_scoped_resource_service.py:68-74`). | Read | The native recognizer needs a form parameter: UTF-8 for the startup containers, ASCII for the run-scoped config. | V-C.1, V-C.3 |
| NF-9 | `client_peer_relay.receive_request_peer` (`rw/client_peer_relay.py:32-121`) rebuilds a `RequestPeer` in a receiver through the same re-read equality as the original (`:111-112`, with `rw/client_peer.py:116-117`). The file is byte-identical to S5's copy (sha256 `52276d2f7e8f76362e4e97e2dd64ff51f2e5198f57969542bf85e9f50c9ef1f4`, observed). In the lane only `tests/test_client_peer_producer.py` refers to it (observed). | Read | The original transfer pattern is equality of the whole re-read. A receiver in another PID namespace would read a different PID **[unverified reasoning, K-1]**, which is why the worker uses a separate exact type. | V-I.1 |
| NF-10 | The owner plan reaches `serve_root_front` as an argument (`rw/protected_root_endpoint.py:12`, `:28`) and is bound only as source-lease DATA (`rw/protected_root_worker.py:92-97`). The v1 descriptor has no root-worker key (`rw/protected_startup.py:173-176`). The plan's exact keyset already names the custody journal and genesis (`rw/protected_root_worker.py:98-104`). | Read | The v2 descriptor selects the owner plan, and the plan keeps its keyset. | V-J.2 |
| NF-11 | The custody genesis carries no MAC. It is bound as source-lease DATA (`rw/root_worker_journal.py:39-41`) and by exact equalities with the descriptor digest, the owner-plan digest and the issuer-key digest (`:43-53`), and its stored copy must equal it (`:95-97`). Events and the head carry an HMAC-SHA256 under the issuer key (`:25-26`, `:99-113`). | Read | Corrects the genesis-authenticity statement V-C.3 builds on. | V-C.3 |

---

## B. What v3 carries from v2, and how to read it

### B.1 Bound v2 slices

- v2 `SEAM-DESIGN.md` has 2296 lines and ends with a newline (observed). Its whole-file sha256 is `db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5`.
- Each slice's sha256 is that of the UTF-8 bytes of its lines, each line followed by `\n`. A read-only script computed them.
- CARRIED_VERBATIM slices are part of v3 exactly. CARRIED_WITH_LINE_REPLACEMENTS slices are part of v3 with the listed v2 lines replaced by the §B.2 text.

| Slice | v2 lines | sha256 | Disposition | Content |
|---|---|---|---|---|
| C2-A3 | 110-137 | `8dac441d5568bfcef6a6c76374715a07fe27405694cfcd656e92a05a198c6c8e` | CARRIED_VERBATIM | A.3: DF-1 … DF-6 and N-1 … N-10 |
| C2-B | 149-245 | `c67275cf95e85f817827aed32125f8176dfbff82dddad82c299c1765bc8d2ad9` | CARRIED_VERBATIM | §B: what v2 carried from v1 (history) |
| C2-G | 315-366 | `b5e1ebc659b11f56fef5582a7b7d6d2f8c502509eac2a063de4cdfc8224b5b28` | CARRIED_WITH_LINE_REPLACEMENTS (R3-1) | §1 global invariants G-1 … G-13 |
| C2-S2 | 367-426 | `6dcd2745d1553e7df50e36f32fcee59805fb673f3b0f071387e48cdeb4cbadec` | CARRIED_WITH_LINE_REPLACEMENTS (R3-2, R3-3) | §2 state model O/U/C/P and CD-1 … CD-9 |
| C2-31 | 427-506 | `c87034a71bded859d0e99a88a434b8b41859700f016fe87b589f7d69f1d9d6e5` | CARRIED_WITH_LINE_REPLACEMENTS (R3-25 … R3-31) | §3.1–§3.4 the scoped unit, its clauses, their correspondence, and the FRESH, RETAINED and HISTORICAL domains |
| C2-35 | 507-517 | `0cddde6146e7d4dd8afb6c01251906bc0b4ba2117886c28f6492906d4d7ed38f` | CARRIED_VERBATIM | §3.5 exact projection |
| C2-36 | 518-528 | `075fa1f1cabc71e2aa8de92397b9464d2abcd6567e03cb337699f94ea2d7cfe4` | CARRIED_WITH_LINE_REPLACEMENTS (R3-32) | §3.6 arena and span mapping, L-RB-1 … L-RB-3 |
| C2-37 | 529-557 | `54e7ff5925f03274d6307277bf0d053e19da710c8ba0e9b0c23ac2acae3b8484` | CARRIED_WITH_LINE_REPLACEMENTS (R3-33, R3-34) | §3.7 structural embedding, field by field |
| C2-38 | 558-574 | `bef4081b98fafa5007943ba15d886489742f5caea851d3b0bd18b37f6ad1066d` | CARRIED_WITH_LINE_REPLACEMENTS (R3-4) | §3.8 coherent witness W1 … W10 |
| C2-39 | 575-605 | `21226be6818e55837d4adb06c998c75ec745eef118bbf56d19ac9674d35ce33d` | CARRIED_WITH_LINE_REPLACEMENTS (R3-35 … R3-37) | §3.9 obligations L-EQ, L-C2a–f, L-C3, L-CL-1, L-SC-1, L-INV-1, CV-B, CV-C, CV-D; gaps G1 … G6 |
| C2-310 | 606-618 | `5b36da424bb523a9b3c69fdf9772654c7637ab5770de4c099c0974def5e8ee2d` | CARRIED_VERBATIM | §3.10 non-circularity; §3.11 contracts and cost |
| C2-41 | 673-711 | `896299ddfd0f03131a8dae49e1750cb6ca1788392acb813b0c848a3ad61b841a` | CARRIED_WITH_LINE_REPLACEMENTS (R3-38 … R3-40) | §4.1 tagged source-record grammar and `Pair_Valid` |
| C2-42 | 712-742 | `fc91b4f77d8f1834dc1cc7f3201c84860b299cb054f7a3829d0d27ca8f5a3aec` | CARRIED_WITH_LINE_REPLACEMENTS (R3-5, R3-6) | §4.2 per-pair table P1 … P11; §4.3 V2 controller |
| C2-46 | 780-792 | `8e76f0684917bbbaa5f7cd4f09d057fa760c5f8162db4f07a4dd2b84c5d13597` | CARRIED_VERBATIM | §4.6 controls |
| C2-51 | 810-865 | `4f8921ed4b596034925228f695ba43942ecc96f88adedb9fb3322f2a8b516f0c` | CARRIED_VERBATIM | §5.1–§5.2 delegation and classification successor |
| C2-53 | 866-878 | `812b0f969a4d7d83789b8e913cc29ed96018a6cb66743265be10a10db2d9c660` | CARRIED_VERBATIM | §5.3 coordinator enforcement argument P-CE1 … P-CE4 |
| C2-55 | 898-926 | `48d0e0b2dda73fc1166cd476be7228ed467af13dca8ff92aa890d6443094d944` | CARRIED_WITH_LINE_REPLACEMENTS (R3-41, R3-42) | §5.5 dispatcher: interim refusal, TaskIntent, child RESERVE, closure, follow-ups, race |
| C2-56 | 927-944 | `7529db2726968380b627dee2fd78f695a0bffcaad9cc813703b1c8b9db6d7406` | CARRIED_VERBATIM | §5.6 controls |
| C2-62 | 970-1010 | `f3206d63e4f973203d33c9b79c6903fc8f69245d3fed5d333ee386ea319cdd39` | CARRIED_WITH_LINE_REPLACEMENTS (R3-10 … R3-13) | §6.2 root phase graph, exclusive branches, INV-C1 … INV-C5 |
| C2-64 | 1032-1054 | `d20b643a28c3ce661b76d2b9e3ad946f9e114b52edc9a0627b3a13b4c4b97a00` | CARRIED_VERBATIM | §6.4–§6.6 seed, reconstruction, EOF and deadlines |
| C2-68 | 1061-1073 | `ca153ae5d2f5316532fdaa0556897a15d2ab7360f63b611c99070fc3e20cd5f4` | CARRIED_VERBATIM | §6.8–§6.9 retention, lingering units |
| C2-612 | 1102-1114 | `13b4b7d1d1613d5ee532b755713f585dd88ef25cf862b35d99c85adb87f7686a` | CARRIED_VERBATIM | §6.12 controls |
| C2-71 | 1128-1152 | `c4c99830f20477e39c1b1ce669244480784e55bd8dd4237a2125b5e01595297a` | CARRIED_VERBATIM | §7.1–§7.2 scope, producer retention |
| C2-74 | 1178-1203 | `cfd9689a5c70f04acf4c0393a5ee50cada435752b990af6480968fbb37a9903a` | CARRIED_WITH_LINE_REPLACEMENTS (R3-14) | §7.4–§7.6 TransferredSlot, return, controls |
| C2-84 | 1274-1312 | `ed4b145a8eab266619fd01b252c5e269f3bb9fb895e8b206954b609e4fb67ae2` | CARRIED_WITH_LINE_REPLACEMENTS (R3-15 … R3-17) | §8.4–§8.7 domains D8-1 … D8-6, K items, actor isolation, controls |
| C2-91 | 1325-1347 | `5a62982b2b8a56fea60ebf833766fed64bad3443a84db78ff5f6d347cbe8c678` | CARRIED_VERBATIM | §9.1 AM-1 … AM-9 |
| C2-92 | 1348-1364 | `24559c4678b960b688d45bfc824b8af576718292d03743a643b8142a4abff957` | CARRIED_VERBATIM | §9.2 options A, B, C and E with their known gaps (none selected) |
| C2-93 | 1365-1395 | `11c31e0731c39d44cc9d1f49993c554ae215cef37ab05ee65c3381bd4e3b8f8b` | CARRIED_WITH_LINE_REPLACEMENTS (R3-18, R3-19) | §9.3 phase routing; §9.4 request transfer |
| C2-96 | 1410-1434 | `fe1aa2509829dfae86875d0bbf833589b0a35362751671d45a848d2756b4652a` | CARRIED_VERBATIM | §9.6–§9.8 |
| C2-101 | 1447-1463 | `97d4336ec60f9f5d7f57b6325542125755a16183ad226af2e04da9f92dce5e35` | CARRIED_VERBATIM | §10.1–§10.2 finish split, root route while LIVE |
| C2-104 | 1470-1496 | `78063127ff72fed2cf97e4ccdd8125a12716aaa5194a26b4a59bef72f3e1642a` | CARRIED_VERBATIM | §10.4–§10.6 adapters, ordering, controls |
| C2-111 | 1509-1527 | `939f5ffea62a01b55833b59d960eb42ec21c75a7da44b27ee13b4f820a3d1401` | CARRIED_WITH_LINE_REPLACEMENTS (R3-43) | §11.1 version, loader, schema and creation-slot union U-1 … U-12 |
| C2-113 | 1538-1554 | `096a1f9cebf774dc6e0f2b46931cbfc6d424c7d77b808da0fd89d4d483473ddc` | CARRIED_VERBATIM | §11.3–§11.4 one-shot provisioning, diagnostic startup |
| C2-116 | 1580-1616 | `b3e66978fdb903fd63f0d3e4cf206984093bf3fff5aa4ddc7594110dd761d222` | CARRIED_VERBATIM | §11.6–§11.8 frontier control, attach, controls |
| C2-12 | 1625-1698 | `1270f8b508dea88d6e83f20b7c56b6845252e8ef1fa9bf8000f07398d4c5d967` | CARRIED_VERBATIM | §12 pins, freeze, enrollment, roster order, C helper, seal controls |
| C2-132 | 1724-1749 | `aece2edd58c21f8040a88fbc84ce9625e0d0d76f5a3631a22264c1cbc2a11822` | CARRIED_VERBATIM | §13.2–§13.4 attach, guard order, rest of SL-0 |
| C2-141 | 1754-1783 | `068c98ed137fb8f03551e40d4c18beaf1ac2ad1a74f1456d786c4a758830e097` | CARRIED_VERBATIM | §14.1–§14.2 observed facts and hazards H1 … H8 |
| C2-151 | 1836-1850 | `47c205aa2729d14e3013c875c4fed99d07c31dab03f45d1a988bddc0e3245741` | CARRIED_WITH_LINE_REPLACEMENTS (R3-7) | §15.1 lineage nodes |
| C2-153 | 1903-1915 | `4345ba3cb8acc7aef1c691de65a4985065d6c6bf1e2bc65b4575875cf8510f4e` | CARRIED_VERBATIM | §15.3 corrections to v1's plan |
| C2-16 | 1922-1962 | `cc000abe9c5f8be6e6b1d38cdc84985e9374b2e94b52767e6032b1aaa95b704e` | CARRIED_WITH_LINE_REPLACEMENTS (R3-8) | §16 operator items OP-1 … OP-9, K-1 … K-14 |
| C2-17 | 1963-1991 | `da7d4b09f0286d4e53fc5029d489c1fc5a44c8462726bfa299f64570a75ad27c` | CARRIED_WITH_LINE_REPLACEMENTS (R3-9) | §17 controls |
| C2-18 | 1992-2053 | `30a010d01ceec959afbad58e1a744c405aa9fa21a89cf7b4b17979c160f8d368` | CARRIED_WITH_LINE_REPLACEMENTS (R3-20 … R3-24) | §18 everything that remains OPEN (v2's list, which the review keeps open; V-P adds v3's items) |
| C2-APC | 2221-2287 | `92d6c824fe889f692157a260213635d1ddca56bd9f7266ee38e0c19720cc147c` | CARRIED_VERBATIM | v2 Appendix C: the v1 slice bindings and R-1 … R-4 (transitive) |

### B.2 Line replacements

Each replacement quotes the exact v2 line, then gives the v3 text.

**R3-1 replaces v2 line 362 (in C2-G).**
```text
v2:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace and socket semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14, §16).
v3:
- **G-12. Unmeasured semantics.** Kernel, systemd, cgroup, namespace, socket and interpreter semantics are unmeasured. Each design element that depends on them names its measurement item (K-1 … K-14 in §16, K-15 … K-19 in v3 V-O) or its installed-runtime check (RC-1 … RC-4 in v3 V-O).
```

**R3-2 replaces v2 line 380 (in C2-S2).**
```text
v2:
The exact mapping from O's values to the broker's and transaction store's record states is a deliverable of spec slice S6 (OPEN). O is recorded once per exchange-bearing operation. Operations without an exchange keep `NO_EXCHANGE`, and their effect is tracked in U.
v3:
The exact mapping from O's values to the broker's record states is v3 V-F.2. O is recorded once per exchange-bearing operation. Operations without an exchange keep `NO_EXCHANGE`, and their effect is tracked in U.
```

**R3-3 replaces v2 line 408 (in C2-S2).**
```text
v2:
### 2.3 Illustrative combinations (DESIGN; the full legal-product table is an S6 deliverable)
v3:
### 2.3 Illustrative combinations (DESIGN; the legal product relation and its complete O×U table are v3 V-F.3)
```

**R3-4 replaces v2 line 572 (in C2-38).**
```text
v2:
- **W9.** `WD` is disjoint from every rebased original span. `Rebase` satisfies L-RB-1 … L-RB-3.
v3:
- **W9.** Every witness field has one of the three forms of v3 V-B.3: a present zero-length span, an alias of an original span, or fresh bytes placed outside every rebased original span. `Rebase` satisfies L-RB-1 … L-RB-4 (v3 V-B.6).
```

**R3-5 replaces v2 line 720 (in C2-42).**
```text
v2:
| P3 | source_lease ↔ process `P_source_lease` (`.ads:59`) | Host-side capture of the worker through host procfs and the worker pidfd: interpreter executable digest and mapped executables (`rw/root_worker_process_capture.py`) | The P2 loader record, a distinct producer | The intersection both can observe (interpreter and extension digests). Exact definition OPEN for spec slice S2 (RQ-5). Today's caller-provided value (`rw/protected_root_observation.py:74-76`, `:121`) is withdrawn. |
v3:
| P3 | source_lease ↔ process `P_source_lease` (`.ads:59`) | Host-side capture of the worker's executable images (exe plus every file-backed executable mapping, each with dev, ino and sha256) through a read-only host procfs view and the worker pidfd | The P2 loader lease record, a distinct producer | Native subset relation `Process_Images_Covered`, defined in v3 V-C.7 with its non-claims. Today's caller-provided value (`rw/protected_root_observation.py:74-76`, `:121`) is withdrawn. |
```

**R3-6 replaces v2 line 738 (in C2-42).**
```text
v2:
- **`Controller_Valid_V2`.** Every non-pair conjunct of `Controller_Valid` (`.ads:48-52`), reproduced literally, plus `Pair_Valid` for P1–P7. The original `Controller_Valid` is unchanged and keeps deciding V1 inputs.
v3:
- **`Controller_Valid_V2`.** Every non-pair conjunct of `Controller_Valid` (`.ads:48-52`), reproduced literally, plus `Pair_Valid` for P1, P2 and P4–P7, plus `Process_Images_Covered` for P3 (v3 V-C.7), plus `Roster_Join` for every expected anchor (v3 V-C.3). The original `Controller_Valid` is unchanged and keeps deciding V1 inputs.
```

**R3-7 replaces v2 line 1844 (in C2-151).**
```text
v2:
| **L-CAPI** | The C-API consolidation successor | CAPI4 is DRAFT_FOR_GPT61_REVIEW. Its source packets PK-0 … PK-S are unwritten. The v3 review is sealed. |
v3:
| **L-CAPI** | The C-API consolidation successor | The sealed actual gpt-6.1-sol review of CAPI4 is ENDORSED_WITH_REQUIRED_CHANGES, with V4-RC4-GATE and V4-RC4-ALIAS OPEN. CAPI5 answers both and is UNREVIEWED. Source packets PK-0 … PK-S are unwritten. |
```

**R3-8 replaces v2 line 1932 (in C2-16).**
```text
v2:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 in an authorized lab | §3–§9 runtime evidence |
v3:
| OP-7 | **D-8b.** Kernel measurements K-1 … K-14 (§16) and K-15 … K-19 (v3 V-O) in an authorized lab | §3–§9 and v3 V-B … V-I runtime evidence |
```

**R3-9 replaces v2 line 1980 (in C2-17).**
```text
v2:
- It enumerates every control of §3.14, §4.6, §5.6, §6.12, §7.6, §8.7, §9.8, §10.6, §11.8, §12.6 and §14.5. Each entry gives:
v3:
- It enumerates every control of §4.6, §5.6, §6.12, §7.6, §8.7, §9.8, §10.6, §11.8 and §12.6 (carried) and of v3 V-B.9 and V-N (which replace v2 §3.14 and §14.5). Each entry gives:
```

**R3-10 replaces v2 line 985 (in C2-62) with two rows.** The handoff gains the roster-evidence step of V-H.4.
```text
v2:
| TRANSFER_SENT | CUSTODY_ACK | **Worker** | Intake native redecision `ROOT_READY_CONJUNCTION`. Seed equals current under the transferred OFDs. CAS on g. |
v3:
| TRANSFER_SENT | ROSTER_EVIDENCE | Front | `kcmp (KCMP_FILE)` and lock-held evidence for every transferred lock descriptor, recorded while the front still holds its copies (v3 V-H.4) |
| ROSTER_EVIDENCE | CUSTODY_ACK | **Worker** | Intake native redecision `ROOT_READY_CONJUNCTION`. Seed equals current under the transferred OFDs. The roster evidence matches the worker's report of its received descriptors. CAS on g. |
```

**R3-11 replaces v2 line 986 (in C2-62).**
```text
v2:
| TRANSFER_SENT | ABANDON | **Front** or Reconciler | CAS on g. No `CUSTODY_ACK(g)` committed. |
v3:
| TRANSFER_SENT, ROSTER_EVIDENCE | ABANDON | **Front** or Reconciler | CAS on g. No `CUSTODY_ACK(g)` committed. |
```

**R3-12 replaces v2 line 992 (in C2-62).**
```text
v2:
| WORKER_OWNED | DRAIN_FREEZE(d) → DRAIN_INTAKE(d) / DRAIN_ABANDON(d) | Front, then Worker / Front | §7.3 protocol, exclusive CAS on d |
v3:
| WORKER_OWNED | DRAIN_STOP_INTENT(d) → DRAIN_FREEZE(d) → DRAIN_OFD_EVIDENCE(d) → DRAIN_INTAKE(d) / DRAIN_ABANDON(d) → DRAIN_RELEASED(d) | Front, then Worker / Front | v3 V-H protocol, exclusive CAS on d and its sub-generation |
```

**R3-13 replaces v2 line 998 (in C2-62).** This removes the handler-terminal prerequisite that RECOVERY-DOMAIN rejects.
```text
v2:
| PHYSICAL_SETTLED | HISTORICAL_SETTLEMENT | Collector | Use settled natively (`SETTLE_USE`) if a terminal and retained result exist. Otherwise native `QUARANTINE_USE` (CD-2). Both are legal. |
v3:
| PHYSICAL_SETTLED | HISTORICAL_SETTLEMENT | Collector | Use settled natively through the original `recover_committed` → `finish` path when exactly one retained first `RESULT_CAPTURE` exists (v3 V-G.3 (a)); no handler terminal is required. Otherwise native `QUARANTINE_USE` (CD-2). Both are legal. |
```

**R3-14 replaces v2 line 1188 (in C2-74).**
```text
v2:
- Slot custody returns to the reconstructed front through the `ClosedFrontEscrow` roster by the same T1–T5 protocol (§6.5).
v3:
- Slot custody returns to the reconstructed front through the `ClosedFrontEscrow` roster by the same H0–H6 protocol (v3 V-H; §6.5).
```

**R3-15 replaces v2 line 1285 (in C2-84).** REQUESTER-PROVIDER: an explicit non-ready status is replaced by the domain-preserving path.
```text
v2:
Where correspondence cannot be established, the result is an explicit named status, and the obligation stays OPEN. Examples: no socket cookie on the lab kernel, or unreadable namespace identities. Nothing is substituted: no sender PID label, no synthesized `SO_PEERCRED` bytes, and no `fstat` equality as custody.
v3:
Where the worker cannot establish correspondence for a transferred request, it declines intake (`REQUEST_ABANDON(r)`). The request stays queued and is served by the front under the original `RequestPeer` gate (v3 V-I.6). It is never refused for that reason. An absent socket cookie or an unreadable namespace identity never blocks (v3 V-I.3). Nothing is substituted: no sender PID label, no synthesized `SO_PEERCRED` bytes, and no `fstat` equality as custody.
```

**R3-16 replaces v2 line 1304 (in C2-84).**
```text
v2:
- Socket identity mismatch, or cookie mismatch, is refused.
v3:
- Socket identity mismatch, or a cookie mismatch when both cookies are present, makes the worker decline intake. The front then serves the request under the original gate (v3 V-I.6), and the original checks decide it.
```

**R3-17 replaces v2 line 1305 (in C2-84).**
```text
v2:
- A different user namespace is refused.
v3:
- A worker in a different user namespace declines intake. The front serves the request under the original gate (v3 V-I.6).
```

**R3-18 replaces v2 line 1389 (in C2-93).**
```text
v2:
1. The front appends `REQUEST_TRANSFER_INTENT(r)`. The record holds the full raw request line, the original host observation, the socket identity and cookie, and the namespace identities.
v3:
1. The front appends `REQUEST_TRANSFER_INTENT(r)`. The record holds the full raw request line, the original host observation, the front's own re-read at transfer (JF) and the socket identity. When available, it also holds the socket cookie and the namespace identities, as optional corroboration (v3 V-I.3).
```

**R3-19 replaces v2 line 1391 (in C2-93).**
```text
v2:
3. The worker computes the native `Join` (§8.1) and CASes `REQUEST_INTAKE(r)`, which is exclusive with `REQUEST_ABANDON(r)`. Then it acknowledges.
v3:
3. The worker receives everything first, validates it, computes the native `Join` in FRESH mode (v3 V-I.3, V-I.7) and CASes `REQUEST_INTAKE(r)`, which is exclusive with `REQUEST_ABANDON(r)`. Then it acknowledges. If `Join` is not Ready, it declines and the front CASes `REQUEST_ABANDON(r)`. The request stays queued, and the front serves it under the original gate once custody returns (v3 V-I.6).
```

**R3-20 replaces v2 line 2002 (in C2-18).**
```text
v2:
  - The exact definition of P3 (RQ-5). The mapping of "minimum/low" (RQ-4).
v3:
  - The P3 relation of v3 V-C.7 and its proof (RQ-5). RQ-4 is withdrawn (v3 V-D.1). The per-class capacity correspondence of v3 V-D.2 stays OPEN.
```

**R3-21 replaces v2 line 2018 (in C2-18).**
```text
v2:
  - The T1–T5 protocol bodies.
v3:
  - The H0–H6 protocol bodies (v3 V-H).
```

**R3-22 replaces v2 line 2043 (in C2-18).**
```text
v2:
  - R-RW-1 … R-RW-10 and IC-1 … IC-10; IC-10 needs the admitted frame.
v3:
  - R-RW-1 … R-RW-10 and IC-1 … IC-12 (v3 V-K.8, V-K.9); IC-10 needs the admitted frame.
```

**R3-23 replaces v2 line 2045 (in C2-18).**
```text
v2:
  - CAPI4 is itself unreviewed.
v3:
  - The sealed CAPI4 review leaves V4-RC4-GATE and V4-RC4-ALIAS OPEN. CAPI5 is unreviewed (v3 V-K.1).
```

**R3-24 replaces v2 line 2053 (in C2-18).**
```text
v2:
- **Process.** The independent actual gpt-6.1-sol review of this v2, of every slice and of the full lane.
v3:
- **Process.** The independent actual gpt-6.1-sol review of v3, of every slice and of the full lane. The sealed review of v2 is its predecessor.
```

**R3-25 replaces v2 line 467 (in C2-31).** RQ-1: the FRESH conjunct leaves the scoped C2.
```text
v2:
| C2 resource (lifted) | `not L.Conserved (Data,State,Rows) or else not L.Contained (Data,Rows) or else not L.Native_Valid (Data,State,Rows,Observed) or else not (for some I => L.Same_Binding (Rows(I).Bound,Bound) and then Rows(I).State in Reserved\|Launch_Intent\|Running)` → `Resource_Refused` | `not S.Valid (Data,State,Frames,Rows,Projection,Buckets,Current) or else not S.Native_Valid (Data,State,Frames,Rows,Observed,Facts) or else not S.Current_Facts (Data,Current,Facts) or else not (for some I => S.Retained_Origin (Data,State,Frames,Rows(I)) and then L.Same_Binding (Data,Rows(I).Bound,Bound) and then Rows(I).State in L.Reserved\|L.Launch_Intent\|L.Running and then L.Same_Context (Data,Rows(I).Scope,State.Current))` → `Resource_Refused` |
v3:
| C2 resource (lifted) | `not L.Conserved (Data,State,Rows) or else not L.Contained (Data,Rows) or else not L.Native_Valid (Data,State,Rows,Observed) or else not (for some I => L.Same_Binding (Rows(I).Bound,Bound) and then Rows(I).State in Reserved\|Launch_Intent\|Running)` → `Resource_Refused` | `not S.Valid (Data,State,Frames,Rows,Projection,Buckets,Current) or else not S.Native_Valid (Data,State,Frames,Rows,Observed,Facts) or else not S.Current_Facts (Data,Current,Facts) or else not (for some I => S.Retained_Origin (Data,State,Frames,Rows(I)) and then L.Same_Binding (Data,Rows(I).Bound,Bound) and then Rows(I).State in L.Reserved\|L.Launch_Intent\|L.Running)` → `Resource_Refused`. There is no current-context conjunct: the bound row is joined through `Retained_Origin` (RETAINED, v3 V-B.10). |
```

**R3-26 replaces v2 line 468 (in C2-31).**
```text
v2:
| C3 binding (literal, scope re-read) | Equalities of peer, owner and the seven bound digests; `State.Scope.Instance`, `.Policy`, `.Policy_Epoch` against `B`; `Bound.Resource_Epoch` against `B.Resource_Epoch` → `Binding_Mismatch` | Identical, with `State.Scope` replaced by `State.Current` (the scoped ledger's current context) and `O.Digest_Matches` reused. |
v3:
| C3 binding (literal, scope re-read) | Equalities of peer, owner and the seven bound digests; `State.Scope.Instance`, `.Policy`, `.Policy_Epoch` against `B`; `Bound.Resource_Epoch` against `B.Resource_Epoch` → `Binding_Mismatch` | Identical, with `State.Scope` replaced by the bound row's own scope `Rows (I).Scope`, for the unique I that C2 joins (rows have distinct reservations). `Retained_Origin` makes that scope `Same_Context` with its origin frame's scope, the context in which the use was reserved (v3 V-B.10). `O.Digest_Matches` is reused. |
```

**R3-27 replaces v2 line 482 (in C2-31).**
```text
v2:
| bound row ∈ {Reserved, Launch_Intent, Running} | the same, plus `Retained_Origin` and FRESH `Same_Context` | L-C2e |
v3:
| bound row ∈ {Reserved, Launch_Intent, Running} | the same, plus `Retained_Origin` (no current-context conjunct, v3 V-B.10) | L-C2e |
```

**R3-28 replaces v2 line 484 (in C2-31).**
```text
v2:
| C3 with `State.Scope` | C3 with `State.Current` | L-C3: `State.Current = State.Scope` under `Emb` |
v3:
| C3 with `State.Scope` | C3 with the bound row's own scope | L-C3: under `Emb`, every row's scope is `Same_Context` with `State.Scope` (`L.Shape`, `core/resource_run_ledger.ads:229-232`), and `State.Current = State.Scope` |
```

**R3-29 replaces v2 lines 489-493 (in C2-31).** RQ-1 and the D-1b remaining gap.
```text
v2:
**FRESH.** This covers the pre-effect conjunction of this unit and an in-request scoped exchange input (B2b). B2b and B2c are the body nodes of the scoped exchange and K4 successors in §15.2.
- The bound row's origin context must be `L.Same_Context` with `State.Current`. That is a semantic comparison, never record equality.
- Static consistency argument (STATIC_REASONING): a fresh reservation natively requires `Same_Context (Before.Current, R.New_Row.Scope)` (`resource_scoped_run_ledger.ads:359`). `Record_Launch_Intent` and `Record_Running` natively refuse `Context_Changed` when `Before.Current` differs from the request scope (`:436-438`), and a non-Reserve request scope must equal the row's origin scope (`:373-375`). So a rollover between reserve and launch already blocks the launch in the original scoped kernel. The FRESH clause asks the same of the pre-effect.
- A rollover between reserve and pre-effect therefore gives `Resource_Refused`, with holds retained and the native release still available (CD-5).
- This case has **no counterpart** in the original flat domain, because the single-frame embedding admits no rollover. Review question RQ-1 asks whether the reviewer treats it as an accepted case. If so, the pre-effect needs the RETAINED join below rather than refusal, and that join's obligations apply.
v3:
**FRESH.** The current request with its current authority use: C1 is unchanged. No scoped canonical caller carries a current-context conjunct. The pre-effect conjunction of this unit and the in-request scoped exchange (B2b) use the RETAINED join below. B2b and B2c are the body nodes of the scoped exchange and K4 successors (v3 V-M).
- Current context is checked only where an original native command checks it: Reserve (`resource_scoped_run_ledger.ads:359`, `:436-438`), and Record_Launch_Intent and Record_Running (`:436-438`). A scope or universe rollover between reserve and launch is therefore refused by the launch itself, as the original scoped kernel already does. A rollover of the root head, PRIME, catalogue head or physical head alone is not refused there (v3 NF-2).
- The command, caller and time mapping, with its positive rollover controls, is v3 V-B.10. It answers RQ-1 at design level, and RQ-1 stays OPEN.
```

**R3-30 replaces v2 line 495 (in C2-31).**
```text
v2:
**RETAINED.** This covers the scoped successors that decide after a possible rollover: K4 owner completion (`rw/protected_operations.py:605-622`, B2c), and exchange recovery after restart (B2b). Each needs a `Retained_Join` obligation, as a native relation proved with its caller:
v3:
**RETAINED.** This covers every scoped canonical caller (v3 V-B.10): the pre-effect conjunction, the in-request scoped exchange and exchange recovery after restart (B2b), and K4 owner completion (`rw/protected_operations.py:605-622`, B2c). Each needs a `Retained_Join` obligation, as a native relation proved with its caller:
```

**R3-31 replaces v2 line 498 (in C2-31).**
```text
v2:
3. The original native use replays to `Reserved_New` on its retained snapshot (`_original_native_use`, `rw/protected_operations.py:430-438`). No fresh `Reserve_Use` is decided.
v3:
3. For exchange recovery and K4 completion, the original native use replays to `Reserved_New` on its retained snapshot (`_original_native_use`, `rw/protected_operations.py:430-438`), and no fresh `Reserve_Use` is decided. For the pre-effect conjunction and the in-request exchange, C1 is unchanged: `Reserve_Use` on the current snapshot must give `Reserved_Replay` (`core/worldline-canonical_operation.adb:10`).
```

**R3-32 replaces v2 line 527 (in C2-36).**
```text
v2:
- **Gap G3.** An arena with fewer free `Byte_Index` positions than `|WD|` on both sides has no room for `WD`. Example: `Data'First = 1` and `Data'Last` near `Byte_Count'Last` (`resource_quantities.ads:7-8`). Such arenas are not covered by this construction. This gap is a coverage gap of the lemma, not a runtime refusal. It stays OPEN until another construction covers it (RQ-2).
v3:
- **Gap G3.** An arena with fewer free `Byte_Index` positions than `|WD|` on both sides has no room for `WD`. Example: `Data'First = 1` and `Data'Last` near `Byte_Count'Last` (`resource_quantities.ads:7-8`). v3 V-B.6 covers such arenas: forms (a) and (b) need no `WD` (case S-a), and compaction covers case S-b. Residual R3 stays OPEN (RQ-2). No gap is a runtime refusal.
```

**R3-33 replaces v2 line 529 (in C2-37).** TOTAL-EMBEDDING.
```text
v2:
### 3.7 Structural embedding `Emb (Orig, W)` (total, Ghost)
v3:
### 3.7 Structural embedding `Emb (Orig, W)` (Ghost; defined on D_emb only, not total: v3 V-B.2)
```

**R3-34 replaces v2 line 556 (in C2-37).**
```text
v2:
A **multi-frame variant** with more than one frame and a valid `Prior_Frame` chain is defined in the same way for gap G1. Its coverage is claimed only where L-INV-1 does not already apply.
v3:
The **multi-frame variant** is v3 V-B.5, and the saturated-arena construction is v3 V-B.6. Coverage is exactly D_emb (v3 V-B.2). The residuals R1, R2 and R3 are decided by the unchanged original unit.
```

**R3-35 replaces v2 line 592 (in C2-39).**
```text
v2:
- **CV-B (producer coverage).** For every original input that satisfies L-INV-1 and whose `Observed` was produced by `K.Classify` over facts `F_i` (W6, W7), a coherent witness exists. The proof is constructive: `Fct (i) := F_i`, and the frame, key, factor and amount fields are fresh bytes in `WD`.
v3:
- **CV-B (producer coverage).** For every original input that satisfies L-INV-1 and whose `Observed` was produced by `K.Classify` over facts `F_i` (W6, W7), a coherent witness exists. The proof is constructive: `Fct (i) := F_i`, and every frame, key, factor and amount field takes one of the three forms of v3 V-B.3, as v3 V-B.4 assigns them.
```

**R3-36 replaces v2 line 593 (in C2-39).** Raw-domain-only exclusion withdrawn.
```text
v2:
- **CV-C (fixture coverage).** Every original native fixture vector that exercises `Worldline.Canonical_Operation`, accepted or refusal, is either embedded with a coherent witness and shown to give the same decision, or is listed as raw-domain-only. In every case the original unit and its fixture remain unchanged and keep running.
v3:
- **CV-C (fixture coverage).** Every original native fixture vector that exercises `Worldline.Canonical_Operation`, accepted or refusal, is either embedded with a coherent witness and shown to give the same decision, or is identified as residual R1, R2 or R3 (v3 V-B.2), whose correspondence obligation stays OPEN. In every case the original unit and its fixture remain unchanged and keep running and deciding.
```

**R3-37 replaces v2 lines 599-604 (in C2-39).**
```text
v2:
| G1 | Original raw inputs whose rows carry a universe head different from the state's. `L.Shape` accepts them; scoped `Origin` refuses under one frame. | L-INV-1 covers reachable states. Raw-only inputs need the multi-frame variant or are raw-domain-only (CV-C). |
| G2 | `Observed` labels not produced by `K.Classify`, so W6 fails. `L.Native_Valid` does not re-check liveness, while scoped `Native_Valid` does (`:256-257`). | Raw-domain-only for fixtures. The scoped model refuses copied liveness labels by design (G-8). |
| G3 | Arenas with no room for `WD` (§3.6). | Another embedding construction (RQ-2). |
| G4 | The added `S.Current_Facts` conjunct. | Covered by W5 for coherent witnesses. RQ-3 asks the reviewer to confirm the choice. |
| G5 | The `Same_Context` algebra. | L-SC-1 must be proved from the existing definitions. |
| G6 | Live rows without effect (`Launch_Intent` rows classified Live). The original does not constrain observed unit fields for such rows. | W7, the producer rule. Raw-domain-only otherwise. |
v3:
| G1 | Original raw inputs whose rows carry a universe head different from the state's. `L.Shape` accepts them; scoped `Origin` refuses under one frame. | L-INV-1 covers reachable states. The multi-frame construction (v3 V-B.5) covers the rest except residual R1. |
| G2 | `Observed` labels not produced by `K.Classify`, so W6 fails. `L.Native_Valid` does not re-check liveness, while scoped `Native_Valid` does (`:256-257`). | Residual R2 (v3 V-B.7), decided by the unchanged original unit. The scoped model refuses copied liveness labels by design (G-8). |
| G3 | Arenas with no room for `WD` (§3.6). | v3 V-B.6, except residual R3 (RQ-2). |
| G4 | The added `S.Current_Facts` conjunct. | PD-1 (v3 V-B.8) from the producer's single current observation, and W5 for coherent witnesses (RQ-3). |
| G5 | The `Same_Context` algebra. | L-SC-1 must be proved from the existing definitions. |
| G6 | Live rows without effect (`Launch_Intent` rows classified Live). The original does not constrain observed unit fields for such rows. | W7, the producer rule. Otherwise residual R2 (v3 V-B.7). |
```

**R3-38 replaces v2 line 688 (in C2-41).**
```text
v2:
   Raw, Payload, Container, Anchor : L.Identity;   -- spans in the shared arena
v3:
   Raw, Payload, Container, Anchor : L.Identity;   -- spans in the shared arena
   Path : L.Identity;    -- expected side: the encoded JSON path into Container (v3 V-C.1); empty on the observed side
   Kind : Anchor_Kind;   -- expected side: the roster kind of Anchor (v3 V-C.3)
   Form : Json_Form;     -- expected side: UTF8 or ASCII, chosen by Kind (v3 V-C.1)
```

**R3-39 replaces v2 line 693 (in C2-41).** 02.1: the expected side is not framed.
```text
v2:
- **`Payload_Extracted (Data, R)`** is a native per-domain extraction relation: the payload is the canonical comparable encoding (CCE) derived from `Raw` by that domain's grammar. Raw records use a fixed producer framing, `WL-SRC-V1`: magic, domain, field, side, value length, value, evidence length, evidence. Extraction is a total native parse of that framing plus the per-domain rule in §4.2.
v3:
- **`Payload_Extracted (Data, R)`** is a native per-domain extraction relation: the payload is the canonical comparable encoding (CCE) derived from `Raw` by that domain's grammar. Producer records use a fixed producer framing, `WL-SRC-V1`: magic, domain, field, side, value length, value, evidence length, evidence. They are every observed-side record and the expected-side records of producer domains (`Loader_Exec_Record` for P3, `Scoped_Running_Commit`, `Helper_Held_Frame`, `Dispatch_Ticket`). Extraction is a total native parse of that framing plus the per-domain rule in §4.2. Expected-side records of container domains are not framed: `Raw` is the value at `Path` inside the unchanged container, and its CCE is `Extract` (v3 V-C.1).
```

**R3-40 replaces v2 lines 694-696 (in C2-41).** 02.2: the anchor joins the authenticated roster.
```text
v2:
- **`Container_Bound (Data, R)`** holds for expected-side domains whose container is owner-provisioned DATA (descriptor, owner plan, crosswalk, startup genesis):
  - `Anchor` equals the SHA-256 of `Container`, computed natively with the proved `Attest.SHA256` units already in the core;
  - `Raw` is a sub-span of `Container`.
v3:
- **`Container_Bound (Data, R)`** holds for expected-side domains whose container is owner-provisioned DATA (descriptor, owner plan, crosswalk, startup genesis, run-scoped config):
  - `Anchor` equals the SHA-256 of `Container`, computed natively with the proved `Attest.SHA256` units already in the core;
  - `Canonical_Json (Container, Form)` and `Path_Value (Container, Path, Raw)` hold, so `Raw` is exactly the value at `Path` (v3 V-C.1);
  - `Roster_Join` holds: `Anchor` is the roster value for `Kind` (v3 V-C.3).
```

**R3-41 replaces v2 line 914 (in C2-55).**
```text
v2:
   4. **Physical nesting** per §5.3, with the helper successor per §5.4.
v3:
   4. **Physical nesting** per §5.3, with the helper successor and the exact protocol of v3 V-E.1 (steps E3–E6).
```

**R3-42 replaces v2 lines 915-919 (in C2-55).** 03.2: one exact order.
```text
v2:
   5. **Before exec:**
      - actor credential measurement;
      - `K.Check` and `Child_Ready_Conjunction` (`.ads:194-208`);
      - a durable witness, then ACK, then GO;
      - the original stdin/EOF pump (actor stdin V4).
v3:
   5. **Before exec**, in the order of v3 V-E.1 (steps E7–E11), which mirrors the V1 helper:
      - GO_FORK, then actor credential measurement;
      - `K.Check` and `Child_Ready_Conjunction` (`.ads:194-208`);
      - a durable witness, then the commit ACK, then exec;
      - the original stdin/EOF pump (actor stdin V4).
```

**R3-43 replaces v2 line 1517 (in C2-111).**
```text
v2:
| U-3 | v2 | `StartupLease (descriptor)`, then `construct_v2 ()` via `serve ()` | Daemon entry | `worldline.protected-startup-v2`: v1 keys plus `runtime.resource_scoped_producer`; `tools` adds `resource_supervisor_v3`, `bwrap`, `systemctl`, `systemd_run`; `provisioned_state` adds the owner plan, crosswalk, custody v2 DB, lock and genesis | Descriptor, genesis, owner plan, crosswalk, run-scoped config, custody v2 genesis, header DATA | none | Named refusal, or the genuine reconciler (§11.5) |
v3:
| U-3 | v2 | `StartupLease (descriptor)`, then `construct_v2 ()` via `serve ()` | Daemon entry | `worldline.protected-startup-v2`, with the exact key sets of v3 V-J.2: the v1 keys plus `root_worker`; `runtime` adds `resource_scoped_producer`; `tools` includes the V3 supervisor helper, `bwrap`, `systemctl` and `systemd-run` under their installed names; `provisioned_state` adds the owner plan, crosswalk, custody v2 DB, lock and genesis | Descriptor, genesis, owner plan, crosswalk, run-scoped config, custody v2 genesis, header DATA | none | Named refusal, or the genuine reconciler (§11.5) |
```

### B.3 Where each replaced v2 section went

| v2 section | Status in v3 | v3 location |
|---|---|---|
| A (closure tables), C (truth boundary), D | Replaced | §A, §C, Appendix D |
| §3.1–§3.4, §3.6, §3.7, §3.9 | Carried with line replacements (C2-31, C2-36, C2-37, C2-39) | V-B extends them |
| §3.12–§3.16 | Replaced | V-A.2 (ABI and wrapper), V-B.10 (the caller), V-B.9 and V-N (controls), V-M (dependencies), §A.6 (review questions) |
| §4.1 | Carried with line replacements (C2-41) | V-C extends it |
| §4.4, §4.5, §4.7 | Replaced | V-C.6, V-D, V-M |
| §5.3 | Carried (C2-53) | V-E.3 extends it |
| §5.4 | Replaced | V-E.1, V-E.2 |
| §5.5 | Carried with line replacements (C2-55) | V-E.1 |
| §5.7 | Replaced | V-M |
| §6.1, §6.3, §6.7, §6.10, §6.11, §6.13 | Replaced | V-F.6, V-F.5 and V-F.6, V-G.1 and V-G.2, V-G.5, V-F.5 and V-J.3, V-M |
| §7.3, §7.7 | Replaced | V-H, V-M |
| §8.1–§8.3, §8.8 | Replaced | V-I, V-M |
| §9.2 | Carried (C2-92) | V-D.4 extends it |
| §9.5, §9.9 | Replaced | V-L, V-M |
| §10.3, §10.7 | Replaced | V-G.3, V-M |
| §11.1 | Carried with line replacements (C2-111) | V-J.2 makes it exact |
| §11.2, §11.5, §11.9 | Replaced | V-J.2, V-G.5 and V-J.5, V-M |
| §13.1 | Replaced | V-L |
| §14.3–§14.5 | Replaced | V-K |
| §15.2, §15.4 | Replaced | V-M |
| §18 | Carried (C2-18, with R3-20 … R3-24) | V-P adds v3's items |
| §19, Appendices A, B, D | Replaced | V-Q, Appendices A, B, D |

### B.4 Reading rules

- **RR3-1.** Inside carried v2 slices, v2's aliases and notation apply (v2 §C.2, restated in §C.2 below).
- **RR3-2.** A reference inside a carried slice to a replaced v2 section resolves through this map: §3.14 → V-B.9 and V-N; §4.4 → V-C.6; §4.5 → V-D; §5.4 → V-E.1 and V-E.2; §6.1 → V-F.6; §6.3 → V-F.6; §6.7 → V-G.1; §6.10 → V-G.5; §6.11 → V-F.5; §7.3 → V-H; §8.1, §8.2 and §8.3 → V-I; §9.5 → V-L; §11.2 → V-J.2; §11.5 → V-G.5; §13.1 → V-L; §14.3 → V-K.8; §14.5 → V-K.9; §15.2 → V-M. A reference to a carried section (for example §3.4 or §9.2) means that carried slice with its replacements. Any other replaced section resolves through §B.3.
- **RR3-3.** Inside C2-APC, v1's reading rules RR1 … RR5 (carried by C2-B) apply to the v1 slices it binds.
- **RR3-4.** Numbers inside carried slices keep the status v2 gave them: observed, or JACKAL exact (v2 J01 … J18). They are not re-derived here.
- **RR3-5.** R-2's phrase "design v4, unreviewed" inside C2-APC is historical. The current C-API predecessor status is V-K.1.
- **RR3-6.** The FRESH, RETAINED and HISTORICAL domains are those of C2-31 as replaced by R3-29 … R3-31. No scoped canonical caller is FRESH in the v2 sense, and V-B.10 gives the caller-by-caller placement.
- **RR3-7.** "AUTHOR-NOTES" inside a carried slice means v2's `AUTHOR-NOTES.md` (sha256 `782379cd1944dc03e59ec7f50eb4aae70bfbdf69c164e9167817b80883652990`, observed unchanged). It is not v3's.
- **RR3-8.** "Appendix C" inside a carried v2 slice means v2's Appendix C, carried as C2-APC. Its v1 slices (B-S1-CUR, B-S7-CUR and so on) are bound there.

### B.5 v2 statements withdrawn or replaced

| v2 text (location) | Why | Replacement |
|---|---|---|
| "total" `Rebase`/`Emb`, and raw-domain-only exclusions (D:527, D:529, D:556, D:592-593, D:599-604; `seams.json` closure 01.2, 01.3) | TOTAL-EMBEDDING; V2-REQ-B, V2-REQ-L | R3-32 … R3-37; V-B.2 (domains and residuals) |
| FRESH conjunct and FRESH placement for the pre-effect and in-request exchange (D:467-468, D:482, D:484, D:489-495, D:498) | RQ-1; D-1b remaining gap | R3-25 … R3-31; V-B.10 |
| Scoped-only Resource_Refused vector list, multi-frame and multi-bucket (D:642-654) | SCOPED-CONTROLS | V-B.9 |
| WL-SRC-V1 framing and Raw as a sub-span of an expected container (D:693-696) | 02.1; V2-REQ-C | R3-39, R3-40; V-C.1 |
| §5.5 "a durable witness, then ACK, then GO" (D:915-919) | 03.2 | R3-42; V-E.1 |
| E3 "the reserved amount is actually kept available", and the minimum/low mapping of RQ-4 (D:775, D:778, D:801) | 02.4; V2-REQ-D | V-D.1 |
| §5.4 order: "obtains and journals the native child decision … then sends a child-creation request" (D:882) | 03.2; V2-REQ-E | V-E.1 |
| §6.3 and §6.11: UNIQUE `(operation, generation, kind)` as the exclusivity rule (D:1095-1096) | 04.3; V2-REQ-F | V-F.5 |
| §6.2 row PHYSICAL_SETTLED → HISTORICAL_SETTLEMENT: settlement "if a terminal and retained result exist" (D:998) | RECOVERY-DOMAIN | R3-13, V-G.3 |
| §8.4 explicit named status where correspondence fails; §8.7 cookie and user-namespace refusals; §9.4 mandatory cookie and namespace records (D:1285, D:1304-1305, D:1389) | REQUESTER-PROVIDER | R3-15 … R3-18, V-I.6 |
| §6.7: three awaits versus "the physical three" (D:1055-1059) | 04.5; V2-REQ-G | V-G.1 |
| §6.10 row "PREPARED, before HELD → … release" (D:1078) | 04.4; RECOVERY-DOMAIN | V-G.5 rows PR-a, PR-b |
| §7.3 T1 stop before the durable record; T4 I/O before T5 evidence (D:1157-1161) | 08.1, 08.4 | V-H.2 |
| §8.1 J1/J3/J4 unconditional; J5 mandatory cookies (D:1233-1239) | 09.3, 09.5 | V-I.3 |
| §11.5 RT-7's HANDLER_TERMINAL prerequisite (D:1567) | 12.2 | V-G.5 RT-7′ |
| §14.3 R-RW-1 adopting v4 R-GATE/R-ALIAS unchanged; R-RW-2 global ban; §14.5 IC-1 subset; IC-3 global uniqueness (D:1786-1826) | V2-REQ-K; CAPI-SCOPE-CONTRADICTION | V-K |
| §9.5 availability bullets treated as complete (D:1396-1408) | 06.4; V2-REQ-L | V-L |
| §13.1 as the lock model (D:1703-1722) | V2-REQ-L | V-L (SL-0 discipline kept) |
| §15.2 graph (D:1855-1896) | 11.1 | V-M |

---

## C. Truth boundary, bases and method

### C.1 What was done

- **Reading only.** Static reading with the Read tool, and read-only Bash for inspection (`sed -n`, `grep`, `find`, `sha256sum`, `wc`, `cut`, `nl`, `fold`, `cat`, `od`, `tail`, `awk`, and short Python scripts that read files as text or JSON and printed to standard output). No output was redirected to a file. `2>&1` was used only into a pipe. Every command form and deviation is in AUTHOR-NOTES §5.
- **Not run.** No compiler, prover, test, WORLDLINE, COSMOGONY or root-worker code (nothing imported or executed), service, `systemctl`, sudo, namespace, project-vault or restic. No `/srv` lab, store, socket or window was touched.
- **Not read.** Nothing under CAPI5's `review/` directory. The lane draft was read and not changed.
- **SIA.** `sia.ask` once at the start of this task, then one `sia.recall` of a returned slug. The ask returned agent notes labelled `[model]` (agent-authored, model-origin, not evidence) and one `[evidence]` item, the `skills/worldline` skill text. The recall returned a note labelled `[origin:model]`. No SIA content is used as evidence for any design statement. Truth-boundary line, verbatim: "boundary: senses live · chains pass · graph complete · 6 span(s) redacted at ingest · semantic recall · associative rerank off by measured default; retrieval.associative_rerank enables it · absence of recall ≠ evidence of absence". No SIA note was written.
- **Skills.** The eight Ada skills (`ada`, `ada-omarchy`, `spark-users-guide`, `ada-programming`, `advanced-ada`, `gnat-toolchain`, `ada-2005-amendment`, `ada-high-integrity`) and `worldline` and `cosmogony` were already loaded in this session's context and were applied, not reloaded. The SPARK User's Guide is release 28.0w documentation, not evidence about the installed 16.1.0 toolchain.

### C.2 Bases (aliases)

| Alias | Path |
|---|---|
| `W` | `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow` |
| `WT` | `W/work/claude-lead-isolation-v1/wt-1` |
| `L` | `W/work/protected-original-root-worker-repair-v1` (the draft lane) |
| `R` | `L/source`. Unprefixed `core/…`, `runtime/…` and `protected-*/…` paths are relative to `R`. |
| `rw/` | `R/runtime/worldline/` |
| `D2` | `WT/designs/claude-root-worker-seam-design-v2` (v2 design, its slices and its sealed review) |
| `D2R` | `D2/review/gpt61-v1` |
| `CAPI4` | `WT/designs/claude-capi-boundary-design-v4` |
| `CAPI4R` | `CAPI4/review/gpt61-v1` (sealed) |
| `CAPI5` | `WT/designs/claude-capi-boundary-design-v5` (UNREVIEWED; only `DESIGN.md` read) |
| `S5` | `W/work/claude-composition-v5-beta/source` |
| `A1` | `W/work/scoped-committed-envelope-repair-v2-retry1` |
| `CHILD` | `W/work/resource-child-authority-source-v1` |
| `P1/` | `W/outputs/claude-phase1-handoff-20261004/` (`P1:n` is `HANDOFF.md`, line n) |
| `PROMPT` | `/home/sicarii/Documents/complete-phase1-prompt.txt` |
| `D:n` | v2 `SEAM-DESIGN.md`, line n (as the review cites) |

### C.3 Status labels

| Label | Meaning |
|---|---|
| OBSERVED | Read from a file or printed by a read-only command. |
| STATIC_REASONING | The author's inference from read source. Not executed. |
| [unverified reasoning] | Kernel, systemd, interpreter or Ada-visibility semantics as the author reads them. Each names its evidence: a K or RC item (V-O), or the installed-compiler check D-38 of CAPI4. |
| [depends on unreviewed CAPI5] | Relies on a CAPI5 rule that no reviewer has assessed. |
| DESIGN | A proposal for review. |
| OPEN | An obligation not discharged. |

### C.4 Numbers

- Every count in this document is observed: printed by a read-only command or read from a file. Counts quoted from the reviews, v2, CAPI4 or CAPI5 keep their own stated status.
- No numeral in this document was derived by arithmetic, so no JACKAL call was needed. `jackal.json` records that, and confirms that v2's J01 … J18 keep their status inside carried slices.

---

## V-A. Typed V2 consumers end to end (V2-REQ-A; 01.1, 03.3)

### V-A.1 Two relation families, with no implicit bridge

- **V1 (original, unchanged).** These units decide every v1 deployment, and every row whose facts come from the original producers, including today's self-filled pairs (N-10):
  - `Resource_Observation_Classification`: `K.Facts`, `K.Classify`;
  - `Resource_Scoped_Run_Ledger`: `S.Classify`, `S.Native_Valid`, `S.Check`;
  - `Worldline.Resource_Child_Execution`: `Root_Admission`, `Decide`, `Task_Admission`;
  - `Worldline.Resource_Actor_Execution`.
- **V2 (additive).** The units of v2 §5.2 (carried, C2-51):
  - `Resource_Observation_Classification_V2` (`K2`): `Facts_V2`, `Custody_V2`, `Delegated_Custody`, `Classify_V2`;
  - `Resource_Scoped_Run_Ledger_V2` (`S2`): `Native_Valid_V2`, `Check_V2`;
  - `Worldline.Resource_Child_Execution_V2` (`X2`): `Root_Controller_V2`, `Root_Admission_V2`, `Decide_V2`, `Task_Admission_V2`.
- **No mixing.** A packet is entirely V1 or entirely V2. `Facts_V2` embeds `Base : K.Facts`, so V2 decides non-delegated rows through its no-delegation branch, with `Pair_Valid` in place of the self-filled pair equalities (C2-51).

### V-A.2 Consumer table

| Consumer | V1 entry (unchanged or new with V1 types) | V2 entry (new) | Facts and current packet | Wrapper (exact-type dispatch) | Producer | ABI |
|---|---|---|---|---|---|---|
| Scoped canonical operation (S1) | `Worldline.Scoped_Canonical_Operation.Decide`/`Reference` over `S.Facts_Array` (`core/resource_scoped_run_ledger.ads:44`), `S.Native_Valid` (`:247-268`), `S.Current_Facts` (`:296-300`) | `Decide_V2`/`Reference_V2`: the same clauses (C2-31 with R3-25 … R3-31), with `S2.Facts_V2_Array`, `S2.Selection_Array` (per-row optional delegation record), `S2.Native_Valid_V2` and `S2.Current_Facts_V2` | `ScopedPacket` (existing) / `ScopedPacketV2` (new exact type) | `ScopedCanonicalOperationKernel.observe`: `ScopedPacket` → V1 export; `ScopedPacketV2` → V2 export; any other type → named refusal | V1: `_capture`/`_inspect` (`rw/protected_scoped_resource_runtime.py:642-644`). V2: `ScopedV2Producer` (V-A.3). | `wl_scoped_canonical_operation_{version,layout,decide}_v1` (V1 types) and `…_v2` (V2 types) |
| Scoped exchange successor (B2b) | `Worldline.Scoped_Canonical_Exchange.Decide`: the original `Canonical_Exchange.Reference` (`core/worldline-canonical_exchange.ads:151-165`) with its resource conjuncts lifted by the RETAINED join | `Decide_V2` | as above | `ScopedCanonicalExchangeKernel` | as above | `…_v1` / `…_v2` |
| Scoped K4 successor (B2c) | `Worldline.Scoped_Owner_Completion.Decide` (lifted `Canonical_Owner_Completion.Reference`, `core/worldline-canonical_owner_completion.ads:53-60`) | `Decide_V2` | as above | `ScopedOwnerCompletionKernel` | as above | `…_v1` / `…_v2` |
| Root admission | `Root_Admission` (`core/worldline-resource_child_execution.ads:172-184`), unchanged | `X2.Root_Admission_V2` (V2 controller, `Native_Valid_V2`) | as above | existing root kernel wrapper / new V2 wrapper | as above | unchanged / new |
| Child decision and task admission | `Decide` (`:194-208`), `Task_Admission` (`:248-257`), unchanged | `X2.Decide_V2`, `X2.Task_Admission_V2` | as above | existing / new | as above | unchanged / new |
| Scoped ledger transition | `S.Check` (`:443-457`), unchanged | `S2.Check_V2` (C2-51) | as above | scoped service commit: `ScopedPacket` → `Check`, `ScopedPacketV2` → `Check_V2` | as above | unchanged / new |

### V-A.3 Which family decides

- **Selection is deployment-level and authenticated.** A deployment is V2 when the startup descriptor's exact schema is `worldline.protected-startup-v2` (V-J.2) **and** every live row's producer is the V2 producer. Otherwise every packet is V1.
- **The V2 producer.** `ScopedV2Producer` builds `Facts_V2` for every row:
  - tagged source records for P8–P11 from distinct producers (C2-42, V-C);
  - `Delegation_Facts` (C2-51);
  - `Selection` from the crosswalk entry's delegation record, joined to the roster (V-C.3, V-C.6).
- **Before the V2 producers exist,** a v2 deployment refuses the V2 route by name: `SCOPED_V2_PRODUCER_UNAVAILABLE`. This is an interim refusal that keeps its obligation OPEN, under G-2. v1 deployments are unaffected, so no original accepted case moves.
- **No conversion.** No Python function converts a `ScopedPacket` into a `ScopedPacketV2` or back.

### V-A.4 Bridge lemma (Ghost statement; not proved)

**L-BR-1.** Let P2 be a V2 packet in which every row has `Selection` absent and every P8–P11 pair satisfies `Pair_Valid`. Let `Base (P2)` be P2 with every `Facts_V2` replaced by its `Base`. Then `Reference_V2 (P2) = Reference (Base (P2))`, and likewise for B2b, B2c, root admission, the child decision and `Check_V2`.

Proof route:
- The V2 producer fills each `Base` pair field from the record payloads.
- So `Pair_Valid` (payload equality) gives the original `Custody` pair equalities on `Base` (`core/resource_observation_classification.ads:81-84`).
- L-V2-1 (C2-51) then gives `Classify_V2 = Classify`.

### V-A.5 Unchanged

- Every V1 reference, contract and ABI.
- The original wire units and every original export's code, meaning, layout and caller protocol. Altering an original API would be D-7a (operator); none is proposed.

---

## V-B. Original-domain correspondence and RQ-1 (V2-REQ-B; 01.2, 01.3, 01.5, 01.7)

### V-B.1 Withdrawn

- v2's "total" `Rebase` and `Emb`.
- v2's FRESH conjunct for the pre-effect and the in-request exchange.
- v2's scoped-only refusal list (§B.5).

### V-B.2 Domains

| Domain | Definition |
|---|---|
| D_raw | Every input of the original `Worldline.Canonical_Operation.Reference` |
| D_prod | Inputs the original flat producers can present. The ledger is reached from an authentic empty ledger by `L.Check = Ready` steps (`core/resource_run_ledger.ads:392-404`), so L-INV-1 holds. Every observed liveness is `K.Classify` of the producer's facts (`core/resource_observation_classification.ads:121-125`). |
| D_emb | Inputs that have a coherent witness under one of the constructions V-B.4 … V-B.6 |

Obligations, stated and not proved:
- **CV-B′.** D_prod ⊆ D_emb, via the single-frame construction.
- **CV-R.** D_raw \ D_emb equals exactly R1 ∪ R2 ∪ R3 (V-B.5 … V-B.7).

How residuals are treated:
- A residual input is never routed to the successor.
- The original unit decides every flat input (byte-exact, G-1), and flat principals keep calling it.
- Scoped callers present only scoped packets made by the scoped producer.

So no original accepted case is excluded from the system. A residual is a coverage limit of the correspondence proof, and it stays OPEN.

### V-B.3 Witness span forms (with R3-4)

Each witness field takes one of three forms:
1. **(a) A present zero-length span.**
   - Identity validity holds for length 0 anywhere (`core/resource_reservation_transition.ads:85-88`).
   - Two present zero-length identities are `Same` (`:93-100`).
   - A zero-length quantity has value 0 (little-endian magnitude, `core/resource_quantities.ads:12-17`, `:25-28`).
2. **(b) An alias of an original span.**
   - `Same` compares bytes (`core/resource_reservation_transition.ads:93-100`), and `Q.Value` reads content, so aliases preserve every relation.
3. **(c) Fresh bytes**, only where (a) and (b) cannot supply a value: text constants, or a positive numeral.

W10 (no witness field computed from a scoped decision) is unchanged.

### V-B.4 Single-frame construction (default)

The construction is C2-37 (v2 §3.7, carried with R3-33 and R3-34), with these field forms:
- **Present zero-length:** frame head, store genesis and id, root head, cause, requester, receipt, catalogue and observation heads, physical head, `K_Resource`, `K_Unit`, capacity source, bucket observation head, and `First_Epoch` (value 0, which is ≤ every epoch).
- **N = D:** an alias of a positive-valued span supplied by L-SAT-1.
- **`Amt (i)`:** an alias of the span that `L.Amount` selects (`core/resource_run_ledger.ads:187-192`): `Observed_Usage.Value` or `Amount`. A zero-length span when the row is Released.
- **`Fct (i)`:** the producer's facts (W6, W7).
  - Unknown and Never_Launched rows need only aliases and zero-length spans (`core/resource_observation_classification.ads:96-102`).
  - Live and Reaped rows need the `Text` constants of `Custody`, `Live_Holds` and `Reaped_Holds` (`:79-114`). Producer-built arenas contain them. Otherwise form (c) applies.

**L-SAT-1** (statement, to prove).
- If clause C1 does not refuse, some grant is `Grant_Valid`.
- `Grant_Valid` requires `Issued_At < Expires_At` with both non-negative (`core/worldline-operation_authority.ads:72-82`), so its `Expires_At` span has a positive value. That span is the alias for N.
- If C1 refuses, the decision is `Authority_Refused` before C2, by the original clause order (`core/worldline-canonical_operation.adb:10-34`), so N may be any span.

### V-B.5 Multi-frame construction (G1)

**Inputs.** Inputs in which some row's universe head differs from the state's. L.Shape allows this (`core/resource_run_ledger.ads:223-235` checks the rows' contexts, not their universe heads). `L.Check` excludes it from D_prod (`:342-345`, `:367`).

**Construction.**
1. Sort rows by epoch and split them into maximal runs of equal universe head. Frames F_1 … F_k get one run each.
2. **Scope.** `F_j.Scope = State'.Scope`, since every row is `Same_Context` with the state (`:229-232`).
3. **Universe head.** `F_j.Universe_Head` is an alias of the run's head.
4. **First epochs.** `F_1.First_Epoch` is zero-length. For j > 1, `F_j.First_Epoch` is an alias of the run's least row epoch.
5. **Frame heads.** `Frame_Head (F_j)` is an alias of the reservation span of the run's first row. These are pairwise distinct, because rows have distinct reservations (`:233-235`).
6. **Prior frames.** `Prior_Frame (F_j) = Frame_Head (F_{j-1})`.
7. **Store identities.** Store genesis and store id are a common zero-length span.
8. **Last frame.** If the last run's head is not the state's head, append a frame with the state's head. Its `First_Epoch` is an alias of the state's epoch. Its frame head is any span distinct from the others: an alias where one exists, otherwise form (c).

**Validity conditions,** from `History_Valid` and `Retained_Origin` (`core/resource_scoped_run_ledger.ads:92-109`, `:116-121`):
- (i) the greatest epoch of run j is less than the least epoch of run j+1;
- (ii) when a last frame is appended, the greatest row epoch is less than the state epoch.

**Residual R1.** Inputs violating (i) or (ii). None is in D_prod (L-INV-1).

### V-B.6 Saturated-arena construction (G3)

| Case | Construction | Coverage |
|---|---|---|
| S-a: no form-(c) field is needed. There is no Live or Reaped row, or the needed text constants and a positive numeral already occur in `Data`. | Forms (a) and (b) only, inside `Data` itself. No witness region. | Saturated arenas included: `Data'First = 1` and `Data'Last = Byte_Count'Last` (`core/resource_quantities.ads:7-9`). |
| S-b: constants are needed and absent | **Compaction.** `Data2` is the maximal intervals of the union of every span the original packet references, in order, followed by the constants. `Rebase` maps each span to its compacted position. | Holds when the union's length plus the constants' length is at most `Byte_Count'Last`. |

- **L-RB-4** (statement, to prove). Every predicate used by `O.Reference` and the scoped `Reference` depends on span contents and span validity only, never on absolute positions. Such predicates read only `Data (First + Offset)` forms. This is to be shown by a static audit of the predicates, then proved.
- **Residual R3.** A Live or Reaped row is present, the constants are absent from `Data`, and the referenced union is longer than `Byte_Count'Last` minus the constants' length. Such an arena exceeds anything a producer can allocate. No claim is made about it. The original unit decides it, and its coverage stays OPEN (RQ-2).

### V-B.7 Raw-invalid versus legitimate producer domains (G2, G6)

- **Residual R2.** Inputs for which no facts make W6 and W7 hold: an `Observed` label that no `K.Classify` application produces (G2), or a Live row without effect whose observed unit fields match no facts (G6).
- Flat `L.Native_Valid` does not re-derive liveness (`core/resource_run_ledger.ads:266-282`). The scoped `Native_Valid` does (`core/resource_scoped_run_ledger.ads:256-257`).
- In D_prod every label comes from `K.Classify`, so W6 holds.
- R2 inputs are not in D_prod. The original unit decides them. G6 is covered by W7 for D_prod.

### V-B.8 Extra conjuncts, derived from the caller domain

Each scoped conjunct without a flat counterpart is discharged on the scoped producer's domain by a producer lemma, stated and not proved:

| Lemma | Conjunct | Basis |
|---|---|---|
| PD-1 | `Current_Facts` (`:296-300`) (RQ-3) | The producer builds every fact from the same `current` it validates (`rw/protected_scoped_resource_runtime.py:642-646`). This is a Python producer-correspondence obligation plus the native `validate`. |
| PD-2 | `Retained_Origin` of every row | Every committed row entered through a `Check = Ready` Reserve. Check's post ensures `Shape (Proposed …)` (`:450-452`), and later transitions keep historical rows (`:422-423`, `:441`). |
| PD-3 | `Physical_Reference`, `Contained_Reference` | Check's post (`:450-453`) |
| PD-4 | `Current_Valid` | The producer re-reads its snapshot before deciding (`before == current_snapshot ()`, `rw/protected_scoped_resource_runtime.py:696`; `rw/protected_operations.py:711`). |
| PD-5 | `History_Valid` | Check's post (`History_Prefix`, `:452`) and `Advance_Valid` (`:313-339`) |

### V-B.9 Qualified scoped fixtures (replaces v2 §3.14's scoped list)

**Refusal vectors.** Each gives `Resource_Refused` and names the predicate it violates:

| Vector | Violated predicate |
|---|---|
| Broken `Prior_Frame` chain | `History_Valid` `:100-104` |
| Duplicate frame head | `:105-106` |
| Row whose epoch lies in no frame interval | `Retained_Origin` `:116-121` |
| Child row without an earlier supporting parent | `Contained_Reference` `:204-206` |
| Bucket `Held_Total` off by one unit | `Physical_Reference` `:188-190` |
| Projection with a non-zero remainder | `Projection_Valid` `:149-150` |
| Stale current observation | `Current_Valid` `:216-231` |
| Facts of another current observation | `Current_Facts` `:296-300` |

**Positive vectors.** Each must give `Ready`:
- a valid multi-frame history whose bound row's origin is an earlier frame;
- a valid multi-bucket roster with distinct keys;
- an exact projection with N ≠ D;
- the rollover positives of V-B.10.

A multi-frame or multi-bucket **shape** alone never refuses.

### V-B.10 RQ-1: command, caller and time mapping

**Domains.** FRESH, RETAINED and HISTORICAL are C2-31's (v2 §3.4) as replaced by R3-29 … R3-31.

**Rule.**
- The scoped canonical operation and its exchange (B2b) and K4 (B2c) successors carry **no current-context conjunct** (R3-25, R3-29).
- Each uses `Retained_Join`, which is C2-31's RETAINED points 1–5 with R3-30 and R3-31:
  - `Retained_Origin` of the bound row, which is also C2's join (R3-25), with `Same_Binding` and the row in `Reserved | Launch_Intent | Running`;
  - C3's instance, policy and policy-epoch equalities against the bound row's own origin scope (R3-26);
  - for the pre-effect and the in-request exchange, C1 unchanged: `Reserve_Use` on the current snapshot must give `Reserved_Replay` (`core/worldline-canonical_operation.adb:10`; `core/worldline-operation_authority.adb:111-113`). For exchange recovery and K4, the original use replays to `Reserved_New` on its retained snapshot (R3-31);
  - every original retained-origin lifecycle step, preserved (C2-31 point 5).
- **Current context is checked only by the native scoped commands that require it:**
  - Reserve (`core/resource_scoped_run_ledger.ads:359`, `:436-438`);
  - Record_Launch_Intent and Record_Running (`:436-438`).
- Every other lifecycle command joins the request to the row's origin scope (`:373-375`).
- Every ordinary scoped command, whatever its kind, also requires `Current_Valid` of its own current observation packet (`:426-430`). That conjunct is the original transition's observation freshness, not a request-context check, and it is unchanged.
- Rollovers are routine (NF-2).

| Caller (source) | When | Native scoped commands | Current context required (source) | Canonical conjunct | Positive rollover control | Refusal control |
|---|---|---|---|---|---|---|
| Reserve: `_reserve` → `intent_for_operation`/`submit_bound` (`rw/protected_operations.py:623-676`) | t0 | Reserve | yes (`:359`, `:436-438`) | none (A `RESERVE_USE`) | Rollover before t0: the reservation is made under the new context | Request scope stale → `Context_Changed` |
| Serial pre-effect (`rw/protected_operations.py:678-714`) | t0 < t1, same section under `operation_lock` | none (machine-admission observation only) | no | Retained_Join | Root-head-only rollover, and scope rollover, between t0 and t1 → `Ready` | Bound row Released → `Resource_Refused` |
| Root pre-effect (`rw/protected_root_worker.py:167`) | same | none | no | Retained_Join | same | same |
| Launch: `launch_reserved`; root `launch_root_worker` (`rw/protected_root_worker.py:172`) | t1 < t2 | Record_Launch_Intent, Record_Running | yes (`:436-438`) | none | Root-head-only rollover → launch `Ready` (NF-2) | Scope or universe rollover → native `Context_Changed`, an existing scoped-kernel refusal. Then quarantine and K4 by the original semantics (`rw/protected_operations.py:767-768`). |
| GO: `go_scoped` (`rw/protected_scoped_resource_runtime.py:851-865`) | after Running | none (machine admission at GO; `GO_INTENT` journal) | no | none | — | — |
| In-request exchange: broker commit (`rw/canonical_full_broker.py:147-174`) | during the handler | exchange phases ISSUED … CANONICAL_INTENT | no | Retained_Join (B2b) | Rollover between pre-effect and commit → `Ready` | Changed binding → `Refused` |
| Exchange recovery after restart: `broker.recover` (`:177-191`), from `reconcile_before_endpoint` (`rw/protected_operations.py:369-375`) | after restart | RECORD_EFFECT | no | Retained_Join (B2b) | Rollover before restart → `Ready` | — |
| Settlement: `finish` → `settle_historical`; collector | after the effect or closure | Record_Terminal, Release_Hold, Charge_Budget, Retain_Uncertain | no (origin join `:373-375`) | none (HISTORICAL) | Rollover before settlement → release `Ready` | — |
| K4 owner completion: `resolve_historical`; `Canonical_Owner_Completion` | after quarantine | lifecycle commands (origin join) plus the resolving request's own fresh use | no | Retained_Join (B2c) | Rollover → `Ready` | Wrong quarantine head → `Refused` |
| Startup reconcile (`rw/protected_scoped_resource_runtime.py:611-622`) | startup | Retain_Uncertain, Record_Terminal, Release_Hold | no | none | Rollover → reconcile `Ready` | — |
| Child task admission (`core/worldline-resource_child_execution.ads:248-257`) | during the root workload | Reserve (child row) | yes (native) | none (`Task_Admission`) | — | Stale child scope → `Context_Changed` |

**RQ-1** is answered at design level. It and its original obligations stay OPEN until the fixtures and proofs exist.

---

## V-C. Source records, anchors, crosswalk and P3 (V2-REQ-C; 02.1–02.3, D-7a)

### V-C.1 Expected-side records: native extraction from unchanged containers

**Containers are canonical JSON.**
- `exact_json` requires the raw bytes to equal the canonical encoding, optionally plus a trailing newline. It refuses duplicate keys and non-finite numbers (`rw/protected_startup.py:40-51`).
- That canonical encoding is `protected_startup.canonical`: sorted keys, `,` and `:` separators, `ensure_ascii=False`, encoded as UTF-8 (`rw/protected_startup.py:35-37`). Call it form UTF8.
- This covers the descriptor, startup genesis, custody genesis and owner plan (all read by `exact_json`: `rw/protected_startup.py:172`, `:189`; `rw/root_worker_journal.py:42`; `rw/protected_root_worker.py:97`), and (V-J.2) the crosswalk.
- The run-scoped config, which holds the resource catalogue, is read by `exact` instead: the ASCII encoder of `rw/protected_resource_runtime.py:20`, with no trailing LF (`:22-23`; `rw/protected_scoped_resource_service.py:68-74`). Call it form ASCII (NF-8).

**CJ-1** (to prove). In a canonical container, the bytes of any nested value are exactly that value's own canonical encoding.

**An expected record** is a `Source_Record` of C2-41 (with R3-38) with `Which = Expected`: `Container` is the span of the exact container bytes; `Path` encodes a sequence of object keys or array indices; `Raw` is the value span at `Path` inside `Container`; `Anchor` holds a SHA-256; `Kind` is the roster kind and `Form` the container's JSON form.

**Native relations**, in the new SPARK unit `Worldline.Source_Json`:
1. `Canonical_Json (Container, Form)`. A total recognizer of what the selected encoder emits, with Form chosen by the container's kind, never by its bytes:
   - no insignificant whitespace; for form UTF8 an optional single trailing LF, for form ASCII none;
   - strings in which `"` and `\` appear only as `\"` and `\\`, the controls U+0008, U+000C, U+000A, U+000D and U+0009 only as `\b`, `\f`, `\n`, `\r` and `\t`, and every other control below U+0020 only as `\u00XX` with lowercase hex digits. Every other character is its raw UTF-8 bytes in form UTF8; in form ASCII, a non-ASCII character is `\uXXXX`, or a surrogate pair of them, with lowercase hex digits, and every byte is below 0x80 **[unverified reasoning, RC-4: the installed CPython's `json` encoder]**;
   - objects whose keys are strictly increasing by decoded code-point sequence (sorted, no duplicates);
   - arrays; number lexemes of the RFC 8259 grammar; `true`, `false` and `null`.

   The unchanged Python check (`exact_json` or `exact`) runs first and establishes canonicality. The native recognizer must accept every byte string that check accepts and give each nested value's exact span. On its own it refuses whitespace, unsorted or duplicate keys, malformed UTF-8 and non-canonical string escapes. It accepts number lexemes by the RFC 8259 grammar, so the canonicality of numbers rests on the Python check alone. That is a stated limit, not a claim.
2. `Path_Value (Container, Path, Raw)`. `Raw` is the exact span of the value at `Path`. Total, by structural scan, with a `Subprogram_Variant` on the remaining length.
3. `Extract (Domain, Raw)`, giving the canonical comparable encoding (CCE): a string becomes its unescaped bytes, an integer its canonical decimal, an object or array its raw canonical bytes (by CJ-1).

No WL-SRC-V1 framing applies to expected records of container domains (R3-39). `Container_Bound` (R3-40) joins these relations with the anchor and the roster. The unit's linear native cost is a D2 obligation and stays OPEN.

### V-C.2 Framed producer records

Every observed-side record, and the expected-side records of producer domains (P3, P6, P8, P9, P11), are WL-SRC-V1 producer frames (C2-41 line 693, as replaced by R3-39): magic, domain, field, side, value length, value, evidence length, evidence. These are new records that producers create and journal, so framing them is feasible. Their anchors are journal event identities, checked natively only for validity and distinctness (C2-41).

### V-C.3 Anchor join to the authenticated roster

`Roster_Join (Exp, Roster)` holds when `Exp.Anchor` equals `Roster (Exp.Kind)`. The roster is derived natively:

| Kind | Roster value | Source |
|---|---|---|
| `Descriptor` | `Custody_Genesis.startup_descriptor_sha256` | `rw/root_worker_journal.py:43-49` |
| `Owner_Plan` | `Custody_Genesis.owner_plan_sha256` | same |
| `Startup_Genesis`, `Crosswalk` | `Installed_Digest (Descriptor, P)` for the file's path P (for the startup genesis, P is `Path_Value (Descriptor, ["genesis"])`; for the crosswalk, `["root_worker", "crosswalk"]`) | the descriptor's installed inventory (`rw/protected_startup.py:251-262`, with `inventory` at `:104-113`); V-J.2 requires both in `files` |
| `Policy` | `Installed_Digest (Descriptor, P)` of the operation policy file, which must also equal the crosswalk's `policy_sha256` | an installed file today (`rw/protected_operations.py:303-306`), in `files` or `trees` |
| `Run_Config` (holds the catalogue) | `Installed_Digest (Descriptor, P)` of the run-scoped config, form ASCII. The catalogue is the value at `["catalogue"]`, and the SHA-256 of that span must equal the crosswalk's `catalogue_sha256`. By CJ-1 it also equals the scoped `catalogue_head` (`rw/protected_scoped_resource_runtime.py:164`, `:178`). | an installed file today (`rw/protected_scoped_resource_service.py:68-74`) |
| helper image, header DATA | the crosswalk entry's `helper_image_sha256` and `header_data` values | roster-bound through the crosswalk's own anchor |

`Installed_Digest (Descriptor, P)` is the sha256 recorded for P in the descriptor: `Path_Value (Descriptor, ["files", P, "sha256"])`, or `Path_Value (Descriptor, ["trees", Root, Rel, "sha256"])` for a tree root `Root` with P = Root/Rel. It holds only when at least one entry exists and all existing entries agree.

Native checks:
- `Container_Bound` (`Anchor = SHA-256 (Container)`), using the proved `Attest.SHA256`;
- `SHA-256 (Descriptor_Container) = Custody_Genesis.startup_descriptor_sha256`.

**Genesis authenticity (NF-11).**
- Today the custody genesis carries no MAC. It is bound as source-lease DATA (`rw/root_worker_journal.py:39-41`) and by exact equalities with the descriptor digest, the owner-plan digest and the issuer-key digest (`:43-53`). Its stored copy must equal it (`:95-97`).
- Events and the head carry an HMAC-SHA256 under the issuer key, and the head MAC covers the genesis (`:25-26`, `:99-113`).
- v3 adds a native `Hmac_Sha256` over `Attest.SHA256`, with the key passed inside the private arena. It verifies every event MAC and the head MAC natively, so the genesis content is authenticated under the issuer key and not only by Python.
- Key handling, meaning the arena's lifetime and zeroization, is a non-claim and stays OPEN.

### V-C.4 Per-domain grammar

| Pair | Observed domain: raw grammar → CCE | Expected domain: container, path → CCE |
|---|---|---|
| P1 owner_endpoint | `Listener_Bind`: WL-SRC-V1 frame of `getsockname` bytes and (dev, ino) → `sun_path` bytes **[unverified reasoning, K-13]** | `Descriptor_Endpoint`: descriptor, `["endpoint", "path"]` → string bytes |
| P2 source_lease | `Loader_Exec_Record`: WL-SRC-V1 frame of the worker's early-loader lease (role, path, sha256), sorted → canonical list | `Owner_Plan_Sources`: owner plan, `["sources"]` → canonical list restricted to SOURCE and EXECUTABLE roles |
| P3 process source | see V-C.7 | see V-C.7 |
| P4 worker image | `Helper_Exe_Read`: WL-SRC-V1 frame of the sha256 of `/proc/<helper>/exe`, read through the read-only procfs view (M-2) with pidfd pinning | `Crosswalk_Helper_Digest`: crosswalk, `["entries", i, "helper_image_sha256"]` |
| P5 handler plan | `Worker_Process_Read`: frame of raw cmdline and exe digest, with the custody-fd argument excluded | `Crosswalk_Coordinator_Plan`: crosswalk, `["entries", i, "coordinator"]` → canonical object, with the argv template instantiated natively |
| P6 running event | `Custody_Running_Event`: custody `RUNNING` event record | `Scoped_Running_Commit`: committed `RECORD_RUNNING` packet and reply (scoped history) → (reservation, planned unit, actual unit, cgroup, invocation, ledger head) |
| P7 store genesis | `Store_Meta_Read`: frame of `protectedStoreGenesis`, read under the store lock | `Startup_Genesis_Store`: startup genesis, `["store", "identity"]` |
| P8 namespace | `Namespace_Read`: frame of (dev, ino), read now | `Helper_Held_Frame`: HELD custody event payload |
| P9 peer | `Channel_Peer_Read`: raw ucred of the supervisor channel | `Helper_Held_Frame` peer |
| P10 helper image | `Helper_Exe_Read` | `Crosswalk_Helper_Digest` |
| P11 challenge | `Helper_Ticket_Echo`: the ticket in the HELD and CLOSED frames | `Dispatch_Ticket`: the `DISPATCH_INTENT` record |

`Domain_Allowed (Field, Which, Domain)` is exactly this table. Any other combination is false.

### V-C.5 What the predicates establish, and what they do not

**A copied or relabelled record fails, per V-C.4:**
- `Pair_Valid` requires `Obs.Which = Observed`, `Exp.Which = Expected`, distinct domains, and grammar membership per side.
- An expected record also needs `Canonical_Json`, `Path_Value`, `Container_Bound` and `Roster_Join`.
- So an expected-side record must be the genuine roster-bound container or a SHA-256 preimage of it.
- A copy of the expected value into an observed frame must be a journaled custody event with distinct valid anchors. It then fails payload equality if it is corrupted, and the raw-distinctness conjunct if it is copied verbatim.

**Non-claim.** A forged but well-formed observed frame written by a compromised producer is not detected natively. Producer authenticity stays an OS-workstream obligation (P1:137, OB-030).

### V-C.6 The full dynamic crosswalk

**Schema** `worldline.protected-root-operation-crosswalk-v1` (canonical JSON):

```text
{"schema":"worldline.protected-root-operation-crosswalk-v1",
 "installation":<installation_id>,
 "policy_sha256":<sha256 of the operation policy file>,
 "catalogue_sha256":<sha256 of the catalogue value span in the run-scoped config>,
 "entries":[ sorted by (kind,name,right) ;
   {"kind":"operation"|"owner_route"|"followup",
    "name":<OPS name | owner route>, "right":<followup right or null>,
    "plan_sha256":<sha256 of policy.plans[name] or of broker.followup_plans[right]>,
    "cost_key":<the plan's cost_key>,
    "coordinator":{"interpreter_sha256":…,"entry":…,"envelope_sha256":…,"argv_template":[…],"worker_policy_sha256":…},
    "helper_image_sha256":…, "child_plans":[{"task_kind":…,"plan_sha256":…}…],
    "delegation_record_sha256":<sha256 or null>,
    "physical_key":{"machine":…,"resource":…,"unit":…},
    "header_data":[{"path":…,"sha256":…}…]} ] }
```

**Native decode**, in the new unit `Worldline.Root_Crosswalk`:
- **`Entry_For (Crosswalk, Kind, Name, Right)`.** The unique entry. Absence is a named refusal that keeps the obligation OPEN.
- **`Plan_Join`.** `entry.plan_sha256 = SHA-256 (Path_Value (Policy, ["plans", Name]))`, or for a follow-up, `["broker", "followup_plans", Right]` (`rw/canonical_full_broker.py:202-217`). By CJ-1 the value span is the plan's canonical bytes. The policy container is roster-bound (`Policy` kind).
- **`Cost_Join`.**
  - `entry.cost_key` equals the plan's `cost_key`.
  - The catalogue entry selected by (scope policy, resource, unit) yields `costs[cost_key] = {kind, amount}` (`rw/protected_scoped_resource_runtime.py:374-381`).
  - That kind and amount must equal the reservation request's.
  - The catalogue is roster-bound through the run-scoped config (`Run_Config` kind). Magnitudes are never changed.
- **`Followup_Join`.** The broker still selects follow-up rights dynamically by (operation, right, event_id) through `followup_plan`. The crosswalk only binds the right's plan digest. The event binding stays the broker's.

**Rules** (v2 §4.4's, restated here because that section is replaced):
- **Coverage.** One entry for each original operation in the `OPS` roster (`rw/operation_authority_kernel.py:8`), each owner route (`owner.retry`, `owner.adopt`, `owner.recover`, `quarantine.resolve`) and each follow-up right of `policy['broker']['followup_plans']`.
- **Binding, never copying.** An entry binds the original plan's digest and never copies or replaces the plan.
- **One source of plan truth.** `pre_effect`, `launch_root_worker`, `resource_launch_material` and `machine_admission` all read the same entry. That removes the dual policy source and the root `cost_key` equality refusal (`rw/protected_root_resource.py:40-41`) without weakening either comparison.
- **Magnitudes unchanged.** The reservation kind and amount still come from the catalogue `costs[cost_key]` of the operation's own plan. The crosswalk adds no cost, caps no magnitude and narrows no case. Two operations with different cost keys both dispatch.
- **Absence** of an entry is a named refusal that keeps the obligation OPEN. Nothing is defaulted.
- **Native cost.** Container hashing and extraction add checked-build native cost, a D2 item that stays OPEN.

### V-C.7 P3, the process source pair, defined

**Observed side**, `Process_Images` (`Host_Process_Exec` domain, C2-41):
- From the worker's `/proc/<pid>/maps`, read through the read-only procfs view (M-2) with pidfd pinning: the executable image plus every file-backed mapping.
- Each entry is (path, dev, ino, sha256 of the file opened through `map_files` where available).
- Today's capture already checks each mapped path against the lease (`rw/root_worker_process_capture.py:69-74`).

**Expected side.** The P2 loader lease record (`Loader_Exec_Record`).

**Relation `Process_Images_Covered (Images, Lease)`** (native subset relation):
- Every image is a lease entry with role INTERPRETER, EXECUTABLE, EXTENSION or DATA and an equal sha256.
- The exe is a lease entry with role INTERPRETER or EXECUTABLE, as today (`rw/root_worker_process_capture.py:69-70`).
- Each image's (dev, ino) equals the identity of the file that was hashed. This prevents a path swap after mapping **[unverified reasoning, K-19]**.

**Coverage.** Natively mapped code: the interpreter, extensions and shared objects.

**Retained non-claims:**
- Python SOURCE-role files are read, not mapped. Their identity rests on the loader lease (P2) alone.
- Anonymous executable memory (JIT, `ctypes`) is not covered.
- Files mapped and unmapped outside the capture interval are not covered. The capture is a point-in-time snapshot, with before/after equality only (`rw/root_worker_process_capture.py:75-88`).
- The relation does not establish that the process is running only those images, or what that code computes.

### V-C.8 Original producers and cases kept

The V1 `Root_Controller` and its producers (`rw/protected_root_observation.py:32-49`) stay for v1 deployments. V2 controllers and joins apply only where the V2 producers of V-A.3 exist.

---

## V-D. Capacity correspondence and the accounting comparison (V2-REQ-D; 02.4, 06.2, D-4a)

### V-D.1 Withdrawn

- E3's sentence "the withholding includes every outstanding held capacity, so the reserved amount is actually kept available" (D:775).
- The mapping of "minimum/low" to the admission floors and `memory_high_bytes` (D:778, D:801, RQ-4).

`memory.high` throttles and applies reclaim pressure; `memory.min` and `memory.low` protect from reclaim. These are documentation statements from the review's cited Linux cgroup v2 documentation, **[unverified reasoning, K-16]** on this machine.

### V-D.2 Per-class correspondence

Sources:
- the original policy fields (`rw/admission.py:76-85`);
- the admission sample (`rw/protected_scoped_resource_runtime.py:649-695`; floors in `rw/config.py:192-195`);
- the ledger (`core/resource_scoped_run_ledger.ads:285-288`).

| Class | Ledger quantity | Original enforcement (policy field) | Admission sample | Reserved against interference? (STATIC_REASONING) | Candidate mechanism for D-4a (none selected) | Readback | Status |
|---|---|---|---|---|---|---|---|
| Memory (`MEMORY_BYTES` role) | Held projection per top-level row; withheld total (`:652-673`, `:680`) | `memory_max_bytes` (hard limit), `memory_high_bytes` (throttle), `memory_swap_max_bytes` | `available_memory − withheld ≥ min_free_memory_bytes`; pressure ceiling | **No.** Another process may take memory after the sample (OB-176's gap). | **P-M1** per-unit `memory.min` equal to the projected reservation, held by the helper outside the coordinator's reach. **P-M2** `memory.low`. **P-M3** none (status quo). Feasibility for P-M1 needs the bucket capacity at most host memory minus the original floor (`Within_Capacity` bounds the held sum). | `memory.min`/`memory.low`/`memory.max` readback; `memory.current`; `memory.events` oom counters | OPEN. A protection claim requires a selected mechanism and its measurement. |
| CPU | none | `cpu_quota_percent` (cap), `cpu_weight` (share) | none | Not reservable. CPU is time-shared; progress under weight share only. | none proposed | `cpu.max`, `cpu.weight`, `cpu.stat` | No reservation claim |
| Tasks | none | `tasks_max` (cap per unit) | none | **No.** Global PID exhaustion by others is possible. The pids controller has no minimum. | none, short of a cap on others, which is not proposed | `pids.max`, `pids.current` | OPEN; non-claim |
| Disk bytes and inodes | none | `disk_growth_max_bytes` (cap) | `min_free_disk_bytes`, `min_free_inodes` floors | **No.** Other writers can fill the filesystem. | **P-D1** a dedicated filesystem or project quota with reserved blocks for workload and store. This is a provider and operator decision. | statfs; quota readback | OPEN |
| Concurrency | outstanding count | `max_concurrent_workloads` | `outstanding_count` vs limit (`:676`) | Yes, in software at admission | — | admission record | Enforced as original |
| Time | — | `timeout_seconds` (the workload's own mechanism) | — | n/a | unchanged | — | Original |
| Native cost | — | — | — | — | — | — | D2 obligations OPEN |

**Completion guarantee (OB-176).** "Admitted work holds real, enforced reservations so it can finish" is **not claimed** for any class. It would hold only for a class whose reservation is protected by a selected and measured mechanism, and whose workload stays within its own limits. No resource-policy field, cap, provider prerequisite or accepted native failure is added. Selecting P-M1, P-M2 or P-D1 is an authoritative resource-policy change, reserved to the operator (D-4a, OP-3).

### V-D.3 E1–E4, restated

- **E1, E2 and E4** are carried in substance: exact correspondence of each enforced control under its documented representation (K-8); hard memory limit at most the projection; concurrency, disk growth and timeout by their original mechanisms.
- **E3** is now only "machine admission accepted at DISPATCH and GO under the original floors and withholding". It is a sample, and it asserts nothing about future availability.

### V-D.4 Independent-request accounting comparison, completed

Options A, B, C and E are C2-92 (v2 §9.2, carried verbatim with their known gaps), summarized here with the added columns. F is new.

| Option | AM cells kept (C2-91) | Who is metered | Protection of a later request's reservation | Double counting | Availability | Cost | Known gaps |
|---|---|---|---|---|---|---|---|
| A: contained child hold under the root | AM-3, AM-5, partly AM-8 | the root unit | none beyond the root's | no | good | low | AM-1, AM-2 (borrows the first root's grant), AM-4, AM-6, AM-7 (C2-92) |
| B: ownership handoff between requests | AM-1–AM-7 at ledger level | each request in the front | as serial | no | poor: waits for detached jobs | moderate | Liveness regression |
| C: nested units per request under the delegated subtree | AM-1–AM-7 | only nested work; handler code stays in the coordinator | per nested unit (if P-M1) | **yes**: the root counter includes descendants (`rw/protected_scoped_resource_runtime.py:655-658`) | good | moderate | Unmetered handler work; root ceiling bounds all |
| E: ledger-only hold, handler in the coordinator | AM-1–AM-7, AM-9 | the coordinator container | none: in-process work shares the root's limits | no | good | low | Root limit may kill admitted work, or unbacked headroom is needed |
| **F (new): per-request handler subprocess in its own nested unit** under the delegated subtree. Its limits and protection derive from that request's own reservation. The root's outer ceiling is raised by the helper by exactly the nested reservations, on a native ledger-backed request. | AM-1–AM-9 at ledger level | each request's own unit | per request (if P-M1) | no, if the root's own reservation excludes nested units and the ceiling equals root plus nested | good | higher: a process per request | The helper must change the root's ceiling dynamically (a helper command, V-E); the coordinator cannot raise its own (P-CE1). Interpreter start-up cost. **[unverified reasoning, K-8, K-16]** |

No option is selected. The lead's comparison is ready for independent review. Any authoritative policy change, such as F's dynamic ceiling policy or P-M1, is the operator's selection (D-4a). Until then, later consequential requests on the root route are served only through the routing of C2-93, and their accepted cases stay OPEN.

---

## V-E. Child protocol and coordinator reachability (V2-REQ-E; 03.2, D-5a, D-5b)

### V-E.1 One exact protocol

It mirrors the existing V1 root helper order:
1. the outer helper reads `'H'` from init, opens the pidfd and namespace, and sends `HELD` with seven descriptors (`protected-root/native_root_worker_supervisor_v1.c:343-347`, `:239-250`);
2. on `'G'` from the owner, init forks the worker (`:262-266`, `:350-355`);
3. the worker sends its credential frame and waits for the commit (`:166-227`), then execs (`:280-291`);
4. `CLOSED … ECHILD` (`:359`), then the owner's `'A'` (`:366`).

| Step | Actor | Action | Durable record | Native decision |
|---|---|---|---|---|
| E1 | Worker (coordinator) | `TaskIntent`: task id, the complete original workload capture, world ancestry, child plan from the crosswalk (C2-55 item 2.1) | `TASK_INTENT(t)` | — |
| E2 | Worker | Child `RESERVE`: parent is the root reservation, operation is the task id, the root's capability, use, owner and provenance | scoped commit | `Task_Admission` / `Task_Admission_V2` (`core/worldline-resource_child_execution.ads:248-257`): `Check`/`Check_V2` and `Task_Request_Holds` (`:209-231`) |
| E3 | Worker → helper | `CREATE_CHILD` on the helper command channel: task id, child reservation, leaf name, limits from the crosswalk child plan, delegation record digest | `CHILD_CREATE_INTENT(t)` | — |
| E4 | Helper → sub-helper | Create the leaf cgroup under the boundary (a helper-owned write). Fork a per-child sub-helper outside the coordinator's namespaces. The sub-helper unshares `CLONE_NEWPID` and forks the child init into the leaf (`CLONE_INTO_CGROUP`, K-9). Init unshares `CLONE_NEWNS`, makes mounts private, mounts proc and reports `'H'`. This is the V1 pattern (`native_root_worker_supervisor_v1.c:251-262`, `:336-348`). | — | — |
| E5 | Sub-helper → worker | `HELD_CHILD`: ticket, init pid; descriptors for namespace, pidfd, out, err, credential receiver and stdin writer | `CHILD_HELD(t)` | — |
| E6 | Worker | Record_Launch_Intent, then Record_Running for the child row, with actual unit, cgroup and invocation from `HELD_CHILD` | scoped commits | `Check_V2`: Live classification under `Custody_V2` and `Delegated_Custody` (C2-51) |
| E7 | Worker → sub-helper | `GO_FORK` (`'G'`). Init forks the actor, which measures itself and waits for the commit (the `native_root_worker_supervisor_v1.c:166-227` pattern). | `CHILD_GO_FORK(t)` | — |
| E8 | Actor → worker | Credential frame: uids, gids, capabilities, securebits, no_new_privs, groups | `CHILD_MEASURED(t)` | — |
| E9 | Worker | Build the actor observation and the process and namespace ancestry rosters | — | `Decide` / `Decide_V2` = `Child_Ready_Conjunction` (`core/worldline-resource_child_execution.ads:194-208`): K.Check, `Parent_Holds` (`:127-133`), `Child_Holds` (`:103-126`), `Process_Ancestry`, `Namespace_Ancestry` |
| E10 | Worker → actor | Durable witness, then the commit ACK (the `wait_credential_commit` pattern, `native_root_worker_supervisor_v1.c:93`, `:224`). The actor execs. | `CHILD_READY(t)` | — |
| E11 | Worker | Original stdin and EOF pump (V3 `write_input`, `rw/protected_scoped_supervisor_v3.py:307-359`), exactly once | `ACTOR_STDIN_*` | — |
| E12 | Sub-helper, helper, worker | Init reaps until ECHILD. `CLOSED_CHILD`. Outer wait; raw drains (V-H). Then Record_Terminal and release or charge. The root settles after every child (CD-9). | closure events | `Check_V2` (Reaped) |

The durable records of E1–E12 go to the scoped observation journal under the child reservation, as the V3 helper journals its stdin events (`rw/protected_scoped_supervisor_v3.py:320`, `:341`). They are not custody-journal events.

**Failures:**
- Before E7: the sub-helper kills init on channel loss before GO, as the V1 helper does (`protected-root/native_root_worker_supervisor_v1.c:352-353`). The row has an effect after E6, so it settles by Reaped evidence (`Changed_Row_Allowed`, `core/resource_run_ledger.ads:313-322`).
- After E7 and before E10: the actor never execs. Closure evidence decides.
- After E10: normal closure. An unknown child keeps the root held.

### V-E.2 Retained surfaces

- The actor's ABI, argv, env, stdin and EOF are identical to the V3 actor helper's (C2-51 and C2-56).
- FD inheritance is an explicit roster; every other descriptor is `O_CLOEXEC`.
- The V1 root supervisor, the V3 actor helper, the helper-stdin lineage and their controls stay unchanged. `native_root_worker_supervisor_v2.c` is a separately versioned successor (D-5b).
- The C body is unproved, with cost obligations (OB-048 class).

### V-E.3 Coordinator reachability (every retained capability of the euid-0 coordinator)

| Item | Today (source) | Authority it confers | Needed? | v3 constraint | Native input that governs its use | Evidence item |
|---|---|---|---|---|---|---|
| Startup-lease lock descriptors (`rw/root_worker_custody.py:106-107`) | duplicated OFDs of the store, gate, broker and actuator `flock` locks (`rw/protected_startup.py:359-385`) | exclusive ownership of the store and the authority state | yes (store owner while WORKER_OWNED) | V-H.4 roster evidence. The files they guard are writable only inside the provisioned roster (M-1). | `Legal` (V-F.4 mutation table) | K-6 |
| issuer, universe and custody-journal lock descriptors (`:108-115`) | lock OFDs | exclusivity | yes | V-H.4 roster evidence | `Legal` | K-5, K-6 |
| host procfs dirfd (`:117`) | `O_RDONLY` directory fd | **write-capable child opens (NF-1)** | read only | **M-2**: replaced by a read-only procfs view | — | K-18 |
| worker, helper and namespace pidfds; worker namespace fd (`:118-119`) | pidfds | poll, terminal state, signal | poll yes; signal no | signals only through helper commands; `pidfd_send_signal` excluded by the M-3 seccomp list **[unverified reasoning]** | — | K-21 |
| supervisor channel (`:120`) | SEQPACKET to the helper | helper protocol | yes | the command list below | per command | — |
| original client socket and transferred request sockets (`:149`; V-I) | sockets | respond to clients | yes | only after `REQUEST_INTAKE` | Join (V-I) | K-15 |
| HELD descriptors: out, err, credential receiver, stdin writer (C helper `:247`) | pipes and sockets | the workload's I/O | yes | V-H protocol | — | — |
| Mount view (init: `:257-258`) | the host filesystem view, with a private proc | writes anywhere root DAC allows | no | **M-1**: read-only bind of `/`; writable roster = the descriptor's `provisioned_state` directories and spools; `/sys` and `/sys/fs/cgroup` read-only; `/proc/sys` read-only; empty tmpfs over `/run/systemd` and `/run/dbus` | — | K-10, K-17 |
| systemd and D-Bus control (NF-6) | `systemctl` subprocesses (`rw/protected_scoped_supervisor_v3.py:23-36`, `:298-301`) | change any unit, including its own ceilings | no | **M-4**: manager operations only through helper commands | per command | K-17 |
| Capabilities (full root today; the C helper only measures them, `:178-199`) | full set | everything | partly | **M-3**: bounding set reduced to an enumerated list, each item justified (for example `CAP_SYS_PTRACE` for procfs reads of other uids and for kcmp). Excluded: `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_SYS_MODULE`, `CAP_SYS_RAWIO`, `CAP_SYS_BOOT`, `CAP_MKNOD`, `CAP_SETPCAP`, `CAP_BPF`, `CAP_PERFMON`, `CAP_SYS_RESOURCE`. Also `no_new_privs`, and a seccomp list excluding mount, unshare, setns, kexec, bpf and `pidfd_send_signal`. | measured by the credential frame | K-10, K-20 |

**Helper commands.** Every command is validated structurally by the helper (unit and leaf names under the boundary, an allowlisted verb), journaled, and executed outside the coordinator's namespaces:

| Command | Purpose | Validation by the helper |
|---|---|---|
| `CREATE_CHILD` | E3–E4 | leaf under the boundary; limits within the boundary's remaining ceiling |
| `GO_FORK` | E7 | ticket of a held child |
| `COMMIT` | E10 | ticket of a measured child |
| `OBSERVE_UNIT` | manager `show` for a boundary unit | unit under the boundary |
| `STOP_UNIT` | manager `stop` for a boundary unit | unit under the boundary |
| `RESET_UNIT` | lingering-unit reset (C2-68) | unit under the boundary |
| `SET_ROOT_CEILING` | option F only, if selected (D-4a) | raise or lower exactly by a reservation |

- **M-5.** The original ancestry and containment predicates (`Process_Ancestry`, `Namespace_Ancestry`, `Parent_Supports` with `Cgroup_Inside`, `core/resource_run_ledger.ads:214-222`, `:247-254`) decide every child natively. Their inputs come from helper frames and the read-only procfs view.
- **Non-claims.**
  - A compromised coordinator keeps its legitimate authority over the store and its writable roster.
  - The argument is about not escaping the boundary or its ceilings, and not reaching host authority beyond the roster.
  - The C helper is unproved.
  - Kernel semantics are unmeasured.

---

## V-F. Custody product state, mutation table, DDL and CAS (V2-REQ-F; 04.1, 04.3, 07.1)

### V-F.1 Product state

- **Root (per custody generation g).** `phase` follows the root graph of C2-62. `owner` is one of FRONT, WORKER, COLLECTOR, RECONCILER or NONE. There are closure flags {NS, OUTER, RAW} and an optional `unknown_cause`. Generation g is installation-wide and increments at each handoff. The row records its root operation.
- **Request (g, r).** A sub-generation s, and a phase: QUEUED, TRANSFER_INTENT, INTAKE, ABANDON or RESPONDED.
- **Descriptor (g, d).** A sub-generation s; a phase: FRONT_HELD, STOP_INTENT, FROZEN, OFD_EVIDENCE, INTAKE, ABANDON or RELEASED; and the position P (readers) or W (stdin).
- **Alternative sets:**
  - `ACK(g)` = {CUSTODY_ACK, ABANDON};
  - `REQUEST(g, r, s)` = {REQUEST_INTAKE, REQUEST_ABANDON};
  - `DRAIN(g, d, s)` = {DRAIN_INTAKE, DRAIN_ABANDON}.

  A re-attempt after ABANDON uses sub-generation s+1.

### V-F.2 The O mapping (answers 07.1; R3-2)

O keeps exactly v2's five values (C2-S2). It is read from the broker boundaries in the operation journal row:

| O | Durable evidence |
|---|---|
| NO_EXCHANGE | The operation is not `collapse.commit` or `transaction.commit` (`rw/protected_operations.py:692`) |
| UNDECIDED | An exchange operation with neither `FULL_BROKER_COMMITTED` nor `FULL_BROKER_OWNER_DISPOSITION`, and not in the `unresolved` set. Broker progress is an attribute recorded by the boundaries, not another O value: `STAGING_INTENT` (`rw/canonical_full_broker.py:87`), `PREPARED` (`:115`), `NATIVE` (`:144`), `WORKER_INTENT` (`:154`), `WORKER_RESULT` (`:161`), `CANONICAL_INTENT` (`:165`), `PHYSICAL_RESULT` (`:170`). On restart, an `EFFECT_INTENT` row with `PREPARED` goes to `broker.recover` (`rw/protected_operations.py:369-375`). |
| COMMITTED | `FULL_BROKER_COMMITTED` (`rw/canonical_full_broker.py:173`, `:188`). That includes the K4 owner-effect path, which commits through `broker.recover` (`rw/protected_operations.py:958-959`). Absorbing (CD-1). |
| ABORTED | `FULL_BROKER_OWNER_DISPOSITION` whose native decision is `OWNER_RECORD_ABORT` (`rw/canonical_full_broker.py:192-197`; `rw/protected_operations.py:966-968`) |
| UNKNOWN | An exchange operation in the `unresolved` set after a failed recovery (`rw/protected_operations.py:375-376`), or one quarantined after `FULL_BROKER_PHYSICAL_UNKNOWN_OR_REFUSED` (`rw/canonical_full_broker.py:171`; `rw/protected_operations.py:767-768`), in both cases without an owner disposition |

U is the operation journal state (`rw/protected_operations.py:600-601`). C and P are as in C2-S2.

### V-F.3 Legal product relation

`Legal_Product (O, U, C, P)` holds exactly when CD-1 … CD-9 (C2-S2) and the following hold.

**O × U (complete).** "—" means illegal. This table is the design specification of the O×U part of `Legal_Product`. The native relation decides, and the table is for review.

| O \ U | RESERVED | EFFECT_INTENT | EFFECT_OBSERVED | SETTLED | RELEASED | QUARANTINED | RESOLVED_EFFECT | RESOLVED_NO_EFFECT |
|---|---|---|---|---|---|---|---|---|
| NO_EXCHANGE | legal | legal | legal | legal | legal | legal | legal | legal |
| UNDECIDED | legal | legal | — | — | legal only with no broker progress at or after `WORKER_INTENT` | legal | — (K4 resolution records a disposition first) | — (same) |
| COMMITTED | — | legal (before OBSERVE_EFFECT) | legal | legal | — (CD-1: no authentic no-effect evidence) | legal (CD-2) | legal | — |
| ABORTED | — | — | — | — | — | legal (until K4 completes) | — | legal |
| UNKNOWN | — | legal | — | — | — | legal | — | — |

**C × P (rules).**
- **(r1)** While the root phase is FRONT_*, any P phase is legal for non-root rows. The root row is RESERVED or LAUNCH_INTENT before HELD, and RUNNING from RUNNING onwards.
- **(r2)** While the root is WORKER_OWNED … WORKER_RELINQUISH, the root row is RUNNING or TERMINATING, and child rows follow `Parent_Supports`.
- **(r3)** Before CLOSED_WITNESS, the root row is never RELEASED or CHARGED (INV-C4).
- **(r4)** While the root is UNKNOWN, rows are retained or SETTLEMENT_UNKNOWN, never released.
- **(r5)** Request and descriptor sub-states must be QUEUED or FRONT_HELD unless the root generation's phase is TRANSFER_SENT or later.

### V-F.4 Mutation table: the native gate at every actual mutation

| Mutation | Legal when (product state) | Actor | Native gate |
|---|---|---|---|
| M1 operation journal append | owner of the current phase (CD-6) | front, worker or collector | `Operation_Authority.Decide` (U) |
| M2 scoped ledger commit | as M1 | as M1 | `S.Check` / `S2.Check_V2` |
| M3 store mutation (worlds, PRIME) | FRONT_OWNED, or WORKER_OWNED in its CUSTODY_ACK generation (INV-C3) | front or worker | `Legal` and the operation's native decision |
| M4 custody append | per the C2-62 graph | per row | `Root_Custody_Phase.Legal` |
| M5 client response write | the request's admitting owner, after `REQUEST_INTAKE` when transferred | front or worker | Join (V-I) and `Legal` |
| M6 slot read and spool | descriptor owner: FRONT_HELD (front) or INTAKE (worker) | front or worker | `Legal` (descriptor) |
| M7 stdin write | as M6 | as M6 | `Legal` (descriptor) |
| M8 stop or kill | the front only after `ABANDON(g)`; the collector after CLOSED; never under UNKNOWN | front or collector | `Legal` |
| M9 helper command | the worker while WORKER_OWNED; the front while FRONT_* | worker or front | per command (V-E.3) |
| M10 unit reset | after CLOSED_WITNESS | collector | `Legal` |
| M11 escrow claim | FRONT_RECONSTRUCTION | collector | `Legal` |

### V-F.5 Custody journal v2: complete DDL

```sql
CREATE TABLE genesis (
  name  TEXT PRIMARY KEY CHECK (name = 'owner-genesis'),
  value BLOB NOT NULL,
  mac   TEXT NOT NULL CHECK (length(mac) = 64)
);
CREATE TABLE events (
  seq           INTEGER PRIMARY KEY,
  event_id      TEXT NOT NULL UNIQUE CHECK (length(event_id) = 64),
  previous      TEXT NOT NULL UNIQUE CHECK (length(previous) = 64),
  generation    INTEGER NOT NULL CHECK (generation >= 1),
  operation     TEXT NOT NULL,
  subject_kind  TEXT NOT NULL CHECK (subject_kind IN ('ROOT','REQUEST','DESCRIPTOR')),
  subject       TEXT NOT NULL,
  subgeneration INTEGER NOT NULL CHECK (subgeneration >= 0),
  kind          TEXT NOT NULL CHECK (kind IN (
    'PREPARED','HELD','RUNNING','EXECUTION_NATIVE','EXECUTION_ACK','HANDOFF_INTENT',
    'FRONT_CLOSE_INTENT','FRONT_CLOSED','TRANSFER_SENT','ROSTER_EVIDENCE','CUSTODY_ACK','ABANDON','FRONT_RETAINED_ESCROW',
    'ORIGINAL_PROGRESS','ORIGINAL_RESULT','HANDLER_TERMINAL','WORKER_RELINQUISH',
    'CLOSED_NS','CLOSED_OUTER','CLOSED_RAW','CLOSED_WITNESS','PHYSICAL_SETTLED',
    'HISTORICAL_SETTLEMENT','FRONT_RECONSTRUCTION','UNKNOWN','RECONCILED',
    'REQUEST_QUEUED','REQUEST_TRANSFER_INTENT','REQUEST_INTAKE','REQUEST_ABANDON','REQUEST_RESPONDED',
    'DRAIN_STOP_INTENT','DRAIN_FREEZE','DRAIN_OFD_EVIDENCE','DRAIN_INTAKE','DRAIN_ABANDON','DRAIN_RELEASED')),
  actor         TEXT NOT NULL CHECK (actor IN ('FRONT','WORKER','COLLECTOR','RECONCILER')),
  record        BLOB NOT NULL,
  mac           TEXT NOT NULL CHECK (length(mac) = 64),
  CHECK ((subject_kind = 'ROOT') = (subject = ''))
);
CREATE TABLE alternatives (
  generation      INTEGER NOT NULL,
  operation       TEXT NOT NULL,
  subject_kind    TEXT NOT NULL,
  subject         TEXT NOT NULL,
  subgeneration   INTEGER NOT NULL,
  alternative_set TEXT NOT NULL CHECK (alternative_set IN ('ACK','REQUEST','DRAIN')),
  event_id        TEXT NOT NULL UNIQUE REFERENCES events(event_id),
  PRIMARY KEY (generation, operation, subject_kind, subject, subgeneration, alternative_set)
);
CREATE TABLE root_state (
  generation    INTEGER PRIMARY KEY CHECK (generation >= 1),
  operation     TEXT NOT NULL,
  phase         TEXT NOT NULL,
  owner         TEXT NOT NULL CHECK (owner IN ('FRONT','WORKER','COLLECTOR','RECONCILER','NONE')),
  closure_ns    INTEGER NOT NULL CHECK (closure_ns IN (0,1)),
  closure_outer INTEGER NOT NULL CHECK (closure_outer IN (0,1)),
  closure_raw   INTEGER NOT NULL CHECK (closure_raw IN (0,1)),
  unknown_cause TEXT,
  head_event    TEXT NOT NULL REFERENCES events(event_id)
);
CREATE TABLE subject_state (
  generation    INTEGER NOT NULL REFERENCES root_state(generation),
  subject_kind  TEXT NOT NULL CHECK (subject_kind IN ('REQUEST','DESCRIPTOR')),
  subject       TEXT NOT NULL,
  subgeneration INTEGER NOT NULL CHECK (subgeneration >= 0),
  phase         TEXT NOT NULL,
  position      INTEGER CHECK (position IS NULL OR position >= 0),
  head_event    TEXT NOT NULL REFERENCES events(event_id),
  PRIMARY KEY (generation, subject_kind, subject)
);
CREATE TABLE blobs (
  sha256 TEXT PRIMARY KEY CHECK (length(sha256) = 64),
  kind   TEXT NOT NULL CHECK (kind IN ('RAW_OBSERVATION','SPOOL_CHUNK','CAPTURE')),
  bytes  BLOB NOT NULL
);
CREATE TABLE head (
  name     TEXT PRIMARY KEY CHECK (name = 'current'),
  event_id TEXT NOT NULL REFERENCES events(event_id),
  mac      TEXT NOT NULL CHECK (length(mac) = 64)
);
```

- **Phase sets.** `phase` values are checked natively (`Legal`, on every load and append), not by a CHECK list. The loader's exact `sqlite_master.sql` comparison (V-J.4) fixes the DDL itself.
- **Exclusivity.** The `alternatives` primary key makes CUSTODY_ACK and ABANDON (and each other pair) mutually exclusive per generation, subject and sub-generation, in the database as well as in `Legal`.
- **Genesis.** The genesis row holds the custody genesis v2 bytes and their HMAC-SHA256 under the issuer key (C2-113). When a v1 journal exists, the genesis's `prior_custody` binds its sha256 and final head (V-J.2). Prior history is never replaced.

### V-F.6 CAS and replay semantics

`append (expected, proposed)` runs inside one `BEGIN IMMEDIATE` with `synchronous=FULL`:
1. Load and verify the chain: MAC, previous links, head (`rw/root_worker_journal.py:93-114`).
2. **Replay first.** If an event with the same (generation, operation, subject, sub-generation, kind) and an identical record exists, return it. This is idempotent: no second mutation and no action. It comes before the CAS check, so a caller whose acknowledgement was lost gets its own committed event back, not a stale-state refusal.
3. If the alternative-set slot is held by a different kind, refuse `CUSTODY_ALTERNATIVE_TAKEN`. The loser does not act.
4. Require that the `root_state` and `subject_state` rows equal `expected`: head, generation, root phase, subject phase and sub-generation. Otherwise refuse `CUSTODY_CAS_STALE`. The caller re-reads and re-decides; it never retries the same proposal blindly.
5. Require the native `Legal (state, proposed) = Ready` and compute `Next (state, proposed)` natively.
6. Insert the event, the `alternatives` row (when the kind belongs to a set) and the updated state rows. Update the head.
7. Read back, re-decide natively (`Legal` and `Next` equality), then commit.

The native unit `Worldline.Root_Custody_Phase` provides `State`, `Event`, `Legal`, `Next` and `Mutation_Allowed`, with `Global => null`, `Post => Legal'Result = Legal_Reference (…)` and `Always_Terminates`. It is exported in the C-API successor pattern (V-K).

---

## V-G. Physical collection barrier and crash/recovery product table (V2-REQ-G; 04.4, 04.5, 12.2)

### V-G.1 The typed barrier

`Physical_Closure` is exactly three typed custody events, plus terminal pidfds:
- `CLOSED_NS`: the helper's `CLOSED … ECHILD` frame (`protected-root/native_root_worker_supervisor_v1.c:359`), and the namespace pidfd terminal;
- `CLOSED_OUTER`: the helper pidfd terminal and the unit's inactive state with its main exit, observed through `OBSERVE_UNIT`;
- `CLOSED_RAW`: every owned or transferred output spool at EOF with a complete hash chain;
- plus the worker, helper and namespace pidfds terminal (`rw/root_worker_closed.py:48-50` pattern).

`CLOSED_WITNESS` requires exactly these and nothing else.

`Handler_Terminal` is a separate typed optional input (`Present (event)` or `Absent`), consumed only by the U decision. It is not part of the barrier.

### V-G.2 Collector futures

- There are four independent awaitables: handler terminal, NS closure, outer wait and raw drains.
- The barrier awaits the three physical ones.
- The handler terminal has no ordering constraint.
- **"Missing terminal"** means `Handler_Terminal = Absent` in the state on which `CLOSED_WITNESS` commits.
- Today's sequential awaits (`rw/root_worker_closed.py:126-128`) and the escrow's `handler_terminal` precondition (`:26-29`) are replaced.

### V-G.3 The U decision after CLOSED_WITNESS

- **(a) A retained first `RESULT_CAPTURE`** (operation journal, `rw/protected_operations.py:780-785`) settles automatically by `recover_committed` semantics: exactly one retained capture leads to `finish` (`:812-816`). This is what the original startup recovery does (`:367-368`, NF-4), and it requires no `HANDLER_TERMINAL`. The collector uses the retained first capture, never the worker's later one (fixing `rw/root_worker_closed.py:150-151`).
- **What (a) still requires.** `finish` keeps every native check it has today: `OBSERVE_EFFECT` must return `EFFECT_ACCEPTED` and `SETTLE_USE` must return `SETTLED_NEW` (`rw/protected_operations.py:791-811`). If a native check refuses, the outcome is exactly what the original recovery gives for that refusal. Nothing in (a) widens what settles.
- **(b) No retained capture.** Native `QUARANTINE_USE` (CD-2), then K4.
- **COMMITTED** is absorbing (CD-1), and the first result is write-once (CD-8).

### V-G.4 NEVER_DISPATCHED separated from dispatched/no-HELD

| Launch journal phase (`core/resource_observation_classification.ads:13-14`) | Classification | Decision |
|---|---|---|
| `Never_Dispatched`, no dispatch, no protocol or unit fact | `Never_Launched` (`Never_Holds`, `:96-102`) | `Release_Hold` (`core/resource_run_ledger.ads:319-320`) |
| `Dispatch_Intended`: dispatch journaled, no HELD | `Unknown`: a present `Dispatch` defeats `Never_Holds` (`:97`), and no Live or Reaped rule holds | `Retain_Uncertain`; holds retained; owner or recovery resolution |

### V-G.5 Crash and recovery product table

Rows are grouped by root phase. Every row keeps COMMITTED absorbing, genuine quarantine and K4, and the write-once first result. RT numbers keep v2's identities where they survive.

| Id | Root phase (custody) | Launch journal | U (operation journal) | Physical facts | Native decisions | Action | Automatic or owner |
|---|---|---|---|---|---|---|---|
| PR-a (RT-1) | none or PREPARED | `Never_Dispatched` | RESERVED or EFFECT_INTENT | none | `Never_Launched` → `Release_Hold` | Release P. U follows the original restart path: a RESERVED row, or an EFFECT_INTENT row with neither a retained result nor a broker preparation, is unresolved (`rw/protected_operations.py:376`, `:383-384`) and goes to the owner, with quarantine and K4 as the original does | P automatic; U owner |
| PR-b (RT-2) | PREPARED | `Dispatch_Intended` | EFFECT_INTENT | no HELD | `Unknown` → `Retain_Uncertain` | Holds retained | Retain automatic; resolution by owner or recovery |
| RT-3 | HELD or RUNNING, front alive | `Namespace_Held` | EFFECT_INTENT | live slot | `Live` | Continue | — |
| RT-4 | RUNNING or TERMINATING | — | any | authentic retained CLOSED witness | `Reaped` → `Record_Terminal` → release or charge | Settle P | Automatic |
| RT-5 | RUNNING or TERMINATING | — | any | no slot, no witness | `Unknown` → `Retain_Uncertain` | Retain | Automatic retain |
| RT-6 | — | — | any | row SETTLEMENT_UNKNOWN, later witness | `Reaped` (`core/resource_run_ledger.ads:313-314`) | Settle P | Automatic |
| RT-7′ | WORKER_OWNED … CLOSED_WITNESS; worker dead | — | EFFECT_INTENT **with** a retained first RESULT_CAPTURE | barrier complete | V-G.3 (a): `OBSERVE_EFFECT`, `SETTLE_USE`; **no HANDLER_TERMINAL prerequisite** | Complete | Automatic |
| RT-8 | as RT-7′ | — | EFFECT_INTENT **without** a retained capture | barrier complete | V-G.3 (b): `QUARANTINE_USE` | Quarantine | Owner (K4) |
| RT-9 | TRANSFER_SENT(g), no CUSTODY_ACK; front restarted | — | any | — | `ABANDON(g)` by the Reconciler (CAS) | Collect, then RT-7′ or RT-8 | Automatic |
| RT-10 | CUSTODY_ACK(g); worker alive; front restarted | — | any | worker holds the transferred OFD locks (`rw/protected_startup.py:374-385` `_lock`; `rw/root_worker_journal.py:59-62`) | — | Diagnostic WORKER_OWNED_LIVE. No stop. | Automatic |
| RT-11 | CUSTODY_ACK(g); worker dead | — | any | — | collection (V-G.1) | Settle P; U by RT-7′ or RT-8 | Automatic or owner |
| RT-12 | UNKNOWN | — | any | authentic terminal evidence | Reconciler redecides (`Legal`) | Collect | Automatic |
| RT-13 | UNKNOWN; worker possibly alive | — | any | — | none | Wait; never stop | Automatic retain |
| RT-14 | any | — | any | a journal, key, genesis or head missing or changed | none | Named refusal; no reinitialization | Owner (restore; never a new genesis) |
| RT-15 | — | — | — | bootstrap INTENT without its file | existing refusal (`rw/protected_startup.py:587`) | Diagnostic | Owner |
| RT-16 | any | — | QUARANTINED | — | none | Retained | Owner (K4 through `quarantine.resolve`) |
| RT-17 | any | — | RESOLVED_EFFECT or RESOLVED_NO_EFFECT | — | original `recover_owner_resolution` (`rw/protected_operations.py:363-365`) | Complete | Automatic; unresolved goes to the owner |
| RT-18 | any | — | EFFECT_INTENT with `FULL_BROKER_PREPARED` | — | original `broker.recover` then `finish` (`rw/protected_operations.py:369-375`) | Complete | Automatic; failure is UNKNOWN and goes to the owner |
| RT-19 | descriptor `STOP_INTENT` … `OFD_EVIDENCE` | — | any | — | V-H.3 | Resume or ABANDON | Automatic |
| RT-20 | request `TRANSFER_INTENT` without intake | — | any | — | `REQUEST_ABANDON(r)` | The request stays queued; the front serves it under the original gate once custody returns (V-I.6) | Automatic |

Authentic known outcomes complete automatically (RT-4, RT-6, RT-7′, RT-9, RT-11, RT-12, RT-17, RT-18). Uncertain ones retain their holds, and their use goes to native quarantine or the owner (PR-b, RT-5, RT-8, RT-13). The protected owner route stays available (RT-16).

---

## V-H. Slot and drain transfer, complete (V2-REQ-H; 08.1–08.6, D-3a)

### V-H.1 Descriptor states

FRONT_HELD → STOP_INTENT → FROZEN → (sent) → OFD_EVIDENCE → INTAKE or ABANDON → RELEASED (V-F.1). Every step is a CAS on (g, d, s).

### V-H.2 Steps

1. **H0 STOP_INTENT(d)**, durable and **before any pause.** It records the role and the current spool head.
2. **H1 QUIESCE.**
   - **Output pipes on today's V3 slots,** which use an asyncio `StreamReader` over a dup: `os.fdopen (os.dup (fd))` and `connect_read_pipe` (`rw/protected_scoped_supervisor_v3.py:489-490`).
     1. Call `transport.pause_reading ()` and set the transfer flag.
     2. Call `transport.close ()`. This closes only the dup; the slot's own fd stays open.
     3. The protocol feeds EOF after the bytes already buffered.
     4. The existing consumer reads until `b''` and appends every chunk to the durable spool before anything else (spool-first).
     5. With the transfer flag set, the consumer treats `b''` as the transfer point, not the stream's end.
     6. Bytes the transport has not yet read stay in the kernel pipe, because the slot's own fd is still open. The new owner reads them after position P.

     **[unverified reasoning, RC-1]** for the installed CPython's asyncio.
   - **Successor slots.** These read raw, spool-first: `os.read` on readiness, append and hash-chain, then deliver.
   - **SEQPACKET channel.** Stop polling at a message boundary. There are no partial messages.
   - **stdin writer** (`write_input`, `:307-359`).
     - A stop flag is checked after each `os.write` return and before any await.
     - The written count W is updated immediately after each `os.write` (`:328-329`).
     - So at a stop, W equals exactly the bytes the kernel accepted. Non-blocking pipe writes return their exact count **[unverified reasoning, RC-2]**.
     - No bytes are buffered in user space, because the remaining payload is the retained `payload[W:]`.
3. **H2 FREEZE(d)**, after `fsync` of the spool. It records P (spool length), the spool head, W for stdin, the descriptor identity (dev, ino, mode) and the role.
4. **H3 SEND.** `SCM_RIGHTS` in batches, with a frame of (d, s, P or W, spool head).
5. **H4 VALIDATE.**
   - The worker receives the **whole roster** first and performs no I/O.
   - It checks types and identities, then reports its received fd numbers. It cannot know its own host pid inside its PID namespace.
   - The front derives the worker's host pid from the worker pidfd it holds (fdinfo, read in the host namespace) **[unverified reasoning, K-4]**.
   - The front, which still holds its copy, computes `kcmp (front, worker, KCMP_FILE, fd_f, fd_w)` and journals `DRAIN_OFD_EVIDENCE(d)` **[unverified reasoning, K-5]**.
   - For lock descriptors it also records lock-held evidence: a fresh open with `LOCK_EX | LOCK_NB` fails **[K-6]**.
   - If validation fails, the worker does not intake. It closes its copies unread, and the front CASes `DRAIN_ABANDON(d)` and resumes from P or W.
6. **H5 INTAKE(d).** A CAS that is exclusive with ABANDON (`alternatives` key). It is legal only when `OFD_EVIDENCE(d)` exists and matches the worker's report. **Only after INTAKE commits may the worker read (from P) or write (from W).**
7. **H6 RELEASE(d).** The front reads the durable INTAKE, closes its copy and journals `DRAIN_RELEASED(d)`.

**Stdin EOF.**
- EOF happens when the last write end closes.
- Only the owner that has written `W = len (payload)` journals `STDIN_EOF` and closes.
- If the owner dies with `W < len`, the kernel closes its end. The result is premature EOF, recorded at collection as `STDIN_TRUNCATED`. The actor's outcome is then UNKNOWN, never PASS (OB-020).

### V-H.3 Failure and restart table

| Window | Owner | Action |
|---|---|---|
| Before STOP_INTENT | old | Nothing changes |
| After STOP_INTENT, before FREEZE | old | If the old owner is alive, it resumes reading; nothing has moved. If the front process crashed, bytes that a StreamReader transport had read but its consumer had not yet spooled die with it. They can be neither recovered nor always detected, exactly as for a crash of today's V3 slot. That stream's completeness is then UNKNOWN, and no PASS rests on it. Successor slots (raw, spool-first) close this window. |
| After FREEZE, before SEND | old | `DRAIN_ABANDON(d)`; the old owner resumes from P or W |
| After SEND, before OFD_EVIDENCE | old | Same; the worker's copies are closed unread |
| Validation failure | old | Same |
| After OFD_EVIDENCE, before INTAKE | old, until INTAKE or ABANDON commits | CAS decides. The loser does not act. |
| After INTAKE, before RELEASE | new | The old owner never resumes; it reads the journal |
| After RELEASE | new | — |

There are never two concurrent readers or writers.

### V-H.4 The root handoff's lock roster

- For the root custody transfer, `VALIDATE` records kcmp and lock-held evidence for **every** lock descriptor before `CUSTODY_ACK(g)`: the startup-lease locks (store, gate, broker and actuator locks), `issuer.lock`, `universe.lock` and the custody journal lock (`rw/root_worker_custody.py:106-115`).
- `Legal` requires the complete `ROSTER_EVIDENCE` event.
- Today's fstat-identity checks (`:187-204`) remain additional, not sufficient.
- The real helper, init and outer-wait producers stay the reapers (C2-71).

---

## V-I. Requester correspondence by mode, and the exact gate list (V2-REQ-I; 09.1–09.3, 09.5)

### V-I.1 Original evidence baseline

`RequestPeer` requires the retained descriptor's re-read to equal the initial observation (`rw/client_peer.py:73-90`, `:116-117`, `:134-135`):
- raw `SO_PEERCRED` bytes, including the pid;
- the socket's (dev, ino, mode).

The original has no cookie and no namespace record. The existing relay, `rw/client_peer_relay.py:32-121` (byte-identical to S5's copy), moves a `RequestPeer` to a receiver by the same whole-re-read equality (`:111-112`). That pattern is unchanged for any receiver in the front's namespaces. The worker needs its own exact type only because its PID namespace differs (NF-9).

### V-I.2 Inputs with typed presence (additive SPARK unit `Worldline.Requester_Correspondence`; spec slice S8; DESIGN)

This replaces v2 §8.1's record, whose cookie and namespace fields were unconditional.

```ada
type Mode is (Fresh, Retained, Historical);
type Optional_Record (Present : Boolean := False) is record
   case Present is
      when True  => Value : L.Identity;              -- a raw record span
      when False => Errno : Interfaces.Integer_32;   -- typed absence; 0 when the field does not apply to the mode
   end case;
end record;
type Requester_Crosswalk is record
   Raw_Host_Ucred      : L.Identity;       -- the retained 12-byte "@iII" record (rw/client_peer.py:21, :81); always present
   Raw_Relative_Ucred  : Optional_Record;  -- the worker's re-read; FRESH only
   Front_Reread        : Optional_Record;  -- JF: the front's original observation re-read at transfer; FRESH only
   Host_Socket_Identity, Reader_Socket_Identity : Optional_Record;  -- (dev, ino, mode); FRESH only
   Host_Socket_Cookie, Reader_Socket_Cookie     : Optional_Record;  -- optional corroboration
   Origin_User_Ns, Reader_User_Ns, Origin_Pid_Ns, Reader_Pid_Ns : Optional_Record;  -- optional corroboration
   Pidfd_Record        : Optional_Record;  -- optional; never required
   Custody_Head        : L.Identity;       -- the event that carried the request (J8)
   Which               : Mode;
end record;
```

**Results of `Join`:**
- `Join_Ready`;
- `Ucred_Malformed`;
- `Uid_Gid_Mismatch`;
- `Front_Reread_Mismatch` (JF);
- `Socket_Mismatch` (J4, or both cookies present and unequal);
- `Namespace_Mismatch` (both namespace records present and unequal);
- `Presence_Invalid` (a field present or absent against its mode);
- `Custody_Missing`.

v2's `Socket_Custody_Unestablished` is withdrawn (REQUESTER-PROVIDER). Any result other than `Join_Ready` makes the worker decline intake, and V-I.6 applies.

**Where the native code consumes it:**
1. `Legal` (V-F.4) for `REQUEST_INTAKE(r)` (mode FRESH) and `CUSTODY_ACK(g)` (mode RETAINED). Both require `Join_Ready`.
2. `Root_Admission_V2`. Its `Requester_Uid` and `Requester_Gid` must equal J1's decoded host values. Today Python unpacks them from `rawUcred` (`rw/protected_root_observation.py:35`).

No digest is hidden in an opaque `current_source`.

### V-I.3 Mode predicates

| Conjunct | FRESH | RETAINED | HISTORICAL |
|---|---|---|---|
| J1 decode raw host ucred (retained) | required | required | required |
| J1′ decode the relative ucred, re-read now | required | Absent (typed) | Absent (typed) |
| J2 retained host bytes equal the original document's `rawUcred` | required | required | required |
| JF front re-read at transfer: the original `RequestPeer.observation ()` in the front's own namespace, journaled in `REQUEST_TRANSFER_INTENT` (pid included) | required | — | — |
| J3 relative uid/gid equal host uid/gid | required. The same user namespace holds by construction: the helper uses only `CLONE_NEWPID` and `CLONE_NEWNS` (`protected-root/native_root_worker_supervisor_v1.c:257`, `:336`). Namespace records, if present, must be equal; absence never blocks. | — | — |
| J4 socket identity (dev, ino, mode): the front's journaled value equals the worker's fstat, while the front still holds its copy | required **[unverified reasoning, K-15]** | Absent | Absent |
| J5 cookies | if both Present they must be equal; absence never blocks | Absent | Absent |
| J6 relative pid recorded uninterpreted | yes | — | — |
| J7 pidfd | optional, never required | — | — |
| J8 custody head | the current generation's `REQUEST_INTAKE(r)` | the operation's own intake or `CUSTODY_ACK` | the operation's original capture |

### V-I.4 Explicit joins

- **Request:** the document's `requestId`, `operation` and raw request (`rw/client_peer.py:123-126`).
- **Operation:** the preparation and journal row `capture['request']` (`rw/protected_operations.py:402-403`, `:415`).
- **Transaction:** `preparerPeer` (`rw/client_peer.py:204-220`).
- **Reservation:** `capture['resource_intent'].reservation`.
- **Custody:** generation g and the intake record.
- **Source containers:** the descriptor and genesis through `Roster_Join` (V-C.3).

`Join` checks every one of these equalities natively.

### V-I.5 Exact gate list

Observed: 18 sites in 11 modules (`grep` listing). The original gates stay exactly `type (x) is RequestPeer` in the front. Worker-side handling is by additive successor methods that accept exactly `CrosswalkRequestPeer` with a native `Join_Ready` of the stated mode. No gate accepts both types.

| Gate (source) | Front (unchanged) | Worker successor mode |
|---|---|---|
| `rw/canonical_actor_execution.py:64` before-exec capture | `RequestPeer` | RETAINED for the root's own operation; FRESH for a transferred request |
| `rw/protected_operations.py:401` `resource_request_material` | `RequestPeer` | FRESH (transferred request) |
| `rw/protected_operations.py:414` `_row_for_request` | `RequestPeer` | FRESH, or RETAINED for its own operation |
| `rw/protected_operations.py:686` pre-effect boundary | `RequestPeer` | FRESH |
| `rw/protected_operations.py:728` `_invoke_serial` context | `RequestPeer` | FRESH (worker invoke successor) |
| `rw/protected_owner.py:323` owner peer | `RequestPeer` | FRESH |
| `rw/canonical_owner_witness.py:22` | `RequestPeer` | FRESH |
| `rw/protected_resource_runtime.py:229` `credential_join` | `RequestPeer` | FRESH |
| `rw/protected_resource_runtime.py:387` reserve packet | `RequestPeer` | FRESH |
| `rw/protected_scoped_resource_runtime.py:386` `intent_for_operation` | `RequestPeer` | FRESH |
| `rw/protected_scoped_resource_runtime.py:625` `lifecycle_packet` | `RequestPeer` | RETAINED (settlement uses the original observation) |
| `rw/protected_scoped_resource_runtime.py:702` `launch_reserved` | `RequestPeer` | FRESH |
| `rw/protected_scoped_resource_runtime.py:858` `go_scoped` retained | `RequestPeer` | RETAINED |
| `rw/protected_root_resource.py:33` root launch | `RequestPeer` | front only |
| `rw/protected_root_observation.py:28` `RootControllerCapture` | `RequestPeer` (FRESH) | RETAINED |
| `rw/protected_root_supervisor.py:21` | `RequestPeer` | front only |
| `rw/root_worker_custody.py:97` `CustodyOffer` | `RequestPeer` | front only |
| `rw/protected_root_worker.py:53` `RootWorkerSlot` | `RequestPeer` | front only |

Settlement and K4-history gates (HISTORICAL) accept only the exact type `RetainedRequestObservation`, labelled RETAINED and built from retained bytes, never a fresh-read dictionary. `CrosswalkRequestPeer` is a new exact type, not a subclass of `KernelPeer` or `RequestPeer`. Outside worker custody, no gate admits it.

### V-I.6 Domain-preserving path

When the worker cannot establish a FRESH join for a transferred request — for example, J4's evidence or an optional record is inconsistent — the request is **not refused**:
1. The worker declines intake, and `REQUEST_ABANDON(r)` commits.
2. The request stays QUEUED in the durable queue.
3. The front serves it under the **original** `RequestPeer` gate when custody returns (FRONT_OWNED g+1).

No still-live-client, fresh-pidfd or unavailable-provider condition becomes an acceptance condition. The availability cost is recorded in V-L.5.

### V-I.7 Ordering

1. Receive the full roster: frame, sockets, locks and origins. This fixes the order at `rw/root_worker_custody.py:183-185`, where a `RequestPeer` is built before the roster arrives.
2. Validate every element.
3. `Join`.
4. CAS `REQUEST_INTAKE` or `CUSTODY_ACK`.
5. Only then use any gate.

---

## V-J. Startup union, keysets, DDL and recovery mapping (V2-REQ-J; 12.1, 12.4, D-2a)

### V-J.1 v1, exactly (observed)

- **Top level:** `schema`, `installation_id`, `trees`, `files`, `runtime`, `paths`, `genesis`, `bootstrap_ledger`, `provisioned_state`, `actuator_transactions`, `endpoint`, with `schema = worldline.protected-startup-v1` (`rw/protected_startup.py:173-176`).
- **`endpoint`:** {`path`, `requester_uid`, `requester_gid`} (`:192-197`).
- **`runtime`:** {`interpreter`, `worldline_source`, `gate_source`, `principal_source`, `native_library`, `proof_manifest`, `proof_summary`, `tools`, `shared_objects`} (`:264-266`).
- **`tools`:** a non-empty command → path map, each resolved by `which` (`:285-295`).
- **Source-lease roles:** the executable roles HELPER, ENTRY, INTERPRETER, SOURCE, EXTENSION and CACHE (`:278-280`), and DATA for the descriptor and the startup genesis (`:275-277`).
- **Operation-head creation slot:** exactly `authority_root/authority/issuer/state/worldline-operation-head.sqlite`, listed in `provisioned_state`, absent before creation, created by the ENTRY `protected-canonical/provision_operation_head.py` (`:328-350`).
- **Owner plan v1** (`worldline.protected-root-worker-plan-v1`): exactly {`schema`, `installation`, `startup_descriptor`, `entry`, `early_envelope`, `helper`, `sources`, `worker_policy`, `cost_key`, `native_components`, `handoff_genesis`, `handoff_journal`, `child_dispatch`} (`rw/protected_root_worker.py:98-104`). `entry`, `early_envelope`, `helper` and `handoff_genesis` are absolute and selected in the source lease (`:106-108`). `sources` is non-empty and digest-equal (`:109-114`). The plan path arrives as an argument (NF-10).
- **Custody genesis v1** (`worldline.owner-provisioned-root-custody-v1`): exactly {`schema`, `installation`, `startup_descriptor_sha256`, `owner_plan_sha256`, `issuer_key_sha256`, `initial_event`} (`rw/root_worker_journal.py:43-49`).
- **Custody journal v1:** tables `genesis (name, value)`, `events (event_id, previous, operation, kind, record, mac)` and `head (name, event_id, mac)` (`:16-20`), with the kinds of `:21-23`. Its path must be in `provisioned_state` (`:54-55`), and its lock is the path plus `.lock` (`:38`).
- The schema file `protected-startup/protected-startup-v1.schema.json` lists the same required top-level keys (observed).

### V-J.2 v2, exactly (DESIGN)

v2 §11.1's union table U-1 … U-12 is carried (C2-111). The exact keysets below make U-3, U-5 and U-12 concrete.

- **Startup descriptor v2** (`worldline.protected-startup-v2`, U-3):
  - top level: exactly the eleven v1 keys plus `root_worker`;
  - `root_worker`: exactly {`owner_plan`, `crosswalk`}, both absolute paths;
  - `runtime`: exactly the nine v1 keys plus `resource_scoped_producer`. The draft already reads that key, and requires it to be exactly `<gate root>/authority/resource/run-scoped-config-v1.json` and installed (`rw/protected_scoped_resource_runtime.py:54-56`). Today's v1 keyset (`rw/protected_startup.py:264-266`) cannot carry it;
  - `runtime.tools`: a roster map with v1 semantics (`:285-295`). It must include every command the v2 root route runs by name (U-3: the V3 supervisor helper, `bwrap`, `systemctl` and `systemd-run`, under their installed names);
  - `endpoint` and `paths`: the v1 keysets and checks, unchanged;
  - `provisioned_state`: the v1 required set (`:298-317`) plus the owner plan, the crosswalk, the custody database, its `.lock` and the custody genesis (U-3);
  - `files` must bind the owner plan, the crosswalk, the startup genesis, the owner-plan, crosswalk and custody-genesis schema files (v2 §11.2), and both provisioner entries, with v1's mode and sha256 semantics (`:256-262`). This makes `Installed_Digest` exact (V-C.3). The custody genesis is deliberately absent: it binds the descriptor's own digest (`rw/root_worker_journal.py:47`), so the descriptor cannot bind its digest.
- **Owner plan:** `worldline.protected-root-worker-plan-v1`, keyset and checks unchanged (`rw/protected_root_worker.py:98-114`), with a schema file bound in `files` (v2 §11.2). Its `handoff_journal` and `handoff_genesis` name the custody database and genesis. The custody version is the custody genesis's exact schema.
- **Custody genesis v2** (`worldline.owner-provisioned-root-custody-v2`): the six v1 keys plus `prior_custody`, which is either `null` or exactly {`journal_sha256`, `head_event`} binding a retained v1 journal (C2-113).
- **Crosswalk** (`worldline.protected-root-operation-crosswalk-v1`): V-C.6, read by `exact_json`.
- **Early-envelope DATA** (U-3): the descriptor, the startup genesis, the owner plan, the crosswalk, the run-scoped config, the custody genesis and the header DATA (for example `/usr/include/asm-generic/socket.h`, v2 §11.2). The plan's `entry`, `early_envelope` and `helper` are selected as today (`rw/protected_root_worker.py:106-108`). The provisioners are ENTRY selections, offline only (the `_offline_operation_slot` pattern, `rw/protected_startup.py:340-344`).
- **Selection by exact schema.** A v1 descriptor selects every v1 path, and a v2 descriptor every v2 path, by the exact `schema` value. Nothing defaults between versions (C2-111). The v1 check `schema == worldline.protected-startup-v1` (`:175-176`) stays for v1.
- **Who selects the owner plan.** Under v2, the descriptor's `root_worker.owner_plan`. If the `serve_root_front` argument (NF-10) is kept, it must equal that path.

### V-J.3 Creation slots, exactly

| Slot | Versions | Entry | Rule |
|---|---|---|---|
| Operation head (existing exact path) | v1 and v2 | `protected-canonical/provision_operation_head.py` | Exclusive create. Refuses if present. The slot is in `provisioned_state` (`rw/protected_startup.py:336-339`). |
| Crosswalk file (U-12) | v2 | The crosswalk provisioner, an offline ENTRY | Exclusive create. Refuses if present. |
| Custody v2 database, its `.lock` and the custody genesis (U-5) | v2 | The custody provisioner, an offline ENTRY | Exclusive create of all three. Refuses if any exists. The paths are exactly the plan's `handoff_journal`, that path plus `.lock` (today's lock rule, `rw/root_worker_journal.py:38`) and the plan's `handoff_genesis`. The database is in no source-lease selection (the `rw/protected_startup.py:345-346` pattern). When a v1 journal exists, `prior_custody` binds its sha256 and final head, and existing history is never re-genesised. |

**Order.** The crosswalk is provisioned first. The descriptor is then finalized with the crosswalk's digest in `files`. Custody provisioning comes last, because the custody genesis binds the final descriptor's digest. Every later startup selects the custody genesis as DATA (`rw/root_worker_journal.py:40-41`). Every slot is operator-run (D-2a, OP-1).

### V-J.4 DDL

- Custody journal v2: V-F.5.
- Operation head: `protected-canonical/operation_head_schema.sql`, unchanged.
- At run time each database opens `mode=rw` only. The loader compares the complete `sqlite_master.sql` text, beyond today's table-roster and column (name, type) checks (`rw/root_worker_journal.py:85-92`).

### V-J.5 Every original recovery and owner path, mapped to the product relation

| Original path (`rw/protected_operations.py:355-384`) | Product-relation row |
|---|---|
| A retained preparation without a row → startup refusal for owner diagnosis (`:358`) | Unchanged; owner (RT-14 class) |
| Owner-witness reconciliation before the loop (`:359`) | Unchanged |
| `RESOLVED_EFFECT` or `RESOLVED_NO_EFFECT` → `recover_owner_resolution`; failure → unresolved (`:363-365`) | RT-17 |
| `EFFECT_OBSERVED` or `SETTLED` → `recover_committed` (`:366`) | RT-7′ (U already observed) and RT-4 |
| `EFFECT_INTENT` with `RESULT_CAPTURE` → `recover_committed` (`:367-368`) | RT-7′ |
| `EFFECT_INTENT` with `FULL_BROKER_PREPARED` → `broker.recover`, then `finish`; failure → unresolved (`:369-375`) | RT-18 |
| `EFFECT_INTENT` otherwise → unresolved (`:376`) | RT-8 (owner) |
| `QUARANTINED` with `FULL_BROKER_OWNER_DISPOSITION` → K4 `recover_pending`; failure → unresolved (`:377-382`) | RT-16 and RT-17 |
| `RESERVED`, or `QUARANTINED` without a disposition → unresolved (`:383-384`) | P by PR-a or PR-b from the launch journal; U stays with the owner (RT-16) |
| Owner routes: `owner.retry` (interim named refusal), `owner.adopt`, `owner.recover`, `quarantine.resolve` (the exact exception) | C2-93 routing; the product state decides which owner serves |

### V-J.6 v1 parity and the frontier control

Unchanged: C2-116. No missing prior state is ever initialized, and no chain history is replaced.

---

## V-K. C-API predecessor status and root-worker stages (V2-REQ-K; 11.1, D-7a)

### V-K.1 Predecessor status

- **Sealed CAPI4 review:** ENDORSED_WITH_REQUIRED_CHANGES. V3-RC4 NOT_CLOSED. V3-RC5 and V3-RC6 CLOSED_AT_DESIGN_LEVEL (`CAPI4R/REVIEW.md:3`). The two required changes are carried **OPEN**, verbatim:
  - **V4-RC4-GATE:** "Reconcile normative B0.7, DESIGN 8.4, B4 tiles, B8 gate algorithm, B10 gate rows, B11 promises, mutation specifications and the machine twin. State branch-sensitive payload rules that permit the existing False-variant rejection diagnostic after its discriminant test. State the sole WF-X finalization O assignment exception with exact exclusive assignments before its test. Preserve A1, diagnostics, codes, write order and the accepted domain."
  - **V4-RC4-ALIAS:** "Complete the fully expanded naming invariant for indirect package paths admitted by the scoped inventory, including F.P.Decide and paths through the transport package qualifier. Define deterministic path-aware exclusion or an exact per-call expanded-qualifier invariant, and specify matching indirect-path mutation controls. Do not weaken V7/O6(a) or relax the scoped inventory."
- **CAPI5 (UNREVIEWED)** proposes:
  - R-GATE v5, branch-sensitive (`CAPI5/DESIGN.md:186-190`);
  - R-QUAL, an exact per-call expanded-qualifier invariant (`:173`);
  - R-ALIAS kept as a subset (`:172`);
  - "every stage enforces … R-QUAL …" (`:230`);
  - §19: R-QUAL fails closed on the root-worker draft, and a rebase needs re-observed, reviewed tables (`:332-339`).

  Each use below is **[depends on unreviewed CAPI5]**. If a different repair is accepted, the root-worker stage rules follow the accepted one.
- **Neither lane's acceptance** is decided here.

### V-K.2 The gate chain

G-CAPI → G-CAPI-P → G-PROT → G-RW (explicit in V-M). G-CAPI requires the reviewed C-API successor, including the review closing V4-RC4-GATE and V4-RC4-ALIAS. This is a review dependency, not an operator gate.

### V-K.3 The complete invariant and table set of each root-worker stage

**Floor.** Each root-worker stage RW-k (one packet per export family, appended after the C-API successor's stages) enforces, on the composed text:
- G1–G10;
- K1–K5, and K6 from PK-7;
- P1–P3;
- R-ISO, R-TRANS, R-TILE, R-INV, R-ALIAS;
- R-QUAL **[depends on unreviewed CAPI5]**;
- R-W;
- R-GATE in the form that repairs V4-RC4-GATE **[depends on unreviewed CAPI5]**;
- R-RES, S-RES, R-LAYOUT, R-GLUE;
- D1–D5 when applicable (from PK-6b).

All are as defined in `CAPI4/DESIGN.md:450-490` and its stage rule (`:247`), with CAPI5's replacements as labelled.

**Appended RW tables.** Each is appended, never edits an earlier table, and is re-observed on the rebased base and reviewed:
- `RW_LAYOUT_PACKAGES`, appended at the end of the successor's `CAPI_LAYOUT_PACKAGES` run (in CAPI4 the run ends with `Completion_Transport` and `Finalization_Transport`, and every stage appends at its end: `CAPI4/DESIGN.md:344-345`), still before `package body Authority_Glue is`;
- `RW_LAYOUT_EXPORTS`, appended at the end of the successor's `CAPI_LAYOUT_EXPORTS` run of export bodies, still before the final `end Worldline.C_API;` (`CAPI4/DESIGN.md:356`);
- `RW_SPEC_RUN`, appended after the successor's run of relocated specification declarations, still before the final `end Worldline.C_API;` (`CAPI4/DESIGN.md:337-338`);
- `RW_TILES`;
- `RW_TRANSPORT_HELPERS` (sha256-bound);
- `RW_CLAUSE_TUPLES`, per new scope;
- `RW_GATES` (kind `bool` or `case`);
- `RW_WRITES` (rows appended to the R-W forms);
- `RW_QUALIFIED`, per-scope expanded qualifier multisets of root-worker routine names;
- `RW_EXTERNAL_NAMES`;
- `RW_LIBRARY_INTERFACE` (K3, G9).

### V-K.4 Indirect and transport-qualified aliases

- In new root-worker scopes, every call into a SPARK unit uses its full expanded name.
- No SPARK unit is renamed in a new root-worker scope.
- R-QUAL's per-scope multiset rule is extended to the root-worker routine names: a dotted name whose last selector is a root-worker routine must match `RW_QUALIFIED` exactly. So `F.P.Decide`-style indirect paths, transport-qualified, `C_API`-qualified, parent-shortened, library-unit and `Standard.`-prefixed spellings are refused without resolving them.
- Mutation controls mirror CAPI5's MQ1–MQ14 for the root-worker names **[depends on unreviewed CAPI5]**.

### V-K.5 Write and gate rules

- Each acceptance object in a root-worker transport has an `RW_GATES` row of kind `bool` or `case`.
- `False`-variant (rejection) components are selected only inside the rejection branch.
- `True` components are selected only after the gate.
- `case` components are selected only inside their alternative.
- No acceptance object is assigned, passed whole or renamed. **Root-worker stages introduce no WF-X-style assignment exception.**
- Writes only through listed forms with appended `RW_WRITES` rows.

### V-K.6 Residual, glue, diagnostics and finalization

- Root-worker stages make **no glue edits.** GE1–GE9 are unchanged.
- R-RES, S-RES and R-GLUE identities are preserved through every RW stage.
- Every existing tile is untouched, including G16a's `False`-variant rejection diagnostic and finalization's exclusive WF-X `O` assignments.
- Root-worker exports return exactly the original wire refusal codes for their units.

### V-K.7 Scope of the hygiene rules (CAPI-SCOPE-CONTRADICTION)

- R-RW-2's declaration and renaming ban and IC-3's uniqueness apply **only to the new root-worker scopes.**
- Preserved unchanged:
  - the S5 residual's package-level renamings `Owner_Wire`, `Owner_Kernel`, `Owner_History` (`S5/core/worldline-c_api.adb:879-881`) and `Retry_Wire`, `Retry_Kernel`, `Join_Wire`, `Join_Kernel` (`:1024-1027`) (CAPI4 A-BIND rows 25–27 and 30–33, `CAPI4/APPENDIX-BINDINGS.md:1497-1505`);
  - the per-scope `W` aliases in `Recovery_Authorization_Transport`, `Recovery_Authorization_V3_Transport`, `Recovery_Protocol_Transport`, `Run_Ledger_Transport` and `Chain_Transport`, and finalization's `W renames F.W` (clause tuples CL-T3, CL-T4, CL-T5, CL-T12, CL-T13, CL-T15, `:1529-1541`).
- No old clause is renamed or deleted to make a census pass.

### V-K.8 Rules R-RW-1 … R-RW-10 (v3; replaces v2 §14.3)

- **R-RW-1.** Each root-worker export follows the C-API pattern. It has one transport package appended to `RW_LAYOUT_PACKAGES`, one export body appended to `RW_LAYOUT_EXPORTS` and one spec declaration appended to `RW_SPEC_RUN`. All value logic sits in On units, enrolled by name.
- **R-RW-2.** In new root-worker scopes only: no package renaming of a SPARK unit, and no declarations beyond the transport's tiled content.
- **R-RW-3.** No new identifier is a homograph of a C_API-level declaration (`U8`, `U32`, `I64`, `Size`, layout package names, export names). The draft's `Size` and `Alignment` literals are renamed or moved into an On wire unit.
- **R-RW-4.** Each new export body uses exactly its own transport.
- **R-RW-5.** Every new clause, write, gate and tile is listed in the appended RW tables.
- **R-RW-6.** Writes use listed forms only.
- **R-RW-7.** No `REQUIRED_PROVED` name lies under `Worldline.C_API`.
- **R-RW-8.** S5's On units are taken. L-CAPI-P consolidates the protected lineage's Off files before G-PROT.
- **R-RW-9.** S5's recovery units and the successor's recovery packets are taken (Optional_Marker untouched, G-10).
- **R-RW-10.** Every new On unit is accounted in the core `Library_Interface` (K3, G9), re-observed after the rebase.

### V-K.9 Integration checks IC-1 … IC-12 (replaces v2 §14.5)

| Id | Check | Mutation that must refuse |
|---|---|---|
| IC-1 | The **complete** stage floor of V-K.3 on the composed text, for every stage | A moved export run; a dropped table row |
| IC-2 | Declaration census of new root-worker scopes against C_API-level identifiers | A `Size` literal; a new C_API-level renaming |
| IC-3 | Renaming identifiers unique among **new** root-worker scopes; the S5 residual and CAPI4 tuples unchanged | A new transport declaring `W`; any edit to CL-T3 |
| IC-4 | One transport per new export body | An export using two transports |
| IC-5 | `External_Name` census re-observed: CAPI's final count plus each RW export exactly once | A duplicated symbol |
| IC-6 | No `REQUIRED_PROVED` name under `Worldline.C_API` | An enrolled `Worldline.C_API.X` |
| IC-7 | No `SPARK_Mode => Off` outside `worldline-c_api` | A restored Off unit |
| IC-8 | `Authority_Glue` and GE1–GE9 identical after every RW stage | A changed glue line |
| IC-9 | Optional_Marker files identical to S5's or to the reviewed successor's | The lane's `worldline-recovery.ads` |
| IC-10 | Installed-compiler name resolution, with no warning on any transported clause (CAPI4 D-38) | OPEN: needs the admitted frame |
| IC-11 | Per-call expanded qualifiers of root-worker routines, with indirect and transport-qualified mutation controls **[depends on unreviewed CAPI5]** | `F.P`-style path; `Pending_Transport.X` path |
| IC-12 | Branch-correct `RW_GATES` with exact accepted rejection diagnostics. Positive: a rejection diagnostic inside the rejection branch. Negative: the same selection on the accepted path. **[depends on unreviewed CAPI5]** | A `False` component on the accepted path |

### V-K.10 Ordering

O1 (C2-141's hazards; CAPI4R's "sound conditional order") is kept: the C-API successor on S5, then L-CAPI-P, then G-PROT, then root-worker run-end append stages. Each stage binds its context, span removals, tables and glue exceptions.

---

## V-L. Lock and availability model (V2-REQ-L; 06.4, D-4a)

### V-L.1 Lock inventory

| Lock | Kind | Source | Holders |
|---|---|---|---|
| Router lock | `asyncio.Lock` | `rw/root_worker_endpoint_router.py:18` | the dispatcher (no awaits of collectors, V-L.4) |
| Daemon mutation lock | `asyncio.Lock` | `rw/daemon.py:77`, taken for mutating operations including `status` (`:84`, `:350-357`; NF-3). `list`, `show` and `ping` are not mutating (`:83-86`) and skip it (`:358-359`). | request handlers |
| Operation lock | `asyncio.Lock` | `rw/protected_operations.py:308`, `:717` | `principal.invoke` |
| `Gate.mutex` | `threading.Lock`, non-reentrant | `L/dependency-source/lab/intent_gate.py:371` | protected-lane sections only |
| Producer `order` | `threading.RLock` | `rw/protected_resource_runtime.py:150` | protected-lane sections only |
| `StateStore._lock` | `threading.RLock` | `rw/store.py:243` | protected-lane sections only |
| Custody journal lock | `threading.RLock`, plus SQLite `BEGIN IMMEDIATE` | `rw/root_worker_journal.py:33`, `:129` | protected-lane sections only |
| `flock` OFD locks | kernel | `rw/protected_startup.py:374-385` (store, gate, broker and actuator locks, rostered at `:359-372`); `rw/root_worker_journal.py:59-62` (custody journal) | the owner process (custody) |
| Gate connection slots | `threading.BoundedSemaphore(32)` | `L/dependency-source/lab/intent_gate.py:1159` | the gate's own server |

### V-L.2 Thread placement

- **The protected lane.** One dedicated single-thread executor per principal. Every section that takes `Gate.mutex`, `order`, `store._lock` or the journal locks runs there, never on the loop thread and never on the default executor. Because the Gate serializes these sections anyway, blocked waiters never occupy other workers.
- **The registered-root I/O executor.** Separate, with per-requester fair shares. All I/O on user-registered paths (captures, root-link resolution) runs here **without** holding any lane lock, under per-call deadlines. Results are re-validated inside a lane section. This addresses OB-163.
- **Loop callbacks** (`add_reader`, `add_writer`, done-callbacks) take no lock. They only complete futures.

### V-L.3 Lock order and await rules

- Asyncio locks are acquired in this order: router → daemon mutation → operation. They may be held across awaits.
- Thread locks are acquired in this order: `Gate.mutex` → `order` → `store._lock` → journal and SQLite. They are acquired only inside synchronous lane functions, which contain no await.
- No thread lock is held while an asyncio lock is acquired. This holds by construction.
- SL-0 (C2-132 and v2 §13.1's discipline) is retained: one acquisition per public entry through `_protected_section`, `_locked` variants with a holder marker, and the original non-reentrant Gate unchanged, with no `RLock` substitution.
- N-6's sites are all converted. The two A1-origin files (`rw/protected_resource_runtime.py`, `rw/protected_scoped_resource_service.py`, from `L/secondary-source-union-v1.json`) are changed only under G-A1's separate selection and freeze as well as SL-0's review.

### V-L.4 Router and collector

- The router never awaits a collector under its lock. It consults the durable product state (V-F) and queues or transfers requests (C2-93).
- The collector runs as its own task. It uses the lane for its sections and holds neither `operation_lock` nor the router lock.
- `RootWorkerFront.invoke` refusing while not FRONT_OWNED (`rw/protected_root_worker.py:159`) is replaced by the routing of C2-93.

### V-L.5 Progress table (conditions stated; no unconditional liveness claim)

| Request class | Critical path | Who can block it, and for how long | Under stalled I/O | Under executor occupancy | Refusal? |
|---|---|---|---|---|---|
| `status`, `list`, `show`, `ping` (grant-bearing, AM-9) | per-requester queue → (for `status`, which is mutating, `rw/daemon.py:84`: the daemon mutation lock, `:350-357`) → `operation_lock` through `principal.invoke` for every protected request, mutating or not (`rw/daemon.py:379-384`; `rw/protected_operations.py:716-717`) → lane sections → response | the current request's sections and handler, bounded by their own I/O. A detached root holds no `operation_lock` after its initial result (`rw/protected_root_worker.py:184-190`). | Waits while the store's filesystem stalls. The loop stays responsive and accepts and queues. | The lane is single-threaded by design, and registered-root workers have fair shares. | Never refused for phase or occupancy. UNKNOWN only for genuinely uncertain effects. |
| `job.cancel` | same; transferred to the worker while WORKER_OWNED (C2-93) | same | same | same | same |
| `quarantine.resolve` / K4 | same, with the original exception (C2-93) | same | same | same | same |
| Collector and reconciler | their own task → lane | lane FIFO | waits; holds kept (G-3) | — | — |
| Startup recovery | before serving (C2-113) | — | waits; the daemon still starts in a diagnostic state (OB-202) | — | — |

**The availability cost of V-I.6:** a request that falls back to the front waits until custody returns. That is recorded, never converted into a refusal. Every original floor and control is kept.

### V-L.6 Fairness (OB-186; v2 §9.5's rule, kept)

- Requests are queued per requester host UID, served round-robin across requesters and FIFO within one requester.
- Only original policy inputs are used. There is no new priority class and no depth cap.
- Resource exhaustion of the queue makes the affected requests' outcome UNKNOWN. It is never an accepted refusal.
- The original `operation_lock` is unchanged (`rw/protected_operations.py:308`, `:717`). It serializes handler execution as the original does.

---

## V-M. Dependency graph (replaces v2 §15.2 and §15.4; RC-11 11.1)

**Spec nodes.** Passive lead drafting, each with independent GPT-6.1 review.

| Spec | Content | Depends on |
|---|---|---|
| S0 | SL-0 hygiene and the lock model (V-L): no native spec | — |
| S1 | Scoped canonical operation, V1 and V2 entries (V-A, V-B) | S2, S3, S4 (V2 types) |
| S2 | `Source_Record`, `Source_Json`, `Root_Controller_V2` (V-C) | existing types, `Attest` |
| S3 | `Root_Crosswalk` and `Enforcement_Corresponds` (V-C.6, V-D.3) | S2 |
| S4 | Classification and ledger V2 (C2-51) | S2, S3 |
| S6 | State model and the O mapping (V-F.2, V-F.3); `finish` split; adapters | S1, S9 |
| S7 | Slot and drain transfer (V-H) | S9 |
| S8 | Requester correspondence (V-I) | existing types |
| S9 | Custody product relation (V-F) | S8 |
| S10 | Multiplexing and accounting (V-D.4, C2-93) | S1, S3, S4, S7, S8, S9, and the D-4a selection |
| S11 | Startup union and reconciliation (V-J, V-G.5) | S3, S4, S6, S7, S9 |

The graph is acyclic: S2 → S3 → S4 → S1; S8 → S9 → {S6, S7}; S1 → S6.

**Body and caller nodes.** Each needs its spec, the listed bodies and the listed gates.

| Body | Content | Needs |
|---|---|---|
| B0 | SL-0 source changes | S0; G-A1 for the A1-origin files |
| B9 | Custody bodies, journal v2, provisioner | S9, B0 |
| B-RECV | Full-roster receive, `CrosswalkRequestPeer`, gate successors | S8, B9 |
| B7 | Slot transfer | S7, B9, B-RECV |
| B3 | Crosswalk, pair producers, V2 controller callers | S2, S3, B9 |
| B4 | Delegation bodies, helper successor, dispatcher (V-E) | S4, B3, B6, B7, B9 |
| B1 | Scoped canonical operation bodies and wrappers (V1 and V2), `pre_effect` branch | S1, **S2, S3, S4, B3**, B0 |
| B2b, B2c | Exchange and K4 successors | S1, S4, S6, **B1**, G-A1 |
| B6 | `finish` split, adapters, collector settlement (V-G) | S6, B1, **B2b, B2c**, B9 |
| B10 | Request multiplexing | S10, B1, B3, B4, B7, B9, B-RECV |
| B11 | Startup union and reconciler | S11, B3, B6, B7, B9 |
| B12 | Seal: pins, freeze, enrollment, rosters (C2-12) | all bodies |
| **Exports** of B1, B2b, B2c, B3, B4, B9 and B-RECV | **G-RW** |

**Integration gates.** Precedence is explicit:

| Gate | Condition | Needs |
|---|---|---|
| G-CAPI | The reviewed C-API successor composed, with V4-RC4-GATE/ALIAS closed by review | — |
| G-CAPI-P | L-CAPI-P reviewed and composed | **G-CAPI** |
| G-PROT | L-PROT composed by explicit reviewed import (P1:153) | **G-CAPI-P** |
| G-RW | Root-worker stages rebased by R-RW-1 … R-RW-10; IC-1 … IC-12 pass | **G-PROT** |
| G-A1 | L-A1 selected and frozen separately | — |
| G-DEP | L-DEP selected, reviewed and frozen | — |
| G-REVIEW | Different-author actual gpt-6.1-sol review per slice and for the full lane | every node |

**Runtime gates.** R-PROOF, R-LAB and R-PUB, unchanged in meaning (C2-16).

**What can proceed now.** Passive drafting of S0, S2 and S8, then S3 and S9, then S4, S6 and S7, then S1, S10 and S11. Each is independently reviewed. None needs the lab, root or an operator decision.

---

## V-N. Additive controls added by v3

These join the additive roster (C2-17 with R3-9). Pure value fixtures need no root; lab controls need the operator.

- **V-B** (pure). The qualified refusal vectors and positives of V-B.9. RQ-1 rollover positives and refusals per row of V-B.10. Embedding vectors for the single-frame, multi-frame and saturated constructions, including a zero-length-witness case. L-SAT-1 boundary vectors.
- **V-C** (pure). `Canonical_Json` accepts every container the Python check accepts, and refuses: a duplicate key, an unsorted key, whitespace, a raw non-ASCII byte or a trailing LF in form ASCII, an escaped non-ASCII character in form UTF8. `Path_Value` on nested paths. `Roster_Join` refuses a hash-valid container absent from the roster. A relabelled observed frame is refused. P3: an unmapped image in the lease → positive; a mapped image absent from the lease → refusal; a dev/ino mismatch → refusal.
- **V-D** (lab, operator). Readback of every enforced control. No claim test for protection unless D-4a selects a mechanism.
- **V-E** (lab). The E1–E12 sequence. A crash at each step. A coordinator write attempt outside the roster → EROFS. A systemd/D-Bus reach attempt → absent. A `pidfd_send_signal` attempt → seccomp refusal. Each helper command with an out-of-boundary argument → refused.
- **V-F** (pure). `Legal` and `Next` for every product transition. `ALTERNATIVE_TAKEN` for each exclusive pair. Idempotent replay. `CAS_STALE`. DDL constraint violations rejected.
- **V-G** (lab and pure). RT-7′ without a handler terminal → settled. PR-a versus PR-b. A barrier with each fact missing → no CLOSED_WITNESS.
- **V-H** (lab). Every failure window of V-H.3. Asyncio buffered bytes survive. Stdin stopped mid-pump resumes exactly once with one EOF. Premature EOF → `STDIN_TRUNCATED` → UNKNOWN.
- **V-I** (lab). A FRESH join without cookies → Ready. An unavailable correspondence → served later by the front, never refused. RETAINED and HISTORICAL with sockets Absent → Ready. Every gate in V-I.5 exercised by its mode.
- **V-J** (lab). Every v2 key missing or extra → schema refusal. v1 parity.
- **V-K** (static). IC-1 … IC-12 with their mutations.
- **V-L** (lab). A stalled registered-root path does not block `status` for another requester. Lane FIFO. No callback acquires a lock (static audit).

---

## V-O. Measurement items and installed-runtime checks added by v3

These are reserved to the operator under OP-7 (R3-8). The RC items are ordinary installed-runtime checks by the lead, with no root needed.

| Id | Question | Used in |
|---|---|---|
| K-15 | Socket identity (dev, ino) of a live socket that still has a holder: not reused, and equal across `SCM_RIGHTS` | V-I.3 J4 |
| K-16 | `memory.min`, `memory.low` and `memory.high` semantics and systemd `MemoryMin=`/`MemoryLow=` on the lab kernel | V-D |
| K-17 | Reachability of systemd and D-Bus control from a mount namespace with `/run/systemd` and `/run/dbus` hidden, including abstract sockets | V-E.3 M-1, M-4 |
| K-18 | A read-only host procfs view (bind or `fsmount`) refuses writes. An `O_RDONLY` procfs dirfd permits write-opens of child entries. | V-E.3 M-2; NF-1 |
| K-19 | `/proc/<pid>/map_files` access, and dev/ino agreement between maps and hashed files | V-C.7 |
| K-20 | Capability bounding-set reduction with `no_new_privs`, and the seccomp list, for an euid-0 process | V-E.3 M-3 |
| K-21 | `pidfd_send_signal` refused under the seccomp list | V-E.3 |
| RC-1 | Installed CPython asyncio: `connect_read_pipe` transport close feeds EOF after buffered data; `pause_reading` semantics | V-H.2 H1 |
| RC-2 | Non-blocking pipe `os.write` partial-count semantics on the installed CPython | V-H.2 H1 |
| RC-3 | Default executor and `to_thread` behaviour on the installed CPython (the lane design does not rely on its size) | V-L.2 |
| RC-4 | The installed CPython `json` encoder with `ensure_ascii` False and True: which characters it escapes, the case of `\uXXXX` hex digits, and its surrogate-pair output | V-C.1 |

---

## V-P. Everything that remains OPEN

v2's §18 list is carried whole as C2-18 (with R3-20 … R3-24), as the review's `open_design_obligations` require. The items below are in addition to it.

- **All original obligations.** OB-001 … OB-219 stay OPEN (D2R `review.json` `open_obligations`, 219 entries, all OPEN with no closure credited, observed). Nothing here closes any of them.
- **V2-REQ-A … V2-REQ-L, RQ-1 … RQ-5, and every PARTIALLY_CLOSED clause and ruling** stay OPEN until reviewed, with source, proofs and controls on matching source.
- **V4-RC4-GATE and V4-RC4-ALIAS** stay OPEN (predecessor). CAPI5 is unreviewed.
- **Lemmas:** L-BR-1, L-SAT-1, L-RB-4, CJ-1, PD-1 … PD-5, CV-B′, CV-R, plus every carried lemma (C2-38, C2-310).
- **Residuals R1, R2, R3:** coverage limits, decided by the original unit.
- **Native units, unwritten:**
  - `Source_Json`, `Root_Crosswalk`, `Hmac_Sha256`;
  - `Root_Custody_Phase` (product);
  - `Requester_Correspondence` (modes);
  - the V2 successors;
  - the B2b and B2c successors.
- **Design tables still to be reviewed:** the O×U table and the C×P rules (V-F.3), the mutation table (V-F.4), the crash and recovery table (V-G.5), the failure table (V-H.3) and the gate modes (V-I.5).
- **Schemas and provisioner:** the startup descriptor v2, owner plan v2, custody genesis v2, crosswalk and custody provisioner of V-J. Their provisioning is operator work (OP-1).
- **Number canonicality** in expected containers rests on the Python `exact_json` check alone (V-C.1).
- **Protection mechanisms P-M1, P-M2, P-D1 and option F** await operator selection (D-4a). No completion claim is made.
- **Coordinator confinement M-1 … M-5:** design only; K-17, K-18, K-20, K-21.
- **Measurements and checks:** K-1 … K-21; RC-1 … RC-4.
- **The SL-0 audit:** complete receiver, Gate, thread and callback coverage (V-L), including `run_service` and A1-origin files under G-A1.
- **L-CAPI-P:** not designed.
- **G-PROT:** shared callers and ABI.
- **IC-10:** needs the admitted frame.
- **Proof and runtime:**
  - the admitted strict frame (R-PROOF);
  - the full matching-source campaign: floor 251, the sole boundary, zero unproved, justified and `pragma Assume`;
  - the 52-action roster, the lifetime controls, RQC and every additive control;
  - hosted assurance and publication (R-PUB).
- **Operator:** OP-1 … OP-9; paused frame, capacity and storage gates.
- **Process:** the independent actual gpt-6.1-sol review of this v3, of every slice and of the full lane.

---

## V-Q. Non-claims

- This document reviews, accepts, qualifies, proves and authorizes nothing. Every original Phase One obligation and every lane seam remains OPEN.
- Nothing was compiled, run, imported, proved, tested or measured. Every design is an untested engineering hypothesis.
- Hash and inventory agreement establishes only byte identity. It establishes no authenticity, atomic snapshot, installed state or producer correctness.
- **[unverified reasoning]** and **[depends on unreviewed CAPI5]** statements need the named evidence or review.
- No reserved-capacity, completion, confinement or deadlock-freedom property is claimed.
- The native recognizer of V-C.1 does not establish the canonicality of number lexemes, and the observed-side producers' authenticity is not established natively (V-C.5).
- SIA recall is model-origin recall, not evidence. The lead's STATUS index is not operating-state evidence.
- Author checks are self-checks and do not substitute for the required independent review.
- Nothing here changes any original target, accepted case, deterministic fixture, control, contract, threshold, proof floor or scope. Temporary named refusals keep their obligations OPEN.

---

## Appendix A. JACKAL

No numeral in v3 was derived by arithmetic (§C.4), so no JACKAL call was made. `jackal.json` records this, and the status of v2's J01 … J18 inside carried slices (exact, `formal=false`, lane `rat`, informational about arithmetic only).

## Appendix B. Bound inputs (sha256 observed while drafting v3)

```
db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5  D2/SEAM-DESIGN.md
65a8c73028ad1cb22550bf26ffb3d0027ce125c3ac4b29b64def7765a83415c4  D2/seams.json
1a41b5c5bc0b0fba759ecd66357c401a8b5cdee6c5bf1e3914d6989242f010ac  D2R/REVIEW.md
84c176dfc3f2f49deb2a0967da90179ab1e80681e00fa33203a158066d01b942  D2R/review.json
63a36b12ec283916619a668162129ea4562dc316ec30a0410f45b42d2d124fe4  D2R/checks.json
d40060e5d9cdea0f65c117b95a1048570a3e3d18c6ce002efa8d1d8a2198c32b  D2R/review-freeze.json
3d1ef7f82c2458f24ef9a8916e82db0d97c3e1730038cf20ac3d5e0e0323e4aa  CAPI4R/REVIEW.md
d7bf825a6c3d0da5f1b9302b64991d05759ae4754eb7347dcf187eb89b2e1f4e  CAPI4R/review.json
d70fe4677ae2159ad617a0dc6f9982fc976fd86b7d43f66dc9a3913e51e96963  CAPI4R/checks.json
f1dcb0a77264dedd4c08be8b71ce390db66295cb25d1eb79eeb3701c7c0413dc  CAPI4R/review-freeze.json
533f0e043fb991d015bcf16494674d791b6f8f8bd5049fef5a8e60594c9341de  CAPI5/DESIGN.md
fe664cc888e348292b6e3cd28c37f89a6e4dfb7ea2e843f94253595dda4a7561  D2/jackal.json
782379cd1944dc03e59ec7f50eb4aae70bfbdf69c164e9167817b80883652990  D2/AUTHOR-NOTES.md
531d11282f811518b868470c0012f23a5e34bdbe3891ef39194cd8f230933f46  D1/SEAM-DESIGN.md   (v1; D1 = WT/designs/claude-root-worker-seam-design-v1)
a9b5dcce5ca5808f8049ae8e7020a79c3fbfc33cc4dcbcc3706fd8f4f40fbfd6  CAPI4/DESIGN.md
39ca995998d68b57d13c02796ee30d8826eecc07e750abf95a83f7d348f7d626  CAPI4/APPENDIX-BINDINGS.md
2f3a0b4b3bb2a0996824859c2d9f8a59e7c58f624b2d81cb00e40e76bf588237  P1/HANDOFF.md
1587e068fc2c31a562e38b459728a75dbf7e8d7d9f8afb8efa1474e2a702aeec  P1/OBLIGATIONS-v2.json
0a17c0efb95904ee865182a20d3bcabceeef93b1cc3639687aab27696339f35b  S5/core/worldline-c_api.adb
74d3f2f95a830738fcfdb741494d0b9ee1f021e63d150bcb77d51a7cf56e14d5  L/dependency-source/lab/intent_gate.py
a87f12865e30789d850cff3a25c69f3ea1793f8dae47404b82acb751efb3a6f9  L/secondary-source-union-v1.json
d25a94919a8bed008d007273ab6a887159bd1dd367d71e9a428f2e5bbd96f5ef  R/core/resource_scoped_run_ledger.ads
65a38d24f3c5444bd21bc15ecf8dee6ec9e2e93a71ba911f6678ca9b4797562d  R/core/resource_run_ledger.ads
23c43aaaad873052b8e2e192a4c33a46b1d08f7b427f11f7b27f10602553c07f  R/core/resource_observation_classification.ads
ea4397f3b8b1e4561603253dddcc5f9515116f4096d35b8ead50fbfe70470e0d  R/core/resource_quantities.ads
570a1cd5fc4ffb20cef000eb669cf0c15105e8a7e70f737c2933c8c2fd676c20  R/core/resource_reservation_transition.ads
fe3fd5583b5aa91ac902bc969c389ede02962976103118ed7c85e8f09d958b66  R/core/worldline-operation_authority.ads
c0c62623152021d578cd65b96efce18a0cc7805e5c4b25fdde923c949db193d7  R/core/worldline-operation_authority.adb
5aafbe6337572c6be44801900387cde2be776b0cdf55775ef09331f48dfd0ba9  R/core/worldline-resource_child_execution.ads
c5821527426f828807ed4eff37bc0be31df0b4cb8159e8c91fa4734410fe5f9c  R/core/worldline-canonical_operation.adb
a83c7dfc92c8314fb371fad3b4a56c47fae2c96a330b9233c4211cc75351e600  R/core/worldline-canonical_exchange.ads
f3300f5408493b100157dd286d80dd818cf2abd2479f26bad5b26e903a635b79  R/core/worldline-canonical_owner_completion.ads
f2a321d07e667e80f4359634e8e4a956b555368b8d449e8c8c930b8f511aeff7  R/protected-root/native_root_worker_supervisor_v1.c
56a3643486fb9ca3eaef735c0af6a210128f47267d6af5c226015146be62d211  R/protected-startup/protected-startup-v1.schema.json
ea1a01df19ddef2418d4e4ec14dab6cea1eaa70423172eedea36a48ec383f0cb  rw/protected_operations.py
15cbbfcd61a98da55a704af16fd5d853a3af64bc0aba84599d936440ba8f74a1  rw/protected_root_worker.py
2510f8edac3937509d36bc3b38511af89f81ecf9a5eff77fefc87f927f3aa811  rw/root_worker_journal.py
25f38ae7c1b63f14329400155562c18e459b80f46797851ef81d82db03172169  rw/root_worker_custody.py
68740eda2668faddfe28bd3a8ac1720adac3de32f0bc68d8d95e45f94170d07b  rw/root_worker_closed.py
1022187a02c19fb25ecfcafcc9a43a91e5ab62cf243ae38014c14d4c73463ade  rw/client_peer.py
52276d2f7e8f76362e4e97e2dd64ff51f2e5198f57969542bf85e9f50c9ef1f4  rw/client_peer_relay.py
acf5ac0fb4035d53c3e053e7a3a10b4f29fd29d5bc0aefbdb0d9de181665080f  rw/protected_scoped_resource_runtime.py
8d03960180e599f192d997a4b3809dc0f4e1a7624f9d4581a6b8a51fcae107ed  rw/protected_scoped_supervisor_v3.py
e29a14a63d67fa3228ede57f0ad12aaa55cbf7c7cf61a8bc09971d5731680ca6  rw/protected_startup.py
9d448dcc8741b698750147a8a0ccb9aaaf0215cba6a16c702facde394b6b52e4  rw/daemon.py
774e35565b93aef70420183a591ceb3acf9ddc9148c0b4ae55fb83bb9efc83ce  rw/root_worker_endpoint_router.py
5ec258a2cbb06a8dbcc5ab02e214d111ff2845b26c19a456c5ba360cf7ea231d  rw/canonical_full_broker.py
f3cda07cf0556a515c9b41663d16a8a8f34bb3e4c27ed584869791628a8e4778  rw/protected_root_observation.py
7e7eaed2b8ebf191a89224d26daa69f69a6ef130f5008088b64cd377a76d9ecb  rw/root_worker_process_capture.py
d80f79bcedace5364d2e9a238ab05b48250660d86cfb4c14aa5393f4b37952af  rw/canonical.py
fc6f00f698160f1a854ef7ae72c425f3c7ed11243809b6dac1a5132c0e2ad33f  rw/protected_resource_runtime.py
fe8dc07d25d5da50d8678e644c1e19c076226774436abb56079aff3b02039e91  rw/store.py
a0781e70e8a4b2b630f6956d0c89208140edc871c4a2a003666573767a32d13d  rw/admission.py
64a0163f2938b0cd4858a3b133af3614a3f2dc39bdbb16016dccca650d54c00b  rw/config.py
100d635842c0df20b1a98921fbfcebc94f2ba862abc0b02a10d1792359c286b0  rw/protected_root_endpoint.py
e062ff0335d312366c90517cca21c73c0879d0b95de469840c36cea46250248f  rw/protected_scoped_resource_service.py
f1089a091399dd0c1a0602aebb027edff4737fbf562750e95e3a0c561067f723  rw/protected_root_resource.py
0fc7f5fde1357f1a97da2ce1977c60290cb15bb4e4e5b77205b4e678f6a5f482  rw/operation_authority_kernel.py
7c089300563f417c2467cb9c327202323071664762fa4c8c1df2d575915e3939  rw/canonical_actor_execution.py
17664c88daa5e8d707e3309ecfa01f1db75fa30090597662d6aa23b3d57589bd  rw/protected_owner.py
4a8c71fa4617b09af2aab8724375c09fabfb2acb5c1676e10f6690b7153270d9  rw/canonical_owner_witness.py
37b58317dac57e21888a01c7b1254d20ec94e85cefe094e68df40fa4c5771d43  rw/protected_root_supervisor.py
```

These identities are byte identities at the time of reading. They establish no authenticity, installed state or atomic snapshot.

## Appendix C. Slice verification

A read-only Python script read the v2 bytes and v3's own text. It printed its results to standard output and wrote no file. It checked (observed):
- v2 `SEAM-DESIGN.md`: sha256 `db512ddb…e1b5`, 2296 lines, ending with a newline;
- every row of the §B.1 table: the sha256 of the stated v2 lines equals the stated hash (all rows matched);
- every R3 replacement: the quoted "v2:" text equals the stated v2 line or lines exactly (all matched);
- transitively, every v1 slice that v2's Appendix C (C2-APC) binds, against v1 `SEAM-DESIGN.md` (sha256 `531d1128…3f46`, 1329 lines): all matched.

The script's final run is recorded in AUTHOR-NOTES §5.

## Appendix D. Companion file identities

Observed with `sha256sum` and `wc -c` after the files were written. This file cannot contain its own hash; `seams.json` records it.

| File | sha256 | Bytes |
|---|---|---|
| `jackal.json` | `8cce45e34f12d9d7976cb9b04ab6ac47e3a99ae8cacc22708a84abe06ec0c024` | 3736 |
| `AUTHOR-NOTES.md` | `dd382e1b0f74e825735e168ab6856b1c85e93f9a39312f3bc15019faf390a0ea` | 12856 |
| `seams.json` | recorded in the handback (it binds this file's hash) | — |
