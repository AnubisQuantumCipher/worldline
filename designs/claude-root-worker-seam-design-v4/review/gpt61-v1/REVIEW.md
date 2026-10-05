**WORLDLINE Phase One root-worker SEAM DESIGN v4 — independent design review**

**Verdict: ENDORSED_WITH_REQUIRED_CHANGES.** Actual model selection: gpt-6.1-sol. Author: Claude Code lead claude-opus-5-5 (drafting subagent). I authored none of the reviewed material. This verdict endorses the design direction subject to the repairs below. It grants no source, proof, runtime, lane, phase, deployment or operator acceptance.

All original Phase One obligations remain OPEN, including their original targets, owners, dependencies, controls and operator reservations. The draft lane remains INCOMPLETE_UNREVIEWED_UNUSED_SOURCE_ONLY. Neither C-API lane acceptance nor integration order is decided. Evidence: D4:1825-1852; P1/HANDOFF.md:91-93,119-131,153-167; complete-phase1-prompt.txt:32-34,64-78.

References below use these exact aliases; D1–D4 refer to the named SEAM-DESIGN.md file, not a free-floating version label.

| Alias | Exact file or root |
|---|---|
| W | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow |
| WT | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1 |
| D4 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v4/SEAM-DESIGN.md |
| D3 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v3/SEAM-DESIGN.md |
| D2 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v2/SEAM-DESIGN.md |
| D1 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v1/SEAM-DESIGN.md |
| AUTHOR-NOTES.md | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-root-worker-seam-design-v4/AUTHOR-NOTES.md |
| R | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/protected-original-root-worker-repair-v1/source |
| rw | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/protected-original-root-worker-repair-v1/source/runtime/worldline |
| L | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/protected-original-root-worker-repair-v1 |
| P1 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/outputs/claude-phase1-handoff-20261004 |
| S5 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-composition-v5-beta/source |
| CAPI4 | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v4 |
| CAPI5 / CAPI5R | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v5 / review/gpt61-v1 |
| CAPI6 / CAPI6R | /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/designs/claude-capi-boundary-design-v6 / review/gpt61-v1 |
| complete-phase1-prompt.txt | /home/sicarii/Documents/complete-phase1-prompt.txt |

The four requested primary identities were recomputed and match; every relied-on carried slice and sealed review identity also matched. checks.json retains the file identities, line-range hashes, quote checks, owner comparisons and checkpoint hashes. No target code, compiler, prover, test, service, namespace or live lab/storage/process action was run. Only the designated process-disclosure note was read; no transcript was read.

| Input | Computed sha256 |
|---|---|
| SEAM-DESIGN.md | f65629cb45e6e8a5ea798f5130a7f98e1d365758a7175343444f4022864efbda |
| seams.json | 92a814a4883d3e01680dbfeae82cb7889b038930bc4e21bcaefd39b622a2a86c |
| jackal.json | 4d556a457caa268c80b5d7ef4edae949433034ffeb950a5b4d2f8a29fcafcfab |
| AUTHOR-NOTES.md | 0bd92ccd556e39a358a5e93db5a57fe55ba206080d7b6dc1f033508d7f9c66e4 |

**1. Closure of predecessor required changes, every RC clause and ruling**

All V3-REQ-A through V3-REQ-L and RQ-1 are PARTIALLY_CLOSED. The numbered item-5 check refines checkpoint-1.json: its preliminary CLOSED_AT_DESIGN_LEVEL for V3-REQ-K is superseded by checkpoint-5.json’s integration-control finding. The create-only checkpoint is retained as history; this report and review.json carry the final assessment.

| Required change | Final closure | Remaining gap | File:line evidence |
|---|---|---|---|
| V3-REQ-A | PARTIALLY_CLOSED | The specification waves repair the S1/S6 edge and include HMAC/request/child nodes. Most consumer rows still use schematic ABI/export and producer descriptions rather than complete typed consumed interfaces; V1 fallback also inherits a newly imposed root workload guard. | D4:845-881; D4:883-948; D4:1017-1024 |
| V3-REQ-B | PARTIALLY_CLOSED | W2/W8 are frame-local, positional/compaction Rebase are distinguished and the C1 shortcut is removed. Compaction must retain the newly selected witness subspan as well as original packet spans, and the carried three-form text must agree. RQ-1 does not establish original operation-by-operation acceptance or cost equivalence. | D4:958-1009; D4:1011-1039; D3:823-879 |
| V3-REQ-C | PARTIALLY_CLOSED | P3 scope and non-claims now agree. The exact-rational Decimal_Value intermediate has no explicit lexical-sign channel for accepted negative zero, and Repr remains an external CPython definition. Authentic selection/currentness is still an open premise; compromise exclusions and rollback-detection overstatement cannot discharge the original target. | D4:1047-1104; D4:1106-1134; D4:1802 |
| V3-REQ-D | PARTIALLY_CLOSED | AO-1..AO-11 and unselected G improve the comparison and correctly reject F. The matrix admits that no option satisfies all obligations; qualitative cost labels and ledger checkmarks do not complete kind/amount/rollover/physical/native-cost correspondence. D-4a cannot authorize a weaker target. | D4:1142-1176; P1/HANDOFF.md:125-131 |
| V3-REQ-E | PARTIALLY_CLOSED | Launch ordering, measurement relay and native sub-helper redecision improve the design. READY followed by a disagreement ABORT violates the exclusive pair. The blanket worker-owned condition excludes collector finalization, and complete command material, C ABI and authority-preserving surfaces remain unfinished. | D4:1184-1227; D4:1229-1259; D4:735-748 |
| V3-REQ-F | PARTIALLY_CLOSED | Subject-kind replay and mutation choke points improve the proposal. The carried root graph still mixes request/drain and root transitions, root r1 excludes the newly permitted prelaunch release, r6 is written as an invariant instead of a barrier check, and M8(c) lacks an original job/unit authorization correspondence. The DDL cannot encode all new native fields/modes/quantities as specified. | D4:1267-1401; D2:974-1002; D3:1301-1369 |
| V3-REQ-G | PARTIALLY_CLOSED | The inactive-unit condition is removed and the handoff seed no longer requires HANDLER_TERMINAL. Never_Launched release is permitted in r3 but no coherent root-product release/return route is supplied. Complete restart recovery still depends on descriptor/escrow survival and serving authority not supplied by the tables. | D4:1359-1364; D4:1409-1453; D2:976-1000 |
| V3-REQ-H | PARTIALLY_CLOSED | Armed intervals detect uncertainty and duplicate writers are distinguished. Reattachment enables a reader before ARMED, READ interval detection is underspecified after chunk records, and front-crash/restart rows claim recovery of process-local pipe copies. Durable P/W cannot recreate an absent pipe or its consumed bytes. | D4:1461-1512; D4:1449-1451 |
| V3-REQ-I | PARTIALLY_CLOSED | Request Transfer_Join no longer requires its future intake and PID/user namespaces are separated. RELAY framing, per-gate response/request/generation binding and costs are unspecified, optional presence is internally inconsistent, the root ACK path is conflated with already-worker-owned request joins, and all own/historical gate modes are not supplied. | D4:1520-1634; D4:1572-1593; D4:1604-1617; AUTHOR-NOTES.md:73 |
| V3-REQ-J | PARTIALLY_CLOSED | Tool keys, provisioner paths and explicit migration alternatives are supplied. Empty-genesis head references an absent events row under the retained foreign-key setting, genesis raw bytes versus archive representation are conflated, new State fields have no exact DDL/fold encoding, and plan-v1 migration needs an explicit changed-path/exclusive-create mapping. | D4:1646-1698; D3:1339-1368; rw/root_worker_journal.py:78-98 |
| V3-REQ-K | PARTIALLY_CLOSED | Define an explicit effective joined checkview for the owning On-unit roster, qualified scope attribution and appended layout/tile sets while retaining every CAPI base-table byte. CAPI5's carried qualifier check tests each routine prefix for membership in CAPI_SPARK_UNITS, and V4 adds RW_ROUTINE_NAMES but supplies no explicit corresponding effective owning-unit map; derive it from a reviewed enrolled RW unit roster, not from the candidate name alone. Repair MQ-RW2's stimulus/expected relation without narrowing any existing qualified/gate rule or C-API row. | D4:1719-1726,1732-1743; D3:1744-1768,1779-1833; CAPI5/APPENDIX-BINDINGS.md:185-199,347-381; CAPI6/APPENDIX-BINDINGS.md:97-103,391-425; CAPI6/DESIGN.md:319-324; S5/core/worldline-c_api.adb:879-881,1024-1027; CAPI4/APPENDIX-BINDINGS.md:1529-1541 |
| V3-REQ-L | PARTIALLY_CLOSED | The dedicated lane is withdrawn and router waits leave the lock. The progress table lists new custody/UNKNOWN/collection waits but does not show original accepted response progress when the owner or its physical evidence never becomes available. M8(c) is not a proved substitute; RELAY and executor/storage dependencies remain incomplete. | D4:1751-1792; D4:1383; D4:1624-1626 |
| RQ-1 | PARTIALLY_CLOSED | The W0-W5 table preserves the three scoped Context_Changed sites and Retained_Join, but W2/W3/W5 equivalence is overclaimed. The root route inserts launch/currentness/physical waits before handlers that may not launch on the serial route, and restoring an unintegrated lane guard adds a root workload refusal. Exact per-operation original durable outcomes, recovery, accepted cases and costs are still required. | D4:1013-1039; rw/protected_operations.py:742-768; rw/protected_root_worker.py:162-199; P1/HANDOFF.md:91-93,115,125-131 |

The same-letter V2-REQ-A through V2-REQ-L remain PARTIALLY_CLOSED, with the same outstanding repaired-design/producer/body/control obligations. Their predecessor requirements are preserved, not replaced by the v4 letter labels. RQ-2 through RQ-5 remain OPEN dependencies where carried; this review does not grant them source/proof closure. Evidence: D4:31-67,1827-1838; D3/review/gpt61-v1/review.json:rc_closure and inherited_rc_closure (sealed identity in checks.json).

