#!/usr/bin/env python3
"""Optional finite-case ctypes dispatch observer; never a native-entry proof.

This scratch observer replaces only three CDLL attribute lookups with forwarding
objects. The exact original _CFuncPtr receives the original argument objects once.
It neither authorizes work nor supplies a result. Instrumentation can affect
timing/allocation; only explicitly qualified finite correspondence may be claimed.
"""
from __future__ import annotations
import ctypes
import hashlib
import inspect
import json
import os
from pathlib import Path
import time
import uuid

SYMBOLS = ('wl_resource_ledger_compute', 'wl_resource_ledger_headroom',
           'wl_resource_policy_admit')

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def typename(kind):
    return kind.__module__ + '.' + kind.__qualname__ if kind is not None else None

def signature(function):
    return {'argtypes': None if function.argtypes is None else [typename(t) for t in function.argtypes],
            'restype': typename(function.restype),
            'errcheck_present': hasattr(function, 'errcheck')}

class CaptureRefusal(Exception):
    pass

class EventLog:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(exist_ok=False)
        self.stream = (self.directory/'dispatch.jsonl').open('x', buffering=1)
        self.errors = []
        self.step = None
        self.completed = []

    def emit(self, event):
        # No arbitrary repr(args) or payload is written by this helper.
        self.stream.write(json.dumps(event, sort_keys=True) + '\n')
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def best_effort(self, operation, label):
        try:
            return operation()
        except Exception as error:
            self.errors.append({'operation': label, 'exception_type': type(error).__name__,
                                'message': str(error)})
            return None

    def finish(self):
        self.stream.close()
        return {'event_path': str(self.directory/'dispatch.jsonl'),
                'event_sha256': digest(self.directory/'dispatch.jsonl'),
                'observation_errors': self.errors, 'completed_calls': self.completed,
                'claim': 'UNVERIFIED until finite observer qualification and exact source/library joins are reviewed',
                'native_instruction_entry': 'UNVERIFIED', 'independent_acceptance': 'NOT PERFORMED'}

class ObservedFunction:
    """Forwarding object. Properties preserve production ABI configuration."""
    def __init__(self, function, name, provenance, snapshot, log):
        if not isinstance(function, ctypes._CFuncPtr):
            raise TypeError('Observer requires an actual ctypes._CFuncPtr')
        self.original = function
        self.name = name
        self.provenance = provenance
        self.snapshot = snapshot
        self.log = log

    @property
    def argtypes(self):
        return self.original.argtypes

    @argtypes.setter
    def argtypes(self, value):
        self.original.argtypes = value

    @property
    def restype(self):
        return self.original.restype

    @restype.setter
    def restype(self, value):
        self.original.restype = value

    def __call__(self, *args, **kwargs):
        call_id = uuid.uuid4().hex
        caller = inspect.currentframe().f_back
        try:
            site = {'path': caller.f_code.co_filename, 'function': caller.f_code.co_name,
                    'line': caller.f_lineno}
        finally:
            del caller
        base = {'id': call_id, 'symbol': self.name, 'step': self.log.step,
                'source_site': site, 'provenance': self.provenance,
                'signature': signature(self.original), 'kwargs_present': bool(kwargs)}
        saved_errno = ctypes.get_errno()
        before = self.log.best_effort(lambda: self.snapshot(args), 'capture-before')
        written_before = self.log.best_effort(lambda: (self.log.emit({**base, 'event': 'before-underlying-ctypes-call',
            'monotonic_ns': time.monotonic_ns(), 'arguments': before}), True)[1], 'write-before')
        ctypes.set_errno(saved_errno)
        try:
            # This is the sole dispatch. No copied arguments, substituted return,
            # callback, alternative kernel or Python policy decision is used.
            returned = self.original(*args, **kwargs)
        except BaseException as error:
            native_errno = ctypes.get_errno()
            after = self.log.best_effort(lambda: self.snapshot(args), 'capture-raised')
            self.log.best_effort(lambda: self.log.emit({**base, 'event': 'underlying-ctypes-raised',
                'monotonic_ns': time.monotonic_ns(), 'exception_type': type(error).__name__,
                'exception_message': str(error), 'exception_identity': id(error),
                'arguments': after, 'private_errno': native_errno,
                'native_entry': 'UNVERIFIED; ctypes conversion may have raised before native entry'}), 'write-raised')
            ctypes.set_errno(native_errno)
            raise
        else:
            native_errno = ctypes.get_errno()
            after = self.log.best_effort(lambda: self.snapshot(args), 'capture-after')
            event = {**base, 'event': 'underlying-ctypes-returned',
                'monotonic_ns': time.monotonic_ns(), 'return_value': returned,
                'return_python_type': type(returned).__name__, 'arguments': after,
                'private_errno': native_errno}
            written = self.log.best_effort(lambda: (self.log.emit(event), True)[1], 'write-returned')
            if before is not None and after is not None and written_before and written:
                self.log.completed.append({'id': call_id, 'symbol': self.name, 'step': self.log.step})
            ctypes.set_errno(native_errno)
            return returned

