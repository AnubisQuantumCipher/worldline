"""WORLDLINE Phase One — W-1 frame-v6w1 shared primitive library (DRAFTING source).

FROZEN, REVIEWABLE, UNINSTALLED. Author: Claude (Opus 4.8), DRAFTING implementer, not a
reviewer. This file establishes no premise, grants nothing and was EXECUTED NOWHERE.

Why this module exists (disclosed drafting-structure deviation). v11 §3.2 names exactly four
installed Python members (front.py, writer.py, sandbox_launch.py, launch_target.py). All four
reuse the same custody primitives, which v11 inherits verbatim from the base frame v6
`scratch.py` (sha256 2255d6e14967d62aa9ce4c2b93b986340dd6840df9b659f9252e522546884c84). To keep
the four members byte-reviewable and avoid four divergent copies of one reviewed primitive, the
reused primitives live here, as faithful transcriptions of the CITED base-frame functions. The
installed frame may inline these back into each member or keep this as a fifth reviewed member
of the same root-owned `/opt/wlscratch/frame-v6w1/` package (every member is root:root 0644, so
a sibling import under `python3 -I -B <member>` resolves from the script's own directory, which
`-I` does not strip). This module adds no authority and no new mutation path; it only hosts code
the base frame already carries. SELFCHECK.md records the deviation; MANIFEST.json pins it.

Each public symbol below names the base-frame function it transcribes, by scratch.py line, so a
reviewer can diff byte-for-byte. Nothing here is modified from the base-frame semantics except
that `commit()` is NEW W-1 code (v11 §10.1: O_TMPFILE + create-only linkat), kept here beside
the create-only write it supersedes so both forms are reviewable together.
"""
import sys


def require(condition, message):
    """Non-removable gate (scratch.py:46-49). Unaffected by python -O; the members also refuse
    to run under optimization (scratch.py:52)."""
    if not condition:
        raise RuntimeError(message)


require(sys.flags.optimize == 0, 'refusing to run under Python optimization: gates must not be removable')
sys.dont_write_bytecode = True

import contextlib, datetime, hashlib, json, os, re, stat, uuid
from pathlib import Path

# ---- names / regexes carried verbatim from scratch.py:91-95 -------------------------------------
NAME_RE = r'[a-z0-9][a-z0-9-]{0,40}'
STAMP_RE = r'[0-9]{8}t[0-9]{6}-[0-9a-f]{8}'
UNIT_RE = r'[a-z][a-z0-9_]*(?:-[a-z0-9_]+)*\.ad[bs]'
COMPONENT_RE = r'[A-Za-z0-9_.][A-Za-z0-9_.-]*'   # names the frame CREATES; '.' and '..' refused separately
SHA_RE = r'[0-9a-f]{64}'
GEN_RE = r'[0-9a-f]{32}'

# scratch.py:96-97 (engineering-only label). W-1 is a CONTAINMENT frame, not an engineering run;
# the label is carried so retained records keep the original non-acceptance meaning verbatim.
LABEL = ('ENGINEERING_ONLY: scratch result on a throwaway copy; never proof, review, admission, ordinary, '
         'source-qualification or Phase One acceptance evidence. Original guarantees OPEN_UNCHANGED.')

# scratch.py:104-105 — the open discipline (O_CLOEXEC|O_NOFOLLOW everywhere; O_NONBLOCK so a
# substituted FIFO cannot stall; O_DIRECTORY for every anchor step).
O_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
O_FILE = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def stamp_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dt%H%M%S') + '-' + uuid.uuid4().hex[:8]


def created_name(name):          # scratch.py:126-129
    require(isinstance(name, str) and re.fullmatch(COMPONENT_RE, name) is not None and name not in ('.', '..'),
            'created path component: ' + repr(name))
    return name


def existing_name(name):         # scratch.py:132-135
    require(isinstance(name, str) and name not in ('', '.', '..') and '/' not in name and '\0' not in name,
            'path component: ' + repr(name))
    return name


