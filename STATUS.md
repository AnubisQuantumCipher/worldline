# WORLDLINE Phase One: Claude lead status (live index)

As of 2026-10-04 ~22:12Z. This file supersedes the stale status sections of the read-only
`work/claude-workflow-v1/REPAIR-MAP.md`, which stays preserved.

**Every original Phase One obligation is OPEN.** Nothing below is proof, source, native or Phase One acceptance.

## Gates that block proof dispatch (all in force)

| Gate | State | Where |
|---|---|---|
| Confinement / frame qualification | **BLOCKED.** Frame v5 is UNQUALIFIED (final actual gpt-6.1-sol report). V5-B01 requires custody that *prevents* the admitted generation from changing before use. V5-B02 requires enforced location custody for every frame mutation. No unprivileged design meets either. | frame v5 `review/gpt61-v1`; `frame-v6-PLAN.md` |
| Capacity | **BLOCKED.** Gate 0 v4.1 requires 9304350902252/1397 bytes (JACKAL exact, formal=false) above the 10 GB reserve for one unit run. The margin at 18:49Z was negative. The backup service is failed. | `RUNBOOK-first-proof-iteration.md` |
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

**Lead response.**
- No discretionary agents or copies are started.
- The D2, root-worker seam and C-API v3 reviews have sealed. The D1 v3 review started when a runner slot freed
  (20:41Z) and is still running.
- The next review is the instructed one of the consolidated operator package, after D1 v3 seals.

**Incident (disclosed).** A `find` over `~/.local` listed file metadata under `~/.local/share/sia/.gbrain/`. That
breaks the machine rule "never access ~/.local/share/sia/.gbrain/ directly". It was metadata only: nothing was read or
written. Future scans exclude that path.

## Independent review verdicts (actual gpt-6.1-sol, sealed, freeze verified)

| Item | Verdict | Next |
|---|---|---|
| Scratch frame v1–v5 | All UNQUALIFIED. v5: V5-B01, V5-B02; the compact identity records and four residuals were ruled acceptable. | The W-1 proposal (candidate), then frame v6-W1, only after an operator decision |
| Composition commonV5-alpha (packets 01, 02, 04) | QUALIFIED_SOURCE_COMPOSITION | — |
| Composition commonV5-beta (+05..09) | QUALIFIED_SOURCE_COMPOSITION (rulings 7a/7b; notes N on packets 05/06 metadata) | — |
| C-API design v2 | ENDORSED_WITH_REQUIRED_CHANGES (RC1–RC6; LD4 rejected as written) | v3 being drafted |
| D1 native design v2 | NOT_ENDORSED (V2-RC1..RC6; RC4–RC7 still open) | v3 drafted; its review is running |
| C-API design v3 | ENDORSED_WITH_REQUIRED_CHANGES (RC1–RC3 CLOSED_AT_DESIGN_LEVEL; V3-RC4 binding spec, V3-RC5 PK-0 effect classification, V3-RC6 cost map NOT_CLOSED; D-13 operator choice on a concrete reviewed packet before PK-7; N-06 at deployment; N-01 lead-owned) | DESIGN v4 |
| Root-worker seam design v1 | ENDORSED_WITH_REQUIRED_CHANGES (RC-01..RC-12; rulings D-1a..D-9a: `Delegate=yes` not endorsed, the frontier control cannot be retired by the lead, native custody-phase legality is mandatory) | v2 after operator decisions |
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

## In progress

- **Operator package.** DRAFT-v4 is frozen (`e36f517c…`, 35034 bytes, plus a copy in `wt-1/package-frozen`). Its
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
