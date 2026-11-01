"""Source and injected-error checks; no real namespace, IPC or quota exercise."""
from pathlib import Path
import ast
import datetime
import errno
import hashlib
import importlib.util
import json
import os
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "completion-20261026/ram_qualification_v4.py"
BASE = SOURCE.with_name("ram_qualification_v3.py")
EXPECTED = "2cb4bdc25dfec576c5117d303406193f1d8ad4b083946f7f5df874f0ca165716"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def definitions(path):
    tree = ast.parse(path.read_text())
    return {n.name: ast.dump(n, include_attributes=False) for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def unchanged_definitions():
    old, new = definitions(BASE), definitions(SOURCE)
    changed = sorted(n for n in old if old[n] != new.get(n))
    require(changed == ["inside", "parent", "sandbox", "source_state"],
            "unexpected predecessor definition changed")
    return {"case": "unchanged_17_definitions", "changed": changed,
            "unchanged": sorted(n for n in old if old[n] == new.get(n)), "passed": True}


def argv_case(module, base):
    ram = base / "ram"
    ram.mkdir()
    boundary = dict(token="a" * 32, host_identity=[1, 2],
                    parent_ipc="ipc:[3]", parent_mnt="mnt:[4]")
    (base / "host-boundary-before.json").write_text(json.dumps(boundary))
    captured = []
    class Child:
        def wait(self, timeout):
            require(timeout == 180, "tool deadline changed")
            return 0
    def launch(argv, **kwargs):
        require(kwargs["start_new_session"] is True, "owned process group missing")
        captured.append(argv)
        return Child()
    with patch.object(module.subprocess, "Popen", side_effect=launch):
        result = module.sandbox(["fixed-no-execution-command"], ram, [])
    argv = captured[0]
    prefix = ["bwrap", "--die-with-parent", "--unshare-pid", "--unshare-net",
              "--unshare-ipc", "--ro-bind", "/", "/", "--proc", "/proc",
              "--dev", "/dev", "--dir", "/dev/shm", "--bind", str(ram / "ipc"),
              "/dev/shm", "--remount-ro", "/dev"]
    require(argv[:len(prefix)] == prefix, "private bind/remount order changed")
    require(argv.count("--bind") == 1 and "--tmpfs" not in argv, "unexpected writable mount")
    require(result["exit_code"] == 0 and result["stop"] is None, "mock tool status lost")
    return {"case": "emitted_sandbox_topology_and_deadline", "argv": argv,
            "actual_subprocess": False, "passed": True}


def wrong_identity_case(module, base):
    path = base / "owned-regular"
    path.write_bytes(b"preserve")
    info = path.lstat()
    try:
        module.owned_remove(path, [info.st_dev, info.st_ino + 1])
    except RuntimeError:
        pass
    else:
        raise RuntimeError("mismatched inode accepted")
    require(path.read_bytes() == b"preserve", "unowned file changed")
    path.unlink()
    return {"case": "mismatched_fixture_identity_preserved", "passed": True}


def byte_case(module, base, number):
    with patch.object(module, "RAM_LIMIT", 8192):
        with patch.object(module.os, "write", side_effect=[4096, OSError(number, "injected")]):
            result = module.byte_cap(base, "byte-test")
    require(result["passed"] == (number == errno.ENOSPC), "wrong quota errno accepted")
    require(result["cleanup_ok"] and not (base / "quota-bytes-byte-test").exists(),
            "owned byte fixture not cleaned")
    require(result["attempts"] == 2 and result["written_bytes"] == 4096,
            "byte attempts not bounded/accounted")
    return {"case": "injected_byte_error_" + str(number), "result": result,
            "actual_quota_test": False, "passed": True}


def inode_case(module, base, number):
    real_open, calls = os.open, []
    def limited_open(path, flags, mode):
        calls.append(str(path))
        if len(calls) == 3:
            raise OSError(number, "injected")
        return real_open(path, flags, mode)
    with patch.object(module, "ENTRY_LIMIT", 4):
        with patch.object(module.os, "open", side_effect=limited_open):
            result = module.inode_cap(base, "inode-test")
    require(result["passed"] == (number == errno.ENOSPC), "wrong inode errno accepted")
    require(result["cleanup"]["ok"] and not (base / "quota-inodes-inode-test").exists(),
            "owned inode fixture not cleaned")
    require(result["attempts"] == 3 and result["created_files"] == 2,
            "inode attempts not bounded/accounted")
    return {"case": "injected_inode_error_" + str(number), "result": result,
            "actual_quota_test": False, "passed": True}


def main():
    require(hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED, "source changed")
    spec = importlib.util.spec_from_file_location("private_ipc_profile_under_test", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  source_sha256=EXPECTED, tests=[], actual_IPC=False,
                  actual_namespace=False, actual_quota=False, phase_acceptance=False)
    try:
        result["tests"].append(unchanged_definitions())
        with tempfile.TemporaryDirectory(prefix="ipc-source-test-", dir=HERE) as raw:
            base = Path(raw)
            result["tests"].append(argv_case(module, base))
            result["tests"].append(wrong_identity_case(module, base))
            for number in (errno.ENOSPC, errno.EACCES):
                result["tests"].append(byte_case(module, base, number))
                result["tests"].append(inode_case(module, base, number))
        result["status"] = "TESTED_SOURCE_AND_INJECTED_ERRORS_ONLY"
        code = 0
    except Exception as error:
        result.update(status="FAILED", error_type=type(error).__name__, error=str(error))
        code = 1
    with (HERE / "private-ipc-profile-source-tests-v1.json").open("x") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
