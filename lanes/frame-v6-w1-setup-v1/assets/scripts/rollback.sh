# SOURCE-ONLY TEMPLATE of the v11 Section 15.1 rollback state machine (operator; every
# step's before and after state captured raw). NOT EXECUTED. This is a reviewable skeleton:
# the per-step raw before/after captures, the retained-tree manifests M0/M1 and each
# equality comparison are filled and pinned by the concrete inventory + operator package
# O-4; they are NOT inlined here. The rollback is its OWN state machine, not the inverse of
# setup: it starts from a complete setup that has run (observation = G_N plus runtime growth)
# and it RETAINS every tree. W=950, N=951 instantiated.
#
# Reversal uses the same staged_deactivate discipline as S-D/S-E (rename final -> inert,
# sync, confirm absent, preserve bytes+sha256, then remove after full-byte equality).
# Nothing is called restored/removed without its equality capture. Runtime growth is NEVER
# "reversed"; the trees are retained and compared.
set -eu; umask 077
st=/root/wlscratch-staging
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
rb="$st/rollback-$stamp"            # per-rollback capture directory (O_EXCL, operator-created)
py='/usr/bin/python3 -I -B'
need_absent() { $py "$st/absent.py" "$@"; }
# capture <label> : the operator's reviewed raw-capture helper (getent/lstat/getfacl -n -c -p/
# digests/entry sets/link counts/systemctl show/sshd -T), each producer under check_out.py.
# Its exact body is pinned by O-4; here it is a named obligation.
capture() { : "operator O-4 raw capture: $1"; }

# M0: retained-tree manifest of /var/lib/wlscratch (and /var/lib/wlscratch-images with images):
# every entry's path, type, size, sha256 (regular files), owner, group, mode and ACL digest.
capture "M0 retained-tree manifest"

# R1  revoke new launches: deactivate the S1 (frame) rule; preserve bytes+sha256; visudo -c;
#     remove the inert file after equality. Postcondition: both names absent; preserved copy
#     equal; visudo -c passes; no new writer can start.
capture "R1 before"
/usr/bin/mv -T -n -- /etc/sudoers.d/wlscratch-frame /etc/sudoers.d/.wlscratch-frame.new
/usr/bin/sync -- /etc/sudoers.d
# preserve .wlscratch-frame.new bytes + sha256 into "$rb/" (operator O-4), then:
/usr/bin/visudo -c
# remove inert only after full-byte equality with the preserved reviewed bytes (operator check)
capture "R1 after"; need_absent /etc/sudoers.d/wlscratch-frame /etc/sudoers.d/.wlscratch-frame.new

# R2  wait for and reconcile every pending/running participant: no process with uid W
#     (including writers started before R1); no sudo process naming a frame entry; every RL
#     scope absent or populated 0 and not live (K and M, Section 9.4); RL's root-scan
#     conditions (no uid-N process, no N-owned user namespace outside RL scopes). A live
#     participant is WAITED FOR; killing one is a separate, recorded, explicit operator
#     decision; any UNKNOWN holds the rollback here.
capture "R2 participant reconciliation"

# R3  the shared window: if reserved by a W-1 attempt and known-terminal ownership is
#     uncertain -> HOLD; if ownership is known terminal and the reserving front is gone, the
#     operator resolves it explicitly and records the resolution. The frame never does.
capture "R3 window state"

# R4  deactivate the RL rule; preserve; visudo -c; remove after equality (as R1).
capture "R4 before"
/usr/bin/mv -T -n -- /etc/sudoers.d/wlscratch-rl /etc/sudoers.d/.wlscratch-rl.new
/usr/bin/sync -- /etc/sudoers.d
/usr/bin/visudo -c
capture "R4 after"; need_absent /etc/sudoers.d/wlscratch-rl /etc/sudoers.d/.wlscratch-rl.new

# R5  images, if used: identify every start source first (two mount units,
#     systemctl list-dependencies --reverse of each, any automount unit, fstab: none
#     expected); systemctl disable both; verify no process has a file open on them and R2
#     still holds; stop records unit first, work unit second (unmount); verify each unmounted
#     and each bare mount point equals its setup identity; preserve unit files, deactivate +
#     remove, systemctl daemon-reload, verify no remount; KEEP the image files, record sha256.
capture "R5 images (only if images configuration)"

# R6  nothing is restored in /home/sicarii: W-1 sets no ACL there.

# R7  lock and expire W (N is already locked and expired); keep BOTH accounts so evidence
#     ownership keeps its meaning. Postcondition: W locked and expired; N unchanged.
capture "R7 before"
/usr/bin/usermod -L -e 1 wlscratch
capture "R7 after"

# R8  deactivate the sshd drop-in; preserve; sshd -t; systemctl reload sshd; remove after
#     equality. Postcondition: drop-in absent; sshd -T without S-E's DenyUsers line.
capture "R8 before"
/usr/bin/mv -T -n -- /etc/ssh/sshd_config.d/30-wlscratch.conf /etc/ssh/sshd_config.d/.30-wlscratch.conf.new
/usr/bin/sync -- /etc/ssh/sshd_config.d
/usr/bin/sshd -t
/usr/bin/systemctl reload sshd.service
capture "R8 after"; need_absent /etc/ssh/sshd_config.d/30-wlscratch.conf

# R9  keep as evidence: /var/lib/wlscratch (generations, records, exports, captures),
#     /opt/wlscratch, /root/wlscratch-staging (step logs + every rollback capture) and every
#     capture; capture the retained-tree manifest M1. Postcondition: M1 EQUALS M0 (the
#     retained trees were not changed by the rollback); any difference stops for an explicit
#     operator decision.
capture "M1 retained-tree manifest"
# operator: assert M1 == M0, else STOP for an explicit operator decision.
