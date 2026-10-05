# ROLLBACK.md — exact reversal per install step + rehearsal spec (§15.1, §16.1 O-4)

Operator-only; privileged; **nothing here is executed**. The script bytes are
`assets/scripts/rollback.sh` (a reviewable template; the raw before/after captures and the
M0/M1 manifests are pinned by the concrete inventory + O-4). The rollback is its OWN state
machine, not the inverse of setup: it starts from a complete setup that has RUN (observation =
G_N plus runtime growth) and it RETAINS every tree. Nothing is called restored/removed without
its full-byte equality capture; runtime growth is never "reversed".

## Reversal per step

| Step | Reverses | Action (exact, from §15.1) | Postcondition observed |
|---|---|---|---|
| **M0** | — | capture retained-tree manifest of `/var/lib/wlscratch` (+`/var/lib/wlscratch-images` with images): every entry's path, type, size, sha256 (regular files), owner, group, mode, ACL digest | M0 recorded raw |
| **R1** | the S1 (frame) sudo rule — revoke NEW launches first | `staged_deactivate /etc/sudoers.d/wlscratch-frame`; preserve bytes+sha256 in `rollback-<stamp>/`; `visudo -c`; remove inert after equality | final + inert names absent; preserved copy equal; `visudo -c` passes; no new writer can start |
| **R2** | running/pending participants (wait, do not kill) | no process with uid W (incl. writers started before R1); no `sudo` process naming a frame entry; every RL scope absent or `populated 0` and not live (K,M §9.4); RL root-scan conditions (no uid-N process, no N-owned userns outside RL scopes) | all hold; a live participant is WAITED FOR; killing one is a separate, recorded, explicit operator decision; any UNKNOWN holds here |
| **R3** | the shared window | if reserved by a W-1 attempt and known-terminal ownership uncertain → HOLD; if ownership known-terminal and reserving front gone, operator resolves explicitly and records it; the frame never does | window state recorded |
| **R4** | the RL sudo rule | `staged_deactivate /etc/sudoers.d/wlscratch-rl`; preserve; `visudo -c`; remove after equality | as R1, for the RL rule |
| **R5** | image mount units (images only) | identify every start source first (two mount units, `systemctl list-dependencies --reverse` each, any automount, fstab: none expected); `systemctl disable` both; verify no open file + R2 still holds; stop RECORDS unit first, WORK unit second (unmount); verify each unmounted + each bare mount point == setup identity; preserve unit files, deactivate+remove, `daemon-reload`, verify no remount; KEEP image files, record sha256 | per the action; units removed, images kept |
| **R6** | — | nothing is restored in `/home/sicarii`: W-1 set no ACL there | — |
| **R7** | the W account state | `usermod -L -e 1 wlscratch` (N already locked+expired); KEEP both accounts so evidence ownership keeps meaning | W locked and expired; N unchanged |
| **R8** | the sshd drop-in | `staged_deactivate /etc/ssh/sshd_config.d/30-wlscratch.conf`; preserve; `sshd -t`; `systemctl reload sshd`; remove after equality | drop-in absent; `sshd -T` without S-E's `DenyUsers` line |
| **R9** | — (retain evidence) | KEEP `/var/lib/wlscratch` (generations, records, exports, captures), `/opt/wlscratch`, `/root/wlscratch-staging` (step logs + every rollback capture) and every capture; capture retained-tree manifest M1 | **M1 == M0** (retained trees unchanged by the rollback); any difference STOPS for an explicit operator decision |

**Reachable rollback states** are exactly the products of these per-step states in step order
(each step starts only after the previous step's postcondition holds). A stopped rollback
continues from the first step whose postcondition does not hold; S-R classifies it by the same
rules as setup (§11.4) against this table. A rollback atom is one reversing action of §11.5's
class table run as an atom of the rollback sequence (its intermediates are that class's reversal
intermediates with their co-effects).

## What rollback leaves (§15.2)

Remaining: the two LOCKED and EXPIRED accounts (W, N) and their two user-private groups, with
their numbers and their passwd/group/shadow/gshadow entries; every file under
`/var/lib/wlscratch*`, `/opt/wlscratch`, `/root/wlscratch-staging`; images if any; journal
entries. Removed: both sudoers files, the sshd drop-in, the mount units. **Not restored**: a
pristine pre-setup system (by design — evidence is retained).

## Rehearsal spec (§16.1 O-4, O-5 — what to observe to confirm rollback)

Rehearsed on a SACRIFICIAL copy of the setup (a second sacrificial account pair + tree prepared
by O-1's scripts), never on the live setup:

1. **O-4**: run the rollback script set on the sacrificial copy; retain every step's raw
   before/after capture and the retained-tree manifests M0/M1. Confirm: each step's postcondition
   above holds on re-observation; **M1 == M0** (sacrificial trees unchanged by the rollback);
   both sacrificial sudoers files, the sshd drop-in and (images) the mount units are absent;
   `visudo -c` and `sshd -t` pass; the sacrificial accounts are locked+expired and kept.
2. **O-5**: run S-R against the rehearsal's recorded observations so that EVERY vector of the
   §11.4 reachable set (67 / 104 states, including the `userdel` co-removal states X1-X4 / W_A /
   W_B of W1-V9-ENUM-USERDEL) is produced on the sacrificial copy, continued AND reversed, with
   S-R's reverse rules from W_A and every co-removed state (NO failing `groupdel`). Confirm: S-R
   classifies each produced observation as exactly one reachable-set vector (never *other* for a
   partial install/deactivation/reversal), and never issues a known-failing `groupdel`.

IMPLEMENTATION STATUS: the rollback machine and S-R are MISSING as frozen code (GAP.md M28, M30);
`assets/scripts/rollback.sh` is a reviewable template, not the pinned artifact.
