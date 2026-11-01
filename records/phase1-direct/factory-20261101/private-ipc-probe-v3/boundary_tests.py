"""Bounded synthetic mount-record edges; no actual OS/IPC evidence read."""
from pathlib import Path
import hashlib
import json
import source_tests as tests

HERE = Path(__file__).resolve().parent


def check_refusal(probe, name, rows, expected):
    report, error = tests.observe(probe, rows)
    tests.require(error == expected, name + ": wrong refusal " + str(error))
    rendered = probe.render_report(report)
    tests.require(len(rendered.encode("ascii")) <= probe.MAX_RESULT, "result cap")
    result = json.loads(rendered)
    tests.require(result["status"] == "FAILED", "edge qualified")
    evidence = report.get("mount_evidence")
    if evidence is not None:
        tests.require(len(json.dumps(evidence, sort_keys=True).encode("ascii"))
                      <= probe.MOUNT_EVIDENCE_LIMIT, "evidence cap")
    return dict(name=name, error=error, result_bytes=len(rendered.encode("ascii")),
                candidate_count=evidence.get("candidate_count") if evidence else None,
                complete=evidence.get("complete") if evidence else None,
                selected_id_exact=evidence.get("selected_id_exact") if evidence else None,
                omitted_rows=evidence.get("omitted_rows") if evidence else None,
                fixture_sha256=hashlib.sha256("\n".join(rows).encode("ascii")).hexdigest())


def main():
    probe = tests.load_source()
    cases = []
    rows = list(tests.BASE)
    rows.extend(str(n) + " 2 0:3 /ipc /dev/shm rw - tmpfs tmpfs rw" for n in range(6, 513))
    tests.require(len(rows) == 512, "fixture roster")
    cases.append(check_refusal(probe, "512-lines-with-many-stacked-shm-rows", rows,
                               "shm candidate evidence incomplete: bound refusal"))
    prefix, suffix = "3 2 0:3 /", " /dev/shm rw - tmpfs tmpfs rw"
    row = prefix + "\\" * (2048 - len(prefix) - len(suffix)) + suffix
    tests.require(len(row) == 2048, "max-row fixture")
    rows = list(tests.BASE)
    rows[2] = row
    cases.append(check_refusal(probe, "2048-byte-row-with-JSON-escaping", rows,
                               "shm candidate evidence incomplete: bound refusal"))
    rows = list(tests.BASE)
    rows[2] = "9" * 65 + rows[2][1:]
    cases.append(check_refusal(probe, "oversized-selected-ID-explicitly-unknown", rows,
                               "shm candidate evidence incomplete: bound refusal"))
    rows = list(tests.BASE) + ["6 2 0:3 /ipc /dev/shm rw - tmpfs tmpfs rw"] * 508
    cases.append(check_refusal(probe, "513-lines-original-rejection", rows,
                               "mountinfo entry bound"))
    rows = list(tests.BASE)
    rows[2] = prefix + "x" * (2049 - len(prefix) - len(suffix)) + suffix
    cases.append(check_refusal(probe, "2049-byte-row-original-rejection", rows,
                               "mountinfo line bound"))
    result = dict(schema="worldline.private-ipc-probe-v3.boundary-tests.v1",
                  status="TESTED_SYNTHETIC_BOUNDARIES_ONLY_NOT_FORMAL_PROOF",
                  source_sha256=tests.SOURCE_SHA256, cases=cases,
                  enforcement="shm_mount_evidence checks final-counter serialized bytes before retaining each "
                              "candidate and at return; record_os_evidence checks after FD ID; "
                              "render_report checks original8192-byte ceiling. Incomplete mandatory "
                              "candidate evidence refuses before original mount predicates/IPC.",
                  actual_mount_or_IPC_execution=False, phase_acceptance=False)
    data = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("ascii")
    tests.require(len(data) <= 8192, "boundary receipt cap")
    with (HERE / "boundary-tests.json").open("xb") as stream:
        tests.require(stream.write(data) == len(data), "short boundary receipt write")
    print(json.dumps({"status": result["status"], "cases": len(cases),
                      "largest_rendered_result_bytes": max(c["result_bytes"] for c in cases)},
                     sort_keys=True))


if __name__ == "__main__":
    main()