class Capture:
    """Read only raw ABI bytes and layout fields from original owned arguments.

    The observer budget limits evidence capture, never the accepted product
    domain. An over-budget capture is incomplete evidence and still forwards.
    """
    def __init__(self, ledger, policy, byte_budget=1000000):
        self.ledger = ledger
        self.policy = policy
        self.byte_budget = byte_budget

    def _regions(self, name, args):
        l, p = self.ledger, self.policy
        if name == SYMBOLS[0]:
            data, data_len, rows, count, detail, detail_len, total, total_len, details, result = args
            return [('data',data,data_len,None,None), ('rows',rows,count*ctypes.sizeof(l._Row),l._Row,count),
                    ('detail_data',detail,detail_len,None,None), ('total_data',total,total_len,None,None),
                    ('details',details,count*ctypes.sizeof(l._Quantity),l._Quantity,count),
                    ('result',result,ctypes.sizeof(l._Result),l._Result,None)]
        if name == SYMBOLS[1]:
            data, data_len, available, withheld, floor, output, output_len, result = args
            return [('data',data,data_len,None,None), ('available',available,ctypes.sizeof(l._Quantity),l._Quantity,None),
                    ('withheld',withheld,ctypes.sizeof(l._Quantity),l._Quantity,None), ('floor',floor,ctypes.sizeof(l._Quantity),l._Quantity,None),
                    ('output',output,output_len,None,None), ('result',result,ctypes.sizeof(l._Result),l._Result,None)]
        if name == SYMBOLS[2]:
            data, data_len, inputs, disks, count, result = args
            return [('data',data,data_len,None,None), ('input',inputs,ctypes.sizeof(p._Input),p._Input,None),
                    ('disks',disks,count*ctypes.sizeof(p._Disk),p._Disk,count),
                    ('result',result,ctypes.sizeof(p._Result),p._Result,None)]
        raise CaptureRefusal('Unknown ABI symbol')

    @staticmethod
    def fields(value):
        return {name: (Capture.fields(getattr(value,name)) if isinstance(getattr(value,name),ctypes.Structure)
                       else getattr(value,name)) for name,_ in value._fields_}

    def snapshot(self, name, args):
        regions = self._regions(name,args)
        lengths = [entry[2] for entry in regions]
        if any(type(size) is not int or size < 0 for size in lengths):
            raise CaptureRefusal('Unexpected noncanonical ABI extent')
        if sum(lengths) > self.byte_budget:
            raise CaptureRefusal('Observer capture budget exceeded; product call remains forwarded')
        result = {'raw_arguments': [{'python_type': type(arg).__name__, 'scalar': arg if type(arg) is int else None,
                     'address': ctypes.cast(arg,ctypes.c_void_p).value if type(arg) is not int else None}
                    for arg in args], 'regions': []}
        for label, value, size, kind, count in regions:
            address = ctypes.cast(value,ctypes.c_void_p).value
            if size and address is None:
                raise CaptureRefusal('Nonempty ABI region has null pointer')
            raw = b'' if not size else ctypes.string_at(value,size)
            row = {'name': label, 'address': address, 'byte_length': size,
                   'bytes_hex': raw.hex(), 'sha256': hashlib.sha256(raw).hexdigest()}
            if kind is not None:
                row['record_type'] = typename(kind)
                row['record_size'] = ctypes.sizeof(kind)
                row['field_offsets'] = {n:getattr(kind,n).offset for n,_ in kind._fields_}
                if count is None:
                    row['fields'] = self.fields(kind.from_buffer_copy(raw))
                else:
                    row['record_count'] = count
                    row['records'] = [self.fields(v) for v in (kind*count).from_buffer_copy(raw)]
            result['regions'].append(row)
        return result

