# WORLDLINE Phase One: Claude lead status (live index)

As of 2026-10-05 ~04:20Z. This file supersedes the stale status sections of the read-only
`work/claude-workflow-v1/REPAIR-MAP.md`, which stays preserved.

**Every original Phase One obligation is OPEN.** Nothing below is proof, source, native or Phase One acceptance.

## Gates that block proof dispatch (all in force)

| Gate | State | Where |
|---|---|---|
| Confinement / frame qualification | **BLOCKED.** Frame v5 is UNQUALIFIED (final actual gpt-6.1-sol report). V5-B01 requires custody that *prevents* the admitted generation from changing before use. V5-B02 requires enforced location custody for every frame mutation. No qualified unprivileged route has been demonstrated. W-1 (separate writer and target accounts) is the candidate: the package v6 review found W-1 v3 NOT_READY (8 sub-gaps CLOSED, 12 NOT_CLOSED), and W-1 v4 is being drafted. | frame v5 `review/gpt61-v1`; `frame-v6-PLAN.md`; `proposal/ISOLATION-STORAGE-PROPOSAL-v3.md`; `package-review/gpt61-v3` |
| Capacity | **BLOCKED.** Gate 0 (runbook v4.3) requires 9304350902252/1397 bytes above the 10 GB reserve for one unit run. At 04:17:40Z, free − reserve − Required = −9113451232236/1397 (JACKAL exact, formal=false). The vault timers are held for Codex's repository recovery. | `RUNBOOK-first-proof-iteration.md` |
| Operator approvals | None given: no choice, no privileged action. | operator package |

## Storage alert (2026-10-04 20:37Z)

**Observations.**
- Free space was 10592727040 bytes at 20:37:33Z, 592727040 above the unchanged 10000000000 reserve. The backup service
  is still failed.
- The mean decline since 18:49:03Z is 296433664/3255 bytes/s, about 91 KB/s (JACKAL exact, formal=false).
- At that past mean, the reserve is crossed after about 6508 s, roughly 1.8 h. This is not a forecast.
- **20:58:28Z:** free 10558955520 bytes, 558955520 above the reserve. The decline since 20:37:33Z was 6754304/251
  bytes/s, about 27 KB/s, slower than the earlier mean. At that rate the reserve is crossed after 137009605/6596 s,
  about 5.8 h. This is also not a forecast. JACKAL exact, formal=false, for all three figures.

**Where it comes from.**
- Large files modified since 18:49Z include:
  - `~/.codex/thread_history_1.sqlite` (2.3 GB) and `~/.codex/logs_2.sqlite` (540 MB), which every codex exec review
    writes;
  - SIA database files;
  - a 166 MB Codex rollout from a non-lead session.
- The lead's own measurable additions since then are about 100 MB: review-record copies, job scratch, review rollouts.

- **22:06:53Z** (`storage_status.py`): free 10516545536 bytes, 516545536 above the reserve, and `backup_service` is
  still failed. The decline since 21:02:25Z was 8587264/967 bytes/s, about 8.9 KB/s. JACKAL exact, formal=false.

**Lead response.**
- Copies are kept to records.
- The D2, root-worker seam, C-API v3 and D1 v3 reviews have all sealed.
- The instructed package review started at 22:08Z.
- One drafting agent (D1 v4) started at ~22:10Z. Agents are deliberately started one at a time.

**Incident (disclosed).** A `find` over `~/.local` listed file metadata under `~/.local/share/sia/.gbrain/`. That
breaks the machine rule "never access ~/.local/share/sia/.gbrain/ directly". It was metadata only: nothing was read or
written. Future scans exclude that path.

## Independent review verdicts (actual gpt-6.1-sol, sealed, freeze verified)

