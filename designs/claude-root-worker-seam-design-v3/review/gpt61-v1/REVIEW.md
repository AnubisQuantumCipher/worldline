# Independent review: WORLDLINE Phase One root-worker SEAM DESIGN v3

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.**

The model is a useful continuation of the sealed v2 design, subject to the required changes below. It repairs the create/measure order, separates requester modes, removes the extra handler-terminal prerequisite from retained-result recovery, and states OFD/roster evidence before intake. It still has contradictory witness, custody and requester rules and unfinished original-domain, authenticity, resource and availability obligations. All V2-REQ-A through V2-REQ-L and RQ-1 remain PARTIALLY_CLOSED. Clauses 01.2, 01.3, 04.1, 07.3 and 09.1 are NOT_CLOSED; 07.3 reopens because the effective v3 rules contradict the preserved Never_Launched release. Clauses 08.4 and 08.6 newly close at design level. Every original Phase One obligation stays OPEN.

Actual reviewer model selection: **gpt-6.1-sol**. Different from author: **true**. Author under review: **Claude Code lead claude-opus-5-5 (drafting subagent)**.

**source_acceptance=false; proof_acceptance=false; phase_acceptance=false.**

This is a different-author passive review by actual model selection gpt-6.1-sol. I authored none of the Claude design or draft lane. I read source as text/JSON and used hashing and bounded inspection scripts. I did not import or execute WORLDLINE/COSMOGONY/root-worker code, run compilers/provers/tests/services, inspect live stores/sockets/windows, or write outside this review directory. No SIA note or agent delegation was used. No explicit stop/kill/interrupt request was issued. Source-only and sealed-review identities are evidence of bytes, not proof of authentic runtime inputs, confinement or loaded-library correspondence. The author's process record is disclosed author prose; its complete tool history was not independently audited.

File aliases resolve as follows; every D3/D2 citation names the exact design file, and V3 names its companion directory:

| Alias | Absolute path |
|---|---|
| D3 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v3/SEAM-DESIGN.md |
| V3 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v3 |
| D2 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v2/SEAM-DESIGN.md |
| D2R | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v2/review/gpt61-v1 |
| D1 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1/SEAM-DESIGN.md |
| R | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/protected-original-root-worker-repair-v1/source |
| P1 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/outputs/claude-phase1-handoff-20261004 |
| CAPI4 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v4 |
| CAPI4R | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v4/review/gpt61-v1 |
| CAPI5 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v5 |
| CAPI5R | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v5/review/gpt61-v1 |
| S5 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-composition-v5-beta/source |
| PROMPT | /home/sicarii/Documents/complete-phase1-prompt.txt |

All supplied v3 pins match the passive readback:

| Input | Computed sha256 | Observed bytes |
|---|---|---|
| SEAM-DESIGN.md | a0f2f411d654f1cce472a1ad2a13d3c082fff42def050c5ed4694a8b094d07a0 | 217264 |
| seams.json | 093f31176dd9560a236b8ad00f5fd28a683c810c8f400d646631318ca1b582e8 | 36028 |
| jackal.json | 8cce45e34f12d9d7976cb9b04ab6ac47e3a99ae8cacc22708a84abe06ec0c024 | 3736 |
| AUTHOR-NOTES.md | dd382e1b0f74e825735e168ab6856b1c85e93f9a39312f3bc15019faf390a0ea | 12856 |

The sealed v1/v2 root-worker and v4/v5 C-API review freezes, report hashes, bytes and modes also match their named files; checks.json retains the full identity results. The post-draft C-API v5 review is evaluated as a sealed dependency, while v6 and in-progress reviews were not read. Evidence: D3:8-14; D2R/REVIEW.md:1-16; CAPI4R/REVIEW.md:3-7; CAPI5R/REVIEW.md:3-19,172-175.

## 1. Required-change, clause and ruling closure

The statuses below concern design closure. A stated future proof/body/control does not receive acceptance credit. Exact v2 ruling owners and evidence requirements are preserved verbatim, including their reserved operator decisions.

| Target | Closure | Remaining gap / evidence |
|---|---|---|
| V2-REQ-A | PARTIALLY_CLOSED | Typed families and V2 consumer names are supplied. Complete consumed native input/producer/ABI contracts and reconcile the declared graph with its preparation order; family selection must not substitute an interim refusal for an original accepted case. Evidence: D3:744-795; D3:1894-1949; D2:810-878 |
| V2-REQ-B | PARTIALLY_CLOSED | The multiframe construction contradicts carried W8; compaction contradicts carried L-RB-1; the C1-refusal factor shortcut contradicts unconditional W3. R1-R3 completeness and original-domain correspondence remain unestablished. Evidence: D3:804-955; D2:522-573; R/core/resource_scoped_run_ledger.ads:436-438 |
| V2-REQ-C | PARTIALLY_CLOSED | Container extraction and roster joins are better specified, but native key/genesis/current-head trust is not independently established, numeric canonicality remains Python-only, and P3 has conflicting executable-only versus all-file-backed coverage. Evidence: D3:959-1109; D3:1669-1682; R/runtime/worldline/root_worker_journal.py:39-53 |
| V2-REQ-D | PARTIALLY_CLOSED | False future-capacity and memory_high claims are withdrawn. No accounting/enforcement/native-cost option establishes the full target; option F is unselected and must preserve the immutable outer reservation bound. Evidence: D3:1110-1158; D2:866-877; P1/HANDOFF.md:125-131 |
| V2-REQ-E | PARTIALLY_CLOSED | Create/GO_FORK/measure/decide/ACK/exec ordering is repaired. Exact successor event/FD/native-command authorization and the exhaustive coordinator authority inventory remain incomplete. Evidence: D3:1159-1233; V3/AUTHOR-NOTES.md:47; R/protected-root/native_root_worker_supervisor_v1.c:336-368 |
| V2-REQ-F | PARTIALLY_CLOSED | Subject states, DDL, alternatives and replay-before-CAS improve the design. Legal/Next is not a complete product relation; actual mutation gates conflict with other sections, and replay identity omits subject_kind. Evidence: D3:1234-1390; D3:1466-1477; D3:1591-1645 |
| V2-REQ-G | PARTIALLY_CLOSED | Typed physical futures and first-capture recovery without handler terminal are supplied. Inactive-unit closure is an additional condition beyond the original terminal check; Never_Launched release conflicts with r3; complete post-intake and recovery-seed paths remain unspecified. Evidence: D3:1391-1457; D3:1279-1295; R/runtime/worldline/protected_root_supervisor.py:203-227; R/runtime/worldline/root_worker_closed.py:48-92 |
| V2-REQ-H | PARTIALLY_CLOSED | Stop intent and validate-before-intake order are supplied. Kernel-read-to-spool and write-to-durable-W windows, consumer reconstruction, retained writer duplicates and post-intake/release failures are not covered coherently. Evidence: D3:1458-1524; D3:1292-1293; V3/AUTHOR-NOTES.md:35-39 |
| V2-REQ-I | PARTIALLY_CLOSED | Optional corroboration, typed modes and the observed exact gate inventory improve the design. J8 requires the intake event before the Join that authorizes it; namespace comparisons and native join operands are incomplete; queued fallback does not establish protected response progress. Evidence: D3:1525-1649; D3:1877-1889; R/runtime/worldline/client_peer.py:110-117 |
| V2-REQ-J | PARTIALLY_CLOSED | Version union, exclusive creation and no missing-state initialization are retained. Exact tool/provisioner selection, genesis/head initialization, prior-v1 migration paths and every automatic recovery state still need a consistent specification. Evidence: D3:1650-1720; D3:1301-1374; V3/AUTHOR-NOTES.md:42-45 |
| V2-REQ-K | PARTIALLY_CLOSED | The stage floor, dependency chain, new-scope qualifier inventory and no root-worker assignment exception are sound directions. Both sealed C-API reviews keep gate/alias closure open; the v5 sole-exception and with-prefix capture repairs are not incorporated. Evidence: D3:1721-1836; CAPI4R/REVIEW.md:54-60; CAPI5R/REVIEW.md:58-60,84-92,172-175 |
| V2-REQ-L | PARTIALLY_CLOSED | Single-acquisition Gate discipline, thread placement and callback constraints are normative. Status/cancel/recovery and declined intake can wait indefinitely behind custody or stalled protected storage; response progress and prose/twin consistency remain incomplete. Evidence: D3:1837-1893; D3:1946-1949; V3/seams.json:226-338 |
| RQ-1 | PARTIALLY_CLOSED | Native guard placement and retained joins are improved; rollover crosses EFFECT_INTENT before possible launch refusal/quarantine. Original accepted-case, root/serial recovery and cost correspondence remain open. Evidence: D3:927-955; V3/AUTHOR-NOTES.md:23-27; R/core/resource_scoped_run_ledger.ads:436-438. |

Inherited RC aggregates: RC-01 = PARTIALLY_CLOSED; RC-02 = PARTIALLY_CLOSED; RC-03 = PARTIALLY_CLOSED; RC-04 = PARTIALLY_CLOSED; RC-05 = CLOSED_AT_DESIGN_LEVEL; RC-06 = PARTIALLY_CLOSED; RC-07 = PARTIALLY_CLOSED; RC-08 = PARTIALLY_CLOSED; RC-09 = PARTIALLY_CLOSED; RC-10 = CLOSED_AT_DESIGN_LEVEL; RC-11 = PARTIALLY_CLOSED; RC-12 = PARTIALLY_CLOSED.

