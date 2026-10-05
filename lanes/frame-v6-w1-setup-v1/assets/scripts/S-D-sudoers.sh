# SOURCE-ONLY TRANSCRIPTION of v11 Section 11.5 S-D (install the two sudoers drop-ins
# via staged rename, with visudo validation and fail-closed deactivation). NOT EXECUTED.
# The reviewed bytes are assets/sudoers.d/wlscratch-frame and assets/sudoers.d/wlscratch-rl.
# <common lines, S=D; umask 077>
set -eu; umask 077
st=/root/wlscratch-staging
py='/usr/bin/python3 -I -B'
S=D
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
step begin 0
need_absent /etc/sudoers.d/wlscratch-frame /etc/sudoers.d/wlscratch-rl
/usr/bin/visudo -cf "$st/sudoers/wlscratch-frame"
/usr/bin/visudo -cf "$st/sudoers/wlscratch-rl"
step done 0
step begin 1
staged_install "$st/sudoers/wlscratch-frame" /etc/sudoers.d/wlscratch-frame root root 0440
/usr/bin/visudo -cf /etc/sudoers.d/.wlscratch-frame.new
staged_activate /etc/sudoers.d/wlscratch-frame
step done 1
step begin 2
staged_install "$st/sudoers/wlscratch-rl" /etc/sudoers.d/wlscratch-rl root root 0440
/usr/bin/visudo -cf /etc/sudoers.d/.wlscratch-rl.new
staged_activate /etc/sudoers.d/wlscratch-rl
step done 2
step begin 3
if ! /usr/bin/visudo -c; then
  staged_deactivate /etc/sudoers.d/wlscratch-rl
  staged_deactivate /etc/sudoers.d/wlscratch-frame
  echo "S-D: visudo -c failed; both rules deactivated to their inert names; run S-R D" >&2; exit 40
fi
step done 3
