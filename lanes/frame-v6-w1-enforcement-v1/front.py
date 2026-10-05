"""WORLDLINE Phase One — W-1 frame-v6w1 member F: the front / coordinator.

FROZEN, REVIEWABLE, UNINSTALLED DRAFTING source. Author: Claude (Opus 4.8), DRAFTING implementer,
not a reviewer. ESTABLISHES NO PREMISE; EXECUTED NOWHERE, INSTALLED NOWHERE this session.

Role (v11 §3.2, §8.2). F = the lead's REAL non-isolated outer invocation
`/usr/bin/python3 -B /opt/wlscratch/frame-v6w1/front.py <verb> …`, uid 1000 (sicarii). Verbs:
adopt, materialize, dispatch. F keeps v5's real outer invocation (§8.2): it does the lead-side
bookkeeping, the fresh lead observation, custody, and the shared-window protocol, and it drives the
privileged writer W through the S1 sudoers rule. F itself holds NO writer authority.

The privilege chain, exactly (v11 §3.2):   lead → F → [S1 sudo] → W(writer.py) → [RL sudo] → RL(sandbox_launch.py) → L/O
  - F starts S1:  sudo -n -u wlscratch -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py <verb> …
  - W starts RL (the RL sudoers rule); F NEVER starts RL and NEVER builds a view.
(The operator directive's one-line summary "front … issues RL and writer" compresses this chain;
the authoritative v11 §3.2/§5.1 placement is: F→W via S1, W→RL via the RL rule, the LEASE is W's.
This member follows v11; SELFCHECK.md records the reconciliation.)

WHAT F WRITES (v11 §3.4 "No new outside-tree authority"). F writes NOTHING in the protected run
tree T — every generation record is written by W inside T. F's ONLY outside-tree writes are v5's
shared-window protocol (frame-plan note N07, the one deliberate outside-tree write), unchanged.
F reads lead inputs (sicarii-owned, O_NOATIME where owner; foreign-owned inputs stay accepted,
read without the flag — v11 §9.8 R-c/R-d) and streams them to W over the channel; it writes the
bytes into no file of its own. Enforcing "F writes nothing in T" keeps the N0(c) obligation visible
but does NOT discharge V5-B02 (OPEN).
"""
import sys


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


require(sys.flags.optimize == 0, 'refusing to run under Python optimization: gates must not be removable')
sys.dont_write_bytecode = True

import os, signal
from pathlib import Path

import framelib
from framelib import now

INSTALL_ROOT = Path('/opt/wlscratch/frame-v6w1')
PYTHON = '/usr/bin/python3'
SUDO = '/usr/bin/sudo'
WLSCRATCH_USER = 'wlscratch'
# The shared build/proof window — the ONE inherited outside-tree object (v5 N07; v11 §9.4). F uses
# the cooperating flock protocol on its single-link .lock, unchanged from the base frame.
WINDOW = Path('/home/sicarii/Documents/Codex/2026-09-30/how-do-u-feel-about-the/work/worldline-build-proof-window.json')
SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
VERBS = ('adopt', 'materialize', 'dispatch')


def start_writer(verb, writer_args, channel_socket_fd, out_fd, err_fd):
    """Start W through the S1 sudoers rule (v11 §3.2):
      sudo -n -u wlscratch -- /usr/bin/python3 -I -B /opt/wlscratch/frame-v6w1/writer.py <verb> <args>
    F hands W EXACTLY three descriptors (v11 §12.2 step 3, inherited by RL unchanged): fd 0 the
    channel socket, fds 1-2 the stream files; every other descriptor is close-on-exec. The argv
    carries only the sealed grammar W (and later RL) re-reads and re-checks itself. DRAFTING: the
    argv/fd wiring is constructed; nothing is spawned here."""
    argv = [SUDO, '-n', '-u', WLSCRATCH_USER, '--',
            PYTHON, '-I', '-B', str(INSTALL_ROOT / 'writer.py'), verb] + list(writer_args)
    # installed body: subprocess with close_fds=True and stdin=channel_socket_fd, stdout=out_fd,
    # stderr=err_fd, so W inherits exactly {0,1,2}. Not executed in this copy.
    return {'argv': argv, 'fds': {0: channel_socket_fd, 1: out_fd, 2: err_fd}}


def window_reserve(holder, token):
    """v5/v6 shared-window protocol (frame-plan N07; base frame scratch.py window_locked:1263,
    window_write:1287, reserve:1304). The flock is LOCK_EX on the window's single-link .lock; F
    refuses on a prior reservation and records token ownership and history. This is F's ONLY
    outside-tree write and is unchanged from the base frame. Installed body is the cited base-frame
    code; drafting cites it rather than re-transcribing."""
    raise NotImplementedError('base-frame window protocol (scratch.py:1263-1346), reused unchanged')


def window_release(ctx):
    """v5/v6 release (scratch.py release:1330): only F (the launching parent) releases, and only on
    an observed terminal state with no unresolved participant record (FRAME.md 'Window and
    ownership'). A killed/dead F leaves the window reserved until an operator-visible manual
    resolution — no late collector (FRAME.md 'Missing release'). Reused unchanged."""
    raise NotImplementedError('base-frame release (scratch.py:1330), reused unchanged')


def census_and_holder_state():
    """v11 §9.4 — the census, holder state, known-terminal ownership and the release rule. F reads
    only world-readable /proc/<pid>/{cmdline,status,stat} of its OWN participants and the window
    record; it opens no other process's mem/fd/root/cwd. Reused from the base frame's owned-terminal
    observation (FRAME.md V4-B02 'Raw records are never trusted')."""
    raise NotImplementedError('base-frame owned-terminal census (scratch.py owned_terminal), reused')


def main(argv):
    require(len(argv) >= 2 and argv[1] in VERBS, 'usage: front.py (%s) …' % '|'.join(VERBS))
    verb = argv[1]
    # F blocks SIGNALS across its terminal path (FRAME.md N09) and runs the reviewed v5/v6 verb
    # logic: fresh lead observation; read lead inputs (O_NOATIME where owner); open the channel to
    # W; start W via start_writer(); stream inputs; run the window protocol (the one outside-tree
    # write); observe the owned-terminal census; and, for `adopt`, request W to write the §4.6
    # adoption record INSIDE T (F writes no adoption record itself — v11 §4.6 moved it into T).
    # Those bodies are the base frame v6 scratch.py semantics (cited in MANIFEST.json); this
    # enforcement-core copy fixes the privilege chain and the "F writes nothing in T" invariant and
    # leaves the reviewed verb bodies to the installed member.
    raise NotImplementedError('installed verb bodies: v5/v6 lead-side logic + start_writer() + the '
                              'window protocol; F writes nothing in T (v11 §3.4, §4.6, §8.2, §9)')


if __name__ == '__main__':
    raise SystemExit('front.py is FROZEN DRAFTING source for review; it is not run here')
    # main(sys.argv)   # the installed entrypoint, shown and deliberately unreachable in this copy
