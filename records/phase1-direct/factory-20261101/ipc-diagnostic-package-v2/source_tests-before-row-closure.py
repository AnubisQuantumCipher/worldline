"""Pure synthetic collector/guard tests; no runtime entry point or real OS evidence."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import io
import json
import tarfile
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COLLECTOR = ROOT / "records/phase1-direct/completion-20261026/ram_qualification_v6.py"
GUARD = HERE.parent / "ipc_diagnostic_guard_v3.py"
COLLECTOR_PIN = "a3fb057ec60841ded57b3611662336974285bb7ca13e4ef2c6611aa80b0dbb77"
GUARD_PIN = "a3ac95a4228f1b4ba7be02349e5963d877a251bfe169880c8c88cd3bf3201ec2"
PREVIOUS = COLLECTOR.with_name("ram_qualification_v4.py")
PREVIOUS_GUARD = GUARD.with_name("ipc_capacity_guard_v1.py")
OPEN_TAR = tarfile.open


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Definitions only; never __main__.
    return module


def formation():
    old, new = PREVIOUS.read_text(), COLLECTOR.read_text()
    a = {n.name: n for n in ast.parse(old).body if isinstance(n, ast.FunctionDef)}
    b = {n.name: n for n in ast.parse(new).body if isinstance(n, ast.FunctionDef)}
    changed = [n for n in a if ast.dump(a[n]) != ast.dump(b[n])]
    require(changed == ["parent"], "unexpected inherited function delta")
    transformed = old.replace("private-ipc-probe-v1/probe.py", "private-ipc-probe-v3/probe.py")
    transformed = transformed.replace('import json\n', 'import json\nimport math\nimport zlib\n')
    transformed = transformed.replace(
        "692c99dd98d2da06087346b641236307fc1512aa7dd95a981cac48e2f7cc1693",
        "8d7816d6a37ed353c6682dd27b97c4b7cbbc95f7e20282cb84a4c10177b16260")
    transformed = transformed.replace('mode + "-v4"', 'mode + "-v6"')
    transformed = transformed.replace('    save(base / "ipc-profile-check.json", control)\n',
        '    save(base / "ipc-profile-check.json", control)\n'
        '    diagnostic = diagnostic_write(base, complete, tool) if mode == "ipc-probe" else None\n')
    transformed = transformed.replace('         "private_ipc_control": control,',
        '         "private_ipc_control": control,\n'
        '         "mount_diagnostic_receipt": diagnostic,')
    normalized = ast.parse(new)
    normalized.body = [n for n in normalized.body if not
                       (isinstance(n, ast.FunctionDef) and n.name not in a) and not
                       (isinstance(n, ast.ClassDef) and n.name == "DiagnosticInflater")]
    require(ast.dump(normalized) == ast.dump(ast.parse(transformed)), "unregistered collector delta")
    expected_guard = PREVIOUS_GUARD.read_text()
    for before, after in (("private-ipc-probe-job-v1", "private-ipc-diagnostic-job-v3"),
                          ("ipc_capacity_guard_v1.jsonl", "ipc_diagnostic_guard_v3.jsonl"),
                          ("ram-qualification-ipc-probe-v4", "ram-qualification-ipc-probe-v6"),
                          ("ram_qualification_v4.py", "ram_qualification_v6.py")):
        expected_guard = expected_guard.replace('"' + before + '"', '"' + after + '"')
    require(GUARD.read_text() == expected_guard, "guard is not four-literal-only copy")
    lengths = {n.name: n.end_lineno - n.lineno + 1 for n in ast.walk(ast.parse(new))
               if isinstance(n, ast.FunctionDef)}
    require(max(lengths.values()) <= 60, "collector function exceeds60lines")
    return dict(changed_inherited_functions=changed, guard_four_literals_only=True,
                unchanged_parent_exit_AST=True, maximum_collector_function_lines=max(lengths.values()),
                new_consumer_functions=sorted(set(b) - set(a)))


def synthetic_reports():
    tests = load(HERE.parent / "private-ipc-probe-v3/source_tests.py", "v3_pure_fixtures")
    probe = tests.load_source()
    rows = list(tests.BASE)
    rows[2] = rows[2].replace("/dev/shm rw", "/dev/shm ro")
    normal, error = tests.observe(probe, rows)
    require(error == "private shm mount mismatch", "synthetic original predicate changed")
    duplicate, _ = tests.observe(probe, rows + [rows[2]])
    overflow_rows = rows + [str(i) + " 2 0:3 /" + "x" * 109 +
                            " /dev/shm rw - tmpfs tmpfs rw" for i in range(6, 28)]
    incomplete, error = tests.observe(probe, overflow_rows)
    require(error == "shm candidate evidence incomplete: bound refusal", "incomplete fixture")
    return normal, duplicate, incomplete


def fixture(facts, receipt=None, raw=None, duplicate=False):
    stdout = raw if raw is not None else (json.dumps(facts, sort_keys=True) + "\n").encode("ascii")
    payloads = {"tool.stdout": stdout, "tool.stderr": b""}
    if receipt is not None:
        payloads["tmp/private-ipc-probe.json"] = (json.dumps(receipt, indent=2,
                                                            sort_keys=True) + "\n").encode("ascii")
    files, buffer = {}, io.BytesIO()
    with OPEN_TAR(fileobj=buffer, mode="w:gz", format=tarfile.USTAR_FORMAT) as archive:
        for name, raw_bytes in payloads.items():
            item = tarfile.TarInfo(name)
            item.size = len(raw_bytes)
            archive.addfile(item, io.BytesIO(raw_bytes))
            if duplicate and name == "tool.stdout":
                archive.addfile(item, io.BytesIO(raw_bytes))
            files[name] = dict(kind="file", mode=item.mode, uid=0, gid=0, mtime_ns=0, bytes=len(raw_bytes),
                               sha256=hashlib.sha256(raw_bytes).hexdigest())
    archive = buffer.getvalue()
    tool = dict(exit_code=2, stop=None)
    inside = dict(files=files, tool=tool, archive=dict(bytes=len(archive),
                  sha256=hashlib.sha256(archive).hexdigest(), full_content_and_metadata_comparison=True))
    return dict(archive=archive, inside=inside, tool=tool)


def evaluate(collector, case, complete=True):
    with patch.object(collector, "bounded_text", return_value=json.dumps(case["inside"])):
        with patch.object(collector, "digest", return_value=hashlib.sha256(case["archive"]).hexdigest()):
            with patch.object(collector.Path, "stat", return_value=SimpleNamespace(st_size=len(case["archive"]))):
                with patch.object(collector.Path, "open", side_effect=lambda *a, **k: io.BytesIO(case["archive"])):
                    return collector.mount_diagnostic(Path("/synthetic/not-opened"), complete, case["tool"])


def outcome(results, name, value, accepted=False, error=None):
    require(value["mechanism_qualified"] is False and value["phase_acceptance"] is False,
            name + ": accidental qualification")
    require(value["terminal_tool_failure"] is True, name + ": terminal failure promoted")
    require((value["interpretation"] != "UNPROVEN") == accepted, name + ": wrong interpretation")
    if error is not None:
        require(error in value.get("error", ""), name + ": wrong diagnostic error " + str(value))
    results.append(dict(name=name, result=value))


def core_cases(collector, normal, duplicate, incomplete, results):
    result = evaluate(collector, fixture(normal))
    outcome(results, "tool-exit2-original-predicate-no-result", result, True)
    require(result["optional_result"] == "ABSENT", "absent result replaced stdout")
    changed = copy.deepcopy(normal)
    changed["mount_evidence"]["opened_fd_mount_id"] = "999"
    changed["shm_fdinfo"] = changed["shm_fdinfo"].replace("mnt_id:\t3", "mnt_id:\t999")
    outcome(results, "unknown-FD999", evaluate(collector, fixture(changed)),
            error="missing/ambiguous")
    outcome(results, "duplicate-FD-row-ID", evaluate(collector, fixture(duplicate)),
            error="missing/ambiguous")
    changed = copy.deepcopy(incomplete)
    changed["mount_evidence"]["candidate_lines_joined_LF_sha256"] = "f" * 64
    result = evaluate(collector, fixture(changed))
    outcome(results, "incomplete-declared-hash-never-verified-from-prefix", result,
            error="incomplete")
    require(result["candidate_digest_verified"] is False and result["fd_join"] == "UNPROVEN",
            "incomplete hash/global join claimed")
    earlier = copy.deepcopy(normal)
    earlier.update(status="PASSED", stage="completed")
    earlier.pop("error", None)
    result = evaluate(collector, fixture(normal, receipt=earlier))
    outcome(results, "earlier-success-result-final-failure-stdout-exit2", result,
            error="result/stdout disagreement")
    require(result["optional_result"] == "DIFFERENT", "stale success receipt ignored")
    outcome(results, "matching-optional-report-exit2-still-failure",
            evaluate(collector, fixture(normal, receipt=normal)), True)


def tamper_cases(collector, normal, results):
    mutations = (("candidate_count", True), ("retained_rows", True), ("omitted_rows", -1),
                 ("candidate_count", 512), ("complete", False), ("selected_id_exact", False),
                 ("candidate_lines_joined_LF_sha256", "f" * 64),
                 ("selected_mount_id", "999"), ("selected_line_index", True),
                 ("selected_mount_id_sha256", "f" * 64), ("equal_longest_count", True),
                 ("ambiguous", True), ("opened_fd_mount_id", "not-decimal"))
    for field, value in mutations:
        changed = copy.deepcopy(normal)
        changed["mount_evidence"][field] = value
        outcome(results, "forged-" + field, evaluate(collector, fixture(changed)))
    for name, index in (("boolean", True), ("negative", -1), ("too-large", 512), ("duplicate", 0)):
        changed = copy.deepcopy(normal)
        changed["mount_evidence"]["rows"][1]["line_index"] = index
        outcome(results, "forged-index-" + name, evaluate(collector, fixture(changed)))
    changed = copy.deepcopy(normal)
    changed["mount_evidence"]["rows"].reverse()
    outcome(results, "out-of-order-indices", evaluate(collector, fixture(changed)))
    changed = copy.deepcopy(normal)
    changed["mount_evidence"]["rows"][0]["raw"] = "not a mount row"
    outcome(results, "malformed-raw-row", evaluate(collector, fixture(changed)))
    changed = copy.deepcopy(normal)
    changed["shm_fdinfo"] += "mnt_id:\t3\n"
    outcome(results, "duplicate-fdinfo-ID-fields", evaluate(collector, fixture(changed)))
    changed = copy.deepcopy(normal)
    changed["mount_evidence"]["opened_fd_mount_id"] = "999"
    outcome(results, "forged-ID-vs-fdinfo", evaluate(collector, fixture(changed)))


def archive_cases(collector, normal, results):
    for name, field, value in (("archive-hash", "sha256", "f" * 64),
                              ("restore-not-verified", "full_content_and_metadata_comparison", False),
                              ("archive-size", "bytes", 1)):
        case = fixture(normal)
        case["inside"]["archive"][field] = value
        outcome(results, name, evaluate(collector, case))
    outcome(results, "no-complete-archive", evaluate(collector, fixture(normal), False))
    case = fixture(normal)
    case["inside"]["files"]["tool.stdout"]["sha256"] = "f" * 64
    outcome(results, "stdout-inventory-digest-forged", evaluate(collector, case))
    case = fixture(normal)
    case["inside"]["files"]["tool.stdout"]["bytes"] = True
    outcome(results, "stdout-inventory-bool-size", evaluate(collector, case))
    outcome(results, "duplicate-stdout-tar-member", evaluate(collector, fixture(normal, duplicate=True)))


def encoding_cases(collector, normal, results):
    encoded = json.dumps(normal, sort_keys=True).encode("ascii")
    raw = encoded[:-1] + b', "schema":"duplicate"}'
    outcome(results, "duplicate-JSON-key", evaluate(collector, fixture(normal, raw=raw)))
    for constant in (b"NaN", b"Infinity", b"-Infinity"):
        raw = encoded[:-1] + b',"extra":' + constant + b'}'
        outcome(results, "nonfinite-" + constant.decode(), evaluate(collector, fixture(normal, raw=raw)))
    outcome(results, "aggregate-stdout-cap", evaluate(collector, fixture(normal, raw=b"x" * 8194)))
    raw = encoded + b" " * (8193 - len(encoded))
    outcome(results, "compact-8193-non-newline-refusal", evaluate(collector, fixture(normal, raw=raw)))
    changed = copy.deepcopy(normal)
    changed["mount_evidence"]["extra"] = "x" * 3073
    outcome(results, "aggregate-mount-evidence-cap", evaluate(collector, fixture(changed)))
    changed = copy.deepcopy(normal)
    changed["padding"] = ""
    empty = len(json.dumps(changed, sort_keys=True).encode("ascii"))
    changed["padding"] = "x" * (8192 - empty)
    compact = len(json.dumps(changed, sort_keys=True).encode("ascii"))
    pretty = len((json.dumps(changed, sort_keys=True, indent=2) + "\n").encode("ascii"))
    require(compact == 8192 and pretty > 8192, "pretty/compact boundary fixture")
    result = evaluate(collector, fixture(changed))
    outcome(results, "pretty-overflow-compact8192-no-result-exit2", result, True)
    return dict(compact_bytes=compact, pretty_bytes=pretty, result_file="ABSENT", terminal_exit=2)


def main():
    require(hashlib.sha256(COLLECTOR.read_bytes()).hexdigest() == COLLECTOR_PIN,
            "derived collector pin changed")
    require(hashlib.sha256(GUARD.read_bytes()).hexdigest() == GUARD_PIN, "derived guard pin changed")
    collector = load(COLLECTOR, "pure_collector_v5")
    normal, duplicate, incomplete = synthetic_reports()
    results = []
    structure = formation()
    core_cases(collector, normal, duplicate, incomplete, results)
    tamper_cases(collector, normal, results)
    archive_cases(collector, normal, results)
    encoding = encoding_cases(collector, normal, results)
    evidence = dict(schema="worldline.ipc-diagnostic-package-v2.synthetic-tests.v1",
                    status="TESTED_AUTHOR_SYNTHETIC_ONLY_NOT_INDEPENDENT_REVIEW",
                    collector_sha256=COLLECTOR_PIN, guard_sha256=GUARD_PIN,
                    structure=structure, cases=results, pretty_compact_boundary=encoding,
                    actual_probe_or_runtime_entry_executed=False, phase_acceptance=False,
                    boundary="In-memory synthetic USTAR/gzip fixtures. Inside receipt/Path.stat/digest/"
                    "archive-open boundary mocked; bounded in-memory USTAR scan and "
                    "stream digest checks. V3 fixture observation uses mocked read_limited and forbids "
                    "os.open. No actual mounts/FDs/IPC/runtime entry/heavy job/compiler/proof.")
    data = (json.dumps(evidence, sort_keys=True, indent=2) + "\n").encode("ascii")
    require(len(data) <= 131072, "synthetic receipt byte bound")
    with (HERE / "source-tests.json").open("xb") as stream:
        require(stream.write(data) == len(data), "short synthetic receipt write")
    print(json.dumps(dict(status=evidence["status"], cases=len(results),
                          receipt_bytes=len(data), structure=structure), sort_keys=True))


if __name__ == "__main__":
    main()
