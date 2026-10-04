"""W-1 DAC probe, inner half. Runs as inner root of a rootless user namespace created by dacprobe_outer.py with the
mapping inner 0 -> outer 1000 (sicarii), inner 1..65536 -> outer 100000..165535 (the operator-configured
/etc/subuid and /etc/subgid range). Inner uid 1 (outer 100000) plays the writer, inner uid 2 (outer 100001) the
target, inner uid 3 (outer 100002) a stand-in owner for the root-owned writer home. All objects live under a
sacrificial directory in /tmp. ENGINEERING_ONLY: not the W-1 setup, no WORLDLINE code, no prover or compiler.

Protocol on stdin/stdout with the outer driver: prints 'READY <json>' once the tree exists, the writer holds the lease
and the in-namespace probes are done; waits for 'DONE'; finishes the writer, cleans up, prints 'RESULT <json>'."""
import errno, json, os, shutil, subprocess, sys

B = sys.argv[1]
PROTO = sys.argv[2]
sys.path.insert(0, PROTO)
import w1proto as P   # imported before any uid change: children never need to read the proto directory

WRITER, TARGET, HOMEOWNER = 1, 2, 3
HOME = os.path.join(B, 'home')
LEASE_DIR = os.path.join(HOME, 'lease')
RUNS = os.path.join(HOME, 'runs')
probes = []


def errname(code):
    return errno.errorcode.get(code, str(code))


def probe(actor, label, action, expect):
    """expect: 'ok' or an errno name or a tuple of acceptable errno names."""
    try:
        action()
        got = 'ok'
    except P.LeaseHeld:
        got = 'LeaseHeld'
    except OSError as caught:
        got = errname(caught.errno)
    except P.Refused as caught:
        got = 'Refused: ' + str(caught)
    allowed = expect if isinstance(expect, tuple) else (expect,)
    return {'actor': actor, 'probe': label, 'expected': list(allowed), 'got': got, 'as_required': got in allowed}


def become(uid):
    os.setgroups([])
    os.setresgid(uid, uid, uid)
    os.setresuid(uid, uid, uid)


def setfacl(*args):
    subprocess.run(['/usr/bin/setfacl', *args], check=True, capture_output=True)


def run_as(uid, fn):
    """Run fn() in a child with the given inner uid; return its JSON result through a pipe."""
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        try:
            become(uid)
            out = fn()
        except BaseException as caught:
            out = {'child_error': '%s: %s' % (type(caught).__name__, caught)}
        os.write(w, json.dumps(out).encode())
        os._exit(0)
    os.close(w)
    data = b''
    while True:
        chunk = os.read(r, 1 << 16)
        if not chunk:
            break
        data += chunk
    os.close(r)
    os.waitpid(pid, 0)
    return json.loads(data)


def write_file(path, data, mode):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


# ---------------------------------------------------------------- setup as inner root (the operator's role in W-1)
os.chdir(B)
os.mkdir(HOME, 0o750)
os.chown(HOME, HOMEOWNER, WRITER)                    # stand-in for root:wlscratch 0750
os.mkdir(LEASE_DIR, 0o700)
os.chown(LEASE_DIR, WRITER, WRITER)
write_file(os.path.join(LEASE_DIR, 'writer.lock'), b'', 0o600)
os.chown(os.path.join(LEASE_DIR, 'writer.lock'), WRITER, WRITER)
os.mkdir(RUNS, 0o750)
os.chown(RUNS, WRITER, WRITER)
setfacl('-m', 'u:0:r-x,u:%d:--x' % TARGET, HOME)       # inner 0 is outer sicarii
setfacl('-m', 'u:0:r-x,u:%d:--x' % TARGET, RUNS)
setfacl('-d', '-m', 'u:0:r-x,u:%d:--x' % TARGET, RUNS)

# ---------------------------------------------------------------- the writer: lease, generation, ACLs; it then holds the lease
ready_r, ready_w = os.pipe()
go_r, go_w = os.pipe()
writer_pid = os.fork()
if writer_pid == 0:
    os.close(ready_r)
    os.close(go_w)
    report = {}
    try:
        become(WRITER)
        report['nondumpable'] = P.set_nondumpable()
        dfd = os.open(LEASE_DIR, os.O_RDONLY | os.O_DIRECTORY)
        lease = P.acquire_lease(dfd)
        report['lease'] = 'held'
        g = os.path.join(RUNS, 'gen-' + os.urandom(8).hex())
        os.mkdir(g, 0o750)
        frame = os.path.join(g, 'frame')
        src = os.path.join(g, 'src')
        obj = os.path.join(src, 'obj')
        os.mkdir(frame, 0o750)
        write_file(os.path.join(frame, 'generation.json'), b'{"generation":"probe"}\n', 0o640)
        os.mkdir(src, 0o750)
        write_file(os.path.join(src, 'a.ads'), b'package A is end A;\n', 0o640)
        os.mkdir(obj, 0o750)
        setfacl('-m', 'u:%d:r-x' % TARGET, src)
        setfacl('-m', 'u:%d:r--' % TARGET, os.path.join(src, 'a.ads'))
        setfacl('-m', 'u:%d:rwx' % TARGET, obj)
        setfacl('-d', '-m', 'u:%d:rwx,u:%d:r-x,u:0:r-x' % (TARGET, WRITER), obj)
        report['generation'] = g
        os.write(ready_w, json.dumps(report).encode())
        os.close(ready_w)
        os.read(go_r, 1)                                # hold the lease until told to finish
        with open(os.path.join(obj, 'out.o'), 'rb') as stream:   # target-owned output, readable through the default ACL
            report['writer_reads_target_output'] = stream.read().decode()
        os.close(lease)
        report['lease'] = 'released'
        print(json.dumps({'writer_final': report}), file=sys.stderr)
        os._exit(0)
    except BaseException as caught:
        try:
            os.write(ready_w, json.dumps({'writer_error': '%s: %s' % (type(caught).__name__, caught)}).encode())
        except OSError:
            pass
        os._exit(1)
