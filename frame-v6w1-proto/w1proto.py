"""Prototype of the W-1 v2 writer-side mechanisms that can be exercised without privileges (same-user simulation).

ENGINEERING_ONLY. Not the installed frame, not reviewed, and never evidence of the account boundary: these functions
implement the lease (W-1 v2 section 4.1), the authenticated framing with a running SHA-256 chain (5.1), verification of
streamed inputs against compiled-in pins (6.1) and the non-dumpable hardening (5.1/2). The kernel-enforced writer
boundary itself (separate accounts, DAC, ACLs) cannot be tested by the lead user and is not claimed here.
"""
import base64, ctypes, errno, fcntl, hashlib, json, os, re, stat, struct

MAX_MESSAGE = 1 << 26          # 64 MiB framing ceiling; a larger frame is refused, never truncated
ZERO_CHAIN = '0' * 64
PATH_RE = re.compile(r'(?:[A-Za-z0-9_.+-]+/)*[A-Za-z0-9_.+-]+')


class Refused(Exception):
    """A refusal: the caller must stop before any further mutation."""


class LeaseHeld(Refused):
    pass


def require(condition, message):
    if not condition:
        raise Refused(message)


# ---------------------------------------------------------------- 4.1 lease

def acquire_lease(lease_dir_fd, name='writer.lock'):
    """Open the existing lock file (never created here: setup creates it) without following links and take an
    exclusive non-blocking flock. Returns the fd, which the caller holds for its whole life. Refuses a symlink,
    a non-regular or multiply linked file, a foreign owner or a mode other than 0600, and refuses if already held."""
    try:
        fd = os.open(name, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=lease_dir_fd)
    except OSError as caught:
        raise Refused('lease file cannot be opened without following: %s' % errno.errorcode.get(caught.errno, caught.errno))
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'lease file is not a single-link regular file')
        require(info.st_uid == os.geteuid(), 'lease file is not owned by the writer account')
        require(stat.S_IMODE(info.st_mode) == 0o600, 'lease file mode is not 0600')
        entry = os.stat(name, dir_fd=lease_dir_fd, follow_symlinks=False)
        require((entry.st_dev, entry.st_ino) == (info.st_dev, info.st_ino), 'lease file replaced during open')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as caught:
            if caught.errno in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise LeaseHeld('lease held by another writer')
            raise
        return fd
    except BaseException:
        os.close(fd)
        raise


# ---------------------------------------------------------------- 5.1 framing

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def encode_message(seq, chain, body):
    payload = canonical({'seq': seq, 'prev': chain, 'body': body})
    require(len(payload) <= MAX_MESSAGE, 'message exceeds the framing ceiling')
    return struct.pack('>Q', len(payload)) + payload, hashlib.sha256(bytes.fromhex(chain) + payload).hexdigest()


def read_exact(stream, count):
    data = b''
    while len(data) < count:
        chunk = stream.read(count - len(data))
        require(chunk, 'channel closed inside a frame')
        data += chunk
    return data


def decode_message(stream, expected_seq, chain):
    """Read one frame; refuse a wrong sequence number, a wrong previous chain head, non-canonical bytes or an
    oversized frame. Returns (body, new_chain)."""
    header = stream.read(8)
    require(header, 'channel closed')
    header += read_exact(stream, 8 - len(header)) if len(header) < 8 else b''
    (length,) = struct.unpack('>Q', header)
    require(0 < length <= MAX_MESSAGE, 'frame length outside the framing ceiling')
    payload = read_exact(stream, length)
    try:
        message = json.loads(payload.decode('ascii'))
    except (UnicodeDecodeError, ValueError):
        raise Refused('frame is not ASCII JSON')
    require(isinstance(message, dict) and set(message) == {'seq', 'prev', 'body'}, 'frame fields are not exactly seq/prev/body')
    require(canonical(message) == payload, 'frame is not canonical JSON')
    require(message['seq'] == expected_seq, 'frame sequence number is not the expected one')
    require(message['prev'] == chain, 'frame does not continue this channel chain')
    return message['body'], hashlib.sha256(bytes.fromhex(chain) + payload).hexdigest()


# ---------------------------------------------------------------- 6.1 streamed inputs

def verify_inputs(entries, pins, observation_names=()):
    """entries: list of {path, size, mode, sha256, data_b64}. Pinned paths must match their pin exactly; declared
    observation names are accepted with their recorded digest; anything else, duplicates, traversal, absolute paths,
    a size or digest mismatch, or a missing pinned path is refused. Returns {path: bytes}."""
    seen, out = set(), {}
    for entry in entries:
        require(isinstance(entry, dict) and set(entry) == {'path', 'size', 'mode', 'sha256', 'data_b64'}, 'input entry fields')
        path = entry['path']
        require(isinstance(path, str) and PATH_RE.fullmatch(path) is not None
                and not any(part in ('.', '..') for part in path.split('/')), 'input path is not a plain relative path: ' + repr(path))
        require(path not in seen, 'duplicate input path: ' + path)
        seen.add(path)
        data = base64.b64decode(entry['data_b64'], validate=True)
        digest = hashlib.sha256(data).hexdigest()
        require(len(data) == entry['size'] and digest == entry['sha256'], 'input bytes do not match their declared identity: ' + path)
        require(isinstance(entry['mode'], int) and entry['mode'] in (0o400, 0o440, 0o444, 0o600, 0o640, 0o644, 0o700, 0o750, 0o755),
                'input mode outside the allowed set: ' + path)
        if path in pins:
            require(digest == pins[path], 'pinned input differs from its pin: ' + path)
        else:
            require(path in observation_names, 'input is neither pinned nor a declared observation: ' + path)
        out[path] = data
    missing = sorted(set(pins) - seen)
    require(not missing, 'pinned inputs missing: ' + repr(missing[:10]))
    return out


# ---------------------------------------------------------------- 5.1 / 2 hardening

PR_GET_DUMPABLE, PR_SET_DUMPABLE = 3, 4


def set_nondumpable():
    """prctl(PR_SET_DUMPABLE, 0) and read it back. Returns the read-back evidence."""
    libc = ctypes.CDLL(None, use_errno=True)
    require(libc.prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) == 0, 'PR_SET_DUMPABLE failed: errno %d' % ctypes.get_errno())
    value = libc.prctl(PR_GET_DUMPABLE, 0, 0, 0, 0)
    require(value == 0, 'process is still dumpable after PR_SET_DUMPABLE 0')
    fd_dir_owner = os.stat('/proc/self/fd').st_uid
    return {'pr_get_dumpable': value, 'proc_self_fd_owner_uid': fd_dir_owner}
