# Isolation and storage proposal W-1, v11: a self-contained same-identity view with the enumerated asynchronous-write obligation, a namespace owner no principal resolves to, the complete user-deletion state table, the staged probe plan with operator-reserved boundary exercises, and the stated review-provenance join change (specification)

**Status.** Drafting author's design specification, written 2026-10-05 UTC for the Claude Code lead. It is a
CANDIDATE specification of the protected-writer confinement design for the scratch proof frame, and the successor to
v10. It answers the sealed independent review of v10, `wt-1/proposal/v10-review/claude-v1` (verdict **NOT_ENDORSED**,
sealed by `review-freeze.json`; the review's `report_sha256` is
`81419b7a6a830b78d6232412dfe686b9bb8ca9706f120a0caa1e1bd2fa515833`, sealed from reviewer agent id
`aae3a07f9c8701b8e` with task-output sha256 `91f6cf7d577f30cce3a8caa54dabc1d764c1d7d19611003f4467bc3d3f6a60b8`).
That review found eight of the nine W1-V9 required changes CLOSED_AT_SPEC_LEVEL, the ninth (review provenance,
§23) correctly stated as an unreviewed change with adoption blocked, and three bookkeeping/form defects to fix:
**W1-V10-COUNT**, **W1-V10-FORM** and the **W1-V9-REVIEW-PROVENANCE source-path residual**. v11 fixes exactly those
three and makes the document **self-contained**, changing nothing else that v10 closed.

- Nothing in it is implemented, installed, approved, executed or reviewed. No account, group, ACL, sudo rule,
  installation, scope, mount, namespace, Landlock domain, seccomp filter, probe, selftest, vault, adoption or window
  action has been performed for v11.
- Proof dispatch stays blocked by the confinement criteria (V5-B01, V5-B02, both OPEN) and by the capacity gate
  (Gate 0, NOT ESTABLISHED). **V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION and W1-V7-HOLDER-STATE stay
  OPEN and are not narrowed.** v11 closes no obligation by itself. Every original Phase One obligation (the 219 entries
  of `OBLIGATIONS-v2.json`, sha256 `1587e068fc2c31a562e38b459728a75dbf7e8d7d9f8afb8efa1474e2a702aeec`) stays OPEN with
  its original owner, release and dependencies.
- **Critical premises** (a refuted one stops every installed use until the redesign is reviewed; §9.8 N7):
  **P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP, P-ASYNC**. (W1-V9-FORM-CONSISTENCY: this list names P-SECCOMP, matching
  N7 and §9.8 N4.)
- v1–v8 are preserved as v9 states them; v9 (`ISOLATION-STORAGE-PROPOSAL-v9.md`, sha256
  `4bc0272c0c7b586a7e161b82318b7ae4a0b732067081e3a4073ea1dd3d22b53b`, 562201 bytes, 5143 lines, with
  `v9-support/jackal.json` sha256 `2d225e26780c95035f2ef57d79cc1a1758304fb82f08c4a75adab254d2b02270`) is the base of
  the §18.5 change map; v10 (`ISOLATION-STORAGE-PROPOSAL-v10.md`, sha256
  `d5fe8f3152dd8782adeee65478d7f70fb06e5fac50f0b17943d53598da66d8ef`) is the change document v11 self-contains.

**Form of v11 (W1-V10-FORM resolved).** v11 is a **single self-contained specification**: every unit's bytes are
present in this file, and §18.5 records every unit's own computed v11 sha256 (the change-document / amendment-block
form of v10, which regressed W1-V8-FORM-SUBUNIT, is withdrawn). §V11-0.1 states how each unit's bytes were obtained
(verbatim from v9 for CARRIED units, from v9 plus a stated normalization rule for AMENDED units, from v10 for
COMPOSED units), so the composed bytes of the formerly-AMENDED units are now materialized and hashable. No obligation,
fixture, control, threshold, accepted case, criterion, allowance, cap, gate or join is weakened by self-containing the
document.

**Two sensitive areas, drafted by obligation only (unchanged from v10).** The detailed asynchronous-holder refutation
and the privilege-boundary probe procedures are **not** written here as step-by-step recipes. For the asynchronous
boundary (W1-V9-ASYNC-ENUM) this document states the closed specification, its enumeration basis and the state an
operator-run probe must observe, and marks the detailed procedure OPEN (operator-prepared package, §16.1 O-ASYNC,
stages E1/E2). For every privilege-boundary probe it gives only NAME, OBLIGATION, ENTRY RULE and DISCHARGE/REFUTE
PREDICATE, and defers every boundary-exercising or object-constructing procedure to the operator stages. The
asynchronous-holder containment and the boundary properties remain OPEN obligations, not asserted here.

**Inputs read for v11** (read-only): the sealed v10 review (`REVIEW.md` and `review.json` in full); v10 and v9 (for
the unit bytes and the §18.5 identities); `STATUS.md`; the original texts
`/home/sicarii/Documents/complete-phase1-prompt.txt:60` and
`.../outputs/claude-phase1-handoff-20261004/HANDOFF.md:173` (for §23). No kernel/systemd/sudo source was re-fetched;
where v11 relies on installed-build or upstream readings it relies on v9's dated observations (Appendix I) under
premise P-KSRC, and §13.2 S-1 binds the running kernel image and build-id to the package before any installed use.

**Non-claims, short form** (full list §20). No sufficiency is claimed. V5-B01, V5-B02, W1-V5-PRESERVATION,
W1-V6-READ-MUTATION, W1-V7-HOLDER-STATE, Gate 0 and every original Phase One obligation stay OPEN. Every premise of
§9.8 N7 is NAMED_UNESTABLISHED; a refuted premise requires redesign with no exception; a refuted critical premise
stops every installed use until the redesign is reviewed. The review-provenance join change of §23 is itself a change
to an original admission join and is **not reviewed**; adoption stays blocked until it is reviewed in the frame-design
revision.

---

## 0. Reading guide, form and what changed from v9 and v10

### 0.1 Form (self-contained; W1-V10-FORM resolved)

A *unit* is as in v9 §0.1: it begins at each line, outside fenced code blocks, that starts with `# `, `## ` or `### `,
and runs to the line before the next unit's first line (the last unit to end of file); its bytes are those lines with
their line terminators. The file ends with exactly one trailing newline after the last unit's last line.

v11 is **self-contained**: every unit's bytes are materialized in this file, in v9's section order, and §18.5 records
each unit's own v11 line range, byte count and sha256, computed by a read-only script over this file (Appendix I). How
each unit's bytes were obtained:
- **CARRIED** — the unit's bytes are v9's bytes for that unit, emitted verbatim (unchanged); §18.5 shows the v11
  sha256 equal to the v9 sha256, so byte-identity with v9 is checkable from the two files.
- **AMENDED** — the unit's bytes are v9's bytes with the v10 review-required edits applied under the **normalization
  rule** below; §18.5 shows the v11 sha256 (a new value) and names the v9 unit it derives from.
- **COMPOSED** — the unit's bytes are v10's composed bytes (the units v10 authored afresh: the title, §0, this §0.1,
  §0.7, §13, §13.1, §13.2, §16, §16.1, §20, §18.5 and Appendix I), carried into v11 and updated only for v11's own
  three fixes; §18.5 shows the v11 sha256.
- **NEW** — §0.7 and §23 have no v9 counterpart; §18.5 shows the v11 sha256.

**Normalization rule for AMENDED units** (so each edit composes to a unique byte sequence; W1-V10-FORM part (a)). An
amendment's quoted old-text anchor is matched against the v9 unit's exact bytes **after joining each hard-wrapped
logical line** — that is, the anchor is located in v9's text read as if soft-wrapped, so a quoted span that v9 breaks
across a newline (with v9's leading-space continuation) still matches. The replacement text is then emitted
**re-wrapped to v9's prevailing column (lines ≤ 118 bytes, breaking at spaces), preserving v9's indentation, list
markers, inline-code backticks and the single `\n` terminator per line**; an "append" inserts its text immediately
after the anchor with v9's paragraph spacing (one blank line between paragraphs); an "insert rows" adds the rows as
table lines in v9's `| … |` format, immediately before the paragraph that follows the table. Every other byte of the
unit is v9's, unchanged. Under this rule each AMENDED unit's composed bytes are uniquely determined, and §18.5 gives
their computed v11 sha256.

### 0.2 Author corrections of v8 (v8 itself is not edited)

1. **v8 §9.8 N4 on `io_uring`** said that "a task's `io_uring` requests are cancelled or completed before its exit
   proceeds". False as written. Upstream v7.2 `do_exit` calls `io_uring_files_cancel()`, which is
   `__io_uring_cancel(false)` (`include/linux/io_uring.h`); in `io_uring_cancel_generic(cancel_all=false, …)` the loop
   ends as soon as the *tracked* in-flight count is zero (`if (!tctx_inflight(tctx, !cancel_all)) break;`,
   `io_uring/cancel.c`), so an untracked request already issued (for example a direct-I/O write) is not waited for, and
   the ring's final teardown happens later. So, quite apart from the outside memory-context holder that v8 named, an
   `io_uring` write by a task of U could complete after `populated 0`. v9 removes the two asynchronous submission
   interfaces from every view (§12.2 step 13b; review W1-V8-HOLDER-IOEXIT).
2. **v8 made W the owner of every U8.** By the owner rule every process with euid W in the initial namespace held
   every capability over every U8, and A1 can start one (the S1 rule runs `writer.py` with A1's arguments). v8's N2 did
   not state this (review W1-V8-WRITER-AS-W). v9 makes the owner a dedicated identity, N, that no route confers on any
   process except RL's short-lived helper (§3.1, §5.3, §9.8 N2).
3. **v8's P-IOEXIT discharge kind "S"** overstated what a source reading could close for the outside-holder path. v9
   withdraws P-IOEXIT and replaces it by P-ASYNC (§9.8 N7), a statement about a closed list of write paths that a
   source reading can discharge.
4. **v8 §10.6 and §15.3** relied on H(U) for stream finality and the complete capture without separating what they
   observe from what they assume. v9 states, for each, the observation, the premise and a self-check (§10.6, §15.3).
5. **v8's form**: two units carried paragraph sub-ranges of v7 by line numbers under a whole-unit hash, and several
   amendments were rules to be merged by the reader. v9 is self-contained (§0.1).
6. **v8 §11.4** deferred the global state table to a concrete inventory. v9 gives the table, parameterised only by the
   frame's directory and member lists, which do not exist until the frame is frozen (§11.4).

### 0.3 What v9 changes, per required change (§18.1 gives each verbatim, with the author's assessment)

1. **W1-V8-HOLDER-IOEXIT** (§12.2 step 13b, §9.8 N4, §10.6, §15.3): the holder boundary is redesigned so that the
   path cannot exist: RL installs a seccomp filter that makes `io_setup` and `io_uring_setup` fail with `ENOSYS` in
   every view, so no task of a view can submit an asynchronous write; every remaining write path completes inside a
   task, before that task leaves its cgroup. H(U)'s absorbing property is argued over a closed list of write paths
   (P-ASYNC, source-dischargeable). The capture and stream finality add their own consistency checks.
2. **W1-V8-PRESERVATION-ESTABLISH** (§21, §13.2): every OPEN row has an exact discharge route (source comparison or
   run), with what discharges and what refutes it; the original control fixtures that can serve are named. No row is
   established in v9; the rows stay OPEN.
3. **W1-V8-PREMISE-DISCHARGE** (§9.8 N7, §13.2, §16.1): every premise has its executable discharge or refutation run
   on the installed 7.2.6-1-aarch64-ARCH host, in an order the lead can execute, P-KSRC first and P-NOSUID/P-NOCAP
   before any installed use; privileged steps are in the operator package.
4. **W1-V8-WRITER-AS-W** (§9.8 N2, §5.3, §3.1): the vector is stated, and removed by redesign (owner N).
5. **W1-V8-COMPOSED-ENUM** (§11.4, §11.5, §15.1): the global atom table and the reachable-state enumeration.
6. **W1-V8-EVIDENCE-EQUIV** (§8.5, §15.3, §13.2 V-BACKUP): the original backup consumers named, the equivalence
   predicate per consumer, its verification run; the capture's dependence on H(U) reduced to P-ASYNC plus a
   self-check; safe fresh capacity stays OPEN as the original obligation it is.
7. **W1-V8-FORM-SUBUNIT** (§0.1): self-contained.

### 0.4 The architecture decision, stated plainly

**v9 keeps the same-identity view (SIV)** of v8 (§12.2), with three changes: the view's user namespace U8 is owned
by a dedicated identity N (`wlscratch-ns`) instead of W; RL adds a seccomp filter that makes `io_setup` and
`io_uring_setup` return `ENOSYS`; and the specification is self-contained. Everything else of v8's SIV stands: the
target runs with the lead's host credentials inside U8 (identity maps), in a kernel copy of the host mount namespace
(all mounts kept, `nosuid`, private propagation) with g/source bound at the run path and g/tmpdir at `TMPDIR`, a
private network namespace, a Landlock domain handling only `RESOLVE_UNIX`, `MAKE_SOCK` and `REFER`, and a
system-manager scope in `user-1000.slice`.

**Why these two design changes, and their cost.** Owner N removes the only route by which an untrusted actor could
hold capabilities over a view (through W), at the cost of one more locked system identity (operator setup, §21 C4).
The asynchronous-submission filter removes the only write paths that can outlive a task (§9.8 N4), at the cost of a
new target-world change, V14: Linux AIO and `io_uring` are unavailable in the view, exactly as on a kernel built without
them (`ENOSYS`), and `/proc/self/status` shows `Seccomp: 2`. The alternatives (a per-attempt filesystem freeze, a
mount-reference barrier, restricting only direct I/O) were evaluated and not adopted (§22.3).

**It does not preserve the original success domain as established.** §12.3 and §21 list every change; each is either
required by the criterion through the only mechanism available on this kernel, or not yet shown irrelevant to the full
original domain. **V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION and W1-V7-HOLDER-STATE stay OPEN** until
the runs of §13.2 discharge their premises and rows and an independent review accepts the evidence. No accepted case
is narrowed by rule.

### 0.5 What is carried

Everything the reviews closed is kept in substance, and the units that serve those closures are reproduced byte for
byte where nothing in them changed (§18.5): the criteria (§1); W1-DURABILITY-RELEASE (the release rule, procedure,
hold and window-write paragraphs inside §9.4); W1-IMAGE-OBSERVATION, W1-V5-IMAGE-PINS and W1-V6-IMAGE-PIN (§3.4, §11.7,
§14.5, amended only for the identities and units v9 has); W1-JOURNAL-CONTINUATION (§10.2's continuation rules);
W1-RESOURCES (§14.1, §14.4); W1-SETUP-IDENTITY (§11.7's seal paragraph); W1-V5-PROTOCOL-REFUSALS (Appendix B.4's
refusal frames); W1-V6-C1-DATA (C1 checks only compiled, argv and kernel facts); W1-V6-INVARIANTS; the v8 review's
CLOSED_AT_SPEC_LEVEL items W1-V7-ARCHITECTURE, W1-V7-VIEW-ROOT, W1-V7-C3-DATA, W1-V7-PROBES, W1-V7-SYNC-PROVENANCE and
W1-V7-PREMISES (their v8 text is kept and only extended where §0.3 says); and the closed gaps and sub-gaps of §18.3 and
§18.4. No original admission join, control, fixture, accepted case, criterion, allowance, cap or gate is relaxed.

### 0.6 Reading notes

- "v4", "v5", "v6", "v7" or "v8" in reproduced text names the design state it was written for; where a reproduced
  unit is byte-identical to v7, it is because its statement holds for v9 unchanged (§18.5).
- Appendices C-H are historical records of earlier versions' arithmetic and observations; their mentions of withdrawn
  mechanisms (C9, the S-F drop-in, the user manager, masks, the copy route, R, GATE, `wlscratch.slice`, the tmpfiles
  rule) describe those versions. Appendix I holds v9's numbers and observations.

### 0.7 What v10 and v11 change, per required change (NEW)

The sealed v9 review named nine required changes; v10 answered them (eight CLOSED_AT_SPEC_LEVEL, §23 stated as an
unreviewed change) and the sealed v10 review confirmed that and named three bookkeeping/form fixes, which v11 makes.
"Author's assessment" is the author's claim for the independent reviewer to judge, never closure.

1. **W1-V9-ASYNC-ENUM** (§9.8, §10.6, §15.3, §13.1, §13.2) — the "never a silent change" self-check overclaims are
   withdrawn; the outside memory-context holder is named as a holder of a task-created mapping reference and a
   deferred-`fput` context, shown held-but-unusable; P-ASYNC is a closed specification with a defined enumeration basis
   (both syscall tables; the four deferred-holder classes) and an observed-state discharge/refute predicate; the
   detailed refutation procedure is OPEN (operator-reserved). v10 review: CLOSED_AT_SPEC_LEVEL. Unchanged in v11.
2. **W1-V9-NOOWNER-SCOPE** (§2.3, §5.3, §9.8 N7, §11.3, §16.1) — P-NOOWNER's inventory is extended to every principal
   and every Runas/polkit form for N and W. v10 review: CLOSED_AT_SPEC_LEVEL. Unchanged in v11.
3. **W1-V9-ENUM-USERDEL** (§11.4, §11.5) — `USERGROUPS_ENAB` co-removal modelled for k3 and k4 with X1–X3 and
   W_A/W_B, S-R reverse/resume without a failing `groupdel`, `/var/log/lastlog` captured; reachable set recomputed to
   67 / 104. v10 review: CLOSED_AT_SPEC_LEVEL, counts JACKAL-verified. Unchanged in v11.
4. **W1-V9-PLAN-CONSTRAINTS** (§13.2) — v9's U-11 withdrawn; I-7 gated behind fresh original admission + dispatch-stage
   Gate 0 in a reviewed adopted frame with a nondeterminism control, else blocked. v10 review: CLOSED_AT_SPEC_LEVEL.
   Unchanged in v11.
5. **W1-V9-PREMISE-ORDER** (§16, §13.2) — the critical-premise E0 discharge review precedes O-1; S-1 binds the running
   kernel image/build-id. v10 review: CLOSED_AT_SPEC_LEVEL. Unchanged in v11.
6. **W1-V9-RL-SELFTEST-FIXTURE** (§16.1, §13, §13.1, §9.8 N5, §13.2 S-5) — no installed/S1/RL-reachable path creates a
   set-ID/cap object or drives a test-only switch; fixtures operator-only. v10 review: CLOSED_AT_SPEC_LEVEL as a
   removal requirement. Unchanged in v11.
7. **W1-V9-INVENTORY** (§12.3 V15/V16/V17, §12.2, §9.3, §6.1, §21.3) — new OPEN V-rows; RL closes/CLOEXECs every
   descriptor opened after step 8; G4/C1 check the exact `{0,1,2}` fd set. v10 review: CLOSED_AT_SPEC_LEVEL. Unchanged
   in v11.
8. **W1-V9-REVIEW-PROVENANCE** (§23, with §16, §20, §4.6, §8.6, §17, Appendix D, B.3) — stated as a change to an
   original admission join, adoption blocked. v10 review: correct disposition; **one minor residual fixed in v11** —
   the prompt's source path is `/home/sicarii/Documents/complete-phase1-prompt.txt` (not under `.../outputs/`),
   corrected at the three cite sites (the title/§V11-0 input line, §23.3 and Appendix I); the quoted text and line :60
   were already correct.
9. **W1-V9-FORM-CONSISTENCY** (title critical-premise list; §8.1, §9.1 schema names; §11.6 candidate baseline) — three
   v9 defects fixed. v10 review: PARTIALLY_CLOSED because v10 introduced a unit-partition miscount (**W1-V10-COUNT**),
   fixed in v11 (below).

**v11's three fixes to the v10 review's required changes:**
- **W1-V10-COUNT** — §18.5 and §V11-C.2 and `v11-support/jackal.json` now state the actual partition of v9's 134
  units: **100 CARRIED, 23 AMENDED, 9 COMPOSED, 2 SUPERSEDED** in the v10 accounting (`100+23+9+2` = 134; changed
  = `23+9` = 32, JACKAL exact). Once self-contained, v11 materializes the 2 formerly-SUPERSEDED units (§0.1, the
  §18.5 map) as COMPOSED, so the **v11 partition is 100 CARRIED, 23 AMENDED, 11 COMPOSED, 0 SUPERSEDED, plus 2 NEW
  (§0.7, §23) = 136 v11 units**; of v9's 134, `100+23+11` = 134 and changed-from-v9 = `23+11` = 34 (JACKAL exact,
  Appendix I). §18.5, §V11-C.2 and jackal.json are internally consistent with this.
- **W1-V10-FORM** — resolved: the document is self-contained (every unit materialized, every unit carries a computed
  v11 sha256, §18.5), and §V11-0.1 states the normalization rule under which the formerly-AMENDED units' bytes are
  uniquely determined. The v10 Appendix I self-referential identity defect does not recur: v11's Appendix I identity
  is computed over the assembled file with the single-trailing-newline convention of §V11-0.1 and verified equal to
  the file's bytes for that unit.
- **W1-V9-REVIEW-PROVENANCE residual** — the prompt source path is corrected (item 8 above).

**No spec-closed content changes.** Every spec-closed answer of v10 (ASYNC-ENUM at obligation+predicate,
NOOWNER-SCOPE, ENUM-USERDEL, PLAN-CONSTRAINTS, PREMISE-ORDER, RL-SELFTEST-FIXTURE, INVENTORY, §23) is carried into v11
unchanged. The sensitive-area discipline is kept: the detailed async/privilege-boundary procedures stay
operator-reserved and OPEN. The execution-bound W1-V8-PRESERVATION-ESTABLISH / -PREMISE-DISCHARGE / -EVIDENCE-EQUIV and
V5-B01/B02 stay OPEN; adoption stays blocked.

## 1. Criteria (verbatim, unchanged)

Source: frame v5's sealed actual gpt-6.1-sol review, `work/claude-scratch-frame-v5/review/gpt61-v1/REVIEW.md`
(sha256 above). Lines 76 and 82 are quoted here; lines 76, 82 and 84-123 are reproduced byte-exactly in Appendix A.

**V5-B01 (REVIEW.md:76):**

> Retain file observation identities through the complete walk and revalidate every encountered leaf, including
> excluded generated leaves, using complete descriptor metadata and named-entry joins at the final admission
> boundary. Bind the accepted source/output generation to the spawn under custody that prevents the admitted
> generation from changing before use. Directory-only revalidation or after-run detection must not substitute for
> pre-launch alias refusal. Preserve the exact base recipe, output partitions, allowlist, caps and original gates.

**V5-B02 (REVIEW.md:82):**

> Provide enforced location custody across each frame-owned mutation and the final admission-to-spawn handoff,
> rather than observer-only checks before and after it. Use an independently protected writer/location boundary or
> an equivalent enforced lease that concurrent same-user rename/substitution cannot invalidate while writes or launch
> are possible. Keep original outside-tree authority limited to the documented window protocol and prescribed
> preparation records. Do not relabel frame-owned outside-tree writes as the running-target residual or lower the
> original guarantee; retain this blocker if custody cannot yet be established.

**Residual rulings, N-items and terminal semantics (REVIEW.md:84-123)** are carried unchanged (Appendix A). In
particular: residuals (a)-(d) are ACCEPTABLE_AS_DOCUMENTED only within their stated limits and none authorizes
frame-owned outside-tree mutation or an unsafe alias present at final launch admission; N01, N03, N04, N07, N08,
N09 remain engineering ceilings; N11-N14 are required corrections (§10); "SIGKILL/dead launching parent has no late
collector and leaves manual reservation resolution" stays in force (§9.4).

**WORLDLINE monitor rulings (unchanged; as carried by `frame-v6-PLAN.md:5-13,33-39` and v2 §1):**
- An own-inode "detected and refused" residual does not satisfy V5-B02.
- A root-made filesystem, and W-1 itself, are candidates, not established designs or approved actions.
- Storage (two separate exact excerpts, joined here by an ellipsis): "live preflight that budgets measured run growth
  AND temporary full-restore space above the unchanged reserve … If safe capacity cannot be established, keep dispatch
  deferred."
- "periodic storage sampling plus a factor on the maximum observed write rate does not establish a maximum future
  write rate or stop latency".

**Ineligibility.** No W-1 setting closes an unchanged obligation by lowering it: a lowered reserve, a narrowed
confinement scope, a frame write relabelled as target residual, a waived warning, a narrowed accepted case, control,
fixture, allowlist, cap or gate, a finite cap, a new size refusal, catch-and-refuse, or image ENOSPC presented as an
accepted refusal or success. Any of these leaves the original obligation OPEN.

## 2. Threat model, trusted base, preconditions and residuals

### 2.1 Adversaries

- **A1, concurrent `sicarii` processes** (other agents and sessions; uid 1000): arbitrary code as `sicarii`, user
  namespaces over the delegated subordinate range 100000-165535, FUSE mounts through the set-user-ID `fusermount3`,
  reads of every dumpable `sicarii` process's `/proc` entries in their own user namespace, reads of the world-readable
  `/proc/<pid>/{cmdline,status,statm}` of every process, signals, writes to every `sicarii`-writable file (the window
  file, the inbox, frozen inputs, the toolchain under `/home/sicarii/opt/gnat`, every ancestor of the run path), renames
  of every `sicarii`-owned directory, and invocations of the reviewed `sicarii`→`wlscratch` sudo rule with arbitrary
  arguments, which give A1 a process with **euid W running the reviewed `writer.py`** (§9.8 N2 states what that process
  can and cannot reach). Because A1 can rewrite the toolchain between its identity check and its use (the ruled residual
  (c)), **the target is treated as A1's agent**: anything A2 may do, A1 may in effect do inside the view. A1 must not be
  able to create, rename, substitute, modify or delete any frame-owned location or the admitted generation, or cause the
  frame to mutate outside its tree.
- **A2, the running target** (the allowlisted command and everything it starts, inside the same-identity view of
  §12.2: the lead's host credentials, the user namespace U8, the copied mount namespace with the two binds, the private
  network namespace, the Landlock domain, the seccomp filter, the attempt scope). It may do anything that view permits:
  write wherever `sicarii` can write, change the modes and ACLs of everything it owns, use `openat2` and synchronous
  I/O of every kind, create nested user and mount namespaces (in which Landlock still forbids mounts), pass descriptors
  among its own processes, signal any `sicarii` process (as in v5), and leave processes running in its scope. It cannot
  connect to a pathname UNIX server created outside its domain, create a socket file outside the two binds, reach any
  abstract socket of the host, mount anything, gain privilege by `exec`, submit Linux AIO or `io_uring` requests, ptrace
  or read the `/proc` details of a process outside its namespace, reach g except its `source/` and `tmpdir/`, or leave
  its scope. Nothing it does may let a principal outside the attempt's own process tree hold a usable reference to, or a
  usable name for, an admitted entry (§9.8).
- **A3, every other non-root principal** (other users' processes and non-root services). They hold no credential that
  reaches g, and no channel into a view (§9.8 N1-N3).

### 2.2 Trusted base (outside the threat model)

Root and everything running as root (sudo, systemd and logind, PAM, sshd, the kernel, RL and RL's short-lived helpers);
the reviewed code that alone runs as W (the writer and W2; W owns g); root-owned installed files (`/usr`, `/etc`, the
installed frame under `/opt/wlscratch`); the kernel's namespace, idmapped-mount, Landlock, seccomp, cgroup, ptrace and
file-handle implementations, whose relied-on behaviour is stated as premises (§9.8 N7) — a premise of the trusted base
is an assumption with a refutation probe and a source-reading obligation, never a passing test; the distribution's
build of the installed kernel, systemd and sudo from their published sources (T-DISTRO, §9.8 N7); the Python 3.14.7
runtime under `/usr/lib/python3.14`; the operator's credential. N, the namespace owner, is not a trusted actor: no
process ever runs as N except RL's helper, which runs RL's code and exits (§5.3). No installed code path, and no path
reachable through the S1 rule (`writer.py *`) or the RL rule (`sandbox_launch.py *`), creates a set-user-ID-root object
or a file-capability object or drives a writer/selftest test-only switch; the set-ID and file-capability probe fixtures
are operator-only (§13, §16.1 O-2′), so an installed failure of P-NOSUID or P-NOCAP could not be combined with an
on-demand set-ID object (W1-V9-RL-SELFTEST-FIXTURE). The design gives no protection against root, against kernel
defects or against a compromised operator credential.

### 2.3 Preconditions (checked at setup, §11.3; their failure refuses setup)

- **No privilege route for `sicarii`.** Apart from the reviewed frame rule, no route lets a `sicarii` process run as
  root, `wlscratch` or `wlscratch-ns` without the operator's interactive credential: no `NOPASSWD` sudo rule, of
  `sicarii` or of any principal whose Runas set resolves to `wlscratch` (W) or `wlscratch-ns` (N) through `ALL`, a
  group (`%group`), a uid (`#uid`), an alias or a negation, yielding root or those identities; no polkit grant to any
  subject (not only `sicarii` or a group it is in) for unit management or exec-as-user (for example
  `systemd-run --uid=`); the `empower`
  group empty, no membership in `docker` in any running session, no file capability or setuid/setgid binary owned by the
  new identities. An unprivileged process cannot read `/etc/sudoers` (0440), `/etc/sudoers.d` (not listable) or
  `/etc/polkit-1/rules.d` (not listable); the drafting author observed those refusals on 2026-10-04, so this inventory is
  operator-produced. Observed by the drafting author on 2026-10-04: `/etc/group` lists no member of `docker` or
  `empower`, and the drafting session's own process had supplementary groups 954, 955, 956, 982, 983, 992, 995, 998,
  1000 (no `docker`). This inventory is the obligation of P-NOOWNER (§9.8 N7) and of §5.3; it states what the
  operator-produced inventory must show for N and for W over every principal and every Runas/polkit form
  (W1-V9-NOOWNER-SCOPE), not how to probe it.
- **Kernel settings** as observed: `fs.protected_hardlinks=1`, `fs.protected_symlinks=1`, `fs.protected_regular=1`,
  `kernel.yama.ptrace_scope=1`, `/proc` mounted without `hidepid`, cgroup2 with `nsdelegate`, `fs.suid_dumpable=2`,
  `user.max_user_namespaces=128053`, `kernel.io_uring_disabled=0` and `fs.aio-max-nr=65536` (the last two recorded,
  not required: the view's filter does not depend on them).
- **Kernel features the view needs** (each is also a premise with a probe, §9.8 N7): the running kernel is
  `7.2.6-1-aarch64-ARCH`; the active LSMs are `capability,yama,landlock`; its build configuration sets
  `CONFIG_USER_NS`, `CONFIG_NET_NS`, `CONFIG_SECURITY_LANDLOCK`, `CONFIG_SECCOMP_FILTER`,
  `CONFIG_FANOTIFY_ACCESS_PERMISSIONS`, `CONFIG_AIO` and `CONFIG_IO_URING`, and does not set `CONFIG_BPF_LSM`,
  `CONFIG_SECURITY_SELINUX` or `CONFIG_SECURITY_APPARMOR`; `CONFIG_COMPAT` is set, so 32-bit ARM binaries can run and
  the filter covers both system-call tables (§12.2 step 13b); the installed `linux-api-headers` 7.2 define
  `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` (Landlock ABI 9), `LANDLOCK_ACCESS_FS_MAKE_SOCK`, the scope flags, `MOUNT_ATTR_IDMAP`,
  `NS_GET_MNTNS_ID`, `NS_GET_OWNER_UID`, `STATX_MNT_ID_UNIQUE`, `struct statmount` with `STATMOUNT_MNT_NS_ID` and
  `LSMT_ROOT`, `AUDIT_ARCH_AARCH64` and `AUDIT_ARCH_ARM`; cgroup2 offers the controllers `cpuset cpu io memory hugetlb
  pids rdma`; systemd is 261. (Observed 2026-10-05: v7 Appendix G, v8 Appendix H, Appendix I.)
- **One local filesystem.** Observed: `/`, `/var/lib`, `/opt`, `/tmp`, `/var/tmp` and `/home` are all on `/dev/vda`
  ext4, in one mount (mount ID 32, `relatime`); `/run`, `/dev/shm` and `/run/user/1000` are tmpfs mounts. v9 relies
  only on the non-success of `link` and `rename` between distinct mounts of the view (premise P-XMNT, §9.8 N7); the
  rename and link probes of §13 state per operand whether they are same-mount or cross-mount.

### 2.4 Residuals (stated exactly; none is a new accepted exception)

- **R1, the lead's own processes** (unchanged): W-1 does not protect `sicarii` processes from other `sicarii`
  processes; each frame process outside a view sets itself non-dumpable as its first effective act (§7.7). This is the
  inability carried from frame v5.
- **R2, lead authentication** (unchanged): the original v5 engineering ceiling, carried exactly.
- **R3, the running target** (the ruled `no-target-confinement` residual, ACCEPTABLE_AS_DOCUMENTED at the reference
  ceiling): no confinement of the running target outside g; it covers target writes only, never a frame write and never
  an unsafe alias at final admission. In v9 the target holds `sicarii`'s own credentials and authority, so its writes
  outside g are exactly the original target's, apart from the changes of §12.3.
- **R3b, the running target's path lookups** (the ruled residual (b), REVIEW.md:161 of the v5 review, Appendix A): "v5
  similarly cannot prevent an already-running target from resolving absolute paths or writing while another process
  changes the tree". The ancestors of the run path are `sicarii`-owned host directories (§3.3); A1 can rename them after
  the spawn and so redirect a later absolute lookup by the running target. The admitted generation in g is not changed
  by that, and the conclusion's comparison of the generation detects a run whose outputs did not land in it. Before the
  spawn, a redirected path is a pre-launch alias, which C refuses (§4.5 item 4), as v5 refused a run directory that its
  location chain did not reach.
- **R4, the toolchain** (ruled ACCEPTABLE_AS_DOCUMENTED, unchanged): identity-checked, then executed by path; W-1
  claims no custody of it.
- **R5, exposure**: the target reads exactly what `sicarii` reads, including the export trees that the lead may read
  (§6.3); the view's construction is privileged code (RL), reviewed and installed by the operator.
- **R6, availability**: a `sicarii` process can stop an attempt (kill the front, signal processes whose real uid is
  `sicarii`, which includes the target, as in v5, or modify the window file, N07). The result is an interrupted,
  non-success attempt or a held window, never a custody change. Whether sudo relays such signals is probe P-SIG.
- **R8, root and the kernel** (§2.2).

## 3. Principals, accounts and layout

### 3.1 Accounts and groups (two new identities)

| Identity | Kind | Purpose | Members |
|---|---|---|---|
| `wlscratch`, uid = gid = W | user + user-private group | The only writer of generation trees | none besides the user |
| `wlscratch-ns`, uid = gid = N | user + user-private group | The owner of every view user namespace U8 (§12.2 step 10). No process runs as N except RL's helper, which creates the namespace and exits; N owns no file, has no sudo rule, no login, no linger, no subordinate range | none besides the user |

Candidate numbers: W = 950, N = 951. As observed on 2026-10-04 both are unused by every passwd and group entry (the
lowest used system uid is 957 and the lowest used gid at or above 900 is 954), inside `SYS_UID_MIN`-`SYS_UID_MAX`
500-999 of `/etc/login.defs`, and outside every range in `/etc/subuid` and `/etc/subgid` (§5.4). §11.2 fixes the policy
and the prestate re-verifies them. v7's `wlscratch-run` and `wlscratch-gate` do not exist; no process of a view has
another host identity than the lead's. `sicarii` gets no new group membership and no new login.

### 3.2 Roles (processes)

| Role | Process and credentials | Started by | Code |
|---|---|---|---|
| F, front | the lead's real outer invocation `/usr/bin/python3 -B /opt/wlscratch/frame-v6w1/front.py <verb> …`, uid 1000; verbs `adopt`, `materialize`, `dispatch` | the lead | installed, root-owned |
| S1 | `sudo -n -u wlscratch -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py <verb> …` | F | `/usr/bin/sudo` |
| W, writer | `writer.py`, uid/gid W; verbs `adopt`, `materialize`, `dispatch`, `selftest` | S1 | installed |
| S2, S_O | `sudo -n -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py <verb> …` (the RL rule) | W or W2 | `/usr/bin/sudo` |
| RL, root launcher | `sandbox_launch.py launch …`, `observe …` or `selftest …`, root: checks its invocation, creates the scope with `systemd-run --scope` in the system manager under `user-1000.slice`, builds the view (§12.2), sends `RL_IDENTITY` and `exec`s L or O | S2 or S_O | installed, privileged |
| RL's helpers | short-lived children of RL: one per U8 with uid and gid N (creates U8 and exits), one per idmap namespace M_run (uid and gid N, likewise) | RL | installed (part of `sandbox_launch.py`) |
| L, launcher | `launch_target.py launch …`, the lead's host credentials, in U8 and the view, in the attempt scope | RL, which `exec`s it in place | installed |
| C, in-scope child | `launch_target.py child …`, the same pid, credentials, view and scope as L | L, by `exec` after `GO` | installed |
| U, scope | transient `wlscratch-<g12>-<A>.scope` of the system manager in `user-1000.slice`, with `MemoryMax=8G`, `MemorySwapMax=0` and the properties of §8.3 | RL, through `systemd-run --scope` | systemd |
| T, target | the exact allowlisted command, the same credentials, view, filter and scope; started by C's spawn call (v5 `spawn`) | C | toolchain |
| O, observer | `launch_target.py observe …`, the lead's host credentials, in its own scope `wlscratch-o-<g12>-<A>-<n>.scope` in `user-1000.slice` and its own view instance | RL, for W or W2 | installed |
| S3, W2 | `sudo -n -u wlscratch -- … writer.py seal-front <N_F> <g> <A> <mode>` (the S1 rule); W2 = `writer.py seal-front`, uid/gid W, mode `seal` after W ended with `FINAL`, mode `recover` after W died or its channel failed (§9.7) | F | installed |

`<g12>` is the first 12 hex digits of the generation id; `<A>` is the v5 attempt stamp (`STAMP_RE`). The installed
frame carries two compiled path constants besides `install_root`: `SOURCE_FRAME`, the frozen v6-W1 source directory in
the lead's tree, and below it the sealed review directories `REVIEW` (`<SOURCE_FRAME>/review/<code review>`) and
`INSTALLED_REVIEW` (`<SOURCE_FRAME>/review/<installed-evidence review>`) (§4.6, §16). Every process of a view is started
by RL inside a new scope whose cgroup no non-root process can enter or leave (premise P-CG), and every process whose
user namespace is a U8 descends from RL's stage-2 process (premise P-SETNS).

### 3.3 Layout

```
/var/lib/wlscratch                     root:W        writer home (setup)
  lease/                               root:W        setup; writer-only traverse
    writer.lock                        root:W 0440   setup; flock-only
  runs/                                W:W           T_root (setup); work-image mount point
    <g>/                               W:W           generation root g (writer-created at M4); no sicarii search
      generation.json                  initial generation record                               [P_adm]
      commits/                         generation journal (P_adm markers)                      [P_adm]
      inputs/                          streamed input records + manifest.json                  [P_adm]
      overlay-snapshot/                v5 overlay snapshot (0700 dirs, 0600 files)             [P_adm]
      source/                          admitted recipe (exact recipe modes)                    [P_adm; outputs below it]
      tmpdir/                          the view's TMPDIR (M7, 0700)                            [P_adm: directory only]
      materialization.json             v5 schema plus §4.3 fields                              [P_adm]
    records/                           W:W           R_root (setup); records-image mount point
      <g>/                             W:W           g_rec (M4)
        attempts/<A>/                  P_att(g, A): attempt.json, commits/ (attempt journal), fallback.journal,
                                       fallback-allocation.json, inputs/, front/, channel/, w2-<k>/,
                                       stream files, observer files, every v5 attempt record
        export/                        P_exp(g): generation/, <A>/inc-<n>/, capture-<A>/ (§15.3)
      adoption-<I>/                    W:W           P_ado(I), installed-frame adoption root (writer-created by `adopt`)
        lead-adoption.json, commits/ (adoption journal), invocations/<stamp>/, export/inc-<n>/
    selftest-<h>/                      W:W           sacrificial selftest generation root (§13)
    records/selftest-<h>/              W:W           its record root
/opt/wlscratch/frame-v6w1/             root:root     installed frame (member-exact)
/opt/wlscratch/setup-identities.json   root:root 0644 setup identity record (§11.5 S-H, §11.7)
```

`I` is the sha256 (64 lowercase hex) of the installed `frame-inventory.json`; `h` is 32 lowercase hex. Exact modes and
ACLs are in §6.3. N owns no file and no directory of this layout. The target's `/tmp` is the host's, and the scopes
live in the lead's existing `user-1000.slice`.

**The run path without a lead preparation step.** `<RUNS>` is v5's `RUNS`
(`/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-runs-v5`). Neither the
lead nor the frame creates anything there: the frame's outside-tree authority stays limited to the window protocol and
the prescribed preparation records (V5-B02), and no lead step is required. RL presents the run path inside the view
only (§12.2 step 11):
- if `<RUNS>/<label>/source` exists in the copied namespace as a directory reached without symlinks, RL binds g/source
  over it (the host directory's contents are hidden in the view);
- otherwise RL mounts a private read-only `tmpfs` (the *skeleton*) over the deepest existing directory ancestor D of
  the run path, creates in it the missing directories of the path (owner 1000:1000, mode 0700, as v5's `materialize`
  created `<RUNS>` and `<RUNS>/<label>`, S:977-986), re-attaches every entry of D as a bind of the host entry, and binds
  g/source at the end of the path.
No host filesystem is written in either case. **Label semantics** (v5: `materialize` refused when `<RUNS>/<label>`
existed, S:984-986): `materialize` refuses when `<RUNS>/<label>` exists on the host (F's anchored, read-only check,
v5's own test) or when a generation of T carries the label. For every state reachable through frame verbs the outcome
is v5's: the frame never creates `<RUNS>/<label>`, so v5's refusal "the run directory this label's materialize created
exists" corresponds to "a generation with this label exists". The one remaining difference (C6' in §21): in v5 the
lead could free a label by deleting the run directory; a generation in T cannot be deleted by the lead. W refuses a
`materialize` whose label an existing generation of T already carries.

### 3.4 The protected intended run tree, its anchors and routing [corrections: W1-V6-IMAGE-PIN, W1-V6-INVARIANTS; v4: W1-IMAGE-TREE]

**Definition.** The protected intended run tree T is the directory tree rooted at T_root = `/var/lib/wlscratch/runs`,
including its record root R_root = `/var/lib/wlscratch/runs/records` and every mount at or below T_root that
`setup-identities.json` lists. Every component from `/` to T_root is root-owned and writable only by root (`/`, `/var`,
`/var/lib` root:root 0755; `/var/lib/wlscratch` root:W 0750 with search-only ACL entries). Inside T only W can create,
rename or remove entries, except that the processes of a view can do so below `g/source` and `g/tmpdir` of their own
generation, which RL binds into the view with the idmap M_run (§12.2). No principal other than W, root and those
processes can search g (§6.3). T is the categorical writer tree of §5.2: no writer verb writes anywhere else, in any
configuration.

**Anchors.** Every writer and helper reaches T only by anchored descriptor chains (v5 `Dir.anchor`, `O_DIRECTORY|
O_NOFOLLOW` per component, from `/`):
- `A_T` = T_root; `A_R` = `A_T` + `records`, opened from the held `A_T` descriptor;
- per generation: g = `A_T` + `<g>`, g_rec = `A_R` + `<g>`;
- per adoption: P_ado(I) = `A_R` + `adoption-<I>`;
- per selftest: `A_T` + `selftest-<h>` and `A_R` + `selftest-<h>`.
Each anchor's pinned identity (§11.7) is compared with `setup-identities.json` before any use: both anchors at every
writer invocation, and `A_T` and g at every RL invocation before RL builds a view. L, C, O and T never traverse T by
path: RL hands them their generation's `source/` and `tmpdir/` as binds of the view. g, g_rec and P_ado(I) are
compared with the identities committed when they were created (`generation.json`, the adoption journal).

**Names.** The entries of T_root are exactly: generation roots (`^[0-9a-f]{32}$`), `records`, and `selftest-<h>`. The
entries of R_root are exactly: record roots (`^[0-9a-f]{32}$`, each matching an existing generation root),
`adoption-<I>` (`^adoption-[0-9a-f]{64}$`) and `selftest-<h>`. Each is a W-owned directory. With images, each image
root also contains `lost+found` (made by `mkfs.ext4`), which W never uses and no walk enters. It is the one special
entry, admitted only in an image root, only under that name, and only if `fstatat(…, AT_SYMLINK_NOFOLLOW)` shows a
directory with uid 0, gid 0, mode 0700 and the inode number pinned for that image (§11.7) and reading its access ACL
finds none; its link count, size, times and contents are root's (`e2fsck` may add entries), W cannot read them, and
they are never compared. Without images no `lost+found` is admitted. W lists T_root and R_root at every invocation and
refuses before any mutation if an entry falls outside this grammar or is neither a W-owned directory nor that special
entry (with images, `records` must be the records mount, below). Only W or root can create entries there, so an
unexpected entry is a defect, not an adversary's move, and it refuses.

**Routing** (complete; one table for both configurations):

| Object | Anchor and path | Journal that commits it |
|---|---|---|
| `generation.json`, `inputs/**` (materialize), `overlay-snapshot/**`, the recipe, `tmpdir/` (M7), `materialization.json` | g (P_adm; the contents of `tmpdir/` are target temporaries, never admitted, §4.1) | generation journal `g/commits/` |
| `attempt.json`, `fallback-allocation.json`, every attempt record, stream files, observer files, front records, channel segments, recovery records, W2 records, release records | g_rec `/attempts/<A>/` (P_att) | attempt journal `g_rec/attempts/<A>/commits/` |
| `fallback.journal` slots | g_rec `/attempts/<A>/fallback.journal` | none: described by `fallback-allocation.json`; slots are self-validating (§10.4) |
| generation export with its payload pack | g_rec `/export/generation/` (P_exp) | attempt journal of the materializing attempt A0 |
| attempt exports and complete captures | g_rec `/export/<A>/inc-<n>/`, g_rec `/export/capture-<A>/` (P_exp) | attempt journal of A |
| adoption record and its bookkeeping and exports | P_ado(I) | adoption journal `P_ado(I)/commits/` |
| selftest objects | `A_T/selftest-<h>`, `A_R/selftest-<h>` | their own sacrificial journals |

**Missing-mount checks.** Without images, `A_T` and `A_R` are plain setup directories on the root filesystem: their
pinned identity includes `st_dev` and `st_ino`, and `A_R`'s `st_dev` equals `A_T`'s. With images (§14.5):
- `A_T` must be the root of the work image: its `st_dev` differs from that of `/var/lib/wlscratch`; `/proc/self/mountinfo`
  has exactly one entry whose mount point is `/var/lib/wlscratch/runs`, whose major:minor equals `A_T`'s `st_dev`, whose
  fs type is ext4, whose super options include the reviewed ones and whose mount options include `nosuid,nodev,noexec`;
  its source is a loop device whose `/sys/block/<loop>/loop/backing_file` names the pinned image file;
  `/dev/disk/by-uuid/<pinned UUID>` resolves to that loop device; the image root's owner, group, mode, ACL and inode
  number equal the pinned ones. W and W2 also check the images directory and the backing file at every use: they open
  `/var/lib/wlscratch-images` through an anchored chain (root:W 0750, so W can list and search it, §14.5 J1), require
  its pinned identity and its exact entry set (the two pinned image file names and nothing else, read from the open
  directory descriptor), and require by `fstatat(images, <name>, AT_SYMLINK_NOFOLLOW)` a regular file with the pinned
  `[dev, ino]` and size, uid 0, gid 0, mode 0600 and one link. RL (root) repeats every item of this check before it
  builds a view; L, C, O and T see the images directory as `sicarii` does: it is root:W 0750 and grants them nothing.
- `A_R` must be the root of the records image, checked the same way, and its mountinfo parent ID must equal the work
  image's mount ID (the records image is mounted inside T, on the work image).
- If an image is not mounted, the path resolves to its bare mount point: root-owned, mode 0700, empty, on the parent
  filesystem. Its `st_dev` equals the parent's, so the check refuses before any mutation, and W could not create
  anything in it anyway. The loop device number and mount ID may change across boots; they are observed, never pinned
  (§11.7).

**No new outside-tree authority.** Every writer mutation lies in T. The adoption record, which v5 wrote into the
frame's own review directory outside its run tree as a prescribed preparation record, now lies inside T (§4.6). F
writes nothing. RL's effects outside T are exactly those of the inventory of §9.8 N5-N6, each classified there. The
only frame writes outside T remain v5's window protocol by F, unchanged (N07).

## 4. Generation order and record partitions [correction: W1-GENERATION-PROTOCOL; gap: generation-order]

### 4.1 Partitions [correction: W1-V6-INVARIANTS]

- **P_adm(g), the admitted generation partition**, in g: `generation.json`, `commits/` (the generation journal),
  `inputs/**`, `overlay-snapshot/**`, every recipe object under `source/` (files, directories, their modes and
  contents), the directory `tmpdir/` itself (not its contents; only its `[dev, ino]`, because its mode and ACL become
  the target's, as `TMPDIR` was the target's in v5) and `materialization.json`. The frame writes P_adm only in the
  `materialize` invocation that creates g. After that invocation's final verification and the materialization marker
  (§4.2, M8), no writer verb has any path that mutates P_adm: no verb rewrites, renames, deletes, chmods or re-ACLs an
  existing P_adm object. The only other process that can change the recipe is the target of a launched attempt, during
  its run and through its view, where it owns `source/` as it owned its run tree in v5 (§12.2): v5's conclusion detects
  every change of a recorded file or directory (S:1684-1691, `verify_materialization`), the attempt is non-success, and
  every later admission refuses the changed generation, exactly as in v5 (§21).
- **Partition contents.** The output partitions are v5's (`obj/`, `lib/`, `resource-tests/obj/`,
  `resource-tests/bin/` below `source/`, S:79). The target creates them and everything below them, as in v5:
  `materialize` creates none, and v5's own rule requires that none exists at materialization (S:1033). The frame never
  writes, renames, deletes, or changes the mode, ACL or owner of, any entry below `source/` after M8; it reads them only
  through a view, with `O_NOATIME` (§9.8 N6), or, after the attempt's holder event, as their on-disk owner for the
  complete capture (§15.3). They are part of what each later attempt admits, so every attempt re-observes them in full
  (§4.5).
- **Target temporaries**, below `g/tmpdir/` (the view's `TMPDIR`, `/home/sicarii/.cache/workflow-tmp`) (§12.2). Never
  walked or admitted by the frame; copied as evidence by the complete capture after the holder event (§15.3). Nothing
  removes them, as nothing removed them from v5's `TMPDIR`. An attempt sees what earlier attempts of the same generation
  left there, but not what other generations' targets or other `sicarii` processes put in the shared `TMPDIR`, which it
  saw in v5; and they no longer see its files (a change, §12.3 V7'). The view's `/tmp` is the host's `/tmp`, outside T.
- **P_att(g, A), the attempt bookkeeping partition**, in g_rec `/attempts/<A>/`. Every writer invocation that creates
  an attempt has one: the creating `materialize` invocation (A0, kind `materialize`) and every `dispatch` invocation
  (kind `dispatch`). It is created and written by that W; afterwards only W2 instances of the same attempt append to
  it, each only in new names below its own `w2-<k>/` and in the attempt journal (§5.2, §9.7).
  Create-only. The target never reads it and cannot reach it (§12.2): launch records reach C over its channel
  (§7.1), and target streams are passed as open descriptors (§6.4).
- **P_exp(g), the export partition**, in g_rec `/export/`. Writer-produced read-only copies of committed records, of the
  recipe and snapshot payload for the generation, and of each ended attempt's complete capture (§15.3), for the lead and
  the vault. Create-only. Never read by the target, never an admission input.
- **P_ado(I), the adoption partition**, in R_root `/adoption-<I>/`: the installed-frame adoption record, the adoption
  journal, per-invocation bookkeeping and the adoption exports (§4.6). Written only by W in `adopt`; create-only; read
  by W at every dispatch.

The partitions are disjoint. Every frame mutation after a generation's creation lands in a P_att, a P_exp or a P_ado,
never in P_adm, the partition contents or the target temporaries. No frame mutation of `source/` or of any directory
above an admitted entry remains after M8.

### 4.2 Exact order

The steps below and the state machines of Appendix B.4.4 are one specification: each step names the state in which
its messages travel, and Appendix B.4.2-B.4.3 give every message's exact body.

**Adoption of the installed frame (`front.py adopt <code-events> <code-argv> <installed-events> <installed-argv>`;
v5 `adopt`).**

- AD1. F starts (§7.7 first act), records its identity (§8.1), validates its argv (four absolute paths: the event
  stream and the exec-argv record of the code review and of the installed-evidence review).
- AD2. F performs, in the real lead context, every check of v5 `adopt` (S:816-837) for both sealed reviews (§4.6,
  joins 1-4). F writes nothing.
- AD3. F creates its two channel pipes and starts S1 → W (`writer.py adopt <N_F>`). W: first act, identity, lease
  (§5.1), anchors A_T and A_R with the missing-mount checks (§3.4); computes I and S (the sha256 of the installed
  `frame-inventory.json` and of `setup-identities.json`, read through anchored root-owned paths); requires
  `P_ado(I)/lead-adoption.json` absent (§11.1: no-follow ENOENT; any present state refuses, as v5 S:821 "adoption
  already recorded"); creates P_ado(I) with `commits/` and `invocations/` if absent, or requires their §6.3 identity
  (owner W, mode, ACL) if present; creates `invocations/<stamp>/` and commits `invocation.json` (§4.3). State
  `HELLO`: `W_HELLO`, `HELLO_ACK`. This bookkeeping precedes the seal comparison of AD5 (§11.7).
- AD4. State `INPUTS` (phase `adoption`): F streams the lead module (pinned), the two review rosters with their freeze
  records (joined), the two review-provenance records (the §23.4 join selected by `reviewer_kind`: for a
  Claude-subagent review the sealed review-freeze, `raw-final-message.txt`, the reviewer agent id and the task-output
  sha256; for a gpt-6.1-sol review the event stream, exec-argv record and rollout) (joined), the `scratch-adopt`
  lead observation (observation) and F's adoption body (joined).
- AD5. State `COMMIT`: W verifies (§4.6), including the seal comparison of §11.7, and, only if every join holds,
  commits `lead-adoption.json` and its marker in the adoption journal; `ADOPTED`. Otherwise `REFUSAL`, and no adoption
  record exists.
- AD6. State `EXPORT`: the adoption export increment (§15.3), `EXPORTED`. State `FINAL`: `FINAL`, `BYE`; W closes and
  exits.
- AD7. F waits for S1 and exits by §10.7. No W2 runs for `adopt`; F's terminal facts are its console output, as v5
  `adopt` had no terminal record.

The adopt invocation runs only after a procedural Gate 0 receipt computed with the adopt/materialize-stage expression
(§14.3), and its retained bytes are counted under A_in (§14.2). It reserves nothing and launches nothing.

**Generation creation (`front.py materialize <label> <overlay-dir>`; v5 `materialize`).**

- M1. F starts (§7.7 first act), records its identity (§8.1), validates its argv grammar (`label` matches v5
  `NAME_RE`; `overlay-dir` absolute).
- M2. F reads, through the v5 anchored readers, the base descriptors (`source-binding.json`,
  `source-inventory.json`, `source-directory-modes.json`), observes `BASE/source` against the pinned inventory
  (`observe_tree`, as v5 `base_tree`), and observes and reads the overlay directory (`observe_tree` + `read_files`,
  as v5 `materialize`), opening every file it reads, all `sicarii`-owned, with `O_NOATIME` (§9.8 N6). F then performs
  v5's label test read-only: it anchors `RUNS.parent` by v5's `Dir.anchor`, and if `<RUNS>` exists it requires that
  `<RUNS>/<label>` is absent (v5's "run already exists", S:977-985); it creates nothing (§3.3). F writes nothing.
- M3. F creates its two channel pipes after its first act and starts S1 → W (`writer.py materialize <N_F> <label>`,
  `N_F` = 32 random bytes as 64 hex, §7.3).
- M4. W starts (§7.7), records its identity, takes the lease (§5.1), anchors A_T and A_R with the missing-mount checks
  (§3.4), refuses if a generation of T already carries the label (§3.3), and then, in this order: creates g (v5
  `Dir.child(create=True)`: mode 0700, owner W, link count 2, same device, empty, not an ancestor) and reads back
  that it carries no ACL (g has none, so no principal but W and root can search it, §6.3), creates `g/commits/`
  (0700, authenticated); creates g_rec the same way, then sets its access ACL by
  `fsetxattr` on the held descriptor and reads it back (§6.3), then creates `g_rec/attempts/` and
  `g_rec/attempts/<A0>/` with its `commits/` (0700, authenticated); commits **`generation.json`** (§4.3; it binds g,
  g_rec and both anchor chains) as the first record of the generation journal; commits **`attempt.json`** (kind
  `materialize`) as the first record of A0's attempt journal; creates `fallback.journal` and commits
  **`fallback-allocation.json`** (§10.4). State `HELLO`: `W_HELLO` lists those three committed records.
- M5. F answers `HELLO_ACK` (it echoes `N_W` and carries F's identity). W commits `front/front-identity.json` and
  sends `RECORD_COMMITTED`.
- M6. States `INPUTS_DESCRIPTORS`, `INPUTS_OVERLAY`, `INPUTS_BASE`: inputs are streamed in three requested phases
  (§7.2): (i) the three base descriptors, the lead module and F's base-tree observation; (ii) the overlay files and
  `DELETE.list`; (iii) exactly the base files the recipe needs (base inventory minus deletions minus overlay-replaced
  paths), in sorted path order. W verifies every pinned input before it uses or writes it (§8.6, pinned versus
  observation inputs). Descriptor bytes, the lead module and the observation go to `g/inputs/` as create-only input
  records. Overlay bytes go only to `overlay-snapshot/` and base-file bytes go only to their recipe path under
  `source/`; the message log records their headers and a reference to the place their bytes were written, so no bulk
  payload is retained twice in P_adm and P_att (§7.3). W commits the input records of each phase and sends
  `PHASE_DONE`; after the last phase it commits `inputs/manifest.json`. Overlay and base bytes become snapshot and
  recipe content, not records: M8 verifies them as a whole and `materialization.json` binds their digests.
- M7. State `MATERIALIZE`: W materializes exactly as v5 `materialize` (S:959-1049), with streamed verified bytes in
  place of anchored reads of `BASE` and the overlay directory: `overlay_rules`; `expected_source`; snapshot files
  written by `write_bytes` with the default 0600 into snapshot directories created 0700; every recipe directory
  created 0700 and authenticated; every expected file written with its row mode (base mode, or 0644 for a new overlay
  unit); then the recipe directory modes applied deepest first, the recipe root last (`set_mode`); then `source.sync()`.
  No output partition is created (v5, S:1033). Then `tmpdir/` is created (0700, authenticated), with no ACL.
- M8. W verifies with a full walk of `source/` and of the snapshot: recipe content and modes equal the recipe, and no
  output partition exists (v5's rule, S:1033); `tmpdir/` is empty with mode 0700 and no ACL. W then writes
  **`materialization.json`** (§4.3) and its marker, runs `verify_materialization` against the committed record, and
  re-verifies the location of every held handle. **This is the frame's last mutation of P_adm(g), ever.** The
  generation journal ends with this marker and never grows again.
- M9. Still in `MATERIALIZE`: W writes the generation export (`g_rec/export/generation/`, §15.3): the whole generation
  journal and every record it commits (`generation.json`, the input records and manifest, `materialization.json`), a
  finite prefix ending at the materialization marker, and the **payload pack**: one export copy of every recipe file
  and every snapshot file, read back by W from P_adm (W-owned, opened with `O_NOATIME`) and listed in the manifest with
  its relative path, sha256 and size, so that every channel and record reference into the recipe or the snapshot
  resolves inside the exports (§7.3, §15.3). Its export markers go to A0's attempt journal; W sends `MATERIALIZED`.
- M10. State `VAULT`: W sends `STAGE_REQUEST {stage: vault}`; F runs `project-vault pin <g_rec>/export` and
  `project-vault status` (§8.5) and answers `STAGE_RESULT`; W commits `front/front-stage-vault.json`.
- M11. State `EXPORT`: A0's export increment 0 (§15.3), `EXPORTED`. State `FINAL`: `FINAL`, `BYE`; W closes and
  exits. F waits for S1; F starts S3 → W2 (`seal-front … seal`), which commits F's terminal record and A0's next
  export increment (§9.7, §15.3); F exits (§10.7).

A failure in M4-M8 leaves a generation that can never be admitted: without a committed materialization marker no
dispatch can use g (D3). W refuses on the path Appendix B.4.4 gives for the state it is in (`EARLY_REFUSAL` before
`W_HELLO`, `REFUSAL` after it); whenever A0's `attempt.json` is committed it commits `refusal.json` in P_att(g, A0) and
an export increment, and otherwise its facts are in `EARLY_REFUSAL` and on its stderr; the partial P_adm stays as
evidence.

**Dispatch attempt (`front.py dispatch <inbox> <g> <action> [args]`; v5 `dispatch` + `run` + `child`).**

- D1. F starts, records its identity and its process attributes (§8.3), validates `action`/`args` against v5
  `ACTIONS`/`command()` grammar and anchors the lead-created inbox (`sicarii`-owned, mode 0700, empty).
- D2. F creates its two channel pipes and starts S1 → W (`writer.py dispatch <N_F> <g> <action> [args]`).
- D3. W starts, takes the lease, anchors A_T and A_R with the missing-mount checks, opens g and g_rec by anchored
  chains; requires the committed markers of `generation.json` and `materialization.json` in the generation journal
  and equality of the P_adm identities with them, `tmpdir/` included by `[dev, ino]` only; requires the committed
  adoption record `P_ado(I)/lead-adoption.json` of the installed inventory I with its marker in the adoption journal
  (otherwise it refuses: the installed frame is not adopted); requires `setup-identities.json` to match the seal that
  adoption record carries, and the setup identity recorded in `generation.json` to equal it (§11.7; otherwise it refuses
  before any mutation); creates `g_rec/attempts/<A>/` with its `commits/` (0700, authenticated); commits
  **`attempt.json`** (kind `dispatch`); creates `fallback.journal` and commits **`fallback-allocation.json`**. State
  `HELLO`: `W_HELLO`.
- D4. F answers `HELLO_ACK`; W commits `front/front-identity.json`.
- D5. State `INPUTS` (phase `dispatch`): F streams the lead module (pinned) and its process attributes (§8.3); W
  verifies the module and commits it as `attempts/<A>/inputs/<seq>-lead-module`, and commits the attributes as
  `attempts/<A>/inputs/<seq>-process-attributes`.
- D6. State `ADOPTION`: W sends the committed adoption record's descriptor, marker digest and bytes
  (`ADOPTION_RECORD`).
- D7. State `FRONT_PARENT`: `STAGE_REQUEST {stage: front-parent}`; F performs its parent-stage half (§8.1): fresh lead
  observation (`claude_lead.observe('scratch-run', …)`), the front part of frame admission (installed-inventory pin
  against both reviews and the delivered adoption record; the review-provenance re-joins (§23.4, selected by
  `reviewer_kind`); adoption observation and transcript prefix; §4.6), base-tree re-observation, its own runtime and
  manager identity, and the front half of the `preflight` sample (sibling units in `sicarii`'s manager,
  `storage_status.py`). `STAGE_RESULT`; W commits `front/front-stage-parent.json`.
- D8. State `PARENT`: the writer half (record pins, location, the attempt-journal join of §10.6, and the manager census
  M of §9.4: no RL scope live); then the observer for the parent stage: W creates and syncs the observer stream files,
  commits `observer-intent-1.json` binding them (§9.3, G0) and starts S_O → RL → O, and W commits
  `observer-1-rl-identity.json` before its request. RL (stage 1, root) takes the kernel census K and its root scan of
  §12.2 step 5 before it builds O's view. O, inside its observer view: takes the parent-stage kernel census K (§9.4; no
  process naming g); takes the full walk of the view's `source/` with the original walk rules and v6's final pass, with
  every excluded leaf's `stat_key`, every file and directory opened with `O_NOATIME`; takes the target-context
  identities `parent` in its view (§8.4); and takes the helper half of `preflight` (heavy processes, meminfo). W commits
  `observer-1-parent.json` and `observer-wait-1.json`. A failed join, a refusal by an original walk rule, or a census
  observation that fails or is UNKNOWN refuses the attempt (nothing reserved).
- D9. State `VAULT`: `project-vault pin <g_rec>/export` and `project-vault status` by F (§8.5).
- D10. State `GATE0`: frame-enforced Gate 0 receipt for the dispatch stage (§14.3, with the expression of §14.7).
- D11. State `LAUNCH_RECORD`: W commits **`launch.json`** (§4.3). Its parent-observation pin is the admitted parent
  observation, `observer-1-parent.json`.
- D12. State `RESERVE`: reservation, driven by F under the shared-window lock (§9.4): `reservation-intent.json` is
  committed by W before F's window write; `reservation.json` after it.
- D13. State `MEMORY_GATE`: v5 memory gate: W issues each challenge; F prints it and forwards the lead's answer line
  and receipt bytes from the inbox; W verifies exactly as v5 (`memory_gate`, `receipt_line` deadlines 300 s and 30 s).
- D14. State `ADMIT`: W commits **`admission.json`**; then creates `launcher.stdout`, `launcher.stderr`,
  `scope.stdout`, `scope.stderr`, `child.stdout` and `child.stderr` in P_att, each create-only 0600 and synced, keeps
  their descriptors, reads each `[dev, ino]` by `fstat` on the held descriptor and syncs the directory; then commits
  **`launcher-intent.json`** binding those identities (§4.3); sends `LAUNCH_INTENT_COMMITTED`.
- D15. State `PROCEED`: F sends `PROCEED_LAUNCH` only after D14's acknowledgement and only while it still owns the
  window (`owns_window` under the lock); otherwise it sends `STOP`. No launcher process exists before
  `PROCEED_LAUNCH`.
- D16. State `RUNNING`: RL, the scope and the view, then launch, child stage, final pass, spawn and run (§9.3, §12.2).
- D17. State `AFTER`: F's after-stage half; the observer's after stage (the next `observer-intent-<n>.json`, the walk
  with `O_NOATIME`, the identities `after`, the report bytes read with `O_NOATIME`, and the classification of §9.4);
  W's stream finality record (§10.6); `result.json`; then, once the kernel census shows U `populated 0`, the complete
  capture of the attempt (§15.3). State `CONCLUDE`: `CONCLUSION`.
- D18. State `RELEASE`: the release protocol of §9.4, driven by F, with W committing the release records.
- D19. W commits `final-status.json`. State `EXPORT`: export increment 0 (§15.3), `EXPORTED`. State `FINAL`:
  `FINAL`, `BYE`; W closes and exits.
- D20. F waits for S1; F starts S3 → W2 (`seal-front … seal`), which commits F's terminal record and the next export
  increment; F exits (§10.7). If F did not receive `FINAL` from W, F runs writer-death recovery instead (§9.7).

**Post-writer (`writer.py seal-front <N_F> <g> <A> <mode>`, started only by F).** §9.7 specifies both modes. W2 takes
the lease, verifies its capability (§5.2), never modifies an existing record, and writes only new names in P_att(g, A)
and P_exp(g).

### 4.3 The records that order the generation (complete field lists in Appendix B.3)

- **`generation.json`** (initial generation record, first record of the generation journal). It binds only facts that
  exist when it is written: generation id, creation time, boot id, W's identity and invocation (argv,
  `SUDO_USER`/`SUDO_UID`/`SUDO_COMMAND`), the `N_F` nonce from W's argv, the front-process triple
  `(pid, start_time_ticks, boot_id)` that W reads from `/proc` (F is the parent of S1, which is W's parent), the lease
  identity, the location chains from `/` to g and to g_rec (device, inode, owner, mode, ACL digest for each component,
  with the mount facts of §3.4 where images are used), the installed frame inventory pin, the setup identity record
  pin, the channel genesis heads, the verb, the label and the stamp of A0. It binds **no** input digest, recipe,
  reservation or launch fact, because none exists yet. F's self-reported identity arrives later (`HELLO_ACK`) and is
  recorded in P_att(g, A0), not here.
- **`inputs/<seq>-<name>` and `inputs/manifest.json`** (P_adm, `materialize` only). One create-only record per
  descriptor, lead module and observation input (bytes plus `{path, size, mode, sha256, class, pin_source, verdict}`),
  and a manifest written after the last input: every input header including overlay and base files, the place each
  payload was written, the channel heads after the last input.
- **`materialization.json`.** The v5 schema (`claude-scratch-materialization-v5` fields: base pins, overlay snapshot
  and identities, overlays, deletions, `source`, `source_directory_identities`) plus `generation` (pin of
  `generation.json` and its marker), `inputs_manifest` (pin), `tmpdir_dir` (path, `[dev, ino]`), `run_path` (the view
  path `<RUNS>/<label>/source` of §12.2), `recipe_mode_property` (§6.1), `channel_heads`. Its schema name becomes
  `wlscratch-materialization-v3`; the v5 `run` field becomes the generation root path.
- **`attempts/<A>/attempt.json`**, two exact schemas. Kind `materialize` (`wlscratch-attempt-materialize-v1`): its
  `generation_pins` are exactly `{generation, generation_marker}`, because `materialization.json` does not exist yet.
  Kind `dispatch` (`wlscratch-attempt-dispatch-v1`): its `generation_pins` are exactly `{generation,
  generation_marker, materialization, materialization_marker}`, and it adds `adoption` `{record, marker}`, the
  committed adoption record W read at D3. Both kinds: W's identity and invocation, the lease identity, the channel
  genesis, the front-process triple read by W from `/proc` as the grandparent of W through S1 (§9.2, used by W2), the
  boot id and the verb and arguments. Each binds nothing that does not yet exist.
- **`fallback-allocation.json`**: the immutable descriptor of the attempt's fallback journal (§10.4).
- **`inputs/<seq>-lead-module`** and **`inputs/<seq>-process-attributes`** (P_att, `dispatch` only): the streamed lead
  module and F's process attributes (§8.3).
- **`front/front-identity.json`, `front/front-stage-<stage>.json`**: F's identity and its stage halves (stages
  `parent`, `vault`, `child`, `after` for `dispatch`; `vault` for `materialize`).
- **`writer-half-parent.json`, `writer-half-child.json`**: W's own halves of the parent stage (D8) and the child stage
  (C4).
- **`observer-intent-<n>.json`**: committed before each observer start, after its stream files exist: O's argv (with
  its nonce) and RL's argv, the stage, the `[dev, ino]` of `observer-<n>.stdout` and `observer-<n>.stderr`.
  **`observer-<n>-<stage>.json`** and **`observer-wait-<n>.json`**: O's results (stages `parent`, `after`, `recover`)
  and S_O's wait. **`launcher-rl-identity.json`** and **`observer-<n>-rl-identity.json`** (the latter also under
  `w2-<k>/`): RL's `RL_IDENTITY` frame (§7.3, §9.3 G3), committed before W sends `GO`, or its first `OBSERVE_REQUEST`,
  to the helper RL started.
- **`launch.json`** (v5 schema plus): `generation`/`attempt` pins; the pin of the admitted parent observation (§4.2
  D11; files, directories, identities and every excluded generated leaf's `stat_key`, §4.5); the view specification
  (§12.2: the namespaces and their owners, the maps, the binds and the run-path rule, the Landlock rules, the seccomp
  program, the credentials) and its sha256; `process_attributes` (§8.3); the target environment, which is v5's (§8.4);
  the exact RL, L and C argv templates; the stream-file names; the unit name; the front stage-record pins. v5 fields kept
  unchanged in meaning: `action`, `args`, `child_argv`, `cwd` (the view's run path), `directory_identities` (run = g,
  attempt, source, snapshot, `source_tree`), `unit`, `scope_argv_template` (RL's `systemd-run --scope` template),
  `scope_argv_tail`, `environment`, `frame_inventory`, `review`, `adoption` (the descriptor of the protected adoption
  record, §4.6), `materialization`, `storage_reserve_bound`, `holder`. The run-path mode (`bind` or `skeleton`) is
  decided by RL from the copied namespace and reported in `RL_IDENTITY`, not fixed in advance.
- **`reservation-intent.json`, `reservation.json`** (v5 fields: `at`, `token`, `launch`, `prior`, `holder_task`,
  `candidate`; `current`) plus the window-lock identity F observed under the lock and the F request message digest.
- **`admission.json`** (v5: `memory_gate`, `reservation`, `launch`) plus the Gate 0 receipt pin (D10), the front
  stage-record pins, the O parent-stage record pin and the writer-half pins. It is the complete create-only
  admission/launch record: written after every input, the reservation and the memory gate.
- **`launcher-intent.json`** (v5: `scope_argv`) plus RL's argv and the L argv (with `launch.json` and
  `admission.json` sha256 and the W↔L nonce `n_wl`), the C argv with its nonce `n_c`, the view specification's
  sha256, the stream files as a list of `{name, dev, ino}` read from the descriptors W already holds (D14), and the
  attempt-journal head. It is the launch intent: committed after the stream files exist and before any launcher
  process can exist (§9.3).
- **Launch, child and conclusion records** (`launcher-start.json`, `launcher-wait.json`, `sudo-launcher-wait.json`, the
  `child-*` records, `effective-limits.json`, `spawn-ok.json`, `stream-finality.json`, `result.json`, the release
  records, `final-status.json`, `conclude-errors.json`, `refusal.json`): Appendix B.3.
- **W2 and recovery records** (`w2-<k>/identity.json`, `w2-<k>/recovery/scan-<r>.json`,
  `w2-<k>/recovery/result.json`, the release records and observer files of a recovery under `w2-<k>/`,
  `w2-<k>/front-terminal.json`): §9.7.
- **Export increments and captures** (`export/<A>/inc-<n>/manifest.json`, `freeze.json` and the copies; the generation
  export with its payload pack; `export/capture-<A>/` with `capture-manifest.json`): §15.3.
- **Adoption records** (`invocations/<stamp>/invocation.json`, `lead-adoption.json`): §4.6.

No sealed record is ever rewritten. Later facts go into new records (for example the input manifest, the admission
record, `final-status.json`, `conclude-errors.json`), never into an earlier one.

### 4.4 Anchors and joins

- Channel genesis: `head0(dir) = SHA256("wlscratch-channel-v1" ‖ 0x00 ‖ dir ‖ 0x00 ‖ N)` for each direction `dir` of
  each channel, where N is the nonce in the argv of the helper the channel serves: F↔W and F↔W2 use `N_F` (directions
  `F2W`, `W2F`); W↔L uses `n_wl` (`W2L`, `L2W`); W↔C uses `n_c` (`W2C`, `C2W`); W↔O and W2↔O use `n_o` (`W2O`,
  `O2W`). F knows `N_F` because it chose it; W reads it from its own argv, which `sudo` also reports in
  `SUDO_COMMAND`; W chooses `n_wl`, `n_c` and `n_o` and puts them in the argv of L, C and O. Each helper's first
  message carries its own fresh nonce and the first reply echoes it, so both nonces are bound into both chains by the
  first messages (§7.3).
- Every record carries `generation`, `attempt` (or `null` for P_adm and P_ado records), `boot_id`, the current heads
  of both directions of its invocation's channel, a writer-local `record_seq`, and `prev_commit` (§10.2). Committed
  records form hash-linked journals: the generation journal (`g/commits/`, P_adm, final after M8); one attempt
  journal per attempt (`g_rec/attempts/<A>/commits/`, for P_att and P_exp, appended to by W and then by each W2 of the
  attempt in turn); and one adoption journal (`P_ado(I)/commits/`) (§10.2; the frame plan's H-M4 journal).
- Joins required before launch: `attempt.json` → generation pins equal the committed `generation.json` and
  `materialization.json` markers, and its `adoption` pin equals the committed adoption record; `launch.json` →
  `attempt.json` pin, the O parent-stage observation pin and the adoption descriptor; `reservation-intent.json` →
  `launch.json` pin (v5); `admission.json` → launch and both reservation pins (v5) plus the Gate 0 and stage pins;
  `launcher-intent.json` → launch and admission pins and the stream identities; L's and C's argv → the sha256 of
  `launch.json` and `admission.json` (v5 V4-B03 seal); C → the bytes it received over its channel hash to those
  values, and the stream descriptors it received have the bound identities.
- F's expectations join W's records through the channel: every `*_COMMITTED` message carries the record descriptor
  `{path, sha256, bytes, mode}` and the marker digest, which F keeps in memory (§7.5).
- **No original join is relaxed.** Appendix D lists every v5 admission, child, conclusion and adoption join with the
  role and state in which v4 performs it.

### 4.5 Where the final pass is, exactly [corrections: W1-V6-INVARIANTS, W1-V6-SCAN-STATE]

The **final admission boundary** is C's last full walk, inside the scope and the view, immediately before the spawn:

1. C performs v5 `verify_materialization` over the view's `source/` with v6's final pass: every encountered leaf,
   recorded or excluded generated, is re-stat'ed by name without following and must keep its complete `stat_key`, and
   every directory is re-reached with unchanged metadata (`scratch.py` v6 :554, :569-573). That final pass is the
   criterion-required repair of V5-B01, not part of v5's behaviour (§21 separates them). Through the bind's idmap M_run
   (on-disk W shown as 1000) C is the owner of every entry below `source/` (§12.2), so it opens every file and
   directory it reads with `O_NOATIME` (§9.8 N6).
2. The observation (files, directory modes, identities and every excluded generated leaf's `stat_key`) must equal the
   admitted parent observation sealed in `launch.json` exactly (§4.2 D11). A difference in any recorded or excluded
   leaf refuses the launch. (v5 compared directory identities only; the excluded-leaf comparison is the criterion's
   addition and an engine change to `observe_tree`, which must return the excluded leaves' keys it already computes.
   Against v5 this comparison is a new refusal; under §9.8's custody nothing but root, W and the attempt's own frame
   helpers can change the generation between the two walks, so it fires only if a premise of §9.8 N7 failed or one of
   those misbehaved, §21 R2.)
3. Then C takes the child-stage observations of §9.4 (its scope holds exactly C; every other RL scope in
   `user-1000.slice` is absent or `populated 0`) and re-verifies the location of its held handles.
4. **Run-path alias check.** C resolves the run path `<RUNS>/<label>/source` and the `TMPDIR` path from `/` component
   by component (`openat2` with `RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS`, `O_PATH|O_DIRECTORY`) and requires each
   result to be the root of the corresponding bind (`statx` `STATX_ATTR_MOUNT_ROOT`, `stx_mnt_id` with
   `STATX_MNT_ID_UNIQUE` equal to the bind's ID in `launcher-rl-identity.json`, `[dev, ino]` equal to the sealed
   identity). It also requires the same of every absolute path in T's environment that lies below the run path
   (`PENDING_LIBRARY_DIR`, `PENDING_OBJECT_DIR`, `PYTHONPATH`, `WORLDLINE_CORE_LIB`, as far as each exists). A failure
   is a pre-launch alias and refuses (RP1), as v5 refused a run directory its location chain did not reach. Then C
   reaches the interruption point (pending-signal check) and spawns with `fchdir` on the held `source` descriptor (v5
   `spawn`).

This pass follows (a) the frame's last mutation of P_adm(g) (M8, at generation creation; there is no later frame
mutation of `source/` or of any directory above an admitted entry), (b) the commit and delivery of every record C's
admission depends on (`launch.json`, `admission.json`, `launcher-intent.json`, `launcher-rl-identity.json`, the
adoption record) and (c) the `SPAWN_OK` of §9.3. Every frame write after it goes to P_att(g, A) or P_exp(g):
`child-start.json`, waits, the conclusion, the capture. Those partitions are disjoint from P_adm and the partition
contents, lie under a record root the target cannot reach (§12.2), and the target never reads them. **So "the final
pass runs after the last frame mutation of the admitted generation" is exact, and the remaining frame writes are
bookkeeping by construction, not exceptions.**

Custody from the final pass to `exec` (V5-B01, second sentence) rests on these facts, each with its own section:
(i) no principal outside the attempt's own process tree, other than root and W, holds a usable reference to, or a
usable name for, an admitted entry, and none can obtain one (§9.8 N0-N3);
(ii) W does not mutate P_adm after M8, and any other writer instance refuses before its first mutation and before
starting any helper while W holds the lease (§5.1, §5.2);
(iii) every process whose user namespace is a U8 descends from an RL stage-2 process inside a new RL scope (premises
P-SETNS and P-CG), and no process can hold capabilities over a U8 except root and RL's exited helper (premise
P-NOOWNER);
(iv) at the final pass, by C's own observations, the attempt scope holds exactly C and every earlier RL scope is absent
or `populated 0`;
(v) by §9.8 N4, each earlier scope's holder event H has occurred and is absorbing, so no earlier holder can act before
T's `exec`; outside principals have neither path, reference nor channel (i); C is frame code;
(vi) root and the kernel are outside the threat model.
This is an argument for review, not evidence; its kernel premises are listed with their probes in §9.8 N7.

### 4.6 The fresh installed-frame adoption record [correction: W1-GENERATION-PROTOCOL]

**Writer and destination.** The only writer is W, executing the reviewed `adopt` verb of the installed frame, started
by F (`front.py adopt …`) through S1 under the reviewed `sicarii`→`wlscratch` rule. The only destination is
`/var/lib/wlscratch/runs/records/adoption-<I>/lead-adoption.json` (P_ado(I), inside T), written create-only, with its
marker in `adoption-<I>/commits/`, where I is the sha256 of the installed `frame-inventory.json`. No other process,
verb or path can create it: only W can write R_root (§6.3), W's mutation list names this path for `adopt` only
(§5.2), and `adopt` refuses if `lead-adoption.json` is present in any state, committed or not (v5 S:821 "adoption
already recorded"). Nothing is written into the frozen source tree, the installed frame or `/home/sicarii`.

**Why there, and not in a review directory.** v5's `adopt` wrote `FRAME/review/lead-adoption.json`, where FRAME was the
executing frame's own directory. For W-1 the executing frame is the root-owned, member-exact installed tree, which
neither F nor W can write and which must contain no extra entry (§11.6). Writing the record into the lead-owned frozen
source tree would be a frame-owned write without enforced location custody (V5-B02). Inside T the write has the same
enforced custody as every other frame record, and it is no longer an outside-tree write at all.

**What the record binds** (`wlscratch-lead-adoption-v2`, Appendix B.3; §23): every key of v5's
`claude-scratch-frame-lead-adoption-v5` record (`at`, `frame` = INSTALL_ROOT, `lead_id`, `frame_inventory_sha256` = I,
`review_sha256`, `review_freeze_sha256`, `review_report_sha256`, `mismatches` = `[]`, v5's provenance keys for the
code review (`reviewer_thread`, `rollout`, `turn_contexts`, `session_providers`, `exec_argv`, `exec_argv_record`,
`event_stream`, `rollout_final_message_sha256`, `rollout_final_timestamp`), `lead_observation`, `truth_boundary`), plus
`source_frame` (SOURCE_FRAME), `setup_identities_sha256` (S) and `installed_review` (the same review, freeze, report
and provenance keys for INSTALLED_REVIEW); for a Claude-subagent review the provenance keys are the §23.4 set
(`review_freeze_sha256`, `raw_final_message_sha256`, `reviewer_agent_id`, `reviewer_task_output_sha256`,
`reviewer_kind`, `different_from_author`), selected by `reviewer_kind` (§23, B.3).

**Joins at adoption** (none of v5's is dropped; the installed-review joins are added):
1. Code review (REVIEW): v5 `review_profile_problems` against the compiled `REVIEW_PROFILE`, with `candidate` =
   SOURCE_FRAME (the frozen tree it reviewed), `lead_id` = `LEAD_ID`, `frame_inventory_sha256` = I, `report_sha256`
   and the three sidecar pins; v5 `rollout_join` (freeze roster and member identities, `actual_model_selection`
   gpt-6.1-sol and `different_from_author`, exactly one thread and one rollout, model, cwd = REVIEW, provider, final
   message and its timestamp, the reported digests, an actual gpt-6.1-sol max-effort exec argv).
2. Installed-evidence review (INSTALLED_REVIEW): the same rollout join, and the compiled installed-review profile with
   `candidate` = INSTALL_ROOT, `frame_inventory_sha256` = I, `setup_identities_sha256` = S and the installed-evidence
   pins it reviewed.
   Both joins 1 and 2 are the review-provenance join of §23.4, selected by `reviewer_kind`: the gpt-6.1-sol
   `rollout_join` as stated for a GPT-6.1 review, or the sealed-freeze / `raw-final-message.txt` / reviewer-agent-id /
   task-output-sha256 join for a Claude-subagent review (§23); a review of neither recognized form refuses.
3. Member exactness: the installed tree equals the frozen inventory member by member (§11.6), so the installed frame
   executing `adopt` is the frame REVIEW reviewed. This is how v5's single join "`candidate` equals the executing
   FRAME" is preserved when reviewed bytes are installed elsewhere: the code review binds SOURCE_FRAME and I, and the
   installed review binds INSTALL_ROOT, I and S.
4. The fresh lead observation `scratch-adopt` with `candidate` = INSTALL_ROOT, `check_observation`, and v5
   `validate_adoption_observation`: schema, stage, candidate, authority profile, identity profile, start
   instruction, observed transcript prefix of the append-only transcript, goal records and goal commands in that
   prefix, liveness, and ordering after the completion of both reviews and before the adoption time.

F performs all of 1-4 in the lead context (it can read the review directories, `~/.codex/sessions` and the transcript;
W cannot). W then re-verifies, over the bytes F streamed, everything that does not need the lead context: the
lead-module pin, both review profiles, both freeze rosters and member digests, both review-provenance joins (§23.4,
selected by `reviewer_kind`) except the uniqueness of the GPT rollout file among `~/.codex/sessions` (which only F can
list, and which it reports as an observation; for a Claude-subagent review there is no such rollout file, and its
place is taken by the sealed task-output sha256 and reviewer agent id, which F reports and W re-verifies), the
observation's structural profile and time ordering, and that the adoption body equals what those
inputs determine. Verified bulk inputs that do not become records are retained in the channel segments by reference
(§7.3). This is v5's trust for joined inputs and observations (R2), with W's independent structural check added.

**Consumers.** At every dispatch: W requires the committed record and marker (D3) and binds them in `attempt.json`; W
streams the bytes to F (D6), and F's frame admission front part re-runs v5 `frame_admitted`'s adoption checks against
them at the parent and child stages (provenance re-pin, rollout re-join, adoption-observation re-validation, review
pins); `launch.json`'s `adoption` is the record's descriptor; W delivers the bytes to C, which requires their sha256 to
equal `launch.json`'s `adoption` (v5 child, S:1814-1815). `materialize` does not use the adoption record, as v5
`materialize` did not call `frame_admitted`.

**Exports.** The adopt invocation exports the record to `adoption-<I>/export/inc-<n>/` with the export ACL (§15.3), so
the lead and reviewers can read it; the original stays in P_ado(I).

**A failed adoption commit.** If `lead-adoption.json` was written but its marker was not committed, the record is raw
evidence (§10.1): dispatch refuses (not adopted), and a new `adopt` refuses because the name is present, exactly as v5's
`adopt` refused when its file existed. Resolution is an explicit operator decision; no verb removes or replaces the
record.

## 5. Lease, writer authority and entrypoint closure [corrections: W1-IMAGE-TREE, W1-TERMINAL-CUSTODY; gap: lease-and-writer-authority]

### 5.1 `writer.lock`: creation, checks, use

**Creation (setup script S-B, §11.5).** As root, in a freshly created root-owned directory:
`install -d -o root -g <W> -m 0750 /var/lib/wlscratch/lease`, then
`touch /var/lib/wlscratch/lease/writer.lock && chown root:<W> … && chmod 0440 …`, then a check that
`stat -c '%F %h %s %u %g %a'` prints exactly `regular empty file 1 0 0 <W> 440`. Only root can create, replace,
rename or chmod either object, because the directory is root-owned and not writable by its group, and the file is
root-owned.

**Checks at every writer invocation, before any mutation** (all through descriptors, no pathname re-resolution):
1. Anchor `/var/lib/wlscratch/lease` from `/` component by component with `O_DIRECTORY|O_NOFOLLOW` (v5 `Dir.anchor`);
   each ancestor's `[dev, ino]`, owner and mode must equal `setup-identities.json` (`/` and `/var` and `/var/lib`
   root:root 0755; `/var/lib/wlscratch` root:<W> with the ACL of §6.3; `lease` root:<W> 0750 with no ACL xattr).
2. `openat(lease_fd, "writer.lock", O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK)`; `fstat` must show `S_ISREG`,
   `st_nlink == 1`, `st_uid == 0`, `st_gid == W`, mode 0440, `st_size == 0`; `fgetxattr(…, "system.posix_acl_access")`
   must fail with `ENODATA`; `fstatat(lease_fd, "writer.lock", AT_SYMLINK_NOFOLLOW)` must name the same `[dev, ino]`;
   and `[dev, ino]` must equal the value in `setup-identities.json`.
3. `flock(fd, LOCK_EX|LOCK_NB)`. `EWOULDBLOCK` → refuse before any mutation (W writes nothing, reports on its stderr
   to F, exits non-zero). Any other error → refuse the same way.
4. The descriptor stays open for W's whole life and is never passed on (`O_CLOEXEC`; every child is spawned with
   close-on-exec descriptors only). The lock is released when W exits.

**No byte write.** `flock` needs no write access and changes neither content nor metadata, the descriptor is
read-only, and the file is root-owned 0440. The lease therefore causes no frame mutation outside g, so no
outside-tree classification is needed. Because the lock inode is root-owned in a root-owned directory, the frame
plan's N07 "stable cooperating lock inode" ceiling does not apply to the writer lease. It still applies to the shared
window lock, which is unchanged (§9.4).

### 5.2 What the writer may mutate (the complete list) [corrections: W1-V6-INVARIANTS, W1-V6-COMMIT-AMBIGUITY; v4: W1-IMAGE-TREE]

Every row lies inside T (§3.4), reached through §3.4's anchors, in both storage configurations.

| Verb | Mutation (create-only new names) | Where | When | Parent writable by |
|---|---|---|---|---|
| `adopt` | P_ado(I) with `commits/` and `invocations/` (first `adopt` of I only); `invocations/<stamp>/**` (identity, channel segments); `lead-adoption.json`; the adoption journal's markers; `export/inc-<n>/**` and their ACLs | R_root (P_ado) | AD3-AD6 | W only |
| `materialize` | g (no ACL), `g/commits/`, `generation.json` and its marker | T_root and g | M4 | T_root: W only; g: W only |
| `materialize` | inputs, snapshot, recipe files/directories/modes, `tmpdir/`, `materialization.json`, their markers | g (P_adm) | M6-M8 only | W only (recipe directories are 0755 owned by W) |
| `materialize` | g_rec, its ACL, `attempts/`, `attempts/<A0>/**` (records, markers, fallback journal and its slots, allocation descriptor, front records, channel segments); `export/generation/**` with its payload pack and `export/<A0>/inc-<n>/**`, with their ACLs | R_root and g_rec (P_att, P_exp) | M4-M11 | W only |
| `dispatch` | `attempts/<A>/**` (records, markers, fallback journal and its slots, allocation descriptor, inputs, stream and observer files, front records, channel segments); `export/<A>/inc-<n>/**` and `export/capture-<A>/**` with their ACLs | g_rec (P_att, P_exp) | D3-D19 | W only |
| `seal-front` (W2, either mode) | `attempts/<A>/w2-<k>/` (k the smallest unused) and new names only below it: identity, channel segments, observer files and records, recovery records, release records, the front terminal record; markers appended to A's attempt journal; `export/<A>/inc-<n>/**` and, if W did not make it, `export/capture-<A>/**`, with their ACLs | g_rec (P_att, P_exp) | §9.7 | W only |
| `selftest` | sacrificial `selftest-<h>/**` under T_root and under R_root | T | selftest | W only |

Nothing else. In particular W writes nothing in `lease/` (§5.1), nothing below `source/` after M8 and nothing in
`tmpdir/` after M7 (W never renames, changes or deletes an entry there; it reads them only for the complete capture,
after the holder event), nothing outside T (so nothing in `/home/sicarii`, the installed frame, the shared window file or
`/tmp`), and creates no named temporary file anywhere: a record or marker that W creates with `O_TMPFILE` has no name
until its create-only `linkat` (§10.2), and an unlinked `O_TMPFILE` inode disappears with its last descriptor. No verb
renames, deletes, truncates, chmods or re-ACLs an existing object. A writer instance that cannot take the lease refuses
before any mutation and before starting any helper (S2, S_O), so while one writer holds the lease no other can start
RL, a launcher or an observer. Post-run work (conclusion, captures, exports, recovery, release records, the front's
terminal record) is in the table: every one of those writes goes through a W-exclusive parent inside T.

**W2's capability.** W2 (`writer.py seal-front <N_F> <g> <A> <mode>`) takes the lease like any writer and may only
create new names under `attempts/<A>/w2-<k>/`, append markers to A's attempt journal and create export increments
and, if missing, the complete capture of A. It verifies its capability before writing: W2 reads `/proc/<W2's
parent>/stat` (the S3 sudo process) and `/proc/<S3's parent>/stat`, and the latter's `(pid, start_time_ticks)` together
with the current boot id must equal the front-process triple committed in `attempt.json`. A different `sicarii`
process cannot satisfy that, because the kernel assigns pids and start times. In mode `recover`, W2 additionally
requires the triple of the attempt's writer (from `attempt.json`'s `writer`) to be absent or reused (§9.7). W2 never
modifies an existing record.

### 5.3 Entrypoint closure [corrections: W1-V8-WRITER-AS-W, W1-V6-SCAN-STATE]

A process can carry a given uid or gid only through: inheritance from a process that already has it; a privileged
credential change by root or by a holder of `CAP_SETUID`/`CAP_SETGID`; executing a set-user-ID or set-group-ID file;
executing a file with file capabilities; or user-namespace mapping, which `newuidmap`/`newgidmap` permit only within
`/etc/subuid`/`/etc/subgid` and which otherwise needs root. The table closes each route for each new identity. "Check"
means a setup prestate or verification item (§11.3, §11.6) and, where marked, a per-invocation check by the frame.

| Route | `wlscratch` (W) | `wlscratch-ns` (N) |
|---|---|---|
| sudo | only rule yielding W: the S1 rule `sicarii ALL=(wlscratch) NOPASSWD: WLSCRATCH_W` (§11.5 S-D). The operator inventory shows that **no sudoers rule of any principal** resolves its Runas set to W through `ALL`, a group (`%group`), a uid (`#uid`), an alias or a negation without a password, and that no rule lists W in a user or Runas list except the S1 rule. A1 can therefore run `writer.py` as W with any arguments; what that process can reach is stated in §9.8 N2 | the operator inventory shows that **no sudoers rule of any principal** resolves its Runas set to N through `ALL`, a group, a uid, an alias or a negation, and that no rule lists N in a user or Runas list (P12); the RL rule runs RL as root, and RL gives N only to its own short-lived helpers, which run RL's code, create one namespace and exit (§12.2 step 10) |
| user manager | no linger; the frame rules set `!pam_session` (§11.5), so sudo opens no PAM session and `pam_systemd` does not run for W; probe P-NS verifies that no `user@W.service` and no `/run/user/W` appear | no session of any kind: RL's helper is a plain `fork` of RL; no `user@N.service` and no `/run/user/N` ever exist (probe P-NS) |
| sshd (active: observed `ActiveState=active`) | `DenyUsers wlscratch wlscratch-ns` drop-in (§11.5 S-E); home root-owned, so no `authorized_keys` can be planted; no userdb record with keys (`userdbctl`) | same drop-in; the home named in `passwd` (`/var/lib/wlscratch-ns`) does not exist and its parent is root-owned |
| login, getty, display manager | shell `/usr/bin/nologin`, password locked | same |
| PAM account controls | `sudo` uses `system-auth` (`pam_unix` account, `pam_time`) for the invoking user; login services (`system-login`) add `pam_access`, `pam_nologin` and `pam_shells`; the locked password makes every password authentication fail; account expiry (`usermod -e 1`) is applied only at rollback, because sudo must still reach W while installed (observed stacks, P10) | the same locked password and `nologin`; N is never a sudo target, so it is expired at setup (`usermod -e 1` in S-A), which closes every PAM account route at once |
| `su`, `runuser` | `su` needs the target's password (locked); `runuser` is root-only (`pam_rootok`) | same |
| polkit, `pkexec`, `run0`, `machinectl` | require admin authentication (`unix-group:wheel`, interactive); the operator inventory shows **no polkit grant to any subject** (not only `sicarii` or a group it is in) for unit management or exec-as-user that could yield W (for example a `systemd-run`/`systemctl` action with `--uid=wlscratch` or a `org.freedesktop.systemd1.manage-units` allow); `empower` empty | same |
| cron, at | not installed: `/usr/bin/crontab`, `/usr/bin/at`, `/usr/bin/batch` absent, cronie and atd not found, no spool directories (observed 2026-10-04); re-checked at setup and by W at every invocation (absence of those paths) | same |
| system units, D-Bus system services | no unit or D-Bus service file references W (operator `grep -r` inventory of `/etc/systemd`, `/usr/lib/systemd`, `/usr/share/dbus-1`, `/etc/dbus-1`); the transient scopes RL creates in `user-1000.slice` are runtime objects of the system manager and run as 1000 | none references N |
| setuid/setgid files and file capabilities | none owned by W (operator `find / -xdev \( -uid W -o -gid W \)` empty before and, apart from setup objects, after); no untrusted code ever runs as W | none owned by N: N owns no file at all (S-I: `find / -xdev \( -uid N -o -gid N \)` empty) |
| user namespaces | W is outside every subordinate range; no range is allocated to W | N is outside every subordinate range; RL maps N into no namespace (U8's identity map shows N as N, but no process inside U8 has it: RL sets 1000 before L exists, and nothing in a view can set its uid, P-NOCAP) |
| existing processes | none at setup; afterwards only W instances (S1/S3 children) | none ever, except RL's helper during the creation of one namespace (RL's root scan, §12.2 step 5, requires that no other process has uid N) |
| capabilities over a U8 (the owner rule of commoncap) | none: W does not own U8 (§9.8 N2) | a process with euid N in the initial namespace would hold every capability over every U8; only RL's helper ever has that euid, and it runs RL's code and exits before L exists (premise P-NOOWNER) |

**P-NOOWNER / P-W route inventory (obligation, W1-V9-NOOWNER-SCOPE).** The inventory discharging the `sudo` and
`polkit` rows above must be shown over **every** principal, not only `sicarii` and not only rules that literally name
W or N: for each of W and N, there is no sudoers rule of any user or group whose Runas set resolves to the identity
through `ALL`, `%group`, `#uid`, a `User_Alias`/`Runas_Alias`, or a negation; and no polkit authority (rule, pkla, or
compiled action default) grants any subject a passwordless path to manage a unit or exec as the identity. This states
what must be shown; §16.1 O-1 carries the operator-produced evidence, and §13.2 S-5/E0 reads the frame's own
non-reliance on any such route.

### 5.4 Subordinate-ID exclusion

Observed `/etc/subuid` and `/etc/subgid` (identical): `sicarii:100000:65536`, `cosmov1lab:165536:65536`,
`wlrehearsal:231072:65536`, `wldrill:362144:65536`, `worldline:296608:65536`. Every new uid and gid must lie outside
every listed range and no range may be allocated to a new identity. That keeps `sicarii` (and every other user) from
mapping them through `newuidmap`/`newgidmap`. Policy, checks and the post-setup re-check are in §11.2.

## 6. Modes, ACLs and access paths [corrections: W1-IMAGE-TREE, W1-COMMIT-JOURNAL-EXPORT, W1-SETUP-PROBES-ROLLBACK; gap: per-entry-modes-acls]

### 6.1 The v5 recipe and record modes are preserved exactly [correction: W1-V6-INVARIANTS]

v5 semantics (S:308-327, 913, 995-1026, 1992): the process umask is 077; `write_bytes` creates with 0600 and then
`fchmod`s to the requested mode (default 0600, so every JSON record and stream is 0600); created directories are
authenticated at 0700; the overlay snapshot keeps 0600 files in 0700 directories; recipe directories are created 0700
and then set to their base directory mode, deepest first, the root last; recipe files are written with their row's
mode (the base inventory mode, or 0644 for a new overlay unit).

W-1 keeps every one of these. **The frame sets no ACL on any recipe object, frame record, snapshot entry, stream file,
marker or journal, and no default ACL anywhere**, so the umask 077 semantics apply exactly as in v5 to everything W
creates. The partition contents and the target temporaries carry whatever modes and ACLs the target gives them, as in
v5, where the target could set access and default ACLs on what it owned; the frame never sets, changes or removes one
there, and v7 has no copy that would reproduce one (v6's copied ACLs are withdrawn with the copy route). Through the
M_run idmapped bind (uid/gid `W 1000 1`), a target process cannot `chgrp` an entry below `source/` to a supplementary
group and cannot set an ACL entry naming an id other than 1000; an unmapped id appears as the overflow id. This is an
observable change against v5 (where the target could set such group ownership and ACL entries), listed as the OPEN row
**V16** (§12.3, §21.3); it is not a new refusal by rule, only the idmap's effect, and it is recorded, not narrowed
(W1-V9-INVENTORY).

Recipe-mode property, observed on the pinned base (inventory `943ea95e…3bf`, directory modes `1049c831…bde`): 635
files, 617 with mode 0644 and 18 with mode 0755 (617 + 18 = 635, JACKAL exact, parsed `617+18`); 55 directories, all
0755. Overlay units take a base mode or 0644. Every recipe file is therefore others-readable and every recipe
directory others-readable and others-searchable. W records this as `recipe_mode_property` at M7. It is not a new
refusal of an accepted case: for the pinned base it holds row by row, and a base with other modes would be a
different pinned base, which is itself a reviewed change.

### 6.2 Why ACLs never touch a mode that is recorded [correction: W1-V6-INVARIANTS]

POSIX ACL semantics (acl(5)): a named-user or named-group entry requires a mask entry; `stat` reports the mask in
the group bits of `st_mode`; `chmod` rewrites the mask. A named entry on a 0600 file therefore shows as 0640 or 0620
and changes the observed mode. A default ACL on a directory replaces the umask for new entries (their ACL is derived
from the default ACL and the creating mode), so a default ACL inherited "under 0600" does not give the promised read
access and silently changes creation semantics. The frame therefore puts ACLs only on objects whose modes are not part
of the recipe or of any v5 record, and puts no default ACL anywhere:
- setup objects `/var/lib/wlscratch`, `runs/` (T_root) and `runs/records` (R_root);
- the record root g_rec (created 0700, authenticated at 0700 by `Dir.child(create=True)`, then given its ACL; v5
  records no mode for its run directory); the generation root g gets none;
- the adoption roots `adoption-<I>`;
- export directories and export files, which are new writer-produced copies whose final mode, after the ACL, is the
  one their export marker records (§15.3).
v6's ACLs on pre-created partition roots and on `/home/sicarii` (Option A) are withdrawn. A mode or ACL that the target
sets on its own objects is the target's behaviour, recorded by the walks as v5 records it, and never the frame's.

### 6.3 Per-object owners, modes and ACLs

ACLs are written by W through `fsetxattr(fd, "system.posix_acl_access", …)` on the held descriptor (POSIX ACL xattr
version 2 encoding; entries sorted by tag then id) and read back with `fgetxattr` plus `fstat`; a mismatch refuses.
Setup ACLs are written by `setfacl` as root and read back with `getfacl -n`. "W" is a numeric id; `1000` is `sicarii`.
N owns no object and appears in no ACL.

| Object | Owner:group | Base mode | Access ACL (`getfacl -n` order) | `st_mode` shown | Default ACL |
|---|---|---|---|---|---|
| `/var/lib/wlscratch` | root:W | 0750 | `user::rwx user:1000:--x group::r-x mask::r-x other::---` | 0750 | none |
| `lease/` | root:W | 0750 | none | 0750 | none |
| `lease/writer.lock` | root:W | 0440 | none | 0440 | n/a |
| `runs/` (T_root) | W:W | 0700 | `user::rwx user:1000:--x group::--- mask::--x other::---` | 0710 | none |
| g | W:W | 0700 | none: only W and root can search it | 0700 | none |
| `runs/records` (R_root), g_rec, `adoption-<I>` | W:W | 0700 | `user::rwx user:1000:--x group::--- mask::--x other::---` | 0710 | none |
| `generation.json`, `materialization.json`, `inputs/**`, `commits/**` of g | W:W | 0600 files, 0700 dirs | none | same | none |
| `overlay-snapshot/**` | W:W | 0600 files, 0700 dirs (v5) | none | same | none |
| `source/` and every recipe directory | W:W | recipe mode (0755 for all 55 observed) | none | same | none |
| recipe files | W:W | recipe mode (0644 or 0755 observed) | none | same | n/a |
| partition contents (created by the target through its view) | on disk W:W, because the run-path bind's idmap M_run stores the target's 1000:1000 as W:W (§12.2); the target sees them as 1000:1000 | as the target leaves them (umask 077 from the frame, v5); the frame never changes a mode | none set by the frame; the target may set entries | as the target leaves it | none set by the frame; the target may set one |
| `tmpdir/` | W:W (seen in the view as 1000:1000, like v5's `TMPDIR`) | 0700 at M7; afterwards as the target leaves it | none set by the frame | as the target leaves it | none set by the frame |
| contents of `tmpdir/` (target temporaries) | on disk W:W through M_run (§12.2) | as the target leaves them | as the target leaves them | as the target leaves it | as the target leaves it |
| `attempts/**` (records, markers, `fallback.journal`, stream and observer files, `w2-<k>/**`); `adoption-<I>/commits/**`, `invocations/**`, `lead-adoption.json` | W:W | 0600 files, 0700 dirs | none | same | none |
| `export/` of g_rec and of `adoption-<I>`, and every directory below them (the payload packs and `capture-<A>/` included) | W:W | 0700, then the ACL | `user::rwx user:1000:r-x group::--- mask::r-x other::---` | 0750 | none |
| export files (the payload packs and the capture copies included) | W:W | 0600 at creation, then the ACL | `user::rw- user:1000:r-- group::--- mask::r-- other::---` | 0640, the final mode the export marker records (§15.3) | n/a |
| `/opt/wlscratch`, `/opt/wlscratch/frame-v6w1/**` | root:root | 0755 dirs, 0644 files | none | same | none |
| `/opt/wlscratch/setup-identities.json` | root:root | 0644 | none | 0644 | n/a |
| image roots (images only, §14.5): the work image root seen at `runs/`, the records image root seen at `runs/records` | as `runs/` and `runs/records` above | | | | |
| bare mount points (images only; visible only while unmounted) | root:root | 0700, empty | none | 0700 | none |
| `/var/lib/wlscratch-images` (images only) | root:W | 0750: W and W2 list and search it and compare its exact entry set at every use (§3.4, §11.7); nobody but root opens the image files | none | 0750 | none |
| the image files in it (images only) | root:root | 0600 | none | 0600 | n/a |
| `lost+found` of each image root (images only; made by `mkfs.ext4`; never used, opened or walked by the frame) | root:root | 0700 | none | 0700 | none |

Because the target's host uid is the lead's 1000, the `user:1000` search and read entries that serve the lead (on
`/var/lib/wlscratch`, `runs/`, `runs/records`, g_rec, `adoption-<I>` and the exports) apply to the target exactly as to
every other `sicarii` process. g, the records originals and `lease/` carry no entry for 1000, so the target reaches T
only as `sicarii` does, plus its two binds.

### 6.4 Access paths

- **The target reaches its generation only through its two binds** (§12.2): `source/` at the original run path and
  `tmpdir/` at the original `TMPDIR`, both idmapped by M_run, under which it owns every entry, as it owned its run tree
  and its `TMPDIR` in v5. Everything else of T it reaches only as `sicarii` does (§6.3): search on the ancestors, read
  on the exports, nothing in g. It creates its output partitions itself, as in v5, and writes its stream files through
  descriptors it was given.
- **C and O** read through the same binds, as owners of every entry, with `O_NOATIME`. A target-created object that its
  owner cannot read (for example mode 0000) yields an observation failure and a non-success outcome, v5's own
  readability rule. Everything C needs from the records tree reaches it over its channel (§9.3 C2).
- **The writer never opens a target-created object while a task of the attempt can exist.** Its own walks cover the
  recipe and skip the output partitions. After the attempt's holder event (§9.8 N4) it reads the whole generation, as
  owner on disk, with `O_NOATIME`, only to make the complete capture (§15.3).
- **The lead reads evidence from P_exp and the adoption exports**, through the `user:1000` entries (§6.3).
- **Every other non-root principal** falls to `other::---` below `/var/lib/wlscratch`.
- **Partition roots**: as in v5, created by the target (S:1033); v6's ROOTS hypothesis is not needed.

### 6.5 Denial matrix (each cell is a probe in §13)

| Object | `sicarii` processes outside views (A1, including A1's `writer.py` as W only where W's column says), and view processes outside their binds | other non-root principals (A3) | view processes through their binds | W |
|---|---|---|---|---|
| `/var/lib/wlscratch`, `runs/`, `runs/records`, g_rec, `adoption-<I>` | search only | none | n/a | read, search (owner of all but `/var/lib/wlscratch`, which it reads and searches by group) |
| `lease/`, `writer.lock` | none | none | n/a | search; open read-only and `flock` |
| g, P_adm records, `inputs/`, snapshot, `commits/` | none | none | n/a (not reachable) | full (owner) |
| recipe and partition entries below `source/` | none | none | owner through M_run | owner on disk; reads only after H (§6.4) |
| `tmpdir/` and its contents | none | none | owner through M_run (the view's `TMPDIR`) | owner on disk; reads only after H |
| P_att and P_ado originals | none | none | stream bytes only through passed descriptors | full (owner) |
| P_exp and adoption exports | read | none | read (as `sicarii`) | full (owner) |

In every cell marked "none", "read" or "search", every mutation (create, `mkdir`, `unlink`, `rmdir`, `rename` in or
out, `link`, `symlink`, `open` for write, `truncate`, `chmod`, `chown`, `setfacl`, `utimensat`) must not succeed. The
expected errno of each probe cell is derived per probe from its exact operand and the first check that fails: a
missing search permission on an ancestor gives `EACCES` during path resolution; a create, unlink, rename or symlink in
a directory the actor can search but not write gives `EACCES`; an open for writing, a `truncate` or a `utimensat`
without explicit times on a reachable file the actor cannot write gives `EACCES`; `chmod`, `chown`, an ACL `setxattr`
and `utimensat` with explicit times by a non-owner give `EPERM`; a hard link of another owner's file that the actor
cannot both read and write gives `EPERM` (`fs.protected_hardlinks=1`). A `link` or `rename` whose two paths resolve to
different mounts gives `EXDEV` only if path resolution and every earlier check succeed, and Landlock's `EACCES` takes
precedence over its own `EXDEV` (installed `landlock.h`); §13 therefore states, per probe, whether the operands are
same-mount (then the permission errno is expected) or cross-mount with fully permitted resolution (then `EXDEV`), and
the custody claim uses only "does not succeed". The frame's walks refuse any symlink, special file and multiply linked
regular file, as the original walk does (S:531, S:554); they refuse no set-ID leaf and no device boundary.

## 7. Channels, expectations and dumpability [correction: W1-GENERATION-PROTOCOL; gap: channel-and-dumpability]

### 7.1 Channels and transports

| Channel | Transport | Created by | Carries |
|---|---|---|---|
| F↔W and F↔W2 | three pipes: F→W on W's fd 0, W→F framed messages on W's fd 1, W→F diagnostics on W's fd 2 | F, after its first act; F's ends close-on-exec | inputs, observations, requests, answers, record descriptors |
| W↔L | `AF_UNIX`/`SOCK_STREAM` socketpair SP_L on L's fd 0 (passed through S2 and RL); L's fd 1 and fd 2 are `launcher.stdout`/`launcher.stderr` in P_att, created by W before `launcher-intent.json` binds them | W | RL's `RL_IDENTITY`, then `GO` with record bytes, `FDS` with three descriptors by `SCM_RIGHTS` (SP_C's end, `scope.stdout`, `scope.stderr`), `LAUNCHER_START` (L's last message: it then `exec`s C, and SP_L closes with the `exec`), `STOP` |
| W↔C | socketpair SP_C: W keeps one end and passes the other to L in `FDS`; L moves it to fd 0, and the received `scope.stdout` and `scope.stderr` (W-created) to fds 1 and 2, before it `exec`s C | W | child stage, record bytes (`RECORDS`, which includes the committed `launcher-rl-identity.json`, §9.3 C2), `STREAMS` with the child stream descriptors by `SCM_RIGHTS`, `SPAWN_REQUEST`/`SPAWN_OK`, child records, waits, `STOP` |
| W↔O and W2↔O | socketpair SP_O on O's fd 0 (passed through S_O and RL); O's fd 1 and fd 2 are `observer-<n>.stdout`/`.stderr`, created before `observer-intent-<n>.json` binds them | W or W2 | RL's `RL_IDENTITY`, then observation requests and results, report bytes |

`sudo` passes only fds 0-2 (its default `closefrom` is 3), so every helper gets exactly one bidirectional socket on
fd 0 and two W-created files on fd 1 and fd 2; further descriptors travel only by `SCM_RIGHTS`, and only from W to its
helpers. W reads every socket with `recvmsg` and a zero-length control buffer, so a descriptor that L, C or O sends is
truncated by the kernel (`MSG_CTRUNC`) and never installed in W, and W records a channel failure. L never reads or
writes SP_C: C's messages reach W directly, so the W↔C chain is end to end. RL sits between S2 and L, and between S_O
and O; it passes the helper's fds 0-2 through unchanged, closes every other descriptor (§12.2), and before its `exec`
it writes exactly one `RL_IDENTITY` frame on fd 0, on a direction of its own (§7.3). T receives only `/dev/null` and
the two child stream files; no socket of any channel reaches T.

### 7.2 Canonical encoding and framing

- **Frame**: an 8-byte unsigned big-endian length `n`, then `n` payload bytes, `1 ≤ n ≤ MAX_FRAME`,
  `MAX_FRAME = 67108864` (JACKAL exact, parsed `64*2^20`).
- **Payload**: the canonical JSON of an object with exactly the keys `body`, `kind`, `prev`, `seq`:
  `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)`, encoded as ASCII.
- **Strict decoding**: ASCII only; `json.loads` with hooks that reject floating-point numbers (`parse_float`),
  `NaN`/`Infinity` (`parse_constant`) and duplicate keys (`object_pairs_hook`); nesting depth at most 32; every number an
  integer with absolute value below 2^63; and the payload must equal its canonical re-encoding byte for byte.
- `seq` counts from 0 per direction; `prev` is 64 lowercase hex; `kind` must be allowed in the current protocol state;
  `body` must have exactly the key set and types of the kind's schema (Appendix B.4).
- **Bulk bytes** (input files, record bytes delivered to C, report bytes from O) travel as `BEGIN {name, size, mode,
  sha256, chunks}`, then `chunks` × `CHUNK {index, data_b64}` of at most `CHUNK = 4194304` raw bytes each (JACKAL
  exact, parsed `4*2^20`), then `END {sha256}`. The receiver checks index order, count, size and sha256. Base64 of a
  full chunk is at most 4·(CHUNK+2)/3 bytes, leaving 61516456 bytes of `MAX_FRAME` for the envelope (JACKAL exact,
  parsed `67108864-4*(4194304+2)/3`). Inputs of any size are streamed in chunks and never refused for size. An
  over-length header can only come from a non-conforming sender and is a protocol violation, not an input-size refusal.
- **Observation results and record bytes are bulk bytes.** Front stage results, observer results, relayed child
  records and receipts travel as `BEGIN`/`CHUNK`/`END` carrying their own JSON encoding (v5 `write_json` form), so the
  strict envelope rules (for example, no floating-point number) constrain only control bodies and never the content of
  a v5 observation (v5 observations contain floating-point fields such as `transcriptSilenceSeconds`). The receiver
  parses bulk JSON with the v5 readers after the digest check.

### 7.3 Chain initialization, validation and retained form [correction: W1-V6-EVIDENCE-RESTORE]

- `head0(dir)` is defined in §4.4. The receiver of message k of a direction requires `seq == k` and
  `prev == head_k`, then sets `head_{k+1} = SHA256(bytes.fromhex(head_k) ‖ payload_k)`. The prototype implements the
  same recurrence (ENGINEERING_ONLY).
- The first message from the helper side of each channel (`W_HELLO`, `W2_HELLO`, `L_HELLO`, `C_HELLO`, `O_HELLO`)
  carries that process's own fresh 64-hex nonce and its identity; the first message of the other direction
  (`HELLO_ACK`, `GO`, `RECORDS`, `OBSERVE_REQUEST`) echoes the nonce. Each side refuses a hello whose identity fails
  §8.1's joins. A writer that refuses before its hello sends `EARLY_REFUSAL` as its first message instead; it carries
  no nonce, gets no reply, and the channel then ends (Appendix B.4.4). Likewise an L whose G4 checks fail sends
  `L_REFUSAL` as the first message of its own direction (after RL's frame), and a C whose C1 checks fail sends
  `CHILD_REFUSAL`; neither carries a nonce or gets a reply (§9.3, Appendix B.4.4).
- **RL's frame.** The first frame on the W↔L and W↔O sockets is RL's `RL_IDENTITY`, the only message of the direction
  `RL2W`, whose genesis is §4.4's `head0("RL2W")` computed with the nonce of the helper RL serves (`n_wl` or `n_o`); the
  helper's own `L2W` or `O2W` chain then starts at seq 0 with `L_HELLO` or `O_HELLO`. W verifies the frame (§9.3 G3)
  and commits it before it sends `GO` or its first `OBSERVE_REQUEST`. A missing or second `RL_IDENTITY` is a channel
  failure.
- **Bulk carriers.** A bulk transfer is allowed only immediately after a control message whose schema declares a
  `bulk` list (Appendix B.4); the sender must then send exactly one `BEGIN`/`CHUNK`/`END` sequence per listed name, in
  the listed order, before any other message in that direction. Anything else is a channel failure (§7.4).
- **Retained form.** W retains its channels as create-only segment records `channel/<channel>-<first-seq>-<last-seq>.json`
  (in `attempts/<A>/` for W, in `w2-<k>/` for W2, in `invocations/<stamp>/` for `adopt`), written at every state
  boundary of Appendix B.4.4 and at conclusion, each with a marker. A segment holds, per message, `{dir, seq, prev, kind,
  length, payload_sha256}` and the payload, except that bulk chunk data is replaced by a reference: `{record, offset,
  length, sha256}` to the committed record it became; `{written, offset, length, sha256}` to the P_adm recipe or
  snapshot path its bytes were written to; or, for the verify-only inputs of `adopt` (§4.6), `{source, offset, length,
  sha256}` naming the sealed lead-tree path F read. **Every reference resolves inside the exports** (correction
  W1-V6-EVIDENCE-RESTORE): a `record` reference names a record whose export copy the increment cut of §15.3 covers; a
  `written` reference names a recipe or snapshot path whose bytes the generation export's payload pack carries (§4.2
  M9); and a `source` reference names a verify-only input whose bytes `adopt` exports in the adoption increment's
  payload pack (§15.3). A verifier with nothing but the exports reconstructs every payload and recomputes both chains.
  If W dies, messages after the last committed segment are durability-UNKNOWN (§10.5); records still carry the heads.
- F writes nothing; it keeps both heads in memory, and its terminal record (committed by W2) carries them.

### 7.4 Rejection rules

- EOF at a frame boundary in a state that permits it (after `BYE`, or the states so marked in Appendix B.4) is a clean
  end.
- Everything else is a **channel failure**: EOF inside a frame or in any other state; `n == 0` or `n > MAX_FRAME`;
  non-ASCII, non-canonical, duplicate-key, floating-point or non-finite payload; wrong key set; `seq` out of order;
  `prev` not the current head; a kind not allowed in the state; a body schema mismatch; a chunk index, count, size or
  sha256 error. The receiver stops reading that channel, retains the raw bytes of the failing frame (if any) as a raw
  record, never acts on a later message and proceeds by §9.5.
- Deadlines: only v5's own, at v5's points: 300 s first byte and 30 s completion for an answer line; 30 s per
  subprocess observation. W-1 adds none. A peer that dies closes its end, and the receiver sees EOF (a channel failure,
  §9.5); a peer that is alive but slow is waited for, as v5 waited for a slow frame operation. The lead's interrupt of F
  closes F's channel ends, which every later receiver sees as EOF. Before launch an EOF refuses with nothing reserved or
  launched, as applicable; after launch it never stops the wait for participants.

### 7.5 In-memory expectations (the v5 admission protocol's, carried)

| Expectation | Held by | Compared with |
|---|---|---|
| challenge (each memory challenge, and the Gate 0 receipt challenge of §14.3) | W: the pin of the `challenge.json` it committed and the expression it issued | the answer's `challenge_sha256`; the receipt row's `parsed`, `status`, `formal`, `exact`; no receipt hash reused within the attempt (v5 S:1195-1248) |
| lead | F and W: `claude_lead.LEAD_ID` (W from the verified lead-module bytes); C: the same, from the lead-module bytes W delivers, verified against the compiled pin | every front observation's `leadId`, the window `holder_task`, `launch.json` `holder` (v5) |
| window | F: token, holder, candidate path, the reservation record descriptors W returned | `owns_window` under the window lock; the release rule (§9.4, v5) |
| argv | F: W's and W2's exact argv; W: S2/RL/L, S_O/RL/O argv, the scope and C templates; W2: its S_O/RL/O argv; C: its own command line against its compiled template (§9.3 C1) and, after `RECORDS`, against the sealed one (C2) | `/proc/<pid>/cmdline` read by the parent role, `SUDO_COMMAND`, C's `/proc/self/cmdline` (v5 S:1786-1791) |
| records | W: every marker it wrote (the journal head and the committed set); F: every descriptor it was sent | the attempt-journal join of §10.6: every committed record unchanged; the fallback journal by its allocation descriptor and slot prefix, never by a content digest; drift is an error |
| exports | W: each increment's manifest and freeze descriptors with their final values (mode 0640, ACL); F: the freeze-marker digests from `EXPORTED` and `FINAL` | F re-reads every export copy through its ACL and compares with the manifest's final values (§15.3) |
| adoption | W: the committed adoption record and its marker (D3); F and C: the bytes W delivered | F's frame admission front part; C's `launch.adoption` join (§4.6) |
| streams | W: the `[dev, ino]` it bound in `launcher-intent.json` | L's and C's checks of the descriptors they receive (§9.3) |
| participants | W: S2, RL, L, C, T, O identities (§9.1); W2: its S_O, RL and O; F: S1, W, S3, W2 and the participants reported to it | the observations and classifications (§9.4) |

No re-read local record defines its own expectation (v5 V4-B03 rule).

### 7.6 Integrity is not sender authentication

The chain shows that the receiver saw exactly the ordered bytes written by whoever holds the other end, with no loss,
reordering or alteration in transit. It does not show who that is. For F, the other end of the W pipes is the process
F started: F created the pipes after becoming non-dumpable, kept its own ends close-on-exec, and requires W's reported
`fstat` of fds 0-2 (`S_ISFIFO`, `[dev, ino]`) to equal its pipe inodes. For W, the other end is "the `sicarii`
process that invoked `sudo` and kept the pipe", which W cannot distinguish from any other `sicarii` process. The lead
is therefore authenticated only by the original v5 joins (§2.4 R2). W-1 makes them neither weaker nor stronger, and
this is the original v5 engineering ceiling, not a newly accepted residual.

### 7.7 Dumpability: set, read back, when

- **First act.** Each entry script (`front.py`, `writer.py`, `launch_target.py`, `sandbox_launch.py`) begins, before
  importing anything but `sys` and `ctypes`: `libc = ctypes.CDLL(None, use_errno=True)`;
  `libc.prctl(4, 0, 0, 0, 0)` (`PR_SET_DUMPABLE`, 0) must return 0; `libc.prctl(3, 0, 0, 0, 0)` (`PR_GET_DUMPABLE`) must
  return 0; `os.stat('/proc/self/fd').st_uid` must be 0 (the kernel makes a non-dumpable process's `/proc/<pid>`
  entries root-owned; `os` is already loaded by interpreter start-up, so binding it loads nothing new). On any failure
  the process writes one line to stderr and exits 125 with no other action. Both readbacks go into its role identity
  (§8.1). `/proc/self/status` has no `Dumpable` field on this host and is not used.
- **Relative to start-up.** Before the first act come: the dynamic loader, `libpython` initialization, the encodings
  import, `site` (for F including the user site directory and its `.pth` processing; for the `-I` helpers only the
  system site), and `import ctypes` with its own imports. Only then the two `prctl` calls, then the `sys.flags` checks
  of §8.2, then every other import.
- **Each invocation.** `execve` resets the attribute (to 1 when the credentials do not change in the exec), so every
  process sets it itself: F, W, W2, RL, L, C (after L's `exec`), O. T does not (R3).
- **Pre-first-call residual, per role.** F (uid 1000) is readable by every `sicarii` process until the call: its
  environment, command line and inherited descriptors (Yama still blocks attach). Its channel pipes are created after
  the call and are never exposed. W and W2 are readable only by other `wlscratch` processes (frame writer instances)
  and root. RL runs as root. L, C and O run with the lead's host uid inside a U8: before their call, a process outside
  their U8 cannot read them, because every ptrace-mode access from another user namespace needs `CAP_SYS_PTRACE` in
  theirs (§9.8 N2); inside their U8 nothing else exists before C's spawn call. Their non-dumpable setting is therefore
  defense in depth, not the reason for their closure. Their stream files are W-owned 0600 and their channel sockets
  cannot be reopened through `/proc`. The window's duration is not measured; probe P-DUMP timestamps it. This residual
  is stated, not accepted as a new guarantee.

## 8. Fresh identities, the real outer invocation, the original context and the vault [gap: fresh-identities-and-vault]

### 8.1 Per-invocation role identity

Every process of every invocation records a fresh `wlscratch-role-identity-v2` (Appendix B.1) immediately after its
first act (§7.7). It contains: role; boot id; pid, ppid, `start_time_ticks` (field 22 of `/proc/self/stat`); comm;
argv (`/proc/self/cmdline`); exe (`readlink /proc/self/exe`, `[dev, ino]`, sha256); all four uids and gids and the
supplementary groups (`/proc/self/status`); capability sets, `NoNewPrivs`, `Seccomp` and `Seccomp_filters`; both
dumpability readbacks; umask; resource limits; cgroup (`/proc/self/cgroup`); mount, pid, user, network and cgroup
namespace inodes; cwd `[dev, ino]`; for fds 0-2 the file type, `[dev, ino]`, mode and open flags, and the full list of
open fds; the environment as sorted names plus the sha256 of every value, with clear values only for the non-secret keys
`HOME USER LOGNAME LANG PATH SHELL PWD TMPDIR XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS INVOCATION_ID SUDO_USER SUDO_UID
SUDO_GID SUDO_COMMAND` and every `PYTHON*` key; Python `sys.version`, `sys.executable`, prefixes, every `sys.flags`
field and `sys.path`; and the loaded module closure (every `sys.modules` entry with a file: name, path, size, sha256;
builtin names listed). Processes inside a view (L, C, O) also record `/proc/self/uid_map`, `gid_map` and `setgroups`
and the owner of their user namespace (`NS_GET_OWNER_UID`); because U8's maps are the identity, their
`/proc/self/status` shows the host ids. The parent role independently reads the child's
`/proc/<pid>/{stat,status,cmdline,cgroup}` from the initial user namespace and joins them with the child's self-report
(pid, start time, credentials, command line); a mismatch refuses before launch and is an error after.

Per stage, in addition (each a fresh observation, never reused across stages or attempts):

| Role | Parent stage | Child stage | After (conclusion) |
|---|---|---|---|
| F (real lead context) | fresh lead observation `scratch-run`; frame admission front part; base-tree re-observation; v5 runtime-closure observation with the original spec against the original baseline (compact if equal, v5 item 4); `systemctl --user show-environment` of `sicarii`'s manager against the original `manager_environment` baseline; sibling units of v5's `sample` (no unit allowed, because the frame's scopes are not in `sicarii`'s manager) and `storage_status.py` | the same set with stage `scratch-child`, and the window ownership check | the same set except the lead observation, as v5 conclusion re-ran frame admission and identities |
| W | own identity against the reviewed writer-context baseline (system standard library only, `-I` flags); the manager census M (§9.4) | lease, location, snapshot, record-drift writer half; the manager census M | same, plus v5's terminal predicate (§9.4) |
| O (in its view) | full walk; tool, proof-data, proof-ELF, vendor and runtime-closure observations with v5's own specifications (the source relocated to the run path exactly as v5 relocated it) against the original v5 baselines; heavy processes and meminfo; the kernel census K (§9.4) | n/a | same as parent, plus the report bytes |
| C (in the view) | n/a | v5 child admission in full (§9.3 C1-C11), with the same observations as O, the kernel census and the final pass; the manager environment is F's half (C4), because no process of the view can reach `sicarii`'s manager | n/a |

### 8.2 The real non-isolated outer invocation is kept

The front is the lead's real outer invocation and keeps the original shape: `/usr/bin/python3 -B
/opt/wlscratch/frame-v6w1/front.py <verb> …`, with no added `-I` (HANDOFF.md:177: "Retain the real non-isolated outer
invocation (no added -I)"). F requires `sys.flags.isolated == 0`, `ignore_environment == 0`, `no_user_site == 0`,
`safe_path == 0`, `optimize == 0`, `dont_write_bytecode == 1`, and that `sys.executable` resolves to
`/usr/bin/python3.14` with the reviewed digest. F's runtime and manager observations use the original specifications
and baselines, because F runs in the original `sicarii` context. The helpers (W, W2, L, C, O, RL) run with `-I -B` and
require `isolated == 1`, `optimize == 0`, `dont_write_bytecode == 1`. The frame plan's H-M7 ("every verb runs -I") is
applied to helpers only. Helper observations are additional; none replaces F's. The inherited bootstrap ceiling (N08:
`site`, `.pth` and cached state before main) applies to F unchanged.

### 8.3 The original target command, environment, limits and process attributes [corrections: W1-V7-FULL-DOMAIN, W1-V8-HOLDER-IOEXIT]

- `child_argv` is exactly v5 `command()` (S:1054-1070), executed by path (R4); the view shows it at the same path, in
  the same object, because the view's root is a copy of the host's mount table with no idmap (§12.2).
- **Process attributes.** In v5 the target inherited the frame's attributes through `systemd-run --user --scope`,
  which runs the command in the caller's context, and v5 changed only the cwd (`fchdir`), the umask (077, S:1992),
  `RLIMIT_CORE` (0, 0) and the signal mask (S:1508-1517). In v9 the chain F → sudo → W → sudo → RL would otherwise
  substitute root's and sudo's values, so F records its own values (D1, D5) and RL applies them to its stage-2 process
  before L's `exec`; L, C and T inherit them. C reads every one back before the spawn (C6) and the parent observation
  records them.

| Attribute | v5 source | v9 reproduction |
|---|---|---|
| uid, gid (real, effective, saved, fs) | the lead (1000, 1000) | `setresgid`, `setresuid` to 1000 inside U8, whose identity map makes the host ids 1000 (§12.2 step 14) |
| supplementary groups | the lead's | `setgroups` to F's recorded list |
| capability sets | the lead's (all zero for a uid-1000 process; bounding set as inherited) | permitted, effective, inheritable and ambient zero (the `setresuid` rule); bounding set equal to F's recorded `CapBnd` (RL drops only what F's lacks); no securebits set |
| `no_new_privs` | 0 | 0 |
| seccomp | none | RL's one filter (§12.2 step 13b): `io_setup` and `io_uring_setup` return `ENOSYS`, every other system call is allowed; `/proc/self/status` shows `Seccomp: 2` and `Seccomp_filters: 1` (§12.3 V14) |
| every resource limit (soft and hard) | the lead's, `RLIMIT_CORE` set to (0, 0) by v5 | F's recorded values for every `RLIMIT_*`, then `RLIMIT_CORE` (0, 0) |
| nice value, scheduling policy and priority, I/O priority | the lead's | F's recorded values (`setpriority`, `sched_setscheduler`, `ioprio_set`) |
| CPU affinity | the lead's | F's recorded mask (`sched_setaffinity`); if CPUs of that mask have gone offline since F recorded it, the kernel's own intersection applies, as it would have to the lead's process, and the difference is recorded, not refused (§21 C9) |
| `oom_score_adj` | the lead's | F's recorded value, written by RL (root may lower it) |
| umask | 077 (v5) | 077 |
| environment | v5 `specifications()` | identical (§8.4) |
| cwd | `fchdir` to the source directory | `fchdir` to the held bind root of g/source |
| signal mask and dispositions | v5 `spawn`: handled signals unblocked before exec, dispositions default after exec | identical (C9) |
| session, process group, controlling terminal | the lead's session; no controlling terminal is assumed by v5 | the RL and S1 sudo rules set `!use_pty` (§11.5), so no pseudo-terminal or new session is created by sudo; the target's session and process group are those of the chain's last session leader, recorded and listed in §21 C9 as a difference if they are not the lead's |
| personality, timer slack | the lead's | F's recorded values (`personality`, `PR_SET_TIMERSLACK`) |
| cgroup, memory limits | user-manager scope in `app.slice`, `MemoryMax=8G`, `MemorySwapMax=0` | system-manager scope in `user-1000.slice` with the same two limits and the properties below |
| namespaces | the host's | U8, the copied mount namespace, a private network namespace; host IPC, PID, UTS, time and cgroup namespaces |

- **Scope properties.** `systemd-run --scope --slice=user-1000.slice --unit=<U> -p MemoryMax=8G -p MemorySwapMax=0
  -p LogLevelMax=warning` plus, from the concrete inventory, the original scope's effective `CPUWeight`, `IOWeight`,
  `TasksMax`, `OOMPolicy`, `ManagedOOMSwap` and `ManagedOOMMemoryPressure` values (read at setup from `sicarii`'s
  manager defaults, read-only, P28). The hierarchical limits of the original ancestors `user@1000.service` and
  `app.slice` cannot be reproduced on a scope outside them; on 2026-10-05T15:51:43Z `app.slice` had `memory.max`
  25769803776 (24 GiB), `memory.high` 21474836480 (20 GiB) and `memory.swap.max` 17179869184 (16 GiB) (JACKAL exact,
  parsed `25769803776/2^30`, `21474836480/2^30`, `17179869184/2^30`, v8 Appendix H), shared by every member of
  `app.slice`, and `user@1000.service` and `user-1000.slice` had `memory.max` `max`, `user-1000.slice` `pids.max`
  84514. The shared `app.slice` budget is therefore a remaining difference (§21 V10'); the `user-1000.slice` limits
  apply as in v5, because the scope lies below it.
- `MIN_MEM_AVAILABLE_KB = 16777217`, `MAX_CHALLENGES = 3`, v5's 300 s and 30 s receipt deadlines and its 30 s
  observation timeouts are unchanged; the target executable's digest is checked before the spawn (v5 S:1839-1841).
- W-1 adds no `no_new_privs` and no capability change beyond what the namespace rule implies; its one seccomp filter is
  V14. What the view itself changes for T is inventoried in §12.3 and §21.

### 8.4 The original context inside the view [correction: W1-V6-PRESERVE]

v6 relocated `HOME`, `USER`, `LOGNAME`, `XDG_RUNTIME_DIR`, `DBUS_SESSION_BUS_ADDRESS` and `TMPDIR`, because its
target ran as another uid in the host's namespaces. v9 relocates nothing beyond v5's own rule. The target is uid 1000
and gid 1000 with the lead's supplementary groups both on the host and inside U8, whose maps are the identity, and the
view shows the host's own mount table, with no idmap except the two binds. The target environment is exactly v5's
`specifications()` result: the `KEEP_ENVIRONMENT` keys `HOME`, `USER`, `LOGNAME` and `LANG` with the lead's values
(observed by F, streamed and recorded); the tool specification's `effective_environment` with v5's relocation of
`PENDING_LIBRARY_DIR`, `PENDING_OBJECT_DIR`, `PYTHONPATH` and `WORLDLINE_CORE_LIB` from the F10K source to the run's
source path; and the runtime specification's environment (`TMPDIR=/home/sicarii/.cache/workflow-tmp`, the `null` keys
removed). The run's source path is v5's own, `<RUNS>/<label>/source` (S:977-999); in the view it is the bind of
g/source.

The original observations compare these rows, which the view reproduces:

| Object | v5 baseline row | In the view |
|---|---|---|
| `TMPDIR` | uid 1000, gid 1000, mode 0700 (runtime closure) | the bind of `g/tmpdir`, seen through M_run as uid 1000, gid 1000, mode 0700 until the target changes its mode, as it could change v5's |
| `/tmp` | uid 0, gid 0, mode 01777 | the host `/tmp`, unchanged |
| `/var/tmp`; `/usr/tmp` | uid 0, gid 0, mode 01777; absent | the host objects, unchanged |
| the run's source (v5's relocation of the F10K row) | uid 1000, gid 1000, mode 0755 | the bind of g/source, seen through M_run as uid 1000, gid 1000, mode 0755 (the recipe root's mode, §6.1) |
| every other path of the tool, proof-data, proof-ELF, vendor and runtime baselines | as recorded | the same object of the host, unchanged |

So O and C compare with the original v5 baselines, unchanged; the only new baseline is the writer-context baseline.
That every original observation taken in the view equals its original baseline is the relation P-VIEW (§9.8 N7); each
run's comparison is evidence for that run only, never a qualification of the design. A difference keeps the full
observation and refuses (v5 `retain_observation`); it would be a defect of the view, to be repaired, never an accepted
case to narrow.

`DBUS_SESSION_BUS_ADDRESS` keeps v5's value byte for byte, and the socket it names is visible in the view (the host's
`/run/user/1000`), but a connection to it fails with `EACCES`, because Landlock denies a connection to every UNIX server
created outside the target's domain (§12.2). The same holds for every other `sicarii` service socket. This is a change,
listed in §12.3 (V2).

### 8.5 Vault scope and the original backup semantics [corrections: W1-V8-EVIDENCE-EQUIV, W1-V7-EVIDENCE-RESTORE]

- **What v5 did**: dispatch ran `project-vault pin <run directory>` and `project-vault status` before launch
  (S:1562-1563). The run directory held every record, the snapshot, the recipe and, after the run, every native output;
  the vault's later snapshots therefore covered the complete run as it then was.
- **What v9 pins**: P_exp(g), `g_rec/export`, and the adoption exports of the bound adoption, by v5's own calls, by F
  as `sicarii`, at M10 and D9, with the authentic HOME, configuration, user bus, reserve and queue. They must succeed or
  the stage refuses, as in v5.
- **What the pinned tree contains** (the equivalent capture): the exports with their payload packs, and for every ended
  attempt A the **complete capture** `capture-<A>/` (§15.3): the whole generation tree (the recipe, every native output
  and partition entry, `tmpdir/`) with every entry's bytes and complete metadata recorded as data; every raw torn or
  uncommitted record and marker of A as bytes; the whole `fallback.journal` file; every channel segment and continuation;
  W2's files; and the sync-provenance attestations (§10.5).
- **The original backup consumers and their equivalence predicates** (correction W1-V8-EVIDENCE-EQUIV). Each consumer
  is named with the question it asked of v5's run directory and the predicate the capture must satisfy:

| Consumer | What it obtained from v5's run directory | Equivalence predicate for the capture |
|---|---|---|
| B1, `project-vault pin` + `status` (registration) | the run directory registered as a vault source; `status` exit 0 | the export tree registered; `status` exit 0 (D9, unchanged calls) |
| B2, a vault snapshot (restic, run by project-vault, later) | every file's bytes and the metadata restic stores (type, mode, uid, gid, times, size, link structure, extended attributes) as of the snapshot | for every entry of the generation and of P_att(g, A) at the capture point: a copy with equal bytes, and in `capture-manifest.json` the original's type, `stat_key`, atime, access and default ACLs, extended attributes and link group; the vault snapshot of the export tree then holds those bytes and that manifest |
| B3, a vault restore to a new directory, and its verification | the restored tree, comparable with the original tree | the restore of the export tree plus `wlscratch-materialize-capture` (a reviewed read-only tool of the frame, run as `sicarii` on the restored tree into a new directory the lead names) reproduces every captured entry's bytes, type, relative path and link structure, and reports every recorded field that a `sicarii` process cannot reproduce (owner W, ctime, inode numbers) as recorded data, not as a restored attribute |
| B4, the lead or a reviewer reading records | the record files in place | every committed record by its export copy; every raw or torn byte by its copy; every payload by the payload packs (§7.3) |
| B5, an offline verifier of chains and digests | recomputation from the run directory | recomputation from the restored export tree alone (§7.3, §15.3), including the provenance attestations |

  Where a field cannot be reproduced by a non-root restore (ownership by W, ctime, inode numbers), v5's own restore as
  `sicarii` could not reproduce v5's values either (restic restores ownership only as root, and never ctime or inode
  numbers); the capture keeps them as data. Whether every consumer's predicate holds is the obligation V-BACKUP (§21
  C1), whose verification run is V-VAULT in §13.2 (step U-14 on a sacrificial export before setup, I-6 after setup on a
  selftest generation). It stays OPEN until that run passes and is reviewed.
- **Consistency of the capture** (correction W1-V8-HOLDER-IOEXIT): it is taken after the kernel census shows U
  `populated 0`; under P-ASYNC no write by a task of U can then still take effect (§9.8 N4); and the capture checks
  itself (§15.3): each file's `stat_key` before and after its copy, and the whole tree's walk before and after, must be
  equal, or the capture is `failed` and is retried once, then reported.
- **Capacity**: the capture's bytes and the full-restore peak enter Gate 0 (§14.3, §14.7). Safe fresh capacity stays
  the original OPEN obligation; no design text establishes it.

### 8.6 Input classes (v2 §6.1 carried; the re-review closed W1-READ-ACCESS)

W reads nothing under `/home/sicarii`. F reads every lead-side input with the v5 anchored readers and streams it.
- **Pinned inputs**, verified by W against values compiled into the installed frame before any use: the three base
  descriptors (`BASE_BINDING_SHA256`, `BASE_INVENTORY_SHA256`, `BASE_DIRMODES_SHA256`, unchanged from v5); every base
  file (digest and size from the pinned inventory); the lead module (`LEAD_MODULE_SHA256`; W executes the verified bytes
  with v5 `exec_verified` only to read its constants and never calls `observe`).
- **Joined inputs**, verified structurally exactly as v5 does, because they postdate the frozen frame: the overlay
  (v5 `overlay_rules`: Ada units under `core/` and `DELETE.list` only; retained by digest in the snapshot); the
  code-review and installed-review rosters with their freeze and provenance records (v5 `review_profile_problems` and
  the review-provenance join of §23.4 — the gpt-6.1-sol `rollout_join` or the Claude-subagent join, selected by
  `reviewer_kind`, and the installed-review profile, with each review's `frame_inventory_sha256` equal to the sha256 of
  the installed `frame-inventory.json`, §4.6).
- **Protected frame records.** The adoption record is no longer a lead-side input: W commits it inside T (§4.6),
  reads it at every dispatch and delivers it to F and C; F's lead-context joins over it are observations at v5 trust.
- **Observations**, recorded with digests at v5's trust (R2): F's lead observation, the review-provenance join (§23.4,
  by `reviewer_kind`) and adoption-observation/transcript-prefix results, base-tree re-observation, window snapshots,
  storage readings, vault results, sibling units, F's runtime and manager observations, and F's identity.

A concurrent `sicarii` change to a home file between F's read and W's use yields the pinned bytes or a refusal for a
pinned input; for joined inputs and observations the trust is v5's. After materialization the admitted copy exists only
in g. No ACL is added for W anywhere under `/home/sicarii`, and the frozen 0600 review files keep their modes.

## 9. Participants, waits, launch gating, terminal ownership and recovery [corrections: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE, W1-GENERATION-PROTOCOL; gap: participants-and-recovery]

### 9.1 Participant set and schemas

Launch participants of attempt A: S2; RL, which becomes L and then C (one pid: RL `exec`s `systemd-run`, which `exec`s
RL's second stage, which `exec`s L, which `exec`s C, §12.2); U; T and all its descendants. Observer participants:
every S_O and its RL/O pid started for A, by W or by a W2, and each observer scope. Post-writer participants: every
S3/W2 of A. F and W are the owner processes (as v5's dispatch and run). Schemas (Appendix B.2):
`wlscratch-participant-v1` `{role, pid, start_time_ticks, boot_id, ppid, uids[4], gids[4], groups, cmdline, cgroup,
observed_by, at, state ∈ {alive, absent,
reused, unknown}}`; `wlscratch-wait-v1` `{waiter_role, waited_role, pid, start_time_ticks, boot_id, raw_status, exited,
exit_code, signaled, signal, core_dumped, wait_error, interrupts, unresolved, at, meaning}`; `wlscratch-scope-v3`
`{manager: "system", unit, invocation_id, control_group, properties_at_start, properties_at_end, populated, cgroup_state
∈ {ABSENT, EMPTY, NONEMPTY, UNAVAILABLE}}`; `wlscratch-census-v2` (§9.4, Appendix B.2). A process is identified by
`(pid, start_time_ticks, boot_id)`: a different start time at the same pid means the original ended and the pid was
reused; a different boot id means the original ended with its boot.

A participant is known only from positive evidence: a committed record or a received message that names its triple,
or an observation that sees it. The absence of a record never shows that a participant does not exist. Whether any
launch participant may still exist is decided only by U's state and v5's terminal predicate (§9.4).

O's jobs per invocation: the census of §9.4; the full walk of the view's `source/` (v5 `verify_materialization` with
v6's final pass, returning every excluded leaf's `stat_key`, every file and directory opened with `O_NOATIME`); the
target-context identities (`parent` or `after`) and the helper half of v5's `preflight` sample (heavy processes,
meminfo); at `after` the report bytes and the observations of v5's terminal predicate; and under W2 the recovery
rounds (§9.7). O writes, renames, deletes and changes no file; its only outputs are its channel messages and its two
stream files.

### 9.2 Waits, reaping and relay

| Waiter | Waits for | Mechanism | Retained as |
|---|---|---|---|
| F | S1, and through sudo's relay W | `waitpid` on S1 (F's child) | front terminal record via W2: S1's raw status, W's self-reported final status (from `FINAL`), and W's `(pid, start)` absent or reused afterwards |
| F | S3 (W2) | `waitpid` | console only. It is the last wait, as v5's lead wait of `dispatch` was |
| W | S2, and through sudo's relay the RL/L/C pid; each S_O (RL/O) | `waitpid` | `sudo-launcher-wait.json` (S2's raw status) and `launcher-wait.json` (the relayed status of the RL/L/C pid; v5 meaning: the actual wait of the pid that `systemd-run` had `exec`ed into the child), `observer-wait-<n>.json` |
| W2 | each S_O (RL/O) it started | `waitpid` | `w2-<k>/observer-wait-<n>.json` |
| C | T | `waitpid` (`wait_blocked`) | sent to W as `CHILD_WAIT`, committed as `child-wait.json` (v5) |

Every wait record is committed before any cleanup (v5 V4-B02 rule). Relay evidence: `sudo` reports the command's
status; whether it re-raises a fatal signal is probe P-RELAY. The parent role always keeps both its direct child's raw
status and the grandchild's self-report; disagreement is an error. Each role reaps only its own children. An orphan
(a child whose parent died) is not waited for by the frame; it stays in its scope, which stays populated until it ends
(§9.4). Handled signals are blocked at the start of every role and consumed only synchronously (frame plan H-S1,
H-M3). `STOP` messages travel down the channels (F→W, then W→L before `GO` and W→C after it), and C forwards `SIGTERM`
to T exactly as v5's `wait_blocked` did. W cannot signal L or C (different uid) and does not try.

### 9.3 Launch gating [corrections: W1-V7-C3-DATA, W1-V6-C1-DATA, W1-V6-SCAN-STATE; v6: W1-V5-PROTOCOL-REFUSALS, W1-V5-REVOCATION-CONFINEMENT; v5: W1-PROTOCOL-FAILURE-STATES, W1-CUSTODY-CLOSURE; v4: W1-GENERATION-PROTOCOL]

- G0. **Bind before start.** Before W or W2 starts any helper through sudo, it creates the helper's stream files
  create-only 0600 (W in P_att, W2 in its `w2-<k>/`), syncs them and their directory, reads each `[dev, ino]` by
  `fstat` on the held descriptor, and commits the record that binds them: `launcher-intent.json` for S2 (D14),
  `observer-intent-<n>.json` for each S_O. Only then is the sudo process started, with exactly those descriptors as
  its fds 1-2.
- G1. W commits `admission.json`, creates and binds the stream files (G0), commits `launcher-intent.json` and sends
  `LAUNCH_INTENT_COMMITTED` with its descriptor.
- G2. F sends `PROCEED_LAUNCH` only if it still owns the window (`owns_window` under the window lock) and has had no
  channel failure; otherwise it sends `STOP`, and W refuses with nothing launched.
- G3. W creates socketpairs SP_L and SP_C (its own ends close-on-exec), starts S2 with fd 0 = SP_L's other end and
  fds 1-2 = the bound `launcher.stdout` and `launcher.stderr` descriptors, reads S2's identity and commits
  `launcher-start.json`. The RL rule's sudo front-end starts RL, which performs §12.2's steps and writes `RL_IDENTITY`
  on fd 0 before it `exec`s L (§7.3). W reads that frame first and verifies it: RL's argv and the seals it checked;
  the scope U (unit, control group `/user.slice/user-1000.slice/<U>`, the censuses RL took before the view, and its root
  scan); the view specification's sha256 equal to the one `launch.json` binds; the namespace inodes and IDs (user,
  mount, network: `/proc/<pid>/ns/*` inode numbers and `NS_GET_MNTNS_ID`); U8's owner (`NS_GET_OWNER_UID`, equal to N)
  and maps (`0 0 4294967295` for uids and gids, JACKAL exact, parsed `2^32-1`); M_run's maps (`W 1000 1` for uids and
  gids) and its owner N; the run-path mode (`bind` or `skeleton`) with, for `skeleton`, the ancestor D, the created
  directories and the re-attached entries; every new mount's ID, root `[dev, ino]` and attributes as `statmount`
  reports them; the root and cwd checks of §12.2 step 12; the Landlock ruleset digest; the seccomp program's sha256 and
  `Seccomp_filters: 1`; and the credentials and capability sets RL holds just before its `exec` (uids and gids 1000 in
  all positions, the groups and the bounding set F recorded, every other capability set zero, `NoNewPrivs: 0`,
  `Seccomp: 2`). W commits `launcher-rl-identity.json`. A missing or second RL frame is a channel failure (Appendix
  B.4.5), after which W sends no `GO`; a frame that fails W's verification makes W send `STOP`. Either way L exits 125
  having started nothing, and W refuses before launch. The same holds for every S_O
  (`observer-<n>-rl-identity.json`, committed before the first `OBSERVE_REQUEST`; on a failing frame W sends `O_BYE`
  instead of a request).
- G4. L: first act, identity, argv grammar; requires uid and gid 1000, a user namespace whose owner is N and whose maps
  are `0 0 4294967295`, `Seccomp: 2`, its cgroup to be `/user.slice/user-1000.slice/<U>` with U derived from its argv,
  fd 0 a socket and fds 1-2 regular files, and its exact open-fd set to be {0,1,2} (no other descriptor open, read from
  `/proc/self/fd`; W1-V9-INVENTORY); sends `L_HELLO`; waits for `GO`. If a G4 check fails, L sends `L_REFUSAL`
  (stage: the failed check) as its first message instead of `L_HELLO` (after RL's frame), or writes the statement to its
  stderr if SP_L does not work, and exits 125 having started nothing. **EOF before `GO` → L exits 125 having started
  nothing.**
- G5. W verifies L through `/proc/<L>` (credentials; `PPid` equal to S2 or to S2's own sudo monitor child, whichever
  P-LAUNCH records for this host's sudo; start time equal to RL's; cmdline; cgroup) and sends `GO` with the bytes of
  `launch.json`, `admission.json` and `launcher-intent.json`, then `FDS` with SP_C's other end and the bound
  `scope.stdout` and `scope.stderr` descriptors by `SCM_RIGHTS`.
- G6. L verifies the two seals (sha256 of the delivered `launch.json` and `admission.json` equal its argv), that
  `launcher-intent.json`'s C argv is exactly what it will run, and that its own fds 1-2 and the received scope
  descriptors have the `[dev, ino]` the intent binds; sets umask 077; reaches its **interruption point**: a
  non-blocking poll of SP_L, where a pending `STOP` makes L send `L_REFUSAL` (stage `stop`) and exit 125 having
  started nothing (any other pending frame is a channel failure with the same effect); then sends `LAUNCHER_START`
  (its identity and the C argv it is about to execute), moves the received SP_C end to fd 0 and the scope descriptors
  to fds 1 and 2 (SP_L and every other descriptor are close-on-exec), and makes its **exec call**: C =
  `/usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/launch_target.py child <n_c> <g> <A> <launch_sha>
  <admission_sha>`, the same pid in the same scope and view, with the environment of `launch.json` and the handled
  signals unblocked across the `exec` (v5 `spawn`; `RLIMIT_CORE` is already (0, 0)). In v5 the launcher started
  `systemd-run`, which `exec`ed the child in place inside the new scope; here RL's `systemd-run` has already placed this
  pid in U, and L's `exec` is that in-place start, so U holds no launcher process, as v5's scope held none. If the
  `exec` fails, L, which still holds SP_L, sends `L_REFUSAL` (stage `exec`) and exits 125: nothing was started. A `STOP`
  that W sent on SP_L and L did not read before its interruption point is lost with SP_L at the `exec`; W, which then
  receives `LAUNCHER_START`, repeats the `STOP` to C over W↔C, and C refuses before its spawn call.
- C1. C: first act, identity. **Only facts available from compiled expectations, its argv and kernel observations**
  (correction W1-V6-C1-DATA): its argv against the compiled `child` grammar (`n_c` 64 hex, g 32 hex, A `STAMP_RE`, two
  64-hex seals); uid and gid 1000; `NS_GET_OWNER_UID` of `/proc/self/ns/user` equal to the compiled N (in the initial
  namespace it is 0, so this distinguishes U8); `/proc/self/uid_map` and `gid_map` equal to the compiled identity line;
  `Seccomp: 2`; its cgroup equal to `/user.slice/user-1000.slice/wlscratch-<g12>-<A>.scope` with g and A from its argv;
  its parent a `sudo` process (the `comm` field of the world-readable `/proc/<ppid>/stat`), as L's was, because L became
  C by `exec`; fd 0 a socket and fds 1-2 regular files, and its exact open-fd set is {0,1,2} (no other descriptor open,
  read from `/proc/self/fd`, not only fd types; W1-V9-INVENTORY). C sends `C_HELLO` to W over SP_C. If a C1 check
  fails, C sends `CHILD_REFUSAL` with `child-refusal.json` as its first message instead of `C_HELLO`, or writes the
  statement to its stderr if SP_C does not work, and exits without spawning; W cannot have sent it `SPAWN_OK` (C8).
- C2. W verifies C through `/proc/<C>` (pid and start time equal to L's, because L became C by `exec`; `PPid` as G5
  found it; credentials, cgroup, cmdline); if that verification fails, W sends `STOP` instead of `RECORDS`, and C
  refuses. Otherwise W sends `RECORDS` (correction W1-V7-C3-DATA): in this exact order, the committed bytes of
  `launch.json`, `admission.json`, `reservation-intent.json`, `reservation.json`, `launcher-intent.json`,
  `materialization.json`, `lead-adoption.json`, **`launcher-rl-identity.json`** and the lead module, each as `{name,
  sha256, bytes, marker}` where `marker` is the descriptor of its committed close marker, together with the attempt
  journal head (Appendix B.4); and then `STREAMS` (`child.stdout` and `child.stderr` by `SCM_RIGHTS`). C requires:
  exactly that key set and order; every sha256 equal to the bytes delivered and to the digest its marker descriptor
  records; `launcher-rl-identity.json` committed (W commits it in G3, before `GO`, so its marker precedes `RECORDS` in
  the attempt journal, and the journal head `RECORDS` carries includes it); the record's pid and start time equal to C's
  own (C is RL's stage-2 process after two `exec`s); the record's view facts equal C's own independent observations
  (§12.2 step 12: namespace inodes and IDs, the root mount's `statx` mount ID and `[dev, ino]`, the binds' IDs, roots and
  attributes through `statmount`, the run-path mode, the seccomp state). After this authenticated delivery and before any
  spawn request, C performs the checks that need the records: its `/proc/self/cmdline` equals the sealed C template of
  `launcher-intent.json` plus its argv items; its environment equals `launch.json`'s; its fds 1-2 and the received child
  stream descriptors have the identities `launcher-intent.json` binds; the lead module against the compiled pin; and
  every v5 child join (S:1782-1817): both seals; `intent.launch` equals the delivered `launch.json` descriptor;
  `admission.launch` equals `intent.launch`; the `reservation.json` token taken from the `admission.json`-pinned record
  (frame plan H-M6) equals the intent's token; `launch.materialization` equals the delivered `materialization.json`
  descriptor; `launch.adoption` equals the delivered adoption record's descriptor. A missing record, an extra or
  reordered key, a digest mismatch, an observation mismatch or any failing check makes C send `CHILD_REFUSAL` (in state
  `RECORDS`, stage `records`) and exit without spawning. No fact that only `RECORDS` delivers is checked before it.
- C3. C opens the view's `source/` at the run path with `O_DIRECTORY|O_NOFOLLOW|O_NOATIME` and requires its `[dev,
  ino]` to equal the seal's source identity, the opened directory to be a mount root (`STATX_ATTR_MOUNT_ROOT`) and its
  `STATX_MNT_ID_UNIQUE` mount ID to be the bind ID named in the delivered `launcher-rl-identity.json`; the same for
  `TMPDIR` and g/tmpdir's identity; the attempt and snapshot identities are checked by W in C4.
- C4. `CHILD_STAGE_REQUEST`. W performs the writer half (snapshot observation equals the record, attempt-directory
  identity equals the seal, the attempt-journal join of §10.6, lease held, location chains unchanged, the manager census
  M of §9.4) and obtains F's child-stage half (§8.1: fresh lead observation `scratch-child`, `owns_window(LEAD_ID,
  attempt path, token)` under the window lock, frame admission front part over the adoption bytes, base-tree
  re-observation, F's runtime and manager identity, the front half of the `child-final` sample with the reserve equal to
  the bound and the sibling units of `sicarii`'s manager with no unit allowed). W commits both halves and sends them to C
  (`CHILD_STAGE_RESULT`).
- C5. C requires `launch.holder == LEAD_ID == intent.holder_task` and window ownership true (v5 S:1809-1811); runs
  the installed-frame inventory check, the target-context identities `child`, and the admission walk with source-tree
  identities equal to the seal (v5 S:1812-1813).
- C6. v5 S:1814-1841 in order: pins (frame inventory, review, adoption, materialization), environment, parent memory
  gate, the helper half of `child-final` (heavy-process refusal, meminfo at or above 16777217 kB; the sibling units are
  F's half), cwd, allowlist re-derivation, limits readback, scope membership, target executable digest; and the readback
  of every process attribute of §8.3 against `launch.json`'s `process_attributes` (a mismatch refuses; it can arise only
  if RL misbehaved or a premise failed).
- C7. Child-stage census (§9.4): U holds exactly C; every other RL scope in `user-1000.slice` is absent or `populated 0`
  (K). Any failure or UNKNOWN refuses (RP1); it can arise only if a premise of §9.8 N7 failed or a frame helper
  misbehaved, and it is recorded as premise evidence.
- C8. `SPAWN_REQUEST` with the digest of C's admission summary. W answers `SPAWN_OK` only if F answered a `PING`
  before EOF, W's error list is empty, the attempt-journal join holds and the manager census M shows no other RL scope
  live, and only after committing `spawn-ok.json`; otherwise W sends `STOP`. `STOP` or EOF → C refuses.
- C9. C prepares T's pre-exec exactly as v5 `spawn`: `fchdir` to the held `source` descriptor, `RLIMIT_CORE` (0, 0),
  then unblock the handled signals. C adds no `no_new_privs` and no filter of its own; RL's filter (§12.2 step 13b) is
  inherited, as every process attribute is (§8.3).
- C10. **Final pass** (§4.5): the walk with `O_NOATIME`; the observation must equal the admitted parent observation;
  then the census K again; `verify_location` of every held handle; the run-path alias check of §4.5 item 4.
- C11. **Interruption point**: the pending-signal check, and a non-blocking poll of SP_C, where a pending `STOP` (the
  only frame W may send in `SPAWN` after `SPAWN_OK`) makes C refuse; any other pending frame is a channel failure, and
  C refuses without spawning. Then the **spawn call**: T with stdin `/dev/null`, stdout/stderr the child stream
  descriptors, the sealed environment, `child_argv`.
- C12. Exactly one outcome message: if the spawn call returned T, `CHILD_START` with T's identity and the bytes of
  `child-start.json`, which W commits (v5) and reports to F (`TARGET_STARTED`); if it failed and `waitpid(-1, WNOHANG)`
  reports `ECHILD`, `SPAWN_FAILED` with the bytes of `child-wait.json` (v5 keys, `started: false`, the error), which W
  commits and reports to F (`TARGET_EXITED` with `started: false`); if it failed while a child of C exists, no outcome
  message: C waits for its children, writes what it knows to its stderr and exits, and `target_started` stays
  `unknown`.
- Then, after `CHILD_START`, C waits for T, sends `CHILD_WAIT` (`child-wait.json`) before cleanup, closes the child
  streams (failures: `CHILD_CLEANUP`), sends `C_DONE` and exits by v5's rule; after `SPAWN_FAILED`, C sends
  `CHILD_CLEANUP` if needed and `C_DONE`. A `STOP` that C reads after its spawn call is forwarded to T as `SIGTERM`
  (v5 `wait_blocked`) or, after `SPAWN_FAILED`, recorded. C's exit status reaches W through S2 (`launcher-wait.json`,
  §9.2).

**C's refusals.** Every refusal by C before its spawn call (C1 before its hello, C2 after `RECORDS`, C3-C11, including
C8's `STOP` or EOF and a `STOP` pending at C11's interruption point) sends `CHILD_REFUSAL` with `child-refusal.json`
(v5 keys, `target_started: false`, v5 meaning "refused before the target spawn; nothing was started") if SP_C still
works, and otherwise writes the same statement to its stderr (`scope.stderr`, raw evidence); C then exits without
spawning. Appendix B.4.4 admits `CHILD_REFUSAL` in every W↔C state before C's spawn call, C's first message included. C
never sends `CHILD_REFUSAL` after its spawn call; a failed spawn call that leaves no child is reported by `SPAWN_FAILED`
with `child-wait.json` and `started: false`, as v5 reported it in `child-wait.json`. **`target_started`** is therefore
`true` if `child-start.json` is committed, `false` only if C's committed `child-refusal.json` or its committed
`child-wait.json` with `started: false` exists, and `unknown` otherwise. W writes `child-refusal.json` only from the
bytes C sent: C's silence, an EOF or a channel failure leaves `target_started` `unknown` (Appendix B.4.5). A missing
`CHILD_START` never means that no target exists, and `unknown` never shortens a classification.

**Why a late launch after writer death is possible only through an issued, recorded permission.** No L can start C
without `GO` (G4), which only a live W sends, and only after `PROCEED_LAUNCH` and the committed launch intent. No T
can start without `SPAWN_OK` (C8), which only a live W sends after committing `spawn-ok.json`. A sudo front-end (S2)
that outlives W can only start an RL and an L, which then reads EOF and exits. So after W's death the only possible
future target is one whose C already holds `SPAWN_OK`; that C is a process of U, which stays populated until C and
everything it started have ended (§9.4), and it either refuses before its spawn call or spawns a T in U. Whether a
launch is still pending is concluded only from U's state and v5's terminal predicate (§9.4), never from a missing
record.

### 9.4 The census, holder state, known-terminal ownership and the release rule [corrections: W1-V8-HOLDER-IOEXIT, W1-V7-HOLDER-STATE, W1-V6-SCAN-STATE, W1-V6-PRESERVE; v6: W1-V5-REVOCATION-CONFINEMENT, W1-V5-PRESERVATION; v5: W1-CUSTODY-CLOSURE, W1-PROTOCOL-FAILURE-STATES; v4: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE]

v7's CRED and P-CENSUS are withdrawn. Two observations and one defined event replace them; nothing assumes that two
observations taken at different moments agree.

**Kernel census K(P).** At a point P an observer reads, from the world-readable cgroup2 hierarchy below
`/sys/fs/cgroup/user.slice/user-1000.slice`, the list of child cgroups whose name matches `wlscratch-*.scope` (RL's
scopes; only root can create a cgroup there, because `user-1000.slice` and its `cgroup.procs` are root-owned, observed
2026-10-05T15:51:43Z), and for each its `cgroup.events` `populated` value and `cgroup.procs`, each process as
`(pid, start_time_ticks, boot_id)`. K passes at P iff each scope that P expects holds exactly the processes the table
gives and every other RL scope is absent or `populated 0`. An unreadable entry makes K UNKNOWN, which refuses before
launch and holds at a classification.

**Manager census M(P).** Taken only by processes outside views (W, W2, F), because a view process cannot reach the
system bus (§12.3 V2): `systemctl show` (read-only) of every `wlscratch-*.scope` unit the system manager lists, with
`LoadState`, `ActiveState` and `SubState`. M passes iff no RL scope other than the expected one is `active`,
`activating`, `deactivating` or `reloading`. This is v5's sibling-unit rule (S:1156-1163) applied to the manager that
now holds the frame's scopes; F's half still applies v5's rule to `sicarii`'s own manager unchanged.

**Race-aware use.** Before launch both are required, each conservatively: a scope that either census shows as live
refuses (as v5 refused on its manager's view alone, and as a populated cgroup is a live scope by the kernel's own
account). No refusal is justified by an assumed equality of the two; §21 D1 lists the one state in which K refuses
where v5's manager-only rule would not (a cgroup still populated while its unit is already reported inactive, which
the systemd source reading says the manager does not produce, premise P-MGR) and keeps it OPEN.

**The holder event H(U)** (corrections W1-V7-HOLDER-STATE, W1-V8-HOLDER-IOEXIT) is defined and argued in §9.8 N4: K
reads U absent or `populated 0`, every task that was ever in U has completed its exit, and no logical mutation of an
admitted entry can take effect afterwards through a reference created by a task of U. Its absorbing property rests on
P-CG, P-SETNS, P-NOOWNER and P-ASYNC; with the view's filter (§12.2 step 13b) no asynchronous write path of a task
outlives the task (§9.8 N4).

| Point P | Observer | K expectation | Also required |
|---|---|---|---|
| parent stage (D8) | RL (stage 1, before O's view), then O | U absent; O's scope holds exactly O; every other RL scope absent or `populated 0` | M by W; RL's root scan; the original walk rules |
| child stage (C7) and final pass (C10) | C | U holds exactly C; every other RL scope absent or `populated 0` | M by W at C4 and C8 |
| after stage (D17) | O, for W | O's scope holds exactly O; U absent or `populated 0` | v5's terminal predicate (below) |
| complete capture (D17, §15.3) | W, from the host (K is world-readable) | U absent or `populated 0` | none: the capture is evidence, not a release condition |
| recovery round (§9.7) | O, for W2 | as at the after stage | v5's terminal predicate |
| release (D18, RC4) | F under the window lock | not taken | v5's terminal predicate only |

**Known-terminal ownership** of attempt A is v5's `owned_terminal` predicate (S:1373-1415), unchanged in meaning and
evaluated over v9's participants: U has ended in the manager (`LoadState` `not-found`, or `ActiveState` `inactive` or
`failed`); its cgroup is absent or empty; every recorded participant pid (L, C, T) is absent from `/proc`; no process
names the attempt (v5 `processes_naming`); the launcher pid is known if a launch was made; no child record is
unresolved. The evaluation is ordered and conservative: manager state, then cgroup, then pids and process names, then
manager state again; terminal only if both manager reads show ended and every other term holds. A manager that lags
the kernel only delays the classification (a hold, exactly as v5 held while its manager reported the scope active);
no instantaneous equivalence is used. W's after stage or W2's recovery establishes it; nothing else is a condition.

**Release rule** (only F; v5's "only the launching parent releases" is kept, because F is the reserving process). F
releases if and only if both hold under the window lock:
1. `owns_window(holder, candidate, token)` (v5, unchanged: status reserved, holder, candidate, token);
2. known-terminal ownership of A has been established by W's after-stage classification or, after W's death or
   channel failure, by W2's recovery (§9.7), and F's own evaluation of the same predicate, taken under the window lock
   immediately before the window write, holds.
Nothing else is a condition. In particular the durability of a record (`release-intent.json`, `window-release.json`,
the conclusion, the observations' own records), the holder event H(U) and the complete capture are not.

**Procedure, all under the window lock** [correction: W1-PROTOCOL-FAILURE-STATES]. F verifies 1 and 2; F sends
`RELEASE_INTENT_REQ`; the serving writer instance (W, or W2 after recovery) tries to commit `release-intent.json`
(primary, retry, fallback, §10) and answers `RELEASE_INTENT_RESULT` with the outcome. F waits for that answer until it
arrives or the channel reports EOF (§7.4). With the answer, or at EOF without it, F performs v5's window write (the
commit point), re-reads the window and sends `RELEASE_DONE`; the writer then commits `window-release.json` (re-read
`released`) or `release-failure.json` (otherwise) and answers `RELEASE_RECORD_RESULT`. A `RELEASE_INTENT_RESULT` that
arrives after F's window write is a late result: it is legal (Appendix B.4.4), F records it in its terminal facts
(`release.intent_result_late`), and it changes and delays nothing. Any outcome other than a committed intent record
makes the attempt durability-UNKNOWN: no success credit, and the uncertainty is reported (console, `FINAL`, and the
front terminal record if it can be committed). It creates neither a hold nor an approval gate (supplied ruling, gpt61-v2
REVIEW.md:230). If the channel reports EOF after `RELEASE_DONE` and before a `RELEASE_RECORD_RESULT`, F treats the
channel as failed after its window write (Appendix B.4.5): writer-death recovery (§9.7) follows, and its `RELEASE`
state finds the window no longer held by this attempt (`RELEASE_NOT_OWNER`, with F's terminal record stating
`release.performed: true`). No archival or durability timeout adds a condition to the release.

**Hold.** F does not release, and the window stays reserved, when 1 fails (F sends `RELEASE_NOT_OWNER`; v5
`NotOwner`; nothing released) or when 2 fails: a live or UNKNOWN participant, an UNKNOWN or failing scan, an
unreadable or reused identity, `terminal_ok == false`, or no complete classification at all (for example W2 or its
observer could not run). F sends `RELEASE_WITHHELD` with the facts so that the writer commits `release-withheld.json`,
and prints them; resolution is explicit and operator-visible; there is no late collector, and no frame verb ever
releases a reservation made by another process. These are the original participant-uncertainty holds and
holder/candidate/token checks; none of them is caused by failed durability.

**Window write failure.** If v5's window write raises, F re-reads the window under the lock: released with this
attempt's token in `release_history` → released, with the error recorded; still reserved by this attempt → not
released, `release-failure.json` (v5 meaning: the window state needs explicit resolution); unreadable → the window
state is unknown, `release-failure.json`, explicit resolution. This concerns the shared window's own state, not record
durability.

The window protocol itself (`window_locked`, `window_read`, `window_write`, `reserve`, `owns_window`, `release`, the
released-status prerequisite, holder/candidate/token joins, history fields, the lock file and its single-link check)
is v5's, unchanged; N07 stays the inherited ceiling for the window lock. The attempt records v5 wrote inside
`reserve`/`release` are committed by the serving writer on F's request, under F's window lock, in the same order
relative to the window commit; for the reservation, as in v5, F writes the window only after `reservation-intent.json`
is committed, because before the window write nothing is reserved and a refusal costs nothing.

**Does the census refuse a case that v5 admitted?** v5 refused while an earlier frame scope was active in its manager
(S:1156-1163). v9 refuses when M shows an earlier RL scope live (v5's rule in the new manager) or K shows one populated.
Whether K ever refuses where M would not is premise P-MGR; §21 D1 keeps that state OPEN.

### 9.5 Failure table [corrections: W1-V6-COMMIT-AMBIGUITY, W1-V6-CATALOGUE; v6: W1-V5-PROTOCOL-REFUSALS, W1-V5-REVOCATION-CONFINEMENT, W1-V5-JOURNAL-FAILED-CLOSE; v5: W1-PROTOCOL-FAILURE-STATES, W1-CUSTODY-CLOSURE, W1-JOURNAL-CONTINUATION, W1-SETUP-IDENTITY, W1-IMAGE-OBSERVATION]

| Event | Behaviour |
|---|---|
| Lease held | W refuses before any mutation and before starting any helper: `EARLY_REFUSAL` (stage `lease`) on its channel and the facts on its stderr; it exits non-zero. F has reserved nothing (reservation is D12). For W2, F retries after its fixed interval (§9.7) |
| A pre-hello check fails, or a record that must precede `W_HELLO` (`generation.json`, `attempt.json`, `fallback-allocation.json`, `invocation.json`) cannot be committed as primary or retry | W refuses before any reservation with `EARLY_REFUSAL`, which lists what it committed; it commits `refusal.json` and an export increment only if `attempt.json` is committed, and F then runs W2 in mode `seal`; otherwise F's terminal facts stay on its console, because without a committed `attempt.json` no W2 can verify its capability |
| `setup-identities.json` does not match its seal (§11.7) | refuse before any mutation: `EARLY_REFUSAL` (`dispatch`; `materialize` when an adoption record exists; `seal-front`); `REFUSAL` at `COMMIT` (`adopt`), after AD3's bookkeeping and before `lead-adoption.json` is written (§11.7) |
| F's identity fails §8.1's joins at `HELLO_ACK` | `REFUSAL` (`adopt`, `materialize`, `seal-front`: then `EXPORT`; `dispatch`: RP0) |
| A pinned input fails its pin or verification | `REFUSAL` in place of `PHASE_DONE` (`materialize`, `dispatch`: RP0; nothing of that input is written), or at `COMMIT` (`adopt`) |
| F's front-parent half fails; dispatch's vault pin or status fails (J9) | `REFUSAL`, RP0 |
| The vault stage of `materialize` fails | recorded and reported (`FINAL.vault`); neither a refusal nor a success condition (§10.7) |
| F sends `STOP` (the lead's interrupt) | the effect the current state's row gives (Appendix B.4.4): a refusal on the verb's refusal path in every state before the verb's commitment (`ADOPTED`, `MATERIALIZED`, `PROCEED_LAUNCH`); a forward down the channels in `RUNNING`; the end of W2's recovery rounds in `RECOVER`; otherwise recorded, and the machine continues (W2 never refuses because of a `STOP`) |
| sudo refuses, account locked, rule missing (each invoke) | F observes S1's exit before any reservation; nothing to release. A setup selftest never stands in for this |
| Channel failure or refusal before D12 | W: `refusal.json` ("refused before reservation and launch; nothing was started") when `attempt.json` is committed; F: no reservation; F runs W2 in mode `seal` if it knows that `attempt.json` is committed (from `W_HELLO` or `EARLY_REFUSAL`) |
| `reservation-intent.json` cannot be committed | F does not write the window (`RESERVE_ABORT`); nothing reserved; W: `refusal.json` |
| `reservation.json` cannot be committed | the reservation exists; durability-UNKNOWN for that record; W refuses before launch, concludes with the after-stage classification, and F releases by §9.4 |
| W dies or its channel fails after F's window write and before `PROCEED_LAUNCH` | W never started S2, but this is not inferred from missing records: F runs recovery (§9.7); release only on known-terminal ownership |
| W dies or its channel fails after `PROCEED_LAUNCH` | a launch may exist; recovery (§9.7) classifies until known-terminal or unknown; release by §9.4; otherwise hold |
| F dies after its window write | W: before launch, refuses and concludes; after launch, keeps waiting and concludes. W cannot release (F alone can): `release-withheld.json` ("front absent"); manual resolution. A front EOF never implies a refusal after launch |
| RL refuses its invocation, the system manager refuses the scope, or a step of the view fails (§12.2), including the creation of U8 or M_run, a mount call, the run-path presentation (step 11), the Landlock domain or the seccomp filter (step 13b) | RL writes the failed step and errno to its stderr (the W-created `launcher.stderr` or `observer-<n>.stderr`) and exits non-zero before it sends anything and before L or O exists; W: a channel failure before `RL_IDENTITY`, S2's or S_O's wait recorded; before launch the stage refuses (RP0); U is absent or `populated 0` once RL has exited. A refusal in a state v5 accepts unless a premise failed (§21 D2) |
| `RL_IDENTITY` missing or second, or failing W's verification | missing or second: a channel failure, and W sends no `GO` or `OBSERVE_REQUEST`, so the helper sees EOF and exits 125 having started nothing; failing: W sends `STOP` (L) or `O_BYE` (O). Before launch the stage refuses; at a classification the observation fails (§9.4) |
| L dies before `GO` / the pid dies after `LAUNCHER_START` | before: nothing was started; after: L may have become C; U's state and the classification decide |
| A G4 check of L fails, L reads a `STOP` at its interruption point, or its `exec` of C fails | `L_REFUSAL` (L's first message when a G4 check failed); L exits 125 having started nothing |
| C refuses before its spawn call (C1 before its hello, C2 after `RECORDS` including its key set, order, digest and view-fact joins, C3-C11 including the run-path alias check and a `STOP` pending at C11) | C's `child-refusal.json` (C's own pre-spawn statement), committed by W; `target_started: false`; terminal ownership still by §9.4 |
| C's spawn call fails and no child exists | `SPAWN_FAILED`; `child-wait.json` with `started: false`, committed by W; `target_started: false`; terminal ownership still by §9.4 |
| C dies or SP_C fails without either record, or C's spawn call fails while a child exists | `target_started: unknown`; never inferred from a missing `CHILD_START` or from C's silence; the classification decides |
| T exits | C's `child-wait.json`, L's and W's waits, O's after stage, conclusion |
| O fails | before launch: the stage refuses; after launch: no complete classification, so hold until a later O under a live W or a W2 succeeds; W never releases on its own |
| The census K or M fails or is UNKNOWN at the parent stage, the child stage or the final pass (an earlier scope not `populated 0` or live in the manager, an unexpected process in U or in the observer scope), or RL's root scan finds a process with uid N or in a U8 outside an RL scope | refuse before launch (RP0 at the parent stage, RP1 at the child stage); recorded as premise evidence when it contradicts §9.8 N7 (P-CG, P-SETNS, P-NOOWNER, P-MGR) |
| An original walk rule refuses an entry below the view's `source/` (an alias, a special file, a multiply linked regular file, an entry its owner cannot open, list or read, an entry that changes during its observation) | v5's refusal at the same stage, unchanged (S:495-566); no other walk rule is added |
| A step before the close marker's link fails (the create, write, `fsync`, validation or link of the record or of either marker, or a directory `fsync` before that link) (§10.1, §10.2 J4) | the record is not committed for any consumer; a named record file or record-bearing marker is RAW; §10.3's retry with its downgrade, then the fallback, carry the record |
| The close marker's link succeeded, then its directory `fsync` or its post-link join fails (§10.1) | the record is committed for every consumer with sync provenance `failed` (§10.5); success withheld; no release effect |
| The writer dies after a close marker's link and before reporting or attesting its sync outcome | the record is committed; provenance `unobserved` for every consumer (§10.5); success withheld; no release effect |
| A marker fails and its continuation fails too (§10.2 J4) | the writer writes no further marker in that journal; later records go to the fallback journal (durability-UNKNOWN for `adopt`, which has none); success withheld; no release effect |
| A journal is branched (§10.2) | the writer writes no marker in it; its records go to the fallback journal or are durability-UNKNOWN; success withheld; no release effect |
| Records exhaustion | §10: success withheld; release by §9.4 only |
| A stream file not final (§10.6) | success withheld; no release effect |
| An export increment fails | `EXPORTED` with state `failed`; success withheld; no release effect |
| The complete capture fails (an `ENOSPC`, an I/O error, or its self-check finds a change twice, §15.3) | `capture-<A>` recorded `failed` with its facts; success withheld (§10.7); no release effect; W2 may make it later |
| Window not owned at release | `NotOwner`, nothing released (v5) |
| Window write error at release | §9.4, window write failure |
| The images directory, a backing image file or a mount check fails (§3.4) | W, W2, RL: refuse before any mutation or view |
| `sicarii` or target mutation attempt on frame objects | kernel `EACCES`/`EPERM` (§6.5) — prevention, verified by probes in future |

### 9.6 Reboot

- Every record and participant identity carries the boot id. After a reboot every participant of an earlier boot has
  ended. An attempt of an earlier boot whose `launcher-intent.json` is committed but which has no committed
  `result.json` is "interrupted by reboot: outcome unknown"; it is non-success forever and is never re-entered. An
  attempt of an earlier boot without a committed `final-status.json` is non-success forever as well, whatever its stage.
- The window, if still reserved by that attempt, stays reserved: F (the only releaser) is gone, and no frame verb
  collects it. The operator resolves it explicitly, citing the boot ids and the attempt's committed records.
- At its next invocation W (or W2) re-verifies the protected inventory before any mutation, by the pinned fields of
  §11.7 only: the ancestor chain, `lease/`, `writer.lock`, T_root and R_root with the missing-mount checks of §3.4
  (with images: filesystem UUID and label, backing image file identity, mount point, options and nesting, image-root
  owner, mode and ACL; the loop device number and mount ID are re-observed, not compared) and the installed frame; it
  refuses otherwise. A missing image mount leaves the bare root-owned mount point, which W can neither write nor mistake
  (§3.4).
- Journals are interpreted, never repaired: each journal's committed chain is recomputed (§10.2), and a torn marker
  or torn fallback slot left by the interrupted boot is raw evidence, never reused (§10.2, §10.4). A close marker whose
  link reached the disk before the crash confirms its record; one whose link did not is absent, and its record is
  uncommitted (§10.1): the same answer for every reader. A post-reboot reader classifies each committed record's sync
  provenance by §10.5: a close marker present after the reboot is `present-after-reboot` (its entry reached the disk),
  in addition to whatever provenance a committed later record attests; it never infers `observed` from presence alone.
- Scopes, views, their namespaces and their filters end with the boot. The first census of the new boot sees
  `user-1000.slice` without the earlier RL scopes.
- There is no implicit new genesis: W never recreates or reinitializes a generation; a new one exists only through
  `materialize`. Stale evidence earns no credit: no record of an earlier attempt is ever an admission input.

### 9.7 Writer-death recovery and the post-writer W2 [corrections: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE]

**Mode `seal`** (W ended normally with `FINAL`). F starts S3 → W2 `seal-front <N_F> <g> <A> seal`. W2: first act,
identity, lease (on `LeaseHeld` it exits before any mutation, and F retries after a fixed interval of 10 s, a
judgment, until the lead stops F), capability (§5.2); creates `w2-<k>/` and commits `w2-<k>/identity.json`;
`W2_HELLO`. F: `HELLO_ACK`. State `FRONT_TERMINAL`: F sends its terminal record (S1's raw wait, W's `FINAL`, W's triple
absent or reused, the answers forwarded, interrupts, errors, channel heads, durability) and W2 commits
`w2-<k>/front-terminal.json`. If A's complete capture is missing and K shows U absent or `populated 0`, W2 makes it
(§15.3). State `EXPORT`: A's next export increment (§15.3). State `FINAL`: `FINAL`, `BYE`.

**Mode `recover`** (F did not receive W's `FINAL`: W died or the F↔W channel failed; and F wrote the window during this
attempt, or cannot tell whether its window write took effect):
- RC1. F closes its ends of the W pipes and waits for S1 to exit, without a deadline; the lead's interrupt is
  recorded and forwarded as in v5. While S1 or W lives, W holds the lease and no W2 can start.
- RC2. F starts S3 → W2 `seal-front <N_F> <g> <A> recover`. W2: first act, identity, lease (retried as above),
  capability (§5.2), including the attempt writer's triple absent or reused; creates `w2-<k>/` and commits its
  identity; reads A's committed journal chain (§10.2) and every committed participant record of A, and classifies each
  committed record's sync provenance by §10.5 (it never re-derives `observed` by its own `fsync`, because a later
  `fsync` need not report an earlier write-back error); `W2_HELLO`.
- RC3. State `RECOVER`, rounds r = 1, 2, …: W2 uses an observer O (G0 first: `w2-<k>/observer-intent-<n>.json`; one O
  may serve several rounds) to evaluate v5's terminal predicate at the recovery point (§9.4): U's state and cgroup,
  every participant named by A's committed records or seen in U, no process naming the attempt, no unresolved child
  record. The verdict is `known-terminal` (the predicate holds), `live` (U active or populated, or a recorded
  participant pid present: W2 waits a fixed round interval of 10 s, a judgment that paces the rounds and refuses
  nothing, and repeats) or `unknown` (an unreadable entry, an O that cannot run or answer, an unresolved participant
  record: the rounds end). W2 commits `w2-<k>/recovery/scan-<r>.json` when the verdict or the set of live participants
  changes and for the last round, and `w2-<k>/recovery/result.json` with the final verdict and `target_started`; it
  sends `RECOVERY_SCAN` after each committed round and `RECOVERY_RESULT` at the end, after its O has ended (`O_BYE`,
  wait). F may send `STOP` (the lead's interrupt): W2 ends the rounds with the last verdict, `live` or `unknown`.
- RC4. State `RELEASE`: the rule of §9.4 with W2 as the serving writer instance; W2's release records are
  `w2-<k>/release-intent.json`, `w2-<k>/window-release.json`, `w2-<k>/release-withheld.json`,
  `w2-<k>/release-not-owner.json` and `w2-<k>/release-failure.json`.
- RC5. `FRONT_TERMINAL`, the complete capture if missing and U is `populated 0` (§15.3), `EXPORT` and `FINAL` as in mode
  `seal`; the front terminal record carries `recovery: true` and the recovery result.

**No inference from missing evidence.** W2 never concludes that a participant did not exist because a record is
missing, and `target_started` follows §9.3 (C's refusals). The classification always evaluates the whole predicate.

**Authority.** W2 uses only the reviewed rules: S3 is the `sicarii`→`wlscratch` writer rule, and W2's S_O uses the
`wlscratch`→root RL rule exactly as W's observers do, with `recover` as O's stage. W2 writes only inside `w2-<k>/`,
A's attempt journal, A's export increments and A's complete capture (§5.2). F alone releases. If W2 or O cannot run (a
sudo refusal, a lease that never becomes free, a refusing O), no complete classification exists, and the window is held
(§9.4).

**When F does not run recovery.** If F never wrote the window (a refusal before D12, or `RESERVE_ABORT`), there is
nothing to release; F still runs W2 in mode `seal` if `attempt.json` is committed (otherwise F's terminal facts stay on
its console). If F dies, nobody releases: the window is held for manual resolution (§9.5), as in v3.

### 9.8 Custody by the same-identity view [corrections: W1-V8-HOLDER-IOEXIT, W1-V8-WRITER-AS-W, W1-V8-PREMISE-DISCHARGE; v8: W1-V7-ARCHITECTURE, W1-V7-HOLDER-STATE, W1-V7-READ-EFFECTS, W1-V7-PROBES, W1-V7-PREMISES; v7: W1-V6-PRESERVE, W1-V6-READ-MUTATION, W1-V6-SCAN-STATE]

The K0 statement stands as the v6 review ruled it (§22.2): an obstruction for the unprivileged DAC architecture and
already-shared writable descriptions, not a universal theorem.

**N0. The obligation and its terms.** From the final pass to T's `exec` (V5-B01, second sentence) and across every
frame mutation (V5-B02):
(a) no principal outside the attempt's own process tree, other than root and W, holds a *usable reference* to, or a
*usable name* for, an admitted entry, or can obtain one;
(b) no logical mutation of an admitted entry can take effect through a reference created by an earlier attempt's
holder after that holder's event H (N4);
(c) every frame mutation lies in T or is v5's window protocol, and every other frame-caused effect is in the inventory
of N5-N6 with its classification.
A *reference* to an entry E is an open file description of E; a `struct path` naming E held as a process's root or
cwd; a mapping of E; an in-flight `SCM_RIGHTS` entry for E; or a kernel request that will write E (in v9 only the
synchronous system calls of a live task can be such a request, N4). It is *usable* by a principal P if P can perform an
operation through it (read, write, truncate, metadata change, re-open, mapping store, pass it on). A *usable name* of E
for P is a path whose resolution by P, in P's mount namespace from P's root or cwd, reaches E. A string that resolves
elsewhere for P is not a name of E.

**N1. Push routes** (a process of a view hands a reference to a process outside its tree).
- Inherited descriptors: a view process holds only `/dev/null`, its stream files and, for L, C and O, its channel
  socket to W (C11); T receives `/dev/null` and its two stream files. W reads its sockets with a zero-length control
  buffer, so a descriptor sent by L, C or O is truncated (`MSG_CTRUNC`), never installed, and recorded as a channel
  failure.
- Pathname UNIX sockets, outward: the domain handles `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` and grants it nowhere. The
  installed `landlock.h` (2026-10-05T15:51:39Z): "On UNIX domain sockets, this restricts both calls to connect(2) as
  well as calls to sendmsg(2) with an explicit recipient address. This access right only applies to connections to
  UNIX server sockets which were created outside of the newly created Landlock domain … Newly created UNIX servers
  within the same Landlock domain continue to be accessible." So `sicarii`'s session bus, user and system managers,
  agents, compositor, `/dev/log` and every other outside server are unreachable (`EACCES`), while the target's own
  servers (for example `why3server`, which inherits the domain) stay reachable.
- Pathname UNIX sockets, inward: `MAKE_SOCK` is granted only beneath the two binds, so every socket file a view
  process creates, renames or links lies below g/source or g/tmpdir, which exist as names only inside view mount
  namespaces (N3); no outside process can resolve them.
- Abstract sockets: their namespace is the network namespace; the view's is private and owned by the initial user
  namespace, so no outside process can join it (`setns` needs `CAP_SYS_ADMIN` over that owner) or reach it through
  `/proc/<pid>/ns/net` (ptrace-gated, N2). This closes both directions.
- Other descriptor-carrying interfaces: binder needs a binder device (none exists, v7 Appendix G; a binderfs mount is
  a mount, which Landlock forbids); `io_uring` (whose `IORING_OP_MSG_RING` could carry a descriptor between rings) is
  unavailable in the view (`io_uring_setup` returns `ENOSYS`, §12.2 step 13b); `pidfd_getfd` and `/proc/<pid>/fd` are
  pulls (N2); signals and file contents carry no reference.
- So every process that can receive a reference from a view process is in the same view and scope, or is W, which
  discards it.

**N2. Pull routes, grounded in the controlling rule** (corrections W1-V7-ARCHITECTURE, W1-V8-WRITER-AS-W).
Upstream Linux v7.2 `kernel/ptrace.c` `__ptrace_may_access` (fetched 2026-10-05; installed correspondence is premise
P-KSRC): after the same-thread-group shortcut, the caller passes if its uid and gid (fs or real, per mode) equal the
target's real, effective and saved ids, or if `ptrace_has_cap(tcred->user_ns, mode)`; then `task_still_dumpable`;
then `security_ptrace_access_check`. Upstream `security/commoncap.c`:

```c
	if (cred->user_ns == child_cred->user_ns &&
	    cap_issubset(child_cred->cap_permitted, *caller_caps))
		goto out;
	if (ns_capable(child_cred->user_ns, CAP_SYS_PTRACE))
		goto out;
	ret = -EPERM;
```

and `cap_capable_helper` walks from the target namespace towards the caller's: equal namespaces decide by the caller's
effective set; a target at a level not above the caller's denies; a target whose parent is the caller's namespace and
whose owner equals the caller's euid grants every capability (the owner rule); otherwise it moves to the parent.

**Every principal that could try, and what decides** (U8 is a child of the initial namespace, owned by N):

| Principal | uid half of `__ptrace_may_access` | commoncap | Outcome |
|---|---|---|---|
| A1, initial namespace, euid 1000, no capabilities | passes (same host ids as T) | namespaces differ; `ns_capable(U8, CAP_SYS_PTRACE)`: U8's parent is A1's namespace but its owner N ≠ 1000, so the walk reaches the initial namespace, where A1 lacks `CAP_SYS_PTRACE` | denied |
| A1 inside a user namespace Ua that it created (owner 1000 or a subordinate id) | passes or fails by ids | U8 is not above Ua's level, or Ua is not an ancestor of U8, so the walk denies | denied |
| A1's `writer.py` started through the S1 rule (initial namespace, euid W, reviewed code with A1's arguments) | fails (W ≠ 1000) | the owner rule would apply only if U8's owner were W; it is N; W holds no capability in the initial namespace | denied — the W-owned design of v8 granted this process every capability over U8; v9 removes that by the owner choice, so the pull closure does not rest on `writer.py`'s behaviour (it still rests on `writer.py` for g, which W owns, §2.2) |
| A process with euid N in the initial namespace | — | the owner rule grants every capability over U8 | only RL's helper ever has euid N; it runs RL's code, creates one namespace and exits before L exists (premise P-NOOWNER; RL's root scan, §12.2 step 5, requires that no other process has uid N) |
| A3 (another uid, initial namespace) | fails | as A1 | denied |
| T or O of another attempt (a sibling U8) | passes | sibling namespaces: the target's is not above the caller's level | denied |
| T towards any process outside its U8 | passes for `sicarii` processes | the target namespace (initial) is not above U8's level | denied |
| processes inside the same U8 | passes | same namespace, every view process has an empty permitted set | allowed, subject to Yama `ptrace_scope=1` for attach and to Landlock (same domain) |
| root (initial namespace) | — | holds `CAP_SYS_PTRACE` in the initial namespace, which covers U8 | trusted base |

Operations and their modes (upstream readings, P-KSRC): `/proc/<pid>/{fd/*,cwd,root,exe}` open and `readlink`
(`call_proc_get_link`, `PTRACE_MODE_READ_FSCREDS`), `/proc/<pid>/fdinfo/*` (`proc_fdinfo_permission`,
`READ_FSCREDS`), `/proc/<pid>/ns/*` (read), `/proc/<pid>/{mem,environ}` (`mm_access` with `FSCREDS`; attach for
`mem`, read for `environ`), `pidfd_getfd` (`__pidfd_fget`: `PTRACE_MODE_ATTACH_REALCREDS`, under `exec_update_lock`),
`ptrace` attach and seize (`PTRACE_MODE_ATTACH_REALCREDS`), `process_vm_readv`/`writev` and `kcmp` (ptrace modes),
`/proc/<pid>/map_files/*` (`checkpoint_restore_ns_capable(&init_user_ns)`): each needs the ptrace check above or a
capability in the initial namespace, so each fails for every non-root principal of the table. Listing `/proc/<T>/fd`
passes DAC (`proc_fd_permission`) and reveals descriptor numbers only. Reading the world-readable
`/proc/<pid>/{cmdline,status,statm}` needs no ptrace check and can hold the target's memory context briefly; it yields
no reference to any file and, with no asynchronous I/O in the view, no write (N4). An unprivileged fanotify group
reports file identifiers, not descriptors, and marks only inodes its owner reaches by path, which excludes g.

**N3. Names.**
- Paths: on disk every admitted entry lies below g, which grants search to W and root only (§6.3). The binds exist
  only in view mount namespaces (each owned by the initial user namespace, with private propagation, P-PROP), which no
  outside principal can enter (`setns` needs `CAP_SYS_ADMIN` there) or reach through `/proc/<pid>/root` (N2).
- New names: a `link` or `rename` whose paths lie in different mounts does not succeed (P-XMNT), so every name of an
  admitted entry made by a view process stays below g/source or g/tmpdir. Landlock forbids every mount, unmount, move
  and `pivot_root` to a domain process, in every user namespace (P-LOCK), so no view process can attach a subtree of a
  bind elsewhere; the nested mount namespaces a view process can still create (by `unshare`) hold locked copies usable
  only by processes of the attempt's own tree.
- Run-path ancestors: the path above the bind is `sicarii`'s (§3.3). A rename by A1 moves names, not the bind; before
  the spawn C refuses an alias (§4.5 item 4); afterwards it is residual R3b (§2.4).
- File handles: in the installed-version-unverified upstream `may_decode_fh`, an unprivileged caller may decode only a
  directory handle, only through a mount whose namespace it administers and which has no locked child mounts, only
  with `CAP_DAC_READ_SEARCH` in its own namespace, and only if every ancestor from the decoded directory up to that
  mount's root has an owner and group mapped in its namespace. Every admitted directory has the W-owned g (and the
  root- or W-owned directories above it) among its ancestors on disk; W and 0 are mapped in no namespace that A1 can
  create (A1 maps 1000 and its subordinate range 100000-165535). Premise P-FH.

**N4. The holder event, with the asynchronous paths closed** (corrections W1-V7-HOLDER-STATE, W1-V8-HOLDER-IOEXIT).
For an RL scope U, H(U) holds at time t iff
(1) K reads U absent or `populated 0` at t;
(2) every task that was ever a member of U has completed `do_exit` up to its cgroup exit;
(3) no logical mutation of an admitted entry can take effect after t through a reference created by a task of U.

*Why v8's argument was not enough.* v8 named one path by which (3) could fail after (1): a Linux AIO direct-I/O write
whose completion wait runs only when the last user of the task's memory context releases it, which an outside reader
of `/proc/<pid>/cmdline` can delay. There is a second: at exit, upstream `do_exit` calls `io_uring_files_cancel()`
(`__io_uring_cancel(false)`), and `io_uring_cancel_generic(cancel_all=false, …)` stops waiting as soon as the *tracked*
in-flight count is zero, so an issued untracked request (a direct-I/O write) is not waited for (correction 0.2 item 1).
Both are asynchronous submission interfaces.

*The redesign.* RL installs, before it gives up its privileges, a seccomp filter (§12.2 step 13b) under which
`io_setup` and `io_uring_setup` return `ENOSYS` for both system-call tables of this kernel (`AUDIT_ARCH_AARCH64`:
numbers 0 and 425; `AUDIT_ARCH_ARM`, the 32-bit compatibility table: 243 and 425; read from the installed build's
generated `unistd_64.h` and `unistd_32.h`, Appendix I). A seccomp filter cannot be removed, is inherited across
`fork` and `exec`, and applies to every task of the view. No task of a view can therefore create an AIO context or an
`io_uring` instance, and no such object can reach it from outside (N1).

*The closed list of logical-mutation paths of a task* (P-ASYNC; each a source-reading obligation on the installed
build, §13.2 S-2): (i) system calls that write file data or metadata (the `write`, `pwrite`, vector and `splice`
families, `copy_file_range`, `sendfile` into a file, `fallocate`, `truncate`, metadata and namespace operations) complete
or fail before the call returns, and a fatal signal is acted on only on the return path; a synchronous direct-I/O write
waits for its bios before it returns, in an uninterruptible wait; (ii) stores through a shared writable mapping are made
by the task's own threads, so none happens after its last thread has exited, and no outside process can write the
memory context (`/proc/<pid>/mem` writing and `process_vm_writev` need ptrace access, N2); (iii) Linux AIO and
`io_uring` — the only interfaces whose requests outlive the submitting task — are unavailable; (iv) the deferred final
`fput` of a file runs in one of these contexts — task work before the cgroup exit; later through the UNIX-socket
garbage collector for a descriptor caught in an unreachable socket; or, for a file mapped by a task, in the context of
the **last releaser of that task's memory**, which may be an **outside holder** of the memory (a
`get_task_mm`/`get_task_exe_file` user reachable through a world-readable `/proc` file) dropping the mapping's
`vm_file` reference **after** the cgroup exit — and in every such context runs the filesystem's `release`, which on
ext4 changes no content, size, mode, owner, link count, mtime or ctime (P-RELEASE). Such an outside holder holds a
task-created mapping **reference** but no **usable** reference and no write path: by N0's definition the reference
yields no operation a principal outside the tree can perform (reading the memory needs ptrace access, which N2 denies;
with the asynchronous submission interfaces unavailable there is no pending write), so it is **held-but-unusable**;
(v) write-back of pages already dirtied is physical, not logical: the content
was set by the store; (vi) no view process can create a loop device, swap file, mount or other kernel user of a file
(no capability in the initial namespace, Landlock's topology rule).

*From (1) to (2):* a task leaves a cgroup only by exiting or by migration, which needs write access to the
destination's `cgroup.procs` and to the common ancestor's; below `user-1000.slice` those files are root-owned, and the
common ancestor of an RL scope and any other cgroup is `user-1000.slice` or above (P-CG). RL never migrates a task out;
root's other actions are trusted base. In upstream `do_exit`, `cgroup_task_exit` follows `exit_mm`, `exit_files`,
`exit_fs` and `exit_task_work` (quoted order, Appendix I).
*From (2) to (3):* by (i)-(vi), every logical mutation that a task of U can cause has taken effect before that task's
cgroup exit, or never will; and every reference a task of U created is held by tasks of U, by sockets only they could
read, by kernel objects reachable only through those (N1-N3), **or — for a mapping reference whose memory an outside
principal holds through a world-readable `/proc` file — by that outside holder, which holds it but cannot use it (N0,
N2) and through which no content can change (by (iii) there is no asynchronous write, and by N2 no outside process can
write the memory)**. No **usable** reference, and no reference through which content can change, is held by a principal
outside the tree; v8's and v9's unqualified 'none by a principal outside the tree' is corrected to this
held-but-unusable statement (W1-V9-ASYNC-ENUM).
*Absorbing:* once (1)-(3) hold they hold forever after: no task can join U (only a member can fork into it, and only
root migrates), no task can join U's U8 (`setns` needs `CAP_SYS_ADMIN` in U8, held only by root and by an euid-N process
of the initial namespace, P-SETNS, P-NOOWNER), and RL never reuses a scope name or a namespace.
H(U) is not observed directly: K's `populated 0` observes (1), and (2)-(3) follow from P-CG, P-SECCOMP, P-ASYNC and
P-RELEASE. Each is a source-dischargeable statement with a refutation run (§13.2); none is a known gap. The two
consumers of H(U) — the complete capture (§15.3) and stream finality (§10.6) — add their own self-checks. **Each
self-check is evidence for its own observation window only: an equal pair (or triple) of `stat_key` readings shows no
change between the readings, not the absence of a later write, so no 'never a silent change' claim is made
(W1-V9-ASYNC-ENUM).** The completeness of N4's closed list (i)-(vi) over the installed kernel is the obligation
P-ASYNC, discharged only by the source enumeration of §13.2 S-2 over the basis stated in N7, and refuted only by the
operator-reserved exercise of §16.1 O-ASYNC under the observed-state predicate of §13.1.

**N5. Frame-caused privileged and control-plane effects** (W1-V7-READ-EFFECTS). Every effect outside T caused by RL,
by the sudo rules or by the system manager on the frame's request, with its classification. "Frame-own object" means a
kernel object the frame creates for the attempt, which no other principal uses and which ends with it; the author
classifies such effects as outside the location-custody question, which the reviewer may reject, so V5-B02 stays OPEN
for them until ruled.

| Effect | Cause | Original counterpart | Treatment |
|---|---|---|---|
| transient unit `<U>`: unit state in PID 1, a transient unit file under `/run/systemd/transient/`, the cgroup | RL's `systemd-run --scope` | v5's `systemd-run --user --scope`: the same objects in `sicarii`'s manager and `/run/user/1000/systemd/transient/` | same class as v5; OPEN for classification |
| journal entries about `<U>` | the system manager | v5's user-manager entries | reduced: `LogLevelMax=warning` drops the manager's informational messages about the unit (installed `systemd.exec(5)`: "applied to any log messages … written by the system or user manager processes in reference to this unit"); warnings and errors remain; OPEN |
| sudo's syslog, audit and PAM-session effects | S1, S2, S_O, S3 | none in v5 | removed by `Defaults!<alias> !log_allowed, !pam_session, !pam_setcred, !use_pty` on the two frame rules (§11.5; installed `sudoers(5)`: `log_allowed` "will log commands allowed by the policy to the system audit log (where supported) as well as to syslog and/or a log file"); sudo's PAM account phase remains (reads only, P-SUDO); OPEN until P-SUDO's before/after capture shows no write |
| sudo timestamp and lecture files | S1, S2 | none | not created for `NOPASSWD` rules without authentication (P-SUDO) |
| U8's and M_run's `uid_map`, `gid_map`, `setgroups` writes | RL, on its own helper processes | none | frame-own objects |
| RL's helpers with uid N | RL | none | frame-own processes; they exist only while one namespace is created |
| copied mount namespace, its `nosuid` and propagation changes, the binds, the skeleton `tmpfs` | RL | none | frame-own objects; no host filesystem write |
| network namespace and its loopback state | RL | none | frame-own object |
| Landlock domain, seccomp filter, credentials, limits, `oom_score_adj` of its own process | RL | v5 set its own limits | frame-own |
| per-user kernel accounting of the view (user namespaces, inotify, mount namespaces, …) | the view's processes, charged at the initial level to U8's owner N | charged to 1000 in v5 | a change (§12.3 V13), not a write |

**No frame-caused effect creates a set-user-ID or file-capability object**, and no installed path, nor any path
reachable through the S1 or RL rule, creates one; the set-ID and file-capability probe fixtures are operator-only
(§13, §16.1 O-2′), so an installed failure of a critical premise could not be combined with an on-demand set-ID object
at A1's request (W1-V9-RL-SELFTEST-FIXTURE).

**N6. Read-side effects of the frame** (W1-V7-READ-EFFECTS). Every causal read route of every frame process with its
effect. `O_NOATIME` is permitted to the owner of the file (through the mount's idmap) or to a holder of `CAP_FOWNER`.

| Route | Reads | Mechanism | Effect | Status |
|---|---|---|---|---|
| R-a | W, W2: records, recipe, snapshot in T | `O_NOATIME` (owner) | none | closed (conditional on P-NOATIME) |
| R-b | C, O: every entry below `source/` and `tmpdir/`, and the report | `O_NOATIME`, owner through M_run | none | closed (P-NOATIME, P-IDMAP) |
| R-c | F: `sicarii`-owned lead inputs | `O_NOATIME` (owner) | none | closed for F's explicit reads |
| R-d | F: a lead input owned by another non-root user | `O_NOATIME` fails (`EPERM`); read without it, as v5 | possible atime update outside T | **OPEN** (refusing would narrow an accepted case) |
| R-e | C, O: `sicarii`-owned files outside the binds (toolchain, proof data, ELF, vendor, `TMPDIR` identity) | `O_NOATIME` (owner: host uid 1000, no idmap needed) | none | closed (P-NOATIME) |
| R-e' | C, O: such files owned by another non-root user | read without the flag | possible atime update | **OPEN** (as R-d) |
| R-f | every frame process: root-owned files read by explicit observation code | RL uses `O_NOATIME` (`CAP_FOWNER`); others cannot | atime under `relatime` on root-owned files | **OPEN** |
| R-g | `/proc`, `/sys`, cgroupfs reads | pseudo-filesystems | their reads change no stored state (P-PSEUDO); the control-plane writes are N5's | closed for reads only, conditional on P-PSEUDO |
| R-h | C's `execve` of the target and the loader's reads of its libraries | no `O_NOATIME` for `exec` | atime of `sicarii`-owned toolchain files | **OPEN** |
| R-i | bootstrap of every frame process: the dynamic loader (`ld.so.cache`, `libc`, `libpython`), `site`, `.pth` files (F: the user site directory too), `encodings`, `ctypes` and every import, locale and `nsswitch` reads, the module hashing of the role identity | ordinary opens, before or outside frame code | atime of root-owned files; for F also of `sicarii`-owned site files | **OPEN**; F must keep the real non-isolated invocation (§8.2), so these reads are the original's, and their effect is a frame-caused read mutation outside T |
| R-j | subprocesses: `sudo`, `systemd-run`, `systemctl`, `project-vault`, `storage_status.py` and their own reads | ordinary opens | atime of root- and `sicarii`-owned files | **OPEN** (v5 ran `systemd-run`, `project-vault` and `storage_status.py` itself) |
| R-k | RL: the skeleton's enumeration of D and its path lookups | `O_NOATIME` (root); lookups do not touch atime | none | closed (P-NOATIME) |
| R-l | C: the run-path alias check | `O_PATH` resolution | none | closed |
| R-m | W, W2: the complete capture of g after H | `O_NOATIME` (owner on disk); symlinks by `readlinkat`, on W-owned symlinks inside T | none outside T | closed (P-NOATIME) |

Readable foreign-owned inputs stay accepted (R-d, R-e'). W1-V6-READ-MUTATION and V5-B02 stay OPEN for R-d, R-e', R-f,
R-h, R-i and R-j; no root-trust, pseudo-filesystem or target-residual relabelling is used.

**N7. Premise and dependency register** (W1-V7-PREMISES, W1-V8-PREMISE-DISCHARGE; the one complete register; §18.6
points here). Every row is NAMED_UNESTABLISHED. Discharge kinds: **S**, a source reading matched to the installed build
(never an upstream reading alone); **P**, a probe, which can refute a universal statement and never establishes one;
**T**, a trusted-base exclusion, which is a threat-model assumption and not a test result. The last column names the
steps of the probe-and-evidence plan (§13.2) that discharge (S) or refute (P) the premise; "O-" steps need the operator
package (§16.1). **If any premise is refuted, W-1 must be redesigned for it; no exception is taken and no accepted case
is narrowed. A refuted critical premise (P-NOSUID, P-NOCAP, P-NOOWNER, P-ASYNC, P-SECCOMP) stops every installed use
until the redesign is reviewed.**

| Premise | Statement | Kind | §13.2 steps |
|---|---|---|---|
| P-KSRC | the installed 7.2.6-1-aarch64-ARCH kernel's code for every function this register relies on is the published source of that package version, and that source says what the upstream v7.2 readings quoted or summarized here say ; S-1 binds the **running** kernel image and build-id to the package, not only the installed files (W1-V9-PREMISE-ORDER) | S (package source and patch list; function texts compared); binary-to-source correspondence is T-DISTRO | S-1, S-2 |
| P-PTRACE | N2's operations fail for every non-root principal of N2's table except as N2 states | S, P | S-2; U-6 (the branches an unprivileged process can reproduce); I-2 (the full matrix) |
| P-NOCAP | no view process ever holds a capability in U8 or an ancestor of U8 | S (exec credential computation under `nosuid`; `setns`; `setresuid` from root), P | S-2; I-1 (with O-2's fixtures) |
| P-NOSUID | every mount of the view (the copies, the binds, the skeleton and its re-attached entries) is `nosuid`; copies into nested namespaces keep the flag locked; set-ID bits and file capabilities take no effect on `exec` | S, P | S-2; U-5 (nested-copy locking, unprivileged); I-1 (with O-2's set-ID and file-capability fixtures) |
| P-NOOWNER | no process other than RL's helper ever has euid N in the initial namespace, and the helper runs only RL's code and exits before L exists | S (RL code; the §5.3 route table **over every principal and every Runas/polkit form that could resolve to N or W**, W1-V9-NOOWNER-SCOPE; the sudoers, polkit and PAM inventory of §11.3 P12/P13), T (root), P | S-5; O-1 inventory; I-1 (RL's root scan) |
| P-SETNS | a process joins U8 only by inheritance from RL's stage-2 process, or by `setns` with `CAP_SYS_ADMIN` in U8 (root, or an euid-N process of the initial namespace) | S, T | S-2; I-3 |
| P-CG | `populated` semantics; no task enters or leaves an RL scope except by fork inside it, exit, or root migration; the `cgroup.procs` files of `user-1000.slice` and of RL scopes are root-owned | S, P | S-2; U-1 (ownership read); I-3 |
| P-MGR | the system manager never reports an RL scope inactive, failed or not-found while its cgroup is populated | S (systemd 261 scope code), P | S-3; I-3 |
| P-SLICE | systemd 261 accepts a transient system scope in `user-1000.slice`; the scope stops with that slice, as the original user-manager scope stopped with `user@1000.service` | S, P | S-3; I-3 |
| P-ROOT | `unshare(CLONE_NEWNS)` copies the mount tree and moves the caller's root and cwd to the copies; descriptors opened before keep the original mounts | S, P | S-2; U-5; I-1 |
| P-MSET | `mount_setattr(AT_RECURSIVE)` and `OPEN_TREE_CLONE` change or copy mount structures without calling into any mounted filesystem (no FUSE contact) | S | S-2 |
| P-SKEL | the skeleton construction of §12.2 step 11 succeeds with no host write and shows each entry as the host shows it | S, P | S-2; U-5 (in an unprivileged namespace, partial); I-1 |
| P-PROP | no mount event propagates between a view and the host in either direction | S, P | S-2; U-5; I-1 |
| P-LOCK | Landlock denies `mount`, `umount2`, `move_mount`, `fsmount` attach and `pivot_root` to every domain process in every user namespace; nested copies lock the binds and the skeleton | S, P | S-2; U-2; U-5; I-4 |
| P-LL | with handled `{MAKE_SOCK, RESOLVE_UNIX, REFER}`, `REFER` granted on `/` and `MAKE_SOCK` on the two bind roots: `RESOLVE_UNIX` as quoted in N1; a socket can be created, renamed or linked only into a directory beneath a bind (`EACCES` elsewhere); for every other file type, a `rename` or `link` between two directories of one mount meets `REFER`'s conditions (both directories have `REFER`; the only handled `MAKE_*` right is `MAKE_SOCK`; the handled rights of all directories of one mount are equal, so no access is gained) and succeeds or fails as without Landlock | S, P | S-2; U-2; I-4 |
| P-XMNT | a `link`, `rename` or `renameat2` whose two paths resolve to different mounts does not succeed; its errno is `EXDEV` only when resolution and every earlier check pass, and Landlock's `EACCES` takes precedence | S, P | S-2; U-3; I-4 |
| P-FH | N3's file-handle statement for every handle type and mount configuration A1 or a view process can create | S, P | S-2; U-7; I-4 |
| P-IDMAP | M_run shows on-disk W as 1000 and stores 1000 as W; unmapped ids appear as the overflow id and cannot be created; `O_NOATIME`'s owner test is made through the idmap | S, P | S-2; I-4 |
| P-NETNS | abstract UNIX sockets are scoped by network namespace; joining the view's needs `CAP_SYS_ADMIN` over the initial user namespace | S, P | S-2; U-4; I-1 |
| P-SECCOMP | the filter of §12.2 step 13b returns `ENOSYS` for `io_setup` and `io_uring_setup` on both system-call tables, allows every other call, cannot be removed or bypassed by a view process (including through `io_uring`, which it cannot create), and is inherited across `fork` and `exec` | S, P | S-2; U-8; I-5 |
| P-ASYNC | **(closed specification; obligation.)** Every kernel mechanism by which a reference to an admitted entry or to a task's address space can outlive the cgroup-populated-0 transition, and every entry by which content could still be written through such a reference afterward, is enumerated against the basis below and shown either impossible under the stated confinement (Landlock topology; `nosuid`; the private network and user namespaces; the seccomp `ENOSYS` of `io_setup`/`io_uring_setup`) or incapable of changing already-committed bytes. **Enumeration basis:** every entry of both of this kernel's system-call tables (`AUDIT_ARCH_AARCH64` and the `AUDIT_ARCH_ARM` compatibility table); and every known class of holder that can retain a task-created file or memory reference past the cgroup exit — task-work and the delayed-`fput` workqueue; the UNIX-socket garbage collector; outside `get_task_mm`/`get_task_exe_file` holders reachable through world-readable `/proc` files; io-workqueue and kernel-thread contexts. The two asynchronous submission interfaces are unavailable (P-SECCOMP), so no request outlives its submitting task. | S (the enumeration traversed in the installed source, S-2) | S-2 (E0 source enumeration); O-ASYNC / I-5 **refute only**, under the observed-state predicate of §13.1 (the committed capture byte-equals a re-read taken after every enumerated holder class is shown released); the detailed exercise is OPEN (operator, §16.1 O-ASYNC) |
| P-RELEASE | the final `fput` of an ext4 regular file or directory changes no content, size, mode, owner, link count, mtime or ctime | S, P | S-2; U-9 |
| P-UCOUNT | the view's per-user namespace accounting is charged at the initial level to (initial namespace, N) | S, P | S-2; I-3 |
| P-NOATIME | the `O_NOATIME` opens of R-a, R-b, R-c, R-e, R-k and R-m change no atime | S, P | S-2; U-10; I-4 |
| P-PSEUDO | reads of `/proc`, `/sys` and cgroupfs change no stored state | S | S-2 |
| P-SUDO | with the options of §11.5, sudo 1.9.17p2 writes nothing (no syslog, audit, I/O log, timestamp or lecture file) for an allowed `NOPASSWD` frame command | S, P (before/after capture) | S-4; O-3 |
| P-LOGLEVEL | `LogLevelMax=warning` drops the manager's informational messages about the scope | S (systemd 261), P | S-3; I-3 |
| P-SIG | sudo's relay of signals to the frame commands, as v7 | P | I-3 |
| P-ENOSPC, P-MOUNT, P-IMAGE | carried unchanged (§10.4, §14.5) | S, P | O-2; I-6 |
| P-SYNCPROV | an `fsync` failure is reported to the writer that issued it; a later `fsync` by another opener need not report an earlier write-back failure (why W2 never derives `observed`) | S | S-2; O-2 (failure injection) |
| P-VIEW | (relation, not a kernel fact) every original observation taken in the view equals its original baseline for every original relevant context | S (producer code), with each run's comparison as evidence for that run only | S-5; I-7 |
| TOOL-CLOSURE | (sub-lemma of §21's relation) for each allowlisted action on the pinned toolchain, the observable outcome does not depend on any item of §12.3 | S (source to release-binary correspondence, helpers, configuration); runs refute only | S-6; U-11; I-7 |
| T-DISTRO | the installed kernel, systemd and sudo binaries were built by the distribution from the sources S-1, S-3 and S-4 name | T (unless reproduced by a reproducible build, which v9 does not require) | S-1 records the package and file hashes (`pacman -Qkk`) |
| T-ROOT, T-W, T-RL | root, the kernel, the reviewed writer code and RL behave as reviewed | T | S-5 (code review of the frame, including that W and W2 never call `setns`, `unshare`, `ptrace`, `pidfd_getfd`, `process_vm_*`, and never open another process's `/proc/<pid>/{mem,fd,root,cwd}`) |
| P-TMPAGE | withdrawn with its mechanism in v8 (no private `/tmp`, no tmpfiles rule); recorded so that the register is complete | — | — |
| P-IOEXIT | withdrawn in v9: replaced by P-SECCOMP and P-ASYNC, which a source reading can discharge, because the paths v8's statement could not close no longer exist | — | — |

**N8. What remains outside:** root and the kernel (R8); a writer instance running changed code (outside the threat
model); availability (R6); the target's own confinement outside g (R3) and its path lookups after the spawn (R3b).

## 10. Commits, journals, retries, durable fallback and durability-UNKNOWN [corrections: W1-COMMIT-JOURNAL-EXPORT, W1-DURABILITY-RELEASE; gap: commits-and-durable-channel]

### 10.1 Commit primitive (N11) [corrections: W1-V7-SYNC-PROVENANCE, W1-V6-COMMIT-AMBIGUITY]

`commit(dir, name, value)`:
1. v5 `write_json` bytes (`json.dumps(value, indent=2, sort_keys=True, default=str)` plus a newline, with v5's
   `label`), written into an unnamed inode: `openat(dir, ".", O_TMPFILE|O_RDWR|O_CLOEXEC, 0600)`, a write loop that
   continues after a short write, `fchmod` 0600, `fsync`. Raw byte records (input bytes, the report) use the same
   steps with their bytes.
2. Validation on the held descriptor, before any name exists: `pread` every byte back and require equal sha256 and
   size; `fstat` shows a regular file with `st_nlink == 0`, owner W and mode 0600; `fgetxattr` of
   `system.posix_acl_access` fails with `ENODATA`.
3. Link: `linkat(AT_FDCWD, "/proc/self/fd/<n>", dir, name, AT_SYMLINK_FOLLOW)`. It is create-only: it fails with
   `EEXIST` if the name exists and never replaces a file. After any error of this call W re-observes the name with
   `fstatat(dir, name, AT_SYMLINK_NOFOLLOW)`: if it names the held inode, the link happened (a kernel may report an
   error after adding the entry); otherwise it did not.
4. After the link: `fsync` of the directory; the post-link join (the name names the held inode, `st_nlink == 1`);
   `verify_location`.
5. **Sync attestation.** The outcome of step 4 (directory `fsync` and post-link join) is the record's sync outcome. It
   is reported in `RECORD_COMMITTED {…, sync: "ok" | "failed", errors}` to F, and it is attested durably by the
   writer's next committed record of the same journal, whose body carries `prior_sync: [{name, marker_sha256, sync}]`
   for every record committed since the previous attestation (Appendix B.3). A sync outcome that reaches neither F nor
   a later committed attestation is **unobserved**.

**Commit point (structural commit membership).** A record is committed exactly when the link of its close marker
(§10.2) has happened, and at no other moment. A failure at any step before that link decides nothing for any reader:
no close marker exists, so the record is not committed for any consumer, and its named bytes, if its own link
happened, are "written, uncommitted": raw evidence, never parsed as valid input (v5 `retain` already never reused a
partial primary). A failure after that link changes nothing about commitment: a failed directory `fsync` or post-link
join leaves the record committed for every consumer, with sync provenance `failed` (§10.5). Because a close marker can
appear only by the link of an inode that is already complete, synced and validated, no state exists in which a reader
finds a valid close marker that its writer treats as failed, and no continuation is ever needed to retract one. A
failed file `fsync` or validation happens before the link, so that close marker never gets a name; a failed directory
`fsync` or join happens after the commit point, so that record is committed, with provenance `failed`, for the writer
and for every reader, export and post-reboot interpretation alike (§9.6: after a crash, a close marker whose entry did
not reach the disk is absent and its record uncommitted). Membership and provenance are separate facts (§10.5).

Export copies are committed by the export primitive of §15.3: the same steps, with the export's final mode and ACL
applied to the unnamed inode by `fchmod` and `fsetxattr` before its validation and link.

### 10.2 Markers, journals and the committed chain [corrections: W1-V6-COMMIT-AMBIGUITY; v6: W1-V5-JOURNAL-FAILED-CLOSE; v5: W1-JOURNAL-CONTINUATION]

v4's rule let a torn or unlinked marker end the committed chain while a later writer skipped its seq and linked to the
previous head (review R3). v5 had one rule, the same for every reader and writer, with no case in which a marker both
ends the chain and is bypassed by a successor treated as committed. v5's J4 still let the continuation after a failed
close marker link to the record-bearing marker whose close had failed, and so confirm that record, while §10.3 retried
and downgraded it (review W1-V5-JOURNAL-FAILED-CLOSE). v6 made a record-bearing marker's only possible successor its
own close marker and linked a continuation only to a record-free marker, but a valid close marker whose writer saw a
later step fail could still confirm a record that its writer retried (review W1-V6-COMMIT-AMBIGUITY). v7 put every
file `fsync` and validation before the link (§10.1), so a close marker either exists, complete, and confirms its record
for every reader, or does not exist. The rule is a function of the files present and the same for every reader and
writer.

- **Marker files.** A marker is `commits/<seq:08d>-<tag16>.commit` in its journal's `commits/` directory, holding
  `wlscratch-commit-v2` (Appendix B.3) `{generation, attempt, seq, kind, record, skipped, prev_commit, channel_heads,
  boot_id, at}`. `kind` ∈ {`primary`, `retry`, `export`, `continuation`, `close`}. `record` is `{path, sha256, bytes,
  mode, acl_sha256}` for the three record-bearing kinds (`acl_sha256` is `null` except for export copies) and `null`
  for the two record-free kinds. `skipped` is, for a `continuation`, a non-empty list of `{seq, files: [{name, sha256,
  bytes}]}` (`sha256` and `bytes` are `null` for a file that cannot be read), and `[]` otherwise. `prev_commit` is the
  sha256 of the predecessor marker's bytes, or `null` for a genesis marker. `tag16` is the first 16 hex digits of the
  sha256 of the record's partition-relative path for a record-bearing marker, and of the ASCII string `<kind>:<seq:08d>`
  for a record-free one, so every name is a single component and no two files share a name.
- **Journals:** the generation journal `g/commits/` (P_adm records; final after M8); one attempt journal per attempt,
  `g_rec/attempts/<A>/commits/` (every P_att record and every P_exp copy of A, written first by W and then by each W2
  of A in turn, never concurrently, because each writer holds the lease); the adoption journal `P_ado(I)/commits/`.
- **Valid marker.** A file of `commits/` is a valid marker iff its name matches `^[0-9]{8}-[0-9a-f]{16}\.commit$`, it is
  a regular file owned by W with mode 0600, one link and no ACL, its bytes decode strictly (v5 `read_record` and the
  exact key set of `wlscratch-commit-v2`), its `seq` equals the name's seq, and its tag equals the one its kind and
  record determine. Every other file of `commits/` is RAW. (A reader of an export increment applies the same rule to the
  copied bytes, with the export primitive's final values in place of the file-level conditions, §15.3.)
- **Successor candidates.** For a valid marker H with seq s and digest d:
  - if H is of a record-bearing kind (`primary`, `retry`, `export`), its only candidates are *close candidates*: valid
    markers of kind `close` with seq s+1 and `prev_commit` d;
  - if H is record-free (`close` or `continuation`), a *normal candidate* is a valid marker of a record-bearing kind with
    seq s+1 and `prev_commit` d, and a *continuation candidate* is a valid marker of kind `continuation` with
    `prev_commit` d and seq t ≥ s+2 whose `skipped` names exactly the seqs s+1, …, t−1 and, for each of them, exactly
    the files of `commits/` that carry that seq, with the sha256 and size of their current bytes.
  A continuation or a record-bearing marker whose `prev_commit` is the digest of a record-bearing marker, and a `close`
  marker whose `prev_commit` is the digest of a record-free marker, is nobody's candidate. *Genesis candidates* are
  defined the same way with `prev_commit` `null`: a normal genesis is a record-bearing marker with seq 0, and a
  continuation genesis with seq t skips exactly 0, …, t−1.
- **The chain.**
  1. If there is exactly one continuation candidate, it is the successor, and every marker at a seq it skips is RAW,
     valid or not. Otherwise, if there is exactly one normal or close candidate, it is the successor. Otherwise, if
     there is no candidate, the chain ends. Otherwise (two or more continuation candidates, or two or more normal
     candidates and no continuation candidate) the journal is **branched** there and the chain ends.
  2. Starting from the genesis, this gives the chain E_0, …, E_k (empty if there is no genesis or the genesis is
     branched). The **head** is E_k, or none.
  3. A record is **committed** iff its record-bearing marker is a chain element E_i whose successor E_(i+1) is its own
     close marker. A record-bearing marker whose close marker is missing, torn, invalid or skipped by a continuation is
     never confirmed: either it is the head (unconfirmed), or a continuation from the record-free marker before it skips
     it and it is RAW. Its record is not committed.
  4. Every file of `commits/` that is not a chain element is RAW, and so is every record file whose marker is not a
     confirmed chain element. RAW files are retained, listed and copied as bytes by exports (§15.3); they are never
     parsed as valid input and never get success credit.
  A torn or unlinked marker therefore ends the chain only while no continuation lists it, and once one does it is RAW
  and outside the chain; nothing it carries is ever committed.
- **Commit primitive (completing §10.1).** A record is committed by three create-only links: the record (§10.1), its
  record-bearing marker M (linked to the head as J2-J4 below require), and a `close` marker with `prev_commit` = M's
  digest and the next seq. Each is fully written when §10.1 steps 1-3 succeed for it. A failure in those steps for any
  of the three, or a failed directory `fsync` of the record or of M (both precede the close marker's link), is a failed
  commit: the record is not committed (rule 3), and it follows §10.3 (retry with its downgrade, then fallback). Once
  the close marker is linked, the commit has succeeded; a failure of its directory `fsync` or join is reported as sync
  outcome `failed` (§10.1 step 5, §10.5) and never retracted. Wherever this document says that a record and its marker
  are committed, or that a journal or a prefix ends at, or is cut at, a record's marker, it means this primitive and the
  close marker that confirms that marker. Between commits the head is therefore always record-free.
- **Writer rules** (only the lease holder writes; a W2 only after W has exited):
  - J1 (open). The writer computes the chain. If the journal is branched, it writes no marker in it: every record it
    would commit there goes to the fallback journal (state `fallback`) or, without one (`adopt`), is
    durability-UNKNOWN, and the branch is an error in every later record and in `FINAL`. Otherwise its *base* is the
    head if the head is record-free, else the head's predecessor (an unconfirmed record-bearing head is skipped, never
    confirmed by a writer that did not write it), or none if there is no such marker.
  - J2 (seq). The next seq is one more than the largest seq of any file of `commits/` whose name has the marker form,
    valid or not, and larger than every seq this writer has attempted. No seq is reused, and no file is ever
    overwritten or removed.
  - J3 (linking). A writer links a record-bearing marker only to a record-free marker that it has itself fully written
    in this invocation, or to its record-free base, and a `close` marker only to the record-bearing marker it has just
    fully written. Its first marker is a normal marker linking to the base when the base is the head and the next seq
    is the base's seq + 1; otherwise it is a continuation linking to the base (a genesis continuation if the base is
    none) that lists every seq from the base's seq + 1, or from 0, to its own seq − 1.
  - J4 (failure). If any step before the close marker's link fails, the commit has failed, and the writer's next
    marker in that journal is a continuation that links to the last record-free marker it fully wrote in this
    invocation (a `close` or a continuation), or to its base if it fully wrote none (a genesis continuation if the base
    is none), and lists every seq above that marker up to its own seq − 1. The failed commit's record-bearing marker,
    if linked, is therefore RAW, no close marker for it exists, and its record is not committed; the record follows
    §10.3 (retry, then fallback). A continuation never links to a record-bearing marker. If that continuation also
    fails, the writer writes no further marker in that journal for the rest of its invocation: its later records go to
    the fallback journal or are durability-UNKNOWN, and a record whose confirmation is now impossible is not committed.
    (A failure while writing the record itself, §10.1, uses no seq; the record is "written, uncommitted" if its link
    happened, and follows §10.3.)
  - J5 (one truth). Every record state the writer reports (`RECORD_COMMITTED`, `W_HELLO.committed`, `record_states`,
    `FINAL`) is the state the chain rule gives for the files present after its own writes, re-observed after any
    failed link (§10.1 step 3). It sends `RECORD_COMMITTED` for a record only after the close marker that confirms it
    is linked, with its sync outcome `ok` or `failed`, and it never reports, records or relies on a belief that the rule
    contradicts.
- **First-marker failure.** If the first record-bearing marker of a journal, or its close marker, fails, J4's
  continuation is a genesis continuation; if that fails too, the journal has no chain and nothing in it is committed.
  For a record that must precede `W_HELLO` (`generation.json`, `attempt.json`, `invocation.json`,
  `fallback-allocation.json`) this is §9.5's refusal before any reservation (`EARLY_REFUSAL`); without a committed
  `attempt.json` no W2 can run (§9.7).
- **Gaps.** A seq at which no file exists (a create or link that failed before any name appeared) is listed by the
  next continuation with an empty `files` list.
- **Every consumer, every time.** The rule is a function of the files present: W's attempt-journal join, W2, the
  conclusion, the exports, a reviewer reading an export, and a writer or reader after a reboot all obtain the same
  chain, head, branches and committed set from the same files (§9.6: interpreted, never repaired). A record whose close
  marker was never linked is uncommitted for every one of them: its record bytes and markers are RAW, listed and copied
  by the exports and never parsed as valid input, and its state for every consumer is that of the retry or the
  fallback, with the failure and the downgrade (§10.3, §10.6). A record whose close marker was linked is committed for
  every one of them, and carries the sync provenance that §10.5 assigns to it for the consumer concerned, in every later
  record, in `FINAL` and in the exports. Files lost or torn by a crash change the answer only by making later markers
  RAW or a record uncommitted; such an attempt is non-success by §9.6 in any case.
- **Exports.** §15.3's cut is the head at the start of an increment, which the commit primitive makes record-free, so
  every record-bearing chain marker at or below the cut is confirmed.

### 10.3 Retries and downgrade

v5 `retain` semantics are kept: on any failure in steps 1-3 of the primary the failure is appended, `downgrade` is
applied if given (a retried `result.json` never claims success), and the record is committed under
`name.retry-<12hex>` with its `record_errors`. If the retry's commit also fails, the record goes to the fallback journal.

### 10.4 The fallback journal: immutable allocation, append-only slots [correction: W1-COMMIT-JOURNAL-EXPORT]

- **Allocation (immutable).** At D3 (and at M4 for the creating invocation), before any reservation or launch, W
  creates `attempts/<A>/fallback.journal` create-only 0600 and writes 16777216 zero bytes (JACKAL exact, parsed
  `16*2^20`), syncs the file and its directory, and requires by `fstat`: a regular file, one link, owner W, mode 0600,
  `st_size` 16777216 and `st_blocks` at least 32768 (512-byte units, JACKAL exact, parsed `16*2^20/512`), that is,
  fully allocated with no hole. W then commits **`fallback-allocation.json`** (`wlscratch-fallback-allocation-v1`:
  `path`, `dev`, `ino`, `uid`, `gid`, `mode`, `bytes`, `slot_bytes`, `slots`, `st_blocks`, `created_at`) as an
  ordinary record with its marker. The allocation record is immutable and describes the file's identity and geometry,
  never its content: no digest of the journal's content is committed, and no consumer ever compares the journal's
  content with its initial zero state.
- **Slots.** 256 slots of 65536 bytes (JACKAL exact: parsed `16*2^20/(64*2^10)` gives 256, parsed `64*2^10` gives
  65536). Slot k occupies the bytes from k·65536 up to (k+1)·65536. Layout: magic `"WLFB0001"` (8 bytes), the slot
  index k (u32, big-endian), the payload length L (u32, big-endian), the sha256 of the payload (32 bytes) — a 48-byte
  header (JACKAL exact, parsed `8+4+4+32`) — then the payload (canonical JSON, at most 65488 bytes, JACKAL exact,
  parsed `64*2^10-(8+4+4+32)`), then zero bytes to the end of the slot.
- **Append-only content.** Slots are written in increasing index order only. A writer never writes a slot it has
  already attempted, and a slot that holds any non-zero byte is never written again, cleared or reused. The writer
  keeps the next index n in memory. At open (W2, or any later writer of the attempt), n is the larger of one more than
  the highest index whose slot is not all zero (0 if every slot is zero) and the `slot_range.to` of the attempt's
  latest committed freeze record (§15.3), so that a later writer never writes below a range an earlier export has
  already covered.
- **Write procedure.** The writer builds the complete 65536-byte slot image and writes it at offset n·65536 with a
  loop of `pwrite` calls: after a short write it continues at the advanced offset with the remaining bytes, until all
  are written or a call fails (handled signals are blocked, §9.2, so `EINTR` does not occur); then `fdatasync`. Whatever
  the outcome, n advances: a slot that was partly written, or whose `fdatasync` failed, is never written again. A
  failed slot write appends the failure to the record's error list and tries the next slot, while slots remain; after
  index 255 (JACKAL exact, parsed `16*2^20/(64*2^10)-1`) there is none.
- **Interpretation (the same for every consumer).** EMPTY: all 65536 bytes zero. VALID: the magic, the index equal to
  k, L at most 65488, the sha256 of the L payload bytes equal to the header digest, zero padding, and a payload that
  decodes strictly (§7.2) as `wlscratch-fallback-v1`. TORN: anything else. A TORN slot is raw evidence only: never
  parsed, never reused, never success credit; its raw bytes stay in the journal, and the export lists its index and
  the sha256 of its 65536 bytes (§15.3). An EMPTY slot below n is one whose write failed before any byte reached it,
  or one skipped by the opening rule above; it carries nothing and names no record.
- **Payload** `wlscratch-fallback-v1`: `{record_name, stage, errors, value_sha256, value_bytes, value}` when the
  canonical value fits, or `{record_name, stage, errors, value_sha256, value_bytes, value_truncated: true}` without a
  value when it does not. A truncated payload shows only that a value with that digest and size existed and failed to
  commit; no consumer treats it as the record's content.
- **What the fallback can claim.** Overwriting already-allocated, already-written blocks needs no new data block, so
  slot writes are expected to succeed when the filesystem can no longer allocate. This is a hypothesis until the
  required probe P-ENOSPC (§13) passes; before that, no record is described as durable under allocation failure. The
  journal does not survive a read-only filesystem or a device failure; a torn slot after power loss is TORN.
- Only the lease holder writes slots; W2 writes only after W has exited.

### 10.5 Durability-UNKNOWN and sync provenance [correction: W1-V7-SYNC-PROVENANCE]

Two separate facts are kept for every record name N: its **membership** (committed primary, committed retry,
`fallback`, `raw` or `unknown`, by §10.6's precedence; decided by markers and slots alone) and, for a committed record,
its **sync provenance**, one of:
- `observed`: a sync outcome `ok` reached the consumer through F's in-memory `RECORD_COMMITTED` (for F only) or
  through a committed attestation (`prior_sync`, §10.1 step 5) in the same journal;
- `failed`: an outcome `failed` reached it the same ways;
- `unobserved`: neither exists — in particular when the writer died after the close marker's link and before
  reporting or attesting its outcome;
- `present-after-reboot` (an addition, never a replacement): the reader runs after a reboot later than the record's
  commit (boot ids differ) and finds the close marker; its entry reached the disk. It is reported with whichever of the
  three above also applies.
`observed` is never derived by a later reader's own `fsync` (P-SYNCPROV).

| Consumer | membership | provenance it reports | success effect |
|---|---|---|---|
| live W (the writer itself) | its own markers | its own step-4 outcome | success needs `observed` for every required record |
| F (live) | descriptors from W | `observed`/`failed` from `RECORD_COMMITTED`; `unobserved` for a record whose `RECORD_COMMITTED` never arrived (EOF) | F's terminal record and exit follow §10.7 |
| W2 (after writer death) | the committed chain | attestations only; else `unobserved`; plus `present-after-reboot` when applicable | no success credit for any `unobserved` or `failed` required record |
| a reader after a reboot | the committed chain | as W2 | interpretation only |
| an export and its offline reader | the exported chain and markers | the provenance the exporting writer computed, with the attestation records exported, so the offline reader recomputes it | as recorded |

If primary, retry and fallback all fail for a record, it is **durability-UNKNOWN**: the writer sends `RECORD_UNKNOWN
{name, value_sha256, value_bytes, errors}` to F, writes the facts to its stderr (v5 `last_resort`), records
`durability: UNKNOWN` in every later record it can still commit, and the attempt cannot succeed. A record committed only
to a fallback slot is `fallback`: it earns no success credit either. A record whose provenance is `failed` or
`unobserved` earns no success credit, is not retried (it is committed; a retry would add a second committed version)
and is reported in every later record, in `FINAL` and in the exports. F prints every `RECORD_UNKNOWN`,
`RECORD_FALLBACK` and every commit whose provenance is not `observed` to its console; that output reaches the lead's
tool output and transcript, written by the harness, not by the frame, and is not durable if F dies or the transcript
filesystem fills. Effect: no success or acceptance credit, and the uncertainty is preserved and reported; no hold, no
effect on the window and no approval gate (§9.4). Failure controls (§13.1 P-COMMIT, P-CHAIN): an injected
directory-`fsync` failure (`failed`), the writer killed between the marker's link and its report (`unobserved` for F,
W2, a post-reboot reader and an export, consistently), and a reboot after a linked but unsynced marker (absent marker:
uncommitted; present: committed with `present-after-reboot`).

### 10.6 Consumers (complete)

**Precedence for every record name N:** the committed primary; else the committed retry (with its downgrade); else a
VALID fallback slot naming N (state `fallback`: never success credit; a truncated payload gives only digest and size);
else raw uncommitted bytes of N (state `raw`: evidence only, never parsed as valid input); else `unknown`. TORN slots
name nothing. A committed primary or retry carries its sync provenance (§10.5).

| Consumer | What it uses | Rule |
|---|---|---|
| C | record bytes W delivers over SP_C | only committed primary or retry records; their sha256 must equal W's in-memory descriptors and the seals; fallback and raw bytes are never delivered |
| RL | `launch.json` and `admission.json` read from P_att by anchored chain | their sha256 must equal its argv's seals; nothing else is read as input |
| W's attempt-journal join (D8, C4, C8, the conclusion) | every record of the attempt | each committed record still has its committed sha256, size, mode, single link and ACL state (export copies: their final export values); `fallback.journal` has the identity and size of `fallback-allocation.json`, every slot below the in-memory next index is byte-identical to what this writer last read or wrote (after a failed slot write it reads the slot back), and every slot at or above it is EMPTY; no content digest of the journal is ever compared; the journal's committed chain is unchanged up to the in-memory head |
| F | descriptors from `*_COMMITTED`, `RECORD_FALLBACK`, `RECORD_UNKNOWN`, `EXPORTED` | in memory; export copies re-read and compared with their final values (§15.3) |
| The conclusion, `result.json`, `final-status.json` | every expected record | `record_states` maps each name to `primary`, `retry`, `fallback`, `raw` or `unknown`, with its sync provenance; success needs every required record `primary` or `retry` with provenance `observed` |
| The classification (N12) | participant records | exact schema validation (Appendix B.2); only committed records are participant evidence; a fallback, raw or missing participant record removes no participant (participants are classified by U's state and v5's terminal predicate, §9.4); a parseable record with a missing or mistyped field is unresolved and makes its participant UNKNOWN |
| W2 | A's journal and records | the committed chain only (§10.2); slots by this section's interpretation |
| Exports and reviewers | export increments and captures | §15.3: committed records copied with their sync provenance and attestations; fallback slots decoded or listed; raw bytes copied |
| A writer after a reboot | earlier attempts | interpretation only (§9.6); never an admission input |

- **Stream finality** (correction W1-V8-HOLDER-IOEXIT). After every launch participant's wait is recorded and before
  `result.json`, W closes its own copies of the stream descriptors, syncs the stream files and records their
  `stat_key`, and requires K to show U absent or `populated 0`, which observes term (1) of H(U) (§9.8 N4). Every other
  holder of a stream description is a process of U (W passed them only to L and C, and C only to T; N1-N3), and under
  P-ASYNC no write by a task of U can take effect after its cgroup exit, so no writable description of a stream remains
  outside W, W's copies are closed, and no write is pending. **Self-check:** W re-reads each stream file's `stat_key`
  after the census and once more immediately before committing `stream-finality.json`; the three readings must be
  equal, or the streams are recorded as not final. If U is still populated when W concludes (a target process still
  runs), `stream-finality.json` records it, the streams are not final and success is withheld, with no effect on
  release. The finality claim is therefore observed (K and the equal readings) plus P-ASYNC. **The self-check is
  evidence for its own window only: the three equal `stat_key` readings show no change between them, not the absence of
  a later write, so no 'never a silent change' claim is made (W1-V9-ASYNC-ENUM).** A change the self-check catches
  records the streams as not final; a change outside its window is bounded only by P-ASYNC, which the §13.1 state
  predicate and the operator-reserved exercise (§16.1 O-ASYNC) refute, never establish.
- **Error joins.** Every `record_errors` list, `*-failure.json`, `conclude-errors.json`, channel failures,
  durability-UNKNOWN entries, provenance `failed` or `unobserved`, fallback entries, TORN slots and raw records are
  joined into the conclusion, `final-status.json` and the front terminal record.

### 10.7 Exit statuses and success, per verb (N13, N14) [correction: W1-PROTOCOL-FAILURE-STATES]

- **W, `dispatch` (N13).** `success` = v5's conjunction (launched, scope wait 0, child wait 0 and clean, no error,
  post-identity clean, materialization unchanged, owned terminal) ∧ every required record `primary` or `retry` with
  sync provenance `observed` ∧ no `fallback`, `raw` or `unknown` record ∧ the attempt journal not branched ∧ streams
  final ∧ released (F reported `RELEASE_DONE` with a re-read showing the release) ∧ the release records committed ∧
  export increment 0 frozen ∧ the complete capture of A committed (§15.3). v5's "scope wait" is the relayed status of
  the RL/L/C pid in `launcher-wait.json` (§9.2). Errors appended after `result.json`, including late handle-close and
  export errors, force `success = false`, are committed as `conclude-errors.json` (or to the fallback journal), and make
  W exit 1. `final-status.json` records the final values.
- **W, `materialize`.** `success` = `materialization.json` committed after M8's verification ∧ `verify_materialization`
  against it passed ∧ the generation export frozen (M9) ∧ A0's export increment 0 frozen ∧ every required record of the
  generation journal and of A0's attempt journal `primary` or `retry` with provenance `observed`, none `fallback`,
  `raw` or `unknown`, neither journal branched ∧ no `EARLY_REFUSAL` or `REFUSAL` ∧ no error. The vault stage's outcome
  (M10) is recorded and reported in `FINAL.vault` and is not a condition: v5 `materialize` ran no vault command
  (Appendix E), while `dispatch` keeps v5's vault requirement (J9, `run` S:1562-1563).
- **W, `adopt`.** `success` = `lead-adoption.json` committed and `ADOPTED` sent ∧ the adoption export increment frozen
  ∧ every record of the invocation `primary` or `retry` with provenance `observed` (adopt has no fallback journal, so a
  record that is not committed is `unknown`) ∧ the adoption journal not branched ∧ no error.
- **W2, mode `seal`.** `success` = `w2-<k>/identity.json` and `front-terminal.json` committed ∧ its export increment
  frozen ∧ every W2 record `primary` or `retry` with provenance `observed` ∧ no error.
- **W2, mode `recover`.** The `seal` conjunction ∧ the recovery verdict `known-terminal` ∧ the window released for this
  attempt (by F in this W2's `RELEASE` state, or earlier in the attempt, as F's terminal record states) ∧ the release
  record of this W2's `RELEASE` state committed.
- Each writer exits 0 iff its `success` holds, 1 otherwise, and 125 only on a first-act failure (§7.7).
- **F (N14).** `dispatch`: exit 0 only if W's `FINAL` reports success and release, F's own error list is empty, no
  interrupt reached F, S1's raw status is 0, W2 (mode `seal`) reported success and S3's raw status is 0, and nothing is
  `fallback`, durability-UNKNOWN or of provenance other than `observed`; a run that needed recovery exits 1 even if it
  released. `materialize`: exit 0 only if W's `FINAL` reports success, S1's raw status is 0, W2 (mode `seal`) reported
  success and S3's raw status is 0, F's own error list is empty, no interrupt reached F, and nothing is `fallback`,
  durability-UNKNOWN or of provenance other than `observed`. `adopt`: exit 0 only if W reported `ADOPTED`, `EXPORTED`
  with state `frozen` and a successful `FINAL`, S1's raw status is 0, F's own error list is empty and no interrupt
  reached F (no W2 runs for `adopt`).
- **C, L, O, RL.** C keeps v5's rule (`code` if it is not `None` and there were no failure, notes or errors, else
  `code or 1`); L never exits once it has `exec`ed C, and exits 125 when it started nothing (a failed G4 check, EOF or
  `STOP` before its `exec`, or a failed `exec`); O exits 0 only if its observation succeeded; RL never exits after its
  `exec` of L or O, and exits non-zero on any refusal before it.
- **No success predicate gates release.** Release follows §9.4's rule only. Durability, export, capture and success
  outcomes are reported; none of them holds the window or adds an approval.

## 11. Prestate and installation [corrections: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY; gap: prestate-and-installation]

### 11.1 Rules used throughout

- **Absence is a no-follow ENOENT, decided exactly.** In frame code and in the reviewed operator helper `absent.py`
  (§11.5): the parent path is opened from `/` component by component with `O_DIRECTORY|O_NOFOLLOW` (each component
  must be a directory); then `fstatat(parent, name, AT_SYMLINK_NOFOLLOW)` is called (in Python
  `os.stat(name, dir_fd=parent, follow_symlinks=False)`). The outcome is `absent` if and only if that call fails with
  errno ENOENT (Python `FileNotFoundError`); `present` if it succeeds, whatever the type (a dangling symlink is
  present); and `undetermined` for every other errno, at the parent walk or at the final call (`EACCES`, `ENOTDIR`,
  `ELOOP`, `EIO`, a missing parent component, …). Only `absent` passes an absence check. An `undetermined` result of
  an unprivileged run is repeated by the operator; an `undetermined` result as root refuses. `test ! -e`,
  `[ -e ] || [ -L ]` and every other shell test are never used for absence.
- **Regular-file identity:** `S_ISREG`, `st_nlink == 1`, owner, group, mode, size, sha256, no ACL xattr, and the
  named entry naming the same `[dev, ino]`.
- **Directory identity:** `S_ISDIR`, owner, group, mode, the exact entry set, `st_nlink == 2 + (number of immediate
  subdirectories)`, the exact ACL text (or none), `[dev, ino]`, and the same `st_dev` as its parent unless it is a
  declared mount point. The `nlink == 1` rule applies to regular files only. Which of these fields later invocations
  compare is fixed per object class by §11.7.
- **Symlinks:** none anywhere in an installed or setup tree (v6's mask links are withdrawn with the user manager).
- Every capture is retained raw with its sha256.

### 11.2 Numeric identity policy

- W and N are explicit numbers fixed in the concrete inventory (candidates 950 and 951 as observed in §3.1).
- For each number n: `getent passwd n` and `getent group n` exit 2; n lies in 500-999 (`SYS_UID_MIN`-`SYS_UID_MAX`,
  `SYS_GID_MIN`-`SYS_GID_MAX`, the system range used by `useradd --system`, which allocates no subordinate range for
  system accounts); for every line `owner:start:count` of `/etc/subuid` and `/etc/subgid`, n < start or n ≥ start +
  count, each bound computed with JACKAL in the concrete inventory (all current ranges start at 100000 or above,
  observed); no file on any local filesystem is owned by uid n or group n (P4).
- After setup: `/etc/subuid` and `/etc/subgid` byte-identical to their prestate; `getent` shows exactly the two new
  users and their two user-private groups; `/etc/shadow` password fields of W and N begin with `!` (or `*`), and N's
  account expiry field is 1; the `gshadow` entries of both groups have no members and a locked password.
- N owns no file and no process; RL gives N only to its own helpers (§12.2 step 10) and maps it into no namespace as
  any process's credential.

### 11.3 Prestate inventory (read-only; "lead" = unprivileged agent, "operator" = needs root)

| Id | Check | Runner | Required |
|---|---|---|---|
| P1 | `getent passwd wlscratch`, `getent passwd wlscratch-ns`, `getent group wlscratch`, `getent group wlscratch-ns` | lead | each exits 2 |
| P2 | `getent passwd <n>`, `getent group <n>` for every candidate | lead | each exits 2 |
| P3 | contents, digests and `lstat` of `/etc/subuid`, `/etc/subgid` | lead | every candidate outside every range; files root:root 0644 |
| P4 | `find <fs> -xdev \( -uid <n> -o -gid <n> \) -print -quit` for `/` and each other local non-FUSE filesystem (never `~/iPad`, `~/iPadBackup`) | operator | empty |
| P5 | `absent.py` on `/var/lib/wlscratch`, `/var/lib/wlscratch-ns`, `/opt/wlscratch`, `/etc/ssh/sshd_config.d/30-wlscratch.conf`, `/var/spool/mail/wlscratch`, `/var/spool/mail/wlscratch-ns`, and with images `/var/lib/wlscratch-images` and the mount-unit paths | lead; every `undetermined` repeated by the operator | `absent` each |
| P6 | before any staging exists, so without running any helper as root: `find /etc/sudoers.d -mindepth 1 -maxdepth 1 \( -name wlscratch-frame -o -name wlscratch-rl -o -name .wlscratch-frame.new -o -name .wlscratch-rl.new \) -print` (a complete listing of the root-only directory; no symlink is followed) | operator | exit status 0 and empty output; a non-zero exit is `undetermined` and refuses |
| P7 | `lstat` of `/`, `/var`, `/var/lib`, `/opt`, `/etc/ssh/sshd_config.d`, `/etc/sudoers.d`; `getfacl -n -c` of `/var/lib` and `/opt` | lead (operator for `/etc/sudoers.d`) | root-owned, no extended ACL |
| P8 | `protected_hardlinks`, `protected_symlinks`, `protected_regular`, `ptrace_scope`, `suid_dumpable`, `max_user_namespaces`, `max_mnt_namespaces`, `max_net_namespaces`, `kernel.unprivileged_bpf_disabled`, `kernel.io_uring_disabled`, `fs.aio-max-nr` | lead | as in §2.3; the rest recorded |
| P9 | `findmnt` of `/`, `/var/lib`, `/opt`, `/tmp`, `/var/tmp`, `/dev/shm`, `/run/user`, `/proc`, `/sys/fs/cgroup`; the complete `/proc/self/mountinfo` with the FUSE mounts below `/home/sicarii` listed but never touched | lead | as in §2.3 (`/proc` without `hidepid`; `/tmp` and `/var/lib` on one mount, for §13); recorded as the host mount list the view copies |
| P10 | digests of `/etc/pam.d/{sudo,system-auth,system-login,system-remote-login,sshd,su,su-l,runuser,runuser-l,login,other}` | lead | recorded; the account phase that `!pam_session` leaves is the `system-auth` account stack |
| P11 | digests of `/etc/ssh/sshd_config` and drop-ins; `systemctl show sshd.service -p ActiveState -p UnitFileState`; `sshd -T` | lead; operator for `sshd -T` | recorded; gives the expected `denyusers` line |
| P12 | `sudo --version`; digests of `/etc/sudoers` and every `/etc/sudoers.d` file; `visudo -c`; `sudo -l -U` for `sicarii`, `wlscratch`, `wlscratch-ns` and every other non-root account (for example `cosmov1lab`, `wlrehearsal`, `wldrill`, `worldline`); the rule set read for any `%group`/`#uid`/alias/negation Runas resolving to W or N | lead for the version; operator | §2.3 privilege-route precondition holds; no sudoers rule of any principal resolves its Runas set to N or W through `ALL`, `%group`, `#uid`, an alias or a negation, and none lists N in a user or Runas list, nor W except the S1 rule (W1-V9-NOOWNER-SCOPE) |
| P13 | digests of `/usr/share/polkit-1/rules.d/*`; listing and digests of `/etc/polkit-1/rules.d`; `getent group empower wheel docker` | lead; operator for `/etc` | no polkit authority grants any subject (not only `sicarii` or its groups) a passwordless path to manage a unit or exec as another user (for example `org.freedesktop.systemd1.manage-units`, `org.freedesktop.policykit.exec`, machine shell or login actions, or a `systemd-run --uid=` path to W or N); `empower` and `docker` without members (W1-V9-NOOWNER-SCOPE) |
| P14 | `absent.py` on `/usr/bin/crontab`, `/usr/bin/at`, `/usr/bin/batch`, `/var/spool/cron`, `/var/spool/at`, `/var/spool/atjobs`; `systemctl show cronie.service atd.service -p LoadState` | lead | `absent`; `not-found` |
| P15 | listing of `/var/lib/systemd/linger` | lead | recorded (no new linger file is created) |
| P17 | `find / -xdev -perm /6000 -type f` with digests; `getcap -r /usr` | operator | baseline for S-I |
| P18 | `readlink -f /usr/bin/python3`; sha256 of `/usr/bin/python3.14` and `/usr/lib/libpython3.14.so`; `sys.version` | lead | observed `/usr/bin/python3.14`, `c6bc1ef4…`; 3.14.7 (the lead's earlier observation, reproduced by the re-review) |
| P19 | `systemctl --version`, `setfacl --version`, presence of `/usr/bin/nologin`, `/usr/bin/visudo` | lead | recorded (systemd 261 and sudo 1.9.17p2 are the lead's earlier observations) |
| P20 | `cgroup.subtree_control` of `/sys/fs/cgroup` and of `user.slice/user-1000.slice`; owners of `user.slice/cgroup.procs`, `user-1000.slice` and `user-1000.slice/cgroup.procs` | lead | `memory` and `pids` among the controllers; the three root-owned |
| P22 | the frozen v6-W1 inventory digest and the review-freeze digests that the install will use | lead | recorded |
| P23 | `/etc/default/useradd` (`CREATE_MAIL_SPOOL` and the other defaults) | operator (unreadable to the lead: `Permission denied`, observed 2026-10-05) | recorded; the expected-object list of S-I follows it |
| P25 | kernel and features: `uname -r`; `/sys/kernel/security/lsm`; the build configuration (`CONFIG_USER_NS`, `CONFIG_NET_NS`, `CONFIG_SECURITY_LANDLOCK`, `CONFIG_SECCOMP_FILTER`, `CONFIG_AIO`, `CONFIG_IO_URING`, `CONFIG_COMPAT`, `CONFIG_ANDROID_BINDER_IPC`, `CONFIG_ANDROID_BINDERFS`); the installed `linux-api-headers` version, `landlock.h`, `nsfs.h`, `stat.h`, `mount.h`, `audit.h`; the build tree's generated `unistd_64.h` and `unistd_32.h`; `absent.py` on `/dev/binder`, `/dev/hwbinder`, `/dev/vndbinder`, `/dev/binderfs` | lead | as in §2.3; the binder devices `absent`; the four system-call numbers of §12.2 step 13b |
| P27 | cgroup2 limits and ownership of `user.slice`, `user-1000.slice`, `user@1000.service` and `user@1000.service/app.slice` (`memory.max`, `memory.high`, `memory.swap.max`, `pids.max`, `cpu.weight`, `cpu.max`, owner of each `cgroup.procs`) | lead | recorded; §8.3 and §12.3 V10' |
| P28 | `systemctl --user show` of `app.slice` and the user manager's defaults relevant to a scope (`CPUWeight`, `IOWeight`, `TasksMax`, `OOMPolicy`, `ManagedOOMSwap`, `ManagedOOMMemoryPressure`) | lead | the values that fix §8.3's scope properties |
| P29 | the installed `sudoers(5)` text for `log_allowed`, `pam_session`, `pam_setcred` and `use_pty`; the sudo version | lead | recorded; S-D's options are those the installed version documents |
| P30 | the lead's process attributes as F would record them (§8.3) | lead | each one reproducible by RL (recorded) |

P16, P21, P24 and P26 (v6's user-unit listings, Option A's home ACL captures, the user-manager unit, and v7's `/tmp`
age for the tmpfiles rule) are withdrawn with the mechanisms they served.

Observed on 2026-10-04 by the drafting author (passive reads): the `/etc/passwd` and `/etc/group` entries at or
above 900 (§3.1, for P1/P2); P3 (§5.4); `/etc/login.defs` ranges; P5 for `/var/lib/wlscratch` and `/opt/wlscratch`
(absent from the listings of `/var/lib` and `/opt`); P8 (`protected_*` 1, `ptrace_scope` 1, `suid_dumpable` 2,
`max_user_namespaces` 128053); P9; P10 (the `sudo`, `system-auth`, `system-login`, `system-remote-login`, `sshd`,
`su` and `runuser` stacks); P11 (sshd active; drop-ins `20-systemd-userdb.conf` and `99-archlinux.conf`; `UsePAM yes`;
`AuthorizedKeysFile .ssh/authorized_keys`; `AuthorizedKeysCommand /usr/bin/userdbctl ssh-authorized-keys %u`); P13
(the two `/usr/share` rules files read, the `/etc` directory unreadable); P14; P15; P18 (path and digest).

Observed on 2026-10-05 by the drafting author (passive reads; v7 Appendix G, v8 Appendix H, Appendix I): P9's mount IDs
(`/tmp` and `/var/lib` both 32, on `/dev/vda` ext4) and the full mount list; `/var/spool/mail` present (mode 1777) with
`MAIL_DIR /var/spool/mail` in `/etc/login.defs`; P23's refusal; P8's `kernel.unprivileged_bpf_disabled` 2,
`kernel.io_uring_disabled` 0 and `fs.aio-max-nr` 65536; P20's owners (all three root); P25 (kernel `7.2.6-1-aarch64-ARCH`,
LSMs `capability,yama,landlock`, the listed configuration options including `CONFIG_SECCOMP_FILTER`, `CONFIG_AIO`,
`CONFIG_IO_URING` and `CONFIG_COMPAT`, binder built with binderfs and no binder device present, the system-call numbers);
P27; P29. These are observations only; the concrete inventory repeats them fresh.

### 11.4 Staged atoms, the global state table and reconciliation [corrections: W1-V8-COMPOSED-ENUM, W1-V7-COMPOSED-STATE; v7: W1-V6-COMPOSED-STATE; v6: W1-V5-RECONCILIATION-STATES; v5: W1-SETUP-RECONCILIATION; v4: W1-SETUP-PROBES-ROLLBACK]

- **Reviewed bytes.** Every privileged byte is part of the reviewed concrete inventory with its sha256: both sudoers
  files, the sshd drop-in, every expected ACL text, every expected output that `check_out.py` compares, the
  identity-record generator, the helpers `absent.py`, `step.py` and `check_out.py`, the scripts S-A to S-J, S-R's
  global table, every frame member and the member/directory lists. Every list file a script reads ends with a newline
  and holds one plain name per line; the staging review checks both, so a `read` loop never drops a last line.
- **S-0 (operator, root):** create `/root/wlscratch-staging` with `mkdir -m 0700` (create-only: `mkdir` fails with
  `EEXIST` for any existing entry at that path, a dangling symlink included, so no stale staging tree can be reused)
  and verify root:root 0700 with `stat`; copy the staging manifest from the lead's frozen inventory directory with
  `install -m 0600`; verify it as root with `echo "<MANIFEST_SHA256>  $st/staging-manifest.sha256" | sha256sum -c
  --strict -`, where the digest is the one in the sealed review record (the procedure's only pipeline: its producer is
  the shell's `echo` of a constant line, and the pipeline's status is `sha256sum`'s own, which decides); copy every
  listed file the same way; verify all as root with `sha256sum -c --strict`; create `log/` (0700) and, with `O_EXCL`,
  one empty log file per script (0600). The lead-writable source can change after review, which is why only the
  root-owned copies, checked as root, are ever used.
- **Execution and status handling.** Each script runs as `sudo sh -eu /root/wlscratch-staging/S-<x>.sh` from the
  verified copy. On this host `/usr/bin/sh` and `/bin/sh` are bash, and the installed bash(1) states that a pipeline's
  status is that of its last command unless `pipefail` is set, and that `-e` ignores a failure of any command in a
  pipeline but the last (v7 Appendix E). The scripts never rely on `-e` to observe a producer:
  1. no script contains a pipeline; a command whose output is checked runs under `check_out.py` (§11.5), which runs it
     without a shell and exits 0 only if the command's own exit status is 0 and its output passes the stated check;
  2. a command substitution is used only as the whole right-hand side of an assignment (`v=$(…)`), whose status is the
     substitution's and stops the script under `-e`, and never inside a test, a `case` word or an argument;
  3. a command whose non-zero status is an expected answer is written `rc=0; cmd || rc=$?` and followed by a `case` on
     `$rc` that names every accepted value and stops on every other (`no_entry`, §11.5);
  4. there is no `cd` and no subshell; checksum files name absolute paths;
  5. an `if` condition holds only an explicit test whose every outcome the branch handles (the combined checks of S-D
     and S-E, whose failure leads to the deactivation below and a stop).
  Installs read only from the staging copies; there is no `cp -a` and no recursive `chmod`.
- **Staged-rename file atoms** (correction W1-V7-COMPOSED-STATE). Every regular file the setup installs (except
  `writer.lock`, below) is installed in two steps: the reviewed bytes are written to an inert staging name in the
  destination directory (`.<name>.new`; sudo's `includedir` skips names containing `.`, sshd's `Include *.conf` does not
  match the `.new` suffix, and the frame never opens a dot-name), with owner, group and mode, then synced (`sync --
  <file>`), compared byte for byte with the staging copy (`cmp -s` under `check_out.py --empty`), and renamed to the
  final name with `mv -T -n` (`renameat2` with `RENAME_NOREPLACE`), after which the destination directory is synced and
  the final name is checked to hold the reviewed bytes while the staging name is `absent`. A file atom's observable
  state is therefore one of: `absent`; `staged-partial` (the inert name holds a proper prefix or other bytes);
  `staged-attr` (the reviewed bytes under the inert name, owner, group or mode not yet set); `staged-equal`;
  `installed-equal` (final name, reviewed bytes, owner, group, mode, one link, no ACL); `installed-other` (never produced
  by a script); and `deactivated-equal` (the reviewed bytes back under the inert name after a failed combined check).
  `writer.lock` is the empty file of v7's file class (one `install`; its intermediates are a file with any owner and mode).
- **No script removes an installed atom.** A failed combined check (`visudo -c` after S-D's renames, `sshd -t` after
  S-E's) does not delete files: the script renames each atom it just activated back to its inert name
  (`deactivated-equal`, atomic per atom, in reverse order) and stops. Removal of any object happens only in S-R or in
  rollback, by explicit operator choice, and only after full-byte equality with the reviewed bytes (a prefix is never
  "equal").
- **Service co-effects.** `systemctl daemon-reload` (images only) and `systemctl reload sshd` change in-memory
  configuration. Each is an atom whose state is observed (`systemctl show -p NeedDaemonReload -p FragmentPath -p
  DropInPaths` of the units the script changed; `sshd -T` for the effective `DenyUsers`), never inferred from a log.
  Enablement links of the image mount units (images only) are part of the enablement atom.
- **Step logs (advisory).** `step begin <k>` before and `step done <k>` after each atom append lines
  `<UTC time> (begin|done) <k>` to `log/S-<x>.log` through `step.py`, which writes the whole line and syncs it or
  fails, and which refuses to append after a torn line (§11.5). A log is evidence of what ran; no object's state is
  ever decided from it.

**The global atom table (without images)** (correction W1-V8-COMPOSED-ENUM). Atoms run one at a time in this order
(§16). n_d and n_m are the numbers of lines of `frame-dirs.list` and `frame-members.list`, which exist once the frame is
frozen; everything else is exact now. "I" lists the forward intermediates (each with its completing action and its
reversing action in §11.5's class table), "I_rev" the reversal intermediates. Checks change nothing and are not atoms.

| k | Script.step | Object (co-objects) | Class | post(k) | I(k) | I_rev(k) |
|---|---|---|---|---|---|---|
| 1 | A.1 | group `wlscratch` (W) (`group`, `gshadow` lines) | group | both lines | `group` line without `gshadow` | `gshadow` line without `group` |
| 2 | A.2 | group `wlscratch-ns` (N) | group | both lines | as k1 | as k1 |
| 3 | A.3-A.4 | account `wlscratch` (`passwd`, `shadow`) | account | both lines, locked, no spool | `passwd` without `shadow`; both, unlocked | `shadow` without `passwd` |
| 4 | A.5-A.6 | account `wlscratch-ns` | account-expired | both lines, locked, expiry 1, no spool | `passwd` without `shadow`; both, unlocked; locked, not expired | `shadow` without `passwd` |
| 5 | B.1 | `/var/lib/wlscratch` (`/var/lib` +name) | directory | root:W 0750, no ACL | present root:root umask mode; owner set, mode not | — |
| 6 | B.2 | `lease/` (`/var/lib/wlscratch` +name) | directory | root:W 0750 | as k5 | — |
| 7 | B.3 | `lease/writer.lock` (`lease/` +name) | file (direct) | root:W 0440, empty | any owner and mode; root:W wrong mode | — |
| 8 | B.4.1 | `runs/` | directory | W:W 0700 | as k5 | — |
| 9 | B.4.2 | `runs/records` | directory | W:W 0700 | as k5 | — |
| 10 | B.5.1 | ACL of `/var/lib/wlscratch` | ACL | §6.3 text | — | — |
| 11 | B.5.2 | ACL of `runs/` | ACL | §6.3 text | — | — |
| 12 | B.5.3 | ACL of `runs/records` | ACL | §6.3 text | — | — |
| 13 | C.1.1 | `/opt/wlscratch` (`/opt` +name) | directory | root:root 0755 | as k5 | — |
| 14 | C.1.2 | `/opt/wlscratch/frame-v6w1` | directory | root:root 0755 | as k5 | — |
| 15 … 14+n_d | C.2.i | the i-th frame directory | directory | root:root 0755 | as k5 | — |
| 15+n_d … 14+n_d+n_m | C.3.i | the i-th frame member | staged-rename file | `installed-equal`, root:root 0644 | `staged-partial`; `staged-attr`; `staged-equal` | `deactivated-equal` |
| 15+n_d+n_m | D.1 | `/etc/sudoers.d/wlscratch-frame` | staged-rename file | root:root 0440 | as C.3.i | as C.3.i |
| 16+n_d+n_m | D.2 | `/etc/sudoers.d/wlscratch-rl` | staged-rename file | root:root 0440 | as C.3.i | as C.3.i |
| 17+n_d+n_m | E.1 | `/etc/ssh/sshd_config.d/30-wlscratch.conf` | staged-rename file | root:root 0644 | as C.3.i | as C.3.i |
| 18+n_d+n_m | E.3 | sshd's loaded configuration | service action | `sshd -T` shows `denyusers wlscratch wlscratch-ns` | — | — |
| 19+n_d+n_m | H.1 | `/opt/wlscratch/setup-identities.json` | generated staged-rename file | root:root 0644, the generator's bytes | as C.3.i | as C.3.i |

So N = 19 + n_d + n_m state-changing atoms (JACKAL exact, parsed `4+5+3+2+2+1+1+1` gives 19).

**The reachable set.** With G_j the global vector after atoms 1…j (§11.4 of v7's definition, kept: every object's
P-capture with the effects of atoms 1…j applied, co-effects included), the states that setup, its resumption, its
reversal and its own deactivations can leave are exactly:
- G_0, …, G_N;
- G_j^+(s) for every atom k = j+1 and every s ∈ I(k): G_j with atom k applied as far as s;
- G_j^-(s) for every atom k = j and every s ∈ I_rev(k): G_j with the reversal of atom k applied as far as s; for the
  staged-rename atoms this includes the deactivated state that S-D's or S-E's failed combined check produces for the
  last atom it activated;
- D_SD: the state after S-D's failed `visudo -c` has deactivated both sudoers atoms (both `deactivated-equal`, every
  earlier atom in its post-state);
- The **`userdel` `USERGROUPS_ENAB yes` co-removal states** (correction W1-V9-ENUM-USERDEL). `/etc/login.defs` sets
  `USERGROUPS_ENAB yes`, so **each** account's `userdel` also removes the same-name user-private group: the reversal of
  k4 (`userdel wlscratch-ns`) co-removes group `wlscratch-ns` (k2's object), and the reversal of k3 (`userdel
  wlscratch`) co-removes group `wlscratch` (k1's object). v9 modelled only W_A (the k4 case); v10/v11 add the k3 case
  and the intermediate states under the file-update order (passwd before shadow for the account; group before
  `gshadow` for the group). **W_A** (already among v9's 63): k4 removed, group k2 co-removed, k1 and k3 in their
  post-states. The four **new** constant states are:
  - **X1:** inside k4's `userdel` (k4 absent), the co-removed group k2 mid-removal under the file-update order (group
    line gone, `gshadow` remains: k2 = "gshadow without group"), k1 and k3 in post;
  - **X2:** after W_A, inside k3's `userdel` (k3 absent, k2 absent), the account mid-removal under the file-update order
    (k3 = "shadow without passwd");
  - **X3:** from G_3 (k4 not created), inside k3's `userdel` (k3 absent), the co-removed group k1 mid-removal (k1 =
    "gshadow without group"), k2 in post;
  - **X4 = W_B:** k3 removed, group k1 co-removed, k2 in its post-state, k4 absent (the completed co-removal on the k3
    reversal path).
  S-R gains reverse and resume rules from W_A, W_B and X1–X3 that never issue a known-failing `groupdel` (§11.5).
  `/var/log/lastlog` (present, 0 bytes) is recorded as a possible `useradd`/`userdel` co-object of an account atom: S-R
  and S-I capture its state as data, never deciding from it.
Their number is 67 + 3·n_d + 5·n_m (JACKAL exact: parsed `4+5+3+2+2+1+1+1+1+7+10+4+6+3+3+4+0+0+2+1+1+1+1+1+1+1+1` gives
67, cross-check `63+4` = 67; Appendix I I1′, I1″), read as v9's 63 groups
(4+5+3+2+2+1+1+1)+1+(7+10+4+6+3+3)+(4+0+0+2+1+1)+1+1 — the G vectors, the forward intermediates, the reversal
intermediates, D_SD and W_A of the atoms whose count does not depend on the lists — **plus the four `userdel`
co-removal constant states X1, X2, X3 and X4 = W_B** (the reversal intermediates and completed co-removal that
`USERGROUPS_ENAB yes` adds for k3 as well as k4, W_A already being among the 63); the coefficients are `1+2` = 3 for
each frame directory (its G vector and two intermediates) and `1+3+1` = 5 for each frame member. The vectors
themselves are listed by the concrete inventory as the table above instantiated; every one is a table vector, and S-R
classifies any observation that is none of them as *other*.

**With images** (§14.5, S-J): k8 and k9 are replaced by the image atoms J1 (`/var/lib/wlscratch-images`, directory),
J2a and J2b (the two image files, class image: I = `allocated-partial` (size below the reviewed size), `allocated`
(any owner and mode), `allocated` root:root 0600 without a filesystem, `formatted-partial` (a superblock not matching the
reviewed UUID, label, geometry or features); I_rev none, one `unlink`), J4 (T_root's bare mount point, directory), J5a
and J7a (the two mount-unit files, staged-rename), J5b and J7b (enable and start each unit, class enablement: I =
enabled not active, active not enabled; I_rev = not enabled still active), the two `daemon-reload` service actions, J6a
and J8 (the image roots' owner and mode, class attribute: I = owner set, mode not), and J6b (R_root's bare mount point,
directory). Then N = 30 + n_d + n_m (JACKAL exact, parsed `4+5+3+2+2+1+1+1-2+13`), and the reachable set has
104 + 3·n_d + 5·n_m states (JACKAL exact, parsed
`4+5+3+2+2+1+1+1-2+13+1+7+10+4+6+3+3-4+26+4+0+0+2+1+1+4+1+1+1+1+1+1`, cross-check `100+4` = 104; Appendix I I2′, I2″;
read as the groups
(4+5+3+2+2+1+1+1-2+13)+1+(7+10+4+6+3+3-4+26)+(4+0+0+2+1+1+4)+1+1 plus the four `userdel` co-removal states X1-X4=W_B).

**S-R, reconciliation** (operator; interactive): after any stop the operator runs the reviewed `S-R <x>`, which
1. reads `log/S-<x>.log`: every complete line must match the grammar, and `begin` and `done` must alternate per atom
   in script order; a last line without a final newline is torn and is ignored (and reported); any other malformed or
   out-of-order line stops S-R for an explicit operator decision;
2. observes every object of the global object set (every object and co-object of the table, whichever script stopped),
   with the prestate methods (`getent`, `absent.py`, `lstat`, `getfacl -n -c -p`, digests, entry sets, link counts,
   `systemctl show`, `sshd -T`), each producer run under `check_out.py`;
3. classifies the whole observation against the reachable set: exactly one vector must equal it. An observation that
   equals none is *other* and stops S-R for an explicit operator decision (the existing reserved operator authority,
   not a new gate); a partial install, deactivation or reversal is never *other*;
4. offers the operator two actions, each needing an explicit choice, from the matched state:
   - **resume**: from G_j^+(s), run the completing action of atom j+1 for s; from G_j^-(s), first complete the reversal
     of atom j, which gives G_(j−1); from D_SD, rename both sudoers atoms back to their final names only after the
     operator has corrected the cause and `visudo -cf` passes on the inert names, which gives G_(16+n_d+n_m); from W_A,
     run atom 2's forward action (restore group k2), which gives the vector with k2 restored; from W_B, run atom 1's
     forward action (restore group k1); from an X1, X2 or X3 intermediate, first let the in-progress `userdel`
     co-removal complete to its W_A/W_B state, then resume from there; from G_j, run the forward action of atom
     j+1; then every later atom in order. No atom at or before the matched position is run again, whatever the log
     says;
   - **reverse**: from G_j^+(s) or G_j^-(s), first complete the reversal of the partial atom; from D_SD, remove both
     inert files after full-byte equality; then run the reversing action of atoms j, j−1, …, 1 in that order, each from
     its post-state to its pre-state with its co-effects (a staged-rename atom: rename back to its inert name, check
     equality, then remove), followed by `visudo -c`, `sshd -t` and `systemctl reload sshd` or `daemon-reload` where
     the object belongs to those services. At an atom whose same-name user-private group was already co-removed by a
     later `userdel` (states W_A, W_B, X1–X3), the reversal **confirms the group absent** (the co-removal already
     reached that group atom's pre-state) and continues with the next atom's reversing action; it does **not** issue a
     `groupdel` for that group, so no reversing command is a known-failing `groupdel` and S-R does not stop on it
     (W1-V9-ENUM-USERDEL; this removes the v9 defect where S-R's reversing `groupdel` of an already co-removed group
     failed and stopped S-R);
5. re-observes after each action and retains every capture; an action is complete only if the re-observation equals
   the expected vector;
6. stops on any failed command or unequal re-observation and reports it for an explicit operator decision.
S-R logs its own actions in a new log, `log/S-R<x>-<n>.log` (n the smallest unused, created with `O_EXCL`), and never
appends to the stopped script's log. Nothing is resumed or reversed without the operator's choice, and nothing is
called undone without equality. S-R lies inside the existing reserved privileged setup and rollback authority; it adds
no approval gate.

**Rollback is its own machine** (§15.1): an evidence-retaining rollback starts from runtime state (generations,
records, exports, captures), which setup's inverse vectors do not describe. Its states and their postconditions are
enumerated in §15.1.

### 11.5 Setup scripts (templates; texts and digests become exact in the concrete inventory) [corrections: W1-V8-COMPOSED-ENUM, W1-V7-COMPOSED-STATE, W1-V6-COMPOSED-STATE; v6: W1-V5-RECONCILIATION-STATES; v5: W1-SETUP-RECONCILIATION, W1-SETUP-IDENTITY, W1-CUSTODY-CLOSURE; v4: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY]

`<W>` and `<N>` are the fixed numbers. Every script begins with the same lines; only `S` and the `umask` differ (077,
except S-C and S-E, which use 022):
```sh
set -eu; umask 077
st=/root/wlscratch-staging
py='/usr/bin/python3 -I -B'
S=A
step() { $py "$st/step.py" "$1" "$S" "$2"; }
need_absent() { $py "$st/absent.py" "$@"; }
check() { $py "$st/check_out.py" "$@"; }
no_entry() {
  rc=0; /usr/bin/getent "$1" "$2" >/dev/null || rc=$?
  case $rc in
    2) : ;;
    0) echo "S-$S: $1 entry $2 exists" >&2; exit 10 ;;
    *) echo "S-$S: getent $1 $2 failed with status $rc" >&2; exit 13 ;;
  esac
}
staged_install() {
  # $1 staged source, $2 final path, $3 owner, $4 group, $5 mode
  d=${2%/*}; b=${2##*/}; t="$d/.$b.new"
  need_absent "$t" "$2"
  /usr/bin/install -o "$3" -g "$4" -m "$5" "$1" "$t"
  /usr/bin/sync -- "$t"
  check --empty -- /usr/bin/cmp -s "$1" "$t"
}
staged_activate() {
  # $1 final path
  d=${1%/*}; b=${1##*/}; t="$d/.$b.new"
  /usr/bin/mv -T -n -- "$t" "$1"
  /usr/bin/sync -- "$d"
  need_absent "$t"
}
staged_deactivate() {
  d=${1%/*}; b=${1##*/}; t="$d/.$b.new"
  /usr/bin/mv -T -n -- "$1" "$t"
  /usr/bin/sync -- "$d"
  need_absent "$1"
}
```
Every call of a helper or function is a simple command, or the whole right-hand side of an assignment, so under `-e`
its failure stops the script; §11.4 gives the status rules. `no_entry` accepts exactly the status 2 that §11.2 and
P1-P2 already expect for an absent entry, and stops on every other status. `staged_install` followed by
`staged_activate` is one staged-rename atom; its step boundaries are the intermediates of §11.4's class.

**`absent.py`** (reviewed helper, byte-identical to v4; exit 0 only if every operand is `absent`, 2 if any is
`present`, 3 if any is `undetermined`; one output line per operand):
```python
import errno, os, sys

def check(path):
    parts = path.split('/')
    if not path.startswith('/') or '' in parts[1:] or '.' in parts or '..' in parts:
        return 'undetermined', 'not a normalized absolute path'
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for name in parts[1:-1]:
            try:
                nxt = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            except OSError as e:
                return 'undetermined', 'component ' + name + ': ' + errno.errorcode.get(e.errno, str(e.errno))
            os.close(fd)
            fd = nxt
        try:
            os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
        except OSError as e:
            if e.errno == errno.ENOENT:
                return 'absent', ''
            return 'undetermined', errno.errorcode.get(e.errno, str(e.errno))
        return 'present', ''
    finally:
        os.close(fd)

worst = 3 if len(sys.argv) < 2 else 0
for operand in sys.argv[1:]:
    verdict, why = check(operand)
    print(verdict, operand, why)
    worst = max(worst, {'absent': 0, 'present': 2, 'undetermined': 3}[verdict])
sys.exit(worst)
```

**`step.py`** (reviewed helper; v5: it writes the whole line or fails, and never appends after a torn line):
```python
import os, re, sys, time

def main(argv):
    if (len(argv) != 4 or argv[1] not in ('begin', 'done')
            or re.fullmatch(r'[A-J]|R[A-J]-[0-9]+', argv[2]) is None
            or re.fullmatch(r'[0-9]+(\.[0-9]+)?', argv[3]) is None):
        return 2
    line = ('%s %s %s\n' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), argv[1], argv[3])).encode('ascii')
    try:
        fd = os.open('/root/wlscratch-staging/log/S-' + argv[2] + '.log',
                     os.O_RDWR | os.O_APPEND | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError:
        return 3
    status = 0
    try:
        size = os.fstat(fd).st_size
        if size > 0 and os.pread(fd, 1, size - 1) != b'\n':
            status = 3
        else:
            written = 0
            while written < len(line):
                n = os.write(fd, line[written:])
                if n <= 0:
                    status = 3
                    break
                written += n
            if status == 0:
                os.fsync(fd)
    except OSError:
        status = 3
    try:
        os.close(fd)
    except OSError:
        status = 3
    return status

sys.exit(main(sys.argv))
```
Exit 0 means that the complete line is in the log and synced; 2 is a usage error; 3 is everything else, including a
short or failed write and a log that ends in a torn line. A failed `step` stops the script, so a torn line can only be
the last line of a log, and S-R continues in a new log (§11.4).

**`check_out.py`** (reviewed helper; it runs one command, given by absolute path, without a shell, and checks the
command's own exit status and output):
```python
import os, subprocess, sys

def write_all(fd, data):
    done = 0
    while done < len(data):
        n = os.write(fd, data[done:])
        if n <= 0:
            raise OSError('short write')
        done += n

def main(argv):
    if '--' not in argv:
        return 2
    i = argv.index('--')
    opts, cmd = argv[1:i], argv[i + 1:]
    if not cmd or not cmd[0].startswith('/'):
        return 2
    if opts in (['--print'], ['--empty']):
        mode, arg = opts[0], None
    elif len(opts) == 2 and opts[0] in ('--equal', '--line-ci'):
        mode, arg = opts
    else:
        return 2
    try:
        done = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, check=False)
    except OSError:
        return 4
    if done.returncode != 0:
        return 4
    out = done.stdout
    if mode == '--print':
        try:
            write_all(1, out)
        except OSError:
            return 6
        return 0
    if mode == '--empty':
        return 0 if out == b'' else 5
    try:
        with open(arg, 'rb') as f:
            want = f.read()
    except OSError:
        return 2
    if mode == '--equal':
        return 0 if out == want else 5
    if not want.endswith(b'\n') or want.count(b'\n') != 1:
        return 2
    return 0 if want[:-1].lower() in [l.lower() for l in out.split(b'\n')] else 5

sys.exit(main(sys.argv))
```
Modes: `--equal FILE` (the output equals the staged expected bytes), `--line-ci FILE` (some output line equals the
single line of FILE, ignoring case), `--empty` (no output), `--print` (the output is copied to the helper's own stdout,
for an assignment). Exit 0 only if the command ran, exited 0 and the check holds; 4 if it could not run or exited
non-zero; 5 if the check failed; 6 if the helper's own output failed; 2 on a usage error. The command's stderr reaches
the operator unchanged.

**S-A, accounts and groups** (atoms k1-k4 of §11.4).
```sh
<common lines, S=A; umask 077>
lock_account() {
  line=$(check --print -- /usr/bin/getent shadow "$1")
  pw=${line#*:}; pw=${pw%%:*}
  case $pw in '!'*|'*'*) : ;; *) /usr/bin/usermod -L "$1" ;; esac
  line=$(check --print -- /usr/bin/getent shadow "$1")
  pw=${line#*:}; pw=${pw%%:*}
  case $pw in '!'*|'*'*) : ;; *) echo "S-A: $1 not locked" >&2; exit 12 ;; esac
  need_absent "/var/spool/mail/$1"
}
step begin 0
for n in wlscratch wlscratch-ns; do no_entry passwd "$n"; no_entry group "$n"; done
for i in <W> <N>; do no_entry passwd "$i"; no_entry group "$i"; done
need_absent /var/spool/mail/wlscratch /var/spool/mail/wlscratch-ns /var/lib/wlscratch-ns
step done 0
step begin 1; /usr/bin/groupadd --system --gid <W> wlscratch; step done 1
step begin 2; /usr/bin/groupadd --system --gid <N> wlscratch-ns; step done 2
step begin 3
/usr/bin/useradd --system --uid <W> --gid <W> --no-create-home --home-dir /var/lib/wlscratch \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame writer' wlscratch
step done 3
step begin 4; lock_account wlscratch; step done 4
step begin 5
/usr/bin/useradd --system --uid <N> --gid <N> --no-create-home --home-dir /var/lib/wlscratch-ns \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch view namespace owner' wlscratch-ns
step done 5
step begin 6
lock_account wlscratch-ns
/usr/bin/usermod -e 1 wlscratch-ns
line=$(check --print -- /usr/bin/getent shadow wlscratch-ns)
case $line in *:1:*) : ;; *) echo "S-A: wlscratch-ns not expired" >&2; exit 14 ;; esac
step done 6
```
A mail spool that `useradd` created despite P23 stops the script, and S-R classifies that account as *other*.
`/var/lib/wlscratch-ns`, the home that `passwd` names for N, is never created. (The expiry test matches the eighth
`shadow` field written by `usermod -e 1`; the concrete inventory replaces the pattern by an exact field comparison
under `check_out.py`.)

**S-B, writer home, lease, run tree** (without images; with images, steps 4.1 and 4.2 are replaced by S-J, §14.5, and
steps 5.1-5.4 apply to the image roots).
```sh
<common lines, S=B; umask 077>
step begin 0; need_absent /var/lib/wlscratch /opt/wlscratch; step done 0
step begin 1; /usr/bin/install -d -o root -g <W> -m 0750 /var/lib/wlscratch; step done 1
step begin 2; /usr/bin/install -d -o root -g <W> -m 0750 /var/lib/wlscratch/lease; step done 2
step begin 3
/usr/bin/install -o root -g <W> -m 0440 "$st/empty" /var/lib/wlscratch/lease/writer.lock
v=$(check --print -- /usr/bin/stat -c '%F %h %s %u %g %a' /var/lib/wlscratch/lease/writer.lock)
[ "$v" = "regular empty file 1 0 0 <W> 440" ]
step done 3
step begin 4.1; /usr/bin/install -d -o <W> -g <W> -m 0700 /var/lib/wlscratch/runs; step done 4.1
step begin 4.2; /usr/bin/install -d -o <W> -g <W> -m 0700 /var/lib/wlscratch/runs/records; step done 4.2
step begin 5.1
/usr/bin/setfacl -m u:1000:--x /var/lib/wlscratch
check --equal "$st/acl/var-lib-wlscratch.expected" -- /usr/bin/getfacl -n -c -p /var/lib/wlscratch
step done 5.1
step begin 5.2
/usr/bin/setfacl -m u:1000:--x /var/lib/wlscratch/runs
check --equal "$st/acl/runs.expected" -- /usr/bin/getfacl -n -c -p /var/lib/wlscratch/runs
step done 5.2
step begin 5.3
/usr/bin/setfacl -m u:1000:--x /var/lib/wlscratch/runs/records
check --equal "$st/acl/records.expected" -- /usr/bin/getfacl -n -c -p /var/lib/wlscratch/runs/records
step done 5.3
step begin 5.4
check --equal "$st/acl/lease.expected" -- /usr/bin/getfacl -n -c -p /var/lib/wlscratch/lease /var/lib/wlscratch/lease/writer.lock
step done 5.4
```
`$st/empty` is a staged empty file. The expected files hold exactly the §6.3 texts (and, for `lease`, only the base
entries).

**S-C, frame install** (from the verified staging copy of the frozen v6-W1 tree).
```sh
<common lines, S=C; umask 022>
step begin 0; need_absent /opt/wlscratch; step done 0
step begin 1.1; /usr/bin/install -d -o root -g root -m 0755 /opt/wlscratch; step done 1.1
step begin 1.2; /usr/bin/install -d -o root -g root -m 0755 /opt/wlscratch/frame-v6w1; step done 1.2
i=0
while read -r d; do
  i=$((i+1)); step begin "2.$i"
  /usr/bin/install -d -o root -g root -m 0755 "/opt/wlscratch/frame-v6w1/$d"
  step done "2.$i"
done < "$st/frame-dirs.list"
i=0
while read -r m; do
  i=$((i+1)); step begin "3.$i"
  staged_install "$st/frame/$m" "/opt/wlscratch/frame-v6w1/$m" root root 0644
  staged_activate "/opt/wlscratch/frame-v6w1/$m"
  step done "3.$i"
done < "$st/frame-members.list"
step begin 4; /usr/bin/sha256sum -c --strict "$st/frame-members.abs.sha256"; step done 4
```
The v6-W1 source is frozen with every member at 0644 and every directory at 0755, so installed modes equal frozen
modes; `frame-members.abs.sha256` names each installed member by its absolute path; the inventory records
`install_root = /opt/wlscratch/frame-v6w1` and `source_frame` (v5 checked `inventory['frame'] == FRAME`; the installed
frame checks `install_root` instead, and §4.6 binds `source_frame`).

**S-D, sudo rules** (reviewed bytes). `wlscratch-frame`:
```
Cmnd_Alias WLSCRATCH_W = /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py *
Defaults!WLSCRATCH_W !log_allowed, !pam_session, !pam_setcred, !use_pty
sicarii ALL=(wlscratch) NOPASSWD: WLSCRATCH_W
```
`wlscratch-rl` (the RL rule):
```
Cmnd_Alias WLSCRATCH_RL = /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py *
Defaults!WLSCRATCH_RL !log_allowed, !pam_session, !pam_setcred, !use_pty
wlscratch ALL=(root) NOPASSWD: WLSCRATCH_RL
```
```sh
<common lines, S=D; umask 077>
step begin 0
need_absent /etc/sudoers.d/wlscratch-frame /etc/sudoers.d/wlscratch-rl
/usr/bin/visudo -cf "$st/sudoers/wlscratch-frame"
/usr/bin/visudo -cf "$st/sudoers/wlscratch-rl"
step done 0
step begin 1
staged_install "$st/sudoers/wlscratch-frame" /etc/sudoers.d/wlscratch-frame root root 0440
/usr/bin/visudo -cf /etc/sudoers.d/.wlscratch-frame.new
staged_activate /etc/sudoers.d/wlscratch-frame
step done 1
step begin 2
staged_install "$st/sudoers/wlscratch-rl" /etc/sudoers.d/wlscratch-rl root root 0440
/usr/bin/visudo -cf /etc/sudoers.d/.wlscratch-rl.new
staged_activate /etc/sudoers.d/wlscratch-rl
step done 2
step begin 3
if ! /usr/bin/visudo -c; then
  staged_deactivate /etc/sudoers.d/wlscratch-rl
  staged_deactivate /etc/sudoers.d/wlscratch-frame
  echo "S-D: visudo -c failed; both rules deactivated to their inert names; run S-R D" >&2; exit 40
fi
step done 3
```
That the installed sudo honours these options as `sudoers(5)` states is premise P-SUDO; the options do not change the
rules' authority, and `!use_pty` keeps the frame commands in the caller's session as v5's frame was.

**S-E, sshd** (reviewed byte line `DenyUsers wlscratch wlscratch-ns`).
```sh
<common lines, S=E; umask 022>
f=/etc/ssh/sshd_config.d/30-wlscratch.conf
step begin 0; need_absent "$f"; step done 0
step begin 1; staged_install "$st/30-wlscratch.conf" "$f" root root 0644; staged_activate "$f"; step done 1
step begin 2
if ! /usr/bin/sshd -t; then
  staged_deactivate "$f"
  echo "S-E: sshd -t failed; drop-in deactivated to its inert name; run S-R E" >&2; exit 50
fi
rc=0; check --line-ci "$st/sshd-denyusers.expected" -- /usr/bin/sshd -T -C user=wlscratch,host=localhost,addr=127.0.0.1 || rc=$?
case $rc in
  0) : ;;
  *) echo "S-E: DenyUsers not shown by a successful sshd -T (status $rc); run S-R E" >&2; exit 51 ;;
esac
step done 2
step begin 3; /usr/bin/systemctl reload sshd.service; step done 3
```

**S-H, setup identity record** [correction: W1-SETUP-IDENTITY]. A reviewed generator, run as
`$py "$st/make_setup_identities.py" /opt/wlscratch/.setup-identities.json.new`, creates the inert file with `O_EXCL`,
0644, root:root and syncs it, holding: the numbers; for every setup object other than the record itself, its path, its
class (§11.7), the value of every field §11.7 pins for that class, and the names of the fields that class leaves
intentionally mutable (`mutable_fields`); the mount facts of T_root and R_root (with images: the pinned image facts, the
images directory with its exact entry set, and each image root's `lost+found`); the installed frame root identity and
member digests; the sudoers and sshd digests; the digests of `/etc/subuid`, `/etc/subgid` and of the new `passwd`,
`group`, `shadow` and `gshadow` lines. `staged_activate /opt/wlscratch/setup-identities.json` then renames it into place.
The record does not list itself and holds no digest, size or identity of its own bytes; its seal is external (§11.7). S-R
classifies a partial inert file by re-running the generator with `--print` under `check_out.py` and comparing.

**S-I, post-setup capture** (operator, read-only, every producer under `check_out.py`): the first character only of
each new `shadow` password field and N's expiry field; the `gshadow` lines of both user-private groups (no members,
locked); sudoers digests and `visudo -c`; `sudo -l -U` for `sicarii`, `wlscratch`, `wlscratch-ns` and every other
non-root account (no rule yielding W or N), the sudoers rule set read for any `%group`/`#uid`/alias/negation Runas
resolving to W or N, and the polkit inventory over every subject (P12, P13; W1-V9-NOOWNER-SCOPE); `sshd -T -C
user=wlscratch,…` and `-C user=wlscratch-ns,…`; no process with uid W outside writer instances and none with uid N;
no `user@<W>.service`, `user@<N>.service`, `/run/user/<W>` or `/run/user/<N>`; `absent.py` on
`/var/spool/mail/wlscratch`, `/var/spool/mail/wlscratch-ns` and `/var/lib/wlscratch-ns`; `/var/log/lastlog`'s state
recorded as data (W1-V9-ENUM-USERDEL); `find / -xdev -perm /6000 -type
f` and `getcap -r /usr` compared with P17, confirming no set-user-ID or file-capability object owned by W or N or
created by any installed path (W1-V9-RL-SELFTEST-FIXTURE); `find / -xdev \( -uid <W> -o -gid <W> \)` equal to exactly
the W-owned and W-group setup objects; `find / -xdev \( -uid <N> -o -gid <N> \)` empty; and the seal capture of
`setup-identities.json` (sha256, size, `[dev, ino]`, owner, group, mode, link count and `getfacl -n -c`; §11.7), which
the installed-evidence review records.

**Atom classes** (the reviewed table S-R uses; the concrete inventory adds each atom's exact captures; "—" means none).
States are global (§11.4): a class's pre-state is whatever the earlier atoms of the global sequence left on the objects
it touches, and its post-state is the state right after the atom, co-effects included. "Parent +name" means the
parent directory's entry set gains the name and, for a directory, its link count gains one; "parent −name" the
reverse.

| Class | Forward action | pre(k) | Forward intermediates I(k) (completing action; reversing action) | post(k) | Reversing action from post(k) | Reversal intermediates I_rev(k) (action that completes the reversal) |
|---|---|---|---|---|---|---|
| group | `groupadd --system --gid n name` | no `group` or `gshadow` line with the name or the number | the `group` line as expected without its `gshadow` line (—; `groupdel name`) | both lines as captured | `groupdel name` (no member, owns no file) | the `gshadow` line without its `group` line (—: an explicit operator decision) |
| account | `useradd …`, then `lock_account` | no `passwd` or `shadow` line with the name or the number | a `passwd` line without its `shadow` line (—; `userdel name`); both lines with an unlocked password field (`usermod -L name`; `userdel name`) | both lines as captured, the password field locked, no mail spool | `userdel name` without `-r` (owns no file); under `/etc/login.defs` `USERGROUPS_ENAB yes`, `userdel` also removes the same-name user-private group, for **each** account atom (k3 co-removes k1, k4 co-removes k2); the completed co-removal states are W_A (k4) and X4 = W_B (k3) with the file-update intermediates X1/X2/X3 (§11.4), and S-R does not then issue a `groupdel` for that group (it is already gone; §11.4 S-R reverse) | a `shadow` line without its `passwd` line (—: an explicit operator decision) |
| account-expired | as account, then `usermod -e 1` | as account | as account, plus: locked and not expired (`usermod -e 1`; `userdel name`) | as account, with expiry 1 | as account | as account |
| directory | `install -d -o -g -m path` | `absent`; parent without the name | the entry present (parent +name) as an empty directory with root:root and the umask's mode, or with the owner set and not the mode (`chown` and `chmod` to the expected values; `rmdir -- path`, which also gives parent −name) | a directory with the expected owner, group and mode, no ACL; parent +name | `rmdir -- path` (empty) | — (one `rmdir` call; the parent's entry and link count change with it) |
| file (direct; `writer.lock` only) | `install -o -g -m staged path` | `absent`; parent without the name | the entry present with any owner and mode (`chown`, `chmod`; `rm -- path`); root:W with another mode (`chmod`; `rm`) | a regular empty file, one link, root:W 0440, no ACL; parent +name | `rm -- path` | — |
| staged-rename file | `staged_install`, then `staged_activate` | `absent` at both names; parent without either | `staged-partial` (—; `rm -- inert`); `staged-attr` (`chown`, `chmod`; `rm -- inert`); `staged-equal` (`staged_activate`; `rm -- inert`), each with parent +inert name | `installed-equal`; parent +name | `staged_deactivate`, equality check, `rm -- inert` | `deactivated-equal` (`rm -- inert` after equality; or, in resume, `staged_activate`) |
| generated staged-rename file (`setup-identities.json`) | the generator into the inert name, then `staged_activate` | as staged-rename | as staged-rename, with "the generator's bytes" in place of the staged bytes | as staged-rename | as staged-rename | as staged-rename |
| ACL of one object | `setfacl -m entries path` | the object as earlier atoms left it | — (one `setxattr`) | pre(k) with the expected ACL text | `setfacl -b -- path`, then equality with pre(k) | — (one `setxattr`) |
| unit enablement (images) | `systemctl enable --now unit` | not enabled and not active | enabled and not active (`systemctl start unit`; `systemctl disable unit`); active and not enabled (`systemctl enable unit`; `systemctl stop unit`) | enabled and active, with §3.4's mount entry, and the enablement link present in its `.wants` directory | `systemctl disable --now unit`, after §15.1's checks | not enabled and still active (`systemctl stop unit`) |
| image file and filesystem (images) | `fallocate`, `chmod 0600`, `chown root:root`, `mkfs.ext4` | `absent`; the images directory without the name | `allocated-partial` (—; `rm -- path`); `allocated` with any owner and mode (`chmod`, `chown`, `mkfs.ext4`; `rm`); `allocated` root:root 0600 without a filesystem (`mkfs.ext4`; `rm`); `formatted-partial` (—; `rm`) | root:root 0600, the reviewed size, ext4 with the reviewed UUID and label; the images directory +name | `rm -- path`, after it is unmounted and no loop device uses it | — (one `unlink` call) |
| attribute (images: image root owner and mode) | `chown`, `chmod` | the image root as `mkfs.ext4` left it | owner set, mode not (`chmod`; `chown root:root` and `chmod 0755`) | the expected owner and mode | `chown root:root`, `chmod 0755` | — |
| check | the command | no object | — | no state | none: a check is never reversed, and runs again only when resume reaches it | — |
| service action | the command (`daemon-reload`, `systemctl reload sshd`, with the checks that follow it in the same step) | no object | — | its observable effect (`NeedDaemonReload=no` and the expected `DropInPaths` and `FragmentPath`; `sshd -T`) | run again after the reversal of the objects it concerns | — |

A rollback atom (§15.1) is one of these reversing actions run as an atom of the rollback's sequence; its
intermediates are the class's reversal intermediates with their co-effects. Every state not given by this table and
§11.4's reachable set is *other*: S-R stops and reports it for an explicit operator decision. A state that the setup,
its resumption, its reversal, its deactivations or the rollback reaches is never *other*.

### 11.6 Post-setup verification

- Lead (unprivileged): `getent` for the two identities; `lstat` and `getfacl -n -c` of `/var/lib/wlscratch`, `runs/`
  and `runs/records` compared with the pinned fields of `setup-identities.json` (§11.7) and §6.3; the installed frame
  listed and hashed member by member against the frozen inventory, with §11.1's regular-file and directory rules, no
  extra entry (no inert `.new` name) and no ACL; `/var/lib/systemd/linger` equal to P15; no process with uid N;
  `/etc/subuid` and `/etc/subgid` unchanged.
- Through the selftest verbs (W, and RL with L, C and O): `lease/` and `writer.lock` identities, role identities and
  readbacks; one view of each kind built on the sacrificial selftest generation and recorded (its namespace
  identities, maps, binds, Landlock ruleset, seccomp state, credentials and the original observations of §8.4 taken
  inside it) as the candidate view baseline, which is **evidence only** — reviewed with the installed evidence before
  adoption (§16) and **never used as a comparison baseline** (the only new comparison baseline is the writer-context
  one of §8.4; W1-V9-FORM-CONSISTENCY); and the
  installed steps I-1 to I-8 of §13.2.
- Operator: S-I, and P-SUDO's before/after capture (O-3, §16.1).

### 11.7 Setup identities: pinned and intentionally mutable fields [corrections: W1-V6-IMAGE-PIN, W1-V6-INVARIANTS; v6: W1-V5-IMAGE-PINS; v4: W1-SETUP-PROBES-ROLLBACK]

Every later invocation, and every invocation after a reboot, compares only the pinned fields; it observes and records
the mutable ones in its role or stage identity and never compares them with setup-time values. A change of a pinned
field refuses before any mutation, except in `adopt`, whose one exception is stated exactly below.

| Object class | Pinned (compared at every use) | Intentionally mutable (recorded, never compared with setup values) | Constraint on the mutable part |
|---|---|---|---|
| Regular setup files: `writer.lock`, the sudoers files `wlscratch-frame` and `wlscratch-rl`, the sshd drop-in, every installed frame member | type, `dev`, `ino`, uid, gid, mode, `nlink` 1, size, sha256 (`writer.lock`: size 0), no ACL | atime, mtime, ctime | none |
| `setup-identities.json` (never listed in itself; sealed from outside, below) | fixed values checked at every use: type regular, uid 0, gid 0, mode 0644, `nlink` 1, no ACL; sha256, size, `dev` and `ino` compared with the seal below, never with the record's own content | atime, mtime, ctime | none |
| Static setup directories: `/var/lib/wlscratch`, `lease/`, `/opt/wlscratch`, the installed frame directories | type, `dev`, `ino`, uid, gid, mode, exact ACL text, exact entry set, `nlink` | atime, mtime, ctime (they move only with the entry set, which is pinned) | none |
| Growing tree directories: `runs/` (T_root) and `runs/records` (R_root) | type, uid, gid, mode, exact ACL text; without images also `dev` and `ino`; with images the mount identity of the next row instead | `nlink`, size, atime, mtime, ctime, the entry set | every entry obeys §3.4's name grammar and is a W-owned directory, except, with images, the pinned `lost+found` special entry of §3.4; W checks it at every invocation |
| Image mounts (images only, §14.5) | filesystem UUID and label; the backing image file's `dev`, `ino`, size, mode 0600, uid 0, gid 0 and `nlink` 1 on the root filesystem, read by W and W2 through the images directory (§3.4, §14.5 J1); the mount point path; mount options `nosuid,nodev,noexec`; the nesting (records inside work); the image root's uid, gid, mode, ACL and `ino` | the mounted filesystem's `st_dev` (the loop device number), the loop device name, the mount ID | `st_dev` differs from the parent's and equals the device of the mountinfo entry whose loop device's backing file is the pinned image file |
| Images directory `/var/lib/wlscratch-images` (images only) | type, `dev`, `ino`, uid 0, gid W, mode 0750, no ACL, and the exact entry set (the two pinned image file names), which W and W2 compare at every use by listing the directory through their anchored descriptor (§3.4) | atime, mtime, ctime | W and W2 can list and search it but not write it; the image files stay root:root 0600 |
| `lost+found` of each image root (images only) | name, type directory, `ino`, uid 0, gid 0, mode 0700, no ACL | `nlink`, size, times, contents (root's; `e2fsck` may add entries; W cannot read them) | never used, opened or walked by the frame |
| Bare mount points (images only; observed at setup and rollback while unmounted) | type, `dev`, `ino`, uid 0, gid 0, mode 0700, empty, no ACL | times | must be empty |
| Accounts W and N | the `passwd` and `group` lines, the `shadow` password field's lock prefix, N's expiry field 1 | the other `shadow` fields | none |

The setup identity record stores, for every object other than itself, the class and the pinned values. Every field
pinned "at every use" is one that the comparing role can read with its own credentials. The images directory is
root:W 0750, so W and W2 list it and compare its exact entry set at every use, as the sealed W1-V5-IMAGE-PINS
correction requires (correction W1-V6-IMAGE-PIN); no operator gate is added. The listing exposes the two file names,
which `setup-identities.json` already states; W gains no write access and no access to the image files' bytes. RL,
which runs as root, repeats the same comparison before it builds a view (§3.4), and also requires the account lines of
N to equal the pinned ones.

**Seal of `setup-identities.json` [correction: W1-SETUP-IDENTITY].** The record never lists itself: S-H's generator
leaves it out of every class, so its bytes hold no digest, size or identity of themselves and no fixed point is
needed. Its final bytes are bound from outside, in this order: (1) S-I captures its sha256 (S), size, `[dev, ino]`,
owner, group, mode, link count and ACL text; (2) the installed-evidence review (INSTALLED_REVIEW) reviews that capture
and records S (§4.6, join 2); (3) `adopt` requires, before it writes `lead-adoption.json`, that the live file's sha256
is the S of the installed review it joins, and the adoption record binds S with the size and `[dev, ino]` W read
(`setup_identities_file`, Appendix B.3). Every later invocation opens the live file through an anchored no-follow chain,
checks the fixed values (regular, uid 0, gid 0, mode 0644, one link, no ACL), computes its sha256 and size from the
bytes it reads, and compares them, with `[dev, ino]`, with a seal:
- `dispatch`: before its first mutation, the committed adoption record's values (D3), and also the values
  `generation.json` recorded, so a generation materialized under another setup record is refused;
- `seal-front` (W2): before its first mutation, the values its attempt sealed (the adoption record pinned in a
  dispatch attempt's `attempt.json`; `generation.json`'s recorded values for A0);
- `materialize`: before its first mutation, the committed adoption record of the installed inventory I if one exists;
  otherwise there is no reviewed seal yet, and W records the values in `generation.json` with `setup_seal: unadopted`
  (v5's `materialize` does not depend on adoption, §4.6); such a generation is admitted only after `dispatch` finds
  those values equal to the adoption record's;
- `adopt` (the one exception to "before any mutation"; correction W1-V6-INVARIANTS): AD3's bookkeeping precedes the
  comparison, and it is exactly this: if absent, the directories `P_ado(I)`, `P_ado(I)/commits/` and
  `P_ado(I)/invocations/`; the directory `invocations/<stamp>/`; `invocation.json` and its markers; and the channel
  segments committed before AD5. The comparison is made at AD5, against the installed review, before
  `lead-adoption.json` is written; a mismatch is `REFUSAL`, no adoption record exists, and the bookkeeping stays as
  evidence;
- `selftest`: records the values only, because the selftests precede the installed review.
For every verb but `adopt` a mismatch refuses before any mutation. The pinned and intentionally mutable fields of
every other object stay as tabled above; the record's own atime, mtime and ctime are recorded and never compared.

## 12. The target view [corrections: W1-V8-HOLDER-IOEXIT, W1-V8-WRITER-AS-W; v8: W1-V7-ARCHITECTURE, W1-V7-VIEW-ROOT, W1-V7-FULL-DOMAIN; v7: W1-V6-PRESERVE, W1-V6-READ-MUTATION; gap: exposure-options]

### 12.1 The design adopted

v9 keeps v8's same-identity view (§0.4, §22), with the namespace owner N and the asynchronous-submission filter.
Like every earlier view it is privileged code, installed only by the operator inside the existing reserved setup (S-C,
S-D) and removed by its rollback (§15.1); no approval gate is added. It changes no host identity, reconstructs no root,
hides nothing of the host except what the two binds (and, when needed, the skeleton) cover, and needs no lead
preparation.

### 12.2 RL and the view, exactly

**Stage 1** (`sandbox_launch.py launch …`, `observe …` or `selftest …`, root, started by S2 or S_O):
1. First act (§7.7); role identity; argv grammar (verb, g, A, the helper nonce `n_wl` or `n_o`, the observer index for
   `observe`, and the seals: `launch.json` and `admission.json` sha256 for `launch`, `observer-intent-<n>.json` sha256
   for `observe`).
2. Invoker: `SUDO_UID` is W, and its nearest ancestor that is not a `sudo` process has uid W. RL trusts nothing else
   from W: every input it uses it reads itself from T and checks against its argv's seals.
3. Descriptors: exactly 0-2 (fd 0 a socket, fds 1-2 regular files owned by W in P_att or in `w2-<k>/`), verified in
   `/proc/self/fd`.
4. Anchors (§3.4) and records (`O_NOATIME`): A_T and g by anchored chains, compared with `setup-identities.json` and,
   with images, the missing-mount checks and the images directory's exact entry set; g's committed
   `materialization.json`; for `launch`, `launch.json` and `admission.json` read from P_att with sha256 equal to the
   seals, which give the view specification, `process_attributes` and U; for `observe`, `observer-intent-<n>.json`;
   the account lines of N equal to the pinned ones (§11.7).
5. Censuses and root scan (§9.4): U absent (for `launch`) or the observer scope name unused; every other RL scope
   absent or `populated 0` (K) and not live in the manager (M). As root, RL also reads `/proc/<pid>/status` and
   `/proc/<pid>/ns/user` of every process and requires that no process has uid N in any position, and that every process
   whose user namespace has owner N (`NS_GET_OWNER_UID`) lies in an RL scope; a failure is premise evidence (P-NOOWNER,
   P-SETNS, P-CG) and refuses.
6. `RLIMIT_CORE` (0, 0); then `exec` of `/usr/bin/systemd-run --scope --quiet --slice=user-1000.slice --unit=<U>`
   `-p MemoryMax=8G -p MemorySwapMax=0 -p LogLevelMax=warning` plus the scope properties of §8.3 (an observer scope
   `wlscratch-o-<g12>-<A>-<n>.scope` carries no memory properties, because v5 took its observations in the unscoped
   frame process), `-- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py <verb>-scoped <the same
   arguments>`.

**Stage 2** (the same pid, now in the scope, root):
7. First act, identity, argv, the reads of step 4 again; its cgroup is `/user.slice/user-1000.slice/<U>` and U holds
   exactly this pid. RL records, before any namespace change, the initial namespace's identities: `/proc/self/ns/mnt`
   inode and `NS_GET_MNTNS_ID`, which must equal PID 1's (`/proc/1/ns/mnt`), and `statx("/")` with
   `STATX_MNT_ID_UNIQUE` and `[dev, ino]`.
8. **Mount namespace and the process root**: `unshare(CLONE_NEWNS)`. The kernel copies the whole mount tree of the
   initial namespace (every mount present at that moment, FUSE and network mounts included, without calling into any
   filesystem, P-MSET) and moves this process's root and cwd to the copies (P-ROOT); no `open_tree` of the root and no
   `move_mount` or `pivot_root` is used for the root. Then `mount_setattr("/", AT_RECURSIVE, {attr_set:
   MOUNT_ATTR_NOSUID, propagation: MS_PRIVATE})` and `chdir("/")`. The namespace is owned by the initial user namespace.
9. Network namespace: `unshare(CLONE_NEWNET)`; the loopback interface brought up; nothing else.
10. **User namespaces** (correction W1-V8-WRITER-AS-W). U8: RL forks a helper that calls `setgroups(0, NULL)`,
    `setresgid(N, N, N)`, `setresuid(N, N, N)`, `prctl(PR_SET_DUMPABLE, 0)` and `unshare(CLONE_NEWUSER)`, so U8's owner is
    N; RL, as root in the parent namespace, writes U8's `setgroups` (`allow`), `uid_map` and `gid_map` (`0 0 4294967295`:
    every id maps to itself, JACKAL exact, parsed `2^32-1`; the highest id is 4294967294, JACKAL exact, parsed
    `4294967295-1`), opens `/proc/<helper>/ns/user`, signals the helper and reaps it; the helper runs no other code. M_run
    (the idmap of the binds, which no process ever enters): created the same way, with `uid_map` and `gid_map` `W 1000
    1`. The concrete inventory states every map line. After this step no process with euid N exists (RL re-reads
    `/proc` for the helper's pid and requires it reaped).
11. **The two binds and the run-path presentation.** For each of (`<RUNS>/<label>/source`, g/source) and (`TMPDIR` =
    `/home/sicarii/.cache/workflow-tmp`, g/tmpdir): RL resolves the destination in the new namespace from `/`
    component by component (`openat2` with `RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS`, `O_PATH|O_DIRECTORY`; lookups
    change no atime).
    - If every component exists as a directory: `open_tree(<held g directory>, "", OPEN_TREE_CLONE|AT_EMPTY_PATH)`,
      `mount_setattr` with `MOUNT_ATTR_IDMAP` (M_run), `MOUNT_ATTR_NOSUID` and private propagation, and `move_mount`
      onto the resolved destination (mode `bind`).
    - Otherwise (mode `skeleton`): let D be the deepest resolved directory. RL opens D with
      `O_RDONLY|O_DIRECTORY|O_NOATIME` (root may) and lists it; creates a `tmpfs` (`fsopen`, `fsconfig` `mode=` and
      `uid=`/`gid=` equal to D's mode, owner and group, `fsmount` with `MOUNT_ATTR_NOSUID`); creates in it a placeholder
      for every entry of D (an empty directory for a directory, an empty regular file for any other type) and the
      missing chain of directories down to the destination (each 0700, owner 1000:1000, as v5's `materialize` would
      have created `<RUNS>` and `<RUNS>/<label>`); attaches the `tmpfs` over D (`move_mount`); attaches
      `open_tree(D's fd, <entry>, OPEN_TREE_CLONE|AT_RECURSIVE|AT_SYMLINK_NOFOLLOW|AT_NO_AUTOMOUNT)` onto every
      placeholder (`nosuid`, private); remounts the `tmpfs` read-only; and attaches the g bind as above at the end of
      the chain. No host filesystem is written. That the clone of a symlink entry attaches onto its placeholder, and
      that no step calls into a mounted filesystem, is premise P-SKEL; an entry RL cannot attach is omitted from the
      view and recorded (a change, §21 V8), never a refusal.
    No other mount is added, removed or changed: every other host mount stays in the copy, unchanged apart from
    `nosuid` and propagation.
12. **Verification independent of mountinfo**: `NS_GET_MNTNS_ID` of `/proc/self/ns/mnt` differs from the initial
    namespace's (step 7); `statx("/")` has the initial root's `[dev, ino]` and a mount ID different from the initial root
    mount's, and `statmount(<that ID>, STATMOUNT_MNT_NS_ID|…)` reports the new namespace's ID; `statx(".")` equals
    `statx("/")` (the cwd is the root); for each bind, the destination resolved as in step 11 is a mount root
    (`STATX_ATTR_MOUNT_ROOT`) whose `[dev, ino]` is the held g directory's and whose `statmount` reports
    `MOUNT_ATTR_IDMAP`, `MOUNT_ATTR_NOSUID` and private propagation; `statmount` of `LSMT_ROOT` and the mount list
    (`listmount`) of the namespace show every mount `nosuid`. Every descriptor opened before step 8 except fds 0-2 is
    closed now; fds 0-2 refer to W's socket and W's stream files on host mounts by design. **Every descriptor RL opens
    after step 8 — the held g directory, the helper's user-namespace fd, the `open_tree` fds, the Landlock ruleset fd
    and the seccomp program fd — is opened `O_CLOEXEC` or is explicitly closed before `execve` (step 16); RL verifies
    immediately before `execve` that its exact open-fd set is {0,1,2}, which pairs with G4's and C1's exact {0,1,2}
    check (§9.3, W1-V9-INVENTORY).** RL also reads
    `/proc/self/mountinfo` for the record, as data, not as the verification.
13. **Landlock**: a ruleset that handles `LANDLOCK_ACCESS_FS_MAKE_SOCK`, `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` and
    `LANDLOCK_ACCESS_FS_REFER`, with a path-beneath rule granting `REFER` on `/` and rules granting `MAKE_SOCK` on the
    two bind roots; no rule grants `RESOLVE_UNIX`; no scope flag and no network rule. RL applies it with
    `landlock_restrict_self` while it holds `CAP_SYS_ADMIN` (so `no_new_privs` is not needed and not set).
13b. **The asynchronous-submission filter** (correction W1-V8-HOLDER-IOEXIT). RL installs one seccomp filter
    (`seccomp(SECCOMP_SET_MODE_FILTER, 0, …)`, permitted because RL holds `CAP_SYS_ADMIN`; no `no_new_privs`) whose
    classic BPF program is, in full: load `arch`; if `arch == AUDIT_ARCH_AARCH64`: load `nr`; if `nr == 0`
    (`io_setup`) or `nr == 425` (`io_uring_setup`) return `SECCOMP_RET_ERRNO | ENOSYS`, else return
    `SECCOMP_RET_ALLOW`; if `arch == AUDIT_ARCH_ARM`: load `nr`; if `nr == 243` (`io_setup`) or `nr == 425`
    (`io_uring_setup`) return `SECCOMP_RET_ERRNO | ENOSYS`, else return `SECCOMP_RET_ALLOW`; any other `arch`: return
    `SECCOMP_RET_ALLOW` (this kernel has only these two system-call tables). The numbers are those of the installed
    build's generated tables (Appendix I); the program's bytes and sha256 are part of the reviewed concrete inventory and
    of `RL_IDENTITY`. RL then reads `/proc/self/status` (`Seccomp: 2`, `Seccomp_filters: 1`). `ENOSYS` is what a kernel
    built without AIO or `io_uring` returns, so the target sees the same behaviour as on such a kernel. No other
    system call is filtered (§12.3 V14).
14. **Credentials**: `setns` into U8 (RL, root of the initial namespace, holds `CAP_SYS_ADMIN` over it); bounding set
    reduced only to F's recorded `CapBnd` (normally the full set, as the lead's); `setgroups` to F's recorded
    supplementary groups; `setresgid(1000, 1000, 1000)`; `setresuid(1000, 1000, 1000)`, which clears the permitted,
    effective and ambient sets; verify `/proc/self/status` (uids and gids 1000 in all positions, the groups, `CapPrm`,
    `CapEff`, `CapAmb` and `CapInh` zero, `CapBnd` equal to F's, `NoNewPrivs: 0`, `Seccomp: 2`), `NS_GET_OWNER_UID` of
    `/proc/self/ns/user` equal to N, and the maps. Seen from the initial namespace the process now has uid 1000, gid 1000
    and the lead's groups: its host identity is the lead's.
15. **Process attributes and environment**: every attribute of §8.3's table from `launch.json`; the environment is
    `launch.json`'s for L and the same target environment for O.
16. `RL_IDENTITY` on fd 0 (§7.3, with the fields of §9.3 G3); then `execve` of L or O. The new image is loaded through
    the view's root, so its mappings belong to the new namespace; L and C verify `/proc/self/exe` by `statx` mount ID
    against the record.

**Failures.** Any failed step writes the step and errno to RL's stderr and exits non-zero before `RL_IDENTITY`;
nothing else is sent, and no L or O exists (§9.5).

**New trust.** RL is privileged code behind a passwordless rule that any writer instance can call with any arguments,
so it must be robust to arbitrary input; it reads its inputs only from T and checks them against its argv's seals.
Because U8's maps include host root and every mount is `nosuid`, P-NOSUID and P-NOCAP are critical: a set-ID root
`exec` inside U8 would hold every capability in U8 and, through the identity map, DAC override over every host inode.
Because N owns every U8, P-NOOWNER is critical in the same way. Their discharge (S and P, §13.2) is required before any
installed use, and their refutation requires redesign (for example, leaving 0 unmapped, at the cost of a further change
of every root-owned object's apparent owner).

### 12.3 What the view changes for the target (the complete inventory known to the author)

Each item is a change of the original success domain unless the relation of §21 shows that no original accepted or
refused case observes it. None is presented as preserving; none narrows an accepted case by rule.

| Id | Change against v5 | Mechanism | Needed for |
|---|---|---|---|
| V1 | no host network: a private network namespace with only loopback; no external connectivity, no host loopback service, abstract UNIX sockets only among the view's processes | N1 | inbound abstract-socket channels (no other available mechanism scopes them) |
| V2 | no `connect`, and no `sendmsg` with an address, to a pathname UNIX server created outside the domain (`sicarii`'s buses, managers, agents, compositor, `/dev/log`, WORLDLINE daemons): `EACCES`; no socket file created, renamed or linked outside the two binds: `EACCES` | Landlock | outward and inward pathname channels |
| V3 | no mount, unmount, move or `pivot_root`, also in nested user namespaces | Landlock (inherent to any handled filesystem right) | follows from V2's mechanism |
| V4 | set-ID programs and file capabilities confer nothing; mounts show `nosuid` | `nosuid` | P-NOCAP |
| V6' | host mounts made after the view's creation do not appear in it, and host unmounts do not remove copies; every mount present at creation appears | private propagation | substitution of the run path by a later host mount |
| V7' | `TMPDIR` is private to the generation (other processes' files in the lead's `TMPDIR` are invisible, and the target's are invisible to them); `/tmp`, `/var/tmp`, `/dev/shm` and `/run/user/1000` are the host's | the g/tmpdir bind | socket files of `why3server` and other tools in `TMPDIR` must be unreachable from outside |
| V8 | `<RUNS>/<label>/source` is a mount root (the target cannot rename or remove it) whose contents are g's; the run directory holds none of v5's records and snapshot; with the skeleton, the levels from D down are a read-only `tmpfs` (creations there fail with `EROFS`), D's entries are separate mounts (renames and links between them fail), host entries created in D after the view's creation do not appear, and an entry RL could not attach is absent | binds, skeleton | location custody of the generation; no frame or lead write outside T |
| V10' | U is a system-manager scope directly in `user-1000.slice`, not a user-manager scope in `app.slice`: `app.slice`'s shared limits (24 GiB maximum, 20 GiB high, 16 GiB swap on 2026-10-05) and `user@1000.service`'s do not apply, the sibling set for CPU and I/O weights differs, and `systemctl --user` does not list it; `MemoryMax`, `MemorySwapMax` and the matched properties of §8.3 are v5's or the original's | §8.3 | a scope no non-root process can enter or leave (H(U)) |
| V12 | a Landlock domain: the target can stack its own; its ptrace reaches only its own domain | Landlock | V2 |
| V13 | the namespace-qualified effects of U8: no ptrace-mode access between the target and any process outside its namespace in either direction (`/proc/<pid>/{environ,fd/*,cwd,root,exe,mem}`, `pidfd_getfd`, `process_vm_*`, attach); per-user namespace accounting (user and mount namespaces, inotify instances and watches, and the other ucounts) charged at the initial level to N and counted per U8 for the target, and `RLIMIT_NPROC` counted over the target's own processes only; the user namespace is a child of the initial one (nested namespaces are one level deeper) | U8 | the pull closure (N2) |
| V14 | Linux native AIO (`io_setup`) and `io_uring` (`io_uring_setup`) fail with `ENOSYS`, as on a kernel built without them; `/proc/self/status` shows `Seccomp: 2` and `Seccomp_filters: 1`; a program that requires either interface fails or falls back (for example to POSIX AIO, which glibc implements with threads) | the seccomp filter of §12.2 step 13b | H(U)'s absorbing property: the only write paths that outlive their task (§9.8 N4) |
| V15 | between the run tree, `TMPDIR` and any other host path, `rename`, `link` and `renameat2` fail with `EXDEV` (in v5 these shared one mount, mount ID 32); the errno is `EXDEV` only when resolution and every earlier check pass | the two binds are distinct mounts (P-XMNT) | the target cannot move or hard-link an entry across the run tree / `TMPDIR` / host boundary, which v5's single mount allowed |
| V16 | through M_run (uid/gid `W 1000 1`) the target cannot `chgrp` an entry below `source/` to a supplementary group and cannot set an ACL entry naming an id other than 1000; an unmapped id shows as the overflow id | M_run idmap (P-IDMAP) | enforced-location identity of generation bytes (on-disk W) |
| V17 | the view's keyrings are per user namespace (U8): a session/user keyring in the view is not the host's, and host keyrings are unreachable from the view | U8 | follows from the user namespace (V13) |

v7's V5 (host identity R and GATE), V6's first half (unreproduced mounts), V7's private `/tmp`, V9 (masks) and V11
(lead-created mount point) stay removed. Frame-side changes are in §21.

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
pull-attempt actor of v9 (A1w) is **not** an installed-reachable actor in v11: the euid-W-towards-a-view-process
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
records its raw outputs, environment pins and date. **Nothing in this plan was executed for v11.**

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

## 14. Resources, staged Gate 0 and images [corrections: W1-IMAGE-TREE; gap: resources-and-images]

Every derived number below was computed with actual MCP `jackal_exact`: v3's computations (reproduced by the sealed
gpt61-v3 review) are carried, v4's are recorded in `v4-support/jackal.json`, v7's in `v7-support/jackal.json`, v8's in
`v8-support/jackal.json` and v9's in `v9-support/jackal.json` (Appendix I). Each result has status `exact`, `formal`
false, lane `rat`, and the non_claims "NOT formal-bounded: this lane carries no Lean-checked certificate", "The
epistemic class above is the STRONGEST claim this result supports", "exact rational arithmetic (not yet
checker-covered)". No consequence ceiling field was returned; the results are informational arithmetic only. Exact is
not formal-bounded. The "approx" figures are the tool's decimal display of the exact value. v9 changes no allowance
downward; it keeps v8's capture allowance (§14.7).

### 14.1 Gate 0 of runbook v4.3, unchanged

Allowances (labelled judgments; runbook v4.3 = v4.2 plus O1's corrected provenance, values identical): A_mat 16777216;
A_obj 2242440646; A_rec 545393048; A_ambient 1468268019712/1397; R = A_mat + A_obj + A_rec. Required = A_mat + A_obj
+ A_rec + A_ambient + R = 9304350902252/1397 (reproduced by the re-review, parsed
`2*(16777216+2*1121220323+545393048)+1468268019712/1397`). Reserve 10000000000, unchanged. The allowances are never
lowered because a run used less, and an observation can only raise them.

### 14.2 W-1 allowances (labelled judgments)

| Id | Covers | Bytes | Basis (JACKAL parsed input) |
|---|---|---|---|
| A_idf | F's real-context runtime-closure observations, full form, three stages, × 2 (A_rec's convention) | 152953998 | `2*3*25492333` (O2 runtime-closure size 25492333, observed) |
| A_in | retained inputs and messages: descriptors, lead module, observation inputs, front records, channel segments (headers and references, no bulk duplicate), role identities with module closures, F-captured W diagnostics, and `adopt`'s verify-only inputs, which are copied into the adoption payload pack (§15.3) | 134217728 | `128*2^20`, judgment. Largest comparable observed inputs: the v5 frame-review roster, 979762 bytes (`49133+602614+68556+250916+8543`); the base descriptors, 108768 (`1735+105491+1542`); lead module 8639 and START 2699 bytes (observed) |
| A_exp | export copies, each retained record at most once | 832564774 | `545393048+152953998+134217728` (A_rec + A_idf + A_in) |
| A_retry | partial primaries and retries, each record at most twice | 832564774 | same expression |
| A_fb | the fallback journal | 16777216 | `16*2^20` (fixed by design) |
| X | all W-1 retained additions: A_idf + A_in + A_exp + A_retry + A_fb | 1969078490 | `2*545393048+3*152953998+3*134217728+16777216`; the check, echoed as parsed `152953998+134217728+545393048+152953998+134217728+545393048+152953998+134217728+16777216-1969078490` (the tool flattened the submitted grouping parentheses), gives 0 |
| A_tmp | target temporaries (the view's `TMPDIR`, g/tmpdir; and the host `/tmp`, `/var/tmp` and `/dev/shm` the target uses): not retained by the frame except in the capture, peak use | 268435456 | `256*2^20`, judgment; no observation exists and v4.3 has no such term; the first observation can only raise it |
| A_jrnl | sudo, PAM, journal and unit effects of the scopes, per stage (minimized by §9.8 N5) | 134217728 | `128*2^20`, judgment |
| A_install | installed frame: code and the original baselines | 115303191 | `3*38434397`; the 17 v5 frame members total 38434397 bytes (`13976+19614+922860+4986+5773785+3198141+26383551+4153+1974792+1467+5300+7869+4763+749+755+745+116891`, member sizes observed in `frame-inventory.json`) |
| A_homes | setup directories and the lock file | 1048576 | `1*2^20`, judgment (kept; no allowance is lowered) |
| A_setuprec | setup evidence (prestate, captures, installed listings, identities) | 16777216 | `16*2^20`, judgment |
| A_selftest | sacrificial selftest generations, probe records, sacrificial export | 67108864 | `64*2^20`, judgment |
| A_pack | the generation export's payload pack (§4.2 M9, §15.3): one copy of the recipe and the snapshot | 16777216 | A_mat, judgment: the pack copies exactly the materialized recipe and snapshot, which A_mat covers |
| A_capture | one attempt's complete capture (§15.3): the recipe (A_mat), the native outputs (A_obj), `tmpdir/` (A_tmp), the attempt's records and raw bytes (A_rec, A_retry) and the fallback journal (A_fb) | 3922388356 | `16777216+2242440646+268435456+545393048+832564774+16777216` |

### 14.3 Stage budgets and the rule

| Stage | Required (exact) | approx | JACKAL parsed input |
|---|---|---|---|
| before setup | 2027732564230/1397 | 1451490740.3221188 | `2*(115303191+1048576+16777216)+134217728+1468268019712/1397` (A_install + A_homes + A_setuprec, their full restore, A_jrnl, A_ambient) |
| before selftests | 1843272351744/1397 | 1319450502.3221188 | `2*67108864+134217728+1468268019712/1397` (A_selftest, its restore, A_jrnl, A_ambient) |
| before every `adopt` and every `materialize` | 15415338242864/1397 | 11034601462.322119 | `15368462701360/1397+2*16777216`, v6's reviewed expression `2*(16777216+2242440646+545393048)+1468268019712/1397+2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` plus the payload pack and its full restore |
| before every dispatch | 26374491309528/1397 | 18879378174.32212 | `15415338242864/1397+2*(16777216+2242440646+268435456+545393048+832564774+16777216)`: the line above plus A_capture and its full restore; the check `26374491309528/1397-15415338242864/1397-2*3922388356` gives 0 |

The dispatch-stage W-1 addition over v7 is 7844776712 (JACKAL exact, parsed `2*3922388356`).

**Rule.** A stage proceeds only if free − reserve − Required(stage) ≥ 0, computed with actual MCP JACKAL from a
fresh `storage_status.py` reading taken by F as `sicarii`, with the configured reserve unchanged. Otherwise the stage is
DEFERRED. The setup and selftest stages are procedural (the lead computes and records the receipt before asking the
operator, and before running any selftest). The dispatch stage is procedural (runbook) **and** frame-enforced: at D10,
W issues the challenge `<free>-<reserve>-(<the reviewed dispatch-stage expression>)` built from F's fresh reading; F
forwards the lead's actual-MCP receipt; W requires `status` exact, `formal` false, `parsed` equal to the challenge,
`exact` ≥ 0, and free and reserve equal to the reading. Raising an allowance is allowed only upward, and changes the
frame's compiled expression, which is a reviewed frame change.

**What these numbers are not.** Satisfying the inequality is not a safe-capacity argument. Periodic sampling plus a
factor is not a bound. Images and ENOSPC never count as capacity or as an accepted refusal.

### 14.4 Historical arithmetic (not capacity and not current)

Against the retained 23:32:06Z reading (free 10460753920; reserve 10000000000; the re-review reproduced
free − reserve = 460753920 with parsed `10460753920-10000000000`):

| Stage | Margin (exact) | approx | parsed |
|---|---|---|---|
| dispatch | −14724789475120/1397 | −10540293110.322119 | `10460753920-10000000000-15368462701360/1397` |
| setup | −1384059337990/1397 | −990736820.3221189 | `10460753920-10000000000-2027732564230/1397` |
| selftest | −1199599125504/1397 | −858696582.3221189 | `10460753920-10000000000-1843272351744/1397` |

All three are negative, so every stage would have been DEFERRED at that reading. No fresh reading was taken for v3.

### 14.5 Images (only if S-1 option 3 is chosen) [correction: W1-V6-IMAGE-PIN]

Carried unchanged in substance from v2 (re-review: W1-IMAGE-GEOMETRY and W1-IMAGE-COMPATIBILITY CLOSED): payload
allowances, not image sizes (work 2259217862 = A_mat + A_obj; records 545393048 = A_rec for v2's record set);
filesystem metadata, journal, inode tables, reserved blocks, geometry and setup effects to be measured on a sacrificial
image and never assumed; the zero difference is an ideal payload identity, not physical allocation equality or safe
capacity; `fallocate` creates under the umask, so each image needs an explicit `chmod 0600` and `chown root:root`,
verified; `noexec` is compatible with the proof/compile-only allowlist (gnatprove, gprbuild and the provers execute
from the toolchain path) and incompatible with any control that executes built artifacts in the tree, and such
original executable or native-loading controls keep a separate compatible admitted frame and mount and are never
narrowed to suit a mount; images enforce bounded writes only; ENOSPC is a retained failure, never an accepted refusal
and never capacity evidence; images earn no capacity or admission credit without a reviewed preserving argument.

v3 additions. v3's record classes raise the records payload allowance to A_rec + X = 2514471538 (parsed
`545393048+1969078490`). The v3 ideal payload identity (work payload + records payload + full restore + A_ambient +
A_tmp + A_jrnl − Required(dispatch)) is 0; JACKAL returned it with parsed
`16777216+2242440646+545393048+1969078490+16777216+2242440646+545393048+1969078490+1468268019712/1397+268435456+134217728-15368462701360/1397`
(the tool flattened the grouping parentheses of the submitted expression). It is still only an ideal payload identity.

v7 additions (kept, with v9's names). The view's `TMPDIR` (g/tmpdir) lies on the work image, so the work payload
allowance is A_mat + A_obj + A_tmp = 2527653318 (JACKAL exact, parsed `16777216+2242440646+268435456`); the payload pack
lies on the records image, which becomes A_rec + X + A_pack = 2531248754 (JACKAL exact, parsed
`545393048+1969078490+16777216`). The captures (A_capture each) lie on the records image too; images enforce bounded
writes only, so a capture that does not fit is a recorded failure (§9.5), never an accepted refusal and never capacity
evidence. Every identity here is only an ideal payload identity.

**Layout with images (v4) [correction: W1-IMAGE-TREE].** The layout, anchors, routing and names are exactly those of
§3.3 and §3.4, which are the same with and without images. The work image is mounted at T_root
(`/var/lib/wlscratch/runs`); the records image is mounted at R_root (`/var/lib/wlscratch/runs/records`), that is,
inside T, on a mount point that is a directory of the work image. P_adm, the partition contents and the target
temporaries are therefore on the work image, and P_att, P_exp and P_ado on the records image, so target output cannot
exhaust the space that frame records need. Each bare mount point is root-owned, mode 0700 and empty (T_root's on the
root filesystem, R_root's on the work image), so W can neither write into a missing mount nor mistake one (§3.4's
missing-mount checks run at every writer and every RL invocation). Each image root contains `lost+found` from
`mkfs.ext4`, admitted only under §3.4's pinned special-entry rule. The mount units `var-lib-wlscratch-runs.mount` and
`var-lib-wlscratch-runs-records.mount` carry `Options=loop,nosuid,nodev,noexec`; the records unit has `Requires=` and
`After=` on the work unit; both are enabled through `local-fs.target` as their only start source; there is no
automount unit and no fstab line. The views' binds of `g/source` and `g/tmpdir` are binds of the work image and
inherit its `noexec`, as the compatibility statement above requires.

**S-J, images (only if chosen; replaces steps 4.1 and 4.2 of S-B; every step logged as in §11.4; the atom classes and
the reachable set are §11.4's image rows).**
- J0: `need_absent /var/lib/wlscratch-images /var/lib/wlscratch/runs` and the two mount-unit paths.
- J1: `install -d -o root -g <W> -m 0750 /var/lib/wlscratch-images` (W and W2 can list and search it, so they compare
  its exact entry set and the image files' pinned identities at every use, §3.4, §11.7; nobody but root can write it or
  open the image files, which stay root:root 0600, J2).
- J2: create the two image files with `fallocate -l <reviewed size>`, then `chmod 0600` and `chown root:root`;
  verify type, size, owner and mode; then `mkfs.ext4 -L <reviewed label> -U <reviewed uuid>` on each image file (one
  atom per image file, class "image file and filesystem").
- J4: `install -d -o root -g root -m 0700 /var/lib/wlscratch/runs` (T_root's bare mount point).
- J5: install `var-lib-wlscratch-runs.mount` (reviewed bytes) by the staged-rename rule, `systemctl daemon-reload`,
  `systemctl enable --now` it; verify the mountinfo entry (§3.4).
- J6: on the mounted work image root: `chown <W>:<W>`, `chmod 0700`; then `install -d -o root -g root -m 0700
  /var/lib/wlscratch/runs/records` (R_root's bare mount point, on the work image).
- J7: install `var-lib-wlscratch-runs-records.mount` (reviewed bytes) by the staged-rename rule, reload, `systemctl
  enable --now` it; verify the mountinfo entry and its parent mount ID (§3.4).
- J8: on the mounted records image root: `chown <W>:<W>`, `chmod 0700`. S-B's step B 5 then sets and checks the ACLs.
A stop in S-J is reconciled by S-R like any other script, against §11.4's reachable set with images.

### 14.6 Memory, CPU and caps

Unchanged from v5: `MemoryMax=8G`, `MemorySwapMax=0`, core 0/0, `-j2`, the 16777217 kB gate and the receipt
protocol. U holds only C and the target, as v5's scope held only its child and the target (§9.3 G6), so no frame
process shares the target's memory limit beyond v5's child. The scope lies in `user-1000.slice` with the properties of
§8.3, and `app.slice`'s shared limits do not apply (§12.3 V10'). A skeleton, when used, is a small read-only `tmpfs`, and
the views' namespaces and filters are kernel objects; RL, L, C and O use RAM and processes; this is not disk and is not
budgeted as disk.

### 14.7 The complete storage accounting [correction: W1-V7-EVIDENCE-RESTORE]

- **Originals in T:** P_adm under A_mat and A_in; the partition contents under A_obj; `tmpdir/` under A_tmp; P_att and
  P_ado under A_rec, A_idf, A_in, A_retry and A_fb.
- **Exports:** every retained record at most once under A_exp; the payload packs under A_pack and A_in; each
  attempt's complete capture under A_capture.
- **Full restore:** every exported class, the capture included, is doubled in the dispatch-stage expression, so a full
  restore of what the attempt adds has temporary space above the reserve at the moment the stage proceeds.
- **Simultaneous peak:** originals, exports, payload packs, raw bytes, temporaries and the capture of the new attempt,
  plus the restore space for its additions, are all in one stage expression evaluated against one fresh reading
  before launch; bytes already retained by earlier attempts are already absent from that reading. This is the
  arithmetic of a judgment-based allowance (exact identities, JACKAL exact, not formal-bounded); it is not a bound on
  future writes, and safe fresh capacity stays OPEN (the original obligation; no design text can establish it).
- A capture that fails (for example `ENOSPC`) is recorded as failed, the attempt cannot succeed (§10.7), and nothing
  else changes; it is not presented as an accepted refusal (§21 D6).

## 15. Rollback, freeze/export and evidence [corrections: W1-SETUP-PROBES-ROLLBACK, W1-COMMIT-JOURNAL-EXPORT; gap: rollback-and-evidence]

### 15.1 Rollback order (operator; every step's before and after state captured raw) [correction: W1-V8-COMPOSED-ENUM]

The rollback is its own state machine, not the inverse of setup: it starts from a complete setup that has run (the
observation equals G_N plus runtime growth: generations, records, exports, captures), and it retains every tree.
Before step 1 the operator captures the **retained-tree manifest** M0 of `/var/lib/wlscratch` (and of
`/var/lib/wlscratch-images` with images): every entry's path, type, size, sha256 (regular files), owner, group, mode
and ACL digest. Steps:

| Step | Action | States the step can leave (its intermediates) | Postcondition (checked by the step's after capture) |
|---|---|---|---|
| R1 | revoke new launches: `staged_deactivate /etc/sudoers.d/wlscratch-frame`; preserve its bytes and sha256 in `/root/wlscratch-staging/rollback-<stamp>/`; `visudo -c`; remove the inert file after equality | installed; deactivated; deactivated and preserved; removed | the final and inert names `absent`; the preserved copy equal; `visudo -c` passes; no new writer can start |
| R2 | wait for and reconcile every pending and running participant: no process with uid W (including writers started before R1); no `sudo` process naming a frame entry; K and M (§9.4): every RL scope absent or `populated 0` and not live; RL's root scan conditions (no uid-N process, no N-owned user namespace outside RL scopes) observed by root | no state change (a check); it holds the rollback while a participant lives | all of these hold; a live participant is waited for; killing one is a separate, recorded, explicit operator decision; any UNKNOWN holds the rollback here |
| R3 | the shared window: if it is reserved by a W-1 attempt and known-terminal ownership is uncertain, it is a hold; if ownership is known terminal and the reserving front is gone, the operator resolves it explicitly and records the resolution; the frame never does | no frame state | the window's state recorded |
| R4 | `staged_deactivate /etc/sudoers.d/wlscratch-rl`; preserve; `visudo -c`; remove after equality | as R1 | as R1 for the RL rule |
| R5 | images, if used: identify every start source first (the two mount units, `systemctl list-dependencies --reverse` of each, any automount unit, fstab: none expected); `systemctl disable` both units; verify that no process has a file open on them and that R2 still holds; stop the records unit first and the work unit second (unmount); verify that each is unmounted and that each bare mount point equals its setup identity (§11.7); preserve the unit files (bytes and sha256), deactivate and remove them, `systemctl daemon-reload`, verify no remount; keep the image files and record their sha256 | per unit: enabled and active; not enabled, active; not enabled, inactive; unit file deactivated; removed; reload pending; reloaded | as stated in the action |
| R6 | nothing is restored in `/home/sicarii`: W-1 sets no ACL there | — | — |
| R7 | lock and expire W (`usermod -L -e 1 wlscratch`; N is already locked and expired); keep both accounts, so evidence ownership keeps its meaning | W unlocked; locked, not expired; locked and expired | W locked and expired; N unchanged |
| R8 | `staged_deactivate /etc/ssh/sshd_config.d/30-wlscratch.conf`; preserve; `sshd -t`; `systemctl reload sshd`; remove after equality | installed; deactivated; preserved; removed; reload pending; reloaded | the drop-in `absent`; `sshd -T` without the `DenyUsers` line of S-E |
| R9 | keep as evidence: `/var/lib/wlscratch` (generations, records, exports, captures), `/opt/wlscratch`, `/root/wlscratch-staging` (including the step logs and every rollback capture) and every capture; capture the retained-tree manifest M1 | — | **M1 equals M0** (the retained trees were not changed by the rollback); any difference stops for an explicit operator decision |

The reachable rollback states are exactly the products of these per-step states in step order (each step starts only
after the previous step's postcondition holds). A stopped rollback continues from the first step whose postcondition
does not hold; S-R classifies it by the same rules as setup (§11.4), against this table. Nothing is called restored
without its equality capture, and runtime growth is never "reversed": the trees are retained and compared, not undone.

### 15.2 What rollback leaves

Remaining: the two locked and expired accounts (W and N) and their two user-private groups, with their numbers; their
`passwd`, `group`, `shadow` and `gshadow` entries; every file under `/var/lib/wlscratch*`, `/opt/wlscratch` and
`/root/wlscratch-staging`; images, if any; journal entries. Removed: both sudoers files, the sshd drop-in, the mount
units. Not restored: a pristine pre-setup system.

### 15.3 Freeze, export and the complete capture [corrections: W1-V8-EVIDENCE-EQUIV, W1-V7-EVIDENCE-RESTORE, W1-V6-EVIDENCE-RESTORE; v4: W1-COMMIT-JOURNAL-EXPORT]

**Export primitive** (every copy in P_exp or in an adoption export):
1. create the copy as an unnamed inode (`O_TMPFILE`, mode 0600) in its export directory, write its bytes, `fsync`;
2. set the export access ACL with `fsetxattr` on the held descriptor;
3. read back on the same descriptor: `fgetxattr` equals the encoded ACL; `fstat` shows a regular file, no link yet,
   owner W, group W, the source's size and `st_mode` 0640 (the mask in the group bits); the bytes, re-read, have the
   source's committed or pinned sha256;
4. link it create-only under its export name (§10.1 step 3); `fsync` the directory; entry join; `verify_location`;
5. only then commit the export marker (kind `export`) in the journal, with `record` = `{path, sha256, bytes, mode:
   0640, acl_sha256}`: the final values.
An export copy therefore never has a name with any mode or ACL but its final ones.

Export directories are created 0700, given their ACL and read back (`st_mode` 0750) before any entry is created in
them; their identities and ACL digests are listed in the increment's manifest. Every consumer of an export copy (F,
reviewers, the vault) compares with these final values, never with 0600.

**Payload packs.** The generation export (`export/generation/`) holds, besides the generation journal's records, a
payload pack: one export copy of every recipe file and every snapshot file, read back by W from P_adm with `O_NOATIME`
and listed in the manifest with its relative path, sha256 and size (§4.2 M9). Each `adopt` increment holds an adoption
payload pack: one export copy of every verify-only input F streamed (the two review rosters and freeze records, the
provenance triples, the observation), with the lead-tree path F read it from. These are exactly the payloads that
channel segments reference by `written` or `source` (§7.3); everything else a segment references is a record that some
increment exports. So the exports of a generation, of each of its attempts and of the adoption they bind are
self-contained: an offline reader holding only them, from the vault or locally, recomputes every chain head, every
marker digest and every payload digest.

**Increments and the finite prefix.**
- An export increment n of a journal J (an attempt journal or an adoption journal) is defined by its cut c_n: the head
  (seq, sha256) of J's chain (§10.2) when the increment starts, which §10.2's commit primitive makes a record-free
  marker, so that every record-bearing chain marker at or below it is confirmed (c_−1 lies before seq 0); and, for an
  attempt journal, the writer's next fallback slot index s_n at that moment (s_−1 = 0). Increment n exports exactly:
  every chain marker of J with c_(n−1).seq < seq ≤ c_n.seq, as a marker file; for each such marker of kind `primary`
  or `retry`, the record it commits (a marker of kind `export` points at a copy that is already in P_exp, so only the
  marker file is exported); the fallback slots with index from s_(n−1) up to s_n − 1, the VALID ones as decoded
  entries of `fallback-slots.json` and, for every slot, its raw 65536 bytes as an export copy with state `slot-raw`; and
  every RAW file of J's `commits/` (§10.2) and every uncommitted record file present in the partition at the cut,
  whatever its seq, that no earlier increment copied, **as an export copy of its bytes** with state `raw` or
  `uncommitted`, with its path, size and sha256. Raw bytes get no parsed or success credit. A writer that cannot append
  to J (a branched journal, or rule J4 of §10.2) makes no increment, and `EXPORTED` reports state `failed`. A committed
  record is exported with its sync provenance and with the attestation records it rests on (§10.5).
- After the copies, the increment's `manifest.json` (`wlscratch-export-v4`: per entry the export path, source path,
  sha256, bytes, final mode, `acl_sha256`, source marker digest, `sync_provenance` and state ∈ {`committed`,
  `fallback`, `slot-raw`, `raw`, `uncommitted`, `payload`}, and the export directories' identities) and `freeze.json`
  (`wlscratch-freeze-v3`: increment number, cut c_n, slot range, the previous increment's freeze-marker digest, the
  digest of every export marker committed for this increment, the manifest's sha256, `raw_files`, channel heads, boot
  id, time) are written with the export primitive and committed. `raw_files` lists every RAW file of J's `commits/` and
  every uncommitted record file that appeared after the cut and that neither an earlier increment nor this manifest
  copied, so every raw file is copied exactly once, by this or the next increment. The export markers of increment n,
  its freeze marker and the close markers that confirm them have seq > c_n.seq, so the next increment exports them. The
  last increment's export markers are listed by digest in its own freeze record; only its freeze marker and the close
  marker that confirms it are never exported: the freeze marker's digest goes to F in `EXPORTED` and `FINAL` and is
  printed, and the originals stay in the protected journal.
- **Who makes increments.** For an attempt: W at M11 or D19 (increment 0, after `final-status.json`), then each W2 at
  the end of its work (the next increment), which therefore exports the later evidence: W's late records if any, W2's
  recovery and release records, the front terminal record and their markers. For a generation: one export,
  `export/generation/`, of the generation journal with the materialization marker as its cut, and its payload pack;
  that journal never grows again, so this export is complete and final; its export markers live in A0's attempt journal
  and are exported by A0's increment 0. For an adoption: each `adopt` invocation makes the next increment of the
  adoption journal, with its payload pack, in `adoption-<I>/export/inc-<n>/`.
- **Accounting.** Cuts are disjoint, so every record and marker is exported at most once across all increments, and
  A_exp's "each retained record at most once" (§14.2) is unchanged; the payload packs are counted under A_pack and A_in,
  the captures under A_capture (§14.2, §14.7).

**The complete capture** (corrections W1-V7-EVIDENCE-RESTORE, W1-V8-EVIDENCE-EQUIV). After the kernel census shows
attempt A's scope U absent or `populated 0` (term (1) of H(U), §9.8 N4) and before A's terminal record, the serving
writer (W at D17, or W2, §9.7) writes `export/capture-<A>/` by the export primitive: an export copy of every entry of g
(the recipe, every partition entry, `tmpdir/` and its contents), read as on-disk owner with `O_NOATIME`, and of every
file of P_att(g, A) and of every `w2-<k>/` directory; regular files by bytes, directories as directories, symlinks by
their target string (read by `readlinkat`, on W-owned symlinks inside T), special files by type and device number only.
Its `capture-manifest.json` (`wlscratch-capture-v1`) records, for every original entry, the relative path, type,
`stat_key` (dev, ino, mode, nlink, uid, gid, size, mtime_ns, ctime_ns), atime_ns, the access and default ACLs, the
extended attributes, the link structure (inode groups) and the sha256 of the bytes; and for every copy its export path,
sha256 and final mode. **Self-check:** W walks g and P_att(g, A) before the copies and again after them, and records each
file's `stat_key` immediately before and after its copy; every pair must be equal and the two walks must give the same
entry set and keys. A difference makes the capture `failed`; W retries it once, then reports it (§9.5). The capture
starts only after (1); under P-ASYNC (a closed specification discharged by source enumeration, §9.8 N4, §13.2 S-2) no
write of a task of U can take effect after its cgroup exit. **The self-check (the before/after `stat_key` pairs and the
two walks) is evidence for its own window only: an equal pair shows no change between the readings, not the absence of
a later write.** A caught difference makes the capture `failed`; a change outside the self-check's window is bounded
only by P-ASYNC, which the operator-reserved exercise (§16.1 O-ASYNC) and I-5 refute under the state predicate of
§13.1, never establish. No 'never a silent change' claim is made (W1-V9-ASYNC-ENUM). A complete capture is
committed by an export marker whose record is the manifest's descriptor. Captures are additive per attempt and never
modified.

**What the vault pins.** The whole `export/` tree (§8.5), so the complete captures, the raw bytes, the slots, the channel
segments and their continuations, the payload packs and the provenance attestations are all inside the pinned tree.

- F re-reads every copy of each increment and capture through its ACL, compares it with the manifest's final values,
  and keeps each freeze-marker digest from `EXPORTED` and `FINAL`.
- **What "frozen" means:** create-only, W-exclusive, no verb that modifies or deletes, digests in a hash-linked
  journal. **Limits:** root, or W running changed code, could still alter them; no immutable attribute is set (that
  needs `CAP_LINUX_IMMUTABLE`).
- Lead copies of exports are mutable evidence records, not authentic producer custody. A project-vault transfer of
  exports (§8.5) is backup, not authenticity.

### 15.4 Evidence classes (all retained raw)

Pre- and post-setup captures with digests, the step logs and every S-R capture; `passwd`, `group`, `shadow` (first
character only, and N's expiry field) and `gshadow` lines; `getfacl`/`stat` outputs; sudoers and sshd bytes; `findmnt`,
mountinfo, kernel settings and features; installed-inventory comparisons; role identities and module closures; RL
identities with their view specifications, namespace identities, maps, binds, Landlock rulesets and seccomp programs;
selftest and probe records with raw errnos, and every run of §13.2 with its pins; every committed record and marker,
every retry, every fallback allocation descriptor and slot (VALID decoded, every slot raw), every raw uncommitted
record, channel segment, wait, participant, scope and census record; launch and observer intents, `spawn-ok`, the
conclusion, stream finality, final status and the release records (`release-intent`, `window-release`,
`release-withheld`, `release-not-owner`, `release-failure`) from W and from each W2; recovery records; front terminal
records; export increments with their manifests, freeze records and payload packs; complete captures with their
manifests; the adoption record and its exports; F's console output as preserved in the lead transcript (neither durable
nor frame custody); rollback captures and the retained-tree manifests M0 and M1. **Limits:** hashes of W-owned files
describe files that root or W could change; copies are evidence records; none of this is producer authenticity, proof or
acceptance.

## 16. Setup, verification and adoption order [corrections: W1-V9-PREMISE-ORDER, W1-V9-REVIEW-PROVENANCE]

1. Independent review of this v11 design (by an independent Claude review subagent, the review track since
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
admission join (HANDOFF.md:173, /home/sicarii/Documents/complete-phase1-prompt.txt:60), made under the operator's
~17:05Z direction. It is NOT reviewed. Adoption therefore stays blocked until that change is itself reviewed in the
frame-design revision that follows this W-1 review** (§23). v11 does not reach adoption.

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

## 17. Placement of every v5 mechanism

| v5 mechanism (frozen `scratch.py`) | W-1 placement | Change, and why it preserves the original |
|---|---|---|
| `Dir` anchoring, `verify_location`, `child(create=True)` authentication, `write_bytes`/`write_json`/`open_stream`/`set_mode` (S:144-358) | W and W2 for every frame mutation; C and O for anchored reads through the view; F for anchored input and window reads | none in semantics; the location chain is now protected (§3.4, §4.5); records are linked only after validation (§10.1) |
| `stat_key`, `observe_tree` (v6 final pass), `read_observed`, `read_prefix`, `read_files` | C and O full walks through the view, with `O_NOATIME`; W writer-owned walks (partition contents skipped) and the complete capture after H; F base-tree and transcript reads, with `O_NOATIME` | `observe_tree` also returns excluded-leaf keys (§4.5); the walk rules are v5's |
| `retain`, `guarded`, `read_record`, `last_resort`, `retain_observation` (S:375-436, 1109-1128) | W and W2 | commit markers, journals with committed chains, the fallback journal with an immutable allocation descriptor and append-only slots, consumer precedence, sync provenance, durability-UNKNOWN (§10); the compact equal-record form unchanged |
| `exec_verified`, frame inventory, `frame_admitted` (S:587-863) | installed members checked by W, RL, L, C, O; review, installed-review, rollout and transcript joins by F; the adoption record's structural joins by W | `install_root` replaces `frame`; the adoption record is W's protected record (§4.6); F's joins at v5 trust (R2) |
| `adopt`, `validate_adoption_observation`, `rollout_join`, `review_profile_problems` (S:687-837) | F (lead-context checks), W (structural re-verification, create-only commit) | destination moved from the frame's review directory into the protected tree; every v5 join kept except that `rollout_join` becomes the §23.4 review-provenance join selected by `reviewer_kind` (§23); installed-review joins added (§4.6); the review-provenance join change is stated in §23, not an open conflict |
| `materialize` run directory (S:977-999) | label check by F (read-only, §3.3), generation creation by W in T, run-path presentation by RL in the view only (§12.2 step 11) | no host write; v5's label refusal kept; C6' is the one difference (§21) |
| `materialize` recipe (S:959-1049), `expected_source`, `overlay_rules` | W `materialize` | streamed verified bytes; no partition root is created, as in v5 (S:1033); `tmpdir/` is created for the view (§4.2 M7) |
| `command()` allowlist (S:1054-1070) | W, re-derived by C | unchanged |
| `specifications()` (S:1073-1106) | W builds, C verifies | v5's own source relocation only (§8.4) |
| `identities()` (S:1131-1153) | O (`parent`, `after`) and C (`child`) inside the view, against the original baselines; the manager environment and F's runtime in the real context | the original baselines (§8.4, P-VIEW) |
| `sample()` (S:1156-1179) | F half (sibling units in `sicarii`'s manager, with no unit allowed, and `storage_status.py`); W's manager census M; helper half (heavy processes, meminfo) | split by authority; same checks, applied also to the manager that now holds the frame's scopes (§9.4) |
| `threshold_receipts`, `receipt_line`, `memory_gate` (S:1186-1248) | W issues and verifies; F forwards from the inbox | unchanged constants and deadlines; "through original stdin" = W's stdin channel |
| `window_locked`, `window_read`, `window_write`, `reserve`, `owns_window`, `release` (S:1253-1341) | F | unchanged protocol; attempt records committed by the serving writer under F's lock in the same order; the release record's durability does not gate the window write (§9.4, supplied ruling) |
| `ancestors`, `processes_naming`, `owned_terminal` (S:1346-1415) | O at the after stage, W2's recovery rounds, F at the release point | v5's predicate, unchanged in meaning, over a system-manager scope, evaluated in a race-aware order (§9.4); no inference from missing records |
| `final_stream_sync` (S:1420-1437) | W after terminal | unchanged, followed by stream finality with its self-check (§10.6) |
| `admission()` (S:1440-1448) | split per stage among F, W, O and C | the same checks (Appendix D) |
| `spawn`, `wait_blocked`, `pending_handled`, `raising_handler` (S:1469-1517) | every waiting role; C spawns T exactly as v5 (`fchdir`, core 0) with the attributes of §8.3 | H-S1/H-M3 synchronous handling; `STOP` down the channels |
| v5's scope launch `systemd-run --user --scope` (S:1564-1594) | RL's `systemd-run --scope` in the system manager under `user-1000.slice`, before the view; L `exec`s C in place | the same limits; another manager (§12.3 V10'); U holds C and the target only, as v5's scope did |
| `started_by_dispatch` (S:1520-1527) | W: `SUDO_*` plus `HELLO_ACK` plus stdio inode join; W2: front-process triple | the invoker is bound by kernel identities instead of a parent command line |
| `refusal_record`, `run`, `conclude` (S:1530-1765) | W (`dispatch`), F (release), O (terminal observations), W2 (recovery) | N13 recomputation; `final-status.json` |
| `child` (S:1768-1896) | C | §9.3 C1-C12, over a direct channel to W |
| `dispatch` (S:1899-1988) | F | inbox answers over the channel; S1 wait via W2; N14 exit |
| v5's vault pin of the run directory (S:1562-1563) | F pins the export tree with its complete captures (§8.5) | the equivalence predicates B1-B5 (§8.5), OPEN until V-VAULT passes |
| `verify_materialization` placement: materialize, parent and child admission, immediately before spawn, conclusion | W at M8; O at the parent stage and W's writer half; C at the child stage and as the final pass; O and W at the conclusion | same placements, now split by authority |
| launch seal in argv (S:1570-1594, 1783-1817) | RL's, L's and C's argv carry the `launch.json` and `admission.json` sha256; C verifies the bytes delivered over its channel | V4-B03 kept |

## 18. Per-correction and per-gap status (the author's assessment, for the independent reviewer to judge)

"CLOSED-AT-SPEC-LEVEL" is this author's claim that the specification text now covers what the item asks for. It is
not closure, not executed evidence and not acceptance; the reviews state that they do not adopt such claims by
repetition. "OPEN" marks an item that v9 does not claim to meet. "CLOSED (review), carried" marks items that the sealed
v8 review closed; v9 keeps them as §0.5 states. Every original obligation, V5-B01, V5-B02, W1-V5-PRESERVATION,
W1-V6-READ-MUTATION, W1-V7-HOLDER-STATE and Gate 0 stay OPEN regardless (§0.4, §22).

### 18.1 The v8 review's required W-1 changes (verbatim) and the author's assessment

Source: `v8-review/claude-v1/review.json` `required_changes[].change` (sha256 above); seven entries (JACKAL exact,
parsed `1+1+1+1+1+1+1`, Appendix I). The assessment is the author's claim, not closure.

1. **W1-V8-HOLDER-IOEXIT**
   > Close the P-IOEXIT asynchronous path (direct-I/O/AIO write completing after cgroup populated 0 via an outside /proc/<pid>/cmdline reader holding the mm) by establishing H(U)'s absorbing property for all asynchronous paths (not refutation-only), or redesign the holder boundary; resolve the dependent consistency of the §15.3 complete capture and §10.6 stream finality.

   Author: CLOSED-AT-SPEC-LEVEL as a redesign; the premises it rests on are NAMED_UNESTABLISHED. The holder boundary is
   redesigned so the asynchronous paths cannot exist in a view: the seccomp filter of §12.2 step 13b makes `io_setup` and
   `io_uring_setup` return `ENOSYS` (v8's AIO path, and a second path v8 missed, untracked `io_uring` requests at exit,
   correction 0.2 item 1). The absorbing property is argued over the closed list of write paths (§9.8 N4) under
   P-SECCOMP, P-ASYNC and P-RELEASE, which a source reading of the installed build can discharge (§13.2 S-2), not
   refutation-only. The capture (§15.3) and stream finality (§10.6) rest on the same premises and add self-checks.
   W1-V7-HOLDER-STATE stays OPEN until those premises are discharged and reviewed. The cost is a new change, V14 (§12.3).
2. **W1-V8-PRESERVATION-ESTABLISH**
   > Establish the §21.1 preservation relation over the complete original domain for each OPEN V/C/D row with source-to-binary correspondence, or redesign to remove the change; keep V5-B01, V5-B02, W1-V5-PRESERVATION and W1-V6-READ-MUTATION OPEN until done.

   Author: OPEN. v9 cannot establish the relation without the runs; it gives every OPEN row its exact discharge route
   (§21.3-§21.5, §13.2 S-5, S-6, U-11, U-12, I-7, I-8), and names the rows that cannot close by any route (C1's reader
   workflow, C6', V10's shared budget). V5-B01, V5-B02, W1-V5-PRESERVATION and W1-V6-READ-MUTATION stay OPEN.
3. **W1-V8-PREMISE-DISCHARGE**
   > Before any installed use, supply the S/P discharges of N7 matched to the installed 7.2.6-1-aarch64-ARCH build (P-KSRC first), in particular P-NOSUID and P-NOCAP on which the identity-map design's host-DAC safety rests.

   Author: OPEN (it requires execution). v9 supplies the executable plan: P-KSRC first (S-1), every kernel premise's
   source reading on the installed build's source (S-2), the probes in order (U-1 to U-14, I-1 to I-8), and the
   privileged fixtures in the operator package (§16.1); P-NOSUID, P-NOCAP, P-NOOWNER, P-SECCOMP and P-ASYNC are marked
   critical, stopping every installed use if refuted. No premise is discharged in v9.
4. **W1-V8-WRITER-AS-W**
   > Surface in N2 the A1-via-sudo euid-W vector (A1 may run writer.py as W, which holds the owner rule and CAP_SYS_PTRACE over every U8) as an explicit premise/obligation, not only a §16 code-review item and general trusted-base clause.

   Author: CLOSED-AT-SPEC-LEVEL. The vector is stated in §2.1 and in N2's principal table, and removed by redesign:
   U8's owner is N, an identity no route confers (§5.3); A1's `writer.py` as W holds no capability over U8. The
   remaining reliance (no process but RL's helper has euid N) is premise P-NOOWNER with its discharge steps.
5. **W1-V8-COMPOSED-ENUM**
   > Produce the actual global state-vector table and reachable-state enumeration required by W1-V7-COMPOSED-STATE; the current spec gives a model only, deferring the table to a concrete inventory that does not exist.

   Author: CLOSED-AT-SPEC-LEVEL: §11.4 gives the global atom table and the reachable set with its size, exact except for
   the two list lengths n_d and n_m, which the frozen frame fixes (63 + 3·n_d + 5·n_m states without images, 100 + 3·n_d +
   5·n_m with); §15.1 gives the rollback machine with its states and postconditions; O-4 and O-5 rehearse both.
6. **W1-V8-EVIDENCE-EQUIV**
   > Establish capture equivalence for every original backup consumer (V-BACKUP via V-VAULT) and safe fresh capacity, and resolve the capture's dependence on H(U)/P-IOEXIT.

   Author: OPEN for the establishment (it requires U-14 and I-6); the consumers B1-B5 and their predicates are named
   (§8.5), the capture copies raw bytes and records complete metadata (§15.3), and its dependence on H(U) is reduced to
   P-ASYNC with a self-check. Safe fresh capacity stays the original OPEN obligation; no design text can establish it.
7. **W1-V8-FORM-SUBUNIT**
   > Independently hash-pin every carried paragraph sub-range (§9.4 release-rule paragraphs; §11.4 staging/status rules), or inline the composed text, so the specification is self-verifying.

   Author: CLOSED-AT-SPEC-LEVEL: v9 is self-contained (§0.1); every unit holds its full text, and §18.5 identifies the
   units byte-identical to v7 or v8 by sha256.

### 18.2 Prior corrections, as the v8 review ruled on them

`prior_closure` of the v8 review (verbatim statuses): CLOSED_AT_SPEC_LEVEL: W1-V7-ARCHITECTURE, W1-V7-VIEW-ROOT,
W1-V7-C3-DATA, W1-V7-PROBES, W1-V7-SYNC-PROVENANCE, W1-V7-PREMISES — carried (§0.5), extended only as §0.3 states.
PARTIALLY_CLOSED: W1-V7-HOLDER-STATE (§18.1 item 1), W1-V7-FULL-DOMAIN (item 2), W1-V7-READ-EFFECTS (routes OPEN, §9.8
N6), W1-V7-COMPOSED-STATE (item 5), W1-V7-EVIDENCE-RESTORE (item 6). NOT_CLOSED: W1-V5-PRESERVATION, W1-V6-PRESERVE —
OPEN (§21). PARTIALLY_CLOSED: W1-COMMIT-JOURNAL-EXPORT, W1-CUSTODY, W1-CUSTODY-CLOSURE, W1-TERMINAL-CUSTODY,
W1-V5-REVOCATION-CONFINEMENT, W1-LIFETIME-ROLLBACK, W1-SETUP, W1-SETUP-RECONCILIATION, W1-SETUP-PROBES-ROLLBACK,
W1-PROTOCOL-FAILURE-STATES, W1-GENERATION-PROTOCOL, W1-IMAGE-TREE, W1-V5-JOURNAL-FAILED-CLOSE,
W1-V5-RECONCILIATION-STATES — each OPEN in the author's assessment, with v9's changes as follows: the custody and
confinement items through §9.8 N2 and N4 (owner N, the filter); the setup, reconciliation and rollback items through
§11.4, §11.5, §15.1 and §16.1; the commit, export and journal items through §10.5 and §15.3 (raw bytes copied); the
lifetime, protocol-failure and terminal items through §9.4 and §9.5. CLOSED_AT_SPEC_LEVEL_CARRIED: W1-DURABILITY-RELEASE,
W1-IMAGE-OBSERVATION, W1-JOURNAL-CONTINUATION, W1-RESOURCES, W1-SETUP-IDENTITY, W1-V5-IMAGE-PINS,
W1-V5-PROTOCOL-REFUSALS, W1-V6-C1-DATA, W1-V6-IMAGE-PIN, W1-V6-INVARIANTS — carried.

### 18.3 The section-3 gaps

`w1_gap_closure` of the v8 review (verbatim statuses): CLOSED_AT_SPEC_LEVEL_CARRIED: denial-probes, exposure-options,
fresh-identities-and-vault, lease-and-writer-authority, per-entry-modes-acls, resources-and-images — carried.
PARTIALLY_CLOSED: channel-and-dumpability, commits-and-durable-channel, generation-order, participants-and-recovery,
prestate-and-installation, rollback-and-evidence — OPEN in the author's assessment.

### 18.4 The original W-1 subgaps

`w1_subgap_closure` of the v8 review (verbatim statuses): CLOSED_AT_SPEC_LEVEL: W1-FINAL-PASS, W1-NONCLAIMS;
CLOSED_AT_SPEC_LEVEL_CARRIED: W1-IMAGE-COMPATIBILITY, W1-IMAGE-GEOMETRY, W1-PREFLIGHT-IDENTITY, W1-READ-ACCESS,
W1-READ-EXPOSURE, W1-SETUP-ORDER, W1-SETUP-PRESTATE, W1-VERIFICATION-PROBES, W1-WRITE-AUTHORITY — carried.
PARTIALLY_CLOSED: W1-CHANNEL, W1-CLOSURE, W1-CUSTODY, W1-EVIDENCE, W1-FAILURE-LEASE, W1-FAILURE-RECORDS,
W1-REBOOT-RECOVERY, W1-ROLLBACK, W1-SETUP-EXACTNESS — OPEN.

`open_obligations` of the v8 review: all 219 entries of `OBLIGATIONS-v2.json` (sha256
`1587e068fc2c31a562e38b459728a75dbf7e8d7d9f8afb8efa1474e2a702aeec`), V5-B01, V5-B02, W1-V5-PRESERVATION,
W1-V6-READ-MUTATION, W1-V7-HOLDER-STATE and Gate 0 stay OPEN with their original owners, releases and dependencies.

### 18.5 Change map (every v11 unit's identity)

The complete v11 change map — every one of v9's 134 units with its v9 identity and its v11 status (CARRIED, AMENDED,
COMPOSED, NEW), and every COMPOSED/AMENDED/NEW unit's computed v11 line range, byte count and sha256 — is **Part
V11-MAP at the end of this document**. It is placed last so that a single read-only script over the assembled file
computes every unit's line range before the map's own bytes are written, avoiding the self-reference cascade a
mid-document map would create (v9's §18.5 noted the same limit for its own identity). §V11-C.2 there gives the unit
partition (JACKAL exact).

### 18.6 New design elements that need the reviewer's attention, and the remaining premises

The new elements of v9: the namespace owner N and its closure (§3.1, §5.3, §9.8 N2, P-NOOWNER); the asynchronous-
submission filter and the closed list of write paths (§12.2 step 13b, §9.8 N4, V14, P-SECCOMP, P-ASYNC, P-RELEASE); the
staged-rename setup with the explicit reachable set (§11.4, §11.5) and the rollback table (§15.1); the capture's copying
of raw bytes and its self-check (§15.3); the backup consumers' equivalence predicates (§8.5); the probe-and-evidence
plan (§13.2) and the operator package (§16.1); the adoption-join conflict with the new review track (§16, open item for
the lead). The complete premise register is §9.8 N7; this unit holds no second list.

## 19. Future execution and installed evidence (none of it exists)

- §13.2's phases in order: S-1 to S-6 and U-1 to U-14 by the lead before setup; the operator package O-1 to O-5 (§16.1);
  I-1 to I-8 after setup through the reviewed selftest verbs. Each run's raw outputs, pins and dates are retained.
- The frame v6-W1 code, its freeze, its code review (§16 step 2) and the concrete setup inventory (§16 step 3).
- The installed-evidence review (§16 step 8), which reviews the S-discharges of §9.8 N7 matched to the installed build
  (P-KSRC first), the probe records and the complete-capture and vault evidence (V-VAULT, V-BACKUP).
- Nothing listed here is claimed by v9. "First engineering run" qualifies nothing (§9.8 N7 P-VIEW).

## 20. Non-claims [corrections: W1-V9-REVIEW-PROVENANCE, W1-V9-ASYNC-ENUM, W1-V10-FORM, W1-V10-COUNT]

- No sufficiency is claimed for any requirement. V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION,
  W1-V7-HOLDER-STATE, Gate 0 and every original Phase One obligation (the 219 entries of `OBLIGATIONS-v2.json`
  included) stay OPEN with their owners, releases and dependencies.
- The same-identity view is not established as preserving the original success domain (§21, §22.4). No change it
  makes is presented as an accepted exception, a narrowed case or a criterion entitlement.
- Every premise of §9.8 N7 is NAMED_UNESTABLISHED. Source readings are not installed-version discharges by themselves;
  probes refute and never establish; trusted-base exclusions are assumptions. The probe-and-evidence plan (§13.2) is a
  plan; nothing in it was run for v11. The asynchronous-holder containment (P-ASYNC, P-RELEASE) is an OPEN obligation,
  stated as a closed specification with its enumeration basis and its observed-state predicate (§9.8 N4, §13.1); its
  refutation exercise is operator-reserved (§16.1 O-ASYNC, procedure OPEN) and **is not asserted here**. The
  stream-finality and capture self-checks are evidence for their observation window only; no "never a silent change"
  claim is made (W1-V9-ASYNC-ENUM).
- No probe, selftest, namespace, mount, seccomp filter, sudo, setup, vault or window action was performed for v11.
- Exact arithmetic (JACKAL `exact`, lane `rat`, not formal-bounded, outside the Lean certificate chain) supplies no
  capacity bound, no geometry, no backup completeness and no correctness of any code. No consequence-ceiling field was
  returned; the results are informational.
- A kernel-enforced writer boundary is not proof of the frame code, not lead authentication, not target confinement
  and not capacity. The ruled residuals (a)–(d) keep exactly their stated limits.
- v11 requests no approval and adds no gate; every privileged element stays inside the existing reserved operator
  setup, probe and rollback authority, prepared as the package of §16.1.
- **The review-provenance join change (§23) is a change to an original admission join, stated as such with its
  authority and the original texts it changes. It is not a loosening by assertion, and it is not reviewed. Adoption is
  blocked until it is reviewed in the frame-design revision.** v11 decides nothing about it beyond stating it.
- **W1-V10-FORM is resolved in v11.** v11 is a single self-contained specification: every unit's bytes are present in
  this file and §18.5 / Part V11-MAP records each unit's own computed v11 sha256, under the normalization rule of
  §V11-0.1 for the formerly-AMENDED units. **W1-V10-COUNT is fixed**: the unit partition in Part V11-MAP and in
  `v11-support/jackal.json` is the actual map (§V11-C.2), re-derived through JACKAL. These are form/bookkeeping
  corrections that weaken no obligation, fixture, threshold, accepted case or join.

## 21. Preservation over the complete original domain [corrections: W1-V8-PRESERVATION-ESTABLISH, W1-V7-FULL-DOMAIN; v7: W1-V6-CATALOGUE, W1-V6-PRESERVE; v6: W1-V5-PRESERVATION]

### 21.1 The relation

**The original domain.** Its elements are complete original situations: a lead invocation of `adopt`, `materialize`
or `dispatch` with any operands the original frame validates (labels by `NAME_RE`, overlays with validated Ada units
and deletions, every action of `command()` with every enrolled unit and line operand, S:33, S:78, S:959, S:1054); any
prestate the original accepts (lead-tree contents, owners and modes of inputs, foreign-owned readable inputs, the
window and inbox, the toolchain, the vault's state, the host's processes, mounts, services, network and load); the
inherited environment and process attributes (§8.3); the resources (memory, CPU, storage, limits); the target-created
partition states of earlier attempts; and the schedule of concurrent events by other principals. The original system
is frame v5 (S5) with the criterion-required repair (S6, R1-R2).

**What the original yields** for each situation: an outcome (accepted with success, accepted with non-success, or
refused at a named stage); the target's observable behaviour (its exit status, streams, report, partition contents
and their metadata, its side effects outside the run tree, its interactions with other processes and services);
the frame's records and their readers; the window's state; and the backup behaviour (the vault pin and what later
snapshots contain).

**Preservation** holds for a situation iff W-1 yields the same outcome class at the same stage, the same target
behaviour (apart from fields that vary between two original runs of the same situation, such as times and inode
numbers, which the original compares never or only within one run), equivalent records for every original reader,
the same window behaviour and equivalent backup content, **except** where the criterion itself requires otherwise:
(i) R1-R2 (V5-B01's revalidation and parent-observation join) and (ii) situations whose original outcome depended on
an outside principal changing the admitted generation or a frame location after admission or during a frame mutation,
which V5-B01 and V5-B02 forbid. Timing equality is not part of the relation, but every outcome that depends on timing
or cost (a prover limit reached, a time limit, an OOM kill, an allocation failure) is: a W-1 change of cost that can
change such an outcome is a change.

**TOOL-CLOSURE** (§9.8 N7) is a sub-lemma for the target-behaviour part over the allowlisted tools; the frame,
preparation, reader, window and backup parts need the separate rows below. **How a row closes** (§13.2): a V-row by
S-6 (the tools' source, with release-to-installed equality) together with S-5 (the frame); a C-row or D-row by S-5,
with I-8 and I-7 as refutation and per-input evidence. Runs never close a row on their own.

### 21.2 The criterion's repairs

| | Outcome | Treatment |
|---|---|---|
| R1 | the final pass refuses a leaf whose complete `stat_key` changes during the final walk, excluded leaves included (§4.5 item 1) | required by V5-B01 (review: PERMISSIBLE_REQUIRED_CRITERION_REPAIR); OPEN as V5-B01 is |
| R2 | the child stage refuses a recorded or excluded leaf that differs from the admitted parent observation (§4.5 item 2) | required by V5-B01; the author's argument that it fires only after a premise failure or helper misbehaviour is not established; I-8's drift cases (P-DRIFT) refute or support it per input |

### 21.3 Target-world changes (V-rows)

"Kept for" names the custody fact whose only available mechanism on this kernel causes the change; that is a reason,
not an entitlement. Every row is OPEN.

| | Change (§12.3) | Kept for | Discharge route (§13.2) | What would close it, and what refutes it |
|---|---|---|---|---|
| V1 | no host network | inbound abstract-socket channels | S-6; U-11; I-7 | closes if S-6 shows no allowlisted action, operand or option uses the network or a host loopback service; refuted by any traced or source-found use, which requires a redesign (for example a userspace forwarder, §22.3) |
| V2 | no outward pathname UNIX connection; no socket file outside the binds | pathname channels in both directions | S-6; U-11; I-7 | closes if every socket the tools create lies in the run tree or `TMPDIR` and every connection is to a server of the attempt's own tree; refuted by a connection to an outside server or a socket elsewhere |
| V3 | no mount operations | inherent to V2's mechanism | S-6; U-11 | closes if no tool mounts (including in nested namespaces); refuted otherwise |
| V4 | set-ID and file-capability `exec` confers nothing | credential containment of an identity-mapped U8 | S-6; U-11 | closes if no tool execs a set-ID or file-capability program; refuted otherwise |
| V6' | later host mounts and unmounts do not reach the view | the run path must not be substitutable by a later host mount | S-6 (no tool reads a path under a mount made during its run) | closes only by that source argument; no run can show it |
| V7' | private `TMPDIR` | unreachable socket files of the target's own servers | S-6; U-11; I-7 | closes if no tool reads or writes another process's files in `TMPDIR` and no other process needs the target's; refuted otherwise |
| V8 | run-path presentation (mount root, skeleton levels, separate D entries) | location custody of the generation; no frame or lead write outside T | S-6; S-5; I-7 | closes if no tool renames or removes `source/`, writes at the skeleton levels or renames between D's entries; refuted otherwise |
| V10' | system scope in `user-1000.slice` | an RL scope no non-root process can enter or leave (H(U)) | S-3; I-7 | the `app.slice` shared budget and the CPU/IO sibling set cannot be reproduced; stays OPEN as a stated change unless S-6 and the capacity evidence show no original outcome depends on them |
| V12 | Landlock domain | V2 | S-6; U-11 | closes with V2 and V3, and if no tool inspects or stacks Landlock in a way whose result differs |
| V13 | namespace-qualified ptrace and accounting effects | the pull closure | S-6; U-11; I-7 | closes if no tool inspects other processes' details or reaches a per-user limit whose accounting changed; refuted otherwise |
| V14 | Linux AIO and `io_uring` return `ENOSYS` | H(U)'s absorbing property | S-6; U-11 (the trace includes `io_setup` and `io_uring_setup`); I-7 | closes if no tool calls either interface (or every caller falls back with an identical observable outcome); refuted by a call whose outcome differs |
| V15 | cross-mount `EXDEV` | the run tree, `TMPDIR` and host paths are distinct mounts (v5: one mount) | S-6; S-5; I-4 | closes if S-6 shows no allowlisted action moves or hard-links an entry across the run tree / `TMPDIR` / host boundary; refuted by any such use |
| V16 | M_run id restrictions | enforced-location identity of generation bytes | S-6; S-5; I-4 | closes if no action `chgrp`s a generation entry to a supplementary group or sets a foreign-id ACL and no reader depends on such ownership/ACL; refuted otherwise |
| V17 | per-namespace keyrings | the user namespace (V13) | S-6; I-4 | closes if no allowlisted action uses a keyring whose contents or scope the view changes; refuted otherwise |

### 21.4 Frame-side and observer changes (C-rows)

| | Change | Discharge route | Treatment |
|---|---|---|---|
| C1 | the generation's originals are not readable by the lead; readers use exports, which include the complete capture; the vault pins the export tree (V-BACKUP) | U-14, I-6 for B1-B5; S-5 | OPEN: the capture's equivalence for every original reader and backup consumer is established only by those runs and their review; direct reading of the run directory by the lead is a workflow change that no route removes |
| C2 | the frame's reads below `source/` and `tmpdir/` change no access time (v5's did) | S-5; P-NOATIME | criterion-serving (V5-B02 read mutation); observable; OPEN |
| C4 | setup changes visible to every host process: the two accounts, the sudoers and sshd drop-ins, `/var/lib/wlscratch` with its ACLs, `/opt/wlscratch`, images if chosen | O-1; S-I | reserved operator setup (review: RESERVED_OPERATOR_SETUP_NOT_NEW_AUTHORITY); OPEN |
| C5 | added cost before launch (RL's two stages, the view, the censuses) and after (the capture) | I-7 (timings recorded per run) | OPEN: outcomes that depend on cost are in the relation (§21.1) |
| C6' | label lifecycle: v5's lead could free a label by deleting the run directory; a generation in T cannot be deleted by the lead | — | OPEN; every state reachable through frame verbs has v5's outcome (§3.3) |
| C7 | the scope is listed by the system manager, not by `systemctl --user` | — | part of V10'; OPEN |
| C9 | process attributes that cannot be reproduced identically: the session and process group (sudo's chain), CPUs gone offline | I-7 (recorded per run) | OPEN |

### 21.5 Non-success outcomes in states the original accepts (D-rows)

| | Outcome | Discharge route | Treatment |
|---|---|---|---|
| D1 | K shows an earlier RL scope populated while M shows it ended | S-3 (P-MGR); I-3 | OPEN; refuted P-MGR → redesign |
| D2 | RL cannot build the view (a namespace, mount, Landlock, seccomp or credential step fails, for example from kernel resource exhaustion) | S-2 (the failure modes of each call); I-8 | OPEN: new non-success states |
| D3 | an original observation taken in the view differs from its baseline | U-13, I-7 (per run) | OPEN (P-VIEW is a relation) |
| D4 | Gate 0 deferral with the W-1 allowances, A_capture included | — | the original storage ruling's own deferral (review: PERMISSIBLE_ORIGINAL_STORAGE_DEFERRAL_IF_COMPLETE); OPEN as safe fresh capacity is |
| D6 | W-1 machinery: lease held, channel failure, first-act failure, RL identity failure, record membership `fallback`/`raw`/`unknown`, provenance `failed`/`unobserved`, branched journal, export or capture failure, recovery needed | S-5; I-8 | OPEN: truthful failure reporting, not a redefinition of success; no causal absolute is claimed |
| D7 | C's run-path alias check refuses (§4.5 item 4) | S-5; I-8 | v5-class: v5 refused a run directory its held location chain no longer reached; OPEN only as the mapping argument |

### 21.6 What remains, and what would discharge it

Every V-, C- and D-row marked OPEN keeps W1-V5-PRESERVATION OPEN, and with it V5-B01 and V5-B02. A row is discharged
only by the relation of §21.1 established for it over the complete original domain, with source-to-binary
correspondence for the tools and the frame (strings, sampled runs or the absence of a known counterexample do not
discharge), or by a redesign that removes the change. No row is narrowed by restricting the domain, adding a gate,
stripping an attribute or calling a failure accepted. Rows that no route can close as written (C1's reader workflow,
C6', V10's shared budget) stay OPEN as stated changes of the original domain.

## 22. Architecture evaluation: enforcement designs beyond the unprivileged DAC architecture [correction: W1-V6-PRESERVE]

### 22.1 The question, with the success domain fixed

Does any enforcement design meet V5-B01 and V5-B02 while keeping the original success domain fixed: no new refusal
of an original accepted case, no observable output substitution, no cap? The original success domain is §21's S5
baseline; the S6 repair is the criterion's. Every privileged element must lie inside the existing reserved operator
setup and rollback, with no new approval gate.

### 22.2 The review's K0 ruling (verbatim, `review.json` `k0_assessment`)

> A sound obstruction for the stated unprivileged userspace/DAC architecture and already-shared writable open file descriptions; no preserving mechanism was identified. Not a universal proved impossibility theorem for every Linux enforcement design. Keeping both original blockers OPEN is correct; the no-output-refusal absolutes are false.

What a design must therefore establish, without copying or changing outputs: (1) no principal outside the target's
own process tree can obtain or keep a description of, or a name for, an admitted entry; (2) the end of every holder
inside that tree is an observable event that cannot be undone; (3) every frame mutation is confined, read-side access
times included; (4) the original success domain is unchanged.

### 22.3 Candidates, re-evaluated [corrections: W1-V8-HOLDER-IOEXIT, W1-V8-WRITER-AS-W; v8: W1-V7-ARCHITECTURE]

The v7 review's direction (verbatim, in part): "Candidate (a)+Landlock is a plausible custody research direction that
removes copy-induced inode/attribute substitutions, not an endorsed design or an authorized implementation direction.
Its custody conclusion is conditional and incomplete. The c8 ptrace rejection is wrong for the documented commoncap
rule; blanket seccomp-user-notification impossibility and instantaneous cgroup/manager/holder equivalence are
overstated. Re-evaluate lesser-change root-owned, same-host-UID namespace designs before claiming (a) alone is viable."
The v8 review found v8's evaluation sound (`alternatives_assessment`) and asked for two things that change this unit:
the owner vector (W1-V8-WRITER-AS-W) and the asynchronous holder path (W1-V8-HOLDER-IOEXIT).

**c8 (kept from v8, with the owner changed).** Pull routes: an outside `sicarii` process passes the uid half of
`__ptrace_may_access` and fails commoncap's capability half, because the target's user namespace is not its own and
its owner is not 1000 (§9.8 N2). Owner choice: root-owned and dedicated-owner namespaces give the same pull closure; a
`sicarii`-owned one gives every `sicarii` process the owner rule. v8 chose W, which spares root's per-user budgets but
gives A1's `writer.py` (reachable through the S1 rule) every capability over every U8. v9 chooses N, an identity no route
confers (§5.3): it keeps root's budgets apart (P-UCOUNT charges N) and removes the vector, at the cost of one more locked
system identity. Push and name routes: as v8 (§9.8 N1, N3). Set-ID: `nosuid` everywhere (V4).

**The holder boundary — candidates for closing the asynchronous paths** (W1-V8-HOLDER-IOEXIT):

| Candidate | What it closes | Cost | Verdict |
|---|---|---|---|
| H1: argue v8's P-IOEXIT from the source | nothing new: the source shows the opposite (an AIO completion wait deferred to the last memory-context user; untracked `io_uring` requests not waited for at exit, correction 0.2 item 1) | — | rejected: the path exists |
| H2: deny the two asynchronous submission interfaces in the view (seccomp, `ENOSYS`) | every write path that can outlive its task (§9.8 N4) | V14: AIO and `io_uring` unavailable in the view; `Seccomp: 2` visible | **adopted** |
| H3: deny only direct I/O (`O_DIRECT` in `open`/`openat`/`fcntl` flags) | not enough: `openat2` passes its flags in memory (unfilterable), and `io_uring`'s own open operations bypass the filter, so `io_uring` must be denied anyway | a larger, less precise change | rejected |
| H4: a per-attempt filesystem freeze (`FIFREEZE`/`FITHAW` by RL after `populated 0`), which waits for every write that holds freeze protection, async completions included | the asynchronous paths, without a target-world change | a privileged per-attempt action that freezes the whole filesystem holding g: without images that is the host root filesystem (every host writer stalls; a host-wide availability effect and a frame-caused effect outside T); with images a finite image, whose size is a cap the criteria make ineligible as an accepted refusal | not adopted: it moves the change from the target to every host process, or depends on images |
| H5: a mount-reference barrier (a root keeper unmounts the attempt's bind without `MNT_DETACH`, which succeeds only when no reference through it remains) | references opened through the bind | fails for references through copies of the bind in nested mount namespaces the target can create, unless nested user namespaces are also denied (a further change); needs a privileged keeper process outside the scope | not adopted |
| H6: a PID namespace with the scope's init as reaper | task ends, not asynchronous completions | changes the target's process view; does not close the paths | rejected |

**seccomp, narrowed (v8, kept).** Classic filters see `struct seccomp_data` (the syscall number, architecture,
instruction pointer and `args[6]`; installed `/usr/include/linux/seccomp.h` lines 62 and 66), so they can deny a system
call by number (H2 does exactly that) but cannot judge pointed-to memory. User notification with a decision on target
memory followed by `SECCOMP_USER_NOTIF_FLAG_CONTINUE` (header caution at line 85, flag at line 109) is unsound for policy;
an emulating broker using `SECCOMP_IOCTL_NOTIF_ADDFD` (line 152) is not excluded, and remains a rework candidate for V1
and V2, not adopted (§22.3 table below).

**The comparison** (custody "under premises" means: established under the premises of §9.8 N7, none established):

| Candidate | Custody under premises | Target-world changes | New trusted components | Verdict |
|---|---|---|---|---|
| (a) v7 view, host uid R | yes (with H2's gap closed the same way) | V1-V12 of v7, including the host identity change, the root idmap, omitted mounts, masks, private `/tmp`, the lead step | RL, three identities | superseded by SIV |
| c8, root-owned, same uid | yes | SIV's, plus the target's per-user counts charged to root | RL | not adopted (host-wide accounting effect) |
| c8, W-owned (v8's SIV) | yes for the target, but A1's `writer.py` as W holds every capability over U8 | as SIV | RL, one identity | superseded: the owner vector (W1-V8-WRITER-AS-W) |
| **SIV v9** (c8, N-owned, with H2) | yes | §12.3 (V1-V4, V6', V7', V8, V10', V12, V13, V14) | RL, two identities | **adopted** |
| SIV + PID namespace, user-manager scope | no: a delegated scope lets processes leave and enter, which breaks v5's terminal predicate | adds a PID namespace and a new `/proc` | RL | rejected |
| SIV without network namespace (Landlock abstract scope) | no: inbound abstract connections stay open | fewer | RL | rejected |
| SIV + userspace network forwarder | yes | V1 replaced by changed addresses and interfaces | RL plus the forwarder | not adopted; a V1 rework candidate |
| SIV + emulating seccomp broker in place of V1/V2 | possible, not specified | narrower refusals, `io_uring` denied already, seccomp visible already | a root broker | not adopted; a V1/V2 rework candidate |
| b, Landlock alone | no (inbound callers unconstrained) | — | — | insufficient |
| b, seccomp classic alone | no | — | — | insufficient |
| c1 distinct uid alone | no | — | — | insufficient |
| c2 BPF LSM / another per-domain LSM | possible with a narrow policy | potentially fewest | a kernel with that LSM (an existing reserved toolchain/deployment decision) | unavailable on this boot (`CONFIG_BPF_LSM` not set; LSMs `capability,yama,landlock`) |
| c3 fanotify | not alone; combinations unestablished | — | — | insufficient alone |
| c4 separate kernel | not specified; nested virtualization UNVERIFIED | wholesale | a VM | not adopted (fidelity objection, not impossibility) |
| c5 copies, overlays | substitutes inodes and attributes | — | — | rejected (the fixed target) |
| c6 revocation, c7 locks and leases | no general mechanism | — | — | insufficient |

### 22.4 Conclusion

**v9 adopts the same-identity view with owner N and the asynchronous-submission filter** because, of the candidates
that establish the custody facts under named premises, it has the smallest set of changes and no known gap in its
holder argument: against v8 it adds one locked identity and one target-world change (V14), and removes the owner vector
and the asynchronous holder paths. It does **not** preserve the original success domain as established: §21's OPEN rows
remain, and the rework candidates (a network forwarder, an emulating broker) and the preserving-direction candidate (a
narrower LSM in a different kernel, a reserved decision) are not designed here. **V5-B01, V5-B02, W1-V5-PRESERVATION,
W1-V6-READ-MUTATION and W1-V7-HOLDER-STATE stay OPEN** until §13.2's runs discharge the premises and rows and an
independent review accepts the evidence. If any premise of §9.8 N7 is refuted, W-1 must be redesigned for it; no
exception is taken.

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
- `/home/sicarii/Documents/complete-phase1-prompt.txt:60`: *"Use actual gpt-6.1-sol for every required independent
  review. Confirm the actual model identity; never substitute a role label or another model. If unavailable, continue
  independent authorized preparation and engineering, but retain the review gate as blocked. …"*

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
cannot bind any review of either form and v11 cannot reach adoption.** The join still refuses anything unsealed,
unbound or author-reviewed, and never a label alone; whether that makes it "not a loosening" is for the frame-design
review to judge.

## Appendix A. Verbatim criteria

Source: `work/claude-scratch-frame-v5/review/gpt61-v1/REVIEW.md`, sha256
`2c414c694ed75d72cffae2172bef967bdcf63d73cc0a3764f96762a59d49ec71` (sealed by `review-freeze.json`
`48539bdf57e11edeabe0844c7860284fa1cde26c1cab58a7b86317ef82a34ef7`). Each block reproduces the named source lines
byte for byte, one source line per line, blank lines included.

**A.1, line 76 (V5-B01 required change):**

```text
Required change: Retain file observation identities through the complete walk and revalidate every encountered leaf, including excluded generated leaves, using complete descriptor metadata and named-entry joins at the final admission boundary. Bind the accepted source/output generation to the spawn under custody that prevents the admitted generation from changing before use. Directory-only revalidation or after-run detection must not substitute for pre-launch alias refusal. Preserve the exact base recipe, output partitions, allowlist, caps and original gates.
```

**A.2, line 82 (V5-B02 required change):**

```text
Required change: Provide enforced location custody across each frame-owned mutation and the final admission-to-spawn handoff, rather than observer-only checks before and after it. Use an independently protected writer/location boundary or an equivalent enforced lease that concurrent same-user rename/substitution cannot invalidate while writes or launch are possible. Keep original outside-tree authority limited to the documented window protocol and prescribed preparation records. Do not relabel frame-owned outside-tree writes as the running-target residual or lower the original guarantee; retain this blocker if custody cannot yet be established.
```

**A.3, lines 84-123 (boundary assessments, N-items, explicit residual rulings, terminal semantics):**

```text
The source-tree problem does not require unchanged timestamps or undetectable file metadata. The earlier leaf's nlink/ctime/content can actually differ; the final algorithm simply never compares those file fields again. An outside hard link does not add/remove/rename an entry in the walked source directory. The frame-mutation problem likewise does not depend on target behavior: the frame's own fd-relative writes/chmod/mkdir can happen after a location check and before its later refusal. Detection and a non-success result are useful, but they do not undo those specified prohibited outcomes.

| Boundary reviewed | Passive assessment | Evidence |
|---|---|---|
| Reviewed/adopted frame and fresh lead | Full fixed roster/profile/sidecar and actual rollout/final/model/cwd/provider/argv joins remain. fresh_lead runs before parent and child admission. This UNQUALIFIED review must fail the required QUALIFIED profile; no adoption or fresh observation was performed. | S:687-863, 1557-1559, 1809-1815 |
| Launch seal carried in argv | The child hashes launch/admission bytes, joins launch to intent/admission and verifies its own argv. Parent conclusion checks launch/intents/reservation/admission/launcher records against in-memory pins and uses the original seal. No re-read local data substitutes for those expectations. | S:1570-1594, 1662-1694, 1783-1817 |
| Token window and other holder protection | Reservation requires released status; ownership joins holder/candidate/token; only parent conclude calls release and checks those fields under the same flock. No conforming-protocol holder overwrite found. Stable lock replacement remains N07. No live window was read or locked by the reviewer. | S:1253-1341, 1735-1755 |
| Full child admission, allowlisted argv, exact environment and caps | Common admission repeats frame/materialization/tool/data/ELF/vendor/runtime/manager checks. Child compares the complete observed environment minus a validated INVOCATION_ID, parent memory gate, final memory threshold, allowlisted command, cgroup unit and effective memory/swap/core limits. Named gate calls are preserved; V5-B01/B02 prevent treating the directory/leaf observations as sufficient custody. | S:1054-1106, 1131-1179, 1440-1448, 1809-1845 |
| Dir location chains and created-directory authentication | Components use O_DIRECTORY/O_NOFOLLOW; created directories require owner/mode/nlink/device/empty/non-ancestor checks before chmod/write. Residual (a) is narrowly acceptable in item 3. V5-B02 blocks full mutation/launch lifetime reliance. | S:155-237, 308-345 |
| observe_tree and verify_materialization | Exact fixed base descriptors/keyset/modes plus validated Ada snapshot/deletions are reconstructed; non-partition and snapshot directory identities are bound to materialization. Partition identities are sealed. The final pass omits file metadata and remains V5-B01. | S:495-582, 868-956, 1030-1044, 1566-1569, 1842-1845 |
| retain/read_record/refusals | Primary/retry/stderr are create-only attempts; cleanup/parsing errors are aggregated. Parent and child pre-launch refusal records include explicit no-target-started meaning. Unparseable child records remain raw and withhold release. Durability is not established when commit fails; N11/N12 describe remaining consumer/schema hardening. | S:375-436, 1530-1537, 1579-1581, 1848-1858 |
| Owned participants and conclude | Active/unavailable scope/cgroup or present known pid/process marker refuses terminal classification; unreadable/unparseable participant records are unresolved. Wait records precede fallible cleanup. Materialization/seals/report/post-identities/raw child-wait read are guarded. Only terminal ownership permits release; release errors/withholding/conclude errors have separate records. | S:1375-1437, 1611-1765 |
| Signal, interrupt and crash paths: dispatch/parent/child | Handled signals are masked through Popen/handle enrollment and recording, child preexec unblocks, and wait_blocked synchronously forwards SIGTERM until actual exit or explicit unresolved wait. Pending sweeps exist at the requested boundaries. SIGKILL/dead launching parent has no late collector and leaves manual reservation resolution. Surviving parent independently observes child/wrapper/launcher scope/pids and treats partial records conservatively. No new lost-started-wait/unsafe-release path was found under those stated ceilings; V5-B02 still affects record custody and N13/N14 affect final error reporting. | S:1469-1517, 1595-1641, 1848-1896, 1918-1988; F:358-361 |
| Retained evidence and reviewed inputs | Writes use exclusive leaves; the report is copied to a distinct exclusive artifact; snapshots/base/launch pins are rechecked; no prune/standing verify/late collect surface exists. This does not grant same-user protected evidence or immutable source proof. V5-B02 can still place frame writes outside the named tree. | S:308-327, 959-1048, 1662-1717, 1991-2007 |

NON-BLOCKING observations (the source references are part of each finding):

- **N01 — Actual fresh per-challenge MCP origin remains a lead obligation.** Shape, parsed/exact fields and in-attempt hash non-reuse do not authenticate actual MCP origin or cross-attempt freshness. Every live challenge still needs the legitimate lead to call actual MCP. Reviewer fixed-expression responses authorize no challenge or launch. Evidence: S:1182-1248, F:85-90;277-280.
- **N03 — Report mtime and zero exit remain engineering observations.** The old separately reread report mtime is fixed: bytes and st_mtime_ns now come from read_observed on the same descriptor. Incremental output may still be old, and neither mtime nor command-zero establishes report origin, full body/caller coverage, proof or acceptance. Evidence: S:1695-1708, F:281-282;366-367.
- **N04 — Copies and prospective identities transfer no original acceptance.** All original support/native-cost/custody/capacity/backup/body/caller/runtime/fault/Phase One obligations remain OPEN. Passing author cases, copied modules and exact arithmetic supply none of those guarantees. Evidence: F:368-373, /home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-frame-v5/modules/runtime_inventory.py:1-5.
- **N07 — Shared flock still assumes a stable cooperating protocol inode.** O_NONBLOCK and single-link regular-file hardening are implemented. The name/parent/inode of the cooperating lock still must not be independently replaced while another holder uses it. This is the inherited reference ceiling, not a new conforming-protocol overwrite finding. The exception grants no arbitrary outside-tree write. Evidence: S:1253-1292;1295-1341, F:285-286;356-357.
- **N08 — Verified-byte module execution retains its bootstrap and cached-state ceiling.** Fresh exec_verified hashes the exact bytes it compiles/executes. Its sys.modules branch relies on __verified_sha256__ metadata; outer Python bootstrap and path-launched frame entrypoints are not protected pre-main/provider/cached-code custody attestation. Complete prospective identities remain required and original custody obligations remain OPEN. Evidence: S:52-57;587-614, F:277-280;350-355.
- **N09 — Pending-signal sweeps are observations rather than atomic cancellation.** The requested pre-spawn and post-wait sweeps exist. Signals arriving after a sweep can still be forwarded during waiting or arrive later during final recording; the code does not atomically combine signal arrival with Popen. This alone bypasses no admission/cap or terminal-ownership gate. Evidence: S:1478-1517;1596-1606;1861-1884;1923-1930.
- **N11 — Fully written failed primary commits need explicit archival interpretation.** write_json can finish bytes then fail fsync or post-validation. retain leaves that primary and writes a retry/error record; result retries are downgraded. read_record distinguishes unreadable/unparseable bytes but has no separate committed-primary marker, so a syntactically complete failed primary can still be parsed. Current aggregated errors/nonzero wait outcomes prevent scratch success in the affected paths; archival consumers must join primary, retries and refusal/error records instead of treating any parseable primary as durable success. Add explicit committed-record descriptors/markers for consumers. Evidence: S:308-327;387-436;1731-1759;1880-1896.
- **N12 — Participant-record semantic validation is narrower than parse validation.** read_record requires only a JSON object; owned_terminal extracts whichever integer pid fields are present. A valid JSON object with missing/wrong participant fields is not marked unresolved. Scope/cgroup and in-memory launcher observation still independently prevent a demonstrated live conforming participant release. Validate each participant schema and required pid/wait fields before classifying the record. Evidence: S:418-436;1372-1415.
- **N13 — Late directory-close errors are reported after the success calculation.** conclude checks errors after result/release, then guarded handle closes can append further errors. Its success variable and exit decision are not recomputed after those closes, and no new terminal error record is then attempted. This contradicts the blanket any aggregated error means nonzero prose, but occurs after waits/stream sync/terminal observation and does not establish one of the blocking outcomes. Include late close errors in the terminal disposition. Evidence: S:1756-1765, F:215-216.
- **N14 — Dispatch can exit zero despite its own failure or interrupt record.** dispatch terminal.json records failure/notes, but its exit expression considers only code and errors. If the run returns zero, a dispatch failure or interrupt can still leave dispatch exit zero. The actual run wait and terminal failure remain retained and this is not a target admission bypass. Make dispatch exit reflect failure/interrupts too. Evidence: S:1953-1988.

The author self-check's observed case count and success are author reports only. AUTHOR-SELFCHECK.json explicitly excludes adopt and the real run/child launch/scope path. No candidate code, compiler, prover, build, test, reservation or admission action was executed by this reviewer. The Claude adversarial pre-read was not consulted and supplies no closure weight.

**3. Explicit residual rulings**

| Stated residual | Ruling and exact limit | File:line evidence |
|---|---|---|
| (a) Empty owned 0700 directory between mkdir and open | **Acceptable as documented, narrowly.** The frame requires owner, exact mode, link count, same device, empty contents, named/open inode agreement and non-ancestor identity. Substitution of an indistinguishable empty directory at the intended name does not itself redirect a file write to another location or overwrite prior file contents. POSIX mkdir did not return an inode handle, so no original-mkdir identity is established. This ruling is not a continuing location lease; the separate post-check/pre-mutation detachment in V5-B02 remains BLOCKING. | F:117-135; S:192-223 |
| (b) No confinement of the running target; conclusion detection | **Acceptable as documented at the reference engineering ceiling.** Reference run_checks.py starts the target by path/cwd without a filesystem sandbox; it performs before/after readbacks. v5 similarly cannot prevent an already-running target from resolving absolute paths or writing while another process changes the tree. The resulting attempt must remain non-successful on detected drift. All original confinement/custody obligations remain OPEN. This residual does not authorize frame-owned outside-tree mutation, nor an unsafe alias already present at the final launch admission. | F:69-76, 349; S:1512-1517, 1662-1694; F10K/run_checks.py:42-47, 293-325 |
| (c) Executing the identity-checked target by path | **Acceptable as documented at the reference ceiling.** S:1839-1841 checks the allowlisted executable hash; S:1867 executes the sealed argv by path. Full before/after tool/ELF/data/vendor/runtime identity comparisons remain. F10K run_checks.py:43 and :294 use Popen paths too. This establishes no exec-inode, mapped-library or protected pre-main custody; those original guarantees remain OPEN. | F:354-355; S:1131-1153, 1711-1716, 1839-1867; modules/proof_elf_inventory.py:1-5, 85-89 |
| (d) Metadata/timestamp granularity | **Acceptable as documented for genuinely identical compared fields.** Device/inode/mode/nlink/owner/size/mtime_ns/ctime_ns are compared by stat_key, excluding read-altered atime. No claim is made about the actual kernel resolution. A change preserving every compared field is an acknowledged observational limit, not an original consistent-snapshot proof. V5-B01 differs: changed leaf fields are simply never revisited by the final tree pass. | F:363-365; S:138-141, 246-266, 530-567 |

No residual ruling changes a required accepted case, contract, proof floor, control or Phase One exit requirement. None removes V5-B01/V5-B02 or authorizes use of this UNQUALIFIED candidate.
```

## Appendix B. Schemas (exact key sets; every record also carries the §4.4 common fields)

Common fields of every record: `generation` (str, 32 hex, or `null` for P_ado records), `attempt` (str stamp, or
`null` for P_adm and P_ado records), `boot_id` (str), `channel_heads` (`{"F2W": hex, "W2F": hex}` or the pair of the
invoking channel), `record_seq` (int), `prev_commit` (hex, or `null` for the first of a journal, §10.2), `at` (UTC
ISO-8601 string), `label` (v5 `LABEL`). The new keys listed below are str, int (|n| < 2^63), bool, null, list or
object, never floating-point; embedded v5 structures (observations, samples, v5 record keys) keep their v5 types
unchanged.

### B.1 Role identity: `wlscratch-role-identity-v2`

`role` ∈ {`front`, `writer`, `seal-front`, `launcher`, `child`, `observer`, `root-launcher`}; `pid`, `ppid`,
`start_time_ticks` (int); `comm` (str); `argv` (list of str); `exe` `{path, dev, ino, sha256, mnt_id}`; `uids`, `gids`
(4 ints: real, effective, saved, fs); `groups` (list of int); `caps` `{inh, prm, eff, bnd, amb}` (hex str);
`no_new_privs` (int); `seccomp` `{mode, filters}` (int); `dumpable` `{set_result, pr_get_dumpable, proc_self_fd_uid}`
(int); `umask` (int); `rlimits` (object: every `RLIMIT_*` name → pair of int); `sched` `{nice, policy, priority,
ioprio, affinity, oom_score_adj, personality, timerslack_ns}`; `cgroup` (str); `namespaces` `{mnt, mnt_id, pid, user,
user_owner, net, cgroup}` (int); `maps` `{uid_map, gid_map, setgroups}` (str, as read from `/proc/self`; for processes
outside a view the initial namespace's); `cwd` `{dev, ino, mnt_id}`; `stdio` (list of `{fd, type, dev, ino, mode,
flags}`, `type` ∈ {`fifo`, `socket`, `regular`, `char`, `dir`, `other`}); `open_fds` (list of int); `environment`
`{names, sha256, values}` (values only for the clear keys of §8.1); `python` `{version, executable, prefix,
base_prefix, flags, path}`; `modules` `{files: [{name, path, bytes, sha256}], builtins: [str]}`; `frame_inventory`
`{sha256, bytes}`. Inside a view, U8's identity maps make `uids`, `gids` and `groups` the host values; the parent
role's join still reads them through `maps` (§8.1).

### B.2 Participants, waits, scopes, census [corrections: W1-V8-HOLDER-IOEXIT, W1-V6-SCAN-STATE; v6: W1-V5-REVOCATION-CONFINEMENT; v5: W1-CUSTODY-CLOSURE]

- `wlscratch-participant-v1`: `role` ∈ {`S1`, `W`, `S2`, `RL`, `L`, `C`, `T`, `S_O`, `O`, `S3`, `W2`} (RL, L and C of
  one launch, and RL and O of one observer, share a pid; each role is recorded with the start time it had); `pid`,
  `start_time_ticks`, `ppid` (int); `uids`, `gids` (4 ints, as the initial namespace shows them); `groups`; `cmdline`
  (list of str); `cgroup` (str); `observed_by` (role); `state` ∈ {`alive`, `absent`, `reused`, `unknown`}.
- `wlscratch-wait-v1`: `waiter_role`, `waited_role`; `pid`, `start_time_ticks` (int); `raw_status` (int or null);
  `exited`, `signaled`, `core_dumped` (bool); `exit_code`, `signal` (int or null); `wait_error` (object or null);
  `interrupts` (list); `unresolved` (bool); `meaning` (str).
- `wlscratch-scope-v3`: `manager` (str: `system`); `slice` (str: `user-1000.slice`); `unit` (str); `invocation_id`
  (str); `control_group` (str); `properties_at_start`, `properties_at_end` (objects with `LoadState`, `ActiveState`,
  `SubState`, `Result`, `ControlGroup`, `MemoryMax`, `MemorySwapMax`, `LogLevelMax` and the §8.3 properties);
  `populated` (int or null); `cgroup_state` ∈ {`ABSENT`, `EMPTY`, `NONEMPTY`, `UNAVAILABLE`}.
- `wlscratch-census-v2`: `point` ∈ {`parent`, `child`, `final`, `after`, `capture`, `recovery`}; `round` (int or null);
  `observer` (participant); `k` (list of `{cgroup, populated, procs: [participant]}` for every `wlscratch-*.scope` child
  of `user-1000.slice`, with `observed_at`); `m` (list of `{unit, LoadState, ActiveState, SubState}` with
  `observed_at`, or null where the observer cannot reach the manager); `expected` (list of `{cgroup, procs:
  [participant]}`, §9.4's table); `root_scan` (object or null: RL only; `uid_n_processes` and
  `n_owned_userns_outside_rl_scopes`, each a list of participant); `unknown` (list of reasons); `verdict` ∈ {`pass`,
  `refuse`, `unknown`}.
- `wlscratch-terminal-v2` (v5's `owned_terminal` observation, §9.4): `unit`, `properties_first`, `cgroup`, `pids`,
  `processes_naming_attempt`, `properties_second` (the race-aware order of §9.4), `launched`, `launcher_pid`,
  `participant_pids_absent` (pid → bool), `unresolved_participant_records`, `terminal` (bool), `verdict` ∈
  {`known-terminal`, `live`, `unknown`} (at the after and recovery points).

### B.3 Records [corrections: W1-V8-EVIDENCE-EQUIV, W1-V7-SYNC-PROVENANCE, W1-V7-C3-DATA, W1-V6-COMMIT-AMBIGUITY, W1-V6-EVIDENCE-RESTORE, W1-V6-INVARIANTS; v6: W1-V5-REVOCATION-CONFINEMENT; v5: W1-PROTOCOL-FAILURE-STATES, W1-JOURNAL-CONTINUATION, W1-SETUP-IDENTITY, W1-CUSTODY-CLOSURE]

Every journal record body also carries `prior_sync` (list of `{name, marker_sha256, sync}`, `sync` ∈ {`ok`,
`failed`}: the sync outcomes of the records this writer committed in the same journal since its previous attestation,
§10.1 step 5).

| Record | Schema name | Keys beyond the common fields |
|---|---|---|
| `generation.json` | `wlscratch-generation-v2` | `created_at`, `writer` (B.1), `invocation` `{argv, sudo_user, sudo_uid, sudo_command, n_f}`, `front_triple` `{pid, start_time_ticks, boot_id}`, `lease` `{lease_dir: [dev, ino], lock: [dev, ino], uid, gid, mode}`, `location_chain` (list of `{name, dev, ino, uid, gid, mode, acl_sha256}` from `/` to g), `record_chain` (the same from `/` to g_rec), `mounts` (the §3.4 mount facts; empty without images), `installed_frame` `{inventory_sha256, inventory_bytes, install_root, source_frame}`, `setup_identities` `{sha256, bytes, dev, ino}`, `setup_seal` (str: `adopted`, `unadopted`; §11.7), `channel` `{protocol, n_f, n_w, genesis}`, `verb`, `run_label`, `attempt0` |
| `inputs/<seq>-<name>` and its `.json` header (P_adm; P_att for `dispatch`) | `wlscratch-input-v1` (header) | raw bytes file; header `{seq, name, class ∈ {pinned, joined, observation}, size, mode, sha256, pin_source, verdict, atime_route ∈ {noatime, foreign}}` (§8.6, §9.8 N6); `process-attributes` is an observation input |
| `inputs/manifest.json` | `wlscratch-inputs-manifest-v1` | `entries` (list of `{seq, name, class, size, mode, sha256, written_to}`), `heads_after_inputs` |
| `materialization.json` | `wlscratch-materialization-v3` | every v5 `claude-scratch-materialization-v5` key (with `run` = g's path), plus `generation_pin` `{record, marker}`, `inputs_manifest_pin`, `tmpdir_dir` `{path, dev, ino}`, `run_path` (str), `recipe_mode_property` `{files_others_readable, dirs_others_searchable}`, `channel_heads` |
| `attempt.json`, kind `materialize` | `wlscratch-attempt-materialize-v1` | `kind` = `materialize`, `created_at`, `writer` (B.1), `invocation`, `front_triple`, `generation_pins` exactly `{generation, generation_marker}`, `lease`, `channel`, `verb`, `args` `{label, overlay_dir}` |
| `attempt.json`, kind `dispatch` | `wlscratch-attempt-dispatch-v1` | `kind` = `dispatch`, `created_at`, `writer` (B.1), `invocation`, `front_triple`, `generation_pins` exactly `{generation, generation_marker, materialization, materialization_marker}`, `adoption` `{record, marker}`, `lease`, `channel`, `verb`, `args` `{action, args, inbox}` |
| `fallback-allocation.json` | `wlscratch-fallback-allocation-v1` | `path`, `dev`, `ino`, `uid`, `gid`, `mode`, `bytes`, `slot_bytes`, `slots`, `st_blocks`, `created_at` |
| `front/front-identity.json`, `front/front-stage-<stage>.json` | `wlscratch-front-stage-v1` | `stage`, `front` (B.1 at stage), `lead_observation`, `frame_admission_front` `{inventory, review, installed_review, adoption, rollout, adoption_observation}`, `base_tree_observation`, `runtime_observation` (compact or full, v5 item 4), `manager_environment`, `sibling_units`, `storage_reading`, `window_ownership` (child stage), `vault` (where run) |
| `observer-intent-<n>.json` (also under `w2-<k>/`) | `wlscratch-observer-intent-v3` | `n`, `stage` ∈ {`parent`, `after`, `recover`}, `observer_argv`, `rl_argv`, `n_o`, `view_spec_sha256`, `streams` (list of `{name, dev, ino}`) |
| `observer-<n>-<stage>.json` (also under `w2-<k>/`) | `wlscratch-observation-v5` | `n`, `stage` ∈ {`parent`, `after`, `recover`}, `observer` (B.1), `census` (`wlscratch-census-v2`), `walk` (with every excluded leaf's `stat_key` and every entry's mount ID), `identities` (v5, taken in the view), `sample_half`, `terminal` (`wlscratch-terminal-v2`; stages `after` and `recover`, else null), `report` (descriptor or null) |
| `launcher-rl-identity.json`, `observer-<n>-rl-identity.json` (the latter also under `w2-<k>/`) | `wlscratch-rl-identity-v3` | `frame_sha256` (hex64), `channel` (str: `W-L` or `W-O`), and the `RL_IDENTITY` body (B.4.3): `root_launcher` (B.1 at its `exec`), `view_spec_sha256`, `scope` (B.2), `census` (B.2), `user_ns` `{inode, owner_uid, uid_map, gid_map}`, `idmap_ns` `{owner_uid, uid_map, gid_map}`, `mnt_ns` `{inode, id}`, `net_ns` `{inode}`, `root` `{dev, ino, mnt_id}`, `cwd` `{dev, ino, mnt_id}`, `binds` (list of `{dest, mnt_id, root_dev, root_ino, attrs}`), `run_path_mode` (str: `bind`, `skeleton`), `skeleton` (object or null: `{d, created, attached, omitted}`), `mount_list` (the `listmount`/`statmount` results), `mountinfo` (list of str, as data), `landlock` `{abi, handled, rules}`, `seccomp` `{program_sha256, mode, filters}`, `helpers` (list of `{pid, start_time_ticks, uid, reaped}`), `scope_properties` |
| `launch.json` | v5 keys plus | `generation_pin`, `attempt_pin`, `parent_observation_pin` (the admitted parent observation of §4.2 D11: O's full walk incl. excluded-leaf keys), `view_spec` (§12.2: the namespaces and their owners, the maps, the binds and the run-path rule, the Landlock ruleset, the seccomp program, the credentials, U) and `view_spec_sha256`, `process_attributes` (§8.3: `uid`, `gid`, `groups`, `cap_bnd`, `rlimits` as `{name: [soft, hard]}` for every `RLIMIT_*`, `nice`, `sched` `{policy, priority}`, `ioprio`, `affinity`, `oom_score_adj`, `personality`, `timerslack_ns`), `rl_argv_template`, `launcher_argv_template`, `child_argv_template` (C), `streams` (names), `front_stage_pins`; v5 `environment` holds v5's environment (§8.4); v5 `adoption` is the descriptor of `lead-adoption.json` |
| `reservation-intent.json`, `reservation.json` | v5 keys plus | `window_lock_identity` `{dev, ino, nlink}` observed by F under the lock, `request_digest` |
| `admission.json` | v5 keys plus | `gate0_receipt_pin`, `front_stage_pins`, `observer_parent_pin` (the pin of the admitted parent observation, §4.2 D11), `writer_half_pins` |
| `launcher-intent.json` | v5 `scope_argv` (RL's `systemd-run` argv) plus | `rl_argv`, `launcher_argv`, `child_argv`, `seals` `{launch_sha256, admission_sha256}`, `view_spec_sha256`, `n_wl`, `n_c`, `streams` (list of `{name, dev, ino}`, exactly the stream names of D14), `journal_head` |
| `launcher-start.json`, `launcher-wait.json` (the relayed status of the RL/L/C pid), `sudo-launcher-wait.json`, `observer-wait-<n>.json` | B.2 participant or wait | — |
| `child-wrapper.json`, `child-stage-child.json`, `child-admission-summary.json`, `effective-limits.json`, `child-start.json`, `child-wait.json`, `child-refusal.json`, `child-cleanup.json` | v5 keys (`child-stage-child.json`: C's observations of the child stage, census and process-attribute readbacks included; `child-admission-summary.json`: the digests of every C1-C7 result) | sent by C over SP_C and committed by W; plus `channel` `{c2w_head}`; `child-refusal.json` keeps v5's `target_started: false` and its meaning, and is sent only before C's spawn call; `child-wait.json` keeps v5's keys and is sent after `CHILD_START` (`CHILD_WAIT`) or as the only outcome of a failed spawn call that left no child (`SPAWN_FAILED`, `started: false`) |
| `writer-half-parent.json`, `writer-half-child.json` | `wlscratch-writer-half-v4` | `stage`, `snapshot_observation`, `attempt_identity`, `journal_join` (§10.6 result), `lease` (held, identity), `location_chains`, `manager_census` (B.2 `m`) |
| `spawn-ok.json` | `wlscratch-spawn-ok-v1` | `c_identity_pin`, `admission_summary_sha256`, `front_pong_at`, `writer_errors` (must be empty) |
| `stream-finality.json` | `wlscratch-stream-finality-v3` | `streams` (list of `{name, dev, ino, sha256, bytes, stat_key_after_sync, stat_key_after_census, stat_key_before_commit}`), `census_pin` (U absent or `populated 0`), `final` (bool) |
| `result.json` | v5 `claude-scratch-run-result-v5` keys plus | `record_states` (name → `{state: primary/retry/fallback/raw/unknown, sync_provenance}`), `durability` ∈ {`complete`, `UNKNOWN`}, `terminal` (`wlscratch-terminal-v2`), `target_started` ∈ {`true`, `false`, `unknown`} (str), `streams_final` (bool), `w1` `{generation, attempt}` |
| `release-intent.json` (W) or `w2-<k>/release-intent.json` | v5 keys (`at`, `token`, `terminal`, `prior`) plus | `writer_role` ∈ {`W`, `W2`}, `classification_pin` (the after-stage or recovery terminal observation) |
| `window-release.json` (or under `w2-<k>/`) | v5 keys (`at`, `token`, `prior`, `current`, `terminal`) plus | `writer_role`, `intent_state` (the state of `release-intent.json`) |
| `release-withheld.json` (or under `w2-<k>/`) | v5 keys (`at`, `reason`, `owned_terminal`, `resolution`) plus | `writer_role`, `facts_sha256` |
| `release-not-owner.json` (or under `w2-<k>/`) | `wlscratch-release-not-owner-v1` | `token`, `window` (pin or null), `writer_role` |
| `release-failure.json` (or under `w2-<k>/`) | v5 keys (`at`, `error`, `resolution`) plus | `writer_role`, `reread` ∈ {`released`, `reserved`, `unreadable`} |
| `final-status.json` | `wlscratch-final-status-v3` | `success`, `released`, `durability`, `record_states_sha256`, `unknown_records`, `fallback_records`, `provenance_not_observed` (list of `{name, provenance}`), `capture` `{state, manifest}`, `late_errors` |
| `conclude-errors.json`, `refusal.json` | v5 keys | — |
| `w2-<k>/identity.json` | `wlscratch-w2-identity-v1` | `mode` ∈ {`seal`, `recover`}, `writer` (B.1), `capability` `{front_triple, s3: {pid, start_time_ticks}, front_parent: {pid, start_time_ticks}, verified}`, `attempt_writer_state` (participant state of the attempt's W), `lease`, `channel` |
| `w2-<k>/recovery/scan-<r>.json` | `wlscratch-recovery-round-v3` | `round` = r, `census` (B.2, point `recovery`), `terminal` (B.2) |
| `w2-<k>/recovery/result.json` | `wlscratch-recovery-result-v3` | `verdict` ∈ {`known-terminal`, `live`, `unknown`}, `rounds`, `last_round_pin`, `target_started`, `participants` (list of B.2), `provenance` (name → provenance, §10.5) |
| `w2-<k>/front-terminal.json` | `wlscratch-front-terminal-v3` | `mode`, `s1_wait` (B.2), `w_final` (or null), `w_early_refusal` (the `EARLY_REFUSAL` body, or null), `w_absent`, `answers_forwarded` (list of `{n, sha256, at}`), `interrupts`, `errors`, `heads`, `durability`, `recovery` (bool), `recovery_result_pin` (or null), `release` `{performed, intent_state, record_state, intent_result_late}` |
| `commits/<seq>-<tag16>.commit` | `wlscratch-commit-v2` | `seq`, `kind` ∈ {`primary`, `retry`, `export`, `continuation`, `close`}, `record` (`{path, sha256, bytes, mode, acl_sha256}`, or null for `continuation` and `close`), `skipped` (list of `{seq, files: [{name, sha256, bytes}]}`, non-empty exactly for `continuation`) (§10.2); a marker never states its own sync outcome, which later records attest (§10.1 step 5, §10.5) |
| fallback slot payload | `wlscratch-fallback-v1` | `record_name`, `stage`, `errors`, `value_sha256`, `value_bytes`, and exactly one of `value` or `value_truncated: true` |
| `export/generation/manifest.json`, `export/<A>/inc-<n>/manifest.json`, `adoption-<I>/export/inc-<n>/manifest.json` | `wlscratch-export-v4` | `increment`, `entries` (list of `{export_path, source_path, sha256, bytes, mode, acl_sha256, source_marker_sha256, state, sync_provenance}`, `state` ∈ {`committed`, `fallback`, `slot-raw`, `raw`, `uncommitted`, `payload`}; a `payload` entry has the lead-tree or P_adm path it was read from and no marker), `directories` (list of `{path, dev, ino, mode, acl_sha256}`) |
| the matching `freeze.json` | `wlscratch-freeze-v3` | `increment`, `cut` `{journal, seq, sha256}`, `slot_range` `{from, to}` (null for the generation and adoption journals), `previous_freeze_marker`, `export_markers` (list of sha256), `manifest_sha256`, `raw_files` (list of `{path, sha256, bytes}`, §15.3), `heads` |
| `export/capture-<A>/capture-manifest.json` | `wlscratch-capture-v1` | `attempt`, `census_pin` (U absent or `populated 0`), `entries` (list of `{rel_path, type, stat_key, atime_ns, acl_access, acl_default, xattrs, link_group, sha256, export_path, export_sha256, export_mode}`), `walk_before_sha256`, `walk_after_sha256`, `self_check` (`pass` or the differences), `state` ∈ {`complete`, `failed`} |
| `channel/<channel>-<first>-<last>.json` | `wlscratch-channel-segment-v2` | `channel`, `messages` (list of `{dir, seq, prev, kind, length, payload_sha256}` plus either `payload` or `ref`, where `ref` is `{record, offset, length, sha256}`, `{written, offset, length, sha256}` or `{source, offset, length, sha256}`, each resolving inside the exports, §7.3; `dir` includes `RL2W`) |
| `adoption-<I>/invocations/<stamp>/invocation.json` | `wlscratch-adopt-invocation-v1` | `created_at`, `writer` (B.1), `invocation`, `front_triple`, `lease`, `channel`, `installed` `{inventory_sha256, install_root, source_frame, setup_identities_sha256}` |
| `adoption-<I>/lead-adoption.json` | `wlscratch-lead-adoption-v2` (key set as v5 defines it plus the §23.4 Claude-review provenance keys; nothing is implemented) | every key of v5's `claude-scratch-frame-lead-adoption-v5` record (with `frame` = INSTALL_ROOT), plus `source_frame`, `setup_identities_sha256`, `setup_identities_file` `{bytes, dev, ino}` (the seal of §11.7), `installed_review` `{review_sha256, review_freeze_sha256, review_report_sha256, reviewer_thread, rollout, turn_contexts, session_providers, exec_argv, exec_argv_record, event_stream, rollout_final_message_sha256, rollout_final_timestamp}`, `invocation_pin`; and, for a Claude-subagent review (selected by `reviewer_kind`; §23.4, §23.5 item 7), the provenance keys `review_freeze_sha256`, `raw_final_message_sha256`, `reviewer_agent_id`, `reviewer_task_output_sha256`, `reviewer_kind`, `different_from_author` in place of the gpt-6.1-sol `rollout`/`reviewer_thread`/`turn_contexts`/`session_providers`/`exec_argv`/`exec_argv_record`/`event_stream`/`rollout_final_message_sha256`/`rollout_final_timestamp` keys (for a given review exactly one form's keys are present and non-null; the gpt-6.1-sol form is retained for a GPT-6.1 review) |

### B.4 Channel kinds (body key sets) and the states that permit them [corrections: W1-V7-C3-DATA, W1-V7-SYNC-PROVENANCE, W1-V6-C1-DATA, W1-V6-COMMIT-AMBIGUITY; v6: W1-V5-PROTOCOL-REFUSALS, W1-V5-REVOCATION-CONFINEMENT; v5: W1-PROTOCOL-FAILURE-STATES; v4: W1-GENERATION-PROTOCOL]

**B.4.1 Conventions.** Types: `hex64` and `hex32` are lowercase hex strings of that length; `desc` is
`{path: str, sha256: hex64, bytes: int, mode: int}` (v5's `pin` shape); `pin` is `{record: desc, marker: hex64}`;
`identity` is B.1; `participant` and `wait` are B.2. Every body has exactly the listed keys. A kind marked *carrier*
has the key `bulk` (list of str) and is followed immediately by one `BEGIN`/`CHUNK`/`END` sequence per listed name, in
that order (§7.3): `BEGIN` `{name: str, size: int, mode: int, sha256: hex64, chunks: int}`, with `chunks` = 0 exactly
when `size` = 0; `CHUNK` `{index: int, data_b64: str}`; `END` `{sha256: hex64}`. A kind marked *fds* is sent in one
`sendmsg` carrying exactly the listed descriptors as `SCM_RIGHTS` ancillary data, in the listed order; other ancillary
data, or none, is a channel failure.

**B.4.2 F↔W and F↔W2 kinds** (v5 changes: `EARLY_REFUSAL` is new; `TARGET_EXITED`, `MATERIALIZED`, `EXPORTED` and
`FINAL` have changed key sets; v6 change: `FINAL`'s `vault` may be `interrupted`; v8/v9 changes: `RECORD_COMMITTED`
carries the sync outcome and `FINAL` the provenance of §10.5; the dispatch input phase streams the process attributes).

| Kind | Direction | Body keys (types) |
|---|---|---|
| `W_HELLO` | W→F | `nonce` (hex64), `verb` (str: `adopt`, `materialize`, `dispatch`), `writer` (identity), `generation` (hex32 or null), `attempt` (str or null), `committed` (list of pin) |
| `W2_HELLO` | W2→F | `nonce` (hex64), `mode` (str: `seal`, `recover`), `writer` (identity), `generation` (hex32), `attempt` (str), `w2_dir` (str), `capability` (object: `front_triple`, `s3`, `front_parent`, `verified`), `attempt_writer_state` (str: `absent`, `reused`), `committed` (list of pin) |
| `EARLY_REFUSAL` | W→F, W2→F | `verb` (str: `adopt`, `materialize`, `dispatch`, `seal-front`), `stage` (str), `error` (object: v5 failure row), `generation` (hex32 or null), `attempt` (str or null), `committed` (list of pin), `refusal` (desc or null), `export` (object or null: `increment` int, `freeze_marker` hex64) |
| `HELLO_ACK` | F→W, F→W2 | `echo` (hex64), `front` (identity) |
| `REQUEST_INPUTS` | W→F | `phase` (str: `adoption`, `descriptors`, `overlay`, `base`, `dispatch`), `names` (list of str) |
| `INPUT` | F→W | carrier; `phase` (str), `name` (str), `class` (str: `pinned`, `joined`, `observation`), `bulk` (exactly `[name]`) |
| `PHASE_END` | F→W | `phase` (str), `names` (list of str, equal to the request's) |
| `PHASE_DONE` | W→F | `phase` (str), `committed` (list of pin) |
| `ADOPTION_RECORD` | W→F | carrier; `record` (pin), `bulk` (exactly `["lead-adoption.json"]`) |
| `STAGE_REQUEST` | W→F, W2→F | `stage` (str: `front-parent`, `vault`, `front-child`, `front-after`, `front-terminal`) |
| `STAGE_RESULT` | F→W, F→W2 | carrier; `stage` (str), `results_sha256` (hex64), `bulk` (exactly the stage record's name) |
| `CHALLENGE` | W→F | `challenge_kind` (str: `gate0`, `memory`), `number` (int), `challenge_sha256` (hex64), `expression` (str) |
| `ANSWER` | F→W | carrier; `challenge_kind` (str), `number` (int), `line_b64` (str), `bulk` (exactly the receipt record's name) |
| `RECORD_COMMITTED` | W→F, W2→F | `name` (str), `record` (desc), `marker` (hex64), `state` (str: `primary`, `retry`), `sync` (str: `ok`, `failed`), `errors` (list) |
| `RECORD_FALLBACK` | W→F, W2→F | `name` (str), `slot` (int), `value_sha256` (hex64), `value_bytes` (int), `truncated` (bool), `errors` (list) |
| `RECORD_UNKNOWN` | W→F, W2→F | `name` (str), `value_sha256` (hex64), `value_bytes` (int), `errors` (list) |
| `RESERVE_REQUEST` | W→F | `token` (hex32), `launch` (desc), `holder` (str), `candidate` (str) |
| `RESERVE_INTENT_REQ` | F→W | `token` (hex32), `prior` (desc), `lock_identity` (object: `dev`, `ino`, `nlink`), `request_sha256` (hex64) |
| `RESERVE_INTENT_COMMITTED` | W→F | `record` (desc), `marker` (hex64) |
| `RESERVE_INTENT_REFUSED` | W→F | `state` (str: `fallback`, `unknown`), `errors` (list) |
| `RESERVE_DONE` | F→W | `token` (hex32), `current` (desc or null), `error` (object or null) |
| `RESERVE_ABORT` | F→W | `token` (hex32), `reason` (str), `prior` (desc or null) |
| `RESERVE_COMMITTED` | W→F | `record` (desc or null), `marker` (hex64 or null), `state` (str: `primary`, `retry`, `fallback`, `unknown`) |
| `LAUNCH_INTENT_COMMITTED` | W→F | `record` (desc), `marker` (hex64) |
| `PROCEED_LAUNCH` | F→W | `intent` (desc) |
| `PING` | W→F | `nonce` (hex32) |
| `PONG` | F→W | `nonce` (hex32) |
| `PARTICIPANT` | W→F | `participant` |
| `TARGET_STARTED` | W→F | `participant` |
| `TARGET_EXITED` | W→F | `wait`, `started` (bool: `false` exactly when C reported a failed spawn call with `SPAWN_FAILED`, §9.3 C12) |
| `REFUSAL` | W→F, W2→F | `stage` (str), `error` (object: v5 failure row), `record` (desc or null) |
| `CONCLUSION` | W→F | `result` (desc or null), `result_state` (str), `classification` (pin or null), `verdict` (str: `known-terminal`, `live`, `unknown`), `target_started` (str: `true`, `false`, `unknown`), `streams_final` (bool), `capture` (str: `complete`, `failed`, `pending`), `success_before_release` (bool) |
| `RECOVERY_SCAN` | W2→F | `round` (int), `verdict` (str: `known-terminal`, `live`, `unknown`), `record` (pin or null), `live` (list of participant) |
| `RECOVERY_RESULT` | W2→F | `verdict` (str), `record` (pin or null), `target_started` (str) |
| `RELEASE_INTENT_REQ` | F→W, F→W2 | `token` (hex32), `prior` (desc), `classification` (pin or null) |
| `RELEASE_INTENT_RESULT` | W→F, W2→F | `state` (str: `primary`, `retry`, `fallback`, `unknown`), `record` (desc or null), `marker` (hex64 or null), `errors` (list) |
| `RELEASE_DONE` | F→W, F→W2 | `token` (hex32), `prior` (desc), `current` (desc or null), `reread` (str: `released`, `reserved`, `unreadable`), `error` (object or null) |
| `RELEASE_WITHHELD` | F→W, F→W2 | carrier; `token` (hex32 or null), `reason` (str), `bulk` (exactly `["release-facts.json"]`) |
| `RELEASE_NOT_OWNER` | F→W, F→W2 | `token` (hex32), `window` (desc or null) |
| `RELEASE_RECORD_RESULT` | W→F, W2→F | `name` (str: `window-release.json`, `release-failure.json`, `release-withheld.json`, `release-not-owner.json`), `state` (str: `primary`, `retry`, `fallback`, `unknown`), `record` (desc or null), `marker` (hex64 or null), `errors` (list) |
| `MATERIALIZED` | W→F | `generation` (pin), `materialization` (pin), `generation_export` (object or null: `manifest` desc, `freeze` desc, `freeze_marker` hex64; null when the generation export failed) |
| `ADOPTED` | W→F | `adoption` (pin) |
| `EXPORTED` | W→F, W2→F | `increment` (int), `state` (str: `frozen`, `failed`), `cut` (object or null: `journal` str, `seq` int, `sha256` hex64), `manifest` (desc or null), `freeze` (desc or null), `freeze_marker` (hex64 or null), `errors` (list) |
| `STOP` | F→W, F→W2 | `reason` (str) |
| `FINAL` | W→F, W2→F | `exit_status` (int), `success` (bool), `released` (bool or null), `durability` (str: `complete`, `UNKNOWN`), `unknown_records` (list of str), `fallback_records` (list of str), `provenance_not_observed` (list of objects: `name` str, `provenance` str), `exports` (list of objects: `increment` int, `freeze_marker` hex64), `capture` (str or null: `complete`, `failed`; null for a verb without a capture), `vault` (str or null: `ok`, `failed`, `interrupted` (a `STOP` in `materialize`'s `VAULT` before its result, B.4.4); null for a verb without a vault stage) |
| `BYE` | F→W, F→W2 | no key |

After `RELEASE_DONE`, the writer commits `window-release.json` when `reread` is `released` and `release-failure.json`
otherwise. A writer sends `RECORD_COMMITTED` only for a record that §10.2 calls committed, after the close marker that
confirms it is linked; `marker` is the digest of the record-bearing marker, and `sync` is `failed` when that close
marker's directory `fsync` or post-link join failed (§10.1).

**B.4.3 W↔L, W↔C, W↔O and W2↔O kinds** (v5 changes: `RL_IDENTITY` and `SPAWN_FAILED` are new; `L_REFUSAL`'s stages,
`OBSERVE_REQUEST` and `OBSERVATION` have changed; v6 changes: `L_REFUSAL` and `CHILD_REFUSAL` may be the helper's first
message, B.4.4; v7 changes: `RL_IDENTITY` is sent in every configuration; `LAUNCHER_START` precedes L's `exec` of C;
v8/v9 changes: `RL_IDENTITY`'s body is B.3's `wlscratch-rl-identity-v3`; `RECORDS` carries `launcher-rl-identity.json`,
the record descriptors and the journal head).

| Channel | Kind | Direction | Body keys (types) |
|---|---|---|---|
| W↔L, W↔O, W2↔O | `RL_IDENTITY` | RL→W, direction `RL2W` (§7.3) | the keys of `wlscratch-rl-identity-v3` after `channel` (B.3): `root_launcher` (identity, role `root-launcher`, taken immediately before its `exec`), `view_spec_sha256`, `scope`, `census`, `user_ns`, `idmap_ns`, `mnt_ns`, `net_ns`, `root`, `cwd`, `binds`, `run_path_mode`, `skeleton`, `mount_list`, `mountinfo`, `landlock`, `seccomp`, `helpers`, `scope_properties` |
| W↔L | `L_HELLO` | L→W | `nonce` (hex64), `launcher` (identity) |
| W↔L | `GO` | W→L | carrier; `echo` (hex64), `bulk` (exactly `["launch.json", "admission.json", "launcher-intent.json"]`) |
| W↔L | `FDS` | W→L | fds; `names` (exactly `["sp_c", "scope.stdout", "scope.stderr"]`) |
| W↔L | `LAUNCHER_START` | L→W | `participant` (L, about to `exec` C), `child_argv` (list of str) |
| W↔L | `L_REFUSAL` | L→W | `stage` (str: the name of the failed G4 or G6 check, `stop` or `exec`), `error` (object) |
| W↔L | `STOP` | W→L | `reason` (str) |
| W↔L | `BYE` | W→L | no key |
| W↔C | `C_HELLO` | C→W | `nonce` (hex64), `child` (identity) |
| W↔C | `RECORDS` | W→C | carrier; `echo` (hex64), `journal_head` (object: `seq` int, `sha256` hex64), `records` (list, in the order of `bulk`, of objects: `name` str, `sha256` hex64, `bytes` int, `marker` hex64; null `marker` only for `lead-module`, which is a pinned input, not a record), `bulk` (exactly `["launch.json", "admission.json", "reservation-intent.json", "reservation.json", "launcher-intent.json", "materialization.json", "lead-adoption.json", "launcher-rl-identity.json", "lead-module"]`) |
| W↔C | `STREAMS` | W→C | fds; `names` (exactly `["child.stdout", "child.stderr"]`) |
| W↔C | `CHILD_RECORD` | C→W | carrier; `name` (str: `child-wrapper.json`, `effective-limits.json`, `child-stage-child.json`), `bulk` (exactly `[name]`) |
| W↔C | `CHILD_STAGE_REQUEST` | C→W | `stage` (str: `child`) |
| W↔C | `CHILD_STAGE_RESULT` | W→C | carrier; `results_sha256` (hex64), `bulk` (exactly `["front-stage-child.json", "writer-half-child.json"]`) |
| W↔C | `SPAWN_REQUEST` | C→W | carrier; `admission_summary_sha256` (hex64), `bulk` (exactly `["child-admission-summary.json"]`) |
| W↔C | `SPAWN_OK` | W→C | `spawn_ok` (desc), `marker` (hex64) |
| W↔C | `CHILD_REFUSAL` | C→W | carrier; `before_spawn` (bool, always true), `bulk` (exactly `["child-refusal.json"]`) |
| W↔C | `CHILD_START` | C→W | carrier; `participant` (T), `bulk` (exactly `["child-start.json"]`) |
| W↔C | `SPAWN_FAILED` | C→W | carrier; `error` (object: the errno and the exception text of the failed spawn call), `bulk` (exactly `["child-wait.json"]`) |
| W↔C | `CHILD_WAIT` | C→W | carrier; `bulk` (exactly `["child-wait.json"]`) |
| W↔C | `CHILD_CLEANUP` | C→W | carrier; `bulk` (exactly `["child-cleanup.json"]`) |
| W↔C | `STOP` | W→C | `reason` (str) |
| W↔C | `C_DONE` | C→W | `exit_status` (int) |
| W↔O, W2↔O | `O_HELLO` | O→W | `nonce` (hex64), `observer` (identity) |
| W↔O, W2↔O | `OBSERVE_REQUEST` | W→O | `echo` (hex64 in the first request, null afterwards), `stage` (str: `parent`, `after`, `recover`), `round` (int or null), `participants` (list of participant), `walk` (bool), `report` (bool) |
| W↔O, W2↔O | `OBSERVATION` | O→W | carrier; `stage` (str), `round` (int or null), `bulk` (exactly the observation record's name) |
| W↔O, W2↔O | `REPORT_BYTES` | O→W | carrier; `present` (bool), `bulk` (`["gnatprove.out"]` if present, else empty) |
| W↔O, W2↔O | `O_BYE` | W→O | no key |
| W↔O, W2↔O | `O_DONE` | O→W | `exit_status` (int) |

**B.4.4 State machines.** Rules common to every machine: a state ends when the side that speaks first in the next
state sends that state's first message; where that first message is a record message, the record name the table gives
identifies it; a message valid neither in the current state nor as the first message of a permitted next state is a
channel failure (§7.4). A *record message* is `RECORD_COMMITTED`, `RECORD_FALLBACK` or `RECORD_UNKNOWN`; wherever a
row names a record, any of the three may report it, and in every F↔W and F↔W2 state after `START` the writer may also
send record messages for other records it commits in that state. F may send `STOP` in every F↔W and F↔W2 state after
`START`, in place of any message the row expects from F or between messages; W sends `STOP` to L and C only where
their rows say, and never to O. A `STOP` has exactly the effect that its row's STOP column gives, and nothing else:
where the column names `REFUSAL`, the writer finishes the step it is in (an observer it runs answers its current
request and receives `O_BYE`) and then sends `REFUSAL` and follows the verb's refusal path; where it says "recorded",
the writer records the `STOP` and the machine continues. Every F↔W and F↔W2 machine starts in `START`, whose only
messages are the writer's hello (to `HELLO`) and `EARLY_REFUSAL` (to `DONE`); F sends nothing before the hello. Every
helper machine starts in `HELLO`, where L and C may send `L_REFUSAL` and `CHILD_REFUSAL` as their first message.
`REFUSAL` is legal only where a row lists it, in its messages or in its STOP column. Clean EOF is permitted only in
`DONE`, and on W↔L also in `EXEC`. These machines, with these rules, are the complete set of legal sequences.

F↔W, verb `adopt`:

| State | Messages, in order | On `STOP` (F→W) | Next |
|---|---|---|---|
| `START` | `W_HELLO` (W→F) → `HELLO`; or `EARLY_REFUSAL` (W→F) → `DONE` | — (F sends nothing before the hello) | `HELLO` |
| `HELLO` | `HELLO_ACK` (F→W); then the next state's first message, or `REFUSAL` (W→F: F's identity fails §8.1's joins) → `EXPORT` | `REFUSAL` → `EXPORT` | `INPUTS` |
| `INPUTS` | `REQUEST_INPUTS` with phase `adoption` (W→F); one `INPUT` per requested name, in order (F→W); `PHASE_END` (F→W) | `REFUSAL` → `EXPORT` | `COMMIT` |
| `COMMIT` | `ADOPTED` (W→F) or `REFUSAL` (W→F: a join, the setup-identity seal or the commit of `lead-adoption.json` failed) | before `lead-adoption.json` is committed: `REFUSAL` → `EXPORT`; after it: recorded, and `ADOPTED` follows | `EXPORT` |
| `EXPORT` | `EXPORTED` (W→F; state `frozen` or `failed`) | recorded | `FINAL` |
| `FINAL` | `FINAL` (W→F); `BYE` (F→W) | recorded | `DONE` |

F↔W, verb `materialize`:

| State | Messages, in order | On `STOP` (F→W) | Next |
|---|---|---|---|
| `START` | `W_HELLO` → `HELLO`; or `EARLY_REFUSAL` → `DONE` | — | `HELLO` |
| `HELLO` | `HELLO_ACK`; then the record message for `front/front-identity.json` → `INPUTS_DESCRIPTORS`, or `REFUSAL` (F's identity fails the joins) → `EXPORT` | `REFUSAL` → `EXPORT` | `INPUTS_DESCRIPTORS` |
| `INPUTS_DESCRIPTORS`, `INPUTS_OVERLAY`, `INPUTS_BASE` | `REQUEST_INPUTS` with phase `descriptors`, `overlay` or `base`; one `INPUT` per name; `PHASE_END`; then `PHASE_DONE` → the next of these states, then `MATERIALIZE`; or `REFUSAL` in place of `PHASE_DONE` (an input failed its pin or verification; nothing from it was written) → `EXPORT` | `REFUSAL` → `EXPORT` (nothing of an unfinished input is written) | `MATERIALIZE` |
| `MATERIALIZE` | `MATERIALIZED` (W→F) → `VAULT`; or `REFUSAL` (W→F) → `EXPORT` | before `materialization.json` is committed: `REFUSAL` → `EXPORT`; after it: recorded, and `MATERIALIZED` follows | `VAULT` |
| `VAULT` | `STAGE_REQUEST` with stage `vault`; `STAGE_RESULT`; the record message for `front/front-stage-vault.json` (a failed vault result is recorded and reported in `FINAL.vault`; it does not refuse) | recorded, never a refusal: a `STOP` in place of `STAGE_RESULT` ends the stage without a result, and `FINAL.vault` is `interrupted` | `EXPORT` |
| `EXPORT` | `EXPORTED` | recorded | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | recorded | `DONE` |

F↔W, verb `dispatch` (refusal path RP0: nothing reserved, `REFUSAL` → `EXPORT`; refusal path RP1: reserved and
nothing launched, `REFUSAL` → `AFTER` → `CONCLUDE` → `RELEASE` → `EXPORT`):

| State | Messages, in order | On `STOP` (F→W) | Next |
|---|---|---|---|
| `START` | `W_HELLO` → `HELLO`; or `EARLY_REFUSAL` → `DONE` | — | `HELLO` |
| `HELLO` | `HELLO_ACK`; then the record message for `front/front-identity.json` → `INPUTS`, or `REFUSAL` (RP0) | `REFUSAL` (RP0) | `INPUTS` |
| `INPUTS` | `REQUEST_INPUTS` with phase `dispatch` and names `["lead-module", "process-attributes"]`; one `INPUT` per name; `PHASE_END`; then `PHASE_DONE` → `ADOPTION`, or `REFUSAL` in place of `PHASE_DONE` (RP0) | `REFUSAL` (RP0) | `ADOPTION` |
| `ADOPTION` | `ADOPTION_RECORD` (W→F) | `REFUSAL` (RP0) | `FRONT_PARENT` |
| `FRONT_PARENT` | `STAGE_REQUEST` with stage `front-parent`; `STAGE_RESULT`; the record message; then the next state's first message, or `REFUSAL` (RP0: F's half failed) | `REFUSAL` (RP0) | `PARENT` |
| `PARENT` | `PARTICIPANT` and record messages for the observer (W→F); then the next state's first message, or `REFUSAL` (RP0: a failed join, an original walk rule, an RL refusal, a failing or UNKNOWN census K or M, or RL's root scan) | `REFUSAL` (RP0) | `VAULT` |
| `VAULT` | `STAGE_REQUEST` with stage `vault`; `STAGE_RESULT`; the record message; then the next state's first message, or `REFUSAL` (RP0: v5's vault pin or status failed, J9) | `REFUSAL` (RP0) | `GATE0` |
| `GATE0` | `CHALLENGE` with kind `gate0`; `ANSWER`; the record message; or `REFUSAL` (RP0) | `REFUSAL` (RP0) | `LAUNCH_RECORD` |
| `LAUNCH_RECORD` | the record message for `launch.json`; `REFUSAL` (RP0) if it is not committed | `REFUSAL` (RP0) | `RESERVE` |
| `RESERVE` | `RESERVE_REQUEST` (W→F); then `RESERVE_ABORT` (F→W; `REFUSAL`, RP0) or `RESERVE_INTENT_REQ` (F→W); then `RESERVE_INTENT_COMMITTED` (W→F) or `RESERVE_INTENT_REFUSED` (W→F, after which F sends `RESERVE_ABORT`; RP0); then `RESERVE_DONE` (F→W: the window was written, or the write failed and the re-read shows this reservation or is unreadable) or `RESERVE_ABORT` (F→W: the write failed and the re-read shows no reservation; RP0); then `RESERVE_COMMITTED` (W→F) | F sends no `STOP` in this state: before its window write it sends `RESERVE_ABORT` with reason `stop` (`REFUSAL`, RP0); after it, F completes the state and sends `STOP` in `MEMORY_GATE` | `MEMORY_GATE` |
| `MEMORY_GATE` | per challenge, at most `MAX_CHALLENGES`: `CHALLENGE` with kind `memory`; `ANSWER`; `RECORD_COMMITTED`; on failure `REFUSAL` (RP1) | `REFUSAL` (RP1) | `ADMIT` |
| `ADMIT` | the record message for `admission.json`; `LAUNCH_INTENT_COMMITTED`; or `REFUSAL` (RP1) if either record is not committed | `REFUSAL` (RP1) | `PROCEED` |
| `PROCEED` | `PROCEED_LAUNCH` (F→W) → `RUNNING`; or `STOP` (F→W) → `REFUSAL` (RP1) | `REFUSAL` (RP1) | `RUNNING` |
| `RUNNING` | W→F: `PARTICIPANT` any number; `STAGE_REQUEST` with stage `front-child` at most once; `PING` at most once, after the front-child result; `TARGET_STARTED` at most once; `TARGET_EXITED` at most once (`started` true after `TARGET_STARTED`, false for a failed spawn call reported by `SPAWN_FAILED`, which sends no `TARGET_STARTED`); `REFUSAL` at most once (C refused before its spawn call, or the launch failed before C: RL or L refused). F→W: `STAGE_RESULT` with stage `front-child` exactly once after its request; `PONG` exactly once after `PING`; `STOP`. The state ends only when W has recorded the wait of every launch participant it started | forwarded down the channels (§9.2), and the machine continues | `AFTER` |
| `AFTER` | `STAGE_REQUEST` with stage `front-after`; `STAGE_RESULT`; `PARTICIPANT` and record messages for the observer, for stream finality and for the complete capture | recorded; a `STOP` in place of `STAGE_RESULT` ends F's half without a result, which the conclusion records | `CONCLUDE` |
| `CONCLUDE` | `CONCLUSION` (W→F) | recorded | `RELEASE` |
| `RELEASE` | F→W, exactly one of: (i) `RELEASE_INTENT_REQ`, later `RELEASE_DONE`; (ii) `RELEASE_WITHHELD`; (iii) `RELEASE_NOT_OWNER`. W→F: in (i), `RELEASE_INTENT_RESULT` exactly once, in answer to `RELEASE_INTENT_REQ`, then `RELEASE_RECORD_RESULT` exactly once, in answer to `RELEASE_DONE`; in (ii) and (iii), `RELEASE_RECORD_RESULT` exactly once. The two directions interleave freely: F sends `RELEASE_DONE` after its window write whether or not `RELEASE_INTENT_RESULT` has arrived, having waited for it until it arrived or EOF (§9.4), and a `RELEASE_INTENT_RESULT` that arrives after that is legal, recorded and changes nothing. The state ends when F has read `RELEASE_RECORD_RESULT` | recorded; F's release follows §9.4 only | `EXPORT` |
| `EXPORT` | the record message for `final-status.json`; `EXPORTED` | recorded | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | recorded | `DONE` |

F↔W2, verb `seal-front` (W2 never refuses because of a `STOP`):

| State | Messages, in order | On `STOP` (F→W2) | Next |
|---|---|---|---|
| `START` | `W2_HELLO` (W2→F) → `HELLO`; or `EARLY_REFUSAL` (W2→F: lease held, capability or seal failure; nothing written) → `DONE` | — | `HELLO` |
| `HELLO` | `HELLO_ACK` (F→W2); then the next state's first message (mode `seal`: `STAGE_REQUEST` of `FRONT_TERMINAL`; mode `recover`: `RECOVERY_SCAN` or `RECOVERY_RESULT` of `RECOVER`), or `REFUSAL` (W2→F: F's identity fails the joins) → `EXPORT` | recorded | `FRONT_TERMINAL` in mode `seal`; `RECOVER` in mode `recover` |
| `RECOVER` | `RECOVERY_SCAN` any number (W2→F); `STOP` (F→W2) ends the rounds; `RECOVERY_RESULT` exactly once (W2→F), after W2's observer has ended | ends the rounds: `RECOVERY_RESULT` carries the last verdict | `RELEASE` |
| `RELEASE` | as in `dispatch`, with W2 as the writer; F re-reads the window under the lock first and sends `RELEASE_NOT_OWNER` if this attempt does not hold it, which includes the case in which F already released it earlier in the attempt (F's terminal record then states `release.performed: true`) | recorded | `FRONT_TERMINAL` |
| `FRONT_TERMINAL` | `STAGE_REQUEST` with stage `front-terminal` (W2→F); `STAGE_RESULT` carrying `front-terminal.json` (F→W2); `RECORD_COMMITTED`, `RECORD_FALLBACK` or `RECORD_UNKNOWN` (W2→F), including the records of a complete capture W2 makes (§9.7) | recorded | `EXPORT` |
| `EXPORT` | `EXPORTED` | recorded | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | recorded | `DONE` |

W↔L:

| State | Messages, in order | On `STOP` (W→L) | Next |
|---|---|---|---|
| `HELLO` | first: `RL_IDENTITY` (RL→W, direction `RL2W`); then `L_HELLO` (L→W) → `GO`, or `L_REFUSAL` (L→W, as L's first message: a G4 check failed; nothing started) → `DONE` | W's check of RL's frame or of L failed: L exits 125 having started nothing → `DONE` | `GO` |
| `GO` | `GO` and `FDS` (W→L); then exactly one of: `LAUNCHER_START` (L→W: L is about to `exec` C) → `EXEC`; `L_REFUSAL` (L→W: a G6 check failed or a `STOP` was pending at its interruption point; nothing started) → `DONE` | pending at L's interruption point: `L_REFUSAL` (stage `stop`) → `DONE`; arriving after it: lost with SP_L at the `exec`, and W repeats it to C over W↔C | `EXEC` |
| `EXEC` | clean EOF (the `exec` succeeded and closed SP_L; L is now C) → `DONE`; or `L_REFUSAL` (L→W, stage `exec`: the `exec` failed; nothing started) → `DONE` | W sends none on SP_L; it stops C over W↔C | `DONE` |
| `DONE` | `BYE` (W→L) only after an `L_REFUSAL`; clean EOF | — | — |

W↔C:

| State | Messages, in order | On `STOP` (W→C) | Next |
|---|---|---|---|
| `HELLO` | `C_HELLO` (C→W) → `RECORDS`; or `CHILD_REFUSAL` (C→W, as C's first message: a C1 check failed; nothing spawned) → `REFUSED` | — (W sends nothing before C's first message) | `RECORDS` |
| `RECORDS` | `RECORDS` and `STREAMS` (W→C) → `ADMIT`; or `CHILD_REFUSAL` (C→W, after `RECORDS`: a C2 check failed, including its key set, order, digest or view-fact joins) → `REFUSED` | in place of `RECORDS` (W's verification of C failed, C2) or after it: C refuses (`CHILD_REFUSAL` → `REFUSED`) | `ADMIT` |
| `ADMIT` | C→W: `CHILD_RECORD` any number, `CHILD_STAGE_REQUEST` once; W→C: `CHILD_STAGE_RESULT` once after it; then C→W `SPAWN_REQUEST` → `SPAWN`, or `CHILD_REFUSAL` → `REFUSED` | C refuses (`CHILD_REFUSAL` → `REFUSED`) | `SPAWN` |
| `SPAWN` | W→C: `SPAWN_OK`, or `STOP` instead. After `SPAWN_OK`, exactly one C→W outcome: `CHILD_REFUSAL` (C refused before its spawn call: the final pass, the run-path alias check or a later check failed, or a `STOP` was pending at its interruption point) → `REFUSED`; `CHILD_START` (the spawn call returned T) → `RUNNING`; `SPAWN_FAILED` (the spawn call failed and C has no child) → `FAILED`. A spawn call that failed while a child exists ends C's messages: W sees a channel failure (B.4.5), and `target_started` stays `unknown` | in place of `SPAWN_OK`, or pending at C's interruption point: C refuses (`CHILD_REFUSAL` → `REFUSED`); read after the spawn call: in `RUNNING` forwarded to T as `SIGTERM`, in `FAILED` recorded | `RUNNING` |
| `RUNNING` | C→W `CHILD_WAIT` once, then `CHILD_CLEANUP` at most once, then `C_DONE` | C forwards `SIGTERM` to T | `DONE` |
| `FAILED` | C→W `CHILD_CLEANUP` at most once, then `C_DONE` | recorded | `DONE` |
| `REFUSED` | C→W `C_DONE` | recorded | `DONE` |
| `DONE` | clean EOF | — | — |

W↔O and W2↔O (W and W2 never send `STOP` to O; an observer is ended with `O_BYE` in `REQUEST`):

| State | Messages, in order | On `STOP` | Next |
|---|---|---|---|
| `HELLO` | first: `RL_IDENTITY` (RL→W, direction `RL2W`); then `O_HELLO` (O→W) | — | `REQUEST` |
| `REQUEST` | W→O `OBSERVE_REQUEST` → `RESULT`; or `O_BYE` → `DONE`. Every observer of W receives exactly one request; W2 may send one per recovery round | — | `RESULT` |
| `RESULT` | O→W `OBSERVATION`; then `REPORT_BYTES` if the request asked for it | — | `REQUEST` |
| `DONE` | O→W `O_DONE`; clean EOF | — | — |

**B.4.5 Channel failures** (any violation of §7.4 or of the machines above):

| Channel, side and moment | Action |
|---|---|
| F↔W at F, in `START` (EOF or a malformed first frame before any hello or `EARLY_REFUSAL`) | W refused or failed before its hello: nothing reserved; F cannot know whether `attempt.json` is committed, so it runs no W2 and keeps W's stderr and its own facts on its console |
| F↔W at W, before F's window write | `refusal.json` and the export increment if `attempt.json` is committed; exit non-zero; nothing reserved |
| F↔W at F, before F's window write | stop reading, close the pipe ends, wait for S1; W2 in mode `seal` if F knows `attempt.json` is committed; nothing to release |
| F↔W at W, after F's window write and before `PROCEED_LAUNCH` | refuse (no S2 is started), take the after-stage classification, commit the conclusion and `release-withheld.json` ("front channel failed; release left to the front's recovery or to manual resolution"), export, exit |
| F↔W at W, from `PROCEED_LAUNCH` on | continue the run and its waits (a front EOF never implies a refusal after launch), conclude, commit `release-withheld.json` as above, export, exit |
| F↔W at F, after F's window write, including EOF after `RELEASE_DONE` before a `RELEASE_RECORD_RESULT` | writer-death recovery (§9.7) |
| F↔W2 at W2 | commit what it has (recovery and release records) and its export increment, exit; if no release happened, the window stays held |
| F↔W2 at F | wait for S3; if no release happened and F wrote the window, start W2 in mode `recover` again (§9.7 RC2) until the lead stops F; otherwise the window stays held |
| W↔L at L | before its interruption point: exit 125, nothing started; after `LAUNCHER_START`: it `exec`s C, or exits 125 if the `exec` fails; C's rules then apply |
| W↔L at W, including a missing or second `RL_IDENTITY` | if `GO` was not sent, W sends none and closes SP_L (L sees EOF and exits 125 having started nothing) and refuses; otherwise W records the failure, whether a launch happened is decided by U's state and the classification, and if C appears, W stops it over W↔C |
| W↔C at C | before its interruption point: refuse without spawning, with the statement on its stderr; after a spawn call that returned T: keep waiting for T, write what it can to its stderr, exit; after a failed spawn call: write the failure to its stderr, wait for any child it has, exit, never stating that nothing started unless no child exists |
| W↔C at W | `target_started` stays `unknown` unless `CHILD_START`, `SPAWN_FAILED` or C's refusal arrived; the classification decides |
| W↔O or W2↔O at O | exit 125 |
| W↔O or W2↔O at W or W2, including a missing or second `RL_IDENTITY` | the observation fails: before launch the stage refuses; at a classification the verdict is `unknown` (§9.4) |

## Appendix C. JACKAL results used in this document

All calls through actual MCP `jackal_exact`; each returned status `exact`, `formal` false, lane `rat`, evaluator
sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, and the three non_claims quoted in §14. No
consequence ceiling field was returned. `parsed` is the tool's echo.

**C.1 v3's results, used as given** (computed for v3, recorded in `v3-support/jackal.json`, and reproduced with
status `exact` by the sealed gpt61-v3 review; not recomputed for v4):

| Use | parsed | exact | approx (tool display) |
|---|---|---|---|
| v5 frame member total | `13976+19614+922860+4986+5773785+3198141+26383551+4153+1974792+1467+5300+7869+4763+749+755+745+116891` | 38434397 | 38434397 |
| v5 frame review roster | `49133+602614+68556+250916+8543` | 979762 | 979762 |
| base descriptors | `1735+105491+1542` | 108768 | 108768 |
| recipe file-mode rows | `617+18` | 635 | 635 |
| A_idf | `2*3*25492333` | 152953998 | 152953998 |
| A_in, A_jrnl | `128*2^20` | 134217728 | 134217728 |
| A_fb, A_setuprec | `16*2^20` | 16777216 | 16777216 |
| A_tmp | `256*2^20` | 268435456 | 268435456 |
| A_selftest, MAX_FRAME | `64*2^20` | 67108864 | 67108864 |
| A_homes | `1*2^20` | 1048576 | 1048576 |
| A_install | `3*38434397` | 115303191 | 115303191 |
| A_exp, A_retry | `545393048+152953998+134217728` | 832564774 | 832564774 |
| X | `2*545393048+3*152953998+3*134217728+16777216` | 1969078490 | 1969078490 |
| X check | `152953998+134217728+545393048+152953998+134217728+545393048+152953998+134217728+16777216-1969078490` | 0 | 0 |
| W-1 dispatch addition | `2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` | 4340810164 | 4340810164 |
| Required, dispatch | `2*(16777216+2242440646+545393048)+1468268019712/1397+2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` | 15368462701360/1397 | 11001047030.322119 |
| addition check | `15368462701360/1397-9304350902252/1397-4340810164` | 0 | 0 |
| Required, setup | `2*(115303191+1048576+16777216)+134217728+1468268019712/1397` | 2027732564230/1397 | 1451490740.3221188 |
| Required, selftest | `2*67108864+134217728+1468268019712/1397` | 1843272351744/1397 | 1319450502.3221188 |
| historical margin, dispatch | `10460753920-10000000000-15368462701360/1397` | -14724789475120/1397 | -10540293110.322119 |
| historical margin, setup | `10460753920-10000000000-2027732564230/1397` | -1384059337990/1397 | -990736820.3221189 |
| historical margin, selftest | `10460753920-10000000000-1843272351744/1397` | -1199599125504/1397 | -858696582.3221189 |
| records payload with images | `545393048+1969078490` | 2514471538 | 2514471538 |
| ideal payload identity | `16777216+2242440646+545393048+1969078490+16777216+2242440646+545393048+1969078490+1468268019712/1397+268435456+134217728-15368462701360/1397` | 0 | 0 |
| CHUNK | `4*2^20` | 4194304 | 4194304 |
| frame headroom | `67108864-4*(4194304+2)/3` | 61516456 | 61516456 |
| fallback slots | `16*2^20/(64*2^10)` | 256 | 256 |
| slot size | `64*2^10` | 65536 | 65536 |
| new groups | `1+1+1` | 3 | 3 |
| new users | `1+1` | 2 | 2 |
| last id of `sicarii`'s subordinate range | `100000+65536-1` | 165535 | 165535 |

**C.2 v4's new results** (actual MCP calls made for v4 on 2026-10-05, recorded in `v4-support/jackal.json`):

| Use | parsed | exact | approx (tool display) |
|---|---|---|---|
| fallback slot header bytes (magic, index, length, sha256) | `8+4+4+32` | 48 | 48 |
| fallback slot payload capacity | `64*2^10-(8+4+4+32)` | 65488 | 65488 |
| last fallback slot index | `16*2^20/(64*2^10)-1` | 255 | 255 |
| minimum `st_blocks` of the fully allocated journal (512-byte units) | `16*2^20/512` | 32768 | 32768 |
| the gpt61-v3 review's W-1 required corrections, one per named id | `1+1+1+1+1+1` | 6 | 6 |
| the prior W-1 corrections it ruled on, one per named id | `1+1+1+1` | 4 | 4 |

Values used as given (observations, or results reproduced by a sealed review, not recomputed here):
9304350902252/1397 (v4.3 Required), the allowances of §14.1, 25492333 (O2 runtime closure), 10460753920 (free at
23:32:06Z), 10000000000 (reserve), the file sizes read from `frame-inventory.json`, `wc -c` and the inventory JSON,
the sizes of the gpt61-v3 review's gap tables (twelve section-3 gaps and twenty original subgaps, read from
`review.json`), and the host observations dated 2026-10-04 and 2026-10-05.

## Appendix D. v5 joins and where v4 performs them [corrections: W1-V6-C1-DATA; v4: W1-GENERATION-PROTOCOL]

Every admission, child, conclusion and adoption join of frame v5 (`scratch.py`, sha256 `f9f6596d…be86`) is kept. The
right column names the role and the state (Appendix B.4) in which W-1 v7 performs it. No join is dropped, narrowed or
replaced by a weaker one; where a join moves to another role, the role that has the needed authority performs it and
the result reaches the others over a channel.

| v5 join (source) | Where v7 performs it | Role, state |
|---|---|---|
| J1 `started_by_dispatch` (S:1520-1527): the run is the dispatch verb's child | W: `SUDO_*`, `HELLO_ACK` and the stdio inode join; W2: the front-process triple | W `HELLO`; W2 `HELLO` |
| J2 `open_run`: the run directory and the materialization record pin | W at D3: the committed generation and materialization markers and the P_adm identities | W, before `HELLO` |
| J3 `command(action, args, materialization)` | F at D1 (grammar), W at D3, C at C6 (re-derivation) | F; W; C `ADMIT` |
| J4 `fresh_lead('scratch-run')` | F at D7 | F `FRONT_PARENT` |
| J5 `admission(parent)`: `frame_admitted` (inventory, review profile, adoption profile, rollout re-join (the §23.4 join selected by `reviewer_kind`, §23), adoption observation) | F (the lead-context parts, D7) over the adoption bytes W delivers (D6); W (inventory, structural adoption joins, D3) | F `FRONT_PARENT`; W `ADOPTION` |
| J6 `verify_materialization` at the parent stage | O's walk in its view (D8) and W's writer half | W `PARENT` |
| J7 `identities(parent)` (tool, data, ELF, vendor, runtime, manager) | O inside its view against the original baselines (D8); F in the real context, which also takes the manager environment (D7) | `PARENT`; `FRONT_PARENT` |
| J8 `sample('preflight')` | F's front half (D7) and O's helper half (D8) | `FRONT_PARENT`; `PARENT` |
| J9 vault pin and status | F at D9 | `VAULT` |
| J10 `verify_location` of the held handles | W (D8, C4, C8, the conclusion) | W |
| J11 the seal: run, attempt, source and snapshot identities and `source_tree` | `launch.json` `directory_identities` (D11) | `LAUNCH_RECORD` |
| J12 the `launch.json` fields (frame inventory, review pin, adoption pin, materialization pin, reserve bound, holder, environment, argv and templates) | W at D11; the adoption pin is the protected record's descriptor | `LAUNCH_RECORD` |
| J13 `reserve`: released status; holder, candidate and token; the intent before the window write and `reservation.json` after it | F under the window lock, W committing the records (D12) | `RESERVE` |
| J14 `memory_gate` | W issues and verifies, F forwards (D13) | `MEMORY_GATE` |
| J15 `admission.json` binds the memory gate, the reservation and the launch | W at D14 | `ADMIT` |
| J16 `launcher-intent.json`: the scope argv is the template plus both seals | W at D14, plus the stream identities | `ADMIT` |
| J17 pending signals before the launcher spawn; `source.verify_location()` | W at G3 | `RUNNING` |
| K1 the launch bytes hash to the argv seal | RL (§12.2 step 4), L at G6 and C at C2 | W↔L `HELLO` (RL's frame), `GO`; W↔C `RECORDS` |
| K2 `/proc/self/cmdline` equals the sealed template plus the seals | C at C2, after `RECORDS`; C1 checks only its argv against the compiled grammar (correction W1-V6-C1-DATA) | W↔C `RECORDS` |
| K3 `reservation-intent.launch` equals the launch pin | C at C2 | W↔C `RECORDS` |
| K4 the admission bytes hash to their seal; `gate.launch` equals `intent.launch` | C at C2 | W↔C `RECORDS` |
| K5 run, attempt, source and snapshot identities equal the seal; `verify_location` | C at C3 (the view's `source/`) and W at C4 (attempt, snapshot) | W↔C `ADMIT` |
| K6 `fresh_lead('scratch-child')`; `holder` equals `LEAD_ID` equals `intent.holder_task` | F at C4 (the fresh observation), C at C5 (the holder join) | `RUNNING`; W↔C `ADMIT` |
| K7 `owns_window(LEAD_ID, attempt, token)` | F under the window lock at C4; C requires the result at C5 | `RUNNING`; W↔C `ADMIT` |
| K8 `admission(child)` with `frame_admitted`; observed identities equal `seal.source_tree` | F (frame admission front part at C4, over the adoption bytes); C (inventory check, identities `child`, admission walk, C5) | `RUNNING`; W↔C `ADMIT` |
| K9 the launch pins (frame inventory, review, adoption, materialization) equal the current ones | C at C6; the adoption pin against the delivered protected record | W↔C `ADMIT` |
| K10 the environment equals `launch.environment`; the observed environment minus `INVOCATION_ID` equals it; `INVOCATION_ID` is 32 hex | C at C1 (`INVOCATION_ID`'s form only), at C2 (the environment, after `RECORDS`) and at C6 | W↔C `HELLO`, `RECORDS`, `ADMIT` |
| K11 the parent memory gate; the final sample at or above the minimum; the reserve bound; siblings allow only U | C at C6, with F's front half of `child-final` (C4), whose sibling check of `sicarii`'s manager allows no unit, because U is the system manager's (§9.4) | W↔C `ADMIT` |
| K12 cwd; allowlist re-derivation | C at C6 | W↔C `ADMIT` |
| K13 effective limits (`memory.max`, `memory.swap.max`, core) and scope membership | C at C6 | W↔C `ADMIT` |
| K14 the target executable's identity | C at C6 | W↔C `ADMIT` |
| K15 `verify_materialization` again before the spawn | C at C10, with v6's leaf pass, in the view with `O_NOATIME` | W↔C `SPAWN` |
| K16 `verify_location`; pending signals before the spawn | C at C10 and C11 | W↔C `SPAWN` |
| K17 `child-refusal.json` ("nothing was started") only on the pre-spawn path | C (§9.3, C's refusals) | W↔C `ADMIT`, `SPAWN` |
| Q1 `owned_terminal` | O's after-stage observation of v5's predicate (§9.4); W2's recovery rounds (§9.7); F at the release point | `AFTER`; W2 `RECOVER`; `RELEASE` |
| Q2 `final_stream_sync` | W after terminal, followed by stream finality from U's `populated 0` | `AFTER` |
| Q3 the launch-gate records (launch, intent, reservation, admission, launcher intent, launcher start, launcher wait) equal their in-memory pins | W's attempt-journal join (§10.6) at the conclusion | `AFTER` |
| Q4 the held directories equal the seal; materialization unchanged; `verify_materialization`; no replaced or outside directories | W and O at the conclusion | `AFTER` |
| Q5 the report copy | O sends the bytes; W commits its copy | `AFTER` |
| Q6 the post identities with `frame_admitted` | F's after half (frame admission front part) and O's identities `after` | `AFTER` |
| Q7 child records read raw; unparseable bytes reported, never trusted | W, with §10.6's precedence | `AFTER` |
| Q8 the success conjunction; `result.json`; release only on terminal ownership and `owns_window`; `release-withheld.json`; `release-failure.json`; `conclude-errors.json`; exit 0 only on success and release | W's `result.json` and `final-status.json` (N13); F's release rule (§9.4; record durability is not a condition, by the supplied ruling); N14 | `CONCLUDE`, `RELEASE`, `FINAL` |
| P1 `dispatch`: action in `ACTIONS`; `command()`; answer forwarding; the actual run wait; the terminal record | F (D1; inbox answers over the channel); F's wait of S1; W2's front terminal record | F; W2 `FRONT_TERMINAL` |
| A1 `adopt`: "adoption already recorded" | W at AD3: `lead-adoption.json` present in any state refuses | W, before `HELLO` |
| A2 `adopt`: `review_profile_problems` (profile, candidate, lead id, inventory sha, report sha, sidecars) | F (AD2) and W (AD5) for the code review, with `candidate` = SOURCE_FRAME and member exactness (§4.6, join 3); the installed review added | F; W `COMMIT` |
| A3 `adopt`: `rollout_join` (the §23.4 join selected by `reviewer_kind`; for a Claude review the task-output/agent-id identity in place of the rollout-file uniqueness, §23) | F (AD2, including the uniqueness of the rollout file) and W (AD5, over the streamed bytes) for both reviews | F; W `COMMIT` |
| A4 `adopt`: the fresh `scratch-adopt` observation, `check_observation`, `validate_adoption_observation` | F (AD2); W re-checks the structural profile and the time ordering (AD5) | F; W `COMMIT` |
| A5 `adopt`: the create-only record with every v5 key | W at AD5 in P_ado(I); schema renamed `wlscratch-lead-adoption-v2` (§23.4, B.3), every v5 key kept | W `COMMIT` |
| A6 `frame_admitted`'s adoption checks at every use (schema, frame, lead id, mismatches, inventory sha, review pins, provenance re-pins, the §23.4 review-provenance re-join by `reviewer_kind`, adoption-observation re-validation) | F in every frame admission front part (D7, C4, D17), over the protected bytes from W; the schema check expects `wlscratch-lead-adoption-v2` | `FRONT_PARENT`; `RUNNING`; `AFTER` |

## Appendix E. v5's JACKAL results and dated passive observations

**E.1 JACKAL.** All calls through actual MCP `jackal_exact` on 2026-10-05; each returned status `exact`, `formal`
false, lane `rat`, evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, and the three
non_claims quoted in §14 ("NOT formal-bounded: this lane carries no Lean-checked certificate", "The epistemic class
above is the STRONGEST claim this result supports", "exact rational arithmetic (not yet checker-covered)"). No
consequence ceiling field was returned; the results are informational arithmetic only, and exact is not
formal-bounded. `parsed` is the tool's echo. Recorded in `v5-support/jackal.json`.

| Use | parsed | exact | approx (tool display) |
|---|---|---|---|
| the gpt61-v4 review's W-1 required corrections, one per named id | `1+1+1+1+1+1` | 6 | 6 |
| change-map partition check: carried + replaced + amended − v4 units | `69+21+16-106` | 0 | 0 |
| rows of the §18.5 change map: v4 units + new units | `106+3` | 109 | 109 |

One further call, parsed `69+33+4-106` (exact 0), checked an earlier draft partition of the change map that v5 does
not use; it is recorded in `v5-support/jackal.json` and relied on nowhere.

Values used as given (observed, not recomputed): the v4 unit count 106 and the status counts 69, 21 and 16, printed by
the read-only script that computed §18.5; the v4 sizes 321052 and 4566 bytes (`wc -c`); the counts of E.2, printed by
`grep -c`; every number carried from v3-support and v4-support (Appendix C); and the values the gpt61-v4 review
reproduced.

**E.2 Passive observations by the drafting author, 2026-10-05 (read-only; not setup evidence).**
- 06:24:47Z: `/proc/sys/kernel/io_uring_disabled` reads 0, so io_uring is available to every process; C9's and the S-F
  drop-in's io_uring rules are therefore needed.
- Installed manual sources, read with `zcat` (roff line numbers):
  - systemd.exec(5), `/usr/share/man/man5/systemd.exec.5.gz`: `RestrictSUIDSGID=` (roff 3498-3511) denies "any
    attempts to set the set-user-ID (SUID) or set-group-ID (SGID) bits on files or directories", is "implemented using
    seccomp filtering", and for calls whose mode bits are passed indirectly, "such as openat2()", "the call is blocked
    entirely"; the entry names no io_uring call. `NoNewPrivileges=` (roff 1235-1248) affects "the unit's processes
    themselves (or any processes directly or indirectly forked off them)" and has "no effect on processes potentially
    invoked on request of them through tools such as at(1), crontab(1), systemd-run(1), or arbitrary IPC services".
    `SystemCallFilter=` (roff 3634-3639): a denied call terminates the process with `SIGSYS` by default, and
    deny-listed calls "may optionally be suffixed with a colon (":") and an argument in the same format as
    SystemCallErrorNumber=".
  - systemd.unit(5), `/usr/share/man/man5/systemd.unit.5.gz`: roff 333-334, a unit file symlinked to `/dev/null`
    "appears with a load state of "masked", and cannot be activated"; roff 545-622, the user unit load path in priority
    order (`user.control`, `transient`, `generator.early`, `~/.config/systemd/user`, `$XDG_CONFIG_DIRS/systemd/user`,
    `/etc/systemd/user`, `$XDG_RUNTIME_DIR/systemd/user`, `/run/systemd/user`, `generator`,
    `~/.local/share/systemd/user`, `$XDG_DATA_DIRS/systemd/user`, `/usr/local/lib/systemd/user`,
    `/usr/lib/systemd/user`, `generator.late`).
  - systemd(1), `/usr/share/man/man1/systemd.1.gz`: roff 297, requests "are encapsulated as 'jobs' and maintained in a
    job queue"; roff 1596, "hardware, socket, bus or other kinds of activation might add additional jobs"; roff
    448-451, "systemd user managers will start the exit.target unit" on `SIGTERM`.
  - bash(1), `/usr/share/man/man1/bash.1.gz`: roff 614-618, "The return status of a pipeline is the exit status of the
    last command, unless the pipefail option is enabled"; roff 11411-11414, `-e` does not stop the shell for "any
    command in a pipeline but the last (subject to the state of the pipefail shell option)".
  - No getent(1) manual is installed (no `getent.1` below `/usr/share/man`); §11.5's `getent` statuses rest on §11.2's
    existing expectation (status 2 for an absent entry), not on a manual.
- 06:28:42Z: user unit load-path directories: `/etc/xdg/systemd/user` is a symbolic link to `../../systemd/user`;
  `/etc/systemd/user` and `/usr/lib/systemd/user` exist; `/run/systemd/user`, `/usr/local/share/systemd/user`,
  `/usr/share/systemd/user` and `/usr/local/lib/systemd/user` do not. `grep -c` counts 93 names in
  `/usr/lib/systemd/user` ending in `.service`, `.socket`, `.timer`, `.path`, `.mount`, `.automount` or `.swap`, and 10
  ending in `@.service` or `@.socket`; the only `.timer`, `.path`, `.mount`, `.automount` or `.swap` name there is
  `systemd-tmpfiles-clean.timer`. `/etc/xdg/autostart`, the input of `systemd-xdg-autostart-generator`, holds the
  desktop files `at-spi-dbus-bus`, `gnome-keyring-pkcs11`, `gnome-keyring-secrets`, `localsearch-3`,
  `org.fcitx.Fcitx5`, `org.gnome.SettingsDaemon.DiskUtilityNotify`, `print-applet`, `user-dirs-update-gtk` and
  `xdg-user-dirs`.
- 06:45:33Z: `readlink /usr/bin/sh /bin/sh` prints `bash` for both.
- Frame v5 `scratch.py` (sha256 `f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86`, equal to v4's
  citation): the only lines naming `vault` are `run`'s `project-vault pin` and `project-vault status` requirements
  (S:1562-1563) and the storage-script path (S:69); `materialize` runs no vault command.
- 07:00:32Z: `df -h /` shows 9.2G available, recorded for this drafting session only; it is not a Gate 0 reading.
## Appendix F. v6's JACKAL results and dated passive observations

**F.1 JACKAL.** All calls through actual MCP `jackal_exact` on 2026-10-05; each returned status `exact`, `formal`
false, lane `rat`, evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, and the three
non_claims quoted in E.1. No consequence ceiling field was returned; the results are informational arithmetic only,
and exact is not formal-bounded. `parsed` is the tool's echo. Recorded in `v6-support/jackal.json`.

| Use | parsed | exact | approx (tool display) |
|---|---|---|---|
| the gpt61-v5 review's W-1 required corrections, one per named id | `1+1+1+1+1+1` | 6 | 6 |
| change-map partition check: carried + amended + replaced − composed-v5 units | `70+29+16-115` | 0 | 0 |
| v6 units: composed-v5 units + new units | `115+3` | 118 | 118 |
| one per named item: the partition roots `obj`, `lib`, `resource-tests/obj` and `resource-tests/bin`, and so their fresh roots; the options (i)-(iv) of §9.8 K0 | `1+1+1+1` | 4 | 4 |
| one per named item: the new units §14.7, §21 and Appendix F; the rows §6.3 adds (`outputs/`, `outputs/<A>/`, the fresh and retired roots) | `1+1+1` | 3 | 3 |
| one per named item: the two routes; SCAN-GATE and SCAN-W; the two directories an exchange renames; the two steps of an account atom and the operator's two S-R actions; a copy beside its source (§14.7) | `1+1` | 2 | 2 |

The first three expressions were also evaluated earlier on 2026-10-05 in this drafting session, with the same
results; all six were evaluated for the record kept in `v6-support/jackal.json`.

Values used as given (observed, not recomputed): the composed-v5 unit count 115 and the status counts 70, 29 and 16,
printed by the read-only script that computed §18.5; the composed-v5 size of 466105 bytes and 4780 lines; the line
ranges, sizes and sha256 values of §18.5; the block size and free-space readings of F.2; every number carried from
v3-, v4- and v5-support (Appendices C and E); and the values the gpt61-v5 review states.

**F.2 Passive observations by the drafting author, 2026-10-05 (read-only; not setup evidence).**
- 08:43:48Z: the sha256 values of the gpt61-v5 review's `REVIEW.md`, `review.json`, `checks.json` and
  `review-freeze.json` and of the composed v5 equal those in the header (verified again, untimed, before §18 was
  written); `df -h /` showed 9.3G available.
- Frame v5 `scratch.py` (`f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86`), frame v6 `scratch.py`
  (`2255d6e14967d62aa9ce4c2b93b986340dd6840df9b659f9252e522546884c84`) and `frame-v6-PLAN.md`
  (`9a07534bdb0d2ca8413b2433f13def7c2629b0c615e48c7aba0572913ddfe1d9`) were read. `observe_tree` (S:495-567; v6
  scratch.py:495-576) refuses an entry that is neither a directory nor a regular file (S:554), a regular file with
  more than one link (S:531), an entry it cannot open, list or read, and an entry whose metadata changes; it compares
  no set-ID bit and no directory device (§0.2 item 1). It reads file contents only outside the partitions (S:538-544).
  Lines cited by §21: `spawn` (S:1508, `RLIMIT_CORE` at S:1515), the scope's `MemoryMax=8G` and `MemorySwapMax=0`
  (S:1570-1571), `sample()` (S:1156-1179), `owned_terminal` (S:1375-1415), the conclusion's directory checks
  (S:1684-1691) and `os.umask(0o077)` (S:1992).
- The composed v5 file has 4780 lines, 466105 bytes and 115 units (read-only script).
- 09:37:31Z: `stat -f /var/lib` shows block size 4096 and type ext2/ext3; `df -B1 /` shows 9877860352 bytes
  available.
- 10:07:53Z: `/etc/login.defs` line 305 reads `USERGROUPS_ENAB yes`; §11.4 treats an account's user-private group as a
  co-object of the account's reversal (W_j).
- 10:43:14Z: `stat -f /` shows block size 4096 (fundamental block size 4096) and type ext2/ext3; `df -B1 /` shows
  9849405440 bytes available and `df -h /` 9.2G, recorded for this drafting session only; neither is a Gate 0
  reading.
## Appendix G. v7's JACKAL results and dated passive observations

**G.1 JACKAL.** All calls through actual MCP `jackal_exact` on 2026-10-05; each returned status `exact`, `formal`
false, lane `rat`, evaluator sha256 `4c0ae28d2f41353332dbb29f1b6084cd275d08bad73a84942fbe6f500255d872`, and the three
non_claims quoted in E.1. No consequence ceiling field was returned; the results are informational arithmetic only,
and exact is not formal-bounded. `parsed` is the tool's echo. Recorded in `v7-support/jackal.json`.

| Use | parsed | exact | approx (tool display) |
|---|---|---|---|
| Required, the `adopt`, `materialize` and dispatch stages, with A_pack (§14.3) | `15368462701360/1397+2*16777216` | 15415338242864/1397 | 11034601462.322119 |
| W-1 dispatch addition with A_pack | `2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728+2*16777216` | 4374364596 | 4374364596 |
| addition check | `15368462701360/1397+2*16777216-9304350902252/1397-4374364596` | 0 | 0 |
| work payload with images (A_mat + A_obj + A_tmp) | `16777216+2242440646+268435456` | 2527653318 | 2527653318 |
| records payload with images (A_rec + X + A_pack) | `545393048+1969078490+16777216` | 2531248754 | 2531248754 |
| v7 ideal payload identity | `16777216+2242440646+268435456+545393048+1969078490+16777216+16777216+2242440646+545393048+1969078490+16777216+1468268019712/1397+134217728-15415338242864/1397` | 0 | 0 |
| the gpt61-v6 review's required W-1 changes, one per named id | `1+1+1+1+1+1+1+1+1+1+1` | 11 | 11 |
| change-map partition check: carried + amended + replaced − v6 units | `29+63+26-118` | 0 | 0 |
| v7 units: v6 units + new units | `118+6` | 124 | 124 |
| one per named item: the changes V1-V12 of §12.3, which §0.4 also names | `1+1+1+1+1+1+1+1+1+1+1+1` | 12 | 12 |
| one per named item: the new units (§22, its four subsections, Appendix G) | `1+1+1+1+1+1` | 6 | 6 |
| one per named item: the subsections of §22 | `1+1+1+1` | 4 | 4 |
| one per named item: the OPEN read routes R-d, R-f and R-h (§9.8 N6) | `1+1+1` | 3 | 3 |
| octal 0700 in decimal (the `TMPDIR` baseline mode 448, §8.4) | `7*8^2` | 448 | 448 |
| octal 01777 in decimal (the `/tmp` and `/var/tmp` baseline mode 1023) | `1*8^3+7*8^2+7*8+7` | 1023 | 1023 |
| octal 0755 in decimal (the F10K source baseline mode 493) | `7*8^2+5*8+5` | 493 | 493 |
| one per named item: v5's allowlisted actions (`prove-all-k`, `prove-all`, `prove-file`, `prove-subp`, `compile-all`; S:88), §22.4 | `1+1+1+1+1` | 5 | 5 |
| U_v's map bounds (§12.2 step 10): the id below W | `950-1` | 949 | 949 |
| the id above GATE | `952+1` | 953 | 953 |
| the id below `sicarii`'s 1000 | `1000-1` | 999 | 999 |
| the id above `sicarii`'s 1000 | `1000+1` | 1001 | 1001 |

Values used as given (observed, not recomputed): the v6 unit count 118, its 4792 lines and 501735 bytes, and the
line ranges, sizes and sha256 values of §18.5, printed by the read-only script; the count of 29 byte-identical units,
printed by the same script, and the split of the remaining units into 63 amended and 26 replaced, which is the
author's labelling of §18.5; the allowances of §14.1 and §14.2 and v6's reviewed expression, carried; the
observations of G.2; every number carried from v3- to v6-support (Appendices C, E and F).

**G.2 Passive observations by the drafting author, 2026-10-05 (read-only; not setup evidence).**
- 11:57:18Z: the sha256 values of the gpt61-v6 review's `REVIEW.md` (596 lines, 108076 bytes), `review.json` (202672
  bytes), `checks.json` and `review-freeze.json`, of v6 and of `v6-support/jackal.json` equal those in the header and
  in the lead's instruction.
- 12:04:32Z: kernel release `7.2.6-1-aarch64-ARCH`; `/sys/kernel/security/lsm` reads `capability,yama,landlock`;
  `user.max_user_namespaces`, `max_pid_namespaces`, `max_net_namespaces`, `max_mnt_namespaces` and
  `max_ipc_namespaces` 128053 each; `kernel.yama.ptrace_scope` 1; `kernel.unprivileged_bpf_disabled` 2;
  `fs.protected_hardlinks` 1; `fs.leases-enable` 1; `kernel.io_uring_disabled` 0; `fs.suid_dumpable` 2; no
  `kernel.unprivileged_userns_clone` and no `kernel.apparmor_restrict_unprivileged_userns` sysctl. About 12:04Z
  (untimed command): `/usr/include/linux/landlock.h` defines `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` (bit 16, "available
  since the ninth version of the Landlock ABI", and for UNIX sockets restricting `connect` and `sendmsg` with an
  explicit recipient address to servers created inside the domain), `LANDLOCK_ACCESS_FS_MAKE_SOCK`,
  `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET` and `LANDLOCK_SCOPE_SIGNAL`, and describes network rights up to ABI 10;
  `pacman -Qi` shows `linux-api-headers` 7.2-1 and `linux-aarch64` 7.2.6-1.
- 12:12:23Z: no manual page for `landlock`, the namespace pages, `unix`, `cgroups`, `capabilities`, `fanotify`,
  `mount_setattr`, `open_tree`, `link`, `ptrace`, `pidfd_getfd`, `seccomp`, `open`, `execve`, `proc`, `core`,
  `clone3`, `unshare`, `rename`, `prctl` or `credentials` is installed below `/usr/share/man`; 12:55:31Z: `man -w`
  finds none of `landlock`, `landlock_create_ruleset`, `landlock_restrict_self`, `open_by_handle_at`, `mount_setattr`,
  `user_namespaces`, `mount_namespaces` or `pidfd_getfd`. The kernel statements of §9.8 and §22 are therefore the
  author's reading of upstream documentation and are stated as premises.
- About 12:12Z (untimed command): the kernel build configuration
  `/usr/lib/modules/7.2.6-1-aarch64-ARCH/build/.config` sets `CONFIG_USER_NS`, `CONFIG_PID_NS`, `CONFIG_NET_NS`,
  `CONFIG_IPC_NS`, `CONFIG_CGROUPS`, `CONFIG_MEMCG`, `CONFIG_SECURITY_LANDLOCK`, `CONFIG_SECURITY_YAMA`,
  `CONFIG_FANOTIFY_ACCESS_PERMISSIONS`, `CONFIG_SECCOMP_FILTER`, `CONFIG_CHECKPOINT_RESTORE`, `CONFIG_IO_URING`,
  `CONFIG_ANDROID_BINDER_IPC`, `CONFIG_ANDROID_BINDERFS`, `CONFIG_FS_POSIX_ACL`, `CONFIG_TMPFS` and `CONFIG_EXT4_FS`
  (each `y`), `CONFIG_FUSE_FS` and `CONFIG_OVERLAY_FS` (`m`), and does not set `CONFIG_BPF_LSM`,
  `CONFIG_SECURITY_SELINUX` or `CONFIG_SECURITY_APPARMOR`.
- 12:27:33Z: mounts `/` (ID 32, ext4 on `/dev/vda`, `relatime`), `/proc` (27), `/sys` (28), `/dev` (29), `/run` (30),
  `/dev/shm` (34), `/sys/fs/cgroup` (36, cgroup2) and `/run/user/1000` (282); `systemd 261 (261.3-1-arch)`;
  `cgroup.controllers` `cpuset cpu io memory hugetlb pids rdma`; the slices `system.slice` and `user.slice`.
- 12:30:14Z: `/usr/lib/tmpfiles.d/tmp.conf` holds `q /tmp 1777 root root 10d` and `q /var/tmp 1777 root root 30d`;
  `/etc/tmpfiles.d` is empty; `/tmp` and `/var/tmp` are `drwxrwxrwt` root root.
- About 12:31Z (untimed command): `<RUNS>` (`…/work/claude-scratch-runs-v5`) does not exist.
- About 12:40Z (untimed command; the frame files read again, untimed, before 12:45:11Z):
  `/home/sicarii/.cache/workflow-tmp` exists as `drwx------` owned by `sicarii`; frame v5's runtime-closure
  specification sets
  `TMPDIR=/home/sicarii/.cache/workflow-tmp` and lists it, the F10K source, `/tmp`, `/usr/tmp` and `/var/tmp` as
  `mutable_directory_identities`; its baseline rows are `TMPDIR` uid 1000, gid 1000, mode 448; `/tmp` and `/var/tmp`
  uid 0, gid 0, mode 1023; `/usr/tmp` absent; the F10K source uid 1000, gid 1000, mode 493 (G.1 gives the octal
  forms); the tool specification's `effective_environment` holds the values §8.4 cites. Read untimed between 12:45Z
  and 13:02Z: `KEEP_ENVIRONMENT` is `HOME`, `USER`, `LOGNAME`, `LANG` (S:86); v5's scope unit is
  `claude-worldline-scratch-<name>-<stamp>.scope` (S:1564); `owned_terminal` (S:1373-1415) and `sample` (S:1156-1179)
  read as §9.4 and §21 cite them.
- 12:51:34Z: the drafting session's own process has uid 1000, gid 1000 and the groups 1000 (`sicarii`), 954
  (`worldline-clients`), 955 (`wldrill-clients`), 956 (`wlrehearsal-clients`), 982 (`users`), 983 (`video`), 992
  (`input`), 995 (`audio`) and 998 (`wheel`); `/proc/config.gz` agrees with the build configuration above and does not
  set `CONFIG_USERFAULTFD`.
- 12:51:48Z: `/proc/config.gz` sets `CONFIG_ANDROID_BINDER_DEVICES="binder,hwbinder,vndbinder"`, `CONFIG_FHANDLE`,
  `CONFIG_SYSVIPC`, `CONFIG_POSIX_MQUEUE` and `CONFIG_BPF_UNPRIV_DEFAULT_OFF`; `/dev/binder`, `/dev/hwbinder`,
  `/dev/vndbinder` and `/dev/binderfs` do not exist; `kernel.io_uring_group` is -1.
- 12:59:28Z: the mount list from `/proc/self/mountinfo` (read without touching any mount; lines below
  `/home/sicarii/iPad` were filtered out unread): besides the mounts above, the `/sys` submounts (33, 36, 37, 38, 42,
  43, 46, 47), `/dev/pts` (35), `/dev/mqueue` (44), `/dev/hugepages` (45), `/proc/sys/fs/binfmt_misc` (39 autofs, 928),
  `/run/credentials/*` (40, 51, 384), `/srv/worldline` (55, ext4, `nosuid,nodev`), `/mnt/mac` (265, 9p),
  `/run/user/1002`, `/run/user/1001` and `/run/user/1004` (383, 395, 407), `/run/user/1000/doc` (541, fuse.portal) and
  `/run/user/1000/gvfs` (587, fuse.gvfsd-fuse); `/` is mounted without `nosuid`; `/run`, `/dev/shm`, `/dev/pts`,
  `/dev/mqueue` and the `/run/user/*` mounts are `nosuid`; `/run/lock` is 0755 root, `/run/user/1000` 0700 `sicarii`,
  and `/dev/shm`, `/dev/mqueue`, `/tmp` and `/var/tmp` 01777 root.
- 13:02:24Z: no entry of the pinned base `…/reviewed-common-proof-source-composition-v4/source` has an owner or group
  other than `sicarii`, and no entry of `/home/sicarii/opt/gnat` has an owner other than `sicarii`.
- 13:16:18Z: `systemd-tmpfiles-clean.timer` `ActiveState=active`, `UnitFileState=static`; `cgroup.subtree_control` of
  `/sys/fs/cgroup` and of `system.slice` is `cpuset cpu io memory pids`.
- 13:16:27Z: `systemctl show wlscratch.slice` reports `LoadState=loaded`, `ActiveState=inactive`, and empty
  `FragmentPath` and `DropInPaths`; an unused arbitrary slice name shows the same `LoadState` and an empty
  `FragmentPath`.
- 13:39:04Z: the pinned toolchain's `libexec/spark/bin` holds, among others, `why3server`, `spark_memcached_wrapper`,
  `spark_semaphore_wrapper`, `alt-ergo`, `cvc5` and `z3`; `strings` of its `bin/gnatprove` contains `--socket`,
  `why3server`, `GNATPROVE_SOCKET`, `why3server_` and `configuration__compute_socket_dir__exists_and_is_writable`.
- 13:51:44Z: `/usr/include/linux/mount.h` defines `MOUNT_ATTR_NOSUID` and `MOUNT_ATTR_IDMAP`; `df -B1 /` shows
  9744343040 bytes available, recorded for this drafting session only; it is not a Gate 0 reading.

## Appendix H. v8's JACKAL results and dated passive observations

**JACKAL.** Every derived numeral of v8 was computed with actual MCP `jackal_exact`, one call at a time, on
2026-10-05; each returned status `exact`, `formal` false, lane `rat`, assurance "exact rational arithmetic (not yet
checker-covered)", and the non_claims "NOT formal-bounded: this lane carries no Lean-checked certificate", "The
epistemic class above is the STRONGEST claim this result supports", "exact rational arithmetic (not yet
checker-covered)"; no consequence ceiling field was returned (informational arithmetic only; exact is not
formal-bounded). The complete results are in `v8-support/jackal.json`.

| Id | parsed | exact | Used in |
|---|---|---|---|
| J1 | `2^32-1` | 4294967295 | §12.2 step 10, §9.3 G3 |
| J2 | `25769803776/2^30` | 24 | §8.3, §12.3 V10' |
| J3 | `17179869184/2^30` | 16 | §8.3, §12.3 V10' |
| J4 | `21474836480/2^30` | 20 | §8.3, §12.3 V10' |
| J5 | `4294967295-1` | 4294967294 | §12.2 step 10 |
| J6 | `16777216+2242440646+268435456+545393048+832564774+16777216` | 3922388356 | §14.2 A_capture |
| J7 | `15415338242864/1397+2*(16777216+2242440646+268435456+545393048+832564774+16777216)` | 26374491309528/1397 (approx 18879378174.32212) | §14.3 |
| J8 | `26374491309528/1397-15415338242864/1397-2*3922388356` | 0 | §14.3 |
| J9 | `2*3922388356` | 7844776712 | the dispatch-stage addition of §14.3 |

| J10 | `1+1+1+1+1+1+1+1+1+1+1` | 11 | §18.1 (the eleven required changes) |
| J11 | `45+41+38-124` | 0 | §18.5 |
| J12 | `124+7` | 131 | §18.5 |

**Dated passive observations by the drafting author** (2026-10-05, UTC; read-only; nothing was executed but reading,
hashing and listing):
- 15:20:38Z: the review's four hashes and v7's hash verified; free space on the filesystem holding `wt-1`: 8819634176
  bytes available. 15:26:56Z: the same hashes re-verified; 9209733120 bytes available. (The lead reported 19667271680
  bytes at 15:50Z; that is the lead's observation, recorded as reported.)
- 15:22:14Z: `/usr/lib/modules/7.2.6-1-aarch64-ARCH/build` lists `include/`, `security/` (with `Kconfig` and
  `landlock/Kconfig` only), `vmlinux` and no `commoncap.c`; the installed `include/linux/ptrace.h` defines
  `PTRACE_MODE_READ` 0x01, `ATTACH` 0x02, `NOAUDIT` 0x04, `FSCREDS` 0x08, `REALCREDS` 0x10 and declares
  `ptrace_may_access`; `include/linux/lsm_hook_defs.h` declares the `ptrace_access_check` hook.
- About 15:23Z-15:30Z: upstream Linux v7.2 `security/commoncap.c` (`cap_capable_helper`, `cap_capable`,
  `cap_ptrace_access_check`), `kernel/ptrace.c` (`ptrace_has_cap`, `__ptrace_may_access`, the `ptrace_attach` call),
  `kernel/pid.c` (`__pidfd_fget`, `pidfd_getfd`), `fs/proc/fd.c` (`proc_fd_permission`, `proc_fd_link`,
  `proc_fdinfo_permission`) and `fs/proc/base.c` (`call_proc_get_link`, `proc_pid_get_link`, `proc_pid_readlink`, the
  `ptrace_may_access` and `checkpoint_restore_ns_capable` call sites) read through a web fetch of
  `raw.githubusercontent.com/torvalds/linux/v7.2/…`. Upstream, not the installed build (P-KSRC).
- 15:51:35Z: v7's 124 units with their line ranges, sizes and sha256 (§18.5), by a read-only script.
- 15:51:39Z: installed `/usr/include/linux/landlock.h` text for `RESOLVE_UNIX` (lines 313-326), `MAKE_SOCK` (line 354)
  and `REFER` (lines 359-389); `linux/nsfs.h` defines `NS_GET_PARENT` (line 13), `NS_GET_OWNER_UID` (line 18) and
  `NS_GET_MNTNS_ID` (line 44); `linux/stat.h` `STATX_MNT_ID_UNIQUE` (line 218); `linux/mount.h` `struct statmount`
  (line 157), `STATMOUNT_MNT_NS_ID` (line 224), `LSMT_ROOT` (line 237).
- 15:51:43Z: cgroup2 below `user.slice/user-1000.slice`: `user-1000.slice` `memory.max` max, `memory.swap.max` max,
  `memory.high` max, `pids.max` 84514, `cpu.weight` 100, `cpu.max` `max 100000`; `user@1000.service` the same except
  `pids.max` max; `user@1000.service/app.slice` `memory.max` 25769803776, `memory.swap.max` 17179869184, `memory.high`
  21474836480, `pids.max` max, `cpu.weight` 100; no `io.weight` file at any of the three; owners: `user-1000.slice`
  directory and its `cgroup.procs` root, `user.slice/cgroup.procs` root, `user@1000.service/cgroup.procs` `sicarii`.
- 15:54:09Z: installed `sudoers(5)` text for `log_allowed` (quoted in §9.8 N5) and four mentions of `pam_session`;
  installed `systemd.exec(5)` text for `LogLevelMax=` (quoted in §9.8 N5).
- Frame v5 `scratch.py`: `materialize` at S:959, `runs_parent` at S:977, "run already exists" at S:985, `command()` at
  S:1054-1070, `spawn` at S:1508-1517, the vault calls at S:1562-1563, `os.umask(0o077)` at S:1992.
## Appendix I. v11's JACKAL results and inputs (replaces v9's Appendix I for v11)

**JACKAL.** Every derived numeral of v11 was computed with actual MCP `jackal_exact` on 2026-10-05, sequentially or in
groups of at most four; each returned status `exact`, `formal` false, lane `rat`, assurance "exact rational arithmetic
(not yet checker-covered)", and the non_claims "NOT formal-bounded: this lane carries no Lean-checked certificate",
"The epistemic class above is the STRONGEST claim this result supports", "exact rational arithmetic (not yet
checker-covered)"; no consequence-ceiling field was returned (informational arithmetic only; exact is not
formal-bounded). The complete records are in `v11-support/jackal.json`. Numbers v11 carries unchanged from v9 (the
reachable-set/unit arithmetic v11 does not change, the identity-map line, the `app.slice` limits, A_capture, the
Required) are carried with their v9/v8 records; the ENUM-USERDEL counts (I1′, I2′) are v10's, re-derived here.

| Id | parsed (the tool's echo; grouping parentheses are flattened) | exact | Used in |
|---|---|---|---|
| I1′ | `4+5+3+2+2+1+1+1+1+7+10+4+6+3+3+4+0+0+2+1+1+1+1+1+1+1+1` | 67 | §11.4, reachable set without images (W1-V9-ENUM-USERDEL) |
| I1″ | `63+4` | 67 | §11.4, cross-check (v9's 63 plus X1,X2,X3,X4=W_B) |
| I2′ | `4+5+3+2+2+1+1+1-2+13+1+7+10+4+6+3+3-4+26+4+0+0+2+1+1+4+1+1+1+1+1+1` | 104 | §11.4, reachable set with images |
| I2″ | `100+4` | 104 | §11.4, cross-check with images |
| I3′ | `1+1+1+1+1+1+1+1+1` | 9 | §0.7, the nine v9-review required changes |
| I4′ | `100+23+9+2` | 134 | W1-V10-COUNT, the v10 change-map partition corrected (CARRIED+AMENDED+COMPOSED+SUPERSEDED) |
| I4″ | `23+9` | 32 | W1-V10-COUNT, v10 units changed (AMENDED + COMPOSED) |
| I5′ | `100+23+11` | 134 | §18.5 / V11-C.2, the **v11** partition of v9's 134 units (CARRIED+AMENDED+COMPOSED; the 2 formerly-SUPERSEDED units are materialized as COMPOSED) |
| I5″ | `23+11` | 34 | §18.5 / V11-C.2, v9 units v11 changes (AMENDED + COMPOSED) |
| I6′ | `100+23+11+2` | 136 | §18.5 / V11-C.2, total v11 spec units (v9's 134 plus the 2 NEW §0.7 and §23) |

**Inputs read for v11** (read-only; 2026-10-05): the sealed v10 review `wt-1/proposal/v10-review/claude-v1`
(`REVIEW.md` and `review.json` in full); v10 (for the COMPOSED units' bytes) and v9 (for the carried/amended unit
bytes and the §18.5 identities); `STATUS.md`; `…/outputs/claude-phase1-handoff-20261004/HANDOFF.md:173` and
`/home/sicarii/Documents/complete-phase1-prompt.txt:60` (§23). v11 did **not** re-fetch kernel, systemd or sudo
source; where it relies on installed-build or upstream readings it relies on v9's dated observations (v9 Appendix I,
carried) under premise P-KSRC, and §13.2 S-1 binds the running kernel image and build-id to the package before any
installed use. **Nothing was executed for v11 but reading, read-only hashing (the §0.1 / §18.5 unit-identity script)
and JACKAL calls; no probe, selftest, namespace, mount, seccomp filter, sudo, setup, vault or window action was
performed.** The §18.5 / Part V11-MAP line ranges, byte counts and sha256 are observations of this file produced by
the read-only script, not derived arithmetic.

**Dated passive observations.** v11 adds no new installed-build or upstream observations of its own; the observations
on which the design relies are v9's (carried in Appendices E–I of v9, 2026-10-05), under P-KSRC. The §5.4
subordinate-id inventory, the §2.3 kernel settings and the §6.1 recipe-mode facts are v9's observations, unchanged.

---

# Part V11-MAP — the §18.5 change map (placed last so line ranges cover the assembled file)

## V11-C.1 Method

Every v9 unit is one of: **CARRIED** (v11 bytes equal v9's, emitted verbatim; the v11 sha256 equals the v9 sha256, so
byte-identity is checkable from the two files); **AMENDED** (v11 bytes are v9's with the Part-inline edits applied
under the normalization rule of §0.1; a new v11 sha256); **COMPOSED** (v11 bytes are v10's composed bytes, updated
only for v11's three fixes, or freshly authored; a new v11 sha256). Two units (§0.7, §23) are **NEW** (no v9
counterpart). The table gives, for each unit, its v9 identity (from v9 §18.5, verified by the independent v9 and v10
reviewers) and, for every unit, its computed v11 line range, byte count and sha256 over the assembled file (the
read-only script of Appendix I). This map unit and Appendix I are themselves computed over the final file and cannot
contain their own post-assembly identity; their final identities are recorded in `v11-support/jackal.json`.

## V11-C.2 Counts (JACKAL exact; Appendix I)

**W1-V10-COUNT (the v10 partition corrected).** v10's §V10-C.2 and `v10-support/jackal.json` stated 101 CARRIED / 22
AMENDED / "changes 31"; the actual v10 change map was **100 CARRIED, 23 AMENDED, 9 COMPOSED, 2 SUPERSEDED**
(`100+23+9+2` = 134, I4′) with **23+9 = 32** changed units (I4″). The 23 AMENDED units are exactly
2.2, 2.3, 4.2, 4.6, 5.3, 6.1, 8.1, 8.6, 9.1, 9.3, 9.8, 10.6, 11.3, 11.4, 11.5, 11.6, 12.2, 12.3, 15.3, 17, 21.3, B.3
and App. D.

**The v11 partition (self-contained; the partition v11 actually produces).** Materializing the document moves the two
formerly-SUPERSEDED units (v9's §0.1 and v9's §18.5) into COMPOSED, so of v9's 134 units v11 has **100 CARRIED, 23
AMENDED, 11 COMPOSED, 0 SUPERSEDED** (`100+23+11` = 134, I5′), with **23+11 = 34** changed from v9 (I5″), plus **2
NEW** spec units (§0.7, §23), for **136** total v11 spec units (`100+23+11+2` = 136, I6′). The 11 COMPOSED units are
the title, §0, §0.1, §13, §13.1, §13.2, §16, §16.1, §20, §18.5 and Appendix I. `v11-support/jackal.json` and the
§18.5 table below are internally consistent with this partition.

## V11-C.3 The change map (every v9 unit; v9 identity, v11 status, computed v11 identity)

| Unit | Status | v11 lines | Bytes | v11 sha256 | v9 sha256 |
|---|---|---|---|---|---|
| (title) | COMPOSED | 1-62 | 5595 | `b4db4107ee221bc2655ab8b8ddf7e918a8198e68d40782a31e89c00a06773755` | `1f2d0a2e955f43bcfcae97b3addf521b098f980ca79cd84f37f80accc78820e5` |
| §0 | COMPOSED | 63-64 | 60 | `19a4bb19d1bf917d1809b95333ace93ad36d2fcde986f67fbee408a5d86935ad` | `80267ea40473bab37f029b4b9573c239125e131fd185982839b93f108a0d16cd` |
| §0.1 | COMPOSED | 65-93 | 2533 | `9dbb89a4f2f9de95de1740a7c8c5425a6ed1e2a288c35aecfba7c12609b1c559` | `e34b3bbee3ea4744f2d2de21492b84c2a425c797bdbb29189ce5e7ecbbb235fb` |
| §0.2 | CARRIED | 94-117 | 2266 | `2986013a0b6f35c6d88d74e8e6c50b20c0ad4c9aebe7edff78fd0756ea2691c4` | `2986013a0b6f35c6d88d74e8e6c50b20c0ad4c9aebe7edff78fd0756ea2691c4` |
| §0.3 | CARRIED | 118-137 | 1834 | `a8722812979b2fe89b67dd0f0903d64f8bba384311c1f3a57b1ecdb89aa70d35` | `a8722812979b2fe89b67dd0f0903d64f8bba384311c1f3a57b1ecdb89aa70d35` |
| §0.4 | CARRIED | 138-160 | 1944 | `125e4c53d7b2747d0d17865a22f2d84a3fe9d4952d2c4e1bf75b74624b347c0a` | `125e4c53d7b2747d0d17865a22f2d84a3fe9d4952d2c4e1bf75b74624b347c0a` |
| §0.5 | CARRIED | 161-172 | 1083 | `ed814dad3e6cac843dd7f488a74900cc8de8b8dd8f6b83322dc7ed81403e8054` | `ed814dad3e6cac843dd7f488a74900cc8de8b8dd8f6b83322dc7ed81403e8054` |
| §0.6 | CARRIED | 173-180 | 547 | `fc36e0f7e099a40aa73199c89e9a5d0f1816203392dcf11b5541c28f664e0e08` | `fc36e0f7e099a40aa73199c89e9a5d0f1816203392dcf11b5541c28f664e0e08` |
| §0.7 | NEW | 181-236 | 5094 | `7f188aed849597b1efb086b56d2a20b56e4d3a3a69e048d8b457acb12156feee` | (none; NEW) |
| §1 | CARRIED | 237-278 | 3156 | `2ae9da8b3dc5177eb189805c8f7fdc48e4908a2204fb68a6b4be0b5118aa0dac` | `2ae9da8b3dc5177eb189805c8f7fdc48e4908a2204fb68a6b4be0b5118aa0dac` |
| §2 | CARRIED | 279-280 | 63 | `35f6eb75cbc9b074ead5488fca9693875386deb826fbd0374020398a83887683` | `35f6eb75cbc9b074ead5488fca9693875386deb826fbd0374020398a83887683` |
| §2.1 | CARRIED | 281-307 | 2658 | `62cb14bcb695c40049aa8b23195b0242a1a145576a18ebe88e45093b377e7d91` | `62cb14bcb695c40049aa8b23195b0242a1a145576a18ebe88e45093b377e7d91` |
| §2.2 | AMENDED | 308-323 | 1520 | `adc0ace242f095eeb222e2607d2d881d322626249367a53626deb8036c2df9df` | `f954d0a34a6d4eb0952d04b74d966e115ece877ea302dcba7cda7df19b569c2c` |
| §2.3 | AMENDED | 324-358 | 3470 | `bbc6240254ddf2c5ce91d67fea48e4b7fa748f9b0927b04f69799b09b4789ebf` | `698fa0836f497267eae07b89aeecfba6d8cfc56f8d33054ad860b79d937d2210` |
| §2.4 | CARRIED | 359-384 | 2356 | `076cf02493e497a50951aeefad90ebdb31354f810d176a088b96cf861f790276` | `076cf02493e497a50951aeefad90ebdb31354f810d176a088b96cf861f790276` |
| §3 | CARRIED | 385-386 | 39 | `5510e891fd324593657d164471cb63078bbc71af4f71c2da3fc35163ae8c2ed0` | `5510e891fd324593657d164471cb63078bbc71af4f71c2da3fc35163ae8c2ed0` |
| §3.1 | CARRIED | 387-399 | 1099 | `37ca5ff4babc986bc4343989256bc66bb67426a9087763eb22cb9868addbb8aa` | `37ca5ff4babc986bc4343989256bc66bb67426a9087763eb22cb9868addbb8aa` |
| §3.2 | CARRIED | 400-423 | 2989 | `7dc9ea13d4cffc14bd9e56c1c312dc8167f92faae117c4ac9a3ef2451aa6c47f` | `7dc9ea13d4cffc14bd9e56c1c312dc8167f92faae117c4ac9a3ef2451aa6c47f` |
| §3.3 | CARRIED | 424-475 | 4416 | `8134e140129264e3b3ff24284829f410cfb16f21f2a4500394ea722718cb426c` | `8134e140129264e3b3ff24284829f410cfb16f21f2a4500394ea722718cb426c` |
| §3.4 | CARRIED | 476-546 | 6805 | `ff14802bd61c0964c53306a5455e0ecff05b6acb3bf492246942ea39171a9748` | `ff14802bd61c0964c53306a5455e0ecff05b6acb3bf492246942ea39171a9748` |
| §4 | CARRIED | 547-548 | 106 | `030cba113f70fd51a55fba2cdbacef1d4bebdd0fa2b0813f0a7f935356beaa45` | `030cba113f70fd51a55fba2cdbacef1d4bebdd0fa2b0813f0a7f935356beaa45` |
| §4.1 | CARRIED | 549-589 | 3972 | `32381257ff4beca2691c3205f0c564b871539e093efff642c3b8351f7cd4b1ed` | `32381257ff4beca2691c3205f0c564b871539e093efff642c3b8351f7cd4b1ed` |
| §4.2 | AMENDED | 590-753 | 15451 | `78273e4068da7bf7b06ea288b7e8c1c70e8d2f0f332be4d39a1e29a5de0cd96b` | `28116cedfbb901f9a161eba4427e4aa1e8603aa961e991aab7b7e05c09dd246d` |
| §4.3 | CARRIED | 754-826 | 7157 | `5a924fb6ac8d8f39071a809c5c4befd2d0c43c0d6e324bd63c79612171798918` | `5a924fb6ac8d8f39071a809c5c4befd2d0c43c0d6e324bd63c79612171798918` |
| §4.4 | CARRIED | 827-852 | 2451 | `eb572f6edb96f31e7bf59a9d8176ed06a37de4f96282533d86a1d70d7d31a59c` | `eb572f6edb96f31e7bf59a9d8176ed06a37de4f96282533d86a1d70d7d31a59c` |
| §4.5 | CARRIED | 853-905 | 4784 | `de91424f7f367655a5ffa26ebaed048bf781978281c45d1ee1e364a3ef9d5de5` | `de91424f7f367655a5ffa26ebaed048bf781978281c45d1ee1e364a3ef9d5de5` |
| §4.6 | AMENDED | 906-977 | 6703 | `f4fd67c565c8790159522f200ff1ca8d2a1279fe9717919b0193dbaf18d59db6` | `00b3ed65328eb21773f171bf89852ac17c227e4c242c254aa4e2bc5c739eb234` |
| §5 | CARRIED | 978-979 | 137 | `46adbb0dd725d4f1ca5f142a684061fafc17e2c5165b6da45647a41585de9bab` | `46adbb0dd725d4f1ca5f142a684061fafc17e2c5165b6da45647a41585de9bab` |
| §5.1 | CARRIED | 980-1007 | 2284 | `e0bc923e20b24b36609ff4d44f5a354e999dcd57c67793c398d1890d68c14b97` | `e0bc923e20b24b36609ff4d44f5a354e999dcd57c67793c398d1890d68c14b97` |
| §5.2 | CARRIED | 1008-1040 | 3910 | `3f5976199bc5eb57fbd117bcb4bd98e4d530c17e14dd5638145b65501590b76b` | `3f5976199bc5eb57fbd117bcb4bd98e4d530c17e14dd5638145b65501590b76b` |
| §5.3 | AMENDED | 1041-1072 | 5784 | `74eed3fd62846c2a69bf3f174ef91683d6485bf9a25348bebc196498b7cca970` | `afba96af1fe021ef8a8705a4bfcf785481182ae4698070d3a361169694e4a647` |
| §5.4 | CARRIED | 1073-1079 | 478 | `debd77ac854c1a74be9913a849254ef55cff1e9f0adc2553f42431b3167eee6a` | `debd77ac854c1a74be9913a849254ef55cff1e9f0adc2553f42431b3167eee6a` |
| §6 | CARRIED | 1080-1081 | 144 | `6a852dcafc48edb984b90136498474c97f6f0348b8e6541fe33b803af9034fd3` | `6a852dcafc48edb984b90136498474c97f6f0348b8e6541fe33b803af9034fd3` |
| §6.1 | AMENDED | 1082-1107 | 2324 | `4d5e7541775b238e6761aecf7490f677eaef9221cf052628f2a5696ddfacd708` | `3d18ff6cf3be2307f6980717d1796fd4963eed1bddb4d51232ac59c328d2d608` |
| §6.2 | CARRIED | 1108-1124 | 1442 | `155a6ef1dfdbbf811f6bd5f0a35f3134e8e60f171ee273535f4b227a30e760c2` | `155a6ef1dfdbbf811f6bd5f0a35f3134e8e60f171ee273535f4b227a30e760c2` |
| §6.3 | CARRIED | 1125-1162 | 4302 | `995566ec7d4ddeee26abcf3c43ec78d72f7d17efe46d9228b9ee2790f474709c` | `995566ec7d4ddeee26abcf3c43ec78d72f7d17efe46d9228b9ee2790f474709c` |
| §6.4 | CARRIED | 1163-1179 | 1468 | `30a2971341b7817ab2ebed17553a1e51152729aa025201f4027d1b4f0cbfd4a3` | `30a2971341b7817ab2ebed17553a1e51152729aa025201f4027d1b4f0cbfd4a3` |
| §6.5 | CARRIED | 1180-1205 | 2640 | `7f63c223dc48968db1840b0c03fc711097648093ecbbfc7d5ed248d1578e2b8b` | `7f63c223dc48968db1840b0c03fc711097648093ecbbfc7d5ed248d1578e2b8b` |
| §7 | CARRIED | 1206-1207 | 113 | `8ab0b34614a172ffb23cde8314d7bef25492c58858feabd1d30e543cde17fbae` | `8ab0b34614a172ffb23cde8314d7bef25492c58858feabd1d30e543cde17fbae` |
| §7.1 | CARRIED | 1208-1225 | 2380 | `f3956fa90333b2462b6dc6ca3996d581f2365859a7527438b267176b79d6b895` | `f3956fa90333b2462b6dc6ca3996d581f2365859a7527438b267176b79d6b895` |
| §7.2 | CARRIED | 1226-1248 | 2191 | `7faec7003ad60f3723bd527d117099d1c40615466ed7acd274903c19a54d8047` | `7faec7003ad60f3723bd527d117099d1c40615466ed7acd274903c19a54d8047` |
| §7.3 | CARRIED | 1249-1282 | 3468 | `eeaeab07f27381c5af35893f610b81e421bd7ca96e7568d96540ced5164e5e2e` | `eeaeab07f27381c5af35893f610b81e421bd7ca96e7568d96540ced5164e5e2e` |
| §7.4 | CARRIED | 1283-1297 | 1237 | `a345f95d51ea80e4e381b4301095d46f94cef1b8b5235322c52800b5a404f8bb` | `a345f95d51ea80e4e381b4301095d46f94cef1b8b5235322c52800b5a404f8bb` |
| §7.5 | CARRIED | 1298-1313 | 2318 | `58b24a0d5a3462b2659cb856abf0558bf42183193c745d16bdba67a72037114a` | `58b24a0d5a3462b2659cb856abf0558bf42183193c745d16bdba67a72037114a` |
| §7.6 | CARRIED | 1314-1323 | 826 | `da3dc6642e8c8b1bf407a522e929faa1997c00c2b74738d67783089debc1b34a` | `da3dc6642e8c8b1bf407a522e929faa1997c00c2b74738d67783089debc1b34a` |
| §7.7 | CARRIED | 1324-1348 | 2379 | `8885f573d2d0fbdd54b85fa094eec6c601477ae7908bac413fe05274e29795cc` | `8885f573d2d0fbdd54b85fa094eec6c601477ae7908bac413fe05274e29795cc` |
| §8 | CARRIED | 1349-1350 | 121 | `5dc90f8d992d37f789b9fdc38f5cef1248a2bb2ae0c5322ab39442c58024bc66` | `5dc90f8d992d37f789b9fdc38f5cef1248a2bb2ae0c5322ab39442c58024bc66` |
| §8.1 | AMENDED | 1351-1377 | 3403 | `16e506614ca92c62c7a4287c75108d13d2e0900de45bfbd497beec241c267e78` | `818cd88571e5eeb889a08aae3a267c1a63abc20b07948478d6a608361fd31c91` |
| §8.2 | CARRIED | 1378-1389 | 1030 | `309b19cccb33bc3a0a2d9863e13e869de1e42a9ae055ede4b84a47ec7fde5705` | `309b19cccb33bc3a0a2d9863e13e869de1e42a9ae055ede4b84a47ec7fde5705` |
| §8.3 | CARRIED | 1390-1435 | 5061 | `ac234959421ccdd77c8be3ce605c43d1e6967450793033d765e31a0d5918b98f` | `ac234959421ccdd77c8be3ce605c43d1e6967450793033d765e31a0d5918b98f` |
| §8.4 | CARRIED | 1436-1469 | 2819 | `897375821817ed762c6b5cf287e32d44e0f8ea439afbb714c153c60f5116cf58` | `897375821817ed762c6b5cf287e32d44e0f8ea439afbb714c153c60f5116cf58` |
| §8.5 | CARRIED | 1470-1505 | 4369 | `2980b640ea948fef9793bf3f21123cdbf3f9fd28313ebd0aeac4be67b3105653` | `2980b640ea948fef9793bf3f21123cdbf3f9fd28313ebd0aeac4be67b3105653` |
| §8.6 | AMENDED | 1506-1528 | 2182 | `1b711ff01055da49b97cde294fe320097a2161ead13103574ccc4fc9a2835ed2` | `3ec9d7f237addb503a8f3a90434741ae57e7386139ae3ab5b5a06271ae25dd1f` |
| §9 | CARRIED | 1529-1530 | 189 | `d1843b7e7e7bee1fec119a7314ce98958f5e46327d872070510c73a6b1c90a01` | `d1843b7e7e7bee1fec119a7314ce98958f5e46327d872070510c73a6b1c90a01` |
| §9.1 | AMENDED | 1531-1556 | 2226 | `57398c14ba66ceabf2e03c7ca8a73985c23e8e82da54210f2dfabf56036fb8db` | `bb6878ba3ff06de0beee08216c93ad10d2e4d4e483b8fdab0c693cb757e15502` |
| §9.2 | CARRIED | 1557-1574 | 1714 | `6c4a383502ee74cabb5b597ae8220ba1d86122fa6d12400adfb30845910dc11f` | `6c4a383502ee74cabb5b597ae8220ba1d86122fa6d12400adfb30845910dc11f` |
| §9.3 | AMENDED | 1575-1728 | 16273 | `869ca17e0e564e8666b2ad5e69bcc5f2028f95f0b1fb8bfd1775f07a171ce0df` | `17a191ab2b3e38f1edc2808573e60375be8195f0b567f36ce2df5a4be962624a` |
| §9.4 | CARRIED | 1729-1826 | 9225 | `ef7160cdca5dff8e1c4a85559a76603e21275f6337b6381050aa3d68917e9c6d` | `ef7160cdca5dff8e1c4a85559a76603e21275f6337b6381050aa3d68917e9c6d` |
| §9.5 | CARRIED | 1827-1870 | 8966 | `fe247395518af3df20cefd0609def440f77429f1e69e08335e6a67eb79491586` | `fe247395518af3df20cefd0609def440f77429f1e69e08335e6a67eb79491586` |
| §9.6 | CARRIED | 1871-1895 | 2396 | `c98574eebfb51d6313ef4ac6dfeadb9b6c276a7cfb2fd44596744bba7207ba84` | `c98574eebfb51d6313ef4ac6dfeadb9b6c276a7cfb2fd44596744bba7207ba84` |
| §9.7 | CARRIED | 1896-1943 | 4489 | `dc6b60071dc98380aa87d184fd7ac3b8904c1800991e561804a7083d4a4c2983` | `dc6b60071dc98380aa87d184fd7ac3b8904c1800991e561804a7083d4a4c2983` |
| §9.8 | AMENDED | 1944-2215 | 33091 | `26cb68b6f8ede911baa4d89bdda38a2d948b90e6ec5d718fd2cbbb92757e595b` | `9d84e8e6f9f01c833468290b639c6804994cce69b9ff9b0fed542baafd5c84d5` |
| §10 | CARRIED | 2216-2217 | 173 | `b923c50c51930667776aced4d6d5b16a080102e4e056e61d0ade2fd420c1d98d` | `b923c50c51930667776aced4d6d5b16a080102e4e056e61d0ade2fd420c1d98d` |
| §10.1 | CARRIED | 2218-2255 | 3416 | `22ae43ed8d8e6266e387df30cb572b6148a9934242deb6a3ef6db7b65a2dde02` | `22ae43ed8d8e6266e387df30cb572b6148a9934242deb6a3ef6db7b65a2dde02` |
| §10.2 | CARRIED | 2256-2369 | 11746 | `ecb48668e7ca7ad2348fbff5af741a954c6b25a73f5635b42c7ef9076acdd435` | `ecb48668e7ca7ad2348fbff5af741a954c6b25a73f5635b42c7ef9076acdd435` |
| §10.3 | CARRIED | 2370-2375 | 369 | `2b275b998e8c39b306421b0c6400ea8c12528d2b9741410c51f99ac4bca59990` | `2b275b998e8c39b306421b0c6400ea8c12528d2b9741410c51f99ac4bca59990` |
| §10.4 | CARRIED | 2376-2419 | 4467 | `45c96fa1f94741a0a04242424778df566daa7cd7914d7c8ff2cc04be34e7d85f` | `45c96fa1f94741a0a04242424778df566daa7cd7914d7c8ff2cc04be34e7d85f` |
| §10.5 | CARRIED | 2420-2456 | 3427 | `88f1ca6288ee6dbb64ac667c945e450260a3b1250371efd3a35513e66abe89a9` | `88f1ca6288ee6dbb64ac667c945e450260a3b1250371efd3a35513e66abe89a9` |
| §10.6 | AMENDED | 2457-2493 | 4614 | `85f4d375a1251675df201c51fc16ead8a1a378e16933657ad0d6612dc72f5121` | `e922ecf42fcaeb673d72fa459602d9de4b103216c447ab1e4c9cc4ae3bd1b071` |
| §10.7 | CARRIED | 2494-2533 | 4099 | `9cdcd4ca80399bb8b09faff5404b7acaed06a81f8c1c79318797212a30a08826` | `9cdcd4ca80399bb8b09faff5404b7acaed06a81f8c1c79318797212a30a08826` |
| §11 | CARRIED | 2534-2535 | 127 | `554fcbe4c216f90ff9d4ae0b8672903c7d18685221dc80a7ec07dbc59d5df8cd` | `554fcbe4c216f90ff9d4ae0b8672903c7d18685221dc80a7ec07dbc59d5df8cd` |
| §11.1 | CARRIED | 2536-2555 | 1723 | `0ad981bd44c1a4c63a85f56e89f7983c354e19b1eea1b5ab56eec3357a73463e` | `0ad981bd44c1a4c63a85f56e89f7983c354e19b1eea1b5ab56eec3357a73463e` |
| §11.2 | CARRIED | 2556-2569 | 1173 | `64562978ae2d418c938f8705884948c597351891964557787afcc6ba66fed3da` | `64562978ae2d418c938f8705884948c597351891964557787afcc6ba66fed3da` |
| §11.3 | AMENDED | 2570-2619 | 8589 | `c62d8d7032341d358f890e7f6fab44967913cb6d52a0425ad6b3dd86127f822f` | `88d54fa1f3dd5c7273297996b0bd0318421b84767a802f3538f80f7c7da033d6` |
| §11.4 | AMENDED | 2620-2798 | 17610 | `b206a125123ac987dfefda7ebaf5f39db75e0dab79439b56402db517cda2e79a` | `165128c67ddb943e055d82157760cd177c45aeadfc38ca30b694a10b97db6182` |
| §11.5 | AMENDED | 2799-3197 | 22986 | `5176b983f524bf0322f260236ec66b1823a9e2f49b572de096056e685d032c04` | `c809520b94062d6fa33b561af2f2c02ac37ec156a9162cc4c3cdd0d91fb46ff8` |
| §11.6 | AMENDED | 3198-3213 | 1282 | `c68905f87c767f0ffd451fdfed87ede86ff77b3b40c25c506ad9cdc9f348bf5d` | `d0f19a4c6ca8991a4ff06e94687723a8b967797778fac7c277ce3ae30907c8f2` |
| §11.7 | CARRIED | 3214-3266 | 6915 | `610b5ea29a17f2da23d66da5a3e4bebdc5bed2c425046ee4e055b398dd397333` | `610b5ea29a17f2da23d66da5a3e4bebdc5bed2c425046ee4e055b398dd397333` |
| §12 | CARRIED | 3267-3268 | 202 | `b60fea083ed7bef57ec1a8638c5bcdaeb9875f3b247ed1853060446f6a013935` | `b60fea083ed7bef57ec1a8638c5bcdaeb9875f3b247ed1853060446f6a013935` |
| §12.1 | CARRIED | 3269-3276 | 508 | `c9c23c0260e6bbd67676b1725419425239b37769d2081a5e66e793e07bcfa9d1` | `c9c23c0260e6bbd67676b1725419425239b37769d2081a5e66e793e07bcfa9d1` |
| §12.2 | AMENDED | 3277-3393 | 11342 | `13c03acf81361084ea0e10a733a19c204630320a14bd635c3ab1decf3bcad275` | `43a1796a7072f0301c9e5e03abb4defd601da4fddcf6d279d1cbd8b1f46ad7c6` |
| §12.3 | AMENDED | 3394-3418 | 5086 | `6757ea4a413182bf0844c182503cd1e192900a0bf6e6377ce4404462f4d36d7f` | `b9392577ca84a9c6741e0a0113036b34307d3c2029966cf67e5d0540751ea014` |
| §13 | COMPOSED | 3419-3474 | 5596 | `bd5211e6e348674c31d437cc203dc7c6beeb061c6e429e6bfb1f06cf9f5791fa` | `59661d221f58572e506e70aedfdeb1fb34c5b21fb4d8f1a9a48653a56913cd04` |
| §13.1 | COMPOSED | 3475-3496 | 5704 | `ba84454a84746f7b8acd1772335176c3c3d0ccd9f5ba0171560a19b7d475d1c6` | `597c6887c79dd4c24794ae248c1ddd560eec940f25278170a6e61b9af87ef387` |
| §13.2 | COMPOSED | 3497-3564 | 9779 | `2ea928b6a2c3eae4943f0fce5e59aa09151e4c7d20cccf7b5c741b822afdb8bd` | `722c476e0e6f94ce635e6792f6f64746aabe8be5cbb1216f779c963dc89c450a` |
| §14 | CARRIED | 3565-3575 | 955 | `00a709ad5f406f810c5a993c63c2516e27b876053ffc7b070e74bdd503d5e06a` | `00a709ad5f406f810c5a993c63c2516e27b876053ffc7b070e74bdd503d5e06a` |
| §14.1 | CARRIED | 3576-3583 | 552 | `74064f167fa18ca4c37b49cef1070d1902ab55bf3201fcca04aac6be3a9c59f9` | `74064f167fa18ca4c37b49cef1070d1902ab55bf3201fcca04aac6be3a9c59f9` |
| §14.2 | CARRIED | 3584-3602 | 3098 | `2d1d3c6cd2a9786ab739b7dfa7f802ecabff525141eee66539f20eb777f600c7` | `2d1d3c6cd2a9786ab739b7dfa7f802ecabff525141eee66539f20eb777f600c7` |
| §14.3 | CARRIED | 3603-3625 | 2259 | `b3e074d76f438d2e0c270eea40ff16b326ec917c6ec852d25f9c02a8ce55baa4` | `b3e074d76f438d2e0c270eea40ff16b326ec917c6ec852d25f9c02a8ce55baa4` |
| §14.4 | CARRIED | 3626-3638 | 739 | `e9387e358eaffbf6a7244c1a7c9e15c237cfce7b2d5a39cd2e05a71af4860f1b` | `e9387e358eaffbf6a7244c1a7c9e15c237cfce7b2d5a39cd2e05a71af4860f1b` |
| §14.5 | CARRIED | 3639-3697 | 5582 | `0f88ce97455fdced4ca5111cdcbb6d4ab306cb0f3775221a8237520f371a51a1` | `0f88ce97455fdced4ca5111cdcbb6d4ab306cb0f3775221a8237520f371a51a1` |
| §14.6 | CARRIED | 3698-3706 | 635 | `41c190d586646edc31cdee4609544d067a3a7a3586a9c725a620daccca10f8ed` | `41c190d586646edc31cdee4609544d067a3a7a3586a9c725a620daccca10f8ed` |
| §14.7 | CARRIED | 3707-3722 | 1391 | `bd990a9b3c3e6b09845754ee99a2ae58cfd0199a46bb5b5b1c0aef0ffa2723a7` | `bd990a9b3c3e6b09845754ee99a2ae58cfd0199a46bb5b5b1c0aef0ffa2723a7` |
| §15 | CARRIED | 3723-3724 | 139 | `c28ab08b1a6cf57c5c65775871754ab7312225c4fb76ff455a1da064d04a35d0` | `c28ab08b1a6cf57c5c65775871754ab7312225c4fb76ff455a1da064d04a35d0` |
| §15.1 | CARRIED | 3725-3749 | 4358 | `132ed3166570227fad818e570035aba1c7cf0d5c033471c28c114989a5ffee4d` | `132ed3166570227fad818e570035aba1c7cf0d5c033471c28c114989a5ffee4d` |
| §15.2 | CARRIED | 3750-3756 | 429 | `89e6432791fdcfd0fb53c905eaf9bea0fd8fe81b4ff1f212c3cc10fb0a1250c9` | `89e6432791fdcfd0fb53c905eaf9bea0fd8fe81b4ff1f212c3cc10fb0a1250c9` |
| §15.3 | AMENDED | 3757-3852 | 9370 | `0928e187125a7a4933989ff4108436c0e0e69bb35e869f8fa24296194ca63eac` | `c63a0485c9548f73a653b7f7acc2999d27133288b5b3e353f70979982a1e8ee7` |
| §15.4 | CARRIED | 3853-3869 | 1563 | `feec26c34e5d6bf58ff90bbae7b31979ac154a0a0c802a0395f15cee98a9f557` | `feec26c34e5d6bf58ff90bbae7b31979ac154a0a0c802a0395f15cee98a9f557` |
| §16 | COMPOSED | 3870-3914 | 4159 | `51ee28350490e2ec734db578152b2c456d4c6153c33e3ae54c892b5517fe09ad` | `1592969c78f6aaf42bf5af4ca29bdbda4dedcb17f74f8cf5b7eb57d206b097b3` |
| §16.1 | COMPOSED | 3915-3933 | 3881 | `ea8283a12b1bd2b47c3d1eb8cc7b33e7c5ec384e4bcbd6faac6400f4522ba237` | `b17c49541c24d07b1e6aa970861b3cd5c0a5aa4ffee2378435b3c9fc1c073a28` |
| §17 | AMENDED | 3934-3963 | 5941 | `1104415e8f728d51ec3cf25d7c05527f2dca64d9789e3b11508cb89d473e5713` | `2c819d7d7a8025b4844b931432a0686efa666c1c8d1ac9c97b7440b69e2c39f4` |
| §18 | CARRIED | 3964-3971 | 653 | `e92c04dede085626f123091986be4884fc74d60a2819e97e584daea9411eac00` | `e92c04dede085626f123091986be4884fc74d60a2819e97e584daea9411eac00` |
| §18.1 | CARRIED | 3972-4023 | 5023 | `43d110e60d6ed26bc65fdaf89b7ab88198c944ed7e0b427a00fc2992435c5e10` | `43d110e60d6ed26bc65fdaf89b7ab88198c944ed7e0b427a00fc2992435c5e10` |
| §18.2 | CARRIED | 4024-4039 | 1517 | `6f0835c8d587e8ec3361fb94606cb20dd98c1a9ee79af748a4900ff7893f5771` | `6f0835c8d587e8ec3361fb94606cb20dd98c1a9ee79af748a4900ff7893f5771` |
| §18.3 | CARRIED | 4040-4046 | 463 | `234ad3759214ab92b3e76c373cb9e0d11ae01d1bee9f4f0ae001c14a1a6af099` | `234ad3759214ab92b3e76c373cb9e0d11ae01d1bee9f4f0ae001c14a1a6af099` |
| §18.4 | CARRIED | 4047-4058 | 841 | `d36420f06d07ec16061137f3fe68d0fd10fc664287d54a9126606bc42e303f90` | `d36420f06d07ec16061137f3fe68d0fd10fc664287d54a9126606bc42e303f90` |
| §18.5 | COMPOSED | 4059-4067 | 654 | `6bdff5afe9d52e97acdf3f7d7016982afaf926134bb8555b7d308232fd998f3a` | `f15db00c2490cfd2d3073036f024cbba94eabc01cb2b01778fc7c2c7875c18f7` |
| §18.6 | CARRIED | 4068-4076 | 785 | `ba1db167e50f1026298c1841bf3c269c5f6b11ff906443a14a549aed72ca715e` | `ba1db167e50f1026298c1841bf3c269c5f6b11ff906443a14a549aed72ca715e` |
| §19 | CARRIED | 4077-4085 | 744 | `fb08e68e1409c1040975b20fcee3cc498a93566cdf33531ea01ad8d87f4221ec` | `fb08e68e1409c1040975b20fcee3cc498a93566cdf33531ea01ad8d87f4221ec` |
| §20 | COMPOSED | 4086-4116 | 3002 | `e52693a876b86a2a3d8341a5b5aa9b784af792d2a66eebf38a9a8c771af49bb9` | `350d52edb55a8aaad58322e7a1897ffcbb2048aef20bdc1aac695ca656aef78d` |
| §21 | CARRIED | 4117-4118 | 179 | `d7c0a6d1ec091464b5328e651ac42c7c1b51caa47cb511f2ed2032ab62cc669a` | `d7c0a6d1ec091464b5328e651ac42c7c1b51caa47cb511f2ed2032ab62cc669a` |
| §21.1 | CARRIED | 4119-4150 | 2779 | `99ddb6ca43802e3d762978ee5017ff5206ad9641ee29b06c248e17197e5e7269` | `99ddb6ca43802e3d762978ee5017ff5206ad9641ee29b06c248e17197e5e7269` |
| §21.2 | CARRIED | 4151-4157 | 614 | `8d89026d3ccffcd9a5f769c10389dc18adfe391d1c61c3de492d78e040b932c1` | `8d89026d3ccffcd9a5f769c10389dc18adfe391d1c61c3de492d78e040b932c1` |
| §21.3 | AMENDED | 4158-4179 | 3761 | `c110fb9656b84c749f78b641878d2bb5c8c5be48a268287a9b1f151522d895d3` | `c88585c55cf0cd068baa975b96f7619bcc61f005e51a4381affc87d1ddfd305e` |
| §21.4 | CARRIED | 4180-4191 | 1648 | `02071661f88bfbc66710aa02e7a4046e020b22dfd8eba3b3010323ae4c24c911` | `02071661f88bfbc66710aa02e7a4046e020b22dfd8eba3b3010323ae4c24c911` |
| §21.5 | CARRIED | 4192-4202 | 1344 | `a474c25556f0c4ddb261eb5cbb9c11fe337db64d13dfafc6d1095e71d75e1e16` | `a474c25556f0c4ddb261eb5cbb9c11fe337db64d13dfafc6d1095e71d75e1e16` |
| §21.6 | CARRIED | 4203-4211 | 701 | `e5abdf4693c889e748acf2847cdc71284026e09ee068af6561c31df182f66615` | `e5abdf4693c889e748acf2847cdc71284026e09ee068af6561c31df182f66615` |
| §22 | CARRIED | 4212-4213 | 123 | `b54545344d2fa2a11b5eb45e57b506b71db7804be049af649f17c3c500268df0` | `b54545344d2fa2a11b5eb45e57b506b71db7804be049af649f17c3c500268df0` |
| §22.1 | CARRIED | 4214-4220 | 447 | `2b1b5b5b560192d039e64e0bfba3e6f7bb0f4a821b43ffdc176e3880836002fb` | `2b1b5b5b560192d039e64e0bfba3e6f7bb0f4a821b43ffdc176e3880836002fb` |
| §22.2 | CARRIED | 4221-4229 | 829 | `4b3bc48c8f9987d6b8f27783d5bc73cd86d6fd0b649018137ae2f358364aadf6` | `4b3bc48c8f9987d6b8f27783d5bc73cd86d6fd0b649018137ae2f358364aadf6` |
| §22.3 | CARRIED | 4230-4286 | 7037 | `f0e3f291a1ae70b759aeccb5c6f4c71729ce8b9da0a2dc9049420fcdb5855c4d` | `f0e3f291a1ae70b759aeccb5c6f4c71729ce8b9da0a2dc9049420fcdb5855c4d` |
| §22.4 | CARRIED | 4287-4298 | 978 | `480e422524317a9cf0037fbacdb1c817077ab0b82e2f4262addd2b2ff9b0c438` | `480e422524317a9cf0037fbacdb1c817077ab0b82e2f4262addd2b2ff9b0c438` |
| §23 | NEW | 4299-4394 | 8410 | `18215927660ce1ad012bf1d4715134b1e84cfc9d904600ac9a8bc51d22028d73` | (none; NEW) |
| App. A | CARRIED | 4395-4458 | 14868 | `1211f48a394f8dd03602066280d11ec7ee0089976919ad7028fa422a3556b9a0` | `1211f48a394f8dd03602066280d11ec7ee0089976919ad7028fa422a3556b9a0` |
| App. B | CARRIED | 4459-4467 | 676 | `eef7ebf9b21f869d21e2f3fe24a6052fd5fa503a50145afd3a1676bffaa30fc7` | `eef7ebf9b21f869d21e2f3fe24a6052fd5fa503a50145afd3a1676bffaa30fc7` |
| §B.1 | CARRIED | 4468-4483 | 1483 | `95c9bb599940e2e67647c21baac4e57bb6c59d181fc24dcab85e3e41fd549abe` | `95c9bb599940e2e67647c21baac4e57bb6c59d181fc24dcab85e3e41fd549abe` |
| §B.2 | CARRIED | 4484-4508 | 2456 | `2c2a322a54675cf10ff5245169b20cab8ff83be262bdd1b220baec43e0f08bb5` | `2c2a322a54675cf10ff5245169b20cab8ff83be262bdd1b220baec43e0f08bb5` |
| §B.3 | AMENDED | 4509-4557 | 14227 | `f56d96fb3077ec80fbcadb202c8540d1ac33c8e5a5d29f04e93c61723ce65577` | `d5d6f30ee183ad65fa9cfb379b627511d632aec8174bc24499e0ab9f621c8b6c` |
| §B.4 | CARRIED | 4558-4790 | 29645 | `58d7d91044c698fb9251dc82a0e38e75f29baebd6f9ae85d3c5cf149c6edaf26` | `58d7d91044c698fb9251dc82a0e38e75f29baebd6f9ae85d3c5cf149c6edaf26` |
| App. C | CARRIED | 4791-4850 | 4399 | `e21904702b855c69feb1afe86117e9088684c70162571459c5b906ea2b9a79c5` | `e21904702b855c69feb1afe86117e9088684c70162571459c5b906ea2b9a79c5` |
| App. D | AMENDED | 4851-4909 | 8688 | `d9afe09ef61c0e03ec0883c46e70a0fd2522062da1ceb8d7be7019ad87cc4fb5` | `f00e0b1b9c786fddced73bf368ddd416d57d13b6afcf5d78fad73dd86415e3a1` |
| App. E | CARRIED | 4910-4973 | 5709 | `f7d449206492465183052962b4a8ea13d20a28202ac41069c31a283e1d2b06f1` | `f7d449206492465183052962b4a8ea13d20a28202ac41069c31a283e1d2b06f1` |
| App. F | CARRIED | 4974-5018 | 3963 | `4b6f95f0f14f03859e6c6e08222fd51c35a0fc46365a1bf35c31d4d3fb409cc1` | `4b6f95f0f14f03859e6c6e08222fd51c35a0fc46365a1bf35c31d4d3fb409cc1` |
| App. G | CARRIED | 5019-5126 | 10289 | `56ff67770137755792dea29437261ae2a148e41b3f2cbb437f29d942f99df9b1` | `56ff67770137755792dea29437261ae2a148e41b3f2cbb437f29d942f99df9b1` |
| App. H | CARRIED | 5127-5180 | 4593 | `dd7b25abacb71a46a9c81f6399db2e7f7f7c3047348f36bf364202958406a20a` | `dd7b25abacb71a46a9c81f6399db2e7f7f7c3047348f36bf364202958406a20a` |
| App. I | COMPOSED | 5181-5221 | 3586 | `fd041599c0c88370df8637d8cf3e5ca51b3a66d4b7ffed95dbbe24a74adda509` | `afdb7864df65b89c9b21b411a9263de11b59ab9af9ba28c236aa0feb2aa986fa` |
