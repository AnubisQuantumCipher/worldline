# Isolation and storage proposal W-1, v7: a root-built target view, custody without copying, and an architecture evaluation (specification)

**Status.** Drafting author's design specification, written 2026-10-05 UTC for the Claude Code lead. It is a
CANDIDATE specification of the protected-writer confinement design for the scratch proof frame, and the successor to
v6.
- Nothing in it is implemented, installed, approved, executed or reviewed. No account, group, ACL, sudo rule,
  installation, slice, tmpfiles rule, mount, namespace, Landlock domain, probe, selftest, vault, adoption or window
  action has been performed for v7.
- Proof dispatch stays blocked by the confinement criteria (V5-B01, V5-B02, both OPEN) and by the capacity gate
  (Gate 0, NOT ESTABLISHED). v7 evaluates enforcement designs beyond the unprivileged DAC architecture (§22) and finds
  none that is established as keeping the original success domain fixed. It adopts the target view (§12), which
  establishes the custody facts of §9.8 under named premises and changes the target's environment in the ways §12.3
  lists. V5-B01, V5-B02 and W1-V5-PRESERVATION stay OPEN and are not narrowed (§0.4).
- v1-v5 (hashes as v6 states them) and v6 (`ISOLATION-STORAGE-PROPOSAL-v6.md`, sha256
  `5a0e861b042d11f0d9932b6b0f83020d61e944b09e730d2f7279867f24ec8f6d`, 501735 bytes, with `v6-support/jackal.json`
  sha256 `10c30d8ea534269d90b83c56da2dffe38c3e96dff4ff21f426fb9b1378eb23f3`) are preserved unchanged.
- **Form.** This file is one complete specification, not a delta. Its base is v6 (118 units). §18.5 maps every v6
  unit, with its sha256, to its v7 status (carried byte for byte, amended or replaced); six units are new. The
  architecture changed substantially, so most of the document is amended or replaced (§0.1); no other document has to
  be composed with this one.
- v7 answers the sealed actual gpt-6.1-sol design review of v6, `wt-1/proposal/v6-review/gpt61-v1` (verdict
  NOT_ENDORSED; hashes verified before drafting, 11:57:18Z: REVIEW.md
  `b519d27dd77b650bad5ae61b6425b090c42c76373b3f254917fc0e8ae4168ca1`, review.json
  `f8825bc011674c9f90455398c7b582619719f0af5e1291d77e7bb770ff211ddc`, checks.json
  `1a3c6d0539be473cf15166e8c51e246400f88002e50e8c994ab39be7b225b8e8`, review-freeze.json
  `b251aab01555a2b304be5b54011ec7ca3d0be1dadf4a2adf28e5e0e959509c90`). Its 11 required changes (W1-V6-PRESERVE …
  W1-V6-CATALOGUE; JACKAL exact, parsed `1+1+1+1+1+1+1+1+1+1+1`) are quoted verbatim in §18.1, its K0 ruling in §22.2,
  and every prior correction, gap and sub-gap it rules is mapped in §18.2-§18.4.
- **Review track.** W-1 has its own design-review track: v7 is reviewed on its own by actual gpt-6.1-sol, and the
  operator package reports only W-1's reviewed status. The criteria and every earlier correction are unchanged and
  binding.
- **§18 gives the author's own assessment (CLOSED-AT-SPEC-LEVEL or OPEN) for an independent actual gpt-6.1-sol
  reviewer to judge. It is not closure, and no row says a section "answers" a finding.**
- Authority. Design and frame code are routine reversible engineering under the human's preserved authorization; no
  in-principle approval is needed for them. Reserved to the operator: actual privileged setup (accounts, groups, ACLs,
  sudo rules, the sshd drop-in, the slice unit, the tmpfiles rule, installation of the frame and of its root launcher
  RL, mounts, reconciliation, rollback) on a concrete reviewed inventory; material API/ABI/owner-policy changes;
  toolchain/deployment architecture; merge, release, install, sudo, production and real PRIME. Every privileged
  element of v7 (RL's installation and rule, the slice, the tmpfiles rule, the images) lies inside that reserved setup
  and rollback; RL's per-attempt namespaces and mounts are actions of the installed, reviewed code under that rule. v7
  adds no approval gate.
- Every "verify", "check", "probe", "selftest" or "observe" below names future work, except the passive observations
  explicitly dated and attributed to the drafting author (Appendices E, F and G). Design text is not executed evidence.

**Inputs read for v7** (read-only): the gpt61-v6 `REVIEW.md` and `review.json` in full, with `prior_closure`, the gap
and sub-gap maps, the routes and catalogue assessments and the K0 ruling (checks.json and review-freeze.json
hash-verified only); v6; frame v5 `scratch.py` (`f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86`)
with its baselines `tool-inventory-template.json`, `launch-environment.json` and `runtime-closure.json`; the installed
`/usr/include/linux/landlock.h`; the kernel's build configuration; host facts dated in Appendix G. "S:N" is line N of
frame v5's `scratch.py`; frame v6's lines are cited as "v6 scratch.py:N".

**Non-claims, short form** (full list §20). No sufficiency is claimed. V5-B01, V5-B02, W1-V5-PRESERVATION, Gate 0 and
every original Phase One obligation stay OPEN with their original owners, releases and dependencies. The target view
is not established as preserving the original success domain (§22); three frame read routes stay OPEN under V5-B02
(§9.8 N6). A kernel-enforced writer boundary is not proof of the frame code, not lead authentication, not target
confinement and not capacity. Installed verification of every premise named in §9.8 N7 and of TOOL-CLOSURE (§22.4) is
future work; if a premise fails, W-1 must be redesigned, and no exception is taken.

---

## 0. Reading guide, form and what changed from v6

### 0.1 Form

A *unit* of a document begins at each line, outside fenced code blocks, that starts with `# `, `## ` or `### `, and
runs to the line before the next unit's first line (the last unit to the end of the file); its bytes are those lines
with their line terminators, as in v6 §0.1. v6 has 118 units (counted by a read-only script, Appendix G). §18.5 lists
each of them with its v6 line range, size and sha256, and its v7 status:
- **CARRIED**: the v7 unit is byte-identical to the v6 unit, so it has the listed sha256;
- **AMENDED**: the v7 unit is the v6 unit with the changes §18.5 names; its whole text is in this file;
- **REPLACED**: the v7 unit with the same heading number is new text;
- **NEW**: §22 with its four subsections and Appendix G, which v6 does not have.

The counts are 29 carried, 63 amended and 26 replaced v6 units (JACKAL exact, parsed `29+63+26-118` gives 0), and v7
has 124 units (JACKAL exact, parsed `118+6`). No v6 unit is dropped: where v7 withdraws a v6 mechanism, the unit that
held it says so. Units of this file appear in v6 order, with the new units at these places: §22 and its subsections
after §21; Appendix G after Appendix F. Every cross-reference resolves in this file.

### 0.2 Author corrections of v6 (v6 itself is not edited)

1. **v6's preservation claims** ("no output state that the original walk accepts is refused", §0.3 and §9.8 K1; "the
   copy-data ceiling is not a narrowed case", §14.7 and §21 D3) are withdrawn with the copy route (review
   W1-V6-PRESERVE). The copy route substituted inodes and attributes, had its own failures and ceiling, and refused
   cases the original accepted.
2. **v6 §9.8 K5 and K8** stated that the frame mutates nothing outside its creations and reads foreign sources in one
   place only. Both are false: directory listings and the report read were omitted, and a read of a foreign-owned
   source updates its access time (review K8). §9.8 N6 replaces them with a complete read-route inventory.
3. **v6 §10.2** allowed a complete, valid close marker whose writer saw a later step fail to confirm a record that
   the writer retried and downgraded. §10.1's single commit point replaces it.
4. **v6 §11.4** said that every atom changes one object and that its vectors were all reachable states; both are
   false for parent-directory entry sets and link counts and for objects that several scripts change. Replaced by the
   global phase (§11.4).
5. **v6 §11.7** replaced the per-use comparison of the images directory's entry set with operator captures. Withdrawn
   (§11.7).
6. **v6 §9.3 C1** checked facts that only `RECORDS` delivers (the sealed template, the environment, the descriptor
   pins) before C's hello. Moved to C2.
7. **v6 §9.4** gave no argument that its scans observed one common state, and v6 used "same `st_dev`" as "no mount
   boundary". Replaced by the census of an absorbing kernel state and the exact mount predicate (§9.4, §9.8 N3).
8. **v6 §21** mixed the S5 baseline with the S6 repair, stated A4's baseline inexactly, omitted the report read from
   the read baseline, and stated D3 and D8 with causal absolutes. Rewritten (§21).
9. **v6 §0.4**'s "the author has found no such mechanism" concerned the unprivileged DAC architecture; the review's K0
   ruling limits it to that architecture (§22.2). v7 evaluates the designs beyond it (§22).
10. **v6's release condition** (its D5: global uid, manager and lease conditions) exceeded v5's `owned_terminal`.
    Withdrawn: release follows v5's predicate (§9.4).

### 0.3 What v7 changes, per required change (§18.1 gives each verbatim, with the author's assessment)

1. **W1-V6-PRESERVE** (§22, §12, §21): the architecture evaluation; the target view adopted; every remaining change
   listed; both absolutes withdrawn. V5-B01, V5-B02 and W1-V5-PRESERVATION stay OPEN.
2. **W1-V6-READ-MUTATION** (§9.8 N6): `O_NOATIME` wherever the reader owns the object, which in the view covers every
   entry below `source/`; routes R-d, R-f and R-h keep V5-B02 OPEN.
3. **W1-V6-COMMIT-AMBIGUITY** (§10.1, §10.2, §10.5, §13.1 P-CHAIN): one commit point, the close marker's link of an
   already synced and validated inode; `synced: false` after it.
4. **W1-V6-COMPOSED-STATE** (§11.4, §11.5): effect sets with co-effects, one global sequence, global vectors and
   their partial and co-object forms, for setup and rollback.
5. **W1-V6-IMAGE-PIN** (§3.4, §11.7, §14.5 J1): the images directory is root:W 0750 and listed at every use.
6. **W1-V6-C1-DATA** (§9.3 C1, C2; Appendix B.4.4): C1 checks compiled, argv and kernel facts only.
7. **W1-V6-SCAN-STATE** (§9.4, §9.8 N3, N4, N7): the census and CRED; the exact mount predicate; the unestablished
   premises named with their probes.
8. **W1-V6-COPY-PROBES** (§13): the copy route and L1 withdrawn; P-PTRACE complete; no probe promoted to a premise.
9. **W1-V6-INVARIANTS** (§4.1, §4.5, §6.1, §6.2, §11.7): no frame mutation of the admitted tree after M8; the no-ACL
   rule scoped; `adopt`'s exception exact.
10. **W1-V6-EVIDENCE-RESTORE** (§7.3, §8.5, §14.7, §15.3): payload packs, self-contained exports, A_pack.
11. **W1-V6-CATALOGUE** (§21): rewritten as the change requires.

### 0.4 The architecture decision, stated plainly

The review ruled that v6's K0 is a sound obstruction for the unprivileged userspace/DAC architecture and
already-shared writable open file descriptions, and not an impossibility theorem for every Linux enforcement design
(§22.2). The lead's instruction for v7: evaluate the designs beyond it; if one keeps the original success domain
fixed (no new refusal of an original accepted case, no observable output substitution, no cap), make it the design; if
none does, say so and keep V5-B01, V5-B02 and W1-V5-PRESERVATION OPEN without narrowing them.

**None does, as established.** §22 evaluates a root-built launcher with private namespaces (the lead's Option B,
extended), the unprivileged kernel scoping of this kernel (Landlock, seccomp, the exposure of `SCM_RIGHTS` and
`pidfd_getfd`) and the other routes the author could identify. v7 adopts the first with Landlock: the target view. It
admits outputs in place, unchanged, with no copy route, no `chmod` and no cap; it restores the original environment,
paths, ownership and release condition; and under the premises of §9.8 N7 no principal outside the attempt's own
process tree can obtain or keep a description of, or a name for, an admitted entry. It changes the target's world in
the twelve ways §12.3 lists (network, foreign UNIX servers, mounting, set-ID programs, host identity, unreproduced
mounts, private temporaries, the run directory, masks, the scope's manager, a lead preparation step, the Landlock
domain). Whether any of them can change an allowlisted action's observable result is the premise TOOL-CLOSURE
(§22.4), unestablished. **So V5-B01, V5-B02 and W1-V5-PRESERVATION stay OPEN.** v7 is a candidate design with a
complete inventory of its changes, for the independent reviewer and the operator; nothing in it narrows the criteria.

### 0.5 What is carried

The 29 v6 units marked CARRIED in §18.5 are carried byte for byte. Everything the gpt61-v6 review closed is carried in
substance:
- W1-DURABILITY-RELEASE: inside the replaced §9.4, the release procedure, hold, window-write and window-protocol
  paragraphs are v6's, and the release rule's condition 2 is restated as v5's terminal predicate (v6's D5 expansion
  is withdrawn under W1-V6-PRESERVE); Appendix B.4.4's `RELEASE` rows are unchanged;
- W1-SETUP-IDENTITY: §11.7's seal paragraph is carried with `adopt`'s exception stated exactly (W1-V6-INVARIANTS);
  §11.5's S-H and S-I follow the new setup objects; B.3's `generation.json` and `lead-adoption.json` rows are
  unchanged;
- W1-V5-PROTOCOL-REFUSALS: Appendix B.4.4's early refusal frames, every row's STOP column and C's refusal rules are
  carried; the W↔L and W↔C rows are amended for L's `exec` of C and for C1's narrowed checks;
- W1-RESOURCES, resources-and-images, W1-IMAGE-GEOMETRY and W1-IMAGE-COMPATIBILITY: §14.1 and §14.4 carried; §14.2,
  §14.3 and §14.5-§14.7 only raise;
- lease-and-writer-authority and W1-WRITE-AUTHORITY: §5.1 and §5.4 carried; §5.2 amended (no exchange, `tmpdir/`);
- per-entry-modes-acls (§6), exposure-options and W1-READ-EXPOSURE (§12: the exposure is the original's, R5),
  fresh-identities-and-vault and W1-PREFLIGHT-IDENTITY (§8.2 and §8.6 carried), W1-READ-ACCESS (§8.6), denial-probes
  and W1-VERIFICATION-PROBES (§13, same form), W1-SETUP-PRESTATE (§11.1-§11.3) and W1-SETUP-ORDER (§16): amended only
  as the view requires;
- W1-FINAL-PASS: §4.5's items 1-3 keep their substance, in the view;
- W1-NONCLAIMS: §20 amended; no non-claim is weakened.

No original admission join, control, accepted case, criterion, allowance, cap or gate is relaxed; where v7 differs
from the original frame, §12.3 and §21 say how.

### 0.6 Reading notes for carried text

- "v4", "v5" or "v6" in carried text names the design state it was written for; unless this §0, an amendment or a
  replaced unit says otherwise, the statement holds for v7 unchanged.
- §10.4 (carried): `fallback.journal` is created by a named create-only open and zero-filled before its allocation
  record is committed; it is not a temporary file, and §5.2's "no named temporary file" concerns records, markers and
  export copies.
- §4.4 (carried): the direction `RL2W` and its genesis are §7.3's.
- §8.2 (carried): "the helpers (W, W2, L, C, O, RL)" holds; RL is the root launcher of §12.2.
- §8.6 (carried): F's reads use `O_NOATIME` where `sicarii` owns the input (§4.2 M2, §9.8 N6).
- §9.4's carried hold paragraph and Appendix B.4's `RECOVERY_SCAN`: "scan" means an observation of v5's terminal
  predicate or of the census (§9.4); v6's scans are withdrawn.
- Appendices C, E and F (carried): their mentions of C9, the S-F drop-in, the user manager, masks and the copy route
  are historical; Appendix G holds v7's numbers and observations.

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

- **A1, concurrent `sicarii` processes** (other agents and sessions; uid 1000). They may run arbitrary code as
  `sicarii`, including user namespaces over `sicarii`'s delegated subordinate range 100000-165535 (start 100000, count
  65536; last id JACKAL exact, parsed `100000+65536-1`), FUSE mounts, reads of every dumpable `sicarii` process's
  `/proc` entries, signals to `sicarii` processes and to processes whose real uid is `sicarii`, writes to every
  `sicarii`-writable file (including the shared window file, the lead inbox and every frozen input under
  `/home/sicarii`), and invocations of the reviewed `sicarii`→`wlscratch` sudo rule with arbitrary arguments. They must
  not be able to create, rename, substitute, modify or delete any frame-owned location or the admitted generation, or
  cause the frame to mutate outside its tree. They may make themselves non-dumpable, so their descriptor tables are not
  assumed observable. v7 gives them no route to the generation: the generation root grants `sicarii` no search
  permission (§6.3), the target's processes run under another host uid (§3.2), and the target view offers them no
  channel through which a target could hand them a descriptor or a name (§9.8 N1-N4).
- **A2, the running target** (the allowlisted command and everything it starts, inside the target view of §12.2: host
  uid `wlscratch-run`, gid `wlscratch-gate`, supplementary groups those of the lead's process with 1000 replaced by
  `wlscratch-gate`, seen inside its user namespace as uid 1000, gid 1000 and the lead's groups; a private network
  namespace; a mount namespace that shows the host filesystem through idmapped mounts with `sicarii`'s on-disk
  authority, the generation's `source/` at the original run path, and a private `/tmp` and `TMPDIR`; a Landlock
  domain). It may do anything the view permits: write wherever `sicarii` can write in the view, change the modes and
  ACLs of everything it owns (set-ID bits included; every mount of the view is `nosuid`), use `io_uring` and `openat2`,
  create user and network namespaces, pass descriptors among its own processes, and leave processes running in its
  scope. It cannot connect to a UNIX server created outside its Landlock domain, create a socket file outside its
  private places, mount or unmount anything, reach the protected tree except its own `source/`, `tmp/` and `tmpdir/`,
  or leave its scope. It must not be able to mutate frame records, the frame's location chain, another generation or
  another attempt's evidence, and nothing it does may let a principal outside its own process tree hold or obtain a
  description of an admitted file, or a name for one (§9.8).
- **A3, every other non-root principal of the host** (other users' processes and system services that do not run as
  root). They hold no credential that reaches the generation and no channel into the target view (§9.8 N1-N4). v6's
  A3, the target account's user manager, does not exist in v7: `wlscratch-run` has no user manager, no linger and no
  PAM session (§3.2, §11.5).

### 2.2 Trusted base (outside the threat model)

Root and everything running as root (sudo, systemd and logind, PAM, sshd, the kernel, the root launcher RL of §3.2 and
§12.2); root-owned installed files (`/usr`, `/etc`, the installed frame under `/opt/wlscratch`); the kernel's
namespace, idmapped-mount, Landlock and cgroup implementations, whose relied-on behaviour is stated as premises with
probes (§9.8 N7); the Python 3.14.7 runtime under `/usr/lib/python3.14` (interpreter `/usr/bin/python3.14`, sha256
observed by v2 as `c6bc1ef497b896b7575c546b13f9bafe52e2066f184fdd3fec6af4b5b6349947`); the operator's credential. The
design gives no protection against root, against kernel defects or against a compromised operator credential.

### 2.3 Preconditions (checked at setup, §11.3; their failure refuses setup)

- **No privilege route for `sicarii`.** Apart from the reviewed frame rule, no route lets a `sicarii` process run as
  root, `wlscratch`, `wlscratch-run` or with `wlscratch-gate` without the operator's interactive credential: no
  `NOPASSWD` sudo rule yielding root or those identities, no polkit rule granting `sicarii` (or a group it is in) a
  passwordless `YES`, the `empower` group empty, no membership in `docker` in any running session, no file capability
  or setuid/setgid binary owned by the new identities. An unprivileged process cannot read `/etc/sudoers` (0440),
  `/etc/sudoers.d` (not listable) or `/etc/polkit-1/rules.d` (not listable); the drafting author observed those
  refusals on 2026-10-04, so this inventory is operator-produced. Observed by the drafting author on 2026-10-04:
  `/etc/group` lists no member of `docker` or `empower`, and the drafting session's own process had supplementary
  groups 954, 955, 956, 982, 983, 992, 995, 998, 1000 (no `docker`).
- **Kernel settings** as observed: `fs.protected_hardlinks=1`, `fs.protected_symlinks=1`, `fs.protected_regular=1`,
  `kernel.yama.ptrace_scope=1`, `/proc` mounted without `hidepid`, cgroup2 with `nsdelegate`, `fs.suid_dumpable=2`,
  `user.max_user_namespaces=128053`. v6's lease test is withdrawn, so `fs.leases-enable` is recorded but no longer
  required.
- **Kernel features the target view needs** (observed 2026-10-05, Appendix G; each is also a premise with a probe,
  §9.8 N7): the running kernel is `7.2.6-1-aarch64-ARCH`; the active LSMs are `capability,yama,landlock`; its build
  configuration sets `CONFIG_USER_NS`, `CONFIG_NET_NS`, `CONFIG_PID_NS`, `CONFIG_IPC_NS`, `CONFIG_SECURITY_LANDLOCK`
  and `CONFIG_FANOTIFY_ACCESS_PERMISSIONS` and does not set `CONFIG_BPF_LSM`, `CONFIG_SECURITY_SELINUX` or
  `CONFIG_SECURITY_APPARMOR`; the installed `linux-api-headers` 7.2 define `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` (Landlock
  ABI 9), `LANDLOCK_ACCESS_FS_MAKE_SOCK`, the scope flags and `MOUNT_ATTR_IDMAP`; cgroup2 offers the controllers
  `cpuset cpu io memory hugetlb pids rdma`; systemd is 261.
- **One local filesystem.** Observed: `/`, `/var/lib`, `/opt`, `/tmp`, `/var/tmp` and `/home` are all on `/dev/vda`
  ext4, in one mount (mount ID 32, `relatime`); `/run`, `/dev/shm` and `/run/user/1000` are tmpfs mounts. v7 relies on
  `EXDEV` only between the distinct mounts of the target view, which RL creates (premise P-XDEV, §9.8 N7); the rename
  and link probes of §13 use same-mount operands, and with images T lies on separate mounts (§14.5).

### 2.4 Residuals (stated exactly; none is a new accepted exception)

- **R1, the lead's own processes.** W-1 does not protect `sicarii` processes from other `sicarii` processes. Yama
  `ptrace_scope=1` stops non-ancestor attach; read-mode `/proc` access is not covered by Yama, so each frame process
  sets itself non-dumpable as its first effective act (§7.7). Before that call there is a pre-first-call window. This
  is an explicit inability carried from frame v5, where the whole frame ran as `sicarii`; it grants no acceptance.
- **R2, lead authentication.** The frame authenticates the lead only through the reviewed v5 admission protocol:
  frame review and adoption joins, the fresh lead observation, the actual-MCP JACKAL challenge and receipt (N01: a
  lead obligation), and window ownership. Private pipes, the channel chain and the sudo rule add integrity and
  ordering, not sender authentication (§7.6). This is the original v5 engineering ceiling, carried exactly, not a new
  accepted residual. All original joins are implemented.
- **R3, the running target.** No confinement of the running target outside the generation: the ruled
  `no-target-confinement` residual (ACCEPTABLE_AS_DOCUMENTED at the reference ceiling). It covers target writes only,
  never a frame write and never an unsafe alias at final admission. v7 gives the target the original file authority of
  `sicarii` through the view (§12.2): it can write what `sicarii` can write, except the masked W-1 trees and with a
  private `/tmp` and `TMPDIR`; the inventory of §12.3 states the differences.
- **R4, the toolchain.** The target executable is identity-checked and then executed by path (ruled
  ACCEPTABLE_AS_DOCUMENTED). The toolchain under `/home/sicarii/opt/gnat` stays `sicarii`-owned and `sicarii`-writable,
  and the target can write it through the view as in the original; its closure is observed before and after. W-1
  claims no custody of it.
- **R5, exposure.** The target reads what `sicarii` reads (the original exposure), except the masked W-1 trees; the
  view's construction is privileged code (RL, §12.2), reviewed and installed by the operator.
- **R6, availability.** A `sicarii` process can stop an attempt: it can kill the front, signal processes whose real
  uid is `sicarii` (which may include the sudo front-ends, so a signal may be relayed to a frame helper), or modify
  the cooperating window file (N07). The result is an interrupted, non-success attempt or a held window, never a
  custody change. Whether sudo relays such signals is a probe item (§13, P-SIG). A target process that stays alive in
  its scope keeps the window held until it ends, as in the original (`owned_terminal`, S:1375-1415).
- **R7, `(sd-pam)` (withdrawn with the user manager).** v4-v6 needed a PAM-less user manager for `wlscratch-run`; v7
  has no user manager for it at all (§3.2), so no `(sd-pam)` helper and no manager state exist to classify.
- **R8, root and the kernel** (§2.2).
- **R9, descriptors in transit and retained references (closed by the view).** A scan of descriptor tables cannot see
  a descriptor queued in a socket or held by a non-dumpable process, and v7's custody conclusion needs none: no
  principal outside the target's process tree can hold or obtain a description of an admitted file, because the view
  gives the target no channel to such a principal and gives such a principal no access to the target (§9.8 N1-N4);
  every descriptor the target's processes hold, queued or not, is released when the last process of its scope ends,
  which the kernel reports atomically (§9.4). v4's and v5's arguments, v5's write revocation and v6's lease test and
  copy route are withdrawn.

## 3. Principals, accounts and layout

### 3.1 Accounts and groups (three new identities)

| Identity | Kind | Purpose | Members |
|---|---|---|---|
| `wlscratch`, uid = gid = W | user + user-private group | The only writer of generation trees | none besides the user |
| `wlscratch-run`, uid = gid = R | user + user-private group | The host uid of every process RL starts inside a target view (L, C, O, T; §3.2); no user manager, no linger, no login | none besides the user |
| `wlscratch-gate`, gid = GATE | group only | The host primary gid of every process RL starts; no file, directory or ACL entry carries it (§6.3, §12.2); no process outside RL's scopes holds it (§9.4) | none in `/etc/group` |

Candidate numbers: W = 950, R = 951, GATE = 952. As observed on 2026-10-04 they are unused by every passwd and group
entry (the lowest used system uid is 957 and the lowest used gid at or above 900 is 954), inside `SYS_UID_MIN`-`SYS_UID_MAX`
500-999 of `/etc/login.defs`, and outside every range in `/etc/subuid` and `/etc/subgid`. They are candidates; §11.2
fixes the policy and the prestate re-verifies them. Counts: new users 2 (JACKAL exact, parsed `1+1`); new groups 3
(JACKAL exact, parsed `1+1+1`: the two user-private groups and `wlscratch-gate`).

The v1 `wlscratch-clients` group is not used. `sicarii` gets no new group membership and no new login.

### 3.2 Roles (processes)

| Role | Process and credentials | Started by | Code |
|---|---|---|---|
| F, front | the lead's real outer invocation `/usr/bin/python3 -B /opt/wlscratch/frame-v6w1/front.py <verb> …`, uid 1000; verbs `adopt`, `materialize`, `dispatch` | the lead | installed, root-owned |
| S1 | `sudo -n -u wlscratch -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py <verb> …` | F | `/usr/bin/sudo` |
| W, writer | `writer.py`, uid/gid W; verbs `adopt`, `materialize`, `dispatch`, `selftest` | S1 | installed |
| S2, S_O | `sudo -n -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py <verb> …` (the RL rule, §11.5 S-D) | W or W2 | `/usr/bin/sudo` |
| RL, root launcher | `sandbox_launch.py launch …` or `observe …`, root: checks its invocation, creates the scope with `systemd-run --scope` in the system manager, builds the target view (§12.2), sends `RL_IDENTITY` and starts L (`launch`) or O (`observe`) inside the view | S2 or S_O | installed, privileged |
| L, launcher | `launch_target.py launch …`, host uid R, gid GATE, supplementary groups G_V (the lead's, with 1000 replaced by GATE, §12.2), inside the view, in the attempt scope | RL, which `exec`s it in place | installed |
| C, in-scope child | `launch_target.py child …`, the same pid, credentials, view and scope as L | L, which `exec`s it in place after `GO`, so that U holds only C and its descendants, as v5's scope held only its child and the target | installed |
| U, scope | transient `wlscratch-<g12>-<A>.scope` of the system manager under `wlscratch.slice`, with `MemoryMax=8G` and `MemorySwapMax=0` | RL, through `systemd-run --scope` | systemd |
| T, target | the exact allowlisted command, the same credentials, view and scope; inside its user namespace uid and gid 1000 | C | toolchain |
| O, observer | `launch_target.py observe …`, host uid R, gid GATE, groups G_V, in its own scope `wlscratch-o-<g12>-<A>-<n>.scope` under `wlscratch.slice` and an observer view (§12.2) | RL, for W (parent and after stages) or W2 (recovery) | installed |
| S3 | `sudo -n -u wlscratch -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py seal-front …` (the S1 rule) | F | `/usr/bin/sudo` |
| W2, post-writer | `writer.py seal-front <N_F> <g> <A> <mode>`, uid/gid W; mode `seal` after W ended with `FINAL`, mode `recover` after W died or its channel failed (§9.7) | S3 | installed |

`<g12>` is the first 12 hex digits of the generation id; `<A>` is the v5 attempt stamp (`STAMP_RE`). The installed
frame carries two compiled path constants besides `install_root`: `SOURCE_FRAME`, the frozen v6-W1 source directory in
the lead's tree, and below it the sealed review directories `REVIEW` (`<SOURCE_FRAME>/review/gpt61-v1`, code review)
and `INSTALLED_REVIEW` (`<SOURCE_FRAME>/review/installed-gpt61-v1`, installed-evidence review) (§4.6, §16).

v6's user manager M, its drop-in and masks, its linger file, Option A's direct `-g` launcher rule and the
`systemd-run --user` scope are withdrawn. Every process with host uid R or gid GATE is started by RL inside a scope
under `wlscratch.slice` and stays in that scope's cgroup, which it cannot leave (§9.4, premise P-CG).

### 3.3 Layout

The layout is the same with and without optional images (§3.4, §14.5).

```
/var/lib/wlscratch                     root:W        writer home (setup)
  lease/                               root:W        setup; writer-only traverse
    writer.lock                        root:W 0440   setup; flock-only
  runs/                                W:W           T_root: root of the protected run tree T (setup); work-image mount point
    <g>/                               W:W           generation root g (writer-created at M4), g = 32 lowercase hex; no sicarii search
      generation.json                  initial generation record                               [P_adm]
      commits/                         generation journal (P_adm markers)                      [P_adm]
      inputs/                          streamed input records + manifest.json                  [P_adm]
      overlay-snapshot/                v5 overlay snapshot (0700 dirs, 0600 files)             [P_adm]
      source/                          admitted recipe (exact recipe modes)                    [P_adm; the target's outputs below it]
      tmp/                             the view's /tmp (M7, 01777)                             [P_adm: directory only]
      tmpdir/                          the view's TMPDIR (M7, 0700)                            [P_adm: directory only]
      materialization.json             v5 schema plus §4.3 fields                              [P_adm]
    records/                           W:W           R_root: record root of T (setup); records-image mount point
      <g>/                             W:W           g_rec, record root of g (writer-created at M4)
        attempts/<A>/                  P_att(g, A): attempt.json, commits/ (attempt journal), fallback.journal,
                                       fallback-allocation.json, inputs/, front/, channel/, w2-<k>/,
                                       stream files, observer files, every v5 attempt record
        export/                        P_exp(g): generation/ (with its payload pack), <A>/inc-<n>/
      adoption-<I>/                    W:W           P_ado(I), installed-frame adoption root (writer-created by `adopt`)
        lead-adoption.json, commits/ (adoption journal), invocations/<stamp>/, export/inc-<n>/
    selftest-<h>/                      W:W           sacrificial selftest generation root (§13)
    records/selftest-<h>/              W:W           its record root
/etc/systemd/system/wlscratch.slice    root:root 0644 the slice of every RL scope (setup, S-F)
/etc/tmpfiles.d/wlscratch.conf         root:root 0644 age-based cleanup of every g/tmp (setup, S-F)
/opt/wlscratch/frame-v6w1/             root:root     installed frame (member-exact)
/opt/wlscratch/setup-identities.json   root:root 0644 setup identity record (§11.5 S-H, §11.7)
<RUNS>/<label>/source/                 sicarii       created empty by the lead before the generation's first dispatch;
                                                     RL binds g/source over it only inside a view's private mount
                                                     namespace (§12.2)
```

`I` is the sha256 (64 lowercase hex) of the installed `frame-inventory.json`; `h` is 32 lowercase hex. Exact modes and
ACLs are in §6.3. `<RUNS>` is v5's `RUNS` (`/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/
work/claude-scratch-runs-v5`), which did not exist on 2026-10-05 (Appendix G). v5's own `materialize` created `<RUNS>`,
`<RUNS>/<label>` and `<RUNS>/<label>/source` as ordinary `sicarii` directories (S:977-999); in v7 the lead creates them,
empty, before the generation's first dispatch, and the frame never writes them. Through the root view (§12.2) the
target sees the lead's real `<RUNS>` and `<RUNS>/<label>`, with only `source/` replaced by the bind of g/source. W
refuses a `materialize` whose label an existing generation of T already carries (v5's "run already exists").

### 3.4 The protected intended run tree, its anchors and routing [corrections: W1-V6-IMAGE-PIN, W1-V6-INVARIANTS; v4: W1-IMAGE-TREE]

**Definition.** The protected intended run tree T is the directory tree rooted at T_root = `/var/lib/wlscratch/runs`,
including its record root R_root = `/var/lib/wlscratch/runs/records` and every mount at or below T_root that
`setup-identities.json` lists. Every component from `/` to T_root is root-owned and writable only by root (`/`, `/var`,
`/var/lib` root:root 0755; `/var/lib/wlscratch` root:W 0750 with search-only ACL entries). Inside T only W can create,
rename or remove entries, except that the processes of a target view can do so below `g/source`, `g/tmp` and
`g/tmpdir` of their own generation, which RL binds into the view with idmaps (§12.2). No principal other
than W, root and those processes can search g (§6.3). T is the categorical writer tree of §5.2: no writer verb writes
anywhere else, in any configuration.

**Anchors.** Every writer and helper reaches T only by anchored descriptor chains (v5 `Dir.anchor`, `O_DIRECTORY|
O_NOFOLLOW` per component, from `/`):
- `A_T` = T_root; `A_R` = `A_T` + `records`, opened from the held `A_T` descriptor;
- per generation: g = `A_T` + `<g>`, g_rec = `A_R` + `<g>`;
- per adoption: P_ado(I) = `A_R` + `adoption-<I>`;
- per selftest: `A_T` + `selftest-<h>` and `A_R` + `selftest-<h>`.
Each anchor's pinned identity (§11.7) is compared with `setup-identities.json` before any use: both anchors at every
writer invocation, and `A_T` and g at every RL invocation before RL builds a view. L, C, O and T never traverse T by
path: RL hands them their generation's `source/`, `tmp/` and `tmpdir/` as mounts of the view. g, g_rec and P_ado(I)
are compared with the identities committed when they were created (`generation.json`, the adoption journal).

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
| `generation.json`, `inputs/**` (materialize), `overlay-snapshot/**`, the recipe, `tmp/` and `tmpdir/` (M7), `materialization.json` | g (P_adm; the contents of `tmp/` and `tmpdir/` are target temporaries, never admitted, §4.1) | generation journal `g/commits/` |
| `attempt.json`, `fallback-allocation.json`, every attempt record, stream files, observer files, front records, channel segments, recovery records, W2 records, release records | g_rec `/attempts/<A>/` (P_att) | attempt journal `g_rec/attempts/<A>/commits/` |
| `fallback.journal` slots | g_rec `/attempts/<A>/fallback.journal` | none: described by `fallback-allocation.json`; slots are self-validating (§10.4) |
| generation export with its payload pack | g_rec `/export/generation/` (P_exp) | attempt journal of the materializing attempt A0 |
| attempt exports | g_rec `/export/<A>/inc-<n>/` (P_exp) | attempt journal of A |
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
  builds a view; L, C, O and T never see the images directory (§12.2).
- `A_R` must be the root of the records image, checked the same way, and its mountinfo parent ID must equal the work
  image's mount ID (the records image is mounted inside T, on the work image).
- If an image is not mounted, the path resolves to its bare mount point: root-owned, mode 0700, empty, on the parent
  filesystem. Its `st_dev` equals the parent's, so the check refuses before any mutation, and W could not create
  anything in it anyway. The loop device number and mount ID may change across boots; they are observed, never pinned
  (§11.7).

**No new outside-tree authority.** Every writer mutation lies in T. The adoption record, which v5 wrote into the
frame's own review directory outside its run tree as a prescribed preparation record, now lies inside T (§4.6). F
writes nothing. RL mounts only inside the private mount namespaces it creates, writes only the maps and settings of the
namespaces and processes it creates, and asks the system manager for the scope; it writes no file outside T (§9.8 N5).
The only frame writes outside T remain v5's window protocol by F, unchanged (N07).

## 4. Generation order and record partitions [correction: W1-GENERATION-PROTOCOL; gap: generation-order]

### 4.1 Partitions [correction: W1-V6-INVARIANTS]

- **P_adm(g), the admitted generation partition**, in g: `generation.json`, `commits/` (the generation journal),
  `inputs/**`, `overlay-snapshot/**`, every recipe object under `source/` (files, directories, their modes and
  contents), the directories `tmp/` and `tmpdir/` themselves (not their contents; for `tmpdir/` only its `[dev, ino]`,
  because its mode and ACL become the target's, as `TMPDIR` was the target's in v5) and `materialization.json`. The
  frame writes P_adm only in
  the `materialize` invocation that creates g. After that invocation's final verification and the materialization
  marker (§4.2, M8), no writer verb has any path that mutates P_adm: no verb rewrites, renames, deletes, chmods or
  re-ACLs an existing P_adm object. The only other process that can change the recipe is the target of a launched
  attempt, during its run and through its view, where it owns `source/` as it owned its run tree in v5 (§12.2): v5's
  conclusion detects every change of a recorded file or directory (S:1684-1691, `verify_materialization`), the
  attempt is non-success, and every later admission refuses the changed generation, exactly as in v5 (§21).
- **Partition contents.** The output partitions are v5's (`obj/`, `lib/`, `resource-tests/obj/`,
  `resource-tests/bin/` below `source/`, S:79). The target creates them and everything below them, as in v5:
  `materialize` creates none, and v5's own rule requires that none exists at materialization (S:1033). The frame never
  writes, renames, deletes, or changes the mode, ACL or owner of, any entry below `source/` after M8; it reads them only
  through a view, with `O_NOATIME` (§9.8 N6). They are part of what each later attempt admits, so every attempt
  re-observes them in full (§4.5).
- **Target temporaries**, below `g/tmp/` (the view's `/tmp`) and `g/tmpdir/` (the view's `TMPDIR`,
  `/home/sicarii/.cache/workflow-tmp`) (§12.2). Never read, walked, admitted or exported by the frame. Below `g/tmp/`
  they are removed only by root's age-based tmpfiles rule, with the age `/tmp` has on this host (§11.5 S-F); below
  `g/tmpdir/` nothing removes them, as nothing removed them from v5's `TMPDIR`. An attempt sees what earlier attempts
  of the same generation left there, but not what other generations' targets or other `sicarii` processes put in the
  shared `/tmp` and `TMPDIR`, which it saw in v5; and they no longer see its files (a change, §12.3).
- **P_att(g, A), the attempt bookkeeping partition**, in g_rec `/attempts/<A>/`. Every writer invocation that creates
  an attempt has one: the creating `materialize` invocation (A0, kind `materialize`) and every `dispatch` invocation
  (kind `dispatch`). It is created and written by that W; afterwards only W2 instances of the same attempt append to
  it, each only in new names below its own `w2-<k>/` and in the attempt journal (§5.2, §9.7).
  Create-only. The target never reads it and cannot reach it (§12.2): launch records reach C over its channel
  (§7.1), and target streams are passed as open descriptors (§6.4).
- **P_exp(g), the export partition**, in g_rec `/export/`. Writer-produced read-only copies of committed records and,
  for the generation, of the recipe and snapshot payload, for the lead. Create-only. Never read by the target, never
  an admission input.
- **P_ado(I), the adoption partition**, in R_root `/adoption-<I>/`: the installed-frame adoption record, the adoption
  journal, per-invocation bookkeeping and the adoption exports (§4.6). Written only by W in `adopt`; create-only; read
  by W at every dispatch.

The partitions are disjoint. Every frame mutation after a generation's creation lands in a P_att, a P_exp or a P_ado,
never in P_adm, the partition contents or the target temporaries. v6's P_out, its fresh and retired roots and its
root exchange are withdrawn with the copy route, so no frame mutation of `source/` or of any directory above an
admitted entry remains after M8.

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
  records (joined), the two provenance triples (event stream, exec-argv record, rollout) (joined), the `scratch-adopt`
  lead observation (observation) and F's adoption body (joined).
- AD5. State `COMMIT`: W verifies (§4.6), including the seal comparison of §11.7, and, only if every join holds,
  commits `lead-adoption.json` and its marker in the adoption journal; `ADOPTED`. Otherwise `REFUSAL`, and no adoption
  record exists.
- AD6. State `EXPORT`: the adoption export increment (§15.3), `EXPORTED`. State `FINAL`: `FINAL`, `BYE`; W closes and
  exits.
- AD7. F waits for S1 and exits by §10.7. No W2 runs for `adopt`; F's terminal facts are its console output, as v5
  `adopt` had no terminal record.

The adopt invocation runs only after a procedural Gate 0 receipt computed with the materialize/dispatch-stage
expression (§14.3, raised by §14.7), and its retained bytes are counted under A_in (§14.2). It reserves nothing and
launches nothing.

**Generation creation (`front.py materialize <label> <overlay-dir>`; v5 `materialize`).**

- M1. F starts (§7.7 first act), records its identity (§8.1), validates its argv grammar (`label` matches v5
  `NAME_RE`; `overlay-dir` absolute).
- M2. F reads, through the v5 anchored readers, the base descriptors (`source-binding.json`,
  `source-inventory.json`, `source-directory-modes.json`), observes `BASE/source` against the pinned inventory
  (`observe_tree`, as v5 `base_tree`), and observes and reads the overlay directory (`observe_tree` + `read_files`,
  as v5 `materialize`), opening every file it reads, all `sicarii`-owned, with `O_NOATIME` (§9.8 N6). F writes
  nothing.
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
  No output partition is created (v5, S:1033). Then `tmp/` is created (0700, authenticated) and set to mode 01777 by
  `fchmod` on the held descriptor, and `tmpdir/` is created (0700, authenticated), both with no ACL.
- M8. W verifies with a full walk of `source/` and of the snapshot: recipe content and modes equal the recipe, and no
  output partition exists (v5's rule, S:1033); `tmp/` is empty with mode 01777 and `tmpdir/` empty with mode 0700, both
  with no ACL. W then writes
  **`materialization.json`** (§4.3) and its marker, runs `verify_materialization` against the committed record, and
  re-verifies the location of every held handle. **This is the frame's last mutation of P_adm(g), ever.** The
  generation journal ends with this marker and never grows again.
- M9. Still in `MATERIALIZE`: W writes the generation export (`g_rec/export/generation/`, §15.3): the whole generation
  journal and every record it commits (`generation.json`, the input records and manifest, `materialization.json`), a
  finite prefix ending at the materialization marker, and the **payload pack**: one export copy of every recipe file
  and every snapshot file, read back by W from P_adm (W-owned, opened with `O_NOATIME`) and listed in the manifest with
  its relative path, sha256 and size, so that every channel and record reference into the recipe or the snapshot
  resolves inside the exports (§7.3, §15.3; correction W1-V6-EVIDENCE-RESTORE). Its export markers go to A0's attempt
  journal; W sends `MATERIALIZED`.
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

- D1. F starts, records its identity, validates `action`/`args` against v5 `ACTIONS`/`command()` grammar and anchors
  the lead-created inbox (`sicarii`-owned, mode 0700, empty).
- D2. F creates its two channel pipes and starts S1 → W (`writer.py dispatch <N_F> <g> <action> [args]`).
- D3. W starts, takes the lease, anchors A_T and A_R with the missing-mount checks, opens g and g_rec by anchored
  chains; requires the committed markers of `generation.json` and `materialization.json` in the generation journal
  and equality of the P_adm identities with them, `tmp/` and `tmpdir/` included (`tmpdir/` by `[dev, ino]` only);
  requires the committed adoption record
  `P_ado(I)/lead-adoption.json` of the installed inventory I with its marker in the adoption journal (otherwise it
  refuses: the installed frame is not adopted); requires `setup-identities.json` to match the seal that adoption
  record carries, and the setup identity recorded in `generation.json` to equal it (§11.7; otherwise it refuses before
  any mutation); creates `g_rec/attempts/<A>/` with its `commits/` (0700, authenticated); commits **`attempt.json`**
  (kind `dispatch`); creates `fallback.journal` and commits **`fallback-allocation.json`**. State `HELLO`: `W_HELLO`.
- D4. F answers `HELLO_ACK`; W commits `front/front-identity.json`.
- D5. State `INPUTS` (phase `dispatch`): F streams the lead module (pinned); W verifies it and commits it as
  `attempts/<A>/inputs/<seq>-lead-module`.
- D6. State `ADOPTION`: W sends the committed adoption record's descriptor, marker digest and bytes
  (`ADOPTION_RECORD`).
- D7. State `FRONT_PARENT`: `STAGE_REQUEST {stage: front-parent}`; F performs its parent-stage half (§8.1): fresh lead
  observation (`claude_lead.observe('scratch-run', …)`), the front part of frame admission (installed-inventory pin
  against both reviews and the delivered adoption record; rollout joins; adoption observation and transcript prefix;
  §4.6), base-tree re-observation, its own runtime and manager identity, and the front half of the `preflight`
  sample (sibling units in `sicarii`'s manager, `storage_status.py`). `STAGE_RESULT`; W commits
  `front/front-stage-parent.json`.
- D8. State `PARENT`: the writer half (record pins, location, the attempt-journal join of §10.6, and the census of
  `wlscratch.slice`, §9.4: every scope under it absent or depopulated); then the observer for the parent stage: W
  creates and syncs the observer stream files, commits `observer-intent-1.json` binding them (§9.3, G0) and starts
  S_O → RL → O, and W commits `observer-1-rl-identity.json` before its request. O, inside its observer view: takes the
  parent-stage observations of §9.4 (the census; no process with host uid R or gid GATE outside the scopes of
  `wlscratch.slice`; no process naming g); takes the full walk of the view's `source/` with the original walk rules
  and v6's final pass, with every excluded leaf's `stat_key`, every file and directory opened with `O_NOATIME`; takes
  the target-context identities `parent` in its view (§8.4); and takes the helper half of `preflight` (heavy
  processes, meminfo). W commits `observer-1-parent.json` and `observer-wait-1.json`. A failed join, a refusal by an
  original walk rule, or a census or credential-closure observation that fails or is UNKNOWN refuses the attempt
  (nothing reserved).
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
  W's stream finality record (§10.6); `result.json`. State `CONCLUDE`: `CONCLUSION`.
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
  `generation.json` and its marker), `inputs_manifest` (pin), `tmp_dir` (path, `[dev, ino]`, mode), `tmpdir_dir`
  (path, `[dev, ino]`), `run_path` (the view path `<RUNS>/<label>/source` of §12.2), `recipe_mode_property` (§6.1),
  `channel_heads`. Its schema name becomes `wlscratch-materialization-v2`; the v5 `run` field becomes the generation
  root path.
- **`attempts/<A>/attempt.json`**, two exact schemas. Kind `materialize` (`wlscratch-attempt-materialize-v1`): its
  `generation_pins` are exactly `{generation, generation_marker}`, because `materialization.json` does not exist yet.
  Kind `dispatch` (`wlscratch-attempt-dispatch-v1`): its `generation_pins` are exactly `{generation,
  generation_marker, materialization, materialization_marker}`, and it adds `adoption` `{record, marker}`, the
  committed adoption record W read at D3. Both kinds: W's identity and invocation, the lease identity, the channel
  genesis, the front-process triple read by W from `/proc` as the grandparent of W through S1 (§9.2, used by W2), the
  boot id and the verb and arguments. Each binds nothing that does not yet exist.
- **`fallback-allocation.json`**: the immutable descriptor of the attempt's fallback journal (§10.4).
- **`inputs/<seq>-lead-module`** (P_att, `dispatch` only): the streamed lead module.
- **`front/front-identity.json`, `front/front-stage-<stage>.json`**: F's identity and its stage halves (stages
  `parent`, `vault`, `child`, `after` for `dispatch`; `vault` for `materialize`).
- **`writer-half-parent.json`, `writer-half-child.json`**: W's own halves of the parent stage (D8) and the child stage
  (C4).
- **`observer-intent-<n>.json`**: committed before each observer start, after its stream files exist: O's argv (with
  its nonce) and RL's argv, the stage, the `[dev, ino]` of `observer-<n>.stdout` and `observer-<n>.stderr`.
  **`observer-<n>-<stage>.json`** and **`observer-wait-<n>.json`**: O's results (stages `parent`, `after`, `recover`)
  and S_O's wait. **`launcher-rl-identity.json`** and **`observer-<n>-rl-identity.json`** (the latter also under
  `w2-<k>/`): RL's `RL_IDENTITY` frame (§7.3), committed before W sends `GO`, or its first `OBSERVE_REQUEST`, to the
  helper RL started.
- **`launch.json`** (v5 schema plus): `generation`/`attempt` pins; the pin of the admitted parent observation (§4.2
  D11; files, directories, identities and every excluded generated leaf's `stat_key`, §4.5); the view specification
  (§12.2: mounts, idmaps, user-namespace maps, network namespace, Landlock rules, credentials) and its sha256; the
  target environment, which is v5's (§8.4); the exact RL, L and C argv templates; the stream-file names; the unit name;
  the front stage-record pins. v5 fields kept unchanged in meaning: `action`, `args`, `child_argv`, `cwd` (the view's
  run path), `directory_identities` (run = g, attempt, source, snapshot, `source_tree`), `unit`,
  `scope_argv_template` (RL's `systemd-run --scope` template), `scope_argv_tail`, `environment`, `frame_inventory`,
  `review`, `adoption` (the descriptor of the protected adoption record, §4.6), `materialization`,
  `storage_reserve_bound`, `holder`.
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
- **Export increments** (`export/<A>/inc-<n>/manifest.json`, `freeze.json` and the copies; the generation export
  with its payload pack): §15.3.
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
   criterion-required repair of V5-B01, not part of v5's behaviour (§21 separates them). Through RL's idmap C is the
   owner of every entry below `source/` (§12.2), so it opens every file and directory it reads with `O_NOATIME`
   (§9.8 N6).
2. The observation (files, directory modes, identities and every excluded generated leaf's `stat_key`) must equal the
   admitted parent observation sealed in `launch.json` exactly (§4.2 D11). A difference in any recorded or excluded
   leaf refuses the launch. (v5 compared directory identities only; the excluded-leaf comparison is the criterion's
   addition and an engine change to `observe_tree`, which must return the excluded leaves' keys it already computes.
   Against v5 this comparison is a new refusal; under §9.8's custody nothing but root, W and the attempt's own frame
   helpers can change the generation between the two walks, so it fires only if a premise of §9.8 N7 failed or one of
   those misbehaved, §21 D7.)
3. Then C takes the child-stage observations of §9.4 (its scope holds exactly C; every other scope under
   `wlscratch.slice` is absent or depopulated; no process with host uid R or gid GATE exists outside those scopes),
   re-verifies the location of its held handles, reaches the interruption point (pending-signal check) and spawns with
   `fchdir` on the held `source` descriptor (v5 `spawn`).

This pass follows (a) the frame's last mutation of P_adm(g) (M8, at generation creation; v7 has no later frame
mutation of `source/` or of any directory above an admitted entry), (b) the commit and delivery of every record C's
admission depends on (`launch.json`, `admission.json`, `launcher-intent.json`, the adoption record) and (c) the
`SPAWN_OK` of §9.3. Every frame write after it goes to P_att(g, A) or P_exp(g): `child-start.json`, waits, the
conclusion. Those partitions are disjoint from P_adm and the partition contents, lie under a record root the target
cannot reach (§12.2), and the target never reads them. **So "the final pass runs after the last frame mutation of the
admitted generation" is exact, and the remaining frame writes are bookkeeping by construction, not exceptions.**

Custody from the final pass to `exec` (V5-B01, second sentence) rests on these facts, each with its own section:
(i) no principal other than root, W and the attempt's own frame helpers holds a description of, or a name for, any
entry of the admitted generation, and none can obtain one: g grants no other principal search permission (§6.3); every
earlier target's scope is depopulated, so every description its processes held, queued or not, is released (§9.4);
and no target view gives its processes a channel to a principal outside their scope or such a principal a way into
the view (§9.8 N1-N4);
(ii) W does not mutate P_adm after M8, and any other writer instance refuses before its first mutation and before
starting any helper while W holds the lease (§5.1, §5.2);
(iii) the processes that hold host uid R or gid GATE are exactly the processes RL starts, inside scopes under
`wlscratch.slice` that they cannot leave (§9.4 CRED; premises P-CG and P-NOR);
(iv) at the final pass, by C's own observations: the attempt scope holds exactly C, and every other scope under
`wlscratch.slice` is absent or depopulated (§9.4);
(v) that state is absorbing until T's `exec`: a process can enter `wlscratch.slice` only through RL, which only W
starts, under its lease (§5.2); a depopulated scope cannot repopulate, because no process remains in it to fork and
only root can move a process into it (premise P-CG); outside principals have neither path, description nor channel
(i); C, which L became by `exec`, is frame code;
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

**What the record binds** (`wlscratch-lead-adoption-v1`, Appendix B.3): every key of v5's
`claude-scratch-frame-lead-adoption-v5` record (`at`, `frame` = INSTALL_ROOT, `lead_id`, `frame_inventory_sha256` = I,
`review_sha256`, `review_freeze_sha256`, `review_report_sha256`, `mismatches` = `[]`, v5's provenance keys for the
code review (`reviewer_thread`, `rollout`, `turn_contexts`, `session_providers`, `exec_argv`, `exec_argv_record`,
`event_stream`, `rollout_final_message_sha256`, `rollout_final_timestamp`), `lead_observation`, `truth_boundary`), plus
`source_frame` (SOURCE_FRAME), `setup_identities_sha256` (S) and `installed_review` (the same review, freeze, report
and provenance keys for INSTALLED_REVIEW).

**Joins at adoption** (none of v5's is dropped; the installed-review joins are added):
1. Code review (REVIEW): v5 `review_profile_problems` against the compiled `REVIEW_PROFILE`, with `candidate` =
   SOURCE_FRAME (the frozen tree it reviewed), `lead_id` = `LEAD_ID`, `frame_inventory_sha256` = I, `report_sha256`
   and the three sidecar pins; v5 `rollout_join` (freeze roster and member identities, `actual_model_selection`
   gpt-6.1-sol and `different_from_author`, exactly one thread and one rollout, model, cwd = REVIEW, provider, final
   message and its timestamp, the reported digests, an actual gpt-6.1-sol max-effort exec argv).
2. Installed-evidence review (INSTALLED_REVIEW): the same rollout join, and the compiled installed-review profile with
   `candidate` = INSTALL_ROOT, `frame_inventory_sha256` = I, `setup_identities_sha256` = S and the installed-evidence
   pins it reviewed.
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
lead-module pin, both review profiles, both freeze rosters and member digests, both rollout joins except the
uniqueness of the rollout file among `~/.codex/sessions` (which only F can list, and which it reports as an
observation), the observation's structural profile and time ordering, and that the adoption body equals what those
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
| `materialize` | inputs, snapshot, recipe files/directories/modes, `tmp/` and its mode, `tmpdir/`, `materialization.json`, their markers | g (P_adm) | M6-M8 only | W only (recipe directories are 0755 owned by W) |
| `materialize` | g_rec, its ACL, `attempts/`, `attempts/<A0>/**` (records, markers, fallback journal and its slots, allocation descriptor, front records, channel segments); `export/generation/**` with its payload pack and `export/<A0>/inc-<n>/**`, with their ACLs | R_root and g_rec (P_att, P_exp) | M4-M11 | W only |
| `dispatch` | `attempts/<A>/**` (records, markers, fallback journal and its slots, allocation descriptor, inputs, stream and observer files, front records, channel segments); `export/<A>/inc-<n>/**` and their ACLs | g_rec (P_att, P_exp) | D3-D19 | W only |
| `seal-front` (W2, either mode) | `attempts/<A>/w2-<k>/` (k the smallest unused) and new names only below it: identity, channel segments, observer files and records, recovery records, release records, the front terminal record; markers appended to A's attempt journal; `export/<A>/inc-<n>/**` and their ACLs | g_rec (P_att, P_exp) | §9.7 | W only |
| `selftest` | sacrificial `selftest-<h>/**` under T_root and under R_root | T | selftest | W only |

Nothing else. In particular W writes nothing in `lease/` (§5.1), nothing below `source/` after M8 and nothing in
`tmp/` or `tmpdir/` after M7 (W never opens, renames, changes or deletes an entry there), nothing outside T (so
nothing in `/home/sicarii`, the installed frame, the shared window file or `/tmp`), and creates no named temporary
file anywhere:
a record or marker that W creates with `O_TMPFILE` has no name until its create-only `linkat` (§10.2), and an unlinked
`O_TMPFILE` inode disappears with its last descriptor. No verb renames, deletes, truncates, chmods or re-ACLs an
existing object; v6's root exchange is withdrawn with the copy route. A writer instance that cannot take the lease
refuses before any mutation and before starting any helper (S2, S_O), so while one writer holds the lease no other
can start RL, a launcher or an observer. Post-run work (conclusion, exports, recovery, release records, the front's
terminal record) is in the table: every one of those writes goes through a W-exclusive parent inside T.

**W2's capability.** W2 (`writer.py seal-front <N_F> <g> <A> <mode>`) takes the lease like any writer and may only
create new names under `attempts/<A>/w2-<k>/`, append markers to A's attempt journal and create export increments of
A. It verifies its capability before writing: W2 reads `/proc/<W2's parent>/stat` (the S3 sudo process) and
`/proc/<S3's parent>/stat`, and the latter's `(pid, start_time_ticks)` together with the current boot id must equal the
front-process triple committed in `attempt.json`. A different `sicarii` process cannot satisfy that, because the kernel
assigns pids and start times. In mode `recover`, W2 additionally requires the triple of the attempt's writer (from
`attempt.json`'s `writer`) to be absent or reused (§9.7). W2 never modifies an existing record.

### 5.3 Entrypoint closure [correction: W1-V6-SCAN-STATE]

A process can carry a given uid or gid only through: inheritance from a process that already has it; a privileged
credential change by root or by a holder of `CAP_SETUID`/`CAP_SETGID`; executing a set-user-ID or set-group-ID file;
executing a file with file capabilities; or user-namespace mapping, which `newuidmap`/`newgidmap` permit only within
`/etc/subuid`/`/etc/subgid` and which otherwise needs root. The table closes each route for each new identity. "Check"
means a setup prestate or verification item (§11.3, §11.6) and, where marked, a per-invocation check by the frame.

| Route | `wlscratch` (W) | `wlscratch-run` (R) | `wlscratch-gate` (GATE) |
|---|---|---|---|
| sudo | only rule naming W: `sicarii ALL=(wlscratch) NOPASSWD: <writer entry> *`; no other sudoers rule lists W in a Runas or user list, and no `sicarii` rule has Runas `ALL` without a password (operator inventory) | no sudo rule names R; the RL rule `wlscratch ALL=(root) NOPASSWD: <RL entry> *`, usable only by W, runs RL as root, and RL gives R only to the processes it starts, each in a scope under `wlscratch.slice` (§12.2) | conferred only by RL, in the same way |
| user manager | no linger; `sudo`'s PAM session uses `pam_systemd.so class=none` (observed in `/etc/pam.d/sudo`); probe P-NS verifies that no `user@W.service` and no `/run/user/W` appear | no linger and no session: RL starts R's processes itself, not through logind or PAM, so no `user@R.service` and no `/run/user/R` ever exist (probe P-NS); the target cannot reach any manager's socket (§12.2) | n/a |
| sshd (active: observed `ActiveState=active`) | `DenyUsers wlscratch wlscratch-run` drop-in (§11.5 S-E); home root-owned, so no `authorized_keys` can be planted; no userdb record with keys (`userdbctl`) | same drop-in; the home named in `passwd` does not exist and its parent is root-owned | not a login identity |
| login, getty, display manager | shell `/usr/bin/nologin`, password locked | same | n/a |
| PAM account controls | `sudo` uses `system-auth` (`pam_unix` account, `pam_time`) for the invoking user and opens its session with `pam_systemd.so class=none` (that no user manager results for W is probe P-NS); login services (`system-login`) add `pam_access`, `pam_nologin` and `pam_shells`; the locked password makes every password authentication fail; account expiry (`usermod -e 1`) is applied only at rollback, because sudo must still reach the accounts while they are installed (observed stacks, P10) | same | n/a |
| `su`, `runuser` | `su` needs the target's password (locked); `runuser` is root-only (`pam_rootok`) | same | `newgrp`/`sg` need a group password: none is set (`gshadow` entry locked) |
| polkit, `pkexec`, `run0`, `machinectl` | require admin authentication (`unix-group:wheel`, interactive); no rules.d grant (operator inventory); `empower` empty | same | same |
| cron, at | not installed: `/usr/bin/crontab`, `/usr/bin/at`, `/usr/bin/batch` absent, cronie and atd not found, no spool directories (observed 2026-10-04); re-checked at setup and by W at every invocation (absence of those paths) | same | n/a |
| system units, D-Bus system services | no unit or D-Bus service file references W (operator `grep -r` inventory of `/etc/systemd`, `/usr/lib/systemd`, `/usr/share/dbus-1`, `/etc/dbus-1`) | same, except the reviewed `wlscratch.slice` and the transient scopes RL creates under it | none references GATE |
| setuid/setgid files and file capabilities | none owned by W (operator `find / -xdev \( -uid W -o -gid W \)` empty before and, apart from setup objects, after); no untrusted code ever runs as W | none owned by R at setup, and none can be minted where it would confer R: every mount of a view that the target can write is an idmapped mount whose map stores the target's files as on-disk W below `source/` and as on-disk `sicarii` elsewhere (§12.2), never as R; every mount of the view is `nosuid`, so no set-ID bit or file capability takes effect inside it (premise P-NOSUID); frame code never sets either bit | likewise: the idmaps store the target's files with on-disk gid W below `source/` and `sicarii`'s 1000 elsewhere, never GATE; the target has no writable non-idmapped mount (§12.2); a set-group-ID bit confers nothing inside the `nosuid` view |
| user namespaces | W is outside every subordinate range; no range is allocated to W | same for R; RL, as root, maps R only into the user namespaces it creates for views (§12.2) | GATE outside every subordinate gid range; RL maps it only into those namespaces |
| existing processes | none at setup; afterwards only W instances (S1/S3 children) | only the processes RL starts (L, C, T, O) and their descendants, all in scopes under `wlscratch.slice`, which they cannot leave (premise P-CG) | the same processes |

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
there, and v7 has no copy that would reproduce one (v6's copied ACLs are withdrawn with the copy route).

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
Setup ACLs are written by `setfacl` as root and read back with `getfacl -n`. "GATE" and "W", "R" are numeric ids;
`1000` is `sicarii`.

| Object | Owner:group | Base mode | Access ACL (`getfacl -n` order) | `st_mode` shown | Default ACL |
|---|---|---|---|---|---|
| `/var/lib/wlscratch` | root:W | 0750 | `user::rwx user:1000:--x group::r-x mask::r-x other::---` | 0750 | none |
| `lease/` | root:W | 0750 | none | 0750 | none |
| `lease/writer.lock` | root:W | 0440 | none | 0440 | n/a |
| `runs/` (T_root) | W:W | 0700 | `user::rwx user:1000:--x group::--- mask::--x other::---` | 0710 | none |
| g | W:W | 0700 | none: only W and root can search it | 0700 | none |
| `runs/records` (R_root), g_rec, `adoption-<I>` | W:W | 0700 | `user::rwx user:1000:--x group::--- mask::--x other::---` (no GATE entry) | 0710 | none |
| `generation.json`, `materialization.json`, `inputs/**`, `commits/**` of g | W:W | 0600 files, 0700 dirs | none | same | none |
| `overlay-snapshot/**` | W:W | 0600 files, 0700 dirs (v5) | none | same | none |
| `source/` and every recipe directory | W:W | recipe mode (0755 for all 55 observed) | none | same | none |
| recipe files | W:W | recipe mode (0644 or 0755 observed) | none | same | n/a |
| partition contents (created by the target through its view) | on disk W:W, because the run-path bind's idmap stores the target's R and GATE as W (§12.2); the target sees them as 1000:1000 | as the target leaves them (umask 077 from the frame, v5); the frame never changes a mode | none set by the frame; the target may set entries | as the target leaves it | none set by the frame; the target may set one |
| `tmp/` | W:W (seen in the view as 0:0, like the host `/tmp`) | 01777 | none | 01777 | none |
| contents of `tmp/` (target temporaries) | on disk 1000:1000 through the `/tmp` bind's idmap (§12.2) | as the target leaves them | as the target leaves them | as the target leaves it | as the target leaves it |
| `tmpdir/` | W:W (seen in the view as 1000:1000, like v5's `TMPDIR`) | 0700 at M7; afterwards as the target leaves it | none set by the frame | as the target leaves it | none set by the frame |
| contents of `tmpdir/` (target temporaries) | on disk W:W through the run-path idmap (§12.2) | as the target leaves them | as the target leaves them | as the target leaves it | as the target leaves it |
| `attempts/**` (records, markers, `fallback.journal`, stream and observer files, `w2-<k>/**`); `adoption-<I>/commits/**`, `invocations/**`, `lead-adoption.json` | W:W | 0600 files, 0700 dirs | none | same | none |
| `export/` of g_rec and of `adoption-<I>`, and every directory below them (the payload pack included) | W:W | 0700, then the ACL | `user::rwx user:1000:r-x group::--- mask::r-x other::---` | 0750 | none |
| export files (the payload pack included) | W:W | 0600 at creation, then the ACL | `user::rw- user:1000:r-- group::--- mask::r-- other::---` | 0640, the final mode the export marker records (§15.3) | n/a |
| `/etc/systemd/system/wlscratch.slice` | root:root | 0644 | none | 0644 | n/a |
| `/etc/tmpfiles.d/wlscratch.conf` | root:root | 0644 | none | 0644 | n/a |
| `/opt/wlscratch`, `/opt/wlscratch/frame-v6w1/**` | root:root | 0755 dirs, 0644 files | none | same | none |
| `/opt/wlscratch/setup-identities.json` | root:root | 0644 | none | 0644 | n/a |
| image roots (images only, §14.5): the work image root seen at `runs/`, the records image root seen at `runs/records` | as `runs/` and `runs/records` above | | | | |
| bare mount points (images only; visible only while unmounted) | root:root | 0700, empty | none | 0700 | none |
| `/var/lib/wlscratch-images` (images only) | root:W | 0750: W and W2 list and search it and compare its exact entry set at every use (§3.4, §11.7); nobody but root opens the image files | none | 0750 | none |
| the image files in it (images only) | root:root | 0600 | none | 0600 | n/a |
| `lost+found` of each image root (images only; made by `mkfs.ext4`; never used, opened or walked by the frame) | root:root | 0700 | none | 0700 | none |

v6's rows for pre-created partition roots, `outputs/` and its roots, `/var/lib/wlscratch-run` and its children, the
mask links and the user-manager drop-in are withdrawn with the mechanisms they served.

### 6.4 Access paths

- **The target reaches its generation only through its view** (§12.2): `source/` at the original run path, through
  RL's idmapped bind under which it owns `source/` and everything below it, as it owned its run tree in v5; `/tmp`,
  the bind of `g/tmp`; and its `TMPDIR`, the bind of `g/tmpdir`. It reaches nothing else of T, because the view masks
  `/var/lib/wlscratch`. It creates its output
  partitions itself, as in v5, and writes its stream files through descriptors it was given.
- **C and O** read through the same kind of bind, as owners of every entry below `source/`, with `O_NOATIME`. As in
  v5, where the frame ran as the target's owner, a target-created object that its owner cannot read (for example mode
  0000) yields an observation failure and a non-success outcome; that is v5's own readability rule. Everything C needs
  from the records tree reaches it over its channel.
- **The writer never opens a target-created object.** Its own walks cover the recipe and skip the output partitions,
  and it never opens an entry of `tmp/` or `tmpdir/`. It receives partition observations and the report bytes
  (`obj/core/gnatprove/gnatprove.out`) from O over the channel and writes its own copy, as v5 copied the report
  (S:1696-1708).
- **The lead reads evidence only from P_exp and the adoption exports**, through `user:1000` entries on
  `/var/lib/wlscratch`, `runs/`, `runs/records`, g_rec and `adoption-<I>` (`--x`) and on the export directories and
  files (`r-x`, `r--`). g has no entry for the lead: the recipe reaches it through the generation export's payload pack
  (§4.2 M9), and nothing else in g or in the records tree has an entry for it.
- **Every other non-root principal** falls to `other::---` below `/var/lib/wlscratch` and cannot reach g or the
  records tree by path at all.
- **Partition roots.** v6's pre-created, writer-owned partition roots are withdrawn: as in v5, the target creates
  `obj/` and the other partitions inside a source tree it owns (in its view), and v5's rule that none exists at
  materialization (S:1033) is kept unchanged. v6's ROOTS hypothesis is therefore no longer needed.

### 6.5 Denial matrix (each cell is a probe in §13)

| Object | `sicarii` (A1) | other non-root principals (A3) | processes of a target view (T, C, O: host R and GATE) | W |
|---|---|---|---|---|
| `/var/lib/wlscratch` | search only | none | not visible: masked in every view | read, search |
| `lease/`, `writer.lock` | none | none | not visible | search; open read-only and `flock` |
| `runs/` | search only | none | not visible | full (owner) |
| g | none | none | not visible; its `source/`, `tmp/` and `tmpdir/` only through RL's binds | full (owner) |
| `runs/records`, g_rec, `adoption-<I>` | search only | none | not visible | full (owner) |
| P_adm records, `inputs/`, snapshot, `commits/` | none | none | not visible | full (owner); code writes create-only |
| recipe directories and files below `source/` | none | none | owner through the bind; a change is detected at the conclusion (v5) | owner; code does not mutate after M8 |
| partition contents | none | none | owner through the bind | owner on disk; code never opens them |
| `g/tmp`, `g/tmpdir` and their contents | none | none | the view's `/tmp` and `TMPDIR` | owner of both directories; code never opens their contents |
| P_att and P_ado originals | none | none | not visible (stream bytes only through passed descriptors) | full (owner) |
| P_exp and adoption exports | read | none | not visible | full (owner) |

In every cell marked "none", "read", "search" or "not visible", every mutation (create, `mkdir`, `unlink`, `rmdir`,
`rename` in or out, `link`, `symlink`, `open` for write, `truncate`, `chmod`, `chown`, `setfacl`, `utimensat`) must
fail. The errno is that of the first kernel check that fails, so it depends on the operand: a missing search permission
on an ancestor gives `EACCES` at path resolution; a create, unlink, rename or symlink in a directory the actor can
search but not write gives `EACCES`; an open for writing, a `truncate` or a `utimensat` without explicit times on a
file the actor can reach but not write gives `EACCES`; `chmod`, `chown`, an ACL `setxattr` and `utimensat` with
explicit times by a non-owner give `EPERM`; a hard link of another owner's file that the actor cannot both read and
write gives `EPERM` (`fs.protected_hardlinks=1`); a rename or link across mounts gives `EXDEV` before any permission
check, which is why §13 requires same-mount operands, and inside a view it is what keeps every admitted entry from
gaining a name outside the run-path bind (premise P-XDEV). §13 lists the operand, precondition and expected errno of
every probe cell. The frame's walks additionally refuse any symlink, special file and multiply linked regular file, as
the original walk does (S:531, S:554); they refuse no set-ID leaf and no device boundary.

## 7. Channels, expectations and dumpability [correction: W1-GENERATION-PROTOCOL; gap: channel-and-dumpability]

### 7.1 Channels and transports

| Channel | Transport | Created by | Carries |
|---|---|---|---|
| F↔W and F↔W2 | three pipes: F→W on W's fd 0, W→F framed messages on W's fd 1, W→F diagnostics on W's fd 2 | F, after its first act; F's ends close-on-exec | inputs, observations, requests, answers, record descriptors |
| W↔L | `AF_UNIX`/`SOCK_STREAM` socketpair SP_L on L's fd 0 (passed through S2 and RL); L's fd 1 and fd 2 are `launcher.stdout`/`launcher.stderr` in P_att, created by W before `launcher-intent.json` binds them | W | RL's `RL_IDENTITY`, then `GO` with record bytes, `FDS` with three descriptors by `SCM_RIGHTS` (SP_C's end, `scope.stdout`, `scope.stderr`), `LAUNCHER_START` (L's last message: it then `exec`s C, and SP_L closes with the `exec`), `STOP` |
| W↔C | socketpair SP_C: W keeps one end and passes the other to L in `FDS`; L moves it to fd 0, and the received `scope.stdout` and `scope.stderr` (W-created) to fds 1 and 2, before it `exec`s C | W | child stage, record bytes, `STREAMS` with the child stream descriptors by `SCM_RIGHTS`, `SPAWN_REQUEST`/`SPAWN_OK`, child records, waits, `STOP` |
| W↔O and W2↔O | socketpair SP_O on O's fd 0 (passed through S_O and RL); O's fd 1 and fd 2 are `observer-<n>.stdout`/`.stderr`, created before `observer-intent-<n>.json` binds them | W or W2 | RL's `RL_IDENTITY`, then observation requests and results, report bytes |

`sudo` passes only fds 0-2 (its default `closefrom` is 3), so every helper gets exactly one bidirectional socket on
fd 0 and two W-created files on fd 1 and fd 2; further descriptors travel only by `SCM_RIGHTS`. L never reads or
writes SP_C: C's messages reach W directly, so v3's relay through L is gone and the W↔C chain is end to end. RL sits
between S2 and L, and between S_O and O, in every configuration (v6's Option A is withdrawn); it passes the helper's
fds 0-2 through unchanged, closes every other descriptor (§12.2), and before its `exec` it writes exactly one
`RL_IDENTITY` frame on fd 0, on a direction of its own (§7.3). T receives only `/dev/null` and the two child stream
files; no socket of any channel reaches T.

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
  sha256 error; an expired deadline. The receiver stops reading that channel, retains the raw bytes of the failing
  frame (if any) as a raw record, never acts on a later message and proceeds by §9.5.
- Deadlines (judgments, not bounds): v5's 300 s first byte and 30 s completion for an answer line, unchanged; v5's
  30 s per subprocess observation, unchanged; 600 s for a front stage-observation set; 60 s for a control reply
  (acknowledgement, `GO`, `SPAWN_OK`). Before launch an expired deadline refuses (nothing reserved or launched, as
  applicable). After launch it is recorded and never stops the wait for participants.

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
  and root. RL runs as root. L, C and O run with host uid R, which only processes that RL starts have (§5.3): no target
  exists before C's spawn call, and an observer never shares a scope or a time with a target (§9.4), so before their
  call only frame helpers and root could read them; their channel sockets cannot be reopened through `/proc` and their
  stream files are W-owned 0600. The window's duration is not measured; probe P-DUMP timestamps it. This residual is
  stated, not accepted as a new guarantee.

## 8. Fresh identities, the real outer invocation, the original context and the vault [gap: fresh-identities-and-vault]

### 8.1 Per-invocation role identity

Every process of every invocation records a fresh `wlscratch-role-identity-v1` (Appendix B.1) immediately after its
first act (§7.7). It contains: role; boot id; pid, ppid, `start_time_ticks` (field 22 of `/proc/self/stat`); comm;
argv (`/proc/self/cmdline`); exe (`readlink /proc/self/exe`, `[dev, ino]`, sha256); all four uids and gids and the
supplementary groups (`/proc/self/status`); capability sets, `NoNewPrivs` and `Seccomp`; both dumpability readbacks;
umask; resource limits; cgroup (`/proc/self/cgroup`); mount, pid, user, network and cgroup namespace inodes; cwd
`[dev, ino]`; for fds 0-2 the file type, `[dev, ino]`, mode and open flags, and the full list of open fds; the
environment as sorted names plus the sha256 of every value, with clear values only for the non-secret keys `HOME USER
LOGNAME LANG PATH SHELL PWD TMPDIR XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS INVOCATION_ID SUDO_USER SUDO_UID SUDO_GID
SUDO_COMMAND` and every `PYTHON*` key; Python `sys.version`, `sys.executable`, prefixes, every `sys.flags` field and
`sys.path`; and the loaded module closure (every `sys.modules` entry with a file: name, path, size, sha256; builtin
names listed). Processes inside a view (L, C, O) also record `/proc/self/uid_map`, `gid_map` and `setgroups`; their
`/proc/self/status` shows ids as their user namespace sees them (1000 for host R and for host GATE). The parent role
independently reads the child's `/proc/<pid>/{stat,status,cmdline,cgroup}` from the initial user namespace, where the
host ids appear, and joins them with the child's self-report through the recorded maps (pid, start time, credentials,
command line); a mismatch refuses before launch and is an error after.

Per stage, in addition (each a fresh observation, never reused across stages or attempts):

| Role | Parent stage | Child stage | After (conclusion) |
|---|---|---|---|
| F (real lead context) | fresh lead observation `scratch-run`; frame admission front part; base-tree re-observation; v5 runtime-closure observation with the original spec against the original baseline (compact if equal, v5 item 4); `systemctl --user show-environment` of `sicarii`'s manager against the original `manager_environment` baseline; sibling units of v5's `sample` (no unit allowed, because the frame's scopes are not in `sicarii`'s manager) and `storage_status.py` | the same set with stage `scratch-child`, and the window ownership check | the same set except the lead observation, as v5 conclusion re-ran frame admission and identities |
| W | own identity against the reviewed writer-context baseline (system standard library only, `-I` flags) | lease, location, snapshot, record-drift writer half; CRED (§9.4) | same, plus v5's terminal predicate (§9.4) |
| O (in its view) | full walk; tool, proof-data, proof-ELF, vendor and runtime-closure observations with v5's own specifications (the source relocated to the run path exactly as v5 relocated it) against the original v5 baselines; heavy processes and meminfo; the census of §9.4 | n/a | same as parent, plus the report bytes |
| C (in the view) | n/a | v5 child admission in full (§9.3 C1-C11), with the same observations as O, the census and the final pass; the manager environment is F's half (C4), because no process of the view can reach `sicarii`'s manager | n/a |

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

### 8.3 The original target path, environment and caps are kept [correction: W1-V6-PRESERVE]

- `child_argv` is exactly v5 `command()`: `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/bin/gnatprove -P
  core/worldline_core_sources.gpr -U --mode=all --level=3 --report=all --checks-as-errors=on --proof-warnings=on -j2`
  (with `-k` for `prove-all-k`), the `prove-file`/`prove-subp` forms, or the `gprbuild … -p -j2 -c -U` form for
  `compile-all`. The path is executed as written (R4); the view shows it at the same path, through the root view's
  idmap, with the same owner, mode and bytes (§12.2).
- The scope is a transient scope of the system manager, `systemd-run --scope --slice=wlscratch.slice --unit=<U> -p
  MemoryMax=8G -p MemorySwapMax=0` (RL's first stage, §12.2), in place of v5's `systemd-run --user --scope --unit=<U>
  -p MemoryMax=8G -p MemorySwapMax=0` in `sicarii`'s manager. `RLIMIT_CORE` is (0, 0), set by RL before that `exec`
  and inherited. C reads back `memory.max == 8589934592`, `memory.swap.max == 0`, core `[0, 0]` and its scope
  membership (v5 S:1828-1838). `-j2` stays in the argv. The limits are v5's; the manager that applies them is not
  (§12.3).
- `MIN_MEM_AVAILABLE_KB = 16777217`, `MAX_CHALLENGES = 3`, the 300 s and 30 s receipt deadlines and the 30 s
  observation timeouts are unchanged; the target executable's digest is checked against the baseline before the spawn
  (v5 S:1839-1841).
- W-1 adds no restriction on T's process attributes. v6's `no_new_privs` and anti-setid seccomp filter (v6 C9, with
  its compatibility hypothesis) are withdrawn: no file that T can create confers R or GATE (§5.3), and every mount of
  the view is `nosuid` (P-NOSUID). What the view itself changes for T is inventoried in §12.3; whether any of those
  changes can alter an allowlisted action's observable behaviour is the premise TOOL-CLOSURE (§22), unestablished.

### 8.4 The original context inside the view [correction: W1-V6-PRESERVE]

v6 relocated `HOME`, `USER`, `LOGNAME`, `XDG_RUNTIME_DIR`, `DBUS_SESSION_BUS_ADDRESS` and `TMPDIR`, because its
target ran as R in the host's namespaces. v7 relocates nothing beyond v5's own rule. Inside its user namespace the
target is uid 1000 and gid 1000 with the lead's supplementary groups, and the view shows the host filesystem with
`sicarii`'s on-disk ownership (§12.2). The target environment is exactly v5's `specifications()` result: the
`KEEP_ENVIRONMENT` keys `HOME`, `USER`, `LOGNAME` and `LANG` with the lead's values (observed by F, streamed and
recorded); the tool specification's `effective_environment` with v5's relocation of `PENDING_LIBRARY_DIR`,
`PENDING_OBJECT_DIR`, `PYTHONPATH` and `WORLDLINE_CORE_LIB` from the F10K source to the run's source path; and the
runtime specification's environment (`TMPDIR=/home/sicarii/.cache/workflow-tmp`, the `null` keys removed). The run's
source path is v5's own, `<RUNS>/<label>/source` (S:977-999); in the view it is the bind of g/source.

The original observations compare these rows, which the view reproduces:

| Object | v5 baseline row | In the view |
|---|---|---|
| `TMPDIR` | uid 1000, gid 1000, mode 0700 (runtime closure) | the bind of `g/tmpdir`, seen as uid 1000, gid 1000, mode 0700 until the target changes its mode, as it could change v5's |
| `/tmp` | uid 0, gid 0, mode 01777 | the bind of `g/tmp`, seen as uid 0, gid 0, mode 01777 |
| `/var/tmp`; `/usr/tmp` | uid 0, gid 0, mode 01777; absent | the host objects through the root view; absent |
| the run's source (v5's relocation of the F10K row) | uid 1000, gid 1000, mode 0755 | the bind of g/source, seen as uid 1000, gid 1000, mode 0755 (the recipe root's mode, §6.1) |
| every other path of the tool, proof-data, proof-ELF, vendor and runtime baselines | as recorded | the same object through the root view: on-disk 1000 shown as 1000, every other on-disk id shown as itself |

So O and C compare with the original v5 baselines, unchanged. v6's relocated runtime-closure inventory, R's manager
baseline, S_units and S_socks are withdrawn; the only new baseline is the writer-context baseline. That every original
observation taken in the view equals its original baseline is premise P-VIEW (§9.8 N7). A difference keeps the full
observation and refuses (v5 `retain_observation`); it would be a defect of the view, to be repaired, never an accepted
case to narrow.

`DBUS_SESSION_BUS_ADDRESS` keeps v5's value byte for byte, and the socket it names is visible in the view (the idmapped
`/run/user/1000`), but a connection to it fails with `EACCES`, because Landlock denies a connection to every UNIX
server created outside the target's domain (§12.2). The same holds for every other `sicarii` service socket. This is
a change, listed in §12.3.

### 8.5 Vault scope [correction: W1-V6-EVIDENCE-RESTORE]

- **What is pinned:** P_exp(g), the path `g_rec/export` (`/var/lib/wlscratch/runs/records/<g>/export`), with the
  generation export's payload pack, and the adoption exports `adoption-<I>/export` of the adoption the attempt binds.
  `sicarii` can read both through the ACLs of §6.3. The originals in g, g_rec and P_ado(I) are unreadable to
  `sicarii`; they are neither pinned nor backed up by the vault. Their custody is the protected local tree.
- **Who and when:** F, as `sicarii`, runs `project-vault pin <g_rec>/export` and `project-vault status` at M10, and
  `project-vault pin` for both paths and `project-vault status` at D9, each under the original 30 s observation
  timeout, keeping the authentic HOME, configuration, user bus, reserve, queue and backup state of `sicarii`; W records
  the results (v5 S:1562-1563 did the same for its run directory). They must succeed or the stage refuses, as in v5.
  `storage_status.py` and `project-vault` are never run as W or R. No new gate: these are v5's vault calls with the
  export paths in place of the run directory.
- **What a reader needs, and where it is** (correction W1-V6-EVIDENCE-RESTORE): every channel segment reference
  resolves inside the pinned trees (§7.3): `record` references in the same increment cut, `written` references in the
  generation export's payload pack, `source` references in the adoption increment's payload pack. A verifier holding
  only the two pinned trees, locally or restored, recomputes every chain head, every marker digest and every payload
  digest. No dependency on the protected originals remains for any promised reader.
- **Unverified:** whether project-vault backs up and restores a path outside `/home` correctly. Sacrificial
  verification V-VAULT (§13) is future evidence; until it passes, vault coverage of exports is not claimed and the
  Gate 0 restore term remains in full (§14).

### 8.6 Input classes (v2 §6.1 carried; the re-review closed W1-READ-ACCESS)

W reads nothing under `/home/sicarii`. F reads every lead-side input with the v5 anchored readers and streams it.
- **Pinned inputs**, verified by W against values compiled into the installed frame before any use: the three base
  descriptors (`BASE_BINDING_SHA256`, `BASE_INVENTORY_SHA256`, `BASE_DIRMODES_SHA256`, unchanged from v5); every base
  file (digest and size from the pinned inventory); the lead module (`LEAD_MODULE_SHA256`; W executes the verified bytes
  with v5 `exec_verified` only to read its constants and never calls `observe`).
- **Joined inputs**, verified structurally exactly as v5 does, because they postdate the frozen frame: the overlay
  (v5 `overlay_rules`: Ada units under `core/` and `DELETE.list` only; retained by digest in the snapshot); the
  code-review and installed-review rosters with their freeze and provenance records (v5 `review_profile_problems` and
  `rollout_join`, and the installed-review profile, with each review's `frame_inventory_sha256` equal to the sha256 of
  the installed `frame-inventory.json`, §4.6).
- **Protected frame records.** The adoption record is no longer a lead-side input: W commits it inside T (§4.6),
  reads it at every dispatch and delivers it to F and C; F's lead-context joins over it are observations at v5 trust.
- **Observations**, recorded with digests at v5's trust (R2): F's lead observation, rollout join and
  adoption-observation/transcript-prefix results, base-tree re-observation, window snapshots, storage readings, vault
  results, sibling units, F's runtime and manager observations, and F's identity.

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
exit_code, signaled, signal, core_dumped, wait_error, interrupts, unresolved, at, meaning}`; `wlscratch-scope-v2`
`{manager: "system", unit, invocation_id, control_group, properties_at_start, properties_at_end, populated, cgroup_state
∈ {ABSENT, EMPTY, NONEMPTY, UNAVAILABLE}}`; `wlscratch-census-v1` (§9.4, Appendix B.2). A process is identified by
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

### 9.3 Launch gating [corrections: W1-V6-C1-DATA, W1-V6-SCAN-STATE; v6: W1-V5-PROTOCOL-REFUSALS, W1-V5-REVOCATION-CONFINEMENT; v5: W1-PROTOCOL-FAILURE-STATES, W1-CUSTODY-CLOSURE; v4: W1-GENERATION-PROTOCOL]

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
  the scope U (unit, control group `/wlscratch.slice/<U>`, the census RL took before the view); the view
  specification's sha256 equal to the one `launch.json` binds; the namespace inodes; the maps; the mountinfo of the
  view; the Landlock ruleset digest; and the credentials and capability sets RL holds just before its `exec` (all
  uids R and gids GATE as seen from the initial namespace, groups G_V, every capability set zero in the initial user
  namespace). W commits `launcher-rl-identity.json`. A missing or second RL frame is a channel failure (Appendix
  B.4.5), after which W sends no `GO`; a frame that fails W's verification makes W send `STOP`. Either way L exits 125
  having started nothing, and W refuses before launch. The same holds for every S_O (`observer-<n>-rl-identity.json`,
  committed before the first `OBSERVE_REQUEST`; on a failing frame W sends `O_BYE` instead of a request).
- G4. L: first act, identity, argv grammar; requires, from `/proc/self/status` and its maps, uid and gid 1000 inside
  a user namespace whose maps are the view's (so its host credentials are R and GATE), its cgroup to be
  `/wlscratch.slice/<U>` with U derived from its argv, fd 0 a socket and fds 1-2 regular files; sends `L_HELLO`;
  waits for `GO` within the control deadline. If a G4 check fails, L sends `L_REFUSAL` (stage: the failed check) as its
  first message instead of `L_HELLO` (after RL's frame), or writes the statement to its stderr if SP_L does not work,
  and exits 125 having started nothing. **EOF or deadline before `GO` → L exits 125 having started nothing.**
- G5. W verifies L through `/proc/<L>` (credentials; `PPid` equal to S2 or to S2's own sudo monitor child, whichever
  P-LAUNCH records for this host's sudo; start time equal to RL's; cmdline; cgroup) and
  sends `GO` with the bytes of `launch.json`, `admission.json` and `launcher-intent.json`, then `FDS` with SP_C's other
  end and the bound `scope.stdout` and `scope.stderr` descriptors by `SCM_RIGHTS`.
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
  64-hex seals); uid and gid 1000 inside a user namespace whose maps are the compiled view maps; its cgroup equal to
  `/wlscratch.slice/wlscratch-<g12>-<A>.scope` with g and A from its argv; its parent a `sudo` process (the `comm`
  field of the world-readable `/proc/<ppid>/stat`), as L's was, because L became C by `exec`; fd 0 a socket and fds
  1-2 regular files (types only). C sends `C_HELLO` to W over SP_C. If a C1 check fails, C sends `CHILD_REFUSAL` with
  `child-refusal.json` as its first message instead of `C_HELLO`, or writes the statement to its stderr if SP_C does
  not work, and exits without spawning; W cannot have sent it `SPAWN_OK` (C8).
- C2. W verifies C through `/proc/<C>` (pid and start time equal to L's, because L became C by `exec`; `PPid` as G5
  found it; credentials, cgroup, cmdline); if that verification fails, W sends `STOP` instead of `RECORDS`, and C
  refuses. Otherwise W sends `RECORDS` (the bytes of
  `launch.json`, `admission.json`, `reservation-intent.json`, `reservation.json`, `launcher-intent.json`,
  `materialization.json`, `lead-adoption.json` and the lead module) and `STREAMS` (`child.stdout` and `child.stderr` by
  `SCM_RIGHTS`). After this authenticated delivery and before any spawn request, C performs the checks that need the
  records: its `/proc/self/cmdline` equals the sealed C template of `launcher-intent.json` plus its argv items; its
  environment equals `launch.json`'s; its fds 1-2 and the received child stream descriptors have the identities
  `launcher-intent.json` binds; the lead module against the compiled pin; and every v5 child join (S:1782-1817): both
  seals; `intent.launch` equals the delivered `launch.json` descriptor; `admission.launch` equals `intent.launch`; the
  `reservation.json` token taken from the `admission.json`-pinned record (frame plan H-M6) equals the intent's token;
  `launch.materialization` equals the delivered `materialization.json` descriptor; `launch.adoption` equals the
  delivered adoption record's descriptor. A failing C2 check makes C send `CHILD_REFUSAL` (in state `RECORDS`) and exit
  without spawning.
- C3. C opens the view's `source/` at the run path with `O_DIRECTORY|O_NOFOLLOW|O_NOATIME` and requires its `[dev,
  ino]` to equal the seal's source identity and the opened directory to be a mount root (`statx`
  `STATX_ATTR_MOUNT_ROOT`) whose mount ID the view's mountinfo in `launcher-rl-identity.json` names as the bind of
  g/source; the attempt and snapshot identities are checked by W in C4.
- C4. `CHILD_STAGE_REQUEST`. W performs the writer half (snapshot observation equals the record, attempt-directory
  identity equals the seal, the attempt-journal join of §10.6, lease held, location chains unchanged, CRED of §9.4)
  and obtains F's child-stage half (§8.1: fresh lead observation `scratch-child`, `owns_window(LEAD_ID, attempt path,
  token)` under the window lock, frame admission front part over the adoption bytes, base-tree re-observation, F's
  runtime and manager identity, the front half of the `child-final` sample with the reserve equal to the bound and the
  sibling units of `sicarii`'s manager with no unit allowed). W commits both halves and sends them to C
  (`CHILD_STAGE_RESULT`).
- C5. C requires `launch.holder == LEAD_ID == intent.holder_task` and window ownership true (v5 S:1809-1811); runs
  the installed-frame inventory check, the target-context identities `child`, and the admission walk with source-tree
  identities equal to the seal (v5 S:1812-1813).
- C6. v5 S:1814-1841 in order: pins (frame inventory, review, adoption, materialization), environment, parent memory
  gate, the helper half of `child-final` (heavy-process refusal, meminfo at or above 16777217 kB; the sibling units are
  F's half), cwd, allowlist re-derivation, limits readback, scope membership, target executable digest.
- C7. Child-stage census (§9.4): U holds exactly C; every other child cgroup of `wlscratch.slice` is
  `populated 0`; CRED. Any failure or UNKNOWN refuses (RP1); it can arise only if a premise of §9.8 N7 failed or a
  frame helper misbehaved, and it is recorded as premise evidence.
- C8. `SPAWN_REQUEST` with the digest of C's admission summary. W answers `SPAWN_OK` only if F answered a `PING`
  within the control deadline, W's error list is empty, the attempt-journal join holds and W's CRED passes, and only
  after committing `spawn-ok.json`; otherwise W sends `STOP`. `STOP`, EOF or deadline → C refuses.
- C9. C prepares T's pre-exec exactly as v5 `spawn`: `fchdir` to the held `source` descriptor, `RLIMIT_CORE` (0, 0),
  then unblock the handled signals. No `no_new_privs`, no seccomp filter (§8.3).
- C10. **Final pass** (§4.5): the walk with `O_NOATIME`; the observation must equal the admitted parent observation;
  then the census and CRED again; `verify_location` of every held handle.
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
C8's `STOP`, EOF or deadline and a `STOP` pending at C11's interruption point) sends `CHILD_REFUSAL` with
`child-refusal.json` (v5 keys, `target_started: false`, v5 meaning "refused before the target spawn; nothing was
started") if SP_C still works, and otherwise writes the same statement to its stderr (`scope.stderr`, raw evidence); C
then exits without spawning. Appendix B.4.4 admits `CHILD_REFUSAL` in every W↔C state before C's spawn call, C's first
message included. C never sends `CHILD_REFUSAL` after its spawn call; a failed spawn call that leaves no child is
reported by `SPAWN_FAILED` with `child-wait.json` and `started: false`, as v5 reported it in `child-wait.json`.
**`target_started`** is therefore `true` if `child-start.json` is committed, `false` only if C's committed
`child-refusal.json` or its committed `child-wait.json` with `started: false` exists, and `unknown` otherwise. W writes
`child-refusal.json` only from the bytes C sent: C's silence, an EOF, a deadline or a channel failure leaves
`target_started` `unknown` (Appendix B.4.5). A missing `CHILD_START` never means that no target exists, and `unknown`
never shortens a classification.

**Why a late launch after writer death is possible only through an issued, recorded permission.** No L can start C
without `GO` (G4), which only a live W sends, and only after `PROCEED_LAUNCH` and the committed launch intent. No T
can start without `SPAWN_OK` (C8), which only a live W sends after committing `spawn-ok.json`. A sudo front-end (S2)
that outlives W can only start an RL and an L, which then reads EOF and exits. So after W's death the only possible
future target is one whose C already holds `SPAWN_OK`; that C is a process of U, which stays populated until C and
everything it started have ended (§9.4), and it either refuses before its spawn call or spawns a T in U. Whether a
launch is still pending is concluded only from U's state and v5's terminal predicate (§9.4), never from a missing
record.

### 9.4 The census, credential closure, known-terminal ownership and the release rule [corrections: W1-V6-SCAN-STATE, W1-V6-PRESERVE; v6: W1-V5-REVOCATION-CONFINEMENT, W1-V5-PRESERVATION; v5: W1-CUSTODY-CLOSURE, W1-PROTOCOL-FAILURE-STATES; v4: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE]

v6's process, unit, reference, quiescence and lease scans, its in-place predicate, M-QUIESCENT, the systemd premises
S1-S6 and the absorption lemma are withdrawn with the user manager and the copy route. Two observations replace them.

**The census of `wlscratch.slice`.** At a point P, the observer reads from the cgroup2 hierarchy, which is root-owned
and world-readable (`/sys/fs/cgroup/wlscratch.slice`): the list of its child cgroups and, for each, `cgroup.events`
(`populated`) and `cgroup.procs`, each process by `(pid, start_time_ticks, boot_id)`. The census passes at P iff each
scope that P expects holds exactly the processes the table below gives, and every other child cgroup is `populated 0`.
An unreadable entry makes it UNKNOWN.

**Why the census reads a state and not a sample** (correction W1-V6-SCAN-STATE). `populated` is maintained by the
kernel together with process exit and migration, and for a scope with no live process `populated 0` is absorbing: a
process can enter a cgroup only as the child of a process already in it, or by migration, which needs write access to
the destination's `cgroup.procs` (root-owned below `wlscratch.slice`) and to the common ancestor's (premise P-CG). A
depopulated scope has no process left to fork and only root migrates processes, and RL never moves one into an
existing scope. So, once a census reads `populated 0` for an earlier scope, that scope is empty at every later moment,
including the final pass and T's `exec`: the custody conclusion of §4.5 rests on this absorbing kernel state, not on a
composition of scans taken at different instants under fork, exit, credential or queued-input churn. The membership
of the current scope at the child stage (exactly C) is not absorbing, because C can fork; C is frame code, and it
reads that membership immediately before and after its final pass. The one premise this needs and that is not yet
established is P-CG, with its probe (§9.8 N7).

**Credential closure, CRED.** A process with host uid R or gid GATE in any position, or GATE among its supplementary
groups, exists only inside a scope of `wlscratch.slice`: RL is the only code that confers them (§5.3), it confers them
only on itself after `systemd-run` has placed it in a new scope, and no process can leave its cgroup (P-CG, P-NOR).
CRED observes this: every process whose `Uid:`, `Gid:` or `Groups:` line in `/proc/<pid>/status` (world-readable)
contains R or GATE has a `/proc/<pid>/cgroup` below `/wlscratch.slice/`. From inside a view the same test reads 1000 in
those lines, because the view's user namespace shows host R and host GATE as 1000 and no other host id as 1000. A
failing CRED is evidence that P-NOR failed; it refuses before launch and holds at a classification. It checks an
enforced property; nothing rests on its completeness at a single instant.

| Point P | Observer | Census expectation | Also required |
|---|---|---|---|
| parent stage (D8) | RL before it builds O's view, then O | U absent; O's observer scope holds exactly O; every other child `populated 0` | CRED; the original walk rules |
| child stage (C7) and final pass (C10) | C | U holds exactly C; every other child `populated 0` | CRED (C and, at C4 and C8, W) |
| after stage (D17) | O, for W | O's scope holds exactly O; U absent or `populated 0` | v5's terminal predicate |
| recovery round (§9.7) | O, for W2 | as at the after stage | v5's terminal predicate |
| release (D18, RC4) | F under the window lock | not taken | v5's terminal predicate only |

**Known-terminal ownership** of attempt A is v5's `owned_terminal` predicate (S:1373-1415), unchanged in meaning and
evaluated over v7's participants: U has ended (`systemctl show <U>` in the system manager reports `LoadState`
`not-found`, or `ActiveState` `inactive` or `failed`); its cgroup is absent or empty; every recorded participant pid
(L from `LAUNCHER_START`, C, T from the child records) is absent from `/proc`; no process names the attempt (v5
`processes_naming`); the launcher pid is known if a launch was made; no child record is unresolved. W's after stage or
W2's recovery establishes it; nothing else is a condition. v6's global uid, manager and lease conditions (its D5) are
withdrawn, so an ended participant set with a closed foreign-owned file no longer yields UNKNOWN: v7 has no such
file and no such test.

**Release rule** (only F; v5's "only the launching parent releases" is kept, because F is the reserving process). F
releases if and only if both hold under the window lock:
1. `owns_window(holder, candidate, token)` (v5, unchanged: status reserved, holder, candidate, token);
2. known-terminal ownership of A has been established by W's after-stage classification or, after W's death or
   channel failure, by W2's recovery (§9.7), and F's own evaluation of the same predicate, taken under the window lock
   immediately before the window write, holds.
Nothing else is a condition. In particular the durability of a record (`release-intent.json`, `window-release.json`,
the conclusion, the observations' own records) is not.

**Procedure, all under the window lock** [correction: W1-PROTOCOL-FAILURE-STATES]. F verifies 1 and 2; F sends
`RELEASE_INTENT_REQ`; the serving writer instance (W, or W2 after recovery) tries to commit `release-intent.json`
(primary, retry, fallback, §10) and answers `RELEASE_INTENT_RESULT` with the outcome. F waits for that answer at most
the control deadline (§7.4). With the answer, or at the deadline without it, F performs v5's window write (the commit
point), re-reads the window and sends `RELEASE_DONE`; the writer then commits `window-release.json` (re-read
`released`) or `release-failure.json` (otherwise) and answers `RELEASE_RECORD_RESULT`. A `RELEASE_INTENT_RESULT` that
arrives after F's window write is a late result: it is legal (Appendix B.4.4), F records it in its terminal facts
(`release.intent_result_late`), and it changes and delays nothing. Any outcome other than a committed intent record
makes the attempt durability-UNKNOWN: no success credit, and the uncertainty is reported (console, `FINAL`, and the
front terminal record if it can be committed). It creates neither a hold nor an approval gate (supplied ruling, gpt61-v2
REVIEW.md:230). If no `RELEASE_RECORD_RESULT` arrives within the control deadline after `RELEASE_DONE`, F treats the
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

**Does the census refuse a case that v5 admitted?** In v5 an earlier scope of the frame was the unit
`claude-worldline-scratch-<name>-<stamp>.scope` of `sicarii`'s manager (S:1564), which matches v5's sibling pattern
`claude-worldline-*`, and v5's `sample` refused while such a unit was active, activating or deactivating (S:1156-1163);
a reservation still held by an earlier attempt refused at `reserve`. A child of `wlscratch.slice` that is not
`populated 0` is a scope whose processes still run. That these two states coincide in every case (a scope unit is
active exactly while its cgroup is populated) is premise P-CENSUS (§9.8 N7), unestablished; if it fails, the census
is a new refusal and §21 lists it as such.

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
| Channel failure, deadline or refusal before D12 | W: `refusal.json` ("refused before reservation and launch; nothing was started") when `attempt.json` is committed; F: no reservation; F runs W2 in mode `seal` if it knows that `attempt.json` is committed (from `W_HELLO` or `EARLY_REFUSAL`) |
| `reservation-intent.json` cannot be committed | F does not write the window (`RESERVE_ABORT`); nothing reserved; W: `refusal.json` |
| `reservation.json` cannot be committed | the reservation exists; durability-UNKNOWN for that record; W refuses before launch, concludes with the after-stage classification, and F releases by §9.4 |
| W dies or its channel fails after F's window write and before `PROCEED_LAUNCH` | W never started S2, but this is not inferred from missing records: F runs recovery (§9.7); release only on known-terminal ownership |
| W dies or its channel fails after `PROCEED_LAUNCH` | a launch may exist; recovery (§9.7) classifies until known-terminal or unknown; release by §9.4; otherwise hold |
| F dies after its window write | W: before launch, refuses and concludes; after launch, keeps waiting and concludes. W cannot release (F alone can): `release-withheld.json` ("front absent"); manual resolution. A front EOF never implies a refusal after launch |
| RL refuses its invocation, the system manager refuses the scope, or a step of the view fails (§12.2) | RL writes the failed step to its stderr (the W-created `launcher.stderr` or `observer-<n>.stderr`) and exits non-zero before it sends anything and before L or O exists; W: a channel failure before `RL_IDENTITY`, S2's or S_O's wait recorded; before launch the stage refuses; U is absent or `populated 0` once RL has exited |
| `RL_IDENTITY` missing or second, or failing W's verification | missing or second: a channel failure, and W sends no `GO` or `OBSERVE_REQUEST`, so the helper reaches its deadline and exits 125 having started nothing; failing: W sends `STOP` (L) or `O_BYE` (O). Before launch the stage refuses; at a classification the observation fails (§9.4) |
| L dies before `GO` / the pid dies after `LAUNCHER_START` | before: nothing was started; after: L may have become C; U's state and the classification decide |
| A G4 check of L fails, L reads a `STOP` at its interruption point, or its `exec` of C fails | `L_REFUSAL` (L's first message when a G4 check failed); L exits 125 having started nothing |
| C refuses before its spawn call (C1 before its hello, C2 after `RECORDS`, C3-C11, including a `STOP` pending at C11) | C's `child-refusal.json` (C's own pre-spawn statement), committed by W; `target_started: false`; terminal ownership still by §9.4 |
| C's spawn call fails and no child exists | `SPAWN_FAILED`; `child-wait.json` with `started: false`, committed by W; `target_started: false`; terminal ownership still by §9.4 |
| C dies or SP_C fails without either record, or C's spawn call fails while a child exists | `target_started: unknown`; never inferred from a missing `CHILD_START` or from C's silence; the classification decides |
| T exits | C's `child-wait.json`, L's and W's waits, O's after stage, conclusion |
| O fails | before launch: the stage refuses; after launch: no complete classification, so hold until a later O under a live W or a W2 succeeds; W never releases on its own |
| The census or CRED fails or is UNKNOWN at the parent stage, the child stage or the final pass (an earlier scope not `populated 0`, an unexpected process in U or in the observer scope, a process with R or GATE outside `wlscratch.slice`) | refuse before launch (RP0 at the parent stage, RP1 at the child stage); recorded as premise evidence when it contradicts §9.8 N7 (P-CG, P-NOR); whether v5 refused the same state is P-CENSUS (§9.4) |
| An original walk rule refuses an entry below the view's `source/` (an alias, a special file, a multiply linked regular file, an entry its owner cannot open, list or read, an entry that changes during its observation) | v5's refusal at the same stage, unchanged (S:495-566); no other walk rule is added |
| A step before the close marker's link fails (the create, write, `fsync`, validation or link of the record or of either marker, or a directory `fsync` before that link) (§10.1, §10.2 J4) | the record is not committed for any consumer; a named record file or record-bearing marker is RAW; §10.3's retry with its downgrade, then the fallback, carry the record |
| The close marker's link succeeded, then its directory `fsync` or its post-link join fails (§10.1) | the record is committed for every consumer, `synced: false`; durability-UNKNOWN for it; success withheld; no release effect |
| A marker fails and its continuation fails too (§10.2 J4) | the writer writes no further marker in that journal; later records go to the fallback journal (durability-UNKNOWN for `adopt`, which has none); success withheld; no release effect |
| A journal is branched (§10.2) | the writer writes no marker in it; its records go to the fallback journal or are durability-UNKNOWN; success withheld; no release effect |
| Records exhaustion | §10: success withheld; release by §9.4 only |
| A stream file not final (§10.6) | success withheld; no release effect |
| An export increment fails | `EXPORTED` with state `failed`; success withheld; no release effect |
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
  owner, mode and ACL; the loop device number and mount ID are re-observed, not compared), `wlscratch.slice`, the
  tmpfiles rule and the installed frame; it refuses otherwise. A missing image mount leaves the bare root-owned mount
  point, which W can neither write nor mistake (§3.4).
- Journals are interpreted, never repaired: each journal's committed chain is recomputed (§10.2), and a torn marker
  or torn fallback slot left by the interrupted boot is raw evidence, never reused (§10.2, §10.4). A close marker whose
  link reached the disk before the crash confirms its record; one whose link did not is absent, and its record is
  uncommitted (§10.1): the same answer for every reader.
- Scopes, views and their namespaces end with the boot. The first census of the new boot sees `wlscratch.slice`
  without the earlier scopes.
- There is no implicit new genesis: W never recreates or reinitializes a generation; a new one exists only through
  `materialize`. Stale evidence earns no credit: no record of an earlier attempt is ever an admission input.

### 9.7 Writer-death recovery and the post-writer W2 [corrections: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE]

**Mode `seal`** (W ended normally with `FINAL`). F starts S3 → W2 `seal-front <N_F> <g> <A> seal`. W2: first act,
identity, lease (on `LeaseHeld` it exits before any mutation, and F retries after a fixed interval of 10 s, a
judgment, until the lead stops F), capability (§5.2); creates `w2-<k>/` and commits `w2-<k>/identity.json`;
`W2_HELLO`. F: `HELLO_ACK`. State `FRONT_TERMINAL`: F sends its terminal record (S1's raw wait, W's `FINAL`, W's triple
absent or reused, the answers forwarded, interrupts, errors, channel heads, durability) and W2 commits
`w2-<k>/front-terminal.json`. State `EXPORT`: A's next export increment (§15.3). State `FINAL`: `FINAL`, `BYE`.

**Mode `recover`** (F did not receive W's `FINAL`: W died, the F↔W channel failed or a deadline expired; and F wrote
the window during this attempt, or cannot tell whether its window write took effect):
- RC1. F closes its ends of the W pipes and waits for S1 to exit, without a deadline; the lead's interrupt is
  recorded and forwarded as in v5. While S1 or W lives, W holds the lease and no W2 can start.
- RC2. F starts S3 → W2 `seal-front <N_F> <g> <A> recover`. W2: first act, identity, lease (retried as above),
  capability (§5.2), including the attempt writer's triple absent or reused; creates `w2-<k>/` and commits its
  identity; reads A's committed journal chain (§10.2) and every committed participant record of A; `W2_HELLO`.
- RC3. State `RECOVER`, rounds r = 1, 2, …: W2 uses an observer O (G0 first: `w2-<k>/observer-intent-<n>.json`; one O
  may serve several rounds) to evaluate v5's terminal predicate at the recovery point (§9.4): U's state and cgroup,
  every participant named by A's committed records or seen in U, no process naming the attempt, no unresolved child
  record. The verdict is `known-terminal` (the predicate holds), `live` (U active or populated, or a recorded
  participant pid present: W2 waits a fixed round interval of 10 s, a judgment, and repeats) or `unknown` (an
  unreadable entry, an O that cannot run or answer, an unresolved participant record: the rounds end). W2 commits
  `w2-<k>/recovery/scan-<r>.json` when the verdict or the set of live participants changes and for the last round,
  and `w2-<k>/recovery/result.json` with the final verdict and `target_started`; it sends `RECOVERY_SCAN` after each
  committed round and `RECOVERY_RESULT` at the end, after its O has ended (`O_BYE`, wait). F may send `STOP` (the
  lead's interrupt): W2 ends the rounds with the last verdict, `live` or `unknown`.
- RC4. State `RELEASE`: the rule of §9.4 with W2 as the serving writer instance; W2's release records are
  `w2-<k>/release-intent.json`, `w2-<k>/window-release.json`, `w2-<k>/release-withheld.json`,
  `w2-<k>/release-not-owner.json` and `w2-<k>/release-failure.json`.
- RC5. `FRONT_TERMINAL`, `EXPORT` and `FINAL` as in mode `seal`; the front terminal record carries `recovery: true`
  and the recovery result.

**No inference from missing evidence.** W2 never concludes that a participant did not exist because a record is
missing, and `target_started` follows §9.3 (C's refusals). The classification always evaluates the whole predicate.

**Authority.** W2 uses only the reviewed rules: S3 is the `sicarii`→`wlscratch` writer rule, and W2's S_O uses the
`wlscratch`→root RL rule exactly as W's observers do, with `recover` as O's stage. W2 writes only inside `w2-<k>/`,
A's attempt journal and A's export increments (§5.2). F alone releases. If W2 or O cannot run (a sudo refusal, a lease
that never becomes free, a refusing O), no complete classification exists, and the window is held (§9.4).

**When F does not run recovery.** If F never wrote the window (a refusal before D12, or `RESERVE_ABORT`), there is
nothing to release; F still runs W2 in mode `seal` if `attempt.json` is committed (otherwise F's terminal facts stay on
its console). If F dies, nobody releases: the window is held for manual resolution (§9.5), as in v3.

### 9.8 Custody by the target view [corrections: W1-V6-PRESERVE, W1-V6-READ-MUTATION, W1-V6-SCAN-STATE; v6: W1-V5-REVOCATION-CONFINEMENT; v5: W1-CUSTODY-CLOSURE]

v6's §9.8 (the in-place and copy routes, the lease test, the fresh roots and the root exchange, K0-K8) is withdrawn.
Its K0 obstruction stands exactly as the review ruled it (§22): for the unprivileged userspace/DAC architecture and an
already-shared writable open file description, no preserving mechanism was identified. v7 changes the architecture so
that no description of an admitted entry can be shared with, and no name for one obtained by, a principal outside the
attempt's own process tree, and so that every holder in that tree ends with one atomic, absorbing kernel event.

**N0. The obligation.** From the final pass to T's `exec` (V5-B01, second sentence) and across every frame mutation
(V5-B02): (a) only root, W and the attempt's own frame helpers (RL, L, C) can change the admitted generation or hold a
description of, or a name for, an admitted entry; (b) every frame mutation lies in T or is v5's window protocol.

**N1. Push routes** (a process of a view hands a descriptor to another process).
- `SCM_RIGHTS` over inherited sockets: a process of a view holds only `/dev/null`, its stream files and, for L, C and
  O, its channel socket to W (§7.1); T receives only `/dev/null` and its two stream files (C11). W reads its sockets
  with `recvmsg` and a zero-length control buffer, so a descriptor that L, C or O sends is discarded by the kernel
  (`MSG_CTRUNC`) and never installed in W; W records it as a channel failure.
- Pathname sockets: Landlock's `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` is handled and granted nowhere, so a process of the
  view can connect, or `sendmsg` with an address, only to a UNIX server created inside its own domain (the installed
  `landlock.h` text, Appendix G). Its `LANDLOCK_ACCESS_FS_MAKE_SOCK` is granted only beneath the three private binds
  (the run path, `/tmp`, `TMPDIR`), so every socket file it creates lies in g, which no outside principal can reach
  (N3).
- Abstract sockets: their namespace is the network namespace, and the view's is private (§12.2); no outside principal
  can enter it (`setns` needs `CAP_SYS_ADMIN` over its owner, the initial user namespace; `/proc/<pid>/ns/net` needs
  ptrace access, N2).
- Other descriptor-passing interfaces: binder needs a shared binder device; none exists on the host (no `/dev/binder`,
  `/dev/hwbinder`, `/dev/vndbinder` or `/dev/binderfs`, observed 2026-10-05, Appendix G; the kernel builds binder with
  binderfs), and T cannot mount a binderfs (P-LL); `io_uring`'s `IORING_OP_MSG_RING` needs a descriptor of the
  receiving ring, that is, an existing channel; `pidfd_getfd` is a pull (N2).
- So every process that can receive a descriptor from a process of the view is in the same view and scope, or is W,
  which discards it.

**N2. Pull routes** (a process outside takes a descriptor, a name or memory from a view process): `/proc/<pid>/fd/*`
(open and `readlink`), `/proc/<pid>/{cwd,root,exe,map_files,mem,environ}`, `pidfd_getfd`, `ptrace` attach or seize,
`process_vm_readv`, `process_vm_writev` and `kcmp` each require ptrace access to the view process (read-fscreds or
attach-realcreds mode). A non-root principal outside the view has no uid R, the view's user namespace is owned by root,
so it holds no capability over the view's processes, and Yama `ptrace_scope=1` limits attach to descendants. The
frame's own helpers (L, C, O) are non-dumpable (§7.7), so T, which has uid R, cannot take from them either. An
unprivileged fanotify group reports file identifiers, not descriptors, and can mark only inodes its owner reaches by
path, which excludes g. Premise P-PTRACE, with the complete matrix of §13.

**N3. Names.**
- Paths: g grants search permission to nobody but W and root (§6.3). Every mount of a view is private (no propagation
  in either direction, P-PROP), so the binds of `g/source`, `g/tmp` and `g/tmpdir` exist only in the view's mount
  namespace, which no outside principal can enter or reach through `/proc/<pid>/root` (N2).
- New names: a hard link or rename from a bind into any other mount of the view fails with `EXDEV` (P-XDEV), so every
  name of an admitted entry stays in g; no process of the view can mount, bind or move a mount, because Landlock forbids
  filesystem-topology changes to a process whose domain restricts filesystem access (P-LL), and the view's mount
  namespace is owned by the initial user namespace.
- No mount lies below the run-path bind: the view's mountinfo in `launcher-rl-identity.json` has no mount point at or
  below the run path other than the bind itself, and nothing can add one (above). This is the exact predicate in place
  of v6's "same `st_dev` means no mount boundary" (correction W1-V6-SCAN-STATE): `st_dev` equality is evidence of
  nothing here, because a bind of the same filesystem has the same `st_dev`. The walks record each entry's `statx`
  mount ID for review; they add no refusal (§6.5).
- File handles: a principal holding a handle's bytes (T could write them into a shared file) cannot open the entry:
  `open_by_handle_at` requires `CAP_DAC_READ_SEARCH` in the initial user namespace or, in the relaxed mode of recent
  kernels, a directory, `CAP_SYS_ADMIN` over the mount's namespace, no locked mount above, and every ancestor's owner
  and group mapped in the caller's user namespace, which fails at g's W-owned ancestors. Premise P-FH: the drafting
  author's reading of the upstream kernel, not available on this host; probe P-FH.

**N4. Holders that outlive the run.** Every holder of a description of an admitted entry other than root and W is a
process of an attempt scope or an observer scope (N1-N3, CRED). What a scope's processes hold, in descriptor tables,
mappings, `io_uring` registrations or queued messages, belongs to them or to sockets only they hold. When the scope
is `populated 0` none of them remains; a descriptor queued in a socket that no process holds can be received by
nobody, because receiving needs a descriptor of that socket, and a bound path only delivers into a queue; and the
`io_uring` and AIO requests of an exiting task are completed or cancelled before its threads leave the cgroup
(premise P-IOEXIT). The census at the parent stage, at C7 and at C10 requires every earlier scope `populated 0`, and
that state is absorbing (§9.4). So at the final pass no holder outside the current attempt's helpers exists, and none
can arise before T's `exec`. This replaces v6's K2 (no new holder after an observation) and its descriptor scans.

**N5. RL's privileged effects** (V5-B02: no outside-tree frame write). RL writes no file on any host filesystem. Its
effects are: the transient scope, created by the system manager on `systemd-run`'s request; the namespaces it creates
and their settings (the user namespace's `uid_map`, `gid_map` and `setgroups`, the network namespace's loopback
state); the mounts of its private mount namespace, whose mount points all exist beforehand (the lead-created run path,
`/tmp`, `TMPDIR`, the masked W-1 directories), the masks being fresh empty read-only `tmpfs` mounts; its Landlock
domain; and its own credentials. Its reads of records in T use `O_NOATIME`, which root may use on any file.

**N6. Read-side effects of the frame** (correction W1-V6-READ-MUTATION; the review ruled that an atime update caused by
a frame read is a frame-caused mutation under V5-B02). Every route by which a frame process reads a file or lists a
directory, with its effect:

| Route | Reads | Mechanism | Effect | Status |
|---|---|---|---|---|
| R-a | W, W2: records, recipe and snapshot in T | `O_NOATIME` (W owns them) on files and directories | none | inside T; closed |
| R-b | C, O: every entry below the view's `source/`, files and directories, recorded or excluded, and the report `obj/core/gnatprove/gnatprove.out` | `O_NOATIME`: through the run-path idmap the reader owns every entry (on-disk W shown as R), because the target can create entries only as R and nothing else can create, link or move an entry there (N3) | none | inside T; closed |
| R-c | F: `sicarii`-owned lead inputs (base tree files and directories, overlay, review directories, rollouts, transcript prefix, window file, inbox) | `O_NOATIME` (F owns them); every entry of the pinned base and of the toolchain was `sicarii`-owned on 2026-10-05 (Appendix G) | none | closed |
| R-d | F: a lead input not owned by `sicarii` (possible for any input, because v5 pins no owner; on 2026-10-05 no entry of the pinned base was such) | `O_NOATIME` fails with `EPERM`; F reads it without the flag, as v5 did, and records `atime_route: foreign` | a possible atime update of a file outside T whose location `sicarii` controls | **V5-B02 OPEN for this route** (no preserving mechanism identified; refusing would narrow an accepted case) |
| R-e | C, O: `sicarii`-owned files outside `source/` in the view (toolchain hashing for the tool, proof-data, proof-ELF and vendor observations; `TMPDIR`'s identity) | `O_NOATIME` (through the root view's idmap the reader owns them) | none | closed |
| R-f | every frame process: root-owned files (interpreter, standard library, installed frame, `setup-identities.json`, `/etc`, `/usr` files hashed by the observations) | `O_NOATIME` is not permitted to a non-owner without `CAP_FOWNER`; RL is root and uses it | atime updates under `relatime`, as v5's frame caused, on root-owned objects whose location only root can change | **V5-B02 OPEN for this route**: location custody is root's, but the mutation is outside T and not in the window protocol; a `noatime` view would change T's own atime behaviour, and F, W and W2 run in the host namespace |
| R-g | every frame process: `/proc`, `/sys`, cgroupfs | pseudo-filesystems | no persistent state | closed |
| R-h | C's `execve` of the target executable and the loading of its libraries (the first acts of T's run) | none possible for an `exec` | atime of `sicarii`-owned toolchain files | **V5-B02 OPEN for this route** unless review rules it part of the target's run (R3, R4); this proposal does not decide that |

v6's K5 and K8 statements ("no frame mutation" universally; reads in "one place only") are withdrawn; this table
replaces them. W1-V6-READ-MUTATION is answered by this inventory and by the three OPEN routes, not closed.

**N7. Premises** (each NAMED_UNESTABLISHED until its probe of §13.1 and, where stated, a source-level reading in the
installed-evidence review pass; if one fails, W-1 must be redesigned, and no accepted case is narrowed):

| Premise | Statement | Probe |
|---|---|---|
| P-NS | RL's namespaces are created as §12.2 states, owned as stated; no `user@W`, `user@R`, `/run/user/W` or `/run/user/R` ever exists | P-NS |
| P-IDMAP | idmapped mounts show and store ownership as §12.2's maps state; an unmapped id cannot be written; the reader is the owner for `O_NOATIME` through the map | P-IDMAP |
| P-LL | the Landlock domain of §12.2: `RESOLVE_UNIX` admits own-domain servers only; `MAKE_SOCK` only beneath the private binds; `REFER` granted everywhere leaves every same-mount rename and link as without Landlock; no mount, unmount, bind or `pivot_root` | P-LL |
| P-XDEV | `link`, `rename` and `renameat2` across two mounts of one filesystem fail with `EXDEV` before any permission check | P-XDEV |
| P-PROP | no mount event propagates between a view and the host in either direction | P-PROP |
| P-PTRACE | N2's operations fail for every non-root principal outside the view, in the initial user namespace and in one it creates | P-PTRACE |
| P-FH | N3's file-handle statement | P-FH |
| P-CG | `populated` semantics; no process enters a `wlscratch.slice` cgroup except by fork inside it or by root; `io_uring` workers are members of their task's cgroup | P-CG |
| P-NOR | only RL confers R or GATE (§5.3), and only inside a new scope | P-NOR |
| P-IOEXIT | no write by a former member of a depopulated scope can still modify a file | P-IOEXIT |
| P-NOATIME | the `O_NOATIME` opens of routes R-a, R-b, R-c and R-e change no atime | P-NOATIME |
| P-NOSUID | every view mount is `nosuid`; the flag is locked for every namespace a view process creates; set-ID bits and file capabilities do not take effect | P-NOSUID |
| P-LOCK | the masks and binds of a view cannot be separated, unmounted or revealed by a nested namespace | P-LOCK |
| P-VIEW | every original observation taken in the view equals its original baseline (§8.4) | first engineering run |
| P-CENSUS | a scope unit is active exactly while its cgroup is populated (§9.4) | P-CENSUS |
| P-ENOSPC, IMG | carried unchanged (§10.4, §14.5) | P-ENOSPC; P-MOUNT and P-IMAGE |
| TOOL-CLOSURE | the preservation premise of §22.4 | the source-grounded toolchain review of §22.4 (engineering runs bound it, never establish it) |

**N8. What remains outside:** root and the kernel (R8); a writer instance running changed code (outside the threat
model, as before); availability (R6); the target's own confinement outside g (R3).

## 10. Commits, journals, retries, durable fallback and durability-UNKNOWN [corrections: W1-COMMIT-JOURNAL-EXPORT, W1-DURABILITY-RELEASE; gap: commits-and-durable-channel]

### 10.1 Commit primitive (N11) [correction: W1-V6-COMMIT-AMBIGUITY]

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

**Commit point.** A record is committed exactly when the link of its close marker (§10.2) has happened, and at no other
moment. A failure at any step before that link decides nothing for any reader: no close marker exists, so the record
is not committed for any consumer, and its named bytes, if its own link happened, are "written, uncommitted": raw
evidence, never parsed as valid input (v5 `retain` already never reused a partial primary). A failure after that link
changes nothing about commitment: a failed directory `fsync` or post-link join leaves the record committed for every
consumer, with `synced: false` (§10.5). Because a close marker can appear only by the link of an inode that is already
complete, synced and validated, no state exists in which a reader finds a valid close marker that its writer treats as
failed, and no continuation is ever needed to retract one. The review's case, "a complete valid close whose fsync,
directory fsync, post-validation or join failed and whose continuation is absent or fails before producing a valid
file", splits accordingly: a failed file `fsync` or validation happens before the link, so that close marker never
gets a name; a failed directory `fsync` or join happens after the commit point, so that record is committed, unsynced,
for the writer and for every reader, export and post-reboot interpretation alike (§9.6: after a crash, a close marker
whose entry did not reach the disk is absent and its record uncommitted, which the writer's `synced: false` already
reported as possible).

Export copies are committed by the export primitive of §15.3: the same steps, with the export's final mode and ACL
applied to the unnamed inode by `fchmod` and `fsetxattr` before its validation and link.

### 10.2 Markers, journals and the committed chain [corrections: W1-V6-COMMIT-AMBIGUITY; v6: W1-V5-JOURNAL-FAILED-CLOSE; v5: W1-JOURNAL-CONTINUATION]

v4's rule let a torn or unlinked marker end the committed chain while a later writer skipped its seq and linked to the
previous head (review R3). v5 had one rule, the same for every reader and writer, with no case in which a marker both
ends the chain and is bypassed by a successor treated as committed. v5's J4 still let the continuation after a failed
close marker link to the record-bearing marker whose close had failed, and so confirm that record, while §10.3 retried
and downgraded it (review W1-V5-JOURNAL-FAILED-CLOSE). v6 made a record-bearing marker's only possible successor its
own close marker and linked a continuation only to a record-free marker, but a valid close marker whose writer saw a
later step fail could still confirm a record that its writer retried (review W1-V6-COMMIT-AMBIGUITY). v7 puts every
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
     confirmed chain element. RAW files are retained and listed by exports (§15.3); they are never parsed as valid
     input and never get success credit.
  A torn or unlinked marker therefore ends the chain only while no continuation lists it, and once one does it is RAW
  and outside the chain; nothing it carries is ever committed.
- **Commit primitive (completing §10.1).** A record is committed by three create-only links: the record (§10.1), its
  record-bearing marker M (linked to the head as J2-J4 below require), and a `close` marker with `prev_commit` = M's
  digest and the next seq. Each is fully written when §10.1 steps 1-3 succeed for it. A failure in those steps for any
  of the three, or a failed directory `fsync` of the record or of M (both precede the close marker's link), is a failed
  commit: the record is not committed (rule 3), and it follows §10.3 (retry with its downgrade, then fallback). Once
  the close marker is linked, the commit has succeeded; a failure of its directory `fsync` or join is reported as
  `synced: false` (§10.5) and never retracted. Wherever this document says that a record and its marker are committed,
  or that a journal or a prefix ends at, or is cut at, a record's marker, it means this primitive and the close marker
  that confirms that marker. Between commits the head is therefore always record-free.
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
    is linked, with `synced` true or false, and it never reports, records or relies on a belief that the rule
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
  marker was never linked is uncommitted for every one of them: its record bytes and markers are RAW, listed by the
  exports and never parsed as valid input, and its state for every consumer is that of the retry or the fallback, with
  the failure and the downgrade (§10.3, §10.6). A record whose close marker was linked is committed for every one of
  them, and its `synced: false`, if any, travels with it in every later record, in `FINAL` and in the exports. Files
  lost or torn by a crash change the answer only by making later markers RAW or a record uncommitted; such an attempt
  is non-success by §9.6 in any case.
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

### 10.5 Durability-UNKNOWN

If primary, retry and fallback all fail for a record, that record is **durability-UNKNOWN**: the writer sends
`RECORD_UNKNOWN {name, value_sha256, value_bytes, errors}` to F, writes the facts to its stderr (v5 `last_resort`),
records `durability: UNKNOWN` in every later record it can still commit, and the attempt cannot succeed. A record
committed only to a fallback slot is `fallback`: it earns no success credit either. A record whose close marker was
linked but whose directory `fsync` or post-link join failed (§10.1) is committed for every consumer and **unsynced**:
the writer sends `RECORD_COMMITTED` with `synced: false`, records `durability: UNKNOWN` for it in every later record,
and the attempt cannot succeed; it is not retried, because it is committed and a retry would add a second committed
version. F prints every `RECORD_UNKNOWN`, `RECORD_FALLBACK` and unsynced commit to its console; that output reaches the
lead's tool output and transcript, written by the harness, not by the frame, and is not durable if F dies or the
transcript filesystem fills. Effect: no success or acceptance credit, and the uncertainty is preserved and reported;
no hold, no effect on the window and no approval gate (§9.4).

### 10.6 Consumers (complete)

**Precedence for every record name N:** the committed primary; else the committed retry (with its downgrade); else a
VALID fallback slot naming N (state `fallback`: never success credit; a truncated payload gives only digest and size);
else raw uncommitted bytes of N (state `raw`: evidence only, never parsed as valid input); else `unknown`. TORN slots
name nothing. A committed primary or retry carries its `synced` value.

| Consumer | What it uses | Rule |
|---|---|---|
| C | record bytes W delivers over SP_C | only committed primary or retry records; their sha256 must equal W's in-memory descriptors and the seals; fallback and raw bytes are never delivered |
| RL | `launch.json` and `admission.json` read from P_att by anchored chain | their sha256 must equal its argv's seals; nothing else is read as input |
| W's attempt-journal join (D8, C4, C8, the conclusion) | every record of the attempt | each committed record still has its committed sha256, size, mode, single link and ACL state (export copies: their final export values); `fallback.journal` has the identity and size of `fallback-allocation.json`, every slot below the in-memory next index is byte-identical to what this writer last read or wrote (after a failed slot write it reads the slot back), and every slot at or above it is EMPTY; no content digest of the journal is ever compared; the journal's committed chain is unchanged up to the in-memory head |
| F | descriptors from `*_COMMITTED`, `RECORD_FALLBACK`, `RECORD_UNKNOWN`, `EXPORTED` | in memory; export copies re-read and compared with their final values (§15.3) |
| The conclusion, `result.json`, `final-status.json` | every expected record | `record_states` maps each name to `primary`, `retry`, `fallback`, `raw` or `unknown`, with `synced`; success needs every required record `primary` or `retry` and synced |
| The classification (N12) | participant records | exact schema validation (Appendix B.2); only committed records are participant evidence; a fallback, raw or missing participant record removes no participant (participants are classified by U's state and v5's terminal predicate, §9.4); a parseable record with a missing or mistyped field is unresolved and makes its participant UNKNOWN |
| W2 | A's journal and records | the committed chain only (§10.2); slots by this section's interpretation |
| Exports and reviewers | export increments | §15.3: committed records copied with their `synced` value; fallback slots decoded or listed; raw records listed by digest |
| A writer after a reboot | earlier attempts | interpretation only (§9.6); never an admission input |

- **Stream finality.** After every launch participant's wait is recorded and before `result.json`, W closes its own
  copies of the stream descriptors, syncs the stream files and records their `stat_key`, and requires the census to
  show U absent or `populated 0`. Every other holder of a stream description is a process of U (W passed them only to
  L and C, and C only to T; N1-N4), so once U is depopulated no writable description of a stream remains outside W, and
  W's copies are closed. If U is still populated when W concludes (a target process still runs), `stream-finality.json`
  records it, the streams are not final and success is withheld, with no effect on release. v6's lease test of the
  streams is withdrawn.
- **Error joins.** Every `record_errors` list, `*-failure.json`, `conclude-errors.json`, channel failures,
  durability-UNKNOWN, unsynced and fallback entries, TORN slots and raw records are joined into the conclusion,
  `final-status.json` and the front terminal record.

### 10.7 Exit statuses and success, per verb (N13, N14) [correction: W1-PROTOCOL-FAILURE-STATES]

- **W, `dispatch` (N13).** `success` = v5's conjunction (launched, scope wait 0, child wait 0 and clean, no error,
  post-identity clean, materialization unchanged, owned terminal) ∧ every required record `primary` or `retry` and
  synced ∧ no `fallback`, `raw` or `unknown` record ∧ the attempt journal not branched ∧ streams final ∧ released (F
  reported `RELEASE_DONE` with a re-read showing the release) ∧ the release records committed ∧ export increment 0
  frozen. v5's "scope wait" is the relayed status of the RL/L/C pid in `launcher-wait.json` (§9.2). Errors appended
  after `result.json`, including late handle-close and export errors, force `success = false`, are committed as
  `conclude-errors.json` (or to the fallback journal), and make W exit 1. `final-status.json` records the final values.
- **W, `materialize`.** `success` = `materialization.json` committed after M8's verification ∧ `verify_materialization`
  against it passed ∧ the generation export frozen (M9) ∧ A0's export increment 0 frozen ∧ every required record of the
  generation journal and of A0's attempt journal `primary` or `retry` and synced, none `fallback`, `raw` or `unknown`,
  neither journal branched ∧ no `EARLY_REFUSAL` or `REFUSAL` ∧ no error. The vault stage's outcome (M10) is recorded and
  reported in `FINAL.vault` and is not a condition: v5 `materialize` ran no vault command (Appendix E), while
  `dispatch` keeps v5's vault requirement (J9, `run` S:1562-1563).
- **W, `adopt`.** `success` = `lead-adoption.json` committed and `ADOPTED` sent ∧ the adoption export increment frozen
  ∧ every record of the invocation `primary` or `retry` and synced (adopt has no fallback journal, so a record that is
  not committed is `unknown`) ∧ the adoption journal not branched ∧ no error.
- **W2, mode `seal`.** `success` = `w2-<k>/identity.json` and `front-terminal.json` committed ∧ its export increment
  frozen ∧ every W2 record `primary` or `retry` and synced ∧ no error.
- **W2, mode `recover`.** The `seal` conjunction ∧ the recovery verdict `known-terminal` ∧ the window released for this
  attempt (by F in this W2's `RELEASE` state, or earlier in the attempt, as F's terminal record states) ∧ the release
  record of this W2's `RELEASE` state committed.
- Each writer exits 0 iff its `success` holds, 1 otherwise, and 125 only on a first-act failure (§7.7).
- **F (N14).** `dispatch`: exit 0 only if W's `FINAL` reports success and release, F's own error list is empty, no
  interrupt reached F, S1's raw status is 0, W2 (mode `seal`) reported success and S3's raw status is 0, and nothing is
  `fallback`, unsynced or durability-UNKNOWN; a run that needed recovery exits 1 even if it released. `materialize`:
  exit 0 only if W's `FINAL` reports success, S1's raw status is 0, W2 (mode `seal`) reported success and S3's raw
  status is 0, F's own error list is empty, no interrupt reached F, and nothing is `fallback`, unsynced or
  durability-UNKNOWN. `adopt`: exit 0 only if W reported `ADOPTED`, `EXPORTED` with state `frozen` and a successful
  `FINAL`, S1's raw status is 0, F's own error list is empty and no interrupt reached F (no W2 runs for `adopt`).
- **C, L, O, RL.** C keeps v5's rule (`code` if it is not `None` and there were no failure, notes or errors, else
  `code or 1`); L never exits once it has `exec`ed C, and exits 125 when it started nothing (a failed G4 check, EOF,
  deadline or `STOP` before its `exec`, or a failed `exec`); O exits 0 only if its observation succeeded; RL never
  exits after its `exec` of L or O, and exits non-zero on any refusal before it.
- **No success predicate gates release.** Release follows §9.4's rule only. Durability, export and success outcomes
  are reported; none of them holds the window or adds an approval.

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

- W, R and GATE are explicit numbers fixed in the concrete inventory (candidates 950, 951, 952 as observed in §3.1).
- For each number n: `getent passwd n` and `getent group n` exit 2; n lies in 500-999 (`SYS_UID_MIN`-`SYS_UID_MAX`,
  `SYS_GID_MIN`-`SYS_GID_MAX`, the system range used by `useradd --system`, which allocates no subordinate range for
  system accounts); for every line
  `owner:start:count` of `/etc/subuid` and `/etc/subgid`, n < start or n ≥ start + count, each bound computed with
  JACKAL in the concrete inventory (all current ranges start at 100000 or above, observed); no file on any local
  filesystem is owned by uid n or group n (P4).
- After setup: `/etc/subuid` and `/etc/subgid` byte-identical to their prestate; `getent` shows exactly the two new
  users and the three new groups; `/etc/shadow` password fields of W and R begin with `!` (or `*`); the `gshadow`
  entry of GATE has no members and a locked password.
- v6's provision for moving R to a regular uid (for a lingering manager) is withdrawn: R has no manager. R stays a
  system uid outside every subordinate range, and RL maps it only into the user namespaces it creates (§12.2).

### 11.3 Prestate inventory (read-only; "lead" = unprivileged agent, "operator" = needs root)

| Id | Check | Runner | Required |
|---|---|---|---|
| P1 | `getent passwd wlscratch`, `getent passwd wlscratch-run`, `getent group wlscratch`, `getent group wlscratch-run`, `getent group wlscratch-gate` | lead | each exits 2 |
| P2 | `getent passwd <n>`, `getent group <n>` for every candidate | lead | each exits 2 |
| P3 | contents, digests and `lstat` of `/etc/subuid`, `/etc/subgid` | lead | every candidate outside every range; files root:root 0644 |
| P4 | `find <fs> -xdev \( -uid <n> -o -gid <n> \) -print -quit` for `/` and each other local non-FUSE filesystem (never `~/iPad`, `~/iPadBackup`) | operator | empty |
| P5 | `absent.py` on `/var/lib/wlscratch`, `/opt/wlscratch`, `/etc/ssh/sshd_config.d/30-wlscratch.conf`, `/etc/systemd/system/wlscratch.slice`, `/etc/tmpfiles.d/wlscratch.conf`, `/var/spool/mail/wlscratch`, `/var/spool/mail/wlscratch-run`, and with images `/var/lib/wlscratch-images` and the mount-unit paths | lead; every `undetermined` repeated by the operator | `absent` each |
| P6 | before any staging exists, so without running any helper as root: `find /etc/sudoers.d -mindepth 1 -maxdepth 1 \( -name wlscratch-frame -o -name wlscratch-run \) -print` (a complete listing of the root-only directory; no symlink is followed) | operator | exit status 0 and empty output; a non-zero exit is `undetermined` and refuses. The staging directory needs no separate check: S-0 creates it with a create-only `mkdir`, and S-D re-checks both names with the staged `absent.py` |
| P7 | `lstat` of `/`, `/var`, `/var/lib`, `/opt`, `/etc/ssh/sshd_config.d`, `/etc/systemd/system`, `/etc/tmpfiles.d`; `getfacl -n -c` of `/var/lib` and `/opt` | lead | root-owned, no extended ACL |
| P8 | `protected_hardlinks`, `protected_symlinks`, `protected_regular`, `ptrace_scope`, `suid_dumpable`, `max_user_namespaces`, `max_mnt_namespaces`, `max_net_namespaces`, `kernel.unprivileged_bpf_disabled`, `kernel.io_uring_disabled` | lead | as in §2.3; the rest recorded |
| P9 | `findmnt` of `/`, `/var/lib`, `/opt`, `/tmp`, `/var/tmp`, `/dev/shm`, `/run/user`, `/proc`, `/sys/fs/cgroup`; the complete `/proc/self/mountinfo` with the FUSE mounts below `/home/sicarii` listed but never touched | lead | as in §2.3 (`/proc` without `hidepid`; `/tmp` and `/var/lib` on one mount, for §13); the mount list is the input of §12.2's view table |
| P10 | digests of `/etc/pam.d/{sudo,system-auth,system-login,system-remote-login,sshd,su,su-l,runuser,runuser-l,login,other}` | lead | `sudo` keeps `session optional pam_systemd.so class=none` |
| P11 | digests of `/etc/ssh/sshd_config` and drop-ins; `systemctl show sshd.service -p ActiveState -p UnitFileState`; `sshd -T` | lead; operator for `sshd -T` | recorded; gives the expected `denyusers` line |
| P12 | `sudo --version`; digests of `/etc/sudoers` and every `/etc/sudoers.d` file; `visudo -c`; `sudo -l -U sicarii` | lead for the version; operator | §2.3 privilege-route precondition holds |
| P13 | digests of `/usr/share/polkit-1/rules.d/*`; listing and digests of `/etc/polkit-1/rules.d`; `getent group empower wheel docker` | lead; operator for `/etc` | no rule grants `sicarii` or any of its groups a passwordless `YES` for an action that runs code as another user (for example `org.freedesktop.systemd1.manage-units`, `org.freedesktop.policykit.exec`, machine shell or login actions); `empower` and `docker` without members |
| P14 | `absent.py` on `/usr/bin/crontab`, `/usr/bin/at`, `/usr/bin/batch`, `/var/spool/cron`, `/var/spool/at`, `/var/spool/atjobs`; `systemctl show cronie.service atd.service -p LoadState` | lead | `absent`; `not-found` |
| P15 | listing of `/var/lib/systemd/linger` | lead | recorded (no new linger file is created) |
| P17 | `find / -xdev -perm /6000 -type f` with digests; `getcap -r /usr` | operator | baseline for S-I |
| P18 | `readlink -f /usr/bin/python3`; sha256 of `/usr/bin/python3.14` and `/usr/lib/libpython3.14.so`; `sys.version` | lead | observed `/usr/bin/python3.14`, `c6bc1ef4…`; 3.14.7 (the lead's earlier observation, reproduced by the re-review) |
| P19 | `systemctl --version`, `setfacl --version`, presence of `/usr/bin/nologin`, `/usr/bin/visudo` | lead | recorded (systemd 261 and sudo 1.9.17p2 are the lead's earlier observations) |
| P20 | `cgroup.subtree_control` of `/sys/fs/cgroup` and of `system.slice`; `systemctl show wlscratch.slice -p LoadState -p FragmentPath -p DropInPaths` | lead | `memory` and `pids` among the controllers; `FragmentPath` and `DropInPaths` empty (systemd loads a slice without a unit file, so `LoadState` alone shows nothing) |
| P22 | the frozen v6-W1 inventory digest and the review-freeze digests that the install will use | lead | recorded |
| P23 | `/etc/default/useradd` (`CREATE_MAIL_SPOOL` and the other defaults) | operator (unreadable to the lead: `Permission denied`, observed 2026-10-05) | recorded; the expected-object list of S-I follows it |
| P25 | kernel and features: `uname -r`; `/sys/kernel/security/lsm`; `/proc/config.gz` (`CONFIG_USER_NS`, `CONFIG_NET_NS`, `CONFIG_SECURITY_LANDLOCK`, `CONFIG_ANDROID_BINDER_IPC`, `CONFIG_ANDROID_BINDERFS`); the installed `linux-api-headers` version and its `landlock.h`; `absent.py` on `/dev/binder`, `/dev/hwbinder`, `/dev/vndbinder`, `/dev/binderfs` | lead | as in §2.3; the binder devices `absent` |
| P26 | `/usr/lib/tmpfiles.d/tmp.conf`; `systemctl show systemd-tmpfiles-clean.timer -p ActiveState` | lead | the `/tmp` age that S-F's rule repeats; the timer active |

P16, P21 and P24 (v6's user-unit listings, Option A's home ACL captures and the user-manager unit) are withdrawn with
the mechanisms they served.

Observed on 2026-10-04 by the drafting author (passive reads): the `/etc/passwd` and `/etc/group` entries at or
above 900 (§3.1, for P1/P2); P3 (§5.4); `/etc/login.defs` ranges; P5 for `/var/lib/wlscratch` and `/opt/wlscratch`
(absent from the listings of `/var/lib` and `/opt`); P8 (`protected_*` 1, `ptrace_scope` 1, `suid_dumpable` 2,
`max_user_namespaces` 128053); P9; P10 (the `sudo`, `system-auth`, `system-login`, `system-remote-login`, `sshd`,
`su` and `runuser` stacks); P11 (sshd active; drop-ins `20-systemd-userdb.conf` and `99-archlinux.conf`; `UsePAM yes`;
`AuthorizedKeysFile .ssh/authorized_keys`; `AuthorizedKeysCommand /usr/bin/userdbctl ssh-authorized-keys %u`); P13
(the two `/usr/share` rules files read, the `/etc` directory unreadable); P14; P15; P18 (path and digest).

Observed on 2026-10-05 by the drafting author (passive reads; Appendix G): P9's mount IDs (`/tmp` and `/var/lib` both
32, on `/dev/vda` ext4) and the full mount list; `/var/spool/mail` present (mode 1777) with `MAIL_DIR /var/spool/mail`
in `/etc/login.defs`; P23's refusal; P8's `kernel.unprivileged_bpf_disabled` 2 and `kernel.io_uring_disabled` 0; P20
(`cpuset cpu io memory pids` at the root and in `system.slice`; `wlscratch.slice` `LoadState=loaded` with empty
`FragmentPath` and `DropInPaths`, as for any other slice name); P25 (kernel `7.2.6-1-aarch64-ARCH`, LSMs
`capability,yama,landlock`, the listed configuration options, binder built with binderfs and no binder device present);
P26 (`q /tmp 1777 root root 10d`, `q /var/tmp 1777 root root 30d`; the timer `active`); `/etc/tmpfiles.d` empty. These
are observations only; the concrete inventory repeats them fresh.

### 11.4 Protected reviewed-byte staging, checked execution and reconciliation [corrections: W1-V6-COMPOSED-STATE; v6: W1-V5-RECONCILIATION-STATES; v5: W1-SETUP-RECONCILIATION; v4: W1-SETUP-PROBES-ROLLBACK]

- Every privileged byte is part of the reviewed concrete inventory with its sha256: both sudoers files, the sshd
  drop-in, the slice unit, the tmpfiles rule, every expected ACL text, every expected output that `check_out.py`
  compares, the identity-record generator, the helpers `absent.py`, `step.py` and `check_out.py`, the scripts S-A to
  S-J, S-R's atom table, every frame member and the member/directory lists. Every list file a script reads ends with a
  newline and holds one plain name per line; the staging review checks both, so a `read` loop never drops a last line.
- **S-0 (operator, root):** create `/root/wlscratch-staging` with `mkdir -m 0700` (create-only: `mkdir` fails with
  `EEXIST` for any existing entry at that path, a dangling symlink included, so no stale staging tree can be reused)
  and verify root:root 0700 with `stat`; copy the staging manifest from the lead's frozen inventory directory with
  `install -m 0600`; verify it as root with `echo "<MANIFEST_SHA256>  $st/staging-manifest.sha256" | sha256sum -c
  --strict -`, where the digest is the one in the sealed review record (the procedure's only pipeline: its producer is
  the shell's `echo` of a constant line, and the pipeline's status is `sha256sum`'s own, which decides); copy every
  listed file the same way; verify all as root with `sha256sum -c --strict`; create `log/` (0700) and, with `O_EXCL`,
  one empty log file per script (0600). The lead-writable source can change after review, which is why only the
  root-owned copies, checked as root, are ever used. v2's predictable lead-owned `/tmp` files are not used.
- **Execution and status handling.** Each script runs as `sudo sh -eu /root/wlscratch-staging/S-<x>.sh` from the
  verified copy. On this host `/usr/bin/sh` and `/bin/sh` are bash, and the installed bash(1) states that a pipeline's
  status is that of its last command unless `pipefail` is set, and that `-e` ignores a failure of any command in a
  pipeline but the last (Appendix E). v4's statement that under `-e` a failing pipeline command stops the script is
  therefore withdrawn (§0.5 item 10). The scripts never rely on `-e` to observe a producer:
  1. no script contains a pipeline; a command whose output is checked runs under `check_out.py` (§11.5), which runs it
     without a shell and exits 0 only if the command's own exit status is 0 and its output passes the stated check;
  2. a command substitution is used only as the whole right-hand side of an assignment (`v=$(…)`), whose status is the
     substitution's and stops the script under `-e`, and never inside a test, a `case` word or an argument;
  3. a command whose non-zero status is an expected answer is written `rc=0; cmd || rc=$?` and followed by a `case` on
     `$rc` that names every accepted value and stops on every other (`no_entry`, §11.5);
  4. there is no `cd` and no subshell; checksum files name absolute paths;
  5. an `if` condition holds only an explicit test whose every outcome the branch handles (the syntax checks of S-D and
     S-E, whose failure leads to the reviewed removal below and a stop).
  Installs read only from the staging copies (`install -o -g -m`); there is no `cp -a` and no recursive `chmod`.
- **Atoms and their effects** (correction W1-V6-COMPOSED-STATE). Every numbered step of a script is one *atom*: it
  changes one object (a group, an account, a directory, a file, the ACL of one object, a unit's enablement, an image
  file with its filesystem), or it only checks, or it is a service action (`daemon-reload`, `systemctl reload sshd`).
  Steps that touch several objects are split into sub-steps `<n>.<i>`, and a loop over a list (frame directories and
  members) makes each iteration its own sub-step. An atom's effect is not limited to its object: creating or removing
  an entry changes its parent directory's entry set, and for a directory also the parent's link count; `groupadd`,
  `useradd`, `userdel` and `groupdel` change lines of `group`, `gshadow`, `passwd` and `shadow`; a service action
  changes what its service reports. The reviewed S-R table gives each atom k its *effect set* E(k): its object o(k)
  with the fields it changes, and every co-effect with its object and fields. Example: S-B step 2 has o = `lease/`,
  absent → a directory root:W 0750 without ACL, and the co-effect on `/var/lib/wlscratch`: entry set + `lease`,
  `nlink` + 1. A check has no effect; a service action's effect is its observation and expected value where it has one
  (for `daemon-reload`, `systemctl show <unit> -p NeedDaemonReload -p DropInPaths -p FragmentPath` for every unit
  whose files the step's script changed), and otherwise none. A reversing action that also returns an earlier atom's
  object to its pre-state (`userdel` with `USERGROUPS_ENAB yes`, which removes the user-private group of the same
  name, §11.5) names that object as a *co-object* of the reversal.
- **One global phase.** Setup is one global sequence: the state-changing atoms of S-A, S-B, S-J (with images), S-C,
  S-D, S-E, S-F and S-H, in the order the procedure runs them (§16), numbered k_1 < … < k_N across scripts. The
  *global object set* O holds every object that any E(k) touches: among them every parent of a created entry
  (`/var/lib`, `/opt`, `/etc/sudoers.d`, `/etc/ssh/sshd_config.d`, `/etc/systemd/system`, `/etc/tmpfiles.d`,
  `/var/lib/wlscratch`, `lease/`, `runs/`, `/opt/wlscratch`, the frame directories, with images
  `/var/lib/wlscratch-images` and the mount-unit directory) and the account-database lines of the new names and
  numbers. The *global vector* G_j (j = 0, …, N) gives every object of O its state after k_1, …, k_j: its P-capture
  with the effects of those atoms applied in order. An earlier script's object that a later atom changes is therefore
  expected in its projected state (S-C's `/opt/wlscratch` gains `setup-identities.json` at S-H; `/var/lib/wlscratch`
  gains `lease` and `runs` and their link counts within S-B), and a later script's objects are expected in their
  pre-states, as G_j gives them. v6's per-script final vectors V_m and its rule "every earlier script in V_m, every
  later script in V_0" are withdrawn.
- **Partial vectors.** For atom k_(j+1) and each forward intermediate s of its class (§11.5), G_j^+(s) is G_j with
  E(k_(j+1)) applied as far as s states, co-effects included (for example a directory whose entry and parent link count
  exist but whose owner or mode is not yet set). For atom k_j and each reversal intermediate s, G_j^-(s) is G_j with the
  reversal of E(k_j) applied as far as s states. Where a reversal has a co-object, it passes through W_j, which is G_j
  with every co-object of the reversals of k_(j+1), …, k_N in its pre-state, and through W_j's partial vectors.
  These are exactly the states that the setup, its resumption and its reversal can leave, because the global sequence
  runs one atom at a time and every intermediate of every class is listed with its co-effects. G_0, …, G_N are
  pairwise different, because every state-changing atom changes its own object and no setup atom undoes another's
  effect.
- **Step logs (advisory).** `step begin <k>` before and `step done <k>` after each atom append lines
  `<UTC time> (begin|done) <k>` to `log/S-<x>.log` through `step.py`, which writes the whole line and syncs it or
  fails, and which refuses to append after a torn line (§11.5). A log is evidence of what ran; no object's state is
  ever decided from it.
- **No automatic undo is claimed; reconciliation S-R.** A stopped script can leave an atom between states (for example
  a group whose `gshadow` entry is missing, or an account without its lock). The only automatic action in any script is
  the removal, in S-D and S-E, of a just-installed configuration file that its own syntax check rejects, and only if
  its bytes still equal the staged copy, so that `sudo` and `sshd` stay usable. After any stop the operator runs the
  reviewed reconciliation `S-R <x>`, which:
  1. reads `log/S-<x>.log`: every complete line must match the grammar, and `begin` and `done` must alternate per atom
     in script order; a last line without a final newline is torn and is ignored (and reported); any other malformed or
     out-of-order line stops S-R for an explicit operator decision;
  2. observes every object of O, whichever script stopped, with the prestate methods (`getent`, `absent.py`, `lstat`,
     `getfacl -n -c -p`, digests, entry sets, link counts, `systemctl show`), each producer run under `check_out.py`,
     and the observable effect of each service action;
  3. classifies the whole observation against G_0, …, G_N, their partial vectors and the W_j: exactly one must equal
     it. An observation that equals none is *other* and stops S-R for an explicit operator decision; more than one
     match (possible only with co-objects) stops it as well. A partial create, install, removal or reversal is never
     *other*: each is a partial vector of its class, with its co-effects;
  4. offers the operator two actions, each needing an explicit choice, from the matched global position:
     - **resume**: from G_j^+(s), run the completing action of atom k_(j+1) for s (an intermediate without one cannot
       be resumed: reverse, or stop); from G_j^-(s), first complete the reversal of k_j for s, which gives G_(j−1);
       from W_j, first run, in global order, the forward action of every atom whose object is a co-object in its
       pre-state, which gives G_j; from G_j, run the forward action of k_(j+1); then the forward action of every later
       atom of the global sequence, in order. A check runs when resume reaches it, never one at or before the matched
       position. A service action runs when resume reaches it, and also at the start of resume when its observable
       effect differs from what G_j implies (it is idempotent). No atom at or before the matched position is run again,
       whatever the log says: a create whose object and co-effects are in their post-state is never rerun;
     - **reverse**: from G_j^+(s) or G_j^-(s), first complete the reversal of the partial atom; then run the reversing
       action of k_j, k_(j−1), …, k_1 in that order, each from its post-state to its pre-state with its co-effects,
       with the preconditions of the atom classes (for example `userdel <name>` without `-r` only for an account that
       owns no file, `rm` only for a file whose bytes equal the staged copy), followed by `systemctl daemon-reload`,
       `visudo -c` or `sshd -t` where the object belongs to those services;
  5. re-observes after each action and retains every capture; an action is complete only if the re-observation equals
     the expected global vector (G_(j+1) after a forward or completing action of k_(j+1); G_(j−1), byte for byte, after
     a reversing action of k_j);
  6. stops on any failed command or unequal re-observation and reports it for an explicit operator decision.
  S-R logs its own actions in a new log, `log/S-R<x>-<n>.log` (n the smallest unused, created with `O_EXCL`), and never
  appends to the stopped script's log, so a torn line stays the last line of the log it ends. Nothing is resumed or
  reversed without the operator's choice, and nothing is called undone without equality. S-R lies inside the existing
  reserved privileged setup and rollback authority; it adds no approval gate.
- **Rollback.** §15.1's rollback is a global sequence of its own, r_1 < … < r_M, whose vectors H_0, …, H_M start at
  the setup's G_N over the same object set O; each rollback atom is a class's reversing action run forward, with its
  co-effects, and its intermediates are the class's reversal intermediates. It runs only from a complete setup (the
  observation equals G_N); a setup that stopped part-way is undone by S-R's reverse, never by §15.1. S-R classifies,
  resumes and reverses a stopped rollback by the same rules against H_0, …, H_M and their partial vectors (§15.1's last
  paragraph). Neither a stopped setup nor a stopped rollback can leave a state that these rules do not name.

### 11.5 Setup scripts (templates; texts and digests become exact in the concrete inventory) [corrections: W1-V6-COMPOSED-STATE; v6: W1-V5-RECONCILIATION-STATES; v5: W1-SETUP-RECONCILIATION, W1-SETUP-IDENTITY, W1-CUSTODY-CLOSURE; v4: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY]

`<W>`, `<R>`, `<GATE>` are the fixed numbers. Every script begins with the same lines; only `S` and the `umask` differ
(077, except S-C, S-E and S-F, which use 022):
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
```
Every call of a helper or function is a simple command, or the whole right-hand side of an assignment, so under `-e`
its failure stops the script; §11.4 gives the status rules. `no_entry` accepts exactly the status 2 that §11.2 and
P1-P2 already expect for an absent entry, and stops on every other status.

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

**`check_out.py`** (new reviewed helper; it runs one command, given by absolute path, without a shell, and checks the
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

**S-A, accounts and groups** (atoms: three groups; then each account, which is created, locked and checked for a mail
spool, as one atom over two steps).
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
for n in wlscratch wlscratch-run wlscratch-gate; do no_entry passwd "$n"; no_entry group "$n"; done
for i in <W> <R> <GATE>; do no_entry passwd "$i"; no_entry group "$i"; done
need_absent /var/spool/mail/wlscratch /var/spool/mail/wlscratch-run
step done 0
step begin 1; /usr/bin/groupadd --system --gid <W> wlscratch; step done 1
step begin 2; /usr/bin/groupadd --system --gid <R> wlscratch-run; step done 2
step begin 3; /usr/bin/groupadd --system --gid <GATE> wlscratch-gate; step done 3
step begin 4
/usr/bin/useradd --system --uid <W> --gid <W> --no-create-home --home-dir /var/lib/wlscratch \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame writer' wlscratch
step done 4
step begin 5; lock_account wlscratch; step done 5
step begin 6
/usr/bin/useradd --system --uid <R> --gid <R> --no-create-home --home-dir /var/lib/wlscratch-run \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame target' wlscratch-run
step done 6
step begin 7; lock_account wlscratch-run; step done 7
```
The other scripts begin with the same common lines (every line through the end of `no_entry`), with their own `S`
and `umask`; below they are written `<common lines, S=…>`. A mail spool that `useradd` created despite P23 stops the
script, and S-R classifies that account as *other*. `/var/lib/wlscratch-run`, the home that `passwd` names for R, is
never created (§5.3).

**S-B, writer home, lease, run tree** (without images; with images, steps 4.1 and 4.2 (v4's step B 4) are replaced by
S-J, §14.5, and steps 5.1-5.4 (v4's step B 5) apply to the image roots).
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
entries). v6's `g:<GATE>:--x` entries are withdrawn (§6.3). `writer.lock` is one `install`; its intermediate states
are those of the file class below.

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
  /usr/bin/install -o root -g root -m 0644 "$st/frame/$m" "/opt/wlscratch/frame-v6w1/$m"
  step done "3.$i"
done < "$st/frame-members.list"
step begin 4; /usr/bin/sha256sum -c --strict "$st/frame-members.abs.sha256"; step done 4
```
The v6-W1 source is frozen with every member at 0644 and every directory at 0755, so installed modes equal frozen
modes; `frame-members.abs.sha256` names each installed member by its absolute path; the inventory records
`install_root = /opt/wlscratch/frame-v6w1` and `source_frame` (v5 checked `inventory['frame'] == FRAME`; the installed
frame checks `install_root` instead, and §4.6 binds `source_frame`).

**S-D, sudo rules** (reviewed bytes, one line each).
- `wlscratch-frame`: `sicarii ALL=(wlscratch) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py *`
- `wlscratch-run` (the RL rule; v6's Option A line is withdrawn): `wlscratch ALL=(root) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py *`
```sh
<common lines, S=D; umask 077>
step begin 0
need_absent /etc/sudoers.d/wlscratch-frame /etc/sudoers.d/wlscratch-run
/usr/bin/visudo -cf "$st/sudoers/wlscratch-frame"
/usr/bin/visudo -cf "$st/sudoers/wlscratch-run"
step done 0
step begin 1; /usr/bin/install -o root -g root -m 0440 "$st/sudoers/wlscratch-frame" /etc/sudoers.d/wlscratch-frame; step done 1
step begin 2; /usr/bin/install -o root -g root -m 0440 "$st/sudoers/wlscratch-run"   /etc/sudoers.d/wlscratch-run;   step done 2
step begin 3
if ! /usr/bin/visudo -c; then
  for f in wlscratch-frame wlscratch-run; do
    if /usr/bin/cmp -s "$st/sudoers/$f" "/etc/sudoers.d/$f"; then /usr/bin/rm -- "/etc/sudoers.d/$f"; fi
  done
  echo "S-D: visudo -c failed; staged-equal files removed; run S-R D" >&2; exit 40
fi
step done 3
```
`cmp -s` reports equal (0), different (1) or an error (2); only equality removes a file, and the script then stops in
every case, so no outcome of either condition is lost.

**S-E, sshd** (reviewed byte line `DenyUsers wlscratch wlscratch-run`).
```sh
<common lines, S=E; umask 022>
f=/etc/ssh/sshd_config.d/30-wlscratch.conf
step begin 0; need_absent "$f"; step done 0
step begin 1; /usr/bin/install -o root -g root -m 0644 "$st/30-wlscratch.conf" "$f"; step done 1
step begin 2
if ! /usr/bin/sshd -t; then
  if /usr/bin/cmp -s "$st/30-wlscratch.conf" "$f"; then /usr/bin/rm -- "$f"; fi
  echo "S-E: sshd -t failed; staged-equal drop-in removed; run S-R E" >&2; exit 50
fi
rc=0; check --line-ci "$st/sshd-denyusers.expected" -- /usr/bin/sshd -T -C user=wlscratch,host=localhost,addr=127.0.0.1 || rc=$?
case $rc in
  0) : ;;
  *) echo "S-E: DenyUsers not shown by a successful sshd -T (status $rc); run S-R E" >&2; exit 51 ;;
esac
step done 2
step begin 3; /usr/bin/systemctl reload sshd.service; step done 3
```
v4's `sshd -T … | grep -qixF …` pipeline is replaced: `check_out.py` requires `sshd -T` itself to exit 0 before it
looks for the line.

**S-F, the scope slice and the cleanup rule for target temporaries** (replaces v6's target home, masks, user-manager
drop-in and linger). Reviewed bytes of `wlscratch.slice`:
```ini
[Unit]
Description=WORLDLINE scratch frame scopes (W-1)
[Slice]
```
and of `wlscratch-tmpfiles.conf`, which repeats for every `g/tmp` the age that `/usr/lib/tmpfiles.d/tmp.conf` gives
`/tmp` on this host (`10d`, observed 2026-10-05, P26), so that target temporaries age out as they did in v5's `/tmp`:
```
e /var/lib/wlscratch/runs/*/tmp - - - 10d
```
```sh
<common lines, S=F; umask 022>
step begin 0; need_absent /etc/systemd/system/wlscratch.slice /etc/tmpfiles.d/wlscratch.conf; step done 0
step begin 1; /usr/bin/install -o root -g root -m 0644 "$st/wlscratch.slice" /etc/systemd/system/wlscratch.slice; step done 1
step begin 2; /usr/bin/install -o root -g root -m 0644 "$st/wlscratch-tmpfiles.conf" /etc/tmpfiles.d/wlscratch.conf; step done 2
step begin 3
/usr/bin/systemctl daemon-reload
check --equal "$st/slice.show.expected" -- /usr/bin/systemctl show wlscratch.slice -p LoadState -p FragmentPath -p DropInPaths -p NeedDaemonReload
step done 3
```
`slice.show.expected` (reviewed) holds `LoadState=loaded`, `FragmentPath=/etc/systemd/system/wlscratch.slice`, an
empty `DropInPaths` and `NeedDaemonReload=no`. No `g/tmpdir` rule exists, because nothing cleaned v5's `TMPDIR`. The
rule is read by the existing `systemd-tmpfiles-clean.timer`; whether its cleanup of a `g/tmp` behaves as its cleanup of
`/tmp` (age, no symlink following, no descent across mounts) is probe P-TMPAGE.

**S-G** (v6's Option A home traverse entry and S-G′) is withdrawn: the view needs no ACL on `/home/sicarii`, and
`sandbox_launch.py` is a frame member installed by S-C.

**S-H, setup identity record** [correction: W1-SETUP-IDENTITY]. A reviewed generator, run as
`$py "$st/make_setup_identities.py" /opt/wlscratch/setup-identities.json`, creates the file with `O_EXCL`, 0644,
root:root, holding: the numbers; for every setup object other than the record itself, its path, its class (§11.7), the
value of every field §11.7 pins for that class, and the names of the fields that class leaves intentionally mutable
(`mutable_fields`); the mount facts of T_root and R_root (with images: the pinned image facts, the images directory
with its exact entry set, and each image root's `lost+found`); the installed frame root identity and member digests;
the sudoers, sshd, slice and tmpfiles digests; the digests of `/etc/subuid`, `/etc/subgid` and of the new `passwd`,
`group`, `shadow` and `gshadow` lines. The record does not list itself and holds no digest, size or identity of its own
bytes; its seal is external (§11.7).

**S-I, post-setup capture** (operator, read-only, every producer under `check_out.py`): the first character only of
each new `shadow` password field; the `gshadow` lines of GATE and of both user-private groups (no members, locked);
sudoers digests and `visudo -c`; `sudo -l -U sicarii` and `sudo -l -U wlscratch`; `sshd -T -C user=wlscratch,…`;
`systemctl show wlscratch.slice` as in S-F; no process with uid W, R or gid GATE; no `user@<W>.service`,
`user@<R>.service`, `/run/user/<W>` or `/run/user/<R>`; `absent.py` on `/var/spool/mail/wlscratch`,
`/var/spool/mail/wlscratch-run` and `/var/lib/wlscratch-run`; `find / -xdev -perm /6000 -type f` and `getcap -r /usr`
compared with P17; `find / -xdev \( -uid <W> -o -gid <W> -o -uid <R> -o -gid <R> -o -gid <GATE> \)` equal to exactly
the W-owned and W-group setup objects (no file carries R or GATE); and the seal capture of `setup-identities.json`
(sha256, size, `[dev, ino]`, owner, group, mode, link count and `getfacl -n -c`; §11.7), which the installed-evidence
review records.

**S-R, reconciliation** (operator; interactive): the procedure of §11.4, with the reviewed global atom table (each
atom's global index, script and step numbers, class, effect set with co-effects, the composed pre-state and post-state
captures of every object it touches, forward and reversal intermediate states and actions, and for a service action
its observation and expected value where it has one).

**Atom classes** (the reviewed table S-R uses; the concrete inventory adds each atom's exact captures; "—" means none).
States are global (§11.4): a class's pre-state is whatever the earlier atoms of the global sequence left on the objects
it touches, and its post-state is the state right after the atom, co-effects included. "Parent +name" means the
parent directory's entry set gains the name and, for a directory, its link count gains one; "parent −name" the
reverse.

| Class | Forward action | pre(k) | Forward intermediates I(k) (completing action; reversing action) | post(k) | Reversing action from post(k) | Reversal intermediates I_rev(k) (action that completes the reversal) |
|---|---|---|---|---|---|---|
| group | `groupadd --system --gid n name` | no `group` or `gshadow` line with the name or the number | the `group` line as expected without its `gshadow` line (—; `groupdel name`) | both lines as captured | `groupdel name` (no member, owns no file) | the `gshadow` line without its `group` line (—: an explicit operator decision) |
| account (two steps) | `useradd …`, then `lock_account` | no `passwd` or `shadow` line with the name or the number | a `passwd` line without its `shadow` line (—; `userdel name`); both lines with an unlocked password field (`usermod -L name`; `userdel name`) | both lines as captured, the password field locked, no mail spool | `userdel name` without `-r` (owns no file); where `/etc/login.defs` sets `USERGROUPS_ENAB yes`, `userdel` also removes the user-private group of the same name, which the table names as the reversal's co-object (§11.4), so that the group atom's reversal is then found complete | a `shadow` line without its `passwd` line (—: an explicit operator decision) |
| directory | `install -d -o -g -m path` | `absent`; parent without the name | the entry present (parent +name) as an empty directory with root:root and the umask's mode, or with the owner set and not the mode (`chown` and `chmod` to the expected values; `rmdir -- path`, which also gives parent −name) | a directory with the expected owner, group and mode, no ACL; parent +name | `rmdir -- path` (empty) | — (one `rmdir` call; the parent's entry and link count change with it) |
| file | `install -o -g -m staged path` | `absent`; parent without the name | the entry present (parent +name) as a regular file whose bytes are a proper prefix of the staged bytes, with any owner and mode (—; `rm -- path`); the staged bytes with another owner, group or mode (`chown`, `chmod`; `rm -- path`) | a regular file, one link, the staged bytes, the expected owner, group and mode, no ACL; parent +name | `rm -- path` (bytes equal to the staged copy) | — (one `unlink` call; parent −name with it) |
| ACL of one object | `setfacl -m entries path` | the object as earlier atoms left it (the post-state of the atom that created it) | — (one `setxattr`) | pre(k) with the expected ACL text | `setfacl -b -- path`, then equality with pre(k) | — (one `setxattr`) |
| unit enablement (images) | `systemctl enable --now unit` | not enabled and not active | enabled and not active (`systemctl start unit`; `systemctl disable unit`); active and not enabled (`systemctl enable unit`; `systemctl stop unit`) | enabled and active, with §3.4's mount entry, and the enablement link present in its `.wants` directory (that directory +name) | `systemctl disable --now unit`, after §15.1 step 6's checks | not enabled and still active (`systemctl stop unit`) |
| image file and filesystem (images) | `fallocate`, `chmod 0600`, `chown root:root`, `mkfs.ext4` | `absent`; the images directory without the name | a file of the reviewed size with any owner and mode and no filesystem signature (`chmod`, `chown`, `mkfs.ext4`; `rm -- path`); a root:root 0600 file without a filesystem signature (`mkfs.ext4`; `rm -- path`) | root:root 0600, the reviewed size, ext4 with the reviewed UUID and label; the images directory +name | `rm -- path`, after it is unmounted and no loop device uses it | — (one `unlink` call) |
| check | the command | no object | — | no state | none: a check is never reversed, and runs again only when resume reaches it | — |
| service action | the command (`daemon-reload`, `systemctl reload sshd`, with the checks that follow it in the same step, such as S-F 3's) | no object | — | its observable effect where it has one (for `daemon-reload`: `NeedDaemonReload=no` and the expected `DropInPaths` and `FragmentPath` of every unit whose files the script changed, and S-F 3's checked values), otherwise no state | run again after the reversal of the objects it concerns (`daemon-reload`, `visudo -c`, `sshd -t`, `systemctl reload sshd`) | — |

v6's mask-link and linger classes are withdrawn with S-F's old content. A rollback atom (§15.1) is one of these
reversing actions run as an atom of the rollback's global sequence; its intermediates are the class's reversal
intermediates with their co-effects. Every state not given by this table and §11.4's vectors is *other*: S-R stops and
reports it for an explicit operator decision. A state that the setup, its resumption, its reversal or the rollback
reaches is never *other*.

### 11.6 Post-setup verification

- Lead (unprivileged): `getent` for the three identities; `lstat` and `getfacl -n -c` of `/var/lib/wlscratch`,
  `runs/` and `runs/records` compared with the pinned fields of `setup-identities.json` (§11.7) and §6.3; the installed
  frame listed and hashed member by member against the frozen inventory, with §11.1's regular-file and directory
  rules, no extra entry and no ACL; the slice and tmpfiles files by digest, and `systemctl show wlscratch.slice` as in
  S-F; `/var/lib/systemd/linger` equal to P15; no process with uid W, R or gid GATE; `/etc/subuid` and `/etc/subgid`
  unchanged.
- Through the selftest verbs (W, and RL with L, C and O): `lease/` and `writer.lock` identities, role identities and
  readbacks; one view of each kind built on the sacrificial selftest generation and recorded (its mountinfo, maps,
  Landlock ruleset, credentials and the original observations of §8.4 taken inside it) as the candidate view baseline,
  which is reviewed with the installed evidence before adoption (§16); and the probes of §13.
- Operator: S-I.

### 11.7 Setup identities: pinned and intentionally mutable fields [corrections: W1-V6-IMAGE-PIN, W1-V6-INVARIANTS; v6: W1-V5-IMAGE-PINS; v4: W1-SETUP-PROBES-ROLLBACK]

Every later invocation, and every invocation after a reboot, compares only the pinned fields; it observes and records
the mutable ones in its role or stage identity and never compares them with setup-time values. A change of a pinned
field refuses before any mutation, except in `adopt`, whose one exception is stated exactly below.

| Object class | Pinned (compared at every use) | Intentionally mutable (recorded, never compared with setup values) | Constraint on the mutable part |
|---|---|---|---|
| Regular setup files: `writer.lock`, the sudoers files, the sshd drop-in, `wlscratch.slice`, `wlscratch.conf` (tmpfiles), every installed frame member | type, `dev`, `ino`, uid, gid, mode, `nlink` 1, size, sha256 (`writer.lock`: size 0), no ACL | atime, mtime, ctime | none |
| `setup-identities.json` (never listed in itself; sealed from outside, below) | fixed values checked at every use: type regular, uid 0, gid 0, mode 0644, `nlink` 1, no ACL; sha256, size, `dev` and `ino` compared with the seal below, never with the record's own content | atime, mtime, ctime | none |
| Static setup directories: `/var/lib/wlscratch`, `lease/`, `/opt/wlscratch`, the installed frame directories | type, `dev`, `ino`, uid, gid, mode, exact ACL text, exact entry set, `nlink` | atime, mtime, ctime (they move only with the entry set, which is pinned) | none |
| Growing tree directories: `runs/` (T_root) and `runs/records` (R_root) | type, uid, gid, mode, exact ACL text; without images also `dev` and `ino`; with images the mount identity of the next row instead | `nlink`, size, atime, mtime, ctime, the entry set | every entry obeys §3.4's name grammar and is a W-owned directory, except, with images, the pinned `lost+found` special entry of §3.4; W checks it at every invocation |
| Image mounts (images only, §14.5) | filesystem UUID and label; the backing image file's `dev`, `ino`, size, mode 0600, uid 0, gid 0 and `nlink` 1 on the root filesystem, read by W and W2 through the images directory (§3.4, §14.5 J1); the mount point path; mount options `nosuid,nodev,noexec`; the nesting (records inside work); the image root's uid, gid, mode, ACL and `ino` | the mounted filesystem's `st_dev` (the loop device number), the loop device name, the mount ID | `st_dev` differs from the parent's and equals the device of the mountinfo entry whose loop device's backing file is the pinned image file |
| Images directory `/var/lib/wlscratch-images` (images only) | type, `dev`, `ino`, uid 0, gid W, mode 0750, no ACL, and the exact entry set (the two pinned image file names), which W and W2 compare at every use by listing the directory through their anchored descriptor (§3.4) | atime, mtime, ctime | W and W2 can list and search it but not write it; the image files stay root:root 0600 |
| `lost+found` of each image root (images only) | name, type directory, `ino`, uid 0, gid 0, mode 0700, no ACL | `nlink`, size, times, contents (root's; `e2fsck` may add entries; W cannot read them) | never used, opened or walked by the frame |
| Bare mount points (images only; observed at setup and rollback while unmounted) | type, `dev`, `ino`, uid 0, gid 0, mode 0700, empty, no ACL | times | must be empty |

The setup identity record stores, for every object other than itself, the class and the pinned values. Every field
pinned "at every use" is one that the comparing role can read with its own credentials. The images directory is now
root:W 0750, so W and W2 list it and compare its exact entry set at every use, as the sealed W1-V5-IMAGE-PINS
correction requires (correction W1-V6-IMAGE-PIN); v6's search-only 0710 directory, its known-name lookup and its
operator-only captures of the entry set are withdrawn, and no operator gate is added. The listing exposes the two file
names, which `setup-identities.json` already states; W gains no write access and no access to the image files' bytes.
RL, which runs as root, repeats the same comparison before it builds a view (§3.4).

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

## 12. The target view [corrections: W1-V6-PRESERVE, W1-V6-READ-MUTATION; gap: exposure-options]

### 12.1 The design adopted

v6 offered two exposure options and selected none. v7 adopts one design, the target view, because §22 finds it the
only candidate evaluated that removes the copy route, the user manager and the release expansion while keeping the
original environment, paths and file authority. v6's Option A (a traverse ACL on `/home/sicarii`) is withdrawn. v6's
Option B (a root launcher with a private mount namespace that showed only the toolchain) is extended into the view,
which shows what `sicarii` can reach, as the original target saw it. The view is privileged code, installed only by
the operator inside the existing reserved setup (§11.5 S-C, S-D, S-F) and removed by its rollback (§15.1); no approval
gate is added.

### 12.2 RL and the view, exactly

**Stage 1** (`sandbox_launch.py launch …` or `observe …`, root, started by S2 or S_O):
1. First act (§7.7); role identity; argv grammar: verb `launch`, `observe` or `selftest`, g, A, the helper nonce
   (`n_wl` or `n_o`), the observer index for `observe`, and the seals (`launch.json` and `admission.json` sha256 for
   `launch`, `observer-intent-<n>.json` sha256 for `observe`).
2. Invoker: `SUDO_UID` is W, and its nearest ancestor that is not a `sudo` process has uid W. RL trusts nothing else
   from W: every input it uses it reads itself from T and checks against its argv's seals.
3. Descriptors: exactly 0-2 (fd 0 a socket, fds 1-2 regular files owned by W in P_att or in `w2-<k>/`), verified in
   `/proc/self/fd`.
4. Anchors (§3.4): A_T and g by anchored chains, compared with `setup-identities.json` and, with images, the
   missing-mount checks and the images directory's exact entry set; g's committed `materialization.json` (label, run
   path, the identities of `source/`, `tmp/` and `tmpdir/`); for `launch`, `launch.json` and `admission.json` read from
   P_att with sha256 equal to the seals, which give the view specification (the lead's supplementary groups G_V, the
   environment, the mount table below) and U; for `observe`, `observer-intent-<n>.json`, which gives its stage and its
   copy of the view specification. RL opens every record with `O_NOATIME`.
5. Census (§9.4): U absent (for `launch`) or the observer scope name unused; every child of `wlscratch.slice`
   `populated 0`.
6. `RLIMIT_CORE` (0, 0); then `exec` of `/usr/bin/systemd-run --scope --quiet --slice=wlscratch.slice --unit=<U> -p
   MemoryMax=8G -p MemorySwapMax=0 -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py <verb>-scoped
   <the same arguments>` (an observer scope `wlscratch-o-<g12>-<A>-<n>.scope` carries no memory properties, because
   v5 took its observations in the unscoped frame process).

**Stage 2** (the same pid, now in the scope, root):
7. First act, identity, argv, and the reads of step 4 again (a new process image trusts no earlier one); its cgroup is
   `/wlscratch.slice/<U>` and U holds exactly this pid.
8. Mount namespace: `unshare(CLONE_NEWNS)`, then every mount made private recursively before any other change (no
   propagation in either direction, P-PROP). The new namespace is owned by the initial user namespace, so no process
   that later enters the view's user namespace can change it.
9. Network namespace: `unshare(CLONE_NEWNET)`; the loopback interface brought up; nothing else.
10. User namespaces, each created by a short-lived helper child that calls `unshare(CLONE_NEWUSER)`, whose maps RL
    writes as root and whose `/proc/<pid>/ns/user` RL opens before the helper exits (each is owned by root):
    - U_v, the view's own: uid map 0-949 → itself, 953-999 → itself, 1000 → R, 1001 and above → itself (the bounds
      JACKAL exact, Appendix G); gid map the same with 1000 → GATE; 950, 951 and 952 unmapped; `setgroups` allowed;
    - U_run, the idmap of the run-path and `TMPDIR` binds: uid W → R, gid W → GATE, nothing else mapped;
    - U_tmp, the idmap of the `/tmp` bind: uid W → 0 and 1000 → R; gid W → 0 and 1000 → GATE; nothing else mapped.
    The concrete inventory states the maps' numeric lines, with their counts computed by JACKAL.
11. Mounts (each a non-recursive `open_tree(OPEN_TREE_CLONE)` of a host mount or of a held directory, given its
    attributes with `mount_setattr`, `MOUNT_ATTR_NOSUID` on every one, and attached with `move_mount`):

| Path in the view | Source | Idmap | Purpose |
|---|---|---|---|
| `/` | the host's root mount (ID 32, ext4 on `/dev/vda`) | U_v | the original filesystem with `sicarii`'s on-disk authority |
| `/proc`, `/sys` and the `/sys` submounts (`kernel/security`, `fs/cgroup`, `fs/pstore`, `fs/bpf`, `kernel/tracing`, `kernel/debug`, `kernel/config`, `fs/fuse/connections`) | the host mounts | none | as on the host |
| `/dev`, `/dev/pts`, `/dev/mqueue`, `/dev/hugepages` | the host mounts | none | as on the host |
| `/dev/shm` | the host mount | U_v | shared memory files with `sicarii`'s authority, as in v5 |
| `/run` | the host mount (ID 30) | none | as on the host |
| `/run/user/1000` | the host mount, without its FUSE submounts | U_v | `XDG_RUNTIME_DIR` with `sicarii`'s authority |
| `/srv/worldline` | the host mount (ID 55) | U_v | as on the host |
| `<RUNS>/<label>/source` | g/source, held since step 4 | U_run | the run's source, owned by the target (§8.4) |
| `/tmp` | g/tmp | U_tmp | the private `/tmp`, seen as root:root 01777 |
| `/home/sicarii/.cache/workflow-tmp` | g/tmpdir | U_run | the private `TMPDIR`, seen as 1000:1000 |
| `/var/lib/wlscratch`, and with images `/var/lib/wlscratch-images` | a fresh empty `tmpfs`, read-only | none | masks |

Not reproduced, and never opened, statted or traversed by RL: the FUSE and network mounts (`/home/sicarii/iPad`,
`/home/sicarii/iPadBackup`, `/run/user/1000/doc`, `/run/user/1000/gvfs`, `/mnt/mac`), `/proc/sys/fs/binfmt_misc`,
`/run/credentials/*` and other users' `/run/user/<uid>`; their mount points show the directories beneath them. A live
host mount that the table does not name (P9 captures the list at setup) is likewise not reproduced and is recorded in
`RL_IDENTITY` from `/proc/self/mountinfo`, which RL reads without touching the mount; RL never refuses because of one.
Every mount point exists beforehand; RL creates no file or directory on any host filesystem (§9.8 N5).

12. Verification: the new namespace's `/proc/self/mountinfo` equals the planned table (mount points, root
    `[dev, ino]`, options with `nosuid` and the idmaps, private propagation), the three binds' roots have the
    identities of step 4, and no mount lies at or below the run path other than its bind.
13. Landlock: a ruleset that handles `LANDLOCK_ACCESS_FS_MAKE_SOCK`, `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` and
    `LANDLOCK_ACCESS_FS_REFER`, with a path-beneath rule granting `REFER` on the view's `/` and rules granting
    `MAKE_SOCK` and `REFER` on the three binds; no rule grants `RESOLVE_UNIX`; no scope flag and no network rule. RL
    applies it with `landlock_restrict_self` while it still holds `CAP_SYS_ADMIN` (no `no_new_privs`); the domain
    covers this pid and everything it later `exec`s and forks. Each RL invocation creates a new domain, so a target and
    an observer never share one.
14. Credentials: `setns` into U_v; drop the bounding set; `setgroups` to G_V's ids as U_v shows them (the lead's
    groups, 1000 for GATE); `setresgid(1000, 1000, 1000)`; `setresuid(1000, 1000, 1000)`, which clears every
    capability set; verify `/proc/self/status` (uids and gids 1000, the groups, every capability set zero, `NoNewPrivs:
    0`) and the maps. From the initial user namespace the pid now has uid R, gid GATE and groups G_V in all positions.
15. Environment: exactly `launch.json`'s (§8.4) for L, the same target environment for O.
16. `RL_IDENTITY` on fd 0 (§7.3): its role identity taken at this moment, the view specification's sha256, the
    mountinfo of step 12, the maps, the Landlock ruleset, the scope and the census of step 5; then `execve` of L
    (`launch_target.py launch …`) or O (`launch_target.py observe …`).

**Failures.** Any failed step writes the step and errno to RL's stderr (fd 2, a W-created stream file) and exits
non-zero before `RL_IDENTITY`; nothing else is sent, and no L or O exists (§9.5).

**New trust.** RL is privileged code behind a passwordless rule that any writer instance can call with any
arguments, so it must be robust to arbitrary input; it reads its inputs only from T and checks them against its argv's
seals. Its code, rule, probes (§13) and residuals are reviewed in the concrete setup package before any approval.
No implementation or sufficiency evidence exists.

### 12.3 What the view changes for the target (the complete inventory known to the author)

Each item is a change of the original success domain unless premise TOOL-CLOSURE (§22) shows that no allowlisted
action observes it. None is presented as preserving; none narrows an accepted case by rule, and none is used to close
a blocker.

| Id | Change against v5 | Mechanism |
|---|---|---|
| V1 | No host network: a private network namespace with only loopback; no external connectivity, no host loopback service, abstract UNIX sockets only among the view's processes | N1 (abstract sockets) |
| V2 | No connection, and no `sendmsg` with an address, to any pathname UNIX server created outside the target's Landlock domain (`sicarii`'s session bus and user manager, agents, display and audio servers, the system bus, WORLDLINE daemons): `EACCES`; no socket file outside the run path, `/tmp` and `TMPDIR`: `EACCES` | N1 (pathname sockets) |
| V3 | No mount, unmount, bind or `pivot_root`, also inside user namespaces the target creates | Landlock (P-LL) |
| V4 | Set-ID programs and file capabilities confer nothing (`sudo`, `su`, `newuidmap`, `newgidmap`, `fusermount3`, `mount`, `ping`, …); unprivileged `unshare -U` with a single mapping still works | `nosuid` (P-NOSUID) |
| V5 | Host identity R and GATE: on the non-idmapped mounts (`/proc`, `/sys`, `/dev`, `/run` apart from `/run/user/1000`) and for IPC objects, `sicarii`'s objects are foreign (for example `sicarii`'s terminals in `/dev/pts`, `sicarii`'s SysV and POSIX IPC objects); `sicarii`'s processes appear with an unmapped uid, and neither side can signal, trace or read the other's `/proc` details; per-user kernel accounting (`RLIMIT_NPROC`, inotify, user namespaces, keyrings, message queues, epoll watches) counts against R; the target's user keyring is R's | U_v, credentials |
| V6 | Mounts not reproduced (FUSE and network mounts, `binfmt_misc`, `/run/credentials`, other users' runtime directories), and host mounts made after the view's creation do not appear in it | §12.2 step 11, private propagation |
| V7 | `/tmp` and `TMPDIR` are private to the generation (§4.1): files of other processes there are invisible, and the target's are invisible to them; `/var/tmp`, `/dev/shm` and `/run/user/1000` stay shared; with images (§14.5) the run path, `/tmp` and `TMPDIR` inherit the work image's `noexec` | binds |
| V8 | The run directory `<RUNS>/<label>` no longer holds v5's frame records and snapshot (they are in T); `source/` is a mount root, so the target cannot rename or remove it; the target's writes elsewhere in `<RUNS>` land in the lead's directories, as in v5 | binds |
| V9 | `/var/lib/wlscratch` and `/var/lib/wlscratch-images` appear as empty read-only directories (they did not exist in v5) | masks |
| V10 | U is a scope of the system manager under `wlscratch.slice`, not of `sicarii`'s manager: the system manager's defaults for scopes (OOM policy, managed-OOM settings, CPU and IO weights) replace the user manager's; MemoryMax and MemorySwapMax are v5's | §8.3 |
| V11 | The lead creates `<RUNS>/<label>/source` before the generation's first dispatch (v5's `materialize` created the run directory); a missing mount point refuses at RL | §3.3 |
| V12 | The target runs inside a Landlock domain: it can stack its own, and its ptrace reaches only its own domain | Landlock |

Frame-side changes that a lead or an accepted case can observe (the census and the other refusals of §21, the read
routes of §9.8 N6) are listed in §21, not here.

## 13. Probe specification (future; nothing here has been executed) [corrections: W1-V6-COPY-PROBES, W1-V6-COMMIT-AMBIGUITY; v6: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY, W1-COMMIT-JOURNAL-EXPORT; gap: denial-probes]

**What a probe can do.** A probe can refute a premise of §9.8 N7; it never establishes one. A premise stays
NAMED_UNESTABLISHED until its probe passes and, where §9.8 N7 says so, a source-level reading for the installed kernel
or systemd version is reviewed with the installed evidence (§16). No finite probe and no first engineering run is
promoted into a universal premise, and no probe result is turned into an exception: a failed premise means that W-1
must be redesigned (correction W1-V6-COPY-PROBES).

**Fixtures.** The writer selftest creates a sacrificial pair, `runs/selftest-<h>` (written `sg` below) and
`runs/records/selftest-<h>` (written `sg_rec`), with §3.3's layout and §6.3's modes and ACLs, reduced to: a recipe
directory `sg/source/src/` (0755) holding `src/a.adb` (0644); a P_adm record `sg/rec.json` (0600); `sg/inputs/` (0700)
holding `in.bin` (0600); `sg/tmp/` (01777) and `sg/tmpdir/` (0700); `sg_rec/attempts/<A>/` (0700) holding `att.json`
(0600); `sg_rec/export/` (0750 by ACL) holding `exp.json` (0640 by ACL). The selftest view (§12.2 on `sg`, with a
sacrificial label and run path that the lead creates) creates, as T would, `src/obj/` (0700) with `t.o` (0600) and
`d/` (0700). Each actor has its own directory for rename and link targets: `/tmp/wl-probe-a1-<h>/` (A1, 0700, on the
host) and, inside the view, `/tmp/wl-probe-a2-<h>/` (A2, in the private `/tmp`). Probes never touch a real
generation, the real window file or anything below `/home/sicarii` other than the lead's own records, the sacrificial
run path and a sacrificial probe directory `/home/sicarii/wl-probe-<h>/` that the lead creates. The tables write
paths relative to `/var/lib/wlscratch/runs/`; each probe uses the absolute path. The selftest verbs use §7's framing
with their own test-only state machines, which are part of the code review (§16, step 2); they never run in a real
generation.

**Actors.** A1: the lead, uid 1000, outside, in the initial user namespace. A1u: an A1 process inside a user and mount
namespace it creates itself (mapping 1000 and `sicarii`'s subordinate range). A2: a process of the selftest view with
T's credentials and domain. A3: a process of a second, concurrent selftest view of the same generation (another
Landlock domain and network namespace, the same credentials). A4: a second writer selftest instance while the first
holds the lease. A5: W itself (positive controls). A6: root, through the operator's sacrificial probe harness
(positive controls only).

**Each probe row records:** the actor's full credentials and namespaces; the exact syscall and its absolute operands;
the preconditions observed immediately before (below); the raw errno number and name, or success; and, on unexpected
success, the whole resulting state, retained and never cleaned. An unexpected success is a setup failure. An unexpected
errno fails the row as well, because it may show a wrong operand rather than the intended denial.

**Preconditions, checked immediately before each row.** (1) By W, the fixture's owner: each source operand exists with
the expected type (`lstat`), and each destination name is `absent` (§11.1). (2) By the actor: `faccessat(…, X_OK,
AT_EACCESS)` on every ancestor of each operand equals the search permission §6.3 implies for that actor; a difference
fails the row as a fixture error. (3) For a `rename` or `link` meant to test permission: both operands on the same mount
(equal mount IDs), so that `EXDEV`, which the kernel reports before any permission check, cannot mask the result;
rows meant to test `EXDEV` (P-XDEV) state their two mounts.

**Expected errnos** follow §6.5's rule (the first failing check). "ok" marks a positive control.

A1 (`sicarii`), without images:

| Operand(s) | Operation | Expected | Reason |
|---|---|---|---|
| `sg/source/src/a.adb`; `sg/rec.json`; `sg/inputs/in.bin`; `sg/tmp/x`; `sg/tmpdir/x` | `open(O_RDONLY)`; `open(O_WRONLY)`; `open(O_CREAT)`; `stat` | `EACCES` each | no search permission on `sg` (no ACL, §6.3) |
| `sg` | `rename` to a new name in `runs/`; `rmdir`; `chmod`; `setxattr(system.posix_acl_access)` | `EACCES`, `EACCES`, `EPERM`, `EPERM` | search-only `runs/`; not the owner |
| `/tmp/wl-probe-a1-<h>/y` (A1's own file) → `sg/y` | `rename` in; `link` in | `EACCES` each | no search permission on `sg` |
| `records/selftest-<h>/attempts/<A>/att.json` | `open(O_RDONLY)` | `EACCES` | no search permission on `attempts/` |
| `records/selftest-<h>/export/exp.json` | `open(O_RDONLY)` | ok | export ACL |
| `records/selftest-<h>/export/exp.json` | `open(O_WRONLY)` | `EACCES` | export file `r--` for 1000 |
| `records/selftest-<h>/export/n` | `open(O_CREAT)` | `EACCES` | export directory `r-x` for 1000 |
| `/var/lib/wlscratch/lease/writer.lock` | `open(O_RDONLY)` | `EACCES` | no search permission on `lease/` |
| a new name in `runs/`; a new name in `records/` | `mkdir` | `EACCES` each | search-only entries |
| the host path of the sacrificial run path | `stat`, `readdir` | ok: the lead's own empty directory, never the bind | the bind exists only in the view (P-PROP) |

A1u repeats every A1 row from inside its own namespaces (its mount namespace is a copy of the host's, owned by its
user namespace) with the same expected results, and additionally: a bind mount of any ancestor of `sg` inside its
namespace shows the same denials; `open_by_handle_at` with handles of `sg`, `sg/source`, `src/` and `src/obj/`
obtained by A6 fails (P-FH).

A2 (inside the selftest view):

| Operand(s) | Operation | Expected | Reason |
|---|---|---|---|
| `<run>/source/src/a.adb` | `open(O_RDWR)`; `chmod 0600`; `unlink` and re-create | ok each | the target owns `source/` through U_run |
| `<run>/source/src/obj/n` | `open(O_CREAT\|O_EXCL)`, `fstat` | ok; uid and gid 1000 in the view; W and W on disk (A6 checks) | U_run, U_v |
| `<run>/source/src/a.adb` → `/tmp/wl-probe-a2-<h>/l`; → `/home/sicarii/.cache/workflow-tmp/l`; → `<RUNS>/<label>/l` | `link`; `rename` | `EXDEV` each | different mounts (P-XDEV) |
| `<run>/source` | `rename`; `rmdir` | `EBUSY` each | a mount root in the view |
| `/var/lib/wlscratch/lease`; `/var/lib/wlscratch/runs` | `stat` | `ENOENT` each | the mask (an empty read-only tmpfs) |
| `/var/lib/wlscratch/x` | `open(O_CREAT)` | `EROFS` | the mask is read-only |
| `/run/user/1000/bus`; `/run/dbus/system_bus_socket` | `connect` | `EACCES` each | `RESOLVE_UNIX` (P-LL) |
| a server that A2 binds in `/tmp/wl-probe-a2-<h>/` | `connect` from A2 | ok | own domain |
| the same server | `connect` from A3 | `EACCES` | another domain |
| `/home/sicarii/wl-probe-<h>/sock`; `/var/tmp/wl-probe-sock-<h>` | `bind` of a pathname socket | `EACCES` each | `MAKE_SOCK` only in the binds |
| an abstract name bound by an A1 process | `connect` from A2 | `ECONNREFUSED` | private network namespace (P-NS) |
| an abstract name bound by A2 | `connect` from A1 | `ECONNREFUSED` | the same |
| a `tmpfs`; a bind of `<run>/source` at `/home/sicarii/x`; `pivot_root` | `mount`, `mount --bind`, `pivot_root`, also after `unshare -Urm` | `EPERM` each | Landlock (P-LL) |
| `/usr/bin/sudo -n true`; a set-user-ID copy that A2 makes of `/usr/bin/id` in `<run>/source/` | `execve` | sudo refuses (its effective uid is not 0); the copy runs with A2's ids | `nosuid` (P-NOSUID) |
| `/proc/self/mountinfo` | read | §12.2 step 12's table, private propagation | P-NS |
| a file A2 creates under `<run>/source/` | its on-disk owner and group (A6) | W and W | U_run (P-IDMAP) |
| a file A2 creates in `/tmp`; in `/home/sicarii/wl-probe-<h>/` | on-disk owner (A6) | 1000 each | U_tmp; U_v |
| on-disk 950, 951 and 952 objects that A6 prepares in `/home/sicarii/wl-probe-<h>/` | `stat`; `open(O_RDWR)` | owner shown as the overflow id; `EOVERFLOW` or `EACCES`, recorded | unmapped ids (P-IDMAP) |

A3: the A2 rows that concern its own view hold for it as well; the cross-domain rows are above.

A4: `LeaseHeld` before any mutation and before starting any helper; the listings of `runs/` and `runs/records` are
identical before and after.

A5 (W): `open(writer.lock, O_WRONLY)` → `EACCES` (0440, group `r--`); `chmod` of `writer.lock` → `EPERM` (owned by
root); `rename` or `unlink` in `lease/` → `EACCES` (root-owned 0750); a record committed with the generic primitive
(ok, 0600, linked only after its validation, §10.1) and an export copy made with the export primitive, whose unnamed
inode shows 0640 and the export ACL before its link (ok, §15.3).

With images the tables are the same, with `runs/` and `records/` on the image mounts and the cross-directory A1 rows
`not-applicable: different mount`.

| Family | Operations and expected outcome |
|---|---|
| P-MUT, P-ALIAS, P-READ | the tables above |
| P-LEASE | A4 and A5 above |
| P-DRIFT | between the O parent-stage walk and C's final pass of a sacrificial attempt, a test-only switch of the selftest machine lets A6 change an excluded partition leaf (content, mode, mtime, a second hard link inside the partition, replacement): C refuses with the recorded reason. A control without change is accepted |
| P-LAUNCH | A1 runs `sudo -n -u wlscratch-run …` and `sudo -n … sandbox_launch.py …` (refused; exact status and message); a writer selftest starts RL and L and closes SP_L before `GO` (L exits 125, nothing started); RL with a wrong seal, an unknown verb, an extra descriptor or an invoker that is not W refuses before any namespace; C started outside its scope or with a wrong seal refuses; C without `SPAWN_OK` refuses; L or C given a stream descriptor whose `[dev, ino]` differs from `launcher-intent.json` refuses; the credential sets in which sudo's monitoring processes appear in `/proc` are recorded |
| P-NS | every namespace RL creates has the stated owner (`ioctl(NS_GET_OWNER_UID)` and `NS_GET_USERNS` read by A6); `lo` is the only interface; no `user@W`, `user@R`, `/run/user/W` or `/run/user/R` exists during or after a selftest |
| P-IDMAP | the A2 ownership rows; `O_NOATIME` opens by A2 and by O of entries below `<run>/source` and of `sicarii`'s files through the root view succeed |
| P-LL | `landlock_create_ruleset` with `LANDLOCK_CREATE_RULESET_VERSION` reports ABI 9 or higher; the A2 socket and mount rows; every same-mount `rename` and `link` that DAC permits succeeds in the view as outside it (a sample of directory pairs inside `<run>/source`, inside `/tmp`, inside `/home/sicarii/wl-probe-<h>`), and a socket file cannot be renamed out of a private bind (`EXDEV`) |
| P-XDEV | the A2 `EXDEV` rows, and the same with `renameat2(RENAME_EXCHANGE)` and `RENAME_NOREPLACE` |
| P-PROP | a mount that A6 makes in the host namespace during a selftest view does not appear in the view, and the view's binds never appear in the host's `/proc/self/mountinfo` |
| P-PTRACE | while L, C, O and a sacrificial target (uid R) run, A1, A1u and A3 each: `open` of `/proc/<pid>/fd/<n>` for reading and for writing, `readlink` of it, `open` of `/proc/<pid>/{cwd,root,exe,environ,mem}` (`mem` for reading and for writing), `readdir` of `/proc/<pid>/map_files`, `pidfd_open` with `pidfd_getfd`, `ptrace(PTRACE_ATTACH)` and `ptrace(PTRACE_SEIZE)`, `process_vm_readv`, `process_vm_writev`, `kcmp`, and a fanotify group (without `FAN_REPORT_FID`: refused; with it: a mark on an entry of the generation fails, because no path reaches it): every one refused (`EACCES` or `EPERM`, recorded), in each role's pre-first-call window as well as after it; for A3, which has uid R, the refusals come from Landlock's ptrace scoping between domains, and the row records that; the sacrificial target does the same to L, C and O (refused: they are non-dumpable). Positive controls: A6 succeeds on each operation, and a child of the sacrificial target that the target itself traces succeeds where Yama permits a descendant, which shows that each refusal comes from the stated rule and not from a broken operand (correction W1-V6-COPY-PROBES) |
| P-FH | the A1u row; and A1 in the initial namespace: `open_by_handle_at` → `EPERM` |
| P-CG | a sacrificial target forks, exits and leaves children: the scope stays `populated 1` until the last one ends, then `populated 0`; writes to `cgroup.procs` of any cgroup below `wlscratch.slice` by the target and by A1 fail; `clone3(CLONE_INTO_CGROUP)` into another cgroup fails; an `io_uring` worker of the target is listed in the scope's `cgroup.threads` |
| P-NOR | after every selftest, CRED passes and no process with uid R or gid GATE exists |
| P-IOEXIT | a sacrificial target submits long `io_uring` writes and AIO writes to a sacrificial partition file and exits; after the scope reads `populated 0` the file's `stat_key` and bytes stay unchanged for a recorded period (refutation only) |
| P-NOATIME | the access times of the files and directories read in routes R-a, R-b, R-c and R-e (§9.8 N6) are unchanged by those reads (A6 reads them with `statx`) |
| P-NOSUID | the A2 `execve` rows; `MOUNT_ATTR_NOSUID` cannot be cleared from inside the view or a namespace it creates |
| P-LOCK | after `unshare -Urm` inside the view (allowed), an attempt to unmount a mask or bind, or to bind an ancestor of a mask non-recursively, fails, and nothing beneath a mask becomes visible |
| P-CENSUS | for each scope a selftest leaves: `systemctl show <U> -p ActiveState` and `cgroup.events populated` agree at every sampled moment, including a scope whose last process is exiting (refutation only) |
| P-TMPAGE | `systemd-tmpfiles --clean` run by the operator on the sacrificial `sg/tmp` with back-dated files removes exactly what the `/tmp` rule would remove, follows no symlink and does not descend into a mount |
| P-STREAM | a sacrificial target leaves a child that holds `child.stdout` open: W's stream finality reports the stream not final until the scope reads `populated 0`; a control is final |
| P-RUNTIME | role identities, module closures and the original observations of §8.4 taken inside a selftest view against their baselines; this is evidence for that run only, and every attempt re-checks (P-VIEW) |
| P-SIG, P-RELAY | A1 sends `SIGTERM` to S1 during a writer selftest wait: W's interrupt record, whether `sudo` relayed it, and that W made no mutation outside its sacrificial tree; the status `sudo` reports for a selftest C that exits with a code and one killed by a signal |
| P-TERM | terminal-failure controls through test-only switches of the selftest verbs (never of `dispatch`): W death after the launch intent and after `PROCEED_LAUNCH` (recovery by W2 with complete rounds, §9.7); death of the RL/L pid after `GO` and before `LAUNCHER_START`; C refusal; C killed after its spawn call and before `CHILD_START` (`target_started: unknown`, classification by §9.4); target non-zero exit (`/usr/bin/false` as the selftest target); F death after a reservation of a sacrificial copy of the window protocol on a sacrificial path. Expected behaviour as §9.5 and §9.7 |
| P-COMMIT | failures injected into the commit primitive at each step of §10.1: the write, `fsync`, validation and link of the record and of each marker (not committed for any consumer; retry, then fallback), the directory `fsync` and post-link join after the close marker's link (committed, `synced: false`, success withheld, no retry), an error from `linkat` after which the name exists (treated as linked); fallback (a VALID slot); a short slot write followed by an error (a TORN slot, never reused); fallback exhausted (UNKNOWN); the export primitive (final mode 0640 and ACL before the link); increments and cuts (each record exported exactly once; the final freeze marker reported); a release whose `release-intent.json` cannot be committed still releases when known-terminal ownership holds (durability-UNKNOWN, success withheld) |
| P-ENOSPC | required before any record is described as durable under allocation failure: on an operator-provided sacrificial small filesystem, fill it; fallback slot writes must then succeed. Until it passes no such claim is made (§10.4) |
| P-SETUP | `absent.py` on an absent path (`absent`), an existing file (`present`), a dangling symlink (`present`), a path below an unreadable directory (`undetermined`, `EACCES`), a path whose parent is a regular file (`undetermined`, `ENOTDIR`) and a path with a missing parent (`undetermined`); S-R's classification logic run against recorded synthetic logs and observations (no account is created by a probe) |
| P-MOUNT | images only: with the records image unmounted (its bare mount point visible), and then with both images unmounted, every writer verb and RL refuse before any mutation or view; the bare mount points are unchanged afterwards; a remount at a different loop device number is accepted, because the loop device number is a mutable field (§11.7) |
| V-VAULT | as `sicarii`: `project-vault pin`, `status` and the project-vault recovery comparison on `runs/records/selftest-<h>/export`, and an offline verification of the restored export that recomputes every chain head and payload digest from the restored tree alone (§8.5) |

### 13.1 v5, v6 and v7 probe additions (future; nothing here has been executed) [corrections: W1-V6-COMMIT-AMBIGUITY, W1-V6-COMPOSED-STATE, W1-V6-IMAGE-PIN; v6: the six of gpt61-v5; v5: all six of gpt61-v4]

The fixtures, actors, record rules and preconditions of §13 apply. Parent-stage and child-stage steps run on a
sacrificial attempt of the sacrificial generation, never on a real generation or the real window file. v6's P-ROUTE,
P-COPY, P-SETID, P-MGR and P-QUIESCE rows are withdrawn with the mechanisms they tested; P-PTRACE is replaced by §13's
complete row.

| Family | Operations and expected outcome |
|---|---|
| P-CHAIN | on sacrificial journals, every consumer (W's join, W2, the conclusion, an export, an offline reader of the export, and a reader after a simulated reboot that drops unsynced directory entries) computes the same chain, head and committed set for: a torn record-bearing marker followed by its continuation; a record-bearing marker whose close marker's write, `fsync` or validation failed, so that the close marker never received a name, followed by the writer's continuation, which links to the record-free marker before the record-bearing one and lists both seqs (not committed for any consumer; the record's bytes and the marker are RAW and listed once by the exports; the retry carries the record with its failure and its downgrade); the same with the continuation absent because the writer was killed (the head is the unconfirmed record-bearing marker; not committed for any consumer; the next writer's continuation skips it); a close marker linked, then its directory `fsync` failed (committed, `synced: false`, for the writer and every live reader; after the simulated reboot either committed or, if the entry was dropped, uncommitted, which the writer had reported as possible); a close marker linked, then its post-link join failed (committed, an error of the attempt); a `linkat` that reported an error although the name appeared (committed for everyone, because the writer re-observed the name); a continuation whose `prev_commit` names a record-bearing marker (nobody's candidate: RAW); a marker and its continuation both failing (the writer stops, and the record is not committed for any consumer); a torn genesis followed by a genesis continuation; a create or link that left no name (a gap listed with an empty `files` list); two markers of one seq (branched; no writer appends); a W2 opening a journal whose head is an unconfirmed record-bearing marker (its first marker is a continuation that skips it); and export cuts and `raw_files` that list every raw file exactly once (correction W1-V6-COMMIT-AMBIGUITY) |
| P-PROTO | the selftest machines drive each transition of Appendix B.4.4: `EARLY_REFUSAL` from every pre-hello check of each verb; `REFUSAL` after `HELLO_ACK`, in place of `PHASE_DONE`, and on a `STOP` in every row whose STOP column says so (adopt `INPUTS` and `COMMIT`, materialize `MATERIALIZE`, dispatch `ADOPTION` among them); a `STOP` recorded without a refusal in materialize `VAULT` and in every W2 state (seal `FRONT_TERMINAL` among them); `L_REFUSAL` as L's first message after RL's frame and a failing G4 check; `L_REFUSAL` (stage `exec`) after `LAUNCHER_START` when the `exec` fails; `CHILD_REFUSAL` as C's first message after a failing C1 check (C1 checking only compiled, argv and kernel facts), and in `RECORDS` after a failing C2 check and after W's `STOP` in place of `RECORDS`; a `STOP` lost on SP_L at L's `exec` and repeated to C; a `STOP` before C's interruption point (`CHILD_REFUSAL`) and after it (`CHILD_START`, then `SIGTERM` to the selftest target); a failing spawn call (`SPAWN_FAILED`, `started: false`); an EOF from C before any message (`target_started` stays `unknown`, and no refusal record is written); `RELEASE_INTENT_RESULT` after the deadline (the window written first, the late result recorded) and never (release performed, durability-UNKNOWN); a failed export (`EXPORTED` with state `failed`); `RL_IDENTITY` present, missing and duplicated; a descriptor sent by L, C or O to W (discarded, a channel failure); and any message outside the machines is a channel failure. The release cases use a sacrificial copy of the window protocol on a sacrificial path |
| P-SEAL | `setup-identities.json` does not list itself; on a sacrificial copy of the installation that the operator prepares, never the real one, a changed byte of it makes `dispatch` and `seal-front` refuse before any mutation and `materialize` refuse when an adoption record exists; without one, `materialize` records `unadopted`, and the later `dispatch` refuses on the mismatch; `adopt` refuses at AD5 after exactly the AD3 bookkeeping of §11.7; a selftest only records the values |
| P-SR | S-R's classification and transition logic run against recorded synthetic observations and logs, as in P-SETUP (no account is created by a probe): every atom class in its pre-state, in each forward and reversal intermediate state with its co-effects, in its post-state and in *other*; a parent directory whose entry set and link count an atom changed, classified at its G_j, never *other*; an earlier script's object that a later script changed (`/opt/wlscratch` after S-H) classified at the current global phase; a partial create, a partial install, a partial removal and a partial reversal, each classified as its partial vector, never *other*, and completed without rerunning any completed create; an atom whose object and co-effects are in their post-state and whose `done` line is missing (resume skips it); an account reversal that also removed its user-private group (`USERGROUPS_ENAB yes`; a W_j vector, from which resume re-creates the group first); a service action pending (its effect absent) and done; a check never re-run at or before the matched position; a stopped rollback classified against H_0, …, H_M; two objects between states (S-R stops); a torn last log line (ignored; S-R's own log is new) and a malformed middle line (S-R stops). Helper tests: `step.py` with an injected short `os.write` completes the line or exits 3, and refuses to append after a torn line; `check_out.py` exits non-zero for a failing command, a mismatching or extra output, and a command path that is not absolute (correction W1-V6-COMPOSED-STATE) |
| P-IMAGE | images only: W, W2 and RL list the images directory and compare its exact entry set at every use; a third entry that A6 adds to a sacrificial copy makes each of them refuse before any mutation or view; they read the backing files' pinned identities by name; O and C never see the directory (masked); each image root's `lost+found` matches its pin, and a second root-owned entry in an image root makes W refuse (correction W1-V6-IMAGE-PIN) |

## 14. Resources, staged Gate 0 and images [corrections: W1-IMAGE-TREE; gap: resources-and-images]

Every derived number below was computed with actual MCP `jackal_exact`: v3's computations (reproduced by the sealed
gpt61-v3 review) are carried, v4's are recorded in `v4-support/jackal.json`, and v7's new numbers are recorded in
`v7-support/jackal.json` (Appendix G). Each result has status `exact`, `formal` false, lane `rat`, and the non_claims
"NOT formal-bounded: this lane carries no Lean-checked certificate", "The epistemic class above is the STRONGEST claim
this result supports", "exact rational arithmetic (not yet checker-covered)". No consequence ceiling field was
returned; the results are informational arithmetic only. Exact is not formal-bounded. The "approx" figures are the
tool's decimal display of the exact value. Full records: `v3-support/jackal.json`, `v4-support/jackal.json`,
`v7-support/jackal.json` and Appendices C and G. v7 changes no allowance downward; it adds the payload-pack allowance
of §14.7 and moves A_tmp's places into T (§14.5).

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
| A_in | retained inputs and messages: descriptors, lead module, observation inputs, front records, channel segments (headers and references, no bulk duplicate), role identities with module closures, F-captured W diagnostics, and `adopt`'s verify-only inputs, which v7 copies into the adoption payload pack (§15.3) | 134217728 | `128*2^20`, judgment. Largest comparable observed inputs: the v5 frame-review roster, 979762 bytes (`49133+602614+68556+250916+8543`); the base descriptors, 108768 (`1735+105491+1542`); lead module 8639 and START 2699 bytes (observed) |
| A_exp | export copies, each retained record at most once | 832564774 | `545393048+152953998+134217728` (A_rec + A_idf + A_in) |
| A_retry | partial primaries and retries, each record at most twice | 832564774 | same expression |
| A_fb | the fallback journal | 16777216 | `16*2^20` (fixed by design) |
| X | all W-1 retained additions: A_idf + A_in + A_exp + A_retry + A_fb | 1969078490 | `2*545393048+3*152953998+3*134217728+16777216`; the check, echoed as parsed `152953998+134217728+545393048+152953998+134217728+545393048+152953998+134217728+16777216-1969078490` (the tool flattened the submitted grouping parentheses), gives 0 |
| A_tmp | target temporaries (the view's `/tmp` and `TMPDIR`, now `g/tmp` and `g/tmpdir`; `/var/tmp`; `/dev/shm`): not retained by the frame, peak use | 268435456 | `256*2^20`, judgment; no observation exists and v4.3 has no such term; the first observation can only raise it |
| A_jrnl | sudo, PAM, journal and unit effects of the scopes, per stage | 134217728 | `128*2^20`, judgment; the new identities are system ids, whose messages go to the system journal |
| A_install | installed frame: code and the original baselines (v6's relocated baselines are withdrawn; the allowance is not lowered) | 115303191 | `3*38434397`; the 17 v5 frame members total 38434397 bytes (`13976+19614+922860+4986+5773785+3198141+26383551+4153+1974792+1467+5300+7869+4763+749+755+745+116891`, member sizes observed in `frame-inventory.json`) |
| A_homes | setup directories, lock, slice and tmpfiles files | 1048576 | `1*2^20`, judgment |
| A_setuprec | setup evidence (prestate, captures, installed listings, identities) | 16777216 | `16*2^20`, judgment |
| A_selftest | sacrificial selftest generations, probe records, sacrificial export | 67108864 | `64*2^20`, judgment |
| A_pack | the generation export's payload pack (§4.2 M9, §15.3): one copy of the recipe and the snapshot | 16777216 | A_mat, judgment: the pack copies exactly the materialized recipe and snapshot, which A_mat covers |

### 14.3 Stage budgets and the rule

| Stage | Required (exact) | approx | JACKAL parsed input |
|---|---|---|---|
| before setup | 2027732564230/1397 | 1451490740.3221188 | `2*(115303191+1048576+16777216)+134217728+1468268019712/1397` (A_install + A_homes + A_setuprec, their full restore, A_jrnl, A_ambient) |
| before selftests | 1843272351744/1397 | 1319450502.3221188 | `2*67108864+134217728+1468268019712/1397` (A_selftest, its restore, A_jrnl, A_ambient) |
| before every `adopt`, every `materialize` and every dispatch | 15415338242864/1397 | 11034601462.322119 | `15368462701360/1397+2*16777216`, v6's reviewed expression `2*(16777216+2242440646+545393048)+1468268019712/1397+2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` plus the payload pack and its full restore (§14.7) |

The dispatch-stage W-1 addition is 4374364596 (parsed
`2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728+2*16777216`: X, its full restore, A_tmp, A_jrnl,
A_pack and its full restore), and `15368462701360/1397+2*16777216-9304350902252/1397-4374364596` gives 0.

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

v7 additions. The view's `/tmp` and `TMPDIR` are `g/tmp` and `g/tmpdir`, which lie on the work image, so the work
payload allowance becomes A_mat + A_obj + A_tmp = 2527653318 (JACKAL exact, parsed `16777216+2242440646+268435456`);
the payload pack lies on the records image, which becomes A_rec + X + A_pack = 2531248754 (JACKAL exact, parsed
`545393048+1969078490+16777216`). The v7 ideal payload identity (work payload + records payload + the full restore of
everything retained, which excludes the temporaries + A_ambient + A_jrnl − Required) is 0 (JACKAL exact, parsed
`16777216+2242440646+268435456+545393048+1969078490+16777216+16777216+2242440646+545393048+1969078490+16777216+1468268019712/1397+134217728-15415338242864/1397`).
It is still only an ideal payload identity.

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
automount unit and no fstab line. The views' binds of `g/source`, `g/tmp` and `g/tmpdir` are binds of the work image
and inherit its `noexec`, as the compatibility statement above requires.

**S-J, images (only if chosen; replaces step B 4 of S-B; every step logged as in §11.4).**
- J0: `need_absent /var/lib/wlscratch-images /var/lib/wlscratch/runs` and the two mount-unit paths.
- J1: `install -d -o root -g <W> -m 0750 /var/lib/wlscratch-images` (W and W2 can list and search it, so they compare
  its exact entry set and the image files' pinned identities at every use, §3.4, §11.7; nobody but root can write it or
  open the image files, which stay root:root 0600, J2).
- J2: create the two image files with `fallocate -l <reviewed size>`, then `chmod 0600` and `chown root:root`;
  verify type, size, owner and mode.
- J3: `mkfs.ext4 -L <reviewed label> -U <reviewed uuid>` on each image file.
- J4: `install -d -o root -g root -m 0700 /var/lib/wlscratch/runs` (T_root's bare mount point).
- J5: install `var-lib-wlscratch-runs.mount` (reviewed bytes), `systemctl daemon-reload`, `systemctl enable --now` it;
  verify the mountinfo entry (§3.4).
- J6: on the mounted work image root: `chown <W>:<W>`, `chmod 0700`; then `install -d -o root -g root -m 0700
  /var/lib/wlscratch/runs/records` (R_root's bare mount point, on the work image).
- J7: install `var-lib-wlscratch-runs-records.mount` (reviewed bytes), reload, `systemctl enable --now` it; verify the
  mountinfo entry and its parent mount ID (§3.4).
- J8: on the mounted records image root: `chown <W>:<W>`, `chmod 0700`. S-B's step B 5 then sets and checks the ACLs.
A stop in S-J is reconciled by S-R like any other script, in the global phase of §11.4.

### 14.6 Memory, CPU and caps

Unchanged from v5: `MemoryMax=8G`, `MemorySwapMax=0`, core 0/0, `-j2`, the 16777217 kB gate and the receipt
protocol. U holds only C and the target, as v5's scope held only its child and the target (§9.3 G6), so no frame
process shares the target's memory limit beyond v5's child. The views' masks are empty `tmpfs` mounts and their
namespaces are kernel objects; RL, L, C and O use RAM and processes; this is not disk and is not budgeted as disk.

### 14.7 The payload pack and the complete storage accounting (v7) [correction: W1-V6-EVIDENCE-RESTORE]

v6's copy-route allowance A_copy, its fresh and retired roots and their exemption from export are withdrawn with the
copy route. Every byte the frame retains, and every byte a full restore needs, is now counted under the unchanged
storage obligation and the unchanged reserve:
- **Originals in T:** P_adm under A_mat (the recipe and the snapshot) and A_in (input records); the partition contents
  under A_obj; P_att and P_ado under A_rec, A_idf, A_in, A_retry (written but uncommitted records and retries, each
  record at most twice) and A_fb (the fallback journal). An unnamed `O_TMPFILE` inode whose commit failed is freed when
  its descriptor closes and retains nothing (§10.1).
- **Exports:** every retained record at most once under A_exp, and the payload pack under A_pack.
- **Target temporaries:** A_tmp, not retained by the frame; v5's `/tmp` rule removes aged files below `g/tmp` (§11.5
  S-F), and nothing removes `g/tmpdir`'s, as nothing removed v5's `TMPDIR`'s.
- **Full restore:** the vault backs up only the exports (§8.5); a full restore of them needs temporary space equal to
  what it restores, which the formula's doubled terms carry for every retained class, the pack included (2 × A_pack).
- **Copies:** none. v7 copies no target output; there are no partial, fresh or retired copies to account for.
So the materialize, dispatch and adopt stages' Required becomes 15415338242864/1397 (§14.3); the raise is only added,
replaces or lowers no allowance, and no allowance shrinks because a run used less. A stage whose fresh reading does not
satisfy the rule is DEFERRED: a legitimate capacity deferral under the original storage ruling, with the reserve and
the accounting unchanged, never a new cap, a release gate or a refusal of an accepted case (§21).

## 15. Rollback, freeze/export and evidence [corrections: W1-SETUP-PROBES-ROLLBACK, W1-COMMIT-JOURNAL-EXPORT; gap: rollback-and-evidence]

### 15.1 Rollback order (operator; every step's before and after state captured raw)

1. **Revoke new launches first.** Preserve the bytes and sha256 of `/etc/sudoers.d/wlscratch-frame` in
   `/root/wlscratch-staging/rollback-<stamp>/`, remove it, run `visudo -c`. No new writer can start.
2. **Wait for and reconcile every pending and running participant before withdrawing anything else:** no process with
   uid W (including writers started before step 1); no `sudo` process naming a frame entry; every child cgroup of
   `wlscratch.slice` absent or `populated 0`; CRED (§9.4): no process with uid R or gid GATE. A live participant is
   waited for; killing one is a separate, recorded, explicit operator decision. Any UNKNOWN holds the rollback at this
   step.
3. **The shared window.** If it is reserved by a W-1 attempt and known-terminal ownership is uncertain, it is a hold:
   never force a release. If ownership is known terminal and the reserving front is gone, the operator resolves it
   explicitly and records the resolution; the frame never does.
4. Preserve and remove `/etc/sudoers.d/wlscratch-run` (the RL rule); `visudo -c`.
5. Only after step 2 holds: preserve (bytes and sha256) and remove `/etc/tmpfiles.d/wlscratch.conf` and
   `/etc/systemd/system/wlscratch.slice`; `systemctl daemon-reload`; verify that `systemctl show wlscratch.slice -p
   FragmentPath -p DropInPaths` shows both empty.
6. **Images, if used:** identify every start source first (the two mount units, `systemctl list-dependencies
   --reverse` of each, any automount unit, fstab: none expected); `systemctl disable` both units; verify that no process
   has a file open on them and that step 2 still holds; then stop the records unit first and the work unit second
   (unmount); verify that each is unmounted and that each bare mount point equals its setup identity (§11.7); preserve
   the unit files (bytes and sha256), remove them, `systemctl daemon-reload`, verify no remount. Keep the image files and
   record their sha256.
7. Nothing is restored in `/home/sicarii`: v7 sets no ACL there (v6's home-ACL restore is withdrawn with Option A).
8. Lock and expire both accounts (`usermod -L -e 1`); keep them, so evidence ownership keeps its meaning. Then preserve
   and remove the sshd drop-in, `sshd -t`, reload.
9. Keep as evidence: `/var/lib/wlscratch` (generations, records and exports), `/opt/wlscratch`,
   `/root/wlscratch-staging` (including the step logs and every rollback capture) and every capture.

The rollback steps are the atoms of the rollback's global sequence (§11.4) and are logged like setup steps. A stopped
rollback step is reconciled by the same rules, and nothing is called restored without its equality capture.

### 15.2 What rollback leaves

Remaining: the two locked and expired accounts and the three groups (the two user-private groups and
`wlscratch-gate`), with their numbers; their `passwd`, `group`, `shadow` and `gshadow` entries; every file under
`/var/lib/wlscratch*`, `/opt/wlscratch` and `/root/wlscratch-staging`; images, if any; journal entries. Removed: both
sudoers files, the sshd drop-in, the slice unit, the tmpfiles rule, the mount units. Not restored: a pristine
pre-setup system.

### 15.3 Freeze and export [corrections: W1-V6-EVIDENCE-RESTORE; v4: W1-COMMIT-JOURNAL-EXPORT]

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

**Payload packs** (correction W1-V6-EVIDENCE-RESTORE). The generation export (`export/generation/`) holds, besides the
generation journal's records, a payload pack: one export copy of every recipe file and every snapshot file, read back
by W from P_adm with `O_NOATIME` and listed in the manifest with its relative path, sha256 and size (§4.2 M9). Each
`adopt` increment holds an adoption payload pack: one export copy of every verify-only input F streamed (the two review
rosters and freeze records, the provenance triples, the observation), with the lead-tree path F read it from. These are
exactly the payloads that channel segments reference by `written` or `source` (§7.3); everything else a segment
references is a record that some increment exports. So the exports of a generation, of each of its attempts and of the
adoption they bind are self-contained: an offline reader holding only them, from the vault or locally, recomputes every
chain head, every marker digest and every payload digest. The protected originals are not needed by any promised
reader, which is why the vault pins exports only (§8.5).

**Increments and the finite prefix.**
- An export increment n of a journal J (an attempt journal or an adoption journal) is defined by its cut c_n: the head
  (seq, sha256) of J's chain (§10.2) when the increment starts, which §10.2's commit primitive makes a record-free
  marker, so that every record-bearing chain marker at or below it is confirmed (c_−1 lies before seq 0); and, for an
  attempt journal, the writer's next fallback slot index s_n at that moment (s_−1 = 0). Increment n exports exactly:
  every chain marker of J with c_(n−1).seq < seq ≤ c_n.seq, as a marker file; for each such marker of kind `primary`
  or `retry`, the record it commits (a marker of kind `export` points at a copy that is already in P_exp, so only the
  marker file is exported); the fallback slots with index from s_(n−1) up to s_n − 1, the VALID ones as decoded
  entries of `fallback-slots.json` and the TORN ones by index and the sha256 of their raw 65536 bytes only; and, by
  path, size and sha256 with state `raw`, every RAW file of J's `commits/` (§10.2) and every uncommitted record file
  present in the partition at the cut, whatever its seq, that no earlier increment listed. Raw bytes (TORN slots, RAW
  marker files, uncommitted records) stay in their protected original place and get no parsed or success credit. A
  writer that cannot append to J (a branched journal, or rule J4 of §10.2) makes no increment, and `EXPORTED` reports
  state `failed`. A committed record with `synced: false` is exported with that value.
- After the copies, the increment's `manifest.json` (`wlscratch-export-v3`: per entry the export path, source path,
  sha256, bytes, final mode, `acl_sha256`, source marker digest, `synced` and state ∈ {`committed`, `fallback`,
  `torn`, `raw`, `payload`}, and the export directories' identities) and `freeze.json` (`wlscratch-freeze-v3`:
  increment number, cut c_n, slot range, the previous increment's freeze-marker digest, the digest of every export
  marker committed for this increment, the manifest's sha256, `raw_files`, channel heads, boot id, time) are written
  with the export primitive and committed. `raw_files` lists every RAW file of J's `commits/` and every uncommitted
  record file that appeared after the cut and that neither an earlier increment nor this manifest listed, so every raw
  file is listed exactly once. The export markers of increment n, its freeze marker and the close markers that confirm
  them have seq > c_n.seq, so the next increment exports them. The last increment's export markers are listed by
  digest in its own freeze record; only its freeze marker and the close marker that confirms it are never exported:
  the freeze marker's digest goes to F in `EXPORTED` and `FINAL` and is printed, and the originals stay in the
  protected journal.
- **Who makes increments.** For an attempt: W at M11 or D19 (increment 0, after `final-status.json`), then each W2 at
  the end of its work (the next increment), which therefore exports the later evidence: W's late records if any, W2's
  recovery and release records, the front terminal record and their markers. For a generation: one export,
  `export/generation/`, of the generation journal with the materialization marker as its cut, and its payload pack;
  that journal never grows again, so this export is complete and final; its export markers live in A0's attempt journal
  and are exported by A0's increment 0. For an adoption: each `adopt` invocation makes the next increment of the
  adoption journal, with its payload pack, in `adoption-<I>/export/inc-<n>/`.
- **Accounting.** Cuts are disjoint, so every record and marker is exported at most once across all increments, and
  A_exp's "each retained record at most once" (§14.2) is unchanged; the payload packs are counted under A_pack and A_in
  (§14.2, §14.7).
- F re-reads every copy of each increment through its ACL, compares it with the manifest's final values, and keeps each
  freeze-marker digest from `EXPORTED` and `FINAL`.
- **What "frozen" means:** create-only, W-exclusive, no verb that modifies or deletes, digests in a hash-linked
  journal. **Limits:** root, or W running changed code, could still alter them; no immutable attribute is set (that
  needs `CAP_LINUX_IMMUTABLE`).
- Lead copies of exports are mutable evidence records, not authentic producer custody. A project-vault transfer of
  exports (§8.5) is backup, not authenticity.

### 15.4 Evidence classes (all retained raw)

Pre- and post-setup captures with digests, the step logs and every S-R capture; `passwd`, `group`, `shadow` (first
character only) and `gshadow` lines; `getfacl`/`stat` outputs; sudoers, sshd, slice and tmpfiles bytes; `findmnt`,
mountinfo, kernel settings and features; installed-inventory comparisons; role identities and module closures; RL
identities with their view specifications, mountinfo, maps and Landlock rulesets; selftest and probe records with raw
errnos; every committed record and marker, every retry, every fallback allocation descriptor and slot (VALID decoded,
TORN raw), every raw uncommitted record, channel segment, wait, participant, scope, census and CRED record; launch and
observer intents, `spawn-ok`, the conclusion, stream finality, final status and the release records (`release-intent`,
`window-release`, `release-withheld`, `release-not-owner`, `release-failure`) from W and from each W2; recovery
records; front terminal records; export increments with their manifests, freeze records and payload packs; the
adoption record and its exports; F's console output as preserved in the lead transcript (neither durable nor frame
custody); rollback captures. **Limits:** hashes of W-owned files describe files that root or W could change; copies
are evidence records; none of this is producer authenticity, proof or acceptance.

## 16. Setup, verification and adoption order

1. Actual gpt-6.1-sol review of this v7 design.
2. Frame v6-W1 code implemented, frozen in SOURCE_FRAME (members 0644, directories 0755; the inventory records
   `install_root` and `source_frame`) and reviewed as code by actual gpt-6.1-sol, the review sealed in
   `<SOURCE_FRAME>/review/gpt61-v1/` (REVIEW): front (`adopt`, `materialize`, `dispatch`), writer (the same verbs,
   `seal-front` in both modes, `selftest`), RL (`sandbox_launch.py`) and the view it builds, launcher, child, observer,
   the final pass with excluded-leaf keys, the census and CRED, the channels and their state machines, commits,
   journals, the fallback journal and exports with their payload packs, recovery, the selftest verbs and probes, and the
   helpers `absent.py`, `step.py` and `check_out.py`.
3. Concrete setup inventory (fixed numbers; filled prestate P1-P26; exact script texts and digests, with S-J if images
   are chosen, and S-R's global atom table; expected ACL texts; sudoers, sshd, slice and tmpfiles bytes; the view's
   mount table, maps and Landlock ruleset), reviewed by actual gpt-6.1-sol.
4. Gate 0, setup stage, on a fresh reading.
5. Operator approval of the concrete setup (reserved authority).
6. The operator runs, or explicitly authorizes, S-0 to S-I (and S-J if images are chosen); S-R only after a stopped
   script, by explicit operator choice.
7. Gate 0, selftest stage; lead verification (§11.6), selftests and probes (§13), including P-NS, P-IDMAP, P-LL,
   P-PTRACE, P-FH, P-CG, P-IOEXIT and P-ENOSPC.
8. Installed-identity, baseline (including the candidate view baseline) and probe evidence, with the source-level
   readings that §9.8 N7 names, reviewed by actual gpt-6.1-sol, the review sealed in
   `<SOURCE_FRAME>/review/installed-gpt61-v1/` (INSTALLED_REVIEW).
9. Gate 0 with the materialize/dispatch-stage expression (procedural); then `front.py adopt …`: W commits the fresh
   installed-frame adoption record at `/var/lib/wlscratch/runs/records/adoption-<I>/lead-adoption.json` (§4.6), with
   the fresh lead observation `scratch-adopt` (v5 `adopt` semantics).
10. Gate 0, dispatch stage; only then `materialize` and dispatch, each under fresh original admission.

No step authorizes the next by inference. This refines v3's order (closed as W1-SETUP-ORDER) by naming the adoption's
writer, destination and review inputs, without changing its substance.

## 17. Placement of every v5 mechanism

| v5 mechanism (frozen `scratch.py`) | W-1 placement | Change, and why it preserves the original |
|---|---|---|
| `Dir` anchoring, `verify_location`, `child(create=True)` authentication, `write_bytes`/`write_json`/`open_stream`/`set_mode` (S:144-358) | W and W2 for every frame mutation; C and O for anchored reads through the view; F for anchored input and window reads | none in semantics; the location chain is now protected (§3.4, §4.5); records are linked only after validation (§10.1) |
| `stat_key`, `observe_tree` (v6 final pass), `read_observed`, `read_prefix`, `read_files` | C and O full walks through the view, with `O_NOATIME`; W writer-owned walks (partition contents skipped); F base-tree and transcript reads, with `O_NOATIME` | `observe_tree` also returns excluded-leaf keys (§4.5); the walk rules are v5's |
| `retain`, `guarded`, `read_record`, `last_resort`, `retain_observation` (S:375-436, 1109-1128) | W and W2 | commit markers, journals with committed chains, the fallback journal with an immutable allocation descriptor and append-only slots, consumer precedence, durability-UNKNOWN (§10); the compact equal-record form unchanged |
| `exec_verified`, frame inventory, `frame_admitted` (S:587-863) | installed members checked by W, RL, L, C, O; review, installed-review, rollout and transcript joins by F; the adoption record's structural joins by W | `install_root` replaces `frame`; the adoption record is W's protected record (§4.6); F's joins at v5 trust (R2) |
| `adopt`, `validate_adoption_observation`, `rollout_join`, `review_profile_problems` (S:687-837) | F (lead-context checks), W (structural re-verification, create-only commit) | destination moved from the frame's review directory into the protected tree; every v5 join kept; installed-review joins added (§4.6) |
| `materialize` recipe (S:959-1049), `expected_source`, `overlay_rules` | W `materialize` | streamed verified bytes; no partition root is created, as in v5 (S:1033); `tmp/` and `tmpdir/` are created for the view (§4.2 M7) |
| `command()` allowlist (S:1054-1070) | W, re-derived by C | unchanged |
| `specifications()` (S:1073-1106) | W builds, C verifies | v5's own source relocation only (§8.4) |
| `identities()` (S:1131-1153) | O (`parent`, `after`) and C (`child`) inside the view, against the original baselines; the manager environment and F's runtime in the real context | the original baselines (§8.4, P-VIEW) |
| `sample()` (S:1156-1179) | F half (sibling units in `sicarii`'s manager, with no unit allowed, and `storage_status.py`); helper half (heavy processes, meminfo) | split by authority; same checks (§9.4) |
| `threshold_receipts`, `receipt_line`, `memory_gate` (S:1186-1248) | W issues and verifies; F forwards from the inbox | unchanged constants and deadlines; "through original stdin" = W's stdin channel |
| `window_locked`, `window_read`, `window_write`, `reserve`, `owns_window`, `release` (S:1253-1341) | F | unchanged protocol; attempt records committed by the serving writer under F's lock in the same order; the release record's durability does not gate the window write (§9.4, supplied ruling) |
| `ancestors`, `processes_naming`, `owned_terminal` (S:1346-1415) | O at the after stage, W2's recovery rounds, F at the release point | v5's predicate, unchanged in meaning, over a system-manager scope (§9.4); no inference from missing records |
| `final_stream_sync` (S:1420-1437) | W after terminal | unchanged, followed by stream finality from U's `populated 0` (§10.6) |
| `admission()` (S:1440-1448) | split per stage among F, W, O and C | the same checks (Appendix D) |
| `spawn`, `wait_blocked`, `pending_handled`, `raising_handler` (S:1469-1517) | every waiting role; C spawns T exactly as v5 (`fchdir`, core 0) | H-S1/H-M3 synchronous handling; `STOP` down the channels |
| v5's scope launch `systemd-run --user --scope` (S:1564-1594) | RL's `systemd-run --scope` in the system manager, before the view; L `exec`s C in place | the same limits; another manager (§12.3 V10); U holds C and the target only, as v5's scope did |
| `started_by_dispatch` (S:1520-1527) | W: `SUDO_*` plus `HELLO_ACK` plus stdio inode join; W2: front-process triple | the invoker is bound by kernel identities instead of a parent command line |
| `refusal_record`, `run`, `conclude` (S:1530-1765) | W (`dispatch`), F (release), O (terminal observations), W2 (recovery) | N13 recomputation; `final-status.json` |
| `child` (S:1768-1896) | C | §9.3 C1-C12, over a direct channel to W |
| `dispatch` (S:1899-1988) | F | inbox answers over the channel; S1 wait via W2; N14 exit |
| `verify_materialization` placement: materialize, parent and child admission, immediately before spawn, conclusion | W at M8; O at the parent stage and W's writer half; C at the child stage and as the final pass; O and W at the conclusion | same placements, now split by authority |
| launch seal in argv (S:1570-1594, 1783-1817) | RL's, L's and C's argv carry the `launch.json` and `admission.json` sha256; C verifies the bytes delivered over its channel | V4-B03 kept |

## 18. Per-correction and per-gap status (the author's assessment, for the independent reviewer to judge)

"CLOSED-AT-SPEC-LEVEL" is this author's claim that the specification text now covers what the item asks for. It is
not closure, not executed evidence and not acceptance; the reviews state that they do not adopt such claims by
repetition. "OPEN" marks an item that v7 does not claim to meet. "CLOSED (gpt61-v6), carried" marks items that the
gpt61-v6 review closed; v7 keeps them as §0.5 states. Every original obligation, V5-B01, V5-B02,
W1-V5-PRESERVATION and Gate 0 stay OPEN regardless (§0.4, §22).

### 18.1 The gpt61-v6 review's required W-1 changes (verbatim) and the author's assessment

Each change is quoted verbatim from `review.json` (`required_changes`, field `change`). There are 11 (JACKAL exact,
parsed `1+1+1+1+1+1+1+1+1+1+1`).

1. **W1-V6-PRESERVE.**
   > Keep the original success domain fixed. Replace accepted-case restrictions and observable substitutions with a preserving design; where none exists, retain V5-B01, V5-B02 and W1-V5-PRESERVATION OPEN. Remove the claims that no original output state is refused and that the copy-data ceiling is not a narrowed case.

   v7: §22 evaluates the enforcement designs beyond the unprivileged DAC architecture and adopts the target view
   (§12), which removes the copy route with its observable substitutions and its ceiling, the user manager, the
   relocation, `no_new_privs` and the anti-setid filter, the pre-created partition roots, Option A and v6's release
   expansion; §12.3 and §21 list every change that remains; both claims the change names are withdrawn with the copy
   route (§0.2). **Author's assessment: OPEN.** No candidate is established as preserving: the view's changes
   (§12.3 V1-V12) leave the allowlisted actions' observable behaviour unchanged only if premise TOOL-CLOSURE holds,
   which is unestablished (§22). V5-B01, V5-B02 and W1-V5-PRESERVATION stay OPEN and are not narrowed.
2. **W1-V6-READ-MUTATION.**
   > Provide enforced confinement for every frame-caused filesystem mutation, including file/directory read-side atime updates and proof-report reads. Prevent the foreign-source side effect with a preserving mechanism or retain V5-B02 OPEN for that route; correct K5/K8's universal no-mutation and only-copy-read statements.

   v7: §9.8 N6 inventories every read route, the report read and directory listings included; `O_NOATIME` on every
   route where the reader owns the object (R-a, R-b, R-c, R-e), which in the view covers every entry below `source/`,
   because through the run-path idmap the reader owns them all; K5's and K8's statements are withdrawn (§0.2).
   **Author's assessment: OPEN for routes R-d, R-f and R-h, where V5-B02 stays OPEN; CLOSED-AT-SPEC-LEVEL for the
   other routes, conditional on P-NOATIME and P-IDMAP.** Still needed: the code, P-NOATIME, P-IDMAP, and the
   reviewer's ruling on R-f (root-owned files, as v5 read them) and R-h (the target's `exec`).
3. **W1-V6-COMMIT-AMBIGUITY.**
   > Make failed-close truth observable and consistent for every writer, reader, export and reboot interpretation, including a complete valid close whose fsync, directory fsync, post-validation or join failed and whose continuation is absent or fails before producing a valid file. Preserve failure/downgrade/raw evidence; add these declarative cases to P-CHAIN.

   v7: §10.1 (unnamed inodes; `fsync` and validation before a create-only link; one commit point, the close marker's
   link; `synced: false` after it), §10.2 (J4, J5, every consumer), §10.5, §9.5, §9.6, §15.3 and §13.1 P-CHAIN with the
   declarative cases. **Author's assessment: CLOSED-AT-SPEC-LEVEL.** Still needed: the code and its review; P-CHAIN and
   P-COMMIT, including the link through `/proc/self/fd` from a non-dumpable writer.
4. **W1-V6-COMPOSED-STATE.**
   > Define global phase-aware setup and rollback vectors over all effects of each atom, including parent-directory entry sets/link counts and cross-script shared objects. Project earlier and later script expectations through the current global phase. Name all ordinary partial creates, installs, removals and reversals without classifying them as other or rerunning completed creates.

   v7: §11.4 (effect sets with co-effects, one global sequence and object set, G_j with partial and co-object vectors,
   S-R over the whole observation, the rollback's H_i) and §11.5's class table with co-effects; §15.1; §13.1 P-SR.
   **Author's assessment: CLOSED-AT-SPEC-LEVEL (templates; the exact global atom table comes with the concrete
   inventory).** Still needed: the concrete inventory and its review; P-SR and P-SETUP.
5. **W1-V6-IMAGE-PIN.**
   > Restore complete per-use exact images-directory entry-set verification while preserving protected exposure and role authority, or redesign the branch. Do not replace it with setup/rollback-only operator captures or add a new operator gate.

   v7: the images directory becomes root:W 0750, so W, W2 and RL list it and compare its exact entry set at every use
   (§3.4, §11.7, §14.5 J1); the image files stay root:root 0600; no operator capture substitutes and no gate is added;
   §13.1 P-IMAGE. **Author's assessment: CLOSED-AT-SPEC-LEVEL.** The names become listable by W, which the setup record
   already states (§11.7). Still needed: the image inventory and its review; P-IMAGE and P-MOUNT.
6. **W1-V6-C1-DATA.**
   > Limit C's first hello checks to facts available from compiled expectations, argv and kernel observations. Perform launch-environment/template and launcher-intent descriptor-pin checks only after authenticated RECORDS delivery in C2, before any spawn request. Preserve legal early refusal and STOP branches and truthful no-start/unknown outcomes.

   v7: §9.3 C1 (compiled grammar, argv, kernel facts only) and C2 (the template, environment and descriptor-pin checks
   after `RECORDS`, before `SPAWN_REQUEST`); C's refusals and `target_started` unchanged; Appendix B.4.4.
   **Author's assessment: CLOSED-AT-SPEC-LEVEL.** Still needed: the code; P-PROTO.
7. **W1-V6-SCAN-STATE.**
   > Supply an enforced or source-grounded argument connecting complete process/credential/manager/descriptor scans to one common quiescent state under fork, exit, credential and queued-input churn. State any missing premise explicitly as unestablished with its evidence obligation. Replace 'same st_dev means no mount boundary' with the exact required predicate.

   v7: the manager and descriptor scans are withdrawn with the manager and the copy route; §9.4's census reads one
   absorbing kernel state per earlier scope (`populated 0`), and CRED checks an enforced property; §9.8 N4 connects
   them to the final pass; §9.8 N3 states the exact mount predicate; §9.8 N7 names P-CG, P-NOR, P-IOEXIT and P-CENSUS
   as unestablished with their probes. **Author's assessment: CLOSED-AT-SPEC-LEVEL as an argument, conditional on
   those unestablished premises.**
8. **W1-V6-COPY-PROBES.**
   > Specify the group-setting operation and readback, source/destination attribute order and compatibility for all original accepted filesystems/owners. Complete L1's registered-description coverage and P-PTRACE's process_vm_writev and access-mode/positive controls. Preserve redesign/no-exception consequences; do not promote finite probes or a first run into universal premises.

   v7: the copy route, its group setting and attribute order, and premise L1 with the lease test are withdrawn, so the
   first two sentences have no object left; §13's P-PTRACE row is complete (`process_vm_writev`, both access modes,
   every pull operation, positive controls by root and by a traced descendant); §13 states that a probe only refutes
   and that no first run becomes a premise. **Author's assessment: CLOSED-AT-SPEC-LEVEL.** Still needed: P-PTRACE.
9. **W1-V6-INVARIANTS.**
   > Reconcile the P_adm/P_out model with root-exchange mutations of admitted parent directories and place final admission after every actual admitted-tree mutation without deleting checks. Scope 'no ACL/default ACL/no mode changes' to the intended immutable recipe/bookkeeping objects while explicitly accounting for fresh-copy attributes. Make adopt's seal timing exception to pre-mutation wording exact.

   v7: P_out, the fresh roots and the root exchange are withdrawn, so after M8 no frame mutation of `source/` or of a
   directory above an admitted entry exists (§4.1, §5.2), and the final pass follows every actual mutation (§4.5); §6.1
   and §6.2 scope the no-ACL rule to the frame's recipe and bookkeeping objects and leave the target's objects to the
   target; no copy exists, so no copy attribute; §11.7 states `adopt`'s one exception exactly. **Author's assessment:
   CLOSED-AT-SPEC-LEVEL.**
10. **W1-V6-EVIDENCE-RESTORE.**
    > Account for all retained originals, partial/fresh/retired copies and required temporary full-restore space under the unchanged storage obligation. Specify which protected payload dependencies let each promised channel/export reader reconstruct and verify its evidence, and how those dependencies remain available through backup/restore. Retain authentic-context vault gates and existing operator authority.

    v7: §14.7's accounting with A_pack (§14.2, §14.3, §14.5); the payload packs (§4.2 M9, §15.3), with every segment
    reference resolving inside the exports (§7.3); the vault pins both export trees with v5's authentic-context gate
    (§8.5). **Author's assessment: CLOSED-AT-SPEC-LEVEL.** The storage obligation itself (safe-fresh-capacity,
    verified-backup-restore-rollback) stays OPEN; V-VAULT is unexecuted.
11. **W1-V6-CATALOGUE.**
    > Correct section 21 and its cross-references: separate the original S5 baseline from the criterion-required S6 final-pass repair; correct A4's recorded-mode claim and K8/report-read baseline; enumerate copy byte-read/SEEK/attribute failures and new deadline effects; remove D3/D8 causal absolutes; distinguish legitimate capacity deferral from new caps, release gates and accepted-case refusals.

    v7: §21 is rewritten: the S5 baseline and the S6 repair are separate; A4 and the report-read baseline are
    corrected; the copy failures are listed as withdrawn with the copy route; the deadline effects are rows; no causal
    absolute remains; capacity deferral is distinguished. **Author's assessment: CLOSED-AT-SPEC-LEVEL as presentation;
    the rows' OPEN treatments stand.**

### 18.2 Prior corrections, as the gpt61-v6 review ruled on them

| Prior correction | gpt61-v6 | v7 | Author's assessment |
|---|---|---|---|
| W1-COMMIT-JOURNAL-EXPORT | PARTIALLY_CLOSED | §10.1, §10.2, §15.3 (W1-V6-COMMIT-AMBIGUITY, W1-V6-EVIDENCE-RESTORE) | CLOSED-AT-SPEC-LEVEL |
| W1-CUSTODY | PARTIALLY_CLOSED | §9.8, §9.4, §4.5, §12.2 | custody: CLOSED-AT-SPEC-LEVEL, conditional on §9.8 N7; preservation: OPEN (§22) |
| W1-CUSTODY-CLOSURE | PARTIALLY_CLOSED | §5.3, §9.4 CRED, §9.8 N1-N4 | the same |
| W1-DURABILITY-RELEASE | CLOSED_AT_SPEC_LEVEL | §9.4's procedure, hold and window-write paragraphs and B.4.4's `RELEASE` rows carried; condition 2 of the release rule restated as v5's terminal predicate (W1-V6-PRESERVE, v6 D5) | CLOSED (gpt61-v6), carried, with that restatement for the reviewer |
| W1-GENERATION-PROTOCOL | PARTIALLY_CLOSED | §4.2, §9.3 (W1-V6-C1-DATA), Appendix B.4 | CLOSED-AT-SPEC-LEVEL |
| W1-IMAGE-OBSERVATION | PARTIALLY_CLOSED | through W1-V6-IMAGE-PIN | CLOSED-AT-SPEC-LEVEL |
| W1-IMAGE-TREE | PARTIALLY_CLOSED | through W1-V6-IMAGE-PIN and W1-V6-INVARIANTS (no `outputs/`) | CLOSED-AT-SPEC-LEVEL |
| W1-JOURNAL-CONTINUATION | PARTIALLY_CLOSED | through W1-V6-COMMIT-AMBIGUITY | CLOSED-AT-SPEC-LEVEL |
| W1-LIFETIME-ROLLBACK | PARTIALLY_CLOSED | through W1-V6-COMPOSED-STATE (§11.4, §15.1) | CLOSED-AT-SPEC-LEVEL |
| W1-PROTOCOL-FAILURE-STATES | PARTIALLY_CLOSED | through W1-V6-C1-DATA and W1-V6-COMMIT-AMBIGUITY (§9.5) | CLOSED-AT-SPEC-LEVEL |
| W1-RESOURCES | CLOSED_AT_SPEC_LEVEL | §14.1 and §14.4 carried; §14.2, §14.3, §14.5-§14.7 raise only (A_pack, A_tmp placement); A_copy withdrawn | CLOSED (gpt61-v6), carried, with the raise for the reviewer |
| W1-SETUP | PARTIALLY_CLOSED | through W1-V6-COMPOSED-STATE and W1-V6-IMAGE-PIN | CLOSED-AT-SPEC-LEVEL (templates) |
| W1-SETUP-IDENTITY | CLOSED_AT_SPEC_LEVEL | §11.7's seal paragraph carried with `adopt`'s exception stated exactly (W1-V6-INVARIANTS); §11.5 S-H and S-I lists follow the new setup objects | CLOSED (gpt61-v6), carried |
| W1-SETUP-PROBES-ROLLBACK | PARTIALLY_CLOSED | through W1-V6-COMPOSED-STATE, W1-V6-IMAGE-PIN and W1-V6-COPY-PROBES | CLOSED-AT-SPEC-LEVEL (templates) |
| W1-SETUP-RECONCILIATION | PARTIALLY_CLOSED | through W1-V6-COMPOSED-STATE | CLOSED-AT-SPEC-LEVEL (templates) |
| W1-TERMINAL-CUSTODY | PARTIALLY_CLOSED | §9.4 (v5's predicate; the census), §9.7, §9.8 N4 | CLOSED-AT-SPEC-LEVEL, conditional on §9.8 N7 |
| W1-V5-IMAGE-PINS | NOT_CLOSED | through W1-V6-IMAGE-PIN | CLOSED-AT-SPEC-LEVEL |
| W1-V5-JOURNAL-FAILED-CLOSE | PARTIALLY_CLOSED | through W1-V6-COMMIT-AMBIGUITY | CLOSED-AT-SPEC-LEVEL |
| W1-V5-PRESERVATION | NOT_CLOSED | through W1-V6-PRESERVE | OPEN |
| W1-V5-PROTOCOL-REFUSALS | CLOSED_AT_SPEC_LEVEL | Appendix B.4.4's early refusal frames and STOP column carried; L's `exec` of C and C1's narrowed checks amend the W↔L and W↔C rows | CLOSED (gpt61-v6), carried, with those amendments for the reviewer |
| W1-V5-RECONCILIATION-STATES | PARTIALLY_CLOSED | through W1-V6-COMPOSED-STATE | CLOSED-AT-SPEC-LEVEL (templates) |
| W1-V5-REVOCATION-CONFINEMENT | PARTIALLY_CLOSED | through W1-V6-READ-MUTATION and W1-V6-SCAN-STATE; revocation and the copy route withdrawn | custody of frame mutations: CLOSED-AT-SPEC-LEVEL except routes R-d, R-f, R-h (OPEN); preservation: OPEN |
| PKG-V6-OPERATOR-TEXT, PKG-SUPERVISION-RECORD, OD2-CONSEQUENCES, PKG-V5-FACTS, PKG-CLOSURE-STATUS, PKG-V7-AUTHOR-RECORDS | CLOSED (not re-reviewed) | package items | not in W-1's scope |

### 18.3 The section-3 gaps

| Gap | gpt61-v6 | v7 | Author's assessment |
|---|---|---|---|
| generation-order | PARTIALLY_CLOSED | §4.2, §9.3, Appendix B.4.4 | CLOSED-AT-SPEC-LEVEL |
| lease-and-writer-authority | CLOSED_AT_SPEC_LEVEL | §5.1 and §5.4 carried; §5.2 amended by withdrawing the exchange and `outputs/` and adding `tmpdir/` | CLOSED (gpt61-v6), carried |
| per-entry-modes-acls | CLOSED_AT_SPEC_LEVEL | §6.1-§6.5 amended: no partition roots, no GATE entries, `tmp/` and `tmpdir/` rows, the view column | CLOSED (gpt61-v6), carried; the amended rows are new text for the reviewer |
| channel-and-dumpability | PARTIALLY_CLOSED | §7.1, §7.3 (payload references), §7.7, Appendix B.4 | CLOSED-AT-SPEC-LEVEL |
| prestate-and-installation | PARTIALLY_CLOSED | §11 | CLOSED-AT-SPEC-LEVEL (templates) |
| exposure-options | CLOSED_AT_SPEC_LEVEL | §12 replaced by the view (one design, its exposure the original's, §12.3) | CLOSED (gpt61-v6) as to stating the options; the adopted view is new text for the reviewer |
| fresh-identities-and-vault | CLOSED_AT_SPEC_LEVEL | §8.2 and §8.6 carried; §8.1, §8.3-§8.5 amended | CLOSED (gpt61-v6), carried; amendments for the reviewer |
| denial-probes | CLOSED_AT_SPEC_LEVEL | §13 rewritten for the view | CLOSED (gpt61-v6) as to form; the rows are new text for the reviewer |
| resources-and-images | CLOSED_AT_SPEC_LEVEL | §14 raised only | CLOSED (gpt61-v6), carried |
| commits-and-durable-channel | PARTIALLY_CLOSED | §10 | CLOSED-AT-SPEC-LEVEL |
| participants-and-recovery | PARTIALLY_CLOSED | §9 | CLOSED-AT-SPEC-LEVEL, conditional on §9.8 N7 |
| rollback-and-evidence | PARTIALLY_CLOSED | §11.4, §15 | CLOSED-AT-SPEC-LEVEL |

### 18.4 The original W-1 subgaps

| Subgap | gpt61-v6 | v7 | Author's assessment |
|---|---|---|---|
| W1-CUSTODY | PARTIALLY_CLOSED | §9.8, §9.4, §4.5 | custody: CLOSED-AT-SPEC-LEVEL, conditional on §9.8 N7; preservation: OPEN (§22) |
| W1-FINAL-PASS | CLOSED_AT_SPEC_LEVEL | §4.5 items 1-3 kept, in the view | CLOSED (gpt61-v6), carried in substance |
| W1-CLOSURE | PARTIALLY_CLOSED | §10.7, Appendix B.4, §11.7 | CLOSED-AT-SPEC-LEVEL |
| W1-CHANNEL | PARTIALLY_CLOSED | Appendix B.4, §7.3 | CLOSED-AT-SPEC-LEVEL |
| W1-WRITE-AUTHORITY | CLOSED_AT_SPEC_LEVEL | §5.1 and §9.7 carried in substance; §5.2 amended | CLOSED (gpt61-v6), carried |
| W1-READ-ACCESS | CLOSED_AT_SPEC_LEVEL | §8.6 carried | CLOSED (gpt61-v6), carried |
| W1-READ-EXPOSURE | CLOSED_AT_SPEC_LEVEL | §12 (the original exposure through the view, R5) | CLOSED (gpt61-v6), carried in substance |
| W1-PREFLIGHT-IDENTITY | CLOSED_AT_SPEC_LEVEL | §8.1 amended | CLOSED (gpt61-v6), carried |
| W1-SETUP-PRESTATE | CLOSED_AT_SPEC_LEVEL | §11.1-§11.3 amended | CLOSED (gpt61-v6), carried |
| W1-SETUP-ORDER | CLOSED_AT_SPEC_LEVEL | §16 amended in content lists only | CLOSED (gpt61-v6), carried |
| W1-SETUP-EXACTNESS | PARTIALLY_CLOSED | §11.4, §11.5, §11.7 | CLOSED-AT-SPEC-LEVEL (templates) |
| W1-IMAGE-GEOMETRY | CLOSED_AT_SPEC_LEVEL | §14.5 carried, raised | CLOSED (gpt61-v6), carried |
| W1-IMAGE-COMPATIBILITY | CLOSED_AT_SPEC_LEVEL | §14.5 carried | CLOSED (gpt61-v6), carried |
| W1-VERIFICATION-PROBES | CLOSED_AT_SPEC_LEVEL | §13 rewritten | CLOSED (gpt61-v6) as to form |
| W1-FAILURE-LEASE | PARTIALLY_CLOSED | §9.4, §9.5, §9.8, Appendix B.4 | CLOSED-AT-SPEC-LEVEL, conditional on §9.8 N7 |
| W1-FAILURE-RECORDS | PARTIALLY_CLOSED | §10 | CLOSED-AT-SPEC-LEVEL |
| W1-REBOOT-RECOVERY | PARTIALLY_CLOSED | §10.1, §10.2, §9.6, §11.7 | CLOSED-AT-SPEC-LEVEL |
| W1-ROLLBACK | PARTIALLY_CLOSED | §11.4, §15.1 | CLOSED-AT-SPEC-LEVEL |
| W1-EVIDENCE | PARTIALLY_CLOSED | §7.3, §10, §15.3, Appendix B.3 | CLOSED-AT-SPEC-LEVEL |
| W1-NONCLAIMS | CLOSED_AT_SPEC_LEVEL | header, §20, §21 | CLOSED (gpt61-v6), carried in substance |

The review's additional open requirements stay OPEN, and v7 changes none of them: V5-B01, V5-B02,
W1-V5-PRESERVATION, safe-fresh-capacity, successor-frame-qualification-adoption, W1-installed-identity-probes,
full-original-strict-proof, original-native-semantic-and-cost-correspondence,
complete-original-ordinary-and-additive-controls, original-fault-campaigns, integrated-source-identity,
actual-GPT6.1-independent-acceptance, hosted-assurance-publication-deployment, verified-backup-restore-rollback and
applicable-operator-decisions.

### 18.5 Change map (every v6 unit, with its identity)

Units as §0.1 defines them. Lines, sizes (bytes) and sha256 values were computed from v6
(`ISOLATION-STORAGE-PROPOSAL-v6.md`, sha256 `5a0e861b042d11f0d9932b6b0f83020d61e944b09e730d2f7279867f24ec8f6d`) by a
read-only script on 2026-10-05. Codes: PS W1-V6-PRESERVE, RM W1-V6-READ-MUTATION, CA W1-V6-COMMIT-AMBIGUITY, CS
W1-V6-COMPOSED-STATE, IP W1-V6-IMAGE-PIN, CD W1-V6-C1-DATA, SS W1-V6-SCAN-STATE, CP W1-V6-COPY-PROBES, IV
W1-V6-INVARIANTS, ER W1-V6-EVIDENCE-RESTORE, CT W1-V6-CATALOGUE. A CARRIED unit is v7 text byte for byte, so its
sha256 is also that of the v7 unit. Counts as in §0.1: 29 CARRIED, 63 AMENDED, 26 REPLACED, and 6 NEW units.

| v6 unit | v6 lines | bytes | sha256 | v7 status | correction (change) |
|---|---|---|---|---|---|
| title | 1-66 | 5888 | `60295ce26a2f32782c4472ee88979dcc40492827791e7d81253ba8d5ef21c3d3` | REPLACED | all (status, inputs, non-claims) |
| 0 | 67-68 | 52 | `2d25497213fd27a9df7c65283d4e27447ed806290d57fc287f252ba1492b664d` | REPLACED | all |
| 0.1 | 69-86 | 1415 | `48a7c12a5d48d57858332fe860ae44f56cc8e2e5ebf329b0a4fd642043008d98` | REPLACED | all (form; base v6) |
| 0.2 | 87-123 | 3552 | `a5cd36c9f9ab2dc1b8ec631cb7cbbc81bbec527c274fea63fd77bdc163c9046e` | REPLACED | all (author corrections of v6) |
| 0.3 | 124-152 | 2808 | `d4f8fc8ed875fa72a5457918a38253ad7f4a02b7f76132f0af1485cdbc467227` | REPLACED | all (changes per required change) |
| 0.4 | 153-172 | 1580 | `a742c9e266af532b235ea132ffa00927e56add2ac6586e31ef092ad3cc71c985` | REPLACED | PS (the architecture decision) |
| 0.5 | 173-197 | 1887 | `9f79b7ce089400f7bdecf229a9895f11c946ebff3441ed9c27edcae8184bd31f` | REPLACED | all (what is carried) |
| 0.6 | 198-222 | 2111 | `d988376a3d9786f0430a4b4b340d84df54ba5d2f49054a7451282b5843f27851` | REPLACED | all (reading notes) |
| 1 | 223-264 | 3156 | `2ae9da8b3dc5177eb189805c8f7fdc48e4908a2204fb68a6b4be0b5118aa0dac` | CARRIED | — |
| 2 | 265-266 | 63 | `35f6eb75cbc9b074ead5488fca9693875386deb826fbd0374020398a83887683` | CARRIED | — |
| 2.1 | 267-304 | 3782 | `5d839c4f0cc6f849b2f8cddf356ff7c58d9bf1d42412a7ee01d2e3e3e70ae2cd` | AMENDED | PS (A1-A3 for the view) |
| 2.2 | 305-312 | 582 | `0bd0f3c4f134ef27bc917b88222b83f93d615e28a7f33367af0d32f16a568a88` | AMENDED | PS (RL and the kernel's namespace, idmap, Landlock and cgroup code in the trusted base) |
| 2.3 | 313-332 | 1910 | `5f9e1ef7a6329d7bacd127fa3f56b0aedee57b914a8f9fd599154ad0120d3820` | AMENDED | PS (kernel features; EXDEV between view mounts) |
| 2.4 | 333-380 | 4757 | `0899a44158ee6bc5d2144afe3318a72cbe9076407d6f4fee15d8220c60e4be35` | AMENDED | PS, SS (R3, R5-R7, R9) |
| 3 | 381-382 | 39 | `5510e891fd324593657d164471cb63078bbc71af4f71c2da3fc35163ae8c2ed0` | CARRIED | — |
| 3.1 | 383-398 | 1257 | `f9c9591dda30db333f3ff9de5018f53e6f5e4debb6f60934210e28352c0da597` | AMENDED | PS (the roles of R and GATE) |
| 3.2 | 399-421 | 2487 | `a2569cc36fec62f221918354895e28398a0641c187d386264eb85b0f0dde4160` | AMENDED | PS (RL, L's `exec` of C, U in the system manager; M and Option A withdrawn) |
| 3.3 | 422-462 | 3207 | `9f1f7d684a44ccf514c0bfa049fb9296b952d9c2f7acd1325735bd6d39c4a0de` | AMENDED | PS, IV (g without ACL; `tmp/`, `tmpdir/`; slice and tmpfiles; the run path) |
| 3.4 | 463-532 | 6695 | `e2961b6719c03fb094b993e932b2c20963e43f67e402de6efa4e60d602bbf601` | AMENDED | IP, IV (listable images directory; routing; RL's checks) |
| 4 | 533-534 | 106 | `030cba113f70fd51a55fba2cdbacef1d4bebdd0fa2b0813f0a7f935356beaa45` | CARRIED | — |
| 4.1 | 535-569 | 3196 | `168416e6bd78c8135e5e9224136f826dd924ed5f4fb0aaa61e89010ea637b842` | AMENDED | IV, PS (P_out withdrawn; partition contents; target temporaries) |
| 4.2 | 570-742 | 16121 | `11f5e4649567eabb5aaa1e21c4fd21cb7f2b47598297cfccc1a631a6096f90da` | AMENDED | PS, IV, ER, RM (M2, M4, M7-M9; D3, D8, D16, D17; the copy stage withdrawn) |
| 4.3 | 743-815 | 7164 | `39fdf45a201374929e1811a239aba9a4140524b1853613a62769ef952fa3fc93` | AMENDED | PS, ER (materialization v2; the view specification; RL identity records) |
| 4.4 | 816-841 | 2451 | `eb572f6edb96f31e7bf59a9d8176ed06a37de4f96282533d86a1d70d7d31a59c` | CARRIED | — |
| 4.5 | 842-899 | 5331 | `ee8568f2b29acf355943b81e6f67273307f0635b4184f926a7735928f7bd4d3a` | AMENDED | IV, SS (the final pass in the view; custody facts) |
| 4.6 | 900-964 | 5877 | `00b3ed65328eb21773f171bf89852ac17c227e4c242c254aa4e2bc5c739eb234` | CARRIED | — |
| 5 | 965-966 | 137 | `46adbb0dd725d4f1ca5f142a684061fafc17e2c5165b6da45647a41585de9bab` | CARRIED | — |
| 5.1 | 967-994 | 2284 | `e0bc923e20b24b36609ff4d44f5a354e999dcd57c67793c398d1890d68c14b97` | CARRIED | — |
| 5.2 | 995-1027 | 4082 | `e29a8aa2813c2686ccaf07ec84b2e2e7cec6d8d97c58e077df43800fcb993666` | AMENDED | IV, CA (no exchange; unnamed inodes; `tmpdir/`) |
| 5.3 | 1028-1050 | 5424 | `f9e101d7977a6f70055027a7f8f8116477ce7d8377674c7909056d2b0a179bbf` | AMENDED | SS, PS (RL; no manager; idmaps; `nosuid`) |
| 5.4 | 1051-1057 | 478 | `debd77ac854c1a74be9913a849254ef55cff1e9f0adc2553f42431b3167eee6a` | CARRIED | — |
| 6 | 1058-1059 | 144 | `6a852dcafc48edb984b90136498474c97f6f0348b8e6541fe33b803af9034fd3` | CARRIED | — |
| 6.1 | 1060-1078 | 1485 | `dec415263fdf543ce1d47b1039e29c82cb17785eb6401b6a30d4f5a6065311e8` | AMENDED | IV (the no-ACL rule scoped to frame objects) |
| 6.2 | 1079-1095 | 1360 | `630d79f31755b6b9e03fedccb984ab0e63f7ee5f2d2d72e996bdaa7614638971` | AMENDED | IV (the ACL objects) |
| 6.3 | 1096-1136 | 4581 | `9de850056bbedc58cdd9dfcaf1203ebb3c3af71335af7cac494375afe93a4dd3` | AMENDED | IV, PS, IP (g without ACL; no GATE entries; `tmp/`, `tmpdir/`; slice, tmpfiles; images 0750) |
| 6.4 | 1137-1164 | 2736 | `1ccb9a123c91616c1b68fb74985ecf9d39b85af9c7878add3eaf434ebd4fa731` | AMENDED | PS (access through the view) |
| 6.5 | 1165-1194 | 2718 | `323fb1612e330b2fa304b3d18f325232cbaba12c150e77c700f09529578c75fb` | AMENDED | PS (the view column) |
| 7 | 1195-1196 | 113 | `8ab0b34614a172ffb23cde8314d7bef25492c58858feabd1d30e543cde17fbae` | CARRIED | — |
| 7.1 | 1197-1211 | 1950 | `1a0a5da3a2cbd9fa5a3c7e695d08ad254002b60a72a29372f78a132747a22d75` | AMENDED | PS (RL in every configuration; L's `exec` of C) |
| 7.2 | 1212-1234 | 2191 | `7faec7003ad60f3723bd527d117099d1c40615466ed7acd274903c19a54d8047` | CARRIED | — |
| 7.3 | 1235-1265 | 3069 | `698565a6689e94d4e1bf2e54f3affb07a23cc7b21ba32edcc8558434df9fa70b` | AMENDED | ER (every reference resolves in the exports) |
| 7.4 | 1266-1279 | 1131 | `66f9582ac696d0efbf60ec1e3ff0f29f7f484f24093b667798f983ee0a9a9a0d` | CARRIED | — |
| 7.5 | 1280-1295 | 2205 | `7a1a529a70e8da31c3b00decf7ae064fbd28dcb47db229103604db26ab1b9398` | AMENDED | CD (C's argv checks split between C1 and C2) |
| 7.6 | 1296-1305 | 826 | `da3dc6642e8c8b1bf407a522e929faa1997c00c2b74738d67783089debc1b34a` | CARRIED | — |
| 7.7 | 1306-1326 | 2099 | `9a35135a6ed5b397783b23a914eabe300e8d9d2caddc9281bcc9c0e6b9f34763` | AMENDED | PS (the pre-first-call residual of L, C and O) |
| 8 | 1327-1328 | 119 | `a61d10425836c77bd06805b89c361fee0f7b18967c522ffed965fe9f7f7d3d05` | AMENDED | PS (heading: the original context) |
| 8.1 | 1329-1352 | 2730 | `81091a55b4279f4cfded6b1484f9743d32c887588558e169935c2d241fec95c7` | AMENDED | PS (namespaces and maps; the stage table) |
| 8.2 | 1353-1364 | 1030 | `309b19cccb33bc3a0a2d9863e13e869de1e42a9ae055ede4b84a47ec7fde5705` | CARRIED | — |
| 8.3 | 1365-1381 | 1496 | `209bd4d33569f07b733c3d9df9bb3d3955777b2dc0584151b71adaeb3369c0cc` | AMENDED | PS (system-manager scope; no `no_new_privs` and no filter) |
| 8.4 | 1382-1421 | 3623 | `309db868a9c2204102a55fdfb86dd89b881b8610b1c3b8d097da57c0a4cf4402` | REPLACED | PS (the original context inside the view; no relocation) |
| 8.5 | 1422-1434 | 1072 | `d651794d2e2a2f64dc0256d765b1dfb3f56cb7316f27be7fa0f7cd17d386d859` | AMENDED | ER (both export trees; what a reader needs) |
| 8.6 | 1435-1456 | 2023 | `3ec9d7f237addb503a8f3a90434741ae57e7386139ae3ab5b5a06271ae25dd1f` | CARRIED | — |
| 9 | 1457-1458 | 189 | `d1843b7e7e7bee1fec119a7314ce98958f5e46327d872070510c73a6b1c90a01` | CARRIED | — |
| 9.1 | 1459-1483 | 2272 | `355f5f36ed5ec022646d45db0105f53c7c6678571befc4c3a08447a5f6a1131b` | AMENDED | PS, SS (participants; the census schema) |
| 9.2 | 1484-1502 | 1652 | `f9a758c96a803f6b57691c87999a525b6992738ca6163249e26e97640a1fb178` | AMENDED | PS (waits; the launcher wait through sudo) |
| 9.3 | 1503-1636 | 13874 | `c3913417ba30e4175c4e610f7cd2eaaf35feb44c1b1eff8d757d66d4ac6130bf` | AMENDED | CD, SS, PS (G3-G6, C1-C10) |
| 9.4 | 1637-1846 | 21279 | `0e9b21eea35401a7eec6f273ad645c90a295c8fbd511acf067f9ee0da0bf750f` | REPLACED | SS, PS (census, CRED, v5's terminal predicate; v6's release paragraphs kept, condition 2 restated) |
| 9.5 | 1847-1892 | 8815 | `b3b743406a20feaea1c43ea7f81d03590c8013087f70a18773e50edd4f73198e` | AMENDED | CA, CT, PS (failure rows) |
| 9.6 | 1893-1913 | 2037 | `6e22317b456f3cae05193dc42d34363ded46900043cf08f38e5dc9da8a8950ba` | AMENDED | CA, PS (reboot) |
| 9.7 | 1914-1958 | 4112 | `916816ae34590700a3f46c8d6500a8518866dea6f3f6b65304154eb7973db6f9` | AMENDED | PS (recovery rounds evaluate v5's predicate) |
| 9.8 | 1959-2185 | 23130 | `da771cb5aef63c3c6fc89c846406c7ea1be66588527ea01b0cae1e58b34d22be` | REPLACED | PS, RM, SS (custody by the view, N0-N8) |
| 10 | 2186-2187 | 173 | `b923c50c51930667776aced4d6d5b16a080102e4e056e61d0ade2fd420c1d98d` | CARRIED | — |
| 10.1 | 2188-2203 | 1162 | `52feefb6ac485169b1217cb73f674fae8f6477b8046e6a0db7bda861a5651a0f` | AMENDED | CA (unnamed inodes; the commit point) |
| 10.2 | 2204-2311 | 10940 | `009394f10629bde271ebe7d92d4222997af213597d1bb2013f4e5e869383bd53` | AMENDED | CA (J4, J5, consumers) |
| 10.3 | 2312-2317 | 369 | `2b275b998e8c39b306421b0c6400ea8c12528d2b9741410c51f99ac4bca59990` | CARRIED | — |
| 10.4 | 2318-2361 | 4467 | `45c96fa1f94741a0a04242424778df566daa7cd7914d7c8ff2cc04be34e7d85f` | CARRIED | — |
| 10.5 | 2362-2371 | 841 | `5178acc5917198bcbf50bc34358e123e263a72594c8410237fd622065a82f6c8` | AMENDED | CA (unsynced records) |
| 10.6 | 2372-2398 | 3116 | `651fb2122dbff804b02b66f8b498dd90ee18339fce5acdec8e3dc8d4bc3c853b` | AMENDED | CA, PS (`synced`; stream finality) |
| 10.7 | 2399-2435 | 3693 | `5233ab4519b7a801006948abc0dcb39ddb1cce959a4d5f657c6256d899e3c8ab` | AMENDED | CA, PS (the synced conjunct; L's and RL's exits) |
| 11 | 2436-2437 | 127 | `554fcbe4c216f90ff9d4ae0b8672903c7d18685221dc80a7ec07dbc59d5df8cd` | CARRIED | — |
| 11.1 | 2438-2458 | 1749 | `311a9b017bef4fd59870b92ff6126e8be5a8218c12e2181b57465c0b9befdc54` | AMENDED | PS (no mask links) |
| 11.2 | 2459-2475 | 1340 | `42fd1ec6a0f589f9b98a3bd1a451cd17cd9478f4839c5816582828d2e52fcea4` | AMENDED | PS (the manager clause withdrawn) |
| 11.3 | 2476-2525 | 7542 | `c14e0560b3f0093e6afc4567484205beda02680fc5315263c2024ff92184b2de` | AMENDED | PS (P5-P26) |
| 11.4 | 2526-2639 | 12188 | `bad8411d75995ac6e0989279d94bc8865cca2be71d29c75b20357659e929dfb2` | AMENDED | CS (effects, the global phase, vectors) |
| 11.5 | 2640-3119 | 30171 | `0418b2fbd53cc6dad1a238c986f74e7155d612aa391b765aaac84c394a12bd3a` | AMENDED | CS, PS (S-B, S-D, S-F, S-G, S-H, S-I, S-R, class table) |
| 11.6 | 3120-3133 | 1069 | `1443a7bbdcc0dd019cbc74ce2c2f44b12a8a5f2ca7bae7de45c8fed736ad6b02` | AMENDED | PS (the view baseline) |
| 11.7 | 3134-3183 | 7015 | `671db25e0bf2853da535967ce5e1c4b5f4cb7b7abfa9fe517f72910886583c73` | AMENDED | IP, IV (listable images directory; `adopt`'s exception) |
| 12 | 3184-3187 | 143 | `885b22172938418cce68053ca979e7f60082b4920c2606c4f2d0a579ee5ed5e7` | REPLACED | PS (the target view) |
| 12.1 | 3188-3208 | 1723 | `1e6066edfba180d9dff736cf3f5b95025109f49f35f34e91d986dc56739ae408` | REPLACED | PS (the design adopted) |
| 12.2 | 3209-3238 | 2785 | `c438cb6b6e750e971ceea9b6b6ba7917bdc84b762ce428bd2259e24624619c58` | REPLACED | PS (RL and the view) |
| 12.3 | 3239-3250 | 886 | `a9894889e896aa05dae51c56c4ffb3ba29a0696c094a4019ccabcefed2515247` | REPLACED | PS (what the view changes) |
| 13 | 3251-3361 | 13608 | `f15f4010d52710ae8b96c2c0c8eba527494d37496de6e93364babea11e8016cc` | REPLACED | CP, CA (probes for the view; P-PTRACE complete) |
| 13.1 | 3362-3382 | 11176 | `e5fe97d1d869a601ec9ac278cd6af8d5a3c56eaed0ffd390f6c25818b4636599` | REPLACED | CA, CS, IP (P-CHAIN, P-PROTO, P-SEAL, P-SR, P-IMAGE) |
| 14 | 3383-3395 | 1153 | `c95b67595ab8c4f051b33cb23613f43971bc60578c01f258fca0a15ba02029e1` | AMENDED | ER (v7's JACKAL records) |
| 14.1 | 3396-3403 | 552 | `74064f167fa18ca4c37b49cef1070d1902ab55bf3201fcca04aac6be3a9c59f9` | CARRIED | — |
| 14.2 | 3404-3420 | 2421 | `b08b58e84485ca9f8315121c3ba79b6e1ae4be3fef93b5aaf71d235990b6eb1f` | AMENDED | ER (A_pack; descriptions) |
| 14.3 | 3421-3443 | 2012 | `f34b228b12070739cf2c17fa4022aad1e39316668e571cb279ed6f6099d2a7d7` | AMENDED | ER (the raised Required) |
| 14.4 | 3444-3456 | 739 | `e9387e358eaffbf6a7244c1a7c9e15c237cfce7b2d5a39cd2e05a71af4860f1b` | CARRIED | — |
| 14.5 | 3457-3505 | 4519 | `e1fbf48380f58b9d3e15734a1c62a14263c05eea002debd9ad2e53adec1113b5` | AMENDED | IP, ER (J1 0750; v7 payload identity) |
| 14.6 | 3506-3511 | 280 | `0633b9be1ccd21a6c5eba0f8857b5623a5a25b5b5689318dce2ba98df525e419` | AMENDED | PS (U holds C and the target only) |
| 14.7 | 3512-3539 | 2596 | `a3b5edaed08df251ec48887ffcb14cddd6677e5db9c06ba4b79964fe394357eb` | REPLACED | ER (the payload pack and the complete accounting) |
| 15 | 3540-3541 | 139 | `c28ab08b1a6cf57c5c65775871754ab7312225c4fb76ff455a1da064d04a35d0` | CARRIED | — |
| 15.1 | 3542-3586 | 4035 | `27b9e552038b515beeec395bda4a02c7342d2dd536de4d063cfae76f1dd26715` | AMENDED | CS, PS (the rollback of v7's objects) |
| 15.2 | 3587-3594 | 581 | `a777313fcfda24aa6425bb03bdf472121ec21647b5a33958e6e3bb421ab68e81` | AMENDED | PS |
| 15.3 | 3595-3653 | 5376 | `eeae4c333baad3beeeed56e629a0d5d0f8d3ba417cececbbf1dffa6751eef8aa` | AMENDED | ER, CA (the export primitive; payload packs) |
| 15.4 | 3654-3668 | 1394 | `540ceb1e230c110537af0759ad791d4fa72d6df225ac5f9c6f2abb4c282fe6c0` | AMENDED | ER |
| 16 | 3669-3697 | 2285 | `2c11efa09b6f51fe32888dda3c2f1d14509bbe4ef5f05ff7db097c4c47b5f002` | AMENDED | PS (content lists) |
| 17 | 3698-3724 | 4551 | `fc56e39a368b270894b1754b4503f68c72302035bf9db54f112eb52b64bd1f8b` | AMENDED | PS (placements) |
| 18 | 3725-3732 | 596 | `52c11aa619e77ddcba2c87e1cb1535e34228fe5618060962d5a2a8b8cd08c391` | REPLACED | all |
| 18.1 | 3733-3797 | 7389 | `22d033d7f801ae1de8b3cac1e927a2f4ddb94666511b0646a9ed38fd359b404b` | REPLACED | all (the eleven changes) |
| 18.2 | 3798-3819 | 2771 | `52256a1a6bf87f470e2e011372c0c17b4e4f3b153ba939620784b711d15d1b89` | REPLACED | all |
| 18.3 | 3820-3836 | 1583 | `55abe6e839e00ae17d4f1c10e3a79525f08187879a2ed4c3922e77483bcaadcd` | REPLACED | all |
| 18.4 | 3837-3867 | 2535 | `5d1d7b9fa05c6c583c303e8daf72c409a0bdfcab1333638d90d4e8c9d2489d17` | REPLACED | all |
| 18.5 | 3868-3997 | 16600 | `ad877b26f73e7a2fd19017dbf1b4c2e7832e71be2370417647db4b4e5070e91a` | REPLACED | all (this map) |
| 18.6 | 3998-4018 | 1654 | `b117afa1838fd927d507d75472ebf54cee9cec6d8f432ce7d2efcb0e1244be9b` | REPLACED | all |
| 19 | 4019-4055 | 3428 | `48e1ab337ec159f404c06b4ffdb876784fcb2bfb7e0d22da703627581c372356` | AMENDED | PS |
| 20 | 4056-4085 | 2749 | `d971bca579b6d446e991a90d7ca6b028317a2297831433ad9a861982891e7ba3` | AMENDED | PS, RM |
| 21 | 4086-4171 | 13773 | `50c3411e9a4703d113c5eac4d432f8b6ba7dbaf6b3aa673c83c23ef2a1d23103` | REPLACED | CT, PS |
| Appendix A | 4172-4235 | 14868 | `1211f48a394f8dd03602066280d11ec7ee0089976919ad7028fa422a3556b9a0` | CARRIED | — |
| Appendix B | 4236-4244 | 676 | `eef7ebf9b21f869d21e2f3fe24a6052fd5fa503a50145afd3a1676bffaa30fc7` | CARRIED | — |
| B.1 | 4245-4256 | 1035 | `62ad241f9410a181967e43900aac0220861720c14c427f6aa571fbdaf8d6aefe` | AMENDED | PS (namespaces and maps) |
| B.2 | 4257-4287 | 3192 | `93a0e52fddaa4686e488accf772ebfffce7a7c1aa53495cf9d1653e821ec5317` | AMENDED | SS (the census and terminal schemas) |
| B.3 | 4288-4333 | 12686 | `93be491820a934d7ae63eab26c10ecaa31a671dcebf922590e213db87c54fa21` | AMENDED | CA, ER, IV, PS |
| B.4 | 4334-4565 | 29331 | `1d7f7aa1452fd9bc115b76508db4b80a74b27a819dd4cfda869ab89e007804e3` | AMENDED | CD, CA, PS |
| Appendix C | 4566-4625 | 4399 | `e21904702b855c69feb1afe86117e9088684c70162571459c5b906ea2b9a79c5` | CARRIED | — |
| Appendix D | 4626-4683 | 7942 | `43c155f98ef42f7aabefe4de787ddd9cd43360fd1968c19c0ccab04236de5a9f` | AMENDED | CD, PS |
| Appendix E | 4684-4747 | 5709 | `f7d449206492465183052962b4a8ea13d20a28202ac41069c31a283e1d2b06f1` | CARRIED | — |
| Appendix F | 4748-4792 | 3963 | `4b6f95f0f14f03859e6c6e08222fd51c35a0fc46365a1bf35c31d4d3fb409cc1` | CARRIED | — |
| 22, 22.1, 22.2, 22.3, 22.4 | — | — | — | NEW | PS (the architecture evaluation) |
| Appendix G | — | — | — | NEW | all (v7's JACKAL results and dated observations) |

### 18.6 New design elements in v7 that need the reviewer's attention, and the remaining premises

1. §22's evaluation of the enforcement designs and its conclusion that none is established as preserving.
2. The target view (§12.2): RL's two stages, the scope, the namespaces and their owners, the idmaps U_v, U_run and
   U_tmp, the mount table and what it does not reproduce, the Landlock ruleset, the credential drop and L's `exec` of
   C; and the inventory of what it changes (§12.3).
3. Custody by the view (§9.8 N1-N5) and the census of an absorbing kernel state (§9.4), in place of v6's scans.
4. The read-route inventory and its three OPEN routes (§9.8 N6).
5. The commit point at the close marker's link (§10.1) and the `synced: false` state.
6. The global composed state of setup and rollback (§11.4) and the class table with co-effects (§11.5).
7. The listable images directory (§11.7).
8. The payload packs and A_pack (§15.3, §14.7).
9. §21's catalogue.

Remaining premises. Installed verification is future work; each premise keeps its probe, and its failure means
redesign, with no exception. §9.8 N7 lists them: P-NS, P-IDMAP, P-LL, P-XDEV, P-PROP, P-PTRACE, P-FH, P-CG, P-NOR,
P-IOEXIT, P-NOATIME, P-NOSUID, P-LOCK, P-VIEW, P-CENSUS, and the carried ENOSPC and IMG; §22 adds TOOL-CLOSURE, the
preservation premise. v7 withdraws L1, K-PERM, PTRACE-GID, EXCH, COPY, H1-H3, S1-S6, M-PAM, BUS, ROOTS, OPT-B and
LOOKUP with the mechanisms they served.

## 19. Future execution and installed evidence (none of it exists)

- Frame v6-W1 code for every role and verb (`adopt`, `materialize`, `dispatch`, `seal-front` in both modes,
  `selftest`), frozen, with its own actual gpt-6.1-sol review: RL and the view, the excluded-leaf keys, the census and
  CRED, the state machines and keysets of Appendix B.4 (including `EARLY_REFUSAL`, the early `L_REFUSAL` and
  `CHILD_REFUSAL`, every row's `STOP` rule, the interruption points, L's `exec` of C, `SPAWN_FAILED`, the release timing
  and `RL_IDENTITY`), the commit primitive with its single commit point, close and continuation markers with §10.2's
  successor rule and chain reader, the fallback journal, exports with their payload packs, recovery, the setup-identity
  seal checks, the selftest verbs and probes, and the helpers `absent.py`, `step.py` and `check_out.py`.
- The concrete setup inventory (fixed numbers, P1-P26 outputs, script texts and digests including S-J and S-R's
  global atom table with effect sets and co-effects (§11.4), expected ACL texts and `systemctl show` outputs, the
  sudoers, sshd, slice and tmpfiles bytes, the view's mount table, maps and Landlock ruleset) and its review; JACKAL
  bounds for the subordinate-range checks and the counts of the maps' lines.
- Operator approval and execution of S-0 to S-I (and S-J if images are chosen), with S-I captures including the seal
  capture of `setup-identities.json`; S-R records if a script stops.
- Post-setup verification (§11.6); every probe of §13 and §13.1 with raw records; V-VAULT.
- The source-level readings that §9.8 N7 calls for (the installed kernel's Landlock, idmapped-mount, cgroup,
  file-handle and `io_uring` exit paths), as part of the installed evidence.
- The candidate view baseline and the writer-context baseline as reviewed installed evidence; the installed-evidence
  review, which records S; the adoption run.
- Fresh storage readings and Gate 0 receipts for every stage; measured image geometry if images are chosen.
- The evidence obligation of TOOL-CLOSURE (§22): a source-grounded review, by actual gpt-6.1-sol, of the pinned
  toolchain's use of every item of §12.3 for every allowlisted action; engineering runs in the view bound the practical
  effect and remove no item.
- Rollback execution records, whenever rollback happens.
- Independent actual gpt-6.1-sol review of all of the above, with §21's inventory. Only then can V5-B01 and V5-B02 be
  assessed against exact successor evidence.

## 20. Non-claims

- No sufficiency is claimed for V5-B01, V5-B02 or any original obligation. All stay OPEN until exact successor
  evidence meets the original required changes, with their original owners, releases and dependencies.
- v7 does not establish that the target view preserves the original success domain (§22); it lists every change it
  knows (§12.3, §21), presents none as preserving and narrows no original obligation.
- Nothing here is executed or installed evidence. Design statements, templates and probe specifications are plans.
  The passive host observations are dated and attributed (Appendices E, F and G), and they are not setup evidence.
- The account, view and gate design gives a kernel-enforced writer and generation boundary under the stated trusted
  base, preconditions and premises. It is not proof of the frame code, not lead authentication (R2), not confinement
  of the running target outside g (R3), not custody of the toolchain (R4), and no protection from root.
- Routes R-d, R-f and R-h of §9.8 N6 are frame-caused metadata updates outside T that v7 does not confine; V5-B02 stays
  OPEN for them.
- The custody arguments rest on kernel behaviour that is stated (§9.8 N7), not yet observed on this host. Until the
  probes and the installed-version readings pass they are premises; if one fails, the conclusion that rests on it is
  lost, the affected stage refuses or the classification is UNKNOWN, and W-1 must be redesigned. Nothing is weakened to
  make them pass, and no finite probe stands in for a premise.
- Integrity of the channels is not sender authentication.
- No storage capacity is established. Allowances are labelled judgments, never bounds; the arithmetic is exact
  arithmetic outside the Lean certificate chain (status `exact`, not `formal-bounded`) and is informational only.
- Images enforce write limits only. ENOSPC is never an accepted refusal and never capacity.
- Exports and lead copies are evidence records, not authentic producer custody; a vault transfer is backup.
- Fallback, raw, unconfirmed, unsynced and durability-UNKNOWN records earn no success credit; they have no release
  effect.
- No operator choice is made or recommended; no approval is requested; no new approval gate is created.
- Phase One is incomplete.

## 21. Preservation inventory: every change against the original frame [corrections: W1-V6-CATALOGUE, W1-V6-PRESERVE; v6: W1-V5-PRESERVATION]

**Baseline (S5).** The original accepted behaviour is that of frame v5 `scratch.py` (S:N): one account, `sicarii`,
for the lead, the frame and the target; the run directory `<RUNS>/<label>` with its records and snapshot, created by
`materialize` (S:977-999); the target started by v5 `spawn` (S:1508) under umask 077 (S:1992) with `RLIMIT_CORE` 0
(S:1515), in a transient scope of `sicarii`'s user manager with `MemoryMax=8G` and `MemorySwapMax=0` (S:1570-1571), in
the host's namespaces with `sicarii`'s credentials and v5's environment (S:1073-1106); the walk rules of `observe_tree`
(S:495-567) and `verify_materialization`; the admission joins, `sample()` (S:1156-1179), the memory gate
(S:1186-1248) and the window protocol (S:1253-1341); the conclusion's checks (S:1684-1691) and its read of the report
(S:1696-1708); and `owned_terminal` (S:1373-1415) as the release condition. v5's reads (the walk's file reads,
S:538-544, its directory listings and the report read) update access times under `relatime` with no suppression: the
report read and the listings belong to the baseline (correction W1-V6-CATALOGUE).

**The criterion-required repair (S6), separate from the baseline.** Frame v6's final pass (v6 `scratch.py`:554,
:569-573), in which every encountered leaf, excluded generated leaves included, keeps its complete `stat_key` through
the final walk and every directory is re-reached, and the comparison of every recorded and excluded leaf with the
admitted parent observation (§4.5 item 2) are what V5-B01 requires. Their refusals are the criterion's own (rows R1
and R2); every other row compares against S5 alone.

**Treatments.** REMOVED: v6 had it, v7 does not. OPEN: v7 keeps it; the preservation obligation stays OPEN for the
states concerned, and the row says why v7 keeps it. PREMISE: it can occur only if a premise of §9.8 N7 fails, and then
W-1 must be redesigned; it is still a new outcome, not a preserved one. No row is a preserved acceptance.

**R. The criterion's repairs**

| | Outcome | Where | Baseline | Treatment |
|---|---|---|---|---|
| R1 | the final pass refuses a leaf whose complete `stat_key` changes during the final walk, excluded leaves included | §4.5 item 1 | v5's walk checked the stability of each entry during its own observation | required by V5-B01; OPEN as V5-B01 is |
| R2 | the child stage refuses a recorded or excluded leaf that differs from the admitted parent observation | §4.5 item 2 | v5 compared directory identities only | required by V5-B01; the author argues that under §9.8's custody it fires only if a premise of N7 failed or a frame helper misbehaved, which is an argument, not an established fact |

**A. Removed in v7** (v6 mechanisms withdrawn)

| | v6 mechanism | Baseline | v7 |
|---|---|---|---|
| A1 | the copy route (fresh roots, O's descriptor-only copy, the root exchange) with every effect of it: v6 C1 (new identities, owners, groups, bits and attributes of the copies), C2 (a foreign-source access time), C3 (retired roots), C4 (the exchange's times), and v6 D3's copy-stage refusals, among them the copy's byte-read, `SEEK_DATA`/`SEEK_HOLE`, attribute-reproduction, allocation and `ENOSPC` failures, its deadline and the A_copy ceiling | the outputs are used in place | REMOVED: no target output is copied, so none of these failures exists (correction W1-V6-CATALOGUE) |
| A2 | the user manager M with its masks, drop-in, linger, `no_new_privs` and filter (v6 B4, B5), and the scans and premises S1-S6 | the scope in `sicarii`'s manager | REMOVED |
| A3 | the relocation of `HOME`, `USER`, `LOGNAME`, `XDG_RUNTIME_DIR`, `DBUS_SESSION_BUS_ADDRESS` and `TMPDIR` (v6 B2) | v5's environment | REMOVED: v5's environment (§8.4) |
| A4 | `no_new_privs` and the anti-setid filter on T (v6 B3), and v5's refusal of a set-ID leaf ((c4)) | a set-ID leaf is accepted; the mode of a recorded file is recorded, and an excluded partition leaf's mode is not recorded at all, only its `stat_key` compared within the walk (S:495-505) | REMOVED. v6's "accepted, the mode recorded" was inexact for excluded leaves and is corrected here (correction W1-V6-CATALOGUE) |
| A5 | pre-created W-owned partition roots (v6 B8, premise ROOTS) | the target creates them (S:1033) | REMOVED: the target creates them, as in v5 |
| A6 | Option A's traverse ACL on `/home/sicarii` (v6 B6, C7's home entry) | — | REMOVED |
| A7 | the walks as R with GATE (v6 D2) | the walk runs as the owner of the run tree | REMOVED: C and O read as the owners of every entry below `source/` through the run-path idmap (§6.4) |
| A8 | the expanded release condition (v6 D5: global uid, manager and lease conditions) and the stream lease test (v6 D6) | `owned_terminal` | REMOVED: release is v5's predicate (§9.4); stream finality is U's `populated 0` (§10.6) |
| A9 | v6's in-place predicate, its child-stage re-checks and SCAN-GATE/SCAN-W refusals (v6 D1, D7's in-place part) | not checked | REMOVED; the census replaces them (D1 below) |
| A10 | v5's write revocation and W-CLOSED (v6 A1-A6) | — | stay removed |

**B. Restrictions on what a target may do** (each is a row of §12.3; treatment OPEN until TOOL-CLOSURE, §22)

| | Restriction | Why v7 keeps it |
|---|---|---|
| B1 | V1: no host network | abstract UNIX sockets have no permission check and are reachable from every process of a network namespace (N1) |
| B2 | V2: outward UNIX connections only to servers of the target's domain; socket files only in the private binds | a connection to, or from, an outside process is a descriptor channel (N1) |
| B3 | V3: no mount, unmount, bind or `pivot_root` | a new mount could give an admitted entry a name outside g or reveal a mask (N3) |
| B4 | V4: set-ID programs and file capabilities confer nothing | the root view shows on-disk root as root, so a set-user-ID root program would otherwise run with host euid 0 (§12.2) |
| B5 | V5: host identity R and GATE, with its effects on foreign objects, signals, tracing and per-user accounting | a target with `sicarii`'s host uid is reachable by every `sicarii` process's pull routes: the K0 obstruction (§22) |
| B6 | V6: FUSE and network mounts, `binfmt_misc`, other users' runtime directories and later host mounts not in the view | RL must not touch a possibly hung FUSE server; these filesystems are not idmapped; private propagation (N3) |
| B7 | V7: private `/tmp` and `TMPDIR` (with images, `noexec`) | the target's socket files and temporaries must lie where no outside principal can reach them (N1, N3) |
| B8 | V8: the frame's records and snapshot are not in the run directory; `source/` is a mount root | V5-B02's protected writer and location boundary; the recipe below `source/` stays the target's, and a change to it is detected by v5's conclusion, as in v5 |
| B9 | V9: the W-1 trees are masked | the protected tree is not part of the target's world |
| B10 | V10: the scope is the system manager's | only root can create a scope under `wlscratch.slice`, which the census relies on (§9.4) |
| B11 | V12: the Landlock domain | B2 and B3 |

**C. Changes to what a later target, the lead or another process observes**

| | Change | Where | Baseline | Treatment |
|---|---|---|---|---|
| C1 | the generation, its records and the attempt records lie in the protected tree, which the lead cannot search; the lead reads exports, which carry the payload packs | §3.3, §6.3, §15.3 | the run tree and records were `sicarii`'s and readable in place | kept from v4, OPEN |
| C2 | the frame's reads below `source/` no longer change access times (`O_NOATIME`); v5's walk, listings and report read did | §9.8 N6 | access times updated under `relatime` | NEW in v7 (W1-V6-READ-MUTATION), OPEN |
| C3 | the target's processes appear to other host processes with uid R and gid GATE | §12.3 V5 | uid 1000 | OPEN (B5) |
| C4 | setup changes to existing objects: the sudoers and sshd drop-ins, the slice unit, the tmpfiles rule, with images the mount units | §11.5 | — | kept (operator setup), OPEN |
| C5 | added time before launch: RL's two stages, the view's construction, the census | §12.2, §9.4 | — | NEW, OPEN; no time is added at release beyond v5's predicate |
| C6 | `materialize` refuses a label that an existing generation of T carries, not one whose `<RUNS>/<label>` exists (the lead creates that directory for the view) | §3.3 | v5 refused when the run directory existed (S:984-986) | changed in both directions, OPEN |
| C7 | the target's scope is listed by the system manager, not by `sicarii`'s | §12.3 V10 | `sicarii`'s manager | OPEN (B10) |

**D. Non-success outcomes in states that the baseline accepts**

| | Outcome | Where | Baseline | Treatment |
|---|---|---|---|---|
| D1 | census and CRED refusals before launch (an earlier scope not `populated 0`, an unexpected process in U or in the observer scope, an R or GATE process outside `wlscratch.slice`) | §9.4, §9.3 C7 and C10 | v5's `sample` refused while an earlier frame scope was active | OPEN: whether every such state is one that v5 also refused is premise P-CENSUS; a CRED failure is PREMISE (P-NOR) |
| D2 | RL refusals: the lead-created run-path mount point is missing (V11), a view step fails, a seal or invoker check fails | §12.2, §3.3 | no such step | NEW, OPEN; the missing-mount-point refusal is a refusal of an accepted case unless review rules the lead's preparation part of the protocol, as v5's lead-created inbox was |
| D3 | an original observation taken in the view differs from its baseline: v5's `retain_observation` refuses | §8.4 | the observation is taken in the lead's context | PREMISE (P-VIEW) |
| D4 | Gate 0: W-1's allowances, A_pack included, enter every stage's receipt, so a stage may be DEFERRED where the baseline would proceed | §14.2, §14.3, §14.7 | `sample()`'s free-space check above the reserve (S:1156-1179) | a capacity deferral, kept: it places no size limit on any accepted case, the stage proceeds whenever a fresh reading satisfies the rule, and deferral without established capacity is what the original storage ruling requires (§1). It is not a new cap, not a release gate and not a refusal of an accepted case (correction W1-V6-CATALOGUE); OPEN only as safe-fresh-capacity is |
| D5 | deadline effects: W-1's control deadlines (60 s for an acknowledgement, `GO` or `SPAWN_OK`; 600 s for a front stage-observation set, §7.4) and the 10 s retry and round intervals (§9.7) are new; before launch an expired deadline refuses an attempt that v5 would have run when a frame process is slow (load, a stalled filesystem); after launch it is recorded and stops no wait | §7.4, §9.7 | v5's own deadlines (300 s, 30 s, 30 s), unchanged | NEW, OPEN (correction W1-V6-CATALOGUE) |
| D6 | W-1 machinery: the lease held, a channel failure, a first-act failure, an RL identity failure, record durability (`fallback`, `raw`, `unknown`, unsynced), a branched journal, an export failure, a run that needed recovery (F exits 1) | §9.5, §10, §10.7 | none of this machinery exists | NEW, OPEN. The author knows of no target state that causes one of them, but that is not established: for example a target that loads the host heavily can slow a frame process into a deadline (correction W1-V6-CATALOGUE: no causal absolute) |

**E. Baseline behaviour that W-1 keeps (not a change).** Umask 077 (S:1992), `RLIMIT_CORE` 0 (S:1515),
`MemoryMax=8G` and `MemorySwapMax=0` (S:1570-1571; in another manager, C7), the allowlist (`command()`,
S:1054-1070), v5's environment and run path (§8.4), `sample()`'s sibling-unit, heavy-process, storage-reserve and
meminfo checks (S:1156-1179; the sibling check in `sicarii`'s manager by F, with no unit allowed), the memory gate
and its receipts (S:1186-1248), the window protocol (S:1253-1341), the walk rules (S:495-567) with v5's readability
rule, the within-attempt identity seals and the conclusion's checks and report read (S:1684-1708; the reads with
`O_NOATIME`, C2), and `owned_terminal` (S:1373-1415) as the release condition, with stream finality and success
following it.

**What bounds the OPEN rows, and what would discharge them.** Rows B1-B11, C3 and C7 change the target's world;
TOOL-CLOSURE (§22) would show that no allowlisted action observes them, which would discharge them for the original
accepted cases; engineering runs bound their practical effect and discharge nothing. Rows C1, C2, C4, C5, C6 and
D1-D6 are frame-side; P-CENSUS would discharge D1, a ruling on the lead's preparation step D2, and P-VIEW D3; D4 is
the original storage ruling's own deferral; for C2, C5, D5 and D6 the author knows no frame design without some such
outcome, and they stay OPEN with that reason. Until then every OPEN row stays OPEN, and with them W1-V5-PRESERVATION,
V5-B01 and V5-B02 (§0.4). No row is an accepted exception, and none narrows an original obligation.

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

### 22.3 Candidates

**(a) Option B, extended: a root-owned reviewed launcher and private namespaces** (the lead's candidate). Evaluated
namespace by namespace, against the original success domain as read from S5 and S6 (§21) and the allowlisted actions
(`command()`, S:1054-1070: `gnatprove` and `gprbuild` on the pinned toolchain):
- *Mount namespace* (owned by the initial user namespace, mounts private): needed, to show `g/source`, `g/tmp` and
  `g/tmpdir` at the original paths and to mask the W-1 trees. With an idmapped clone of the root filesystem the
  target sees the original paths, owners and modes (§8.4). Changes: V6-V9.
- *User namespace* (root-owned; 1000 ↔ R and 1000 ↔ GATE): needed for fidelity (the target is uid and gid 1000 inside,
  with the lead's groups, and owns what `sicarii` owns) and as the idmaps' basis; it adds no capability for anyone
  but root, because root owns it. Changes: part of V5.
- *Network namespace*: needed for custody, because abstract UNIX sockets have no permission check and are scoped only
  by the network namespace; Landlock's abstract-socket scope restricts only outward connections. Change: V1.
- *PID namespace*: the candidate's "when the pid namespace's init exits, every holder is gone" is the event (2)
  requires. A cgroup's `populated 0` gives the same event, observable from outside, without changing what the target
  sees in `/proc` or its pids; `kill`, ptrace and the `/proc` pull routes are already closed by the distinct host uid
  (N2). v7 therefore uses the scope, not a pid namespace: the same custody with fewer changes. A pid namespace would
  add the change "the target sees only its own processes".
- *IPC namespace*: System V IPC and POSIX message queues carry no descriptor, so a private IPC namespace adds no
  custody; v7 keeps the host's.
- *Outputs admitted in place, unchanged, with no copy route and no `chmod`*: yes (§4.1, §4.5).
- *Holders*: no principal outside the target's tree can obtain or keep a writable description or reference
  (§9.8 N1-N4), under premises N7.
Conclusion (a): with the refinements above and with (b)'s Landlock it establishes the custody facts of §9.8 under
premises N7, and it removes the copy route, the user manager, the relocation, the release expansion and v6's other
mechanisms (§21 A). **It does not keep the original success domain fixed as established**: V1-V12 (§12.3) are
observable changes of the target's world, and they leave every allowlisted action's observable behaviour unchanged
only if TOOL-CLOSURE (§22.4) holds.

**(b) Kernel-enforced scoping available unprivileged on this kernel** (7.2.6; LSMs `capability,yama,landlock`;
`CONFIG_BPF_LSM` not set; Appendix G).
- *Landlock* (the installed `linux-api-headers` 7.2-1 describe rights up to ABI 10; `RESOLVE_UNIX` exists since ABI
  9). It can enforce, for a sandboxed process: filesystem access rights, among them `RESOLVE_UNIX` (no `connect`, and
  no `sendmsg` with an address, to a pathname UNIX server created outside the domain) and `MAKE_SOCK` (where socket
  files may be created); the scopes `ABSTRACT_UNIX_SOCKET` and `SIGNAL`
  (outward connections to abstract sockets and signals to processes outside the domain); a prohibition of
  filesystem-topology changes; ptrace only within the domain. It cannot enforce anything on processes outside the
  domain: an unsandboxed process can still connect to an abstract socket the target binds, connect to a socket file
  the target creates where it can reach it, read the target's `/proc/<pid>/fd` when it has the target's uid and the
  target is dumpable, call `pidfd_getfd` where ptrace attach is permitted, or decode a file handle where the kernel
  allows it. What it would refuse: the target's outward connections and its socket files outside the granted places
  (`EACCES`), its mounts (`EPERM`), and with the scopes its outward abstract connections and signals.
- *seccomp argument filters*: a classic filter sees only register arguments, not the memory they point to (a
  `sockaddr`, a path, a `msghdr` with `SCM_RIGHTS`), so it can deny a system call family entirely but cannot express
  "no descriptor to an outside process"; unprivileged use needs `no_new_privs`; it never constrains another process.
  What it would refuse: whole families (`sendmsg`, `socket(AF_UNIX)`, `io_uring`, `mount`, `ptrace`), each a broad
  change of the target's behaviour. User-notification supervision (`SECCOMP_RET_USER_NOTIF`) reads the target's memory
  after the target supplied it, which the target can change before the kernel acts: unsound as a security policy.
- *`SCM_RIGHTS` and `pidfd_getfd` exposure*: `SCM_RIGHTS` needs a connected or addressed AF_UNIX socket; `pidfd_getfd`
  needs ptrace-attach access. For a target that keeps `sicarii`'s uid, every `sicarii` process passes the uid half of
  those checks, and the target controls its own dumpability, so the pull routes stay open to A1 whatever Landlock and
  seccomp do.
Conclusion (b): unprivileged scoping alone does not establish custody for a same-uid target, which is K0's own
architecture, and what it can enforce it enforces by refusing target operations (V2, V3 and more). Inside (a), where
the target has another host uid, Landlock closes the routes that DAC leaves (outward connections to `sicarii`'s
servers, socket files in shared places, new mounts), which is why v7 uses it there; it does not preserve.

**(c) Other routes considered.**
- *(c1) A distinct uid without namespaces* (v4-v6): the target can still connect to world-accessible or abstract
  servers and receive connections in shared places, so custody of already-shared descriptions needs v6's copy route
  or lease test. Not preserving (v6's own result).
- *(c2) BPF LSM*: not built (`CONFIG_BPF_LSM` not set); unavailable.
- *(c3) fanotify permission events*: they mediate opens and accesses, not descriptor passing or naming, and need
  privilege for the useful modes. They do not close N1-N3.
- *(c4) A separate kernel (a micro-VM or nested VM)*: strongest isolation, but it changes paths (shared filesystems),
  identities, devices, timing and the toolchain's environment wholesale, and the host is itself a VM whose nested
  virtualization is unknown. Not preserving.
- *(c5) Snapshot or reflink admission copies, overlay filesystems*: they substitute inodes and attributes, as v6's
  copy did (W1-V6-PRESERVE). Not preserving.
- *(c6) Revocation*: Linux has no general `revoke()`; changing modes changes observable state (v5's withdrawn route).
- *(c7) Leases and locks*: they detect writable descriptions but not readers or names, and revoke nothing (v6's
  withdrawn route).
- *(c8) A launcher that keeps `sicarii`'s host uid but runs the target inside a root-owned user namespace*: other
  `sicarii` processes keep the uid half of every pull check, and the target's dumpability is its own: the K0
  obstruction stands.
K0 leaves room for designs it does not cover; the author found one that establishes custody without copying or
changing outputs, (a) with (b), and none that does so without changing the target's world.

### 22.4 Conclusion, and the premise that would discharge it

**No candidate evaluated preserves the original success domain as established.** v7 adopts (a) with (b)'s Landlock,
because it alone of the candidates removes every observable substitution of an output, every cap and every expanded
gate of v6, while establishing the custody facts under named premises. It keeps the changes of §12.3, which are
changes of the target's environment, not of its outputs; whether any of them can change an allowlisted action's
observable result is the premise:

- **TOOL-CLOSURE** (NAMED_UNESTABLISHED): for each allowlisted action (the five forms of v5 `command()`) on the pinned
  toolchain (`gnat` 16.1.0-1, `gprbuild` 26.0.0-1, `gnatprove` 16.1.0-1 and every prover and helper they start), the
  observable outcome (exit status, streams, report, partition contents, apart from timing) does not depend on any
  item of §12.3: no network use; no UNIX connection to a server outside the target's own process tree, and every socket
  file it creates lies in the run path, `/tmp` or `TMPDIR` (the pinned `gnatprove` names `why3server`, a `--socket`
  option, `GNATPROVE_SOCKET` and a socket-directory computation, observed as strings on 2026-10-05, Appendix G; where
  that directory lies, and that the server is started by the target itself, are part of this premise's review); no
  mount; no set-ID program; no use of foreign-owned objects on the non-idmapped mounts; no FUSE or network mount; no
  file of another process in `/tmp` or `TMPDIR`; no entry of the run directory other than `source/`; no W-1 tree; no
  dependence on the scope's manager defaults or on the Landlock domain itself. **Evidence obligation:** a
  source-grounded review, by actual gpt-6.1-sol, of the pinned toolchain's use of each item for each action, recorded
  with the
  installed evidence; engineering runs in the view bound the practical effect and never establish the premise.

Until TOOL-CLOSURE and the premises of §9.8 N7 are established and reviewed, V5-B01, V5-B02 and W1-V5-PRESERVATION
stay OPEN and are not narrowed. If TOOL-CLOSURE fails for some item, that item is an accepted-case change, and W-1
must be redesigned for it; no exception is taken.

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

### B.1 Role identity: `wlscratch-role-identity-v1`

`role` ∈ {`front`, `writer`, `seal-front`, `launcher`, `child`, `observer`, `root-launcher`}; `pid`, `ppid`,
`start_time_ticks` (int); `comm` (str); `argv` (list of str); `exe` `{path, dev, ino, sha256}`; `uids`, `gids` (4 ints:
real, effective, saved, fs); `groups` (list of int); `caps` `{inh, prm, eff, bnd, amb}` (hex str); `no_new_privs`,
`seccomp` (int); `dumpable` `{set_result, pr_get_dumpable, proc_self_fd_uid}` (int); `umask` (int); `rlimits`
`{core, nofile, nproc}` (pairs of int); `cgroup` (str); `namespaces` `{mnt, pid, user, net, cgroup}` (int inode); `maps`
`{uid_map, gid_map, setgroups}` (str, as read from `/proc/self`; for processes outside a view the initial
namespace's); `cwd` `{dev, ino}`; `stdio` (list of `{fd, type, dev, ino, mode, flags}`, `type` ∈ {`fifo`, `socket`,
`regular`, `char`, `dir`, `other`}); `open_fds` (list of int); `environment` `{names, sha256, values}` (values only for
the clear keys of §8.1); `python` `{version, executable, prefix, base_prefix, flags, path}`; `modules` `{files: [{name,
path, bytes, sha256}], builtins: [str]}`; `frame_inventory` `{sha256, bytes}`. Inside a view, `uids`, `gids` and
`groups` are the values the view's user namespace shows; the parent role's join maps them through `maps` (§8.1).

### B.2 Participants, waits, scopes, census [corrections: W1-V6-SCAN-STATE; v6: W1-V5-REVOCATION-CONFINEMENT; v5: W1-CUSTODY-CLOSURE]

- `wlscratch-participant-v1`: `role` ∈ {`S1`, `W`, `S2`, `RL`, `L`, `C`, `T`, `S_O`, `O`, `S3`, `W2`} (RL, L and C of
  one launch, and RL and O of one observer, share a pid; each role is recorded with the start time it had); `pid`,
  `start_time_ticks`, `ppid` (int); `uids`, `gids` (4 ints, as the initial namespace shows them); `groups`; `cmdline`
  (list of str); `cgroup` (str); `observed_by` (role); `state` ∈ {`alive`, `absent`, `reused`, `unknown`}.
- `wlscratch-wait-v1`: `waiter_role`, `waited_role`; `pid`, `start_time_ticks` (int); `raw_status` (int or null);
  `exited`, `signaled`, `core_dumped` (bool); `exit_code`, `signal` (int or null); `wait_error` (object or null);
  `interrupts` (list); `unresolved` (bool); `meaning` (str).
- `wlscratch-scope-v2`: `manager` (str: `system`); `unit` (str); `invocation_id` (str); `control_group` (str);
  `properties_at_start`, `properties_at_end` (objects with `LoadState`, `ActiveState`, `SubState`, `Result`,
  `ControlGroup`, `MemoryMax`, `MemorySwapMax`); `populated` (int or null); `cgroup_state` ∈ {`ABSENT`, `EMPTY`,
  `NONEMPTY`, `UNAVAILABLE`}.
- `wlscratch-census-v1`: `point` ∈ {`parent`, `child`, `final`, `after`, `recovery`}; `round` (int or null);
  `observer` (participant); `slice` (list of `{cgroup, populated, procs: [participant]}` for every child cgroup of
  `wlscratch.slice`); `expected` (list of `{cgroup, procs: [participant]}`, §9.4's table); `cred` `{checked, outside:
  [participant]}` (CRED); `unknown` (list of reasons); `verdict` ∈ {`pass`, `refuse`, `unknown`}.
- `wlscratch-terminal-v1` (v5's `owned_terminal` observation, §9.4): `unit`, `properties`, `cgroup` (as v5),
  `launched`, `launcher_pid`, `participant_pids_absent` (pid → bool), `processes_naming_attempt`,
  `unresolved_participant_records`, `terminal` (bool), `verdict` ∈ {`known-terminal`, `live`, `unknown`} (at the after
  and recovery points).

### B.3 Records [corrections: W1-V6-COMMIT-AMBIGUITY, W1-V6-EVIDENCE-RESTORE, W1-V6-INVARIANTS; v6: W1-V5-REVOCATION-CONFINEMENT; v5: W1-PROTOCOL-FAILURE-STATES, W1-JOURNAL-CONTINUATION, W1-SETUP-IDENTITY, W1-CUSTODY-CLOSURE]

| Record | Schema name | Keys beyond the common fields |
|---|---|---|
| `generation.json` | `wlscratch-generation-v2` | `created_at`, `writer` (B.1), `invocation` `{argv, sudo_user, sudo_uid, sudo_command, n_f}`, `front_triple` `{pid, start_time_ticks, boot_id}`, `lease` `{lease_dir: [dev, ino], lock: [dev, ino], uid, gid, mode}`, `location_chain` (list of `{name, dev, ino, uid, gid, mode, acl_sha256}` from `/` to g), `record_chain` (the same from `/` to g_rec), `mounts` (the §3.4 mount facts; empty without images), `installed_frame` `{inventory_sha256, inventory_bytes, install_root, source_frame}`, `setup_identities` `{sha256, bytes, dev, ino}` (v4's `setup_identities_sha256` is its `sha256`), `setup_seal` (str: `adopted`, `unadopted`; §11.7), `channel` `{protocol, n_f, n_w, genesis}`, `verb`, `run_label`, `attempt0` |
| `inputs/<seq>-<name>` and its `.json` header (P_adm; P_att for `dispatch`) | `wlscratch-input-v1` (header) | raw bytes file; header `{seq, name, class ∈ {pinned, joined, observation}, size, mode, sha256, pin_source, verdict, atime_route ∈ {noatime, foreign}}` (§8.6, §9.8 N6) |
| `inputs/manifest.json` | `wlscratch-inputs-manifest-v1` | `entries` (list of `{seq, name, class, size, mode, sha256, written_to}`), `heads_after_inputs` |
| `materialization.json` | `wlscratch-materialization-v2` | every v5 `claude-scratch-materialization-v5` key (with `run` = g's path), plus `generation_pin` `{record, marker}`, `inputs_manifest_pin`, `tmp_dir` `{path, dev, ino, mode}`, `tmpdir_dir` `{path, dev, ino}`, `run_path` (str), `recipe_mode_property` `{files_others_readable, dirs_others_searchable}`, `channel_heads` |
| `attempt.json`, kind `materialize` | `wlscratch-attempt-materialize-v1` | `kind` = `materialize`, `created_at`, `writer` (B.1), `invocation`, `front_triple`, `generation_pins` exactly `{generation, generation_marker}`, `lease`, `channel`, `verb`, `args` `{label, overlay_dir}` |
| `attempt.json`, kind `dispatch` | `wlscratch-attempt-dispatch-v1` | `kind` = `dispatch`, `created_at`, `writer` (B.1), `invocation`, `front_triple`, `generation_pins` exactly `{generation, generation_marker, materialization, materialization_marker}`, `adoption` `{record, marker}`, `lease`, `channel`, `verb`, `args` `{action, args, inbox}` |
| `fallback-allocation.json` | `wlscratch-fallback-allocation-v1` | `path`, `dev`, `ino`, `uid`, `gid`, `mode`, `bytes`, `slot_bytes`, `slots`, `st_blocks`, `created_at` |
| `front/front-identity.json`, `front/front-stage-<stage>.json` | `wlscratch-front-stage-v1` | `stage`, `front` (B.1 at stage), `lead_observation`, `frame_admission_front` `{inventory, review, installed_review, adoption, rollout, adoption_observation}`, `base_tree_observation`, `runtime_observation` (compact or full, v5 item 4), `manager_environment`, `sibling_units`, `storage_reading`, `window_ownership` (child stage), `vault` (where run) |
| `observer-intent-<n>.json` (also under `w2-<k>/`) | `wlscratch-observer-intent-v3` | `n`, `stage` ∈ {`parent`, `after`, `recover`}, `observer_argv`, `rl_argv`, `n_o`, `view_spec_sha256`, `streams` (list of `{name, dev, ino}`) |
| `observer-<n>-<stage>.json` (also under `w2-<k>/`) | `wlscratch-observation-v4` | `n`, `stage` ∈ {`parent`, `after`, `recover`}, `observer` (B.1), `census` (`wlscratch-census-v1`), `walk` (with every excluded leaf's `stat_key` and every entry's mount ID), `identities` (v5, taken in the view), `sample_half`, `terminal` (`wlscratch-terminal-v1`; stages `after` and `recover`, else null), `report` (descriptor or null) |
| `launcher-rl-identity.json`, `observer-<n>-rl-identity.json` (the latter also under `w2-<k>/`) | `wlscratch-rl-identity-v2` | `frame_sha256` (hex64), `channel` (str: `W-L` or `W-O`), and the `RL_IDENTITY` body (B.4.3): `root_launcher` (B.1 at its `exec`), `view_spec_sha256`, `scope` (B.2), `census` (B.2), `namespaces`, `maps` `{view, run, tmp}`, `mountinfo`, `unreproduced_mounts`, `landlock` `{abi, handled, rules}` |
| `launch.json` | v5 keys plus | `generation_pin`, `attempt_pin`, `parent_observation_pin` (the admitted parent observation of §4.2 D11: O's full walk incl. excluded-leaf keys), `view_spec` (§12.2: groups G_V, the mount table, the maps, the Landlock ruleset, U) and `view_spec_sha256`, `rl_argv_template`, `launcher_argv_template`, `child_argv_template` (C), `streams` (names), `front_stage_pins`; v5 `environment` holds v5's environment (§8.4); v5 `adoption` is the descriptor of `lead-adoption.json` |
| `reservation-intent.json`, `reservation.json` | v5 keys plus | `window_lock_identity` `{dev, ino, nlink}` observed by F under the lock, `request_digest` |
| `admission.json` | v5 keys plus | `gate0_receipt_pin`, `front_stage_pins`, `observer_parent_pin` (the pin of the admitted parent observation, §4.2 D11), `writer_half_pins` |
| `launcher-intent.json` | v5 `scope_argv` (RL's `systemd-run` argv) plus | `rl_argv`, `launcher_argv`, `child_argv`, `seals` `{launch_sha256, admission_sha256}`, `view_spec_sha256`, `n_wl`, `n_c`, `streams` (list of `{name, dev, ino}`, exactly the stream names of D14), `journal_head` |
| `launcher-start.json`, `launcher-wait.json` (the relayed status of the RL/L/C pid), `sudo-launcher-wait.json`, `observer-wait-<n>.json` | B.2 participant or wait | — |
| `child-wrapper.json`, `child-stage-child.json`, `child-admission-summary.json`, `effective-limits.json`, `child-start.json`, `child-wait.json`, `child-refusal.json`, `child-cleanup.json` | v5 keys (`child-stage-child.json`: C's observations of the child stage, census included; `child-admission-summary.json`: the digests of every C1-C7 result) | sent by C over SP_C and committed by W; plus `channel` `{c2w_head}`; `child-refusal.json` keeps v5's `target_started: false` and its meaning, and is sent only before C's spawn call; `child-wait.json` keeps v5's keys and is sent after `CHILD_START` (`CHILD_WAIT`) or as the only outcome of a failed spawn call that left no child (`SPAWN_FAILED`, `started: false`) |
| `writer-half-parent.json`, `writer-half-child.json` | `wlscratch-writer-half-v3` | `stage`, `snapshot_observation`, `attempt_identity`, `journal_join` (§10.6 result), `lease` (held, identity), `location_chains`, `cred` (B.2 `cred`) |
| `spawn-ok.json` | `wlscratch-spawn-ok-v1` | `c_identity_pin`, `admission_summary_sha256`, `front_pong_at`, `writer_errors` (must be empty) |
| `stream-finality.json` | `wlscratch-stream-finality-v2` | `streams` (list of `{name, dev, ino, sha256, bytes, stat_key}`), `census_pin` (U absent or `populated 0`), `final` (bool) |
| `result.json` | v5 `claude-scratch-run-result-v5` keys plus | `record_states` (name → `{state: primary/retry/fallback/raw/unknown, synced}`), `durability` ∈ {`complete`, `UNKNOWN`}, `terminal` (`wlscratch-terminal-v1`), `target_started` ∈ {`true`, `false`, `unknown`} (str), `streams_final` (bool), `w1` `{generation, attempt}` |
| `release-intent.json` (W) or `w2-<k>/release-intent.json` | v5 keys (`at`, `token`, `terminal`, `prior`) plus | `writer_role` ∈ {`W`, `W2`}, `classification_pin` (the after-stage or recovery terminal observation) |
| `window-release.json` (or under `w2-<k>/`) | v5 keys (`at`, `token`, `prior`, `current`, `terminal`) plus | `writer_role`, `intent_state` (the state of `release-intent.json`) |
| `release-withheld.json` (or under `w2-<k>/`) | v5 keys (`at`, `reason`, `owned_terminal`, `resolution`) plus | `writer_role`, `facts_sha256` |
| `release-not-owner.json` (or under `w2-<k>/`) | `wlscratch-release-not-owner-v1` | `token`, `window` (pin or null), `writer_role` |
| `release-failure.json` (or under `w2-<k>/`) | v5 keys (`at`, `error`, `resolution`) plus | `writer_role`, `reread` ∈ {`released`, `reserved`, `unreadable`} |
| `final-status.json` | `wlscratch-final-status-v2` | `success`, `released`, `durability`, `record_states_sha256`, `unknown_records`, `fallback_records`, `unsynced_records`, `late_errors` |
| `conclude-errors.json`, `refusal.json` | v5 keys | — |
| `w2-<k>/identity.json` | `wlscratch-w2-identity-v1` | `mode` ∈ {`seal`, `recover`}, `writer` (B.1), `capability` `{front_triple, s3: {pid, start_time_ticks}, front_parent: {pid, start_time_ticks}, verified}`, `attempt_writer_state` (participant state of the attempt's W), `lease`, `channel` |
| `w2-<k>/recovery/scan-<r>.json` | `wlscratch-recovery-round-v2` | `round` = r, `census` (B.2, point `recovery`), `terminal` (B.2) |
| `w2-<k>/recovery/result.json` | `wlscratch-recovery-result-v2` | `verdict` ∈ {`known-terminal`, `live`, `unknown`}, `rounds`, `last_round_pin`, `target_started`, `participants` (list of B.2) |
| `w2-<k>/front-terminal.json` | `wlscratch-front-terminal-v3` | `mode`, `s1_wait` (B.2), `w_final` (or null), `w_early_refusal` (the `EARLY_REFUSAL` body, or null), `w_absent`, `answers_forwarded` (list of `{n, sha256, at}`), `interrupts`, `errors`, `heads`, `durability`, `recovery` (bool), `recovery_result_pin` (or null), `release` `{performed, intent_state, record_state, intent_result_late}` |
| `commits/<seq>-<tag16>.commit` | `wlscratch-commit-v2` | `seq`, `kind` ∈ {`primary`, `retry`, `export`, `continuation`, `close`}, `record` (`{path, sha256, bytes, mode, acl_sha256}`, or null for `continuation` and `close`), `skipped` (list of `{seq, files: [{name, sha256, bytes}]}`, non-empty exactly for `continuation`) (§10.2); a marker never states its own `synced` value, which later records carry (§10.5) |
| fallback slot payload | `wlscratch-fallback-v1` | `record_name`, `stage`, `errors`, `value_sha256`, `value_bytes`, and exactly one of `value` or `value_truncated: true` |
| `export/generation/manifest.json`, `export/<A>/inc-<n>/manifest.json`, `adoption-<I>/export/inc-<n>/manifest.json` | `wlscratch-export-v3` | `increment`, `entries` (list of `{export_path, source_path, sha256, bytes, mode, acl_sha256, source_marker_sha256, state, synced}`, `state` ∈ {`committed`, `fallback`, `torn`, `raw`, `payload`}; a `payload` entry has the lead-tree or P_adm path it was read from and no marker), `directories` (list of `{path, dev, ino, mode, acl_sha256}`) |
| the matching `freeze.json` | `wlscratch-freeze-v3` | `increment`, `cut` `{journal, seq, sha256}`, `slot_range` `{from, to}` (null for the generation and adoption journals), `previous_freeze_marker`, `export_markers` (list of sha256), `manifest_sha256`, `raw_files` (list of `{path, sha256, bytes}`, §15.3), `heads` |
| `channel/<channel>-<first>-<last>.json` | `wlscratch-channel-segment-v2` | `channel`, `messages` (list of `{dir, seq, prev, kind, length, payload_sha256}` plus either `payload` or `ref`, where `ref` is `{record, offset, length, sha256}`, `{written, offset, length, sha256}` or `{source, offset, length, sha256}`, each resolving inside the exports, §7.3; `dir` includes `RL2W`) |
| `adoption-<I>/invocations/<stamp>/invocation.json` | `wlscratch-adopt-invocation-v1` | `created_at`, `writer` (B.1), `invocation`, `front_triple`, `lease`, `channel`, `installed` `{inventory_sha256, install_root, source_frame, setup_identities_sha256}` |
| `adoption-<I>/lead-adoption.json` | `wlscratch-lead-adoption-v1` (key set as v5 defines it; nothing is implemented) | every key of v5's `claude-scratch-frame-lead-adoption-v5` record (with `frame` = INSTALL_ROOT), plus `source_frame`, `setup_identities_sha256`, `setup_identities_file` `{bytes, dev, ino}` (the seal of §11.7, added in v5), `installed_review` `{review_sha256, review_freeze_sha256, review_report_sha256, reviewer_thread, rollout, turn_contexts, session_providers, exec_argv, exec_argv_record, event_stream, rollout_final_message_sha256, rollout_final_timestamp}`, `invocation_pin` |

### B.4 Channel kinds (body key sets) and the states that permit them [corrections: W1-V6-C1-DATA, W1-V6-COMMIT-AMBIGUITY; v6: W1-V5-PROTOCOL-REFUSALS, W1-V5-REVOCATION-CONFINEMENT; v5: W1-PROTOCOL-FAILURE-STATES; v4: W1-GENERATION-PROTOCOL]

**B.4.1 Conventions.** Types: `hex64` and `hex32` are lowercase hex strings of that length; `desc` is
`{path: str, sha256: hex64, bytes: int, mode: int}` (v5's `pin` shape); `pin` is `{record: desc, marker: hex64}`;
`identity` is B.1; `participant` and `wait` are B.2. Every body has exactly the listed keys. A kind marked *carrier*
has the key `bulk` (list of str) and is followed immediately by one `BEGIN`/`CHUNK`/`END` sequence per listed name, in
that order (§7.3): `BEGIN` `{name: str, size: int, mode: int, sha256: hex64, chunks: int}`, with `chunks` = 0 exactly
when `size` = 0; `CHUNK` `{index: int, data_b64: str}`; `END` `{sha256: hex64}`. A kind marked *fds* is sent in one
`sendmsg` carrying exactly the listed descriptors as `SCM_RIGHTS` ancillary data, in the listed order; other ancillary
data, or none, is a channel failure.

**B.4.2 F↔W and F↔W2 kinds** (v5 changes: `EARLY_REFUSAL` is new; `TARGET_EXITED`, `MATERIALIZED`, `EXPORTED` and
`FINAL` have changed key sets; v6 change: `FINAL`'s `vault` may be `interrupted`; v7 changes: `RECORD_COMMITTED` and
`FINAL` carry the unsynced state of §10.5).

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
| `RECORD_COMMITTED` | W→F, W2→F | `name` (str), `record` (desc), `marker` (hex64), `state` (str: `primary`, `retry`), `synced` (bool) |
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
| `CONCLUSION` | W→F | `result` (desc or null), `result_state` (str), `classification` (pin or null), `verdict` (str: `known-terminal`, `live`, `unknown`), `target_started` (str: `true`, `false`, `unknown`), `streams_final` (bool), `success_before_release` (bool) |
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
| `FINAL` | W→F, W2→F | `exit_status` (int), `success` (bool), `released` (bool or null), `durability` (str: `complete`, `UNKNOWN`), `unknown_records` (list of str), `fallback_records` (list of str), `unsynced_records` (list of str), `exports` (list of objects: `increment` int, `freeze_marker` hex64), `vault` (str or null: `ok`, `failed`, `interrupted` (a `STOP` in `materialize`'s `VAULT` before its result, B.4.4); null for a verb without a vault stage) |
| `BYE` | F→W, F→W2 | no key |

After `RELEASE_DONE`, the writer commits `window-release.json` when `reread` is `released` and `release-failure.json`
otherwise. A writer sends `RECORD_COMMITTED` only for a record that §10.2 calls committed, after the close marker that
confirms it is linked; `marker` is the digest of the record-bearing marker, and `synced` is false when that close
marker's directory `fsync` or post-link join failed (§10.1).

**B.4.3 W↔L, W↔C, W↔O and W2↔O kinds** (v5 changes: `RL_IDENTITY` and `SPAWN_FAILED` are new; `L_REFUSAL`'s stages,
`OBSERVE_REQUEST` and `OBSERVATION` have changed; v6 changes: `L_REFUSAL` and `CHILD_REFUSAL` may be the helper's first
message, B.4.4; v7 changes: `RL_IDENTITY` is sent in every configuration, with a new body; `LAUNCHER_START` precedes
L's `exec` of C; `LAUNCHER_WAIT` and v6's `ROOTS` are withdrawn; `OBSERVE_REQUEST` has changed again).

| Channel | Kind | Direction | Body keys (types) |
|---|---|---|---|
| W↔L, W↔O, W2↔O | `RL_IDENTITY` | RL→W, direction `RL2W` (§7.3) | `root_launcher` (identity, role `root-launcher`, taken immediately before its `exec`), `view_spec_sha256` (hex64), `scope` (B.2 scope), `census` (B.2 census), `namespaces` (object: `mnt`, `net`, `user`, `cgroup`, `pid`; int inodes), `maps` (object: `view`, `run`, `tmp`; each the `uid_map` and `gid_map` text), `mountinfo` (list of str: the view's lines), `unreproduced_mounts` (list of str), `landlock` (object: `abi` int, `handled` list of str, `rules` list of objects) |
| W↔L | `L_HELLO` | L→W | `nonce` (hex64), `launcher` (identity) |
| W↔L | `GO` | W→L | carrier; `echo` (hex64), `bulk` (exactly `["launch.json", "admission.json", "launcher-intent.json"]`) |
| W↔L | `FDS` | W→L | fds; `names` (exactly `["sp_c", "scope.stdout", "scope.stderr"]`) |
| W↔L | `LAUNCHER_START` | L→W | `participant` (L, about to `exec` C), `child_argv` (list of str) |
| W↔L | `L_REFUSAL` | L→W | `stage` (str: the name of the failed G4 or G6 check, `stop` or `exec`), `error` (object) |
| W↔L | `STOP` | W→L | `reason` (str) |
| W↔L | `BYE` | W→L | no key |
| W↔C | `C_HELLO` | C→W | `nonce` (hex64), `child` (identity) |
| W↔C | `RECORDS` | W→C | carrier; `echo` (hex64), `bulk` (exactly `["launch.json", "admission.json", "reservation-intent.json", "reservation.json", "launcher-intent.json", "materialization.json", "lead-adoption.json", "lead-module"]`) |
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
| `INPUTS` | `REQUEST_INPUTS` with phase `dispatch` and names `["lead-module"]`; `INPUT`; `PHASE_END`; then `PHASE_DONE` → `ADOPTION`, or `REFUSAL` in place of `PHASE_DONE` (RP0) | `REFUSAL` (RP0) | `ADOPTION` |
| `ADOPTION` | `ADOPTION_RECORD` (W→F) | `REFUSAL` (RP0) | `FRONT_PARENT` |
| `FRONT_PARENT` | `STAGE_REQUEST` with stage `front-parent`; `STAGE_RESULT`; the record message; then the next state's first message, or `REFUSAL` (RP0: F's half failed) | `REFUSAL` (RP0) | `PARENT` |
| `PARENT` | `PARTICIPANT` and record messages for the observer (W→F); then the next state's first message, or `REFUSAL` (RP0: a failed join, an original walk rule, an RL refusal, or a failing or UNKNOWN census or CRED) | `REFUSAL` (RP0) | `VAULT` |
| `VAULT` | `STAGE_REQUEST` with stage `vault`; `STAGE_RESULT`; the record message; then the next state's first message, or `REFUSAL` (RP0: v5's vault pin or status failed, J9) | `REFUSAL` (RP0) | `GATE0` |
| `GATE0` | `CHALLENGE` with kind `gate0`; `ANSWER`; the record message; or `REFUSAL` (RP0) | `REFUSAL` (RP0) | `LAUNCH_RECORD` |
| `LAUNCH_RECORD` | the record message for `launch.json`; `REFUSAL` (RP0) if it is not committed | `REFUSAL` (RP0) | `RESERVE` |
| `RESERVE` | `RESERVE_REQUEST` (W→F); then `RESERVE_ABORT` (F→W; `REFUSAL`, RP0) or `RESERVE_INTENT_REQ` (F→W); then `RESERVE_INTENT_COMMITTED` (W→F) or `RESERVE_INTENT_REFUSED` (W→F, after which F sends `RESERVE_ABORT`; RP0); then `RESERVE_DONE` (F→W: the window was written, or the write failed and the re-read shows this reservation or is unreadable) or `RESERVE_ABORT` (F→W: the write failed and the re-read shows no reservation; RP0); then `RESERVE_COMMITTED` (W→F) | F sends no `STOP` in this state: before its window write it sends `RESERVE_ABORT` with reason `stop` (`REFUSAL`, RP0); after it, F completes the state and sends `STOP` in `MEMORY_GATE` | `MEMORY_GATE` |
| `MEMORY_GATE` | per challenge, at most `MAX_CHALLENGES`: `CHALLENGE` with kind `memory`; `ANSWER`; `RECORD_COMMITTED`; on failure `REFUSAL` (RP1) | `REFUSAL` (RP1) | `ADMIT` |
| `ADMIT` | the record message for `admission.json`; `LAUNCH_INTENT_COMMITTED`; or `REFUSAL` (RP1) if either record is not committed | `REFUSAL` (RP1) | `PROCEED` |
| `PROCEED` | `PROCEED_LAUNCH` (F→W) → `RUNNING`; or `STOP` (F→W) → `REFUSAL` (RP1) | `REFUSAL` (RP1) | `RUNNING` |
| `RUNNING` | W→F: `PARTICIPANT` any number; `STAGE_REQUEST` with stage `front-child` at most once; `PING` at most once, after the front-child result; `TARGET_STARTED` at most once; `TARGET_EXITED` at most once (`started` true after `TARGET_STARTED`, false for a failed spawn call reported by `SPAWN_FAILED`, which sends no `TARGET_STARTED`); `REFUSAL` at most once (C refused before its spawn call, or the launch failed before C: RL or L refused). F→W: `STAGE_RESULT` with stage `front-child` exactly once after its request; `PONG` exactly once after `PING`; `STOP`. The state ends only when W has recorded the wait of every launch participant it started | forwarded down the channels (§9.2), and the machine continues | `AFTER` |
| `AFTER` | `STAGE_REQUEST` with stage `front-after`; `STAGE_RESULT`; `PARTICIPANT` and record messages for the observer | recorded; a `STOP` in place of `STAGE_RESULT` ends F's half without a result, which the conclusion records | `CONCLUDE` |
| `CONCLUDE` | `CONCLUSION` (W→F) | recorded | `RELEASE` |
| `RELEASE` | F→W, exactly one of: (i) `RELEASE_INTENT_REQ`, later `RELEASE_DONE`; (ii) `RELEASE_WITHHELD`; (iii) `RELEASE_NOT_OWNER`. W→F: in (i), `RELEASE_INTENT_RESULT` exactly once, in answer to `RELEASE_INTENT_REQ`, then `RELEASE_RECORD_RESULT` exactly once, in answer to `RELEASE_DONE`; in (ii) and (iii), `RELEASE_RECORD_RESULT` exactly once. The two directions interleave freely: F sends `RELEASE_DONE` after its window write whether or not `RELEASE_INTENT_RESULT` has arrived, having waited for it at most the control deadline (§9.4), and a `RELEASE_INTENT_RESULT` that arrives after that is legal, recorded and changes nothing. The state ends when F has read `RELEASE_RECORD_RESULT` | recorded; F's release follows §9.4 only | `EXPORT` |
| `EXPORT` | the record message for `final-status.json`; `EXPORTED` | recorded | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | recorded | `DONE` |

F↔W2, verb `seal-front` (W2 never refuses because of a `STOP`):

| State | Messages, in order | On `STOP` (F→W2) | Next |
|---|---|---|---|
| `START` | `W2_HELLO` (W2→F) → `HELLO`; or `EARLY_REFUSAL` (W2→F: lease held, capability or seal failure; nothing written) → `DONE` | — | `HELLO` |
| `HELLO` | `HELLO_ACK` (F→W2); then the next state's first message (mode `seal`: `STAGE_REQUEST` of `FRONT_TERMINAL`; mode `recover`: `RECOVERY_SCAN` or `RECOVERY_RESULT` of `RECOVER`), or `REFUSAL` (W2→F: F's identity fails the joins) → `EXPORT` | recorded | `FRONT_TERMINAL` in mode `seal`; `RECOVER` in mode `recover` |
| `RECOVER` | `RECOVERY_SCAN` any number (W2→F); `STOP` (F→W2) ends the rounds; `RECOVERY_RESULT` exactly once (W2→F), after W2's observer has ended | ends the rounds: `RECOVERY_RESULT` carries the last verdict | `RELEASE` |
| `RELEASE` | as in `dispatch`, with W2 as the writer; F re-reads the window under the lock first and sends `RELEASE_NOT_OWNER` if this attempt does not hold it, which includes the case in which F already released it earlier in the attempt (F's terminal record then states `release.performed: true`) | recorded | `FRONT_TERMINAL` |
| `FRONT_TERMINAL` | `STAGE_REQUEST` with stage `front-terminal` (W2→F); `STAGE_RESULT` carrying `front-terminal.json` (F→W2); `RECORD_COMMITTED`, `RECORD_FALLBACK` or `RECORD_UNKNOWN` (W2→F) | recorded | `EXPORT` |
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
| `RECORDS` | `RECORDS` and `STREAMS` (W→C) → `ADMIT`; or `CHILD_REFUSAL` (C→W, after `RECORDS`: a C2 check failed) → `REFUSED` | in place of `RECORDS` (W's verification of C failed, C2) or after it: C refuses (`CHILD_REFUSAL` → `REFUSED`) | `ADMIT` |
| `ADMIT` | C→W: `CHILD_RECORD` any number, `CHILD_STAGE_REQUEST` once; W→C: `CHILD_STAGE_RESULT` once after it; then C→W `SPAWN_REQUEST` → `SPAWN`, or `CHILD_REFUSAL` → `REFUSED` | C refuses (`CHILD_REFUSAL` → `REFUSED`) | `SPAWN` |
| `SPAWN` | W→C: `SPAWN_OK`, or `STOP` instead. After `SPAWN_OK`, exactly one C→W outcome: `CHILD_REFUSAL` (C refused before its spawn call: the final pass or a later check failed, or a `STOP` was pending at its interruption point) → `REFUSED`; `CHILD_START` (the spawn call returned T) → `RUNNING`; `SPAWN_FAILED` (the spawn call failed and C has no child) → `FAILED`. A spawn call that failed while a child exists ends C's messages: W sees a channel failure (B.4.5), and `target_started` stays `unknown` | in place of `SPAWN_OK`, or pending at C's interruption point: C refuses (`CHILD_REFUSAL` → `REFUSED`); read after the spawn call: in `RUNNING` forwarded to T as `SIGTERM`, in `FAILED` recorded | `RUNNING` |
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
| F↔W at F, in `START` (EOF, a deadline or a malformed first frame before any hello or `EARLY_REFUSAL`) | W refused or failed before its hello: nothing reserved; F cannot know whether `attempt.json` is committed, so it runs no W2 and keeps W's stderr and its own facts on its console |
| F↔W at W, before F's window write | `refusal.json` and the export increment if `attempt.json` is committed; exit non-zero; nothing reserved |
| F↔W at F, before F's window write | stop reading, close the pipe ends, wait for S1; W2 in mode `seal` if F knows `attempt.json` is committed; nothing to release |
| F↔W at W, after F's window write and before `PROCEED_LAUNCH` | refuse (no S2 is started), take the after-stage classification, commit the conclusion and `release-withheld.json` ("front channel failed; release left to the front's recovery or to manual resolution"), export, exit |
| F↔W at W, from `PROCEED_LAUNCH` on | continue the run and its waits (a front EOF never implies a refusal after launch), conclude, commit `release-withheld.json` as above, export, exit |
| F↔W at F, after F's window write, including no `RELEASE_RECORD_RESULT` within the control deadline after `RELEASE_DONE` | writer-death recovery (§9.7) |
| F↔W2 at W2 | commit what it has (recovery and release records) and its export increment, exit; if no release happened, the window stays held |
| F↔W2 at F | wait for S3; if no release happened and F wrote the window, start W2 in mode `recover` again (§9.7 RC2) until the lead stops F; otherwise the window stays held |
| W↔L at L | before its interruption point: exit 125, nothing started; after `LAUNCHER_START`: it `exec`s C, or exits 125 if the `exec` fails; C's rules then apply |
| W↔L at W, including a missing or second `RL_IDENTITY` | if `GO` was not sent, W sends none (L reaches its deadline and exits 125 having started nothing) and refuses; otherwise W records the failure, whether a launch happened is decided by U's state and the classification, and if C appears, W stops it over W↔C |
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
| J5 `admission(parent)`: `frame_admitted` (inventory, review profile, adoption profile, rollout re-join, adoption observation) | F (the lead-context parts, D7) over the adoption bytes W delivers (D6); W (inventory, structural adoption joins, D3) | F `FRONT_PARENT`; W `ADOPTION` |
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
| A3 `adopt`: `rollout_join` | F (AD2, including the uniqueness of the rollout file) and W (AD5, over the streamed bytes) for both reviews | F; W `COMMIT` |
| A4 `adopt`: the fresh `scratch-adopt` observation, `check_observation`, `validate_adoption_observation` | F (AD2); W re-checks the structural profile and the time ordering (AD5) | F; W `COMMIT` |
| A5 `adopt`: the create-only record with every v5 key | W at AD5 in P_ado(I); schema renamed `wlscratch-lead-adoption-v1`, every v5 key kept | W `COMMIT` |
| A6 `frame_admitted`'s adoption checks at every use (schema, frame, lead id, mismatches, inventory sha, review pins, provenance re-pins, rollout re-join, adoption-observation re-validation) | F in every frame admission front part (D7, C4, D17), over the protected bytes from W; the schema check expects `wlscratch-lead-adoption-v1` | `FRONT_PARENT`; `RUNNING`; `AFTER` |
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

