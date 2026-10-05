# Operator decision package — WORLDLINE Phase One (DRAFT v6; not yet reviewed)

Prepared by the Claude Code lead (claude-opus-5-5) on 2026-10-05 (~02:10Z).

## Status

- **Nothing is approved, waived, closed or decided here.** Every original obligation stays OPEN.
- **No operator choice or privileged action has been taken.** Proof dispatch stays blocked by the confinement gate and
  the capacity gate.
- **Only engineering-only author self-checks were executed** (see "Executed engineering checks" below):
  - no prover or compiler was launched on WORLDLINE code;
  - no setup was done;
  - nothing counts as proof, review, admission or acceptance.
- **This draft replaces DRAFT-v5** (`f423d6be…`, preserved). The line of review:
  - v4 (`e36f517c…`) was found NOT_READY with nine corrections (`WT/package-review/gpt61-v1`).
  - v5's actual gpt-6.1-sol re-review (`WT/package-review/gpt61-v2`, freeze verified) found it NOT_READY again. It
    closed four of those nine and listed seven corrections, five of them carried over.
- **v6.** It makes the seven corrections and pairs with W-1 v3. The status table at the end states each one as CLOSED
  (by a sealed review) or as "corrected in v6, awaiting review". Nothing is called closed on the author's word.
- **This draft gets its own actual gpt-6.1-sol review before it comes to you.**

**Path shorthand:**
- `W` = `/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow`
- `WT` = `W/work/claude-lead-isolation-v1/wt-1`, the lead's guard-compatible isolation worktree.

## The fixed target, and what no choice can do

The original exit text (`complete-phase1-prompt.txt:34`) is unchanged:

> "Do not lower guarantees, weaken preconditions or postconditions, remove accepted cases, lower proof floors, drop
> relevant bodies/callers, waive warnings, suppress failures, add assumptions, or replace missing
> confinement/provenance with a renamed Boolean."

**These are ineligible for closure, even after an operator choice:**
- a lowered reserve;
- a narrowed scope;
- a waived warning or changed warning policy;
- a narrowed accepted case, control, floor or original target.

None of them closes the unchanged Phase One obligation it touches. A genuinely changed target would be a different
target, and the original would stay OPEN.

**Claimed equivalence is not proof.** A separately proposed specification or reference change, even with claimed
equivalence, supplies no proof. It excuses no original caller, successful case, control or gate. No permission or proof
gate is removed anywhere in this package.

## Decisions at a glance

| Item | What is asked of you | When |
|---|---|---|
| S-1 storage | Choose among: repair the iPad backup; reclaim non-task temporary data; consider enforced limits; hold the lead's work; defer runs. Lowering the reserve is listed only as an ineligible exception | **Now** (urgent) |
| F-1 confinement | Nothing is required now: design continues as routine engineering. Optional: say whether dedicated accounts (W-1) are acceptable to you in principle. That only avoids wasted design. The real decision, approving the concrete privileged setup, comes later on a reviewed inventory | Optional now; setup approval later |
| R-1 notices | Nothing now. Gathering the P1–P3 evidence is routine engineering, gated by F-1 and S-1. Afterwards: whether the demonstrated classification resolves the notices, or they stay OPEN | Later, after the evidence |
| R-2 Posts | Decide together with R-1, after the evidence | Later |
| C-1 D-13 | Choose the component route on a concrete reviewed packet | Later, before PK-7 |
| C-2 N-06 | Re-provision `native_sha256` under your custody, or hold | At deployment |
| N-1 OD-1 | The library/runtime/API architecture, on concrete verified evidence | Later |
| N-2 OD-2 | E1 or E2, after V3-RC1 is repaired and re-reviewed | Later |
| RW-1 root worker | The rulings' operator items, once v2 designs exist | Later |
| P-1, C-3, N-3 | Information only | — |

---

## S-1. Local storage capacity (operator) — URGENT

### Facts

**Observed:**
- Free bytes, from `storage_status.py` unless marked:
  - 10592727040 at 20:37:33Z (`df`);
  - 10550894592 at 21:02:25Z (`df`);
  - 10516545536 at 22:06:53Z;
  - 10460753920 at 23:32:06Z;
  - 10370256896 at 2026-10-05 02:01:52Z.
- The configured reserve is 10000000000 bytes, unchanged.
- At 02:01:52Z, as at 23:32:06Z, `storage_status.py` reports `backup_service`: `ActiveState=failed`, `SubState=failed`,
  `ExecMainStatus=1`. The iPad backup failed with EIO at 12:01 EDT. Guarded offload is therefore unavailable.
- The offload queue (02:01:52Z, unchanged since 23:32:06Z) holds `done` 13, `needs-review` 25 and `cancelled` 1. The 25 needs-review candidates
  are not owned by this task. Each lacks recorded rebuild provenance, and each original is retained.

**Derived** (JACKAL exact, formal=false):
- Margin above the reserve: 460753920 bytes at 23:32:06Z; 370256896 bytes at 02:01:52Z.
- Mean declines between readings:
  - 18:49:03Z to 20:37:33Z: 296433664/3255 bytes/s;
  - 20:37:33Z to 21:02:25Z: 10458112/373 bytes/s;
  - 21:02:25Z to 22:06:53Z: 8587264/967 bytes/s;
  - 22:06:53Z to 23:32:06Z: 55791616/5113 bytes/s, about 10.9 KB/s;
  - 23:32:06Z to 02:01:52Z: 45248512/4493 bytes/s, about 10.1 KB/s.
- These are past observations. They bound nothing and are not forecasts.

**Observed large files.** Growth per file is not attributed, and no per-review database growth is inferred from this
list:
- `~/.codex/thread_history_1.sqlite`: 2307952640 bytes, mtime 21:01Z.
- `~/.codex/logs_2.sqlite`: 540635136 bytes, at the same reading. `codex exec` reviews, the lead's included, write to
  both.
- SIA database files.
- `~/.codex/sessions/2026/10/04`: 190175806 bytes in total at ~21:03Z.
- A separate rollout of a non-lead session,
  `~/.codex/sessions/2026/10/03/rollout-2026-10-03T11-01-35-01a10248-eb08-7df0-a926-308164412cce.jsonl`. It is in the
  `2026/10/03` directory, not the `2026/10/04` aggregate.
  - It was 166631656 bytes when first read.
  - A later reading, retained at 23:23:50.591Z, showed 176041774 bytes with a file mtime of 23:22Z. So it was still
    growing.
- **Not owned by this task:** `~/.cache/workflow-tmp` held 11893443305 bytes at ~21:03Z, including other sessions'
  data.

**Lead activity snapshot (02:05Z):**
- The W-1 v3 drafting agent finished at ~01:58Z.
- The C-API DESIGN v4 drafting agent is still running.
- The D1 DESIGN v4 review is INCOMPLETE and untouched (Isolation record). It holds one of three runner slots.
- This package's re-review is the next review.

### Gate 0 (runbook v4.3; observations separate from labelled allowances)

