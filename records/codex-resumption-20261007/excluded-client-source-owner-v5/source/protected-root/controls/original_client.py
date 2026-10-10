"""Selected disposable client: send exact original bytes as the real actor UID.

The root operator selects the actor and raw original requests before dropping
credentials permanently. This is a socket producer, never an authority adapter.
"""
from __future__ import annotations
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('CLIENT_EARLY_APPROVED_SOURCE_REQUIRED')
_lease = _approved.current()
_lease.check()
import argparse
import json
import os
from pathlib import Path
import socket
import struct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    args = parser.parse_args()
    record = json.loads(_lease.file(args.request, ('DATA',)))
    if set(record) != {'schema', 'uid', 'gid', 'groups', 'endpoint', 'requests', 'timeout', 'disconnect'}:
        raise RuntimeError('CLIENT_EXACT_ORIGINAL_ACTOR_REQUEST_SCHEMA')
    if record['schema'] != 'worldline.original-custody-client-v1':
        raise RuntimeError('CLIENT_ORIGINAL_ACTOR_SCHEMA')
    endpoint = Path(record['endpoint'])
    if not any(parent.parent == Path('/srv') and parent.name.startswith('cosmogony-canonical-v1.control-')
               for parent in endpoint.parents):
        raise RuntimeError('CLIENT_DISPOSABLE_ORIGINAL_ENDPOINT_REQUIRED')
    requests = [_lease.file(path, ('DATA',)) for path in record['requests']]
    if not requests or any(not raw.endswith(b'\n') or raw.count(b'\n') != 1 for raw in requests):
        raise RuntimeError('CLIENT_COMPLETE_ORIGINAL_LINE_REQUIRED')
    if record['disconnect'] not in ('never', 'after-send', 'after-progress'):
        raise RuntimeError('CLIENT_EXACT_TRANSPORT_CONTROL_REQUIRED')
    if os.geteuid() != 0:
        raise RuntimeError('CLIENT_OPERATOR_MUST_SELECT_ORIGINAL_ACTOR')
    for value in (record['uid'], record['gid'], *record['groups']):
        if type(value) is not int or not 0 <= value < (1 << 32) - 1:
            raise RuntimeError('CLIENT_FULL_ORIGINAL_KERNEL_IDENTITY_REQUIRED')
    if not _lease.excluded_actor():
        runtime = str(Path(__file__).parents[2] / 'runtime')
        _lease.directory_or_absent(runtime)
        sys.path.insert(0, runtime)
        from worldline.excluded_source_owner import run_original_client_owner
        return run_original_client_owner(_lease, _approved, args.request, __file__)
    _lease.check()
    os.setgroups(record['groups'])
    os.setresgid(record['gid'], record['gid'], record['gid'])
    os.setresuid(record['uid'], record['uid'], record['uid'])
    if os.getresuid() != (record['uid'],) * 3 or os.getresgid() != (record['gid'],) * 3:
        raise RuntimeError('CLIENT_ACTUAL_EXCLUDED_IDENTITY_CHANGED')
    if os.getgroups() != sorted(record['groups']):
        raise RuntimeError('CLIENT_ACTUAL_EXCLUDED_GROUPS_CHANGED')
    _lease.excluded_actor_ready()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
        channel.settimeout(record['timeout'])
        channel.connect(_lease.excluded_endpoint(str(endpoint)))
        peer = channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('@iII'))
        _lease.excluded_target(channel, str(endpoint))
        print(json.dumps({'actual_client_pid': os.getpid(), 'actual_uid': os.getuid(),
              'actual_gid': os.getgid(),
              'actual_server_ucred_hex': peer.hex()}), flush=True)
        pending = b''
        for raw in requests:
            channel.sendall(raw)
            print(json.dumps({'original_request_hex': raw.hex(), 'actual_send_complete': True}), flush=True)
            if record['disconnect'] == 'after-send':
                channel.shutdown(socket.SHUT_RDWR)
                return 0
            while True:
                while b'\n' not in pending:
                    chunk = channel.recv(65536)
                    if not chunk:
                        raise RuntimeError('CLIENT_ORIGINAL_RESPONSE_EOF_WITHOUT_RESULT')
                    pending += chunk
                line, pending = pending.split(b'\n', 1)
                response = json.loads(line)
                print(json.dumps({'original_response_hex': (line + b'\n').hex()}), flush=True)
                if 'event' in response:
                    if record['disconnect'] == 'after-progress':
                        channel.shutdown(socket.SHUT_RDWR)
                        return 0
                else:
                    break
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
