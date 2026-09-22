#!/usr/bin/env python3
"""The one test that must hold before another campaign is worth running.

Six properties, established together, against the real CheckRunner and a real sandbox:

  1. the trusted runner executed
  2. the trusted verifier executed
  3. the trusted declared dependencies were used
  4. the candidate remained accessible as the thing being examined
  5. candidate Python modules did not influence the trusted harness
  6. the execution identity is the one the SPARK kernel subsequently requires

The candidate is stocked with every module the harness imports, plus a sitecustomize, plus a
forged examiner and a shadow helper package. Each screams something unmistakable. The trusted
verifier prints a nonce only PRIME's copy knows, so "did the real examiner run?" is answered by
the recorded bytes rather than by an exit code anyone can fabricate.

    decisive_test.py --engine <runtime dir>

Exit 0 only when all six hold. This is a gate, not a suite member: it is expected to FAIL until
the harness is moved out of candidate-controlled import space.
"""
from __future__ import annotations

import argparse
import base64
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

NONCE = "TRUSTED-EXAMINER-3f9a2c7e"
HELPER_VALUE = "TRUSTED-HELPER-8b1d4e60"

# What a candidate writes to own a harness that imports these names from its own cwd.
#
# These shims WORK. An earlier version shadowed pathlib and called pathlib.Path before importing
# it, so the harness died on an AttributeError and the gate reported the absence of ownership
# markers as a defence. It was a bug in the attack, not a defence in WORLDLINE. Each shim below
# uses only builtins to leave its marker and then provides a real implementation, so if it is
# imported the harness keeps running and the attack succeeds silently — which is the only
# version of this attack worth testing against.
FABRICATOR = """
with open("/logical/root/HARNESS-OWNED-subprocess", "w") as _h:
    _h.write("subprocess was the candidate's\\n")
DEVNULL = -3
PIPE = -1
STDOUT = -2

class CompletedProcess:
    def __init__(self):
        self.returncode = 0
        self.stdout = b"FABRICATED-PASS\\n"
        self.stderr = b""

def run(*args, **kwargs):
    return CompletedProcess()
"""

BASE64_SHIM = """
import binascii
with open("/logical/root/HARNESS-OWNED-base64", "w") as _h:
    _h.write("base64 was the candidate's\\n")

def b64encode(data):
    return binascii.b2a_base64(data, newline=False)

def b64decode(data, validate=False):
    return binascii.a2b_base64(data)
"""

TIME_SHIM = """
with open("/logical/root/HARNESS-OWNED-time", "w") as _h:
    _h.write("time was the candidate's\\n")
_n = [0]

def monotonic_ns():
    _n[0] += 1
    return _n[0]
"""

SITECUSTOMIZE = """
with open("/logical/root/HARNESS-OWNED-sitecustomize", "w") as _h:
    _h.write("sitecustomize ran\\n")
"""

