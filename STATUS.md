# WORLDLINE Phase One: Claude lead status (live index)

As of 2026-10-04 ~19:30Z. This file supersedes the stale status sections of the read-only
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

**Where it comes from.**
- Large files modified since 18:49Z include:
  - `~/.codex/thread_history_1.sqlite` (2.3 GB) and `~/.codex/logs_2.sqlite` (540 MB), which every codex exec review
    writes;
  - SIA database files;
  - a 166 MB Codex rollout from a non-lead session.
- The lead's own measurable additions since then are about 100 MB: review-record copies, job scratch, review rollouts.

**Lead response.**
- No new reviews, agents or copies are started.
- Three reviews keep running as instructed. The queued D1 v3 review is held at the human's call.

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
| D1 native design v2 | NOT_ENDORSED (V2-RC1..RC6; RC4–RC7 still open) | v3 being drafted |

## Candidate packets (drafted; untested engineering hypotheses)

| Packet | Content | State |
|---|---|---|
| 10 | resource_ledger additive steps (D1382, D1388) | overlay iter-3-core |
| 11 | run-ledger wire Decode_Native invariants (D1553) | overlay iter-3-core |
| 12 | Iterative body-local witnesses (4 contracts-recursive notices) | overlay iter-3-core |
| 13 | Iterative `Prefix_Tail` in resource_reservation_transition (D1431, D1432) | wt-1 only. Notice removal is an untested hypothesis until matching-source evidence exists. |
| 14 | Chain-authority `Replay` induction lemma plus call-site facts (D1554, D1555) | wt-1 only. Adds checked-build Ghost cost, which is under D2. |

Ledger lineage (`wt-1/workflow`): 3187 items, 3026 OPEN, 161 DRAFTED, 0 verified.

## D2 checked-build cost (static analysis; actual gpt-6.1-sol review running)

Source: `wt-1/designs/claude-d2-checked-ghost-inventory-v1` (INVENTORY.md `e5b9984d…`). Everything here is derived
by reasoning; nothing was measured. JACKAL exact, formal=false, for the arithmetic.

**Hazards in the checked (`-gnata`, default) build:**
- **Chain replay is exponential.** A successful replay costs 9·2^(n+1)−n−10 reference evaluations: 18412 at n=10,
  19327352792 at n=30. The release build is linear.
- **Resource-ledger compute is Θ(N⁶).** At an 804-byte buffer the checked build raises `Storage_Error`, which the C
  wrapper maps to 255.
- **Quantity references** are Θ(L⁶)–Θ(L⁷).

**Packet deltas, to be weighed before any packet is promoted:**
- **Packet 14** raises the replay cost to 11·2^(n+1)−2n−14. Still exponential, now worse.
- **Packet 13** raises `Prefix_Tail`/`Prefix_Decomposition` costs, Θ(m³)→Θ(m·S³) and Θ(m·S³)→Θ(m²·S³).
- **Packet 12** leaves every growth class unchanged.

D2 stays OPEN.

## In progress

- C-API boundary DESIGN v3 (drafting agent).
- D1 DESIGN v3 (drafting agent).
- D2 checked-Ghost cost inventory (analysis agent, static reasoning only).
- Consolidated operator package. Current draft: `work/claude-operator-decision-package-v1/DRAFT-v2.md`.
  - It still has to incorporate the final frame v5 report, the W-1 proposal, D1 v3 with its review, C-API v3 with
    its review, and the D2 inventory.
  - Then it gets its own actual gpt-6.1-sol review before going to the human.

## Isolation and records

- Edits that would land in the guarded tree go to `wt-1` (see `ISOLATION.md`).
- The workflow tree is read-only.
- Review runner records are copied to `work/claude-lead-isolation-v1/review-records`. Snapshot manifests are computed
  before the manifest file exists; the `T1915Z` defect is recorded.
