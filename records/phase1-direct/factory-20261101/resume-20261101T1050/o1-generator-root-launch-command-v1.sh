/usr/bin/env -i \
  PATH=/usr/bin LC_ALL=C TZ=UTC \
  HOME=/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/completion-20261026/o1-xgen-build-v1/control \
  PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 \
  XDG_RUNTIME_DIR=/run/user/1000 \
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
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
