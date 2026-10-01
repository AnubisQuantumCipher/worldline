"""The anchor: an append-only, Ed25519-signed ledger of every receipt and causal event.

The receipt and causal chains inside the SQLite store are self-consistent, and that is all
they are: a process running as the operator can rewrite the store and both chains still verify
(SECURITY.md, audit 2026-09-02). The anchor adds what the store cannot give itself:

* every committed receipt and (from 1.9.2) every causal event is signed with a key the daemon
  holds, in ledgers written in the Custos/ATTEST format, so ``attest verify-custos LEDGER
  PUBKEY`` replays each key epoch and every signature with the SPARK-proved SHA-256 and Ed25519
  in ~/Projects/attest, using none of this code;
* (1.9.2) a WITNESS: the whole transcript is appended, never rewritten, to
  ``anchor.exportPath/anchor.tsv``, a file the daemon account can append to but not truncate
  (the append-only attribute), or cannot write at all (another account owns it and appends).
  Before anything is exported the witness is compared with the local ledger, so a local
  rollback or rewrite is detected and the witness is left as it was;
* (1.9.2) a PIN: the sequence of public keys, one per key epoch, in a file the daemon account
  cannot write (``anchor.pinPath``, default ``exportPath/anchor.pin``). A regenerated or
  replaced key is refused, and verification uses the pinned keys, never ``public.hex``;
* (1.9.2) key ROTATION: an offline ``worldline anchor rotate`` closes the current epoch with an
  entry naming the new public key, signed by the old key, and opens a new epoch file whose first
  entry, signed by the new key, names the old epoch's head. When the old key is lost, the owner
  records the retirement in the pin instead.

Whether the witness and the pin are out of the daemon account's reach is MEASURED at each check
(the file's append-only or immutable attribute, or foreign ownership of the file and every
directory above it), never taken from configuration.

What this does not do: stop a process that holds the current signing key (it lives beside the
store, 0600) from appending NEW forged entries. Witnessed history cannot be rewritten; new
history can be forged until the signer is separated from the daemon account (OB-086, K7).
"""
from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import tempfile
import threading
import time
from typing import Any, Callable, Iterable, Mapping, Sequence

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from .canonical import atomic_write
from .errors import WorldlineError
from .paths import WorldlinePaths, secure_directory

GENESIS = hashlib.sha256(b"custos-genesis-v1").hexdigest()
_FIELDS = 9
PIN_SCHEMA = "worldline-anchor-pin-v1"

# Entry actions. Receipts: "collapse" and "return" as committed, "backfill" for receipts that
# predate the anchor. Causal events (1.9.2): "causal" at append, "causal-backfill" for events
# that predate it. Key epochs (1.9.2): a rotation entry closes an epoch, "rotated-from" opens one.
RECEIPT_ACTIONS = frozenset({"collapse", "return", "backfill"})
CAUSAL_ACTIONS = frozenset({"causal", "causal-backfill"})
ROTATION_ACTIONS = frozenset({"rotate", "retire-compromised"})
EPOCH_START = "rotated-from"

# Overall verdict states, most severe first. OK only when none applies.
SEVERITY = (
    "BROKEN", "ATTEST_FAILED", "KEY_MISMATCH", "MISMATCH", "ROLLED_BACK", "RECEIPT_CHAIN_TRUNCATED",
    "CAUSAL_CHAIN_TRUNCATED", "COVERAGE_MISMATCH", "CANONICAL_PATH_OUTSIDE_STORE", "KEY_UNPINNED",
    "WITNESS_UNPROTECTED", "WITNESS_UNCONFIGURED", "EXPORT_BEHIND", "UNANCHORED",
)

# Linux FS_IOC_GETFLAGS (_IOR('f', 1, long)) and the two attributes the daemon's uid cannot clear
# without CAP_LINUX_IMMUTABLE.
FS_IOC_GETFLAGS = 0x80086601 if struct.calcsize("l") == 8 else 0x80046601
FS_IMMUTABLE_FL = 0x00000010
FS_APPEND_FL = 0x00000020
_ACL_NAMES = ("system.posix_acl_access", "system.posix_acl_default")

# A test build's seam, honoured only by a runtime running from a source checkout: subprocess
# daemons in the test suite cannot create root-owned or append-only files. An installed runtime
# ignores it (core.runtime_installed), and every report names the method as an assumption.
TEST_PROTECTION_ENV = "WORLDLINE_TEST_ASSUME_ANCHOR_PROTECTION"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def line_head(line: str) -> str:
    return _sha(line.encode("utf-8"))


def _read_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [line for line in path.read_text("utf-8").split("\n") if line]


# ----- protection measurement ------------------------------------------------------------------

def _file_flags(path: Path) -> int | None:
    """The inode attribute flags (chattr), or None where the filesystem cannot report them."""
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    except OSError:
        return None
    try:
        buffer = bytearray(8)
        fcntl.ioctl(descriptor, FS_IOC_GETFLAGS, buffer, True)
        return struct.unpack_from("=I", buffer)[0]
    except OSError:
        return None
    finally:
        os.close(descriptor)


def _entry_facts(path: Path) -> dict[str, Any]:
    """Ownership, mode and ACL of one path, read without following a link."""
    info = os.lstat(path)
    try:
        names = os.listxattr(path, follow_symlinks=False)
    except OSError as exc:
        if exc.errno not in (errno.ENOTSUP, errno.EOPNOTSUPP):
            raise
        names = []
    return {"uid": info.st_uid, "gid": info.st_gid, "mode": info.st_mode,
            "acl": any(name in _ACL_NAMES or (name.startswith("system.") and "acl" in name) for name in names)}


def _test_protection_assumed() -> bool:
    if os.environ.get(TEST_PROTECTION_ENV) != "1":
        return False
    from .core import runtime_installed
    return not runtime_installed()


