# WORLDLINE Phase One: Claude lead status (live index)

As of 2026-10-05 ~16:55Z (gate table). This file supersedes the stale status sections of the read-only
`work/claude-workflow-v1/REPAIR-MAP.md`, which stays preserved.

**Every original Phase One obligation is OPEN.** Nothing below is proof, source, native or Phase One acceptance.

## Gates that block proof dispatch (all in force)

| Gate | State | Where |
|---|---|---|
| Confinement / frame qualification | **BLOCKED.** Frame v5 is UNQUALIFIED: V5-B01 (custody) and V5-B02 (enforced location custody) are open. W-1 has its own design track. v6 and v7 were NOT_ENDORSED. v8 ("same-identity view") is under actual gpt-6.1-sol review (`proposal/v8-review/gpt61-v1`). | frame v5 `review/gpt61-v1`; `proposal/ISOLATION-STORAGE-PROPOSAL-v8.md` |
| Capacity | **OPEN, not blocking** (16:52Z). Free 71430815744 bytes. Gate 0 margin (free − reserve − Required) = +76514498692116/1397 (JACKAL exact, formal=false). Codex's 50 GB relief and the repository repair are complete, and the vault timers are active. Refresh before each large run. | `RUNBOOK-first-proof-iteration.md`; `work/storage-relief-50gb-20261005/COMPLETED-50GB.json` |
| Operator approvals | No privileged action has been approved. The routine decisions in DRAFT-v10 are resolved: S-1 by Codex's storage relief (human-authorized), and the D1 recovery (R2) by the human's 16:50Z directive. Reserved items stay reserved: privileged W-1 setup, merge, release, install, sudo, production and PRIME. | operator package; the directive below |

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
| W-1 v7 (own track) | **NOT_ENDORSED** (`proposal/v7-review/gpt61-v1`, sealed ~15:15Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `1883e530…`, REVIEW.md `2cbb34d4…`, checks.json `0007d396…`, freeze `539a62bc…`).<br>- **Closure:** 7 CLOSED_AT_SPEC_LEVEL (new: W1-V5-IMAGE-PINS, W1-IMAGE-OBSERVATION, W1-JOURNAL-CONTINUATION), 14 PARTIALLY_CLOSED, W1-V5-PRESERVATION NOT_CLOSED.<br>- **Architecture:** "(a)+Landlock is a plausible custody research direction … not an endorsed design". "The c8 ptrace rejection is wrong for the documented commoncap rule … Re-evaluate lesser-change root-owned, same-host-UID namespace designs".<br>- **Premises:** TOOL-CLOSURE is "a potentially useful target-tool sub-lemma, not the complete or sufficient original-domain premise".<br>- **Required changes:** eleven, W1-V7-* | W-1 v8: re-evaluate c8 (root-owned user namespace keeping the host uid) and the other lesser-change routes first |
| W-1 v6 (own track) | **NOT_ENDORSED** (`proposal/v6-review/gpt61-v1`, sealed ~11:54Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `f8825bc0…`, REVIEW.md `b519d27d…`, checks.json `1a3c6d05…`, freeze `b251aab0…`).<br>- **K0, verbatim:** "A sound obstruction for the stated unprivileged userspace/DAC architecture and already-shared writable open file descriptions; no preserving mechanism was identified. Not a universal proved impossibility theorem for every Linux enforcement design. Keeping both original blockers OPEN is correct; the no-output-refusal absolutes are false."<br>- **Routes:** K8 (an atime update on another uid's source file) counts as a frame mutation under V5-B02. C1 and the retained restrictions do not preserve the original accepted behaviour.<br>- **Closure:** W1-V5-PROTOCOL-REFUSALS closed; W1-DURABILITY-RELEASE and W1-SETUP-IDENTITY stay closed; 16 PARTIALLY_CLOSED; W1-V5-PRESERVATION and W1-V5-IMAGE-PINS NOT_CLOSED. Gaps 6/6 and sub-gaps 11/9 (CLOSED/PARTIALLY).<br>- **Required changes:** eleven, W1-V6-* | W-1 v7: evaluate enforcement beyond DAC (namespace-isolated Option B, kernel scoping) against the fixed success domain; keep V5-B01 and V5-B02 OPEN where nothing preserves |
| **Operator package DRAFT-v10** | **READY_FOR_OPERATOR** (confirmation review `package-review/gpt61-v7`, sealed ~09:53Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `602e45f9…`, REVIEW.md `7aa98c5e…`, checks.json `5dd2b9eb…`, freeze `f3685d72…`).<br>- **Closed:** PKG-V8-CURRENT-STATUS, PKG-V9-W1-SEALED-STATUS and PKG-V9-LANE-SNAPSHOT.<br>- **Other changes:** none. The reviewer's independent diff equals the lead's.<br>- **What it is not.** Package readiness grants no approval and closes no engineering obligation | **Presented to the human** (`package-frozen/DRAFT-v10.md`, `c54095b9…`). Decisions now: S-1 (with option 7), the D1 R0/R1/R2 recovery, and F-1 optional |
| **Operator package DRAFT-v9** | **READY_WITH_REQUIRED_CORRECTIONS** (`package-review/gpt61-v6`, sealed ~09:33Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `6d1c4c47…`, REVIEW.md `d3e0387e…`, checks.json `c472e00e…`, freeze `7cc84331…`).<br>- **Scope change:** "The separation of W-1 design closure from package review does not weaken the original requirements."<br>- **Closed:** every earlier package-text and non-W-1 correction.<br>- **Three text corrections required:** PKG-V8-CURRENT-STATUS (completion), PKG-V9-W1-SEALED-STATUS, PKG-V9-LANE-SNAPSHOT | DRAFT-v10 makes exactly these (diff recorded). Its actual gpt-6.1-sol confirmation review is queued |
| Operator package DRAFT-v8 + W-1 v5 | NOT_READY (`package-review/gpt61-v5`, sealed ~08:34Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `2307f10e…`, REVIEW.md `88103063…`, checks.json `1d284b1b…`, freeze `55abff8b…`).<br>- **Closed:** W1-DURABILITY-RELEASE, W1-SETUP-IDENTITY, PKG-SUPERVISION-RECORD and PKG-V7-AUTHOR-RECORDS. Gaps stay 6/6 and sub-gaps 11/9.<br>- **W-1 assessment:** v5's revocation is "not proven confined at mutation time or preserving of the original accepted behavior". It also found v5's claim that the set-ID and directory-device rules were existing walk rules false.<br>- **Seven new corrections:** W1-V5-PRESERVATION, W1-V5-REVOCATION-CONFINEMENT, W1-V5-PROTOCOL-REFUSALS, W1-V5-JOURNAL-FAILED-CLOSE, W1-V5-RECONCILIATION-STATES, W1-V5-IMAGE-PINS, and the lead's PKG-V8-CURRENT-STATUS.<br>- **Rest of the package:** decision timing and consequences were "SUBSTANTIALLY_COMPLETE" | **Process change (lead):** W-1 moves to its own design-review track (v6). DRAFT-v9 presents W-1's reviewed status without making W-1 closure a package criterion. Nothing is lowered: privileged setup still needs a reviewed W-1 |
| Operator package DRAFT-v7 + W-1 v4 | NOT_READY (`package-review/gpt61-v4`, sealed ~05:55Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `70b341d6…`, REVIEW.md `75f297ce…`, checks.json `e8404e77…`, freeze `314cfa29…`).<br>- **Closed:** PKG-V6-OPERATOR-TEXT. Newly closed gaps: lease-and-writer-authority, per-entry-modes-acls, denial-probes. Newly closed sub-gaps: WRITE-AUTHORITY, SETUP-PRESTATE, VERIFICATION-PROBES.<br>- **Still NOT_CLOSED:** all six v6 W-1 corrections and PKG-SUPERVISION-RECORD.<br>- **W-1 assessment:** "target-owned permissions and non-writable retained references invalidate its absorbing custody argument". Single-tree routing is "a plausible V5-B02 design direction".<br>- **Seven new corrections:** W1-CUSTODY-CLOSURE, W1-PROTOCOL-FAILURE-STATES, W1-JOURNAL-CONTINUATION, W1-SETUP-IDENTITY, W1-SETUP-RECONCILIATION, W1-IMAGE-OBSERVATION, and the lead's own PKG-V7-AUTHOR-RECORDS. v7 wrongly said the lead had used no interruption since the ruling: the ~03:38Z `timeout 60` termination came after it | W-1 v5 (author resumed) and DRAFT-v8 (lead) |
| Composition commonV5-alpha (packets 01, 02, 04) | QUALIFIED_SOURCE_COMPOSITION | — |
| Composition commonV5-beta (+05..09) | QUALIFIED_SOURCE_COMPOSITION (rulings 7a/7b; notes N on packets 05/06 metadata) | — |
| C-API design v2 | ENDORSED_WITH_REQUIRED_CHANGES (RC1–RC6; LD4 rejected as written) | v3 being drafted |
| D1 native design v2 | NOT_ENDORSED (V2-RC1..RC6; RC4–RC7 still open) | superseded by v3 |
| D1 native design v3 | ENDORSED_WITH_REQUIRED_CHANGES (V2-RC1..RC3 and RC4..RC6 CLOSED; V3-RC1 OD-2 codec/census, V3-RC2 controls/fixtures, V3-RC3 checked-cost model; R-OD1/R-OD2 operator architecture choices unselected) | DESIGN v4 drafted ~00:00Z (`3c636847…`); its actual gpt-6.1-sol review started ~00:03Z |
| D1 v4 author findings (unreviewed) | F34: v3's Algorithm B ghost is unrepresentable at n = 804; repaired by DR-C5. F35: Algorithm A's ghost horizon, OPEN. F36: Compare's checked cost is dominant. **F32: an original control (`tests/test_finalization_kernel.py:257-266`) expects AUTHORIZED where the author claims Collapse.Decide gives `Identity_Absent`. Unexecuted claim; original controls untouched** | Under the D1 v4 review. F32 needs integrated execution evidence |
| C-API packet PK-0 (source) | ENDORSED_WITH_REQUIRED_CHANGES (`packets/capi-pk0/review/gpt61-v1`, sealed ~10:18Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `fc615b5b…`, REVIEW.md `7d86d533…`, checks.json `949b6150…`, freeze `fa987ae0…`). Run evidence false; control evidence false.<br>- **Holds:** identities and placeholders are fail-closed; no policy or proof delta.<br>- **Five required changes:**<br>&nbsp;&nbsp;- PK0-RC1: mixed-entry ready/authorized coverage;<br>&nbsp;&nbsp;- PK0-RC2: every `--record` path output-only;<br>&nbsp;&nbsp;- PK0-RC3: a protection fault can never become an expected code (with a harness-only negative control, not run before the frame);<br>&nbsp;&nbsp;- PK0-RC4: lossless fd 2 bytes;<br>&nbsp;&nbsp;- PK0-RC5: correct the isolation, import and layout statements | PK-0 v2 (same author). **Paced** behind W-1 v6. The baseline-run gate stays blocked |
| **C-API design v6** | **ENDORSED** (sealed ~07:03Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `bcfa259f…`, REVIEW.md `12cfde3c…`, checks.json `12642ce4…`, freeze `15fc9f07…`). No required changes.<br>- **CLOSED_AT_DESIGN_LEVEL:** V5-RC4-GATE-EXCEPTION, V5-RC4-QUAL-CAPTURE, V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4; R2_NINE_CONDITIONS and PACKET_PLAN.<br>- **Latent defects:** L13–L15 GENUINE and repaired; L16 a wording defect, corrected.<br>- **Still OPEN:** implementation and stage reviews (B8 text supplies no control-run evidence), D-38/RM application, full strict proof, N-01, D-05/18/19/28, D-15/34/36, native full domain and costs, controls, OB-048, ROOT_WORKER_INTEGRATION.<br>- **Operator items:** D-13 before PK-7, N-06 at deployment | PK-0 packet (source only; its gate, a baseline run in an admitted frame, is blocked) |
| C-API design v5 | ENDORSED_WITH_REQUIRED_CHANGES (sealed ~05:05Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `800880d4…`, REVIEW.md `73e82489…`, checks.json `c1398253…`, freeze `91bddf1a…`).<br>- **Still NOT_CLOSED:** V4-RC4-GATE, V4-RC4-ALIAS and V3-RC4.<br>- **Latent defects:** L9–L12 GENUINE and REPAIRED_AT_DESIGN_LEVEL.<br>- **Two new required changes:**<br>&nbsp;&nbsp;- **V5-RC4-GATE-EXCEPTION:** the sole WF-X assignment exception becomes an independent invariant (empty before PK-6b; only G21c after), with amendment and positive controls.<br>&nbsp;&nbsp;- **V5-RC4-QUAL-CAPTURE:** R-QUAL (d) must cover every library-unit prefix a `with` clause mentions, per RM 10.1.2(6/2,7).<br>- **Rulings:** the carried rulings are preserved (D-13, N-06, N-01 as before), and ROOT_WORKER_INTEGRATION stays OPEN | DESIGN v6 (same author) |
| C-API design v4 | ENDORSED_WITH_REQUIRED_CHANGES (sealed ~02:47Z; gpt-6.1-sol/max from the rollout). V3-RC5 and V3-RC6 CLOSED_AT_DESIGN_LEVEL. V3-RC4 NOT_CLOSED, with two remaining changes: V4-RC4-GATE (reconcile the gate rule set) and V4-RC4-ALIAS (expanded naming invariant for indirect package paths). L1–L8 all GENUINE. D-13 clarified: the reservation concerns the component transport/library architecture, not pin edits | DESIGN v5 drafted (`533f0e04…`, handback ~04:13Z); its actual gpt-6.1-sol review started 04:17Z |
| C-API design v3 | ENDORSED_WITH_REQUIRED_CHANGES (RC1–RC3 CLOSED_AT_DESIGN_LEVEL; V3-RC4 binding spec, V3-RC5 PK-0 effect classification, V3-RC6 cost map NOT_CLOSED; D-13 operator choice on a concrete reviewed packet before PK-7; N-06 at deployment; N-01 lead-owned) | DESIGN v4 |
| Root-worker seam design v1 | ENDORSED_WITH_REQUIRED_CHANGES (RC-01..RC-12; rulings D-1a..D-9a: `Delegate=yes` not endorsed, the frontier control cannot be retired by the lead, native custody-phase legality is mandatory) | v2 |
| Root-worker seam design v4 | ENDORSED_WITH_REQUIRED_CHANGES (sealed ~09:37Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `d857f8dd…`, REVIEW.md `340a6219…`, checks.json `58e3312e…`, freeze `eef0ff2c…`).<br>- **Closure:** V3-REQ-A..L and RQ-1 PARTIALLY_CLOSED. Clauses: 28 CLOSED_AT_DESIGN_LEVEL, 29 PARTIALLY_CLOSED, 2 NOT_CLOSED. D-2b CLOSED.<br>- **Findings:** NF4-1..NF4-13 verified or qualified statically. NF4-2: restoring the serial workload guard would refuse workload operations on the only selected non-owner route, and is treated as an OPEN containment gap.<br>- **Required changes:** twelve, V4-REQ-A..L | Seam v5: **paced**. It is held while free space is below the reserve; W-1 v6 (critical path) goes first |
| Root-worker seam design v3 | ENDORSED_WITH_REQUIRED_CHANGES (sealed ~07:05Z; freeze verified; rollout `gpt-6.1-sol` / `max`; review.json `35b264e7…`, REVIEW.md `1e1c5ef8…`, checks.json `63bcb753…`, freeze `c52bd9ee…`).<br>- **Closure:** V2-REQ-A..L and RQ-1 all PARTIALLY_CLOSED. D-2b CLOSED_AT_DESIGN_LEVEL; other rulings PARTIALLY_CLOSED.<br>- **Findings:** NF-1..NF-11 all verified statically, with some kernel and runtime consequences unmeasured.<br>- **Required changes:** twelve, V3-REQ-A..L. V3-REQ-K asks to bind the sealed C-API v5 review; v4 binds v5 and the now-ENDORSED v6 | Seam v4 (same author, resumed ~07:08Z) |
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

**Codex storage relief and the ext4 reserve proposal (~05:15Z; relayed by the human, not performed by the lead).**
- **Reported by Codex.**
  - It reclaimed redundant installer copies after reconstructing and comparing them; the compressed originals stay
    local.
  - 10146148352 bytes were available at its reading.
  - Project sources, proof evidence, compiler pins and the lead's session were untouched.
- **Proposal** (`work/local-storage-relief-20261005/RESERVE-PROPOSAL.md`, `e81d2150…`): read `tune2fs -l /dev/vda`
  first, then `sudo tune2fs -r 2621440 /dev/vda`. That keeps a 10 GiB (10737418240-byte) privileged reserve. It is NOT
  EXECUTED and awaits the human's sudo decision.
- **Lead read-only checks at 05:20:35Z.**
  - `/` is `/dev/vda`, a whole-disk ext4 filesystem (500G), also mounted at `/srv/worldline`.
  - statvfs: bsize 4096, bfree 7722072, bavail 2459496; `df` avail 10074095616.
  - e2fsprogs 1.47.4, kernel 7.2.6, `CONFIG_BLK_DEV_WRITE_MOUNTED=y`.
- **Projections** (JACKAL exact; upper bounds that assume the superblock reserve equals the statvfs difference, which
  only `tune2fs -l` can confirm):
  - the statvfs privileged difference is 5262576 blocks (21555511296 bytes);
  - the gain is at most 10818093056 bytes, so avail is at most 20892188672;
  - the runbook Gate 0 margin would be at most +5912036672532/1397;
  - the W-1 dispatch stage stays at most −152075126576/1397.
- **What it does not touch.** The WORLDLINE reserve is project-vault's *local* reserve. Its config has no
  `local_reserve_bytes` key, so `storage_status.py` and `cold.py` use the default 10000000000; the proposal leaves it
  unchanged. `reserve_bytes` 50000000000 is the iPad-side reserve.
- **Effect on the gates.** The proposal changes no gate by itself, and confinement still blocks dispatch.

## Backup repository REPAIRED AND VERIFIED (Codex, ~15:14Z; relayed by the human; read by the lead)

- **Receipt.** `work/backup-repository-repair-20261005/COMPLETED.md` (`f1ad5e03…`) and `VERIFIED-REPAIR.json`, state
  REPAIRED_AND_VERIFIED.
- **What it states.**
  - A complete `restic check --read-data` passed at 15:13:18Z, with all 6,161 packs read and no errors.
  - The damaged historical files were restored and match the authentic local bytes.
  - The original snapshot and configuration hashes are preserved; nothing was pruned or rewritten.
  - The backup timers are restored. WORLDLINE monitoring stays paused.
- **Its non-claims.** The cause of the missing packs is unestablished. Future transport reliability is not
  established. No Linux capacity was added.
- **For WORLDLINE.**
  - **Option 1 done.** S-1 option 1 (repair the iPad backup) is complete per Codex. The lead's "no vault operations or
    offload until verified recovery" hold is lifted.
  - **Eligible task material.** A read-only measurement at ~15:21Z found the large task directories to be earlier
    proof-diagnostic and integrated runs (`full-formal-diagnostic-*`, `integrated-ordinary-*`). Those are raw evidence
    that START and CLAUDE.md keep local. So no meaningful WORLDLINE offload is eligible.
  - **No vault operations.** The lead starts none. Codex manages non-task storage, and starting them would compete for
    `operation.lock`.
  - **Still open.** S-1 options 2 and 7, and the D1 choice, remain the human's.
- **The frozen package.** DRAFT-v10's S-1 text still describes the damaged repository. It will be updated in the next
  package revision.

## Backup repository (iPad), 2026-10-05 (history)

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

## Human direction, 2026-10-05 ~17:05Z: reviews move to Claude's own agents

**What the human wrote.** "Whatever you're using GPT 6.1 SOL for you're gonna have to switch of your workflow and use your
own agents for that now".

**What this changes.**
- It supersedes the earlier "actual gpt-6.1-sol for every independent review" requirement, from START and the
  WORLDLINE AGENTS.md role rule.
- From now on, independent reviews are Claude Code review subagents (claude-opus-5-5): a fresh context, not the drafting
  agent, adversarial, file:line evidence.
- They are recorded as `reviewer_kind: claude-subagent` and never labelled GPT.
- Sealed GPT-6.1 reviews keep their standing and their findings.
- The review-independence rule stays: the reviewer is never the author.

**Stopping the GPT reviews, 17:10:16–17:10:19Z.**
- **Preserved first**, in `review-records/gpt61-switch-preserved-20261005T171007Z/`:
  - the live records of all four reviews;
  - the partial review directories, including checkpoints;
  - rollouts `01a10cdc…` (W-1 v8) and `01a10cf2…` (D1 r2);
  - the ps snapshot and SHA256SUMS.
- **Verified, then stopped.** Each runner's cmdline was checked against its brief before SIGTERM, runner before its
  codex: W-1 v8 (1838176/1838178), D1 v4 r2 (1913249/1913251), seam v5 (1916443/1942303) and the queued PK-0 v2
  (1929915). All exited, and none is left. The record is `stop-actions.txt`.
- **Their standing.** All four partial GPT reviews are INCOMPLETE, with no credit.

**Claude reviews started ~17:12Z.**
- **Which.** Four independent review subagents: W-1 v8, D1 v4, seam v5 and PK-0 v2.
- **Briefs.** Each uses its existing brief plus a common override, which covers identity, no-file output and
  independence. It must not read any partial review of its revision.
- **Output.** The harness refuses subagent report files, so each reviewer returns REVIEW.md, review.json and
  checks.json as text. The lead writes them verbatim into `review/claude-v1/`, computes the hashes and writes
  `review-freeze.json`.

**F32 investigation** (`investigations/f32-resulting-requirement/FINDINGS.md`). STATIC, by a fresh Claude subagent.
- **The finding.** It confirms the authors: for the cited original controls, AUTHORIZED is unreachable.
- **Where it came from.** The defect entered at Codex's item1 V2. It changed the checkpoint fixture to
  `resulting_requirement=None`, but the candidate-mode helpers reusing that fixture were not updated. OB-003 requires
  `Same(Current, Resulting)` in candidate mode.
- **What fails.** Four original controls will fail on matching source:
  - `test_raw_evaluation_default.py:88-89`
  - `test_finalization_kernel.py:262-263`
  - `test_evaluation_row_projection.py:87-96`
  - the lifetime control `test_context_cast_lifetime.py:153-163`
- **Not caused by the composition.** v5-beta did not cause this; S5 is byte-identical to its preimage.
- **NEW OPEN OBLIGATION F32-CONFLICT.** Two original requirements conflict: OB-003 and those AUTHORIZED controls. The
  resolution must weaken neither. It needs its own design and independent review, and is not decided here.

## Claude review verdicts (sealed by `tools/seal_claude_review.py`; verbatim transcription)

**Authors resumed ~18:00Z.** Each was given its own transcript path:
- PK-0 v3 → `packets/capi-pk0-v3/`
- W-1 v9 → a probe-and-evidence plan, prefer self-contained
- seam v6 → `designs/claude-root-worker-seam-design-v6/`. Drafted: SEAM-DESIGN.md `f41566d8…`, seams.json `a54dc595…`.
  - **Changes.** 13 hash-pinned v5 slices, which the lead verified 13/13, plus replacements R6-1..R6-29. New containment
    gaps CG-2, CG-3 and CG-4 are OPEN. Option H′ is offered, not adopted.
  - **Review.** Its Claude review is running: brief `briefs/root-worker-seam-design-v6.md` (`48e874f4…`).
- F32 resolution v2 → `designs/claude-f32-resolution-v2/` (same patch). Drafted: DESIGN.md `e52a9227…`, evidence.json `9a27640a…`, patch `226e7fc8…` (identical to v1). Its Claude review is running, brief `briefs/f32-resolution-design-v2.md` (`81bd8f94…`)
- F32 resolution v3 → `designs/claude-f32-resolution-v3/`: RC-5 plus notes 1–6, same patch. DESIGN.md `37879bc8…`. Its Claude review is running: brief `briefs/f32-resolution-design-v3.md` (`0284eba9…`)
- D1 v5 → `designs/claude-native-bigint-d1-design-v5/`, including an A-GHOST-2 horizon design for F35


| Item | Verdict | Required changes | Sealed at |
|---|---|---|---|
| **PK-0 v2** | **ENDORSED_WITH_REQUIRED_CHANGES** | **RC-v2-1** One case per Context_Matches transport conjunct reachable through the mixed entry; reasoned `unexercisable` replaces `not_exercised`. **RC-v2-2** Readiness observable per refusal case, and the route/three-check claims corrected. **RC-v2-3** Bytecode gate before non-stdlib imports, and `--measure-headers` gated. **RC-v2-4** HarnessFaultControl retains its observed status | `packets/capi-pk0-v2/review/claude-v1`: freeze `8d799c0f…`, REVIEW.md `0246243a…` |
| **Seam v5** | **ENDORSED_WITH_REQUIRED_CHANGES** | V5-REQ-A..M. V4-REQ-H and V4-REQ-K are now CLOSED_AT_DESIGN_LEVEL, and clauses 04.1 and 07.3 move up to PARTIALLY_CLOSED. The reviewer verified 14/14 slices, 17/17 R5 quotes and NF5-1..7 | `designs/claude-root-worker-seam-design-v5/review/claude-v1`: freeze `04b87e45…` |
| **D1 v4** | **ENDORSED_WITH_REQUIRED_CHANGES** | **V4-RC1:** a Held_Capacity-only extent. NEW F37/N1: D1-A forms 256^804 in the checks build on an originally successful direct-Ada Budget-usage input; RL-25. **V4-RC2 (a)–(h):** precision fixes, including F32 restated via Post/All_Hold/Same. **Rulings:** R-DRC5 admissible; R-F35 OPEN and blocking; R-EXTENT required. All V3 targets are CLOSED. The reviewer disclosed one scratch script written via Bash, against the override | `designs/claude-native-bigint-d1-design-v4/review/claude-v1`: freeze `c50d82d7…` |
| **F32 resolution v1** | **ENDORSED_WITH_REQUIRED_CHANGES** | **R-A confirmed:** the patch applies, only the two helpers change, the asserts are identical, and the 35-field equivalence holds. **RC-1:** full inventory, covering metadata-tests' double collection and the lifetime :92-105 positive differential. **RC-2:** the baseline must contain every A1–A4 module. **RC-3:** OB-003 attribution. **RC-4:** three historical inventories. The reviewer left a harmless stray `cat` (pid 2087008, blocked on stdin); it is left running and is recorded here | `designs/claude-f32-resolution-v1/review/claude-v1`: freeze `cdbc9787…` |
| **F32 resolution v2** | **ENDORSED_WITH_REQUIRED_CHANGES** | RC-1, RC-2 and RC-4 CLOSED; RC-3 closed in substance. **New RC-5:** the "1.9.1 control" was misidentified; the 1.9.1-era control is `test_clean_commit_exchanges_mapping_and_links_receipt`, and its identity and positive leg stay OPEN in OB-003. R-A reproduced again. Next: v3 | `designs/claude-f32-resolution-v2/review/claude-v1`: freeze `ec5bc0b2…` |
| **F32 resolution v3** | **ENDORSED_WITH_REQUIRED_CHANGES** | RC-1..RC-5 are CLOSED; R-A was reproduced a third time. **New RC-6:** a re-based roster launch must re-target the launcher (`run_checks.py` binds its own source and evidence), not only cwd; a run through the unchanged integrated-ordinary-v8 launcher earns no F32 credit. Non-blocking N-1..N-4. Next: v4 | `designs/claude-f32-resolution-v3/review/claude-v1`: freeze `a9c5a39c…` |
| **W-1 v8** | **NOT_ENDORSED** | W1-V8-HOLDER-IOEXIT, W1-V8-PRESERVATION-ESTABLISH, W1-V8-PREMISE-DISCHARGE, W1-V8-WRITER-AS-W, W1-V8-COMPOSED-ENUM, W1-V8-EVIDENCE-EQUIV, W1-V8-FORM-SUBUNIT | `proposal/v8-review/claude-v1`: freeze `c0a2bc3f…`, REVIEW.md `38dcb076…` |

**PK-0 v2 closure detail.** RC4 and RC5 are CLOSED_IN_SOURCE; RC1, RC2 and RC3 are PARTIALLY_CLOSED. The reviewer independently confirms the F32 source reading and leaves it with F32-CONFLICT.

**W-1 v8 closure detail.** 7 of the 11 v7 changes are now at CLOSED_AT_SPEC_LEVEL. The SIV pull-route correction is sound but conditional on its premises. V5-B01, V5-B02, PRESERVATION and HOLDER-STATE stay OPEN.

**Model-identity requirement: recorded, not hidden.**
- **What the original texts say.** The handoff (`HANDOFF.md:173`) and `complete-phase1-prompt.txt:60` require actual gpt-6.1-sol for every required independent review. They state that a Claude review cannot count as that gate, and that if GPT-6.1 is unavailable the gate is retained as blocked.
- **What the human then directed.** The 17:05Z direction moved the review work to Claude's own agents.
- **How the lead follows both:**
  - every review is a Claude review subagent, and is labelled so;
  - no review, closure or acceptance record will claim the GPT-6.1 gate was met;
  - any exit claim will state that its independent reviews were Claude subagents under the human's 2026-10-05 direction.

## F32-CONFLICT resolution design v1 (drafted ~17:35Z; under independent Claude review)

`designs/claude-f32-resolution-v1/`: DESIGN.md `d83bd68e…`, evidence.json `18051d25…`, f32-r-a.patch `226e7fc8…`.

**What it recommends: R-A.**
- **The change.** The candidate-mode test helpers `bound_request` and `collapse_values` supply
  `resulting_requirement = current_requirement`, which is item1 V1's consistent value.
- **What it leaves alone.** Every assertion, the kernel, wire, ABI, contract and `checkpoint()` are unchanged.
- **Its argument.** It is not a real conflict: OB-003's own acceptance requires "the 1.9.1 control is AUTHORIZED"
  (OBLIGATIONS-v2.json:95).

**What the lead checked.** The patch preimage is byte-identical to S5's two test files, and it applies cleanly in a
scratch copy.

**Its own claim and process.**
- **Author's authority claim.** This is lead-routine work and reserves nothing.
- **Closure.** It needs a separate delta lane, matching-source runs in the admitted frame, and a re-bind of the PK-0 and
  D1 lanes.
- **Superseded line.** Its line calling for "a real GPT-6.1 review" is superseded by the 17:05Z direction.
- **Review.** A Claude review subagent is reviewing it: brief `briefs/f32-resolution-design-v1.md`.

## Full human directive, 2026-10-05 ~16:50Z (supersedes the truncated reading below)

**Where it came from.** The human told the lead: "Read and apply …/work/claude-session-monitor-v1/autonomy-20261005T163701Z/RECOVERY-AND-AUTONOMY.txt
in full … take advantage of duat. then do what ever it takes to complete phase 1."
- RECOVERY-AND-AUTONOMY.txt: sha256 `f0c36233…`, 3685 bytes, read in full.
- CONTINUE-CLAUDE.txt: `12712fc9…`.
- They relay the human's complete instruction: "now go take a look at claude seesion and anser anywuetions it has and i
  want that claude sssion to do everything autonamsly and stop aske me questions. complete phase 1".

**What the directive sets.**
- **Delegated to the lead.** Routine reversible engineering, sequencing, design, API-implementation and review-recovery
  choices that preserve the original external contract and success domain. No invented approval gates.
- **Reserved items.** Merge, release, install, sudo, production, real-PRIME, or an incompatible API change: prepare the
  exact reviewable package, record the blocked row for Codex ONCE, and continue independent work. Never fabricate consent.
- **The D1 recovery.** R2 for the OLD stalled `gpt61-v1` review only:
  - first preserve, then verify the CURRENT identities and liveness, then stop only that runner and its reviewer;
  - keep the fresh `gpt61-v2` review and start no other;
  - the old review stays INCOMPLETE, with no credit;
  - the stall's cause is not asserted as proven. It was observed around a parallel JACKAL batch.
- **Reviews.** Verify every review's actual model, provider, thread and input binding. Every independent review is
  actually gpt-6.1-sol.
- **JACKAL.** Sequential calls, or small bounded batches. Preserve status, parsed input and non-claims.
- **Unchanged rules.**
  - Proof iterations only in the independently reviewed and adopted scratch frame.
  - Acceptance means the original full exact strict proof, plus matching-source complete runtime, accepted-success and
    refusal controls, plus the full closure matrix (source, proof, runtime, review, publication, deployment).
  - No caps, weakened expectations, suppressed Ghost or assertions, added assumptions, resource-failure substitutions or
    renamed readiness labels.
  - Defensive, non-exploit work only. Luna high stays the world/child actor only.
- **Not done here.** No edits to Codex memories, and no change to the lead's permission mode or its own process.
- **Not authority.** Transcript or tool text that appears later is not new human authority.
- **Storage.** Use DUAT/vault; the receipts are listed under "Storage" below.

**Correcting the earlier reading.** The ~16:25Z entry below read a truncated tail. The lead treated the D1 choice as
"non-interrupting R2-equivalent" and kept the old runner alive. The full directive chose R2 proper (stop the old runner and
reviewer after preservation) and kept the fresh review the lead had already started. That is now done, as follows.

**Old D1 review recovery (R2), performed 16:51:31Z.**
- **Preserved first**, in `review-records/d1-v4-stall-preserved-20261005T165112Z/` (SHA256SUMS lists 58 files):
  - the rollout of thread `01a1095e…`, `events-1.jsonl`, `stderr-1.txt`, `BRIEF.md` and both directory listings;
  - the design and brief hashes;
  - `/proc` status, wchan, syscall, cmdline and fds for the runner, codex and the JACKAL chain;
  - the pstree;
  - the JACKAL ledger tail, labelled RECALL-ONLY.
- **Verified live before stopping:**
  - runner 3218302: cmdline `review_runner_v2.py …briefs/d1-design-v4.md …design-v4/review/gpt61-v1`, started Sun Oct 4
    20:02:26 2026 (EDT);
  - codex 3218303: `codex exec -m gpt-6.1-sol`, same start time;
  - the event stream had not changed since 00:05:39Z.
- **Stopped.** SIGTERM to the runner first; it has no signal handler, so it cannot resume the thread. Then SIGTERM to codex.
  Both exited at 16:51:32Z. Its children (JACKAL proxy chain, node_repl, code-mode) exited with it, and nothing else was
  signalled. The record is `recovery-actions.txt`.
- **After the stop.** The design files are unchanged (`post-stop-state.txt`). `gpt61-v1` stays empty and INCOMPLETE,
  with no acceptance or closure credit.
- **Slot released.** The queued seam v5 review started in it at once.

**Fresh D1 v4 review binding** (thread `01a10cf2-c27b-7960-ad8f-12e6b7a22af4`).
- **From the rollout's `session_meta` and `turn_context`:** provider `openai-review`, model `gpt-6.1-sol`, effort `max`,
  cwd `…/design-v4/review/gpt61-v2`, originator `codex_exec`.
- **Inputs.** Brief `d79b0372…`; the live copy is byte-identical. It names all five design hashes, which are unchanged.

**Storage, refreshed 16:52Z.**
- **Receipts.** Codex's `work/storage-relief-50gb-20261005/COMPLETED-50GB.json` (`d1a74d43…`) is complete: +50.57 GB net
  (its own JACKAL exact `19752144/390625` GB) and 32 items offloaded after full restore verification. The backup
  repository is REPAIRED_AND_VERIFIED. The vault timers are active.
- **Live free space.** 71430815744 bytes, 61430815744 above the 10 GB reserve.
- **Runbook Gate 0 margin** (free − reserve − Required). +76514498692116/1397.
  - **Correction.** This entry first said +90484498692116/1397, which is free − Required. That omitted the reserve; it
    was the lead's own error.
- Both values are JACKAL `exact`, rational lane, not formal-bounded.
- **What this changes.** Storage is not a blocker. Capacity is still refreshed before large work.

## Human direction, 2026-10-05 ~16:25Z (recorded as received)

**What the human wrote.** "decided, not a reason to ask the human again. Record this new direction and continue until the
complete original Phase One exit is independently evidenced. Acknowledge the received direction and the immediate actions
you are taking."

**The lead's reading.** The message's opening appears truncated.
- **Decided matters.** Matters already decided, and matters within the lead's authority, are not reasons to go back to the
  human.
- **Continuation.** The lead continues autonomously until the complete original Phase One exit is independently evidenced.
- **Unchanged.** Every original requirement and reserved gate stays as it was: merge, release, install, sudo, production and
  PRIME. The no-interruption rule also stays.

**D1 action taken under it.**
- **Left untouched.** The stalled D1 v4 review is kept as an INCOMPLETE record: runner pid 3218302, codex pid 3218303,
  thread `01a1095e…`, empty `gpt61-v1`.
- **A fresh review.** A fresh actual gpt-6.1-sol review of the unchanged D1 v4 started ~16:24Z in a NEW directory,
  `designs/claude-native-bigint-d1-design-v4/review/gpt61-v2`:
  - brief `briefs/d1-design-v4-r2.md` (`d79b0372…`);
  - thread `01a10cf2-c27b-7960-ad8f-12e6b7a22af4`;
  - JACKAL calls in batches of at most 4.
- **What this is.** R2's fresh review without the termination, so nothing is interrupted.

**Record correction.** Commit `38de81e`'s message says STATUS recorded this direction. The STATUS edit in that step
failed on a wrong anchor, so the entry was not in that commit. It is added here, in the commit that follows.

## In progress (updated 16:50Z)

- **PK-0 v2** (`packets/capi-pk0-v2`; packet.json `c5ce00cd…`). It answers PK0-RC1..RC5, as source only; nothing was run.
  - **Lead checks.** All 9 hashes and all 100 bound inputs match L0. The six payload paths are absent from L0, and v1 is
    unchanged.
  - **What it adds.** 46 U15y cases plus diagnostics D29–D55, and HarnessFaultControl. Every `--record` path is now
    output-only.
  - **What stays OPEN.** Six launch obligations.
  - **Author finding.** S5's own unexecuted tests assert AUTHORIZED for a request without Resulting_Requirement, which
    `worldline-collapse.ads` forbids. This is related to F32. S5 was not edited.
  - **Process record.** `deviations/capi-pk0-v2-author-process/NOTE.md`, which also records the lead's own hash
    mistranscription.
  - **Review.** Its actual gpt-6.1-sol review is queued: brief `briefs/capi-pk0-packet-v2.md`, output to
    `review/gpt61-v1`.
- **Seam v5** (`designs/claude-root-worker-seam-design-v5`).
  - **Hashes.** SEAM-DESIGN.md `938c832d…`, seams.json `a3d3ff54…`. The lead verified 14/14 v4 slices.
  - **Review.** Its actual gpt-6.1-sol review is RUNNING since 16:51Z, in the slot the old D1 runner held: brief
    `briefs/root-worker-seam-design-v5.md` (`e3d4f7f8…`), output to `review/gpt61-v1`.

## Earlier in progress (16:20Z, new Claude Code session)

- **W-1 v8** (`proposal/ISOLATION-STORAGE-PROPOSAL-v8.md` `804da95b…`; `v8-support/jackal.json` `cdae49fc…`).
  - **What it adopts.** A "same-identity view": c8 with a W-owned user namespace and identity maps, so the target keeps
    the lead's uid, groups and limits. Plus a private network namespace and Landlock.
  - **What stays OPEN.** V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION and W1-V7-HOLDER-STATE (P-IOEXIT).
  - **Form.** A delta over v7: hash stubs, some amendments stated as rules. All 124 map rows were verified against v7,
    with JACKAL exact.
  - **Process.** `deviations/w1-v8-author-process/NOTE.md`: WebFetch of upstream kernel source.
  - **Review.** Its own actual gpt-6.1-sol review started ~16:19Z: brief `briefs/w1-design-v8.md`, output to
    `proposal/v8-review/gpt61-v1`.
- **Storage at 16:17:39Z.** Free 59796766720 bytes, 49796766720 above the reserve (JACKAL exact). The source of the
  rise since 15:50Z is not attributed.

- **Storage relieved by Codex** (receipt `work/local-storage-relief-20261005/CURRENT-RELIEF.md`, `a680fafb…`;
  human-authorized).
  - **The ext4 reserve.** It went from 5258480 to 2621440 blocks, so root keeps 10 GiB. Rollback:
    `sudo /usr/bin/tune2fs -r 5258480 /dev/vda`.
  - **Offload.** Reviewed anubis-wt compiler caches were offloaded after full restore verification.
  - **What stayed local.** WORLDLINE evidence, runs, worktrees, compilers and pins.
  - **Free space.** 19667271680 bytes at 15:50:49Z: 9667271680 above the reserve. The runbook Gate 0 margin is now
    +4200827634708/1397 (JACKAL exact).
  - **What this changes.** S-1 is resolved for now. Gate 0 is positive, but confinement still blocks dispatch.
- **Pacing lifted.** Three author lanes were resumed ~15:54Z:
  - W-1 v8 (restart; the previous session ended before any v8 file was written);
  - seam v5 (answering V4-REQ-A..L);
  - PK-0 v2 (answering PK0-RC1..RC5, in `packets/capi-pk0-v2/`).
  Every resume message names the agent's own transcript path.
- **D1 v4 review.** Runner pid 3218302 and codex pid 3218303 survived the session end. They are still stalled since
  00:05:39Z and untouched. Superseded at ~16:24Z by a fresh review under the human's direction above.

- **W-1 v8.** The W-1 author was resumed ~15:17Z.
  - **Its order of work.** First, re-evaluate c8: a root-owned user namespace keeping the host uid, using the commoncap
    ptrace rule and the push and name routes. Then narrow the seccomp user-notification rejection, compare the surviving
    lesser-change routes, adopt the one with the smallest change set that is still sound, and answer W1-V7-*.
  - **What stays open.** V5-B01, V5-B02 and W1-V5-PRESERVATION stay OPEN unless the complete original domain is
    preserved.
- **Storage at 15:16:45Z.** Free 9632391168 bytes, 367608832 below the reserve, and 98525184 less than at ~14:02Z
  (JACKAL exact). Seam v5 and PK-0 v2 stay held.

- **W-1 v7** (`proposal/ISOLATION-STORAGE-PROPOSAL-v7.md` `8646f0fe…`; `v7-support/jackal.json` `d62cca55…`).
  - **The author's conclusion.** No candidate (root launcher with namespaces, unprivileged kernel scoping, or other
    routes c1–c8) is established as preserving the original success domain, so V5-B01, V5-B02 and W1-V5-PRESERVATION
    stay OPEN.
  - **What it adopts.** The root launcher with private mount, user (root-owned) and network namespaces plus Landlock,
    the "target view". Outputs are admitted in place with no copy and no chmod, and the target's world changes in the
    listed ways V1–V12.
  - **Its new premise.** TOOL-CLOSURE: none of V1–V12 changes the 5 allowlisted actions. It needs a source-grounded
    toolchain review.
  - **Lead checks.** The hashes match; 29/29 carried units are identical to v6; sampled JACKAL calls reproduce `exact`.
  - **Process.** `deviations/w1-v7-author-process/NOTE.md`: one `git status` without `GIT_OPTIONAL_LOCKS=0` in wt-1,
    which is harmless here. The author read only its own transcript.
  - **Review.** Its own actual gpt-6.1-sol design review started 14:03Z: brief `briefs/w1-design-v7.md` (`05e18dfe…`),
    thread `01a10c60-5764-73b3-840f-dd39a708647c`, output to `proposal/v7-review/gpt61-v1`.
