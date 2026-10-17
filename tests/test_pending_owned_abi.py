"""Additive actual-native v1/v2 extent, ownership and read-only alias controls.

No fake kernel, arbitrary mapped-address claim, or replacement lifetime roster.
Run only against the explicitly selected integrated shared library.
"""
import ctypes as C
import gc
import os
from pathlib import Path
import unittest

from worldline import pending_kernel as V1
from worldline import pending_kernel_v2 as V2

LIBRARY = Path(os.environ.get("WORLDLINE_CORE_LIB", Path(__file__).resolve().parents[1] / "lib/libworldline_core.so")).resolve()


def empty_span(module):
    return module.Span(1, 0)


def absent_cursor(module):
    # Inactive payloads are intentionally malformed and must remain ignored.
    return module.Cursor(0, module.Span(-1, -1), module.Span(-1, -1))


def request(module, version):
    r = module.Request()
    r.version = version
    r.operation = 0
    for name in ("store_id", "subject", "content", "run", "proposed_epoch"):
        setattr(r, name, empty_span(module))
    r.authority_head = absent_cursor(module)
    r.target_head = absent_cursor(module)
    if version == 2:
        r.required = module.OptionalRequirement(0, module.Span(-1, -1))
    return r


def row(module, version):
    r = module.Row()
    for name in ("store_id", "subject", "content", "run", "sequence"):
        setattr(r, name, empty_span(module))
    r.previous = absent_cursor(module)
    if version == 2:
        r.requirement = module.OptionalRequirement(0, module.Span(-1, -1))
    return r


def raw_call(kernel, module, input_address, output_address):
    return kernel.call(C.cast(input_address, C.POINTER(module.Request)),
                       C.cast(output_address, C.POINTER(module.Result)))


