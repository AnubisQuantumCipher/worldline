#!/usr/bin/bash
# D159 operational plumbing, NOT runtime admission. Invoke only through entry.sh.
# Same-UID hostile mutation, OS failure and terminal reconciliation are external gates.
set -uC
umask 077
shopt -u varredir_close
ROOT=/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-root-capture-package-v2/case-10-lost-diag
IO_DEADLINE=0.4s
KILL_GRACE=0.1s
declare -A FILE_IDS=()
OUT_F= ERR_F= OUT_DIAG_F= ERR_DIAG_F= STATUS_F=
P_OUT= P_ERR= P_OUT_PID= P_ERR_PID=
GUARD_STATUS=NOT_STARTED OUT_STATUS=NOT_STARTED ERR_STATUS=NOT_STARTED
FAIL=0
# A caught interruption does not claim cleanup or completed capture.
trap 'exit 125' HUP INT TERM

fail() { FAIL=1; }

close_fd() {
    local fd=$1
    [[ $fd =~ ^[0-9]+$ ]] || return 125
    exec {fd}>&-
}

close_captures() {
    local fd result=0
    for fd in "$OUT_F" "$ERR_F" "$OUT_DIAG_F" "$ERR_DIAG_F"; do
        [[ -z $fd ]] && continue
        close_fd "$fd" || result=125
    done
    return "$result"
}

open_file() {
    local slot=$1 name=$2 fd identity path_identity
    [[ ! -e $ROOT/$name && ! -L $ROOT/$name ]] || return 125
    exec {fd}>"$ROOT/$name" || return 125
    printf -v "$slot" '%s' "$fd" || return 125
    identity=$(/usr/bin/stat -Lc '%f:%h:%u:%a:%d:%i' "/proc/$$/fd/$fd") || return 125
    path_identity=$(/usr/bin/stat -Lc '%f:%h:%u:%a:%d:%i' "$ROOT/$name") || return 125
    [[ -f /proc/$$/fd/$fd && $identity == *:1:1000:600:* && $identity == "$path_identity" ]] || return 125
    FILE_IDS[$name]=$identity
}

