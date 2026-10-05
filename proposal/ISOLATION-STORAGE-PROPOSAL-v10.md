# Isolation and storage proposal W-1, v10: the same-identity view answered against the sealed v9 review — an enumerated asynchronous-write obligation, a namespace owner no principal resolves to, a complete user-deletion state table, a staged probe plan with operator-reserved boundary exercises, and a stated review-provenance join change (specification)

**Status.** Drafting author's design specification, written 2026-10-05 UTC for the Claude Code lead. It is a
CANDIDATE specification of the protected-writer confinement design for the scratch proof frame, and the successor to
v9. It answers the sealed independent review of v9, `wt-1/proposal/v9-review/claude-v1` (verdict **NOT_ENDORSED**,
sealed by `review-freeze.json` over REVIEW.md, review.json and checks.json; the review's `report_sha256` is
`51e80795e688bc11df156d47ca86646da45be0dce41659db3a36cddfeb851637`, and it was sealed from reviewer agent id
`a2f0fe859b64fb102` with task-output sha256
`ec4f6227252e0b26ef6feb0da21907c988af492d0cfa0b5940e2da14317f839a`), whose nine required changes
W1-V9-ASYNC-ENUM, W1-V9-NOOWNER-SCOPE, W1-V9-ENUM-USERDEL, W1-V9-PLAN-CONSTRAINTS, W1-V9-PREMISE-ORDER,
W1-V9-RL-SELFTEST-FIXTURE, W1-V9-INVENTORY, W1-V9-REVIEW-PROVENANCE and W1-V9-FORM-CONSISTENCY, together with the three
execution-bound carried changes W1-V8-PRESERVATION-ESTABLISH, W1-V8-PREMISE-DISCHARGE and W1-V8-EVIDENCE-EQUIV, are
the subject of §V10-0.7 and the revised units below.

- Nothing in it is implemented, installed, approved, executed or reviewed. No account, group, ACL, sudo rule,
  installation, scope, mount, namespace, Landlock domain, seccomp filter, probe, selftest, vault, adoption or window
  action has been performed for v10.
- Proof dispatch stays blocked by the confinement criteria (V5-B01, V5-B02, both OPEN) and by the capacity gate
  (Gate 0, NOT ESTABLISHED). **V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION and W1-V7-HOLDER-STATE stay
  OPEN and are not narrowed.** v10 closes no obligation by itself. Every original Phase One obligation (the 219 entries
  of `OBLIGATIONS-v2.json`, sha256 `1587e068fc2c31a562e38b459728a75dbf7e8d7d9f8afb8efa1474e2a702aeec`) stays OPEN with
  its original owner, release and dependencies.
- **Critical premises** (a refuted one stops every installed use until the redesign is reviewed; §9.8 N7):
  **P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP, P-ASYNC**. (This list now names P-SECCOMP, matching N7 and §9.8 N4;
  correction W1-V9-FORM-CONSISTENCY.)
- v1–v8 are preserved as v9 states them; v9 (`ISOLATION-STORAGE-PROPOSAL-v9.md`, sha256
  `4bc0272c0c7b586a7e161b82318b7ae4a0b732067081e3a4073ea1dd3d22b53b`, 562201 bytes, 5143 lines, with
  `v9-support/jackal.json` sha256 `2d225e26780c95035f2ef57d79cc1a1758304fb82f08c4a75adab254d2b02270`) is preserved
  unchanged and is the base of the §18.5 change map.

**Form of v10 (read this first; §V10-0.1).** v10 is a **change document over v9**, not a single self-contained
re-composition. It gives the full composed text of every unit it revises or adds, with that unit's own v10 sha256,
and it carries every unchanged v9 unit by binding it to its v9 sha256 (which the independent v9 reviewer verified
against the v9 file). A small number of large v9 units that change in only a few places are carried by an **explicit
amendment block** (v9 sha256 plus the exact edits), rather than re-typed in full. **This is a deliberate, disclosed
deviation from the brief's "self-contained like v9".** It is forced by the drafting limits for this task
(Write/Edit only to the two v10 paths; no mechanical file composition; execute nothing): under those limits a
byte-faithful 562 KB re-composition could only be produced by lossy re-typing, which cannot guarantee that every
original threshold, fixture, accepted case and obligation survives byte-for-byte — and preserving those exactly is a
hard requirement that dominates the self-containment form. The self-containment achieved in v9 (correction
W1-V8-FORM-SUBUNIT) is therefore **partially regressed here as a form matter**, recorded as the OPEN item
**W1-V10-FORM** (§V10-0.7), to be discharged by the operator-prepared composition or the next author, who can run a
read-only composition script and emit the self-contained v10 with per-unit hashes. No obligation, fixture, control,
threshold, accepted case, criterion, allowance, cap, gate or join is weakened by this form choice.

**Two sensitive areas, drafted by obligation only.** The detailed asynchronous-holder refutation and the
privilege-boundary probe procedures are **not** written here as step-by-step recipes. For the asynchronous boundary
(W1-V9-ASYNC-ENUM) this document states the closed specification, its enumeration basis and the state an
operator-run probe must observe, and marks the detailed procedure OPEN (owned by the operator-prepared package,
§16.1 E1/E2). For every privilege-boundary probe (the E0 probe plan and the boundary exercises) it gives only NAME,
OBLIGATION, ENTRY RULE and DISCHARGE/REFUTE PREDICATE, and defers every boundary-exercising or object-constructing
procedure to the operator stages. No obligation is weakened by this: the asynchronous-holder containment and the
boundary properties remain OPEN obligations, to be discharged by the operator-prepared probes under their stated
predicates and an independent review, and are not asserted here.

**Inputs read for v10** (read-only): the sealed v9 review (`REVIEW.md` and `review.json` in full); v9 and the units it
reproduces; `STATUS.md` (the D-LEAD-REVIEW-PROVENANCE decision at ~19:05Z and the human direction of ~17:05Z); the
original texts `.../outputs/claude-phase1-handoff-20261004/HANDOFF.md:173` and `.../outputs/complete-phase1-prompt.txt:60`
(for W1-V9-REVIEW-PROVENANCE). The installed-build and upstream readings v9 relied on are not re-fetched for v10;
where v10 relies on them it relies on v9's dated observations (Appendix I) under premise P-KSRC, and S-1 of §13.2
still binds the running kernel image and build-id to the package before any installed use.

**Non-claims, short form** (full list §20). No sufficiency is claimed. V5-B01, V5-B02, W1-V5-PRESERVATION,
W1-V6-READ-MUTATION, W1-V7-HOLDER-STATE, Gate 0 and every original Phase One obligation stay OPEN. Every premise of
§9.8 N7 is NAMED_UNESTABLISHED; a refuted premise requires redesign with no exception; a refuted critical premise
stops every installed use until the redesign is reviewed. The review-provenance join change of §23 is itself a change
to an original admission join and is **not reviewed**; adoption stays blocked until it is reviewed in the frame-design
revision.

---

## 0. Reading guide, form and what changed from v9

### V10-0.1 Form (supersedes §0.1 for v10)

A *unit* is as in v9 §0.1: it begins at each line, outside fenced code blocks, that starts with `# `, `## ` or `### `,
and runs to the line before the next unit's first line (the last unit to end of file); its bytes are those lines with
their line terminators.

v10 is a **change document over v9**. The document is organized as:
- this front matter (the title unit, this §V10-0.1, and §V10-0.7);
- **Part V10-R — units revised or added in full**: the complete composed text of every unit v10 changes pervasively
  or adds, each under its ordinary section heading, so each has its own v10 sha256 computed over its bytes;
- **Part V10-A — amendment blocks**: for a few large v9 units that change in only a few places, the v9 unit id, its
  v9 sha256, and the exact edits (anchored old → new text), so the composed v10 unit is obtained by applying the edits
  to the carried v9 bytes;
- **Part V10-C — the §18.5 change map and the carried-unit binding table**: every one of v9's 134 units with its v9
  identity and its v10 status (CARRIED, COMPOSED, AMENDED, NEW), and, for COMPOSED and NEW units, its v10 line range,
  byte count and sha256 computed by a read-only script over this file (Appendix I records the arithmetic).

Where this document carries a v9 unit unchanged, its authoritative bytes are the v9 unit's bytes, identified by the v9
sha256 that the v9 §18.5 map gives and that the independent v9 reviewer verified against the v9 file; this document
does not re-type them. **W1-V10-FORM** (§V10-0.7) records that a fully self-contained v10 with every unit's bytes
inline and a per-unit v10 sha256 is OPEN, to be produced by a read-only composition that the drafting limits for this
task do not permit the author to run. No carried obligation, fixture, threshold or accepted case is altered by being
carried this way.

### V10-0.7 What v10 changes, per required change (NEW)

The sealed v9 review (`v9-review/claude-v1`, NOT_ENDORSED) names nine new required changes and keeps three
execution-bound ones. Each is answered as follows; "author's assessment" is the author's claim for the independent
reviewer to judge, never closure.

1. **W1-V9-ASYNC-ENUM** — §9.8 (amended: N4(iv), the "From (2) to (3)" paragraph, the N4 absorbing/self-check
   sentence, the P-ASYNC and P-RELEASE rows of N7), §10.6 (amended) and §15.3 (amended): the self-check "never a
   silent change" overclaims are **withdrawn**; the holder boundary is restated so that an outside memory-context
   holder (a `get_task_mm`/`get_task_exe_file` user reachable through a world-readable `/proc` file) is named as a
   holder of a task-created mapping reference and as a context for a deferred final `fput` after the cgroup exit, and
   is shown **held-but-unusable** (it yields no write path and no reference usable by a principal outside the tree).
   P-ASYNC is restated as a **closed specification with a defined enumeration basis** (every entry of both of this
   kernel's system-call tables; every known class of holder that can retain a task-created file or memory reference
   past the cgroup exit — task-work and the delayed-`fput` workqueue, the UNIX-socket garbage collector, outside
   `get_task_mm`/`get_task_exe_file` holders, and io-workqueue/kernel-thread contexts), with the obligation that each
   is shown impossible under the stated confinement or incapable of changing already-committed bytes. The **discharge/
   refute predicate** is a state an operator-run probe must observe — the committed capture byte-equals a re-read
   taken after every such holder is shown released — not a method to force that state; the detailed probe procedure is
   **OPEN**, owned by the operator-prepared package (§16.1, stage E1/E2). Author's assessment: the overclaim is
   corrected and the obligation is stated as a closed specification; P-ASYNC stays NAMED_UNESTABLISHED and
   W1-V7-HOLDER-STATE stays OPEN.
2. **W1-V9-NOOWNER-SCOPE** — §2.3, §5.3, §9.8 N7 (P-NOOWNER row, amended), §11.3 (P12/P13, amended) and §16.1 (O-1):
   P-NOOWNER's route inventory is extended from "rules that name N" to an **inventory obligation over every
   principal**: no sudoers rule of **any** user whose Runas set resolves to N or W through `ALL`, a group
   (`%group`), a uid form (`#uid`), an alias or a negation; no polkit grant to **any** subject for unit management or
   exec-as-user (for example `systemd-run --uid=`); and the same for W. The inventory states **what must be shown**,
   not how to probe it. Author's assessment: CLOSED-AT-SPEC-LEVEL as an obligation; P-NOOWNER stays
   NAMED_UNESTABLISHED and is critical.
3. **W1-V9-ENUM-USERDEL** — §11.4 (amended) and §11.5 (amended, the account class and S-R): the `userdel`
   `USERGROUPS_ENAB yes` co-removal is modelled for **k3 as well as k4** (each account's `userdel` co-removes its
   same-name user-private group: k4→k2, k3→k1), with the intermediate states under the file-update order (X1–X4) and
   the completed-co-removal states (W_A for k4, W_B = X4 for k3); S-R gains **reverse rules from W_A and from every
   co-removed state** that never issue a failing `groupdel`; `/var/log/lastlog` is captured as a possible useradd/
   userdel co-object (observed, never decided from). The reachable set without images is recomputed to **67**
   (JACKAL exact, parsed `4+5+3+2+2+1+1+1+1+7+10+4+6+3+3+4+0+0+2+1+1+1+1+1+1+1+1`; cross-check `63+4` = 67) and with
   images to **104** (JACKAL exact; Appendix I). Author's assessment: CLOSED-AT-SPEC-LEVEL.
4. **W1-V9-PLAN-CONSTRAINTS** — §13.2 (U-11 and I-7 respecified): no allowlisted prover or build action runs outside a
   reviewed, adopted frame under fresh original admission and a dispatch-stage Gate 0 receipt; where that is not yet
   available the step is **blocked by those original gates** and is not run; I-7's comparison gains an
   original-versus-original nondeterminism control. The `strace`-in-original-context form of v9's U-11 (which launched
   the raw prover outside a reviewed frame, contrary to START-CLAUDE.txt:8, under the selftest-stage allowance) is
   withdrawn. Author's assessment: CLOSED-AT-SPEC-LEVEL; the runs stay OPEN and gated.
5. **W1-V9-PREMISE-ORDER** — §16 and §13.2 (S-1, S-2): the independent review of the S-discharges of the critical
   premises (P-KSRC, P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP, P-ASYNC) is required **before O-1 installs the sudo
   rules**, because from the moment the S1 rule exists A1 can drive installed RL through `writer.py selftest`; S-1
   binds the **running kernel image and build-id** (not only the package files) to the package. Author's assessment:
   CLOSED-AT-SPEC-LEVEL for the ordering; the discharges themselves stay OPEN.
6. **W1-V9-RL-SELFTEST-FIXTURE** — §16.1 (O-2), §13, §13.1, §9.8 N5 and §13.2 S-5: **no installed code path, and no
   path reachable through the S1 rule or the RL rule, creates a set-user-ID-root object, a file-capability object or
   drives the writer's test-only switches.** The set-ID and file-capability fixtures become an **operator-only**
   mechanism of the operator-prepared package (stage E1/E2), created and destroyed by the operator harness on a
   sacrificial mount, never by RL's `selftest` verb or any installed verb; the writer/selftest test-only switches are
   removed from installed paths. §2.2 and §9.8 N5 list that no such object is reachable; S-5 requires the code review
   to show that no installed or S1/RL-reachable path can create one or affect real state. The fixtures themselves are
   **not** written here. Author's assessment: CLOSED-AT-SPEC-LEVEL as a removal requirement; the code review (S-5) is
   execution-bound.
7. **W1-V9-INVENTORY** — §12.3 (new OPEN rows V15, V16, V17), §12.2 and §9.3 (amended), §6.1 (amended), §21.3 (new
   rows): the complete-inventory claim gains OPEN V-rows for **V15** (cross-mount `EXDEV` on `rename`/`link`/
   `renameat2` between the run tree, `TMPDIR` and any other host path, which in v5 shared one mount), **V16** (M_run
   id restrictions: no `chgrp` to a supplementary group, no ACL entry naming an id other than 1000, unmapped ids shown
   as the overflow id), and **V17** (per-user-namespace keyrings), each with its §13.2 discharge route; RL is required
   to **close, or mark close-on-exec, every descriptor it opens after step 8** (the held g directory, the helper
   namespace fd, the `open_tree` fds, the Landlock ruleset fd, the seccomp program fd), and G4/C1 are required to check
   the **exact fd set {0,1,2}**, not only fd types. Author's assessment: CLOSED-AT-SPEC-LEVEL for the inventory and the
   descriptor rule; the new V-rows are OPEN like every V-row.
