#!/usr/bin/bash
# Prospective exact entry; source/tool/admission checks MUST precede invocation.
exec /usr/bin/env -i PATH=/usr/bin LC_ALL=C TZ=UTC \
  HOME=/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/completion-20261026/o1-xgen-build-v1/control \
  PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 XDG_RUNTIME_DIR=/run/user/1000 \
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
  /usr/bin/bash --noprofile --norc \
  /home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-root-capture-package-v2/launch.sh
