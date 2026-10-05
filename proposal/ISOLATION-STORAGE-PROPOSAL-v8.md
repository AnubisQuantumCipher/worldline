# Isolation and storage proposal W-1, v8: the same-identity view, a re-evaluated architecture, and the eleven v7 corrections (specification)

**Status.** Drafting author's design specification, written 2026-10-05 UTC for the Claude Code lead. It is a
CANDIDATE specification of the protected-writer confinement design for the scratch proof frame, and the successor to
v7.
- Nothing in it is implemented, installed, approved, executed or reviewed. No account, group, ACL, sudo rule,
  installation, scope, mount, namespace, Landlock domain, probe, selftest, vault, adoption or window action has been
  performed for v8.
- Proof dispatch stays blocked by the confinement criteria (V5-B01, V5-B02, both OPEN) and by the capacity gate
  (Gate 0, NOT ESTABLISHED). **V5-B01, V5-B02, W1-V5-PRESERVATION and W1-V6-READ-MUTATION stay OPEN and are not
  narrowed** (§0.4, §21, §22.4).
- v1-v6 (hashes as v7 states them) and v7 (`ISOLATION-STORAGE-PROPOSAL-v7.md`, sha256
  `8646f0fed3cf3f61dceb4fbf3a583f96f2bf7a0adce4986cb415789edeb82a7a`, 501544 bytes, with `v7-support/jackal.json`
  sha256 `d62cca5521f007ccc7cc59fcce171f0de1d1d60f9e9e90eac75f51db49e20287`) are preserved unchanged.
- v8 answers the sealed actual gpt-6.1-sol design review of v7, `wt-1/proposal/v7-review/gpt61-v1` (verdict
  NOT_ENDORSED; hashes re-verified by the drafting author before drafting, 2026-10-05T15:26:56Z: REVIEW.md
  `2cbb34d4d528e8a0a42ab64058eed4ab2f5ff91a6a3d5c7cdd082013b64fe958`, review.json
  `1883e530a7d53dff68a7d2c4dbed2ef2df9c2a7b6d801f5181c19cc4ce28bf6d`, checks.json
  `0007d396c149af5e0ab8ae9cd92b6e4e6bac8753eb1ba738e6a40ca88940514e`, review-freeze.json
  `539a62bcf9b203e55055bdf46d89659081c728d952f2e2ced955a42a8eb48032`). Its eleven required changes (W1-V7-ARCHITECTURE
  … W1-V7-PREMISES) are quoted verbatim in §18.1 with the author's assessment; its three assessments are answered in
  §22 (architecture), §9.8 and §12 (target view) and §21 with §9.8 N7 (changes and premises).
- **Form** (§0.1). One complete specification, composed of the units whose text is in this file and of v7 units
  carried by hash. §18.5 maps every v7 unit, with its line range, size and sha256, to its v8 status.
- **Review track.** W-1 has its own design-review track: v8 is reviewed on its own by actual gpt-6.1-sol. The criteria
  and every earlier correction are unchanged and binding. **§18 gives the author's own assessment (CLOSED-AT-SPEC-LEVEL
  or OPEN) for the independent reviewer to judge. It is not closure.**
- **Authority.** Design and frame code are routine reversible engineering under the human's preserved authorization.
  Reserved to the operator, unchanged: actual privileged setup (the account, its group, ACLs, sudo rules, the sshd
  drop-in, installation of the frame and of its root launcher RL, images and their mounts, reconciliation, rollback) on
  a concrete reviewed inventory; material API/ABI/owner-policy changes; toolchain/deployment architecture; merge,
  release, install, sudo, production and real PRIME. Every privileged element of v8 (RL's installation and rule, the
  images) lies inside that reserved setup and rollback; RL's per-attempt namespaces, mounts and scopes are actions of
  the installed, reviewed code under that rule. **v8 adds no approval gate**, removes v7's invitation to a reviewer
  ruling on a lead preparation step (v7 §21 D2), and removes that preparation step itself (§3.3, §12.2).
- Every "verify", "check", "probe", "selftest" or "observe" names future work, except the passive observations
  explicitly dated and attributed to the drafting author (Appendices E-H). Design text is not executed evidence.

**Inputs read for v8** (read-only): the gpt61-v7 `REVIEW.md` and `review.json` in full, with the three assessments,
`prior_closure`, the candidate, premise, route and change classifications (checks.json and review-freeze.json
hash-verified only); v7; frame v5 `scratch.py` (`f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86`;
"S:N" is its line N); the installed kernel build headers below `/usr/lib/modules/7.2.6-1-aarch64-ARCH/build`; the
installed `/usr/include/linux/{landlock,nsfs,stat,mount}.h`; the installed man pages `sudoers(5)` and
`systemd.exec(5)`; upstream Linux v7.2 `security/commoncap.c`, `kernel/ptrace.c`, `kernel/pid.c`, `fs/proc/base.c`
and `fs/proc/fd.c` (fetched read-only; their correspondence to the installed 7.2.6-1 build is a premise, P-KSRC); the
cgroup2 limits of `sicarii`'s user slice; host facts dated in Appendix H.

**Non-claims, short form** (full list §20). No sufficiency is claimed. V5-B01, V5-B02, W1-V5-PRESERVATION,
W1-V6-READ-MUTATION, Gate 0 and every original Phase One obligation stay OPEN with their original owners, releases and
dependencies. The same-identity view is not established as preserving the original success domain: §21 lists every
remaining change, and §22.4 states why none is yet discharged. Every premise of §9.8 N7 is NAMED_UNESTABLISHED; a
failed premise requires redesign with no exception.

---

## 0. Reading guide, form and what changed from v7

### 0.1 Form

A *unit* is defined as in v7 §0.1: it begins at each line, outside fenced code blocks, that starts with `# `, `## `
or `### `, and runs to the line before the next unit's first line. v7 has 124 units (counted by a read-only script
on 2026-10-05T15:51:35Z, Appendix H). §18.5 lists each with its v7 line range, size and sha256, and its v8 status:
- **CARRIED**: the v7 unit belongs to v8 byte for byte. Its text is not repeated here, to keep v8 compact (the lead's
  instruction); this file holds a one-line stub with the unit's heading, v7 line range, size and sha256. The text is
  the v7 file's bytes at those lines, verifiable by the hash.
- **AMENDED**: the v8 unit is the v7 unit (identified by hash, as for CARRIED) with the exact amendments listed in the
  v8 stub. An amendment states the replaced text or the rule that supersedes it; where an amendment and the carried
  text conflict, the amendment governs.
- **REPLACED**: the v8 unit with the same heading number is new text, entirely in this file; the v7 unit is not part
  of v8.
- **NEW**: §21.1-§21.6 and Appendix H.

The global reading rules of §0.6 apply to every CARRIED and AMENDED unit. Units appear in v7 order; §21.1-§21.6
follow §21's heading, and Appendix H follows Appendix G. Every cross-reference resolves in v8 (a reference into a carried unit resolves into its v7 text).

### 0.2 Author corrections of v7 (v7 itself is not edited)

1. **v7 §22.3 (c8)** rejected a launcher that keeps `sicarii`'s host uid inside a root-owned user namespace, because
   "other `sicarii` processes keep the uid half of every pull check, and the target's dumpability is its own". That
   omitted the controlling capability rule: `cap_ptrace_access_check` admits a caller in another user namespace only
   with `CAP_SYS_PTRACE` in the target's namespace (§22.3, quoted). The rejection is withdrawn; c8 is re-evaluated
   first and adopted (§0.4).
2. **v7 §22.3 (b), user notification**: "unsound as a security policy" was too broad. It holds for decisions on
   target memory followed by `SECCOMP_USER_NOTIF_FLAG_CONTINUE`; it does not exclude a broker that emulates calls and
   inserts descriptors with `SECCOMP_IOCTL_NOTIF_ADDFD`. Narrowed in §22.3.
3. **P-LL** (v7 §9.8 N7) said that granting `REFER` everywhere "leaves every same-mount rename and link as without
   Landlock". False as written: `MAKE_SOCK` also governs renaming and linking a socket into a directory, and `REFER`
   requires the per-type `MAKE_*` right and no access gain (installed `landlock.h`, quoted in §9.8 N7). Corrected.
4. **P-XDEV** said that cross-mount `link` and `rename` fail with `EXDEV` "before any permission check". False: path
   resolution, with its search-permission checks, precedes the mount comparison, and Landlock's `EACCES` takes
   precedence over its own `EXDEV`. The custody argument needs only that such an operation does not succeed.
   Corrected (§9.8 N7, §6.5).
5. **P-CENSUS** asserted that a scope unit is active exactly while its cgroup is populated. False as an invariant:
   the manager handles the kernel's empty-cgroup event later. Withdrawn; §9.4 uses the conservative conjunction of
   the original predicate and the kernel state, with no equivalence assumed.
6. **"Instantaneous" holder equivalence** (v7 §2.4 R9, §9.8 N4: "every descriptor … is released when the last
   process of its scope ends, which the kernel reports atomically"). Overstated: `populated 0` reports that no task
   remains, not that every description and asynchronous mutation has ended. §9.8 N4 defines the holder event
   exactly and names what it rests on.
7. **P-VIEW's probe "first engineering run"** was a circular qualification. Withdrawn: a run's baseline comparison is
   evidence for that run only (§9.8 N7).
8. **v7 §9.8 N5** ("RL writes no file on any host filesystem"; its effects listed as complete) was too broad: map
   and `setgroups` writes, sudo, PAM, manager and journal effects were not inventoried. §9.8 N6 now holds the causal
   read and control-plane write inventory.
9. **v7's run path was not location-custodied above `source/`.** v7 bound g/source over a lead-created directory whose
   ancestors are `sicarii`-owned; an outside `sicarii` process can rename an ancestor and recreate the path, so an
   absolute lookup by the running target can be redirected. The author had not stated this. Before the spawn it is a
   pre-launch alias, which C now checks (§4.5 item 4); after the spawn it is the running-target behaviour that the
   original residual (b) covers (REVIEW.md:161, Appendix A), with conclusion detection. The admitted generation itself
   is in g and is not affected.
10. **v7 §2.3's sudo assumption**: v7 did not state sudo's PTY, PAM-session and logging behaviour for the two frame
    rules. §11.5 (amended) fixes them by sudoers options.
11. **v7 §8.3** reproduced the environment, umask and `RLIMIT_CORE` but not the other inherited process attributes
    (the other resource limits, `oom_score_adj`, nice value, I/O priority, CPU affinity, capability bounding set,
    session and terminal). §8.3 now lists every attribute with its original source and its v8 reproduction.

### 0.3 What v8 changes, per required change (§18.1 gives each verbatim, with the author's assessment)

1. **W1-V7-ARCHITECTURE** (§22): c8 re-evaluated first, grounded in the commoncap and `__ptrace_may_access` source; the
   user-notification rejection narrowed; every surviving alternative compared with (a); the same-identity view (SIV)
   adopted as the sound design with the smallest change set. Preservation obligations stay OPEN.
2. **W1-V7-VIEW-ROOT** (§12.2 steps 8, 11, 12): no root clone; the kernel's own copy of the mount namespace rebases the
   process root and cwd; one or two binds; old references closed; identities verified by `statx`, `statmount` and
   namespace ioctls, independently of mountinfo, by RL, L, C and O.
3. **W1-V7-HOLDER-STATE** (§9.4, §9.8 N4): the holder event H(U) defined; its absorbing property argued from named
   premises; P-CENSUS withdrawn; the original terminal, ownership, window and manager predicates kept in a race-aware
   conjunction.
4. **W1-V7-FULL-DOMAIN** (§21): the preservation relation over the complete original accepted and refused frame and
   target domain; TOOL-CLOSURE demoted to a sub-lemma; every v7 V-, C- and D-effect removed, reworked or kept OPEN
   with its reason.
5. **W1-V7-C3-DATA** (§9.3 C2, C3; Appendix B.4): `launcher-rl-identity.json` delivered in `RECORDS` with its commit
   binding; exact keyset and order; missing and mismatch controls.
6. **W1-V7-READ-EFFECTS** (§9.8 N6): the causal explicit, implicit and control-plane inventory; R-d, R-f, R-h and new
   bootstrap routes OPEN; foreign-owner cases preserved.
7. **W1-V7-PROBES** (§9.8 N7, §13, §13.1): P-LL and P-XDEV corrected; per-API, type- and mode-valid positive controls;
   cause-separating controls for namespace, dumpability, Yama and Landlock denials.
8. **W1-V7-COMPOSED-STATE** (§11.4, §11.5, §15.1): staged-then-renamed atoms (no script removes an installed atom);
   complete partial-file and image states; service co-effects; the evidence-retaining rollback as its own machine.
9. **W1-V7-SYNC-PROVENANCE** (§10.1, §10.5, §10.6): commit membership separated from sync provenance (`observed`,
   `failed`, `unobserved`), consistent for every consumer.
10. **W1-V7-EVIDENCE-RESTORE** (§8.5, §14.7, §15.3): a complete capture of the generation, raw records, markers,
    slots and continuations, registered with the vault as v5 registered the run; the restore peak budgeted.
11. **W1-V7-PREMISES** (§9.8 N7): one register; P-TMPAGE removed with its mechanism and recorded; sampled refutation,
    installed-version source discharge and trusted-base exclusion distinguished; "redesign, no exception" kept.

### 0.4 The architecture decision, stated plainly

**v8 adopts the same-identity view (SIV), which is c8 made concrete** (§12.2): RL, the root launcher, starts the
target with the lead's own host credentials (uid 1000, gid 1000, the lead's supplementary groups, the lead's capability
bounding set and resource limits) inside a user namespace that **W, not `sicarii`, owns**, whose maps are the identity
(`0 0 4294967295`), together with a copy of the host mount namespace (all mounts present, `nosuid`, private
propagation) in which g/source is bound at the original run path and g/tmpdir at the original `TMPDIR`, a private
network namespace, and a Landlock domain that handles only `RESOLVE_UNIX`, `MAKE_SOCK` and `REFER`. The scope is a
system-manager scope in the lead's own `user-1000.slice`.

