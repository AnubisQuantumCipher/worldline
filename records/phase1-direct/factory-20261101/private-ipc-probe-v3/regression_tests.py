"""Pure counter-width regression tests; every OS observation is synthetic."""
from pathlib import Path
import hashlib
import importlib.util
import json
from unittest.mock import patch
import source_tests as tests

HERE = Path(__file__).resolve().parent
PREIMAGE = "b6da769aa9d5707951b58a7737535657032c1df5077262a6017cd29db0497e8b"


def predecessor():
    source = HERE.parent / "private-ipc-probe-v2/probe.py"
    tests.require(hashlib.sha256(source.read_bytes()).hexdigest() == PREIMAGE,
                  "predecessor source changed")
    spec = importlib.util.spec_from_file_location("pure_v2_counter_regression", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Definitions only; never __main__.
    return module


def old_failure(rows):
    probe, saved, dumps = predecessor(), {}, json.dumps
    def capture(value, *args, **kwargs):
        rendered = dumps(value, *args, **kwargs)
        if isinstance(value, dict) and "candidate_count" in value:
            saved.update(envelope=json.loads(rendered), bytes=len(rendered.encode("ascii")))
        return rendered
    with patch.object(probe.json, "dumps", side_effect=capture):
        report, error = tests.observe(probe, rows)
    tests.require(error == "mount evidence metadata bound", "predecessor defect not reproduced")
    tests.require("mount_evidence" not in report and "shm_fdinfo" not in report,
                  "predecessor lost-evidence behavior changed")
    old = saved["envelope"]
    tests.require((old["candidate_count"], old["retained_rows"], old["omitted_rows"],
                   saved["bytes"]) == (25, 15, 10, 2817), "wrong pinned regression")
    return dict(error=error, evidence=saved, fdinfo_retained=False,
                actual_OS_observation=False)


def check_prefix(probe, rows):
    chosen = probe.mount_record("/dev/shm", rows)
    evidence = probe.shm_mount_evidence(rows, chosen)
    candidates = [(i, row) for i, row in enumerate(rows)
                  if "/dev/shm" == row.split()[4] or
                  "/dev/shm".startswith(row.split()[4].rstrip("/") + "/")]
    count, expected, previous = len(candidates), 0, 0
    for size in range(count + 1):
        prefix = [dict(line_index=i, raw=row) for i, row in candidates[:size]]
        proposed = dict(evidence, rows=prefix, retained_rows=size, omitted_rows=count - size,
                        complete=size == count and evidence["selected_id_exact"])
        encoded = len(json.dumps(proposed, sort_keys=True).encode("ascii"))
        tests.require(encoded >= previous, "fixture prefix sizes unexpectedly decrease")
        previous = encoded
        if encoded <= probe.MOUNT_EVIDENCE_LIMIT - 256:
            expected = size
    tests.require(evidence["retained_rows"] == expected, "incorrect retained prefix")
    tests.require(evidence["rows"] == [dict(line_index=i, raw=r)
                                      for i, r in candidates[:expected]], "not exact prefix")
    tests.require(evidence["omitted_rows"] == count - expected, "omitted count wrong")
    joined = "\n".join(row for _, row in candidates).encode("ascii")
    tests.require(evidence["candidate_lines_joined_LF_sha256"] ==
                  hashlib.sha256(joined).hexdigest(), "candidate digest lost")
    error = None if evidence["complete"] else "shm candidate evidence incomplete: bound refusal"
    report = tests.check_selected(probe, rows, error)
    tests.require(report["mount_evidence"]["opened_fd_mount_id"] == "3", "FD ID lost")
    return dict(candidate_count=count, retained_rows=expected, omitted_rows=count - expected,
                complete=evidence["complete"], serialized_bytes=len(json.dumps(
                    evidence, sort_keys=True).encode("ascii")), fdinfo_retained=True,
                fixture_sha256=hashlib.sha256("\n".join(rows).encode("ascii")).hexdigest())


def transitions(probe):
    cases = []
    for count in (*range(9, 151), 509, 510):
        for padding in ((0, 109) if count <= 150 else (0,)):
            rows = tests.BASE + [str(i) + " 2 0:3 /" + "x" * padding +
                                 " /dev/shm rw - tmpfs tmpfs rw"
                                 for i in range(6, 6 + count - 3)]
            cases.append(check_prefix(probe, rows))
    for field, values in (("candidate_count", (9, 10, 99, 100)),
                          ("retained_rows", (9, 10)),
                          ("omitted_rows", (9, 10, 99, 100))):
        tests.require(set(values) <= {case[field] for case in cases},
                      "counter-width transition not exercised: " + field)
    return cases


def unjoined_ids(probe):
    unknown = tests.check_selected(probe, tests.BASE, None,
                                   tests.FDINFO.replace("mnt_id:\t3", "mnt_id:\t999"))
    duplicate = list(tests.BASE) + ["3 2 0:3 /ipc /dev/shm rw - tmpfs tmpfs rw"]
    repeated = tests.check_selected(probe, duplicate, None)
    tests.require(unknown["mount_evidence"]["complete"] and
                  repeated["mount_evidence"]["complete"], "retention marker changed meaning")
    return dict(unknown_fd_id_retention_complete=True, duplicate_id_retention_complete=True,
                descriptor_row_join="UNPROVEN_NOT_ENFORCED",
                qualification=False, interpretation="complete means bounded retention only")


def main():
    probe = tests.load_source()
    rows = tests.BASE + [str(i) + " 2 0:3 /" + "x" * 109 +
                         " /dev/shm rw - tmpfs tmpfs rw" for i in range(6, 28)]
    result = dict(schema="worldline.private-ipc-probe-v3.counter-tests.v1",
                  status="TESTED_PURE_SYNTHETIC_NOT_INDEPENDENT_REVIEW",
                  source_sha256=tests.SOURCE_SHA256, predecessor_sha256=PREIMAGE,
                  exact_regression=dict(rows=len(rows), input_bytes=len(
                      ("\n".join(rows) + "\n").encode("ascii")),
                      predecessor=old_failure(rows), revised=check_prefix(probe, rows)),
                  counter_width_cases=transitions(probe), unjoined_ids=unjoined_ids(probe),
                  actual_probe_executed=False, phase_acceptance=False)
    data = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("ascii")
    tests.require(len(data) <= 131072, "counter receipt bound")
    with (HERE / "regression-tests.json").open("xb") as stream:
        tests.require(stream.write(data) == len(data), "short counter receipt write")
    print(json.dumps(dict(status=result["status"], cases=len(result["counter_width_cases"]),
                          regression=result["exact_regression"]["revised"]), sort_keys=True))


if __name__ == "__main__":
    main()