| Item | Verdict | Next |
|---|---|---|
| Scratch frame v1–v5 | All UNQUALIFIED. v5: V5-B01, V5-B02; the compact identity records and four residuals were ruled acceptable. | W-1 v2 and the frame v6-W1 design continue as routine engineering. Privileged setup needs operator approval later |
| Operator package DRAFT-v4 | NOT_READY (9 required corrections; W-1 "potentially capable … not sufficient as described"; P-1: no operator approval solely for pinning) | DRAFT-v5 and W-1 v2 |
| Operator package DRAFT-v5, DRAFT-v6 | Both NOT_READY (`package-review/gpt61-v2`, `gpt61-v3`). v6: W-1 v3 8 sub-gaps CLOSED, 12 NOT_CLOSED; eight new corrections | DRAFT-v7 with W-1 v4, then re-review |
| Composition commonV5-alpha (packets 01, 02, 04) | QUALIFIED_SOURCE_COMPOSITION | — |
| Composition commonV5-beta (+05..09) | QUALIFIED_SOURCE_COMPOSITION (rulings 7a/7b; notes N on packets 05/06 metadata) | — |
| C-API design v2 | ENDORSED_WITH_REQUIRED_CHANGES (RC1–RC6; LD4 rejected as written) | v3 being drafted |
| D1 native design v2 | NOT_ENDORSED (V2-RC1..RC6; RC4–RC7 still open) | superseded by v3 |
| D1 native design v3 | ENDORSED_WITH_REQUIRED_CHANGES (V2-RC1..RC3 and RC4..RC6 CLOSED; V3-RC1 OD-2 codec/census, V3-RC2 controls/fixtures, V3-RC3 checked-cost model; R-OD1/R-OD2 operator architecture choices unselected) | DESIGN v4 drafted ~00:00Z (`3c636847…`); its actual gpt-6.1-sol review started ~00:03Z |
| D1 v4 author findings (unreviewed) | F34: v3's Algorithm B ghost is unrepresentable at n = 804; repaired by DR-C5. F35: Algorithm A's ghost horizon, OPEN. F36: Compare's checked cost is dominant. **F32: an original control (`tests/test_finalization_kernel.py:257-266`) expects AUTHORIZED where the author claims Collapse.Decide gives `Identity_Absent`. Unexecuted claim; original controls untouched** | Under the D1 v4 review. F32 needs integrated execution evidence |
| C-API design v4 | ENDORSED_WITH_REQUIRED_CHANGES (sealed ~02:47Z; gpt-6.1-sol/max from the rollout). V3-RC5 and V3-RC6 CLOSED_AT_DESIGN_LEVEL. V3-RC4 NOT_CLOSED, with two remaining changes: V4-RC4-GATE (reconcile the gate rule set) and V4-RC4-ALIAS (expanded naming invariant for indirect package paths). L1–L8 all GENUINE. D-13 clarified: the reservation concerns the component transport/library architecture, not pin edits | DESIGN v5 drafted (`533f0e04…`, handback ~04:13Z); its actual gpt-6.1-sol review started 04:17Z |
| C-API design v3 | ENDORSED_WITH_REQUIRED_CHANGES (RC1–RC3 CLOSED_AT_DESIGN_LEVEL; V3-RC4 binding spec, V3-RC5 PK-0 effect classification, V3-RC6 cost map NOT_CLOSED; D-13 operator choice on a concrete reviewed packet before PK-7; N-06 at deployment; N-01 lead-owned) | DESIGN v4 |
| Root-worker seam design v1 | ENDORSED_WITH_REQUIRED_CHANGES (RC-01..RC-12; rulings D-1a..D-9a: `Delegate=yes` not endorsed, the frontier control cannot be retired by the lead, native custody-phase legality is mandatory) | v2 |
| Root-worker seam design v2 | ENDORSED_WITH_REQUIRED_CHANGES (sealed ~04:19Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `84c176df…`, REVIEW.md `1a41b5c5…`, checks.json `63a36b12…`, freeze `d40060e5…`).<br>- **Closed at design level:** RC-05, RC-10, D-2b. All other RCs and rulings PARTIALLY_CLOSED.<br>- **Required changes:** twelve, V2-REQ-A..L. V2-REQ-K brings the C-API status up to date.<br>- **Findings:** N-1..N-10 verified or supported statically. N-6 is SUPPORTED_STATIC_CONDITIONAL_RECEIVER_RESOLVED.<br>- **RQ-1:** PARTIALLY_CLOSED: no unconditional FRESH placement; it needs caller-by-caller domain correspondence and Retained_Join.<br>- **Operator items:** OP-1..OP-9 within the reserved scope; no new gate, nothing lowered | Seam v3 (routine lead engineering) |
| D2 checked-Ghost inventory v1 | ACCURATE_WITH_CORRECTIONS (12 corrections, hazard rulings H1–H11; see below) | Corrections carried here and into the package |

