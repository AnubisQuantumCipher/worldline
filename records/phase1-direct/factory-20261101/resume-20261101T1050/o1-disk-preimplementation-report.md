Use a source derivative of `chunk_capacity_guard_v5.py` plus a small fixed-command worker. No writes or compiler/generator execution occurred.

The exact reusable sources are:

```text
guard v5  f5850499903a25985f477ba3b593b452bae8223bae5c970da2a515f9d6bfda18
heavy     c3c7fcc84bb509668d0136606449486d1179d67d7c89bf68f6f5db79a4ece61a
preflight 47714e59f0f6f5407e7ba6bf0c09d8897978b717ff5cf267986b979205fa5e01
```

Keep the guard’s bounded receipt writer, safe control-file reads, launcher cancellation **before** scope-receipt reading, exact owned-scope checks and finite20s scope cleanup. Change task paths, launch arguments, inventory and monitoring only. Move its two8KiB `systemctl` scratch files from `/dev/shm` to registered disk control storage if all task writes must remain under owned disk paths. Do not reuse the blocked IPC consumer.

Use a60s admission/lock-wait bound, first-refusal cancellation,1s sampling, and a1590s outer monitor bound:60s admission +1500s inner deadline + inherited30s timeout grace. Cleanup then has the inherited5s launcher wait and20s scope limit. Missing receipts or unconfirmed cleanup remain UNVERIFIED; they cannot authorize succession.

The worker should have straightforward helpers, each≤60lines: pin validation, exclusive byte-identical staging, sanitized environment, child limits, bounded stage execution, template-roster validation and output comparison. Preserve original GPRs and the previously recorded minimal→core→helpers command graph. All writable source copies, GPR configuration, objects/libraries, executable, tmp/cache and full logs belong under the registered work root.

Set compiler/build child `RLIMIT_FSIZE=64MiB` and `RLIMIT_CORE=0`. **Do not lower the recovery parent’s hard file limit**: an archive child needs its own separately registered larger limit. Full captures exceeding their limit are FAILED/evidence loss. Preserve failed artifacts.

The4GiB live aggregate,8192entries and1GiB shutdown/growth allowance remain **unmeasured admission/stop ceilings**, monitored rather than a hard aggregate quota. Archive and restoration need separately reserved4GiB payload budgets plus explicit framing. A strict uncompressed USTAR framing allowance is at most:

```text
8192 × (512-byte header +511-byte payload padding) +10240
= 8,390,656 bytes
```

That allowance requires representable USTAR paths and rejected extensions; compression requires an additional registered allowance. Native recovery tooling and bounded archive/restore deadlines still need explicit selection. No reserve against unrelated writers is established.

The read-only inventory is concrete. For each group, the digest is SHA256 of canonical JSON mapping filenames to `{bytes,sha256}` using sorted keys and compact separators:

| Group | Files / bytes | SHA256 |
|---|---:|---|
| GPR configuration KB |71 /258537|`88fd3b13da49e3ec7ffa420022f63e3207eb17d648aad479a6768a15353087b8`|
| GNAT `adalib` |887 /95982422|`a440dcb02e1a22357c5c1f09c74e76e898e2c0ebd99447b333b1576833c23aec`|
| GCC internal headers |39 /1114632|`b89110b19cebffceb166a058a0ebeb31ecc4146a897a3e67e0d8e685e635ced9`|
| Generator tools |20 /268066232|`ccfbcbc54b7d6e9e449540a253bdbaddc33162e44db6b49178ebfda4078297a7`|
| GCC link inputs |9 /8250763|`585d5c59be9060457551319c37658cf8a8390b04d2459219d21bd3745af36523`|
| OS candidate inputs |13 /4365743|`2accd03890a199902c1297cfc52f1d86538370720faf5a65ae039958e7e3259e`|

First three groups use paths relative to their group root; last three use absolute paths. Materialize individual mappings during preparation; record symlink text/resolution separately.

The20tool membership is:

- GPR installation: `bin/gprbuild`, `bin/gprconfig`, `libexec/gprbuild/{gprlib,gprbind,gprdriver,processes_wrapper}`.
- GNAT installation: `bin/{gcc,gnatbind,gnatlink,as,ar,ranlib,ld}`, `libexec/gcc/aarch64-linux-gnu/16.1.0/{gnat1,cc1,collect2}`, and `aarch64-linux-gnu/bin/{as,ar,ranlib,ld}`.

The9GCC inputs are `ada_target_properties`, `crtbegin{,S,T}.o`, `crtend{,S}.o`, `crtfastmath.o`, `libgcc.a`, `libgcc_eh.a`. All1573runtime-source hashes in the existing preflight still match.

Static ELF inspection found dependencies on loader/libc/libm/libgmp/libzstd. OS candidate membership is `/usr/lib/{libc.so.6,ld-linux-aarch64.so.1,libgmp.so.10,libm.so.6,libzstd.so.1,libgcc_s.so.1,crt1.o,Scrt1.o,crti.o,crtn.o,libc.so,libdl.a,libpthread.a}`. Actual loader resolution, system-header closure, Python runtime and shared-library closure remain explicit trusted dependencies—not whole-OS proof. No loader tracing or compiler execution occurred.

The verifier can establish source consistency without xtree:

-21unique `Process` outputs and21templates,63495template bytes.
-35placeholder occurrences,35unique placeholder names and35unique registered `Add` names; the sets match exactly.
- Syntax is `([ ]*)_@([A-Za-z_]+)@_`.
- Ordered output-roster digest: `e359af3a27b74100b22f1d7455fce94cb0792a5823f759f3407c612431a26290`.

Require that static join, reject substitution-warning stdout, reject remaining marker delimiters, validate the exact21regular outputs and compare all bytes from two fresh generations using the same pinned executable. Unknown placeholders are deleted with warnings, so marker absence alone proves insufficient.

The smallest next step is the registered source-only preparation lease, followed by synthetic guard/worker/verifier tests and independent review. Actual target/configuration receipts, budget fit, generator execution, semantic adequacy and all downstream acceptance remain UNPROVEN.
