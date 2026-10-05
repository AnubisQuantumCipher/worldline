# WORLDLINE Phase One root-worker SEAM DESIGN v2 — independent review

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.** This endorses the additive design direction subject to the required repairs below. It is not permission to implement the conflicting statements unchanged. No source, proof, Phase One, integration, execution, publication or deployment acceptance is granted. Every original Phase One obligation remains **OPEN**, with its original dependencies, owners and evidence requirements.

Reviewer: actual model selection **gpt-6.1-sol**, independent and different from the author. Author: **Claude Code lead claude-opus-5-5 (drafting subagent)**. The reviewer authored none of the material under review and wrote only these review artifacts/checkpoints. This review decides the Claude design, not the draft lane's acceptance.

Evidence is passive text/AST/hash inspection and conditional source reasoning. No WORLDLINE/COSMOGONY/root-worker module was imported or executed. No compiler, prover, test, service, namespace, sudo, storage operation, SIA note or process interruption was used. No live lab/store/socket/window or installed-kernel behavior was inspected. Documentation and hashes are not authenticity, confinement, runtime or proof evidence.

## Evidence identity and notation

Line references use these absolute aliases. `D:n` means the line in SEAM-DESIGN.md; `R/...:n` and the other directory aliases name exact files. `AUTHOR-NOTES.md` and `seams.json` are in D's directory. `rw/` is R/runtime/worldline.

- **D**: `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v2/SEAM-DESIGN.md`
- **V1**: `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1`
- **CAPI4**: `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v4`
- **L**: `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/protected-original-root-worker-repair-v1`
- **R**: `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/protected-original-root-worker-repair-v1/source`
- **S5**: `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-composition-v5-beta/source`
- **P1**: `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/outputs/claude-phase1-handoff-20261004`
- **A1**: `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/scoped-committed-envelope-repair-v2-retry1`
- **PROMPT**: `/home/sicarii/Documents/complete-phase1-prompt.txt`
- **SPARK-UG**: `/home/sicarii/.agents/skills/spark-users-guide`
- **ADA-ADV**: `/home/sicarii/.agents/skills/advanced-ada`

All four supplied design identities match. All Appendix B input hashes and all Appendix C carried v1 slice hashes were independently recomputed and matched. The complete path/digest/range results are in checks.json, not merely a selected subset. The bound v1 and C-API v4 review seals and their report/JSON/check files match their declared hashes, sizes and modes. Evidence: D:2122-2250; checks.json:input_audit.

| Design input | Computed SHA-256 |
|---|---|
| SEAM-DESIGN.md | `db512ddb0bc24c1282c45ebbdb035842234a833046b46b702d020cf14027e1b5` |
| seams.json | `65a8c73028ad1cb22550bf26ffb3d0027ce125c3ac4b29b64def7765a83415c4` |
| jackal.json | `fe664cc888e348292b6e3cd28c37f89a6e4dfb7ea2e843f94253595dda4a7561` |
| AUTHOR-NOTES.md | `782379cd1944dc03e59ec7f50eb4aae70bfbdf69c164e9167817b80883652990` |

The carried slices were checked byte-for-byte as line ranges including line endings against the bound v1 whole-file identity. R-1..R-4 were read as explicit replacements, not silently applied to the v1 source: conditional deadlock at D:2252-2258; distinct C-API/A1 lineage at D:2261-2266; only the named pair equalities vacuous at D:2269-2274; conditional requester mismatch with unmeasured kernel semantics at D:2277-2284. R-2's 'unreviewed' C-API wording is now historical: the supplied sealed C-API v4 review exists and is ENDORSED_WITH_REQUIRED_CHANGES, with V4-RC4-GATE and V4-RC4-ALIAS still required (CAPI4/review/gpt61-v1/REVIEW.md:3,54-60).

All observed AST/file counts are source observations. Derived arithmetic was replayed through JACKAL MCP sequentially or in modest groups; the full responses and evaluator identity are retained in checks.json. Each result has status **exact**, lane `rat`, `formal=false`, assurance `exact rational arithmetic (not yet checker-covered)`. No tool returned a consequence ceiling; this review uses the arithmetic only informationally about the supplied numerals. It does not certify source counts, author process counts or program correctness.

| JACKAL call | parsed= | status | exact result |
|---|---|---|---|
| J01 | `parsed=535-419` | exact | 116 |
| J02 | `parsed=614-419` | exact | 195 |
| J03 | `parsed=485-419` | exact | 66 |
| J04 | `parsed=614-485` | exact | 129 |
| J05 | `parsed=66+129` | exact | 195 |
| J06 | `parsed=2+30+9` | exact | 41 |
| J07 | `parsed=2284-1166+1` | exact | 1119 |
| J08 | `parsed=1160+6+1119` | exact | 2285 |
| J09 | `parsed=56596-56543` | exact | 53 |
| J10 | `parsed=34-31` | exact | 3 |
| J11 | `parsed=1165-1160` | exact | 5 |
| J12 | `parsed=6-1` | exact | 5 |
| J13 | `parsed=129-8` | exact | 121 |
| J14 | `parsed=613-606+1` | exact | 8 |
| J15 | `parsed=275-244+1` | exact | 32 |
| J16 | `parsed=1+1+1+1+1+1` | exact | 6 |
| J17 | `parsed=1+1+1+2+1+1` | exact | 7 |
| J18 | `parsed=1+1+1+1` | exact | 4 |

JACKAL non_claims, verbatim:

- NOT formal-bounded: this lane carries no Lean-checked certificate
- The epistemic class above is the STRONGEST claim this result supports
- exact rational arithmetic (not yet checker-covered)

J16-J18 establish only the sums of the supplied terms. They do not establish how many commands or redirects the author performed. Historical machine-memory notes were used for routing only; current conclusions come from the bound files.

## 1. RC clauses and rulings

`CLOSED_AT_DESIGN_LEVEL` means the design supplies the requested specification/direction, with subsequent original proof/source/runtime duties still OPEN. `PARTIALLY_CLOSED` means a substantive response exists but a concrete design gap remains. No original Phase One closure credit follows from either label.

| RC | Design closure | Remaining gap |
|---|---|---|
| RC-01 | PARTIALLY_CLOSED | Typed Reference/Decide/Post and decision subtype supplied; §3 still uses original Facts/Native_Valid, not the delegated V2 classifier. Shared production arena and identity decision mapping supplied; Rebase/Emb is not total while G3 remains uncovered. Field-level embedding supplied; multi-frame construction and saturated arenas are deferred. Coverage lemmas supplied, but raw-domain-only exclusions cannot discharge the original full-domain target; blanket multi-frame/multi-bucket refusal controls contradict the unrestricted scoped domain. Fresh/retained/historical separated; blanket pre-effect FRESH placement and RQ-1 are not established by the launch guard. |
| RC-02 | PARTIALLY_CLOSED | CCE and per-pair producers supplied; P3 remains undefined, and framed Raw-as-subspan of unchanged JSON containers is not specified coherently. Native distinct domains proposed; expected anchors must join the authenticated roster and each claimed raw grammar. Distinct labels/hash-valid containers alone do not establish distinct authentic sources. Crosswalk covers operation/owner/follow-up dimensions in prose; exact schema, native decode, selected-plan joins and complete costs are pending. E1-E4 cover original fields/floors. E3's sampled admission/ledger subtraction does not demonstrate reserved future capacity; memory_high is not a minimum/low guarantee. |
| RC-03 | PARTIALLY_CLOSED | Concrete P-CE1-P-CE4 mechanisms/observations supplied; helper ordering requires Child_Ready before creation of its measured child. Exact protocol and OS/runtime evidence remain open. Original predicates/cases retained by rule; compatibility only covers distinct-pair inputs and S1/B2 consumers still use the old classifier. End-to-end original-domain preservation is not yet designed completely. |
| RC-04 | PARTIALLY_CLOSED | Native append legality mandatory, but complete Legal table and correspondence at each actual state mutation are pending. Head/phase/generation CAS transaction supplied; operation phase and parallel request/drain sub-state need separate retained native state. UNIQUE(operation,generation,kind) does not itself enforce exclusive alternatives or represent repeated sub-generations. Seed/read-only capture, lost-ACK handling and escrow reuse supplied; selected crash table contradicts RT-2 for dispatch without HELD and omits complete crash/replay state. Physical independence intended; §6.7 ambiguously says three awaits while enumerating handler, combined closure/wait, drains, then says physical three. Missing-terminal barrier needs an exact field/future definition. |
| RC-05 | CLOSED_AT_DESIGN_LEVEL | No remaining design-level clause gap; all original evidence obligations remain OPEN. |
| RC-06 | PARTIALLY_CLOSED | AM-1-AM-9 and concrete A/B/C/E failures supplied; no accounting option meets the full target. Phase/owner/recovery table supplied with exact quarantine.resolve exception; UNKNOWN and collecting progress still depend on incomplete custody/reconciliation design. to_thread and fair queue preserve loop responsiveness in intent, but shared gate/operation lock and bounded executor saturation can still block response progress; no full liveness argument supplied. |
| RC-07 | PARTIALLY_CLOSED | O/U/C/P and couplings supplied; exact broker-state mapping/legal product table deferred. |
| RC-08 | PARTIALLY_CLOSED | T1-T5 supplied, but stopping before durable FREEZE conflicts with failure table's claim that reader never stopped. Buffers/in-flight bytes intended to spool; interrupted write/cancellation and already buffered stdin output need exact quiescence rules. Durable P/W and spool head supplied; FREEZE/SPOOL crash and write-progress linearization incomplete. Durable intake/abandon acknowledgement supplied; new owner starts I/O before OFD evidence is recorded. Ownership table excludes pre-commit stop/spool failure and post-intake failed validation. kcmp and lock evidence correctly replace fstat-only proof, but validate before role use and record full-root lock roster evidence, not only descriptor release. |
| RC-09 | PARTIALLY_CLOSED | Native raw credential/socket/ns inputs supplied; request/operation/transaction/container joins and mode-specific presence need complete predicates. Journaled host records/full roster first supplied; cookie unavailable yields non-ready intake despite original domain, and validation/ownership ordering remains incomplete. Retained exact type supplied; per-gate list deferred and J1/J3/J4 unconditional fields conflict with socket-free J8 modes. No pidfd/live-client condition, but FRESH introduces mandatory cookies. No new accepted-case refusal may be approved on provider absence. |
| RC-10 | CLOSED_AT_DESIGN_LEVEL | No remaining design-level clause gap; all original evidence obligations remain OPEN. |
| RC-11 | PARTIALLY_CLOSED | Spec/body graph is acyclic as declared; B1 omits consumed crosswalk/V2 inputs, B2b/B2c and B6 integration edges need explicit reconciliation, and gate precedence is not encoded in body Needs. |
| RC-12 | PARTIALLY_CLOSED | U-1-U-12 union supplied; exact descriptor/schema keysets, provisioner DDL and every early selection remain future spec deliverables. RT table automatic known-outcome direction supplied; RT-7 requires HANDLER_TERMINAL, leaving authentic retained result without that frame unclassified; pre-launch table contradicts RT-2. Original K4/quarantine.resolve retained; exact recovery progress through UNKNOWN/locks depends on complete product/native relation. |

