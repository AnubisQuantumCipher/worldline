#!/usr/bin/python3
"""Targeted final shim qualification; preserve and source-bind first suite."""
import json
import time
import run_tests as t


def main():
    names = t.SOURCES + ("final_tests.py",)
    before = {name: t.digest(t.BASE / name) for name in names}
    t.write_json(t.BASE / "final-03-source-at-execution.json", before)
    prior = json.loads((t.BASE / "test-results.json").read_text())
    assert prior["source_pins"]["launch.sh"] == before["launch.sh"]
    assert prior["source_pins"]["tee-fixture.sh"] == before["tee-fixture.sh"]
    compile_run = t.execute(["/usr/bin/gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                             "-Wpedantic", "-Wconversion", "-Wshadow", "-Wformat=2", "-O2",
                             "-fPIC", "-shared", "-o", str(t.BASE / "fault-final.so"),
                             str(t.BASE / "fault.c"), "-ldl"])
    t.write_json(t.BASE / "final-03-compile-command.json", compile_run)
    assert compile_run["returncode"] == 0
    # The wrapper's exact final-shim copy has separate fixed path, no product env.
    final_wrapper = t.BASE / "tee-final-fixture.sh"
    final_wrapper.write_text((t.BASE / "tee-fixture.sh").read_text().replace("fault.so", "fault-final.so"))
    old_variant = t.variant

    def final_variant(folder, body):
        path, replacements = old_variant(folder, body)
        old = str(t.BASE / "tee-fixture.sh")
        new = str(final_wrapper)
        path.write_text(path.read_text().replace(old, new))
        replacements.append({"old": old, "new": new})
        return path, replacements

    t.variant = final_variant
    cases = [
        ("final-lost-diag", "    printf 'lost' || :", False, ("stdout", "lost_diag"), None),
        ("final-receipt-close", "    :", False, ("status", "close"), None),
        ("final-close-empty", "    :", False, ("stdout", "close"), None),
        ("final-stderr-first", "    printf 'lost' >&2 || :", False, ("stderr", "first_eio"), None),
        ("final-receipt-enospc", "    :", False, ("status", "first_enospc"), None),
        ("final-close-output", "    printf 'kept'", False, ("stdout", "close"), None),
        ("final-stderr-partial", "    printf 'abcdef' >&2 || :", False, ("stderr", "partial"), None),
        ("final-empty", "    :", True, None, None),
    ]
    error = None
    try:
        for index, args in enumerate(cases, 100):
            t.one_case(index, *args)
        rows = {row["case"]: row for row in t.RESULTS}
        assert rows["final-lost-diag"]["files"]["stdout-consumer.stderr"]["bytes"] == 0
        assert rows["final-lost-diag"]["files"]["stdout"]["bytes"] == 0
        assert rows["final-stderr-first"]["files"]["stderr"]["bytes"] == 0
        assert rows["final-stderr-partial"]["files"]["stderr"]["bytes"] == 1
        assert rows["final-close-output"]["files"]["stdout"]["text"] == "kept"
        text = rows["final-receipt-close"]["files"]["status"]["text"]
        assert text.count("=WAIT_STATUS:0") == 3 and "capture_rejected=0" in text
        assert all(row["passed"] for row in t.RESULTS)
        assert before == {name: t.digest(t.BASE / name) for name in names}
    except Exception as problem:
        error = repr(problem)
        raise
    finally:
        t.write_json(t.BASE / "final-test-results.json", {"results": t.RESULTS, "error": error,
                     "seconds": time.monotonic() - t.START, "source_pins": before,
                     "prior_launch_unchanged": True, "prior_suite": "test-results.json",
                     "prior_fixture_coverage_failure_retained": prior["error"],
                     "synthetic_only": True, "operational_guard": "UNRUN"})


if __name__ == "__main__":
    main()