def measure_protection(path: Path, *, purpose: str) -> dict[str, Any]:
    """Whether the daemon's account can rewrite `path` (1.9.2). MEASURED here, at each check.

    A witness is protected when it carries the append-only attribute (the daemon may append but
    not truncate, rewrite, unlink or rename over it) or the immutable one; a pin when it carries
    the immutable attribute. Either is also protected when the file and every directory above it
    are owned by another uid and grant this uid no write permission, with no ACL (the "pull"
    model: another account writes it). Anything else, a file that cannot report its attributes
    included, is unprotected."""
    report: dict[str, Any] = {"path": str(path), "purpose": purpose}
    if _test_protection_assumed():
        return {**report, "state": "PROTECTED", "method": "assumed-by-test-runtime"}
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return {**report, "state": "MISSING", "reason": "the file does not exist"}
    except OSError as exc:
        return {**report, "state": "UNKNOWN", "reason": str(exc)}
    if not stat.S_ISREG(info.st_mode):
        return {**report, "state": "UNPROTECTED", "reason": "not a regular file (a link or special file is never a witness)"}
    flags = _file_flags(path)
    wanted = FS_APPEND_FL | FS_IMMUTABLE_FL if purpose == "witness" else FS_IMMUTABLE_FL
    if flags is not None and flags & wanted:
        method = "append-only-attribute" if flags & FS_APPEND_FL and purpose == "witness" else "immutable-attribute"
        return {**report, "state": "PROTECTED", "method": method, "flags": flags}
    uid = os.getuid()
    groups = {os.getgid(), *os.getgroups()}
    # The directories as they really are: a linked ancestor's own owner says nothing about the
    # directory it leads to. The file itself was checked above not to be a link.
    current = Path(os.path.realpath(path.parent)) / path.name
    chain = [current, *current.parents]
    for entry in chain:
        try:
            facts = _entry_facts(entry)
        except OSError as exc:
            return {**report, "state": "UNPROTECTED", "reason": f"cannot read {entry}: {exc}", "flags": flags}
        mode = facts["mode"]
        if facts["uid"] == uid:
            return {**report, "state": "UNPROTECTED", "flags": flags,
                    "reason": f"{entry} is owned by this account and carries no {'append-only' if purpose == 'witness' else 'immutable'} attribute"}
        if mode & stat.S_IWOTH or (mode & stat.S_IWGRP and facts["gid"] in groups):
            return {**report, "state": "UNPROTECTED", "flags": flags, "reason": f"{entry} is writable by this account"}
        if facts["acl"]:
            return {**report, "state": "UNPROTECTED", "flags": flags, "reason": f"{entry} carries an ACL this check does not evaluate"}
    return {**report, "state": "PROTECTED", "method": "foreign-owner", "flags": flags}


# ----- ledger lines ------------------------------------------------------------------------------

def _message(fields: Sequence[str]) -> bytes:
    return ("custos-v1\t" + "\t".join(fields[:8])).encode("utf-8")


def _signed_line(key: ed25519.Ed25519PrivateKey, fields: list[str]) -> str:
    for value in fields:
        if "\t" in value or "\n" in value:
            raise WorldlineError("ANCHOR_FIELD_INVALID", "anchor fields may not contain tabs or newlines")
    return "\t".join([*fields, key.sign(_message(fields)).hex()])


def _public_hex(key: ed25519.Ed25519PrivateKey) -> str:
    return key.public_key().public_bytes_raw().hex()


def _valid_public_hex(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(value))
    except ValueError:
        return False
    return True


def rotation_key(fields: Sequence[str]) -> str | None:
    """The public key a rotation entry names, or None when the entry is not one."""
    if len(fields) != _FIELDS or fields[2] not in ROTATION_ACTIONS or not fields[3].startswith("key:"):
        return None
    return fields[3].removeprefix("key:")