## Candidate packets (drafted; untested engineering hypotheses)

| Packet | Content | State |
|---|---|---|
| 10 | resource_ledger additive steps (D1382, D1388) | overlay iter-3-core |
| 11 | run-ledger wire Decode_Native invariants (D1553) | overlay iter-3-core |
| 12 | Iterative body-local witnesses (4 contracts-recursive notices) | overlay iter-3-core |
| 13 | Iterative `Prefix_Tail` in resource_reservation_transition (D1431, D1432) | wt-1 only. Notice removal is an untested hypothesis until matching-source evidence exists. |
| 14 | Chain-authority `Replay` induction lemma plus call-site facts (D1554, D1555) | wt-1 only. Adds checked-build Ghost cost, which is under D2. |

Ledger lineage (`wt-1/workflow`): 3187 items, 3026 OPEN, 161 DRAFTED, 0 verified.

## D2 checked-build cost (static analysis; actual gpt-6.1-sol review sealed)

Source: `wt-1/designs/claude-d2-checked-ghost-inventory-v1` (INVENTORY.md `e5b9984d…`). Everything here is derived
by reasoning; nothing was measured. JACKAL exact, formal=false, for the arithmetic.

**Review verdict: ACCURATE_WITH_CORRECTIONS** (`review/gpt61-v1`, freeze verified). It grants no proof, native or
phase acceptance. Its 12 corrections bind every later use of the inventory:
- **C-PINS.** A concrete change to enrolled pinned text needs O-PINS operator approval, independent review and
  regenerated effective pins. "Body-only, lead-owned" authorizes no change to the pin package, its keyset, or a pinned
  contract or reference.
  - **Provenance (supervision correction, ~21:10Z).** The operator-approval boundary C-PINS applied came from the
    lead's own brief (item 4), not from the original requirements.
  - HANDOFF acceptance-sequence item 1 requires explicit reviewed deltas and recomputed effective pins. "a review brief
    or review finding is not new authority to add approval gates."
  - So no operator approval is requested solely because an implementation file is pinned.
  - Reference semantics, unapproved APIs, contracts, scope, accepted cases, controls and every gate stay reserved and
    unchanged.
  - C-PINS and erratum E1 are preserved. The package review is asked to correct the inconsistency.
  - E1 (`wt-1/errata/d2-inventory-E1-pinned-files.md`): chain-authority and run-ledger files are pinned (169 effective
    keys), so every packet 01–14 touches a pinned implementation file.
- **C-ABI.** A changed public transport code, meaning, layout or caller protocol is an API/ABI package and needs
  operator approval, not "possibly". A clearer failure classification supplies no native acceptance.
- **C-COPY.** Narrowing a Ghost arena snapshot can change the copy's growth class and must keep the whole-arena frame
  relations. Replacing an assertion needs review.
- **C-PACKET-GAP.** Equal-endpoint calls still pay absolute-position Posts. Packet 13's `Prefix_Tail` gains an absolute
  `Prefix_Reference` Post even when First = Stop. The gap-multiplied classes need nonzero-gap qualifications, or the
  base terms must be kept.