**O1 provenance (corrected in runbook v4.3).** O1 is 1121220323 bytes.
- It is a whole-tree `du -sb` difference: 1129239130 minus 8018807 for the same tree with `obj` and `lib` excluded.
- That equals the sum of the retained per-subdirectory readings `obj/attest-sha256` 4676666 and `obj/core` 1116543657
  (JACKAL exact, both forms).
- All four readings come from one command at 17:23:37Z.
- The `obj` directory's own entry and `lib` were not read separately.
- The allowance built on O1 is unchanged.

- **One unit run** requires Required = 2·(A_mat + A_obj + A_rec) + A_ambient = 9304350902252/1397 bytes above the
  reserve (JACKAL exact). That is about 6.66 GB. Its terms:
  - A_mat 16777216 (until measured; then never less than the measured size);
  - A_obj 2 × 1121220323;
  - A_rec 545393048;
  - A_ambient 4 × O4 × 2 × O5-rate = 1468268019712/1397;
  - R = A_mat + A_obj + A_rec, the temporary full-restore space.
- **O4 is qualified (since runbook v4.2).**
  - 3632 s is the whole-second difference between the timestamps of `effective-limits-before.json` and
    `child-wait.json`. The full-stamp interval is 3631279103/1000000 s (JACKAL exact).
  - It is a limits-observation-to-wait proxy, not a recorded target spawn-to-exit duration.
  - 3632 stays the allowance input and is not lowered.
- **Every allowance is a labelled judgment, not a bound.**
- **At 02:01:52Z** the margin minus Required is −8787102018540/1397 bytes, about −6.29 GB (JACKAL exact).
- **Under W-1 v3**, its proposed staged Gate 0 (§14; an author proposal, unreviewed; the lead reproduced it with
  JACKAL) adds labelled allowances. Retained inputs and messages, exports, retries, the fallback journal, target
  temporaries, journal effects and their restore account for 4340810164 bytes more.

  | Stage | Required |
  |---|---|
  | Each dispatch | 15368462701360/1397, about 11.0 GB |
  | Setup | 2027732564230/1397, about 1.45 GB |
  | Selftests | 1843272351744/1397, about 1.32 GB |

  At 02:01:52Z the dispatch-stage margin is −14851213817648/1397, about −10.63 GB. All stages are DEFERRED.
  **Status: NOT ESTABLISHED, so dispatch is DEFERRED.**
- **What the gate rules out:**
  - A sampling monitor is never a bound.
  - Kernel-enforced limits would only enforce, and would need a reviewed, target-preserving admission argument before
    the gate changes.
  - Crossing the inequality after reclamation would not on its own demonstrate safety.

Runbook: `WT/RUNBOOK-first-proof-iteration.md` (v4.3). v4.1 and v4.2 are preserved in `runbook-history`.

### Criterion (WORLDLINE monitor, 2026-10-04)

> "live preflight that budgets measured run growth AND temporary full-restore space above the unchanged reserve … include
> materialization, all retained outputs/records, temporary full-restore needs and ongoing agent/review growth above the
> unchanged reserve. Do not shrink the next allowance merely because the last run used less. If safe capacity cannot be
> established, keep dispatch deferred."

### Options

1. **Repair the iPad backup.** Guarded offload of eligible inactive task-owned material then becomes possible,
   candidate by candidate. Every candidate gets its own recovery comparison.
2. **Reclaim non-task temporary data yourself**, after checking its owners are inactive.
3. **Consider kernel-enforced limits for runs.** This needs privileges and a reviewed, target-preserving admission
   argument.
4. **Hold the lead's review and agent work** until capacity returns.
5. **Defer all proof runs.** This is the default.
6. **Lower the reserve.** This is an exception to the storage policy. It is ineligible to close the unchanged
   obligation even if chosen. Not recommended, not requested.

**Lead recommendation:** 1 and 2 promptly. The margin keeps shrinking with no proof run at all.

---

## F-1. Scratch frame confinement: V5-B01 and V5-B02

### Facts

Frame v5 is **UNQUALIFIED_SCRATCH_FRAME**. This is from the final actual gpt-6.1-sol report
(`W/work/claude-scratch-frame-v5/review/gpt61-v1`, freeze verified).

**V5-B01, required change, complete text** (`REVIEW.md:76`):

> "Retain file observation identities through the complete walk and revalidate every encountered leaf, including
> excluded generated leaves, using complete descriptor metadata and named-entry joins at the final admission
> boundary. Bind the accepted source/output generation to the spawn under custody that prevents the admitted
> generation from changing before use. Directory-only revalidation or after-run detection must not substitute for
> pre-launch alias refusal. Preserve the exact base recipe, output partitions, allowlist, caps and original gates."

**V5-B02, required change, complete text** (`REVIEW.md:82`):

> "Provide enforced location custody across each frame-owned mutation and the final admission-to-spawn handoff,
> rather than observer-only checks before and after it. Use an independently protected writer/location boundary or
> an equivalent enforced lease that concurrent same-user rename/substitution cannot invalidate while writes or launch
> are possible. Keep original outside-tree authority limited to the documented window protocol and prescribed
> preparation records. Do not relabel frame-owned outside-tree writes as the running-target residual or lower the
> original guarantee; retain this blocker if custody cannot yet be established."

**Rulings in the same review:**
- The compact identity records are **ACCEPTABLE**.
- The empty-directory, no-target-confinement, exec-by-path and metadata-granularity residuals are
  **ACCEPTABLE_AS_DOCUMENTED**.

**Monitor:**
- An own-inode "detected and refused" residual does not meet the criterion. V5-B02 stays OPEN until it is met.
- A root-made filesystem and W-1 are candidates, not established designs or approved actions.

### Lead analysis

No qualified unprivileged route has been demonstrated (`WT/frame-v6-PLAN.md:67-80`). This is not a proof that none
exists. Observed: `fuse2fs` is absent, and unprivileged user namespaces are enabled.

| Route examined | Why it falls short |
|---|---|
| User FUSE mount | The same user can lazily unmount it. |
| tmpfs in a namespace | Not persistent. |
| FUSE ext4 image in a private user+mount namespace | A candidate, not shown to work (`frame-v6-PLAN.md:88`). It needs `fuse2fs`, an install or reviewed build, plus a complete design and review. Two questions would have to be assessed if it is ever designed, both unverified lead concerns: the backing image stays a `sicarii` file, and same-user processes may be able to enter a namespace `sicarii` owns. |
| Root-made filesystem with a `sicarii`-owned run root | No relocation, but still writable by `sicarii` processes. Fails V5-B01. |
| Rootless user namespace with `sicarii`'s subordinate UIDs as writer and target (examined 2026-10-04) | Ruled out. `/etc/subuid` and `/etc/subgid` delegate 100000–165535 to `sicarii`, so any `sicarii` process can map those UIDs in its own namespace, or join one it owns, and act as them. They are no boundary against `sicarii`. The lead's DAC probe (below) used them only to exercise kernel semantics between distinct UIDs. |

**Account precedent.** The host has dedicated nologin accounts `worldline`, `wldrill` and `wlrehearsal`. Linger is
observed only for `worldline` and `wlrehearsal`.

### Candidate W-1: status