class AnchorLedger:
    def __init__(self, paths: WorldlinePaths, export_path: Path | None = None, *,
                 pin_path: Path | None = None, alarm: Callable[[], Any] | None = None) -> None:
        self.paths = paths
        self.directory = paths.config / "anchor"
        self.secret_path = self.directory / "secret.key"
        self.public_path = self.directory / "public.hex"
        self.ledger_path = paths.state / "anchor.tsv"
        self.export_path = export_path
        # The pin lives beside the witness unless configured elsewhere; either way its
        # protection is measured, not assumed.
        self.pin_path = pin_path if pin_path is not None else (None if export_path is None else export_path / "anchor.pin")
        # The standing alarm a start raised (store meta), consulted by the promotion guard.
        self.alarm = alarm or (lambda: None)
        # One writer at a time: seq and prev are read, then the line is appended. Commit,
        # recovery and agent event ingestion (worker threads) all append (review note A13).
        self._lock = threading.RLock()

    # ----- files ------------------------------------------------------------------------------

    def epoch_path(self, epoch: int) -> Path:
        return self.ledger_path if epoch == 0 else self.paths.state / f"anchor.{epoch}.tsv"

    def epoch_count(self) -> int:
        count = 1
        while self.epoch_path(count).is_file():
            count += 1
        return count

    def epochs(self) -> list[list[str]]:
        return [_read_lines(self.epoch_path(epoch)) for epoch in range(self.epoch_count())]

    def entries(self) -> list[str]:
        """The whole transcript: every epoch's lines in order (what the witness holds)."""
        return [line for lines in self.epochs() for line in lines]

    def head(self) -> str:
        lines = self.entries()
        return GENESIS if not lines else line_head(lines[-1])

    @property
    def witness_path(self) -> Path | None:
        return None if self.export_path is None else self.export_path / "anchor.tsv"

    def anchored(self) -> dict[str, dict[str, list[str]]]:
        """Anchored identities and the content hashes signed for them, by kind."""
        result: dict[str, dict[str, list[str]]] = {"receipts": {}, "events": {}}
        for line in self.entries():
            fields = line.split("\t")
            if len(fields) != _FIELDS:
                continue
            kind = "receipts" if fields[2] in RECEIPT_ACTIONS else "events" if fields[2] in CAUSAL_ACTIONS else None
            if kind is not None:
                result[kind].setdefault(fields[3], []).append(fields[5])
        return result

    def anchored_receipts(self) -> set[str]:
        return set(self.anchored()["receipts"])

    # ----- keys -------------------------------------------------------------------------------

    def ensure_keys(self) -> str:
        """The current public key. A key is minted only at first initialization: when there is
        no key, no pin and no ledger entry. Otherwise a missing key is refused (1.9.2, OB-089):
        a silently regenerated key re-signs everything and reads as intact."""
        secure_directory(self.directory)
        if not self.secret_path.is_file():
            pinned = self.pin_path is not None and os.path.lexists(self.pin_path)
            if pinned or any(self.epochs()):
                raise WorldlineError(
                    "ANCHOR_KEY_MISSING",
                    "the anchor signing key is missing and the ledger or a pin already names one; a new key is "
                    "never minted over existing history (restore the key, or record the old key's retirement "
                    "with `worldline anchor rotate --old-key-unavailable` while the daemon is stopped)",
                    {"secret": str(self.secret_path), "pin": None if self.pin_path is None else str(self.pin_path)})
            key = ed25519.Ed25519PrivateKey.generate()
            raw = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
            descriptor = os.open(self.secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="ascii") as handle:
                handle.write(raw.hex() + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        public = _public_hex(self._private_key())
        if not self.public_path.is_file() or self.public_path.read_text("ascii").strip() != public:
            atomic_write(self.public_path, (public + "\n").encode("ascii"))
        return public

    def _private_key(self, path: Path | None = None) -> ed25519.Ed25519PrivateKey:
        path = path or self.secret_path
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or (info.st_mode & 0o077):
            raise WorldlineError("UNSAFE_ANCHOR_KEY", f"anchor signing key is not owner-only: {path}")
        return ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(path.read_text("ascii").strip()))

    def public_key_hex(self) -> str:
        return self.public_path.read_text("ascii").strip()

    def current_public(self) -> str | None:
        """The public half of the key the daemon signs with now (derived from the secret, never
        read from public.hex), or None without a usable key."""
        try:
            return _public_hex(self._private_key())
        except (OSError, ValueError, WorldlineError):
            return None

    # ----- pin --------------------------------------------------------------------------------

    def read_pin(self) -> dict[str, Any]:
        if self.pin_path is None:
            return {"state": "UNCONFIGURED", "path": None}
        report: dict[str, Any] = {"path": str(self.pin_path)}
        try:
            info = os.lstat(self.pin_path)
        except FileNotFoundError:
            return {**report, "state": "ABSENT"}
        except OSError as exc:
            return {**report, "state": "UNREADABLE", "reason": str(exc)}
        if not stat.S_ISREG(info.st_mode):
            return {**report, "state": "INVALID", "reason": "the pin is not a regular file"}
        try:
            descriptor = os.open(self.pin_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
            with os.fdopen(descriptor, "rb") as handle:
                value = json.loads(handle.read(65536).decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return {**report, "state": "INVALID", "reason": f"unreadable pin: {exc}"}
        keys = value.get("keys") if isinstance(value, dict) else None
        if not isinstance(value, dict) or value.get("schema") != PIN_SCHEMA or not isinstance(keys, list) or not keys:
            return {**report, "state": "INVALID", "reason": f"the pin is not a {PIN_SCHEMA} document with keys"}
        parsed: list[dict[str, Any]] = []
        for index, item in enumerate(keys):
            if not isinstance(item, dict) or not _valid_public_hex(item.get("publicKey")) or set(item) - {"publicKey", "retires"}:
                return {**report, "state": "INVALID", "reason": f"pin key {index} is malformed"}
            retires = item.get("retires")
            if retires is not None and (index == 0 or not isinstance(retires, dict) or set(retires) != {"entries"}
                                        or type(retires["entries"]) is not int or retires["entries"] < 0):
                return {**report, "state": "INVALID", "reason": f"pin key {index} has a malformed retirement record"}
            parsed.append({"publicKey": item["publicKey"], **({"retires": dict(retires)} if retires is not None else {})})
        return {**report, "state": "PRESENT", "keys": parsed}

    def pin_document(self, *, retires: Mapping[int, int] | None = None) -> dict[str, Any]:
        """The pin the operator should install for the current key sequence (1.9.2). Only the
        operator's own copy, written where this account cannot write, protects anything."""
        sequence = self.key_sequence(pin_keys=None)
        keys: list[dict[str, Any]] = []
        existing = self.read_pin()
        existing_keys = existing.get("keys") or []
        for epoch, public in enumerate(sequence["keys"]):
            if public is None and epoch == len(sequence["keys"]) - 1:
                public = sequence["current"]  # an owner-recorded retirement: the new key is the one in use
            item: dict[str, Any] = {"publicKey": public}
            recorded = (retires or {}).get(epoch)
            if recorded is None and epoch < len(existing_keys) and existing_keys[epoch].get("publicKey") == public:
                recorded = (existing_keys[epoch].get("retires") or {}).get("entries")
            if recorded is not None:
                item["retires"] = {"entries": int(recorded)}
            keys.append(item)
        return {"schema": PIN_SCHEMA, "keys": keys}

    # ----- key epochs -------------------------------------------------------------------------

    def key_sequence(self, *, pin_keys: list[dict[str, Any]] | None) -> dict[str, Any]:
        """The public key of each epoch, as the ledger and the pin establish it, WITHOUT checking
        signatures (verify() does). Epoch 0's key is the pin's first key; with no pin it is the
        current key (self-attested, reported KEY_UNPINNED). Each later epoch's key is the key the
        closing rotation entry of the epoch before names, or, for an owner-recorded retirement,
        the pin's key for that epoch."""
        epochs = self.epochs()
        current = self.current_public() or (self.public_key_hex() if self.public_path.is_file() else None)
        keys: list[str | None] = []
        problems: list[str] = []
        for epoch in range(len(epochs)):
            if epoch == 0:
                keys.append(pin_keys[0]["publicKey"] if pin_keys else (current if len(epochs) == 1 else None))
                if keys[0] is None and epochs[0]:
                    problems.append("epoch 0 has no established key (no pin, and no usable signing key)")
                continue
            previous = epochs[epoch - 1]
            named = rotation_key(previous[-1].split("\t")) if previous else None
            pinned = pin_keys[epoch] if pin_keys and epoch < len(pin_keys) else None
            if named is None and pinned is not None and pinned.get("retires") is not None:
                named = pinned["publicKey"]  # owner-recorded retirement: the pin names the key
            if named is None:
                problems.append(f"epoch {epoch - 1} does not end with a rotation entry and the pin records no retirement")
            keys.append(named)
        if pin_keys is None and len(epochs) > 1 and keys[0] is None:
            # Unpinned and rotated: the oldest key is known only from the retired public copy.
            retired = self.directory / "public.0.hex"
            if retired.is_file():
                keys[0] = retired.read_text("ascii").strip()
                problems = [problem for problem in problems if not problem.startswith("epoch 0 has no established key")]
        return {"keys": keys, "problems": problems, "current": current}

    def _pin_problems(self, pin: Mapping[str, Any], sequence: Mapping[str, Any]) -> list[str]:
        keys = [item["publicKey"] for item in pin.get("keys") or []]
        problems: list[str] = []
        if len(keys) != len(sequence["keys"]):
            problems.append(f"the pin names {len(keys)} key epoch(s), the ledger has {len(sequence['keys'])}")
        for epoch, (pinned, derived) in enumerate(zip(keys, sequence["keys"])):
            if derived is not None and pinned != derived:
                problems.append(f"epoch {epoch}: the ledger's key differs from the pinned key")
        if sequence["current"] is None:
            problems.append("no usable signing key")
        elif not keys or keys[-1] != sequence["current"]:
            problems.append("the signing key in use is not the pin's current key")
        return problems

    # ----- appending --------------------------------------------------------------------------

    def append(self, *, action: str, receipt_id: str, canonical: bytes) -> dict[str, Any]:
        """Append one signed entry to the current epoch and bring the witness up to date. Fields
        follow the Custos ledger exactly. Refused with a key that is not the pinned one."""
        with self._lock:
            self.ensure_keys()
            key = self._private_key()
            pin = self.read_pin()
            if pin["state"] == "PRESENT":
                # The key signing now must be the pinned key, or reached from it only through
                # rotation entries (a pin the operator has not yet updated after a rotation;
                # verification and the promotion guard still refuse that until it is).
                derived = self.key_sequence(pin_keys=pin["keys"])["keys"]
                pinned = [item["publicKey"] for item in pin["keys"]]
                if derived[-1] != _public_hex(key) or derived[: len(pinned)] != pinned[: len(derived)]:
                    raise WorldlineError("ANCHOR_KEY_MISMATCH",
                                         "the anchor signing key is not the pinned key, nor reached from it by a "
                                         "rotation; nothing was signed", {"pin": pin["path"]})
            epoch = self.epoch_count() - 1
            path = self.epoch_path(epoch)
            lines = _read_lines(path)
            if lines and rotation_key(lines[-1].split("\t")) is not None:
                raise WorldlineError("ANCHOR_ROTATION_INCOMPLETE",
                                     "the current key epoch is closed by a rotation entry but no next epoch exists; "
                                     "finish it with `worldline anchor rotate` while the daemon is stopped")
            fields = [str(len(lines)), str(int(time.time())), action, receipt_id, "-", _sha(canonical),
                      str(len(canonical)), GENESIS if not lines else line_head(lines[-1])]
            line = _signed_line(key, fields)
            self._append_line(path, line)
            exported = self.export()
            return {"seq": len(lines), "epoch": epoch, "head": line_head(line), "export": exported}

    def anchor_event(self, event_id: str, canonical: bytes) -> dict[str, Any]:
        return self.append(action="causal", receipt_id=event_id, canonical=canonical)

    def _append_line(self, path: Path, line: str) -> None:
        secure_directory(path.parent)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    # ----- witness ----------------------------------------------------------------------------

    def witness_state(self, local: list[str] | None = None) -> dict[str, Any]:
        """The witness compared with the local transcript: MATCH, EXPORT_BEHIND (a prefix),
        ROLLED_BACK (the local ledger is a prefix of the witness) or MISMATCH."""
        witness = self.witness_path
        if witness is None:
            return {"state": "UNCONFIGURED"}
        local = self.entries() if local is None else local
        if not os.path.lexists(witness):
            return {"state": "MISSING", "path": str(witness), "localEntries": len(local), "externalEntries": 0}
        try:
            remote = _read_lines(witness)
        except OSError as exc:
            return {"state": "UNAVAILABLE", "path": str(witness), "reason": str(exc)}
        detail = {"localEntries": len(local), "externalEntries": len(remote), "path": str(witness)}
        if remote == local:
            return {"state": "MATCH", "entries": len(remote), **detail}
        if len(remote) < len(local) and local[: len(remote)] == remote:
            return {"state": "EXPORT_BEHIND", **detail}
        if len(local) < len(remote) and remote[: len(local)] == local:
            return {"state": "ROLLED_BACK", **detail}
        return {"state": "MISMATCH", **detail}

    def export(self) -> dict[str, Any]:
        """Append the missing suffix of the local transcript to the witness (1.9.2, OB-083). The
        witness is compared first and never overwritten or truncated: a witness that is not a
        prefix of the local ledger (a local rollback or rewrite) is left exactly as it is."""
        witness = self.witness_path
        if witness is None:
            return {"state": "UNCONFIGURED"}
        with self._lock:
            local = self.entries()
            compared = self.witness_state(local)
            if compared["state"] in ("ROLLED_BACK", "MISMATCH", "UNAVAILABLE"):
                return {"state": "REFUSED", "witness": compared["state"], "path": str(witness),
                        "reason": "the witness is not a prefix of the local ledger; it was left unchanged"}
            if compared["state"] == "MATCH":
                return {"state": "CURRENT", "path": str(witness)}
            missing = local[compared.get("externalEntries", 0):]
            try:
                self.export_path.mkdir(parents=True, exist_ok=True)
                flags = os.O_WRONLY | os.O_APPEND | os.O_CLOEXEC | os.O_NOFOLLOW
                if compared["state"] == "MISSING":
                    flags |= os.O_CREAT | os.O_EXCL
                descriptor = os.open(witness, flags, 0o644)
            except PermissionError as exc:
                # The pull model: another account appends; this one only reads.
                return {"state": "PULL", "path": str(witness), "reason": str(exc), "behind": len(missing)}
            except OSError as exc:
                return {"state": "FAILED", "path": str(witness), "reason": str(exc)}
            try:
                with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
                    handle.write("".join(line + "\n" for line in missing))
                    handle.flush()
                    os.fsync(handle.fileno())
            except OSError as exc:
                return {"state": "FAILED", "path": str(witness), "reason": str(exc)}
            return {"state": "EXPORTED", "path": str(witness), "appended": len(missing)}

    # ----- verification -----------------------------------------------------------------------

    def _verify_epochs(self, keys: Sequence[str | None], pin_keys: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        epochs = self.epochs()
        for epoch, lines in enumerate(epochs):
            public_hex = keys[epoch] if epoch < len(keys) else None
            result: dict[str, Any] = {"epoch": epoch, "entries": len(lines), "publicKey": public_hex,
                                      "head": GENESIS if not lines else line_head(lines[-1]),
                                      "badChain": 0, "badSignature": 0, "problems": []}
            retirement = None
            if pin_keys and epoch + 1 < len(pin_keys):
                retirement = (pin_keys[epoch + 1].get("retires") or {}).get("entries")
            if lines and public_hex is None:
                result["problems"].append("no key is established for this epoch")
            public = None
            if public_hex is not None:
                try:
                    public = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_hex))
                except ValueError:
                    result["problems"].append("the epoch's key is not an Ed25519 public key")
            expected_prev = GENESIS
            closed_at: int | None = None
            for index, line in enumerate(lines):
                fields = line.split("\t")
                if len(fields) != _FIELDS or fields[0] != str(index) or fields[7] != expected_prev:
                    result["badChain"] += 1
                elif public is None:
                    result["badSignature"] += 1
                else:
                    try:
                        public.verify(bytes.fromhex(fields[8]), _message(fields))
                    except Exception:  # noqa: BLE001 - any failure is a bad signature
                        result["badSignature"] += 1
                if len(fields) == _FIELDS and fields[2] in ROTATION_ACTIONS and closed_at is None:
                    closed_at = index
                    result["rotation"] = {"index": index, "kind": fields[2], "names": rotation_key(fields)}
                if index == 0 and epoch > 0:
                    previous = epochs[epoch - 1]
                    link_ok = (len(fields) == _FIELDS and fields[2] == EPOCH_START and fields[3] == f"epoch:{epoch - 1}"
                               and fields[5] == (GENESIS if not previous else line_head(previous[-1]))
                               and fields[6] == str(len(previous)))
                    if not link_ok:
                        result["problems"].append("the first entry does not name the previous epoch's head")
                expected_prev = line_head(line)
            if closed_at is not None and closed_at != len(lines) - 1:
                result["problems"].append(
                    f"{len(lines) - 1 - closed_at} entr{'y' if len(lines) - 1 - closed_at == 1 else 'ies'} signed with a retired key after its rotation (index {closed_at})")
            if retirement is not None and len(lines) > retirement:
                result["problems"].append(
                    f"{len(lines) - retirement} entr{'y' if len(lines) - retirement == 1 else 'ies'} after the owner-recorded retirement at {retirement}")
            if epoch < len(epochs) - 1 and closed_at is None and retirement is None:
                result["problems"].append("the epoch is followed by another but was never closed by a rotation")
            if epoch == len(epochs) - 1 and closed_at is not None:
                result["problems"].append("the current epoch is closed by a rotation but no next epoch exists")
            results.append(result)
        return results

    def verify(self, *, items: Mapping[str, Any] | None = None, receipts_known: int | None = None) -> dict[str, Any]:
        """One verdict over everything the anchor claims (1.9.2, OB-196/OB-089/OB-083/OB-087/OB-205).

        OK only if every epoch's chain and signatures hold under the pinned key sequence, the key
        in use is the pinned current key, the witness is protected and equals the local ledger,
        and (when `items` is given) every store receipt and causal event is anchored with the hash
        of its canonical bytes and every anchored one is still in the store. Otherwise `state`
        names the most severe problem and `problems` lists them all."""
        pin = self.read_pin()
        pin_keys = pin.get("keys") if pin["state"] == "PRESENT" else None
        sequence = self.key_sequence(pin_keys=pin_keys)
        epoch_results = self._verify_epochs(sequence["keys"], pin_keys)
        local = [line for lines in self.epochs() for line in lines]
        problems: list[dict[str, Any]] = []

        def problem(state: str, detail: str, **extra: Any) -> None:
            problems.append({"state": state, "detail": detail, **extra})

        bad_chain = sum(item["badChain"] for item in epoch_results)
        bad_signature = sum(item["badSignature"] for item in epoch_results)
        if bad_chain or bad_signature:
            problem("BROKEN", f"{bad_chain} chain and {bad_signature} signature failure(s) under the established keys")
        for item in epoch_results:
            for text in item["problems"]:
                problem("BROKEN", f"epoch {item['epoch']}: {text}")
        for text in sequence["problems"]:
            problem("BROKEN", text)

        key_report: dict[str, Any] = {"pin": pin.get("path"), "pinState": pin["state"], "current": sequence["current"],
                                      "epochs": len(sequence["keys"])}
        if pin["state"] == "PRESENT":
            key_report["protection"] = measure_protection(self.pin_path, purpose="pin")
            mismatches = self._pin_problems(pin, sequence)
            for text in mismatches:
                problem("KEY_MISMATCH", text)
            if key_report["protection"]["state"] != "PROTECTED":
                problem("KEY_UNPINNED", f"the pin is not protected: {key_report['protection'].get('reason')}")
            key_report["state"] = "MISMATCH" if mismatches else "PINNED" if key_report["protection"]["state"] == "PROTECTED" else "UNPROTECTED"
        else:
            key_report["state"] = "UNPINNED"
            problem("KEY_UNPINNED", f"no valid pin ({pin['state'].lower()}{': ' + pin['reason'] if pin.get('reason') else ''})"
                    + ("" if self.pin_path is None else f" at {self.pin_path}"))

        witness = self.witness_state(local)
        if self.witness_path is not None:
            witness["protection"] = measure_protection(self.witness_path, purpose="witness")
        state = witness["state"]
        if state == "UNCONFIGURED":
            problem("WITNESS_UNCONFIGURED", "anchor.exportPath is not set, so no copy outside this account exists")
        elif state in ("MISMATCH", "ROLLED_BACK", "EXPORT_BEHIND"):
            problem(state, f"witness {witness['externalEntries']} entries, local {witness['localEntries']}")
        elif state in ("MISSING", "UNAVAILABLE"):
            problem("WITNESS_UNPROTECTED", f"the witness is {state.lower()}: {witness['path']}")
        if witness.get("protection") and witness["protection"]["state"] != "PROTECTED" and state not in ("MISSING",):
            problem("WITNESS_UNPROTECTED", str(witness["protection"].get("reason")))

        coverage: dict[str, Any] | None = None
        if items is not None:
            coverage = self._coverage(items)
            for state_name, key in (("RECEIPT_CHAIN_TRUNCATED", "truncatedReceipts"), ("CAUSAL_CHAIN_TRUNCATED", "truncatedEvents"),
                                    ("COVERAGE_MISMATCH", "mismatched"), ("UNANCHORED", "unanchoredReceiptIds"),
                                    ("UNANCHORED", "unanchoredEventIds")):
                if coverage[key]:
                    problem(state_name, f"{len(coverage[key])} {key}", ids=list(coverage[key])[:20])
            if coverage.get("error"):
                problem(coverage["error"]["code"], coverage["error"]["message"])

        attest = self._attest_verify(sequence["keys"], witness)
        if attest["state"] == "FAILED":
            problem("ATTEST_FAILED", attest.get("verdict") or "attest verify-custos failed")

        alarm = self.alarm()
        overall = "OK"
        for name in SEVERITY:
            if any(item["state"] == name for item in problems):
                overall = name
                break
        result: dict[str, Any] = {
            "state": overall,
            "problems": problems,
            "entries": len(local),
            "head": GENESIS if not local else line_head(local[-1]),
            "ledger": str(self.ledger_path),
            "publicKey": sequence["current"],
            "badChain": bad_chain,
            "badSignature": bad_signature,
            "epochs": epoch_results,
            "key": key_report,
            "witness": witness,
            "external": witness,
            "attest": attest,
            "alarm": alarm,
        }
        if coverage is not None:
            result["coverage"] = coverage
            result["receipts"] = coverage["receipts"]
            result["unanchoredReceipts"] = len(coverage["unanchoredReceiptIds"])
        elif receipts_known is not None:
            result["receipts"] = receipts_known
        return result

    def _coverage(self, items: Mapping[str, Any]) -> dict[str, Any]:
        anchored = self.anchored()
        result: dict[str, Any] = {"receipts": 0, "events": 0, "unanchoredReceiptIds": [], "unanchoredEventIds": [],
                                  "truncatedReceipts": [], "truncatedEvents": [], "mismatched": []}
        if items.get("error"):
            result["error"] = dict(items["error"])
        for kind, missing_key, truncated_key in (("receipts", "unanchoredReceiptIds", "truncatedReceipts"),
                                                  ("events", "unanchoredEventIds", "truncatedEvents")):
            present = {identity: digest for identity, digest in items.get(kind) or []}
            result[kind] = len(present)
            for identity, digest in present.items():
                signed = anchored[kind].get(identity)
                if signed is None:
                    result[missing_key].append(identity)
                elif any(value != digest for value in signed):
                    result["mismatched"].append(identity)
            if not items.get("error"):
                result[truncated_key] = sorted(identity for identity in anchored[kind] if identity not in present)
        return result

    def _attest_verify(self, keys: Sequence[str | None], witness: Mapping[str, Any]) -> dict[str, Any]:
        """Replay each key epoch with attest, pinned to the witnessed prefix of that epoch
        (--min-entries/--expect-head) so a rollback of an epoch fails there too."""
        executable = shutil.which("attest")
        if executable is None:
            return {"state": "UNAVAILABLE", "reason": "attest is not installed"}
        epochs = self.epochs()
        if not any(epochs):
            return {"state": "UNAVAILABLE", "reason": "no ledger yet"}
        witnessed: list[str] = []
        if witness.get("state") in ("MATCH", "EXPORT_BEHIND") and self.witness_path is not None:
            try:
                witnessed = _read_lines(self.witness_path)
            except OSError:
                witnessed = []
        results: list[dict[str, Any]] = []
        offset = 0
        with tempfile.TemporaryDirectory(prefix="worldline-attest-") as temporary:
            for epoch, lines in enumerate(epochs):
                public = keys[epoch] if epoch < len(keys) else None
                if public is None:
                    results.append({"epoch": epoch, "state": "FAILED", "verdict": "no key established"})
                    offset += len(lines)
                    continue
                key_file = Path(temporary) / f"public.{epoch}.hex"
                key_file.write_text(public + "\n", encoding="ascii")
                argv = [executable, "verify-custos", str(self.epoch_path(epoch)), str(key_file), "--quiet"]
                seen = max(0, min(len(lines), len(witnessed) - offset))
                if seen:
                    argv += ["--min-entries", str(seen), "--expect-head", line_head(witnessed[offset + seen - 1])]
                offset += len(lines)
                try:
                    completed = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE, timeout=120, check=False)
                except (OSError, subprocess.TimeoutExpired) as exc:
                    return {"state": "UNAVAILABLE", "reason": str(exc), "tool": executable}
                verdict = completed.stdout.decode("utf-8", "replace").strip().splitlines()
                results.append({"epoch": epoch, "state": "VERIFIED" if completed.returncode == 0 else "FAILED",
                                "exitCode": completed.returncode, "verdict": verdict[-1] if verdict else "",
                                "witnessedEntries": seen})
        failed = [item for item in results if item["state"] != "VERIFIED"]
        return {"state": "FAILED" if failed else "VERIFIED", "exitCode": failed[0].get("exitCode", 1) if failed else 0,
                "verdict": failed[0]["verdict"] if failed else (results[-1]["verdict"] if results else ""),
                "epochs": results, "tool": executable}

    # ----- promotion guard (G2) ---------------------------------------------------------------

    def promotion_guard(self) -> None:
        """Refuse a prepare or commit when no protected witness agrees with the local ledger, or
        the key is not the pinned one (1.9.2, G2; OB-083, OB-087, OB-089). Refusal only: it runs
        before the kernel is asked and never changes an input of the decision."""
        witness = self.witness_path
        if witness is None:
            raise WorldlineError("ANCHOR_WITNESS_UNAVAILABLE",
                                 "no anchor witness is configured (anchor.exportPath); a collapse would leave no copy of "
                                 "the evidence outside this account, so none is prepared or committed",
                                 {"refusedBy": "anchor-witness-guard", "missing": "anchor.exportPath"})
        protection = measure_protection(witness, purpose="witness")
        if protection["state"] != "PROTECTED":
            raise WorldlineError("ANCHOR_WITNESS_UNAVAILABLE",
                                 f"the anchor witness is not out of this account's reach: {protection.get('reason')}; "
                                 "make it append-only (chattr +a, as root) or owned by another account",
                                 {"refusedBy": "anchor-witness-guard", "witness": protection})
        compared = self.witness_state()
        if compared["state"] in ("ROLLED_BACK", "MISMATCH", "UNAVAILABLE"):
            raise WorldlineError("ANCHOR_WITNESS_DISAGREES",
                                 f"the local anchor ledger disagrees with its witness ({compared['state']}); the witness "
                                 "was left unchanged and nothing is promoted until the operator resolves it",
                                 {"refusedBy": "anchor-witness-guard", "witness": compared})
        pin = self.read_pin()
        if pin["state"] != "PRESENT":
            raise WorldlineError("ANCHOR_KEY_UNPINNED",
                                 f"the anchor key is not pinned ({pin['state'].lower()}); write the pin that "
                                 "`worldline anchor pin` prints to a file this account cannot write",
                                 {"refusedBy": "anchor-witness-guard", "pin": pin})
        pin_protection = measure_protection(self.pin_path, purpose="pin")
        if pin_protection["state"] != "PROTECTED":
            raise WorldlineError("ANCHOR_KEY_UNPINNED",
                                 f"the anchor key pin is not out of this account's reach: {pin_protection.get('reason')}",
                                 {"refusedBy": "anchor-witness-guard", "pin": pin_protection})
        mismatches = self._pin_problems(pin, self.key_sequence(pin_keys=pin["keys"]))
        if mismatches:
            raise WorldlineError("ANCHOR_KEY_MISMATCH", "the anchor key sequence differs from the pin: " + "; ".join(mismatches),
                                 {"refusedBy": "anchor-witness-guard", "problems": mismatches})
        alarm = self.alarm()
        if isinstance(alarm, dict) and alarm:
            raise WorldlineError("ANCHOR_ALARM",
                                 f"the anchor raised an alarm at start ({alarm.get('code')}): {alarm.get('message')}",
                                 {"refusedBy": "anchor-witness-guard", "alarm": alarm})

    # ----- start ------------------------------------------------------------------------------

    def startup(self, *, verify_chains: Callable[[], Any], items: Callable[[], Mapping[str, Any]],
                canonical: Callable[[str, str], bytes]) -> dict[str, Any]:
        """What a start does before anything is served (1.9.2): verify the store's chains
        (confined), compare the witness, check coverage by identity and hash, and only then sign
        what predates the anchor and bring the witness up to date. Any disagreement signs
        nothing, leaves the witness untouched and returns an alarm (OB-083, OB-089)."""
        with self._lock:
            try:
                verify_chains()
            except WorldlineError as exc:
                return {"alarm": {"code": exc.code, "message": exc.message, "stage": "store-chains"}}
            compared = self.witness_state()
            if compared["state"] in ("ROLLED_BACK", "MISMATCH", "UNAVAILABLE"):
                return {"alarm": {"code": "ANCHOR_WITNESS_DISAGREES", "stage": "witness", "witness": compared,
                                  "message": f"the local anchor ledger is {compared['state']} against its witness"}}
            listed = items()
            if listed.get("error"):
                return {"alarm": {**listed["error"], "stage": "store-files"}}
            coverage = self._coverage(listed)
            wrong = {key: coverage[key] for key in ("truncatedReceipts", "truncatedEvents", "mismatched") if coverage[key]}
            if wrong:
                return {"alarm": {"code": "ANCHOR_COVERAGE_MISMATCH", "stage": "coverage",
                                  "message": "the store no longer holds what the anchor signed", **{k: v[:20] for k, v in wrong.items()}}}
            added = self.backfill_ids(coverage["unanchoredReceiptIds"], coverage["unanchoredEventIds"], canonical)
            exported = self.export()
            return {"alarm": None, "backfilled": added, "export": exported}

    def backfill_ids(self, receipt_ids: Iterable[str], event_ids: Iterable[str],
                     canonical: Callable[[str, str], bytes]) -> dict[str, int]:
        """Sign receipts and events that predate the anchor, in store order. Called only after
        the store's chains verified (startup)."""
        added = {"receipts": 0, "events": 0}
        for kind, action, identities in (("receipts", "backfill", receipt_ids), ("events", "causal-backfill", event_ids)):
            for identity in identities:
                self.append(action=action, receipt_id=identity, canonical=canonical(kind, identity))
                added[kind] += 1
        return added

    def backfill(self, receipts: list[dict[str, Any]]) -> int:
        """1.9.1's receipt backfill, kept for callers that hold rows (tests, tools). It now signs
        only what the caller's rows carry and is not used by the daemon's start, which verifies
        first (startup)."""
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

    # ----- rotation (offline) -----------------------------------------------------------------

    def rotate(self, *, compromised: bool = False, old_key_unavailable: bool = False) -> dict[str, Any]:
        """Close the current key epoch and open the next (1.9.2, OB-205). Run with the daemon
        stopped and the store lock held (cli: `worldline anchor rotate`): it is not a daemon
        operation, so the operation registry is unchanged.

        Normally the closing entry names the new public key and is signed by the OLD key; the new
        epoch's first entry names the old epoch's head and is signed by the NEW key. With
        `old_key_unavailable` there is no old key to sign with: the retirement is the owner's to
        record in the pin (`retires`), and entries of the old epoch after that point are invalid."""
        with self._lock:
            epoch = self.epoch_count() - 1
            path = self.epoch_path(epoch)
            lines = _read_lines(path)
            pending = self.directory / "secret.key.next"
            if os.path.lexists(pending):
                raise WorldlineError("ANCHOR_ROTATION_INCOMPLETE",
                                     f"a previous rotation left {pending}; inspect the ledger's last entry, then remove "
                                     "the file if that rotation was never written")
            if lines and rotation_key(lines[-1].split("\t")) is not None:
                raise WorldlineError("ANCHOR_ROTATION_INCOMPLETE", "the current epoch is already closed by a rotation entry")
            old_key = None
            if not old_key_unavailable:
                if not self.secret_path.is_file():
                    raise WorldlineError("ANCHOR_KEY_MISSING", "the anchor signing key is missing; rotate with "
                                         "--old-key-unavailable to record its retirement in the pin instead")
                old_key = self._private_key()
                pin = self.read_pin()
                if pin["state"] == "PRESENT" and pin["keys"][-1]["publicKey"] != _public_hex(old_key):
                    raise WorldlineError("ANCHOR_KEY_MISMATCH", "the key to retire is not the pinned current key")
            secure_directory(self.directory)
            new_key = ed25519.Ed25519PrivateKey.generate()
            new_public = _public_hex(new_key)
            raw = new_key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
            descriptor = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="ascii") as handle:
                handle.write(raw.hex() + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            retired_public = None if old_key is None else _public_hex(old_key)
            if old_key is not None:
                fields = [str(len(lines)), str(int(time.time())), "retire-compromised" if compromised else "rotate",
                          f"key:{new_public}", "-", _sha(bytes.fromhex(new_public)), "32",
                          GENESIS if not lines else line_head(lines[-1])]
                closing = _signed_line(old_key, fields)
                self._append_line(path, closing)
                lines.append(closing)
            opening_fields = ["0", str(int(time.time())), EPOCH_START, f"epoch:{epoch}", "-",
                              GENESIS if not lines else line_head(lines[-1]), str(len(lines)), GENESIS]
            self._append_line(self.epoch_path(epoch + 1), _signed_line(new_key, opening_fields))
            if retired_public is not None:
                atomic_write(self.directory / f"public.{epoch}.hex", (retired_public + "\n").encode("ascii"))
            os.replace(pending, self.secret_path)
            atomic_write(self.public_path, (new_public + "\n").encode("ascii"))
            exported = self.export()
            retires = {epoch + 1: len(lines)} if old_key is None else None
            return {"epoch": epoch + 1, "publicKey": new_public, "retiredEpoch": epoch,
                    "retiredPublicKey": retired_public, "compromised": compromised,
                    "ownerRecordedRetirement": old_key is None, "export": exported,
                    "pin": self.pin_document(retires=retires), "pinPath": None if self.pin_path is None else str(self.pin_path)}
