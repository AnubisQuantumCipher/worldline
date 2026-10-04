# Isolation and storage proposal W-1: protected writer account for the scratch run tree

**Status.** Lead preparation, 2026-10-04 ~19:35Z. This is a CANDIDATE. It is not an established sufficient design and
it is not approved.
- No operator choice, privileged action, sudo use, account creation, mount or installation is approved or performed.
- Proof dispatch stays blocked by the confinement gate (V5-B01, V5-B02) and the capacity gate (runbook Gate 0 v4.1).
- This document goes to actual gpt-6.1-sol review inside the consolidated operator package. The human then decides.

## 1. Criteria this must meet (exact, unchanged)

From the sealed actual gpt-6.1-sol review of frame v5: UNQUALIFIED_SCRATCH_FRAME, inventory `c45720ef…5aa45`,
freeze verified.

**V5-B01 required change:**

> "Retain file observation identities through the complete walk and revalidate every encountered leaf, including
> excluded generated leaves, using complete descriptor metadata and named-entry joins at the final admission
> boundary. Bind the accepted source/output generation to the spawn under custody that prevents the admitted
> generation from changing before use. Directory-only revalidation or after-run detection must not substitute for
> pre-launch alias refusal. Preserve the exact base recipe, output partitions, allowlist, caps and original gates."

**V5-B02 required change:**

> "Provide enforced location custody across each frame-owned mutation and the final admission-to-spawn handoff,
> rather than observer-only checks before and after it. Use an independently protected writer/location boundary or
> an equivalent enforced lease that concurrent same-user rename/substitution cannot invalidate while writes or launch
> are possible. Keep original outside-tree authority limited to the documented window protocol and prescribed
> preparation records. Do not relabel frame-owned outside-tree writes as the running-target residual or lower the
> original guarantee; retain this blocker if custody cannot yet be established."

**Storage, WORLDLINE monitor 2026-10-04:**

> "live preflight that budgets measured run growth AND temporary full-restore space above the unchanged reserve";
> "include materialization, all retained outputs/records, temporary full-restore needs and ongoing agent/review growth
> above the unchanged reserve. Do not shrink the next allowance merely because the last run used less. If safe
> capacity cannot be established, keep dispatch deferred."

Also: "periodic storage sampling plus a factor on the maximum observed write rate does not establish a maximum
future write rate or stop latency".

## 2. Why the candidate is a separate account

**Threat.** The actors that defeat v5 are concurrent processes of the same user (`sicarii`), meaning other agents.
They can rename, substitute, detach or modify anything that user owns, between any frame check and the frame's next
mutation or the target's next read.

**Routes examined** (`frame-v6-PLAN.md`; observed host facts: `fuse2fs` absent, unprivileged user namespaces
enabled, `/dev/fuse` 0666):

| Route | Why it fails |
|---|---|
| User FUSE mount | The same user can lazily unmount it. |
| tmpfs in a private user namespace | Not persistent, and copying out reintroduces the window. |
| Private-namespace FUSE image | Needs an install, and the image file stays writable by the same user, so it gives detection only. |
| Root-made filesystem with a `sicarii`-owned run root | Prevents relocation out of the tree (EXDEV, root-owned mount root), but NOT modification by `sicarii` processes. V5-B01's "custody that prevents the admitted generation from changing before use" fails. |

**What remains.** Only a writer boundary that `sicarii` processes cannot write at all addresses both criteria: a run
tree owned by a different account, with no write permission for `sicarii` anywhere in it or on its ancestors. The
host already uses this pattern:

| Account | Shell | Home |
|---|---|---|
| `worldline` (1004) | `/usr/bin/nologin` | `/var/lib/worldline`, 0700 |
| `wldrill` (1003) | `/usr/bin/nologin` | `/var/lib/wldrill`, 0700 |
| `wlrehearsal` (1002) | `/usr/bin/nologin` | `/var/lib/wlrehearsal`, 0700 |

Each has a `<account>-clients` group containing `sicarii`. Linger is on for `worldline` and `wlrehearsal`.

## 3. Architecture W-1

### Front (`sicarii`, the lead's process)

The front:
- runs the existing shared-window protocol: reserve and release, the one documented outside-tree authority;
- forwards the lead's JACKAL challenge answers to the writer. It reads lead-written answer files from a lead inbox;
  creating those files is the lead's own action, not a frame mutation;
- invokes the writer only through one sudoers-permitted command;
- observes the writer's actual exit;
- observes scope/cgroup terminal state through world-readable `/proc` and `/sys/fs/cgroup`;
- releases the window only on an observed terminal state with no unresolved participant.