prepare() {
    [[ $# == 0 && $UID == 1000 && $EUID == 1000 && ! -o posix ]] || return 125
    [[ -d $ROOT && ! -L $ROOT && -O $ROOT ]] || return 125
    [[ $(/usr/bin/stat -Lc '%a:%u' "$ROOT") == 700:1000 ]] || return 125
    [[ $(ulimit -H -f) == unlimited ]] || return 125
    ulimit -S -f 8192 || return 125
    [[ $(ulimit -S -f) == 8192 && $(ulimit -H -f) == unlimited ]] || return 125
    open_file STATUS_F status || return 125
    open_file OUT_F stdout || return 125
    open_file ERR_F stderr || return 125
    open_file OUT_DIAG_F stdout-consumer.stderr || return 125
    open_file ERR_DIAG_F stderr-consumer.stderr || return 125
}

consume() {
    local target=$1 diagnostic=$2 inherited=$3
    exec 1>&"$target" 2>&"$diagnostic" || exit 125
    if [[ -n $inherited ]]; then close_fd "$inherited" || exit 125; fi
    close_captures || exit 125
    close_fd "$STATUS_F" || exit 125
    exec /usr/bin/timeout --signal=TERM --kill-after="$KILL_GRACE" "$IO_DEADLINE" \
        /usr/bin/bash /home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-root-capture-package-v2/tee-fixture.sh --output-error=exit
}

start_consumers() {
    exec {P_OUT}> >(consume "$OUT_F" "$OUT_DIAG_F" '') || return 125
    P_OUT_PID=$!
    [[ $P_OUT_PID =~ ^[1-9][0-9]*$ ]] || return 125
    exec {P_ERR}> >(consume "$ERR_F" "$ERR_DIAG_F" "$P_OUT") || return 125
    P_ERR_PID=$!
    [[ $P_ERR_PID =~ ^[1-9][0-9]*$ ]] || return 125
}

operational_guard() {
    # BEGIN FIXED GUARD -- tests replace this body, never execute it.
    printf 'lost' || :
    # END FIXED GUARD
}

run_guard() {
    (
        exec 1>&"$P_OUT" 2>&"$P_ERR" </dev/null || exit 125
        close_fd "$P_OUT" || exit 125
        close_fd "$P_ERR" || exit 125
        close_captures || exit 125
        close_fd "$STATUS_F" || exit 125
        operational_guard
    )
    GUARD_STATUS=WAIT_STATUS:$?
    [[ $GUARD_STATUS == WAIT_STATUS:0 ]] || fail
}

finish_consumers() {
    local fd pid rc
    for fd in "$P_OUT" "$P_ERR"; do
        [[ -z $fd ]] && continue
        close_fd "$fd" || fail
    done
    close_captures || fail
    if [[ -n $P_OUT_PID ]]; then
        if wait "$P_OUT_PID"; then rc=0; else rc=$?; fi
        OUT_STATUS=WAIT_STATUS:$rc
    fi
    if [[ -n $P_ERR_PID ]]; then
        if wait "$P_ERR_PID"; then rc=0; else rc=$?; fi
        ERR_STATUS=WAIT_STATUS:$rc
    fi
    [[ $OUT_STATUS == WAIT_STATUS:0 && $ERR_STATUS == WAIT_STATUS:0 ]] || fail
}

check_captures() {
    local name info identity
    for name in stdout stderr stdout-consumer.stderr stderr-consumer.stderr; do
        [[ -f $ROOT/$name && ! -L $ROOT/$name ]] || return 125
        info=$(/usr/bin/stat -Lc '%s:%h:%u:%a' "$ROOT/$name") || return 125
        [[ $info == 0:1:1000:600 ]] || return 125
        identity=$(/usr/bin/stat -Lc '%f:%h:%u:%a:%d:%i' "$ROOT/$name") || return 125
        [[ $identity == "${FILE_IDS[$name]-UNOPENED}" ]] || return 125
    done
}

retain_status() {
    [[ -n $STATUS_F ]] || return 125
    printf '%s\n' 'schema=worldline.root-capture-status.v2' \
        "guard=$GUARD_STATUS" "stdout_consumer=$OUT_STATUS" \
        "stderr_consumer=$ERR_STATUS" "capture_rejected=$FAIL" \
        'cleanup=UNDETERMINED_EXTERNAL_RECONCILIATION_REQUIRED' | (
        exec 1>&"$STATUS_F" || exit 125
        close_fd "$STATUS_F" || exit 125
        exec /usr/bin/timeout --signal=TERM --kill-after="$KILL_GRACE" "$IO_DEADLINE" \
            /usr/bin/bash /home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-root-capture-package-v2/tee-fixture.sh --output-error=exit
    )
    local -a statuses=("${PIPESTATUS[@]}")
    local result=0 info identity
    [[ ${#statuses[@]} == 2 && ${statuses[0]} == 0 && ${statuses[1]} == 0 ]] || result=125
    close_fd "$STATUS_F" || result=125
    [[ -f $ROOT/status && ! -L $ROOT/status ]] || return 125
    info=$(/usr/bin/stat -Lc '%s:%h:%u:%a' "$ROOT/status") || return 125
    [[ $info =~ ^[1-9][0-9]{0,3}:1:1000:600$ ]] || return 125
    identity=$(/usr/bin/stat -Lc '%f:%h:%u:%a:%d:%i' "$ROOT/status") || return 125
    [[ $identity == "${FILE_IDS[status]-UNOPENED}" ]] || return 125
    return "$result"
}

main() {
    if prepare "$@"; then
        if start_consumers; then run_guard; else fail; fi
    else
        fail
    fi
    finish_consumers
    check_captures || fail
    retain_status || fail
    [[ $FAIL == 0 ]]
}

main "$@"
