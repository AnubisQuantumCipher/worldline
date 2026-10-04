"""W-1 DAC probe, outer half (runs as the real lead user sicarii, outside the namespace).

Creates a sacrificial directory under /tmp, starts dacprobe_inner.py as inner root of a rootless user namespace
(mapping inner 0 -> 1000, inner 1..65536 -> 100000..165535 from /etc/subuid and /etc/subgid), waits for READY, then
attempts, as genuine uid 1000, every mutation W-1 says sicarii processes cannot make on the writer's tree. The
kernel's ordinary DAC and protected_hardlinks decide each probe. It also demonstrates the one property this
environment cannot model: here the ancestor directory is sicarii-owned, where W-1 places root-owned /var/lib.

ENGINEERING_ONLY: not the W-1 setup (no accounts, sudo, install or mounts), no WORLDLINE code, no prover or compiler.
Usage: dacprobe_outer.py OUTPUT_JSON"""
import errno, hashlib, json, os, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
assert not os.path.exists(OUT)


def errname(code):
    return errno.errorcode.get(code, str(code))


def probe(label, action, expect):
    try:
        action()
        got = 'ok'
    except OSError as caught:
        got = errname(caught.errno)
    allowed = expect if isinstance(expect, tuple) else (expect,)
    return {'actor': 'sicarii (outer uid 1000)', 'probe': label, 'expected': list(allowed), 'got': got,
            'as_required': got in allowed}


base = tempfile.mkdtemp(prefix='wl-dacprobe-', dir='/tmp')
os.chmod(base, 0o755)          # namespace uids are 'other' here and must traverse it
argv = ['/usr/bin/unshare', '--map-users', '0:1000:1', '--map-users', '1:100000:65536',
        '--map-groups', '0:1000:1', '--map-groups', '1:100000:65536', '--setuid', '0', '--setgid', '0',
        '/usr/bin/python3', '-I', '-B', os.path.join(HERE, 'dacprobe_inner.py'), base, HERE]
child = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                         cwd=base)
ready_line = child.stdout.readline()
outer, ancestor = [], {}
if not ready_line.startswith('READY '):
    rest, err = child.communicate(timeout=60)
    summary = {'fatal': 'inner did not become ready', 'line': ready_line, 'rest': rest, 'stderr': err}