The front creates, writes and chmods **no file** except the window. Every record it would previously have written is
sent to the writer and written there.

### Writer (`wlscratch`, the installed reviewed frame code)

The writer:
- owns `/var/lib/wlscratch/runs`;
- materializes from the reviewed base and overlays it reads, hash-verified against pinned inventories;
- performs every admission;
- writes every create-only record;
- starts the scope with `systemd-run --user` under the `wlscratch` user manager;
- spawns the target `gnatprove`/`gprbuild` as `wlscratch` from the held source descriptor;
- waits;
- concludes.

No `sicarii` process can create, rename, chmod or write anything in the tree. So the admitted generation cannot be
changed by them before use (V5-B01), and frame mutations cannot be relocated by them (V5-B02).

### Target

The target runs as `wlscratch` and writes only into the tree. Tool binaries stay where they are and are executed by
path. That is the residual "target_exec_by_path", ruled ACCEPTABLE_AS_DOCUMENTED, with tool closures re-observed after
the run.

### Inputs read by the writer

All reads go through a traverse-only ACL on `/home/sicarii`; everything below it is already 0755/0644 (observed):
- the reviewed base composition;
- overlays;
- the lead module;
- the lead transcript, for the fresh lead observation;
- the START file;
- the frame review/adoption records;
- the Codex review rollouts;
- the window file (read for the ownership check);
- the GNAT toolchain;
- `storage_status.py`;
- the JACKAL receipts.

### Frame changes this requires

A successor frame v6-W1, which must be frozen and pass actual gpt-6.1-sol review:
- the front/writer split and its channel: stdin/stdout pipes through sudo, with authenticated framing;
- all records written by the writer;
- a writer read-only `export` verb for the lead's evidence reads;
- V5-B01's final-pass leaf revalidation (drafted in the v6 working copy);
- the mode policy for group readability (0640/0750, group `wlscratch-clients`);
- the author items H-S1..H-M7 and N11..N14 from `frame-v6-PLAN.md`;
- **new reviewed baselines for the `wlscratch` environment.** HOME, USER and `XDG_RUNTIME_DIR` differ, so the tool,
  runtime and manager identities change. That is a new identity input, reviewed and never assumed equal.

## 4. Exact authority boundary

| Actor | May | May not |
|---|---|---|
| Human operator | Approve or reject W-1. Run, or explicitly authorize, each privileged command in §5 and §8. Choose whether to use the optional images (§5.6) and their sizes. Choose rollback. | — |
| Lead (`sicarii`, this Claude session) | Prepare designs and frame code. Run the unprivileged verification in §5.7. Run the front. Invoke only the sudoers-permitted writer command, and only after frame v6-W1 is QUALIFIED, adopted and Gate 0 is established. Read evidence. | Run any other privileged command. Edit the installed frame. Write in the protected tree. Widen any ACL, sudo rule or permission. Treat setup as approval of anything else. |
| Writer account `wlscratch` | Run the installed reviewed frame and the target. Read the enumerated inputs. Write only under `/var/lib/wlscratch/runs` (and the records image, if used). | Hold a login shell or password login. Write `sicarii` files. Run other software through sudo. |
| Other `sicarii` processes | Read the tree (group `wlscratch-clients`). | Create, write, rename, chmod or delete anything in the tree or its ancestors. |
| Actual gpt-6.1-sol reviewer | Assess designs, frame code and setup evidence. | Grant operator authority or weaken a criterion. |

## 5. Required setup (NOT approved; exact commands for the operator)

### 5.0 Preconditions, checked by the lead before asking

- Frame v6-W1 is frozen and QUALIFIED by actual gpt-6.1-sol. Its installed bytes equal the reviewed inventory.
- Gate 0 is established (§6).
- The operator has approved this package.

### 5.1 Account and groups (mirrors the existing dedicated accounts)

```
sudo useradd --system --user-group --home-dir /var/lib/wlscratch --create-home \
     --shell /usr/bin/nologin --comment "WORLDLINE scratch protected writer (dedicated account)" wlscratch
sudo groupadd --system wlscratch-clients
sudo gpasswd -a sicarii wlscratch-clients            # read access; effective in NEW login sessions only
sudo gpasswd -a wlscratch wlscratch-clients          # lets the writer set group ownership
sudo chown wlscratch:wlscratch-clients /var/lib/wlscratch && sudo chmod 0750 /var/lib/wlscratch
sudo install -d -o wlscratch -g wlscratch-clients -m 0750 /var/lib/wlscratch/runs
```

### 5.2 User manager for `systemd-run --user` scopes

