"""Final exact-source rerun after completing the row-boundary repair."""
from pathlib import Path
import copy
import hashlib
import json
import source_tests as tests
import revision_tests as revision

HERE = Path(__file__).resolve().parent


def delimiter_cases(collector, normal):
    results = []
    for delimiter in ("\n", "\r", "\v", "\f", "\t", " "):
        facts = copy.deepcopy(normal)
        rows = facts["mount_evidence"]["rows"]
        rows[0]["raw"] += delimiter + rows[2]["raw"]
        digest = hashlib.sha256("\n".join(x["raw"] for x in rows).encode("ascii")).hexdigest()
        facts["mount_evidence"]["candidate_lines_joined_LF_sha256"] = digest
        results.append(revision.recorded_failure(collector, tests.fixture(facts),
                                                 "appended-record-delimiter-" + repr(delimiter)))
    return results


def main():
    tests.require(hashlib.sha256(tests.COLLECTOR.read_bytes()).hexdigest() == tests.COLLECTOR_PIN,
                  "final collector pin changed")
    collector = tests.load(tests.COLLECTOR, "final_v6_definitions")
    normal, duplicate, incomplete = tests.synthetic_reports()
    prior = []
    tests.core_cases(collector, normal, duplicate, incomplete, prior)
    tests.tamper_cases(collector, normal, prior)
    tests.archive_cases(collector, normal, prior)
    encoding = tests.encoding_cases(collector, normal, prior)
    zero = []
    for mode in ("unique", "unknown999"):
        facts = copy.deepcopy(normal)
        facts.update(status="PASSED", stage="completed")
        facts.pop("error", None)
        if mode == "unknown999":
            facts["mount_evidence"]["opened_fd_mount_id"] = "999"
            facts["shm_fdinfo"] = facts["shm_fdinfo"].replace("mnt_id:\t3", "mnt_id:\t999")
        fixture = tests.fixture(facts, receipt=facts)
        fixture["tool"]["exit_code"] = 0
        value = tests.evaluate(collector, fixture)
        tests.require(not value["mechanism_qualified"] and not value["terminal_tool_failure"] and
                      (value["interpretation"] == "UNPROVEN") == (mode == "unknown999"),
                      "zero-exit qualification/join regression")
        zero.append(value)
    result = dict(schema="worldline.ipc-composition-r2.final-tests.v1",
                  status="TESTED_FINAL_SOURCE_AUTHOR_ONLY_NOT_INDEPENDENT_REVIEW",
                  source_sha256=tests.COLLECTOR_PIN, guard_sha256=tests.GUARD_PIN,
                  structure=tests.formation(), original42=prior, original_zero2=zero,
                  encoding=encoding, exact_r1=revision.exact_counterexamples(collector, normal),
                  scanner=revision.scanner_cases(collector, normal),
                  fields_containment=revision.field_and_containment_cases(collector, normal),
                  delimiter_closure=delimiter_cases(collector, normal),
                  historical_archive=revision.historical_compatibility(collector),
                  runtime_entrypoints_executed=False, phase_acceptance=False)
    data = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("ascii")
    tests.require(len(data) <= 131072, "final receipt cap")
    with (HERE / "final-tests.json").open("xb") as stream:
        tests.require(stream.write(data) == len(data), "short final receipt write")
    print(json.dumps(dict(status=result["status"], prior_cases=len(prior) + len(zero),
                          exact_regressions=len(result["exact_r1"]), scanner_cases=len(result["scanner"]),
                          delimiter_cases=len(result["delimiter_closure"]), historical_archive="485B_COMPATIBLE"),
                     sort_keys=True))


if __name__ == "__main__":
    main()
