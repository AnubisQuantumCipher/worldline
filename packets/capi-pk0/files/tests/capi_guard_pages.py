"""PK-0 helper: page-placed call frames, PROT_NONE guard pages and forked calls.

Packet PK-0 of the C-API boundary design (v4 DESIGN.md section 9.6, carried unchanged into
the endorsed v6). This module is test infrastructure. It decides nothing about WORLDLINE and
the runtime never imports it. It is not a test module (unittest discovery uses test_*.py).

* Every native call that the PK-0 characterization makes runs in a forked child. A
  foreign-pointer fault, a hang or a damaged heap in one case therefore cannot take the
  unittest process, and every other module's tests, down with it. PROT_NONE pages exist
  only in that child. The parent first requires a normal exit with status 0, and only then
  reads what the child reported. A fault is never mapped to a refusal code (class X, design
  section 9.6.5): it is an abnormal exit, and the case fails.
* The child's memory is one anonymous mapping. Each object gets its own page group. Every
  byte that the scenario did not write holds FILL (0xA5, rule R13), so a stray write anywhere
  in the mapping is visible to the before/after comparison.
* Guard placement (C-05, rule R14):
    "end"        the object ends exactly at a page boundary; the next page is PROT_NONE;
    "prefix"     elements 1..k end exactly at a page boundary; element k+1 starts on the
                 PROT_NONE page and is never written;
    "unreadable" the pointer names the start of a PROT_NONE page; nothing is written.
* No file is written. The child reports on a pipe and leaves with os._exit.
"""
from __future__ import annotations

import ctypes
import json
import mmap
import os
import select

PAGE = mmap.PAGESIZE
FILL = 0xA5
GAP = 64
# One past the largest address value: Integer_Address is modular over the full word.
ADDRESS_LIMIT = ctypes.c_size_t(-1).value + 1
# <asm-generic/mman-common.h>:16 "#define PROT_NONE 0x0"; Python's mmap module has no name for it.
PROT_NONE = 0

_LIBC = ctypes.CDLL(None, use_errno=True)
_MPROTECT = _LIBC.mprotect
_MPROTECT.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
_MPROTECT.restype = ctypes.c_int

TARGET_KEYS = frozenset(("to", "null", "addr", "overflow", "misaligned"))


class PlacementError(AssertionError):
    """A scenario that cannot be placed as declared is a defect of the case, never a pass."""


def is_target(value) -> bool:
    return isinstance(value, dict) and bool(TARGET_KEYS & set(value))


class Obj:
    """One foreign object.

    value: a ctypes instance, bytes, or an int (a size whose bytes stay FILL).
    init:  whether the value's bytes are written before the call (outputs default to FILL).
    elem:  element size of an array, for "prefix" guards.
    """

    def __init__(self, name, value, *, align=1, elem=None, init=True):
        self.name = name
        self.value = value
        self.align = align
        self.elem = elem
        self.init = init and not isinstance(value, int)

    def size(self) -> int:
        if isinstance(self.value, int):
            return self.value
        if isinstance(self.value, (bytes, bytearray)):
            return len(self.value)
        return ctypes.sizeof(self.value)

    def data(self) -> bytes:
        return bytes(self.value)


class Scenario:
    """One call: its objects, its arguments, the pointer fields inside records and outputs."""

    def __init__(self, export, restype):
        self.export = export
        self.restype = restype
        self.objects = {}
        self.args = []
        self.slots = {}
        self.outputs = {}
        self.labels = {}
        self.values = {}

    def add(self, name, value, *, align=None, elem=None, init=True):
        if name in self.objects:
            raise PlacementError(f"object {name} declared twice")
        if align is None:
            align = 1 if isinstance(value, (bytes, bytearray, int)) else ctypes.alignment(value)
        self.objects[name] = Obj(name, value, align=align, elem=elem, init=init)
        return value

    def arg(self, name, ctype, value):
        self.args.append([name, ctype, value])

    def set_arg(self, name, value):
        for entry in self.args:
            if entry[0] == name:
                entry[2] = value
                return
        raise PlacementError(f"{self.export} has no argument {name}")

    def get_arg(self, name):
        for entry in self.args:
            if entry[0] == name:
                return entry[2]
        raise PlacementError(f"{self.export} has no argument {name}")

    def slot(self, path, target):
        self.slots[path] = target

    def output(self, pointer, ctype):
        """pointer: "arg:<name>" or "<object>.<field>"; ctype: the type written there."""
        self.outputs[pointer] = ctype


