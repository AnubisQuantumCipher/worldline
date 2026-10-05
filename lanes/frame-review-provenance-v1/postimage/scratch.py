"""WORLDLINE Phase One engineering scratch frame v5 (Claude lead).

Engineering-only focused gprbuild/gnatprove runs on THROWAWAY copies of the reviewed commonV4 source plus
Ada-unit overlays under core/. Results are ENGINEERING_ONLY: never proof, review, admission, ordinary,
source-qualification or Phase One acceptance evidence.

History: v1-v4 were reviewed by actual different-author gpt-6.1-sol and left UNQUALIFIED (v1 B01-B09; v2
V2-B01..B08; v3 V3-B01..B06; v4 V4-B01..B04); all are preserved unchanged. v5 keeps v4's reduced surface (no late
collection, no standing verify, the dispatch verb, verified-byte module execution) and closes the v4 findings:
- directory custody (V4-B01): every held directory carries the chain of directory identities it was anchored
  through and is re-verified against that chain before and after every mutation through it; a created directory
  is authenticated (its entry names the opened inode; owner, mode 0700, link count 2, same device, empty, not an
  ancestor) before any chmod or write; the source and snapshot directories are opened once per process and the
  same descriptors are verified, sealed, re-verified immediately before the spawn and passed to fchdir; the
  identity of every source-tree directory is recorded at materialization, sealed at launch, required equal in the
  child immediately before the spawn and compared at conclusion;
- exceptional retention (V4-B02): every actual wait is recorded first, by a create-only writer that never raises
  and retries under a fresh name; stream closes, parsing and post-identity collection are individually guarded and
  their errors aggregated into the terminal record; partial records stay raw and are reported, never parsed as
  valid input; an unparseable participant record leaves the participant unresolved and the window reserved;
- launch seal (V4-B03): the launcher argv carries the sha256 of launch.json and of admission.json, the child
  authenticates both and its own command line by them, and conclusion uses the parent's in-memory launch record
  and directory seal and reports drift of every retained launch-gate record;
- stable reads (V4-B04): complete descriptor metadata is compared before and after every read and against the
  named entry afterwards, for recorded and excluded generated files alike, and every walked directory is
  re-reached with unchanged metadata after the walk.
FRAME.md maps every v4 finding and note to its mechanism and states the residual limits.

Operator decision (claude-lead-v2/approvals/scratch-frame-decision-v1): no prover launch outside a reviewed
and adopted frame; existing caps, shared-window ownership, no-sibling controls, source/tool identities,
storage checks and raw logs preserved; results engineering-only.

Usage (always invoke as /usr/bin/python3 -B <absolute frame>/scratch.py ...):
  scratch.py freeze
  scratch.py adopt EVENTS_JSONL EXEC_ARGV_JSON
  scratch.py materialize NAME OVERLAY_DIR
  scratch.py dispatch NAME ACTION [ARG ...]   (lead entry point; prints its dispatch directory and forwards
                                               lead-written answer-N.json lines to the run's stdin)
  scratch.py run NAME ACTION [ARG ...]        (refuses unless started by `dispatch` with the same arguments)
  scratch.py child RUN_NAME ATTEMPT_STAMP LAUNCH_SHA256 ADMISSION_SHA256
                                              (inside the owned scope only; repeats the full admission)
"""
import sys


def require(condition, message):
    """Non-removable gate (unaffected by python -O)."""
    if not condition:
        raise RuntimeError(message)


require(sys.flags.optimize == 0, 'refusing to run under Python optimization: gates must not be removable')
sys.dont_write_bytecode = True

from pathlib import Path
import contextlib, datetime, fcntl, glob, hashlib, json, os, re, resource, select, signal, stat, subprocess
import time, traceback, types, uuid

FRAME = Path(__file__).resolve().parent
W = Path('/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow')
RUNS = W / 'work/claude-scratch-runs-v5'
BASE = W / 'work/reviewed-common-proof-source-composition-v4'
BASE_BINDING_SHA256 = '719cdda909c100515ac2434c53d8a2d27df138eec237fd13cda3f10142ea72ed'
BASE_INVENTORY_SHA256 = '943ea95ec98bd770ae9dd22ff1ea85bbf932db3192f6ba07f120284c1122e3bf'
BASE_DIRMODES_SHA256 = '1049c8313a09368d1a2ffa1f18300477390a27c9d642b3b3d7914493ce50dbde'
LEAD_MODULE = W / 'work/claude-lead-v2/claude_lead.py'
LEAD_MODULE_SHA256 = '774656a243d604a922a746e65ee74603d7a4797cf3d7f0c8f2caff542dc80713'
WINDOW = Path('/home/sicarii/Documents/Codex/2026-09-30/how-do-u-feel-about-the/work/worldline-build-proof-window.json')
STORAGE = '/home/sicarii/.codex/skills/project-vault/scripts/storage_status.py'
F10K_SOURCE = str(W / 'work/full-formal-diagnostic-v10k-retry1/source')
REVIEW = FRAME / 'review/gpt61-v1'
ADOPTION = FRAME / 'review/lead-adoption.json'
INVENTORY = FRAME / 'frame-inventory.json'
GNAT = Path('/home/sicarii/opt/gnat')
GNATPROVE = str(GNAT / 'gnatprove-aarch64-linux-16.1.0-1/bin/gnatprove')
GPRBUILD = str(GNAT / 'gprbuild-aarch64-linux-26.0.0-1/bin/gprbuild')
PYTHON = '/usr/bin/python3'
STRICT_TAIL = ['--mode=all', '--level=3', '--report=all', '--checks-as-errors=on', '--proof-warnings=on', '-j2']
OUTPUT_PARTITIONS = ('obj/', 'lib/', 'resource-tests/obj/', 'resource-tests/bin/')
HEAVY = ('gprbuild', 'gcc', 'gnat1', 'gnatprove', 'gnat2why', 'gnatwhy3', 'why3server', 'z3', 'cvc5', 'alt-ergo')
MIN_MEM_AVAILABLE_KB = 16777217
MAX_CHALLENGES = 3
RECEIPT_WAIT_SECONDS = 300
RECEIPT_READ_SECONDS = 30
OBSERVATION_TIMEOUT_SECONDS = 30
KEEP_ENVIRONMENT = ('HOME', 'USER', 'LOGNAME', 'LANG')
SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
ACTIONS = ('prove-all-k', 'prove-all', 'prove-file', 'prove-subp', 'compile-all')
FRAME_REVIEW_ROSTER = {'REVIEW.md', 'review.json', 'checks.json', 'bound-inputs.json', 'tool-topology.json'}
# D-LEAD-REVIEW-PROVENANCE (W-1 §23.4, NEW): a Claude-subagent review freeze seals exactly these three files
# (no bound-inputs/tool-topology sidecars). SOURCE-ONLY, UNINSTALLED; adoption BLOCKED until this change is reviewed.
CLAUDE_REVIEW_ROSTER = {'REVIEW.md', 'review.json', 'checks.json'}
INVENTORY_MODULES =('tool_inventory', 'proof_elf_inventory', 'proof_data_inventory', 'runtime_inventory')
NAME_RE = r'[a-z0-9][a-z0-9-]{0,40}'
STAMP_RE = r'[0-9]{8}t[0-9]{6}-[0-9a-f]{8}'
UNIT_RE = r'[a-z][a-z0-9_]*(?:-[a-z0-9_]+)*\.ad[bs]'
COMPONENT_RE = r'[A-Za-z0-9_.][A-Za-z0-9_.-]*'   # names this frame CREATES; '.' and '..' refused separately
SHA_RE = r'[0-9a-f]{64}'
LABEL = ('ENGINEERING_ONLY: scratch result on a throwaway copy; never proof, review, admission, ordinary, '
         'source-qualification or Phase One acceptance evidence. Original guarantees OPEN_UNCHANGED.')
# D-LEAD-REVIEW-PROVENANCE (W-1 §23.5 item 13): the compiled profile no longer fixes a single model.
# `actual_model_selection` is accepted per form, selected by `reviewer_kind` in review_profile_problems():
# 'gpt-6.1-sol' for a GPT-6.1 review, the sealed Claude model string for a claude-subagent review. Every
# other profile key (schema, different_from_author, author, disposition, the five acceptance Falses) is UNCHANGED.
REVIEW_PROFILE = {'schema': 'claude-scratch-frame-review-v5', 'different_from_author': True,
                  'author': 'Claude Code lead claude-opus-5-5',
                  'disposition': 'QUALIFIED_ENGINEERING_SCRATCH_FRAME', 'blocking_findings': [],
                  'execution_authority': 'NONE_FRESH_LEAD_ADOPTION_AND_ORIGINAL_GATES_REQUIRED',
                  'scratch_results_as_evidence': False, 'proof_acceptance': False, 'phase_acceptance': False,
                  'source_acceptance': False, 'target_execution': False}
O_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
O_FILE = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK   # NONBLOCK: a substituted FIFO cannot stall


class Interrupted(Exception):
    pass


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def parse_time(text):
    return datetime.datetime.fromisoformat(text.replace('Z', '+00:00'))


def stamp_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dt%H%M%S') + '-' + uuid.uuid4().hex[:8]


# ---------------------------------------------------------------- anchored filesystem with custody (V4-B01, V4-B04)

def created_name(name):
    require(isinstance(name, str) and re.fullmatch(COMPONENT_RE, name) is not None and name not in ('.', '..'),
            'created path component: ' + repr(name))
    return name


def existing_name(name):
    require(isinstance(name, str) and name not in ('', '.', '..') and '/' not in name and '\0' not in name,
            'path component: ' + repr(name))
    return name


def stat_key(info):
    """Complete descriptor metadata compared across one observation (the access time is excluded: reads change it)."""
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_uid, info.st_gid, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


class Dir:
    """A directory reached from / one component at a time, each step opened O_DIRECTORY|O_NOFOLLOW relative to
    the previous descriptor. Every later read, write, walk and identity is relative to the held descriptor, so no
    pathname is re-resolved. `chain` holds [name, st_dev, st_ino] of every directory on the anchored path;
    verify_location() re-walks it and refuses unless the held descriptor is still exactly that directory at that
    place (no rename-away, detachment, ordinary-directory substitution or alias anywhere above it). Every mutation
    through a handle is bracketed by verify_location() (V4-B01). `path` is documentation only."""

    def __init__(self, path, fd, chain):
        self.path, self.fd, self.chain = Path(path), fd, chain

    @classmethod
    def anchor(cls, path):
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

    def verify_location(self):
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

    def child(self, name, create=False):
        """A handle on directory `name` below this one, whose entry must name the opened inode. With create=True the
        directory is made here (mkdir fails if the name exists) and authenticated before any chmod or write: owned
        by this user, mode 0700 (umask 077), link count 2, on this directory's device, empty, and not an ancestor;
        its new location is then verified."""
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

    def descend(self, relative, create=False):
        """A new handle for `relative` below this directory (Path('.') gives a duplicate with the same chain); the
        caller closes it."""
        current = Dir(self.path, os.dup(self.fd), [list(row) for row in self.chain])
        try:
            for part in Path(relative).parts:
                nxt = current.child(part, create=create and not current.has(part))
                current.close()
                current = nxt
        except BaseException:
            current.close()
            raise
        return current

    def has(self, name):
        try:
            os.stat(existing_name(name), dir_fd=self.fd, follow_symlinks=False)
            return True
        except FileNotFoundError:
            return False

    def read_observed(self, name):
        """(bytes, final fstat) of a single-link regular file opened without following aliases. Complete descriptor
        metadata must be identical before and after the read, the named entry must still name the opened inode with
        that same metadata afterwards, and the byte count must equal the size (V4-B04)."""
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

    def read_regular(self, name):
        data, info = self.read_observed(name)
        return data, stat.S_IMODE(info.st_mode)

    def read_prefix(self, name, size):
        """The first `size` bytes of an append-only single-link regular file (the live lead transcript): identity,
        type, mode, owner and link count unchanged across the read, the file never shorter than `size`, and the
        named entry still naming the opened inode afterwards. Growth past the prefix is allowed; the caller verifies
        the prefix hash."""
        fd = os.open(existing_name(name), O_FILE, dir_fd=self.fd)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size >= size,
                    'not a single-link regular file of at least the observed size: ' + str(self.path / name))
            chunks, offset = [], 0
            while offset < size:
                chunk = os.pread(fd, min(1 << 20, size - offset), offset)
                require(bool(chunk), 'append-only file shrank during read: ' + str(self.path / name))
                chunks.append(chunk)
                offset += len(chunk)
            after = os.fstat(fd)
            entry = os.stat(name, dir_fd=self.fd, follow_symlinks=False)

            def fixed(info):
                return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_uid, info.st_gid)
            require(fixed(before) == fixed(after) == fixed(entry) and after.st_size >= size,
                    'append-only file replaced, aliased or truncated during read: ' + str(self.path / name))
            return b''.join(chunks)
        finally:
            os.close(fd)

    def read_bytes(self, name):
        return self.read_regular(name)[0]

    def ident(self, name):
        data, mode = self.read_regular(name)
        return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'mode': mode}

    def write_bytes(self, name, data, mode=0o600):
        """Create-only (O_EXCL, no alias) file in this verified directory; after the file and the directory are
        synced the entry must name the written single-link inode and the location is verified again."""
        self.verify_location()
        fd = os.open(created_name(name), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600,
                     dir_fd=self.fd)
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data); handle.flush(); os.fchmod(handle.fileno(), mode); os.fsync(handle.fileno())
            written = os.fstat(handle.fileno())
        os.fsync(self.fd)
        entry = os.stat(name, dir_fd=self.fd, follow_symlinks=False)
        require((entry.st_dev, entry.st_ino) == (written.st_dev, written.st_ino) and entry.st_nlink == 1
                and entry.st_size == len(data), 'written file entry changed: ' + str(self.path / name))
        self.verify_location()
        return {'path': str(self.path / name), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'mode': mode}

    def write_json(self, name, value):
        if isinstance(value, dict) and 'label' not in value:
            value = {**value, 'label': LABEL}
        return self.write_bytes(name, (json.dumps(value, indent=2, sort_keys=True, default=str) + '\n').encode())

    def open_stream(self, name):
        self.verify_location()
        fd = os.open(created_name(name), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600,
                     dir_fd=self.fd)
        try:
            os.fsync(self.fd)
            self.verify_location()
        except BaseException:
            os.close(fd)
            raise
        return fd

    def set_mode(self, mode):
        self.verify_location()
        os.fchmod(self.fd, mode)
        os.fsync(self.fd)
        self.verify_location()

    def identity(self):
        info = os.fstat(self.fd)
        return [info.st_dev, info.st_ino]

    def sync(self):
        os.fsync(self.fd)

    def close(self):
        if self.fd is not None:
            fd, self.fd = self.fd, None
            os.close(fd)