| Inherited RC | Final closure | Clause scope / evidence |
|---|---|---|
| RC-01 | PARTIALLY_CLOSED | Clauses 01.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-02 | PARTIALLY_CLOSED | Clauses 02.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-03 | PARTIALLY_CLOSED | Clauses 03.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-04 | PARTIALLY_CLOSED | Clauses 04.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-05 | CLOSED_AT_DESIGN_LEVEL | Clauses 05.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-06 | PARTIALLY_CLOSED | Clauses 06.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-07 | PARTIALLY_CLOSED | Clauses 07.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-08 | PARTIALLY_CLOSED | Clauses 08.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-09 | PARTIALLY_CLOSED | Clauses 09.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-10 | CLOSED_AT_DESIGN_LEVEL | Clauses 10.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-11 | PARTIALLY_CLOSED | Clauses 11.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |
| RC-12 | PARTIALLY_CLOSED | Clauses 12.* below; D4:75-139; D2/review/gpt61-v1/review.json:rc_clause_closure |

Every clause is assessed below. CLOSED_AT_DESIGN_LEVEL preserves only the already specified property; all matching-source implementation, body/reference/caller/native-cost proof and genuine runtime controls remain OPEN. In particular, 01.2, 01.3 and 09.1 have useful partial repairs; 04.1 and 07.3 still lack a coherent complete transition/product. Clause 04.5 closes at design level because the original outer wait/MainPID-zero predicate is restored. Clause 12.3 remains closed for retained uncertainty holds and no EOF/deadline settlement, while M8(c)’s cancellation-authority/behaviour gap remains in V4-REQ-F/L.

| Clause | Final closure | Remaining gap / retained property | File:line evidence |
|---|---|---|---|
| 01.1 | PARTIALLY_CLOSED | Typed interfaces are schematic; graph order repaired, caller/ABI contracts incomplete. | D4:845-948 |
| 01.2 | PARTIALLY_CLOSED | Rebase variants remove the positional contradiction, but compaction needs a precise union including witness N and a consistent form roster. | D4:960-975; D3:823-879 |
| 01.3 | PARTIALLY_CLOSED | Frame-local W2/W8 and unconditional positive-factor intent repair the old contradictions; saturated compaction/witness coverage and consistent carried forms remain incomplete. | D4:966-1009; D4:374-386,599-613,751-757 |
| 01.4 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:744-955; D2:522-574,606-618 |
| 01.5 | PARTIALLY_CLOSED | Extra-conjunct and R0 audits are explicit and all originals remain, but D_prod coverage and saturated witness specification remain open. | D4:981-1009 |
| 01.6 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:744-955; D2:522-574,606-618 |
| 01.7 | PARTIALLY_CLOSED | The W0-W5 table preserves the three scoped Context_Changed sites and Retained_Join, but W2/W3/W5 equivalence is overclaimed. The root route inserts launch/currentness/physical waits before handlers that may not launch on the serial route, and restoring an unintegrated lane guard adds a root workload refusal. Exact per-operation original durable outcomes, recovery, accepted cases and costs are still required. | D4:1013-1039 |
| 02.1 | PARTIALLY_CLOSED | Native canonicality is proposed, but signed zero and fully specified binary64/Repr/extraction correspondence remain unresolved. | D4:1085-1104,1802 |
| 02.2 | PARTIALLY_CLOSED | Independent selection and currentness remain premises; cross-references only constrain referenced prefixes and cannot justify the full detection claim. | D4:1049-1081 |
| 02.3 | PARTIALLY_CLOSED | Typed decoding/caller table improves the crosswalk; full consumed operands and authentic producer/ABI/native-cost contracts remain incomplete. | D4:1118-1134; D4:858-868 |
| 02.4 | PARTIALLY_CLOSED | Sampling stays separate from protection; no option meets enforcement/capacity/native-cost target. | D4:1140-1176 |
| 03.1 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:744-795,1159-1233; D2:810-878 |
| 03.2 | PARTIALLY_CLOSED | Helper redecision and launch order repaired; exclusive child decisions, collector completion, exact payload/C ABI and retained authority correspondence remain incomplete. | D4:1186-1259 |
| 03.3 | PARTIALLY_CLOSED | V1/V2 separation remains, but root-route refusal and schematic compatibility interfaces leave end-to-end accepted cases open. | D4:883-887,858-868,1021 |
| 04.1 | NOT_CLOSED | No complete consistent product: r1/release, r6, request-versus-root transitions, M8(c), State/DDL and predicate inputs conflict or are missing. | D4:1324-1401; D2:974-1002; D3:1339-1358 |
| 04.2 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1234-1524; D2:970-1010,1061-1073 |
| 04.3 | PARTIALLY_CLOSED | Replay includes subject_kind; CAS/exclusivity intent preserved. Exact State/DDL/fold, transition ownership and replay-authorized recovery actions remain incomplete. | D4:1392-1401; D4:1324-1388; D3:1307-1368 |
| 04.4 | PARTIALLY_CLOSED | Durable seed and added routes improve recovery; process-local descriptor loss and legal post-crash serving/side-effect replay remain unresolved. | D4:1427-1453,1487-1495 |
| 04.5 | CLOSED_AT_DESIGN_LEVEL | Original MainPID-zero/helper-pidfd/launcher-wait semantics restored; no inactive-unit/reset-cycle condition. All actual physical/native evidence remains OPEN. | D4:467-473,1417-1423; rw/protected_root_supervisor.py:203-227 |
| 04.6 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1234-1524; D2:970-1010,1061-1073 |
| 05.1 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105 |
| 05.2 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105 |
| 05.3 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105 |
| 05.4 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105 |
| 05.5 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D2:1580-1598,1965-1988; D3:109-116; R/protected-startup/controls/test_protected_startup_v1.py:97-105 |
| 06.1 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1110-1158,1837-1893; D2:1348-1364 |
| 06.2 | PARTIALLY_CLOSED | No option satisfies all AO obligations; actual costs and per-kind enforcement remain incomplete. | D4:1144-1176 |
| 06.3 | PARTIALLY_CLOSED | UNKNOWN holds remain but job.cancel-root-stop mapping and owner diagnosis progress are incomplete. | D4:1383,1767-1780 |
| 06.4 | PARTIALLY_CLOSED | Serialized lane withdrawn; fair executor isolation is a proposal and custody/evidence waits still obstruct accepted responses. | D4:1753-1792 |
| 07.1 | PARTIALLY_CLOSED | O/U mapping carried; C/P/request/descriptor and mutation relation remains inconsistent. | D4:1265-1401; D2:974-1002 |
| 07.2 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1234-1457; D2:384-405,1447-1463,1470-1496 |
| 07.3 | NOT_CLOSED | r3 and INV-C4 now permit Never_Launched release, but r1 still restricts pre-HELD root rows to RESERVED/LAUNCH_INTENT and the root graph supplies no no-launch settlement/return branch. The complete product still cannot admit the case. | D4:1359-1364,1409-1413; D2:976-1000 |
| 07.4 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1234-1457; D2:384-405,1447-1463,1470-1496 |
| 07.5 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1234-1457; D2:384-405,1447-1463,1470-1496 |
| 08.1 | PARTIALLY_CLOSED | STOP_INTENT spooling is authorized; reattachment and front-crash custody survival remain incomplete. | D4:1381,1463-1495 |
| 08.2 | PARTIALLY_CLOSED | Armed/duplicate rules improve accounting; restart FD survival, exact open-interval detection and write truncation/progress remain incomplete. | D4:1463-1506 |
| 08.3 | PARTIALLY_CLOSED | Clean-stop P/W durability specified, but reattach starts reading before ARMED and crash-gap detection needs a precise interval fold. | D4:1463-1481 |
| 08.4 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1458-1524; D2:1128-1152 |
| 08.5 | PARTIALLY_CLOSED | A-G table covers intended windows but several front-restart rows require lost FDs and gate states; no complete reconstruction route. | D4:1487-1495,1449-1451 |
| 08.6 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1458-1524; D2:1128-1152 |
| 08.7 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1458-1524; D2:1128-1152 |
| 09.1 | PARTIALLY_CLOSED | Request-intake circularity removed and namespace semantics separated; root ACK and native join operands/presence/independent selection remain incomplete. | D4:1524-1598,1630-1634 |
| 09.2 | PARTIALLY_CLOSED | Receive/validate before request intake retained. RELAY supplies a direction, but exact authentication/framing and real queue progress remain open. | D4:1624-1634; AUTHOR-NOTES.md:73 |
| 09.3 | PARTIALLY_CLOSED | Per-gate table exists but own/RETAINED/HISTORICAL modes and root-before-ACK versus request-intake phases remain incomplete. | D4:1604-1620,1633 |
| 09.4 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1525-1649 |
| 09.5 | PARTIALLY_CLOSED | Providers remain optional in intent; optional-field presence rules conflict and RELAY/queue adds unresolved service dependencies. | D4:1534-1593,1624-1626,1765-1780 |
| 10.1 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D2:1625-1698; D3:113,1810-1827 |
| 10.2 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D2:1625-1698; D3:113,1810-1827 |
| 10.3 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D2:1625-1698; D3:113,1810-1827 |
| 10.4 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D2:1625-1698; D3:113,1810-1827 |
| 11.1 | PARTIALLY_CLOSED | Spec waves now follow declared edges; full consumed interfaces and exact exports/body dependencies still schematic. | D4:870-948 |
| 11.2 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1894-1949; D2:1836-1850,1926-1940 |
| 11.3 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1894-1949; D2:1836-1850,1926-1940 |
| 11.4 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1894-1949; D2:1836-1850,1926-1940 |
| 12.1 | PARTIALLY_CLOSED | Selection union improves; initial FK/encoding and native State-to-DDL/migration contracts remain inconsistent. | D4:1648-1692; D3:1339-1368 |
| 12.2 | PARTIALLY_CLOSED | Closure inactivity removed, seed and recover_committed routes restored; no-launch product and crash custody survival still incomplete. | D4:1409-1453,1487-1495 |
| 12.3 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1391-1457,1650-1720; D2:1538-1554 |
| 12.4 | PARTIALLY_CLOSED | Original K4 and unresolved exception preserved in intent; unavailable-owner/UNKNOWN serving progress still incomplete. | D4:1773-1792,1383 |
| 12.5 | CLOSED_AT_DESIGN_LEVEL | Carried unchanged at design level; implementation, full matching-source proofs, authentic runtime and original/additive controls remain OPEN. | D4:129-139; D3:1391-1457,1650-1720; D2:1538-1554 |

