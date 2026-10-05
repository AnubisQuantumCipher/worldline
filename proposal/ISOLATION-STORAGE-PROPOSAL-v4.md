# Isolation and storage proposal W-1, v4: protected writer, gated target account, committed records (specification)

**Status.** Drafting author's design specification, written 2026-10-05 UTC for the Claude Code lead. It is a
CANDIDATE specification of the protected-writer confinement design for the scratch proof frame, and a targeted
successor to v3.
- Nothing in it is implemented, installed, approved, executed or reviewed. No account, group, ACL, sudo rule,
  installation, drop-in, mount, linger, unit, probe, selftest, vault, adoption or window action has been performed
  for v4.
- Proof dispatch stays blocked by the confinement criteria (V5-B01, V5-B02, both OPEN) and by the capacity gate
  (Gate 0, NOT ESTABLISHED).
- v1 (`ISOLATION-STORAGE-PROPOSAL.md`, sha256 `a27d3e74305b5edd47acd31a7c881d7147cfecdaa0935195e2b0acea1dc70442`),
  v2 (`ISOLATION-STORAGE-PROPOSAL-v2.md`, sha256 `1c116f27bd11bcd3e2fae0d00792b27c2e598928bb9ccc97f1db418102232cf6`)
  and v3 (`ISOLATION-STORAGE-PROPOSAL-v3.md`, sha256 `97f39c8967ec32538474827256271e65ab8ee0347165aa971b5887608e02ed8c`,
  193544 bytes, with `v3-support/jackal.json` sha256 `6b0853230bf777c9861a0b1f71cdfdd875d315eca7ddac725aeeca2243fcc86b`)
  are preserved unchanged.
- v4 is written against the sealed actual gpt-6.1-sol review `wt-1/package-review/gpt61-v3` (verdict NOT_READY;
  hashes verified before drafting: REVIEW.md `5191f1593cfa5381ce9e7b8709307bc8d33c9bc640426f64914d4a83f021929d`,
  review.json `2ff78fc9fb04305b017c9fd434a77e976f21d95a947b00aa5dc10deb609bee13`, checks.json
  `2645bc786be95a2cc702b129813fe5002c08e27cc37e19082f902b570a316451`, review-freeze.json
  `e329512a580d889440d004c89917a7ec306718b57809fbdd8de22f4ab85c7177`; the reviewer's separate
  `REVIEW-LIMITS-ERRATUM.md` `58693c79f317ceae101671600bb03120a8d9171a1bff691068bda3577bef36c9`). Its six required
  W-1 corrections (W1-GENERATION-PROTOCOL, W1-COMMIT-JOURNAL-EXPORT, W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE,
  W1-SETUP-PROBES-ROLLBACK, W1-IMAGE-TREE; JACKAL exact, parsed `1+1+1+1+1+1`), the four prior corrections (JACKAL
  exact, parsed `1+1+1+1`), the twelve section-3 gaps and the twenty original W-1 subgaps (sizes read from
  `review.json`) it rules on are mapped in §18. Its two package corrections (PKG-V6-OPERATOR-TEXT,
  PKG-SUPERVISION-RECORD) concern the lead's operator package, not this proposal, and are not addressed here.
  **§18 gives the author's own assessment (CLOSED-AT-SPEC-LEVEL or OPEN) for an independent actual gpt-6.1-sol
  reviewer to judge. It is not closure, and no row says a section "answers" a finding.**
- Authority. Design and frame code are routine reversible engineering under the human's preserved authorization; no
  in-principle approval is needed for them. Reserved to the operator: actual privileged setup (accounts, groups, ACLs,
  sudo, sshd configuration, the user-manager drop-in, installation, mounts, linger, rollback) on a concrete reviewed
  inventory; material API/ABI/owner-policy changes; toolchain/deployment architecture; merge, release, install, sudo,
  production and real PRIME. v4 adds no other approval gate.
- Every "verify", "check", "probe", "selftest" or "observe" below names future work, except the passive observations
  explicitly dated and attributed to the drafting author. Design text is not executed evidence.

**Inputs read for v4** (sha256, read-only): the gpt61-v3 review files above; v3 and its support file above; the prior
re-review `gpt61-v2/REVIEW.md` `dc0127eb4c55b1913a6ea3e2c72b316aa9f4c57292bb3e5b00a430f4e059a226` (its durability
ruling, line 230); frame v5 sealed review `REVIEW.md` `2c414c694ed75d72cffae2172bef967bdcf63d73cc0a3764f96762a59d49ec71`;
frame v5 `scratch.py` `f9f6596defa933e1edf3c37af59f7173ff252b7b4add40542dda7c8642b2be86` (in particular `adopt`,
S:816-837, `frame_admitted`, S:840-863, `run`, `release`, `conclude` and `child`); frame v6 working copy `scratch.py`
`2255d6e14967d62aa9ce4c2b93b986340dd6840df9b659f9252e522546884c84`; runbook v4.3
`d7db4439c75e664bc20022b01bc49a68be4c7f1b8316f90a80aaf225258f7201`; the installed `getfacl(1)` and `setfacl(1)`
manuals.

**Non-claims, short form** (full list §20). No sufficiency is claimed. V5-B01, V5-B02, Gate 0 and every original
Phase One obligation stay OPEN with their original owners, releases and dependencies. A kernel-enforced writer boundary
is not proof of the frame code, not lead authentication, not target confinement and not capacity.

---

## 0. Reading guide and what changed from v3

v4 keeps v3's architecture (separate writer account, separate gated target account, streamed pinned inputs, root-owned
flock-only writer lease, preserved recipe modes, front-only release, front-side storage and vault) and every item the
gpt61-v3 review closed or accepted. It repairs the six W-1 corrections the review required:

1. **W1-GENERATION-PROTOCOL (§3.2, §4, §4.6, §7.1, §9.3, Appendix B.3-B.4, Appendix D).** Every create-only step binds
   only objects that already exist. An attempt's stream files are created, opened and synced, and their `[dev, ino]`
   read from the held descriptors, before `launcher-intent.json` binds them; observer stream files likewise precede
   the `observer-intent-<n>.json` that binds them. `attempt.json` has two exact schemas: kind `materialize` pins only
   `generation.json` and its marker; kind `dispatch` pins both generation records, both markers and the committed
   adoption record. Every channel has an exact per-verb state machine (adopt, materialize, dispatch, seal-front in
   modes `seal` and `recover`, launcher, child, observer) with its failure transitions, and every message kind has an
   exact body key set. The fresh installed-frame adoption record has one authorized writer (W, through the reviewed
   `adopt` verb) and one destination inside the protected tree (`runs/records/adoption-<I>/lead-adoption.json`). Every
   v5 admission, child and conclusion join is kept; Appendix D maps each to its v4 place.