def close_stream(fd):
    """fsync then close; both are attempted and the first failure is raised after both ran."""
    failure = None
    try:
        os.fsync(fd)
    except BaseException as caught:
        failure = caught
    try:
        os.close(fd)
    except BaseException as caught:
        failure = failure or caught
    if failure is not None:
        raise failure


# ---------------------------------------------------------------- record retention that never raises (V4-B02)

def failure_row(stage, caught):
    return {'stage': stage, 'type': type(caught).__name__, 'message': str(caught)}


def last_resort(value):
    """When no record could be committed the facts still go to this process's own retained stderr stream."""
    with contextlib.suppress(BaseException):
        os.write(2, (json.dumps(value, sort_keys=True, default=str) + '\n').encode())


def retain(handle, name, value, errors, downgrade=None):
    """Create-only JSON record that never raises: the primary name first, then one uniquely named retry in the same
    directory, then stderr. Every failure is appended to `errors`. When the primary commit fails, `downgrade` (if
    given) is applied before the retry so a retried record never claims what the failed commit could not
    establish. A partially written primary is left in place as raw evidence; it is never reused or parsed as the
    record. Returns the pin of the committed record or None."""
    try:
        return handle.write_json(name, value)
    except BaseException as caught:
        errors.append(failure_row('record ' + name, caught))
    if downgrade is not None:
        with contextlib.suppress(BaseException):
            downgrade(value)
    retry = name + '.retry-' + uuid.uuid4().hex[:12]
    try:
        return handle.write_json(retry, {**value, 'record_errors': list(errors)})
    except BaseException as caught:
        errors.append(failure_row('record ' + retry, caught))
    last_resort({'unretained_record': name, 'value': value, 'record_errors': errors, 'label': LABEL})
    return None


def guarded(errors, stage, action, *args):
    """One cleanup or observation step whose failure is aggregated into `errors`, never raised."""
    try:
        return action(*args)
    except BaseException as caught:
        errors.append(failure_row(stage, caught))
        return None


def read_record(handle, name, errors):
    """A retained JSON record read without trusting it: (value, raw row). A missing record gives (None, None).
    Unreadable or unparseable bytes give (None, row with the raw identity and the error): they stay retained raw and
    are never parsed as valid input."""
    try:
        if not handle.has(name):
            return None, None
        data, mode = handle.read_regular(name)
    except BaseException as caught:
        errors.append(failure_row('read ' + name, caught))
        return None, {'name': name, 'unreadable': True, 'error': failure_row('read ' + name, caught)}
    row = {'name': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'mode': mode}
    try:
        value = json.loads(data)
        require(isinstance(value, dict), 'record is not a JSON object')
        return value, row
    except BaseException as caught:
        errors.append(failure_row('parse ' + name, caught))
        return None, {**row, 'unparseable': True, 'error': failure_row('parse ' + name, caught)}


def pinned(path):
    """One anchored read of an absolute path: (bytes, pin) computed from the same bytes."""
    path = Path(path)
    parent = Dir.anchor(path.parent)
    try:
        data, mode = parent.read_regular(existing_name(path.name))
    finally:
        parent.close()
    return data, {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'mode': mode}


def pin(path):
    return pinned(path)[1]


def bare(path):
    row = pin(path)
    return {k: row[k] for k in ('sha256', 'bytes', 'mode')}


def sha(path):
    return pin(path)['sha256']


def read_path(path):
    return pinned(path)[0]


def load_json(path):
    return json.loads(read_path(path))


def sha_many(paths):
    """Anchored identities of many absolute files, one anchored parent per directory."""
    cache, out = {}, {}
    try:
        for text in paths:
            path = Path(text)
            if path.parent not in cache:
                cache[path.parent] = Dir.anchor(path.parent)
            out[text] = cache[path.parent].ident(existing_name(path.name))['sha256']
    finally:
        for handle in cache.values():
            handle.close()
    return out


def in_partition(relative):
    """True for a generated output directory (or anything below one) of the fixed build graph."""
    return relative not in ('', '.') and (relative + '/').startswith(OUTPUT_PARTITIONS)


def tree_content(tree):
    return {'files': tree['files'], 'directories': tree['directories']}


def observe_tree(handle, exclude_partitions, skip_top=()):
    """Files (sha256/bytes/mode), directory modes and the [st_dev, st_ino] of every directory below an anchored
    directory, walked by a descriptor stack. Refuses aliases, special files, multiply linked files, unreadable
    entries, any entry replaced between its lstat and its O_NOFOLLOW open, and any file whose complete metadata
    changed during its observation or whose name no longer names it afterwards - recorded files and excluded
    generated files alike (V4-B04). Every directory must keep its complete metadata across its own listing and must
    be re-reached by the same names with unchanged metadata after the whole walk, so no entry was renamed, added or
    removed after its check. Files directly inside generated output partitions are, when excluded, checked but not
    recorded, and partition directory modes are not recorded; partition directory identities are."""
    files, directories, identities, walked = {}, {}, {}, []
    stack = [('', os.dup(handle.fd))]
    try:
        while stack:
            relative, fd = stack.pop()
            try:
                info = os.fstat(fd)
                require(stat.S_ISDIR(info.st_mode), 'not a directory in tree: ' + (relative or '.'))
                identities[relative or '.'] = [info.st_dev, info.st_ino]
                walked.append((relative, stat_key(info)))
                partition = exclude_partitions and in_partition(relative)
                if not partition:
                    directories[relative or '.'] = stat.S_IMODE(info.st_mode)
                for name in sorted(os.listdir(fd)):
                    existing_name(name)
                    if relative == '' and name in skip_top:
                        continue
                    path = relative + '/' + name if relative else name
                    entry = os.stat(name, dir_fd=fd, follow_symlinks=False)
                    if stat.S_ISDIR(entry.st_mode):
                        sub = os.open(name, O_DIR, dir_fd=fd)
                        sub_info = os.fstat(sub)
                        if (sub_info.st_dev, sub_info.st_ino) != (entry.st_dev, entry.st_ino):
                            os.close(sub)
                            raise RuntimeError('directory replaced during walk: ' + path)
                        stack.append((path, sub))
                    elif stat.S_ISREG(entry.st_mode):
                        require(entry.st_nlink == 1, 'multiply linked file in tree: ' + path)
                        file_fd = os.open(name, O_FILE, dir_fd=fd)
                        try:
                            first = os.fstat(file_fd)
                            require(stat_key(first) == stat_key(entry) and stat.S_ISREG(first.st_mode) and first.st_nlink == 1,
                                    'file replaced during walk: ' + path)
                            digest, size = hashlib.sha256(), 0
                            if not partition:
                                while True:
                                    chunk = os.read(file_fd, 1 << 20)
                                    if not chunk:
                                        break
                                    digest.update(chunk)
                                    size += len(chunk)
                            last = os.fstat(file_fd)
                            final = os.stat(name, dir_fd=fd, follow_symlinks=False)
                            require(stat_key(last) == stat_key(first) == stat_key(final) and (partition or size == last.st_size),
                                    'file changed, aliased or renamed during walk: ' + path)
                            if not partition:
                                files[path] = {'sha256': digest.hexdigest(), 'bytes': size, 'mode': stat.S_IMODE(last.st_mode)}
                        finally:
                            os.close(file_fd)
                    else:
                        raise RuntimeError('alias or special file in tree: ' + path)
                require(stat_key(os.fstat(fd)) == stat_key(info), 'directory changed during walk: ' + (relative or '.'))
            finally:
                os.close(fd)
    finally:
        for _relative, fd in stack:
            os.close(fd)
    for relative, recorded in walked:
        again = handle.descend(relative or '.')
        try:
            require(stat_key(os.fstat(again.fd)) == recorded, 'directory changed after its walk: ' + (relative or '.'))
        finally:
            again.close()
    return {'files': files, 'directories': directories, 'identities': identities}


