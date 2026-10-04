# Isolation and storage proposal W-1, v2: protected writer and separate target account

**Status.** Lead preparation, 2026-10-04 ~23:20Z. This is a CANDIDATE design for the scratch frame's confinement. It is
not an established sufficient design, not a setup request and not approved.
- No account, ACL, sudo rule, installation, mount or other privileged action is approved or performed.
- Proof dispatch stays blocked by the confinement gate (V5-B01, V5-B02) and the capacity gate (Gate 0).
- v1 (`ISOLATION-STORAGE-PROPOSAL.md`, sha256 `a27d3e74…0442`) is preserved unchanged.
- v2 answers the sealed actual gpt-6.1-sol package review (`wt-1/package-review/gpt61-v1`, verdict NOT_READY). Its W-1
  findings are traced gap by gap in §14.
- Design preparation is routine engineering under the existing authorization (package review, item 3). Only the
  concrete privileged setup in §8 needs the operator, and only after the steps in §8.0.

## 1. Criteria (exact, unchanged)

Source: frame v5's sealed actual gpt-6.1-sol review, `work/claude-scratch-frame-v5/review/gpt61-v1/REVIEW.md:76` and
`:82`.

**V5-B01:**

> "Retain file observation identities through the complete walk and revalidate every encountered leaf, including
> excluded generated leaves, using complete descriptor metadata and named-entry joins at the final admission
> boundary. Bind the accepted source/output generation to the spawn under custody that prevents the admitted
> generation from changing before use. Directory-only revalidation or after-run detection must not substitute for
> pre-launch alias refusal. Preserve the exact base recipe, output partitions, allowlist, caps and original gates."

**V5-B02:**

> "Provide enforced location custody across each frame-owned mutation and the final admission-to-spawn handoff,
> rather than observer-only checks before and after it. Use an independently protected writer/location boundary or
> an equivalent enforced lease that concurrent same-user rename/substitution cannot invalidate while writes or launch
> are possible. Keep original outside-tree authority limited to the documented window protocol and prescribed
> preparation records. Do not relabel frame-owned outside-tree writes as the running-target residual or lower the
> original guarantee; retain this blocker if custody cannot yet be established."

**WORLDLINE monitor rulings, unchanged:**
- An own-inode "detected and refused" residual does not satisfy V5-B02.
- A root-made filesystem, and W-1 itself, are candidates, not established designs or approved actions.
- Storage: "live preflight that budgets measured run growth AND temporary full-restore space above the unchanged
  reserve … If safe capacity cannot be established, keep dispatch deferred."
- "periodic storage sampling plus a factor on the maximum observed write rate does not establish a maximum future
  write rate or stop latency".

**Ineligibility, stated plainly.** No setting chosen under W-1 can close the unchanged obligations by lowering them.
That covers a lowered reserve, a narrowed scope, a waived warning, a relabelled residual, or a narrowed accepted case
or control. Doing any of these leaves the original obligation OPEN.

## 2. Threat model and boundary

**What W-1 must stop.**
1. Concurrent processes of the lead user `sicarii` (other agents and sessions). They must not create, rename,
   substitute, modify or delete any frame-owned location, or the admitted generation, from admission until use and
   through every later frame mutation.
2. The running target. It must not mutate frame-owned locations or records either: the target/writer overlap.

**What W-1 does not stop. These residuals are carried and stated:**
- **The lead's own processes.** W-1 does not protect them from other `sicarii` processes. Observed: Yama
  `ptrace_scope=1` already stops a non-ancestor same-user process from attaching. But `/proc/<pid>/fd` and similar
  read-mode access is not covered by Yama. The front and writer therefore set `PR_SET_DUMPABLE=0` as their first act
  (§5). There is a window before that call, and it is a residual. This boundary is the same as frame v5's, where the
  whole frame ran as `sicarii`.
- **Lead authentication.** The front authenticates the lead only through the reviewed v5 admission protocol: seals,
  the JACKAL challenge and receipt, the fresh lead observation, and window ownership. W-1 makes this no stronger against
  a `sicarii` process forging those inputs.
- **Root.** Root can do anything; it is outside the threat model.
- **The target's own writes.** The target is unconfined outside the tree, writing wherever `wlscratch-run` can. This is
  the ruled `no-target-confinement` residual, and it covers target writes only, never frame writes. W-1 narrows the
  set of writable places from all of `sicarii`'s home to `wlscratch-run`'s home, `/tmp`, `/var/tmp`, `/dev/shm` and
  its runtime directory.
