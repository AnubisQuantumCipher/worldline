# Prestate inventory and run-path-skeleton spec (DEFENSIVE confinement config)

SOURCE-ONLY. Nothing here is executed. This records (A) the prestate obligations the setup
reads before it changes anything, and (B) the step-11 run-path presentation ("skeleton"),
which is part of the sandbox view construction, described defensively — it hides host
content behind the generation's own bind, it does not attack anything.

## A. Prestate inventory (v11 Section 11.3, P1-P30)

Read-only; "lead" = unprivileged `sicarii`, "operator" = needs root. Every `undetermined`
result of an unprivileged run is repeated by the operator; an `undetermined` result as root
refuses. Highlights that gate installation:

- P1/P2: the two names and both candidate numbers absent from passwd/group (`getent` exits 2).
- P3: /etc/subuid, /etc/subgid digests + lstat; every candidate outside every range.
- P4 (operator): `find <fs> -xdev \( -uid n -o -gid n \)` empty for `/` and each local
  non-FUSE filesystem (NEVER ~/iPad, ~/iPadBackup).
- P5: `absent.py` on /var/lib/wlscratch, /var/lib/wlscratch-ns, /opt/wlscratch, the sshd
  drop-in path, the two mail-spool paths (and, with images, /var/lib/wlscratch-images and
  the mount-unit paths).
- P6 (operator): /etc/sudoers.d has none of wlscratch-frame, wlscratch-rl, .wlscratch-frame.new,
  .wlscratch-rl.new (a complete listing of the root-only directory; no symlink followed).
- P7/P12/P13: root-owned ancestors with no extended ACL; the EXTENDED P-NOOWNER route
  inventory (W1-V9-NOOWNER-SCOPE) over EVERY principal — no sudoers rule of any user/group
  whose Runas set resolves to W or N through ALL/%group/#uid/alias/negation (none lists N, none
  lists W except the S1 rule), and no polkit authority granting any subject a passwordless
  unit-management or exec-as-user path to W or N.
- P8/P25: kernel sysctls and build config (protected_* = 1, ptrace_scope = 1, the LSM list
  capability,yama,landlock, CONFIG_SECCOMP_FILTER, CONFIG_AIO, CONFIG_IO_URING, CONFIG_COMPAT),
  and the FOUR system-call numbers used by the step-13b seccomp filter, read from the installed
  build's generated unistd_64.h / unistd_32.h.
- P14: cron/at absent. P15: linger listing (no new linger created). P17: setuid/setgid and
  file-capability baseline for S-I. P18/P19: python3 and tool versions. P20/P27/P28: cgroup2
  controllers, limits and ownership (memory + pids controllers; user-1000.slice cgroup.procs
  root-owned). P30: the lead's process attributes as F records them, each reproducible by RL.

## B. The run-path presentation / skeleton (v11 Section 12.2 step 11)

For each of the two bind pairs
  (`<RUNS>/<label>/source`, g/source) and (`TMPDIR = /home/sicarii/.cache/workflow-tmp`, g/tmpdir)
RL resolves the destination in the NEW mount namespace from `/` component by component with
`openat2(RESOLVE_NO_SYMLINKS | RESOLVE_NO_MAGICLINKS, O_PATH | O_DIRECTORY)` (lookups change
no atime):

- **bind mode** (every component exists as a directory): `open_tree(<held g directory>, "",
  OPEN_TREE_CLONE | AT_EMPTY_PATH)`, then `mount_setattr` with `MOUNT_ATTR_IDMAP` (the M_run
  idmap), `MOUNT_ATTR_NOSUID` and private propagation, then `move_mount` onto the resolved
  destination. The host directory's contents are hidden behind g in the view.

- **skeleton mode** (otherwise): let D be the deepest resolved directory. RL opens D read-only
  with `O_NOATIME` and lists it; creates a private `tmpfs` (`fsopen`/`fsconfig` with mode/uid/gid
  equal to D's, `fsmount` with `MOUNT_ATTR_NOSUID`); creates in it a placeholder for every entry
  of D (empty directory for a directory, empty regular file for any other type) and the missing
  chain of directories down to the destination (each 0700, owner 1000:1000, exactly as v5's
  `materialize` created `<RUNS>` and `<RUNS>/<label>`); attaches the tmpfs over D (`move_mount`);
  re-attaches every entry of D as a bind of the host entry (`open_tree(..., OPEN_TREE_CLONE |
  AT_RECURSIVE | AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT)`, nosuid, private) onto its placeholder;
  remounts the tmpfs read-only; attaches the g bind at the end of the chain.

NO host filesystem is written in either mode. An entry RL cannot re-attach is OMITTED from the
view and recorded (a stated change, Section 21 V8), never a refusal. That the clone of a symlink
entry attaches onto its placeholder and that no step calls into a mounted filesystem is premise
P-SKEL (NAMED_UNESTABLISHED; discharge S-2 source reading + I-1).

IMPLEMENTATION STATUS: MISSING. This lives in RL (sandbox_launch.py), which does not exist as
frozen code. The frame v6 scratch.py has no namespace/mount construction at all.