Each original required-change target is retained, followed by every clause as decomposed in v2 §A.1/seams.json. The original sealed v1 requirement governs if a summary differs.

### RC-01 — PARTIALLY_CLOSED

Original target: Define the scoped canonical spec, complete arena/span/decision mapping, structural embedding and non-circular coherent witness relation; prove original accepted/refusal coverage later. Correct the rounding claim and distinguish fresh reservation from retained rollover/lifecycle cases. Evidence: V1/review/gpt61-v1/review.json:2183.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 01.1 | Define the scoped canonical spec | PARTIALLY_CLOSED | Typed Reference/Decide/Post and decision subtype supplied; §3 still uses original Facts/Native_Valid, not the delegated V2 classifier. Evidence: D:431-485; D:820-845; R/core/resource_scoped_run_ledger.ads:232-268. |
| 01.2 | complete arena/span/decision mapping | PARTIALLY_CLOSED | Shared production arena and identity decision mapping supplied; Rebase/Emb is not total while G3 remains uncovered. Evidence: D:518-556; D:601. |
| 01.3 | structural embedding | PARTIALLY_CLOSED | Field-level embedding supplied; multi-frame construction and saturated arenas are deferred. Evidence: D:529-556; D:599-601. |
| 01.4 | non-circular coherent witness relation | CLOSED_AT_DESIGN_LEVEL | Coherent W1-W10 does not presuppose equal decisions; producer coverage remains an independent obligation. Evidence: D:558-611. |
| 01.5 | prove original accepted/refusal coverage later | PARTIALLY_CLOSED | Coverage lemmas supplied, but raw-domain-only exclusions cannot discharge the original full-domain target; blanket multi-frame/multi-bucket refusal controls contradict the unrestricted scoped domain. Evidence: D:589-604; D:642-654; P1/HANDOFF.md:27-29,125-131. |
| 01.6 | Correct the rounding claim | CLOSED_AT_DESIGN_LEVEL | Rounding withdrawn; exact divisible projection and raw Amount versus L.Amount distinguished. Evidence: D:507-516; R/core/resource_scoped_run_ledger.ads:149-152,210-211. |
| 01.7 | distinguish fresh reservation from retained rollover/lifecycle cases | PARTIALLY_CLOSED | Fresh/retained/historical separated; blanket pre-effect FRESH placement and RQ-1 are not established by the launch guard. Evidence: D:487-505,629-640,667; R/core/resource_scoped_run_ledger.ads:436-438. |

### RC-02 — PARTIALLY_CLOSED

Original target: Specify canonical comparable source records and native enforcement of distinct authenticated source domains for every RootController pair; define full dynamic plan/cost and real enforced capacity correspondence. Evidence: V1/review/gpt61-v1/review.json:2195.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 02.1 | Specify canonical comparable source records | PARTIALLY_CLOSED | CCE and per-pair producers supplied; P3 remains undefined, and framed Raw-as-subspan of unchanged JSON containers is not specified coherently. Evidence: D:686-710,718-724,802. |
| 02.2 | native enforcement of distinct authenticated source domains for every RootController pair | PARTIALLY_CLOSED | Native distinct domains proposed; expected anchors must join the authenticated roster and each claimed raw grammar. Distinct labels/hash-valid containers alone do not establish distinct authentic sources. Evidence: D:692-710,737-741. |
| 02.3 | define full dynamic plan/cost ... correspondence | PARTIALLY_CLOSED | Crosswalk covers operation/owner/follow-up dimensions in prose; exact schema, native decode, selected-plan joins and complete costs are pending. Evidence: D:743-763,2001-2004. |
| 02.4 | real enforced capacity correspondence | PARTIALLY_CLOSED | E1-E4 cover original fields/floors. E3's sampled admission/ledger subtraction does not demonstrate reserved future capacity; memory_high is not a minimum/low guarantee. Evidence: D:765-778; R/runtime/worldline/protected_scoped_resource_runtime.py:673-696; P1/HANDOFF.md:125-131. |

### RC-03 — PARTIALLY_CLOSED

Original target: Replace the Delegate=yes-only proposal with a separately reviewed additive native delegation/custody model and actual enforcement/provenance design; preserve the old no-delegation model, Parent_Supports, Original_Holds and every original child case. Evidence: V1/review/gpt61-v1/review.json:2207.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 03.1 | Replace the Delegate=yes-only proposal with a separately reviewed additive native delegation/custody model | CLOSED_AT_DESIGN_LEVEL | Separately reviewed additive classifier/scoped/child successor and no-delegation branch replace the Python Delegate-only change. Evidence: D:818-859. |
| 03.2 | actual enforcement/provenance design | PARTIALLY_CLOSED | Concrete P-CE1-P-CE4 mechanisms/observations supplied; helper ordering requires Child_Ready before creation of its measured child. Exact protocol and OS/runtime evidence remain open. Evidence: D:866-896,913-919; R/core/worldline-resource_child_execution.ads:203-208. |
| 03.3 | preserve the old no-delegation model, Parent_Supports, Original_Holds and every original child case | PARTIALLY_CLOSED | Original predicates/cases retained by rule; compatibility only covers distinct-pair inputs and S1/B2 consumers still use the old classifier. End-to-end original-domain preservation is not yet designed completely. Evidence: D:845-859; D:445-450,467,640. |

### RC-04 — PARTIALLY_CLOSED

Original target: Make native custody legality mandatory; define an exclusive CUSTODY_ACK/ABANDON graph, complete durable CAS generations and crash/ACK/seed/reconstruction rules, independent physical collection and lossless acyclic retention. Evidence: V1/review/gpt61-v1/review.json:2217.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 04.1 | Make native custody legality mandatory | PARTIALLY_CLOSED | Native append legality mandatory, but complete Legal table and correspondence at each actual state mutation are pending. Evidence: D:962-967,1004-1009,2011-2015. |
| 04.2 | exclusive CUSTODY_ACK/ABANDON graph | CLOSED_AT_DESIGN_LEVEL | ACK/ABANDON branches explicitly exclusive and ABANDON cannot reach WORKER_OWNED. Evidence: D:972-988,1004-1008. |
| 04.3 | complete durable CAS generations | PARTIALLY_CLOSED | Head/phase/generation CAS transaction supplied; operation phase and parallel request/drain sub-state need separate retained native state. UNIQUE(operation,generation,kind) does not itself enforce exclusive alternatives or represent repeated sub-generations. Evidence: D:965-967,990-992,1015-1021,1092-1097. |
| 04.4 | crash/ACK/seed/reconstruction rules | PARTIALLY_CLOSED | Seed/read-only capture, lost-ACK handling and escrow reuse supplied; selected crash table contradicts RT-2 for dispatch without HELD and omits complete crash/replay state. Evidence: D:1032-1053,1078,1090-1100; D:1562. |
| 04.5 | independent physical collection | PARTIALLY_CLOSED | Physical independence intended; §6.7 ambiguously says three awaits while enumerating handler, combined closure/wait, drains, then says physical three. Missing-terminal barrier needs an exact field/future definition. Evidence: D:1055-1059,995-998,1466-1468. |
| 04.6 | lossless acyclic retention | CLOSED_AT_DESIGN_LEVEL | Defined snapshot exclusion and raw-only content addressing remove recursive retention; size/OOM/native costs explicitly unclaimed. Evidence: D:1061-1067. |

### RC-05 — CLOSED_AT_DESIGN_LEVEL

