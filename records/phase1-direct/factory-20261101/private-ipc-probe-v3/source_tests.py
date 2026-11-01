"""Deterministic source/pure-diagnostic tests; no real IPC/namespace/OS reads."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "probe.py"
SOURCE_SHA256 = "8d7816d6a37ed353c6682dd27b97c4b7cbbc95f7e20282cb84a4c10177b16260"
BEFORE = HERE.parent / "private-ipc-probe-v2/probe.py"
CFG = {"PROBE_RAM_IPC": "/owned/ram/ipc", "TMPDIR": "/owned/tmp"}
UID_MAP = "         0       1000          1\n"
FDINFO = "pos:\t0\nflags:\t02300000\nmnt_id:\t3\nino:\t1\n"
BASE = ["1 0 0:1 / / ro - rootfs rootfs ro",
        "2 1 0:2 / /dev ro - tmpfs tmpfs rw",
        "3 2 0:3 /ipc /dev/shm rw - tmpfs tmpfs rw",
        "4 1 0:3 / /owned ro - tmpfs tmpfs rw",
        "5 1 0:3 /tmp /owned/tmp rw - tmpfs tmpfs rw"]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def load_source():
    require(hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256,
            "tested source pin changed")
    spec = importlib.util.spec_from_file_location("private_ipc_probe_v3_source_tests", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Definitions only; __main__ is not invoked.
    return module


def formation():
    old, new = ast.parse(BEFORE.read_bytes()), ast.parse(SOURCE.read_bytes())
    before = {n.name: n for n in old.body if isinstance(n, ast.FunctionDef)}
    after = {n.name: n for n in new.body if isinstance(n, ast.FunctionDef)}
    changed = [k for k in before if ast.dump(before[k]) != ast.dump(after[k])]
    require(changed == ["shm_mount_evidence"], "unexpected source delta")
    require(set(before) == set(after), "unexpected function roster")
    require(all(n.end_lineno - n.lineno + 1 <= 60 for n in after.values()),
            "probe function exceeds60lines")
    predicates = [n for n in ast.walk(before["record_os_evidence"])
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                  and n.func.id == "require"]
    actual = [ast.dump(n) for n in ast.walk(after["record_os_evidence"])
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
              and n.func.id == "require"]
    require(all(ast.dump(n) in actual for n in predicates), "old predicate changed")
    return dict(changed_original_functions=changed,
                unchanged_original_functions=[k for k in before if k not in changed],
                every_original_mount_predicate_retained=True)


def observe(probe, rows, fdinfo=FDINFO):
    fixtures = {"/proc/self/mountinfo": "\n".join(rows) + "\n",
                "/proc/self/uid_map": UID_MAP, "/proc/self/gid_map": UID_MAP,
                "/proc/self/fdinfo/17": fdinfo}
    def fake_read(path, limit):
        value = fixtures[path]
        require(len(value.encode("ascii")) <= limit, "synthetic OS evidence exceeds cap")
        return value
    report = dict(schema=probe.SCHEMA, status="FAILED", stage="private identity",
                  mode="normal", phase_acceptance=False)
    error = None
    with patch.object(probe, "read_limited", side_effect=fake_read):
        with patch.object(probe.os, "open", side_effect=RuntimeError("OS open forbidden")):
            try:
                probe.record_os_evidence(CFG, report, 17)
            except RuntimeError as caught:
                error = str(caught)
                report["error"] = error
    return report, error


def check_selected(probe, rows, expected_error, fdinfo=FDINFO):
    report, error = observe(probe, rows, fdinfo)
    require(error == expected_error, "wrong original/refusal predicate: " + str(error))
    require(set(report["mounts"]) == {"dev", "shm", "alias", "tmp"}, "selected records absent")
    require(report["uid_map"] == UID_MAP and report["gid_map"] == UID_MAP, "maps lost")
    require(report["shm_fdinfo"] == fdinfo, "opened FD evidence lost")
    evidence = report["mount_evidence"]
    require(len(json.dumps(evidence, sort_keys=True).encode("ascii")) <= probe.MOUNT_EVIDENCE_LIMIT,
            "mount evidence byte cap failed")
    rendered = probe.render_report(report)
    require(len(rendered.encode("ascii")) <= probe.MAX_RESULT, "stdout cap failed")
    return report


def predicate_cases(probe):
    normal = check_selected(probe, BASE, None)
    readonly = list(BASE)
    readonly[2] = readonly[2].replace("/dev/shm rw", "/dev/shm ro")
    ro = check_selected(probe, readonly, "private shm mount mismatch")
    wrongfs = list(BASE)
    wrongfs[2] = wrongfs[2].replace("- tmpfs", "- ext4")
    fs = check_selected(probe, wrongfs, "private shm mount mismatch")
    wrongpoint = list(BASE)
    wrongpoint[2] = wrongpoint[2].replace("/dev/shm ", "/dev/shm-other ")
    point = check_selected(probe, wrongpoint, "private shm mount mismatch")
    require(ro["mounts"]["shm"]["options"] == "ro", "ro distinction lost")
    require(fs["mounts"]["shm"]["filesystem"] == "ext4", "filesystem distinction lost")
    require(point["mounts"]["shm"]["mountpoint"] == "/dev", "wrong mountpoint distinction lost")
    return dict(normal=normal, readonly_shm=ro, wrong_filesystem=fs, wrong_mountpoint=point)


def stacked_cases(probe):
    rows = list(BASE)
    rows[2] = rows[2].replace("/dev/shm rw", "/dev/shm ro")
    rows.insert(3, "6 2 0:3 /ipc /dev/shm rw - tmpfs tmpfs rw")
    fd = FDINFO.replace("mnt_id:\t3", "mnt_id:\t6")
    report = check_selected(probe, rows, "private shm mount mismatch", fd)
    evidence = report["mount_evidence"]
    require(evidence["selected_mount_id"] == "3" and evidence["opened_fd_mount_id"] == "6",
            "selected-vs-opened distinction lost")
    require(evidence["ambiguous"] and evidence["equal_longest_count"] == 2, "tie evidence absent")
    require(all(any(x["raw"] == row for x in evidence["rows"]) for row in rows[2:4]),
            "stacked candidate raw row lost")
    rows[2], rows[3] = rows[3], rows[2]
    first_rw = check_selected(probe, rows, None, fd)
    require(first_rw["mounts"]["shm"]["mount_id"] == "6", "tie policy changed")
    return dict(first_readonly=report, first_writable=first_rw)


def budget_cases(probe):
    rows = list(BASE)
    rows.extend(str(n) + " 2 0:3 /" + "x" * 128 + " /dev/shm rw - tmpfs tmpfs rw"
                for n in range(6, 46))
    report = check_selected(probe, rows, "shm candidate evidence incomplete: bound refusal")
    evidence = report["mount_evidence"]
    require(not evidence["complete"] and evidence["omitted_rows"] > 0, "overflow not refused")
    require(evidence["candidate_count"] == evidence["retained_rows"] + evidence["omitted_rows"],
            "candidate accounting wrong")
    source = json.dumps(report, sort_keys=True).encode("ascii")
    require(evidence["candidate_lines_joined_LF_sha256"] == hashlib.sha256(
        "\n".join(row for row in rows if row.split()[4] in ("/", "/dev", "/dev/shm"))
        .encode("ascii")).hexdigest(), "candidate hash wrong")
    huge = dict(report, padding="x" * 16384)
    original = json.dumps(huge, sort_keys=True).encode("ascii")
    fallback = json.loads(probe.render_report(huge))
    require(huge["status"] == "FAILED" and fallback["status"] == "FAILED", "overflow pass")
    require(fallback["mount_evidence"] == evidence and fallback["mandatory_evidence_discarded"],
            "failure fallback lost evidence/unknown marker")
    require(fallback["full_report_sha256"] == hashlib.sha256(original).hexdigest(), "overflow hash")
    require(len(json.dumps(fallback, sort_keys=True).encode("ascii")) <= probe.MAX_RESULT,
            "bounded fallback exceeds original MAX_RESULT")
    return dict(candidate_refusal=report, overflow_fallback=fallback,
                candidate_evidence_bytes=len(json.dumps(evidence, sort_keys=True).encode("ascii")),
                fallback_bytes=len(json.dumps(fallback, sort_keys=True).encode("ascii")))


def main():
    probe = load_source()
    result = dict(schema="worldline.private-ipc-probe-v3.source-tests.v1",
                  status="TESTED_SYNTHETIC_RECORDS_ONLY_NO_ACTUAL_OS_IPC",
                  source_sha256=SOURCE_SHA256, formation=formation(),
                  predicate_cases=predicate_cases(probe), stacked_cases=stacked_cases(probe),
                  budgets=budget_cases(probe), phase_acceptance=False,
                  boundary="All mount/maps/fdinfo values are deterministic synthetic fixtures. "
                           "Only record_os_evidence with mocked read_limited, unchanged pure "
                           "mount_record, shm_mount_evidence and render_report executed. "
                           "No open_context/main/semaphore/cleanup/socket/namespace/mount/guard job.")
    data = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("ascii")
    require(len(data) < 65536, "synthetic receipt bound")
    with (HERE / "source-tests.json").open("xb") as stream:
        require(stream.write(data) == len(data), "short synthetic receipt write")
    print(json.dumps({"status": result["status"], "receipt_bytes": len(data),
                      "mount_evidence_bytes": result["budgets"]["candidate_evidence_bytes"],
                      "fallback_bytes": result["budgets"]["fallback_bytes"]}, sort_keys=True))


if __name__ == "__main__":
    main()