8. **W1-V9-REVIEW-PROVENANCE** — NEW §23, with amendments to §16, §20, §4.6, §8.6, §17, Appendix D (J5/A3/A6) and B.3:
   the decision D-LEAD-REVIEW-PROVENANCE (STATUS.md ~19:05Z) is stated exactly as a **change to an original admission
   join** (not as preservation), with the authority it rests on (the operator's verbatim ~17:05Z direction, quoted)
   and the original texts it changes (HANDOFF.md:173 and complete-phase1-prompt.txt:60) quoted; **every** dependent
   site is enumerated; the replacement join is specified precisely (a sealed Claude-review freeze over
   REVIEW.md/review.json/checks.json, `raw-final-message.txt`, the reviewer agent id, the sha256 of the reviewer task
   output, `reviewer_kind: claude-subagent` and `different_from_author: true`; never a label alone; never a GPT
   claim). Adoption stays blocked until this change is itself reviewed in the frame-design revision. Author's
   assessment: stated as a change, not closed; adoption impossible until reviewed.
9. **W1-V9-FORM-CONSISTENCY** — title unit (the critical-premise list now names P-SECCOMP), §8.1 (schema name
   `wlscratch-role-identity-v2`), §9.1 (schema names `wlscratch-scope-v3`, `wlscratch-census-v2`) and §11.6 (the
   candidate view baseline is **evidence only**, never a comparison baseline). Author's assessment: CLOSED-AT-SPEC-
   LEVEL.

**Carried execution-bound changes** (still required, not closed by any design text):
- **W1-V8-PRESERVATION-ESTABLISH**: every OPEN V/C/D row of §21 keeps its exact discharge route (§13.2); none is
  established in v10; the rows stay OPEN.
- **W1-V8-PREMISE-DISCHARGE**: every N7 premise keeps its executable discharge, now in the order fixed by
  W1-V9-PREMISE-ORDER; none is discharged in v10.
- **W1-V8-EVIDENCE-EQUIV**: the backup consumers B1–B5 and their predicates (§8.5) and the capture (§15.3) are
  unchanged in substance; V-BACKUP/V-VAULT stay OPEN; safe fresh capacity stays the original OPEN obligation.

**New OPEN item raised by this draft:**
- **W1-V10-FORM**: v10 is a change document, not a self-contained re-composition (§V10-0.1). A self-contained v10 with
  every unit's bytes inline and a computed per-unit v10 sha256 is OPEN, to be produced by a read-only composition the
  drafting limits for this task do not permit. This is a form regression of W1-V8-FORM-SUBUNIT; it weakens no
  obligation.

---

# Part V10-R — units revised or added in full

The units in this part carry their own v10 sha256 (computed by the read-only script of §18.5 / Appendix I over this
file). §13, §13.1 and §13.2 are authored afresh for v10: their v9 text (detailed syscall/operand probe recipes) is
**not** reproduced, both because the asynchronous-holder and privilege-boundary procedures are operator-reserved
(front-matter "Two sensitive areas") and because v10 re-frames the plan into the E0/E1/E2 staging. The obligations,
controls, accepted cases and refute criteria of v9 §13–§13.2 are preserved; only the recipes move to the
operator-prepared package and the probe rows are stated by obligation and predicate.

## 13. Probe specification (future; nothing here has been executed; procedures that exercise a privilege boundary or construct a set-ID/capability object are operator-reserved) [corrections: W1-V9-RL-SELFTEST-FIXTURE, W1-V9-INVENTORY, W1-V9-ASYNC-ENUM; carried: W1-V7-PROBES, W1-V6-COPY-PROBES, W1-V6-COMMIT-AMBIGUITY; v6: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY, W1-COMMIT-JOURNAL-EXPORT; gap: denial-probes]

**What a probe can do.** A probe can refute a premise of §9.8 N7; it never establishes one. A premise stays
NAMED_UNESTABLISHED until its source discharge (§13.2 phase E0 source readings) is done and reviewed and no probe has
refuted it. No finite probe and no engineering run is promoted into a universal premise, and no probe result is turned
into an exception: a refuted premise means W-1 must be redesigned (no exception; a refuted critical premise stops every
installed use until the redesign is reviewed, §9.8 N7).

**Staging (E0/E1/E2).** Every step of the plan is assigned a stage by a fixed entry rule.
- **E0 — lead, before setup.** A step is E0 iff it is **unprivileged** (run as `sicarii`, no sudo) **and** mutates
  nothing outside a lead scratch directory under `/home/sicarii/wl-probe-<h>/` **and** runs no prover, compiler or
  WORLDLINE code **and** creates no set-user-ID-or-capability object **and** exercises no privilege boundary that would
  require constructing such an object or driving a cross-principal or cross-namespace attack. E0 holds source readings
  of published sources and benign unprivileged observations whose only effect is on the lead's own scratch objects. A
  step that fails any clause is not E0.
- **E1 — operator, privileged, before install or on a sacrificial setup copy.** Every boundary exercise: anything that
  needs root, a sacrificial account, a set-ID or file-capability object, a device, failure injection, or the driving of
  a kernel privilege boundary (ptrace/`setns`/credential/cross-namespace). E1 steps are delivered in the
  operator-prepared package (§16.1), with their fixtures, and are run or explicitly authorized by the operator; the
  detailed procedures live there, not here.
- **E2 — operator-authorized installed runs.** After setup, the lead runs the reviewed `selftest` verbs and the
  installed observations; the operator runs the privileged installed captures (P-SUDO before/after, failure injection,
  ENOSPC). No installed or `selftest` path creates a set-ID or file-capability object or drives a writer/selftest
  test-only switch (W1-V9-RL-SELFTEST-FIXTURE); any such object a negative case needs is produced only by the operator
  harness at E1/E2.

**Fixtures (W1-V9-RL-SELFTEST-FIXTURE).** Probes run on sacrificial objects, never on a live generation, the real
window file, `~/iPad`, `~/iPadBackup`, `/home/sicarii` itself or `~/.local/share/sia/.gbrain/`. The **set-user-ID-root
and file-capability fixtures are operator-only**: they are built from reviewed source by the operator harness, exist
only on a sacrificial mount the operator controls, and are created and destroyed by that harness (§16.1 O-2). **No
installed code path, and no path reachable through the S1 rule (`writer.py *`) or the RL rule (`sandbox_launch.py *`),
creates such an object or writes it into any view**; RL's `selftest` verb does not create it. The writer's and the
selftest verbs' former test-only switches (v9 §13 Actors; v9 P-DRIFT and P-TERM) are **removed from installed paths**:
any behaviour a probe needs that a switch used to drive is driven only by the operator harness at E1/E2 on sacrificial
objects. The detailed fixture bytes and the boundary-exercise steps are **not** written in this document.

**Actors.** A1: the lead, uid 1000, in the initial user namespace (E0 for benign observations of its own scratch
objects; E1 for any attempt to exercise a boundary against a view process). A2: a process of a sacrificial selftest
view with T's credentials, domain and filter (E2). A3: a process of a second concurrent sacrificial selftest view
(E2). A4: a second writer selftest instance (E2). A5: W, positive controls (E2). A6: root, through the operator's
sacrificial probe harness (E1 positive controls and every set-ID/cap and cross-principal exercise). The euid-W
pull-attempt actor of v9 (A1w) is **not** an installed-reachable actor in v10: the euid-W-towards-a-view-process
exercise is an operator E1 step, because it requires driving a boundary; the design's reliance on it (N2's row for
`writer.py` as W) is a source statement (S-5/E0 code review) and an E1 exercise, not an installed selftest switch.

**Each probe records** the actor's full credentials and namespaces, the exact operation and operands, the
preconditions observed immediately before, the raw errno or success, and, on unexpected success, the whole resulting
state, retained and never cleaned; an unexpected success or an unexpected errno fails the row. The record format is as
v9; the operand-level detail of a boundary exercise is produced and retained by the operator harness at E1/E2.

**Preconditions, checked immediately before each row** (carried from v9): the fixture owner confirms each source
operand's type and each destination name absent; the actor confirms the search permission §6.3 implies for every
ancestor; a `rename`/`link` row states whether its operands are same-mount (the permission errno is expected) or
cross-mount with every earlier check passing (`EXDEV` expected, P-XMNT, V15); a row whose operand fails an earlier
check is labelled with that cause and never counted as `EXDEV` evidence.

## 13.1 Probe set as obligations (future; nothing here has been executed) [corrections: W1-V9-ASYNC-ENUM, W1-V9-RL-SELFTEST-FIXTURE, W1-V9-INVENTORY, W1-V8-PREMISE-DISCHARGE; carried: W1-V7-PROBES, W1-V7-PREMISES]

Each row names a probe, the **obligation** (the property it must establish or the universal it can only refute), its
**stage** by the §13 entry rule, and the **discharge/refute predicate** as a state to observe. The positive controls,
negative cases, cause separations and operand tables of v9 §13/§13.1 are preserved as the content of the operator E1/E2
procedures; they are not reproduced here. "Refute-only" marks a universal premise, which no run establishes.

| Probe | Obligation | Stage | Discharge / refute predicate (a state to observe) |
|---|---|---|---|
| P-PTRACE | N2's pull operations fail for every non-root principal of N2's table except as N2 states; the owner rule is why the owner is N | E0 for the branches reproducible without root on the lead's own namespaces; **E1** for every cross-principal/cross-namespace exercise and the owner-rule demonstration | each cell equals N2's table entry; refuted if any cell grants where N2 denies |
| P-NOCAP, P-NOSUID | a set-ID or file-capability `exec` confers no uid or capability change in a view | **E1/E2** (the set-ID/cap object is operator-only, O-2) | `/proc/self/status` shows no uid or capability change for the operator-built object run in a view; the same object elevates on a non-`nosuid` sacrificial mount (A6 positive control); refuted by any change in the view |
| P-NOOWNER | no process other than RL's helper ever has euid N; no principal resolves to N or W by any sudoers/polkit form (§5.3 inventory) | E0 for the source/code reading and the inventory obligation (reads of the operator-produced inventory); **E1/E2** for the installed census and the root scan | at every census and after every selftest, no process has uid N (A6 scan); the operator inventory shows no principal resolving to N or W; refuted by any such process or any resolving rule |
| P-SECCOMP | the filter returns `ENOSYS` for `io_setup` and `io_uring_setup` on both system-call tables, allows every other call, cannot be removed or bypassed by a view process, and is inherited across `fork`/`exec` | E0 for the BPF-program reading against the installed tables; **E2** in the real view | in a view, the two calls yield `ENOSYS` and every other sampled call is unaffected; a grandchild after two `exec`s still carries the filter; refuted by any other outcome or a removal |
| P-ASYNC, P-RELEASE | **the closed specification of §9.8 N4 is complete** (see the obligation stated there): every kernel mechanism by which a reference to an admitted entry or to a task's address space can outlive the cgroup-populated-0 transition, and every entry by which content could still be written through such a reference afterward, is enumerated against the stated basis and shown either impossible under the stated confinement or incapable of changing already-committed bytes; the final `fput` of an ext4 regular file or directory changes no content, size, mode, owner, link count, mtime or ctime | E0 for the source reading of every enumerated path and holder class; **E1 (operator, procedure OPEN)** for the refutation exercise | **discharge/refute predicate (a state to observe):** the committed capture of a sacrificial tree **byte-equals** a re-read taken after every enumerated holder class has been shown released, for every enumerated holder; refuted if any compared byte or `stat_key` field differs after `populated 0`. The detailed exercise that drives a holder to its release is **OPEN**, owned by the operator package (§16.1 E1); this document states no method to force that state |
| P-ROOT, P-MSET, P-SKEL, P-PROP, P-LOCK, P-LL, P-XMNT (V15), P-FH, P-IDMAP (V16), P-NETNS, P-UCOUNT, P-KEYRING (V17), P-NOATIME | each premise's statement of §9.8 N7 holds on the installed build | E0 for the source reading and the benign unprivileged mount/namespace observations on the lead's own scratch objects that create no set-ID/cap object and exercise no cross-principal boundary; **E1/E2** for the view-internal and cross-principal exercises | the observed state equals the premise's statement (for V15, `EXDEV` on a fully-resolved cross-mount `rename`/`link`/`renameat2`; for V16, M_run shows on-disk W as 1000 and refuses `chgrp`/foreign-id ACL; for V17, the view's keyring is per-user-namespace and unreachable from outside); refuted by any counterexample |
| P-CG, P-SETNS, P-MGR, P-SLICE, P-LOGLEVEL, P-SUDO, P-SIG | the scope/manager/sudo statements of N5/N7 | E0 for the source readings; **E2** for the installed scope and sudo captures (P-SUDO's before/after is O-3) | each observed as its statement; P-SUDO refuted by any new or changed file under the sudo log/db/run paths or a new journal entry for an allowed `NOPASSWD` frame command |
| P-COMMIT, P-CHAIN, P-ENOSPC, P-STREAM, P-SR, P-SETUP, P-MOUNT, V-VAULT | the commit/journal/fallback/stream/reconciliation/setup/vault obligations of §10, §11, §15 | E0 where the logic runs on recorded synthetic inputs and sacrificial lead objects; **E1/E2** for failure injection (O-2's device), ENOSPC (O-2's filesystem) and the installed vault runs | as v9's P-COMMIT/P-CHAIN/P-ENOSPC/P-STREAM/P-SR/V-VAULT predicates; no account is created by a probe; refuted per v9 |

The stream-finality and complete-capture self-checks (§10.6, §15.3) are **evidence for their own observation window
only** (W1-V9-ASYNC-ENUM): an equal pair of `stat_key` readings shows no change **within** the readings; it does not
show the absence of a later write, so no "never a silent change" claim is made.

## 13.2 The probe-and-evidence plan (ordered; the critical-premise discharges are reviewed before O-1 installs the sudo rules) [corrections: W1-V9-PREMISE-ORDER, W1-V9-PLAN-CONSTRAINTS, W1-V9-ASYNC-ENUM, W1-V8-PREMISE-DISCHARGE, W1-V8-PRESERVATION-ESTABLISH, W1-V8-EVIDENCE-EQUIV]

This plan turns every premise of §9.8 N7 and every OPEN row of §21 into a step with a stated obligation and a
discharge/refute predicate, assigned a stage by §13's entry rule. Steps run in the order given; a step that refutes a
premise stops the plan for that premise's dependants and opens a redesign (no exception). Every run is defensive and
records its raw outputs, environment pins and date. **Nothing in this plan was executed for v10.**

**Ordering constraint (W1-V9-PREMISE-ORDER).** The independent review of the **E0 source discharges of the critical
premises** (P-KSRC, P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP, P-ASYNC) is required **before O-1 installs the sudo
rules** (§16). The reason: from the moment the S1 rule exists, A1 can start `writer.py selftest` through it and so
drive installed RL; installed use must not precede the reviewed discharge of the premises on which the identity-mapped
design's host-DAC safety rests. S-1 therefore also binds the **running kernel image and build-id** to the package (not
only the installed files), because P-KSRC concerns the code that runs.

