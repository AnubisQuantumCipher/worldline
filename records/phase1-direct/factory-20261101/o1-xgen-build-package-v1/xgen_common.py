"""Bounded observational filesystem helpers; no authorization decisions."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
WORK = ROOT / "records/phase1-direct/completion-20261026/o1-xgen-build-v1"
LIVE_ROOT = WORK / "live"
JOB = HERE.parent / "o1-xgen-build-job-v1"
G = Path("/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1")
P = Path("/home/sicarii/opt/gnat/gprbuild-aarch64-linux-26.0.0-1")
LIVE = 4 * 1024**3
FILE = 64 * 1024**2
ENTRIES = 8192
RESERVE = 10_000_000_000
TOTAL = 14_050_918_400
ARCHIVE = LIVE + 16 * 1024**2


def regular(path, limit):
    """Reject links at every component, then open without following final link."""
    path = Path(path).absolute()
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise RuntimeError("symlink component: " + str(parent))
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise RuntimeError("nonregular or oversized file")
        return fd, info
    except BaseException:
        os.close(fd)
        raise


def digest(path, limit=FILE):
    fd, info = regular(path, limit)
    total, value = 0, hashlib.sha256()
    try:
        for _ in range(limit // 65536 + 2):
            data = os.read(fd, 65536)
            if not data:
                if total != info.st_size or os.fstat(fd).st_size != total:
                    raise RuntimeError("file changed during hash")
                return {"bytes": total, "sha256": value.hexdigest()}
            total += len(data)
            if total > limit:
                raise RuntimeError("file grew beyond bound")
            value.update(data)
        raise RuntimeError("hash iteration bound")
    finally:
        os.close(fd)


def bounded_read(path, limit):
    fd, _ = regular(path, limit)
    try:
        raw = os.read(fd, limit + 1)
        if len(raw) > limit:
            raise RuntimeError("read overflow")
        return raw
    finally:
        os.close(fd)


def reject_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load_json(path, limit=2 * 1024**2):
    return json.loads(bounded_read(path, limit), object_pairs_hook=reject_pairs,
                      parse_float=reject_number, parse_constant=reject_number)


def reject_number(_token):
    raise ValueError("non-integer JSON number")


def write_json(path, value, limit=1024**2):
    raw = (json.dumps(value, sort_keys=True, allow_nan=False) + "\n").encode("ascii")
    if len(raw) > limit:
        raise RuntimeError("receipt overflow")
    with Path(path).open("xb") as stream:
        if stream.write(raw) != len(raw):
            raise RuntimeError("short receipt write")


def relative(name):
    if not isinstance(name, str):
        raise RuntimeError("relative path type")
    path = Path(name)
    if (not name or path.is_absolute()
            or any(x in ("", ".", "..") for x in name.split("/"))
            or any(ord(x) < 32 or ord(x) > 126 for x in name)):
        raise RuntimeError("unsupported relative path")
    # A conservative USTAR subset; no prefix splitting or extension records.
    if len(name.encode("ascii")) > 99:
        raise RuntimeError("USTAR name exceeds registered subset")
    return path


def inventory(root, byte_limit=LIVE, file_limit=FILE, entry_limit=ENTRIES):
    """Finite lstat scan; sizes are logical bytes, not an aggregate quota."""
    root, pending, result, total = Path(root), [Path(root)], {}, 0
    for _ in range(entry_limit + 1):
        if not pending:
            return result, total
        parent = pending.pop()
        if parent.is_symlink() or not parent.is_dir():
            raise RuntimeError("invalid inventory root/directory")
        with os.scandir(parent) as rows:
            for row in rows:
                name = str(Path(row.path).relative_to(root))
                relative(name)
                if len(result) >= entry_limit or row.is_symlink():
                    raise RuntimeError("inventory count/link")
                info = row.stat(follow_symlinks=False)
                if info.st_mode & (stat.S_ISUID | stat.S_ISGID):
                    raise RuntimeError("unsupported privilege mode")
                if stat.S_ISDIR(info.st_mode):
                    result[name] = {"kind": "directory", "mode": stat.S_IMODE(info.st_mode)}
                    pending.append(Path(row.path))
                elif stat.S_ISREG(info.st_mode):
                    total += info.st_size
                    if info.st_size > file_limit or total > byte_limit or info.st_nlink != 1:
                        raise RuntimeError("inventory size/hardlink")
                    result[name] = {"kind": "file", "bytes": info.st_size,
                                    "mode": stat.S_IMODE(info.st_mode)}
                else:
                    raise RuntimeError("unsupported inventory object")
    raise RuntimeError("inventory directory bound")


def hashed_inventory(root):
    result, _ = inventory(root)
    for name, item in result.items():
        if item["kind"] == "file":
            item.update(digest(Path(root) / name))
    return result


def verify_pins(rows):
    if not isinstance(rows, list) or len(rows) > 4096:
        raise RuntimeError("pin count/type")
    total = 0
    for row in rows:
        expected = row["identity"]
        size = expected["bytes"]
        if type(size) is not int or size < 0 or size > 128 * 1024**2:
            raise RuntimeError("pin size/type")
        if (not isinstance(expected.get("sha256"), str)
                or re.fullmatch(r"[0-9a-f]{64}", expected["sha256"]) is None):
            raise RuntimeError("pin hash type/syntax")
        total += size
        if total > 512 * 1024**2:
            raise RuntimeError("pin aggregate")
        path = Path(row["path"])
        if row.get("link") is not None:
            if not path.is_symlink() or os.readlink(path) != row["link"]:
                raise RuntimeError("pin link drift")
            path = path.resolve(strict=True)
        if digest(path, 128 * 1024**2) != expected:
            raise RuntimeError("source/tool pin drift: " + str(path))


def verify_packet():
    manifest = load_json(HERE / "manifest.json")
    rows = manifest["files"]
    if not isinstance(rows, list) or len(rows) > 95:
        raise RuntimeError("packet manifest count/type")
    total, seen = 0, set()
    for row in rows:
        name, identity = row["path"], row["identity"]
        relative(name)
        if name in seen or type(identity["bytes"]) is not int:
            raise RuntimeError("packet duplicate/type")
        total += identity["bytes"]
        seen.add(name)
        if total > 8 * 1024**2 or digest(HERE / name, 8 * 1024**2) != identity:
            raise RuntimeError("packet identity/budget")


def isolated(argv, cwd):
    return ["/usr/bin/bwrap", "--die-with-parent", "--unshare-pid", "--unshare-net",
            "--cap-drop", "ALL", "--ro-bind", "/", "/", "--proc", "/proc",
            "--dev", "/dev", "--bind", str(LIVE_ROOT), str(LIVE_ROOT),
            "--chdir", str(cwd), "--", *map(str, argv)]
