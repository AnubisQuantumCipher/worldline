#!/usr/bin/python3 -B
"""Replay the complete original runtime roster against the Source21 candidate.

Every original action (116 planned rows) and every enrolled addition (11 rows) is
executed in its recorded order with its recorded child argv, cwd, explicit and
additional environment, after substituting the original receiving-candidate root
for this working copy. Each child runs in its own memory-capped transient scope
(like the original frame: MemoryMax 8G, MemorySwapMax 0, no core dumps). For every
action the exact argv, cwd, environment, start/end times, wall seconds, exit code,
stdout/stderr (complete bytes plus SHA-256), and the SHA-256 of the executed
binary/script are retained under receipts/<index>-<mode>/. Nothing is skipped,
no failure stops the roster (each row records its own outcome), and no result is
summarized as a pass unless the child's own exit status is 0.

This is a lead-executed replay, not the original Codex Main/admission frame; it
produces the same children on the same source with the same relative paths.
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ORIGINAL_C = ('/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/'
              'claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/codex-takeover-20261010/'
              'runtime-frame-successor-v20-ultra-v1-draft/candidate')
ORIGINAL_S20 = ('/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/'
                'claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/codex-takeover-20261010/'
                'integrated-candidate-v20/source')
GNAT = '/home/sicarii/opt/gnat'
GNAT_PATH = (f'{GNAT}/gnat-aarch64-linux-16.1.0-1/bin:{GNAT}/gprbuild-aarch64-linux-26.0.0-1/bin:'
             f'{GNAT}/gnatprove-aarch64-linux-16.1.0-1/bin')


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def substitute(value, work):
    if isinstance(value, str):
        return value.replace(ORIGINAL_C + '/source', str(work / 'source')).replace(
            ORIGINAL_C, str(work)).replace(ORIGINAL_S20, str(work / 'source'))
    if isinstance(value, list):
        return [substitute(v, work) for v in value]
    if isinstance(value, dict):
        return {k: substitute(v, work) for k, v in value.items()}
    return value


def environment(work, row):
    source = work / 'source'
    inbound = dict(row.get('explicit_inbound_environment') or {})
    path = inbound.get('PATH') or os.environ.get('PATH', '/usr/bin')
    env = {
        'PATH': GNAT_PATH + ':' + path,
        'HOME': os.environ.get('HOME', '/home/sicarii'),
        'LANG': os.environ.get('LANG', 'C.UTF-8'),
        'XDG_RUNTIME_DIR': '/run/user/1000',
        'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
        'TMPDIR': '/home/sicarii/.cache/workflow-tmp',
        'GNAT_ROOT': GNAT,
        'GPR_PROJECT_PATH': f'{GNAT}/gnatprove-aarch64-linux-16.1.0-1/lib/gnat:{GNAT}/auxiliary/share/gpr',
        'PYTHONPATH': f'{source}/runtime:{source}/tests',
        'PYTHONDONTWRITEBYTECODE': '1',
        'WORLDLINE_BUILD': 'checks',
        'WORLDLINE_CORE_LIB': f'{source}/lib/libworldline_core.so',
        'PENDING_LIBRARY_DIR': f'{source}/lib/pending-standalone',
        'PENDING_OBJECT_DIR': f'{source}/obj/pending-standalone',
    }
    extra = row.get('additional_environment')
    if extra is None and isinstance(row.get('additional_command'), dict):
        extra = row['additional_command'].get('additional_environment')
    for key, value in (extra or {}).items():
        env[key] = substitute(value, work)
    for forbidden in ('PYTHONOPTIMIZE', 'WORLDLINE_DAEMON_UID'):
        env.pop(forbidden, None)
    return env


def run_row(work, out, index, source_name, row, cap, original_receipt=None, child_deadline=600):
    mode = row.get('mode') or (row.get('additional_command') or {}).get('mode') or f'row{index}'
    receipt = out / f'{source_name}-{index:03d}-{mode}'
    receipt.mkdir(parents=True, exist_ok=False)
    # The original frame created each action's receipt directory under <candidate>/evidence before
    # launching the child; children derive fixture paths from it (e.g. native_workload_controls).
    child_receipt = None
    original = original_receipt or row.get('receipt')
    if original:
        child_receipt = Path(substitute(original, work))
        child_receipt.mkdir(parents=True, exist_ok=True)
    argv = substitute(row['child_argv'], work)
    cwd = substitute(row['cwd'], work)
    env = environment(work, row)
    # The original frame bounded every child by its 600 s child deadline (scope 840, Main 1000); the same
    # bound is applied here with timeout(1) so a hung child records a deadline kill instead of stalling the roster.
    scope = ['systemd-run', '--user', '--scope', '-q', f'-p', f'MemoryMax={cap}', '-p', 'MemorySwapMax=0',
             '--unit', f'phase1-roster-{source_name}-{index:03d}-{os.getpid()}',
             'timeout', '-s', 'KILL', str(child_deadline)]
    record = {'index': index, 'source': source_name, 'mode': mode, 'argv': argv, 'cwd': cwd,
              'child_receipt_dir': str(child_receipt) if child_receipt else None,
              'child_deadline_seconds': child_deadline,
              'environment': env, 'scope_argv': scope, 'depends_on': row.get('depends_on'),
              'original_child_argv': row['child_argv'], 'original_cwd': row['cwd'],
              'executed_binary_sha256': sha(argv[0]) if argv and os.path.isabs(argv[0]) else None,
              'script_sha256': sha(argv[2]) if len(argv) > 2 and argv[2].endswith('.py') and os.path.isabs(argv[2]) else None,
              'started_at': now()}
    started = time.monotonic()
    with open(receipt / 'stdout.bin', 'wb') as so, open(receipt / 'stderr.bin', 'wb') as se:
        try:
            proc = subprocess.run(scope + argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=so, stderr=se,
                                  preexec_fn=lambda: __import__('resource').setrlimit(__import__('resource').RLIMIT_CORE, (0, 0)))
            record['exit_code'] = proc.returncode
            record['launch_error'] = None
            record['deadline_killed'] = (proc.returncode == 137)
        except OSError as error:
            record['exit_code'] = None
            record['launch_error'] = repr(error)
    record['ended_at'] = now()
    record['wall_seconds'] = round(time.monotonic() - started, 3)
    for name in ('stdout.bin', 'stderr.bin'):
        data = (receipt / name).read_bytes()
        record[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                        'tail': data[-600:].decode('utf-8', 'replace')}
    record['library_sha256_after'] = sha(work / 'source/lib/libworldline_core.so')
    if child_receipt is not None and child_receipt.exists():
        listing = []
        for item in sorted(child_receipt.rglob('*')):
            if item.is_file():
                listing.append({'path': str(item.relative_to(child_receipt)), 'bytes': item.stat().st_size, 'sha256': sha(item)})
        record['child_receipt_files'] = listing
        if sum(f['bytes'] for f in listing) <= 50 * 1024 * 1024:
            shutil.copytree(child_receipt, receipt / 'child-receipt', dirs_exist_ok=True)
    (receipt / 'record.json').write_text(json.dumps(record, indent=1))
    verdict = 'PASS' if record['exit_code'] == 0 else 'FAIL'
    print(f'[{now()}] {source_name} {index:03d} {mode}: exit={record["exit_code"]} {verdict} {record["wall_seconds"]}s', flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', required=True)
    parser.add_argument('--planned', required=True)
    parser.add_argument('--additional', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--first', type=int, default=0)
    parser.add_argument('--last', type=int, default=None, help='inclusive planned index; default all')
    parser.add_argument('--additions', action='store_true', help='also run the 11 additional rows after the planned range')
    parser.add_argument('--cap', default='8G')
    parser.add_argument('--child-deadline', type=int, default=600, help='seconds before a child is killed (original frame: 600)')
    parser.add_argument('--clean', action='store_true', help='remove obj/, bin/, lib/*.so, lib/*.ali, lib/pending-standalone, native-artifacts first')
    parser.add_argument('--receipts', default=str(Path(__file__).resolve().parent / 'receipts.json'),
                        help='ordered original receipt directories (planned 116, additions 11) extracted from RUNTIME-ROSTER.md')
    args = parser.parse_args()
    work = Path(args.work).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    planned = json.load(open(args.planned))
    additional = json.load(open(args.additional))
    source = work / 'source'
    if args.clean:
        removed = []
        for rel in ('obj', 'bin', 'lib/pending-standalone', 'lib/gnatprove'):
            target = source / rel
            if target.exists():
                shutil.rmtree(target); removed.append(rel)
        for pattern in ('lib/*.so', 'lib/*.ali'):
            for item in source.glob(pattern):
                item.unlink(); removed.append(str(item.relative_to(source)))
        for sub in source.iterdir():
            # test projects keep their own obj/bin under their directory
            if sub.is_dir():
                for rel in ('obj', 'bin'):
                    target = sub / rel
                    if target.exists() and sub.name not in ('.git',):
                        shutil.rmtree(target); removed.append(str(target.relative_to(source)))
        for rel in ('native-artifacts', 'evidence'):
            target = work / rel
            if target.exists():
                shutil.rmtree(target); removed.append(rel)
        (out / 'clean.json').write_text(json.dumps({'at': now(), 'removed': removed}, indent=1))
        print('cleaned', removed, flush=True)
    # The additions run scripts the original frame kept beside its source (candidate/additional-commands);
    # a byte copy of that directory travels with the runner and is placed at the same relative path.
    original_commands = Path(__file__).resolve().parent / 'additional-commands'
    if original_commands.is_dir():
        shutil.copytree(original_commands, work / 'additional-commands', dirs_exist_ok=True)
    head = subprocess.run(['git', '-C', str(source), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(['git', '-C', str(source), 'status', '--porcelain', '--untracked-files=no'], capture_output=True, text=True).stdout
    (out / 'run.json').write_text(json.dumps({'started_at': now(), 'commit': head, 'dirty': dirty.splitlines(),
                                               'planned_count': len(planned), 'additional_count': len(additional),
                                               'first': args.first, 'last': args.last, 'additions': args.additions,
                                               'cap': args.cap, 'host': os.uname().nodename}, indent=1))
    receipts = json.load(open(args.receipts))
    assert len(receipts['planned']) == len(planned) and len(receipts['additions']) == len(additional)
    results = []
    last = len(planned) - 1 if args.last is None else args.last
    for index in range(args.first, last + 1):
        results.append(run_row(work, out, index, 'planned', planned[index], args.cap, receipts['planned'][index]['receipt'], args.child_deadline))
        (out / 'results.json').write_text(json.dumps(results, indent=1))
    if args.additions:
        for index, row in enumerate(additional):
            results.append(run_row(work, out, index, 'additional', row, args.cap, receipts['additions'][index]['receipt'], args.child_deadline))
            (out / 'results.json').write_text(json.dumps(results, indent=1))
    failed = [r for r in results if r['exit_code'] != 0]
    summary = {'ended_at': now(), 'commit': head, 'rows': len(results), 'passed': len(results) - len(failed),
               'failed': [{'source': r['source'], 'index': r['index'], 'mode': r['mode'], 'exit_code': r['exit_code']} for r in failed]}
    (out / 'summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1), flush=True)
    return 0 if not failed else 1


if __name__ == '__main__':
    raise SystemExit(main())
