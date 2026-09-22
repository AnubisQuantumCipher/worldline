#!/usr/bin/env python3
"""Release gate: the trusted evaluation domain, run as two evaluations with different purposes.

    CANDIDATE ACCEPTANCE  the proposed build must hold every property, INCLUDING positive
                          evidence that the intended examiner actually ran. Absence of an
                          attacker's fingerprints is not a defence if nothing executed.
    COUNTEREXAMPLE CONTROL a preserved vulnerable build must FAIL, which is what establishes that
                          the instrument can still see the defect it was written for.

Both are required. A gate that only checks the candidate cannot distinguish "the vulnerability is
fixed" from "the instrument stopped working".

    evaluation_domain_gate.py --engine <runtime> [--counterexample <runtime>]

Exit 0 only when the candidate holds and, when supplied, the counterexample fails.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECISIVE = HERE / "decisive_evaluation_test.py"


def run(engine: Path, core_lib: Path | None) -> tuple[int, str, dict]:
    import json
    import os
    import tempfile
    environment = None
    if core_lib is not None:
        environment = {**os.environ, "WORLDLINE_CORE_LIB": str(core_lib)}
    with tempfile.TemporaryDirectory(prefix="evaldomain-") as temporary:
        verdict_path = Path(temporary) / "verdict.json"
        proc = subprocess.run([sys.executable, str(DECISIVE), "--engine", str(engine),
                               "--json", str(verdict_path)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              timeout=900, env=environment)
        try:
            verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            verdict = {}
    return proc.returncode, proc.stdout, verdict


def candidate_holds(code: int, verdict: dict) -> bool:
    """The candidate arm passes only on a complete, positive verdict."""
    # `allHold` must be present AND true: a missing verdict file means the instrument did not
    # report, which is not the same as reporting success.
    return code == 0 and verdict.get("allHold") is True


def control_detected(code: int, verdict: dict) -> tuple[bool, str]:
    """The control arm passes only when the KNOWN DEFECT was observed.

    Every infrastructure failure also exits non-zero: an import error, an incompatible
    library, a missing fixture, a timeout. Reading any of those as "the vulnerability was
    detected" lets the instrument rot silently while reporting that it still works. The
    signature that distinguishes the real defect is specific and was established when the
    vulnerability was first reproduced: the harness reports success for work it never did,
    and the trusted examiner never runs.
    """
    observed = verdict.get("observedVulnerability") or {}
    if code == 0:
        return False, "the preserved vulnerable build PASSED: the instrument no longer detects the defect it exists for"
    if verdict.get("ranAtAll") is not True:
        return False, f"the control produced no run: ranAtAll={verdict.get('ranAtAll')!r} (a crash is not a detection)"
    if observed.get("trustedExaminerRan") is not False:
        return False, f"the control did not establish that the trusted examiner was bypassed: trustedExaminerRan={observed.get('trustedExaminerRan')!r}"
    if not (observed.get("fabricatedOutputAccepted") is True or observed.get("harnessOwnershipMarkers")):
        return False, "the control showed neither fabricated output nor harness ownership by candidate code"
    return True, (f"fabricated output {observed.get('fabricatedOutputAccepted')},"
                  f" harness ownership {observed.get('harnessOwnershipMarkers')},"
                  f" trusted examiner ran {observed.get('trustedExaminerRan')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--counterexample", required=True,
                        help="a preserved vulnerable runtime that MUST exhibit the known defect")
    parser.add_argument("--core-lib")
    args = parser.parse_args()
    core = Path(args.core_lib) if args.core_lib else None

    code, output, verdict = run(Path(args.engine), core)
    print("== candidate acceptance ==")
    print(output.rstrip())
    ok = candidate_holds(code, verdict)
    if not ok:
        print("\nGATE FAILED: the candidate build does not hold the evaluation-domain properties.")

    control_code, control_output, control = run(Path(args.counterexample), core)
    print("\n== counterexample control ==")
    print(control_output.rstrip())
    detected, detail = control_detected(control_code, control)
    if detected:
        print(f"\ncounterexample control: the known defect was OBSERVED — {detail}")
    else:
        print(f"\nGATE FAILED: {detail} (exit={control_code})."
              "\n  A vulnerable build that merely crashes is an instrument failure, not evidence"
              "\n  that the instrument still detects anything.")
        ok = False
    print(f"\nEVALUATION DOMAIN GATE: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
