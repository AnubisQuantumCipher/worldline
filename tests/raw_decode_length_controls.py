"""Out-of-process native decoder preconditions; crashes never count as refusal."""
from pathlib import Path
import argparse
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REJECTION = re.compile(
    r"raised ADA\.ASSERTIONS\.ASSERTION_ERROR : failed precondition from "
    r"worldline-retained_raw_decode\.ads:[0-9]+")



def validate_roster(cases):
    spec = (ROOT / "core/worldline-retained_raw_decode.ads").read_text()
    spec = re.sub(r"--[^\n]*", "", spec)
    declared = re.findall(
        r"function\s+Load\s*\(Data\s*:\s*Q.Byte_Array\)\s*return\s+([\w.]+)", spec)
    if not declared or sorted(item["type"] for item in cases) != sorted(declared):
        raise ValueError("decoder fixture must cover every declared Load overload")
    ids = [item["case"] for item in cases]
    if ids != list(range(1, len(declared) + 1)):
        raise ValueError("decoder probe case IDs must be complete and unique")
    test_source = (ROOT / "tests/raw_decode_tests.adb").read_text()
    instantiated = re.findall(
        r"procedure Case_([0-9]+) is new Raw_Decode_Case \(D\.([\w.]+), D.Load,",
        test_source)
    if [(int(index), name) for index, name in instantiated] != [
            (item["case"], item["type"]) for item in cases]:
        raise ValueError("decoder fixture and compiled probe mapping differ")
    for case in cases:
        if not 0 < case["value_bytes"] <= case["object_bytes"]:
            raise ValueError("invalid compiler representation widths")


def run_case(case, length, admitted):
    child = subprocess.run(
        [str(ROOT / "bin/raw-decode-contracts/raw_decode_tests"), str(case["case"]), str(length)],
        text=True, capture_output=True, timeout=10, check=False)
    if admitted:
        passed = child.returncode == 0 and child.stdout.strip() == "ACCEPTED"
    else:
        passed = child.returncode == 1 and bool(REJECTION.fullmatch(child.stderr.strip()))
    return {"case": case, "length": length, "admitted": admitted,
            "exit_code": child.returncode, "stdout": child.stdout,
            "stderr": child.stderr, "passed": passed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    cases = json.loads((ROOT / "tests/raw_decode_layout_cases.json").read_text())
    validate_roster(cases)
    results = []
    for case in cases:
        value, storage = case["value_bytes"], case["object_bytes"]
        controls = [(length, True) for length in sorted({value, storage})]
        controls += [(0, False), (storage + 1, False)]
        if value + 1 < storage:
            controls.append((value + 1, False))
        for length, admitted in controls:
            results.append(run_case(case, length, admitted))
            args.out.write_text(json.dumps(results, indent=2) + "\n")
    passed = all(result["passed"] for result in results)
    print(json.dumps({"controls": len(results), "passed": passed}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