Original target: Retain every original required control and roster, including the unchanged v1 frontier control on its exact version/domain; add v2 controls. Remove lead-only retirement authority and expose any concrete re-enrollment proposal for explicit applicable adjudication. Evidence: V1/review/gpt61-v1/review.json:2228.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 05.1 | Retain every original required control and roster | CLOSED_AT_DESIGN_LEVEL | All ordered ordinary/lifetime/protected/lane rosters retained on matching candidate. Evidence: D:1965-1988; P1/HANDOFF.md:162. |
| 05.2 | including the unchanged v1 frontier control on its exact version/domain | CLOSED_AT_DESIGN_LEVEL | Exact v1 frontier bytes/version/domain and refusal retained. Evidence: D:1580-1587; R/protected-startup/controls/test_protected_startup_v1.py:97-105. |
| 05.3 | add v2 controls | CLOSED_AT_DESIGN_LEVEL | Separate additive v2 roster proposed; no replacement. Evidence: D:1977-1988. |
| 05.4 | Remove lead-only retirement authority | CLOSED_AT_DESIGN_LEVEL | Lead-only retirement expressly withdrawn. Evidence: D:1588. |
| 05.5 | expose any concrete re-enrollment proposal for explicit applicable adjudication | CLOSED_AT_DESIGN_LEVEL | No re-enrollment proposed; any future package retains originals and reserved adjudication/review. Evidence: D:1589-1598. |

### RC-06 — PARTIALLY_CLOSED

Original target: Leave in-coordinator option A unselected until a full-domain accounting design covers independent grants/owners/kinds/costs/rollovers and requests larger than the first root hold; specify actual owner/recovery authority in every phase and availability beyond router-lock changes. Evidence: V1/review/gpt61-v1/review.json:2240.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 06.1 | Leave in-coordinator option A unselected | CLOSED_AT_DESIGN_LEVEL | Option A and all other options remain unselected. Evidence: D:1348-1363. |
| 06.2 | until a full-domain accounting design covers independent grants/owners/kinds/costs/rollovers and requests larger than the first root hold | PARTIALLY_CLOSED | AM-1-AM-9 and concrete A/B/C/E failures supplied; no accounting option meets the full target. Evidence: D:1325-1363,2026-2028. |
| 06.3 | specify actual owner/recovery authority in every phase | PARTIALLY_CLOSED | Phase/owner/recovery table supplied with exact quarantine.resolve exception; UNKNOWN and collecting progress still depend on incomplete custody/reconciliation design. Evidence: D:1365-1385; D:1555-1578. |
| 06.4 | availability beyond router-lock changes | PARTIALLY_CLOSED | to_thread and fair queue preserve loop responsiveness in intent, but shared gate/operation lock and bounded executor saturation can still block response progress; no full liveness argument supplied. Evidence: D:1396-1408,1433; R/runtime/worldline/protected_operations.py:717,728-768. |

### RC-07 — PARTIALLY_CLOSED

Original target: Separate canonical committed outcome, native use quarantine, custody and physical resource states. Preserve native QUARANTINE_USE/K4 recovery and NEVER_LAUNCHED held-capacity release, terminal replay and serial semantics; keep write-once original result plus additive reports. Evidence: V1/review/gpt61-v1/review.json:2252.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 07.1 | Separate canonical committed outcome, native use quarantine, custody and physical resource states | PARTIALLY_CLOSED | O/U/C/P and couplings supplied; exact broker-state mapping/legal product table deferred. Evidence: D:367-423,2011-2014. |
| 07.2 | Preserve native QUARANTINE_USE/K4 recovery | CLOSED_AT_DESIGN_LEVEL | COMMITTED absorbing, genuine native quarantine and original K4 exits retained. Evidence: D:384-390,1457-1462. |
| 07.3 | NEVER_LAUNCHED held-capacity release | CLOSED_AT_DESIGN_LEVEL | Original Never_Launched held-capacity release included. Evidence: D:393-398,1453; R/core/resource_run_ledger.ads:317-320. |
| 07.4 | terminal replay and serial semantics | CLOSED_AT_DESIGN_LEVEL | Serial order and SETTLED replay explicitly retained; later matching-source demonstration required. Evidence: D:1447-1455,1494. |
| 07.5 | keep write-once original result plus additive reports | CLOSED_AT_DESIGN_LEVEL | First RESULT_CAPTURE immutable, later report captures additive, collector uses first. Evidence: D:405,1450,1464-1468. |

### RC-08 — PARTIALLY_CLOSED

Original target: Define full slot/drain transfer barriers, buffered/in-flight bytes, durable positions, acknowledgments, failure ownership, OFD/lock custody and genuine helper/outer-wait producer retention or relay. Evidence: V1/review/gpt61-v1/review.json:2263.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 08.1 | Define full slot/drain transfer barriers | PARTIALLY_CLOSED | T1-T5 supplied, but stopping before durable FREEZE conflicts with failure table's claim that reader never stopped. Evidence: D:1157-1169. |
| 08.2 | buffered/in-flight bytes | PARTIALLY_CLOSED | Buffers/in-flight bytes intended to spool; interrupted write/cancellation and already buffered stdin output need exact quiescence rules. Evidence: D:1157-1160. |
| 08.3 | durable positions | PARTIALLY_CLOSED | Durable P/W and spool head supplied; FREEZE/SPOOL crash and write-progress linearization incomplete. Evidence: D:1157-1158,1167-1169. |
| 08.4 | acknowledgments | PARTIALLY_CLOSED | Durable intake/abandon acknowledgement supplied; new owner starts I/O before OFD evidence is recorded. Evidence: D:1160-1161. |
| 08.5 | failure ownership | PARTIALLY_CLOSED | Ownership table excludes pre-commit stop/spool failure and post-intake failed validation. Evidence: D:1165-1176. |
| 08.6 | OFD/lock custody | PARTIALLY_CLOSED | kcmp and lock evidence correctly replace fstat-only proof, but validate before role use and record full-root lock roster evidence, not only descriptor release. Evidence: D:1160-1176; D:1041. |
| 08.7 | genuine helper/outer-wait producer retention or relay | CLOSED_AT_DESIGN_LEVEL | Helper/init/systemd retained as reapers; only observation/reader/writer roles transfer. Evidence: D:1143-1151. |

### RC-09 — PARTIALLY_CLOSED

Original target: Define explicit native requester correspondence and authenticated socket/host-record custody. Label retained observations separately from fresh reads; preserve exited/delegated/same-UID-new-process and full UID/GID domains without a new live-client or fresh-pidfd acceptance precondition. Evidence: V1/review/gpt61-v1/review.json:2275.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 09.1 | Define explicit native requester correspondence | PARTIALLY_CLOSED | Native raw credential/socket/ns inputs supplied; request/operation/transaction/container joins and mode-specific presence need complete predicates. Evidence: D:1220-1247,1389-1393. |
| 09.2 | authenticated socket/host-record custody | PARTIALLY_CLOSED | Journaled host records/full roster first supplied; cookie unavailable yields non-ready intake despite original domain, and validation/ownership ordering remains incomplete. Evidence: D:1238,1246,1251-1259. |
| 09.3 | Label retained observations separately from fresh reads | PARTIALLY_CLOSED | Retained exact type supplied; per-gate list deferred and J1/J3/J4 unconditional fields conflict with socket-free J8 modes. Evidence: D:1233-1243,1260-1272,2023. |
| 09.4 | preserve exited/delegated/same-UID-new-process and full UID/GID domains | CLOSED_AT_DESIGN_LEVEL | Full UID/GID and exited/delegated/same-UID process/preparer cases explicitly retained. Evidence: D:1274-1285. |
| 09.5 | without a new live-client or fresh-pidfd acceptance precondition | PARTIALLY_CLOSED | No pidfd/live-client condition, but FRESH introduces mandatory cookies. No new accepted-case refusal may be approved on provider absence. Evidence: D:1238-1240,1282-1285; P1/HANDOFF.md:137. |

### RC-10 — CLOSED_AT_DESIGN_LEVEL

Original target: Use reviewed appended effective pin overrides plus an external exact inventory/freeze for the manifest itself and all source/control/project/header/helper/dependency files; enroll every new native semantic unit and retain the full original strict scope. Evidence: V1/review/gpt61-v1/review.json:2286.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 10.1 | Use reviewed appended effective pin overrides | CLOSED_AT_DESIGN_LEVEL | Append-only reviewed final-source effective overrides. Evidence: D:1629-1636. |
| 10.2 | plus an external exact inventory/freeze for the manifest itself and all source/control/project/header/helper/dependency files | CLOSED_AT_DESIGN_LEVEL | External exact inventory includes manifest/control/project/header/helper/dependencies and binds to independent freeze. Evidence: D:1638-1650. |
| 10.3 | enroll every new native semantic unit | CLOSED_AT_DESIGN_LEVEL | New semantic/wire units enrolled; impossible draft Off-body names explicitly transferred to reviewed On carriers, not given proof credit. Evidence: D:1652-1668. |
| 10.4 | retain the full original strict scope | CLOSED_AT_DESIGN_LEVEL | S5 original prefix, strict command/floor/boundary and zero unproved/justified/Assume retained. Evidence: D:334-342,1670-1679,1693-1697; P1/HANDOFF.md:158-161. |

### RC-11 — PARTIALLY_CLOSED

