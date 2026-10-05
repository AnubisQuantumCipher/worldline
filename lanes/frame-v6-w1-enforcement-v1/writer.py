"""WORLDLINE Phase One — W-1 frame-v6w1 member W: the privileged writer.

FROZEN, REVIEWABLE, UNINSTALLED DRAFTING source. Author: Claude (Opus 4.8), DRAFTING implementer,
not a reviewer. ESTABLISHES NO PREMISE; EXECUTED NOWHERE, INSTALLED NOWHERE this session.

Role (v11 §3.2). W = `writer.py <verb> …`, uid/gid wlscratch (W); the ONLY writer of generation
trees. F starts it through the S1 sudoers rule
`sicarii ALL=(wlscratch) NOPASSWD: /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py *`
(setup asset sudoers.d/wlscratch-frame). Because that rule lets A1 run writer.py as W with ANY
arguments, W must be robust to arbitrary input and must do ONLY what §5 authorizes (v11 §9.8 N2
row for writer.py-as-W). Verbs: adopt, materialize, dispatch, selftest, seal-front (W2).

WHAT W MAY DO, EXACTLY (v11 §5.2, the complete mutation list). Every mutation lies inside the
protected run tree T (§3.4), reached through anchored descriptor chains, create-only, via
framelib.commit (O_TMPFILE + create-only linkat, v11 §10.1); W renames/deletes/truncates/chmods/
re-ACLs NOTHING existing, writes nothing in lease/, nothing below source/ after M8, nothing in
tmpdir/ after M7, and nothing outside T. This member routes EVERY write through `authorize()` +
`commit`, so the mutation set is auditable in one place.

WHAT W NEVER DOES (v11 §9.8 N7 T-W/T-RL, the S-5 code-review obligation). W and W2 make NO boundary
call — no setns, unshare, ptrace, pidfd_getfd, process_vm_* — and open no other process's
/proc/<pid>/{mem,fd,root,cwd}. The view is built only by RL (sandbox_launch.py), which W invokes
through the RL sudoers rule; W never builds a namespace itself. Enforcing this in code is NOT the
discharge of T-W/T-RL (that is the operator's reviewed S-5 reading, OPEN).

The pull-closure does NOT rest on this member's behaviour for U8: v11 §12.2 step 10 chose N (not
W) to own U8, so an euid-W writer holds NO capability over any U8 (v11 §9.8 N2). It still rests on
W for g, which W owns (v11 §2.2). Premises P-NOOWNER etc. stay OPEN.
"""
import sys


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


require(sys.flags.optimize == 0, 'refusing to run under Python optimization: gates must not be removable')
sys.dont_write_bytecode = True

import fcntl, json, os, stat, subprocess
from pathlib import Path

import framelib
from framelib import Dir, commit, commit_json, retain, now

INSTALL_ROOT = Path('/opt/wlscratch/frame-v6w1')
PYTHON = '/usr/bin/python3'
SUDO = '/usr/bin/sudo'
LEASE_DIR = '/var/lib/wlscratch/lease'
LEASE_FILE = 'writer.lock'
T_ROOT = '/var/lib/wlscratch/runs'
R_ROOT = '/var/lib/wlscratch/runs/records'
SETUP_IDENTITIES = '/opt/wlscratch/setup-identities.json'
W_ID = 950     # candidate (v11 §3.1; the lease check pins [dev,ino] from setup-identities, not this literal)

VERBS = ('adopt', 'materialize', 'dispatch', 'selftest', 'seal-front')

# v11 §5.2 — the complete set of (verb -> partition-root) write authorities. Any write to a parent
# not on this list, or an attempt to replace an existing object, is refused by authorize().
MUTATION_AUTHORITY = {
    'adopt':      {'roots': ('P_ado',), 'create_only': True},
    'materialize': {'roots': ('T_root', 'g', 'g_rec'), 'create_only': True},
    'dispatch':   {'roots': ('g_rec',), 'create_only': True},
    'selftest':   {'roots': ('selftest_T', 'selftest_R'), 'create_only': True},
    'seal-front': {'roots': ('g_rec_w2',), 'create_only': True},
}


