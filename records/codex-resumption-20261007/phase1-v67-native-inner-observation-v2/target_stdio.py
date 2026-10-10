"""Owned diagnostic stdio/exec preamble, not a target/test/domain alteration.

GDB launches only this fresh inferior; it execs the byte-identical original
run_controls with exact final argv and explicitly inherited original/relocated
environment. Never attach, signal, invoke a shell, or create a target fixture.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import sys

import observation_support as s


def main():
    assert __debug__ and len(sys.argv) == 2
    launch_path = Path(sys.argv[1])
    attempt = launch_path.parent
    assert attempt.parent == s.F / "attempts" and attempt.is_dir() and not attempt.is_symlink()
    assert launch_path.name == "inferior-launch.json" and launch_path.resolve(strict=True) == launch_path
    launch = s.read(launch_path)
    assert launch["schema"] == "worldline-N67-owned-inferior-exec-v1"
    assert launch["attempt"] == str(attempt) and launch["target_kind"] in ("native-diagnostic", "observer-control-only")
    assert launch["unit"] == s.SCOPE_PREFIX + attempt.name + ".scope"
    assert os.getuid() == os.geteuid() != 0
    actual_cgroup = Path("/proc/self/cgroup").read_text()
    relative = next(row[3:] for row in actual_cgroup.splitlines() if row.startswith("0::"))
    assert Path(relative).name == launch["unit"]
    manifest = s.read(s.F / "manifest.json")
    if launch["target_kind"] == "native-diagnostic":
        assert launch["argv"] == manifest["exact_target_argv"]
        assert launch["environment"] == manifest["exact_target_environment"]
    else:
        assert launch["argv"] == s.control_argv()
        assert launch["native_observation"] is True
    assert launch["cwd"] == str(s.F / "source")
    descriptors = {}
    try:
        for name in ("stdout", "stderr", "native_boundaries"):
            row = launch["streams"][name]
            path = Path(row["path"])
            assert path.parent == attempt and path.resolve(strict=True) == path
            flags = os.O_WRONLY | os.O_NOFOLLOW
            if name == "native_boundaries":
                flags |= os.O_APPEND | os.O_NONBLOCK
            fd = os.open(path, flags)
            observed = os.fstat(fd)
            assert stat.S_ISREG(observed.st_mode) and stat.S_IMODE(observed.st_mode) == 0o600
            assert (observed.st_dev, observed.st_ino) == (row["device"], row["inode"])
            descriptors[name] = fd
        os.dup2(descriptors["stdout"], 1)
        os.dup2(descriptors["stderr"], 2)
        env = dict(launch["environment"])
        env.pop("WORLDLINE_NATIVE_TRANSACTION_OBSERVATION_ACTIVE_FD", None)
        fd = descriptors["native_boundaries"]
        os.set_inheritable(fd, True)
        if launch["native_observation"]:
            env["WORLDLINE_NATIVE_TRANSACTION_OBSERVATION_PENDING_FD"] = str(fd)
        else:
            env.pop("WORLDLINE_NATIVE_TRANSACTION_OBSERVATION_PENDING_FD", None)
        for name in ("stdout", "stderr"):
            if descriptors[name] > 2:
                os.close(descriptors[name])
        s.save_new(attempt / "inferior-exec-admission.json", {
            "at": s.utc_now(), "pid": os.getpid(), "process_birth": s.birth(os.getpid()),
            "ppid": os.getppid(), "argv": launch["argv"], "cwd": launch["cwd"],
            "environment": env, "native_fd": fd if launch["native_observation"] else None,
            "target_kind": launch["target_kind"], "target_execution": False,
            "meaning": "Observed pre-exec admission only; final target argv/environment require later actual /proc evidence",
            "phase_acceptance": False})
        os.chdir(launch["cwd"])
        os.execve(launch["argv"][0], launch["argv"], env)
    finally:
        for fd in descriptors.values():
            if fd > 2:
                try:
                    os.close(fd)
                except OSError:
                    pass


if __name__ == "__main__":
    main()
