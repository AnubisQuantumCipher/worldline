"""D21 staged-source audit and replay, never a confinement/admission decision.

The source snapshot is read without executing or importing any bundle module.
Replaying it binds the observation to the caller's independently supplied
executed-member digests. It does not authenticate that caller or establish
runtime confinement, provenance completeness, or protected evidence custody.
"""
from __future__ import annotations

import ast
import base64
import binascii
import hashlib
import importlib.machinery
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

SCHEMA = "worldline-examiner-audit-v1"
# Match the existing private evaluator's admitted frozen-tree resource domain.
MAX_TREE_BYTES = 268_435_456
MAX_TREE_ENTRIES = 100_000
_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_IMPORTS = frozenset((
    "importlib", "runpy", "pkgutil", "zipimport", "site", "pickle", "shelve",
    "marshal", "code", "codeop", "timeit", "doctest", "pdb", "bdb", "trace",
    "profile", "cProfile", "ctypes", "_ctypes", "subprocess", "multiprocessing",
    "pty", "unittest", "logging.config", "http.server", "webbrowser", "builtins",
))
_NAMES = frozenset(("exec", "eval", "compile", "__import__", "breakpoint", "__builtins__"))
_STATE = frozenset(("sys.path", "sys.meta_path", "sys.path_hooks",
                    "sys.path_importer_cache", "sys.modules"))
_MUTATORS = frozenset(("append", "extend", "insert", "remove", "pop", "clear",
                       "reverse", "sort", "update", "setdefault", "popitem",
                       "__setitem__", "__delitem__", "__iadd__", "__imul__",
                       "__ior__", "__init__"))


def _relative(value):
    return (type(value) is str and bool(value) and "\0" not in value
            and not value.startswith("/") and str(PurePosixPath(value)) == value
            and all(part not in (".", "..") for part in value.split("/")))


def _pins(value):
    if type(value) is not dict or not value:
        raise ValueError("executed digest inventory is absent")
    if any(not _relative(k) or type(v) is not str or _HEX.fullmatch(v) is None
           for k, v in value.items()):
        raise ValueError("executed digest inventory is malformed")
    return dict(sorted(value.items()))


def executed_digests(executed):
    """Translate the existing executed-verifier schema without trusting labels."""
    if type(executed) is not dict or type(executed.get("members")) is not list:
        raise ValueError("executed members are absent")
    result = {}
    for member in executed["members"]:
        if type(member) is not dict:
            raise ValueError("executed member is malformed")
        root, path = member.get("rootKey"), member.get("path")
        if not _relative(root) or "/" in root or not _relative(path):
            raise ValueError("executed member path is malformed")
        relative = root + "/" + path
        if relative in result or member.get("executedAs") != "/run/worldline-verifiers/" + relative:
            raise ValueError("executed member is duplicated or rebound")
        result[relative] = member.get("sha256")
    return _pins(result)


def _runtime():
    return {"implementation": sys.implementation.name,
            "cacheTag": sys.implementation.cache_tag,
            "version": list(sys.version_info),
            "stdlibNames": sorted(sys.stdlib_module_names),
            "extensionSuffixes": list(importlib.machinery.EXTENSION_SUFFIXES)}