- **C-P12-REACH.** Packet 12's witnesses are not reached once per call. One outer mismatch can trigger many nested
  witness evaluations through the unchanged recursive `Prefix_Modulus`.
- **Cost-class corrections:**
  - C-SLOT: the slot term is Θ(N²·S⁴).
  - C-SUM: `Sum` is quadratic; `Contained` is cubic.
  - C-OWNER: owner/retry exported paths are history-dependent.
  - C-EMPTY: empty rosters still pay `Check_Capacity`.
  - C-UNIT: a PR invocation is a call count, not an allocation count.
- **Repairs to the inventory's own description:**
  - C-LOC: the chain C API call is at line 99 and its handler at 102; the run-ledger handler is at 222.
  - C-BASE: the base-to-candidate delta description was incomplete.

**Hazard rulings, condensed:**
- H1 (exponential chain replay) is correct as source-semantic reasoning. No native cost was measured.
- H9: stack and heap layout and exhaustion behaviour are not determined statically.
- H10: a catch-all exception mapping does not make stack or process failure catchable. Neither outcome is an accepted
  refusal.

**Hazards in the checked (`-gnata`, default) build:**
- **Chain replay is exponential.** A successful replay costs 9·2^(n+1)−n−10 reference evaluations: 18412 at n=10,
  19327352792 at n=30. The release build is linear.
- **Resource-ledger compute is Θ(N⁶).** At an 804-byte buffer the checked build raises `Storage_Error`, which the C
  wrapper maps to 255.
- **Quantity references** are Θ(L⁶)–Θ(L⁷).

**Packet deltas, to be weighed before any packet is promoted:**
- **Packet 14** raises the replay cost to 11·2^(n+1)−2n−14. Still exponential, now worse.
- **Packet 13** raises `Prefix_Tail`/`Prefix_Decomposition` costs, Θ(m³)→Θ(m·S³) and Θ(m·S³)→Θ(m²·S³).
  Per C-PACKET-GAP, it also keeps an absolute-position base term when First = Stop.
- **Packet 12** leaves the standalone growth classes unchanged. They remain conditional worst-case classes. Per
  C-P12-REACH, the witnesses can still be evaluated many times inside one outer mismatch.

D2 stays OPEN.

## Executed engineering checks (ENGINEERING_ONLY; no prover or compiler; never acceptance evidence)

| When | What | Result | Where |
|---|---|---|---|
| 23:37:20Z | V5-B01 final-pass self-check. A library import of `observe_tree` on throwaway trees; mutations injected after a file's observation | v6 working copy (`2255d6e1…`): **14/14 as required**. Frozen v5 (`f9f6596d…`): 6/14. v5 accepts 8 post-observation changes, which reproduces V5-B01 | `frame-v6-selfcheck/RESULTS.md` |
| 23:40:21Z | Regression: the unchanged 85-case v5 author self-check, retargeted in memory to the v6 working copy | **85/85, 0 failures**, the same as the v5 baseline | `frame-v6-selfcheck/regression-2026-10-04T234021Z` |
| 23:46:52Z | W-1 kernel DAC probe across genuinely different UIDs. Rootless user namespace on the operator-configured subuid range: writer 100000, target 100001, home stand-in 100002; the lead probes from outside as uid 1000 | **30/30 as required.** The target writes only its partition; `sicarii` and the target cannot mutate frame records, source, generation, `runs` or lease; the lease is exclusive. Renaming the home in a `sicarii`-owned parent succeeds, as expected, which is why W-1 needs root-owned `/var/lib`. **Caveat:** the subordinate UIDs are delegated to `sicarii`, which can always map them, so they are no boundary against `sicarii`. That rules out a rootless W-1 variant, and it adds a W-1 setup check: the new account IDs must lie outside every subuid/subgid range | `frame-v6w1-proto/RESULTS.md` |
| 23:39:12Z | W-1 v2 writer-side mechanisms (prototype `w1proto.py` `2c7d6100…`): lease, chained framing, streamed-input pins, non-dumpable. Same-user simulation | **27/27 as required** | `frame-v6w1-proto/results-2026-10-04T233912Z` |

