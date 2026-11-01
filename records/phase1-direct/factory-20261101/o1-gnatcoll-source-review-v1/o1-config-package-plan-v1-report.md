Use a **small fixed configuration package**, derived from existing containment/capture mechanisms, with one command and no build continuation. Its output becomes a separately reviewed prerequisite; D158/D159 entries and decisions remain immutable.

Proposed fresh paths:

```text
records/phase1-direct/factory-20261101/o1-config-package-v1/
records/phase1-direct/factory-20261101/o1-config-job-v1/
records/phase1-direct/completion-20261026/o1-config-v1/
```

The package needs these bounded files:

| File | Fixed responsibility |
|---|---|
| `config_guard.py` | Verify package/tool/input identities, fresh paths and capacity; invoke unchanged heavy helper; enforce finite admission/monitor/owned-cleanup bounds; retain terminal evidence. Derive from the qualified D158 guard rather than create a general runner. |
| `config_worker.py` | Establish child limits/environment/sandbox, execute **one fixed GPRconfig argv**, capture complete streams, inventory outputs and record result. No compiler-build, fixture, validator or successor branch. |
| `profile.json` | Exact paths, command, time/resource/output bounds and retained-root reservation. |
| `input-pins.json` | GPRconfig, complete selected KB/entity inventory, discovery tools/runtime and inherited orchestration dependencies. |
| `manifest.json` | Exact package identities. |
| `README.md` | Caller prerequisites, state distinctions, semantic-review checklist and reversal. |
| Focused tests | Fresh-path rejection, drift, timeout/capture ceiling, extra output, failed/missing terminal evidence and prohibition of subsequent compilation. |

The initial caller supplies an allowlisted environment and descriptors 0/1/2 **before any interpreter startup**. No new shell entry is necessary if the existing caller can provide that concrete custody evidence. Otherwise an entry must be separately reviewed; the old entry supplies no authority.

Use the candidate argv already documented in:

`o1-compatibility-review-metadata-v1/o1-config-only-prerequisite-plan-v1-report.md`

with exact substitutions:

```text
P=/home/sicarii/opt/gnat/gprbuild-aarch64-linux-26.0.0-1
G=/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1
F=/home/sicarii/Work/worldline-phase1-direct-20261019/records/phase1-direct/completion-20261026/o1-config-v1
```

```text
P/bin/gprconfig --batch --db- --db=P/share/gprconfig
--target=aarch64-linux-gnu
--config=Ada,16.1,default,G/bin,gnatls
--config=C,16.1.0,,G/bin,gcc
-o F/live/native.cgpr
```

**Choose unprefixed C `gcc` explicitly.** Installed `compilers.xml:20–33` describes GCC discovery through the matched executable; `c.xml:17` emits `${PATH(c)}${EXEC(c)}`. Selecting basename `gcc` therefore requests the unprefixed driver and avoids relying on selection among target-prefixed aliases. This choice is justified by discovery/driver rules, not equal executable hashes. Later semantic review must require `G/bin/gcc` as the selected C driver. No automatic fallback to `aarch64-linux-gnu-gcc`, `GCC`, or another tuple after rejection.

For Ada, `compilers.xml:190–214` identifies `gnatls`, major/minor version and the default runtime. `gnat.xml:12–33` supplies the resulting Ada compiler/binder/runtime bindings. Exact basename/path/version matching and duplicate resolution remain **UNRUN parser behavior**.

Embedded-help evidence:

`resume-20261101T1050/o1-selected-configuration-embedded-help-readback-v1.json`

binds binary SHA256 `58e81e9c21d18f20b80f7c2594a3f473621b64dff2498f191e4fbe2da9d0ce46`; offsets `15170078–15170395` establish tuple grammar, while `15169768–15169881` describe explicit KB loading. No native-help stage is needed merely to recover that grammar.

The child environment should be exactly:

```text
PATH=G/bin:P/bin:/usr/bin
HOME=F/live/home
TMPDIR=F/live/tmp
XDG_CACHE_HOME=F/live/cache
LC_ALL=C
TZ=UTC
```

Use the existing bubblewrap shape from D158 `xgen_common.py:193–197`: readonly host root, private PID/network namespaces, dropped capabilities, proc/dev, and **only `F/live` writable**. Keep helper receipts outside that writable child root. No ambient GPR variables, startup hooks, compiler flags or loader overrides.

Proposed finite envelope:

- **One attempt; configuration timeout 30 seconds.**
- Unchanged heavy-helper **8 GiB / swap 0**, and **14 GiB post-lock MemAvailable** requirement.
- Admission/lock wait **60 seconds**; inherited timeout kill grace **30 seconds**.
- Outer monitor **180 seconds/samples**, 1-second nominal polling; owned cleanup **20 seconds**, launcher reap **5 seconds**, using existing qualified behavior.
- CORE=0; configuration and child stdout/stderr each **64 KiB**, reject ceiling contact.
- `F/live`: **1 MiB / 128 entries**; helper/outer metadata combined **8 MiB**.
- Existing reserve and shutdown margin remain unchanged.

The unchanged helper has unbounded retry/cleanup loops (`scripts/phase1_heavy.py:60–72,123–134`), so **it cannot be the sole finite supervisor**. The derived outer guard must retain first-refusal rejection, finite admission and owned cleanup rather than trusting those loops.

Register an additional retained-root reservation of **9,437,184 bytes** (1 MiB payload plus 8 MiB metadata) before preparation. Conservatively retaining the previous `24,178,844,672`-byte floor gives a proposed floor of **24,188,281,856 bytes**, subject to the current reservation ledger. Existing failed `W` remains retained and its actual occupancy remains reflected in fresh capacity measurements. The 1 MiB aggregate limit is sampled detection, not a hard filesystem quota; preserve that limitation and the existing shutdown-growth margin explicitly.

Why old entries cannot run this unchanged:

- D158 guard fixes old `WORK/JOB` and invokes its worker (`xgen_guard.py:253–270`); worker proceeds into dependency builds and generation.
- D159 `entry.sh:3–8` fixes old HOME/launcher; `launch.sh:7,79–84` fixes old capture root/guard.
- D158 diagnostic dispatch rejects unregistered stages; D159 requires its public captures to remain empty.
- Rebinding any of these requires a distinct reviewed package, not reuse of their old approval.

After termination, seal CGPR, captures, exact argv/environment, side-effect inventory, tool/KB identities and terminal chain. Review selected target normalization, both drivers, runtime, binder/library/link/archive tools and diagnostics **before any compilation**. Review waiting occurs with no running configuration job and consumes none of the original generator’s 1500/1590-second budgets.

Unresolved design choices are limited to concrete outer-entry custody, verified aggregate-growth enforcement versus documented sampling, and actual GPRconfig selector/KB behavior. None is resolved by this plan.

Relevant reusable immutable hashes:

```text
scripts/phase1_heavy.py   c3c7fcc84bb509668d0136606449486d1179d67d7c89bf68f6f5db79a4ece61a
D158 xgen_guard.py        55ea7858c376211ad8898f7c7058cc33f16d6cf9bad6b1b3f1111a8b5ff6fb53
D158 xgen_common.py       59ded210655b149eac6846683552605663509a25b5f7fb6441496dd1f818decf
D159 entry.sh            3b9953b0cde34d1b570a13107c575bae060305e615c1056a97e8255aafe05afd
D159 launch.sh           6b6d79cf6c268ee944c6b4e6a0748a2560ee9ffe5d11ca29ea511a2b11a62a55
```

No writes or native execution occurred. D160/D158/D159 remain at zero revisions; D161 remains separate. **No launch authority granted. F7 NOT PERFORMED.**