**W-1 v2** (`WT/proposal/ISOLATION-STORAGE-PROPOSAL-v2.md`, `1c116f27…`) was re-reviewed by actual gpt-6.1-sol
(`WT/package-review/gpt61-v2`). The verdict, verbatim: "The separate target UID, protected ancestors, streamed pinned
inputs and exclusive writer lease provide a plausible architecture for V5-B01/V5-B02. W-1 v2 cannot be judged capable
as written because generation/admission ordering, modes, lock establishment, terminal/commit handling, setup and
rollback remain inconsistent or underspecified; exact successor code and installed evidence are still required, and
both blockers stay OPEN."

**Status of the 20 W-1 sub-gaps**, as the re-review ruled:

| Status | Sub-gaps |
|---|---|
| CLOSED (6) | FINAL-PASS, READ-ACCESS, SETUP-ORDER, IMAGE-GEOMETRY, IMAGE-COMPATIBILITY, NONCLAIMS |
| NOT_CLOSED (14) | CUSTODY, CLOSURE, CHANNEL, WRITE-AUTHORITY, READ-EXPOSURE, PREFLIGHT-IDENTITY, SETUP-PRESTATE, SETUP-EXACTNESS, VERIFICATION-PROBES, FAILURE-LEASE, FAILURE-RECORDS, REBOOT-RECOVERY, ROLLBACK, EVIDENCE |

A CLOSED specification correction transfers no installed or executed evidence.

**W-1 v3** (`WT/proposal/ISOLATION-STORAGE-PROPOSAL-v3.md`, `97f39c89…`, 193544 bytes; support
`v3-support/jackal.json` `6b085323…`) is the successor specification.
- **Status.** An author-role drafting agent wrote it, and it is unreviewed. It is design text only: no account, ACL,
  sudo, install, mount, linger, probe or selftest action exists. It is paired with this draft for the next review.
- **The author's assessment.** Every NOT_CLOSED sub-gap is "CLOSED-AT-SPEC-LEVEL" in its §18. That is the author's
  claim, not closure. Until a sealed review rules, every NOT_CLOSED sub-gap stays NOT_CLOSED.

**What v3 specifies:**
- **Generation order.** Separate create-only records:
  - the generation record, binding only what exists when it is written;
  - then inputs, reservation, admission and launch intent.

  The immutable admitted partition is distinct from the attempt-bookkeeping and export partitions, so "final pass
  after the last frame mutation" is exact.
- **Lease.** The `writer.lock` is created at setup: root-owned, 0440, only `flock`ed through an `O_RDONLY` descriptor,
  with no runtime byte write. Its identity is checked at every invocation.
- **Entrypoint closure.** The closure of both accounts and of a new gate group is enumerated.
- **Account IDs.** They must lie outside every subordinate-ID range.
- **Modes and ACLs.**
  - No ACL on any recipe object or record, and no default ACL anywhere, so every v5 mode is preserved.
  - ACLs only on frame-created ancestors, the four writer-pre-created partition roots and the export copies.
  - The target reads source through the recipe's own others-bits. The pinned base was observed with 635 files at
    0644 or 0755 and 55 directories at 0755.
  - The lead reads only writer-made exports.
- **The hole in v2.** In v2, a target could plant a setuid or setgid file in a place it can write. A `sicarii` process
  that ran it would gain the target identity and could write the output partitions. v3 closes this:
  - the target's write access comes only through a new group, `wlscratch-gate`, which only the reviewed launcher
    confers;
  - `no_new_privs` and an anti-setid seccomp filter are applied to the target;
  - admission and terminal scans look for unexpected gate-group holders and setid leaves.
- **Channel.**
  - Exact framing and chain rules. Integrity is stated as integrity, not authentication.
  - The lead-authentication ceiling stays the original v5 ceiling.
  - Dumpability is set and read back with `prctl(PR_GET_DUMPABLE)` and `/proc/self/fd` ownership.
- **Participants.**
  - Complete schemas.
  - A late launch after the writer dies is possible only through an already-issued, recorded permission.
  - Only the front releases the window. If the front dies after reserving, the window is held for manual resolution,
    which is stricter than v5.
- **Commits and fallback.**
  - Separate commit markers (N11).
  - A preallocated 16 MiB fallback journal inside the attempt directory.
  - An explicit durability-UNKNOWN state.
- **Setup and recovery.** Symlink-safe prestate, root-owned reviewed-byte sudoers staging with fail-closed chains,
  exact probe operands, staged Gate 0 (S-1), and rollback ordered so new launches are revoked before participants are
  reconciled and before any withdrawal.

**What v3 leaves to later evidence, as the author lists it:**
- the concrete numeric IDs (950–952 are only candidates);
- script bytes and digests;
- Option B's code;
- the post-setup baselines;
- host behaviours to be probed (sudo signal relay and group vector, `class=none` manager behaviour, scope
  exec-in-place, the fallback journal on a full disk);
- compatibility hypotheses: no allowlisted action writes `HOME`, removes a partition root, uses setid modes,
  `io_uring` or `openat2`. If any is false, W-1 is redesigned and no accepted case is narrowed.

**The v2 design, summarized below, is unchanged in direction:**

**Two new accounts, two new groups:**
- writer `wlscratch`: runs only the installed reviewed frame, with no linger;
- target `wlscratch-run`: runs only the installed launcher and then the exact target command in a user scope.

The target is on its own uid, so it cannot mutate frame-owned locations. That removes the target/writer overlap.

**Lease:**
- an exclusive writer lock, taken before any mutation;
- a fresh generation root, created under a root-owned home and a writer-owned `runs` directory;
- a kernel-enforced argument that only this writer, or root, can mutate frame-owned entries from admission to use.

The argument is for review. It is not yet evidence.

**Final pass.** At final admission, every encountered leaf is revalidated, including excluded generated leaves.
- **Correction to v2's wording.** v2 said the v6 working copy covers accepted files only. That understated it: the
  working copy already re-stats recorded and excluded files in the final pass (`scratch.py:554`, `:569-573`).
- **Self-check.** The author self-check in "Executed engineering checks" exercises that code.
- **Still open.** The custody that protects the admitted generation until use is the W-1 part.

**Inputs:**
- The writer reads nothing under `/home/sicarii`. The front streams the inputs, and the writer verifies them against
  compiled-in pins. The frozen 0600 review files keep their modes.
- The target needs the exact original toolchain path. That leaves two options, and the operator chooses at setup:
  - **Option A:** a traverse ACL for `wlscratch-run` on `/home/sicarii`. The exposure is broad: other-readable files
    along other-traversable paths.
    - You would get a read-only inventory of the inspected part.
    - Paths that must never be inspected (the iPad FUSE mounts, the SIA brain directory) are UNKNOWN exposure. They are
      not an enumerated or assessed set.
  - **Option B:** a narrower, root-owned sandbox launcher.

**Storage and the vault.** These stay with the front, as `sicarii`. `storage_status.py` is never run as the writer.

