#!/usr/bin/env python3
"""Disposable root-owned COSMOGONY authority for one private WORLDLINE mission.

The public socket accepts intent only from the restricted orchestrator. Canonical
Universe, policy, grant, ticket and transaction facts stay under a root-owned state
directory. This is a lab boundary; a sudo-capable host administrator can replace it.
"""

from __future__ import annotations

import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise RuntimeError('AUTHORITY_SHARED_EARLY_SOURCE_REQUIRED')
_source_lease = _approved.current()
if type(_source_lease) is not _approved.ApprovedSourceLease:
    raise RuntimeError('AUTHORITY_SHARED_ACTUAL_SOURCE_LEASE_REQUIRED')
_source_lease.check()
_source_lease.file(__file__, ('SOURCE',))

import base64
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import socket
import socketserver
import stat
import struct
import sys
import threading
import time
import uuid
from typing import Any

import genesis
import daemon_endpoint
import observe_worldline
import evaluation_record as protected_evaluation
from canonical_store import CanonicalRefusal, CanonicalStore
from accepted_actuator import AcceptedActuator
from protected_evaluator import ProtectedEvaluator
from worldline.core import Core, hash_id
from worldline.canonical import canonical_bytes as worldline_canonical
from worldline.finalize import evaluation_record as native_evaluation_record
from worldline.manifest import Manifest


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: bytes) -> str:
    return sha256(value).hexdigest()


def file_sha(path: Path) -> str:
    return digest(path.read_bytes())


def identity(label: str) -> str:
    return digest(label.encode())


def require(condition: bool, code: str) -> None:
    if not condition:
        raise Refusal(code)


class Refusal(Exception):
    pass


