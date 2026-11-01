"""Sole-revision counterexamples and controls; every fixture is in memory."""
import copy
import ast
from contextlib import ExitStack
import hashlib
import io
import json
from pathlib import Path
import types
import unittest
from unittest.mock import Mock, patch
import xgen_common as c
import xgen_diagnostics as d
import xgen_guard as g
import xgen_worker as w
import xgen_recovery as r
import progress_policy_source as ps


def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


class Stream(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class MemoryPath:
    def __init__(self, name, store):
        self.name, self.store = name, store

    def __str__(self):
        return self.name

    def __truediv__(self, name):
        return MemoryPath(self.name + "/" + name, self.store)

    def with_suffix(self, suffix):
        return MemoryPath(str(Path(self.name).with_suffix(suffix)), self.store)

    def open(self, mode):
        if mode != "xb" or self.name in self.store.files:
            raise RuntimeError("unexpected memory open")
        self.store.files[self.name] = Stream()
        return self.store.files[self.name]


class MemoryStore:
    def __init__(self, chunk=d.CHUNK):
        self.files, self.positions, self.fds, self.chunk = {}, {}, {}, chunk

    def add(self, name, raw):
        self.files[name] = Stream(raw)
        return MemoryPath(name, self)

    def regular(self, path, limit):
        name = str(path)
        if name not in self.files:
            raise FileNotFoundError(name)
        size = len(self.files[name].getvalue())
        if size > limit:
            raise RuntimeError("memory file cap")
        fd = len(self.fds) + 100
        self.fds[fd], self.positions[fd] = name, 0
        return fd, types.SimpleNamespace(st_size=size)

    def read(self, fd, maximum):
        raw, start = self.files[self.fds[fd]].getvalue(), self.positions[fd]
        data = raw[start:start+min(maximum, self.chunk)]
        self.positions[fd] += len(data)
        return data

    def fstat(self, fd):
        return types.SimpleNamespace(st_size=len(self.files[self.fds[fd]].getvalue()))

    def digest(self, path, _limit=c.FILE):
        return identity(self.files[str(path)].getvalue())

    def mocks(self, stack, allowed):
        stack.enter_context(patch.object(d, "regular", side_effect=self.regular))
        stack.enter_context(patch.object(d.os, "read", side_effect=self.read))
        stack.enter_context(patch.object(d.os, "fstat", side_effect=self.fstat))
        stack.enter_context(patch.object(d.os, "close"))
        stack.enter_context(patch.object(d, "progress_policy", return_value=allowed))


class FinalReceipt(io.StringIO):
    def __init__(self, failure):
        super().__init__()
        self.failure, self.final, self.initial_flushes = failure, False, 0

    def write(self, text):
        if '"normal_wrapper_exit"' in text:
            self.final = True
            if self.failure == "write":
                raise OSError("injected final write failure")
            if self.failure == "short":
                return super().write(text[:-1])
        return super().write(text)

    def flush(self):
        if self.final and self.failure == "flush":
            raise OSError("injected final flush failure")
        self.initial_flushes += 1
        return super().flush()


class MemorySelector:
    def __init__(self):
        self.entries = {}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def register(self, pipe, _event, channel):
        fd = pipe.fileno()
        self.entries[fd] = types.SimpleNamespace(fd=fd, data=channel, fileobj=pipe)

    def unregister(self, pipe):
        del self.entries[pipe.fileno()]

    def get_map(self):
        return self.entries

    def select(self, _timeout):
        return [(key, None) for key in self.entries.values()]


class RevisionCases(unittest.TestCase):
    def setUp(self):
        self.allowed = d.progress_policy()

    def stream_check(self, raw, allowed=None, chunk=d.CHUNK, expected=None):
        store = MemoryStore(chunk)
        path = store.add("capture", raw)
        with ExitStack() as stack:
            store.mocks(stack, self.allowed)
            result = d.validate_stream(path, expected or identity(raw), c.FILE,
                                       frozenset({b"Compile"}) if allowed is None else allowed)
        return result, store

    def guard_run(self, failure=None, code=0, monitor_failure=False):
        stream = FinalReceipt(failure)
        def monitored(_process, target):
            if failure == "budget":
                target.write("x" * (512*1024-target.tell()-1))
            if monitor_failure:
                return 125, "monitor failure"
            return code, None
        with patch.object(g.subprocess, "Popen", return_value=Mock(pid=123)), patch.object(g, "monitor", side_effect=monitored), patch.object(g, "cleanup_owned") as cleanup:
            result = g.run(stream, ["NEVER_EXECUTED"])
            return result, stream, cleanup.call_count

    def test_final_success_control(self):
        code, stream, cleanups = self.guard_run()
        self.assertEqual(code, 0)
        self.assertTrue(stream.final)
        self.assertEqual(cleanups, 0)
        self.assertGreaterEqual(stream.initial_flushes, 2)

    def test_final_write_flush_short_fail(self):
        for failure in ("write", "flush", "short"):
            with self.subTest(failure=failure):
                code, _stream, cleanups = self.guard_run(failure)
                self.assertEqual(code, 125)
                self.assertEqual(cleanups, 1)

    def test_final_budget_fail(self):
        code, _stream, cleanups = self.guard_run("budget")
        self.assertEqual(code, 125)
        self.assertEqual(cleanups, 1)

    def test_final_failure_preserves_nonzero(self):
        for failure in (None, "write", "flush", "short", "budget"):
            code, _, _ = self.guard_run(failure, code=2)
            self.assertEqual(code, 2)

    def test_no_second_cleanup_on_failed_monitor(self):
        code, _, cleanups = self.guard_run("write", monitor_failure=True)
        self.assertEqual(code, 125)
        self.assertEqual(cleanups, 1)

    def test_cleanup_error_cannot_restore_zero(self):
        with patch.object(g.subprocess, "Popen", return_value=Mock(pid=123)), patch.object(g, "monitor", return_value=(0, None)), patch.object(g, "cleanup_owned", side_effect=OSError("cleanup failed")) as cleanup:
            self.assertEqual(g.run(FinalReceipt("write"), ["NEVER_EXECUTED"]), 125)
        self.assertEqual(cleanup.call_count, 1)

    def test_close_error_overrides_apparent_zero(self):
        class Closing(FinalReceipt):
            def __exit__(self, *_args):
                raise OSError("injected final close failure")
        with patch.object(g.subprocess, "Popen", return_value=Mock(pid=123)), patch.object(g, "monitor", return_value=(0, None)), self.assertRaises(OSError):
            with Closing(None) as stream:
                raise SystemExit(g.run(stream, ["NEVER_EXECUTED"]))

    def test_stream_clean_silent_and_progress(self):
        self.assertEqual(self.stream_check(b"")[0]["records"], 0)
        self.assertEqual(self.stream_check(b"Compile\n")[0]["records"], 1)

    def test_split_boundaries(self):
        record = next(iter(self.allowed["core"]))
        for size in (1, 2, 3, 7, 17, d.CHUNK):
            result, _ = self.stream_check(record+b"\n", self.allowed["core"], size)
            self.assertEqual(result["records"], 1)

    def test_warning_unknown_and_appended_text(self):
        for raw in [b"warning: injected\n", b"Compile warning: injected\n", b"Compile\nwarning: injected\n", b"unknown ordinary progress\n", b"Compile \n", b"\n"]:
            with self.subTest(raw=raw), self.assertRaises(RuntimeError):
                self.stream_check(raw, chunk=1)

    def test_controls_and_nonascii(self):
        for bad in (b"\r", b"\x00", b"\t", b"\x1b[0m", b"\x7f", b"\x80", b"\xc3\xa9"):
            with self.subTest(bad=bad), self.assertRaises(RuntimeError):
                self.stream_check(b"Compile"+bad+b"\n", chunk=1)

    def test_overlong_incomplete_and_record_count(self):
        for raw in (b"Compile", b"x"*(d.LINE+1)+b"\n", b"Compile\n"*(d.RECORDS+1)):
            with self.subTest(size=len(raw)), self.assertRaises(RuntimeError):
                self.stream_check(raw)

    def test_rejected_record_still_hashes_full_capture(self):
        raw, store = b"warning: rejected\n" + b"x"*70000, MemoryStore()
        path = store.add("capture", raw)
        with ExitStack() as stack:
            store.mocks(stack, self.allowed)
            with self.assertRaises(RuntimeError):
                d.validate_stream(path, identity(raw), c.FILE, frozenset())
        self.assertTrue(all(x == len(raw) for x in store.positions.values()))
        self.assertEqual(store.files["capture"].getvalue(), raw)

    def test_changed_hash_and_length(self):
        for expected in ({"bytes": 8, "sha256": "0"*64}, {"bytes": 7, "sha256": identity(b"Compile\n")["sha256"]}):
            with self.assertRaises(RuntimeError):
                self.stream_check(b"Compile\n", expected=expected)

    def test_identity_types_and_capture_bound(self):
        for size in (True, False, 0.0, "0", -1, c.FILE, c.FILE+1):
            with self.subTest(size=size), self.assertRaises(RuntimeError):
                d.identity_schema({"bytes": size, "sha256": "0"*64}, c.FILE)
        for value in (None, {}, {"bytes": 0, "sha256": "bad"}, {"bytes": 0, "sha256": "0"*64, "extra": 1}):
            with self.assertRaises(RuntimeError):
                d.identity_schema(value, c.FILE)

    def stage(self, name, stdout, stderr, code=0, observed=None, adjust=None):
        store, receipts = MemoryStore(), []
        def fake(_argv, **kwargs):
            kwargs["stdout"].write(stdout)
            kwargs["stderr"].write(stderr)
            return types.SimpleNamespace(returncode=code)
        def dig(path):
            value = store.digest(path)
            return value if adjust is None else adjust(str(path), value)
        if observed is not None:
            observed.update(store=store, receipts=receipts)
        with ExitStack() as stack:
            store.mocks(stack, self.allowed)
            stack.enter_context(patch.object(w, "LIVE_ROOT", MemoryPath("memory", store)))
            stack.enter_context(patch.object(w, "digest", side_effect=dig))
            stack.enter_context(patch.object(w, "inventory", return_value=({}, 0)))
            stack.enter_context(patch.object(w.subprocess, "run", side_effect=fake))
            w.stage_command(name, ["NEVER_EXECUTED"], c.LIVE_ROOT, 1, 10**20, receipts)
        return receipts, store

    def test_all_build_stages_clean_control(self):
        for stage in ("minimal", "core", "helpers"):
            receipts, _ = self.stage(stage, b"Compile\n", b"")
            self.assertEqual(receipts[0]["exit"], 0)
            self.assertEqual(receipts[0]["diagnostic_validation"], "OBSERVED_EXACT_PROGRESS_OR_SILENCE")

    def test_all_build_stages_both_warning_streams(self):
        for stage in ("minimal", "core", "helpers"):
            for channel in ("stdout", "stderr"):
                observed = {}
                with self.subTest(stage=stage, channel=channel), self.assertRaises(RuntimeError):
                    self.stage(stage, b"warning: zero exit\n" if channel == "stdout" else b"Compile\n",
                               b"warning: zero exit\n" if channel == "stderr" else b"", observed=observed)
                path = "memory/logs/" + stage + "." + channel
                self.assertEqual(observed["store"].files[path].getvalue(), b"warning: zero exit\n")
                self.assertEqual(observed["receipts"][0]["diagnostic_validation"], "FAILED")

    def test_all_build_stages_nonzero_clean_fails(self):
        for stage in ("minimal", "core", "helpers"):
            with self.assertRaises(RuntimeError):
                self.stage(stage, b"Compile\n", b"", code=2)

    def test_build_capture_identities_and_bounds(self):
        for stage in ("minimal", "core", "helpers"):
            for channel in ("stdout", "stderr"):
                for failure in ("missing", "hash", "bound"):
                    def adjust(path, value):
                        if path.endswith("."+channel):
                            if failure == "missing":
                                raise FileNotFoundError("missing capture")
                            value["sha256" if failure == "hash" else "bytes"] = "0"*64 if failure == "hash" else c.FILE
                        return value
                    with self.subTest(stage=stage, channel=channel, failure=failure), self.assertRaises((OSError, RuntimeError)):
                        self.stage(stage, b"Compile\n", b"", adjust=adjust)

    def test_stderr_progress_not_accepted(self):
        with self.assertRaises(RuntimeError):
            self.stage("core", b"Compile\n", b"Compile\n")

    def test_unknown_stage_rejected(self):
        with self.assertRaises(RuntimeError):
            self.stage("unknown", b"", b"")

    def test_target_version_and_generator_policies(self):
        for name, raw in (("target", b"aarch64-linux-gnu\n"), ("version", b"16.1.0\n"), ("generation-a", b""), ("generation-b", b"")):
            self.stage(name, raw, b"")
            with self.assertRaises(RuntimeError):
                self.stage(name, raw, b"warning\n")
        for raw in (b"", b"16.1.0\n16.1.0\n"):
            with self.assertRaises(RuntimeError):
                self.stage("version", raw, b"")

    def test_both_streams_checked_when_one_invalid(self):
        store = MemoryStore()
        paths = {"stdout": store.add("out", b"warning\n"), "stderr": store.add("err", b"warning\n")}
        identities = {name: identity(store.files[str(path)].getvalue()) for name, path in paths.items()}
        with ExitStack() as stack:
            store.mocks(stack, self.allowed)
            with self.assertRaisesRegex(RuntimeError, "stdout:.*stderr:"):
                d.validate_pair(paths, identities, c.FILE, frozenset())
        self.assertEqual(len(store.fds), 2)

    def test_missing_log_and_missing_identity(self):
        store = MemoryStore()
        paths = {"stdout": MemoryPath("absent", store), "stderr": store.add("err", b"")}
        for evidence in ({"stdout": identity(b""), "stderr": identity(b"")}, {"stderr": identity(b"")}):
            with ExitStack() as stack:
                store.mocks(stack, self.allowed)
                with self.assertRaises(RuntimeError):
                    d.validate_pair(paths, evidence, c.FILE, frozenset())

    def recovery(self, stdout=b"", stderr=b"", alter=None):
        store = MemoryStore()
        prefix = MemoryPath("recovery", store)
        store.add("recovery.stdout", stdout)
        store.add("recovery.stderr", stderr)
        item = {"captured_bytes": {"stdout": len(stdout), "stderr": len(stderr)},
                "stdout": identity(stdout), "stderr": identity(stderr)}
        if alter is not None:
            alter(item)
        with ExitStack() as stack:
            store.mocks(stack, self.allowed)
            return d.recovery_diagnostics(prefix, item, r.CAPTURE)

    def test_recovery_silent_control(self):
        self.assertEqual(set(self.recovery()), {"stdout", "stderr"})

    def test_both_recovery_warning_streams(self):
        for _stage in ("create", "extract"):
            for channel in ("stdout", "stderr"):
                with self.subTest(stage=_stage, channel=channel), self.assertRaises(RuntimeError):
                    self.recovery(b"tar: warning\n" if channel == "stdout" else b"",
                                  b"tar: warning\n" if channel == "stderr" else b"")

    def test_recovery_counts_missing_hash_drift(self):
        for channel in ("stdout", "stderr"):
            for change in ("bool", "float", "missing", "hash", "count"):
                def alter(item):
                    if change == "missing":
                        del item[channel]
                    elif change == "hash":
                        item[channel]["sha256"] = "0"*64
                    else:
                        item["captured_bytes"][channel] = {"bool": False, "float": 0.0, "count": 1}[change]
                with self.subTest(channel=channel, change=change), self.assertRaises(RuntimeError):
                    self.recovery(alter=alter)

    def capture_case(self, label, channel=None, failure=None, observed=None):
        store, positions = MemoryStore(), {10: 0, 11: 0}
        payloads = {10: b"", 11: b""}
        if channel is not None:
            payloads[10 if channel == "stdout" else 11] = b"x"*r.CAPTURE if failure == "overflow" else b"tar: warning retained\n"
        process = Mock(pid=123)
        process.stdout, process.stderr = Mock(), Mock()
        process.stdout.fileno.return_value, process.stderr.fileno.return_value = 10, 11
        process.poll.return_value = process.wait.return_value = 2 if failure == "nonzero" else 0
        def read(fd, maximum):
            if fd not in payloads:
                return store.read(fd, maximum)
            data = payloads[fd][positions[fd]:positions[fd]+maximum]
            positions[fd] += len(data)
            return data
        def dig(path, limit):
            if str(path).endswith("."+str(channel)):
                if failure == "missing":
                    raise FileNotFoundError("missing recovery capture")
                if failure == "hash":
                    return {"bytes": len(store.files[str(path)].getvalue()), "sha256": "0"*64}
            return store.digest(path, limit)
        if observed is not None:
            observed.update(store=store)
        with ExitStack() as stack:
            store.mocks(stack, self.allowed)
            stack.enter_context(patch.object(r.os, "read", side_effect=read))
            stack.enter_context(patch.object(r.os, "set_blocking"))
            stack.enter_context(patch.object(r, "digest", side_effect=dig))
            stack.enter_context(patch.object(r.selectors, "DefaultSelector", return_value=MemorySelector()))
            child = stack.enter_context(patch.object(r.subprocess, "Popen", return_value=process))
            limits = r.archive_limits if label == "create" else r.restore_limits
            result = r.capture(["NEVER_EXECUTED"], MemoryPath(label, store), 10**20, limits)
        self.assertIs(child.call_args.kwargs["preexec_fn"], limits)
        return result, store

    def test_native_capture_clean_both_stages(self):
        for label in ("create", "extract"):
            result, _ = self.capture_case(label)
            self.assertEqual(result["captured_bytes"], {"stdout": 0, "stderr": 0})
            self.assertEqual(set(result["diagnostics"]), {"stdout", "stderr"})

    def test_native_capture_negative_matrix_retains_logs(self):
        for label in ("create", "extract"):
            for channel in ("stdout", "stderr"):
                for failure in ("warning", "nonzero", "missing", "hash", "overflow"):
                    observed = {}
                    with self.subTest(label=label, channel=channel, failure=failure), self.assertRaises((OSError, RuntimeError)):
                        self.capture_case(label, channel, failure, observed)
                    raw = observed["store"].files[label+"."+channel].getvalue()
                    if failure == "overflow":
                        self.assertLess(len(raw), r.CAPTURE)
                    else:
                        self.assertEqual(raw, b"tar: warning retained\n")

    def test_policy_exact_regeneration_and_join(self):
        raw = (c.HERE / "input-pins.json").read_bytes()
        expected = ps.policy(json.loads(raw), hashlib.sha256(raw).hexdigest())
        self.assertEqual(expected, c.load_json(c.HERE / "progress-policy.json"))
        for stage, rows in expected["records"].items():
            self.assertEqual(len(rows), len(set(rows)))
            for row in rows:
                self.assertNotIn((row+" warning: injected").encode(), self.allowed[stage])

    def test_every_finite_progress_record(self):
        for stage, allowed in self.allowed.items():
            raw = b"\n".join(sorted(allowed)) + b"\n"
            result, _ = self.stream_check(raw, allowed, chunk=17)
            self.assertEqual(result["records"], len(allowed), stage)

    def test_policy_bad_types_duplicates_controls(self):
        base = {"schema": ps.SCHEMA, "records": {name: ["Compile"] for name in self.allowed}}
        for rows in (True, [True], ["Compile", "Compile"], ["Compile\r"], ["x"*(d.LINE+1)], ["Compile"]*4097):
            altered = copy.deepcopy(base)
            altered["records"]["core"] = rows
            with patch.object(d, "load_json", return_value=altered), self.assertRaises(RuntimeError):
                d.progress_policy()

    def test_command_caps_and_unmodified_controls(self):
        before = json.loads((c.HERE.parent / "o1-xgen-build-package-v1/input-pins.json").read_bytes())
        self.assertEqual(before, c.load_json(c.HERE / "input-pins.json"))
        for name in ("input-pins.json", "tool-runtime-pins.json", "profile.json", "template-roster.json", "xgen_common.py"):
            self.assertEqual((c.HERE / name).read_bytes(), (c.HERE.parent / "o1-xgen-build-package-v1" / name).read_bytes())

    def test_ast_only_necessary_function_changes(self):
        allowed = {"xgen_guard.py": {"run"}, "xgen_worker.py": {"stage_command"},
                   "xgen_recovery.py": {"capture"}}
        for name, changed in allowed.items():
            versions = []
            for path in (c.HERE.parent / "o1-xgen-build-package-v1" / name, c.HERE / name):
                versions.append({node.name: ast.dump(node, include_attributes=False)
                                 for node in ast.parse(path.read_text()).body
                                 if isinstance(node, ast.FunctionDef)})
            self.assertEqual(set(versions[0]), set(versions[1]))
            for function in versions[0]:
                self.assertEqual(versions[0][function] == versions[1][function], function not in changed)