Original target: Repair the spec/body/integration dependency DAG; bind reviewed C-API and scoped committed-envelope lineages separately. Correct operator-item scope for protected runtime versus pure value work and draft publication; retain Optional_Marker and paused frame/capacity/storage gates. Evidence: V1/review/gpt61-v1/review.json:2299.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 11.1 | Repair the spec/body/integration dependency DAG | PARTIALLY_CLOSED | Spec/body graph is acyclic as declared; B1 omits consumed crosswalk/V2 inputs, B2b/B2c and B6 integration edges need explicit reconciliation, and gate precedence is not encoded in body Needs. Evidence: D:629-640,1499,1855-1896. |
| 11.2 | bind reviewed C-API and scoped committed-envelope lineages separately | CLOSED_AT_DESIGN_LEVEL | L-CAPI/L-A1 separately bound; L-CAPI-P newly identified and explicitly open. Evidence: D:1836-1849,1890-1894. |
| 11.3 | Correct operator-item scope for protected runtime versus pure value work and draft publication | CLOSED_AT_DESIGN_LEVEL | Pure-value work/draft publication separated from reserved privileged decisions. Evidence: D:1926-1940. |
| 11.4 | retain Optional_Marker and paused frame/capacity/storage gates | CLOSED_AT_DESIGN_LEVEL | No Optional_Marker alteration or infrastructure-resume authority from this lane; approval reconciliation remains outside acceptance. Evidence: D:357-363,1799-1801,1939-1940. |

### RC-12 — PARTIALLY_CLOSED

Original target: Complete startup version/loader/schema/creation-slot correspondence and a native full-ledger reconciliation table that automatically completes authentic known outcomes, retains all uncertain holds and preserves the protected owner route without initializing absent prior state. Evidence: V1/review/gpt61-v1/review.json:2311.

| Clause | Required content | Closure | Assessment and file:line evidence |
|---|---|---|---|
| 12.1 | Complete startup version/loader/schema/creation-slot correspondence | PARTIALLY_CLOSED | U-1-U-12 union supplied; exact descriptor/schema keysets, provisioner DDL and every early selection remain future spec deliverables. Evidence: D:1509-1547,2033-2034. |
| 12.2 | a native full-ledger reconciliation table that automatically completes authentic known outcomes | PARTIALLY_CLOSED | RT table automatic known-outcome direction supplied; RT-7 requires HANDLER_TERMINAL, leaving authentic retained result without that frame unclassified; pre-launch table contradicts RT-2. Evidence: D:1078,1555-1578; R/runtime/worldline/protected_operations.py:812-827. |
| 12.3 | retains all uncertain holds | CLOSED_AT_DESIGN_LEVEL | UNKNOWN retains holds and native uncertainty; no EOF/deadline settlement. Evidence: D:1562-1568,1573. |
| 12.4 | preserves the protected owner route | PARTIALLY_CLOSED | Original K4/quarantine.resolve retained; exact recovery progress through UNKNOWN/locks depends on complete product/native relation. Evidence: D:1383,1576-1578. |
| 12.5 | without initializing absent prior state | CLOSED_AT_DESIGN_LEVEL | No missing-state initialization; one-shot offline operator provisioning. Evidence: D:1538-1553,1574-1575. |

### Rulings and preserved ownership

The sealed v1 rulings, owners and evidence_required strings are copied verbatim into review.json. This table gives their current design closure and remaining gap. The evidence requirements below remain cumulative with the required repairs; none is dropped or converted into a new operator approval gate.

| Ruling | Closure | Preserved owner | Remaining gap and evidence |
|---|---|---|---|
| D-1a | PARTIALLY_CLOSED | Lead source designer; independent GPT-6.1 source/spec reviewer | Typed V2 integration, total arena/multi-frame coverage and all extra-conjunct/caller correspondence remain incomplete. Evidence: V1/review/gpt61-v1/review.json:2318; D:445-450,467,518-611,818-859. |
| D-1b | PARTIALLY_CLOSED | Lead scoped model/caller designer; independent GPT-6.1 reviewer | RQ-1 needs full per-command/per-caller placement, not a blanket inference from current-context launch guards. Evidence: V1/review/gpt61-v1/review.json:2324; D:487-505,667; R/core/resource_scoped_run_ledger.ads:436-441. |
| D-2a | PARTIALLY_CLOSED | Lead authors schema/callers; operator provisions or installs authoritative state | Exact version union, all schema keysets/provisioner DDL and full reconciliation remain incomplete; installation reservation preserved. Evidence: V1/review/gpt61-v1/review.json:2330; D:1509-1578,1926. |
| D-2b | CLOSED_AT_DESIGN_LEVEL | Lead prepares concrete equivalence/adoption package; applicable operator authority; independent GPT-6.1 review | No remaining design-level control-retirement gap: original v1 frontier remains byte/version/domain exact; no re-enrollment proposed. Runtime/proof original obligations remain OPEN. Evidence: V1/review/gpt61-v1/review.json:2336; D:1580-1598,1927; R/protected-startup/controls/test_protected_startup_v1.py:97-105. |
| D-3a | PARTIALLY_CLOSED | Lead protocol designer; operator for lab execution | Stop/freeze/spool crash and OFD-validation-before-use barriers remain incomplete; all slot/reaper roles are retained in intent. Evidence: V1/review/gpt61-v1/review.json:2342; D:1130-1189. |
| D-4a | PARTIALLY_CLOSED | Lead prepares native accounting comparison; independent GPT-6.1 review; operator selects any authoritative resource-policy change | No option selected; no full original-domain accounting/cost/enforcement or protected-response liveness argument. Operator policy selection is preserved. Evidence: V1/review/gpt61-v1/review.json:2348; D:765-778,1325-1408,1928. |
| D-5a | PARTIALLY_CLOSED | Lead prepares native/OS design; independent GPT-6.1 review; operator for delegation and privileged lab action | Additive model supplied, but old-classifier consumers, exact coordinator authority reachability and future-capacity correspondence remain incomplete. Evidence: V1/review/gpt61-v1/review.json:2354; D:818-877,1929; R/core/resource_observation_classification.ads:95. |
| D-5b | PARTIALLY_CLOSED | Lead helper designer; independent GPT-6.1 review; operator for privileged execution/installation | Separate helper successor is sound direction; create/measure/decide ordering and exact protocol surfaces still require a single complete design. Evidence: V1/review/gpt61-v1/review.json:2360; D:881-925,1930. |
| D-6a | PARTIALLY_CLOSED | Lead historical/canonical model designer; independent GPT-6.1 review | Orthogonal directions preserve COMMITTED/quarantine/never-launched/result immutability; product relation and automatic missing-terminal known-result recovery still incomplete. Evidence: V1/review/gpt61-v1/review.json:2366; D:367-423,1447-1478,1561-1578; R/runtime/worldline/protected_operations.py:812-816. |
| D-7a | PARTIALLY_CLOSED | Lead native/provenance designer; child-authority and GPT-6.1 re-review; operator for any original API/owner-policy alteration | Native pair relation is a useful successor, but container/anchor authentication/extraction and P3/crosswalk coverage are incomplete. Original API/owner-policy reservation is preserved. Evidence: V1/review/gpt61-v1/review.json:2372; D:692-763,1931. |
| D-8a | PARTIALLY_CLOSED | Lead OS/native requester designer; independent GPT-6.1 review | Complete request/transaction/custody joins, mode-specific predicates and exact gate list remain missing. Evidence: V1/review/gpt61-v1/review.json:2378; D:1220-1272,2023. |
| D-8b | PARTIALLY_CLOSED | Lead prepares domain-preserving protocol; operator for kernel measurement; independent GPT-6.1 review | No live-client/pidfd requirement is added; mandatory FRESH cookies still need accepted-profile coverage or a domain-preserving design. Measurements remain reserved. Evidence: V1/review/gpt61-v1/review.json:2384; D:1238-1241,1274-1285,1932. |
| D-9a | PARTIALLY_CLOSED | Lead additive SPARK relation and caller designer; independent GPT-6.1 review; operator for fault campaign | Mandatory Legal/exclusive branches/CAS are good direction; product state/schema, all actual mutation gates and complete crash/physical-barrier evidence remain incomplete. Evidence: V1/review/gpt61-v1/review.json:2390; D:965-1100,1933. |

| Ruling | Original evidence_required, preserved verbatim |
|---|---|
| D-1a | Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls. |
| D-1b | Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof. |
| D-2a | Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls. |
| D-2b | Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit. |
| D-3a | Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection. |
| D-4a | Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls. |
| D-5a | Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls. |
| D-5b | Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations. |
| D-6a | Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement. |
| D-7a | Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation. |
| D-8a | Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage. |
| D-8b | Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client. |
| D-9a | Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes. |

## 2. Draft defects and new observations

These findings are about the selected unused source. Static reachability is conditional on earlier startup/precondition checks passing; no hang, prover refusal or kernel behavior was reproduced.

| Defect | Assessment | Details and file:line evidence |
|---|---|---|
| DF-1 | VERIFIED_STATIC_RECOMPUTATION | All effective lane pins recomputed with a reviewer transcription of the read normalizer. Sole mismatch is protected_operations, with exactly the supplied stale/computed digests. Protected startup/intake require no contract_problems. Evidence: R/runtime/worldline/proof_manifest.py:420-450,1012; R/runtime/worldline/protected_startup.py:683-684; R/runtime/worldline/protected_root_worker.py:355-357. |
| DF-2 | VERIFIED_STATIC | Definitions at 52 and 961 shadow; latter loses exact early-selected producer check. No call in selected lane/runtime dependencies; defect predates lane delta. Evidence: R/runtime/worldline/protected_scoped_resource_runtime.py:52-58,961-964; D:117. |
| DF-3 | VERIFIED_STATIC | Root invoke omits genuine context/unresolved/workload guard order and DISPATCH_INTENT relative to serial path. Restore exact original exception order and quarantine semantics. Evidence: R/runtime/worldline/protected_root_worker.py:158-171; R/runtime/worldline/protected_operations.py:728-749. |
| DF-4 | VERIFIED_STATIC | Named six controller expected/observed pairs self-fill; process source lease is passed caller material. Only named equalities are vacuous; non-pair predicates retained. Evidence: R/runtime/worldline/protected_root_observation.py:36-49,74-76,121; R/core/worldline-resource_child_execution.ads:48-59. |
| DF-5 | VERIFIED_STATIC_ABSENCE_IN_SELECTED_TREES | Historical settlement/lifecycle/owner adapters referenced through getattr but have no definitions in read selected runtime/dependency trees. Static absence claim limited to selected source. Evidence: R/runtime/worldline/protected_scoped_resource_runtime.py:530-531,548-549,571-572; R/runtime/worldline/protected_operations.py:505-585,852-897. |
| DF-6 | SUPPORTED_STATIC_CONDITIONAL | Same object's non-reentrant threading.Lock nested at intent_for_operation -> reconcile_context, conditional on passing earlier checks. N-6 widens the required audit; no observed hang. Evidence: L/dependency-source/lab/intent_gate.py:371; R/runtime/worldline/protected_scoped_resource_runtime.py:357,385-388; R/runtime/worldline/protected_operations.py:640. |

