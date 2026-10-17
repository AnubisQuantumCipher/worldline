#!/usr/bin/env python3
"""Serialize Phase 1 jobs and retain admission, process and cgroup evidence."""
from __future__ import annotations
import argparse
import datetime
import json
import os
import resource
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
LOCK = Path('/home/sicarii/.worldline-heavy.lock')

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def record(path, value):
    with path.open('a') as stream:
        stream.write(json.dumps(value, sort_keys=True) + '\n')

def cgroup_facts():
    entry = next(line for line in Path('/proc/self/cgroup').read_text().splitlines() if line.startswith('0::'))
    root = Path('/sys/fs/cgroup') / entry[3:].lstrip('/')
    result = {'path': str(root)}
    for name in ('memory.max', 'memory.peak', 'memory.current', 'memory.events', 'memory.swap.max'):
        target = root / name
        result[name] = target.read_text().strip() if target.exists() else None
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=('outer', 'locked', 'worker'), default='outer')
    parser.add_argument('--swap-max', default='0', help='Original acquisition setting is 0; retain an explicit setting')
    parser.add_argument('--timeout', required=True, help='GNU timeout duration; always explicit')
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a command is required')
    out = args.out.resolve()
    if not out.is_relative_to(ROOT):
        parser.error('evidence directory must be inside this worktree')
    os.chdir(ROOT)
    os.environ.setdefault('XDG_RUNTIME_DIR', '/run/user/' + str(os.getuid()))
    os.environ.setdefault('DBUS_SESSION_BUS_ADDRESS', 'unix:path=' + os.environ['XDG_RUNTIME_DIR'] + '/bus')
    if args.phase == 'outer':
        out.mkdir(parents=True, exist_ok=False)
        (out / 'tmp').mkdir()
        (out / 'cache').mkdir()
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        (out / 'tracked.diff').write_bytes(subprocess.check_output(['git', 'diff', 'HEAD', '--']))
        record(out / 'launch.jsonl', {'utc': stamp(), 'commit': head, 'argv': command,
               'timeout': args.timeout, 'MemoryMax': '8G', 'MemorySwapMax': args.swap_max, 'lock': str(LOCK),
               'status': 'UNVERIFIED', 'cwd': str(ROOT)})
        while True:
            admission_marker = out / 'admitted.json'
            if admission_marker.exists():
                admission_marker.unlink()
            argv = ['flock', str(LOCK), sys.executable, __file__, '--phase', 'locked',
                    '--timeout', args.timeout, '--swap-max', args.swap_max, '--out', str(out), '--', *command]
            code = subprocess.call(argv)
            admission = json.loads(admission_marker.read_text()) if admission_marker.exists() else None
            if not (admission == {'admitted': False} and code == 75):
                record(out / 'result.jsonl', {'utc': stamp(), 'exit_code': code})
                return code
            # Lock holder has exited before the required five-minute backoff.
            time.sleep(300)
    if args.phase == 'locked':
        mem = next(line for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
        available = int(mem.split()[1]) * 1024
        threshold = int(subprocess.check_output(['numfmt', '--from=iec', '14G'], text=True))
        admitted = available >= threshold
        record(out / 'admission.jsonl', {'utc': stamp(), 'MemAvailable': mem,
               'threshold': '14GiB (conservative interpretation of 14GB)', 'admitted': admitted})
        (out / 'admitted.json').write_text(json.dumps({'admitted': admitted}))
        if not admitted:
            return 75
        bus = subprocess.run(['systemctl', '--user', 'show-environment'], capture_output=True)
        if bus.returncode != 0:
            record(out / 'refusal.jsonl', {'utc': stamp(), 'reason': 'user systemd unavailable', 'stderr': bus.stderr.decode(errors='replace')})
            return 125
        unit = 'wl-phase1-' + uuid.uuid4().hex
        record(out / 'scope.jsonl', {'utc': stamp(), 'unit': unit + '.scope'})
        argv = ['systemd-run', '--user', '--scope', '--quiet', '--unit=' + unit,
                '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=' + args.swap_max, '-p', 'MemoryAccounting=yes',
                sys.executable, __file__, '--phase', 'worker', '--timeout', args.timeout,
                '--swap-max', args.swap_max, '--out', str(out), '--', *command]
        with (out / 'launcher.stdout').open('ab') as stdout, (out / 'launcher.stderr').open('ab') as stderr:
            process = subprocess.Popen(argv, stdout=stdout, stderr=stderr)
            group = None
            scope_state = {}
            def observe():
                nonlocal group, scope_state
                state = subprocess.run(['systemctl', '--user', 'show', unit + '.scope',
                    '-p', 'ControlGroup', '-p', 'LoadState', '-p', 'ActiveState', '-p', 'SubState', '-p', 'Result',
                    '-p', 'MemoryPeak', '-p', 'MemoryMax', '-p', 'MemorySwapMax'],
                    text=True, capture_output=True)
                values = dict(line.split('=', 1) for line in state.stdout.splitlines() if '=' in line)
                scope_state = values
                if values.get('ControlGroup'):
                    group = Path('/sys/fs/cgroup') / values['ControlGroup'].lstrip('/')
                sample = {'utc': stamp(), 'systemctl_exit': state.returncode, 'unit': values}
                if group is not None:
                    for name in ('memory.events', 'memory.peak', 'memory.current', 'cgroup.events'):
                        try:
                            sample[name] = (group / name).read_text().strip()
                        except FileNotFoundError:
                            sample[name] = None
                record(out / 'supervisor.jsonl', sample)
                return 'populated 1' in (sample.get('cgroup.events') or '')
            try:
                while process.poll() is None:
                    observe()
                    if (out / 'worker-result.json').exists():
                        break
                    time.sleep(1)
                code = json.loads((out / 'worker-result.json').read_text())['exit_code'] if (out / 'worker-result.json').exists() else process.returncode
            finally:
                populated = observe()
                if populated or process.poll() is None or scope_state.get('ActiveState') not in ('inactive', 'failed'):
                    record(out / 'cleanup.jsonl', {'utc': stamp(), 'action': 'stop owned scope', 'unit': unit})
                    subprocess.run(['systemctl', '--user', 'stop', '--no-block', unit + '.scope'], check=False)
                    while True:
                        populated = observe()
                        if not populated and scope_state.get('ActiveState') in ('inactive', 'failed'):
                            break
                        subprocess.run(['systemctl', '--user', 'kill', '--signal=KILL', '--kill-whom=all', unit + '.scope'], check=False)
                        time.sleep(1)
                    process.wait()
                record(out / 'terminal-scope.jsonl', {'utc': stamp(), 'scope_state': scope_state, 'populated': populated})
            journal = subprocess.run(['journalctl', '--user', '-u', unit + '.scope', '--no-pager'], capture_output=True)
            (out / 'scope-journal.txt').write_bytes(journal.stdout + journal.stderr)
            return code
    facts = cgroup_facts()
    record(out / 'cgroup.jsonl', {'utc': stamp(), 'event': 'before', **facts})
    expected_max = subprocess.check_output(['numfmt', '--from=iec', '8G'], text=True).strip()
    expected_swap = subprocess.check_output(['numfmt', '--from=iec', args.swap_max], text=True).strip()
    if facts['memory.max'] != expected_max or facts['memory.swap.max'] != expected_swap:
        record(out / 'refusal.jsonl', {'utc': stamp(), 'reason': 'actual cgroup cap mismatch', 'expected_max': expected_max, 'expected_swap': expected_swap})
        return 125
    env = dict(os.environ, TMPDIR=str(out / 'tmp'), XDG_CACHE_HOME=str(out / 'cache'),
               PYTHONDONTWRITEBYTECODE='1')
    started = time.monotonic()
    argv = ['timeout',
            '--signal=TERM', '--kill-after=30s', args.timeout, *command]
    with (out / 'stdout').open('xb') as stdout, (out / 'stderr').open('xb') as stderr:
        process = subprocess.Popen(argv, env=env, stdout=stdout, stderr=stderr)
        while process.poll() is None:
            record(out / 'cgroup.jsonl', {'utc': stamp(), 'event': 'sample', **cgroup_facts()})
            time.sleep(1)
        code = process.returncode
    record(out / 'cgroup.jsonl', {'utc': stamp(), 'event': 'after', 'exit_code': code, **cgroup_facts()})
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    (out / 'rusage.json').write_text(json.dumps({'ru_maxrss_kib': usage.ru_maxrss, 'elapsed_seconds': time.monotonic() - started, 'measurement': 'RUSAGE_CHILDREN maximum child RSS; aggregate cap measured separately by cgroup'}))
    (out / 'worker-result.json').write_text(json.dumps({'exit_code': code, 'utc': stamp()}))
    return code

if __name__ == '__main__':
    raise SystemExit(main())
