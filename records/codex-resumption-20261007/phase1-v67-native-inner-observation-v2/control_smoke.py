"""Main-only real machinery control; NEVER N67 native or runtime evidence."""
from __future__ import annotations

import native_observation
import observation_support as s


def run(attempt, unit, manifest, custody):
    result = native_observation.run(attempt, unit, manifest, custody, "observer-control-only")
    stdout = (attempt / "tests.stdout").read_bytes()
    stderr = (attempt / "tests.stderr").read_bytes()
    passed = (result["status"] == "ACTUAL_OBSERVER_CONTROL_ONLY_NO_NATIVE_EVIDENCE"
              and result["terminal_retention_complete"]
              and result["actual_debugger_Popen_wait_returncode"] == 0
              and stdout == b"OBSERVER_CONTROL_ONLY\n"
              and stderr == b"OBSERVER_CONTROL_STDERR_ONLY\n"
              and not result["samples"]
              and (attempt / "tests.native-boundaries.stdout").read_bytes() == b"OBSERVER_CONTROL_ONLY_REGULAR_FD\n")
    s.save_new(attempt / "observer-control-smoke.json", {
        "schema": "worldline-N67-real-observer-control-smoke-v1",
        "at": s.utc_now(), "attempt": str(attempt), "candidate": str(s.F),
        "manifest": s.pin(s.F / "manifest.json"), "identity": s.pin(s.F / "identity.json"),
        "inner_observation": s.pin(attempt / "inner-observation.json"),
        "actual_machinery_control_pass": passed,
        "native_target_run": False, "original_controls_run": False,
        "native_stack_or_cost_claim": False, "runtime_acceptance": False,
        "fixture_authority": False, "phase_acceptance": False, "timeout_resolution": False})
    return passed