DF-1's expected normalized protected_operations pin is `8be1f9ab2c689ecc9e915464e8e454863c205ca2f1f4a1763a5125aa2b61139e`; the reviewer transcription of the read normalizer computes `2a6d71c7ca81d456d41f242a880b8fa3e0f115d794f4772e115767236b183547`. Effective dict/update order was read through AST, not executed. All other effective lane pins matched in this inspection (checks.json:static_observations.pins/pin_mismatches; R/runtime/worldline/proof_manifest.py:420-450,1012).

| Observation | Assessment | Details and file:line evidence |
|---|---|---|
| N-1 | VERIFIED_STATIC | AST literal roster observations match: lane 614, preimage 485, S5/commonV4 535, shared prefix 419, S5/lane set differences 116/195, preimage-only 66. The common names preserve order. S5 remains the integrated original prefix. Evidence: D:127,1670-1679; R/runtime/worldline/proof_manifest.py:25,312,314,974,1031; S5/runtime/worldline/proof_manifest.py:25. |
| N-2 | SUPPORTED_STATIC_TOOL_BEHAVIOR_OPEN | Eight enrolled names at zero-based positions 606-613 are in C_API's Off body, including nested Child_Boundary with no On aspect. Missing required-name logic is at manifest:857-859. Static boundary incompatibility is supported; no GNATprove result was produced. Evidence: R/core/worldline-c_api.adb:31,1166-1198,2251-2254; R/core/worldline-c_api.ads:6; R/runtime/worldline/proof_manifest.py:857-859,1031; SPARK-UG/chapters/ch04-identifying-spark-code.md:19,35-36,76-78. |
| N-3 | VERIFIED_STATIC | Off-file census and S5 comparison support all classes: sole C_API spec/body, S5's On component files, and protected-only Off files. These are existing open body obligations, not authorized exemptions. Evidence: D:129,1799; P1/HANDOFF.md:29,161; R/core/worldline-canonical_operation_c_api.ads:2; R/core/worldline-canonical_operation_c_api.adb:3; S5/core/resource_run_ledger_c_api.ads:4. |
| N-4 | VERIFIED_BYTE_DIFF_AND_LAYOUT | Pure insertion diffs, anchors, specs and External_Name counts match. Old child block cannot be carried verbatim into C-API v4's exact runs/residual. Evidence: D:130,1758-1765; R/core/worldline-c_api.adb:1165-1166,2284-2285; R/core/worldline-c_api.ads:242-275; CAPI4/DESIGN.md:330-355,768-781. |
| N-5 | VERIFIED_LEXICAL_SCOPE | All named renamings are within package body Child_Boundary. They are not C_API body-level declarations. Rebase scope-merging remains a hazard; no current same-scope collision is asserted. Evidence: R/core/worldline-c_api.adb:1198-1220,2251; CAPI4/DESIGN.md:775-780. |
| N-6 | SUPPORTED_STATIC_CONDITIONAL_RECEIVER_RESOLVED | All listed same-thread re-acquisitions are supported at their receivers; service and principal share the exact Gate by constructor identity. Base/service files are byte-identical to A1-selected origins. Fixing only intent_for_operation nesting leaves reserve submit/recover, launch/admission/GO/settlement/reconcile/capture blocked when reached. Not reproduced; other paths and cross-thread lock freedom remain open. Evidence: R/runtime/worldline/protected_scoped_resource_runtime.py:62-75,357,373,385-388,412-436,507-516,526-556,567-596,612-613,630-642,701-769,854-930; R/runtime/worldline/protected_scoped_resource_service.py:62-66,213,223; R/runtime/worldline/protected_resource_runtime.py:149-150,404,474,534-595,604-624; R/runtime/worldline/protected_root_observation.py:57-61; R/runtime/worldline/canonical_actor_execution.py:61; L/dependency-source/lab/intent_gate.py:371; L/secondary-source-union-v1.json:407-431. |
| N-7 | VERIFIED_STATIC | append serializes BEGIN IMMEDIATE and derives previous head itself; signature has no expected head/phase/generation and native Legal is absent. Evidence: R/runtime/worldline/root_worker_journal.py:123-140. |
| N-8 | VERIFIED_STATIC_ORDER | capture_execution appends ACTOR_EXECUTION_NATIVE inside an ACK; _current calls it. The seed-before-second-capture order supports a conditional stale-seed risk once earlier blockers are repaired. Evidence: R/runtime/worldline/canonical_actor_execution.py:125-127; R/runtime/worldline/protected_root_observation.py:61; R/runtime/worldline/root_worker_custody.py:124-142. |
| N-9 | VERIFIED_TEXT_SCOPE_RESOLUTION_OPEN | Child block counts match 84 non-attribute Size tokens and 67 Size attributes. Same-spelled literals versus spec subtype are real textual declarations; installed overload/hiding/warning behavior is unmeasured. Rename/move rule is conservative and sound. Evidence: R/core/worldline-c_api.adb:1285-1300; CAPI4/DESIGN.md:334; D:1794; ADA-ADV/chapters/ch14-packages.md:34-36. |
| N-10 | VERIFIED_STATIC_PAIR_FILLING | Root namespace/image/challenge and child image/challenge pairs are filled from the same values at the cited producers; peer pairs use distinct sources. Only these native equalities are vacuous; other classification predicates and separate producer checks remain real. Evidence: R/runtime/worldline/root_worker_physical.py:90-98; R/runtime/worldline/protected_resource_runtime.py:881-888; R/runtime/worldline/protected_scoped_supervisor_v3.py:185-191; R/core/resource_observation_classification.ads:79-114. |

N-3's illustrative protected canonical body locator in checkpoint-2 was corrected in checkpoint-6: its Off aspect is at R/core/worldline-canonical_operation_c_api.adb:3, not :7. S5's resource ledger On aspect is at S5/core/resource_run_ledger_c_api.ads:4. The census/digests themselves are unchanged.

### N-6 receiver and lineage resolution

`lease.gate is gate` is a constructor invariant, and both principals/services receive that same gate: R/runtime/worldline/protected_resource_runtime.py:149-150; R/runtime/worldline/protected_scoped_resource_runtime.py:62-75; R/runtime/worldline/protected_scoped_resource_service.py:62-66. The gate uses `threading.Lock`, not a reentrant lock (L/dependency-source/lab/intent_gate.py:371); the producer's separate order lock is an RLock (base runtime:150). Thus the following calls re-acquire the same gate on the calling thread if reached. This is source reasoning, not a statement about a running object.

| Held entry/section | Receiver and nested acquisition | Consequence/qualification |
|---|---|---|
| scoped intent_for_operation :385 | self.reconcile_context :388 -> :357 | Known DF-6. |
| scoped reconcile_context :357 | self.scoped_service.commit :373 -> service :223 | Conditional on context advance. |
| scoped submit_bound :412 | self.scoped_service.recover :416 -> service :213; commit :436 -> :223 | Reservation path remains blocked after an intent-only fix. |
| scoped settle_bound :507 | self.reconcile_context :508 -> :357; local commit closure -> self.submit_bound :516 -> :412 | The bare commit is a local closure, not the service method. |
| scoped settle_historical :526 | self.reconcile_context :538 -> :357; local closure -> self.scoped_service.commit :556 -> :223 | Conditional on missing adapter/preconditions first being repaired. |
| scoped resolve_historical :567 | self.reconcile_context :581 -> :357; local closure -> self.scoped_service.commit :596 -> :223 | Same adapter qualification. |
| scoped reconcile :612 | self.reconcile_context :613 -> :357 | First call in section. |
| scoped machine_admission :630 | self.reconcile_context :642 -> :357 | Conditional on policy checks passing. |
| scoped launch_reserved :701 | self.reconcile_context :714 -> :357; self.machine_admission :739 -> :630; self.submit_bound :742/:769 -> :412 | Conditional on launch checks; downstream entries also nest. |
| scoped go_scoped :854 | self.machine_admission :863/:930 -> :630 | Conditional on GO checks. |
| base launch_reserved :534 | self.machine_admission :567 -> :474; self.submit_bound :570/:595 -> :404 | Normal base-instance dispatch; scoped overrides this holder. |
| base settle_bound :604 | self.submit_bound :615/:618/:621/:624 -> :404 | Reaped, never-launched and unknown branches; scoped overrides this holder. |
| RootControllerCapture._current, root observation :57 | capture_execution(p,...) :61 -> actor execution :61, using same p.gate | Cross-module acquisition, not an unrelated method name. |
| base machine_admission :474 / settle_bound :604 / settle_historical :633 | self.current_context :480/:609/:654 -> base :235, which takes no gate | Not nested for a base instance. Normal scoped dispatch overrides all these holders; do not infer a false scoped override call from the bare name. |
| base settle_historical :633 | self.service.recover :652 and closure -> self.service.mutate :665 | RunLedgerService is outside the author's scan; no completeness/deadlock-freedom claim. |