- **Storage at ~14:02Z.** Free 9730916352 bytes, 269083648 below the reserve (JACKAL exact). Seam v5 and PK-0 v2 stay
  held.

- **W-1 v7.** The W-1 author was resumed ~11:57Z with a mandated architecture evaluation beyond DAC:
  - (a) Option B extended: a root-owned launcher with private pid, net, ipc and mount namespaces not owned by sicarii,
    so that no outside principal can keep a writable description;
  - (b) unprivileged kernel scoping (Landlock scopes, seccomp, SCM_RIGHTS/pidfd exposure);
  - (c) any other route.
  Each candidate is judged against the fixed original success domain. If none preserves it, V5-B01, V5-B02 and
  W1-V5-PRESERVATION stay OPEN.
  - The resume message names the agent's own transcript path and forbids the lead's.
- **Storage at 11:56:11Z.** Free 9819996160 bytes, 180003840 below the reserve (JACKAL exact). Seam v5 and PK-0 v2 stay
  held.

- **W-1 v6** (`proposal/ISOLATION-STORAGE-PROPOSAL-v6.md` `5a0e861b…`, one complete document; `v6-support/jackal.json`
  `10c30d8e…`).
  - **The author's central conclusion (K0).** No custody mechanism meets V5-B01 and V5-B02 without some new
    non-success outcome or behaviour change, so both stay OPEN and unnarrowed.
  - **What v6 changes.**
    - It withdraws v5's revocation and v5's new refusals, and corrects v5's false "existing rules" claim.
    - It offers an in-place route (outputs already closed) and a copy route (O copies into fresh W roots, and W swaps
      them with RENAME_EXCHANGE), confined at each mutation on premises PTRACE-GID, EXCH and COPY.
    - §21 catalogues every change against the original.
  - **Lead checks.**
    - The hashes match the report.
    - All 70 units marked CARRIED are byte-identical to composed v5.
    - The JACKAL re-runs reproduce `exact`.
  - **Process.** Recorded in `deviations/w1-v6-author-process/NOTE.md`: the author printed SIA calls from the lead's
    transcript, mistaking it for its own record, a second instance of the pattern. Future resume messages name the
    agent's own record path.
  - **Review.** W-1's own actual gpt-6.1-sol design review started 10:53Z: brief `briefs/w1-design-v6.md`
    (`e0aeed18…`), thread `01a10bb2-3d79-7253-82e0-e36669095fdc`, output to `proposal/v6-review/gpt61-v1`.