def _signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _directory(path):
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("staged bundle must have an absolute path")
    fd = os.open("/", _DIR)
    try:
        for part in path.parts[1:]:
            child = os.open(part, _DIR, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _capture(root):
    """Capture every member, including unimported data, through stable names/fds."""
    fd = _directory(root)
    directories, files = [""], []
    total = 0
    try:
        # Directory frames retain their parent until every child is restated.
        def visit(directory, prefix, depth=0):
            nonlocal total
            if depth > 128:
                raise ValueError("staged tree exceeds existing depth bound")
            before = os.fstat(directory)
            names = sorted(os.listdir(directory))
            for name in names:
                relative = prefix + name
                if not _relative(relative):
                    raise ValueError("invalid staged member name")
                named = os.stat(name, dir_fd=directory, follow_symlinks=False)
                if stat.S_ISDIR(named.st_mode):
                    child = os.open(name, _DIR, dir_fd=directory)
                    try:
                        opened = os.fstat(child)
                        if _signature(opened) != _signature(named):
                            raise ValueError("staged directory changed while opening")
                        directories.append(relative)
                        if len(directories) + len(files) > MAX_TREE_ENTRIES:
                            raise ValueError("staged tree exceeds existing entry bound")
                        visit(child, relative + "/", depth + 1)
                        if _signature(os.fstat(child)) != _signature(opened):
                            raise ValueError("staged directory changed while reading")
                    finally:
                        os.close(child)
                elif stat.S_ISREG(named.st_mode) and named.st_nlink == 1:
                    child = os.open(name, _FILE, dir_fd=directory)
                    try:
                        opened = os.fstat(child)
                        if _signature(opened) != _signature(named):
                            raise ValueError("staged file changed while opening")
                        if total + opened.st_size > MAX_TREE_BYTES:
                            raise ValueError("staged tree exceeds existing byte bound")
                        chunks, size = [], 0
                        while True:
                            chunk = os.read(child, min(1_048_576, opened.st_size - size + 1))
                            if not chunk:
                                break
                            size += len(chunk)
                            if size > opened.st_size:
                                raise ValueError("staged file grew while reading")
                            chunks.append(chunk)
                        if size != opened.st_size or _signature(os.fstat(child)) != _signature(opened):
                            raise ValueError("staged file changed while reading")
                        payload = b"".join(chunks)
                    finally:
                        os.close(child)
                    total += len(payload)
                    files.append({"path": relative,
                                  "payloadB64": base64.b64encode(payload).decode("ascii")})
                    if len(directories) + len(files) > MAX_TREE_ENTRIES:
                        raise ValueError("staged tree exceeds existing entry bound")
                else:
                    raise ValueError("staged member is not an ordinary singly linked file/directory")
                if _signature(os.stat(name, dir_fd=directory, follow_symlinks=False)) != _signature(named):
                    raise ValueError("staged pathname changed while reading")
            if names != sorted(os.listdir(directory)) or _signature(os.fstat(directory)) != _signature(before):
                raise ValueError("staged directory inventory changed while reading")
        visit(fd, "")
    finally:
        os.close(fd)
    return sorted(directories), sorted(files, key=lambda item: item["path"])


def _forbidden_import(name):
    return any(name == denied or name.startswith(denied + ".") for denied in _IMPORTS)


def _forbidden_attribute(name):
    if name.startswith("os."):
        attribute = name[3:]
        return attribute in ("system", "popen", "fork", "forkpty", "startfile") or attribute.startswith(("exec", "spawn", "posix_spawn"))
    return (name == "concurrent.futures.ProcessPoolExecutor"
            or name.startswith("sqlite3.") and name.rsplit(".", 1)[-1] in ("enable_load_extension", "load_extension"))


def _qualified(node, aliases):
    if isinstance(node, ast.Name):
        return aliases.get(node.id, {node.id})
    if isinstance(node, ast.Attribute):
        return {prefix + "." + node.attr for prefix in _qualified(node.value, aliases)}
    if isinstance(node, ast.Subscript):
        return _qualified(node.value, aliases)
    if isinstance(node, ast.Call):
        factories = _qualified(node.func, aliases)
        return {'sqlite3.Connection'} if factories & {'sqlite3.connect', 'sqlite3.Connection'} else set()
    return set()


def _scope_contents(tree):
    """Definition headers execute in the enclosing scope; bodies do not."""
    comprehensions = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
    scopes = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda, *comprehensions)
    if isinstance(tree, comprehensions):
        body = [tree.key, tree.value] if isinstance(tree, ast.DictComp) else [tree.elt]
        for index, generator in enumerate(tree.generators):
            body.extend((generator.target, *generator.ifs))
            if index:
                body.append(generator.iter)
    else:
        body = tree.body
    nodes, children, pending = [], [], list(body) if isinstance(body, list) else [body]
    while pending:
        node = pending.pop()
        nodes.append(node)
        if isinstance(node, scopes):
            children.append(node)
            if isinstance(node, comprehensions):
                pending.append(node.generators[0].iter)
            elif isinstance(node, ast.ClassDef):
                pending.extend(node.bases)
                pending.extend(node.keywords)
                pending.extend(node.decorator_list)
            else:
                pending.extend(node.args.defaults)
                pending.extend(value for value in node.args.kw_defaults if value is not None)
                for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs,
                            *([node.args.vararg] if node.args.vararg else []),
                            *([node.args.kwarg] if node.args.kwarg else [])):
                    if arg.annotation is not None:
                        pending.append(arg.annotation)
                if not isinstance(node, ast.Lambda):
                    pending.extend(node.decorator_list)
                    if node.returns is not None:
                        pending.append(node.returns)
            pending.extend(getattr(node, 'type_params', ()))
        else:
            pending.extend(ast.iter_child_nodes(node))
    return nodes, children


