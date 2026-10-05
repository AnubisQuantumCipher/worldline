# INSTALL-ORDER.md — the frozen §16 setup/verification/adoption order

This maps 1:1 to v11 §16, with the critical-premise E0 review gate of §16 step 5b (W1-V9-
PREMISE-ORDER) placed BEFORE O-1 installs the sudo rules, and the §16.1 operator package
(O-1..O-5) called out. Every command is TEXT; **nothing here is executed by this package**,
and this lead session (the drafting E0 actor) runs NOTHING privileged. Executor column:
**lead** = unprivileged `sicarii` / review subagents; **operator/Codex** = privileged, holds
the human's authentication.

Legend for gates: **[REVIEW]** independent review; **[GATE 0]** runbook capacity gate;
**[OP-APPROVE]** operator's reserved approval (not a new gate).

| # (§16) | Step | Executor | Gate / review |
|---|---|---|---|
| 1 | Independent review of the v11 design (independent Claude review subagent, the review track since 2026-10-05; §23) | lead (review subagent) | **[REVIEW]** design |
| 2 | Frame v6-W1 code implemented, frozen in `SOURCE_FRAME` (members 0644, dirs 0755; inventory records `install_root` + `source_frame`) and reviewed AS CODE, review sealed in `<SOURCE_FRAME>/review/…` (REVIEW): front, writer (incl. `selftest` — no set-ID/cap object, no installed-reachable test switch), RL + its view + seccomp program, launcher, child, observer, final pass, censuses + root scan, channels, commits, journals, fallback journal, exports, complete capture, recovery, selftest verbs, and §13.2 S-5 code-review items. Phase E0 of §13.2 (source discharges S-1..S-4, S-6 + benign unprivileged observations) runs before/alongside | lead (author) + review subagent | **[REVIEW]** code; produces REVIEW seal |
| 3 | Concrete setup inventory (fixed numbers; filled prestate P1-P30 WITH the extended P-NOOWNER route inventory of W1-V9-NOOWNER-SCOPE, §5.3/§11.3/O-1; exact script texts + digests, S-J if images; the instantiated reachable set of §11.4 — **67 / 104 states incl. the userdel co-removal states**; expected ACL texts; sudoers + sshd bytes; scope properties; the seccomp program's bytes; the §16.1 operator package), reviewed independently | operator/Codex produces; lead review subagent reviews | **[REVIEW]** concrete inventory |
| 4 | Gate 0, SETUP stage, on a fresh reading | lead | **[GATE 0]** setup |
| 5 | Operator approval of the concrete setup (existing reserved authority, not a new gate) | operator/Codex | **[OP-APPROVE]** |
| **5b** | **Independent review of the E0 source discharges of the critical premises** (P-KSRC, P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP, P-ASYNC: S-1 with the running-kernel/build-id binding, and S-2's readings), **COMPLETED BEFORE O-1 RUNS** (W1-V9-PREMISE-ORDER). Reason: once the S1 rule exists, A1 can `writer.py selftest` and drive installed RL; the host-DAC-safety premises must be reviewed before the sudo rules exist. A refuted critical premise stops the plan and opens a redesign; no installed use precedes this review | lead (review subagent) | **[REVIEW]** critical-premise E0 — **HARD GATE before 6/O-1** |
| 6 | The operator runs, or explicitly authorizes, **S-0 → S-I** (and S-J if images) and the operator package E1 probe fixtures (§16.1); **O-1 (the sudo rules among them) runs ONLY AFTER step 5b**. S-R only after a stopped script, by explicit operator choice | operator/Codex | gated by 5b; O-2′/O-ASYNC/O-3/O-4/O-5 as scheduled |
| 7 | Gate 0, SELFTEST stage; lead verification (§11.6), selftests, and phase E2 of §13.2 (I-1..I-8, under W1-V9-PLAN-CONSTRAINTS gating for I-7) | lead (selftest verbs) + operator (privileged captures) | **[GATE 0]** selftest |
| 8 | Installed-identity, baseline (incl. the candidate view baseline, EVIDENCE ONLY, §11.6), probe and source-reading evidence (E0/E1/E2) reviewed independently, sealed in `<SOURCE_FRAME>/review/…` (INSTALLED_REVIEW) | lead (review subagent) | **[REVIEW]** installed evidence; produces INSTALLED_REVIEW seal |
| 9 | Gate 0 with the adopt/materialize-stage expression; then `front.py adopt …`: W commits the fresh installed-frame adoption record at `runs/records/adoption-<I>/lead-adoption.json` (§4.6) — whose review-provenance joins require the provenance of the review mechanism ACTUALLY used (§23), not a gpt-6.1-sol rollout | operator/Codex (privileged) + lead | **[GATE 0]** adopt; **BLOCKED**, see below |
| 10 | Gate 0, DISPATCH stage; only then `materialize` and dispatch, each under fresh original admission | operator/Codex + lead | **[GATE 0]** dispatch |

## The two ordering invariants (stated so a reviewer can check them)

1. **No step authorizes the next by inference.** Each gate/review is independently satisfied.
2. **Critical-premise E0 review precedes O-1 (the sudo rules).** Step 5b is a hard gate before
   any part of step 6 that installs the S1/RL rules. This is the fix for "a check must not pass
   by not asking": installed privilege must not precede the reviewed discharge of the premises
   the identity-mapped design's host-DAC safety rests on.

## Adoption is BLOCKED (not reachable by v11)

§16 is explicit: the review-provenance join change (§23) is itself a change to an original
admission join (HANDOFF.md:173; complete-phase1-prompt.txt:60), made under the operator's
~17:05Z direction, and it is **NOT reviewed**. Adoption therefore stays blocked until that
change is itself reviewed in the frame-design revision that follows the W-1 review. **v11 does
not reach adoption (steps 9-10).** This package is uninstalled source; it changes none of that.

## The §16.1 operator package (prepared, NOT executed — all operator/Codex)

| Item | Contents (summary) | Serves |
|---|---|---|
| O-1 | the setup (S-0, S-A..S-E, S-H, S-I; S-J with images) + helpers, expected outputs, sudoers/sshd bytes, the frame staging copy, the instantiated reachable set (67/104), S-R; and the operator-produced prestate inventory extended per W1-V9-NOOWNER-SCOPE (every sudoers rule of any principal resolving to W/N; every polkit grant to any subject) | every installed step; P-NOOWNER route inventory |
| O-2′ | **operator-only** sacrificial probe fixtures: a set-user-ID-root program and a `cap_dac_override+ep` file-capability program (built from reviewed source, created/destroyed by the operator harness A6 on a sacrificial mount, NEVER by RL `selftest` or any installed/S1/RL-reachable path); a loop device with a dm failure target; a small sacrificial ext4 for ENOSPC | I-1 (P-NOSUID/P-NOCAP), P-COMMIT, P-SYNCPROV, P-ENOSPC |
| O-ASYNC | the asynchronous-holder refutation package for P-ASYNC/P-RELEASE — per holder class of §9.8 N4, a sacrificial exercise whose ONLY verdict is the byte-equality state predicate of §13.1. **Detailed procedure is OPEN**, authored by the operator; this package supplies obligation + predicate only | P-ASYNC/P-RELEASE (refute-only) |
| O-3 | P-SUDO before/after capture around one invocation of each frame rule by a selftest | P-SUDO |
| O-4 | the §15.1 rollback as a reviewed script set + captures + retained-tree manifests, rehearsed on a sacrificial copy | §15.1 rollback states |
| O-5 | S-R classification run against the rehearsal: every vector of the reachable set (67/104, incl. X1-X4/W_A/W_B), continued and reversed, with S-R's reverse rules (no failing `groupdel`) | P-SR |

The critical-premise E0 source discharges (S-1, S-2 for P-NOSUID/P-NOCAP/P-NOOWNER/P-SECCOMP/
P-ASYNC) and their independent review complete **before** O-1 runs (W1-V9-PREMISE-ORDER).
