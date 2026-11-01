"""D161 permitted static checks only; never import or execute fixture/validator."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import stat
import time

ROOT = Path(__file__).resolve().parent
START = time.perf_counter()
MAX_FILE = 64 * 1024 * 1024


def require(condition, label):
    if not condition:
        raise ValueError(label)
    if time.perf_counter() - START > 7.5:
        raise TimeoutError("STATIC_TIME_RESERVATION_EXHAUSTED")


def identity(path):
    before = path.stat()
    require(stat.S_ISREG(before.st_mode), "NOT_REGULAR_INPUT")
    require(before.st_size <= MAX_FILE, "INPUT_FILE_LIMIT")
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        for _ in range(1024):
            chunk = stream.read(65536)
            if not chunk:
                break
            count += len(chunk)
            digest.update(chunk)
            require(count <= MAX_FILE, "INPUT_GROWTH_LIMIT")
        require(stream.read(1) == b"", "EXCESS_INPUT_BYTES")
    after = path.stat()
    require(before.st_size == after.st_size == count, "INPUT_SIZE_CHANGED")
    require(before.st_mtime_ns == after.st_mtime_ns, "INPUT_MTIME_CHANGED")
    return {"bytes": count, "sha256": digest.hexdigest()}


def check_inputs():
    packet = json.loads((ROOT / "input-references.json").read_text())
    refs = packet["references"]
    require(len(refs) <= 96, "REFERENCE_COUNT")
    for row in refs:
        require(identity(Path(row["path"])) ==
                {key: row[key] for key in ("bytes", "sha256")}, "INPUT_MISMATCH")
    base = ROOT.parent
    pins = json.loads((base / "o1-xgen-build-package-v2/input-pins.json").read_text())
    require(len(pins) == 342, "SOURCE_ROSTER_COUNT")
    for row in pins:
        require(identity(Path(row["path"])) == row["identity"], "SOURCE_PIN_MISMATCH")
    return {"immutable_references_matched": len(refs), "source_pins_matched": len(pins)}


def check_patch():
    dossier = ROOT.parent / "o1-gnatcoll-compatibility-dossier-v2"
    meta = json.loads((dossier / "identities.json").read_text())
    original = (ROOT / "original/gnatcoll-boyer_moore.adb").read_bytes()
    derived = (ROOT / "derived/gnatcoll-boyer_moore.adb").read_bytes()
    require(original == Path(meta["original"]["path"]).read_bytes(), "ORIGINAL_CHANGED")
    require(derived == derived.decode("ascii").encode("ascii"), "NON_ASCII_DERIVATIVE")
    work = original
    require(len(meta["replacements"]) == 3, "REPLACEMENT_COUNT")
    for row in meta["replacements"]:
        old, new = row["preimage"].encode(), row["replacement"].encode()
        require(work.count(old) == 1, "PREIMAGE_COUNT")
        work = work.replace(old, new, 1)
    require(work == derived, "DERIVATIVE_MISMATCH")
    for row in reversed(meta["replacements"]):
        old, new = row["preimage"].encode(), row["replacement"].encode()
        require(work.count(new) == 1, "POSTIMAGE_COUNT")
        work = work.replace(new, old, 1)
    require(work == original, "REVERSE_ROUNDTRIP")
    diff = "".join(difflib.unified_diff(
        original.decode().splitlines(keepends=True),
        derived.decode().splitlines(keepends=True),
        fromfile="upstream/gnatcoll/minimal/src/gnatcoll-boyer_moore.adb",
        tofile="prospective-derived/gnatcoll/minimal/src/gnatcoll-boyer_moore.adb"))
    require(diff.encode() == (ROOT / "prospective.diff").read_bytes(), "EXACT_PATCH")
    require(identity(ROOT / "derived/gnatcoll-boyer_moore.adb") ==
            {key: meta["prospective_derived"][key] for key in ("bytes", "sha256")},
            "DERIVED_IDENTITY")
    return {"three_sites_forward_reverse_exact": True, "unchanged_patch_exact": True}


def fold(char, sensitive):
    if not sensitive and "A" <= char <= "Z":
        return chr(ord(char) + 32)
    return char


def arithmetic_case(row):
    needle, text = row["motif"], row["text"]
    require(len(needle) <= 6 and len(text) <= 10, "CASE_LENGTH")
    require(row["text_first"] in (1, 5), "CASE_ORIGIN")
    answer = -1
    if needle and len(needle) <= len(text):
        for start in range(len(text) - len(needle) + 1):
            match = True
            for offset in range(len(needle)):
                if fold(needle[offset], row["case_sensitive"]) != fold(
                        text[start + offset], row["case_sensitive"]):
                    match = False
                    break
            if match:
                answer = row["text_first"] + start
                break
    require(answer == row["expected"], "CASE_ARITHMETIC")
    return answer


def check_cases_and_protocol():
    packet = json.loads((ROOT / "case-roster.json").read_text())
    cases = packet["cases"]
    require(len(cases) == 11, "LIFECYCLE_COUNT")
    expected = []
    for row in cases:
        result = arithmetic_case(row)
        expected.append((f"SEARCH {row['id']} EXPECTED {result} "
                         f"ORACLE {result} ACTUAL {result}").encode())
        expected.append(f"FREE {row['id']} COMPLETED 2".encode())
    require(sum(bool(row["motif"]) for row in cases) == 10, "NONEMPTY_COUNT")
    consumer = packet["consumer"]
    require(len(consumer) == 2, "CONSUMER_COUNT")
    require(len(consumer[0]["exact_ascii"]) == 47, "D01_LENGTH")
    require(len(consumer[1]["exact_ascii"]) == 23, "D02_LENGTH")
    require(consumer[0]["exact_ascii"].find("\nFrom ") + 1 == 24, "D01_SEPARATOR")
    require(consumer[0]["exact_ascii"].find("From b") + 1 == 25, "D01_MESSAGE")
    expected.extend([b"CONSUMER D01 TRUE TRUE FALSE", b"CONSUMER D02 TRUE FALSE",
                     b"COMPLETE SEARCH 11 FREE 11 CONSUMER 2"])
    source = (ROOT / "validation/validate_results.py").read_text()
    tree = ast.parse(source, filename="validation/validate_results.py")
    values = [ast.literal_eval(node.value) for node in tree.body
              if isinstance(node, ast.Assign) and any(
                  isinstance(name, ast.Name) and name.id == "EXPECTED_ROWS"
                  for name in node.targets)]
    require(len(values) == 1 and tuple(expected) == values[0], "PROTOCOL_LITERAL")
    require(len(expected) == 25 and max(map(len, expected)) <= 128, "PROTOCOL_BOUNDS")
    return {"cases_recomputed": 11, "consumer_lengths": [47, 23],
            "canonical_records": 25, "canonical_bytes": sum(map(len, expected)) + 25}


def check_python_source():
    files = [ROOT / "static_checks.py", ROOT / "validation/validate_results.py",
             ROOT / "validation/negative_controls.py"]
    routines = 0
    for path in files:
        tree = ast.parse(path.read_text(), filename=str(path.relative_to(ROOT)))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                require(node.end_lineno - node.lineno + 1 <= 60, "LONG_PYTHON_ROUTINE")
                routines += 1
    return {"python_files_AST_parsed": len(files), "short_python_routines": routines,
            "validator_or_controls_executed_or_imported": False}


def main():
    receipt = {"schema": "worldline.source-only-static-checks.v1",
               "command": "python3 static_checks.py (in owned source root)",
               "scope": "hash/roster, exact patch, finite literal arithmetic and AST only",
               "native_fixture_validator_controls": "NOT_RUN_FORBIDDEN",
               "prior_preparatory_command_wall_reservation_seconds": 2.0,
               "script_time_stop_seconds": 7.5,
               "aggregate_registered_ceiling_seconds": 10}
    status = 0
    try:
        receipt["input_readback"] = check_inputs()
        receipt["patch"] = check_patch()
        receipt["arithmetic_and_literal_protocol"] = check_cases_and_protocol()
        receipt["AST"] = check_python_source()
        receipt["state"] = "PASSED_LISTED_STATIC_CHECKS_ONLY"
    except (ValueError, OSError, KeyError, TypeError, SyntaxError, TimeoutError) as error:
        receipt["state"] = "FAILED_STATIC_CHECK_PRESERVED"
        receipt["error"] = type(error).__name__ + ": " + str(error)[:256]
        status = 1
    receipt["measured_script_seconds"] = round(time.perf_counter() - START, 6)
    with (ROOT / "static-verification.json").open("x") as output:
        json.dump(receipt, output, indent=2)
        output.write("\n")
    print(json.dumps(receipt))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
