"""Reproduce synthetic decoder operands with the original producer codec.

Default mode checks committed bytes. These values confer no custody authority.
"""
import argparse
import hashlib
from pathlib import Path

from worldline.custody_load_kernel import envelope
from worldline.root_worker_codec import archive


def fixtures():
    names = ("events", "heads", "roots", "subjects", "alternatives", "blobs")
    empty = {name: [] for name in names}
    populated = {name: [] for name in names}
    event = [None] * 13
    event[0], event[1] = -257, "ab" * 32
    event[10] = archive({"x5": {"primitive_inputs": {}}})
    event[11] = b"base"
    populated["events"] = [tuple(event)]
    populated["heads"] = [("current", "ORIGIN", None, None, "mac")]
    populated["roots"] = [tuple([None] * 16)]
    populated["subjects"] = [tuple([None] * 9)]
    populated["alternatives"] = [(b"\x01", None, "ROOT", None, b"", "ACK", "00" * 32)]
    populated["blobs"] = [(b"\x00\xff", -257, 1.5)]
    result = {}
    for label, rows in (("empty", empty), ("populated", populated)):
        owner = {"custody_head_messages": [b"message" for _ in rows["heads"]]}
        result[label] = envelope(b"fixture-key", b"genesis-file", b"genesis-row",
                                 "genesis-mac", owner, rows, {})
    cause = {"reason": "synthetic-cause"}
    result["extras"] = archive({
        "x5": {"primitive_inputs": {
            "reattach_epoch": 257, "position": -3, "next_subgeneration": b"\x00\xff",
            "transfer_mode": "abc", "abort_class": None, "unknown_cause": cause},
            "root_evidence": b"root", "native_observations": b"native",
            "subject_evidence_raw": b"subject"},
        "original": {"synthetic": "original"}})
    result["extras_digest"] = hashlib.sha256(archive(cause)).hexdigest().encode("ascii")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    for label, raw in fixtures().items():
        path = root / ("custody_load_" + label + ".json")
        if args.write:
            path.write_bytes(raw)
        elif path.read_bytes() != raw:
            raise ValueError("committed custody fixture differs: " + label)
    print("PASS original producer custody decoder fixtures")


if __name__ == "__main__":
    main()