| Clause | v2 closure | v3 closure | Assessment / file:line evidence |
|---|---|---|---|
| 01.1 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | V-A supplies Facts_V2 families and typed consumer names; native input, current-observation, producer and wrapper obligations are not yet complete contracts, and preparation order disagrees with the declared graph. Evidence: D3:744-955; D2:522-574,606-618. Predecessor: D2:431-485; D2:820-845; R/core/resource_scoped_run_ledger.ads:232-268 |
| 01.2 | PARTIALLY_CLOSED | NOT_CLOSED | Carried L-RB-1 keeps valid span positions; V-B.6 compacts and moves them. The declared Rebase cannot satisfy both rules. Evidence: D3:744-955; D2:522-574,606-618. Predecessor: D2:518-556; D2:601 |
| 01.3 | PARTIALLY_CLOSED | NOT_CLOSED | Carried W8 requires every row universe head to equal the state head; V-B.5 constructs unequal-head histories without replacing W8. W3 also contradicts the arbitrary-factor shortcut on C1 refusal. Evidence: D3:744-955; D2:522-574,606-618. Predecessor: D2:529-556; D2:599-601 |
| 01.4 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Coherent W1-W10 does not presuppose equal decisions; producer coverage remains an independent obligation. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:744-955; D2:522-574,606-618. Predecessor: D2:558-611 |
| 01.5 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Invalid-predicate controls and valid multiframe/multibucket positives are specified. CV-B-prime/CV-R and all extra-conjunct correspondence are still unproved and the constructions are inconsistent. Evidence: D3:744-955; D2:522-574,606-618. Predecessor: D2:589-604; D2:642-654; P1/HANDOFF.md:27-29,125-131 |
| 01.6 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Rounding withdrawn; exact divisible projection and raw Amount versus L.Amount distinguished. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:744-955; D2:522-574,606-618. Predecessor: D2:507-516; R/core/resource_scoped_run_ledger.ads:149-152,210-211 |
| 01.7 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Canonical/B2b/B2c use retained joins and the three native command guards are correctly distinguished. Rollover now crosses EFFECT_INTENT before launch refusal/quarantine; complete root/serial recovery and accepted-case cost/outcome mapping remain open. Evidence: D3:744-955; D2:522-574,606-618. Predecessor: D2:487-505,629-640,667; R/core/resource_scoped_run_ledger.ads:436-438 |
| 02.1 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Expected JSON containers are preserved and extraction/form parameters are supplied. Numeric canonicality is entrusted to Python and UTF8/escape/path/no-cap native semantics remain unspecified or unverified. Evidence: D3:959-1158. Predecessor: D2:686-710,718-724,802 |
| 02.2 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Roster_Join is explicit, but genesis/key/head authenticity requires an independently selected trust/custody/currentness chain; self-consistent packet hashes and MACs cannot supply that premise. Evidence: D3:959-1158. Predecessor: D2:692-710,737-741 |
| 02.3 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Crosswalk schema and operation/plan/cost/follow-up joins are proposed. Complete typed native decode, dynamic producer/caller correspondence and full costs remain open. Evidence: D3:959-1158. Predecessor: D2:743-763,2001-2004 |
| 02.4 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Sampling and memory_high are no longer described as reserved future capacity. No full-domain resource enforcement/interference/cost correspondence is supplied. Evidence: D3:959-1158. Predecessor: D2:765-778; R/runtime/worldline/protected_scoped_resource_runtime.py:673-696; P1/HANDOFF.md:125-131 |
| 03.1 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Separately reviewed additive classifier/scoped/child successor and no-delegation branch replace the Python Delegate-only change. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:744-795,1159-1233; D2:810-878. Predecessor: D2:818-859 |
| 03.2 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | The sequencing error is repaired; exact event relation, FD inheritance and helper enforcement of authentic native Child_Ready remain incomplete. Kernel/OS evidence remains unmeasured. Evidence: D3:744-795,1159-1233; D2:810-878. Predecessor: D2:866-896,913-919; R/core/worldline-resource_child_execution.ads:203-208 |
| 03.3 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | V1 and additive V2 families are retained; compatibility and accepted-case preservation are still stated lemmas with incomplete typed producer/caller coverage. Evidence: D3:744-795,1159-1233; D2:810-878. Predecessor: D2:845-859; D2:445-450,467,640 |
| 04.1 | PARTIALLY_CLOSED | NOT_CLOSED | M1/M2 omit a native custody-product gate, M6 excludes STOP_INTENT spooling, M8 conflicts with cancellation/helper stop, and r3 contradicts Never_Launched release. The complete Legal/Next reference is not defined. Evidence: D3:1234-1524; D2:970-1010,1061-1073. Predecessor: D2:962-967,1004-1009,2011-2015 |
| 04.2 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: ACK/ABANDON branches explicitly exclusive and ABANDON cannot reach WORKER_OWNED. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1234-1524; D2:970-1010,1061-1073. Predecessor: D2:972-988,1004-1008 |
| 04.3 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Independent subjects/subgenerations and an exclusive alternative primary key are supplied. Replay identity must include subject_kind; legal request/descriptor transitions and initial-head/state mapping remain incomplete. Evidence: D3:1234-1524; D2:970-1010,1061-1073. Predecessor: D2:965-967,990-992,1015-1021,1092-1097 |
| 04.4 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | PR-a/PR-b and retained-result recovery distinguish the old contradictions. Full post-intake/release failure and reconstruction seed/result-state mapping remain incomplete. Evidence: D3:1234-1524; D2:970-1010,1061-1073. Predecessor: D2:1032-1053,1078,1090-1100; D2:1562 |
| 04.5 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | The physical futures are now separately typed. CLOSED_OUTER adds unit inactivity beyond the original MainPID-zero/pidfd/wait test and can obstruct the original closure/reset route. Evidence: D3:1234-1524; D2:970-1010,1061-1073. Predecessor: D2:1055-1059,995-998,1466-1468 |
| 04.6 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Defined snapshot exclusion and raw-only content addressing remove recursive retention; size/OOM/native costs explicitly unclaimed. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1234-1524; D2:970-1010,1061-1073. Predecessor: D2:1061-1067 |
| 05.1 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: All ordered ordinary/lifetime/protected/lane rosters retained on matching candidate. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105. Predecessor: D2:1965-1988; P1/HANDOFF.md:162 |
| 05.2 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Exact v1 frontier bytes/version/domain and refusal retained. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105. Predecessor: D2:1580-1587; R/protected-startup/controls/test_protected_startup_v1.py:97-105 |
| 05.3 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Separate additive v2 roster proposed; no replacement. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105. Predecessor: D2:1977-1988 |
| 05.4 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Lead-only retirement expressly withdrawn. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105. Predecessor: D2:1588 |
| 05.5 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: No re-enrollment proposed; any future package retains originals and reserved adjudication/review. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105. Predecessor: D2:1589-1598 |
| 06.1 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Option A and all other options remain unselected. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1110-1158,1837-1893; D2:1348-1364. Predecessor: D2:1348-1363 |
| 06.2 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | A/B/C/E/F are compared and unselected; no option proves full-domain independent-request accounting, immutable parent bounds, enforcement and costs. Evidence: D3:1110-1158,1837-1893; D2:1348-1364. Predecessor: D2:1325-1363,2026-2028 |
| 06.3 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | UNKNOWN holds and owner routes are retained, but r3/M8 and shared-lock/custody waits prevent a complete original cancel/quarantine/owner recovery progress argument. Evidence: D3:1110-1158,1837-1893; D2:1348-1364. Predecessor: D2:1365-1385; D2:1555-1578 |
| 06.4 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Event-loop responsiveness is improved in intent. A dedicated serialized lane blocked on protected storage or held asyncio operation ownership can still prevent protected response completion. Evidence: D3:1110-1158,1837-1893; D2:1348-1364. Predecessor: D2:1396-1408,1433; R/runtime/worldline/protected_operations.py:717,728-768 |
| 07.1 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | O mapping and O-by-U cells are supplied; C/P/request/descriptor event transitions and their actual mutation gates remain incomplete and inconsistent. Evidence: D3:1234-1457; D2:384-405,1447-1463,1470-1496. Predecessor: D2:367-423,2011-2014 |
| 07.2 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: COMMITTED absorbing, genuine native quarantine and original K4 exits retained. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1234-1457; D2:384-405,1447-1463,1470-1496. Predecessor: D2:384-390,1457-1462 |
| 07.3 | CLOSED_AT_DESIGN_LEVEL | NOT_CLOSED | REOPENED: carried original Never_Launched release and PR-a require release without CLOSED_WITNESS, while r3 forbids it. Repair without weakening closure requirements for any possibly launched row. Evidence: D3:1234-1457; D2:384-405,1447-1463,1470-1496. Predecessor: D2:393-398,1453; R/core/resource_run_ledger.ads:317-320 |
| 07.4 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Serial order and SETTLED replay explicitly retained; later matching-source demonstration required. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1234-1457; D2:384-405,1447-1463,1470-1496. Predecessor: D2:1447-1455,1494 |
| 07.5 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: First RESULT_CAPTURE immutable, later report captures additive, collector uses first. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1234-1457; D2:384-405,1447-1463,1470-1496. Predecessor: D2:405,1450,1464-1468 |
| 08.1 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Durable stop intent precedes quiescence. M6 does not authorize required STOP_INTENT spooling, and restart does not specify reconstruction of the closed transport/consumer. Evidence: D3:1458-1524; D2:1128-1152. Predecessor: D2:1157-1169 |
| 08.2 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Raw stdin and buffer rules are proposed. Kernel write versus durable W and kernel read versus durable spool still have unclassified uncertainty windows; writer duplicates invalidate unconditional owner-death EOF. Evidence: D3:1458-1524; D2:1128-1152. Predecessor: D2:1157-1160 |
| 08.3 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | FREEZE requires spool fsync, but durable exact P/W and detection/recovery of pre-FREEZE consumption windows are not established. Evidence: D3:1458-1524; D2:1128-1152. Predecessor: D2:1157-1158,1167-1169 |
| 08.4 | PARTIALLY_CLOSED | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL: full receive/validate/report/OFD evidence precedes INTAKE and new-owner I/O. Runtime/caller/native evidence remains OPEN. Evidence: D3:1458-1524; D2:1128-1152. Predecessor: D2:1160-1161 |
| 08.5 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | The table covers more windows but post-INTAKE/new-owner failure and post-RELEASE restart, partial drain/spool and stdin progress recovery are incomplete. Evidence: D3:1458-1524; D2:1128-1152. Predecessor: D2:1165-1176 |
| 08.6 | PARTIALLY_CLOSED | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL: full root lock roster comparison/evidence is specified while originals are retained, before ACK/intake/role use. kcmp/pidfd/flock measurements and authentic roster proof remain OPEN. Evidence: D3:1458-1524; D2:1128-1152. Predecessor: D2:1160-1176; D2:1041 |
| 08.7 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Helper/init/systemd retained as reapers; only observation/reader/writer roles transfer. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1458-1524; D2:1128-1152. Predecessor: D2:1143-1151 |
| 09.1 | PARTIALLY_CLOSED | NOT_CLOSED | J8 requires committed REQUEST_INTAKE before Join, while Join authorizes that intake. Request/transaction/reservation inputs are named in prose but not fully represented in the native Join interface; PID versus user namespace comparison is ambiguous. Evidence: D3:1525-1649. Predecessor: D2:1220-1247,1389-1393 |
| 09.2 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Provider absence no longer directly refuses; validation precedes intake by rule. Circular Join and queued-only fallback still leave accepted transfer/protected response progress open. Evidence: D3:1525-1649. Predecessor: D2:1238,1246,1251-1259 |
| 09.3 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | The exact source gate list verifies. Mode-specific types improve the design, but all own-operation/transferred/historical caller operands and admission-head phases need complete contracts. Evidence: D3:1525-1649. Predecessor: D2:1233-1243,1260-1272,2023 |
| 09.4 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Full UID/GID and exited/delegated/same-UID process/preparer cases explicitly retained. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1525-1649. Predecessor: D2:1274-1285 |
| 09.5 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Cookie/namespace/pidfd absence is optional. Declining transfer then waiting until custody returns is not an accepted-case-neutral service path for live/UNKNOWN/stalled owners. Evidence: D3:1525-1649. Predecessor: D2:1238-1240,1282-1285; P1/HANDOFF.md:137 |
| 10.1 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Append-only reviewed final-source effective overrides. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D2:1625-1698; D3:113,1810-1827. Predecessor: D2:1629-1636 |
| 10.2 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: External exact inventory includes manifest/control/project/header/helper/dependencies and binds to independent freeze. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D2:1625-1698; D3:113,1810-1827. Predecessor: D2:1638-1650 |
| 10.3 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: New semantic/wire units enrolled; impossible draft Off-body names explicitly transferred to reviewed On carriers, not given proof credit. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D2:1625-1698; D3:113,1810-1827. Predecessor: D2:1652-1668 |
| 10.4 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: S5 original prefix, strict command/floor/boundary and zero unproved/justified/Assume retained. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D2:1625-1698; D3:113,1810-1827. Predecessor: D2:334-342,1670-1679,1693-1697; P1/HANDOFF.md:158-161 |
| 11.1 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Body/gate edges are richer, but V-M.4 preparation order places S6 before S1 although S6 depends on S1; native HMAC/roster/request product dependencies and consumed interfaces remain incomplete. Evidence: D3:1894-1949; D2:1836-1850,1926-1940. Predecessor: D2:629-640,1499,1855-1896 |
| 11.2 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: L-CAPI/L-A1 separately bound; L-CAPI-P newly identified and explicitly open. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1894-1949; D2:1836-1850,1926-1940. Predecessor: D2:1836-1849,1890-1894 |
| 11.3 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: Pure-value work/draft publication separated from reserved privileged decisions. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1894-1949; D2:1836-1850,1926-1940. Predecessor: D2:1926-1940 |
| 11.4 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: No Optional_Marker alteration or infrastructure-resume authority from this lane; approval reconciliation remains outside acceptance. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1894-1949; D2:1836-1850,1926-1940. Predecessor: D2:357-363,1799-1801,1939-1940 |
| 12.1 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Exact principal keysets and selection rules are proposed. Tool keys/provisioner paths, custody initial event/head/state authentication, migration paths and all constructor/loader selection artifacts remain unfinished. Evidence: D3:1391-1457,1650-1720; D2:1538-1554. Predecessor: D2:1509-1547,2033-2034 |
| 12.2 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | No handler terminal is required for retained first capture. Inactive-unit barrier, r3 versus PR-a, recovery material previously seeded by handler_terminal, and observed/settled mappings prevent complete closure. Evidence: D3:1391-1457,1650-1720; D2:1538-1554. Predecessor: D2:1078,1555-1578; R/runtime/worldline/protected_operations.py:812-827 |
| 12.3 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: UNKNOWN retains holds and native uncertainty; no EOF/deadline settlement. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1391-1457,1650-1720; D2:1538-1554. Predecessor: D2:1562-1568,1573 |
| 12.4 | PARTIALLY_CLOSED | PARTIALLY_CLOSED | Original K4/quarantine.resolve remain. Native mutation and actual serving progress through UNKNOWN, shared locks and unavailable custody are still incomplete. Evidence: D3:1391-1457,1650-1720; D2:1538-1554. Predecessor: D2:1383,1576-1578 |
| 12.5 | CLOSED_AT_DESIGN_LEVEL | CLOSED_AT_DESIGN_LEVEL | Preserved at design level: No missing-state initialization; one-shot offline operator provisioning. Full matching-source proof/runtime/control obligations remain OPEN. Evidence: D3:1391-1457,1650-1720; D2:1538-1554. Predecessor: D2:1538-1553,1574-1575 |