def _scoped_nodes(tree, inherited=None, *, outside_class=None):
    """Keep all possible imported origins within each lexical scope.

    Reusing an alias cannot erase an earlier listed operation. Child scopes do
    not overwrite siblings. This is a syntactic over-approximation, not a
    theorem about values reaching an operation at runtime.
    """
    nodes, children = _scope_contents(tree)
    aliases = {name: set(origins) for name, origins in (inherited or {}).items()}
    local, outer, imported, assigned = set(), set(), {}, {}
    if isinstance(tree, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        local.update(arg.arg for arg in (*tree.args.posonlyargs, *tree.args.args, *tree.args.kwonlyargs,
                     *([tree.args.vararg] if tree.args.vararg else []),
                     *([tree.args.kwarg] if tree.args.kwarg else [])))
    for node in nodes:
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            local.add(node.id)
        elif isinstance(node, ast.arg):
            local.add(node.arg)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            outer.update(node.names)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split('.')[0]
                origin = alias.name if alias.asname else alias.name.split('.')[0]
                imported.setdefault(name, set()).add(origin)
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            for alias in node.names:
                if alias.name != '*':
                    imported.setdefault(alias.asname or alias.name, set()).add(node.module + '.' + alias.name)
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and node.value is not None:
                    assigned.setdefault(target.id, []).append(node.value)
    for name in local - outer:
        aliases[name] = set()
    for name, origins in imported.items():
        # A scope-local import binds the local variable; global/nonlocal writes
        # conservatively retain the inherited alternatives as well.
        aliases[name] = (aliases.get(name, set()) if name in outer else set()) | origins
    seeds = {name: set(origins) for name, origins in aliases.items()}

    def origin(node, active):
        if isinstance(node, ast.Name):
            return binding(node.id, active)
        if isinstance(node, ast.Attribute):
            return {prefix + '.' + node.attr for prefix in origin(node.value, active)}
        if isinstance(node, ast.Call):
            factories = origin(node.func, active)
            return {'sqlite3.Connection'} if factories & {'sqlite3.connect', 'sqlite3.Connection'} else set()
        return set()

    def binding(name, active):
        result = set(seeds.get(name, {name}))
        if name in active:
            return result
        for value in assigned.get(name, ()):
            result.update(origin(value, active | {name}))
        return result

    for name in assigned:
        aliases[name] = binding(name, set())
    for node in nodes:
        yield node, aliases
    for child in children:
        # Class attributes are not an enclosing lexical namespace for method
        # bodies or nested classes. Their headers above still use this class.
        parent = outside_class if isinstance(tree, ast.ClassDef) else aliases
        yield from _scoped_nodes(child, parent, outside_class=parent)


class _Closure:
    def __init__(self, files, directories, entry):
        self.files, self.directories, self.entry = files, set(directories), entry
        parent = str(PurePosixPath(entry).parent)
        self.roots = tuple(dict.fromkeys(("", "" if parent == "." else parent)))
        self.pending = [(entry, "__main__", False)]
        self.seen, self.closure, self.findings = set(), {}, []
        self.package_paths = {}
        self.suffixes = (*importlib.machinery.EXTENSION_SUFFIXES, ".py", ".pyc", ".pyd", ".so", ".zip")

    def finding(self, path, line, detail):
        item = {"code": "EXAMINER_CODE_LOADING", "file": path, "line": line, "detail": detail}
        if item not in self.findings:
            self.findings.append(item)

    def resolve(self, name, path, line, optional=False):
        if name == "candidate":
            return "runtime"
        locations = self.roots
        full = []
        for component in name.split("."):
            full.append(component)
            selected, namespaces = None, []
            for location in locations:
                base = (location + "/" if location else "") + component
                for suffix in self.suffixes:
                    candidate = base + "/__init__" + suffix
                    if candidate in self.files:
                        selected = (candidate, True, (base,))
                        break
                if selected is None:
                    for suffix in self.suffixes:
                        candidate = base + suffix
                        if candidate in self.files:
                            selected = (candidate, False, ())
                            break
                if selected is not None:
                    break
                if base in self.directories:
                    namespaces.append(base)
            if selected is None:
                if len(full) == 1 and component in sys.stdlib_module_names:
                    return "stdlib"
                if namespaces:
                    locations = tuple(namespaces)
                    continue
                if not optional:
                    self.finding(path, line, "unresolved import: " + name)
                return None
            selected_path, package, locations = selected
            if not selected_path.endswith(".py"):
                self.finding(path, line, "non-source import: " + selected_path)
                return None
            self.pending.append((selected_path, ".".join(full), package))
            if package:
                self.package_paths[".".join(full)] = selected_path
            if len(full) < len(name.split(".")) and not package:
                if not optional:
                    self.finding(path, line, "non-package import parent: " + name)
                return None
        return "bundle"

    def wildcard(self, module, path, line):
        package_path = self.package_paths.get(module)
        if package_path is None:
            return
        try:
            tree = ast.parse(self.files[package_path], filename=package_path)
        except (SyntaxError, ValueError, UnicodeError, RecursionError):
            return  # The ordinary closure scan retains the parse finding.
        # Literal __all__ strings are module names, never Python programs.
        # Unknown computed exports cannot silently omit potentially loaded code.
        exports, dynamic = set(), False
        nodes, _children = _scope_contents(tree)
        aliases = {'__all__'}
        while True:
            prior = set(aliases)
            for node in nodes:
                if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    if isinstance(node.value, ast.Name) and node.value.id in aliases:
                        aliases.update(target.id for target in targets if isinstance(target, ast.Name))
            if prior == aliases:
                break

        def export_names(value, *, single=False):
            nonlocal dynamic
            try:
                literal = ast.literal_eval(value)
            except (ValueError, TypeError, SyntaxError, RecursionError):
                dynamic = True
                return
            if single and type(literal) is str:
                exports.add(literal)
            elif type(literal) in (list, tuple) and all(type(name) is str for name in literal):
                exports.update(literal)
            else:
                dynamic = True

        def aliased(node):
            while isinstance(node, (ast.Attribute, ast.Subscript)):
                node = node.value
            return isinstance(node, ast.Name) and node.id in aliases

        for node in nodes:
            targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, (ast.AnnAssign, ast.AugAssign)) else []
            for target in targets:
                if isinstance(target, ast.Name) and target.id == '__all__':
                    export_names(node.value)
                elif isinstance(node, ast.AugAssign) and isinstance(target, ast.Name) and target.id in aliases:
                    export_names(node.value)
                elif isinstance(target, (ast.Subscript, ast.Attribute)) and aliased(target):
                    export_names(node.value, single=True)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if any((alias.asname or alias.name.split('.')[0]) == '__all__' for alias in node.names):
                    dynamic = True
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and aliased(node.func.value):
                    method = node.func.attr
                    if method in ('append', 'extend', '__iadd__', '__init__') and len(node.args) == 1 and not node.keywords:
                        export_names(node.args[0], single=method == 'append')
                    elif method in ('insert', '__setitem__') and len(node.args) == 2 and not node.keywords:
                        export_names(node.args[1], single=True)
                    elif method not in ('clear', 'pop', 'remove', 'reverse', 'sort', '__delitem__', '__imul__', 'copy', 'count', 'index'):
                        dynamic = True
                elif any(aliased(argument) for argument in (*node.args, *(keyword.value for keyword in node.keywords))):
                    dynamic = True
        if dynamic:
            self.finding(path, line, 'package wildcard export set is not statically resolved: ' + module)
        for name in sorted(exports):
            self.resolve(module + '.' + name, path, line, optional=True)

    def run(self):
        while self.pending:
            path, module, package = self.pending.pop()
            if (path, module, package) in self.seen:
                continue
            self.seen.add((path, module, package))
            payload = self.files.get(path)
            if payload is None or not path.endswith(".py"):
                self.finding(path, 0, "entry/closure member is absent or non-source")
                continue
            self.closure[path] = hashlib.sha256(payload).hexdigest()
            try:
                tree = ast.parse(payload, filename=path)
            except (SyntaxError, ValueError, UnicodeError, RecursionError) as exc:
                self.finding(path, getattr(exc, "lineno", 0) or 0, "source cannot be parsed: " + type(exc).__name__)
                continue
            for node, aliases in _scoped_nodes(tree):
                line = getattr(node, "lineno", 0)
                if isinstance(node, ast.Import):
                    imports = [alias.name for alias in node.names]
                    for name in imports:
                        if _forbidden_import(name) or _forbidden_attribute(name):
                            self.finding(path, line, "forbidden import: " + name)
                        self.resolve(name, path, line)
                elif isinstance(node, ast.ImportFrom):
                    name = node.module or ""
                    if node.level:
                        parent = module.split(".") if package else module.split(".")[:-1]
                        if node.level > len(parent):
                            self.finding(path, line, "relative import escapes its package")
                            continue
                        prefix = parent[:len(parent) - node.level + 1]
                        name = ".".join(prefix + ([name] if name else []))
                    if _forbidden_import(name):
                        self.finding(path, line, "forbidden import: " + name)
                    resolved = self.resolve(name, path, line)
                    for alias in node.names:
                        member = name + "." + alias.name
                        if _forbidden_import(member) or _forbidden_attribute(member) or alias.name in _NAMES:
                            self.finding(path, line, "forbidden imported name: " + member)
                        if resolved == "bundle" and alias.name != "*":
                            self.resolve(member, path, line, optional=True)
                        elif resolved == 'bundle' and alias.name == '*':
                            self.wildcard(name, path, line)
                elif isinstance(node, ast.Name) and node.id in _NAMES:
                    self.finding(path, line, "forbidden executable name: " + node.id)
                if isinstance(node, ast.Attribute):
                    for name in _qualified(node, aliases):
                        if _forbidden_attribute(name):
                            self.finding(path, line, "forbidden executable attribute: " + name)
                if isinstance(node, (ast.Attribute, ast.Subscript, ast.Name)) and isinstance(node.ctx, (ast.Store, ast.Del)):
                    for name in _qualified(node, aliases):
                        if any(name == state or name.startswith(state + ".") for state in _STATE):
                            self.finding(path, line, "importer state mutation: " + name)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    for target in _qualified(node.func.value, aliases):
                        if target in _STATE and node.func.attr in _MUTATORS:
                            self.finding(path, line, "importer state mutation: " + target + "." + node.func.attr)
        return sorted(self.findings, key=lambda x: (x["file"], x["line"], x["detail"])), [
            {"path": path, "sha256": digest} for path, digest in sorted(self.closure.items())]