# ---------------------------------------------------------------- §5.1 the writer lease ------------
def acquire_lease():
    """v11 §5.1 — `writer.lock`: creation checked, then flock, before ANY mutation; all through
    descriptors, no pathname re-resolution. Returns the held lease fd (kept open for W's whole life,
    O_CLOEXEC, never passed on). Refuses before any mutation (and before starting any helper S2/S_O)
    on EWOULDBLOCK or any other error, so while one writer holds the lease no other can start RL.

    No byte is written: flock needs no write access, the descriptor is read-only, and the file is
    root-owned 0440 — so the lease causes no frame mutation outside g (v11 §5.1 "No byte write")."""
    ids = _setup_identities()
    # 1. anchor the lease directory from '/', each ancestor's [dev,ino]/owner/mode == setup-identities
    lease = Dir.anchor(LEASE_DIR)
    _require_anchor_matches(lease, ids, LEASE_DIR)
    # 2. open writer.lock O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK; fstat + xattr identity
    fd = os.open(LEASE_FILE, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=lease.fd)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == 0
                and info.st_gid == W_ID and stat.S_IMODE(info.st_mode) == 0o440 and info.st_size == 0,
                'writer.lock is not root:W 0440 empty single-link regular file (v11 §5.1 check 2)')
        try:
            os.getxattr(fd, 'system.posix_acl_access')
            raise RuntimeError('writer.lock carries an access ACL (v11 §5.1: must be ENODATA)')
        except OSError as e:
            require(e.errno == 61, 'unexpected xattr errno on writer.lock: %d' % e.errno)  # ENODATA
        entry = os.stat(LEASE_FILE, dir_fd=lease.fd, follow_symlinks=False)
        require((entry.st_dev, entry.st_ino) == (info.st_dev, info.st_ino),
                'writer.lock entry does not name the opened inode')
        require([info.st_dev, info.st_ino] == ids['lease']['writer_lock_dev_ino'],
                'writer.lock [dev,ino] != setup-identities.json (v11 §5.1 check 2)')
        # 3. flock(LOCK_EX|LOCK_NB); EWOULDBLOCK or any error -> refuse before any mutation
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        os.close(fd)
        lease.close()
        raise
    # 4. descriptor stays open for life; the lease dir handle is kept so re-verification is possible
    return {'lease_dir': lease, 'lock_fd': fd}


def _require_anchor_matches(handle, ids, path):
    """Every ancestor of the anchored path has the [dev,ino]/owner/mode setup-identities pins
    (v11 §5.1 check 1 / §3.4). Detailed per-component comparison is the installed body; this names
    the contract. verify_location() already refuses a rename/substitution above the directory."""
    handle.verify_location()
    require(path in ids['anchors'], 'anchor not pinned in setup-identities.json: ' + path)


def _setup_identities():
    """Read /opt/wlscratch/setup-identities.json (root:root 0644, v11 §3.3, §11.5 S-H, §11.7). Its
    pinned fields (anchors, lease [dev,ino], N's account lines) are the ONLY identity source; W never
    trusts a numeric id from argv. Installed body does the stable read + schema pin; drafting names
    it."""
    raise NotImplementedError('installed body reads setup-identities.json (v11 §11.7) and returns its pins')


# ---------------------------------------------------------------- §5.2 mutation confinement --------
def authorize(verb, partition_root, parent_handle, name):
    """Gate EVERY write. Refuses unless (verb, partition_root) is in MUTATION_AUTHORITY, the parent
    handle is W-owned and inside T (verify_location passes and its on-disk owner is W or root per
    §3.4), and the name is create-only (does not already exist). This is the single auditable choke
    point for v11 §5.2 'Nothing else.' It performs NO privilege or namespace operation."""
    auth = MUTATION_AUTHORITY.get(verb)
    require(auth is not None and partition_root in auth['roots'],
            'write not authorized for verb %r into %r (v11 §5.2)' % (verb, partition_root))
    parent_handle.verify_location()
    require(not parent_handle.has(name), 'create-only violated: %r already exists (v11 §5.2)' % name)
    return True