```
sudo loginctl enable-linger wlscratch
```

### 5.3 Traverse-only access into the lead's home

```
sudo setfacl -m u:wlscratch:--x /home/sicarii
```

**Exposure, stated plainly.** With traverse, `wlscratch` can open any path under `/home/sicarii` whose components are
already world-traversable and readable (observed: `~/opt`, `~/Documents`, `~/.claude`, `~/.codex` are 0755). That
includes the lead transcripts under `~/.claude/projects`.
- The account runs only the installed reviewed frame under the sudo rule.
- A narrower alternative is a per-path ACL on each enumerated input chain. It is more commands and more maintenance.

### 5.4 Installed frame (root-owned, immutable to `sicarii`)

```
sudo install -d -o root -g root -m 0755 /opt/wlscratch/frame-v6w1
sudo cp -a <reviewed frozen frame-v6w1 members> /opt/wlscratch/frame-v6w1/
sudo chown -R root:root /opt/wlscratch/frame-v6w1 && sudo chmod -R u=rwX,go=rX /opt/wlscratch/frame-v6w1
```

The lead then verifies that every installed member's sha256 equals the reviewed frame inventory (§5.7).

### 5.5 Sudo rule (validated)

```
printf '%s\n' 'sicarii ALL=(wlscratch) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/scratch.py *' \
  | sudo tee /etc/sudoers.d/wlscratch-frame >/dev/null
sudo chmod 0440 /etc/sudoers.d/wlscratch-frame && sudo visudo -c
```

The frame refuses unknown verbs, and sudo's `env_reset` stays in force. The rule names an interpreter and a
root-owned script only.

### 5.6 Optional enforced-capacity images

Only if S-1 option 3 is chosen. The sizes are operator choices; the minimums below come from the current
allowances:

```
sudo install -d -o root -g root -m 0700 /var/lib/wlscratch-images
sudo fallocate -l <N_work> /var/lib/wlscratch-images/work.img
sudo mkfs.ext4 -q -m 0 -L wlscratch-work /var/lib/wlscratch-images/work.img
sudo fallocate -l <N_records> /var/lib/wlscratch-images/records.img
sudo mkfs.ext4 -q -m 0 -L wlscratch-records /var/lib/wlscratch-images/records.img
sudo mount -o loop,nodev,nosuid,noexec /var/lib/wlscratch-images/work.img /var/lib/wlscratch/runs
sudo install -d -o wlscratch -g wlscratch-clients -m 0750 /var/lib/wlscratch/records
sudo mount -o loop,nodev,nosuid,noexec /var/lib/wlscratch-images/records.img /var/lib/wlscratch/records
sudo chown wlscratch:wlscratch-clients /var/lib/wlscratch/runs /var/lib/wlscratch/records
sudo chmod 0750 /var/lib/wlscratch/runs /var/lib/wlscratch/records
# persistence across reboot: systemd .mount units (operator-written), never assumed
```

The image files are root-owned 0600 in a root-owned 0700 directory, so no `sicarii` or `wlscratch` process can write
them directly. A full work image makes the target fail with ENOSPC, which is a retained engineering failure. The
separate records image keeps records writable when the work image is full.

### 5.7 Unprivileged verification (lead), outputs retained

```
getent passwd wlscratch; getent group wlscratch wlscratch-clients
stat -c '%A %U:%G %n' /var/lib/wlscratch /var/lib/wlscratch/runs [/var/lib/wlscratch/records]
getfacl -p /home/sicarii
loginctl show-user wlscratch -p Linger
sudo -n -l                                              # lists only the lead's own rule
sha256sum /opt/wlscratch/frame-v6w1/* (compared with the frozen inventory)
findmnt -n -o SOURCE,FSTYPE,OPTIONS /var/lib/wlscratch/runs [/var/lib/wlscratch/records]
```

A negative probe follows, run by the lead as `sicarii`. Each command must fail with EACCES:

```
touch /var/lib/wlscratch/runs/x
mv /var/lib/wlscratch/runs /tmp/y
```

## 6. Resource budget

**Disk.** Gate 0 v4.1 applies unchanged.
- One unit run requires 9304350902252/1397 bytes above the 10000000000-byte reserve (JACKAL exact, formal=false).
- At 18:49Z the margin was −7648075570156/1397 (JACKAL exact). **W-1 cannot be executed now.** Capacity must first be
  established through S-1 options 1 or 2.
