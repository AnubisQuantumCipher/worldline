**No additional immutable source input was identified.** The frozen 771-file candidate, sealed GNATcoll sources, and planned generated files form an adequate **static candidate for the next baseline build attempt**. Executable closure remains UNPROVEN.

| Dependency | Source-observed resolution |
|---|---|
| GCC glue | `gnat2why/smissing.c` includes no headers. It defines `gnat_encodings`, `optimize`, `optimize_size`, `callgraph_info_file`, `save_argc`, `save_argv`, and `gnat_version_string`. No GCC `toplev`/`misc` source acquisition is indicated. |
| CPU timing | Linux `src/utils/process_cpu_time.c` includes only `<time.h>` and calls `clock_gettime(CLOCK_PROCESS_CPUTIME_ID, …)`. `<windows.h>` belongs to the inactive Windows branch. |
| Target queries | GNAT project Naming selects sealed `ada_get_targ.adb`. Imports such as `get_target_bits_per_unit`, `enumerate_modes`, and `flag_short_enums` occur in the alternative `get_targ.adb`; they do not establish missing GCC backend inputs for this selection. |
| GNAT OS support | Read-only `nm` inspection found `get_gcc_version` and sampled `__gnat_*` OS symbols in selected installed `libgnat.a`’s `adaint.o`; `gnat_argc`, `gnat_argv`, and `gnat_envp` occur in `argv.o`. |
| GNATcoll compatibility glue | Already sealed `core/src/set_std_prefix.c` and `update_path.c` provide the two corresponding imports from `osint.adb`. Other included compatibility stubs provide linker-option variables used by auxiliary GNAT tools. |
| Ada runtime compatibility name | `Unchecked_Deallocation` resolves to installed `adainclude/unchdeal.ads`. |

The inspected runtime archive is:

```text
/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adalib/libgnat.a
bytes: 26140732
sha256: e04cc0c2cfccafda7790e45e101f27751c6371252c164d84f071cd9024536b27
```

This proves symbol presence in that archive, **not** that a future linker selects it or that it corresponds to the pinned frontend source.

For GNATcoll’s Linux/aarch64 source directories, I inspected 18 C units and three project headers. Every active quoted project include is retained:

```text
blake3.h
blake3_impl.h
xxhash.h
```

The apparent missing `"vxWorks.h"` occurs under the inactive VxWorks branch. Windows, Mach, x86 intrinsic, and other architecture headers likewise require configuration-specific branch selection; they are not evidence for broad acquisition. Native `arm_neon.h`, `stdint.h`, `stddef.h`, `stdbool.h`, and `stdatomic.h` are present in the selected compiler’s include directory.

Remaining external headers are ordinary compiler/libc/POSIX inputs: standard C headers, `<time.h>`, and Linux filesystem/process/mapping/resource headers. The checked native header paths exist. Effective include paths, feature-test macros, ABI compatibility, library ordering, and any additional linker options remain unresolved until retained compiler/link commands establish them. In particular, final linking must resolve `clock_gettime`, libc/POSIX services, GNAT runtime imports, compiler atomic support, and GNATcoll’s Unix `-ldl` option.

A bounded lexical context-clause scan covered **955 retained Ada files** across the compiler candidate and GNATcoll cut. After distinguishing generic formal syntax and the runtime compatibility unit, unresolved nonruntime names were the expected generated GNAT units—`Einfo.Entities`, `Nmake`, `Seinfo`, `Sinfo.Nodes`, `Snames`—and generated Why-tree units. No additional source package acquisition was identified. This scan is supporting static evidence, not an Ada parser or compiler-resolution proof.

One inherited error boundary must remain recorded: Linux `process_cpu_time` ignores `clock_gettime`’s return value and then reads `ts`. That is **SOURCE-OBSERVED unchecked error handling**, not a demonstrated runtime failure. Preserve the unmodified baseline; it limits any whole-toolchain assurance claim.

The smallest sound next step is the admitted generator/build attempt using the sealed inputs. Required acceptance evidence is complete generated-output receipts, actual compiler unit/include resolution, successful link with selected libraries identified, candidate-translator execution provenance, and reproduction of unchanged D47 static leak failures. No source amendment is currently justified; no compiler, generator, or proof was executed here.