2. **W1-COMMIT-JOURNAL-EXPORT (§10, §15.3).** The fallback journal's immutable allocation descriptor
   (`fallback-allocation.json`) is a committed record of its own; slot content is append-only and is never compared
   with an initial digest. Slot writes, short writes, torn slots, truncated payloads and every consumer are specified.
   An export copy is created 0600, given its ACL and read back (ACL, `st_mode` 0640, digest) before its export marker
   records those final values. Exports are cut at a fixed journal prefix; later evidence (late errors, recovery and
   release records, W2's front terminal record) goes into further hash-linked export increments.
3. **W1-TERMINAL-CUSTODY (§2.1, §2.4, §4.5, §9.4, §9.7, §11.5 S-F, §13).** Baseline services and descriptor queues are
   closed rather than assumed: the target account keeps no service except its manager M (every user unit and socket
   and the user bus masked, and no PAM session, so no `(sd-pam)`); M's state is observed completely and must be
   quiescent (no foreign unit, job, connection or queued input, no reference into g); and a kernel lease test on every
   admitted target-written file shows that no writable open description of it exists anywhere, queued or not. A
   quiescent state is shown to be absorbing. Writer-death recovery obtains the complete scans through W2 and its
   observer, and "nothing was started" is concluded only from C's own pre-spawn refusal record, never from a missing
   `CHILD_START`.
4. **W1-DURABILITY-RELEASE (§9.4, §10.5, §10.7).** Release no longer requires a committed `release-intent.json`.
   Release is governed by the original holder/candidate/token joins and authentic, independently established
   known-terminal ownership; every participant UNKNOWN still holds. A release record that cannot be made durable
   withholds success, is reported as durability-UNKNOWN, and creates no hold and no approval gate.
5. **W1-SETUP-PROBES-ROLLBACK (§11, §13, §15.1).** Absence is decided by a reviewed no-follow `lstat` helper that
   distinguishes ENOENT from every error; scripts are fail-stop with a step log and a reviewed reconciliation procedure
   instead of a false "undo" claim; the home-ACL capture keeps a full headed `getfacl` restore dump separately from
   the `-c` comparison text; the probe tables give exact operands, preconditions and the errno each cell of the ACL
   matrix implies; setup identities separate pinned from intentionally mutable fields (§11.7).
6. **W1-IMAGE-TREE (§3.3, §3.4, §5.2, §9.6, §14.5).** One layout for both storage choices. The protected intended
   run tree T is `/var/lib/wlscratch/runs`; the attempt, export and adoption partitions live below its record root
   `runs/records`; an optional records image is mounted exactly there, inside T. The writer's complete mutation list
   stays inside T in every configuration; anchors, routing and missing-mount checks are specified.

**Carried byte-for-byte from v3** (sections the review closed, accepted or did not ask to change): §1, §2.2, §3.1,
§5.1, §5.4, §6.1, §7.2, §7.4, §7.6, §7.7, §8.1, §8.2, §8.3, §11.2, §12.1, §12.2, §14.1, §14.2, §14.4, §14.6,
Appendix A and Appendix B.1. Every other section is revised or new (§14.3 only to renumber its dispatch step from D7 to
D10); §18.5 is the section-by-section change map. No original admission
join, control, accepted case, criterion, allowance, cap or gate is relaxed.

**Author corrections of v3** (v3 itself is not edited):
- v3 §11.4 said that where a step can leave a partial change "the script undoes exactly that change". That was false
  for sequential `groupadd`/`useradd` under `sh -e`; it is withdrawn (§11.4).
- v3 §11.1 said its `absent` shell function treats a permission error as "present"; the function shown
  (`[ -e ] || [ -L ]`) cannot tell ENOENT from a permission or stat error. Withdrawn (§11.1).
- v3 §13 expected A1's first denial below g to be the path search, and P-ALIAS expected `EACCES` for A1's hard link of
  a recipe file. A1 can search g and read the recipe, so those expectations were wrong (§13 gives the corrected table).
- v3 §2.1 A3 ("not adversaries by assumption") and §2.4 R7 (accepting an unreadable `(sd-pam)` descriptor table) are
  withdrawn.
- v3 §9.4 made a committable `release-intent.json` a release precondition, contrary to the supplied durability ruling.
  Withdrawn.
- v3 §15.1 step 7 restored from the P21 capture, which `getfacl -c` produces without the headers that
  `setfacl --restore` needs. Withdrawn (§11.3 P21, §15.1).

Every cross-reference in v4 resolves to a section of this document.

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
  are not assumed observable.
- **A2, the running target** (`wlscratch-run` with group `wlscratch-gate`, and everything it starts). It may do
  anything those credentials allow, including commanding its account's user manager through the manager's private
  socket (transient units and services, descriptor-carrying unit properties, reloads), moving itself between cgroups
  of that manager's delegated subtree, passing open descriptors and connection handles to processes of any uid
  (including A1 processes, over abstract sockets), leaving descriptors queued in sockets, and writing everywhere its
  credentials permit outside the generation. It must not be able to mutate frame records, the admitted recipe, the
  frame's location chain or another attempt's evidence, and its leftovers must not change an admitted generation
  between a later final pass and spawn.
- **A3, the target account's user manager M** (`systemd --user` of uid `wlscratch-run`, without `wlscratch-gate`).
  After setup M is the account's only process outside the frame's own participants: every user unit, socket and the
  user bus are masked, and M runs without a PAM session, so no `(sd-pam)` helper exists (§11.5 S-F). M executes
  root-installed code, but every uid-R process (T included) can command it and pass it descriptors, so M's *state* is
  treated as attacker-influenced. No benign-service premise is used: final-pass custody and known-terminal ownership
  require that M hold no reference into g and have no foreign unit, job, connection or queued input, and that no
  writable description of an admitted file exist anywhere (§9.4). A state that cannot be observed completely is
  UNKNOWN.

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
- **R9, descriptors in transit (v3's limit, now closed by mechanism).** A scan of descriptor tables cannot see a
  descriptor queued in a socket. v4's custody conclusions no longer rest on such a scan: a writable open description
  of an admitted file is detected wherever it is, queued or not, by the lease test; a directory descriptor permits a
  mutation only to a uid-R or GATE process, and all of those are enumerated; M's queues must be empty and M must hold
  no foreign connection (§9.4). What remains is stated in §9.4 as conditions with UNKNOWN outcomes, not as a residual.

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
| M, user manager | `systemd --user` of R (lingering; every unit masked; no PAM session) | `user@<R>.service` | systemd |
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
root also contains `lost+found` (root-owned, 0700, created by `mkfs.ext4`), which W never uses. W lists T_root and R_root
at every invocation and refuses before any mutation if an entry falls outside this grammar or is not a W-owned
directory (with images, `records` must be the records mount, below). Only W or root can create entries there, so an
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
  its source is a loop device whose `/sys/block/<loop>/loop/backing_file` names the pinned image file, and that file's
  `[dev, ino]` (by `lstat` on the root filesystem) equals the pinned one; `/dev/disk/by-uuid/<pinned UUID>` resolves to
  that loop device; the image root's owner, group, mode and ACL equal the pinned ones.
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
- **Partition contents.** Entries below the four partition roots are written only by targets of launched attempts
  (through the gate group, §6.3). They are not frame writes. They are part of what each later attempt admits, so every
  attempt re-observes them in full (§4.5).
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
never in P_adm.

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
dispatch can use g (D3). W commits `refusal.json` in P_att(g, A0) and its export increment; the partial P_adm stays as
evidence.

**Dispatch attempt (`front.py dispatch <inbox> <g> <action> [args]`; v5 `dispatch` + `run` + `child`).**

- D1. F starts, records its identity, validates `action`/`args` against v5 `ACTIONS`/`command()` grammar and anchors
  the lead-created inbox (`sicarii`-owned, mode 0700, empty).
- D2. F creates its two channel pipes and starts S1 → W (`writer.py dispatch <N_F> <g> <action> [args]`).
- D3. W starts, takes the lease, anchors A_T and A_R with the missing-mount checks, opens g and g_rec by anchored
  chains; requires the committed markers of `generation.json` and `materialization.json` in the generation journal
  and equality of the P_adm identities with them; requires the committed adoption record `P_ado(I)/lead-adoption.json`
  of the installed inventory I with its marker in the adoption journal (otherwise it refuses: the installed frame is
  not adopted); creates `g_rec/attempts/<A>/` with its `commits/` (0700, authenticated); commits **`attempt.json`**
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
  `observer-intent-1.json` binding them (§9.3, G0), starts S_O → O, and O returns the full walk of `g/source` (with
  every excluded leaf's `stat_key`), the target-context identities `parent`, the helper half of `preflight` (heavy
  processes, meminfo, M's units) and the parent-stage scans of §9.4 including SCAN-QUIESCE and SCAN-LEASE; W commits
  `observer-1-parent.json` and `observer-wait-1.json`. Any failed join or scan refuses the attempt (nothing reserved).
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
| user manager | no linger; `sudo`'s PAM session uses `pam_systemd.so class=none` (observed in `/etc/pam.d/sudo`); probe P-MGR verifies that no `user@W.service` and no `/run/user/W` appear | linger (needed for the scope); every unit that would start a process is masked, including `dbus.socket` and `dbus-broker.service`, and M runs without a PAM session (S-F drop-in), so M is R's only process outside the frame's participants; M can still start units that R's own processes request through its private socket, which is why §9.4 requires M quiescent and reference-free; the masks and the drop-in are root-owned, under a root-owned home and in `/etc`, so R cannot remove them | the manager's units run with R's default credentials, without GATE |
| sshd (active: observed `ActiveState=active`) | `DenyUsers wlscratch wlscratch-run` drop-in (§11.5 S-E); home root-owned, so no `authorized_keys` can be planted; no userdb record with keys (`userdbctl`) | same drop-in; home root-owned | not a login identity |
| login, getty, display manager | shell `/usr/bin/nologin`, password locked | same | n/a |
| PAM account controls | `sudo` uses `system-auth` (`pam_unix` account, `pam_time`) for the invoking user and opens its session with `pam_systemd.so class=none` (that no user manager results for W is probe P-MGR); login services (`system-login`) add `pam_access`, `pam_nologin` and `pam_shells`; the locked password makes every password authentication fail; account expiry (`usermod -e 1`) is applied only at rollback, because sudo must still reach the accounts while they are installed (observed stacks, P10) | same | n/a |
| `su`, `runuser` | `su` needs the target's password (locked); `runuser` is root-only (`pam_rootok`) | same | `newgrp`/`sg` need a group password: none is set (`gshadow` entry locked) |
| polkit, `pkexec`, `run0`, `machinectl` | require admin authentication (`unix-group:wheel`, interactive); no rules.d grant (operator inventory); `empower` empty | same | same |
| cron, at | not installed: `/usr/bin/crontab`, `/usr/bin/at`, `/usr/bin/batch` absent, cronie and atd not found, no spool directories (observed 2026-10-04); re-checked at setup and by W at every invocation (absence of those paths) | same | n/a |
| system units, D-Bus system services | no unit or D-Bus service file references W (operator `grep -r` inventory of `/etc/systemd`, `/usr/lib/systemd`, `/usr/share/dbus-1`, `/etc/dbus-1`) | same, except the user@R.service instance created by linger and its reviewed drop-in | none references GATE |
| setuid/setgid files and file capabilities | none owned by W (operator `find / -xdev \( -uid W -o -gid W \)` empty before and, apart from setup objects, after); no untrusted code ever runs as W | none owned by R at setup. A target could otherwise mint a set-user-ID-R file anywhere it can write (`/tmp` and the other places of §12.3 are on the `suid`-enabled root filesystem). That would confer only R, which reaches nothing in g (g's ACLs name GATE, §6.3), and any process holding R is an unknown participant (§9.4) | the decisive route: a target holding GATE could chgrp a file to GATE and set the set-group-ID bit, and anyone executing it would gain GATE. C therefore sets `no_new_privs` and installs the anti-setid seccomp filter of §9.3 (step C9) before `exec` of T; the filter is inherited by every descendant. Processes outside T's tree that lack GATE cannot create GATE-group setid files (not members). The frame also refuses any set-user-ID or set-group-ID leaf it meets in g (§6.5), and every admission stage and the terminal check refuse any unknown GATE holder (§9.4) |
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
| partition contents | created by T: uid R, group GATE | as created under umask 077 | none set by the frame | as created | none |
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
Option B, RL sits between S2 and L and passes L's fds through unchanged (§12.2).

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
  §8.1's joins.
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
descendants, and under Option B also RL. Observer participants: every S_O/O started for A, by W or by a W2.
Post-writer participants: every S3/W2 of A. F and W are the owner processes (as v5's dispatch and run). Schemas
(Appendix B.2): `wlscratch-participant-v1` `{role, pid, start_time_ticks, boot_id, ppid, uids[4], gids[4], groups,
cmdline, cgroup, observed_by, at, state ∈ {alive, absent, reused, unknown}}`; `wlscratch-wait-v1` `{waiter_role,
waited_role, pid, start_time_ticks, boot_id, raw_status, exited, exit_code, signaled, signal, core_dumped, wait_error,
interrupts, unresolved, at, meaning}`; `wlscratch-scope-v1` `{manager_uid, unit, invocation_id, control_group,
properties_at_start, properties_at_end, cgroup_state ∈ {ABSENT, EMPTY, NONEMPTY, UNAVAILABLE}}`; `wlscratch-scan-v2`
(§9.4). A process is identified by `(pid, start_time_ticks, boot_id)`: a different start time at the same pid means
the original ended and the pid was reused; a different boot id means the original ended with its boot.

A participant is known only from positive evidence: a committed record or a received message that names its triple,
or a scan that sees it. The absence of a record never shows that a participant does not exist. Whether any launch
participant may still exist is decided only by the complete scans of §9.4.

O's jobs per invocation: the scans of §9.4 that need R credentials (SCAN-UNITS, SCAN-REFS, SCAN-QUIESCE,
SCAN-LEASE), the full walk of `g/source` (v5 `verify_materialization` with v6's final pass, returning every excluded
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

### 9.3 Launch gating

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
  `launcher-start.json`.
- G4. L: first act, identity, argv grammar; requires ruid = euid = suid = fsuid = R and rgid = egid = sgid = fsgid =
  GATE (under either option; Option B's RL produces the same credentials, §12.2), fd 0 a socket and fds 1-2 regular
  files; sends `L_HELLO`; waits for `GO` within the control deadline.
  **EOF or deadline before `GO` → L exits 125 having started nothing.**
- G5. W verifies L through `/proc/<L>` (credentials, `PPid == S2`, start time, cmdline) and sends `GO` with the bytes
  of `launch.json`, `admission.json` and `launcher-intent.json`, then `FDS` with SP_C's other end and the bound
  `scope.stdout` and `scope.stderr` descriptors by `SCM_RIGHTS`.
- G6. L verifies the two seals (sha256 of the delivered `launch.json` and `admission.json` equal its argv), that
  `launcher-intent.json`'s scope argv is exactly what it will run, and that its own fds 1-2 and the received scope
  descriptors have the `[dev, ino]` the intent binds; sets umask 077 and `no_new_privs`; starts SR =
  `/usr/bin/systemd-run --user --scope --unit=<U> -p MemoryMax=8G -p MemorySwapMax=0 /usr/bin/python3 -I -B
  /opt/wlscratch/frame-v6w1/launch_target.py child <n_c> <g> <A> <launch_sha> <admission_sha>` with stdin = the
  received SP_C end, stdout/stderr = the scope descriptors, the environment of `launch.json`, and a pre-exec that sets
  `RLIMIT_CORE` (0, 0) and unblocks the handled signals (v5 `spawn`); closes its own copy of the SP_C end; sends
  `LAUNCHER_START` with SR's identity.
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
  shows M quiescent apart from C's own connection. Any failure or UNKNOWN refuses.
- C8. `SPAWN_REQUEST` with the digest of C's admission summary. W answers `SPAWN_OK` only if F answered a `PING`
  within the control deadline, W's error list is empty and the attempt-journal join holds, and only after committing
  `spawn-ok.json`. EOF or deadline → C refuses.
- C9. C prepares T's pre-exec: `fchdir` to the held `source` descriptor, `RLIMIT_CORE` (0, 0), umask 077,
  `PR_SET_NO_NEW_PRIVS` = 1, then the **anti-setid filter**: a classic seccomp BPF program for `AUDIT_ARCH_AARCH64`
  (any other arch: kill) that returns `EPERM` for `fchmod`, `fchmodat` and `fchmodat2` when the mode argument has any
  of the bits 06000, for `openat` and `mknodat` when the mode argument has any of those bits, returns `ENOSYS` for
  `io_uring_setup` and `openat2` (whose arguments a classic filter cannot inspect), and allows everything else; then
  unblock the handled signals. The filter and `no_new_privs` are inherited by every descendant and cannot be removed.
- C10. **Final pass** (§4.5), with the lease test inside the walk; then SCAN-GATE, SCAN-R and SCAN-W again with the
  child-stage point; `verify_location` of every held handle.
- C11. Pending-signal check (interruption point); spawn T with stdin `/dev/null`, stdout/stderr the child stream
  descriptors, the sealed environment, `child_argv`.
- C12. `CHILD_START` with T's identity and the bytes of `child-start.json`; W commits `child-start.json` (v5) and tells
  F (`TARGET_STARTED`).
- Then C waits for T, sends `CHILD_WAIT` (`child-wait.json`) before cleanup, closes the child streams (failures:
  `CHILD_CLEANUP`), sends `C_DONE` and exits by v5's rule; L sends `LAUNCHER_WAIT` and exits; W retains its wait of S2.

**C's refusals.** Every refusal by C before the spawn call of C11 (C1-C10, C8's EOF or deadline included) sends
`CHILD_REFUSAL` with `child-refusal.json` (v5 keys, `target_started: false`, v5 meaning "refused before the target
spawn; nothing was started") if SP_C still works, and otherwise writes the same statement to its stderr
(`scope.stderr`, raw evidence); C then exits without spawning. C never sends `CHILD_REFUSAL` after calling spawn; a
failed spawn call is reported in `child-wait.json` with `started: false`, as v5 did. **`target_started`** is therefore
`true` if `child-start.json` is committed, `false` only if C's committed `child-refusal.json` or its committed
`child-wait.json` with `started: false` exists, and `unknown` otherwise. A missing `CHILD_START` never means that no
target exists, and `unknown` never shortens a classification.

**Why a late launch after writer death is possible only through an issued, recorded permission.** No L can start SR
without `GO` (G4), which only a live W sends, and only after `PROCEED_LAUNCH` and the committed launch intent. No T
can start without `SPAWN_OK` (C8), which only a live W sends after committing `spawn-ok.json`. A sudo front-end (S2)
that outlives W can only start an L, which then reads EOF and exits. So after W's death the only possible future
target is one whose C already holds `SPAWN_OK`; that C is a GATE holder and visible to every scan until it ends.
Whether a launch is still pending is concluded only from a complete classification (§9.4) in which every scan passes,
never from a missing record and never from an empty target-account or cgroup snapshot alone.

### 9.4 Scans, quiescence, lease test, known-terminal ownership and the release rule [corrections: W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE]

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
  job, is recorded but does not fail the scan: a scope cannot be restarted and holds no process.
- `SCAN-REFS` (R credentials): for M, `/proc/<M>/{cwd,root}`, every `/proc/<M>/fd/<n>` and every file mapping in
  `/proc/<M>/maps` is stat'ed; a `[dev, ino]` equal to any object observed in g by the same stage's walk is a reference
  into g. M is dumpable (it is `exec`ed after its credentials are set), so its `/proc` entries belong to R: observed by
  the drafting author on 2026-10-05 for `sicarii`'s own manager (`/proc/1019/fd` owned by `sicarii`, mode 0500).
  Any entry that cannot be read or stat'ed makes the scan UNKNOWN.
- `SCAN-QUIESCE` (R credentials): (1) every socket in M's descriptor table is identified by inode and examined with
  `NETLINK_SOCK_DIAG` for unix sockets (`UNIX_DIAG_RQLEN`, `UNIX_DIAG_PEER`, `UNIX_DIAG_NAME`; `/usr/bin/ss -x` shows
  the same data): its receive queue, or for a listening socket its accept queue, must be empty; (2) M must hold no
  accepted connection of its private socket other than the classifying process's own; (3) every socket of M must be of
  a kind, name and peer class in the reviewed static baseline S_socks (§11.6), which by setup contains only M's own
  private and notify sockets and its journal stream; (4) after (1)-(3) the classifier makes a synchronous call to M on
  the private socket (`ListUnits`, `ListJobs`), and when the answer arrives it repeats SCAN-UNITS, SCAN-REFS and
  (1)-(3) and requires identical results. M dispatches its API calls one at a time in its event loop (installed
  systemd behaviour, part of the trusted code of §2.2; checked by probe P-QUIESCE), so the answer follows the complete
  processing of every message M had already read, and the equal repetition shows that no such message was still
  taking effect. A transient difference (for example the accepted connection of a just-exited `systemd-run`, which M
  closes when it reads the end of file) is re-scanned until two consecutive scans agree and pass, within the stage
  deadline; otherwise the stage refuses (before launch) or the verdict is `live` (at a classification).
- `SCAN-LEASE` (R credentials; the owner of the files): for every regular file of the partition contents observed by
  the same stage's walk, open it `O_RDONLY|O_NOFOLLOW|O_NONBLOCK|O_NOATIME|O_CLOEXEC`, require its `fstat` to equal the
  walk's `stat_key`, request a read lease (`fcntl(F_SETLEASE, F_RDLCK)`), release it (`F_UNLCK`) and close it. The
  Linux kernel refuses a read lease with `EAGAIN` while the inode is open for writing by any open file description
  (`check_conflicting_open` in `fs/locks.c`); a description counts while any descriptor, in-flight `SCM_RIGHTS`
  message or shared mapping still holds it, whatever the holder's uid and whether or not its tables are readable. This
  kernel behaviour is a premise, not observed on this host (no section-2 manual is installed); probe P-QUIESCE verifies
  it before any reliance. A refusal, a file not owned by R (leases need ownership), or an `fs.leases-enable` other than
  1 refuses before launch and makes a classification UNKNOWN.
- Recorded participants: each `(pid, start_time_ticks, boot_id)` classified alive, absent, reused or unknown.

Any unreadable entry needed by a scan makes that scan UNKNOWN. There is no exception: v3's R7 is withdrawn (§2.4).

**Why these scans close baseline references and descriptor queues** (the reviewed argument; it uses no premise that
any service of the target account is benign):
- (a) *Who can change the admitted generation.* P_adm objects are W-owned and written by W only in `materialize`; the
  four partition roots are W-owned with `group:GATE:rwx`; partition contents are created by targets and owned by R.
  A mutation therefore needs one of: W's credentials (only trusted writer code; any other W process is visible to
  SCAN-W); GATE (SCAN-GATE); uid R together with a path or a directory descriptor into the partition contents (every
  uid-R process is visible to SCAN-R, and M's descriptors to SCAN-REFS); or an open writable file description of a
  partition file, which allows writing whoever holds it (SCAN-LEASE). A directory descriptor held by a process that
  has neither uid R nor GATE allows nothing, because every directory operation is checked against the caller's own
  credentials, and such a caller is `other` on every partition directory (0700, owned by R) and partition root
  (0770 W:GATE). Root is the trusted base.
- (b) *What M can still do, and why a quiescent M stays quiescent.* M executes root-installed code and acts only on
  input: messages on its private socket, datagrams on its notify socket, signals, its own timers, and unit-file changes
  that it reads only on a reload request. The private socket was observed for `sicarii`'s own manager on 2026-10-05
  as mode 0700, owned by the user, in a 0700 runtime directory, and systemd's private API accepts only peers whose
  credentials are root or the manager's own uid (P-MGR verifies both for R); notify datagrams are honoured only from
  processes of M's own units; only uid R or root can signal M; S_units contains no timer, path or socket unit (every
  enabled one is masked, and P16 observed no timer at all, §11.5 S-F). With no foreign connection, empty queues, no foreign unit or job, no uid-R process
  other than M and no GATE process, M has no pending input. New input could come only from a new uid-R or GATE
  process, which only the frame's own sudo rule can start (while the lease holder runs, §5.2), or from root. So a
  quiescent state is absorbing: it lasts until the frame itself starts a participant, whose own stage scans then
  apply.
- (c) *Descriptor queues.* A writable description in flight anywhere is caught by SCAN-LEASE, because it keeps the
  description open. A directory descriptor in flight can be used only by a uid-R or GATE receiver (a); the only possible
  receiver is M, whose queues are empty and which holds no foreign connection. A connection handle to M that a target
  passed to another process shows as a foreign accepted connection in M's table (QUIESCE (2)) and holds.
- (d) *What remains outside*: root and the kernel (R8); a writer instance running changed code (outside the threat
  model, as before); availability (R6).

**Classification points.** K(P) is the set of known triples of the frame's own processes running at point P. A scan
passes at P if every process it reports is in K(P) (for SCAN-R, K(P) plus M), SCAN-SCOPE and SCAN-UNITS show what the
table says, and SCAN-REFS, SCAN-QUIESCE and SCAN-LEASE pass. K(P) includes the sudo processes the serving writer
started, so it does not matter in which credential sets the kernel shows sudo's monitoring process (P-LAUNCH records
it).

| Point P | Classifier | K(P) | SCAN-SCOPE | SCAN-UNITS | Also required |
|---|---|---|---|---|---|
| parent stage (D8) | O, for W | F, S1, W, S_O, O | U absent | S_units | SCAN-GATE = {O} |
| child stage (C7, C10) | C | F, S1, W, S2, L, C | U holds exactly C | S_units ∪ {U} | SCAN-GATE = {L, C} |
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

Procedure, all under the window lock: F verifies 1 and 2; F sends `RELEASE_INTENT_REQ` and the serving writer
instance (W, or W2 after recovery) tries to commit `release-intent.json` (primary, retry, fallback, §10) and answers
`RELEASE_INTENT_RESULT` with the outcome; whatever the outcome, and also if no answer arrives within the control
deadline, F performs v5's window write (the commit point), re-reads the window, and sends `RELEASE_DONE` so that the
writer commits `window-release.json`. Any outcome other than a committed record makes the attempt durability-UNKNOWN:
no success credit, and the uncertainty is reported (console, `FINAL`, and the front terminal record if it can be
committed). It creates neither a hold nor an approval gate (supplied ruling, gpt61-v2 REVIEW.md:230).

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

### 9.5 Failure table

| Event | Behaviour |
|---|---|
| Lease held | W refuses before any mutation and before starting any helper, writes only to its stderr, exits non-zero. F has reserved nothing (reservation is D12) |
| A record that must precede `W_HELLO` (`generation.json`, `attempt.json`, `fallback-allocation.json`, `invocation.json`) cannot be committed as primary or retry | W refuses before any reservation: `REFUSAL` if the channel is up, its stderr otherwise; nothing reserved; without a committed `attempt.json` no W2 can verify its capability, so F's terminal facts stay on its console |
| sudo refuses, account locked, rule missing (each invoke) | F observes S1's exit before any reservation; nothing to release. A setup selftest never stands in for this |
| Channel failure, deadline or refusal before D12 | W: `refusal.json` ("refused before reservation and launch; nothing was started"); F: no reservation; F runs W2 in mode `seal` if `attempt.json` is committed |
| `reservation-intent.json` cannot be committed | F does not write the window (`RESERVE_ABORT`); nothing reserved; W: `refusal.json` |
| `reservation.json` cannot be committed | the reservation exists; durability-UNKNOWN for that record; W refuses before launch, concludes with the after-stage classification, and F releases by §9.4 |
| W dies or its channel fails after F's window write and before `PROCEED_LAUNCH` | W never started S2, but this is not inferred from missing records: F runs recovery (§9.7); release only on known-terminal ownership |
| W dies or its channel fails after `PROCEED_LAUNCH` | a launch may exist; recovery (§9.7) classifies until known-terminal or unknown; release by §9.4; otherwise hold |
| F dies after its window write | W: before launch, refuses and concludes; after launch, keeps waiting and concludes. W cannot release (F alone can): `release-withheld.json` ("front absent"); manual resolution. A front EOF never implies a refusal after launch |
| L dies before `GO` / after | before: L started nothing; after: SR/C may exist; the classification decides |
| C refuses before spawn | C's `child-refusal.json` (C's own pre-spawn statement), committed by W; `target_started: false`; classification still by complete scans |
| C dies or SP_C fails without such a record | `target_started: unknown`; never inferred from a missing `CHILD_START`; the classification decides |
| T exits | C's `child-wait.json`, L's and W's waits, O's after stage, conclusion |
| O fails | before launch: the stage refuses; after launch: no complete classification, so hold until a later O under a live W or a W2 succeeds; W never releases on its own |
| SCAN-LEASE refuses at the parent or child stage | refuse before launch: an admitted file has a writable description somewhere |
| SCAN-QUIESCE or SCAN-UNITS shows a foreign unit, job, connection or queued input | before launch: refuse; at a classification: verdict `live` while it persists, `unknown` if unreadable |
| Records exhaustion | §10: success withheld; release by §9.4 only |
| A stream file not final (W's stream lease test, §10.6) | success withheld; no release effect |
| M unavailable | L refuses before systemd-run (C never exists) |
| Window not owned at release | `NotOwner`, nothing released (v5) |
| Window write error at release | §9.4, window write failure |
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

### 10.2 Markers and journals

- A marker is `commits/<seq:08d>-<pathhash16>.commit` in its journal's `commits/` directory, holding
  `wlscratch-commit-v1` `{generation, attempt, seq, record: {path, sha256, bytes, mode, acl_sha256}, kind ∈ {primary,
  retry, export}, prev_commit, channel_heads, boot_id, at}` (`pathhash16` = the first 16 hex digits of the sha256 of
  the record's partition-relative path, so marker names are single components; `acl_sha256` is `null` except for
  export copies).
- Journals: the generation journal `g/commits/` (P_adm records; final after M8); one attempt journal per attempt,
  `g_rec/attempts/<A>/commits/` (every P_att record and every P_exp copy of A, written first by W and then by each W2
  of A in turn, never concurrently, because each writer holds the lease); the adoption journal `P_ado(I)/commits/`.
- **Committed chain.** A journal's committed chain is the longest sequence of marker files, starting at seq 0, in
  which every marker is committed (written, synced, post-validated) and each `prev_commit` equals the sha256 of the
  previous marker. A marker file that does not validate, or does not link, is raw evidence and ends the chain. The
  journal head is the seq and sha256 of the chain's last marker.
- **Appending after another writer.** A writer that appends to an existing journal (a W2 after W, a second W2) first
  recomputes the committed chain; its first marker takes `seq` = one more than the largest seq of any marker file
  present, valid or not, and `prev_commit` = the head's sha256. A seq is therefore never reused, a torn marker is never
  overwritten, and the chain stays linked across writers.
- A torn or unlinked marker leaves its record uncommitted (§10.1); consumers apply §10.6.

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

### 10.7 Exit statuses (N13, N14)

- **W (N13).** `success` = v5's conjunction (launched, scope wait 0, child wait 0 and clean, no error, post-identity
  clean, materialization unchanged, owned terminal) ∧ every required record `primary` or `retry` ∧ no `fallback`,
  `raw` or `unknown` record ∧ streams final ∧ released (F reported `RELEASE_DONE` with a re-read showing the release) ∧
  the release records committed. Errors appended after `result.json`, including late handle-close and export errors,
  force `success = false`, are committed as `conclude-errors.json` (or to the fallback journal), and make W exit 1.
  `final-status.json` records the final values.
- **W2.** Exit 0 only if its records are committed, its export increment is frozen and, in mode `recover`, known-
  terminal ownership was established and the release was performed.
- **F (N14).** Exit 0 only if W's `FINAL` reports success and release, F's own error list is empty, no interrupt
  reached F, S1's raw status is 0, W2 (mode `seal`) reported success and S3's raw status is 0, and nothing is
  `fallback` or durability-UNKNOWN. A run that needed recovery exits 1 even if it released. For `adopt`, F exits 0 only
  if W reported `ADOPTED`, `EXPORTED` and a successful `FINAL` and S1's raw status is 0.
- **C, L, O.** C keeps v5's rule (`code` if it is not `None` and there were no failure, notes or errors, else `code or
  1`); L exits 0 only if its scope wait is 0 and it had no error; O exits 0 only if its observation succeeded.

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

### 11.4 Protected reviewed-byte staging and fail-stop execution

- Every privileged byte is part of the reviewed concrete inventory with its sha256: both sudoers files, the sshd
  drop-in, the user-manager drop-in, every expected ACL text and restore dump, the mask list, the identity-record
  generator, the helpers `absent.py` and `step.py`, the scripts S-A to S-J and S-R, every frame member and the
  member/directory lists.
- **S-0 (operator, root):** create `/root/wlscratch-staging` with `mkdir -m 0700` (create-only: `mkdir` fails with
  `EEXIST` for any existing entry at that path, a dangling symlink included, so no stale staging tree can be reused)
  and verify root:root 0700 with `stat`; copy the staging manifest from the lead's frozen inventory directory with `install -m 0600`; verify it as root with
  `echo "<MANIFEST_SHA256>  $st/staging-manifest.sha256" | sha256sum -c --strict -`, where the digest is the one in the
  sealed review record; copy every listed file the same way; verify all as root with `sha256sum -c --strict`; create
  `log/` (0700) and, with `O_EXCL`, one empty log file per script (0600). The lead-writable source can change after
  review, which is why only the root-owned copies, checked as root, are ever used. v2's predictable lead-owned `/tmp`
  files are not used.
- Each script runs as `sudo sh -eu /root/wlscratch-staging/S-<x>.sh` from the verified copy. Under `-e` a failing simple
  command, pipeline or loop-body command stops the script; an `if` condition is the only test whose failure does not,
  and it is used only where the script reacts explicitly. Installs read only from the staging copies
  (`install -o -g -m`); there is no `cp -a` and no recursive `chmod`.
- **Step log.** Before each numbered step a script runs `step begin <x> <k>` and after it `step done <x> <k>`, where
  `step` calls the reviewed helper `step.py`, which appends one line to `log/S-<x>.log` and syncs it. A stopped script
  therefore leaves a log whose last `begin` without `done` names the interrupted step.
- **No automatic undo is claimed; reconciliation S-R.** A stopped script can leave partial state (for example
  `groupadd` done and `useradd` not). The only automatic action in any script is the removal, in S-D and S-E, of a
  just-installed configuration file that its own syntax check rejects, and only if its bytes still equal the staged
  copy, so that `sudo` and `sshd` stay usable. After any stop the operator runs the reviewed reconciliation
  `S-R <x>`, which:
  1. reads `log/S-<x>.log`;
  2. observes every object that any begun step of S-<x> can touch, with the prestate methods (`getent`, `absent.py`,
     `lstat`, `getfacl -n -c -p`, digests, `systemctl show`, `loginctl show-user`);
  3. classifies each object as *prestate* (equal to its P-capture), *expected-post* (equal to the documented result
     of the step that creates it) or *other*;
  4. if no object is *other* and the *expected-post* objects are exactly those of a prefix of S-<x>'s steps, offers
     the operator two actions, each needing an explicit choice: *resume* (run the remaining steps from the first step
     without `done`) or *reverse* (remove the *expected-post* objects in reverse step order with the reviewed
     per-object command: `userdel <name>` without `-r` for an account that owns no file (`find / -xdev -uid <n>`
     empty), `groupdel <name>` for a group with no member that owns no file, `rm -- <file>` for a file whose bytes
     equal the staged copy, `rmdir -- <dir>` for an empty directory, `loginctl disable-linger <user>` for a linger it
     enabled, `setfacl -P --restore=<dump>` for an ACL it changed, followed by `systemctl daemon-reload`, `visudo -c`
     or `sshd -t` where the object belongs to those services);
  5. re-observes every object and retains the captures;
  6. calls an object "reversed" only if its re-observation equals its prestate capture byte for byte.
  Any *other* object, any failed command and any unequal re-observation stops S-R and is reported for an explicit
  operator decision. Nothing is reversed without the operator's choice, and nothing is called undone without that
  equality.

### 11.5 Setup scripts (templates; texts and digests become exact in the concrete inventory)

`<W>`, `<R>`, `<GATE>` are the fixed numbers. Every script begins with the same lines:
```sh
st=/root/wlscratch-staging
py='/usr/bin/python3 -I -B'
step() { $py "$st/step.py" "$@"; }
need_absent() { $py "$st/absent.py" "$@"; }
```
A call of either function is a simple command, so under `set -e` its failure stops the script.

**`absent.py`** (reviewed helper; exit 0 only if every operand is `absent`, 2 if any is `present`, 3 if any is
`undetermined`; one output line per operand):
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

**`step.py`** (reviewed helper):
```python
import os, sys, time
if len(sys.argv) != 4 or sys.argv[1] not in ('begin', 'done'):
    sys.exit(2)
verb, script, number = sys.argv[1:]
fd = os.open('/root/wlscratch-staging/log/S-' + script + '.log', os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW | os.O_CLOEXEC)
try:
    os.write(fd, ('%s %s %s\n' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), verb, number)).encode('ascii'))
    os.fsync(fd)
finally:
    os.close(fd)
```

**S-A, accounts and groups.**
```sh
set -eu; umask 077
step begin A 0
for n in wlscratch wlscratch-run wlscratch-gate; do
  if getent passwd "$n" >/dev/null || getent group "$n" >/dev/null; then echo "S-A: $n exists" >&2; exit 10; fi
done
for i in <W> <R> <GATE>; do
  if getent passwd "$i" >/dev/null || getent group "$i" >/dev/null; then echo "S-A: id $i used" >&2; exit 11; fi
done
need_absent /var/spool/mail/wlscratch /var/spool/mail/wlscratch-run
step done A 0
step begin A 1; groupadd --system --gid <W> wlscratch; step done A 1
step begin A 2; groupadd --system --gid <R> wlscratch-run; step done A 2
step begin A 3; groupadd --system --gid <GATE> wlscratch-gate; step done A 3
step begin A 4
useradd --system --uid <W> --gid <W> --no-create-home --home-dir /var/lib/wlscratch \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame writer' wlscratch
step done A 4
step begin A 5
useradd --system --uid <R> --gid <R> --no-create-home --home-dir /var/lib/wlscratch-run \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame target' wlscratch-run
step done A 5
step begin A 6
for u in wlscratch wlscratch-run; do
  case "$(getent shadow "$u" | cut -d: -f2)" in '!'*|'*'*) : ;; *) usermod -L "$u" ;; esac
  case "$(getent shadow "$u" | cut -d: -f2)" in '!'*|'*'*) : ;; *) echo "S-A: $u not locked" >&2; exit 12 ;; esac
