"""Formation only: copy exact dependency bytes and hash an unapplied proposal.

Does not import candidate/product modules or execute build/proof/test payloads.
Fails on pre-existing outputs; retained evidence is never overwritten.
"""
import hashlib
import json
import pathlib
import subprocess
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DEPENDENCIES = [
    "core/resource_quantities.ads",
    "core/resource_quantities.adb",
    "core/worldline-archive_text.ads",
    "core/worldline-archive_text.adb",
    "core/worldline.ads",
    "core/attest/attest.ads",
    "core/attest/attest-sha256.ads",
    "core/attest/attest-sha256.adb",
]
REFERENCES = [
    "core/worldline-raw_json.ads",
    "core/worldline-raw_json.adb",
    "core/evaluation_pending.ads",
    "core/worldline-producer_values.ads",
    "core/worldline-producer_values.adb",
    "core/worldline_core_sources.gpr",
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exclusive_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


rows = []
for group, names in (("dependencies", DEPENDENCIES), ("reference-source", REFERENCES)):
    for name in names:
        source = ROOT / name
        data = source.read_bytes()
        target = HERE / group / source.name
        exclusive_bytes(target, data)
        later = source.read_bytes()
        rows.append({
            "original": name,
            "snapshot": str(target.relative_to(HERE)),
            "sha256": sha(data),
            "size_bytes": len(data),
            "source_unchanged_during_copy": data == later,
            "second_read_sha256": sha(later),
        })

head = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
    capture_output=True, text=True,
).stdout.strip()
artifacts = []
for path in sorted(HERE.rglob("*")):
    if path.is_file():
        data = path.read_bytes()
        artifacts.append({
            "path": str(path.relative_to(HERE)),
            "sha256": sha(data), "size_bytes": len(data),
        })

receipt = {
    "schema": "worldline-unapplied-cursor-candidate-v1",
    "formed_utc": datetime.now(timezone.utc).isoformat(),
    "evidence_class": "MEASURED",
    "measurement_scope": "Source bytes, identities and scratch proposal formation only",
    "engineering_status": "UNVERIFIED / UNAPPLIED / NOT COMPILED / NOT PROVED / NOT TESTED",
    "root": str(ROOT),
    "observed_head": head,
    "head_is_freeze": False,
    "exact_command": "python3 -B scratch/acquisition2/resume-20261015-v1/decoder-cursor-candidate-v1/prepare_receipt.py",
    "command_workdir": str(ROOT),
    "source_snapshots": rows,
    "artifacts": artifacts,
    "all_snapshot_source_reads_stable": all(row["source_unchanged_during_copy"] for row in rows),
    "mutations": "New files only within the assigned fresh scratch candidate directory",
    "payloads_executed": [],
    "non_claims": [
        "No compilation, proof, test, product import, reproducer, runtime or heavy job executed",
        "No production file modified",
        "No runtime measurement of decoder memory or time",
        "No scalar semantic correspondence proof result",
        "No full JSON grammar, full-value equivalence or whole-path integration claim",
        "No valid enormous-input execution inferred from endpoint-index fixtures",
        "No timeout classification or acceptance gate closed",
    ],
}
payload = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
exclusive_bytes(HERE / "preparation-receipt.json", payload)
print(json.dumps({
    "evidence_class": receipt["evidence_class"],
    "engineering_status": receipt["engineering_status"],
    "observed_head": head,
    "receipt_sha256": sha(payload),
    "all_snapshot_source_reads_stable": receipt["all_snapshot_source_reads_stable"],
    "payloads_executed": [],
}, indent=2))
