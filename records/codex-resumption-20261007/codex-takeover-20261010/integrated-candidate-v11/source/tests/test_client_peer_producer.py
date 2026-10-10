"""Additive actual-kernel controls. Authorship does not claim these were run."""
from __future__ import annotations

import asyncio
import ctypes
import json
import os
import socket
from pathlib import Path
import tempfile
import unittest

from worldline.client_peer import (
    KernelPeer, RequestPeer, UCRED, current_observation, current_peer,
    decode_credentials, request_scope, preparer_observations,
)
from worldline.client_peer_relay import receive_request_peer, send_request_peer
from worldline.daemon import RequestContext, WorldlineDaemon
from worldline.errors import WorldlineError


class Writer:
    def __init__(self, connection):
        self.connection = connection

    def get_extra_info(self, name):
        return self.connection if name == "socket" else None


class KernelProducerTests(unittest.TestCase):
    def setUp(self):
        self.left, self.right = socket.socketpair()
        self.request = RequestPeer.capture(
            Writer(self.left), line=b'{"id":"original","op":"collapse.prepare","args":{}}\n',
            operation="collapse.prepare", request_id="original")

    def tearDown(self):
        self.request.close()
        self.left.close()
        self.right.close()

    def test_complete_actual_kernel_and_detached_duplicate(self):
        raw = self.left.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, UCRED.size)
        observation = self.request.observation()
        self.assertEqual(observation["peer"]["rawUcred"], raw.hex())
        self.assertEqual(decode_credentials(raw), (os.getpid(), os.getuid(), os.getgid()))
        duplicate = self.request.duplicate()
        try:
            self.request.close()
            self.left.close()
            self.right.close()
            self.assertEqual(duplicate.observation(), observation)
            self.assertFalse(os.get_inheritable(duplicate.peer.descriptor()))
        finally:
            duplicate.close()

    def test_unsigned_native_credentials_are_not_signed_or_narrowed(self):
        # Native unsigned representation, not an invented signed UID ceiling.
        uid = ctypes.c_uint(-1).value
        raw = UCRED.pack(os.getpid(), uid, uid)
        self.assertEqual(decode_credentials(raw), (os.getpid(), uid, uid))

    def test_preparer_join_preserves_same_uid_new_connection(self):
        preparer = self.request.observation()
        fresh_left, fresh_right = socket.socketpair()
        fresh = RequestPeer.capture(Writer(fresh_left), line=b'{"id":"commit","op":"collapse.commit","args":{}}\n',
                                    operation="collapse.commit", request_id="commit")
        try:
            with request_scope(fresh):
                pair = preparer_observations({"preparerPeer": preparer})
                self.assertEqual(pair, {"preparer": preparer, "requester": fresh.observation()})
                self.assertEqual(pair["preparer"]["peer"]["uid"], pair["requester"]["peer"]["uid"])
            self.assertEqual(preparer_observations({"preparerPeer": preparer}),
                             {"preparer": preparer, "requester": None})
            self.assertEqual(preparer_observations({"preparerPeer": None}),
                             {"preparer": None, "requester": None})
        finally:
            fresh.close()
            fresh_left.close()
            fresh_right.close()

    def test_dto_alone_cannot_replace_actual_peer(self):
        document = self.request.observation()
        document["peer"]["uid"] = None
        with self.assertRaises(WorldlineError) as refused:
            RequestPeer(self.request.peer, document)
        self.assertEqual(refused.exception.code, "PREPARER_PEER_MALFORMED")

    def test_same_uid_new_actual_process_preserves_original_acceptance_domain(self):
        preparer = self.request.observation()
        with tempfile.TemporaryDirectory(prefix="worldline-peer-new-process-") as directory:
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.settimeout(5)
            endpoint = str(Path(directory) / "original.sock")
            server.bind(endpoint)
            server.listen()
            child = os.fork()
            if child == 0:
                server.close()
                transport = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                try:
                    transport.settimeout(5)
                    transport.connect(endpoint)
                    transport.sendall(b"ready")
                    transport.recv(1)
                    os._exit(0)
                except BaseException:
                    os._exit(1)
            connection = None
            fresh = None
            try:
                connection, _address = server.accept()
                fresh = RequestPeer.capture(Writer(connection),
                    line=b'{"id":"new-process","op":"collapse.commit","args":{}}\n',
                    operation="collapse.commit", request_id="new-process")
                with request_scope(fresh):
                    pair = preparer_observations({"preparerPeer": preparer})
                self.assertEqual(pair["requester"]["peer"]["pid"], child)
                self.assertNotEqual(pair["preparer"]["peer"]["pid"], child)
                self.assertEqual(pair["preparer"]["peer"]["uid"], pair["requester"]["peer"]["uid"])
                connection.sendall(b"x")
            finally:
                if fresh is not None:
                    fresh.close()
                if connection is not None:
                    connection.close()
                server.close()
                waited, status = os.waitpid(child, 0)
                self.assertEqual(waited, child)
                self.assertEqual(os.waitstatus_to_exitcode(status), 0)

    def test_actual_scm_rights_round_trip_recaptures_original_fd(self):
        sender, receiver = socket.socketpair()
        original = self.request.observation()
        try:
            send_request_peer(sender, self.request)
            received = receive_request_peer(receiver, expected_daemon_uid=os.getuid(),
                                            frame_limit=len(json.dumps(original).encode()) + UCRED.size)
            try:
                self.assertEqual(received.observation(), original)
                self.request.close()
                self.assertEqual(received.observation(), original)
            finally:
                received.close()
        finally:
            sender.close()
            receiver.close()