def stat_key(info):              # scratch.py:138-141 — complete descriptor metadata minus atime
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_uid, info.st_gid, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


class Dir:
    """Anchored directory with custody (scratch.py:144-357, class Dir). Reached from `/` one
    component at a time, each step O_DIRECTORY|O_NOFOLLOW relative to the previous descriptor;
    `chain` holds [name, st_dev, st_ino] of every directory on the path; verify_location() re-walks
    it (scratch.py:174-190). Transcribed faithfully; see scratch.py for the V4-B01/B04 proofs."""

    def __init__(self, path, fd, chain):
        self.path, self.fd, self.chain = Path(path), fd, chain

    @classmethod
    def anchor(cls, path):                                   # scratch.py:155-172
        path = Path(path)
        require(path.is_absolute(), 'anchored path must be absolute: ' + str(path))
        fd = os.open('/', O_DIR)
        try:
            info = os.fstat(fd)
            chain = [['/', info.st_dev, info.st_ino]]
            for part in path.parts[1:]:
                nxt = os.open(existing_name(part), O_DIR, dir_fd=fd)
                os.close(fd)
                fd = nxt
                info = os.fstat(fd)
                chain.append([part, info.st_dev, info.st_ino])
        except BaseException:
            os.close(fd)
            raise
        return cls(path, fd, chain)

    def verify_location(self):                               # scratch.py:174-190
        fd = os.open('/', O_DIR)
        try:
            info = os.fstat(fd)
            require([info.st_dev, info.st_ino] == self.chain[0][1:], 'root directory identity changed')
            for name, dev, ino in self.chain[1:]:
                nxt = os.open(name, O_DIR, dir_fd=fd)
                os.close(fd)
                fd = nxt
                info = os.fstat(fd)
                require([info.st_dev, info.st_ino] == [dev, ino],
                        'directory is no longer at its anchored location: ' + str(self.path))
        finally:
            os.close(fd)
        held = os.fstat(self.fd)
        require([held.st_dev, held.st_ino] == self.chain[-1][1:],
                'held descriptor is not the anchored directory: ' + str(self.path))

    def child(self, name, create=False):                     # scratch.py:192-223
        if create:
            created_name(name)
            self.verify_location()
            os.mkdir(name, 0o700, dir_fd=self.fd)
            os.fsync(self.fd)
        fd = os.open(existing_name(name), O_DIR, dir_fd=self.fd)
        try:
            info = os.fstat(fd)
            entry = os.stat(name, dir_fd=self.fd, follow_symlinks=False)
            require((entry.st_dev, entry.st_ino) == (info.st_dev, info.st_ino) and stat.S_ISDIR(entry.st_mode),
                    'entry does not name the opened directory: ' + str(self.path / name))
            if create:
                require(info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700 and info.st_nlink == 2
                        and info.st_dev == self.chain[-1][1] and not os.listdir(fd)
                        and [info.st_dev, info.st_ino] not in [row[1:] for row in self.chain],
                        'created directory failed authentication: ' + str(self.path / name))
        except BaseException:
            os.close(fd)
            raise
        handle = Dir(self.path / name, fd, self.chain + [[name, info.st_dev, info.st_ino]])
        if create:
            try:
                handle.verify_location()
            except BaseException:
                handle.close()
                raise
        return handle

    def has(self, name):                                     # scratch.py:239-244
        try:
            os.stat(existing_name(name), dir_fd=self.fd, follow_symlinks=False)
            return True
        except FileNotFoundError:
            return False

    def read_observed(self, name):                           # scratch.py:246-268 (V4-B04 stable read)
        fd = os.open(existing_name(name), O_FILE, dir_fd=self.fd)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                    'not a single-link regular file: ' + str(self.path / name))
            chunks = []
            while True:
                chunk = os.read(fd, 1 << 20)
                if not chunk:
                    break
                chunks.append(chunk)
            after = os.fstat(fd)
            entry = os.stat(name, dir_fd=self.fd, follow_symlinks=False)
            data = b''.join(chunks)
            require(stat_key(before) == stat_key(after) == stat_key(entry) and len(data) == after.st_size,
                    'changed, aliased or renamed during read: ' + str(self.path / name))
            return data, after
        finally:
            os.close(fd)

    def read_regular(self, name):                            # scratch.py:270-272
        data, info = self.read_observed(name)
        return data, stat.S_IMODE(info.st_mode)

    def read_bytes(self, name):                              # scratch.py:301-302
        return self.read_regular(name)[0]

    def ident(self, name):                                   # scratch.py:304-306
        data, mode = self.read_regular(name)
        return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'mode': mode}

    def identity(self):                                      # scratch.py:347-349
        info = os.fstat(self.fd)
        return [info.st_dev, info.st_ino]

    def sync(self):
        os.fsync(self.fd)

    def close(self):                                         # scratch.py:354-357
        if self.fd is not None:
            fd, self.fd = self.fd, None
            os.close(fd)


