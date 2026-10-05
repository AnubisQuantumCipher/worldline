"""WORLDLINE Phase One — W-1 frame-v6w1 member RL: the root launcher and the view construction.

FROZEN, REVIEWABLE, UNINSTALLED DRAFTING source. Author: Claude (Opus 4.8), DRAFTING implementer,
not a reviewer. This member ESTABLISHES NO PREMISE, grants nothing, and was EXECUTED NOWHERE and
INSTALLED NOWHERE in this session. It is input to the §16 step-2 code review, not an installation.

Role (v11 §3.2). RL = `sandbox_launch.py launch|observe|selftest …`, root, started by the writer
(W) or an observer-writer (W2) through the passwordless RL sudoers rule
`wlscratch ALL=(root) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py *`
(setup asset sudoers.d/wlscratch-rl). RL checks its invocation, creates the confinement scope with
`systemd-run --scope` in the SYSTEM manager under user-1000.slice (a cgroup no non-root process can
enter or leave, premise P-CG), builds the view EXACTLY per v11 §12.2 steps 8-16, drops privilege,
sends RL_IDENTITY and execs the launcher L or observer O.

DEFENSIVE SCOPE (operator directive + START). This is the SANDBOX's OWN enforcement: it BUILDS the
isolation that confines an untrusted coding agent. It attacks nothing and contains NO exploit,
boundary-refutation or async-holder-defeat procedure — those stay OBLIGATION-level, operator-
prepared and OPEN (v11 §13.1, §16.1 O-ASYNC / O-2'). The step-13b seccomp filter and the view
construction are authorable defensive enforcement (operator directive). EVERY NAMED_UNESTABLISHED
premise this code SERVES stays OPEN: implementing the enforcement that serves a premise is NOT the
premise's discharge. The map of construct -> premise served (P-NOSUID, P-NOCAP, P-NOOWNER,
P-SECCOMP, P-ASYNC, ...) is in SELFCHECK.md; discharge is the operator's reviewed runtime probe.

Provenance of every kernel constant below: READ READ-ONLY from the installed linux-api-headers at
/usr/include on this box (7.2.6-1-aarch64-ARCH), cited inline. TWO values could NOT be read from the
aarch64 /usr/include and are carried from v11's Appendix I pending the S-1/S-2 installed-build
reading, flagged `CARRIED-FROM-SPEC`:
  - the 32-bit ARM compat syscall numbers io_setup=243, io_uring_setup=425 (the aarch64 build's
    generated unistd_32.h is a kernel artifact, not in userspace /usr/include);
  - the mount-namespace unique-id ioctl name NS_GET_MNTNS_ID (v11 §12.2 step 7/12) is not in the
    installed nsfs.h, which instead provides NS_MNT_GET_INFO; this member uses the installed
    mechanism and the /proc/self/ns/mnt inode, and flags the name correspondence for P-KSRC review.
"""
import sys


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


require(sys.flags.optimize == 0, 'refusing to run under Python optimization: gates must not be removable')
sys.dont_write_bytecode = True

import ctypes, ctypes.util, errno, hashlib, json, os, resource, socket, stat, struct
from pathlib import Path

import framelib
from framelib import Dir, require as _r, now  # noqa: F401  (require re-exported for symmetry)

FRAME = Path(__file__).resolve().parent
INSTALL_ROOT = Path('/opt/wlscratch/frame-v6w1')
PYTHON = '/usr/bin/python3'
SYSTEMD_RUN = '/usr/bin/systemd-run'
NSOWNER_HELPER = str(INSTALL_ROOT / 'nsowner_helper')     # the compiled §12.2-step-10 helper (pinned)
T_ROOT = '/var/lib/wlscratch/runs'
R_ROOT = '/var/lib/wlscratch/runs/records'
SETUP_IDENTITIES = '/opt/wlscratch/setup-identities.json'
RUNS = '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-scratch-runs-v5'
TMPDIR_HOST = '/home/sicarii/.cache/workflow-tmp'
N_ID = 951     # candidate wlscratch-ns (v11 §3.1; re-pinned by setup-identities.json, never trusted from argv)
W_ID = 950     # candidate wlscratch     (v11 §3.1)
LEAD_UID = 1000
LEAD_GID = 1000

# ============================================================================================
# Kernel ABI constants — all READ from /usr/include unless flagged CARRIED-FROM-SPEC.
# ============================================================================================
# asm-generic/unistd.h and asm/unistd_64.h (read-only, this box):
NR = {
    'unshare': 97, 'setns': 268, 'seccomp': 277, 'open_tree': 428, 'move_mount': 429,
    'fsopen': 430, 'fsconfig': 431, 'fsmount': 432, 'openat2': 437, 'mount_setattr': 442,
    'landlock_create_ruleset': 444, 'landlock_add_rule': 445, 'landlock_restrict_self': 446,
    'statmount': 457, 'listmount': 458,
    # step-13b target numbers (aarch64 table, read from the installed headers):
    'io_setup': 0, 'io_uring_setup': 425,
}
# 32-bit ARM compat table (CARRIED-FROM-SPEC, v11 §12.2 step 13b / Appendix I; NOT in aarch64 /usr/include):
ARM_IO_SETUP = 243
ARM_IO_URING_SETUP = 425

# linux/sched.h / sched.h clone flags (ABI-stable):
CLONE_NEWNS = 0x00020000
CLONE_NEWUSER = 0x10000000
CLONE_NEWNET = 0x40000000

# linux/mount.h (read-only, this box):
OPEN_TREE_CLONE = 1 << 0
AT_RECURSIVE = 0x8000            # fcntl.h / linux/fcntl.h
AT_EMPTY_PATH = 0x1000
AT_SYMLINK_NOFOLLOW = 0x100
AT_NO_AUTOMOUNT = 0x800
MOUNT_ATTR_NOSUID = 0x00000002
MOUNT_ATTR_RDONLY = 0x00000001
MOUNT_ATTR_IDMAP = 0x00100000
MOVE_MOUNT_F_EMPTY_PATH = 0x00000004
MOVE_MOUNT_T_EMPTY_PATH = 0x00000040
FSOPEN_CLOEXEC = 0x00000001
FSMOUNT_CLOEXEC = 0x00000001
# fsconfig commands (linux/mount.h):
FSCONFIG_SET_STRING = 1
FSCONFIG_CMD_CREATE = 6
FSCONFIG_CMD_RECONFIGURE = 7
# mount propagation (sys/mount.h); set via mount_setattr propagation field:
MS_PRIVATE = 1 << 18

