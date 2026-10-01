#!/usr/bin/env python3
"""The proof-manifest gate: may this tree be built, installed or released as proved?

    verify_proof_manifest.py [--sources-only] [--require-summary [PATH]] [--print-contract-pins]

From 1.9.2 the checks themselves live in runtime/worldline/proof_manifest.py, which the runtime
imports too (proof.ProofStatus), so the gate that admits a build and the receipt that states
`invariantPreservation` cannot disagree (OB-084). This file is the command line around them and
re-exports the pinned tables under their old names.

--require-summary re-reads the GNATprove summary (default obj/core-library/gnatprove/
gnatprove.out), refuses any line it does not recognize, and requires its digest and the counts
and coverage re-derived from it to equal the manifest's (OB-085). prove.sh always passes it;
install.sh passes it whenever the proof ran.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT / "runtime"))

from worldline.proof_manifest import (  # noqa: E402
    CONTRACT_PINS,
    MINIMUM_CHECKS,
    REQUIRED_PROVED,
    UNANALYZED_BOUNDARY,
    SummaryError,
    contract_pin,
    contract_problems,
    contract_text,
    digest,
    expected_units,
    export_problems,
    manifest_problems,
    normalized_ada,
    parse_summary,
    proof_source_files,
    source_paths,
    stray_sources,
    summary_problems,
)

__all__ = [
    "CONTRACT_PINS", "MINIMUM_CHECKS", "REQUIRED_PROVED", "UNANALYZED_BOUNDARY", "SummaryError", "contract_pin",
    "contract_problems", "contract_text", "digest", "expected_units", "export_problems", "manifest_problems",
    "normalized_ada", "parse_summary", "proof_source_files", "source_paths", "stray_sources", "summary_problems",
]

DEFAULT_SUMMARY = "obj/core-library/gnatprove/gnatprove.out"


def main() -> int:
    root = Path(__file__).resolve().parent
    arguments = sys.argv[1:]
    if "--print-contract-pins" in arguments:
        if arguments != ["--print-contract-pins"]:
            print("--print-contract-pins is an inspection mode and cannot be combined with verification options", file=sys.stderr)
            return 2
        for key in CONTRACT_PINS:
            print(f'    "{key}": "{contract_pin(root, key)}",')
        return 0
    known = {"--sources-only", "--require-summary"}
    summary_path: Path | None = None
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument == "--require-summary":
            following = arguments[index + 1] if index + 1 < len(arguments) else None
            if following is not None and not following.startswith("--"):
                summary_path = Path(following)
                index += 1
            else:
                summary_path = root / DEFAULT_SUMMARY
        elif argument not in known:
            # An option this gate does not know must not be ignored: a caller who meant to ask
            # for a stronger check would otherwise get a weaker one and exit 0 (1.9.2).
            print(f"unknown option: {argument}", file=sys.stderr)
            return 2
        index += 1
    problems = contract_problems(root)
    if problems:
        print("; ".join(problems), file=sys.stderr)
        return 1
    manifest_path = root / "proof-manifest.json"
    if not manifest_path.is_file():
        print("proof manifest missing", file=sys.stderr)
        return 1
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        print(f"invalid proof manifest: {exc}", file=sys.stderr)
        return 1
    summary: bytes | None = None
    if summary_path is not None:
        try:
            summary = summary_path.read_bytes()
        except OSError as exc:
            print(f"the proof summary cannot be read: {summary_path}: {exc}", file=sys.stderr)
            return 1
    sources_only = "--sources-only" in arguments
    # A source release carries no built library; the manifest still records the hash of the
    # library the proof ran against, for anyone who builds and compares.
    library = None
    if not sources_only:
        record = manifest.get("library") if isinstance(manifest, dict) else None
        if not isinstance(record, dict) or record.get("path") != "lib/libworldline_core.so":
            print("invalid proof manifest: expected library path lib/libworldline_core.so", file=sys.stderr)
            return 1
        library = root / "lib/libworldline_core.so"
    try:
        problems = manifest_problems(manifest, root, library=library, summary=summary, require_summary=summary_path is not None)
    except (OSError, UnicodeError) as exc:
        print(f"proof evidence could not be read: {exc}", file=sys.stderr)
        return 1
    if problems:
        print(problems[0] if len(problems) == 1 else "; ".join(problems), file=sys.stderr)
        return 1
    if sources_only:
        print("proof manifest verified (sources; library not checked)")
    else:
        print("proof manifest verified" + (" (summary re-derived)" if summary is not None else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