These show code behaviour on throwaway inputs only. They do not test the separate-account kernel boundary. V5-B01,
V5-B02 and every original obligation stay OPEN.

**Author correction.** W-1 v2 §4.5 understates: the v6 working copy already revalidates excluded leaves
(`scratch.py:554`, `:569-573`). Recorded in `frame-v6-selfcheck/RESULTS.md`. The frozen v2 is not edited.

## RESERVE CROSSED (2026-10-05 03:37Z)

- **Readings (`df`).** Free 8098127872 bytes at 03:37:37Z, and 8096395264 at 03:39:12Z.
- **Derived (JACKAL exact).** That is 1901872128 bytes **below** the unchanged 10000000000 reserve, and 2264367104
  bytes less than at 02:06:26Z.
- **Read-only size readings of named local paths:**
  - the vault's `restic-cache`: 1184994266 bytes;
  - Codex's repair folder: 135204714;
  - `~/.codex/sessions/2026/10/03`: 542287870;
  - `~/.codex/thread_history_1.sqlite`: 2330456064;
  - `workflow-tmp`: 11894682920, essentially unchanged.
- **Attribution.** The per-file share of the drop is not attributed.
- **Gates.** Every Gate 0 stage is far from established. The lead's own additions are small: agent transcripts and
  review records.
- **Decision.** S-1, including option 4 (hold the lead's review and agent work), is the operator's choice.

**Back above the reserve, 04:17:40Z (`df`).**
- **Reading.** Free 10136649728 bytes.
- **Derived (JACKAL exact, formal=false):**
  - 136649728 bytes above the reserve;
  - 2040254464 bytes more than at 03:39:12Z;
  - Gate 0 margin (runbook v4.3) −9113451232236/1397.
- **Attribution.** The source of the increase is not attributed. The lead deleted, moved and offloaded nothing, and it
  took no size reading of vault paths after the handover to Codex.
- **What it changes.** The reading does not change any gate. S-1 stays the operator's decision.

## Backup repository (iPad), 2026-10-05

**Observed.**
- The iPad reconnected at about 02:47Z, and reads work.
- The 03:00Z backup saved snapshots, but every scope's `restic check` fails with 4 missing packs. The lead verified at
  03:16:00Z that all four are absent (ENOENT).

**How far that goes.**
- The missing packs and failed checks are verified.
- That the disconnect caused them is a hypothesis.
- The saved snapshots do not establish a healthy backup or write reliability.

**Ownership changed, ~03:24Z.** The human assigned vault recovery to **Codex**.
- The lead starts no vault inspection, repository command, lock action or timer change.
- The planned packet was not completed. Its script was never run.
- The lead's completed read-only observations, with hashes, are in `backup-repair-packet/` (README and
  `observations/`).
- Codex reports verified vault health when its recovery completes. No offload or proof admission follows from the
  takeover alone.

**Codex's update, ~03:5xZ.** Relayed by the supervisor; reported by Codex, not observed by the lead.
- The original backup scope finished naturally and deferred on the normal maintenance lock.
- Metadata preservation and read-only reference inspection hit I/O errors.
- The iPad then disappeared from the USB bridge and both mounts went offline.
- Nothing has been repaired, forgotten or pruned.
- Recovery records and a partial metadata copy are in `work/backup-repository-repair-20261005`. One missing blob has
  matching local original bytes preserved.
- Repository health is not established. The vault timers are held for maintenance.
- The lead does nothing on the vault, does no offload and touches no iPad mount path (FUSE hang risk), until Codex
  reports verified recovery.

## Package v6 review (sealed ~03:08Z)