The scoped rows refer to R/runtime/worldline/protected_scoped_resource_runtime.py; base rows to R/runtime/worldline/protected_resource_runtime.py; service rows to R/runtime/worldline/protected_scoped_resource_service.py. Root rows refer to protected_root_observation.py and canonical_actor_execution.py in the same runtime directory. The actual closure bodies were followed, rather than classifying every bare `commit` as a service call. No settle_bound caller was found in the selected runtime/dependency search; that is not permission to remove its accepted domain.

The base runtime and scoped service match A1's selected bytes: base SHA-256 `fc6f00f698160f1a854ef7ae72c425f3c7ed11243809b6dac1a5132c0e2ad33f`; service `e062ff0335d312366c90517cca21c73c0879d0b95de469840c36cea46250248f` (L/secondary-source-union-v1.json:407-431; checks.json:static_observations.A1_identity). This expands SL-0 into A1-origin files; it is not contradicted by the narrowly scoped committed-envelope review (AUTHOR-NOTES.md:105).

**Consequence:** fixing only the intent_for_operation nesting does not unblock the other listed reservation/admission/launch/GO/reconcile/settlement/capture paths. The repaired intent method itself might progress when its remaining conditions do; this review does not claim every entry is unconditionally blocked. SL-0's single-acquisition design is appropriate, but a complete receiver/Gate/thread/callback audit and separate A1 selection/freeze are still required (D:1710-1722). Do not replace the Gate with an RLock or treat a lower-bound scan as whole-system deadlock freedom.

## 3. Original accepted cases, controls and RQ-1

Do not endorse unconditional FRESH placement for every pre-effect or in-request exchange. The original scoped Check already refuses current-context rollover for Reserve, Record_Launch_Intent and Record_Running. That supports the proposed refusal for the concrete first-launch route, but does not prove the placement for every accepted retained reserve/replay/recovery caller. A single-frame flat embedding cannot establish the whole original scoped domain. No accepted first-launch rollover counterexample was established in this passive review.

Required treatment: Provide command-by-command and caller-by-caller domain correspondence. Apply current-context checks only where the original native command requires them; design Retained_Join for every required retained-origin path, and retain positive rollover controls. Keep RQ-1 and the original obligations OPEN until that mapping and evidence exist. Evidence: D:487-505; D:629-640; D:667; R/core/resource_scoped_run_ledger.ads:353-392,436-441; R/runtime/worldline/protected_root_worker.py:158-172.

The root first-launch ordering is reserve -> pre_effect -> launch (R/runtime/worldline/protected_root_worker.py:162,167,172). The original scoped Check rejects current-context changes specifically for Reserve, Record_Launch_Intent and Record_Running (resource_scoped_run_ledger.ads:436-438), while other retained lifecycle steps join the request to the row's origin (353-392). This review therefore finds no demonstrated original accepted first-launch rollover counterexample. It also declines to bless FRESH for all pre-effect/exchange callers or to infer full-domain equivalence from a single-frame construction. RQ-1 is PARTIALLY_CLOSED and remains an engineering obligation, not an operator-choice question.

| Domain/control issue | Decision | Evidence |
|---|---|---|
| TOTAL-EMBEDDING | G3 and the unspecified multi-frame variant leave the declared total embedding incomplete. Raw-domain-only exclusions cannot narrow the original quantified domain. | D:518-556,589-604 |
| SCOPED-CONTROLS | The multi-frame/multi-bucket refusal vectors do not specify an invalid predicate. Qualify the exact violated condition and include genuinely valid multi-frame/multi-bucket positives; neither shape alone is a new refusal. | D:642-654; R/core/resource_scoped_run_ledger.ads:303-312 |
| REQUESTER-PROVIDER | Mandatory FRESH socket cookies and namespace records can add a provider restriction. Explicit non-ready status does not preserve an originally accepted case; establish profile coverage or an authentic domain-preserving design. No new live-client/pidfd requirement is introduced. | D:1233-1247,1274-1285; R/runtime/worldline/client_peer.py:73-90,120-126 |
| REQUESTER-MODES | Unconditional J1/J3/J4 are inconsistent with J8's socket-free retained/historical modes. Mode-specific presence and request/operation/transaction joins must be explicit. | D:1220-1247,1265-1272,2023 |
| RECOVERY-DOMAIN | PREPARED-no-HELD release must exclude any dispatched/possibly-launched case; retained RESULT_CAPTURE recovery must not acquire an extra HANDLER_TERMINAL prerequisite. | D:1078,1562,1567; R/core/resource_observation_classification.ads:97-102; R/runtime/worldline/protected_operations.py:812-816 |

RQ-2 remains OPEN: an alternate construction must cover G3 without changing original arena/index domains or references. RQ-3 remains OPEN: Current_Facts can be a legitimate same-observation coherence requirement only with complete original caller-domain correspondence; a convenient witness is not coverage of every original accepted producer. RQ-4's minimum/low identification is not endorsed; RQ-5's P3 remains undefined. Evidence: D:518-611,667-669,720,765-778,1995-2003.

The exact v1 frontier control is retained, with additive v2 controls and no lead-only retirement (D:1580-1598; R/protected-startup/controls/test_protected_startup_v1.py:97-105). Every original ordinary/lifetime/control roster remains required on matching source (D:1965-1988; P1/HANDOFF.md:162). No new cap, narrower quantity/index/UID/GID domain, accepted native-failure refusal or weaker floor is authorized. Explicit UNKNOWN or a named non-ready status is honest disclosure; it does not satisfy the original genuine-positive requirement (PROMPT:32-34,64-66; P1/HANDOFF.md:125-137,161).

## 4. C-API v4 integration

| Hazard | Assessment | Evidence |
|---|---|---|
| H1 | SUPPORTED: Draft body insertion occupies the exact CAPI4 export-run anchor; reviewed run-end append is required. | D:1760,1775; CAPI4/DESIGN.md:334-355; R/core/worldline-c_api.adb:1165-1166,2284-2285 |
| H2 | SUPPORTED: Draft spec additions occupy the relocated subtype/export run; preserve original prefix and design reviewed append stage. | D:1761,1776; CAPI4/DESIGN.md:336-340; R/core/worldline-c_api.ads:242-275 |
| H3 | SUPPORTED: A draft text cannot satisfy S5 residual/spec/clause identities by assumption. Rebase must bind all new context and designed spans without editing earlier tables to fit. | D:1777; CAPI4/DESIGN.md:343,462-487 |
| H4 | SUPPORTED: External symbols must be re-observed exactly after composition; no calculated census substitutes for that observation. | D:1762,1778,1823; CAPI4/DESIGN.md:339 |
| H5 | SUPPORTED_CONDITIONAL: Nested Child_Boundary aliases are not current C_API-level collisions. Flattening/re-scoping can introduce hiding or altered resolution; hygienic names and explicit qualification are sound, installed resolution remains OPEN. | D:1779,1793-1795; R/core/worldline-c_api.adb:1198-1220,1285-1300,2251 |
| H6 | SUPPORTED: Use S5 On units and a separately reviewed protected C-API consolidation. Restoring Off files outside sole boundary violates the existing floor. | D:1780,1799; P1/HANDOFF.md:29,161 |
| H7 | SUPPORTED_STATIC_NOT_A_PROVER_RESULT: Off-body REQUIRED_PROVED names lack a designed proof-bearing carrier; move logic to enrolled On units, retaining obligations. | D:1781,1790,1798; R/runtime/worldline/proof_manifest.py:857-859,1031 |
| H8 | SUPPORTED: Recovery/Optional_Marker lineage must follow the explicit reviewed composition and preserve the separate infrastructure approval constraint. | D:1782,1800; CAPI4/DESIGN.md:768-781; D:357-363 |

Ordering: O1 is a sound staged direction: repaired/reviewed C-API successor on S5, then L-CAPI-P, reviewed protected import G-PROT, then root-worker run-end append stages. S5 residual identity can persist only if every later stage explicitly binds its context, span removals, gate/clause/alias/write tables and glue exceptions. G-CAPI-P/G-PROT dependencies must be in the body/gate DAG. No stage or lane acceptance follows. Evidence: D:1786-1809,1836-1901; CAPI4/DESIGN.md:247,343-355,424.

Rules: R-RW-1..10 are conservative and broadly sound but cannot adopt contradictory R-GATE or incomplete R-ALIAS unchanged. Carry V4-RC4-GATE and V4-RC4-ALIAS as predecessor obligations. Transport/renaming-name uniqueness does not enforce full expanded call qualification or catch indirect/transport-qualified alias paths. Evidence: D:1794-1801; CAPI4/review/gpt61-v1/REVIEW.md:3,48-60; CAPI4/DESIGN.md:472-484.

Checks: IC-1's subset and IC-8's glue check do not explicitly require the complete stage floor: G1-G10, K1-K5/K6 at their prescribed stage, P1-P3, R-ISO, R-TRANS, R-TILE, R-INV, repaired R-ALIAS/R-W/R-GATE, R-RES/S-RES/R-LAYOUT/R-GLUE, and D1-D5 when applicable. Add full scope-sensitive identifier/alias resolution including transport-qualified paths, branch-specific gate/write obligations and exact accepted rejection diagnostics. IC-10 remains installed-tool evidence; no compiler was run. Evidence: D:1819-1828; CAPI4/DESIGN.md:247,450-490; CAPI4/review/gpt61-v1/REVIEW.md:54-60.

