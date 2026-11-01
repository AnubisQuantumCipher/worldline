"""Exact r1 counterexamples, bounded scanner controls and finalization containment."""
from pathlib import Path
import copy
import gzip
import hashlib
import io
import json
import tarfile
from unittest.mock import patch
import source_tests as tests

HERE = Path(__file__).resolve().parent


class RepeatedInput:
    def read(self, size):
        tests.require(0 <= size <= 65536, "synthetic writer read bound")
        return b"X" * size


def rebuild(case, extra_entries=(), listed=False):
    buffer = io.BytesIO()
    with tests.OPEN_TAR(fileobj=io.BytesIO(case["archive"]), mode="r:gz") as old:
        members = [(m, old.extractfile(m).read()) for m in old.getmembers()]
    with tests.OPEN_TAR(fileobj=buffer, mode="w:gz", format=tarfile.USTAR_FORMAT) as tar:
        for member, raw in members:
            tar.addfile(member, io.BytesIO(raw))
        for member in extra_entries:
            tar.addfile(member, RepeatedInput() if member.size else None)
            if listed:
                expected_hash = hashlib.sha256()
                for offset in range(0, member.size, 65536):
                    expected_hash.update(b"X" * min(65536, member.size - offset))
                case["inside"]["files"][member.name] = dict(kind="file", bytes=member.size,
                    mode=member.mode, uid=0, gid=0, mtime_ns=member.mtime * 1_000_000_000,
                    sha256=expected_hash.hexdigest())
    return set_archive(case, buffer.getvalue())


def set_archive(case, raw):
    case["archive"] = raw
    case["inside"]["archive"].update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    return case


def recorded_failure(collector, case, name):
    delivered, original = [], collector.DiagnosticInflater.read
    def traced(reader, size):
        try:
            return original(reader, size)
        finally:
            delivered.append(reader.expanded)
    with patch.object(collector.DiagnosticInflater, "read", traced):
        result = tests.evaluate(collector, case)
    tests.require(result["interpretation"] == "UNPROVEN" and not result["mechanism_qualified"],
                  name + ": malformed input interpreted")
    return dict(name=name, result=result, expanded_before_refusal=max(delivered, default=0),
                compressed_bytes=len(case["archive"]))


def exact_counterexamples(collector, normal):
    previous_tests = tests.load(HERE.with_name("ipc-diagnostic-package-v1") / "source_tests.py",
                                "preserved_r1_test_definitions")
    previous = previous_tests.load(previous_tests.COLLECTOR, "preserved_r1_collector")
    changed = copy.deepcopy(normal)
    changed["mount_evidence"]["rows"][0]["raw"] += "\n" + changed["mount_evidence"]["rows"][2]["raw"]
    joined = "\n".join(x["raw"] for x in changed["mount_evidence"]["rows"]).encode("ascii")
    changed["mount_evidence"]["candidate_lines_joined_LF_sha256"] = hashlib.sha256(joined).hexdigest()
    old_join = previous_tests.evaluate(previous, previous_tests.fixture(changed))
    tests.require(old_join["interpretation"] != "UNPROVEN", "r1 delimiter defect not reproduced")
    cases = [dict(name="exact-embedded-newline-false-join", previous=old_join,
                  revised=recorded_failure(collector, tests.fixture(changed), "embedded-newline"))]
    minimal = dict(schema="worldline.private-ipc-probe.v1", mode="normal", status="FAILED",
                   error="x" * 7900)
    raw = (json.dumps(minimal, sort_keys=True) + "\n").encode("ascii")
    tests.require(len(raw) == 7996, "exact7996-byte regression")
    try:
        previous_tests.evaluate(previous, previous_tests.fixture(minimal, raw=raw))
    except RuntimeError as error:
        tests.require(str(error) == "diagnostic summary byte bound", "wrong r1 summary defect")
        old_error = str(error)
    else:
        raise RuntimeError("r1 summary escape not reproduced")
    cases.append(dict(name="exact7996-byte-summary-escape", previous_error=old_error,
                      revised=recorded_failure(collector, tests.fixture(minimal, raw=raw), "large-error")))
    receipt = copy.deepcopy(normal)
    receipt["mount_evidence"]["candidate_count"] = 3.0
    old_optional = previous_tests.evaluate(previous, previous_tests.fixture(normal, receipt=receipt))
    tests.require(old_optional["optional_result"] == "IDENTICAL", "r1 numeric equality defect")
    cases.append(dict(name="exact-int3-float3.0-equality", previous=old_optional,
                      revised=recorded_failure(collector, tests.fixture(normal, receipt=receipt), "type-sensitive")))
    oversized = tarfile.TarInfo("unlisted33MiB")
    oversized.size = 33 * 1024**2
    bad = rebuild(previous_tests.fixture(normal), (oversized,))
    old_archive = previous_tests.evaluate(previous, bad)
    tests.require(old_archive["interpretation"] != "UNPROVEN", "r1 unlisted payload defect")
    revised_case = rebuild(tests.fixture(normal), (oversized,))
    revised = recorded_failure(collector, revised_case, "unlisted33MiB")
    tests.require(revised["expanded_before_refusal"] < 65536, "rejected payload expanded")
    cases.append(dict(name="exact-unlisted33MiB-archive", previous=old_archive, revised=revised))
    return cases


