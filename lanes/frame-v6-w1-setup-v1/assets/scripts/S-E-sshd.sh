# SOURCE-ONLY TRANSCRIPTION of v11 Section 11.5 S-E (install the sshd DenyUsers drop-in
# via staged rename, with sshd -t validation and fail-closed deactivation). NOT EXECUTED.
# The reviewed byte line is assets/sshd_config.d/30-wlscratch.conf.
# <common lines, S=E; umask 022>
set -eu; umask 022
st=/root/wlscratch-staging
py='/usr/bin/python3 -I -B'
S=E
step() { $py "$st/step.py" "$1" "$S" "$2"; }
need_absent() { $py "$st/absent.py" "$@"; }
check() { $py "$st/check_out.py" "$@"; }
staged_install() {
  d=${2%/*}; b=${2##*/}; t="$d/.$b.new"
  need_absent "$t" "$2"
  /usr/bin/install -o "$3" -g "$4" -m "$5" "$1" "$t"
  /usr/bin/sync -- "$t"
  check --empty -- /usr/bin/cmp -s "$1" "$t"
}
staged_activate() {
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
f=/etc/ssh/sshd_config.d/30-wlscratch.conf
step begin 0; need_absent "$f"; step done 0
step begin 1; staged_install "$st/30-wlscratch.conf" "$f" root root 0644; staged_activate "$f"; step done 1
step begin 2
if ! /usr/bin/sshd -t; then
  staged_deactivate "$f"
  echo "S-E: sshd -t failed; drop-in deactivated to its inert name; run S-R E" >&2; exit 50
fi
rc=0; check --line-ci "$st/sshd-denyusers.expected" -- /usr/bin/sshd -T -C user=wlscratch,host=localhost,addr=127.0.0.1 || rc=$?
case $rc in
  0) : ;;
  *) echo "S-E: DenyUsers not shown by a successful sshd -T (status $rc); run S-R E" >&2; exit 51 ;;
esac
step done 2
step begin 3; /usr/bin/systemctl reload sshd.service; step done 3
