# Isolation and storage proposal W-1, v5: protected writer, gated target account, committed records (specification)

**Status.** Drafting author's design specification, written 2026-10-05 UTC for the Claude Code lead. It is a
CANDIDATE specification of the protected-writer confinement design for the scratch proof frame, and a targeted
successor to v4.
- Nothing in it is implemented, installed, approved, executed or reviewed. No account, group, ACL, sudo rule,
  installation, drop-in, mount, linger, unit, probe, selftest, vault, adoption or window action has been performed
  for v5.
- Proof dispatch stays blocked by the confinement criteria (V5-B01, V5-B02, both OPEN) and by the capacity gate
  (Gate 0, NOT ESTABLISHED).
- v1 (`ISOLATION-STORAGE-PROPOSAL.md`, sha256 `a27d3e74305b5edd47acd31a7c881d7147cfecdaa0935195e2b0acea1dc70442`),
  v2 (`ISOLATION-STORAGE-PROPOSAL-v2.md`, sha256 `1c116f27bd11bcd3e2fae0d00792b27c2e598928bb9ccc97f1db418102232cf6`),
  v3 (`ISOLATION-STORAGE-PROPOSAL-v3.md`, sha256 `97f39c8967ec32538474827256271e65ab8ee0347165aa971b5887608e02ed8c`)
  and v4 (`ISOLATION-STORAGE-PROPOSAL-v4.md`, sha256 `a1924e74555ca85169e33d25d9fd9adc0c89f2a19fbc846edd7c49ed11b49c1c`,
  321052 bytes, with `v4-support/jackal.json` sha256 `298caa0371fe7f2b3af90f71f24e27e25051cc09c698bbec6bf469ed77f547a5`,
  4566 bytes) are preserved unchanged.
- **Form.** This file is a delta over v4. The complete v5 specification is v4 composed with this file by the rule of
  §0.1: every v4 unit that v5 does not change is carried byte-for-byte by its line range, size and sha256 (§18.5);
  changed units are either replaced by a unit of this file or amended by exact old/new text (§0.4); three units are
  new.
- v5 is written against the sealed actual gpt-6.1-sol review `wt-1/package-review/gpt61-v4` of DRAFT-v7 and W-1 v4
  (verdict NOT_READY; hashes verified before drafting: REVIEW.md
  `75f297ceeed617b60ac073cb513a6514efa4849d8d0cd691d307d3723e5d0138`, review.json
  `70b341d6d7c7f51e7b0fcaa028a705df8d564c33c0087170151bce415d331b9c`, checks.json
  `e8404e77ff85dfd6e7c5a56d083c7827057b4949c20fba26ea215551ca63f449`, review-freeze.json
  `314cfa294a03247e70d9c8026bdc28b73fd0e07f42ec25100d26dd8357d7376a`). Its six required W-1 corrections
  (W1-CUSTODY-CLOSURE, W1-PROTOCOL-FAILURE-STATES, W1-JOURNAL-CONTINUATION, W1-SETUP-IDENTITY, W1-SETUP-RECONCILIATION,
  W1-IMAGE-OBSERVATION; JACKAL exact, parsed `1+1+1+1+1+1`), quoted verbatim in §18.1, and every prior correction, gap
  and sub-gap it rules NOT_CLOSED are mapped in §18. Its package correction PKG-V7-AUTHOR-RECORDS concerns the lead's
  package text, not this proposal, and is not addressed here.
- **§18 gives the author's own assessment (CLOSED-AT-SPEC-LEVEL or OPEN) for an independent actual gpt-6.1-sol
  reviewer to judge. It is not closure, and no row says a section "answers" a finding.**
- Authority. Design and frame code are routine reversible engineering under the human's preserved authorization; no
  in-principle approval is needed for them. Reserved to the operator: actual privileged setup (accounts, groups, ACLs,
  sudo, sshd configuration, the user-manager drop-in, installation, mounts, linger, reconciliation, rollback) on a
  concrete reviewed inventory; material API/ABI/owner-policy changes; toolchain/deployment architecture; merge,
  release, install, sudo, production and real PRIME. Every operator choice v5 mentions lies inside that reserved setup
  and rollback. v5 adds no other approval gate.
- Every "verify", "check", "probe", "selftest" or "observe" below names future work, except the passive observations
  explicitly dated and attributed to the drafting author (Appendix E). Design text is not executed evidence.

**Inputs read for v5** (read-only): the gpt61-v4 `REVIEW.md` and `review.json` above (checks.json and
review-freeze.json hash-verified only); v4 and its support file above; frame v5 `scratch.py`
`f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86` (only the lines that name `vault`); the installed
manual sources of systemd(1), systemd.exec(5), systemd.unit(5) and bash(1); host listings dated in Appendix E.

**Non-claims, short form** (full list §20). No sufficiency is claimed. V5-B01, V5-B02, Gate 0 and every original
Phase One obligation stay OPEN with their original owners, releases and dependencies. A kernel-enforced writer boundary
is not proof of the frame code, not lead authentication, not target confinement and not capacity. Installed
verification of every premise named in §9.8 K7 is future work; if a premise fails, W-1 must be redesigned, and no
exception is taken.

---

## 0. Reading guide, composition and what changed from v4

### 0.1 Composition rule

A *unit* of a document begins at each line, outside fenced code blocks, that starts with `# `, `## ` or `### `, and
runs to the line before the next unit's first line (the last unit to the end of the file). v4 has 106 units, each
listed in §18.5 with its v4 line range, size in bytes and sha256. The complete v5 text is v4's units in v4 order, each
treated by its status in §18.5:
- **CARRIED**: the v4 unit's bytes, unchanged.
- **AMENDED**: the v4 unit's bytes with every amendment of §0.4 that names it applied: each amendment's old text (the
  lines of its first `text` block, joined by newlines, without a final newline) occurs exactly once in that unit and is
  replaced by its new text (the lines of its second `text` block).
- **REPLACED**: the unit of this file with the same heading number. This file's title unit and its §0 (the `## 0` unit
  with its `### 0.x` units) replace v4's title and §0. v4's §18 group (its `## 18` unit and six `### 18.x` units) is
  replaced unit by unit by this file's §18 group.
- **NEW**: the units of this file that v4 does not have, at these places: §9.8 after §9.7; §13.1 after §13; Appendix E
  after Appendix D.
Units of this file appear in composed order. "v4:N" is line N of the v4 file. Every cross-reference resolves in the
composed text. The counts: 69 carried, 21 replaced and 16 amended v4 units (counted by the read-only script that
computed §18.5's hashes; JACKAL exact, parsed `69+21+16-106` gives 0); with the 3 new units, §18.5 has 109 rows
(JACKAL exact, parsed `106+3`). In the composed text this file's `### 0.1` to `### 0.6` are units as well.

### 0.2 What v5 changes, per required correction

1. **W1-CUSTODY-CLOSURE** (new §9.8; §9.4; §9.3 C7-C11; §11.5 S-F; §13.1; amendments to §2.1, §2.4, §3.2, §4.1, §4.2
   D8, §4.3, §4.5, §5.3, §6.3, §9.1). v4's absorbing-custody argument relied on partition directories staying 0700 and
   on a momentary lease test. v5 replaces it with a mechanism. At each dispatch's parent stage, before its walk, O
   clears every group-class and other-class write bit on the partition contents, in pre-order on held descriptors, and
   records each change (§9.8 K1). The parent walk and C's final pass then require every entry to be W-CLOSED: owner R,
   a regular file or directory, no group-class or other-class write bit, no set-ID bit, one link (K2). The set of
   processes that can hold uid R or GATE is closed: C9's anti-setid filter also denies `io_uring_enter` and
   `io_uring_register`, and the existing S-F drop-in gives M and every process M starts `no_new_privs`,
   `RestrictSUIDSGID=` and an io_uring filter (K3). Custody from the final pass to `exec` then follows from the checks
   the kernel makes at each operation, whatever references, queued or not, any process holds (K4-K5). No target action
   is refused or changed (K6); every premise has a probe and a redesign consequence (K7). The mask promise and the
   mask inventory are one rule (§11.5 S-F). §9.4 states the stronger quiescence property M-QUIESCENT (Q1-Q8), the
   trusted-systemd premises S1-S6 and the absorption lemma that replaces v4's inference from serialized dispatch.
2. **W1-PROTOCOL-FAILURE-STATES** (Appendix B.4; §9.3; §9.4 release procedure; §9.5; §10.7; amendments to §4.2, §4.3,
   §7.1, §7.3). Every F↔W and F↔W2 machine starts in `START`, where `EARLY_REFUSAL` carries any refusal before the
   hello. `REFUSAL` is legal after `HELLO_ACK`, in place of `PHASE_DONE`, after a failed front-parent half and after a
   failed dispatch vault stage, each with its refusal path. C and L have an interruption point immediately before their
   spawn calls: a `STOP` pending there is a refusal; a later `STOP` is forwarded (C) or recorded (L). A failed spawn
   call that leaves no child is reported by `SPAWN_FAILED` (C, with `child-wait.json`, `started: false`) or
   `L_REFUSAL` (L); a failed call that leaves a child is reported by nothing, so `target_started` stays `unknown`.
   `RELEASE` fixes the order within each direction and lets the directions interleave: at the control deadline F
   writes the window without `RELEASE_INTENT_RESULT`, and a late result is legal, recorded and changes nothing. §10.7
   gives verb-specific success for `materialize`, `adopt`, `dispatch`, both `seal-front` modes and F. `EXPORTED` can
   report a failed export. Option B's `RL_IDENTITY` is a frame of its own direction `RL2W`, before `L_HELLO` or
   `O_HELLO`.
3. **W1-JOURNAL-CONTINUATION** (§10.2; amendment to §15.3; Appendix B.3). One chain rule for every consumer. A
   record's commit is the record, a record-bearing marker and a `close` marker; a record is committed only when a later
   chain marker confirms its marker. After any marker failure the writer's next marker is a `continuation` that lists
   every skipped seq with the files present there and overrides any marker at those seqs. Exactly one candidate is a
   successor; more is a branch. First-marker failures, gaps, head selection and prefix cuts follow from the same rule,
   no writer ever confirms another writer's unconfirmed marker, and every raw file is listed by exports exactly once.
4. **W1-SETUP-IDENTITY** (amendments to §11.7 and §4.2 D3; §11.5 S-H and S-I; Appendix B.3). `setup-identities.json`
   never lists itself. Its bytes are sealed from outside (S-I capture, then the installed-evidence review's S, then
   the adoption record's sha256, size and `[dev, ino]`), and every later invocation checks its fixed values and
   compares it with that seal before any mutation.
5. **W1-SETUP-RECONCILIATION** (§11.4, §11.5). Every step is one atom (one object). S-R classifies atoms by
   observation into P, a stated intermediate state, E or *other*, accepts only an E-prefix with at most one atom in
   between, never re-runs an atom in E, and gives every partial state its completing and reversing action. S-R logs
   its own actions in a new log and never extends a stopped script's log. `step.py` writes the whole line or fails; a
   torn last line is tolerated and a malformed line stops S-R. Scripts contain no pipeline: the new helper
   `check_out.py` checks each producer's own status and output, and `-e` is never relied on to observe a producer.
6. **W1-IMAGE-OBSERVATION** (amendments to §3.4, §6.3, §11.7, §14.5). The images directory is root:W 0710, so W and W2
   can `fstatat` the root-owned 0600 image files by name; O and C keep every other mount check. `lost+found` is one
   pinned special entry of each image root, reconciled with the name grammar and the growing-tree rule.

### 0.3 What is carried

The 69 v4 units marked CARRIED in §18.5 are carried byte-for-byte. They include everything the gpt61-v4 review
closed: lease-and-writer-authority and W1-WRITE-AUTHORITY (§5.1, §5.2, §9.7, and §3.4's authority paragraph, which
AM-06 and AM-07 leave untouched); per-entry-modes-acls (§6.1, §6.2, every v4 row of §6.3 except the partition-contents
row, which AM-17 changes, while AM-18 only adds image rows, and §15.3's export primitive, which AM-30 leaves
untouched); denial-probes and W1-VERIFICATION-PROBES (§13,
byte-for-byte; v5's probes are the new §13.1); W1-SETUP-PRESTATE (§11.1-§11.3; `absent.py` is byte-identical inside the
replaced §11.5; AM-24 to AM-27 remove the identity record's self-entry, add the sealed-record, images-directory and
`lost+found` rows, admit `lost+found` in the growing-tree constraint and say how W reads the backing file, and leave
every other pinned and mutable field unchanged); W1-FINAL-PASS (§4.5's items 1-3 and its placement paragraph, which
AM-14 leaves untouched); W1-READ-ACCESS, W1-READ-EXPOSURE and exposure-options (§12); W1-PREFLIGHT-IDENTITY and
fresh-identities-and-vault (§8); W1-SETUP-ORDER (§16, read with §0.6); W1-RESOURCES, resources-and-images,
W1-IMAGE-GEOMETRY and W1-IMAGE-COMPATIBILITY (§14, of which only §14.5's J1 and one sentence are amended); W1-NONCLAIMS.
No original admission join, control, accepted case, criterion, allowance, cap or gate is relaxed.

### 0.4 Amendments (exact old and new text)

Each amendment names its unit and the v4 lines of its old text.

**AM-01** (§2.1, v4:171-173).
```text
They may also hold anything a target
  hands them (open descriptors, connection handles) and may make themselves non-dumpable, so their descriptor tables
  are not assumed observable.
```
```text
They may also hold anything a target
  hands them (open descriptors, connection handles) and may make themselves non-dumpable, so their descriptor tables
  are not assumed observable. They may also hold write permission that a target granted them on what it owns, until
  O's write revocation removes it, before any custody conclusion relies on the partition contents (§9.8).
```

**AM-02** (§2.1, v4:177-179).
```text
passing open descriptors and connection handles to processes of any uid
  (including A1 processes, over abstract sockets), leaving descriptors queued in sockets, and writing everywhere its
  credentials permit outside the generation.
```
```text
passing open descriptors and connection handles to processes of any uid
  (including A1 processes, over abstract sockets), leaving descriptors queued in sockets, changing the modes and ACLs
  of everything it owns (including granting write permission to any uid or gid; set-ID modes excepted, §9.3 C9), and
  writing everywhere its credentials permit outside the generation.
```

**AM-03** (§2.1, v4:182-189).
```text
- **A3, the target account's user manager M** (`systemd --user` of uid `wlscratch-run`, without `wlscratch-gate`).
  After setup M is the account's only process outside the frame's own participants: every user unit, socket and the
  user bus are masked, and M runs without a PAM session, so no `(sd-pam)` helper exists (§11.5 S-F). M executes
  root-installed code, but every uid-R process (T included) can command it and pass it descriptors, so M's *state* is
  treated as attacker-influenced. No benign-service premise is used: final-pass custody and known-terminal ownership
  require that M hold no reference into g and have no foreign unit, job, connection or queued input, and that no
  writable description of an admitted file exist anywhere (§9.4). A state that cannot be observed completely is
  UNKNOWN.
```
```text
- **A3, the target account's user manager M** (`systemd --user` of uid `wlscratch-run`, without `wlscratch-gate`).
  After setup M is the account's only process outside the frame's own participants: every unit file of a
  process-starting type in the user unit load path at inventory time is masked, the user bus included (one rule,
  §11.5 S-F); M runs without a PAM session, so no `(sd-pam)` helper exists; and M and every process it starts run with
  `no_new_privs` and a seccomp filter that denies set-ID modes and the io_uring calls (§11.5 S-F, §9.8 K3). Units that
  are generated when M starts, installed after the inventory or created at run time (transient units) are not masked;
  M-QUIESCENT governs them (§9.4). M executes root-installed code, but every uid-R process (T included) can command it
  and pass it descriptors, so M's *state* is treated as attacker-influenced. No benign-service premise is used:
  final-pass custody and known-terminal ownership require M-QUIESCENT (no foreign unit, job, trigger, connection,
  queued input or pending signal) and no reference of M into g; final-pass custody also requires the write closure of
  §9.8 and that no writable description of an admitted file exist anywhere (§9.4). A state that cannot be observed
  completely is UNKNOWN.
```

**AM-04** (§2.4, v4:252-256).
```text
- **R9, descriptors in transit (v3's limit, now closed by mechanism).** A scan of descriptor tables cannot see a
  descriptor queued in a socket. v4's custody conclusions no longer rest on such a scan: a writable open description
  of an admitted file is detected wherever it is, queued or not, by the lease test; a directory descriptor permits a
  mutation only to a uid-R or GATE process, and all of those are enumerated; M's queues must be empty and M must hold
  no foreign connection (§9.4). What remains is stated in §9.4 as conditions with UNKNOWN outcomes, not as a residual.
```
```text
- **R9, descriptors in transit and retained references (v4's argument withdrawn; closed by mechanism).** A scan of
  descriptor tables cannot see a descriptor queued in a socket or held by a non-dumpable process, and v5's custody
  conclusion does not need one: a writable open description of an admitted file is detected wherever it is, queued or
  not, by the lease test (premise L1, §9.8 K7); once the partition contents are write-closed (§9.8 K2), any other
  retained reference (a read-only, `O_PATH` or directory descriptor, a current directory, queued or held) lets its
  holder do only what the holder's own credentials allow at the moment of each operation, and the credentials that
  could change the generation are confined to enumerated processes (§9.8 K3-K5); M's queues must be empty and M must
  hold no foreign connection (§9.4). v4's statement that a directory descriptor permits a mutation only to a uid-R or
  GATE process rested on partition directories staying 0700, which the target can change; it is withdrawn. What
  remains is stated in §9.4 and §9.8 as conditions with UNKNOWN outcomes and as premises with probes, not as a
  residual.
```

**AM-05** (§3.2, v4:289).
```text
| M, user manager | `systemd --user` of R (lingering; every unit masked; no PAM session) | `user@<R>.service` | systemd |
```
```text
| M, user manager | `systemd --user` of R (lingering; the unit files of §11.5 S-F masked; no PAM session; `no_new_privs` and the S-F seccomp filter) | `user@<R>.service` | systemd |
```

**AM-06** (§3.4, v4:357-363).
```text
**Names.** The entries of T_root are exactly: generation roots (`^[0-9a-f]{32}$`), `records`, and `selftest-<h>`. The
entries of R_root are exactly: record roots (`^[0-9a-f]{32}$`, each matching an existing generation root),
`adoption-<I>` (`^adoption-[0-9a-f]{64}$`) and `selftest-<h>`. Each is a W-owned directory. With images, each image
root also contains `lost+found` (root-owned, 0700, created by `mkfs.ext4`), which W never uses. W lists T_root and R_root
at every invocation and refuses before any mutation if an entry falls outside this grammar or is not a W-owned
directory (with images, `records` must be the records mount, below). Only W or root can create entries there, so an
unexpected entry is a defect, not an adversary's move, and it refuses.
```
```text
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
```

**AM-07** (§3.4, v4:379-384).
```text
- `A_T` must be the root of the work image: its `st_dev` differs from that of `/var/lib/wlscratch`; `/proc/self/mountinfo`
  has exactly one entry whose mount point is `/var/lib/wlscratch/runs`, whose major:minor equals `A_T`'s `st_dev`, whose
  fs type is ext4, whose super options include the reviewed ones and whose mount options include `nosuid,nodev,noexec`;
  its source is a loop device whose `/sys/block/<loop>/loop/backing_file` names the pinned image file, and that file's
  `[dev, ino]` (by `lstat` on the root filesystem) equals the pinned one; `/dev/disk/by-uuid/<pinned UUID>` resolves to
  that loop device; the image root's owner, group, mode and ACL equal the pinned ones.
```
```text
- `A_T` must be the root of the work image: its `st_dev` differs from that of `/var/lib/wlscratch`; `/proc/self/mountinfo`
  has exactly one entry whose mount point is `/var/lib/wlscratch/runs`, whose major:minor equals `A_T`'s `st_dev`, whose
  fs type is ext4, whose super options include the reviewed ones and whose mount options include `nosuid,nodev,noexec`;
  its source is a loop device whose `/sys/block/<loop>/loop/backing_file` names the pinned image file;
  `/dev/disk/by-uuid/<pinned UUID>` resolves to that loop device; the image root's owner, group, mode, ACL and inode
  number equal the pinned ones. W and W2 also check the backing file itself, which needs search permission on its
  directory: they open `/var/lib/wlscratch-images` with `O_PATH|O_DIRECTORY|O_NOFOLLOW` through an anchored chain (it
  is root:W 0710, so W can search it but not list it, §14.5 J1), require that directory's pinned identity, and require
  by `fstatat(images, <name>, AT_SYMLINK_NOFOLLOW)` a regular file with the pinned `[dev, ino]` and size, uid 0, gid 0,
  mode 0600 and one link. O and C (uid R) cannot search that directory; they make every other check of this item and
  rely, for the file itself, on W's check in the same invocation before W started them, since only root can change what
  is mounted.
```

**AM-08** (§4.1, v4:407-409).
```text
- **Partition contents.** Entries below the four partition roots are written only by targets of launched attempts
  (through the gate group, §6.3). They are not frame writes. They are part of what each later attempt admits, so every
  attempt re-observes them in full (§4.5).
```
```text
- **Partition contents.** Entries below the four partition roots are created and written only by targets of launched
  attempts (through the gate group, §6.3); the frame never writes their content or names. The frame's only action on
  them is O's write revocation at each dispatch's parent stage (§9.8 K1), which clears the group-class and other-class
  write bits of entries owned by R and changes nothing else; it is a frame mutation inside T, recorded in P_att. They
  are part of what each later attempt admits, so every attempt re-observes them in full (§4.5).
```

**AM-09** (§4.1, v4:422-423).
```text
The partitions are disjoint. Every frame mutation after a generation's creation lands in a P_att, a P_exp or a P_ado,
never in P_adm.
```
```text
The partitions are disjoint. Every frame mutation after a generation's creation lands in a P_att, a P_exp or a P_ado,
never in P_adm; the one frame action on partition contents is the write revocation above.
```

**AM-10** (§4.2, v4:509-511).
```text
A failure in M4-M8 leaves a generation that can never be admitted: without a committed materialization marker no
dispatch can use g (D3). W commits `refusal.json` in P_att(g, A0) and its export increment; the partial P_adm stays as
evidence.
```
```text
A failure in M4-M8 leaves a generation that can never be admitted: without a committed materialization marker no
dispatch can use g (D3). W refuses on the path Appendix B.4.4 gives for the state it is in (`EARLY_REFUSAL` before
`W_HELLO`, `REFUSAL` after it); whenever A0's `attempt.json` is committed it commits `refusal.json` in P_att(g, A0) and
an export increment, and otherwise its facts are in `EARLY_REFUSAL` and on its stderr; the partial P_adm stays as
evidence.
```

**AM-11** (§4.2, v4:522).
```text
not adopted); creates `g_rec/attempts/<A>/` with its `commits/` (0700, authenticated); commits **`attempt.json`**
```
```text
not adopted); requires `setup-identities.json` to match the seal that adoption record carries, and the setup identity
  recorded in `generation.json` to equal it (§11.7; otherwise it refuses before any mutation); creates
  `g_rec/attempts/<A>/` with its `commits/` (0700, authenticated); commits **`attempt.json`**
```

**AM-12** (§4.2, v4:535-540).
```text
- D8. State `PARENT`: the writer half (writer-owned recipe walk, snapshot, record pins, location, the attempt-journal
  join of §10.6); then the observer for the parent stage: W creates and syncs the observer stream files, commits
  `observer-intent-1.json` binding them (§9.3, G0), starts S_O → O, and O returns the full walk of `g/source` (with
  every excluded leaf's `stat_key`), the target-context identities `parent`, the helper half of `preflight` (heavy
  processes, meminfo, M's units) and the parent-stage scans of §9.4 including SCAN-QUIESCE and SCAN-LEASE; W commits
  `observer-1-parent.json` and `observer-wait-1.json`. Any failed join or scan refuses the attempt (nothing reserved).
```
```text
- D8. State `PARENT`: the writer half (writer-owned recipe walk, snapshot, record pins, location, the attempt-journal
  join of §10.6); then the observer for the parent stage: W creates and syncs the observer stream files, commits
  `observer-intent-1.json` binding them (§9.3, G0) and starts S_O → O (under Option B, RL → O, and W commits
  `observer-1-rl-identity.json` before its request). O, in this order: takes the first parent-stage scans of §9.4
  (SCAN-GATE = {O}, SCAN-R, SCAN-W, SCAN-UNITS and SCAN-QUIESCE with its barrier; phase `pre`); performs the write
  revocation of §9.8 K1; takes the full walk of `g/source` (with every excluded leaf's `stat_key`), with SCAN-WCLOSED
  and SCAN-LEASE inside it; takes the target-context identities `parent` and the helper half of `preflight` (heavy
  processes, meminfo, M's units); and repeats SCAN-GATE, SCAN-R, SCAN-W, SCAN-UNITS, SCAN-REFS and SCAN-QUIESCE (phase
  `post`). W commits `write-revocation-1.json`, `observer-1-parent.json` and `observer-wait-1.json`. Any failed join,
  revocation or scan refuses the attempt (nothing reserved).
```

**AM-13** (§4.3, v4:602-604).
```text
- **`observer-intent-<n>.json`**: committed before each observer start, after its stream files exist: O's argv (with
  its nonce), the stage, the `[dev, ino]` of `observer-<n>.stdout` and `observer-<n>.stderr`. **`observer-<n>-<stage>.json`**
  and **`observer-wait-<n>.json`**: O's results and S_O's wait.
```
```text
- **`observer-intent-<n>.json`**: committed before each observer start, after its stream files exist: O's argv (with
  its nonce), the stage, the `[dev, ino]` of `observer-<n>.stdout` and `observer-<n>.stderr`. **`observer-<n>-<stage>.json`**
  and **`observer-wait-<n>.json`**: O's results and S_O's wait.
- **`write-revocation-<n>.json`**: the record of O's write revocation at the parent stage (§9.8 K1), sent with O's
  observation and committed with it: every entry examined, every mode changed (before and after, with `[dev, ino]`
  and link counts) and, if the revocation stopped, why. **`launcher-rl-identity.json`** and
  **`observer-<n>-rl-identity.json`** (Option B only; the latter also under `w2-<k>/`): RL's `RL_IDENTITY` frame
  (§7.3), committed before W sends `GO`, or its first `OBSERVE_REQUEST`, to the helper RL started.
```

**AM-14** (§4.5, v4:684-699).
```text
Custody from the final pass to `exec` (V5-B01, second sentence) rests on these facts, each with its own section:
(i) no `sicarii` process can write any P_adm object or partition entry by path (§6.3, §6.5), and a directory
descriptor lets any process do only what its own credentials allow (§9.4, argument (a));
(ii) W does not mutate P_adm after M8, and any other writer instance refuses before its first mutation and before
starting any helper while W holds the lease (§5.1, §5.2);
(iii) GATE can be held only by processes started through the reviewed launcher rule, and no earlier target could mint
a GATE-conferring set-group-ID file, because its whole process tree ran under `no_new_privs` and the anti-setid filter
(§9.3, C9);
(iv) at the final pass, by C's own scans: GATE holders are exactly L and C; uid-R processes are within {L, C, M}; M
holds no reference into g and is quiescent (no foreign unit, job, connection or queued input); and no writable open
description of any admitted partition file exists anywhere, in any process, queue or mapping (§9.4; §9.3, C7 and C10);
(v) that state is absorbing until T's `exec`: no new GATE or uid-R process can appear except through the frame's own
sudo rule, no new writable description of a partition file can be created except by such a process, and L and C are
frame code (§9.4, argument (b));
(vi) root and the kernel are outside the threat model.
This is an argument for review, not evidence.
```
```text
**Write closure in the same walk (v5).** Inside the same walk C also checks W-CLOSED (§9.8 K2) for every entry of the
partition contents, on the descriptors the walk already holds: owner R, a regular file or a directory, no group-class
or other-class write bit, no set-user-ID or set-group-ID bit, one link for a regular file, its partition root's
`st_dev` for a directory. Any violation, or an entry that cannot be examined, refuses the launch. O's parent-stage
walk checks the same after its write revocation (§9.8 K1), so a difference between the two walks in any of these
fields refuses as well, by item 2.

Custody from the final pass to `exec` (V5-B01, second sentence) rests on these facts, each with its own section:
(i) at the final pass every partition entry is W-CLOSED, and no writable open description of an admitted partition
file exists anywhere, in any process, queue or mapping (§9.8 K2; §9.4 SCAN-LEASE, premise L1);
(ii) W does not mutate P_adm after M8, and any other writer instance refuses before its first mutation and before
starting any helper while W holds the lease (§5.1, §5.2);
(iii) the processes that can hold uid R or GATE are only those started through the reviewed sudo rules with their
descendants, and M with its descendants; no set-user-ID or set-group-ID file of R or GATE can be minted, by T's tree
(`no_new_privs` and the anti-setid filter, §9.3 C9) or by M's (the S-F drop-in, §11.5) (§9.8 K3);
(iv) at the final pass, by C's own scans: GATE holders are exactly L and C; uid-R processes are within {L, C, M}; M
holds no reference into g and is M-QUIESCENT apart from C's own connection (§9.4; §9.3 C7 and C10);
(v) that state is absorbing until T's `exec`: by (i) and (iii) every process other than L, C, M and root is denied
every mutation of the admitted generation at the moment it attempts it, whatever descriptors or references it holds,
queued or not (§9.8 K4-K5); M stays quiescent by the absorption lemma of §9.4; and L and C are frame code;
(vi) root and the kernel are outside the threat model.
This is an argument for review, not evidence; its kernel and systemd premises are listed with their probes in §9.8
K7.
```

**AM-15** (§5.3, v4:836).
```text
every unit that would start a process is masked, including `dbus.socket` and `dbus-broker.service`, and M runs without a PAM session (S-F drop-in)
```
```text
every unit file of a process-starting type in the user unit load path at inventory time is masked, including `dbus.socket` and `dbus-broker.service` (one rule, §11.5 S-F; generated, later-installed and transient units are not masked and are governed by M-QUIESCENT, §9.4), and M runs without a PAM session and with the S-F drop-in's `no_new_privs` and seccomp filter
```

**AM-16** (§5.3, v4:844).
```text
That would confer only R, which reaches nothing in g (g's ACLs name GATE, §6.3), and any process holding R is an unknown participant (§9.4)
```
```text
Such a file would confer R, and R has owner rights on the partition contents through any retained descriptor, so v5 prevents every process tree of uid R from minting one: T's by C9 (§9.3) and M's by the S-F drop-in (§11.5, §9.8 K3); any process holding R is also a participant that every scan sees (§9.4)
```

**AM-17** (§6.3, v4:913).
```text
| partition contents | created by T: uid R, group GATE | as created under umask 077 | none set by the frame | as created | none |
```
```text
| partition contents | created by T: uid R, group GATE unless T changes it | as T leaves it (T may `chmod` and set ACLs on what it owns); from each later dispatch's parent stage, without any group-class or other-class write bit (§9.8 K1-K2) | none set by the frame; T may set entries, whose write permission the cleared group-class bits mask | as T leaves it, then without those write bits | none set by the frame; T may set one, which affects only entries created later, which the next parent stage revokes again |
```

**AM-18** (§6.3, v4:926).
```text
| bare mount points (images only; visible only while unmounted) | root:root | 0700, empty | none | 0700 | none |
```
```text
| bare mount points (images only; visible only while unmounted) | root:root | 0700, empty | none | 0700 | none |
| `/var/lib/wlscratch-images` (images only) | root:W | 0710: search for W only (W and W2 look up the pinned image files by name; nobody but root lists or opens them) | none | 0710 | none |
| the image files in it (images only) | root:root | 0600 | none | 0600 | n/a |
| `lost+found` of each image root (images only; made by `mkfs.ext4`; never used, opened or walked by the frame) | root:root | 0700 | none | 0700 | none |
```

**AM-19** (§7.1, v4:998-999).
```text
Under
Option B, RL sits between S2 and L and passes L's fds through unchanged (§12.2).
```
```text
Under
Option B, RL sits between S2 and L, and between S_O and O, and passes the helper's fds through unchanged (§12.2); before
its `exec` it writes exactly one `RL_IDENTITY` frame on fd 0, on a direction of its own (§7.3).
```

**AM-20** (§7.3, v4:1029-1032).
```text
- The first message from the helper side of each channel (`W_HELLO`, `W2_HELLO`, `L_HELLO`, `C_HELLO`, `O_HELLO`)
  carries that process's own fresh 64-hex nonce and its identity; the first message of the other direction
  (`HELLO_ACK`, `GO`, `RECORDS`, `OBSERVE_REQUEST`) echoes the nonce. Each side refuses a hello whose identity fails
  §8.1's joins.
```
```text
- The first message from the helper side of each channel (`W_HELLO`, `W2_HELLO`, `L_HELLO`, `C_HELLO`, `O_HELLO`)
  carries that process's own fresh 64-hex nonce and its identity; the first message of the other direction
  (`HELLO_ACK`, `GO`, `RECORDS`, `OBSERVE_REQUEST`) echoes the nonce. Each side refuses a hello whose identity fails
  §8.1's joins. A writer that refuses before its hello sends `EARLY_REFUSAL` as its first message instead; it carries
  no nonce, gets no reply, and the channel then ends (Appendix B.4.4).
- **Option B's RL frame.** Under Option B the first frame on the W↔L and W↔O sockets is RL's `RL_IDENTITY`, the only
  message of the direction `RL2W`, whose genesis is §4.4's `head0("RL2W")` computed with the nonce of the helper RL
  serves (`n_wl` or `n_o`); the helper's own `L2W` or `O2W` chain then starts at seq 0 with `L_HELLO` or `O_HELLO`. W
  verifies the frame (§9.3 G3) and commits it before it sends `GO` or its first `OBSERVE_REQUEST`. Under Option A any
  `RL_IDENTITY`, and under Option B a missing or second one, is a channel failure.
```

**AM-21** (§9.1, v4:1243).
```text
Observer participants: every S_O/O started for A, by W or by a W2.
```
```text
Observer participants: every S_O/O started for A, by W or by a W2, and under Option B the RL before each O.
```

**AM-22** (§9.1, v4:1249-1250).
```text
`wlscratch-scan-v2`
(§9.4).
```
```text
`wlscratch-scan-v3`
(§9.4; v4's `wlscratch-scan-v2` with the fields of v5's scans, Appendix B.2).
```

**AM-23** (§9.1, v4:1257-1260).
```text
O's jobs per invocation: the scans of §9.4 that need R credentials (SCAN-UNITS, SCAN-REFS, SCAN-QUIESCE,
SCAN-LEASE), the full walk of `g/source` (v5 `verify_materialization` with v6's final pass, returning every excluded
leaf's `stat_key`), the target-context identities (`parent` or `after`), at `after` the report bytes, and under W2 the
recovery rounds (§9.7).
```
```text
O's jobs per invocation: the scans of §9.4 that need R credentials (SCAN-UNITS, SCAN-REFS, SCAN-QUIESCE,
SCAN-LEASE and, at the parent stage, SCAN-WCLOSED), at the parent stage the write revocation of §9.8 K1 before its
walk, the full walk of `g/source` (v5 `verify_materialization` with v6's final pass, returning every excluded
leaf's `stat_key`), the target-context identities (`parent` or `after`), at `after` the report bytes, and under W2 the
recovery rounds (§9.7).
```

**AM-24** (§11.7, v4:2165).
```text
| Regular setup files: `writer.lock`, `setup-identities.json`, the sudoers files, the sshd and user-manager drop-ins, every installed frame member | type, `dev`, `ino`, uid, gid, mode, `nlink` 1, size, sha256 (`writer.lock`: size 0), no ACL | atime, mtime, ctime | none |
```
```text
| Regular setup files: `writer.lock`, the sudoers files, the sshd and user-manager drop-ins, every installed frame member | type, `dev`, `ino`, uid, gid, mode, `nlink` 1, size, sha256 (`writer.lock`: size 0), no ACL | atime, mtime, ctime | none |
| `setup-identities.json` (never listed in itself; sealed from outside, below) | fixed values checked at every use: type regular, uid 0, gid 0, mode 0644, `nlink` 1, no ACL; sha256, size, `dev` and `ino` compared with the seal below, never with the record's own content | atime, mtime, ctime | none |
```

**AM-25** (§11.7, v4:2168).
```text
| Growing tree directories: `runs/` (T_root) and `runs/records` (R_root) | type, uid, gid, mode, exact ACL text; without images also `dev` and `ino`; with images the mount identity of the next row instead | `nlink`, size, atime, mtime, ctime, the entry set | every entry obeys §3.4's name grammar and is a W-owned directory; W checks it at every invocation |
```
```text
| Growing tree directories: `runs/` (T_root) and `runs/records` (R_root) | type, uid, gid, mode, exact ACL text; without images also `dev` and `ino`; with images the mount identity of the next row instead | `nlink`, size, atime, mtime, ctime, the entry set | every entry obeys §3.4's name grammar and is a W-owned directory, except, with images, the pinned `lost+found` special entry of §3.4; W checks it at every invocation |
```

**AM-26** (§11.7, v4:2170).
```text
| Image mounts (images only, §14.5) | filesystem UUID and label; the backing image file's `dev`, `ino`, size, mode and owner on the root filesystem; the mount point path; mount options `nosuid,nodev,noexec`; the nesting (records inside work); the image root's uid, gid, mode, ACL and `ino` | the mounted filesystem's `st_dev` (the loop device number), the loop device name, the mount ID | `st_dev` differs from the parent's and equals the device of the mountinfo entry whose loop device's backing file is the pinned image file |
```
```text
| Image mounts (images only, §14.5) | filesystem UUID and label; the backing image file's `dev`, `ino`, size, mode 0600, uid 0, gid 0 and `nlink` 1 on the root filesystem, read by W and W2 through the search-only images directory (§3.4, §14.5 J1); the mount point path; mount options `nosuid,nodev,noexec`; the nesting (records inside work); the image root's uid, gid, mode, ACL and `ino` | the mounted filesystem's `st_dev` (the loop device number), the loop device name, the mount ID | `st_dev` differs from the parent's and equals the device of the mountinfo entry whose loop device's backing file is the pinned image file |
| Images directory `/var/lib/wlscratch-images` (images only) | type, `dev`, `ino`, uid 0, gid W, mode 0710, no ACL; its exact entry set, captured by the operator (W cannot list it) | atime, mtime, ctime | W only looks up the pinned names in it |
| `lost+found` of each image root (images only) | name, type directory, `ino`, uid 0, gid 0, mode 0700, no ACL | `nlink`, size, times, contents (root's; `e2fsck` may add entries; W cannot read them) | never used, opened or walked by the frame |
```

**AM-27** (§11.7, v4:2175-2176).
```text
The setup identity record stores, for every object, the class and the pinned values; `/run/user/<R>` is not a setup
object (logind recreates it) and is observed per invocation.
```
```text
The setup identity record stores, for every object other than itself, the class and the pinned values;
`/run/user/<R>` is not a setup object (logind recreates it) and is observed per invocation.

**Seal of `setup-identities.json` [correction: W1-SETUP-IDENTITY].** The record never lists itself: S-H's generator
leaves it out of every class, so its bytes hold no digest, size or identity of themselves and no fixed point is
needed. Its final bytes are bound from outside, in this order: (1) S-I captures its sha256 (S), size, `[dev, ino]`,
owner, group, mode, link count and ACL text; (2) the installed-evidence review (INSTALLED_REVIEW) reviews that capture
and records S (§4.6, join 2); (3) `adopt` requires, before it writes `lead-adoption.json`, that the live file's sha256
is the S of the installed review it joins, and the adoption record binds S with the size and `[dev, ino]` W read
(`setup_identities_file`, Appendix B.3). Every later invocation opens the live file through an anchored no-follow chain,
checks the fixed values (regular, uid 0, gid 0, mode 0644, one link, no ACL), computes its sha256 and size from the
bytes it reads, and compares them, with `[dev, ino]`, with a seal before its first mutation:
- `dispatch`: the committed adoption record's values (D3), and also the values `generation.json` recorded, so a
  generation materialized under another setup record is refused;
- `seal-front` (W2): the values its attempt sealed (the adoption record pinned in a dispatch attempt's `attempt.json`;
  `generation.json`'s recorded values for A0);
- `materialize`: the committed adoption record of the installed inventory I if one exists; otherwise there is no
  reviewed seal yet, and W records the values in `generation.json` with `setup_seal: unadopted` (v5's `materialize`
  does not depend on adoption, §4.6); such a generation is admitted only after `dispatch` finds those values equal to
  the adoption record's;
- `adopt`: AD3's bookkeeping in P_ado(I) (its directories and `invocation.json`) precedes the check, which is made at
  AD5 against the installed review and precedes `lead-adoption.json`; a mismatch is `REFUSAL`, and no adoption record
  exists;
- `selftest`: records the values only, because the selftests precede the installed review.
A mismatch refuses before any mutation. The pinned and intentionally mutable fields of every other object stay as
tabled above; the record's own atime, mtime and ctime are recorded and never compared.
```

**AM-28** (§14.5, v4:2456).
```text
Each image root contains `lost+found` from `mkfs.ext4` (§3.4).
```
```text
Each image root contains `lost+found` from `mkfs.ext4`, admitted only under §3.4's pinned special-entry rule.
```

**AM-29** (§14.5, v4:2463).
```text
- J1: `install -d -o root -g root -m 0700 /var/lib/wlscratch-images`.
```
```text
- J1: `install -d -o root -g <W> -m 0710 /var/lib/wlscratch-images` (search for W only, so W and W2 can look up the
  image files' pinned identities by name; nobody but root can list or open them; the image files stay root:root 0600,
  J2).
```

**AM-30** (§15.3, v4:2556-2572).
```text
- An export increment n of a journal J (an attempt journal or an adoption journal) is defined by its cut c_n: the head
  (seq, sha256) of J's committed chain when the increment starts (c_−1 lies before seq 0), and, for an attempt journal,
  the writer's next fallback slot index s_n at that moment (s_−1 = 0). Increment n exports exactly: every marker of J
  with c_(n−1).seq < seq ≤ c_n.seq, as a marker file; for each such marker of kind `primary` or `retry`, the record it
  commits (a marker of kind `export` points at a copy that is already in P_exp, so only the marker file is exported);
  the fallback slots with index from s_(n−1) up to s_n − 1, the VALID ones as decoded entries of `fallback-slots.json`
  and the TORN ones by index and the sha256 of their raw 65536 bytes only; and, by path, size and sha256 with state
  `raw`, every uncommitted record file present in the partition at the cut and not listed by an earlier increment. Raw
  bytes (TORN slots, uncommitted records) stay in their protected original place, and they get no success credit.
- After the copies, the increment's `manifest.json` (`wlscratch-export-v2`: per entry the export path, source path,
  sha256, bytes, final mode, `acl_sha256`, source marker digest and state ∈ {`committed`, `fallback`, `torn`, `raw`}, and
  the export directories' identities) and `freeze.json` (`wlscratch-freeze-v2`: increment number, cut c_n, slot range,
  the previous increment's freeze-marker digest, the digest of every export marker committed for this increment, the
  manifest's sha256, channel heads, boot id, time) are written with the export primitive and committed. The export
  markers of increment n and its freeze marker have seq > c_n.seq, so the next increment exports them. The last
  increment's export markers are listed by digest in its own freeze record; only its freeze marker is never exported:
  its digest goes to F in `EXPORTED` and `FINAL` and is printed, and the original stays in the protected journal.
```
```text
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
  state `failed`.
- After the copies, the increment's `manifest.json` (`wlscratch-export-v2`: per entry the export path, source path,
  sha256, bytes, final mode, `acl_sha256`, source marker digest and state ∈ {`committed`, `fallback`, `torn`, `raw`}, and
  the export directories' identities) and `freeze.json` (`wlscratch-freeze-v3`: increment number, cut c_n, slot range,
  the previous increment's freeze-marker digest, the digest of every export marker committed for this increment, the
  manifest's sha256, `raw_files`, channel heads, boot id, time) are written with the export primitive and committed.
  `raw_files` lists every RAW file of J's `commits/` and every uncommitted record file that appeared after the cut and
  that neither an earlier increment nor this manifest listed, so every raw file is listed exactly once. The export
  markers of increment n, its freeze marker and the close markers that confirm them have seq > c_n.seq, so the next
  increment exports them. The last increment's export markers are listed by digest in its own freeze record; only its
  freeze marker and the close marker that confirms it are never exported: the freeze marker's digest goes to F in
  `EXPORTED` and `FINAL` and is printed, and the originals stay in the protected journal.
```

### 0.5 Author corrections of v4 (v4 itself is not edited)

1. v4 §9.4 (a), §2.4 R9 and §4.5 (i) argued that a retained directory reference allows nothing to a process without
   uid R or GATE because partition directories are 0700; the target owns them and may change their modes and ACLs.
   Withdrawn (§9.8).
2. v4 §9.4 (b) inferred from M's serialized API dispatch and two equal snapshots that M had finished every message it
   had read. Withdrawn as an inference; replaced by the property M-QUIESCENT, the premises S1-S6 and the absorption
   lemma (§9.4).
3. v4 §2.1 A3 promised that every user unit is masked, while S-F inventoried only the enabled closure; and v4 §9.4 (b)
   said that P16 observed no timer at all, although P16 lists enabled units only and
   `/usr/lib/systemd/user/systemd-tmpfiles-clean.timer` exists (observed 2026-10-05, Appendix E). Withdrawn; one mask
   rule (§11.5 S-F), which masks that timer too.
4. v4 §5.3 argued that a set-user-ID-R file "would confer only R, which reaches nothing in g". Through a retained
   descriptor uid R has owner rights on partition contents. Withdrawn (AM-16); minting is now prevented for T's and M's
   process trees (§9.8 K3).
5. v4 §9.3 C9 returned `ENOSYS` for `io_uring_setup` but not for `io_uring_enter` or `io_uring_register`, so a ring
   that another process created and passed to T could perform an open with a set-ID mode outside the filter.
   Corrected (§9.3 C9).
6. v4 §9.3 and B.4.4 required a refusal for a `STOP` received after `SPAWN_OK` even after C's spawn call, and had no
   legal route for a failed spawn call; v4's W↔L `GO` row had the same `STOP` problem for L's spawn of SR. Corrected
   (§9.3, B.4.4).
7. v4 B.4.4 required `RELEASE_INTENT_RESULT` before `RELEASE_DONE`, contrary to v4 §9.4's deadline rule; it had no
   route for refusals before the hello, after `HELLO_ACK`, in the input phases, after a failed front-parent half or
   after a failed dispatch vault stage; and `EXPORT` could not report a failed export. Corrected (B.4).
8. v4 §10.2 let a torn marker end the chain while a later writer linked past it. Withdrawn (§10.2).
9. v4 §11.7 listed `setup-identities.json` among the files whose own sha256 and size it pins. Withdrawn (AM-24, AM-27).
10. v4 §11.4 claimed that under `sh -e` a failing pipeline command stops the script; on this host `sh` is bash, whose
    errexit ignores every pipeline command but the last (Appendix E). Withdrawn. Two v4 templates relied on unchecked
    producers: S-F step 4's `[ -z "$(systemctl show …)" ]` would have accepted a failing `systemctl` as an empty
    `PAMName`, and S-A's `case "$(getent shadow … | cut …)"` would have read a failing `getent` as an unlocked account
    (it would then have run `usermod -L` and stopped with a misleading message). Corrected (§11.5).
11. v4 `step.py` ignored the length `os.write` returned. Corrected (§11.5).
12. v4 S-R resumed from the first step without `done`, which would re-run a completed create-only step. Withdrawn
    (§11.4).
13. v4 §3.4 and §11.7 required every T_root and R_root entry to be a W-owned directory while each image root holds a
    root-owned `lost+found`, and asked W and W2 to `lstat` a backing file below a root-only 0700 directory. Corrected
    (AM-06, AM-07, AM-25, AM-26, AM-29).

### 0.6 Reading notes for carried text

- "v4" in carried or amended text names the design state it was written for; unless §0.2, an amendment or a replaced
  unit says otherwise, the statement holds for v5 unchanged.
- §16 (carried; W1-SETUP-ORDER is closed): step 1's "this v4 design" reads as the current design revision; step 2's
  code includes v5's mechanisms (§9.8, §10.2, the extended C9, the Appendix B.4 machines and `check_out.py`), which
  §19 lists.
- §13 (carried; closed): P-COMMIT's "a torn marker (the next writer's seq skips it and its `prev_commit` links to the
  head)" holds under §10.2, whose next marker is a continuation with exactly that seq and `prev_commit`; §13.1's P-CHAIN
  covers the whole rule.
- §4.2 M8 and M9, and §15.3's "the materialization marker as its cut": by §10.2's commit primitive, a record's marker
  used as an end or a cut means the close marker that confirms it.
- §9.6 (carried): its torn-marker and torn-slot statements hold under §10.2's reader rule.
- §12.2 (carried): RL's identity "to W over fd 0 before `exec`" is the `RL_IDENTITY` frame of §7.3 and Appendix B.4.3.
- §14 (carried): v5 changes no allowance and no stage budget; its added records (write-revocation records, RL identity
  records, and the close and continuation markers of §10.2) are small control records of the kinds §14's introduction
  and §14.2 already count under A_in.

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
  65536; last id JACKAL exact, parsed `100000+65536-1`), FUSE mounts,
  reads of every dumpable `sicarii` process's `/proc` entries, signals to `sicarii` processes and to processes whose
  real uid is `sicarii`, writes to every `sicarii`-writable file (including the shared window file, the lead inbox and
  every frozen input under `/home/sicarii`), and invocations of the reviewed `sicarii`→`wlscratch` sudo rule with
  arbitrary arguments. They must not be able to create, rename, substitute, modify or delete any frame-owned location
  or the admitted generation, or cause the frame to mutate outside its tree. They may also hold anything a target
  hands them (open descriptors, connection handles) and may make themselves non-dumpable, so their descriptor tables
  are not assumed observable. They may also hold write permission that a target granted them on what it owns, until
  O's write revocation removes it, before any custody conclusion relies on the partition contents (§9.8).
- **A2, the running target** (`wlscratch-run` with group `wlscratch-gate`, and everything it starts). It may do
  anything those credentials allow, including commanding its account's user manager through the manager's private
  socket (transient units and services, descriptor-carrying unit properties, reloads), moving itself between cgroups
  of that manager's delegated subtree, passing open descriptors and connection handles to processes of any uid
  (including A1 processes, over abstract sockets), leaving descriptors queued in sockets, changing the modes and ACLs
  of everything it owns (including granting write permission to any uid or gid; set-ID modes excepted, §9.3 C9), and
  writing everywhere its credentials permit outside the generation. It must not be able to mutate frame records, the admitted recipe, the
  frame's location chain or another attempt's evidence, and its leftovers must not change an admitted generation
  between a later final pass and spawn.
- **A3, the target account's user manager M** (`systemd --user` of uid `wlscratch-run`, without `wlscratch-gate`).
  After setup M is the account's only process outside the frame's own participants: every unit file of a
  process-starting type in the user unit load path at inventory time is masked, the user bus included (one rule,
  §11.5 S-F); M runs without a PAM session, so no `(sd-pam)` helper exists; and M and every process it starts run with
  `no_new_privs` and a seccomp filter that denies set-ID modes and the io_uring calls (§11.5 S-F, §9.8 K3). Units that
  are generated when M starts, installed after the inventory or created at run time (transient units) are not masked;
  M-QUIESCENT governs them (§9.4). M executes root-installed code, but every uid-R process (T included) can command it
  and pass it descriptors, so M's *state* is treated as attacker-influenced. No benign-service premise is used:
  final-pass custody and known-terminal ownership require M-QUIESCENT (no foreign unit, job, trigger, connection,
  queued input or pending signal) and no reference of M into g; final-pass custody also requires the write closure of
  §9.8 and that no writable description of an admitted file exist anywhere (§9.4). A state that cannot be observed
  completely is UNKNOWN.

### 2.2 Trusted base (outside the threat model)

Root and everything running as root (sudo, systemd and logind, PAM, sshd, the kernel, the root launcher of Option B);
root-owned installed files (`/usr`, `/etc`, the installed frame under `/opt/wlscratch`); the Python 3.14.7 runtime
under `/usr/lib/python3.14` (interpreter `/usr/bin/python3.14`, sha256 observed by v2 as
`c6bc1ef497b896b7575c546b13f9bafe52e2066f184fdd3fec6af4b5b6349947`); the operator's credential. The design gives no
protection against root, against kernel defects or against a compromised operator credential.

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
  `kernel.yama.ptrace_scope=1`, `/proc` mounted without `hidepid`, cgroup2 with `nsdelegate`. Observed too:
  `fs.suid_dumpable=2`. Observed by the drafting author on 2026-10-05: `fs.leases-enable=1` (required by the lease
  test of §9.4) and `fs.lease-break-time=45`.
- **One local filesystem.** Observed: `/`, `/var/lib`, `/opt`, `/tmp`, `/var/tmp` and `/home` are all on `/dev/vda`
  ext4; `/dev/shm` and `/run/user/*` are tmpfs. No EXDEV boundary is relied on anywhere. Observed on 2026-10-05:
  `/tmp` and `/var/lib` resolve to the same mount (mount ID 32 in `/proc/self/mountinfo`), which the rename and link
  probes of §13 need; with images, T lies on separate mounts (§14.5) and those probes use same-mount operands.

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
  never a frame write and never an unsafe alias at final admission. W-1 narrows where the target can write but the
  inventory of target-writable places is incomplete and stated as UNKNOWN beyond the listed places (§12.3).
- **R4, the toolchain.** The target executable is identity-checked and then executed by path (ruled
  ACCEPTABLE_AS_DOCUMENTED). The toolchain under `/home/sicarii/opt/gnat` stays `sicarii`-owned and `sicarii`-writable;
  its closure is observed before and after. W-1 claims no custody of it.
- **R5, exposure.** Option A's read exposure is known only for named places and UNKNOWN elsewhere (§12.1). Option B
  adds privileged code (§12.2).
- **R6, availability.** A `sicarii` process can stop an attempt: it can kill the front, signal processes whose real
  uid is `sicarii` (which may include the sudo front-ends, so a signal may be relayed to a frame helper), or modify
  the cooperating window file (N07). The result is an interrupted, non-success attempt or a held window, never a
  custody change. Whether sudo relays such signals is a probe item (§13, P-SIG). A held connection handle or a held
  writable descriptor (§9.4) likewise yields only a held window or a refused launch.
- **R7, `(sd-pam)` (v3's limit, withdrawn).** v3 accepted an unreadable `(sd-pam)` descriptor table under identity
  conditions. v4 accepts nothing unreadable. The reviewed `user@<R>.service` drop-in (§11.5 S-F) runs M without a PAM
  session, so no `(sd-pam)` process exists; P-MGR verifies it. Observed by the drafting author on 2026-10-05 for
  `sicarii`'s own manager: its `(sd-pam)` (pid 1023, parent 1019) has `/proc/1023/fd` owned by root, mode 0500, and
  unreadable to its own uid, while `/proc/1019/fd` of the manager itself is owned by `sicarii`; this is why v3's
  exception cannot stand. If the drop-in cannot be made to work, every terminal classification of the target account
  is UNKNOWN and W-1 must be redesigned; no exception is taken.
- **R8, root and the kernel** (§2.2).
- **R9, descriptors in transit and retained references (v4's argument withdrawn; closed by mechanism).** A scan of
  descriptor tables cannot see a descriptor queued in a socket or held by a non-dumpable process, and v5's custody
  conclusion does not need one: a writable open description of an admitted file is detected wherever it is, queued or
  not, by the lease test (premise L1, §9.8 K7); once the partition contents are write-closed (§9.8 K2), any other
  retained reference (a read-only, `O_PATH` or directory descriptor, a current directory, queued or held) lets its
  holder do only what the holder's own credentials allow at the moment of each operation, and the credentials that
  could change the generation are confined to enumerated processes (§9.8 K3-K5); M's queues must be empty and M must
  hold no foreign connection (§9.4). v4's statement that a directory descriptor permits a mutation only to a uid-R or
  GATE process rested on partition directories staying 0700, which the target can change; it is withdrawn. What
  remains is stated in §9.4 and §9.8 as conditions with UNKNOWN outcomes and as premises with probes, not as a
  residual.

## 3. Principals, accounts and layout

### 3.1 Accounts and groups (three new identities)

| Identity | Kind | Purpose | Members |
|---|---|---|---|
| `wlscratch`, uid = gid = W | user + user-private group | The only writer of generation trees | none besides the user |
| `wlscratch-run`, uid = gid = R | user + user-private group | Runs the launcher, observer, in-scope child and target; owns a lingering user manager | none besides the user |
| `wlscratch-gate`, gid = GATE | group only | Granted to processes started through the reviewed launcher rule; the only non-writer, non-lead key to the generation | none in `/etc/group` |

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
| S2, S_O | `sudo -n -u wlscratch-run -g wlscratch-gate -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/launch_target.py <verb> …` (Option A) | W or W2 | `/usr/bin/sudo` |
| L, launcher | `launch_target.py launch …`, uid R, egid GATE | S2 | installed |
| SR/C, scope launcher then in-scope child | `systemd-run --user --scope …` which, being a scope, `exec`s `launch_target.py child …` in the same process inside the scope | L | systemd, installed |
| U, scope | transient `claude-worldline-scratch-<g12>-<A>.scope` in M | SR | systemd |
| T, target | the exact allowlisted command, uid R, egid GATE | C | toolchain |
| O, observer | `launch_target.py observe …`, uid R, egid GATE | S_O, started by W (parent and after stages) or by W2 (recovery) | installed |
| M, user manager | `systemd --user` of R (lingering; the unit files of §11.5 S-F masked; no PAM session; `no_new_privs` and the S-F seccomp filter) | `user@<R>.service` | systemd |
| S3 | `sudo -n -u wlscratch -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py seal-front …` (the S1 rule) | F | `/usr/bin/sudo` |
| W2, post-writer | `writer.py seal-front <N_F> <g> <A> <mode>`, uid/gid W; mode `seal` after W ended with `FINAL`, mode `recover` after W died or its channel failed (§9.7) | S3 | installed |
| RL (Option B only) | root launcher `sandbox_launch.py`, replacing S2's direct `-g` start | W or W2, via Option B's rule, which replaces the launcher rule | installed, privileged |

`<g12>` is the first 12 hex digits of the generation id; `<A>` is the v5 attempt stamp (`STAMP_RE`). The installed
frame carries two compiled path constants besides `install_root`: `SOURCE_FRAME`, the frozen v6-W1 source directory in
the lead's tree, and below it the sealed review directories `REVIEW` (`<SOURCE_FRAME>/review/gpt61-v1`, code review)
and `INSTALLED_REVIEW` (`<SOURCE_FRAME>/review/installed-gpt61-v1`, installed-evidence review) (§4.6, §16).

### 3.3 Layout

The layout is the same with and without optional images (§3.4, §14.5).

```
/var/lib/wlscratch                     root:W        writer home (setup)
  lease/                               root:W        setup; writer-only traverse
    writer.lock                        root:W 0440   setup; flock-only
  runs/                                W:W           T_root: root of the protected run tree T (setup); work-image mount point
    <g>/                               W:W           generation root g (writer-created at M4), g = 32 lowercase hex
      generation.json                  initial generation record                               [P_adm]
      commits/                         generation journal (P_adm markers)                      [P_adm]
      inputs/                          streamed input records + manifest.json                  [P_adm]
      overlay-snapshot/                v5 overlay snapshot (0700 dirs, 0600 files)             [P_adm]
      source/                          admitted recipe (exact recipe modes)                    [P_adm]
        obj/ lib/ resource-tests/obj/ resource-tests/bin/   output partition roots            [P_adm roots; contents target-owned]
      materialization.json             v5 schema plus §4.3 fields                              [P_adm]
    records/                           W:W           R_root: record root of T (setup); records-image mount point
      <g>/                             W:W           g_rec, record root of g (writer-created at M4)
        attempts/<A>/                  P_att(g, A): attempt.json, commits/ (attempt journal), fallback.journal,
                                       fallback-allocation.json, inputs/, front/, channel/, w2-<k>/,
                                       stream files, observer files, every v5 attempt record
        export/                        P_exp(g): generation/, <A>/inc-<n>/
      adoption-<I>/                    W:W           P_ado(I), installed-frame adoption root (writer-created by `adopt`)
        lead-adoption.json, commits/ (adoption journal), invocations/<stamp>/, export/inc-<n>/
    selftest-<h>/                      W:W           sacrificial selftest generation root (§13)
    records/selftest-<h>/              W:W           its record root
/var/lib/wlscratch-run                 root:root     target account home (setup; not writable by R)
  tmp/                                 R:R 0700      the target's TMPDIR (setup)
  .config/systemd/user/                root:root     masks for M (setup)
/etc/systemd/system/user@<R>.service.d/
  50-wlscratch.conf                    root:root 0644 drop-in: M without a PAM session (setup, S-F)
/opt/wlscratch/frame-v6w1/             root:root     installed frame (member-exact)
/opt/wlscratch/setup-identities.json   root:root 0644 setup identity record (§11.5 S-H, §11.7)
```

`I` is the sha256 (64 lowercase hex) of the installed `frame-inventory.json`; `h` is 32 lowercase hex. Exact modes and
ACLs are in §6.3.

### 3.4 The protected intended run tree, its anchors and routing [correction: W1-IMAGE-TREE]

**Definition.** The protected intended run tree T is the directory tree rooted at T_root = `/var/lib/wlscratch/runs`,
including its record root R_root = `/var/lib/wlscratch/runs/records` and every mount at or below T_root that
`setup-identities.json` lists. Every component from `/` to T_root is root-owned and writable only by root (`/`, `/var`,
`/var/lib` root:root 0755; `/var/lib/wlscratch` root:W 0750 with search-only ACL entries). Inside T only W can create,
rename or remove entries, except that GATE holders can do so inside the four partition roots of each generation (§6.3).
T is the categorical writer tree of §5.2: no writer verb writes anywhere else, in any configuration.

**Anchors.** Every writer and helper reaches T only by anchored descriptor chains (v5 `Dir.anchor`, `O_DIRECTORY|
O_NOFOLLOW` per component, from `/`):
- `A_T` = T_root; `A_R` = `A_T` + `records`, opened from the held `A_T` descriptor;
- per generation: g = `A_T` + `<g>`, g_rec = `A_R` + `<g>`;
- per adoption: P_ado(I) = `A_R` + `adoption-<I>`;
- per selftest: `A_T` + `selftest-<h>` and `A_R` + `selftest-<h>`.
Each anchor's pinned identity (§11.7) is compared with `setup-identities.json` before any use: both anchors at every
writer invocation, and `A_T` at every O and C stage (O and C cannot search `A_R` and never need it). g, g_rec and
P_ado(I) are compared with the identities committed when they were created (`generation.json`, the adoption journal).

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
| `generation.json`, `inputs/**` (materialize), `overlay-snapshot/**`, recipe, partition roots, `materialization.json` | g (P_adm) | generation journal `g/commits/` |
| `attempt.json`, `fallback-allocation.json`, every attempt record, stream files, observer files, front records, channel segments, recovery records, W2 records, release records | g_rec `/attempts/<A>/` (P_att) | attempt journal `g_rec/attempts/<A>/commits/` |
| `fallback.journal` slots | g_rec `/attempts/<A>/fallback.journal` | none: described by `fallback-allocation.json`; slots are self-validating (§10.4) |
| generation export | g_rec `/export/generation/` (P_exp) | attempt journal of the materializing attempt A0 |
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
  number equal the pinned ones. W and W2 also check the backing file itself, which needs search permission on its
  directory: they open `/var/lib/wlscratch-images` with `O_PATH|O_DIRECTORY|O_NOFOLLOW` through an anchored chain (it
  is root:W 0710, so W can search it but not list it, §14.5 J1), require that directory's pinned identity, and require
  by `fstatat(images, <name>, AT_SYMLINK_NOFOLLOW)` a regular file with the pinned `[dev, ino]` and size, uid 0, gid 0,
  mode 0600 and one link. O and C (uid R) cannot search that directory; they make every other check of this item and
  rely, for the file itself, on W's check in the same invocation before W started them, since only root can change what
  is mounted.
- `A_R` must be the root of the records image, checked the same way, and its mountinfo parent ID must equal the work
  image's mount ID (the records image is mounted inside T, on the work image).
- If an image is not mounted, the path resolves to its bare mount point: root-owned, mode 0700, empty, on the parent
  filesystem. Its `st_dev` equals the parent's, so the check refuses before any mutation, and W could not create
  anything in it anyway. The loop device number and mount ID may change across boots; they are observed, never pinned
  (§11.7).

**No new outside-tree authority.** Every writer mutation lies in T. The adoption record, which v5 wrote into the
frame's own review directory outside its run tree as a prescribed preparation record, now lies inside T (§4.6). F
writes nothing. The only frame writes outside T remain v5's window protocol by F, unchanged (N07).

## 4. Generation order and record partitions [correction: W1-GENERATION-PROTOCOL; gap: generation-order]

### 4.1 Partitions

- **P_adm(g), the admitted generation partition**, in g: `generation.json`, `commits/` (the generation journal),
  `inputs/**`, `overlay-snapshot/**`, every recipe object under `source/` (files, directories, their modes and
  contents), the four output partition root directories (their identity, mode and ACL) and `materialization.json`.
  P_adm is written only by the `materialize` invocation that creates g. After that invocation's final verification
  and the materialization marker (§4.2, M8), no writer verb has any path that mutates P_adm: no verb rewrites,
  renames, deletes, chmods or re-ACLs an existing P_adm object. Only W can write there at all (§6.3), and W writes
  P_adm only in `materialize`.
- **Partition contents.** Entries below the four partition roots are created and written only by targets of launched
  attempts (through the gate group, §6.3); the frame never writes their content or names. The frame's only action on
  them is O's write revocation at each dispatch's parent stage (§9.8 K1), which clears the group-class and other-class
  write bits of entries owned by R and changes nothing else; it is a frame mutation inside T, recorded in P_att. They
  are part of what each later attempt admits, so every attempt re-observes them in full (§4.5).
- **P_att(g, A), the attempt bookkeeping partition**, in g_rec `/attempts/<A>/`. Every writer invocation that creates
  an attempt has one: the creating `materialize` invocation (A0, kind `materialize`) and every `dispatch` invocation
  (kind `dispatch`). It is created and written by that W; afterwards only W2 instances of the same attempt append to
  it, each only in new names below its own `w2-<k>/` and in the attempt journal (§5.2, §9.7).
  Create-only. The target never reads it and cannot search to it (§6.3): launch records reach C over its channel
  (§7.1), and target streams are passed as open descriptors (§6.4).
- **P_exp(g), the export partition**, in g_rec `/export/`. Writer-produced read-only copies of committed records, for
  the lead. Create-only. Never read by the target, never an admission input.
- **P_ado(I), the adoption partition**, in R_root `/adoption-<I>/`: the installed-frame adoption record, the adoption
  journal, per-invocation bookkeeping and the adoption exports (§4.6). Written only by W in `adopt`; create-only; read
  by W at every dispatch.

The partitions are disjoint. Every frame mutation after a generation's creation lands in a P_att, a P_exp or a P_ado,
never in P_adm; the one frame action on partition contents is the write revocation above.

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
  `HELLO`: `W_HELLO`, `HELLO_ACK`.
- AD4. State `INPUTS` (phase `adoption`): F streams the lead module (pinned), the two review rosters with their freeze
  records (joined), the two provenance triples (event stream, exec-argv record, rollout) (joined), the `scratch-adopt`
  lead observation (observation) and F's adoption body (joined).
- AD5. State `COMMIT`: W verifies (§4.6) and, only if every join holds, commits `lead-adoption.json` and its marker in
  the adoption journal; `ADOPTED`. Otherwise `REFUSAL`, and no adoption record exists.
- AD6. State `EXPORT`: the adoption export increment (§15.3), `EXPORTED`. State `FINAL`: `FINAL`, `BYE`; W closes and
  exits.
- AD7. F waits for S1 and exits by §10.7. No W2 runs for `adopt`; F's terminal facts are its console output, as v5
  `adopt` had no terminal record.

The adopt invocation runs only after a procedural Gate 0 receipt computed with the materialize/dispatch-stage
expression (§14.3), and its retained bytes are counted under A_in (§14.2). It reserves nothing and launches nothing.

**Generation creation (`front.py materialize <label> <overlay-dir>`; v5 `materialize`).**

- M1. F starts (§7.7 first act), records its identity (§8.1), validates its argv grammar (`label` matches v5
  `NAME_RE`; `overlay-dir` absolute).
- M2. F reads, through the v5 anchored readers, the base descriptors (`source-binding.json`,
  `source-inventory.json`, `source-directory-modes.json`), observes `BASE/source` against the pinned inventory
  (`observe_tree`, as v5 `base_tree`), and observes and reads the overlay directory (`observe_tree` + `read_files`,
  as v5 `materialize`). F writes nothing.
- M3. F creates its two channel pipes after its first act and starts S1 → W (`writer.py materialize <N_F> <label>`,
  `N_F` = 32 random bytes as 64 hex, §7.3).
- M4. W starts (§7.7), records its identity, takes the lease (§5.1), anchors A_T and A_R with the missing-mount checks
  (§3.4), and then, in this order: creates g (v5 `Dir.child(create=True)`: mode 0700, owner W, link count 2, same
  device, empty, not an ancestor), sets g's access ACL by `fsetxattr` on the held descriptor and reads it back (§6.3),
  creates `g/commits/` (0700, authenticated); creates g_rec the same way with its own ACL, then `g_rec/attempts/` and
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
  payload is retained twice (§7.3). W commits the input records of each phase and sends `PHASE_DONE`; after the last
  phase it commits `inputs/manifest.json`. Overlay and base bytes become snapshot and recipe content, not records: M8
  verifies them as a whole and `materialization.json` binds their digests.
- M7. State `MATERIALIZE`: W materializes exactly as v5 `materialize` (S:959-1049), with streamed verified bytes in
  place of anchored reads of `BASE` and the overlay directory: `overlay_rules`; `expected_source`; snapshot files
  written by `write_bytes` with the default 0600 into snapshot directories created 0700; every recipe directory
  created 0700 and authenticated; every expected file written with its row mode (base mode, or 0644 for a new overlay
  unit); then the four partition roots created (0700, authenticated) with their ACLs set and read back (§6.3); then
  the recipe directory modes applied deepest first, the recipe root last (`set_mode`); then `source.sync()`.
- M8. W verifies with a full walk of `source/` (all partition roots are empty and writer-owned at this point, so W
  can walk them) and of the snapshot: recipe content and modes equal the recipe; the partition roots are exactly the
  four, empty, with their exact mode and ACL. W then writes **`materialization.json`** (§4.3) and its marker, runs
  `verify_materialization` against the committed record, and re-verifies the location of every held handle. **This is
  the last mutation of P_adm(g), ever.** The generation journal ends with this marker and never grows again.
- M9. Still in `MATERIALIZE`: W writes the generation export (`g_rec/export/generation/`, §15.3), which is the whole
  generation journal and every record it commits (`generation.json`, the input records and manifest,
  `materialization.json`): a finite prefix ending at the materialization marker. The recipe is readable by the lead in
  place and the snapshot is bound by digest, so neither is copied. Its export markers go to A0's attempt journal; W
  sends `MATERIALIZED`.
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
  and equality of the P_adm identities with them; requires the committed adoption record `P_ado(I)/lead-adoption.json`
  of the installed inventory I with its marker in the adoption journal (otherwise it refuses: the installed frame is
  not adopted); requires `setup-identities.json` to match the seal that adoption record carries, and the setup identity
  recorded in `generation.json` to equal it (§11.7; otherwise it refuses before any mutation); creates
  `g_rec/attempts/<A>/` with its `commits/` (0700, authenticated); commits **`attempt.json`**
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
- D8. State `PARENT`: the writer half (writer-owned recipe walk, snapshot, record pins, location, the attempt-journal
  join of §10.6); then the observer for the parent stage: W creates and syncs the observer stream files, commits
  `observer-intent-1.json` binding them (§9.3, G0) and starts S_O → O (under Option B, RL → O, and W commits
  `observer-1-rl-identity.json` before its request). O, in this order: takes the first parent-stage scans of §9.4
  (SCAN-GATE = {O}, SCAN-R, SCAN-W, SCAN-UNITS and SCAN-QUIESCE with its barrier; phase `pre`); performs the write
  revocation of §9.8 K1; takes the full walk of `g/source` (with every excluded leaf's `stat_key`), with SCAN-WCLOSED
  and SCAN-LEASE inside it; takes the target-context identities `parent` and the helper half of `preflight` (heavy
  processes, meminfo, M's units); and repeats SCAN-GATE, SCAN-R, SCAN-W, SCAN-UNITS, SCAN-REFS and SCAN-QUIESCE (phase
  `post`). W commits `write-revocation-1.json`, `observer-1-parent.json` and `observer-wait-1.json`. Any failed join,
  revocation or scan refuses the attempt (nothing reserved).
- D9. State `VAULT`: `project-vault pin <g_rec>/export` and `project-vault status` by F (§8.5).
- D10. State `GATE0`: frame-enforced Gate 0 receipt for the dispatch stage (§14.3).
- D11. State `LAUNCH_RECORD`: W commits **`launch.json`** (§4.3).
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
- D16. State `RUNNING`: launch, child stage, final pass, spawn and run (§9.3).
- D17. State `AFTER`: F's after-stage half; the observer's after stage (`observer-intent-2.json`, the walk, the
  identities `after`, the report bytes and the classification scans of §9.4); W's stream finality test (§10.6);
  `result.json`. State `CONCLUDE`: `CONCLUSION`.
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
  `generation.json` and its marker), `inputs_manifest` (pin), `partition_roots` (path, `[dev, ino]`, mode, exact ACL
  text), `recipe_mode_property` (§6.1), `channel_heads`. Its schema name becomes `wlscratch-materialization-v1`; the
  v5 `run` field becomes the generation root path.
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
  its nonce), the stage, the `[dev, ino]` of `observer-<n>.stdout` and `observer-<n>.stderr`. **`observer-<n>-<stage>.json`**
  and **`observer-wait-<n>.json`**: O's results and S_O's wait.
- **`write-revocation-<n>.json`**: the record of O's write revocation at the parent stage (§9.8 K1), sent with O's
  observation and committed with it: every entry examined, every mode changed (before and after, with `[dev, ino]`
  and link counts) and, if the revocation stopped, why. **`launcher-rl-identity.json`** and
  **`observer-<n>-rl-identity.json`** (Option B only; the latter also under `w2-<k>/`): RL's `RL_IDENTITY` frame
  (§7.3), committed before W sends `GO`, or its first `OBSERVE_REQUEST`, to the helper RL started.
- **`launch.json`** (v5 schema plus): `generation`/`attempt` pins; the parent-stage full-walk observation pin from O
  (files, directories, identities and every excluded generated leaf's `stat_key`, §4.5); the relocated target
  environment (§8.4); the exact L, systemd-run and C argv templates; the stream-file names; the unit name; the front
  stage-record pins. v5 fields kept unchanged in meaning: `action`, `args`, `child_argv`, `cwd`,
  `directory_identities` (run = g, attempt, source, snapshot, `source_tree`), `unit`, `scope_argv_template`,
  `scope_argv_tail`, `environment`, `frame_inventory`, `review`, `adoption` (the descriptor of the protected adoption
  record, §4.6), `materialization`, `storage_reserve_bound`, `holder`.
- **`reservation-intent.json`, `reservation.json`** (v5 fields: `at`, `token`, `launch`, `prior`, `holder_task`,
  `candidate`; `current`) plus the window-lock identity F observed under the lock and the F request message digest.
- **`admission.json`** (v5: `memory_gate`, `reservation`, `launch`) plus the Gate 0 receipt pin (D10), the front
  stage-record pins, the O parent-stage record pin and the writer-half pins. It is the complete create-only
  admission/launch record: written after every input, the reservation and the memory gate.
- **`launcher-intent.json`** (v5: `scope_argv`) plus the L argv (with `launch.json` and `admission.json` sha256 and
  the W↔L nonce `n_wl`), the C nonce `n_c` (inside the scope argv), the stream files as a list of `{name, dev, ino}`
  read from the descriptors W already holds (D14), and the attempt-journal head. It is the launch intent: committed
  after the stream files exist and before any launcher process can exist (§9.3).
- **Launch, child and conclusion records** (`launcher-start.json`, `launcher-wait.json`, `sudo-launcher-wait.json`, the
  `child-*` records, `effective-limits.json`, `spawn-ok.json`, `stream-finality.json`, `result.json`, the release
  records, `final-status.json`, `conclude-errors.json`, `refusal.json`): Appendix B.3.
- **W2 and recovery records** (`w2-<k>/identity.json`, `w2-<k>/recovery/scan-<r>.json`,
  `w2-<k>/recovery/result.json`, the release records and observer files of a recovery under `w2-<k>/`,
  `w2-<k>/front-terminal.json`): §9.7.
- **Export increments** (`export/<A>/inc-<n>/manifest.json`, `freeze.json` and the copies): §15.3.
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

### 4.5 Where the final pass is, exactly

The **final admission boundary** is C's last full walk, inside the scope, immediately before the spawn:

1. C performs v5 `verify_materialization` over `g/source` with the v6 final pass: every encountered leaf, recorded or
   excluded generated, is re-stat'ed by name without following and must keep its complete `stat_key`, and every
   directory is re-reached with unchanged metadata (`scratch.py` v6 :554, :569-573). C walks as `wlscratch-run`
   with `wlscratch-gate`, so it can read recipe files (others-readable recipe modes) and every target-owned partition
   entry (owner). Inside the same walk every regular file of the partition contents receives the lease test of §9.4
   (SCAN-LEASE), on a descriptor whose `fstat` equals the walk's `stat_key`.
2. The observation (files, directory modes, identities and every excluded generated leaf's `stat_key`) must equal the
   O parent-stage observation sealed in `launch.json` exactly. A difference in any recorded or excluded leaf, and any
   lease refusal, refuses the launch. (v5 compared directory identities only; the excluded-leaf comparison is added
   and is an engine change to `observe_tree`, which must return the excluded leaves' keys it already computes.)
3. Then C repeats SCAN-GATE, SCAN-R and SCAN-W with the child-stage allowed sets (§9.4), re-verifies the location of
   its held handles, reaches the interruption point (pending-signal check) and spawns with `fchdir` on the held
   `source` descriptor (v5 `spawn`).

This pass follows (a) the last mutation of P_adm(g) (M8, at generation creation), (b) the commit and delivery of
every record C's admission depends on (`launch.json`, `admission.json`, `launcher-intent.json`, the adoption record)
and (c) the `SPAWN_OK` of §9.3. Every frame write after it goes to P_att(g, A) or P_exp(g): `child-start.json`,
waits, the conclusion. Those partitions are disjoint from P_adm, lie under a record root the target cannot search
(§6.3), and the target never reads them. **So "the final pass runs after the last frame mutation of the admitted
generation" is exact, and the remaining frame writes are bookkeeping by construction, not exceptions.**

**Write closure in the same walk (v5).** Inside the same walk C also checks W-CLOSED (§9.8 K2) for every entry of the
partition contents, on the descriptors the walk already holds: owner R, a regular file or a directory, no group-class
or other-class write bit, no set-user-ID or set-group-ID bit, one link for a regular file, its partition root's
`st_dev` for a directory. Any violation, or an entry that cannot be examined, refuses the launch. O's parent-stage
walk checks the same after its write revocation (§9.8 K1), so a difference between the two walks in any of these
fields refuses as well, by item 2.

Custody from the final pass to `exec` (V5-B01, second sentence) rests on these facts, each with its own section:
(i) at the final pass every partition entry is W-CLOSED, and no writable open description of an admitted partition
file exists anywhere, in any process, queue or mapping (§9.8 K2; §9.4 SCAN-LEASE, premise L1);
(ii) W does not mutate P_adm after M8, and any other writer instance refuses before its first mutation and before
starting any helper while W holds the lease (§5.1, §5.2);
(iii) the processes that can hold uid R or GATE are only those started through the reviewed sudo rules with their
descendants, and M with its descendants; no set-user-ID or set-group-ID file of R or GATE can be minted, by T's tree
(`no_new_privs` and the anti-setid filter, §9.3 C9) or by M's (the S-F drop-in, §11.5) (§9.8 K3);
(iv) at the final pass, by C's own scans: GATE holders are exactly L and C; uid-R processes are within {L, C, M}; M
holds no reference into g and is M-QUIESCENT apart from C's own connection (§9.4; §9.3 C7 and C10);
(v) that state is absorbing until T's `exec`: by (i) and (iii) every process other than L, C, M and root is denied
every mutation of the admitted generation at the moment it attempts it, whatever descriptors or references it holds,
queued or not (§9.8 K4-K5); M stays quiescent by the absorption lemma of §9.4; and L and C are frame code;
(vi) root and the kernel are outside the threat model.
This is an argument for review, not evidence; its kernel and systemd premises are listed with their probes in §9.8
K7.

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

### 5.2 What the writer may mutate (the complete list) [correction: W1-IMAGE-TREE]

Every row lies inside T (§3.4), reached through §3.4's anchors, in both storage configurations.

| Verb | Mutation (create-only new names) | Where | When | Parent writable by |
|---|---|---|---|---|
| `adopt` | P_ado(I) with `commits/` and `invocations/` (first `adopt` of I only); `invocations/<stamp>/**` (identity, channel segments); `lead-adoption.json`; the adoption journal's markers; `export/inc-<n>/**` and their ACLs | R_root (P_ado) | AD3-AD6 | W only |
| `materialize` | g, its ACL, `g/commits/`, `generation.json` and its marker | T_root and g | M4 | T_root: W only; g: W only |
| `materialize` | inputs, snapshot, recipe files/directories/modes, partition roots and their ACLs, `materialization.json`, their markers | g (P_adm) | M6-M8 only | W only (recipe directories are 0755 owned by W) |
| `materialize` | g_rec, its ACL, `attempts/`, `attempts/<A0>/**` (records, markers, fallback journal and its slots, allocation descriptor, front records, channel segments); `export/generation/**` and `export/<A0>/inc-<n>/**` with their ACLs | R_root and g_rec (P_att, P_exp) | M4-M11 | W only |
| `dispatch` | `attempts/<A>/**` (records, markers, fallback journal and its slots, allocation descriptor, inputs, stream and observer files, front records, channel segments); `export/<A>/inc-<n>/**` and their ACLs | g_rec (P_att, P_exp) | D3-D19 | W only |
| `seal-front` (W2, either mode) | `attempts/<A>/w2-<k>/` (k the smallest unused) and new names only below it: identity, channel segments, observer files and records, recovery records, release records, the front terminal record; markers appended to A's attempt journal; `export/<A>/inc-<n>/**` and their ACLs | g_rec (P_att, P_exp) | §9.7 | W only |
| `selftest` | sacrificial `selftest-<h>/**` under T_root and under R_root | T | selftest | W only |

Nothing else. In particular W writes nothing in `lease/` (§5.1), nothing in partition contents, nothing outside T (so
nothing in `/home/sicarii`, the installed frame, the shared window file or `/tmp`), and creates no temporary file
anywhere. No verb renames, deletes, truncates, chmods or re-ACLs an existing object. A writer instance that cannot take
the lease refuses before any mutation and before starting any helper (S2, S_O), so while one writer holds the lease no
other can start a launcher or an observer. Post-run work (conclusion, exports, recovery, release records, the front's
terminal record) is in the table: every one of those writes goes through a W-exclusive parent inside T.

**W2's capability.** W2 (`writer.py seal-front <N_F> <g> <A> <mode>`) takes the lease like any writer and may only
create new names under `attempts/<A>/w2-<k>/`, append markers to A's attempt journal and create export increments of
A. It verifies its capability before writing: W2 reads `/proc/<W2's parent>/stat` (the S3 sudo process) and
`/proc/<S3's parent>/stat`, and the latter's `(pid, start_time_ticks)` together with the current boot id must equal the
front-process triple committed in `attempt.json`. A different `sicarii` process cannot satisfy that, because the kernel
assigns pids and start times. In mode `recover`, W2 additionally requires the triple of the attempt's writer (from
`attempt.json`'s `writer`) to be absent or reused (§9.7). W2 never modifies an existing record.

### 5.3 Entrypoint closure

A process can carry a given uid or gid only through: inheritance from a process that already has it; a privileged
credential change by root or by a holder of `CAP_SETUID`/`CAP_SETGID`; executing a set-user-ID or set-group-ID file;
executing a file with file capabilities; or user-namespace mapping, which `newuidmap`/`newgidmap` permit only within
`/etc/subuid`/`/etc/subgid`. The table closes each route for each new identity. "Check" means a setup prestate or
verification item (§11.3, §11.6) and, where marked, a per-invocation check by the frame.

| Route | `wlscratch` (W) | `wlscratch-run` (R) | `wlscratch-gate` (GATE) |
|---|---|---|---|
| sudo | only rule naming W: `sicarii ALL=(wlscratch) NOPASSWD: <writer entry> *`; no other sudoers rule lists W in a Runas or user list, and no `sicarii` rule has Runas `ALL` without a password (operator inventory) | only rule: `wlscratch ALL=(wlscratch-run : wlscratch-gate) NOPASSWD: <launcher entry> *`, usable only by W | conferred only by that rule's `-g` (Option A) or by RL (Option B) |
| user manager | no linger; `sudo`'s PAM session uses `pam_systemd.so class=none` (observed in `/etc/pam.d/sudo`); probe P-MGR verifies that no `user@W.service` and no `/run/user/W` appear | linger (needed for the scope); every unit file of a process-starting type in the user unit load path at inventory time is masked, including `dbus.socket` and `dbus-broker.service` (one rule, §11.5 S-F; generated, later-installed and transient units are not masked and are governed by M-QUIESCENT, §9.4), and M runs without a PAM session and with the S-F drop-in's `no_new_privs` and seccomp filter, so M is R's only process outside the frame's participants; M can still start units that R's own processes request through its private socket, which is why §9.4 requires M quiescent and reference-free; the masks and the drop-in are root-owned, under a root-owned home and in `/etc`, so R cannot remove them | the manager's units run with R's default credentials, without GATE |
| sshd (active: observed `ActiveState=active`) | `DenyUsers wlscratch wlscratch-run` drop-in (§11.5 S-E); home root-owned, so no `authorized_keys` can be planted; no userdb record with keys (`userdbctl`) | same drop-in; home root-owned | not a login identity |
| login, getty, display manager | shell `/usr/bin/nologin`, password locked | same | n/a |
| PAM account controls | `sudo` uses `system-auth` (`pam_unix` account, `pam_time`) for the invoking user and opens its session with `pam_systemd.so class=none` (that no user manager results for W is probe P-MGR); login services (`system-login`) add `pam_access`, `pam_nologin` and `pam_shells`; the locked password makes every password authentication fail; account expiry (`usermod -e 1`) is applied only at rollback, because sudo must still reach the accounts while they are installed (observed stacks, P10) | same | n/a |
| `su`, `runuser` | `su` needs the target's password (locked); `runuser` is root-only (`pam_rootok`) | same | `newgrp`/`sg` need a group password: none is set (`gshadow` entry locked) |
| polkit, `pkexec`, `run0`, `machinectl` | require admin authentication (`unix-group:wheel`, interactive); no rules.d grant (operator inventory); `empower` empty | same | same |
| cron, at | not installed: `/usr/bin/crontab`, `/usr/bin/at`, `/usr/bin/batch` absent, cronie and atd not found, no spool directories (observed 2026-10-04); re-checked at setup and by W at every invocation (absence of those paths) | same | n/a |
| system units, D-Bus system services | no unit or D-Bus service file references W (operator `grep -r` inventory of `/etc/systemd`, `/usr/lib/systemd`, `/usr/share/dbus-1`, `/etc/dbus-1`) | same, except the user@R.service instance created by linger and its reviewed drop-in | none references GATE |
| setuid/setgid files and file capabilities | none owned by W (operator `find / -xdev \( -uid W -o -gid W \)` empty before and, apart from setup objects, after); no untrusted code ever runs as W | none owned by R at setup. A target could otherwise mint a set-user-ID-R file anywhere it can write (`/tmp` and the other places of §12.3 are on the `suid`-enabled root filesystem). Such a file would confer R, and R has owner rights on the partition contents through any retained descriptor, so v5 prevents every process tree of uid R from minting one: T's by C9 (§9.3) and M's by the S-F drop-in (§11.5, §9.8 K3); any process holding R is also a participant that every scan sees (§9.4) | the decisive route: a target holding GATE could chgrp a file to GATE and set the set-group-ID bit, and anyone executing it would gain GATE. C therefore sets `no_new_privs` and installs the anti-setid seccomp filter of §9.3 (step C9) before `exec` of T; the filter is inherited by every descendant. Processes outside T's tree that lack GATE cannot create GATE-group setid files (not members). The frame also refuses any set-user-ID or set-group-ID leaf it meets in g (§6.5), and every admission stage and the terminal check refuse any unknown GATE holder (§9.4) |
| user namespaces | W is outside every subordinate range; no range is allocated to W | same for R | GATE outside every subordinate gid range |
| existing processes | none at setup; afterwards only W instances (S1/S3 children) | M only, and L/C/T/O | only L/C/T/O and their descendants |

### 5.4 Subordinate-ID exclusion

Observed `/etc/subuid` and `/etc/subgid` (identical): `sicarii:100000:65536`, `cosmov1lab:165536:65536`,
`wlrehearsal:231072:65536`, `wldrill:362144:65536`, `worldline:296608:65536`. Every new uid and gid must lie outside
every listed range and no range may be allocated to a new identity. That keeps `sicarii` (and every other user) from
mapping them through `newuidmap`/`newgidmap`. Policy, checks and the post-setup re-check are in §11.2.

## 6. Modes, ACLs and access paths [corrections: W1-IMAGE-TREE, W1-COMMIT-JOURNAL-EXPORT, W1-SETUP-PROBES-ROLLBACK; gap: per-entry-modes-acls]

### 6.1 The v5 recipe and record modes are preserved exactly

v5 semantics (S:308-327, 913, 995-1026, 1992): the process umask is 077; `write_bytes` creates with 0600 and then
`fchmod`s to the requested mode (default 0600, so every JSON record and stream is 0600); created directories are
authenticated at 0700; the overlay snapshot keeps 0600 files in 0700 directories; recipe directories are created 0700
and then set to their base directory mode, deepest first, the root last; recipe files are written with their row's
mode (the base inventory mode, or 0644 for a new overlay unit).

W-1 keeps every one of these. **No ACL is set on any recipe object, frame record, snapshot entry, stream file,
marker or journal, and no default ACL exists anywhere in the design**, so the umask 077 semantics apply exactly as in
v5 to everything W and the target create.

Recipe-mode property, observed on the pinned base (inventory `943ea95e…3bf`, directory modes `1049c831…bde`): 635
files, 617 with mode 0644 and 18 with mode 0755 (617 + 18 = 635, JACKAL exact, parsed `617+18`); 55 directories, all
0755. Overlay units take a base mode or 0644. Every recipe file is therefore others-readable and every recipe
directory others-readable and others-searchable. W records this as `recipe_mode_property` at M7. It is not a new
refusal of an accepted case: for the pinned base it holds row by row, and a base with other modes would be a
different pinned base, which is itself a reviewed change.

### 6.2 Why ACLs never touch a mode that is recorded

POSIX ACL semantics (acl(5)): a named-user or named-group entry requires a mask entry; `stat` reports the mask in
the group bits of `st_mode`; `chmod` rewrites the mask. A named entry on a 0600 file therefore shows as 0640 or 0620
and changes the observed mode. A default ACL on a directory replaces the umask for new entries (their ACL is derived
from the default ACL and the creating mode), so a default ACL inherited "under 0600" does not give the promised read
access and silently changes creation semantics. v4 therefore puts ACLs only on objects whose modes are not part of
the recipe or of any v5 record, and puts no default ACL anywhere:
- setup objects `/var/lib/wlscratch`, `runs/` (T_root) and `runs/records` (R_root);
- the generation root g and its record root g_rec (each created 0700, authenticated at 0700 by
  `Dir.child(create=True)`, then given its ACL; v5 records no mode for its run directory);
- the adoption roots `adoption-<I>`;
- the four partition roots (v5 records partition identities but never partition directory modes, S:502-503);
- export directories and export files, which are new writer-produced copies whose final mode, after the ACL, is the
  one their export marker records (§15.3);
- Option A only: `/home/sicarii` (operator-captured before and after, §11.5 S-G).

### 6.3 Per-object owners, modes and ACLs

ACLs are written by W through `fsetxattr(fd, "system.posix_acl_access", …)` on the held descriptor (POSIX ACL xattr
version 2 encoding; entries sorted by tag then id) and read back with `fgetxattr` plus `fstat`; a mismatch refuses.
Setup ACLs are written by `setfacl` as root and read back with `getfacl -n`. "GATE" and "W", "R" are numeric ids;
`1000` is `sicarii`.

| Object | Owner:group | Base mode | Access ACL (`getfacl -n` order) | `st_mode` shown | Default ACL |
|---|---|---|---|---|---|
| `/var/lib/wlscratch` | root:W | 0750 | `user::rwx user:1000:--x group::r-x group:GATE:--x mask::r-x other::---` | 0750 | none |
| `lease/` | root:W | 0750 | none | 0750 | none |
| `lease/writer.lock` | root:W | 0440 | none | 0440 | n/a |
| `runs/` (T_root) | W:W | 0700 | `user::rwx user:1000:--x group::--- group:GATE:--x mask::--x other::---` | 0710 | none |
| g | W:W | 0700 | same text as `runs/` | 0710 | none |
| `runs/records` (R_root), g_rec, `adoption-<I>` | W:W | 0700 | `user::rwx user:1000:--x group::--- mask::--x other::---` (no GATE entry) | 0710 | none |
| `generation.json`, `materialization.json`, `inputs/**`, `commits/**` of g | W:W | 0600 files, 0700 dirs | none | same | none |
| `overlay-snapshot/**` | W:W | 0600 files, 0700 dirs (v5) | none | same | none |
| `source/` and every recipe directory | W:W | recipe mode (0755 for all 55 observed) | none | same | none |
| recipe files | W:W | recipe mode (0644 or 0755 observed) | none | same | n/a |
| `obj/`, `lib/`, `resource-tests/obj/`, `resource-tests/bin/` roots | W:W | 0700 | `user::rwx group::--- group:GATE:rwx mask::rwx other::---` | 0770 | none |
| partition contents | created by T: uid R, group GATE unless T changes it | as T leaves it (T may `chmod` and set ACLs on what it owns); from each later dispatch's parent stage, without any group-class or other-class write bit (§9.8 K1-K2) | none set by the frame; T may set entries, whose write permission the cleared group-class bits mask | as T leaves it, then without those write bits | none set by the frame; T may set one, which affects only entries created later, which the next parent stage revokes again |
| `attempts/**` (records, markers, `fallback.journal`, stream and observer files, `w2-<k>/**`); `adoption-<I>/commits/**`, `invocations/**`, `lead-adoption.json` | W:W | 0600 files, 0700 dirs | none | same | none |
| `export/` of g_rec and of `adoption-<I>`, and every directory below them | W:W | 0700, then the ACL | `user::rwx user:1000:r-x group::--- mask::r-x other::---` | 0750 | none |
| export files | W:W | 0600 at creation, then the ACL | `user::rw- user:1000:r-- group::--- mask::r-- other::---` | 0640, the final mode the export marker records (§15.3) | n/a |
| `/var/lib/wlscratch-run` | root:root | 0755 | none | 0755 | none |
| `/var/lib/wlscratch-run/tmp` | R:R | 0700 | none | 0700 | none |
| `/var/lib/wlscratch-run/.config`, `…/systemd`, `…/systemd/user` | root:root | 0755 | none | 0755 | none |
| mask links in `…/systemd/user` | root:root symlink → `/dev/null` | n/a | n/a | n/a | n/a |
| `/etc/systemd/system/user@<R>.service.d/` | root:root | 0755 | none | 0755 | none |
| `…/user@<R>.service.d/50-wlscratch.conf` | root:root | 0644 | none | 0644 | n/a |
| `/opt/wlscratch`, `/opt/wlscratch/frame-v6w1/**` | root:root | 0755 dirs, 0644 files | none | same | none |
| `/opt/wlscratch/setup-identities.json` | root:root | 0644 | none | 0644 | n/a |
| image roots (images only, §14.5): the work image root seen at `runs/`, the records image root seen at `runs/records` | as `runs/` and `runs/records` above | | | | |
| bare mount points (images only; visible only while unmounted) | root:root | 0700, empty | none | 0700 | none |
| `/var/lib/wlscratch-images` (images only) | root:W | 0710: search for W only (W and W2 look up the pinned image files by name; nobody but root lists or opens them) | none | 0710 | none |
| the image files in it (images only) | root:root | 0600 | none | 0600 | n/a |
| `lost+found` of each image root (images only; made by `mkfs.ext4`; never used, opened or walked by the frame) | root:root | 0700 | none | 0700 | none |

### 6.4 Access paths

- **The target reads admitted source** through `/var/lib/wlscratch` (GATE `--x`), `runs/` (GATE `--x`) and g (GATE
  `--x`), then through the recipe's own others bits (0755 directories, 0644/0755 files). It writes only partition
  contents, through the roots' GATE `rwx` and its own ownership of what it created, and its stream files, through
  descriptors it was given. It never needs write access to a recipe directory, because the partition roots exist
  before it runs. `runs/records` has no GATE entry, so P_att, P_exp and P_ado are not even searchable for it.
- **C and O** use the same path as the target. They read partition contents as their owner (uid R). As in v5, where
  the frame ran as the target's owner, a target-created object without owner read permission yields an observation
  failure and a non-success outcome. Everything C needs from the records tree reaches it over its channel.
- **The writer never opens a target-owned object.** Its own walks treat the four roots as opaque (root identity,
  mode and ACL only). It receives partition observations and the report bytes (`obj/core/gnatprove/gnatprove.out`) from
  O over the channel and writes its own copy, as v5 copied the report (S:1696-1708).
- **The lead reads evidence only from P_exp and the adoption exports**, through `user:1000` entries on
  `/var/lib/wlscratch`, `runs/`, `runs/records`, g_rec and `adoption-<I>` (`--x`) and on the export directories and
  files (`r-x`, `r--`). The lead could also read the recipe through g (`--x`) and the recipe's others bits, which is its
  own base content; nothing else in g or in the records tree has an entry for it.
- **The target account's manager M** (uid R without GATE) has no entry on `/var/lib/wlscratch` and falls to
  `other::---`, so it cannot reach g or the records tree by path at all.
- **Pre-created partition roots.** v5's target created `obj/` and the other partition directories itself, inside a
  source tree it owned. Under W-1 the writer creates the four roots at M7 (empty, writer-owned, GATE `rwx`), so the
  target never needs write access to a recipe directory. The partition paths, their exclusion rules and the
  allowlisted commands are unchanged; v5's "no generated output at materialization" check becomes "exactly the four
  empty writer-created roots at materialization", which is stricter for everything else. The only behaviour the
  target loses is removing or renaming a partition root itself. No allowlisted action (gnatprove proof actions,
  `gprbuild -p -c`) is known to do that; this is a compatibility hypothesis that the first engineering run's evidence
  must confirm. If it is false, W-1 must be redesigned; the accepted case is not narrowed.

### 6.5 Denial matrix (each cell is a probe in §13)

| Object | `sicarii` (A1) | T, C, O (R + GATE) | M and any R process without GATE | W |
|---|---|---|---|---|
| `/var/lib/wlscratch` | search only | search only | none | read, search |
| `lease/`, `writer.lock` | none | none | none | search; open read-only and `flock` |
| `runs/`, g | search only | search only | none | full (owner) |
| `runs/records`, g_rec, `adoption-<I>` | search only | none | none | full (owner) |
| P_adm records, `inputs/`, snapshot, `commits/` | none | none | none | full (owner); code writes create-only |
| recipe directories | read, search | read, search | none | full (owner); code does not mutate after M8 |
| recipe files | read | read | none | owner; code does not mutate |
| partition roots | none | create, rename and unlink entries | none | owner; code never uses |
| partition contents | none | owner of what T created | none by path; owner rights only through a held descriptor (§9.4) | none |
| P_att and P_ado originals | none | none (stream bytes only through passed descriptors) | none | full (owner) |
| P_exp and adoption exports | read | none | none | full (owner) |
| `/var/lib/wlscratch-run/tmp` | none | owner | owner | none |

In every cell marked "none", "read" or "search", every mutation (create, `mkdir`, `unlink`, `rmdir`, `rename` in or
out, `link`, `symlink`, `open` for write, `truncate`, `chmod`, `chown`, `setfacl`, `utimensat`) must fail. The errno
is that of the first kernel check that fails, so it depends on the operand: a missing search permission on an
ancestor gives `EACCES` at path resolution; a create, unlink, rename or symlink in a directory the actor can search
but not write gives `EACCES`; an open for writing, a `truncate` or a `utimensat` without explicit times on a file the
actor can reach but not write gives `EACCES`; `chmod`, `chown`, an ACL `setxattr` and `utimensat` with explicit times
by a non-owner give `EPERM`; a hard link of another owner's file that the actor cannot both read and write gives
`EPERM` (`fs.protected_hardlinks=1`); a rename or link across mounts gives `EXDEV` before any permission check, which
is why §13 requires same-mount operands. §13 lists the operand, precondition and expected errno of every probe cell.
The frame's walks additionally refuse any symlink, special file, multiply linked regular file, and (new in W-1) any
set-user-ID or set-group-ID leaf in g.

## 7. Channels, expectations and dumpability [correction: W1-GENERATION-PROTOCOL; gap: channel-and-dumpability]

### 7.1 Channels and transports

| Channel | Transport | Created by | Carries |
|---|---|---|---|
| F↔W and F↔W2 | three pipes: F→W on W's fd 0, W→F framed messages on W's fd 1, W→F diagnostics on W's fd 2 | F, after its first act; F's ends close-on-exec | inputs, observations, requests, answers, record descriptors |
| W↔L | `AF_UNIX`/`SOCK_STREAM` socketpair SP_L on L's fd 0; L's fd 1 and fd 2 are `launcher.stdout`/`launcher.stderr` in P_att, created by W before `launcher-intent.json` binds them | W | `GO` with record bytes, `FDS` with three descriptors by `SCM_RIGHTS` (SP_C's end, `scope.stdout`, `scope.stderr`), `LAUNCHER_START`, `LAUNCHER_WAIT`, `STOP` |
| W↔C | socketpair SP_C: W keeps one end and passes the other to L in `FDS`; L gives it to SR as stdin, and C keeps it as fd 0 after the scope `exec`. C's fd 1 and fd 2 are `scope.stdout`/`scope.stderr` (W-created, passed through L) | W | child stage, record bytes, `STREAMS` with the child stream descriptors by `SCM_RIGHTS`, `SPAWN_REQUEST`/`SPAWN_OK`, child records, waits, `STOP` |
| W↔O and W2↔O | socketpair SP_O on O's fd 0; O's fd 1 and fd 2 are `observer-<n>.stdout`/`.stderr`, created before `observer-intent-<n>.json` binds them | W or W2 | observation requests and results, report bytes |

`sudo` passes only fds 0-2 (its default `closefrom` is 3), so every helper gets exactly one bidirectional socket on
fd 0 and two W-created files on fd 1 and fd 2; further descriptors travel only by `SCM_RIGHTS`. L never reads or
writes SP_C: C's messages reach W directly, so v3's relay through L is gone and the W↔C chain is end to end. Under
Option B, RL sits between S2 and L, and between S_O and O, and passes the helper's fds through unchanged (§12.2); before
its `exec` it writes exactly one `RL_IDENTITY` frame on fd 0, on a direction of its own (§7.3).

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

### 7.3 Chain initialization, validation and retained form

- `head0(dir)` is defined in §4.4. The receiver of message k of a direction requires `seq == k` and
  `prev == head_k`, then sets `head_{k+1} = SHA256(bytes.fromhex(head_k) ‖ payload_k)`. The prototype implements the
  same recurrence (ENGINEERING_ONLY).
- The first message from the helper side of each channel (`W_HELLO`, `W2_HELLO`, `L_HELLO`, `C_HELLO`, `O_HELLO`)
  carries that process's own fresh 64-hex nonce and its identity; the first message of the other direction
  (`HELLO_ACK`, `GO`, `RECORDS`, `OBSERVE_REQUEST`) echoes the nonce. Each side refuses a hello whose identity fails
  §8.1's joins. A writer that refuses before its hello sends `EARLY_REFUSAL` as its first message instead; it carries
  no nonce, gets no reply, and the channel then ends (Appendix B.4.4).
- **Option B's RL frame.** Under Option B the first frame on the W↔L and W↔O sockets is RL's `RL_IDENTITY`, the only
  message of the direction `RL2W`, whose genesis is §4.4's `head0("RL2W")` computed with the nonce of the helper RL
  serves (`n_wl` or `n_o`); the helper's own `L2W` or `O2W` chain then starts at seq 0 with `L_HELLO` or `O_HELLO`. W
  verifies the frame (§9.3 G3) and commits it before it sends `GO` or its first `OBSERVE_REQUEST`. Under Option A any
  `RL_IDENTITY`, and under Option B a missing or second one, is a channel failure.
- **Bulk carriers.** A bulk transfer is allowed only immediately after a control message whose schema declares a
  `bulk` list (Appendix B.4); the sender must then send exactly one `BEGIN`/`CHUNK`/`END` sequence per listed name, in
  the listed order, before any other message in that direction. Anything else is a channel failure (§7.4).
- **Retained form.** W retains its channels as create-only segment records `channel/<channel>-<first-seq>-<last-seq>.json`
  (in `attempts/<A>/` for W, in `w2-<k>/` for W2, in `invocations/<stamp>/` for `adopt`), written at every state
  boundary of Appendix B.4.4 and at conclusion, each with a marker. A segment holds, per message, `{dir, seq, prev, kind,
  length, payload_sha256}` and the payload, except that bulk chunk data is replaced by a reference: `{record, offset,
  length, sha256}` to the committed record it became; `{written, offset, length, sha256}` to the P_adm recipe or
  snapshot path its bytes were written to; or, for the verify-only inputs of `adopt` (§4.6), `{source, offset, length,
  sha256}` naming the sealed lead-tree path F read. A verifier reconstructs every payload from those places and
  recomputes both chains. If W dies, messages after the last committed segment are durability-UNKNOWN (§10.5); records
  still carry the heads.
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
| argv | F: W's and W2's exact argv; W: S2/L, S_O/O argv, the scope and C templates; W2: its S_O/O argv; C: its own sealed command line | `/proc/<pid>/cmdline` read by the parent role, `SUDO_COMMAND`, C's `/proc/self/cmdline` (v5 S:1786-1791) |
| records | W: every marker it wrote (the journal head and the committed set); F: every descriptor it was sent | the attempt-journal join of §10.6: every committed record unchanged; the fallback journal by its allocation descriptor and slot prefix, never by a content digest; drift is an error |
| exports | W: each increment's manifest and freeze descriptors with their final values (mode 0640, ACL); F: the freeze-marker digests from `EXPORTED` and `FINAL` | F re-reads every export copy through its ACL and compares with the manifest's final values (§15.3) |
| adoption | W: the committed adoption record and its marker (D3); F and C: the bytes W delivered | F's frame admission front part; C's `launch.adoption` join (§4.6) |
| streams | W: the `[dev, ino]` it bound in `launcher-intent.json` | L's and C's checks of the descriptors they receive (§9.3) |
| participants | W: S2, L, SR/C, T, O identities (§9.1); W2: its O; F: S1, W, S3, W2 and the participants reported to it | the scans and classifications (§9.4) |

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
  entries root-owned; `os` is already loaded by interpreter start-up, so binding it loads nothing new). On any failure the process writes one line to stderr and exits 125 with no other action. Both
  readbacks go into its role identity (§8.1). `/proc/self/status` has no `Dumpable` field on this host and is not used.
- **Relative to start-up.** Before the first act come: the dynamic loader, `libpython` initialization, the encodings
  import, `site` (for F including the user site directory and its `.pth` processing; for the `-I` helpers only the
  system site), and `import ctypes` with its own imports. Only then the two `prctl` calls, then the `sys.flags` checks
  of §8.2, then every other import.
- **Each invocation.** `execve` resets the attribute (to 1 when the credentials do not change in the exec), so every
  process sets it itself: F, W, W2, L, C (after systemd-run's `exec` into it), O and RL. T does not (R3).
- **Pre-first-call residual, per role.** F (uid 1000) is readable by every `sicarii` process until the call: its
  environment, command line and inherited descriptors (Yama still blocks attach). Its channel pipes are created after
  the call and are never exposed. W and W2 are readable only by other `wlscratch` processes (frame writer instances)
  and root. L, C and O are readable by other `wlscratch-run` processes (the manager baseline) until the call; their
  channel sockets cannot be reopened through `/proc` and their stream files are W-owned 0600. The window's duration is
  not measured; probe P-DUMP timestamps it. This residual is stated, not accepted as a new guarantee.

## 8. Fresh identities, the real outer invocation, context relocation and the vault [gap: fresh-identities-and-vault]

### 8.1 Per-invocation role identity

Every process of every invocation records a fresh `wlscratch-role-identity-v1` (Appendix B.1) immediately after its
first act (§7.7). It contains: role; boot id; pid, ppid, `start_time_ticks` (field 22 of `/proc/self/stat`); comm;
argv (`/proc/self/cmdline`); exe (`readlink /proc/self/exe`, `[dev, ino]`, sha256); all four uids and gids and the
supplementary groups (`/proc/self/status`); capability sets, `NoNewPrivs` and `Seccomp`; both dumpability readbacks;
umask; resource limits; cgroup (`/proc/self/cgroup`); mount, pid and user namespace inodes; cwd `[dev, ino]`; for fds
0-2 the file type, `[dev, ino]`, mode and open flags, and the full list of open fds; the environment as sorted names
plus the sha256 of every value, with clear values only for the non-secret keys `HOME USER LOGNAME LANG PATH SHELL PWD
TMPDIR XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS INVOCATION_ID SUDO_USER SUDO_UID SUDO_GID SUDO_COMMAND` and every
`PYTHON*` key; Python `sys.version`, `sys.executable`, prefixes, every `sys.flags` field and `sys.path`; and the loaded
module closure (every `sys.modules` entry with a file: name, path, size, sha256; builtin names listed). The parent role
independently reads the child's `/proc/<pid>/{stat,status,cmdline,cgroup}` and joins them with the child's
self-report (pid, start time, credentials, command line); a mismatch refuses before launch and is an error after.

Per stage, in addition (each a fresh observation, never reused across stages or attempts):

| Role | Parent stage | Child stage | After (conclusion) |
|---|---|---|---|
| F (real lead context) | fresh lead observation `scratch-run`; frame admission front part; base-tree re-observation; v5 runtime-closure observation with the **original** unrelocated spec against the **original** baseline (compact if equal, v5 item 4); `systemctl --user show-environment` of `sicarii`'s manager against the original `manager_environment` baseline; sibling units and `storage_status.py` | the same set with stage `scratch-child`, and the window ownership check | the same set except the lead observation, as v5 conclusion re-ran frame admission and identities |
| W | own identity against the reviewed writer-context baseline (system standard library only, `-I` flags) | lease, location, snapshot, record-drift writer half | same, plus the conclusion of §9.4 |
| O (target context) | full walk; tool, proof-data, proof-ELF, vendor and runtime-closure observations with the relocated spec; R's manager environment; the scans of §9.4 | n/a | same as parent, plus the report bytes |
| C (target context) | n/a | v5 child admission in full (§9.3 C1-C11), with the same observations as O and the final pass | n/a |

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

### 8.3 The original target path and caps are kept

- `child_argv` is exactly v5 `command()`: `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/bin/gnatprove -P
  core/worldline_core_sources.gpr -U --mode=all --level=3 --report=all --checks-as-errors=on --proof-warnings=on -j2`
  (with `-k` for `prove-all-k`), the `prove-file`/`prove-subp` forms, or the `gprbuild … -p -j2 -c -U` form for
  `compile-all`. The path is executed as written (R4); Options A and B both make that exact path resolvable (§12).
- The scope is `systemd-run --user --scope --unit=<U> -p MemoryMax=8G -p MemorySwapMax=0`; `RLIMIT_CORE` is (0, 0)
  from L's pre-exec of systemd-run and is inherited; C reads back `memory.max == 8589934592`, `memory.swap.max == 0`,
  core `[0, 0]` and its scope membership (v5 S:1828-1838). `-j2` stays in the argv.
- `MIN_MEM_AVAILABLE_KB = 16777217`, `MAX_CHALLENGES = 3`, the 300 s and 30 s receipt deadlines and the 30 s
  observation timeouts are unchanged; the target executable's digest is checked against the baseline before the spawn
  (v5 S:1839-1841).
- W-1 adds two restrictions on T and changes no cap: `no_new_privs`, and the anti-setid seccomp filter (§9.3 C9),
  both needed so that T cannot mint a GATE-conferring file (§5.3). They are reviewed deltas with a compatibility
  hypothesis: no allowlisted action sets set-user-ID or set-group-ID bits or relies on `io_uring` or `openat2`. If
  that is false, W-1 must be redesigned; no accepted case is narrowed.

### 8.4 Context relocation table and the new baselines

The target now runs as R, so the account-bound part of its environment must change. Nothing else may. v5 already
relocated four source-bearing keys and one runtime-closure entry to the run's source (S:1077-1095); W-1 keeps that
rule (with g's source path) and adds exactly these relocations:

| Key or entry | v5 value and source | W-1 value |
|---|---|---|
| `HOME` | `/home/sicarii`, from the run's environment (`KEEP_ENVIRONMENT`) | `/var/lib/wlscratch-run` |
| `USER`, `LOGNAME` | `sicarii`, same | `wlscratch-run` |
| `LANG` | the lead environment's value | the lead environment's value, as observed by F and streamed (unchanged) |
| `XDG_RUNTIME_DIR` | `/run/user/1000` (tool spec) | `/run/user/<R>` |
| `DBUS_SESSION_BUS_ADDRESS` | `unix:path=/run/user/1000/bus` (tool spec) | `unix:path=/run/user/<R>/bus` |
| `TMPDIR` | `/home/sicarii/.cache/workflow-tmp` (runtime spec) | `/var/lib/wlscratch-run/tmp` |
| runtime-closure `mutable_directory_identities` entry for `TMPDIR` | `/home/sicarii/.cache/workflow-tmp` | `/var/lib/wlscratch-run/tmp` |
| runtime-closure tree `/home/sicarii/.local/lib/python3.14/site-packages` | `sicarii`'s user site, observed | `/var/lib/wlscratch-run/.local/lib/python3.14/site-packages`, required absent |
| `PENDING_LIBRARY_DIR`, `PENDING_OBJECT_DIR`, `PYTHONPATH`, `WORLDLINE_CORE_LIB`; runtime entry for the source | F10K source path | g's source path (v5 rule) |
| `PATH`, `GPR_PROJECT_PATH`, `GNAT_ROOT`, `WORLDLINE_BUILD`, `PYTHONDONTWRITEBYTECODE`, every `null` key | spec | unchanged, byte-identical |

`HOME` itself is root-owned and not writable by R (§6.3, S-F), so that no `~/.ssh/authorized_keys` and no persistent
user unit can be planted there; v5's target could write its `HOME`. This is a compatibility hypothesis: the
allowlisted actions write their outputs to the object directories and `TMPDIR`, not to `HOME`. The first engineering
run's evidence must confirm it; if it is false, W-1 must be redesigned and the accepted case is not narrowed.

**User bus (v4).** `DBUS_SESSION_BUS_ADDRESS` keeps its relocated value byte for byte, but `dbus.socket` and
`dbus-broker.service` are masked for R (§11.5 S-F), so the socket it names does not exist and a connection attempt
fails. `systemd-run --user --scope` does not need the bus: it talks to M over M's private socket. This is a
compatibility hypothesis: no allowlisted action uses the session bus. The first engineering run's evidence must
confirm it; if it is false, W-1 must be redesigned and the accepted case is not narrowed.

New baselines, each reviewed installed evidence before adoption (§16): the relocated runtime-closure inventory (the
v5 inventory with the user-site subtree removed and recorded absent, the `TMPDIR` row replaced by R's directory row,
the source row relocated); R's manager environment, as M has it without a PAM session (§11.5 S-F); M's static unit
and socket baselines S_units and S_socks (§9.4, §11.6); the writer-context baseline. The tool, proof-data, proof-ELF and
vendor baselines are expected byte-identical in the target context, because the toolchain files are the same; any
difference keeps the full observation and refuses (v5 `retain_observation`), pending review. Under Option A, `PATH`
entries below `/home/sicarii` that are not others-searchable become unresolvable for T; under Option B every `PATH`
entry below `/home/sicarii` except the bound toolchain is absent (§12.2). The tool-inventory observation records the
effect, and its baseline for the chosen option is part of the reviewed installed evidence.

### 8.5 Vault scope

- **What is pinned:** P_exp(g), the path `g_rec/export` (`/var/lib/wlscratch/runs/records/<g>/export`), which
  `sicarii` can read through the ACLs of §6.3. The originals in g and g_rec are unreadable to `sicarii`; they are
  neither pinned nor backed up by the vault. Their custody is the protected local tree.
- **Who and when:** F, as `sicarii`, runs `project-vault pin <g_rec>/export` and `project-vault status` at M10 and at
  D9, each under the original 30 s observation timeout, keeping the authentic HOME, configuration, user bus, reserve,
  queue and backup state of `sicarii`; W records the results (v5 S:1562-1563 did the same for its run directory). Both
  must succeed or the stage refuses, as in v5. `storage_status.py` and `project-vault` are never run as W or R.
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

Launch participants of attempt A: S2, L, SR/C (one pid: systemd-run `exec`s C inside the scope), U, T and all its
descendants, and under Option B also RL. Observer participants: every S_O/O started for A, by W or by a W2, and under Option B the RL before each O.
Post-writer participants: every S3/W2 of A. F and W are the owner processes (as v5's dispatch and run). Schemas
(Appendix B.2): `wlscratch-participant-v1` `{role, pid, start_time_ticks, boot_id, ppid, uids[4], gids[4], groups,
cmdline, cgroup, observed_by, at, state ∈ {alive, absent, reused, unknown}}`; `wlscratch-wait-v1` `{waiter_role,
waited_role, pid, start_time_ticks, boot_id, raw_status, exited, exit_code, signaled, signal, core_dumped, wait_error,
interrupts, unresolved, at, meaning}`; `wlscratch-scope-v1` `{manager_uid, unit, invocation_id, control_group,
properties_at_start, properties_at_end, cgroup_state ∈ {ABSENT, EMPTY, NONEMPTY, UNAVAILABLE}}`; `wlscratch-scan-v3`
(§9.4; v4's `wlscratch-scan-v2` with the fields of v5's scans, Appendix B.2). A process is identified by `(pid, start_time_ticks, boot_id)`: a different start time at the same pid means
the original ended and the pid was reused; a different boot id means the original ended with its boot.

A participant is known only from positive evidence: a committed record or a received message that names its triple,
or a scan that sees it. The absence of a record never shows that a participant does not exist. Whether any launch
participant may still exist is decided only by the complete scans of §9.4.

O's jobs per invocation: the scans of §9.4 that need R credentials (SCAN-UNITS, SCAN-REFS, SCAN-QUIESCE,
SCAN-LEASE and, at the parent stage, SCAN-WCLOSED), at the parent stage the write revocation of §9.8 K1 before its
walk, the full walk of `g/source` (v5 `verify_materialization` with v6's final pass, returning every excluded
leaf's `stat_key`), the target-context identities (`parent` or `after`), at `after` the report bytes, and under W2 the
recovery rounds (§9.7).

### 9.2 Waits, reaping and relay

| Waiter | Waits for | Mechanism | Retained as |
|---|---|---|---|
| F | S1, and through sudo's relay W | `waitpid` on S1 (F's child) | front terminal record via W2: S1's raw status, W's self-reported final status (from `FINAL`), and W's `(pid, start)` absent or reused afterwards |
| F | S3 (W2) | `waitpid` | console only. It is the last wait, as v5's lead wait of `dispatch` was |
| W | S2 (and L through relay), each S_O (O) | `waitpid` | `sudo-launcher-wait.json`, `observer-wait-<n>.json` |
| W2 | each S_O (O) it started | `waitpid` | `w2-<k>/observer-wait-<n>.json` |
| L | SR = C | `waitpid` | sent to W as `LAUNCHER_WAIT`, committed as `launcher-wait.json` (v5 meaning: the actual wait of the systemd-run scope launcher) |
| C | T | `waitpid` (`wait_blocked`) | sent to W as `CHILD_WAIT`, committed as `child-wait.json` (v5) |

Every wait record is committed before any cleanup (v5 V4-B02 rule). Relay evidence: `sudo` reports the command's
status; whether it re-raises a fatal signal is probe P-RELAY. The parent role always keeps both its direct child's raw
status and the grandchild's self-report; disagreement is an error. Each role reaps only its own children. An orphan
(a child whose parent died) is not waited for by the frame; it is observed by the scans until it ends. Handled
signals are blocked at the start of every role and consumed only synchronously (frame plan H-S1, H-M3).
`STOP` messages travel down the channels (F→W, then W→L before `GO` and W→C after it), and C forwards `SIGTERM` to T
exactly as v5's `wait_blocked` did. W cannot signal L or C (different uid) and does not try.

### 9.3 Launch gating [corrections: W1-PROTOCOL-FAILURE-STATES, W1-CUSTODY-CLOSURE; v4: W1-GENERATION-PROTOCOL]

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
  `launcher-start.json`. Under Option B the rule's sudo front-end starts RL, which writes `RL_IDENTITY` on fd 0 before
  it `exec`s L (§7.3). W reads that frame first, verifies it (all uids R, all gids GATE, groups `[R]`, every capability
  set zero, `NoNewPrivs: 1`, a mount namespace other than W's, the `/home/sicarii` mountinfo lines and the held
  toolchain identity of §12.2) and commits `launcher-rl-identity.json`. A missing or second RL frame is a channel
  failure (Appendix B.4.5), after which W sends no `GO`; a frame that fails W's verification makes W send `STOP`. Either
  way L exits 125 having started nothing, and W refuses before launch. The same holds for every S_O under Option B
  (`observer-<n>-rl-identity.json`, committed before the first `OBSERVE_REQUEST`; on a failing frame W sends `O_BYE`
  instead of a request).
- G4. L: first act, identity, argv grammar; requires ruid = euid = suid = fsuid = R and rgid = egid = sgid = fsgid =
  GATE (under either option; Option B's RL produces the same credentials, §12.2), fd 0 a socket and fds 1-2 regular
  files; sends `L_HELLO`; waits for `GO` within the control deadline.
  **EOF or deadline before `GO` → L exits 125 having started nothing.**
- G5. W verifies L through `/proc/<L>` (credentials, `PPid == S2`, start time, cmdline) and sends `GO` with the bytes
  of `launch.json`, `admission.json` and `launcher-intent.json`, then `FDS` with SP_C's other end and the bound
  `scope.stdout` and `scope.stderr` descriptors by `SCM_RIGHTS`.
- G6. L verifies the two seals (sha256 of the delivered `launch.json` and `admission.json` equal its argv), that
  `launcher-intent.json`'s scope argv is exactly what it will run, and that its own fds 1-2 and the received scope
  descriptors have the `[dev, ino]` the intent binds; sets umask 077 and `no_new_privs`; reaches its **interruption
  point**: a non-blocking poll of SP_L, where a pending `STOP` makes L send `L_REFUSAL` (stage `stop`) and exit 125
  having spawned nothing (any other pending frame is a channel failure with the same effect); then makes its **spawn
  call**: SR = `/usr/bin/systemd-run --user --scope --unit=<U> -p MemoryMax=8G -p MemorySwapMax=0 /usr/bin/python3 -I -B
  /opt/wlscratch/frame-v6w1/launch_target.py child <n_c> <g> <A> <launch_sha> <admission_sha>` with stdin = the
  received SP_C end, stdout/stderr = the scope descriptors, the environment of `launch.json`, and a pre-exec that sets
  `RLIMIT_CORE` (0, 0) and unblocks the handled signals (v5 `spawn`). If the call returned SR, L closes its own copy of
  the SP_C end and sends `LAUNCHER_START` with SR's identity. If it failed and `waitpid(-1, WNOHANG)` reports `ECHILD`
  (no child exists), L sends `L_REFUSAL` (stage `spawn`) and exits 125. If it failed while a child exists, L sends
  nothing more about the launch: it waits for its children, writes what it knows to its stderr and exits, and the
  classification decides. A `STOP` that reaches L after its interruption point is read after the spawn call and
  recorded; W stops C over W↔C, never through L.
- C1. C (inside the scope after the `exec`): first act, identity; requires its `/proc/self/cmdline` to equal the
  sealed template plus `[n_c, g, A, launch_sha, admission_sha]`, its cgroup to end in `/<U>`, its credentials R/GATE,
  its parent to be L, `INVOCATION_ID` to be 32 hex, its environment minus `INVOCATION_ID` to equal `launch.json`'s,
  fd 0 a socket and fds 1-2 the scope files whose `[dev, ino]` `launcher-intent.json` binds; sends `C_HELLO` to W
  over SP_C. (That C's pid equals SR's, because a scope `exec`s in place, is verified by probe P-LAUNCH; if
  systemd-run were to fork instead, C's parent would be SR and both identities would be recorded and joined.)
- C2. W verifies C through `/proc/<C>` (pid equal to SR's as L reported it, credentials, cgroup, cmdline) and sends
  `RECORDS` (the bytes of `launch.json`, `admission.json`, `reservation-intent.json`, `reservation.json`,
  `launcher-intent.json`, `materialization.json`, `lead-adoption.json` and the lead module) and `STREAMS` (`child.stdout`
  and `child.stderr` by `SCM_RIGHTS`). C verifies the lead module against the compiled pin and every v5 child join
  (S:1782-1817): both seals; `intent.launch` equals the delivered `launch.json` descriptor; `admission.launch` equals
  `intent.launch`; the `reservation.json` token taken from the `admission.json`-pinned record (frame plan H-M6) equals
  the intent's token; `launch.materialization` equals the delivered `materialization.json` descriptor;
  `launch.adoption` equals the delivered adoption record's descriptor; and the received child stream descriptors have
  the identities `launcher-intent.json` binds.
- C3. C opens g and `source/` by anchored chains and requires their identities to equal the seal; the attempt and
  snapshot identities are checked by W in C4.
- C4. `CHILD_STAGE_REQUEST`. W performs the writer half (snapshot observation equals the record, attempt-directory
  identity equals the seal, the attempt-journal join of §10.6, lease held, location chains unchanged) and obtains F's
  child-stage half (§8.1: fresh lead observation `scratch-child`, `owns_window(LEAD_ID, attempt path, token)` under the
  window lock, frame admission front part over the adoption bytes, base-tree re-observation, F's runtime and manager
  identity, the front half of the `child-final` sample with the reserve equal to the bound). W commits both halves and
  sends them to C (`CHILD_STAGE_RESULT`).
- C5. C requires `launch.holder == LEAD_ID == intent.holder_task` and window ownership true (v5 S:1809-1811); runs
  the installed-frame inventory check, the target-context identities `child`, and the admission walk with source-tree
  identities equal to the seal (v5 S:1812-1813).
- C6. v5 S:1814-1841 in order: pins (frame inventory, review, adoption, materialization), environment, parent memory
  gate, the helper half of `child-final` (sibling units of M allowing only U, heavy-process refusal, meminfo at or
  above 16777217 kB), cwd, allowlist re-derivation, limits readback, scope membership, target executable digest.
- C7. Child-stage scans (§9.4, child-stage point): every scan passes, SCAN-GATE contains both L and C, SCAN-SCOPE shows
  U holding exactly C, SCAN-UNITS equals S_units ∪ {U}, SCAN-REFS finds no reference of M into g, and SCAN-QUIESCE
  establishes M-QUIESCENT apart from C's own connection. Any failure or UNKNOWN refuses.
- C8. `SPAWN_REQUEST` with the digest of C's admission summary. W answers `SPAWN_OK` only if F answered a `PING`
  within the control deadline, W's error list is empty and the attempt-journal join holds, and only after committing
  `spawn-ok.json`; otherwise W sends `STOP`. `STOP`, EOF or deadline → C refuses.
- C9. C prepares T's pre-exec: `fchdir` to the held `source` descriptor, `RLIMIT_CORE` (0, 0), umask 077,
  `PR_SET_NO_NEW_PRIVS` = 1, then the **anti-setid filter**: a classic seccomp BPF program for `AUDIT_ARCH_AARCH64`
  (any other arch: kill) that returns `EPERM` for `fchmod`, `fchmodat` and `fchmodat2` when the mode argument has any
  of the bits 06000, for `openat` and `mknodat` when the mode argument has any of those bits, returns `ENOSYS` for
  `io_uring_setup`, `io_uring_enter`, `io_uring_register` and `openat2` (a classic filter cannot inspect `openat2`'s
  mode, and a ring that another process created and passed to T would perform opens outside this filter; v4 denied
  only `io_uring_setup`, §0.5 item 5), and allows everything else; then unblock the handled signals. The filter and
  `no_new_privs` are inherited by every descendant and cannot be removed.
- C10. **Final pass** (§4.5), with the lease test and the W-CLOSED check inside the walk; then SCAN-GATE, SCAN-R and
  SCAN-W again with the child-stage point; `verify_location` of every held handle.
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
  (v5 `wait_blocked`) or, after `SPAWN_FAILED`, recorded. L sends `LAUNCHER_WAIT` and exits; W retains its wait of S2.

**C's refusals.** Every refusal by C before its spawn call (C1-C11, including C8's `STOP`, EOF or deadline and a `STOP`
pending at C11's interruption point) sends `CHILD_REFUSAL` with `child-refusal.json` (v5 keys, `target_started: false`,
v5 meaning "refused before the target spawn; nothing was started") if SP_C still works, and otherwise writes the same
statement to its stderr (`scope.stderr`, raw evidence); C then exits without spawning. C never sends `CHILD_REFUSAL`
after its spawn call; a failed spawn call that leaves no child is reported by `SPAWN_FAILED` with `child-wait.json` and
`started: false`, as v5 reported it in `child-wait.json`. **`target_started`** is therefore `true` if `child-start.json`
is committed, `false` only if C's committed `child-refusal.json` or its committed `child-wait.json` with
`started: false` exists, and `unknown` otherwise. A missing `CHILD_START` never means that no target exists, and
`unknown` never shortens a classification.

**Why a late launch after writer death is possible only through an issued, recorded permission.** No L can start SR
without `GO` (G4), which only a live W sends, and only after `PROCEED_LAUNCH` and the committed launch intent. No T
can start without `SPAWN_OK` (C8), which only a live W sends after committing `spawn-ok.json`. A sudo front-end (S2)
that outlives W can only start an L, which then reads EOF and exits. So after W's death the only possible future
target is one whose C already holds `SPAWN_OK`; that C is a GATE holder and visible to every scan until it ends, and it
either refuses before its spawn call or spawns a T that every scan then sees. Whether a launch is still pending is
concluded only from a complete classification (§9.4) in which every scan passes, never from a missing record and never
from an empty target-account or cgroup snapshot alone.

### 9.4 Scans, quiescence, lease test, write closure, known-terminal ownership and the release rule [corrections: W1-CUSTODY-CLOSURE, W1-PROTOCOL-FAILURE-STATES; v4: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE]

**Scans.** All run over the whole `/proc` of the initial pid namespace; `/proc` has no `hidepid`, and
`/proc/<pid>/{status,cmdline,cgroup}` are world-readable for every process, dumpable or not:
- `SCAN-GATE`: processes whose `Gid:` line (real, effective, saved, fs) or `Groups:` line contains GATE.
- `SCAN-R`, `SCAN-W`: processes whose `Uid:` line contains R, respectively W, in any position.
- `SCAN-NAME`: processes whose argv contains g's id as a word or the path of g, g_rec or the attempt directory (v5
  `processes_naming`).
- `SCAN-SCOPE`: U's cgroup below `user@R.service` absent, empty or holding exactly the expected processes
  (`cgroup.procs` is world-readable).
- `SCAN-UNITS` (R credentials, C or O): M's loaded units with their states, M's job queue, and the unit files in M's
  runtime unit directories (`/run/user/<R>/systemd/{transient,user,user.control,generator,generator.early,
  generator.late}`), compared with the reviewed static baseline S_units (§11.6), plus U at the child stage. The job
  queue must be empty, and every unit's state must be its baseline state. A transient scope of an earlier attempt of
  this frame (`claude-worldline-scratch-*.scope`) that is inactive or failed, with an absent or empty cgroup and no
  job, is recorded but does not fail the scan: a scope cannot be restarted and holds no process. SCAN-UNITS establishes
  Q2, Q3, Q4 and Q7 below.
- `SCAN-REFS` (R credentials): for M, `/proc/<M>/{cwd,root}`, every `/proc/<M>/fd/<n>` and every file mapping in
  `/proc/<M>/maps` is stat'ed; a `[dev, ino]` equal to any object observed in g by the same stage's walk is a reference
  into g. M is dumpable (it is `exec`ed after its credentials are set), so its `/proc` entries belong to R: observed by
  the drafting author on 2026-10-05 for `sicarii`'s own manager (`/proc/1019/fd` owned by `sicarii`, mode 0500).
  Any entry that cannot be read or stat'ed makes the scan UNKNOWN. SCAN-REFS establishes Q6.
- `SCAN-QUIESCE` (R credentials): (1) every socket in M's descriptor table is identified by inode and examined with
  `NETLINK_SOCK_DIAG` for unix sockets (`UNIX_DIAG_RQLEN`, `UNIX_DIAG_PEER`, `UNIX_DIAG_NAME`; `/usr/bin/ss -x` shows
  the same data): its receive queue, or for a listening socket its accept queue, must be empty; (2) M must hold no
  accepted connection of its private socket other than the classifying process's own; (3) every socket of M must be of
  a kind, name and peer class in the reviewed static baseline S_socks (§11.6), which by setup contains only M's own
  private and notify sockets and its journal stream; (4) after (1)-(3), (5) and (6) the classifier makes a synchronous
  call to M on the private socket (`ListUnits`, `ListJobs`), and when the answer arrives it repeats SCAN-UNITS,
  SCAN-REFS, (1)-(3), (5) and (6) and requires identical results. By premises S4 and S5 below, M sends that answer only
  after it has dispatched every event it took before the call and has processed every message it had read on any
  connection it still holds, so the repetition shows that none of them left anything behind; that nothing can arise
  later is the absorption lemma below, not this repetition. A transient difference (for example the accepted
  connection of a just-exited `systemd-run`, which M closes when it reads the end of file) is re-scanned until two
  consecutive scans agree and pass, within the stage deadline; otherwise the stage refuses (before launch) or the
  verdict is `live` (at a classification); (5) the `SigPnd` and `ShdPnd` fields of `/proc/<M>/status` and of every
  `/proc/<M>/task/<tid>/status` are zero; (6) every populated cgroup below `user@R.service` is M's own `init.scope`
  holding exactly M or, at the child stage, U holding exactly C. SCAN-QUIESCE establishes Q1 (with SCAN-R), Q5 and Q8.
- `SCAN-LEASE` (R credentials; the owner of the files): for every regular file of the partition contents observed by
  the same stage's walk, open it `O_RDONLY|O_NOFOLLOW|O_NONBLOCK|O_NOATIME|O_CLOEXEC`, require its `fstat` to equal the
  walk's `stat_key`, request a read lease (`fcntl(F_SETLEASE, F_RDLCK)`), release it (`F_UNLCK`) and close it. The
  Linux kernel refuses a read lease with `EAGAIN` while the inode is open for writing by any open file description
  (`check_conflicting_open` in `fs/locks.c`); a description counts while any descriptor, in-flight `SCM_RIGHTS`
  message, shared mapping or io_uring registration still holds it, whatever the holder's uid and whether or not its
  tables are readable. This kernel behaviour is premise L1 (§9.8 K7), not observed on this host (no section-2 manual
  is installed); probe P-QUIESCE verifies it before any reliance. A refusal, a file not owned by R (leases need
  ownership), or an `fs.leases-enable` other than 1 refuses before launch and makes a classification UNKNOWN. The
  test shows the absence of a writable description at its moment; that none can appear later is §9.8 K4's conclusion.
- `SCAN-WCLOSED` (R credentials; parent and child stages): W-CLOSED (§9.8 K2) for every entry of the partition contents
  that the same stage's walk observes; a violation, or an entry that cannot be examined, refuses before launch.
- Recorded participants: each `(pid, start_time_ticks, boot_id)` classified alive, absent, reused or unknown.

Any unreadable entry needed by a scan makes that scan UNKNOWN. There is no exception: v3's R7 is withdrawn (§2.4).

**M-QUIESCENT (the property the scans establish).** M is quiescent at a moment t iff all of these hold at t:
- Q1: every process whose `Uid:` line contains R is M or in K(P) (SCAN-R), and every populated cgroup below
  `user@R.service` is M's `init.scope` holding exactly M or, at the child stage, U holding exactly C;
- Q2: M's job queue is empty;
- Q3: every loaded unit is in its baseline state of S_units, and none is activating, deactivating, reloading,
  refreshing or waiting to restart (at the child stage, U is active and holds exactly C);
- Q4: no loaded timer, path, socket or automount unit exists beyond S_units, and S_units holds none in an active,
  waiting or listening state (§11.5 S-F masks every such unit file found at inventory time);
- Q5: every socket of M is in S_socks by kind, name and peer class, every receive and accept queue is empty, and M
  holds no accepted private-socket connection other than the classifier's own;
- Q6: M holds no reference into g;
- Q7: the unit files in M's runtime unit directories equal the baseline;
- Q8: no signal is pending for M or for any of its threads.

**Trusted-systemd premises.** They describe the installed systemd, which is part of the trusted base (§2.2); each is a
premise until the installed-evidence review (§16 step 8, a source-level reading for the installed version) and
P-QUIESCE establish it. If one fails, the absorption lemma fails with it, every classification and stage that relies
on it is UNKNOWN or refuses, and W-1 must be redesigned; no exception is taken.
- S1 (process creation): M creates a process only to execute a unit's job (a unit command, through its executor), or
  to run its generators at manager start, daemon-reload or daemon-reexec.
- S2 (job sources): M installs a job only (i) on an API request (private socket or bus), (ii) as a dependency of a job
  being installed, (iii) from a trigger unit (timer, path, socket, automount), (iv) on a unit state change
  (`OnFailure=`, `OnSuccess=`, `Restart=`, `Upholds=`, `StopWhenUnneeded=`, `BindsTo=`, `PropagatesStopTo=` and the
  like), or (v) at manager start, reload or reexec, or on a manager signal. The installed systemd(1) describes the job
  model ("these requests are encapsulated as 'jobs' and maintained in a job queue", roff line 297), activation adding
  jobs (roff line 1596) and a user manager starting `exit.target` on `SIGTERM` (roff lines 448-451) (Appendix E).
- S3 (event-driven state): M changes a unit's state only on an event: a process exit or cgroup notification of that
  unit, a timer of a unit in a transitional or restart-wait state, a trigger unit's event, a notification from that
  unit's processes, an API request, a signal, or a job it runs.
- S4 (drain and order): M completes its internal per-unit queues before it dispatches the next external event; a job
  it decides to run stays installed, and visible to `ListJobs`, until it finishes; and M sends the reply to a
  synchronous API call while dispatching that call, after the dispatch of every event it took before it.
- S5 (connections): M processes every message it has read from a connection before it closes that connection, and a
  connection M still holds is a socket in its descriptor table.
- S6 (authority): only processes of uid R or root can connect to M's private socket (systemd's peer-credential check,
  P-MGR) or signal M, and M honours notification datagrams only from processes of its own units.

**Absorption lemma.** If M-QUIESCENT holds when M answers the barrier call of SCAN-QUIESCE (4), and afterwards no
process other than root and the classifier's own frame peers communicates with M or signals it, then M-QUIESCENT still
holds at every later moment until the frame itself starts a participant that talks to M: M creates no process and
changes no unit state. From S1-S6: by Q1 no child of M exists whose exit or cgroup event could occur; by Q3 and Q4 no
unit timer or trigger can fire; by Q5 and S5 no foreign connection and no unread or unprocessed message remains; by Q8
no signal is pending; by S4 nothing deferred remains except installed jobs, and by Q2 there are none; by S6 new input
can come only from uid R or root, and by Q1 and §9.8 K3 the only uid-R processes are M and the frame's own, which send
M nothing but the classifier's read-only calls; so no event occurs in M, by S2 and S3 no job is installed and no state
changes, and by S1 no process is created. This replaces v4's inference from serialized API dispatch and two equal
snapshots (§0.5 item 2): serialized dispatch is part of S4, the equal snapshots are the observation of Q, and the
conclusion rests on the stated property and premises, not on a finite repetition.

**Why these scans and §9.8 close references and queues** (the reviewed argument; it uses no premise that any service of
the target account is benign):
- (a) *Who can change the admitted generation.* P_adm objects are W-owned and written by W only in `materialize`; the
  four partition roots are W-owned with `group:GATE:rwx`; partition contents are R-owned and, from each dispatch's
  parent stage on, W-CLOSED (§9.8 K1-K2). A mutation therefore needs W's credentials (only trusted writer code; any
  other W process is visible to SCAN-W), GATE (SCAN-GATE), uid R (every uid-R process is visible to SCAN-R, and M's
  descriptors to SCAN-REFS), an existing writable open file description of a partition file (SCAN-LEASE), or root.
  Every other process is denied each mutation when it attempts it, whatever references it holds (§9.8 K4-K5). v4's
  version of this item, which relied on partition directories staying 0700, is withdrawn (§0.5 item 1).
- (b) *What M can still do, and why a quiescent M stays quiescent.* M executes root-installed code and acts only on
  input: messages on its private socket, datagrams on its notify socket, signals, timers of its units, and unit-file
  changes that it reads only on a reload request. The private socket was observed for `sicarii`'s own manager on
  2026-10-05 as mode 0700, owned by the user, in a 0700 runtime directory, and systemd's private API accepts only peers
  whose credentials are root or the manager's own uid (S6; P-MGR verifies both for R); notify datagrams are honoured
  only from processes of M's own units (S6). Every timer, path, socket, automount and other process-starting unit file
  found at inventory time is masked (§11.5 S-F), so S_units holds no trigger in an active, waiting or listening state
  (Q4). From M-QUIESCENT the absorption lemma shows that M has no pending input and creates nothing. New input could
  come only from a new uid-R or GATE process, which only the frame's own sudo rule can start (while the lease holder
  runs, §5.2), or from root; §9.8 K3 closes the set-ID routes to uid R and GATE. So a quiescent state is absorbing: it
  lasts until the frame itself starts a participant, whose own stage scans then apply.
- (c) *Descriptor queues and retained references.* A writable description in flight anywhere is caught by SCAN-LEASE,
  because it keeps the description open (premise L1). Any other reference in flight or retained (a read-only, `O_PATH`
  or directory descriptor, a current directory) lets its eventual holder do only what that holder's own credentials
  allow when it acts (§9.8 K5): nothing that changes the generation unless the holder is uid R, GATE or root, which (a)
  enumerates. A connection handle to M that a target passed to another process shows as a foreign accepted connection
  in M's table (Q5) and holds.
- (d) *What remains outside*: root and the kernel (R8); a writer instance running changed code (outside the threat
  model, as before); availability (R6).

**Classification points.** K(P) is the set of known triples of the frame's own processes running at point P. A scan
passes at P if every process it reports is in K(P) (for SCAN-R, K(P) plus M), SCAN-SCOPE and SCAN-UNITS show what the
table says, and SCAN-REFS, SCAN-QUIESCE, SCAN-LEASE and, where the table requires it, SCAN-WCLOSED pass. K(P) includes
the sudo processes the serving writer started, so it does not matter in which credential sets the kernel shows sudo's
monitoring process (P-LAUNCH records it).

| Point P | Classifier | K(P) | SCAN-SCOPE | SCAN-UNITS | Also required |
|---|---|---|---|---|---|
| parent stage (D8) | O, for W | F, S1, W, S_O, O | U absent | S_units | SCAN-GATE = {O}; phase `pre` scans before the write revocation (§9.8 K1); SCAN-WCLOSED and SCAN-LEASE in the walk after it; phase `post` scans after the walk |
| child stage (C7, C10) | C | F, S1, W, S2, L, C | U holds exactly C | S_units ∪ {U} | SCAN-GATE = {L, C}; SCAN-WCLOSED and SCAN-LEASE inside the final pass |
| after stage (D17) | O, for W | F, S1, W, S_O, O | U absent or empty | S_units | SCAN-GATE = {O}; every launch participant absent or reused |
| recovery round (§9.7) | O, for W2 | F, S3, W2, S_O, O | U absent or empty | S_units | SCAN-GATE = {O}; every launch participant absent or reused |
| release (D18, RC4) | F under the window lock, world-readable scans only | F, S1 or S3, the serving writer | U absent or empty | not taken (supplied by the after stage or the recovery round) | SCAN-GATE = ∅ (the classifying O has ended) |

**Known-terminal ownership** of attempt A holds when the after-stage classification or the latest recovery round
passes completely (every scan within its point, none UNKNOWN, every recorded launch participant absent or reused). It
is never established from F's scans alone, from a missing record, or from an empty target-account or cgroup snapshot
alone.

**Release rule** (only F; v5's "only the launching parent releases" is kept, because F is the reserving process). F
releases if and only if both hold under the window lock:
1. `owns_window(holder, candidate, token)` (v5, unchanged: status reserved, holder, candidate, token);
2. known-terminal ownership of A has been established by W's after-stage classification or, after W's death or
   channel failure, by W2's recovery (§9.7), and F's own world-readable scans, taken under the window lock immediately
   before the window write, pass at the release point.
Nothing else is a condition. In particular the durability of a record (`release-intent.json`, `window-release.json`,
the conclusion, the scans' own records) is not.

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

### 9.5 Failure table [corrections: W1-PROTOCOL-FAILURE-STATES, W1-CUSTODY-CLOSURE, W1-JOURNAL-CONTINUATION, W1-SETUP-IDENTITY, W1-IMAGE-OBSERVATION]

| Event | Behaviour |
|---|---|
| Lease held | W refuses before any mutation and before starting any helper: `EARLY_REFUSAL` (stage `lease`) on its channel and the facts on its stderr; it exits non-zero. F has reserved nothing (reservation is D12). For W2, F retries after its fixed interval (§9.7) |
| A pre-hello check fails, or a record that must precede `W_HELLO` (`generation.json`, `attempt.json`, `fallback-allocation.json`, `invocation.json`) cannot be committed as primary or retry | W refuses before any reservation with `EARLY_REFUSAL`, which lists what it committed; it commits `refusal.json` and an export increment only if `attempt.json` is committed, and F then runs W2 in mode `seal`; otherwise F's terminal facts stay on its console, because without a committed `attempt.json` no W2 can verify its capability |
| `setup-identities.json` does not match its seal (§11.7) | refuse before any mutation: `EARLY_REFUSAL` (`dispatch`; `materialize` when an adoption record exists; `seal-front`); `REFUSAL` at `COMMIT` (`adopt`), before `lead-adoption.json` is written |
| F's identity fails §8.1's joins at `HELLO_ACK` | `REFUSAL` (`adopt`, `materialize`, `seal-front`: then `EXPORT`; `dispatch`: RP0) |
| A pinned input fails its pin or verification | `REFUSAL` in place of `PHASE_DONE` (`materialize`, `dispatch`: RP0; nothing of that input is written), or at `COMMIT` (`adopt`) |
| F's front-parent half fails; dispatch's vault pin or status fails (J9) | `REFUSAL`, RP0 |
| The vault stage of `materialize` fails | recorded and reported (`FINAL.vault`); neither a refusal nor a success condition (§10.7) |
| sudo refuses, account locked, rule missing (each invoke) | F observes S1's exit before any reservation; nothing to release. A setup selftest never stands in for this |
| Channel failure, deadline or refusal before D12 | W: `refusal.json` ("refused before reservation and launch; nothing was started") when `attempt.json` is committed; F: no reservation; F runs W2 in mode `seal` if it knows that `attempt.json` is committed (from `W_HELLO` or `EARLY_REFUSAL`) |
| `reservation-intent.json` cannot be committed | F does not write the window (`RESERVE_ABORT`); nothing reserved; W: `refusal.json` |
| `reservation.json` cannot be committed | the reservation exists; durability-UNKNOWN for that record; W refuses before launch, concludes with the after-stage classification, and F releases by §9.4 |
| W dies or its channel fails after F's window write and before `PROCEED_LAUNCH` | W never started S2, but this is not inferred from missing records: F runs recovery (§9.7); release only on known-terminal ownership |
| W dies or its channel fails after `PROCEED_LAUNCH` | a launch may exist; recovery (§9.7) classifies until known-terminal or unknown; release by §9.4; otherwise hold |
| F dies after its window write | W: before launch, refuses and concludes; after launch, keeps waiting and concludes. W cannot release (F alone can): `release-withheld.json` ("front absent"); manual resolution. A front EOF never implies a refusal after launch |
| `RL_IDENTITY` missing or second (Option B), or failing W's verification | missing or second: a channel failure, and W sends no `GO` or `OBSERVE_REQUEST`, so the helper reaches its deadline and exits 125 having started nothing; failing: W sends `STOP` (L) or `O_BYE` (O). Before launch the stage refuses; at a classification the observation fails (§9.4) |
| L dies before `GO` / after | before: L started nothing; after: SR/C may exist; the classification decides |
| L reads a `STOP` at its interruption point, or its spawn call fails and no child exists | `L_REFUSAL`; L exits 125 having spawned nothing |
| C refuses before its spawn call (C1-C11, including a `STOP` pending at C11) | C's `child-refusal.json` (C's own pre-spawn statement), committed by W; `target_started: false`; classification still by complete scans |
| C's spawn call fails and no child exists | `SPAWN_FAILED`; `child-wait.json` with `started: false`, committed by W; `target_started: false`; classification still by complete scans |
| C dies or SP_C fails without either record, or C's spawn call fails while a child exists | `target_started: unknown`; never inferred from a missing `CHILD_START`; the classification decides |
| T exits | C's `child-wait.json`, L's and W's waits, O's after stage, conclusion |
| O fails | before launch: the stage refuses; after launch: no complete classification, so hold until a later O under a live W or a W2 succeeds; W never releases on its own |
| The write revocation cannot complete (an entry not owned by R, a symlink or special file, a set-ID or multiply linked file, another `st_dev`, a changed entry set, a `fchmodat2` error or an unexpected `fstat` after it) | refuse before launch (nothing reserved); `write-revocation-<n>.json` records every change made and why it stopped |
| SCAN-WCLOSED fails at the parent or child stage | refuse before launch |
| SCAN-LEASE refuses at the parent or child stage | refuse before launch: an admitted file has a writable description somewhere |
| SCAN-QUIESCE or SCAN-UNITS shows a foreign unit, job, trigger, connection, queued input, pending signal or populated cgroup | before launch: refuse; at a classification: verdict `live` while it persists, `unknown` if unreadable |
| `RELEASE_INTENT_RESULT` not received within the control deadline | F writes the window anyway and sends `RELEASE_DONE`; durability-UNKNOWN unless the intent record is committed; a later result is recorded and changes nothing |
| No `RELEASE_RECORD_RESULT` within the control deadline after `RELEASE_DONE` | channel failure after F's window write: writer-death recovery (§9.7), whose `RELEASE` state finds the window not held (`RELEASE_NOT_OWNER`) |
| A marker fails and its continuation fails too (§10.2 J4) | the writer writes no further marker in that journal; later records go to the fallback journal (durability-UNKNOWN for `adopt`, which has none); success withheld; no release effect |
| A journal is branched (§10.2) | the writer writes no marker in it; its records go to the fallback journal or are durability-UNKNOWN; success withheld; no release effect |
| Records exhaustion | §10: success withheld; release by §9.4 only |
| A stream file not final (W's stream lease test, §10.6) | success withheld; no release effect |
| An export increment fails | `EXPORTED` with state `failed`; success withheld; no release effect |
| M unavailable | L refuses before systemd-run (C never exists) |
| Window not owned at release | `NotOwner`, nothing released (v5) |
| Window write error at release | §9.4, window write failure |
| The images directory, a backing image file or a mount check fails (§3.4) | W, W2: refuse before any mutation; O, C: the stage refuses |
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
  owner, mode and ACL; the loop device number and mount ID are re-observed, not compared), the target home and its
  masks, the user-manager drop-in and the installed frame; it refuses otherwise. A missing image mount leaves the bare
  root-owned mount point, which W can neither write nor mistake (§3.4).
- Journals are interpreted, never repaired: each journal's committed chain is recomputed (§10.2), and a torn marker
  or torn fallback slot left by the interrupted boot is raw evidence, never reused (§10.2, §10.4).
- M restarts with the boot. The first parent-stage classification of the new boot compares M's units and sockets with
  S_units and S_socks by kind, name and peer class (socket inode numbers are boot-local and are not compared, §11.7).
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
  may serve several rounds) to take the complete classification of §9.4 at the recovery point: every scan, and the
  triples of every participant named by A's committed records or seen by a scan. The verdict is `known-terminal`
  (everything passes), `live` (some participant, unit, job, connection, queue, reference or writable description is
  still present: W2 waits a fixed round interval of 10 s, a judgment, and repeats) or `unknown` (an unreadable entry,
  an O that cannot run or answer, an unresolved participant record: the rounds end). W2 commits
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
missing, and `target_started` follows §9.3 (C's refusals). The classification always takes the complete scans.

**Authority.** W2 uses only the reviewed rules: S3 is the `sicarii`→`wlscratch` writer rule, and W2's S_O uses the
`wlscratch`→`wlscratch-run:wlscratch-gate` launcher rule exactly as W's observers do, with `recover` as O's stage. W2
writes only inside `w2-<k>/`, A's attempt journal and A's export increments (§5.2). F alone releases. If W2 or O cannot
run (a sudo refusal, a lease that never becomes free, a refusing O), no complete classification exists, and the window
is held (§9.4).

**When F does not run recovery.** If F never wrote the window (a refusal before D12, or `RESERVE_ABORT`), there is
nothing to release; F still runs W2 in mode `seal` if `attempt.json` is committed (otherwise F's terminal facts stay on
its console). If F dies, nobody releases: the window is held for manual resolution (§9.5), as in v3.

### 9.8 Custody closure of the partition contents [correction: W1-CUSTODY-CLOSURE]

v4 concluded that a retained directory reference lets a process without uid R or GATE do nothing, because every
partition directory stays 0700 (v4 §9.4 (a), §2.4 R9, §4.5 (i)). The target owns those directories and may change
their modes and ACLs (§2.1 A2), so that invariant was never enforced; and a momentary lease test does not exclude a
later write open (review R1). v5 replaces the argument by a mechanism. Before any custody conclusion, every write
permission that a non-owner holds on the partition contents is removed (K1) and shown absent (K2); the set of
processes that can hold the owner's credentials is closed (K3); custody then follows from the checks the kernel makes
at the moment of each operation (K4), whatever references exist (K5). Nothing the target may do is refused or changed
(K6). The premises are in K7.

**K1. Write revocation (O, at each dispatch's parent stage, before its walk).**
1. *Preconditions*, from O's first parent-stage scans (§4.2 D8, phase `pre`): SCAN-GATE = {O}; every uid-R process is
   in K(P) or is M; SCAN-W within K(P); SCAN-UNITS and SCAN-QUIESCE establish M-QUIESCENT (§9.4). Otherwise the stage
   refuses before any revocation.
2. *Traversal.* O opens each of the four partition roots by an anchored chain from `A_T`, each equal to the identity
   `materialization.json` records for it, and visits the partition contents in pre-order. For each directory D it holds
   (a root, or a content directory already revoked), it lists D (`getdents` on D's descriptor) and, for each name in
   sorted order: calls `fstatat(D, name, AT_SYMLINK_NOFOLLOW)`; refuses the stage if the entry is not owned by R, is
   neither a regular file nor a directory, has a set-user-ID or set-group-ID bit, is a regular file with more than one
   link, or is a directory with another `st_dev` than its root; opens it with `O_PATH|O_NOFOLLOW|O_CLOEXEC` (a
   directory also with `O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`, for its listing) and requires `fstat` of the held
   descriptor to equal the `fstatat` result; and, if the mode has a group-class or other-class write bit
   (`st_mode & 0o022`), calls `fchmodat2(fd, "", st_mode & 0o7777 & ~0o022, AT_EMPTY_PATH)` and requires a following
   `fstat` to show exactly that mode, the same `[dev, ino]`, owner R and, for a file, one link. A directory is thus
   revoked when it is found, before its own entries are listed.
3. *Stability.* After processing the entries of D, O lists D again and requires the same entry set; a difference
   refuses the stage.
4. *Record.* Every change goes into `write-revocation-<n>.json` (path, `[dev, ino]`, type, mode and link count before
   and after), with the reason if the stage refused; O sends it with its observation and W commits it (§4.3).
5. *Containment.* O changes only the group-class and other-class write bits of the mode of inodes owned by R that it
   holds through descriptors anchored in T: no content, name, owner, group, ACL entry other than the mask that `chmod`
   rewrites (acl(5), as §6.2 uses it), default ACL, extended attribute or time except the ctime the kernel sets.
   Because a non-owner without `CAP_FOWNER` cannot change a mode, O cannot affect an inode of any other owner, wherever
   it is named. Each directory is write-closed when it is found, before its entries are examined, so during the pass
   no process other than uid-R processes, GATE holders and root can add, remove or move entries in it, and at the
   parent stage those are O and the quiescent M only (precondition 1, K3). A regular file can gain a second name
   concurrently only through write access that the target itself granted to another process, before O's
   `fchmodat2` reached it; the following `fstat` then shows a second link, the stage refuses, and the record names the
   inode, whose only change was the removal of that granted write access.

**K2. W-CLOSED.** An entry of the partition contents is W-CLOSED iff (c1) its owner is R; (c2) it is a regular file or
a directory; (c3) `st_mode & 0o022` is 0, so neither the group class nor the other class has write permission (with an
extended ACL the group-class bits are the ACL mask, so no named-user, named-group or owning-group entry has effective
write permission); (c4) `st_mode & 0o6000` is 0; (c5) a regular file has one link; and a directory has its partition
root's `st_dev`. (c2), (c4) and (c5) are the walks' existing rules (§6.5); (c1) extends to every entry the ownership
that v4's lease test already required of every regular file; (c3) is new. O's parent-stage walk checks W-CLOSED after
K1 (SCAN-WCLOSED), and C's final pass checks it in the same walk (§4.5). Any violation, or an entry that cannot be
examined, refuses the launch.

**K3. Credential closure.** A process can hold uid R or GATE only through the routes of §5.3. v5 keeps every route
closed:
- sudo: only W can start L, C or O with R and GATE, and only through the reviewed rules (Option B: through RL);
- M holds R without GATE; every process M starts descends from M and inherits `no_new_privs` and the S-F seccomp
  filter (§11.5), which no process can remove;
- set-user-ID and set-group-ID files of R or GATE: none exists after setup (S-I compares `find / -xdev -perm /6000` with
  P17 and scans ownership), and none can be minted afterwards: T's tree runs under C9's filter (§9.3), M's tree under
  the S-F filter, and the frame's own L, C and O never set those bits;
- group passwords: the `gshadow` entries of GATE and of the two user-private groups have no members and a locked
  password (§11.2, S-I);
- user namespaces: no new identity lies in a subordinate range (§5.4), so no other user can map R or GATE;
- root: the trusted base (§2.2).
So at every moment the processes holding uid R or GATE in any credential field are frame participants started through
the reviewed rules, T's process tree, and M with its descendants, and each of them is seen by SCAN-R or SCAN-GATE.

**K4. Custody from the final pass to `exec`.** Suppose that at C's final pass (C10) every partition entry is W-CLOSED
(K2); no writable open description of an admitted partition file exists anywhere (SCAN-LEASE, premise L1); the uid-R
processes are within {L, C, M} and the GATE holders are exactly L and C (C7, C10); and M is M-QUIESCENT (C7, §9.4). Then
until T's `exec` no process other than L, C and root changes the admitted generation:
1. changing a file's content needs a writable open description; none exists, and a new one needs write permission at
   `open` time, which W-CLOSED denies to every process whose fsuid is not R (the owner class does not apply to it, and
   neither the group class, nor an ACL entry, nor the other class carries write permission);
2. creating, linking, unlinking or renaming an entry, and making or removing a directory, need write permission on the
   directory concerned, which is denied in the same way; a partition root additionally needs W or GATE;
3. `chmod`, `chown`, ACL changes, inode flags and explicit times need the owner's fsuid or `CAP_FOWNER`; setting times
   to now and `user.*` extended attributes need write permission; other attribute namespaces need `CAP_SYS_ADMIN`; a
   hard link to the file from anywhere needs ownership or read and write permission (`fs.protected_hardlinks=1`);
4. by K3, the only processes with fsuid R are L, C and M, and no new one can appear except through the frame's own
   sudo rule;
5. M creates no process and changes no unit while quiescent (absorption lemma, §9.4).
P_adm objects are W-owned and unchanged since M8 (§4.5 (ii)). Hence the admitted generation is unchanged at `exec`,
except through root, which is the trusted base.

**K5. Retained, queued and unobservable references.** K4 assumes nothing about which processes hold which
references. A read-only, `O_PATH` or directory descriptor, a current or root directory, a descriptor queued in a socket
or held by a non-dumpable process, and a `/proc/<pid>/fd` link each let their holder do only what the holder's own
credentials allow when it acts, because every operation of K4 1-3 is checked at that moment against the inode's
current mode, ACL and owner. Re-opening through `/proc/self/fd`, `openat` relative to a held directory and `linkat`
from a held descriptor are path operations with the same checks (premise K-PERM). A writable open description is the
only reference that carries write access by itself, and premise L1 makes every one of them visible to SCAN-LEASE. This
replaces v4's "a directory descriptor permits a mutation only to a uid-R or GATE process".

**K6. Preservation.** No target action is refused or changed. A target runs as R, and the owner class governs its
access to everything it created, so clearing group-class and other-class write bits changes nothing the target itself
can do. The target may still `chmod` and set ACLs, default ACLs included, which affect only entries created later and
which the next parent stage revokes again. O narrows the write permission of non-owners only, never read or search
permission, owner bits, ownership, names or content, and records every change with the mode the target left, so the
target's own result stays evidence. An entry owned by another uid, which only a process the target had given write
access could create, refuses the next launch, as v4's lease test already refused a regular file not owned by R: this is
a refused launch, never a narrowed acceptance. The recipe, the partition roots, the allowlist, the caps and every
original gate are unchanged. The revocation is a frame mutation inside T and is reported as one (§4.1); it is never
relabelled as target residual.

**K7. Premises, probes and consequences.** None is observed on this host yet. Each keeps its probe; if one fails, the
conclusion that rests on it is lost, the affected stage refuses or the classification is UNKNOWN, and W-1 must be
redesigned. No exception is taken, and no finite probe stands in for a premise: a probe can only refute one.

| Premise | Content | Probe or evidence | If it fails |
|---|---|---|---|
| L1 | a read lease is refused while any writable open description of the inode exists anywhere: in a descriptor table, an in-flight `SCM_RIGHTS` message, a shared writable mapping or an io_uring registration | P-QUIESCE (d)-(f) (§13) | redesign |
| K-PERM | the permission and ownership checks of K4 1-3 and K5, including `chmod`'s ACL-mask rule and `fs.protected_hardlinks=1`, hold on the installed kernel and filesystems | P-WCLOSED (§13.1) | redesign |
| K-CHMOD | `fchmodat2(fd, "", mode, AT_EMPTY_PATH)` on an `O_PATH` descriptor changes exactly the held inode's mode | P-WCLOSED | redesign of K1's primitive |
| H1 | C9's filter, with the io_uring additions, denies every listed set-ID request and system call to T's tree | P-SETID (A2 rows, §13 and §13.1) | redesign |
| H2 | the S-F drop-in's `NoNewPrivileges=`, `RestrictSUIDSGID=`, `SystemCallArchitectures=` and `SystemCallFilter=` take effect for M and for every process M starts on this aarch64 host, and M works with them | P-MGR, P-SETID (A3 rows, §13.1) | redesign |
| H3 | no other interface lets a uid-R process create a set-ID file of R or GATE, or a file capability effective in the initial user namespace | a review of both filter lists against the installed kernel's system-call table; P-SETID | redesign |
| S1-S6 | the trusted-systemd premises of §9.4 | the installed-version source reading (§16 step 8); P-QUIESCE (a)-(c) and (g)-(k) | redesign |
| M-PAM | M starts, delegates and gets its runtime directory without PAM (v4) | P-MGR | redesign |
| BUS | no allowlisted action needs the session bus (v4) | first engineering run | redesign |
| ROOTS | no allowlisted action removes or renames a partition root (v4 §6.4) | first engineering run | redesign |
| OPT-B | Option B's namespace, exposure and root-launcher behaviour (v4 §12.2) | Option B's probes in the concrete setup package | Option B redesigned, or not used |
| ENOSPC | fallback slot writes succeed when allocation fails (v4 §10.4) | P-ENOSPC | no durability claim under allocation failure (v4) |
| IMG | image geometry and `noexec`/native compatibility (v4 §14.5) | measurement on a sacrificial image | requirements stay; execution controls keep a separate compatible admitted frame; nothing is narrowed |
| LOOKUP | W can `fstatat` through a search-only `O_PATH` directory descriptor, and reading `lost+found`'s access ACL needs no read permission on it | P-IMAGE (§13.1) | redesign of the image branch |

## 10. Commits, journals, retries, durable fallback and durability-UNKNOWN [corrections: W1-COMMIT-JOURNAL-EXPORT, W1-DURABILITY-RELEASE; gap: commits-and-durable-channel]

### 10.1 Commit primitive (N11)

`commit(dir, name, value)`:
1. v5 `write_json` bytes (`json.dumps(value, indent=2, sort_keys=True, default=str)` plus a newline, with v5's
   `label`) written by v5 `write_bytes(name, bytes, 0600)`: `O_CREAT|O_EXCL|O_NOFOLLOW`, write, `fchmod`, `fsync` of
   file, `fsync` of directory, entry join (the name names the written single-link inode of the written size),
   `verify_location`. Raw byte records (copies, input bytes, the report) use `write_bytes` directly.
2. Post-validation: re-read through `read_observed` and require equal sha256, size, mode 0600, one link and no ACL.
3. Marker: the same primitive and post-validation for the next marker of the record's journal (§10.2).

Export copies are committed by the export primitive of §15.3 instead, whose final mode is 0640 with the export ACL.

**A record is committed exactly when its marker is committed.** A record whose bytes exist but whose marker does not
(failed `fsync`, failed post-validation, failed marker) is "written, uncommitted": retained as raw evidence, reported,
and never parsed as valid input (v5 `retain` already never reused a partial primary).

### 10.2 Markers, journals and the committed chain [correction: W1-JOURNAL-CONTINUATION]

v4's rule let a torn or unlinked marker end the committed chain while a later writer skipped its seq and linked to the
previous head (review R3). v5 has one rule, the same for every reader and writer, with no case in which a marker both
ends the chain and is bypassed by a successor treated as committed.

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
- **Successor candidates.** For a valid marker H with seq s and digest d: a *normal candidate* is a valid marker of a
  record-bearing kind or of kind `close` with seq s+1 and `prev_commit` d; a *continuation candidate* is a valid marker
  of kind `continuation` with `prev_commit` d and seq t ≥ s+2 whose `skipped` names exactly the seqs s+1, …, t−1 and,
  for each of them, exactly the files of `commits/` that carry that seq, with the sha256 and size of their current
  bytes. *Genesis candidates* are defined the same way with `prev_commit` `null`: a normal genesis has seq 0, and a
  continuation genesis with seq t skips exactly 0, …, t−1.
- **The chain.**
  1. If there is exactly one continuation candidate, it is the successor, and every marker at a seq it skips is RAW,
     valid or not. Otherwise, if there is exactly one normal candidate, it is the successor. Otherwise, if there is no
     candidate, the chain ends. Otherwise (two or more continuation candidates, or two or more normal candidates and no
     continuation candidate) the journal is **branched** there and the chain ends.
  2. Starting from the genesis, this gives the chain E_0, …, E_k (empty if there is no genesis or the genesis is
     branched). The **head** is E_k, or none.
  3. A record is **committed** iff its marker is a chain element E_i with i < k: a later chain marker confirms it. A
     record-bearing head is unconfirmed, and its record is not committed.
  4. Every file of `commits/` that is not a chain element is RAW, and so is every record file whose marker is not a
     confirmed chain element. RAW files are retained and listed by exports (§15.3); they are never parsed as valid
     input and never get success credit.
  A torn or unlinked marker therefore ends the chain only while no continuation lists it, and once one does it is RAW
  and outside the chain; nothing it carries is ever committed.
- **Commit primitive (completing §10.1's step 3).** A record is committed by three create-only writes: the record
  (§10.1 steps 1-2), its record-bearing marker M (linked to the head as J2-J4 below require), and a `close` marker
  with `prev_commit` = M's digest and the next seq. A marker is fully written when its create, write,
  file `fsync`, directory `fsync`, post-validation and entry join all succeed. Wherever this document says that a record
  and its marker are committed, or that a journal or a prefix ends at, or is cut at, a record's marker, it means this
  primitive and the close marker that confirms that marker. Between commits the head is therefore always record-free.
- **Writer rules** (only the lease holder writes; a W2 only after W has exited):
  - J1 (open). The writer computes the chain. If the journal is branched, it writes no marker in it: every record it
    would commit there goes to the fallback journal (state `fallback`) or, without one (`adopt`), is
    durability-UNKNOWN, and the branch is an error in every later record and in `FINAL`. Otherwise its *base* is the
    head if the head is record-free, else the head's predecessor (an unconfirmed record-bearing head is skipped, never
    confirmed by a writer that did not write it), or none if there is no such marker.
  - J2 (seq). The next seq is one more than the largest seq of any file of `commits/` whose name has the marker form,
    valid or not, and larger than every seq this writer has attempted. No seq is reused, and no file is ever
    overwritten or removed.
  - J3 (linking). A writer links a normal marker only to a marker it has itself fully written in this invocation, or to
    its record-free base. Its first marker is a normal marker linking to the base when the base is the head and the
    next seq is the base's seq + 1; otherwise it is a continuation linking to the base (a genesis continuation if the
    base is none) that lists every seq from the base's seq + 1, or from 0, to its own seq − 1.
  - J4 (failure). If any step of writing a marker fails, the writer's next marker in that journal is a continuation that
    links to the last marker it fully wrote (or to its base) and lists every seq above that one up to its own seq − 1,
    so the failed marker is RAW and its record is not committed; the record then follows §10.3 (retry, then fallback).
    If that continuation also fails, the writer writes no further marker in that journal for the rest of its
    invocation: its later records go to the fallback journal or are durability-UNKNOWN, and a record whose
    confirmation is now impossible is not committed.
  - J5 (one truth). Every record state the writer reports (`RECORD_COMMITTED`, `W_HELLO.committed`, `record_states`,
    `FINAL`) is the state the chain rule gives for the files present after its own writes. It sends `RECORD_COMMITTED`
    for a record only after the marker that confirms it is fully written, and it never reports, records or relies on a
    belief that the rule contradicts.
- **First-marker failure.** If the first record-bearing marker of a journal fails, J4's continuation is a genesis
  continuation; if that fails too, the journal has no chain and nothing in it is committed. For a record that must
  precede `W_HELLO` (`generation.json`, `attempt.json`, `invocation.json`, `fallback-allocation.json`) this is §9.5's
  refusal before any reservation (`EARLY_REFUSAL`); without a committed `attempt.json` no W2 can run (§9.7).
- **Gaps.** A seq at which no file exists (a create that failed before any file appeared) is listed by the next
  continuation with an empty `files` list.
- **Every consumer, every time.** The rule is a function of the files present: W's attempt-journal join, W2, the
  conclusion, the exports, a reviewer reading an export, and a writer or reader after a reboot all obtain the same
  chain, head, branches and committed set from the same files (§9.6: interpreted, never repaired). Files lost or torn
  by a crash change the answer only by making later markers RAW or a record uncommitted; such an attempt is
  non-success by §9.6 in any case.
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
committed only to a fallback slot is `fallback`: it earns no success credit either. F prints every `RECORD_UNKNOWN` and
`RECORD_FALLBACK` to its console; that output reaches the lead's tool output and transcript, written by the harness,
not by the frame, and is not durable if F dies or the transcript filesystem fills. Effect: no success or acceptance
credit, and the uncertainty is preserved and reported; no hold, no effect on the window and no approval gate (§9.4).

### 10.6 Consumers (complete)

**Precedence for every record name N:** the committed primary; else the committed retry (with its downgrade); else a
VALID fallback slot naming N (state `fallback`: never success credit; a truncated payload gives only digest and size);
else raw uncommitted bytes of N (state `raw`: evidence only, never parsed as valid input); else `unknown`. TORN slots
name nothing.

| Consumer | What it uses | Rule |
|---|---|---|
| C | record bytes W delivers over SP_C | only committed primary or retry records; their sha256 must equal W's in-memory descriptors and the seals; fallback and raw bytes are never delivered |
| W's attempt-journal join (D8, C4, C8, the conclusion) | every record of the attempt | each committed record still has its committed sha256, size, mode, single link and ACL state (export copies: their final export values); `fallback.journal` has the identity and size of `fallback-allocation.json`, every slot below the in-memory next index is byte-identical to what this writer last read or wrote (after a failed slot write it reads the slot back), and every slot at or above it is EMPTY; no content digest of the journal is ever compared; the journal's committed chain is unchanged up to the in-memory head |
| F | descriptors from `*_COMMITTED`, `RECORD_FALLBACK`, `RECORD_UNKNOWN`, `EXPORTED` | in memory; export copies re-read and compared with their final values (§15.3) |
| The conclusion, `result.json`, `final-status.json` | every expected record | `record_states` maps each name to `primary`, `retry`, `fallback`, `raw` or `unknown`; success needs every required record `primary` or `retry` |
| The classification (N12) | participant records | exact schema validation (Appendix B.2); only committed records are participant evidence; a fallback, raw or missing participant record removes no participant (participants are classified by the scans, §9.4); a parseable record with a missing or mistyped field is unresolved and makes its participant UNKNOWN |
| W2 | A's journal and records | the committed chain only (§10.2); slots by this section's interpretation |
| Exports and reviewers | export increments | §15.3: committed records copied; fallback slots decoded or listed; raw records listed by digest |
| A writer after a reboot | earlier attempts | interpretation only (§9.6); never an admission input |

- **Stream finality.** After every launch participant's wait is recorded and before `result.json`, W closes its own
  copies of the stream descriptors, syncs the stream files, and applies the lease test of §9.4 to each (W owns them).
  A refusal means a writable description of the stream still exists outside W (for example one the target passed to
  another process): `stream-finality.json` records it, the streams are not final and success is withheld, with no
  effect on release.
- **Error joins.** Every `record_errors` list, `*-failure.json`, `conclude-errors.json`, channel failures,
  durability-UNKNOWN and fallback entries, TORN slots and raw records are joined into the conclusion,
  `final-status.json` and the front terminal record.

### 10.7 Exit statuses and success, per verb (N13, N14) [correction: W1-PROTOCOL-FAILURE-STATES]

- **W, `dispatch` (N13).** `success` = v5's conjunction (launched, scope wait 0, child wait 0 and clean, no error,
  post-identity clean, materialization unchanged, owned terminal) ∧ every required record `primary` or `retry` ∧ no
  `fallback`, `raw` or `unknown` record ∧ the attempt journal not branched ∧ streams final ∧ released (F reported
  `RELEASE_DONE` with a re-read showing the release) ∧ the release records committed ∧ export increment 0 frozen.
  Errors appended after `result.json`, including late handle-close and export errors, force `success = false`, are
  committed as `conclude-errors.json` (or to the fallback journal), and make W exit 1. `final-status.json` records the
  final values.
- **W, `materialize`.** `success` = `materialization.json` committed after M8's verification ∧ `verify_materialization`
  against it passed ∧ the generation export frozen (M9) ∧ A0's export increment 0 frozen ∧ every required record of the
  generation journal and of A0's attempt journal `primary` or `retry`, none `fallback`, `raw` or `unknown`, neither
  journal branched ∧ no `EARLY_REFUSAL` or `REFUSAL` ∧ no error. The vault stage's outcome (M10) is recorded and
  reported in `FINAL.vault` and is not a condition: v5 `materialize` ran no vault command (Appendix E), while
  `dispatch` keeps v5's vault requirement (J9, `run` S:1562-1563).
- **W, `adopt`.** `success` = `lead-adoption.json` committed and `ADOPTED` sent ∧ the adoption export increment frozen
  ∧ every record of the invocation `primary` or `retry` (adopt has no fallback journal, so a record that is not
  committed is `unknown`) ∧ the adoption journal not branched ∧ no error.
- **W2, mode `seal`.** `success` = `w2-<k>/identity.json` and `front-terminal.json` committed ∧ its export increment
  frozen ∧ every W2 record `primary` or `retry` ∧ no error.
- **W2, mode `recover`.** The `seal` conjunction ∧ the recovery verdict `known-terminal` ∧ the window released for this
  attempt (by F in this W2's `RELEASE` state, or earlier in the attempt, as F's terminal record states) ∧ the release
  record of this W2's `RELEASE` state committed.
- Each writer exits 0 iff its `success` holds, 1 otherwise, and 125 only on a first-act failure (§7.7).
- **F (N14).** `dispatch`: exit 0 only if W's `FINAL` reports success and release, F's own error list is empty, no
  interrupt reached F, S1's raw status is 0, W2 (mode `seal`) reported success and S3's raw status is 0, and nothing is
  `fallback` or durability-UNKNOWN; a run that needed recovery exits 1 even if it released. `materialize`: exit 0 only
  if W's `FINAL` reports success, S1's raw status is 0, W2 (mode `seal`) reported success and S3's raw status is 0,
  F's own error list is empty, no interrupt reached F, and nothing is `fallback` or durability-UNKNOWN. `adopt`: exit 0
  only if W reported `ADOPTED`, `EXPORTED` with state `frozen` and a successful `FINAL`, S1's raw status is 0, F's own
  error list is empty and no interrupt reached F (no W2 runs for `adopt`).
- **C, L, O.** C keeps v5's rule (`code` if it is not `None` and there were no failure, notes or errors, else `code or
  1`); L exits 0 only if its scope wait is 0 and it had no error, and 125 when it spawned nothing (EOF, deadline or
  `STOP` before its spawn call, or a failed spawn call with no child); O exits 0 only if its observation succeeded.
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
- **Symlinks:** none anywhere in an installed or setup tree, except the reviewed mask links (root-owned, target
  `/dev/null`, exact names).
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
- If probe P-MGR shows that a system-range uid cannot host a lingering manager with cpu, memory and pids delegation,
  the concrete inventory moves R to a regular uid and removes any subordinate range `useradd` allocates
  (`usermod --del-subuids/--del-subgids`), re-reviewed. (The existing lingering accounts here have regular uids 1001,
  1002 and 1004.)

### 11.3 Prestate inventory (read-only; "lead" = unprivileged agent, "operator" = needs root)

| Id | Check | Runner | Required |
|---|---|---|---|
| P1 | `getent passwd wlscratch`, `getent passwd wlscratch-run`, `getent group wlscratch`, `getent group wlscratch-run`, `getent group wlscratch-gate` | lead | each exits 2 |
| P2 | `getent passwd <n>`, `getent group <n>` for every candidate | lead | each exits 2 |
| P3 | contents, digests and `lstat` of `/etc/subuid`, `/etc/subgid` | lead | every candidate outside every range; files root:root 0644 |
| P4 | `find <fs> -xdev \( -uid <n> -o -gid <n> \) -print -quit` for `/` and each other local non-FUSE filesystem (never `~/iPad`, `~/iPadBackup`) | operator | empty |
| P5 | `absent.py` on `/var/lib/wlscratch`, `/var/lib/wlscratch-run`, `/opt/wlscratch`, `/var/lib/systemd/linger/wlscratch`, `/var/lib/systemd/linger/wlscratch-run`, `/etc/ssh/sshd_config.d/30-wlscratch.conf`, `/etc/systemd/system/user@<R>.service.d`, `/var/spool/mail/wlscratch`, `/var/spool/mail/wlscratch-run`, and with images `/var/lib/wlscratch-images` and the mount-unit paths | lead; every `undetermined` repeated by the operator | `absent` each |
| P6 | before any staging exists, so without running any helper as root: `find /etc/sudoers.d -mindepth 1 -maxdepth 1 \( -name wlscratch-frame -o -name wlscratch-run \) -print` (a complete listing of the root-only directory; no symlink is followed) | operator | exit status 0 and empty output; a non-zero exit is `undetermined` and refuses. The staging directory needs no separate check: S-0 creates it with a create-only `mkdir`, and S-D re-checks both names with the staged `absent.py` |
| P7 | `lstat` of `/`, `/var`, `/var/lib`, `/opt`, `/var/lib/systemd/linger`, `/etc/ssh/sshd_config.d`, `/etc/systemd/system`; `getfacl -n -c` of `/var/lib` and `/opt` | lead | root-owned, no extended ACL |
| P8 | `protected_hardlinks`, `protected_symlinks`, `protected_regular`, `ptrace_scope`, `suid_dumpable`, `max_user_namespaces`, `fs.leases-enable`, `fs.lease-break-time` | lead | as in §2.3 (`fs.leases-enable` 1) |
| P9 | `findmnt` of `/`, `/var/lib`, `/opt`, `/tmp`, `/var/tmp`, `/dev/shm`, `/run/user`, `/proc`, `/sys/fs/cgroup`; the mount IDs of `/tmp` and `/var/lib` in `/proc/self/mountinfo` | lead | as in §2.3 (`/proc` without `hidepid`; `/tmp` and `/var/lib` on one mount, for §13) |
| P10 | digests of `/etc/pam.d/{sudo,system-auth,system-login,system-remote-login,sshd,su,su-l,runuser,runuser-l,login,other}` | lead | `sudo` keeps `session optional pam_systemd.so class=none` |
| P11 | digests of `/etc/ssh/sshd_config` and drop-ins; `systemctl show sshd.service -p ActiveState -p UnitFileState`; `sshd -T` | lead; operator for `sshd -T` | recorded; gives the expected `denyusers` line |
| P12 | `sudo --version`; digests of `/etc/sudoers` and every `/etc/sudoers.d` file; `visudo -c`; `sudo -l -U sicarii` | lead for the version; operator | §2.3 privilege-route precondition holds |
| P13 | digests of `/usr/share/polkit-1/rules.d/*`; listing and digests of `/etc/polkit-1/rules.d`; `getent group empower wheel docker` | lead; operator for `/etc` | no rule grants `sicarii` or any of its groups a passwordless `YES` for an action that runs code as another user (for example `org.freedesktop.systemd1.manage-units`, `org.freedesktop.policykit.exec`, machine shell or login actions); `empower` and `docker` without members |
| P14 | `absent.py` on `/usr/bin/crontab`, `/usr/bin/at`, `/usr/bin/batch`, `/var/spool/cron`, `/var/spool/at`, `/var/spool/atjobs`; `systemctl show cronie.service atd.service -p LoadState` | lead | `absent`; `not-found` |
| P15 | listing of `/var/lib/systemd/linger` | lead | observed `cosmov1lab`, `wlrehearsal`, `worldline` |
| P16 | listings of `/etc/systemd/user/**`, `/usr/lib/systemd/user/*.wants/**` and `*.requires/**`, `/usr/lib/systemd/user-generators`, `/usr/lib/systemd/user-environment-generators` | lead | gives the mask list (§11.5 S-F) |
| P17 | `find / -xdev -perm /6000 -type f` with digests; `getcap -r /usr` | operator | baseline for S-I |
| P18 | `readlink -f /usr/bin/python3`; sha256 of `/usr/bin/python3.14` and `/usr/lib/libpython3.14.so`; `sys.version` | lead | observed `/usr/bin/python3.14`, `c6bc1ef4…`; 3.14.7 (the lead's earlier observation, reproduced by the re-review) |
| P19 | `systemctl --version`, `setfacl --version`, presence of `/usr/bin/nologin`, `/usr/bin/visudo` | lead | recorded (systemd 261 and sudo 1.9.17p2 are the lead's earlier observations) |
| P20 | `cgroup.controllers` of an existing lingering manager (`user@1002.service`) | lead | observed `cpu memory pids` |
| P21 | Option A: `getfacl -n -p /home/sicarii` (the full headed restore dump: `# file:`, `# owner:`, `# group:` and any `# flags:` line, then the entries), `getfacl -n -c -p /home/sicarii` (the comparison text), `stat -c '%a %u %g %d %i' /home/sicarii`, `namei -l` of the gnatprove path | operator (agents never list or stat the home directory itself) | recorded; the first becomes `home-acl.pre.dump`, the second `home-acl.pre.expected` |
| P22 | the frozen v6-W1 inventory digest and the review-freeze digests that the install will use | lead | recorded |
| P23 | `/etc/default/useradd` (`CREATE_MAIL_SPOOL` and the other defaults) | operator (unreadable to the lead: `Permission denied`, observed 2026-10-05) | recorded; the expected-object list of S-I follows it |
| P24 | `/usr/lib/systemd/system/user@.service`, its drop-in directories, `/usr/lib/pam.d/systemd-user` | lead | recorded |

Observed on 2026-10-04 by the drafting author (passive reads): the `/etc/passwd` and `/etc/group` entries at or
above 900 (§3.1, for P1/P2); P3 (§5.4); `/etc/login.defs` ranges; P5 for `/var/lib/wlscratch`,
`/var/lib/wlscratch-run`, `/opt/wlscratch` (absent from the listings of `/var/lib` and `/opt`); P8 (`protected_*` 1,
`ptrace_scope` 1, `suid_dumpable` 2, `max_user_namespaces` 128053); P9; P10 (the `sudo`, `system-auth`,
`system-login`, `system-remote-login`, `sshd`, `su` and `runuser` stacks); P11 (sshd active; drop-ins
`20-systemd-userdb.conf` and `99-archlinux.conf`; `UsePAM yes`; `AuthorizedKeysFile .ssh/authorized_keys`;
`AuthorizedKeysCommand /usr/bin/userdbctl ssh-authorized-keys %u`); P13 (the two `/usr/share` rules files read, the
`/etc` directory unreadable); P14; P15; P16; P18 (path and digest); P20.

Observed on 2026-10-05 by the drafting author (passive reads): P8's `fs.leases-enable` 1 and `fs.lease-break-time` 45;
P9's mount IDs (`/tmp` and `/var/lib` both 32, on `/dev/vda` ext4); P16 again (listed in §11.5 S-F); `/var/spool/mail`
present (mode 1777) with `MAIL_DIR /var/spool/mail` in `/etc/login.defs`; P23's refusal; P24 (`PAMName=systemd-user`,
`Delegate=pids memory cpu`, `DelegateSubgroup=init.scope`, `KillMode=mixed`, drop-ins `10-login-barrier.conf` and
`faster-shutdown.conf` adding `After=systemd-user-sessions.service` and `TimeoutStopSec=5s`; the PAM stack:
`account include system-login`, `session required pam_loginuid.so`, `session optional pam_keyinit.so force revoke`,
`session include system-auth`, `session optional pam_umask.so`, `session optional pam_systemd.so`,
`session required pam_env.so`); for `sicarii`'s own manager: `/run/user/1000` mode 0700, `/run/user/1000/systemd`
0755, the private socket 0700, the bus socket 0666, `/proc/1019/fd` (the manager) owned by `sicarii`, `/proc/1023/fd`
(its `(sd-pam)`) owned by root 0500 and unreadable to `sicarii`; `/usr/bin/ss` present. These are observations only;
the concrete inventory repeats them fresh.

### 11.4 Protected reviewed-byte staging, checked execution and reconciliation [correction: W1-SETUP-RECONCILIATION; v4: W1-SETUP-PROBES-ROLLBACK]

- Every privileged byte is part of the reviewed concrete inventory with its sha256: both sudoers files, the sshd
  drop-in, the user-manager drop-in, every expected ACL text and restore dump, every expected output that
  `check_out.py` compares, the mask list, the identity-record generator, the helpers `absent.py`, `step.py` and
  `check_out.py`, the scripts S-A to S-J, S-R's atom table for each script, every frame member and the
  member/directory lists. Every list file a script reads ends with a newline and holds one plain name per line; the
  staging review checks both, so a `read` loop never drops a last line.
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
- **Atoms.** Every numbered step of a script is one *atom*: it changes one object (a group, an account, a directory, a
  file, the ACL of one object, a symbolic link, the linger state, a unit's enablement, an image file with its
  filesystem), or it only checks, or it is an idempotent service action (`daemon-reload`, `systemctl reload sshd`).
  v4 steps that touched several objects are split into sub-steps `<n>.<i>`, one per object, and a loop over a list
  (frame directories and members, mask links) makes each iteration its own sub-step. For each atom the reviewed S-R
  table gives its class (the atom classes of §11.5), its prestate P (equal to its P-capture), its expected-post state E,
  the intermediate states its commands can leave, and the forward, completing and reversing actions.
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
  2. observes every atom of S-<x> with the prestate methods (`getent`, `absent.py`, `lstat`, `getfacl -n -c -p`,
     digests, `systemctl show`, `loginctl show-user`), each producer run under `check_out.py`;
  3. classifies each atom as exactly one of: P, one of its intermediate states, E, or *other*;
  4. requires the classes, in script order, to read: E for every atom before some atom j, then atom j in P, in an
     intermediate state or in E, then P for every later atom; at most one atom is between states, and it is the first
     that is not in E. Any other pattern, and any *other*, stops S-R;
  5. offers the operator two actions, each needing an explicit choice:
     - **resume**: from the first atom not in E, run its completing action if it is in an intermediate state that has
       one, or its forward action if it is in P, then the forward action of every later atom, in order. An atom in E is
       never run again, whatever the log says: a create-only step whose `done` line is missing but whose object is in
       E is skipped. An atom in an intermediate state without a completing action cannot be resumed (reverse, or stop);
     - **reverse**: for every atom in E or in an intermediate state, in reverse script order, run its reversing action
       for that state, with the preconditions of the atom classes (for example `userdel <name>` without `-r` only for an
       account that owns no file, `rm` only for a file whose bytes equal the staged copy), followed by `systemctl
       daemon-reload`, `visudo -c` or `sshd -t` where the object belongs to those services;
  6. re-observes the atom after each action and retains every capture; an action is complete only if the
     re-observation equals the expected state (E after a forward or completing action, the P-capture byte for byte
     after a reversing action);
  7. stops on any failed command or unequal re-observation and reports it for an explicit operator decision.
  S-R logs its own actions in a new log, `log/S-R<x>-<n>.log` (n the smallest unused, created with `O_EXCL`), and never
  appends to the stopped script's log, so a torn line stays the last line of the log it ends. Nothing is resumed or
  reversed without the operator's choice, and nothing is called undone without equality. S-R lies inside the existing
  reserved privileged setup and rollback authority; it adds no approval gate.
- The rollback steps of §15.1 are atoms of the same classes and are reconciled by the same S-R rules (§15.1's last
  paragraph).

### 11.5 Setup scripts (templates; texts and digests become exact in the concrete inventory) [corrections: W1-SETUP-RECONCILIATION, W1-SETUP-IDENTITY, W1-CUSTODY-CLOSURE; v4: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY]

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
script, and S-R A classifies that account as *other*.

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
/usr/bin/setfacl -m u:1000:--x,g:<GATE>:--x /var/lib/wlscratch
check --equal "$st/acl/var-lib-wlscratch.expected" -- /usr/bin/getfacl -n -c -p /var/lib/wlscratch
step done 5.1
step begin 5.2
/usr/bin/setfacl -m u:1000:--x,g:<GATE>:--x /var/lib/wlscratch/runs
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
entries). v4's `touch`, `chown`, `chmod` sequence for `writer.lock` is one `install` here; its intermediate states are
those of the file class below.

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
- `wlscratch-run` (Option A): `wlscratch ALL=(wlscratch-run : wlscratch-gate) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/launch_target.py *`
- Option B replaces the second file: `wlscratch ALL=(root) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py *`
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

**S-F, target home, masks, user-manager drop-in, linger.**

*Mask scope (one rule; it is also the promise of §2.1 A3, §3.2 and §5.3) [correction: W1-CUSTODY-CLOSURE].* The mask
list is the set of names of every regular file and every symbolic link that, at inventory time, lies directly in a
directory of the user manager's unit load path other than its per-user and runtime directories, and whose name ends in
`.service`, `.socket`, `.timer`, `.path`, `.mount`, `.automount` or `.swap`, whether enabled, disabled, static,
indirect, a template (`name@.service`) or an alias, together with `xdg-desktop-autostart.target`. Those directories
are the ones the installed systemd.unit(5) lists for user units (roff lines 545-622, Appendix E):
`/etc/xdg/systemd/user` (on this host a link to `/etc/systemd/user`), `/etc/systemd/user`, `/run/systemd/user`,
`/usr/local/share/systemd/user`, `/usr/share/systemd/user`, `/usr/local/lib/systemd/user` and `/usr/lib/systemd/user`.
The masks are symbolic links to `/dev/null` in `/var/lib/wlscratch-run/.config/systemd/user`, which precedes every one
of those directories in that load path; a masked unit "cannot be activated" (systemd.unit(5), roff lines 333-334). Not
masked, and governed instead by M-QUIESCENT at every classification point (§9.4, Q2-Q4 and Q7): units in the per-user
and runtime directories (`user.control`, `transient`, `generator.early`, and `$XDG_RUNTIME_DIR/systemd/{user,
generator,generator.late}`), which do not exist before M starts and whose contents are baselined in S_units; unit files
a package installs after the inventory, which the next inventory review adds (until then a classification that finds
such a unit loaded refuses); and transient units. The load path M actually uses (`UnitPath`) is recorded by the
selftest and reviewed with S_units, and a different path fails verification (§11.6). v4's enabled-closure rule is
withdrawn (§0.5 item 3).

*Observed* (passive, by the drafting author). On 2026-10-05 (v4's reading): `/etc/systemd/user` enables, through
`default.target.wants`, `omarchy-native-audio-bridge.service`, `omarchy-native-camera-bridge.service` and
`omarchy-native-mac-share-link.service`; through `graphical-session-pre.target.wants`, `xdg-user-dirs.service`; through
`graphical-session.target.wants`, `omarchy-native-clipboard-bridge.service`; through `pipewire.service.wants`,
`wireplumber.service` (also aliased as `pipewire-session-manager.service`); through `sockets.target.wants`,
`gnome-keyring-daemon.socket`, `p11-kit-server.socket`, `pipewire-pulse.socket` and `pipewire.socket`.
`/usr/lib/systemd/user/sockets.target.wants` enables `dbus.socket`, `dirmngr.socket`, `gpg-agent-browser.socket`,
`gpg-agent-extra.socket`, `gpg-agent-ssh.socket`, `gpg-agent.socket`, `keyboxd.socket`, `systemd-ask-password.socket`,
`systemd-importd.socket`, `systemd-journalctl.socket`, `systemd-machined.socket` and `systemd-storage-fs.socket`.
Neither directory has a `timers.target.wants`. Again on 2026-10-05 for v5 (Appendix E): of the load-path directories
only `/etc/systemd/user` (also reached as `/etc/xdg/systemd/user`) and `/usr/lib/systemd/user` exist; `grep -c` counts
93 names in `/usr/lib/systemd/user` with a process-starting suffix, 10 of them templates ending in `@.service` or
`@.socket`; the only timer, path, mount, automount or swap unit file there is `systemd-tmpfiles-clean.timer`, which no
`.wants` directory listed above enables. The user generators `systemd-xdg-autostart-generator` and
`30-systemd-environment-d-generator` run only when M starts or reloads, as short-lived children of M; a classification
that sees one is not quiescent and repeats (§9.4). (Existing lingering accounts run `pipewire`, `wireplumber`,
`pipewire-pulse` and `dbus-broker` processes, observed with `ps`; each also has an `(sd-pam)` process, observed
2026-10-05.)

The user-manager drop-in `user-at-R.conf` (reviewed bytes):
```ini
[Service]
PAMName=
Environment=XDG_RUNTIME_DIR=/run/user/<R>
NoNewPrivileges=yes
RestrictSUIDSGID=yes
SystemCallArchitectures=native
SystemCallFilter=~io_uring_setup:ENOSYS io_uring_enter:ENOSYS io_uring_register:ENOSYS
```
The empty `PAMName=` resets the vendor `PAMName=systemd-user`, so systemd starts M without a PAM session and without
the `(sd-pam)` helper; `XDG_RUNTIME_DIR` is set explicitly because `pam_systemd` no longer sets it, and
`user-runtime-dir@<R>.service` still creates `/run/user/<R>` (the vendor unit's `BindsTo=`). The other four lines give
M, and every process M starts, the closure that C9 gives T's process tree (§9.8 K3): `RestrictSUIDSGID=yes` denies
setting set-user-ID or set-group-ID bits by a seccomp filter that also blocks `openat2()` entirely (the installed
systemd.exec(5); its `RestrictSUIDSGID=` entry names no io_uring call, Appendix E); the system-call filter returns
`ENOSYS` for the three io_uring calls, through which a set-ID open would otherwise bypass that filter (the `:ENOSYS`
suffix is the per-call action systemd.exec(5) documents for deny-listed calls); `SystemCallArchitectures=native`
removes non-native system-call tables, as C9 kills any other architecture; and `NoNewPrivileges=yes` keeps M's
processes from gaining privileges through `execve`. A seccomp filter and `no_new_privs` are inherited by every process
M forks and cannot be removed. systemd.exec(5)'s caveat that `NoNewPrivileges=` has no effect "on processes
potentially invoked on request of them through tools such as … systemd-run(1)" concerns processes that another manager
starts; the units R's processes request are started by M itself and descend from it. That M works this way (linger
start, scope creation, cpu, memory and pids delegation, the runtime directory, and the four restrictions in effect for
M and its units on this aarch64 host) is a hypothesis that P-MGR and P-SETID verify (premises M-PAM and H2, §9.8 K7);
if it fails, W-1 must be redesigned, and no exception is taken (§2.4 R7).
```sh
<common lines, S=F; umask 022>
h=/var/lib/wlscratch-run
d=/etc/systemd/system/user@<R>.service.d
step begin 0; need_absent "$h" /var/lib/systemd/linger/wlscratch-run "$d"; step done 0
step begin 1.1; /usr/bin/install -d -o root -g root -m 0755 "$h"; step done 1.1
step begin 1.2; /usr/bin/install -d -o root -g root -m 0755 "$h/.config"; step done 1.2
step begin 1.3; /usr/bin/install -d -o root -g root -m 0755 "$h/.config/systemd"; step done 1.3
step begin 1.4; /usr/bin/install -d -o root -g root -m 0755 "$h/.config/systemd/user"; step done 1.4
step begin 2; /usr/bin/install -d -o <R> -g <R> -m 0700 "$h/tmp"; step done 2
i=0
while read -r u; do
  i=$((i+1)); step begin "3.$i"; /usr/bin/ln -s /dev/null "$h/.config/systemd/user/$u"; step done "3.$i"
done < "$st/masks.list"
step begin 4.1; /usr/bin/install -d -o root -g root -m 0755 "$d"; step done 4.1
step begin 4.2; /usr/bin/install -o root -g root -m 0644 "$st/user-at-R.conf" "$d/50-wlscratch.conf"; step done 4.2
step begin 4.3
/usr/bin/systemctl daemon-reload
v=$(check --print -- /usr/bin/systemctl show 'user@<R>.service' -p PAMName --value); [ -z "$v" ]
v=$(check --print -- /usr/bin/systemctl show 'user@<R>.service' -p NoNewPrivileges --value); [ "$v" = yes ]
v=$(check --print -- /usr/bin/systemctl show 'user@<R>.service' -p RestrictSUIDSGID --value); [ "$v" = yes ]
check --equal "$st/user-at-R.show.expected" -- /usr/bin/systemctl show 'user@<R>.service' -p SystemCallFilter -p SystemCallArchitectures
step done 4.3
step begin 5; /usr/bin/loginctl enable-linger wlscratch-run; step done 5
```
`ln -s` without `-f` fails if a name exists; the masks and the drop-in precede linger, so M first starts with them in
place. A failing `systemctl show` now stops the script instead of passing as an empty `PAMName` (§0.5 item 10).
`user-at-R.show.expected` is the exact `systemctl show` text, part of the reviewed concrete inventory.

**S-G, Option A only: home traverse entry** (operator; agents never stat the home directory).
```sh
<common lines, S=G; umask 077>
step begin 0
check --equal "$st/home-acl.pre.dump" -- /usr/bin/getfacl -n -p /home/sicarii         # P21 restore dump; a concurrent change stops here
check --equal "$st/home-acl.pre.expected" -- /usr/bin/getfacl -n -c -p /home/sicarii  # P21 comparison text
step done 0
step begin 1; /usr/bin/setfacl -m g:<GATE>:--x /home/sicarii; step done 1
step begin 2
check --equal "$st/home-acl.post.expected" -- /usr/bin/getfacl -n -c -p /home/sicarii # pre + the entry + the recalculated mask
check --equal "$st/home-acl.post.dump" -- /usr/bin/getfacl -n -p /home/sicarii
step done 2
```
If step 2 stops, the operator runs S-R G at once; its reversal is the restore of §15.1 step 7 from
`home-acl.pre.dump`.
**S-G′, Option B only:** no home ACL; `sandbox_launch.py` is a frame member installed by S-C, and its rule is S-D's
Option B line.

**S-H, setup identity record** [correction: W1-SETUP-IDENTITY]. A reviewed generator, run as
`$py "$st/make_setup_identities.py" /opt/wlscratch/setup-identities.json`, creates the file with `O_EXCL`, 0644,
root:root, holding: the numbers; for every setup object other than the record itself, its path, its class (§11.7), the
value of every field §11.7 pins for that class, and the names of the fields that class leaves intentionally mutable
(`mutable_fields`); the mount facts of T_root and R_root (with images: the pinned image facts, the images directory and
each image root's `lost+found`); the installed frame root identity and member digests; the sudoers, sshd and
user-manager drop-in digests; the mask list digest; the linger file; the digests of `/etc/subuid`, `/etc/subgid` and
of the new `passwd`, `group`, `shadow` and `gshadow` lines. The record does not list itself and holds no digest, size
or identity of its own bytes; its seal is external (§11.7).

**S-I, post-setup capture** (operator, read-only, every producer under `check_out.py`): the first character only of
each new `shadow` password field; the `gshadow` lines of GATE and of both user-private groups (no members, locked);
sudoers digests and `visudo -c`; `sudo -l -U sicarii` and `sudo -l -U wlscratch`; `sshd -T -C user=wlscratch,…`;
`systemctl show user@<R>.service -p PAMName -p Environment -p NoNewPrivileges -p RestrictSUIDSGID -p SystemCallFilter
-p SystemCallArchitectures`; R's processes (exactly M: no `(sd-pam)`, no `dbus-broker`) and the `NoNewPrivs` and
`Seccomp` lines of M's `/proc/<M>/status`; `absent.py` on `/var/spool/mail/wlscratch` and
`/var/spool/mail/wlscratch-run`; `find / -xdev -perm /6000 -type f` and `getcap -r /usr` compared with P17;
`find / -xdev \( -uid <W> -o -gid <W> -o -uid <R> -o -gid <R> -o -gid <GATE> \)` equal to exactly the setup objects;
and the seal capture of `setup-identities.json` (sha256, size, `[dev, ino]`, owner, group, mode, link count and
`getfacl -n -c`; §11.7), which the installed-evidence review records.

**S-R, reconciliation** (operator; interactive): the procedure of §11.4, with, per script, the reviewed atom table
(each atom's step numbers, class, P-capture, expected-post capture, intermediate states and actions).

**Atom classes** (the reviewed table S-R uses; the concrete inventory adds each atom's exact captures; "—" means none):

| Class | Forward action | P | Intermediate states (completing action; reversing action) | E | Reversing action from E |
|---|---|---|---|---|---|
| group | `groupadd --system --gid n name` | no `group` or `gshadow` entry with the name or the number | a `group` entry as expected without its `gshadow` entry (—; `groupdel name`) | both entries as captured | `groupdel name` (no member, owns no file) |
| account (two steps) | `useradd …`, then `lock_account` | no `passwd` or `shadow` entry with the name or the number | a `passwd` entry without its `shadow` entry (—; `userdel name`); both entries with an unlocked password field (`usermod -L name`; `userdel name`) | both entries as captured, the password field locked, no mail spool | `userdel name` without `-r` (owns no file) |
| directory | `install -d -o -g -m path` | `absent` | an empty directory with another owner, group or mode (`chown` and `chmod` to the expected values; `rmdir -- path`) | a directory with the expected owner, group and mode, no ACL | `rmdir -- path` (empty) |
| file | `install -o -g -m staged path` | `absent` | a regular file with the staged bytes and another owner, group or mode (`chown`, `chmod`; `rm -- path`); a regular file whose bytes are a proper prefix of the staged bytes (—; `rm -- path`) | a regular file, one link, the staged bytes, the expected owner, group and mode, no ACL | `rm -- path` (bytes equal to the staged copy) |
| mask link | `ln -s /dev/null path` | `absent` | — (one `symlink` call) | a symbolic link to `/dev/null` owned by root | `rm -- path` (target `/dev/null`) |
| ACL of one object | `setfacl -m entries path` | `getfacl -n -c -p` equal to the P-capture | — (one `setxattr`) | equal to the expected text | `setfacl -b -- path` for an object setup created, then equality with that object's own E-capture; for `/home/sicarii`, §15.1 step 7 |
| linger | `loginctl enable-linger name` | linger file `absent`, no `Linger=yes` | — | the linger file present (§11.7) and `Linger=yes` | `loginctl disable-linger name`, only after §15.1 step 2 holds |
| unit enablement (images) | `systemctl enable --now unit` | not enabled and not active | enabled and not active (`systemctl start unit`; `systemctl disable unit`); active and not enabled (`systemctl enable unit`; `systemctl stop unit`) | enabled and active, with §3.4's mount entry | `systemctl disable --now unit`, after §15.1 step 6's checks |
| image file and filesystem (images) | `fallocate`, `chmod 0600`, `chown root:root`, `mkfs.ext4` | `absent` | a file of the reviewed size with any owner and mode and no filesystem signature (`chmod`, `chown`, `mkfs.ext4`; `rm -- path`); a root:root 0600 file without a filesystem signature (`mkfs.ext4`; `rm -- path`) | root:root 0600, the reviewed size, ext4 with the reviewed UUID and label | `rm -- path`, after it is unmounted and no loop device uses it |
| check or service action | the command | no object | — | — | re-run after the reversal of the objects it concerns (`daemon-reload`, `visudo -c`, `sshd -t`, `systemctl reload sshd`) |

Every state not in this table, for its class, is *other*: S-R stops and reports it for an explicit operator decision.

### 11.6 Post-setup verification

- Lead (unprivileged): `getent` for the three identities; `lstat` and `getfacl -n -c` of `/var/lib/wlscratch`,
  `runs/`, `runs/records`, `/var/lib/wlscratch-run` and its children compared with the pinned fields of
  `setup-identities.json` (§11.7) and §6.3; the installed frame listed and hashed member by member against the frozen
  inventory, with §11.1's regular-file and directory rules, no extra entry and no ACL; `/var/lib/systemd/linger` equal
  to P15 plus `wlscratch-run`; `loginctl show-user` for both accounts; `cgroup.controllers` of `user@R.service`
  containing `cpu memory pids`; R's processes exactly M (no `(sd-pam)`, no bus broker); `/etc/subuid` and
  `/etc/subgid` unchanged.
- Through the selftest verbs (W and L/C/O): `lease/` and `writer.lock` identities, role identities and readbacks; M's
  units, job queue and sockets, observed and recorded as the candidate baselines S_units and S_socks, which are
  reviewed with the installed evidence before adoption (§16); and the probes of §13.
- Operator: S-I.

### 11.7 Setup identities: pinned and intentionally mutable fields [correction: W1-SETUP-PROBES-ROLLBACK]

Every later invocation, and every invocation after a reboot, compares only the pinned fields; it observes and records
the mutable ones in its role or stage identity and never compares them with setup-time values. A change of a pinned
field refuses before any mutation.

| Object class | Pinned (compared at every use) | Intentionally mutable (recorded, never compared with setup values) | Constraint on the mutable part |
|---|---|---|---|
| Regular setup files: `writer.lock`, the sudoers files, the sshd and user-manager drop-ins, every installed frame member | type, `dev`, `ino`, uid, gid, mode, `nlink` 1, size, sha256 (`writer.lock`: size 0), no ACL | atime, mtime, ctime | none |
| `setup-identities.json` (never listed in itself; sealed from outside, below) | fixed values checked at every use: type regular, uid 0, gid 0, mode 0644, `nlink` 1, no ACL; sha256, size, `dev` and `ino` compared with the seal below, never with the record's own content | atime, mtime, ctime | none |
| Mask links | type symlink, `dev`, `ino`, uid 0, gid 0, target `/dev/null`, the exact name set | atime, mtime, ctime | none |
| Static setup directories: `/var/lib/wlscratch`, `lease/`, `/var/lib/wlscratch-run`, `.config`, `.config/systemd`, `.config/systemd/user`, the drop-in directory, `/opt/wlscratch`, the installed frame directories | type, `dev`, `ino`, uid, gid, mode, exact ACL text, exact entry set, `nlink` | atime, mtime, ctime (they move only with the entry set, which is pinned) | none |
| Growing tree directories: `runs/` (T_root) and `runs/records` (R_root) | type, uid, gid, mode, exact ACL text; without images also `dev` and `ino`; with images the mount identity of the next row instead | `nlink`, size, atime, mtime, ctime, the entry set | every entry obeys §3.4's name grammar and is a W-owned directory, except, with images, the pinned `lost+found` special entry of §3.4; W checks it at every invocation |
| `/var/lib/wlscratch-run/tmp` | type, `dev`, `ino`, uid R, gid R, mode 0700, no ACL | `nlink`, size, times, the entries (target temporaries) | none (target-writable residual, §12.3) |
| Image mounts (images only, §14.5) | filesystem UUID and label; the backing image file's `dev`, `ino`, size, mode 0600, uid 0, gid 0 and `nlink` 1 on the root filesystem, read by W and W2 through the search-only images directory (§3.4, §14.5 J1); the mount point path; mount options `nosuid,nodev,noexec`; the nesting (records inside work); the image root's uid, gid, mode, ACL and `ino` | the mounted filesystem's `st_dev` (the loop device number), the loop device name, the mount ID | `st_dev` differs from the parent's and equals the device of the mountinfo entry whose loop device's backing file is the pinned image file |
| Images directory `/var/lib/wlscratch-images` (images only) | type, `dev`, `ino`, uid 0, gid W, mode 0710, no ACL; its exact entry set, captured by the operator (W cannot list it) | atime, mtime, ctime | W only looks up the pinned names in it |
| `lost+found` of each image root (images only) | name, type directory, `ino`, uid 0, gid 0, mode 0700, no ACL | `nlink`, size, times, contents (root's; `e2fsck` may add entries; W cannot read them) | never used, opened or walked by the frame |
| Bare mount points (images only; observed at setup and rollback while unmounted) | type, `dev`, `ino`, uid 0, gid 0, mode 0700, empty, no ACL | times | must be empty |
| Linger file `/var/lib/systemd/linger/wlscratch-run` | existence, type regular, uid 0, gid 0, size 0 | `dev`, `ino`, times (logind's file) | none |
| M's socket baseline S_socks and unit baseline S_units (§9.4) | the kind, bound name, type and peer class of every socket; the unit names and baseline states | socket inode numbers, pids, invocation ids (boot-local) | compared by kind, name and peer class only |

The setup identity record stores, for every object other than itself, the class and the pinned values;
`/run/user/<R>` is not a setup object (logind recreates it) and is observed per invocation.

**Seal of `setup-identities.json` [correction: W1-SETUP-IDENTITY].** The record never lists itself: S-H's generator
leaves it out of every class, so its bytes hold no digest, size or identity of themselves and no fixed point is
needed. Its final bytes are bound from outside, in this order: (1) S-I captures its sha256 (S), size, `[dev, ino]`,
owner, group, mode, link count and ACL text; (2) the installed-evidence review (INSTALLED_REVIEW) reviews that capture
and records S (§4.6, join 2); (3) `adopt` requires, before it writes `lead-adoption.json`, that the live file's sha256
is the S of the installed review it joins, and the adoption record binds S with the size and `[dev, ino]` W read
(`setup_identities_file`, Appendix B.3). Every later invocation opens the live file through an anchored no-follow chain,
checks the fixed values (regular, uid 0, gid 0, mode 0644, one link, no ACL), computes its sha256 and size from the
bytes it reads, and compares them, with `[dev, ino]`, with a seal before its first mutation:
- `dispatch`: the committed adoption record's values (D3), and also the values `generation.json` recorded, so a
  generation materialized under another setup record is refused;
- `seal-front` (W2): the values its attempt sealed (the adoption record pinned in a dispatch attempt's `attempt.json`;
  `generation.json`'s recorded values for A0);
- `materialize`: the committed adoption record of the installed inventory I if one exists; otherwise there is no
  reviewed seal yet, and W records the values in `generation.json` with `setup_seal: unadopted` (v5's `materialize`
  does not depend on adoption, §4.6); such a generation is admitted only after `dispatch` finds those values equal to
  the adoption record's;
- `adopt`: AD3's bookkeeping in P_ado(I) (its directories and `invocation.json`) precedes the check, which is made at
  AD5 against the installed review and precedes `lead-adoption.json`; a mismatch is `REFUSAL`, and no adoption record
  exists;
- `selftest`: records the values only, because the selftests precede the installed review.
A mismatch refuses before any mutation. The pinned and intentionally mutable fields of every other object stay as
tabled above; the record's own atime, mtime and ctime are recorded and never compared.

## 12. Exposure options [gap: exposure-options]

No option is selected or recommended here. Both keep the exact original target command path.

### 12.1 Option A: one traverse entry on `/home/sicarii`

- **Change:** `group:<GATE>:--x` on `/home/sicarii` (S-G). It is a group entry, so only GATE holders (L, C, O, T and
  T's descendants) get it; R's background processes and W do not.
- **Known required:** the toolchain subtree `/home/sicarii/opt/gnat/**`. Every component below `/home/sicarii` must
  be others-searchable and the toolchain files others-readable and, for executables, others-executable; P21's
  `namei -l` capture verifies the components at setup.
- **Known exposed (historical observation, not re-inspected for v3):** during v1's preparation `~/opt`,
  `~/Documents`, `~/.claude` and `~/.codex` were observed 0755. Every others-readable file reachable through
  others-searchable directories below them is readable by T, including lead transcripts under `~/.claude/projects` and
  the WORLDLINE work tree under `~/Documents`.
- **UNKNOWN:** everything else below `/home/sicarii`, explicitly including `~/iPad` and `~/iPadBackup` (FUSE mounts,
  never listed or stat'ed) and `~/.local/share/sia/.gbrain` (never inspected). No exact exposure set is claimed and no
  aggregate count is offered as one. A complete enumeration would require listing the home directory itself, which the
  machine rules forbid to agents; an operator enumeration with the same exclusions would still leave those paths
  UNKNOWN.
- **Write exposure added:** none by the entry itself (search only). T can write any others-writable object below
  `/home/sicarii` that it can reach: part of the UNKNOWN inventory of §12.3.
- **PATH:** original `PATH` entries below `/home/sicarii` resolve for T only where others-searchable; executables
  there are `sicarii`-writable (R4).

### 12.2 Option B: root launcher with a private mount namespace (design level; concrete review in the setup package)

- **Rule:** S-D's Option B line replaces the launcher rule; RL runs as root, then becomes L.
- **RL steps:** first act (§7.7); role identity; argv grammar (verb `launch`, `observe` or `selftest`; g; A; nonce;
  seals); before any namespace change, open the real toolchain directory by an anchored no-follow walk
  (`openat2` with `RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS`) and record its `[dev, ino]`, owner and mode;
  `unshare(CLONE_NEWNS)`; set `MS_REC|MS_PRIVATE` on `/` before any mount (**mount propagation**: nothing propagates
  back to the host and host mount events do not enter); mount a tmpfs on `/home/sicarii` (mode 0755, uid 0, gid 0,
  size 1 MiB, few inodes); create `opt/gnat` in it; bind the held toolchain directory there (`open_tree`/`move_mount`
  from the held descriptor) and remount it `MS_RDONLY|MS_NOSUID|MS_NODEV`; verify inside the namespace that
  `/home/sicarii` lists exactly `opt`, `opt` lists exactly `gnat`, the bound root's `[dev, ino]` equals the held one and
  the mount is read-only.
- **Inherited fds:** only 0-2 (sudo's `closefrom` guarantees it; RL verifies `/proc/self/fd`).
- **Capability, uid, gid and group drop:** drop every bounding-set capability (`PR_CAPBSET_DROP`), clear ambient
  capabilities, `setgroups([R])`, `setresgid(GATE, GATE, GATE)`, `setresuid(R, R, R)`, `PR_SET_NO_NEW_PRIVS` = 1; then
  verify `/proc/self/status`: all uids R, all gids GATE, groups `[R]`, every capability set zero, `NoNewPrivs: 1`.
- **Root-before-drop work** is only validation, identity, the namespace and its mounts, the checks, fd verification,
  the credential drop and `execve`. RL writes no file on any host filesystem; the tmpfs exists only inside the
  namespace.
- **Environment:** RL builds L's exact environment (the relocated environment of §8.4) and `execve`s L.
- **Identity:** RL sends its `root-launcher` role identity (namespace inodes before and after, the relevant
  `mountinfo` lines, credentials and capability sets after the drop) to W over fd 0 before `exec`; W commits it.
- **Reachable paths** for L, C, O and T: the host mount table except `/home/sicarii`, where only the read-only
  toolchain is visible.
- **New trust:** privileged code behind a passwordless rule that any writer instance can call with any arguments, so
  RL must be robust to arbitrary input. Its code, rule, probes (propagation, fds, credentials, capabilities,
  namespace contents) and residuals are reviewed in the concrete setup package before any approval. No implementation
  or sufficiency evidence exists.
- **Exposure:** known required: the toolchain subtree, read-only. Nothing else below `/home/sicarii` is visible to T.

### 12.3 Target-write residual (both options), stated as an inventory

- **Known target-writable places:** partition contents of g; its stream descriptors; `/var/lib/wlscratch-run/tmp`;
  `/tmp` and `/var/tmp` (world-writable, sticky, on the same ext4 as everything else); `/dev/shm`; `/run/user/R`
  (including M's transient-unit state); M itself, through its private socket (transient units and the other requests
  of §9.4 (b); the user bus is masked).
- **UNKNOWN:** every other location on the host that is others-writable or writable by R or GATE. No complete
  inventory of world-writable objects exists; under Option A this includes anything others-writable below
  `/home/sicarii`.
- The residual covers target writes only and never a frame write (V5-B02). What a target leaves in M or in another
  process's hands is checked by §9.4 before any later final pass or release.

## 13. Probe specification (future; nothing here has been executed) [corrections: W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY, W1-COMMIT-JOURNAL-EXPORT; gap: denial-probes]

**Fixtures.** The writer selftest creates a sacrificial pair, `runs/selftest-<h>` (written `sg` below) and
`runs/records/selftest-<h>` (written `sg_rec`), with §3.3's layout and §6.3's modes and ACLs, reduced to: a recipe
directory `sg/source/src/` (0755) holding `src/a.adb` (0644); a partition root `sg/source/src/obj` (0770 by ACL); a
P_adm record `sg/rec.json` (0600); `sg/inputs/` (0700) holding `in.bin` (0600); `sg_rec/attempts/<A>/` (0700) holding
`att.json` (0600); `sg_rec/export/` (0750 by ACL) holding `exp.json` (0640 by ACL). The launcher selftest creates, as T
would, `src/obj/t.o` (0600) and `src/obj/d/` (0700). Each actor has its own directory for rename and link targets:
`/tmp/wl-probe-a1-<h>/` (A1, 0700) and `/tmp/wl-probe-a2-<h>/` (A2, 0700). Probes never touch a real generation, the
real window file or anything below `/home/sicarii` other than the lead's own records. The tables write paths relative
to `/var/lib/wlscratch/runs/`; each probe uses the absolute path. The selftest verbs use §7's framing with their own
test-only state machines, which are part of the code review (§16, step 2); they never run in a real generation.

**Actors.** A1: the lead, uid 1000, outside. A2: a launcher-selftest process with T's credentials (R + GATE,
`no_new_privs`, the anti-setid filter). A3: a transient service started through M by the launcher selftest (R without
GATE). A4: a second writer selftest instance while the first holds the lease. A5: W itself (positive controls).

**Each probe row records:** the actor's full credentials; the exact syscall and its absolute operands; the
preconditions observed immediately before (below); the raw errno number and name, or success; and, on unexpected
success, the whole resulting state, retained and never cleaned. An unexpected success is a setup failure. An unexpected
errno fails the row as well, because it may show a wrong operand rather than the intended denial.

**Preconditions, checked immediately before each row.** (1) By W, the fixture's owner: each source operand exists with
the expected type (`lstat`), and each destination name is `absent` (§11.1; W can decide it because it owns the
fixture). (2) By the actor: `faccessat(…, X_OK, AT_EACCESS)` on every ancestor of each operand equals the search
permission §6.3 implies for that actor; a difference fails the row as a fixture error. (3) For a `rename` or `link`
between two directories: both on the same mount (equal mount IDs in `/proc/self/mountinfo`), so that `EXDEV`, which the
kernel reports before any permission check, cannot mask the result. `/tmp` and `/var/lib` share mount 32 (§2.3). With
images no actor-owned directory exists on the image mounts, so the cross-directory rows are recorded
`not-applicable: different mount`, and the same-directory rows carry the denial.

**Expected errnos** follow §6.5's rule (the first failing check). "ok" marks a positive control.

A1 (`sicarii`), without images:

| Operand(s) | Operation | Expected | Reason |
|---|---|---|---|
| `sg/source/src/a.adb` | `open(O_RDONLY)` | ok | search granted (`--x` on `/var/lib/wlscratch`, `runs/` and `sg`; recipe directories 0755); file 0644 |
| `sg/source/src/a.adb` | `open(O_WRONLY)`; `truncate`; `utimensat(NULL)` | `EACCES` each | no write permission on the file |
| `sg/source/src/a.adb` | `chmod 0666`; `chown 1000`; `setxattr(system.posix_acl_access)`; `utimensat` with explicit times | `EPERM` each | not the owner |
| `sg/source/src/a.adb` | `unlink`; `rename` to `sg/source/src/b` | `EACCES` each | no write permission on `src/` |
| `sg/source/src/a.adb` → `/tmp/wl-probe-a1-<h>/x` | `rename` out | `EACCES` | no write permission on the source parent |
| `/tmp/wl-probe-a1-<h>/y` (A1's own file) → `sg/source/src/y` | `rename` in | `EACCES` | no write permission on `src/` |
| `sg/source/src/a.adb` → `/tmp/wl-probe-a1-<h>/l` | `link` out | `EPERM` | `protected_hardlinks`: not the owner, no read-write access |
| `/tmp/wl-probe-a1-<h>/y` → `sg/source/src/l` | `link` in | `EACCES` | no write permission on `src/` |
| `sg/source/src/n`; `sg/source/src/d`; `sg/source/src/s` | `open(O_CREAT\|O_EXCL)`; `mkdir`; `symlink` | `EACCES` each | no write permission on `src/` |
| `sg/rec.json` | `open(O_RDONLY)`; `open(O_WRONLY)` | `EACCES` each | file 0600 owned by W |
| `sg/rec.json` → `/tmp/wl-probe-a1-<h>/r` | `link` out | `EPERM` | `protected_hardlinks` |
| `sg/rec.json` | `unlink` | `EACCES` | no write permission on `sg` |
| `sg/inputs/in.bin` | `open(O_RDONLY)` | `EACCES` | no search permission on `inputs/` |
| `sg/source/src/obj/t.o`; `sg/source/src/obj/n` | `open(O_RDONLY)`; `open(O_CREAT)` | `EACCES` each | no search permission on the partition root (`other::---`) |
| `records/selftest-<h>/attempts/<A>/att.json` | `open(O_RDONLY)` | `EACCES` | no search permission on `attempts/` |
| `records/selftest-<h>/export/exp.json` | `open(O_RDONLY)` | ok | export ACL |
| `records/selftest-<h>/export/exp.json` | `open(O_WRONLY)` | `EACCES` | export file `r--` for 1000 |
| `records/selftest-<h>/export/n` | `open(O_CREAT)` | `EACCES` | export directory `r-x` for 1000 |
| `/var/lib/wlscratch/lease/writer.lock` | `open(O_RDONLY)` | `EACCES` | no search permission on `lease/` |
| a new name in `runs/`; a new name in `records/` | `mkdir` | `EACCES` each | search-only entries |

A2 (R + GATE, `no_new_privs`, the anti-setid filter), without images:

| Operand(s) | Operation | Expected | Reason |
|---|---|---|---|
| `sg/source/src/a.adb` | `open(O_RDONLY)` | ok | GATE search, others read |
| `sg/source/src/a.adb` | `open(O_WRONLY)` | `EACCES` | file 0644 owned by W |
| `sg/source/src/a.adb` | `chmod 0666` | `EPERM` | not the owner |
| `sg/source/src/a.adb` → `/tmp/wl-probe-a2-<h>/l` | `link` out | `EPERM` | `protected_hardlinks` |
| `sg/source/src/n` | `open(O_CREAT\|O_EXCL)` | `EACCES` | no write permission on `src/` |
| `sg/rec.json` | `open(O_RDONLY)` | `EACCES` | file 0600 owned by W |
| `sg/inputs/in.bin` | `open(O_RDONLY)` | `EACCES` | no search permission on `inputs/` |
| `sg/source/src/obj/n2` | `open(O_CREAT\|O_EXCL)`, then `unlink` | ok, ok | partition root GATE `rwx` |
| `sg/source/src/obj` → `sg/source/src/obj2` | `rename` | `EACCES` | no write permission on `src/` |
| `sg/source/src/obj` | `rmdir` | `EACCES` | no write permission on `src/` |
| `sg/source/src/obj` | `chmod 0777` | `EPERM` | owned by W |
| `records/selftest-<h>/attempts/<A>/att.json`; `records/selftest-<h>/export/exp.json` | `open(O_RDONLY)` | `EACCES` each | no search permission on `records/` (no GATE entry) |
| `/var/lib/wlscratch/lease/writer.lock` | `open(O_RDONLY)` | `EACCES` | no search permission on `lease/` |

A3 (R without GATE): `open(O_RDONLY)` of `sg/source/src/a.adb` and of `records/selftest-<h>/export/exp.json` →
`EACCES` at `/var/lib/wlscratch` (`other::---`); `mkdir` of `/var/lib/wlscratch-run/tmp/wl-probe-a3-<h>` → ok (its
own `TMPDIR`).

A4: `LeaseHeld` before any mutation and before starting any helper; the listings of `runs/` and `runs/records` are
identical before and after.

A5 (W): `open(writer.lock, O_WRONLY)` → `EACCES` (0440, group `r--`); `chmod` of `writer.lock` → `EPERM` (owned by
root); `rename` or `unlink` in `lease/` → `EACCES` (root-owned 0750); a record committed with the generic primitive
(ok, 0600) and an export copy made with the export primitive, whose `fstat` after the ACL shows 0640 before its marker
is written (ok, §15.3).

With images the tables are the same, with `runs/` and `records/` on the image mounts, the cross-directory rows
`not-applicable: different mount` and the same-directory rows unchanged.

| Family | Operations and expected outcome |
|---|---|
| P-MUT, P-ALIAS, P-READ | the tables above; in addition A1 mounts over `sg` inside its own user namespace and `findmnt` in the host namespace shows no change |
| P-LEASE | A4 and A5 above |
| P-DRIFT | Between the O parent-stage walk and C's final pass of a sacrificial attempt, A2 changes an excluded partition leaf (content, mode, mtime, a second hard link inside the partition, replacement): C refuses with the recorded reason. A control without change is accepted |
| P-LAUNCH | A1 runs `sudo -n -u wlscratch-run …` (refused; exact status and message); a writer selftest starts L and closes SP_L before `GO` (L exits 125, nothing started); C started outside the scope or with a wrong seal refuses; C without `SPAWN_OK` refuses; L or C given a stream descriptor whose `[dev, ino]` differs from `launcher-intent.json` refuses; the credential sets in which sudo's monitoring processes appear in `/proc` are recorded (§9.4, K(P)) |
| P-SETID | A2: `fchmod`, `fchmodat`, `fchmodat2` with 04755 and 02755, `openat(O_CREAT)` with 06755, `mknodat` with 06755 → `EPERM`; `io_uring_setup`, `openat2` → `ENOSYS`; ordinary `chmod 0755` and `open` 0644 succeed. A3: `chown` to group GATE → `EPERM` |
| P-DUMP | every role's two readbacks; timestamps of `exec` and of the first act (pre-first-call window) |
| P-MGR | `loginctl show-user` for W (no manager, no `/run/user/W`) and R (`Linger=yes`, running); `systemctl show user@<R>.service -p PAMName` empty; R's processes exactly M (no `(sd-pam)`, no `dbus-broker`); `/proc/<M>/fd` readable by R; `user@R.service` controllers ⊇ {cpu, memory, pids}; `systemd-run --user --scope` works; the modes of `/run/user/<R>`, its `systemd` directory and the private socket; a connection to the private socket by A1, by path and through a descriptor of `/run/user/<R>/systemd` handed over by A2, is refused (by `EACCES` on the socket or by systemd's peer-credential check, whichever comes first; both recorded); M's units, jobs and sockets recorded as the candidate S_units and S_socks |
| P-QUIESCE | on a sacrificial attempt A2, in turn: (a) starts a transient unit; (b) hands a connection to M's private socket to an A1 process over an abstract socket and exits; (c) sends M a request and exits at once; (d) hands an `O_RDWR` descriptor of a sacrificial partition file to an A1 process and exits; (e) leaves such a descriptor queued in a socket whose other end an A1 process holds and never reads; (f) leaves a shared writable mapping of a partition file in a process handed to A1. For each: the after-stage classification is `live`, never `known-terminal`, while the condition lasts (SCAN-LEASE refuses for (d)-(f); SCAN-QUIESCE or SCAN-UNITS shows (a)-(c)), and it becomes `known-terminal` only after the condition ends; a control with none of them reaches `known-terminal`. A request sent to M immediately before the barrier call of SCAN-QUIESCE (4) is visible in the repeated scan |
| P-STREAM | A2 hands its `child.stdout` descriptor to an A1 process and exits: W's stream finality test reports the stream not final; a control is final |
| P-RUNTIME | role identities, module closures and runtime-closure observations in each context against their baselines |
| P-SIG, P-RELAY | A1 sends `SIGTERM` to S1 during a writer selftest wait: W's interrupt record, whether `sudo` relayed it, and that W made no mutation outside its sacrificial tree |
| P-TERM | terminal-failure controls through test-only switches of the selftest verbs (never of `dispatch`): W death after the launch intent and after `PROCEED_LAUNCH` (recovery by W2 with complete rounds, §9.7); L death after `GO`; C refusal; C killed after its spawn call and before `CHILD_START` (`target_started: unknown`, classification by scans); target non-zero exit (`/usr/bin/false` as the selftest target); F death after a reservation of a sacrificial copy of the window protocol on a sacrificial path. Expected behaviour as §9.5 and §9.7 |
| P-COMMIT | failures injected into the commit primitive: primary; primary and retry; fallback (a VALID slot); a short slot write followed by an error (a TORN slot, never reused; the next write goes to the next slot); fallback exhausted (UNKNOWN); a torn marker (the next writer's seq skips it and its `prev_commit` links to the head); the export ACL readback (final mode 0640 before the marker); increments and cuts (each record exported exactly once; the final freeze marker reported); a release whose `release-intent.json` cannot be committed still releases when known-terminal ownership holds (durability-UNKNOWN, success withheld) |
| P-ENOSPC | required before any record is described as durable under allocation failure: on an operator-provided sacrificial small filesystem, fill it; fallback slot writes must then succeed. Until it passes no such claim is made (§10.4) |
| P-SETUP | `absent.py` on an absent path (`absent`), an existing file (`present`), a dangling symlink (`present`), a path below an unreadable directory (`undetermined`, `EACCES`), a path whose parent is a regular file (`undetermined`, `ENOTDIR`) and a path with a missing parent (`undetermined`); S-R's classification logic run against recorded synthetic logs and observations (no account is created by a probe) |
| P-MOUNT | images only: with the records image unmounted (its bare mount point visible), and then with both images unmounted, every writer verb refuses before any mutation and O and C refuse; the bare mount points are unchanged afterwards; a remount at a different loop device number is accepted, because the loop device number is a mutable field (§11.7) |
| V-VAULT | as `sicarii`: `project-vault pin`, `status` and the project-vault recovery comparison on `runs/records/selftest-<h>/export` |

### 13.1 v5 probe additions (future; nothing here has been executed) [corrections: all six]

The fixtures, actors, record rules and preconditions of §13 apply. A3 is, as in §13, a transient service started
through M by the launcher selftest. Parent-stage and child-stage steps run on a sacrificial attempt of the
sacrificial generation, never on a real generation or the real window file. A probe can refute a premise of §9.8 K7;
it never establishes one, and no probe result is turned into an exception.

| Family | Operations and expected outcome |
|---|---|
| P-WCLOSED | A2 creates below `sg/source/src/obj` a file `w1` and a directory `wd/` holding a file `w2`, and sets `w1` to mode 0666, `wd` to 0777 with a default ACL entry `d:u:1000:rwx`, and `w2` to 0644 with ACL entries `u:1000:rw-` and `g:<the lead's gid>:rw-`; it hands an A1 process, over a socket, an `O_PATH` descriptor of `w1`, an `O_RDONLY` descriptor of `w2` and an `O_RDONLY\|O_DIRECTORY` descriptor of `wd`, leaves one more descriptor queued in a socket A1 holds, and exits. The next parent stage's revocation records exactly the changes that clear the group-class and other-class write bits (the ACL entries remain, masked). Afterwards each of A1's attempts fails with the errno §6.5's rule gives: `openat(wd, "w2", O_WRONLY)`, `open("/proc/self/fd/<n>", O_WRONLY)` on the `O_PATH` descriptor, `unlinkat`, `renameat`, `linkat`, `mkdirat` and `symlinkat` in `wd`, `fchmod`, `fchownat`, `setxattr(system.posix_acl_access)` and `utimensat` with explicit times or with `NULL` times; and a later A2, the owner, still opens `w1` for writing. Controls: an attempt without grants records no change; a file A1 created in `wd` while it was 0777 makes the stage refuse (not owned by R); a hard link A1 made of a file A2 had made `o+rw` makes the stage refuse (two links); a `fchmodat2(…, AT_EMPTY_PATH)` on an `O_PATH` descriptor changes the held inode only (K-CHMOD) |
| P-SETID (v5 rows) | A2: `io_uring_enter` and `io_uring_register` on a ring descriptor received from an A1 process → `ENOSYS`. A3: `fchmod`, `fchmodat` and `fchmodat2` with 04755 and 02755, `openat(O_CREAT)` with 06755 and `mknodat` with 06755 → `EPERM`; `openat2`, `io_uring_setup`, `io_uring_enter` and `io_uring_register` → `ENOSYS`; its `/proc/self/status` shows `NoNewPrivs: 1` and seccomp mode 2; an ordinary `chmod 0755` and `open` 0644 succeed. Both filter lists are compared with the installed kernel's aarch64 system-call table for every call that takes or sets a file mode, a set-ID bit or a file capability (H3) |
| P-MGR (v5 rows) | with the hardened drop-in: `systemctl show user@<R>.service` shows the empty `PAMName` and the four restrictions; M's `/proc/<M>/status` shows `NoNewPrivs: 1` and seccomp mode 2; every v4 P-MGR item (linger start, cpu, memory and pids delegation, `systemd-run --user --scope`, the runtime directory, the private socket's modes and peer check) passes under it; M's `UnitPath` equals the load path of §11.5 S-F |
| P-QUIESCE (v5 rows) | for the installed systemd version, S1-S6 by a source-level reading of its manager loop, job engine, D-Bus connection handling and signal handling, reviewed with the installed evidence (§16 step 8); and on a sacrificial attempt, each after A2 exits: (g) a transient timer A2 started is seen (Q4) until it is gone; (h) a unit A2 left waiting to restart is seen (Q3); (i) a signal A2 sent M just before exiting is seen pending (Q8) or its effect is seen after the barrier; (j) a request A2 wrote to M's private socket just before exiting is seen as a queued message or a foreign connection (Q5) or its effect is seen after the barrier; (k) after a passing classification and with no further input, M's units, jobs, cgroups, sockets and pending signals stay unchanged for a recorded period |
| P-CHAIN | on sacrificial journals, every consumer (W's join, W2, the conclusion, an export, an offline reader of the export) computes the same chain, head and committed set for: a torn record-bearing marker followed by its continuation; a torn close marker followed by a continuation (the record stays committed); a marker and its continuation both torn (the writer stops, and the record is not committed for any consumer); a complete marker whose `fsync` failed, followed by its continuation (the marker is RAW); a torn genesis followed by a genesis continuation; a create that left no file (a gap listed with an empty `files` list); two markers of one seq (branched; no writer appends); a W2 opening a journal whose head is an unconfirmed record-bearing marker (its first marker is a continuation that skips it); and export cuts and `raw_files` that list every raw file exactly once |
| P-PROTO | the selftest machines drive each v5 transition of Appendix B.4.4: `EARLY_REFUSAL` from every pre-hello check of each verb; `REFUSAL` after `HELLO_ACK` and in place of `PHASE_DONE`; a `STOP` before C's interruption point (`CHILD_REFUSAL`) and after it (`CHILD_START`, then `SIGTERM` to the selftest target); a failing spawn call (`SPAWN_FAILED`, `started: false`); a `STOP` before and after L's interruption point; `RELEASE_INTENT_RESULT` after the deadline (the window written first, the late result recorded) and never (release performed, durability-UNKNOWN); a failed export (`EXPORTED` with state `failed`); Option B's `RL_IDENTITY` present, missing and duplicated; and any message outside the machines is a channel failure. The release cases use a sacrificial copy of the window protocol on a sacrificial path |
| P-SEAL | `setup-identities.json` does not list itself; on a sacrificial copy of the installation that the operator prepares, never the real one, a changed byte of it makes `dispatch` and `seal-front` refuse before any mutation and `materialize` refuse when an adoption record exists; without one, `materialize` records `unadopted`, and the later `dispatch` refuses on the mismatch; a selftest only records the values |
| P-SR | S-R's classification and transition logic run against recorded synthetic observations and logs, as in P-SETUP (no account is created by a probe): each atom class in P, in each intermediate state, in E and in *other*; an atom in E whose `done` line is missing (resume skips it); a pattern with two atoms between states (S-R stops); a torn last log line (ignored; S-R's own log is new) and a malformed middle line (S-R stops). Helper tests: `step.py` with an injected short `os.write` completes the line or exits 3, and refuses to append after a torn line; `check_out.py` exits non-zero for a failing command, a mismatching or extra output, and a command path that is not absolute |
| P-IMAGE | images only: W and W2 look up the backing files through the search-only images directory and read their pinned identities; O and C get `EACCES` there and still pass every other mount check; each image root's `lost+found` matches its pin, and a second root-owned entry in an image root makes W refuse |

## 14. Resources, staged Gate 0 and images [corrections: W1-IMAGE-TREE; gap: resources-and-images]

Every derived number below was computed with actual MCP `jackal_exact`: v3's computations (reproduced by the sealed
gpt61-v3 review) are carried, and v4's new numbers are recorded in `v4-support/jackal.json`. Each result has status
`exact`, `formal` false, lane `rat`, and the non_claims "NOT formal-bounded: this lane carries no Lean-checked
certificate", "The epistemic class above is the STRONGEST claim this result supports", "exact rational arithmetic (not
yet checker-covered)". No consequence ceiling field was returned; the results are informational arithmetic only. Exact
is not formal-bounded. The "approx" figures are the tool's decimal display of the exact value. Full records:
`v3-support/jackal.json`, `v4-support/jackal.json` and Appendix C. v4 changes no allowance and no stage budget: its new
records (allocation descriptors, observer intents, recovery and release records, export manifests and freeze records,
the adoption record) are small control records counted under A_in, and each record is still exported at most once
(§15.3).

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
| A_in | retained inputs and messages: descriptors, lead module, observation inputs, front records, channel segments (headers and references, no bulk duplicate), role identities with module closures, F-captured W diagnostics | 134217728 | `128*2^20`, judgment. Largest comparable observed inputs: the v5 frame-review roster, 979762 bytes (`49133+602614+68556+250916+8543`); the base descriptors, 108768 (`1735+105491+1542`); lead module 8639 and START 2699 bytes (observed) |
| A_exp | export copies, each retained record at most once | 832564774 | `545393048+152953998+134217728` (A_rec + A_idf + A_in) |
| A_retry | partial primaries and retries, each record at most twice | 832564774 | same expression |
| A_fb | the fallback journal | 16777216 | `16*2^20` (fixed by design) |
| X | all W-1 retained additions: A_idf + A_in + A_exp + A_retry + A_fb | 1969078490 | `2*545393048+3*152953998+3*134217728+16777216`; the check, echoed as parsed `152953998+134217728+545393048+152953998+134217728+545393048+152953998+134217728+16777216-1969078490` (the tool flattened the submitted grouping parentheses), gives 0 |
| A_tmp | target temporaries (`TMPDIR`, `/tmp`, `/var/tmp`): not retained, peak use | 268435456 | `256*2^20`, judgment; no observation exists and v4.3 has no such term; the first observation can only raise it |
| A_jrnl | manager, sudo, PAM, journal and unit effects, per stage | 134217728 | `128*2^20`, judgment; the new identities are system ids, whose messages go to the system journal |
| A_install | installed frame: code plus original and relocated baselines | 115303191 | `3*38434397`; the 17 v5 frame members total 38434397 bytes (`13976+19614+922860+4986+5773785+3198141+26383551+4153+1974792+1467+5300+7869+4763+749+755+745+116891`, member sizes observed in `frame-inventory.json`) |
| A_homes | setup directories, lock, masks | 1048576 | `1*2^20`, judgment |
| A_setuprec | setup evidence (prestate, captures, installed listings, identities) | 16777216 | `16*2^20`, judgment |
| A_selftest | sacrificial selftest generations, probe records, sacrificial export | 67108864 | `64*2^20`, judgment |

### 14.3 Stage budgets and the rule

| Stage | Required (exact) | approx | JACKAL parsed input |
|---|---|---|---|
| before setup | 2027732564230/1397 | 1451490740.3221188 | `2*(115303191+1048576+16777216)+134217728+1468268019712/1397` (A_install + A_homes + A_setuprec, their full restore, A_jrnl, A_ambient) |
| before selftests | 1843272351744/1397 | 1319450502.3221188 | `2*67108864+134217728+1468268019712/1397` (A_selftest, its restore, A_jrnl, A_ambient) |
| before every `materialize` and every dispatch | 15368462701360/1397 | 11001047030.322119 | `2*(16777216+2242440646+545393048)+1468268019712/1397+2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728` |

The dispatch-stage W-1 addition is 4340810164 (parsed `2*(2*545393048+3*152953998+3*134217728+16777216)+268435456+134217728`:
X, its full restore, A_tmp, A_jrnl), and `15368462701360/1397-9304350902252/1397-4340810164` gives 0.

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

### 14.5 Images (only if S-1 option 3 is chosen)

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

**Layout with images (v4) [correction: W1-IMAGE-TREE].** The layout, anchors, routing and names are exactly those of
§3.3 and §3.4, which are the same with and without images. The work image is mounted at T_root
(`/var/lib/wlscratch/runs`); the records image is mounted at R_root (`/var/lib/wlscratch/runs/records`), that is,
inside T, on a mount point that is a directory of the work image. P_adm and partition contents are therefore on the
work image, and P_att, P_exp and P_ado on the records image, so target output cannot exhaust the space that frame
records need. Each bare mount point is root-owned, mode 0700 and empty (T_root's on the root filesystem, R_root's on
the work image), so W can neither write into a missing mount nor mistake one (§3.4's missing-mount checks run at every
writer invocation and every O and C stage). Each image root contains `lost+found` from `mkfs.ext4`, admitted only under §3.4's pinned special-entry rule. The mount
units `var-lib-wlscratch-runs.mount` and `var-lib-wlscratch-runs-records.mount` carry `Options=loop,nosuid,nodev,noexec`;
the records unit has `Requires=` and `After=` on the work unit; both are enabled through `local-fs.target` as their only
start source; there is no automount unit and no fstab line. A_tmp's places are not on the images.

**S-J, images (only if chosen; replaces step B 4 of S-B; every step logged as in §11.4).**
- J0: `need_absent /var/lib/wlscratch-images /var/lib/wlscratch/runs` and the two mount-unit paths.
- J1: `install -d -o root -g <W> -m 0710 /var/lib/wlscratch-images` (search for W only, so W and W2 can look up the
  image files' pinned identities by name; nobody but root can list or open them; the image files stay root:root 0600,
  J2).
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
A stop in S-J is reconciled by S-R J like any other script (§11.4).

### 14.6 Memory, CPU and caps

Unchanged from v5: `MemoryMax=8G`, `MemorySwapMax=0`, core 0/0, `-j2`, the 16777217 kB gate and the receipt
protocol. The new user manager and helpers use RAM (tmpfs under `/run/user/R`) and processes; this is not disk and is
not budgeted as disk.

## 15. Rollback, freeze/export and evidence [corrections: W1-SETUP-PROBES-ROLLBACK, W1-COMMIT-JOURNAL-EXPORT; gap: rollback-and-evidence]

### 15.1 Rollback order (operator; every step's before and after state captured raw)

1. **Revoke new launches first.** Preserve the bytes and sha256 of `/etc/sudoers.d/wlscratch-frame` in
   `/root/wlscratch-staging/rollback-<stamp>/`, remove it, run `visudo -c`. No new writer can start.
2. **Wait for and reconcile every pending and running participant before withdrawing anything else:** `SCAN-W` empty
   (including writers started before step 1); no `sudo` process naming a frame entry; `SCAN-GATE` empty; `SCAN-R` ⊆
   {M}; M's units equal to S_units and its job queue empty (`systemctl --user -M wlscratch-run@ list-units --all` and
   `list-jobs`, as root); no scope cgroup below `user@R.service` other than the manager's own. A live participant is
   waited for; killing one is a separate, recorded, explicit operator decision. Any UNKNOWN holds the rollback at this
   step.
3. **The shared window.** If it is reserved by a W-1 attempt and known-terminal ownership is uncertain, it is a hold:
   never force a release. If ownership is known terminal and the reserving front is gone, the operator resolves it
   explicitly and records the resolution; the frame never does.
4. Preserve and remove `/etc/sudoers.d/wlscratch-run` (or Option B's root rule); `visudo -c`.
5. `loginctl disable-linger wlscratch-run`, only after step 2 holds; verify `user@R.service` stopped and
   `/run/user/R` gone. Then preserve (bytes and sha256) and remove `/etc/systemd/system/user@<R>.service.d/50-wlscratch.conf`
   and its directory, `systemctl daemon-reload`, and verify that `systemctl show user@<R>.service -p PAMName` shows the
   vendor value again.
6. **Images, if used:** identify every start source first (the two mount units, `systemctl list-dependencies
   --reverse` of each, any automount unit, fstab: none expected); `systemctl disable` both units; verify that no process
   has a file open on them and that step 2 still holds; then stop the records unit first and the work unit second
   (unmount); verify that each is unmounted and that each bare mount point equals its setup identity (§11.7); preserve
   the unit files (bytes and sha256), remove them, `systemctl daemon-reload`, verify no remount. Keep the image files and
   record their sha256.
7. **Restore the exact approved home ACL (Option A):**
   (a) capture `getfacl -n -c -p /home/sicarii`, `getfacl -n -p /home/sicarii` and
   `stat -c '%a %u %g %d %i' /home/sicarii`; require byte equality with `home-acl.post.expected`, `home-acl.post.dump`
   and the post-setup `stat` capture (a difference is a concurrent change: stop and report, never overwrite it blindly);
   (b) `setfacl -P --test --restore="$st/home-acl.pre.dump"`, output retained;
   (c) `setfacl -P --restore="$st/home-acl.pre.dump"`: the headed P21 dump restores the owner and group of its
   `# owner:` and `# group:` lines, sets the setuid, setgid and sticky bits from its `# flags:` line or clears them when
   there is none, and restores the entries and the mask (`setfacl(1)`, `--restore`, read from the installed manual);
   when P21 showed no extended ACL, the dump holds only the base entries, which the restore re-applies;
   (d) capture again and require byte equality of `getfacl -n -c -p` with `home-acl.pre.expected`, of `getfacl -n -p`
   with `home-acl.pre.dump`, and of `stat` with P21's capture.
   Every capture is retained. The comparison text (`-c`) is never used as restore input.
8. Lock and expire both accounts (`usermod -L -e 1`); keep them, so evidence ownership keeps its meaning. Then preserve
   and remove the sshd drop-in, `sshd -t`, reload.
9. Keep as evidence: `/var/lib/wlscratch` (generations, records and exports), `/var/lib/wlscratch-run` (including
   masks), `/opt/wlscratch`, `/root/wlscratch-staging` (including the step logs and every rollback capture) and every
   capture.

The rollback steps are logged like setup steps (§11.4). A stopped rollback step is reconciled by the same rules, and
nothing is called restored without its equality capture.

### 15.2 What rollback leaves

Remaining: the two locked and expired accounts and the three groups (the two user-private groups and
`wlscratch-gate`), with their numbers; their `passwd`, `group`, `shadow` and `gshadow` entries; every file under
`/var/lib/wlscratch*`, `/opt/wlscratch` and `/root/wlscratch-staging`; images, if any; journal entries; and, if step 7
stopped on a concurrent change, the home ACL as found (reported). Removed: both sudoers files, the sshd drop-in, the
user-manager drop-in, the linger file, the mount units. Not restored: a pristine pre-setup system.

### 15.3 Freeze and export [correction: W1-COMMIT-JOURNAL-EXPORT]

**Export primitive** (every copy in P_exp or in an adoption export):
1. create the copy create-only (`O_CREAT|O_EXCL|O_NOFOLLOW`) with mode 0600 in an export directory, write its bytes,
   `fsync`;
2. set the export access ACL with `fsetxattr` on the held descriptor;
3. read back on the same descriptor: `fgetxattr` equals the encoded ACL; `fstat` shows a regular file, one link,
   owner W, group W, the source's size and `st_mode` 0640 (the mask in the group bits); the bytes, re-read, have the
   source record's committed sha256;
4. `fsync` the file and its directory; entry join; `verify_location`;
5. only then commit the export marker (kind `export`) in the journal, with `record` = `{path, sha256, bytes, mode:
   0640, acl_sha256}`: the final values.

Export directories are created 0700, given their ACL and read back (`st_mode` 0750) before any entry is created in
them; their identities and ACL digests are listed in the increment's manifest. Every consumer of an export copy (F,
reviewers, the vault) compares with these final values, never with 0600.

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
  state `failed`.
- After the copies, the increment's `manifest.json` (`wlscratch-export-v2`: per entry the export path, source path,
  sha256, bytes, final mode, `acl_sha256`, source marker digest and state ∈ {`committed`, `fallback`, `torn`, `raw`}, and
  the export directories' identities) and `freeze.json` (`wlscratch-freeze-v3`: increment number, cut c_n, slot range,
  the previous increment's freeze-marker digest, the digest of every export marker committed for this increment, the
  manifest's sha256, `raw_files`, channel heads, boot id, time) are written with the export primitive and committed.
  `raw_files` lists every RAW file of J's `commits/` and every uncommitted record file that appeared after the cut and
  that neither an earlier increment nor this manifest listed, so every raw file is listed exactly once. The export
  markers of increment n, its freeze marker and the close markers that confirm them have seq > c_n.seq, so the next
  increment exports them. The last increment's export markers are listed by digest in its own freeze record; only its
  freeze marker and the close marker that confirms it are never exported: the freeze marker's digest goes to F in
  `EXPORTED` and `FINAL` and is printed, and the originals stay in the protected journal.
- **Who makes increments.** For an attempt: W at M11 or D19 (increment 0, after `final-status.json`), then each W2 at
  the end of its work (the next increment), which therefore exports the later evidence: W's late records if any, W2's
  recovery and release records, the front terminal record and their markers. For a generation: one export,
  `export/generation/`, of the generation journal with the materialization marker as its cut; that journal never grows
  again, so this export is complete and final; its export markers live in A0's attempt journal and are exported by A0's
  increment 0. For an adoption: each `adopt` invocation makes the next increment of the adoption journal, in
  `adoption-<I>/export/inc-<n>/`.
- **Accounting.** Cuts are disjoint, so every record and marker is exported at most once across all increments, and
  A_exp's "each retained record at most once" (§14.2) is unchanged.
- F re-reads every copy of each increment through its ACL, compares it with the manifest's final values, and keeps each
  freeze-marker digest from `EXPORTED` and `FINAL`.
- **What "frozen" means:** create-only, W-exclusive, no verb that modifies or deletes, digests in a hash-linked
  journal. **Limits:** root, or W running changed code, could still alter them; no immutable attribute is set (that
  needs `CAP_LINUX_IMMUTABLE`).
- Lead copies of exports are mutable evidence records, not authentic producer custody. A project-vault transfer of
  exports (§8.5) is backup, not authenticity.

### 15.4 Evidence classes (all retained raw)

Pre- and post-setup captures with digests, the step logs and every S-R capture; `passwd`, `group`, `shadow` (first
character only) and `gshadow` lines; `getfacl`/`stat` outputs, including the headed restore dumps and the comparison
texts; sudoers, sshd and user-manager drop-in bytes; `findmnt`, kernel settings, linger state; installed-inventory
comparisons; role identities and module closures; selftest and probe records with raw errnos; every committed record
and marker, every retry, every fallback allocation descriptor and slot (VALID decoded, TORN raw), every raw uncommitted
record, channel segment, wait, participant, scope and scan record (including the quiescence and lease results); launch
and observer intents, `spawn-ok`, the conclusion, stream finality, final status and the release records
(`release-intent`, `window-release`, `release-withheld`, `release-not-owner`, `release-failure`) from W and from each
W2; recovery records; front terminal records; export increments with their manifests and freeze records; the adoption
record and its exports; F's console output as preserved in the lead transcript (neither durable nor frame custody);
rollback captures. **Limits:** hashes of W-owned files describe files that root or W could change; copies are evidence
records; none of this is producer authenticity, proof or acceptance.

## 16. Setup, verification and adoption order

1. Actual gpt-6.1-sol review of this v4 design.
2. Frame v6-W1 code implemented, frozen in SOURCE_FRAME (members 0644, directories 0755; the inventory records
   `install_root` and `source_frame`) and reviewed as code by actual gpt-6.1-sol, the review sealed in
   `<SOURCE_FRAME>/review/gpt61-v1/` (REVIEW): front (`adopt`, `materialize`, `dispatch`), writer (the same verbs,
   `seal-front` in both modes, `selftest`), launcher, child, observer, Option B's RL if pursued, the final pass with
   excluded-leaf keys and the lease test, the channels and their state machines, commits, journals, the fallback
   journal and exports, the scans with quiescence, recovery, the selftest verbs and probes, and the helpers `absent.py`
   and `step.py`.
3. Concrete setup inventory (fixed numbers; filled prestate P1-P24; exact script texts and digests, with S-J if images
   are chosen and S-R; expected ACL texts and restore dumps; mask list; sudoers, sshd and user-manager drop-in bytes;
   the Option A or B text), reviewed by actual gpt-6.1-sol.
4. Gate 0, setup stage, on a fresh reading.
5. Operator approval of the concrete setup (reserved authority).
6. The operator runs, or explicitly authorizes, S-0 to S-I (and S-J if images are chosen); S-R only after a stopped
   script, by explicit operator choice.
7. Gate 0, selftest stage; lead verification (§11.6), selftests and probes (§13), including P-MGR, P-QUIESCE and
   P-ENOSPC.
8. Installed-identity, baseline (including S_units and S_socks) and probe evidence reviewed by actual gpt-6.1-sol, the
   review sealed in `<SOURCE_FRAME>/review/installed-gpt61-v1/` (INSTALLED_REVIEW).
9. Gate 0 with the materialize/dispatch-stage expression (procedural); then `front.py adopt …`: W commits the fresh
   installed-frame adoption record at `/var/lib/wlscratch/runs/records/adoption-<I>/lead-adoption.json` (§4.6), with
   the fresh lead observation `scratch-adopt` (v5 `adopt` semantics).
10. Gate 0, dispatch stage; only then `materialize` and dispatch, each under fresh original admission.

No step authorizes the next by inference. This refines v3's order (closed as W1-SETUP-ORDER) by naming the adoption's
writer, destination and review inputs, without changing its substance.

## 17. Placement of every v5 mechanism

| v5 mechanism (frozen `scratch.py`) | W-1 placement | Change, and why it preserves the original |
|---|---|---|
| `Dir` anchoring, `verify_location`, `child(create=True)` authentication, `write_bytes`/`write_json`/`open_stream`/`set_mode` (S:144-358) | W and W2 for every frame mutation; C and O for anchored reads; F for anchored input and window reads | none in semantics; the location chain is now protected (§3.4, §4.5) |
| `stat_key`, `observe_tree` (v6 final pass), `read_observed`, `read_prefix`, `read_files` | C and O full walks; W writer-owned walks (partition roots opaque); F base-tree and transcript reads | `observe_tree` also returns excluded-leaf keys (§4.5); the lease test rides on the same walk (§9.4) |
| `retain`, `guarded`, `read_record`, `last_resort`, `retain_observation` (S:375-436, 1109-1128) | W and W2 | commit markers, journals with committed chains, the fallback journal with an immutable allocation descriptor and append-only slots, consumer precedence, durability-UNKNOWN (§10); the compact equal-record form unchanged |
| `exec_verified`, frame inventory, `frame_admitted` (S:587-863) | installed members checked by W, L, C, O; review, installed-review, rollout and transcript joins by F; the adoption record's structural joins by W | `install_root` replaces `frame`; the adoption record is W's protected record (§4.6); F's joins at v5 trust (R2) |
| `adopt`, `validate_adoption_observation`, `rollout_join`, `review_profile_problems` (S:687-837) | F (lead-context checks), W (structural re-verification, create-only commit) | destination moved from the frame's review directory into the protected tree; every v5 join kept; installed-review joins added (§4.6) |
| `materialize` recipe (S:959-1049), `expected_source`, `overlay_rules` | W `materialize` | streamed verified bytes; partition roots pre-created (§6.4) |
| `command()` allowlist (S:1054-1070) | W, re-derived by C | unchanged |
| `specifications()` (S:1073-1106) | W builds, C verifies | relocation table (§8.4) |
| `identities()` (S:1131-1153) | O (`parent`, `after`), C (`child`) in the target context; F's runtime and manager in the real context | baselines per context (§8.1, §8.4) |
| `sample()` (S:1156-1179) | F half (sibling units in `sicarii`'s manager, `storage_status.py`); helper half (heavy processes, meminfo, M's units) | split by authority; same checks |
| `threshold_receipts`, `receipt_line`, `memory_gate` (S:1186-1248) | W issues and verifies; F forwards from the inbox | unchanged constants and deadlines; "through original stdin" = W's stdin channel |
| `window_locked`, `window_read`, `window_write`, `reserve`, `owns_window`, `release` (S:1253-1341) | F | unchanged protocol; attempt records committed by the serving writer under F's lock in the same order; the release record's durability does not gate the window write (§9.4, supplied ruling) |
| `ancestors`, `processes_naming`, `owned_terminal` (S:1346-1415) | O and C scans with quiescence and the lease test; F's world-readable scans; W2's recovery rounds | complete classification at fixed points; no inference from missing records (§9.4, §9.7) |
| `final_stream_sync` (S:1420-1437) | W after terminal | unchanged, followed by the stream finality test (§10.6) |
| `admission()` (S:1440-1448) | split per stage among F, W, O and C | the same checks (Appendix D) |
| `spawn`, `wait_blocked`, `pending_handled`, `raising_handler` (S:1469-1517) | every waiting role | H-S1/H-M3 synchronous handling; `STOP` down the channels |
| `started_by_dispatch` (S:1520-1527) | W: `SUDO_*` plus `HELLO_ACK` plus stdio inode join; W2: front-process triple | the invoker is bound by kernel identities instead of a parent command line |
| `refusal_record`, `run`, `conclude` (S:1530-1765) | W (`dispatch`), F (release), O (terminal observations), W2 (recovery) | N13 recomputation; `final-status.json` |
| `child` (S:1768-1896) | C | §9.3 C1-C12, over a direct channel to W |
| `dispatch` (S:1899-1988) | F | inbox answers over the channel; S1 wait via W2; N14 exit |
| `verify_materialization` placement: materialize, parent and child admission, immediately before spawn, conclusion | W at M8; O at the parent stage and W's writer half; C at the child stage and as the final pass; O and W at the conclusion | same placements, now split by authority |
| launch seal in argv (S:1570-1594, 1783-1817) | L's and C's argv carry the `launch.json` and `admission.json` sha256; C verifies the bytes delivered over its channel | V4-B03 kept |

## 18. Per-correction and per-gap status (the author's assessment, for the independent reviewer to judge)

"CLOSED-AT-SPEC-LEVEL" is this author's claim that the specification text now covers what the item asks for. It is
not closure, not executed evidence and not acceptance; the gpt61-v4 review states that it does not adopt such claims
by repetition. "CLOSED (gpt61-v4), carried" marks items that review closed; v5 keeps their text as §0.3 states. Every
original obligation, V5-B01, V5-B02 and Gate 0 stay OPEN regardless.

### 18.1 The gpt61-v4 review's required W-1 corrections (verbatim) and the author's assessment

Each correction is quoted verbatim from `review.json` (`required_corrections`).

1. **W1-CUSTODY-CLOSURE.**
   > Replace the unsupported all-directories-remain-0700/only-R-or-GATE-can-mutate argument with a complete custody mechanism for target-modifiable modes/ACLs and surviving non-writable references, including queued references and future write opens. Preserve all original accepted actions/cases. Make the promised every-process-starting-unit mask coverage agree with S-F's enabled-closure inventory, and specify the stronger asynchronous/buffered-work quiescence property needed beyond serialized API dispatch. Retain UNKNOWN and the installed-premise verification requirements; do not convert any premise or finite control into an exception.

   v5: §9.8 (K1-K7); §9.4 (SCAN-WCLOSED, M-QUIESCENT Q1-Q8, S1-S6, the absorption lemma, arguments (a)-(c)); §9.3
   C7-C11; §11.5 S-F (one mask rule, the hardened drop-in); §13.1; AM-01 to AM-05, AM-08, AM-09, AM-12 to AM-17 and
   AM-21 to AM-23. **Author's assessment: CLOSED-AT-SPEC-LEVEL, conditional on the premises of §9.8 K7** (L1, K-PERM,
   K-CHMOD, H1-H3, S1-S6, M-PAM), each kept with its probe and its redesign consequence; no premise or finite control
   becomes an exception, and UNKNOWN stays UNKNOWN. Still needed as future evidence: the v6-W1 code (revocation, W-CLOSED
   check, both filters, scans) and its review; the hardened drop-in and the mask list in the reviewed concrete
   inventory; P-WCLOSED, P-SETID, P-MGR and P-QUIESCE, with the source-level reading of S1-S6; the reviewed S_units and
   S_socks.
2. **W1-PROTOCOL-FAILURE-STATES.**
   > Complete and reconcile exact per-verb states/keysets and dispositions: early materialize/adopt refusals; failure or STOP after spawn permission but before CHILD_START; failed spawn reporting without a fabricated start/refusal; the release-intent timeout and late responses; verb-specific W/F success for materialize/adopt/seal-front; and Option B's RL identity message. No missing start record may imply no target, and no archival timeout may add a window-release gate.

   v5: Appendix B.4 (`START` and `EARLY_REFUSAL`, the `REFUSAL` positions, W↔C `SPAWN` and `FAILED`, W↔L `GO`,
   `RELEASE`, `EXPORTED`, `RL_IDENTITY`); §9.3 (G3, G6, C8, C11, C12, C's refusals); §9.4's release procedure; §9.5;
   §10.7; Appendix B.3; AM-10, AM-13, AM-19 and AM-20. **Author's assessment: CLOSED-AT-SPEC-LEVEL.** Still needed:
   the code implementing the machines and keysets, and its review; P-PROTO, P-TERM, P-LAUNCH.
3. **W1-JOURNAL-CONTINUATION.**
   > Give one unambiguous reader/writer/export recovery rule for torn or unlinked markers and later appends: a marker cannot both end the committed chain and be bypassed by a later marker that is treated as committed. Define gaps, first-marker failures, head selection, branches and prefix cuts consistently for every consumer, preserving all raw files and forbidding failed primaries from parsed/success credit.

   v5: §10.2; AM-30 (§15.3); Appendix B.3 (`wlscratch-commit-v2`, `wlscratch-freeze-v3`); Appendix B.4 (`EXPORTED`).
   **Author's assessment: CLOSED-AT-SPEC-LEVEL.** Still needed: the code and its review; P-CHAIN and P-COMMIT; P-ENOSPC
   before any claim of durability under allocation failure.
4. **W1-SETUP-IDENTITY.**
   > Define a constructible non-circular setup identity seal. setup-identities.json cannot be required to store its own final size/digest as an ordinary pinned member without a separate construction/verification rule. Bind its final bytes externally through the reviewed installed/adoption identity, or specify an equally strong non-circular scheme; preserve immutable versus intentionally mutable field checks.

   v5: AM-24 and AM-27 (§11.7, the seal); AM-11 (D3); §11.5 S-H and S-I; Appendix B.3 (`generation.json`,
   `lead-adoption.json`). **Author's assessment: CLOSED-AT-SPEC-LEVEL.** Still needed: the concrete inventory and its
   review; the S-I seal capture; the installed-evidence review recording S; P-SEAL.
5. **W1-SETUP-RECONCILIATION.**
   > Make S-R resume agree with observed poststate when a mutation completed but its done record did not: do not rerun create-only account/group/mask steps blindly. Specify complete/partial multi-object steps and their checked resume/reverse transitions. Make step.py check/write the complete log line or fail, and specify malformed/torn log handling; preserve root-reviewed staging, explicit operator choice and equality captures without a new gate. Replace the blanket sh -e pipeline-failure claim with checked producer/pipeline status handling; errexit alone does not observe every pipeline component.

   v5: §11.4 (status rules, atoms, S-R) and §11.5 (`step.py`, `check_out.py`, the scripts, the atom classes).
   **Author's assessment: CLOSED-AT-SPEC-LEVEL (templates; the exact script bytes, atom tables and captures come with
   the concrete inventory, as v4's templates did).** Still needed: the concrete inventory and its review; P-SR and
   P-SETUP; the operator's setup with S-I; S-R records if a script stops.
6. **W1-IMAGE-OBSERVATION.**
   > Make every W/W2 backing-file identity check possible with the actual setup permissions, while preserving image custody and the same intended tree. Reconcile root-owned lost+found with the categorical W-owned-entry/name validation and growing-tree identity rules. Retain missing-mount, boot-local device observation, geometry and full executable/native compatibility requirements.

   v5: AM-06 and AM-07 (§3.4); AM-18 (§6.3); AM-25 and AM-26 (§11.7); AM-28 and AM-29 (§14.5). The missing-mount
   checks, the boot-local loop device and mount ID, the geometry measurement and the full executable and native
   compatibility requirements are unchanged. **Author's assessment: CLOSED-AT-SPEC-LEVEL.** Still needed: measured
   geometry on a sacrificial image; the image inventory and its review; P-IMAGE and P-MOUNT.

PKG-V7-AUTHOR-RECORDS concerns the lead's package text and is not in W-1's scope.

### 18.2 Prior corrections, as the gpt61-v4 review ruled on them

| Prior correction | gpt61-v4 | v5 | Author's assessment |
|---|---|---|---|
| W1-GENERATION-PROTOCOL | NOT_CLOSED (R2) | through W1-PROTOCOL-FAILURE-STATES: Appendix B.4, §9.3, §10.7, AM-10 | CLOSED-AT-SPEC-LEVEL |
| W1-COMMIT-JOURNAL-EXPORT | NOT_CLOSED (R3) | through W1-JOURNAL-CONTINUATION: §10.2, AM-30 | CLOSED-AT-SPEC-LEVEL |
| W1-TERMINAL-CUSTODY | NOT_CLOSED (R1) | through W1-CUSTODY-CLOSURE: §9.8, §9.4, AM-14 | CLOSED-AT-SPEC-LEVEL, conditional as in §18.1 |
| W1-DURABILITY-RELEASE | NOT_CLOSED (R2's release timing) | §9.4's release procedure, Appendix B.4.4 `RELEASE`, §9.5 | CLOSED-AT-SPEC-LEVEL |
| W1-SETUP-PROBES-ROLLBACK | NOT_CLOSED (R4, R5) | §11.4, §11.5, AM-24 to AM-27, §13.1 | CLOSED-AT-SPEC-LEVEL (templates) |
| W1-IMAGE-TREE | NOT_CLOSED (R6) | AM-06, AM-07, AM-25, AM-26, AM-28, AM-29 | CLOSED-AT-SPEC-LEVEL |
| W1-CUSTODY | NOT_CLOSED | through R1, R2 and R6 | CLOSED-AT-SPEC-LEVEL, conditional as in §18.1 |
| W1-SETUP | NOT_CLOSED | through R4 and R5 | CLOSED-AT-SPEC-LEVEL (templates) |
| W1-LIFETIME-ROLLBACK | NOT_CLOSED | through R2's release timing, R3 and R5 | CLOSED-AT-SPEC-LEVEL |
| PKG-SUPERVISION-RECORD | NOT_CLOSED | the lead's package | not in W-1's scope |
| W1-RESOURCES | CLOSED | §14 carried; no allowance or stage budget changed (§0.6) | CLOSED (gpt61-v4), carried |
| PKG-V6-OPERATOR-TEXT, OD2-CONSEQUENCES, PKG-V5-FACTS, PKG-CLOSURE-STATUS | CLOSED | package items | not in W-1's scope |

### 18.3 The section-3 gaps

| Gap | gpt61-v4 | v5 | Author's assessment |
|---|---|---|---|
| generation-order | NOT_CLOSED | AM-10 to AM-13, Appendix B.4 | CLOSED-AT-SPEC-LEVEL |
| lease-and-writer-authority | CLOSED | §5.1, §5.2, §9.7 and §3.4's authority paragraph carried byte-for-byte; v5 adds no writer mutation (its new records are new names under `attempts/<A>/**`, §5.2) | CLOSED (gpt61-v4), carried |
| per-entry-modes-acls | CLOSED | §6.1, §6.2 and the export primitive carried; §6.3 amended only in the partition-contents row (R1) and the image rows (R6) | CLOSED (gpt61-v4), carried |
| channel-and-dumpability | NOT_CLOSED | AM-19, AM-20, Appendix B.4 | CLOSED-AT-SPEC-LEVEL |
| prestate-and-installation | NOT_CLOSED | §11.4, §11.5, AM-24 to AM-27 | CLOSED-AT-SPEC-LEVEL (templates) |
| exposure-options | CLOSED | §12 carried; Option B's identity frame integrated (§7.3, Appendix B.4) | CLOSED (gpt61-v4), carried |
| fresh-identities-and-vault | CLOSED | §8 carried | CLOSED (gpt61-v4), carried |
| denial-probes | CLOSED | §13 carried byte-for-byte; v5 adds §13.1 | CLOSED (gpt61-v4), carried |
| resources-and-images | CLOSED | §14.1-§14.4 and §14.6 carried; §14.5 amended only at J1 and one sentence | CLOSED (gpt61-v4), carried |
| commits-and-durable-channel | NOT_CLOSED | §10.2, AM-30 | CLOSED-AT-SPEC-LEVEL |
| participants-and-recovery | NOT_CLOSED | §9.3, §9.4, §9.8 | CLOSED-AT-SPEC-LEVEL, conditional as in §18.1 |
| rollback-and-evidence | NOT_CLOSED | §11.4 (S-R), §10.2, AM-30 | CLOSED-AT-SPEC-LEVEL |

### 18.4 The original W-1 subgaps

| Subgap | gpt61-v4 | v5 | Author's assessment |
|---|---|---|---|
| W1-CUSTODY | NOT_CLOSED | §9.8, §9.4, AM-06, AM-07, Appendix B.4 | CLOSED-AT-SPEC-LEVEL, conditional as in §18.1 |
| W1-FINAL-PASS | CLOSED | §4.5 items 1-3 untouched; W-CLOSED added in the same walk (AM-14) | CLOSED (gpt61-v4), carried |
| W1-CLOSURE | NOT_CLOSED | §10.7, Appendix B.4, §11.7's seal | CLOSED-AT-SPEC-LEVEL |
| W1-CHANNEL | NOT_CLOSED | Appendix B.4, AM-19, AM-20 | CLOSED-AT-SPEC-LEVEL |
| W1-WRITE-AUTHORITY | CLOSED | §3.4's authority paragraph, §5.2, §9.7 carried | CLOSED (gpt61-v4), carried |
| W1-READ-ACCESS | CLOSED | carried | CLOSED (gpt61-v4), carried |
| W1-READ-EXPOSURE | CLOSED | §12 carried; `RL_IDENTITY` in Appendix B.4 | CLOSED (gpt61-v4), carried |
| W1-PREFLIGHT-IDENTITY | CLOSED | §8 carried | CLOSED (gpt61-v4), carried |
| W1-SETUP-PRESTATE | CLOSED | §11.1-§11.3 carried; `absent.py` byte-identical; §11.7's v4 classes kept | CLOSED (gpt61-v4), carried |
| W1-SETUP-ORDER | CLOSED | §16 carried byte-for-byte (read with §0.6) | CLOSED (gpt61-v4), carried |
| W1-SETUP-EXACTNESS | NOT_CLOSED | §11.4, §11.5, §11.7's seal | CLOSED-AT-SPEC-LEVEL (templates) |
| W1-IMAGE-GEOMETRY | CLOSED | §14.5's geometry text untouched | CLOSED (gpt61-v4), carried |
| W1-IMAGE-COMPATIBILITY | CLOSED | §14.5's compatibility text untouched | CLOSED (gpt61-v4), carried |
| W1-VERIFICATION-PROBES | CLOSED | §13 carried; §13.1 added | CLOSED (gpt61-v4), carried |
| W1-FAILURE-LEASE | NOT_CLOSED | §9.4's release procedure, §9.8, Appendix B.4 | CLOSED-AT-SPEC-LEVEL, conditional as in §18.1 |
| W1-FAILURE-RECORDS | NOT_CLOSED | §10.2 | CLOSED-AT-SPEC-LEVEL |
| W1-REBOOT-RECOVERY | NOT_CLOSED | §10.2's reader rule, §11.7's seal, AM-06, AM-07 | CLOSED-AT-SPEC-LEVEL |
| W1-ROLLBACK | NOT_CLOSED | §11.4's S-R, applied to §15.1's steps | CLOSED-AT-SPEC-LEVEL |
| W1-EVIDENCE | NOT_CLOSED | §10.2, AM-30 | CLOSED-AT-SPEC-LEVEL |
| W1-NONCLAIMS | CLOSED | header, §20 | CLOSED (gpt61-v4), carried |

The review's item-3 note that `sh -e` does not observe non-last pipeline commands is answered in §11.4; its list of
remaining premises is §9.8 K7 (and §18.6).

### 18.5 Change map (every v4 unit, with its identity)

Units as §0.1 defines them; lines, sizes (bytes) and sha256 values were computed from the v4 file by a read-only
script on 2026-10-05. Codes: CC W1-CUSTODY-CLOSURE, PF W1-PROTOCOL-FAILURE-STATES, JC W1-JOURNAL-CONTINUATION, SI
W1-SETUP-IDENTITY, SR W1-SETUP-RECONCILIATION, IO W1-IMAGE-OBSERVATION. A CARRIED unit is v5 text byte for byte.

| v4 unit | v4 lines | bytes | sha256 | v5 status | Correction (amendments) |
|---|---|---|---|---|---|
| title | 1-51 | 4465 | `be7f2fa75e717a319536cfdbb076ab39dc9329eb9875dbe548700a618209178c` | REPLACED | all |
| 0 | 52-117 | 6185 | `6f07b6930a05c92dc884edd89a4e4d7180822322d1d6323a1a42e089979bf826` | REPLACED | all |
| 1 | 118-159 | 3156 | `2ae9da8b3dc5177eb189805c8f7fdc48e4908a2204fb68a6b4be0b5118aa0dac` | CARRIED | — |
| 2 | 160-161 | 63 | `35f6eb75cbc9b074ead5488fca9693875386deb826fbd0374020398a83887683` | CARRIED | — |
| 2.1 | 162-190 | 2708 | `6cc93137cbbd64702c98911bf7836ef03bc0c9cf88ccc237fd4aff9cbca91538` | AMENDED | CC (AM-01..03) |
| 2.2 | 191-198 | 582 | `0bd0f3c4f134ef27bc917b88222b83f93d615e28a7f33367af0d32f16a568a88` | CARRIED | — |
| 2.3 | 199-218 | 1910 | `5f9e1ef7a6329d7bacd127fa3f56b0aedee57b914a8f9fd599154ad0120d3820` | CARRIED | — |
| 2.4 | 219-257 | 3867 | `5ec12048d6b477c6dd11e4b84e46c925b816923b09b595d70896ebc2c927d960` | AMENDED | CC (AM-04) |
| 3 | 258-259 | 39 | `5510e891fd324593657d164471cb63078bbc71af4f71c2da3fc35163ae8c2ed0` | CARRIED | — |
| 3.1 | 260-275 | 1257 | `f9c9591dda30db333f3ff9de5018f53e6f5e4debb6f60934210e28352c0da597` | CARRIED | — |
| 3.2 | 276-298 | 2420 | `cba76434f42a6d74a25b1c40852e99713c93448c05e9ae5ce7a2508d74d46a50` | AMENDED | CC (AM-05) |
| 3.3 | 299-337 | 3006 | `67c0667a5d73b7cc18bbdb63ee86e2947966b5579b00e5e0d197fbf78007f411` | CARRIED | — |
| 3.4 | 338-395 | 5209 | `189555bcd2871e8079664b2f4912707766df44651ca8b232490629f83ebf0cd7` | AMENDED | IO (AM-06, AM-07) |
| 4 | 396-397 | 106 | `030cba113f70fd51a55fba2cdbacef1d4bebdd0fa2b0813f0a7f935356beaa45` | CARRIED | — |
| 4.1 | 398-424 | 2238 | `6ee8d38cae54884b9a80c7c476666769e7e88e0020c710a302d1fd4e17245e8c` | AMENDED | CC (AM-08, AM-09) |
| 4.2 | 425-568 | 13031 | `02d3a57199ef7d2b76933e67e617c113598677a3dc560769c203c4297828b3d1` | AMENDED | PF, SI, CC (AM-10..12) |
| 4.3 | 569-632 | 6179 | `07d3b82b34620a62bf38a1d69ffdf0660c1e724975fc126379a2a43159f4e4da` | AMENDED | CC, PF (AM-13) |
| 4.4 | 633-658 | 2451 | `eb572f6edb96f31e7bf59a9d8176ed06a37de4f96282533d86a1d70d7d31a59c` | CARRIED | — |
| 4.5 | 659-700 | 3669 | `1c71c054894b03e916e18184f58f84ea37a37330e48f4ad4ae6ab4b9190c1254` | AMENDED | CC (AM-14) |
| 4.6 | 701-765 | 5877 | `00b3ed65328eb21773f171bf89852ac17c227e4c242c254aa4e2bc5c739eb234` | CARRIED | — |
| 5 | 766-767 | 137 | `46adbb0dd725d4f1ca5f142a684061fafc17e2c5165b6da45647a41585de9bab` | CARRIED | — |
| 5.1 | 768-795 | 2284 | `e0bc923e20b24b36609ff4d44f5a354e999dcd57c67793c398d1890d68c14b97` | CARRIED | — |
| 5.2 | 796-824 | 3387 | `a62194774d5de67fb65136c7d7adf0bbf51ab7b7f2b1ca78a89c871cc20c0d12` | CARRIED | — |
| 5.3 | 825-847 | 4984 | `293faf34fc244d9bbfc727ff88234e9f7664520423dbba8d552701d2f6e1799b` | AMENDED | CC (AM-15, AM-16) |
| 5.4 | 848-854 | 478 | `debd77ac854c1a74be9913a849254ef55cff1e9f0adc2553f42431b3167eee6a` | CARRIED | — |
| 6 | 855-856 | 144 | `6a852dcafc48edb984b90136498474c97f6f0348b8e6541fe33b803af9034fd3` | CARRIED | — |
| 6.1 | 857-875 | 1485 | `dec415263fdf543ce1d47b1039e29c82cb17785eb6401b6a30d4f5a6065311e8` | CARRIED | — |
| 6.2 | 876-892 | 1360 | `630d79f31755b6b9e03fedccb984ab0e63f7ee5f2d2d72e996bdaa7614638971` | CARRIED | — |
| 6.3 | 893-927 | 3369 | `083b1b6b352a529a880f822e927b1dc0774e6c446cf9a41877f78ac540dba255` | AMENDED | CC, IO (AM-17, AM-18) |
| 6.4 | 928-955 | 2736 | `1ccb9a123c91616c1b68fb74985ecf9d39b85af9c7878add3eaf434ebd4fa731` | CARRIED | — |
| 6.5 | 956-984 | 2432 | `11f91ae0420504882f20f6f44f39f6bf17cf5c809633a3a1349ba4f41663f9d0` | CARRIED | — |
| 7 | 985-986 | 113 | `8ab0b34614a172ffb23cde8314d7bef25492c58858feabd1d30e543cde17fbae` | CARRIED | — |
| 7.1 | 987-1000 | 1716 | `82f112911b4b63b7bc8a568ad60586cbe980ac67fde2354b12d8dd54c7897ca0` | AMENDED | PF (AM-19) |
| 7.2 | 1001-1023 | 2191 | `7faec7003ad60f3723bd527d117099d1c40615466ed7acd274903c19a54d8047` | CARRIED | — |
| 7.3 | 1024-1046 | 2087 | `d00b62901e717d27e39b9dc8b7a11675cfdb1fbef17eded6971321998048af84` | AMENDED | PF (AM-20) |
| 7.4 | 1047-1060 | 1131 | `66f9582ac696d0efbf60ec1e3ff0f29f7f484f24093b667798f983ee0a9a9a0d` | CARRIED | — |
| 7.5 | 1061-1076 | 2205 | `7a1a529a70e8da31c3b00decf7ae064fbd28dcb47db229103604db26ab1b9398` | CARRIED | — |
| 7.6 | 1077-1086 | 826 | `da3dc6642e8c8b1bf407a522e929faa1997c00c2b74738d67783089debc1b34a` | CARRIED | — |
| 7.7 | 1087-1107 | 2099 | `9a35135a6ed5b397783b23a914eabe300e8d9d2caddc9281bcc9c0e6b9f34763` | CARRIED | — |
| 8 | 1108-1109 | 119 | `a61d10425836c77bd06805b89c361fee0f7b18967c522ffed965fe9f7f7d3d05` | CARRIED | — |
| 8.1 | 1110-1133 | 2730 | `81091a55b4279f4cfded6b1484f9743d32c887588558e169935c2d241fec95c7` | CARRIED | — |
| 8.2 | 1134-1145 | 1030 | `309b19cccb33bc3a0a2d9863e13e869de1e42a9ae055ede4b84a47ec7fde5705` | CARRIED | — |
| 8.3 | 1146-1162 | 1496 | `209bd4d33569f07b733c3d9df9bb3d3955777b2dc0584151b71adaeb3369c0cc` | CARRIED | — |
| 8.4 | 1163-1202 | 3623 | `309db868a9c2204102a55fdfb86dd89b881b8610b1c3b8d097da57c0a4cf4402` | CARRIED | — |
| 8.5 | 1203-1215 | 1072 | `d651794d2e2a2f64dc0256d765b1dfb3f56cb7316f27be7fa0f7cd17d386d859` | CARRIED | — |
| 8.6 | 1216-1237 | 2023 | `3ec9d7f237addb503a8f3a90434741ae57e7386139ae3ab5b5a06271ae25dd1f` | CARRIED | — |
| 9 | 1238-1239 | 189 | `d1843b7e7e7bee1fec119a7314ce98958f5e46327d872070510c73a6b1c90a01` | CARRIED | — |
| 9.1 | 1240-1261 | 1846 | `2f65f00d238120d373117e911df52af24a18207a22d90e8bf97bacdf72ce8bf1` | AMENDED | CC, PF (AM-21..23) |
| 9.2 | 1262-1280 | 1652 | `f9a758c96a803f6b57691c87999a525b6992738ca6163249e26e97640a1fb178` | CARRIED | — |
| 9.3 | 1281-1376 | 9317 | `162720bdc67f18273c9234d298792fd5f5a38b72c7668674f7dffd504115bb07` | REPLACED | PF, CC |
| 9.4 | 1377-1509 | 12771 | `d173f164f0a0d712526adab4a4ca75c578292ee4b1f1ca240c89620b0dda9bce` | REPLACED | CC, PF |
| 9.5 | 1510-1536 | 3477 | `80dfc04475a8a553e99df2c2b44db1fe1ba788bf9191a5f3bb1702e8b67e4693` | REPLACED | PF, CC, JC, SI, IO |
| 9.6 | 1537-1557 | 2037 | `6e22317b456f3cae05193dc42d34363ded46900043cf08f38e5dc9da8a8950ba` | CARRIED | — |
| 9.7 | 1558-1602 | 4112 | `916816ae34590700a3f46c8d6500a8518866dea6f3f6b65304154eb7973db6f9` | CARRIED | — |
| 10 | 1603-1604 | 173 | `b923c50c51930667776aced4d6d5b16a080102e4e056e61d0ade2fd420c1d98d` | CARRIED | — |
| 10.1 | 1605-1620 | 1162 | `52feefb6ac485169b1217cb73f674fae8f6477b8046e6a0db7bda861a5651a0f` | CARRIED | — |
| 10.2 | 1621-1640 | 1760 | `3f4d0512022faa2c672d85c5a27836a1fbbbd8eecb0a160f8afd280ea0f7dd46` | REPLACED | JC |
| 10.3 | 1641-1646 | 369 | `2b275b998e8c39b306421b0c6400ea8c12528d2b9741410c51f99ac4bca59990` | CARRIED | — |
| 10.4 | 1647-1690 | 4467 | `45c96fa1f94741a0a04242424778df566daa7cd7914d7c8ff2cc04be34e7d85f` | CARRIED | — |
| 10.5 | 1691-1700 | 841 | `5178acc5917198bcbf50bc34358e123e263a72594c8410237fd622065a82f6c8` | CARRIED | — |
| 10.6 | 1701-1727 | 3116 | `651fb2122dbff804b02b66f8b498dd90ee18339fce5acdec8e3dc8d4bc3c853b` | CARRIED | — |
| 10.7 | 1728-1744 | 1522 | `be90fc8a859b2d3a7d89acb5e3c29b8464baf177bd69cf55f0e1a58f068b409f` | REPLACED | PF |
| 11 | 1745-1746 | 127 | `554fcbe4c216f90ff9d4ae0b8672903c7d18685221dc80a7ec07dbc59d5df8cd` | CARRIED | — |
| 11.1 | 1747-1767 | 1749 | `311a9b017bef4fd59870b92ff6126e8be5a8218c12e2181b57465c0b9befdc54` | CARRIED | — |
| 11.2 | 1768-1784 | 1340 | `42fd1ec6a0f589f9b98a3bd1a451cd17cd9478f4839c5816582828d2e52fcea4` | CARRIED | — |
| 11.3 | 1785-1834 | 7542 | `c14e0560b3f0093e6afc4567484205beda02680fc5315263c2024ff92184b2de` | CARRIED | — |
| 11.4 | 1835-1879 | 4175 | `e08d506caa92e590cf0054f91dc76b72eaf84480e932db608398c3207286f18f` | REPLACED | SR |
| 11.5 | 1880-2142 | 14167 | `88da095a162937206b62048edd36a72446c7e2269d7a640cf5fb924c374cf20d` | REPLACED | SR, SI, CC |
| 11.6 | 2143-2156 | 1069 | `1443a7bbdcc0dd019cbc74ce2c2f44b12a8a5f2ca7bae7de45c8fed736ad6b02` | CARRIED | — |
| 11.7 | 2157-2177 | 3160 | `72a05530b96e6a844ce3b0543b85f208c6c6caab96e6615d5c6ae266e101d320` | AMENDED | SI, IO (AM-24..27) |
| 12 | 2178-2181 | 143 | `885b22172938418cce68053ca979e7f60082b4920c2606c4f2d0a579ee5ed5e7` | CARRIED | — |
| 12.1 | 2182-2202 | 1723 | `1e6066edfba180d9dff736cf3f5b95025109f49f35f34e91d986dc56739ae408` | CARRIED | — |
| 12.2 | 2203-2232 | 2785 | `c438cb6b6e750e971ceea9b6b6ba7917bdc84b762ce428bd2259e24624619c58` | CARRIED | — |
| 12.3 | 2233-2244 | 886 | `a9894889e896aa05dae51c56c4ffb3ba29a0696c094a4019ccabcefed2515247` | CARRIED | — |
| 13 | 2245-2355 | 13608 | `f15f4010d52710ae8b96c2c0c8eba527494d37496de6e93364babea11e8016cc` | CARRIED | — |
| 14 | 2356-2368 | 1153 | `c95b67595ab8c4f051b33cb23613f43971bc60578c01f258fca0a15ba02029e1` | CARRIED | — |
| 14.1 | 2369-2376 | 552 | `74064f167fa18ca4c37b49cef1070d1902ab55bf3201fcca04aac6be3a9c59f9` | CARRIED | — |
| 14.2 | 2377-2393 | 2421 | `b08b58e84485ca9f8315121c3ba79b6e1ae4be3fef93b5aaf71d235990b6eb1f` | CARRIED | — |
| 14.3 | 2394-2416 | 2012 | `f34b228b12070739cf2c17fa4022aad1e39316668e571cb279ed6f6099d2a7d7` | CARRIED | — |
| 14.4 | 2417-2429 | 739 | `e9387e358eaffbf6a7244c1a7c9e15c237cfce7b2d5a39cd2e05a71af4860f1b` | CARRIED | — |
| 14.5 | 2430-2476 | 4301 | `e1ab2814372cd373ab9fba50c8ea054d3c2939b26c6a5cc7f05594b1ae2d96da` | AMENDED | IO (AM-28, AM-29) |
| 14.6 | 2477-2482 | 280 | `0633b9be1ccd21a6c5eba0f8857b5623a5a25b5b5689318dce2ba98df525e419` | CARRIED | — |
| 15 | 2483-2484 | 139 | `c28ab08b1a6cf57c5c65775871754ab7312225c4fb76ff455a1da064d04a35d0` | CARRIED | — |
| 15.1 | 2485-2529 | 4035 | `27b9e552038b515beeec395bda4a02c7342d2dd536de4d063cfae76f1dd26715` | CARRIED | — |
| 15.2 | 2530-2537 | 581 | `a777313fcfda24aa6425bb03bdf472121ec21647b5a33958e6e3bb421ab68e81` | CARRIED | — |
| 15.3 | 2538-2589 | 4686 | `0b06a741ca5ccac5c3ff9602215cd800dd636ee512d2d3342df8c04cae6f61e4` | AMENDED | JC (AM-30) |
| 15.4 | 2590-2604 | 1394 | `540ceb1e230c110537af0759ad791d4fa72d6df225ac5f9c6f2abb4c282fe6c0` | CARRIED | — |
| 16 | 2605-2633 | 2285 | `2c11efa09b6f51fe32888dda3c2f1d14509bbe4ef5f05ff7db097c4c47b5f002` | CARRIED | — |
| 17 | 2634-2660 | 4551 | `fc56e39a368b270894b1754b4503f68c72302035bf9db54f112eb52b64bd1f8b` | CARRIED | — |
| 18 | 2661-2667 | 460 | `9d291f744b3299fa9f288ac878e104a65a4d2809f8e3f2d008a8abb780b87a5e` | REPLACED | all |
| 18.1 | 2668-2679 | 2036 | `84daeb553b6a175df602301ee6fa3940348406c0aac15e1cd209f5188aa5bba0` | REPLACED | all |
| 18.2 | 2680-2689 | 908 | `fde2432cc675b3666775f7987cafc079beb9095045b8e5e59990b35a8e938eab` | REPLACED | all |
| 18.3 | 2690-2706 | 2638 | `f608f802db8444a483fd5ca7f2b309fa0477946c8dce92395b0c6b06b280cf6f` | REPLACED | all |
| 18.4 | 2707-2731 | 1690 | `6a89ad06e69c609877c1b0e003603e4cf56ec7b8e77b53f247b6f8e163efc2e6` | REPLACED | all |
| 18.5 | 2732-2783 | 2802 | `7c76ff978e1289df4e7e15dcdf65c4beed37094fbff88e769affe735123ec2ad` | REPLACED | all |
| 18.6 | 2784-2801 | 1476 | `74892b13d630cc15961c6b702f8fb35690cdf447b388d066d164673a7acc695a` | REPLACED | all |
| 19 | 2802-2825 | 1975 | `f15d6110f0ac5b0fd9c46de15622b457a491a39e29587b950abc5e3a9ea6d3b8` | REPLACED | all |
| 20 | 2826-2846 | 1775 | `2c9528df5e4a349e2aedebbb88104bd0f661a9f0c74fd61809706cb3eede6fd7` | REPLACED | all |
| Appendix A | 2847-2910 | 14868 | `1211f48a394f8dd03602066280d11ec7ee0089976919ad7028fa422a3556b9a0` | CARRIED | — |
| Appendix B | 2911-2919 | 676 | `eef7ebf9b21f869d21e2f3fe24a6052fd5fa503a50145afd3a1676bffaa30fc7` | CARRIED | — |
| B.1 | 2920-2931 | 1035 | `62ad241f9410a181967e43900aac0220861720c14c427f6aa571fbdaf8d6aefe` | CARRIED | — |
| B.2 | 2932-2953 | 2041 | `c6c34691e8ac1653613d8a2c308d8680ad362d996e13d91e0156fc998dc33f7c` | REPLACED | CC |
| B.3 | 2954-2996 | 9475 | `b327dfab936a0d7ccb0b10869c80c43cabaa6ad78ab830f710e14eb243aa29c0` | REPLACED | PF, JC, SI, CC |
| B.4 | 2997-3206 | 18767 | `9962653ad1f16f8b4f00be0b530be3f27b9ed992bd54afe9b9ac04e205a0e092` | REPLACED | PF |
| Appendix C | 3207-3266 | 4399 | `e21904702b855c69feb1afe86117e9088684c70162571459c5b906ea2b9a79c5` | CARRIED | — |
| Appendix D | 3267-3325 | 7942 | `43c155f98ef42f7aabefe4de787ddd9cd43360fd1968c19c0ccab04236de5a9f` | CARRIED | — |
| 9.8 | — | — | — | NEW, after §9.7 | CC |
| 13.1 | — | — | — | NEW, after §13 | all |
| Appendix E | — | — | — | NEW, after Appendix D | — |

### 18.6 New design elements in v5 that need the reviewer's attention, and the remaining premises

1. O's write revocation: a frame mutation of target-owned modes inside T at each parent stage, with its containment
   argument and its preservation argument (§9.8 K1, K6).
2. W-CLOSED and the custody lemma, which make retained, queued and unobservable references irrelevant to custody
   (§9.8 K2, K4, K5).
3. The credential closure: C9's io_uring additions and M's hardened drop-in (§9.8 K3, §9.3 C9, §11.5 S-F).
4. M-QUIESCENT, the trusted-systemd premises S1-S6 and the absorption lemma, with S1-S6 verified by a source-level
   reading of the installed version (§9.4).
5. The confirmation rule of §10.2: a record is committed only when a later chain marker confirms it, with close and
   continuation markers.
6. The protocol additions: `START` and `EARLY_REFUSAL`, interruption points, `SPAWN_FAILED`, the release timing and
   `RL_IDENTITY` (Appendix B.4).
7. The external seal of `setup-identities.json`, and `materialize`'s `unadopted` path (§11.7).
8. S-R by observation of atoms and their intermediate states, and `check_out.py` in place of pipelines (§11.4,
   §11.5).
9. The search-only images directory and the `lost+found` special entry (§3.4, §14.5).

Remaining premises. Installed verification is future work; each premise keeps its probe, and its failure means
redesign, with no exception. §9.8 K7 lists them all. It covers every premise the gpt61-v4 review names in item 3: the
PAM-less manager's start, delegation and runtime directory (M-PAM); no session-bus need (BUS); private-socket peer
credentials and notify authentication (S6); a sufficient manager barrier and complete observation of buffered and
deferred work (S1-S6 with Q1-Q8); the kernel read-lease conflict for queued descriptions and mappings (L1);
pre-created output-directory compatibility (ROOTS); home exposure, namespace and root-launcher compatibility (OPT-B);
ENOSPC overwrite durability (ENOSPC); and image geometry and `noexec`/native compatibility (IMG). v5 adds K-PERM,
K-CHMOD, H1-H3 and LOOKUP.

## 19. Future execution and installed evidence (none of it exists)

- Frame v6-W1 code for every role and verb (`adopt`, `materialize`, `dispatch`, `seal-front` in both modes,
  `selftest`), frozen, with its own actual gpt-6.1-sol review: the excluded-leaf keys, the lease test, the write
  revocation and the W-CLOSED check, the state machines and keysets of Appendix B.4 (including `EARLY_REFUSAL`, the
  interruption points, `SPAWN_FAILED`, the release timing and `RL_IDENTITY`), commit, close and continuation markers
  with the chain reader, the fallback journal, exports, the scans with M-QUIESCENT, recovery, the setup-identity seal
  checks, the extended anti-setid filter, the selftest verbs and probes, and the helpers `absent.py`, `step.py` and
  `check_out.py`.
- The concrete setup inventory (fixed numbers, P1-P24 outputs, script texts and digests including S-J and S-R's atom
  tables, expected ACL texts, restore dumps and `systemctl show` outputs, the mask list under §11.5's rule, the sudoers,
  sshd and hardened user-manager drop-in bytes, the Option A or B text) and its review; JACKAL bounds for the
  subordinate-range checks.
- Option B's concrete code, rule and probes, if Option B is pursued, and their review.
- Operator approval and execution of S-0 to S-I (and S-J if images are chosen), with S-I captures including the seal
  capture of `setup-identities.json`; S-R records if a script stops.
- Post-setup verification (§11.6); every probe of §13 and §13.1 with raw records, including P-MGR, P-QUIESCE,
  P-WCLOSED, P-SETID, P-STREAM, P-COMMIT, P-CHAIN, P-PROTO, P-SEAL, P-SR, P-ENOSPC, P-SETUP and, with images, P-MOUNT
  and P-IMAGE; V-VAULT.
- The source-level reading of S1-S6 for the installed systemd version, and the comparison of both filter lists with
  the installed kernel's system-call table (H3), as part of the installed evidence.
- The new baselines (relocated runtime closure, R's manager environment without PAM and with the drop-in's
  restrictions, `UnitPath`, S_units and S_socks, writer context, tool inventory per option) as reviewed installed
  evidence; the installed-evidence review, which records S; the adoption run.
- Fresh storage readings and Gate 0 receipts for every stage; measured image geometry if images are chosen.
- First engineering-run evidence for the compatibility hypotheses: no `HOME` writes, no partition-root removal, no
  set-user-ID or set-group-ID mode, no `io_uring` or `openat2` use and no session-bus use by the allowlisted actions, no
  allowlisted action that needs a unit of M, and a working PAM-less, hardened M.
- Rollback execution records, whenever rollback happens.
- Independent actual gpt-6.1-sol review of all of the above. Only then can V5-B01 and V5-B02 be assessed against
  exact successor evidence.

## 20. Non-claims

- No sufficiency is claimed for V5-B01, V5-B02 or any original obligation. All stay OPEN until exact successor
  evidence meets the original required changes, with their original owners, releases and dependencies.
- Nothing here is executed or installed evidence. Design statements, templates and probe specifications are plans.
  The passive host observations are dated and attributed (Appendix E), and they are not setup evidence.
- The account and gate design gives a kernel-enforced writer and generation boundary under the stated trusted base,
  preconditions and premises. It is not proof of the frame code, not lead authentication (R2), not confinement of the
  running target (R3), not custody of the toolchain (R4), and no protection from root.
- The write revocation narrows only non-owners' write permission on the partition contents; it confines nothing the
  target does while it runs, and it is reported as the frame mutation it is.
- The custody, quiescence and lease arguments rest on kernel and systemd behaviour that is stated (§9.8 K7, §9.4
  S1-S6), not yet observed on this host. Until the probes and the installed-version reading pass they are premises;
  if one fails, the affected stage refuses or the classification is UNKNOWN, and W-1 must be redesigned. Nothing is
  weakened to make them pass, and no finite probe stands in for a premise.
- Integrity of the channels is not sender authentication.
- No storage capacity is established. Allowances are labelled judgments, never bounds; the arithmetic is exact
  arithmetic outside the Lean certificate chain (status `exact`, not `formal-bounded`) and is informational only.
- Images enforce write limits only. ENOSPC is never an accepted refusal and never capacity.
- Exports and lead copies are evidence records, not authentic producer custody; a vault transfer is backup.
- Fallback, raw, unconfirmed and durability-UNKNOWN records earn no success credit; they have no release effect.
- No operator choice is made or recommended; no approval is requested; no new approval gate is created.
- Phase One is incomplete.

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
`{core, nofile, nproc}` (pairs of int); `cgroup` (str); `namespaces` `{mnt, pid, user}` (int inode); `cwd` `{dev, ino}`;
`stdio` (list of `{fd, type, dev, ino, mode, flags}`, `type` ∈ {`fifo`, `socket`, `regular`, `char`, `dir`, `other`});
`open_fds` (list of int); `environment` `{names, sha256, values}` (values only for the clear keys of §8.1); `python`
`{version, executable, prefix, base_prefix, flags, path}`; `modules` `{files: [{name, path, bytes, sha256}], builtins:
[str]}`; `frame_inventory` `{sha256, bytes}`.

### B.2 Participants, waits, scopes, scans [correction: W1-CUSTODY-CLOSURE]

- `wlscratch-participant-v1`: `role` ∈ {`S1`, `W`, `S2`, `L`, `SR/C`, `T`, `S_O`, `O`, `S3`, `W2`, `RL`, `M`}; `pid`,
  `start_time_ticks`, `ppid` (int); `uids`, `gids` (4 ints); `groups`; `cmdline` (list of str); `cgroup` (str);
  `observed_by` (role); `state` ∈ {`alive`, `absent`, `reused`, `unknown`}.
- `wlscratch-wait-v1`: `waiter_role`, `waited_role`; `pid`, `start_time_ticks` (int); `raw_status` (int or null);
  `exited`, `signaled`, `core_dumped` (bool); `exit_code`, `signal` (int or null); `wait_error` (object or null);
  `interrupts` (list); `unresolved` (bool); `meaning` (str).
- `wlscratch-scope-v1`: `manager_uid` (int); `unit` (str); `invocation_id` (str); `control_group` (str);
  `properties_at_start`, `properties_at_end` (objects with `LoadState`, `ActiveState`, `SubState`, `Result`,
  `ControlGroup`, `MemoryMax`, `MemorySwapMax`); `cgroup_state` ∈ {`ABSENT`, `EMPTY`, `NONEMPTY`, `UNAVAILABLE`}.
- `wlscratch-scan-v3` (v4's `wlscratch-scan-v2` with v5's fields): `point` ∈ {`parent`, `child`, `after`, `recovery`,
  `release`}; `phase` ∈ {`pre`, `post`} (`pre` only for the parent stage's first scans, §4.2 D8); `round` (int or
  null); `classifier` (participant); `known` (list of participant: K(P), §9.4); `scans` `{gate, r, w, name, scope,
  units, refs, quiesce, lease, wclosed}`, each `{result, unknown: [reason]}`, where `result` is: for `gate`, `r`, `w`,
  `name` a list of participants; for `scope` a `wlscratch-scope-v1`; for `units` `{loaded: [{unit, load, active, sub}],
  jobs: [{id, unit, type}], unit_files: [path], unit_path: [str]}`; for `refs` `{entries_checked, references: [{where,
  dev, ino, path}]}`; for `quiesce` `{sockets: [{fd, ino, type, state, name, peer_ino, peer_name, rqlen}],
  foreign_connections: [ino], barrier: {call, answered_at}, repeat_equal, pending_signals: [{tid, sigpnd, shdpnd}],
  cgroups: [{path, procs}]}`; for `lease` `{files_tested, refused: [{path, errno}], not_owned: [path],
  leases_enable}`; for `wclosed` `{entries_checked, violations: [{path, dev, ino, type, uid, mode, nlink}]}`. At the
  release point `units`, `refs`, `quiesce`, `lease` and `wclosed` are `null`; at the after and recovery points
  `wclosed` is `null`; in the parent stage's `pre` phase `refs`, `lease` and `wclosed` are `null` (they need the
  walk). `verdict` ∈ {`known-terminal`, `live`, `unknown`} at the after and recovery points, and ∈ {`pass`, `refuse`,
  `unknown`} at the parent, child and release points.

### B.3 Records [corrections: W1-PROTOCOL-FAILURE-STATES, W1-JOURNAL-CONTINUATION, W1-SETUP-IDENTITY, W1-CUSTODY-CLOSURE]

| Record | Schema name | Keys beyond the common fields |
|---|---|---|
| `generation.json` | `wlscratch-generation-v2` | `created_at`, `writer` (B.1), `invocation` `{argv, sudo_user, sudo_uid, sudo_command, n_f}`, `front_triple` `{pid, start_time_ticks, boot_id}`, `lease` `{lease_dir: [dev, ino], lock: [dev, ino], uid, gid, mode}`, `location_chain` (list of `{name, dev, ino, uid, gid, mode, acl_sha256}` from `/` to g), `record_chain` (the same from `/` to g_rec), `mounts` (the §3.4 mount facts; empty without images), `installed_frame` `{inventory_sha256, inventory_bytes, install_root, source_frame}`, `setup_identities` `{sha256, bytes, dev, ino}` (v4's `setup_identities_sha256` is its `sha256`), `setup_seal` (str: `adopted`, `unadopted`; §11.7), `channel` `{protocol, n_f, n_w, genesis}`, `verb`, `run_label`, `attempt0` |
| `inputs/<seq>-<name>` and its `.json` header (P_adm; P_att for `dispatch`) | `wlscratch-input-v1` (header) | raw bytes file; header `{seq, name, class ∈ {pinned, joined, observation}, size, mode, sha256, pin_source, verdict}` (§8.6) |
| `inputs/manifest.json` | `wlscratch-inputs-manifest-v1` | `entries` (list of `{seq, name, class, size, mode, sha256, written_to}`), `heads_after_inputs` |
| `materialization.json` | `wlscratch-materialization-v1` | every v5 `claude-scratch-materialization-v5` key (with `run` = g's path), plus `generation_pin` `{record, marker}`, `inputs_manifest_pin`, `partition_roots` (list of `{path, dev, ino, mode, acl_text}`), `recipe_mode_property` `{files_others_readable, dirs_others_searchable}`, `channel_heads` |
| `attempt.json`, kind `materialize` | `wlscratch-attempt-materialize-v1` | `kind` = `materialize`, `created_at`, `writer` (B.1), `invocation`, `front_triple`, `generation_pins` exactly `{generation, generation_marker}`, `lease`, `channel`, `verb`, `args` `{label, overlay_dir}` |
| `attempt.json`, kind `dispatch` | `wlscratch-attempt-dispatch-v1` | `kind` = `dispatch`, `created_at`, `writer` (B.1), `invocation`, `front_triple`, `generation_pins` exactly `{generation, generation_marker, materialization, materialization_marker}`, `adoption` `{record, marker}`, `lease`, `channel`, `verb`, `args` `{action, args, inbox}` |
| `fallback-allocation.json` | `wlscratch-fallback-allocation-v1` | `path`, `dev`, `ino`, `uid`, `gid`, `mode`, `bytes`, `slot_bytes`, `slots`, `st_blocks`, `created_at` |
| `front/front-identity.json`, `front/front-stage-<stage>.json` | `wlscratch-front-stage-v1` | `stage`, `front` (B.1 at stage), `lead_observation`, `frame_admission_front` `{inventory, review, installed_review, adoption, rollout, adoption_observation}`, `base_tree_observation`, `runtime_observation` (compact or full, v5 item 4), `manager_environment`, `sibling_units`, `storage_reading`, `window_ownership` (child stage), `vault` (where run) |
| `observer-intent-<n>.json` (also under `w2-<k>/`) | `wlscratch-observer-intent-v1` | `n`, `stage` ∈ {`parent`, `after`, `recover`}, `observer_argv`, `n_o`, `streams` (list of `{name, dev, ino}`) |
| `observer-<n>-<stage>.json` (also under `w2-<k>/`) | `wlscratch-observation-v2` | `n`, `stage`, `observer` (B.1), `scan_pre` (`wlscratch-scan-v3`, phase `pre`; stage `parent` only, else null), `revocation` (desc of `write-revocation-<n>.json`; stage `parent` only, else null), `walk` (with every excluded leaf's `stat_key`), `identities` (v5), `sample_half`, `scan` (`wlscratch-scan-v3`, phase `post`), `report` (descriptor or null) |
| `write-revocation-<n>.json` | `wlscratch-write-revocation-v1` | `n`, `roots` (list of `{path, dev, ino}`), `entries_examined` (int), `changes` (list of `{path, dev, ino, type, mode_before, mode_after, nlink_before, nlink_after}`), `result` (str: `complete`, `refused`), `refusal` (object or null: `path`, `reason`) (§9.8 K1) |
| `launcher-rl-identity.json`, `observer-<n>-rl-identity.json` (Option B; the latter also under `w2-<k>/`) | `wlscratch-rl-identity-v1` | `frame_sha256` (hex64), `channel` (str: `W-L` or `W-O`), and the `RL_IDENTITY` body (B.4.3): `root_launcher`, `ns_before`, `ns_after`, `mountinfo`, `toolchain` |
| `launch.json` | v5 keys plus | `generation_pin`, `attempt_pin`, `parent_observation_pin` (O's full walk incl. excluded-leaf keys), `launcher_argv_template`, `child_argv_template` (C), `streams` (names), `front_stage_pins`; v5 `environment` holds the relocated environment; v5 `adoption` is the descriptor of `lead-adoption.json` |
| `reservation-intent.json`, `reservation.json` | v5 keys plus | `window_lock_identity` `{dev, ino, nlink}` observed by F under the lock, `request_digest` |
| `admission.json` | v5 keys plus | `gate0_receipt_pin`, `front_stage_pins`, `observer_parent_pin`, `writer_half_pins` |
| `launcher-intent.json` | v5 `scope_argv` plus | `launcher_argv`, `seals` `{launch_sha256, admission_sha256}`, `n_wl`, `n_c`, `streams` (list of `{name, dev, ino}`, exactly the stream names of D14), `journal_head` |
| `launcher-start.json`, `launcher-wait.json`, `sudo-launcher-wait.json`, `observer-wait-<n>.json` | B.2 participant or wait | — |
| `child-wrapper.json`, `child-stage-child.json`, `child-admission-summary.json`, `effective-limits.json`, `child-start.json`, `child-wait.json`, `child-refusal.json`, `child-cleanup.json` | v5 keys (`child-stage-child.json`: C's target-context observations of the child stage; `child-admission-summary.json`: the digests of every C1-C7 result) | sent by C over SP_C and committed by W; plus `channel` `{c2w_head}`; `child-refusal.json` keeps v5's `target_started: false` and its meaning, and is sent only before C's spawn call; `child-wait.json` keeps v5's keys and is sent after `CHILD_START` (`CHILD_WAIT`) or as the only outcome of a failed spawn call that left no child (`SPAWN_FAILED`, `started: false`) |
| `writer-half-parent.json`, `writer-half-child.json` | `wlscratch-writer-half-v1` | `stage`, `snapshot_observation`, `attempt_identity`, `journal_join` (§10.6 result), `lease` (held, identity), `location_chains` |
| `spawn-ok.json` | `wlscratch-spawn-ok-v1` | `c_identity_pin`, `admission_summary_sha256`, `front_pong_at`, `writer_errors` (must be empty) |
| `stream-finality.json` | `wlscratch-stream-finality-v1` | `streams` (list of `{name, dev, ino, sha256, bytes, lease: {result, errno}}`), `final` (bool) |
| `result.json` | v5 `claude-scratch-run-result-v5` keys plus | `record_states` (name → `primary`/`retry`/`fallback`/`raw`/`unknown`), `durability` ∈ {`complete`, `UNKNOWN`}, `terminal_scans` (B.2 scan), `target_started` ∈ {`true`, `false`, `unknown`} (str), `streams_final` (bool), `w1` `{generation, attempt}` |
| `release-intent.json` (W) or `w2-<k>/release-intent.json` | v5 keys (`at`, `token`, `terminal`, `prior`) plus | `writer_role` ∈ {`W`, `W2`}, `classification_pin` (the after-stage or recovery scan) |
| `window-release.json` (or under `w2-<k>/`) | v5 keys (`at`, `token`, `prior`, `current`, `terminal`) plus | `writer_role`, `intent_state` (the state of `release-intent.json`) |
| `release-withheld.json` (or under `w2-<k>/`) | v5 keys (`at`, `reason`, `owned_terminal`, `resolution`) plus | `writer_role`, `facts_sha256` |
| `release-not-owner.json` (or under `w2-<k>/`) | `wlscratch-release-not-owner-v1` | `token`, `window` (pin or null), `writer_role` |
| `release-failure.json` (or under `w2-<k>/`) | v5 keys (`at`, `error`, `resolution`) plus | `writer_role`, `reread` ∈ {`released`, `reserved`, `unreadable`} |
| `final-status.json` | `wlscratch-final-status-v1` | `success`, `released`, `durability`, `record_states_sha256`, `unknown_records`, `fallback_records`, `late_errors` |
| `conclude-errors.json`, `refusal.json` | v5 keys | — |
| `w2-<k>/identity.json` | `wlscratch-w2-identity-v1` | `mode` ∈ {`seal`, `recover`}, `writer` (B.1), `capability` `{front_triple, s3: {pid, start_time_ticks}, front_parent: {pid, start_time_ticks}, verified}`, `attempt_writer_state` (participant state of the attempt's W), `lease`, `channel` |
| `w2-<k>/recovery/scan-<r>.json` | `wlscratch-scan-v3` | B.2, with `point` = `recovery` and `round` = r |
| `w2-<k>/recovery/result.json` | `wlscratch-recovery-result-v1` | `verdict` ∈ {`known-terminal`, `live`, `unknown`}, `rounds`, `last_scan_pin`, `target_started`, `participants` (list of B.2) |
| `w2-<k>/front-terminal.json` | `wlscratch-front-terminal-v3` | `mode`, `s1_wait` (B.2), `w_final` (or null), `w_early_refusal` (the `EARLY_REFUSAL` body, or null), `w_absent`, `answers_forwarded` (list of `{n, sha256, at}`), `interrupts`, `errors`, `heads`, `durability`, `recovery` (bool), `recovery_result_pin` (or null), `release` `{performed, intent_state, record_state, intent_result_late}` |
| `commits/<seq>-<tag16>.commit` | `wlscratch-commit-v2` | `seq`, `kind` ∈ {`primary`, `retry`, `export`, `continuation`, `close`}, `record` (`{path, sha256, bytes, mode, acl_sha256}`, or null for `continuation` and `close`), `skipped` (list of `{seq, files: [{name, sha256, bytes}]}`, non-empty exactly for `continuation`) (§10.2) |
| fallback slot payload | `wlscratch-fallback-v1` | `record_name`, `stage`, `errors`, `value_sha256`, `value_bytes`, and exactly one of `value` or `value_truncated: true` |
| `export/generation/manifest.json`, `export/<A>/inc-<n>/manifest.json`, `adoption-<I>/export/inc-<n>/manifest.json` | `wlscratch-export-v2` | `increment`, `entries` (list of `{export_path, source_path, sha256, bytes, mode, acl_sha256, source_marker_sha256, state}`), `directories` (list of `{path, dev, ino, mode, acl_sha256}`) |
| the matching `freeze.json` | `wlscratch-freeze-v3` | `increment`, `cut` `{journal, seq, sha256}`, `slot_range` `{from, to}` (null for the generation and adoption journals), `previous_freeze_marker`, `export_markers` (list of sha256), `manifest_sha256`, `raw_files` (list of `{path, sha256, bytes}`, §15.3), `heads` |
| `channel/<channel>-<first>-<last>.json` | `wlscratch-channel-segment-v2` | `channel`, `messages` (list of `{dir, seq, prev, kind, length, payload_sha256}` plus either `payload` or `ref`, where `ref` is `{record, offset, length, sha256}`, `{written, offset, length, sha256}` or `{source, offset, length, sha256}`; `dir` includes `RL2W` under Option B) |
| `adoption-<I>/invocations/<stamp>/invocation.json` | `wlscratch-adopt-invocation-v1` | `created_at`, `writer` (B.1), `invocation`, `front_triple`, `lease`, `channel`, `installed` `{inventory_sha256, install_root, source_frame, setup_identities_sha256}` |
| `adoption-<I>/lead-adoption.json` | `wlscratch-lead-adoption-v1` (key set as v5 defines it; nothing is implemented) | every key of v5's `claude-scratch-frame-lead-adoption-v5` record (with `frame` = INSTALL_ROOT), plus `source_frame`, `setup_identities_sha256`, `setup_identities_file` `{bytes, dev, ino}` (the seal of §11.7, added in v5), `installed_review` `{review_sha256, review_freeze_sha256, review_report_sha256, reviewer_thread, rollout, turn_contexts, session_providers, exec_argv, exec_argv_record, event_stream, rollout_final_message_sha256, rollout_final_timestamp}`, `invocation_pin` |

### B.4 Channel kinds (body key sets) and the states that permit them [correction: W1-PROTOCOL-FAILURE-STATES; v4: W1-GENERATION-PROTOCOL]

**B.4.1 Conventions.** Types: `hex64` and `hex32` are lowercase hex strings of that length; `desc` is
`{path: str, sha256: hex64, bytes: int, mode: int}` (v5's `pin` shape); `pin` is `{record: desc, marker: hex64}`;
`identity` is B.1; `participant` and `wait` are B.2. Every body has exactly the listed keys. A kind marked *carrier*
has the key `bulk` (list of str) and is followed immediately by one `BEGIN`/`CHUNK`/`END` sequence per listed name, in
that order (§7.3): `BEGIN` `{name: str, size: int, mode: int, sha256: hex64, chunks: int}`, with `chunks` = 0 exactly
when `size` = 0; `CHUNK` `{index: int, data_b64: str}`; `END` `{sha256: hex64}`. A kind marked *fds* is sent in one
`sendmsg` carrying exactly the listed descriptors as `SCM_RIGHTS` ancillary data, in the listed order; other ancillary
data, or none, is a channel failure.

**B.4.2 F↔W and F↔W2 kinds** (v5 changes: `EARLY_REFUSAL` is new; `TARGET_EXITED`, `MATERIALIZED`, `EXPORTED` and
`FINAL` have changed key sets).

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
| `RECORD_COMMITTED` | W→F, W2→F | `name` (str), `record` (desc), `marker` (hex64), `state` (str: `primary`, `retry`) |
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
| `FINAL` | W→F, W2→F | `exit_status` (int), `success` (bool), `released` (bool or null), `durability` (str: `complete`, `UNKNOWN`), `unknown_records` (list of str), `fallback_records` (list of str), `exports` (list of objects: `increment` int, `freeze_marker` hex64), `vault` (str or null: `ok`, `failed`; null for a verb without a vault stage) |
| `BYE` | F→W, F→W2 | no key |

After `RELEASE_DONE`, the writer commits `window-release.json` when `reread` is `released` and `release-failure.json`
otherwise. A writer sends `RECORD_COMMITTED` only for a record that §10.2 calls committed, after the marker that
confirms it is fully written; `marker` is the digest of the record-bearing marker.

**B.4.3 W↔L, W↔C, W↔O and W2↔O kinds** (v5 changes: `RL_IDENTITY` and `SPAWN_FAILED` are new; `L_REFUSAL`'s stages,
`OBSERVE_REQUEST` and `OBSERVATION` have changed).

| Channel | Kind | Direction | Body keys (types) |
|---|---|---|---|
| W↔L, W↔O, W2↔O (Option B only) | `RL_IDENTITY` | RL→W, direction `RL2W` (§7.3) | `root_launcher` (identity, role `root-launcher`, taken after the credential drop), `ns_before` (object: `mnt`, `pid`, `user`; int inodes), `ns_after` (the same), `mountinfo` (list of str: the lines for `/home/sicarii` and the toolchain bind), `toolchain` (object: `dev`, `ino`, `uid`, `mode`) |
| W↔L | `L_HELLO` | L→W | `nonce` (hex64), `launcher` (identity) |
| W↔L | `GO` | W→L | carrier; `echo` (hex64), `bulk` (exactly `["launch.json", "admission.json", "launcher-intent.json"]`) |
| W↔L | `FDS` | W→L | fds; `names` (exactly `["sp_c", "scope.stdout", "scope.stderr"]`) |
| W↔L | `LAUNCHER_START` | L→W | `participant` (SR/C) |
| W↔L | `L_REFUSAL` | L→W | `stage` (str: the name of the failed G4 or G6 check, `stop` or `spawn`), `error` (object) |
| W↔L | `LAUNCHER_WAIT` | L→W | `wait` |
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
| W↔O, W2↔O | `OBSERVE_REQUEST` | W→O | `echo` (hex64 in the first request, null afterwards), `stage` (str: `parent`, `after`, `recover`), `round` (int or null), `participants` (list of participant), `walk` (bool), `revoke` (bool: true exactly for stage `parent`), `report` (bool) |
| W↔O, W2↔O | `OBSERVATION` | O→W | carrier; `stage` (str), `round` (int or null), `bulk` (exactly the observation record's name, followed, for stage `parent`, by `write-revocation-<n>.json`) |
| W↔O, W2↔O | `REPORT_BYTES` | O→W | carrier; `present` (bool), `bulk` (`["gnatprove.out"]` if present, else empty) |
| W↔O, W2↔O | `O_BYE` | W→O | no key |
| W↔O, W2↔O | `O_DONE` | O→W | `exit_status` (int) |

**B.4.4 State machines.** Rules common to every machine: a state ends when the side that speaks first in the next
state sends that state's first message; where that first message is a record message, the record name the table gives
identifies it; a message valid neither in the current state nor as the first message of a permitted next state is a
channel failure (§7.4). A *record message* is `RECORD_COMMITTED`, `RECORD_FALLBACK` or `RECORD_UNKNOWN`; wherever a
row names a record, any of the three may report it, and in every F↔W and F↔W2 state after `START` the writer may also
send record messages for other records it commits in that state, and F may send `STOP`. Before `PROCEED_LAUNCH`, a
`STOP` makes the writer refuse (`REFUSAL`, then the refusal path of the verb); from `PROCEED_LAUNCH` on, it is
forwarded down (§9.2) and the machine continues. Every F↔W and F↔W2 machine starts in `START`, whose only messages
are the writer's hello (to `HELLO`) and `EARLY_REFUSAL` (to `DONE`); F sends nothing before the hello. `REFUSAL` is
legal only where a row lists it. Clean EOF is permitted only in `DONE`. These machines, with these rules, are the
complete set of legal sequences.

F↔W, verb `adopt`:

| State | Messages, in order | Next |
|---|---|---|
| `START` | `W_HELLO` (W→F) → `HELLO`; or `EARLY_REFUSAL` (W→F) → `DONE` | `HELLO` |
| `HELLO` | `HELLO_ACK` (F→W); then the next state's first message, or `REFUSAL` (W→F: F's identity fails §8.1's joins) → `EXPORT` | `INPUTS` |
| `INPUTS` | `REQUEST_INPUTS` with phase `adoption` (W→F); one `INPUT` per requested name, in order (F→W); `PHASE_END` (F→W) | `COMMIT` |
| `COMMIT` | `ADOPTED` (W→F) or `REFUSAL` (W→F: a join, the setup-identity seal or the commit of `lead-adoption.json` failed) | `EXPORT` |
| `EXPORT` | `EXPORTED` (W→F; state `frozen` or `failed`) | `FINAL` |
| `FINAL` | `FINAL` (W→F); `BYE` (F→W) | `DONE` |

F↔W, verb `materialize`:

| State | Messages, in order | Next |
|---|---|---|
| `START` | `W_HELLO` → `HELLO`; or `EARLY_REFUSAL` → `DONE` | `HELLO` |
| `HELLO` | `HELLO_ACK`; then the record message for `front/front-identity.json` → `INPUTS_DESCRIPTORS`, or `REFUSAL` (F's identity fails the joins) → `EXPORT` | `INPUTS_DESCRIPTORS` |
| `INPUTS_DESCRIPTORS`, `INPUTS_OVERLAY`, `INPUTS_BASE` | `REQUEST_INPUTS` with phase `descriptors`, `overlay` or `base`; one `INPUT` per name; `PHASE_END`; then `PHASE_DONE` → the next of these states, then `MATERIALIZE`; or `REFUSAL` in place of `PHASE_DONE` (an input failed its pin or verification; nothing from it was written) → `EXPORT` | `MATERIALIZE` |
| `MATERIALIZE` | `MATERIALIZED` (W→F) → `VAULT`; or `REFUSAL` (W→F) → `EXPORT` | `VAULT` |
| `VAULT` | `STAGE_REQUEST` with stage `vault`; `STAGE_RESULT`; the record message for `front/front-stage-vault.json` (a failed vault result is recorded and reported in `FINAL.vault`; it does not refuse) | `EXPORT` |
| `EXPORT` | `EXPORTED` | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | `DONE` |

F↔W, verb `dispatch` (refusal path RP0: nothing reserved, `REFUSAL` → `EXPORT`; refusal path RP1: reserved and
nothing launched, `REFUSAL` → `AFTER` → `CONCLUDE` → `RELEASE` → `EXPORT`):

| State | Messages, in order | Next |
|---|---|---|
| `START` | `W_HELLO` → `HELLO`; or `EARLY_REFUSAL` → `DONE` | `HELLO` |
| `HELLO` | `HELLO_ACK`; then the record message for `front/front-identity.json` → `INPUTS`, or `REFUSAL` (RP0) | `INPUTS` |
| `INPUTS` | `REQUEST_INPUTS` with phase `dispatch` and names `["lead-module"]`; `INPUT`; `PHASE_END`; then `PHASE_DONE` → `ADOPTION`, or `REFUSAL` in place of `PHASE_DONE` (RP0) | `ADOPTION` |
| `ADOPTION` | `ADOPTION_RECORD` (W→F) | `FRONT_PARENT` |
| `FRONT_PARENT` | `STAGE_REQUEST` with stage `front-parent`; `STAGE_RESULT`; the record message; then the next state's first message, or `REFUSAL` (RP0: F's half failed) | `PARENT` |
| `PARENT` | `PARTICIPANT` and record messages for the observer (W→F); then the next state's first message, or `REFUSAL` (RP0: a failed join, write revocation or scan) | `VAULT` |
| `VAULT` | `STAGE_REQUEST` with stage `vault`; `STAGE_RESULT`; the record message; then the next state's first message, or `REFUSAL` (RP0: v5's vault pin or status failed, J9) | `GATE0` |
| `GATE0` | `CHALLENGE` with kind `gate0`; `ANSWER`; the record message; or `REFUSAL` (RP0) | `LAUNCH_RECORD` |
| `LAUNCH_RECORD` | the record message for `launch.json`; `REFUSAL` (RP0) if it is not committed | `RESERVE` |
| `RESERVE` | `RESERVE_REQUEST` (W→F); then `RESERVE_ABORT` (F→W; `REFUSAL`, RP0) or `RESERVE_INTENT_REQ` (F→W); then `RESERVE_INTENT_COMMITTED` (W→F) or `RESERVE_INTENT_REFUSED` (W→F, after which F sends `RESERVE_ABORT`; RP0); then `RESERVE_DONE` (F→W: the window was written, or the write failed and the re-read shows this reservation or is unreadable) or `RESERVE_ABORT` (F→W: the write failed and the re-read shows no reservation; RP0); then `RESERVE_COMMITTED` (W→F) | `MEMORY_GATE` |
| `MEMORY_GATE` | per challenge, at most `MAX_CHALLENGES`: `CHALLENGE` with kind `memory`; `ANSWER`; `RECORD_COMMITTED`; on failure `REFUSAL` (RP1) | `ADMIT` |
| `ADMIT` | the record message for `admission.json`; `LAUNCH_INTENT_COMMITTED`; or `REFUSAL` (RP1) if either record is not committed | `PROCEED` |
| `PROCEED` | `PROCEED_LAUNCH` (F→W) → `RUNNING`; or `STOP` (F→W) → `REFUSAL` (RP1) | `RUNNING` |
| `RUNNING` | W→F: `PARTICIPANT` any number; `STAGE_REQUEST` with stage `front-child` at most once; `PING` at most once, after the front-child result; `TARGET_STARTED` at most once; `TARGET_EXITED` at most once (`started` true after `TARGET_STARTED`, false for a failed spawn call reported by `SPAWN_FAILED`, which sends no `TARGET_STARTED`); `REFUSAL` at most once (C refused before its spawn call, or the launch failed before L). F→W: `STAGE_RESULT` with stage `front-child` exactly once after its request; `PONG` exactly once after `PING`; `STOP`. The state ends only when W has recorded the wait of every launch participant it started | `AFTER` |
| `AFTER` | `STAGE_REQUEST` with stage `front-after`; `STAGE_RESULT`; `PARTICIPANT` and record messages for the observer | `CONCLUDE` |
| `CONCLUDE` | `CONCLUSION` (W→F) | `RELEASE` |
| `RELEASE` | F→W, exactly one of: (i) `RELEASE_INTENT_REQ`, later `RELEASE_DONE`; (ii) `RELEASE_WITHHELD`; (iii) `RELEASE_NOT_OWNER`. W→F: in (i), `RELEASE_INTENT_RESULT` exactly once, in answer to `RELEASE_INTENT_REQ`, then `RELEASE_RECORD_RESULT` exactly once, in answer to `RELEASE_DONE`; in (ii) and (iii), `RELEASE_RECORD_RESULT` exactly once. The two directions interleave freely: F sends `RELEASE_DONE` after its window write whether or not `RELEASE_INTENT_RESULT` has arrived, having waited for it at most the control deadline (§9.4), and a `RELEASE_INTENT_RESULT` that arrives after that is legal, recorded and changes nothing. The state ends when F has read `RELEASE_RECORD_RESULT` | `EXPORT` |
| `EXPORT` | the record message for `final-status.json`; `EXPORTED` | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | `DONE` |

F↔W2, verb `seal-front`:

| State | Messages, in order | Next |
|---|---|---|
| `START` | `W2_HELLO` (W2→F) → `HELLO`; or `EARLY_REFUSAL` (W2→F: lease held, capability or seal failure; nothing written) → `DONE` | `HELLO` |
| `HELLO` | `HELLO_ACK` (F→W2); then the next state's first message (mode `seal`: `STAGE_REQUEST` of `FRONT_TERMINAL`; mode `recover`: `RECOVERY_SCAN` or `RECOVERY_RESULT` of `RECOVER`), or `REFUSAL` (W2→F: F's identity fails the joins) → `EXPORT` | `FRONT_TERMINAL` in mode `seal`; `RECOVER` in mode `recover` |
| `RECOVER` | `RECOVERY_SCAN` any number (W2→F); `STOP` (F→W2) ends the rounds; `RECOVERY_RESULT` exactly once (W2→F), after W2's observer has ended | `RELEASE` |
| `RELEASE` | as in `dispatch`, with W2 as the writer; F re-reads the window under the lock first and sends `RELEASE_NOT_OWNER` if this attempt does not hold it, which includes the case in which F already released it earlier in the attempt (F's terminal record then states `release.performed: true`) | `FRONT_TERMINAL` |
| `FRONT_TERMINAL` | `STAGE_REQUEST` with stage `front-terminal` (W2→F); `STAGE_RESULT` carrying `front-terminal.json` (F→W2); `RECORD_COMMITTED`, `RECORD_FALLBACK` or `RECORD_UNKNOWN` (W2→F) | `EXPORT` |
| `EXPORT` | `EXPORTED` | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | `DONE` |

W↔L:

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | Option B only, first: `RL_IDENTITY` (RL→W, direction `RL2W`); then `L_HELLO` (L→W). A `STOP` (W→L) here (W's check of RL's frame or of L failed) makes L exit 125 having started nothing | `GO` |
| `GO` | `GO` and `FDS` (W→L); then exactly one of: `LAUNCHER_START` (L→W: its spawn call returned SR) → `WAIT`; `L_REFUSAL` (L→W: a G6 check failed, a `STOP` was pending at its interruption point, or its spawn call failed and no child exists; nothing spawned) → `DONE`. A `STOP` that reaches L after its interruption point is read after the spawn call and recorded; W stops C over W↔C. A spawn call that failed while a child exists ends L's messages: W sees a channel failure (B.4.5) | `WAIT` |
| `WAIT` | `LAUNCHER_WAIT` (L→W); a `STOP` (W→L) may still arrive and is recorded | `DONE` |
| `DONE` | `BYE` (W→L); clean EOF | — |

W↔C:

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | `C_HELLO` (C→W) | `RECORDS` |
| `RECORDS` | `RECORDS` and `STREAMS` (W→C); a `STOP` (W→C) makes C refuse | `ADMIT` |
| `ADMIT` | C→W: `CHILD_RECORD` any number, `CHILD_STAGE_REQUEST` once; W→C: `CHILD_STAGE_RESULT` once after it; then C→W `SPAWN_REQUEST` → `SPAWN`, or `CHILD_REFUSAL` → `REFUSED`; a `STOP` (W→C) makes C refuse | `SPAWN` |
| `SPAWN` | W→C: `SPAWN_OK`, or `STOP` instead (C refuses: `CHILD_REFUSAL` → `REFUSED`). After `SPAWN_OK`, exactly one C→W outcome: `CHILD_REFUSAL` (C refused before its spawn call: the final pass or a later check failed, or a `STOP` was pending at its interruption point) → `REFUSED`; `CHILD_START` (the spawn call returned T) → `RUNNING`; `SPAWN_FAILED` (the spawn call failed and C has no child) → `FAILED`. A `STOP` that C has not read by its interruption point is read after the spawn call: in `RUNNING` C forwards it as `SIGTERM` to T, in `FAILED` it is recorded. A spawn call that failed while a child exists ends C's messages: W sees a channel failure (B.4.5), and `target_started` stays `unknown` | `RUNNING` |
| `RUNNING` | W→C `STOP` (C forwards `SIGTERM` to T); C→W `CHILD_WAIT` once, then `CHILD_CLEANUP` at most once, then `C_DONE` | `DONE` |
| `FAILED` | C→W `CHILD_CLEANUP` at most once, then `C_DONE`; a `STOP` (W→C) is recorded | `DONE` |
| `REFUSED` | C→W `C_DONE` | `DONE` |
| `DONE` | clean EOF | — |

W↔O and W2↔O:

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | Option B only, first: `RL_IDENTITY` (RL→W, direction `RL2W`); then `O_HELLO` (O→W) | `REQUEST` |
| `REQUEST` | W→O `OBSERVE_REQUEST` → `RESULT`; or `O_BYE` → `DONE`. W sends exactly one request per observer; W2 may send one per recovery round | `RESULT` |
| `RESULT` | O→W `OBSERVATION` (for stage `parent` carrying the observation and `write-revocation-<n>.json`); then `REPORT_BYTES` if the request asked for it | `REQUEST` |
| `DONE` | O→W `O_DONE`; clean EOF | — |

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
| W↔L at L | before its interruption point: exit 125, nothing started; after its spawn call: wait for SR, then exit |
| W↔L at W, including a missing or second `RL_IDENTITY` | if `GO` was not sent, W sends none (L reaches its deadline and exits 125 having started nothing) and refuses; otherwise W records the failure, whether a launch happened is decided by the classification, and if C appears, W stops it over W↔C |
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

## Appendix D. v5 joins and where v4 performs them [correction: W1-GENERATION-PROTOCOL]

Every admission, child, conclusion and adoption join of frame v5 (`scratch.py`, sha256 `f9f6596d…be86`) is kept. The
right column names the role and the state (Appendix B.4) in which v4 performs it. No join is dropped, narrowed or
replaced by a weaker one; where a join moves to another role, the role that has the needed authority performs it and
the result reaches the others over a channel.

| v5 join (source) | Where v4 performs it | Role, state |
|---|---|---|
| J1 `started_by_dispatch` (S:1520-1527): the run is the dispatch verb's child | W: `SUDO_*`, `HELLO_ACK` and the stdio inode join; W2: the front-process triple | W `HELLO`; W2 `HELLO` |
| J2 `open_run`: the run directory and the materialization record pin | W at D3: the committed generation and materialization markers and the P_adm identities | W, before `HELLO` |
| J3 `command(action, args, materialization)` | F at D1 (grammar), W at D3, C at C6 (re-derivation) | F; W; C `ADMIT` |
| J4 `fresh_lead('scratch-run')` | F at D7 | F `FRONT_PARENT` |
| J5 `admission(parent)`: `frame_admitted` (inventory, review profile, adoption profile, rollout re-join, adoption observation) | F (the lead-context parts, D7) over the adoption bytes W delivers (D6); W (inventory, structural adoption joins, D3) | F `FRONT_PARENT`; W `ADOPTION` |
| J6 `verify_materialization` at the parent stage | O's walk (D8) and W's writer half | W `PARENT` |
| J7 `identities(parent)` (tool, data, ELF, vendor, runtime, manager) | O in the target context (D8) and F in the real context (D7) | `PARENT`; `FRONT_PARENT` |
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
| K1 the launch bytes hash to the argv seal | L at G6 and C at C2 | W↔L `GO`; W↔C `RECORDS` |
| K2 `/proc/self/cmdline` equals the sealed template plus the seals | C at C1 | W↔C `HELLO` |
| K3 `reservation-intent.launch` equals the launch pin | C at C2 | W↔C `RECORDS` |
| K4 the admission bytes hash to their seal; `gate.launch` equals `intent.launch` | C at C2 | W↔C `RECORDS` |
| K5 run, attempt, source and snapshot identities equal the seal; `verify_location` | C at C3 (g, source) and W at C4 (attempt, snapshot) | W↔C `ADMIT` |
| K6 `fresh_lead('scratch-child')`; `holder` equals `LEAD_ID` equals `intent.holder_task` | F at C4 (the fresh observation), C at C5 (the holder join) | `RUNNING`; W↔C `ADMIT` |
| K7 `owns_window(LEAD_ID, attempt, token)` | F under the window lock at C4; C requires the result at C5 | `RUNNING`; W↔C `ADMIT` |
| K8 `admission(child)` with `frame_admitted`; observed identities equal `seal.source_tree` | F (frame admission front part at C4, over the adoption bytes); C (inventory check, identities `child`, admission walk, C5) | `RUNNING`; W↔C `ADMIT` |
| K9 the launch pins (frame inventory, review, adoption, materialization) equal the current ones | C at C6; the adoption pin against the delivered protected record | W↔C `ADMIT` |
| K10 the environment equals `launch.environment`; the observed environment minus `INVOCATION_ID` equals it; `INVOCATION_ID` is 32 hex | C at C1 and C6 | W↔C `HELLO`, `ADMIT` |
| K11 the parent memory gate; the final sample at or above the minimum; the reserve bound; siblings allow only U | C at C6, with F's front half of `child-final` (C4) | W↔C `ADMIT` |
| K12 cwd; allowlist re-derivation | C at C6 | W↔C `ADMIT` |
| K13 effective limits (`memory.max`, `memory.swap.max`, core) and scope membership | C at C6 | W↔C `ADMIT` |
| K14 the target executable's identity | C at C6 | W↔C `ADMIT` |
| K15 `verify_materialization` again before the spawn | C at C10, with v6's leaf pass and the lease test | W↔C `SPAWN` |
| K16 `verify_location`; pending signals before the spawn | C at C10 and C11 | W↔C `SPAWN` |
| K17 `child-refusal.json` ("nothing was started") only on the pre-spawn path | C (§9.3, C's refusals) | W↔C `ADMIT`, `SPAWN` |
| Q1 `owned_terminal` | O's after-stage classification with the complete scans (§9.4); W2's recovery rounds (§9.7) | `AFTER`; W2 `RECOVER` |
| Q2 `final_stream_sync` | W after terminal, followed by the stream finality test | `AFTER` |
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
