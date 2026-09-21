"""Receipt anchoring: an append-only, Ed25519-signed ledger of every committed receipt.

The receipt chain inside the SQLite store is self-consistent, and that is all it is: a process
running as the operator can rewrite the store and the chain still verifies (SECURITY.md,
audit 2026-09-02). Anchoring adds two things the store cannot give itself:

* every receipt is signed with a key the daemon holds, in a ledger written in the Custos/ATTEST
  format, so ``attest verify-custos LEDGER PUBKEY`` replays the whole chain and every signature
  with the SPARK-proved SHA-256 and Ed25519 in ~/Projects/attest, using none of this code;
* the ledger and public key can be exported to a place the store's writer does not control
  (``anchor.exportPath``: a synced folder, a git checkout, another machine). ``verify`` compares
  the local head with the exported one, so a local rollback or rewrite shows up as a mismatch.

What this does not do: protect against an attacker who also holds the signing key (it lives
beside the store, 0600) and can reach the export location. It moves the bar from "rewrite one
SQLite file" to "rewrite the file, re-sign every entry, and rewrite the external copy too".
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from .canonical import atomic_write
from .errors import WorldlineError
from .paths import WorldlinePaths, secure_directory

GENESIS = hashlib.sha256(b"custos-genesis-v1").hexdigest()
_FIELDS = 9


class AnchorLedger:
    def __init__(self, paths: WorldlinePaths, export_path: Path | None = None) -> None:
        self.paths = paths
        self.directory = paths.config / "anchor"
        self.secret_path = self.directory / "secret.key"
        self.public_path = self.directory / "public.hex"
        self.ledger_path = paths.state / "anchor.tsv"
        self.export_path = export_path

    # ----- keys -----------------------------------------------------------------------------

    def ensure_keys(self) -> str:
        secure_directory(self.directory)
        if not self.secret_path.is_file():
            key = ed25519.Ed25519PrivateKey.generate()
            raw = key.private_bytes(
                serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()
            )
            descriptor = os.open(self.secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="ascii") as handle:
                handle.write(raw.hex() + "\n")
            atomic_write(self.public_path, (key.public_key().public_bytes_raw().hex() + "\n").encode("ascii"))
        return self.public_key_hex()

    def _private_key(self) -> ed25519.Ed25519PrivateKey:
        info = self.secret_path.lstat()
        if info.st_uid != os.getuid() or (info.st_mode & 0o077):
            raise WorldlineError("UNSAFE_ANCHOR_KEY", f"anchor signing key is not owner-only: {self.secret_path}")
        return ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(self.secret_path.read_text("ascii").strip()))

    def public_key_hex(self) -> str:
        return self.public_path.read_text("ascii").strip()

    # ----- ledger ---------------------------------------------------------------------------

    def entries(self) -> list[str]:
        if not self.ledger_path.is_file():
            return []
        return [line for line in self.ledger_path.read_text("utf-8").split("\n") if line]

    def head(self) -> str:
        lines = self.entries()
        return GENESIS if not lines else hashlib.sha256(lines[-1].encode("utf-8")).hexdigest()

    def anchored_receipts(self) -> set[str]:
        return {line.split("\t")[3] for line in self.entries() if line.count("\t") == _FIELDS - 1}

    def append(self, *, action: str, receipt_id: str, canonical: bytes) -> dict[str, Any]:
        """Append one signed entry for a receipt. Fields follow the Custos ledger exactly."""
        self.ensure_keys()
        lines = self.entries()
        seq = len(lines)
        prev = self.head()
        fields = [
            str(seq),
            str(int(time.time())),
            action,
            receipt_id,
            "-",
            hashlib.sha256(canonical).hexdigest(),
            str(len(canonical)),
            prev,
        ]
        for value in fields:
            if "\t" in value or "\n" in value:
                raise WorldlineError("ANCHOR_FIELD_INVALID", "anchor fields may not contain tabs or newlines")
        message = ("custos-v1\t" + "\t".join(fields)).encode("utf-8")
        signature = self._private_key().sign(message).hex()
        line = "\t".join([*fields, signature])
        secure_directory(self.ledger_path.parent)
        descriptor = os.open(self.ledger_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        exported = self.export()
        return {"seq": seq, "head": hashlib.sha256(line.encode("utf-8")).hexdigest(), "export": exported}

    def export(self) -> dict[str, Any]:
        if self.export_path is None:
            return {"state": "UNCONFIGURED"}
        try:
            self.export_path.mkdir(parents=True, exist_ok=True)
            if self.ledger_path.is_file():
                atomic_write(self.export_path / "anchor.tsv", self.ledger_path.read_bytes())
            if self.public_path.is_file():
                atomic_write(self.export_path / "public.hex", self.public_path.read_bytes())
        except OSError as exc:
            return {"state": "FAILED", "reason": str(exc), "path": str(self.export_path)}
        return {"state": "EXPORTED", "path": str(self.export_path)}

    # ----- verification ---------------------------------------------------------------------

    def verify(self, *, receipts_known: int | None = None) -> dict[str, Any]:
        lines = self.entries()
        result: dict[str, Any] = {
            "state": "EMPTY" if not lines else "OK",
            "entries": len(lines),
            "head": self.head(),
            "ledger": str(self.ledger_path),
            "publicKey": self.public_key_hex() if self.public_path.is_file() else None,
            "badChain": 0,
            "badSignature": 0,
        }
        if lines and result["publicKey"] is None:
            result["state"] = "BROKEN"
            result["reason"] = "ledger has entries but no public key"
        elif lines:
            public = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(result["publicKey"]))
            expected_prev = GENESIS
            for index, line in enumerate(lines):
                fields = line.split("\t")
                if len(fields) != _FIELDS or fields[0] != str(index) or fields[7] != expected_prev:
                    result["badChain"] += 1
                else:
                    message = ("custos-v1\t" + "\t".join(fields[:8])).encode("utf-8")
                    try:
                        public.verify(bytes.fromhex(fields[8]), message)
                    except Exception:  # noqa: BLE001 - any failure is a bad signature
                        result["badSignature"] += 1
                expected_prev = hashlib.sha256(line.encode("utf-8")).hexdigest()
            if result["badChain"] or result["badSignature"]:
                result["state"] = "BROKEN"
        if receipts_known is not None:
            result["receipts"] = receipts_known
            result["unanchoredReceipts"] = max(0, receipts_known - len(self.anchored_receipts()))
        result["attest"] = self._attest_verify()
        result["external"] = self._external_check()
        return result

    def _attest_verify(self) -> dict[str, Any]:
        executable = shutil.which("attest")
        if executable is None:
            return {"state": "UNAVAILABLE", "reason": "attest is not installed"}
        if not self.ledger_path.is_file() or not self.public_path.is_file():
            return {"state": "UNAVAILABLE", "reason": "no ledger yet"}
        try:
            completed = subprocess.run(
                [executable, "verify-custos", str(self.ledger_path), str(self.public_path), "--quiet"],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"state": "UNAVAILABLE", "reason": str(exc)}
        verdict = completed.stdout.decode("utf-8", "replace").strip().splitlines()
        return {
            "state": "VERIFIED" if completed.returncode == 0 else "FAILED",
            "exitCode": completed.returncode,
            "verdict": verdict[-1] if verdict else "",
            "tool": executable,
        }

    def _external_check(self) -> dict[str, Any]:
        if self.export_path is None:
            return {"state": "UNCONFIGURED"}
        external = self.export_path / "anchor.tsv"
        if not external.is_file():
            return {"state": "UNAVAILABLE", "path": str(external)}
        try:
            remote = [line for line in external.read_text("utf-8").split("\n") if line]
        except OSError as exc:
            return {"state": "UNAVAILABLE", "path": str(external), "reason": str(exc)}
        local = self.entries()
        if remote == local:
            return {"state": "MATCH", "entries": len(remote), "path": str(external)}
        if len(local) < len(remote) and remote[: len(local)] == local:
            return {"state": "ROLLED_BACK", "localEntries": len(local), "externalEntries": len(remote), "path": str(external)}
        if len(local) > len(remote) and local[: len(remote)] == remote:
            return {"state": "EXPORT_BEHIND", "localEntries": len(local), "externalEntries": len(remote), "path": str(external)}
        return {"state": "MISMATCH", "localEntries": len(local), "externalEntries": len(remote), "path": str(external)}

    def backfill(self, receipts: list[dict[str, Any]]) -> int:
        """Anchor receipts that predate the ledger, in chain order. Returns how many were added."""
        already = self.anchored_receipts()
        added = 0
        for row in receipts:
            receipt = row.get("receipt")
            receipt_id = (receipt or {}).get("receiptId") if isinstance(receipt, dict) else None
            canonical_path = row.get("canonical_path")
            if not receipt_id or receipt_id in already or not canonical_path:
                continue
            try:
                canonical = Path(canonical_path).read_bytes()
            except OSError:
                continue
            self.append(action="backfill", receipt_id=receipt_id, canonical=canonical)
            already.add(receipt_id)
            added += 1
        return added