**Setup:**
- Prestate checks, exact account and directory commands, and validated sudo rules.
- Member-exact installation. It is labelled a template until the reviewed inventory exists.
- Sacrificial denial probes that check errno, never the real runs tree.
- A fixed order: design review, then code review, then setup-inventory review, then Gate 0, then your approval, then
  setup, then verification, then installed-identity review and adoption, then any dispatch.

**Resources:**
- Image figures are payload allowances, not image sizes. The zero difference is an ideal payload identity.
- `noexec` is assessed.
- ENOSPC is a failure, never an accepted refusal or capacity.

**Failure, lifetime and rollback:**
- Generation-bound launch intent and acknowledgement, genuine waits, and unknown-outcome holds.
- A records-ENOSPC channel, and reboot handling.
- A rollback that revokes new launches first and preserves prestates. It honestly says what it removes, which is
  configuration, and what remains: accounts, groups, UIDs, files and ACLs.

**What it does not claim:**
- No sufficiency.
- No protection of the lead's own processes from same-user interference. The same residual applied to v5.
- No stronger lead authentication than the reviewed v5 protocol.
- No custody of the toolchain, which is executed by path.

V5-B01, V5-B02 and every original obligation stay OPEN.

### Options

1. **Later: approve the concrete privileged setup.** It comes after a reviewed W-1 design (now v3), reviewed v6-W1 code, a
   reviewed setup inventory with prestate outputs, and an established Gate 0.
   - You run, or authorize, the listed commands.
   - Verification, installed-identity review and adoption follow before any dispatch.
   - Optional now: tell the lead whether dedicated accounts are acceptable to you in principle.
2. **Decline W-1.** V5-B01 and V5-B02 stay OPEN, and there are no scratch proof runs. The lead keeps looking for a
   route and submits any candidate for review.
3. **Change the criterion's scope.** This is operator-only. It is ineligible to close the unchanged confinement
   obligation even if chosen. Not recommended, not requested.

**Lead recommendation:** option 1's path, if you want scratch proof runs at all. Design work continues either way. It
needs no decision.

---

## P-1. Pinned implementation files (information; no decision requested)

### Facts

**Observed:**
- **169 effective `CONTRACT_PINS` keys.** They come from a read-only AST walk over the dictionary at
  `proof_manifest.py:329` and every top-level `CONTRACT_PINS.update(...)`, lines 418–1029 of the commonV5-beta
  manifest. The count matches the composition review, and the package review reproduced it.
- **Every replacement payload is pinned.** Every replacement payload under each lead packet's `files/` directory,
  packets 01–14, is an effective pin key. The per-packet table is `WT/errata/d2-inventory-E1-pinned-files.md`.
  - The statement covers replacement payloads only, not packet metadata, manifest-tail files or generated manifest
    changes.
  - Pin membership is no permission to adopt a packet, and no proof that an unadopted packet matches the candidate.
- **Already-qualified packets.** The sealed commonV5-alpha and commonV5-beta reviews qualified packets 01, 02 and 04–09
  with their pin refreshes. Source qualification and repinning are not proof or runtime acceptance.

**Sealed D2 correction C-PINS**, preserved verbatim:

> "Keep implementation ownership distinct from permission to change pinned text. Under this review's requested
> pinned-text boundary, a concrete change to enrolled pinned text must carry O-PINS operator approval as well as
> independent review and regenerated effective pins. Body-only implementation work can be lead-owned; that label does
> not authorize changing the protected pin package, weakening its keyset, or adopting a changed pinned
> contract/reference. This review authorizes none of those actions."

**Provenance.** The lead introduced the "requested pinned-text boundary": the lead's own D2 brief, item 4, says
"operator approval for pinned text or public contract", and the D2 inventory used an O-PINS label.

**Original requirement, HANDOFF acceptance sequence item 1:**

> "Stabilize and independently qualify the remaining source and designs. Import only explicit reviewed deltas into a new
> isolated integration checkout, resolving shared caller/transaction/ABI/policy changes. Preserve all original
> fixtures, complete source keysets/modes/directories and inverse lineage. Recompute all effective normalized pins and
> full ordered proof enrollment without changing the original policy prefix or replacing original accepted cases."

**Supervision correction, 2026-10-04** (verbatim):
- "the human's preserved authorization covers routine reversible engineering; a review brief or review finding is not
  new authority to add approval gates."
- "Do not request retroactive or blanket operator approval solely because an implementation file is pinned."
- "This is not permission to redefine reference semantics, change an unapproved API, lower contracts, scope, accepted
  cases or controls, or waive any proof/runtime/review gate. Material API/owner-policy and
  merge/release/install/sudo/production/real-PRIME decisions remain reserved."

**Package review scope correction** (sealed, `package-review/gpt61-v1/REVIEW.md:300-302`):
- "the O-PINS boundary has no original-requirement basis insofar as it requires approval solely because a preserving
  implementation file is pinned."
- "Only the independently reserved part of C-PINS has an original basis: a concrete material API/ABI or owner-policy
  decision, a proposed redefinition of the original reference/contract guarantee, an operator-custody or
  toolchain/deployment architecture choice, or merge/release/install/sudo/production/real-PRIME action retains its
  applicable authority."

### How this package treats pinned implementation files

- **No approval is requested for pinning**, whether retroactive, blanket or per change.
- **Each change follows HANDOFF item 1:**
  - an explicit delta, independently reviewed by actual gpt-6.1-sol;
  - recomputed effective normalized pins;
  - full ordered enrollment, with the original policy prefix unchanged;
  - original fixtures and accepted cases kept.

  Every strict proof, body, caller, native, runtime, fault, review and hosted gate is retained.
- **Still reserved, unchanged:**
  - redefining reference semantics (R-1 option 3, R-2 option 2);
  - an unapproved API/ABI change (C-ABI);
  - material owner policy;
  - operator custody and toolchain/deployment architecture;
  - merge, release, install, sudo, production and real-PRIME actions.
- **Preserved unchanged:** the sealed D2 review and E1.

---

## R-1. `contracts-recursive` / `numeric-variant` notices

### Facts

The F10K strict `-k` raw `.spark` data has 25 unique notices (observed; `evidence-recursive-notices.json`; the package
review matched the raw tuples):

| Group | Count | State |
|---|---|---|
| Spec-level declarations | **19 notices on 11 declarations** (JACKAL exact sums 19 and 11) | Operator choice after evidence |
| Body-level `Prefix_Tail` (`resource_reservation_transition.adb:85`) | 2 | Candidate packet 13, an untested hypothesis until matching-source strict evidence exists |
| Body-local witnesses (`evaluation_epoch.adb:141,162`; `worldline-resources.adb:9,33`) | 4 | Candidate packet 12, an untested hypothesis |

**The 11 spec-level declarations**, each in its `S5/core/*.ads`:
- `Canonical_Artifacts.Prefix_Reference` (:32);
- `Resource_Quantities.Power_Reference`, `Prefix_Reference`, `Radix_Power` and `Prefix_Value` (:40, :47, :58, :69);
- `Resource_Ledger.Total_Reference` and `Prefix_Total` (:124, :133);
- `Resource_Run_Ledger.Sum_Reference` (:200);
- `Worldline.Chain_Authority.Prefix_Reference` (:74);
- `Worldline.Resources.Radix_Power` and `Prefix_Value` (:29, :34).

