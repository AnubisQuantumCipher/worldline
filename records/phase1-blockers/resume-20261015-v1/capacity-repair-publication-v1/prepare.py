import datetime
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "records/phase1-blockers/resume-20261015-v1"
OUT = Path(__file__).resolve().parent
paths = {ROOT / "core/resource_quantities.adb", Path(__file__).resolve()}
copies = []
for version in ("v1", "v2"):
    candidate = BASE / ("decoder-cursor-" + version)
    for directory in (candidate, candidate / "dependencies", candidate / "results"):
        paths.update(p for p in directory.iterdir() if p.is_file())
    for kind in ("parent", "scope"):
        directory = BASE / ("decoder-cursor-" + kind + "-" + version)
        paths.update(p for p in directory.iterdir() if p.is_file() and p.name != "storage-preflight.stdout")
    report = candidate / "obj/gnatprove/gnatprove.out"
    copy = OUT / ("decoder-cursor-" + version + "-gnatprove.out")
    data = report.read_bytes()
    with copy.open("xb") as stream:
        stream.write(data)
    copies.append({"source": str(report.relative_to(ROOT)), "copy": str(copy.relative_to(ROOT)), "sha256": hashlib.sha256(data).hexdigest()})
    paths.add(copy)
for name in ("run_decoder_cursor.py", "run_decoder_cursor_v2.py", "decoder-cursor-live-readback-v1.json"):
    paths.add(BASE / name)
proposal = ROOT / "scratch/final-gates/resume-20261015-v1/capacity-fits-column-lemma-v1"
paths.update(p for p in proposal.iterdir() if p.is_file())
review = ROOT / "scratch/reviewer2/resume-20261015-v1"
for pattern in ("D53-*.json", "D56-*.json"):
    paths.update(review.glob(pattern))

rows, flags = [], []
patterns = {
    "private-key": rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----",
    "github-token": rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})",
    "openai-token": rb"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}",
    "aws-access": rb"AKIA[0-9A-Z]{16}",
}
for path in sorted(paths):
    assert path.is_file() and not path.is_symlink() and path.is_relative_to(ROOT)
    data = path.read_bytes()
    relative = str(path.relative_to(ROOT))
    if b"\0" in data or len(data) > 1000000:
        flags.append({"path": relative, "kind": "NUL/oversize", "bytes": len(data)})
    data.decode("utf-8")
    for name, pattern in patterns.items():
        if re.search(pattern, data):
            flags.append({"path": relative, "kind": name})
    rows.append({"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
receipt = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "scope": "One core call-only proof repair, immutable failed and successful isolated candidate evidence; no complete WORLDLINE/final freeze acceptance",
           "rows": rows, "plain_report_copies": copies, "finite_scan_flags": flags,
           "excluded": ["generated obj/bin/library/binder files", "SPARK library vendor sources", "full host storage catalogue", "unrelated product source and tests"],
           "limitations": ["Finite secret patterns are not general secret detection", "Only core call is applied; candidate cursor and pending patch remain unapplied", "Current full documentary log remains a separate dirty epoch"]}
with (OUT / "selection.json").open("x") as stream:
    json.dump(receipt, stream, indent=2)
    stream.write("\n")
print(json.dumps({"files": len(rows), "bytes": sum(row["bytes"] for row in rows), "finite_scan_flags": flags}))
raise SystemExit(1 if flags else 0)
