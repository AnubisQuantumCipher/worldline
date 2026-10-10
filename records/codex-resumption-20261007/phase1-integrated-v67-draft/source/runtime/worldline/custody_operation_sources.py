"""Original factual mapped-kernel acquisition, independent of target constructors."""
from pathlib import Path
import ctypes as C
import os
from .protected_startup import private_bytes


def capture_kernel_material(core, kernel_build):
    """Retain the complete original recovery capture; never select an action."""
    from intent_gate import protected
    from .protected_recovery_capture import refuse
    if core.library_source == 'environment':
        refuse('RECOVERY_ENVIRONMENT_NATIVE_LIBRARY')
    library = Path(core.library_path)
    protected(library)
    raw = library.read_bytes()
    info = library.stat()
    build = private_bytes(kernel_build)
    segments = []
    ranges = []
    for line in Path('/proc/self/maps').read_text().splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6 or fields[5] != str(library):
            continue
        bounds, permissions, offset, device, inode, _path = fields
        start, end = (int(value, 16) for value in bounds.split('-'))
        mapped = Path('/proc/self/map_files') / bounds
        try:
            fd = os.open(mapped, os.O_RDONLY | os.O_CLOEXEC)
        except OSError:
            refuse('RECOVERY_MAPPED_DESCRIPTOR_UNAVAILABLE')
        try:
            measured = os.fstat(fd)
            with os.fdopen(os.dup(fd), 'rb') as stream:
                contents = stream.read()
            if (measured.st_dev, measured.st_ino) != (info.st_dev, info.st_ino) or contents != raw:
                refuse('RECOVERY_MAPPED_DESCRIPTOR_DIFFERS')
        finally:
            os.close(fd)
        segments.append({'permissions': permissions, 'offset': offset, 'device': device,
                         'inode': inode, 'mapped_length': end - start})
        ranges.append((start, end, permissions))
    if not segments:
        refuse('RECOVERY_NATIVE_MAPPING_ABSENT')
    symbols = ('wl_collapse_decide_raw_evaluation_v3', 'wl_recovery_authorization_decide_v3',
               'wl_recovery_protocol_decide_v1')
    for name in symbols:
        try:
            address = C.cast(getattr(core._lib, name), C.c_void_p).value
        except AttributeError:
            refuse('RECOVERY_EXACT_NATIVE_ABI_UNAVAILABLE')
        if address is None or not any(start <= address < end and 'x' in perms
                                      for start, end, perms in ranges):
            refuse('RECOVERY_NATIVE_SYMBOL_MAPPING_DIFFERS')
    after = library.stat()
    if (info.st_dev, info.st_ino, info.st_size, info.st_ctime_ns, info.st_mtime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_ctime_ns, after.st_mtime_ns):
        refuse('RECOVERY_NATIVE_LIBRARY_CHANGED')
    return {'library_path': os.fsencode(library), 'device': info.st_dev, 'inode': info.st_ino,
            'library_bytes': raw, 'segments': segments, 'symbols': symbols, 'build_bytes': build}