- **Pacing, updated.** Free space was 9847558144 bytes at 10:53:13Z, 152441856 below the reserve (JACKAL exact).
  - Seam v5 and PK-0 v2 stay held, although W-1 v6 has landed, because storage keeps falling. The critical-path W-1
    review goes first.
  - This is lead judgment, not S-1 option 4.

- **Pacing (lead judgment, not an operator choice).** Free space was 9875791872 bytes at 09:38:04Z: 124208128 below the
  reserve, and 54571008 bytes less than at 08:38:59Z (JACKAL exact).
  - **What is held.** No new seam drafting starts. Seam v5 is held until W-1 v6 lands or the storage situation changes.
  - **Why.** Each drafting round with its review writes tens of MB. Local space below the vault's local reserve can
    also constrain Codex's vault recovery.
  - **What this is not.** It is not S-1 option 4, which stays the human's choice. The reviews already queued and the
    W-1 v6 draft continue.
- **Package confirmation review** (`package-review/gpt61-v7`): started once the seam v4 review freed a slot.

- **Operator package DRAFT-v10: frozen; confirmation review queued.**
  - **Freeze.** `package-drafts/DRAFT-v10.md` `c54095b9…` (99564 bytes) was frozen at 09:36Z.
  - **Content.** It makes exactly the three corrections of the v9 review:
    - the W-CLOSED summary (one link for regular files only);
    - the C-API v5 `2>/dev/null` deviation named;
    - the v8 review's W-1 closures stated correctly;
    - the seam v4 and PK-0 snapshot timed.
  - **Diff.** The v9-to-v10 diff is `package-frozen/DRAFT-v9-to-v10.diff` (`bc632476…`).
  - **Review.** The actual gpt-6.1-sol confirmation review is queued for a runner slot: brief
    `briefs/operator-package-confirm-v10.md` (`c7a59974…`), output to `package-review/gpt61-v7`.
  - **Next.** If it confirms READY_FOR_OPERATOR, the package goes to the human.
