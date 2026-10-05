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