class Authority:
    @staticmethod
    def _protected_path(path: Path, *, directory: bool) -> None:
        selected = path.absolute()
        for parent in selected.parents:
            info = parent.lstat()
            sticky_tmp = parent == Path("/tmp") and bool(info.st_mode & stat.S_ISVTX)
            require(info.st_uid == 0 and stat.S_ISDIR(info.st_mode) and
                    (not stat.S_IMODE(info.st_mode) & 0o022 or sticky_tmp),
                    "UNTRUSTED_IMPORT_ANCESTRY")
        info = selected.lstat()
        require(info.st_uid == 0 and not stat.S_ISLNK(info.st_mode) and
                (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)) and
                not stat.S_IMODE(info.st_mode) & 0o022,
                "UNTRUSTED_IMPORT_PATH")

    def fault_hook(self, name: str) -> str | None:
        """A test hook for the fault laboratory; always None in a non-fault deployment (F11)."""
        return (os.environ.get(name)
                if self.config.get("fault_laboratory") is True else None)

    def __init__(self, config_path: Path) -> None:
        require(os.geteuid() == 0, "SERVICE_PRINCIPAL_REQUIRED")
        info = config_path.stat(follow_symlinks=False)
        require(info.st_uid == 0 and stat.S_IMODE(info.st_mode) == 0o600,
                "PROTECTED_CONFIG_OWNERSHIP")
        self.config_path = config_path
        self.config = json.loads(config_path.read_text())
        require(self.config["schema"] == "cosmogony.authority-v1.lab-config", "CONFIG_SCHEMA")
        # Composed step (b): behind the root intent gate, the promotion operation identity is
        # the gate's journaled operation ID, so one identity spans gate, ledger and broker.
        require(self.config["promotion_operation_source"] in ("broker", "root-intent-gate"),
                "CONFIG_PROMOTION_OPERATION_SOURCE")
        # Composed step (e): with an evidence state, contract step 3 (examine) is a journaled
        # barrier before the COMMIT ticket. Absence is explicit (None), never a missing key.
        require((self.config["evidence_state"] is None) ==
                (self.config["evidence_policy"] is None), "CONFIG_EVIDENCE_SHAPE")
        self.state_dir = Path(self.config["state_dir"])
        state_info = self.state_dir.stat(follow_symlinks=False)
        require(state_info.st_uid == 0 and stat.S_IMODE(state_info.st_mode) == 0o700,
                "PROTECTED_STATE_OWNERSHIP")
        self.state_file = self.state_dir / "authority.json"
        self.lock = threading.RLock()
        self.transaction_lock = threading.Lock()
        self._check_static_inputs()
        try:
            self.endpoint_generation = daemon_endpoint.read_seal(self.config)["generation"]
        except daemon_endpoint.EndpointRefusal as exc:
            raise Refusal(str(exc)) from exc
        if self.state_file.exists():
            self.state = json.loads(self.state_file.read_text())
            require(self.state["config_sha256"] == file_sha(config_path), "CONFIG_CHANGED_AFTER_STATE")
        else:
            self.state = {"schema": "cosmogony.authority-v1.state", "phase": "NEW",
                          "config_sha256": file_sha(config_path), "universe": None,
                          "world": None, "evaluation": None, "transaction": None,
                          "tickets": {}, "events": [],
                          "grants": {str(self.config["orchestrator_uid"]): {
                              "actor_id": self.actor_id,
                              "actions": ["abandon", "create_world", "promote", "recover",
                                          "state"]}}}
            self._save()
        self.canonical_store = CanonicalStore(
            Path(self.config["canonical_root"]),
            managed_root=Path(self.config["managed_root"]),
            daemon_data_root=Path(self.config["daemon_data_root"]),
            mission_target=self.config["mission_spec"]["target"],
            expected_target_sha256=self.config["mission_spec"]["expected_sha256"],
            fixture_baseline_sha256=self.config["fixture_baseline_sha256"],
            fixture_modes=self.config["fixture_modes"],
            fault_laboratory=self.config["accepted_fault_laboratory"])
        self.accepted_actuator = AcceptedActuator(self.config, self.canonical_store)
        self.protected_evaluator = ProtectedEvaluator(self.config, self.canonical_store)
        self.evidence_state = None
        if self.config["evidence_state"] is not None:
            self.evidence_state = Path(self.config["evidence_state"])
            with self.evidence_protected.ProtectedEvidence(self.evidence_state) as evidence:
                require(evidence.policy == self.config["evidence_policy"],
                        "EVIDENCE_POLICY_UNBOUND")

    def _check_static_inputs(self) -> None:
        cfg = self.config
        marker = Path(cfg["managed_realm"])
        self._protected_path(marker, directory=False)
        require(file_sha(marker) == cfg["managed_realm_sha256"] and
                json.loads(marker.read_text()).get("phase") == "SEALED",
                "MANAGED_REALM_NOT_SEALED")
        if hasattr(self, "state"):
            require(file_sha(self.config_path) == self.state["config_sha256"],
                    "CONFIG_CHANGED_AFTER_STATE")
        for path_key, hash_key in (("worldline_library", "worldline_library_sha256"),
                                   ("proof_manifest", "proof_manifest_sha256"),
                                   ("genesis_library", "genesis_library_sha256"),
                                   ("genesis_proof_manifest", "genesis_proof_manifest_sha256")):
            path = Path(cfg[path_key])
            info = path.stat(follow_symlinks=False)
            require(info.st_uid == 0 and not stat.S_ISLNK(info.st_mode) and
                    not stat.S_IMODE(info.st_mode) & 0o022 and file_sha(path) == cfg[hash_key],
                    "PROTECTED_INPUT_CHANGED")
        manifest = json.loads(Path(cfg["proof_manifest"]).read_text())
        require(manifest["library"]["sha256"] == cfg["worldline_library_sha256"] and
                manifest["proof"]["unproved"] == manifest["proof"]["justified"] ==
                manifest["proof"]["pragmaAssume"] == 0,
                "PROOF_RUNTIME_BINDING_REFUSED")
        genesis_manifest = json.loads(Path(cfg["genesis_proof_manifest"]).read_text())
        report = Path(cfg["genesis_proof_report"])
        self._protected_path(report, directory=False)
        require(genesis_manifest.get("schema") ==
                "cosmogony-genesis-proof-runtime-binding-v1" and
                genesis_manifest["library"]["sha256"] == cfg["genesis_library_sha256"] and
                genesis_manifest["proof"]["reportSha256"] == file_sha(report) and
                all(genesis_manifest["proof"][name] == 0 for name in
                    ("justified", "unproved", "pragmaAssume", "pragmaAnnotate")),
                "GENESIS_PROOF_RUNTIME_BINDING_REFUSED")
        inventory_path = Path(cfg["source_inventory"])
        self._protected_path(inventory_path, directory=False)
        require(file_sha(inventory_path) == cfg["source_inventory_sha256"],
                "SOURCE_INVENTORY_CHANGED")
        inventory = json.loads(inventory_path.read_text())
        install = Path(cfg["install_root"])
        self._protected_path(install, directory=True)
        require(type(inventory) is dict and inventory and
                all(type(name) is str and type(value) is str for name, value in inventory.items()),
                "SOURCE_INVENTORY_INVALID")
        for name, expected in inventory.items():
            path = install / name
            require(path.resolve(strict=True).is_relative_to(install) and
                    file_sha(path) == expected, "INSTALLED_SOURCE_CHANGED")
            self._protected_path(path, directory=False)
        import worldline.core
        import worldline.finalize
        import canonical_store
        import accepted_actuator
        import protected_evaluator
        checked = [genesis, daemon_endpoint, observe_worldline, protected_evaluation,
                   canonical_store, accepted_actuator, protected_evaluator,
                   worldline.core, worldline.finalize]
        if cfg["evidence_state"] is not None:
            # The evidence ledger modules come from the installed universe_source, whose every
            # file the inventory loop above has already hashed.
            evidence_source = str(install / "universe_source")
            if evidence_source not in sys.path:
                sys.path.append(evidence_source)
            import adapter.evidence_store
            import adapter.universe_store
            import evidence_authority.protected
            self.evidence_protected = evidence_authority.protected
            self.evidence_canonical = adapter.universe_store.canonical
            checked += [adapter.evidence_store, adapter.universe_store,
                        evidence_authority.protected]
        if "shared_source_binding" in cfg:
            # Only the actual immutable WORLDLINE import/native boundary moves.
            # All original external E inventories and mutable authority facts stay.
            from worldline.protected_shared_source import from_path
            require(install == self.state_dir.parents[1] / "install",
                    "SHARED_AUTHORITY_ORIGINAL_INSTALL_STATE_LAYOUT_REQUIRED")
            shared = from_path(cfg["shared_source_binding"], mutable_root=self.state_dir.parents[1])
            require(Path(cfg["worldline_library"]) == shared.library and
                    cfg["worldline_library_sha256"] ==
                    shared.inventory[shared.library.relative_to(shared.root).as_posix()]["sha256"] and
                    Path(cfg["daemon_source_path"]) == shared.root / "runtime/worldline/daemon.py" and
                    cfg["daemon_source_sha256"] == shared.inventory["runtime/worldline/daemon.py"]["sha256"],
                    "SHARED_AUTHORITY_NATIVE_DAEMON_SOURCE_SPLIT")
            for module in checked:
                source = Path(module.__file__).resolve(strict=True)
                if module in (worldline.core, worldline.finalize):
                    expected = shared.root / ("runtime/" + module.__name__.replace(".", "/") + ".py")
                    require(source == expected and
                            source.relative_to(shared.root).as_posix() in shared.inventory,
                            "SHARED_AUTHORITY_IMPORT_SOURCE_UNPROTECTED")
                else:
                    require(source.is_relative_to(install) and
                            str(source.relative_to(install)) in inventory,
                            "IMPORT_SOURCE_UNPROTECTED")
            require(Path(__file__).resolve(strict=True) ==
                    shared.root / "protected-authority/authority_service.py",
                    "SHARED_AUTHORITY_SERVICE_SOURCE_UNPROTECTED")
            shared.check()
            _source_lease.check()
        else:
            for module in checked:
                source = Path(module.__file__).resolve(strict=True)
                require(source.is_relative_to(install) and
                        str(source.relative_to(install)) in inventory,
                        "IMPORT_SOURCE_UNPROTECTED")
            require(Path(__file__).resolve(strict=True) == install / "authority_service.py",
                    "SERVICE_SOURCE_UNPROTECTED")
        for entry in sys.path:
            require(bool(entry), "PYTHON_IMPORT_PATH_UNSAFE")
            path = Path(entry)
            if path.exists():
                self._protected_path(path, directory=True)
        self.mission_id = digest(b"COSMOGONY-phase4-mission-v1\0" + canonical(cfg["mission_spec"]))
        self.policy_id = digest(b"COSMOGONY-phase4-policy-v1\0" + canonical(cfg["policy"]))
        self.actor_id = identity("phase4 disposable builder:" + self.mission_id)

    def _save(self) -> None:
        try:
            self._write_state()
        except BaseException:
            # Review E4: a failed journal write must not leave memory ahead of the file while
            # the broker keeps serving. Stop, so startup reloads the authoritative journal.
            os._exit(75)

    def _write_state(self) -> None:
        path = self.state_dir / ("authority." + secrets.token_hex(8) + ".tmp")
        payload = json.dumps(self.state, sort_keys=True, indent=2).encode() + b"\n"
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(path, self.state_file)
        directory = os.open(self.state_dir, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)

    def _event(self, kind: str, facts: dict[str, Any]) -> None:
        self.state["events"].append({"kind": kind, "facts": facts})
        self._save()

    @staticmethod
    def _create_private_file(path: Path, payload: bytes) -> None:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)

    def _transaction_dir(self, operation_id: str) -> Path:
        top = self.state_dir / "transactions"
        top.mkdir(mode=0o700, exist_ok=True)
        path = top / operation_id
        path.mkdir(mode=0o700)
        return path

    def _evaluation_policy(self, observation: dict, status: dict, universe: dict) -> dict:
        mission = self.config["mission_spec"]["objective"]
        mission_hash = hash_id(Core.shared().hash_bytes(
            b"worldline-mission-v1" + mission.encode("utf-8", "strict")))
        self._mapped_library(os.getpid())
        return {
            "schema": "cosmogony-authority-v1-evaluation-policy",
            "universeId": universe["universe_id"], "missionId": self.mission_id,
            "policyId": self.policy_id, "policyEpoch": self.config["policy_epoch"],
            "worldlineInstanceId": observation["worldline_instance_id"],
            "worldlineInstanceUuid": observation["worldline_instance_uuid"],
            "rootSetId": observation["root_set_id"],
            "rootSetFingerprint": digest(protected_evaluation.canonical(status["prime"]["roots"])),
            "primeId": status["prime"]["id"],
            "primeGeneration": observation["prime_generation"],
            "allowedWorldAlias": self.config["world_alias"],
            "requiredCheckId": "exam", "missionHash": mission_hash,
            "kernelLibrarySha256": self.config["worldline_library_sha256"],
            "servicePrincipalId": identity("cosmogony-authority-v1:root-service:" + self.policy_id),
        }

    def _daemon(self, operation: str, args: dict[str, Any] | None = None,
                *, return_raw: bool = False) -> Any:
        request_id = str(uuid.uuid4())
        request = {"id": request_id, "op": operation, "args": args or {}}
        try:
            record = daemon_endpoint.read_seal(
                self.config, generation=self.endpoint_generation)
            daemon_endpoint.check_entry(self.config, record)
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(240)
                try:
                    connection.connect(self.config["daemon_socket"])
                except OSError as exc:
                    raise Refusal("SEALED_ENDPOINT_CONNECT_FAILED") from exc
                daemon_endpoint.check_connection(self.config, record, connection)
                self._mapped_library(record["pid"])
                connection.sendall(canonical(request) + b"\n")
                with connection.makefile("rb") as reader:
                    while True:
                        raw = reader.readline()
                        require(bool(raw), "DAEMON_DISCONNECTED")
                        response = json.loads(raw.decode("utf-8", "strict"))
                        require(raw == worldline_canonical(response) + b"\n",
                                "DAEMON_WIRE_NOT_CANONICAL")
                        if "event" in response:
                            daemon_endpoint.check_connection(self.config, record, connection)
                            continue
                        require(response.get("id") == request_id, "DAEMON_RESPONSE_ID")
                        daemon_endpoint.check_connection(self.config, record, connection)
                        if not response.get("ok"):
                            error = response.get("error") or {}
                            raise Refusal("WORLDLINE_" + str(error.get("code", "REFUSED")))
                        result = response["result"]
                        result_raw = worldline_canonical(result)
                        require(b'"result":' + result_raw in raw,
                                "DAEMON_WIRE_RESULT_MISMATCH")
                        return (result, result_raw) if return_raw else result
        except daemon_endpoint.EndpointRefusal as exc:
            raise Refusal(str(exc)) from exc

    def _observation(self) -> tuple[dict, dict, bytes]:
        status, raw = self._daemon("status", return_raw=True)
        observation = observe_worldline.summarize(status, raw)
        require(observation["daemon"]["state"] == "RUNNING" and
                observation["prime_state"] == "VALID" and
                observation["prime_dirty"] is False and not observation["running_jobs"],
                "UNSAFE_WORLDLINE_OBSERVATION")
        ping = self._daemon("ping")
        sealed_pid = daemon_endpoint.read_seal(
            self.config, generation=self.endpoint_generation)["pid"]
        require(ping["pid"] == sealed_pid == observation["daemon"]["pid"] and
                ping.get("runtimeSourcePath") == self.config["daemon_source_path"] and
                ping.get("runtimeSourceSha256") == self.config["daemon_source_sha256"],
                "DAEMON_IDENTITY_CHANGED")
        self._mapped_library(sealed_pid)
        return observation, status, raw

    def _mapped_library(self, pid: int) -> None:
        self._check_static_inputs()
        selected = Path(self.config["worldline_library"])
        info = selected.stat()
        if pid == os.getpid():
            require(Core.shared().library_path == selected.resolve(strict=True) and
                    file_sha(selected) == self.config["worldline_library_sha256"],
                    "BROKER_NATIVE_LIBRARY_MISMATCH")
        maps = Path(f"/proc/{pid}/maps").read_text().splitlines()
        rows = [line.split() for line in maps if line.split()[-1] == str(selected)]
        require(bool(rows), "PROVED_LIBRARY_NOT_MAPPED")
        for fields in rows:
            major, minor = (int(item, 16) for item in fields[3].split(":"))
            require(int(fields[4]) == info.st_ino and major == os.major(info.st_dev) and
                    minor == os.minor(info.st_dev), "PROVED_LIBRARY_MAPPING_CHANGED")

    def _mapped_genesis(self) -> None:
        selected = Path(self.config["genesis_library"])
        info = selected.stat()
        rows = [line.split() for line in Path(f"/proc/{os.getpid()}/maps").read_text().splitlines()
                if line.split()[-1] == str(selected)]
        require(bool(rows) and file_sha(selected) == self.config["genesis_library_sha256"],
                "GENESIS_LIBRARY_NOT_MAPPED")
        for fields in rows:
            major, minor = (int(item, 16) for item in fields[3].split(":"))
            require(int(fields[4]) == info.st_ino and major == os.major(info.st_dev) and
                    minor == os.minor(info.st_dev), "GENESIS_LIBRARY_MAPPING_CHANGED")

    def _universe(self, observation: dict) -> dict:
        mission_id = self.mission_id
        return {
            "universe_id": identity("authority-v1 universe:" + mission_id),
            "mission_id": mission_id, "policy_id": self.policy_id,
            "policy_owner_mission": mission_id,
            "worldline_instance_id": observation["worldline_instance_id"],
            "root_set_id": observation["root_set_id"],
            "prime_id": observation["prime_id"],
            "policy_epoch": self.config["policy_epoch"],
            "budget": {"world_limit": 1, "worlds_reserved": 0,
                       "evaluation_limit": 1, "evaluations_reserved": 0},
            "agents": [{"identity": self.actor_id, "role": "builder"}],
        }

    def _genesis_decision(self, universe: dict, action: str) -> tuple[dict, dict]:
        request = {"request_id": identity("authority-v1 " + action + ":" + self.mission_id),
                   **{key: universe[key] for key in (
                       "universe_id", "mission_id", "policy_id", "worldline_instance_id",
                       "root_set_id", "prime_id", "policy_epoch")},
                   "actor_id": self.actor_id, "action": action}
        decision = genesis.decide(universe, request, Path(self.config["genesis_library"]))
        self._mapped_genesis()
        require(decision == {"kind": "FORWARD_WORLDLINE", "reason": "WORLDLINE_REQUEST_ELIGIBLE",
                             "authority": "COSMOGONY_REQUEST_ONLY"}, "GENESIS_DENIED")
        return request, decision

    def _issue(self, operation: str, args: dict, observation: dict, *, stage: str) -> str:
        self._check_static_inputs()
        token = secrets.token_hex(32)
        self.state["tickets"][token] = {
            "operation": operation, "args_sha256": digest(canonical(args)),
            "instance_id": observation["worldline_instance_id"],
            "root_set_id": observation["root_set_id"],
            "prime_id": observation["prime_id"],
            "prime_generation": observation["prime_generation"],
            "policy_id": self.policy_id, "policy_epoch": self.config["policy_epoch"],
            "mission_id": self.mission_id,
            "runtime_library_sha256": self.config["worldline_library_sha256"],
            "endpoint_generation": self.endpoint_generation,
            "stage": stage, "used": False,
        }
        self._event("TICKET_ISSUED", {"stage": stage, "ticket_sha256": digest(token.encode())})
        return token

    def redeem(self, request: dict, *, peer_uid: int, peer_pid: int) -> dict:
        require(peer_uid == self.config["daemon_uid"], "DAEMON_PRINCIPAL_REQUIRED")
        require(not self._accepted_binding_exists(),
                "ACCEPTED_BINDING_SEALED")
        self._check_static_inputs()
        ping = self._daemon("ping")
        sealed = daemon_endpoint.read_seal(
            self.config, generation=self.endpoint_generation)
        daemon_endpoint.check_entry(self.config, sealed)
        daemon_endpoint.check_process(sealed)
        sealed_pid = sealed["pid"]
        require(peer_pid == ping["pid"] == sealed_pid,
                "DAEMON_PEER_PID_MISMATCH")
        token = request.get("ticket")
        require(type(token) is str and token in self.state["tickets"], "TICKET_UNKNOWN")
        record = self.state["tickets"][token]
        require(not record["used"], "TICKET_REPLAY")
        # Burning the ticket before any recheck/action makes interruption fail closed.
        record["used"] = True
        self._event("TICKET_CONSUMED", {"stage": record["stage"],
                                        "ticket_sha256": digest(token.encode())})
        require(request.get("operation") == record["operation"] and
                digest(canonical(request.get("args"))) == record["args_sha256"],
                "TICKET_OPERATION_MISMATCH")
        require(record.get("endpoint_generation") == self.endpoint_generation,
                "TICKET_ENDPOINT_GENERATION_CHANGED")
        status = json.loads(Path(self.config["daemon_status"]).read_text())
        raw = json.dumps(status, sort_keys=True, indent=2).encode() + b"\n"
        observation = observe_worldline.summarize(status, raw)
        require(observation["worldline_instance_id"] == record["instance_id"] and
                observation["root_set_id"] == record["root_set_id"] and
                observation["prime_id"] == record["prime_id"] and
                observation["prime_generation"] == record["prime_generation"] and
                observation["prime_dirty"] is False,
                "TICKET_STALE_WORLDLINE")
        self._mapped_library(peer_pid)
        daemon_endpoint.check_entry(self.config, sealed)
        daemon_endpoint.check_process(sealed)
        return {"state": "AUTHORIZED_SINGLE_USE"}

    def actuator_request(self, request: dict, *, peer_uid: int, peer_pid: int) -> dict:
        """The root broker is the C actuator's distinct worker for an authorized commit."""
        require(peer_uid == self.config["daemon_uid"], "DAEMON_PRINCIPAL_REQUIRED")
        require(not self._accepted_binding_exists(),
                "ACCEPTED_BINDING_SEALED")
        require(set(request) == {"op", "transactionId"},
                "ACTUATOR_REQUEST_INVALID")
        transaction = self.state.get("transaction")
        require(self.state["phase"] == "AUTHORIZED" and type(transaction) is dict and
                request["transactionId"] == transaction["id"],
                "ACTUATOR_TRANSACTION_NOT_AUTHORIZED")
        try:
            parsed_id = uuid.UUID(transaction["id"])
        except ValueError as exc:
            raise Refusal("ACTUATOR_TRANSACTION_ID_INVALID") from exc
        require(str(parsed_id) == transaction["id"], "ACTUATOR_TRANSACTION_ID_INVALID")
        require(transaction.get("endpoint_generation") == self.endpoint_generation,
                "ACTUATOR_TRANSACTION_ENDPOINT_CHANGED")
        expected_args = digest(canonical({"transactionId": transaction["id"]}))
        require(any(ticket["operation"] == "collapse.commit" and
                    ticket["stage"] == "COMMIT" and ticket["used"] is True and
                    ticket.get("endpoint_generation") == self.endpoint_generation and
                    ticket["args_sha256"] == expected_args
                    for ticket in self.state["tickets"].values()),
                "ACTUATOR_COMMIT_TICKET_NOT_CONSUMED")
        status = json.loads(Path(self.config["daemon_status"]).read_text())
        sealed = daemon_endpoint.read_seal(
            self.config, generation=self.endpoint_generation)
        daemon_endpoint.check_entry(self.config, sealed)
        daemon_endpoint.check_process(sealed)
        sealed_pid = sealed["pid"]
        require(status["daemon"]["pid"] == peer_pid == sealed_pid,
                "DAEMON_PEER_PID_MISMATCH")
        self._mapped_library(peer_pid)
        runtime_parent = Path("/run/user") / str(peer_uid)
        runtime_info = runtime_parent.lstat()
        require(runtime_info.st_uid == peer_uid and stat.S_ISDIR(runtime_info.st_mode) and
                stat.S_IMODE(runtime_info.st_mode) == 0o700,
                "ACTUATOR_RUNTIME_PARENT_UNTRUSTED")
        ingress = runtime_parent / ("wla-" + transaction["id"]) / "request.sock"
        require(ingress.name == "request.sock" and
                ingress.parent.parent == runtime_parent and
                ingress.parent.lstat().st_uid == peer_uid and
                stat.S_IMODE(ingress.parent.lstat().st_mode) == 0o711,
                "ACTUATOR_INGRESS_UNTRUSTED")
        info = ingress.lstat()
        require(stat.S_ISSOCK(info.st_mode) and info.st_uid == peer_uid and
                stat.S_IMODE(info.st_mode) == 0o666,
                "ACTUATOR_SOCKET_UNTRUSTED")
        self._event("ACTUATOR_BROKER_REQUEST", {"transaction_id": transaction["id"]})
        with socket.socket(socket.AF_UNIX) as worker:
            worker.settimeout(10)
            worker.connect(str(ingress))
            peer = worker.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED,
                                     struct.calcsize("3i"))
            service_pid, service_uid, _service_gid = struct.unpack("3i", peer)
            require(service_uid == peer_uid and service_pid > 0,
                    "ACTUATOR_SERVICE_PEER_INVALID")
            expected_service = Path(self.config["install_root"]) / "bin/worldline-protected-service"
            self._protected_path(expected_service, directory=False)
            inventory = json.loads(Path(self.config["source_inventory"]).read_text())
            require(file_sha(expected_service) ==
                    inventory["bin/worldline-protected-service"] and
                    os.readlink(f"/proc/{service_pid}/exe") == str(expected_service),
                    "ACTUATOR_SERVICE_EXECUTABLE_MISMATCH")
            executable_info = expected_service.stat()
            process_info = os.stat(f"/proc/{service_pid}/exe")
            require((process_info.st_dev, process_info.st_ino) ==
                    (executable_info.st_dev, executable_info.st_ino),
                    "ACTUATOR_SERVICE_INODE_MISMATCH")
            process_fields = Path(f"/proc/{service_pid}/stat").read_text().rsplit(") ", 1)[1].split()
            require(int(process_fields[1]) == peer_pid,
                    "ACTUATOR_SERVICE_PARENT_MISMATCH")
            worker.sendall(b"A")
            require(worker.recv(1) == b"C", "ACTUATOR_EXCHANGE_REFUSED")
        daemon_endpoint.check_entry(self.config, sealed)
        daemon_endpoint.check_process(sealed)
        self._event("ACTUATOR_BROKER_COMMITTED", {"transaction_id": transaction["id"]})
        return {"state": "ACTUATOR_WORKER_COMMITTED"}

    def _accepted_binding_exists(self) -> bool:
        transaction = self.state.get("transaction")
        if type(transaction) is not dict:
            return False
        path = (self.canonical_store.transactions / transaction["id"] /
                "config.json")
        try:
            path.lstat()
        except FileNotFoundError:
            return False
        return True

    def grant_for(self, peer_uid: int, action: str) -> dict:
        grant = self.state["grants"].get(str(peer_uid))
        require(type(grant) is dict and action in grant.get("actions", []),
                "ORCHESTRATOR_GRANT_REQUIRED")
        require(grant.get("actor_id") == self.actor_id, "ORCHESTRATOR_ACTOR_MISMATCH")
        return grant

    def create_world(self) -> dict:
        with self.lock:
            require(self.state["phase"] == "NEW", "MISSION_ALREADY_STARTED")
            observation, status, raw_status_before = self._observation()
            universe = self._universe(observation)
            request, decision = self._genesis_decision(universe, "create_world")
            policy = self._evaluation_policy(observation, status, universe)
            require(len(status["prime"]["roots"]) == 1,
                    "CANONICAL_ROOT_SET_INVALID")
            canonical_before = self.canonical_store.initialize(
                universe_id=universe["universe_id"], policy_id=self.policy_id,
                mission_id=self.mission_id, prime=status["prime"],
                root_info=status["prime"]["roots"][0])
            require(canonical_before["generation"] == observation["prime_generation"],
                    "CANONICAL_OBSERVATION_CHANGED")
            operation = {"operationId": secrets.token_hex(32), "kind": "create_world",
                         "worldAlias": self.config["world_alias"],
                         "expectedPrimeGeneration": observation["prime_generation"]}
            transaction_dir = self._transaction_dir(operation["operationId"])
            launch = {
                "schema": "cosmogony-authority-v1-launch",
                "operationId": operation["operationId"],
                "admissionNonce": secrets.token_hex(32),
                "universeId": universe["universe_id"], "missionId": self.mission_id,
                "policyId": self.policy_id, "policyEpoch": self.config["policy_epoch"],
                "worldAlias": self.config["world_alias"],
                "primeInstanceId": observation["worldline_instance_uuid"],
                "primeId": status["prime"]["id"],
                "primeGeneration": observation["prime_generation"],
                "statusBeforeSha256": digest(raw_status_before),
                "kernelLibrarySha256": self.config["worldline_library_sha256"],
            }
            self._create_private_file(transaction_dir / "status-before.json", raw_status_before)
            self._create_private_file(transaction_dir / "launch.json",
                                      protected_evaluation.canonical(launch))
            self.state["universe"] = universe
            self.state["grant"] = {"request": request, "decision": decision,
                                   "observation": observation}
            self.state["evaluation_policy"] = policy
            self.state["creation_operation"] = operation
            self.state["evaluation_transaction_dir"] = str(transaction_dir)
            self.state["phase"] = "ELIGIBLE"
            self._save()
            args = {"name": self.config["world_alias"],
                    "mission": self.config["mission_spec"]["objective"],
                    "agent": self.config["agent"], "wait": True}
            ticket = self._issue("fork", args, observation, stage="CREATE_WORLD")
        try:
            world, raw_fork = self._daemon(
                "fork", {**args, "authorityTicket": ticket}, return_raw=True)
        except Refusal:
            with self.lock:
                self.state["phase"] = "FORK_REFUSED"
                self._save()
            raise
        with self.lock:
            self.state["world"] = world
            self.state["phase"] = "FORK_RETURNED"
            self._event("WORLD_CREATED", {"instanceId": world.get("instanceId"),
                                           "contentId": world.get("id")})
        require(world.get("state") == "VALID", "WORLD_NOT_VALID")
        try:
            shown, raw_show = self._daemon(
                "show", {"world": self.config["world_alias"]}, return_raw=True)
            _after_observation, after_status, raw_after = self._observation()
            checks = world.get("checks") or []
            check = next(row for row in checks if row.get("id") == "exam")
            private_report = check["privateReport"]
            raw_report = base64.b64decode(private_report["payloadB64"], validate=True)
            raw_boundary = protected_evaluation.canonical(check["evaluatorBoundary"])
            fork_result = {
                "schema": "cosmogony-authority-v1-fork-result",
                "operationId": operation["operationId"],
                "admissionNonce": launch["admissionNonce"],
                "forkResponseSha256": digest(raw_fork),
                "worldInstanceId": world["instanceId"],
                "worldContentId": world["id"],
                "runId": private_report["runId"],
                "reportSha256": private_report["sha256"],
            }
            for name, payload in (
                ("fork-response.json", raw_fork), ("show.json", raw_show),
                ("status-after.json", raw_after), ("report.bin", raw_report),
                ("boundary.json", raw_boundary),
                ("fork-result.json", protected_evaluation.canonical(fork_result)),
            ):
                self._create_private_file(transaction_dir / name, payload)
            bundle = protected_evaluation.persist_once(transaction_dir, policy, operation)
        except (KeyError, ValueError, StopIteration, protected_evaluation.Refusal) as exc:
            with self.lock:
                self.state["phase"] = "EVALUATION_REFUSED"
                self._event("EVALUATION_REFUSED", {"reason": str(exc)})
            raise Refusal("EVALUATION_JOURNAL_REFUSED") from exc
        with self.lock:
            self.state["evaluation"] = bundle
            self.state["phase"] = "WORLD_VALID"
            self._event("EVALUATION_RECORDED", {"digest": bundle["digest"]})
        return {"state": "WORLD_VALID", "world": world,
                "evaluation_digest": bundle["digest"],
                "worldline_verdict_source": "DAEMON_REPORTED",
                "mission_id": self.mission_id, "universe_id": universe["universe_id"],
                "policy_id": self.policy_id, "policy_epoch": self.config["policy_epoch"],
                "canonical_prime": self.canonical_store.current()}

    def _evaluation(self) -> tuple[dict, dict]:
        self._check_static_inputs()
        policy = self.state["evaluation_policy"]
        creation = self.state["creation_operation"]
        promotion = self.state["promotion_operation"]
        directory = Path(self.state["evaluation_transaction_dir"])
        _observation, status, raw_status = self._observation()
        world, raw_show = self._daemon(
            "show", {"world": self.config["world_alias"]}, return_raw=True)
        self._mapped_library(os.getpid())
        try:
            binding = protected_evaluation.promotion_binding(
                directory, policy, creation, promotion,
                raw_current_status=raw_status, raw_current_show=raw_show)
        except protected_evaluation.Refusal as exc:
            raise Refusal(str(exc)) from exc
        checks = (world.get("evidence") or {}).get("checks") or []
        check = next((row for row in checks if row.get("id") == "exam"), None)
        require(type(check) is dict, "REQUIRED_EVALUATION_MISSING")
        native = native_evaluation_record(check)
        observed = check.get("evaluation") or {}
        fields = ("bundleIntegrity", "executionStatus", "evaluationOutcome",
                  "reportIntegrity", "admissibleForPromotion")
        require(all(native.get(field) == observed.get(field) for field in fields) and
                native["admissibleForPromotion"] is True,
                "NATIVE_EVALUATION_GATE_REFUSED")
        return binding, world

    def promote(self, operation_id: str | None = None,
                protected_universe: dict | None = None) -> dict:
        with self.lock:
            require(self.state["phase"] == "WORLD_VALID", "PROMOTION_STATE_INVALID")
            gate_sourced = self.config["promotion_operation_source"] == "root-intent-gate"
            require((operation_id is not None) == gate_sourced and
                    (protected_universe is not None) == (self.evidence_state is not None),
                    "PROMOTION_OPERATION_SOURCE_MISMATCH")
            if gate_sourced:
                require(not any(row.get("promotion_operation_id") == operation_id
                                for row in self.state.get("transaction_history", [])),
                        "PROMOTION_OPERATION_REPLAY")
                # Review C1: an operation the gate abandoned can never start later.
                require(operation_id not in self.state.get("abandoned_operations", []),
                        "PROMOTION_OPERATION_ABANDONED")
            self._test_refusal("before_prepare")
            observation, _status, _raw_status = self._observation()
            grant = self.state["grant"]["observation"]
            require(all(observation[key] == grant[key] for key in (
                "worldline_instance_id", "root_set_id", "prime_id", "prime_generation")),
                "PROMOTION_STALE_WORLDLINE")
            universe = self.state["universe"]
            self._genesis_decision(universe, "request_promotion")
            policy = self.state["evaluation_policy"]
            # Review C5: the protected Universe identity and admission head the evidence must
            # bind. Kept beside the promotion operation, whose shape the reviewed evaluation
            # record fixes at exactly five keys.
            self.state["promotion_protected_universe"] = protected_universe
            self.state["promotion_operation"] = {
                "promotionOperationId": (operation_id if gate_sourced
                                         else secrets.token_hex(32)),
                "creationOperationId": self.state["creation_operation"]["operationId"],
                "kind": "promote", "worldAlias": self.config["world_alias"],
                "expectedPrimeGeneration": policy["primeGeneration"],
            }
            self._save()
            evaluation, world = self._evaluation()
            self.state["promotion_binding"] = evaluation
            self.state["phase"] = "EVALUATION_BOUND"
            self._event("PROMOTION_EVALUATION_BOUND", {
                "digest": evaluation["binding"]["evaluationRecordDigest"],
                "promotion_binding_digest": evaluation["digest"]})
            args = {"world": self.config["world_alias"]}
            ticket = self._issue("collapse.prepare", args, observation, stage="PREPARE")
        prepared = self._daemon("collapse.prepare", {**args, "authorityTicket": ticket})
        require(prepared.get("decision") == "AUTHORIZED" and
                prepared.get("candidate_instance") == world["instance_id"] and
                prepared.get("candidate_content") == world["content_id"] and
                prepared.get("candidate_alias") == world["alias"] and
                prepared.get("current_prime") == policy["worldlineInstanceUuid"] and
                prepared.get("before_root") == world["base_root"] and
                prepared.get("candidate_root") ==
                self.state["evaluation"]["record"]["evaluation"]["candidateSnapshotRootSetHash"] and
                prepared.get("delta", {}).get("deltaHash") == world["delta_hash"] and
                not prepared.get("conflicts") and not prepared.get("contamination"),
                "PREPARED_FACTS_MISMATCH")
        with self.lock:
            self.state["transaction"] = {"id": prepared["transaction_id"], "phase": "PREPARED",
                                         "endpoint_generation": self.endpoint_generation,
                                         "prepared": prepared, "world_instance_id": world["instance_id"],
                                         "evaluation_digest": evaluation["binding"]["evaluationRecordDigest"],
                                         "promotion_operation_id":
                                         self.state["promotion_operation"]["promotionOperationId"],
                                         "promotion_binding_digest": evaluation["digest"]}
            self.state["phase"] = "PREPARED"
            self._event("PREPARED", {"transaction_id": prepared["transaction_id"]})
        if self.fault_hook("COSMOGONY_TEST_PREPARED_GATE") == "1":
            self._create_private_file(self.state_dir / "test-prepared-gate-entered",
                                      canonical({"transaction_id": prepared["transaction_id"]}))
            deadline = time.monotonic() + 30
            while not (self.state_dir / "test-prepared-gate-release").exists():
                require(time.monotonic() < deadline, "TEST_PREPARED_GATE_TIMEOUT")
                time.sleep(0.02)
        return self._authorize_commit()

    def abandon(self, operation_id: str) -> dict:
        """Review C1: durably close a gate operation the broker has not started.

        Serialized with promote and recover by the caller's transaction lock. It is refused
        unless the broker is at WORLD_VALID with no transaction, so an operation that is
        prepared or further along can never be abandoned; once recorded, a queued or replayed
        promote with this identity is refused.
        """
        with self.lock:
            require(self.config["promotion_operation_source"] == "root-intent-gate",
                    "ABANDON_REQUIRES_GATE")
            require(self.state["phase"] == "WORLD_VALID" and
                    self.state["transaction"] is None, "OPERATION_NOT_ABANDONABLE")
            closed = self.state.setdefault("abandoned_operations", [])
            if operation_id not in closed:
                closed.append(operation_id)
                self._event("PROMOTION_OPERATION_ABANDONED", {"operation_id": operation_id})
            return {"state": "ABANDONED", "operation_id": operation_id}

    def _test_refusal(self, point: str) -> None:
        """Review C4: a fault-laboratory refusal, so the gate's refusal paths actually run."""
        if self.fault_hook("COSMOGONY_TEST_BROKER_REFUSE") != point:
            return
        marker = self.state_dir / "test-refusal-marker.json"
        if not marker.exists():
            self._create_private_file(marker, canonical({
                "schema": "cosmogony.broker-test-refusal-v1", "point": point,
                "pid": os.getpid()}))
        raise Refusal("TEST_REFUSED_" + point.upper())

    def _protected_origin_facts(self) -> dict:
        launch_path = Path(self.state["evaluation_transaction_dir"]) / "launch.json"
        self._protected_path(launch_path, directory=False)
        launch = json.loads(launch_path.read_text())
        transaction = self.state["transaction"]
        prepared = transaction["prepared"]
        require(launch["operationId"] ==
                self.state["creation_operation"]["operationId"] and
                launch["missionId"] == self.mission_id,
                "PROTECTED_ORIGIN_LAUNCH_CHANGED")
        return {"admission_nonce": launch["admissionNonce"],
                "creation_operation_id": launch["operationId"],
                "promotion_operation_id": transaction["promotion_operation_id"],
                "candidate_instance": prepared["candidate_instance"],
                "candidate_content": prepared["candidate_content"],
                "mission_id": self.mission_id,
                "broker_phase": self.state["phase"],
                "commit_ticket_issued": any(
                    ticket["stage"] == "COMMIT" for ticket in
                    self.state["tickets"].values())}

    def _protected_origin(self, *, expected_digest: str | None = None,
                          committed: dict | None = None) -> dict:
        transaction_id = self.state["transaction"]["id"]
        return self.protected_evaluator.verify(
            transaction_id, self._protected_origin_facts(),
            expected_digest=expected_digest, committed=committed)

    def _protected_commit_intent(self, transaction_id: str, *, create: bool) -> dict:
        """Bind one accepted exchange to root-owned state before native commit."""
        transaction = self.state["transaction"]
        pending = self.canonical_store.state["pending"]
        require(self.state["phase"] == "AUTHORIZED" and
                transaction["id"] == transaction_id and
                pending is not None and pending["phase"] == "AUTHORIZED" and
                pending["transaction_id"] == transaction_id and
                transaction["prepared"]["staged_root"] == pending["staged_root"] and
                transaction["prepared"]["before_root"] == pending["before_root"],
                "PROTECTED_COMMIT_STATE_CHANGED")
        args_sha = digest(canonical({"transactionId": transaction_id}))
        tickets = [(token, ticket) for token, ticket in self.state["tickets"].items()
                   if ticket["operation"] == "collapse.commit" and
                   ticket["stage"] == "COMMIT" and
                   ticket["args_sha256"] == args_sha]
        require(len(tickets) == 1, "PROTECTED_COMMIT_TICKET_AMBIGUOUS")
        token, ticket = tickets[0]
        require(ticket["endpoint_generation"] ==
                transaction["endpoint_generation"] == self.endpoint_generation and
                ticket["policy_id"] == self.policy_id and
                ticket["policy_epoch"] == self.config["policy_epoch"],
                "PROTECTED_COMMIT_TICKET_CHANGED")
        universe = self.state["universe"]
        prepared = transaction["prepared"]
        record = {
            "schema": "cosmogony.authority-v1.protected-commit-intent",
            "transaction_id": transaction_id, "operation": "collapse.commit",
            "universe_id": universe["universe_id"],
            "mission_id": self.mission_id, "policy_id": self.policy_id,
            "policy_epoch": self.config["policy_epoch"],
            "requester_uid": self.config["orchestrator_uid"],
            "grant_sha256": digest(canonical(self.state["grants"])),
            "ticket_sha256": digest(token.encode()),
            "ticket_args_sha256": args_sha,
            "endpoint_generation": self.endpoint_generation,
            "candidate_instance": prepared["candidate_instance"],
            "candidate_content": prepared["candidate_content"],
            "candidate_root": prepared["candidate_root"],
            "before_generation": pending["before_generation"],
            "before_root": pending["before_root"],
            "staged_root": pending["staged_root"],
            "staged_manifest": pending["staged_manifest"],
            "copy_digest": pending["copy_digest"],
            "evaluation_digest": transaction["evaluation_digest"],
            "promotion_binding_digest": transaction["promotion_binding_digest"],
            "protected_origin_digest": transaction["protected_origin_digest"],
            "target_sha256": self.config["mission_spec"]["expected_sha256"],
        }
        if self.evidence_state is not None:
            evidence = transaction.get("evidence")
            require(type(evidence) is dict, "PROTECTED_COMMIT_EVIDENCE_MISSING")
            record.update({"evidence_id": evidence["evidence_id"],
                           "evidence_chain_head": evidence["chain_head"],
                           "evidence_binding_sha256": evidence["binding_sha256"]})
        raw = canonical(record)
        path = self.canonical_store.transactions / transaction_id / "commit-intent.json"
        if create and not path.exists():
            self._create_private_file(path, raw)
        self._protected_path(path, directory=False)
        info = path.lstat()
        require(stat.S_IMODE(info.st_mode) == 0o600 and info.st_nlink == 1 and
                path.read_bytes() == raw, "PROTECTED_COMMIT_INTENT_CHANGED")
        intent = {"path": str(path), "sha256": digest(raw), "record": record}
        if not create:
            require(transaction.get("commit_intent_digest") == intent["sha256"],
                    "PROTECTED_COMMIT_INTENT_NOT_JOURNALED")
        return intent

    def _authorize_commit(self) -> dict:
        with self.lock:
            require(self.state["phase"] == "PREPARED", "TRANSACTION_NOT_PREPARED")
            require(self.state["transaction"].get("endpoint_generation") ==
                    self.endpoint_generation, "TRANSACTION_ENDPOINT_GENERATION_CHANGED")
            observation, status, _raw_status = self._observation()
            grant = self.state["grant"]["observation"]
            require(all(observation[key] == grant[key] for key in (
                "worldline_instance_id", "root_set_id", "prime_id", "prime_generation")),
                "AUTHORIZATION_STALE_WORLDLINE")
            evaluation, world = self._evaluation()
            require(evaluation["binding"]["evaluationRecordDigest"] ==
                    self.state["transaction"]["evaluation_digest"] and
                    evaluation["binding"]["promotionOperationId"] ==
                    self.state["transaction"]["promotion_operation_id"] and
                    evaluation["binding"]["creationOperationId"] ==
                    self.state["creation_operation"]["operationId"] and
                    world["instance_id"] == self.state["transaction"]["world_instance_id"] and
                    self.state["transaction"]["prepared"]["candidate_root"] ==
                    self.state["evaluation"]["record"]["evaluation"]["candidateSnapshotRootSetHash"],
                    "AUTHORIZATION_EVALUATION_CHANGED")
            transaction_id = self.state["transaction"]["id"]
            require(len(status["prime"]["roots"]) == 1,
                    "CANONICAL_ROOT_SET_INVALID")
            self.canonical_store.stage(
                self.state["transaction"]["prepared"], prime=status["prime"],
                root_info=status["prime"]["roots"][0])
            self._test_refusal("after_stage")
            try:
                protected_origin = self.protected_evaluator.run(
                    transaction_id, self._protected_origin_facts())
            except CanonicalRefusal as exc:
                self._event("PROTECTED_ORIGIN_REFUSED", {
                    "transaction_id": transaction_id, "reason": str(exc)})
                raise
            self.state["transaction"]["protected_origin_digest"] = protected_origin["digest"]
            self._event("PROTECTED_ORIGIN_SEALED", {
                "transaction_id": transaction_id,
                "digest": protected_origin["digest"],
                "outcome": protected_origin["record"]["outcome"]})
            if self.evidence_state is not None:
                # Contract step 3: nothing is committable until the live examiner fact is
                # retained and bound to this promotion operation. A crash here is recovered by
                # resuming through this barrier, which then reuses the matching record.
                self.state["phase"] = "EVIDENCE_REQUIRED"
                self.state["transaction"]["phase"] = "EVIDENCE_REQUIRED"
                self._event("EVIDENCE_REQUIRED", {"transaction_id": transaction_id})
                bound = self._bind_live_evidence(transaction_id)
                if self.fault_hook("COSMOGONY_TEST_EVIDENCE_FAULT") == "after_append":
                    # Review F1: a root-owned marker proves which crash happened.
                    self._create_private_file(self.state_dir / "fault-marker.json", canonical({
                        "schema": "cosmogony.broker-fault-marker-v1",
                        "hook": "COSMOGONY_TEST_EVIDENCE_FAULT", "value": "after_append",
                        "exit_code": 77, "pid": os.getpid(),
                        "transaction_id": transaction_id}))
                    os._exit(77)
                self.state["transaction"]["evidence"] = bound
                self._event("EVIDENCE_BOUND", {"transaction_id": transaction_id, **bound})
            require(self.evidence_state is None or
                    type(self.state["transaction"].get("evidence")) is dict,
                    "EVIDENCE_BARRIER_NOT_PASSED")
            self.canonical_store.authorize(transaction_id)
            args = {"transactionId": transaction_id}
            ticket = self._issue("collapse.commit", args, observation, stage="COMMIT")
            self.state["phase"] = "AUTHORIZED"
            self.state["transaction"]["phase"] = "AUTHORIZED"
            self._event("AUTHORIZED", {"transaction_id": transaction_id,
                                       "evaluation_digest": evaluation["binding"]["evaluationRecordDigest"],
                                       "promotion_operation_id":
                                       evaluation["binding"]["promotionOperationId"]})
            intent = self._protected_commit_intent(transaction_id, create=True)
            self.state["transaction"]["commit_intent_digest"] = intent["sha256"]
            self._event("PROTECTED_COMMIT_INTENT_SEALED", {
                "transaction_id": transaction_id, "sha256": intent["sha256"]})
        # Composed step (e): the former test-only commit stop (COSMOGONY_TEST_COMMIT_GATE) is
        # removed; the evidence barrier above is the examination point before commit.
        result = self._daemon("collapse.commit", {**args, "authorityTicket": ticket})
        if self.fault_hook("COSMOGONY_TEST_NATIVE_EVENT_GATE") == "1":
            self._create_private_file(self.state_dir / "test-native-event-gate-entered",
                                      canonical({"transaction_id": transaction_id}))
            deadline = time.monotonic() + 30
            while not (self.state_dir / "test-native-event-gate-release").exists():
                require(time.monotonic() < deadline, "TEST_NATIVE_EVENT_GATE_TIMEOUT")
                time.sleep(0.02)
        check = self._commit_check(transaction_id)
        with self.lock:
            self.accepted_actuator.prepare(
                broker_state=self.state, broker_state_file=self.state_file,
                broker_config_file=self.config_path, check=check,
                protected_origin=self._protected_origin(
                    expected_digest=self.state["transaction"]["protected_origin_digest"]))
            if self.fault_hook("COSMOGONY_TEST_ACCEPTED_GATE") == "1":
                self._create_private_file(self.state_dir / "test-accepted-gate-entered",
                                          canonical({"transaction_id": transaction_id}))
                deadline = time.monotonic() + 30
                while not (self.state_dir / "test-accepted-gate-release").exists():
                    require(time.monotonic() < deadline, "TEST_ACCEPTED_GATE_TIMEOUT")
                    time.sleep(0.02)
            actuator_witness = self.accepted_actuator.exchange(transaction_id)
            if self.fault_hook("COSMOGONY_TEST_CRASH_AFTER_CANONICAL_PUBLISH") == "1":
                # Review F1: a root-owned marker proves which crash happened.
                self._create_private_file(self.state_dir / "fault-marker.json", canonical({
                    "schema": "cosmogony.broker-fault-marker-v1",
                    "hook": "COSMOGONY_TEST_CRASH_AFTER_CANONICAL_PUBLISH", "value": "1",
                    "exit_code": 73, "pid": os.getpid(), "transaction_id": transaction_id}))
                os._exit(73)
            canonical_after = self.canonical_store.record_actuated(
                transaction_id,
                worker_receipt_sha256=digest(canonical(check["selectedReceipt"])),
                actuator_witness_sha256=actuator_witness["sha256"])
            self.state["phase"] = "COMMITTED"
            self.state["transaction"]["phase"] = "COMMITTED"
            self.state["transaction"]["commit_result"] = result
            self._event("COMMITTED", {"transaction_id": transaction_id})
        return {"state": "COMMITTED", "transaction_id": transaction_id,
                "worker_commit_result": result, "canonical_prime": canonical_after,
                "accepted_actuator_witness": actuator_witness,
                "evaluation_digest": evaluation["binding"]["evaluationRecordDigest"]}

    def _bind_live_evidence(self, transaction_id: str) -> dict:
        """Append (or, when resuming, match) the one live examiner fact for this promotion.

        This replaces the slice-3 service's second broker Authority: the broker that holds
        the transaction builds the fact from its own state and sealed files, with the same
        checks, and the evidence ledger binds it to the promotion operation.
        """
        state = self.state
        transaction = state["transaction"]
        universe = state["universe"]
        origin = self._protected_origin(expected_digest=transaction["protected_origin_digest"])
        evaluation, world = self._evaluation()
        promotion = state["promotion_binding"]
        require(promotion["digest"] == transaction["promotion_binding_digest"] and
                promotion["binding"]["promotionOperationId"] ==
                transaction["promotion_operation_id"] and
                promotion["binding"]["worldInstanceId"] == transaction["world_instance_id"] and
                promotion["binding"]["worldContentId"] ==
                transaction["prepared"]["candidate_content"] and
                evaluation["binding"]["evaluationRecordDigest"] ==
                transaction["evaluation_digest"] and
                world["instance_id"] == transaction["world_instance_id"] and
                world["content_id"] == transaction["prepared"]["candidate_content"],
                "EVIDENCE_PROMOTION_BINDING_CHANGED")
        record = origin["record"]
        report_path = Path(record["report_path"])
        self._protected_path(report_path, directory=False)
        protected_report = report_path.read_bytes()
        private_report_path = Path(state["evaluation_transaction_dir"]) / "report.bin"
        self._protected_path(private_report_path, directory=False)
        private_report = private_report_path.read_bytes()
        require(digest(protected_report) == origin["report_sha256"] ==
                record["report_sha256"] and
                digest(private_report) ==
                state["evaluation"]["record"]["evaluation"]["rawReportSha256"] and
                record["outcome"] == "PASS" and
                record["verifier_sha256"] == self.config["protected_examiner_sha256"] and
                record["policy_sha256"] == digest(canonical(self.config["policy"])) and
                record["candidate_content"] == transaction["prepared"]["candidate_content"] and
                record["staged_root"] == transaction["prepared"]["staged_root"],
                "EVIDENCE_SEALED_RESULT_CHANGED")
        policy = self.config["evidence_policy"]
        binding = {
            "schema": "cosmogony.live-examiner-binding.v2",
            "broker_root": policy["broker_root"],
            "broker_config_sha256": file_sha(self.config_path),
            "broker_inventory_sha256": self.config["source_inventory_sha256"],
            "transaction_id": transaction_id,
            "promotion_operation_id": transaction["promotion_operation_id"],
            "protected_universe_id": state["promotion_protected_universe"]["universe_id"],
            "protected_universe_head": state["promotion_protected_universe"]["universe_head"],
            "universe_id": universe["universe_id"],
            "mission_id": self.mission_id, "policy_id": self.policy_id,
            "policy_epoch": self.config["policy_epoch"],
            "policy_sha256": record["policy_sha256"],
            "candidate_instance": record["candidate_instance"],
            "candidate_content": record["candidate_content"],
            "candidate_snapshot_root": record["staged_root"],
            "candidate_snapshot_manifest": record["staged_manifest"],
            "evaluation_digest": transaction["evaluation_digest"],
            "promotion_binding_digest": transaction["promotion_binding_digest"],
            "protected_origin_digest": origin["digest"],
            "protected_report_sha256": digest(protected_report),
            "protected_report_size": len(protected_report),
            "worldline_private_report_sha256": digest(private_report),
            "worldline_private_report_size": len(private_report),
            "verifier_sha256": self.config["protected_examiner_sha256"],
            "evaluator_run_id": record["run_id"],
        }

        def identity_of(value: str) -> str:
            selected = value.removeprefix("sha256:")
            require(len(selected) == 64 and selected != "0" * 64 and
                    all(letter in "0123456789abcdef" for letter in selected),
                    "EVIDENCE_IDENTITY_INVALID")
            return selected

        fact = {
            "requirementId": digest(b"COSMOGONY-LIVE-EXAMINER-REQUIREMENT-v1\x00" +
                                    self.evidence_canonical({
                                        "mission_id": self.mission_id,
                                        "policy_id": self.policy_id,
                                        "verifier_sha256": binding["verifier_sha256"]})),
            "evaluationId": identity_of(binding["evaluation_digest"]),
            "universeId": identity_of(binding["protected_universe_id"]),
            "worldId": identity_of(binding["candidate_content"]),
            "candidateId": identity_of(binding["candidate_snapshot_root"]),
            "policyId": identity_of(binding["policy_id"]),
            "policyEpoch": binding["policy_epoch"],
            "verifierId": identity_of(binding["verifier_sha256"]),
            "executionId": identity_of(binding["evaluator_run_id"]),
            "observationSource": "examiner", "executionState": "PERFORMED",
            "outcome": "PASS", "complete": True, "assumptions": [],
            "nonClaims": ["A sealed evaluator observation is not actuation permission."],
        }
        protected = self.evidence_protected
        try:
            with protected.ProtectedEvidence(self.evidence_state) as evidence:
                rows = evidence.read()["rows"]
                if rows:
                    # A resumed barrier: the one retained live row must be this fact, bound
                    # to this binding (the ledger authenticated live-binding.json on open).
                    live = json.loads((self.evidence_state / "live-binding.json").read_bytes())
                    require(len(rows) == 1 and rows[0]["fact"] == fact and
                            live["binding"] == binding, "EVIDENCE_BINDING_CONFLICT")
                    appended = {"evidenceId": rows[0]["evidenceId"],
                                "chainHash": rows[0]["chainHash"]}
                else:
                    appended = evidence.append(fact, evidence.head()["chain_head"],
                                               "examiner", live_binding=binding)
        except protected.EvidenceAuthorityError as exc:
            raise Refusal("EVIDENCE_LEDGER_REFUSED") from exc
        return {"evidence_id": appended["evidenceId"], "chain_head": appended["chainHash"],
                "binding_sha256": digest(self.evidence_canonical(binding))}

    def _commit_check(self, transaction_id: str) -> dict:
        intent = self._protected_commit_intent(transaction_id, create=False)
        commits = [event for event in self.state["events"]
                   if event["kind"] == "ACTUATOR_BROKER_COMMITTED" and
                   event["facts"].get("transaction_id") == transaction_id]
        require(len(commits) == 1, "PROTECTED_NATIVE_COMMIT_EVENT_MISSING")
        shown = self._daemon("transaction.show", {"transactionId": transaction_id})
        require(shown.get("state") == "COMMITTED" and
                shown.get("candidateWorld") == self.state["world"]["instanceId"] and
                shown.get("candidateContent") == self.state["world"]["id"],
                "COMMITTED_TRANSACTION_MISMATCH")
        _observation, status, _raw_status = self._observation()
        prime = status["prime"]
        require(prime["generation"] == transaction_id and
                prime["dirty"] is False and prime["state"] == "VALID",
                "COMMITTED_PRIME_MISMATCH")
        root = Path(self.config["managed_root"])
        backing = root.resolve(strict=True)
        store = Path(self.config["daemon_data_root"]).resolve(strict=True)
        require(backing.is_relative_to(store), "COMMITTED_LIVE_BACKING_MISMATCH")
        require(len(prime["roots"]) == 1 and prime["roots"][0]["path"] == str(root),
                "COMMITTED_ROOT_SET_MISMATCH")
        root_info = prime["roots"][0]
        captured = Manifest.capture(backing, logical_root=root,
                                    root_key=root_info["rootKey"], kind=root_info["kind"],
                                    core=Core.shared())
        full_root = Manifest.root_set_hash((captured,), Core.shared())
        prepared = self.state["transaction"]["prepared"]
        require(captured.root_hash == root_info["manifestRoot"] and
                full_root == prepared["staged_root"] and
                shown["stagedRoot"] == full_root,
                "COMMITTED_FULL_ROOT_MISMATCH")
        target = root / self.config["mission_spec"]["target"]
        require(digest(target.read_bytes()) == self.config["mission_spec"]["expected_sha256"],
                "COMMITTED_LIVE_BYTES_MISMATCH")
        verified = self._daemon("log", {"verify": True})
        receipts = [receipt for receipt in verified.get("receipts", []) if
                    type(receipt) is dict and receipt.get("transactionId") == transaction_id]
        require(len(receipts) == 1 and receipts[0].get("afterRoot") == full_root,
                "COMMITTED_RECEIPT_MISSING")
        return {"transaction": shown, "prime": prime,
                "liveBacking": str(backing), "liveSha256": digest(target.read_bytes()),
                "fullRoot": full_root, "capturedManifestRoot": captured.root_hash,
                "logVerify": verified, "selectedReceipt": receipts[0],
                "protectedIntent": intent,
                "nativeCompletionSource": "ROOT_BROKER_ACTUATOR_EVENT"}

    def _recover_accepted_effect(self, transaction_id: str) -> dict | None:
        """Reconcile a sealed native effect without asking the daemon for new facts.

        The protected config is written last during actuator preparation. Its
        absence means this path was never ready to invoke the native service.
        """
        transaction, actuator_state, _ingress = self.accepted_actuator.paths(transaction_id)
        binding_path = transaction / "config.json"
        if not binding_path.exists():
            return None
        intent_path = transaction / "commit-intent.json"
        for path in (binding_path, intent_path,
                     transaction / "selected-receipt.json",
                     transaction / "broker-state-before.json",
                     transaction / "canonical-state-before.json",
                     actuator_state / "authority.bin"):
            self._protected_path(path, directory=False)
            info = path.lstat()
            require(stat.S_IMODE(info.st_mode) == 0o600 and info.st_nlink == 1,
                    "ACCEPTED_RECOVERY_RECORD_UNPROTECTED")
        binding = json.loads(binding_path.read_text())
        require(binding.get("schema") == "cosmogony.accepted-actuator-binding.v1" and
                binding.get("transaction_id") == transaction_id and
                binding.get("broker_state_path") == str(self.state_file) and
                binding.get("broker_state_before_path") ==
                str(transaction / "broker-state-before.json") and
                binding.get("canonical_state_path") ==
                str(self.canonical_store.state_path) and
                binding.get("canonical_state_before_path") ==
                str(transaction / "canonical-state-before.json") and
                binding.get("selected_receipt_path") ==
                str(transaction / "selected-receipt.json") and
                binding.get("protected_commit_intent_path") == str(intent_path) and
                binding.get("protected_commit_intent_sha256") ==
                file_sha(intent_path) and
                binding.get("native_completion_source") ==
                "ROOT_BROKER_ACTUATOR_EVENT" and
                binding.get("selected_receipt_source") ==
                "SEALED_DAEMON_OBSERVATION" and
                binding.get("accepted_authority_path") ==
                str(actuator_state / "authority.bin") and
                binding.get("broker_config_sha256") == file_sha(self.config_path) and
                binding.get("library_sha256") ==
                file_sha(self.accepted_actuator.library) and
                binding.get("broker_state_sha256") ==
                file_sha(transaction / "broker-state-before.json") and
                binding.get("canonical_state_sha256") ==
                file_sha(transaction / "canonical-state-before.json") and
                binding.get("accepted_authority_sha256") ==
                file_sha(actuator_state / "authority.bin"),
                "ACCEPTED_RECOVERY_BINDING_CHANGED")
        protected_origin = self._protected_origin(
            expected_digest=binding.get("protected_origin_sha256"),
            committed=binding if self.canonical_store.state["pending"] is None else None)
        require(binding.get("protected_origin_path") == protected_origin["path"] and
                binding.get("protected_report_sha256") ==
                protected_origin["report_sha256"] and
                self.state["transaction"].get("protected_origin_digest") ==
                protected_origin["digest"],
                "ACCEPTED_RECOVERY_ORIGIN_CHANGED")
        selected = (transaction / "selected-receipt.json").read_bytes()
        receipt = json.loads(selected)
        require(binding.get("selected_receipt_sha256") == digest(selected) and
                receipt.get("transactionId") == transaction_id and
                receipt.get("afterRoot") == binding.get("staged_root"),
                "ACCEPTED_RECOVERY_RECEIPT_CHANGED")
        prepared = self.state["transaction"]["prepared"]
        require(prepared["transaction_id"] == transaction_id and
                self.state["transaction"].get("commit_intent_digest") ==
                binding["protected_commit_intent_sha256"] and
                len([event for event in self.state["events"]
                     if event["kind"] == "ACTUATOR_BROKER_COMMITTED" and
                     event["facts"].get("transaction_id") == transaction_id]) == 1 and
                prepared["before_root"] == binding.get("before_root") and
                prepared["staged_root"] == binding.get("staged_root") and
                self.state["transaction"]["evaluation_digest"] ==
                binding.get("evaluation_digest") and
                self.state["transaction"]["promotion_binding_digest"] ==
                binding.get("promotion_binding_digest"),
                "ACCEPTED_RECOVERY_TRANSACTION_CHANGED")
        if self.state["phase"] == "AUTHORIZED":
            require(file_sha(self.state_file) == binding["broker_state_sha256"],
                    "ACCEPTED_RECOVERY_BROKER_CHANGED")
        canonical_state = self.canonical_store.state
        if canonical_state["last_transaction"] == transaction_id:
            require(canonical_state["phase"] == "COMMITTED" and
                    canonical_state["generation"] == transaction_id and
                    canonical_state["root_set_hash"] == binding["staged_root"],
                    "ACCEPTED_RECOVERY_CANONICAL_CHANGED")
        else:
            pending = canonical_state["pending"]
            require(pending is not None and pending["phase"] == "AUTHORIZED" and
                    pending["transaction_id"] == transaction_id and
                    pending["before_root"] == binding["before_root"] and
                    pending["staged_root"] == binding["staged_root"] and
                    file_sha(self.canonical_store.state_path) ==
                    binding["canonical_state_sha256"],
                    "ACCEPTED_RECOVERY_CANONICAL_CHANGED")
        native_phase = self.accepted_actuator.recover(transaction_id)
        if native_phase == "NO_TRANSACTION":
            require(self.state["phase"] == "AUTHORIZED" and
                    canonical_state["last_transaction"] != transaction_id,
                    "ACCEPTED_COMMITTED_EFFECT_MISSING")
            return None
        require(native_phase in ("COMMITTED", "RECOVERED_COMMITTED"),
                "ACCEPTED_ACTUATOR_RECOVERY_STOPPED")
        witness = self.accepted_actuator.witness(transaction_id)
        canonical_after = self.canonical_store.record_actuated(
            transaction_id, worker_receipt_sha256=digest(selected),
            actuator_witness_sha256=witness["sha256"])
        if self.state["phase"] != "COMMITTED":
            self.state["phase"] = "COMMITTED"
            self.state["transaction"]["phase"] = "COMMITTED"
            self._event("RECOVERED_COMMITTED", {"transaction_id": transaction_id,
                                                "source": "PROTECTED_ACCEPTED_WITNESS"})
        return {"state": "COMMITTED", "transaction_id": transaction_id,
                "recovered": True, "recovery_source": "PROTECTED_ACCEPTED_WITNESS",
                "protected_selected_receipt": receipt,
                "canonical_prime": canonical_after,
                "accepted_actuator_witness": witness}

    def recover(self) -> dict:
        with self.lock:
            phase = self.state["phase"]
            if phase == "COMMITTED":
                recovered = self._recover_accepted_effect(self.state["transaction"]["id"])
                require(recovered is not None, "ACCEPTED_ACTUATOR_NOT_COMMITTED")
                return recovered
            require(phase in ("PREPARED", "EVIDENCE_REQUIRED", "AUTHORIZED"),
                    "NOTHING_RECOVERABLE")
            transaction_id = self.state["transaction"]["id"]
            if phase == "AUTHORIZED":
                recovered = self._recover_accepted_effect(transaction_id)
                if recovered is not None:
                    return recovered
        shown = self._daemon("transaction.show", {"transactionId": transaction_id})
        if phase == "PREPARED" and shown.get("state") == "ABORTED":
            with self.lock:
                transaction = self.state["transaction"]
                prepared = transaction["prepared"]
                require(self.state["phase"] == "PREPARED" and
                        transaction["id"] == transaction_id and
                        transaction["phase"] == "PREPARED" and
                        not transaction.get("protected_origin_digest") and
                        shown.get("recordReadable") is True and
                        shown.get("transactionId") == transaction_id and
                        shown.get("kind") == "collapse" and
                        shown.get("decision") == "AUTHORIZED" and
                        shown.get("error") ==
                        {"code": "RECOVERED_BEFORE_ACTUATOR"} and
                        shown.get("candidateWorld") ==
                        transaction["world_instance_id"] and
                        shown.get("candidateAlias") ==
                        prepared["candidate_alias"] and
                        shown.get("candidateContent") ==
                        prepared["candidate_content"] and
                        shown.get("candidateRoot") ==
                        prepared["candidate_root"] and
                        shown.get("currentPrime") ==
                        prepared["current_prime"] and
                        shown.get("deltaHash") ==
                        prepared["delta"]["deltaHash"] and
                        shown.get("beforeRoot") == prepared["before_root"] and
                        shown.get("stagedRoot") == prepared["staged_root"],
                        "PREPARED_ABORT_NATIVE_RECORD_MISMATCH")
                grant = self.state["grant"]["observation"]
                canonical_before = self.canonical_store.certify_prepared_abort(
                    transaction_id,
                    expected_generation=grant["prime_generation"],
                    expected_root=prepared["before_root"])
                history = self.state.setdefault("transaction_history", [])
                require(not any(row.get("id") == transaction_id for row in history),
                        "PREPARED_ABORT_ALREADY_RECONCILED")
                transaction["phase"] = "REFUSED"
                transaction["refusal_code"] = "RECOVERED_BEFORE_ACTUATOR"
                history.append(transaction)
                for ticket in self.state["tickets"].values():
                    ticket["used"] = True
                self.state["transaction"] = None
                self.state["promotion_operation"] = None
                self.state["promotion_protected_universe"] = None
                self.state["promotion_binding"] = None
                self.state["phase"] = "WORLD_VALID"
                try:
                    self._event("PREPARED_ABORT_RECONCILED", {
                        "transaction_id": transaction_id,
                        "native_error": "RECOVERED_BEFORE_ACTUATOR",
                        "canonical_generation": canonical_before["generation"],
                        "canonical_root": canonical_before["root_set_hash"],
                        "accepted_artifacts": "ABSENT"})
                except Exception:
                    # An interrupted durable write may have installed either state.
                    # Stop serving until startup reloads the authoritative file.
                    os._exit(75)
                return {"state": "REFUSED", "transaction_id": transaction_id,
                        "reason": "RECOVERED_BEFORE_ACTUATOR",
                        "fresh_promotion_request_allowed": True,
                        "canonical_prime": canonical_before}
        if shown.get("state") == "COMMITTED":
            check = self._commit_check(transaction_id)
            with self.lock:
                self.canonical_store.authorize(transaction_id)
                state = self.canonical_store.actuator / transaction_id
                if not (self.canonical_store.transactions / transaction_id /
                        "config.json").is_file():
                    self.accepted_actuator.prepare(
                        broker_state=self.state, broker_state_file=self.state_file,
                        broker_config_file=self.config_path, check=check,
                        protected_origin=self._protected_origin(
                            expected_digest=self.state["transaction"]["protected_origin_digest"]))
                native_phase = self.accepted_actuator.recover(transaction_id)
                if native_phase == "NO_TRANSACTION":
                    actuator_witness = self.accepted_actuator.exchange(transaction_id)
                else:
                    require(native_phase in ("COMMITTED", "RECOVERED_COMMITTED"),
                            "ACCEPTED_ACTUATOR_RECOVERY_STOPPED")
                    actuator_witness = self.accepted_actuator.witness(transaction_id)
                canonical_after = self.canonical_store.record_actuated(
                    transaction_id,
                    worker_receipt_sha256=digest(canonical(check["selectedReceipt"])),
                    actuator_witness_sha256=actuator_witness["sha256"])
                self.state["phase"] = "COMMITTED"
                self.state["transaction"]["phase"] = "COMMITTED"
                self._event("RECOVERED_COMMITTED", {"transaction_id": transaction_id})
            return {"state": "COMMITTED", "transaction_id": transaction_id,
                    "recovered": True, "worker_reconciliation": check,
                    "canonical_prime": canonical_after}
        if (phase in ("PREPARED", "EVIDENCE_REQUIRED", "AUTHORIZED") and
                shown.get("state") in ("PREPARED", "AUTHORIZED")):
            with self.lock:
                # The daemon owns this native phase claim. Once root-owned commit
                # progress exists, it cannot cause another authorization attempt.
                transaction = self.state["transaction"]
                pending = self.canonical_store.state["pending"]
                commit_args_sha = digest(canonical({"transactionId": transaction_id}))
                intent_path = (self.canonical_store.transactions / transaction_id /
                               "commit-intent.json")
                try:
                    intent_path.lstat()
                    intent_exists = True
                except FileNotFoundError:
                    intent_exists = False
                native_request_started = any(
                    event["kind"] in ("ACTUATOR_BROKER_REQUEST",
                                      "ACTUATOR_BROKER_COMMITTED") and
                    event["facts"].get("transaction_id") == transaction_id
                    for event in self.state["events"])
                commit_ticket_consumed = any(
                    ticket["stage"] == "COMMIT" and ticket["used"] is True and
                    ticket["args_sha256"] == commit_args_sha
                    for ticket in self.state["tickets"].values())
                require(not (phase == "AUTHORIZED" or
                             transaction.get("commit_intent_digest") or
                             intent_exists or native_request_started or
                             commit_ticket_consumed or
                             (pending is not None and
                              pending["transaction_id"] == transaction_id and
                              pending["phase"] == "AUTHORIZED")),
                        "PROTECTED_COMMIT_REISSUE_REFUSED")
                if self.state["transaction"].get("endpoint_generation") != self.endpoint_generation:
                    observation, _status, _raw = self._observation()
                    grant = self.state["grant"]["observation"]
                    require(all(observation[key] == grant[key] for key in (
                        "worldline_instance_id", "root_set_id", "prime_id",
                        "prime_generation")), "RESEALED_RECOVERY_STALE_WORLDLINE")
                    previous = self.state["transaction"]["endpoint_generation"]
                    self.state["transaction"]["endpoint_generation"] = self.endpoint_generation
                    self._event("ENDPOINT_RESEALED_FOR_EXPLICIT_RECOVERY", {
                        "transaction_id": transaction_id,
                        "previous_generation": previous,
                        "current_generation": self.endpoint_generation})
                if phase == "AUTHORIZED":
                    for ticket in self.state["tickets"].values():
                        if ticket["stage"] == "COMMIT":
                            ticket["used"] = True
                self.state["phase"] = "PREPARED"
                self._save()
            result = self._authorize_commit()
            return {**result, "recovered": True}
        raise Refusal("PREPARED_NOT_AUTHORIZED_RECOVERY_REFUSED")

    def public_state(self) -> dict:
        with self.lock:
            canonical_prime = (None if self.canonical_store.state["phase"] == "EMPTY"
                               else self.canonical_store.current())
            return {"phase": self.state["phase"],
                    "mission_id": self.mission_id, "policy_id": self.policy_id,
                    "universe_id": None if self.state["universe"] is None else self.state["universe"]["universe_id"],
                    "world_instance_id": None if self.state["world"] is None else self.state["world"].get("instanceId"),
                    "transaction_id": None if self.state["transaction"] is None else self.state["transaction"]["id"],
                    "canonical_prime": canonical_prime,
                    "release_gate": "BLOCKED"}

    def public_health(self) -> dict:
        """Readiness without asking a pending native exchange to look committed."""
        record = daemon_endpoint.read_seal(
            self.config, generation=self.endpoint_generation)
        daemon_endpoint.check_entry(self.config, record)
        daemon_endpoint.check_process(record)
        return {"state": "RUNNING", "broker_phase": self.state["phase"],
                "endpoint_generation": self.endpoint_generation,
                "release_gate": "BLOCKED"}


class Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        self.connection.settimeout(3)
        peer_pid, peer_uid, _peer_gid = struct.unpack(
            "3i", self.connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
        try:
            authority: Authority = self.server.authority  # type: ignore[attr-defined]
            require(peer_uid in (authority.config["daemon_uid"],
                                 authority.config["orchestrator_uid"]),
                    "PEER_PRINCIPAL_REFUSED")
            raw = self.rfile.readline(65536)
            require(bool(raw) and len(raw) < 65536, "REQUEST_TOO_LARGE")
            value = json.loads(raw.decode("utf-8", "strict"))
            require(type(value) is dict, "REQUEST_INVALID")
            operation = value.get("op")
            if operation == "redeem":
                require(peer_uid == authority.config["daemon_uid"],
                        "DAEMON_PRINCIPAL_REQUIRED")
                with authority.lock:
                    result = authority.redeem(value, peer_uid=peer_uid, peer_pid=peer_pid)
            elif operation == "actuator_request":
                require(peer_uid == authority.config["daemon_uid"],
                        "DAEMON_PRINCIPAL_REQUIRED")
                with authority.lock:
                    result = authority.actuator_request(value, peer_uid=peer_uid,
                                                        peer_pid=peer_pid)
            elif operation == "health":
                require(set(value) == {"op"}, "INTENT_ONLY_API")
                result = authority.public_health()
            else:
                if (operation in ("promote", "abandon") and
                        authority.config["promotion_operation_source"] == "root-intent-gate"):
                    # Review C5: with an evidence ledger, promote also names the protected
                    # Universe and the admission head the evidence must bind.
                    fields = ({"op", "operation_id", "universe_id", "universe_head"}
                              if operation == "promote" and
                              authority.config["evidence_state"] is not None
                              else {"op", "operation_id"})
                    require(set(value) == fields and all(
                        type(value[name]) is str and len(value[name]) == 64 and
                        all(character in "0123456789abcdef" for character in value[name])
                        for name in fields - {"op"}), "INTENT_ONLY_API")
                else:
                    require(set(value) == {"op"}, "INTENT_ONLY_API")
                authority.grant_for(peer_uid, operation)
                if operation == "create_world":
                    result = authority.create_world()
                elif operation == "promote":
                    with authority.transaction_lock:
                        result = authority.promote(
                            value.get("operation_id"),
                            None if "universe_id" not in value else
                            {"universe_id": value["universe_id"],
                             "universe_head": value["universe_head"]})
                elif operation == "abandon":
                    with authority.transaction_lock:
                        result = authority.abandon(value["operation_id"])
                elif operation == "recover":
                    with authority.transaction_lock:
                        result = authority.recover()
                elif operation == "state":
                    result = authority.public_state()
                else:
                    raise Refusal("UNKNOWN_INTENT")
        except (Refusal, CanonicalRefusal, daemon_endpoint.EndpointRefusal) as exc:
            result = {"state": "REFUSED", "code": str(exc)}
        except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            result = {"state": "REFUSED", "code": "PROTECTED_SERVICE_INPUT_OR_IO"}
        self.wfile.write(canonical(result) + b"\n")


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.slots = threading.BoundedSemaphore(16)
        super().__init__(*args, **kwargs)

    def process_request(self, request: socket.socket, client_address: Any) -> None:
        if not self.slots.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request: socket.socket, client_address: Any) -> None:
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: authority_service.py ROOT_OWNED_CONFIG")
    config_path = Path(sys.argv[1])
    lock_path = config_path.parent / "state/broker.lock"
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW,
                      0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        raise SystemExit("BROKER_ALREADY_RUNNING") from exc
    authority = Authority(config_path)
    broker_identity = authority.state_dir / "broker-identity.json"
    _parent, started, _state = daemon_endpoint.process_identity(os.getpid())
    identity_record = {"schema": "cosmogony.authority-v1.broker-process",
                       "pid": os.getpid(), "start_ticks": started,
                       "endpoint_generation": authority.endpoint_generation,
                       "service_source_sha256": file_sha(Path(__file__))}
    temporary_identity = authority.state_dir / ("broker-identity." + secrets.token_hex(8))
    fd = os.open(temporary_identity, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(canonical(identity_record) + b"\n")
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary_identity, broker_identity)
    directory_fd = os.open(authority.state_dir, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    path = Path(authority.config["service_socket"])
    parent = path.parent.lstat()
    require(parent.st_uid == 0 and stat.S_ISDIR(parent.st_mode) and
            stat.S_IMODE(parent.st_mode) == 0o711,
            "SERVICE_SOCKET_PARENT_UNTRUSTED")
    if path.exists():
        require(stat.S_ISSOCK(path.lstat().st_mode) and path.lstat().st_uid == 0,
                "SERVICE_SOCKET_REPLACED")
        path.unlink()
    with Server(str(path), Handler) as server:
        server.authority = authority
        os.chmod(path, 0o666)
        server.serve_forever(poll_interval=0.05)


if __name__ == "__main__":
    main()