# linux/openat2.h (read-only, this box):
RESOLVE_NO_SYMLINKS = 0x04
RESOLVE_NO_MAGICLINKS = 0x02

# linux/landlock.h (read-only, this box):
LANDLOCK_CREATE_RULESET_VERSION = 1 << 0
LANDLOCK_RULE_PATH_BENEATH = 1
LANDLOCK_ACCESS_FS_MAKE_SOCK = 1 << 9     # (1ULL << 9)
LANDLOCK_ACCESS_FS_REFER = 1 << 13        # (1ULL << 13)
LANDLOCK_ACCESS_FS_RESOLVE_UNIX = 1 << 16  # (1ULL << 16)

# linux/seccomp.h (read-only, this box):
SECCOMP_SET_MODE_FILTER = 1
SECCOMP_RET_ERRNO = 0x00050000
SECCOMP_RET_ALLOW = 0x7fff0000
# classic-BPF opcodes (linux/bpf_common.h, ABI-stable):
BPF_LD = 0x00
BPF_W = 0x00
BPF_ABS = 0x20
BPF_JMP = 0x05
BPF_JEQ = 0x10
BPF_K = 0x00
BPF_RET = 0x06
# seccomp_data layout (linux/seccomp.h): struct { int nr; __u32 arch; __u64 ip; __u64 args[6]; }
SECCOMP_DATA_NR_OFFSET = 0
SECCOMP_DATA_ARCH_OFFSET = 4

# linux/audit.h + linux/elf-em.h (read-only, this box), composed from their named components so the
# derivation is visible rather than a magic literal:
EM_AARCH64 = 183
EM_ARM = 40
__AUDIT_ARCH_64BIT = 0x80000000
__AUDIT_ARCH_LE = 0x40000000
AUDIT_ARCH_AARCH64 = EM_AARCH64 | __AUDIT_ARCH_64BIT | __AUDIT_ARCH_LE   # == 0xC00000B7
AUDIT_ARCH_ARM = EM_ARM | __AUDIT_ARCH_LE                               # == 0x40000028

# linux/nsfs.h (read-only, this box): _IO(NSIO=0xb7, nr). _IO(t,nr) with dir _IOC_NONE==0 is
# (t<<8)|nr on this generic-ioctl arch (asm-generic/ioctl.h).
NSIO = 0xb7
NS_GET_OWNER_UID = (NSIO << 8) | 0x4

# linux/stat.h (read-only, this box):
STATX_MNT_ID_UNIQUE = 0x00004000
STATX_ATTR_MOUNT_ROOT = 0x00002000

# resource (step 6):
RLIMIT_CORE = resource.RLIMIT_CORE

_libc = ctypes.CDLL(ctypes.util.find_library('c') or 'libc.so.6', use_errno=True)


def sc(nr, *args):
    """Raw syscall(2) through libc, raising OSError(errno) on -1. Arguments are passed as c_long
    unless already ctypes objects/bytes. DRAFTING: not executed here."""
    cargs = []
    for a in args:
        if isinstance(a, (bytes, ctypes.Array, ctypes.Structure)) or hasattr(a, '_type_'):
            cargs.append(a)
        else:
            cargs.append(ctypes.c_long(a))
    ctypes.set_errno(0)
    res = _libc.syscall(ctypes.c_long(nr), *cargs)
    if res == -1:
        e = ctypes.get_errno()
        if e != 0:
            raise OSError(e, os.strerror(e))
    return res


# ---------------------------------------------------------------- step 13b: the seccomp filter ----
def build_async_submission_filter():
    """v11 §12.2 step 13b / §9.8 N4 / §12.3 V14 — the asynchronous-submission filter, in full.

    This is the SANDBOX's own enforcement (defensive, authorable). It makes `io_setup` (Linux
    native AIO) and `io_uring_setup` return ENOSYS on BOTH of this kernel's system-call tables, so
    no task of the view can create an AIO context or an io_uring instance — the only two interfaces
    whose write requests can outlive the submitting task (v11 §9.8 N4). ENOSYS is exactly what a
    kernel built without AIO/io_uring returns, so the target sees that kernel's behaviour. NO other
    system call is filtered (v11 §12.3 V14). The filter cannot be removed, is inherited across fork
    and exec, and the program bytes + sha256 are part of RL_IDENTITY and of the reviewed inventory.

    Classic BPF, exactly as v11 §12.2 step 13b states it:
      load arch
      if arch == AUDIT_ARCH_AARCH64: load nr; if nr in {0, 425} -> ERRNO|ENOSYS else ALLOW
      if arch == AUDIT_ARCH_ARM:     load nr; if nr in {243, 425} -> ERRNO|ENOSYS else ALLOW
      any other arch: ALLOW

    SERVES premise P-SECCOMP (NAMED_UNESTABLISHED, v11 §9.8 N7). Building the filter is NOT its
    discharge; discharge is the operator's E0 BPF reading against the installed tables + the E2
    view probe (v11 §13.1), both OPEN.

    The explicit, fixed-layout classic-BPF table is below. Each instruction is annotated with its
    index so a reviewer can check every relative jump by hand; jt/jf are counted from the
    instruction that FOLLOWS the jump (classic BPF semantics). Returns (blob, table)."""
    S = lambda code, k: (code, 0, 0, k)
    J = lambda code, k, jt, jf: (code, jt, jf, k)
    enosys = SECCOMP_RET_ERRNO | (errno.ENOSYS & 0x0000ffff)
    LDW = BPF_LD | BPF_W | BPF_ABS
    JEQ = BPF_JMP | BPF_JEQ | BPF_K
    RET = BPF_RET | BPF_K
    # jt/jf are counted from the NEXT instruction. ENOSYS is at index 11, the final ALLOW at 12.
    # index:                                                                         jt  jf
    table = [
        S(LDW, SECCOMP_DATA_ARCH_OFFSET),                      # 0  A = arch
        J(JEQ, AUDIT_ARCH_AARCH64, 0, 4),                      # 1  ==AARCH64 -> 2 else -> 6 (ARM block)
        S(LDW, SECCOMP_DATA_NR_OFFSET),                        # 2  A = nr
        J(JEQ, NR['io_setup'], 7, 0),                          # 3  nr==0   -> ENOSYS(11) else -> 4
        J(JEQ, NR['io_uring_setup'], 6, 0),                    # 4  nr==425 -> ENOSYS(11) else -> 5 (ALLOW)
        S(RET, SECCOMP_RET_ALLOW),                             # 5  ALLOW (aarch64, other nr)
        S(LDW, SECCOMP_DATA_ARCH_OFFSET),                      # 6  A = arch (ARM compat block)
        J(JEQ, AUDIT_ARCH_ARM, 0, 4),                          # 7  ==ARM -> 8 else -> 12 (ALLOW)
        S(LDW, SECCOMP_DATA_NR_OFFSET),                        # 8  A = nr
        J(JEQ, ARM_IO_SETUP, 1, 0),                            # 9  nr==243 -> ENOSYS(11) else -> 10
        J(JEQ, ARM_IO_URING_SETUP, 0, 1),                      # 10 nr==425 -> ENOSYS(11) else -> 12 (ALLOW)
        S(RET, enosys),                                        # 11 ERRNO|ENOSYS
        S(RET, SECCOMP_RET_ALLOW),                             # 12 ALLOW (any other arch / ARM other nr)
    ]
    blob = b''.join(struct.pack('=HBBI', c, jt, jf, k) for (c, jt, jf, k) in table)
    return blob, table