class AuthorityObserver:
    def __init__(self, core, directory, expected_library, expected_library_sha256):
        from worldline import resource_ledger, resource_policy
        self.core = core
        self.log = EventLog(directory)
        self.saved = {}
        self.wrappers = {}
        self.restored = False
        self.library = Path(expected_library).resolve(strict=True)
        if core.library_path != self.library or digest(self.library) != expected_library_sha256:
            raise RuntimeError('Observer library identity mismatch')
        # Original admission checks and exact production struct classes configure
        # the genuine pointers before observing calls. They do not decide policy.
        resource_ledger._api(core)
        resource_ledger._headroom_api(core)
        resource_policy._api(core)
        capture = Capture(resource_ledger,resource_policy)
        class DlInfo(ctypes.Structure):
            _fields_ = [('filename',ctypes.c_char_p),('base',ctypes.c_void_p),
                        ('symbol',ctypes.c_char_p),('address',ctypes.c_void_p)]
        libdl = ctypes.CDLL(None)
        dladdr = libdl.dladdr
        dladdr.argtypes = [ctypes.c_void_p,ctypes.POINTER(DlInfo)]
        dladdr.restype = ctypes.c_int
        for name in SYMBOLS:
            function = getattr(core._lib,name)
            if not isinstance(function,ctypes._CFuncPtr):
                raise RuntimeError('Production symbol is not a genuine ctypes function')
            address = ctypes.cast(function,ctypes.c_void_p).value
            info = DlInfo()
            if (dladdr(address,ctypes.byref(info)) == 0 or not info.filename
                or Path(os.fsdecode(info.filename)).resolve(strict=True) != self.library
                or info.symbol != name.encode('ascii') or info.address != address):
                raise RuntimeError('Production symbol/address/library mismatch')
            provenance = {'symbol':name,'address':address,'library':str(self.library),
                          'library_sha256':expected_library_sha256,'library_base':info.base,
                          'function_type':typename(type(function)),
                          'configured_signature':signature(function)}
            self.saved[name] = function
            self.wrappers[name] = ObservedFunction(function,name,provenance,
                lambda args,name=name: capture.snapshot(name,args),self.log)
        for name, wrapper in self.wrappers.items():
            setattr(core._lib,name,wrapper)

    def step(self, name):
        self.log.step = name

    def finish(self):
        errors = []
        for name,original in self.saved.items():
            if getattr(self.core._lib,name) is not self.wrappers[name]:
                errors.append('CDLL attribute changed while observed: '+name)
            else:
                setattr(self.core._lib,name,original)
            if getattr(self.core._lib,name) is not original:
                errors.append('Original CDLL attribute restoration not established: '+name)
        self.restored = not errors
        outcome = self.log.finish()
        outcome.update({'restored_original_functions':self.restored,'restoration_errors':errors,
                        'library_sha256_after':digest(self.library),
                        'observer_sha256':digest(__file__),
                        'runtime_bindings': {m.__name__: {'path':m.__file__,'sha256':digest(m.__file__)}
                            for m in (self._module('worldline.resource_ledger'),self._module('worldline.resource_policy'))}})
        return outcome

    @staticmethod
    def _module(name):
        import sys
        return sys.modules[name]