class PendingOwnedABI(unittest.TestCase):
    def versions(self):
        for version, module in ((1, V1), (2, V2)):
            yield version, module, module.PendingKernel(LIBRARY)

    def assert_refused_untouched(self, kernel, module, r):
        result = module.Result()
        C.memset(C.addressof(result), 0xA5, C.sizeof(result))
        before = bytes(result)
        self.assertEqual(kernel.call(C.byref(r), C.byref(result)), 255)
        self.assertEqual(bytes(result), before)

    def test_all_layouts_and_unknown_sentinels(self):
        for version, module, kernel in self.versions():
            with self.subTest(version=version):
                size = getattr(kernel.library, f"wl_pending_layout_size_v{version}")
                alignment = getattr(kernel.library, f"wl_pending_layout_alignment_v{version}")
                offset = getattr(kernel.library, f"wl_pending_layout_offset_v{version}")
                records = (module.Span, module.Cursor, module.Row, module.Request, module.Result)
                if version == 2:
                    records += (module.OptionalRequirement,)
                for kind, record in enumerate(records, 1):
                    self.assertEqual(size(kind), C.sizeof(record))
                    self.assertEqual(alignment(kind), C.alignment(record))
                    for field, (name, _) in enumerate(record._fields_, 1):
                        self.assertEqual(offset(kind, field), getattr(record, name).offset)
                    self.assertEqual(offset(kind, 0), module.MAX_COUNT)
                    self.assertEqual(offset(kind, len(record._fields_) + 1), module.MAX_COUNT)
                for kind in (0, len(records) + 1, C.c_uint32(-1).value):
                    self.assertEqual(size(kind), module.MAX_COUNT)
                    self.assertEqual(alignment(kind), module.MAX_COUNT)
                    self.assertEqual(offset(kind, 1), module.MAX_COUNT)

    def test_fixed_null_alignment_wrap_and_request_output_overlap(self):
        for version, module, kernel in self.versions():
            r, result = request(module, version), module.Result()
            C.memset(C.addressof(result), 0xA5, C.sizeof(result))
            before = bytes(result)
            maximum = C.c_void_p(-1).value
            for address in (None, C.addressof(r) + 1, maximum - maximum % C.alignment(module.Request)):
                with self.subTest(version=version, address=address):
                    self.assertEqual(raw_call(kernel, module, address, C.addressof(result)), 255)
                    self.assertEqual(bytes(result), before)
            self.assertEqual(raw_call(kernel, module, C.addressof(r), None), 255)
            self.assertEqual(raw_call(kernel, module, C.addressof(r), C.addressof(result) + 1), 255)
            before_request = bytes(r)
            self.assertEqual(raw_call(kernel, module, C.addressof(r), C.addressof(r)), 255)
            self.assertEqual(bytes(r), before_request)

    def test_nested_numeric_malformed_and_mutable_overlap(self):
        for version, module, kernel in self.versions():
            cases = ({"version": 0}, {"operation": 2}, {"data_length": -1},
                     {"row_count": -1}, {"row_count": module.MAX_COUNT},
                     {"data": None, "data_length": 1},
                     {"rows": None, "row_count": 1},
                     {"data": C.c_void_p(-1).value, "data_length": 2},
                     {"authority_head": module.Cursor(2, empty_span(module), empty_span(module))},
                     {"subject": module.Span(0, 0)})
            for changed in cases:
                with self.subTest(version=version, changed=changed):
                    r = request(module, version)
                    for name, value in changed.items():
                        setattr(r, name, value)
                    self.assert_refused_untouched(kernel, module, r)
            rows = (module.Row * 1)(row(module, version))
            r = request(module, version)
            r.rows, r.row_count = C.addressof(rows) + 1, 1
            self.assert_refused_untouched(kernel, module, r)
            # Result is live and aligned, but mutable aliasing is forbidden.
            for target in ("data", "rows"):
                output = C.create_string_buffer(max(C.sizeof(module.Result), C.sizeof(module.Row)))
                r = request(module, version)
                if target == "data":
                    r.data, r.data_length = C.addressof(output), 1
                else:
                    r.rows, r.row_count = C.addressof(output), 1
                before = bytes(output)
                self.assertEqual(raw_call(kernel, module, C.addressof(r), C.addressof(output)), 255)
                self.assertEqual(bytes(output), before)

    def test_zero_null_extents_and_absent_payloads_preserve_semantic_refusal(self):
        for version, module, kernel in self.versions():
            r, result = request(module, version), module.Result()
            self.assertIsNone(r.data)
            self.assertIsNone(r.rows)
            self.assertEqual(kernel.call(C.byref(r), C.byref(result)), 0)
            self.assertEqual(result.reason, module.Reason.EPOCH_PROPOSAL_INVALID)
            self.assertEqual(result.selected, 0)
            self.assertEqual((result.sequence.first, result.sequence.length), (1, 0))
            if version == 2:
                self.assertEqual(result.requirement.present, 0)
                self.assertEqual((result.requirement.value.first, result.requirement.value.length), (1, 0))

    def test_all_raw_row_scalar_validation_before_conversion(self):
        for version, module, kernel in self.versions():
            changes = [{name: module.Span(0, 0)}
                       for name in ("store_id", "subject", "content", "run", "sequence")]
            changes += [{"linked": 2}, {"previous": module.Cursor(2, empty_span(module), empty_span(module))}]
            if version == 2:
                changes += [{"requirement": module.OptionalRequirement(2, empty_span(module))},
                            {"requirement": module.OptionalRequirement(1, module.Span(0, 0))}]
            for changed in changes:
                with self.subTest(version=version, changed=changed):
                    item = row(module, version)
                    for name, value in changed.items():
                        setattr(item, name, value)
                    rows = (module.Row * 1)(item)
                    r = request(module, version)
                    r.rows, r.row_count = C.addressof(rows), 1
                    self.assert_refused_untouched(kernel, module, r)
            if version == 2:
                for optional in (module.OptionalRequirement(2, empty_span(module)),
                                 module.OptionalRequirement(1, module.Span(0, 0))):
                    r = request(module, version)
                    r.required = optional
                    self.assert_refused_untouched(kernel, module, r)

    def test_read_only_data_row_alias_is_accepted_and_not_mutated(self):
        for version, module, kernel in self.versions():
            storage = C.create_string_buffer(C.sizeof(module.Row) + 1)
            item = module.Row.from_buffer(storage)
            C.memmove(C.addressof(item), C.addressof(row(module, version)), C.sizeof(item))
            item.sequence = module.Span(C.sizeof(item) + 1, 1)
            storage[C.sizeof(item)] = b"\x01"
            r, result = request(module, version), module.Result()
            r.operation = 1
            r.data, r.data_length = C.addressof(storage), C.sizeof(storage)
            r.rows, r.row_count = C.addressof(item), 1
            r.authority_head = module.Cursor(1, item.sequence, item.run)
            before = bytes(storage)
            gc.collect()
            self.assertEqual(kernel.call(C.byref(r), C.byref(result)), 0)
            self.assertEqual(result.reason, module.Reason.WRITE_PENDING)
            self.assertEqual(result.selected, 1)
            self.assertEqual(bytes(storage), before)

    def test_read_only_request_data_alias_is_accepted_and_not_mutated(self):
        for version, module, kernel in self.versions():
            storage = C.create_string_buffer(C.sizeof(module.Request) + 1)
            r = module.Request.from_buffer(storage)
            value = request(module, version)
            C.memmove(C.addressof(r), C.addressof(value), C.sizeof(r))
            r.data, r.data_length = C.addressof(storage), C.sizeof(storage)
            r.proposed_epoch = module.Span(C.sizeof(r) + 1, 1)
            storage[C.sizeof(r)] = b"\x01"
            before = bytes(storage)
            result = module.Result()
            self.assertEqual(kernel.call(C.byref(r), C.byref(result)), 0)
            self.assertEqual(result.reason, module.Reason.RESERVE_NEW)
            self.assertEqual(bytes(storage), before)

    def test_actual_ctypes_caller_keeps_native_inputs_live_stable_and_output_exclusive(self):
        for version, module, kernel in self.versions():
            native = kernel.call
            observed = []

            def observing_actual_native(request_arg, result_arg):
                r = request_arg._obj
                output = result_arg._obj
                before_request = bytes(r)
                before_data = C.string_at(r.data, r.data_length)
                before_rows = C.string_at(r.rows, r.row_count * C.sizeof(module.Row))
                self.assertNotEqual(C.addressof(output), C.addressof(r))
                for start, extent in ((C.addressof(r), C.sizeof(r)),
                                      (r.data, r.data_length),
                                      (r.rows, r.row_count * C.sizeof(module.Row))):
                    self.assertTrue(C.addressof(output) + C.sizeof(output) <= start
                                    or start + extent <= C.addressof(output))
                gc.collect()
                status = native(request_arg, result_arg)
                self.assertEqual(bytes(r), before_request)
                self.assertEqual(C.string_at(r.data, r.data_length), before_data)
                self.assertEqual(C.string_at(r.rows, r.row_count * C.sizeof(module.Row)), before_rows)
                observed.append(status)
                return status

            kernel.call = observing_actual_native
            kwargs = dict(store_id=b"s\x00", subject=b"w", content=b"c", run=b"r",
                          authority=None, target=None, proposed_epoch=b"\x01", replay=False)
            if version == 2:
                kwargs["requirement"] = b""
            plan = kernel.decide([], **kwargs)
            self.assertEqual(plan.reason, module.Reason.RESERVE_NEW)
            self.assertEqual(plan.epoch, b"\x01")
            self.assertEqual(observed, [0])
            if version == 2:
                self.assertEqual(plan.requirement, b"")
            row_args = [b"s\x00", b"w", b"c", b"r", b"\x01", None, True]
            if version == 2:
                row_args.append(b"")
            retained = module.Intent(*row_args)
            kwargs.update(authority=(retained.epoch, retained.run),
                          target=(retained.epoch, retained.run),
                          proposed_epoch=b"", replay=True)
            replay = kernel.decide([retained], **kwargs)
            self.assertEqual(replay.reason, module.Reason.ALREADY_LINKED)
            self.assertEqual(replay.epoch, retained.epoch)
            self.assertEqual(replay.selected, 1)
            self.assertEqual(observed, [0, 0])
            if version == 2:
                self.assertEqual(replay.requirement, b"")


if __name__ == "__main__":
    unittest.main()