Each owner and evidence_required string below is preserved byte-for-byte from the sealed v3 ruling record, including D-2b. The new required repair IDs identify unfinished work within those same responsibilities; they create no operator decision.

| Ruling | Closure | Owner (preserved) | Required evidence (preserved) | Current gap / evidence |
|---|---|---|---|---|
| D-1a | PARTIALLY_CLOSED | Lead source designer; independent GPT-6.1 source/spec reviewer | Concrete typed Reference/Decide/Post and embedding/witness definitions, all original clause and case mapping, later full body/reference/termination/native-cost proof and matching controls. | V4-A/B improve specification but typed interfaces, compaction witnesses and full original domain remain unfinished. Evidence: D4:845-948,960-1009 |
| D-1b | PARTIALLY_CLOSED | Lead scoped model/caller designer; independent GPT-6.1 reviewer | Explicit fresh/replay/historical domains, faithful scope/epoch spans, rollover accepted/refusal controls and full caller/kernel proof. | The W0-W5 table preserves the three scoped Context_Changed sites and Retained_Join, but W2/W3/W5 equivalence is overclaimed. The root route inserts launch/currentness/physical waits before handlers that may not launch on the serial route, and restoring an unintegrated lane guard adds a root workload refusal. Exact per-operation original durable outcomes, recovery, accepted cases and costs are still required. Evidence: D4:1013-1039; R/core/resource_scoped_run_ledger.ads:426-441 |
| D-2a | PARTIALLY_CLOSED | Lead authors schema/callers; operator provisions or installs authoritative state | Complete version union over every constructor/loader/schema/creation slot, one-shot full DDL/head/provisioning evidence, v1 parity and v2 genuine startup plus absence/crash controls. | Initial genesis FK/encoding, exact native-state storage and migration/reconstruction remain unfinished; provisioning/install stay operator-owned. Evidence: D4:1646-1698; D3:1307-1368 |
| D-2b | CLOSED_AT_DESIGN_LEVEL | Lead prepares concrete equivalence/adoption package; applicable operator authority; independent GPT-6.1 review | Original bytes/roster retained, exact version/domain mapping, all original negative cases and genuine positives, no replacement or passing-history credit. | Exact frontier bytes/version/domain and reserved re-enrollment adjudication preserved; runtime/proof/phase obligations OPEN. Evidence: D4:131,1698; D2:1580-1598; R/protected-startup/controls/test_protected_startup_v1.py:97-105 |
| D-3a | PARTIALLY_CLOSED | Lead protocol designer; operator for lab execution | Full LIVE/UNKNOWN rosters, true descriptor/lock/wait custody, buffered/raw drain continuity, failure/restart controls and authentic terminal collection. | Crash/restart pipe custody, reader-before-ARMED ordering and complete role-state reconstruction unresolved; physical lab evidence OPEN. Evidence: D4:1461-1512 |
| D-4a | PARTIALLY_CLOSED | Lead prepares native accounting comparison; independent GPT-6.1 review; operator selects any authoritative resource-policy change | Kind/grant/owner/amount/cost/rollover domain matrix, faithful host/ledger cost proof, no first-root grant borrowing or new caps, concurrency/status/cancel/recovery controls. | No admissible accounting option selected; fixed costs/enforcement and accepted response progress unresolved. Operator cannot waive original guarantees. Evidence: D4:1144-1176,1764-1792; P1/HANDOFF.md:125-131 |
| D-5a | PARTIALLY_CLOSED | Lead prepares native/OS design; independent GPT-6.1 review; operator for delegation and privileged lab action | Native classifier/root/child compatibility, actual cgroup/namespace lineage, immutable outer ceilings/capacity, coordinator privilege/FD custody, actor separation and matching controls. | Exhaustive inventory remains contingent on RC-6; retained capabilities/views/helper commands and original handler compatibility unestablished. Evidence: D4:874-887,1231-1259 |
| D-5b | PARTIALLY_CLOSED | Lead helper designer; independent GPT-6.1 review; operator for privileged execution/installation | Explicit input/native/source union, exact ABI/protocol/argv/env/stdin/EOF, FD inheritance audit, authentic ACK/ECHILD/waits/drains and retained native-body/cost obligations. | Child decision alternatives, collector completion and native C-helper ABI/payload/cost remain unfinished; no privileged execution or installation authority granted. Evidence: D4:1186-1227; AUTHOR-NOTES.md:76 |
| D-6a | PARTIALLY_CLOSED | Lead historical/canonical model designer; independent GPT-6.1 review | Original QUARANTINE_USE and K4 transitions/callers, authentic historical result/receipt/cause, current-denial/lost-ACK/never-launched/serial positives, no EOF/return settlement. | Seed/outer semantics repaired, but no-launch product and crash-safe automatic/historical recovery remain incomplete. Evidence: D4:1359-1364,1409-1453 |
| D-7a | PARTIALLY_CLOSED | Lead native/provenance designer; child-authority and GPT-6.1 re-review; operator for any original API/owner-policy alteration | Per-pair producer/canonical encoding/custody mapping, copied-tag and one-side corruption refusals, positive distinct-source equality, exact wire/layout and full original case preservation. | P3 repaired and C-API integration specified, but signed-zero canonicality and authenticity/currentness/producer/native-cost remain unfinished. Evidence: D4:1047-1134,1719-1743 |
| D-8a | PARTIALLY_CLOSED | Lead OS/native requester designer; independent GPT-6.1 review | Raw relative/host credentials, namespace/socket/custody and transaction/request joins, native decode/decision semantics, current-object and exact-type caller coverage. | Request transfer join repaired, but root ACK phases, full gate modes/operands and RELAY protocol remain incomplete. Evidence: D4:1524-1634 |
| D-8b | PARTIALLY_CLOSED | Lead prepares domain-preserving protocol; operator for kernel measurement; independent GPT-6.1 review | Original accepted exited/delegated/same-UID-new-process cases, real SO_PEERPIDFD/fdinfo namespace behavior, no PID-label substitution, historical settlement with no live client. | Providers optional in intent; optional-field contracts, queue progress and all kernel measurements remain unresolved. Evidence: D4:1534-1548,1765-1792,1814-1821 |
| D-9a | PARTIALLY_CLOSED | Lead additive SPARK relation and caller designer; independent GPT-6.1 review; operator for fault campaign | Complete native relation/body and caller correspondence, durable generations/crash-point table, lost-ACK/half-transfer/death/reconstruction controls, retained holds and independent physical/canonical outcomes. | Complete legal product, serialization, crash custody and mutation/cancellation correspondence remain incomplete. Evidence: D4:1324-1401,1487-1495,1662-1692 |

**D-1a — preserved ruling:** C2 is a plausible lifted model, not an established faithful equivalence as written. Exact divisible projection replaces the draft's rounding description; require RC-01 with full-domain coverage and no changes to original references. Required v4 repairs: V4-REQ-A, V4-REQ-B.

**D-1b — preserved ruling:** Epoch equality alone is insufficient. Fresh new reservations obey native current-context equality; retained replay/rollover needs a complete proved origin/current/authority join and must preserve original lifecycle cases. Use Same_Context, not record equality. Required v4 repairs: V4-REQ-B.

**D-2a — preserved ruling:** Prefer an additive exact v2 descriptor, selected by schema, with v1 behavior and controls retained. No implicit migration, defaults, bypass or missing-history genesis. Required v4 repairs: V4-REQ-F, V4-REQ-J.

**D-2b — preserved ruling:** No lead-only retirement of the mandatory frontier control. Keep exact v1/domain behavior and additive v2 controls; any proposed re-enrollment must be explicitly adjudicated while the original obligation remains OPEN. Required v4 repairs: none at design level; original evidence obligations stay OPEN.

**D-3a — preserved ruling:** Transfer complete V3 slot custody; do not require prior terminal state as a domain restriction. The transfer protocol still needs RC-08. Required v4 repairs: V4-REQ-H.

**D-4a — preserved ruling:** No accounting option is selected for acceptance. A may be explored only if it preserves all original independent-request accepted cases and real cost/parent/availability guarantees; otherwise choose or design a faithful alternative. Required v4 repairs: V4-REQ-D, V4-REQ-L.

**D-5a — preserved ruling:** Delegate=yes is not endorsed as a complete native design. Require an additive native custody/delegation successor, unchanged original predicates/cases and a concrete coordinator enforcement argument before operator deployment choice. Required v4 repairs: V4-REQ-A, V4-REQ-D, V4-REQ-E.

**D-5b — preserved ruling:** Prefer a separately versioned helper successor, preserving the exact V3/helper-stdin lineage and old controls. Extending V3 in place is not needed to obtain source design credit. Required v4 repairs: V4-REQ-E.

**D-6a — preserved ruling:** Keep canonical COMMITTED immutable; permit the original native use-quarantine/K4 domain when needed for uncertainty. Define orthogonal outcome/use/resource/custody states rather than selecting a blanket ban on quarantine. Required v4 repairs: V4-REQ-F, V4-REQ-G.

**D-7a — preserved ruling:** Independent sourcing alone does not close OB-030. Native Decide/Well_Formed must consume/enforce the distinct source-record domains or tags and canonical payload relation; use an additive grammar/version and preserve original references/ABI. Required v4 repairs: V4-REQ-C, V4-REQ-K.

**D-8a — preserved ruling:** Choose explicit native semantic correspondence inputs, carried by authentic producers. A producer-only label or digest in opaque current_source is insufficient. Required v4 repairs: V4-REQ-I.

**D-8b — preserved ruling:** Do not add a blanket fresh-pidfd or still-live-client precondition. Retain original kernel socket/credential evidence under authenticated custody and define the exited-peer path; absent evidence remains explicit and unresolved where correspondence cannot be established. Required v4 repairs: V4-REQ-H, V4-REQ-I, V4-REQ-L.