def write_record(verb, partition_root, parent_handle, name, value, errors):
    """Authorized create-only commit of a record (v11 §5.2 + §10.1)."""
    authorize(verb, partition_root, parent_handle, name)
    return retain(parent_handle, name, value, errors)


# ---------------------------------------------------------------- RL handoff -----------------------
def invoke_rl(verb, rl_args):
    """Start RL through the RL sudoers rule (v11 §3.2 S2/S_O):
      sudo -n -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/sandbox_launch.py <verb> <args>
    W passes only the sealed argv grammar RL re-reads and re-checks itself (RL trusts nothing from
    W but the seals, v11 §12.2 step 2). W does NOT build any namespace; the view is RL's alone.
    DRAFTING: the argv is constructed, nothing is spawned here."""
    argv = [SUDO, '-n', '--', PYTHON, '-I', '-B', str(INSTALL_ROOT / 'sandbox_launch.py'), verb] + list(rl_args)
    # Descriptors handed to RL are exactly {0,1,2}: fd 0 a socket, fds 1-2 W-owned stream files in
    # P_att/w2-<k> (v11 §12.2 step 3). The installed body sets close_fds=True and wires those three.
    return argv   # subprocess.run(argv, ...) in the installed body; not executed in this copy


# ---------------------------------------------------------------- §5.3 W2 capability --------------
def verify_w2_capability(attempt_record, mode):
    """v11 §5.2 'W2's capability' / §9.7. W2 (seal-front) verifies BEFORE writing that it was started
    by the recorded front: it reads /proc/<W2 parent=S3>/stat and /proc/<S3 parent>/stat and requires
    (pid, start_time_ticks, boot_id) of the grandparent to equal attempt.json's front triple; in mode
    `recover` it also requires the attempt's writer triple absent or reused. A different sicarii
    process cannot satisfy that (the kernel assigns pids and start times). W2 reads only /proc stat
    of its OWN ancestor chain — never another process's mem/fd/root/cwd (T-W). Installed body does
    the triple comparison; drafting names the contract, keeping the no-foreign-/proc discipline."""
    raise NotImplementedError('installed body compares the front/writer (pid,start,boot) triples '
                              '(v11 §5.2 W2, §9.7); reads only its own ancestor /proc/<pid>/stat')


# ---------------------------------------------------------------- verbs ----------------------------
def main(argv):
    require(len(argv) >= 2 and argv[1] in VERBS, 'usage: writer.py (%s) …' % '|'.join(VERBS))
    verb = argv[1]
    lease = acquire_lease()            # v11 §5.1 — before ANY mutation and before any helper
    try:
        # Each verb runs the reviewed v5/v6 verb logic (adoption record §4.6, materialize/dispatch
        # journals/commits/admission, selftest sacrificial tree, seal-front/W2 §9.7) with EVERY
        # write routed through authorize()+commit so the §5.2 set is enforced here, and with every
        # launch delegated to RL via invoke_rl(). Those verb bodies are the base frame v6 scratch.py
        # semantics (cited in MANIFEST.json), re-homed onto T's anchors and the O_TMPFILE commit;
        # they are reviewed as the installed writer, not re-transcribed in this enforcement-core copy.
        raise NotImplementedError('installed verb bodies: v5/v6 logic re-homed onto T anchors + '
                                  'framelib.commit, launches via invoke_rl() (v11 §4-§10, §15.3)')
    finally:
        os.close(lease['lock_fd'])     # releases the flock; the lease dir handle is closed with it
        lease['lease_dir'].close()


if __name__ == '__main__':
    raise SystemExit('writer.py is FROZEN DRAFTING source for review; it is not run here')
    # main(sys.argv)   # the installed entrypoint, shown and deliberately unreachable in this copy