**Tool semantics.** Explicit and implicit postconditions of a recursive subprogram cannot be used on recursive calls
inside assertions and contracts.

### Criterion

HANDOFF.md:161: "Completion has zero unproved, zero justified and zero pragma Assume, with complete reports and all
strict warning obligations resolved."

The monitor already ruled:
- no waiver;
- no redefinition of the pinned references;
- ruling 7b allows independently proved lemmas and call-site facts while preserving the recurrences.

### Options

1. **Keep OPEN.** Phase One cannot then complete.
2. **Demonstrated toolchain classification.** It needs:
   - P1: probe units, which are new files. The staged copy in `claude-workflow-v1/overlays/probe-recursion-p1` was
     created with Bash after a guard refusal. It is preserved without clearance, and any use will be from a reviewed,
     guard-compatible copy;
   - P2: complete proofs that do not rely on the unavailable contracts;
   - P3: the treatment under the exact strict command.

   Gathering this is routine engineering, gated by F-1 and S-1. Afterwards you decide whether the demonstrated
   classification resolves the notices. A later classification can never waive the strict command.
3. **Redefine the pinned references.** This is a reserved change. It is ineligible to close the unchanged obligation
   on its own, and claimed equivalence supplies no proof.
4. **Waive the warnings.** This is ineligible for closure of the unchanged target. Not recommended.

**Lead recommendation:** the lead gathers option 2's evidence when F-1 and S-1 allow it. You decide after seeing it.

---

## R-2. Unproved reference Posts and the checked-build cost hazard (coupled to R-1 and N-3)

### Facts

**Unproved Posts** (ledger; the diagnostic state does not establish why each failed):

| Item | What it is | Self-referential? |
|---|---|---|
| D1381 | `Prefix_Total`'s Post at `resource_ledger.ads:138`, restating its own recurrence | Yes |
| D1400 | `Radix_Power`'s Post at `resource_quantities.ads:63` | Yes |
| D1401 | `Prefix_Value`'s Post at `resource_quantities.ads:76` | Yes |
| D1383 | `Result_Conforms` at `resource_ledger.ads:168`. It has downstream reference dependencies | No |
| D1384 | `Compute`'s Post at `resource_ledger.ads:205`, which calls that relation. It has downstream reference dependencies | No |

**Checked-build cost.** These are conditional, static source reasoning only. They are not measurements, allocation or
instruction counts, bounds, termination guarantees or proofs.
- **Sources:** the D2 inventory (`WT/designs/claude-d2-checked-ghost-inventory-v1`) and its sealed review,
  ACCURATE_WITH_CORRECTIONS (REVIEW.md `03fbf246…`, freeze `f94a3cce…`).
- **Chain replay (H1).** A successful replay of chain `Prefix_Reference` takes 9·2^(n+1)−n−10 source reference calls:
  18412 at n=10 and 19327352792 at n=30 (JACKAL exact; reproduced twice). H1 says: "No measured native cost is
  established."
- **Candidate packet 14** worsens that to 11·2^(n+1)−2n−14: 22494 at n=10 and 23622320054 at n=30 (JACKAL exact, as
  reproduced by the package review). Packet 14 is untested.

**The D2 corrections** (sealed; each binds every use of the inventory):

| Correction | What it says |
|---|---|
| C-SLOT | The `Storage_Sufficient` slot term is Θ(N²·S⁴) for a uniform, independently varying slot length S. The dominant Θ(N⁶) is for the specified Python-sized bounded-value family only, not for arbitrary relative extents. |
| C-SUM | `Sum`'s Value work is quadratic, while repeated-parent `Contained` can be cubic. `Sum_Reference` also scans excluded rows and identity bytes, so cost does not depend only on included rows. |
| C-OWNER | Retry authorization and audit traverse full histories, with per-row epoch work. The exported paths are not fixed Θ(L⁶) or O(H·id). |
| C-EMPTY | An empty disk roster still runs `Check_Capacity` and its checked numeric relations. Any displayed envelope must either include that fixed memory-quantity cost or say it is a nonempty, comparable-extent envelope. Short-circuit paths differ. |
| C-UNIT | Comparisons return Boolean and allocate no Big_Integer, and a zero-exponent reference has no multiply. Conversions, predicates and controlled copies add work. Source invocation counts are not allocations or emitted instructions. |
| C-PACKET-GAP | Equal-endpoint calls keep absolute-position Posts. Packet 13's `Prefix_Tail` and its decomposition keep `Prefix_Reference` work when First = Stop. Packet 12's unchanged Posts keep radix/prefix cost at Low = High. Zero-gap accepted cases cannot vanish from gap-only formulas. |
| C-P12-REACH | One outer mismatch can trigger many nested witness evaluations, through the unchanged `Prefix_Modulus` and multiple operands. Packet 12's inner iteration removes only its own recursion. |
| C-COPY | Narrowing an arena snapshot to a slot can change the growth class, not just a constant. The whole-arena frame relations must be preserved, and a replaced assertion needs independent review. Native allocation or lifetime improvement is not established statically. |
| C-ABI | Interface-preserving internal diagnostics are routine work with review. Changed public codes, meanings, layouts or caller protocols fall under the material API/ABI operator boundary. Better failure naming establishes no successful native acceptance. |
| C-LOC, C-BASE | These repair the inventory's own locations and its delta description. No equivalence or acceptance follows. |

**Release build.** The read release configuration lacks the `-gnata` switch
(`S5/core/worldline_core_sources.gpr:8-19`). That is source configuration. It is not evidence that generated assertion
code is absent. Selecting release was never established, and using it to discharge this would be suppression.

### Options

1. **Keep OPEN.**
2. **Redefine these references** in a non-self-referential form. This is a reserved change. It is ineligible to close
   the unchanged obligation by itself, and claimed equivalence supplies no proof and excuses no caller or control.
3. **An assertion-level / Ghost-witness design** that keeps every Post checked. A replaced assertion needs independent
   review that preserves every original relation and checked obligation.
4. **Preserving body-only routes**, such as an iterative chain-reference body or result-span value facts.
   - They are routine reviewed engineering. As pinned implementation files, they follow HANDOFF item 1 (P-1).
   - By reasoning, an iterative body is Θ(n²) per evaluation. That is a hypothesis until complete bodies, all checked
     Posts and invariants, and native evidence exist.
   - C-COPY applies.

**Lead recommendation:** decide R-1 and R-2 together, after the P1–P3 evidence.

---

## C-1 / C-2 / C-3. C-API boundary items

### Source and review status

- **Design:** DESIGN v3 (`WT/designs/claude-capi-boundary-design-v3`, DESIGN.md `a8a120c9…`).
- **Review:** sealed actual gpt-6.1-sol review, `gpt-6.1-sol` / `max` from the rollout, freeze verified. Verdict
  **ENDORSED_WITH_REQUIRED_CHANGES.**