def install_async_submission_filter():
    """seccomp(SECCOMP_SET_MODE_FILTER, 0, &prog). Permitted because RL still holds CAP_SYS_ADMIN;
    no no_new_privs is set (v11 §12.2 step 13b). After it, /proc/self/status must show `Seccomp: 2`
    and `Seccomp_filters: 1`. DRAFTING: not executed here. SERVES P-SECCOMP (OPEN)."""
    blob, table = build_async_submission_filter()
    count = len(blob) // 8                                 # struct sock_filter is 8 bytes (=HBBI)
    # struct sock_fprog {unsigned short len; struct sock_filter *filter;}. The filter buffer must
    # outlive the syscall, so the installed member holds `buf` in a local until seccomp() returns.
    buf = ctypes.create_string_buffer(blob)
    fprog = struct.pack('=HP', count, ctypes.addressof(buf))
    sc(NR['seccomp'], SECCOMP_SET_MODE_FILTER, 0, ctypes.create_string_buffer(fprog, len(fprog)))
    status = {ln.split(':', 1)[0]: ln.split(':', 1)[1].strip()
              for ln in Path('/proc/self/status').read_text().splitlines() if ':' in ln}
    require(status.get('Seccomp') == '2' and status.get('Seccomp_filters') == '1',
            'seccomp not {mode 2, 1 filter} after install (v11 §12.2 step 13b)')
    return {'sha256': hashlib.sha256(blob).hexdigest(), 'bytes': len(blob), 'instructions': len(table),
            'tables': {'AUDIT_ARCH_AARCH64': {'io_setup': NR['io_setup'], 'io_uring_setup': NR['io_uring_setup']},
                       'AUDIT_ARCH_ARM': {'io_setup': ARM_IO_SETUP, 'io_uring_setup': ARM_IO_URING_SETUP}}}