done
need_absent /var/spool/mail/wlscratch /var/spool/mail/wlscratch-run
step done A 6
```
The last check stops the script if `useradd` created a mail spool despite P23; S-R A then decides.

**S-B, writer home, lease, run tree** (without images; with images, step B 4 is replaced by S-J, §14.5, and step B 5
applies to the image roots).
```sh
set -eu; umask 077
step begin B 0; need_absent /var/lib/wlscratch /opt/wlscratch; step done B 0
step begin B 1; install -d -o root -g <W> -m 0750 /var/lib/wlscratch; step done B 1
step begin B 2; install -d -o root -g <W> -m 0750 /var/lib/wlscratch/lease; step done B 2
step begin B 3
touch /var/lib/wlscratch/lease/writer.lock
chown root:<W> /var/lib/wlscratch/lease/writer.lock
chmod 0440 /var/lib/wlscratch/lease/writer.lock
[ "$(stat -c '%F %h %s %u %g %a' /var/lib/wlscratch/lease/writer.lock)" = "regular empty file 1 0 0 <W> 440" ]
step done B 3
step begin B 4
install -d -o <W> -g <W> -m 0700 /var/lib/wlscratch/runs
install -d -o <W> -g <W> -m 0700 /var/lib/wlscratch/runs/records
step done B 4
step begin B 5
setfacl -m u:1000:--x,g:<GATE>:--x /var/lib/wlscratch
setfacl -m u:1000:--x,g:<GATE>:--x /var/lib/wlscratch/runs
setfacl -m u:1000:--x /var/lib/wlscratch/runs/records
getfacl -n -c -p /var/lib/wlscratch              | cmp - "$st/acl/var-lib-wlscratch.expected"
getfacl -n -c -p /var/lib/wlscratch/runs         | cmp - "$st/acl/runs.expected"
getfacl -n -c -p /var/lib/wlscratch/runs/records | cmp - "$st/acl/records.expected"
getfacl -n -c -p /var/lib/wlscratch/lease /var/lib/wlscratch/lease/writer.lock | cmp - "$st/acl/lease.expected"
step done B 5
```
The expected files hold exactly the §6.3 texts (and, for `lease`, only the base entries).

**S-C, frame install** (from the verified staging copy of the frozen v6-W1 tree).
```sh
set -eu; umask 022
step begin C 0; need_absent /opt/wlscratch; step done C 0
step begin C 1; install -d -o root -g root -m 0755 /opt/wlscratch /opt/wlscratch/frame-v6w1; step done C 1
step begin C 2
while read -r d; do install -d -o root -g root -m 0755 "/opt/wlscratch/frame-v6w1/$d"; done < "$st/frame-dirs.list"
while read -r m; do install -o root -g root -m 0644 "$st/frame/$m" "/opt/wlscratch/frame-v6w1/$m"; done < "$st/frame-members.list"
( cd /opt/wlscratch/frame-v6w1 && sha256sum -c --strict "$st/frame-members.sha256" )
step done C 2
```
The v6-W1 source is frozen with every member at 0644 and every directory at 0755, so installed modes equal frozen
modes; the inventory records `install_root = /opt/wlscratch/frame-v6w1` and `source_frame` (v5 checked
`inventory['frame'] == FRAME`; the installed frame checks `install_root` instead, and §4.6 binds `source_frame`).

**S-D, sudo rules** (reviewed bytes, one line each).
- `wlscratch-frame`: `sicarii ALL=(wlscratch) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py *`
- `wlscratch-run` (Option A): `wlscratch ALL=(wlscratch-run : wlscratch-gate) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/launch_target.py *`
- Option B replaces the second file: `wlscratch ALL=(root) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py *`
```sh
set -eu; umask 077
step begin D 0
need_absent /etc/sudoers.d/wlscratch-frame /etc/sudoers.d/wlscratch-run
visudo -cf "$st/sudoers/wlscratch-frame"
visudo -cf "$st/sudoers/wlscratch-run"
step done D 0
step begin D 1; install -o root -g root -m 0440 "$st/sudoers/wlscratch-frame" /etc/sudoers.d/wlscratch-frame; step done D 1
step begin D 2; install -o root -g root -m 0440 "$st/sudoers/wlscratch-run"   /etc/sudoers.d/wlscratch-run;   step done D 2
step begin D 3
if ! visudo -c; then
  for f in wlscratch-frame wlscratch-run; do
    if cmp -s "$st/sudoers/$f" "/etc/sudoers.d/$f"; then rm -- "/etc/sudoers.d/$f"; fi
  done
  echo "S-D: visudo -c failed; staged-equal files removed; run S-R D" >&2; exit 40