def read_files(handle, tree):
    """Bytes of every observed file, each re-read by descriptor and required to equal its observed identity."""
    data = {}
    for relative, row in sorted(tree['files'].items()):
        parent = handle.descend(Path(relative).parent.as_posix())
        try:
            content, mode = parent.read_regular(Path(relative).name)
        finally:
            parent.close()
        require({'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content), 'mode': mode} == row,
                'file changed after observation: ' + relative)
        data[relative] = content
    return data


# ---------------------------------------------------------------- verified execution of code (no path import)

def exec_verified(name, path, expected_sha):
    """Execute a module from bytes whose hash was verified in the same read; never a path import."""
    if name in sys.modules:
        module = sys.modules[name]
        require(getattr(module, '__verified_sha256__', None) == expected_sha, 'module already present with other bytes: ' + name)
        return module
    data = read_path(path)
    require(hashlib.sha256(data).hexdigest() == expected_sha, 'module identity: ' + str(path))
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__verified_sha256__ = expected_sha
    sys.modules[name] = module
    try:
        exec(compile(data, str(path), 'exec'), module.__dict__)
    except BaseException:
        del sys.modules[name]
        raise
    return module


def lead():
    return exec_verified('claude_lead', LEAD_MODULE, LEAD_MODULE_SHA256)


def inventory_modules(inventory):
    """The copied F10K inventory modules, executed from their frozen frame-inventory identities (dependency order)."""
    return {name: exec_verified(name, FRAME / 'modules' / (name + '.py'), inventory['members']['modules/' + name + '.py']['sha256'])
            for name in INVENTORY_MODULES}


def frame_json(inventory, relative):
    """A frame data member, read once and required to equal its frozen inventory identity."""
    data, row = pinned(FRAME / relative)
    require({k: row[k] for k in ('sha256', 'bytes', 'mode')} == inventory['members'][relative], 'frame member changed: ' + relative)
    return json.loads(data)


def invoke(argv, env, out, name):
    result = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=OBSERVATION_TIMEOUT_SECONDS)
    out.write_json(name, {'argv': argv, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    return result


def fresh_lead(stage, candidate, out, name):
    claude_lead = lead()
    observation = claude_lead.observe(stage, str(candidate))
    claude_lead.check_observation(observation, stage, str(candidate))
    out.write_json(name, observation)
    return claude_lead


# ---------------------------------------------------------------- frame identity, review and adoption profiles

def frame_members():
    frame = Dir.anchor(FRAME)
    try:
        tree = observe_tree(frame, exclude_partitions=False, skip_top=('review', 'frame-inventory.json'))
    finally:
        frame.close()
    require(not any('__pycache__' in d.split('/') for d in tree['directories']), 'bytecode cache in frame')
    return tree['files']


def base_pins():
    pins = {'binding': pin(BASE / 'source-binding.json'), 'inventory': pin(BASE / 'source-inventory.json'),
            'dirmodes': pin(BASE / 'source-directory-modes.json')}
    require(pins['binding']['sha256'] == BASE_BINDING_SHA256 and pins['inventory']['sha256'] == BASE_INVENTORY_SHA256
            and pins['dirmodes']['sha256'] == BASE_DIRMODES_SHA256, 'reviewed commonV4 descriptor pins')
    return pins


def freeze():
    frame = Dir.anchor(FRAME)
    try:
        require(not frame.has('frame-inventory.json'), 'frame already frozen')
        require(sha(LEAD_MODULE) == LEAD_MODULE_SHA256, 'lead module pin')
        pins = base_pins()
        record = frame.write_json('frame-inventory.json', {
            'schema': 'claude-scratch-frame-inventory-v5', 'at': now(), 'frame': str(FRAME), 'members': frame_members(),
            'lead_module': pin(LEAD_MODULE), 'base_source_binding': pins['binding'], 'base_inventory': pins['inventory'],
            'base_directory_modes': pins['dirmodes'], 'truth_boundary': LABEL})
    finally:
        frame.close()
    print(json.dumps({'frozen': record}))


def frame_inventory():
    data, row = pinned(INVENTORY)
    inventory = json.loads(data)
    require(inventory.get('schema') == 'claude-scratch-frame-inventory-v5' and inventory.get('frame') == str(FRAME), 'inventory profile')
    require(inventory['members'] == frame_members(), 'frame changed after freeze')
    require(inventory['lead_module'] == pin(LEAD_MODULE) and inventory['lead_module']['sha256'] == LEAD_MODULE_SHA256,
            'inventory lead module pin')
    pins = base_pins()
    require((inventory['base_source_binding'], inventory['base_inventory'], inventory['base_directory_modes'])
            == (pins['binding'], pins['inventory'], pins['dirmodes']), 'inventory base pins')
    inventory['__pin__'] = row
    return inventory


def rollout_join(events_path, argv_path):
    """GPT-6.1 form of the review-provenance join (W-1 §23: the gpt-6.1-sol `rollout_join`, RETAINED unchanged for a
    GPT-6.1 review and selected by `reviewer_kind` via review_provenance_join). Actual codex-exec review joined to its
    recorded rollout: roster, model, cwd, provider, final message and its timestamp, argv. All reads anchored."""
    mismatches = []

    def need(condition, what):
        if not condition:
            mismatches.append(what)
    review = Dir.anchor(REVIEW)
    try:
        freeze_record = json.loads(review.read_bytes('review-freeze.json'))
        need(set(freeze_record.get('files', {})) == FRAME_REVIEW_ROSTER, 'review freeze roster')
        for name in sorted(FRAME_REVIEW_ROSTER & set(freeze_record.get('files', {}))):
            row = freeze_record['files'][name]
            need(review.ident(name) == {k: row[k] for k in ('sha256', 'bytes', 'mode')}, 'freeze member ' + name)
        need(freeze_record.get('actual_model_selection') == 'gpt-6.1-sol' and freeze_record.get('different_from_author') is True,
             'freeze model/author profile')
        reported_names = {name: review.ident(name)['sha256'] for name in ('review.json', 'REVIEW.md', 'review-freeze.json')}
    finally:
        review.close()
    events_bytes, events_pin = pinned(events_path)
    events = [json.loads(line) for line in events_bytes.decode().splitlines() if line.strip().startswith('{')]
    threads = sorted({e['thread_id'] for e in events if e.get('type') == 'thread.started'})
    need(len(threads) == 1, 'exactly one thread in the event stream')
    thread = threads[0] if threads else ''
    finals = [e['item']['text'] for e in events
              if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
    rollouts = sorted(glob.glob('/home/sicarii/.codex/sessions/*/*/*/rollout-*' + thread + '.jsonl')) if thread else []
    need(len(rollouts) == 1, 'exactly one rollout for thread')
    contexts, providers, rollout_final, rollout_final_at, rollout_pin = [], [], None, None, None
    if len(rollouts) == 1:
        rollout_bytes, rollout_pin = pinned(rollouts[0])
        for line in rollout_bytes.decode().splitlines():
            row = json.loads(line)
            payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
            if row.get('type') == 'turn_context':
                contexts.append({k: payload.get(k) for k in ('model', 'effort', 'cwd', 'approval_policy', 'sandbox_policy')})
            if row.get('type') == 'session_meta':
                providers.append(payload.get('model_provider'))
            if row.get('type') == 'event_msg' and payload.get('type') == 'task_complete':
                rollout_final, rollout_final_at = payload.get('last_agent_message'), row.get('timestamp')
    need(bool(contexts) and all(c['model'] == 'gpt-6.1-sol' for c in contexts), 'rollout model gpt-6.1-sol')
    need(bool(contexts) and all(c['cwd'] == str(REVIEW) for c in contexts), 'rollout cwd is the review directory')
    need(bool(providers) and all(p in ('openai', 'openai-review') for p in providers), 'rollout provider is the ChatGPT backend')
    need(bool(finals) and rollout_final is not None and finals[-1] == rollout_final, 'event final message equals rollout final')
    need(isinstance(rollout_final_at, str), 'rollout completion timestamp')
    reported = set(re.findall(r'\b[0-9a-f]{64}\b', rollout_final or ''))
    for name, digest in reported_names.items():
        need(digest in reported, 'rollout final message reports ' + name)
    argv_bytes, argv_pin = pinned(argv_path)
    argv = json.loads(argv_bytes)
    need(isinstance(argv, list) and len(argv) > 4 and argv[0] == '/usr/lib/chatgpt/resources/codex' and argv[1] == 'exec'
         and '-m' in argv and argv[argv.index('-m') + 1] == 'gpt-6.1-sol' and 'model_reasoning_effort=max' in argv,
         'recorded exec argv is an actual gpt-6.1-sol max-effort codex exec')
    provenance = {'reviewer_kind': 'gpt-6.1-sol',
                  'reviewer_thread': thread, 'rollout': rollout_pin, 'turn_contexts': contexts, 'session_providers': providers,
                  'exec_argv': argv, 'exec_argv_record': argv_pin, 'event_stream': events_pin,
                  'rollout_final_message_sha256': hashlib.sha256((rollout_final or '').encode()).hexdigest(),
                  'rollout_final_timestamp': rollout_final_at}
    return mismatches, provenance


def review_freeze_kind():
    """D-LEAD-REVIEW-PROVENANCE (W-1 §23). Read the sealed review-freeze.json of the installed frame review and name
    which provenance form it is. Selection is by `reviewer_kind`: 'claude-subagent' selects the Claude-review join;
    an absent `reviewer_kind` with `actual_model_selection == 'gpt-6.1-sol'` is the retained GPT-6.1 rollout form (so
    an already-sealed GPT-6.1 review keeps its standing). Anything else returns the raw value so the caller REFUSES.
    This never accepts a label alone: the chosen join still binds and re-verifies every byte listed in §23.4."""
    review = Dir.anchor(REVIEW)
    try:
        freeze = json.loads(review.read_bytes('review-freeze.json'))
    finally:
        review.close()
    kind = freeze.get('reviewer_kind')
    if kind == 'claude-subagent':
        return 'claude-subagent'
    if kind in (None, 'gpt-6.1-sol') and freeze.get('actual_model_selection') == 'gpt-6.1-sol':
        return 'gpt-6.1-sol'
    return kind


def claude_review_join(task_output_path, reviewer_agent_id):
    """Claude-subagent form of the review-provenance join (W-1 §23.4, NEW; SOURCE-ONLY, UNINSTALLED). For a Claude
    review subagent the join requires ALL of, and binds each into the adoption record for re-check at every use:
      - the sealed review-freeze.json over REVIEW.md/review.json/checks.json, each file's sha256 (and bytes) matching
        the sealed bytes, and the freeze's own sha256;
      - raw-final-message.txt (the reviewer's verbatim final message, transcribed under seal) with its sha256;
      - the reviewer agent id, bound to the identity of the sealed task-output file (the harness names it
        'agent-<id>.jsonl'), not accepted as a bare label;
      - the sha256 of the reviewer's sealed task output (the harness task-output file the lead sealed from); this
        replaces the ~/.codex/sessions rollout-file uniqueness of the GPT form (§23.5 item 3) -- there is no codex
        rollout for a Claude review, so the task-output/agent-id identity is bound instead;
      - reviewer_kind == 'claude-subagent';
      - different_from_author == True (the independence rule is unchanged).
    AUTHOR NOTE (for the §23.6 frame-design review): §23.4's enumerated Claude-form set carries no review-completion
    timestamp, yet validate_adoption_observation() must order the adoption observation AFTER review completion. To
    avoid loosening that invariant, this join ADDITIONALLY requires a sealed `completed_at` in the freeze and binds it
    as `review_completed_at`; this one required field is stricter than §23.4's literal list and is flagged for review.
    Never a label alone; never claims a GPT-6.1 gate was met."""
    mismatches = []

    def need(condition, what):
        if not condition:
            mismatches.append(what)
    review = Dir.anchor(REVIEW)
    try:
        freeze_bytes = review.read_bytes('review-freeze.json')
        freeze_sha = hashlib.sha256(freeze_bytes).hexdigest()
        freeze_record = json.loads(freeze_bytes)
        need(set(freeze_record.get('files', {})) == CLAUDE_REVIEW_ROSTER,
             'claude review freeze roster is exactly REVIEW.md/review.json/checks.json')
        for name in sorted(CLAUDE_REVIEW_ROSTER & set(freeze_record.get('files', {}))):
            row = freeze_record['files'][name]
            ident = review.ident(name)
            need(ident['sha256'] == row.get('sha256') and ident['bytes'] == row.get('bytes'),
                 'claude freeze member sha256/bytes ' + name)
        need(freeze_record.get('reviewer_kind') == 'claude-subagent', 'freeze reviewer_kind is claude-subagent')
        need(freeze_record.get('different_from_author') is True, 'freeze different_from_author is true')
        model_selection = freeze_record.get('actual_model_selection')
        need(isinstance(model_selection, str) and model_selection.strip() != '', 'freeze actual_model_selection present')
        completed_at = freeze_record.get('completed_at')
        need(isinstance(completed_at, str) and completed_at.strip() != '',
             'freeze completed_at present (adoption-observation ordering; §23 author note)')
        need(review.has('raw-final-message.txt'), 'raw-final-message.txt present and sealed')
        raw_final_sha = review.ident('raw-final-message.txt')['sha256'] if review.has('raw-final-message.txt') else None
    finally:
        review.close()
    task_bytes, task_pin = pinned(task_output_path)
    need(isinstance(reviewer_agent_id, str) and reviewer_agent_id.strip() != '', 'reviewer agent id present')
    need(isinstance(reviewer_agent_id, str) and ('agent-' + reviewer_agent_id) in Path(task_output_path).name,
         'reviewer agent id bound to the sealed task-output file name')
    provenance = {'reviewer_kind': 'claude-subagent', 'different_from_author': True,
                  'actual_model_selection': model_selection, 'review_completed_at': completed_at,
                  'review_freeze_sha256': freeze_sha, 'raw_final_message_sha256': raw_final_sha,
                  'reviewer_agent_id': reviewer_agent_id, 'reviewer_task_output': task_pin,
                  'reviewer_task_output_sha256': task_pin['sha256']}
    return mismatches, provenance


def review_provenance_join(events_path=None, argv_path=None, task_output_path=None, reviewer_agent_id=None):
    """D-LEAD-REVIEW-PROVENANCE (W-1 §23) dual-form dispatcher. The form is selected by `reviewer_kind` in the sealed
    review-freeze.json (review_freeze_kind()): a GPT-6.1 review uses the retained rollout join (§23.4 keeps the
    gpt-6.1-sol form), a claude-subagent review uses claude_review_join(). A review of NEITHER recognized form
    REFUSES. Returns (mismatches, provenance); provenance always carries 'reviewer_kind'."""
    kind = review_freeze_kind()
    if kind == 'gpt-6.1-sol':
        if events_path is None or argv_path is None:
            return ['gpt-6.1-sol review requires the recorded event stream and exec-argv record'], {'reviewer_kind': 'gpt-6.1-sol'}
        return rollout_join(events_path, argv_path)
    if kind == 'claude-subagent':
        if task_output_path is None or reviewer_agent_id is None:
            return ['claude-subagent review requires the sealed task-output path and reviewer agent id'], {'reviewer_kind': 'claude-subagent'}
        return claude_review_join(task_output_path, reviewer_agent_id)
    return ['unrecognized reviewer_kind (neither gpt-6.1-sol rollout nor claude-subagent): ' + repr(kind)], {'reviewer_kind': kind}


def review_profile_problems(review, lead_id, inventory_sha, reviewer_kind=None, model_selection=None):
    problems = [key for key, value in REVIEW_PROFILE.items() if review.get(key) != value]
    # D-LEAD-REVIEW-PROVENANCE (§23.5 item 13): actual_model_selection is accepted per form, selected by reviewer_kind.
    if reviewer_kind == 'gpt-6.1-sol':
        if review.get('actual_model_selection') != 'gpt-6.1-sol':
            problems.append('actual_model_selection')
        if review.get('reviewer_kind') not in (None, 'gpt-6.1-sol'):
            problems.append('reviewer_kind')
    elif reviewer_kind == 'claude-subagent':
        if review.get('reviewer_kind') != 'claude-subagent':
            problems.append('reviewer_kind')
        if review.get('actual_model_selection') != model_selection:
            problems.append('actual_model_selection')
        if review.get('different_from_author') is not True:
            problems.append('different_from_author')
    else:
        problems.append('unrecognized reviewer_kind: ' + repr(reviewer_kind))
    if review.get('candidate') != str(FRAME):
        problems.append('candidate')
    if review.get('lead_id') != lead_id:
        problems.append('lead_id')
    if review.get('frame_inventory_sha256') != inventory_sha:
        problems.append('frame_inventory_sha256')
    if review.get('report_sha256') != sha(REVIEW / 'REVIEW.md'):
        problems.append('report_sha256')
    for key, name in (('checks', 'checks.json'), ('complete_bound_inputs', 'bound-inputs.json'), ('tool_topology', 'tool-topology.json')):
        if (review.get(key) or {}) != pin(REVIEW / name):
            problems.append('sidecar ' + key)
    return problems


def validate_adoption_observation(claude_lead, observation, adoption_at, provenance):
    """The retained adoption observation: complete schema, stage, candidate, identity and authority profile, joined to
    the exact append-only transcript prefix it observed, and ordered after the review's completion and before the
    adoption record (v3 B4). The later-goal list must be derived from the observed goal commands (v4 N06)."""
    require(observation.get('schema') == claude_lead.OBSERVATION_SCHEMA and observation.get('stage') == 'scratch-adopt'
            and observation.get('candidate') == str(FRAME), 'adoption observation schema/stage/candidate')
    require(observation.get('sourcePreparationOnly') is False and observation.get('targetExecution') is False
            and observation.get('admission') is False and observation.get('reservation') is False,
            'adoption observation authority profile')
    observed = observation.get('leadObservation') or {}
    expected = {'leadId': claude_lead.LEAD_ID, 'harness': 'claude-code', 'sessionId': claude_lead.SESSION_ID,
                'transcript': str(claude_lead.TRANSCRIPT), 'goalRecord': claude_lead.GOAL_RECORD,
                'goalSetRecord': claude_lead.GOAL_SET_RECORD, 'objectiveSha256': claude_lead.OBJECTIVE_SHA256,
                'startInstruction': claude_lead.START_INSTRUCTION, 'laterGoalCommandIndexes': [],
                'liveWithinSeconds': claude_lead.MAX_LEAD_SILENCE_SECONDS, 'transcriptLive': True, 'status': 'active'}
    wrong = sorted(key for key, value in expected.items() if observed.get(key) != value)
    require(not wrong, 'adoption observation identity/profile: ' + repr(wrong))
    start = pin(claude_lead.START_INSTRUCTION['path'])
    require(start['sha256'] == claude_lead.START_INSTRUCTION['sha256'] and start['bytes'] == claude_lead.START_INSTRUCTION['bytes'],
            'start instruction identity')
    size = observed.get('transcriptBytesObserved')
    require(isinstance(size, int) and not isinstance(size, bool) and size > 0, 'observed transcript size')
    transcript_dir = Dir.anchor(Path(claude_lead.TRANSCRIPT).parent)
    try:
        prefix = transcript_dir.read_prefix(existing_name(Path(claude_lead.TRANSCRIPT).name), size)
    finally:
        transcript_dir.close()
    require(hashlib.sha256(prefix).hexdigest() == observed.get('transcriptSha256Observed'),
            'adoption observation is not a prefix of the append-only transcript')
    lines = prefix.split(b'\n')
    if lines and lines[-1] == b'':
        lines.pop()
    for key in ('goalRecord', 'goalSetRecord'):
        row = observed[key]
        require(row['index'] < len(lines) and hashlib.sha256(lines[row['index']]).hexdigest() == row['sha256'],
                'goal record in the observed prefix: ' + key)
    commands = claude_lead._goal_command_indexes(lines)
    require(commands == observed.get('goalCommandIndexesObserved'), 'goal commands in observed prefix')
    require([index for index in commands if index > claude_lead.GOAL_RECORD['index']] == observed.get('laterGoalCommandIndexes') == [],
            'later goal commands derived from the observed goal commands')
    last = claude_lead._last_timestamp(lines)
    require(last is not None and last == observed.get('lastTranscriptTimestamp'), 'last transcript timestamp in observed prefix')
    observed_at = parse_time(observation['clockObservation']['current_time'])
    silence = (observed_at - parse_time(last)).total_seconds()
    recorded_silence = observed.get('transcriptSilenceSeconds')
    require(isinstance(recorded_silence, (int, float)) and abs(silence - recorded_silence) <= 1.0
            and 0 <= silence <= claude_lead.MAX_LEAD_SILENCE_SECONDS, 'adoption observation liveness')
    # D-LEAD-REVIEW-PROVENANCE (W-1 §23): the observation must follow review completion and precede the adoption
    # record, for EITHER provenance form. The GPT-6.1 form bounds it by the rollout completion timestamp; the
    # claude-subagent form bounds it by the sealed freeze `completed_at` (bound as review_completed_at by
    # claude_review_join). The invariant is preserved, not loosened; a review of neither form never reaches here.
    if provenance.get('reviewer_kind') == 'claude-subagent':
        lower = provenance.get('review_completed_at')
        require(isinstance(lower, str)
                and parse_time(lower) <= observed_at <= parse_time(adoption_at),
                'adoption observation must follow the claude review completion and precede the adoption record')
    else:
        require(isinstance(provenance.get('rollout_final_timestamp'), str)
                and parse_time(provenance['rollout_final_timestamp']) <= observed_at <= parse_time(adoption_at),
                'adoption observation must follow the review completion and precede the adoption record')


def adopt(events_path=None, argv_path=None, task_output_path=None, reviewer_agent_id=None):
    # D-LEAD-REVIEW-PROVENANCE (W-1 §23): the review-provenance join is now dual-form, selected by the sealed
    # review-freeze.json `reviewer_kind`. A GPT-6.1 review supplies (events_path, argv_path); a claude-subagent
    # review supplies (task_output_path, reviewer_agent_id). A review of neither form refuses. SCHEMA bumped to
    # ...-v6 to carry both forms (§23.5 item 7). SOURCE-ONLY, UNINSTALLED; adoption BLOCKED pending review of §23.
    claude_lead = lead()
    inventory = frame_inventory()
    review_dir = Dir.anchor(FRAME / 'review')
    try:
        require(not review_dir.has('lead-adoption.json'), 'adoption already recorded')
        review = load_json(REVIEW / 'review.json')
        mismatches, provenance = review_provenance_join(events_path, argv_path, task_output_path, reviewer_agent_id)
        reviewer_kind = provenance.get('reviewer_kind')
        mismatches += ['review profile: ' + p for p in review_profile_problems(
            review, claude_lead.LEAD_ID, inventory['__pin__']['sha256'], reviewer_kind, provenance.get('actual_model_selection'))]
        observation = claude_lead.observe('scratch-adopt', str(FRAME))
        claude_lead.check_observation(observation, 'scratch-adopt', str(FRAME))
        require(not mismatches, 'adoption mismatches: ' + repr(mismatches))
        at = now()
        validate_adoption_observation(claude_lead, observation, at, provenance)
        record = review_dir.write_json('lead-adoption.json', {
            'schema': 'claude-scratch-frame-lead-adoption-v6', 'at': at, 'frame': str(FRAME), 'lead_id': claude_lead.LEAD_ID,
            'frame_inventory_sha256': inventory['__pin__']['sha256'], 'review_sha256': sha(REVIEW / 'review.json'),
            'review_freeze_sha256': sha(REVIEW / 'review-freeze.json'), 'review_report_sha256': sha(REVIEW / 'REVIEW.md'),
            'mismatches': [], **provenance, 'lead_observation': observation, 'truth_boundary': LABEL})
    finally:
        review_dir.close()
    print(json.dumps({'adoption': record}))


def frame_admitted():
    """Complete frame, review profile, adoption profile, re-joined rollout provenance and the validated retained
    adoption observation; refuses otherwise. Returns the frozen inventory."""
    claude_lead = lead()
    inventory = frame_inventory()
    inventory_sha = inventory['__pin__']['sha256']
    review = load_json(REVIEW / 'review.json')
    adoption = load_json(ADOPTION)
    # D-LEAD-REVIEW-PROVENANCE (W-1 §23 / §23.5 items 7, 9, 10; §17): accept both adoption schema forms (v5 = legacy
    # GPT-6.1-only records keep their standing; v6 carries either form), and re-join + re-pin provenance by reviewer_kind.
    require(adoption.get('schema') in ('claude-scratch-frame-lead-adoption-v5', 'claude-scratch-frame-lead-adoption-v6')
            and adoption.get('frame') == str(FRAME), 'adoption profile')
    require(adoption['lead_id'] == claude_lead.LEAD_ID and adoption['mismatches'] == [], 'adoption lead/mismatches')
    require(adoption['frame_inventory_sha256'] == inventory_sha, 'adoption frame inventory')
    require(adoption['review_sha256'] == sha(REVIEW / 'review.json'), 'adoption review pin')
    require(adoption['review_freeze_sha256'] == sha(REVIEW / 'review-freeze.json'), 'adoption review-freeze pin')
    require(adoption['review_report_sha256'] == sha(REVIEW / 'REVIEW.md'), 'adoption review report pin')
    reviewer_kind = adoption.get('reviewer_kind')
    problems = review_profile_problems(review, claude_lead.LEAD_ID, inventory_sha, reviewer_kind, adoption.get('actual_model_selection'))
    require(not problems, 'review profile: ' + repr(problems))
    if reviewer_kind == 'claude-subagent':
        require(adoption.get('reviewer_task_output') is not None
                and pin(adoption['reviewer_task_output']['path']) == adoption['reviewer_task_output'],
                'adoption provenance pin changed: reviewer_task_output')
        mismatches, provenance = review_provenance_join(
            task_output_path=adoption['reviewer_task_output']['path'], reviewer_agent_id=adoption.get('reviewer_agent_id'))
        require(not mismatches, 'claude review join no longer holds: ' + repr(mismatches))
        for key in ('reviewer_kind', 'different_from_author', 'actual_model_selection', 'review_completed_at',
                    'review_freeze_sha256', 'raw_final_message_sha256', 'reviewer_agent_id', 'reviewer_task_output_sha256'):
            require(provenance.get(key) == adoption.get(key), 'claude review identity changed: ' + key)
    else:
        for key in ('rollout', 'exec_argv_record', 'event_stream'):
            require(adoption[key] is not None and pin(adoption[key]['path']) == adoption[key], 'adoption provenance pin changed: ' + key)
        mismatches, provenance = review_provenance_join(adoption['event_stream']['path'], adoption['exec_argv_record']['path'])
        require(not mismatches, 'rollout join no longer holds: ' + repr(mismatches))
        for key in ('reviewer_thread', 'rollout_final_message_sha256', 'rollout_final_timestamp'):
            require(provenance[key] == adoption[key], 'rollout identity changed: ' + key)
    validate_adoption_observation(claude_lead, adoption['lead_observation'], adoption['at'], provenance)
    return inventory


# ---------------------------------------------------------------- confined throwaway source (B3, B5)

def base_tree():
    """The reviewed commonV4 descriptors and the observed source tree; returns an anchored source handle."""
    binding_bytes, binding_pin = pinned(BASE / 'source-binding.json')
    inventory_bytes, inventory_pin = pinned(BASE / 'source-inventory.json')
    modes_bytes, modes_pin = pinned(BASE / 'source-directory-modes.json')
    require(binding_pin['sha256'] == BASE_BINDING_SHA256 and inventory_pin['sha256'] == BASE_INVENTORY_SHA256
            and modes_pin['sha256'] == BASE_DIRMODES_SHA256, 'reviewed commonV4 descriptor pins')
    binding = json.loads(binding_bytes)
    require(binding['candidate']['inventory']['sha256'] == BASE_INVENTORY_SHA256
            and Path(binding['candidate']['path']) == BASE / 'source', 'base binding profile')
    inventory, directories = json.loads(inventory_bytes), json.loads(modes_bytes)
    source = Dir.anchor(BASE / 'source')
    try:
        require(tree_content(observe_tree(source, exclude_partitions=False)) == {'files': inventory, 'directories': directories},
                'reviewed commonV4 tree changed')
    except BaseException:
        source.close()
        raise
    return source, inventory, directories, {'binding': binding_pin, 'inventory': inventory_pin, 'dirmodes': modes_pin}


def overlay_rules(keys, deletion_bytes, inventory):
    """Only core Ada units plus an optional DELETE.list of base core Ada units; returns the sorted deletions."""
    keys = set(keys)
    for relative in keys:
        if relative != 'DELETE.list':
            require(re.fullmatch('core/' + UNIT_RE, relative) is not None,
                    'overlay may contain only Ada units under core/ (fixed build graph): ' + relative)
    deletions = []
    if 'DELETE.list' in keys:
        deletions = [line.strip() for line in deletion_bytes.decode('utf-8').splitlines() if line.strip()]
    require(len(set(deletions)) == len(deletions), 'duplicate deletion')
    for relative in deletions:
        require(re.fullmatch('core/' + UNIT_RE, relative) is not None, 'deletion outside core Ada units: ' + relative)
        require(relative not in keys, 'overlay and deletion of the same path')
        require(relative in inventory, 'deletion of a non-base file: ' + relative)
    return sorted(deletions)


def expected_source(inventory, directories, unit_rows, deletions):
    """Base inventory minus deletions plus overlay units (base mode, else 0644); base directory modes."""
    removed = set(deletions)
    files = {relative: row for relative, row in inventory.items() if relative not in removed}
    for relative, row in unit_rows.items():
        files[relative] = {'sha256': row['sha256'], 'bytes': row['bytes'],
                           'mode': inventory[relative]['mode'] if relative in inventory else 0o644}
    return {'files': files, 'directories': directories}


def run_record(run):
    data, mode = run.read_regular('materialization.json')
    return data, {'path': str(run.path / 'materialization.json'), 'sha256': hashlib.sha256(data).hexdigest(),
                  'bytes': len(data), 'mode': mode}


def verify_materialization(run, record, source, snapshot):
    """Re-derive the whole recipe - reviewed base descriptors and tree, retained overlay snapshot (Ada-only keyset,
    DELETE.list, applied bytes) - and require the record and the throwaway source, observed through the HELD source
    and snapshot descriptors, to equal it exactly, including the directory identities recorded at materialization
    (V4-B01). Returns the source observation, whose identities cover every directory (generated partitions
    included). Runs at materialize, at parent and child admission, immediately before the target spawn and at
    conclusion (v3 B3, B5)."""
    require(record.get('schema') == 'claude-scratch-materialization-v5' and record.get('run') == str(run.path),
            'materialization profile')
    base_source, inventory, directories, pins = base_tree()
    base_source.close()
    require((record.get('base_source_binding'), record.get('base_inventory'), record.get('base_directory_modes'))
            == (pins['binding'], pins['inventory'], pins['dirmodes']), 'materialization base pins')
    snapshot_tree = observe_tree(snapshot, exclude_partitions=False)
    require(tree_content(snapshot_tree) == record.get('overlay_snapshot')
            and snapshot_tree['identities'] == record.get('overlay_snapshot_identities'), 'overlay snapshot identity changed')
    require(set(snapshot_tree['directories']) <= {'.', 'core'}, 'overlay snapshot directories')
    deletion_bytes = b''
    if 'DELETE.list' in snapshot_tree['files']:
        deletion_bytes, mode = snapshot.read_regular('DELETE.list')
        require({'sha256': hashlib.sha256(deletion_bytes).hexdigest(), 'bytes': len(deletion_bytes), 'mode': mode}
                == snapshot_tree['files']['DELETE.list'], 'DELETE.list changed during verification')
    deletions = overlay_rules(snapshot_tree['files'], deletion_bytes, inventory)
    require(deletions == record.get('deletions'), 'materialization deletions')
    units = {relative: row for relative, row in snapshot_tree['files'].items() if relative != 'DELETE.list'}
    require(sorted(units) == record.get('overlays'), 'materialization overlays')
    expected = expected_source(inventory, directories, units, deletions)
    require(record.get('source') == expected, 'materialization record differs from its recipe')
    observed = observe_tree(source, exclude_partitions=True)
    require(tree_content(observed) == expected, 'throwaway source differs from base plus overlays minus deletions')
    require({relative: row for relative, row in observed['identities'].items() if not in_partition(relative)}
            == record.get('source_directory_identities'),
            'a throwaway source directory is not the directory created at materialization')
    return observed


def materialize(name, overlay_text):
    require(re.fullmatch(NAME_RE, name) is not None, 'invalid run name')
    overlay_path = Path(overlay_text)
    require(overlay_path.is_absolute(), 'overlay path must be absolute')
    overlay = Dir.anchor(overlay_path)
    try:
        overlay_tree = observe_tree(overlay, exclude_partitions=False)
        require(set(overlay_tree['directories']) <= {'.', 'core'}, 'overlay directories')
        overlay_bytes = read_files(overlay, overlay_tree)
    finally:
        overlay.close()
    base_source, inventory, directories, pins = base_tree()
    held = []
    try:
        deletions = overlay_rules(overlay_bytes, overlay_bytes.get('DELETE.list', b''), inventory)
        units = {relative: data for relative, data in overlay_bytes.items() if relative != 'DELETE.list'}
        unit_rows = {relative: {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)} for relative, data in units.items()}
        expected = expected_source(inventory, directories, unit_rows, deletions)
        runs_parent = Dir.anchor(RUNS.parent)
        try:
            if not runs_parent.has(RUNS.name):
                runs_parent.child(RUNS.name, create=True).close()
            runs = runs_parent.child(RUNS.name)
        finally:
            runs_parent.close()
        try:
            require(not runs.has(name), 'run already exists')
            run = runs.child(name, create=True)
        finally:
            runs.close()
        held.append(run)
        snapshot = run.child('overlay-snapshot', create=True)
        held.append(snapshot)
        for relative, data in sorted(overlay_bytes.items()):
            parent = snapshot.descend(Path(relative).parent.as_posix(), create=True)
            try:
                parent.write_bytes(Path(relative).name, data)
            finally:
                parent.close()
        snapshot.sync()
        source = run.child('source', create=True)
        held.append(source)
        for relative in sorted((r for r in directories if r != '.'), key=lambda r: (r.count('/'), r)):
            parent = source.descend(Path(relative).parent.as_posix())
            try:
                parent.child(Path(relative).name, create=True).close()
            finally:
                parent.close()
        for relative, row in sorted(expected['files'].items()):
            if relative in units:
                data = units[relative]
            else:
                holder = base_source.descend(Path(relative).parent.as_posix())
                try:
                    data = holder.read_bytes(Path(relative).name)
                finally:
                    holder.close()
            require(hashlib.sha256(data).hexdigest() == row['sha256'] and len(data) == row['bytes'],
                    'bytes differ from the recipe: ' + relative)
            parent = source.descend(Path(relative).parent.as_posix())
            try:
                parent.write_bytes(Path(relative).name, data, row['mode'])
            finally:
                parent.close()
        for relative in sorted(directories, key=lambda r: (-r.count('/'), r) if r != '.' else (1, '')):
            handle = source.descend('.' if relative == '.' else relative)
            try:
                handle.set_mode(directories[relative])
            finally:
                handle.close()
        source.sync()
        snapshot_tree = observe_tree(snapshot, exclude_partitions=False)
        source_tree = observe_tree(source, exclude_partitions=True)
        require(tree_content(source_tree) == expected, 'materialized source differs from its recipe')
        require(not any(in_partition(relative) for relative in source_tree['identities']), 'generated output at materialization')
        record = run.write_json('materialization.json', {
            'schema': 'claude-scratch-materialization-v5', 'at': now(), 'run': str(run.path),
            'base_source_binding': pins['binding'], 'base_inventory': pins['inventory'],
            'base_directory_modes': pins['dirmodes'], 'overlay_dir': str(overlay_path),
            'overlay_snapshot': tree_content(snapshot_tree), 'overlay_snapshot_identities': snapshot_tree['identities'],
            'overlays': sorted(units), 'deletions': deletions, 'source': expected,
            'source_directory_identities': source_tree['identities'], 'truth_boundary': LABEL})
        data, _pin = run_record(run)
        verify_materialization(run, json.loads(data), source, snapshot)
        for handle in held:
            handle.verify_location()
    finally:
        for handle in reversed(held):
            handle.close()
        base_source.close()
    print(json.dumps({'materialization': record, 'overlays': sorted(units), 'deletions': deletions}))


# ---------------------------------------------------------------- allowlist, specifications, identities, samples

def command(action, args, materialization):
    def unit(text):
        require(re.fullmatch(UNIT_RE, text) is not None, 'unit operand grammar')
        require(('core/' + text) in materialization['source']['files'], 'unit not enrolled in this materialization')
        return text
    project = ['-P', 'core/worldline_core_sources.gpr']
    if action == 'prove-all-k' and args == []:
        return [GNATPROVE] + project + ['-U'] + STRICT_TAIL + ['-k']
    if action == 'prove-all' and args == []:
        return [GNATPROVE] + project + ['-U'] + STRICT_TAIL
    if action == 'prove-file' and len(args) == 1:
        return [GNATPROVE] + project + ['-u', unit(args[0])] + STRICT_TAIL + ['-k']
    if action == 'prove-subp' and len(args) == 2 and re.fullmatch(r'[1-9][0-9]{0,5}', args[1]):
        return [GNATPROVE] + project + ['-u', unit(args[0])] + STRICT_TAIL + ['--limit-subp=' + args[0] + ':' + args[1], '-k']
    if action == 'compile-all' and args == []:
        return [GPRBUILD, '-p', '-j2', '-c', '-U'] + project
    raise RuntimeError('action/arguments not in the reviewed allowlist: ' + action + ' ' + repr(args))


def specifications(inventory, source):
    template = frame_json(inventory, 'baselines/tool-inventory-template.json')
    tool_spec = json.loads(json.dumps(template['tool_inventory_spec']))
    expected = tool_spec['effective_environment']
    for key in ('PENDING_LIBRARY_DIR', 'PENDING_OBJECT_DIR', 'PYTHONPATH', 'WORLDLINE_CORE_LIB'):
        require(F10K_SOURCE in expected[key], 'relocatable key ' + key)
        expected[key] = expected[key].replace(F10K_SOURCE, str(source))
    require(not any(F10K_SOURCE in str(v) for v in expected.values()), 'unrelocated tool environment value')
    launch = frame_json(inventory, 'baselines/launch-environment.json')
    gnat_path = ':'.join(str(GNAT / p / 'bin') for p in
                         ['gnat-aarch64-linux-16.1.0-1', 'gprbuild-aarch64-linux-26.0.0-1', 'gnatprove-aarch64-linux-16.1.0-1'])
    require(expected['PATH'] == gnat_path + ':' + launch['PATH'], 'reviewed PATH composition changed')
    closure = frame_json(inventory, 'baselines/runtime-closure.json')
    runtime_spec = json.loads(json.dumps(closure['spec']))
    require(runtime_spec['mutable_directory_identities'].count(F10K_SOURCE) == 1, 'runtime spec relocation')
    runtime_spec['mutable_directory_identities'] = [str(source) if v == F10K_SOURCE else v
                                                    for v in runtime_spec['mutable_directory_identities']]
    runtime_expected = json.loads(json.dumps(closure['inventory']))
    entry = runtime_expected['directories'].pop(F10K_SOURCE)
    require(entry['resolved'] == F10K_SOURCE, 'runtime baseline relocation entry')
    runtime_expected['directories'][str(source)] = {**entry, 'resolved': str(source)}
    runtime_expected['directories'] = dict(sorted(runtime_expected['directories'].items()))
    require(F10K_SOURCE not in json.dumps(runtime_expected) and F10K_SOURCE not in json.dumps(runtime_spec), 'relocation complete')
    environment = {k: os.environ[k] for k in KEEP_ENVIRONMENT if k in os.environ}
    for spec_env in (expected, runtime_spec['environment']):
        for key, value in spec_env.items():
            require(key not in environment or environment[key] == value or value is None, 'environment conflict ' + key)
            if value is None:
                environment.pop(key, None)
            else:
                environment[key] = value
    for spec_env in (expected, runtime_spec['environment']):
        require({k: environment.get(k) for k in spec_env} == spec_env, 'constructed environment differs from specification')
    return tool_spec, runtime_spec, runtime_expected, environment


def retain_observation(out, name, observation, expected, expectation):
    """Retain one identity observation and return whether it equals its frozen expectation. Equal observations are
    retained as the sha256/size of their canonical JSON, which is then byte-for-byte the canonical JSON of the
    expectation - reproducible from the frozen frame baseline named by `expectation` (and, for the runtime
    closure, the source-path relocation in specifications()). Any difference retains the complete observation for
    diagnosis before the caller refuses. (v5 storage representation: per attempt the three complete copies of an
    unchanged ~34 MB closure would otherwise count against the fixed local reserve.)"""
    canonical = (json.dumps(observation, indent=2, sort_keys=True) + '\n').encode()
    canonical_expected = (json.dumps(expected, indent=2, sort_keys=True) + '\n').encode()
    equal = observation == expected and canonical == canonical_expected
    if equal:
        out.write_json(name, {'equal_to_frozen_expectation': True, 'expectation': expectation,
                              'observation_canonical_sha256': hashlib.sha256(canonical).hexdigest(),
                              'observation_canonical_bytes': len(canonical),
                              'expectation_canonical_sha256': hashlib.sha256(canonical_expected).hexdigest()})
    else:
        out.write_json(name, {'equal_to_frozen_expectation': False, 'expectation': expectation, 'observation': observation,
                              'observation_canonical_sha256': hashlib.sha256(canonical).hexdigest(),
                              'expectation_canonical_sha256': hashlib.sha256(canonical_expected).hexdigest()})
    return equal


def identities(inventory, modules, out, environment, tool_spec, runtime_spec, runtime_expected, suffix):
    baseline = frame_json(inventory, 'baselines/action-baseline.json')
    tools = modules['tool_inventory'].observe(tool_spec)
    require(retain_observation(out, 'tools-' + suffix + '.json', tools, baseline['tool_inventory'],
                               'baselines/action-baseline.json: tool_inventory'), 'tool closure differs from reviewed baseline')
    closure = frame_json(inventory, 'baselines/proof-data-closure.json')
    data = modules['proof_data_inventory'].observe(closure['spec'])
    require(retain_observation(out, 'proof-data-' + suffix + '.json', data, closure['inventory'],
                               'baselines/proof-data-closure.json: inventory'), 'proof installation/configuration data drift')
    elf = modules['proof_elf_inventory'].observe(tools)
    require(retain_observation(out, 'proof-elf-' + suffix + '.json', elf, frame_json(inventory, 'baselines/proof-elf-baseline.json'),
                               'baselines/proof-elf-baseline.json'), 'proof ELF closure drift')
    vendors = sha_many([row['original'] for row in frame_json(inventory, 'baselines/vendor-template.json')])
    require(retain_observation(out, 'vendors-' + suffix + '.json', vendors, baseline['vendor_inventory'],
                               'baselines/action-baseline.json: vendor_inventory'), 'vendor drift')
    runtime = modules['runtime_inventory'].observe(runtime_spec)
    require(retain_observation(out, 'runtime-closure-' + suffix + '.json', runtime, runtime_expected,
                               'baselines/runtime-closure.json: inventory with the single source entry relocated to this '
                               'run (specifications())'), 'Python runtime/cache/spool/native closure drift')
    manager = invoke(['/usr/bin/systemctl', '--user', 'show-environment'], environment, out, 'manager-' + suffix + '.json')
    require(manager.returncode == 0, 'manager environment unavailable')
    values = dict(line.split('=', 1) for line in manager.stdout.splitlines() if '=' in line)
    require({k: values.get(k) for k in baseline['manager_environment']} == baseline['manager_environment'], 'manager env drift')


def sample(out, environment, name, storage_reserve=None, siblings_allowed_unit=None):
    for label, pattern in (('codex-proof', 'codex-*proof*'), ('codex-scopes', 'codex-*.scope'),
                           ('claude-worldline', 'claude-worldline-*')):
        result = invoke(['/usr/bin/systemctl', '--user', 'list-units', '--all', '--state=active,activating,deactivating',
                         '--no-legend', '--plain', pattern], environment, out, name + '-' + label + '.json')
        units = [line.split()[0] for line in result.stdout.splitlines() if line.strip()]
        require(result.returncode == 0 and units in ([], [siblings_allowed_unit] if siblings_allowed_unit else []),
                'live sibling unit: ' + label + ' ' + repr(units))
    processes = invoke(['/usr/bin/ps', '-eo', 'pid,comm'], environment, out, name + '-processes.json')
    require(processes.returncode == 0, 'process sample unavailable')
    heavy = [line for line in processes.stdout.splitlines() if line.split() and line.split()[-1] in HEAVY]
    require(not heavy, 'heavy compiler/prover process present: ' + repr(heavy))
    storage = invoke([PYTHON, '-B', STORAGE], environment, out, name + '-storage.json')
    require(storage.returncode == 0, 'storage status unavailable')
    disk = json.loads(storage.stdout)
    require(disk['local_disk_bytes']['free'] > disk['configured_local_reserve_bytes'], 'local storage reserve unavailable')
    if storage_reserve is not None:
        require(disk['configured_local_reserve_bytes'] == storage_reserve, 'storage reserve policy changed during admission')
    meminfo = Path('/proc/meminfo').read_text()
    out.write_bytes(name + '-meminfo.txt', meminfo.encode())
    memory = dict(line.split(':', 1) for line in meminfo.splitlines())
    require(memory['MemAvailable'].split()[1:] == ['kB'], 'unexpected MemAvailable unit')
    return {'MemAvailable_observed_kB': int(memory['MemAvailable'].split()[0]),
            'configured_local_reserve_bytes': disk['configured_local_reserve_bytes']}


def exact_rows(receipt):
    return [json.loads(item['text']) for item in receipt['content'] if item['type'] == 'text']


def threshold_receipts(inventory):
    for name, parsed, value in (('threshold-receipt.json', '(8589934592+8589934592)/1024+1', str(MIN_MEM_AVAILABLE_KB)),
                                ('positive-boundary-receipt.json', '16777217*1024-8589934592-8589934592', '1024'),
                                ('zero-boundary-receipt.json', '(16777217-1)*1024-8589934592-8589934592', '0')):
        rows = exact_rows(frame_json(inventory, 'receipts/' + name))
        require(any(r['status'] == 'exact' and r['fields']['parsed'] == parsed and r['fields']['exact'] == value
                    and r['formal'] is False and r['non_claims'] for r in rows), 'threshold receipt ' + name)


def receipt_line(where):
    raw = bytearray()
    deadline = time.monotonic() + RECEIPT_WAIT_SECONDS
    try:
        while True:
            remaining = deadline - time.monotonic()
            require(remaining > 0, 'finite receipt input deadline expired')
            ready, _, _ = select.select([sys.stdin.fileno()], [], [], remaining)
            require(bool(ready), 'finite receipt input deadline expired')
            piece = os.read(sys.stdin.fileno(), 1)
            require(bool(piece), 'receipt input closed before complete newline')
            if not raw:
                deadline = time.monotonic() + RECEIPT_READ_SECONDS
            raw.extend(piece)
            if piece == b'\n':
                return bytes(raw).decode('utf-8')
    finally:
        where.write_bytes('stdin-response.bin', bytes(raw))


def memory_gate(inventory, attempt, environment, storage_reserve):
    threshold_receipts(inventory)
    used = set()
    live = sample(attempt, environment, 'challenge-1-before', storage_reserve)
    for number in range(1, MAX_CHALLENGES + 1):
        where = attempt.child('challenge-%d' % number, create=True)
        try:
            challenge = {'at': now(), 'kind': 'SCRATCH_FIXED_CONSERVATIVE_MEMORY_CHALLENGE', 'challenge_number': number,
                         'max_challenges': MAX_CHALLENGES, 'receipt_wait_seconds': RECEIPT_WAIT_SECONDS,
                         'memory_expression': str(live['MemAvailable_observed_kB']) + '*1024-8589934592-8589934592',
                         'minimum_memavailable_kB': MIN_MEM_AVAILABLE_KB, 'proof_usage_credit_bytes': 0,
                         'storage_reserve_bound': storage_reserve, 'no_target_launch_executed': True, 'truth_boundary': LABEL}
            record = where.write_json('challenge.json', challenge)
            print(json.dumps({'kind': challenge['kind'], 'challenge_path': record['path'], 'challenge_sha256': record['sha256'],
                              'memory_expression': challenge['memory_expression']}), flush=True)
            answer = json.loads(receipt_line(where))
            require(set(answer) == {'challenge_sha256', 'receipt_path', 'receipt_sha256'}, 'answer keyset')
            require(answer['challenge_sha256'] == record['sha256'], 'receipt belongs to another challenge')
            require(isinstance(answer['receipt_path'], str) and Path(answer['receipt_path']).is_absolute(), 'receipt path')
            receipt_bytes = read_path(answer['receipt_path'])
            copy = where.write_bytes('memory-receipt.json', receipt_bytes)
            require(copy['sha256'] == answer['receipt_sha256'], 'receipt identity changed')
            require(answer['receipt_sha256'] not in used, 'a receipt may not be reused')
            used.add(answer['receipt_sha256'])
            require(any(r['status'] == 'exact' and r['fields']['parsed'] == challenge['memory_expression']
                        and int(r['fields']['exact']) > 0 and r['formal'] is False and r['non_claims']
                        for r in exact_rows(json.loads(receipt_bytes))), 'exact positive nonformal JACKAL receipt absent')
            current = sample(where, environment, 'immediate', storage_reserve)
        finally:
            where.close()
        if current['MemAvailable_observed_kB'] >= MIN_MEM_AVAILABLE_KB:
            return {'challenge': record, 'receipt': copy, 'immediate': current}
        live = current
    raise RuntimeError('finite same-policy memory challenge limit exhausted')


# ---------------------------------------------------------------- shared window (unchanged protocol, anchored I/O)

@contextlib.contextmanager
def window_locked():
    """The existing shared-window protocol: exclusive flock on WINDOW.lock, then read/replace WINDOW - here all
    relative to the anchored window directory. The lock must be a single-link regular file; it is opened
    non-blocking so a substituted FIFO cannot stall (v4 N07)."""
    directory = Dir.anchor(WINDOW.parent)
    try:
        fd = os.open(WINDOW.name + '.lock', os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                     0o644, dir_fd=directory.fd)
        try:
            info = os.fstat(fd)
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'window lock is not a single-link regular file')
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield directory
        finally:
            os.close(fd)
    finally:
        directory.close()


def window_read(directory):
    data, mode = directory.read_regular(WINDOW.name)
    return json.loads(data), {'path': str(WINDOW), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'mode': mode}


def window_write(directory, value, mode):
    directory.verify_location()
    temporary = WINDOW.name + '.' + uuid.uuid4().hex
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=directory.fd)
    try:
        with os.fdopen(fd, 'w') as handle:
            json.dump(value, handle, indent=2, sort_keys=True); handle.write('\n'); handle.flush()
            os.fchmod(handle.fileno(), mode); os.fsync(handle.fileno())
        os.replace(temporary, WINDOW.name, src_dir_fd=directory.fd, dst_dir_fd=directory.fd)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary, dir_fd=directory.fd)
        raise
    directory.sync()
    directory.verify_location()


