"""Verify nonempty exact-target proof rows; never infer scope from cached totals."""
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1])
names = {"append-sql": "Append_SQL_Cell", "counts": "Counts",
         "event-extras": "Append_Event_Extras", "decode-wrapper": "Decode",
         "grown-wrapper": "Decode_Grown", "extra": "Append_Event_Extras.Extra",
         "materialize-image": "Append_Event_Extras.Materialize_Image",
         "initialize": "Initialize_Input", "decode-into": "Decode_Into"}
results = json.loads((root / "result.json").read_text())
assert 0 < len(results) <= len(names)
verified = []
for item in results:
    assert item["exit_code"] == 0 and item["fresh_summary"]
    symbol = "Worldline.Custody_V2_Load_Input." + names[item["name"]] + " at "
    lines = (root / (item["name"] + ".gnatprove.out")).read_text().splitlines()
    rows = [row.strip() for row in lines if symbol in row and
            re.search(r"proved \([1-9][0-9]* checks\)", row)]
    assert len(rows) == 1, (symbol, rows)
    assert "0 errors, 0 checks, 0 warnings and 0 pragma Assume" in rows[0]
    diagnostics = (root / (item["name"] + ".stderr")).read_text()
    assert not re.search(r"(?:medium|high|warning|error):", diagnostics)
    verified.append({"name": item["name"], "target_row": rows[0]})
(root / "target-verification.json").write_text(json.dumps(verified, indent=2) + "\n")
print(json.dumps(verified, indent=2))
