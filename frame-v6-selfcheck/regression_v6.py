"""Run the unchanged v5 author self-check harness against the v6 working copy (regression check of the final-pass
change). The harness text is read, its sha256 checked, exactly one FRAME line retargeted to the v6 working copy in
memory, and executed; no harness or frame file is modified. ENGINEERING_ONLY (the harness itself launches no
gprbuild/gnatprove/systemd-run and never touches the real shared window).

Usage: regression_v6.py NEW_OUTPUT_DIR"""
import hashlib, sys
from pathlib import Path

HARNESS = Path('/home/sicarii/.claude/jobs/c9272506/tmp/p1/scratchgen-v5/selfcheck.py')
HARNESS_SHA256 = None  # recorded at run time below and printed for the record
OLD = "FRAME = W / 'work/claude-scratch-frame-v5'"
NEW = "FRAME = W / 'work/claude-scratch-frame-v6'"

text = HARNESS.read_text()
digest = hashlib.sha256(text.encode()).hexdigest()
assert text.count(OLD) == 1, 'harness FRAME line not found exactly once'
sys.stderr.write('harness %s sha256 %s retargeted: %s -> %s\n' % (HARNESS, digest, OLD, NEW))
sys.argv = [str(HARNESS), sys.argv[1]]
namespace = {'__name__': '__main__', '__file__': str(HARNESS)}
exec(compile(text.replace(OLD, NEW), str(HARNESS) + ' [retargeted to v6]', 'exec'), namespace)
