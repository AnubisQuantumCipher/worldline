"""An in-process WORLDLINE with a real controller, a registered root and an anchor witness and
key pin (1.9.2), for the chain-verification, anchor and post-commit tests.

Nothing here touches the operator's daemon, store, units or configuration: every XDG path is
under one temporary directory, and no daemon process or agent is started. Commits go through the
controller's own `collapse.commit` handler with synthetic candidates (as test_typed_absence does).

The witness and the pin cannot really be made append-only or root-owned without privilege, so
their protection is INJECTED here, at the lowest level: `worldline.anchor._file_flags` reports
the append-only attribute for the witness and the immutable one for the pin, and the real
`measure_protection` decides from that. The kernel's own enforcement of those attributes is an
operator-run drill (CHANGELOG 1.9.2), not something these tests show.

The same fixture runs against 1.9.1 (631d0d5) for the failing-first runs: there the pin file is
an unread extra file and the patched function does not exist (it is created, and unused).
"""
from __future__ import annotations

import io
import json
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
from typing import Any, Callable
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from worldline.anchor import AnchorLedger
from worldline.core import Core, hash_id

from freshness_support import isolated_paths, synthetic_candidate
from validation_support import DECLARED_EMPTY_POLICY, attach_fresh_context

FS_IMMUTABLE_FL = 0x10
FS_APPEND_FL = 0x20
PIN_SCHEMA = "worldline-anchor-pin-v1"


def pin_document(public_keys: list[str]) -> dict[str, Any]:
    return {"schema": PIN_SCHEMA, "keys": [{"publicKey": key} for key in public_keys]}