Why this one (§22.3-§22.4): of the designs that establish the custody facts of §9.8 under named premises, it changes
the least. Against v7's (a) it removes the host identity change and its outside-observer and accounting effects (V5,
C3), the idmapped root clone, the omitted mounts (V6's first half), the masks (V9), the private `/tmp` and its
tmpfiles rule (half of V7, and P-TMPAGE), the lead-created mount point and its refusal (V11, D2's first case), the
label-logic change (C6, reworked), the new control deadlines (D5) and two of three new identities. The pull routes stay
closed by the namespace rule, not by a uid change: an outside `sicarii` process passes the uid half of the check and
fails the capability half (§9.8 N2). Owning the namespace by W rather than root keeps the target's per-user namespace
accounting off root's budget (§22.3).

**It does not preserve the original success domain as established.** It keeps the changes §12.3 and §21 list: no host
network (V1), no outward pathname UNIX connection and no socket file outside the two binds (V2), no mount operations
(V3), set-ID programs and file capabilities confer nothing (V4), host mounts made after the view's creation do not
appear (V6'), a private `TMPDIR` (V7'), the run directory's changes (V8), the scope's manager (V10'), the Landlock
domain (V12), the namespace-qualified ptrace and accounting effects (V13), and the frame-side rows. Each is either
required by the criterion through the only mechanism available on this kernel, or not yet shown irrelevant to the full
original domain; none is shown irrelevant. **So V5-B01, V5-B02, W1-V5-PRESERVATION and W1-V6-READ-MUTATION stay
OPEN.** No accepted case is narrowed by rule; where a change can turn an original success into a failure, §21 says so.

### 0.5 What is carried

The units marked CARRIED in §18.5 are carried byte for byte, and everything the reviews closed is carried in
substance (the v7 review's `prior_closure`, §18.2):
- W1-V5-IMAGE-PINS and W1-IMAGE-OBSERVATION (newly closed): §3.4's image checks, §11.7's pins and §14.5 are carried
  (§3.4 and §11.7 amended only for the removed identities and units);
- W1-JOURNAL-CONTINUATION (newly closed): §10.2's continuation rules are carried; §10.2's amendment concerns sync
  provenance only;
- W1-DURABILITY-RELEASE, W1-RESOURCES, W1-SETUP-IDENTITY, W1-V5-PROTOCOL-REFUSALS (and every earlier closure listed in
  §18.2-§18.4): unchanged in substance; the release rule of §9.4 keeps v5's predicate and adds no condition;
- W1-V6-C1-DATA, W1-V6-IMAGE-PIN and W1-V6-INVARIANTS (closed by the v6 review's successor): C1 still checks only
  compiled, argv and kernel facts (§9.3, amended for the new credentials); the image pin and the invariants are
  unchanged.

No original admission join, control, fixture, accepted case, criterion, allowance, cap or gate is relaxed.

### 0.6 Global reading rules for CARRIED and AMENDED v7 text

These rules apply wherever carried or amended v7 text uses the named terms; an explicit amendment governs over them.
1. **Credentials.** "host uid R", "gid GATE", "R and GATE", "groups G_V" and "`wlscratch-run`", "`wlscratch-gate`" as
   credentials of L, C, O or T read: the lead's host credentials (uid 1000, gid 1000, the lead's supplementary groups
   as F records them, §8.3). The identities `wlscratch-run` (R) and `wlscratch-gate` (GATE) do not exist in v8.
   Statements whose truth depended on R or GATE being distinct from 1000 (v7 CRED; "T, which has uid R, cannot take
   from them"; the v7 rows of §6.5) are superseded by §9.4 and §9.8.
2. **Namespaces.** "U_v" reads U8 (§12.2 step 10). "U_run" reads M_run, the idmap W ↔ 1000. "U_tmp", "the `/tmp`
   bind", "g/tmp", "`tmp/`" (as a generation directory) and "the masks" have no v8 counterpart: `/tmp` is the host's
   and no mask exists. "The root view", "the idmapped clone of the root" read: the copied mount namespace of §12.2.
3. **Scope.** "`wlscratch.slice`" and "`/wlscratch.slice/<U>`" read `user-1000.slice` and
   `/user.slice/user-1000.slice/<U>`; "every child of `wlscratch.slice`" reads "every `wlscratch-*.scope` child of
   `user-1000.slice`". The unit file `/etc/systemd/system/wlscratch.slice` and `/etc/tmpfiles.d/wlscratch.conf` do not
   exist in v8.
4. **Deadlines.** The W-1 control deadline (60 s) and the front stage-observation deadline (600 s) do not exist in v8
   (§7.4, amended); a carried "within the control deadline" reads "before EOF on the channel"; v5's own time limits
   (300 s, 30 s, 30 s) apply where v5 applied them. W2's 10 s retry and round intervals (§9.7) are pacing of a
   post-writer recovery, not deadlines, and refuse nothing.
5. **Lead preparation.** Every statement that the lead creates `<RUNS>/<label>/source` before dispatch, and every
   refusal for its absence, is withdrawn (§3.3).
6. **v7 premises** P-IDMAP, P-LL, P-XDEV, P-PTRACE, P-CG, P-NOR, P-NOSUID, P-LOCK, P-VIEW, P-CENSUS and P-TMPAGE read
   as §9.8 N7 restates or withdraws them.
7. **Historical text.** Mentions of v4-v7 mechanisms in Appendices C-G are historical.

## 1. Criteria (verbatim, unchanged)

CARRIED from v7: lines 186-227, 3156 bytes, sha256 `2ae9da8b3dc5177eb189805c8f7fdc48e4908a2204fb68a6b4be0b5118aa0dac`.

## 2. Threat model, trusted base, preconditions and residuals

CARRIED from v7: lines 228-229, 63 bytes, sha256 `35f6eb75cbc9b074ead5488fca9693875386deb826fbd0374020398a83887683`.

### 2.1 Adversaries

- **A1, concurrent `sicarii` processes** (other agents and sessions; uid 1000), exactly as in v7: arbitrary code as
  `sicarii`, user namespaces over the delegated subordinate range 100000-165535, FUSE mounts through the set-user-ID
  `fusermount3`, reads of every dumpable `sicarii` process's `/proc` entries in their own user namespace, signals,
  writes to every `sicarii`-writable file (the window file, the inbox, frozen inputs, the toolchain under
  `/home/sicarii/opt/gnat`, every ancestor of the run path), renames of every `sicarii`-owned directory, and invocations
  of the reviewed `sicarii`→`wlscratch` sudo rule with arbitrary arguments. Because A1 can rewrite the toolchain
  between its identity check and its use (the ruled residual (c)), **the target is treated as A1's agent**: anything
  A2 may do, A1 may in effect do inside the view. A1 must not be able to create, rename, substitute, modify or delete
  any frame-owned location or the admitted generation, or cause the frame to mutate outside its tree.
- **A2, the running target** (the allowlisted command and everything it starts, inside the same-identity view of
  §12.2: the lead's host credentials, the user namespace U8, the copied mount namespace with the two binds, the private
  network namespace, the Landlock domain, the attempt scope). It may do anything that view permits: write wherever
  `sicarii` can write, change the modes and ACLs of everything it owns, use `io_uring`, `openat2` and AIO, create
  nested user and mount namespaces (in which Landlock still forbids mounts), pass descriptors among its own processes,
  signal any `sicarii` process (as in v5), and leave processes running in its scope. It cannot connect to a pathname
  UNIX server created outside its domain, create a socket file outside the two binds, reach any abstract socket of the
  host, mount anything, gain privilege by `exec`, ptrace or read the `/proc` details of a process outside its
  namespace, reach g except its `source/` and `tmpdir/`, or leave its scope. Nothing it does may let a principal
  outside the attempt's own process tree hold a usable reference to, or a usable name for, an admitted entry (§9.8).
- **A3, every other non-root principal** (other users' processes and non-root services). They hold no credential that
  reaches g, and no channel into a view (§9.8 N1-N3).

### 2.2 Trusted base (outside the threat model)

Root and everything running as root (sudo, systemd and logind, PAM, sshd, the kernel, RL); the writer identity W and
the reviewed code that alone runs as W (the writer and W2; W owns g and every U8, §12.2); root-owned installed files
(`/usr`, `/etc`, the installed frame under `/opt/wlscratch`); the kernel's namespace, idmapped-mount, Landlock,
cgroup, ptrace and file-handle implementations, whose relied-on behaviour is stated as premises (§9.8 N7) — a premise
of the trusted base is an assumption with a refutation probe and a source-reading obligation, never a passing test;
the Python 3.14.7 runtime under `/usr/lib/python3.14`; the operator's credential. The design gives no protection
against root, against kernel defects or against a compromised operator credential.

### 2.3 Preconditions (checked at setup, §11.3; their failure refuses setup)

AMENDED from v7: lines 270-296, 2629 bytes, sha256 `5c4aad42392d62002b099a573afe71fee7a5d9cb108cfb198638760cdb8ffd6d`.
Amendments:
1. First bullet: "root, `wlscratch`, `wlscratch-run` or with `wlscratch-gate`" reads "root or `wlscratch`"; "owned by
   the new identities" reads "owned by `wlscratch`".
2. Third bullet ("Kernel features the target view needs"): delete `CONFIG_PID_NS` and `CONFIG_IPC_NS` from the list of
   needed options (v8 creates neither namespace) and add: the installed headers define `NS_GET_MNTNS_ID`,
   `NS_GET_OWNER_UID`, `NS_GET_PARENT` (`linux/nsfs.h`), `STATX_MNT_ID_UNIQUE` (`linux/stat.h`) and `struct statmount`
   with `STATMOUNT_MNT_NS_ID` and `LSMT_ROOT` (`linux/mount.h`), observed 2026-10-05T15:51:39Z (Appendix H).
3. Fourth bullet: "v7 relies on `EXDEV` only between the distinct mounts of the target view" reads "v8 relies only on
   the non-success of `link` and `rename` between distinct mounts of the view (premise P-XMNT, §9.8 N7)".

### 2.4 Residuals (stated exactly; none is a new accepted exception)

- **R1, the lead's own processes** (v7 R1, unchanged): W-1 does not protect `sicarii` processes from other `sicarii`
  processes; each frame process outside a view sets itself non-dumpable as its first effective act (§7.7). This is the
  inability carried from frame v5.
- **R2, lead authentication** (v7 R2, unchanged): the original v5 engineering ceiling, carried exactly.
- **R3, the running target** (the ruled `no-target-confinement` residual, ACCEPTABLE_AS_DOCUMENTED at the reference
  ceiling): no confinement of the running target outside g; it covers target writes only, never a frame write and never
  an unsafe alias at final admission. In v8 the target holds `sicarii`'s own credentials and authority, so its writes
  outside g are exactly the original target's, apart from the changes of §12.3.
- **R3b, the running target's path lookups** (the ruled residual (b), REVIEW.md:161 of the v5 review, Appendix A): "v5
  similarly cannot prevent an already-running target from resolving absolute paths or writing while another process
  changes the tree". In v8 the ancestors of the run path are `sicarii`-owned host directories (§3.3); A1 can rename
  them after the spawn and so redirect a later absolute lookup by the running target. The admitted generation in g is
  not changed by that, and the conclusion's comparison of the generation detects a run whose outputs did not land in
  it. Before the spawn, a redirected path is a pre-launch alias, which C refuses (§4.5 item 4), as v5 refused a run
  directory that its location chain did not reach.
- **R4, the toolchain** (ruled ACCEPTABLE_AS_DOCUMENTED, unchanged): identity-checked, then executed by path; W-1
  claims no custody of it.
- **R5, exposure**: the target reads exactly what `sicarii` reads, including the export trees that the lead may read
  (§6.3); the view's construction is privileged code (RL), reviewed and installed by the operator.
- **R6, availability**: a `sicarii` process can stop an attempt (kill the front, signal processes whose real uid is
  `sicarii`, which in v8 includes the target, as in v5, or modify the window file, N07). The result is an interrupted,
  non-success attempt or a held window, never a custody change. Whether sudo relays such signals is probe P-SIG.
- **R8, root and the kernel** (§2.2).
- **R9 (withdrawn as stated in v7)**: v7's "released … which the kernel reports atomically" is replaced by the holder
  event of §9.8 N4 and its premises.

## 3. Principals, accounts and layout

CARRIED from v7: lines 335-336, 39 bytes, sha256 `5510e891fd324593657d164471cb63078bbc71af4f71c2da3fc35163ae8c2ed0`.

### 3.1 Accounts and groups (one new identity)

| Identity | Kind | Purpose | Members |
|---|---|---|---|
| `wlscratch`, uid = gid = W | user + user-private group | The only writer of generation trees; the owner of every view user namespace U8 (§12.2) | none besides the user |

Candidate number: W = 950, unused by every passwd and group entry as observed on 2026-10-04 (v7 §3.1), inside
`SYS_UID_MIN`-`SYS_UID_MAX` and outside every subordinate range; §11.2 fixes the policy and the prestate re-verifies
it. v7's `wlscratch-run` (R) and `wlscratch-gate` (GATE) are withdrawn: no process of a view has another host
identity than the lead's. `sicarii` gets no new group membership and no new login.

### 3.2 Roles (processes)

| Role | Process and credentials | Started by | Code |
|---|---|---|---|
| F, front | the lead's real outer invocation `/usr/bin/python3 -B /opt/wlscratch/frame-v6w1/front.py <verb> …`, uid 1000; verbs `adopt`, `materialize`, `dispatch` | the lead | installed, root-owned |
| S1 | `sudo -n -u wlscratch -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py <verb> …` | F | `/usr/bin/sudo` |
| W, writer | `writer.py`, uid/gid W; verbs `adopt`, `materialize`, `dispatch`, `selftest` | S1 | installed |
| S2, S_O | `sudo -n -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py <verb> …` (the RL rule) | W or W2 | `/usr/bin/sudo` |
| RL, root launcher | `sandbox_launch.py launch …` or `observe …`, root: checks its invocation, creates the scope with `systemd-run --scope` in the system manager under `user-1000.slice`, builds the view (§12.2), sends `RL_IDENTITY` and `exec`s L or O | S2 or S_O | installed, privileged |
| L, launcher | `launch_target.py launch …`, the lead's host credentials, in U8 and the view, in the attempt scope | RL, which `exec`s it in place | installed |
| C, in-scope child | `launch_target.py child …`, the same pid, credentials, view and scope as L | L, by `exec` after `GO` | installed |
| U, scope | transient `wlscratch-<g12>-<A>.scope` of the system manager in `user-1000.slice`, with `MemoryMax=8G`, `MemorySwapMax=0` and the properties of §8.3 | RL, through `systemd-run --scope` | systemd |
| T, target | the exact allowlisted command, the same credentials, view and scope; started by C's spawn call (v5 `spawn`) | C | toolchain |
| O, observer | `launch_target.py observe …`, the lead's host credentials, in its own scope `wlscratch-o-<g12>-<A>-<n>.scope` in `user-1000.slice` and its own view instance | RL, for W or W2 | installed |
| S3, W2 | as v7 (`seal-front`, modes `seal` and `recover`) | F | installed |

`<g12>`, `<A>`, `SOURCE_FRAME`, `REVIEW` and `INSTALLED_REVIEW` are as in v7 §3.2. Every process of a view is started
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
        attempts/<A>/                  P_att(g, A), as v7
        export/                        P_exp(g): generation/, <A>/inc-<n>/, capture-<A>/ (§15.3)
      adoption-<I>/                    W:W           P_ado(I), as v7
    selftest-<h>/, records/selftest-<h>/   as v7
/opt/wlscratch/frame-v6w1/             root:root     installed frame (member-exact)
/opt/wlscratch/setup-identities.json   root:root 0644 setup identity record (§11.5 S-H, §11.7)
```

v7's `g/tmp`, `/etc/systemd/system/wlscratch.slice` and `/etc/tmpfiles.d/wlscratch.conf` are withdrawn: the target's
`/tmp` is the host's, and the scopes live in the lead's existing `user-1000.slice`.

**The run path without a lead preparation step** (rework of v7 V11, D2 and C6). `<RUNS>` is v5's `RUNS`
(`/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-runs-v5`). Neither the
lead nor the frame creates anything there: the frame's outside-tree authority stays limited to the window protocol and
the prescribed preparation records (V5-B02), and no lead step is required. RL presents the run path inside the view
only (§12.2 step 11):
- if `<RUNS>/<label>/source` exists in the copied namespace as a directory reached without symlinks, RL binds g/source
  over it (the host directory's contents are hidden in the view, as in v7);
- otherwise RL mounts a private read-only `tmpfs` (the *skeleton*) over the deepest existing directory ancestor D of
  the run path, creates in it the missing directories of the path (owner 1000:1000, mode 0700, as v5's `materialize`
  created `<RUNS>` and `<RUNS>/<label>`, S:977-986), re-attaches every entry of D as a bind of the host entry, and binds
  g/source at the end of the path.
No host filesystem is written in either case. **Label semantics** (v5: `materialize` refused when `<RUNS>/<label>`
existed, S:984-986): `materialize` refuses when `<RUNS>/<label>` exists on the host (F's anchored, read-only check,
v5's own test) or when a generation of T carries the label. For every state reachable through frame verbs the outcome
is v5's: the frame never creates `<RUNS>/<label>`, so v5's refusal "the run directory this label's materialize created
exists" corresponds to "a generation with this label exists". The one remaining difference (C6' in §21): in v5 the
lead could free a label by deleting the run directory; a generation in T cannot be deleted by the lead.

### 3.4 The protected intended run tree, its anchors and routing [corrections: W1-V6-IMAGE-PIN, W1-V6-INVARIANTS; v4: W1-IMAGE-TREE]

AMENDED from v7: lines 424-495, 6872 bytes, sha256 `0e55f3b852cef2cf3ca2a38ed3b642b91ee463a843abf1ef030a2dbf2b881917`.
Amendments:
1. Definition: "below `g/source`, `g/tmp` and `g/tmpdir`" reads "below `g/source` and `g/tmpdir`"; "with idmaps" reads
   "with the idmap M_run".
2. Anchors: "RL hands them their generation's `source/`, `tmp/` and `tmpdir/` as mounts of the view" reads "RL hands
   them their generation's `source/` and `tmpdir/` as binds of the view".
3. Routing table, first row: "`tmp/` and `tmpdir/` (M7)" reads "`tmpdir/` (M7)"; "the contents of `tmp/` and
   `tmpdir/`" reads "the contents of `tmpdir/`".
4. Missing-mount checks, last sentence of the first bullet: "L, C, O and T never see the images directory" reads "L,
   C, O and T see the images directory as `sicarii` does: `/var/lib/wlscratch-images` is root:W 0750 and grants them
   nothing".
5. "No new outside-tree authority", third sentence: "RL mounts only inside the private mount namespaces it creates,
   writes only the maps and settings of the namespaces and processes it creates, and asks the system manager for the
   scope; it writes no file outside T (§9.8 N5)" reads "RL's effects outside T are exactly those of the inventory
   §9.8 N5-N6, each classified there".

## 4. Generation order and record partitions [correction: W1-GENERATION-PROTOCOL; gap: generation-order]

CARRIED from v7: lines 496-497, 106 bytes, sha256 `030cba113f70fd51a55fba2cdbacef1d4bebdd0fa2b0813f0a7f935356beaa45`.

### 4.1 Partitions [correction: W1-V6-INVARIANTS]

AMENDED from v7: lines 498-540, 4017 bytes, sha256 `a5c68784c918927bb85b3821b3f30cc0cfdfce7f5665f23a80f8454f7d67ceea`.
Amendments: "the directories `tmp/` and `tmpdir/` themselves" reads "the directory `tmpdir/` itself"; the
target-temporaries bullet reads: "**Target temporaries**, below `g/tmpdir/` (the view's `TMPDIR`,
`/home/sicarii/.cache/workflow-tmp`) (§12.2). Never read, walked, admitted or exported by the frame, except that the
complete capture of §15.3 copies them as evidence after the scope has ended." Every sentence about `g/tmp/` is
withdrawn: the view's `/tmp` is the host's `/tmp`, outside T.

### 4.2 Exact order

AMENDED from v7: lines 541-704, 14968 bytes, sha256 `7b7989df8a2e302e11207aab6adaeb1b633b6eba048d56e7cf73336cf9715156`.
Amendments:
1. M7: the creation of `tmp/` and its mode 01777 is withdrawn; after the recipe, `tmpdir/` is created (0700,
   authenticated) as in v7. The M8 and D-step identity lists drop `tmp/`.
2. M10 and D9 (`VAULT`): F runs `project-vault pin <g_rec>/export` and `project-vault status` as v7 states; §8.5 and
   §15.3 (amended) define what that export contains, which now includes the complete capture of every ended attempt.
3. Every W-1 control deadline and every 600 s front stage-observation deadline named in this unit is withdrawn (§0.6
   rule 4, §7.4); D13's v5 deadlines (300 s and 30 s) are unchanged.
4. D8 (parent stage): "no process with host uid R or gid GATE outside the scopes" is withdrawn; the parent-stage
   observations are those of §9.4 (v8).
5. Before M4, F performs v5's label check (§3.3): `<RUNS>/<label>` absent on the host, by `Dir.anchor(RUNS.parent)`
   and `has`, read-only; W additionally refuses a label that a generation of T carries. F creates nothing.

### 4.3 The records that order the generation (complete field lists in Appendix B.3)

AMENDED from v7: lines 705-776, 6825 bytes, sha256 `307c39b54b88ff15c2e44d70df17cd6d62d83ffea57ad12b36a591f4c7c20b0b`.
Amendments: fields naming `tmp/` are withdrawn; `launch.json` additionally binds the lead's process attributes of §8.3
(`process_attributes`, Appendix B.3) and the run-path presentation RL must build (`run_path_mode`: `bind` or
`skeleton`, decided by RL and reported in `RL_IDENTITY`, not by W in advance).

### 4.4 Anchors and joins

CARRIED from v7: lines 777-802, 2451 bytes, sha256 `eb572f6edb96f31e7bf59a9d8176ed06a37de4f96282533d86a1d70d7d31a59c`.

### 4.5 Where the final pass is, exactly [corrections: W1-V6-INVARIANTS, W1-V6-SCAN-STATE]

AMENDED from v7: lines 803-851, 4428 bytes, sha256 `6bac3c43cbe1b3716bd262cb7504ac26b6ebaf5131f420f24ba37e8a35a26fe5`.
Amendments:
1. Item 1: "Through RL's idmap C is the owner" reads "Through the bind's idmap M_run (on-disk W shown as 1000) C is the
   owner".
2. Item 3 reads: "Then C takes the child-stage observations of §9.4 (its scope holds exactly C; every other RL scope in
   `user-1000.slice` is absent or `populated 0`), re-verifies the location of its held handles, and continues with
   item 4."
3. New item 4: "**Run-path alias check.** C resolves the run path `<RUNS>/<label>/source` and the `TMPDIR` path from
   `/` component by component (`openat2` with `RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS`, `O_PATH|O_DIRECTORY`) and
   requires each result to be the root of the corresponding bind (`statx` `STATX_ATTR_MOUNT_ROOT`, `stx_mnt_id` with
   `STATX_MNT_ID_UNIQUE` equal to the bind's ID in `launcher-rl-identity.json`, `[dev, ino]` equal to the sealed
   identity). It also requires the same of every absolute path in T's environment that lies below the run path
   (`PENDING_LIBRARY_DIR`, `PENDING_OBJECT_DIR`, `PYTHONPATH`, `WORLDLINE_CORE_LIB`, as far as each exists). A failure
   is a pre-launch alias and refuses (RP1), as v5 refused a run directory its location chain did not reach. Then C
   reaches the interruption point (pending-signal check) and spawns with `fchdir` on the held `source` descriptor (v5
   `spawn`)."
4. Facts (i)-(v) are replaced by: "(i) no principal outside the attempt's own process tree, other than root and W,
   holds a usable reference to, or a usable name for, an admitted entry, and none can obtain one (§9.8 N0-N3); (ii) as
   v7; (iii) every process whose user namespace is a U8 descends from an RL stage-2 process inside a new RL scope
   (premises P-SETNS and P-CG); (iv) at the final pass, by C's own observations, the attempt scope holds exactly C and
   every earlier RL scope is absent or `populated 0`; (v) by §9.8 N4, each earlier scope's holder event H has occurred
   and is absorbing, so no earlier holder can act before T's `exec`; outside principals have neither path, reference
   nor channel (i); C is frame code." The closing sentence is unchanged.

### 4.6 The fresh installed-frame adoption record [correction: W1-GENERATION-PROTOCOL]

CARRIED from v7: lines 852-916, 5877 bytes, sha256 `00b3ed65328eb21773f171bf89852ac17c227e4c242c254aa4e2bc5c739eb234`.

## 5. Lease, writer authority and entrypoint closure [corrections: W1-IMAGE-TREE, W1-TERMINAL-CUSTODY; gap: lease-and-writer-authority]

CARRIED from v7: lines 917-918, 137 bytes, sha256 `46adbb0dd725d4f1ca5f142a684061fafc17e2c5165b6da45647a41585de9bab`.

### 5.1 `writer.lock`: creation, checks, use

CARRIED from v7: lines 919-946, 2284 bytes, sha256 `e0bc923e20b24b36609ff4d44f5a354e999dcd57c67793c398d1890d68c14b97`.

### 5.2 What the writer may mutate (the complete list) [corrections: W1-V6-INVARIANTS, W1-V6-COMMIT-AMBIGUITY; v4: W1-IMAGE-TREE]

AMENDED from v7: lines 947-979, 3802 bytes, sha256 `8c91cb45b3f5748048a6ea7c12b8573b152a248b3090044b4219bb7a3a9a076c`.
Amendments: "`tmp/` and its mode" and "`tmp/` or" are withdrawn from the `materialize` row and the following
paragraph; the export rows add the complete capture of §15.3 (`capture-<A>/`, P_exp), written only after the
attempt's scope is `populated 0` and its holder event has occurred (§9.8 N4).

### 5.3 Entrypoint closure [correction: W1-V6-SCAN-STATE]

AMENDED from v7: lines 980-1002, 4835 bytes, sha256 `b17708dc9fad2e80adcb7faf433456de4cd5da6d4718f0097856faebebbbd23a`.
Amendments: the columns for `wlscratch-run` (R) and `wlscratch-gate` (GATE) are withdrawn with those identities. The
`sshd` row's drop-in reads `DenyUsers wlscratch`. The `system units` row reads "no unit or D-Bus service file
references W; the transient scopes RL creates in `user-1000.slice` are runtime objects of the system manager". A new
row is added:

| Route | Membership of a view user namespace U8 |
|---|---|
| creation | only RL creates a U8, through a short-lived helper that it forks, gives uid and gid W and no groups, and that calls `unshare(CLONE_NEWUSER)`; the owner of U8 is therefore W (§12.2 step 10) |
| entry | `setns` into U8 needs `CAP_SYS_ADMIN` in U8; a process has it only as root in the initial namespace, as a process with euid W in the initial namespace (the owner rule; only the reviewed writer code and RL's helper run as W), or as a process inside U8 holding it, which no view process does (premise P-NOCAP) |
| inheritance | every other member descends from RL's stage-2 process, which `setns`es into U8 only after `systemd-run` has placed it in the new scope (premises P-SETNS, P-CG) |

### 5.4 Subordinate-ID exclusion

CARRIED from v7: lines 1003-1009, 478 bytes, sha256 `debd77ac854c1a74be9913a849254ef55cff1e9f0adc2553f42431b3167eee6a`.

## 6. Modes, ACLs and access paths [corrections: W1-IMAGE-TREE, W1-COMMIT-JOURNAL-EXPORT, W1-SETUP-PROBES-ROLLBACK; gap: per-entry-modes-acls]

CARRIED from v7: lines 1010-1011, 144 bytes, sha256 `6a852dcafc48edb984b90136498474c97f6f0348b8e6541fe33b803af9034fd3`.

### 6.1 The v5 recipe and record modes are preserved exactly [correction: W1-V6-INVARIANTS]

CARRIED from v7: lines 1012-1032, 1821 bytes, sha256 `3d18ff6cf3be2307f6980717d1796fd4963eed1bddb4d51232ac59c328d2d608`.

### 6.2 Why ACLs never touch a mode that is recorded [correction: W1-V6-INVARIANTS]

CARRIED from v7: lines 1033-1049, 1442 bytes, sha256 `155a6ef1dfdbbf811f6bd5f0a35f3134e8e60f171ee273535f4b227a30e760c2`.

### 6.3 Per-object owners, modes and ACLs

AMENDED from v7: lines 1050-1089, 4528 bytes, sha256 `a9ea41912a3fa75eb1ca915ce4940ba071282e631262acfe94e89deea9482dea`.
Amendments:
1. The rows for `tmp/`, the contents of `tmp/`, `/etc/systemd/system/wlscratch.slice` and `/etc/tmpfiles.d/wlscratch.conf`
   are withdrawn.
2. Partition contents row, owner column: "on disk W:W, because the run-path bind's idmap M_run stores the target's
   1000:1000 as W:W (§12.2); the target sees them as 1000:1000". The same holds for the contents of `tmpdir/`.
3. The `export/` rows add `capture-<A>/` and everything below it, with the export modes and ACL of the existing rows.
4. Note added: because the target's host uid is now 1000, the `user:1000` search and read entries that serve the
   lead (on `/var/lib/wlscratch`, `runs/`, `runs/records`, g_rec, `adoption-<I>` and the exports) apply to the
   target exactly as to every other `sicarii` process. g, the records originals and `lease/` carry no entry for 1000.
   The target therefore reaches T only as `sicarii` does, plus its two binds.

### 6.4 Access paths

- **The target reaches its generation only through its two binds** (§12.2): `source/` at the original run path and
  `tmpdir/` at the original `TMPDIR`, both idmapped by M_run, under which it owns every entry, as it owned its run
  tree and its `TMPDIR` in v5. Everything else of T it reaches only as `sicarii` does (§6.3 amendment 4): search on
  the ancestors, read on the exports, nothing in g. It creates its output partitions itself, as in v5, and writes its
  stream files through descriptors it was given.
- **C and O** read through the same binds, as owners of every entry, with `O_NOATIME`. A target-created object that
  its owner cannot read (for example mode 0000) yields an observation failure and a non-success outcome, v5's own
  readability rule. Everything C needs from the records tree reaches it over its channel (§9.3 C2).
- **The writer never opens a target-created object while a target can run.** Its own walks cover the recipe and skip
  the output partitions. After the attempt's holder event (§9.8 N4) it reads the whole generation, as owner on disk,
  with `O_NOATIME`, only to make the complete capture (§15.3).
- **The lead reads evidence from P_exp and the adoption exports**, through the `user:1000` entries (§6.3).
- **Every other non-root principal** falls to `other::---` below `/var/lib/wlscratch`.
- **Partition roots**: as in v5, created by the target (S:1033); v6's ROOTS hypothesis is not needed.

### 6.5 Denial matrix (each cell is a probe in §13)

| Object | `sicarii` processes outside views (A1), and view processes outside their binds | other non-root principals (A3) | view processes through their binds | W |
|---|---|---|---|---|
| `/var/lib/wlscratch`, `runs/`, `runs/records`, g_rec, `adoption-<I>` | search only | none | n/a | as v7 |
| `lease/`, `writer.lock` | none | none | n/a | search; open read-only and `flock` |
| g, P_adm records, `inputs/`, snapshot, `commits/` | none | none | n/a (not reachable) | full (owner) |
| recipe and partition entries below `source/` | none | none | owner through M_run | owner on disk; reads only after H (§6.4) |
| `tmpdir/` and its contents | none | none | owner through M_run (the view's `TMPDIR`) | owner on disk; reads only after H |
| P_att and P_ado originals | none | none | stream bytes only through passed descriptors | full (owner) |
| P_exp and adoption exports | read | none | read (as `sicarii`) | full (owner) |

In every cell marked "none", "read" or "search", every mutation (create, `mkdir`, `unlink`, `rmdir`, `rename` in or
out, `link`, `symlink`, `open` for write, `truncate`, `chmod`, `chown`, `setfacl`, `utimensat`) must not succeed. The
expected errno of each probe cell is derived from its exact operand and the first check that fails (correction
P-XDEV): a missing search permission on an ancestor gives `EACCES` during path resolution; a create, unlink, rename or
symlink in a directory the actor can search but not write gives `EACCES`; an open for writing, a `truncate` or a
`utimensat` without explicit times on a reachable file the actor cannot write gives `EACCES`; `chmod`, `chown`, an ACL
`setxattr` and `utimensat` with explicit times by a non-owner give `EPERM`; a hard link of another owner's file that
the actor cannot both read and write gives `EPERM` (`fs.protected_hardlinks=1`). A `link` or `rename` whose two paths
resolve to different mounts gives `EXDEV` only if path resolution and every earlier check succeed, and Landlock's
`EACCES` takes precedence over its own `EXDEV` (installed `landlock.h`); §13 therefore states, per probe, whether the
operands are same-mount (then the permission errno is expected) or cross-mount with fully permitted resolution (then
`EXDEV`), and the custody claim uses only "does not succeed". The frame's walks refuse any symlink, special file and
multiply linked regular file, as the original walk does (S:531, S:554); they refuse no set-ID leaf and no device
boundary.

## 7. Channels, expectations and dumpability [correction: W1-GENERATION-PROTOCOL; gap: channel-and-dumpability]

CARRIED from v7: lines 1144-1145, 113 bytes, sha256 `8ab0b34614a172ffb23cde8314d7bef25492c58858feabd1d30e543cde17fbae`.

### 7.1 Channels and transports

AMENDED from v7: lines 1146-1162, 2146 bytes, sha256 `9fbaf54e2de1e4e3e0db688efb1d901ef43faea28a6684a58eea01082dbe8210`.
Amendment: the W↔C channel carries, in `RECORDS`, the committed bytes of `launcher-rl-identity.json` (§9.3 C2,
Appendix B.4); W reads every socket with `recvmsg` and a zero-length control buffer, so a descriptor that L, C or O
sends is truncated by the kernel (`MSG_CTRUNC`) and never installed in W, and W records a channel failure.

### 7.2 Canonical encoding and framing

CARRIED from v7: lines 1163-1185, 2191 bytes, sha256 `7faec7003ad60f3723bd527d117099d1c40615466ed7acd274903c19a54d8047`.

### 7.3 Chain initialization, validation and retained form [correction: W1-V6-EVIDENCE-RESTORE]

CARRIED from v7: lines 1186-1219, 3468 bytes, sha256 `eeaeab07f27381c5af35893f610b81e421bd7ca96e7568d96540ced5164e5e2e`.

### 7.4 Rejection rules

AMENDED from v7: lines 1220-1233, 1131 bytes, sha256 `66f9582ac696d0efbf60ec1e3ff0f29f7f484f24093b667798f983ee0a9a9a0d`.
Amendments (rework of v7 D5): in the second bullet "an expired deadline" is withdrawn. The third bullet reads:
"Deadlines: only v5's own, at v5's points: 300 s first byte and 30 s completion for an answer line; 30 s per subprocess
observation. W-1 adds none. A peer that dies closes its end, and the receiver sees EOF (a channel failure, §9.5); a
peer that is alive but slow is waited for, as v5 waited for a slow frame operation. The lead's interrupt of F closes
F's channel ends, which every later receiver sees as EOF. Before launch an EOF refuses with nothing reserved or
launched, as applicable; after launch it never stops the wait for participants."

### 7.5 In-memory expectations (the v5 admission protocol's, carried)

CARRIED from v7: lines 1234-1249, 2318 bytes, sha256 `58b24a0d5a3462b2659cb856abf0558bf42183193c745d16bdba67a72037114a`.

### 7.6 Integrity is not sender authentication

CARRIED from v7: lines 1250-1259, 826 bytes, sha256 `da3dc6642e8c8b1bf407a522e929faa1997c00c2b74738d67783089debc1b34a`.

### 7.7 Dumpability: set, read back, when

AMENDED from v7: lines 1260-1283, 2261 bytes, sha256 `896aa8191f98cba8110b73eefe4f823da866fc5ae0b2351a883e8b48763115ec`.
Amendment: the pre-first-call residual for L, C and O reads: "L, C and O run with the lead's host uid inside a U8.
Before their call, a process outside their U8 cannot read them, because every ptrace-mode access from another user
namespace needs `CAP_SYS_PTRACE` in theirs (§9.8 N2); inside their U8 only RL's earlier stage (the same process) and,
for C, nothing else exists before the spawn call. Their non-dumpable setting is therefore defense in depth, not the
reason for their closure. Their stream files are W-owned 0600 and their channel sockets cannot be reopened through
`/proc`."

## 8. Fresh identities, the real outer invocation, the original context and the vault [gap: fresh-identities-and-vault]

CARRIED from v7: lines 1284-1285, 121 bytes, sha256 `5dc90f8d992d37f789b9fdc38f5cef1248a2bb2ae0c5322ab39442c58024bc66`.

### 8.1 Per-invocation role identity

CARRIED from v7: lines 1286-1312, 3351 bytes, sha256 `c68f5aea009de4262a665bfffffd00df534776dbc2e70e79dd3637ee6f0334ba`.
(Under §0.6 rule 1, "1000 for host R and for host GATE" reads "1000, which is also the host id".)

### 8.2 The real non-isolated outer invocation is kept

CARRIED from v7: lines 1313-1324, 1030 bytes, sha256 `309b19cccb33bc3a0a2d9863e13e869de1e42a9ae055ede4b84a47ec7fde5705`.

### 8.3 The original target command, environment, limits and process attributes [correction: W1-V7-FULL-DOMAIN]

- `child_argv` is exactly v5 `command()` (S:1054-1070), executed by path (R4); the view shows it at the same path, in
  the same object, because the view's root is a copy of the host's mount table with no idmap (§12.2).
- **Process attributes.** In v5 the target inherited the frame's attributes through `systemd-run --user --scope`,
  which runs the command in the caller's context, and v5 changed only the cwd (`fchdir`), the umask (077, S:1992),
  `RLIMIT_CORE` (0, 0) and the signal mask (S:1508-1517). In v8 the chain F → sudo → W → sudo → RL would otherwise
  substitute root's and sudo's values, so F records its own values in `launch.json` (`process_attributes`) and RL
  applies them to its stage-2 process before L's `exec`; L, C and T inherit them. C reads every one back before the
  spawn (C6) and the parent observation records them.

| Attribute | v5 source | v8 reproduction |
|---|---|---|
| uid, gid (real, effective, saved, fs) | the lead (1000, 1000) | `setresgid`, `setresuid` to 1000 inside U8, whose identity map makes the host ids 1000 (§12.2 step 14) |
| supplementary groups | the lead's | `setgroups` to F's recorded list |
| capability sets | the lead's (all zero for a uid-1000 process; bounding set as inherited) | permitted, effective, inheritable and ambient zero (the `setresuid` rule); bounding set equal to F's recorded `CapBnd` (RL drops only what F's lacks); no securebits set |
| `no_new_privs`, seccomp | 0, none | 0, none |
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
  manager defaults, read-only). The hierarchical limits of the original ancestors `user@1000.service` and `app.slice`
  cannot be reproduced on a scope outside them; on 2026-10-05T15:51:43Z `app.slice` had `memory.max` 25769803776
  (24 GiB), `memory.high` 21474836480 (20 GiB) and `memory.swap.max` 17179869184 (16 GiB) (JACKAL exact, parsed
  `25769803776/2^30`, `21474836480/2^30`, `17179869184/2^30`), shared by every member of `app.slice`, and
  `user@1000.service` and `user-1000.slice` had `memory.max` `max`, `user-1000.slice` `pids.max` 84514 (Appendix H).
  The shared `app.slice` budget is therefore a remaining difference (§21 V10'); the `user-1000.slice` limits apply as
  in v5, because the scope lies below it.
- `MIN_MEM_AVAILABLE_KB = 16777217`, `MAX_CHALLENGES = 3`, v5's 300 s and 30 s receipt deadlines and its 30 s
  observation timeouts are unchanged; the target executable's digest is checked before the spawn (v5 S:1839-1841).
- W-1 adds no `no_new_privs`, no seccomp filter and no capability change beyond what the namespace rule implies.
  What the view itself changes for T is inventoried in §12.3 and §21.

### 8.4 The original context inside the view [correction: W1-V6-PRESERVE]

AMENDED from v7: lines 1346-1378, 2862 bytes, sha256 `dc06ffee8154663ef3eb7a806cc4757b40fd15c191f1da590ff06994b8c9e454`.
Amendments:
1. First paragraph: "Inside its user namespace the target is uid 1000 and gid 1000 with the lead's supplementary
   groups, and the view shows the host filesystem with `sicarii`'s on-disk ownership" reads "The target is uid 1000
   and gid 1000 with the lead's supplementary groups both on the host and inside U8, whose maps are the identity, and
   the view shows the host's own mount table, with no idmap except the two binds".
2. Table rows: `/tmp` reads "the host `/tmp` (uid 0, gid 0, mode 01777), unchanged"; `/var/tmp` and the last row read
   "the host objects, unchanged"; `TMPDIR` and the run's source keep v7's text with "M_run" for "the idmap".
3. The P-VIEW sentence reads: "That every original observation taken in the view equals its original baseline is the
   relation P-VIEW (§9.8 N7); each run's comparison is evidence for that run only, never a qualification of the design.
   A difference keeps the full observation and refuses (v5 `retain_observation`)."
4. Last paragraph: "(the idmapped `/run/user/1000`)" reads "(the host's `/run/user/1000`)".

### 8.5 Vault scope and the original backup semantics [correction: W1-V7-EVIDENCE-RESTORE]

- **What v5 did**: dispatch ran `project-vault pin <run directory>` and `project-vault status` before launch
  (S:1562-1563). The run directory held every record, the snapshot, the recipe and, after the run, every native output;
  the vault's later snapshots therefore covered the complete run as it then was.
- **What v8 pins**: P_exp(g), `g_rec/export`, and the adoption exports of the bound adoption, by v5's own calls, by F
  as `sicarii`, at M10 and D9, with the authentic HOME, configuration, user bus, reserve and queue (as v7). They must
  succeed or the stage refuses, as in v5.
- **What the pinned tree contains** (the equivalent capture): the v7 exports with their payload packs, and for every
  ended attempt A the **complete capture** `capture-<A>/` (§15.3): the whole generation tree (the recipe, every
  native output and partition entry, `tmpdir/`) with every entry's bytes and complete metadata; every raw torn or
  uncommitted record and marker of A; the whole `fallback.journal` file; every channel segment and continuation; W2's
  files. W writes it after A's holder event (§9.8 N4), so no target can change the captured entries any more, and
  before the attempt's terminal record; each later attempt adds its own capture, as later vault snapshots of v5's run
  directory saw its later state.
- **What is not equivalent, stated**: the originals in g, g_rec and P_ado(I) remain unreadable to `sicarii` and are not
  backed up; the capture is a copy, with W-owned inodes, export modes and ACL, and records each original's identity
  and metadata as data. A reader restores the bytes and the recorded metadata, not the original inodes. Whether this
  is "an exactly complete independent equivalent capture" for every original backup consumer is the obligation
  V-BACKUP of §21 C1, OPEN until the restore exercise of §13.1 (V-VAULT, amended) passes and is reviewed.
- **Capacity**: the capture's bytes and the full-restore peak enter Gate 0 (§14.7).

### 8.6 Input classes (v2 §6.1 carried; the re-review closed W1-READ-ACCESS)

CARRIED from v7: lines 1400-1421, 2023 bytes, sha256 `3ec9d7f237addb503a8f3a90434741ae57e7386139ae3ab5b5a06271ae25dd1f`.

## 9. Participants, waits, launch gating, terminal ownership and recovery [corrections: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE, W1-GENERATION-PROTOCOL; gap: participants-and-recovery]

CARRIED from v7: lines 1422-1423, 189 bytes, sha256 `d1843b7e7e7bee1fec119a7314ce98958f5e46327d872070510c73a6b1c90a01`.

### 9.1 Participant set and schemas

CARRIED from v7: lines 1424-1449, 2226 bytes, sha256 `bb6878ba3ff06de0beee08216c93ad10d2e4d4e483b8fdab0c693cb757e15502`.

### 9.2 Waits, reaping and relay

CARRIED from v7: lines 1450-1467, 1714 bytes, sha256 `6c4a383502ee74cabb5b597ae8220ba1d86122fa6d12400adfb30845910dc11f`.

### 9.3 Launch gating [corrections: W1-V7-C3-DATA, W1-V6-C1-DATA, W1-V6-SCAN-STATE; v6: W1-V5-PROTOCOL-REFUSALS, W1-V5-REVOCATION-CONFINEMENT; v5: W1-PROTOCOL-FAILURE-STATES, W1-CUSTODY-CLOSURE; v4: W1-GENERATION-PROTOCOL]

AMENDED from v7: lines 1468-1602, 13868 bytes, sha256 `e6a4fc9f200ee99324f75d622f4713783977dcb3e2fa34605e7cc9646f97e7be`.
Amendments:
1. **G3**, W's verification of the `RL_IDENTITY` frame, reads after "the census RL took before the view": "the
   namespace inodes and IDs (user, mount, network: `/proc/<pid>/ns/*` inode numbers and `NS_GET_MNTNS_ID`); U8's owner
   (`NS_GET_OWNER_UID`, equal to W) and maps (`0 0 4294967295` for uids and gids, JACKAL exact, parsed `2^32-1`); M_run's
   maps (`W 1000 1` for uids and gids); the run-path mode (`bind` or `skeleton`) with, for `skeleton`, the ancestor D,
   the created directories and the re-attached entries; every new mount's ID, root `[dev, ino]` and attributes as
   `statmount` reports them; the root and cwd checks of §12.2 step 12; the Landlock ruleset digest; and the
   credentials and capability sets RL holds just before its `exec` (uids and gids 1000 in all positions, the groups
   and the bounding set F recorded, every other capability set zero, `NoNewPrivs: 0`, `Seccomp: 0`)". W commits it as
   `launcher-rl-identity.json`. The rest of G3 is unchanged.
2. **G4** reads: "L: first act, identity, argv grammar; requires uid and gid 1000, a user namespace whose owner is W
   and whose maps are `0 0 4294967295`, its cgroup to be `/user.slice/user-1000.slice/<U>` with U derived from its
   argv, fd 0 a socket and fds 1-2 regular files; the rest as v7."
3. **C1** reads, for its namespace facts: "uid and gid 1000; `NS_GET_OWNER_UID` of `/proc/self/ns/user` equal to the
   compiled W (in the initial namespace it is 0, so this distinguishes U8); `/proc/self/uid_map` and `gid_map` equal to
   the compiled identity line; its cgroup equal to `/user.slice/user-1000.slice/wlscratch-<g12>-<A>.scope`". Everything
   else in C1 is v7's; C1 still uses only compiled expectations, its argv and kernel observations.
4. **C2** (correction W1-V7-C3-DATA): `RECORDS` carries, in this exact order, the committed bytes of `launch.json`,
   `admission.json`, `reservation-intent.json`, `reservation.json`, `launcher-intent.json`, `materialization.json`,
   `lead-adoption.json`, **`launcher-rl-identity.json`** and the lead module, each as `{name, sha256, bytes, marker}`
   where `marker` is the descriptor of its committed close marker (Appendix B.4, amended). C requires: exactly that
   key set and order; every sha256 equal to the bytes delivered and to the digest its marker descriptor records;
   `launcher-rl-identity.json` committed (W commits it in G3, before `GO`, so its marker precedes `RECORDS` in the
   attempt journal, and `RECORDS` carries the journal head that includes it); the record's pid and start time equal
   to C's own (C is RL's stage-2 process after two `exec`s); the record's view facts equal C's own independent
   observations (§12.2 step 12: namespace inodes and IDs, the root mount's `statx` mount ID and `[dev, ino]`, the
   binds' IDs, roots and attributes through `statmount`, the run-path mode). A missing record, an extra or reordered
   key, a digest mismatch or an observation mismatch makes C send `CHILD_REFUSAL` in state `RECORDS` (stage
   `records`) and exit without spawning. The C1/C2 separation is unchanged: no fact that only `RECORDS` delivers is
   checked before it.
5. **C3** reads: "C opens the view's `source/` at the run path with `O_DIRECTORY|O_NOFOLLOW|O_NOATIME` and requires
   its `[dev, ino]` to equal the seal's source identity, the opened directory to be a mount root
   (`STATX_ATTR_MOUNT_ROOT`) and its `STATX_MNT_ID_UNIQUE` mount ID to be the bind ID named in the delivered
   `launcher-rl-identity.json`; the same for `TMPDIR` and g/tmpdir's identity."
6. **C6** adds: the readback of every process attribute of §8.3 against `launch.json`'s `process_attributes`; a
   mismatch refuses (it can arise only if RL misbehaved or a premise failed).
7. **C7 and C10**: the census is that of §9.4 (v8); "CRED" is withdrawn. C10 also performs §4.5 item 4.
8. **C8**: "W's CRED passes" is withdrawn; W's half is the manager check of §9.4.
9. Every "within the control deadline" reads "before EOF" (§7.4).

### 9.4 The census, holder state, known-terminal ownership and the release rule [corrections: W1-V7-HOLDER-STATE, W1-V6-SCAN-STATE, W1-V6-PRESERVE; v6: W1-V5-REVOCATION-CONFINEMENT, W1-V5-PRESERVATION; v5: W1-CUSTODY-CLOSURE, W1-PROTOCOL-FAILURE-STATES; v4: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE]

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

**The holder event H(U)** (correction W1-V7-HOLDER-STATE) is defined and argued in §9.8 N4: K reads `populated 0` for
U, every task that was ever in U has completed its exit, and no logical mutation of an admitted entry can be performed
through a reference created by a task of U. Its absorbing property rests on P-CG, P-SETNS and P-IOEXIT.

| Point P | Observer | K expectation | Also required |
|---|---|---|---|
| parent stage (D8) | RL (stage 1, before O's view), then O | U absent; O's scope holds exactly O; every other RL scope absent or `populated 0` | M by W (C4-like half); the original walk rules |
| child stage (C7) and final pass (C10) | C | U holds exactly C; every other RL scope absent or `populated 0` | M by W at C4 and C8 |
| after stage (D17) | O, for W | O's scope holds exactly O; U absent or `populated 0` | v5's terminal predicate (below) |
| recovery round (§9.7) | O, for W2 | as at the after stage | v5's terminal predicate |
| release (D18, RC4) | F under the window lock | not taken | v5's terminal predicate only |

**Known-terminal ownership** of attempt A is v5's `owned_terminal` predicate (S:1373-1415), unchanged in meaning and
evaluated over v8's participants: U has ended in the manager (`LoadState` `not-found`, or `ActiveState` `inactive` or
`failed`); its cgroup is absent or empty; every recorded participant pid (L, C, T) is absent from `/proc`; no process
names the attempt (v5 `processes_naming`); the launcher pid is known if a launch was made; no child record is
unresolved. The evaluation is ordered and conservative: manager state, then cgroup, then pids and process names, then
manager state again; terminal only if both manager reads show ended and every other term holds. A manager that lags
the kernel only delays the classification (a hold, exactly as v5 held while its manager reported the scope active);
no instantaneous equivalence is used. W's after stage or W2's recovery establishes it.

**Release rule, procedure, hold, window-write failure and the window protocol**: v7's text (§9.4 of v7, from "Release
rule" to "a refusal costs nothing") applies unchanged, as carried text identified by v7 unit 9.4's hash
`a41ff848d353f97b321eefa24fd7caf0cdb7d614a44d7fdc260b97cc87410e74` (v7 lines 1652-1695). Under §0.6 rule 4, "F waits
for that answer at most the control deadline" reads "F waits for that answer until it arrives or the channel reports
EOF", and the release-record deadline after `RELEASE_DONE` reads "until EOF". No condition is added to the release:
neither H(U) nor any durability state is a release condition; release follows v5's predicate.

**Does the census refuse a case that v5 admitted?** v5 refused while an earlier frame scope was active in its manager
(S:1156-1163). v8 refuses when M shows an earlier RL scope live (v5's rule in the new manager) or K shows one populated.
Whether K ever refuses where M would not is premise P-MGR; §21 D1 keeps that state OPEN.

### 9.5 Failure table [corrections: W1-V6-COMMIT-AMBIGUITY, W1-V6-CATALOGUE; v6: W1-V5-PROTOCOL-REFUSALS, W1-V5-REVOCATION-CONFINEMENT, W1-V5-JOURNAL-FAILED-CLOSE; v5: W1-PROTOCOL-FAILURE-STATES, W1-CUSTODY-CLOSURE, W1-JOURNAL-CONTINUATION, W1-SETUP-IDENTITY, W1-IMAGE-OBSERVATION]

AMENDED from v7: lines 1705-1746, 8230 bytes, sha256 `e50b3781c1482863c0e0b3818a82759c16edcccf68fda8de562f29651689a5f7`.
Amendments: rows citing CRED, a deadline, `g/tmp` or the lead-created mount point are withdrawn; rows citing P-CENSUS
cite §9.4's K and M. The row "The close marker's link succeeded, then its directory `fsync` or its post-link join
fails" reads "… the record is committed for every consumer with sync provenance `failed` (§10.5); success withheld; no
release effect". New rows:

| Event | Outcome |
|---|---|
| RL step 11 cannot build the run-path presentation (a mount call fails) | RL exits before `RL_IDENTITY`; W refuses before launch (RP0); the error and step are recorded. A refusal in a state v5 accepts unless the failure is caused by a premise failure; §21 D2 |
| C's run-path alias check fails (§4.5 item 4) | `CHILD_REFUSAL`, RP1; v5-class pre-launch alias refusal |
| C's `RECORDS` key set, order, digest or view-fact join fails (§9.3 C2) | `CHILD_REFUSAL` in `RECORDS`, nothing spawned |
| The writer dies after a close marker's link and before reporting its sync outcome | the record is committed; provenance `unobserved` for every consumer (§10.5) |

### 9.6 Reboot

AMENDED from v7: lines 1747-1769, 2116 bytes, sha256 `06533416b10f8f1cbda45312a42525c9d390f69ab8822edb7764f4c37babc5a7`.
Amendment: a post-reboot reader classifies each committed record's sync provenance by §10.5: a close marker present
after the reboot is `present-after-reboot` (its entry reached the disk), in addition to whatever provenance a
committed later record attests; it never infers `observed` from presence alone.

### 9.7 Writer-death recovery and the post-writer W2 [corrections: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE]

AMENDED from v7: lines 1770-1813, 4093 bytes, sha256 `cfcab530221830dabf11e41d3c0d09096f5be5f59fdfedaa47d944ce235a4cb4`.
Amendments: W2 classifies each committed record's sync provenance by §10.5 (it never re-derives `observed` by its own
`fsync`, because a later `fsync` need not report an earlier write-back error); W2's 10 s intervals pace its rounds and
refuse nothing (§0.6 rule 4); W2 makes the complete capture of §15.3 for A after H(U), if W did not.

### 9.8 Custody by the same-identity view [corrections: W1-V7-ARCHITECTURE, W1-V7-HOLDER-STATE, W1-V7-READ-EFFECTS, W1-V7-PROBES, W1-V7-PREMISES; v7: W1-V6-PRESERVE, W1-V6-READ-MUTATION, W1-V6-SCAN-STATE]

v7's §9.8 is replaced. Its K0 statement stands as the review ruled it (§22.2): an obstruction for the unprivileged
DAC architecture and already-shared writable descriptions, not a universal theorem.

**N0. The obligation and its terms.** From the final pass to T's `exec` (V5-B01, second sentence) and across every
frame mutation (V5-B02):
(a) no principal outside the attempt's own process tree, other than root and W, holds a *usable reference* to, or a
*usable name* for, an admitted entry, or can obtain one;
(b) no logical mutation of an admitted entry can be performed by an earlier attempt's holder after its holder event;
(c) every frame mutation lies in T or is v5's window protocol, and every other frame-caused effect is in the
inventory of N5-N6 with its classification.
A *reference* to an entry E is an open file description of E; a `struct path` naming E held as a process's root or
cwd; a mapping of E; an `io_uring` fixed-file registration or an in-flight request naming E; an AIO request on E; an
in-flight `SCM_RIGHTS` entry for E. It is *usable* by a principal P if P can perform an operation through it (read,
write, truncate, metadata change, re-open, mapping store, pass it on). A *usable name* of E for P is a path whose
resolution by P, in P's mount namespace from P's root or cwd, reaches E. A string that resolves elsewhere for P is not
a name of E (review: "A leaked string is not automatically a usable inode name").

**N1. Push routes** (a process of a view hands a reference to a process outside its tree).
- Inherited descriptors: a view process holds only `/dev/null`, its stream files and, for L, C and O, its channel
  socket to W (C11); T receives `/dev/null` and its two stream files. W reads its sockets with a zero-length control
  buffer, so a descriptor sent by L, C or O is truncated (`MSG_CTRUNC`), never installed, and recorded as a channel
  failure.
- Pathname UNIX sockets, outward: the domain handles `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` and grants it nowhere. The
  installed `landlock.h` (2026-10-05T15:51:43Z): "On UNIX domain sockets, this restricts both calls to connect(2) as
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
- Other descriptor-carrying interfaces: binder needs a binder device (none exists; observed 2026-10-05, v7 Appendix G;
  and a binderfs mount is a mount, which Landlock forbids); `IORING_OP_MSG_RING` needs a descriptor of the receiving
  ring, which only an existing channel could provide; `pidfd_getfd` and `/proc/<pid>/fd` are pulls (N2); signals and
  file contents carry no reference.
- So every process that can receive a reference from a view process is in the same view and scope, or is W, which
  discards it.

**N2. Pull routes, grounded in the controlling rule** (correction of v7 c8; review W1-V7-ARCHITECTURE).
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

Applied to A1 (initial namespace, euid 1000, no capabilities) and T (host uid 1000 in U8, a child of the initial
namespace owned by W): the uid half of `__ptrace_may_access` passes; T's dumpability is T's choice; commoncap then
denies, because the namespaces differ and `ns_capable(U8, CAP_SYS_PTRACE)` walks U8 (level 1, parent initial, owner W
≠ 1000) to the initial namespace, where A1's effective set lacks `CAP_SYS_PTRACE`. For A1 in a user namespace Ua that it
created: U8 is not at a level above Ua's, or its ancestry does not contain Ua, so the walk denies. For T's own nested
namespaces (owner 1000, parent U8): the owner rule applies only to a namespace whose parent is the caller's, which is
never the case for A1. The same rule denies T access to every outside process (the target namespace is the initial
one, not above U8), and denies T of one attempt access to a target or observer of another (sibling namespaces).
Within U8 the first branch applies (same namespace, every view process has an empty permitted set), subject to Yama
`ptrace_scope=1` for attach and to Landlock (same domain).

Operations and their modes (upstream readings, P-KSRC): `/proc/<pid>/{fd/*,cwd,root,exe}` open and `readlink`
(`call_proc_get_link`, `PTRACE_MODE_READ_FSCREDS`), `/proc/<pid>/fdinfo/*` (`proc_fdinfo_permission`,
`READ_FSCREDS`), `/proc/<pid>/ns/*` (read), `/proc/<pid>/{mem,environ}` (`mm_access` with `FSCREDS`; attach for
`mem`, read for `environ`), `pidfd_getfd` (`__pidfd_fget`: `PTRACE_MODE_ATTACH_REALCREDS`, under `exec_update_lock`),
`ptrace` attach and seize (`PTRACE_MODE_ATTACH_REALCREDS`), `process_vm_readv`/`writev` and `kcmp` (ptrace modes),
`/proc/<pid>/map_files/*` (`checkpoint_restore_ns_capable(&init_user_ns)`): each needs the ptrace check above or a
capability in the initial namespace, so each fails for A1 and A3. Listing `/proc/<T>/fd` passes DAC
(`proc_fd_permission`) and reveals descriptor numbers only. W holds `CAP_SYS_PTRACE` over U8 by the owner rule; W is
trusted base and its reviewed code never uses it (a code-review item, §16). An unprivileged fanotify group reports
file identifiers, not descriptors, and marks only inodes its owner reaches by path, which excludes g.

**N3. Names.**
- Paths: on disk every admitted entry lies below g, which grants search to W and root only (§6.3). The binds exist
  only in view mount namespaces (each owned by the initial user namespace, with private propagation, P-PROP), which no
  outside principal can enter (`setns` needs `CAP_SYS_ADMIN` there) or reach through `/proc/<pid>/root` (N2).
- New names: a `link` or `rename` whose paths lie in different mounts does not succeed (P-XMNT, corrected), so every
  name of an admitted entry made by a view process stays below g/source or g/tmpdir. Landlock forbids every mount,
  unmount, move and `pivot_root` to a domain process, in every user namespace (P-LOCK), so no view process can attach
  a subtree of a bind elsewhere; the nested mount namespaces a view process can still create (by `unshare`) hold
  locked copies usable only by processes of the attempt's own tree.
- Run-path ancestors: the path above the bind is `sicarii`'s (§3.3). A rename by A1 moves names, not the bind; before
  the spawn C refuses an alias (§4.5 item 4); afterwards it is residual R3b (§2.4).
- File handles: in the installed-version-unverified upstream `may_decode_fh`, an unprivileged caller may decode only a
  directory handle, only through a mount whose namespace it administers and which has no locked child mounts, only
  with `CAP_DAC_READ_SEARCH` in its own namespace, and only if every ancestor from the decoded directory up to that
  mount's root has an owner and group mapped in its namespace. Every admitted directory has the W-owned g (and the
  root- or W-owned directories above it) among its ancestors on disk; W and 0 are mapped in no namespace that A1 can
  create (A1 maps 1000 and its subordinate range 100000-165535). Premise P-FH.

**N4. The holder event** (correction W1-V7-HOLDER-STATE). For an RL scope U, H(U) holds at time t iff
(1) K reads U absent or `populated 0` at t;
(2) every task that was ever a member of U has completed `do_exit`;
(3) no logical mutation of an admitted entry can be performed after t through a reference created by a task of U.
*From (1) to (2):* a task leaves a cgroup only by exiting or by migration, which needs write access to the
destination's `cgroup.procs` and to the common ancestor's; below `user-1000.slice` those files are root-owned, and the
common ancestor of an RL scope and any other cgroup is `user-1000.slice` or above (P-CG). RL never migrates a task out;
root's other actions are trusted base. `populated` is cleared only after a task's cgroup exit, which follows its
`exit_files` and `exit_fs` in the upstream exit order (P-CG, P-IOEXIT).
*From (2) to (3):* a logical mutation of a file needs a system call by a live task, an `io_uring` request, an AIO
request, or a store through a shared writable mapping by a live task. No task of U is alive. Every reference a task of
U created is held by tasks of U, by sockets only they could read, by rings or AIO contexts of U, or by kernel objects
reachable only through those (N1-N3); none is held by a principal outside the tree. By the upstream exit path, a task's
`io_uring` requests are cancelled or completed before its exit proceeds, and a memory context's AIO requests are
waited for when its last user releases it. **One gap is stated, not closed:** an outside process that reads
`/proc/<pid>/cmdline` holds the target's memory context briefly (no ptrace check guards that read), so the final
release, with the AIO wait, can run in that process after (1); a direct-I/O write that a task of U issued before its
exit may then complete after (1). Whether any write of U can complete after `populated 0` is premise P-IOEXIT, stated
exactly in N7; if it fails, the holder boundary must be redesigned (no exception). Write-back of pages already dirtied
is physical, not logical: the content was set by the store.
*Absorbing:* once (1)-(3) hold they hold forever after: no task can join U (only a member can fork into it, and only
root migrates), no task can join U's U8 (`setns` needs `CAP_SYS_ADMIN` in U8, P-SETNS), and RL never reuses a scope
name or a namespace.
H(U) is not observed directly; K's `populated 0` observes (1), and (2)-(3) follow from the named premises. A
populated-zero observation is not presented as evidence of (3).

**N5. Frame-caused privileged and control-plane effects** (correction of v7 N5; review W1-V7-READ-EFFECTS). Every
effect outside T caused by RL, by the sudo rules or by the system manager on the frame's request, with its
classification. "Frame-own object" means a kernel object the frame creates for the attempt, which no other principal
uses and which ends with it; the author classifies such effects as outside the location-custody question, which the
reviewer may reject, so V5-B02 stays OPEN for them until ruled.

| Effect | Cause | Original counterpart | Treatment |
|---|---|---|---|
| transient unit `<U>`: unit state in PID 1, a transient unit file under `/run/systemd/transient/`, the cgroup | RL's `systemd-run --scope` | v5's `systemd-run --user --scope`: the same objects in `sicarii`'s manager and `/run/user/1000/systemd/transient/` | same class as v5; OPEN for classification |
| journal entries about `<U>` | the system manager | v5's user-manager entries | reduced: `LogLevelMax=warning` drops the manager's informational messages about the unit (installed `systemd.exec(5)`: "applied to any log messages … written by the system or user manager processes in reference to this unit"); warnings and errors remain; OPEN |
| sudo's syslog, audit and PAM-session effects | S1, S2, S_O, S3 | none in v5 | removed by `Defaults!<entry> !log_allowed, !pam_session, !pam_setcred, !use_pty` on the two frame rules (§11.5; installed `sudoers(5)`: `log_allowed` "will log commands allowed by the policy to the system audit log (where supported) as well as to syslog and/or a log file"); sudo's PAM account phase remains (reads only, P-SUDO); OPEN until P-SUDO's before/after capture shows no write |
| sudo timestamp and lecture files | S1, S2 | none | not created for `NOPASSWD` rules without authentication (P-SUDO) |
| U8's and M_run's `uid_map`, `gid_map`, `setgroups` writes | RL, on its own helper processes | none | frame-own objects |
| copied mount namespace, its `nosuid` and propagation changes, the binds, the skeleton `tmpfs` | RL | none | frame-own objects; no host filesystem write |
| network namespace and its loopback state | RL | none | frame-own object |
| Landlock domain, credentials, limits, `oom_score_adj` of its own process | RL | v5 set its own limits | frame-own |
| per-user kernel accounting of the view (user namespaces, inotify, mount namespaces, …) | the view's processes, charged at the initial level to U8's owner W | charged to 1000 in v5 | a change (§12.3 V13), not a write |

**N6. Read-side effects of the frame** (correction W1-V7-READ-EFFECTS). Every causal read route of every frame process
with its effect. `O_NOATIME` is permitted to the owner of the file (through the mount's idmap) or to a holder of
`CAP_FOWNER`.

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
| R-m | W, W2: the complete capture of g after H | `O_NOATIME` (owner on disk) | none | closed |

Readable foreign-owned inputs stay accepted (R-d, R-e'). W1-V6-READ-MUTATION and V5-B02 stay OPEN for R-d, R-e', R-f,
R-h, R-i and R-j; no root-trust, pseudo-filesystem or target-residual relabelling is used.

**N7. Premise and dependency register** (correction W1-V7-PREMISES; the one complete register; §18.6 points here).
Every row is NAMED_UNESTABLISHED. Discharge kinds: **S**, a source reading matched to the installed build (never an
upstream reading alone); **P**, a probe, which can refute a universal statement and never establishes one; **T**, a
trusted-base exclusion, which is a threat-model assumption and not a test result. **If any premise fails, W-1 must be
redesigned for it; no exception is taken and no accepted case is narrowed.**

| Premise | Statement | Discharge | Probe (§13, §13.1) |
|---|---|---|---|
| P-KSRC | the installed 7.2.6-1-aarch64-ARCH kernel's `commoncap.c`, `ptrace.c`, `pid.c`, `fs/proc/*`, `fhandle.c`, `namespace.c`, `exit.c`, `io_uring`, `aio.c`, cgroup and Landlock code behave as the upstream v7.2 readings quoted or summarized here | S (Arch ARM source package for the exact build and its patches) | none possible as a universal discharge |
| P-PTRACE | N2's operations fail for every non-root principal outside the view, from the initial namespace and from namespaces it creates, and for view processes towards outside processes and other views | S, P | P-PTRACE (corrected controls, §13.1) |
| P-NOCAP | no view process ever holds a capability in U8 or an ancestor of U8 | S (exec credential computation under `nosuid`; `setns` rules), P | P-NOCAP |
| P-NOSUID | every mount of the view (the copies, the binds, the skeleton and its re-attached entries) is `nosuid`; copies into nested namespaces keep the flag locked; set-ID bits and file capabilities take no effect on `exec` | S, P | P-NOSUID |
| P-SETNS | a process joins U8 only by inheritance from RL's stage-2 process, or by `setns` with `CAP_SYS_ADMIN` in U8 (root, or an euid-W process of the initial namespace, which only runs reviewed code) | S, T | P-NS |
| P-CG | `populated` semantics; no task enters or leaves an RL scope except by fork inside it, exit, or root migration; `io_uring` workers are members of their task's cgroup; the `cgroup.procs` files of `user-1000.slice` and of RL scopes are root-owned | S, P | P-CG |
| P-MGR | the system manager never reports an RL scope inactive, failed or not-found while its cgroup is populated | S (systemd 261 scope code), P | P-MGR |
| P-SLICE | systemd 261 accepts a transient system scope in `user-1000.slice`; the scope stops with that slice, as the original user-manager scope stopped with `user@1000.service` | S, P | P-SLICE |
| P-ROOT | `unshare(CLONE_NEWNS)` copies the mount tree and moves the caller's root and cwd to the copies; descriptors opened before keep the original mounts | S, P | P-ROOT |
| P-MSET | `mount_setattr(AT_RECURSIVE)` and `OPEN_TREE_CLONE` change or copy mount structures without calling into any mounted filesystem (no FUSE contact) | S | — |
| P-SKEL | the skeleton construction of §12.2 step 11 (a `tmpfs` over D, the created directories, re-attached clones of D's entries, symlink entries included) succeeds with no host write and shows each entry as the host shows it | S, P | P-SKEL |
| P-PROP | no mount event propagates between a view and the host in either direction | S, P | P-PROP |
| P-LOCK | Landlock denies `mount`, `umount2`, `move_mount`, `fsmount` attach and `pivot_root` to every domain process in every user namespace; nested copies lock the binds and the skeleton | S, P | P-LOCK |
| P-LL | (corrected) with handled `{MAKE_SOCK, RESOLVE_UNIX, REFER}`, `REFER` granted on `/` and `MAKE_SOCK` on the two bind roots: `RESOLVE_UNIX` as quoted in N1; a socket can be created, renamed or linked only into a directory beneath a bind (`EACCES` elsewhere); for every other file type, a `rename` or `link` between two directories of one mount meets `REFER`'s conditions (both directories have `REFER`; the only handled `MAKE_*` right is `MAKE_SOCK`; the handled rights of all directories of one mount are equal, so no access is gained) and succeeds or fails as without Landlock | S, P (each case, real directories, sockets and controls) | P-LL |
| P-XMNT | (replaces P-XDEV) a `link`, `rename` or `renameat2` whose two paths resolve to different mounts does not succeed; its errno is `EXDEV` only when resolution and every earlier check pass, and Landlock's `EACCES` takes precedence | S, P | P-XMNT |
| P-FH | N3's file-handle statement for every handle type and mount configuration A1 or a view process can create | S, P | P-FH |
| P-IDMAP | M_run shows on-disk W as 1000 and stores 1000 as W; unmapped ids appear as the overflow id and cannot be created; `O_NOATIME`'s owner test is made through the idmap | S, P | P-IDMAP |
| P-NETNS | abstract UNIX sockets are scoped by network namespace; joining the view's needs `CAP_SYS_ADMIN` over the initial user namespace | S, P | P-NETNS |
| P-IOEXIT | no logical mutation of a file by an `io_uring`, AIO, direct-I/O or other request of a task of U can take effect after K reads U `populated 0` (N4 states the known gap) | S | P-IOEXIT (refutation only) |
| P-UCOUNT | the view's per-user namespace accounting is charged at the initial level to (initial namespace, W) | S, P | P-UCOUNT |
| P-NOATIME | the `O_NOATIME` opens of R-a, R-b, R-c, R-e, R-k and R-m change no atime | S, P | P-NOATIME |
| P-PSEUDO | reads of `/proc`, `/sys` and cgroupfs change no stored state | S | — |
| P-SUDO | with the options of §11.5, sudo 1.9 writes nothing (no syslog, audit, I/O log, timestamp or lecture file) for an allowed `NOPASSWD` frame command | S, P (before/after capture) | P-SUDO |
| P-LOGLEVEL | `LogLevelMax=warning` drops the manager's informational messages about the scope | S (systemd 261), P | P-LOGLEVEL |
| P-SIG | sudo's relay of signals to the frame commands, as v7 | P | P-SIG |
| P-ENOSPC, P-MOUNT, P-IMAGE | carried unchanged (§10.4, §14.5) | S, P | as v7 |
| P-SYNCPROV | an `fsync` failure is reported to the writer that issued it; a later `fsync` by another opener need not report an earlier write-back failure (why W2 never derives `observed`) | S | P-COMMIT |
| P-VIEW | (relation, not a kernel fact) every original observation taken in the view equals its original baseline for every original relevant context | S (producer code), with each run's comparison as evidence for that run only | per run |
| TOOL-CLOSURE | (sub-lemma of §21's relation) for each allowlisted action on the pinned toolchain, the observable outcome does not depend on any item of §12.3 | S (source to installed-binary correspondence, helpers, configuration) | engineering runs refute only |
| T-ROOT, T-W, T-RL | root, the kernel, the reviewed writer code and RL behave as reviewed | T | — |
| P-TMPAGE | withdrawn with its mechanism (v8 has no private `/tmp` and no tmpfiles rule); recorded here so that the register is complete | — | — |

**N8. What remains outside:** root and the kernel (R8); a writer instance running changed code (outside the threat
model); availability (R6); the target's own confinement outside g (R3) and its path lookups after the spawn (R3b).

## 10. Commits, journals, retries, durable fallback and durability-UNKNOWN [corrections: W1-COMMIT-JOURNAL-EXPORT, W1-DURABILITY-RELEASE; gap: commits-and-durable-channel]

CARRIED from v7: lines 1935-1936, 173 bytes, sha256 `b923c50c51930667776aced4d6d5b16a080102e4e056e61d0ade2fd420c1d98d`.

### 10.1 Commit primitive (N11) [corrections: W1-V7-SYNC-PROVENANCE, W1-V6-COMMIT-AMBIGUITY]

AMENDED from v7: lines 1937-1971, 3022 bytes, sha256 `a0774d3a37aabfb162c3f5386551ea377e7dc756fefebe7f9c2172dde18daa62`.
Amendments: steps 1-4 and the commit point are unchanged (**structural commit membership**: a record is committed
exactly when its close marker's link has happened). Every phrase of the form "committed …, with `synced: false`" or
"committed, unsynced" reads "committed, with sync provenance `failed`" and is governed by §10.5. Added after step 4:
"5. **Sync attestation.** The writer's outcome of step 4 (directory `fsync` and post-link join) is the record's sync
outcome. It is reported in `RECORD_COMMITTED {…, sync: "ok" | "failed", errors}` to F, and it is attested durably by
the writer's next committed record of the same journal, whose body carries `prior_sync: {name, marker_sha256, sync}`
for every record committed since the previous attestation (Appendix B.3). A record's sync outcome that reaches neither
F nor a later committed attestation is **unobserved**."

### 10.2 Markers, journals and the committed chain [corrections: W1-V6-COMMIT-AMBIGUITY; v6: W1-V5-JOURNAL-FAILED-CLOSE; v5: W1-JOURNAL-CONTINUATION]

AMENDED from v7: lines 1972-2085, 11650 bytes, sha256 `f78bc026cea49fb212d14355029a3ac6b1173c045ed3e59cd6b1f6d0cf7710fc`.
Amendment: every statement that a committed record "carries" or "travels with" `synced: false` reads: "carries the sync
provenance that §10.5 assigns to it for the consumer concerned". The continuation rules (closed as
W1-JOURNAL-CONTINUATION) are unchanged.

### 10.3 Retries and downgrade

CARRIED from v7: lines 2086-2091, 369 bytes, sha256 `2b275b998e8c39b306421b0c6400ea8c12528d2b9741410c51f99ac4bca59990`.

### 10.4 The fallback journal: immutable allocation, append-only slots [correction: W1-COMMIT-JOURNAL-EXPORT]

CARRIED from v7: lines 2092-2135, 4467 bytes, sha256 `45c96fa1f94741a0a04242424778df566daa7cd7914d7c8ff2cc04be34e7d85f`.

### 10.5 Durability-UNKNOWN and sync provenance [correction: W1-V7-SYNC-PROVENANCE]

Two separate facts are kept for every record name N: its **membership** (committed primary, committed retry,
`fallback`, `raw` or `unknown`, by §10.6's precedence; decided by markers and slots alone) and, for a committed record,
its **sync provenance**, one of:
- `observed`: a sync outcome `ok` reached the consumer through F's in-memory `RECORD_COMMITTED` (for F only) or
  through a committed attestation (`prior_sync`, §10.1 step 5) in the same journal;
- `failed`: an outcome `failed` reached it the same ways;
- `unobserved`: neither exists — in particular when the writer died after the close marker's link and before
  reporting or attesting its outcome (review W1-V7-SYNC-PROVENANCE);
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

If primary, retry and fallback all fail for a record, it is **durability-UNKNOWN** exactly as v7 §10.5 states
(`RECORD_UNKNOWN`, last-resort stderr, no success). A record whose provenance is `failed` or `unobserved` earns no
success credit, is not retried (it is committed; a retry would add a second committed version) and is reported in every
later record, in `FINAL` and in the exports. No hold, no effect on the window and no approval gate (§9.4).
Failure controls (§13.1 P-COMMIT, P-CHAIN): an injected directory-`fsync` failure (`failed`), the writer killed between
the marker's link and its report (`unobserved` for F, W2, a post-reboot reader and an export, consistently), and a
reboot after a linked but unsynced marker (absent marker: uncommitted; present: committed with
`present-after-reboot`).

### 10.6 Consumers (complete)

AMENDED from v7: lines 2150-2179, 3658 bytes, sha256 `2c1f196a73aa5e6fb60e91055b8e3edcb7f0c6aceff2764fc81016b02c05a092`.
Amendments: "A committed primary or retry carries its `synced` value" reads "… carries its sync provenance (§10.5)";
in the table, "with `synced`" reads "with its sync provenance", and "primary or retry and synced" reads "primary or
retry with provenance `observed`". Stream finality: "requires the census to show U absent or `populated 0`" reads
"requires K to show U absent or `populated 0`, which observes term (1) of H(U) (§9.8 N4)"; "(N1-N4)" is unchanged.

### 10.7 Exit statuses and success, per verb (N13, N14) [correction: W1-PROTOCOL-FAILURE-STATES]

AMENDED from v7: lines 2180-2217, 3924 bytes, sha256 `f7646af077f17d438c07a0641f6aefec1fc3af5f295bb9ee7e8e80a1b0bb7eea`.
Amendments: every "synced" condition of a success predicate reads "sync provenance `observed`"; every "unsynced" in a
non-success list reads "sync provenance `failed` or `unobserved`". The `dispatch` success predicate adds: "∧ the
complete capture of §15.3 committed for A". Exit codes are otherwise v7's.

## 11. Prestate and installation [corrections: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY; gap: prestate-and-installation]

CARRIED from v7: lines 2218-2219, 127 bytes, sha256 `554fcbe4c216f90ff9d4ae0b8672903c7d18685221dc80a7ec07dbc59d5df8cd`.

### 11.1 Rules used throughout

CARRIED from v7: lines 2220-2239, 1723 bytes, sha256 `0ad981bd44c1a4c63a85f56e89f7983c354e19b1eea1b5ab56eec3357a73463e`.

### 11.2 Numeric identity policy

AMENDED from v7: lines 2240-2254, 1210 bytes, sha256 `d07d96f31be7f06b3e6d6723d8163093f6e2d235b675989c22f57fa5f51b167c`.
Amendment: the policy applies to the single new identity W (uid and gid); R and GATE are withdrawn.

### 11.3 Prestate inventory (read-only; "lead" = unprivileged agent, "operator" = needs root)

AMENDED from v7: lines 2255-2302, 7394 bytes, sha256 `746b17ca012b7436847c99cb9ebd9186cd66384854d3b3456f74bb4c12257e50`.
Amendments: rows concerning R, GATE, `wlscratch.slice`, the tmpfiles rule and `/tmp`'s age (P26) are withdrawn. Rows
added (lead, read-only): P27, the cgroup2 limits and ownership of `user.slice`, `user-1000.slice`,
`user@1000.service` and `user@1000.service/app.slice` (`memory.max`, `memory.high`, `memory.swap.max`, `pids.max`,
`cpu.weight`, `cpu.max`, owner of each `cgroup.procs`); P28, `systemctl --user show` of `app.slice` and the user
manager's scope defaults (`DefaultCPUAccounting`…, `CPUWeight`, `IOWeight`, `TasksMax`, `OOMPolicy`, `ManagedOOM*`),
which fix the scope properties of §8.3; P29, the installed sudo's `sudoers(5)` text for `log_allowed`, `pam_session`,
`pam_setcred` and `use_pty` and the sudo version; P30, the lead's process attributes as F would record them (§8.3),
to check that each is reproducible by RL.

### 11.4 Staged atoms, the global state model and reconciliation [correction: W1-V7-COMPOSED-STATE; v7: W1-V6-COMPOSED-STATE; v6: W1-V5-RECONCILIATION-STATES; v5: W1-SETUP-RECONCILIATION; v4: W1-SETUP-PROBES-ROLLBACK]

v7 §11.4's staging (S-0), execution and status-handling rules (its first three bullets and the numbered rules 1-4 of
its execution bullet, v7 lines 2303-2340) are carried in substance; its claims that no atom undoes another and that
its vectors are all reachable states are withdrawn (review: failed `visudo -c` and `sshd -t` removed earlier
installed files). v8 replaces them with the following model.

**Atoms.** Each privileged object is an atom with an observable state. File atoms (the two sudoers files, the sshd
drop-in, every frame member, `setup-identities.json`, each image file) are installed in two steps: the reviewed bytes
are written to an inert staging name in the destination directory (`.<name>.new`, which neither sudo's `includedir`
nor sshd's `Include *.conf` reads, nor the frame), synced, compared byte for byte with the staging copy, and then
renamed to the final name (`mv -T`, atomic). A file atom's observable state is therefore one of: `absent`;
`staged-partial` (the inert name exists with a proper prefix or other bytes); `staged-equal`; `installed-equal` (final
name, reviewed bytes, owner, mode); `installed-other` (final name, other bytes: never produced by a script; a defect or
an outside change); and, for an atom deactivated by a failed check (below), `deactivated-equal` (the inert name holds
the reviewed bytes after a rename back). Directory, account, group, ACL and mount atoms have the state sets of v7 §11.4
(absent, created with each attribute checked, attribute partial, complete). An image file atom adds `allocated-partial`
(size below the reviewed size), `allocated` and `formatted-partial` (a superblock that does not match the reviewed
UUID, geometry or features) before `formatted-equal`.

**No script removes an installed atom.** A failed combined check (`visudo -c` after S-D's renames, `sshd -t` after
S-E's) does not delete files: the script renames each atom it just activated back to its inert name
(`deactivated-equal`) and stops. That is the only backward transition a script makes, it is atomic per atom, and it
appears in the global table. Removal of any object happens only in S-R or in rollback, by explicit operator choice,
and only after full-byte equality with the reviewed bytes (a prefix is never "equal").

**Service co-effects.** `systemctl daemon-reload` and `systemctl reload sshd` change in-memory configuration. Each is
an atom whose state is observed (`systemctl show -p NeedDaemonReload` of the mount units with images; `sshd -T` for
the effective `DenyUsers`), never inferred from a log. Enablement symlinks of the image mount units (images only) are
file atoms.

**The global state.** The state of the setup is the vector of every atom's observed state, read in one S-R capture
(each producer under `check_out.py`). The global table lists, for every script and every step boundary and every
interruption point inside a step (between the staging write and its sync, between the sync and the rename, between
two renames, during an image allocation or format), the vector that can result, including the deactivated vectors.
S-R classifies an observed vector as exactly one of: a table vector (continue from the next step, or reverse
step by step to the empty vector); `installed-other` or any vector not in the table (stop: an outside change or a
defect, reported with the full capture, and the operator decides; this is the original reserved operator decision, not a
new gate). Every ordinary partial state is a table vector with a defined continuation and reversal; none is treated as
an exception.

**Image partial states** (only with images): a `allocated-partial`, `allocated` or `formatted-partial` image file is
never mounted, never listed in `setup-identities.json` and reversed by S-R by recording its size and first and last
blocks' digests and removing it; `formatted-equal` continues.

**Rollback is its own machine** (§15.1, amended): an evidence-retaining rollback grows from runtime state (generations,
records, exports, a locked and expired account), which setup's inverse vectors do not describe. Its states are those
of §15.1's steps, each with a before and after capture, and its postconditions are stated there.

### 11.5 Setup scripts (templates; texts and digests become exact in the concrete inventory) [corrections: W1-V7-COMPOSED-STATE, W1-V6-COMPOSED-STATE; v6: W1-V5-RECONCILIATION-STATES; v5: W1-SETUP-RECONCILIATION, W1-SETUP-IDENTITY, W1-CUSTODY-CLOSURE; v4: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY]

AMENDED from v7: lines 2418-2818, 23350 bytes, sha256 `547c43f3dc06aa2cd44ba799719feda46e70c8f2cf95febf8871c024c7c48ca4`.
Amendments:
1. **S-A** creates one group and one account (W); every step for `wlscratch-run` and `wlscratch-gate` is withdrawn.
2. **S-B** creates no `tmp/` anywhere; the `user:1000` ACL entries are v7's.
3. **S-C** installs every frame member by the staged-rename rule of §11.4.
4. **S-D** installs the two sudoers files by the staged-rename rule. Their reviewed bytes become:
   ```
   Cmnd_Alias WLSCRATCH_W = /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py *
   Defaults!WLSCRATCH_W !log_allowed, !pam_session, !pam_setcred, !use_pty
   sicarii ALL=(wlscratch) NOPASSWD: WLSCRATCH_W
   ```
   in `wlscratch-frame`, and in `wlscratch-rl` (renamed from v7's `wlscratch-run`):
   ```
   Cmnd_Alias WLSCRATCH_RL = /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py *
   Defaults!WLSCRATCH_RL !log_allowed, !pam_session, !pam_setcred, !use_pty
   wlscratch ALL=(root) NOPASSWD: WLSCRATCH_RL
   ```
   Each is checked with `visudo -cf` on its staged name, renamed into place, and then the whole configuration is
   checked with `visudo -c`; on failure both are renamed back (`deactivated-equal`) and the script stops (exit 40).
   That the installed sudo honours these options as `sudoers(5)` states is P-SUDO.
5. **S-E** installs `DenyUsers wlscratch` by the staged-rename rule; on a failed `sshd -t` the drop-in is renamed back
   and the script stops (exit 50); then `sshd -T` and the reload as v7.
6. **S-F** (the slice unit and the tmpfiles rule) is withdrawn; nothing replaces it.
7. **S-H** omits the slice and tmpfiles identities; **S-I** captures, in addition, P27-P30 (§11.3).
8. **S-R** uses the global table of §11.4.

### 11.6 Post-setup verification

AMENDED from v7: lines 2819-2832, 1096 bytes, sha256 `5f165da0bcdc34798a12b60342a2ba3e446e3e1895e7897ba9ce9919af9c8305`.
Amendment: checks of R, GATE, the slice unit and the tmpfiles rule are withdrawn; P-SUDO's before/after capture is
added.

### 11.7 Setup identities: pinned and intentionally mutable fields [corrections: W1-V6-IMAGE-PIN, W1-V6-INVARIANTS; v6: W1-V5-IMAGE-PINS; v4: W1-SETUP-PROBES-ROLLBACK]

AMENDED from v7: lines 2833-2884, 6833 bytes, sha256 `47bedb29cef7055c91c6322c56ae059a1c5d3df389b7d8b9f3e67fd6cbfeb46a`.
Amendment: the fields for `wlscratch-run`, `wlscratch-gate`, `wlscratch.slice` and the tmpfiles rule are withdrawn,
and the sudoers file name `wlscratch-run` reads `wlscratch-rl`. The image pins (closed as W1-V5-IMAGE-PINS and
W1-V6-IMAGE-PIN) are unchanged.

## 12. The target view [corrections: W1-V7-ARCHITECTURE, W1-V7-VIEW-ROOT, W1-V7-FULL-DOMAIN; v7: W1-V6-PRESERVE, W1-V6-READ-MUTATION; gap: exposure-options]

### 12.1 The design adopted

v8 adopts the same-identity view (§0.4, §22). Like v7's view it is privileged code, installed only by the operator
inside the existing reserved setup (S-C, S-D) and removed by its rollback (§15.1); no approval gate is added. Unlike
v7's it changes no host identity, reconstructs no root, hides nothing of the host except what the two binds cover,
and needs no lead preparation.

### 12.2 RL and the view, exactly

**Stage 1** (`sandbox_launch.py launch …`, `observe …` or `selftest …`, root, started by S2 or S_O):
1. First act (§7.7); role identity; argv grammar as v7 (verb, g, A, the helper nonce, the observer index, the seals).
2. Invoker: `SUDO_UID` is W, and its nearest ancestor that is not a `sudo` process has uid W. RL trusts nothing else
   from W: every input it uses it reads itself from T and checks against its argv's seals.
3. Descriptors: exactly 0-2 (fd 0 a socket, fds 1-2 regular files owned by W in P_att or in `w2-<k>/`), verified in
   `/proc/self/fd`.
4. Anchors (§3.4) and records as v7 (`O_NOATIME`), including `launch.json`'s `process_attributes` and the view
   specification.
5. Census K and M (§9.4): U absent (for `launch`) or the observer scope name unused; every other RL scope absent or
   `populated 0` and not live in the manager. As root, RL also reads `/proc/<pid>/ns/user` of every process and
   requires that every process whose user namespace has owner W (`NS_GET_OWNER_UID`) lies in an RL scope; a failure
   is premise evidence (P-SETNS, P-CG) and refuses.
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
8. **Mount namespace and the process root** (correction W1-V7-VIEW-ROOT): `unshare(CLONE_NEWNS)`. The kernel copies
   the whole mount tree of the initial namespace (every mount present at that moment, FUSE and network mounts included,
   without calling into any filesystem, P-MSET) and moves this process's root and cwd to the copies (P-ROOT); no
   `open_tree` of the root and no `move_mount` or `pivot_root` is used for the root. Then `mount_setattr("/",
   AT_RECURSIVE, {attr_set: MOUNT_ATTR_NOSUID, propagation: MS_PRIVATE})` and `chdir("/")`. The namespace is owned by
   the initial user namespace.
9. Network namespace: `unshare(CLONE_NEWNET)`; the loopback interface brought up; nothing else.
10. **User namespaces.** U8: RL forks a helper that calls `setgroups(0, NULL)`, `setresgid(W, W, W)`, `setresuid(W, W,
    W)` and `unshare(CLONE_NEWUSER)`, so U8's owner is W; RL, as root in the parent namespace, writes U8's `setgroups`
    (`allow`), `uid_map` and `gid_map` (`0 0 4294967295`: every id maps to itself, JACKAL exact, parsed `2^32-1`; the
    highest id is 4294967294, JACKAL exact, parsed `4294967295-1`), opens `/proc/<helper>/ns/user` and lets the helper
    exit. M_run (the idmap of the binds, which no process ever enters): created the same way, with `uid_map` and
    `gid_map` `W 1000 1`. The concrete inventory states every map line.
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
12. **Verification independent of mountinfo** (correction W1-V7-VIEW-ROOT): `NS_GET_MNTNS_ID` of `/proc/self/ns/mnt`
    differs from the initial namespace's (step 7); `statx("/")` has the initial root's `[dev, ino]` and a mount ID
    different from the initial root mount's, and `statmount(<that ID>, STATMOUNT_MNT_NS_ID|…)` reports the new
    namespace's ID; `statx(".")` equals `statx("/")` (the cwd is the root); for each bind, the destination resolved as
    in step 11 is a mount root (`STATX_ATTR_MOUNT_ROOT`) whose `[dev, ino]` is the held g directory's and whose
    `statmount` reports `MOUNT_ATTR_IDMAP`, `MOUNT_ATTR_NOSUID` and private propagation; `statmount` of `LSMT_ROOT`
    and the mount list (`listmount`) of the namespace show every mount `nosuid`. Every descriptor opened before step 8
    except fds 0-2 is closed now; fds 0-2 refer to W's socket and W's stream files on host mounts by design. RL also
    reads `/proc/self/mountinfo` for the record, as data, not as the verification.
13. **Landlock**: a ruleset that handles `LANDLOCK_ACCESS_FS_MAKE_SOCK`, `LANDLOCK_ACCESS_FS_RESOLVE_UNIX` and
    `LANDLOCK_ACCESS_FS_REFER`, with a path-beneath rule granting `REFER` on `/` and rules granting `MAKE_SOCK` on the
    two bind roots; no rule grants `RESOLVE_UNIX`; no scope flag and no network rule. RL applies it with
    `landlock_restrict_self` while it holds `CAP_SYS_ADMIN` (so `no_new_privs` is not needed and not set).
14. **Credentials**: `setns` into U8 (RL, root of the initial namespace, holds `CAP_SYS_ADMIN` over it); bounding set
    reduced only to F's recorded `CapBnd` (normally the full set, as the lead's); `setgroups` to F's recorded
    supplementary groups; `setresgid(1000, 1000, 1000)`; `setresuid(1000, 1000, 1000)`, which clears the permitted,
    effective and ambient sets; verify `/proc/self/status` (uids and gids 1000 in all positions, the groups, `CapPrm`,
    `CapEff`, `CapAmb` and `CapInh` zero, `CapBnd` equal to F's, `NoNewPrivs: 0`, `Seccomp: 0`), `NS_GET_OWNER_UID`
    of `/proc/self/ns/user` equal to W, and the maps. Seen from the initial namespace the process now has uid 1000,
    gid 1000 and the lead's groups: its host identity is the lead's.
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
Their discharge (S and P) is required before any installed use, and their failure requires redesign (for example,
leaving 0 unmapped, at the cost of a further change of every root-owned object's apparent owner).

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
| V13 | the namespace-qualified effects of U8: no ptrace-mode access between the target and any process outside its namespace in either direction (`/proc/<pid>/{environ,fd/*,cwd,root,exe,mem}`, `pidfd_getfd`, `process_vm_*`, attach); per-user namespace accounting (user and mount namespaces, inotify instances and watches, and the other ucounts) charged at the initial level to W and counted per U8 for the target, and `RLIMIT_NPROC` counted over the target's own processes only; the user namespace is a child of the initial one (nested namespaces are one level deeper) | U8 | the pull closure (N2) |

v7's V5 (host identity R and GATE), V6's first half (unreproduced mounts), V7's private `/tmp`, V9 (masks) and V11
(lead-created mount point) are removed. Frame-side changes are in §21.

## 13. Probe specification (future; nothing here has been executed) [corrections: W1-V6-COPY-PROBES, W1-V6-COMMIT-AMBIGUITY; v6: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY, W1-COMMIT-JOURNAL-EXPORT; gap: denial-probes]

AMENDED from v7: lines 3008-3137, 17262 bytes, sha256 `cf038b69d325646fd3fd7af3d7373d36cd1a8816953611076a38e19dfd536de2`.
Amendments (correction W1-V7-PROBES; every original fixture and every relevant control is retained):
1. The actor columns and rows for host R and GATE read "a view process (host uid 1000 in a U8)"; the denial cells are
   §6.5's (v8).
2. Every expected errno is derived per probe from its exact operand by §6.5's rule; each rename and link probe states
   whether its operands are same-mount (permission errno expected) or cross-mount with fully permitted resolution
   (`EXDEV` expected), and a probe whose operand fails earlier (for example a search permission) is labelled with that
   cause, never counted as `EXDEV` evidence.
3. P-IDMAP's rows for the root view and the `/tmp` bind are withdrawn; its rows for M_run are kept.
4. P-TMPAGE, P-CENSUS and the CRED rows are withdrawn with their mechanisms (§13.1 lists their successors).
5. P-PTRACE, P-LL and P-XDEV are replaced by §13.1's P-PTRACE, P-LL and P-XMNT.
6. "every probe of §13" and "every original fixture" keep their v7 scope; nothing is removed except rows for removed
   mechanisms, and each such removal keeps the positive, negative and failure controls the successor needs (§13.1).

### 13.1 v8 probe set (future; nothing here has been executed) [corrections: W1-V7-PROBES, W1-V7-PREMISES; v7: W1-V6-COMMIT-AMBIGUITY, W1-V6-COMPOSED-STATE, W1-V6-IMAGE-PIN]

v7 §13.1's rows for P-SEAL, P-SR, P-MOUNT, P-IMAGE, P-ENOSPC, P-COMMIT, P-CHAIN, P-PROTO, P-STREAM, P-SIG, P-RELAY,
P-TERM, P-DUMP, P-LAUNCH, P-RUNTIME and V-VAULT are carried in substance with §0.6's rules; the rows below replace or
add. Every probe runs on sacrificial selftest objects (`selftest-<h>`), never on a live generation, and every row
records raw before and after captures. A probe can refute a premise; none establishes one (§9.8 N7).

| Probe | Positive controls (must succeed) | Negative cases (must not succeed) | Cause separation |
|---|---|---|---|
| P-PTRACE | per API, with a valid operand of the right type and mode: `open` of `/proc/<pid>/fd/<n>` where n is a regular file opened for reading; `readlink` of `/proc/<pid>/{fd/<n>,cwd,root,exe}`; `read` of `/proc/<pid>/environ` and of `/proc/<pid>/mem` at a mapped readable address; `pidfd_getfd` of a regular-file descriptor; `process_vm_readv` of a mapped address; `kcmp` of two existing descriptors; `PTRACE_SEIZE` of a descendant (Yama permits descendants). Controls: (C1) a non-view `sicarii` process towards a dumpable non-view `sicarii` process in the initial namespace (same namespace: success shows the uid half and the operand are valid); (C2) a process inside a sacrificial U8 towards another process of the same U8 (same namespace, empty permitted sets: success) | (N1) a non-view `sicarii` process towards a dumpable selftest target in a U8 (expected `EPERM`/`EACCES` by commoncap); (N2) the same from a user namespace the actor created; (N3) a selftest target towards a non-view process; (N4) a target of one U8 towards a process of a sibling U8; (N5) root and W are not negative actors | (D) a non-dumpable target in the same namespace distinguishes the dumpability check from commoncap; (Y) the attach-mode APIs are run against a non-descendant in the same namespace to show Yama's denial separately, and every cross-namespace case uses read-mode APIs as well, which Yama does not govern; (L) a same-namespace pair in different Landlock domains shows Landlock's denial separately; no negative cell is attributed to one cause unless its controls rule out the others |
| P-LL | a socket created, renamed and linked beneath each bind; a connection to a server created inside the domain; a regular-file, directory, FIFO and symlink rename and link between two directories of the root mount, and between two directories of one bind (each with an unrestricted control run outside any domain on identical operands) | a connection and an addressed `sendmsg` to a server created outside the domain (`EACCES`); a socket created, renamed or linked into a directory outside the binds (`EACCES`); `mount`, `umount2`, `move_mount`, `fsmount` attach and `pivot_root`, also inside a nested user namespace (`EPERM`) | each negative paired with the same operation outside the domain (succeeds), so the denial is Landlock's |
| P-XMNT | same-mount `link` and `rename` succeed (control) | cross-mount `link`, `rename`, `renameat2` between each bind and the root mount, and between the two binds, with resolution fully permitted: `EXDEV`; the same with a denied search on an ancestor: the search errno (recorded as such) | operand table per case |
| P-NOCAP, P-NOSUID | `exec` of an ordinary program inside the view | `exec` of a sacrificial set-user-ID-root and a file-capability program in the view, in a nested namespace, through a bind clone made in a nested namespace, by `execveat` of a descriptor and through `/proc/self/fd/<n>`: no uid or capability change (`/proc/self/status`) | the same programs on a non-`nosuid` sacrificial mount outside any view (they elevate) |
| P-ROOT | after step 8, `statx("/")` and `statx(".")` have the expected `[dev, ino]` and the new namespace's mount IDs | a descriptor opened before step 8 still refers to the initial namespace's mount (expected, recorded); a lookup by absolute path reaches a mount of the new namespace | `statmount` mount-namespace IDs |
| P-SKEL, P-PROP, P-LOCK | the skeleton over a sacrificial D with a directory, a file, a symlink and a FIFO entry: each visible as on the host | a host mount made after the view's creation is absent from it; a view mount does not appear on the host; a nested namespace cannot unmount or reveal the skeleton or a bind | host-side controls |
| P-CG, P-SETNS | fork inside a scope stays in it | migration of a scope process to another cgroup by a non-root process (`EACCES`/`EPERM`); `setns` into a U8 by a non-root, non-W process (`EPERM`); RL's root scan (step 5) finds no W-owned user namespace outside RL scopes | a delegated user-manager cgroup control where migration succeeds |
| P-MGR | — | a scope reported `inactive`, `failed` or `not-found` while its cgroup reads `populated 1` (sampled at high frequency during scope teardown) | refutation only |
| P-IOEXIT | — | direct-I/O and `io_uring` writes issued by a sacrificial target immediately before its exit, with an outside reader of `/proc/<pid>/cmdline` holding its memory context: any data change of the target file observed after K reads `populated 0` refutes the premise | refutation only |
| P-UCOUNT | inotify instances and user namespaces created in a sacrificial view are charged to W's per-user count at the initial level (observed through the counts the kernel exposes, or through the limit being reached by W's count) | — | root's and 1000's counts unchanged |
| P-SUDO, P-LOGLEVEL | a frame-rule invocation | any new or changed file under `/var/log`, `/var/db/sudo`, `/run/sudo`, and any new journal entry for the invocation or for the scope's informational messages (before/after capture of the journal cursor and of those trees) | the same invocation of a sacrificial rule without the options (logs) |
| P-COMMIT, P-CHAIN (extended) | v7's | v7's, plus: the writer killed by the probe harness between a close marker's link and its `RECORD_COMMITTED`; every consumer (F, W2, a post-reboot reader, an export and its offline reader) reports `unobserved`, consistently; an injected directory-`fsync` failure reports `failed` everywhere | — |
| P-SR (extended) | every vector of §11.4's global table is produced on a sacrificial copy and continued and reversed | an `installed-other` vector and an unlisted vector stop | — |
| V-VAULT (extended) | `project-vault pin`, `status` and the recovery comparison on a sacrificial export that includes a complete capture; an offline verifier, holding only the restored tree, recomputes every chain head, marker and payload digest, the provenance of every record, every raw and torn byte, and every captured entry's bytes and recorded metadata | a restored tree missing any byte fails the verifier | — |

## 14. Resources, staged Gate 0 and images [corrections: W1-IMAGE-TREE; gap: resources-and-images]

AMENDED from v7: lines 3153-3164, 1073 bytes, sha256 `620943a5c34f474d1a64aac1493c98000adbd0d545f92c944445fccf1507466d`.
Amendment: the v8 numbers are recorded in `v8-support/jackal.json` (Appendix H); "v7 changes no allowance downward"
reads "v8 changes no allowance downward; it adds the capture allowance of §14.7".

### 14.1 Gate 0 of runbook v4.3, unchanged

CARRIED from v7: lines 3165-3172, 552 bytes, sha256 `74064f167fa18ca4c37b49cef1070d1902ab55bf3201fcca04aac6be3a9c59f9`.

### 14.2 W-1 allowances (labelled judgments)

AMENDED from v7: lines 3173-3190, 2884 bytes, sha256 `8b3d554ccfe9f413dd75b6be3eb19e0428505357a2e26e734c19cd2d51aec4aa`.
Amendments: A_tmp covers the view's `TMPDIR` (g/tmpdir) and the host `/tmp`, `/var/tmp` and `/dev/shm` used by the
target, unchanged in bytes; A_jrnl's basis reads "sudo, PAM, journal and unit effects of the scopes, now minimized by
§9.8 N5, unchanged in bytes"; A_homes keeps its bytes (no slice or tmpfiles file exists any more; no allowance is
lowered). New row:

| Id | Covers | Bytes | Basis (JACKAL parsed input) |
|---|---|---|---|
| A_capture | one attempt's complete capture (§15.3): the recipe (A_mat), the native outputs (A_obj, the output allowance carried in v7's expression), `tmpdir/` (A_tmp), the attempt's records and raw bytes (A_rec, A_retry) and the fallback journal (A_fb) | 3922388356 | `16777216+2242440646+268435456+545393048+832564774+16777216` |

### 14.3 Stage budgets and the rule

AMENDED from v7: lines 3191-3214, 2189 bytes, sha256 `4a63ef7988c871db44c7acb01eb7fff50db51be87e18bdc8bfcca63c2dec733c`.
Amendment: the third row splits. "before every `adopt` and every `materialize`" keeps 15415338242864/1397. "before every
dispatch" becomes 26374491309528/1397 (approx 18879378174.32212), JACKAL exact, parsed
`15415338242864/1397+2*(16777216+2242440646+268435456+545393048+832564774+16777216)`: the v7 expression plus
A_capture and its full restore; the check `26374491309528/1397-15415338242864/1397-2*3922388356` gives 0. The rule,
its procedure and "what these numbers are not" are unchanged.

### 14.4 Historical arithmetic (not capacity and not current)

CARRIED from v7: lines 3215-3227, 739 bytes, sha256 `e9387e358eaffbf6a7244c1a7c9e15c237cfce7b2d5a39cd2e05a71af4860f1b`.

### 14.5 Images (only if S-1 option 3 is chosen) [correction: W1-V6-IMAGE-PIN]

CARRIED from v7: lines 3228-3286, 5542 bytes, sha256 `827f657deaa767316f148b3854a8d22af7ca48366ecad883e8b87be5603f306b`.

### 14.6 Memory, CPU and caps

AMENDED from v7: lines 3287-3293, 481 bytes, sha256 `2fb09568b7cb3df4e323a9d6e3e827531df83bc3946a4037914e696d6fa31758`.
Amendment: "The views' masks are empty `tmpfs` mounts" reads "A skeleton, when used, is a small read-only `tmpfs`"; the
scope lies in `user-1000.slice` with the properties of §8.3, and `app.slice`'s shared limits do not apply (§12.3 V10').

### 14.7 The complete storage accounting (v8) [correction: W1-V7-EVIDENCE-RESTORE]

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
  future writes, and safe fresh capacity stays OPEN.
- A capture that fails (for example `ENOSPC`) is recorded as failed, the attempt cannot succeed (§10.7), and nothing
  else changes; it is not presented as an accepted refusal (§21 D6).

## 15. Rollback, freeze/export and evidence [corrections: W1-SETUP-PROBES-ROLLBACK, W1-COMMIT-JOURNAL-EXPORT; gap: rollback-and-evidence]

CARRIED from v7: lines 3314-3315, 139 bytes, sha256 `c28ab08b1a6cf57c5c65775871754ab7312225c4fb76ff455a1da064d04a35d0`.

### 15.1 Rollback order (operator; every step's before and after state captured raw)

AMENDED from v7: lines 3316-3346, 2739 bytes, sha256 `febdbcf0c70dd9085e6364d21f26d46ab1c41a34e633573207d279624fcb8027`.
Amendments (correction W1-V7-COMPOSED-STATE):
1. Step 2's "every child cgroup of `wlscratch.slice` absent or `populated 0`; CRED (§9.4): no process with uid R or
   gid GATE" reads "K and M (§9.4): every RL scope absent or `populated 0` and not live; RL's root scan (§12.2 step 5)
   finds no W-owned user namespace outside an RL scope".
2. Step 4's file is `/etc/sudoers.d/wlscratch-rl`. Step 5 (slice unit and tmpfiles rule) is withdrawn.
3. Step 8 locks and expires the one account.
4. **The rollback is its own state machine**, not the inverse of setup (§11.4). Its state is the vector of: the two
   sudoers files and the sshd drop-in (each `installed-equal`, `deactivated-equal`, `absent`, or `preserved` with its
   bytes and sha256 in `rollback-<stamp>/`); the image units and enablement links; the account (unlocked, locked,
   locked and expired); every RL scope and W process (live, ended); and the retained trees, each with a hash manifest
   (path, type, size, sha256, owner, mode, ACL digest) captured before step 1 and after the last step. Each step's
   postcondition is checked by its after capture. The retained trees may have grown at runtime and are never
   reverted; the postcondition for them is "the after manifest equals the before manifest". A stopped rollback
   continues from the first step whose postcondition does not hold.

### 15.2 What rollback leaves

AMENDED from v7: lines 3347-3354, 492 bytes, sha256 `a7775b11541a8699f89078f0989a3000b53b50b94a0ef73ec4984b24523e58d2`.
Amendment: "the two locked and expired accounts and the three groups (the two user-private groups and
`wlscratch-gate`)" reads "the locked and expired account and its group"; "the slice unit, the tmpfiles rule" is
withdrawn from the removed list.

### 15.3 Freeze and export [corrections: W1-V7-EVIDENCE-RESTORE, W1-V6-EVIDENCE-RESTORE; v4: W1-COMMIT-JOURNAL-EXPORT]

AMENDED from v7: lines 3355-3426, 6853 bytes, sha256 `a75b83706d17e4cb4a01b0c0f64552476880738538caf91fa8512a75fee13334`.
Amendments:
1. In the increment bullet, "Raw bytes (TORN slots, RAW marker files, uncommitted records) stay in their protected
   original place and get no parsed or success credit" reads "Raw bytes (TORN slots, RAW marker files, uncommitted
   records) are exported **as bytes** (export copies with state `torn`, `raw` or `uncommitted`), in addition to their
   path, size and sha256; they get no parsed or success credit". "A committed record with `synced: false` is exported
   with that value" reads "… is exported with its sync provenance and with the attestation records it rests on (§10.5)".
   The manifest's `synced` field reads `sync_provenance`.
2. New paragraph, **the complete capture**: "After H(U) of attempt A (K reads U `populated 0`, §9.8 N4) and before
   A's terminal record, the serving writer (W, or W2) writes `export/capture-<A>/`: an export copy of every entry of g
   (the recipe, every partition entry, `tmpdir/` and its contents), read as on-disk owner with `O_NOATIME`, and of
   every file of P_att(g, A) and of every W2 directory, by the export primitive; regular files by bytes, directories as
   directories, symlinks by their target string (read by `readlinkat`, whose access-time effect on a W-owned symlink in
   T is inside T), special files by type and device number only. Its `capture-manifest.json` records, for every
   original entry, the relative path, type, `stat_key` (dev, ino, mode, nlink, uid, gid, size, mtime_ns, ctime_ns),
   atime_ns, the access and default ACLs, the extended attributes, the link structure (inode groups) and the sha256 of
   the bytes; and for every copy its export path, sha256 and final mode. A complete capture is committed by an export
   marker whose record is the manifest's descriptor; a capture that cannot complete is recorded as `failed` (§14.7).
   Captures are additive per attempt and never modified."
3. The vault pins the whole `export/` tree (§8.5), so the complete capture, the raw bytes, the slots, the channel
   segments and their continuations are all inside the pinned tree.

### 15.4 Evidence classes (all retained raw)

CARRIED from v7: lines 3427-3441, 1401 bytes, sha256 `9b3b2b684c75092b5ec7cbe8f425241d3de45e7d6f40d540741d7245fa600652`.

## 16. Setup, verification and adoption order

AMENDED from v7: lines 3442-3471, 2437 bytes, sha256 `c6708e6fc8b6169d9517d9f50e198c209197cd36f67c61b681955b201afab56e`.
Amendments: item 1 reads "this v8 design"; item 2 adds "and the code-review item that W never uses its owner
capabilities over a U8 (§9.8 N2)"; item 2's "the census and CRED" reads "the censuses K and M and RL's root scan";
item 3's "sudoers, sshd, slice and tmpfiles bytes" reads "sudoers and sshd bytes and the scope properties of §8.3";
item 7 lists the probes of §13.1; S-F is no longer among the scripts of item 6. Item 5 ("Operator approval of the
concrete setup") is the existing reserved authority, not a new gate.

## 17. Placement of every v5 mechanism

AMENDED from v7: lines 3472-3499, 5120 bytes, sha256 `22632e131fe9a5ea27c4c627c5a0f072fd7ca3028e9ea54b4adafb65bb389927`.
Amendments: v5's run-directory creation by `materialize` (S:977-999) is placed as: label check by F (read-only, §3.3),
generation creation by W in T, run-path presentation by RL in the view only (§12.2 step 11); v5's `spawn` in its
user-manager scope is placed as RL's system scope in `user-1000.slice` with the attributes of §8.3; v5's vault pin of
the run directory is placed as the vault pin of the export tree with its complete captures (§8.5).

## 18. Per-correction and per-gap status (the author's assessment, for the independent reviewer to judge)

AMENDED from v7: lines 3500-3507, 613 bytes, sha256 `e9ac9f10d3a6dc4e47a9292875f4fa00f5c03fa0dbd62c1fcb1268d9258dd6fd`.
Amendment: "v7" reads "v8" and "gpt61-v6" reads "gpt61-v7" throughout the unit; every original obligation, V5-B01,
V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION and Gate 0 stay OPEN regardless (§0.4, §22).

### 18.1 The gpt61-v7 review's required W-1 changes (verbatim) and the author's assessment

Source: `v7-review/gpt61-v1/review.json` `required_changes[].change` (sha256 above); eleven entries (JACKAL exact,
parsed `1+1+1+1+1+1+1+1+1+1+1`, Appendix H). The assessment is the author's claim, not closure.

1. **W1-V7-ARCHITECTURE**
   > Re-evaluate c8 and narrow the seccomp/user-notification rejection to the mechanisms actually excluded; compare surviving alternatives before describing (a) as the sole suitable direction. Keep every original preservation obligation open.

   Author: CLOSED-AT-SPEC-LEVEL for the re-evaluation and the comparison (§22.3: c8 grounded in the quoted commoncap
   and `__ptrace_may_access` text, with push and name routes; user notification narrowed to the CONTINUE pattern and
   io_uring's bypass, the broker alternative evaluated and not adopted; every alternative compared; SIV adopted as the
   smallest sound change set). The preservation obligations stay OPEN (§21, §22.4).
2. **W1-V7-VIEW-ROOT**
   > Specify and bind the actual process filesystem root and cwd to the idmapped/masked view, including handling of old-root/path descriptions and every reproduced mount. Verify these identities independently of mountinfo before any role observes or launches.

   Author: CLOSED-AT-SPEC-LEVEL, conditional on P-ROOT, P-MSET and P-SKEL (§12.2 steps 8, 11, 12, 16; §9.3 G4, C2,
   C3): no root reconstruction; the kernel's namespace copy moves root and cwd; every host mount is kept (none is
   "reproduced"); old descriptors closed or, for fds 0-2, stated; verification by `statx`, `statmount`, namespace
   ioctls and `/proc/self/exe` by RL, L, C and O, with mountinfo kept only as data.
3. **W1-V7-HOLDER-STATE**
   > Define the exact logical holder/mutation completion event and prove its absorbing property under all admitted file-reference and asynchronous paths. Replace instantaneous P-CENSUS equivalence with a conservative race-aware observation protocol that retains the original terminal/ownership/window/manager predicates.

   Author: OPEN. H(U) is defined exactly and its absorbing property argued (§9.8 N4); P-CENSUS is withdrawn and the race-
   aware conjunction of K, M and v5's predicate replaces it (§9.4). The argument for asynchronous paths has a stated
   gap (a direct-I/O write completing after `populated 0` when an outside `/proc/<pid>/cmdline` reader holds the memory
   context), carried as P-IOEXIT; the author does not claim the proof complete.
4. **W1-V7-FULL-DOMAIN**
   > Define preservation over the complete original accepted/refused frame and target domain, including all valid operands/overlays/metadata/environments/resources/prestates/evidence readers and backup behavior. Rework every V1-V12 and C1-C7/D1-D6 effect that changes an originally accepted case. Retain only criterion-authorized changes or changes whose full original-domain irrelevance is established.

   Author: the relation is defined (§21.1) and every effect reworked or classified (§21.2-§21.5). OPEN: changes remain
   whose irrelevance is not established, so W1-V5-PRESERVATION stays OPEN.
5. **W1-V7-C3-DATA**
   > Deliver the authenticated launcher-rl-identity record and its committed/digest binding to C before C3, and define the exact channel keyset/order and missing/mismatch controls. Keep the repaired C1/C2 separation intact.

   Author: CLOSED-AT-SPEC-LEVEL (§9.3 C2, C3; Appendix B.4 amendment).
6. **W1-V7-READ-EFFECTS**
   > Keep READ-MUTATION, R-d/R-f/R-h and V5-B02 open. Complete the causal explicit/implicit read and control-plane write inventory, including imports, site/.pth, dynamic loaders/helpers, namespace map writes, sudo/PAM and manager/journal effects. Redesign any effect outside the original window/preparation authority; preserve readable foreign-owner cases.

   Author: inventory CLOSED-AT-SPEC-LEVEL (§9.8 N5, N6); redesign done where a mechanism exists (sudo options,
   `LogLevelMax`, `O_NOATIME` as root for RL's reads, no host write by RL); READ-MUTATION, V5-B02 and the routes R-d,
   R-e', R-f, R-h, R-i, R-j and the classification of frame-own and baseline-class effects OPEN.
7. **W1-V7-PROBES**
   > Correct P-LL and P-XDEV predicates and expected errno derivations without weakening accepted controls. Supply per-API type/mode-valid positive controls and controls that separate namespace, dumpability/Yama and Landlock denial causes. Retain every original fixture and relevant control.

   Author: CLOSED-AT-SPEC-LEVEL (§9.8 N7 P-LL, P-XMNT; §6.5; §13 amendments; §13.1).
8. **W1-V7-COMPOSED-STATE**
   > Enumerate actual global setup, partial, resumption and rollback effects, including conditional cleanup of previously installed atoms, partial file and image operations, service/enablement co-effects and runtime-grown evidence-retaining rollback. Make S-R classify and safely continue/reverse each reachable state without treating ordinary partial states as reserved exceptions.

   Author: CLOSED-AT-SPEC-LEVEL as a model (§11.4, §11.5, §15.1); the exact global table is part of the concrete
   inventory, which does not exist yet.
9. **W1-V7-SYNC-PROVENANCE**
   > Separate structural commit membership from observed sync/error provenance. Specify writer death after a linked close marker and before any post-link failure/downgrade announcement, with consistent known/unobserved/UNKNOWN results for every live/reboot/offline/export consumer and genuine failure controls.

   Author: CLOSED-AT-SPEC-LEVEL (§10.1 step 5, §10.5, §10.6, §9.6, §9.7, §13.1): "known" is `observed` or `failed`,
   "unobserved" is `unobserved`, "UNKNOWN" is durability-UNKNOWN membership.
10. **W1-V7-EVIDENCE-RESTORE**
    > Preserve the original complete run/native-output backup semantics or provide an exactly complete independent equivalent capture. Restore raw torn/uncommitted records/markers/journal slots, channel continuations and all required original evidence bytes as well as payload packs. Budget the complete simultaneous retained and restore peak under the unchanged reserve.

    Author: specified (§8.5, §15.3, §14.2, §14.3, §14.7). OPEN: whether the capture is "exactly complete" and equivalent
    for every original backup consumer (V-BACKUP, §21 C1) awaits V-VAULT; safe fresh capacity stays OPEN.
11. **W1-V7-PREMISES**
    > Maintain one complete premise/dependency/probe register, including P-TMPAGE and every causal runtime/setup/channel/credential/evidence reliance. Distinguish sampled refutation from installed-version source discharge and trusted-base exclusions; remove circular first-run qualification and false universal claims. Every failed premise requires redesign with no exception.

    Author: CLOSED-AT-SPEC-LEVEL for the register (§9.8 N7); every premise in it NAMED_UNESTABLISHED.

### 18.2 Prior corrections, as the gpt61-v7 review ruled on them

`prior_closure` (verbatim statuses): CLOSED_AT_SPEC_LEVEL: W1-DURABILITY-RELEASE, W1-IMAGE-OBSERVATION,
W1-JOURNAL-CONTINUATION, W1-RESOURCES, W1-SETUP-IDENTITY, W1-V5-IMAGE-PINS, W1-V5-PROTOCOL-REFUSALS — carried
(§0.5). NOT_CLOSED: W1-V5-PRESERVATION — OPEN (§21). PARTIALLY_CLOSED (14): W1-COMMIT-JOURNAL-EXPORT,
W1-CUSTODY, W1-CUSTODY-CLOSURE, W1-GENERATION-PROTOCOL, W1-IMAGE-TREE, W1-LIFETIME-ROLLBACK,
W1-PROTOCOL-FAILURE-STATES, W1-SETUP, W1-SETUP-PROBES-ROLLBACK, W1-SETUP-RECONCILIATION, W1-TERMINAL-CUSTODY,
W1-V5-JOURNAL-FAILED-CLOSE, W1-V5-RECONCILIATION-STATES, W1-V5-REVOCATION-CONFINEMENT — each OPEN in the author's
assessment, with v8's changes as follows: the custody and confinement items through §9.8 and §12; the setup,
reconciliation and rollback items through §11.4, §11.5 and §15.1; the commit, export and journal items through §10.5
and §15.3; the lifetime, protocol-failure and terminal items through §9.4 and §9.5.

`v6_required_change_closure` (verbatim statuses): CLOSED_AT_SPEC_LEVEL: W1-V6-C1-DATA, W1-V6-IMAGE-PIN,
W1-V6-INVARIANTS — carried. NOT_CLOSED: W1-V6-PRESERVE — OPEN (§21). PARTIALLY_CLOSED: W1-V6-CATALOGUE,
W1-V6-COMMIT-AMBIGUITY, W1-V6-COMPOSED-STATE, W1-V6-COPY-PROBES, W1-V6-EVIDENCE-RESTORE, W1-V6-READ-MUTATION,
W1-V6-SCAN-STATE — OPEN, addressed by their W1-V7 successors (§18.1 items 4, 9, 8, 7, 10, 6, 3).

### 18.3 The section-3 gaps

`w1_gap_closure` (verbatim statuses): CLOSED_AT_SPEC_LEVEL: denial-probes, exposure-options,
fresh-identities-and-vault, lease-and-writer-authority, per-entry-modes-acls, resources-and-images — carried; v8
amends their sections only as the new design requires (§6, §8, §12, §13, §14). PARTIALLY_CLOSED: channel-and-dumpability,
commits-and-durable-channel, generation-order, participants-and-recovery, prestate-and-installation,
rollback-and-evidence — OPEN in the author's assessment.

### 18.4 The original W-1 subgaps

`w1_subgap_closure` (verbatim statuses): CLOSED_AT_SPEC_LEVEL: W1-FINAL-PASS, W1-IMAGE-COMPATIBILITY,
W1-IMAGE-GEOMETRY, W1-NONCLAIMS, W1-PREFLIGHT-IDENTITY, W1-READ-ACCESS, W1-READ-EXPOSURE, W1-SETUP-ORDER,
W1-SETUP-PRESTATE, W1-VERIFICATION-PROBES, W1-WRITE-AUTHORITY — carried (W1-FINAL-PASS gains §4.5 item 4, an
addition). PARTIALLY_CLOSED: W1-CHANNEL, W1-CLOSURE, W1-CUSTODY, W1-EVIDENCE, W1-FAILURE-LEASE, W1-FAILURE-RECORDS,
W1-REBOOT-RECOVERY, W1-ROLLBACK, W1-SETUP-EXACTNESS — OPEN.

`open_obligations`: the 219 entries of `OBLIGATIONS-v2.json` (sha256
`1587e068fc2c31a562e38b459728a75dbf7e8d7d9f8afb8efa1474e2a702aeec`) and V5-B01, V5-B02, W1-V5-PRESERVATION and
W1-V6-READ-MUTATION stay OPEN with their original owners, releases and dependencies.

### 18.5 Change map (every v7 unit, with its identity)

Base: v7, sha256 `8646f0fed3cf3f61dceb4fbf3a583f96f2bf7a0adce4986cb415789edeb82a7a`. Units by v7 §0.1's rule, read by
a read-only script on 2026-10-05T15:51:35Z. C = CARRIED, A = AMENDED, R = REPLACED (§0.1). Appendix H is NEW.

| Unit | v7 lines | Bytes | sha256 | v8 |
|---|---|---|---|---|
| title | 1-60 | 5460 | `a83dbdd6f2e5fa1833d537990810f50597f24c465d57c6ec1a99c82c20583c86` | R |
| 0 | 61-62 | 52 | `ecb94117fd1df2cf8364b3ef9cc8cda2b7effffcf7bfc325f29e5c42170b2c60` | R |
| 0.1 | 63-78 | 1227 | `d7f8d3e28cccb1db6f5f0ebe502b93aeda7072f99ef21d9116f78b0f642adc0c` | R |
| 0.2 | 79-105 | 2335 | `515529d769bcbe78b0d42f08ad5df5e3886b561030074731d3504ec948c95edb` | R |
| 0.3 | 106-125 | 1685 | `14c054593cb5da6096fb57ab0d149444cbab99d9c8ad765e5f537695a0fff8f7` | R |
| 0.4 | 126-145 | 1863 | `318c8beb01402b072237e221b5a8ed2150a4072467089c4100d743441b453855` | R |
| 0.5 | 146-170 | 1872 | `27716591dc56c87a8943e00fab64f13b5484dd2eca67af90a91b6ae0297a09df` | R |
| 0.6 | 171-185 | 1102 | `5aa12beb675634083d68cb80bdad73e058a03782b58ef3ea124ec5e1fcc41e97` | R |
| 1 | 186-227 | 3156 | `2ae9da8b3dc5177eb189805c8f7fdc48e4908a2204fb68a6b4be0b5118aa0dac` | C |
| 2 | 228-229 | 63 | `35f6eb75cbc9b074ead5488fca9693875386deb826fbd0374020398a83887683` | C |
| 2.1 | 230-260 | 3089 | `b838b8abc1c56b37d29a114cb70a0076c8a8dd46b5eeda5b272b0b940c587cb8` | R |
| 2.2 | 261-269 | 742 | `b5506e5a5472a1f269982a93b980477cbc9e16ff35fb3dfe00dbcf85d67a8d38` | R |
| 2.3 | 270-296 | 2629 | `5c4aad42392d62002b099a573afe71fee7a5d9cb108cfb198638760cdb8ffd6d` | A |
| 2.4 | 297-334 | 3711 | `6cfa098c8530fdd806099f8444a6173e9f4145e9da03555716deb42994bac612` | R |
| 3 | 335-336 | 39 | `5510e891fd324593657d164471cb63078bbc71af4f71c2da3fc35163ae8c2ed0` | C |
| 3.1 | 337-352 | 1330 | `7af530f409c52595712373b0fac00bceed7aed68618d8749e30ebfe6ae190974` | R |
| 3.2 | 353-378 | 3207 | `9b39bc782e45795c354ded40c35865b1b1649b627e5a887216d30452ad686ec9` | R |
| 3.3 | 379-423 | 3971 | `8591c59f9d9fb8ba0d300fa718ea7ad02239d49e3e113a01f43272f9c13e1d4a` | R |
| 3.4 | 424-495 | 6872 | `0e55f3b852cef2cf3ca2a38ed3b642b91ee463a843abf1ef030a2dbf2b881917` | A |
| 4 | 496-497 | 106 | `030cba113f70fd51a55fba2cdbacef1d4bebdd0fa2b0813f0a7f935356beaa45` | C |
| 4.1 | 498-540 | 4017 | `a5c68784c918927bb85b3821b3f30cc0cfdfce7f5665f23a80f8454f7d67ceea` | A |
| 4.2 | 541-704 | 14968 | `7b7989df8a2e302e11207aab6adaeb1b633b6eba048d56e7cf73336cf9715156` | A |
| 4.3 | 705-776 | 6825 | `307c39b54b88ff15c2e44d70df17cd6d62d83ffea57ad12b36a591f4c7c20b0b` | A |
| 4.4 | 777-802 | 2451 | `eb572f6edb96f31e7bf59a9d8176ed06a37de4f96282533d86a1d70d7d31a59c` | C |
| 4.5 | 803-851 | 4428 | `6bac3c43cbe1b3716bd262cb7504ac26b6ebaf5131f420f24ba37e8a35a26fe5` | A |
| 4.6 | 852-916 | 5877 | `00b3ed65328eb21773f171bf89852ac17c227e4c242c254aa4e2bc5c739eb234` | C |
| 5 | 917-918 | 137 | `46adbb0dd725d4f1ca5f142a684061fafc17e2c5165b6da45647a41585de9bab` | C |
| 5.1 | 919-946 | 2284 | `e0bc923e20b24b36609ff4d44f5a354e999dcd57c67793c398d1890d68c14b97` | C |
| 5.2 | 947-979 | 3802 | `8c91cb45b3f5748048a6ea7c12b8573b152a248b3090044b4219bb7a3a9a076c` | A |
| 5.3 | 980-1002 | 4835 | `b17708dc9fad2e80adcb7faf433456de4cd5da6d4718f0097856faebebbbd23a` | A |
| 5.4 | 1003-1009 | 478 | `debd77ac854c1a74be9913a849254ef55cff1e9f0adc2553f42431b3167eee6a` | C |
| 6 | 1010-1011 | 144 | `6a852dcafc48edb984b90136498474c97f6f0348b8e6541fe33b803af9034fd3` | C |
| 6.1 | 1012-1032 | 1821 | `3d18ff6cf3be2307f6980717d1796fd4963eed1bddb4d51232ac59c328d2d608` | C |
| 6.2 | 1033-1049 | 1442 | `155a6ef1dfdbbf811f6bd5f0a35f3134e8e60f171ee273535f4b227a30e760c2` | C |
| 6.3 | 1050-1089 | 4528 | `a9ea41912a3fa75eb1ca915ce4940ba071282e631262acfe94e89deea9482dea` | A |
| 6.4 | 1090-1114 | 2161 | `f4621332bbe3289a098fd1a85230575cb28ff8806d4b7e08c7c4da2a88a827fa` | R |
| 6.5 | 1115-1143 | 2761 | `c5a816ecadb950e407b66a61400300607f7d558de696a3827e145506eeec90f5` | R |
| 7 | 1144-1145 | 113 | `8ab0b34614a172ffb23cde8314d7bef25492c58858feabd1d30e543cde17fbae` | C |
| 7.1 | 1146-1162 | 2146 | `9fbaf54e2de1e4e3e0db688efb1d901ef43faea28a6684a58eea01082dbe8210` | A |
| 7.2 | 1163-1185 | 2191 | `7faec7003ad60f3723bd527d117099d1c40615466ed7acd274903c19a54d8047` | C |
| 7.3 | 1186-1219 | 3468 | `eeaeab07f27381c5af35893f610b81e421bd7ca96e7568d96540ced5164e5e2e` | C |
| 7.4 | 1220-1233 | 1131 | `66f9582ac696d0efbf60ec1e3ff0f29f7f484f24093b667798f983ee0a9a9a0d` | A |
| 7.5 | 1234-1249 | 2318 | `58b24a0d5a3462b2659cb856abf0558bf42183193c745d16bdba67a72037114a` | C |
| 7.6 | 1250-1259 | 826 | `da3dc6642e8c8b1bf407a522e929faa1997c00c2b74738d67783089debc1b34a` | C |
| 7.7 | 1260-1283 | 2261 | `896aa8191f98cba8110b73eefe4f823da866fc5ae0b2351a883e8b48763115ec` | A |
| 8 | 1284-1285 | 121 | `5dc90f8d992d37f789b9fdc38f5cef1248a2bb2ae0c5322ab39442c58024bc66` | C |
| 8.1 | 1286-1312 | 3351 | `c68f5aea009de4262a665bfffffd00df534776dbc2e70e79dd3637ee6f0334ba` | C |
| 8.2 | 1313-1324 | 1030 | `309b19cccb33bc3a0a2d9863e13e869de1e42a9ae055ede4b84a47ec7fde5705` | C |
| 8.3 | 1325-1345 | 1914 | `967693e4db6dde86e42156df8897336f37cfc7b1ee9cbefe83254e2349b34447` | R |
| 8.4 | 1346-1378 | 2862 | `dc06ffee8154663ef3eb7a806cc4757b40fd15c191f1da590ff06994b8c9e454` | A |
| 8.5 | 1379-1399 | 1954 | `3769a7d52fed28ec54973232d45ef9f4b1efdd015cbee5d11279119712d1c359` | R |
| 8.6 | 1400-1421 | 2023 | `3ec9d7f237addb503a8f3a90434741ae57e7386139ae3ab5b5a06271ae25dd1f` | C |
| 9 | 1422-1423 | 189 | `d1843b7e7e7bee1fec119a7314ce98958f5e46327d872070510c73a6b1c90a01` | C |
| 9.1 | 1424-1449 | 2226 | `bb6878ba3ff06de0beee08216c93ad10d2e4d4e483b8fdab0c693cb757e15502` | C |
| 9.2 | 1450-1467 | 1714 | `6c4a383502ee74cabb5b597ae8220ba1d86122fa6d12400adfb30845910dc11f` | C |
| 9.3 | 1468-1602 | 13868 | `e6a4fc9f200ee99324f75d622f4713783977dcb3e2fa34605e7cc9646f97e7be` | A |
| 9.4 | 1603-1704 | 9577 | `a41ff848d353f97b321eefa24fd7caf0cdb7d614a44d7fdc260b97cc87410e74` | R (its release-rule paragraphs carried by reference) |
| 9.5 | 1705-1746 | 8230 | `e50b3781c1482863c0e0b3818a82759c16edcccf68fda8de562f29651689a5f7` | A |
| 9.6 | 1747-1769 | 2116 | `06533416b10f8f1cbda45312a42525c9d390f69ab8822edb7764f4c37babc5a7` | A |
| 9.7 | 1770-1813 | 4093 | `cfcab530221830dabf11e41d3c0d09096f5be5f59fdfedaa47d944ce235a4cb4` | A |
| 9.8 | 1814-1934 | 13102 | `add1e06a75fd3f917c272cf48014afb91c231c72e04cc330674a3eccd5e18d40` | R |
| 10 | 1935-1936 | 173 | `b923c50c51930667776aced4d6d5b16a080102e4e056e61d0ade2fd420c1d98d` | C |
| 10.1 | 1937-1971 | 3022 | `a0774d3a37aabfb162c3f5386551ea377e7dc756fefebe7f9c2172dde18daa62` | A |
| 10.2 | 1972-2085 | 11650 | `f78bc026cea49fb212d14355029a3ac6b1173c045ed3e59cd6b1f6d0cf7710fc` | A |
| 10.3 | 2086-2091 | 369 | `2b275b998e8c39b306421b0c6400ea8c12528d2b9741410c51f99ac4bca59990` | C |
| 10.4 | 2092-2135 | 4467 | `45c96fa1f94741a0a04242424778df566daa7cd7914d7c8ff2cc04be34e7d85f` | C |
| 10.5 | 2136-2149 | 1252 | `d813613bcbd0fc6619d4422e2391a653d99164df1153276ac104c3e650b423dd` | R |
| 10.6 | 2150-2179 | 3658 | `2c1f196a73aa5e6fb60e91055b8e3edcb7f0c6aceff2764fc81016b02c05a092` | A |
| 10.7 | 2180-2217 | 3924 | `f7646af077f17d438c07a0641f6aefec1fc3af5f295bb9ee7e8e80a1b0bb7eea` | A |
| 11 | 2218-2219 | 127 | `554fcbe4c216f90ff9d4ae0b8672903c7d18685221dc80a7ec07dbc59d5df8cd` | C |
| 11.1 | 2220-2239 | 1723 | `0ad981bd44c1a4c63a85f56e89f7983c354e19b1eea1b5ab56eec3357a73463e` | C |
| 11.2 | 2240-2254 | 1210 | `d07d96f31be7f06b3e6d6723d8163093f6e2d235b675989c22f57fa5f51b167c` | A |
| 11.3 | 2255-2302 | 7394 | `746b17ca012b7436847c99cb9ebd9186cd66384854d3b3456f74bb4c12257e50` | A |
| 11.4 | 2303-2417 | 12348 | `c3130b56528d5bef8c93036f8a982c3cbe62fe15e44270ca5f11490b510f9893` | R (its staging and status rules carried by reference) |
| 11.5 | 2418-2818 | 23350 | `547c43f3dc06aa2cd44ba799719feda46e70c8f2cf95febf8871c024c7c48ca4` | A |
| 11.6 | 2819-2832 | 1096 | `5f165da0bcdc34798a12b60342a2ba3e446e3e1895e7897ba9ce9919af9c8305` | A |
| 11.7 | 2833-2884 | 6833 | `47bedb29cef7055c91c6322c56ae059a1c5d3df389b7d8b9f3e67fd6cbfeb46a` | A |
| 12 | 2885-2886 | 98 | `04379c2b06bfd4ec87e05bb4117e58bc895097efe9acbc161762662ef5d812cc` | R |
| 12.1 | 2887-2896 | 746 | `730af43d666a469fbd8015080261bb3024b6df85e2aa609b7490aa9d278f258b` | R |
| 12.2 | 2897-2983 | 7889 | `1cdecb28852f8628dae2874620581680d56517d598cc357414fbe502c2048235` | R |
| 12.3 | 2984-3007 | 3538 | `508ba763c95be89fe40b566d890c31edf635a521a09083076b747e01092184dd` | R |
| 13 | 3008-3137 | 17262 | `cf038b69d325646fd3fd7af3d7373d36cd1a8816953611076a38e19dfd536de2` | A |
| 13.1 | 3138-3152 | 6758 | `2d1d7fdf62f92c8310eb454ea334bd668aa1af2bd46da94724b5b5ea539fa97d` | R |
| 14 | 3153-3164 | 1073 | `620943a5c34f474d1a64aac1493c98000adbd0d545f92c944445fccf1507466d` | A |
| 14.1 | 3165-3172 | 552 | `74064f167fa18ca4c37b49cef1070d1902ab55bf3201fcca04aac6be3a9c59f9` | C |
| 14.2 | 3173-3190 | 2884 | `8b3d554ccfe9f413dd75b6be3eb19e0428505357a2e26e734c19cd2d51aec4aa` | A |
| 14.3 | 3191-3214 | 2189 | `4a63ef7988c871db44c7acb01eb7fff50db51be87e18bdc8bfcca63c2dec733c` | A |
| 14.4 | 3215-3227 | 739 | `e9387e358eaffbf6a7244c1a7c9e15c237cfce7b2d5a39cd2e05a71af4860f1b` | C |
| 14.5 | 3228-3286 | 5542 | `827f657deaa767316f148b3854a8d22af7ca48366ecad883e8b87be5603f306b` | C |
| 14.6 | 3287-3293 | 481 | `2fb09568b7cb3df4e323a9d6e3e827531df83bc3946a4037914e696d6fa31758` | A |
| 14.7 | 3294-3313 | 1889 | `9ff8c5e2294c536cf181757fbb2457fe4189ffdc6e3847ec72ecddf474b908d3` | R |
| 15 | 3314-3315 | 139 | `c28ab08b1a6cf57c5c65775871754ab7312225c4fb76ff455a1da064d04a35d0` | C |
| 15.1 | 3316-3346 | 2739 | `febdbcf0c70dd9085e6364d21f26d46ab1c41a34e633573207d279624fcb8027` | A |
| 15.2 | 3347-3354 | 492 | `a7775b11541a8699f89078f0989a3000b53b50b94a0ef73ec4984b24523e58d2` | A |
| 15.3 | 3355-3426 | 6853 | `a75b83706d17e4cb4a01b0c0f64552476880738538caf91fa8512a75fee13334` | A |
| 15.4 | 3427-3441 | 1401 | `9b3b2b684c75092b5ec7cbe8f425241d3de45e7d6f40d540741d7245fa600652` | C |
| 16 | 3442-3471 | 2437 | `c6708e6fc8b6169d9517d9f50e198c209197cd36f67c61b681955b201afab56e` | A |
| 17 | 3472-3499 | 5120 | `22632e131fe9a5ea27c4c627c5a0f072fd7ca3028e9ea54b4adafb65bb389927` | A |
| 18 | 3500-3507 | 613 | `e9ac9f10d3a6dc4e47a9292875f4fa00f5c03fa0dbd62c1fcb1268d9258dd6fd` | A |
| 18.1 | 3508-3596 | 9904 | `b49e6c335c8729a14a150e59b1b86580731fcfe4675dc78535f1bea1d086427d` | R |
| 18.2 | 3597-3624 | 3539 | `d7ae301d791e364e8481a12611ae1943704c8040b7f23e768a4737df00d45eca` | R |
| 18.3 | 3625-3641 | 1708 | `5ca975162109cccbfb108571559e22c2a694c61f2c404db2e8ab20c243af8799` | R |
| 18.4 | 3642-3673 | 2682 | `20c3afb07c1c8972c671fd8e55c20f1d72901937af146ac9523bacb9684342c6` | R |
| 18.5 | 3674-3805 | 16874 | `f0f904e1070c0273c2b4e362a0b4b6b99a32c146ec2ad92e4a058e27789ee6b3` | R |
| 18.6 | 3806-3825 | 1480 | `32d4ba200df8768e4b2c34c41b8d61a6515413061ff720e62ab0e21cc53e5c86` | R |
| 19 | 3826-3853 | 2511 | `cd215efb0922abcf42b51d93ad667f3e84b4ae87a005169a3fdae6d4f74fa8f9` | A |
| 20 | 3854-3880 | 2299 | `6191f30357dfa246691c9046c424b32a56cd835f8a2604b330525a087b5b656f` | R |
| 21 | 3881-3981 | 12990 | `b229d634e5690dc3b3b5759ea904396b6caab5676231307c0d880c11dcf39185` | R |
| 22 | 3982-3983 | 123 | `b54545344d2fa2a11b5eb45e57b506b71db7804be049af649f17c3c500268df0` | C |
| 22.1 | 3984-3990 | 447 | `2b1b5b5b560192d039e64e0bfba3e6f7bb0f4a821b43ffdc176e3880836002fb` | C |
| 22.2 | 3991-3999 | 829 | `4b3bc48c8f9987d6b8f27783d5bc73cd86d6fd0b649018137ae2f358364aadf6` | C |
| 22.3 | 4000-4077 | 7115 | `a37e86a046a9ee7bc05112efa4adf88dfcee1bf177359eb7031a7e194122d24c` | R |
| 22.4 | 4078-4103 | 2237 | `eae043215e8ef2e15d2f919913143cf552da9dc1d4f451b110b5db38bc4912c2` | R |
| App. A | 4104-4167 | 14868 | `1211f48a394f8dd03602066280d11ec7ee0089976919ad7028fa422a3556b9a0` | C |
| App. B | 4168-4176 | 676 | `eef7ebf9b21f869d21e2f3fe24a6052fd5fa503a50145afd3a1676bffaa30fc7` | C |
| B.1 | 4177-4190 | 1323 | `57941dad7009f80a1411a3abd19c2ea22bf68224ec8ea0428c0981fa1f7b1f96` | C |
| B.2 | 4191-4212 | 2052 | `95d90c644144c0552e8af355637c1beff7e46cee8ac2f700e6e3695e7afdb6bb` | A |
| B.3 | 4213-4256 | 11879 | `77a62fff09a0d894d6ec6046f337d314ee9779e41e3c1521d8bfdab72771350b` | A |
| B.4 | 4257-4488 | 28890 | `edb8d043e932bbf1ce539e73e9245d1a8ebf812e6a988cdff8fe44aa0c852964` | A |
| App. C | 4489-4548 | 4399 | `e21904702b855c69feb1afe86117e9088684c70162571459c5b906ea2b9a79c5` | C |
| App. D | 4549-4606 | 8434 | `f00e0b1b9c786fddced73bf368ddd416d57d13b6afcf5d78fad73dd86415e3a1` | C |
| App. E | 4607-4670 | 5709 | `f7d449206492465183052962b4a8ea13d20a28202ac41069c31a283e1d2b06f1` | C |
| App. F | 4671-4715 | 3963 | `4b6f95f0f14f03859e6c6e08222fd51c35a0fc46365a1bf35c31d4d3fb409cc1` | C |
| App. G | 4716-4823 | 10289 | `56ff67770137755792dea29437261ae2a148e41b3f2cbb437f29d942f99df9b1` | C |

Counts (observed by a read-only script over this table; arithmetic JACKAL exact, Appendix H): 45 carried, 41 amended,
38 replaced, and `45+41+38-124` gives 0. v8 has 131 units (`124+7`): the 124 above, the six new subsections §21.1-§21.6
and Appendix H.

### 18.6 New design elements that need the reviewer's attention, and the remaining premises

The new elements: the W-owned identity-mapped user namespace U8 and the credential containment it requires (P-NOCAP,
P-NOSUID, §12.2 "New trust"); the copied mount namespace and the skeleton (P-ROOT, P-MSET, P-SKEL); the scope in
`user-1000.slice` (P-SLICE, V10'); the holder event H(U) and its stated gap (P-IOEXIT); sync provenance (§10.5); the
complete capture (§15.3); the staged-rename setup model (§11.4). The complete premise register is §9.8 N7; this unit
holds no second list.

## 19. Future execution and installed evidence (none of it exists)

AMENDED from v7: lines 3826-3853, 2511 bytes, sha256 `cd215efb0922abcf42b51d93ad667f3e84b4ae87a005169a3fdae6d4f74fa8f9`.
Amendments: the probe list is §13.1's; the installed-evidence review adds the S-discharges of §9.8 N7 (each matched to
the installed build: P-KSRC first) and the review of the complete capture (V-VAULT, V-BACKUP); "first engineering run"
is withdrawn as a qualification of anything (§9.8 N7 P-VIEW).

## 20. Non-claims

- No sufficiency is claimed for any requirement. V5-B01, V5-B02, W1-V5-PRESERVATION, W1-V6-READ-MUTATION, Gate 0 and
  every original Phase One obligation (the 219 entries of `OBLIGATIONS-v2.json` included) stay OPEN with their owners,
  releases and dependencies.
- The same-identity view is not established as preserving the original success domain (§21, §22.4). No change it
  makes is presented as an accepted exception, a narrowed case or a criterion entitlement.
- Every premise of §9.8 N7 is NAMED_UNESTABLISHED. Upstream source readings are not installed-version discharges;
  probes refute and never establish; trusted-base exclusions are assumptions, not test results.
- No probe, selftest, namespace, mount, sudo, setup, vault or window action was performed for v8. The drafting author's
  dated passive observations (Appendix H) are observations of one moment, not properties.
- Exact arithmetic (JACKAL exact, lane `rat`, not formal-bounded, outside the Lean certificate chain) supplies no
  capacity bound, no geometry, no backup completeness and no correctness of any code. No consequence ceiling field was
  returned; the results are informational.
- A kernel-enforced writer boundary is not proof of the frame code, not lead authentication, not target confinement and
  not capacity. The ruled residuals (a)-(d) keep exactly their stated limits.
- v8 requests no approval and adds no gate; every privileged element stays inside the existing reserved operator
  setup and rollback.

## 21. Preservation over the complete original domain [corrections: W1-V7-FULL-DOMAIN; v7: W1-V6-CATALOGUE, W1-V6-PRESERVE; v6: W1-V5-PRESERVATION]

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
preparation, reader, window and backup parts need the separate rows below.

### 21.2 The criterion's repairs

| | Outcome | Treatment |
|---|---|---|
| R1 | the final pass refuses a leaf whose complete `stat_key` changes during the final walk, excluded leaves included (§4.5 item 1) | required by V5-B01 (review: PERMISSIBLE_REQUIRED_CRITERION_REPAIR); OPEN as V5-B01 is |
| R2 | the child stage refuses a recorded or excluded leaf that differs from the admitted parent observation (§4.5 item 2) | required by V5-B01; the author's argument that it fires only after a premise failure or helper misbehaviour is not established |

### 21.3 Target-world changes (V-rows)

"Kept for" names the custody fact whose only available mechanism on this kernel causes the change; that is a reason,
not an entitlement (review: DOMAIN_CHANGE_NOT_CRITERION_ENTITLEMENT). Every row is OPEN until §21.1's relation is
shown for it; "would discharge" names what could.

| | Change (§12.3) | Kept for | Rework done in v8 | Would discharge |
|---|---|---|---|---|
| V1 | no host network | inbound abstract-socket channels | none available without a new privileged component (§22.3: a userspace network forwarder or a notification broker could restore some reachability, each with its own changes) | TOOL-CLOSURE plus the full relation showing no original situation uses the network, or a kernel with a narrower mediating LSM (reserved decision) |
| V2 | no outward pathname UNIX connection; no socket file outside the binds | pathname channels in both directions | the socket places are the two binds, so the target's own servers in its run tree and `TMPDIR` work; nothing else is restricted | as V1 |
| V3 | no mount operations | inherent to V2's mechanism | — | as V1 |
| V4 | set-ID and file-capability `exec` confers nothing | credential containment of an identity-mapped U8 | — | the relation showing no original situation's outcome depends on a set-ID or file-capability `exec` (for example `sudo`, `fusermount3`, `newuidmap`, `ping`) |
| V6' | later host mounts and unmounts do not reach the view | the run path must not be substitutable by a later host mount | every mount present at creation is kept (v7's omissions removed) | the relation for situations with a mount change during a run |
| V7' | private `TMPDIR` | unreachable socket files of the target's own servers | `/tmp` is the host's again | TOOL-CLOSURE for the location of every socket the tools create, which could move the bind to a narrower place |
| V8 | run-path presentation (mount root, skeleton levels, separate D entries) | location custody of the generation; no frame or lead write outside T | no lead step, no refusal, no host write | the relation for situations that use the run directory's other contents |
| V10' | system scope in `user-1000.slice` | an RL scope no non-root process can enter or leave (H(U)) | same ancestor slices as v5; v5's limits and the original scope properties matched; `app.slice`'s shared budget not reproducible | the relation for situations near `app.slice`'s limits or sensitive to CPU and I/O weight siblings |
| V12 | Landlock domain | V2 | only three handled rights | as V2 |
| V13 | namespace-qualified ptrace and accounting effects | the pull closure | the uid, groups and on-host identity are the lead's (v7's V5 removed) | the relation for situations in which the target inspects other processes or reaches a per-user limit |

### 21.4 Frame-side and observer changes (C-rows)

| | Change | Treatment |
|---|---|---|
| C1 | the generation's originals are not readable by the lead; readers use exports, which now include the complete capture; the vault pins the export tree (V-BACKUP) | OPEN until the capture's equivalence for every original reader and backup consumer is shown (§8.5, V-VAULT) |
| C2 | the frame's reads below `source/` and `tmpdir/` change no access time (v5's did) | criterion-serving (V5-B02 read mutation); observable; OPEN |
| C3 | (v7: different host uid) | REMOVED |
| C4 | setup changes visible to every host process: the account, the sudoers and sshd drop-ins, `/var/lib/wlscratch` with its ACLs, `/opt/wlscratch`, images if chosen | reserved operator setup (review: RESERVED_OPERATOR_SETUP_NOT_NEW_AUTHORITY); exact ordinary states still to be established; OPEN |
| C5 | added cost before launch (RL's two stages, the view, the censuses) and after (the capture) | OPEN: outcomes that depend on cost are in the relation (§21.1) |
| C6' | label lifecycle: v5's lead could free a label by deleting the run directory; a generation in T cannot be deleted by the lead | OPEN; every state reachable through frame verbs has v5's outcome (§3.3) |
| C7 | the scope is listed by the system manager, not by `systemctl --user` | part of V10'; OPEN |
| C9 | process attributes that cannot be reproduced identically: the session and process group (sudo's chain), CPUs gone offline | recorded per attempt; OPEN |

### 21.5 Non-success outcomes in states the original accepts (D-rows)

| | Outcome | Treatment |
|---|---|---|
| D1 | K shows an earlier RL scope populated while M shows it ended | OPEN; P-MGR says this state does not arise; refuted → redesign |
| D2 | RL cannot build the view (a namespace, mount or credential step fails, for example from kernel resource exhaustion) | OPEN: new non-success states; the lead-created mount point and its refusal are removed; v7's invitation to a reviewer ruling is removed |
| D3 | an original observation taken in the view differs from its baseline | OPEN (P-VIEW is a relation; each run's comparison is evidence for that run only) |
| D4 | Gate 0 deferral with the W-1 allowances, A_capture included | the original storage ruling's own deferral (review: PERMISSIBLE_ORIGINAL_STORAGE_DEFERRAL_IF_COMPLETE); no cap, no release gate; OPEN as safe fresh capacity is |
| D5 | (v7: new control deadlines) | REMOVED (§7.4) |
| D6 | W-1 machinery: lease held, channel failure, first-act failure, RL identity failure, record membership `fallback`/`raw`/`unknown`, provenance `failed`/`unobserved`, branched journal, export or capture failure, recovery needed | OPEN: truthful failure reporting, not a redefinition of success; no causal absolute is claimed (a heavily loaded host can make any of them more likely) |
| D7 | C's run-path alias check refuses (§4.5 item 4) | v5-class: v5 refused a run directory its held location chain no longer reached; OPEN only as the mapping argument |

### 21.6 What remains, and what would discharge it

Every V-, C- and D-row marked OPEN keeps W1-V5-PRESERVATION OPEN, and with it V5-B01 and V5-B02. A row is discharged
only by the relation of §21.1 established for it over the complete original domain, with source-to-binary
correspondence for the tools and the frame (review: strings, sampled runs or the absence of a known counterexample do
not discharge), or by a redesign that removes the change. No row is narrowed by restricting the domain, adding a gate,
stripping an attribute or calling a failure accepted.

## 22. Architecture evaluation: enforcement designs beyond the unprivileged DAC architecture [correction: W1-V6-PRESERVE]

CARRIED from v7: lines 3982-3983, 123 bytes, sha256 `b54545344d2fa2a11b5eb45e57b506b71db7804be049af649f17c3c500268df0`.

### 22.1 The question, with the success domain fixed

CARRIED from v7: lines 3984-3990, 447 bytes, sha256 `2b1b5b5b560192d039e64e0bfba3e6f7bb0f4a821b43ffdc176e3880836002fb`.

### 22.2 The review's K0 ruling (verbatim, `review.json` `k0_assessment`)

CARRIED from v7: lines 3991-3999, 829 bytes, sha256 `4b3bc48c8f9987d6b8f27783d5bc73cd86d6fd0b649018137ae2f358364aadf6`.

### 22.3 Candidates, re-evaluated [correction: W1-V7-ARCHITECTURE]

The reviewer's direction (`architecture_assessment`, in part, verbatim): "Candidate (a)+Landlock is a plausible custody
research direction that removes copy-induced inode/attribute substitutions, not an endorsed design or an authorized
implementation direction. Its custody conclusion is conditional and incomplete. The c8 ptrace rejection is wrong for
the documented commoncap rule; blanket seccomp-user-notification impossibility and instantaneous
cgroup/manager/holder equivalence are overstated. Re-evaluate lesser-change root-owned, same-host-UID namespace designs
before claiming (a) alone is viable."

**c8 first: a launcher-built user namespace that keeps the target's host uid.**
- *Pull routes.* Re-evaluated in §9.8 N2 on the quoted commoncap and `__ptrace_may_access` text: an outside
  `sicarii` process passes the uid half and fails the capability half, because the target's user namespace is not its
  own and its owner is not `sicarii`. v7's rejection omitted exactly that half. **Root ownership (or any owner that no
  untrusted process has as its euid) is what makes this hold**; a namespace that `sicarii` itself created would give
  every `sicarii` process the owner rule and every capability over the target.
- *Push routes.* The uid does not matter for them: they need the same three mechanisms as (a) — a private network
  namespace for abstract sockets, Landlock `RESOLVE_UNIX` for outward pathname connections, `MAKE_SOCK` confined to
  places only the view can name for inward ones (§9.8 N1). With the target's host uid unchanged, its `TMPDIR` must be
  private if its tools create sockets there; its `/tmp` need not be, because no socket may be created there.
- *Name routes.* On disk the generation lies below the W-owned g, which `sicarii` cannot search; the binds exist only in
  the view's mount namespace; links and renames across mounts do not succeed; file-handle decoding needs mapped owners
  on the whole ancestor chain, which g breaks (§9.8 N3). A root-owned 0700 ancestor (or W-owned, as g is) achieves the
  name barrier for every outside principal; mount-namespace hiding is needed only to give the target its original
  paths, not for the barrier.
- *Set-ID.* With the identity map, a set-user-ID-root `exec` would make the target root in its namespace; every mount is
  therefore `nosuid` (V4). Leaving 0 unmapped instead would show every root-owned object with the overflow owner, a
  larger change.
- *Ownership choice.* Root-owned (c8 as stated) and W-owned (SIV) namespaces give the same pull closure. They differ in
  per-user accounting: the kernel charges a child namespace's per-user counts at the parent level to the namespace's
  owner (P-UCOUNT), so with root ownership a target could consume root's inotify and namespace budgets, which host
  services share. SIV uses W, whose only processes are the frame's, and W is already the trusted owner of g.
- *Holder event.* The uid does not help: an outside `sicarii` process cannot enter a root-owned system scope either way,
  and a user-manager scope is delegated to `sicarii`, so its processes can migrate in and out (the common ancestor's
  `cgroup.procs` is `sicarii`'s, observed 2026-10-05T15:51:43Z for `user@1000.service`). So the scope stays a system
  scope; placing it in `user-1000.slice` keeps v5's ancestor slices.
Result: **c8 is sound under the premises of §9.8 N7 with the push and name mechanisms above, and it changes less than
(a).** SIV is c8 with a W-owned namespace.

**seccomp, narrowed** (installed `/usr/include/linux/seccomp.h`, read 2026-10-05T16:14:58Z: classic filters run over
`struct seccomp_data` (line 62), the syscall number, architecture, instruction pointer and `args[6]` (line 66); the
header's own caution about `SECCOMP_USER_NOTIF_FLAG_CONTINUE` begins at line 85 and the flag is defined at line 109;
`SECCOMP_IOCTL_NOTIF_ADDFD` at line 152):
- Classic filters cannot inspect pointed-to memory (a `msghdr`, a `sockaddr`, a path): they can deny a system call
  family, not "a descriptor of an admitted entry to an outside process". Correct as v7 stated.
- User notification with a decision on target memory followed by `CONTINUE` is unsound, because the target can change
  that memory between the supervisor's read and the kernel's own. **This is the excluded mechanism, and only this.**
- Requests submitted through `io_uring` (for example its send-message operation) do not pass through the seccomp
  filter as system calls, so any seccomp design must also deny or mediate `io_uring` (a change).
- An *emulating broker* is not excluded: a root supervisor that performs `connect`, `sendmsg`, `bind` and related calls
  itself on copied arguments, refuses `SCM_RIGHTS` that carry a descriptor on a view bind (and any UNIX socket, whose
  queue could carry one), and returns results with `ADDFD`. It could replace V1 and V2 with narrower refusals. Its cost:
  a new privileged per-attempt component in the trusted base; exact emulation of every call's semantics, errors,
  partial transfers, flags and credentials (itself a full-domain obligation); `io_uring` denied; seccomp visible to the
  target; and the refusal of descriptor passing to outside processes, which is still a change. No such emulator exists
  or is specified; it is a candidate for reworking V1 and V2 if TOOL-CLOSURE shows that they matter, not an adopted
  design.

**The comparison** (custody "under premises" means: established under the premises of §9.8 N7, none established):

| Candidate | Custody under premises | Target-world changes | New trusted components | Verdict |
|---|---|---|---|---|
| (a) v7 view, host uid R | yes | V1-V12 of v7, including the host identity change, the root idmap, omitted mounts, masks, private `/tmp`, the lead step | RL, three identities | superseded by SIV, which removes six of its changes |
| c8, root-owned, same uid | yes | SIV's, plus the target's per-user counts charged to root | RL | not adopted (host-wide accounting effect) |
| **SIV** (c8, W-owned) | yes | §12.3 | RL, one identity | **adopted** |
| SIV + PID namespace, user-manager scope | no: a delegated scope lets processes leave and enter, which breaks v5's terminal predicate | adds a PID namespace and a new `/proc` | RL | rejected |
| SIV without network namespace (Landlock abstract scope) | no: inbound abstract connections stay open | fewer | RL | rejected |
| SIV + userspace network forwarder | yes | V1 replaced by changed addresses and interfaces | RL plus the forwarder | not adopted; a V1 rework candidate |
| SIV + emulating seccomp broker in place of V1/V2 | possible, not specified | narrower refusals, `io_uring` denied, seccomp visible | a root broker | not adopted; a V1/V2 rework candidate |
| b, Landlock alone | no (inbound callers unconstrained) | — | — | insufficient (review agrees) |
| b, seccomp classic alone | no | — | — | insufficient |
| c1 distinct uid alone | no | — | — | insufficient |
| c2 BPF LSM / another per-domain LSM | possible with a narrow `file_receive`/`unix_stream_connect` policy | potentially fewest | a kernel with that LSM (an existing reserved toolchain/deployment decision) | unavailable on this boot (`CONFIG_BPF_LSM` not set; LSMs `capability,yama,landlock`) |
| c3 fanotify | not alone; combinations unestablished | — | — | insufficient alone |
| c4 separate kernel | not specified; nested virtualization UNVERIFIED | wholesale | a VM | not adopted (fidelity objection, not impossibility) |
| c5 copies, overlays | substitutes inodes and attributes | — | — | rejected (the fixed target) |
| c6 revocation, c7 locks and leases | no general mechanism | — | — | insufficient |

### 22.4 Conclusion

**v8 adopts the same-identity view** because, of the candidates that establish the custody facts under named
premises, it has the smallest set of changes: against (a) it removes the host identity change (V5, C3), the root idmap
and the omitted mounts (V6's first half), the masks (V9), the private `/tmp` (V7's first half and P-TMPAGE), the lead
preparation step and its refusal (V11, D2's first case), the label-logic change in the frame-verb states (C6), the new
deadlines (D5) and two identities; it adds none that (a) lacked except the accounting form of V13, which (a) had in
another form (counts against R). It does **not** preserve the original success domain as established: §21's OPEN rows
remain, and the two rework candidates (a network forwarder, an emulating broker) and the preserving-direction
candidate (a narrower LSM in a different kernel, a reserved decision) are not designed here. **V5-B01, V5-B02,
W1-V5-PRESERVATION and W1-V6-READ-MUTATION stay OPEN.** If any premise of §9.8 N7 fails, W-1 must be redesigned for
it; no exception is taken.

## Appendix A. Verbatim criteria

CARRIED from v7: lines 4104-4167, 14868 bytes, sha256 `1211f48a394f8dd03602066280d11ec7ee0089976919ad7028fa422a3556b9a0`.

## Appendix B. Schemas (exact key sets; every record also carries the §4.4 common fields)

CARRIED from v7: lines 4168-4176, 676 bytes, sha256 `eef7ebf9b21f869d21e2f3fe24a6052fd5fa503a50145afd3a1676bffaa30fc7`.

### B.1 Role identity: `wlscratch-role-identity-v1`

CARRIED from v7: lines 4177-4190, 1323 bytes, sha256 `57941dad7009f80a1411a3abd19c2ea22bf68224ec8ea0428c0981fa1f7b1f96`.

### B.2 Participants, waits, scopes, census [corrections: W1-V6-SCAN-STATE; v6: W1-V5-REVOCATION-CONFINEMENT; v5: W1-CUSTODY-CLOSURE]

AMENDED from v7: lines 4191-4212, 2052 bytes, sha256 `95d90c644144c0552e8af355637c1beff7e46cee8ac2f700e6e3695e7afdb6bb`.
Amendments: the census record's key set replaces `cred` with `k` (the kernel census: per RL scope `name`, `populated`,
`procs`) and `m` (the manager census: per unit `LoadState`, `ActiveState`, `SubState`), each with `observed_at`; the
cgroup paths read `/user.slice/user-1000.slice/<U>`.

### B.3 Records [corrections: W1-V6-COMMIT-AMBIGUITY, W1-V6-EVIDENCE-RESTORE, W1-V6-INVARIANTS; v6: W1-V5-REVOCATION-CONFINEMENT; v5: W1-PROTOCOL-FAILURE-STATES, W1-JOURNAL-CONTINUATION, W1-SETUP-IDENTITY, W1-CUSTODY-CLOSURE]

AMENDED from v7: lines 4213-4256, 11879 bytes, sha256 `77a62fff09a0d894d6ec6046f337d314ee9779e41e3c1521d8bfdab72771350b`.
Amendments: `launch.json` adds `process_attributes` (§8.3: `uid`, `gid`, `groups`, `cap_bnd`, `rlimits` as
`{name: [soft, hard]}` for every `RLIMIT_*`, `nice`, `sched` `{policy, priority}`, `ioprio`, `affinity`,
`oom_score_adj`, `personality`, `timerslack_ns`); `launcher-rl-identity.json` adds `user_ns {inode, owner_uid,
uid_map, gid_map}`, `idmap_ns {uid_map, gid_map}`, `mnt_ns {inode, id}`, `net_ns {inode}`, `root {dev, ino,
mnt_id}`, `binds [{dest, mnt_id, root_dev, root_ino, attrs}]`, `run_path_mode`, `skeleton {d, created, attached,
omitted}` and `scope_properties`; every journal record body adds `prior_sync` (§10.1 step 5); every `synced` field
reads `sync` (`ok` or `failed`) in the writer's own records and `sync_provenance` in derived records; the export
manifest adds `capture-manifest.json` (`wlscratch-capture-v1`, §15.3 amendment 2).

### B.4 Channel kinds (body key sets) and the states that permit them [corrections: W1-V7-C3-DATA, W1-V6-C1-DATA, W1-V6-COMMIT-AMBIGUITY; v6: W1-V5-PROTOCOL-REFUSALS, W1-V5-REVOCATION-CONFINEMENT; v5: W1-PROTOCOL-FAILURE-STATES; v4: W1-GENERATION-PROTOCOL]

AMENDED from v7: lines 4257-4488, 28890 bytes, sha256 `edb8d043e932bbf1ce539e73e9245d1a8ebf812e6a988cdff8fe44aa0c852964`.
Amendments (correction W1-V7-C3-DATA): the body of `RECORDS` is exactly `{journal_head, records}`, where `records` is
the ordered list of §9.3 C2 (amendment 4), each element exactly `{name, sha256, bytes, marker}`, with `bytes` the
record's committed bytes (base64, chunked by v7's chunk rules) and `marker` the descriptor of its committed close
marker; a missing, extra or reordered element, a digest mismatch or a view-fact mismatch makes C answer
`CHILD_REFUSAL` in state `RECORDS`. `RECORD_COMMITTED` adds `sync` (`ok` or `failed`) and `errors`. Every state's
"deadline" column reads "EOF" (§7.4). `RL_IDENTITY`'s body adds the fields of `launcher-rl-identity.json` (B.3).

## Appendix C. JACKAL results used in this document

CARRIED from v7: lines 4489-4548, 4399 bytes, sha256 `e21904702b855c69feb1afe86117e9088684c70162571459c5b906ea2b9a79c5`.

## Appendix D. v5 joins and where v4 performs them [corrections: W1-V6-C1-DATA; v4: W1-GENERATION-PROTOCOL]

CARRIED from v7: lines 4549-4606, 8434 bytes, sha256 `f00e0b1b9c786fddced73bf368ddd416d57d13b6afcf5d78fad73dd86415e3a1`.

## Appendix E. v5's JACKAL results and dated passive observations

CARRIED from v7: lines 4607-4670, 5709 bytes, sha256 `f7d449206492465183052962b4a8ea13d20a28202ac41069c31a283e1d2b06f1`.

## Appendix F. v6's JACKAL results and dated passive observations

CARRIED from v7: lines 4671-4715, 3963 bytes, sha256 `4b6f95f0f14f03859e6c6e08222fd51c35a0fc46365a1bf35c31d4d3fb409cc1`.

## Appendix G. v7's JACKAL results and dated passive observations

CARRIED from v7: lines 4716-4823, 10289 bytes, sha256 `56ff67770137755792dea29437261ae2a148e41b3f2cbb437f29d942f99df9b1`.

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
