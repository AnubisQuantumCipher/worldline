# W-1 v2 prototype results (ENGINEERING_ONLY)

None of these is proof, review, admission, setup or acceptance evidence. V5-B01, V5-B02 and every original obligation
stay OPEN.

## 1. Writer-side mechanisms, same-user simulation (2026-10-04 23:39:12Z)

**Code:** `w1proto.py` (`2c7d6100…`) and `selftest_w1proto.py` (`56d3da40…`).
**Result:** 27/27 as required. The cases cover:
- **Lease:** exclusive across processes; re-acquired after release. A wrong mode, a hard link or a symlink is refused,
  and an absent lease file is refused and never created.
- **Chained framing:** tamper, reorder, truncation, non-canonical, extra-field, oversize and wrong-sequence frames are
  all refused.
- **Streamed-input pins:** pin mismatch, digest or size lies, unknown paths, traversal, absolute paths, duplicates,
  missing pins and bad modes are all refused.
- **Non-dumpable:** the read-back shows `PR_GET_DUMPABLE=0` and `/proc/self/fd` owned by root.

**Output:** `results-2026-10-04T233912Z/selftest.json` (`dfe360f2…`).

## 2. Kernel DAC probe across genuinely different UIDs (2026-10-04 23:46:52Z)

**Code:** `dacprobe_outer.py` (`bbf70984…`) and `dacprobe_inner.py` (`c8dcf66f…`).
**Output:** `dacprobe-2026-10-04T234652Z/dacprobe.json` (`e7673b19…`).

**Mechanism.** A rootless user namespace, using the operator-configured subordinate ranges
`/etc/subuid` and `/etc/subgid` `sicarii:100000:65536`. The mapping is inner 0 → outer 1000, and inner 1..65536 →
outer 100000..165535. No root and no new account is involved.
- Files exist on disk, owned by real outer UIDs:
  - the writer tree by **100000**;
  - the target's output by **100001**;
  - the writer home by **100002**, standing in for root.
- The lead's probes run outside the namespace as genuine uid 1000. Every outcome is decided by the kernel's ordinary
  DAC, POSIX ACLs and `fs.protected_hardlinks=1`.
- Everything lives in a sacrificial `/tmp/wl-dacprobe-*` directory. `/tmp` is used because `/home/sicarii` is not
  traversable by other UIDs. The directory was removed afterwards; verified absent.

**Result: 30/30 as required.**

| Actor | Allowed (positive controls) | Refused (as required) |
|---|---|---|
| Second writer (100000) while the lease is held | — | lease → `LeaseHeld`. A later writer re-acquires the lease after release: ok |
| Target (100001) | create a file and a directory in its output partition; read the admitted source; a symlink in its partition (allowed by design, because the frame's walk refuses symlinks) | create in frame records, write the admitted source, create beside the source, rename the partition, unlink a frame record, rename the generation, create in `runs`, open the lease file → EACCES. Hard-link a frame record, chmod the source → EPERM |
| Lead `sicarii` (1000), outside | read a frame record through the ACL; read the target's output through the inherited default ACL | create in frame records, write the source, create in the partition, rename the generation, partition or `runs`, unlink a record, symlink into the frame directory, open the lease → EACCES. chmod a record, hard-link the source out → EPERM |
| Writer (100000) | read the target-owned output through the default ACL; release the lease | — |

**Demonstrated limitation.** Renaming the writer home inside its `sicarii`-owned parent **succeeded**, and it was
renamed back. In this environment the ancestor is owned by `sicarii`. W-1 v2 places the home under root-owned
`/var/lib`, and that is exactly the property this probe cannot model.

**What this supports.** W-1 v2 argues (§4.3–§4.4) that, with separate UIDs, neither `sicarii` processes nor the target
can mutate writer-owned frame locations, records or the admitted source. This probe exercises that argument with real
kernel checks.

**Critical caveat: subordinate UIDs give no protection against `sicarii`.** The 100000–165535 range is delegated to
`sicarii` by `/etc/subuid` and `/etc/subgid`.
- Any `sicarii` process can create its own user namespace mapping that range through `newuidmap`, and so act as those
  UIDs.
- As the namespace owner, it can also join an existing namespace and use its capabilities over files owned by mapped
  UIDs.

The outside probes therefore show only what the kernel enforces between distinct UIDs when neither side can become the
other. **Consequences:**
1. **Not an unprivileged route.** A rootless-namespace variant of W-1, with writer and target as `sicarii`'s
   subordinate UIDs, is not a route for V5-B01/V5-B02. Concurrent `sicarii` processes could defeat it. This is a
   negative finding for the frame plan.
2. **What the probe is still good for.** It is evidence for the DAC, ACL and hard-link semantics W-1 needs only once
   those semantics hold between `sicarii` and accounts that `sicarii` cannot map.
3. **New W-1 setup check, for v3.** Verify that the UIDs and GIDs of `wlscratch` and `wlscratch-run` are outside every
   range delegated in `/etc/subuid` and `/etc/subgid`, to `sicarii` or anyone. Verify too that `newuidmap`/`newgidmap`
   cannot map them for `sicarii`. Nothing allocated by `useradd --system` is expected in 100000–165535, but this must be
   verified, not assumed. The frozen W-1 v2 is not edited; this is carried as an author addendum.

**What it does not show:**
- the real accounts, the sudo rules or their `env_reset`;
- the systemd user manager and its scope limits;
- the installed frame's closure;
- root-owned ancestors;
- writer-to-launcher handoff or launch custody;
- lead authentication, or same-user interference with the lead's own processes;
- storage admission;
- any WORLDLINE code. No prover or compiler was run.