**Verdict: NOT_READY.**
- **Closed:** W1-RESOURCES, OD2-CONSEQUENCES, PKG-V5-FACTS, PKG-CLOSURE-STATUS.
- **W-1 sub-gaps:** 8 CLOSED, 12 NOT_CLOSED.
- **Eight new corrections:**
  - six for W-1, being drafted as W-1 v4 by the resumed W-1 author;
  - two package-text corrections, made in DRAFT-v7 (being prepared; not frozen).

## In progress (updated 04:20Z)

- **C-API DESIGN v5** (`designs/claude-capi-boundary-design-v5`).
  - **Author.** The resumed v4 drafting agent handed back shortly before 04:13:55Z.
  - **Files.** DESIGN.md `533f0e04…`, decisions.json `a069632a…`, APPENDIX-BINDINGS.md `f22944b4…`, jackal.json
    `612d189e…`, AUTHOR-NOTES.md `ed45d1db…`. The lead's re-hashes equal the author's report.
  - **What it answers.** V4-RC4-GATE with one branch-sensitive gate rule, and V4-RC4-ALIAS with R-QUAL, an exact per-call
    expanded-qualifier invariant. It also reports latent v4 defects L9–L12. A-COST v4 is carried unchanged by reference.
  - **Lead checks** (engineering only, not review):
    - A lead script re-hashed every carried slice: 20/20 DESIGN slices and 13/13 A-BIND slices equal the v4 bytes.
    - JACKAL re-runs of J62, J65, J66 and J67 reproduced the recorded values: `exact`, formal=false.
  - **Author process.** Recorded in `deviations/capi-v5-author-process/NOTE.md`: a `mkdir -p /dev/null` slip that
    created nothing, Bash commands outside the literal list, and a late `sia.ask`.
  - **Its sketch run.** The author executed the design's own check sketch in memory. The lead judged that an **author
    self-check**: not WORLDLINE code, not evidence, not a control run. The reviewer may not execute the sketch.
  - **Review.** Its actual gpt-6.1-sol review started 04:17:16Z: brief `briefs/capi-design-v5.md` (`ec0472e1…`),
    thread `01a10a47-a6da-79e2-b8e0-a110e9fc7a8a`, output to `…/review/gpt61-v1`.
- **Root-worker SEAM DESIGN v2.** Its actual gpt-6.1-sol review (thread `01a10a26…`, started 03:40:38Z) sealed
  ~04:19Z: ENDORSED_WITH_REQUIRED_CHANGES (verdict table).
- **Root-worker SEAM DESIGN v3.** Drafting started ~04:23Z. The v2 author (`a01ff3579cb09cea3`) was resumed for
  V2-REQ-A..L, RQ-1 and every PARTIALLY_CLOSED item; output goes to `designs/claude-root-worker-seam-design-v3`.
  - **Its limits.** Write/Edit only in that directory; read-only Bash with no redirection, not even `2>/dev/null`; no
    interruption; `sia.ask` at the start; all eight Ada skills; JACKAL in groups of at most four.
  - **C-API status.** It binds the sealed C-API v4 review as the predecessor status and labels any dependence on the
    unreviewed v5 as such.
- **Operator package DRAFT-v7: working copy moved into wt-1.**
  - At ~04:19Z the edit guard refused Edit-tool changes to `work/claude-operator-decision-package-v1/DRAFT-v7.md`,
    which is outside any git worktree.
  - Nothing was routed around the refusal. The lead copied the file byte-identically (sha256 `044ede9f…`) to
    `package-drafts/DRAFT-v7.md` and edits only that copy.
  - The package-directory drafts v0–v7 are preserved unchanged.
  - The working copy now has the 04:17Z storage reading, the C-API v4/v5 status, the D-13 restatement and the seam v2
    verdict. The W-1 summary is still to be refreshed when W-1 v4 lands.