def scanner_cases(collector, normal):
    results = []
    members = [tarfile.TarInfo("unlisted" + str(i)) for i in range(1025)]
    case = rebuild(tests.fixture(normal), members)
    result = recorded_failure(collector, case, "1025-unlisted-headers")
    tests.require(result["expanded_before_refusal"] < 65536, "entry list expanded before refusal")
    results.append(result)
    member = tarfile.TarInfo("listed33MiB")
    member.size = 33 * 1024**2
    result = recorded_failure(collector, rebuild(tests.fixture(normal), (member,), True),
                              "listed-payload-over32MiB")
    tests.require(result["expanded_before_refusal"] < 65536, "over-budget payload expanded")
    results.append(result)
    for kind in (tarfile.XHDTYPE, tarfile.XGLTYPE, tarfile.GNUTYPE_LONGNAME,
                 tarfile.SYMTYPE, tarfile.LNKTYPE):
        member = tarfile.TarInfo("unsupported")
        member.type = kind
        results.append(recorded_failure(collector, rebuild(tests.fixture(normal), (member,)),
                                        "unsupported-type-" + kind.decode()))
    base = tests.fixture(normal)
    raw = gzip.decompress(base["archive"])
    changed = bytearray(raw)
    changed[0] ^= 1
    results.append(recorded_failure(collector, set_archive(copy.deepcopy(base), gzip.compress(changed)),
                                    "bad-header-checksum"))
    changed = bytearray(raw)
    changed[512] ^= 1
    results.append(recorded_failure(collector, set_archive(copy.deepcopy(base), gzip.compress(changed)),
                                    "payload-hash-mismatch"))
    changed = bytearray(raw)
    changed[100:108] = b"0000700\0"
    changed[148:156] = b"        "
    changed[148:156] = ("%06o\0 " % sum(changed[:512])).encode("ascii")
    results.append(recorded_failure(collector, set_archive(copy.deepcopy(base), gzip.compress(changed)),
                                    "mode-metadata-mismatch"))
    results.append(recorded_failure(collector, set_archive(copy.deepcopy(base), gzip.compress(raw[:200])),
                                    "truncated-header"))
    results.append(recorded_failure(collector, set_archive(copy.deepcopy(base), base["archive"] +
                                                          gzip.compress(b"")), "concatenated-gzip"))
    case = copy.deepcopy(base)
    case["inside"]["files"]["missing"] = dict(kind="directory", mode=448, uid=0, gid=0, mtime_ns=0)
    results.append(recorded_failure(collector, case, "listed-but-missing-member"))
    return results