Ruling closure and the exact preserved ownership/evidence requirements:

| Ruling | Closure and remaining gap | Owner (verbatim) | Evidence required (verbatim) | Current file:line evidence |
|---|---|---|---|---|
| D-1a | PARTIALLY_CLOSED. Typed consumer contracts and graph are incomplete; W8/Rebase/W3 contradictions prevent coherent multiframe/saturated correspondence. Original references, accepted vectors and full body/native-cost target remain fixed. | Lead source designer; independent GPT-6.1 source/spec reviewer | Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls. | D3:744-895,1894-1949; D2:522-573 |
| D-1b | PARTIALLY_CLOSED. Per-command placement is better specified. Rollover may now write EFFECT_INTENT before launch refusal; root/serial quarantine, physical classification, recovery and cost/accepted-case correspondence remain incomplete. | Lead scoped model/caller designer; independent GPT-6.1 reviewer | Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof. | D3:927-955; V3/AUTHOR-NOTES.md:23-27; R/core/resource_scoped_run_ledger.ads:436-438 |
| D-2a | PARTIALLY_CLOSED. Version selection and exclusive creation are supplied, but exact tool/provisioner/initial-genesis/head/state/migration and full automatic recovery semantics remain unfinished. | Lead authors schema/callers; operator provisions or installs authoritative state | Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls. | D3:1650-1720; V3/AUTHOR-NOTES.md:42-45 |
| D-2b | CLOSED_AT_DESIGN_LEVEL. No remaining design-level frontier retirement gap; byte/version/domain and reserved re-enrollment adjudication retained. No re-enrollment is proposed, and all runtime/proof obligations remain OPEN. | Lead prepares concrete equivalence/adoption package; applicable operator authority; independent GPT-6.1 review | Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit. | D3:114-116; D2:1580-1598; R/protected-startup/controls/test_protected_startup_v1.py:97-105 |
| D-3a | PARTIALLY_CLOSED. OFD/roster evidence before use is repaired at design level. STOP_INTENT mutation, read/spool and write/W crash windows, reconstruction and post-intake/release handling remain incomplete. | Lead protocol designer; operator for lab execution | Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection. | D3:1458-1524,1292-1293 |
| D-4a | PARTIALLY_CLOSED. No accounting option selected and no complete original-domain reservation/cost/interference or protected-response progress design; immutable outer-bound and independent grants remain required. | Lead prepares native accounting comparison; independent GPT-6.1 review; operator selects any authoritative resource-policy change | Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls. | D3:1110-1158,1875-1891; D2:866-877 |
| D-5a | PARTIALLY_CLOSED. Typed V2 direction is supplied; native producers/commands, exhaustive coordinator authority reachability and reserved capacity remain incomplete and unmeasured. | Lead prepares native/OS design; independent GPT-6.1 review; operator for delegation and privileged lab action | Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls. | D3:744-795,1159-1233 |
| D-5b | PARTIALLY_CLOSED. Create/measure/native-decision/ACK ordering is repaired; successor event relation, exact retained surfaces and helper enforcement are still incomplete. | Lead helper designer; independent GPT-6.1 review; operator for privileged execution/installation | Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations. | D3:1159-1233; V3/AUTHOR-NOTES.md:47 |
| D-6a | PARTIALLY_CLOSED. COMMITTED, first result and original K4 stay fixed; Never_Launched release, physical barrier, full product and independent automatic reconstruction/retained-result routes need repair. | Lead historical/canonical model designer; independent GPT-6.1 review | Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement. | D3:1275-1457,1703-1716; R/runtime/worldline/protected_operations.py:363-383,778-816 |
| D-7a | PARTIALLY_CLOSED. JSON/source-record/roster/crosswalk direction is useful, but key/genesis/current-head trust, native canonicality, P3 coverage and C-API dependency closure remain open; no original API/owner-policy change selected. | Lead native/provenance designer; child-authority and GPT-6.1 re-review; operator for any original API/owner-policy alteration | Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation. | D3:959-1109,1721-1836 |
| D-8a | PARTIALLY_CLOSED. Mode fields and source gate inventory supplied. Pre-intake Join is circular; complete typed joins, PID/user namespace treatment and all per-gate own/transferred/history contracts are missing. | Lead OS/native requester designer; independent GPT-6.1 review | Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage. | D3:1525-1649 |
| D-8b | PARTIALLY_CLOSED. Optional provider corroboration and no live-client/pidfd condition are retained. Queued fallback lacks original response progress; all actual kernel evidence remains OPEN under the existing reservation. | Lead prepares domain-preserving protocol; operator for kernel measurement; independent GPT-6.1 review | Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client. | D3:1582-1591,1631-1636,1969-1984 |
| D-9a | PARTIALLY_CLOSED. Exclusive alternatives and replay-before-CAS improve the design; complete native event/product/mutation relation, subject identity, crash/reconstruction and physical barrier remain incomplete. | Lead additive SPARK relation and caller designer; independent GPT-6.1 review; operator for fault campaign | Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes. | D3:1234-1524 |

