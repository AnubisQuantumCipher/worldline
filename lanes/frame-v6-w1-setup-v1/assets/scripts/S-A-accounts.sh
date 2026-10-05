# SOURCE-ONLY TRANSCRIPTION of v11 Section 11.5 S-A (accounts and groups, atoms k1-k4).
# NOT EXECUTED. Creates the two locked system identities: wlscratch (W=950) and
# wlscratch-ns (N=951, additionally account-expired). --no-create-home; shell nologin.
# <common lines, S=A; umask 077>  (see S-common.inc.sh; S is set to A here)
set -eu; umask 077
st=/root/wlscratch-staging
py='/usr/bin/python3 -I -B'
S=A
step() { $py "$st/step.py" "$1" "$S" "$2"; }
need_absent() { $py "$st/absent.py" "$@"; }
check() { $py "$st/check_out.py" "$@"; }
no_entry() {
  rc=0; /usr/bin/getent "$1" "$2" >/dev/null || rc=$?
  case $rc in
    2) : ;;
    0) echo "S-$S: $1 entry $2 exists" >&2; exit 10 ;;
    *) echo "S-$S: getent $1 $2 failed with status $rc" >&2; exit 13 ;;
  esac
}
lock_account() {
  line=$(check --print -- /usr/bin/getent shadow "$1")
  pw=${line#*:}; pw=${pw%%:*}
  case $pw in '!'*|'*'*) : ;; *) /usr/bin/usermod -L "$1" ;; esac
  line=$(check --print -- /usr/bin/getent shadow "$1")
  pw=${line#*:}; pw=${pw%%:*}
  case $pw in '!'*|'*'*) : ;; *) echo "S-A: $1 not locked" >&2; exit 12 ;; esac
  need_absent "/var/spool/mail/$1"
}
step begin 0
for n in wlscratch wlscratch-ns; do no_entry passwd "$n"; no_entry group "$n"; done
for i in 950 951; do no_entry passwd "$i"; no_entry group "$i"; done
need_absent /var/spool/mail/wlscratch /var/spool/mail/wlscratch-ns /var/lib/wlscratch-ns
step done 0
step begin 1; /usr/bin/groupadd --system --gid 950 wlscratch; step done 1
step begin 2; /usr/bin/groupadd --system --gid 951 wlscratch-ns; step done 2
step begin 3
/usr/bin/useradd --system --uid 950 --gid 950 --no-create-home --home-dir /var/lib/wlscratch \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch frame writer' wlscratch
step done 3
step begin 4; lock_account wlscratch; step done 4
step begin 5
/usr/bin/useradd --system --uid 951 --gid 951 --no-create-home --home-dir /var/lib/wlscratch-ns \
  --shell /usr/bin/nologin --comment 'WORLDLINE scratch view namespace owner' wlscratch-ns
step done 5
step begin 6
lock_account wlscratch-ns
/usr/bin/usermod -e 1 wlscratch-ns
line=$(check --print -- /usr/bin/getent shadow wlscratch-ns)
case $line in *:1:*) : ;; *) echo "S-A: wlscratch-ns not expired" >&2; exit 14 ;; esac
step done 6