**D-9a — preserved ruling:** Yes: native custody-phase legality is mandatory because it determines who may mutate. Preserve exclusive ACK/ABANDON branches and authentic durable redecision under the actual CAS. Required v4 repairs: V4-REQ-F, V4-REQ-G, V4-REQ-H, V4-REQ-J.

**2. Carry integrity, exact quotes and amendment semantics**

Every substantive carried v3 line is carried or explicitly superseded. Within carried slices, the R4 replacements are the declared amendments, including the six explicitly addressed v2 lines; v4 also openly adds/supersedes its named new sections. No hash/quote mismatch or hidden range edit was found. This is a textual integrity finding, not a claim that the amendments are behaviour-neutral. Evidence: D4:183-214,220-789; D3:196-691; D2:522,561,571,1008,1053,1383.

Observed verified slices: v3 24, v2 43, v1 22. Each was hashed from its exact newline-terminated source bytes. All R4 old quotations match their specified source version and target range, lie inside the declared slice, have no duplicate/overlapping targets, and agree with their slice replacement lists. Transitive R3 quotations and v1 slices match too. This is textual integrity, not a conclusion that every amendment is behaviour-neutral.

| R4 IDs | Semantic assessment |
|---|---|
| R4-1, R4-3, R4-4, R4-5, R4-6, R4-11, R4-12, R4-13, R4-16, R4-17, R4-18, R4-26, R4-27, R4-28, R4-30, R4-37, R4-38, R4-39, R4-40, R4-41, R4-42, R4-43, R4-50, R4-51, R4-52, R4-53, R4-54, R4-55, R4-57, R4-59, R4-60, R4-61, R4-62, R4-63 | JUSTIFIED_CORRECTION_OR_SCOPE_CARRY; substantive completion remains as item 1 and items 3-7. Source measurement, helper verification, provisioning and installed-runtime assertions are not verified by the quotes. |
| R4-2, R4-14, R4-15, R4-19, R4-20, R4-45, R4-46, R4-58 | JUSTIFIED_PARTIAL_CORRESPONDENCE_REPAIR; frame-local witnesses and rebasing improve the construction, but residual coverage, RQ-1 and original acceptance/cost correspondence remain OPEN. |
| R4-7, R4-8, R4-9, R4-10, R4-31, R4-32, R4-33, R4-34, R4-35, R4-36, R4-44, R4-48, R4-49, R4-56 | PARTIAL_SEMANTIC_REPAIR; RELAY message/freshness/response semantics, crash-surviving escrow, armed-interval ordering, M8(c) authorization and progress, and ABANDON from a pre-transfer failure phase remain unresolved. Exact quote integrity does not justify the changed behaviour. |
| R4-21, R4-22, R4-23 | PARTIAL_NATIVE_JSON_AUTHENTICITY_REPAIR; native signed-zero semantics, full cost, selection/producer premise discharge and anti-rollback boundary remain OPEN. |
| R4-24, R4-25 | JUSTIFIED_WITHDRAWAL_OF_OUTER_BOUND_INCREASE; no accounting option selected or proven to meet the unchanged floor. |
| R4-29, R4-47 | PARTIAL_CUSTODY_REPAIR; new event names and Never_Launched exception require a complete product transition/DDL encoding and legal settlement path. |
| R4-64 | NOT_SUFFICIENT_AS_WRITTEN; durable CHILD_READY precedes the sub-helper decision while CHILD_ABORT remains its disagreement response, conflicting with the exclusive READY/ABORT set. Required repair is in item 4. |

The exceptions with required design repair are explicit: R4-48’s global capture-failure stop-after-ABANDON rule conflicts with M8(a)’s handoff-window qualifier, and ABANDON has no stated pre-transfer handoff-failure transition; R4-49/M8(c) changes the UNKNOWN cancellation row; R4-64 commits READY before a possible exclusive ABORT. The root workload guard in V4-B.5 is justified as DF-3 containment/order repair, not as evidence that all original accepted workload cases are preserved. Evidence: D4:623-638,743-748,1021-1039,1204-1226,1383; D3:326-342.

D-2b, the already closed clauses, RC-05/RC-10, NF-1 through NF-11, N-1 through N-10 and DF-1 through DF-6 retain exactly their sealed predecessor assessments. NF/N/DF status labels below are carried static/historical findings, not new executed controls or acceptance. The source and review bytes used to carry them are sealed and unchanged. Evidence: D4:129-139; D3:178-192; D2:85-123; sealed review files in checks.json.

| NF ID | Preserved assessment |
|---|---|
| NF-1 | VERIFIED_STATIC_OPEN_FLAG_KERNEL_CONSEQUENCE_UNMEASURED |
| NF-2 | VERIFIED_STATIC_CONTROL_FLOW_NOT_RUNTIME_COMMIT |
| NF-3 | VERIFIED_STATIC_LOCK_PATH |
| NF-4 | VERIFIED_STATIC_AUTOMATIC_RECOVERY_BRANCH |
| NF-5 | VERIFIED_TEXT_AND_LEXICAL_SCOPE |
| NF-6 | VERIFIED_STATIC_MANAGER_CALLS_REACHABILITY_UNMEASURED |
| NF-7 | VERIFIED_STATIC_ROUTER_WAIT_AND_FRONT_GATE |
| NF-8 | VERIFIED_STATIC_ENCODING_FORMS |
| NF-9 | VERIFIED_BYTE_IDENTITY_AND_STATIC_RELAY_JOIN_KERNEL_VIEW_UNMEASURED |
| NF-10 | VERIFIED_STATIC_PLAN_SELECTION_GAP |
| NF-11 | VERIFIED_STATIC_GENESIS_AND_HMAC_BOUNDARY |

| N ID | Preserved assessment |
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

| DF ID | Preserved assessment |
|---|---|
| DF-1 | VERIFIED_STATIC_RECOMPUTATION |
| DF-2 | VERIFIED_STATIC |
| DF-3 | VERIFIED_STATIC |
| DF-4 | VERIFIED_STATIC |
| DF-5 | VERIFIED_STATIC_ABSENCE_IN_SELECTED_TREES |
| DF-6 | SUPPORTED_STATIC_CONDITIONAL |

The mandatory frontier control is unchanged at sha256 a0d2d529aff1322ce11e66d955f5af4161cbdfff59e0c032d770c51e734cdbeb, with its exact v1/version/domain behavior and no re-enrollment. All old and additive controls remain required. OP-7’s range repair includes previously omitted K-20/K-21 and new K-22/K-23 under the same reservation. Evidence: D4:131-138,254-259,1696-1698; D2:1580-1598,1927,1932; R/protected-startup/controls/test_protected_startup_v1.py:97-105.

**3. NF4-1 through NF4-13, independently checked as static source**