def reserve(holder, attempt, token, launch_record):
    """Returns the pins of reservation-intent.json and reservation.json (both kept in memory for conclusion)."""
    with window_locked() as directory:
        value, prior = window_read(directory)
        require(value['status'] == 'released', 'Do not take a different active reservation')
        intent = attempt.write_json('reservation-intent.json', {'at': now(), 'token': token, 'launch': launch_record, 'prior': prior,
                                                                'holder_task': holder, 'candidate': str(attempt.path), 'label': LABEL})
        at = now()
        reason = 'Claude lead engineering scratch attempt (reviewed frame v5). ' + LABEL
        value.setdefault('reservation_history', []).append({'at': at, 'holder_task': holder, 'candidate': str(attempt.path),
                                                            'reservation_token': token, 'reason': reason, 'prior': prior})
        value.update(status='reserved', holder_task=holder, reserved_at=at, updated_at=at, candidate=str(attempt.path),
                     reservation_token=token, reason=reason, pending_request={'state': 'WORLDLINE_CLAUDE_SCRATCH_ATTEMPT'})
        window_write(directory, value, prior['mode'])
        reservation = attempt.write_json('reservation.json', {'at': at, 'token': token, 'prior': prior,
                                                              'current': window_read(directory)[1]})
        return intent, reservation