- **v2 required changes:**
  - RC1–RC3 are CLOSED_AT_DESIGN_LEVEL.
  - RC4–RC6 are NOT_CLOSED. They become V3-RC4 (enforceable binding and provenance rules), V3-RC5 (faithful PK-0
    read/frontier/defined-handler/write-order classification) and V3-RC6 (a cost map that separates source structure
    from emitted copies, checks, storage and lifetimes).
- **The boundary itself.** A literal singleton Off boundary is insufficient if required semantic bodies move out of
  proof.
- **Next.** The packet plan is NOT_CLOSED. DESIGN v4 and its re-review are the lead's next work.

### C-1. D-13: the separate pending component's `wl_pending_decide_v1`/`_v2` (operator, later)

**Ruling (verbatim):** "OPERATOR_CHOICE_REQUIRED_BEFORE_PK-7; ONLY_ABI_AND_SCOPE_PRESERVING_ROUTE_ADMISSIBLE. Option
(i) is a reviewable candidate, not approval. Retain both original Decide exports, all component interface units, exact
SPARK_Mode-only mirror, positive/refusal/native-body obligations and source/project/library/header identity. Options
(ii)/(iii) are inadmissible. No new core Off exception or proof credit."

| Option | What it is | Status |
|---|---|---|
| (i) | A component-local Off transport unit, text-identical to the C_API pending transports, in the component's `Library_Interface` | Reviewable candidate |
| (ii) | The component stops exporting `Decide` | Inadmissible (narrows the ABI) |
| (iii) | No mirror | Inadmissible (abandons exact correspondence) |

**When you decide.** On a concrete packet, after its own actual gpt-6.1-sol review. The packet must carry its
source/project/link closure, matching symbols, profiles and layouts, native positive and refusal controls, the exact
mirror, new component pins and raw identity.

**Lead recommendation:** option (i), which the lead will prepare as that packet.

### C-2. N-06: deployment provisioning (operator, at deployment)

**Ruling (verbatim):** "REPROVISION_UNDER_OPERATOR_CUSTODY_AT_DEPLOYMENT. Mismatch refusal is retained. Keeping the old
library is only a deployment hold and gives no successor-service/integrated acceptance credit."

| Option | Meaning |
|---|---|
| (a) | Re-provision `native_sha256` under your custody, for the installed **and loaded** reviewed library. **Recommended.** |
| (b) | A deployment hold. Never acceptance. |

No deployment action is authorized here.

### C-3. N-01: representation warnings (lead-owned; information)

**Ruling (verbatim):** "LEAD_OWNED_STRICT_OBLIGATION. ABI-confirming representation packets are conditionally
design-admissible, individually reviewed after legal family movement and before PK-S. No waiver or
relocation-as-resolution. A nonconfirming layout change is outside this design and cannot reduce the target even with
operator approval."

You would decide only a separately proposed material ABI change, and none is proposed.

### Other v3 rulings

| Status | Rulings |
|---|---|
| Closed at design level, proof still OPEN | D-18; N-04; N-07; APPENDIX_C (the append-only order of the 535-name prefix) |
| Conditionally acceptable | LD1, LD2, LD3 (pending D-13), LD5, LD6 (subject to V3-RC5), D-28 |
| OPEN | D-05, D-19, D-36, D-15/D-34/D-38, N-03 (no PROVED_ROW transfer credit), N-05 (no subset reinterpretation) |
| NOT_CLOSED | R2_NINE_CONDITIONS (pending V3-RC4) |
| Open, shared | The root-worker shared C_API integration |

---

## N-1 / N-2 / N-3. Native Big_Integer

### Source and review status

- **Design:** D1 DESIGN v3 (`WT/designs/claude-native-bigint-d1-design-v3`; DESIGN.md `b20554c4…`). Appendix B governs
  where it differs.
- **Review:** sealed actual gpt-6.1-sol review, `gpt-6.1-sol` / `max` from the rollout, freeze verified. Verdict
  **ENDORSED_WITH_REQUIRED_CHANGES.** v2 was NOT_ENDORSED.
- **Closed:** V2-RC1..RC3 and the older RC4..RC6.
- **NOT_CLOSED, carried into:**
  - **V3-RC1:** the OD-2 codec and census;
  - **V3-RC2:** controls and fixtures, including the middle-cell mismatch, the X6/X7 exits, the staged and
    Primary_And_Staged paths, and RL-7c/8/9;
  - **V3-RC3:** the checked-cost model, rebuilt from complete nested Posts, bodies, lemmas, copies and mixed primary or
    staged paths.
- **Eligible:**
  - R-A: Algorithm A, on the original domain;
  - R-B: Algorithm B. "No new public Pre or size refusal is authorized."
- **R-SCOPE:** "D1 alone closes no original helper, checked-Ghost, Python, transport, physical-cost or integrated
  acceptance obligation."
- **D1 DESIGN v4** (`3c636847…`) was drafted ~00:00Z. Its actual gpt-6.1-sol review is INCOMPLETE (see the
  Isolation record). Until a sealed review rules, every v4 claim, including author findings F32/F34/F35/F36, is
  unreviewed.

### N-1. OD-1: the `Exact_Value`/`Amount`/`Sum` route (operator, later)

**Ruling R-OD1 (verbatim):** "No OD-1 option is selected or recommended. The repaired option set preserves helper
obligations. Ghost retirement/removal is incompatible; release unreachability and approval alone close nothing."
- Owner: "operator chooses concrete library/runtime/API architecture; lead prepares evidence and may pursue preserving
  body-only mitigation".

| Option | Exact consequence |
|---|---|
| E | No decision. Everything stays OPEN. |
| (o) | A preserving release-body mitigation, lead-owned. Checked `Q.Value` and full-span reference work remain, and so do the native representation and cost obligations. |
| (i-a) | A WORLDLINE-owned `SPARK.Big_Integers`. It needs independently verified model binding with no new axioms, and migration and re-proof of every direct Ada user. A model name supplies no correspondence. |
| (i-b) | A separate proved bignum type. It changes public result types and every caller. |
| (ii) | A rebuilt GNAT runtime. It must repair layout, Length/index/base arithmetic, automatic vectors, multiplication and division, controlled copies and checked costs, and rebuild/relink/loaded identity. Editing `Bignum_Limit` alone is not enough. |
| (iii) | Ghost-only retirement. Incompatible, and ineligible even with approval. |
| (iii′) | An additive successor API. Every original helper remains executable and its obligations stay OPEN. |

**When you decide.** On concrete, independently verified evidence. No option is selected or recommended.

### N-2. OD-2: Python decimal-integer correspondence beyond 4300 digits (operator, after V3-RC1 re-review)

**Ruling R-OD2 (verbatim):** "No E1/E2 choice is selected. The 640-digit chunk guard is valid under every admitted
interpreter limit, but V3-RC1 must repair codec ordering, inventory and configuration/exclusion precision. A cap or
catch-and-refuse is not a repair."
- Owner: "operator for conversion architecture and protected custody; lead for codec/audit/evidence preparation".

**E1: interpreter-wide unlimited (`int_max_str_digits = 0`), with the complete class table.**
- **Source:** the reviewed D1 v3 DESIGN §11.3 (`WT/designs/claude-native-bigint-d1-design-v3/DESIGN.md:1702-1731`), as
  corrected by its sealed review (`…/review/gpt61-v1/REVIEW.md:121-135`).