| Finding | Assessment class | What the source establishes | Consequence for the design | File:line evidence |
|---|---|---|---|---|
| NF4-1 | VERIFIED_STATIC_CONDITIONAL | After launch returns an owned object, the root exception branch stops/retains and does not itself call original quarantine; with owned None it does quarantine. EFFECT_INTENT lacks the serial DISPATCH_INTENT boundary. This is static control flow, not proof that all dispatched failures take that branch. | V4-B.5 must preserve exception order, durable dispatch boundary and original quarantine. A custody failure must not make those actions impossible while the use remains RESERVED. | D4:165; R/runtime/worldline/protected_root_worker.py:170-171,191-199; R/runtime/worldline/protected_operations.py:749,767-775 |
| NF4-2 | VERIFIED_STATIC_ROUTING_CONSEQUENCE_QUALIFIED | Every selected non-owner invocation routes to RootWorkerFront when attached; the listed workload operations are refused/quarantined by the serial path. The root path has no corresponding workload guard. This supports the selected invocation-path observation, not a whole-program proof that no scoped launch exists elsewhere. | Restoring the serial guard corrects DF-3 but would refuse workload operations on the draft's only selected non-owner route. It cannot count as preserving all original required accepted workload cases. | D4:166; R/runtime/worldline/protected_operations.py:719-745; R/runtime/worldline/protected_root_worker.py:162-179 |
| NF4-3 | VERIFIED_STATIC_RETAINED_SEED_NOT_RECOVERY_PROOF | The retained intent includes root_native and original_native_use; the referenced EXECUTION_NATIVE includes material, observation and provenance. Worker current capture requires that exact root_native event and ROOT_READY_CONJUNCTION. The abbreviated :105-109 reference is protected_root_observation.py, not protected_root_worker.py. | V4-G.3 can reconstruct a seed before HANDLER_TERMINAL, but authentic current physical/closure evidence and legal settlement still require separate evidence. | D4:167; R/runtime/worldline/root_worker_custody.py:125-133,178-185; R/runtime/worldline/protected_root_observation.py:105-117,157-164; R/protected-root/worker_entry.py:36-45 |
| NF4-4 | VERIFIED_STATIC_FULL_PATH_MAPPING_SCOPE | Every maps line with a pathname beginning '/' is source checked with INTERPRETER/EXECUTABLE/EXTENSION/DATA roles, without an execute-permission filter; exe has INTERPRETER/EXECUTABLE roles. | R4-3/R4-23 correctly restore the original file-backed mapping scope. NC-P3 exclusions must remain explicit; subset coverage is not proof that no unlisted dynamically executed bytes exist. | D4:168; R/runtime/worldline/root_worker_process_capture.py:69-88 |
| NF4-5 | VERIFIED_STATIC_ABSENCE_IN_SELECTED_SOURCE | The only selected-source occurrence of initial_event is the exact genesis key set. No selected producer/consumer was found. Absence is limited to that source tree. | Defining v2 initial_event null is justified, but the empty-chain head must be consistent with the carried DDL foreign key and native origin representation. | D4:169; R/runtime/worldline/root_worker_journal.py:43-45; bounded rg over R/source for initial_event |
| NF4-6 | VERIFIED_STATIC_RELATIVE_KEY_AND_PREFIX_LIMIT | The issuer key is selected beneath descriptor authority_root, and head MAC covers head plus genesis. A self-consistent retained prefix and its head have no external monotonic comparison in this loader. | V4-C.2 correctly limits self-MAC authenticity and all-history rollback. Boundary cross-reference checks detect only rollback behind references retained elsewhere, not every valid earlier prefix. | D4:170; R/runtime/worldline/root_worker_journal.py:50-53,98-113 |
| NF4-7 | VERIFIED_STATIC_TOOL_SELECTION | The stated exact native_components keys and tool lookups/value membership are present. | R4-16/R4-37 and V4-J.2 correctly enumerate the selected tools without replacing v1 command-name/which semantics. Provisioning and runtime resolution remain OPEN. | D4:171; R/runtime/worldline/root_worker_plan.py:18-20; R/runtime/worldline/protected_scoped_resource_runtime.py:73-74,732-735; R/runtime/worldline/protected_resource_runtime.py:171-172 |
| NF4-8 | VERIFIED_STATIC_ORIGINAL_JOB_CANCEL | job.cancel is mutating; validates a world string, reads world and active_jobs_for_world, raises NO_ACTIVE_JOB for an empty set, and calls runner.cancel once for each recorded job/unit. | The source supports custody-owner store access and original job-unit stopping. It does not itself authorize the new M8(c) generation-root stop without equivalent world/job/unit and current authorization evidence. | D4:172; R/runtime/worldline/controller.py:423,811-826 |
| NF4-9 | VERIFIED_STATIC_EXPLICIT_HELPER_FD_FLOW_RUNTIME_COMPLETENESS_OPEN | The helpers' created pipes/socketpairs are CLOEXEC; explicit actor stdio is dup2'd, and V1 additionally clears CLOEXEC on its custody sender and appends its descriptor number. V3 sends the measurement receiver to the owner and closes its local receiver without reading that frame. An exhaustive actual inherited-FD roster is not established by these lexical excerpts alone. | A changed relaying sub-helper can enforce COMMIT_CHILD only with its own authenticated material/native decision, cost/source/privilege coverage, and fixed event ordering. The READY-then-ABORT contradiction remains. | D4:173; R/protected-root/native_root_worker_supervisor_v1.c:271-291,323-335; R/protected-resource/native_namespace_supervisor_v3.c:265-275,297-305,337-360 |
| NF4-10 | VERIFIED_STATIC_EXCEPTION_BOUNDARY | recover_committed at EFFECT_OBSERVED/SETTLED and EFFECT_INTENT+RESULT_CAPTURE is outside the branch try handlers. Broker/owner/K4 recovery catches WorldlineError into unresolved. | R4-53 and RT-21/RT-22 correctly preserve that startup exception boundary; new recovery must not reinterpret the original refusal as successful settlement. | D4:174; R/runtime/worldline/protected_operations.py:355-384 |
| NF4-11 | VERIFIED_STATIC_STATUS_MUTATION | status is registered mutating; a dirty store with a reconciler triggers recapture. WorldlineError is reported as degraded status, with store meta updates. | V4-L must preserve genuine status semantics and original dependencies, while demonstrating that its added handoff/UNKNOWN/queue waits do not remove responsiveness. | D4:175; R/runtime/worldline/daemon.py:84,407-422 |
| NF4-12 | VERIFIED_STATIC_SCOPED_LAUNCH_ORDER | RECORD_LAUNCH_INTENT precedes DISPATCH_INTENT and systemd dispatch; RECORD_RUNNING follows accept_held. | R4-59/R4-61 correctly repair E3/E6 ordering. Helper READY commit and native gates remain separate open integration obligations. | D4:176; R/runtime/worldline/protected_scoped_resource_runtime.py:739-769; D4:R4-59,R4-61 |
| NF4-13 | VERIFIED_STATIC_DDL_KIND_OMISSION_REPAIR | The carried graph includes FRONT_RECONSTRUCTION -> FRONT_OWNED(g+1), and v3's event-kind CHECK lacked FRONT_OWNED. R4-29 adds it. | The event-kind omission is repaired; the product transition, owner projection, native encoding and complete DDL-to-Next correspondence still require a precise mapping. | D4:177; D2:1000; D3:1316-1323; D4:R4-29 |

The absence result for NF4-5 is limited to the selected source tree. NF4-1 is conditional on the owned object being returned, and NF4-9 establishes explicit helper-created descriptor flow, not an observed complete kernel FD roster. No runtime, kernel, CPython or commit outcome is inferred from these reads.

**4. Original acceptance, changed behaviour, RQ-1 and RELAY/queue**

**workload refusal — NOT_ESTABLISHED_BEHAVIOUR_NEUTRAL; temporary containment only.**
DF-3's historical serial exception-order repair is preserved. It does not authorize a permanent workload refusal. The guard adds a refusal on the draft's selected root route and leaves the required dynamic child/Codex/AgentRunner accepted cases unimplemented. Specify an additive genuine dispatcher and original-positive correspondence before claiming no accepted case changes. Evidence: D4:1013-1024,1039,1851; AUTHOR-NOTES.md:77; R/runtime/worldline/protected_operations.py:723-745,767-775; R/runtime/worldline/protected_root_worker.py:162-199; P1/HANDOFF.md:91-93,115,125-131; complete-phase1-prompt.txt:32-34.

**rq1 windows — PARTIALLY_CLOSED.**
| Window | Assessment |
|---|---|
| W0 | Correct native stale-context refusal at Reserve; original no-row/no-hold mapping needs per-command producer correspondence. |
| W1 | Retained_Join, unchanged C1 and frame-local history are retained; current original gates and actual-cost proofs remain required. |
| W2 | Same native Launch_Intent refusal site, but adding launch to a previously in-process handler does not establish the same accepted operation, new quarantine/K4 cost or legal no-launch return. |
| W3 | Correct native Running refusal and no-GO uncertainty consequence. R4-48 requires ABANDON for a capture failure, whereas M8(a) limits that requirement to the handoff window; the carried ABANDON edge starts only at TRANSFER_SENT/ROSTER_EVIDENCE. Preserve the original pre-handoff failure stop and specify a legal pre-transfer handoff failure route. The inserted launch/currentness dependency still needs operation-specific original correspondence. |
| W4 | The three Context_Changed guards cease after Running; this is not a claim that every subsequent original/current gate disappears or that added custody/costs are absent. |
| W5 | A head-only change is not Context_Changed for those guards. Native Current_Valid, operation/canonical and physical gates still apply. 'normal/none' and all-window durable/cost equality overstate what the table proves. |

Maintain the original Retained_Join and original scoped commands. Complete original accepted/refusal, U/P recovery and exact-cost mapping for each operation and window without removing the workload positives. Evidence: D4:1026-1039; R/core/resource_scoped_run_ledger.ads:426-441; R/runtime/worldline/protected_operations.py:742-768.

**m8 cancel — HOLDS_SAFETY_PRESERVED; ORIGINAL_STOP_AUTHORITY_AND_BEHAVIOUR_NOT_ESTABLISHED.**
An original authorized cancel looks up the current world and active job/unit roster, returns NO_ACTIVE_JOB when empty, and cancels recorded job units. M8(c) substitutes a front stop of a generation's root without supplying native evidence of that same current request/world/job/unit authorization while store custody is unavailable. ROOT_STOP_INTENT durability supplies retention, not authority. Keep clause 12.3's no-settlement/hold rule closed; cancellation correspondence and response progress remain OPEN. Existing D-7a covers any concrete original owner-policy alteration; no new approval gate is created. Evidence: D4:1383,1767-1780; D4:R4-48,R4-49; AUTHOR-NOTES.md:71; R/runtime/worldline/controller.py:811-826.

**relay queue — PROMISING_PARTIAL_REPAIR; NEW_PROTOCOL_AND_LIVENESS_DEPENDENCIES_OPEN.**
Specify exact authenticated per-gate request/generation/subgeneration/operation/gate/head/response binding, freshness and error propagation, native ABI and cost. Distinguish original RequestPeer re-read errors, which remain original errors, from an unavailable correspondence transport, which may queue. Provide a legal persisted fallback from declined RELAY and the original-response path; prove all own/transferred/retained/historical gates are covered. Optional namespace/cookie/provider records must remain optional. Root ACK requires its distinct pre-worker-owned admission relation. Queue wait must preserve original accepted response progress; progress notices are not completed responses. Evidence: D4:1338-1343,1520-1548,1572-1598,1604-1634,1764-1792; AUTHOR-NOTES.md:73,79.

**accounting g — UNSELECTED; DOES_NOT_MEET_FIXED_TARGET.**
G separates request workload unit accounting but leaves handler work in the coordinator under the first root's limits. AO-6/AO-11 remain unsatisfied, as the design admits. No operator selection may waive independent grants, exact kinds/amounts/costs, immutable bounds, no double count, physical enforcement or original responsiveness. F's bound increase and SET_ROOT_CEILING are correctly withdrawn. Evidence: D4:1146-1176; AUTHOR-NOTES.md:74; P1/HANDOFF.md:125-131.

**escrow read copy — CANNOT_SUPPORT_STATED_FRONT_CRASH_REATTACHMENT.**
A process-local ClosedFrontEscrow copy dies with the front. Durable P/W or identity metadata cannot recreate a pipe after the only owning processes die; rows B/C and host-as-front-crash claims need correction. A concrete surviving custodian, if designed, needs complete source/authority/FD/cost/reaper coverage. Otherwise retain explicit irrecoverable UNKNOWN without claiming continuity or successful recoverability. Retained read ends do not control EOF, but their effects on writer broken-pipe/backpressure must also be measured and mapped to original behaviour. Evidence: D4:1463-1506; D2:1043-1047; AUTHOR-NOTES.md:75; R/runtime/worldline/root_worker_closed.py:19-37.

**armed intervals — PARTIAL_REPAIR_WITH_ORDERING_AND_FOLD_ERRORS.**
Durably arm before enabling any transport/read. Reattach step 3 currently starts a reader before step 4's ARMED. Recovery must fold ARMED/chunk/DISARMED intervals: a last chunk record does not imply the preceding ARMED interval closed. A post-read/pre-fsync crash must never receive PASS. Specify real kernel kcmp operands and custody evidence; an identity record is not an open fd. Evidence: D4:1463-1481; D3:1468-1474; R/runtime/worldline/protected_scoped_supervisor_v3.py:482-493.

