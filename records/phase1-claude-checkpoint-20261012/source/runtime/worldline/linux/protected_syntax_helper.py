# Standalone primitive parser acquisition, intended to be loaded ONLY from the
# independently pinned support artifact inside the genuine read-only provider.
# This code never executes the target source or decides its audit/admission.
import ast
import base64
import struct
import sys
import _imp


def _scope_contents(tree):
    """Original examiner_audit scope traversal, unchanged."""
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


def _b64(value):
    return base64.b64encode(value).decode('ascii')


def _constant(value):
    if value is None or type(value) is bool:
        return value
    if type(value) is str:
        return {'constantType': 'str', 'payloadB64': _b64(value.encode('utf-8', 'surrogatepass'))}
    if type(value) is bytes:
        return {'constantType': 'bytes', 'payloadB64': _b64(value)}
    if type(value) is int:
        magnitude = value if value >= 0 else ~value
        width = max(1, (magnitude.bit_length() + 8) // 8)
        return {'constantType': 'integer', 'payloadB64': _b64(value.to_bytes(width, 'little', signed=True))}
    if type(value) is float:
        return {'constantType': 'float', 'payloadB64': _b64(struct.pack('>d', value))}
    if type(value) is complex:
        return {'constantType': 'complex', 'realB64': _b64(struct.pack('>d', value.real)),
                'imagB64': _b64(struct.pack('>d', value.imag))}
    if value is Ellipsis:
        return {'constantType': 'ellipsis'}
    raise TypeError('ast.parse returned an unsupported Constant type')


def _error(error):
    def frozen(value):
        if type(value) in (list, tuple):
            return [frozen(item) for item in value]
        return _constant(value)
    return {'module': type(error).__module__, 'type': type(error).__qualname__,
            'message': str(error), 'args': frozen(error.args)}


def observe_syntax(payload, path):
    nodes, identities, scopes = [], {}, []
    def observe(value):
        if isinstance(value, ast.AST):
            identity = identities.get(id(value))
            if identity is None:
                identity = len(nodes)
                identities[id(value)] = identity
                item = {'kind': type(value).__name__, 'fields': {},
                        'attributes': {name: getattr(value, name)
                                       for name in value._attributes if hasattr(value, name)}}
                nodes.append(item)
                item['fields'] = {name: (_constant(getattr(value, name))
                                        if isinstance(value, ast.Constant) and name == 'value'
                                        else observe(getattr(value, name)))
                                  for name in value._fields if hasattr(value, name)}
            return {'node': identity}
        if type(value) in (list, tuple):
            return [observe(item) for item in value]
        return value
    def scope(tree, parent):
        identity = len(scopes)
        members, children = _scope_contents(tree)
        item = {'root': observe(tree), 'parent': parent,
                'nodes': [observe(node) for node in members], 'children': []}
        scopes.append(item)
        item['children'] = [scope(child, identity) for child in children]
        return identity
    try:
        # Exactly the original bytes/encoding/NFKC/full grammar acquisition.
        tree = ast.parse(payload, filename=path)
        scope(tree, None)
        error = None
    except (SyntaxError, ValueError, TypeError, UnicodeError, RecursionError) as failure:
        error = _error(failure)
    return {'nodes': nodes, 'scopes': scopes, 'exception': error}


def acquire_source_ast(files):
    """files carry actual held bytes, not saved clean/PASS/AST declarations."""
    rows = []
    for source in files:
        payload, path = source['bytes'], source['path']
        if type(payload) is not bytes:
            raise TypeError('owned parser input is not complete exact bytes')
        row = {'path': path, 'payloadB64': _b64(payload),
               'syntax': observe_syntax(payload, path), 'exception': None}
        if 'phase' in source:
            row['phase'] = source['phase']
        rows.append(row)
    # The original importlib.machinery suffix list is its initial _imp result;
    # this protected producer runs before any target code can mutate that list.
    runtime = {'implementation': sys.implementation.name,
               'cacheTag': sys.implementation.cache_tag,
               'version': list(sys.version_info),
               'stdlibNames': sorted(sys.stdlib_module_names),
               'extensionSuffixes': _imp.extension_suffixes()}
    return {'runtime': runtime, 'files': rows}


# Fixed provider entry. The shared parser acquisition above is byte-for-byte
# EvaluationProducerNative's owned primitive capture, not a second AST policy.
import json
import os
from pathlib import PurePosixPath
import stat

_INPUT = '/logical/worldline-syntax-input'
_REPORT = '/run/worldline-report/report'
_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
_MAX_BYTES = 268435456
_MAX_ENTRIES = 100000


def _relative(value):
    return (type(value) is str and bool(value) and "\0" not in value
            and not value.startswith("/") and str(PurePosixPath(value)) == value
            and all(part not in (".", "..") for part in value.split("/")))


def _object(value):
    return {'device': value.st_dev, 'inode': value.st_ino, 'mode': value.st_mode,
            'uid': value.st_uid, 'gid': value.st_gid, 'nlink': value.st_nlink,
            'size': value.st_size, 'mtime_ns': value.st_mtime_ns,
            'ctime_ns': value.st_ctime_ns}


def _signature(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _close(fd, record):
    try:
        os.close(fd)
        record['closeReturn'], record['closeErrno'] = 0, 0
    except OSError as error:
        record['closeReturn'], record['closeErrno'] = -1, error.errno
        raise


def _held_sources():
    """Original _capture traversal/domain with additional primitive FD receipts."""
    sources, records, directories = [], [], ['']
    directory_records, total = [], 0
    root = os.open(_INPUT, _DIR)
    root_close = {'fd': root}
    try:
        def visit(directory, prefix, depth=0):
            nonlocal total
            if depth > 128:
                raise ValueError('staged tree exceeds existing depth bound')
            before = os.fstat(directory)
            names = sorted(os.listdir(directory))
            directory_record = {'fd': directory, 'path': prefix,
                                'before': _object(before), 'names': names}
            directory_records.append(directory_record)
            for name in names:
                relative = prefix + name
                if not _relative(relative):
                    raise ValueError('invalid staged member name')
                named = os.stat(name, dir_fd=directory, follow_symlinks=False)
                if stat.S_ISDIR(named.st_mode):
                    child = os.open(name, _DIR, dir_fd=directory)
                    close_record = {'fd': child, 'path': relative,
                                    'openReturn': child, 'openErrno': 0}
                    try:
                        opened = os.fstat(child)
                        if _signature(opened) != _signature(named):
                            raise ValueError('staged directory changed while opening')
                        directories.append(relative)
                        if len(directories) + len(sources) > _MAX_ENTRIES:
                            raise ValueError('staged tree exceeds existing entry bound')
                        visit(child, relative + '/', depth + 1)
                        if _signature(os.fstat(child)) != _signature(opened):
                            raise ValueError('staged directory changed while reading')
                    finally:
                        _close(child, close_record)
                        directory_records.append(close_record)
                elif stat.S_ISREG(named.st_mode) and named.st_nlink == 1:
                    child = os.open(name, _FILE, dir_fd=directory)
                    row = {'path': relative, 'fd': child, 'parentFd': directory,
                           'openReturn': child, 'openErrno': 0,
                           'named': _object(named), 'reads': []}
                    records.append(row)
                    try:
                        opened = os.fstat(child)
                        row['before'] = _object(opened)
                        if _signature(opened) != _signature(named):
                            raise ValueError('staged file changed while opening')
                        if total + opened.st_size > _MAX_BYTES:
                            raise ValueError('staged tree exceeds existing byte bound')
                        chunks, size = [], 0
                        while True:
                            read = {'fd': child, 'offset': size, 'return': None,
                                    'errno': 0, 'bytes': None}
                            row['reads'].append(read)
                            try:
                                chunk = os.read(child, min(1048576, opened.st_size - size + 1))
                                read['return'] = len(chunk)
                                read['bytes'] = {'encoding': 'base64', 'payload': _b64(chunk)}
                            except OSError as error:
                                read['return'], read['errno'] = -1, error.errno
                                raise
                            if not chunk:
                                break
                            size += len(chunk)
                            if size > opened.st_size:
                                raise ValueError('staged file grew while reading')
                            chunks.append(chunk)
                        after = os.fstat(child)
                        row['after'] = _object(after)
                        if size != opened.st_size or _signature(after) != _signature(opened):
                            raise ValueError('staged file changed while reading')
                        payload = b''.join(chunks)
                    finally:
                        _close(child, row)
                    total += len(payload)
                    row['bytes'] = {'encoding': 'base64', 'payload': _b64(payload)}
                    sources.append({'path': relative, 'bytes': payload})
                    if len(directories) + len(sources) > _MAX_ENTRIES:
                        raise ValueError('staged tree exceeds existing entry bound')
                    row['edgeAfter'] = _object(os.stat(name, dir_fd=directory,
                                                      follow_symlinks=False))
                else:
                    raise ValueError('staged member is not an ordinary singly linked file/directory')
                if _signature(os.stat(name, dir_fd=directory, follow_symlinks=False)) != _signature(named):
                    raise ValueError('staged pathname changed while reading')
            directory_record['afterNames'] = sorted(os.listdir(directory))
            after = os.fstat(directory)
            directory_record['after'] = _object(after)
            if names != directory_record['afterNames'] or _signature(after) != _signature(before):
                raise ValueError('staged directory inventory changed while reading')
        visit(root, '')
    finally:
        _close(root, root_close)
    return sorted(sources, key=lambda row: row['path']), {
        'root': root_close, 'directories': sorted(directories),
        'directoryReads': directory_records, 'sourceReads': records}


def _main():
    sources, input_observations = _held_sources()
    profile = acquire_source_ast(sources)
    artifact = {'schema': 'worldline-protected-source-syntax-artifact-v1',
                'profile': profile, 'input': input_observations}
    # Constant raw values are typed byte/binary64 operands above. No target code
    # ran; this serializer introduces no JSON integer/nonfinite conversion cap.
    output = json.dumps(artifact, ensure_ascii=True, allow_nan=False,
                        separators=(',', ':')).encode('ascii')
    fd = os.open(_REPORT, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(output):
            count = os.write(fd, output[offset:])
            if count <= 0:
                raise OSError('syntax artifact write made no progress')
            offset += count
        os.fsync(fd)
    finally:
        os.close(fd)


if __name__ == '__main__':
    _main()
