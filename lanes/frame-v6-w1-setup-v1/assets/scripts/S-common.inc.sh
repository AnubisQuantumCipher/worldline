# SOURCE-ONLY TRANSCRIPTION of the v11 Section 11.5 common script header. NOT EXECUTED.
# Every setup script S-A..S-J begins with these lines; only S and the umask differ
# (umask 077, except S-C and S-E which use 022). <W> and <N> are the fixed numeric
# identities; this package instantiates the Section 3.1 candidates W=950, N=951 (the
# concrete inventory re-verifies and pins them; see assets/notes/numeric-identity.md).
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
staged_install() {
  # $1 staged source, $2 final path, $3 owner, $4 group, $5 mode
  d=${2%/*}; b=${2##*/}; t="$d/.$b.new"
  need_absent "$t" "$2"
  /usr/bin/install -o "$3" -g "$4" -m "$5" "$1" "$t"
  /usr/bin/sync -- "$t"
  check --empty -- /usr/bin/cmp -s "$1" "$t"
}
staged_activate() {
  # $1 final path
  d=${1%/*}; b=${1##*/}; t="$d/.$b.new"
  /usr/bin/mv -T -n -- "$t" "$1"
  /usr/bin/sync -- "$d"
  need_absent "$t"
}
staged_deactivate() {
  d=${1%/*}; b=${1##*/}; t="$d/.$b.new"
  /usr/bin/mv -T -n -- "$1" "$t"
  /usr/bin/sync -- "$d"
  need_absent "$1"
}