else:
    ready = json.loads(ready_line[len('READY '):])
    G, HOME, RUNS, LEASE = ready['generation'], ready['home'], ready['runs'], ready['lease_dir']
    FRAME, SRC = os.path.join(G, 'frame'), os.path.join(G, 'src')
    OBJ = os.path.join(SRC, 'obj')
    st = os.stat(os.path.join(FRAME, 'generation.json'))
    ownership = {'frame_record_uid': st.st_uid, 'frame_record_gid': st.st_gid,
                 'output_uid': os.stat(os.path.join(OBJ, 'out.o')).st_uid, 'home_uid': os.stat(HOME).st_uid,
                 'runs_uid': os.stat(RUNS).st_uid}
    outer.append(probe('read_frame_record_via_acl (positive)', lambda: open(os.path.join(FRAME, 'generation.json')).read(), 'ok'))
    outer.append(probe('read_target_output_via_default_acl (positive)', lambda: open(os.path.join(OBJ, 'out.o')).read(), 'ok'))
    outer.append(probe('create_in_frame_records', lambda: os.close(os.open(os.path.join(FRAME, 'x'), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)), 'EACCES'))
    outer.append(probe('write_admitted_source', lambda: os.close(os.open(os.path.join(SRC, 'a.ads'), os.O_WRONLY)), 'EACCES'))
    outer.append(probe('create_in_partition', lambda: os.close(os.open(os.path.join(OBJ, 'y'), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)), 'EACCES'))
    outer.append(probe('rename_generation', lambda: os.rename(G, G + '-moved'), 'EACCES'))
    outer.append(probe('rename_partition', lambda: os.rename(OBJ, OBJ + '-moved'), 'EACCES'))
    outer.append(probe('unlink_frame_record', lambda: os.unlink(os.path.join(FRAME, 'generation.json')), 'EACCES'))
    outer.append(probe('chmod_frame_record', lambda: os.chmod(os.path.join(FRAME, 'generation.json'), 0o666), 'EPERM'))
    outer.append(probe('hardlink_admitted_source_out', lambda: os.link(os.path.join(SRC, 'a.ads'), os.path.join(base, 'alias')), ('EPERM', 'EACCES')))
    outer.append(probe('symlink_into_frame_dir', lambda: os.symlink('/tmp', os.path.join(FRAME, 'evil')), 'EACCES'))
    outer.append(probe('create_in_runs', lambda: os.mkdir(os.path.join(RUNS, 'x')), 'EACCES'))
    outer.append(probe('open_lease_file', lambda: os.close(os.open(os.path.join(LEASE, 'writer.lock'), os.O_RDWR)), 'EACCES'))
    outer.append(probe('rename_runs', lambda: os.rename(RUNS, RUNS + '-moved'), 'EACCES'))
    # The limitation of this environment: the parent of HOME is sicarii-owned here (root-owned /var/lib in W-1).
    moved = HOME + '-moved'
    try:
        os.rename(HOME, moved)
        ancestor['rename_home_in_sicarii_owned_parent'] = 'ok (expected here; W-1 requires root-owned ancestors)'
        os.rename(moved, HOME)
        ancestor['renamed_back'] = 'ok'
    except OSError as caught:
        ancestor['rename_home_in_sicarii_owned_parent'] = errname(caught.errno)
    rest, err = child.communicate('DONE\n', timeout=120)
    result_line = [line for line in rest.splitlines() if line.startswith('RESULT ')]
    inner = json.loads(result_line[0][len('RESULT '):]) if result_line else {'fatal': 'no RESULT', 'rest': rest}
    all_probes = inner.get('probes', []) + outer
    summary = {'schema': 'w1-dacprobe-v1', 'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'base': base,
               'uid_map': 'inner 0->1000 (sicarii), inner 1->100000 (writer), 2->100001 (target), 3->100002 (home owner stand-in)',
               'ownership_seen_from_outside': ownership, 'writer_ready': ready.get('writer'),
               'probes': all_probes, 'probe_count': len(all_probes),
               'as_required': sum(1 for row in all_probes if row['as_required']),
               'not_as_required': [row for row in all_probes if not row['as_required']],
               'ancestor_limitation': ancestor, 'inner': {k: v for k, v in inner.items() if k != 'probes'},
               'inner_stderr': err[-4000:],
               'scripts': {name: hashlib.sha256(open(os.path.join(HERE, name), 'rb').read()).hexdigest()
                           for name in ('dacprobe_outer.py', 'dacprobe_inner.py', 'w1proto.py')},
               'kernel': {name: open('/proc/sys/' + name).read().strip()
                          for name in ('fs/protected_hardlinks', 'fs/protected_symlinks', 'kernel/yama/ptrace_scope')},
               'boundary': 'Real kernel DAC/ACL/protected_hardlinks checks between uid 1000 and subordinate uids 100000/100001 '
                           'on sacrificial /tmp files. Not the W-1 setup: no accounts, sudo, systemd user manager, install, '
                           'mounts or root-owned ancestors; the writer is not the frame; no WORLDLINE code; no prover or compiler.',
               'truth_boundary': 'ENGINEERING_ONLY: never proof, review, admission or acceptance evidence. V5-B01/V5-B02 and all '
                                 'original obligations OPEN_UNCHANGED.'}
try:
    os.rmdir(base)
    summary['base_removed'] = True
except OSError as caught:
    summary['base_removed'] = errname(caught.errno)
with open(OUT, 'x') as stream:
    json.dump(summary, stream, indent=1, sort_keys=True)
print(json.dumps({'probe_count': summary.get('probe_count'), 'as_required': summary.get('as_required'),
                  'not_as_required': summary.get('not_as_required'), 'ancestor': summary.get('ancestor_limitation'),
                  'base_removed': summary.get('base_removed'), 'fatal': summary.get('fatal')}, indent=1))