def owns_window(holder, attempt_path, token):
    with window_locked() as directory:
        value, _row = window_read(directory)
        return (value.get('status') == 'reserved' and value.get('holder_task') == holder
                and value.get('candidate') == str(attempt_path) and value.get('reservation_token') == token)


def release(holder, attempt, token, terminal, errors):
    """Release under the lock only while this attempt still holds the window. The window replacement is the commit
    point: a failure before it raises (nothing released); after it, the post-release record is retained without
    raising. Returns {'committed': True, 'record': pin or None}."""
    with window_locked() as directory:
        value, prior = window_read(directory)
        require(value['status'] == 'reserved' and value['holder_task'] == holder and value['candidate'] == str(attempt.path)
                and value.get('reservation_token') == token, 'coordination ownership changed; do not overwrite')
        attempt.write_json('release-intent.json', {'at': now(), 'token': token, 'terminal': terminal, 'prior': prior})
        at = now()
        reason = 'Claude scratch attempt ended; every owned participant observed terminal. ' + LABEL
        value.setdefault('release_history', []).append({'at': at, 'reason': reason, 'evidence': terminal,
                                                        'candidate': str(attempt.path), 'reservation_token': token})
        value.pop('reservation_token', None)
        value.update(status='released', released_at=at, updated_at=at, reason=reason,
                     pending_request={'state': 'WORLDLINE_CLAUDE_SCRATCH_ENDED_WINDOW_RELEASED'})
        window_write(directory, value, prior['mode'])
        current = guarded(errors, 'window reread after release', lambda: window_read(directory)[1])
        record = retain(attempt, 'window-release.json', {'at': at, 'token': token, 'prior': prior, 'current': current,
                                                         'terminal': terminal}, errors)
        return {'committed': True, 'record': record}


