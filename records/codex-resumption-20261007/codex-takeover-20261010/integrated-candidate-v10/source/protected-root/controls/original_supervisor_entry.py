"""Qualified offline wrapper invoking the unchanged original supervisor main.

The supervisor still owns its real process/namespace/socket/seal lifecycle and
uses its original subprocess argv and actor IDs. This wrapper makes no seal,
principal, grant, journal or successful daemon observation of its own.
"""
from __future__ import annotations
import sys
_loader = sys.modules.get('_worldline_approved_source_loader')
if _loader is None:
    raise SystemExit('OFFLINE_SUPERVISOR_EARLY_SOURCE_REQUIRED')
_lease = _loader.current()
_lease.check()
import importlib
import json
from pathlib import Path


def main():
    enrollment = json.loads(_lease.file(__file__ + '.json', ('DATA',)))
    if set(enrollment) != {'schema', 'source', 'import_roots'} or enrollment['schema'] != 'worldline.original-offline-supervisor-source-v1':
        raise RuntimeError('OFFLINE_SUPERVISOR_SOURCE_SCHEMA')
    raw = _lease.file(enrollment['source'], ('SOURCE',))
    for root in enrollment['import_roots']:
        _lease.directory_or_absent(root)
    sys.path[:0] = enrollment['import_roots']
    original = importlib.import_module('daemon_supervisor')
    if Path(original.__file__) != Path(enrollment['source']) or Path(original.__file__).read_bytes() != raw:
        raise RuntimeError('OFFLINE_SUPERVISOR_ORIGINAL_SOURCE_CHANGED')
    try:
        original.main()
    finally:
        _lease.check()


if __name__ == '__main__':
    main()