- **The toolchain.** It is executed by path (`target_exec_by_path`, ruled ACCEPTABLE_AS_DOCUMENTED). Its closure is
  re-observed after the run. W-1 claims no custody over the toolchain.

## 3. Principals

| Principal | Account | Runs | Writes |
|---|---|---|---|
| Front | `sicarii` | The lead's own process: reviewed front code from the v6-W1 frame | The shared window (documented protocol) and the vault pin of the generation path (a prescribed preparation record). Nothing else. |
| Writer | `wlscratch` (new; nologin; no password; no linger) | Only the installed reviewed frame, started by the `sicarii`→`wlscratch` sudo rule | Its lease file and everything under one generation root `runs/<G>`, except target output partitions |
| Target launcher and target | `wlscratch-run` (new; nologin; no password; linger for its user manager) | Only the installed reviewed launcher (started by the `wlscratch`→`wlscratch-run` sudo rule), then the exact target command inside a transient `systemd-run --user --scope` | Only inside the output partitions of `runs/<G>`, through ACLs the writer grants, plus the target residual places in §2 |

**Accounts and groups.** Two new users (`wlscratch`, `wlscratch-run`) and two new groups (their user-private
primaries); `1+1 = 2` for each, JACKAL exact. The v1 `wlscratch-clients` group is dropped. `sicarii`'s read access to
evidence comes from ACL entries the owners set (§4, §8), so `sicarii` needs no new group membership and no new login.

**Why two accounts.** With a single writer account, the target ran as the writer's uid. It could then rename or
substitute writer-owned directories during the run. That would leave frame records and later frame writes protected
only by detection, which V5-B02 rejects. With the target on a different uid, kernel DAC (discretionary access
control) prevents it.

## 4. Generation and location lease (enforced custody)

### 4.1 Writer exclusivity

As its first filesystem action after argv validation, the writer opens `/var/lib/wlscratch/lease/writer.lock` and takes
`flock(LOCK_EX|LOCK_NB)`.
- The open uses `O_RDWR|O_NOFOLLOW|O_CLOEXEC`, and the file must be a single-link regular file owned by `wlscratch`,
  mode `0600`.
- `lease/` is `wlscratch:wlscratch 0700`.
- If the lock is held, the writer refuses before any mutation. It writes only to its stderr, which goes to the front.
- The lock is held until the writer exits.

### 4.2 Generation root

Under the lock, the writer creates `G = runs/<128-bit random hex>`.
- It uses the v5 anchored `Dir` machinery: authenticated `mkdir` 0750, descriptor checks, and the location chain
  verified from `/`.
- It then writes the create-only generation record `G/frame/generation.json`. The record binds the items in §5.2.

### 4.3 Who can write each level of the chain

| Path | Owner and mode | Writable by |
|---|---|---|
| `/`, `/var`, `/var/lib` | root | root only |
| `/var/lib/wlscratch` | `root:wlscratch 0750`, plus ACL `u:sicarii:r-x`, `u:wlscratch-run:--x` | root only. The writer cannot rename its own home |
| `/var/lib/wlscratch/runs` | `wlscratch:wlscratch 0750`, plus access and default ACLs (§8.3) | `wlscratch` only |
| `G` and everything the writer creates in it | `wlscratch`, 0750/0640, plus ACLs | `wlscratch` only, except output partitions |
| Output partitions in `G` (v5 "generated output partitions") | `wlscratch`, with ACL `u:wlscratch-run:rwx` and defaults | `wlscratch` and `wlscratch-run` |

### 4.4 Enforcement argument (for review, not yet evidence)

**Who can mutate.** During a writer session, the only principals able to rename, substitute, create, chmod or delete
any frame-owned entry are:
- this writer, made exclusive by §4.1;
- root.

**Why `wlscratch` runs nothing else.** The account has:
- a nologin shell;
- a locked password;
- no SSH keys;
- no linger, so no user manager or timers;
- no crontab;
- no setuid binaries.

**Why `sicarii` and the target cannot mutate.** `sicarii` processes and the target have no write permission on any
frame-owned directory, and the target cannot rename an output partition itself. They also cannot hard-link
writer-owned files: observed `fs.protected_hardlinks=1`.

**Admission-to-use.**
- The final pass (§4.5) runs after the last frame mutation before launch.
- Between that pass and the target's exec, only this writer could change the admitted generation, and it does not.
- The target reads the generation through `r-X` ACLs and cannot write it.

