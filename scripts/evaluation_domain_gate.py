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


def run(engine: Path, core_lib: Path | None) -> tuple[int, str]:
    environment = None
    if core_lib is not None:
        import os
        environment = {**os.environ, "WORLDLINE_CORE_LIB": str(core_lib)}
    proc = subprocess.run([sys.executable, str(DECISIVE), "--engine", str(engine)],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                          timeout=900, env=environment)
    return proc.returncode, proc.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--counterexample", help="a preserved vulnerable runtime that MUST fail")
    parser.add_argument("--core-lib")
    args = parser.parse_args()
    core = Path(args.core_lib) if args.core_lib else None

    code, output = run(Path(args.engine), core)
    print("== candidate acceptance ==")
    print(output.rstrip())
    ok = code == 0
    if not ok:
        print("\nGATE FAILED: the candidate build does not hold the evaluation-domain properties.")

    if args.counterexample:
        control_code, control_output = run(Path(args.counterexample), core)
        print("\n== counterexample control ==")
        print(control_output.rstrip())
        if control_code == 0:
            print("\nGATE FAILED: the preserved vulnerable build PASSED, so the instrument is"
                  " no longer detecting the defect it exists for. A green candidate proves"
                  " nothing until this fails.")
            ok = False
        else:
            print("\ncounterexample control: correctly refused")
    print(f"\nEVALUATION DOMAIN GATE: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