fi
step done D 3
```

**S-E, sshd** (reviewed byte line `DenyUsers wlscratch wlscratch-run`).
```sh
set -eu; umask 022
f=/etc/ssh/sshd_config.d/30-wlscratch.conf
step begin E 0; need_absent "$f"; step done E 0
step begin E 1; install -o root -g root -m 0644 "$st/30-wlscratch.conf" "$f"; step done E 1
step begin E 2
if ! sshd -t; then
  if cmp -s "$st/30-wlscratch.conf" "$f"; then rm -- "$f"; fi
  echo "S-E: sshd -t failed; staged-equal drop-in removed; run S-R E" >&2; exit 50
fi
if ! sshd -T -C user=wlscratch,host=localhost,addr=127.0.0.1 | grep -qixF -f "$st/sshd-denyusers.expected"; then
  echo "S-E: DenyUsers not effective; run S-R E" >&2; exit 51
fi
step done E 2
step begin E 3; systemctl reload sshd.service; step done E 3
```

**S-F, target home, masks, user-manager drop-in, linger.** The mask list is derived from P16 at inventory time:
every unit enabled for user managers in `/etc/systemd/user/*.wants`, `*.requires` and in
`/usr/lib/systemd/user/*.wants`, `*.requires`, every unit those activate, and the aliases; **including** `dbus.socket`
and `dbus-broker.service` (v3 kept them; v4's keep set is empty, §2.1 A3), plus `xdg-desktop-autostart.target`.
Observed on 2026-10-05: `/etc/systemd/user` enables, through `default.target.wants`,
`omarchy-native-audio-bridge.service`, `omarchy-native-camera-bridge.service` and `omarchy-native-mac-share-link.service`;
through `graphical-session-pre.target.wants`, `xdg-user-dirs.service`; through `graphical-session.target.wants`,
`omarchy-native-clipboard-bridge.service`; through `pipewire.service.wants`, `wireplumber.service` (also aliased as
`pipewire-session-manager.service`); through `sockets.target.wants`, `gnome-keyring-daemon.socket`,
`p11-kit-server.socket`, `pipewire-pulse.socket` and `pipewire.socket`. `/usr/lib/systemd/user/sockets.target.wants`
enables `dbus.socket`, `dirmngr.socket`, `gpg-agent-browser.socket`, `gpg-agent-extra.socket`, `gpg-agent-ssh.socket`,
`gpg-agent.socket`, `keyboxd.socket`, `systemd-ask-password.socket`, `systemd-importd.socket`,
`systemd-journalctl.socket`, `systemd-machined.socket` and `systemd-storage-fs.socket`. Neither directory has a
`timers.target.wants`. The user generators `systemd-xdg-autostart-generator` and `30-systemd-environment-d-generator`
run only when M starts or reloads, as short-lived children of M; a classification that sees one is not quiescent and
repeats (§9.4). (Existing lingering accounts run `pipewire`, `wireplumber`, `pipewire-pulse` and `dbus-broker`
processes, observed with `ps`; each also has an `(sd-pam)` process, observed 2026-10-05.)

The user-manager drop-in `user-at-R.conf` (reviewed bytes):
```ini
[Service]
PAMName=
Environment=XDG_RUNTIME_DIR=/run/user/<R>
```
The empty `PAMName=` resets the vendor `PAMName=systemd-user`, so systemd starts M without a PAM session and without
the `(sd-pam)` helper; `XDG_RUNTIME_DIR` is set explicitly because `pam_systemd` no longer sets it, and
`user-runtime-dir@<R>.service` still creates `/run/user/<R>` (the vendor unit's `BindsTo=`). That M works this way
(linger start, scope creation, cpu, memory and pids delegation, the runtime directory) is a hypothesis that P-MGR
verifies; if it fails, W-1 must be redesigned, and no `(sd-pam)` exception is taken (§2.4 R7).
```sh
set -eu; umask 022
h=/var/lib/wlscratch-run
d=/etc/systemd/system/user@<R>.service.d
step begin F 0; need_absent "$h" /var/lib/systemd/linger/wlscratch-run "$d"; step done F 0
step begin F 1; install -d -o root -g root -m 0755 "$h" "$h/.config" "$h/.config/systemd" "$h/.config/systemd/user"; step done F 1
step begin F 2; install -d -o <R> -g <R> -m 0700 "$h/tmp"; step done F 2
step begin F 3; while read -r u; do ln -s /dev/null "$h/.config/systemd/user/$u"; done < "$st/masks.list"; step done F 3
step begin F 4
install -d -o root -g root -m 0755 "$d"
install -o root -g root -m 0644 "$st/user-at-R.conf" "$d/50-wlscratch.conf"
systemctl daemon-reload
[ -z "$(systemctl show 'user@<R>.service' -p PAMName --value)" ]
step done F 4
step begin F 5; loginctl enable-linger wlscratch-run; step done F 5
```
`ln -s` without `-f` fails if a name exists; the masks and the drop-in precede linger, so M first starts with them in
place.

**S-G, Option A only: home traverse entry** (operator; agents never stat the home directory).
```sh
set -eu
step begin G 0
getfacl -n -p /home/sicarii   | cmp - "$st/home-acl.pre.dump"       # P21 restore dump; a concurrent change stops here
getfacl -n -c -p /home/sicarii | cmp - "$st/home-acl.pre.expected"  # P21 comparison text
step done G 0
step begin G 1; setfacl -m g:<GATE>:--x /home/sicarii; step done G 1
step begin G 2
getfacl -n -c -p /home/sicarii | cmp - "$st/home-acl.post.expected" # pre + the entry + the recalculated mask
getfacl -n -p /home/sicarii   | cmp - "$st/home-acl.post.dump"
step done G 2
```
If step G 2 stops, the operator runs S-R G at once; its reversal is the restore of §15.1 step 7 from
`home-acl.pre.dump`.
**S-G′, Option B only:** no home ACL; `sandbox_launch.py` is a frame member installed by S-C, and its rule is S-D's
Option B line.

**S-H, setup identity record.** A reviewed generator, run as `$py "$st/make_setup_identities.py"
/opt/wlscratch/setup-identities.json`, creates the file with `O_EXCL`, 0644, root:root, holding: the numbers; for every
setup object its path, its class (§11.7), the value of every field §11.7 pins for that class, and the names of the
fields that class leaves intentionally mutable (`mutable_fields`); the mount facts of T_root and R_root (the pinned
image facts with images); the installed frame root identity and member digests; the sudoers, sshd and user-manager
drop-in digests; the mask list digest; the linger file; the digests of `/etc/subuid`, `/etc/subgid` and of the new
`passwd`, `group`, `shadow` and `gshadow` lines. The operator records its sha256.

**S-I, post-setup capture** (operator, read-only): the first character only of each new `shadow` password field;
the `gshadow` line of GATE; sudoers digests and `visudo -c`; `sudo -l -U sicarii` and `sudo -l -U wlscratch`;
`sshd -T -C user=wlscratch,…`; `systemctl show user@<R>.service -p PAMName -p Environment`; R's processes (exactly M:
no `(sd-pam)`, no `dbus-broker`); `absent.py` on `/var/spool/mail/wlscratch` and `/var/spool/mail/wlscratch-run`;
`find / -xdev -perm /6000 -type f` and `getcap -r /usr` compared with P17; `find / -xdev \( -uid <W> -o -gid <W> -o
-uid <R> -o -gid <R> -o -gid <GATE> \)` equal to exactly the setup objects.

**S-R, reconciliation** (operator; interactive): the procedure of §11.4, with, per script, the reviewed list of the
objects each step creates, their expected-post captures and their reversal commands.

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
| Regular setup files: `writer.lock`, `setup-identities.json`, the sudoers files, the sshd and user-manager drop-ins, every installed frame member | type, `dev`, `ino`, uid, gid, mode, `nlink` 1, size, sha256 (`writer.lock`: size 0), no ACL | atime, mtime, ctime | none |
| Mask links | type symlink, `dev`, `ino`, uid 0, gid 0, target `/dev/null`, the exact name set | atime, mtime, ctime | none |
| Static setup directories: `/var/lib/wlscratch`, `lease/`, `/var/lib/wlscratch-run`, `.config`, `.config/systemd`, `.config/systemd/user`, the drop-in directory, `/opt/wlscratch`, the installed frame directories | type, `dev`, `ino`, uid, gid, mode, exact ACL text, exact entry set, `nlink` | atime, mtime, ctime (they move only with the entry set, which is pinned) | none |
| Growing tree directories: `runs/` (T_root) and `runs/records` (R_root) | type, uid, gid, mode, exact ACL text; without images also `dev` and `ino`; with images the mount identity of the next row instead | `nlink`, size, atime, mtime, ctime, the entry set | every entry obeys §3.4's name grammar and is a W-owned directory; W checks it at every invocation |
| `/var/lib/wlscratch-run/tmp` | type, `dev`, `ino`, uid R, gid R, mode 0700, no ACL | `nlink`, size, times, the entries (target temporaries) | none (target-writable residual, §12.3) |
| Image mounts (images only, §14.5) | filesystem UUID and label; the backing image file's `dev`, `ino`, size, mode and owner on the root filesystem; the mount point path; mount options `nosuid,nodev,noexec`; the nesting (records inside work); the image root's uid, gid, mode, ACL and `ino` | the mounted filesystem's `st_dev` (the loop device number), the loop device name, the mount ID | `st_dev` differs from the parent's and equals the device of the mountinfo entry whose loop device's backing file is the pinned image file |
| Bare mount points (images only; observed at setup and rollback while unmounted) | type, `dev`, `ino`, uid 0, gid 0, mode 0700, empty, no ACL | times | must be empty |
| Linger file `/var/lib/systemd/linger/wlscratch-run` | existence, type regular, uid 0, gid 0, size 0 | `dev`, `ino`, times (logind's file) | none |
| M's socket baseline S_socks and unit baseline S_units (§9.4) | the kind, bound name, type and peer class of every socket; the unit names and baseline states | socket inode numbers, pids, invocation ids (boot-local) | compared by kind, name and peer class only |

The setup identity record stores, for every object, the class and the pinned values; `/run/user/<R>` is not a setup
object (logind recreates it) and is observed per invocation.

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
writer invocation and every O and C stage). Each image root contains `lost+found` from `mkfs.ext4` (§3.4). The mount
units `var-lib-wlscratch-runs.mount` and `var-lib-wlscratch-runs-records.mount` carry `Options=loop,nosuid,nodev,noexec`;
the records unit has `Requires=` and `After=` on the work unit; both are enabled through `local-fs.target` as their only
start source; there is no automount unit and no fstab line. A_tmp's places are not on the images.

**S-J, images (only if chosen; replaces step B 4 of S-B; every step logged as in §11.4).**
- J0: `need_absent /var/lib/wlscratch-images /var/lib/wlscratch/runs` and the two mount-unit paths.
- J1: `install -d -o root -g root -m 0700 /var/lib/wlscratch-images`.
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
not closure, not executed evidence and not acceptance. "CLOSED (gpt61-v3), carried" marks items the gpt61-v3 review
closed; v4 keeps them unchanged in substance. Every original obligation, V5-B01, V5-B02 and Gate 0 stay OPEN
regardless.

### 18.1 The gpt61-v3 review's required corrections

| Correction | v4 sections | Author's assessment | Still needed as future evidence |
|---|---|---|---|
| W1-GENERATION-PROTOCOL | §3.2, §4.2-§4.6, §7.1, §7.3, §9.3 (G0-G6, C1-C2, C's refusals), Appendix B.3, B.4, D | CLOSED-AT-SPEC-LEVEL | v6-W1 code implementing the state machines and keysets, and its review; P-LAUNCH (stream identity checks); the installed-evidence review and the adoption run |
| W1-COMMIT-JOURNAL-EXPORT | §10.1-§10.7, §15.3, Appendix B.3 | CLOSED-AT-SPEC-LEVEL | code; P-COMMIT; P-ENOSPC before any claim of durability under allocation failure |
| W1-TERMINAL-CUSTODY | §2.1 A3, §2.4 R7 and R9, §4.5, §9.1, §9.3 (C7, C10, C's refusals), §9.4, §9.7, §11.5 S-F, §13 | CLOSED-AT-SPEC-LEVEL, conditional on the stated premises being verified (the kernel read-lease rule; systemd's serialized dispatch and peer-credential check; a working PAM-less M). If any premise fails, known-terminal ownership becomes unattainable and W-1 must be redesigned; no exception is taken | P-MGR, P-QUIESCE (including the lease and barrier premises), P-STREAM, P-TERM; the reviewed S_units and S_socks |
| W1-DURABILITY-RELEASE | §9.4 (release rule, hold, window write failure), §9.7 RC4, §10.5, §10.7 | CLOSED-AT-SPEC-LEVEL | code; P-COMMIT's release case; P-TERM |
| W1-SETUP-PROBES-ROLLBACK | §11.1, §11.3 (P5, P6, P21, P23, P24), §11.4, §11.5 (`absent.py`, `step.py`, S-A to S-I, S-R), §11.7, §13, §15.1 step 7 | CLOSED-AT-SPEC-LEVEL (templates; exact bytes come with the concrete inventory, as the review allows) | the concrete inventory and its review; P-SETUP; operator setup and S-I; rollback records |
| W1-IMAGE-TREE | §3.3, §3.4, §5.2, §6.3, §9.6, §11.7, §14.5 (layout, S-J) | CLOSED-AT-SPEC-LEVEL | measured image geometry on a sacrificial image; the image inventory (S-J bytes, UUIDs, labels) and its review; P-MOUNT |
| PKG-V6-OPERATOR-TEXT, PKG-SUPERVISION-RECORD | none | not in W-1's scope (the lead's operator package) | — |

### 18.2 The prior required corrections, as the gpt61-v3 review ruled on them

| Prior correction | gpt61-v3 | v4 | Author's assessment |
|---|---|---|---|
| W1-CUSTODY | NOT_CLOSED | refined by the review into W1-GENERATION-PROTOCOL, W1-TERMINAL-CUSTODY and W1-IMAGE-TREE (§4, §9, §3.4) | CLOSED-AT-SPEC-LEVEL with those three (conditional as in §18.1) |
| W1-SETUP | NOT_CLOSED | refined into W1-SETUP-PROBES-ROLLBACK (§11, §13) | CLOSED-AT-SPEC-LEVEL |
| W1-RESOURCES | CLOSED | §14: no allowance or stage budget changed; the new records counted under A_in; §14.3's dispatch step renumbered | CLOSED (gpt61-v3), carried |
| W1-LIFETIME-ROLLBACK | NOT_CLOSED | refined into W1-COMMIT-JOURNAL-EXPORT, W1-DURABILITY-RELEASE and W1-SETUP-PROBES-ROLLBACK (§10, §9.4, §15) | CLOSED-AT-SPEC-LEVEL |
| OD2-CONSEQUENCES, PKG-V5-FACTS, PKG-CLOSURE-STATUS | CLOSED | package items | not in W-1's scope |

### 18.3 The section-3 gaps

| Gap | gpt61-v3 | v4 | Author's assessment | What v4 adds |
|---|---|---|---|---|
| generation-order | NOT_CLOSED | §4, §9.3 G0, Appendix B.3-B.4 | CLOSED-AT-SPEC-LEVEL | stream inodes created and bound before `launcher-intent.json`; verb-specific `attempt.json` schemas; exact per-verb state machines and keysets with failure transitions (adopt, materialize, dispatch, seal-front); the adoption record's writer and destination |
| lease-and-writer-authority | NOT_CLOSED | §5.2, §3.4, §9.7 | CLOSED-AT-SPEC-LEVEL | the complete mutation list inside T in both storage configurations; W2's two modes with their authority and routing; no helper started without the lease |
| per-entry-modes-acls | NOT_CLOSED | §6.3, §15.3 | CLOSED-AT-SPEC-LEVEL | export copies' final mode 0640 and ACL read back before the export marker records them; consumers compare the final values |
| channel-and-dumpability | NOT_CLOSED | §7.1, §7.3, Appendix B.4 | CLOSED-AT-SPEC-LEVEL | exact body keysets for every kind; the bulk carrier rule; per-verb states; a direct W↔C channel |
| prestate-and-installation | NOT_CLOSED | §11 | CLOSED-AT-SPEC-LEVEL | an ENOENT-exact absence helper; fail-stop scripts with step logs and S-R; pinned versus mutable setup fields |
| exposure-options | CLOSED | §12 | CLOSED (gpt61-v3), carried | §12.3 updated for the masked bus |
| fresh-identities-and-vault | CLOSED | §8 | CLOSED (gpt61-v3), carried | the vault path moved to the record root |
| denial-probes | NOT_CLOSED | §13 | CLOSED-AT-SPEC-LEVEL | operand, precondition and errno tables per actor consistent with §6.3 and §6.5; same-mount preconditions; the families P-QUIESCE, P-STREAM, P-COMMIT, P-SETUP and P-MOUNT |
| resources-and-images | CLOSED | §14 | CLOSED (gpt61-v3), carried | image routing handled under W1-IMAGE-TREE |
| commits-and-durable-channel | NOT_CLOSED | §10 | CLOSED-AT-SPEC-LEVEL | allocation descriptor versus append-only slots; short-write and torn-slot rules; the consumer table; journals with committed chains across writers |
| participants-and-recovery | NOT_CLOSED | §9 | CLOSED-AT-SPEC-LEVEL (conditional as in §18.1) | the baseline reduced to M; quiescence, references and the lease test; the absorbing-state argument; writer-death recovery with complete scans through W2 and O; no inference from missing child-start evidence |
| rollback-and-evidence | NOT_CLOSED | §15 | CLOSED-AT-SPEC-LEVEL | the headed restore dump kept apart from the comparison text, with concurrent-change checks and retained captures; finite export cuts and later increments for W2's terminal evidence |

### 18.4 The original W-1 subgaps

| Subgap | gpt61-v3 | v4 | Author's assessment |
|---|---|---|---|
| W1-CUSTODY | NOT_CLOSED | §3.4, §4, §9.4 | CLOSED-AT-SPEC-LEVEL (conditional as in §18.1) |
| W1-FINAL-PASS | CLOSED | §4.5 | CLOSED (gpt61-v3), carried; the lease test is added inside the same walk |
| W1-CLOSURE | NOT_CLOSED | §4.2, §4.6, §11.7, §16 | CLOSED-AT-SPEC-LEVEL |
| W1-CHANNEL | NOT_CLOSED | §7, Appendix B.4 | CLOSED-AT-SPEC-LEVEL |
| W1-WRITE-AUTHORITY | NOT_CLOSED | §3.4, §5.2, §9.7 | CLOSED-AT-SPEC-LEVEL |
| W1-READ-ACCESS | CLOSED | §4.2 (M6), §8.6 | CLOSED (gpt61-v3), carried |
| W1-READ-EXPOSURE | CLOSED | §12 | CLOSED (gpt61-v3), carried |
| W1-PREFLIGHT-IDENTITY | CLOSED | §8 | CLOSED (gpt61-v3), carried |
| W1-SETUP-PRESTATE | NOT_CLOSED | §11.1-§11.3, §11.7 | CLOSED-AT-SPEC-LEVEL |
| W1-SETUP-ORDER | CLOSED | §16 | CLOSED (gpt61-v3), carried; refined by the adoption step |
| W1-SETUP-EXACTNESS | NOT_CLOSED | §11.4-§11.5 | CLOSED-AT-SPEC-LEVEL (templates) |
| W1-IMAGE-GEOMETRY | CLOSED | §14.5 | CLOSED (gpt61-v3), carried |
| W1-IMAGE-COMPATIBILITY | CLOSED | §14.5 | CLOSED (gpt61-v3), carried |
| W1-VERIFICATION-PROBES | NOT_CLOSED | §13 | CLOSED-AT-SPEC-LEVEL |
| W1-FAILURE-LEASE | NOT_CLOSED | §9.4, §9.5, §9.7 | CLOSED-AT-SPEC-LEVEL |
| W1-FAILURE-RECORDS | NOT_CLOSED | §10, §15.3 | CLOSED-AT-SPEC-LEVEL |
| W1-REBOOT-RECOVERY | NOT_CLOSED | §9.6, §10.2, §10.4, §11.7 | CLOSED-AT-SPEC-LEVEL |
| W1-ROLLBACK | NOT_CLOSED | §11.4, §15.1-§15.2 | CLOSED-AT-SPEC-LEVEL |
| W1-EVIDENCE | NOT_CLOSED | §15.3-§15.4 | CLOSED-AT-SPEC-LEVEL |
| W1-NONCLAIMS | CLOSED | header, §20 | CLOSED (gpt61-v3), carried |

### 18.5 Change map

| v4 section | Status relative to v3 | Correction(s) |
|---|---|---|
| header, §0 | revised | all |
| §1 | carried byte-for-byte | — |
| §2.1 | revised (A1's last sentence, A2, A3) | W1-TERMINAL-CUSTODY |
| §2.2 | carried | — |
| §2.3 | revised (leases, mount IDs) | W1-TERMINAL-CUSTODY, W1-SETUP-PROBES-ROLLBACK |
| §2.4 | revised (R6's last sentence, R7, R9) | W1-TERMINAL-CUSTODY |
| §3.1 | carried | — |
| §3.2 | revised (verbs, M, S3, W2 modes, compiled review paths) | W1-GENERATION-PROTOCOL, W1-TERMINAL-CUSTODY |
| §3.3 | revised (one layout) | W1-IMAGE-TREE |
| §3.4 | new | W1-IMAGE-TREE |
| §4.1-§4.5 | revised | W1-GENERATION-PROTOCOL; §4.5 also W1-TERMINAL-CUSTODY |
| §4.6 | new | W1-GENERATION-PROTOCOL |
| §5.1 | carried | — |
| §5.2 | revised | W1-IMAGE-TREE, W1-TERMINAL-CUSTODY |
| §5.3 | revised (the user-manager, system-unit and existing-process rows) | W1-TERMINAL-CUSTODY |
| §5.4 | carried | — |
| §6.1 | carried | — |
| §6.2-§6.5 | revised | W1-IMAGE-TREE, W1-COMMIT-JOURNAL-EXPORT, W1-SETUP-PROBES-ROLLBACK |
| §7.1 | revised (direct W↔C channel, binding before start) | W1-GENERATION-PROTOCOL |
| §7.2 | carried | — |
| §7.3 | revised (hello nonces, bulk carriers, retained references) | W1-GENERATION-PROTOCOL |
| §7.4 | carried | — |
| §7.5 | revised | W1-GENERATION-PROTOCOL, W1-COMMIT-JOURNAL-EXPORT |
| §7.6, §7.7 | carried | — |
| §8.1-§8.3 | carried | — |
| §8.4 | revised (the user-bus note, the baselines) | W1-TERMINAL-CUSTODY |
| §8.5 | revised (the vault path) | W1-IMAGE-TREE |
| §8.6 | revised (the adoption record is a protected record) | W1-GENERATION-PROTOCOL |
| §9.1-§9.6 | revised | W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE, W1-GENERATION-PROTOCOL |
| §9.7 | new | W1-TERMINAL-CUSTODY, W1-DURABILITY-RELEASE |
| §10 | revised | W1-COMMIT-JOURNAL-EXPORT, W1-DURABILITY-RELEASE |
| §11.1, §11.3-§11.6 | revised | W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY |
| §11.2 | carried | — |
| §11.7 | new | W1-SETUP-PROBES-ROLLBACK |
| §12.1, §12.2 | carried | — |
| §12.3 | revised | W1-TERMINAL-CUSTODY |
| §13 | revised | W1-SETUP-PROBES-ROLLBACK, W1-TERMINAL-CUSTODY, W1-COMMIT-JOURNAL-EXPORT, W1-IMAGE-TREE |
| §14 introduction, §14.3 (D10 only), §14.5 | revised | W1-IMAGE-TREE |
| §14.1, §14.2, §14.4, §14.6 | carried | — |
| §15 | revised | W1-SETUP-PROBES-ROLLBACK, W1-COMMIT-JOURNAL-EXPORT |
| §16, §17 | revised | W1-GENERATION-PROTOCOL |
| §18-§20 | revised | — |
| Appendix A | carried byte-for-byte | — |
| Appendix B.1 | carried | — |
| Appendix B.2-B.4 | revised | W1-GENERATION-PROTOCOL, W1-COMMIT-JOURNAL-EXPORT, W1-TERMINAL-CUSTODY |
| Appendix C | revised (v4 rows added) | — |
| Appendix D | new | W1-GENERATION-PROTOCOL |

### 18.6 New design elements in v4 that need the reviewer's attention

1. The target account reduced to M alone: every user unit masked including the user bus, and M without a PAM session
   through the `user@<R>.service` drop-in (§11.5 S-F), with two compatibility hypotheses (no allowlisted action uses
   the session bus; M works without PAM) and a fail-closed consequence if either fails.
2. SCAN-QUIESCE with its synchronous barrier and the absorbing-state argument (§9.4 (b)), resting on installed systemd
   behaviour (serialized dispatch, peer-credential check) that P-MGR and P-QUIESCE must verify.
3. SCAN-LEASE: the kernel's read-lease refusal used as a global test for writable open descriptions, including queued
   and unreadable ones (§9.4), a premise P-QUIESCE must verify.
4. The direct W↔C channel, replacing v3's relay through L (§7.1, §9.3).
5. The adoption record inside T, written by W, with F's lead-context joins, W's structural re-verification and two
   sealed reviews, of the code and of the installed evidence (§4.6).
6. One layout for both storage choices, with the record root inside T and the records image mounted there (§3.4,
   §14.5).
7. Export increments with disjoint cuts, and a final freeze marker that is reported to F instead of exported (§15.3).
8. W2's `recover` mode (§9.7), and release without any durability precondition (§9.4).
9. Fail-stop setup with step logs and the operator-chosen reconciliation S-R (§11.4).

## 19. Future execution and installed evidence (none of it exists)

- Frame v6-W1 code for every role and verb (`adopt`, `materialize`, `dispatch`, `seal-front` in both modes,
  `selftest`), frozen, with its own actual gpt-6.1-sol review: the excluded-leaf keys, the lease test, the state
  machines and keysets, commit markers, journals, the fallback journal, exports, the scans with quiescence, recovery,
  the anti-setid filter, the selftest verbs and probes, and the helpers.
- The concrete setup inventory (fixed numbers, P1-P24 outputs, script texts and digests including S-J and S-R,
  expected ACL texts and restore dumps, mask list, sudoers, sshd and user-manager drop-in bytes, the Option A or B
  text) and its review; JACKAL bounds for the subordinate-range checks.
- Option B's concrete code, rule and probes, if Option B is pursued, and their review.
- Operator approval and execution of S-0 to S-I (and S-J if images are chosen), with S-I captures; S-R records if a
  script stops.
- Post-setup verification (§11.6); every probe of §13 with raw records, including P-MGR, P-QUIESCE, P-STREAM,
  P-COMMIT, P-ENOSPC, P-SETUP and, with images, P-MOUNT; V-VAULT.
- The new baselines (relocated runtime closure, R's manager environment without PAM, S_units and S_socks, writer
  context, tool inventory per option) as reviewed installed evidence; the installed-evidence review; the adoption run.
- Fresh storage readings and Gate 0 receipts for every stage; measured image geometry if images are chosen.
- First engineering-run evidence for the compatibility hypotheses: no `HOME` writes, no partition-root removal, no
  set-user-ID or set-group-ID mode, no `io_uring` or `openat2` use and no session-bus use by the allowlisted actions,
  and a working PAM-less M.
- Rollback execution records, whenever rollback happens.
- Independent actual gpt-6.1-sol review of all of the above. Only then can V5-B01 and V5-B02 be assessed against
  exact successor evidence.

## 20. Non-claims

- No sufficiency is claimed for V5-B01, V5-B02 or any original obligation. All stay OPEN until exact successor
  evidence meets the original required changes, with their original owners, releases and dependencies.
- Nothing here is executed or installed evidence. Design statements, templates and probe specifications are plans.
  The few passive host observations are dated and attributed, and they are not setup evidence.
- The account and gate design gives a kernel-enforced writer and generation boundary under the stated trusted base
  and preconditions. It is not proof of the frame code, not lead authentication (R2), not confinement of the running
  target (R3), not custody of the toolchain (R4), and no protection from root.
- The quiescence and lease arguments rest on kernel and systemd behaviour that is stated, not yet observed on this
  host. Until P-MGR and P-QUIESCE pass they are premises; if one fails, known-terminal ownership becomes unattainable
  (a hold) and W-1 must be redesigned. Nothing is weakened to make them pass.
- Integrity of the channels is not sender authentication.
- No storage capacity is established. Allowances are labelled judgments, never bounds; the arithmetic is exact
  arithmetic outside the Lean certificate chain (status `exact`, not `formal-bounded`) and is informational only.
- Images enforce write limits only. ENOSPC is never an accepted refusal and never capacity.
- Exports and lead copies are evidence records, not authentic producer custody; a vault transfer is backup.
- Fallback and durability-UNKNOWN records earn no success credit; they have no release effect.
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

### B.2 Participants, waits, scopes, scans

- `wlscratch-participant-v1`: `role` ∈ {`S1`, `W`, `S2`, `L`, `SR/C`, `T`, `S_O`, `O`, `S3`, `W2`, `RL`, `M`}; `pid`,
  `start_time_ticks`, `ppid` (int); `uids`, `gids` (4 ints); `groups`; `cmdline` (list of str); `cgroup` (str);
  `observed_by` (role); `state` ∈ {`alive`, `absent`, `reused`, `unknown`}.
- `wlscratch-wait-v1`: `waiter_role`, `waited_role`; `pid`, `start_time_ticks` (int); `raw_status` (int or null);
  `exited`, `signaled`, `core_dumped` (bool); `exit_code`, `signal` (int or null); `wait_error` (object or null);
  `interrupts` (list); `unresolved` (bool); `meaning` (str).
- `wlscratch-scope-v1`: `manager_uid` (int); `unit` (str); `invocation_id` (str); `control_group` (str);
  `properties_at_start`, `properties_at_end` (objects with `LoadState`, `ActiveState`, `SubState`, `Result`,
  `ControlGroup`, `MemoryMax`, `MemorySwapMax`); `cgroup_state` ∈ {`ABSENT`, `EMPTY`, `NONEMPTY`, `UNAVAILABLE`}.
- `wlscratch-scan-v2`: `point` ∈ {`parent`, `child`, `after`, `recovery`, `release`}; `round` (int or null);
  `classifier` (participant); `known` (list of participant: K(P), §9.4); `scans` `{gate, r, w, name, scope, units,
  refs, quiesce, lease}`, each `{result, unknown: [reason]}`, where `result` is: for `gate`, `r`, `w`, `name` a list of
  participants; for `scope` a `wlscratch-scope-v1`; for `units` `{loaded: [{unit, load, active, sub}], jobs: [{id,
  unit, type}], unit_files: [path]}`; for `refs` `{entries_checked, references: [{where, dev, ino, path}]}`; for
  `quiesce` `{sockets: [{fd, ino, type, state, name, peer_ino, peer_name, rqlen}], foreign_connections: [ino],
  barrier: {call, answered_at}, repeat_equal}`; for `lease` `{files_tested, refused: [{path, errno}], not_owned:
  [path], leases_enable}`; at the release point `units`, `refs`, `quiesce` and `lease` are `null`. `verdict` ∈
  {`known-terminal`, `live`, `unknown`} at the after and recovery points, and ∈ {`pass`, `refuse`, `unknown`} at the
  parent, child and release points.

### B.3 Records

| Record | Schema name | Keys beyond the common fields |
|---|---|---|
| `generation.json` | `wlscratch-generation-v1` | `created_at`, `writer` (B.1), `invocation` `{argv, sudo_user, sudo_uid, sudo_command, n_f}`, `front_triple` `{pid, start_time_ticks, boot_id}`, `lease` `{lease_dir: [dev, ino], lock: [dev, ino], uid, gid, mode}`, `location_chain` (list of `{name, dev, ino, uid, gid, mode, acl_sha256}` from `/` to g), `record_chain` (the same from `/` to g_rec), `mounts` (the §3.4 mount facts; empty without images), `installed_frame` `{inventory_sha256, inventory_bytes, install_root, source_frame}`, `setup_identities_sha256`, `channel` `{protocol, n_f, n_w, genesis}`, `verb`, `run_label`, `attempt0` |
| `inputs/<seq>-<name>` and its `.json` header (P_adm; P_att for `dispatch`) | `wlscratch-input-v1` (header) | raw bytes file; header `{seq, name, class ∈ {pinned, joined, observation}, size, mode, sha256, pin_source, verdict}` (§8.6) |
| `inputs/manifest.json` | `wlscratch-inputs-manifest-v1` | `entries` (list of `{seq, name, class, size, mode, sha256, written_to}`), `heads_after_inputs` |
| `materialization.json` | `wlscratch-materialization-v1` | every v5 `claude-scratch-materialization-v5` key (with `run` = g's path), plus `generation_pin` `{record, marker}`, `inputs_manifest_pin`, `partition_roots` (list of `{path, dev, ino, mode, acl_text}`), `recipe_mode_property` `{files_others_readable, dirs_others_searchable}`, `channel_heads` |
| `attempt.json`, kind `materialize` | `wlscratch-attempt-materialize-v1` | `kind` = `materialize`, `created_at`, `writer` (B.1), `invocation`, `front_triple`, `generation_pins` exactly `{generation, generation_marker}`, `lease`, `channel`, `verb`, `args` `{label, overlay_dir}` |
| `attempt.json`, kind `dispatch` | `wlscratch-attempt-dispatch-v1` | `kind` = `dispatch`, `created_at`, `writer` (B.1), `invocation`, `front_triple`, `generation_pins` exactly `{generation, generation_marker, materialization, materialization_marker}`, `adoption` `{record, marker}`, `lease`, `channel`, `verb`, `args` `{action, args, inbox}` |
| `fallback-allocation.json` | `wlscratch-fallback-allocation-v1` | `path`, `dev`, `ino`, `uid`, `gid`, `mode`, `bytes`, `slot_bytes`, `slots`, `st_blocks`, `created_at` |
| `front/front-identity.json`, `front/front-stage-<stage>.json` | `wlscratch-front-stage-v1` | `stage`, `front` (B.1 at stage), `lead_observation`, `frame_admission_front` `{inventory, review, installed_review, adoption, rollout, adoption_observation}`, `base_tree_observation`, `runtime_observation` (compact or full, v5 item 4), `manager_environment`, `sibling_units`, `storage_reading`, `window_ownership` (child stage), `vault` (where run) |
| `observer-intent-<n>.json` (also under `w2-<k>/`) | `wlscratch-observer-intent-v1` | `n`, `stage` ∈ {`parent`, `after`, `recover`}, `observer_argv`, `n_o`, `streams` (list of `{name, dev, ino}`) |
| `observer-<n>-<stage>.json` (also under `w2-<k>/`) | `wlscratch-observation-v1` | `n`, `stage`, `observer` (B.1), `walk` (with every excluded leaf's `stat_key`), `identities` (v5), `sample_half`, `scan` (`wlscratch-scan-v2`), `report` (descriptor or null) |
| `launch.json` | v5 keys plus | `generation_pin`, `attempt_pin`, `parent_observation_pin` (O's full walk incl. excluded-leaf keys), `launcher_argv_template`, `child_argv_template` (C), `streams` (names), `front_stage_pins`; v5 `environment` holds the relocated environment; v5 `adoption` is the descriptor of `lead-adoption.json` |
| `reservation-intent.json`, `reservation.json` | v5 keys plus | `window_lock_identity` `{dev, ino, nlink}` observed by F under the lock, `request_digest` |
| `admission.json` | v5 keys plus | `gate0_receipt_pin`, `front_stage_pins`, `observer_parent_pin`, `writer_half_pins` |
| `launcher-intent.json` | v5 `scope_argv` plus | `launcher_argv`, `seals` `{launch_sha256, admission_sha256}`, `n_wl`, `n_c`, `streams` (list of `{name, dev, ino}`, exactly the stream names of D14), `journal_head` |
| `launcher-start.json`, `launcher-wait.json`, `sudo-launcher-wait.json`, `observer-wait-<n>.json` | B.2 participant or wait | — |
| `child-wrapper.json`, `child-stage-child.json`, `child-admission-summary.json`, `effective-limits.json`, `child-start.json`, `child-wait.json`, `child-refusal.json`, `child-cleanup.json` | v5 keys (`child-stage-child.json`: C's target-context observations of the child stage; `child-admission-summary.json`: the digests of every C1-C7 result) | sent by C over SP_C and committed by W; plus `channel` `{c2w_head}`; `child-refusal.json` keeps v5's `target_started: false` and its meaning, and is sent only from C's pre-spawn path |
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
| `w2-<k>/recovery/scan-<r>.json` | `wlscratch-scan-v2` | B.2, with `point` = `recovery` and `round` = r |
| `w2-<k>/recovery/result.json` | `wlscratch-recovery-result-v1` | `verdict` ∈ {`known-terminal`, `live`, `unknown`}, `rounds`, `last_scan_pin`, `target_started`, `participants` (list of B.2) |
| `w2-<k>/front-terminal.json` | `wlscratch-front-terminal-v2` | `mode`, `s1_wait` (B.2), `w_final` (or null), `w_absent`, `answers_forwarded` (list of `{n, sha256, at}`), `interrupts`, `errors`, `heads`, `durability`, `recovery` (bool), `recovery_result_pin` (or null), `release` `{performed, intent_state, record_state}` |
| `commits/<seq>-<pathhash16>.commit` | `wlscratch-commit-v1` | `seq`, `record` `{path, sha256, bytes, mode, acl_sha256}`, `kind` ∈ {`primary`, `retry`, `export`} |
| fallback slot payload | `wlscratch-fallback-v1` | `record_name`, `stage`, `errors`, `value_sha256`, `value_bytes`, and exactly one of `value` or `value_truncated: true` |
| `export/generation/manifest.json`, `export/<A>/inc-<n>/manifest.json`, `adoption-<I>/export/inc-<n>/manifest.json` | `wlscratch-export-v2` | `increment`, `entries` (list of `{export_path, source_path, sha256, bytes, mode, acl_sha256, source_marker_sha256, state}`), `directories` (list of `{path, dev, ino, mode, acl_sha256}`) |
| the matching `freeze.json` | `wlscratch-freeze-v2` | `increment`, `cut` `{journal, seq, sha256}`, `slot_range` `{from, to}` (null for the generation and adoption journals), `previous_freeze_marker`, `export_markers` (list of sha256), `manifest_sha256`, `heads` |
| `channel/<channel>-<first>-<last>.json` | `wlscratch-channel-segment-v2` | `channel`, `messages` (list of `{dir, seq, prev, kind, length, payload_sha256}` plus either `payload` or `ref`, where `ref` is `{record, offset, length, sha256}`, `{written, offset, length, sha256}` or `{source, offset, length, sha256}`) |
| `adoption-<I>/invocations/<stamp>/invocation.json` | `wlscratch-adopt-invocation-v1` | `created_at`, `writer` (B.1), `invocation`, `front_triple`, `lease`, `channel`, `installed` `{inventory_sha256, install_root, source_frame, setup_identities_sha256}` |
| `adoption-<I>/lead-adoption.json` | `wlscratch-lead-adoption-v1` | every key of v5's `claude-scratch-frame-lead-adoption-v5` record (with `frame` = INSTALL_ROOT), plus `source_frame`, `setup_identities_sha256`, `installed_review` `{review_sha256, review_freeze_sha256, review_report_sha256, reviewer_thread, rollout, turn_contexts, session_providers, exec_argv, exec_argv_record, event_stream, rollout_final_message_sha256, rollout_final_timestamp}`, `invocation_pin` |

### B.4 Channel kinds (body key sets) and the states that permit them [correction: W1-GENERATION-PROTOCOL]

**B.4.1 Conventions.** Types: `hex64` and `hex32` are lowercase hex strings of that length; `desc` is
`{path: str, sha256: hex64, bytes: int, mode: int}` (v5's `pin` shape); `pin` is `{record: desc, marker: hex64}`;
`identity` is B.1; `participant` and `wait` are B.2. Every body has exactly the listed keys. A kind marked *carrier*
has the key `bulk` (list of str) and is followed immediately by one `BEGIN`/`CHUNK`/`END` sequence per listed name, in
that order (§7.3): `BEGIN` `{name: str, size: int, mode: int, sha256: hex64, chunks: int}`, with `chunks` = 0 exactly
when `size` = 0; `CHUNK` `{index: int, data_b64: str}`; `END` `{sha256: hex64}`. A kind marked *fds* is sent in one
`sendmsg` carrying exactly the listed descriptors as `SCM_RIGHTS` ancillary data, in the listed order; other ancillary
data, or none, is a channel failure.

**B.4.2 F↔W and F↔W2 kinds.**

| Kind | Direction | Body keys (types) |
|---|---|---|
| `W_HELLO` | W→F | `nonce` (hex64), `verb` (str: `adopt`, `materialize`, `dispatch`), `writer` (identity), `generation` (hex32 or null), `attempt` (str or null), `committed` (list of pin) |
| `W2_HELLO` | W2→F | `nonce` (hex64), `mode` (str: `seal`, `recover`), `writer` (identity), `generation` (hex32), `attempt` (str), `w2_dir` (str), `capability` (object: `front_triple`, `s3`, `front_parent`, `verified`), `attempt_writer_state` (str: `absent`, `reused`), `committed` (list of pin) |
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
| `TARGET_EXITED` | W→F | `wait` |
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
| `MATERIALIZED` | W→F | `generation` (pin), `materialization` (pin), `generation_export` (object: `manifest` desc, `freeze` desc, `freeze_marker` hex64) |
| `ADOPTED` | W→F | `adoption` (pin) |
| `EXPORTED` | W→F, W2→F | `increment` (int), `cut` (object: `journal` str, `seq` int, `sha256` hex64), `manifest` (desc), `freeze` (desc), `freeze_marker` (hex64) |
| `STOP` | F→W, F→W2 | `reason` (str) |
| `FINAL` | W→F, W2→F | `exit_status` (int), `success` (bool), `released` (bool or null), `durability` (str: `complete`, `UNKNOWN`), `unknown_records` (list of str), `fallback_records` (list of str), `exports` (list of objects: `increment` int, `freeze_marker` hex64) |
| `BYE` | F→W, F→W2 | no key |

After `RELEASE_DONE`, the writer commits `window-release.json` when `reread` is `released` and `release-failure.json`
otherwise.

**B.4.3 W↔L, W↔C, W↔O and W2↔O kinds.**

| Channel | Kind | Direction | Body keys (types) |
|---|---|---|---|
| W↔L | `L_HELLO` | L→W | `nonce` (hex64), `launcher` (identity) |
| W↔L | `GO` | W→L | carrier; `echo` (hex64), `bulk` (exactly `["launch.json", "admission.json", "launcher-intent.json"]`) |
| W↔L | `FDS` | W→L | fds; `names` (exactly `["sp_c", "scope.stdout", "scope.stderr"]`) |
| W↔L | `LAUNCHER_START` | L→W | `participant` (SR/C) |
| W↔L | `L_REFUSAL` | L→W | `stage` (str), `error` (object) |
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
state sends that state's first message; where that first message is a `RECORD_COMMITTED`, the record name the table
gives identifies it; a message valid neither in the current state nor as the first message of a permitted next state
is a channel failure (§7.4). In every F↔W and F↔W2 state the writer may also send
`RECORD_COMMITTED`, `RECORD_FALLBACK` and `RECORD_UNKNOWN` for records it commits in that state, and F may send
`STOP`. Before `PROCEED_LAUNCH`, a `STOP` makes the writer refuse (`REFUSAL`, then the refusal path below); from
`PROCEED_LAUNCH` on, it is forwarded down (§9.2) and the machine continues. Clean EOF is permitted only in `DONE`.

F↔W, verb `adopt`:

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | `W_HELLO` (W→F); `HELLO_ACK` (F→W) | `INPUTS` |
| `INPUTS` | `REQUEST_INPUTS` with phase `adoption` (W→F); one `INPUT` per requested name, in order (F→W); `PHASE_END` (F→W) | `COMMIT` |
| `COMMIT` | `ADOPTED` or `REFUSAL` (W→F) | `EXPORT` |
| `EXPORT` | `EXPORTED` (W→F) | `FINAL` |
| `FINAL` | `FINAL` (W→F); `BYE` (F→W) | `DONE` |

F↔W, verb `materialize`:

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | `W_HELLO`; `HELLO_ACK`; `RECORD_COMMITTED` for `front/front-identity.json` | `INPUTS_DESCRIPTORS` |
| `INPUTS_DESCRIPTORS`, `INPUTS_OVERLAY`, `INPUTS_BASE` | `REQUEST_INPUTS` with phase `descriptors`, `overlay` or `base`; one `INPUT` per name; `PHASE_END`; `PHASE_DONE` | the next of these states, then `MATERIALIZE` |
| `MATERIALIZE` | `MATERIALIZED` (W→F) | `VAULT` |
| `MATERIALIZE` | `REFUSAL` (W→F) | `EXPORT` |
| `VAULT` | `STAGE_REQUEST` with stage `vault`; `STAGE_RESULT`; `RECORD_COMMITTED` | `EXPORT` |
| `EXPORT` | `EXPORTED` | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | `DONE` |

F↔W, verb `dispatch` (refusal path RP0: nothing reserved, `REFUSAL` → `EXPORT`; refusal path RP1: reserved and
nothing launched, `REFUSAL` → `AFTER` → `CONCLUDE` → `RELEASE` → `EXPORT`):

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | `W_HELLO`; `HELLO_ACK`; `RECORD_COMMITTED` for `front/front-identity.json` | `INPUTS` |
| `INPUTS` | `REQUEST_INPUTS` with phase `dispatch` and names `["lead-module"]`; `INPUT`; `PHASE_END`; `PHASE_DONE` | `ADOPTION` |
| `ADOPTION` | `ADOPTION_RECORD` (W→F) | `FRONT_PARENT` |
| `FRONT_PARENT` | `STAGE_REQUEST` with stage `front-parent`; `STAGE_RESULT`; `RECORD_COMMITTED` | `PARENT` |
| `PARENT` | `PARTICIPANT` and record messages for the observer (W→F); a failed join or scan: `REFUSAL` (RP0) | `VAULT` |
| `VAULT` | `STAGE_REQUEST` with stage `vault`; `STAGE_RESULT`; `RECORD_COMMITTED` | `GATE0` |
| `GATE0` | `CHALLENGE` with kind `gate0`; `ANSWER`; `RECORD_COMMITTED`; or `REFUSAL` (RP0) | `LAUNCH_RECORD` |
| `LAUNCH_RECORD` | `RECORD_COMMITTED` for `launch.json` | `RESERVE` |
| `RESERVE` | `RESERVE_REQUEST` (W→F); then `RESERVE_ABORT` (F→W; `REFUSAL`, RP0) or `RESERVE_INTENT_REQ` (F→W); then `RESERVE_INTENT_COMMITTED` (W→F) or `RESERVE_INTENT_REFUSED` (W→F, after which F sends `RESERVE_ABORT`; RP0); then `RESERVE_DONE` (F→W: the window was written, or the write failed and the re-read shows this reservation or is unreadable) or `RESERVE_ABORT` (F→W: the write failed and the re-read shows no reservation; RP0); then `RESERVE_COMMITTED` (W→F) | `MEMORY_GATE` |
| `MEMORY_GATE` | per challenge, at most `MAX_CHALLENGES`: `CHALLENGE` with kind `memory`; `ANSWER`; `RECORD_COMMITTED`; on failure `REFUSAL` (RP1) | `ADMIT` |
| `ADMIT` | `RECORD_COMMITTED` for `admission.json`; `LAUNCH_INTENT_COMMITTED` | `PROCEED` |
| `PROCEED` | `PROCEED_LAUNCH` (F→W) → `RUNNING`; or `STOP` (F→W) → `REFUSAL` (RP1) | `RUNNING` |
| `RUNNING` | W→F: `PARTICIPANT` any number; `STAGE_REQUEST` with stage `front-child` at most once; `PING` at most once, after the front-child result; `TARGET_STARTED` at most once; `TARGET_EXITED` at most once; `REFUSAL` at most once (C refused, or the launch failed before L). F→W: `STAGE_RESULT` with stage `front-child` exactly once after its request; `PONG` exactly once after `PING`; `STOP`. The state ends only when W has recorded the wait of every launch participant it started | `AFTER` |
| `AFTER` | `STAGE_REQUEST` with stage `front-after`; `STAGE_RESULT`; `PARTICIPANT` and record messages for the observer | `CONCLUDE` |
| `CONCLUDE` | `CONCLUSION` (W→F) | `RELEASE` |
| `RELEASE` | F→W exactly one of: `RELEASE_INTENT_REQ`, then `RELEASE_INTENT_RESULT` (W→F), then `RELEASE_DONE` (F→W), then `RELEASE_RECORD_RESULT` (W→F); `RELEASE_WITHHELD`, then `RELEASE_RECORD_RESULT`; `RELEASE_NOT_OWNER`, then `RELEASE_RECORD_RESULT` | `EXPORT` |
| `EXPORT` | `RECORD_COMMITTED` for `final-status.json`; `EXPORTED` | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | `DONE` |

F↔W2, verb `seal-front`:

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | `W2_HELLO` (W2→F); `HELLO_ACK` (F→W2) | `FRONT_TERMINAL` in mode `seal`; `RECOVER` in mode `recover` |
| `RECOVER` | `RECOVERY_SCAN` any number (W2→F); `STOP` (F→W2) ends the rounds; `RECOVERY_RESULT` exactly once (W2→F), after W2's observer has ended | `RELEASE` |
| `RELEASE` | as in `dispatch`, with W2 as the writer; F re-reads the window under the lock first and sends `RELEASE_NOT_OWNER` if this attempt does not hold it | `FRONT_TERMINAL` |
| `FRONT_TERMINAL` | `STAGE_REQUEST` with stage `front-terminal` (W2→F); `STAGE_RESULT` carrying `front-terminal.json` (F→W2); `RECORD_COMMITTED`, `RECORD_FALLBACK` or `RECORD_UNKNOWN` (W2→F) | `EXPORT` |
| `EXPORT` | `EXPORTED` | `FINAL` |
| `FINAL` | `FINAL`; `BYE` | `DONE` |

W↔L:

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | `L_HELLO` (L→W); a `STOP` (W→L) here makes L exit 125 having started nothing | `GO` |
| `GO` | `GO` and `FDS` (W→L); then `LAUNCHER_START` (L→W) → `WAIT`, or `L_REFUSAL` (L→W) → `DONE` with nothing spawned; a `STOP` (W→L) before `LAUNCHER_START` makes L spawn nothing and exit 125 | `WAIT` |
| `WAIT` | `LAUNCHER_WAIT` (L→W) | `DONE` |
| `DONE` | `BYE` (W→L); clean EOF | — |

W↔C:

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | `C_HELLO` (C→W) | `RECORDS` |
| `RECORDS` | `RECORDS` and `STREAMS` (W→C) | `ADMIT` |
| `ADMIT` | C→W: `CHILD_RECORD` any number, `CHILD_STAGE_REQUEST` once; W→C: `CHILD_STAGE_RESULT` once after it; then C→W `SPAWN_REQUEST` → `SPAWN`, or `CHILD_REFUSAL` → `REFUSED`; a `STOP` (W→C) makes C refuse | `SPAWN` |
| `SPAWN` | W→C `SPAWN_OK`; then C→W `CHILD_START` → `RUNNING`, or `CHILD_REFUSAL` (the final pass or a later check failed) → `REFUSED`; a `STOP` (W→C) before `CHILD_START` makes C refuse | `RUNNING` |
| `RUNNING` | W→C `STOP` (C forwards `SIGTERM` to T); C→W `CHILD_WAIT` once, then `CHILD_CLEANUP` at most once, then `C_DONE` | `DONE` |
| `REFUSED` | C→W `C_DONE` | `DONE` |
| `DONE` | clean EOF | — |

W↔O and W2↔O:

| State | Messages, in order | Next |
|---|---|---|
| `HELLO` | `O_HELLO` (O→W) | `REQUEST` |
| `REQUEST` | W→O `OBSERVE_REQUEST` → `RESULT`; or `O_BYE` → `DONE`. W sends exactly one request per observer; W2 may send one per recovery round | `RESULT` |
| `RESULT` | O→W `OBSERVATION`; then `REPORT_BYTES` if the request asked for it | `REQUEST` |
| `DONE` | O→W `O_DONE`; clean EOF | — |

**B.4.5 Channel failures** (any violation of §7.4 or of the machines above):

| Channel, side and moment | Action |
|---|---|
| F↔W at W, before F's window write | `refusal.json` and the export increment if possible; exit non-zero; nothing reserved |
| F↔W at F, before F's window write | stop reading, close the pipe ends, wait for S1; W2 in mode `seal` if `attempt.json` is committed; nothing to release |
| F↔W at W, after F's window write and before `PROCEED_LAUNCH` | refuse (no S2 is started), take the after-stage classification, commit the conclusion and `release-withheld.json` ("front channel failed; release left to the front's recovery or to manual resolution"), export, exit |
| F↔W at W, from `PROCEED_LAUNCH` on | continue the run and its waits (a front EOF never implies a refusal after launch), conclude, commit `release-withheld.json` as above, export, exit |
| F↔W at F, after F's window write | writer-death recovery (§9.7) |
| F↔W2 at W2 | commit what it has (recovery and release records) and its export increment, exit; if no release happened, the window stays held |
| F↔W2 at F | wait for S3; if no release happened and F wrote the window, start W2 in mode `recover` again (§9.7 RC2) until the lead stops F; otherwise the window stays held |
| W↔L at L | before spawning SR: exit 125, nothing started; after: wait for SR, then exit |
| W↔L at W | record the failure; whether a launch happened is decided by the classification; if C appears, W stops it over W↔C |
| W↔C at C | before `SPAWN_OK`: refuse without spawning, with the statement on its stderr; after `CHILD_START`: keep waiting for T, write what it can to its stderr, exit |
| W↔C at W | `target_started` stays `unknown` unless `CHILD_START` or C's refusal arrived; the classification decides |
| W↔O or W2↔O at O | exit 125 |
| W↔O or W2↔O at W or W2 | the observation fails: before launch the stage refuses; at a classification the verdict is `unknown` (§9.4) |

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
