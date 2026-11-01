The smallest credible chain is **exact-source compilation evidence plus a bounded debugger observation of the existing lifecycle fixture**. Public `Free` completion and repeated `Free` alone cannot establish either allocation’s release.

Let:

```text
C=records/phase1-direct/completion-20261026/old-retirement-compiler-source-cut-v1/gcc/gcc/ada
R=/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude
X=records/phase1-direct/completion-20261026/old-retirement-xgen-source-cut-v1/minimal/src
```

**Existing source chain**

| Obligation | Exact source anchors | What this establishes |
|---|---|---|
| Two concrete access types | `X/gnatcoll-boyer_moore.ads:63–71` | `Offset_Array_Access` and `String_Access`; two distinct stored fields. |
| Both allocations | `X/gnatcoll-boyer_moore.adb:149,199` | String and suffix-array allocations. |
| Both deallocation instances/calls | Original body `:247–254`; approved derivative must retain matching mapping | Offset-array instance/call first, string instance/call second. |
| Canonical generic | `R/a-uncdea.ads:19–31` | Matching generic formals, `Post => X = null`, `Import(Intrinsic)`. |
| Intrinsic instance propagation | `C/sem_ch12.adb:7071–7100` | Intrinsic generic marks its instance intrinsic; no ordinary body is instantiated. |
| Intrinsic call lowering | `C/exp_ch6.adb:5469–5492`; `C/exp_intr.adb:662–663` | Intrinsic calls route to unchecked-deallocation expansion. |
| Pool selection | `C/exp_intr.adb:865–873,1101–1157` | Uses associated pool; special/simple/class-wide/specific cases differ. |
| Nulling | `C/exp_intr.adb:1240–1257,1275–1301` | Generates null assignment; nullable calls receive a nonnull guard. |
| Assertion selection | `C/switch-c.adb:305–309`; `C/sem_prag.adb:34301–34312` | `-gnata` enables assertions; absent overriding policy, applicable policy is Check. |
| Generated-code diagnostic | `C/switch-c.adb:946–956` | `-gnatG` requests generated-code output. |
| Possible runtime release path | `R/s-memory.ads:99–103`; `R/s-memory.adb:49–53,117–125` | `__gnat_free` maps to `System.Memory.Free`, which calls C `free`. |
| Alternative pool release path | `R/s-pooloc.adb:100–129` | An unbounded reclaim pool adjusts its bookkeeping then calls `Memory.Free`. |

These are **source-supported paths**, not proof that the installed compiler selected a particular pool or emitted a particular assertion check. The pinned compiler source’s correspondence to the installed binary remains a separate boundary.

**Minimum later generated evidence**

Use the actual approved derivative, unchanged access types, exact readonly CGPR and strict DEBUG flags. Retain:

1. Complete compiler argv/configuration pragmas and resulting ALI dependency/xref records. Match both instance locations to canonical `Ada.Unchecked_Deallocation` and the selected `a-uncdea.ads` identity.
2. A separately registered, bounded `-gnatG` capture for that same unit/configuration. Inspect both intrinsic expansions, pool/deallocator selection, null guards and null assignments.
3. The resulting object/executable and link-map identities. Use existing disassembly/debug information where generated source leaves backend calls ambiguous.

`gnat_debug.adc` contains only `pragma Initialize_Scalars;`; that is **not** an assertion policy. The actual `-gnata` argv/ALI plus all applicable pragmas must be retained.

The canonical `Post` needs explicit classification. Its presence and `-gnata` do not establish a separately executed postcondition check for an intrinsic. Generated output must distinguish an emitted check, compiler-discharge/redundancy, intrinsic treatment or unresolved behavior. If it cannot, leave canonical-Post execution **UNPROVEN**; direct nulling observations provide a different claim and must not be relabeled as postcondition execution.

**Minimum bounded runtime observation**

Reuse the existing fixture’s nonempty-pattern lifecycle; add no custom allocator, replacement pool, interposition shim or deallocation actuator.

A finite debugger script can observe, without changing execution decisions:

- Both field values immediately before `Free`.
- Each selected deallocation path, with its corresponding allocation address/base, access type and pool.
- Return from each release operation.
- Each field becoming null after its own call.
- A second `Free` producing no additional release of either allocation.

Do not equate an array’s Ada data address with its allocation base: unconstrained-array descriptors and pool bookkeeping may change the address passed to the low-level release. Derive that mapping from generated code and observed call arguments.

`/usr/bin/gdb`, `/usr/bin/nm`, `/usr/bin/objdump` and `/usr/bin/readelf` exist as executable files. They were **not invoked or qualified**. Before using one, register its identity, finite timeout/output/breakpoint bounds and actual symbol/debug-info requirements. If runtime symbols are unavailable, preserve that gap rather than install tools or introduce a shim.

Returning successfully from the actual allocator release establishes a bounded observed release path; it does not prove physical pages returned to the OS, whole-program leak freedom or every error path.

Useful exact hashes:

```text
C/exp_intr.adb  fd2a87b5d6c6877fec2b23d96000915063956b8414235853da3d3d184ce55d62
C/sem_ch12.adb  4d67a12cbf80298c1eacfba27b7c7ae42d9757989d0241993c0da6748320fde8
C/sem_prag.adb  492afe76210ea5539460fd417bbc03cad3bde8fd86889d56144522d71c931093
R/s-memory.adb b668dbef2e3a9a2cdcc5068bd82d483164025774496fe760e626d70dd06a2911
R/s-pooloc.adb 69096e1598bd42cc558b0bd8cccf9d411c87f00bf45a2843a4540e6ff597df98
```

The smallest next step is to register these compiler-output and observational obligations in the later derivative/fixture package. **No compilation, debugger execution, writes or admission occurred. F7 NOT PERFORMED.**