# ---------------------------------------------------------------- owned participants

def ancestors():
    chain, pid = set(), os.getpid()
    while pid > 1 and pid not in chain:
        chain.add(pid)
        try:
            pid = int(Path('/proc', str(pid), 'stat').read_text().rsplit(')', 1)[1].split()[1])
        except (FileNotFoundError, ProcessLookupError, ValueError, IndexError):
            break
    return chain


def processes_naming(marker):
    excluded = ancestors()
    found = []
    for entry in os.listdir('/proc'):
        if not entry.isdigit() or int(entry) in excluded:
            continue
        try:
            command_line = Path('/proc', entry, 'cmdline').read_bytes()
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        if marker.encode() in command_line:
            found.append({'pid': int(entry), 'cmdline': command_line.replace(b'\0', b' ').decode(errors='replace')})
    return found


CHILD_RECORD_RE = r'child-(?:wrapper|start|wait|refusal|cleanup)\.json(?:\.retry-[0-9a-f]{12})?'


def owned_terminal(attempt, environment, unit, launched, launcher_pid, errors):
    """Every owned participant observed terminal: the scope unit ended, its cgroup absent or empty, every recorded
    participant pid (launcher, child wrapper, target) gone, and no process naming the attempt. Child records are
    read raw: an unreadable or unparseable one leaves its participant unresolved, so the observation is not
    terminal and the window stays reserved (V4-B02)."""
    show = invoke(['/usr/bin/systemctl', '--user', 'show', unit] +
                  [v for key in ('LoadState', 'ActiveState', 'SubState', 'MainPID', 'ControlGroup', 'Result') for v in ('-p', key)],
                  environment, attempt, 'owned-scope-show.json')
    properties = dict(line.split('=', 1) for line in show.stdout.splitlines() if '=' in line)
    group = properties.get('ControlGroup', '')
    if group:
        directory = Path('/sys/fs/cgroup') / group.lstrip('/')
        if not os.path.lexists(directory):
            cgroup = 'ABSENT'
        else:
            try:
                cgroup = 'EMPTY' if not (directory / 'cgroup.procs').read_text().split() else 'NONEMPTY'
            except OSError:
                cgroup = 'UNAVAILABLE'
    else:
        cgroup = 'NOT_REPORTED'
    rows, unresolved = {}, []
    for name in sorted(os.listdir(attempt.fd)):
        if re.fullmatch(CHILD_RECORD_RE, name) is None:
            continue
        value, raw = read_record(attempt, name, errors)
        if value is None:
            unresolved.append(raw)
        else:
            rows[name] = value
    pids = sorted({row['pid'] for row in rows.values() if isinstance(row.get('pid'), int) and not isinstance(row.get('pid'), bool)}
                  | ({launcher_pid} if launcher_pid else set()))
    absent = {pid: not os.path.lexists('/proc/%d' % pid) for pid in pids}
    naming = processes_naming(attempt.path.name)
    unit_ended = show.returncode == 0 and (properties.get('LoadState') == 'not-found'
                                           or properties.get('ActiveState') in ('inactive', 'failed'))
    terminal = (unit_ended and cgroup in ('ABSENT', 'EMPTY', 'NOT_REPORTED') and all(absent.values()) and not naming
                and (not launched or launcher_pid is not None) and not unresolved)
    return terminal, {'unit': unit, 'properties': properties, 'cgroup': cgroup, 'launched': launched,
                      'launcher_pid': launcher_pid, 'participant_pids_absent': absent, 'processes_naming_attempt': naming,
                      'unresolved_participant_records': unresolved}


# ---------------------------------------------------------------- admission shared by parent, child and conclusion

def final_stream_sync(attempt):
    """fsync every raw stream of the attempt through read-only descriptors whose entries still name them; called only
    after the owned scope and every participant were observed terminal, so no owned writer remains."""
    synced = {}
    for name in ('scope.stdout', 'scope.stderr', 'child.stdout', 'child.stderr'):
        if attempt.has(name):
            fd = os.open(name, O_FILE, dir_fd=attempt.fd)
            try:
                info = os.fstat(fd)
                require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'raw stream is not a single-link regular file: ' + name)
                os.fsync(fd)
                entry = os.stat(name, dir_fd=attempt.fd, follow_symlinks=False)
                require(stat_key(entry) == stat_key(os.fstat(fd)), 'raw stream entry changed: ' + name)
                synced[name] = {'bytes': info.st_size}
            finally:
                os.close(fd)
    attempt.sync()
    return synced


def admission(run, materialization, out, suffix, source, snapshot):
    """Frame admission, the materialization verified through the held source/snapshot descriptors, and the complete
    tool/data/ELF/vendor/runtime/manager identities. Returns (environment, inventory, source observation)."""
    inventory = frame_admitted()
    observed = verify_materialization(run, materialization, source, snapshot)
    modules = inventory_modules(inventory)
    tool_spec, runtime_spec, runtime_expected, environment = specifications(inventory, run.path / 'source')
    identities(inventory, modules, out, environment, tool_spec, runtime_spec, runtime_expected, suffix)
    return environment, inventory, observed


def open_run(name):
    require(re.fullmatch(NAME_RE, name) is not None, 'invalid run name')
    runs = Dir.anchor(RUNS)
    try:
        run = runs.child(name)
    finally:
        runs.close()
    try:
        data, record_pin = run_record(run)
        materialization = json.loads(data)
        require(materialization.get('schema') == 'claude-scratch-materialization-v5' and materialization.get('run') == str(run.path),
                'materialization profile')
    except BaseException:
        run.close()
        raise
    return run, materialization, record_pin


def raising_handler(state):
    def handler(number, _frame):
        target = state.get('process')
        if target is not None and target.poll() is None:
            target.send_signal(signal.SIGTERM)
        raise Interrupted('signal %d' % number)
    return handler


def wait_blocked(process, notes, poll_seconds=0.5):
    """The actual exit status, collected with SIGNALS blocked: a signal is received synchronously by sigtimedwait
    and forwarded to the process as SIGTERM, so no asynchronous exception can interrupt waiting or recording. A
    failure to wait is returned as an unresolved record (returncode None) instead of raising."""
    try:
        while True:
            code = process.poll()
            if code is not None:
                return code, None
            info = signal.sigtimedwait(SIGNALS, poll_seconds)
            if info is not None:
                notes.append({'at': now(), 'signal': info.si_signo, 'action': 'SIGTERM forwarded; waiting for actual exit'})
                with contextlib.suppress(ProcessLookupError):
                    process.send_signal(signal.SIGTERM)
    except BaseException as caught:
        return None, {'type': type(caught).__name__, 'message': str(caught), 'unresolved': True}


def pending_handled():
    """Handled signals queued while blocked, each consumed and returned so it is recorded, never silently left
    pending (v4 N09). Called with SIGNALS blocked: before a spawn (any result refuses the spawn) and after a wait."""
    found = []
    while set(signal.sigpending()) & set(SIGNALS):
        info = signal.sigtimedwait(SIGNALS, 0)
        if info is None:
            break
        found.append({'at': now(), 'signal': info.si_signo})
    return found


def spawn(argv, environment, stdin, stdout, stderr, directory, core_zero=False):
    """Start a process whose working directory is set by fchdir on an anchored descriptor (no pathname cwd). The
    caller has blocked SIGNALS and keeps them blocked until it exits (synchronous handling via wait_blocked); only
    the new process unblocks them, before exec."""
    def setup():
        os.fchdir(directory.fd)
        if core_zero:
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        signal.pthread_sigmask(signal.SIG_UNBLOCK, SIGNALS)
    return subprocess.Popen(argv, env=environment, stdin=stdin, stdout=stdout, stderr=stderr, preexec_fn=setup)


def started_by_dispatch(name, action, args):
    parent = os.getppid()
    words = Path('/proc', str(parent), 'cmdline').read_bytes().split(b'\0')
    if words and words[-1] == b'':
        words.pop()
    expected = [PYTHON.encode(), b'-B', str(FRAME / 'scratch.py').encode(), b'dispatch', name.encode(), action.encode()] + \
        [a.encode() for a in args]
    require(words == expected, "run must be started by this frame's dispatch verb with the same run/action/arguments")