**child subhelper — ADDITIVE_NATIVE_SURFACE; COMMIT_PROTOCOL_CONTRADICTS_EXCLUSIVITY.**
Native self-decision and relayed credential-byte/ancestry binding are useful, with unproved C/native cost and ABI obligations retained. A worker commits CHILD_READY before the helper may disagree and commit CHILD_ABORT, though exactly one is allowed. Introduce a non-authorizing candidate/decision stage or another coherent exclusive commit protocol, retaining actor-not-executed negatives and genuine successful exec. Make collector/current-owner terminal commits legal outside the blanket WORKER_OWNED condition. Evidence: D4:1186-1227; D4:R4-64; AUTHOR-NOTES.md:76; R/protected-resource/native_namespace_supervisor_v3.c:265-275,358-360.

**custody product — INCOMPLETE_TRANSITION_RELATION.**
Project the root graph independently from REQUEST/DRAIN subjects; define each Legal/Next/owner transition. Reconcile r1 with r3' and supply never-launched release/return without CLOSED. Express r6 as the closure barrier rather than forbidding all live Intake. R4-48's global capture-failure ABANDON rule conflicts with M8(a)'s handoff-window qualifier; ABANDON currently starts only in TRANSFER_SENT/ROSTER_EVIDENCE. Define the original pre-handoff stop and the pre-transfer handoff failure transition explicitly. Specify replay of a committed intent whose physical command or response was not yet completed, without duplicating uncertain effects. Evidence: D4:1324-1401; D2:974-1002,1053; R3-11 as bound by D4:183-214; D4:R4-47,R4-48; R/runtime/worldline/protected_root_resource.py:108-114,142-147; R/runtime/worldline/protected_root_supervisor.py:346-362.

**caps and storage — UNBOUNDED_NATIVE_TO_STORAGE_CORRESPONDENCE_OPEN.**
Q.Quantity generation/subgeneration and optional Position have no bound; the proposed mapping says SQLite INTEGER and seq INTEGER PRIMARY KEY. Integer storage and rowid are finite; non-primary INTEGER affinity alone does not forbid a BLOB, but no exact alternate representation/validator/order mapping is supplied. The inherited v1 rowid limit is an open native-representability obligation, not permission to cap the new domain. Supply a lossless full-domain encoding, fold/replay/order semantics and exact representation for Before_Unknown, Stop_Intent, Mode and carried_from. Do not accept integer overflow/rounding/native failure as a new refusal. Evidence: D4:1285-1304,1368; D3:1307-1368; AUTHOR-NOTES.md:78; P1/HANDOFF.md:125,129-131; SQLite official datatype3.html:74-83 and lang_createtable.html:260-265.

**assumptions and native json — OPEN_PREMISES_ARE_NOT_DISCHARGED_REQUIREMENTS.**
P-A1..P-A4 and coordinator-compromise exclusions do not establish authentic producer/currentness/confinement. Cross-references detect rollback behind recorded references only, with a tolerated append interval, not every older valid prefix. Decimal_Value as an exact rational lacks an explicit signed-zero channel; the named accepted -0.0 control requires it. Complete native Repr/rounding specification and costs on the installed-match domain. RC-6 must decide drops only after preserving all original handler needs. Specification-only L-RB-4 audit does not replace every called-body/reference/native-cost obligation. Evidence: D4:1061-1081,1095-1104,1231-1259,1802,1844-1851; AUTHOR-NOTES.md:70,80; complete-phase1-prompt.txt:32-34,64.

**controls and acceptance — NO_RETIRED_CONTROL_OR_LEAD_ONLY_ACCEPTANCE_FOUND; SUBSTANTIVE_GAPS_REMAIN_OPEN.**
All original fixtures, finite and full-domain controls, frontier v1 bytes/domain, ordinary/lifetime roster, sole C_API boundary, protected floor, zero unproved/justified/Assume and native bodies/costs are retained. New controls are additive and unrun. Defect containment/refusal and conditional waits cannot be counted as original completion. No source, proof, phase or production acceptance is granted. Evidence: D4:1696-1698,1800-1852; D4:110-139; R/protected-startup/controls/test_protected_startup_v1.py:97-105; P1/HANDOFF.md:161-167.

The serial workload refusal is a named unintegrated-lane refusal. Restoring it is not acceptance of a smaller protected API. A temporary refusal leaves the original genuine fork/race/revalidate/simulate/ghost/root/init dispatch obligation OPEN; the design must not claim that its current root path preserves every original accepted case. M8(c) likewise needs original current active-job/unit authorization and response correspondence; ROOT_STOP_INTENT retains the intention but does not grant authority.

No control retirement, accepted native-failure class, new selected accounting cap or new lead-only acceptance was found. The unbounded native/storage join, native number semantics, optional-presence contracts and added queue waits are still unfinished; documenting them does not fulfill the target. P-A1 through P-A4 are explicit premises kept OPEN. Their exclusions must map to the original trust boundary or remain unaccepted dependencies; this review neither broadens nor narrows the original threat/domain requirements.

**5. Sealed C-API v5/v6 integration**

CAPI5’s sealed design verdict is ENDORSED_WITH_REQUIRED_CHANGES. CAPI6’s sealed design verdict is ENDORSED; its fixed capture and sole WF-X repairs close at design level only. Implementation, stage reviews, invariant controls, installed resolution, full strict/native evidence and ROOT_WORKER_INTEGRATION remain OPEN. The seals’ hashes, byte sizes, modes and model/different-author fields all verify. Evidence: D4:1708-1713; CAPI5R/review.json:required_changes; CAPI6R/review.json:rc_closure,rulings,open_obligations.

| Rule | Assessment |
|---|---|
| U-1 | Correct append-only full routine/removed-name discipline and effective root/simple-name definition. Complete the owning-On-unit checkview as well. |
| U-2 | Correctly forbids modifying old qualified rows to fit new RW names and applies (d1)-(d4) to pair plus parent; an already-listed simple selector does not itself change that census. |
| U-3 | Correct all-prefix with-clause restriction, parent check, unchanged use inventory, no separate and new-scope-only qualified inventories. Old-scope exemptions remain exact. |
| U-4 | Sound fixed wfx roster over effective gate union, RW bool/case only, no new assignment exception. |
| U-5 | Sound fixed CAPI_GATE_EXCLUSIVE keys and PK-1 protocol/parent-spec constants; RW has no exclusive table. |
| U-6 | Sound old table byte identity at RW stages and append-only new RW tables. The check's effective scopes/layout/tile/owning-unit views must be distinguished explicitly from those immutable CAPI base tables. |
| U-7 | GE1-GE9, residuals, diagnostics, old S5 renamings and clause tuples retained unchanged. |
| U-8 | Full predecessor stage floor and dependency chain retained; implementing a stage/check remains OPEN. |

| Control / IC | Assessment |
|---|---|
| MX-RW1 | Correct negative design target: added RW wfx violates CR6. |
| MX-RW2 | Correct negative design target: added exclusive-map key violates CR6. |
| MX-RW3 | Correct negative design target: RW gate kind outside bool/case must refuse. |
| MQ-RW1 | Correct named-descendant/prefix capture negative under (d2). |
| MQ-RW2 | UNDERSPECIFIED_EXPECTED_REFUSAL: if the RW selector is already an effective simple name and its root already an effective root, reobserving an unchanged old context can give exactly the same old row. The CAPI5 definition explicitly includes Decide. The control must ensure a newly added selector creates a new census member, or mutate a concrete old-scope call/path; include a positive case for an already-listed selector with old rows unchanged. |
| MQ-RW3 | Correct nested effective-root declaration negative under (d1). |
| MQ-RW4 | Correct separate negative under (d4). |
| MQ-RW5 | Correct unlisted use-clause negative under R-INV. |
| PX-RW1 | Required unchanged old-table/context positive; unrun. |
| PX-RW2 | Required ordinary new-scope bool/case positive; unrun. |
| IC-13 | Required all-old-scope reobservation with effective names at each stage; unrun. |
| IC-14 | Required byte identity of all fixed CAPI base tables at each stage; unrun. |
| IC-10 | Installed name/overload/transported-clause legality remains OPEN; no compiler/prover run here. |

V3-REQ-K is PARTIALLY_CLOSED. Define an explicit effective joined checkview for the owning On-unit roster, qualified scope attribution and appended layout/tile sets while retaining every CAPI base-table byte. CAPI5's carried qualifier check tests each routine prefix for membership in CAPI_SPARK_UNITS, and V4 adds RW_ROUTINE_NAMES but supplies no explicit corresponding effective owning-unit map; derive it from a reviewed enrolled RW unit roster, not from the candidate name alone. Repair MQ-RW2's stimulus/expected relation without narrowing any existing qualified/gate rule or C-API row. Evidence: D4:1719-1726,1732-1743; D3:1744-1768,1779-1833; CAPI5/APPENDIX-BINDINGS.md:185-199,347-381; CAPI6/APPENDIX-BINDINGS.md:97-103,391-425; CAPI6/DESIGN.md:319-324; S5/core/worldline-c_api.adb:879-881,1024-1027; CAPI4/APPENDIX-BINDINGS.md:1529-1541.

The MQ-RW2 issue is a static predicate comparison: R-QUAL collects qualifiers by its effective simple-name set. Decide is already in that set. Adding a disjoint full RW routine under an already effective root with that same selector can leave every old qualifier row unchanged. Occurrence of the selector alone therefore does not imply U-2 failure. This needs a precisely targeted negative stimulus and an unchanged-context positive, not a broader refusal or an edit of an old row. The carried check’s owning-unit test also needs the corresponding effective reviewed RW unit view. Evidence: CAPI5/APPENDIX-BINDINGS.md:193-199,350-381; D4:1719-1724,1736.

RW wfx rows and RW exclusive-map keys remain forbidden. CR5/CR6 still use the fixed CAPI_WFX_PROTOCOL independently of mutable gate/tile rows; the only staged exception remains the sealed G21c/Finalization_Decide/O identity. All-prefix with checks, parent-spec checks, no separate, GE1-GE9, residuals, old S5 package renamings, existing clause tuples and the full stage floor are preserved. Neither lane’s acceptance or integration order is decided. Evidence: D4:1721-1726,1732-1743; D3:1744-1833; CAPI6/APPENDIX-BINDINGS.md:97-103,391-425; S5/core/worldline-c_api.adb:879-881,1024-1027.