The original ruling text is also copied unchanged in review.json. No different ownership, lower evidence requirement or new approval gate is inferred from this review.

## 2. Carried slices, replacements and previously assessed items

The passive scripts observe 43 v2 slices, 43 R3 replacements and 22 transitive v1 slices. Every slice digest matches; v2 slices do not overlap; each replacement old quote is byte-exact, lies inside its declared slice and matches the machine-twin replacement inventory. checks.json retains every source and effective-slice digest. Evidence: D3:198-249,250-629,631-689; D2:2221-2287.

R3-1 through R3-43 are the complete declared local edits inside the carried slices. They are not the complete whole-document delta: B.3/B.5 explicitly replace other v2 sections and add V-A through V-Q. Binding the old text prevents hidden byte edits; it does not resolve conflicting new normative text. The following assesses each replacement:

| Replacement | Exact source quote / location | Assessment |
|---|---|---|
| R3-1 | YES; D2:362; D3:254 | REQUIRED_CHANGE: range omits K-20/K-21; preserve their reserved measurement owner. |
| R3-2 | YES; D2:380; D3:262 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-3 | YES; D2:408; D3:270 | PARTIAL: O-by-U table is supplied, but it is not a complete consistent product/event relation. |
| R3-4 | YES; D2:572; D3:278 | REQUIRED_CHANGE: W9 still requires identity-position L-RB-1, incompatible with compaction; W8/W3 are left inconsistent. |
| R3-5 | YES; D2:720; D3:286 | REQUIRED_CHANGE: executable-only mapping wording differs from V-C.7's every-file-backed-mapping definition. |
| R3-6 | YES; D2:738; D3:294 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-7 | YES; D2:1844; D3:302 | HISTORICALLY_CORRECT; update dependencies to the now-sealed C-API v5 review, which leaves both targets open. |
| R3-8 | YES; D2:1932; D3:310 | REQUIRED_CHANGE: OP-7 range must include K-20/K-21 under the existing D-8b reservation. |
| R3-9 | YES; D2:1980; D3:318 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-10 | YES; D2:985; D3:326 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-11 | YES; D2:986; D3:335 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-12 | YES; D2:992; D3:343 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-13 | YES; D2:998; D3:351 | CORRECT_LOCAL_REPAIR: removes extra handler prerequisite; full automatic recovery/barrier/seed design still incomplete. |
| R3-14 | YES; D2:1188; D3:359 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-15 | YES; D2:1285; D3:367 | PARTIAL: no direct provider refusal, but fallback waits for custody return without protected response progress. |
| R3-16 | YES; D2:1304; D3:375 | PARTIAL: decline-transfer preserves original front checks, but service availability is not established. |
| R3-17 | YES; D2:1305; D3:383 | PARTIAL: no accepted-request refusal for user namespace mismatch, but queue/return path lacks progress. |
| R3-18 | YES; D2:1389; D3:391 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-19 | YES; D2:1391; D3:399 | REQUIRED_CHANGE: Join/intake is circular and queued fallback is not a complete accepted-case service path. |
| R3-20 | YES; D2:2002; D3:407 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-21 | YES; D2:2018; D3:415 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-22 | YES; D2:2043; D3:423 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-23 | YES; D2:2045; D3:431 | HISTORICALLY_CORRECT; must now bind both sealed C-API v5 required repairs. |
| R3-24 | YES; D2:2053; D3:439 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-25 | YES; D2:467; D3:447 | CORRECT_LOCAL_REPAIR; retain RQ-1 original-domain/cost/recovery proof obligations. |
| R3-26 | YES; D2:468; D3:455 | CORRECT_LOCAL_REPAIR; origin/current/authority correspondence remains OPEN. |
| R3-27 | YES; D2:482; D3:463 | CORRECT_LOCAL_REPAIR; Retained_Origin is not itself a proved accepted-case equivalence. |
| R3-28 | YES; D2:484; D3:471 | CORRECT_LOCAL_REPAIR; embedding and Same_Context correspondence remain unproved. |
| R3-29 | YES; D2:489-493; D3:479 | PARTIAL: correct native command guard distinction; rollover may now write EFFECT_INTENT then quarantine. |
| R3-30 | YES; D2:495; D3:493 | CORRECT_LOCAL_REPAIR; every Retained_Join/caller implication remains OPEN. |
| R3-31 | YES; D2:498; D3:501 | CORRECT_LOCAL_REPAIR: separates original retained Reserved_New recovery from current Reserved_Replay pre-effect. |
| R3-32 | YES; D2:527; D3:509 | REQUIRED_CHANGE: compaction coverage is incompatible with carried L-RB-1. |
| R3-33 | YES; D2:529; D3:517 | CORRECT: withdraws unsupported totality without excluding original flat inputs. |
| R3-34 | YES; D2:556; D3:525 | REQUIRED_CHANGE: named construction contradicts carried W8; residual inventory not complete. |
| R3-35 | YES; D2:592; D3:533 | PARTIAL: constructive producer-coverage obligation remains unproved; W3/C1-refusal cases not reconciled. |
| R3-36 | YES; D2:593; D3:541 | PARTIAL: all originals retained, but R1-R3 must not be claimed exhaustive without resolving uncovered cases. |
| R3-37 | YES; D2:599-604; D3:549 | REQUIRED_CHANGE: G1 and G3 coverage claims inherit W8/Rebase contradictions; extra-conjunct proofs remain OPEN. |
| R3-38 | YES; D2:688; D3:567 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-39 | YES; D2:693; D3:578 | PARTIAL: expected containers stay unchanged; exact native extraction/canonicality and authentic producers remain OPEN. |
| R3-40 | YES; D2:694-696; D3:586 | PARTIAL: native roster join is specified but its key/genesis/current-head trust premise is not established. |
| R3-41 | YES; D2:914; D3:599 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-42 | YES; D2:915-919; D3:607 | JUSTIFIED_DESIGN_DIRECTION: declared local replacement is coherent; related full native/proof/control obligations remain OPEN. |
| R3-43 | YES; D2:1517; D3:623 | PARTIAL: additive schema and v1 parity retained; exact tool/provisioner selection remains unfinished. |

RC-05, RC-10 and D-2b remain CLOSED_AT_DESIGN_LEVEL. The exact frontier file digest is a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb; the v1 descriptor/domain refusal remains PROTECTED_FULL_LEDGER_STARTUP_RECONCILER_UNAVAILABLE with constructed gate/store and no controller. Additive v2 positives replace none. No lead-only retirement or re-enrollment is proposed. Evidence: D3:109-116; D2:1580-1598,1965-1988; R/protected-startup/controls/test_protected_startup_v1.py:97-105.

All other prior closed properties are retained at design level except 07.3: the unchanged original release obligation is present, but v3 r3 contradicts its effective implementation direction. The reopening is required precisely to keep that original guarantee fixed. Evidence: D3:124,1279,1424-1425,1433-1434; D2:393-398,1453.

| Carried observation | Exact sealed-v2 assessment |
|---|---|
| N-1 | VERIFIED_STATIC |
| N-2 | SUPPORTED_STATIC_TOOL_BEHAVIOR_OPEN |
| N-3 | VERIFIED_STATIC |
| N-4 | VERIFIED_BYTE_DIFF_AND_LAYOUT |
| N-5 | VERIFIED_LEXICAL_SCOPE |
| N-6 | SUPPORTED_STATIC_CONDITIONAL_RECEIVER_RESOLVED |
| N-7 | VERIFIED_STATIC |
| N-8 | VERIFIED_STATIC_ORDER |
| N-9 | VERIFIED_TEXT_SCOPE_RESOLUTION_OPEN |
| N-10 | VERIFIED_STATIC_PAIR_FILLING |