V4-RC4-GATE must preserve branch-correct discriminant domination, the original False-variant rejection payload, and exclusive finalization assignments while repairing the normative rule, tables, checker promises and machine twin. V4-RC4-ALIAS must cover indirect and transport-qualified paths, or require exact expanded qualifiers per call with the same guarantee. These are inherited open obligations; this review neither repairs that lane nor determines its acceptance (CAPI4/review/gpt61-v1/REVIEW.md:54-60).

A further scope contradiction requires repair: R-RW-2's literal global no-renaming/declaration ban and IC-3's uniqueness across all transports conflict with CAPI4's retained S5 residual and exact per-scope clause tuples. Existing package-level Owner_* and Retry_*/Join_* renames remain in the residual; Recovery_Authorization_Transport, Recovery_Authorization_V3_Transport and Recovery_Protocol_Transport intentionally repeat W in separate scopes. Scope new hygiene bans to new root-worker additions and preserve every previously bound residual/tuple; do not rename/delete old clauses to make a global census pass. Evidence: D:1793,1795,1821; CAPI4/DESIGN.md:351-355,462-487; CAPI4/APPENDIX-BINDINGS.md:1497,1502-1504,1529-1531,1538-1541; S5/core/worldline-c_api.adb:879-880,1024-1026. This was identified in the final passive cross-check after checkpoint-4; the immutable checkpoint is supplemented by checks.json:item4_addendum and this final report.

Root-worker transports are appended after Pending_V2_Transport and their exports after Pending_Decide_V2, with the spec's subtype/declaration run and all original prefix order retained. Context additions must be explicitly stage-bound, On logic enrolled by name, and S5 residual/glue/spec identity maintained through the designed removals. R-RW-3's hygiene and renaming/moving Size are sound conservative choices; actual installed name resolution and warnings remain OPEN (D:1786-1801,1828; CAPI4/DESIGN.md:334-355,485-490). No symbol census or unchanged hash is source/proof acceptance.

## 5. OP-1..OP-9 and authority

| Operator item | Assessment | Reserved ruling / decision | Scope and file:line evidence |
|---|---|---|---|
| OP-1 | WITHIN_RESERVED_SCOPE | D-2a | Authoritative descriptor/journal/head/crosswalk/owner-plan provisioning and installation retain operator ownership. Source/schema/DDL design and review remain lead work. Runtime blocking means the relevant authoritative state, not a new gate on pure fixtures. Evidence: D:1926,1937; v1-review.json:D-2a. |
| OP-2 | WITHIN_RESERVED_SCOPE | D-2b | Frontier adjudication remains reserved, none proposed. Original frontier bytes and control remain. Evidence: D:1927,1580-1598; v1-review.json:D-2b. |
| OP-3 | WITHIN_RESERVED_SCOPE | D-4a | Any authoritative accounting/resource-policy change remains operator selected; no option chosen and no new cap/grant borrowing authorized. Evidence: D:1928,1325-1363; v1-review.json:D-4a. |
| OP-4 | WITHIN_RESERVED_SCOPE | D-5a | Delegation/profile installation and privileged actor/lab action retain existing reservation. Actor remains gpt-6-luna high through existing adapter, never reviewer. Evidence: D:1929; v1-review.json:D-5a; P1/HANDOFF.md:163. |
| OP-5 | WITHIN_RESERVED_SCOPE | D-5b | Helper privileged execution/installation reserved. Passive successor protocol/spec preparation and independent review are ordinary lead work. Evidence: D:1930; v1-review.json:D-5b. |
| OP-6 | WITHIN_RESERVED_SCOPE | D-7a | Reserve actual original API or owner-policy alterations only. An internal transport refactor preserving public ABI/protocol/accepted domain is not automatically a new operator gate; it still requires original source/spec/evidence review. None proposed in OP-6. Evidence: D:1931,1793-1801; v1-review.json:D-7a. |
| OP-7 | WITHIN_RESERVED_SCOPE | D-8b | Kernel measurements retain authorized lab/operator reservation. Static review does not perform them and ordinary pure-value design work is not newly approval gated. Evidence: D:1932,1942-1959; v1-review.json:D-8b. |
| OP-8 | WITHIN_RESERVED_SCOPE | D-9a | Fault campaigns retain existing specialized-validation reservation, with simulation labels and original controls. Evidence: D:1933; P1/HANDOFF.md:163; v1-review.json:D-9a. |
| OP-9 | WITHIN_RESERVED_SCOPE | original publication/deployment reservations | Merge/tag-release/install/sudo/production/real PRIME remain reserved. Authorized commit/push/draft PR after required reviews remain outside that gate; no publication executed in this review. Evidence: D:1934,1938; PROMPT:72-74. |

OP-1..OP-9 match the reserved decision categories: nothing lowered, and no additional gate is approved by this review. Required design/source reviews and evidence obligations are preserved without expanding operator authority.

Draft internal transport re-authoring with unchanged original public ABI/protocol/meaning/accepted cases requires the existing independent source/spec review, not a newly invented operator gate merely because implementation code moves. A genuine alteration of original API/owner policy remains D-7a. Pure native fixtures remain ordinary authorized work. The original prompt reserves tag/merge/release/install/sudo/production/PRIME and authorizes commit/push/draft PR after required reviews (PROMPT:72-74; D:1937-1940; AUTHOR-NOTES.md:96-99).

Optional_Marker approval reconciliation is outside this lane; the author's cited approval was not re-verified here and is not new authority from this review (D:357-360; AUTHOR-NOTES.md:101-106). Paused infrastructure and capacity/storage states are not reopened. No new authority is inferred from a brief, finding, required change or kernel measurement list.

## 6. Remaining weakening/assumption risks and required repairs

E3 samples machine availability and applies ledger withholding (R/runtime/worldline/protected_scoped_resource_runtime.py:673-696); it does not specify a mechanism that keeps future capacity available against interference. The kernel documentation distinguishes memory.high throttling/reclaim pressure from memory.min/low reclaim protection. The inference that E2+E3 fails to establish the claimed reserved-capacity guarantee is this review's source/design reasoning; the documentation does not measure this machine's kernel. Keep the original guarantee OPEN and do not add a policy field to make it pass. [Linux cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html). Evidence: D:773-778; P1/HANDOFF.md:125-131.

Source_Record Container_Bound must join supplied hashes to authenticated expected rosters; distinct tags/raw bytes and well-formed framing do not prove authentic independent producers. P3's source intersection cannot be silently called complete executed-source identity. The euid-0 coordinator's retained FD/capability/helper-channel reachability, the custody substate/DDL and the drain durability barriers are design obligations, not assumptions that become safe when named. Evidence: D:692-741,866-896,965-1100,1157-1176.

No library rename, Off carrier, required-name count, Global=>null annotation, ceiling, finite fixture suite, checked arithmetic or partial frame qualifies the original full relevant body/native-cost/caller scope. The S5 original prefix, original strict proof command, protected floor, zero unproved/justified/pragma Assume, all original accepted cases and complete matching controls remain required. This review ran none of those campaigns (D:334-342,1652-1697; P1/HANDOFF.md:158-164).

### Required changes

These are refinements needed before this design can be used unchanged as an implementation specification. They preserve the original RCs and ruling ownership/evidence. All apply to SEAM-DESIGN.md and seams.json together; they do not grant an operator decision, source acceptance or proof acceptance.

**V2-REQ-A** (RC-01, RC-03, RC-07, RC-11; D-1a, D-5a, D-6a). Specify typed V2 consumers end to end: scoped canonical Reference/Decide, exchange and K4 successors, facts/current-observation packets, wrappers and producers. Use the delegated Classify_V2/Native_Valid_V2 relation where required; keep every V1 reference and ABI unchanged. Add the consumed crosswalk/V2 and B2b/B2c/B6 dependencies to the body/gate graph.

Reason: S1 currently accepts original Facts_Array and calls original Native_Valid. Original Custody requires Delegate=no, while the delegated branch uses new facts/classification. No faithful bridge or complete dependency graph connects them. Evidence: D:445-450,467,629-662,818-859,1877-1896; R/core/resource_observation_classification.ads:79-95; R/core/resource_scoped_run_ledger.ads:232-268.

**V2-REQ-B** (RC-01; D-1a, D-1b). Complete the original-domain correspondence rather than declaring a total embedding over uncovered arenas. Supply the multi-frame construction and saturated-arena construction, distinguish raw-invalid and legitimate producer domains without excluding original accepted cases, and prove each extra conjunct from the original caller domain. For RQ-1 give the command/caller/time mapping and retain Retained_Join wherever originally accepted; qualify multi-frame/multi-bucket refusal fixtures by the actual violated predicate and include valid positives.

Reason: G3 and the unspecified multi-frame variant contradict totality. The single-frame embedding cannot settle every scoped rollover caller. The stated fresh launch guard supports the first-launch refusal only for the commands it names. Shape alone must not become a refusal. Evidence: D:487-556,575-611,642-669; R/core/resource_scoped_run_ledger.ads:353-392,436-441; R/runtime/worldline/protected_root_worker.py:158-172; P1/HANDOFF.md:125-131.

