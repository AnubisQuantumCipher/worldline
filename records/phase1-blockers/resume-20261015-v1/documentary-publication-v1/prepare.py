"""Select authored documentary evidence; never recursively enroll generated trees."""
import datetime
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "records/phase1-blockers/resume-20261015-v1"
OUT = Path(__file__).resolve().parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

paths = {ROOT / name for name in (
    "docs/decisions.md", "docs/old-retirement-analysis.md", "docs/phase1-progress.md",
)}
copies = []
for probe in ("finalizable-scalar-v1", "finalizable-heap-v1", "finalizable-heap-v2", "finalizable-fresh-v1"):
    directory = BASE / probe
    paths.update(directory / name for name in ("lifetime.ads", "lifetime.adb", "main.adb", "probe.gpr", "run.py"))
    paths.update(p for p in (directory / "results").iterdir() if p.is_file())
    report = directory / "obj/gnatprove/gnatprove.out"
    if report.exists():
        target = OUT / (probe + "-gnatprove.out")
        data = report.read_bytes()
        with target.open("xb") as stream:
            stream.write(data)
        copies.append({"source": str(report.relative_to(ROOT)), "copy": str(target.relative_to(ROOT)), "sha256": digest(data)})
        paths.add(target)
for stem in ("finalizable-scalar", "finalizable-heap", "finalizable-fresh", "bwrap-guard"):
    versions = ("v1", "v2") if stem == "finalizable-heap" else ("v1",)
    for version in versions:
        for kind in ("parent", "scope"):
            directory = BASE / (stem + "-" + kind + "-" + version)
            paths.update(p for p in directory.iterdir() if p.is_file() and p.name != "storage-preflight.stdout")
for name in ("run_finalizable_scalar.py", "run_finalizable_heap.py", "run_finalizable_heap_v2.py", "run_finalizable_fresh.py", "run_bwrap_guard.py"):
    paths.add(BASE / name)
for directory in (
    BASE / "bwrap-guard-observation-v1",
    ROOT / "scratch/final-gates/resume-20261015-v1/bwrap-guard-diagnostic-v1",
    ROOT / "scratch/final-gates/resume-20261015-v1/profile-none-correction-v1",
):
    paths.update(p for p in directory.iterdir() if p.is_file())
for name in ("research.md", "research.json"):
    paths.add(ROOT / "scratch/final-gates/resume-20261015-v1/toolchain-support-source-research-v1" / name)
review_directory = ROOT / "scratch/reviewer2/resume-20261015-v1"
for pattern in ("D43-*.json", "D44-*.json", "D45-*.json", "D47-*.json", "decisive-check-profile-positional-correction-review-v1.json"):
    paths.update(review_directory.glob(pattern))
paths.add(Path(__file__).resolve())

rows = []
flags = []
secret_patterns = {
    "private-key": rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----",
    "github-token": rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})",
    "openai-token": rb"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}",
    "aws-access": rb"AKIA[0-9A-Z]{16}",
}
for path in sorted(paths):
    if path.is_symlink() or not path.is_file() or not path.is_relative_to(ROOT):
        raise RuntimeError("Nonregular or missing selection: " + str(path))
    data = path.read_bytes()
    relative = str(path.relative_to(ROOT))
    if b"\x00" in data:
        flags.append({"path": relative, "kind": "NUL"})
    if len(data) > 1000000:
        flags.append({"path": relative, "kind": "oversized", "bytes": len(data)})
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        flags.append({"path": relative, "kind": "non-UTF8"})
    for name, pattern in secret_patterns.items():
        if re.search(pattern, data):
            flags.append({"path": relative, "kind": name})
    rows.append({"path": relative, "sha256": digest(data), "bytes": len(data)})
receipt = {
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "scope": "D43-D52 documentary evidence only; no product source, final freeze or acceptance",
    "rows": rows, "plain_report_copies": copies, "audit_flags": flags,
    "excluded": ["generated objects/libraries/binder/vendor bodies", "full host storage catalogues", "user attachments", "upstream raw source bodies"],
    "limitations": ["Finite pattern scan is not a general secret detector", "Internal review does not establish independent acceptance", "Original raw outputs remain local; copies carry source hashes"],
}
with (OUT / "selection.json").open("x") as stream:
    json.dump(receipt, stream, indent=2)
    stream.write("\n")
print(json.dumps({"rows": len(rows), "bytes": sum(row["bytes"] for row in rows), "audit_flags": flags, "selection": str(OUT / "selection.json")}))
if flags:
    raise SystemExit(1)