def refusal_record(attempt, stage, caught, errors):
    """A refusal before reservation and launch, retained in the attempt with SIGNALS blocked; nothing was reserved
    or started. The caller re-raises."""
    with contextlib.suppress(BaseException):
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    retain(attempt, 'refusal.json', {'at': now(), 'stage': stage, 'error': failure_row(stage, caught),
                                     'traceback': traceback.format_exc(), 'reserved': False, 'launched': False,
                                     'meaning': 'refused before reservation and launch; nothing was started. ' + LABEL}, errors)


def run(name, action, args):
    started_by_dispatch(name, action, args)
    state = {}
    for number in SIGNALS:
        signal.signal(number, raising_handler(state))
    run_handle, materialization, record_pin = open_run(name)
    source = run_handle.child('source')
    snapshot = run_handle.child('overlay-snapshot')
    argv = command(action, args, materialization)
    stamp = stamp_now()
    attempts = run_handle.child('attempts', create=not run_handle.has('attempts'))
    try:
        attempt = attempts.child(stamp, create=True)
    finally:
        attempts.close()
    errors = []
    try:
        claude_lead = fresh_lead('scratch-run', run_handle.path, attempt, 'lead-observation-run.json')
        holder = claude_lead.LEAD_ID
        environment, inventory, observed = admission(run_handle, materialization, attempt, 'parent', source, snapshot)
        first = sample(attempt, environment, 'preflight')
        storage_reserve = first['configured_local_reserve_bytes']
        require(invoke(['project-vault', 'pin', str(run_handle.path)], environment, attempt, 'vault-pin.json').returncode == 0, 'vault pin')
        require(invoke(['project-vault', 'status'], environment, attempt, 'vault-status.json').returncode == 0, 'vault status')
        unit = 'claude-worldline-scratch-' + name + '-' + stamp
        token = uuid.uuid4().hex
        for handle in (run_handle, attempt, source, snapshot):
            handle.verify_location()
        seal = {'run': run_handle.identity(), 'attempt': attempt.identity(), 'source': source.identity(),
                'overlay-snapshot': snapshot.identity(), 'source_tree': observed['identities']}
        template = ['/usr/bin/systemd-run', '--user', '--scope', '--unit=' + unit, '-p', 'MemoryMax=8G',
                    '-p', 'MemorySwapMax=0', PYTHON, '-B', str(FRAME / 'scratch.py'), 'child', name, stamp]
        launch = {'at': now(), 'action': action, 'args': args, 'child_argv': argv, 'cwd': str(run_handle.path / 'source'),
                  'directory_identities': seal, 'unit': unit + '.scope', 'scope_argv_template': template,
                  'scope_argv_tail': ['sha256 of this launch.json', 'sha256 of admission.json'],
                  'environment': environment, 'frame_inventory': inventory['__pin__'], 'review': pin(REVIEW / 'review.json'),
                  'adoption': pin(ADOPTION), 'materialization': record_pin, 'storage_reserve_bound': storage_reserve,
                  'holder': holder, 'label': LABEL}
        launch_record = attempt.write_json('launch.json', launch)
    except BaseException as caught:
        refusal_record(attempt, 'parent admission', caught, errors)
        raise
    ctx = types.SimpleNamespace(run_handle=run_handle, attempt=attempt, source=source, snapshot=snapshot, unit=unit,
                                holder=holder, token=token, environment=environment, launch=launch, seal=seal,
                                pins={'launch': launch_record}, scope_code=None, error=None, notes=[], launched=False,
                                launcher_pid=None, action=action, args=args, argv=argv, record_pin=record_pin, errors=errors)
    process = out_fd = err_fd = None
    try:
        ctx.pins['intent'], ctx.pins['reservation'] = reserve(holder, attempt, token, launch_record)
        gate = memory_gate(inventory, attempt, environment, storage_reserve)
        ctx.pins['admission'] = attempt.write_json('admission.json', {
            'at': now(), 'memory_gate': gate, 'reservation': ctx.pins['reservation'], 'launch': launch_record,
            'label': 'local launch-gate record only; ' + LABEL})
        scope_argv = template + [launch_record['sha256'], ctx.pins['admission']['sha256']]
        ctx.pins['launcher_intent'] = attempt.write_json('launcher-intent.json', {'at': now(), 'scope_argv': scope_argv})
        out_fd, err_fd = attempt.open_stream('scope.stdout'), attempt.open_stream('scope.stderr')
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)   # stays blocked until this process exits
        early = pending_handled()
        if early:
            ctx.notes.extend(dict(row, action='pending before the launcher spawn; not started') for row in early)
            raise Interrupted('handled signal pending before the launcher spawn')
        source.verify_location()
        process = spawn(scope_argv, environment, subprocess.DEVNULL, out_fd, err_fd, source, core_zero=True)
        state['process'] = process
        ctx.launched, ctx.launcher_pid = True, process.pid
        ctx.pins['launcher_start'] = retain(attempt, 'launcher-start.json', {'at': now(), 'pid': process.pid}, errors)
        ctx.scope_code, wait_error = wait_blocked(process, ctx.notes)
        if wait_error is not None:
            ctx.error = wait_error
    except BaseException as caught:
        ctx.error = {'type': type(caught).__name__, 'message': str(caught), 'traceback': traceback.format_exc()}
    finally:
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        if process is not None and ctx.scope_code is None:
            ctx.scope_code, wait_error = wait_blocked(process, ctx.notes)
            if wait_error is not None and ctx.error is None:
                ctx.error = wait_error
        late = guarded(errors, 'pending signals after the launcher wait', pending_handled) or []
        ctx.notes.extend(dict(row, action='received after the launcher exit; recorded') for row in late)
        ctx.pins['launcher_wait'] = retain(attempt, 'launcher-wait.json', {
            'at': now(), 'launched': ctx.launched, 'pid': ctx.launcher_pid, 'returncode': ctx.scope_code,
            'unresolved': ctx.launched and ctx.scope_code is None, 'error': ctx.error, 'interrupts': ctx.notes,
            'meaning': 'actual subprocess.Popen wait of the systemd-run --scope launcher, recorded before any cleanup. ' + LABEL},
            errors)
        for stage, fd in (('close scope.stdout', out_fd), ('close scope.stderr', err_fd)):
            if fd is not None:
                guarded(errors, stage, close_stream, fd)
        if ctx.error is None and ctx.notes:
            ctx.error = {'type': 'Interrupted', 'message': 'interrupted during the launcher wait', 'traceback': ''}
        try:
            conclude(ctx)
        except SystemExit:
            raise
        except BaseException as caught:
            errors.append(failure_row('conclude', caught))
            retain(attempt, 'conclude-failure.json', {
                'at': now(), 'error': failure_row('conclude', caught), 'traceback': traceback.format_exc(),
                'launcher_wait': ctx.scope_code, 'record_errors': errors,
                'release_state': 'not established by this record; window-release.json exists only if a release committed',
                'resolution': 'observe the window and every participant, then resolve explicitly; this frame has no late collector'},
                errors)
            raise SystemExit(1)


def conclude(ctx):
    """Runs with SIGNALS blocked; every step is guarded so the terminal records are always attempted (V4-B02). Order:
    observe every owned participant terminal FIRST; then fsync the raw streams; compare every retained launch-gate
    record with the parent's in-memory pin and use the in-memory directory seal, never re-read run-local data, as the
    expectation (V4-B03); re-verify the held directories' locations and the attempt-bound materialization through the
    held descriptors; copy the report; rerun the identities; read the child records raw (unparseable bytes are
    reported, never trusted); decide; record; release only on an observed terminal state with no unresolved
    participant record."""
    errors = ctx.errors
    observation = guarded(errors, 'owned-terminal observation', owned_terminal, ctx.attempt, ctx.environment,
                          ctx.unit + '.scope', ctx.launched, ctx.launcher_pid, errors)
    terminal_ok, owned = observation if observation is not None else (False, {'observation_error': errors[-1]})
    streams = None
    if terminal_ok:
        streams = guarded(errors, 'stream-sync', final_stream_sync, ctx.attempt)
    else:
        errors.append({'stage': 'stream-sync', 'type': 'Unresolved',
                       'message': 'owned participants not all observed terminal; raw streams may still be written'})
    drift = {}
    for key in ('launch', 'intent', 'reservation', 'admission', 'launcher_intent', 'launcher_start', 'launcher_wait'):
        expected = ctx.pins.get(key)
        if expected is None:
            continue
        try:
            data, mode = ctx.attempt.read_regular(existing_name(Path(expected['path']).name))
            current = {'path': expected['path'], 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'mode': mode}
            if current != expected:
                drift[key] = {'expected': expected, 'current': current}
        except BaseException as caught:
            drift[key] = {'expected': expected, 'error': failure_row('reread ' + key, caught)}
    if drift:
        errors.append({'stage': 'launch-seal', 'type': 'Drift',
                       'message': 'retained launch-gate records differ from their in-memory pins: ' + ', '.join(sorted(drift))})
    provenance_unchanged = False
    try:
        for handle in (ctx.run_handle, ctx.attempt, ctx.source, ctx.snapshot):
            handle.verify_location()
        held = {'run': ctx.run_handle.identity(), 'attempt': ctx.attempt.identity(), 'source': ctx.source.identity(),
                'overlay-snapshot': ctx.snapshot.identity()}
        require(held == {key: ctx.seal[key] for key in held}, 'a held directory is not the one sealed at launch')
        data, current = run_record(ctx.run_handle)
        require(current == ctx.record_pin == ctx.launch['materialization'], 'materialization record changed since launch')
        observed = verify_materialization(ctx.run_handle, json.loads(data), ctx.source, ctx.snapshot)
        sealed = ctx.seal['source_tree']
        replaced = sorted(relative for relative, row in sealed.items() if observed['identities'].get(relative) != row)
        outside = sorted(relative for relative in observed['identities'] if relative not in sealed and not in_partition(relative))
        require(not replaced, 'directories sealed at launch were replaced or removed: ' + repr(replaced[:20]))
        require(not outside, 'new directories outside the generated output partitions: ' + repr(outside[:20]))
        provenance_unchanged = not drift
    except BaseException as caught:
        errors.append(failure_row('materialization and directory seal', caught))
    report_row = None
    start, start_raw = read_record(ctx.attempt, 'child-start.json', errors)
    if (start is not None or start_raw is not None) and ctx.action.startswith('prove'):
        try:
            report_dir = ctx.source.descend('obj/core/gnatprove')
            try:
                if report_dir.has('gnatprove.out'):
                    data, info = report_dir.read_observed('gnatprove.out')
                    report_row = ctx.attempt.write_bytes('gnatprove.out', data)
                    report_row['source_mtime_ns'] = info.st_mtime_ns
            finally:
                report_dir.close()
        except BaseException as caught:
            errors.append(failure_row('report', caught))
    after_error = None
    try:
        inventory = frame_admitted()
        modules = inventory_modules(inventory)
        tool_spec, runtime_spec, runtime_expected, _env = specifications(inventory, ctx.run_handle.path / 'source')
        identities(inventory, modules, ctx.attempt, ctx.environment, tool_spec, runtime_spec, runtime_expected, 'after')
    except BaseException as caught:
        after_error = failure_row('post-identity', caught)
    child_wait, child_wait_raw = read_record(ctx.attempt, 'child-wait.json', errors)
    child_ok = (child_wait is not None and child_wait.get('started') is True and child_wait.get('returncode') == 0
                and not child_wait.get('interrupted') and child_wait.get('error') is None
                and not child_wait.get('record_errors_before_wait_record'))
    success = (ctx.launched and ctx.scope_code == 0 and child_ok and ctx.error is None and after_error is None
               and provenance_unchanged is True and terminal_ok and not errors)
    value = {'schema': 'claude-scratch-run-result-v5', 'at': now(), 'run': str(ctx.run_handle.path), 'action': ctx.action,
             'args': ctx.args, 'child_argv': ctx.argv, 'launched': ctx.launched, 'scope_wait': ctx.scope_code,
             'launcher_wait_interrupts': ctx.notes, 'child_wait': child_wait, 'child_wait_raw': child_wait_raw,
             'error': ctx.error, 'post_identity_error': after_error, 'record_errors': list(errors),
             'launch_seal_drift': drift, 'materialization_unchanged': provenance_unchanged, 'owned_terminal': owned,
             'owned_terminal_observed': terminal_ok, 'final_stream_sync': streams, 'gnatprove_out': report_row,
             'success': success, 'label': LABEL}

    def downgrade(record):
        record['success'] = False
    committed_errors = len(errors)
    result = retain(ctx.attempt, 'result.json', value, errors, downgrade)
    released = False
    if terminal_ok:
        try:
            if owns_window(ctx.holder, ctx.attempt.path, ctx.token):
                released = release(ctx.holder, ctx.attempt, ctx.token, result, errors)['committed']
            else:
                errors.append({'stage': 'release', 'type': 'NotOwner',
                               'message': 'the window is not held by this attempt at conclusion; nothing released'})
        except BaseException as caught:
            errors.append(failure_row('release', caught))
            retain(ctx.attempt, 'release-failure.json', {
                'at': now(), 'error': failure_row('release', caught),
                'resolution': 'the window state is unknown after this failure: observe it and resolve explicitly; this frame '
                              'has no late collector'}, errors)
    else:
        retain(ctx.attempt, 'release-withheld.json', {
            'at': now(), 'reason': 'owned participants not all observed terminal, or a participant record is unresolved; '
                                   'the window stays reserved',
            'owned_terminal': owned,
            'resolution': 'explicit operator-visible manual resolution after observing every participant terminal; this '
                          'frame has no late collector'}, errors)
    if len(errors) > committed_errors:
        success = False
        retain(ctx.attempt, 'conclude-errors.json', {'at': now(), 'errors_after_result': errors[committed_errors:],
                                                     'released': released}, errors)
    for handle in (ctx.source, ctx.snapshot, ctx.attempt, ctx.run_handle):
        guarded(errors, 'close ' + str(handle.path), handle.close)
    print(json.dumps({'result': result, 'scope_wait': ctx.scope_code, 'child_wait': child_wait and child_wait.get('returncode'),
                      'released': released, 'success': success, 'error': ctx.error and ctx.error['message'],
                      'record_errors': len(errors), 'label': LABEL}, default=str), flush=True)
    raise SystemExit(0 if success and released else 1)


