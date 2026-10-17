#!/usr/bin/env python3
"""Strict explicit frozen source/build/frame identity, with no work on import."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def owned_path(path, *, directory=False):
    path = Path(path).resolve(strict=True)
    if not path.is_relative_to(ROOT):
        raise RuntimeError('Identity input must remain inside this worktree: '+str(path))
    if directory and (not path.is_dir() or path == ROOT):
        raise RuntimeError('Use a separately materialized owned source frame')
    if not directory and not path.is_file():
        raise RuntimeError('Identity receipt is not a file: '+str(path))
    return path

def hash_map(value, label):
    if not isinstance(value, dict) or not value:
        raise RuntimeError(label+' missing or empty')
    for relative, digest in value.items():
        if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise RuntimeError('Unsafe relative path in '+label)
        if not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest):
            raise RuntimeError('Missing or invalid digest in '+label)
    return value

def validate(commit, freeze_record, frame, build_manifest, *, link=False):
    if not re.fullmatch('[a-f0-9]{40}', commit):
        raise RuntimeError('Exact frozen commit required')
    freeze_record = owned_path(freeze_record)
    frame = owned_path(frame, directory=True)
    build_manifest = owned_path(build_manifest)
    full_build_receipt = owned_path(build_manifest.parent/'full-root.json')
    frozen = json.loads(freeze_record.read_text())
    build = json.loads(build_manifest.read_text())
    completed = json.loads(full_build_receipt.read_text())
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if head != commit or frozen.get('commit') != commit or build.get('source_commit') != commit:
        raise RuntimeError('Frozen/current/build source commit mismatch')
    if frozen.get('tracked_dirty') != '' or build.get('source_unchanged') is not True:
        raise RuntimeError('Frozen source cleanliness or completed build source identity not established')
    if (completed.get('source_commit') != commit or type(completed.get('exit_code')) is not int
        or completed['exit_code'] != 0 or not isinstance(completed.get('completed_utc'), str)
        or not completed['completed_utc']):
        raise RuntimeError('Full final build not completed on the required source')
    if subprocess.check_output(['git', 'diff', 'HEAD', '--'], cwd=ROOT):
        raise RuntimeError('Tracked product bytes differ from frozen HEAD')
    source_hashes = hash_map(frozen.get('source_hashes'), 'frozen source roster')
    tracked = set(subprocess.check_output(['git', 'ls-tree', '-rz', '--name-only', commit], cwd=ROOT).decode().split('\0'))-{''}
    if set(source_hashes) != tracked:
        raise RuntimeError('Frozen source receipt does not contain the exact original tracked roster')
    for relative, wanted in source_hashes.items():
        for base in (ROOT, frame):
            path = base/relative
            if not path.is_file() or not path.resolve().is_relative_to(base) or sha(path) != wanted:
                raise RuntimeError('Frozen root/frame source bytes differ: '+str(path))
    artifacts = hash_map(build.get('artifacts'), 'completed build artifact roster')
    for required in ('lib/libworldline_core.so', 'bin/worldline_core_tests', 'bin/worldline_core_fuzz'):
        if required not in artifacts:
            raise RuntimeError('Original required build artifact absent: '+required)
    for relative, wanted in artifacts.items():
        path = ROOT/relative
        if not path.is_file() or not path.resolve().is_relative_to(ROOT) or sha(path) != wanted:
            raise RuntimeError('Built artifacts differ from final receipt: '+relative)
    if link:
        for name in ('lib', 'bin', 'obj'):
            destination = frame/name
            target = ROOT/name
            if not target.is_dir():
                raise RuntimeError('Original artifact directory missing: '+name)
            if destination.is_symlink():
                if destination.resolve() != target.resolve():
                    raise RuntimeError('Unexpected existing frame artifact link')
            elif destination.exists():
                raise RuntimeError('Refuse to replace existing frame artifact directory')
            else:
                destination.symlink_to(target, target_is_directory=True)
    library = ROOT/'lib/libworldline_core.so'
    return {'commit': commit, 'source_commit': commit, 'frame': str(frame),
            'freeze_record': str(freeze_record), 'freeze_sha256': sha(freeze_record),
            'build_manifest': str(build_manifest), 'build_sha256': sha(build_manifest),
            'full_build_receipt': str(full_build_receipt), 'full_build_receipt_sha256': sha(full_build_receipt),
            'identity_helper_sha256': sha(__file__),
            'library': str(library), 'library_sha256': sha(library),
            'all_original_tracked_hashes_match': True, 'exact_tracked_roster_matches': True,
            'artifact_hashes': artifacts}
