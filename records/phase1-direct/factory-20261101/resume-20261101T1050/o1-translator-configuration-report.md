Static planning is complete. No files changed, builds/generators/proofs executed, or storage operations performed. No additional source acquisition is justified.

Let:

- `K=/home/sicarii/Work/worldline-phase1-direct-20261019`
- `G=/home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1`
- `P=/home/sicarii/opt/gnat/gprbuild-aarch64-linux-26.0.0-1`
- `C=K/records/phase1-direct/completion-20261026/old-retirement-compiler-source-cut-v1/spark2014/gnat2why`
- `Q=K/records/phase1-direct/factory-20261101/o1-xgen-build-package-v2`
- `W=K/records/phase1-direct/completion-20261026/o1-xgen-build-v1/live`

**Source-supported native bindings**

| Binding | Concrete value |
|---|---|
| GPRbuild | `P/bin/gprbuild` |
| Configuration generator | `P/bin/gprconfig`; KB `P/share/gprconfig/` |
| Ada compiler | `G/bin/gcc` |
| C compiler | `G/bin/aarch64-linux-gnu-gcc` |
| GPR binder driver | `P/libexec/gprbuild/gprbind` |
| Native binder | `G/bin/gnatbind`, selected through controlled tool search |
| Link driver | Ada compiler `G/bin/gcc`; **not `gnatlink` as the CGPR driver** |
| Library builder | `P/libexec/gprbuild/gprlib` |
| Runtime directory | `G/lib/gcc/aarch64-linux-gnu/16.1.0/` |
| Runtime sources/objects | Runtime directory plus `adainclude` / `adalib` |

Evidence: `P/share/gprconfig/gnat.xml:12–33` defines Ada compiler, GPR binder driver and runtime; `compilers.xml:190–214` defines native runtime discovery; `linker.xml:1688–1705` selects Ada compiler for linking. These are static configuration rules, not executed closure evidence.

An **existing exact local Ada+C CGPR specimen** is:

`/home/sicarii/Work/sia-assurance-evidence-20261019/takeover-protected-slot-native-receive-first-build-preparation-v4/selected-native-slot-config.cgpr`

SHA256: `efdd42a1cecee86ec261e72066797225b5b874e575da3acf29a254b702b24146`.

Its lines 11–22, 40–42, 50–60 and 117–135 instantiate the bindings above. However, lines 6–7 use `aarch64-linux` with fallback-target generation, while the future xgen package requires compiler readback `aarch64-linux-gnu`. **It is a reviewable configuration input/specimen, not qualified WORLDLINE configuration.** Do not silently adopt that alias. Future preparation must either explicitly qualify these exact bytes or generate and seal a WORLDLINE CGPR using the pinned KB and exact native selection. No WORLDLINE CGPR was found; `Q/README.md:133–134` explicitly says its generated CGPRs do not yet exist.

**Exact expected `sdefault.adb` substitutions**

```text
@ADAINCLUDE@ = /home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adainclude
@ADALIB@     = /home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/adalib
@GNAT1DIR@   = /home/sicarii/opt/gnat/gnat-aarch64-linux-16.1.0-1/lib/gcc/aarch64-linux-gnu/16.1.0/
@PREFIX@     = @NOPREFIX@
```

The trailing slash on `GNAT1DIR` follows `C/Makefile:16–24` exactly; substitution order/body is at lines 54–58. `C/sdefault.adb.in:41–68` consumes those four strings. Both native runtime directories exist. **Selected `G/bin/gnatls -v` readback and generated-byte verification remain UNRUN.** The executable `libexec/.../gnat1` directory must not replace this source-prescribed GNAT1DIR.

**GNATCOLL reuse is conditional, with exact layout**

The future xgen package defines:

```text
GPR_PROJECT_PATH =
  W/source/gnatcoll/core:W/source/gnatcoll/minimal

GNATCOLL_OBJECT_ROOT = W/gnatcoll/
EXTERNALLY_BUILT=true
GNATCOLL_BUILD_MODE=DEBUG
LIBRARY_TYPE=static
GNATCOLL_VERSION=25.0
GNATCOLL_OS=unix
GNATCOLL_MMAP=yes
GNATCOLL_MADVISE=yes
GNATCOLL_XXHASH_ARCH=generic
GNATCOLL_BLAKE3_ARCH=aarch64-linux
```

Evidence: `Q/xgen_common.py:11–15`; `Q/xgen_worker.py:21–27,90–112`. Exact reuse paths are:

```text
W/source/gnatcoll/core/gnatcoll_core.gpr
W/source/gnatcoll/minimal/gnatcoll_minimal.gpr
W/gnatcoll/obj/gnatcoll_core/static/
W/gnatcoll/obj/gnatcoll_minimal/static/
W/gnatcoll/lib/gnatcoll_core/static/libgnatcoll_core.a
W/gnatcoll/lib/gnatcoll_core/static/libgnatcoll_minimal.a
```

The shared `lib/gnatcoll_core/static` parent for both libraries is intentional upstream GPR behavior: retained minimal GPR lines 49–75; core GPR lines 108–133. `C/gnat2why.gpr:1–3` imports `gnatcoll_core`; it does not require the umbrella `gnatcoll.gpr` and its projects dependency.

`W` is presently absent. Therefore **there is no qualified dependency reuse established by this inspection**. Require completed qualification receipts, complete source/object/library hashes and preserved layout before readonly reuse. Otherwise budget a separate fresh DEBUG/static dependency build. Do not source ambient `env.sh`; its line 4 appends ambient project paths.

**Recorded SHA256 anchors**

| File | SHA256 |
|---|---|
| `C/Makefile` | `7b90cdf4f8563179306d06ce98498dff9021517622c7b49786e737e69f1ed0b8` |
| `C/sdefault.adb.in` | `10d3ebdab6a0614c11c47ddf7b4fb6e81d77f603e7641acbc3e850e0b2e25db8` |
| `Q/xgen_worker.py` | `cfec39957fa6fb742c4099ce8be1d9108783eb99f1b0be621bc2585f63c8f091` |
| `P/share/gprconfig/gnat.xml` | `75860604394acd18884a83321d3644b7f2816906c5dfa7e09b17a1d04c160e30` |
| `P/share/gprconfig/compilers.xml` | `a2584791048467473cee3f348638cc8636155d34e631dbdacdf3b9a95b4d27e4` |
| `P/share/gprconfig/linker.xml` | `377065414daa87ec934a6a5125c448052903c7ce12e2faf2ebf6f667762482a5` |

The smallest future package needs only:

1. Existing sealed SPARK/GCC source cuts and selected generator inputs.
2. Qualified 21 generated outputs and exact GNATCOLL dependency receipt/layout.
3. Selected CGPR bytes, pinned compiler/GPR/KB/runtime identities, isolated environment.
4. Four exact substitutions plus generated `sdefault.adb` identity.
5. Finite build/output/recovery budgets and actual compiler/binder/link/include provenance capture.
6. Original unchanged D47 inputs and fresh replay outputs proving execution of the candidate translator.

Runtime configuration adequacy, actual tool resolution, compiler/link closure, generated compatibility and D47 replay remain **UNVERIFIED**. D158/D159 unchanged; full `'Old` guarantee unchanged; no build, authority or acceptance grant. **F7 NOT PERFORMED.**

<oai-mem-citation>
<citation_entries>
MEMORY.md:701-710|note=[carrier and acceptance boundary orientation]
</citation_entries>
<rollout_ids>
01a1787b-9465-7363-96e3-47c837eec185
</rollout_ids>
</oai-mem-citation>