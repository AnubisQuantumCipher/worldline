**Operational-review proposal only. No launch, admission, source change, or D158 reset.**

Pre-register a fresh owner-only directory:

```text
/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-xgen-root-control-v1
```

Its two capture files must be absent. Register **16,777,216 bytes** for captures, plus an explicit metadata allowance. With a 1MiB metadata allowance, fresh admission minimum becomes **24,068,744,192 bytes**. Preserve the original package’s complete **14,050,918,400-byte** overlap budget and **10,000,000,000-byte** reserve.

Proposed command, after independently retained preflight/admission:

```bash
/usr/bin/env -i \
  PATH=/usr/bin LC_ALL=C TZ=UTC \
  HOME=/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/completion-20261026/o1-xgen-build-v1/control \
  PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 \
  XDG_RUNTIME_DIR="/run/user/$UID" \
  DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$UID/bus" \
  /usr/bin/bash --noprofile --norc -c '
    set -euC
    umask 077
    [[ ! -o posix ]] || exit 125
    [[ "$(ulimit -H -f)" == unlimited ]] || exit 125
    ulimit -S -f 8192
    [[ "$(ulimit -S -f)" == 8192 ]] || exit 125
    [[ "$(ulimit -H -f)" == unlimited ]] || exit 125
    cd /home/sicarii/Work/worldline-phase1-direct-20261019
    exec /usr/bin/python3 -B -W error \
      records/phase1-direct/factory-20261101/o1-xgen-build-package-v2/xgen_guard.py \
      >"$1/stdout" 2>"$1/stderr" </dev/null
  ' xgen-root-launch \
  /home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-xgen-root-control-v1
```

Clean Bash uses 1024-byte `ulimit -f` blocks; `8192` is exactly 8MiB. `-S` preserves the unlimited hard limit. `noclobber` prevents ordinary capture-file replacement; the independently created, checked directory and absent targets are necessary prerequisites. Add `/usr/bin/env` and `/usr/bin/bash` identities and the exact command bytes to the operational packet.

The soft limit is **documented to survive scope launch**: heavy uses `systemd-run --scope` at `phase1_heavy.py:89`; the installed `systemd-run(1)` description says scope commands execute under systemd-run and inherit the caller’s execution environment. Actual worker limits remain UNRUN until observed. Scope inheritance is not needed to bound root streams: heavy redirects systemd-run and descendants to JOB captures at `93–94`. Root-emitting Git/flock/numfmt and outer cleanup-systemctl processes retain the shell’s soft limit. Compiler/archive children raise only their own limits after receiving separately redirected streams.

Required outcome handling:

- Capture creation/redirection/exec failure, signal termination, actual nonzero exit, detected close/write failure, missing capture, or size **≥8MiB** means FAILED. Retain partial files; never truncate or retry automatically. Pre-redirection shell failures also require retained external tool-session output.
- Root must retain the actual tool-process exit, independently reopen/stat/hash both regular capture files, and record their final sizes. Expected successful root streams are empty; unexplained output cannot be silently accepted.
- Normal completion requires guard/heavy receipts, reaped launcher exit, exact owned-unit terminal observation, and the existing populated-zero or complete normal collected-scope conditions.
- Failure requires launcher quiescence followed by exact-scope reconciliation using the existing pinned functions/native commands. Bare-PID reconstruction of `Popen` ownership is invalid. Missing launcher identity or incomplete cleanup remains **UNVERIFIED**, prohibiting a successor.
- Repeat carrier HEAD `7a3127281389f58f2291c86d123ec1f920cee6b7`, package manifest/payload, helper, source/tool-pin and protected-pin identity readback afterward. No successful capture or exit establishes O1/Phase One acceptance or fsync durability.