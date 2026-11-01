"""Bounded fake-libc failure controls; this file never creates real IPC."""
from pathlib import Path
import ctypes
import datetime
import errno
import hashlib
import importlib.util
import json
import os
import stat
import sys
import types
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "private-ipc-probe-v1/probe.py"


class FakeLib:
    def __init__(self, close=0, unlink=0):
        self.calls = []
        self.close_result, self.unlink_result = close, unlink

    def sem_open(self, *arguments):
        self.calls.append("open")
        ctypes.set_errno(errno.EEXIST)
        return None

    def sem_close(self, handle):
        self.calls.append("close")
        ctypes.set_errno(errno.EINVAL if self.close_result else 0)
        return self.close_result

    def sem_unlink(self, name):
        self.calls.append("unlink")
        ctypes.set_errno(errno.EACCES if self.unlink_result else 0)
        return self.unlink_result


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def backing(inode=2):
    return types.SimpleNamespace(st_dev=1, st_ino=inode,
                                 st_mode=stat.S_IFREG | 0o600,
                                 st_nlink=1, st_uid=os.geteuid())


def owned_state(lib):
    return dict(lib=lib, name=b"/synthetic-only", backing="synthetic-only",
                created=True, handle=123, identity=[1, 2])


def cleanup_case(probe, name, lib, stats, expected_calls, failed):
    report = {}
    with patch.object(probe.os, "stat", side_effect=stats):
        probe.close_semaphore({"ipc": 42}, owned_state(lib), report)
    result = report["semaphore_cleanup"]
    check(lib.calls == expected_calls, name + ": wrong operation sequence")
    check(bool(result["errors"]) == failed, name + ": wrong failure result")
    if not failed:
        check(result.get("backing_absent") is True, "absence was not confirmed")
    return {"case": name, "calls": lib.calls, "result": result, "passed": True}


def first_open_collision(probe):
    lib, state, report = FakeLib(), {}, {}
    with patch.object(probe, "load_libc", return_value=lib):
        try:
            probe.semaphore({"token": "a" * 32}, {"ipc": 42}, state, report)
        except RuntimeError as error:
            check("sem_open failed" in str(error), "wrong collision error")
        else:
            raise RuntimeError("first-open EEXIST accepted")
    probe.close_semaphore({"ipc": 42}, state, report)
    check(lib.calls == ["open"], "unowned semaphore was closed or unlinked")
    check(not state.get("created", False), "collision incorrectly grants ownership")
    return {"case": "first_open_EEXIST_never_grants_cleanup", "passed": True}


def trywait_cases(probe):
    rows = []
    for result, number, empty, accepted in ((-1, errno.EAGAIN, True, True),
                                           (0, 0, False, True),
                                           (-1, errno.EINTR, True, False),
                                           (0, 0, True, False)):
        calls = []
        def simulated(handle):
            calls.append(handle)
            ctypes.set_errno(number)
            return result
        lib = types.SimpleNamespace(sem_trywait=simulated)
        actual = True
        try:
            probe.trywait(lib, 123, empty)
        except RuntimeError:
            actual = False
        check(actual == accepted and calls == [123], "trywait contract or call bound")
        rows.append(dict(result=result, errno=number, empty=empty, accepted=actual))
    return {"case": "trywait_exact_result_no_retry", "outcomes": rows, "passed": True}


def run(probe):
    rows, report = [], {}
    probe.close_semaphore({}, {}, report)
    check(report["semaphore_cleanup"]["created"] is False, "unowned cleanup")
    rows.append({"case": "no_ownership_no_cleanup", "passed": True})
    rows.append(first_open_collision(probe))
    rows.append(cleanup_case(probe, "normal_owned_cleanup", FakeLib(),
                             [backing(), FileNotFoundError()], ["close", "unlink"], False))
    rows.append(cleanup_case(probe, "close_failure_still_checks_unlink", FakeLib(close=-1),
                             [backing(), FileNotFoundError()], ["close", "unlink"], True))
    rows.append(cleanup_case(probe, "identity_change_never_unlinks", FakeLib(),
                             [backing(3)], ["close"], True))
    rows.append(cleanup_case(probe, "unlink_failure_is_not_success", FakeLib(unlink=-1),
                             [backing()], ["close", "unlink"], True))
    rows.append(trywait_cases(probe))
    return rows


def main():
    spec = importlib.util.spec_from_file_location("private_ipc_probe_under_test", SOURCE)
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  tests=[], actual_IPC=False, mechanism_qualification=False,
                  phase_acceptance=False)
    try:
        result["tests"] = run(probe)
        result["status"] = "TESTED_FAKE_LIBC_CONTRACTS_ONLY"
        code = 0
    except Exception as error:
        result.update(status="FAILED", error_type=type(error).__name__, error=str(error))
        code = 1
    with (HERE / "private-ipc-root-tests-v1.json").open("x") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