os.close(ready_w)
os.close(go_r)
writer_report = json.loads(os.read(ready_r, 1 << 16))
os.close(ready_r)
if 'writer_error' in writer_report:
    print('RESULT ' + json.dumps({'fatal': writer_report}), flush=True)
    sys.exit(1)
G = writer_report['generation']
FRAME, SRC = os.path.join(G, 'frame'), os.path.join(G, 'src')
OBJ = os.path.join(SRC, 'obj')


# ---------------------------------------------------------------- a second writer while the lease is held
def second_writer():
    dfd = os.open(LEASE_DIR, os.O_RDONLY | os.O_DIRECTORY)
    return [probe('writer#2', 'acquire_lease_while_held', lambda: P.acquire_lease(dfd), 'LeaseHeld')]


probes += run_as(WRITER, second_writer)


# ---------------------------------------------------------------- the target (outer 100001)
def target_probes():
    out = []
    out.append(probe('target', 'create_output_in_partition (positive)',
                     lambda: write_file(os.path.join(OBJ, 'out.o'), b'object', 0o640), 'ok'))
    out.append(probe('target', 'mkdir_in_partition (positive)', lambda: os.mkdir(os.path.join(OBJ, 'sub'), 0o750), 'ok'))
    out.append(probe('target', 'read_admitted_source (positive)', lambda: open(os.path.join(SRC, 'a.ads'), 'rb').read(), 'ok'))
    out.append(probe('target', 'create_in_frame_records', lambda: write_file(os.path.join(FRAME, 'x'), b'x', 0o640), 'EACCES'))
    out.append(probe('target', 'write_admitted_source', lambda: os.close(os.open(os.path.join(SRC, 'a.ads'), os.O_WRONLY)), 'EACCES'))
    out.append(probe('target', 'create_beside_source', lambda: write_file(os.path.join(SRC, 'b.adb'), b'x', 0o640), 'EACCES'))
    out.append(probe('target', 'rename_partition', lambda: os.rename(OBJ, os.path.join(SRC, 'obj2')), 'EACCES'))
    out.append(probe('target', 'unlink_frame_record', lambda: os.unlink(os.path.join(FRAME, 'generation.json')), 'EACCES'))
    out.append(probe('target', 'hardlink_frame_record_into_partition',
                     lambda: os.link(os.path.join(FRAME, 'generation.json'), os.path.join(OBJ, 'alias')), ('EPERM', 'EACCES')))
    out.append(probe('target', 'chmod_admitted_source', lambda: os.chmod(os.path.join(SRC, 'a.ads'), 0o666), 'EPERM'))
    out.append(probe('target', 'rename_generation', lambda: os.rename(G, G + '-moved'), 'EACCES'))
    out.append(probe('target', 'create_in_runs', lambda: os.mkdir(os.path.join(RUNS, 'x'), 0o700), 'EACCES'))
    out.append(probe('target', 'open_lease_file', lambda: os.close(os.open(os.path.join(LEASE_DIR, 'writer.lock'), os.O_RDWR)), 'EACCES'))
    out.append(probe('target', 'symlink_in_partition_allowed_by_design',
                     lambda: os.symlink(FRAME, os.path.join(OBJ, 'link-to-frame')), 'ok'))
    return out


probes += run_as(TARGET, target_probes)

print('READY ' + json.dumps({'generation': G, 'home': HOME, 'runs': RUNS, 'lease_dir': LEASE_DIR,
                             'writer': {k: v for k, v in writer_report.items() if k != 'generation'}}), flush=True)
line = sys.stdin.readline().strip()
assert line == 'DONE', line

# ---------------------------------------------------------------- finish the writer, then re-acquire, then clean up
os.write(go_w, b'x')
os.close(go_w)
_pid, status = os.waitpid(writer_pid, 0)


def reacquire():
    dfd = os.open(LEASE_DIR, os.O_RDONLY | os.O_DIRECTORY)
    return [probe('writer#3', 'acquire_lease_after_release (positive)', lambda: os.close(P.acquire_lease(dfd)), 'ok')]


probes += run_as(WRITER, reacquire)
cleanup = 'ok'
try:
    shutil.rmtree(HOME)
except OSError as caught:
    cleanup = '%s: %s' % (errname(caught.errno), caught)
print('RESULT ' + json.dumps({'probes': probes, 'writer_exit_status': status, 'cleanup': cleanup,
                              'home_absent_after_cleanup': not os.path.exists(HOME)}), flush=True)
