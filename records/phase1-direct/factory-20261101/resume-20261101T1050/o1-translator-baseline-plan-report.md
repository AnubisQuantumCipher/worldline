**Prospective plan only: UNRUN, no launch authorization.** I wrote nothing and inspected neither v2 WIP nor peer reviews.

Fresh installed-asset readback:

```text
/home/sicarii/opt/gnat/gnatprove-aarch64-linux-16.1.0-1/libexec/spark/bin/gnat2why
106,334,584 bytes; device 64768; inode 4375042
SHA256 375d0100954a66c78bace00d2229c9b96a30b6cf28845e00c4db220ba1efddb5
```

Its 101.41 MiB size already exceeds xtree’s 64 MiB file ceiling. Reusing that ceiling for translator linking would reject an installed-sized binary. This measurement does **not** predict candidate Debug size.

The sealed source readback contains 771 files / 37,730,838 bytes: SPARK 292 / 10,178,446; GCC 479 / 27,552,392. Largest source is `gcc/gcc/ada/sem_prag.adb`, 1,304,902 bytes. Manifest SHA256 is `7e59cd169373e045b82896d579dc9256735661e453f29c43c28aa7bf8387d4aa`.

Let a future exclusively registered work root be `W`; these are proposed names, not created paths:

| Stage | Exact layout and provenance obligation |
|---|---|
| Admission | Future qualified xtree receipt must identify all 21 outputs, both-generation equality, executable hash, GNATcoll DEBUG/static configuration, and complete recovery. No v1 result can substitute. |
| Materialize | `S=W/source/spark2014`, `G=W/source/gcc`, `B=S/gnat2why`. Copy sealed compiler inputs preserving relative paths. Copy the qualified 21 outputs into `S/src/why` using their exact roster. `B/gnat_src` must resolve exclusively to `G/gcc/ada`; receipt symlink text and canonical target. |
| Prepare GNAT sources | Fresh `B/{obj,obj-gnat,obj-gnat2why,obj-tools}`. Generate `obj/sdefault.adb`; copy `gnat1drv.adb` to `obj-gnat2why` and `libgnat/s-rident.ads` to `obj-gnat`. Stage exactly the recorded 17 generator inputs into `obj-tools`. |
| Generate | Build/run `xsnamest`, then `gen_il-main`, using the retained explicit recipe with absolute GPRbuild/configuration and `-j2`. Receipt executables, incidental outputs, and all ten required generated files below. |
| Link | Retained `gnat2why.gpr`, `Build=Debug`, empty Coverage/GPR_TOOL, matching GNATcoll DEBUG/static configuration, bounded concurrency. GPR explicitly names output **`S/install/bin/gnat2why`**. Retain actual compiler, binder, C include, library and link resolution. Do not invoke upstream Makefile: setup reruns xgen and defaults to unbounded `-j0`. |
| Runtime candidate | Proposed `R=W/runtime-candidate`, with `R/bin/gnat2why` an exact checked copy of the linked output. Installed driver, configuration, theories, Why3/provers and their actual selected paths remain separately identified trusted inputs. `GNSA_ROOT=R` is a source-supported selection hypothesis requiring execution evidence. |
| D47 | Fresh `W/d47`, byte-identical four source/project files; retain build, runtime, proof, `.spark`, Why3 sessions, and executable provenance. |
| Recovery | Archive the complete owned evidence/output closure, including generated sources, objects/libraries, candidate executable, D47 artifacts, full logs and inventories. Restore into a fresh owned root and compare roster, types, modes, symlink targets, sizes and hashes. Native archive/restore tool identities and behavior require qualification. |

Required ten generated files:

```text
obj/sdefault.adb
obj/snames.ads
obj/snames.adb
obj/nmake.adb
obj/nmake.ads
obj/seinfo.ads
obj/sinfo-nodes.ads
obj/sinfo-nodes.adb
obj/einfo-entities.ads
obj/einfo-entities.adb
```