- With the optional images, the minimum sizes are:
  - N_work ≥ A_mat + A_obj = 2259217862 bytes;
  - N_records ≥ A_rec = 545393048 bytes;

  both JACKAL exact, formal=false. The full-preallocation requirement, plus restore and ambient allowances, equals
  the Gate 0 requirement exactly. JACKAL exact gives a difference of 0. So images add enforcement, not capacity.
- An admission argument that credits the images as an enforced output limit must itself be reviewed before Gate 0
  changes. **Until then Gate 0 v4.1 stays in force exactly.**

**Memory, CPU and limits.** Unchanged:
- MemoryMax=8G, MemorySwapMax=0, core 0/0, `-j2`;
- the 16777217 kB MemAvailable gate;
- the receipt protocol.

**Accounts.** One system user and one system group are added. No network, ports or services beyond the user
manager.

## 7. Failure and custody behavior

| Event | Behavior |
|---|---|
| `sudo` refused, account locked or rule missing | The front refuses before reserving the window. Nothing is started. Recorded on the lead console and in the front's retained stdout. |
| Writer crashes before the spawn | The front observes the writer's exit and the scope/cgroup absent, then releases the window. Writer records written so far stay in the tree. |
| Writer crashes after the spawn | The front releases only after cgroupfs/`/proc` show no live participant. Otherwise the window stays reserved for explicit operator resolution. |
| Front (lead) dies after reserving | The window stays reserved, as today: manual operator-visible resolution. The writer sees stdin close, refuses the challenge and concludes non-success. |
| `wlscratch` user manager unavailable | The writer refuses at the scope start. Recorded. |
| Work image full (optional images) | The target fails with ENOSPC, a retained non-success. Records are on the separate records image. |
| Records image full | Records retry, then go to the writer's stderr, which the front captures. Non-success. The window is released only on observed terminal state. |
| Reboot | Mounts must come back through operator-written units. The writer verifies mount source, fs label and UUID at admission and refuses otherwise. |
| `sicarii` process tries to write, rename or chmod the tree | Kernel EACCES. This is prevention, not detection. |
| Inputs changed in `~` after admission | The base and overlay are copied and hash-verified into the tree at materialization, so later edits don't affect admitted copies. Tools follow the ruled residual (identity before, closure after). |
| Root actions | Out of scope. Root can do anything, and that is not part of the threat model. |

## 8. Rollback (operator; nothing is deleted)

1. Confirm the window is released and `ps -u wlscratch` is empty, with no live scope (cgroupfs).
2. Remove the sudo rule, then validate:

   ```
   sudo rm /etc/sudoers.d/wlscratch-frame && sudo visudo -c
   ```
3. Disable linger:

   ```
   sudo loginctl disable-linger wlscratch
   ```
4. Remove the traverse ACL:

   ```
   sudo setfacl -x u:wlscratch /home/sicarii
   ```
5. Images, if used: unmount both, and remove their mount units or fstab lines.

   ```
   sudo umount /var/lib/wlscratch/runs /var/lib/wlscratch/records
   ```

   **Keep the image files**, then record their sha256 (`sudo sha256sum /var/lib/wlscratch-images/*.img`).
6. Lock the account instead of deleting it. This keeps the uid-to-file ownership of the evidence meaningful:

   ```
   sudo usermod -L -e 1 wlscratch
   ```
7. Keep `/var/lib/wlscratch` and `/opt/wlscratch/frame-v6w1` as evidence. Later offload goes only through
   project-vault's verified path, once backup works.

## 9. Retained evidence

- The setup transcript: each privileged command with its exit status and output, captured by whoever runs it.
- The §5.7 verification outputs, including the negative probes.
- The installed-frame hash comparison.
- Every run tree and records tree.
- Image sha256 values after unmount.
- The rollback transcript.
- All of the above recorded under `wt-1/proposal/setup-record/` by copy, never by editing the originals.

## 10. Non-claims and open items

- **No sufficiency is claimed.** Closing V5-B01/V5-B02 requires frame v6-W1 implemented on this boundary, frozen, and
  QUALIFIED by actual gpt-6.1-sol, then the operator's setup and the §5.7 verification.
- **The new `wlscratch` environment baselines** are a new identity input. They need their own reviewed generation.
- **The transcript-based lead observation** read by `wlscratch` widens read exposure (§5.3). The per-path ACL
  alternative narrows it.
- **The project-vault pin of the run tree** by the `sicarii` vault cannot be written by the writer. The pin step and
  its check need a redesign, for example a front-side pin of a path the vault can stat. It stays an open design item.
- **Storage (S-1)** must be resolved first. Images enforce, they don't add capacity.
- **Every original obligation stays OPEN:** fixtures, contracts, thresholds, controls, proofs, native and Phase One.