**Phase E0 — source discharges and benign unprivileged observations (lead, before setup).**

| Step | Premises / rows | Obligation | Discharge predicate | Refute predicate |
|---|---|---|---|---|
| S-1 | P-KSRC, T-DISTRO | the installed kernel's source for every function N7 relies on is the published source of the package version; the **running** kernel image and build-id are the package's | `pacman -Qi`/`-Qkk` match; the running-kernel build-id matches the package's; the PKGBUILD checksums and `.config` match the installed build tree | any mismatch: P-KSRC unestablished; every S-2 reading on hold |
| S-2 | every kernel premise of N7 | each premise's statement is shown by the installed build's source on the paths N7 names (for P-ASYNC, the enumeration basis of §9.8 N4 is traversed) | each reading shows its statement, and an independent review accepts the readings (this review precedes O-1) | a reading shows a path the statement excludes: redesign |
| S-3, S-4 | P-MGR, P-SLICE, P-LOGLEVEL, scope properties; P-SUDO | the systemd and sudo statements of N5/N7 | the readings show the statements | a reading contradicts one: redesign / effect reclassification |
| S-5 | T-W, T-RL, P-NOOWNER, P-VIEW (producer code), **W1-V9-RL-SELFTEST-FIXTURE** | the frame code review shows W/W2 make no boundary call and open no other process's `/proc`; RL's helper path runs only the step-10 calls; **and no installed path, nor any S1/RL-reachable path, creates a set-ID or file-capability object, writes one into a view, or can affect real (non-sacrificial) state** | the review confirms each item | a violation: code change and re-review |
| S-6 | TOOL-CLOSURE, V1–V4, V7', V12, V13, V14, V15, V16 for the target part | for each allowlisted action on the pinned toolchain, release-to-installed equality holds and the source shows, for each enumerated facility (sockets/paths, network, mount, set-ID helpers, file capabilities, foreign `/proc`, AIO/`io_uring`, `/tmp` vs `TMPDIR`, cross-mount rename/link, chgrp/foreign-id ACL, per-ns keyrings, per-user limits), either no use or a use whose observable outcome in the view is equal | for each facility and each action/operand/option, no use or an equal-outcome use, release assets equal to installed files | a use the view changes: that V-row is a change and W-1 is redesigned for it |

Phase E0 also holds the benign unprivileged observations v9 placed in phase U that satisfy the E0 entry rule
(environment pins; `O_NOATIME` on the lead's own files; the Landlock and cross-mount and network-namespace
observations on the lead's own sacrificial directories that create no set-ID/cap object and exercise no cross-principal
boundary; the file-handle decode on the lead's own sacrificial subtree; recording v5's original observations in the
lead context for the I-7 comparison; and the sacrificial-export V-VAULT build and restore of U-14). Any v9 phase-U
step that would create a set-ID/cap object, drive a boundary against another principal, or run the prover is **not**
E0 and is moved to E1 (operator).