For `sdefault.adb`, resolve `@ADAINCLUDE@`, `@ADALIB@`, and `@GNAT1DIR@` from the selected compiler configuration/readback; retain upstream nonautomated `@NOPREFIX@` behavior. GCC source location is not `GNAT1DIR`.

**Proposed initial disk/output ceilings—all UNMEASURED admission limits, requiring explicit registration and review:**

| Item | Proposed ceiling |
|---|---:|
| Live owned build/replay payload, including copied inputs, dependencies, objects, executable, temporary data and logs | 8 GiB |
| Additional stop/shutdown growth allowance | 2 GiB |
| Entries across owned payload | 32,768 |
| Ordinary build/link child regular file | 1 GiB |
| Generated-source regular file | 64 MiB |
| Individual full log | 64 MiB; exceeding it fails evidence retention |
| Native archive payload | 10 GiB plus format framing |
| Full restore payload | 10 GiB plus framing/metadata allowance |

For strict representable USTAR paths, 32,768 entries require at most **33,531,904 bytes** of header/padding allowance:

```text
32768 × (512 + 511) + 10240
```

Thus simultaneous local allowance is at least **30 GiB plus twice that framing allowance**, separate control/receipt overhead, and the protected **10,000,000,000-byte reserve**. Reject unsupported archive paths/extensions; compression needs its own additional bound. Archive children require separately registered file limits; never inherit the 1 GiB build limit into recovery. These ceilings are proposals, not evidence that the build fits. Monitoring is not a hard aggregate filesystem quota or a reservation against unrelated writers.

Retain **8 GiB memory, swap 0, post-lock MemAvailable ≥14 GiB, one heavy lock**, bounded cleanup and complete failed artifacts. New stage/archive/restore deadlines require explicit finite registration; this plan grants **no extension of any prior failed-job deadline**.

Pinned main now closes the earlier report’s startup-source gap: `Set_Environment` constructs:

```text
GNSA_ROOT/bin → installed prefix/libexec/spark/bin → incoming PATH
```

Both Global_Gen and Analysis use bare `Set_Driver ("gnat2why")`. Nevertheless, installed/source correspondence remains **UNKNOWN**, and GPR2 resolution remains **UNPROVEN**. Require successful child-execution evidence for **both phases**, linking phase/action, argv, ancestry, executable device/inode/hash and candidate output hash. PATH, `which`, scheduler JSON or action creation alone do not establish execution. Any namespace/bind selection additionally needs mount identity and host-installation readback.

Unchanged D47 command:

```sh
gnatprove -P probe.gpr -U --mode=all --level=3 --report=all \
  --checks-as-errors=on --proof-warnings=on \
  --memlimit=1024 --timeout=60 -j1
```

Expected retained baseline: build/runtime exit 0; proof exit 1; 23 checks and six unproved—one Adjust, three allocating `Capture(Text)'Old`, two Main-owner checks. Specifically retain the three static leak failures at `lifetime.ads:11–13`; inspect full `.spark` output, not sessions alone. Changed counts/signatures require explicit classification.

Remaining TCB gaps are actual compiler/configuration/project selection, effective system-header and ABI closure, linker/runtime/library selection, generator compatibility, actual driver/GPR2 execution behavior, runtime auxiliary closure, enforcement/cleanup behavior, and native archive/restore qualification. Existing C analysis found no additional immutable source requirement; `process_cpu_time.c` nevertheless retains unchecked `clock_gettime` failure handling, limiting whole-toolchain assurance.

**Smallest remaining executable blocker:** obtain qualified xtree outputs and complete recovery from the sole v2 owner, then review the exact finite translator package and runtime-selection evidence mechanism before admission. No new orchestrator, source expansion or semantic change is justified here. O1 remains FAILED-OPEN; F7 independent acceptance remains NOT PERFORMED.

<oai-mem-citation>
<citation_entries>
MEMORY.md:918-922|note=[retained resource and original Old claim boundaries checked against current task]
</citation_entries>
<rollout_ids>
01a13631-cd95-7cd2-870d-21561e26c8f2
</rollout_ids>
</oai-mem-citation>