# ---------------------------------------------------------------- create-only commit -------------
def verify_location_pair(handle, name, written_stat, data_len):
    """The post-write entry/location join of scratch.py:318-321, factored for reuse by commit()."""
    entry = os.stat(name, dir_fd=handle.fd, follow_symlinks=False)
    require((entry.st_dev, entry.st_ino) == (written_stat.st_dev, written_stat.st_ino)
            and entry.st_nlink == 1 and entry.st_size == data_len,
            'written file entry changed: ' + str(handle.path / name))
    handle.verify_location()


def commit(handle, name, data, mode=0o600, acl_bytes=None):
    """NEW W-1 commit primitive (v11 §10.1, steps 1-4; the export variant adds the ACL per §15.3).

    Supersedes the base frame's create-only O_CREAT|O_EXCL write (scratch.py:308-322) with the
    nameless O_TMPFILE form v11 requires, so that a record acquires a name ONLY after its bytes are
    complete, synced and validated (the commit-point property of v11 §10.1):

      1. openat(dir,'.',O_TMPFILE|O_RDWR|O_CLOEXEC,0600); write loop (continues after a short
         write); fchmod 0600; fsync.  (Export copies: fchmod to the final mode and fsetxattr the
         ACL here, v11 §15.3 step 2, before validation.)
      2. validation on the HELD descriptor, before any name exists: pread every byte back and
         require equal sha256 and size; fstat shows a regular file with st_nlink==0, owner this
         user, mode 0600 (or the final export mode); fgetxattr system.posix_acl_access is ENODATA
         unless an export ACL was just set.
      3. create-only link: linkat('/proc/self/fd/<n>', dir, name, AT_SYMLINK_FOLLOW); EEXIST never
         replaces; after any error re-observe the name and treat it as linked iff it names the held
         inode (a kernel may report an error after adding the entry — v11 §10.1 step 3).
      4. fsync the directory; post-link join (name names the held inode, st_nlink==1);
         verify_location().

    This function performs NO privilege change, NO namespace call and NO boundary operation; it is
    pure create-only record custody, as in the base frame. verify_location() brackets it."""
    handle.verify_location()
    digest = hashlib.sha256(data).hexdigest()
    fd = os.open('.', os.O_TMPFILE | os.O_RDWR | os.O_CLOEXEC, 0o600, dir_fd=handle.fd)
    try:
        off = 0
        while off < len(data):
            off += os.write(fd, data[off:])              # continue after a short write (v11 §10.1 step 1)
        os.fchmod(fd, mode if acl_bytes is None else mode)
        if acl_bytes is not None:
            os.setxattr(fd, 'system.posix_acl_access', acl_bytes)   # export ACL, before validation (§15.3)
        os.fsync(fd)
        # step 2 — validate on the held descriptor, before any name exists
        back = b''
        while True:
            chunk = os.pread(fd, 1 << 20, len(back))
            if not chunk:
                break
            back += chunk
        info = os.fstat(fd)
        require(hashlib.sha256(back).hexdigest() == digest and len(back) == len(data) == info.st_size
                and stat.S_ISREG(info.st_mode) and info.st_nlink == 0 and info.st_uid == os.getuid()
                and stat.S_IMODE(info.st_mode) == stat.S_IMODE(mode),
                'O_TMPFILE validation failed before link: ' + name)
        if acl_bytes is None:
            with contextlib.suppress(OSError):
                require(False, 'unexpected ACL on a non-export record: ' + name) \
                    if os.getxattr(fd, 'system.posix_acl_access') is not None else None
        # step 3 — create-only link of the already-complete inode
        try:
            os.link('/proc/self/fd/%d' % fd, created_name(name), dst_dir_fd=handle.fd,
                    follow_symlinks=True)
        except OSError:
            entry = os.stat(name, dir_fd=handle.fd, follow_symlinks=False)
            require((entry.st_dev, entry.st_ino) == (info.st_dev, info.st_ino),
                    'link reported an error and the name does not name the held inode: ' + name)
        # step 4 — directory fsync, post-link join, location
        os.fsync(handle.fd)
        entry = os.stat(name, dir_fd=handle.fd, follow_symlinks=False)
        require((entry.st_dev, entry.st_ino) == (info.st_dev, info.st_ino) and entry.st_nlink == 1,
                'post-link join failed: ' + name)
        handle.verify_location()
    finally:
        os.close(fd)
    return {'path': str(handle.path / name), 'sha256': digest, 'bytes': len(data),
            'mode': stat.S_IMODE(mode), 'acl_sha256': (hashlib.sha256(acl_bytes).hexdigest()
                                                       if acl_bytes is not None else None)}