def walk(root, path):
    """Return (container, final attribute or index) for a dotted path with [i] parts."""
    parts = []
    for item in path.split("."):
        while "[" in item:
            head, _, rest = item.partition("[")
            if head:
                parts.append(head)
            index, _, item = rest.partition("]")
            parts.append(int(index))
        if item:
            parts.append(item)
    node = root
    for part in parts[:-1]:
        node = node[part] if isinstance(part, int) else getattr(node, part)
    return node, parts[-1]


def assign(root, path, value):
    node, last = walk(root, path)
    if isinstance(last, int):
        node[last] = value
    else:
        setattr(node, last, value)


def _layout(scenario, guards):
    end = set(guards.get("end", ()))
    unreadable = set(guards.get("unreadable", ()))
    prefix = dict(guards.get("prefix", {}))
    for name in end | unreadable | set(prefix):
        if name not in scenario.objects:
            raise PlacementError(f"guard names unknown object {name}")
    pages, placements, protected = 0, {}, []
    for name, obj in scenario.objects.items():
        size = obj.size()
        if name in unreadable:
            # The whole declared extent lies on PROT_NONE pages; nothing is written.
            guard = max(1, -(-size // PAGE))
            placements[name] = (pages * PAGE, 0)
            protected.extend(range(pages, pages + guard))
            pages += guard
        elif name in end or name in prefix:
            if name in prefix:
                if obj.elem is None:
                    raise PlacementError(f"prefix guard on {name}, which is not an array")
                readable = prefix[name] * obj.elem
                if readable > size:
                    raise PlacementError(f"prefix of {name} exceeds the array")
            else:
                readable = size
            group = -(-(readable + GAP) // PAGE)
            offset = (pages + group) * PAGE - readable
            if offset % obj.align:
                raise PlacementError(f"{name} cannot end at a page boundary with alignment {obj.align}")
            # Every byte after the readable part, and at least one page, is PROT_NONE.
            guard = max(1, -(-(size - readable) // PAGE))
            placements[name] = (offset, readable)
            protected.extend(range(pages + group, pages + group + guard))
            pages += group + guard
        else:
            group = -(-(GAP + size + GAP) // PAGE)
            placements[name] = (pages * PAGE + GAP, size)
            pages += group
    return max(pages, 1), placements, protected


def _ranges(pages, protected):
    blocked = set(protected)
    ranges, start = [], None
    for page in range(pages + 1):
        if page < pages and page not in blocked:
            if start is None:
                start = page
        elif start is not None:
            ranges.append((start * PAGE, page * PAGE))
            start = None
    return ranges


def execute(library, scenario, guards=None, prelude=None):
    """Child side. Place, protect, snapshot, call, snapshot, report (JSON-serialisable)."""
    guards = guards or {}
    pages, placements, protected = _layout(scenario, guards)
    region = mmap.mmap(-1, pages * PAGE)
    region[:] = bytes([FILL]) * (pages * PAGE)
    base = ctypes.addressof(ctypes.c_char.from_buffer(region))

    def address(target):
        if "null" in target:
            return 0
        if "addr" in target:
            return int(target["addr"])
        if "overflow" in target:
            # An address whose extent passes the top of the address space. "back" defaults to
            # the object's alignment, so that the address still passes an alignment test
            # placed before the overflow test; the declared length must then exceed it.
            obj = scenario.objects[target["overflow"]]
            return ADDRESS_LIMIT - int(target.get("back", obj.align))
        if "misaligned" in target:
            return base + placements[target["misaligned"]][0] + 1
        return base + placements[target["to"]][0] + int(target.get("offset", 0))

    for path, target in scenario.slots.items():
        name, _, field = path.partition(".")
        assign(scenario.objects[name].value, field, address(target))
    for name, obj in scenario.objects.items():
        offset, readable = placements[name]
        if obj.init and readable:
            data = obj.data()[:readable]
            region[offset:offset + len(data)] = data
    for page in protected:
        if _MPROTECT(base + page * PAGE, PAGE, PROT_NONE) != 0:
            raise OSError(ctypes.get_errno(), "mprotect failed")
    readable_ranges = _ranges(pages, protected)

    def snapshot():
        return [bytes(region[a:b]) for a, b in readable_ranges]

    windows = {}
    for pointer, ctype in scenario.outputs.items():
        if pointer.startswith("arg:"):
            target = scenario.get_arg(pointer[4:])
        else:
            target = scenario.slots.get(pointer)
        if not isinstance(target, dict) or not is_target(target):
            continue
        where = address(target) - base
        size = ctypes.sizeof(ctype)
        if 0 <= where and where + size <= pages * PAGE:
            windows[pointer] = (where, size)
    oracle = prelude(region, base, address) if prelude is not None else None
    before = snapshot()
    function = library[scenario.export]
    function.restype = scenario.restype
    function.argtypes = [ctype for _, ctype, _ in scenario.args]
    values = [address(v) if is_target(v) else v for _, _, v in scenario.args]
    code = function(*values)
    after = snapshot()
    inside = set()
    for where, size in windows.values():
        inside.update(range(where, where + size))
    changed = []
    for (a, _b), old, new in zip(readable_ranges, before, after):
        if old != new:
            for index, (x, y) in enumerate(zip(old, new)):
                if x != y and a + index not in inside:
                    changed.append(a + index)
    owners = {}
    for name, (offset, readable) in placements.items():
        owners[name] = [offset, offset + max(readable, scenario.objects[name].size())]
    report = {
        "code": int(code),
        "oracle": oracle,
        "changed": changed[:32],
        "changed_count": len(changed),
        "objects": owners,
        "windows": {},
    }
    for pointer, (where, size) in windows.items():
        old = new = None
        for (a, b), chunk_old, chunk_new in zip(readable_ranges, before, after):
            if a <= where and where + size <= b:
                old = chunk_old[where - a:where - a + size]
                new = chunk_new[where - a:where - a + size]
        report["windows"][pointer] = {
            "offset": where,
            "before": None if old is None else old.hex(),
            "after": None if new is None else new.hex(),
        }
    return report


def _read_all(fds):
    chunks = {fd: [] for fd in fds}
    open_fds = set(fds)
    while open_fds:
        ready, _, _ = select.select(sorted(open_fds), [], [])
        for fd in ready:
            data = os.read(fd, 65536)
            if data:
                chunks[fd].append(data)
            else:
                open_fds.discard(fd)
                os.close(fd)
    return {fd: b"".join(parts) for fd, parts in chunks.items()}


def run_forked(child):
    """Run child() in a forked process. Return (wait status, decoded report or None, raw)."""
    rfd, wfd = os.pipe()
    pid = os.fork()
    if pid == 0:
        status = 0
        try:
            os.close(rfd)
            payload = json.dumps(child(), sort_keys=True).encode()
        except BaseException as exc:  # reported, never swallowed: the parent fails the case
            payload = json.dumps({"child_error": f"{type(exc).__name__}: {exc}"}).encode()
            status = 70
        try:
            view = memoryview(payload)
            while view:
                view = view[os.write(wfd, view):]
        finally:
            os._exit(status)
    os.close(wfd)
    raw = _read_all([rfd])[rfd]
    _, wait_status = os.waitpid(pid, 0)
    try:
        report = json.loads(raw.decode()) if raw else None
    except ValueError:
        report = None
    return wait_status, report, raw


def describe(wait_status) -> str:
    if os.WIFSIGNALED(wait_status):
        return f"terminated by signal {os.WTERMSIG(wait_status)}"
    if os.WIFEXITED(wait_status):
        return f"exit status {os.WEXITSTATUS(wait_status)}"
    return f"wait status {wait_status}"


def normal_exit(wait_status) -> bool:
    return os.WIFEXITED(wait_status) and os.WEXITSTATUS(wait_status) == 0