This is the "independently protected writer/location boundary" V5-B02 names. It is enforced by the kernel, not
observed. Whether it is sufficient is for actual gpt-6.1-sol review of the v6-W1 code and of the installed setup
evidence. Nothing here claims sufficiency.

### 4.5 Final pass

The v5 walk keeps every encountered leaf's complete descriptor identity: `stat_key`, plus content digest for
regular files. At the final admission boundary the writer revalidates every encountered leaf by named-entry join,
including excluded generated leaves (for example pre-existing `obj` content in excluded paths), and re-checks each
directory key.
- The v6 working copy's current draft covers accepted files only. The extension to excluded generated leaves is
  required and not yet written.
- The base recipe, output partitions, allowlist, caps and original gates are preserved exactly.

### 4.6 Post-run

The writer observes outputs, which are target-owned files inside partitions, through default ACLs that grant
`wlscratch` read.
- **Target interference.** A target that removes those ACLs, or creates a symlink or other special entry, produces a
  recorded observation failure. That is a non-success outcome. It is never a frame write outside the tree, because
  every frame write goes through anchored writer-owned directories that the target cannot rename.
- **Frame writes outside the tree.** There are none. The writer writes only under `G` and `lease/`.

## 5. Channel and identity binding

### 5.1 Invocation

The front runs:

```
sudo -n -u wlscratch /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/scratch.py <verb> <args>
```

The front writes to the writer's stdin and reads its stdout and stderr through private pipes.
- **Hardening.** Both front and writer call `prctl(PR_SET_DUMPABLE, 0)` first and record the result read back from
  `/proc/self/status`.
- **Framing.** Each message is length-prefixed canonical JSON with a sequence number and a running SHA-256 chain.
  The writer retains every received and sent message in create-only records, together with the chain head.
- **Argument validation.** The sudo rule matches arguments with `*`, so the installed `scratch.py` enforces the exact
  verb grammar: fixed arity and a per-argument regex. The rule cannot authenticate the lead. That is §2's lead
  authentication residual.

### 5.2 What `generation.json` binds

- the lead identity (`claude_lead.LEAD_ID`);
- the front and writer pids and process start times;
- `G`;
- the frame inventory pin and the installed-identity observation (§8.5);
- the JACKAL challenge and receipt digests, under the reviewed v5 admission protocol;
- the window holder, attempt and token, from the front's reserve record digest;
- the verb and arguments;
- every record and export path;
- the exact target launch template;
- the storage observations (§7).

Every later record carries `G` and the chain head.

### 5.3 Target launch

The writer starts the launcher:

```
sudo -n -u wlscratch-run /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/launch_target.py <G> <launch-seal>
```

The launcher:
1. validates `G` and the seal against `G/frame/launch-intent.json`, which it can read but not write;
2. sets the exact reviewed environment: `HOME=/var/lib/wlscratch-run`, `XDG_RUNTIME_DIR=/run/user/<uid>`, the user bus
   address, and the reviewed `PATH`, `GPR_PROJECT_PATH` and toolchain variables;
3. runs `systemd-run --user --scope` with the v5 limits (MemoryMax=8G, MemorySwapMax=0, core 0/0, `-j2`) and the
   exact original target command, in the project directory inside `G`;
4. reports the unit name, the scope cgroup path and the pids on stdout to the writer;
5. waits, and exits with the scope's status.

### 5.4 Sequence

1. The front checks its own preconditions: Gate 0 inputs and a fresh `storage_status.py` reading (§7).
2. The front invokes the writer (§5.1).
3. The writer takes the lease (§4.1), creates `G` (§4.2) and writes `generation.json`.
4. The front streams the inputs (§6).
5. The writer verifies and materializes them, sets the target ACLs, and runs the final pass (§4.5).
6. The writer sends an admission message, carrying the admitted digest and the launch template.
7. The front reserves the shared window under the documented protocol and pins `G` in the vault (§7.2), then sends
   the reservation record digest.
8. The writer writes `launch-intent.json` and starts the launcher (§5.3).
9. The writer waits, then observes and concludes (§4.6).
10. The writer sends the authenticated conclusion. The front checks cgroupfs and releases the window, or keeps it
    reserved (§10).

The front reserves nothing before step 7, and the writer starts no launcher before step 8.

## 6. Inputs and read access

### 6.1 The writer reads nothing under `/home/sicarii`

The front streams every lead-side input over the channel as `{path, size, mode, sha256, bytes}`. The inputs are:
- the base composition;
- overlays;
- the lead module;
- the frame review and adoption records (frozen at mode 0600, readable by the front);
- the START file;
- the fresh-lead-observation input;
- the window snapshot;
- the storage reading.