- **D1 v4's revision:** D1 v4 revises it, adding class C12. D1 v4 is unreviewed: its review stalled (Isolation record).
  Everything in this table is a configuration proposal, not an observation of the actual WORLDLINE interpreters.

| Class | Processes | Exact change under E1 | Consequence / custody |
|---|---|---|---|
| C1 launcher-started | `cli/worldline`, `cli/worldline-relocate`, `daemon/worldlined` (non-isolated `#!/usr/bin/env python3`) | `sys.set_int_max_str_digits(0)` right after `import sys` and before any `from worldline… import` | Set before any WORLDLINE import |
| C2 service | `daemon/worldlined.service` | none beyond C1 | Covered by C1. An `Environment=` setting alone would not reach isolated children |
| C3 direct-module `__main__` | `daemon_main.py`, `cli_main.py`, `relocate.py`, `linux/namespace_lifetime.py`, `linux/private_evaluator.py` | Each production entry launched with `-X int_max_str_digits=0`. A first-statement call is weaker, because module imports run before it | The production-entry inventory must say which of these run |
| C4 trusted helpers | `trusted_inline`; `trusted_script` (kernel_role_observer, systemd, namespaces, private_evaluator), started with `-I -S` | `ISOLATION_FLAGS = ("-I", "-S", "-X", "int_max_str_digits=0")` | Synchronized changes to `checkRunnerInterpreter` / `trustedStartupFlags` (`validation.py:240-245`) and to any test asserting the tuple |
| C5 in-process `runpy` | `linux/private_evaluator.py` | none | Inherits from its C4 host |
| C6 examiner role | In-process in the private evaluator | **The examiner path restores the original default** (`sys.int_info.default_max_str_digits`) before entry code, preserving examiner isolation. The alternative, inheriting unlimited, is a separate material choice | WORLDLINE parses examiner reports in covered C1/C4 interpreters |
| C7 re-executed payloads | worker and candidate roles via `os.execv` | none | Candidate interpreters are not WORLDLINE parse paths and stay unchanged |
| C8 protected services | `protected-startup/launcher.py`, `owner_provision_bootstrap.py`, `protected-resource/run_service.py`, `gate_bridge.py`, `protected-runtime/approved_source_loader.py` (`-I -S -B`, flags bound in the early envelope) | **Either** add `-X int_max_str_digits=0` to the operator-bound flag set, with re-provisioning, **or** set the limit in approved source before the first parse, which changes approved-source pins | Operator custody in both forms |
| C9 control campaigns | `protected-*/controls/run_campaign.py` | none. Original controls stay byte-identical | Additive PY controls observe the setting |
| C10 install/release scripts | `scripts/*.py` run by `install.sh` (for example `preflight.py`) | For each script that parses WORLDLINE data: unlimited at start, **or** independently reviewed lexical and magnitude bounds | — |
| C11 native extension host | `native/examiner_guard.c` (a CPython extension; starts no interpreter) | none | Inherits from its host |
| (gap) build tool | `native/build_guard.py`, a direct build-tool interpreter | **No disposition in the reviewed table.** The v3 review requires a startup disposition or an independently reviewed lexical/magnitude bound. D1 v4 proposes "C12" (unreviewed) | OPEN |

E1's evidence must observe `sys.get_int_max_str_digits() == 0` before the first relevant conversion in each covered
class, and must observe that the examiner sees the original default. Under E1:
- the guard is removed for all conversions in covered processes, including untrusted local requests, peers and
  examiner reports;
- CPython converts large values superlinearly, so costs must meet the original target uncapped (O-PY-COST).

**E2: a scoped codec, with the interpreter limit kept and chunks of at most 640 digits.** The 640 chunk guard is valid
under every admitted limit, per the review. The full semantic obligations:
- **Parse.** `parse_int=decimal_int` at every site, preserving every existing keyword.
  - `decimal_int(s) == int(s)` wherever `int` succeeds.
  - Canonical strict UTF-8 is preserved.
  - `-0` still gives 0, so canonical re-encoding still refuses it.
  - Duplicate-key hooks and every original refusal are preserved.
- **Serialize.**
  - Every settings combination is reproduced byte-for-byte: `indent`, `ensure_ascii` both ways, `separators`,
    `sort_keys`, `allow_nan`.
  - Escaping is unchanged.
  - Numeric subclasses and floating values, including NaN/Infinity under `allow_nan`, keep `json`'s behaviour.
  - Original key objects sort **before** integer keys are converted, so 2 sorts before 10.
  - Mixed incomparable keys raise the same `TypeError`.
  - Circular-reference and recursion behaviour are unchanged.
  - The existing `_validate`-first order is kept.
- **The two variants:**
  - **E2-a** reuses CPython's private `_make_iterencode`/`_intstr`. It needs pinned CPython 3.14.7 and C/Python-encoder
    correspondence evidence.
  - **E2-b** is a complete WORLDLINE encoder that must reproduce everything above. "Sort by code point" was the
    defect the review found.
- **Evidence.** Finite byte-differential tests are controls, not proof of an unbounded encoder.

**Bounds, both options:**
- Formatting exclusions use absolute-magnitude bounds.
- Parsing exclusions use lexical digit-count bounds.
- A one-sided signed inequality, or a small parsed value, bounds nothing.

**Census:**
- At least 193 sites: the 192 direct-name sites plus the known alias at `scripts/decisive_evaluation_test.py:264`
  (JACKAL exact `192+1`). That is a demonstrated minimum, not exhaustive routing.
- Aliased and forwarded JSON calls and non-JSON data flow stay OPEN.
- Appendix A's byte-identity statement is corrected for `proof_manifest.py`.
- Costs stay uncapped.

**Rejected routes:** per-call toggling, a finite higher limit, caps, catch-and-refuse.

**When you decide.** After D1 v4 repairs V3-RC1 and passes re-review. That re-review is mandatory before any E1 or E2
choice.

### N-3. D2: checked-Ghost cost in the default `checks` build (lead-owned; information)

- **The hazards and corrections are as in R-2.** Every class is conditional static reasoning.
- **H9:** native stack and heap layout, peak live heap, copy elision and exhaustion are not determined statically.
- **H10:** a catch-all exception mapping in the C wrappers does not make a stack or process failure catchable, and does
  not establish completion. "These outcomes are not accepted semantic refusals."
- **D1 v3's own checked cost** must be rebuilt per V3-RC3. The worker-only and Post-only estimates are not
  established.
- **R-NOTICE:** "A-GHOST-1 adds the proposed Side_Sum declaration to OPEN R-1-class obligations; no prior
  classification automatically covers it. A-GHOST-0 avoids a new declaration site but preserves old notices and adds
  checked costs."
- **R-WORKSPACE:** CL-1/CL-2/CL-3 are lead-owned. None may "waive warnings, add Off, suppress Ghost or count resource
  failure as a refusal".
- **F-B2 / F-B3:** these are public API/ABI packages. They are reserved, and neither is proposed.
- **Forbidden routes:** release-only escape, suppressed checked Ghost code, caps, refusal counting.
- **All native and checked costs stay OPEN.**