**6. Operator reservations and lead checks**

| Item | Ruling | Reserved responsibility | File:line evidence |
|---|---|---|---|
| OP-1 | WITHIN_RESERVED_SCOPE | D-2a: authoritative state provisioning or installation, including descriptor/custody/operation head/crosswalk/plan/configuration and any privileged lab installation | D2:1926; D4:118,1665-1692 |
| OP-2 | WITHIN_RESERVED_SCOPE | D-2b: frontier re-enrollment adjudication; none proposed | D2:1927; D4:131,1696-1698 |
| OP-3 | WITHIN_RESERVED_SCOPE | D-4a: authoritative resource-policy selection; none selected. Choice cannot weaken the original fixed obligations. | D2:1928; D4:120,1155-1176 |
| OP-4 | WITHIN_RESERVED_SCOPE | D-5a: delegation/profile installation and privileged lab action; Luna high is only the actor in the existing adapter | D2:1929; D4:121,1259,1821 |
| OP-5 | WITHIN_RESERVED_SCOPE | D-5b: privileged successor-helper installation/execution | D2:1930; D4:122,1212,1259 |
| OP-6 | WITHIN_RESERVED_SCOPE | D-7a: original API or owner-policy alteration. No concrete change is approved by the brief or this review. | D2:1931; D4:124; D4:1383; item-4 M8(c) finding |
| OP-7 | WITHIN_RESERVED_SCOPE_RANGE_REPAIR_COMPLETED | D-8b: original and additive kernel measurements, now K-1 through K-23, in an authorized lab | D2:1932; D4:222-227,254-259,137,1814-1819 |
| OP-8 | WITHIN_RESERVED_SCOPE | D-9a: original applicable fault campaigns within the existing specialized-validation boundary | D2:1933; D4:127,1839; P1/HANDOFF.md:163 |
| OP-9 | WITHIN_RESERVED_SCOPE | Merge/tag/release/install/sudo/production/real PRIME; draft engineering publication remains separately governed by existing authorization | D2:1934-1939; P1/HANDOFF.md:165-166 |

No added, lowered or widened operator decision was found. Preserve every reserved one. M8(c) must meet original authorization correspondence or receive the already-reserved concrete owner-policy adjudication, without treating a review finding as new authority. Evidence: D4:110-139,1814-1821; D2:1926-1939; P1/HANDOFF.md:165-166.

| New item | Owner / disposition |
|---|---|
| K-22 | Same OP-7/D-8b reservation. EOF/write-copy question retained. The new read copy's writer/backpressure effects require evidence within this same reservation; no new approval item. |
| K-23 | Same OP-7/D-8b reservation. Child-PID-namespace signal reachability is unmeasured, not an assumed guarantee. |
| RC-5 | Lead-owned installed CPython encoding characterization; unperformed here; ordinary engineering check does not become an operator approval gate. |
| RC-6 | Lead-owned static original-handler privilege/IPC/path/syscall inventory; any traced run needing root remains OP-4. This cannot silently drop a used capability or original accepted handler case. |

D-13 and N-06 are carried pre-existing C-API material-architecture/deployment reservations, not new root-worker gates. G-CAPI/G-CAPI-P/G-PROT/G-RW are engineering review dependencies, not operator approvals.

**7. Additional contract/domain/control/native/proof concerns**