def _analyse(record, pins, entry):
    if (type(record) is not dict or record.get("schema") != SCHEMA
            or record.get("entry") != entry or not _relative(entry)
            or record.get("executedDigests") != pins or record.get("runtime") != _runtime()
            or type(record.get("files")) is not list or type(record.get("directories")) is not list):
        raise ValueError("audit input binding is malformed or changed")
    directories = record["directories"]
    if (directories != sorted(set(directories)) or "" not in directories
            or any(not _relative(p) for p in directories if p)):
        raise ValueError("audit directory inventory is malformed")
    files, total = {}, 0
    if len(directories) + len(record["files"]) > MAX_TREE_ENTRIES:
        raise ValueError("audit inventory exceeds existing entry bound")
    for item in record["files"]:
        if type(item) is not dict or set(item) != {"path", "payloadB64"} or not _relative(item["path"]):
            raise ValueError("audit file entry is malformed")
        path, encoded = item["path"], item["payloadB64"]
        if path in files or path in directories or type(encoded) is not str or len(encoded) > ((MAX_TREE_BYTES + 2) // 3) * 4:
            raise ValueError("audit file is duplicated or over bound")
        payload = base64.b64decode(encoded, validate=True)
        if base64.b64encode(payload).decode("ascii") != encoded:
            raise ValueError("audit file has a noncanonical byte encoding")
        total += len(payload)
        if total > MAX_TREE_BYTES:
            raise ValueError("audit files exceed existing byte bound")
        files[path] = payload
        parent = str(PurePosixPath(path).parent)
        if ("" if parent == "." else parent) not in directories:
            raise ValueError("audit file parent is absent")
    if set(files) != set(pins) or any(hashlib.sha256(value).hexdigest() != pins[path] for path, value in files.items()):
        raise ValueError("staged bytes differ from executed digest inventory")
    return _Closure(files, directories, entry).run()


def audit(bundle_root, entry, executed_digests):
    """Read the actual staged bundle and return replayable D21 observations."""
    record = {"schema": SCHEMA, "entry": entry, "executedDigests": executed_digests,
              "runtime": _runtime(), "directories": [], "files": [],
              "clean": False, "findings": [], "closure": []}
    try:
        pins = _pins(executed_digests)
        record["executedDigests"] = pins
        record["directories"], record["files"] = _capture(bundle_root)
        findings, closure = _analyse(record, pins, entry)
        record.update(clean=not findings, findings=findings, closure=closure)
    except (OSError, ValueError, TypeError, RecursionError, binascii.Error) as exc:
        record["findings"] = [{"code": "EXAMINER_CODE_LOADING", "file": entry,
                               "line": 0, "detail": str(exc)}]
    return record


def replay(record, *, entry, executed_digests):
    """Recompute instead of accepting a saved clean flag or saved findings."""
    try:
        findings, closure = _analyse(record, _pins(executed_digests), entry)
        return (record.get("clean") is True and not findings
                and record.get("findings") == findings and record.get("closure") == closure)
    except (OSError, ValueError, TypeError, KeyError, RecursionError, binascii.Error):
        return False


def report_audit_clean(result):
    """Re-derive the named D21 fact; do not derive confinement from this fact."""
    try:
        executed = result["executedVerifierSet"]
        pins = executed_digests(executed)
        argv = result["argv"]
        if type(argv) is not list or len(argv) < 2 or argv[0] != "/usr/bin/python3":
            return False
        rewrites = executed["argvRewrites"]
        if type(rewrites) is not list:
            return False
        entries = {item["to"] for item in rewrites
                   if type(item) is dict and item.get("from") == argv[1]}
        if len(entries) != 1:
            return False
        mounted = entries.pop()
        prefix = "/run/worldline-verifiers/"
        if type(mounted) is not str or not mounted.startswith(prefix):
            return False
        entry = mounted[len(prefix):]
        evidence = result["examinerAudit"]
        if type(evidence) is not dict or set(evidence) != {"before", "after", "mount"} or evidence["mount"] != prefix[:-1]:
            return False
        before, after = evidence["before"], evidence["after"]
        return (executed.get("stable") is True
                and executed.get("identity") == executed.get("identityAfterExecution")
                and replay(before, entry=entry, executed_digests=pins)
                and replay(after, entry=entry, executed_digests=pins)
                and before["files"] == after["files"]
                and before["directories"] == after["directories"])
    except (ValueError, TypeError, KeyError, IndexError):
        return False