- **W-1 v4** (`proposal/ISOLATION-STORAGE-PROPOSAL-v4.md` `a1924e74…`, 321052 bytes; `v4-support/jackal.json`
  `298caa03…`).
  - **Handback.** The resumed W-1 author handed it back ~04:40Z and reports no refusal, deviation or interruption.
  - **Author's assessment.** All six corrections CLOSED-AT-SPEC-LEVEL, with terminal custody conditional on unverified
    premises that probes P-MGR and P-QUIESCE must check. That is not closure.
  - **Lead checks** (engineering only):
    - both hashes match the report;
    - all six new JACKAL values reproduce `exact`;
    - every section v4 says it carries from v3 has a byte-identical body;
    - §14.3 differs only by the D7→D10 renumbering;
    - the staged Gate 0 figures are unchanged.
  - **A package fact corrected.** Its observation P15 showed three lingering accounts. The lead confirmed it at
    04:43:34Z (`cosmov1lab`, `wlrehearsal`, `worldline`), and the package's "linger only for `worldline` and
    `wlrehearsal`" is corrected in DRAFT-v7.
- **Operator package DRAFT-v7: frozen and under review.**
  - **Freeze.** `package-drafts/DRAFT-v7.md` `96dc07e8…` (73209 bytes) was frozen at 04:46Z with W-1 v4 into
    `package-frozen/`; all copies are byte-identical and 0444.
  - **Content.** F-1 now describes W-1 v4: the target account's masked user manager and its empty-`PAMName=` drop-in,
    the single layout, the S-R reconciliation, and the unverified premises. Storage readings run to 04:45:27Z: 110992384
    above the reserve, Gate 0 −9149294541804/1397, W-1 dispatch stage −15213406340912/1397 (all JACKAL exact).
  - **Review.** Its actual gpt-6.1-sol review started 04:47Z: brief `briefs/operator-package-review-v7.md`
    (`c8189bc0…`), thread `01a10a63-4ab8-7573-a998-209c9ec6fea2`, output to `package-review/gpt61-v4`.
- Actual gpt-6.1-sol review of D1 DESIGN v4 (`designs/claude-native-bigint-d1-design-v4/review/gpt61-v1`).
  - **INCOMPLETE. A tool-layer stall is suspected in its concurrent `exec` batch of `jackal_exact` replays.**
  - The evidence:
    - its event stream and rollout have been unchanged since 00:05:39Z;
    - its processes are in wait states;
    - there are no completed ledger rows for the draft inputs.
  - The evidence does **not** prove that the batch never reached JACKAL, where exactly it is stuck, or that no call ran.
    The ledger is recall, not evidence of nonexecution.
  - It was not interrupted or restarted, as instructed. No checkpoint or result exists, and everything stays OPEN.
  - Corrected diagnosis: `review-monitoring/d1-v4-review-stall-2026-10-05T0040Z.md`. The first version overstated it.
  - Recovery proposal for a human decision (R0 leave, R1 terminate codex only so the runner resumes the same thread,
    R2 a fresh review), not performed: `review-monitoring/d1-v4-review-recovery-proposal.md`.
- **C-API DESIGN v4** (`designs/claude-capi-boundary-design-v4`, DESIGN.md `a9b5dcce…`).
  - The drafting agent finished ~02:05Z. Hashes are verified. It reports latent defects L1–L8, four of them in v3.
  - v3 text is bound as hashed slices.
  - Its actual gpt-6.1-sol review started ~02:08Z (`…/review/gpt61-v1`) and sealed ~02:47Z (verdict table above).
  - The author's process disclosures are recorded in `deviations/capi-v4-author-taskstop/NOTE.md`.
  - **Event, disclosed, by the C-API v4 drafting agent.**
    - At 01:22:20.621Z it ran `TaskStop` on its own timed-out background inspection task `ba0hhwegp`, then finished
      the read with a bounded command.
    - The lead relayed the operator's no-interruption rule to it at ~01:26Z, and to the W-1 v3 author.
    - This grants nothing further. It is distinct from the D1 v4 reviewer, which stays untouched and INCOMPLETE.
    - The note also covers the lead's own two historical `TaskStop` calls (17:00Z and 17:14Z on 10-04, before the first
      no-interruption instruction at 18:29Z), and the `find` the lead ran at ~03:38Z, which its own `timeout 60` wrapper
      terminated.
  - **Correction.** These event lines previously sat, by an editing error, under the root-worker seam v2 bullet. The
    seam v2 agent reported the misattribution. It never used `TaskStop`, and it started only at ~02:10Z.
