"""WORLDLINE Phase One — W-1 frame-v6w1 member L/C/O: the in-view target entrypoint.

FROZEN, REVIEWABLE, UNINSTALLED DRAFTING source. Author: Claude (Opus 4.8), DRAFTING implementer,
not a reviewer. ESTABLISHES NO PREMISE; EXECUTED NOWHERE, INSTALLED NOWHERE this session.

Role (v11 §3.2). This member runs INSIDE the view RL built (uid/gid 1000 in all positions, empty
capability sets, the step-13b seccomp filter active, the Landlock domain active, the private mount
and network namespaces, the idmapped g binds). RL execs it as:
  - L = `launch_target.py launch …`  — the launcher, the lead's host credentials, in U8 and the
        view, in the attempt scope. RL execs L in place (v11 §12.2 step 16).
  - C = `launch_target.py child …`   — the same pid, after GO; L execs C, which repeats admission
        through held descriptors and spawns the target T (v5 `spawn`).
  - O = `launch_target.py observe …` — the observer, its own scope and view instance.

It is UNPRIVILEGED code (the untrusted side of the boundary runs below it); it performs NO
namespace, mount, seccomp or capability operation — the sandbox was already built by RL and cannot
be loosened from here (no_new_privs is 0 but CapEff is empty and the seccomp filter cannot be
removed — v11 §12.2 step 13b/14, §12.3 V14). Its job is to AUTHENTICATE the view it was launched
into and then run the target under v5's reviewed admission/spawn, exactly as the base frame's
child did (scratch.py child/admission/spawn), but with the view's root and binds instead of v5's
single mount.

The verification here is DEFENSIVE self-check only; it refutes nothing and discharges no premise.
"""
import sys


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


require(sys.flags.optimize == 0, 'refusing to run under Python optimization: gates must not be removable')
sys.dont_write_bytecode = True

import json, os, stat
from pathlib import Path

import framelib
from framelib import Dir, now

VERBS = ('launch', 'child', 'observe')


def read_rl_identity(expected_argv_seals):
    """v11 §12.2 step 16 — RL sends RL_IDENTITY on fd 0 just before exec. L/O read it and bind it to
    their argv seals (the launch.json / admission.json / observer-intent sha256 carried in argv, as
    the base frame's child authenticated by argv — FRAME.md V4-B03). The record carries the §9.3 G3
    fields: the seccomp program sha256, the Landlock digest, the namespace ids, the bind identities
    and the fd set. A mismatch refuses before the target runs. Installed body does the stable read
    + seal comparison; drafting names the contract."""
    raise NotImplementedError('installed body: read RL_IDENTITY on fd 0, compare to the argv seals '
                              '(v11 §12.2 step 16; FRAME.md V4-B03)')


def verify_self_exe_mount(rl_identity):
    """v11 §12.2 step 16 — L and C verify /proc/self/exe by statx mount ID against the record: the
    new image was loaded THROUGH the view's root, so its mappings belong to the new namespace.
    statx(/proc/self/exe, STATX_MNT_ID_UNIQUE) must equal the view mount id RL recorded. A mismatch
    means the interpreter image did not load through the view and refuses. DRAFTING: structure
    shown; installed body uses os.statx-equivalent via the statx syscall (RL already pins the id)."""
    raise NotImplementedError('installed body: statx(/proc/self/exe) mount id == RL_IDENTITY view id '
                              '(v11 §12.2 step 16)')


def view_admission(source_dir, snapshot_dir, seal):
    """The base frame's CHILD admission (FRAME.md V4-B03/B04, scratch.py child/admission), re-homed
    onto the view: open source/ and overlay-snapshot/ ONCE through the view (the idmapped g binds),
    require their identities and the run/attempt identities to equal the seal, verify every location
    and the full verify_materialization through the held descriptors, require the observed
    directory-identity map to equal source_tree, and repeat all of it immediately before the spawn
    (the alias check too). Then pass the same source descriptor to spawn (fchdir). Reused unchanged
    in substance; the mount boundary is the view's binds, not v5's single mount. Installed body is
    the cited base-frame code."""
    raise NotImplementedError('base-frame child admission (scratch.py), re-homed onto the view binds')


def spawn_target(argv, environment, source_dir):
    """v5 `spawn` (base frame): fchdir into the held source descriptor and exec the exact allowlisted
    target command T with the view's environment, inheriting the view (U8, the seccomp filter, the
    Landlock domain, the scope). T is the untrusted side; everything confining it was built by RL.
    C spawns T; it opens no other process's /proc and performs no boundary call. Installed body is
    the cited base-frame spawn (streams to the two stream files; v5 memory/heavy-process gates
    preserved, FRAME.md 'Preserved unchanged')."""
    raise NotImplementedError('base-frame spawn (scratch.py spawn): fchdir(source) + exec T in the view')


def main(argv):
    require(len(argv) >= 2 and argv[1] in VERBS, 'usage: launch_target.py (%s) …' % '|'.join(VERBS))
    verb = argv[1]
    # L: read+verify RL_IDENTITY (fd 0) and /proc/self/exe mount id, do the view admission, block
    #    signals (FRAME.md N09), then exec C after GO.
    # C: re-read the held descriptors, repeat admission + the identity map + the alias check
    #    immediately before the spawn, then spawn_target().
    # O: read+verify RL_IDENTITY, take the v5 observations in its own view/scope, retain them.
    # These bodies are the base frame v6 scratch.py child/observe/spawn semantics (cited in
    # MANIFEST.json), re-homed onto the view; this enforcement-core copy fixes the RL_IDENTITY and
    # self-exe-mount authentication and leaves the reviewed admission/spawn to the installed member.
    raise NotImplementedError('installed verb bodies: RL_IDENTITY + self-exe-mount verify, then the '
                              'base-frame child/observe/spawn re-homed onto the view (v11 §12.2 step 16)')


if __name__ == '__main__':
    raise SystemExit('launch_target.py is FROZEN DRAFTING source for review; it is not run here')
    # main(sys.argv)   # the installed entrypoint, shown and deliberately unreachable in this copy
