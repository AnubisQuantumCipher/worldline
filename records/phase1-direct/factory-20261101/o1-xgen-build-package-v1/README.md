# Source preparation only: fixed disk xtree candidate

**UNRUN / UNADMITTED.** This packet does not authorize a launch, establish a
mechanism qualification, close O1/D47/translator correspondence, or perform F7.
Fresh paired review, separate judge, current storage-owner handoff and explicit
admission are required. The compiler acquisition packets remain immutable.

The entry point, if later admitted, is `xgen_guard.py`. Root must check the frozen
packet manifest hash and all payload hashes before and after launch. Importing
Python precedes its in-process checks; the external root source-pin check is a
mandatory bootstrap dependency. `manifest.json` intentionally cannot hash itself.
Start with a clean environment, the pinned `/usr/bin/python3`, `-B -W error`,
`PYTHONOPTIMIZE=0` and `PYTHONDONTWRITEBYTECODE=1`. No other dispatcher or mode is
authorized by this packet. There has been no operational-main execution.

## Requirements, threat and contracts

This is a small Python integration boundary around external GNAT/GPR/native
tools. It grants no WORLDLINE authority. Treat tool failure, malformed control
receipts, source drift, missing evidence, unexpected files and capture overflow
as failure. Source/tool fingerprints are identity observations, not correctness
proofs. The OS, cgroup implementation, filesystem, loader, Python interpreter and
stdlib, native tools and kernel syscall responsiveness remain trusted.

The compiled subprocess sees the host filesystem read-only and only `W/live`
as an ordinary writable filesystem. Bubblewrap also supplies virtual `/proc`
and minimal `/dev` interfaces; this is not a claim of zero device/syscall effects.
PID/network namespaces and dropped capabilities follow the existing disk pattern;
no private IPC namespace is requested. Toolchain/product/acquisition inputs and
control receipts are outside its writable bind. The environment is constructed
from an allowlist; inherited flags, loader injection and project/include paths
do not reach compilation. Python/subprocess/native sandbox behavior is assumed,
not formally verified. The absence of live sandbox tests remains an admission gap.

All future paths are fixed:

- `W=records/phase1-direct/completion-20261026/o1-xgen-build-v1`.
- `W/live`: staging, objects/libraries, executable, tmp/cache/home, generation
  directories and complete build/generator stdout/stderr.
- `W/archive`: only the native `live.tar`, with an independent larger child limit.
- `W/restore`: fresh restoration, writable only in the native restore child.
- `W/control` plus `factory-20261101/o1-xgen-build-job-v1`: guard/heavy/worker
  receipts, recovery inventory and recovery logs. Compiled children cannot mutate
  either control location.

The guard requires fresh exact W/JOB, validates packet/source/tool pins, checks
full overlap capacity, then creates W/control. It retains the original heavy
helper byte-for-byte: memory8GiB, swap0, shared lock and post-lock MemAvailable14GiB.
The derivative cancels on first memory refusal rather than allowing the helper's
five-minute retry loop to continue. No inherited failed-job deadline is increased:
this is a distinct initial proposed generator profile.

## Bounded proposed profile

`profile.json` carries the registration and an append-only framing correction.
Fit has not been measured. Reserve10,000,000,000B plus14,050,918,400B covers the
proposed simultaneous classes: live4GiB, archive4GiB+16MiB, restored payload4GiB
+64MiB filesystem allowance, shutdown/growth1GiB and outer metadata8MiB.

Live/restore scans reject more than8192entries, links/hardlinks/special objects,
setuid/setgid modes, unsupported names or individual files over64MiB. Ordinary
compiler children receive hard `RLIMIT_FSIZE=64MiB` and core0; each full build
stdout/stderr stream shares that cap. Reaching a capture cap is conservatively
FAILED/evidence loss, even if a tool reported exit0. No truncation qualifies.

The archive child independently receives hard file limit4GiB+16MiB; its parent
never inherits the compiler child's64MiB hard limit. Four recovery streams each
have a strict256KiB pipe-capture ceiling, stored under W/control (under1MiB in
total). Guard JSONL is capped512KiB; combined control+JOB logical bytes are
checked against8MiB. Receipt failure cannot bypass owned cleanup. The recovery
inventory receipt is independently capped2MiB; final worker receipt1MiB.

The original8390656B framing estimate omitted explicit root/end-record accounting.
The corrected conservative expression is `512 + 8192*(512+511) + 1024 + 10239
=8392191B`, including root header, per-entry header/padding, end blocks and record
padding. It fits the unchanged16MiB allowance. This uses a conservative USTAR
subset: printable relative names no longer than99bytes, no extensions, only
directories and unique regular files. The registration itself is unchanged.

Capacity classes are scanned separately every nominal1s. Live/archive overlap is
not charged against a single4GiB threshold. Stop if available space falls below
reserve+1GiB or a class/inventory bound is violated. **Sampling and per-file limits
are not an aggregate quota, do not reserve capacity against unrelated writers,
and do not prove filesystem overhead fits64MiB.** These allowances remain
unmeasured; overflow/failure preserves artifacts and requires a new decision.

Admission/lock wait is60s; heavy timeout1500s has its inherited30s kill grace.
Outer monitor is bounded1590s/samples, launcher cancellation wait5s and scope
cleanup20s. Each systemctl child is limited to2s/8KiB streams. The worker uses
the same remaining1500s deadline throughout: target5s/version5s, minimal300s,
core600s, helpers300s, each generation30s, and archive/restore each at most300s
**and no more than the global time remaining**. Setup, hashes and verification
consume that same budget. Outer containment remains necessary for blocking
external behavior; no hard realtime claim under unresponsive kernel/I/O exists.