| Carried defect | Exact sealed-v2 assessment |
|---|---|
| DF-1 | VERIFIED_STATIC_RECOMPUTATION |
| DF-2 | VERIFIED_STATIC |
| DF-3 | VERIFIED_STATIC |
| DF-4 | VERIFIED_STATIC |
| DF-5 | VERIFIED_STATIC_ABSENCE_IN_SELECTED_TREES |
| DF-6 | SUPPORTED_STATIC_CONDITIONAL |

The C2-A3 byte binding carries N-1 through N-10 and DF-1 through DF-6 with their stated fixes and conditional/evidence limits. N-3's locator erratum is preserved: R/core/worldline-canonical_operation_c_api.adb:3. OP-1 through OP-9 retain the reviewed reserved scope; R3-8 only intends to extend its measurement inventory. Evidence: D3:134-154; D2:110-137; D2R/REVIEW.md:295; V3/seams.json:207-230,309.

## 3. Independent static assessment of NF-1 through NF-11

Every NF source citation was read; source hashes are retained in checks.json. Static path/encoding/lock observations are confirmed with the qualifications below. No kernel reachability, PID namespace, systemd or installed-runtime measurement is inferred.

| Finding | Assessment class | Static assessment | Consequence / file:line evidence |
|---|---|---|---|
| NF-1 | VERIFIED_STATIC_OPEN_FLAG_KERNEL_CONSEQUENCE_UNMEASURED | The descriptor is a host /proc directory opened O_RDONLY. That observation does not establish read-only child authority. The author's write-reachability conclusion remains unverified kernel reasoning (K-18). | M-2/read-only view and an exhaustive retained-FD capability argument are required; no measured containment credit. Evidence: D3:182; R/runtime/worldline/root_worker_custody.py:116-120 |
| NF-2 | VERIFIED_STATIC_CONTROL_FLOW_NOT_RUNTIME_COMMIT | The producer proposes Advance_Context on the listed changes, subject to native commit and reachability. Same_Context compares the listed context fields; the three command guards check scope/universe, not root/PRIME/catalogue/physical heads alone. Existing lock/refusal gaps preclude claiming observed commits. | RQ-1 must distinguish current-fact/header validation from the scope/universe command guard; a head-only rollover is not by itself Context_Changed. Evidence: D3:183; R/runtime/worldline/protected_scoped_resource_runtime.py:356-373; R/core/resource_scoped_run_ledger.ads:334-339,436-438; R/core/resource_run_ledger.ads:110-120 |
| NF-3 | VERIFIED_STATIC_LOCK_PATH | Status is mutating and takes the daemon mutation lock; principal.invoke takes operation_lock. This is a source lock path, not a measured stall or a claim that every registered nonmutating handler takes the mutation lock. | Status response progress must account for both locks and the protected lane. Evidence: D3:184; R/runtime/worldline/daemon.py:84,350-357; R/runtime/worldline/protected_operations.py:716-717 |
| NF-4 | VERIFIED_STATIC_AUTOMATIC_RECOVERY_BRANCH | Startup selects recover_committed on EFFECT_INTENT plus retained RESULT_CAPTURE without asking for handler terminal. recover_committed requires exactly one capture and replays the original native finish path; it can still fail its authentic/native gates. | No successor handler-terminal prerequisite is allowed for the original automatic route; first-capture and native result/cause/receipt conditions remain. Evidence: D3:185; R/runtime/worldline/protected_operations.py:363-368,778-816 |
| NF-5 | VERIFIED_TEXT_AND_LEXICAL_SCOPE | CAPI5 uses the words body-level. The renamings are inside the nested Child_Boundary body. The words alone do not establish whole-C_API visibility; v2's narrower lexical finding is confirmed. | Retain scope-specific integration inventories and checks; no review or correction of the other lane is granted here. Evidence: D3:186; CAPI5/DESIGN.md:332-339; R/core/worldline-c_api.adb:1166,1198-1220,2251; D2:131 |
| NF-6 | VERIFIED_STATIC_MANAGER_CALLS_REACHABILITY_UNMEASURED | The slot invokes systemctl --system show and stop. General euid-0 manager actuation reachability is the author's unmeasured inference (K-17), not an executed authority test. | M-1/M-4 must establish coordinator isolation and authentic helper-only manager authorization without changing original accepted manager flows. Evidence: D3:187; R/runtime/worldline/protected_scoped_supervisor_v3.py:23-36,290-305 |
| NF-7 | VERIFIED_STATIC_ROUTER_WAIT_AND_FRONT_GATE | The non-FRONT_OWNED redirect awaits all selected collectors under the router lock, then requires fresh reconstruction. Front.invoke requires FRONT_OWNED. This explains a conditional availability dependency, not a reproduced hang. | The original liveness/accepted-request obligation survives; durable queuing alone is insufficient. Evidence: D3:188; R/runtime/worldline/root_worker_endpoint_router.py:18-34; R/runtime/worldline/protected_root_worker.py:158-190 |
| NF-8 | VERIFIED_STATIC_ENCODING_FORMS | Startup canonical JSON is UTF8 ensure_ascii=False and allows the canonical bytes with one LF; resource exact JSON is ASCII ensure_ascii=True with no LF; the scoped config uses the latter. | Native form-dependent extraction must preserve those exact containers and numeric/escape behavior; RC-4 and full native costs remain OPEN. Evidence: D3:189; R/runtime/worldline/protected_startup.py:35-51; R/runtime/worldline/protected_resource_runtime.py:20-23; R/runtime/worldline/protected_scoped_resource_service.py:68-74 |
| NF-9 | VERIFIED_BYTE_IDENTITY_AND_STATIC_RELAY_JOIN_KERNEL_VIEW_UNMEASURED | Relay and S5 bytes have the supplied digest; the constructor enforces full peer-observation equality. The only other Python module in the selected source referring to the relay is the test module. Cross-namespace PID behavior remains unmeasured (K-1); no installed relay outcome is claimed. | Keep front RequestPeer exact; a worker-specific native correspondence type needs the complete mode/custody/transaction join and original exited-peer cases. Evidence: D3:190; R/runtime/worldline/client_peer_relay.py:32-121; R/runtime/worldline/client_peer.py:110-117; R/tests/test_client_peer_producer.py:17,136-137; S5/runtime/worldline/client_peer_relay.py |
| NF-10 | VERIFIED_STATIC_PLAN_SELECTION_GAP | The plan is an endpoint argument and source-lease DATA with the stated exact plan-v1 keyset. The startup-v1 top-level keyset has no root_worker key. | An additive v2 descriptor must select the exact plan and reject argument mismatch; keep v1 keys, constructors and frontier behavior. Evidence: D3:191; R/runtime/worldline/protected_root_endpoint.py:12,28; R/runtime/worldline/protected_root_worker.py:92-104; R/runtime/worldline/protected_startup.py:173-176 |
| NF-11 | VERIFIED_STATIC_GENESIS_AND_HMAC_BOUNDARY | The existing custody genesis has no MAC field and is DATA plus exact descriptor/plan/key digest equalities; stored genesis bytes are compared. Events/head are HMAC-checked under the loaded issuer key. This verifies code structure, not authentic key selection or anti-rollback. | Native genesis/head authentication must have a independently established key/genesis/currentness custody premise and defined initial/head/migration semantics; key lifetime/zeroization are also OPEN. Evidence: D3:192; R/runtime/worldline/root_worker_journal.py:25-26,39-53,95-113 |

## 4. Original domains, RQ-1 and queued requests

CV-R is an unproved proposed equality, not an exhaustive classification established by review. An unequal-head multiframe input meeting V-B.5(i)/(ii) still violates unchanged W8; compaction violates the unchanged position law; and the factor shortcut does not satisfy unconditional W3. Those cases cannot be waved into R1-R3 without a coherent specification. The unchanged flat route preserves its original inputs in intent, but retaining that route does not finish the required full-domain correspondence or scoped successful workflows. No raw-invalid or fixture case may be dropped.

Evidence: D3:804-879; D2:522,562,571; V3/AUTHOR-NOTES.md:29-31. Multi-frame/multi-bucket controls now name the violated predicate and include valid positives, which is a correct local repair; no shape alone is a refusal. Evidence: D3:902-921.

RQ-1 command / caller / time mapping:

