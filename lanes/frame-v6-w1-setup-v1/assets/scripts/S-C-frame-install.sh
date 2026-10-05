# SOURCE-ONLY TRANSCRIPTION of v11 Section 11.5 S-C (install the frozen frame-v6w1
# tree from the verified staging copy). NOT EXECUTED. Depends on the frozen frame
# members (front.py, writer.py, sandbox_launch.py, launch_target.py, ...) existing in
# the staging copy; those members are MISSING as of this package (see GAP.md), so this
# script cannot be filled with a real frame-members.list / frame-dirs.list yet.
# <common lines, S=C; umask 022>
set -eu; umask 022
st=/root/wlscratch-staging
py='/usr/bin/python3 -I -B'
S=C
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
step begin 0; need_absent /opt/wlscratch; step done 0
step begin 1.1; /usr/bin/install -d -o root -g root -m 0755 /opt/wlscratch; step done 1.1
step begin 1.2; /usr/bin/install -d -o root -g root -m 0755 /opt/wlscratch/frame-v6w1; step done 1.2
i=0
while read -r d; do
  i=$((i+1)); step begin "2.$i"
  /usr/bin/install -d -o root -g root -m 0755 "/opt/wlscratch/frame-v6w1/$d"
  step done "2.$i"
done < "$st/frame-dirs.list"
i=0
while read -r m; do
  i=$((i+1)); step begin "3.$i"
  staged_install "$st/frame/$m" "/opt/wlscratch/frame-v6w1/$m" root root 0644
  staged_activate "/opt/wlscratch/frame-v6w1/$m"
  step done "3.$i"
done < "$st/frame-members.list"
step begin 4; /usr/bin/sha256sum -c --strict "$st/frame-members.abs.sha256"; step done 4
