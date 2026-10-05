# Expected-ACL files (DEFENSIVE confinement config; reconstructed — must be re-pinned)

These `*.expected` files are the `getfacl -n -c -p` outputs that S-B's `check --equal`
steps compare against, holding the Section 6.3 access-ACL texts. They are the sandbox's
own locked-down permission grants (a single `user:1000:--x` search entry for the lead on
`/var/lib/wlscratch`, `runs/` and `runs/records`; no extended ACL on `lease/` or
`writer.lock`).

Source of each entry body (v11 Section 6.3 table):

| Object | base mode | access ACL entries (getfacl -n order) |
|---|---|---|
| `/var/lib/wlscratch` | 0750 | `user::rwx user:1000:--x group::r-x mask::r-x other::---` |
| `runs/` (T_root) | 0700 | `user::rwx user:1000:--x group::--- mask::--x other::---` |
| `runs/records` (R_root) | 0700 | `user::rwx user:1000:--x group::--- mask::--x other::---` |
| `lease/` | 0750 | none (base entries only) |
| `lease/writer.lock` | 0440 | none (base entries only) |

HONESTY CAVEAT (status: reconstructed, NOT observed). The entry bodies above are
transcribed from the specification. The EXACT bytes `getfacl -n -c -p` emits — trailing
newlines, and the per-file block separation when S-B step 5.4 runs `getfacl` over the two
`lease` operands in one call — were NOT observed by this drafting session (no command was
executed). `lease.expected` is therefore deliberately omitted rather than guessed. The
concrete setup inventory (INSTALL-ORDER.md step 3) MUST generate every `*.expected`
file by observing `getfacl -n -c -p` on the real objects during a reviewed dry build and
pin its sha256; these reconstructed single-object files are review aids, not the pinned
artifacts.