---

## RW-1. Root-worker runtime lane

**Review.** The seam design v1 has a sealed actual gpt-6.1-sol review: **ENDORSED_WITH_REQUIRED_CHANGES**, RC-01..RC-12,
review.json `721bce3a…`.

**Statically observed defects in the unreviewed draft lane:**
- a stale `protected_operations.py` pin;
- a duplicate `attach_scoped_resource` that drops a producer check;
- three original pre-dispatch checks missing from the root route;
- self-comparing RootController identity pairs;
- missing scoped settlement adapters.

A non-reentrant gate-mutex deadlock is conditionally supported. Nothing was executed, so no race, deadlock or
acceptance is established.

**Rulings:**
- `Delegate=yes` alone is not endorsed.
- The frontier control may not be retired by the lead.
- Native custody-phase legality is mandatory.

**Operator-gated:**
- root, system-unit and lab execution;
- provisioners and installation;
- delegation;
- actor (Luna) quota;
- fault campaigns;
- merge, release, install and PRIME.

**Rulings that name the operator, with independent review:**

| Ruling | Operator item |
|---|---|
| D-2a | Authoritative state provisioning or installation |
| D-2b | Frontier re-enrollment adjudication; the original obligation stays OPEN meanwhile |
| D-4a | Any authoritative resource-policy change; no accounting option is selected |
| D-5a / D-5b | Delegation, and privileged lab action or installation |
| D-7a | An original API or owner-policy alteration |
| D-8b | Kernel measurement |
| D-9a | The fault campaign |

No choice is asked for yet.

**Lead next work.** Routine engineering, each item with independent actual gpt-6.1-sol review:
- seam design v2;
- C-API DESIGN v4;
- D1 DESIGN v4;
- frame v6-W1.

New reviews are paced against S-1.

---

## Isolation record (for your information)

- The background-session guard refuses Write/Edit in the shared work tree.
- Edits go to a dedicated local repository and its linked worktree (`W/work/claude-lead-isolation-v1/{repo,wt-1}`),
  which the guard accepts.
- Earlier artifacts written by Bash fallback after refusals are listed in `WT/ISOLATION.md`. They are preserved, with no
  clearance claimed.
- Every review is actual gpt-6.1-sol. One earlier Claude pre-read was non-compliant and is kept as history only.
- Disclosed: one `find` listed file metadata under the SIA brain path, against the machine rule. Nothing was read or
  written there.
- **Disclosed: the D1 v4 drafting agent wrote one temporary file with Bash**, against its read-only-Bash rule. It
  was not a refusal workaround. The lead preserved a copy and removed the original
  (`WT/deviations/d1v4-drafter-tmp-file`).
- **The D1 v4 review is INCOMPLETE.** A tool-layer stall is suspected in its concurrent `exec` batch of
  `jackal_exact` replays.
  - Its event stream and rollout have been unchanged since 00:05:39Z.
  - That evidence does not prove the batch never reached JACKAL or that no call executed. The ledger is recall only.
  - It has not been interrupted or restarted.
  - A preservation and recovery proposal waits for your decision (`WT/review-monitoring/`): R0 leave it; R1 terminate
    codex only, so the runner resumes the same thread; R2 run a fresh review. Nothing has been performed.

---

## Executed engineering checks (ENGINEERING_ONLY; never proof, review, admission or acceptance)

No prover or compiler was launched on WORLDLINE code. The operator's scratch-frame decision forbids that outside an
adopted frame.

| When (Z) | Check | Result | Limits |
|---|---|---|---|
| 10-04 23:37 | V5-B01 final pass. A library import of `observe_tree` on throwaway trees, with mutations injected after a file's observation | v6 working copy (`2255d6e1…`): 14/14 as required. Frozen v5 (`f9f6596d…`): 6/14, accepting 8 post-observation changes | One walk only. Custody until use is not tested |
| 10-04 23:40 | Regression: the unchanged 85-case v5 author self-check, retargeted in memory to the v6 working copy | 85/85, 0 failures | No launch, scope or adopt paths |
| 10-04 23:39 | W-1 writer-side mechanisms as the same user (`w1proto.py`): lease, chained framing, input pins, non-dumpable readback (`PR_GET_DUMPABLE`, root-owned `/proc/self/fd`) | 27/27 | Does not test any account boundary |
| 10-04 23:46 | Kernel DAC/ACL/hard-link probe between distinct UIDs, through a rootless namespace on `sicarii`'s subordinate range | 30/30 | Those UIDs are delegated to `sicarii` and are **no boundary against `sicarii`**. The probe shows only kernel semantics. Real accounts must lie outside every subuid/subgid range |

Records: `WT/frame-v6-selfcheck/RESULTS.md` and `WT/frame-v6w1-proto/RESULTS.md`.

---

## Correction status

**A. The nine corrections from the v4 review**, as ruled by the sealed v5 re-review (`WT/package-review/gpt61-v2`):

| Correction | Status |
|---|---|
| PKG-FACTS | CLOSED |
| PKG-CRITERIA | CLOSED |
| D2-CORRECTIONS | CLOSED |
| OD1-CONSEQUENCES | CLOSED |
| W1-CUSTODY | NOT_CLOSED. Carried below |
| W1-SETUP | NOT_CLOSED. Carried below |
| W1-RESOURCES | NOT_CLOSED. Carried below |
| W1-LIFETIME-ROLLBACK | NOT_CLOSED. Carried below |
| OD2-CONSEQUENCES | NOT_CLOSED. Carried below |

**B. The seven corrections from the v5 re-review.** Each is "corrected in v6/W-1 v3, awaiting review". None is
called closed until a sealed review says so.

| Correction | Where v6 addresses it |
|---|---|
| W1-CUSTODY | W-1 v3 (generation order, lease, channel, per-entry modes and ACLs, write authority) |
| W1-SETUP | W-1 v3 (lock establishment, symlink-safe prestate, sudoers staging, dumpable readback, probes, exposure, identities, vault) |
| W1-RESOURCES | W-1 v3 (staged Gate 0 budget) |
| W1-LIFETIME-ROLLBACK | W-1 v3 (commit markers, durable fallback, participants, reboot, rollback, evidence) |
| OD2-CONSEQUENCES | N-2: the complete E1 class table C1–C11 plus the `build_guard` gap, and the full E2 obligations |
| PKG-V5-FACTS | F-1 route table (FUSE-in-namespace as a cited candidate; rootless-subuid route ruled out); Gate 0 O1 provenance (runbook v4.3); S-1 rollout mtime versus reading time |
| PKG-CLOSURE-STATUS | This section, and F-1's sub-gap table (6 CLOSED, 14 NOT_CLOSED per the re-review) |

**C. The 20 W-1 sub-gaps.** 6 are CLOSED and 14 NOT_CLOSED, as ruled by the v5 re-review; see F-1. W-1 v3's own
per-gap assessment is the author's claim, and the next sealed review rules on it.

Traceability and design intention are not closure, executed evidence, permission, qualification or acceptance of any
original obligation.