| Command | Caller | Time | Resource/context join | Authority/facts retained | Evidence |
|---|---|---|---|---|---|
| Reserve | _reserve / scoped submit_bound | t0, new resource hold | current scope/universe native guard | original fresh use conditions retained | D3:943; R/core/resource_scoped_run_ledger.ads:436-438 |
| canonical pre-effect | invoke serial / root front | after reserve, before EFFECT_INTENT | Retained_Origin + Same_Binding; no current-scope conjunct | current snapshot Reserve_Use must be Reserved_Replay; full current facts remain | D3:927-944 |
| root before exec | root admission / custody offer | after HELD/Running, before native commit ACK | retained root row and full current native conjunction | no READY parameter or copied native decision allowed | D3:945; R/runtime/worldline/protected_root_supervisor.py:164-175 |
| Record_Launch_Intent / Record_Running | launch_reserved | before dispatch / after HELD | native current scope/universe guard | authentic original launch admission and physical observations | D3:946; R/core/resource_scoped_run_ledger.ads:436-438 |
| GO | go_scoped | before helper G/actor measurement | retained Running and native machine admission; no such scoped context-command guard | fresh numeric and original execution conjunction remain | D3:947; R/runtime/worldline/protected_scoped_resource_runtime.py:851-908 |
| exchange | in-request B2b | during original effect | retained origin | unchanged C1 Reserved_Replay on current authority snapshot | D3:948,927-932 |
| exchange recovery | broker recover / B2b | after restart or lost result | retained origin | original _original_native_use replay is Reserved_New on retained original snapshot; no fresh Reserve_Use | D3:949; R/runtime/worldline/protected_operations.py:430-438 |
| Record_Observed_Usage / settlement / reconcile | lifecycle / finish / collector | post-effect and lifecycle | retained origin + current observations; no scope/universe guard of the three new-launch commands | original native legal transition and authentic historical result | D3:950 |
| K4 | owner completion B2c | quarantine.resolve / recover / owner disposition | retained origin | original replayed use, cause, receipt and owner predicates | D3:951; R/runtime/worldline/protected_operations.py:605-622 |
| startup | full native reconciler | before endpoint or reconstruction | automatic lifecycle over authentic retained origin/current physical facts | no missing-state initialization; no live-client requirement | D3:952 |
| child Reserve | task dispatcher | new child hold before creation | current native scope/universe guard | original parent/use/ancestry/containment and separate child hold | D3:953 |

Conditional on all other pre-effect conjuncts, scope/universe rollover now passes pre-effect, writes EFFECT_INTENT, and can fail Record_Launch_Intent before dispatch or Record_Running after HELD. The original quarantine/K4 route is the intended outcome. That is a changed durable path and physical classification; the complete root/serial exception and known/uncertain recovery mapping and accepted-case costs are not proved. Head-only changes do not by themselves trigger this specific Context_Changed guard, but other original native/source gates still apply.

The authority distinction is essential: current pre-effect/in-request C1 requires Reserved_Replay, while original retained recovery/K4 replay uses Reserved_New on the retained original snapshot. FRESH requester validation is a separate mode from the withdrawn scoped-current-context conjunct. No current fact, ancestry, binding or original native launch guard is removed. RQ-1 remains PARTIALLY_CLOSED until all original caller/rollover/recovery/cost obligations are met. Evidence: D3:927-955; R/runtime/worldline/protected_operations.py:430-438,678-711,746-775.

For an unjoinable transferred request, REQUEST_ABANDON must mean declining transfer, not refusing the requested operation. Its durable QUEUED record is useful. FRONT_OWNED g+1 is not guaranteed under a live root, UNKNOWN owner or stalled protected storage, however. A complete authentic serving/progress route is still required for status, cancel, owner/quarantine and other original accepted requests. Preserve original named fault outcomes where originally allowed; do not fabricate a Join, borrow the first root's grant, settle on a deadline, or impose a new provider/live-client/cap condition.

The J8 circularity is a static specification contradiction: J8 names REQUEST_INTAKE(r), yet Legal requires Join_Ready to authorize REQUEST_INTAKE and V-I.7 puts Join before the CAS. Typed presence does not resolve that cycle. Origin/Reader PID namespaces are intentionally different; user-namespace equality and PID-namespace correspondence need separate rules. Evidence: D3:1540-1574,1586-1602,1642-1645,1631-1638.

| Accepted-case / assumption risk | Assessment and evidence |
|---|---|
| EMBEDDING | R1-R3 is not an exhaustive coherent partition as written; W8/L-RB-1/W3 contradictions remain. No original raw or fixture case may disappear while repaired. Evidence: D3:804-879; D2:522,562,571 |
| NEVER_LAUNCHED | r3 adds a release prohibition before CLOSED_WITNESS even for genuine never-dispatched rows; conflicts with preserved original release and PR-a. Evidence: D3:1279,1424-1425,1433-1434; D2:393-398,1453 |
| UNIT_INACTIVE | CLOSED_OUTER adds inactive-unit status beyond original terminal conditions. The source launches RemainAfterExit=yes and retains reset-after-closure; equivalence is not established. Evidence: D3:1397; R/runtime/worldline/protected_scoped_resource_runtime.py:761; R/runtime/worldline/protected_root_supervisor.py:218-227; D2:1069-1073 |
| QUEUED_NOT_REFUSED | Declining intake is not an operation refusal. QUEUED fallback must nevertheless preserve service progress; FRONT_OWNED g+1 may never arrive under LIVE/UNKNOWN/stalled custody. No join may be fabricated and no timeout/deadline may settle authority. Evidence: D3:1631-1636,1877-1889 |
| REQUEST_INTAKE | J8 is circular, namespace comparisons can incorrectly compare deliberately distinct PID namespaces, and not all native join operands are typed. Evidence: D3:1540-1602,1642-1645 |
| UNSELECTED_POLICY | No new accounting policy/cap is selected. Option F must remain unselected and may not weaken immutable outer reservation ceilings or first-root independent grant/cost obligations. Evidence: D3:1128-1155; D2:866-877 |
| AUTHENTICITY_PREMISE | Native HMAC/head consistency with packet-selected key/genesis is not an established independent authenticity/currentness premise. Source-lease DATA remains Python producer/custody work, not a native proof shortcut. Evidence: D3:988-1041; V3/AUTHOR-NOTES.md:32 |

The alternatives primary key and replay-before-CAS order are improvements, but they do not replace the complete native event relation. Include subject_kind in replay identity, authorize every actual mutation with the same native product, allow the stipulated quiescence/spooling transitions, and reconcile original cancellation with M8/M9. Define every post-intake/release failure and original known-result recovery route. Never_Launched must use its genuine native no-dispatch/no-effect evidence; any dispatched or possibly launched row still needs the full physical closure floor.

Evidence: D3:1275-1297,1377-1387,1466-1477. In particular, M1/M2 name authorization/resource gates with no custody product; M6 excludes the STOP_INTENT spooling required by H1; M8 disallows worker stopping while M9 proposes STOP_UNIT for the worker. A named Native Legal future cannot make those distinct actual mutation rules agree.

The original helper sends CLOSED and then waits for the owner's A before it exits; the original poll_closed journals CLOSED and sends A before waiting for helper/outer termination. That ordering is supported and must be retained. The source's terminal manager check is MainPID=0, and the launcher uses RemainAfterExit=yes. v3's additional inactive-unit condition lacks original-domain justification and interacts with the carried reset-after-CLOSED_WITNESS rule. The exact actual systemd state behavior is unmeasured here. Reconstructing a known result without HANDLER_TERMINAL also needs a replacement for the old ClosedFrontEscrow seed/current-state material taken from that frame.

Evidence: R/protected-root/native_root_worker_supervisor_v1.c:355-368; R/runtime/worldline/protected_root_supervisor.py:203-227; R/runtime/worldline/protected_scoped_resource_runtime.py:761; D3:1397,1415-1454; D2:1069-1073; R/runtime/worldline/root_worker_closed.py:48-92.

Authenticating a genesis/head under a key supplied in the same packet establishes consistency relative to that key. Authentic selection and currentness require the real issuer-key/genesis/head custody and producer/caller correspondence. The v3 note recognizes source-lease DATA as Python and leaves native key lifetime/zeroization OPEN; the remaining obligation also includes selection and rollback/current-head semantics. No native MAC/hash/tag substitutes for independent source authenticity or truthful executed-source capture.

Evidence: D3:988-1041,1301-1387,1676-1692; V3/AUTHOR-NOTES.md:32. P3 must use one identical coverage definition: R3-5 says every file-backed executable mapping while V-C.7 says every file-backed mapping. DATA-role and non-executable mapped files are not interchangeable with executed-image evidence. The stated anonymous-code/unmap/source-read non-claims remain and do not close truthful executed-code identity. Evidence: D3:291,1084-1100.

No new resource/accounting policy is selected. The inherited Byte_Count representation ceiling is not a new domain cap; compaction is nevertheless required to satisfy the actual witness laws. Candidate F cannot gain permission to weaken immutable outer reservation bounds merely by being listed. Resource protections, complete original grants/owners/costs and native failures remain original obligations. Evidence: D3:1110-1158; D2:866-877; P1/HANDOFF.md:125-131.

## 5. C-API integration against both sealed reviews

The stage floor and G-CAPI -> G-CAPI-P -> G-PROT -> G-RW direction are sound conditional requirements. The historical 'unreviewed CAPI5' label was honest at drafting time. Its now-sealed review leaves V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4 NOT_CLOSED and requires V5-RC4-GATE-EXCEPTION plus V5-RC4-QUAL-CAPTURE. Carry both into the composed stage rules, controls and twin. RW adds no assignment exception; preserve the existing sole finalization exception and every unchanged glue/diagnostic/old-scope tuple. Define the canonical-name/scope union so new RW scopes and calls do not escape or contradict the inherited whole-pair qualifier census. This review does not decide either lane's acceptance.

Evidence: D3:1721-1836,1930-1943; CAPI4R/REVIEW.md:54-60; CAPI5R/REVIEW.md:58-60,84-92,151,172-175.

