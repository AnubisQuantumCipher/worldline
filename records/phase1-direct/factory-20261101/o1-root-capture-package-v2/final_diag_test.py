#!/usr/bin/python3
"""One distinct native diagnostic-file cap control; no product processes."""
import json
import time
import run_tests as t


def main():
    names = t.SOURCES + ("final_tests.py", "final_diag_test.py", "tee-diag-fixture.sh")
    before = {name: t.digest(t.BASE / name) for name in names}
    t.write_json(t.BASE / "final-04-source-at-execution.json", before)
    compile_run = t.execute(["/usr/bin/gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                             "-Wpedantic", "-Wconversion", "-Wshadow", "-Wformat=2", "-O2",
                             "-fPIC", "-shared", "-o", str(t.BASE / "fault-diag.so"),
                             str(t.BASE / "fault.c"), "-ldl"])
    t.write_json(t.BASE / "final-04-compile-command.json", compile_run)
    assert compile_run["returncode"] == 0
    old_variant = t.variant

    def diag_variant(folder, body):
        path, replacements = old_variant(folder, body)
        old = str(t.BASE / "tee-fixture.sh")
        new = str(t.BASE / "tee-diag-fixture.sh")
        path.write_text(path.read_text().replace(old, new))
        replacements.append({"old": old, "new": new})
        return path, replacements

    t.variant = diag_variant
    t.one_case(200, "native-diag-cap", "    printf 'lost' || :", False,
               ("stdout", "lost_diag"))
    row = t.RESULTS[0]
    assert row["passed"]
    assert row["files"]["stdout"]["bytes"] == 0
    assert row["files"]["stdout-consumer.stderr"]["bytes"] == 0
    status = row["files"]["status"]["text"]
    assert "guard=WAIT_STATUS:0" in status
    assert "stdout_consumer=WAIT_STATUS:153" in status
    assert "stderr_consumer=WAIT_STATUS:0" in status
    assert before == {name: t.digest(t.BASE / name) for name in names}
    prior = json.loads((t.BASE / "test-results.json").read_text())
    third = json.loads((t.BASE / "final-test-results.json").read_text())
    assert before["launch.sh"] == prior["source_pins"]["launch.sh"] == third["source_pins"]["launch.sh"]
    t.write_json(t.BASE / "final-04-test-results.json", {"results": t.RESULTS,
                 "seconds": time.monotonic() - t.START, "source_pins": before,
                 "unchanged_launch": True, "final_targeted_control_passed": True,
                 "prior_suite_assertion_failures_retained": [prior["error"], third["error"]],
                 "operational_guard": "UNRUN", "no_claim_all_cases_on_final_shim": True})


if __name__ == "__main__":
    main()