def commit_json(handle, name, value, mode=0o600):
    if isinstance(value, dict) and 'label' not in value:
        value = {**value, 'label': LABEL}
    return commit(handle, name, (json.dumps(value, indent=2, sort_keys=True, default=str) + '\n').encode(), mode)


# ---------------------------------------------------------------- retention that never raises ----
def failure_row(stage, caught):                              # scratch.py:377-378
    return {'stage': stage, 'type': type(caught).__name__, 'message': str(caught)}


def last_resort(value):                                      # scratch.py:381-384
    with contextlib.suppress(BaseException):
        os.write(2, (json.dumps(value, sort_keys=True, default=str) + '\n').encode())


def retain(handle, name, value, errors, downgrade=None):     # scratch.py:387-406 (over commit_json)
    try:
        return commit_json(handle, name, value)
    except BaseException as caught:
        errors.append(failure_row('record ' + name, caught))
    if downgrade is not None:
        with contextlib.suppress(BaseException):
            downgrade(value)
    retry = name + '.retry-' + uuid.uuid4().hex[:12]
    try:
        return commit_json(handle, retry, {**value, 'record_errors': list(errors)})
    except BaseException as caught:
        errors.append(failure_row('record ' + retry, caught))
    last_resort({'unretained_record': name, 'value': value, 'record_errors': errors, 'label': LABEL})
    return None


def guarded(errors, stage, action, *args):                   # scratch.py:409-415
    try:
        return action(*args)
    except BaseException as caught:
        errors.append(failure_row(stage, caught))
        return None


def read_record(handle, name, errors):                       # scratch.py:418- (never trusts bytes)
    try:
        if not handle.has(name):
            return None, None
        data, _ = handle.read_observed(name)
    except BaseException as caught:
        return None, {'name': name, 'raw_error': failure_row('read ' + name, caught)}
    try:
        return json.loads(data), None
    except BaseException as caught:
        return None, {'name': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                      'raw_error': failure_row('parse ' + name, caught)}