**Phase E1 — operator-reserved boundary exercises (prepared in §16.1, run or explicitly authorized by the operator).**
Every set-ID/file-capability exercise (P-NOCAP/P-NOSUID), every cross-principal/cross-namespace ptrace and `setns`
exercise (P-PTRACE, P-CG/P-SETNS), the **asynchronous-holder refutation of P-ASYNC/P-RELEASE (procedure OPEN; its
discharge/refute predicate is the byte-equality state of §9.8 N4 and §13.1)**, failure injection (P-COMMIT,
P-SYNCPROV, O-2's device), ENOSPC (O-2), the P-SUDO before/after capture (O-3), and S-R's reconciliation rehearsal
(O-4, O-5). The detailed procedures are delivered as reviewed bytes in the operator package; this document states the
obligation and the predicate for each (§13.1), never the boundary-exercising steps.

**Phase E2 — installed runs (after O-1, through the reviewed selftest verbs and the operator's privileged captures).**

| Step | Premises / rows | Obligation | Predicate |
|---|---|---|---|
| I-1 | P-NS, P-ROOT, P-MSET, P-SKEL, P-PROP, P-NOSUID, P-NOCAP, P-NOOWNER, P-NETNS | the selftest view's rows for these premises, with the operator-only set-ID/cap fixtures (O-2) and RL's root-scan record | every row as its §13.1 predicate; any unexpected success on a critical premise stops the plan and opens a redesign |
| I-2 | P-PTRACE (full matrix) | the matrix of §13.1 with A1, A3 and the controls; the euid-W exercise is the operator E1 step, not an installed switch | every cell as expected |
| I-3 | P-CG, P-SETNS, P-MGR, P-SLICE, P-LOGLEVEL, P-UCOUNT, P-SIG | the scope/manager rows on selftest scopes | as expected |
| I-4 | P-IDMAP (V16), P-NOATIME, P-XMNT (V15), P-LL, P-FH, P-LOCK, P-KEYRING (V17) in the real view | the view rows, including V15 cross-mount `EXDEV`, V16 M_run id restrictions and V17 per-ns keyring | as expected |
| I-5 | P-SECCOMP, P-ASYNC, P-RELEASE in the real view; the stream-finality and capture self-checks | the filter rows; the P-ASYNC **state predicate** (byte-equality after every enumerated holder is released; the driving procedure is the operator E1 step); both self-checks | the two calls `ENOSYS`; every other sampled call unaffected; the byte-equality predicate holds; the self-checks equal within their window; any change after `populated 0` refutes P-ASYNC |
| I-6 | V-BACKUP, V-VAULT on the installed format | the selftest generation's complete capture and exports through `project-vault`, restore and the offline verifier | B1–B5 hold |
| I-7 | P-VIEW, TOOL-CLOSURE (refutation), V-rows, C5, D2, D3 (per-input evidence) | **differential runs under the original gates only (W1-V9-PLAN-CONSTRAINTS):** for each allowlisted action, the same materialization run (a) by the original v5 frame in the original context and (b) in the adopted selftest view, **each under fresh original admission and a dispatch-stage Gate 0 receipt, in a reviewed adopted frame**; compare exit status, streams, report, every partition entry's bytes and metadata (apart from times and inode numbers, which v5 never compares across runs) and the original observations; **with an original-versus-original nondeterminism control** (the original frame run twice in the original context; fields that differ between the two original runs are excluded from the (a)-vs-(b) comparison, so prover nondeterminism is not misattributed to the view) | equality for every compared field that the nondeterminism control does not exclude: per-input evidence only, never the universal relation | any non-excluded difference: the row it touches is refuted for that input and S-6 or a redesign must address it |
| I-8 | original frame controls under the candidate view (C-rows, D-rows) | the frame-v6-W1 selftest counterparts of v5's 85 recorded cases, run against the installed frame and the view, each outcome compared with v5's recorded result | equal outcomes for every case v5 defines; every difference listed against §21's rows; a difference no row explains is a new row |

**W1-V9-PLAN-CONSTRAINTS, stated plainly.** No allowlisted prover or build action (`gnatprove`/`gprbuild`, the five
forms of v5 `command()`) runs outside a reviewed, adopted frame. v9's U-11 (the raw target under `strace` in the
original context) is **withdrawn**: it launched the prover outside a reviewed frame, contrary to START-CLAUDE.txt:8,
and classified it under the selftest-stage allowance. The source census of each facility's use is now obtained by
S-6's **source reading** (E0), not by running the prover; the only runs of an allowlisted action are the I-7
differential runs, which run only under fresh original admission and a dispatch-stage Gate 0 receipt in an adopted
frame, with the nondeterminism control. Until a reviewed adopted frame and that Gate 0 receipt exist, I-7 is
**blocked by those original gates** and is not run; this blocks no obligation open-endedly — the obligation stays OPEN
until the gated run and its review.

**How the rows of §21 close** (unchanged from v9): a V-row by S-6 (the tools' source, with release-to-installed
equality) together with S-5 (the frame); a C-row or D-row by S-5, with I-8 and I-7 as refutation and per-input
evidence; rows no route can close (C1's reader workflow, C6', V10's shared budget) stay OPEN as stated changes.
Premises close by S-1/S-2 (and S-3–S-5 where named) without a refuting probe.

### 16.1 The operator package (prepared, not executed) [corrections: W1-V9-RL-SELFTEST-FIXTURE, W1-V9-NOOWNER-SCOPE, W1-V9-PREMISE-ORDER, W1-V8-PREMISE-DISCHARGE, W1-V8-COMPOSED-ENUM]

Every item below needs root and lies inside the existing reserved setup, probe and rollback authority. Each is
delivered as reviewed bytes with its sha256 in the concrete inventory; the operator runs it, or explicitly authorizes
it; its raw output is retained. None is a new gate. Items O-2′ and the E1 boundary package are the operator-reserved
probes of §13 phase E1.

| Item | Contents | Serves |
|---|---|---|
| O-1 | the setup (S-0, S-A..S-E, S-H, S-I, and S-J with images) with its helpers, expected outputs, sudoers/sshd bytes, the frame staging copy, the instantiated reachable set (67 / 104 states, §11.4) and S-R; the operator-produced prestate inventory, **extended per W1-V9-NOOWNER-SCOPE** to cover, for N and for W, every sudoers rule of any principal whose Runas set resolves to the identity through `ALL`, `%group`, `#uid`, an alias or a negation, and every polkit grant to any subject for unit management or exec-as-user (P12, P13, S-I of §11.5) | every installed step; P-NOOWNER's route inventory |
| O-2′ | **operator-only** sacrificial probe fixtures: (a) a set-user-ID-root program and a file-capability (`cap_dac_override+ep`) program, built from reviewed source, **created and destroyed by the operator harness (A6) on a sacrificial mount, never by RL's `selftest` verb or any installed/S1/RL-reachable path** (W1-V9-RL-SELFTEST-FIXTURE); for the negative cases the operator harness places them into a view's sacrificial `tmpfs` only under operator control; for the positive control the harness runs them on a non-`nosuid` sacrificial mount; (b) a sacrificial loop device with a device-mapper failure target for directory-`fsync` injection (P-COMMIT, P-SYNCPROV); (c) a sacrificial small ext4 filesystem for P-ENOSPC; each with its creation/removal script and before/after captures | I-1 (P-NOSUID, P-NOCAP), P-COMMIT, P-SYNCPROV, P-ENOSPC |
| O-ASYNC (E1) | the **asynchronous-holder refutation package for P-ASYNC/P-RELEASE**: for each holder class enumerated in §9.8 N4 (task-work/delayed-`fput`, UNIX-socket GC, outside `get_task_mm`/`get_task_exe_file` holders, io-workqueue/kernel-thread), a sacrificial exercise whose **only recorded verdict is the byte-equality state predicate of §13.1** (the committed capture byte-equals a re-read taken after every such holder is shown released). The **detailed procedure is OPEN**: it is authored in the operator package by the operator, who runs privileged probes; this document supplies the obligation, the enumeration basis and the predicate, not the steps | P-ASYNC, P-RELEASE (refute-only); the capture and stream-finality self-checks |
| O-3 | P-SUDO's before/after capture (journal cursor, the listings and digests of the sudo log/db/run paths and the audit log) around one invocation of each frame rule by a selftest | P-SUDO |
| O-4 | the rollback of §15.1 as a reviewed script set with its captures and retained-tree manifests, and its rehearsal on a sacrificial copy of the setup (a second sacrificial account pair and tree prepared by O-1's scripts) | §15.1; the rollback states of W1-V8-COMPOSED-ENUM |
| O-5 | S-R's classification run against the rehearsal's recorded observations: **every vector of §11.4's reachable set (67 / 104 states, including the userdel co-removal states X1–X4 / W_A / W_B of W1-V9-ENUM-USERDEL) produced on the sacrificial copy, continued and reversed, with S-R's reverse rules from W_A and from every co-removed state (no failing `groupdel`)** | P-SR; W1-V8-COMPOSED-ENUM |

The critical-premise E0 source discharges (S-1, S-2 for P-NOSUID/P-NOCAP/P-NOOWNER/P-SECCOMP/P-ASYNC) and their
independent review are completed **before** O-1 is run (W1-V9-PREMISE-ORDER, §16).

## 16. Setup, verification and adoption order [corrections: W1-V9-PREMISE-ORDER, W1-V9-REVIEW-PROVENANCE]

1. Independent review of this v10 design (by an independent Claude review subagent, the review track since
   2026-10-05; §23).
2. Frame v6-W1 code implemented, frozen in SOURCE_FRAME (members 0644, directories 0755; the inventory records
   `install_root` and `source_frame`) and reviewed as code, the review sealed in `<SOURCE_FRAME>/review/…` (REVIEW):
   front, writer (including `selftest`, which **creates no set-ID or file-capability object and carries no test-only
   switch reachable through an installed path**, §13, W1-V9-RL-SELFTEST-FIXTURE), RL (`sandbox_launch.py`) and the
   view it builds with its seccomp program, the launcher, child, observer, the final pass, the censuses and RL's root
   scan, the channels, commits, journals, the fallback journal, exports and the complete capture,
   `wlscratch-materialize-capture`, recovery, the selftest verbs and the code-review items of §13.2 S-5 (including
   that no installed or S1/RL-reachable path can create a set-ID/capability object or affect real state). Phase E0 of
   §13.2 (the source discharges S-1..S-4, S-6, and the benign unprivileged observations) runs before or alongside this
   step; its results are part of the installed-evidence review.
3. Concrete setup inventory (fixed numbers; filled prestate P1–P30 **with the extended P-NOOWNER route inventory of
   W1-V9-NOOWNER-SCOPE**, §5.3, §11.3, O-1; exact script texts and digests, with S-J if images are chosen; the
   instantiated reachable set of §11.4, **67 / 104 states including the userdel co-removal states**; expected ACL
   texts; sudoers and sshd bytes; the scope properties; the seccomp program's bytes; the operator package of §16.1),
   reviewed independently.
4. Gate 0, setup stage, on a fresh reading.
5. Operator approval of the concrete setup (the existing reserved authority, not a new gate).
5b. **Independent review of the E0 source discharges of the critical premises** (P-KSRC, P-NOSUID, P-NOCAP, P-NOOWNER,
   P-SECCOMP, P-ASYNC: S-1 with the running-kernel/build-id binding, and S-2's readings), **completed before O-1 runs**
   (W1-V9-PREMISE-ORDER). The reason: from the moment the S1 rule exists, A1 can start `writer.py selftest` through it
   and drive installed RL, so the premises on which the identity-mapped design's host-DAC safety rests must be
   reviewed before the sudo rules are installed. A refuted critical premise stops the plan and opens a redesign; no
   installed use precedes this review.
6. The operator runs, or explicitly authorizes, S-0 to S-I (and S-J if images are chosen) and the operator package's
   E1 probe fixtures (§16.1); O-1 (the sudo rules among them) runs only after step 5b. S-R only after a stopped script,
   by explicit operator choice.
7. Gate 0, selftest stage; lead verification (§11.6), selftests and phase E2 of §13.2 (I-1 to I-8, under the
   W1-V9-PLAN-CONSTRAINTS gating for I-7).
8. Installed-identity, baseline (including the **candidate view baseline, as evidence only**, §11.6), probe and
   source-reading evidence (phases E0, E1, E2) reviewed independently, the review sealed in `<SOURCE_FRAME>/review/…`
   (INSTALLED_REVIEW).
9. Gate 0 with the adopt/materialize-stage expression; then `front.py adopt …`: W commits the fresh installed-frame
   adoption record at `/var/lib/wlscratch/runs/records/adoption-<I>/lead-adoption.json` (§4.6), **whose review-
   provenance joins require the provenance of the review mechanism actually used (§23), not a gpt-6.1-sol rollout**.
10. Gate 0, dispatch stage; only then `materialize` and dispatch, each under fresh original admission.

No step authorizes the next by inference. **The review-provenance join change (§23) is itself a change to an original
admission join (HANDOFF.md:173, complete-phase1-prompt.txt:60), made under the operator's ~17:05Z direction. It is
NOT reviewed. Adoption therefore stays blocked until that change is itself reviewed in the frame-design revision that
follows this W-1 review** (§23). v10 does not reach adoption.

## 20. Non-claims [corrections: W1-V9-REVIEW-PROVENANCE, W1-V9-ASYNC-ENUM, W1-V10-FORM]

- No sufficiency is claimed for any requirement. V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION,
  W1-V7-HOLDER-STATE, Gate 0 and every original Phase One obligation (the 219 entries of `OBLIGATIONS-v2.json`
  included) stay OPEN with their owners, releases and dependencies.
- The same-identity view is not established as preserving the original success domain (§21, §22.4). No change it
  makes is presented as an accepted exception, a narrowed case or a criterion entitlement.
- Every premise of §9.8 N7 is NAMED_UNESTABLISHED. Source readings are not installed-version discharges by themselves;
  probes refute and never establish; trusted-base exclusions are assumptions. The probe-and-evidence plan (§13.2) is a
  plan; nothing in it was run for v10. The asynchronous-holder containment (P-ASYNC, P-RELEASE) is an OPEN obligation,
  stated as a closed specification with its enumeration basis and its observed-state predicate (§9.8 N4, §13.1); its
  refutation exercise is operator-reserved (§16.1 O-ASYNC, procedure OPEN) and **is not asserted here**. The
  stream-finality and capture self-checks are evidence for their observation window only; no "never a silent change"
  claim is made (W1-V9-ASYNC-ENUM).
- No probe, selftest, namespace, mount, seccomp filter, sudo, setup, vault or window action was performed for v10.
- Exact arithmetic (JACKAL `exact`, lane `rat`, not formal-bounded, outside the Lean certificate chain) supplies no
  capacity bound, no geometry, no backup completeness and no correctness of any code. No consequence-ceiling field was
  returned; the results are informational.
- A kernel-enforced writer boundary is not proof of the frame code, not lead authentication, not target confinement
  and not capacity. The ruled residuals (a)–(d) keep exactly their stated limits.
- v10 requests no approval and adds no gate; every privileged element stays inside the existing reserved operator
  setup, probe and rollback authority, prepared as the package of §16.1.
- **The review-provenance join change (§23) is a change to an original admission join, stated as such with its
  authority and the original texts it changes. It is not a loosening by assertion, and it is not reviewed. Adoption is
  blocked until it is reviewed in the frame-design revision.** v10 decides nothing about it beyond stating it.
- **W1-V10-FORM.** v10 is a change document over v9, not a self-contained re-composition; a self-contained v10 with
  every unit's bytes inline and a computed per-unit v10 sha256 is OPEN (§V10-0.1, §V10-0.7). This is a form regression
  of W1-V8-FORM-SUBUNIT and weakens no obligation, fixture, threshold, accepted case or join.

## 23. Review provenance: the join change D-LEAD-REVIEW-PROVENANCE (NEW) [correction: W1-V9-REVIEW-PROVENANCE]

This section states, as a **change to an original admission join** (never as preservation), how the frame's
review-provenance joins are altered so that `adopt` can bind a review produced by the review mechanism the operator
now directs. It does not decide the change for the project: it states it exactly, with its authority and the original
texts it changes, and it keeps adoption blocked until the change is itself reviewed.

**23.1 The conflict.** Frame v5's adoption join requires, for every required independent review, **gpt-6.1-sol rollout
provenance** (`rollout_join`): the compiled `REVIEW_PROFILE` carries `actual_model_selection: gpt-6.1-sol`
(`scratch.py:98-103`), and the join checks exactly one thread and one rollout, the model, cwd, provider, the final
message and its timestamp, and an actual gpt-6.1-sol max-effort exec argv. Since the operator's direction of
2026-10-05 ~17:05Z, independent reviews are made by **Claude review subagents**, which produce no such rollout. As the
joins stand, `adopt` would refuse every Claude review, so the design could never reach adoption.

**23.2 The authority.** The change rests only on the operator's verbatim direction of 2026-10-05 ~17:05Z, recorded in
STATUS.md: *"Whatever you're using GPT 6.1 SOL for you're gonna have to switch of your workflow and use your own
agents for that now."* The lead records this as superseding the earlier model-identity requirement for the review
work, and records D-LEAD-REVIEW-PROVENANCE (STATUS.md ~19:05Z) as the decision that the review-provenance joins will
require the provenance of the review mechanism actually used.

**23.3 The original texts this changes** (quoted so the change is visible as a change, not an assertion):
- `…/outputs/claude-phase1-handoff-20261004/HANDOFF.md:173`: *"Every required independent review uses actual
  `gpt-6.1-sol`, with recorded real selection/call/result provenance, and a different author. Claude may engineer/
  orchestrate but cannot count a Claude review or role label as that GPT-6.1 gate. Earlier Luna reviews are history
  until independent GPT-6.1 re-review. …"*
- `…/outputs/complete-phase1-prompt.txt:60`: *"Use actual gpt-6.1-sol for every required independent review. Confirm
  the actual model identity; never substitute a role label or another model. If unavailable, continue independent
  authorized preparation and engineering, but retain the review gate as blocked. …"*

Replacing the compiled gpt-6.1-sol rollout join by a Claude-review join **changes** what these texts fixed. It is the
human's ~17:05Z direction applied to a guard. It is **not shown "not a loosening" by assertion**: the claim that it
loosens nothing (the new join still refuses anything unsealed, unbound or author-reviewed) is an argument to be
judged, not a conclusion; it must be reviewed in the frame-design revision before any adoption relies on it.

**23.4 The replacement join (precise).** For a Claude review subagent, the review-provenance join requires **all** of,
and binds each into the adoption record and re-checks it at every use:
- the sealed `review-freeze.json` over the review's `REVIEW.md`, `review.json` and `checks.json`, with each file's
  sha256 and the freeze's own sha256;
- `raw-final-message.txt` (the reviewer's verbatim final message as transcribed under seal) with its sha256;
- the reviewer **agent id**;
- the **sha256 of the reviewer's task output** (the harness task-output file the lead sealed from);
- `reviewer_kind: claude-subagent`;
- `different_from_author: true` (the reviewer is never the author; the independence rule is unchanged).

**Never accepted:** a label alone (for example `reviewer_kind` with no freeze and no bound bytes). **Never claimed:**
that a GPT-6.1 gate was met; any exit claim states that its independent reviews were Claude subagents under the
operator's 2026-10-05 direction. The gpt-6.1-sol `rollout_join` is **retained in the schema and the joins for a
GPT-6.1 review** (sealed GPT-6.1 reviews keep their standing); the Claude-review join is the alternative provenance
form for a Claude-subagent review, selected by `reviewer_kind`, and a review of neither recognized form refuses.

**23.5 Every dependent site** (so the change is complete, not only §4.6). Each site's gpt-6.1-sol `rollout_join` /
"provenance triple" is changed to the §23.4 join selected by `reviewer_kind`; for a Claude-subagent review the sealed
Claude-review freeze, `raw-final-message.txt`, reviewer agent id, task-output sha256, `reviewer_kind` and
`different_from_author` replace the rollout. The sites:
1. **§4.6 join 1** — the code-review `rollout_join` (freeze roster, `actual_model_selection`, `different_from_author`,
   one thread/one rollout, model, cwd = REVIEW, provider, final message and timestamp, exec argv).
2. **§4.6 join 2** — the installed-evidence review's "same rollout join".
3. **§4.6** — "both rollout joins except the uniqueness of the rollout file among `~/.codex/sessions`"; for a Claude
   review there is no `~/.codex/sessions` rollout file, so the uniqueness check is replaced by the uniqueness/identity
   of the sealed task-output and agent id that F reports (F still performs the lead-context part; W re-verifies the
   bound bytes).
4. **§4.2 AD4** — the adoption `INPUTS` stream's "two provenance triples (event stream, exec-argv record, rollout)":
   for a Claude review the streamed provenance is the sealed freeze, `raw-final-message.txt`, the agent id and the
   task-output sha256.
5. **§4.2 D7** — F's parent-stage "rollout joins" in `frame_admitted`.
6. **§8.6** — the joined-input `rollout_join` of the code-review and installed-review rosters, and the observation
   "rollout join".
7. **B.3** — the `wlscratch-lead-adoption-v1` adoption key set's provenance keys `reviewer_thread`, `rollout`,
   `turn_contexts`, `session_providers`, `exec_argv`, `exec_argv_record`, `event_stream`,
   `rollout_final_message_sha256`, `rollout_final_timestamp`: for a Claude review these are superseded by (or carried
   as null beside) the Claude-review keys `review_freeze_sha256`, `raw_final_message_sha256`, `reviewer_agent_id`,
   `reviewer_task_output_sha256`, `reviewer_kind`, `different_from_author`; the schema name becomes
   `wlscratch-lead-adoption-v2` to carry both forms (recorded in B.3's amendment).
8. **Appendix D J5** — `admission(parent)` `frame_admitted` "rollout re-join".
9. **Appendix D A3** — `adopt`'s `rollout_join` (F including the rollout-file uniqueness; for a Claude review, the
   task-output/agent-id identity instead).
10. **Appendix D A6** — `frame_admitted`'s adoption checks at every use ("provenance re-pins, rollout re-join"): the
    re-join is the §23.4 join selected by `reviewer_kind`.
11. **§17** — the placement row "`adopt`, `validate_adoption_observation`, `rollout_join`, `review_profile_problems`":
    "`rollout_join`" there now means the §23.4 join by `reviewer_kind`; "every v5 join kept" is qualified by this
    stated change.
12. **§15.3** — the adoption payload pack's "provenance triples": for a Claude review these are the sealed freeze,
    `raw-final-message.txt`, the agent id and the task-output sha256, exported with the adoption increment.
13. **v5's compiled `REVIEW_PROFILE`** (`scratch.py:98-103`, `actual_model_selection: gpt-6.1-sol`): the installed
    frame's compiled profile accepts a second `actual_model_selection` of a Claude subagent, selected by
    `reviewer_kind`, with the §23.4 join; the GPT-6.1 value is retained for a GPT-6.1 review.
14. **§16 step 9** and the former §16 open item: resolved into this stated change; adoption blocked until it is
    reviewed.

**23.6 Status.** This is a change of an original admission join, recorded with its authority and the original texts it
changes, and enumerated across every dependent site. It is **not closed and not reviewed**. It is implemented in the
frame-design revision that follows this W-1 review and goes through its own independent review; **until then `adopt`
cannot bind any review of either form and v10 cannot reach adoption.** The join still refuses anything unsealed,
unbound or author-reviewed, and never a label alone; whether that makes it "not a loosening" is for the frame-design
review to judge.

---

# Part V10-A — amendment blocks (large/low-change v9 units, carried by sha256 with exact edits)

Each block names the v9 unit, its v9 sha256 (from v9 §18.5, verified by the independent v9 reviewer against the v9
file), and the exact edits. The composed v10 unit is the v9 unit with the edits applied; its v10 sha256 is produced by
the read-only composition recorded OPEN under W1-V10-FORM (§V10-0.1). Anchors quote v9 text verbatim where given;
where an edit is described against a named sub-element, the composer applies it to that sub-element of the carried v9
bytes. No edit weakens an obligation, fixture, threshold, accepted case or join.

## A-§2.2 Trusted base — v9 sha256 `f954d0a34a6d4eb0952d04b74d966e115ece877ea302dcba7cda7df19b569c2c` [W1-V9-RL-SELFTEST-FIXTURE]
- **Append**, after the sentence ending "…runs RL's code and exits (§5.3).":
  " No installed code path, and no path reachable through the S1 rule (`writer.py *`) or the RL rule
  (`sandbox_launch.py *`), creates a set-user-ID-root object or a file-capability object or drives a writer/selftest
  test-only switch; the set-ID and file-capability probe fixtures are operator-only (§13, §16.1 O-2′), so an installed
  failure of P-NOSUID or P-NOCAP could not be combined with an on-demand set-ID object (W1-V9-RL-SELFTEST-FIXTURE)."

## A-§2.3 Preconditions — v9 sha256 `698fa0836f497267eae07b89aeecfba6d8cfc56f8d33054ad860b79d937d2210` [W1-V9-NOOWNER-SCOPE]
- In the first bullet "**No privilege route for `sicarii`.**", **replace** the clause
  "no `NOPASSWD` sudo rule yielding root or those identities, no polkit rule granting `sicarii` (or a group it is in) a
  passwordless `YES`,"
  with:
  "no `NOPASSWD` sudo rule, of `sicarii` or of **any** principal whose Runas set resolves to `wlscratch` (W) or
  `wlscratch-ns` (N) through `ALL`, a group (`%group`), a uid (`#uid`), an alias or a negation, yielding root or those
  identities; no polkit grant to **any** subject (not only `sicarii` or a group it is in) for unit management or
  exec-as-user (for example `systemd-run --uid=`);".
- **Append** to that bullet: " This inventory is the obligation of P-NOOWNER (§9.8 N7) and of §5.3; it states what the
  operator-produced inventory must show for N and for W over every principal and every Runas/polkit form
  (W1-V9-NOOWNER-SCOPE), not how to probe it."

## A-§5.3 Entrypoint closure — v9 sha256 `afba96af1fe021ef8a8705a4bfcf785481182ae4698070d3a361169694e4a647` [W1-V9-NOOWNER-SCOPE]
- **Replace** the `sudo` row's W cell
  "only rule naming W: the S1 rule `sicarii ALL=(wlscratch) NOPASSWD: WLSCRATCH_W` (§11.5 S-D); no other sudoers rule
  lists W in a Runas or user list, and no `sicarii` rule has Runas `ALL` without a password (operator inventory). A1
  can therefore run `writer.py` as W with any arguments; what that process can reach is stated in §9.8 N2"
  with:
  "only rule yielding W: the S1 rule `sicarii ALL=(wlscratch) NOPASSWD: WLSCRATCH_W` (§11.5 S-D). The operator
  inventory shows that **no sudoers rule of any principal** resolves its Runas set to W through `ALL`, a group
  (`%group`), a uid (`#uid`), an alias or a negation without a password, and that no rule lists W in a user or Runas
  list except the S1 rule. A1 can therefore run `writer.py` as W with any arguments; what that process can reach is
  stated in §9.8 N2".
- **Replace** the `sudo` row's N cell
  "no sudo rule names N in a Runas or user list (operator inventory, P12); the RL rule runs RL as root, and RL gives N
  only to its own short-lived helpers, which run RL's code, create one namespace and exit (§12.2 step 10)"
  with:
  "the operator inventory shows that **no sudoers rule of any principal** resolves its Runas set to N through `ALL`, a
  group, a uid, an alias or a negation, and that no rule lists N in a user or Runas list (P12); the RL rule runs RL as
  root, and RL gives N only to its own short-lived helpers, which run RL's code, create one namespace and exit (§12.2
  step 10)".
- **Replace** the `polkit, pkexec, run0, machinectl` row's W cell
  "require admin authentication (`unix-group:wheel`, interactive); no rules.d grant (operator inventory); `empower`
  empty"
  with:
  "require admin authentication (`unix-group:wheel`, interactive); the operator inventory shows **no polkit grant to
  any subject** (not only `sicarii` or a group it is in) for unit management or exec-as-user that could yield W (for
  example a `systemd-run`/`systemctl` action with `--uid=wlscratch` or a `org.freedesktop.systemd1.manage-units`
  allow); `empower` empty"; and the N cell's "same" is read against this extended W cell.
- **Append** after the table a paragraph:
  "**P-NOOWNER / P-W route inventory (obligation, W1-V9-NOOWNER-SCOPE).** The inventory discharging the `sudo` and
  `polkit` rows above must be shown over **every** principal, not only `sicarii` and not only rules that literally name
  W or N: for each of W and N, there is no sudoers rule of any user or group whose Runas set resolves to the identity
  through `ALL`, `%group`, `#uid`, a `User_Alias`/`Runas_Alias`, or a negation; and no polkit authority (rule, pkla, or
  compiled action default) grants any subject a passwordless path to manage a unit or exec as the identity. This states
  what must be shown; §16.1 O-1 carries the operator-produced evidence, and §13.2 S-5/E0 reads the frame's own
  non-reliance on any such route."

## A-§6.1 Recipe and record modes — v9 sha256 `3d18ff6cf3be2307f6980717d1796fd4963eed1bddb4d51232ac59c328d2d608` [W1-V9-INVENTORY]
- **Append** to the paragraph ending "…v6's copied ACLs are withdrawn with the copy route).":
  " Through the M_run idmapped bind (uid/gid `W 1000 1`), a target process cannot `chgrp` an entry below `source/` to a
  supplementary group and cannot set an ACL entry naming an id other than 1000; an unmapped id appears as the overflow
  id. This is an observable change against v5 (where the target could set such group ownership and ACL entries), listed
  as the OPEN row **V16** (§12.3, §21.3); it is not a new refusal by rule, only the idmap's effect, and it is recorded,
  not narrowed (W1-V9-INVENTORY)."

## A-§8.1 Per-invocation role identity — v9 sha256 `818cd88571e5eeb889a08aae3a267c1a63abc20b07948478d6a608361fd31c91` [W1-V9-FORM-CONSISTENCY]
- **Replace** "records a fresh `wlscratch-role-identity-v1` (Appendix B.1)" with
  "records a fresh `wlscratch-role-identity-v2` (Appendix B.1)" (the body now matches the schema name B.1 defines;
  W1-V9-FORM-CONSISTENCY).

## A-§9.1 Participant set and schemas — v9 sha256 `bb6878ba3ff06de0beee08216c93ad10d2e4d4e483b8fdab0c693cb757e15502` [W1-V9-FORM-CONSISTENCY]
- **Replace** "`wlscratch-scope-v2`" with "`wlscratch-scope-v3`" and "`wlscratch-census-v1`" with
  "`wlscratch-census-v2`" (the body now matches the schema names B.2 defines; W1-V9-FORM-CONSISTENCY).

## A-§9.3 Launch gating — v9 sha256 `17a191ab2b3e38f1edc2808573e60375be8195f0b567f36ce2df5a4be962624a` [W1-V9-INVENTORY]
- **Amend G4 and C1**: in addition to the fd-**type** checks each already performs, each verifies that the process's
  **exact open-fd set is {0,1,2}** (no descriptor other than 0, 1 and 2 is open), read from `/proc/self/fd`, and
  refuses before launch (G4) or fails (C1) on any extra descriptor. This makes the descriptor check exact, not
  type-only (W1-V9-INVENTORY), and pairs with the §12.2 step-12 requirement that every descriptor RL opens after step
  8 is closed or close-on-exec.

## A-§11.3 Prestate inventory — v9 sha256 `88d54fa1f3dd5c7273297996b0bd0318421b84767a802f3538f80f7c7da033d6` [W1-V9-NOOWNER-SCOPE]
- **Extend P12** (sudo inventory) so that it establishes, for N **and for W**, that no sudoers rule of any principal
  resolves its Runas set to the identity through `ALL`, `%group`, `#uid`, a `User_Alias`/`Runas_Alias` or a negation,
  and that none lists the identity in a user or Runas list except the S1 rule (for W). The `sudo -l -U <principal>`
  checks are run for `sicarii`, `wlscratch`, `wlscratch-ns` **and for every other non-root account** the host carries
  (for example `cosmov1lab`, `wlrehearsal`, `wldrill`, `worldline`), and the rule set is read for any `%group`/`#uid`/
  alias/negation that resolves to W or N.
- **Extend P13** (polkit inventory) so that it establishes that no polkit authority grants **any** subject a
  passwordless path to manage a unit or exec as W or N, not only grants to `sicarii` or its groups.

## A-§9.8 Custody by the same-identity view — v9 sha256 `9d84e8e6f9f01c833468290b639c6804994cce69b9ff9b0fed542baafd5c84d5` [W1-V9-ASYNC-ENUM, W1-V9-NOOWNER-SCOPE, W1-V9-PREMISE-ORDER, W1-V9-RL-SELFTEST-FIXTURE]

- **N4(iv) — replace** the clause
  "(iv) the deferred final `fput` of a file (task work before the cgroup exit, or later through the UNIX socket garbage
  collector for a descriptor caught in an unreachable socket) runs the filesystem's `release`, which on ext4 changes no
  content, size, mode, owner, link count, mtime or ctime (P-RELEASE);"
  with:
  "(iv) the deferred final `fput` of a file runs in one of these contexts — task work before the cgroup exit; later
  through the UNIX-socket garbage collector for a descriptor caught in an unreachable socket; or, for a file mapped by
  a task, in the context of the **last releaser of that task's memory**, which may be an **outside holder** of the
  memory (a `get_task_mm`/`get_task_exe_file` user reachable through a world-readable `/proc` file) dropping the
  mapping's `vm_file` reference **after** the cgroup exit — and in every such context runs the filesystem's `release`,
  which on ext4 changes no content, size, mode, owner, link count, mtime or ctime (P-RELEASE). Such an outside holder
  holds a task-created mapping **reference** but no **usable** reference and no write path: by N0's definition the
  reference yields no operation a principal outside the tree can perform (reading the memory needs ptrace access, which
  N2 denies; with the asynchronous submission interfaces unavailable there is no pending write), so it is
  **held-but-unusable**;"
- **"From (2) to (3)" — replace** the paragraph
  "*From (2) to (3):* by (i)-(vi), every logical mutation that a task of U can cause has taken effect before that
  task's cgroup exit, or never will; and every reference a task of U created is held by tasks of U, by sockets only
  they could read, or by kernel objects reachable only through those (N1-N3), none by a principal outside the tree."
  with:
  "*From (2) to (3):* by (i)-(vi), every logical mutation that a task of U can cause has taken effect before that
  task's cgroup exit, or never will; and every reference a task of U created is held by tasks of U, by sockets only
  they could read, by kernel objects reachable only through those (N1-N3), **or — for a mapping reference whose memory
  an outside principal holds through a world-readable `/proc` file — by that outside holder, which holds it but cannot
  use it (N0, N2) and through which no content can change (by (iii) there is no asynchronous write, and by N2 no
  outside process can write the memory)**. No **usable** reference, and no reference through which content can change,
  is held by a principal outside the tree; v8's and v9's unqualified 'none by a principal outside the tree' is
  corrected to this held-but-unusable statement (W1-V9-ASYNC-ENUM)."
- **Absorbing / self-check — replace** the sentence
  "The two consumers of H(U) — the complete capture (§15.3) and stream finality (§10.6) — add their own self-checks, so
  that a refutation of P-ASYNC in practice would show as a failed check rather than as a silently wrong record."
  with:
  "The two consumers of H(U) — the complete capture (§15.3) and stream finality (§10.6) — add their own self-checks.
  **Each self-check is evidence for its own observation window only: an equal pair (or triple) of `stat_key` readings
  shows no change between the readings, not the absence of a later write, so no 'never a silent change' claim is made
  (W1-V9-ASYNC-ENUM).** The completeness of N4's closed list (i)-(vi) over the installed kernel is the obligation
  P-ASYNC, discharged only by the source enumeration of §13.2 S-2 over the basis stated in N7, and refuted only by the
  operator-reserved exercise of §16.1 O-ASYNC under the observed-state predicate of §13.1."
- **N7 P-KSRC row — append** to its statement, before the `|` that ends the statement cell: " ; S-1 binds the
  **running** kernel image and build-id to the package, not only the installed files (W1-V9-PREMISE-ORDER)".
- **N7 P-NOOWNER row — replace** the discharge-kind cell
  "S (RL code, the §5.3 route table, sudoers and PAM inventory), T (root), P"
  with:
  "S (RL code; the §5.3 route table **over every principal and every Runas/polkit form that could resolve to N or W**,
  W1-V9-NOOWNER-SCOPE; the sudoers, polkit and PAM inventory of §11.3 P12/P13), T (root), P".
- **N7 P-ASYNC row — replace** the whole row
  "| P-ASYNC | N4's closed list (i)-(vi) is complete for the installed kernel: with Linux AIO and `io_uring`
  unavailable, every logical mutation of a regular file or directory caused by a task completes before that task's
  cgroup exit, or never | S | S-2; U-9 and I-5 refute only |"
  with:
  "| P-ASYNC | **(closed specification; obligation.)** Every kernel mechanism by which a reference to an admitted entry
  or to a task's address space can outlive the cgroup-populated-0 transition, and every entry by which content could
  still be written through such a reference afterward, is enumerated against the basis below and shown either
  impossible under the stated confinement (Landlock topology; `nosuid`; the private network and user namespaces; the
  seccomp `ENOSYS` of `io_setup`/`io_uring_setup`) or incapable of changing already-committed bytes.
  **Enumeration basis:** every entry of both of this kernel's system-call tables (`AUDIT_ARCH_AARCH64` and the
  `AUDIT_ARCH_ARM` compatibility table); and every known class of holder that can retain a task-created file or memory
  reference past the cgroup exit — task-work and the delayed-`fput` workqueue; the UNIX-socket garbage collector;
  outside `get_task_mm`/`get_task_exe_file` holders reachable through world-readable `/proc` files; io-workqueue and
  kernel-thread contexts. The two asynchronous submission interfaces are unavailable (P-SECCOMP), so no request
  outlives its submitting task. | S (the enumeration traversed in the installed source, S-2) | S-2 (E0 source
  enumeration); O-ASYNC / I-5 **refute only**, under the observed-state predicate of §13.1 (the committed capture
  byte-equals a re-read taken after every enumerated holder class is shown released); the detailed exercise is OPEN
  (operator, §16.1 O-ASYNC) |".
- **N5 — append**, after the N5 effect table: "**No frame-caused effect creates a set-user-ID or file-capability
  object**, and no installed path, nor any path reachable through the S1 or RL rule, creates one; the set-ID and
  file-capability probe fixtures are operator-only (§13, §16.1 O-2′), so an installed failure of a critical premise
  could not be combined with an on-demand set-ID object at A1's request (W1-V9-RL-SELFTEST-FIXTURE)."

## A-§10.6 Consumers / stream finality — v9 sha256 `e922ecf42fcaeb673d72fa459602d9de4b103216c447ab1e4c9cc4ae3bd1b071` [W1-V9-ASYNC-ENUM]
- **Replace** "The finality claim is therefore observed (K and the equal readings) plus P-ASYNC; a refutation of
  P-ASYNC in practice would show as a failed self-check, never as a silent change."
  with:
  "The finality claim is therefore observed (K and the equal readings) plus P-ASYNC. **The self-check is evidence for
  its own window only: the three equal `stat_key` readings show no change between them, not the absence of a later
  write, so no 'never a silent change' claim is made (W1-V9-ASYNC-ENUM).** A change the self-check catches records the
  streams as not final; a change outside its window is bounded only by P-ASYNC, which the §13.1 state predicate and the
  operator-reserved exercise (§16.1 O-ASYNC) refute, never establish."

## A-§15.3 The complete capture — v9 sha256 `c63a0485c9548f73a653b7f7acc2999d27133288b5b3e353f70979982a1e8ee7` [W1-V9-ASYNC-ENUM]
- **Replace** "Because the capture starts only after (1) and, under P-ASYNC, no write of a task of U can take effect
  after its cgroup exit (§9.8 N4), a failure would refute P-ASYNC in practice rather than silently capture a moving
  tree."
  with:
  "The capture starts only after (1); under P-ASYNC (a closed specification discharged by source enumeration, §9.8 N4,
  §13.2 S-2) no write of a task of U can take effect after its cgroup exit. **The self-check (the before/after
  `stat_key` pairs and the two walks) is evidence for its own window only: an equal pair shows no change between the
  readings, not the absence of a later write.** A caught difference makes the capture `failed`; a change outside the
  self-check's window is bounded only by P-ASYNC, which the operator-reserved exercise (§16.1 O-ASYNC) and I-5 refute
  under the state predicate of §13.1, never establish. No 'never a silent change' claim is made (W1-V9-ASYNC-ENUM)."

## A-§11.4 Staged atoms and the reachable set — v9 sha256 `165128c67ddb943e055d82157760cd177c45aeadfc38ca30b694a10b97db6182` [W1-V9-ENUM-USERDEL]
- **Replace** the W_A bullet
  "- W_A: the co-object state of S-R's reversal of k4 under `USERGROUPS_ENAB yes`, where `userdel wlscratch-ns` also
  removes group `wlscratch-ns` (k2's object) while k1 and k3 stay in their post-states."
  with:
  "- The **`userdel` `USERGROUPS_ENAB yes` co-removal states** (correction W1-V9-ENUM-USERDEL). `/etc/login.defs` sets
  `USERGROUPS_ENAB yes`, so **each** account's `userdel` also removes the same-name user-private group: the reversal of
  k4 (`userdel wlscratch-ns`) co-removes group `wlscratch-ns` (k2), and the reversal of k3 (`userdel wlscratch`)
  co-removes group `wlscratch` (k1). v9 modelled only W_A (the k4 case); v10 adds the k3 case and the intermediate
  states under the file-update order (passwd before shadow for the account; group before `gshadow` for the group).
  **W_A** (already among v9's 63): k4 removed, group k2 co-removed, k1 and k3 in post. The four **new** constant states
  are:
    - **X1**: inside k4's `userdel` (k4 absent), the co-removed group k2 mid-removal (group line gone, `gshadow`
      remains: k2 = 'gshadow without group'), k1 and k3 in post;
    - **X2**: after W_A, inside k3's `userdel` (k3 absent, k2 absent), the account mid-removal (k3 = 'shadow without
      passwd');
    - **X3**: from G_3 (k4 not created), inside k3's `userdel` (k3 absent), the co-removed group k1 mid-removal (k1 =
      'gshadow without group'), k2 in post;
    - **X4 = W_B**: k3 removed, group k1 co-removed, k2 in post, k4 absent (the completed co-removal on the k3 reversal
      path).
  S-R gains reverse and resume rules from W_A, W_B and X1–X3 that never issue a known-failing `groupdel` (§11.5).
  `/var/log/lastlog` (present, 0 bytes) is recorded as a possible `useradd`/`userdel` co-object of an account atom: S-R
  and S-I capture its state as data, never deciding from it."
- **Replace** the reachable-set count (the sentence beginning "Their number is 63 + 3·n_d + 5·n_m (JACKAL exact: parsed
  `4+5+3+2+2+1+1+1+1+7+10+4+6+3+3+4+0+0+2+1+1+1+1` gives 63, …") so that the number is **67 + 3·n_d + 5·n_m**, the
  parsed string is `4+5+3+2+2+1+1+1+1+7+10+4+6+3+3+4+0+0+2+1+1+1+1+1+1+1+1` (JACKAL exact = 67; cross-check `63+4` =
  67; Appendix I I1′), and the reading adds "the four `userdel` co-removal constant states X1, X2, X3 and X4 = W_B
  (W_A already being among v9's 63)" to v9's reading. The per-list coefficients (`1+2` = 3 per frame directory, `1+3+1`
  = 5 per frame member) are unchanged.
- **Replace** the with-images count so that it is **104 + 3·n_d + 5·n_m** (JACKAL exact = 104; Appendix I I2′), with the
  parsed string extended by the same four `+1`.

## A-§11.5 Setup scripts: account class and S-R — v9 sha256 `c809520b94062d6fa33b561af2f2c02ac37ec156a9162cc4c3cdd0d91fb46ff8` [W1-V9-ENUM-USERDEL, W1-V9-NOOWNER-SCOPE, W1-V9-RL-SELFTEST-FIXTURE]
- **Amend the `account` and `account-expired` class rows** of the Atom-classes table: the reversing-action cell states
  that `userdel` co-removes the same-name user-private group for **each** account atom (k3→k1, k4→k2) under
  `USERGROUPS_ENAB yes`; the completed co-removal states are W_A (k4) and W_B (k3) with intermediates X1/X2/X3 (§11.4);
  and the reversal does **not** subsequently issue a `groupdel` for a group a later `userdel` already co-removed.
- **Amend S-R step 4 (resume)**: "from W_A, run atom 2's forward action (restore group k2)" is extended to: "from W_A,
  run atom 2's forward action (restore group k2); from W_B, run atom 1's forward action (restore group k1); from an X1,
  X2 or X3 intermediate, first let the in-progress `userdel` co-removal complete to its W_A/W_B state, then resume from
  there."
- **Amend S-R step 4 (reverse)** and the stop rule: at an atom whose same-name user-private group was already
  co-removed by a later `userdel` (W_A, W_B, X1–X3), the reversal **confirms the group absent** (the co-removal already
  reached the group atom's pre-state) and continues with the next atom's reversing action; it does **not** issue the
  group's `groupdel`, so no reversing command is a known-failing `groupdel` and S-R does not stop on it
  (W1-V9-ENUM-USERDEL; this removes the v9 defect where S-R's reversing `groupdel` of an already co-removed group
  failed and stopped S-R).
- **Amend S-I**: add to its captures (i) the **extended P-NOOWNER inventory** — `sudo -l -U` for `sicarii`,
  `wlscratch`, `wlscratch-ns` **and every other non-root account**, plus the rule-set read for any `%group`/`#uid`/
  alias/negation Runas resolving to W or N, and the polkit inventory over every subject (W1-V9-NOOWNER-SCOPE); (ii)
  `/var/log/lastlog`'s state as data (W1-V9-ENUM-USERDEL); and (iii) confirmation that `find / -xdev -perm /6000` and
  `getcap -r /usr` show no set-ID or file-capability object owned by W or N or created by any installed path
  (W1-V9-RL-SELFTEST-FIXTURE).

## A-§11.6 Post-setup verification — v9 sha256 `d0f19a4c6ca8991a4ff06e94687723a8b967797778fac7c277ce3ae30907c8f2` [W1-V9-FORM-CONSISTENCY]
- **Replace** "as the candidate view baseline, which is reviewed with the installed evidence before adoption (§16);"
  with:
  "as the candidate view baseline, which is **evidence only** — reviewed with the installed evidence before adoption
  (§16) and **never used as a comparison baseline** (the only new comparison baseline is the writer-context one of
  §8.4; W1-V9-FORM-CONSISTENCY);".

## A-§12.2 RL and the view, step 12 — v9 sha256 `43a1796a7072f0301c9e5e03abb4defd601da4fddcf6d279d1cbd8b1f46ad7c6` [W1-V9-INVENTORY]
- **Replace** "Every descriptor opened before step 8 except fds 0-2 is closed now; fds 0-2 refer to W's socket and W's
  stream files on host mounts by design."
  with:
  "Every descriptor opened before step 8 except fds 0-2 is closed now; fds 0-2 refer to W's socket and W's stream files
  on host mounts by design. **Every descriptor RL opens after step 8 — the held g directory, the helper's
  user-namespace fd, the `open_tree` fds, the Landlock ruleset fd and the seccomp program fd — is opened `O_CLOEXEC` or
  is explicitly closed before `execve` (step 16); RL verifies immediately before `execve` that its exact open-fd set is
  {0,1,2}, which pairs with G4's and C1's exact {0,1,2} check (§9.3, W1-V9-INVENTORY).**"

## A-§12.3 View-change inventory: new OPEN rows — v9 sha256 `b9392577ca84a9c6741e0a0113036b34307d3c2029966cf67e5d0540751ea014` [W1-V9-INVENTORY]
- **Insert**, as new rows at the end of the §12.3 table (before the "v7's V5 … stay removed" paragraph):
  "| V15 | between the run tree, `TMPDIR` and any other host path, `rename`, `link` and `renameat2` fail with `EXDEV`
  (in v5 these shared one mount, mount ID 32); the errno is `EXDEV` only when resolution and every earlier check pass
  | the two binds are distinct mounts (P-XMNT) | the target cannot move or hard-link an entry across the run tree /
  `TMPDIR` / host boundary, which v5's single mount allowed |
  | V16 | through M_run (uid/gid `W 1000 1`) the target cannot `chgrp` an entry below `source/` to a supplementary
  group and cannot set an ACL entry naming an id other than 1000; an unmapped id shows as the overflow id | M_run
  idmap (P-IDMAP) | enforced-location identity of generation bytes (on-disk W) |
  | V17 | the view's keyrings are per user namespace (U8): a session/user keyring in the view is not the host's, and
  host keyrings are unreachable from the view | U8 | follows from the user namespace (V13) |"

## A-§21.3 Target-world changes: new discharge rows — v9 sha256 `c88585c55cf0cd068baa975b96f7619bcc61f005e51a4381affc87d1ddfd305e` [W1-V9-INVENTORY]
- **Insert**, as new rows at the end of the §21.3 table (each OPEN):
  "| V15 | cross-mount `EXDEV` | the run tree, `TMPDIR` and host paths are distinct mounts (v5: one mount) | S-6; S-5;
  I-4 | closes if S-6 shows no allowlisted action moves or hard-links an entry across the run tree / `TMPDIR` / host
  boundary; refuted by any such use |
  | V16 | M_run id restrictions | enforced-location identity of generation bytes | S-6; S-5; I-4 | closes if no
  action `chgrp`s a generation entry to a supplementary group or sets a foreign-id ACL and no reader depends on such
  ownership/ACL; refuted otherwise |
  | V17 | per-namespace keyrings | the user namespace (V13) | S-6; I-4 | closes if no allowlisted action uses a keyring
  whose contents or scope the view changes; refuted otherwise |"

## A-§4.6, §8.6, §17, Appendix D, B.3 — review-provenance sites [W1-V9-REVIEW-PROVENANCE]

Every edit below changes a gpt-6.1-sol `rollout_join` / "provenance triple" to the join of §23.4 **selected by
`reviewer_kind`**: for a Claude-subagent review the sealed Claude-review freeze (over REVIEW.md/review.json/
checks.json), `raw-final-message.txt`, the reviewer agent id, the sha256 of the reviewer task output, `reviewer_kind:
claude-subagent` and `different_from_author: true` replace the rollout; a gpt-6.1-sol review keeps the rollout join; a
review of neither recognized form refuses. §23 holds the full statement, the authority and the original texts; these
blocks mark the sites so the change is complete.

- **§4.6** — v9 sha256 `00b3ed65328eb21773f171bf89852ac17c227e4c242c254aa4e2bc5c739eb234`. In joins 1 and 2 and in
  the sentence "both rollout joins except the uniqueness of the rollout file among `~/.codex/sessions`", the
  `rollout_join` is the §23.4 join by `reviewer_kind`; for a Claude review there is no `~/.codex/sessions` rollout
  file, so the uniqueness check is replaced by the identity of the sealed task-output sha256 and the reviewer agent id
  that F reports and W re-verifies over the bound bytes. The record's bound keys follow B.3's amendment
  (`wlscratch-lead-adoption-v2`).
- **§4.2 AD4 and D7** (unit §4.2, v9 sha256 `28116cedfbb901f9a161eba4427e4aa1e8603aa961e991aab7b7e05c09dd246d`) —
  AD4's "two provenance triples (event stream, exec-argv record, rollout)" and D7's "rollout joins" are, for a Claude
  review, the sealed freeze, `raw-final-message.txt`, the agent id and the task-output sha256, streamed and re-joined
  by `reviewer_kind`.
- **§8.6** — v9 sha256 `3ec9d7f237addb503a8f3a90434741ae57e7386139ae3ab5b5a06271ae25dd1f`. The joined-input
  `rollout_join` of the two rosters and the observation "rollout join" become the §23.4 join by `reviewer_kind`.
- **§17** — v9 sha256 `2c819d7d7a8025b4844b931432a0686efa666c1c8d1ac9c97b7440b69e2c39f4`. In the `adopt`/`rollout_join`
  placement row, "`rollout_join`" means the §23.4 join by `reviewer_kind`; the row's "every v5 join kept" is qualified
  by this stated change (§23).
- **Appendix D** — v9 sha256 `f00e0b1b9c786fddced73bf368ddd416d57d13b6afcf5d78fad73dd86415e3a1`. Rows **J5** (`frame_admitted`
  "rollout re-join"), **A3** (`adopt`'s `rollout_join`, including F's rollout-file uniqueness — for a Claude review the
  task-output/agent-id identity instead) and **A6** (`frame_admitted`'s "rollout re-join" at every use) perform the
  §23.4 join by `reviewer_kind`. The A5/A6 schema expectation becomes `wlscratch-lead-adoption-v2` (below).
- **B.3** — v9 sha256 `d5d6f30ee183ad65fa9cfb379b627511d632aec8174bc24499e0ab9f621c8b6c`. Rename the adoption schema
  `wlscratch-lead-adoption-v1` → `wlscratch-lead-adoption-v2` and add the Claude-review provenance keys
  (`review_freeze_sha256`, `raw_final_message_sha256`, `reviewer_agent_id`, `reviewer_task_output_sha256`,
  `reviewer_kind`, `different_from_author`) beside the gpt-6.1-sol keys (`reviewer_thread`, `rollout`, `turn_contexts`,
  `session_providers`, `exec_argv`, `exec_argv_record`, `event_stream`, `rollout_final_message_sha256`,
  `rollout_final_timestamp`); for a given review exactly one form's keys are present and non-null, selected by
  `reviewer_kind`, and the other form's keys are absent or null. `scratch.py:98-103`'s compiled `REVIEW_PROFILE`
  accepts a `claude-subagent` `actual_model_selection` with the §23.4 join, keeping the gpt-6.1-sol value for a
  GPT-6.1 review.

---

# Part V10-C — change map and carried-unit binding table

## V10-C.1 Carried-unit binding

Every v9 unit not listed in Part V10-R or Part V10-A is **carried unchanged**; its authoritative bytes are the v9
unit's bytes, identified by the v9 §18.5 sha256 that the independent v9 reviewer verified against the v9 file. v10 does
not re-type them. The full per-unit list is the §18.5 change map below (status CARRIED), which gives each carried
unit's v9 line range, byte count and sha256. No carried obligation, fixture, control, threshold, accepted case,
criterion, allowance, cap or join is altered by being carried.

### 18.5 Change map (every v9 unit, with its v9 identity and its v10 status)

Base: v9, sha256 `4bc0272c0c7b586a7e161b82318b7ae4a0b732067081e3a4073ea1dd3d22b53b`, 562201 bytes, 134 units by §0.1's
rule. v9 line/bytes/sha256 are from v9's §18.5 (verified by the v9 reviewer). **Status:** CARRIED (v9 unit unchanged;
authoritative bytes are v9's); AMENDED (v9 unit carried by sha256 with the exact edits in Part V10-A; composed v10
bytes produced by the OPEN composition, W1-V10-FORM); COMPOSED (full v10 text in Part V10-R, with its own v10 sha256);
NEW (no v9 counterpart; full v10 text, with its own v10 sha256). For COMPOSED and NEW units the v10 line range, byte
count and sha256 are computed by a read-only script over this file (Appendix I); they are filled in §18.5-R below after
the file is assembled. For CARRIED and AMENDED units the authoritative identity is the v9 identity in this table.

| v9 unit | v9 lines | v9 bytes | v9 sha256 | v10 status |
|---|---|---|---|---|
| title | 1-55 | 4912 | `1f2d0a2e955f43bcfcae97b3addf521b098f980ca79cd84f37f80accc78820e5` | COMPOSED (R) |
| 0 | 56-57 | 52 | `80267ea40473bab37f029b4b9573c239125e131fd185982839b93f108a0d16cd` | COMPOSED (R: "from v8"→"from v9") |
| 0.1 | 58-74 | 1250 | `e34b3bbee3ea4744f2d2de21492b84c2a425c797bdbb29189ce5e7ecbbb235fb` | SUPERSEDED by §V10-0.1 (NEW) |
| 0.2 | 75-98 | 2266 | `2986013a0b6f35c6d88d74e8e6c50b20c0ad4c9aebe7edff78fd0756ea2691c4` | CARRIED |
| 0.3 | 99-118 | 1834 | `a8722812979b2fe89b67dd0f0903d64f8bba384311c1f3a57b1ecdb89aa70d35` | CARRIED |
| 0.4 | 119-141 | 1944 | `125e4c53d7b2747d0d17865a22f2d84a3fe9d4952d2c4e1bf75b74624b347c0a` | CARRIED |
| 0.5 | 142-153 | 1083 | `ed814dad3e6cac843dd7f488a74900cc8de8b8dd8f6b83322dc7ed81403e8054` | CARRIED |
| 0.6 | 154-161 | 547 | `fc36e0f7e099a40aa73199c89e9a5d0f1816203392dcf11b5541c28f664e0e08` | CARRIED |
| 1 | 162-203 | 3156 | `2ae9da8b3dc5177eb189805c8f7fdc48e4908a2204fb68a6b4be0b5118aa0dac` | CARRIED |
| 2 | 204-205 | 63 | `35f6eb75cbc9b074ead5488fca9693875386deb826fbd0374020398a83887683` | CARRIED |
| 2.1 | 206-232 | 2658 | `62cb14bcb695c40049aa8b23195b0242a1a145576a18ebe88e45093b377e7d91` | CARRIED |
| 2.2 | 233-244 | 1073 | `f954d0a34a6d4eb0952d04b74d966e115ece877ea302dcba7cda7df19b569c2c` | AMENDED (A) |
| 2.3 | 245-274 | 2982 | `698fa0836f497267eae07b89aeecfba6d8cfc56f8d33054ad860b79d937d2210` | AMENDED (A) |
| 2.4 | 275-300 | 2356 | `076cf02493e497a50951aeefad90ebdb31354f810d176a088b96cf861f790276` | CARRIED |
| 3 | 301-302 | 39 | `5510e891fd324593657d164471cb63078bbc71af4f71c2da3fc35163ae8c2ed0` | CARRIED |
| 3.1 | 303-315 | 1099 | `37ca5ff4babc986bc4343989256bc66bb67426a9087763eb22cb9868addbb8aa` | CARRIED |
| 3.2 | 316-339 | 2989 | `7dc9ea13d4cffc14bd9e56c1c312dc8167f92faae117c4ac9a3ef2451aa6c47f` | CARRIED |
| 3.3 | 340-391 | 4416 | `8134e140129264e3b3ff24284829f410cfb16f21f2a4500394ea722718cb426c` | CARRIED |
| 3.4 | 392-462 | 6805 | `ff14802bd61c0964c53306a5455e0ecff05b6acb3bf492246942ea39171a9748` | CARRIED |
| 4 | 463-464 | 106 | `030cba113f70fd51a55fba2cdbacef1d4bebdd0fa2b0813f0a7f935356beaa45` | CARRIED |
| 4.1 | 465-505 | 3972 | `32381257ff4beca2691c3205f0c564b871539e093efff642c3b8351f7cd4b1ed` | CARRIED |
| 4.2 | 506-667 | 15178 | `28116cedfbb901f9a161eba4427e4aa1e8603aa961e991aab7b7e05c09dd246d` | AMENDED (A: AD4, D7) |
| 4.3 | 668-740 | 7157 | `5a924fb6ac8d8f39071a809c5c4befd2d0c43c0d6e324bd63c79612171798918` | CARRIED |
| 4.4 | 741-766 | 2451 | `eb572f6edb96f31e7bf59a9d8176ed06a37de4f96282533d86a1d70d7d31a59c` | CARRIED |
| 4.5 | 767-819 | 4784 | `de91424f7f367655a5ffa26ebaed048bf781978281c45d1ee1e364a3ef9d5de5` | CARRIED |
| 4.6 | 820-884 | 5877 | `00b3ed65328eb21773f171bf89852ac17c227e4c242c254aa4e2bc5c739eb234` | AMENDED (A) |
| 5 | 885-886 | 137 | `46adbb0dd725d4f1ca5f142a684061fafc17e2c5165b6da45647a41585de9bab` | CARRIED |
| 5.1 | 887-914 | 2284 | `e0bc923e20b24b36609ff4d44f5a354e999dcd57c67793c398d1890d68c14b97` | CARRIED |
| 5.2 | 915-947 | 3910 | `3f5976199bc5eb57fbd117bcb4bd98e4d530c17e14dd5638145b65501590b76b` | CARRIED |
| 5.3 | 948-971 | 4545 | `afba96af1fe021ef8a8705a4bfcf785481182ae4698070d3a361169694e4a647` | AMENDED (A) |
| 5.4 | 972-978 | 478 | `debd77ac854c1a74be9913a849254ef55cff1e9f0adc2553f42431b3167eee6a` | CARRIED |
| 6 | 979-980 | 144 | `6a852dcafc48edb984b90136498474c97f6f0348b8e6541fe33b803af9034fd3` | CARRIED |
| 6.1 | 981-1001 | 1821 | `3d18ff6cf3be2307f6980717d1796fd4963eed1bddb4d51232ac59c328d2d608` | AMENDED (A) |
| 6.2 | 1002-1018 | 1442 | `155a6ef1dfdbbf811f6bd5f0a35f3134e8e60f171ee273535f4b227a30e760c2` | CARRIED |
| 6.3 | 1019-1056 | 4302 | `995566ec7d4ddeee26abcf3c43ec78d72f7d17efe46d9228b9ee2790f474709c` | CARRIED |
| 6.4 | 1057-1073 | 1468 | `30a2971341b7817ab2ebed17553a1e51152729aa025201f4027d1b4f0cbfd4a3` | CARRIED |
| 6.5 | 1074-1099 | 2640 | `7f63c223dc48968db1840b0c03fc711097648093ecbbfc7d5ed248d1578e2b8b` | CARRIED |
| 7 | 1100-1101 | 113 | `8ab0b34614a172ffb23cde8314d7bef25492c58858feabd1d30e543cde17fbae` | CARRIED |
| 7.1 | 1102-1119 | 2380 | `f3956fa90333b2462b6dc6ca3996d581f2365859a7527438b267176b79d6b895` | CARRIED |
| 7.2 | 1120-1142 | 2191 | `7faec7003ad60f3723bd527d117099d1c40615466ed7acd274903c19a54d8047` | CARRIED |
| 7.3 | 1143-1176 | 3468 | `eeaeab07f27381c5af35893f610b81e421bd7ca96e7568d96540ced5164e5e2e` | CARRIED |
| 7.4 | 1177-1191 | 1237 | `a345f95d51ea80e4e381b4301095d46f94cef1b8b5235322c52800b5a404f8bb` | CARRIED |
| 7.5 | 1192-1207 | 2318 | `58b24a0d5a3462b2659cb856abf0558bf42183193c745d16bdba67a72037114a` | CARRIED |
| 7.6 | 1208-1217 | 826 | `da3dc6642e8c8b1bf407a522e929faa1997c00c2b74738d67783089debc1b34a` | CARRIED |
| 7.7 | 1218-1242 | 2379 | `8885f573d2d0fbdd54b85fa094eec6c601477ae7908bac413fe05274e29795cc` | CARRIED |
| 8 | 1243-1244 | 121 | `5dc90f8d992d37f789b9fdc38f5cef1248a2bb2ae0c5322ab39442c58024bc66` | CARRIED |
| 8.1 | 1245-1271 | 3403 | `818cd88571e5eeb889a08aae3a267c1a63abc20b07948478d6a608361fd31c91` | AMENDED (A) |
| 8.2 | 1272-1283 | 1030 | `309b19cccb33bc3a0a2d9863e13e869de1e42a9ae055ede4b84a47ec7fde5705` | CARRIED |
| 8.3 | 1284-1329 | 5061 | `ac234959421ccdd77c8be3ce605c43d1e6967450793033d765e31a0d5918b98f` | CARRIED |
| 8.4 | 1330-1363 | 2819 | `897375821817ed762c6b5cf287e32d44e0f8ea439afbb714c153c60f5116cf58` | CARRIED |
| 8.5 | 1364-1399 | 4369 | `2980b640ea948fef9793bf3f21123cdbf3f9fd28313ebd0aeac4be67b3105653` | CARRIED |
| 8.6 | 1400-1421 | 2023 | `3ec9d7f237addb503a8f3a90434741ae57e7386139ae3ab5b5a06271ae25dd1f` | AMENDED (A) |
| 9 | 1422-1423 | 189 | `d1843b7e7e7bee1fec119a7314ce98958f5e46327d872070510c73a6b1c90a01` | CARRIED |
| 9.1 | 1424-1449 | 2226 | `bb6878ba3ff06de0beee08216c93ad10d2e4d4e483b8fdab0c693cb757e15502` | AMENDED (A) |
| 9.2 | 1450-1467 | 1714 | `6c4a383502ee74cabb5b597ae8220ba1d86122fa6d12400adfb30845910dc11f` | CARRIED |
| 9.3 | 1468-1619 | 16042 | `17a191ab2b3e38f1edc2808573e60375be8195f0b567f36ce2df5a4be962624a` | AMENDED (A: G4/C1 fd set) |
| 9.4 | 1620-1717 | 9225 | `ef7160cdca5dff8e1c4a85559a76603e21275f6337b6381050aa3d68917e9c6d` | CARRIED |
| 9.5 | 1718-1761 | 8966 | `fe247395518af3df20cefd0609def440f77429f1e69e08335e6a67eb79491586` | CARRIED |
| 9.6 | 1762-1786 | 2396 | `c98574eebfb51d6313ef4ac6dfeadb9b6c276a7cfb2fd44596744bba7207ba84` | CARRIED |
| 9.7 | 1787-1834 | 4489 | `dc6b60071dc98380aa87d184fd7ac3b8904c1800991e561804a7083d4a4c2983` | CARRIED |
| 9.8 | 1835-2085 | 29524 | `9d84e8e6f9f01c833468290b639c6804994cce69b9ff9b0fed542baafd5c84d5` | AMENDED (A) |
| 10 | 2086-2087 | 173 | `b923c50c51930667776aced4d6d5b16a080102e4e056e61d0ade2fd420c1d98d` | CARRIED |
| 10.1 | 2088-2125 | 3416 | `22ae43ed8d8e6266e387df30cb572b6148a9934242deb6a3ef6db7b65a2dde02` | CARRIED |
| 10.2 | 2126-2239 | 11746 | `ecb48668e7ca7ad2348fbff5af741a954c6b25a73f5635b42c7ef9076acdd435` | CARRIED |
| 10.3 | 2240-2245 | 369 | `2b275b998e8c39b306421b0c6400ea8c12528d2b9741410c51f99ac4bca59990` | CARRIED |
| 10.4 | 2246-2289 | 4467 | `45c96fa1f94741a0a04242424778df566daa7cd7914d7c8ff2cc04be34e7d85f` | CARRIED |
| 10.5 | 2290-2326 | 3427 | `88f1ca6288ee6dbb64ac667c945e450260a3b1250371efd3a35513e66abe89a9` | CARRIED |
| 10.6 | 2327-2360 | 4254 | `e922ecf42fcaeb673d72fa459602d9de4b103216c447ab1e4c9cc4ae3bd1b071` | AMENDED (A) |
| 10.7 | 2361-2400 | 4099 | `9cdcd4ca80399bb8b09faff5404b7acaed06a81f8c1c79318797212a30a08826` | CARRIED |
| 11 | 2401-2402 | 127 | `554fcbe4c216f90ff9d4ae0b8672903c7d18685221dc80a7ec07dbc59d5df8cd` | CARRIED |
| 11.1 | 2403-2422 | 1723 | `0ad981bd44c1a4c63a85f56e89f7983c354e19b1eea1b5ab56eec3357a73463e` | CARRIED |
| 11.2 | 2423-2436 | 1173 | `64562978ae2d418c938f8705884948c597351891964557787afcc6ba66fed3da` | CARRIED |
| 11.3 | 2437-2486 | 8088 | `88d54fa1f3dd5c7273297996b0bd0318421b84767a802f3538f80f7c7da033d6` | AMENDED (A: P12/P13) |
| 11.4 | 2487-2638 | 14925 | `165128c67ddb943e055d82157760cd177c45aeadfc38ca30b694a10b97db6182` | AMENDED (A) |
| 11.5 | 2639-3033 | 22381 | `c809520b94062d6fa33b561af2f2c02ac37ec156a9162cc4c3cdd0d91fb46ff8` | AMENDED (A) |
| 11.6 | 3034-3047 | 1118 | `d0f19a4c6ca8991a4ff06e94687723a8b967797778fac7c277ce3ae30907c8f2` | AMENDED (A) |
| 11.7 | 3048-3100 | 6915 | `610b5ea29a17f2da23d66da5a3e4bebdc5bed2c425046ee4e055b398dd397333` | CARRIED |
| 12 | 3101-3102 | 202 | `b60fea083ed7bef57ec1a8638c5bcdaeb9875f3b247ed1853060446f6a013935` | CARRIED |
| 12.1 | 3103-3110 | 508 | `c9c23c0260e6bbd67676b1725419425239b37769d2081a5e66e793e07bcfa9d1` | CARRIED |
| 12.2 | 3111-3223 | 10920 | `43a1796a7072f0301c9e5e03abb4defd601da4fddcf6d279d1cbd8b1f46ad7c6` | AMENDED (A: step 12) |
| 12.3 | 3224-3245 | 4171 | `b9392577ca84a9c6741e0a0113036b34307d3c2029966cf67e5d0540751ea014` | AMENDED (A: V15-V17) |
| 13 | 3246-3368 | 15503 | `59661d221f58572e506e70aedfdeb1fb34c5b21fb4d8f1a9a48653a56913cd04` | COMPOSED (R: rewritten) |
| 13.1 | 3369-3395 | 8151 | `597c6887c79dd4c24794ae248c1ddd560eec940f25278170a6e61b9af87ef387` | COMPOSED (R: rewritten) |
| 13.2 | 3396-3460 | 15623 | `722c476e0e6f94ce635e6792f6f64746aabe8be5cbb1216f779c963dc89c450a` | COMPOSED (R: rewritten) |
| 14 | 3461-3471 | 955 | `00a709ad5f406f810c5a993c63c2516e27b876053ffc7b070e74bdd503d5e06a` | CARRIED |
| 14.1 | 3472-3479 | 552 | `74064f167fa18ca4c37b49cef1070d1902ab55bf3201fcca04aac6be3a9c59f9` | CARRIED |
| 14.2 | 3480-3498 | 3098 | `2d1d3c6cd2a9786ab739b7dfa7f802ecabff525141eee66539f20eb777f600c7` | CARRIED |
| 14.3 | 3499-3521 | 2259 | `b3e074d76f438d2e0c270eea40ff16b326ec917c6ec852d25f9c02a8ce55baa4` | CARRIED |
| 14.4 | 3522-3534 | 739 | `e9387e358eaffbf6a7244c1a7c9e15c237cfce7b2d5a39cd2e05a71af4860f1b` | CARRIED |
| 14.5 | 3535-3593 | 5582 | `0f88ce97455fdced4ca5111cdcbb6d4ab306cb0f3775221a8237520f371a51a1` | CARRIED |
| 14.6 | 3594-3602 | 635 | `41c190d586646edc31cdee4609544d067a3a7a3586a9c725a620daccca10f8ed` | CARRIED |
| 14.7 | 3603-3618 | 1391 | `bd990a9b3c3e6b09845754ee99a2ae58cfd0199a46bb5b5b1c0aef0ffa2723a7` | CARRIED |
| 15 | 3619-3620 | 139 | `c28ab08b1a6cf57c5c65775871754ab7312225c4fb76ff455a1da064d04a35d0` | CARRIED |
| 15.1 | 3621-3645 | 4358 | `132ed3166570227fad818e570035aba1c7cf0d5c033471c28c114989a5ffee4d` | CARRIED |
| 15.2 | 3646-3652 | 429 | `89e6432791fdcfd0fb53c905eaf9bea0fd8fe81b4ff1f212c3cc10fb0a1250c9` | CARRIED |
| 15.3 | 3653-3744 | 8904 | `c63a0485c9548f73a653b7f7acc2999d27133288b5b3e353f70979982a1e8ee7` | AMENDED (A) |
| 15.4 | 3745-3761 | 1563 | `feec26c34e5d6bf58ff90bbae7b31979ac154a0a0c802a0395f15cee98a9f557` | CARRIED |
| 16 | 3762-3795 | 3158 | `1592969c78f6aaf42bf5af4ca29bdbda4dedcb17f74f8cf5b7eb57d206b097b3` | COMPOSED (R) |
| 16.1 | 3796-3809 | 2761 | `b17c49541c24d07b1e6aa970861b3cd5c0a5aa4ffee2378435b3c9fc1c073a28` | COMPOSED (R) |
| 17 | 3810-3839 | 5809 | `2c819d7d7a8025b4844b931432a0686efa666c1c8d1ac9c97b7440b69e2c39f4` | AMENDED (A) |
| 18 | 3840-3847 | 653 | `e92c04dede085626f123091986be4884fc74d60a2819e97e584daea9411eac00` | CARRIED |
| 18.1 | 3848-3899 | 5023 | `43d110e60d6ed26bc65fdaf89b7ab88198c944ed7e0b427a00fc2992435c5e10` | CARRIED (the v8 review's changes; v9 review's are §V10-0.7) |
| 18.2 | 3900-3915 | 1517 | `6f0835c8d587e8ec3361fb94606cb20dd98c1a9ee79af748a4900ff7893f5771` | CARRIED |
| 18.3 | 3916-3922 | 463 | `234ad3759214ab92b3e76c373cb9e0d11ae01d1bee9f4f0ae001c14a1a6af099` | CARRIED |
| 18.4 | 3923-3934 | 841 | `d36420f06d07ec16061137f3fe68d0fd10fc664287d54a9126606bc42e303f90` | CARRIED |
| 18.5 | 3935-4086 | — | (v9's own map) | SUPERSEDED by this §18.5 |
| 18.6 | 4087-4095 | 785 | `ba1db167e50f1026298c1841bf3c269c5f6b11ff906443a14a549aed72ca715e` | CARRIED (its new-element pointers extend to §V10-0.7 and §23) |
| 19 | 4096-4104 | 744 | `fb08e68e1409c1040975b20fcee3cc498a93566cdf33531ea01ad8d87f4221ec` | CARRIED |
| 20 | 4105-4126 | 1815 | `350d52edb55a8aaad58322e7a1897ffcbb2048aef20bdc1aac695ca656aef78d` | COMPOSED (R) |
| 21 | 4127-4128 | 179 | `d7c0a6d1ec091464b5328e651ac42c7c1b51caa47cb511f2ed2032ab62cc669a` | CARRIED |
| 21.1 | 4129-4160 | 2779 | `99ddb6ca43802e3d762978ee5017ff5206ad9641ee29b06c248e17197e5e7269` | CARRIED |
| 21.2 | 4161-4167 | 614 | `8d89026d3ccffcd9a5f769c10389dc18adfe391d1c61c3de492d78e040b932c1` | CARRIED |
| 21.3 | 4168-4186 | 3054 | `c88585c55cf0cd068baa975b96f7619bcc61f005e51a4381affc87d1ddfd305e` | AMENDED (A: V15-V17) |
| 21.4 | 4187-4198 | 1648 | `02071661f88bfbc66710aa02e7a4046e020b22dfd8eba3b3010323ae4c24c911` | CARRIED |
| 21.5 | 4199-4209 | 1344 | `a474c25556f0c4ddb261eb5cbb9c11fe337db64d13dfafc6d1095e71d75e1e16` | CARRIED |
| 21.6 | 4210-4218 | 701 | `e5abdf4693c889e748acf2847cdc71284026e09ee068af6561c31df182f66615` | CARRIED |
| 22 | 4219-4220 | 123 | `b54545344d2fa2a11b5eb45e57b506b71db7804be049af649f17c3c500268df0` | CARRIED |
| 22.1 | 4221-4227 | 447 | `2b1b5b5b560192d039e64e0bfba3e6f7bb0f4a821b43ffdc176e3880836002fb` | CARRIED |
| 22.2 | 4228-4236 | 829 | `4b3bc48c8f9987d6b8f27783d5bc73cd86d6fd0b649018137ae2f358364aadf6` | CARRIED |
| 22.3 | 4237-4293 | 7037 | `f0e3f291a1ae70b759aeccb5c6f4c71729ce8b9da0a2dc9049420fcdb5855c4d` | CARRIED |
| 22.4 | 4294-4305 | 978 | `480e422524317a9cf0037fbacdb1c817077ab0b82e2f4262addd2b2ff9b0c438` | CARRIED |
| App. A | 4306-4369 | 14868 | `1211f48a394f8dd03602066280d11ec7ee0089976919ad7028fa422a3556b9a0` | CARRIED |
| App. B | 4370-4378 | 676 | `eef7ebf9b21f869d21e2f3fe24a6052fd5fa503a50145afd3a1676bffaa30fc7` | CARRIED |
| B.1 | 4379-4394 | 1483 | `95c9bb599940e2e67647c21baac4e57bb6c59d181fc24dcab85e3e41fd549abe` | CARRIED (defines `-v2`; §8.1 body now matches) |
| B.2 | 4395-4419 | 2456 | `2c2a322a54675cf10ff5245169b20cab8ff83be262bdd1b220baec43e0f08bb5` | CARRIED (defines `scope-v3`/`census-v2`; §9.1 body now matches) |
| B.3 | 4420-4468 | 13602 | `d5d6f30ee183ad65fa9cfb379b627511d632aec8174bc24499e0ab9f621c8b6c` | AMENDED (A: `-v2`, provenance keys) |
| B.4 | 4469-4701 | 29645 | `58d7d91044c698fb9251dc82a0e38e75f29baebd6f9ae85d3c5cf149c6edaf26` | CARRIED |
| App. C | 4702-4761 | 4399 | `e21904702b855c69feb1afe86117e9088684c70162571459c5b906ea2b9a79c5` | CARRIED |
| App. D | 4762-4819 | 8434 | `f00e0b1b9c786fddced73bf368ddd416d57d13b6afcf5d78fad73dd86415e3a1` | AMENDED (A: J5/A3/A6) |
| App. E | 4820-4883 | 5709 | `f7d449206492465183052962b4a8ea13d20a28202ac41069c31a283e1d2b06f1` | CARRIED |
| App. F | 4884-4928 | 3963 | `4b6f95f0f14f03859e6c6e08222fd51c35a0fc46365a1bf35c31d4d3fb409cc1` | CARRIED |
| App. G | 4929-5036 | 10289 | `56ff67770137755792dea29437261ae2a148e41b3f2cbb437f29d942f99df9b1` | CARRIED |
| App. H | 5037-5090 | 4593 | `dd7b25abacb71a46a9c81f6399db2e7f7f7c3047348f36bf364202958406a20a` | CARRIED |
| App. I | 5091-5143 | 4420 | `afdb7864df65b89c9b21b411a9263de11b59ab9af9ba28c236aa0feb2aa986fa` | COMPOSED (R: Appendix I replaced for v10) |

**NEW v10 units** (no v9 counterpart): §V10-0.1, §V10-0.7, §23. Their v10 identities are in §18.5-R.

### 18.5-R Computed v10 identities of the COMPOSED and NEW units

Computed by a read-only script over this file (Appendix I records the run). Each row gives the physical v10 heading,
the status, and the v10 line range, byte count and sha256 of the composed/new unit's bytes (by §0.1's rule).

| v9 unit (v10 role) | status | v10 heading | v10 lines | v10 bytes | v10 sha256 |
|---|---|---|---|---|---|
| title | COMPOSED | `# Isolation … W-1, v10 …` | 1-71 | 6651 | `ab0496b948a1ef2d37461d85fc6c44a9d0067a5c830d2912922c1f1ccb43d6ec` |
| 0 | COMPOSED | `## 0. Reading guide, form and what changed from v9` | 72-73 | 52 | `6e1fd6a108ee4d6a497569c852da181f58f9e65bc38a0fcc8f1f0674ad4693ec` |
| (new) §V10-0.1 | NEW | `### V10-0.1 Form …` | 74-97 | 1887 | `b0277d0565e04c2738f48e513f312aa12c5a61786fc40e3cb3906797ab503e4a` |
| (new) §V10-0.7 | NEW | `### V10-0.7 What v10 changes …` | 98-193 | 9248 | `eb795b24436f6a4fcae835f67218af037751398771f45b04221aa97dcc6a52b2` |
| 13 | COMPOSED | `## 13. Probe specification …` | 203-258 | 5596 | `1dab407ff5beef49e5162d3263a0a68feb46183b6b8bb4c8d905b2e22d75570b` |
| 13.1 | COMPOSED | `## 13.1 Probe set as obligations …` | 259-280 | 5704 | `ba84454a84746f7b8acd1772335176c3c3d0ccd9f5ba0171560a19b7d475d1c6` |
| 13.2 | COMPOSED | `## 13.2 The probe-and-evidence plan …` | 281-348 | 9779 | `55046813f122a145c66c4e4e5c0ea466bbcf4471e1d0a97fb273da924a40a353` |
| 16.1 | COMPOSED | `### 16.1 The operator package …` | 349-367 | 3881 | `ea8283a12b1bd2b47c3d1eb8cc7b33e7c5ec384e4bcbd6faac6400f4522ba237` |
| 16 | COMPOSED | `## 16. Setup, verification and adoption order` | 368-412 | 4135 | `b81f8673e563d44205721fce22d4e0dd752ae27e17d93609d4a82ca28f887ef2` |
| 20 | COMPOSED | `## 20. Non-claims` | 413-441 | 2776 | `9e4b6fe48866179f3a9fe0e6e6ac676973ae033de7cfafc0b1d47093a69c2582` |
| (new) §23 | NEW | `## 23. Review provenance …` | 442-539 | 8403 | `98883301a22a964bee77897a745292e360e21c27513278305dd2287686540ec6` |
| 18.5 (new map) | COMPOSED | `### 18.5 Change map …` | 875-1023 | 15746 | `f3297aeadcf15bb9aefbc0fc60b7958ee1c418ddc0a52f472c199a90af3ece8b` |

Line ranges and byte counts are over this file as assembled, by §0.1's rule, from the read-only script (Appendix I).
Three composed/new units **cannot contain their own post-fill identity** (as v9's §18.5 could not contain its own):
this §18.5-R, V10-C.2 below, and **Appendix I**, because filling §18.5-R and V10-C.2 shifts Appendix I and alters
these two units' own bytes. Their final identities, computed over the fully assembled file by the same read-only
script, are recorded in `v10-support/jackal.json` (`v10_unit_identities`), together with the whole-file sha256. Every
CARRIED and AMENDED unit's authoritative identity is its v9 identity in the §18.5 table above; its composed v10 bytes
are produced by the OPEN composition (W1-V10-FORM).

### V10-C.2 Counts (JACKAL exact; Appendix I)

Of v9's **134** units (v9 §18.5): **101** CARRIED, **22** AMENDED, **9** COMPOSED, **2** SUPERSEDED (§0.1 by the new
§V10-0.1; v9's §18.5 by this §18.5). `101+22+9+2` = **134** (JACKAL exact, Appendix I I4′), so every v9 unit is
accounted for and none is WITHDRAWN. v10 changes `22+9` = **31** v9 units (JACKAL exact, I5′) and adds **3** NEW spec
units (§V10-0.1, §V10-0.7, §23). v10 answers the **9** v9-review required changes (I3′ = 9, §V10-0.7) and keeps the
3 execution-bound carried changes. The document-structure headings (the `# Part V10-R/A/C` headers, the `## A-§…`
amendment-block headers, this §18.5-R and §V10-C.1/§V10-C.2) are scaffolding, not spec units, and carry no v9 unit.

## Appendix I. v10's JACKAL results and inputs (replaces v9's Appendix I for v10)

**JACKAL.** Every derived numeral of v10 was computed with actual MCP `jackal_exact` on 2026-10-05, sequentially or in
groups of at most four; each returned status `exact`, `formal` false, lane `rat`, assurance "exact rational arithmetic
(not yet checker-covered)", and the non_claims "NOT formal-bounded: this lane carries no Lean-checked certificate",
"The epistemic class above is the STRONGEST claim this result supports", "exact rational arithmetic (not yet
checker-covered)"; no consequence-ceiling field was returned (informational arithmetic only; exact is not
formal-bounded). The complete records are in `v10-support/jackal.json`. Numbers v10 carries unchanged from v9 (the v9
reachable-set and unit arithmetic that v10 does not change, the identity-map line, the `app.slice` limits, A_capture,
the Required) are carried with their v9/v8 records.

| Id | parsed (the tool's echo; grouping parentheses are flattened) | exact | Used in |
|---|---|---|---|
| I1′ | `4+5+3+2+2+1+1+1+1+7+10+4+6+3+3+4+0+0+2+1+1+1+1+1+1+1+1` | 67 | §11.4 (A-§11.4), reachable set without images (W1-V9-ENUM-USERDEL) |
| I1″ | `63+4` | 67 | §11.4, cross-check (v9's 63 plus X1,X2,X3,X4=W_B) |
| I2′ | `4+5+3+2+2+1+1+1-2+13+1+7+10+4+6+3+3-4+26+4+0+0+2+1+1+4+1+1+1+1+1+1` | 104 | §11.4, reachable set with images |
| I2″ | `100+4` | 104 | §11.4, cross-check with images |
| I3′ | `1+1+1+1+1+1+1+1+1` | 9 | §V10-0.7, the nine v9-review required changes |
| I4′ | `101+22+9+2` | 134 | §18.5, status partition of v9's 134 units (CARRIED+AMENDED+COMPOSED+SUPERSEDED) |
| I5′ | `22+9` | 31 | §18.5, v9 units v10 changes (AMENDED + COMPOSED) |

**Inputs read for v10** (read-only; 2026-10-05): the sealed v9 review `wt-1/proposal/v9-review/claude-v1` (`REVIEW.md`
and `review.json` in full; `checks.json` and `review-freeze.json` as the sealed freeze records them); `v9` and the
units it reproduces (for the §18.5 identities); `STATUS.md` (D-LEAD-REVIEW-PROVENANCE ~19:05Z; the human direction
~17:05Z); `…/outputs/claude-phase1-handoff-20261004/HANDOFF.md:173` and `…/outputs/complete-phase1-prompt.txt:60`
(§23). v10 did **not** re-fetch kernel, systemd or sudo source: where it relies on installed-build or upstream
readings it relies on v9's dated observations (v9 Appendix I) under premise P-KSRC, and §13.2 S-1 binds the running
kernel image and build-id to the package before any installed use. **Nothing was executed for v10 but reading,
hashing (the read-only §18.5 identity script) and JACKAL calls; no probe, selftest, namespace, mount, seccomp filter,
sudo, setup, vault or window action was performed.** The §18.5-R identities and the §18.5 byte counts are observations
of this file produced by the read-only script, not derived arithmetic.

**Dated passive observations.** v10 adds no new installed-build or upstream observations of its own; the observations
on which the design relies are v9's (v9 Appendix I, 2026-10-05), carried under P-KSRC. The §5.4 subordinate-id
inventory, the §2.3 kernel settings and the §11.4 recipe-mode facts are v9's observations, unchanged.