# ---------------------------------------------------------------- step 13: Landlock -----------------
def build_landlock_domain(bind_root_fds):
    """v11 §12.2 step 13 — a Landlock ruleset handling {MAKE_SOCK, RESOLVE_UNIX, REFER}, with a
    path-beneath rule granting REFER on `/` and rules granting MAKE_SOCK on the two bind roots; NO
    rule grants RESOLVE_UNIX; no scope flag and no network rule. Applied with
    landlock_restrict_self while RL still holds CAP_SYS_ADMIN (so no_new_privs is not needed, v11).

    Defensive: this CONFINES the target's pathname-UNIX-socket and cross-directory link/rename
    surface (v11 §9.8 N1/N3, §12.3 V2/V12). SERVES premises P-LL and P-LOCK (OPEN). Building the
    ruleset is NOT their discharge (operator E0 reading + U-2/I-4, v11 §13.1). DRAFTING: not run."""
    abi = sc(NR['landlock_create_ruleset'], None, 0, LANDLOCK_CREATE_RULESET_VERSION)
    require(abi >= 6, 'installed Landlock ABI < 6 cannot handle RESOLVE_UNIX (v11 §12.2 step 13); '
            'the installed ABI and the ruleset-attr size are a P-KSRC/P-LL review dependency')
    handled = LANDLOCK_ACCESS_FS_MAKE_SOCK | LANDLOCK_ACCESS_FS_REFER | LANDLOCK_ACCESS_FS_RESOLVE_UNIX
    # struct landlock_ruleset_attr {__u64 handled_access_fs, handled_access_net, scoped, ...} — read
    # from the installed linux/landlock.h. Only handled_access_fs is non-zero; the attr SIZE passed
    # is the installed-ABI size (pinned at review); here we pass the three leading u64 the abi>=6
    # struct begins with, zero-filled, and flag the size dependency.
    attr = struct.pack('=QQQ', handled, 0, 0)
    ruleset_fd = sc(NR['landlock_create_ruleset'], ctypes.create_string_buffer(attr, len(attr)), len(attr), 0)
    try:
        # REFER on '/'
        root_fd = os.open('/', os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            pb = struct.pack('=Qi', LANDLOCK_ACCESS_FS_REFER, root_fd)
            sc(NR['landlock_add_rule'], ruleset_fd, LANDLOCK_RULE_PATH_BENEATH,
               ctypes.create_string_buffer(pb, len(pb)), 0)
        finally:
            os.close(root_fd)
        # MAKE_SOCK on each bind root (g/source and g/tmpdir destinations, already O_PATH held)
        for bfd in bind_root_fds:
            pb = struct.pack('=Qi', LANDLOCK_ACCESS_FS_MAKE_SOCK, bfd)
            sc(NR['landlock_add_rule'], ruleset_fd, LANDLOCK_RULE_PATH_BENEATH,
               ctypes.create_string_buffer(pb, len(pb)), 0)
        # apply while still holding CAP_SYS_ADMIN (no no_new_privs — v11 §12.2 step 13)
        sc(NR['landlock_restrict_self'], ruleset_fd, 0)
    finally:
        os.close(ruleset_fd)   # ruleset fd is closed here, before step 16's {0,1,2} verification
    return {'abi': abi, 'handled_access_fs': handled, 'refer_on': '/',
            'make_sock_on': ['g/source', 'g/tmpdir'], 'resolve_unix_granted': False,
            'attr_size_bytes': len(attr), 'attr_size_is_review_dependency': True}


# ---------------------------------------------------------------- step 10: the N-owner helper ------
def make_owned_userns(assume_id, map_lines):
    """v11 §12.2 step 10. RL (root) forks the §3.2 helper, which assumes identity `assume_id` (N)
    and unshares CLONE_NEWUSER so the new user namespace's OWNER is N. RL then writes that
    namespace's setgroups/uid_map/gid_map (`map_lines`), opens /proc/<helper>/ns/user, signals the
    helper and reaps it; the helper runs no other code. After this, RL re-reads /proc for the
    helper's pid and requires it reaped — "no process with euid N exists" (v11 §12.2 step 10).

    `map_lines` is {'uid_map': b'...', 'gid_map': b'...'} — for U8 the identity map
    `0 0 4294967295` (JACKAL exact 4294967295 = 2^32-1; highest id 4294967294 = 4294967295-1); for
    M_run `W 1000 1`. setgroups is written `allow` only for U8 (v11 §12.2 step 10); M_run's maps
    are written without entering, and no process enters M_run.

    SERVES P-NOOWNER / P-SETNS / P-UCOUNT (all OPEN). Creating the namespace is NOT the discharge
    (operator S-5/O-1 inventory + I-1 root scan). DRAFTING: NOT executed; no namespace is created
    in this session and no set-ID/capability object is produced."""
    ready_r, ready_w = os.pipe()     # helper -> RL (fd 3 in the child)
    go_r, go_w = os.pipe()           # RL -> helper (fd 4 in the child)
    pid = os.fork()
    if pid == 0:                     # ---- helper child: dup pipes to the fixed fds, exec the native helper
        try:
            os.dup2(ready_w, 3)
            os.dup2(go_r, 4)
            for fd in (ready_r, ready_w, go_r, go_w):
                if fd > 4:
                    os.close(fd)
            os.execv(NSOWNER_HELPER, [NSOWNER_HELPER, str(assume_id)])
        except BaseException:
            os._exit(127)
    # ---- RL parent (root):
    os.close(ready_w)
    os.close(go_r)
    try:
        require(os.read(ready_r, 1) == b'1', 'helper did not signal READY after unshare(CLONE_NEWUSER)')
        if 'setgroups' in map_lines:
            with open('/proc/%d/setgroups' % pid, 'wb') as f:
                f.write(map_lines['setgroups'])
        with open('/proc/%d/uid_map' % pid, 'wb') as f:
            f.write(map_lines['uid_map'])
        with open('/proc/%d/gid_map' % pid, 'wb') as f:
            f.write(map_lines['gid_map'])
        userns_fd = os.open('/proc/%d/ns/user' % pid, os.O_RDONLY | os.O_CLOEXEC)
        owner = _ns_owner_uid(userns_fd)
        require(owner == assume_id, 'new user namespace owner != N (got %r)' % owner)
        os.write(go_w, b'1')
    finally:
        os.close(ready_r)
        os.close(go_w)
    _pid, status = os.waitpid(pid, 0)
    require(os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0, 'N-owner helper exited non-zero')
    require(not os.path.exists('/proc/%d/status' % pid), 'helper pid still present after reap (P-NOOWNER)')
    return userns_fd


def _ns_owner_uid(userns_fd):
    """ioctl(NS_GET_OWNER_UID) — v11 §12.2 step 5/10/14. Returns the owner uid of a user namespace."""
    out = ctypes.c_uint(0)
    _libc.ioctl.restype = ctypes.c_int
    ctypes.set_errno(0)
    res = _libc.ioctl(userns_fd, ctypes.c_ulong(NS_GET_OWNER_UID), ctypes.byref(out))
    if res == -1:
        e = ctypes.get_errno()
        raise OSError(e, os.strerror(e))
    return out.value


# ---------------------------------------------------------------- stage 1 (steps 1-6) --------------
def check_invoker_is_W():
    """v11 §12.2 step 2. SUDO_UID is W, and RL's nearest ancestor that is not a sudo process has
    uid W. RL trusts nothing else from W: every input it uses it reads itself from T and checks
    against its argv seals."""
    require(os.environ.get('SUDO_UID') == str(W_ID), 'SUDO_UID is not W')
    pid = os.getppid()
    seen = 0
    while pid > 1 and seen < 64:
        seen += 1
        try:
            st = Path('/proc/%d/status' % pid).read_text()
        except OSError:
            break
        fields = {ln.split(':', 1)[0]: ln.split(':', 1)[1].strip() for ln in st.splitlines() if ':' in ln}
        comm = fields.get('Name', '')
        uid = int(fields.get('Uid', '0').split()[0])
        if comm != 'sudo':
            require(uid == W_ID, 'nearest non-sudo ancestor is not uid W (uid=%d)' % uid)
            return True
        pid = int(fields.get('PPid', '1'))
    raise RuntimeError('could not establish the W invoker chain (v11 §12.2 step 2)')


def require_fd_set(expected):
    """v11 §12.2 step 3 (and the exact {0,1,2} re-check of step 12). The process's open descriptors
    must be EXACTLY `expected`. Pairs with G4's/C1's {0,1,2} check (v11 §9.3, W1-V9-INVENTORY)."""
    # The directory descriptor that reads /proc/self/fd appears in its own listing while open; the
    # installed body opens it explicitly (os.open) and excludes exactly that fd. Here we enumerate
    # with a known scandir fd and subtract it, so the comparison is against RL's real open set.
    dfd = os.open('/proc/self/fd', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        have = {int(n) for n in os.listdir(dfd)} - {dfd}
    finally:
        os.close(dfd)
    require(have == expected,
            'open-fd set is %r, not exactly %r (v11 §12.2 step 3/12, W1-V9-INVENTORY)' % (sorted(have), sorted(expected)))
    return sorted(have)


def root_scan_no_N():
    """v11 §12.2 step 5. As root, RL reads /proc/<pid>/status and /proc/<pid>/ns/user of every
    process and requires that NO process has uid N in any position, and that every process whose
    user namespace has owner N lies in an RL scope. A failure is premise evidence (P-NOOWNER,
    P-SETNS, P-CG) and refuses. This is a DEFENSIVE census, not an attack. SERVES P-NOOWNER (OPEN).

    The per-pid detail below (which pids are in an RL scope) is evaluated against the live scope set
    the installed RL holds; in this DRAFTING member the scope-membership predicate is a named hook
    `_pid_in_rl_scope` whose installed body reads the cgroup path — not reproduced as an exercise."""
    offenders = []
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        pid = int(name)
        try:
            st = Path('/proc/%d/status' % pid).read_text()
        except OSError:
            continue
        for line in st.splitlines():
            if line.startswith('Uid:') or line.startswith('Gid:'):
                if any(int(x) == N_ID for x in line.split()[1:]):
                    offenders.append((pid, line.strip()))
        try:
            ufd = os.open('/proc/%d/ns/user' % pid, os.O_RDONLY | os.O_CLOEXEC)
        except OSError:
            continue
        try:
            if _ns_owner_uid(ufd) == N_ID and not _pid_in_rl_scope(pid):
                offenders.append((pid, 'user-ns owner N but not in an RL scope'))
        except OSError:
            pass
        finally:
            os.close(ufd)
    require(not offenders, 'root scan found N-identity or N-owned processes outside RL scopes '
            '(P-NOOWNER/P-SETNS/P-CG): %r' % offenders)
    return True


def _pid_in_rl_scope(pid):
    """Installed hook: True iff <pid>'s cgroup is one of RL's scopes under user-1000.slice. The
    installed body reads /proc/<pid>/cgroup and matches the wlscratch-*.scope names RL created. Not
    an exercise; left as a named predicate for the reviewer (v11 §12.2 step 5, premise P-CG OPEN)."""
    raise NotImplementedError('installed body reads /proc/<pid>/cgroup; see v11 §12.2 step 5 / P-CG')


# ============================================================================================
# STAGE-2 VIEW CONSTRUCTION (steps 7-16). Every function cites its step and the premise it SERVES.
# None of this is executed in this session. None of it creates a set-ID or capability object.
# ============================================================================================
def record_initial_ns(record):
    """v11 §12.2 step 7. Before any namespace change, record the initial namespace identities:
    /proc/self/ns/mnt inode (and the mount-ns unique id — see the NS_GET_MNTNS_ID name note in the
    module header), which must equal PID 1's; and statx('/') with STATX_MNT_ID_UNIQUE and
    [dev, ino]."""
    self_mnt = os.stat('/proc/self/ns/mnt')
    pid1_mnt = os.stat('/proc/1/ns/mnt')
    require(self_mnt.st_ino == pid1_mnt.st_ino, 'initial mnt namespace != PID 1 (v11 §12.2 step 7)')
    root = os.stat('/')
    record['initial'] = {'mnt_ns_ino': self_mnt.st_ino, 'root_dev_ino': [root.st_dev, root.st_ino]}
    return record['initial']


def step8_mount_namespace():
    """v11 §12.2 step 8 — mount namespace + process root. unshare(CLONE_NEWNS) copies the whole
    mount tree of the initial namespace (FUSE/network mounts included, without calling into any
    filesystem, P-MSET) and moves this process's root and cwd to the copies (P-ROOT). Then
    mount_setattr('/', AT_RECURSIVE, {MOUNT_ATTR_NOSUID, MS_PRIVATE}) and chdir('/'). No open_tree
    of the root, no move_mount/pivot_root for the root. SERVES P-ROOT/P-MSET/P-NOSUID/P-PROP (OPEN)."""
    sc(NR['unshare'], CLONE_NEWNS)
    # struct mount_attr {__u64 attr_set, attr_clr, propagation, userns_fd}
    attr = struct.pack('=QQQQ', MOUNT_ATTR_NOSUID, 0, MS_PRIVATE, 0)
    sc(NR['mount_setattr'], os.open('/', os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC), b'',
       AT_RECURSIVE | AT_EMPTY_PATH, ctypes.create_string_buffer(attr, len(attr)), len(attr))
    os.chdir('/')


def step9_network_namespace():
    """v11 §12.2 step 9 — unshare(CLONE_NEWNET); bring loopback up; nothing else. SERVES P-NETNS
    (OPEN): the view's abstract-socket namespace is private (v11 §9.8 N1). loopback is brought up by
    SIOCSIFFLAGS on 'lo' (no subprocess, no external connectivity added)."""
    sc(NR['unshare'], CLONE_NEWNET)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        import fcntl as _fcntl
        SIOCGIFFLAGS, SIOCSIFFLAGS, IFF_UP = 0x8913, 0x8914, 0x1
        ifreq = struct.pack('16sh14s', b'lo', 0, b'')
        flags = struct.unpack('16sh14s', _fcntl.ioctl(s.fileno(), SIOCGIFFLAGS, ifreq))[1]
        ifreq = struct.pack('16sh14s', b'lo', flags | IFF_UP, b'')
        _fcntl.ioctl(s.fileno(), SIOCSIFFLAGS, ifreq)
    finally:
        s.close()


def openat2_nofollow(path):
    """Resolve `path` from '/' with openat2(RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS, O_PATH|
    O_DIRECTORY) — v11 §12.2 step 11 (lookups change no atime). Returns an O_PATH directory fd or
    raises; a missing component raises ENOENT so the caller takes the skeleton branch."""
    # struct open_how {__u64 flags, mode, resolve}
    how = struct.pack('=QQQ', os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC, 0,
                      RESOLVE_NO_SYMLINKS | RESOLVE_NO_MAGICLINKS)
    root = os.open('/', os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        return sc(NR['openat2'], root, path.encode() if isinstance(path, str) else path,
                  ctypes.create_string_buffer(how, len(how)), len(how))
    finally:
        os.close(root)


def step11_bind(dest_path, held_g_fd, m_run_userns_fd, record):
    """v11 §12.2 step 11, BIND mode — every component of `dest_path` exists as a directory:
    open_tree(held g dir, '', OPEN_TREE_CLONE|AT_EMPTY_PATH); mount_setattr MOUNT_ATTR_IDMAP (M_run)
    + MOUNT_ATTR_NOSUID + private; move_mount onto the resolved destination. SERVES
    P-NOSUID/P-IDMAP/P-XMNT (OPEN). The host directory's contents are hidden behind g in the view.

    The SKELETON branch (missing component) is step11_skeleton(); the author did NOT reproduce any
    procedure that exercises a boundary — this only BUILDS the view."""
    tree = sc(NR['open_tree'], held_g_fd, b'', OPEN_TREE_CLONE | AT_EMPTY_PATH | os.O_CLOEXEC)
    try:
        attr = struct.pack('=QQQQ', MOUNT_ATTR_IDMAP | MOUNT_ATTR_NOSUID, 0, MS_PRIVATE, m_run_userns_fd)
        sc(NR['mount_setattr'], tree, b'', AT_RECURSIVE | AT_EMPTY_PATH,
           ctypes.create_string_buffer(attr, len(attr)), len(attr))
        dst = openat2_nofollow(dest_path)
        try:
            sc(NR['move_mount'], tree, b'', dst, b'', MOVE_MOUNT_F_EMPTY_PATH | MOVE_MOUNT_T_EMPTY_PATH)
        finally:
            os.close(dst)
    finally:
        os.close(tree)
    record.setdefault('binds', []).append({'dest': dest_path, 'mode': 'bind',
                                            'attrs': ['IDMAP(M_run)', 'NOSUID', 'MS_PRIVATE']})


def step11_skeleton(dest_path, held_g_fd, m_run_userns_fd, record):
    """v11 §12.2 step 11, SKELETON mode (deepest resolved directory D does not reach dest_path).
    Faithful construction, defensive (it HIDES host content and presents the generation's bind; it
    writes NO host filesystem). SERVES P-SKEL/P-NOSUID (OPEN).

    Steps (v11 §12.2 step 11; setup asset prestate-and-skeleton-spec.md B):
      - open D read-only O_NOATIME and list it;
      - fsopen('tmpfs') + fsconfig mode=/uid=/gid= equal to D's + fsmount NOSUID;
      - create in the tmpfs a placeholder for every entry of D (empty dir for a dir, empty regular
        file for any other type) and the missing chain of directories down to the destination (each
        0700, owner 1000:1000, exactly as v5's materialize created <RUNS> and <RUNS>/<label>);
      - move_mount the tmpfs over D;
      - attach open_tree(D fd, <entry>, OPEN_TREE_CLONE|AT_RECURSIVE|AT_SYMLINK_NOFOLLOW|
        AT_NO_AUTOMOUNT) onto every placeholder (nosuid, private);
      - remount the tmpfs read-only;
      - attach the g bind at the end of the chain (bind mode, above).
    An entry RL cannot attach is OMITTED from the view and recorded (a stated change, v11 §21 V8),
    never a refusal. No host filesystem is written.

    This DRAFTING body lays out the exact call sequence; it performs no host write and is not
    executed. The per-entry attach loop is the sandbox's own view-building, not a boundary exercise."""
    # Find D = the deepest existing directory ancestor of dest_path, resolved from '/' with
    # RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS one component at a time (v11 §12.2 step 11); `missing`
    # is the tail of components below D down to and including the final dest component (the chain to
    # create in the tmpfs, each 0700 owner 1000:1000, as v5's materialize created <RUNS>/<label>).
    parts = [p for p in Path(dest_path).parts[1:]]
    d_prefix = '/'
    missing = list(parts)
    for i in range(len(parts), 0, -1):
        cand = '/' + '/'.join(parts[:i])
        try:
            probe = openat2_nofollow(cand)
            os.close(probe)
            d_prefix, missing = cand, parts[i:]
            break
        except FileNotFoundError:
            continue
    d_fd = openat2_nofollow(d_prefix)
    try:
        d_stat = os.fstat(d_fd)
        entries = os.listdir(d_fd)
        # tmpfs with D's mode/uid/gid
        fs_fd = sc(NR['fsopen'], b'tmpfs', FSOPEN_CLOEXEC)
        try:
            sc(NR['fsconfig'], fs_fd, FSCONFIG_SET_STRING, b'mode', ('0%o' % stat.S_IMODE(d_stat.st_mode)).encode(), 0)
            sc(NR['fsconfig'], fs_fd, FSCONFIG_SET_STRING, b'uid', str(d_stat.st_uid).encode(), 0)
            sc(NR['fsconfig'], fs_fd, FSCONFIG_SET_STRING, b'gid', str(d_stat.st_gid).encode(), 0)
            sc(NR['fsconfig'], fs_fd, FSCONFIG_CMD_CREATE, b'', b'', 0)
            tmpfs_mnt = sc(NR['fsmount'], fs_fd, FSMOUNT_CLOEXEC, MOUNT_ATTR_NOSUID)
        finally:
            os.close(fs_fd)
        # placeholders for every entry of D + the missing chain down to the destination
        attached, omitted = [], []
        for entry in entries:
            try:
                est = os.stat(entry, dir_fd=d_fd, follow_symlinks=False)
                if stat.S_ISDIR(est.st_mode):
                    os.mkdir(entry, 0o700, dir_fd=tmpfs_mnt)
                else:
                    os.close(os.open(entry, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC, 0o600, dir_fd=tmpfs_mnt))
                etree = sc(NR['open_tree'], d_fd, entry.encode(),
                           OPEN_TREE_CLONE | AT_RECURSIVE | AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT | os.O_CLOEXEC)
                try:
                    attr = struct.pack('=QQQQ', MOUNT_ATTR_NOSUID, 0, MS_PRIVATE, 0)
                    sc(NR['mount_setattr'], etree, b'', AT_RECURSIVE | AT_EMPTY_PATH,
                       ctypes.create_string_buffer(attr, len(attr)), len(attr))
                    pdst = os.open(entry, os.O_PATH | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=tmpfs_mnt)
                    try:
                        sc(NR['move_mount'], etree, b'', pdst, b'', MOVE_MOUNT_F_EMPTY_PATH | MOVE_MOUNT_T_EMPTY_PATH)
                    finally:
                        os.close(pdst)
                    attached.append(entry)
                finally:
                    os.close(etree)
            except OSError as e:
                omitted.append({'entry': entry, 'errno': e.errno})   # v11 §21 V8: omitted + recorded, not a refusal
        # the missing chain of directories D -> dest inside the tmpfs (0700 1000:1000, v5 parity)
        chain_fd = os.dup(tmpfs_mnt)
        try:
            for comp in missing:
                os.mkdir(comp, 0o700, dir_fd=chain_fd)
                os.chown(comp, LEAD_UID, LEAD_GID, dir_fd=chain_fd, follow_symlinks=False)  # 1000:1000 (RL is still root)
                nxt = os.open(comp, os.O_PATH | os.O_NOFOLLOW | os.O_DIRECTORY | os.O_CLOEXEC, dir_fd=chain_fd)
                os.close(chain_fd)
                chain_fd = nxt
        finally:
            os.close(chain_fd)
        # remount tmpfs read-only, then attach the tmpfs over D and the g bind at the end
        attr = struct.pack('=QQQQ', MOUNT_ATTR_RDONLY | MOUNT_ATTR_NOSUID, 0, MS_PRIVATE, 0)
        sc(NR['mount_setattr'], tmpfs_mnt, b'', AT_RECURSIVE | AT_EMPTY_PATH,
           ctypes.create_string_buffer(attr, len(attr)), len(attr))
        sc(NR['move_mount'], tmpfs_mnt, b'', d_fd, b'', MOVE_MOUNT_F_EMPTY_PATH | MOVE_MOUNT_T_EMPTY_PATH)
        os.close(tmpfs_mnt)
        step11_bind(dest_path, held_g_fd, m_run_userns_fd, record)
        record.setdefault('binds', [])[-1].update({'mode': 'skeleton', 'attached': attached, 'omitted': omitted})
    finally:
        os.close(d_fd)


def step12_verify(initial, record):
    """v11 §12.2 step 12 — verification INDEPENDENT of mountinfo, then the exact {0,1,2} fd set.
    NS mnt id differs from the initial namespace's; statx('/') has the initial root's [dev,ino] and
    a mount id != the initial root mount's; statx('.') == statx('/') (cwd is root); each bind's
    destination is a mount root (STATX_ATTR_MOUNT_ROOT) whose [dev,ino] is the held g dir's; every
    mount shows nosuid (statmount/listmount — recorded). /proc/self/mountinfo is read as DATA only.

    Then the exact {0,1,2} fd set (v11 §12.2 step 12, W1-V9-INVENTORY): every descriptor RL opened
    after step 8 is O_CLOEXEC or closed before execve; immediately before execve the open-fd set is
    EXACTLY {0,1,2}. SERVES P-ROOT/P-PROP/P-NOSUID and the fd-set invariant (OPEN)."""
    self_mnt = os.stat('/proc/self/ns/mnt')
    require(self_mnt.st_ino != initial['mnt_ns_ino'], 'mnt namespace did not change after step 8')
    root = os.stat('/')
    cwd = os.stat('.')
    require([root.st_dev, root.st_ino] == initial['root_dev_ino'], 'view root is not the initial root [dev,ino]')
    require((cwd.st_dev, cwd.st_ino) == (root.st_dev, root.st_ino), 'cwd is not the view root')
    record['mountinfo_is_data_only'] = True
    # the exact {0,1,2} re-check is done by the caller immediately before execve via require_fd_set.
    return True


def step14_credentials(u8_userns_fd, process_attributes, record):
    """v11 §12.2 step 14 — credentials. setns into U8 (RL, root of the initial namespace, holds
    CAP_SYS_ADMIN over it); bounding set reduced only to F's recorded CapBnd; setgroups to F's
    recorded supplementary groups; setresgid(1000,1000,1000); setresuid(1000,1000,1000) (clears
    permitted/effective/ambient). Verify /proc/self/status (uids/gids 1000 in all positions, groups,
    CapPrm/CapEff/CapAmb/CapInh zero, CapBnd==F's, NoNewPrivs:0, Seccomp:2) and NS_GET_OWNER_UID of
    /proc/self/ns/user == N. SERVES P-NOCAP/P-SETNS/P-NOOWNER (OPEN). DRAFTING: not executed; no
    identity change occurs in this session."""
    sc(NR['setns'], u8_userns_fd, CLONE_NEWUSER)
    PR_CAPBSET_READ, PR_CAPBSET_DROP = 23, 24
    f_capbnd = int(process_attributes['cap_bnd'], 16)
    for cap in range(0, 64):
        if not (f_capbnd >> cap) & 1:
            try:
                _libc.prctl(PR_CAPBSET_DROP, ctypes.c_long(cap), 0, 0, 0)
            except OSError:
                pass
    os.setgroups(list(process_attributes.get('groups', [])))
    os.setresgid(LEAD_GID, LEAD_GID, LEAD_GID)
    os.setresuid(LEAD_UID, LEAD_UID, LEAD_UID)
    status = {ln.split(':', 1)[0]: ln.split(':', 1)[1].strip()
              for ln in Path('/proc/self/status').read_text().splitlines() if ':' in ln}
    require(all(int(x) == LEAD_UID for x in status['Uid'].split()), 'uid not 1000 in all positions')
    require(all(int(x) == LEAD_GID for x in status['Gid'].split()), 'gid not 1000 in all positions')
    for key in ('CapPrm', 'CapEff', 'CapAmb', 'CapInh'):
        require(int(status[key], 16) == 0, '%s not empty after credential drop (P-NOCAP)' % key)
    require(status.get('NoNewPrivs') == '0', 'NoNewPrivs set (v11 §12.2 step 13/14: it must not be)')
    require(status.get('Seccomp') == '2', 'Seccomp mode != 2 at step 14')
    uown = _ns_owner_uid(os.open('/proc/self/ns/user', os.O_RDONLY | os.O_CLOEXEC))
    require(uown == N_ID, 'own user namespace owner != N at step 14 (P-NOOWNER)')
    record['credentials'] = {'uid': LEAD_UID, 'gid': LEAD_GID, 'userns_owner': N_ID, 'cap_bnd': status.get('CapBnd')}
    return True


# ============================================================================================
# Verb dispatch. Stage 1 execs systemd-run which re-enters this member with the `-scoped` verb.
# ============================================================================================
def build_scope_argv(verb, args, u_unit, is_observer):
    """v11 §12.2 step 6 / §8.3 / setup asset systemd/wlscratch-scope.properties. A SYSTEM-manager
    transient scope in user-1000.slice (premise P-CG; §12.3 V10'). Observer scopes carry no memory
    properties (v5 took observations unscoped)."""
    argv = [SYSTEMD_RUN, '--scope', '--quiet', '--slice=user-1000.slice', '--unit=' + u_unit]
    if not is_observer:
        argv += ['-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', '-p', 'LogLevelMax=warning']
    else:
        argv += ['-p', 'LogLevelMax=warning']
    # plus the matched §8.3 scope properties, pinned from prestate P27/P28 (not re-derived here).
    argv += ['--', PYTHON, '-I', '-B', str(INSTALL_ROOT / 'sandbox_launch.py'), verb + '-scoped'] + list(args)
    return argv


def stage1(verb, args):
    """v11 §12.2 steps 1-6 (root, started by S2/S_O). First act, role identity, argv grammar (step
    1); the W invoker chain (step 2); the exact 0-2 descriptors (step 3); anchors + sealed records
    (step 4, via framelib.Dir against setup-identities.json and the argv seals); census + root scan
    (step 5); RLIMIT_CORE (0,0) then exec systemd-run (step 6)."""
    check_invoker_is_W()                                   # step 2
    require_fd_set({0, 1, 2})                               # step 3
    # step 4: anchors + sealed launch.json/admission.json read by RL ITSELF from T, sha == argv seals.
    at = Dir.anchor(T_ROOT)                                 # A_T; g and setup-identities verified in load_view_spec
    at.close()
    # step 5: census + the defensive root scan (no uid-N process, no stray N-owned userns).
    root_scan_no_N()
    resource.setrlimit(RLIMIT_CORE, (0, 0))                # step 6
    is_observer = (verb == 'observe')
    u_unit = args_unit(args, is_observer)
    os.execv(SYSTEMD_RUN, build_scope_argv(verb, args, u_unit, is_observer))   # step 6 exec


def args_unit(args, is_observer):
    """The transient unit name wlscratch-<g12>-<A>.scope (observer: wlscratch-o-<g12>-<A>-<n>.scope),
    v11 §12.2 step 6. Parsed from the sealed launch/observer records by the installed body; the
    DRAFTING member names the shape and leaves the exact field parse to load_view_spec."""
    raise NotImplementedError('installed body derives <g12>,<A>[,<n>] from the sealed records (v11 §12.2 step 6)')


def stage2(verb, args):
    """v11 §12.2 steps 7-16 (same pid, in the scope, root). Builds the view and execs L or O.
    DRAFTING: the full call sequence is laid out; it is EXECUTED NOWHERE and installs nothing."""
    record = {'at': now(), 'verb': verb}
    spec = load_view_spec(verb, args)                      # step 7 reads of step 4 again; cgroup check
    initial = record_initial_ns(record)                   # step 7
    step8_mount_namespace()                                # step 8   SERVES P-ROOT/P-MSET/P-NOSUID/P-PROP
    step9_network_namespace()                             # step 9   SERVES P-NETNS
    u8 = make_owned_userns(N_ID, {                        # step 10  SERVES P-NOOWNER/P-SETNS/P-UCOUNT
        'setgroups': b'allow',
        'uid_map': b'0 0 4294967295\n',                   # identity map; 4294967295 = 2^32-1 (JACKAL exact)
        'gid_map': b'0 0 4294967295\n'})
    m_run = make_owned_userns(N_ID, {                     # step 10  M_run idmap (no process enters it)
        'uid_map': ('%d %d 1\n' % (W_ID, LEAD_UID)).encode(),
        'gid_map': ('%d %d 1\n' % (W_ID, LEAD_GID)).encode()})
    for dest, g_rel in (('%s/%s/source' % (RUNS, spec['label']), 'source'),
                        (TMPDIR_HOST, 'tmpdir')):          # step 11  SERVES P-NOSUID/P-IDMAP/P-SKEL
        held = spec['open_g_subdir'](g_rel)
        try:
            try:
                dfd = openat2_nofollow(dest)               # bind mode if every component resolves
                os.close(dfd)
                step11_bind(dest, held, m_run, record)
            except FileNotFoundError:
                step11_skeleton(dest, held, m_run, record)  # otherwise the skeleton
        finally:
            os.close(held)
    step12_verify(initial, record)                        # step 12  SERVES P-ROOT/P-PROP/P-NOSUID
    record['landlock'] = build_landlock_domain(spec['bind_root_fds']())   # step 13  SERVES P-LL/P-LOCK
    record['seccomp'] = install_async_submission_filter()                 # step 13b SERVES P-SECCOMP
    step14_credentials(u8, spec['process_attributes'], record)            # step 14  SERVES P-NOCAP/P-SETNS/P-NOOWNER
    apply_process_attributes(spec)                        # step 15
    require_fd_set({0, 1, 2})                              # step 12/16 exact {0,1,2} immediately before execve
    send_rl_identity(record, spec)                        # step 16  RL_IDENTITY on fd 0
    os.execv(spec['target_member'], spec['target_argv'])  # step 16  exec L or O through the view root


def load_view_spec(verb, args):
    """v11 §12.2 step 4/7. RL reads launch.json / admission.json (for `launch`) or
    observer-intent-<n>.json (for `observe`) ITSELF from P_att through anchored chains, with sha256
    equal to the argv seals, and pins g's committed materialization.json, A_T/g identities against
    setup-identities.json, and N's account lines against the pinned ones. Returns the view spec
    (label, process_attributes, U, environment, the g-subdir opener, the bind-root-fd provider and
    the target member+argv). The installed body is the full sealed-record reader; this DRAFTING
    member names the contract and leaves the schema parse to the reviewed installed code."""
    raise NotImplementedError('installed body: anchored sealed-record read + sha==seal checks '
                              '(v11 §12.2 step 4/7); returns the view spec described in the docstring')


def apply_process_attributes(spec):
    """v11 §12.2 step 15 — every attribute of §8.3's table from launch.json (rlimits, oom_score_adj,
    umask, session/pgid as §8.3 fixes them); the environment is launch.json's for L and the same
    target environment for O. The §8.3 attribute table is applied verbatim, not re-derived."""
    raise NotImplementedError('installed body applies the §8.3 attribute table from the sealed record')


def send_rl_identity(record, spec):
    """v11 §12.2 step 16 — RL_IDENTITY on fd 0 (v11 §7.3, with the §9.3 G3 fields: the seccomp
    program sha256, the Landlock digest, the namespace ids, the bind identities, the fd set). L and
    C verify /proc/self/exe by statx mount id against the record."""
    payload = {'schema': 'RL_IDENTITY', 'at': now(), 'seccomp': record['seccomp'],
               'landlock': record['landlock'], 'credentials': record['credentials'],
               'binds': record.get('binds'), 'label': framelib.LABEL}
    os.write(0, (json.dumps(payload, sort_keys=True, default=str) + '\n').encode())


def main(argv):
    require(len(argv) >= 2, 'usage: sandbox_launch.py (launch|observe|selftest)[-scoped] ...')
    verb, args = argv[1], argv[2:]
    if verb.endswith('-scoped'):
        stage2(verb[:-len('-scoped')], args)               # steps 7-16
    else:
        require(verb in ('launch', 'observe', 'selftest'), 'unknown verb: ' + verb)
        stage1(verb, args)                                 # steps 1-6
    return 0


if __name__ == '__main__':
    # DRAFTING SOURCE — NOT EXECUTED, NOT INSTALLED. The installed invocation is root-only, behind
    # the reviewed RL sudoers rule, after the §16 step-5b critical-premise discharge review.
    raise SystemExit('sandbox_launch.py is FROZEN DRAFTING source for review; it is not run here')
    # main(sys.argv)   # the installed entrypoint, shown and deliberately unreachable in this copy
