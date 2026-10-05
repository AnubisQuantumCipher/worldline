# Numeric identity policy (v11 Section 3.1, Section 11.2)

W = 950, N = 951 are the CANDIDATE numbers, instantiated throughout this package's scripts.
They are not yet pinned: the concrete setup inventory fixes them and the prestate re-verifies.

Observed 2026-10-04 (v11 Section 3.1): both 950 and 951 are unused by every passwd and group
entry (lowest used system uid is 957; lowest used gid at or above 900 is 954), lie inside
SYS_UID_MIN..SYS_UID_MAX = 500..999 of /etc/login.defs, and lie outside every range in
/etc/subuid and /etc/subgid.

Per-number prestate predicate (Section 11.2, checks P1-P3, P4):
- `getent passwd n` and `getent group n` exit 2 (absent);
- n in 500..999;
- for every line `owner:start:count` of /etc/subuid and /etc/subgid, n < start or
  n >= start + count (each bound computed with JACKAL in the concrete inventory; all current
  ranges start at 100000 or above);
- no file on any local filesystem is owned by uid n or gid n (P4, operator `find -xdev`).

Section 5.4 subordinate-ID exclusion (observed /etc/subuid == /etc/subgid):
  sicarii:100000:65536, cosmov1lab:165536:65536, wlrehearsal:231072:65536,
  wldrill:362144:65536, worldline:296608:65536.
Both new ids must lie outside every listed range and no range may be allocated to a new
identity, so `sicarii` (and every other user) cannot map them through newuidmap/newgidmap.

After setup (Section 11.2): /etc/subuid and /etc/subgid byte-identical to prestate; getent
shows exactly the two new users and their two user-private groups; shadow password fields of
W and N begin with `!` or `*`; N's account-expiry field is 1; both gshadow entries have no
members and a locked password. N owns no file and no process.