class ScopedProducerTests(unittest.IsolatedAsyncioTestCase):
    async def test_thread_propagation_and_background_retained_descriptor(self):
        left, right = socket.socketpair()
        request = RequestPeer.capture(Writer(left), line=b'{"id":"ghost","op":"ghost.run","args":{}}\n',
                                      operation="ghost.run", request_id="ghost")
        expected = request.observation()
        gate = asyncio.Event()
        class Publisher:
            def publish(self):
                pass
        daemon = WorldlineDaemon(None, None, Publisher())
        async def action():
            await gate.wait()
            return await asyncio.to_thread(current_observation)
        try:
            with request_scope(request):
                self.assertEqual(await asyncio.to_thread(current_observation), expected)
                task = daemon.spawn_background("peer-control", action())
            request.close()
            left.close()
            right.close()
            gate.set()
            self.assertEqual(await task, expected)
            self.assertIsNone(current_peer())
        finally:
            request.close()
            left.close()
            right.close()

    async def test_request_context_legacy_constructor_preserves_absence(self):
        async def progress(*_args):
            pass
        context = RequestContext(None, "fixture", progress)
        self.assertIsNone(context.peer_uid)
        self.assertIsNone(context.peer)
        with self.assertRaises(WorldlineError) as missing:
            context.retain_peer()
        self.assertEqual(missing.exception.code, "PEER_CREDENTIALS_UNAVAILABLE")


class DurableDispatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_complete_observation_precedes_real_handler_and_survives_reopen(self):
        from worldline.client import DaemonClient
        from worldline.core import Core
        from worldline.paths import WorldlinePaths
        from worldline.status import StatusPublisher
        from worldline.store import StateStore
        with tempfile.TemporaryDirectory(prefix="worldline-original-peer-") as directory:
            root = Path(directory)
            environment = {name: str(root / name) for name in (
                "HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR")}
            for path in environment.values():
                Path(path).mkdir(mode=0o700)
            paths = WorldlinePaths.from_environment(environment)
            core = Core.shared()
            store = StateStore(paths, core)
            publisher = StatusPublisher(paths, store, lambda: {"overlay": {"state": "UNASSESSED"}})
            daemon = WorldlineDaemon(paths, store, publisher)
            witnessed = []
            def handler(_args, context):
                observation = current_observation()
                self.assertEqual(store.client_request_observations()[-1], observation)
                self.assertEqual(context.peer_uid, observation["peer"]["uid"])
                witnessed.append(observation)
                return {"retained": observation["observationId"]}
            def refusal(_args, _context):
                self.assertEqual(store.client_request_observations()[-1], current_observation())
                raise WorldlineError("CONTROL_REFUSAL", "observation survives refusal")
            daemon.register("peer.control", handler, mutating=True)
            daemon.register("peer.refusal", refusal, mutating=True)
            await daemon.start()
            try:
                client = DaemonClient(paths)
                await asyncio.to_thread(client.request, "peer.control")
                with self.assertRaises(WorldlineError):
                    await asyncio.to_thread(client.request, "peer.refusal")
                roster = store.client_request_observations()
                self.assertEqual(roster[0], witnessed[0])
                self.assertEqual([item["operation"] for item in roster], ["peer.control", "peer.refusal"])
                for item in roster:
                    parsed = json.loads(bytes.fromhex(item["rawRequest"]))
                    self.assertEqual(parsed["op"], item["operation"])
                    self.assertEqual(parsed["id"], item["requestId"])
            finally:
                await daemon.stop()
                store.close()
            reopened = StateStore(paths, core)
            try:
                self.assertEqual(reopened.client_request_observations(), roster)
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