def field_and_containment_cases(collector, normal):
    cases = []
    for field, value in (("stage", []), ("error", {}), ("stage", "x" * 129),
                         ("error", "x" * 7900), ("error", "\u2603" * 512)):
        changed = copy.deepcopy(normal)
        changed[field] = value
        result = tests.evaluate(collector, tests.fixture(changed))
        tests.require(len(json.dumps(result).encode("ascii")) <= 8192, "unbounded returned summary")
        if field != "error" or value != "\u2603" * 512:
            tests.require(result["interpretation"] == "UNPROVEN", "malformed field interpreted")
        cases.append(dict(field=field, value_type=type(value).__name__, result=result))
    for value in (b"1e10000", b"-1e10000"):
        raw = json.dumps(normal).encode("ascii")[:-1] + b',"finite_overflow":' + value + b'}'
        result = tests.evaluate(collector, tests.fixture(normal, raw=raw))
        tests.require(result["interpretation"] == "UNPROVEN" and "nonfinite" in result["error"],
                      "finite-token overflow accepted")
        cases.append(dict(finite_token=value.decode(), result=result))
    calls = []
    with patch.object(collector, "mount_diagnostic", side_effect=RuntimeError("injected generation failure")):
        with patch.object(collector, "save", side_effect=lambda path, value: calls.append(str(path))):
            generated = collector.diagnostic_write(Path("/synthetic"), True, dict(exit_code=2, stop=None))
    tests.require(generated["written"] is True and generated["interpretation"] == "UNPROVEN",
                  "generation escape not contained")
    with patch.object(collector, "mount_diagnostic", return_value=collector.diagnostic_summary(None)):
        with patch.object(collector, "save", side_effect=OSError("injected receipt I/O failure")):
            failed_write = collector.diagnostic_write(Path("/synthetic"), True, dict(exit_code=2, stop=None))
    tests.require(failed_write["written"] is False, "diagnostic I/O exception escaped")
    return dict(fields=cases, injected_generation=generated, injected_receipt_IO=failed_write,
                boundary="Helper injection tests and parent AST sequencing; parent/runtime itself not executed")


def historical_compatibility(collector):
    base = tests.ROOT / "records/phase1-direct/completion-20261026/ram-qualification-ipc-probe-v4"
    inside = json.loads((base / "inside-result.json").read_text())
    archive = base / "complete-output.tar.gz"
    tests.require(archive.stat().st_size == 485 and hashlib.sha256(archive.read_bytes()).hexdigest() ==
                  "5b8c8a2dcb245c2dbc474e64e5a0c72fce625d757690b11870b58b3dc164cb61",
                  "historical archive changed")
    streams = collector.diagnostic_scan(base, inside["files"], inside["archive"])
    facts = collector.diagnostic_json(streams["tool.stdout"], 8193)
    tests.require(facts["status"] == "FAILED" and facts["error"] == "private shm mount mismatch",
                  "historical failure reinterpreted")
    return dict(bytes=485, archive_sha256=inside["archive"]["sha256"],
                stdout_sha256=hashlib.sha256(streams["tool.stdout"]).hexdigest(),
                original_failure=facts["error"], status="SCANNER_COMPATIBLE_ONLY_NOT_DIAGNOSTIC_QUALIFICATION",
                scope="Read-only existing raw archive and inventory, not a new mount/IPC run or restore")


def main():
    tests.require(hashlib.sha256(tests.COLLECTOR.read_bytes()).hexdigest() == tests.COLLECTOR_PIN,
                  "collector pin changed")
    collector = tests.load(tests.COLLECTOR, "v6_revision_definitions")
    normal, _, _ = tests.synthetic_reports()
    value = dict(schema="worldline.ipc-diagnostic-composition-r2.regressions.v1",
                 status="TESTED_AUTHOR_REGRESSIONS_ONLY_NOT_INDEPENDENT_REVIEW",
                 collector_sha256=tests.COLLECTOR_PIN,
                 exact_r1_counterexamples=exact_counterexamples(collector, normal),
                 scanner_cases=scanner_cases(collector, normal),
                 fields_containment=field_and_containment_cases(collector, normal),
                 actual_v4_archive_compatibility=historical_compatibility(collector),
                 runtime_entrypoints_executed=False, phase_acceptance=False)
    data = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("ascii")
    tests.require(len(data) <= 131072, "regression receipt cap")
    with (HERE / "revision-tests.json").open("xb") as stream:
        tests.require(stream.write(data) == len(data), "short revision receipt write")
    print(json.dumps(dict(status=value["status"], exact_regressions=4,
                          scanner_cases=len(value["scanner_cases"]), historical_archive="485B_COMPATIBLE"),
                     sort_keys=True))


if __name__ == "__main__":
    main()
