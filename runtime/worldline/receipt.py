from __future__ import annotations

import fnmatch
from typing import Any, Sequence

from . import SCHEMA_VERSION
from .canonical import canonical_bytes
from .core import Core
from .proof import ProofStatus
from .store import StateStore


class ReceiptBuilder:
    def __init__(self, store: StateStore, core: Core | None = None) -> None:
        self.store = store
        self.core = core or Core.shared()

    def build(
        self,
        *,
        transaction_id: str,
        parent_world: str,
        candidate_world: str,
        before_root: str,
        after_root: str,
        delta: dict[str, Any],
        contamination: Sequence[dict[str, Any]],
        generated: Sequence[dict[str, str]] = (),
        dependency_changes: Sequence[dict[str, Any]] = (),
    ) -> dict[str, Any]:
        previous = self.store.last_receipt()
        previous_id = None if previous is None else previous["receipt_id"]
        files = [
            {
                "rootKey": operation["rootKey"],
                "pathB64": operation["pathB64"],
                "path": operation["pathDisplay"],
                "op": operation["op"],
            }
            for operation in delta["operations"]
        ]
        generated_files = [
            item
            for item in files
            if any(
                classifier.get("root") == item["rootKey"]
                and fnmatch.fnmatchcase(item["path"], classifier.get("glob", ""))
                for classifier in generated
            )
        ]
        proof = ProofStatus.inspect(self.core)
        receipt: dict[str, Any] = {
            "schemaVersion": SCHEMA_VERSION,
            "receiptId": "",
            "previousReceipt": previous_id,
            "parentWorld": parent_world,
            "candidateWorld": candidate_world,
            "baseState": {"state": "VERIFIED", "root": delta.get("baseRoot")},
            "candidateDelta": {
                "hash": delta["deltaHash"],
                "summary": delta["summary"],
            },
            "foreignWorldContamination": {
                "state": "NONE" if not contamination else "DETECTED",
                "writes": list(contamination),
            },
            "mergeSet": {
                "files": files,
                "generatedArtifacts": generated_files,
                "dependencyChanges": list(dependency_changes),
                "unrelatedConfigurationMutations": [
                    item for item in contamination if item.get("scope") == "outside-registered-roots"
                ],
            },
            "invariantPreservation": proof,
            "atomicCollapse": {
                "state": "COMMITTED",
                "mechanism": "renameat2(RENAME_EXCHANGE)",
            },
            "beforeRoot": before_root,
            "afterRoot": after_root,
            "transactionId": transaction_id,
            "nonClaims": [
                "OS syscalls and filesystem behavior are outside the SPARK proof.",
                "Uncooperative external writers and open file descriptors are outside the SPARK proof.",
                "SHA-256 collision resistance is outside the SPARK proof.",
            ],
        }
        preimage = dict(receipt)
        preimage.pop("receiptId")
        receipt["receiptId"] = "WL:" + self.core.hash_bytes(
            b"worldline-receipt-id-v1" + canonical_bytes(preimage)
        ).hex()
        return receipt

    def append(self, **values: Any) -> dict[str, Any]:
        receipt = self.build(**values)
        linked = self.store.append_receipt(receipt)
        return {**receipt, **linked}