**V2-REQ-C** (RC-02; D-7a). Define feasible native extraction/framing for unchanged expected containers, explicitly join every expected Anchor to the authenticated controller/genesis roster, specify per-domain field/side grammars and the full dynamic crosswalk, and complete P3 with precise executed-source coverage and retained non-claims. Keep original producers/cases until authentic V2 producers and joins are designed; copied/relabelled-source assertions must follow from those exact predicates.

Reason: WL-SRC-V1 Raw cannot be assumed to be a subspan of existing JSON containers. Hashing a supplied container does not itself bind it to the authorized roster. P3's intersection remains undefined and cannot inherit full source-lease assurance. Evidence: D:686-710,718-763,802,2001-2004; R/runtime/worldline/protected_root_observation.py:36-49,74-76,121; P1/HANDOFF.md:133-137.

**V2-REQ-D** (RC-02, RC-06; D-4a, D-7a). Replace E3's future-capacity assertion and RQ-4's memory_high/minimum/low identification with a real full-domain host/ledger/enforcement/cost correspondence. Complete the independent-request accounting comparison without choosing an option or adding a cap, provider prerequisite, resource-policy field or accepted native failure. Any actual authoritative policy change retains D-4a operator selection.

Reason: Admission samples and withholding accounting do not demonstrate that capacity remains available against later interference. memory.high provides throttling/reclaim pressure, whereas memory.min/low describe reclaim protection. Ceilings plus samples are insufficient for the original completion/cost guarantee. Evidence: D:765-778,1325-1363,2002,2026-2028; R/runtime/worldline/protected_scoped_resource_runtime.py:673-696; P1/HANDOFF.md:125-131; https://docs.kernel.org/admin-guide/cgroup-v2.html.

**V2-REQ-E** (RC-03; D-5a, D-5b). Reconcile helper and dispatcher into one exact admission/create/measure/native Child_Ready/ACK/GO protocol, including all retained ABI/argv/env/stdin/EOF/FD surfaces. Complete the root coordinator reachability argument over every retained descriptor, writable view, capability and helper-channel command, with authentic native inputs and the original ancestry/containment predicates.

Reason: The helper prose demands a measured decision before creating the child that supplies that measurement. Read-only cgroup exposure and exclusion of one capability do not complete the euid-0 coordinator custody/authority argument. Delegation ownership is not an enforcement proof. Evidence: D:866-925,1130-1141,1942-1959; R/core/worldline-resource_child_execution.ads:203-208,248-257.

**V2-REQ-F** (RC-04, RC-07; D-9a, D-6a). Define the full native custody product state and mutation table: root ownership phase, generation, independent per-request and per-descriptor states, and legal gates at actual mutations. Supply complete DDL and CAS/replay semantics keyed to operation, generation, sub-generation/subject and alternative set, preserving exclusive ACK/ABANDON branches.

Reason: A single latest event does not explain parallel request/drain transitions while the worker remains the mutator. UNIQUE(operation,generation,kind) does not encode exclusivity between different kinds and does not represent repeated subject sub-generations. The CAS direction is sound but the complete state/schema is missing. Evidence: D:965-1009,1015-1030,1092-1100; R/runtime/worldline/root_worker_journal.py:123-140.

**V2-REQ-G** (RC-04, RC-07, RC-12; D-9a, D-6a). Specify the independent physical collection barrier and a complete crash/recovery product table. Separate NEVER_DISPATCHED from any dispatched/no-HELD uncertainty, and preserve automatic recovery of authentic retained RESULT_CAPTURE without an additional HANDLER_TERMINAL prerequisite. Keep canonical COMMITTED absorbing, genuine native quarantine/K4 paths and write-once original results.

Reason: The collector's described awaits and 'physical three' do not define the same typed barrier. The PREPARED/no-HELD release row conflicts with RT-2. RT-7 omits the original known-result recovery case when a helper terminal frame is missing. Evidence: D:995-998,1055-1059,1078,1447-1468,1555-1578; R/core/resource_observation_classification.ads:97-102; R/runtime/worldline/protected_operations.py:812-816.

**V2-REQ-H** (RC-08; D-3a). Complete drain/slot transfer through stop intent, cancellation/quiescence, in-flight buffers/writes, FREEZE/SPOOL durability, received-roster validation, exclusive intake/abandon and failure/restart resumption. Establish OFD/lock/custody/freshness evidence before authorizing new-owner I/O or mutation, and retain the real helper/init/outer-wait producers.

Reason: T1 stops the reader before FREEZE commits, while the failure table claims it never stopped. T4 resumes I/O before T5 records OFD identity. Crash windows and failed validation after intake are uncovered; continuity and exactly-once EOF are obligations rather than consequences of CAS alone. Evidence: D:1041,1130-1189; R/runtime/worldline/root_worker_custody.py:191-204.

**V2-REQ-I** (RC-09; D-8a, D-8b). Give mode-specific native requester predicates and enumerate every exact-type gate. Bind raw credentials, request/operation/transaction/reservation, custody generation and source containers explicitly. RETAINED/HISTORICAL inputs require typed absence where no socket exists. Establish original accepted-profile coverage for FRESH cookies/namespace evidence or design an authentic domain-preserving path; no still-live-client, fresh-pidfd or unavailable-provider refusal may become accepted.

Reason: J1/J3/J4 are unconditional despite J8's no-reader-socket modes; the exact gate list and complete joins are deferred. Join_Ready requires mandatory FRESH cookies absent from the original RequestPeer checks, so unavailability can introduce a new acceptance condition. Evidence: D:1220-1285,1389-1393,2023-2025; R/runtime/worldline/client_peer.py:73-90,120-126; P1/HANDOFF.md:137.

**V2-REQ-J** (RC-12; D-2a, D-2b). Finish exact startup version/loader/schema/creation-slot union, keysets and one-shot provisioning DDL, and connect every original recovery/owner path to the complete native product relation. Preserve v1 behavior and the unchanged frontier control; never initialize missing prior state or replace chain history.

Reason: U-1..U-12 and the RT outline are useful coverage scaffolding, but the exact schema/selectors and complete known/uncertain recovery mapping are still future deliverables. They cannot close RC-12 or D-2a at design level. Evidence: D:1509-1598,2032-2035; R/protected-startup/controls/test_protected_startup_v1.py:97-105.

**V2-REQ-K** (RC-11; D-7a). Update C-API predecessor status to the sealed v4 review; carry V4-RC4-GATE and V4-RC4-ALIAS OPEN. Specify every appended stage's complete invariant/table set, indirect and transport-qualified alias handling, branch-correct write/gate rules, residual/glue preservation and explicit G-CAPI -> G-CAPI-P -> G-PROT -> G-RW dependencies. Preserve original rejection diagnostics and exclusive finalization assignments; decide neither lane's acceptance. Scope R-RW-2's declaration/renaming ban and IC-3's uniqueness to the newly designed root-worker additions, while preserving CAPI4's already bound S5 residual and per-scope clauses.

Reason: O1 is a sound conditional order, but §14 adopts v4 rules whose normative gate promises conflict and whose alias invariant is incomplete. IC-1's subset does not explicitly carry all stage invariants. Name uniqueness is not full semantic qualifier resolution. Their literal global wording conflicts with original residual renamings and repeated legacy transport W aliases. Evidence: D:1750-1828,1851-1896,2264-2266; CAPI4/DESIGN.md:247,334-355,450-490; CAPI4/review/gpt61-v1/REVIEW.md:3,48-60; CAPI4/APPENDIX-BINDINGS.md:1497,1502-1504,1529-1531,1538-1541; S5/core/worldline-c_api.adb:879-880,1024-1026.

**V2-REQ-L** (RC-06, RC-11; D-4a). Make the complete receiver/Gate/thread/callback lock and availability model part of the normative design. Retain SL-0's single acquisition and original non-reentrant Gate, separately bind A1-origin changes, and specify protected status/cancel/recovery progress through shared locks, stalled I/O and executor occupancy. Keep every original floor and control. Apply all required repairs to prose and seams.json together, including withdrawal of uncovered totality claims.

Reason: Fixing intent_for_operation alone leaves submit/recover, launch/admission/GO/settlement/reconcile and capture nested acquisitions. to_thread preserves the event loop but does not alone establish protected-response or recovery progress. The machine twin currently calls uncovered Rebase/Emb total. Evidence: D:1396-1408,1705-1722,1873-1896; AUTHOR-NOTES.md:149-195; R/runtime/worldline/protected_resource_runtime.py:149-150; R/runtime/worldline/protected_scoped_resource_service.py:62-66,213,223; seams.json:closure.required_changes[01.2,01.3].

### Author process disclosures and limits

AUTHOR-NOTES.md labels itself model-origin prose, not evidence or review (:7). Its disclosed output-redirection exceptions, outside-list read commands, harness persistence and mistaken lead-session read are retained as disclosures (:228-248). Its no-interruption claim and the STATUS TaskStop attribution dispute are not independently settled here (:258-265,282-285). No full author-session audit was performed. Arithmetic replay does not authenticate these process counts. These statements are not substituted for the present hash/static checks or producer authenticity.

All numbered review items have create-only checkpoints. checkpoint-6 carries the N-3 locator erratum; checkpoints remain immutable. checks.json includes the complete hash/slice census, static observations, JACKAL responses, closure/checkpoint evidence and explicit NOT_RUN limits. review.json retains every original obligation and dependency as OPEN and every original ruling owner/evidence_required string. review-freeze.json binds exactly REVIEW.md, review.json and checks.json and is written last.

**Design verdict remains ENDORSED_WITH_REQUIRED_CHANGES.** No acceptance or Phase One closure is granted.