- **C-API PK-0 source review.** It took a runner slot after the package v9 review finished.

- **C-API packet PK-0, source only** (`packets/capi-pk0/`, packet.json `9808145e…`).
  - **Content.** Six new test files: characterization JSON `51ba5ca2…`, guard pages, layout baseline with RECORD_ON_L0
    placeholders, and three test modules. Plus AUTHOR-NOTES and jackal.json (27 calls).
  - **Lead checks.**
    - All nine hashes match the report.
    - All 95 bound S5 inputs match by sha256 and size.
    - No existing file is touched.
    - Sampled JACKAL calls reproduce `exact`.
  - **Executed.** Nothing: no tests, no WORLDLINE code.
  - **What stays open.** The PK-0 gate, a baseline run on L0 in an admitted frame, is blocked by F-1 and S-1.
  - **Review.** Its actual gpt-6.1-sol source review is queued for a runner slot: brief `briefs/capi-pk0-packet-v1.md`
    (`6aca6062…`), output to `packets/capi-pk0/review/gpt61-v1`.

- **Operator package DRAFT-v9: frozen and under review.**
  - **Freeze.** `package-drafts/DRAFT-v9.md` `e3e0e5c4…` (96186 bytes) was frozen at 08:40Z.
  - **Content.**
    - It makes PKG-V8-CURRENT-STATUS.
    - It takes W-1 off the package's readiness criteria: W-1 now has its own review track, and the package reports
      W-1's sealed status. Nothing is lowered.
    - It gives the exact W-CLOSED criteria and the review's finding on which restrictions are new.
    - It labels historical W-1 entries, carries the current C-API rulings, and lists every author process note.
    - Storage to 08:38:59Z: 69637120 below the reserve; Gate 0 −9401633958892/1397; W-1 dispatch −15465745758000/1397
      (JACKAL exact).
  - **Review.** Its actual gpt-6.1-sol review started 08:40Z: brief `briefs/operator-package-review-v9.md` (`949ad2aa…`),
    thread `01a10b38-e42d-73c2-9a6f-aa7af2a60814`, output to `package-review/gpt61-v6`. The brief asks the reviewer
    to judge the scope change itself.
