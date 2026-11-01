#!/usr/bin/bash
# Test-only: inject fault exclusively into final tee, never timeout/Bash/guard.
set -u
base=/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-root-capture-package-v2
path=$(/usr/bin/readlink /proc/$$/fd/1) || exit 125
name=${path##*/}
if [[ $name == "${FIXTURE_FAULT_TARGET-UNSET}" ]]; then
    case ${FIXTURE_FAULT_MODE-UNSET} in
        first_eio|first_enospc|partial|lost_diag|close) ;;
        *) exit 125 ;;
    esac
    exec /usr/bin/env LD_PRELOAD="$base/fault-diag.so" CAPTURE_FAULT="$FIXTURE_FAULT_MODE" \
        /usr/bin/tee "$@"
fi
exec /usr/bin/tee "$@"