The predecessor statuses remain: CAPI4 V3-RC4 NOT_CLOSED, V3-RC5/V3-RC6 CLOSED_AT_DESIGN_LEVEL; CAPI5 V4-RC4-GATE/V4-RC4-ALIAS/V3-RC4 NOT_CLOSED. G-CAPI is therefore unmet. G-CAPI-P and G-PROT do not make the draft protected Off units or incomplete shared callers acceptable. Evidence: CAPI4R/REVIEW.md:3,54-74; CAPI5R/REVIEW.md:90-96,172-175; D3:1936-1943.

The complete named floor is G1-G10, K1-K5 (K6 from PK-7), P1-P3, R-ISO/R-TRANS/R-TILE/R-INV/R-ALIAS/R-QUAL/R-W/R-GATE/R-RES/S-RES/R-LAYOUT/R-GLUE and D1-D5 from their applicable stage. Layout packages remain before Authority_Glue; export/spec runs remain at their existing ends. Actual append-only tables, all symbols/library-interface entries, wire/refusal codes, compiler warnings, full callee proof and native copy/stack/allocation/cost correspondence remain OPEN. Evidence: D3:1744-1767; CAPI4/DESIGN.md:337-356; CAPI5/DESIGN.md:225-230; CAPI5R/REVIEW.md:155-162.

The sealed v5 fixes require independent sole-exception identity and every capturing with-clause prefix/ancestor, with amendment and unchanged-stage/context controls. Listing bool/case RW rows or MQ1-MQ14 alone does not finish those repairs. R-QUAL applies to the whole pair and a scope without an entry must contain no listed names; specify how CAPI_ROUTINE_NAMES/CAPI_QUALIFIED and RW names/scopes combine while preserving old rows. Evidence: CAPI5/APPENDIX-BINDINGS.md:183-205; CAPI5R/REVIEW.md:58-60,84-88; D3:1760-1784.

| Check | Assessment | Evidence |
|---|---|---|
| IC-1 | SOUND_CONDITIONAL_INCOMPLETE: complete stage floor named; both v5 invariant repairs and actual append-only table composition still required. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-2 | SOUND_DIRECTION: new declarations census/homographs retained; full expanded-root/context-prefix capture belongs to the repaired qualifier invariant. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-3 | CORRECT_LOCAL_SCOPE_REPAIR: applies to new scopes; S5 residual and CL-T3/4/5/12/13/15 retained. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-4 | SOUND_DIRECTION: exactly one selected transport per export. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-5 | SOUND_DIRECTION: exact re-observed symbol census, no inherited count credit. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-6 | SOUND_FLOOR: no REQUIRED_PROVED name beneath Worldline.C_API; On carrier/body obligations retained. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-7 | SOUND_FLOOR: sole worldline-c_api Off boundary; L-CAPI-P remains required for protected Off files. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-8 | SOUND_DIRECTION: glue and all GE edits unchanged at every stage. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-9 | SOUND_DIRECTION: Optional_Marker remains unchanged; no approval transferred. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-10 | OPEN_UNPERFORMED: installed integrated compiler resolution/warnings, subject to its original admission requirements. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-11 | PARTIAL: indirect and transport-qualified controls specified, but missing v5 with-prefix capture amendment/positive and explicit CAPI/RW canonical-name/scope union. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |
| IC-12 | CORRECT_LOCAL_BRANCH_DIRECTION_WITH_OPEN_DEPENDENCY: RW has no assignment exception; base sole WF-X exception must be independently hard-bound, plus amended-exception/unchanged-stage controls. | D3:1818-1835; CAPI5R/REVIEW.md:58-60,84-92 |

## 6. Operator items and reserved decisions

| Item | Assessment | Reserved decision | Evidence |
|---|---|---|---|
| OP-1 | WITHIN_RESERVED_SCOPE | D-2a: authoritative state provisioning/migration/installation and privileged lab installation; prior chains/history retained | D2:1926; D3:1684-1698 |
| OP-2 | WITHIN_RESERVED_SCOPE | D-2b: frontier re-enrollment adjudication; none proposed | D2:1580-1598,1927; D3:114-116 |
| OP-3 | WITHIN_RESERVED_SCOPE | D-4a: any actual authoritative resource-policy selection/change; no option selected | D2:1928; D3:1110-1158 |
| OP-4 | WITHIN_RESERVED_SCOPE | D-5a: delegation/profile installation, privileged lab use and original WORLDLINE actor quota | D2:1929; D3:1159-1233 |
| OP-5 | WITHIN_RESERVED_SCOPE | D-5b: privileged helper installation/execution | D2:1930; D3:1190-1198 |
| OP-6 | WITHIN_RESERVED_SCOPE | D-7a: original API or owner-policy alteration; none proposed here | D2:1931; D3:109-154,1812 |
| OP-7 | WITHIN_RESERVED_SCOPE_RANGE_REPAIR_REQUIRED | D-8b: kernel/system measurements; K-20/K-21 belong to the same reservation as K-15..K-19, but R3-1/R3-8 omit them | D3:259,315,1969-1984; D2:1932 |
| OP-8 | WITHIN_RESERVED_SCOPE | D-9a: specialized authorized fault campaigns; simulations remain simulations | D2:1933; P1/HANDOFF.md:163 |
| OP-9 | WITHIN_RESERVED_SCOPE | Merge/release/install/sudo/production/real PRIME, under existing applicable operator authority | D2:1934,1938; PROMPT:72-74 |

C-API/root-worker independent-review gates are not new operator gates.

RC-1..RC-4 are ordinary lead-owned installed-runtime checks, OPEN and unperformed here; kernel K-15..K-21 remain D-8b reserved.

Pure-value/source/spec/schema/pin/inventory and concrete approval-package preparation retain existing authorization; draft publication retains the original review/ready conditions and is not expanded by this verdict.

S10 may be passively drafted as alternatives before D-4a selection, but its authoritative selected accounting specification cannot be claimed complete without that already-reserved decision. Clarify V-M.4 without adding a drafting gate.

This review authorizes no operational action and does not resume any paused infrastructure.

K-20 and K-21 are already listed with M-3 and remain D-8b operator measurements. R3-1/R3-8 omit them from their range and must be corrected. RC-1 through RC-4 are ordinary lead-owned installed-runtime checks with no new operator gate. None was performed. Evidence: D3:259,315,1969-1984; V3/seams.json:309-328.

The S10 table depends on D-4a selection, while the “can proceed now” sentence says none of its drafting needs an operator decision. Passive comparison/drafting may proceed; authoritative selection remains the already-reserved D-4a decision. Clarify completion versus preparation and correct the S6-before-S1 ordering; do not gate routine drafting. Evidence: D3:1908,1946-1949; V3/seams.json:284,308.

## 7. Further guarantees, required changes and open work

The effective multiframe witness cannot meet carried W8, and compaction cannot meet carried L-RB-1. The authority-refusal factor shortcut also conflicts with W3. r3 forbids the original pre-closure Never_Launched release. J8 requires the committed intake event before the Join that authorizes intake. M1/M2 do not expose the custody product to their native gates; M6 and M8 disagree with the drain/cancel protocol. CLOSED_OUTER adds an inactive-unit condition beyond the source's terminal check. Queuing until custody returns and leaving a protected storage stall on a single serialized lane do not establish protected response progress. Roster authenticity and C-API invariant closure remain open.

No additional selected cap, lower formal floor, new Off exemption, control retirement, original API replacement or approval authority is found beyond the reported contradictions and open premises. This is a bounded static-delta conclusion, not full successor equivalence. The prose/twin must agree on the witness/product/requester/drain rules, dependency order, plan-v1, complete measurement range and sealed C-API dependencies. Evidence: D3:7,259,315,1677,1946-1949,2004; V3/seams.json:43-54,276-328,343-360.

Required design repairs:

**V3-REQ-A.** Finish the typed V1/V2 consumer, current-fact, producer and wrapper contracts and the native-input dependencies. Reconcile V-M's preparation order with S6 depending on S1, and account for the HMAC/roster/request-product units. Keep original families/ABIs and accepted routes until the authentic successor is available.

Reason: Naming typed consumers and an acyclic declared graph does not complete consumed interfaces; the published preparation order contradicts a declared edge. Evidence: D3:744-788,1894-1949; V3/seams.json:276-308.

**V3-REQ-B.** Give one consistent witness/Rebase specification covering multiframe and saturated arenas: reconcile W8 with frame-local universe heads, reconcile L-RB-1 with compaction, and reconcile W3 with short-circuit authority refusal. Audit every extra conjunct and residual class; preserve all original inputs/fixtures and leave any unclosed correspondence obligation OPEN. Complete RQ-1's root/serial exception and recovery/cost mapping through rollover without moving native guards or weakening retained authority.

Reason: The current constructions cannot satisfy carried witness laws, and R1-R3 does not cover those contradictions. Rollover now has a later durable refusal/quarantine path whose accepted-case implications remain unestablished. Evidence: D2:522,562,571; D3:804-895,927-955; V3/AUTHOR-NOTES.md:23-31.

**V3-REQ-C.** Specify independently selected issuer-key/genesis/current-head custody and its native/producer correspondence, initial authentication and anti-rollback limits; do not treat self-consistent HMAC/hash inputs as authentic selection. Complete both unchanged JSON-form extraction semantics, including numeric canonicality and native domain/cost obligations. Make P3's mapping scope and all non-claims identical in the replacement, prose and twin; preserve the original executed-source target.

Reason: Roster_Join depends on an open trust premise, Python remains the only numeric-canonicality authority, and executable-only versus every-file-backed mapping definitions conflict. Evidence: D3:291,959-1041,1084-1100,1676-1692; V3/AUTHOR-NOTES.md:32-34; R/runtime/worldline/root_worker_journal.py:39-53,95-113.