| Concern | Finding | File:line evidence |
|---|---|---|
| genesis head | Fresh provisioning inserts no events but a non-null head.event_id equal to a genesis-origin digest while the carried DDL requires that id in events. The original connection enables foreign keys. Specify a genesis-or-event head representation without disabling the foreign-key/history check or inventing an event the initial-state fold does not allow. | D4:1666-1683; D3:1365-1368; R/runtime/worldline/root_worker_journal.py:78-98 |
| genesis encoding | The file is canonical JSON while the row stores the typed archive. Startup must compare the canonical decode/archive relation, not byte-equal unlike encodings. The original loader compares archive(self.genesis) with the row. | D4:1665-1669,1678; R/runtime/worldline/root_worker_journal.py:39-48,96-98; R/runtime/worldline/root_worker_codec.py:19-27 |
| migration path | A closed old v1 journal stays in place while v2 exclusively creates a new database at plan.handoff_journal. Specify the changed plan path/digest and the retained old plan/loader context; same-path exclusive creation cannot do both. No implicit migration or re-genesis. | D4:1651-1654,1664-1671,1689-1692 |
| storage | root_state.generation INTEGER PRIMARY KEY and events.seq INTEGER PRIMARY KEY are rowid-backed finite integers, whereas native Generation/Subgeneration/Position have the original arbitrary quantity domain. Full lossless representation/order/replay and the missing state-field projections remain OPEN. Non-primary INTEGER affinity is flexible; that alone supplies no chosen canonical big-quantity encoding. | D4:1285-1304,1368; D3:1307-1358; AUTHOR-NOTES.md:78; P1/HANDOFF.md:125,129-131 |
| witness carriage | W2'/W8', positive N and split Rebase laws improve the specification. The compaction input union must explicitly include the newly chosen form-(b') span as well as original spans whenever text constants still require compaction. The carried 'three forms' and original-packet-only union must be amended or precisely scoped. Every called body, new successor, invalid span and full original native cost remains required. | D4:960-975,1000-1009; D3:825-832,875-879; AUTHOR-NOTES.md:80 |
| consumer and native floor | The specification graph is improved and the original proof/control floor retained. Several consumer ABI/export/material rows are schematic; HMAC/JSON/child/helper/native parser bodies and exact native runtime/representability/cost correspondence are unwritten/unproved. Dependency order or static identity supplies no producer/body/control/acceptance credit. | D4:845-881,895-948,1101-1104,1223-1227,1831-1838; P1/HANDOFF.md:119,125-131,161-164; complete-phase1-prompt.txt:32-34,64-66 |
| process disclosure | The author disclosed reading the lead's transcript against instructions and reports using nothing from it. This reviewer read only the designated disclosure/author notes, no transcript. That report is model prose and does not prove absence of influence; the static design findings here come from independently read bound files. The deviation remains disclosed and does not create an approval gate or any acceptance credit. | WT/deviations/seam-v4-author-process/NOTE.md:19-31; AUTHOR-NOTES.md:28,66 |

FIXED_AND_OPEN. Preserve original raw/producer domains, fixture bytes, accepted cases, controls including v1 frontier, original API/Optional_Marker policy, exact native quantities/costs, sole C_API boundary, strict full body/reference/caller/flow/RTE/termination scope, protected floor and zero unproved/justified/pragma Assume. Any partial implementation, temporary refusal, conditional queue, native allocation failure or premise remains an engineering gap. Evidence: D4:1800-1852; P1/HANDOFF.md:119-131,155-167; complete-phase1-prompt.txt:32-34,64-78.

SQLite’s documented rowid/INTEGER PRIMARY KEY is a signed 64-bit integer; an ordinary non-primary INTEGER-affinity column can use other storage classes, but that does not supply the exact native encoding here. The design must specify it, including generation and all state projections. This is an inference from the proposed DDL and the [SQLite CREATE TABLE documentation](https://www.sqlite.org/lang_createtable.html), with the flexible-affinity qualification from [SQLite datatypes](https://www.sqlite.org/datatype3.html). No SQLite instance or target database was opened or executed.

JACKAL arithmetic only: status=exact, parsed=2^63-1, exact=9223372036854775807. Assurance: exact rational arithmetic (not yet checker-covered). formal=false; lane=rat. This is informational about the integer bound only and supplies no code, storage-encoding or installed-runtime proof.

- NOT formal-bounded: this lane carries no Lean-checked certificate
- The epistemic class above is the STRONGEST claim this result supports
- exact rational arithmetic (not yet checker-covered)

The author’s transcript exposure is preserved as a disclosed process deviation. The author reports using nothing from it; that model report is not evidence of no influence. I independently read only the designated note and bound source/design/review files, and read no transcript. No new approval gate or acceptance credit follows. Evidence: WT/deviations/seam-v4-author-process/NOTE.md:19-31; AUTHOR-NOTES.md:28,66.

**Required changes for v4**

**V4-REQ-A.** Complete every consumed typed native/producer/C-wire/export contract and its dependency edge in V4-A, including exact current observation, HMAC, requester, child and mutation operands. Keep V1 fallback additive and retain every original route/fixture/reference.

Reason: The corrected waves and names improve the graph, but schematic ABI/export/material cells are not complete contracts and cannot establish a faithful caller or full native cost. Evidence: D4:845-948; D4:883-887; P1/HANDOFF.md:119,125-131,161.

**V4-REQ-B.** Make the carried witness forms and compaction union include every selected witness span, including N. Complete RQ-1's original-operation W0-W5 accepted/refusal, U/P recovery and exact-cost correspondence. Preserve exact serial guard/exception/dispatch boundaries while supplying the genuine workload dispatcher; treat the current root workload refusal as an OPEN containment gap.

Reason: Frame-local W2/W8 and split rebasing repair prior contradictions, but the original-packet-only compacted union and carried three-form wording remain ambiguous. Adding root launch/custody checks before a handler does not preserve original acceptance/cost merely because the native refusal point is unchanged. The restored guard rejects the draft's selected workload route. Evidence: D4:960-1009,1013-1039; D3:825-832,875-879; R/runtime/worldline/protected_operations.py:723-768; R/runtime/worldline/protected_root_worker.py:162-199; P1/HANDOFF.md:91-93,115,125-131.

**V4-REQ-C.** Retain the lexical sign needed for accepted signed zero; specify native Number_Canonical/Repr/rounding/archive extraction and full costs on the matched original domain. Bound the rollback statement and its control to recorded cross-reference coverage, including tolerated append windows. Keep selection/currentness/producer/confinement premises as OPEN obligations without excluding any originally required case.

Reason: The exact-rational Decimal_Value intermediate has no explicit signed-zero channel, while -0.0 is a required positive. Repr is left as an installed CPython definition. Relative-key MAC consistency and selected boundary references do not establish authentic latest state or detection of every earlier valid prefix. Evidence: D4:1047-1104,1802,1846; AUTHOR-NOTES.md:70; R/runtime/worldline/root_worker_journal.py:50-53,98-113; complete-phase1-prompt.txt:32-34.

**V4-REQ-D.** Supply a faithful accounting alternative and complete the original kind/grant/owner/amount/plan/cost/epoch/physical/native-cost comparison against AO-1 through AO-11. Keep G unselected until its handler enforcement gap is solved. Preserve immutable outer bounds, independent request grants, no double count and original response progress; D-4a cannot waive them.

Reason: The matrix explicitly contains no option meeting every obligation. G separates workload units while coordinator handler work still shares the first root's limits. Qualitative decision/process cost labels and ledger checkmarks do not close full native or enforcement correspondence. Evidence: D4:1144-1176; AUTHOR-NOTES.md:74; P1/HANDOFF.md:125-131; D4:1764-1792.

**V4-REQ-E.** Provide one consistent CHILD_READY/CHILD_ABORT commit protocol with native sub-helper agreement before an authorizing exclusive decision and before actor exec. Permit collector/current-owner terminal commits in their legal phases. Complete helper command material, exact ABI/source/native-cost and process FD/argv/env/cwd/privilege surfaces, preserving every original used handler facility under RC-6.

Reason: CHILD_READY is durable before the sub-helper can disagree, and disagreement requires CHILD_ABORT although exactly one may commit. The blanket WORKER_OWNED requirement also excludes the collector named for terminal settlement. Native self-decision improves enforcement but adds unproved native ABI/cost surface. Evidence: D4:1186-1227,1231-1259; D4:743-748 (R4-64); AUTHOR-NOTES.md:76; R/protected-resource/native_namespace_supervisor_v3.c:265-275,358-360.

**V4-REQ-F.** Define the complete orthogonal root/request/descriptor Legal/Next/owner relation, reconcile r1/r3' and express r6 as the closure barrier. Reconcile R4-48's capture-failure ABANDON requirement with M8(a)'s handoff-window qualifier; preserve the original pre-handoff failure stop and define a legal pre-transfer handoff abort. Supply replay recovery for committed intents whose effects or responses are pending. For M8(c), establish the original current request/world/active-job/unit authorization, error and cancellation correspondence before permitting a front generation-root stop.

Reason: The carried root graph mixes subject transitions, the no-launch release has no product return path, and r6 contradicts a live Intake. ABANDON only originates in transfer phases, while R4-48 and M8(a) give different capture-failure scopes. A ROOT_STOP_INTENT is not authorization; original job.cancel cancels recorded active job units after store checks. Evidence: D4:1324-1401,1383; D2:974-1002; D3:326-342; D4:R4-48,R4-49; R/runtime/worldline/controller.py:811-826; D4:1767-1774; R/runtime/worldline/protected_root_resource.py:108-114,142-147; R/runtime/worldline/protected_root_supervisor.py:346-362.

**V4-REQ-G.** Complete the legal Never_Dispatched/Never_Launched release and original-use quarantine/recovery/return route without requiring CLOSED_WITNESS. Retain the corrected original outer barrier and seed reconstruction without HANDLER_TERMINAL. Specify all RT-21 through RT-27 recovery actions with authentic closure/current material, immutable first committed result and original fatal-versus-unresolved exception mapping.

Reason: r3' permits a valid no-launch release but r1 and the carried graph do not admit the resulting state or return. The retained seed and new recovery rows are useful inputs, not a complete reconstruction path, especially after descriptor or serving-owner loss. Evidence: D4:1359-1364,1409-1453; D2:976-1000; R/runtime/worldline/protected_operations.py:355-384; R/runtime/worldline/root_worker_custody.py:125-133; R/runtime/worldline/protected_root_observation.py:105-117,157-164.

**V4-REQ-H.** Make each front/worker/host crash row consistent with actual surviving descriptor custody. Specify any surviving custodian and its complete authority/source/FD/cost/reaper coverage, or mark unavailable pipe recovery irrecoverably UNKNOWN while retaining the original successful controls. Arm durably before enabling reads, fold open intervals across chunk records, and specify real kcmp operands. Preserve last-writer EOF and measure the added read copy's writer/backpressure effects.

Reason: ClosedFrontEscrow is process-local and cannot retain the front's pipe after that front dies; durable P/W cannot recreate it. Reattach starts a reader before ARMED, and last-record-ARMED detection misses an open interval ending in a chunk. An identity record cannot substitute for a live kernel fd in an OFD comparison. Evidence: D4:1463-1512; D4:1489-1495; D2:1043-1047; R/runtime/worldline/root_worker_closed.py:19-37; D3:1468-1474,1487-1493; AUTHOR-NOTES.md:75.

**V4-REQ-I.** Separate pre-ACK root admission from already-worker-owned request Transfer_Join/Relay_Join and Serving_Join. Complete every own/transferred/retained/historical per-gate operand/head/presence contract, preserving optional providers. Specify the authenticated RELAY frame and per-gate freshness, request/generation/operation/gate/head/response binding, native ABI/cost, legal fallback state and propagation of original re-read errors.

Reason: The root ACK ordering uses a request join whose root-phase precondition is already WORKER_OWNED. Optional corroboration conflicts with unconditional-looking presence fields, and retained/historical coverage is incomplete. RELAY's exact frame/cost is explicitly unspecified; its no-refusal queue does not supply those contracts. Evidence: D4:1524-1634; D4:1338-1343; AUTHOR-NOTES.md:73; R/runtime/worldline/client_peer.py:131-137.

**V4-REQ-J.** Make empty-chain genesis/head foreign-key and native-origin encoding coherent without disabling integrity checks. Compare canonical JSON to its decoded typed archive relation. Specify full lossless native quantity/state storage and fold/order/replay, including root generation keys and every new state field. Define the new plan path/digest and retained old loader context for closed-v1 migration, preserving exclusive create and all history.

Reason: The provisioner inserts an origin head with no events despite head.event_id REFERENCES events. Startup byte-compares JSON and archive. root_state.generation and events.seq INTEGER PRIMARY KEY cannot by themselves represent the arbitrary native domain; non-primary INTEGER affinity needs an explicit exact mapping. A new database cannot be exclusively created over a retained v1 database at the unchanged plan path. Evidence: D4:1285-1304,1368,1646-1698; D3:1307-1368; R/runtime/worldline/root_worker_journal.py:78-113; R/runtime/worldline/root_worker_codec.py:19-27; AUTHOR-NOTES.md:78; P1/HANDOFF.md:125,129-131.

**V4-REQ-K.** Define the effective joined owning-On-unit, qualifier scope/layout/tile and gate checkviews separately from byte-immutable CAPI base tables, using the reviewed enrolled RW roster. Make MQ-RW2 target a newly added census member or a concrete changed old-scope call/path, and add an unchanged-old-context positive with an already-listed selector. Keep every sealed CAPI6 invariant, old row, fixed protocol and no-RW-wfx/no-RW-exclusive-key rule.

Reason: The inherited qualifier check validates each routine's unit against CAPI_SPARK_UNITS, while the design adds effective RW routines without an explicit corresponding owning-unit checkview. Adding a selector already in the effective set, such as Decide, does not by itself change the old qualified census, so MQ-RW2's unconditional expected U-2 problem is not established. Evidence: D4:1719-1743; D3:1757-1768,1803-1812; CAPI5/APPENDIX-BINDINGS.md:185-199,347-381; CAPI6/APPENDIX-BINDINGS.md:97-103,391-425; CAPI6/DESIGN.md:319-324.

**V4-REQ-L.** Complete original status/cancel/owner/quarantine/non-mutating response progress for unreachable workers, missing closure and UNKNOWN, with the full RELAY/collection/executor/storage model. Show authentic events that make each added wait end and legal service/recovery actions without the circular need for an unavailable owner. Preserve original thread placement, short router locks and response semantics; qualify optional QUEUED event compatibility.

Reason: The design withdraws single-thread serialization and router lock waits, but its table lists additional waits rather than demonstrating original accepted service progress. An original workload limit or authorized stop does not itself supply CLOSED/ECHILD/current custody evidence; QUEUED events are explicitly not responses and client tolerance is unverified. Evidence: D4:1753-1792,1383,1624-1626; R/runtime/worldline/daemon.py:84,407-422; AUTHOR-NOTES.md:79; P1/HANDOFF.md:115,127,162-164.

Each required change stays with the original lead designer and independent GPT-6.1 reviewer named in the ruling table, with operator involvement exactly where already reserved. Drafting alternatives, passive source preparation and ordinary installed-runtime checks gain no new approval gate. No required original body, contract, domain, fixture, threshold, accepted case, control or native cost may be reduced to close these items.

**Open obligations and review boundary**

Every OB-001 through OB-219 is OPEN with closure_credited=false. Their original owner, release, dependencies and needsOperator fields match the frozen registry after key-name normalization; original target, closure and test text remain bound by P1/OBLIGATIONS-v2.json and are not rewritten. review.json retains every ID and responsibility. The full matching-source proof/ordinary/lifetime/fault/native/producer/hosted/publication/deployment obligations remain outstanding.

V3-REQ-A through V3-REQ-L, V2-REQ-A through V2-REQ-L and RQ-1 remain partially closed. The old partial RCs remain partial, RC-05/RC-10 and D-2b retain design-only closure, clauses 04.1/07.3 remain not closed, and every other clause/ruling keeps the final status above. CAPI6’s other open requirements, L-CAPI-P/G-PROT/IC-10, schemas/provisioners, unselected accounting, all lemmas and native bodies/costs, all actual measurements and matching controls remain OPEN. Evidence: D4:1825-1840; P1/HANDOFF.md:119-131,155-167.

proof_acceptance=false; phase_acceptance=false; source_acceptance=false. Seven create-only checkpoints preserve the completed numbered-item work. REVIEW.md, checks.json and review.json are created exclusively with mode 0600 and fsync; review-freeze.json is written last and seals exactly those three files.

