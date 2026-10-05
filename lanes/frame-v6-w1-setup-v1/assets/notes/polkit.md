# polkit: NO rule is installed by W-1 (by design)

The directive lists "any polkit rule" as an asset to produce. For W-1 v11 the correct
artifact is the ABSENCE of one, recorded here so the reviewer can see it is deliberate.

W-1 installs **no** polkit rule, pkla, or action-default change. The polkit requirement is
an **inventory obligation**, not an installed artifact:

- Section 5.3 (route table) and Section 11.3 P13 require the operator to SHOW, over every
  subject (not only `sicarii` or a group it is in), that no polkit authority grants a
  passwordless path to manage a unit or exec as another user that could resolve to W or N
  (for example `org.freedesktop.systemd1.manage-units`, `org.freedesktop.policykit.exec`,
  a `systemd-run --uid=` path, or machine shell/login actions), and that `empower` and
  `docker` groups have no members.
- This is premise P-NOOWNER's polkit half (W1-V9-NOOWNER-SCOPE). It is discharged by the
  operator-produced inventory carried in operator-package item O-1 and read by the
  frame's S-5/E0 code review for non-reliance; it is NEVER satisfied by widening polkit.

DEFENSIVE boundary. Nothing in this package weakens polkit to avoid authentication. If the
operator inventory finds a polkit grant that resolves to W or N, that is a refutation of
P-NOOWNER and forces redesign (Section 9.8 N7) — it is never worked around.