class AnchoredLab:
    def __init__(self, test: unittest.TestCase, *, witness: bool = True, pin: bool = True, protected: bool = True,
                 ghosts: bool = False) -> None:
        self.test = test
        self.temporary = tempfile.TemporaryDirectory(prefix="worldline-anchored-")
        test.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.paths, self.env = isolated_paths(self.root)
        self.core = Core.shared()
        self.work = self.root / "work"
        self.work.mkdir()
        (self.work / ".worldline.json").write_text(json.dumps(DECLARED_EMPTY_POLICY), encoding="utf-8")
        (self.work / "state.txt").write_text("prime", encoding="utf-8")
        self.export = self.root / "witness" if witness else None
        self.config_dir = Path(self.env["XDG_CONFIG_HOME"]) / "worldline"
        self.config_dir.mkdir(mode=0o700, exist_ok=True)
        config: dict[str, Any] = {
            "schemaVersion": 1, "readonlyHomePaths": [],
            "agentCommands": {"fixture": {"argv": ["/usr/bin/true", "{workspace}", "{missionFile}", "{worldState}"],
                                          "credentialMounts": [], "eventFormat": "jsonl"}},
            "ghosts": {"enabled": ghosts, "agent": "fixture" if ghosts else None},
            "anchor": {"exportPath": None if self.export is None else str(self.export)},
        }
        path = self.config_dir / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        os.chmod(path, 0o600)
        self.protected = protected
        self.protected_paths: dict[str, int] = {}
        if self.export is not None:
            self.export.mkdir()
            self.witness = self.export / "anchor.tsv"
            self.pin_path = self.export / "anchor.pin"
            self.protected_paths = {str(self.witness): FS_APPEND_FL, str(self.pin_path): FS_IMMUTABLE_FL}
        if pin and self.export is not None:
            public = AnchorLedger(self.paths, self.export).ensure_keys()
            self.write_pin([public])
        real_flags = None
        try:
            import worldline.anchor as anchor_module
            real_flags = getattr(anchor_module, "_file_flags", None)
        except ImportError:  # pragma: no cover
            pass

        def flags(path: Path) -> int | None:
            if self.protected and str(path) in self.protected_paths:
                return self.protected_paths[str(path)]
            return None if real_flags is None else real_flags(path)

        patcher = mock.patch("worldline.anchor._file_flags", side_effect=flags, create=True)
        patcher.start()
        test.addCleanup(patcher.stop)
        self.app = None
        self.start()
        test.addCleanup(self.close)
        self.controller.roots.register([self.work], confirmed=True)
        self.controller._refresh_watcher()

    # -- lifecycle
    def start(self) -> None:
        from worldline.app import WorldlineApplication
        self.app = WorldlineApplication.build(self.paths)
        self.controller = self.app.controller
        self.store = self.app.store

    def close(self) -> None:
        if self.app is not None:
            self.app.controller.close()
            self.app.store.close()
            self.app = None

    def restart(self) -> None:
        """What a daemon restart does to the anchor: a new controller over the same store."""
        self.close()
        self.start()

    def write_pin(self, public_keys: list[str]) -> None:
        self.pin_path.write_text(json.dumps(pin_document(public_keys)), encoding="utf-8")

    # -- promotion
    def context(self) -> SimpleNamespace:
        return SimpleNamespace(daemon=self.app.daemon)

    def candidate(self, alias: str, changes: dict[str, str] | None = None) -> Any:
        world = synthetic_candidate(self.paths, self.store, self.core, alias, changes or {"state.txt": alias})
        attach_fresh_context(self.store, world, config=self.app.config, core=self.core)
        return self.store.world(alias)

    def prepare(self, alias: str, changes: dict[str, str] | None = None) -> Any:
        self.candidate(alias, changes)
        return self.controller.transactions.prepare(alias)

    def commit(self, alias: str, changes: dict[str, str] | None = None) -> dict[str, Any]:
        prepared = self.prepare(alias, changes)
        return self.controller._collapse_commit({"transactionId": prepared.transaction_id}, self.context())

    # -- the CLI, answered by this controller's own handlers
    def cli(self, *argv: str) -> tuple[int, str, str]:
        from worldline import cli_main
        app = self.app

        def request(_client: Any, operation: str, args: dict[str, Any] | None = None, **_kw: Any) -> Any:
            handler = app.daemon._operations[operation].handler
            return json.loads(json.dumps(handler(args or {}, SimpleNamespace(daemon=app.daemon, peer_uid=os.getuid()))))

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(cli_main.DaemonClient, "request", request), redirect_stdout(out), redirect_stderr(err):
            code = cli_main.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    # -- direct store edits (what a same-uid writer can do)
    def database(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.paths.database, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=OFF")
        return connection

    def ledger_lines(self) -> list[str]:
        path = self.paths.state / "anchor.tsv"
        return [line for line in path.read_text("utf-8").split("\n") if line] if path.is_file() else []

    def rewrite_receipt_consistently(self, index: int, edit: Callable[[dict[str, Any]], None]) -> None:
        """Rewrite receipt `index` and re-link it and every later receipt, keeping ids and count:
        the store's own chain verifies clean afterwards (the SECURITY.md limit)."""
        from worldline.store import CHAIN_GENESIS
        from worldline.canonical import canonical_bytes
        connection = self.database()
        rows = connection.execute("SELECT * FROM receipts ORDER BY rowid").fetchall()
        previous = CHAIN_GENESIS
        for position, row in enumerate(rows):
            payload = Path(row["canonical_path"]).read_bytes()
            if position == index:
                document = json.loads(payload)
                edit(document)
                payload = canonical_bytes(document)
            root = self.core.hash_bytes(b"worldline-receipt-record-v1" + payload)
            chain = self.core.receipt_link(previous, root)
            if position >= index:
                new_path = Path(row["canonical_path"]).parent / f"{chain.hex()}.json"
                Path(row["canonical_path"]).unlink()
                new_path.write_bytes(payload)
                connection.execute("UPDATE receipts SET receipt_root=?,chain_hash=?,canonical_path=? WHERE receipt_id=?",
                                   (hash_id(root), hash_id(chain), str(new_path), row["receipt_id"]))
            previous = chain
        connection.close()

    def rewrite_event_consistently(self, event_id: str, edit: Callable[[dict[str, Any]], None]) -> None:
        """Rewrite one causal event and re-link it and every later event (their ids change with
        their chain hashes, as a real rewrite's would)."""
        from worldline.store import CHAIN_GENESIS
        from worldline.canonical import canonical_bytes
        connection = self.database()
        rows = connection.execute("SELECT * FROM causal_events ORDER BY rowid").fetchall()
        previous = CHAIN_GENESIS
        started = False
        for row in rows:
            payload = Path(row["canonical_path"]).read_bytes()
            if row["event_id"] == event_id:
                document = json.loads(payload)
                edit(document)
                payload = canonical_bytes(document)
                started = True
            root = self.core.hash_bytes(b"worldline-event-v1" + payload)
            chain = self.core.causal_link(previous, root)
            if started:
                new_path = Path(row["canonical_path"]).parent / f"{chain.hex()}.json"
                Path(row["canonical_path"]).unlink()
                new_path.write_bytes(payload)
                connection.execute("UPDATE line_ranges SET event_id=? WHERE event_id=?", (hash_id(chain), row["event_id"]))
                connection.execute(
                    "UPDATE causal_events SET event_id=?,predecessor=?,event_root=?,chain_hash=?,canonical_path=?,reason=? WHERE event_id=?",
                    (hash_id(chain), hash_id(previous), hash_id(root), hash_id(chain), str(new_path),
                     json.loads(payload).get("reason"), row["event_id"]))
            previous = chain
        connection.close()
