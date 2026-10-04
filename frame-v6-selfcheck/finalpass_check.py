"""Author self-check of the V5-B01 final-pass revalidation in the scratch frame v6 working copy's observe_tree.

Library import only: no gprbuild, gnatprove or systemd-run launch; RUNS and WINDOW are redirected to absent fixture
paths, and observe_tree touches neither. Each case builds a throwaway tree containing a recorded file (a/ok.adb), an
excluded generated file inside an output partition (obj/g.ali) and a late-walked directory. A hook on os.listdir fires
once, when the walker lists a directory that is walked AFTER the target file was observed, and mutates that already
observed file. The final pass must refuse every such change. The same cases are run against the frozen v5 frame for
contrast. ENGINEERING_ONLY: never proof, review, admission or acceptance evidence.

Usage: finalpass_check.py FRAME_DIR LABEL NEW_OUTPUT_DIR"""
import contextlib, importlib.util, io, json, os, sys
from pathlib import Path

sys.dont_write_bytecode = True
os.umask(0o077)
FRAME, LABEL, SC = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
assert not SC.exists()
SC.mkdir(parents=True)
spec = importlib.util.spec_from_file_location('scratch_under_test_' + LABEL, FRAME / 'scratch.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
S.RUNS = SC / 'no-runs-here' / 'runs'
S.WINDOW = SC / 'no-window-here' / 'window.json'
results, outcomes = {}, {}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode())


@contextlib.contextmanager
def hooked_listdir(trigger, mutate):
    real = os.listdir
    state = {'fired': False}

    def wrapper(*args, **kwargs):
        listing = real(*args, **kwargs)
        if not state['fired'] and trigger in listing:
            state['fired'] = True
            mutate()
        return listing
    os.listdir = wrapper
    try:
        yield state
    finally:
        os.listdir = real


def build(root):
    # Walk order (descriptor stack, names pushed sorted, popped last-first): '', obj, a, 0late.
    write(root / 'a' / 'ok.adb', 'ok' * 100)
    write(root / 'obj' / 'g.ali', 'generated' * 10)
    write(root / '0late' / 'z.txt', 'z')


def run_case(name, target, mutation):
    """target: 'excluded' mutates obj/g.ali when 'a' is listed (after obj was walked); 'recorded' mutates a/ok.adb when
    '0late' is listed (after a was walked)."""
    root = SC / ('tree-' + name)
    build(root)
    path = root / ('obj/g.ali' if target == 'excluded' else 'a/ok.adb')
    trigger = 'ok.adb' if target == 'excluded' else 'z.txt'
    held = S.Dir.anchor(root)
    try:
        with hooked_listdir(trigger, (lambda: mutation(path)) if mutation else (lambda: None)) as state:
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    tree = S.observe_tree(held, exclude_partitions=True)
                outcome = {'refused': False, 'files': sorted(tree['files']), 'identities': sorted(tree['identities'])}
            except BaseException as caught:
                outcome = {'refused': True, 'error': '%s: %s' % (type(caught).__name__, str(caught)[:200])}
            outcome['hook_fired'] = state['fired']
    finally:
        held.close()
    outcomes[name] = outcome
    return outcome


def append(path):
    with open(path, 'ab') as stream:
        stream.write(b'+')


def chmod(path):
    os.chmod(path, 0o644 if (os.stat(path).st_mode & 0o777) != 0o644 else 0o640)


def replace(path):
    write(path.with_name(path.name + '.new'), path.read_bytes())
    os.replace(path.with_name(path.name + '.new'), path)


def retime(path):
    info = os.stat(path)
    os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns - 10**9))


def same_size_rewrite(path):
    data = path.read_bytes()
    with open(path, 'r+b') as stream:
        stream.write(bytes([data[0] ^ 1]))


def delete(path):
    os.unlink(path)


CASES = [
    ('control_no_mutation_excluded_target', 'excluded', None, False),
    ('control_no_mutation_recorded_target', 'recorded', None, False),
    ('excluded_append', 'excluded', append, True),
    ('excluded_chmod', 'excluded', chmod, True),
    ('excluded_replace', 'excluded', replace, True),
    ('excluded_retime', 'excluded', retime, True),
    ('excluded_same_size_rewrite', 'excluded', same_size_rewrite, True),
    ('excluded_delete', 'excluded', delete, True),
    ('recorded_append', 'recorded', append, True),
    ('recorded_chmod', 'recorded', chmod, True),
    ('recorded_replace', 'recorded', replace, True),
    ('recorded_retime', 'recorded', retime, True),
    ('recorded_same_size_rewrite', 'recorded', same_size_rewrite, True),
    ('recorded_delete', 'recorded', delete, True),
]
for name, target, mutation, must_refuse in CASES:
    outcome = run_case(name, target, mutation)
    results[name] = {'must_refuse': must_refuse, 'refused': outcome['refused'], 'hook_fired': outcome['hook_fired'],
                     'as_required': outcome['refused'] == must_refuse and outcome['hook_fired']}

summary = {'schema': 'frame-finalpass-selfcheck-v1', 'frame': str(FRAME), 'label': LABEL,
           'frame_sha256': __import__('hashlib').sha256((FRAME / 'scratch.py').read_bytes()).hexdigest(),
           'cases': len(CASES), 'as_required': sum(1 for row in results.values() if row['as_required']),
           'not_as_required': sorted(name for name, row in results.items() if not row['as_required']),
           'results': results, 'outcomes': outcomes, 'output_dir': str(SC),
           'boundary': 'library import of observe_tree on throwaway trees; no gprbuild/gnatprove/systemd-run launch; '
                       'RUNS/WINDOW redirected to absent paths',
           'truth_boundary': 'ENGINEERING_ONLY: scratch self-check on throwaway trees; never proof, review, admission, '
                             'source-qualification or Phase One acceptance evidence. Original guarantees OPEN_UNCHANGED.'}
print(json.dumps(summary, indent=1, sort_keys=True))
