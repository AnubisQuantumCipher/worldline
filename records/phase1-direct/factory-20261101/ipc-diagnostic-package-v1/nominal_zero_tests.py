"""Pure zero-exit counterexamples: observation never grants qualification."""
from pathlib import Path
import copy
import hashlib
import json
import source_tests as tests

HERE = Path(__file__).resolve().parent


def main():
    tests.require(hashlib.sha256(tests.COLLECTOR.read_bytes()).hexdigest() ==
                  tests.COLLECTOR_PIN, "collector changed")
    collector = tests.load(tests.COLLECTOR, "zero_exit_collector_definitions")
    facts, _, _ = tests.synthetic_reports()
    facts.update(status="PASSED", stage="completed")
    facts.pop("error", None)
    cases = []
    for mode in ("unique", "unknown999"):
        changed = copy.deepcopy(facts)
        if mode == "unknown999":
            changed["mount_evidence"]["opened_fd_mount_id"] = "999"
            changed["shm_fdinfo"] = changed["shm_fdinfo"].replace("mnt_id:\t3", "mnt_id:\t999")
        fixture = tests.fixture(changed, receipt=changed)
        fixture["tool"]["exit_code"] = 0
        result = tests.evaluate(collector, fixture)
        tests.require(result["terminal_tool_failure"] is False, "invented nonzero tool outcome")
        tests.require(result["mechanism_qualified"] is False and result["proof_credit"] is False
                      and result["phase_acceptance"] is False, "zero exit granted qualification")
        tests.require((result["interpretation"] == "UNPROVEN") == (mode == "unknown999"),
                      "zero-exit join interpretation")
        cases.append(dict(name=mode, result=result))
    value = dict(status="TESTED_SYNTHETIC_ZERO_EXIT_NOT_CONTROL_EXECUTION", cases=cases,
                 source_sha256=tests.COLLECTOR_PIN, phase_acceptance=False,
                 boundary="Terminal0/PASSED tuples are synthetic inputs to diagnostic consumer only. "
                 "No original positive checker, parent, guard, sandbox or actual IPC ran. "
                 "A separately observed parent0 would still require independent diagnostic readback "
                 "and the unchanged six-case mechanism qualification conjunction.")
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("ascii")
    tests.require(len(data) <= 8192, "zero-exit receipt bound")
    with (HERE / "nominal-zero-tests.json").open("xb") as stream:
        tests.require(stream.write(data) == len(data), "short zero-exit receipt write")
    print(json.dumps(dict(status=value["status"], cases=len(cases)), sort_keys=True))


if __name__ == "__main__":
    main()