def child(name, stamp, launch_sha, admission_sha):
    state = {}
    for number in SIGNALS:
        signal.signal(number, raising_handler(state))
    require(re.fullmatch(STAMP_RE, stamp) is not None and re.fullmatch(SHA_RE, launch_sha) is not None
            and re.fullmatch(SHA_RE, admission_sha) is not None, 'invalid attempt stamp or launch seal')
    run_handle, materialization, record_pin = open_run(name)
    attempts = run_handle.child('attempts')
    try:
        attempt = attempts.child(stamp)
    finally:
        attempts.close()
    errors, held, streams = [], [run_handle, attempt], []
    try:
        attempt.write_json('child-wrapper.json', {'at': now(), 'pid': os.getpid()})
        launch_bytes, launch_mode = attempt.read_regular('launch.json')
        require(hashlib.sha256(launch_bytes).hexdigest() == launch_sha, 'launch record differs from the seal carried by the launcher argv')
        launch = json.loads(launch_bytes)
        words = Path('/proc/self/cmdline').read_bytes().split(b'\0')
        if words and words[-1] == b'':
            words.pop()
        template = launch['scope_argv_template']
        require(words == [w.encode() for w in template[template.index(PYTHON):] + [launch_sha, admission_sha]],
                'this process is not the sealed launch command')
        intent = json.loads(attempt.read_bytes('reservation-intent.json'))
        require(intent['launch'] == {'path': str(attempt.path / 'launch.json'), 'sha256': launch_sha,
                                     'bytes': len(launch_bytes), 'mode': launch_mode}, 'launch record differs from the sealed reservation intent')
        gate_bytes = attempt.read_bytes('admission.json')
        require(hashlib.sha256(gate_bytes).hexdigest() == admission_sha, 'admission record differs from the seal carried by the launcher argv')
        gate = json.loads(gate_bytes)
        require(gate['launch'] == intent['launch'], 'admission record is not bound to this launch')
        seal = launch['directory_identities']
        require(run_handle.identity() == seal['run'] and attempt.identity() == seal['attempt'], 'run/attempt directory differs from the launch seal')
        source = run_handle.child('source')
        held.append(source)
        snapshot = run_handle.child('overlay-snapshot')
        held.append(snapshot)
        require(source.identity() == seal['source'] and snapshot.identity() == seal['overlay-snapshot'],
                'source/snapshot directory differs from the launch seal')
        for handle in held:
            handle.verify_location()
        claude_lead = fresh_lead('scratch-child', run_handle.path, attempt, 'lead-observation-child.json')
        require(launch['holder'] == claude_lead.LEAD_ID == intent['holder_task'], 'holder identity')
        require(owns_window(claude_lead.LEAD_ID, attempt.path, intent['token']), 'this attempt does not own the shared window')
        environment, inventory, observed = admission(run_handle, materialization, attempt, 'child', source, snapshot)
        require(observed['identities'] == seal['source_tree'], 'source tree directories differ from the launch seal')
        require(launch['frame_inventory'] == inventory['__pin__'] and launch['review'] == pin(REVIEW / 'review.json')
                and launch['adoption'] == pin(ADOPTION) and launch['materialization'] == record_pin,
                'sealed frame/review/adoption/materialization pins changed')
        require(environment == launch['environment'], 'recomputed environment differs from the sealed launch environment')
        observed_environment = dict(os.environ)
        invocation = observed_environment.pop('INVOCATION_ID', None)
        require(invocation is not None and re.fullmatch(r'[0-9a-f]{32}', invocation) is not None, 'scope invocation id')
        require(observed_environment == environment, 'child process environment differs from the recomputed environment')
        require(gate['memory_gate']['immediate']['MemAvailable_observed_kB'] >= MIN_MEM_AVAILABLE_KB, 'parent memory gate')
        final = sample(attempt, environment, 'child-final', launch['storage_reserve_bound'], siblings_allowed_unit=launch['unit'])
        require(final['MemAvailable_observed_kB'] >= MIN_MEM_AVAILABLE_KB,
                'final post-identity memory observation below the unchanged fixed minimum; launch refused')
        require(launch['cwd'] == str(run_handle.path / 'source'), 'launch cwd')
        require(command(launch['action'], launch['args'], materialization) == launch['child_argv'], 'argv not allowlisted')
        membership = Path('/proc/self/cgroup').read_text()
        relative = next(x.split(':', 2)[2] for x in membership.splitlines() if x.startswith('0::'))
        group = Path('/sys/fs/cgroup') / relative.lstrip('/')
        limits = {'at': now(), 'pid': os.getpid(), 'membership': membership,
                  'memory.max': (group / 'memory.max').read_text().strip(),
                  'memory.swap.max': (group / 'memory.swap.max').read_text().strip(),
                  'core_soft_hard': list(resource.getrlimit(resource.RLIMIT_CORE))}
        attempt.write_json('effective-limits.json', limits)
        require(limits['memory.max'] == '8589934592' and limits['memory.swap.max'] == '0' and limits['core_soft_hard'] == [0, 0],
                'owned scope limits')
        require(relative.rstrip().endswith('/' + launch['unit']), 'not inside the owned scope')
        baseline_tools = frame_json(inventory, 'baselines/action-baseline.json')['tool_inventory']
        executables = [row for row in baseline_tools['executables'] if row['path'] == launch['child_argv'][0]]
        require(len(executables) == 1 and sha(launch['child_argv'][0]) == executables[0]['sha256'], 'target executable identity')
        again = verify_materialization(run_handle, materialization, source, snapshot)
        require(again['identities'] == seal['source_tree'], 'source tree directories changed before the spawn')
        for handle in held:
            handle.verify_location()
        streams.append(attempt.open_stream('child.stdout'))
        streams.append(attempt.open_stream('child.stderr'))
    except BaseException as caught:
        with contextlib.suppress(BaseException):
            signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        retain(attempt, 'child-refusal.json', {'at': now(), 'pid': os.getpid(), 'error': failure_row('child admission', caught),
                                               'traceback': traceback.format_exc(), 'target_started': False,
                                               'meaning': 'refused before the target spawn; nothing was started. ' + LABEL}, errors)
        for fd in streams:
            guarded(errors, 'close child stream', close_stream, fd)
        for handle in reversed(held):
            guarded(errors, 'close', handle.close)
        raise SystemExit(1)
    out_fd, err_fd = streams
    code, notes, failure, process = None, [], None, None
    signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)   # stays blocked until this process exits
    try:
        early = pending_handled()
        if early:
            notes.extend(dict(row, action='pending before the target spawn; not started') for row in early)
            raise Interrupted('handled signal pending before the target spawn')
        process = spawn(launch['child_argv'], environment, subprocess.DEVNULL, out_fd, err_fd, source)
        state['process'] = process
        retain(attempt, 'child-start.json', {'at': now(), 'pid': process.pid, 'argv': launch['child_argv']}, errors)
    except BaseException as caught:
        failure = {'type': type(caught).__name__, 'message': str(caught), 'traceback': traceback.format_exc()}
    finally:
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        if process is not None:
            code, wait_error = wait_blocked(process, notes)
            if wait_error is not None and failure is None:
                failure = wait_error
        late = guarded(errors, 'pending signals after the target wait', pending_handled) or []
        notes.extend(dict(row, action='received after the target exit; recorded') for row in late)
        retain(attempt, 'child-wait.json', {
            'at': now(), 'pid': process.pid if process is not None else None, 'argv': launch['child_argv'],
            'started': process is not None, 'returncode': code, 'unresolved': process is not None and code is None,
            'interrupted': notes, 'error': failure, 'record_errors_before_wait_record': list(errors),
            'meaning': 'actual subprocess.Popen wait of the target, recorded before any cleanup. ' + LABEL}, errors)
        cleanup = []
        guarded(cleanup, 'close child.stdout', close_stream, out_fd)
        guarded(cleanup, 'close child.stderr', close_stream, err_fd)
        if cleanup:
            errors.extend(cleanup)
            retain(attempt, 'child-cleanup.json', {
                'at': now(), 'pid': os.getpid(), 'errors': cleanup,
                'meaning': 'raw stream close/fsync failed after the target wait was recorded; durable streams are not '
                           'claimed. ' + LABEL}, errors)
        for handle in reversed(held):
            guarded(errors, 'close', handle.close)
    raise SystemExit(code if code is not None and failure is None and not notes and not errors else (code or 1))


def dispatch(name, action, args):
    """Lead entry point (replaces v3 dispatch.py): confined to RUNS/NAME/dispatch/STAMP through anchored,
    location-verified descriptors; forwards only lead-written one-line answer-N.json files from that directory. The
    actual run wait is recorded first; stream closes and identities are guarded and aggregated into terminal.json
    (V4-B02)."""
    state = {}
    for number in SIGNALS:
        signal.signal(number, raising_handler(state))
    require(action in ACTIONS, 'action not in the reviewed allowlist')
    run_handle, materialization, _record_pin = open_run(name)
    command(action, args, materialization)
    stamp = stamp_now()
    dispatches = run_handle.child('dispatch', create=not run_handle.has('dispatch'))
    try:
        here = dispatches.child(stamp, create=True)
    finally:
        dispatches.close()
    argv = [PYTHON, '-B', str(FRAME / 'scratch.py'), 'run', name, action] + args
    errors = []
    out_fd, err_fd = here.open_stream('run.stdout'), here.open_stream('run.stderr')
    frame_dir = Dir.anchor(FRAME)
    print(json.dumps({'dispatch_dir': str(here.path), 'answers': 'lead writes answer-N.json (exactly one line) here',
                      'label': LABEL}), flush=True)
    forwarded, notes, code, failure, process = [], [], None, None, None
    signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)   # stays blocked until this process exits
    try:
        early = pending_handled()
        if early:
            notes.extend(dict(row, action='pending before the run spawn; not started') for row in early)
            raise Interrupted('handled signal pending before the run spawn')
        frame_dir.verify_location()
        process = spawn(argv, None, subprocess.PIPE, out_fd, err_fd, frame_dir)
        state['process'] = process
        retain(here, 'started.json', {'at': now(), 'pid': process.pid, 'driver_pid': os.getpid(), 'argv': argv,
                                      'cwd': str(FRAME), 'stdin': 'pipe held by dispatch until the run exits'}, errors)
        number = 1
        while process.poll() is None:
            answer = 'answer-%d.json' % number
            if here.has(answer):
                time.sleep(0.2)
                line = here.read_bytes(answer)
                require(line.endswith(b'\n') and line.count(b'\n') == 1, 'answer must be exactly one line')
                try:
                    process.stdin.write(line)
                    process.stdin.flush()
                    forwarded.append({'n': number, 'at': now(), 'sha256': hashlib.sha256(line).hexdigest()})
                except BrokenPipeError as caught:
                    forwarded.append({'n': number, 'at': now(), 'error': repr(caught)})
                number += 1
            info = signal.sigtimedwait(SIGNALS, 1.0)
            if info is not None:
                notes.append({'at': now(), 'signal': info.si_signo, 'action': 'SIGTERM forwarded to the run'})
                with contextlib.suppress(ProcessLookupError):
                    process.send_signal(signal.SIGTERM)
    except BaseException as caught:
        failure = {'type': type(caught).__name__, 'message': str(caught), 'traceback': traceback.format_exc()}
    finally:
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        if process is not None:
            code, wait_error = wait_blocked(process, notes)
            if wait_error is not None and failure is None:
                failure = wait_error
        late = guarded(errors, 'pending signals after the run wait', pending_handled) or []
        notes.extend(dict(row, action='received after the run exit; recorded') for row in late)
        retain(here, 'run-wait.json', {
            'at': now(), 'pid': process.pid if process is not None else None, 'argv': argv, 'started': process is not None,
            'actual_run_wait_returncode': code, 'unresolved': process is not None and code is None, 'interrupts': notes,
            'error': failure, 'forwarded_answers': forwarded,
            'meaning': 'actual subprocess.Popen wait of the run verb, recorded before any cleanup. ' + LABEL}, errors)
        if process is not None:
            try:
                process.stdin.close()
            except BrokenPipeError as caught:
                notes.append({'at': now(), 'stdin_close': repr(caught), 'meaning': 'the run had exited; nothing was unforwarded'})
            except BaseException as caught:
                errors.append(failure_row('close run stdin', caught))
        guarded(errors, 'close run.stdout', close_stream, out_fd)
        guarded(errors, 'close run.stderr', close_stream, err_fd)
        guarded(errors, 'close frame directory', frame_dir.close)
        stream_rows = {stream: guarded(errors, 'identity ' + stream, here.ident, stream) for stream in ('run.stdout', 'run.stderr')}
        retain(here, 'terminal.json', {
            'at': now(), 'pid': process.pid if process is not None else None, 'argv': argv,
            'actual_run_wait_returncode': code, 'forwarded_answers': forwarded, 'interrupts': notes, 'error': failure,
            'stdout': stream_rows['run.stdout'], 'stderr': stream_rows['run.stderr'], 'record_errors': list(errors),
            'truth_boundary': 'Actual run wait observed by the dispatch verb. ' + LABEL}, errors)
        guarded(errors, 'close dispatch directory', here.close)
        guarded(errors, 'close run directory', run_handle.close)
    print(json.dumps({'run_wait': code, 'forwarded': len(forwarded), 'error': failure and failure['message'],
                      'record_errors': len(errors)}), flush=True)
    raise SystemExit(code if code is not None and not errors else (code or 1))


if __name__ == '__main__':
    os.umask(0o077)
    verb = sys.argv[1] if len(sys.argv) > 1 else ''
    if verb == 'freeze' and len(sys.argv) == 2:
        freeze()
    elif verb == 'adopt' and len(sys.argv) == 4:
        adopt(sys.argv[2], sys.argv[3])
    elif verb == 'materialize' and len(sys.argv) == 4:
        materialize(sys.argv[2], sys.argv[3])
    elif verb == 'dispatch' and len(sys.argv) >= 4:
        dispatch(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif verb == 'run' and len(sys.argv) >= 4:
        run(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif verb == 'child' and len(sys.argv) == 6:
        child(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        raise SystemExit('unknown command or arity')
