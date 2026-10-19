"""Ordinary-process serialization and diagnostic-failure controls.

No protected-host or whole-system acceptance. The diagnostic fixture deliberately
uses the separately retained, still-failing large-successor obligation.
"""
import ctypes as C
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

P, N = C.c_void_p, C.c_size_t
SHAPES = {
    'wl_custody_load_decide_v2': (P, N, P, P),
    'wl_custody_mutation_decide_v2': (P, N, P, P, P, N, P),
    'wl_custody_cleanup_decide_v2': (P, N, P, P),
    'wl_custody_closed_decide_v2': (P, N, P, P),
    'wl_custody_context_view_v2': (P, N, P, P, P, N, P),
    'wl_custody_retry_decide_v2': (P, N, P, P, P, N, P),
    'wl_custody_serving_decide_v2': (P, N, P, P),
    'wl_custody_successor_le_v2': (P, N, P, N, P),
    'wl_custody_provision_decide_v2': (P, N, P, N, N, N, N, P, N),
    **{f'wl_root_worker_output_{name}_v1': (P, N, P, P, P, N, P)
       for name in ('next', 'replay', 'written', 'prefix')},
}


def private_guard_functions(lib):
    """Inspect the same unstripped ELF, without changing its exported ABI.

    This Linux test-only observation uses local C symbol offsets relative to
    an exported function in that very image. A separate helper library would
    own a different mutex and could not test the production guard.
    """
    path = Path(os.environ['WORLDLINE_CORE_LIB']).resolve(strict=True)
    with tempfile.TemporaryFile(mode='w+t') as output:
        subprocess.run(['nm', '--defined-only', '--format=posix', str(path)],
                       stdout=output, timeout=10, check=True)
        if output.tell() > 16 * 1024 * 1024:
            raise ValueError('native symbol inventory exceeds test budget')
        output.seek(0)
        inventory = output.read()
    names = ('wl_native_call_enter_v1', 'wl_native_call_leave_v1',
             'wl_native_call_depth_v1', 'wl_custody_load_decide_v2')
    symbols = {}
    for line in inventory.splitlines():
        fields = line.split()
        if fields and fields[0] in names:
            if len(fields) != 4 or fields[1] not in ('t', 'T') or fields[0] in symbols:
                raise ValueError('missing or ambiguous native function identity')
            symbols[fields[0]] = int(fields[2], 16)
    if set(symbols) != set(names):
        raise ValueError('test requires the unstripped canonical library')
    class DlInfo(C.Structure):
        _fields_ = [('path', C.c_char_p), ('base', P), ('symbol', C.c_char_p),
                    ('address', P)]
    anchor = C.cast(lib.wl_custody_load_decide_v2, P).value
    lookup = C.CDLL(None).dladdr
    lookup.argtypes, lookup.restype = [P, C.POINTER(DlInfo)], C.c_int
    identity = DlInfo()
    if not lookup(anchor, C.byref(identity)) or Path(os.fsdecode(identity.path)).resolve() != path:
        raise ValueError('loaded native library identity differs from symbol source')
    if identity.base + symbols[names[3]] != anchor:
        raise ValueError('native symbol relocation does not match loaded image')
    return tuple(C.CFUNCTYPE(kind)(identity.base + symbols[name])
                 for name, kind in zip(names[:3], (C.c_int, C.c_int, C.c_uint)))


class CustodyNativeGuard(unittest.TestCase):
    def test_every_repaired_entry_serializes_and_releases_its_guard(self):
        lib = C.CDLL(os.environ['WORLDLINE_CORE_LIB'])
        enter, leave, depth = private_guard_functions(lib)
        for name, shape in SHAPES.items():
            with self.subTest(export=name):
                function = getattr(lib, name)
                function.argtypes, function.restype = shape, C.c_int
                args = tuple(None if kind is P else 0 for kind in shape)
                started, finished, answer = threading.Event(), threading.Event(), []
                def invoke():
                    started.set()
                    answer.append((function(*args), depth()))
                    finished.set()
                self.assertEqual(enter(), 0)
                thread = threading.Thread(target=invoke, daemon=True)
                try:
                    self.assertEqual(depth(), 1)
                    self.assertEqual(function(*args), 1)
                    self.assertEqual(depth(), 1)
                    thread.start()
                    self.assertTrue(started.wait(5))
                    self.assertFalse(finished.wait(0.1))
                finally:
                    self.assertEqual(leave(), 0)
                    if thread.ident is not None:
                        thread.join(5)
                self.assertFalse(thread.is_alive())
                self.assertEqual(answer, [(1, 0)])
                self.assertEqual(depth(), 0)

    def test_failed_diagnostic_preserves_primary_failure_and_process(self):
        # The functional test still requires this padded zero to succeed.
        # Here its existing Storage_Error is only a real handler stimulus.
        worker = '''
import ctypes as C, json, os
lib = C.CDLL(os.environ['WORLDLINE_CORE_LIB'])
control = lib.wl_native_diagnostic_control_v1
control.argtypes, control.restype = [C.c_uint32], C.c_uint32
function = lib.wl_custody_successor_le_v2
function.argtypes = [C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t,C.POINTER(C.c_uint64)]
function.restype = C.c_int
data = (C.c_ubyte * 4096)()
output = (C.c_ubyte * 1)()
needed = C.c_uint64(999)
os.close(2)
code = function(data, len(data), output, len(output), C.byref(needed))
print(json.dumps(dict(code=code, needed=needed.value,
    diagnostic_status=control(0), next_invalid=function(None,0,None,0,None))))
'''
        result = subprocess.run([sys.executable, '-c', worker], capture_output=True,
                                text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        facts = json.loads(result.stdout)
        self.assertEqual(facts['code'], 4)
        self.assertEqual(facts['needed'], 0)
        self.assertEqual(facts['diagnostic_status'], 1)
        self.assertEqual(facts['next_invalid'], 1)


if __name__ == '__main__':
    unittest.main()
