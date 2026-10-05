# WORLDLINE Phase One — convergence and the operator-reserved gate

**Prepared by the Claude Code lead, 2026-10-05 ~23:00Z. This is the exact reviewable package and the single blocked
row for the operator, per the handoff rule. Nothing here is a claim that Phase One is complete.**

## 1. What is done (independently reviewed, sealed, verifiable)

Four of the five Phase One work-products are ENDORSED at design/source level by independent Claude review subagents
(each sealed under `tools/seal_claude_review.py`; freeze hashes in STATUS.md). Every one cleared with zero required
changes on its final round:

| Work-product | Verdict | Sealed review |
|---|---|---|
| F32 test-fixture fix (R-A) | ENDORSED (design); delta lane `lanes/f32-r-a-delta-v1` prepared and verified | `designs/claude-f32-resolution-v6/review/claude-v1` |
| D1 native Big_Integer cost correspondence | ENDORSED (design); A-ROW + Theorem H-A, no caps/refusals | `designs/claude-native-bigint-d1-design-v6/review/claude-v1` |
| PK-0 C-API characterization packet | ENDORSED (source); 725 cases | `packets/capi-pk0-v4/review/claude-v1` |
| Root-worker seam design | ENDORSED (design) | `designs/claude-root-worker-seam-design-v8/review/claude-v1` |

W-1 confinement (the fifth) has reached DESIGN COMPLETENESS at v11: all nine W1-V9 required changes are
CLOSED_AT_SPEC_LEVEL (eight substantive + the review-provenance change correctly stated with adoption blocked), the
form is clean and self-contained (lead- and reviewer-verified full change-map parse; 100/100 carried units
byte-identical to v9), and nothing is weakened. Sealed: `proposal/v11-review/claude-v1`.

## 2. Why nothing is ENDORSED further, and why the lead cannot proceed alone

Every endorsed work-product shares ONE remaining gate: their execution. The D1 strict proofs, the PK-0 baseline run,
the F32 matching-source test run, and the seam SPARK body + fault campaign all require GNATprove / the test suite to
run inside an ADOPTED SCRATCH FRAME. The frame cannot be adopted until W-1 confinement is established.

W-1 v11 is NOT_ENDORSED for a STRUCTURAL reason, not a fixable design defect (confirmed by its independent review): the
confinement rests on obligations that can only be established by EXECUTION, and the critical ones require OPERATOR
PRIVILEGE:
- V5-B01, V5-B02 (stale-file revalidation; TOCTOU-on-frame-mutation custody) — OPEN.
- ~30 NAMED_UNESTABLISHED kernel/systemd/sudo premises (P-KSRC, P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP, P-ASYNC, …).
- §21 preservation established for no V/C/D row yet.
- The §23 review-provenance join change (D-LEAD-REVIEW-PROVENANCE) needs its own independent review before adoption.

Drafting further W-1 revisions will not change this: the remaining required changes are all execution-bound, not
design changes.

## 3. The single blocked row — RESERVED FOR THE OPERATOR

**Privileged W-1 setup and frame adoption.** This is reserved (sudo / install / production per START). The exact,
prepared steps are W-1 v11 §16 (order) and §16.1 (operator package O-1..O-5): the account/namespace-owner creation,
the sudo and polkit rules, the frame install and its code review, the privileged lab probes (E1/E2), rollback and its
rehearsal. The lead has written them as an exact reviewable plan; the lead does not execute them.

The staged-evidence plan (W-1 §13.2) splits the work:
- **E0 (lead may run before endorsement):** unprivileged, non-mutating source readings (S-1..S-6; S-1 binds the
  running kernel image/build-id to the package) and benign observations on the lead's own sacrificial objects. These
  produce the source-level premise discharges that the premise-order review then checks.
- **E1/E2 (operator):** every privileged probe, the frame install, and the adopted-frame runs.

Note: several E0 premise discharges (P-NOSUID/P-NOCAP/P-ASYNC kernel-boundary enumeration) fall in the area a safety
classifier stopped earlier; the lead keeps those at the obligation level and does not produce the detailed procedures.
They are operator-prepared.

## 4. What the lead continues (independent, authorized, not operator-gated)

- The §23 D-LEAD-REVIEW-PROVENANCE join change implemented in the frame source and sent for its own independent
  review (unblocks the adoption-join question under the human's 17:05Z review-track direction).
- The clean, non-sensitive E0 source readings (e.g. S-1 kernel/package binding for P-KSRC) if and when the operator
  wants the lead to begin producing E0 discharge evidence.

## 5. What the operator decides now

1. Whether to perform the privileged W-1 setup per §16 / §16.1 (the gate for everything downstream).
2. Whether the lead should begin the lead-executable E0 source-reading discharges now.
3. Password rotation reminder stands (sudo-cutover kit): the 2026-09-29 exposure.

Phase One's exit — zero unproved / zero justified / zero pragma Assume with complete reports — cannot be reached until
the frame is adopted and the proofs/controls run. That is now the one critical path, and its first step is reserved to
the operator.