## Original source and command graph

`input-pins.json` records342 exact copies:278GNATcoll and64xgen/Why inputs.
Original relative source layout/GPR bytes are preserved. GNATcoll's existing
absolute `GNATCOLL_OBJECT_ROOT=W/live/gnatcoll/` redirects its objects/libraries;
helpers.gpr's own obj/executable paths land in the owned copied source tree.
No Makefile, Python build wrapper, installation or shared-library lane is run.

The first bounded future actual stages require `gcc -dumpmachine` exactly
`aarch64-linux-gnu` and `gcc -dumpfullversion` exactly`16.1.0`. Binary identity
is pinned separately. Then gprbuild26 uses `-p -j2`, original minimal/core GPRs,
and these explicit scenarios consistently:

```
GNATCOLL_BUILD_MODE=DEBUG LIBRARY_TYPE=static GNATCOLL_VERSION=25.0
GNATCOLL_OS=unix GNATCOLL_MMAP=yes GNATCOLL_MADVISE=yes
GNATCOLL_XXHASH_ARCH=generic GNATCOLL_BLAKE3_ARCH=aarch64-linux
GNATCOLL_OBJECT_ROOT=<absolute W/live/gnatcoll/>
```

Minimal/core use EXTERNALLY_BUILT=false, `-cargs:Ada -gnatwa -gnatwe -gnatVa`
and `-cargs:C -Wall -Wextra -Werror`. Helpers uses EXTERNALLY_BUILT=true and
`-cargs:Ada -gnata -gnatVa -gnatwa -gnatwe`. Existing DEBUG checks/O0,
Initialize_Scalars/stack checks/binder-E and helpers'gnatg remain in the GPRs.
An upstream warning is a retained failure, never grounds to suppress a gate.

`tool-runtime-pins.json` records2623file identities/402438744bytes, including
GPR tools and71configuration KB files, GNU compiler frontends/link tools and
target binutils aliases,1573runtime sources,887adalib inputs,39GCC headers,
GCC startup/libgcc inputs, orchestration tools and candidate OS link/loader inputs.
Symlink text is recorded separately. These are not the whole loaded closure:
system `/usr/include`, actual transitive C includes, loader resolution/shared
libraries, Python runtime modules and carrier Git configuration remain trusted
dependencies. Generated CGPR files are retained/hashed in local recovery; they
do not yet exist, and their semantic adequacy is UNPROVEN.

## Template and recovery evidence

`template-roster.json` fixes21outputs. Source-specific regex checks join all35
unique `Add` callback names with all35placeholder occurrences. The producer
syntax is `([ ]*)_@([A-Za-z_]+)@_`; unknown names warn on stdout and delete the
line, so marker absence alone is insufficient. Both generations must emit no
stdout/stderr, contain exactly21templates+21nonempty regular outputs with no
remaining delimiter and produce identical output bytes/hashes from the same
hashed executable. This is a source-specific check, not a universal Ada parser
or semantic adequacy proof.

After all compiled children return, native tar runs with `--create --format=ustar
--sort=name --numeric-owner --owner=0 --group=0 --directory W/live .`; only
W/archive is writable. Restoration uses a fresh W/restore with
`--no-same-owner --same-permissions --delay-directory-restore --keep-old-files`;
only W/restore is writable. Native tar is pinned/trusted, not a new archive
parser. Input object/name validation precedes tar. Verify the live inventory
before/after creation, the full archive hash before/after restoration, and all
restored names/types/modes/bytes/SHA256 plus root mode. Archive and logs persist
on failure. This local recovery **does not preserve/prove UID/GID, nanosecond
timestamps, ACLs/xattrs or whole filesystem metadata**. It grants no DUAT
retirement authority. Original pins and the later DUAT full restore gate remain.

Worker state separately reports source validation/build/generation/determinism/
recovery/terminal. Missing work is UNRUN/UNKNOWN; a running failed stage becomes
FAILED. Exit0 still says terminal pending, qualification UNPROVEN and no acceptance
credit. No receipt can override a nonzero process termination.

Fresh terminal evidence requires exact unit Id and either actual populated0 for
the claimed nonempty cgroup, or the exact collected native tuple (exit0,
LoadState=not-found, ActiveState=inactive, empty ControlGroup). Collected state
is accepted for normal wrapper completion only alongside a type-checked reaped
launcher exit and the complete inherited terminal receipt with populated exactly
false/inactive. All are retained together. Missing/malformed populated data for
a nonempty cgroup is UNKNOWN, never unpopulated. Failure cleanup remains
conservative: a collected scope alone does not become its populated0 proof.

## Tests and remaining acceptance

`source_tests.py` is the author's synthetic/mock suite, not independent review.
No operational main, compiler, generator, tar, service, mount or lock is run.
All attempts and initial failed fixture evidence are retained. Attempt01 failed
because a mock PID was not JSON serializable; the guard correctly failed closed.
Attempt02 corrected the fixture; later tests add recovery and terminal controls.
`attempt01-*.txt` preserve the exact first-run sources.

The full author suite uses small temporary fixtures only inside this packet.
Reviewers can run its explicit read-only subset without creating fixtures:

```
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 XGEN_READ_ONLY_TESTS=1 \
  /usr/bin/python3 -B -W error source_tests.py
```

The read-only subset is deliberately identified separately from the full suite.
See `test-results.json` for exact commands, exits, elapsed evidence and source/
output hashes. Tests do not establish native compiler/sandbox/tar/cgroup fit.
Next: immutable same-packet paired review and judge, then fresh storage/admission
review. Successful future generator/recovery observations alone cannot establish
translator closure, installed correspondence, formal proof or Phase One acceptance.