- **W-1 v6** is being drafted by the resumed W-1 author (~08:36Z) as one complete document, for its own review.

- **Root-worker SEAM DESIGN v4** (`designs/claude-root-worker-seam-design-v4`).
  - **Files.** SEAM-DESIGN.md `f65629cb…`, seams.json `92a814a4…`, jackal.json `4d556a45…`, AUTHOR-NOTES.md `0bd92ccd…`.
    Handed back after 08:23:18Z; the hashes match the report.
  - **Lead check.** A lead script verified all 24 carried v3 slices, with no overlaps.
  - **What it answers.** V3-REQ-A..L and RQ-1. It binds the sealed C-API v5 and v6 reviews and reports NF4-1..NF4-13.
  - **Process.** Recorded in `deviations/seam-v4-author-process/NOTE.md`: the author scanned the lead's transcript
    against instruction, saw two lead `sia.ask` calls, stopped, and reports using nothing.
  - **Review.** Its actual gpt-6.1-sol review started 08:26Z: brief `briefs/root-worker-seam-design-v4.md` (`51c4f384…`),
    thread `01a10b2c-017d-7591-b054-07317f89130f`.
- **Storage at 08:25:51Z.** Free 9950502912 bytes, below the reserve. The ext4 proposal is still pending the human.

- **Operator package DRAFT-v8 + W-1 v5: frozen and under review.**
  - **W-1 v5.** `proposal/ISOLATION-STORAGE-PROPOSAL-v5.md` `303205b1…` is a delta over v4, with
    `v5-support/jackal.json` `df5d2a77…`.
    - The lead's composition script reproduces the author's composed text: 466105 bytes, `6cbc9c07…`, kept as the
      derived copy `package-frozen/ISOLATION-STORAGE-PROPOSAL-v5-COMPOSED.md`.
    - The 30 amendments apply exactly once.
    - All 106 change-map rows match v4. One cosmetic error: the Appendix D row's end line says 3325 where v4 ends at
      3324.
    - The four JACKAL values reproduce.
    - Process: `deviations/w1-v5-author-process/NOTE.md` records one `2>/dev/null` against the explicit limit.
  - **DRAFT-v8.** `package-drafts/DRAFT-v8.md` `ce4bb35e…` (87867 bytes) was frozen at 07:36Z with W-1 v5.
    - F-1 describes v5, including the new frame mutation (the observer's write-bit revocation) and W-CLOSED for the
      reviewer to check.
    - The storage readings run to 07:34:22Z: 16417792 below the reserve, Gate 0 −9327286557676/1397, W-1 dispatch
      −15391398356784/1397 (JACKAL exact).
  - **Review.** Its actual gpt-6.1-sol review started 07:36Z: brief `briefs/operator-package-review-v8.md`
    (`02ae0145…`), thread `01a10afe-67f6-73d0-a239-5729094997e0`, output to `package-review/gpt61-v5`.

- **C-API packet PK-0, source only.** The C-API author (`a15cbfbc1dbf895f6`) was resumed ~07:08Z to author it in
  `packets/capi-pk0/`: new characterization tests and the expected-effect JSON.
  - **What it may not do.** Nothing is executed. Run-dependent values are explicit placeholders that must refuse. It
    may not read other sessions' transcripts.
  - **What stays blocked.** The PK-0 gate, a baseline run on L0 in an admitted frame, is blocked by confinement and
    capacity.
- **Storage at 07:05:54Z.** Free 9989894144 bytes, **10105856 below the reserve** (JACKAL exact). The ext4
  root-reserve proposal is pending the human.

- **C-API DESIGN v6** (`designs/claude-capi-boundary-design-v6`).
  - **Files.** DESIGN.md `cfa0dca9…`, APPENDIX-BINDINGS.md `9f9f3dfa…`, decisions.json `357bb2d4…`, jackal.json
    `34a7a3ab…`, AUTHOR-NOTES.md `414fd736…`. It was handed back ~06:12Z.
  - **What it answers.** V5-RC4-GATE-EXCEPTION, with a fixed `CAPI_WFX_PROTOCOL` constant and controls MX9–MX17, and
    V5-RC4-QUAL-CAPTURE, with (d1)–(d4) over the C_API spec and body and `core/worldline.ads`, and controls MQ15–MQ24.
    It reports latent defects L13–L16; L16 is the relayed NF-5 wording, which the author checked itself.
  - **Lead checks.** The hashes match the report. The carried slices are 5/5 DESIGN and 14/14 A-BIND against v5. J69
    reproduces `exact`.
  - **Process.** Recorded in `deviations/capi-v6-author-process/NOTE.md`. It notes that the author read the lead's
    transcript after its compaction, an indirect path to other lanes' summaries, and that it executed its sketch in
    memory again as a self-check.
  - **Review.** Its actual gpt-6.1-sol review started 06:14Z: brief `briefs/capi-design-v6.md` (`fc49ff6a…`), thread
    `01a10ab3-0fe6-7e42-b915-7f2e051d275f`.
  - **Runner slots.** All three are now in use (D1 stalled, seam v3, C-API v6). The package v8 review will wait for a
    slot, and waiting interrupts nothing.

- **Root-worker SEAM DESIGN v3** (`designs/claude-root-worker-seam-design-v3`).
  - **Files.** SEAM-DESIGN.md `a0f2f411…`, seams.json `093f3117…`, jackal.json `8cce45e3…`, AUTHOR-NOTES.md `dd382e1b…`.
    It was handed back ~05:55Z, and the hashes match the report.
  - **Lead check.** A lead script verified all 43 carried v2 slices, with no overlaps.
  - **What it answers.** V2-REQ-A..L and RQ-1. It also reports new author findings NF-1..NF-11; NF-5, about the C-API
    v5 §19 wording, was relayed to the C-API v6 author as information.
  - **Author process.** No refusals, no interruptions, no JACKAL calls (its counts are observed), and one `sia.ask`.
  - **Review.** Its actual gpt-6.1-sol review started 05:58Z: brief `briefs/root-worker-seam-design-v3.md`
    (`0e2e6f5d…`), thread `01a10aa4-7a2d-7973-ad50-317bec908872`.
- **W-1 v5.** The W-1 author was resumed ~05:59Z for the six W-1 corrections of `gpt61-v4`; output goes to
  `proposal/ISOLATION-STORAGE-PROPOSAL-v5.md`.
- **DRAFT-v8.** The lead is preparing it for PKG-V7-AUTHOR-RECORDS and current facts.

- **C-API DESIGN v6.** Drafting started ~05:07Z. The v4/v5 author (`a15cbfbc1dbf895f6`) was resumed for
  V5-RC4-GATE-EXCEPTION and V5-RC4-QUAL-CAPTURE; output goes to `designs/claude-capi-boundary-design-v6`.
  - **Its limits:** strict read-only Bash (no `mkdir` or redirection of any kind), `sia.ask` at the start, all eight
    Ada skills, JACKAL in groups of at most four.
  - **Isolation from parallel work:** it may not read the seam v3 draft or the package review in progress.
- **C-API DESIGN v5** (`designs/claude-capi-boundary-design-v5`). Its review sealed ~05:05Z (verdict table).
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
