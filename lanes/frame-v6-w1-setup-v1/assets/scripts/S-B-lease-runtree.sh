# SOURCE-ONLY TRANSCRIPTION of v11 Section 11.5 S-B (writer home, lease, run tree;
# WITHOUT images). NOT EXECUTED. With images, steps 4.1/4.2 are replaced by S-J and
# steps 5.1-5.4 apply to the image roots. W=950 instantiated for <W>.
# <common lines, S=B; umask 077>
set -eu; umask 077
st=/root/wlscratch-staging
py='/usr/bin/python3 -I -B'
S=B
step() { $py "$st/step.py" "$1" "$S" "$2"; }
need_absent() { $py "$st/absent.py" "$@"; }
check() { $py "$st/check_out.py" "$@"; }
step begin 0; need_absent /var/lib/wlscratch /opt/wlscratch; step done 0
step begin 1; /usr/bin/install -d -o root -g 950 -m 0750 /var/lib/wlscratch; step done 1
step begin 2; /usr/bin/install -d -o root -g 950 -m 0750 /var/lib/wlscratch/lease; step done 2
step begin 3
/usr/bin/install -o root -g 950 -m 0440 "$st/empty" /var/lib/wlscratch/lease/writer.lock
v=$(check --print -- /usr/bin/stat -c '%F %h %s %u %g %a' /var/lib/wlscratch/lease/writer.lock)
[ "$v" = "regular empty file 1 0 0 950 440" ]
step done 3
step begin 4.1; /usr/bin/install -d -o 950 -g 950 -m 0700 /var/lib/wlscratch/runs; step done 4.1
step begin 4.2; /usr/bin/install -d -o 950 -g 950 -m 0700 /var/lib/wlscratch/runs/records; step done 4.2
step begin 5.1
/usr/bin/setfacl -m u:1000:--x /var/lib/wlscratch
check --equal "$st/acl/var-lib-wlscratch.expected" -- /usr/bin/getfacl -n -c -p /var/lib/wlscratch
step done 5.1
step begin 5.2
/usr/bin/setfacl -m u:1000:--x /var/lib/wlscratch/runs
check --equal "$st/acl/runs.expected" -- /usr/bin/getfacl -n -c -p /var/lib/wlscratch/runs
step done 5.2
step begin 5.3
/usr/bin/setfacl -m u:1000:--x /var/lib/wlscratch/runs/records
check --equal "$st/acl/records.expected" -- /usr/bin/getfacl -n -c -p /var/lib/wlscratch/runs/records
step done 5.3
step begin 5.4
check --equal "$st/acl/lease.expected" -- /usr/bin/getfacl -n -c -p /var/lib/wlscratch/lease /var/lib/wlscratch/lease/writer.lock
step done 5.4
