# D159 revision2 outer CORE control; never runtime admission by itself.
ulimit -S -c 0 || exit 125
ulimit -H -c 0 || exit 125
[[ "$(ulimit -S -c)" == 0 && "$(ulimit -H -c)" == 0 ]] || exit 125
[[ "$(ulimit -H -f)" == unlimited ]] || exit 125
exec /usr/bin/bash --noprofile --norc /home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/factory-20261101/o1-root-capture-package-v2/entry.sh