The front reads them with the v5 anchored descriptor readers.

The writer handles them in two classes:
- **Pinned inputs:** the base inventory, overlay inventory, frame inventory, review and adoption freeze digests. The
  writer verifies each digest against the pins compiled into the installed frame and refuses on any mismatch.
- **Observations:** the window, the storage reading and the lead observation. They are recorded with digests, at the
  same trust as v5.

A concurrent `sicarii` change to a home file between the front's read and materialization therefore yields either the
pinned bytes or a refusal. After materialization the admitted copy lives only in `G`, out of `sicarii`'s reach.

**Consequences:**
- No ACL is added for `wlscratch` anywhere under `/home/sicarii`.
- The frozen 0600 review files keep their modes.
- v1's traverse-ACL design and its exposure are withdrawn for the writer.

### 6.2 The target needs the exact original toolchain path

HANDOFF fixes the command `/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/bin/gnatprove …`. `wlscratch-run`
therefore needs to traverse `/home/sicarii`. `~/opt` and the toolchain tree are already world-readable and
world-traversable (observed in v1's preparation). The operator chooses between two options at setup:

**Option A: traverse ACL.**
- Setup command: `setfacl -m u:wlscratch-run:--x /home/sicarii`.
- **Exposure.** `wlscratch-run` could then read every file under `/home/sicarii` that is readable by others along an
  others-traversable path.
- Before setup, the lead produces a read-only enumeration of exactly that set and puts it in front of the operator.
  - It never lists or stats the home directory's own entries `~/iPad` and `~/iPadBackup`, which are FUSE mounts.
  - It never descends into or lists `~/.local/share/sia/.gbrain`.
  - It counts entries per top-level path rather than reading contents.

**Option B: root-owned sandbox launcher (narrower).**
- A third reviewed sudo rule lets `wlscratch` run a root-owned launcher.
- The launcher builds a private mount namespace: an empty tmpfs over `/home/sicarii`, with only
  `/home/sicarii/opt/gnat` bind-mounted read-only at its exact path. It then drops to `wlscratch-run` (all
  capabilities dropped, `no_new_privs`) and execs the §5.3 launcher.
- No home ACL is needed. But this is privileged code, and it needs its own review and its own install identity.

The lead does not choose between A and B. Both keep the exact original command path.

## 7. Preflight, storage and vault identity

### 7.1 Storage

The front runs `storage_status.py` as `sicarii`. That keeps the authentic HOME, configuration, user bus, reserve,
backup service, offload queue and pins. The front streams the reading to the writer.
- The lead computes Gate 0 with JACKAL and binds the receipt digest into admission.
- The writer also records its own `statvfs` of the `runs` filesystem, as a cross-observation. It is never used as a
  bound.
- `storage_status.py` is never run as `wlscratch`. Under that uid it would read a different HOME and user bus, and the
  result would not be authentic.

### 7.2 Vault pin

The front runs `project-vault pin /var/lib/wlscratch/runs/<G>` and `project-vault status` as `sicarii`. These are
prescribed preparation records, done by the front as v5 did them. `sicarii` can read `G` through the default ACLs.
Whether project-vault backs up a path outside home correctly is an open verification item. It is tested on a
sacrificial generation in §8.4.

## 8. Setup (NOT approved): order, prestate, exact commands, verification

### 8.0 Order

1. Actual gpt-6.1-sol review of this v2 design.
2. Frame v6-W1 implemented, frozen, and reviewed as code. That includes the front, writer and launcher; the §4.5 final
   pass; and the §10 failure handling.
3. The concrete setup inventory (§8.1–§8.3), with the prestate outputs filled in, reviewed by actual gpt-6.1-sol.
4. Gate 0 established on a fresh reading.
5. The operator approves the concrete setup.
6. The operator runs, or explicitly authorizes, §8.2–§8.3.
7. The lead runs the §8.4 verification.
8. The installed-identity and baseline observations are reviewed, and the frame is adopted.
9. Only then is there any dispatch, under fresh admission.

No step authorizes the next by inference.

### 8.1 Prestate capture

Read-only. Each command reads a single object's metadata or a configuration entry. There is no home listing.

| Check | Command (lead unless marked) | Required prestate |
|---|---|---|
| Accounts absent | `getent passwd wlscratch wlscratch-run` | No output (exit 2) |
| Groups absent | `getent group wlscratch wlscratch-run` | No output (exit 2) |
| Paths absent | `test ! -e` on `/var/lib/wlscratch`, `/var/lib/wlscratch-run`, `/opt/wlscratch`, `/etc/sudoers.d/wlscratch-frame`, `/etc/sudoers.d/wlscratch-run` | Each absent |
| Home ACL prestate | `getfacl -p /home/sicarii` (one inode; output hashed and retained) | Recorded |
| Kernel settings | read `/proc/sys/fs/protected_{hardlinks,symlinks,regular}` and `/proc/sys/kernel/yama/ptrace_scope` | Observed at 23:10Z as 1, 1, 1, 1 |
| Delegation | read `cgroup.controllers` of `sicarii`'s `user@.service` | Observed `cpu memory pids` |
| PAM | read `/etc/pam.d/sudo` | Observed `session optional pam_systemd.so class=none` |
| Sudoers prestate (operator) | `sudo ls -la /etc/sudoers.d` and `sudo sha256sum /etc/sudoers /etc/sudoers.d/*` | Recorded |
| Interpreter | `sha256sum /usr/bin/python3.14`; `python3 -c 'import sys;print(sys.version)'` | Observed `c6bc1ef4…`, 3.14.7 |
| Tools | `sudo --version`; `systemctl --version` | Observed 1.9.17p2; 261 |

### 8.2 Accounts and directories (operator)

```
sudo useradd --system --user-group --no-create-home --home-dir /var/lib/wlscratch --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame writer' wlscratch
sudo useradd --system --user-group --no-create-home --home-dir /var/lib/wlscratch-run --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame target' wlscratch-run
sudo install -d -o root -g wlscratch -m 0750 /var/lib/wlscratch
sudo install -d -o wlscratch -g wlscratch -m 0700 /var/lib/wlscratch/lease
sudo install -d -o wlscratch -g wlscratch -m 0750 /var/lib/wlscratch/runs
sudo install -d -o wlscratch-run -g wlscratch-run -m 0700 /var/lib/wlscratch-run
sudo setfacl -m u:sicarii:r-x,u:wlscratch-run:--x /var/lib/wlscratch
sudo setfacl -m u:sicarii:r-x,u:wlscratch-run:--x /var/lib/wlscratch/runs
sudo setfacl -d -m u:sicarii:r-x,u:wlscratch-run:--x /var/lib/wlscratch/runs
sudo loginctl enable-linger wlscratch-run
```

Option A only:

```
sudo setfacl -m u:wlscratch-run:--x /home/sicarii
```

### 8.3 Installation and sudo rules (operator)

**Frame members.** The frame is installed member by member from the frozen reviewed inventory. There is no `cp -a`
and no recursive chmod. For each member `m` with digest `d`, the operator runs:

```
sudo install -d -o root -g root -m 0755 /opt/wlscratch /opt/wlscratch/frame-v6w1
sudo install -o root -g root -m 0644 <frozen-dir>/m /opt/wlscratch/frame-v6w1/m
```

The concrete member list (`scratch.py`, `launch_target.py`, and any module) and digests come from the reviewed v6-W1
inventory in step 3. `<frozen-dir>` is that inventory's frozen path. This command list becomes exact only when the
inventory exists. Until then it is a template, and it is labelled as one.

**Sudo rules.** Each is validated before it is moved into place:

```
printf '%s\n' 'sicarii ALL=(wlscratch) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/scratch.py *' > /tmp/wlscratch-frame.sudoers
printf '%s\n' 'wlscratch ALL=(wlscratch-run) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/launch_target.py *' > /tmp/wlscratch-run.sudoers
sudo visudo -cf /tmp/wlscratch-frame.sudoers && sudo visudo -cf /tmp/wlscratch-run.sudoers
sudo install -o root -g root -m 0440 /tmp/wlscratch-frame.sudoers /etc/sudoers.d/wlscratch-frame
sudo install -o root -g root -m 0440 /tmp/wlscratch-run.sudoers /etc/sudoers.d/wlscratch-run
sudo visudo -c
```

Option B adds one further rule for the root launcher. That rule's exact text comes with the Option B launcher review.

### 8.4 Verification (lead; unprivileged; outputs retained raw)

**Structural checks:**
- `getent passwd` and `getent group` for both accounts. Expected: the nologin shells and the two private groups.
- `stat -c '%A %U:%G %n'` on every directory from §8.2, plus `getfacl -p` on each.
- `findmnt -n -o SOURCE,FSTYPE,OPTIONS -T /var/lib/wlscratch/runs`.

**Installed identity:**
- A full listing of `/opt/wlscratch/frame-v6w1` with type, mode, owner, size and sha256 for every entry.
- Required: exactly the inventory's members. No extra member, no symlink, no hard link (`nlink == 1`), and modes
  `0644` for files and `0755` for directories.
- The interpreter's identity and its imported stdlib module closure, with each module file's digest. They are
  recorded and compared with the reviewed baseline.

**Sudo:**
- The operator records `sudo sha256sum /etc/sudoers.d/wlscratch-frame /etc/sudoers.d/wlscratch-run` and the
  `sudo visudo -c` output. The lead compares those hashes with the digests of the reviewed rule text, and with the §8.1
  prestate of the rest of `/etc/sudoers.d`, which must be unchanged.
- `sudo -n -l` as `sicarii` is recorded too. It lists all of `sicarii`'s rules, so on its own it does not show that the
  new rule is the only change.
- A `scratch.py selftest` run must show uid and gid = `wlscratch`, the clean environment, `PR_SET_DUMPABLE=0`, and the
  lease lock taken and released.
- A `launch_target.py selftest` run through the writer must show uid = `wlscratch-run`. It must also show the user
  manager reachable at `/run/user/<uid>`, with the controllers delegated.

**Sacrificial denial probes.** These never touch real runs.
1. The writer's `selftest` verb creates `runs/selftest-<hex>/probe-file` (0640) and `runs/selftest-<hex>/probe-dir`.
2. As `sicarii`, the lead attempts each operation with Python `os` calls: `open(O_WRONLY)`, `rename`, `unlink`,
   `chmod`, `link`, `symlink`-into, and `mkdir`-into. For every attempt it records the exact errno, which must be
   `EACCES` or `EPERM`, never another error. A probe that succeeds is a setup failure, and it is retained.
3. The launcher's `selftest`, as `wlscratch-run`, attempts the same operations against the writer-owned sacrificial
   entries. The same rule applies.
4. The sacrificial directory is kept as evidence.

**Vault:** `project-vault pin`, `status` and `check` on the sacrificial generation, run as `sicarii`.

**Runtime effects:** `loginctl list-sessions` and `loginctl show-user wlscratch-run` before and after a selftest, to
record any session or manager effects.

## 9. Resource budget

### 9.1 Disk

Gate 0 applies unchanged (runbook v4.2):
- Required = 2·(A_mat + A_obj + A_rec) + A_ambient = 9304350902252/1397 bytes above the unchanged 10000000000 reserve
  (JACKAL exact, formal=false).
- Each allowance is a labelled judgment, never lowered because a run used less.

W-1 adds the following, and none of it is yet measured:
- the installed frame (bytes once the inventory exists);
- two account homes;
- `wlscratch-run`'s user-manager state, which lives on tmpfs `/run/user/<uid>`, so it is RAM rather than disk;
- user-manager journal growth, which is part of the ambient allowance;
- the sacrificial selftest generation.

Gate 0 must add each of these as a labelled allowance before dispatch. Nothing here establishes safe capacity. The
margin at 22:06:53Z was negative: free − reserve − Required = −8582736788460/1397 bytes (JACKAL exact).

### 9.2 Optional enforced images (only if S-1 option 3 is chosen)

- **Payload allowances, not image sizes.** `2259217862` bytes for work (A_mat + A_obj) and `545393048` for records
  (A_rec) are payload allowances (JACKAL exact), not image minima.
- **Filesystem overhead.** An image must add ext4 metadata, journal, inode tables, reserved and geometry overhead, and
  setup effects. That overhead is to be measured on a sacrificial image, since nothing here measures it.
- **The zero difference.** The payload-plus-restore-plus-ambient equation that gives zero is an ideal payload
  identity. It is not physical allocation equality and not safe capacity.
- **Image mode.** `fallocate` creates files under the umask, so each image needs an explicit
  `sudo chmod 0600 <image>` and `sudo chown root:root <image>`, verified afterwards.
- **`noexec`.** It is compatible with the scratch proof runs, because gnatprove, gprbuild and the provers execute from
  the toolchain path, not from the tree. It is incompatible with any control that executes built artifacts in the
  tree. Such controls are not part of the scratch frame, but if one is ever run the mount must not be `noexec`, and no
  accepted case may be narrowed to suit a mount.
- **What images do.** They enforce bounded writes only. ENOSPC is a retained failure, never an accepted refusal and
  never evidence of sufficient capacity.
- **Records image.** It can fill too (§10).
- **Credit.** Images earn no capacity or admission credit without a reviewed argument that preserves the target.

### 9.3 Memory, CPU and other limits

Unchanged from v5:
- MemoryMax=8G, MemorySwapMax=0, core 0/0, `-j2`;
- the 16777217 kB MemAvailable gate;
- the receipt protocol.

## 10. Failure, custody and lifetime

Every record is create-only: `O_EXCL`, then fsync of the file and its directory.
- A record that exists is committed.
- A retry goes to `name.retry-<12hex>`, with v5's never-raising `retain` semantics.
- The last resort is the writer's stderr. That is a pipe to the front, whose output becomes the lead's tool output in
  the session transcript. This is the identified durable channel, and it is not a frame write outside the tree.

**Launch acknowledgement:**
1. The writer writes `launch-intent.json`, binding the generation, before it starts the launcher.
2. The launcher's stdout report (unit, cgroup path, pids) is recorded as `launch-ack.json`.
3. The waits are genuine:
   - the writer `waitpid`s sudo, which is the outer wait;
   - the launcher waits on `systemd-run`;
   - the scope's state is read from cgroupfs.

| Event | Behavior |
|---|---|
| Lease held by another writer | Refuse before any mutation. stderr only. The front releases nothing, because it has not yet reserved: reservation comes after lease and admission (§5.4). |
| sudo refused, account locked or rule missing, at invoke time | The front observes sudo's exit before reserving the window. A preflight `selftest` success does not stand in for this check; each invoke is checked. |
| Writer dies before `launch-intent.json` | No launch is possible. That record is written before the launcher starts. The front observes the writer exit, confirms no `wlscratch-run` scope for `G`, then releases the window. |
| Writer dies after `launch-intent.json` | Unknown. The front reads cgroupfs for `wlscratch-run`'s user slice and `pgrep -u wlscratch-run`. Any live, unreadable or reused identity keeps the window reserved and is reported as a hold for explicit operator-visible resolution. There is no late collector, as in v5. |
| Front dies after reserving | The window stays reserved, as in v5. The writer sees stdin EOF. Before launch it refuses and concludes non-success. After launch it keeps waiting and concludes. A front EOF never implies a refusal after launch. |
| Target exits | The writer observes outputs, runs the post-run walk, and writes conclusion records. The window is released only by the front, after an authenticated conclusion message and its own cgroupfs check. |
| Records ENOSPC (records image full, or the filesystem full) | `retain`'s retry names, then stderr to the front. The outcome is non-success. The window is released only on an observed terminal state. |
| `wlscratch-run` user manager unavailable | The launcher refuses before `systemd-run`, and the writer records it. |
| Reboot | All processes are gone, and the outcome of an interrupted run is unknown, so it is non-success. The window stays reserved until explicit resolution. With images: mounts come back only through operator-written mount units. At admission the writer verifies the mount source, filesystem UUID and label, and `st_dev`, and refuses if `runs` is not the expected mount. That also refuses writing into the bare mountpoint directory. There is no implicit new genesis, and stale evidence earns no credit. |
| A `sicarii` process or the target tries to write, rename, chmod or link into frame-owned paths | Kernel `EACCES`/`EPERM`. Prevention, not detection, verified by the §8.4 probes. |

The v6 plan's N11–N14 terminal and participant guarantees, and v5's terminal semantics, are preserved unchanged.

## 11. Rollback (operator)

Rollback withdraws access and removes configuration after preserving it. It does not delete evidence, and it does
not restore a pristine pre-setup system: the UIDs, groups and files remain. Order:

1. **Revoke new launches first.** Copy `/etc/sudoers.d/wlscratch-frame` (bytes and sha256) into the setup evidence
   record, then remove it, then run `sudo visudo -c`.
2. **Preserve terminal custody.** Observe with `pgrep -u wlscratch`, `pgrep -u wlscratch-run` and cgroupfs.
   - Do not kill live participants.
   - Resolve any reserved window explicitly.
3. **Remove the second rule.** Preserve and remove `/etc/sudoers.d/wlscratch-run` (and Option B's rule), then run
   `visudo -c`.
4. **Disable linger.** `sudo loginctl disable-linger wlscratch-run`, only after no scope remains.
5. **Remove the home ACL (Option A).** Capture `getfacl -p /home/sicarii` before, run
   `sudo setfacl -x u:wlscratch-run /home/sicarii`, capture after. Compare with the §8.1 prestate.
6. **Images, if used.** Unmount. Preserve copies of the mount units, then disable and remove them. Keep the image
   files and record their sha256.
7. **Lock both accounts:** `sudo usermod -L -e 1 wlscratch` and the same for `wlscratch-run`. Do not delete them, so
   file ownership in the evidence keeps its meaning.
8. **Keep as evidence:** `/var/lib/wlscratch`, `/var/lib/wlscratch-run` and `/opt/wlscratch`.

**What rollback leaves behind:**
- two locked accounts and two groups;
- their files and ACL entries on `/var/lib/wlscratch*`;
- the retained images, if any;
- `sicarii`'s read access to the evidence through the ACLs on `/var/lib/wlscratch`.

## 12. Retained evidence

**Raw records:**
- pre- and post-setup captures (§8.1, §8.4);
- `passwd` and `group` entries;
- `getfacl` output;
- sudoers file bytes with hashes;
- `findmnt` output, kernel settings and linger state;
- complete installed-inventory comparisons;
- the interpreter and module closure;
- selftest and probe records with their errnos;
- every writer record, with the message chain;
- the launch intent and acknowledgement, the waits, and the conclusion;
- the front's console output as preserved in the lead transcript;
- the rollback transcript.

**What these records are.** Copies kept in the lead-owned `wt-1/proposal/setup-record/` are evidence records, not
immutable or authentic producer custody. Hashes of writer-owned files describe files that can still change, unless
the files are frozen by a reviewed mechanism. Durable retention goes through project-vault once the backup works.

## 13. Non-claims and open items

**Non-claims:**
- No sufficiency is claimed. V5-B01, V5-B02 and every original obligation stay OPEN until exact successor evidence
  meets the original required changes.
- The account design gives a kernel-enforced writer boundary. It is no proof of the frame's code, no proof of lead
  authentication (§2), and no confinement of the target outside the tree.

**Open items:**
- The v6-W1 code: the front, writer, launcher, the excluded-leaf final pass, the channel and the failure handling.
- New reviewed environment baselines for `wlscratch` and `wlscratch-run`.
- Option A versus Option B for the toolchain path, with the Option A exposure enumeration.
- Whether project-vault handles `/var/lib` paths.
- The added Gate 0 allowances.
- Storage (S-1) must be resolved first.

## 14. Traceability to the package review (W-1 findings)

| Finding | Where v2 answers it |
|---|---|
| W1-CUSTODY | §3 (target account), §4.1–§4.4 (lease, chain, enforcement argument) |
| W1-FINAL-PASS | §4.5 (excluded leaves required; draft gap stated) |
| W1-CLOSURE | §8.3–§8.4 (member-exact install, no links, modes, interpreter and module closure); §2 (exec-by-path ceiling kept) |
| W1-CHANNEL | §5 (framing, chain, bindings, dumpable, argv grammar); §2 (authentication residual) |
| W1-WRITE-AUTHORITY | §3, §4.3–§4.6 (enforced writer set; target-only residual separated; front writes only window and vault pin) |
| W1-READ-ACCESS | §6.1 (streamed inputs; 0600 files untouched) |
| W1-READ-EXPOSURE | §6.1 (no writer home ACL); §6.2 (Option A exposure enumeration, or Option B narrow sandbox) |
| W1-PREFLIGHT-IDENTITY | §7 (front-side `storage_status.py` and vault pin; never as `wlscratch`) |
| W1-SETUP-PRESTATE | §8.1 |
| W1-SETUP-ORDER | §8.0 |
| W1-SETUP-EXACTNESS | §3 and §8.2 (two users and two groups; linger observed only for `worldline` and `wlrehearsal` in v1, and now proposed only for `wlscratch-run`); §8.3 (template labelled) |
| W1-IMAGE-GEOMETRY | §9.2 |
| W1-IMAGE-COMPATIBILITY | §9.2 (`noexec`, explicit 0600, ENOSPC) |
| W1-VERIFICATION-PROBES | §8.4 (sacrificial probes, errno, the limit of `sudo -n -l`) |
| W1-FAILURE-LEASE | §10 (intent and ack, genuine waits, unknown and hold) |
| W1-FAILURE-RECORDS | §10 (records ENOSPC, stderr channel, commit semantics) |
| W1-REBOOT-RECOVERY | §10 (reboot row) |
| W1-ROLLBACK | §11 |
| W1-EVIDENCE | §12 |
| W1-NONCLAIMS | §13 |