- **Root-worker SEAM DESIGN v2.** A drafting agent (author role) started ~02:10Z on RC-01..RC-12 and D-1a..D-9a,
  including the shared `worldline-c_api.adb` integration with C-API v4. Output goes to
  `designs/claude-root-worker-seam-design-v2`.
  - Its prompt forbids Bash writes and any interruption of tools.
  - The drafting agent has finished; its review is running (above).
- **W-1 v3** (`proposal/ISOLATION-STORAGE-PROPOSAL-v3.md`, `97f39c89…`, 193544 bytes).
  - Drafted by an author-role agent, which finished ~01:58Z with no refusal, deviation or interruption.
  - It specifies the gate group, `no_new_privs` with an anti-setid seccomp filter, no-ACL recipe modes with exports, a
    root-owned 0440 flock-only lease, commit markers, a fallback journal and launch gating.
  - Its staged Gate 0 proposes 15368462701360/1397 for each dispatch, about 11.0 GB. The lead reproduced it with
    JACKAL.
- **Package v6.** DRAFT-v6 (`106dea2c…`) and W-1 v3 are frozen in `package-frozen/`. Their actual gpt-6.1-sol
  re-review started ~02:12Z (`package-review/gpt61-v3`) and sealed ~03:08Z NOT_READY (section above).
  - The brief asks the reviewer not to interrupt tools and to batch JACKAL calls modestly.
- **Storage at 02:01:52Z.** Free 10370256896 bytes, 370256896 above the reserve.
  - Runbook v4.3 Gate 0 margin: −8787102018540/1397.
  - W-1 v3 dispatch-stage margin: −14851213817648/1397.
  - Both are JACKAL exact. All stages are DEFERRED.

## Earlier progress log

- **Operator package.** DRAFT-v4 review sealed NOT_READY (9 corrections). DRAFT-v5 (`f423d6be…`) and W-1 v2 (`1c116f27…`) are frozen; their actual gpt-6.1-sol re-review started ~23:36Z (`wt-1/package-review/gpt61-v2`).
  actual gpt-6.1-sol review started 22:08Z (runner, thread `01a108f6…`), with output in `wt-1/package-review/gpt61-v1`.
- **Sealed reviews.** C-API v3 sealed 21:22Z and D1 v3 sealed 22:05Z. Both are ENDORSED_WITH_REQUIRED_CHANGES.
- **D1 DESIGN v4.** A drafting agent (author role, not review) started ~22:10Z on V3-RC1..RC3. Output goes to
  `wt-1/designs/claude-native-bigint-d1-design-v4`. Started deliberately as one agent at a time, paced against S-1:
  free space was 10514870272 bytes at 22:09Z.
- Consolidated operator package. Current draft: `work/claude-operator-decision-package-v1/DRAFT-v3.md`.
  - The next draft folds in the C-API v3 and D1 v3 verdicts and the D2 corrections above.
  - Then it gets its own actual gpt-6.1-sol review before going to the human.

## Isolation and records

- Edits that would land in the guarded tree go to `wt-1` (see `ISOLATION.md`).
- The workflow tree is read-only.
- Review runner records are copied to `work/claude-lead-isolation-v1/review-records`. Snapshot manifests are computed
  before the manifest file exists; the `T1915Z` defect is recorded.