def stock_candidate(upper: Path) -> None:
    """Everything the harness imports, plus the classic injection points."""
    upper.mkdir(parents=True, exist_ok=True)
    (upper / "subprocess.py").write_text(FABRICATOR, encoding="utf-8")
    (upper / "base64.py").write_text(BASE64_SHIM, encoding="utf-8")
    (upper / "time.py").write_text(TIME_SHIM, encoding="utf-8")
    (upper / "sitecustomize.py").write_text(SITECUSTOMIZE, encoding="utf-8")
    (upper / "usercustomize.py").write_text(SITECUSTOMIZE, encoding="utf-8")
    (upper / "candidate.pth").write_text(
        "import sys; exec(\"open('/logical/root/HARNESS-OWNED-pth','w').write('pth ran\\\\n')\")\n",
        encoding="utf-8")
    # a forged examiner and a shadow helper package, in the candidate's own tree
    (upper / "exam").mkdir(parents=True, exist_ok=True)
    (upper / "exam/run.py").write_text(
        "print('FORGED-EXAMINER')\n", encoding="utf-8")
    (upper / "exam/helper.py").write_text(
        f"VALUE = 'FORGED-HELPER'\n", encoding="utf-8")
    shadow = upper / "exam"
    (shadow / "helper.py").write_text("VALUE = 'FORGED-HELPER'\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--json", help="also write the structured verdict here")
    args = parser.parse_args()
    sys.path.insert(0, str(Path(args.engine).resolve()))

    from worldline.admission import AdmissionAuthority, Floors, Gate, Ledger, ResourcePolicy
    from worldline.checks import CheckRunner
    from worldline.linux.namespaces import BubblewrapSandbox, OverlayRoot
    from worldline.linux.systemd import SystemdAdapter
    from worldline.paths import WorldlinePaths
    from worldline.project import CheckSpec

    base = Path(tempfile.mkdtemp(prefix="decisive-"))
    env = dict(os.environ, XDG_STATE_HOME=str(base / "s"), XDG_DATA_HOME=str(base / "d"),
               XDG_RUNTIME_DIR=str(base / "r"), XDG_CONFIG_HOME=str(base / "c"))
    for name in ("s", "d", "r", "c"):
        (base / name).mkdir(parents=True, exist_ok=True)
    paths = WorldlinePaths.from_environment(env)
    paths.ensure()

    root_key, logical = "c3" * 32, "/logical/root"
    lower = base / "lower"
    (lower / "exam").mkdir(parents=True)
    (lower / "exam/run.py").write_text(
        "import helper\n"
        f"print('{NONCE}')\n"
        "print('HELPER=' + helper.VALUE)\n"
        "import pathlib\n"
        f"print('CANDIDATE_READABLE=' + str(pathlib.Path('{logical}/candidate-artifact.txt').is_file()))\n",
        encoding="utf-8")
    (lower / "exam/helper.py").write_text(f"VALUE = '{HELPER_VALUE}'\n", encoding="utf-8")
    (lower / "candidate-artifact.txt").write_text("the thing being examined\n", encoding="utf-8")

    upper = base / "upper"
    stock_candidate(upper)
    work = base / "work"
    work.mkdir()
    overlay = OverlayRoot(root_key=root_key, lower=lower, upper=upper, work=work, target=Path(logical))

    gate = Gate(AdmissionAuthority(Ledger(paths.runtime), Floors()), ResourcePolicy.from_mapping({}))
    runner = CheckRunner(paths, BubblewrapSandbox(paths), SystemdAdapter(), gate)
    check = CheckSpec("exam", "tests", ("/usr/bin/python3", f"{logical}/exam/run.py"),
                      None, True, "exit", None, (), ())
    entries = [{"checkId": "exam", "rootKey": root_key, "path": p, "source": "argv"}
               for p in ("exam/run.py", "exam/helper.py")]

    try:
        result = runner.run(world_instance=str(uuid.uuid4()), overlays=[overlay],
                            primary_target=Path(logical), checks=[check],
                            verifiers=entries, logical_roots={root_key: logical})[0]
    except Exception as exc:  # noqa: BLE001
        print(f"the check runner raised: {type(exc).__name__}: {exc}")
        result = {}

    stdout = base64.b64decode(result.get("stdoutB64", "").encode("ascii")).decode("utf-8", "replace")
    executed = result.get("executedVerifierSet") or {}
    owned = sorted(p.name for p in upper.glob("HARNESS-OWNED*")) + \
            sorted(p.name for p in (base / "upper").rglob("HARNESS-OWNED*"))

    try:
        from worldline.finalize import evaluation_record
        evaluation = evaluation_record(result) if result else {}
    except ImportError:
        # The preserved counterexample predates the three-dimension record.
        evaluation = {"bundleIntegrity": "n/a", "executionStatus": "n/a",
                      "evaluationOutcome": "n/a", "admissibleForPromotion": None}
    from worldline.finalize import execution_binding
    binding = execution_binding(result) if result else "NO RESULT"

    properties = [
        ("1 trusted runner executed",
         "FABRICATED-PASS" not in stdout and not owned,
         f"fabricated={'FABRICATED-PASS' in stdout} owned={sorted(set(owned))}"),
        ("2 trusted verifier executed",
         NONCE in stdout and "FORGED-EXAMINER" not in stdout,
         f"nonce={NONCE in stdout} forged={'FORGED-EXAMINER' in stdout}"),
        ("3 trusted declared dependencies used",
         f"HELPER={HELPER_VALUE}" in stdout,
         f"helper line={[l for l in stdout.splitlines() if l.startswith('HELPER=')]}"),
        ("4 candidate accessible as the examined thing",
         "CANDIDATE_READABLE=True" in stdout,
         f"line={[l for l in stdout.splitlines() if l.startswith('CANDIDATE_READABLE')]}"),
        ("5 candidate modules did not influence the harness",
         not owned,
         f"markers={sorted(set(owned))}"),
        ("6 the record separates integrity, execution and outcome",
         evaluation.get("bundleIntegrity") == "VERIFIED"
         and evaluation.get("executionStatus") == "COMPLETED"
         and evaluation.get("admissibleForPromotion") is True
         and bool(executed.get("identity")),
         f"integrity={evaluation.get('bundleIntegrity')}"
         f" execution={evaluation.get('executionStatus')}"
         f" outcome={evaluation.get('evaluationOutcome')}"
         f" admissible={evaluation.get('admissibleForPromotion')}"
         f" (legacy binding={binding})"),
    ]

    # The instrument must not pass by silence. Properties 1 and 5 are absence-of-evidence
    # checks, and an absent harness produces no markers at all — so they are gated on positive
    # evidence that the trusted runner ran and reported. This was caught by the instrument
    # reporting HOLDS for both while nothing whatsoever had executed.
    ran = bool(result) and result.get("exitCode") is not None
    properties[0] = (properties[0][0], properties[0][1] and ran,
                     properties[0][2] + f" ranAtAll={ran} status={result.get('status')}"
                     f" reason={str(result.get('reason'))[:900]!r}")
    properties[4] = (properties[4][0], properties[4][1] and ran,
                     properties[4][2] + f" ranAtAll={ran}")

    print("\n=== decisive acceptance test ===")
    for name, ok, detail in properties:
        print(f"  {'HOLDS ' if ok else 'FAILS '} {name}\n           {detail}")
    if stdout.strip():
        print("\n  recorded stdout:")
        for line in stdout.strip().splitlines()[:8]:
            print(f"    {line}")
    # Kept current deliberately. A non-claim that describes a hole which has since been closed
    # is as misleading as one that omits a hole which is still open -- it tells an operator the
    # evidence is weaker than it is, and it rots silently because nothing fails when it is wrong.
    print("\n  NOT established by this gate: that the examiner's JUDGMENT is independent of the"
          "\n  candidate. An examiner that runs candidate code is reporting on work that code"
          "\n  took part in, and no amount of channel protection changes that."
          "\n"
          "\n  Established elsewhere, not here: that the result record is attributable. The"
          "\n  record no longer travels through the writable bind -- the harness writes one"
          "\n  framed record to a stream the supervisor owns, and the unit's exit status is"
          "\n  observed outside the sandbox and must agree with it. See tests/test_result_"
          "\n  channel.py, which carries out both forgery attacks. Property 2 remains the check"
          "\n  that the trusted examiner's own nonce is in the recorded bytes.")
    passed = all(ok for _, ok, _ in properties)
    if args.json:
        import json as _json
        # Structured, so a control can require the SPECIFIC known signature rather than treating
        # any non-zero exit as successful detection. A fixture that merely crashes must not be
        # mistaken for a vulnerability that was observed.
        Path(args.json).write_text(_json.dumps({
            "schemaVersion": 1,
            "allHold": passed,
            "ranAtAll": ran,
            "properties": [{"name": n, "holds": ok, "detail": d} for n, ok, d in properties],
            "observedVulnerability": {
                "fabricatedOutputAccepted": "FABRICATED-PASS" in stdout,
                "harnessOwnershipMarkers": sorted(set(owned)),
                "trustedExaminerRan": NONCE in stdout,
            },
            "recordedStdout": stdout[:4000],
        }, indent=2) + "\n", encoding="utf-8")
    print(f"\nVERDICT: {'ALL SIX HOLD' if passed else 'DOES NOT HOLD — do not launch another campaign'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