**V3-REQ-D.** Complete the full-domain kind/grant/owner/amount/rollover enforcement and native-cost design comparison. Keep sampling separate from protected future capacity and compare option F against the preserved immutable outer reservation bound. Leave every actual policy selection to the existing D-4a decision, with no new cap, provider prerequisite, borrowing or accepted native failure.

Reason: Withdrawal of false capacity claims is correct but leaves the original accounting/capacity/cost target unfulfilled; option F cannot inherit permission to raise an admitted outer bound. Evidence: D3:1110-1158; D2:866-877,1348-1364; P1/HANDOFF.md:125-131.

**V3-REQ-E.** Complete the exact E1-E12 successor event/command/native relation, ABI/argv/env/stdin/EOF/FD inheritance roster and Child_Ready enforcement at COMMIT_CHILD. Enumerate every retained capability, descriptor, writable view, IPC/device/control path and justified privilege; define authentic helper ticket/decision/ancestry bindings. Retain all original coordinator/actor containment and immutable ceiling obligations and unperformed measurement status.

Reason: The sequencing repair is useful, but event names/native relation are explicitly unwritten and the reachability table is not exhaustive. Boundary/ticket checks alone are not the full native child authority conjunction. Evidence: D3:1159-1233; V3/AUTHOR-NOTES.md:47; D2:866-877; R/protected-root/native_root_worker_supervisor_v1.c:343-368.

**V3-REQ-F.** Define the complete native custody State/Event/Legal_Reference/Next/Mutation_Allowed relation with all request/descriptor transitions and actual mutations. Apply custody gates to operation-journal and scoped-ledger mutations as well as store/custody writes. Harmonize STOP_INTENT spooling and original cancellation/helper-stop permissions. Include subject_kind in replay identity and complete generation/initial-state/CAS/alternative joins, preserving exclusive branches.

Reason: The product is still rules plus a partial event graph; M1/M2 cannot decide custody, M6 conflicts with H1, M8 conflicts with helper/cancel paths, and replay keys are weaker than the typed subject identity. Evidence: D3:1234-1390,1466-1477,1520,1591-1645.

**V3-REQ-G.** Reconcile r3 with genuine Never_Launched release while retaining the full CLOSED_WITNESS floor for every possibly launched row. Preserve original terminal manager/pidfd/wait semantics without an unjustified new inactive-unit condition or reset cycle. Specify durable reconstruction/physical material independent of HANDLER_TERMINAL and the complete automatic retained-result, EFFECT_OBSERVED, SETTLED, broker-progress and post-intake crash routes; retain COMMITTED and first RESULT_CAPTURE immutability.

Reason: A previously closed accepted release case is contradicted, closure adds an unestablished condition, and the old reconstruction seed depended on the terminal frame that v3 correctly removes from use recovery. Evidence: D3:1279,1297,1391-1457,1703-1716; D2:393-398,1069-1073,1453; R/runtime/worldline/protected_scoped_resource_runtime.py:761; R/runtime/worldline/protected_root_supervisor.py:203-227; R/runtime/worldline/root_worker_closed.py:48-92.

**V3-REQ-H.** Cover kernel-read-to-spool and kernel-write-to-durable-W crash/cancellation windows, including detection of unretained bytes. Define reconstruction after closing transports, complete before/after INTAKE and RELEASE failure/restart behavior, and exact writer-duplicate ownership/EOF rules. Make the product mutation gates authorize the same quiescence/spooling protocol. Preserve full LIVE/UNKNOWN rosters and authentic reapers and keep uncertainty holds.

Reason: FREEZE fsync alone does not make earlier consumption/progress durable; a remaining writer duplicate invalidates unconditional owner-death EOF, and the restart table gives no complete post-intake/release recovery route. Evidence: D3:1292-1293,1458-1524; V3/AUTHOR-NOTES.md:35-38.

**V3-REQ-I.** Separate pre-intake authenticated transfer/head validation from post-intake serving authority so Join can authorize intake without requiring its own future event. Type and decode every request/operation/transaction/reservation/source/custody operand, with complete per-gate mode contracts. Distinguish user-namespace equality from deliberately different PID-namespace correspondence. Preserve optional corroboration and define authentic queued-not-refused progress for requests that cannot be joined, including status/cancel/recovery under live/UNKNOWN/stalled custody.

Reason: J8 is circular, namespace comparison can decline legitimate cross-PID-namespace transfers, native join operands are not fully supplied, and waiting for FRONT_OWNED g+1 does not establish original accepted response progress. Evidence: D3:1540-1649,1877-1889; R/runtime/worldline/client_peer.py:110-117.

**V3-REQ-J.** Finish the exact startup/loader/schema/tool/provisioner selection union, one-shot initial genesis/event/head/state authentication and prior-v1 migration paths, with no implicit creation or re-genesis. Complete each original recovery/owner mapping and keep plan-v1 consistently named. Retain exact v1 frontier/version behavior and additive v2 controls.

Reason: Tool names/provisioner paths and initial head/state semantics remain unfinished; the open list still says owner plan v2 after V-J retains plan-v1, and automatic recovery mappings are incomplete. Evidence: D3:1650-1720,2004; V3/AUTHOR-NOTES.md:42-45,69; D2:1580-1598.

**V3-REQ-K.** Bind the sealed C-API v5 review and carry both V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE as unmet dependencies. Hard-bind the sole staged G21c/Finalization_Decide/O exception independently of mutable tables and forbid any RW assignment exception; cover every capturing with-clause prefix/ancestor. Define the append-only canonical-name/scope inventory union and affected-stage controls, preserving GE1-GE9, old residuals/clauses, the complete stage floor and the gate chain.

Reason: The historical unreviewed dependency labels are honest but now incomplete. Both sealed reviews leave the gating/alias target NOT_CLOSED, and RW's added tables need explicit composition with the whole-pair invariant. Evidence: D3:1721-1836,1930-1943; CAPI4R/REVIEW.md:54-60; CAPI5R/REVIEW.md:58-60,84-92,151,172-175; CAPI5/APPENDIX-BINDINGS.md:183-205.

**V3-REQ-L.** Specify protected status/cancel/recovery response progress through shared asyncio/thread locks, stalled protected storage, registered I/O and executor occupancy, preserving original authorization at mutation. Reconcile the no-refusal queue path with that progress model. Apply all repairs to prose and seams.json, including preparation order, plan version, complete K-15..K-21 range and current sealed C-API dependency status. Retain non-reentrant Gate, SL-0 and separate A1 review lineage; add no approval gate.

Reason: Accepting/queuing connections is not protected response progress. V-L explicitly waits on storage/custody, and the prose/twin contain inconsistent ranges, versions and ordering. Evidence: D3:1837-1893,1946-1949,1969-1984,2004; D3:259,315; V3/seams.json:43-54,308,343-360; D2:121,132.

These repairs keep the predecessor ruling text, exact owners and evidence requirements above. They authorize no kernel/fault/lab/provisioning/deployment action. Subsequent exact-source independent review is still required.

The strict command/floor, sole boundary, complete original proof/ordinary/lifetime/control rosters, every relevant body/reference/caller/native-cost obligation, and zero-unproved/zero-justified/zero-Assume standard remain unchanged. All OB-001 through OB-219, including later release/COSMOGONY scope and dependencies, are copied as OPEN in review.json with closure_credited=false. No finite design closure, static finding, author check, source identity or this verdict grants source, proof or Phase One acceptance.

Evidence: PROMPT:32-34,60-66,72-74; P1/HANDOFF.md:27-29,125-143,153-167; D2:1625-1698,1965-1988; CAPI5R/REVIEW.md:155-162. OB-163 specifically requires filesystem stalls not to prevent answers; the unconditionally waiting protected lane does not meet that target. Evidence: P1/ALL-ORIGINAL-OBLIGATIONS.md:3247-3257; D3:1877-1883.

K-1 through K-21, RC-1 through RC-4 and IC-10 are OPEN and unperformed. All full bodies, references, callers, flow/RTE/termination/native semantic/cost obligations and original/additive control evidence remain OPEN. No prior passing prefix transfers to a changed source.

Numeric quantities, modes, counts and thresholds in this review are read from the inputs or observed by passive scripts. I derived no numerical proof result or native-cost value. No JACKAL arithmetic call was needed for the final report. Carried JACKAL values retain their predecessor status and informational/non-claim limits; neither a ledger nor a hash becomes mathematical or program-correctness evidence. Witness, allocation, termination and cost statements remain unproved obligations.

Passive inspection diagnostics: Some passive inspection scripts initially used an incorrect JSON field/list shape or an out-of-range display endpoint; one search named an absent tools directory. They were corrected without project execution or source writes. A bounded formatting pipeline reported Broken pipe when its output reader completed; direct range readers were used afterward. These diagnostics supply no test, runtime or acceptance evidence. An oversized artifact command was rejected before process creation; its payload was reduced by reading the completed checkpoints.

Checkpoints checkpoint-1.json through checkpoint-7.json are create-only completed records. The final REVIEW.md, checks.json and review.json are created once with O_EXCL, file/directory fsync and mode 0600; review-freeze.json is created last after matching readback. The freeze covers exactly those three final files.

**ENDORSED_WITH_REQUIRED_CHANGES. source_acceptance=false; proof_acceptance=false; phase_acceptance=false. Every original obligation remains OPEN.**
